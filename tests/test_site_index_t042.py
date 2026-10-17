"""T-042: cache danh sách bài (SL-T037-4, SL-T037-5).

- SL-T037-4: chỉ xóa file cache khi CHẮC CHẮN hỏng (SQLite báo hỏng / không phải cơ sở dữ liệu,
  ``quick_check`` lỗi, sai cột). Không mở được, lỗi đọc/ghi: để yên file.
- SL-T037-5: ``load`` đã thấy file bận thì ``get`` không chờ ghi thêm lần nữa.
"""

import sqlite3
import time
from contextlib import closing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fake_wordpress import BASE_URL

import seo_app.storage.site_index as site_index
from seo_app.storage.site_index import SiteIndexError, SiteIndexStore
from seo_app.wordpress import PublishedItem

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def published(id_):
    return PublishedItem(
        id=id_, type="post", slug=f"bai-{id_}", link=f"{BASE_URL}/bai-{id_}/", title=f"Bài {id_}"
    )


class Source:
    def __init__(self, items):
        self.base_url = BASE_URL
        self.items = items
        self.calls = 0

    def list_published(self):
        self.calls += 1
        return list(self.items)


@pytest.fixture
def store(tmp_path):
    return SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")


def sqlite_error(code, text="lỗi giả"):
    exc = sqlite3.OperationalError(text)
    exc.sqlite_errorcode = code
    return exc


def failing_health(code):
    def health(_path):
        raise sqlite_error(code)

    return health


# ------------------------------------------------------------------ _is_corrupt


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (11, True),  # SQLITE_CORRUPT
        (11 | (1 << 8), True),  # SQLITE_CORRUPT_VTAB
        (11 | (2 << 8), True),  # SQLITE_CORRUPT_SEQUENCE
        (26, True),  # SQLITE_NOTADB
        (14, False),  # SQLITE_CANTOPEN
        (14 | (1 << 8), False),
        (10, False),  # SQLITE_IOERR
        (10 | (2 << 8), False),  # SQLITE_IOERR_SHORT_READ
        (5, False),  # SQLITE_BUSY
        (6, False),  # SQLITE_LOCKED
        (8, False),  # SQLITE_READONLY
        (13, False),  # SQLITE_FULL
        (3, False),  # SQLITE_PERM
        (1, False),  # SQLITE_ERROR
    ],
)
def test_is_corrupt_by_error_code(code, expected):
    assert site_index._is_corrupt(sqlite_error(code)) is expected


def test_is_corrupt_without_code_reads_the_text():
    assert site_index._is_corrupt(sqlite3.DatabaseError("file is not a database"))
    assert site_index._is_corrupt(sqlite3.DatabaseError("database disk image is malformed"))
    assert not site_index._is_corrupt(sqlite3.OperationalError("unable to open database file"))


def test_real_garbage_file_is_reported_corrupt(tmp_path):
    path = tmp_path / "x.sqlite"
    path.write_bytes(b"day khong phai sqlite" * 100)
    assert site_index._is_healthy(path) is False


# ------------------------------------------------------------------ SL-T037-4


@pytest.mark.parametrize("code", [14, 10, 10 | (3 << 8), 8, 3, 13, 1])
def test_file_that_cannot_be_opened_is_not_deleted(store, monkeypatch, code):
    store.refresh(Source([published(1)]))
    before = store.path.read_bytes()
    monkeypatch.setattr(site_index, "_is_healthy", failing_health(code))

    assert store.load(BASE_URL) is None
    index = store.refresh(Source([published(2)]))

    assert [i.id for i in index.items] == [2]  # danh sách vừa tải vẫn dùng được
    assert index.cache_error
    assert store.reset_count == 0
    assert store.path.read_bytes() == before
    monkeypatch.undo()
    assert [i.id for i in store.load(BASE_URL).items] == [1]


def test_really_corrupted_sqlite_file_is_dropped(store):
    """File SQLite thật bị ghi đè giữa chừng (đầu file còn đúng): vẫn bị coi là hỏng và tải lại."""
    store.refresh(Source([published(i) for i in range(1, 300)]))
    data = bytearray(store.path.read_bytes())
    assert len(data) > 3 * 4096
    data[4096 : len(data) - 100] = b"\xff" * (len(data) - 100 - 4096)
    store.path.write_bytes(bytes(data))
    assert site_index._is_healthy(store.path) is False
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1
    assert [i.id for i in store.get(Source([published(7)])).items] == [7]


def test_cannot_open_message_is_not_called_corrupt(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_is_healthy", failing_health(14))
    with pytest.raises(SiteIndexError) as err:
        store.save(store.refresh(Source([published(2)])))
    assert "Không mở được" in str(err.value)
    assert "bị lỗi" not in str(err.value)


def test_load_does_not_delete_on_cantopen_from_read(store, monkeypatch):
    """Lỗi không mở được xảy ra lúc đọc (sau bước kiểm): cũng không xóa."""
    store.refresh(Source([published(1)]))

    def broken_read(self, conn, site):
        raise sqlite_error(14, "unable to open database file")

    monkeypatch.setattr(SiteIndexStore, "_read", broken_read)
    assert store.load(BASE_URL) is None
    assert store.reset_count == 0
    assert store.path.exists()


def test_load_deletes_on_corrupt_from_read(store, monkeypatch):
    store.refresh(Source([published(1)]))

    def broken_read(self, conn, site):
        raise sqlite_error(11, "database disk image is malformed")

    monkeypatch.setattr(SiteIndexStore, "_read", broken_read)
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1


def test_bad_columns_still_dropped(store):
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("DROP TABLE pages")
        conn.execute("CREATE TABLE pages (id INTEGER, khac TEXT)")
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1


# ------------------------------------------------------------------ SL-T037-5


def test_get_skips_second_write_when_file_is_busy(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_is_healthy", failing_health(5))
    monkeypatch.setattr(site_index, "_is_busy", lambda exc: True)

    def no_save(self, index):
        raise AssertionError("không được ghi khi file đang bận")

    monkeypatch.setattr(SiteIndexStore, "save", no_save)
    source = Source([published(2)])
    index = store.get(source)
    assert [i.id for i in index.items] == [2]
    assert "đang bận" in index.cache_error
    assert source.calls == 1
    assert store.reset_count == 0


def test_get_on_locked_file_returns_quickly(store):
    """Kết nối khác giữ khóa ghi: ``get`` trả danh sách kèm "đang bận" trong khoảng một lần chờ
    ngắn (trước đây khoảng 14 giây trên Windows: chờ 2 lần, mỗi lần tới 5 giây)."""
    store.refresh(Source([published(1)]))
    holder = sqlite3.connect(store.path, isolation_level=None)
    try:
        holder.execute("BEGIN EXCLUSIVE")
        source = Source([published(2)])
        later = datetime.now(TZ) + timedelta(hours=7)
        start = time.monotonic()
        index = store.get(source, now=later)
        elapsed = time.monotonic() - start
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert [i.id for i in index.items] == [2]
    assert "đang bận" in index.cache_error
    assert source.calls == 1
    assert store.reset_count == 0
    assert elapsed < site_index._SQLITE_TIMEOUT  # một lần chờ ngắn (~1 giây), không phải 2×5
    assert [i.id for i in store.load(BASE_URL).items] == [1]


def test_get_when_not_busy_still_caches(store):
    source = Source([published(3)])
    first = store.get(source)
    second = store.get(source)
    assert first.cache_error == ""
    assert second.from_cache
    assert source.calls == 1

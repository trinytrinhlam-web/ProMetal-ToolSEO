"""T-037: cache danh sách bài đã đăng ``seo_app/storage/site_index.py``."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fake_wordpress import BASE_URL, make_session

import seo_app.storage.site_index as site_index
from seo_app.config import PROJECT_ROOT
from seo_app.storage.site_index import (
    MAX_ITEMS,
    SiteIndex,
    SiteIndexError,
    SiteIndexStore,
)
from seo_app.wordpress import PublishedItem, WordPressClient, WordPressError

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def published(id_, kind="post", **extra):
    return PublishedItem(
        id=id_,
        type=kind,
        slug=f"bai-{id_}",
        link=f"{BASE_URL}/bai-{id_}/",
        title=f"Bài {id_} – cửa sắt",
        meta_title=extra.get("meta_title", f"Meta {id_}"),
        meta_desc=extra.get("meta_desc", ""),
        modified_gmt="2026-10-01T03:04:05",
    )


class Source:
    """Thay ``WordPressClient``: đếm số lần tải."""

    def __init__(self, items=None, base_url=BASE_URL, error=None):
        self.base_url = base_url
        self.items = items if items is not None else [published(1), published(2, "page")]
        self.error = error
        self.calls = 0

    def list_published(self):
        self.calls += 1
        if self.error:
            raise self.error
        return list(self.items)


@pytest.fixture
def store(tmp_path):
    return SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")


def raw_sql(path, sql, params=()):
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute(sql, params)


# ---------------------------------------------------------------- cơ bản


def test_default_file_sits_next_to_drafts():
    assert site_index.DEFAULT_SITE_INDEX_FILE == PROJECT_ROOT / "data" / "site_index.sqlite"
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "data/" in gitignore and "*.sqlite" in gitignore


def test_default_path_read_at_creation(monkeypatch, tmp_path):
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", tmp_path / "x.sqlite")
    assert SiteIndexStore().path == tmp_path / "x.sqlite"


def test_first_get_downloads_and_saves(store):
    source = Source()
    index = store.get(source)
    assert source.calls == 1
    assert not index.from_cache and index.cache_error == ""
    assert store.path.exists()
    assert [i.id for i in index.items] == [1, 2]
    assert index.fetched_at.tzinfo is not None
    assert index.fetched_at.utcoffset() == timedelta(hours=7)


def test_second_get_uses_cache(store):
    source = Source()
    first = store.get(source)
    again = store.get(source)
    assert source.calls == 1
    assert again.from_cache
    assert again.items == first.items
    assert again.fetched_at == first.fetched_at
    assert again.site == BASE_URL


def test_round_trip_keeps_every_field(store):
    item = published(5, meta_title="Tiêu đề | Pro-Metal", meta_desc="Mô tả có dấu “ngoặc”")
    store.refresh(Source([item]))
    (loaded,) = store.load(BASE_URL).items
    assert loaded == item


def test_by_link(store):
    index = store.refresh(Source())
    assert index.by_link()[f"{BASE_URL}/bai-2/"].type == "page"


def test_fetched_at_stored_with_timezone(store):
    store.refresh(Source())
    with closing(sqlite3.connect(store.path)) as conn:
        (value,) = conn.execute("SELECT value FROM info WHERE key = 'fetched_at'").fetchone()
    assert value.endswith("+07:00")


def test_empty_site_is_cached_too(store):
    source = Source(items=[])
    store.get(source)
    index = store.get(source)
    assert source.calls == 1 and index.from_cache and index.items == ()


# ---------------------------------------------------------------- cũ / làm mới


def test_stale_cache_reloads_by_itself(store):
    source = Source()
    store.get(source)
    later = datetime.now(TZ) + timedelta(hours=6, minutes=1)
    index = store.get(source, now=later)
    assert source.calls == 2 and not index.from_cache


def test_not_stale_just_before_limit(store):
    source = Source()
    store.get(source)
    store.get(source, now=datetime.now(TZ) + timedelta(hours=5, minutes=59))
    assert source.calls == 1


def test_is_stale(store):
    assert store.is_stale(BASE_URL)  # chưa có cache
    store.refresh(Source())
    assert not store.is_stale(BASE_URL)
    assert store.is_stale(BASE_URL, now=datetime.now(TZ) + timedelta(hours=7))
    assert SiteIndexStore(path=store.path, max_age_hours=1).is_stale(
        BASE_URL, now=datetime.now(TZ) + timedelta(hours=2)
    )


def test_now_in_other_timezone_compares_correctly(store):
    store.refresh(Source())
    utc_now = datetime.now(ZoneInfo("UTC")) + timedelta(hours=1)
    assert not store.is_stale(BASE_URL, now=utc_now)


def test_fetched_at_in_future_counts_as_stale(store):
    store.refresh(Source())
    future = (datetime.now(TZ) + timedelta(days=30)).isoformat()
    raw_sql(store.path, "UPDATE info SET value = ? WHERE key = 'fetched_at'", (future,))
    assert store.is_stale(BASE_URL)


def test_refresh_always_downloads(store):
    source = Source()
    store.get(source)
    source.items = [published(9)]
    index = store.refresh(source)
    assert source.calls == 2
    assert [i.id for i in index.items] == [9]
    assert [i.id for i in store.load(BASE_URL).items] == [9]  # ghi đè, không cộng dồn


def test_other_site_cache_is_ignored_and_replaced(store):
    store.refresh(Source())
    assert store.load("https://other.example") is None
    other = Source(items=[], base_url="https://other.example")
    store.get(other)
    assert other.calls == 1
    assert store.load(BASE_URL) is None


def test_network_error_propagates_and_keeps_old_cache(store):
    store.refresh(Source())
    with pytest.raises(WordPressError):
        store.refresh(Source(error=WordPressError("mất mạng")))
    assert store.load(BASE_URL) is not None


def test_save_failure_still_returns_fresh_list(store, monkeypatch):
    def broken(_index):
        raise SiteIndexError("File lưu tạm danh sách bài đang bận.")

    monkeypatch.setattr(store, "save", broken)
    index = store.refresh(Source())
    assert [i.id for i in index.items] == [1, 2]
    assert "đang bận" in index.cache_error


def test_save_rejects_naive_time_and_too_many_items(store):
    with pytest.raises(SiteIndexError, match="múi giờ"):
        store.save(SiteIndex(site=BASE_URL, fetched_at=datetime.now(), items=()))
    many = tuple(published(n) for n in range(1, MAX_ITEMS + 2))
    with pytest.raises(SiteIndexError, match="quá dài"):
        store.save(SiteIndex(site=BASE_URL, fetched_at=datetime.now(TZ), items=many))


# ---------------------------------------------------------------- xóa / hỏng


def test_deleted_file_is_recreated(store):
    source = Source()
    store.get(source)
    store.clear()
    assert not store.path.exists()
    store.get(source)
    assert source.calls == 2 and store.path.exists()


def test_deleted_folder_is_recreated(store):
    source = Source()
    store.get(source)
    store.path.unlink()
    store.path.parent.rmdir()
    index = store.get(source)
    assert source.calls == 2 and index.cache_error == "" and store.path.exists()


def test_clear_without_file_is_fine(store):
    store.clear()


@pytest.mark.parametrize(
    "content",
    [b"", b"day khong phai sqlite", b"SQLite format 3\x00" + b"\xff" * 200],
)
def test_garbage_file_is_dropped_and_reloaded(store, content):
    store.path.parent.mkdir(parents=True)
    store.path.write_bytes(content)
    source = Source()
    index = store.get(source)
    assert source.calls == 1 and index.cache_error == ""
    assert store.get(source).from_cache


def test_wrong_structure_is_dropped(store):
    store.path.parent.mkdir(parents=True)
    raw_sql(store.path, "CREATE TABLE pages (id INTEGER, data TEXT)")
    source = Source()
    store.get(source)
    assert store.reset_count == 1
    assert store.get(source).from_cache


def test_extra_table_does_not_break_cache(store):
    # Bảng lạ thêm vào không làm hỏng cache (chỉ đọc đúng 2 bảng của mình).
    store.refresh(Source())
    raw_sql(store.path, "CREATE TABLE extra (x TEXT)")
    assert store.load(BASE_URL) is not None


@pytest.mark.parametrize(
    "sql, params",
    [
        ("UPDATE pages SET link = ? WHERE id = 1", ("https://evil.com/x/",)),
        ("UPDATE pages SET link = ? WHERE id = 1", ("http://example.com/x/",)),
        ("UPDATE pages SET type = ? WHERE id = 1", ("attachment",)),
        ("UPDATE pages SET id = ? WHERE id = 1", (-5,)),
        ("UPDATE pages SET id = ? WHERE id = 1", ("abc",)),
        ("UPDATE pages SET title = ? WHERE id = 1", (b"\xff\xfe",)),
        ("UPDATE pages SET title = ? WHERE id = 1", ("x" * 400,)),
        ("UPDATE pages SET title = ? WHERE id = 1", ("x" * 100_000,)),
        ("UPDATE pages SET meta_desc = ? WHERE id = 1", ("có\x00null",)),
        ("UPDATE pages SET modified_gmt = ? WHERE id = 1", ("hôm qua",)),
        ("UPDATE pages SET slug = ? WHERE id = 1", ("<script>",)),
        ("UPDATE pages SET id = ? WHERE id = 1", (1.5,)),
        ("UPDATE info SET value = ? WHERE key = 'fetched_at'", ("không phải ngày",)),
        ("UPDATE info SET value = ? WHERE key = 'fetched_at'", ("2026-10-01T10:00:00",)),
        ("UPDATE info SET value = ? WHERE key = 'schema_version'", ("99",)),
        ("UPDATE info SET value = ? WHERE key = 'site'", (BASE_URL + "x" * 5000,)),
        ("DELETE FROM info WHERE key = ?", ("fetched_at",)),
    ],
)
def test_tampered_rows_drop_whole_cache(store, sql, params):
    source = Source()
    store.refresh(source)
    raw_sql(store.path, sql, params)
    assert store.load(BASE_URL) is None
    index = store.get(source)
    assert source.calls == 2 and not index.from_cache
    assert store.get(source).from_cache  # tạo lại sạch


def test_bad_row_with_text_decode_error_does_not_crash(store):
    store.refresh(Source())
    # Chữ không phải UTF-8 lưu dưới kiểu TEXT.
    raw_sql(store.path, "UPDATE pages SET title = CAST(X'C328' AS TEXT) WHERE id = 1")
    assert store.load(BASE_URL) is None


def test_too_many_rows_drop_cache(store, monkeypatch):
    store.refresh(Source())
    monkeypatch.setattr(site_index, "MAX_ITEMS", 1)
    assert store.load(BASE_URL) is None


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="máy không tạo được symlink")
def test_symlink_is_replaced_and_target_untouched(tmp_path):
    outside = tmp_path / "ngoai.sqlite"
    raw_sql(outside, "CREATE TABLE secret (x TEXT)")
    before = outside.read_bytes()
    folder = tmp_path / "data"
    folder.mkdir()
    link = folder / "site_index.sqlite"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("không có quyền tạo symlink")
    store = SiteIndexStore(path=link)
    store.refresh(Source())
    assert not link.is_symlink() and link.exists()
    assert outside.read_bytes() == before


def test_unwritable_location_gives_vietnamese_error(tmp_path):
    blocker = tmp_path / "la-file"
    blocker.write_text("x", encoding="utf-8")
    store = SiteIndexStore(path=blocker / "site_index.sqlite")
    assert store.load(BASE_URL) is None
    index = store.refresh(Source())
    assert [i.id for i in index.items] == [1, 2]
    assert "Không tạo được file" in index.cache_error


def test_sql_uses_parameters_only():
    source = (PROJECT_ROOT / "seo_app" / "storage" / "site_index.py").read_text(encoding="utf-8")
    assert "execute(f" not in source and ".format(" not in source and "% (" not in source


# ---------------------------------------------------------------- với client thật (site giả)


def test_works_with_wordpress_client(store, fake_wp):
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/posts",
        [
            {
                "id": 810,
                "status": "publish",
                "slug": "banh-xe",
                "link": f"{BASE_URL}/banh-xe/",
                "title": {"rendered": "Bánh xe &amp; ray"},
                "modified_gmt": "2026-10-01T03:04:05",
                "meta": {"_siteseo_titles_title": "Bánh xe | Pro Metal"},
            },
            {"id": 811, "status": "future", "link": f"{BASE_URL}/sap-dang/"},
        ],
    )
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    client = WordPressClient(BASE_URL, "lam", "abcd", session=make_session(fake_wp))

    index = store.get(client)
    assert [(i.id, i.title, i.meta_title) for i in index.items] == [
        (810, "Bánh xe & ray", "Bánh xe | Pro Metal")
    ]
    assert store.get(client).from_cache
    assert len(fake_wp.requests) == 2
    assert {r.method for r in fake_wp.requests} == {"GET"}

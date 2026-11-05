"""T-131 (Thợ Máy) phần 1–3: dọn kho dữ liệu phụ theo mẫu ``search_cache`` (T-122).

- LC-T129-1: cache danh sách bài (``site_index``) kiểm file như ``search_cache``: so trọn
  ``sqlite_master`` trước khi mở và trong cùng giao dịch (bảng lạ, trigger, khung nhìn, chỉ mục lạ
  là file lạ: bỏ file), ``trusted_schema = OFF``, giới hạn số bước, giới hạn độ dài một giá trị;
  đọc ``sqlite_master`` bằng bộ giải mã có bắt lỗi.
- SL-T117-1: ``site_index``, ``plan_cache`` không tạo, không mở, không xóa gì khi ``data/`` (hay một
  thư mục con) là liên kết; chính file, file nhật ký là liên kết (kể cả hard link) thì chỉ gỡ.
- Mẫu LC-T122-1: bước kiểm file coi UTF-8 hỏng trong ``sqlite_master`` và «unsupported file
  format» là file lạ (bỏ file, ghi lại được); lỗi do môi trường thì giữ file.
- Như LC-T122-2: lỗi đọc thư mục khi kiểm liên kết ra câu cố định, không lọt lỗi Python.

Liên kết thật: junction trên Windows (không cần quyền quản trị), symlink trên Mac/Linux; hard link
bằng ``os.link``. Không gọi mạng; mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import contextlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from seo_app.images.data_dir import MSG_DATA_DIR_LINK
from seo_app.storage import plan_cache, site_index
from seo_app.storage.plan_cache import PlanCacheError, PlanCacheStore
from seo_app.storage.site_index import SiteIndex, SiteIndexError, SiteIndexStore
from seo_app.wordpress.client import PublishedItem

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
NOW = datetime(2026, 11, 5, 14, 0, tzinfo=TZ)
SITE = "https://suachuacuasat.com"
SHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-xyz"
VALUES = (("Mã bài", "Từ khóa chính"), ("B-001", "sửa cửa cuốn"))
# Câu tạo bảng của site_index trước T-131 (chép nguyên văn từ ``_prepare`` cũ): file cũ phải dùng
# tiếp được, không bị bỏ.
OLD_SITE_INDEX_SQL = (
    "CREATE TABLE IF NOT EXISTS pages ("
    "id INTEGER NOT NULL, type TEXT NOT NULL, slug TEXT NOT NULL, "
    "link TEXT NOT NULL, title TEXT NOT NULL, meta_title TEXT NOT NULL, "
    "meta_desc TEXT NOT NULL, modified_gmt TEXT NOT NULL, "
    "PRIMARY KEY (type, id))",
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
)


def published(post_id: int) -> PublishedItem:
    return PublishedItem(
        post_id, "post", f"bai-{post_id}", f"{SITE}/bai-{post_id}/", f"Bài {post_id}"
    )


class Source:
    base_url = SITE

    def __init__(self, ids=(1,)):
        self.ids = ids
        self.calls = 0

    def list_published(self):
        self.calls += 1
        return [published(post_id) for post_id in self.ids]


def link_dir(link: Path, target: Path) -> None:
    """Liên kết thư mục không cần quyền quản trị: junction trên Windows, symlink trên Mac/Linux."""
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def sqlite_error(code: int, text: str = "lỗi giả") -> sqlite3.OperationalError:
    exc = sqlite3.OperationalError(text)
    exc.sqlite_errorcode = code
    return exc


def raw_sql(path: Path, *statements: str) -> None:
    with closing(sqlite3.connect(path)) as conn, conn:
        for sql in statements:
            conn.execute(sql)


def names_in(path: Path) -> set[str]:
    with closing(sqlite3.connect(path)) as conn:
        return {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả; ``PROJECT_ROOT`` của hai kho trỏ vào đó."""
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(site_index, "PROJECT_ROOT", root)
    monkeypatch.setattr(plan_cache, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def index_store(project: Path) -> SiteIndexStore:
    return SiteIndexStore(path=project / "data" / "site_index.sqlite")


@pytest.fixture
def plan_store(project: Path) -> PlanCacheStore:
    return PlanCacheStore(path=project / "data" / "plan_cache.sqlite")


def save_index(store: SiteIndexStore, ids=(1, 2)) -> None:
    store.save(SiteIndex(SITE, NOW, tuple(published(post_id) for post_id in ids)))


# ================================================================ LC-T129-1: cấu trúc file

TAMPER = {
    "trigger-nang": (
        "CREATE TRIGGER nang AFTER INSERT ON pages BEGIN "
        "SELECT count(*) FROM pages a, pages b, pages c; END",
    ),
    "trigger-chen-link-la": (
        "CREATE TRIGGER chen AFTER INSERT ON info BEGIN "
        "UPDATE pages SET link = 'https://evil.com/x/'; END",
    ),
    "bang-la": ("CREATE TABLE extra (x TEXT)",),
    "khung-nhin": ("CREATE VIEW v AS SELECT * FROM pages",),
    "chi-muc": ("CREATE INDEX i ON pages (link)",),
    "bang-pages-khac-cot": ("DROP TABLE pages", "CREATE TABLE pages (id INTEGER, khac TEXT)"),
    "doi-ten-bang-info": ("ALTER TABLE info RENAME TO info_cu",),
}


@pytest.mark.parametrize("change", list(TAMPER), ids=list(TAMPER))
def test_site_index_file_with_foreign_structure_is_dropped(index_store, change):
    save_index(index_store)
    raw_sql(index_store.path, *TAMPER[change])
    assert site_index._is_healthy(index_store.path) is False
    assert index_store.load(SITE) is None
    assert index_store.reset_count == 1
    source = Source((7,))
    assert [item.id for item in index_store.get(source).items] == [7]
    assert index_store.get(source).from_cache and source.calls == 1


def test_site_index_trigger_never_runs_when_saving(index_store):
    save_index(index_store)
    raw_sql(
        index_store.path,
        "CREATE TABLE stolen (x)",
        "CREATE TRIGGER t AFTER INSERT ON pages BEGIN INSERT INTO stolen VALUES (1); END",
    )
    save_index(index_store, (3,))
    assert names_in(index_store.path) == {"pages", "info", "sqlite_autoindex_pages_1",
                                          "sqlite_autoindex_info_1"}  # fmt: skip
    assert [item.id for item in index_store.load(SITE).items] == [3]


@pytest.mark.parametrize("operation", ["load", "save"])
def test_site_index_structure_checked_again_inside_transaction(index_store, monkeypatch, operation):
    """File bị thêm trigger ngay sau bước kiểm của ``_prepare`` (khe giữa kiểm và giao dịch): lớp
    kiểm trong giao dịch bắt được. Đọc: bỏ file; ghi: bỏ file rồi ghi lại trên file mới."""
    save_index(index_store)
    original = SiteIndexStore._prepare
    added = []

    def prepare_then_add_trigger(self):
        original(self)
        if not added:
            added.append(True)
            raw_sql(
                self.path,
                "CREATE TRIGGER chen AFTER INSERT ON pages BEGIN DELETE FROM info; END",
            )

    monkeypatch.setattr(SiteIndexStore, "_prepare", prepare_then_add_trigger)
    if operation == "load":
        assert index_store.load(SITE) is None
    else:
        save_index(index_store, (5,))
        monkeypatch.undo()
        assert [item.id for item in index_store.load(SITE).items] == [5]
        assert "chen" not in names_in(index_store.path)
    assert index_store.reset_count == 1


def test_site_index_old_file_from_before_t131_still_reads(index_store):
    index_store.path.parent.mkdir(parents=True)
    raw_sql(
        index_store.path,
        *OLD_SITE_INDEX_SQL,
        "INSERT INTO pages VALUES (1, 'post', 'bai-1', 'https://suachuacuasat.com/bai-1/', "
        "'Bài 1', '', '', '')",
        "INSERT INTO info VALUES ('schema_version', '2')",
        f"INSERT INTO info VALUES ('site', '{SITE}')",
        f"INSERT INTO info VALUES ('fetched_at', '{NOW.isoformat()}')",
        "INSERT INTO info VALUES ('truncated', '0')",
    )
    cached = index_store.load(SITE)
    assert [item.id for item in cached.items] == [1] and cached.from_cache
    assert index_store.reset_count == 0


def test_site_index_connections_are_guarded(index_store, monkeypatch):
    save_index(index_store)
    seen = []
    original = SiteIndexStore._read

    def spying_read(self, conn, site):
        seen.append(conn.execute("PRAGMA trusted_schema").fetchone()[0])
        seen.append(conn.getlimit(sqlite3.SQLITE_LIMIT_LENGTH))
        return original(self, conn, site)

    monkeypatch.setattr(SiteIndexStore, "_read", spying_read)
    assert index_store.load(SITE) is not None
    assert seen == [0, site_index._MAX_SQLITE_LENGTH]


def test_site_index_too_many_steps_counts_as_foreign_file(index_store, monkeypatch):
    """Giới hạn số bước có trên mọi kết nối: quá mức là file lạ (bỏ file), không treo."""
    save_index(index_store, tuple(range(1, 200)))
    monkeypatch.setattr(site_index, "_MAX_VM_STEPS", 2_000)
    assert index_store.load(SITE) is None
    assert index_store.reset_count == 1


def test_site_index_value_longer_than_limit_counts_as_foreign_file(index_store, monkeypatch):
    save_index(index_store)
    raw_sql(index_store.path, "UPDATE pages SET title = 'Bài ' || hex(randomblob(400))")
    monkeypatch.setattr(site_index, "_MAX_SQLITE_LENGTH", 500)
    assert index_store.load(SITE) is None
    assert index_store.reset_count == 1


def test_site_index_steps_limit_has_room_for_the_biggest_cache():
    # Đo ở báo cáo T-131: danh sách lớn nhất (10.000 dòng, chữ dài tối đa) dùng 340.000 bước mỗi
    # kết nối. Trần phải cao hơn nhiều lần, như các kho khác.
    assert site_index._MAX_VM_STEPS >= 100 * 340_000
    assert site_index._MAX_SQLITE_LENGTH >= 8 * site_index._MAX_FIELD_BYTES


# ================================================================ mẫu LC-T122-1


def break_utf8_in_master(path: Path, table: str) -> None:
    """Byte UTF-8 hỏng trong câu tạo bảng (chú thích cuối câu), như sửa tay bằng công cụ khác."""
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA writable_schema = ON")
        conn.execute(
            "UPDATE sqlite_master SET sql = CAST(sql || X'202D2D20FF' AS TEXT) WHERE name = ?",
            (table,),
        )
        conn.commit()


def schema_format_5(path: Path, _table: str) -> None:
    """Số «schema format» (byte 44–47 đầu file) thành 5: SQLite báo «unsupported file format»."""
    data = bytearray(path.read_bytes())
    data[44:48] = (5).to_bytes(4, "big")
    path.write_bytes(bytes(data))


DAMAGE = [break_utf8_in_master, schema_format_5]


@pytest.mark.parametrize("damage", DAMAGE, ids=["utf8", "schema-5"])
def test_site_index_hand_edited_file_is_dropped_and_rewritable(index_store, damage):
    save_index(index_store)
    damage(index_store.path, "pages")
    assert index_store.load(SITE) is None
    assert index_store.reset_count == 1
    save_index(index_store, (4,))
    assert [item.id for item in index_store.load(SITE).items] == [4]


@pytest.mark.parametrize("damage", DAMAGE, ids=["utf8", "schema-5"])
def test_plan_cache_hand_edited_file_is_dropped_and_rewritable(plan_store, damage):
    plan_store.save(SHEET_ID, VALUES, NOW)
    damage(plan_store.path, "sheet_rows")
    assert plan_store.load(SHEET_ID) is None  # trước đây: «không mở được» mãi, file không bỏ
    assert plan_store.reset_count == 1
    plan_store.save(SHEET_ID, VALUES, NOW)
    assert plan_store.load(SHEET_ID).values == VALUES


@pytest.mark.parametrize("module", [site_index, plan_cache], ids=["site-index", "plan-cache"])
@pytest.mark.parametrize(
    ("code", "kept"),
    [
        (3, True),  # SQLITE_PERM
        (5, True),  # SQLITE_BUSY
        (6, True),  # SQLITE_LOCKED
        (7, True),  # SQLITE_NOMEM
        (8, True),  # SQLITE_READONLY
        (10, True),  # SQLITE_IOERR
        (10 | (3 << 8), True),  # SQLITE_IOERR_WRITE
        (13, True),  # SQLITE_FULL
        (14, True),  # SQLITE_CANTOPEN
        (15, True),  # SQLITE_PROTOCOL
        (1, False),  # SQLITE_ERROR («unsupported file format»…)
        (9, False),  # SQLITE_INTERRUPT (quá số bước)
        (11, False),  # SQLITE_CORRUPT
        (18, False),  # SQLITE_TOOBIG
        (26, False),  # SQLITE_NOTADB
    ],
    ids=lambda value: str(value),
)
def test_health_check_keeps_file_only_on_environment_errors(
    tmp_path, monkeypatch, module, code, kept
):
    path = tmp_path / "x.sqlite"
    raw_sql(path, "CREATE TABLE t (x)")

    def failing(_conn):
        raise sqlite_error(code)

    monkeypatch.setattr(module, "_app_tables", failing)
    if kept:
        with pytest.raises(sqlite3.DatabaseError):
            module._is_healthy(path)
    else:
        assert module._is_healthy(path) is False


@pytest.mark.parametrize("module", [site_index, plan_cache], ids=["site-index", "plan-cache"])
def test_health_check_without_code_is_foreign_file(tmp_path, monkeypatch, module):
    # Lỗi giải mã của Python (không có mã SQLite) khi đọc sqlite_master: file lạ.
    path = tmp_path / "x.sqlite"
    raw_sql(path, "CREATE TABLE t (x)")

    def failing(_conn):
        raise sqlite3.OperationalError("Could not decode to UTF-8 column")

    monkeypatch.setattr(module, "_app_tables", failing)
    assert module._is_healthy(path) is False


# ================================================================ SL-T117-1: data/ là liên kết


@pytest.fixture
def linked_data(project: Path, tmp_path: Path):
    """``du-an/data`` là liên kết tới ``ngoai-du-an`` (đã có sẵn hai file cùng tên kho)."""
    outside = tmp_path / "ngoai-du-an"
    outside.mkdir()
    for name in ("site_index.sqlite", "plan_cache.sqlite", "site_index.sqlite-journal"):
        (outside / name).write_bytes(b"file ngoai du an")
    link_dir(project / "data", outside)
    yield project / "data", outside
    with contextlib.suppress(OSError):
        os.rmdir(project / "data")  # gỡ chính liên kết, không đụng thư mục đích


def untouched(outside: Path) -> bool:
    files = sorted(path.name for path in outside.iterdir())
    expected = ["plan_cache.sqlite", "site_index.sqlite", "site_index.sqlite-journal"]
    return files == expected and all(
        (outside / name).read_bytes() == b"file ngoai du an" for name in expected
    )


def test_site_index_never_opens_or_deletes_through_linked_data(linked_data):
    data, outside = linked_data
    store = SiteIndexStore(path=data / "site_index.sqlite")
    with pytest.raises(SiteIndexError) as error:
        save_index(store)
    assert str(error.value) == MSG_DATA_DIR_LINK
    assert store.load(SITE) is None
    source = Source((9,))
    index = store.get(source)  # danh sách vừa tải vẫn dùng được, kèm câu báo
    assert [item.id for item in index.items] == [9] and index.cache_error == MSG_DATA_DIR_LINK
    assert store.refresh(source).cache_error == MSG_DATA_DIR_LINK
    with pytest.raises(SiteIndexError, match="lối tắt"):
        store.clear()
    assert store.reset_count == 0
    assert untouched(outside)


def test_plan_cache_never_opens_or_deletes_through_linked_data(linked_data):
    data, outside = linked_data
    store = PlanCacheStore(path=data / "plan_cache.sqlite")
    with pytest.raises(PlanCacheError) as error:
        store.save(SHEET_ID, VALUES, NOW)
    assert str(error.value) == MSG_DATA_DIR_LINK
    assert store.load(SHEET_ID) is None
    with pytest.raises(PlanCacheError, match="lối tắt"):
        store.clear()
    assert store.reset_count == 0
    assert untouched(outside)


def test_linked_subfolder_of_data_is_also_refused(project, tmp_path):
    outside = tmp_path / "ngoai"
    outside.mkdir()
    (project / "data").mkdir()
    link_dir(project / "data" / "cache", outside)
    try:
        with pytest.raises(SiteIndexError, match="lối tắt"):
            save_index(SiteIndexStore(path=project / "data" / "cache" / "site_index.sqlite"))
        with pytest.raises(PlanCacheError, match="lối tắt"):
            PlanCacheStore(path=project / "data" / "cache" / "p.sqlite").save(SHEET_ID, VALUES, NOW)
    finally:
        os.rmdir(project / "data" / "cache")
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("operation", ["save", "clear"])
def test_permission_error_while_checking_links_is_a_fixed_message(
    index_store, plan_store, monkeypatch, operation
):
    # Như LC-T122-2: Windows từ chối lstat một tầng thư mục.
    def denied(*_args, **_kwargs):
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(site_index, "dir_has_link", denied)
    monkeypatch.setattr(plan_cache, "dir_has_link", denied)
    with pytest.raises(SiteIndexError) as index_error:
        save_index(index_store) if operation == "save" else index_store.clear()
    with pytest.raises(PlanCacheError) as plan_error:
        if operation == "save":
            plan_store.save(SHEET_ID, VALUES, NOW)
        else:
            plan_store.clear()
    for error in (index_error, plan_error):
        assert "Access is denied" in str(error.value)
        assert error.value.__cause__ is None
    assert index_store.refresh(Source()).cache_error  # danh sách vừa tải vẫn dùng được


# ================================================================ chính file là liên kết


def hard_link_or_skip(outside: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(outside, target)
    except OSError:
        pytest.skip("ổ này không cho tạo hard link")


def save_with(kind: str, path: Path, ids=(1, 2)) -> None:
    if kind == "site-index":
        save_index(SiteIndexStore(path=path), ids)
    else:
        PlanCacheStore(path=path).save(SHEET_ID, VALUES[: len(ids)], NOW)


@pytest.mark.parametrize("kind", ["site-index", "plan-cache"])
def test_hard_linked_cache_file_is_unlinked_not_followed(project, tmp_path, kind):
    """Tên trong ``data/`` là hard link tới một file cache **hợp lệ** nằm ngoài dự án: không được
    ghi xuyên qua (nếu đi theo, lần ghi sau sửa luôn file ngoài, vì hai tên chung một nội dung)."""
    outside = tmp_path / "ngoai" / "cache.sqlite"
    outside.parent.mkdir()
    save_with(kind, outside)
    before = outside.read_bytes()
    target = project / "data" / ("site_index.sqlite" if kind == "site-index" else "plan.sqlite")
    hard_link_or_skip(outside, target)
    save_with(kind, target, (5,))
    assert outside.read_bytes() == before
    assert os.lstat(target).st_nlink == 1 and os.lstat(outside).st_nlink == 1


@pytest.mark.parametrize("kind", ["site-index", "plan-cache"])
def test_hard_linked_journal_is_unlinked_not_followed(project, tmp_path, kind):
    """File nhật ký là hard link tới file ngoài: lần ghi sau tạo nhật ký mới, không ghi đè file
    ngoài (SQLite ghi nhật ký vào đúng tên ``…-journal`` mỗi lần ghi)."""
    target = project / "data" / ("site_index.sqlite" if kind == "site-index" else "plan.sqlite")
    save_with(kind, target)
    outside = tmp_path / "nhat-ky-ngoai"
    outside.write_bytes(b"file ngoai du an" * 64)
    journal = target.with_name(target.name + "-journal")
    hard_link_or_skip(outside, journal)
    save_with(kind, target, (3,))
    assert outside.read_bytes() == b"file ngoai du an" * 64
    assert not journal.exists() or os.lstat(journal).st_nlink == 1


@pytest.mark.parametrize("kind", ["site-index", "plan-cache"])
def test_symlinked_journal_is_removed_not_followed(project, tmp_path, kind):
    """File nhật ký là symlink tới file ngoài: gỡ symlink trước khi mở, lần ghi không đụng file
    ngoài. Windows cần quyền đặc biệt để tạo symlink file: máy không cho thì bỏ qua (chạy được
    trên Mac/Linux)."""
    target = project / "data" / ("site_index.sqlite" if kind == "site-index" else "plan.sqlite")
    save_with(kind, target)
    outside = tmp_path / "nhat-ky-ngoai"
    outside.write_bytes(b"file ngoai du an" * 64)
    journal = target.with_name(target.name + "-journal")
    try:
        os.symlink(outside, journal)
    except OSError:
        pytest.skip("máy này không cho tạo symlink file (Windows cần quyền Developer Mode)")
    save_with(kind, target, (3,))
    assert outside.read_bytes() == b"file ngoai du an" * 64
    assert not journal.is_symlink()


# ================================================================ kho nào cũng chặn


@pytest.mark.parametrize("module", [site_index, plan_cache], ids=["site-index", "plan-cache"])
def test_store_checks_linked_data_before_creating_and_before_clearing(module):
    source = Path(module.__file__).read_text(encoding="utf-8")
    prepare = source[source.index("    def _prepare(") :]
    prepare = prepare[: prepare.index("\n    def ", 10)]
    clear = source[source.index("    def clear(") :]
    clear = clear[: clear.index("\n    def ", 10)]
    for body in (prepare, clear):
        assert "dir_has_link(self.path.parent, PROJECT_ROOT)" in body
    # Kiểm trước khi tạo thư mục, trước khi xóa file.
    assert prepare.index("dir_has_link") < prepare.index("mkdir")
    assert clear.index("dir_has_link") < clear.index("_reset" if module is plan_cache else "unlink")

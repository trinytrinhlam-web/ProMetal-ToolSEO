"""T-136 (Thợ Máy): bảng ca chung cho phần kiểm file của 5 kho SQLite (Lá Chắn T-131 B.1, B.2,
B.4; LC-T131-1; Soi Lỗi T-131 GN-1, GN-2, GN-3).

- Năm kho dùng chung ``seo_app.storage.sqlite_file``; hàm cùng tên của từng kho chuyển đúng hằng số
  của kho đó (giới hạn, thời gian chờ) vào lúc gọi.
- Đầu file ghi phiên bản lạ (byte 18 hay 19 lớn hơn 2) là file lạ ở cả 5 kho: kho cất / bỏ file,
  lần sau dùng được (trước đây byte 18 làm mọi lần ghi lỗi mãi).
- Mã lỗi môi trường chung, có 13 (đầy ổ) ở cả bốn kho dùng bộ mã này.
- Kho nháp: ô chữ có UTF-8 hỏng chỉ làm bỏ dòng đó; SQLite báo «chỉ đọc» thì câu báo nói «chỉ
  đọc»; câu «đã cất file» nói thêm lối tắt và dấu «đã gửi».
- ``plan_cache`` tạo cả hai bảng trong một giao dịch ghi.
"""

from __future__ import annotations

import ast
import os
import sqlite3
import stat
from contextlib import closing
from pathlib import Path

import pytest
import test_app_pages as pages

from seo_app.storage import (
    drafts,
    image_tags,
    plan_cache,
    search_cache,
    site_index,
    sqlite_file,
)
from seo_app.storage.drafts import DraftError, DraftSnapshot, DraftStore
from seo_app.storage.image_tags import ImageTagStore
from seo_app.storage.plan_cache import PlanCacheStore
from seo_app.storage.search_cache import SearchCacheStore
from seo_app.storage.site_index import SiteIndexStore

ROOT = Path(__file__).resolve().parents[1]
env = pages.env  # trang Soạn bài: mật khẩu thử, không có khóa AI thật
fake_ai = pages.fake_ai
MODULES = {
    "drafts": drafts,
    "image-tags": image_tags,
    "site-index": site_index,
    "plan-cache": plan_cache,
    "search-cache": search_cache,
}
STORES = {
    "drafts": DraftStore,
    "image-tags": ImageTagStore,
    "site-index": SiteIndexStore,
    "plan-cache": PlanCacheStore,
    "search-cache": SearchCacheStore,
}
# Hai kho giữ file lạ bằng cách cất sang một bên; ba kho lưu tạm bỏ file (tạo lại được).
MOVED_ASIDE = {"drafts", "image-tags"}


def made(name: str, path: Path):
    """Kho ``name`` ở ``path`` với file hợp lệ, đủ bảng (tạo bằng chính kho)."""
    store = STORES[name](path=path)
    store._prepare()
    return store


def set_byte(path: Path, offset: int, value: int) -> None:
    data = bytearray(path.read_bytes())
    data[offset] = value
    path.write_bytes(bytes(data))


# ================================================================ hàm chung của 5 kho


@pytest.mark.parametrize("name", list(MODULES), ids=list(MODULES))
def test_every_store_uses_the_shared_checks(name):
    module = MODULES[name]
    assert module._is_link is sqlite_file.is_link
    sample = Path("kho.sqlite")
    journals = getattr(module, "_journal_paths", None) or ImageTagStore._journal_paths
    assert journals(sample) == sqlite_file.journal_paths(sample)
    with closing(sqlite3.connect(":memory:")) as conn:
        module._guard(conn)  # giới hạn của chính kho này
        assert conn.getlimit(sqlite3.SQLITE_LIMIT_LENGTH) == module._MAX_SQLITE_LENGTH


@pytest.mark.parametrize("name", list(MODULES), ids=list(MODULES))
def test_lowered_step_limit_still_stops_queries(name, monkeypatch):
    # Hằng số của kho đọc lúc gọi: test hạ được giới hạn như trước T-136.
    module = MODULES[name]
    monkeypatch.setattr(module, "_MAX_VM_STEPS", 5_000)
    with closing(sqlite3.connect(":memory:")) as conn:
        module._guard(conn)
        with pytest.raises(sqlite3.OperationalError, match="interrupted"):
            conn.execute(
                "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n LIMIT 100000) "
                "SELECT count(*) FROM n"
            ).fetchone()


def test_hard_link_and_plain_file(tmp_path):
    plain = tmp_path / "a.sqlite"
    plain.write_bytes(b"")
    assert not sqlite_file.is_link(plain)
    assert not sqlite_file.is_link(tmp_path / "chua-co.sqlite")
    os.link(plain, tmp_path / "b.sqlite")
    assert sqlite_file.is_link(plain)  # hard link: tên kia có thể nằm ngoài data/


@pytest.mark.parametrize(
    ("data", "newer"),
    [
        (b"", False),
        (b"SQLite format 3\x00" + b"\x10\x00\x01", False),  # cụt trước byte 19
        (b"SQLite format 3\x00" + b"\x10\x00\x01\x01", False),
        (b"SQLite format 3\x00" + b"\x10\x00\x02\x02", False),
        (b"SQLite format 3\x00" + b"\x10\x00\x00\x00", False),  # 0: SQLite coi như 1
        (b"SQLite format 3\x00" + b"\x10\x00\x03\x01", True),
        (b"SQLite format 3\x00" + b"\x10\x00\x01\x03", True),
        (b"SQLite format 3\x00" + b"\x10\x00\xff\xff", True),
    ],
    ids=["trong", "cut", "1-1", "2-2", "0-0", "ghi-3", "doc-3", "ff"],
)
def test_newer_file_format(tmp_path, data, newer):
    path = tmp_path / "x.sqlite"
    path.write_bytes(data)
    assert sqlite_file.newer_file_format(path) is newer


# ================================================================ byte 18–19 (LC-T131-1 b, GN-1)


@pytest.mark.parametrize("offset", [18, 19], ids=["byte-18", "byte-19"])
@pytest.mark.parametrize("name", list(STORES), ids=list(STORES))
def test_newer_header_is_a_foreign_file_in_every_store(tmp_path, name, offset):
    path = tmp_path / "kho.sqlite"
    made(name, path)
    assert MODULES[name]._is_healthy(path)  # đối chứng: file do kho tạo
    set_byte(path, offset, 3)
    assert MODULES[name]._is_healthy(path) is False
    store = STORES[name](path=path)
    store._prepare()  # file lạ: cất sang một bên (nháp, thẻ ảnh) hay bỏ (ba kho lưu tạm)
    assert path.read_bytes()[offset] <= 2
    assert MODULES[name]._is_healthy(path)
    if name in MOVED_ASIDE:
        assert store.recovered_from is not None and store.recovered_from.exists()
        assert store.recovered_from.read_bytes()[offset] == 3  # bản cũ giữ nguyên
    else:
        assert store.reset_count == 1


def test_draft_with_newer_header_can_be_saved_again(tmp_path):
    path = tmp_path / "drafts.sqlite"
    store = DraftStore(path=path)
    old = store.save(DraftSnapshot(keyword="cổng inox"))
    set_byte(path, 18, 3)
    fresh = DraftStore(path=path)
    saved = fresh.save(DraftSnapshot(keyword="cửa cuốn"))  # trước T-136: lỗi mãi
    assert [item.id for item in fresh.list_drafts().drafts] == [saved.id]
    assert fresh.recovered_from is not None
    # File đã cất còn nguyên nháp cũ (đọc thẳng: mở bằng kho thì kho lại cất nó vì đầu file lạ).
    with closing(sqlite3.connect(fresh.recovered_from)) as conn:
        assert conn.execute("SELECT id FROM drafts").fetchall() == [(old.id,)]


# ================================================================ mã lỗi môi trường (GN-3)


def sqlite_error(code: int) -> sqlite3.OperationalError:
    exc = sqlite3.OperationalError("lỗi giả")
    exc.sqlite_errorcode = code
    return exc


@pytest.mark.parametrize(("code", "kept"), [(13, True), (8, True), (1, False), (11, False)])
@pytest.mark.parametrize("name", ["drafts", "site-index", "plan-cache", "search-cache"], ids=str)
def test_environment_errors_keep_the_file(tmp_path, monkeypatch, name, code, kept):
    module = MODULES[name]
    path = tmp_path / "kho.sqlite"
    made(name, path)
    assert module._KEEP_FILE_CODES is sqlite_file.KEEP_FILE_CODES
    assert 13 in module._KEEP_FILE_CODES  # search_cache trước T-136 thiếu mã này

    def failing(_conn):
        raise sqlite_error(code)

    monkeypatch.setattr(module, "_app_tables", failing)
    if kept:
        with pytest.raises(sqlite3.DatabaseError):
            module._is_healthy(path)
    else:
        assert module._is_healthy(path) is False


# ================================================================ kho nháp: LC-T131-1 (a), B.2, B.4


def raw(path: Path, sql: str, parameters: tuple = ()) -> None:
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute(sql, parameters)


def test_broken_text_cell_only_skips_that_draft(tmp_path):
    path = tmp_path / "drafts.sqlite"
    store = DraftStore(path=path)
    bad = store.save(DraftSnapshot(keyword="cổng inox"))
    good = store.save(DraftSnapshot(keyword="cửa cuốn"))
    raw(path, "UPDATE drafts SET title = CAST(? AS TEXT) WHERE id = ?", (b"\xff\xfe x", bad.id))
    for _attempt in (1, 2):
        listed = DraftStore(path=path).list_drafts()
        assert [item.id for item in listed.drafts] == [good.id]
        assert listed.skipped == 1
    assert DraftStore(path=path).recovered_from is None  # không cất cả file vì một ô
    assert DraftStore(path=path).load(good.id).keyword == "cửa cuốn"


def test_broken_id_does_not_break_plan_lookups(tmp_path):
    path = tmp_path / "drafts.sqlite"
    store = DraftStore(path=path)
    store.save(DraftSnapshot(keyword="cổng inox"))
    sheet_hash = "a" * 64
    data = f'{{"plan":{{"key":"B-001","sheet_hash":"{sheet_hash}"}}}}'
    raw(
        path,
        "INSERT INTO drafts VALUES (CAST(? AS TEXT), 't', 'k', '2026-11-10T00:00:00+07:00', 1, ?)",
        (b"\xff\xfe", data),
    )
    raw(path, "INSERT INTO plan_writes VALUES (CAST(? AS TEXT), '{}', 1)", (b"\xff\xfe",))
    assert store.find_plan_draft("B-001", sheet_hash) is None
    assert store.list_plan_writes() == []
    assert store.list_drafts().skipped == 1


def test_read_only_draft_file_says_read_only(tmp_path):
    path = tmp_path / "drafts.sqlite"
    store = DraftStore(path=path)
    store.save(DraftSnapshot(keyword="cổng inox"))
    os.chmod(path, stat.S_IREAD)
    try:
        with pytest.raises(DraftError) as info:
            DraftStore(path=path).save(DraftSnapshot(keyword="cửa cuốn"))
    finally:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    assert str(info.value) == drafts._MSG_READONLY
    assert "chỉ đọc" in str(info.value)


def test_db_message_cases():
    assert drafts._db_message(sqlite_error(8)) == drafts._MSG_READONLY
    assert drafts._db_message(sqlite_error(11)) == drafts._MSG_BROKEN
    assert "bận" in drafts._db_message(sqlite3.OperationalError("database is locked"))


def test_recovered_message_tells_about_links_and_sent_marks():
    text = drafts.MSG_RECOVERED.format(name="drafts.hong-20261110-120000.sqlite")
    assert "bị hỏng nên đã được cất sang một bên" in text  # câu cũ ghim ở test_app_drafts
    assert "lối tắt" in text and "đã gửi" in text and "WordPress" in text
    for page in ("app/views/home.py", "app/views/plan.py"):
        source = (ROOT / page).read_text(encoding="utf-8")
        assert "MSG_DRAFTS_MOVED = drafts.MSG_RECOVERED" in source


def test_write_page_shows_the_shared_recovered_message(project_root):
    path = drafts.DEFAULT_DRAFTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"day khong phai sqlite")
    at = pages.write_page(project_root)
    warnings = [w.value for w in at.warning if "cất sang một bên" in w.value]
    assert len(warnings) == 1
    assert "lối tắt" in warnings[0] and "đã gửi" in warnings[0]


# ================================================================ plan_cache: GN-2


def test_plan_cache_creates_both_tables_in_one_write_transaction(tmp_path, monkeypatch):
    statements: list[str] = []
    original = plan_cache._guard

    def traced(conn):
        original(conn)
        conn.set_trace_callback(statements.append)

    monkeypatch.setattr(plan_cache, "_guard", traced)
    PlanCacheStore(path=tmp_path / "plan.sqlite")._prepare()
    begin = statements.index("BEGIN IMMEDIATE")
    commit = statements.index("COMMIT", begin)
    creates = [i for i, sql in enumerate(statements) if sql.lstrip().upper().startswith("CREATE")]
    assert len(creates) == len(plan_cache._CREATE_TABLES)
    assert all(begin < i < commit for i in creates)


# ================================================================ chỉ chạy câu SQL hằng


def test_shared_module_only_runs_constant_sql():
    tree = ast.parse((ROOT / "seo_app/storage/sqlite_file.py").read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("execute", "executemany")
    ]
    assert len(calls) >= 8
    for call in calls:
        first = call.args[0]
        assert isinstance(first, ast.Constant | ast.Name), ast.unparse(first)
        if isinstance(first, ast.Name):  # câu tạo bảng của kho, câu đọc sqlite_master
            assert first.id in ("sql", "MASTER_SQL"), first.id

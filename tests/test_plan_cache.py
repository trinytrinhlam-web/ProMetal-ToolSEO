"""T-100: cache kế hoạch ``data/plan_cache.sqlite`` (``seo_app.storage.plan_cache``).

Điều kiện Lá Chắn LC-T094-29 (F3): SQL chỉ tham số ``?``; kiểm cấu trúc trước khi đọc; mọi dòng đọc
lại qua ``PlanRow``; sai một dòng hay khác mã băm Sheet thì bỏ cả cache; không lưu bí mật, không lưu
mã Sheet gốc. Không gọi Google.
"""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from seo_app.plan import model, sync
from seo_app.storage import plan_cache
from seo_app.storage.plan_cache import PlanCacheError, PlanCacheStore, sheet_hash

SHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-xyz"
NOW = datetime(2026, 10, 29, 9, 30, tzinfo=model.TIMEZONE)
VALUES = (
    ("Mã bài", "Từ khóa chính", "Ngày dự kiến", "Mã bài WordPress", "Ghi chú của thợ"),
    ("B-001", "sửa cửa cuốn", 46337, 77, "Khách «quen»\ndòng 2"),
    (),
    ("B-002", "cổng inox 304", 46340.5, "", True),
)


@pytest.fixture
def store(tmp_path):
    return PlanCacheStore(path=tmp_path / "plan_cache.sqlite")


def connect(store: PlanCacheStore) -> sqlite3.Connection:
    return closing(sqlite3.connect(store.path))


def tamper(store: PlanCacheStore, *sql: str | tuple[str, tuple]) -> None:
    with connect(store) as conn, conn:
        for item in sql:
            statement, params = item if isinstance(item, tuple) else (item, ())
            conn.execute(statement, params)


def test_round_trip_keeps_every_cell_and_time(store):
    store.save(SHEET_ID, VALUES, NOW)
    cached = store.load(SHEET_ID)
    assert cached.values == VALUES and cached.fetched_at == NOW
    assert cached.fetched_at.tzinfo is not None


def test_file_has_no_sheet_id(store):
    store.save(SHEET_ID, VALUES, NOW)
    data = Path(store.path).read_bytes()
    assert SHEET_ID.encode() not in data and sheet_hash(SHEET_ID).encode() in data


def test_another_sheet_is_not_read(store):
    store.save(SHEET_ID, VALUES, NOW)
    assert store.load("Z" * 44) is None
    assert store.load(SHEET_ID) is not None  # cache của Sheet cũ vẫn còn tới lần ghi sau


def test_empty_cache_and_missing_file(store):
    assert store.load(SHEET_ID) is None
    store.save(SHEET_ID, (), NOW)
    assert store.load(SHEET_ID).values == ()


def test_stale_and_future_times(store):
    store.save(SHEET_ID, VALUES, NOW)
    cached = store.load(SHEET_ID)
    assert not store.is_stale(cached, now=NOW + timedelta(minutes=4))
    assert store.is_stale(cached, now=NOW + timedelta(minutes=6))
    assert store.is_stale(cached, now=NOW - timedelta(minutes=10))  # tải «ở tương lai»


def test_save_refuses_bad_values_and_naive_time(store):
    with pytest.raises(PlanCacheError):
        store.save(SHEET_ID, (("a", {"x": 1}),), NOW)
    with pytest.raises(PlanCacheError):
        store.save(SHEET_ID, (("a",) * 27,), NOW)
    with pytest.raises(PlanCacheError):
        store.save(SHEET_ID, VALUES, datetime(2026, 10, 29, 9, 30))
    with pytest.raises(PlanCacheError):
        store.save(SHEET_ID, (("a", float("nan")),), NOW)


BROKEN = {
    "o-la-dict": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ('["B-001", {"a": 1}]',)),
    "khong-phai-list": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ('{"a": 1}',)),
    "qua-26-o": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", (json.dumps(["x"] * 27),)),
    "nan": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ('["B-001", NaN]',)),
    "json-hong": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ("[1, 2",)),
    "long-sau": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ("[" * 5000 + "]" * 5000,)),
    "dong-rong": ("UPDATE sheet_rows SET cells = ? WHERE number = 2", ("[]",)),
    "sua-mot-o": ("UPDATE sheet_rows SET cells = ? WHERE number = 2",
                  (json.dumps(["B-001", "từ khóa khác", 46337, 77, "x"]),)),
    "so-dong-ngoai": ("UPDATE sheet_rows SET number = 9 WHERE number = 4", ()),
    "sai-phien-ban": ("UPDATE info SET value = '9' WHERE key = 'schema_version'", ()),
    "gio-khong-mui": ("UPDATE info SET value = '2026-10-29T09:30:00' WHERE key = 'fetched_at'", ()),
    "them-khoa-info": ("INSERT INTO info VALUES ('secret', 'sk-ant-x')", ()),
    "dem-dong-sai": ("UPDATE info SET value = 'abc' WHERE key = 'row_count'", ()),
    "trigger": ("CREATE TRIGGER t AFTER INSERT ON info BEGIN DELETE FROM sheet_rows; END", ()),
    "view": ("CREATE VIEW v AS SELECT 1", ()),
    "bang-la": ("CREATE TABLE extra (x)", ()),
    "chi-muc": ("CREATE INDEX i ON sheet_rows (cells)", ()),
}  # fmt: skip


@pytest.mark.parametrize("change", list(BROKEN), ids=list(BROKEN))
def test_any_broken_row_or_structure_drops_the_whole_cache(store, change):
    store.save(SHEET_ID, VALUES, NOW)
    tamper(store, BROKEN[change])
    assert store.load(SHEET_ID) is None
    store.save(SHEET_ID, VALUES, NOW)  # tạo lại sạch
    assert store.load(SHEET_ID).values == VALUES


def test_not_a_database_is_replaced(store):
    store.path.write_bytes(b"day khong phai sqlite" * 100)
    assert store.load(SHEET_ID) is None
    store.save(SHEET_ID, VALUES, NOW)
    assert store.load(SHEET_ID).values == VALUES and store.reset_count >= 1


def test_trigger_never_runs_when_saving(store):
    store.save(SHEET_ID, VALUES, NOW)
    tamper(
        store,
        "CREATE TABLE stolen (x)",
        "CREATE TRIGGER t AFTER INSERT ON sheet_rows BEGIN INSERT INTO stolen VALUES (1); END",
    )
    store.save(SHEET_ID, VALUES, NOW)
    with connect(store) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    assert "stolen" not in names and "t" not in names


def test_cached_rows_go_through_plan_row(store):
    rlo = chr(0x202E)
    values = (
        ("Mã bài", "Từ khóa chính", "Ghi chú của thợ"),
        ("B-001", f"sửa{rlo} cửa «cuốn»", "<script>x</script>"),
        ("B-002", "x", ""),  # từ khóa quá ngắn: bỏ dòng, có câu báo
    )
    store.save(SHEET_ID, values, NOW)
    cached = store.load(SHEET_ID)
    plan = sync.parse_sheet(cached.values, fetched_at=cached.fetched_at, from_cache=True)
    (only,) = plan.rows
    assert only.plan.keyword == "sửa cửa ‹cuốn›" and plan.skipped == 1 and plan.from_cache


def test_sql_uses_parameters_only():
    source = Path(plan_cache.__file__).read_text(encoding="utf-8")
    assert not re.search(r"execute(many)?\(\s*f[\"']", source)
    assert ".format(" not in "".join(re.findall(r"execute\([^)]*\)", source))


def test_save_with_utc_time_reads_back_in_vietnam_time(store):
    store.save(SHEET_ID, VALUES, datetime(2026, 10, 29, 2, 30, tzinfo=UTC))
    assert store.load(SHEET_ID).fetched_at == NOW


def test_clear_removes_the_file(store):
    store.save(SHEET_ID, VALUES, NOW)
    store.clear()
    assert not store.path.exists() and store.load(SHEET_ID) is None

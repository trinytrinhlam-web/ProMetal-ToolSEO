"""Cache kế hoạch đọc từ Google Sheets (T-100; thiết kế T-094 mục 2.6; Lá Chắn LC-T094-29).

File ``data/plan_cache.sqlite`` (``data/``, ``*.sqlite`` đã bị ``.gitignore`` chặn) giữ **đúng các
ô** lần đọc gần nhất của tab «KeHoach» trả về (``SheetsClient.read_plan_values``), để vẽ trang Kế
hoạch ngay khi mở và khi mất mạng (nhãn «bản lưu lúc 14:05»). Nguồn thật là Google Sheets: cache
cũ hơn ``DEFAULT_MAX_AGE_MINUTES`` phút thì tải lại; nơi gọi **luôn** đọc lại Sheet trước mọi lệnh
ghi và trước khi mở Soạn bài từ một dòng (``seo_app.plan.sync``). Xóa file vẫn tạo lại được.

An toàn (F3, LC-T094-29):

- Không lưu bí mật, không lưu mã Sheet gốc: chỉ mã băm SHA-256 của mã Sheet (``sheet_hash``).
  Đổi Sheet (mã băm khác) thì cache cũ không dùng, lần tải sau ghi đè.
- Cấu trúc file chưa tin cậy: trước mọi truy vấn khác, ``sqlite_master`` phải khớp đúng hai bảng
  app tạo (như kho thẻ ảnh T-070, T-074), kiểm **trong cùng giao dịch** với thao tác; truy vấn bị
  giới hạn số bước và độ dài giá trị; không chạy hàm trong khung nhìn, trigger của file.
- Dữ liệu chưa tin cậy: giới hạn số dòng, độ dài từng ô (đo theo byte trước khi đọc vào bộ nhớ);
  mỗi dòng là danh sách ô đúng kiểu (chữ, số hữu hạn, đúng/sai); mã băm của toàn bộ ô phải khớp.
  **Một dòng sai** (hay sai phiên bản, sai giờ) là bỏ cả cache. Nơi dùng đọc lại mọi dòng qua
  ``PlanRow`` (``sync.parse_sheet``), như dữ liệu vừa tải từ Sheet.
- Mọi câu SQL dùng tham số ``?``; không ``pickle``, không ``eval``.
"""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT

DEFAULT_PLAN_CACHE_FILE = PROJECT_ROOT / "data" / "plan_cache.sqlite"
DEFAULT_MAX_AGE_MINUTES = 5.0
SCHEMA_VERSION = "1"
MAX_ROWS = 1001  # dòng tiêu đề + 1.000 dòng kế hoạch (như ``SheetsClient``)
MAX_COLUMNS = 26
# Câu trả lời của Google tối đa 2 MB (``sheets.MAX_RESPONSE_BYTES``); JSON lưu lại có thể dài hơn
# chút vì chữ có dấu được ghi thoát (``\u…``). Dòng hay cả file dài hơn mức này là bị sửa tay.
_MAX_ROW_BYTES = 8 * 1024 * 1024
_MAX_TOTAL_BYTES = 16 * 1024 * 1024
_MAX_INFO_CHARS = 200
_SAFE_INT = 2**53
_CLOCK_SKEW = timedelta(minutes=5)  # thời điểm tải "ở tương lai" quá mức này = cache cũ
_SQLITE_TIMEOUT = 5
_HEALTH_TIMEOUT = 1
_WRITE_TIMEOUT = 1
# Lớp phòng sau lớp kiểm cấu trúc (như ``image_tags``): số bước tối đa của một truy vấn, độ dài
# tối đa của một giá trị SQLite.
_MAX_VM_STEPS = 50_000_000
_PROGRESS_EVERY = 1000
_MAX_SQLITE_LENGTH = _MAX_ROW_BYTES + 1024
_SQLITE_CORRUPT = 11
_SQLITE_NOTADB = 26
_SQLITE_TOOBIG = 18
_SQLITE_INTERRUPT = 9

_CREATE_TABLES = (
    "CREATE TABLE IF NOT EXISTS sheet_rows (number INTEGER PRIMARY KEY, cells TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
)
_INFO_KEYS = frozenset({"schema_version", "sheet_hash", "fetched_at", "row_count", "values_hash"})
_MASTER_SQL = "SELECT type, name, tbl_name, substr(sql, 1, ?) FROM sqlite_master LIMIT ?"
_MAX_SQL_BYTES = 2048

CellValue = str | int | float | bool
Values = tuple[tuple[CellValue, ...], ...]


class PlanCacheError(Exception):
    """Lỗi file cache kế hoạch; câu tiếng Việt cố định, hiện thẳng được cho người dùng."""


def sheet_hash(sheet_id: str) -> str:
    """Mã băm SHA-256 (hex) của mã Sheet: cache và kho nháp chỉ giữ mã băm, không giữ mã gốc."""
    return hashlib.sha256(str(sheet_id).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CachedPlan:
    """Các ô của tab «KeHoach» lần đọc gần nhất (dòng 1 là tiêu đề), kèm thời điểm tải."""

    values: Values
    fetched_at: datetime


@dataclass
class PlanCacheStore:
    """Cache trong một file SQLite. Mỗi thao tác mở và đóng kết nối riêng."""

    # Tra lúc tạo (không lúc import) để test trỏ được sang thư mục tạm.
    path: Path = field(default_factory=lambda: DEFAULT_PLAN_CACHE_FILE)
    timezone: str = DEFAULT_TIMEZONE
    max_age_minutes: float = DEFAULT_MAX_AGE_MINUTES
    reset_count: int = field(default=0, init=False)
    """Số lần file cache hỏng hay lạ bị bỏ đi (để test và báo nếu cần)."""

    def load(self, sheet_id: str) -> CachedPlan | None:
        """Cache của Sheet ``sheet_id``. Chưa có, của Sheet khác, hỏng hay lạ: ``None`` (không ném
        lỗi). Hỏng hay lạ thì bỏ luôn file, lần ghi sau tạo lại sạch."""
        try:
            return self._load(sheet_hash(sheet_id))
        except _Corrupt:
            self._reset_quietly()
            return None
        except sqlite3.DatabaseError as exc:
            if _is_corrupt(exc):
                self._reset_quietly()
            return None
        except (PlanCacheError, OSError):
            return None

    def save(
        self, sheet_id: str, values: Sequence[Sequence[CellValue]], fetched_at: datetime
    ) -> None:
        """Ghi đè toàn bộ cache bằng ``values`` (đúng các ô ``read_plan_values`` trả) trong một
        giao dịch. Lỗi: ``PlanCacheError`` (dữ liệu vẫn dùng được, chỉ không lưu tạm)."""
        if fetched_at.tzinfo is None:
            raise PlanCacheError("Thời điểm tải kế hoạch phải kèm múi giờ.")
        rows = _checked_values(values)
        if rows is None:
            raise PlanCacheError("Kế hoạch đọc từ Google Sheets không đúng dạng nên không lưu tạm.")
        encoded = [(number, _dump(row)) for number, row in enumerate(rows, start=1) if row]
        info = [
            ("schema_version", SCHEMA_VERSION),
            ("sheet_hash", sheet_hash(sheet_id)),
            ("fetched_at", fetched_at.isoformat()),
            ("row_count", str(len(rows))),
            ("values_hash", _values_hash(rows)),
        ]
        try:
            with self._connect(write=True, timeout=_WRITE_TIMEOUT) as conn:
                conn.execute("DELETE FROM sheet_rows")
                conn.execute("DELETE FROM info")
                conn.executemany("INSERT INTO sheet_rows (number, cells) VALUES (?, ?)", encoded)
                conn.executemany("INSERT INTO info (key, value) VALUES (?, ?)", info)
        except _Corrupt:
            self._reset_quietly()
            raise PlanCacheError(_MSG_BROKEN) from None
        except sqlite3.DatabaseError as exc:
            raise PlanCacheError(_db_message(exc)) from None
        except OSError as exc:
            raise PlanCacheError(_MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")) from None

    def is_stale(self, cached: CachedPlan, *, now: datetime | None = None) -> bool:
        """Cũ hơn ``max_age_minutes`` phút, hay ở «tương lai» (đồng hồ bị chỉnh, file sửa tay)."""
        age = (now or datetime.now(ZoneInfo(self.timezone))) - cached.fetched_at
        return age < -_CLOCK_SKEW or age > timedelta(minutes=self.max_age_minutes)

    def clear(self) -> None:
        """Xóa file cache (lần sau tự tải lại)."""
        try:
            self._reset()
        except OSError as exc:
            raise PlanCacheError(_MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")) from None

    # ------------------------------------------------------------ nội bộ

    def _load(self, wanted_hash: str) -> CachedPlan | None:
        with self._connect(write=False) as conn:
            info_rows = conn.execute(
                "SELECT key, substr(value, 1, ?) FROM info LIMIT 10", (_MAX_INFO_CHARS + 1,)
            ).fetchall()
            info = {}
            for key, value in info_rows:
                if not isinstance(key, str) or not isinstance(value, str):
                    raise _Corrupt
                if len(value) > _MAX_INFO_CHARS or key in info:
                    raise _Corrupt
                info[key] = value
            if not info:
                return None  # cache mới tạo, chưa tải lần nào
            if set(info) != _INFO_KEYS or info["schema_version"] != SCHEMA_VERSION:
                raise _Corrupt
            if info["sheet_hash"] != wanted_hash:
                return None  # cache của Sheet khác (đổi GOOGLE_SHEET_ID): tải lại, ghi đè
            fetched_at = _parse_time(info["fetched_at"], self.timezone)
            count = _parse_count(info["row_count"])
            total, biggest, numbers, low, high = conn.execute(
                "SELECT COALESCE(SUM(length(CAST(cells AS BLOB))), 0), "
                "COALESCE(MAX(length(CAST(cells AS BLOB))), 0), COUNT(*), MIN(number), "
                "MAX(number) FROM sheet_rows"
            ).fetchone()
            if total > _MAX_TOTAL_BYTES or biggest > _MAX_ROW_BYTES or numbers > MAX_ROWS:
                raise _Corrupt
            if numbers and (not 1 <= low <= high <= count):
                raise _Corrupt
            stored = conn.execute("SELECT number, cells FROM sheet_rows ORDER BY number").fetchall()
        rows: list[tuple[CellValue, ...]] = [()] * count
        for number, cells in stored:
            if type(number) is not int or not isinstance(cells, str):
                raise _Corrupt
            row = _load_row(cells)
            if row is None or not row:
                raise _Corrupt
            rows[number - 1] = row
        if _values_hash(rows) != info["values_hash"]:
            raise _Corrupt
        return CachedPlan(values=tuple(rows), fetched_at=fetched_at)

    @contextmanager
    def _connect(
        self, *, write: bool, timeout: float | None = None
    ) -> Iterator[sqlite3.Connection]:
        """Mở file, mở giao dịch, kiểm cấu trúc (``_app_tables``) **trước** mọi truy vấn khác, trong
        cùng giao dịch với thao tác. Cấu trúc lạ: ``_Corrupt``."""
        self._prepare()
        try:
            with closing(
                sqlite3.connect(self.path, timeout=timeout or _SQLITE_TIMEOUT, isolation_level=None)
            ) as conn:
                _guard(conn)
                conn.text_factory = _decode_text
                conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                try:
                    if _app_tables(conn) != _expected_tables():
                        raise _Corrupt
                    yield conn
                except BaseException:
                    conn.execute("ROLLBACK")
                    raise
                conn.execute("COMMIT")
        except sqlite3.DatabaseError as exc:
            if _is_too_big(exc) or _is_interrupted(exc):
                raise _Corrupt from None
            raise

    def _prepare(self) -> None:
        """Tạo thư mục; liên kết tắt hay file hỏng/lạ thì xóa; tạo bảng nếu chưa có."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.is_symlink() or (self.path.exists() and not _is_healthy(self.path)):
                # Liên kết tắt có thể trỏ ra ngoài data/ (F1): chỉ xóa chính liên kết.
                self._reset()
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                _guard(conn)
                for sql in _CREATE_TABLES:
                    conn.execute(sql)
        except sqlite3.DatabaseError as exc:
            raise PlanCacheError(_db_message(exc)) from None
        except OSError as exc:
            raise PlanCacheError(_MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")) from None

    def _reset(self) -> None:
        self.path.unlink(missing_ok=True)
        for suffix in ("-journal", "-wal", "-shm"):
            self.path.with_name(self.path.name + suffix).unlink(missing_ok=True)
        self.reset_count += 1

    def _reset_quietly(self) -> None:
        with suppress(OSError):  # không xóa được: lần ghi sau sẽ báo lỗi rõ ràng
            self._reset()


# ------------------------------------------------------------------ kiểm dữ liệu

_MSG_BROKEN = "File lưu tạm kế hoạch bị lỗi nên đã bỏ; lần tải sau tạo lại."
_MSG_IO = "Không ghi được file lưu tạm kế hoạch ({detail})."


class _Corrupt(Exception):
    """Nội dung hay cấu trúc cache sai khuôn (nội bộ)."""


def _is_cell(value: object) -> bool:
    if isinstance(value, bool | str):
        return True
    if isinstance(value, int):
        return -_SAFE_INT <= value <= _SAFE_INT
    return isinstance(value, float) and math.isfinite(value)


def _checked_values(values: object) -> list[tuple[CellValue, ...]] | None:
    """Các dòng ô đúng khuôn ``read_plan_values`` (≤ ``MAX_ROWS`` dòng, ≤ 26 ô mỗi dòng)."""
    if (
        not isinstance(values, Sequence)
        or isinstance(values, str | bytes)
        or len(values) > MAX_ROWS
    ):
        return None
    rows: list[tuple[CellValue, ...]] = []
    for row in values:
        if not isinstance(row, Sequence) or isinstance(row, str | bytes) or len(row) > MAX_COLUMNS:
            return None
        if not all(_is_cell(cell) for cell in row):
            return None
        rows.append(tuple(row))
    return rows


def _dump(row: Sequence[CellValue]) -> str:
    return json.dumps(list(row), ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def _values_hash(rows: Sequence[Sequence[CellValue]]) -> str:
    return hashlib.sha256(_dump([_dump(row) for row in rows]).encode("utf-8")).hexdigest()


def _load_row(text: str) -> tuple[CellValue, ...] | None:
    try:
        row = json.loads(text, parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        return None
    if not isinstance(row, list) or len(row) > MAX_COLUMNS or not all(_is_cell(c) for c in row):
        return None
    return tuple(row)


def _reject_constant(_name: str) -> float:
    raise ValueError("NaN/Infinity không phải ô hợp lệ")


def _parse_time(value: str, timezone: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise _Corrupt from None
    if parsed.tzinfo is None:
        raise _Corrupt
    return parsed.astimezone(ZoneInfo(timezone))


def _parse_count(value: str) -> int:
    if not value.isascii() or not value.isdigit() or len(value) > 5:
        raise _Corrupt
    count = int(value)
    if not 0 <= count <= MAX_ROWS:
        raise _Corrupt
    return count


def _decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise _Corrupt from None


# ------------------------------------------------------------------ kiểm cấu trúc file


def _guard(conn: sqlite3.Connection) -> None:
    """File là dữ liệu chưa tin cậy (F3): không chạy hàm "không vô hại" trong khung nhìn, trigger
    của file; dừng truy vấn quá ``_MAX_VM_STEPS`` bước; không cho giá trị dài quá
    ``_MAX_SQLITE_LENGTH``. Lớp chặn chính là ``_app_tables``."""
    conn.execute("PRAGMA trusted_schema = OFF")
    conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, _MAX_SQLITE_LENGTH)
    steps = 0

    def stop_when_too_long() -> int:
        nonlocal steps
        steps += _PROGRESS_EVERY
        return 1 if steps > _MAX_VM_STEPS else 0

    conn.set_progress_handler(stop_when_too_long, _PROGRESS_EVERY)


@cache
def _expected_schema() -> frozenset[tuple]:
    """Các dòng ``sqlite_master`` của hai bảng app tạo, dựng bằng chính ``_CREATE_TABLES`` trong
    bộ nhớ (khớp đúng cách SQLite đang chạy ghi lại câu lệnh, kèm chỉ mục tự sinh)."""
    with closing(sqlite3.connect(":memory:")) as conn:
        for sql in _CREATE_TABLES:
            conn.execute(sql)
        return frozenset(tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, 16)))


def _expected_tables() -> frozenset[tuple]:
    return _expected_schema()


def _app_tables(conn: sqlite3.Connection) -> frozenset[tuple] | None:
    """Các dòng ``sqlite_master`` của file, đọc vào danh sách có giới hạn (như ``image_tags``):
    thừa dòng hay một dòng ``(loại, tên)`` lặp lại thì ``None``. Bất kỳ khung nhìn, trigger, bảng
    ảo, chỉ mục hay bảng lạ nào làm tập này khác ``_expected_schema``."""
    limit = len(_expected_schema())
    rows = [tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, limit + 1))]
    if len(rows) > limit or len({row[:2] for row in rows}) != len(rows):
        return None
    return frozenset(rows)


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, cấu trúc đúng như app tạo (hay còn trống), ``quick_check`` ổn.
    ``False`` chỉ khi chắc chắn hỏng hay lạ; lỗi khác (bận, khóa) được ném lại."""
    try:
        with closing(sqlite3.connect(path, timeout=_HEALTH_TIMEOUT, isolation_level=None)) as conn:
            _guard(conn)
            conn.execute("BEGIN")
            try:
                tables = _app_tables(conn)
                if tables is None or (tables and tables != _expected_schema()):
                    return False
                return conn.execute("PRAGMA quick_check").fetchone() == ("ok",)
            finally:
                conn.execute("ROLLBACK")
    except sqlite3.DatabaseError as exc:
        if _is_corrupt(exc) or _is_too_big(exc) or _is_interrupted(exc):
            return False
        raise


def _code(exc: sqlite3.DatabaseError) -> int | None:
    code = getattr(exc, "sqlite_errorcode", None)
    return code & 0xFF if isinstance(code, int) else None


def _is_corrupt(exc: sqlite3.DatabaseError) -> bool:
    code = _code(exc)
    if code is not None:
        return code in (_SQLITE_CORRUPT, _SQLITE_NOTADB)
    text = str(exc).lower()
    return "not a database" in text or "malformed" in text


def _is_too_big(exc: sqlite3.DatabaseError) -> bool:
    return _code(exc) == _SQLITE_TOOBIG or "too big" in str(exc).lower()


def _is_interrupted(exc: sqlite3.DatabaseError) -> bool:
    return _code(exc) == _SQLITE_INTERRUPT or "interrupted" in str(exc).lower()


def _is_busy(exc: sqlite3.DatabaseError) -> bool:
    text = str(exc).lower()
    return isinstance(exc, sqlite3.OperationalError) and ("locked" in text or "busy" in text)


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if _is_busy(exc):
        return "File lưu tạm kế hoạch đang bận. Thử lại sau giây lát."
    if _is_corrupt(exc):
        return _MSG_BROKEN
    return (
        "Không mở được file lưu tạm kế hoạch (có thể chương trình khác đang giữ file, hoặc không "
        "có quyền ghi). Kế hoạch vừa tải vẫn dùng được."
    )


__all__ = [
    "DEFAULT_MAX_AGE_MINUTES",
    "DEFAULT_PLAN_CACHE_FILE",
    "CachedPlan",
    "PlanCacheError",
    "PlanCacheStore",
    "sheet_hash",
]

"""Phần kiểm file dùng chung của 5 kho SQLite trong ``data/`` (T-136; Lá Chắn T-131 B.1).

Năm kho: nháp (``drafts``), thẻ ảnh sửa tay (``image_tags``), danh sách bài đã đăng
(``site_index``), kế hoạch (``plan_cache``), số liệu Search Console (``search_cache``). File của kho
là dữ liệu chưa tin cậy (F3): chương trình khác có thể sửa, thay, hay đặt liên kết vào chỗ của nó.

Mỗi kho giữ hàm cùng tên của mình (``_guard``, ``_is_link``, ``_app_tables``, ``_is_healthy``…) làm
lớp mỏng gọi vào đây, kèm hằng số riêng của kho đọc **lúc gọi**: chỗ gọi trong kho, chỗ test hạ giới
hạn hay vá từng hàm của kho đều như trước. Hai kiểu so cấu trúc:

- ``app_rows`` (ba kho lưu tạm): mọi dòng ``sqlite_master`` khớp đúng bộ app tạo (file còn trống
  thì được);
- ``app_table_names`` (kho nháp, kho thẻ ảnh): từng bảng có trong file khớp đúng; bảng thiếu thì
  được (file cũ, app tạo thêm).

Không nhập gì từ ``seo_app.storage`` (gói này nạp các kho).
"""

from __future__ import annotations

import sqlite3
import stat
from collections.abc import Callable, Iterable, Mapping
from contextlib import closing
from pathlib import Path

from seo_app.images.data_dir import is_link as _is_link_entry

JOURNAL_SUFFIXES = ("-journal", "-wal", "-shm")
MASTER_SQL = "SELECT type, name, tbl_name, substr(sql, 1, ?) FROM sqlite_master LIMIT ?"
# Mã lỗi SQLite (byte thấp) do môi trường, không do file: quyền (3), bận (5), khóa (6), thiếu bộ
# nhớ (7), chỉ đọc (8), vào ra (10), đầy ổ (13), không mở được (14), giao thức khóa (15). Bước kiểm
# file gặp các mã này thì ném lại để kho báo lỗi mà **không** bỏ file (LC-T122-1). 13: T-042 ghim
# «đầy ổ không xóa file»; trước T-136 ``search_cache`` thiếu mã này (Soi Lỗi T-131 GN-3).
KEEP_FILE_CODES = frozenset({3, 5, 6, 7, 8, 10, 13, 14, 15})
SQLITE_READONLY = 8
# Byte 18 (phiên bản ghi) và 19 (phiên bản đọc) của đầu file SQLite: 1 (kiểu cũ) hay 2 (WAL); 0
# SQLite coi như 1. Lớn hơn 2: SQLite mở file **chỉ đọc** (byte 18: mọi lần ghi báo «readonly»,
# mã 8, lỗi môi trường nên file được giữ và kho kẹt mãi ở câu báo lỗi) hay không đọc được (byte
# 19: «not a database»). App không bao giờ ghi giá trị như vậy: file lạ (LC-T131-1 b, Soi Lỗi T-131
# GN-1). Đã thử SQLite 3.53.1: byte 18 = 3, 255 → đọc được, ghi lỗi mã 8; byte 19 = 3, 255 → mã 26.
_FORMAT_VERSION_OFFSETS = (18, 19)
_MAX_FORMAT_VERSION = 2
_SCHEMA_ROWS_LIMIT = 64  # dựng cấu trúc mẫu trong bộ nhớ: mỗi kho chỉ vài dòng


class _Undecodable(Exception):
    """UTF-8 hỏng trong chữ đọc từ file lúc kiểm (nội bộ): file lạ (LC-T122-1)."""


def _decode_strict(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise _Undecodable from None


# ------------------------------------------------------------------ liên kết, file nhật ký


def journal_paths(path: Path) -> tuple[Path, ...]:
    """Ba file nhật ký SQLite đi kèm ``path``."""
    return tuple(path.with_name(path.name + suffix) for suffix in JOURNAL_SUFFIXES)


def is_link(path: Path) -> bool:
    """Liên kết tắt (symlink, junction, reparse point trỏ đi chỗ khác: ``data_dir.is_link``) hay
    hard link (file thường có hơn một tên; tên kia có thể nằm ngoài ``data/``). SQLite không bao giờ
    tự tạo hard link. Chưa có trên ổ thì ``False``."""
    if _is_link_entry(path):
        return True
    try:
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISREG(info.st_mode) and info.st_nlink > 1


def remove_link(path: Path) -> None:
    """Chỉ gỡ chính liên kết (F1): file, thư mục nó trỏ tới, tên kia của hard link giữ nguyên."""
    try:
        path.unlink()
    except (IsADirectoryError, PermissionError):
        path.rmdir()  # junction Windows: xóa chính junction, không đụng thư mục đích


# ------------------------------------------------------------------ kết nối tới file lạ


def guard(
    conn: sqlite3.Connection, *, max_length: int, max_steps: int, progress_every: int
) -> None:
    """File là dữ liệu chưa tin cậy (F3): không chạy hàm «không vô hại» trong khung nhìn, trigger
    của file; dừng truy vấn quá ``max_steps`` bước trên kết nối này (SQLite báo «interrupted»);
    không cho chuỗi, khối byte dài quá ``max_length`` (``SQLITE_TOOBIG``). Lớp chặn chính là kiểm
    cấu trúc (``app_rows``, ``app_table_names``); đây là lớp phòng sau, không phải giới hạn thời
    gian."""
    conn.execute("PRAGMA trusted_schema = OFF")
    conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, max_length)
    steps = 0

    def stop_when_too_long() -> int:
        nonlocal steps
        steps += progress_every
        return 1 if steps > max_steps else 0

    conn.set_progress_handler(stop_when_too_long, progress_every)


# ------------------------------------------------------------------ so cấu trúc


def _master_rows(conn: sqlite3.Connection, *, max_sql_bytes: int, limit: int) -> list[tuple] | None:
    """Các dòng ``sqlite_master`` đọc vào **danh sách** có ``LIMIT`` (LC-T070-1): nhiều dòng hơn
    ``limit``, hay một dòng ``(loại, tên)`` lặp lại (``writable_schema``), thì ``None``."""
    rows = [tuple(row) for row in conn.execute(MASTER_SQL, (max_sql_bytes, limit + 1))]
    if len(rows) > limit or len({row[:2] for row in rows}) != len(rows):
        return None
    return rows


def schema_rows(create_sqls: Iterable[str], *, max_sql_bytes: int) -> frozenset[tuple]:
    """Các dòng ``sqlite_master`` (chữ) của các bảng app tạo, dựng bằng chính ``create_sqls`` trong
    bộ nhớ: khớp đúng cách SQLite đang chạy ghi lại câu lệnh, kèm chỉ mục tự sinh."""
    with closing(sqlite3.connect(":memory:")) as conn:
        for sql in create_sqls:
            conn.execute(sql)
        rows = conn.execute(MASTER_SQL, (max_sql_bytes, _SCHEMA_ROWS_LIMIT)).fetchall()
    return frozenset(tuple(row) for row in rows)


def schema_by_table(
    create_sqls: Iterable[str], *, max_sql_bytes: int
) -> dict[bytes, frozenset[tuple]]:
    """Như ``schema_rows`` nhưng đọc thành byte và chia theo tên bảng (``tbl_name``)."""
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.text_factory = bytes
        for sql in create_sqls:
            conn.execute(sql)
        rows = conn.execute(MASTER_SQL, (max_sql_bytes, _SCHEMA_ROWS_LIMIT)).fetchall()
    schema: dict[bytes, set[tuple]] = {}
    for row in rows:
        schema.setdefault(row[2], set()).add(tuple(row))
    return {name: frozenset(items) for name, items in schema.items()}


def app_rows(
    conn: sqlite3.Connection, expected: frozenset[tuple], *, max_sql_bytes: int
) -> frozenset[tuple] | None:
    """Các dòng ``sqlite_master`` của file (ba kho lưu tạm), hay ``None`` khi thừa dòng, lặp dòng.
    Khung nhìn, trigger, bảng ảo, chỉ mục hay bảng lạ nào cũng làm tập này khác ``expected``."""
    rows = _master_rows(conn, max_sql_bytes=max_sql_bytes, limit=len(expected))
    return None if rows is None else frozenset(rows)


def app_table_names(
    conn: sqlite3.Connection,
    expected: Mapping[bytes, frozenset[tuple]],
    *,
    max_sql_bytes: int,
) -> frozenset[bytes] | None:
    """Tên các bảng của app có trong file (kho nháp, kho thẻ ảnh), nếu mọi đối tượng trong file đều
    khớp đúng ``expected`` (bảng thiếu thì được); có gì khác thì ``None``: khung nhìn, trigger,
    bảng ảo, chỉ mục hay bảng lạ, câu tạo bảng khác chữ, ``WITHOUT ROWID``…

    Đọc thành byte (``text_factory`` tạm là ``bytes``, trả lại như cũ sau khi đọc): UTF-8 hỏng trong
    ``sqlite_master`` là «khác», không phải lỗi giải mã (LC-T122-1)."""
    limit = sum(len(items) for items in expected.values())
    factory = conn.text_factory
    conn.text_factory = bytes
    try:
        rows = _master_rows(conn, max_sql_bytes=max_sql_bytes, limit=limit)
    finally:
        conn.text_factory = factory
    if rows is None:
        return None
    found: dict[bytes, set[tuple]] = {}
    for row in rows:
        found.setdefault(row[2], set()).add(row)
    for name, items in found.items():
        if name not in expected or items != expected[name]:
            return None
    return frozenset(found)


# ------------------------------------------------------------------ kiểm cả file


def newer_file_format(path: Path) -> bool:
    """Byte 18 hay 19 của đầu file lớn hơn 2 (``_FORMAT_VERSION_OFFSETS``): file lạ. Đọc 20 byte
    đầu, không mở bằng SQLite. File ngắn hơn (trống, cụt): ``False``, để SQLite tự xét."""
    end = max(_FORMAT_VERSION_OFFSETS) + 1
    with path.open("rb") as handle:
        head = handle.read(end)
    return len(head) >= end and any(
        head[offset] > _MAX_FORMAT_VERSION for offset in _FORMAT_VERSION_OFFSETS
    )


def code(exc: sqlite3.DatabaseError) -> int | None:
    """Mã lỗi SQLite (byte thấp, bỏ phần mở rộng); lỗi không kèm mã thì ``None``."""
    value = getattr(exc, "sqlite_errorcode", None)
    return value & 0xFF if isinstance(value, int) else None


def is_busy(exc: sqlite3.DatabaseError) -> bool:
    """File đang bị kết nối khác khóa (không phải hỏng)."""
    text = str(exc).lower()
    return isinstance(exc, sqlite3.OperationalError) and ("locked" in text or "busy" in text)


def keeps_file(exc: sqlite3.DatabaseError) -> bool:
    """Lỗi do môi trường (bận, khóa, quyền, vào ra, chỉ đọc, đầy ổ…): giữ file, chỉ báo lỗi."""
    return is_busy(exc) or code(exc) in KEEP_FILE_CODES


def is_healthy(
    path: Path,
    *,
    timeout: float,
    guard: Callable[[sqlite3.Connection], None],
    app_tables: Callable[[sqlite3.Connection], frozenset | None],
    complete: frozenset | None = None,
    max_bytes: int | None = None,
    strict_text: bool = False,
    extra: Callable[[sqlite3.Connection, frozenset], bool] | None = None,
) -> bool:
    """Bước kiểm file của kho nháp và ba kho lưu tạm: file không quá ``max_bytes``, đầu file đúng
    phiên bản (``newer_file_format``), là SQLite đọc được, cấu trúc đúng (``app_tables`` khác
    ``None``; có ``complete`` thì file còn trống hoặc khớp đủ), ``quick_check`` ổn, rồi ``extra``
    (kho nháp: không có ô dài quá giới hạn). Mọi bước trong **một** giao dịch đọc, cấu trúc kiểm
    trước mọi truy vấn khác.

    ``False`` chỉ khi **chắc chắn** hỏng hay lạ: cấu trúc khác, UTF-8 hỏng trong ``sqlite_master``
    (``strict_text``), SQLite báo hỏng / không phải cơ sở dữ liệu / «unsupported file format», giá
    trị quá dài, quá số bước. Lỗi do môi trường (``keeps_file``) được ném lại để kho báo lỗi mà
    **không** bỏ file.

    ``guard``, ``app_tables`` là hàm của kho, nơi gọi chuyển vào lúc gọi (test vá được hàm của
    từng kho)."""
    if max_bytes is not None and path.stat().st_size > max_bytes:
        return False
    if newer_file_format(path):
        return False
    try:
        with closing(sqlite3.connect(path, timeout=timeout, isolation_level=None)) as conn:
            guard(conn)
            if strict_text:
                conn.text_factory = _decode_strict  # UTF-8 hỏng trong sqlite_master là file lạ
            conn.execute("BEGIN")
            try:
                tables = app_tables(conn)
                if tables is None or (complete is not None and tables and tables != complete):
                    return False
                if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
                    return False
                return extra is None or extra(conn, tables)
            finally:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
    except _Undecodable:
        return False
    except sqlite3.DatabaseError as exc:
        if keeps_file(exc):
            raise
        return False


def create_tables(
    path: Path,
    *,
    timeout: float,
    guard: Callable[[sqlite3.Connection], None],
    app_tables: Callable[[sqlite3.Connection], frozenset | None],
    complete: frozenset,
    create_sqls: Iterable[str],
) -> bool:
    """Ba kho lưu tạm: cấu trúc đúng thì thôi (chỉ đọc, không xin quyền ghi); file còn trống thì tạo
    **mọi** bảng trong một giao dịch ghi, kiểm lại cấu trúc trong chính giao dịch đó trước khi tạo:
    tab khác không bao giờ thấy file mới có một bảng (Soi Lỗi T-131 GN-2). ``False``: cấu trúc khác
    (file bị thay ngay sau lần kiểm, UTF-8 hỏng), chưa ghi gì. Lỗi SQLite khác ném lại."""
    try:
        with closing(sqlite3.connect(path, timeout=timeout, isolation_level=None)) as conn:
            guard(conn)
            conn.text_factory = _decode_strict
            conn.execute("BEGIN")
            try:
                tables = app_tables(conn)
            finally:
                conn.execute("ROLLBACK")
            if tables == complete:
                return True
            if tables is None or tables:
                return False
            conn.execute("BEGIN IMMEDIATE")
            try:
                tables = app_tables(conn)  # kiểm lại trong giao dịch ghi
                if tables is None or (tables and tables != complete):
                    conn.execute("ROLLBACK")
                    return False
                if not tables:
                    for sql in create_sqls:
                        conn.execute(sql)
            except BaseException:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
            conn.execute("COMMIT")
            return True
    except _Undecodable:
        return False


__all__ = [
    "JOURNAL_SUFFIXES",
    "KEEP_FILE_CODES",
    "MASTER_SQL",
    "SQLITE_READONLY",
    "app_rows",
    "app_table_names",
    "code",
    "create_tables",
    "guard",
    "is_busy",
    "is_healthy",
    "is_link",
    "journal_paths",
    "keeps_file",
    "newer_file_format",
    "remove_link",
    "schema_by_table",
    "schema_rows",
]

"""Thẻ ảnh sửa tay, chỉ nhớ trên máy đang dùng (phiếu T-052, quyết định 3A).

Thẻ gốc đọc từ tên thư mục Drive (``seo_app.images.tags``). Người dùng sửa thẻ của một ảnh thì
bản sửa được lưu ở đây, trong một file SQLite cục bộ ``data/image_tags.sqlite`` (``data/`` đã có
trong ``.gitignore``). App **không ghi** gì vào thư mục ảnh hay Drive. Xóa file này thì app tự tạo
lại file rỗng; chỉ mất các thẻ đã sửa tay, ảnh lại dùng thẻ đọc từ tên thư mục.

- Khóa là ``ImageRef`` (số thứ tự thư mục gốc + đường dẫn tương đối, không phân biệt hoa thường,
  cùng dạng Unicode như T-048 so tên), **không** phải đường dẫn tuyệt đối: file không chứa tên
  ổ đĩa, tên tài khoản máy hay đường dẫn tới thư mục Drive.
- Dữ liệu đọc từ file là chưa tin cậy: mỗi dòng được kiểm lại bằng ``ImageRef`` (T-048) và
  ``ImageTags`` (chỉ nhận giá trị trong danh sách cố định); giới hạn độ dài từng ô trước khi đọc
  vào bộ nhớ; chữ sai UTF-8, sai kiểu, sai khóa thì bỏ dòng đó. Không ``pickle``, không ``eval``;
  mọi câu SQL dùng tham số ``?``.
- Cấu trúc file cũng chưa tin cậy (T-070, LC-T052-2): trước mọi truy vấn khác, ``sqlite_master``
  phải khớp đúng hai bảng app tạo (đúng câu ``CREATE TABLE``, kèm chỉ mục tự sinh của khóa chính),
  không thừa dòng, không dòng nào lặp lại (T-074); có khung nhìn, trigger, bảng ảo,
  ``WITHOUT ROWID``, chỉ mục hay bảng lạ thì coi là hỏng. Kiểm ở mỗi lần mở, nên file bị thay khi
  app đang chạy cũng bị bắt; và kiểm **trong cùng giao dịch** với thao tác (T-074), nên cấu trúc
  app dùng luôn là cấu trúc vừa kiểm: ở chế độ nhật ký thường (app không đổi chế độ của file),
  chương trình khác mở file qua SQLite phải chờ giao dịch xong mới ghi được; ở chế độ WAL (chương
  trình khác có thể đặt sẵn), nó ghi được trong lúc app **đọc**, nhưng lần đọc đó vẫn chỉ thấy
  bản đã kiểm (SQLite giữ ảnh chụp của file từ câu kiểm), còn lần ghi của app thì giữ quyền ghi từ
  đầu. Thay đổi chen vào như vậy bị bắt ở lần kiểm sau. Nhờ vậy chỉ câu SQL của app được chạy trên
  file.
- Lớp phòng sau, nếu lớp kiểm trên bị lách: mỗi truy vấn bị giới hạn số bước (``_MAX_VM_STEPS``)
  và độ dài mỗi giá trị (``_MAX_SQLITE_LENGTH``, T-074): truy vấn đệ quy bị dừng, giá trị khổng lồ
  bị từ chối. Đó là giới hạn số bước và độ dài, **không phải giới hạn thời gian**: một truy vấn lạ
  vẫn có thể chạy lâu trước khi bị dừng.
- File hỏng hẳn (không phải SQLite, sai cấu trúc, có ô dài quá giới hạn, quá lớn) thì đổi tên sang
  một bên để giữ lại (như kho nháp), rồi tạo file mới. File đang bận hay không mở được thì báo lỗi,
  không xóa.
- Chỗ đặt file (và file nhật ký ``-journal``, ``-wal``, ``-shm`` cạnh nó) là liên kết: symlink,
  junction, hay hard link (file có tên thứ hai, có thể nằm ngoài ``data/``; Windows tạo được không
  cần quyền quản trị) thì chỉ gỡ chính liên kết, không đụng file nó trỏ tới, rồi tạo file mới
  (F1). Kiểm ở **mỗi lần mở**, không chỉ lần đầu, nên liên kết đặt vào khi app đang chạy cũng bị
  gỡ trước khi SQLite ghi.
- Ảnh trong thư mục ảnh AI (hay tên file có dấu hiệu ảnh AI, ``seo_app.images.tags``) luôn là ảnh
  AI: thẻ sửa tay không đổi được thành ảnh thật.
"""

from __future__ import annotations

import sqlite3
import stat
import unicodedata
from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime
from functools import cache
from pathlib import Path
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
from seo_app.images.folders import MAX_REL_PATH_CHARS, ImageFolderError, ImageRef
from seo_app.images.tags import SOURCE_AI, FolderTags, ImageTags, TagError, tags_for_image

DEFAULT_IMAGE_TAGS_FILE = PROJECT_ROOT / "data" / "image_tags.sqlite"
MAX_MANUAL_TAGS = 20_000  # quá số này thì bỏ các thẻ sửa tay cũ nhất
MAX_FILE_BYTES = 64 * 1024 * 1024  # file lớn hơn thì không phải do app tạo: coi là hỏng
DEFAULT_LIST_LIMIT = 500
SCHEMA_VERSION = "1"
_SQLITE_TIMEOUT = 5
_HEALTH_TIMEOUT = 1  # kiểm file trước khi dùng: chờ ngắn thôi (như cache danh sách bài, T-037)
_QUERY_CHUNK = 400  # số tham số tối đa mỗi câu ``IN (...)``
# Giới hạn byte từng ô khi đọc (chữ UTF-8 tối đa 4 byte/ký tự): đọc ``substr`` dài hơn 1 byte,
# nếu chạm giới hạn thì ô quá dài, bỏ dòng.
_MAX_PATH_BYTES = 4 * MAX_REL_PATH_CHARS
_MAX_TAG_BYTES = 1024
_MAX_TIME_BYTES = 64
_SQLITE_INTERRUPT = 9
_SQLITE_CORRUPT = 11
_SQLITE_TOOBIG = 18
_SQLITE_NOTADB = 26
_SQLITE_MAX_INT = 2**63 - 1  # số nguyên lớn nhất SQLite lưu được
_JOURNAL_SUFFIXES = ("-journal", "-wal", "-shm")
# Giới hạn số bước máy ảo SQLite cho mỗi lần mở (LC-T052-2). Đo trên Windows (T-070): việc nặng
# nhất của một file hợp lệ (kiểm ``quick_check``, liệt kê, lưu kèm dọn thẻ cũ trên file 60.000 dòng,
# 176 MB, gấp gần ba lần ``MAX_FILE_BYTES``) tốn dưới 2,1 triệu bước; truy vấn đệ quy vô hạn chạy
# khoảng 26 triệu bước mỗi giây, nên bị dừng sau vài giây thay vì treo.
_MAX_VM_STEPS = 50_000_000
_PROGRESS_EVERY = 1000  # SQLite gọi bộ đếm sau mỗi chừng này bước
# Độ dài tối đa (byte) của một chuỗi, khối byte hay một dòng trên kết nối tới file thẻ (T-074,
# SL-T070-2): một bước máy ảo không tạo được giá trị khổng lồ (``randomblob``, ``zeroblob``,
# ``printf('%.*c', …)``: SQLite báo ``SQLITE_TOOBIG`` hoặc trả rỗng ngay). Ô app ghi chỉ vài KB
# (đường dẫn tối đa ``MAX_REL_PATH_CHARS`` ký tự, 4 byte/ký tự), mặc định của SQLite là 1 tỷ.
_MAX_SQLITE_LENGTH = 1_000_000
_CREATE_TABLES = (
    "CREATE TABLE IF NOT EXISTS manual_tags ("
    "root_index INTEGER NOT NULL, ref_key TEXT NOT NULL, rel_path TEXT NOT NULL, "
    "source TEXT NOT NULL, project_code TEXT NOT NULL, category TEXT NOT NULL, "
    "area TEXT NOT NULL, phase TEXT NOT NULL, saved_at TEXT NOT NULL, "
    "saved_ts REAL NOT NULL, PRIMARY KEY (root_index, ref_key))",
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
)
_APP_TABLES = frozenset({b"manual_tags", b"info"})
_MASTER_SQL = "SELECT type, name, tbl_name, substr(sql, 1, ?) FROM sqlite_master LIMIT ?"
_MAX_SQL_BYTES = 2048  # câu CREATE dài nhất của app chưa tới 400 byte
_COLUMNS = (
    "root_index",
    "ref_key",
    "rel_path",
    "source",
    "project_code",
    "category",
    "area",
    "phase",
    "saved_at",
    "saved_ts",
)
_SELECT = (
    "SELECT root_index, substr(ref_key, 1, ?), substr(rel_path, 1, ?), substr(source, 1, ?), "
    "substr(project_code, 1, ?), substr(category, 1, ?), substr(area, 1, ?), "
    "substr(phase, 1, ?), substr(saved_at, 1, ?) FROM manual_tags"
)
_SELECT_LIMITS = (
    _MAX_PATH_BYTES + 1,
    _MAX_PATH_BYTES + 1,
    *(_MAX_TAG_BYTES + 1,) * 5,
    _MAX_TIME_BYTES + 1,
)
_TEXT_LIMITS = (_MAX_PATH_BYTES, _MAX_PATH_BYTES, *(_MAX_TAG_BYTES,) * 5, _MAX_TIME_BYTES)


def _oversized_sql(table: str, columns: Iterable[str]) -> str:
    checks = " OR ".join(f"length(CAST({column} AS BLOB)) > ?1" for column in columns)
    return f"SELECT 1 FROM {table} WHERE {checks} LIMIT 1"


# Ô dài hơn ``_MAX_SQLITE_LENGTH`` (app không bao giờ ghi): đọc ô đó báo ``SQLITE_TOOBIG`` ở mọi
# lần đọc (``substr`` vẫn nạp cả ô), còn ``quick_check`` vẫn ra ``ok``. ``_is_healthy`` đọc thử mọi
# ô (``CAST`` phải nạp cả ô: ô quá dài báo ``SQLITE_TOOBIG``; nếu SQLite nào đó không nạp thì phép
# so độ dài vẫn bắt), để file như vậy bị đổi tên sang một bên thay vì làm kho kẹt mãi ở câu báo
# lỗi. Chỉ ghép tên bảng, tên cột hằng.
_OVERSIZED_SQL = {
    b"manual_tags": _oversized_sql("manual_tags", _COLUMNS),
    b"info": _oversized_sql("info", ("key", "value")),
}

_MSG_AI_FOLDER = (
    "Ảnh này nằm trong thư mục ảnh AI (hoặc tên file có chữ AI, tên công cụ tạo ảnh) nên luôn là "
    "ảnh AI. Muốn đổi, hãy đổi tên hoặc chuyển ảnh sang thư mục khác trên Drive."
)
_MSG_BAD_ROOT = "Số thứ tự thư mục ảnh không hợp lệ."
_MSG_BROKEN = "File lưu thẻ ảnh bị lỗi nên không đọc/ghi được. Thử tải lại trang."


class ImageTagStoreError(Exception):
    """Lỗi file lưu thẻ sửa tay; câu tiếng Việt hiện thẳng được, không chứa đường dẫn."""


@dataclass(frozen=True)
class ManualTag:
    """Thẻ sửa tay của một ảnh."""

    ref: ImageRef
    tags: ImageTags
    saved_at: datetime  # có múi giờ


@dataclass(frozen=True)
class ManualTagList:
    items: tuple[ManualTag, ...]
    skipped: int = 0  # số dòng hỏng đã bỏ qua


@dataclass(frozen=True)
class ResolvedTags:
    """Thẻ dùng cho một ảnh: thẻ sửa tay nếu có, không thì thẻ đọc từ tên thư mục."""

    ref: ImageRef
    tags: ImageTags
    auto: FolderTags  # thẻ đọc từ tên thư mục (để giao diện so sánh hoặc quay lại)
    manual: bool = False
    saved_at: datetime | None = None
    error: str = ""  # không đọc được thẻ sửa tay: đang dùng thẻ đọc từ tên thư mục


def ref_key(ref: ImageRef) -> str:
    """Khóa của ảnh trong file: đường dẫn tương đối không phân biệt hoa thường, dạng NFC (Mac lưu
    tên dạng NFD). Cùng cách so tên với ``seo_app.images.folders``."""
    return unicodedata.normalize("NFC", ref.rel_path).casefold()


def _check_ref(ref: object) -> ImageRef:
    if not isinstance(ref, ImageRef):
        raise TypeError("Thẻ sửa tay chỉ gắn với ImageRef (đường dẫn tương đối trong thư mục ảnh).")
    return ref


def _storable(ref: ImageRef) -> bool:
    """Số thứ tự thư mục gốc lưu được vào SQLite. ``ImageRef`` đọc lại từ nháp đã lưu có thể mang
    số rất lớn (SL-T052-6): ảnh đó không thể có thẻ sửa tay."""
    return type(ref.root_index) is int and 0 <= ref.root_index <= _SQLITE_MAX_INT


def _keep_ai(tags: ImageTags, auto: ImageTags) -> ImageTags:
    """Ảnh trong thư mục ảnh AI luôn là ảnh AI (yêu cầu 4), kể cả khi file bị sửa tay."""
    if auto.is_ai and not tags.is_ai:
        return ImageTags(source=SOURCE_AI, category=tags.category)
    return tags


@dataclass
class ImageTagStore:
    """Thẻ sửa tay trong một file SQLite. Mỗi thao tác mở và đóng kết nối riêng (an toàn khi
    Streamlit chạy nhiều luồng)."""

    # Tra lúc tạo (không lúc import) để test trỏ được sang thư mục tạm.
    path: Path = field(default_factory=lambda: DEFAULT_IMAGE_TAGS_FILE)
    timezone: str = DEFAULT_TIMEZONE
    max_items: int = MAX_MANUAL_TAGS
    recovered_from: Path | None = field(default=None, init=False)
    """File cũ hỏng đã được đổi tên sang một bên: đường dẫn bản hỏng (để báo người dùng)."""
    _ready: bool = field(default=False, init=False, repr=False)

    # ------------------------------------------------------------ dùng chính

    def resolve(self, ref: ImageRef) -> ResolvedTags:
        """Thẻ dùng cho ``ref``. Không đọc được file thẻ sửa tay thì vẫn trả thẻ đọc từ tên thư
        mục, kèm câu báo ở ``error`` (không ném lỗi)."""
        return self.resolve_many([ref])[_check_ref(ref)]

    def resolve_many(self, refs: Iterable[ImageRef]) -> dict[ImageRef, ResolvedTags]:
        """Như ``resolve`` cho nhiều ảnh (một trang ảnh), đọc file một lần."""
        refs = [_check_ref(ref) for ref in refs]
        error = ""
        try:
            manual = self.get_many(refs)
        except ImageTagStoreError as exc:
            manual, error = {}, str(exc)
        result: dict[ImageRef, ResolvedTags] = {}
        for ref in refs:
            auto = tags_for_image(ref)
            found = manual.get(ref)
            if found is None:
                result[ref] = ResolvedTags(ref=ref, tags=auto.tags, auto=auto, error=error)
            else:
                result[ref] = ResolvedTags(
                    ref=ref,
                    tags=_keep_ai(found.tags, auto.tags),
                    auto=auto,
                    manual=True,
                    saved_at=found.saved_at,
                )
        return result

    # ------------------------------------------------------------ đọc / ghi

    def get(self, ref: ImageRef) -> ManualTag | None:
        """Thẻ sửa tay của ``ref``; không có (hoặc dòng hỏng): ``None``."""
        return self.get_many([ref]).get(_check_ref(ref))

    def get_many(self, refs: Iterable[ImageRef]) -> dict[ImageRef, ManualTag]:
        """Thẻ sửa tay của các ảnh có thẻ sửa tay (ảnh không có thì không có trong kết quả)."""
        wanted: dict[tuple[int, str], list[ImageRef]] = {}
        for ref in refs:
            if _storable(_check_ref(ref)):
                wanted.setdefault((ref.root_index, ref_key(ref)), []).append(ref)
        if not wanted:
            return {}
        by_root: dict[int, list[str]] = {}
        for root_index, key in wanted:
            by_root.setdefault(root_index, []).append(key)
        # Mọi câu đọc nằm trong một giao dịch đã kiểm cấu trúc (LC-T070-2); kiểm từng dòng sau khi
        # giao dịch đóng (T-077, SL-T074-1), để lần lưu ở tab khác không phải chờ phần đó.
        rows: list[tuple] = []
        with self._connect() as conn:
            for root_index, keys in by_root.items():
                for start in range(0, len(keys), _QUERY_CHUNK):
                    chunk = keys[start : start + _QUERY_CHUNK]
                    marks = ", ".join("?" * len(chunk))
                    rows += conn.execute(
                        f"{_SELECT} WHERE root_index = ? AND ref_key IN ({marks})",
                        (*_SELECT_LIMITS, root_index, *chunk),
                    ).fetchall()
        found: dict[ImageRef, ManualTag] = {}
        for row in rows:
            item = self._row_to_tag(row)
            if item is None:
                continue
            for ref in wanted.get((item.ref.root_index, ref_key(item.ref)), ()):
                # Khóa không phân biệt hoa thường, dấu hiệu ảnh AI thì có thể ("khoai" /
                # "KhoAI"): ép ảnh AI theo đúng ảnh được hỏi (LC-T052-3).
                tags = _keep_ai(item.tags, tags_for_image(ref).tags)
                found[ref] = ManualTag(ref=ref, tags=tags, saved_at=item.saved_at)
        return found

    def set(self, ref: ImageRef, tags: ImageTags) -> ManualTag:
        """Lưu (ghi đè) thẻ sửa tay của ``ref``. Ảnh trong thư mục ảnh AI không đổi được thành
        ảnh thật (``TagError``)."""
        _check_ref(ref)
        if not isinstance(tags, ImageTags):
            raise TypeError("Thẻ phải là ImageTags.")
        # Dựng lại từ giá trị để chạy lại mọi kiểm tra trước khi ghi (lớp con, đối tượng bị sửa).
        ref = ImageRef(ref.root_index, ref.rel_path)
        if not _storable(ref):
            raise ImageTagStoreError(_MSG_BAD_ROOT)
        tags = ImageTags(
            source=tags.source,
            project_code=tags.project_code,
            category=tags.category,
            area=tags.area,
            phase=tags.phase,
        )
        if tags_for_image(ref).tags.is_ai and not tags.is_ai:
            raise TagError(_MSG_AI_FOLDER)
        saved_at = datetime.now(ZoneInfo(self.timezone))
        key = ref_key(ref)
        with self._connect(write=True) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO manual_tags "
                f"({', '.join(_COLUMNS)}) VALUES ({', '.join('?' * len(_COLUMNS))})",
                (
                    ref.root_index,
                    key,
                    ref.rel_path,
                    tags.source,
                    tags.project_code,
                    tags.category,
                    tags.area,
                    tags.phase,
                    saved_at.isoformat(),
                    saved_at.timestamp(),
                ),
            )
            # Giữ thẻ vừa lưu cộng (max - 1) thẻ mới nhất khác; không dựa vào giờ máy để giữ thẻ
            # vừa lưu (đồng hồ bị chỉnh lùi thì nó lại là thẻ "cũ nhất").
            conn.execute(
                "DELETE FROM manual_tags WHERE NOT (root_index = ? AND ref_key = ?) "
                "AND rowid NOT IN (SELECT rowid FROM manual_tags "
                "WHERE NOT (root_index = ? AND ref_key = ?) "
                "ORDER BY saved_ts DESC, rowid DESC LIMIT ?)",
                (ref.root_index, key, ref.root_index, key, max(0, self.max_items - 1)),
            )
        return ManualTag(ref=ref, tags=tags, saved_at=saved_at)

    def clear(self, ref: ImageRef) -> bool:
        """Bỏ thẻ sửa tay của ``ref`` (quay về thẻ đọc từ tên thư mục). ``False``: không có."""
        if not _storable(_check_ref(ref)):
            return False
        with self._connect(write=True) as conn:
            cursor = conn.execute(
                "DELETE FROM manual_tags WHERE root_index = ? AND ref_key = ?",
                (ref.root_index, ref_key(ref)),
            )
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """Bỏ mọi thẻ sửa tay trên máy này. Trả số thẻ đã bỏ."""
        with self._connect(write=True) as conn:
            return conn.execute("DELETE FROM manual_tags").rowcount

    def list_manual(
        self, *, root_index: int | None = None, limit: int = DEFAULT_LIST_LIMIT
    ) -> ManualTagList:
        """Các thẻ sửa tay, mới nhất trước. Dòng hỏng bị bỏ qua và đếm vào ``skipped``."""
        if root_index is not None and (
            type(root_index) is not int or not 0 <= root_index <= _SQLITE_MAX_INT
        ):
            raise ImageTagStoreError(_MSG_BAD_ROOT)
        limit = max(0, min(int(limit), self.max_items))
        where, params = ("", ()) if root_index is None else (" WHERE root_index = ?", (root_index,))
        with self._connect() as conn:
            rows = conn.execute(
                f"{_SELECT}{where} ORDER BY saved_ts DESC, rowid DESC LIMIT ?",
                (*_SELECT_LIMITS, *params, limit),
            ).fetchall()
        items: list[ManualTag] = []
        skipped = 0
        for row in rows:
            item = self._row_to_tag(row)
            if item is None:
                skipped += 1
            else:
                items.append(item)
        return ManualTagList(items=tuple(items), skipped=skipped)

    # ------------------------------------------------------------ nội bộ

    def _row_to_tag(self, row: tuple) -> ManualTag | None:
        """Một dòng đọc từ file → ``ManualTag``; dòng sai bất cứ chỗ nào thì ``None``."""
        root_index, *raw = row
        if type(root_index) is not int or len(raw) != len(_TEXT_LIMITS):
            return None
        texts: list[str] = []
        for value, limit in zip(raw, _TEXT_LIMITS, strict=True):
            if not isinstance(value, bytes) or len(value) > limit:
                return None
            try:
                texts.append(value.decode("utf-8"))
            except UnicodeDecodeError:
                return None
        key, rel_path, source, project_code, category, area, phase, saved_text = texts
        try:
            ref = ImageRef(root_index, rel_path)
            tags = ImageTags(
                source=source, project_code=project_code, category=category, area=area, phase=phase
            )
        except (ImageFolderError, TagError):
            return None
        if key != ref_key(ref):
            return None
        saved_at = _parse_time(saved_text, self.timezone)
        if saved_at is None:
            return None
        return ManualTag(ref=ref, tags=_keep_ai(tags, tags_for_image(ref).tags), saved_at=saved_at)

    @contextmanager
    def _connect(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        """Kết nối trong **một** giao dịch, đã kiểm cấu trúc file. ``write``: thao tác ghi."""
        self._prepare()
        try:
            # ``with conn``: một giao dịch, xong thì commit, lỗi thì rollback
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                _guard(conn)
                conn.text_factory = bytes  # tự giải mã UTF-8 từng ô (``_row_to_tag``)
                _begin(conn, write=write)
                # File bị thay khi app đang chạy (SL-T052-9, -10): kiểm cấu trúc trước khi đọc,
                # trong cùng giao dịch với thao tác (LC-T070-2).
                if _app_tables(conn) != _APP_TABLES:
                    self._ready = False  # lần sau kiểm lại: đổi tên file lạ, tạo file mới
                    raise ImageTagStoreError(_MSG_BROKEN)
                yield conn
        except sqlite3.DatabaseError as exc:
            if not _is_busy(exc):
                # Hỏng, thiếu bảng/cột (file bị thay, SL-T052-10), chạy quá số bước, giá trị dài
                # quá giới hạn (SL-T070-2): lần sau kiểm lại file (``_is_healthy`` coi các lỗi này
                # là hỏng, đổi tên file). Bận/khóa thì chỉ là tab khác đang ghi.
                self._ready = False
            raise ImageTagStoreError(_db_message(exc)) from None
        except OSError as exc:
            raise ImageTagStoreError(
                f"Không đọc/ghi được file lưu thẻ ảnh ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None

    def _prepare(self) -> None:
        """Mỗi lần mở: gỡ liên kết ở chỗ đặt file (F1). Lần đầu, hoặc khi file bị xóa hay bị
        thay khi app đang chạy: tạo thư mục, kiểm file (hỏng, quá lớn), tạo bảng."""
        try:
            # Kiểm mỗi lần, không chỉ lần đầu (SL-T052-7, -8): liên kết đặt vào sau lần dùng đầu
            # cũng bị gỡ trước khi SQLite mở file. File hay cả data/ bị xóa: tạo lại.
            if self._remove_links() or not self.path.is_file():
                self._ready = False
            if self._ready:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                if not self.path.is_file():
                    raise ImageTagStoreError(
                        "Chỗ đặt file lưu thẻ ảnh đang là một thư mục, app không dùng được."
                    )
                if self.path.stat().st_size > MAX_FILE_BYTES or not _is_healthy(self.path):
                    self.recovered_from = self._move_aside()
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                _guard(conn)
                conn.text_factory = bytes
                # File có thể bị thay ngay sau ``_is_healthy`` (LC-T070-2): kiểm lại trong giao
                # dịch ghi, trước ``CREATE``/``INSERT``. Lạ thì chưa ghi gì; lần sau kiểm lại từ
                # đầu, đổi tên file lạ.
                _begin(conn, write=True)
                if _app_tables(conn) is None:
                    raise ImageTagStoreError(_MSG_BROKEN)
                for sql in _CREATE_TABLES:
                    conn.execute(sql)
                conn.execute(
                    "INSERT OR IGNORE INTO info (key, value) VALUES ('schema_version', ?)",
                    (SCHEMA_VERSION,),
                )
        except sqlite3.DatabaseError as exc:
            raise ImageTagStoreError(_db_message(exc)) from None
        except OSError as exc:
            raise ImageTagStoreError(
                f"Không tạo được file lưu thẻ ảnh ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None
        self._ready = True

    def _remove_links(self) -> bool:
        """Gỡ liên kết ở chỗ đặt file và chỗ các file nhật ký của nó. Có gỡ thì ``True``."""
        removed = False
        for path in (self.path, *self._journal_paths(self.path)):
            if _is_link(path):
                _remove_link(path)
                removed = True
        return removed

    @staticmethod
    def _journal_paths(path: Path) -> tuple[Path, ...]:
        return tuple(path.with_name(path.name + suffix) for suffix in _JOURNAL_SUFFIXES)

    def _move_aside(self) -> Path:
        """Đổi tên file hỏng (và file nhật ký đi kèm) sang một bên để giữ lại."""
        stamp = datetime.now(ZoneInfo(self.timezone)).strftime("%Y%m%d-%H%M%S")
        target = self.path.with_name(f"{self.path.stem}.hong-{stamp}{self.path.suffix}")
        number = 1
        while target.exists():
            number += 1
            target = self.path.with_name(
                f"{self.path.stem}.hong-{stamp}-{number}{self.path.suffix}"
            )
        self.path.replace(target)
        # File nhật ký của file cũ mà để lại thì SQLite sẽ "khôi phục" nó vào file mới.
        for journal, moved in zip(
            self._journal_paths(self.path), self._journal_paths(target), strict=True
        ):
            with suppress(FileNotFoundError):
                journal.replace(moved)
        return target


def _is_link(path: Path) -> bool:
    """Liên kết tắt (symlink, junction) hoặc hard link: file thường có hơn một tên, tên kia có thể
    nằm ngoài ``data/`` (SL-T052-7). SQLite không bao giờ tự tạo hard link."""
    try:
        if path.is_symlink() or path.is_junction():
            return True
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISREG(info.st_mode) and info.st_nlink > 1


def _remove_link(path: Path) -> None:
    """Chỉ gỡ chính liên kết (F1): file/thư mục nó trỏ tới, tên kia của hard link giữ nguyên."""
    try:
        path.unlink()
    except (IsADirectoryError, PermissionError):
        path.rmdir()  # junction Windows: xóa chính junction, không đụng thư mục đích


def _parse_time(value: str, timezone: str) -> datetime | None:
    """Giờ lưu có múi giờ; sai dạng, thiếu múi giờ, hay ra ngoài khoảng năm 1–9999 khi đổi múi giờ
    ("9999-12-31T23:59:59-14:00", SL-T052-5) thì ``None`` (bỏ dòng, không ném lỗi)."""
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(ZoneInfo(timezone))
    except (ValueError, OverflowError):
        return None


def _guard(conn: sqlite3.Connection) -> None:
    """File thẻ là dữ liệu chưa tin cậy (F3): không chạy hàm "không vô hại" trong view/trigger/chỉ
    mục của file; dừng truy vấn chạy quá ``_MAX_VM_STEPS`` bước trên kết nối này (LC-T052-2: SQLite
    báo ``interrupted``); không cho tạo chuỗi hay khối byte dài quá ``_MAX_SQLITE_LENGTH``
    (SL-T070-2: SQLite báo ``SQLITE_TOOBIG``).

    Đây là lớp phòng sau lớp kiểm cấu trúc, và **không phải giới hạn thời gian**: mỗi bước bị chặn
    cỡ, số bước bị chặn số, nhưng một truy vấn lạ vẫn có thể chạy lâu trước khi bị dừng. Lớp chặn
    chính là ``_app_tables`` (chỉ câu SQL của app được chạy trên file)."""
    conn.execute("PRAGMA trusted_schema = OFF")
    conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, _MAX_SQLITE_LENGTH)
    limit = _MAX_VM_STEPS  # đọc lúc mở (test hạ được giới hạn)
    steps = 0

    def stop_when_too_long() -> int:
        nonlocal steps
        steps += _PROGRESS_EVERY
        return 1 if steps > limit else 0

    conn.set_progress_handler(stop_when_too_long, _PROGRESS_EVERY)


def _begin(conn: sqlite3.Connection, *, write: bool) -> None:
    """Mở giao dịch **trước** khi kiểm cấu trúc (LC-T070-2), để kiểm và dùng file nằm trong cùng
    một giao dịch: cấu trúc app dùng luôn là cấu trúc vừa kiểm (chế độ WAL: xem docstring module).
    Ghi: ``BEGIN IMMEDIATE`` (giữ quyền ghi ngay; chương trình khác muốn ghi phải chờ, hay nhận
    "database is locked"); đọc: ``BEGIN`` (giữ khóa đọc, hay ảnh chụp ở chế độ WAL, từ câu đọc đầu
    tiên, tức câu kiểm ``sqlite_master``)."""
    conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")


@cache
def _expected_schema() -> dict[bytes, frozenset[tuple]]:
    """Các dòng ``sqlite_master`` (loại, tên, bảng, câu lệnh) của hai bảng app tạo, theo tên bảng.

    Dựng bằng chính ``_CREATE_TABLES`` trong một cơ sở dữ liệu trong bộ nhớ, nên khớp đúng cách
    SQLite đang chạy ghi lại câu lệnh (bỏ ``IF NOT EXISTS``…). Mỗi bảng có một chỉ mục tự sinh
    cho khóa chính (câu lệnh rỗng)."""
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.text_factory = bytes
        for sql in _CREATE_TABLES:
            conn.execute(sql)
        rows = conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, 16)).fetchall()
    schema: dict[bytes, set[tuple]] = {}
    for row in rows:
        schema.setdefault(row[2], set()).add(tuple(row))
    return {name: frozenset(items) for name, items in schema.items()}


def _app_tables(conn: sqlite3.Connection) -> frozenset[bytes] | None:
    """Đọc ``sqlite_master`` (chưa chạm vào bảng nào): các bảng của app đang có, nếu mọi đối tượng
    trong file đều khớp đúng ``_expected_schema``; có gì khác thì ``None`` (LC-T052-2, SL-T052-9).

    Bắt được: khung nhìn, trigger, bảng ảo (``USING …``), ``WITHOUT ROWID``, ``CHECK``, cột sinh,
    kiểu cột khác, chỉ mục thêm, bảng lạ. Kết nối phải đặt ``text_factory = bytes``, và đang ở
    trong giao dịch của thao tác (``_begin``).

    Đọc vào **danh sách** (LC-T070-1): nhiều dòng hơn số mong đợi, hay một dòng ``(loại, tên)``
    lặp lại, thì ``None``. So theo tập hợp thì một dòng chỉ mục lặp lại (``writable_schema``) gộp
    vào dòng cũ và đẩy một trigger ra ngoài ``LIMIT``. Vẫn đọc có ``LIMIT``: không đọc vô hạn.
    """
    expected = _expected_schema()
    limit = sum(len(items) for items in expected.values())
    rows = [tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, limit + 1))]
    if len(rows) > limit or len({row[:2] for row in rows}) != len(rows):
        return None
    found: dict[bytes, set[tuple]] = {}
    for row in rows:
        found.setdefault(row[2], set()).add(row)
    for name, items in found.items():
        if name not in expected or items != expected[name]:
            return None
    return frozenset(found)


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, chỉ chứa đúng các bảng app tạo (bảng chưa có thì được), đúng
    phiên bản.

    ``False`` chỉ khi **chắc chắn** hỏng hoặc lạ (SQLite báo hỏng / không phải cơ sở dữ liệu,
    cấu trúc khác app tạo, ``quick_check`` khác ``ok``, có ô dài quá ``_MAX_SQLITE_LENGTH`` hay
    gặp ``SQLITE_TOOBIG`` (T-074, SL-T070-2), sai phiên bản, kiểm quá số bước). Lỗi khác (bận,
    khóa, không mở được) được ném lại để báo lỗi mà không đổi tên file.
    """
    try:
        with closing(sqlite3.connect(path, timeout=_HEALTH_TIMEOUT)) as conn:
            # File chưa tin cậy: không chạy hàm trong view/trigger/chỉ mục của nó khi kiểm.
            _guard(conn)
            conn.text_factory = bytes
            # Mọi bước kiểm nằm trong một giao dịch đọc (LC-T070-2): cấu trúc không đổi được giữa
            # ``_app_tables`` và ``quick_check``.
            _begin(conn, write=False)
            # Trước mọi truy vấn khác (LC-T052-2): khung nhìn hay trigger đệ quy không bao giờ
            # được chạy, kể cả bởi ``quick_check`` (kiểm ``CHECK``, cột sinh).
            tables = _app_tables(conn)
            if tables is None:
                return False
            if conn.execute("PRAGMA quick_check").fetchone() != (b"ok",):
                return False
            for table in tables:
                if conn.execute(_OVERSIZED_SQL[table], (_MAX_SQLITE_LENGTH,)).fetchone():
                    return False
            version = None
            if b"info" in tables:
                version = conn.execute(
                    "SELECT substr(value, 1, 16) FROM info WHERE key = 'schema_version'"
                ).fetchone()
    except sqlite3.DatabaseError as exc:
        if _is_corrupt(exc) or _is_interrupted(exc) or _is_too_big(exc):
            return False
        raise
    return version is None or version == (SCHEMA_VERSION.encode(),)


def _is_busy(exc: sqlite3.DatabaseError) -> bool:
    text = str(exc).lower()
    return isinstance(exc, sqlite3.OperationalError) and ("locked" in text or "busy" in text)


def _is_corrupt(exc: sqlite3.DatabaseError) -> bool:
    """SQLite báo chắc chắn file hỏng (``SQLITE_CORRUPT``, ``SQLITE_NOTADB``, kể cả mã mở rộng)."""
    code = getattr(exc, "sqlite_errorcode", None)
    if isinstance(code, int):
        return code & 0xFF in (_SQLITE_CORRUPT, _SQLITE_NOTADB)
    text = str(exc).lower()
    return "not a database" in text or "malformed" in text


def _is_interrupted(exc: sqlite3.DatabaseError) -> bool:
    """Truy vấn bị ``_guard`` dừng vì chạy quá số bước (``SQLITE_INTERRUPT``)."""
    code = getattr(exc, "sqlite_errorcode", None)
    if isinstance(code, int):
        return code & 0xFF == _SQLITE_INTERRUPT
    return "interrupted" in str(exc).lower()


def _is_too_big(exc: sqlite3.DatabaseError) -> bool:
    """Chuỗi hay khối byte dài quá ``_MAX_SQLITE_LENGTH`` (``SQLITE_TOOBIG``, ``DataError``): app
    không bao giờ ghi giá trị như vậy, nên file có nó là file lạ (SL-T070-2)."""
    code = getattr(exc, "sqlite_errorcode", None)
    if isinstance(code, int):
        return code & 0xFF == _SQLITE_TOOBIG
    return "too big" in str(exc).lower()


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if _is_busy(exc):
        return (
            "File lưu thẻ ảnh đang bận (có thể app mở ở tab khác đang lưu). Thử lại sau giây lát."
        )
    if _is_corrupt(exc) or _is_interrupted(exc) or _is_too_big(exc):
        return _MSG_BROKEN
    return (
        "Không mở được file lưu thẻ ảnh (có thể chương trình khác đang giữ file, hoặc không có "
        "quyền ghi). Ảnh vẫn dùng thẻ đọc từ tên thư mục."
    )


__all__ = [
    "DEFAULT_IMAGE_TAGS_FILE",
    "MAX_FILE_BYTES",
    "MAX_MANUAL_TAGS",
    "ImageTagStore",
    "ImageTagStoreError",
    "ManualTag",
    "ManualTagList",
    "ResolvedTags",
    "ref_key",
]

"""Cache danh sách bài/trang đã đăng trên site (SQLite có sẵn của Python, không thêm thư viện).

Dùng cho kiểm trùng meta (T-036), liên kết nội bộ (T-039) và kiểm link hỏng (Giai đoạn 5).
Nguồn thật là WordPress (``WordPressClient.list_published``); file này chỉ là bản tạm trên máy:
xóa đi thì lần sau tự tải lại.

Dữ liệu đọc từ file là chưa tin cậy: giới hạn số dòng và độ dài, mỗi dòng kiểm lại bằng
``PublishedItem`` và ``is_site_link`` (như lúc nhận từ site). Một dòng sai cũng coi cả cache là
hỏng: bỏ và tải lại. File hỏng hẳn (không phải SQLite, sai cấu trúc, là liên kết tắt) thì xóa
và tạo lại; cache không có gì cần giữ. Mọi câu SQL dùng tham số ``?``. Không lưu bí mật.

Kiểm file như cache số liệu Search Console (T-122; T-131, LC-T129-1, SL-T117-1):

- ``data/`` (hay một thư mục con) là liên kết thì không tạo, không mở, không xóa gì (câu cố định
  ``MSG_DATA_DIR_LINK``); chính file, file nhật ký là liên kết thì chỉ gỡ liên kết.
- ``sqlite_master`` phải khớp đúng hai bảng app tạo, kiểm trước khi mở **và** trong cùng giao dịch
  với thao tác: bảng lạ, trigger, khung nhìn, chỉ mục lạ là file lạ, bỏ file. Đọc bằng bộ giải mã
  có bắt lỗi (UTF-8 hỏng là file lạ, không lặp LC-T122-1).
- Mỗi kết nối: ``trusted_schema = OFF``, giới hạn số bước máy ảo SQLite, độ dài một giá trị.
"""

from __future__ import annotations

import sqlite3
import stat
from collections.abc import Iterator
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
from seo_app.images.data_dir import MSG_DATA_DIR_LINK, dir_has_link, is_link
from seo_app.wordpress.client import (
    MAX_LINK_CHARS,
    MAX_META_CHARS,
    MAX_PAGES,
    MAX_SLUG_CHARS,
    MAX_TITLE_CHARS,
    PER_PAGE,
    PublishedItem,
    WordPressError,
    is_site_link,
)

DEFAULT_SITE_INDEX_FILE = PROJECT_ROOT / "data" / "site_index.sqlite"
DEFAULT_MAX_AGE_HOURS = 6.0
MAX_ITEMS = 2 * PER_PAGE * MAX_PAGES  # bài + trang, đúng mức client đọc tối đa
SCHEMA_VERSION = "2"  # 2: thêm "truncated" trong bảng info (T-037 lượt 2)
# Một chữ tiếng Việt UTF-8 tối đa 4 byte: chặn dòng quá to trước khi đọc vào bộ nhớ.
_MAX_FIELD_BYTES = 4 * max(MAX_LINK_CHARS, MAX_META_CHARS, MAX_TITLE_CHARS, MAX_SLUG_CHARS)
_MAX_INFO_CHARS = 2048
_CLOCK_SKEW = timedelta(minutes=5)  # thời điểm tải "ở tương lai" quá mức này = cache cũ
_SQLITE_TIMEOUT = 5
# Kiểm file trước khi dùng: chờ ngắn thôi; file bận lâu hơn thì báo "đang bận" (SL-T037-5).
_HEALTH_TIMEOUT = 1
# Ghi cache cũng chờ ngắn (SL-T037-5, T-041): chương trình khác đang ghi dở (giữ khóa ghi nhưng
# vẫn cho đọc) thì bước kiểm file qua được, chỉ bước ghi phải chờ. Ghi không được thì danh sách vừa
# tải vẫn dùng được (``cache_error``), nên không chờ đủ ``_SQLITE_TIMEOUT``.
_WRITE_TIMEOUT = 1
# Mã lỗi SQLite chắc chắn là file hỏng (SL-T037-4). Lỗi khác (không mở được, lỗi đọc/ghi,
# bận, khóa, chỉ đọc…) thì KHÔNG xóa file: có thể chương trình khác đang giữ file.
_SQLITE_CORRUPT = 11
_SQLITE_NOTADB = 26
_SQLITE_INTERRUPT = 9
_SQLITE_TOOBIG = 18
# Lỗi do môi trường, không do file lạ (LC-T122-1): quyền, bận, khóa, hết bộ nhớ, chỉ đọc, vào ra,
# đầy ổ, không mở được, giao thức khóa. Bước kiểm file gặp các mã này thì giữ file, báo câu; mã
# khác («unsupported file format», giá trị quá dài, quá số bước…) là file lạ: bỏ file.
_KEEP_FILE_CODES = frozenset({3, 5, 6, 7, 8, 10, 13, 14, 15})
_JOURNAL_SUFFIXES = ("-journal", "-wal", "-shm")
# Lớp phòng sau lớp kiểm cấu trúc (như ``plan_cache``, ``search_cache``): số bước tối đa của máy
# ảo SQLite cho mỗi kết nối, độ dài tối đa của một giá trị. Kiểm, đọc, ghi danh sách lớn nhất
# (``MAX_ITEMS`` dòng, chữ dài tối đa) dùng chưa tới một phần mười mức này (đo ở báo cáo T-131).
_MAX_VM_STEPS = 50_000_000
_PROGRESS_EVERY = 1000
_MAX_SQLITE_LENGTH = 1_000_000
_COLUMNS = ("id", "type", "slug", "link", "title", "meta_title", "meta_desc", "modified_gmt")
# Câu tạo bảng giữ đúng chữ như trước T-131: file cache cũ trên máy vẫn khớp ``_expected_schema``.
_CREATE_TABLES = (
    "CREATE TABLE IF NOT EXISTS pages ("
    "id INTEGER NOT NULL, type TEXT NOT NULL, slug TEXT NOT NULL, "
    "link TEXT NOT NULL, title TEXT NOT NULL, meta_title TEXT NOT NULL, "
    "meta_desc TEXT NOT NULL, modified_gmt TEXT NOT NULL, "
    "PRIMARY KEY (type, id))",
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
)
_MASTER_SQL = "SELECT type, name, tbl_name, substr(sql, 1, ?) FROM sqlite_master LIMIT ?"
_MAX_SQL_BYTES = 2048
_MSG_BROKEN = "File lưu tạm danh sách bài bị lỗi nên không đọc/ghi được. Thử tải lại."


class SiteIndexError(Exception):
    """Lỗi cache danh sách bài; thông báo tiếng Việt, hiện thẳng được cho người dùng."""


class PublishedSource(Protocol):
    """Thứ cung cấp danh sách bài đã đăng (``WordPressClient``)."""

    base_url: str

    def list_published(self) -> list[PublishedItem]: ...


@dataclass(frozen=True)
class SiteIndex:
    """Danh sách bài/trang đã đăng của một site, kèm thời điểm tải (có múi giờ)."""

    site: str  # WORDPRESS_URL lúc tải
    fetched_at: datetime
    items: tuple[PublishedItem, ...]
    from_cache: bool = False  # True: đọc từ file; False: vừa tải từ site
    cache_error: str = ""  # tải được nhưng không ghi được file (vẫn dùng được danh sách)
    truncated: bool = False  # site có hơn MAX_PAGES trang kết quả: danh sách chưa đủ

    def by_link(self) -> dict[str, PublishedItem]:
        return {item.link: item for item in self.items}


@dataclass
class SiteIndexStore:
    """Cache trong một file SQLite. Mỗi thao tác mở và đóng kết nối riêng."""

    # Tra lúc tạo (không lúc import) để test trỏ được sang thư mục tạm.
    path: Path = field(default_factory=lambda: DEFAULT_SITE_INDEX_FILE)
    timezone: str = DEFAULT_TIMEZONE
    max_age_hours: float = DEFAULT_MAX_AGE_HOURS
    reset_count: int = field(default=0, init=False)
    """Số lần file cache hỏng bị bỏ đi và tạo lại (để test và báo người dùng nếu cần)."""

    # ------------------------------------------------------------ dùng chính

    def get(self, source: PublishedSource, *, now: datetime | None = None) -> SiteIndex:
        """Danh sách còn mới (≤ ``max_age_hours``) từ cache; cũ, thiếu hoặc hỏng thì tải lại.

        Lỗi mạng/WordPress khi tải lại được ném ra (``WordPressError``) để giao diện báo.
        """
        cached, busy = self._load_checked(source.base_url)
        if busy:
            # File đang bị giữ: tải từ site nhưng không chờ ghi thêm lần nữa (SL-T037-5).
            return self._fetch(source, cache_error=busy)
        if cached is not None and not self._is_stale(cached, now):
            return cached
        return self.refresh(source)

    def refresh(self, source: PublishedSource) -> SiteIndex:
        """Tải lại ngay từ site rồi ghi cache (dùng cho nút "Tải lại" và trước khi gửi nháp).

        Ghi file lỗi thì vẫn trả danh sách vừa tải, kèm ``cache_error``.
        """
        index = self._fetch(source)
        try:
            self.save(index)
        except SiteIndexError as exc:
            return replace(index, cache_error=str(exc))
        return index

    def is_stale(self, site: str, *, now: datetime | None = None) -> bool:
        """Cache của ``site`` cũ hơn ``max_age_hours`` giờ, hoặc chưa có / hỏng / của site khác."""
        cached = self.load(site)
        return cached is None or self._is_stale(cached, now)

    # ------------------------------------------------------------ đọc / ghi

    def load(self, site: str) -> SiteIndex | None:
        """Đọc cache của ``site``. Không có, của site khác hoặc hỏng: ``None`` (không ném lỗi).

        Cache **chắc chắn** hỏng thì bỏ file luôn, để lần ghi sau tạo lại sạch. File bận hoặc
        không mở được (chương trình khác đang giữ) thì để yên (SL-T037-4).
        """
        return self._load_checked(site)[0]

    def save(self, index: SiteIndex) -> None:
        """Ghi đè toàn bộ cache bằng ``index`` trong một giao dịch."""
        if index.fetched_at.tzinfo is None:
            raise SiteIndexError("Thời điểm tải danh sách bài phải kèm múi giờ.")
        if len(index.items) > MAX_ITEMS:
            raise SiteIndexError("Danh sách bài quá dài nên không lưu tạm được.")
        rows = [tuple(getattr(item, name) for name in _COLUMNS) for item in index.items]
        info = [
            ("schema_version", SCHEMA_VERSION),
            ("site", index.site),
            ("fetched_at", index.fetched_at.isoformat()),
            ("truncated", "1" if index.truncated else "0"),
        ]
        # File lạ (cấu trúc đổi ngay trước lúc ghi): bỏ rồi ghi lại một lần trên file mới.
        for attempt in (1, 2):
            try:
                with self._connect(timeout=_WRITE_TIMEOUT, write=True) as conn:
                    conn.execute("DELETE FROM pages")
                    conn.executemany(
                        "INSERT OR REPLACE INTO pages "
                        "(id, type, slug, link, title, meta_title, meta_desc, modified_gmt) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        rows,
                    )
                    conn.executemany("INSERT OR REPLACE INTO info (key, value) VALUES (?, ?)", info)
                return
            except _Corrupt:
                self._reset_quietly()
                if attempt == 2:
                    raise SiteIndexError(_MSG_BROKEN) from None
            except sqlite3.DatabaseError as exc:
                raise _db_error(exc) from None
            except OSError as exc:
                raise SiteIndexError(
                    f"Không ghi được file lưu tạm danh sách bài ({exc.strerror or 'lỗi đọc/ghi'})."
                ) from None

    def clear(self) -> None:
        """Xóa file cache và file nhật ký (lần sau tự tải lại). ``data/`` là liên kết thì không xóa
        gì (file ở đó nằm ngoài thư mục phần mềm), báo câu cố định (SL-T117-1). Lỗi đọc thư mục
        khi kiểm liên kết cũng ra câu cố định (như LC-T122-2)."""
        try:
            if dir_has_link(self.path.parent, PROJECT_ROOT):
                raise SiteIndexError(MSG_DATA_DIR_LINK)
            for path in (self.path, *_journal_paths(self.path)):
                path.unlink(missing_ok=True)
        except OSError as exc:
            raise SiteIndexError(
                f"Không xóa được file lưu tạm danh sách bài ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None

    # ------------------------------------------------------------ nội bộ

    def _fetch(self, source: PublishedSource, *, cache_error: str = "") -> SiteIndex:
        """Tải danh sách từ site (không ghi file)."""
        items = source.list_published()
        return SiteIndex(
            site=source.base_url,
            fetched_at=self._now(),
            items=tuple(items),
            cache_error=cache_error,
            truncated=bool(getattr(items, "truncated", False)),
        )

    def _load_checked(self, site: str) -> tuple[SiteIndex | None, str]:
        """Như ``load``, thêm câu báo "đang bận" (rỗng nếu file không bận)."""
        try:
            with self._connect() as conn:
                return self._read(conn, site), ""
        except _Corrupt:
            self._reset_quietly()
            return None, ""
        except _BusyError as exc:
            return None, str(exc)
        except sqlite3.DatabaseError as exc:
            if _is_corrupt(exc):
                self._reset_quietly()
            return None, ""
        except (SiteIndexError, OSError):
            return None, ""

    def _now(self) -> datetime:
        return datetime.now(ZoneInfo(self.timezone))

    def _is_stale(self, index: SiteIndex, now: datetime | None) -> bool:
        now = now or self._now()
        age = now - index.fetched_at
        if age < -_CLOCK_SKEW:  # đồng hồ máy bị chỉnh lùi, hoặc file bị sửa tay
            return True
        return age > timedelta(hours=self.max_age_hours)

    def _read(self, conn: sqlite3.Connection, site: str) -> SiteIndex | None:
        rows = conn.execute(
            "SELECT key, substr(value, 1, ?) FROM info LIMIT 10", (_MAX_INFO_CHARS + 1,)
        ).fetchall()
        if any(not isinstance(v, str) or len(v) > _MAX_INFO_CHARS for _, v in rows):
            raise _Corrupt
        info = dict(rows)
        if not info:
            return None  # cache mới tạo, chưa tải lần nào
        if info.get("schema_version") != SCHEMA_VERSION:
            raise _Corrupt
        if info.get("site") != site:
            return None  # cache của site khác (đổi WORDPRESS_URL): tải lại, ghi đè
        fetched_at = _parse_time(info.get("fetched_at"), self.timezone)
        truncated = {"0": False, "1": True}.get(info.get("truncated", ""))
        if truncated is None:
            raise _Corrupt

        count, biggest = conn.execute(
            "SELECT COUNT(*), MAX(MAX("
            "length(CAST(slug AS BLOB)), length(CAST(link AS BLOB)), "
            "length(CAST(title AS BLOB)), length(CAST(meta_title AS BLOB)), "
            "length(CAST(meta_desc AS BLOB)), length(CAST(modified_gmt AS BLOB)))) FROM pages"
        ).fetchone()
        if count > MAX_ITEMS or (biggest or 0) > _MAX_FIELD_BYTES:
            raise _Corrupt
        rows = conn.execute(
            "SELECT id, type, slug, link, title, meta_title, meta_desc, modified_gmt "
            "FROM pages ORDER BY rowid"
        ).fetchall()
        items: list[PublishedItem] = []
        for row in rows:
            try:
                item = PublishedItem(**dict(zip(_COLUMNS, row, strict=True)))
            except (TypeError, ValueError):
                raise _Corrupt from None
            if not is_site_link(item.link, site):
                raise _Corrupt
            items.append(item)
        return SiteIndex(
            site=site,
            fetched_at=fetched_at,
            items=tuple(items),
            from_cache=True,
            truncated=truncated,
        )

    @contextmanager
    def _connect(
        self, timeout: float | None = None, *, write: bool = False
    ) -> Iterator[sqlite3.Connection]:
        """Mở file, mở giao dịch (``write``: giành quyền ghi ngay), kiểm cấu trúc (``_app_tables``)
        **trước** mọi truy vấn khác, trong cùng giao dịch với thao tác. Cấu trúc lạ, giá trị quá
        dài, quá số bước: ``_Corrupt``. ``timeout``: giây chờ khi file bị khóa; ``None`` là
        ``_SQLITE_TIMEOUT`` (đọc lúc gọi)."""
        self._prepare()
        if timeout is None:
            timeout = _SQLITE_TIMEOUT
        try:
            with closing(sqlite3.connect(self.path, timeout=timeout, isolation_level=None)) as conn:
                _guard(conn)
                conn.text_factory = _decode_text
                conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                try:
                    if _app_tables(conn) != _expected_schema():
                        raise _Corrupt
                    yield conn
                except BaseException:
                    if conn.in_transaction:
                        conn.execute("ROLLBACK")
                    raise
                conn.execute("COMMIT")
        except sqlite3.DatabaseError as exc:
            if _is_too_big(exc) or _is_interrupted(exc):
                raise _Corrupt from None
            if _is_busy(exc):
                raise _db_error(exc) from None
            raise

    def _prepare(self) -> None:
        """Mỗi lần mở: ``data/`` là liên kết thì báo lỗi, không tạo, không mở (SL-T117-1); chính
        file là liên kết thì bỏ (chỉ xóa liên kết, F1), file nhật ký là liên kết thì gỡ; file
        hỏng, lạ thì bỏ; file trống thì tạo bảng. Chỉ xin quyền ghi khi phải tạo bảng."""
        try:
            if dir_has_link(self.path.parent, PROJECT_ROOT):
                raise SiteIndexError(MSG_DATA_DIR_LINK)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if _is_link(self.path):
                # Liên kết tắt có thể trỏ ra ngoài data/ (F1): chỉ xóa chính liên kết.
                self._reset()
            for path in _journal_paths(self.path):
                if _is_link(path):
                    path.unlink()  # chỉ gỡ chính liên kết, không đụng file nó trỏ tới
            if self.path.exists() and not _is_healthy(self.path):
                self._reset()
            _create_tables(self.path)
        except sqlite3.DatabaseError as exc:
            if _is_too_big(exc) or _is_interrupted(exc):
                raise _Corrupt from None
            raise _db_error(exc) from None
        except OSError as exc:
            raise SiteIndexError(
                f"Không tạo được file lưu tạm danh sách bài ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None

    def _reset(self) -> None:
        self.path.unlink(missing_ok=True)
        for path in _journal_paths(self.path):
            path.unlink(missing_ok=True)
        self.reset_count += 1

    def _reset_quietly(self) -> None:
        with suppress(OSError):  # không xóa được: lần ghi sau sẽ báo lỗi rõ ràng
            self._reset()


# ------------------------------------------------------------ dùng ở bước SEO (T-041)

MSG_NOT_CONNECTED = (
    "Chưa kết nối WordPress nên chưa có danh sách bài đã đăng: chưa kiểm trùng với bài khác và "
    "chưa gợi ý liên kết nội bộ được. Các phần khác vẫn dùng bình thường."
)
MSG_TRUNCATED = (
    "Website có nhiều bài hơn mức phần mềm đọc một lần: danh sách chưa đủ, kiểm trùng có thể sót."
)


@dataclass(frozen=True)
class SiteListing:
    """Danh sách bài cho bước SEO. ``index`` là ``None`` khi chưa kết nối WordPress hay tải lỗi
    (các phần không cần danh sách vẫn dùng được). ``notice``: câu báo nhẹ tiếng Việt (chữ cố định,
    hoặc câu của ``WordPressError``/``SiteIndexError`` vốn không chép bí mật hay lời máy chủ), rỗng
    khi bình thường; giao diện hiện bằng chữ thường."""

    index: SiteIndex | None
    notice: str = ""


def site_listing(
    store: SiteIndexStore,
    source: PublishedSource | None,
    *,
    refresh: bool = False,
    now: datetime | None = None,
) -> SiteListing:
    """Danh sách bài đã đăng cho bước SEO; lỗi WordPress và lỗi file cache thành câu báo.

    ``source`` là ``None`` (chưa khai báo WordPress, tạo client lỗi): báo nhẹ «chưa kết nối».
    ``refresh``: nút «Tải lại danh sách bài» (``store.refresh``); không thì ``store.get`` (cache còn
    mới thì không gọi mạng). Lỗi mạng/WordPress (``WordPressError``): ``index`` là ``None`` kèm
    câu báo.
    """
    if source is None:
        return SiteListing(None, MSG_NOT_CONNECTED)
    try:
        index = store.refresh(source) if refresh else store.get(source, now=now)
    except (WordPressError, SiteIndexError) as exc:
        return SiteListing(None, f"Chưa tải được danh sách bài đã đăng. {exc}")
    notes = [MSG_TRUNCATED] if index.truncated else []
    if index.cache_error:
        notes.append(index.cache_error)
    return SiteListing(index, " ".join(notes))


class _Corrupt(Exception):
    """Nội dung cache sai khuôn (nội bộ)."""


class _BusyError(SiteIndexError):
    """File đang bị kết nối/chương trình khác khóa (nội bộ; vẫn là ``SiteIndexError``)."""


def _decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise _Corrupt from None


def _parse_time(value: object, timezone: str) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise _Corrupt
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise _Corrupt from None
    if parsed.tzinfo is None:
        raise _Corrupt
    try:
        return parsed.astimezone(ZoneInfo(timezone))
    except (OverflowError, ValueError):
        # Giờ sửa tay tràn khi đổi múi giờ (sang năm 10000, năm 0): coi như file hỏng, không để
        # lọt lỗi Python ra trang (Lá Chắn LC-T113-2, T-118).
        raise _Corrupt from None


# ------------------------------------------------------------ kiểm cấu trúc file (T-131)


def _journal_paths(path: Path) -> tuple[Path, ...]:
    return tuple(path.with_name(path.name + suffix) for suffix in _JOURNAL_SUFFIXES)


def _is_link(path: Path) -> bool:
    """Liên kết tắt (symlink, junction, reparse point trỏ đi chỗ khác: ``data_dir.is_link``) hay
    hard link (file thường có hơn một tên; tên kia có thể nằm ngoài ``data/``)."""
    if is_link(path):
        return True
    try:
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISREG(info.st_mode) and info.st_nlink > 1


def _guard(conn: sqlite3.Connection) -> None:
    """File là dữ liệu chưa tin cậy (F3): không chạy hàm «không vô hại» trong khung nhìn, trigger
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


def _app_tables(conn: sqlite3.Connection) -> frozenset[tuple] | None:
    """Các dòng ``sqlite_master`` của file, đọc vào danh sách có giới hạn: thừa dòng hay một dòng
    ``(loại, tên)`` lặp lại thì ``None``. Khung nhìn, trigger, bảng ảo, chỉ mục hay bảng lạ nào
    cũng làm tập này khác ``_expected_schema``."""
    limit = len(_expected_schema())
    rows = [tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, limit + 1))]
    if len(rows) > limit or len({row[:2] for row in rows}) != len(rows):
        return None
    return frozenset(rows)


def _create_tables(path: Path) -> None:
    """Cấu trúc đúng thì thôi; file còn trống thì tạo bảng (kiểm lại trong giao dịch ghi); cấu trúc
    khác (file bị thay ngay sau lần kiểm): ``_Corrupt``."""
    with closing(sqlite3.connect(path, timeout=_SQLITE_TIMEOUT, isolation_level=None)) as conn:
        _guard(conn)
        conn.text_factory = _decode_text  # UTF-8 hỏng trong sqlite_master: _Corrupt
        conn.execute("BEGIN")
        try:
            tables = _app_tables(conn)
        finally:
            conn.execute("ROLLBACK")
        if tables == _expected_schema():
            return
        if tables is None or tables:
            raise _Corrupt
        conn.execute("BEGIN IMMEDIATE")
        try:
            tables = _app_tables(conn)
            if tables is None or (tables and tables != _expected_schema()):
                raise _Corrupt
            if not tables:
                for sql in _CREATE_TABLES:
                    conn.execute(sql)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        conn.execute("COMMIT")


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, cấu trúc đúng như app tạo (hay còn trống), ``quick_check`` ổn.

    ``False`` khi chắc chắn hỏng hay lạ: cấu trúc khác (bảng, cột, trigger, khung nhìn, chỉ mục
    lạ), UTF-8 hỏng trong ``sqlite_master``, SQLite báo hỏng / không phải cơ sở dữ liệu /
    «unsupported file format», giá trị quá dài, quá số bước. Lỗi do môi trường (bận, khóa, không
    mở được, lỗi đọc/ghi, chỉ đọc, đầy ổ: ``_KEEP_FILE_CODES``) được ném lại để ``_prepare`` báo
    ``SiteIndexError`` mà không xóa file (SL-T037-1, -4; LC-T122-1).
    """
    try:
        with closing(sqlite3.connect(path, timeout=_HEALTH_TIMEOUT, isolation_level=None)) as conn:
            _guard(conn)
            conn.text_factory = _decode_text
            conn.execute("BEGIN")
            try:
                tables = _app_tables(conn)
                if tables is None or (tables and tables != _expected_schema()):
                    return False
                return conn.execute("PRAGMA quick_check").fetchone() == ("ok",)
            finally:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
    except _Corrupt:
        return False
    except sqlite3.DatabaseError as exc:
        if _is_busy(exc) or _code(exc) in _KEEP_FILE_CODES:
            raise
        return False


def _is_busy(exc: sqlite3.DatabaseError) -> bool:
    """File đang bị kết nối khác khóa (không phải hỏng)."""
    text = str(exc).lower()
    return isinstance(exc, sqlite3.OperationalError) and ("locked" in text or "busy" in text)


def _code(exc: sqlite3.DatabaseError) -> int | None:
    code = getattr(exc, "sqlite_errorcode", None)
    return code & 0xFF if isinstance(code, int) else None


def _is_corrupt(exc: sqlite3.DatabaseError) -> bool:
    """SQLite báo chắc chắn file hỏng (``SQLITE_CORRUPT``, ``SQLITE_NOTADB``, kể cả mã mở rộng)."""
    code = _code(exc)
    if code is not None:
        return code in (_SQLITE_CORRUPT, _SQLITE_NOTADB)
    text = str(exc).lower()  # phòng khi lỗi không kèm mã
    return "not a database" in text or "malformed" in text


def _is_too_big(exc: sqlite3.DatabaseError) -> bool:
    return _code(exc) == _SQLITE_TOOBIG or "too big" in str(exc).lower()


def _is_interrupted(exc: sqlite3.DatabaseError) -> bool:
    return _code(exc) == _SQLITE_INTERRUPT or "interrupted" in str(exc).lower()


def _db_error(exc: sqlite3.DatabaseError) -> SiteIndexError:
    message = _db_message(exc)
    return _BusyError(message) if _is_busy(exc) else SiteIndexError(message)


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if _is_busy(exc):
        return "File lưu tạm danh sách bài đang bận. Thử lại sau giây lát."
    if _is_corrupt(exc):
        return _MSG_BROKEN
    return (
        "Không mở được file lưu tạm danh sách bài (có thể chương trình khác đang giữ file, "
        "hoặc không có quyền ghi). Danh sách vừa tải vẫn dùng được."
    )


__all__ = [
    "DEFAULT_MAX_AGE_HOURS",
    "DEFAULT_SITE_INDEX_FILE",
    "MAX_ITEMS",
    "MSG_NOT_CONNECTED",
    "PublishedSource",
    "SiteIndex",
    "SiteIndexError",
    "SiteIndexStore",
    "SiteListing",
    "site_listing",
]

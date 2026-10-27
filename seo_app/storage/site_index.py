"""Cache danh sách bài/trang đã đăng trên site (SQLite có sẵn của Python, không thêm thư viện).

Dùng cho kiểm trùng meta (T-036), liên kết nội bộ (T-039) và kiểm link hỏng (Giai đoạn 5).
Nguồn thật là WordPress (``WordPressClient.list_published``); file này chỉ là bản tạm trên máy:
xóa đi thì lần sau tự tải lại.

Dữ liệu đọc từ file là chưa tin cậy: giới hạn số dòng và độ dài, mỗi dòng kiểm lại bằng
``PublishedItem`` và ``is_site_link`` (như lúc nhận từ site). Một dòng sai cũng coi cả cache là
hỏng: bỏ và tải lại. File hỏng hẳn (không phải SQLite, sai cấu trúc, là liên kết tắt) thì xóa
và tạo lại; cache không có gì cần giữ. Mọi câu SQL dùng tham số ``?``. Không lưu bí mật.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
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
_COLUMNS = ("id", "type", "slug", "link", "title", "meta_title", "meta_desc", "modified_gmt")


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
        try:
            with self._connect(timeout=_WRITE_TIMEOUT) as conn:
                conn.execute("DELETE FROM pages")
                conn.executemany(
                    "INSERT OR REPLACE INTO pages "
                    "(id, type, slug, link, title, meta_title, meta_desc, modified_gmt) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    rows,
                )
                conn.executemany(
                    "INSERT OR REPLACE INTO info (key, value) VALUES (?, ?)",
                    [
                        ("schema_version", SCHEMA_VERSION),
                        ("site", index.site),
                        ("fetched_at", index.fetched_at.isoformat()),
                        ("truncated", "1" if index.truncated else "0"),
                    ],
                )
        except sqlite3.DatabaseError as exc:
            raise _db_error(exc) from None
        except OSError as exc:
            raise SiteIndexError(
                f"Không ghi được file lưu tạm danh sách bài ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None

    def clear(self) -> None:
        """Xóa file cache (lần sau tự tải lại)."""
        try:
            self.path.unlink(missing_ok=True)
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
    def _connect(self, timeout: float | None = None) -> Iterator[sqlite3.Connection]:
        """``timeout``: giây chờ khi file bị khóa; ``None`` là ``_SQLITE_TIMEOUT`` (đọc lúc gọi)."""
        self._prepare()
        if timeout is None:
            timeout = _SQLITE_TIMEOUT
        try:
            # ``with conn``: một giao dịch, xong thì commit, lỗi thì rollback
            with closing(sqlite3.connect(self.path, timeout=timeout)) as conn, conn:
                conn.text_factory = _decode_text
                yield conn
        except sqlite3.DatabaseError as exc:
            if _is_busy(exc):
                raise _db_error(exc) from None
            raise

    def _prepare(self) -> None:
        """Tạo thư mục; file hỏng / liên kết tắt thì xóa; tạo bảng nếu chưa có."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.is_symlink() or (self.path.exists() and not _is_healthy(self.path)):
                # Liên kết tắt có thể trỏ ra ngoài data/ (F1): chỉ xóa chính liên kết.
                self._reset()
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS pages ("
                    "id INTEGER NOT NULL, type TEXT NOT NULL, slug TEXT NOT NULL, "
                    "link TEXT NOT NULL, title TEXT NOT NULL, meta_title TEXT NOT NULL, "
                    "meta_desc TEXT NOT NULL, modified_gmt TEXT NOT NULL, "
                    "PRIMARY KEY (type, id))"
                )
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
                )
        except sqlite3.DatabaseError as exc:
            raise _db_error(exc) from None
        except OSError as exc:
            raise SiteIndexError(
                f"Không tạo được file lưu tạm danh sách bài ({exc.strerror or 'lỗi đọc/ghi'})."
            ) from None

    def _reset(self) -> None:
        self.path.unlink(missing_ok=True)
        for suffix in ("-journal", "-wal", "-shm"):
            self.path.with_name(self.path.name + suffix).unlink(missing_ok=True)
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
    return parsed.astimezone(ZoneInfo(timezone))


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, và bảng nào đã có thì đúng cột.

    ``False`` chỉ khi **chắc chắn** hỏng: SQLite báo hỏng / không phải cơ sở dữ liệu,
    ``quick_check`` khác ``ok``, hoặc sai cột. Lỗi khác (bận, khóa, không mở được, lỗi đọc/ghi)
    được ném lại để ``_prepare`` báo ``SiteIndexError`` mà không xóa file (SL-T037-1, -4).
    """
    try:
        with closing(sqlite3.connect(path, timeout=_HEALTH_TIMEOUT)) as conn:
            if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
                return False
            pages = {row[1] for row in conn.execute("PRAGMA table_info(pages)")}
            info = {row[1] for row in conn.execute("PRAGMA table_info(info)")}
    except sqlite3.DatabaseError as exc:
        if _is_corrupt(exc):
            return False
        raise
    return (not pages or pages == set(_COLUMNS)) and (not info or info == {"key", "value"})


def _is_busy(exc: sqlite3.DatabaseError) -> bool:
    """File đang bị kết nối khác khóa (không phải hỏng)."""
    text = str(exc).lower()
    return isinstance(exc, sqlite3.OperationalError) and ("locked" in text or "busy" in text)


def _is_corrupt(exc: sqlite3.DatabaseError) -> bool:
    """SQLite báo chắc chắn file hỏng (``SQLITE_CORRUPT``, ``SQLITE_NOTADB``, kể cả mã mở rộng)."""
    code = getattr(exc, "sqlite_errorcode", None)
    if isinstance(code, int):
        return code & 0xFF in (_SQLITE_CORRUPT, _SQLITE_NOTADB)
    text = str(exc).lower()  # phòng khi lỗi không kèm mã
    return "not a database" in text or "malformed" in text


def _db_error(exc: sqlite3.DatabaseError) -> SiteIndexError:
    message = _db_message(exc)
    return _BusyError(message) if _is_busy(exc) else SiteIndexError(message)


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if _is_busy(exc):
        return "File lưu tạm danh sách bài đang bận. Thử lại sau giây lát."
    if _is_corrupt(exc):
        return "File lưu tạm danh sách bài bị lỗi nên không đọc/ghi được. Thử tải lại."
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

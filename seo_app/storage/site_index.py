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
from dataclasses import dataclass, field
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
    is_site_link,
)

DEFAULT_SITE_INDEX_FILE = PROJECT_ROOT / "data" / "site_index.sqlite"
DEFAULT_MAX_AGE_HOURS = 6.0
MAX_ITEMS = 2 * PER_PAGE * MAX_PAGES  # bài + trang, đúng mức client đọc tối đa
SCHEMA_VERSION = "1"
# Một chữ tiếng Việt UTF-8 tối đa 4 byte: chặn dòng quá to trước khi đọc vào bộ nhớ.
_MAX_FIELD_BYTES = 4 * max(MAX_LINK_CHARS, MAX_META_CHARS, MAX_TITLE_CHARS, MAX_SLUG_CHARS)
_MAX_INFO_CHARS = 2048
_CLOCK_SKEW = timedelta(minutes=5)  # thời điểm tải "ở tương lai" quá mức này = cache cũ
_SQLITE_TIMEOUT = 5
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
        cached = self.load(source.base_url)
        if cached is not None and not self._is_stale(cached, now):
            return cached
        return self.refresh(source)

    def refresh(self, source: PublishedSource) -> SiteIndex:
        """Tải lại ngay từ site rồi ghi cache (dùng cho nút "Tải lại" và trước khi gửi nháp).

        Ghi file lỗi thì vẫn trả danh sách vừa tải, kèm ``cache_error``.
        """
        items = source.list_published()
        fetched_at = self._now()
        index = SiteIndex(site=source.base_url, fetched_at=fetched_at, items=tuple(items))
        try:
            self.save(index)
        except SiteIndexError as exc:
            return SiteIndex(
                site=index.site,
                fetched_at=fetched_at,
                items=index.items,
                cache_error=str(exc),
            )
        return index

    def is_stale(self, site: str, *, now: datetime | None = None) -> bool:
        """Cache của ``site`` cũ hơn ``max_age_hours`` giờ, hoặc chưa có / hỏng / của site khác."""
        cached = self.load(site)
        return cached is None or self._is_stale(cached, now)

    # ------------------------------------------------------------ đọc / ghi

    def load(self, site: str) -> SiteIndex | None:
        """Đọc cache của ``site``. Không có, của site khác hoặc hỏng: ``None`` (không ném lỗi).

        Cache hỏng thì bỏ file luôn, để lần ghi sau tạo lại sạch.
        """
        try:
            with self._connect() as conn:
                return self._read(conn, site)
        except (_Corrupt, sqlite3.DatabaseError):
            self._reset_quietly()
            return None
        except (SiteIndexError, OSError):
            return None

    def save(self, index: SiteIndex) -> None:
        """Ghi đè toàn bộ cache bằng ``index`` trong một giao dịch."""
        if index.fetched_at.tzinfo is None:
            raise SiteIndexError("Thời điểm tải danh sách bài phải kèm múi giờ.")
        if len(index.items) > MAX_ITEMS:
            raise SiteIndexError("Danh sách bài quá dài nên không lưu tạm được.")
        rows = [tuple(getattr(item, name) for name in _COLUMNS) for item in index.items]
        try:
            with self._connect() as conn:
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
                    ],
                )
        except sqlite3.DatabaseError as exc:
            raise SiteIndexError(_db_message(exc)) from None
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
        return SiteIndex(site=site, fetched_at=fetched_at, items=tuple(items), from_cache=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self._prepare()
        try:
            # ``with conn``: một giao dịch, xong thì commit, lỗi thì rollback
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                conn.text_factory = _decode_text
                yield conn
        except sqlite3.DatabaseError as exc:
            if isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc).lower():
                raise SiteIndexError(_db_message(exc)) from None
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
            raise SiteIndexError(_db_message(exc)) from None
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


class _Corrupt(Exception):
    """Nội dung cache sai khuôn (nội bộ)."""


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
    """File là SQLite đọc được, và bảng nào đã có thì đúng cột."""
    try:
        with closing(sqlite3.connect(path, timeout=_SQLITE_TIMEOUT)) as conn:
            if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
                return False
            pages = {row[1] for row in conn.execute("PRAGMA table_info(pages)")}
            info = {row[1] for row in conn.execute("PRAGMA table_info(info)")}
    except sqlite3.DatabaseError:
        return False
    return (not pages or pages == set(_COLUMNS)) and (not info or info == {"key", "value"})


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc).lower():
        return "File lưu tạm danh sách bài đang bận. Thử lại sau giây lát."
    return "File lưu tạm danh sách bài bị lỗi nên không đọc/ghi được. Thử tải lại."


__all__ = [
    "DEFAULT_MAX_AGE_HOURS",
    "DEFAULT_SITE_INDEX_FILE",
    "MAX_ITEMS",
    "PublishedSource",
    "SiteIndex",
    "SiteIndexError",
    "SiteIndexStore",
]

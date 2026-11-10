"""Cache số liệu Search Console trong máy (T-122; thiết kế T-120 mục 3.1–3.4).

File ``data/search_cache.sqlite`` (``data/``, ``*.sqlite`` đã bị ``.gitignore`` chặn) giữ số liệu
đã lấy từ Search Console, để trang theo dõi vẽ được ngay khi mở mà không gọi mạng (thiết kế 3.3):
số theo ngày × trang (khuôn Q1), từ khóa theo trang trong từng khoảng ngày (khuôn Q2) và ngày đăng
của bài. Nguồn thật là Search Console (giữ 16 tháng): xóa file thì lần bấm «Lấy số liệu mới» sau
lấy lại được. Mỗi máy có cache riêng, không đồng bộ.

Ghi (mỗi lệnh một giao dịch; lỗi thì không ghi gì của lệnh đó):

- ``save_days``: một đoạn ngày (tối đa ``MAX_CHUNK_DAYS`` ngày, đúng một lệnh Q1) thay trọn số liệu
  của đoạn. Phần đã lấy liền mạch (``covered_start`` … ``covered_end``) chỉ nới khi đoạn mới nối
  liền phần cũ; ngày đầu tiên còn là số tạm (``first_provisional``) đi theo đoạn mới nhất, nên E
  (ngày chốt cuối) đúng cả khi các ngày tạm không có dòng nào. Mỗi lần ghi bỏ ngày cũ hơn
  ``KEEP_DAYS`` ngày (16 tháng).
- ``save_queries``: từ khóa của một khoảng (tối đa ``MAX_QUERY_RANGE_DAYS`` ngày); giữ tối đa
  ``MAX_QUERY_RANGES`` khoảng, bỏ khoảng lấy lâu nhất.
- ``save_post_dates``: ngày đăng (giờ PT) của bài; chỉ giữ bài còn trong danh sách đã đăng.
- Trần (thiết kế 3.2): ``MAX_DAY_ROWS`` dòng ngày, ``MAX_QUERY_ROWS`` dòng mỗi khoảng từ khóa, file
  ``MAX_FILE_BYTES``. Quá trần thì không ghi lệnh đó, báo câu cố định, giữ phần đang có.

An toàn (F1, F3; Lá Chắn LC-T120-9, LC-T120-10):

- ``data/`` (hay thư mục con chứa file) là liên kết: không tạo, không mở, báo ``MSG_DATA_DIR_LINK``
  (``data_dir.dir_has_link``, T-117; không lặp SL-T117-1). Chính file hay file nhật ký
  (``-journal``, ``-wal``, ``-shm``) là liên kết (symlink, junction, hard link): chỉ gỡ liên kết,
  không đụng file nó trỏ tới, rồi tạo file mới.
- Cấu trúc file chưa tin cậy (như ``plan_cache``, ``image_tags``): ``sqlite_master`` phải khớp đúng
  các bảng app tạo, kiểm trong cùng giao dịch với thao tác; ``trusted_schema = OFF``; giới hạn số
  bước và độ dài giá trị; file lạ, hỏng (``quick_check``), quá lớn thì bỏ.
- Dữ liệu đọc ra chưa tin cậy: mỗi dòng kiểm lại như lúc nhận từ Google (thiết kế 2.4): ngày đúng
  dạng trong khoảng năm, địa chỉ qua ``is_site_link`` và tiền tố ``WORDPRESS_URL`` đã chuẩn hóa
  (``site_base``: scheme, tên máy viết thường, bỏ cổng 443), số nguyên thật,
  ``0 ≤ click ≤ hiển thị ≤ 10⁹``, vị trí 1 … 10.000, từ khóa đã làm sạch ≤ 200 ký tự, ``final``
  khớp ``first_provisional``. **Một dòng sai**, hay mã băm phạm vi khác (đổi thuộc tính Search
  Console hay ``WORDPRESS_URL``), là bỏ cả cache (LC-T120-9).
- Mốc ngày giờ (``fetched_at``, các ngày) kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt
  ``OverflowError``, ``ValueError`` (LC-T120-10, như T-118).
- Không lưu bí mật, mã truy cập, email tài khoản dịch vụ; thuộc tính Search Console và
  ``WORDPRESS_URL`` chỉ lưu dạng mã băm phạm vi. Mọi câu SQL dùng tham số ``?``; không ``pickle``,
  ``eval``.

Kiểu đọc ra (``CachedDay``, ``CachedQuery``) có đúng tên trường của thiết kế 3.1, tức của hai
``Protocol`` ``CachedDayLike``, ``CachedQueryLike`` ở gói tính toán (T-123): ``day``, ``start``,
``end`` là ``date`` thuần, ``final`` là ``bool`` thật, số là ``int``/``float`` thật.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import sqlite3
import stat
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from functools import cache
from pathlib import Path
from types import MappingProxyType
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
from seo_app.images.data_dir import MSG_DATA_DIR_LINK, dir_has_link, is_link
from seo_app.plan.model import MAX_POST_ID, clean_text
from seo_app.storage.site_index import MAX_ITEMS
from seo_app.wordpress.client import MAX_LINK_CHARS, is_site_link, site_base

DEFAULT_SEARCH_CACHE_FILE = PROJECT_ROOT / "data" / "search_cache.sqlite"
SCHEMA_VERSION = "1"
KEEP_DAYS = 486  # 16 tháng: phần số liệu Search Console còn giữ
MAX_CHUNK_DAYS = 31  # một lệnh Q1
MAX_QUERY_RANGE_DAYS = 93  # một lệnh Q2
MAX_QUERY_RANGES = 6
MAX_DAY_ROWS = 300_000
MAX_QUERY_ROWS = 50_000  # mỗi khoảng từ khóa
MAX_POST_DATES = MAX_ITEMS  # không quá số bài, trang client WordPress đọc tối đa
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_IMPRESSIONS = 10**9  # một dòng của Google (thiết kế 2.4)
MAX_POSITION = 10_000
MAX_PAGE_CHARS = MAX_LINK_CHARS  # 2.000 ký tự
MAX_QUERY_CHARS = 200
# Năm hợp lệ của mọi ngày, mốc giờ trong cache (như gói tính toán T-123): ngoài khoảng này là dữ
# liệu lạ; cộng trừ vài năm quanh khoảng này không bao giờ tràn ``date``, ``datetime``.
YEAR_MIN, YEAR_MAX = 2000, 2200

MSG_BROKEN = "File lưu tạm số liệu Search Console bị lỗi nên đã bỏ; lần lấy số liệu sau tạo lại."
MSG_BUSY = "File lưu tạm số liệu Search Console đang bận. Thử lại sau giây lát."
MSG_IO = "Không đọc, ghi được file lưu tạm số liệu Search Console ({detail})."
MSG_OPEN = (
    "Không mở được file lưu tạm số liệu Search Console (có thể chương trình khác đang giữ file, "
    "hoặc không có quyền ghi). Số liệu vừa lấy chưa được lưu."
)
MSG_FULL = (
    "File lưu tạm số liệu Search Console đã tới mức tối đa nên không lưu thêm phần này; số liệu "
    "đã lưu vẫn dùng được."
)
MSG_DISK_FULL = "Ổ đĩa đã đầy nên không lưu tạm được số liệu Search Console."
MSG_BAD_DATA = "Số liệu Search Console không đúng dạng nên không lưu tạm."
MSG_BAD_RANGE = (
    "Đoạn ngày mới không khớp phần đã lưu (phải nối liền, bắt đầu từ ngày còn là số tạm) nên "
    "không lưu tạm."
)
MSG_BAD_SCOPE = (
    "Thuộc tính Search Console hay WORDPRESS_URL không hợp lệ nên không dùng bản lưu tạm."
)

_DAY_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_SQLITE_TIMEOUT = 5
_HEALTH_TIMEOUT = 1
_WRITE_TIMEOUT = 1  # như cache kế hoạch: không giữ người dùng chờ lâu khi tab khác đang ghi
_JOURNAL_SUFFIXES = ("-journal", "-wal", "-shm")
# Đầu file SQLite: «số đếm thay đổi» ở byte 24–27, tăng mỗi lần ghi xong (chế độ nhật ký thường).
_HEADER_BYTES = 100
_CHANGE_COUNTER = slice(24, 28)
# Giới hạn byte khi đọc (chữ UTF-8 tối đa 4 byte mỗi ký tự): kiểm bằng SQL trước khi đọc vào bộ nhớ.
_MAX_PAGE_BYTES = 4 * MAX_PAGE_CHARS
_MAX_QUERY_BYTES = 4 * MAX_QUERY_CHARS
_MAX_INFO_CHARS = 200
# Lớp phòng sau lớp kiểm cấu trúc (như ``plan_cache``, ``image_tags``): số bước tối đa của máy ảo
# SQLite cho mỗi lần mở, độ dài tối đa của một giá trị. Đọc cache lớn nhất (300.000 dòng ngày, 6
# khoảng × 50.000 dòng từ khóa) dùng chưa tới một phần mười mức này (đo ở báo cáo T-122).
_MAX_VM_STEPS = 400_000_000
_PROGRESS_EVERY = 1000
_MAX_SQLITE_LENGTH = 1_000_000
_SQLITE_INTERRUPT = 9
_SQLITE_CORRUPT = 11
_SQLITE_FULL = 13
_SQLITE_TOOBIG = 18
_SQLITE_NOTADB = 26
# Lỗi SQLite do môi trường, không phải do file lạ: quyền, bận, khóa, hết bộ nhớ, chỉ đọc, vào ra,
# không mở được, giao thức khóa. Gặp các mã này thì giữ file, báo câu (LC-T122-1).
_KEEP_FILE_CODES = frozenset({3, 5, 6, 7, 8, 10, 14, 15})

_CREATE_TABLES = (
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS page_day ("
    "day TEXT NOT NULL, page TEXT NOT NULL, clicks INTEGER NOT NULL, "
    "impressions INTEGER NOT NULL, position_sum REAL NOT NULL, final INTEGER NOT NULL, "
    "PRIMARY KEY (day, page)) WITHOUT ROWID",
    "CREATE TABLE IF NOT EXISTS query_range ("
    "id INTEGER PRIMARY KEY, start_day TEXT NOT NULL, end_day TEXT NOT NULL, "
    "fetched_at TEXT NOT NULL, row_count INTEGER NOT NULL, truncated INTEGER NOT NULL, "
    "UNIQUE (start_day, end_day))",
    "CREATE TABLE IF NOT EXISTS page_query ("
    "range_id INTEGER NOT NULL, page TEXT NOT NULL, query TEXT NOT NULL, "
    "clicks INTEGER NOT NULL, impressions INTEGER NOT NULL, position_sum REAL NOT NULL)",
    "CREATE TABLE IF NOT EXISTS post_date (post_id INTEGER PRIMARY KEY, published TEXT NOT NULL)",
)
# Bỏ cả cache khi đổi phạm vi: câu cố định cho từng bảng.
_WIPE = (
    "DELETE FROM info",
    "DELETE FROM page_day",
    "DELETE FROM query_range",
    "DELETE FROM page_query",
    "DELETE FROM post_date",
)
_INFO_KEYS = frozenset(
    {
        "schema_version",
        "scope_hash",
        "fetched_at",
        "covered_start",
        "covered_end",
        "first_provisional",
    }
)
_MASTER_SQL = "SELECT type, name, tbl_name, substr(sql, 1, ?) FROM sqlite_master LIMIT ?"
_MAX_SQL_BYTES = 2048


class SearchCacheError(Exception):
    """Lỗi file cache số liệu Search Console; câu tiếng Việt cố định, hiện thẳng được."""


# ------------------------------------------------------------------------------ kiểu dữ liệu


@dataclass(frozen=True)
class CacheScope:
    """Phạm vi của số liệu: thuộc tính Search Console (``GSC_SITE_URL``) và website
    (``WORDPRESS_URL``). Đổi một trong hai thì cache cũ bị bỏ (thiết kế 2.7 bước 5)."""

    site_url: str
    wordpress_url: str

    @property
    def base(self) -> str:
        """``WORDPRESS_URL`` dạng chuẩn (``site_base``); địa chỉ trang bắt đầu bằng nó + «/»."""
        return site_base(self.wordpress_url)

    @property
    def digest(self) -> str:
        """Mã băm phạm vi lưu trong file: SHA-256 của thuộc tính và ``WORDPRESS_URL``."""
        return hashlib.sha256(f"{self.site_url}\n{self.base}".encode()).hexdigest()


@dataclass(frozen=True)
class CachedDay:
    """Một ngày × một trang (khuôn Q1, thiết kế 3.1)."""

    day: date  # ngày theo giờ PT
    page: str  # địa chỉ đã kiểm: https, đúng website, đã bỏ "#…"
    clicks: int  # 0 ≤ clicks ≤ impressions
    impressions: int  # 1 … 10**9
    position_sum: float  # vị trí × lượt hiển thị (≥ impressions)
    final: bool  # False: số tạm (ngày ≥ first_provisional)


@dataclass(frozen=True)
class CachedQuery:
    """Một trang × một từ khóa trong khoảng ``start``–``end`` (khuôn Q2, thiết kế 3.1)."""

    start: date
    end: date
    page: str
    query: str  # đã clean_text, ≤ 200 ký tự
    clicks: int
    impressions: int
    position_sum: float


@dataclass(frozen=True)
class QueryRange:
    """Một khoảng từ khóa đã lấy. ``truncated``: Google trả tới trần số dòng, có thể thiếu từ
    khóa."""

    start: date
    end: date
    fetched_at: datetime
    row_count: int
    truncated: bool


@dataclass(frozen=True)
class SearchCache:
    """Toàn bộ cache của một phạm vi, đã kiểm từng dòng.

    - ``fetched_at``: lần ghi số liệu ngày gần nhất (giờ Việt Nam), để chặn bấm lại và gợi ý «có
      thể đã có số liệu mới»; ``None`` khi chưa ghi số liệu ngày nào.
    - ``covered_start`` … ``covered_end``: các ngày (giờ PT) đã lấy liền mạch, kể cả ngày không có
      lượt hiển thị nào (không có dòng).
    - ``first_provisional``: ngày đầu tiên còn là số tạm; ``None`` khi mọi ngày đã chốt.
    """

    fetched_at: datetime | None
    covered_start: date | None
    covered_end: date | None
    first_provisional: date | None
    days: tuple[CachedDay, ...]
    ranges: tuple[QueryRange, ...]
    queries: tuple[CachedQuery, ...]
    post_dates: Mapping[int, date]

    @property
    def final_end(self) -> date | None:
        """E: ngày chốt cuối (ngày trước ngày tạm đầu tiên, hay ``covered_end``); ``None`` khi
        chưa có ngày nào đã chốt."""
        if self.covered_start is None or self.covered_end is None:
            return None
        if self.first_provisional is None:
            return self.covered_end
        end = self.first_provisional - timedelta(days=1)
        return end if end >= self.covered_start else None

    def queries_for(self, start: date, end: date) -> tuple[CachedQuery, ...]:
        """Các dòng từ khóa của đúng khoảng ``start``–``end``."""
        return tuple(row for row in self.queries if row.start == start and row.end == end)

    def has_range(self, start: date, end: date) -> bool:
        """Đã lấy từ khóa cho đúng khoảng ``start``–``end`` chưa."""
        return any(item.start == start and item.end == end for item in self.ranges)


# ------------------------------------------------------------------------------------ kho


@dataclass
class SearchCacheStore:
    """Cache trong một file SQLite. Mỗi thao tác mở và đóng kết nối riêng."""

    # Tra lúc tạo (không lúc import) để test trỏ được sang thư mục tạm.
    path: Path = field(default_factory=lambda: DEFAULT_SEARCH_CACHE_FILE)
    timezone: str = DEFAULT_TIMEZONE
    reset_count: int = field(default=0, init=False)
    """Số lần file cache hỏng, lạ, hay của phạm vi khác bị bỏ đi (để test và báo nếu cần)."""

    # ------------------------------------------------------------ đọc

    def load(self, scope: CacheScope) -> SearchCache | None:
        """Toàn bộ cache của ``scope``, đã kiểm từng dòng.

        ``None``: chưa có gì, hay cache hỏng, lạ, của phạm vi khác (đã bỏ file, lần lấy sau tạo
        lại). ``SearchCacheError`` câu cố định: ``data/`` là liên kết, file đang bận, lỗi đọc."""
        _check_scope(scope)
        try:
            with self._connect(write=False) as conn:
                return _read(conn, scope, self.timezone)
        except (_Corrupt, _OtherScope):
            self._reset_quietly()
            return None
        except sqlite3.DatabaseError as exc:
            if _is_corrupt(exc):
                self._reset_quietly()
                return None
            raise SearchCacheError(_db_message(exc)) from None
        except OSError as exc:
            raise SearchCacheError(MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")) from None

    # ------------------------------------------------------------ ghi

    def save_days(
        self,
        scope: CacheScope,
        rows: Iterable[CachedDay],
        *,
        start: date,
        end: date,
        first_provisional: date | None,
        fetched_at: datetime,
        today: date,
    ) -> None:
        """Thay trọn số liệu ngày của đoạn ``start``–``end`` bằng ``rows`` (một lệnh Q1).

        - ``first_provisional``: ngày đầu tiên trong đoạn còn là số tạm (``first_incomplete_date``
          của Google, hay 3 ngày cuối khi thiếu); ``None``: cả đoạn đã chốt. ``final`` của mỗi dòng
          phải khớp.
        - Đoạn phải nối liền phần đã lưu: đoạn mới nhất bắt đầu không muộn hơn ngày tạm đầu tiên
          (hay ngày sau ``covered_end``) và tới ít nhất ``covered_end``; hoặc nằm trọn trong phần
          đã chốt. Cache trống hay của phạm vi khác thì đoạn nào cũng nhận.
        - ``today``: hôm nay theo giờ PT; bỏ các ngày cũ hơn ``KEEP_DAYS`` ngày.
        - Địa chỉ trùng sau khi bỏ ``#…`` thì cộng dồn trong cùng ngày."""
        _check_scope(scope)
        start, end, today = _day_arg(start), _day_arg(end), _day_arg(today)
        cutoff = today - timedelta(days=KEEP_DAYS - 1)
        if not cutoff <= start <= end <= today or (end - start).days >= MAX_CHUNK_DAYS:
            raise SearchCacheError(MSG_BAD_DATA)
        provisional = _chunk_provisional(first_provisional, start, end)
        stamp = _stamp(fetched_at, self.timezone)
        merged = _merge_days(rows, scope.base, start, end, provisional)
        if len(merged) > MAX_DAY_ROWS:
            raise SearchCacheError(MSG_FULL)

        def write(conn: sqlite3.Connection) -> None:
            meta = _meta_for_write(conn, scope, self.timezone)
            conn.execute("DELETE FROM page_day WHERE day < ?", (cutoff.isoformat(),))
            covered = _covered_after(meta, cutoff, start, end, provisional)
            conn.execute(
                "DELETE FROM page_day WHERE day BETWEEN ? AND ?",
                (start.isoformat(), end.isoformat()),
            )
            conn.executemany(
                "INSERT INTO page_day (day, page, clicks, impressions, position_sum, final) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                merged,
            )
            (count,) = conn.execute("SELECT COUNT(*) FROM page_day").fetchone()
            if count > MAX_DAY_ROWS:
                raise _Full
            _set_info(
                conn,
                fetched_at=stamp,
                covered_start=covered[0].isoformat(),
                covered_end=covered[1].isoformat(),
                first_provisional=covered[2].isoformat() if covered[2] else "",
            )

        self._write(write)

    def save_queries(
        self,
        scope: CacheScope,
        rows: Iterable[CachedQuery],
        *,
        start: date,
        end: date,
        fetched_at: datetime,
        truncated: bool,
    ) -> None:
        """Ghi từ khóa của khoảng ``start``–``end`` (một lệnh Q2), thay khoảng cùng ngày đã có;
        giữ ``MAX_QUERY_RANGES`` khoảng mới lấy nhất. Mỗi dòng phải đúng khoảng, từ khóa đã làm
        sạch (``clean_text``), không rỗng, tối đa ``MAX_QUERY_CHARS`` ký tự."""
        _check_scope(scope)
        start, end = _day_arg(start), _day_arg(end)
        if start > end or (end - start).days >= MAX_QUERY_RANGE_DAYS or type(truncated) is not bool:
            raise SearchCacheError(MSG_BAD_DATA)
        stamp = _stamp(fetched_at, self.timezone)
        merged = _merge_queries(rows, scope.base, start, end)
        if len(merged) > MAX_QUERY_ROWS:
            raise SearchCacheError(MSG_FULL)

        def write(conn: sqlite3.Connection) -> None:
            _meta_for_write(conn, scope, self.timezone)
            span = (start.isoformat(), end.isoformat())
            old = conn.execute(
                "SELECT id FROM query_range WHERE start_day = ? AND end_day = ?", span
            ).fetchone()
            if old is not None:
                conn.execute("DELETE FROM page_query WHERE range_id = ?", old)
                conn.execute("DELETE FROM query_range WHERE id = ?", old)
            cursor = conn.execute(
                "INSERT INTO query_range (start_day, end_day, fetched_at, row_count, truncated) "
                "VALUES (?, ?, ?, ?, ?)",
                (*span, stamp, len(merged), int(truncated)),
            )
            range_id = cursor.lastrowid
            conn.executemany(
                "INSERT INTO page_query (range_id, page, query, clicks, impressions, position_sum) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [(range_id, *row) for row in merged],
            )
            # Khoảng mới ghi luôn có mã lớn nhất: giữ các khoảng mới lấy nhất.
            conn.execute(
                "DELETE FROM query_range WHERE id NOT IN "
                "(SELECT id FROM query_range ORDER BY id DESC LIMIT ?)",
                (MAX_QUERY_RANGES,),
            )
            conn.execute(
                "DELETE FROM page_query WHERE range_id NOT IN (SELECT id FROM query_range)"
            )

        self._write(write)

    def save_post_dates(
        self,
        scope: CacheScope,
        dates: Mapping[int, date],
        *,
        keep: Iterable[int] | None = None,
    ) -> None:
        """Ghi ngày đăng (giờ PT) của bài: mã bài → ngày. ``keep``: mã các bài còn trong danh sách
        đã đăng (``SiteIndex``); bài khác bị bỏ khỏi cache."""
        _check_scope(scope)
        if not isinstance(dates, Mapping) or len(dates) > MAX_POST_DATES:
            raise SearchCacheError(MSG_BAD_DATA)
        entries = [(_post_id_arg(post), _day_arg(day).isoformat()) for post, day in dates.items()]
        kept = None if keep is None else {_post_id_arg(post) for post in keep}

        def write(conn: sqlite3.Connection) -> None:
            _meta_for_write(conn, scope, self.timezone)
            conn.executemany(
                "INSERT OR REPLACE INTO post_date (post_id, published) VALUES (?, ?)", entries
            )
            if kept is not None:
                stored = [post for (post,) in conn.execute("SELECT post_id FROM post_date")]
                gone = [(post,) for post in stored if post not in kept]
                conn.executemany("DELETE FROM post_date WHERE post_id = ?", gone)
            (count,) = conn.execute("SELECT COUNT(*) FROM post_date").fetchone()
            if count > MAX_POST_DATES:
                raise _Full

        self._write(write)

    def clear(self) -> None:
        """Xóa file cache (lần lấy số liệu sau tạo lại). Lỗi đọc thư mục khi kiểm liên kết (ví dụ
        Windows từ chối quyền) cũng ra câu cố định, không lọt lỗi Python (LC-T122-2)."""
        try:
            if dir_has_link(self.path.parent, PROJECT_ROOT):
                raise SearchCacheError(MSG_DATA_DIR_LINK)
            self._reset()
        except OSError as exc:
            raise SearchCacheError(MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")) from None

    def stamp(self) -> tuple[object, ...] | None:
        """Dấu file lưu tạm, để nơi gọi biết file đã đổi từ lần đọc trước chưa mà không phải đọc,
        kiểm lại cả file (SL-T125-1): ổ đĩa, mã file, cỡ, giờ sửa (nano giây), «số đếm thay đổi» ở
        đầu file SQLite (tăng mỗi lần ghi xong, kể cả hai lần ghi trong cùng một nhịp đồng hồ), và
        cỡ, giờ sửa của file nhật ký WAL nếu có. Dấu khác là file có thể đã đổi: đọc lại bằng
        ``load`` (kiểm đủ như mọi lần, LC-T120-9).

        ``None``: chưa có file, không phải file thường (liên kết, thư mục), hay không đọc được dấu:
        nơi gọi luôn đọc lại. Không mở SQLite, không ghi gì, không đi theo liên kết."""
        try:
            info = os.lstat(self.path)
            if not stat.S_ISREG(info.st_mode):
                return None
            with open(self.path, "rb") as file:
                header = file.read(_HEADER_BYTES)
            try:
                wal_info = os.lstat(_journal_paths(self.path)[1])
                wal = (wal_info.st_size, wal_info.st_mtime_ns)
            except FileNotFoundError:
                wal = None
        except OSError:
            return None
        return (
            os.path.abspath(self.path),
            info.st_dev,
            info.st_ino,
            info.st_size,
            info.st_mtime_ns,
            header[_CHANGE_COUNTER],
            wal,
        )

    # ------------------------------------------------------------ nội bộ

    def _write(self, action: Callable[[sqlite3.Connection], None]) -> None:
        """Chạy ``action`` trong một giao dịch ghi. File hỏng hay lạ thì bỏ rồi thử lại một lần
        trên file mới (dữ liệu đang ghi vẫn đúng)."""
        for attempt in (1, 2):
            try:
                with self._connect(write=True) as conn:
                    action(conn)
                return
            except _Corrupt:
                self._reset_quietly()
                if attempt == 2:
                    raise SearchCacheError(MSG_BROKEN) from None
            except _Full:
                raise SearchCacheError(MSG_FULL) from None
            except _BadRange:
                raise SearchCacheError(MSG_BAD_RANGE) from None
            except sqlite3.DatabaseError as exc:
                if _code(exc) == _SQLITE_FULL:
                    raise SearchCacheError(MSG_DISK_FULL) from None
                raise SearchCacheError(_db_message(exc)) from None
            except OSError as exc:
                raise SearchCacheError(
                    MSG_IO.format(detail=exc.strerror or "lỗi đọc/ghi")
                ) from None

    @contextmanager
    def _connect(self, *, write: bool) -> Iterator[sqlite3.Connection]:
        """Mở file, mở giao dịch, kiểm cấu trúc (``_app_tables``) **trước** mọi truy vấn khác, trong
        cùng giao dịch với thao tác. Cấu trúc lạ, giá trị quá dài, quá số bước: ``_Corrupt``."""
        self._prepare()
        timeout = _WRITE_TIMEOUT if write else _SQLITE_TIMEOUT
        try:
            with closing(sqlite3.connect(self.path, timeout=timeout, isolation_level=None)) as conn:
                _guard(conn)
                conn.text_factory = _decode_text
                conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                try:
                    if _app_tables(conn) != _expected_schema():
                        raise _Corrupt
                    yield conn
                    if write and _file_bytes(conn) > MAX_FILE_BYTES:
                        raise _Full
                except BaseException:
                    if conn.in_transaction:
                        conn.execute("ROLLBACK")
                    raise
                conn.execute("COMMIT")
        except sqlite3.DatabaseError as exc:
            if _is_too_big(exc) or _is_interrupted(exc):
                raise _Corrupt from None
            raise

    def _prepare(self) -> None:
        """Mỗi lần mở: ``data/`` là liên kết thì báo lỗi, không tạo, không mở (T-117); gỡ liên
        kết ở chỗ đặt file và file nhật ký (F1); file hỏng, lạ, quá lớn thì bỏ; file trống thì tạo
        bảng. Chỉ xin quyền ghi khi phải tạo bảng, để lần đọc không phải chờ tab khác đang ghi."""
        if dir_has_link(self.path.parent, PROJECT_ROOT):
            raise SearchCacheError(MSG_DATA_DIR_LINK)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for path in (self.path, *_journal_paths(self.path)):
            if _is_link(path):
                path.unlink()  # chỉ gỡ chính liên kết, không đụng file nó trỏ tới
        if self.path.exists() and not _is_healthy(self.path):
            self._reset()
        with closing(
            sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT, isolation_level=None)
        ) as conn:
            _guard(conn)
            conn.text_factory = _decode_text  # UTF-8 hỏng trong sqlite_master: _Corrupt (LC-T122-1)
            conn.execute("BEGIN")
            try:
                tables = _app_tables(conn)
            finally:
                conn.execute("ROLLBACK")
            if tables == _expected_schema():
                return
            if tables is None or tables:
                raise _Corrupt  # file bị thay ngay sau lần kiểm
            conn.execute("BEGIN IMMEDIATE")
            try:
                tables = _app_tables(conn)  # kiểm lại trong giao dịch ghi
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

    def _reset(self) -> None:
        self.path.unlink(missing_ok=True)
        for path in _journal_paths(self.path):
            path.unlink(missing_ok=True)
        self.reset_count += 1

    def _reset_quietly(self) -> None:
        with suppress(OSError):  # không xóa được: lần ghi sau sẽ báo lỗi rõ ràng
            self._reset()


# ------------------------------------------------------------------ kiểm dữ liệu khi ghi


class _Corrupt(Exception):
    """Nội dung hay cấu trúc cache sai khuôn (nội bộ)."""


class _OtherScope(Exception):
    """Cache của phạm vi khác (nội bộ)."""


class _Full(Exception):
    """Ghi thì vượt trần (nội bộ)."""


class _BadRange(Exception):
    """Đoạn ngày mới không nối liền phần đã lưu (nội bộ)."""


def _utf8_ok(text: str) -> bool:
    """Chữ mã hóa được UTF-8: không có surrogate lẻ (SQLite, mã băm đều cần UTF-8; SL-T122-3)."""
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _check_scope(scope: object) -> None:
    if not isinstance(scope, CacheScope):
        raise SearchCacheError(MSG_BAD_SCOPE)
    for value in (scope.site_url, scope.wordpress_url):
        if not isinstance(value, str) or not value or len(value) > MAX_PAGE_CHARS:
            raise SearchCacheError(MSG_BAD_SCOPE)
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in value) or not _utf8_ok(value):
            raise SearchCacheError(MSG_BAD_SCOPE)


def _is_day(value: object) -> bool:
    return type(value) is date and YEAR_MIN <= value.year <= YEAR_MAX


def _day_arg(value: object) -> date:
    """Ngày thuần (không ``datetime``) trong khoảng năm, trước mọi phép cộng trừ (LC-T120-10)."""
    if type(value) is not date or not YEAR_MIN <= value.year <= YEAR_MAX:
        raise SearchCacheError(MSG_BAD_DATA)
    return value


def _post_id_arg(value: object) -> int:
    if type(value) is not int or not 1 <= value <= MAX_POST_ID:
        raise SearchCacheError(MSG_BAD_DATA)
    return value


def _chunk_provisional(value: object, start: date, end: date) -> date | None:
    """Ngày tạm đầu tiên trong đoạn: sau đoạn thì cả đoạn đã chốt (``None``), trước đoạn thì cả
    đoạn là số tạm (``start``)."""
    if value is None:
        return None
    day = _day_arg(value)
    if day > end:
        return None
    return max(day, start)


def _stamp(moment: object, timezone: str) -> str:
    """``fetched_at`` có múi giờ, đổi sang giờ Việt Nam để lưu. Năm kiểm trước khi đổi (không tràn)
    **và** sau khi đổi: đọc lại kiểm năm của đúng mốc đã lưu, nên mốc nào ghi được thì đọc lại được
    (năm 2000 múi +14 thành 1999 giờ Việt Nam: từ chối ngay khi ghi; SL-T122-2)."""
    if not isinstance(moment, datetime) or moment.tzinfo is None:
        raise SearchCacheError(MSG_BAD_DATA)
    try:
        if moment.utcoffset() is None or not YEAR_MIN <= moment.year <= YEAR_MAX:
            raise SearchCacheError(MSG_BAD_DATA)
        stored = moment.astimezone(ZoneInfo(timezone))
    except (OverflowError, ValueError, TypeError):
        raise SearchCacheError(MSG_BAD_DATA) from None
    if not YEAR_MIN <= stored.year <= YEAR_MAX:
        raise SearchCacheError(MSG_BAD_DATA)
    return stored.isoformat()


def _numbers_ok(clicks: object, impressions: object, position_sum: object) -> bool:
    """Số của một dòng như kiểm câu trả lời Google (thiết kế 2.4): số nguyên thật (không
    ``bool``), ``0 ≤ click ≤ hiển thị``, ``1 ≤ hiển thị ≤ 10⁹``; ``position_sum`` hữu hạn, vị trí
    trung bình trong 1 … ``MAX_POSITION``."""
    if type(clicks) is not int or type(impressions) is not int:
        return False
    if not 1 <= impressions <= MAX_IMPRESSIONS or not 0 <= clicks <= impressions:
        return False
    if type(position_sum) not in (int, float) or not math.isfinite(position_sum):
        return False
    return impressions <= position_sum <= impressions * MAX_POSITION


def _page(value: object, base: str) -> str | None:
    """Địa chỉ trang đã kiểm (``#…`` đã bỏ); ``None``: không phải trang của website ``base``, hay có
    surrogate lẻ (``is_site_link`` không chặn, SQLite không ghi được: SL-T122-3)."""
    if not isinstance(value, str) or len(value) > MAX_PAGE_CHARS or not _utf8_ok(value):
        return None
    page = value.split("#", 1)[0]
    if not page.startswith(base + "/") or not is_site_link(page, base):
        return None
    return page


def _query_ok(value: object) -> bool:
    """Từ khóa đã làm sạch (``clean_text`` không đổi gì), không rỗng, tối đa 200 ký tự."""
    return (
        isinstance(value, str) and 0 < len(value) <= MAX_QUERY_CHARS and clean_text(value) == value
    )


def _fields(row: object, names: tuple[str, ...]) -> tuple[object, ...]:
    try:
        return tuple(getattr(row, name) for name in names)
    except AttributeError:
        raise SearchCacheError(MSG_BAD_DATA) from None


def _merge_days(
    rows: Iterable[CachedDay], base: str, start: date, end: date, provisional: date | None
) -> list[tuple[str, str, int, int, float, int]]:
    """Kiểm từng dòng của đoạn, cộng dồn dòng trùng (ngày, địa chỉ); sai một dòng là
    ``SearchCacheError`` (không ghi gì)."""
    if isinstance(rows, str | bytes):
        raise SearchCacheError(MSG_BAD_DATA)
    sums: dict[tuple[date, str], list] = {}
    names = ("day", "page", "clicks", "impressions", "position_sum", "final")
    for row in rows:
        day, page, clicks, impressions, position_sum, final = _fields(row, names)
        checked = _page(page, base)
        if not _is_day(day) or not start <= day <= end or checked is None:
            raise SearchCacheError(MSG_BAD_DATA)
        if not _numbers_ok(clicks, impressions, position_sum) or type(final) is not bool:
            raise SearchCacheError(MSG_BAD_DATA)
        if final != (provisional is None or day < provisional):
            raise SearchCacheError(MSG_BAD_DATA)
        key = (day, checked)
        total = sums.setdefault(key, [0, 0, 0.0])
        total[0] += clicks
        total[1] += impressions
        total[2] += float(position_sum)
    merged = []
    for (day, page), (clicks, impressions, position_sum) in sorted(sums.items()):
        if not _numbers_ok(clicks, impressions, position_sum):
            raise SearchCacheError(MSG_BAD_DATA)
        final = provisional is None or day < provisional
        merged.append((day.isoformat(), page, clicks, impressions, position_sum, int(final)))
    return merged


def _merge_queries(
    rows: Iterable[CachedQuery], base: str, start: date, end: date
) -> list[tuple[str, str, int, int, float]]:
    """Kiểm từng dòng từ khóa của khoảng, cộng dồn dòng trùng (địa chỉ, từ khóa)."""
    if isinstance(rows, str | bytes):
        raise SearchCacheError(MSG_BAD_DATA)
    sums: dict[tuple[str, str], list] = {}
    names = ("start", "end", "page", "query", "clicks", "impressions", "position_sum")
    for row in rows:
        row_start, row_end, page, query, clicks, impressions, position_sum = _fields(row, names)
        checked = _page(page, base)
        if type(row_start) is not date or type(row_end) is not date:
            raise SearchCacheError(MSG_BAD_DATA)
        if row_start != start or row_end != end or checked is None or not _query_ok(query):
            raise SearchCacheError(MSG_BAD_DATA)
        if not _numbers_ok(clicks, impressions, position_sum):
            raise SearchCacheError(MSG_BAD_DATA)
        total = sums.setdefault((checked, query), [0, 0, 0.0])
        total[0] += clicks
        total[1] += impressions
        total[2] += float(position_sum)
    merged = []
    for (page, query), (clicks, impressions, position_sum) in sorted(sums.items()):
        if not _numbers_ok(clicks, impressions, position_sum):
            raise SearchCacheError(MSG_BAD_DATA)
        merged.append((page, query, clicks, impressions, position_sum))
    return merged


@dataclass(frozen=True)
class _Meta:
    fetched_at: datetime | None
    covered_start: date | None
    covered_end: date | None
    first_provisional: date | None


def _meta_for_write(conn: sqlite3.Connection, scope: CacheScope, timezone: str) -> _Meta:
    """Thông tin cache trước khi ghi. Cache trống hay của phạm vi khác: xóa mọi bảng, ghi phạm vi
    mới (đổi thuộc tính hay ``WORDPRESS_URL`` là bỏ cả cache)."""
    info = _read_info(conn)
    if info and info.get("scope_hash") == scope.digest:
        return _parse_meta(info, timezone)
    for sql in _WIPE:
        conn.execute(sql)
    conn.executemany(
        "INSERT INTO info (key, value) VALUES (?, ?)",
        [
            ("schema_version", SCHEMA_VERSION),
            ("scope_hash", scope.digest),
            ("fetched_at", ""),
            ("covered_start", ""),
            ("covered_end", ""),
            ("first_provisional", ""),
        ],
    )
    return _Meta(None, None, None, None)


def _covered_after(
    meta: _Meta, cutoff: date, start: date, end: date, provisional: date | None
) -> tuple[date, date, date | None]:
    """Phần đã lấy liền mạch và ngày tạm đầu tiên sau khi ghi đoạn ``start``–``end``.

    Nhận: cache trống (sau khi bỏ ngày quá ``KEEP_DAYS``); đoạn mới nhất (bắt đầu không muộn hơn
    ngày sau ``covered_end`` và không muộn hơn ngày tạm đầu tiên, tới ít nhất ``covered_end``); đoạn
    nằm trọn trong phần đã chốt. Còn lại: ``_BadRange``."""
    covered_start, covered_end, first = (
        meta.covered_start,
        meta.covered_end,
        meta.first_provisional,
    )
    if covered_start is None or covered_end is None or covered_end < cutoff:
        return start, end, provisional
    covered_start = max(covered_start, cutoff)
    if first is not None and first < cutoff:
        first = cutoff
    newest = (
        start <= covered_end + timedelta(days=1)
        and end >= covered_end
        and (first is None or start <= first)
    )
    if newest:
        return min(covered_start, start), end, provisional
    inside_final = (
        covered_start <= start
        and end <= covered_end
        and provisional is None
        and (first is None or end < first)
    )
    if inside_final:
        return covered_start, covered_end, first
    raise _BadRange


def _set_info(conn: sqlite3.Connection, **values: str) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO info (key, value) VALUES (?, ?)", sorted(values.items())
    )


# ------------------------------------------------------------------ kiểm dữ liệu khi đọc


def _read(conn: sqlite3.Connection, scope: CacheScope, timezone: str) -> SearchCache | None:
    info = _read_info(conn)
    if not info:
        return None  # file mới tạo, chưa ghi gì
    if info.get("scope_hash") != scope.digest:
        raise _OtherScope
    meta = _parse_meta(info, timezone)
    days = _read_days(conn, scope.base, meta)
    ranges, queries = _read_queries(conn, scope.base, timezone)
    return SearchCache(
        fetched_at=meta.fetched_at,
        covered_start=meta.covered_start,
        covered_end=meta.covered_end,
        first_provisional=meta.first_provisional,
        days=days,
        ranges=ranges,
        queries=queries,
        post_dates=_read_post_dates(conn),
    )


def _read_info(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute(
        "SELECT key, substr(value, 1, ?) FROM info LIMIT ?",
        (_MAX_INFO_CHARS + 1, len(_INFO_KEYS) + 1),
    ).fetchall()
    info: dict[str, str] = {}
    for key, value in rows:
        if not isinstance(key, str) or not isinstance(value, str) or key in info:
            raise _Corrupt
        if len(value) > _MAX_INFO_CHARS:
            raise _Corrupt
        info[key] = value
    if info and (set(info) != _INFO_KEYS or info["schema_version"] != SCHEMA_VERSION):
        raise _Corrupt
    return info


def _parse_meta(info: Mapping[str, str], timezone: str) -> _Meta:
    """Thông tin chung: mốc giờ, phần đã lấy liền mạch, ngày tạm đầu tiên; quan hệ giữa chúng
    phải hợp lý (không thì ``_Corrupt``)."""
    fetched_at = _parse_time(info["fetched_at"], timezone) if info["fetched_at"] else None
    start = _parse_day(info["covered_start"]) if info["covered_start"] else None
    end = _parse_day(info["covered_end"]) if info["covered_end"] else None
    first = _parse_day(info["first_provisional"]) if info["first_provisional"] else None
    if (start is None) != (end is None) or (start is None and (first or fetched_at)):
        raise _Corrupt
    if start is not None and end is not None:
        if start > end or (end - start).days >= KEEP_DAYS or fetched_at is None:
            raise _Corrupt
        if first is not None and not start <= first <= end:
            raise _Corrupt
    return _Meta(fetched_at, start, end, first)


def _read_days(conn: sqlite3.Connection, base: str, meta: _Meta) -> tuple[CachedDay, ...]:
    count, biggest = conn.execute(
        "SELECT COUNT(*), COALESCE(MAX(length(CAST(page AS BLOB))), 0) FROM page_day"
    ).fetchone()
    if count > MAX_DAY_ROWS or biggest > _MAX_PAGE_BYTES:
        raise _Corrupt
    if count and meta.covered_start is None:
        raise _Corrupt
    pages: dict[str, bool] = {}
    days: dict[str, date] = {}
    result: list[CachedDay] = []
    for day_text, page, clicks, impressions, position_sum, final in conn.execute(
        "SELECT day, page, clicks, impressions, position_sum, final FROM page_day "
        "ORDER BY day, page"
    ):
        day = days.get(day_text) if isinstance(day_text, str) else None
        if day is None:
            day = days[day_text] = _parse_day(day_text)
        if not meta.covered_start <= day <= meta.covered_end:
            raise _Corrupt
        if not _known_page(pages, page, base) or type(final) is not int or final not in (0, 1):
            raise _Corrupt
        if not _numbers_ok(clicks, impressions, position_sum):
            raise _Corrupt
        expected = meta.first_provisional is None or day < meta.first_provisional
        if bool(final) != expected:
            raise _Corrupt
        result.append(CachedDay(day, page, clicks, impressions, position_sum, bool(final)))
    return tuple(result)


def _read_queries(
    conn: sqlite3.Connection, base: str, timezone: str
) -> tuple[tuple[QueryRange, ...], tuple[CachedQuery, ...]]:
    ranges: dict[int, QueryRange] = {}
    for range_id, start_text, end_text, stamp, row_count, truncated in conn.execute(
        "SELECT id, start_day, end_day, fetched_at, row_count, truncated FROM query_range "
        "ORDER BY id LIMIT ?",
        (MAX_QUERY_RANGES + 1,),
    ):
        start, end = _parse_day(start_text), _parse_day(end_text)
        if type(range_id) is not int or start > end or (end - start).days >= MAX_QUERY_RANGE_DAYS:
            raise _Corrupt
        if type(row_count) is not int or not 0 <= row_count <= MAX_QUERY_ROWS:
            raise _Corrupt
        if type(truncated) is not int or truncated not in (0, 1) or not isinstance(stamp, str):
            raise _Corrupt
        fetched_at = _parse_time(stamp, timezone)
        ranges[range_id] = QueryRange(start, end, fetched_at, row_count, bool(truncated))
    if len(ranges) > MAX_QUERY_RANGES:
        raise _Corrupt
    counts = conn.execute(
        "SELECT range_id, COUNT(*), MAX(length(CAST(page AS BLOB))), "
        "MAX(length(CAST(query AS BLOB))) FROM page_query GROUP BY range_id LIMIT ?",
        (MAX_QUERY_RANGES + 1,),
    ).fetchall()
    seen = {}
    for range_id, count, page_bytes, query_bytes in counts:
        if range_id not in ranges or count != ranges[range_id].row_count:
            raise _Corrupt
        if page_bytes > _MAX_PAGE_BYTES or query_bytes > _MAX_QUERY_BYTES:
            raise _Corrupt
        seen[range_id] = count
    if any(item.row_count and range_id not in seen for range_id, item in ranges.items()):
        raise _Corrupt
    pages: dict[str, bool] = {}
    texts: dict[str, bool] = {}
    queries: list[CachedQuery] = []
    for range_id, page, query, clicks, impressions, position_sum in conn.execute(
        "SELECT range_id, page, query, clicks, impressions, position_sum FROM page_query "
        "ORDER BY range_id, rowid"
    ):
        item = ranges.get(range_id)
        if item is None or not _known_page(pages, page, base) or not _known_query(texts, query):
            raise _Corrupt
        if not _numbers_ok(clicks, impressions, position_sum):
            raise _Corrupt
        queries.append(
            CachedQuery(item.start, item.end, page, query, clicks, impressions, position_sum)
        )
    return tuple(ranges.values()), tuple(queries)


def _read_post_dates(conn: sqlite3.Connection) -> Mapping[int, date]:
    rows = conn.execute(
        "SELECT post_id, published FROM post_date ORDER BY post_id LIMIT ?",
        (MAX_POST_DATES + 1,),
    ).fetchall()
    if len(rows) > MAX_POST_DATES:
        raise _Corrupt
    dates: dict[int, date] = {}
    for post_id, published in rows:
        if type(post_id) is not int or not 1 <= post_id <= MAX_POST_ID:
            raise _Corrupt
        dates[post_id] = _parse_day(published)
    return MappingProxyType(dates)


def _known_page(seen: dict[str, bool], page: object, base: str) -> bool:
    """Địa chỉ lưu đúng dạng đã kiểm (``_page`` không đổi gì); nhớ kết quả theo chữ."""
    if not isinstance(page, str):
        return False
    if page not in seen:
        seen[page] = _page(page, base) == page
    return seen[page]


def _known_query(seen: dict[str, bool], query: object) -> bool:
    if not isinstance(query, str):
        return False
    if query not in seen:
        seen[query] = _query_ok(query)
    return seen[query]


def _parse_day(value: object) -> date:
    """Ngày ``YYYY-MM-DD`` (chữ số ASCII) trong khoảng năm; sai thì ``_Corrupt``."""
    if not isinstance(value, str) or not _DAY_RE.fullmatch(value):
        raise _Corrupt
    try:
        day = date.fromisoformat(value)
    except ValueError:
        raise _Corrupt from None
    if not YEAR_MIN <= day.year <= YEAR_MAX:
        raise _Corrupt
    return day


def _parse_time(value: object, timezone: str) -> datetime:
    """Mốc giờ có múi giờ; năm kiểm **trước** khi đổi múi giờ (LC-T120-10) và cả sau khi đổi (đối
    xứng với ``_stamp``, G1 Lá Chắn T-122); tràn khi đổi (năm 10000, năm 0) cũng là ``_Corrupt``,
    không để lọt lỗi Python (như T-118, LC-T113-2)."""
    if not isinstance(value, str) or not value.isascii() or len(value) > 40:
        raise _Corrupt
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise _Corrupt from None
    if parsed.tzinfo is None or not YEAR_MIN <= parsed.year <= YEAR_MAX:
        raise _Corrupt
    try:
        moment = parsed.astimezone(ZoneInfo(timezone))
    except (OverflowError, ValueError):
        raise _Corrupt from None
    if not YEAR_MIN <= moment.year <= YEAR_MAX:
        raise _Corrupt
    return moment


def _decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise _Corrupt from None


# ------------------------------------------------------------------ kiểm cấu trúc file


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


def _file_bytes(conn: sqlite3.Connection) -> int:
    """Cỡ file sau thao tác (số trang × cỡ trang), đo trong giao dịch trước khi ghi xong."""
    (pages,) = conn.execute("PRAGMA page_count").fetchone()
    (size,) = conn.execute("PRAGMA page_size").fetchone()
    return pages * size


@cache
def _expected_schema() -> frozenset[tuple]:
    """Các dòng ``sqlite_master`` của các bảng app tạo, dựng bằng chính ``_CREATE_TABLES`` trong
    bộ nhớ (khớp đúng cách SQLite đang chạy ghi lại câu lệnh, kèm chỉ mục tự sinh)."""
    with closing(sqlite3.connect(":memory:")) as conn:
        for sql in _CREATE_TABLES:
            conn.execute(sql)
        return frozenset(tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, 32)))


def _app_tables(conn: sqlite3.Connection) -> frozenset[tuple] | None:
    """Các dòng ``sqlite_master`` của file, đọc vào danh sách có giới hạn: thừa dòng hay một dòng
    ``(loại, tên)`` lặp lại thì ``None``. Khung nhìn, trigger, bảng ảo, chỉ mục hay bảng lạ nào
    cũng làm tập này khác ``_expected_schema``."""
    limit = len(_expected_schema())
    rows = [tuple(row) for row in conn.execute(_MASTER_SQL, (_MAX_SQL_BYTES, limit + 1))]
    if len(rows) > limit or len({row[:2] for row in rows}) != len(rows):
        return None
    return frozenset(rows)


def _is_healthy(path: Path) -> bool:
    """File không quá lớn, là SQLite đọc được, cấu trúc đúng như app tạo (hay còn trống),
    ``quick_check`` ổn. ``False`` chỉ khi chắc chắn hỏng hay lạ; lỗi khác (bận, khóa) ném lại."""
    if path.stat().st_size > MAX_FILE_BYTES:
        return False
    try:
        with closing(sqlite3.connect(path, timeout=_HEALTH_TIMEOUT, isolation_level=None)) as conn:
            _guard(conn)
            conn.text_factory = _decode_text  # UTF-8 hỏng trong sqlite_master là file lạ
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
        # LC-T122-1: chỉ bận, khóa, lỗi vào ra, quyền (chương trình khác đang giữ file, không có
        # quyền) mới ném lại để không xóa nhầm; lỗi khác của SQLite khi đọc cấu trúc (file hỏng,
        # «unsupported file format», giá trị quá dài, quá số bước) là file lạ: bỏ file.
        if _is_busy(exc) or _code(exc) in _KEEP_FILE_CODES:
            raise
        return False


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
        return MSG_BUSY
    if _is_corrupt(exc):
        return MSG_BROKEN
    return MSG_OPEN


__all__ = [
    "DEFAULT_SEARCH_CACHE_FILE",
    "KEEP_DAYS",
    "MAX_QUERY_RANGES",
    "CacheScope",
    "CachedDay",
    "CachedQuery",
    "QueryRange",
    "SearchCache",
    "SearchCacheError",
    "SearchCacheStore",
    "site_base",
]

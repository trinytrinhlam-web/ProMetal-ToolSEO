"""Lấy số liệu Search Console, kiểm kết nối, lưu thuộc tính (T-124; thiết kế T-120 mục 1.2, 1.3,
2.4–2.6, 3.3).

Nối client Search Console (T-121), cache số liệu (T-122) và lõi theo dõi (T-123). Không có giao
diện (trang «📈 Theo dõi» và mục Search Console ở Cài đặt là T-125). Không chạy ngầm, không gọi mạng
khi nạp module: mọi hàm gọi mạng ở đây chỉ chạy khi người dùng bấm (LC-T120-21).

``refresh`` (nút «🔄 Lấy số liệu mới», thiết kế 1.3):

1. Chỉ một lần lấy chạy cùng lúc trong một tiến trình app: khóa cấp module. Tab khác bấm khi đang
   lấy thì báo «đang lấy ở tab khác», không gửi lệnh (LC-T120-22).
2. Một client mỗi lần bấm (``SearchConsoleClient.from_settings``): kiểm lại thuộc tính,
   ``WORDPRESS_URL``, file khóa. Client tự giữ trần ``MAX_REQUESTS`` lệnh, thử lại 429 một lần,
   trần lật trang (LC-T120-8); hết trần thì dừng, giữ phần đã lưu.
3. Chặn bấm lại: lần lấy gần nhất (mốc ``fetched_at`` trong cache, dùng chung các tab, không trong
   ``session_state``) chưa quá ``REFRESH_COOLDOWN``, ngày PT chưa sang ngày mới và đã có từ khóa
   hai kỳ thì không gửi lệnh. Mốc ở tương lai (đồng hồ máy từng chạy nhanh) coi như cũ (GN-2 Soi
   Lỗi T-122).
4. Đồng hồ bị chỉnh lùi (phần đã lấy ở sau hôm nay): bỏ cache rồi lấy lại (Lá Chắn T-122).
5. Khoảng cần lấy: lần đầu 16 tháng; các lần sau từ ngày đầu tiên còn là số tạm (hay ngày sau phần
   đã lấy) tới hôm nay theo giờ Google. Chia đoạn ≤ 31 ngày, ghi từng đoạn từ cũ tới mới; đoạn mới
   nhất là 31 ngày cuối (khi khoảng đủ dài) nên mọi ngày tạm nằm trong nó. Đoạn đầu tiên tới hết
   phần đã lưu (luật nối liền của cache). Gặp lỗi đầu tiên thì dừng, giữ phần đã lưu, lần bấm sau
   lấy tiếp.
6. Số tạm: dòng có ngày ≥ ``first_incomplete_date`` của đoạn. Thiếu trường ở đoạn mới nhất (kết
   thúc hôm nay PT), hay trường sai dạng ở bất kỳ đoạn nào: 3 ngày cuối của đoạn là số tạm (hướng
   an toàn, thiết kế 2.4). Đoạn cũ thiếu trường là bình thường: số đã chốt. Đoạn cũ có ngày tạm
   thì đoạn sau bắt đầu lại từ ngày tạm đó (cache chỉ giữ ngày tạm ở cuối).
7. Từ khóa của kỳ mặc định (28 ngày tới E) và kỳ trước liền kề, khi cache chưa có đúng khoảng đó.
8. Danh sách bài đã đăng: cũ hơn 6 giờ thì tải lại; WordPress lỗi thì dùng bản cũ, ghi chú. Ngày
   đăng của bài có 0 lượt hiển thị cả hai kỳ hỏi ``post_statuses`` (chỉ đọc), đổi sang ngày PT.

Các nút khác: ``check_connection`` («Kiểm tra», thiết kế 1.2), ``find_properties`` («Tìm thuộc
tính»), ``save_property`` (lưu thuộc tính vào ``.env``: chỉ một mục vừa tìm thấy, dùng được, qua
bộ kiểm chặt; LC-T120-12, -23). ``refresh_hint``: gợi ý «có thể đã có số liệu mới» (3.3), không
gọi mạng.

Câu trả về là câu tiếng Việt cố định: câu lỗi của client, cache, WordPress, ``.env`` (đã cố định,
không chép lời máy chủ) hay câu của module này, chỉ chèn số và ngày giờ do code định dạng. Chữ từ
Google (thuộc tính, tên máy) nằm ở trường riêng; giao diện hiện như chữ thuần, câu lỗi qua
``escape_markdown`` (LC-T120-11, -19; Lá Chắn T-121). Từ khóa không đi vào lời dặn AI hay Google
Sheets (LC-T120-13): module này không nhập AI, Google Sheets hay Streamlit.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from seo_app.config import DEFAULT_TIMEZONE, Settings
from seo_app.env_file import EnvFileError, gsc_site_url_overridden, set_gsc_site_url
from seo_app.google.search_console import (
    SearchConsoleClient,
    SearchConsoleError,
    SearchResult,
    SiteEntry,
    parse_property,
)
from seo_app.google.service_account import ServiceAccountError
from seo_app.storage.search_cache import (
    KEEP_DAYS,
    MAX_CHUNK_DAYS,
    CachedDay,
    CachedQuery,
    CacheScope,
    SearchCache,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.storage.site_index import SiteIndex, SiteIndexError, SiteIndexStore
from seo_app.tracking.match import build_tracking
from seo_app.tracking.periods import (
    DEFAULT_DAYS,
    Period,
    PeriodError,
    day_text,
    google_today,
    last_days,
    previous_period,
    published_day,
)
from seo_app.tracking.stats import aggregate, number_text, percent_text
from seo_app.wordpress.client import MAX_STATUS_LOOKUP, PostState, PublishedItem, WordPressError

REFRESH_COOLDOWN = timedelta(minutes=10)  # bấm lại trong chừng này mà không còn gì để lấy: chặn
CLOCK_SKEW = timedelta(minutes=5)  # mốc lấy ở tương lai quá mức này: coi như cũ
HINT_AFTER = timedelta(hours=24)  # gợi ý «có thể đã có số liệu mới» (thiết kế 3.3)
HINT_DAYS_BEHIND = 3  # … hay E cách hôm nay quá chừng này ngày
PROVISIONAL_FALLBACK_DAYS = 3  # thiếu hay sai first_incomplete_date: chừng này ngày cuối là số tạm
CHECK_DAYS = 10  # «Kiểm tra»: ngày cuối có số liệu trong chừng này ngày gần nhất
HOSTS_DAYS = 28  # «Kiểm tra»: phần lượt hiển thị ngoài website trong chừng này ngày
OUTSIDE_WARN_SHARE = 0.9  # gần hết lượt hiển thị ngoài website: WORDPRESS_URL có thể sai

_FETCH_LOCK = threading.Lock()  # LC-T120-22: một lần lấy mỗi tiến trình app

# ---------------------------------------------------------------- câu cố định
MSG_BUSY = "Đang lấy số liệu Search Console ở tab khác. Chờ tab đó xong rồi mở lại trang."
MSG_RECENT = (
    "Vừa lấy số liệu lúc {time}; Google cập nhật khoảng một lần mỗi ngày nên chưa có gì mới. "
    "Để sau rồi bấm lại."
)
MSG_DONE = "Đã lấy số liệu tới hết ngày {day} (ngày theo giờ Google)."
MSG_PROVISIONAL = "{count} ngày gần nhất còn là số tạm, chưa tính."
MSG_NO_FINAL_DAY = "Search Console chưa có ngày nào đã chốt số liệu cho website."
MSG_PARTIAL = "Đã lưu số liệu tới hết ngày {day}; phần còn lại chưa lấy được, bấm lại để lấy tiếp."
MSG_PARTIAL_NO_DAY = "Đã lưu một phần số liệu; phần còn lại chưa lấy được, bấm lại để lấy tiếp."
MSG_FAILED = "Chưa lấy được số liệu Search Console."
MSG_KEYWORDS_FAILED = "Chưa lấy được từ khóa; bấm lại để lấy tiếp."
MSG_STUCK = (
    "Search Console báo số tạm ở đoạn ngày cũ nên chưa lấy tiếp được. Để sau một ngày rồi bấm lại."
)
MSG_DROPPED = "{count} dòng số liệu không đúng dạng bị bỏ."
MSG_TRUNCATED = (
    "Có đoạn ngày nhiều dòng tới mức Google chỉ trả phần đầu: có thể thiếu trang ít lượt hiển thị."
)
MSG_KEYWORDS_TRUNCATED = (
    "Từ khóa của một kỳ chạm trần số dòng Google trả: có thể thiếu từ khóa ít lượt hiển thị."
)
MSG_CLOCK = "Giờ máy không hợp lệ nên chưa tính được ngày theo giờ Google. Kiểm tra giờ máy."
MSG_CLOCK_BACK = (
    "Số liệu đã lưu nằm sau hôm nay (giờ máy đã bị chỉnh lùi) nên bản lưu tạm được bỏ và lấy lại."
)
MSG_SITE_INDEX_OLD = "Chưa tải lại được danh sách bài từ WordPress; dùng danh sách lúc {time}."
MSG_SITE_INDEX_NONE = (
    "Chưa có danh sách bài đã đăng (chưa kết nối WordPress hay tải lỗi): chưa lấy được ngày đăng "
    "của bài."
)
MSG_POST_DATES_FAILED = "Chưa lấy được ngày đăng của bài từ WordPress."
MSG_EMPTY_CACHE = "Chưa có số liệu. Bấm «Lấy số liệu mới» (lần đầu lấy 16 tháng, khoảng một phút)."
MSG_MAY_HAVE_NEW = "Có thể đã có số liệu mới."

MSG_LISTED = "Tài khoản dịch vụ thấy thuộc tính này, quyền «{permission}»."
MSG_PERMISSION_HIGH = (
    "Phần mềm chỉ cần quyền «Hạn chế»: nên hạ quyền của tài khoản dịch vụ xuống «Hạn chế» trong "
    "Search Console (Cài đặt → Người dùng và quyền)."
)
MSG_UNVERIFIED = "Thuộc tính chưa xác minh nên chưa đọc được số liệu."
MSG_NOT_LISTED = (
    "Tài khoản dịch vụ chưa thấy thuộc tính này. Thêm email của tài khoản dịch vụ vào Search "
    "Console (Cài đặt → Người dùng và quyền, quyền «Hạn chế»)."
)
MSG_LAST_DAY = "Có số liệu đã chốt tới hết ngày {day} (ngày theo giờ Google)."
MSG_NO_RECENT_DATA = "Chưa có số liệu đã chốt trong {days} ngày gần nhất."
MSG_ALL_INSIDE = "Mọi lượt hiển thị {days} ngày qua đều thuộc website."
MSG_OUTSIDE = (
    "{share} lượt hiển thị {days} ngày qua nằm ngoài website (danh sách tên máy bên dưới): không "
    "tính."
)
MSG_MOSTLY_OUTSIDE = (
    "Gần hết lượt hiển thị nằm ngoài địa chỉ trong WORDPRESS_URL: Google có thể đang ghi số liệu "
    "cho địa chỉ khác (ví dụ có www.). Kiểm lại WORDPRESS_URL."
)
MSG_NO_IMPRESSIONS = "Chưa có lượt hiển thị nào trong {days} ngày qua."
HOST_SAME_SITE = "địa chỉ http:// hoặc lạ"  # GN-6 Soi Lỗi T-121: tên máy trùng website

MSG_SAVED = "Đã lưu thuộc tính Search Console vào file .env."
MSG_OVERRIDDEN = (
    "Biến môi trường GSC_SITE_URL của máy đang đè file .env nên thuộc tính vừa lưu chưa có hiệu "
    "lực. Xóa biến đó trong cài đặt của máy rồi mở lại phần mềm."
)
MSG_NOT_OFFERED = (
    "Chỉ lưu được thuộc tính vừa tìm thấy ở «Tìm thuộc tính» và dùng được cho website. Bấm «Tìm "
    "thuộc tính» rồi chọn lại."
)

PERMISSION_TEXT = {
    "siteOwner": "Chủ sở hữu",
    "siteFullUser": "Toàn quyền",
    "siteRestrictedUser": "Hạn chế",
    "siteUnverifiedUser": "Chưa xác minh",
}


class Outcome(StrEnum):
    """Kết quả một lần bấm «Lấy số liệu mới»."""

    DONE = "done"  # đã lấy đủ tới hôm nay
    PARTIAL = "partial"  # lưu được một phần; lần bấm sau lấy tiếp
    RECENT = "recent"  # vừa lấy, không còn gì mới: không gửi lệnh
    BUSY = "busy"  # đang lấy ở tab khác: không gửi lệnh
    FAILED = "failed"  # lần bấm này chưa lưu được gì


@dataclass(frozen=True)
class RefreshReport:
    """Kết quả ``refresh``: câu chính, các câu phụ, số lệnh Search Console đã gửi, E (ngày chốt cuối
    trong cache) sau lần bấm."""

    outcome: Outcome
    message: str
    notes: tuple[str, ...] = ()
    requests: int = 0
    final_end: date | None = None


@dataclass(frozen=True)
class HostShare:
    """Một tên máy ngoài website ở «Kiểm tra». ``host`` là chữ từ Google, đã kiểm dạng tên miền
    (T-121): hiện như chữ thuần, không dựng link (LC-T120-19). ``note``: ``HOST_SAME_SITE`` khi tên
    máy trùng website (địa chỉ ``http://`` hay lạ, GN-6)."""

    host: str
    impressions: int
    note: str = ""


@dataclass(frozen=True)
class ConnectionCheck:
    """Kết quả «Kiểm tra». ``messages``: câu cố định theo thứ tự; ``ok``: không câu nào là lỗi."""

    ok: bool
    messages: tuple[str, ...]
    permission: str = ""  # mã quyền Google (một trong PERMISSION_TEXT) hay rỗng
    last_day: date | None = None
    outside_share: float | None = None  # chỉ thuộc tính tên miền
    hosts: tuple[HostShare, ...] = ()
    requests: int = 0


@dataclass(frozen=True)
class PropertyList:
    """Kết quả «Tìm thuộc tính». ``entries`` là chữ từ Google: hiện như chữ thuần; chỉ mục
    ``usable`` mới chọn được. ``message``: câu lỗi cố định khi chưa tìm được."""

    entries: tuple[SiteEntry, ...] = ()
    skipped: int = 0
    account_email: str = ""
    message: str = ""

    @property
    def usable_site_urls(self) -> tuple[str, ...]:
        return tuple(entry.site_url for entry in self.entries if entry.usable)


@dataclass(frozen=True)
class SaveResult:
    ok: bool
    message: str
    overridden: bool = False  # biến môi trường GSC_SITE_URL đè .env (LC-T120-23)


class WordPressSource(Protocol):
    """Client WordPress (``WordPressClient``): danh sách bài đã đăng, trạng thái bài (chỉ đọc)."""

    base_url: str

    def list_published(self) -> list[PublishedItem]: ...

    def post_statuses(self, post_ids: Iterable[int]) -> dict[int, PostState]: ...


ClientFactory = Callable[..., SearchConsoleClient]


def _default_client(settings: Settings, *, with_property: bool = True) -> SearchConsoleClient:
    return SearchConsoleClient.from_settings(settings, with_property=with_property)


# ---------------------------------------------------------------- lấy số liệu


def refresh(
    settings: Settings,
    store: SearchCacheStore,
    *,
    site_index: SiteIndexStore | None = None,
    wordpress: WordPressSource | None = None,
    client_factory: ClientFactory | None = None,
    now: datetime | None = None,
) -> RefreshReport:
    """Nút «🔄 Lấy số liệu mới» (thiết kế 1.3; xem đầu module). ``wordpress``: client WordPress khi
    đã kết nối (để tải lại danh sách bài, hỏi ngày đăng); ``None`` thì chỉ dùng danh sách đã lưu.
    ``client_factory(settings)``: dựng client Search Console, mặc định ``from_settings``."""
    if not _FETCH_LOCK.acquire(blocking=False):
        return RefreshReport(Outcome.BUSY, MSG_BUSY)
    try:
        run = _Refresh(settings, store, site_index, wordpress, client_factory or _default_client)
        return run.go(_aware(now, settings))
    finally:
        _FETCH_LOCK.release()


class _Stop(Exception):
    """Lỗi đầu tiên của một lần lấy (nội bộ): dừng, giữ phần đã lưu."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class _Refresh:
    def __init__(
        self,
        settings: Settings,
        store: SearchCacheStore,
        site_index: SiteIndexStore | None,
        wordpress: WordPressSource | None,
        factory: ClientFactory,
    ) -> None:
        self.settings = settings
        self.store = store
        self.site_index = site_index
        self.wordpress = wordpress
        self.factory = factory
        self.scope = CacheScope(settings.gsc_site_url, settings.wordpress_url)
        self.client: SearchConsoleClient | None = None
        self.notes: list[str] = []
        self.dropped = 0
        self.saved_any = False  # lần bấm này đã lưu ít nhất một đoạn ngày
        self.days_complete = False  # đã lưu số liệu ngày tới hôm nay

    def go(self, now: datetime) -> RefreshReport:
        try:
            today = google_today(now)
        except PeriodError:
            return RefreshReport(Outcome.FAILED, MSG_FAILED, (MSG_CLOCK,))
        try:
            self.client = self.factory(self.settings)
            cache = self.store.load(self.scope)
            if cache is not None and cache.covered_end is not None and cache.covered_end > today:
                self.store.clear()  # đồng hồ bị chỉnh lùi: phần đã lưu ở «tương lai»
                self.notes.append(MSG_CLOCK_BACK)
                cache = None
        except (SearchConsoleError, ServiceAccountError, SearchCacheError) as exc:
            return RefreshReport(Outcome.FAILED, MSG_FAILED, (str(exc), *self.notes))
        if _is_recent(cache, now, today):
            assert cache is not None and cache.fetched_at is not None
            stamp = _time_text(cache.fetched_at, self.settings)
            return RefreshReport(
                Outcome.RECENT, MSG_RECENT.format(time=stamp), final_end=cache.final_end
            )
        try:
            self._days(cache, now, today)
            cache = self.store.load(self.scope)
            if cache is not None and cache.final_end is not None:
                periods = _default_periods(cache.final_end)
                self._keywords(cache, periods, now)
                self._post_dates(cache, periods, now)
        except _Stop as stop:
            return self._report_stop(stop.message, today)
        except SearchCacheError as exc:
            return self._report_stop(str(exc), today)
        return self._report(Outcome.DONE, cache, today, ())

    # ------------------------------------------------------------ các bước
    def _days(self, cache: SearchCache | None, now: datetime, today: date) -> None:
        """Lấy và lưu từng đoạn ngày × trang, từ cũ tới mới (xem đầu module, bước 5–6)."""
        assert self.client is not None
        start = _fetch_start(cache, today)
        reach = None  # đoạn đầu phải tới hết phần đã lưu (luật nối liền của cache)
        if cache is not None and cache.covered_end is not None and start <= cache.covered_end:
            reach = cache.covered_end
        last_end: date | None = None
        while start <= today:
            end = _chunk_end(start, today, reach)
            if last_end is not None and end <= last_end:
                raise _Stop(MSG_STUCK)  # đoạn cũ cả đoạn là số tạm: không tiến được
            try:
                result = self.client.fetch_day_page(start, end)
            except SearchConsoleError as exc:
                raise _Stop(str(exc)) from None
            provisional = _first_provisional(result, start, end, today)
            rows = [
                CachedDay(
                    day=row.day,
                    page=row.page,
                    clicks=row.clicks,
                    impressions=row.impressions,
                    position_sum=row.position_sum,
                    final=provisional is None or row.day < provisional,
                )
                for row in result.rows
                if row.day is not None and row.page is not None
            ]
            self.store.save_days(
                self.scope,
                rows,
                start=start,
                end=end,
                first_provisional=provisional,
                fetched_at=now,
                today=today,
            )
            self.saved_any = True
            self.dropped += result.dropped
            if result.truncated and MSG_TRUNCATED not in self.notes:
                self.notes.append(MSG_TRUNCATED)
            if end >= today:
                break
            last_end = end
            if provisional is None:
                start, reach = end + timedelta(days=1), None
            else:
                start, reach = provisional, today  # lấy lại từ ngày tạm, đoạn dài hết mức
        self.days_complete = True

    def _keywords(self, cache: SearchCache, periods: tuple[Period, ...], now: datetime) -> None:
        """Từ khóa của kỳ mặc định và kỳ trước liền kề, khi cache chưa có đúng khoảng đó."""
        assert self.client is not None
        for period in periods:
            if cache.has_range(period.start, period.end):
                continue
            try:
                result = self.client.fetch_page_query(period.start, period.end)
            except SearchConsoleError as exc:
                raise _Stop(f"{MSG_KEYWORDS_FAILED} {exc}") from None
            rows = [
                CachedQuery(
                    start=period.start,
                    end=period.end,
                    page=row.page,
                    query=row.query,
                    clicks=row.clicks,
                    impressions=row.impressions,
                    position_sum=row.position_sum,
                )
                for row in result.rows
                if row.page is not None and row.query is not None
            ]
            self.store.save_queries(
                self.scope,
                rows,
                start=period.start,
                end=period.end,
                fetched_at=now,
                truncated=result.truncated,
            )
            self.dropped += result.dropped
            if result.truncated and MSG_KEYWORDS_TRUNCATED not in self.notes:
                self.notes.append(MSG_KEYWORDS_TRUNCATED)

    def _post_dates(self, cache: SearchCache, periods: tuple[Period, ...], now: datetime) -> None:
        """Ngày đăng (giờ PT) của bài có 0 lượt hiển thị cả hai kỳ (nhãn «chưa có lượt hiển thị»,
        «mới đăng»). Lỗi WordPress chỉ ghi chú, không dừng."""
        index = self._site_list(now)
        if index is None:
            return
        posts = [item for item in index.items if item.type == "post"]
        tracking = build_tracking(self.settings.wordpress_url, posts, cache.days)
        quiet = [
            page.item.id
            for page in tracking.pages
            if page.item is not None
            and all(aggregate(page.days, period).impressions == 0 for period in periods)
        ]
        missing = [post for post in quiet if post not in cache.post_dates][:MAX_STATUS_LOOKUP]
        dates: dict[int, date] = {}
        if missing and self.wordpress is not None:
            try:
                states = self.wordpress.post_statuses(missing)
            except WordPressError:
                self.notes.append(MSG_POST_DATES_FAILED)
                states = {}
            wanted = set(missing)
            for post, state in states.items():
                day = published_day(state.date_gmt)
                if post in wanted and day is not None:
                    dates[post] = day
        self.store.save_post_dates(self.scope, dates, keep=[item.id for item in posts])

    def _site_list(self, now: datetime) -> SiteIndex | None:
        """Danh sách bài đã đăng: cũ hơn 6 giờ thì tải lại; WordPress lỗi thì dùng bản cũ."""
        if self.site_index is None:
            self.notes.append(MSG_SITE_INDEX_NONE)
            return None
        site = self.settings.wordpress_url
        index: SiteIndex | None
        try:
            if self.wordpress is not None:
                return self.site_index.get(self.wordpress, now=now)
            index = self.site_index.load(site)
        except WordPressError:
            index = self._old_site_list(site)
        except SiteIndexError:
            index = None
        if index is None:
            self.notes.append(MSG_SITE_INDEX_NONE)
        return index

    def _old_site_list(self, site: str) -> SiteIndex | None:
        assert self.site_index is not None
        index = self.site_index.load(site)
        if index is not None:
            stamp = _time_text(index.fetched_at, self.settings)
            self.notes.append(MSG_SITE_INDEX_OLD.format(time=stamp))
        return index

    # ------------------------------------------------------------ câu trả về
    def _report_stop(self, message: str, today: date) -> RefreshReport:
        try:
            cache = self.store.load(self.scope)
        except SearchCacheError:
            cache = None
        if self.days_complete:  # số liệu ngày đã đủ, chỉ thiếu từ khóa hay ngày đăng
            return self._report(Outcome.PARTIAL, cache, today, (message,))
        final_end = cache.final_end if cache is not None else None
        if not self.saved_any:
            outcome, main = Outcome.FAILED, MSG_FAILED
        elif final_end is None:
            outcome, main = Outcome.PARTIAL, MSG_PARTIAL_NO_DAY
        else:
            outcome, main = Outcome.PARTIAL, MSG_PARTIAL.format(day=day_text(final_end))
        notes = (message, *self._extra_notes())
        return RefreshReport(outcome, main, notes, self._requests(), final_end)

    def _report(
        self, outcome: Outcome, cache: SearchCache | None, today: date, first: tuple[str, ...]
    ) -> RefreshReport:
        final_end = cache.final_end if cache is not None else None
        notes = (*first, *self._extra_notes())
        if final_end is None:
            return RefreshReport(outcome, MSG_NO_FINAL_DAY, notes, self._requests(), None)
        message = MSG_DONE.format(day=day_text(final_end))
        waiting = (today - final_end).days
        if waiting > 0:
            message = f"{message} {MSG_PROVISIONAL.format(count=waiting)}"
        return RefreshReport(outcome, message, notes, self._requests(), final_end)

    def _requests(self) -> int:
        return self.client.request_count if self.client is not None else 0

    def _extra_notes(self) -> tuple[str, ...]:
        notes = list(self.notes)
        if self.dropped:
            notes.append(MSG_DROPPED.format(count=number_text(self.dropped)))
        return tuple(notes)


def _zone(settings: Settings) -> ZoneInfo:
    try:
        return ZoneInfo(settings.timezone_name or DEFAULT_TIMEZONE)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return ZoneInfo(DEFAULT_TIMEZONE)


def _aware(now: datetime | None, settings: Settings) -> datetime:
    """Giờ có múi giờ: mặc định đồng hồ máy; giờ không múi giờ coi là giờ của app."""
    if now is None:
        return datetime.now(_zone(settings))
    return now if now.utcoffset() is not None else now.replace(tzinfo=_zone(settings))


def _time_text(moment: datetime, settings: Settings) -> str:
    """«14:05 03/11/2026» theo múi giờ của app (mốc đã kiểm năm ở cache)."""
    try:
        local = moment.astimezone(_zone(settings))
    except (OverflowError, ValueError):
        local = moment
    return f"{local:%H:%M} {day_text(local.date())}"


def _default_periods(end: date) -> tuple[Period, ...]:
    """Kỳ mặc định 28 ngày tới E và kỳ trước liền kề (thiết kế 1.3); ngày lạ: không kỳ nào."""
    try:
        current = last_days(end, DEFAULT_DAYS)
        return current, previous_period(current)
    except PeriodError:
        return ()


def _fetch_start(cache: SearchCache | None, today: date) -> date:
    """Ngày đầu cần lấy: lần đầu 16 tháng; sau đó từ ngày tạm đầu tiên hay ngày sau phần đã lấy."""
    first = today - timedelta(days=KEEP_DAYS - 1)
    if cache is None or cache.covered_end is None or cache.covered_end < first:
        return first
    if cache.first_provisional is not None:
        return max(first, cache.first_provisional)
    return cache.covered_end + timedelta(days=1)


def _chunk_end(start: date, today: date, reach: date | None) -> date:
    """Ngày cuối của đoạn bắt đầu ở ``start`` (≤ 31 ngày). Còn ≤ 31 ngày thì tới hôm nay; không
    thì dừng trước 31 ngày cuối (đoạn mới nhất đủ 31 ngày, chứa mọi ngày tạm), nhưng tới ít nhất
    ``reach`` khi còn trong 31 ngày từ ``start``."""
    longest = start + timedelta(days=MAX_CHUNK_DAYS - 1)
    if longest >= today:
        return today
    end = min(longest, today - timedelta(days=MAX_CHUNK_DAYS))
    if reach is not None and end < reach:
        end = min(reach, longest)
    return end


def _first_provisional(result: SearchResult, start: date, end: date, today: date) -> date | None:
    """Ngày tạm đầu tiên của đoạn (thiết kế 2.4): ``first_incomplete_date`` khi đúng dạng; sai dạng,
    hay thiếu ở đoạn mới nhất (kết thúc hôm nay): 3 ngày cuối; đoạn cũ thiếu: đã chốt cả đoạn."""
    if result.metadata == "ok" and result.first_incomplete_date is not None:
        return result.first_incomplete_date
    if result.metadata == "missing" and end < today:
        return None
    return max(start, end - timedelta(days=PROVISIONAL_FALLBACK_DAYS - 1))


def _is_recent(cache: SearchCache | None, now: datetime, today: date) -> bool:
    """Vừa lấy (mốc trong cache chưa quá ``REFRESH_COOLDOWN``, không ở tương lai quá
    ``CLOCK_SKEW``), ngày PT chưa sang ngày mới, và đã có từ khóa hai kỳ: không còn gì để lấy."""
    if cache is None or cache.fetched_at is None or cache.covered_end is None:
        return False
    age = now - cache.fetched_at
    if age < -CLOCK_SKEW or age >= REFRESH_COOLDOWN or cache.covered_end < today:
        return False
    if cache.final_end is None:
        return True
    return all(cache.has_range(p.start, p.end) for p in _default_periods(cache.final_end))


def refresh_hint(cache: SearchCache | None, *, now: datetime | None = None) -> str:
    """Câu gợi ý ở trang theo dõi (thiết kế 3.3), không gọi mạng: cache trống thì hướng dẫn bấm
    lấy; lần lấy cuối quá 24 giờ (hay ở tương lai), hoặc E cách hôm nay PT quá 3 ngày thì «có thể
    đã có số liệu mới»; còn lại rỗng."""
    if cache is None or cache.fetched_at is None:
        return MSG_EMPTY_CACHE
    moment = datetime.now(cache.fetched_at.tzinfo) if now is None else now
    try:
        today = google_today(moment)
        age = moment - cache.fetched_at
    except (PeriodError, TypeError):
        return ""
    if age < -CLOCK_SKEW or age > HINT_AFTER:
        return MSG_MAY_HAVE_NEW
    final_end = cache.final_end
    if final_end is None or (today - final_end).days > HINT_DAYS_BEHIND:
        return MSG_MAY_HAVE_NEW
    return ""


# ---------------------------------------------------------------- «Kiểm tra»


def check_connection(
    settings: Settings,
    *,
    client_factory: ClientFactory | None = None,
    now: datetime | None = None,
) -> ConnectionCheck:
    """Nút «Kiểm tra» (thiết kế 1.2): (a) thuộc tính có trong ``sites`` và quyền; (b) ngày cuối có
    số liệu đã chốt trong ``CHECK_DAYS`` ngày; (c) thuộc tính tên miền: phần lượt hiển thị
    ``HOSTS_DAYS`` ngày nằm ngoài website (staging, ``www.``…). Một client, tối đa 3 lệnh."""
    factory = client_factory or _default_client
    try:
        today = google_today(_aware(now, settings))
    except PeriodError:
        return ConnectionCheck(False, (MSG_CLOCK,))
    try:
        client = factory(settings)
    except (SearchConsoleError, ServiceAccountError) as exc:
        return ConnectionCheck(False, (str(exc),))
    site = client.site
    messages: list[str] = []
    permission = ""
    last_day: date | None = None
    share: float | None = None
    hosts: tuple[HostShare, ...] = ()
    ok = True
    try:
        entries = client.list_sites().entries
        entry = next((item for item in entries if site and item.site_url == site.site_url), None)
        if entry is None:
            messages.append(MSG_NOT_LISTED)
            ok = False
        else:
            permission = entry.permission
            messages.append(MSG_LISTED.format(permission=PERMISSION_TEXT[permission]))
            if permission in ("siteOwner", "siteFullUser"):
                messages.append(MSG_PERMISSION_HIGH)
            elif permission == "siteUnverifiedUser":
                messages.append(MSG_UNVERIFIED)
                ok = False
        if ok:
            days = client.fetch_days(today - timedelta(days=CHECK_DAYS - 1), today)
            seen = [row.day for row in days.rows if row.day is not None]
            last_day = max(seen) if seen else None
            if last_day is not None:
                messages.append(MSG_LAST_DAY.format(day=day_text(last_day)))
            else:
                messages.append(MSG_NO_RECENT_DATA.format(days=CHECK_DAYS))
            if site is not None and site.kind == "domain":
                share, hosts, notes = _outside(client, today, settings)
                messages.extend(notes)
    except SearchConsoleError as exc:
        messages.append(str(exc))
        ok = False
    return ConnectionCheck(
        ok,
        tuple(messages),
        permission=permission,
        last_day=last_day,
        outside_share=share,
        hosts=hosts,
        requests=client.request_count,
    )


def _outside(
    client: SearchConsoleClient, today: date, settings: Settings
) -> tuple[float | None, tuple[HostShare, ...], list[str]]:
    check = client.check_hosts(today - timedelta(days=HOSTS_DAYS - 1), today)
    total = check.inside_impressions + check.outside_impressions
    if total == 0:
        return None, (), [MSG_NO_IMPRESSIONS.format(days=HOSTS_DAYS)]
    share = check.outside_impressions / total
    website_host = _host(settings.wordpress_url)
    hosts = tuple(
        HostShare(host, impressions, HOST_SAME_SITE if host == website_host else "")
        for host, impressions in check.hosts
    )
    if check.outside_impressions == 0:
        return share, hosts, [MSG_ALL_INSIDE.format(days=HOSTS_DAYS)]
    notes = [MSG_OUTSIDE.format(share=percent_text(share), days=HOSTS_DAYS)]
    if share >= OUTSIDE_WARN_SHARE:
        notes.append(MSG_MOSTLY_OUTSIDE)
    return share, hosts, notes


def _host(url: str) -> str:
    try:
        return urlsplit(url).hostname or ""
    except ValueError:
        return ""


# ---------------------------------------------------------------- thuộc tính


def find_properties(
    settings: Settings, *, client_factory: ClientFactory | None = None
) -> PropertyList:
    """Nút «Tìm thuộc tính»: các thuộc tính tài khoản dịch vụ thấy được (một lệnh ``sites``), kèm
    email tài khoản dịch vụ để chủ dự án thêm vào Search Console. Chưa chọn thuộc tính vẫn chạy
    được (``GSC_SITE_URL`` không được đọc)."""
    factory = client_factory or _default_client
    try:
        client = factory(settings, with_property=False)
        found = client.list_sites()
    except (SearchConsoleError, ServiceAccountError) as exc:
        return PropertyList(message=str(exc))
    return PropertyList(found.entries, found.skipped, client.account_email)


def save_property(
    site_url: str,
    found: PropertyList,
    *,
    env_file: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> SaveResult:
    """Lưu thuộc tính đã chọn vào ``.env`` (câu hỏi 2 = A; LC-T120-12): ``site_url`` phải là một mục
    **dùng được** trong ``found`` (kết quả «Tìm thuộc tính» của cùng phiên), qua ``parse_property``
    (đúng dạng tên miền) và bộ kiểm chặt của ``env_file``. Báo khi biến môi trường ``GSC_SITE_URL``
    có mặt, kể cả rỗng, đè ``.env`` (LC-T120-23)."""
    offered = found.usable_site_urls if isinstance(found, PropertyList) else ()
    if not isinstance(site_url, str) or site_url not in offered:
        return SaveResult(False, MSG_NOT_OFFERED)
    try:
        parse_property(site_url)
        set_gsc_site_url(site_url, offered=offered, env_file=env_file)
    except (SearchConsoleError, EnvFileError) as exc:
        return SaveResult(False, str(exc))
    if gsc_site_url_overridden(environ):
        return SaveResult(True, f"{MSG_SAVED} {MSG_OVERRIDDEN}", overridden=True)
    return SaveResult(True, MSG_SAVED)

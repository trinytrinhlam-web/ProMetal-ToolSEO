"""Client Google Search Console REST (Search Analytics, Sites), **chỉ đọc** (T-121).

Thiết kế T-120 mục 1.2, 2.1–2.8 (``docs/team/reports/T-120-tho-may.md``); điều kiện Lá Chắn
LC-T120-1 → -8, -15 → -18 (``docs/team/reports/T-120-la-chan.md``).

- **Hai lệnh cố định**, kiểm **trước khi gửi** ở một chỗ (``_check_call``): ``GET …/sites`` (thuộc
  tính tài khoản dịch vụ thấy được) và ``POST …/sites/{siteUrl}/searchAnalytics/query`` (số liệu
  Hiệu suất). Không lệnh ghi nào (``sites.add``, ``sites.delete``, ``sitemaps.*``), không URL
  Inspection (LC-T120-7). ``{siteUrl}`` đúng thuộc tính đã kiểm. Thân phải **đủ khóa và đủ giá
  trị** của một trong 4 khuôn cố định ``SHAPES`` (thiết kế 2.3: Q1, Q2, Q3 theo ngày, Q3 theo
  trang), so bằng JSON đã sắp khóa nên ``true``/``1``, ``1.0``/``1`` là khác nhau (LC-T120-2).
- Bộ lọc trang ``includingRegex`` ``^<WORDPRESS_URL>/`` dựng từ ``WORDPRESS_URL`` và so nguyên văn.
  Thuộc tính phải **phủ** website, so theo từng phần tên miền, không ``endswith`` trần
  (LC-T120-17); ``http://``, cổng, đường con, chữ hoa, dấu chấm cuối, địa chỉ IP đều bị từ chối;
  thuộc tính staging không phủ website nên cũng bị từ chối (LC-T120-6).
- Phạm vi ``webmasters.readonly`` duy nhất: client từ chối tài khoản dịch vụ xin phạm vi khác hay
  có ủy quyền toàn miền (LC-T120-1, -16).
- Lớp vận chuyển **dùng chung** với ``seo_app/google/sheets.py`` (nhập, không chép):
  ``_TokenRequest`` (xin mã: chỉ ``POST TOKEN_URI``, giờ chờ 30 giây, không theo chuyển hướng,
  ≤ 64 KB, gắn ``_NoAuth``), ``_refuse_redirect`` (3xx đóng ngay, không đọc thân),
  ``_read_limited`` (đọc theo luồng, quá cỡ thì bỏ), ``_Bearer`` (``repr`` che mã; có ``auth`` nên
  ``requests`` không đọc ``.netrc``). **Sửa một bên phải chạy test cả hai**:
  ``tests/test_google_sheets.py`` và ``tests/test_google_search_console.py`` (LC-T120-18).
- Mọi lệnh: giờ chờ ≤ 30 giây, ``allow_redirects=False`` (phiên ``max_redirects = 0``), câu trả lời
  ≤ 256 KB (``sites``) / ≤ 8 MB (``query``). Lỗi 429: thử lại **một** lần. Một client gửi tối đa
  ``MAX_REQUESTS`` lệnh Search Console; mỗi lần bấm tạo một client mới (LC-T120-8). Client không
  dùng chung giữa các luồng (không có lệnh chạy song song).
- Câu trả lời là dữ liệu **chưa tin cậy** (thiết kế 2.4, LC-T120-5): JSON không ``NaN``/``Infinity``
  (chặn ngay ở bộ đọc của module này), không trùng khóa; từng dòng kiểm số (số thật, không
  ``bool``, số nguyên, 0 ≤ click ≤ hiển thị ≤ 10⁹; vị trí 1 … 10.000), ngày trong khoảng đã hỏi,
  trang qua ``is_site_link`` và tiền tố website (bỏ phần ``#…``; dòng trùng sau khi bỏ thì cộng
  dồn), từ khóa qua ``clean_text`` rồi cắt 200 ký tự. Dòng sai bị bỏ và đếm; quá 10% số dòng của
  một câu trả lời thì bỏ cả câu trả lời.
- Câu lỗi cố định (thiết kế 2.8, LC-T120-4): không chép lời Google, thuộc tính, đường dẫn trang,
  từ khóa; mã lý do của Google chỉ đọc khi thuộc danh sách ASCII cố định, chỉ để chọn câu.

``from_settings`` kiểm lại thuộc tính, ``WORDPRESS_URL`` và file khóa mỗi lần (như
``SheetsClient.from_settings``). Ngày là ngày theo giờ Thái Bình Dương như Search Console
(``today_pacific``). Địa chỉ trang trả về **chưa** chuẩn hóa để so khớp (giải mã ``%``, ``/``
cuối): việc đó ở lõi theo dõi (T-123).
"""

from __future__ import annotations

import json
import math
import random
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo

import requests
from google.auth import exceptions as google_exceptions

from seo_app.google.service_account import SEARCH_CONSOLE_SCOPE, ServiceAccount
from seo_app.google.sheets import (  # lớp vận chuyển dùng chung với client Sheets (LC-T120-18)
    _MSG_AUTH,
    _MSG_AUTH_NETWORK,
    _TOKEN,
    _Bearer,
    _close_and_status,
    _read_limited,
    _Redirected,
    _refresh_message,
    _refuse_redirect,
    _TokenRequest,
    _TooLarge,
)
from seo_app.wordpress.client import MAX_LINK_CHARS, is_site_link

SEARCH_CONSOLE_URL = "https://www.googleapis.com/webmasters/v3/"
SITES_URL = SEARCH_CONSOLE_URL + "sites"
PACIFIC = ZoneInfo("America/Los_Angeles")  # Search Console tính ngày theo giờ California
DEFAULT_TIMEOUT = 30
MAX_SITES_BYTES = 256 * 1024
MAX_QUERY_BYTES = 8 * 1024 * 1024
MAX_SITES = 200
MAX_SITE_URL_CHARS = 300
MAX_REQUESTS = 20  # lệnh Search Console tối đa mỗi client (mỗi lần bấm), LC-T120-8
QUERY_RETRIES = 1  # 429: thử lại một lần
RETRY_DELAY = 2.0
MAX_HISTORY_DAYS = 486  # 16 tháng: phần số liệu Google còn giữ
MAX_COUNT = 10**9
MAX_POSITION = 10_000
MAX_QUERY_CHARS = 2048
QUERY_KEEP_CHARS = 200
MAX_BAD_ROW_SHARE = 0.10
MAX_HOSTS = 3
PERMISSIONS = ("siteOwner", "siteFullUser", "siteRestrictedUser", "siteUnverifiedUser")
_SAFE_INT = 2**53


@dataclass(frozen=True)
class Shape:
    """Khuôn thân cố định của lệnh ``query`` (thiết kế T-120 mục 2.3)."""

    name: str
    dimensions: tuple[str, ...]
    data_state: str  # "final" hoặc "all"
    max_days: int  # số ngày tối đa của khoảng (tính cả hai đầu)
    row_limit: int
    max_rows: int  # tổng số dòng tối đa khi lật trang (startRow + rowLimit ≤ max_rows)
    filtered: bool  # có bộ lọc tiền tố website


SHAPES: dict[str, Shape] = {
    # Q1: số liệu từng ngày × từng trang (số tạm đánh dấu bằng metadata).
    "day_page": Shape("day_page", ("date", "page"), "all", 31, 25_000, 200_000, True),
    # Q2: trang × từ khóa của một kỳ đang xem.
    "page_query": Shape("page_query", ("page", "query"), "final", 93, 5_000, 50_000, True),
    # Q3 theo ngày: «có số liệu tới hết ngày …».
    "days": Shape("days", ("date",), "final", 28, 200, 200, True),
    # Q3 theo trang, không lọc: chỉ đếm phần lượt hiển thị nằm ngoài website (staging, www…).
    "hosts": Shape("hosts", ("page",), "final", 28, 200, 200, False),
}

# Danh sách lệnh cố định (LC-T120-7): (tên, phương thức). Không có PUT, DELETE, PATCH.
_ROUTES: tuple[tuple[str, str], ...] = (("sites", "GET"), ("query", "POST"))

# Tên máy, tên miền: chữ thường ASCII (tên miền tiếng Việt ở dạng «xn--»), nhãn hợp lệ, ít nhất hai
# nhãn, nhãn cuối bắt đầu bằng chữ cái (không nhận địa chỉ IP), không dấu chấm cuối, không cổng.
_LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
_LAST_LABEL = r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?"
_DOMAIN = re.compile(rf"(?=.{{1,253}}$)(?:{_LABEL}\.)+{_LAST_LABEL}")
_PATH = re.compile(r"(?:/[A-Za-z0-9._~-]+)*")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_RE2_SPECIAL = re.compile(r"([\\.^$|?*+()\[\]{}])")
_REASON = re.compile(r"[A-Za-z_]{1,64}")
_API_DISABLED = frozenset({"accessNotConfigured", "SERVICE_DISABLED"})

# ---------------------------------------------------------------- câu báo cố định
_MSG_BAD_PROPERTY = (
    "Thuộc tính Search Console chưa khai báo hoặc sai dạng. Chọn lại ở Cài đặt → Google (dạng "
    "https://ten-mien/ hoặc sc-domain:ten-mien)."
)
_MSG_NOT_SITE = (
    "Thuộc tính Search Console đã chọn không phải của website trong WORDPRESS_URL (ví dụ thuộc "
    "tính staging). Chọn lại ở Cài đặt → Google."
)
_MSG_BAD_WORDPRESS = (
    "WORDPRESS_URL chưa khai báo hoặc không dùng được để lấy số liệu Search Console (phải là "
    "https://ten-mien, không cổng lạ, không ký tự lạ)."
)
_MSG_SCOPE = (
    "Tài khoản dịch vụ chưa được mở đúng quyền chỉ đọc Search Console, phần mềm không gửi lệnh."
)
_MSG_BLOCKED = (
    "Lệnh gọi Search Console này không nằm trong danh sách được phép, phần mềm không gửi."
)
_MSG_BAD_RANGE = (
    "Khoảng ngày lấy số liệu Search Console không hợp lệ (dài quá, ở tương lai hoặc cũ hơn 16 "
    "tháng), phần mềm không gửi."
)
_MSG_BUDGET = (
    "Đã gửi đủ {count} lệnh tới Search Console cho lần bấm này nên phần mềm dừng để không tốn hạn "
    "mức. Bấm lại sau để lấy tiếp."
)
_MSG_TIMEOUT = "Search Console không trả lời sau {timeout:g} giây. Thử lại sau."
_MSG_CONNECTION = "Không kết nối được tới Search Console. Kiểm tra mạng Internet rồi thử lại."
_MSG_SSL = "Lỗi chứng chỉ bảo mật (SSL) khi kết nối Google. Kiểm tra giờ máy và mạng."
_MSG_NETWORK = "Lỗi mạng khi gọi Search Console ({kind}). Thử lại sau."
_MSG_REDIRECT = (
    "Search Console trả lời bằng một lệnh chuyển hướng (mã {code}); phần mềm không đi theo. Thử "
    "lại sau."
)
_MSG_TOO_BIG = (
    "Câu trả lời của Search Console lớn bất thường, phần mềm bỏ qua. Thử lại với khoảng ngày ngắn "
    "hơn."
)
_MSG_BAD_DATA = "Search Console trả về dữ liệu không đúng dạng (mã {code}). Thử lại sau."
_MSG_API_OFF = (
    "Chưa bật Google Search Console API trong Google Cloud (mã 403). Bật API này trong project "
    "của tài khoản dịch vụ rồi thử lại."
)
_MSG_BY_STATUS = {
    400: "Search Console báo yêu cầu không hợp lệ (mã 400).",
    401: (
        "Google không nhận mã truy cập (mã 401). Thử lại; nếu vẫn lỗi, kiểm tra file khóa tài "
        "khoản dịch vụ."
    ),
    403: (
        "Tài khoản dịch vụ chưa có quyền xem thuộc tính này (mã 403). Thêm email của tài khoản "
        "dịch vụ vào Search Console (Cài đặt → Người dùng và quyền, quyền «Hạn chế»), và kiểm tra "
        "đã bật Google Search Console API trong Google Cloud."
    ),
    404: (
        "Không tìm thấy thuộc tính trong Search Console (mã 404). Kiểm tra lại thuộc tính ở trang "
        "Cài đặt."
    ),
    429: ("Search Console đang giới hạn số lần lấy số liệu (mã 429). Đợi 15 phút rồi bấm lại."),
}
_MSG_SERVER = "Máy chủ Search Console đang lỗi (mã {code}). Thử lại sau ít phút."
_MSG_REJECTED = "Search Console từ chối yêu cầu (mã {code})."


class SearchConsoleError(Exception):
    """Lỗi khi làm việc với Search Console. ``str(err)`` là câu tiếng Việt cố định: không chép lời
    Google, thuộc tính, đường dẫn trang hay từ khóa (LC-T120-4)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class SiteProperty:
    """Thuộc tính Search Console đã kiểm dạng (``parse_property``)."""

    site_url: str  # đúng chuỗi Google dùng: "sc-domain:<tên miền>" hoặc "https://<tên máy>/"
    kind: str  # "domain" (tên miền) hoặc "prefix" (tiền tố URL)
    host: str  # tên miền / tên máy, chữ thường ASCII


@dataclass(frozen=True)
class SiteEntry:
    """Một thuộc tính trong ``list_sites``. ``site_url`` là chữ Google trả: đã kiểm là ASCII nhìn
    thấy được, ≤ 300 ký tự, nhưng nơi hiện vẫn phải hiện như chữ thuần."""

    site_url: str
    permission: str  # một trong PERMISSIONS
    kind: str  # "domain", "prefix", hoặc "" khi không đúng dạng app nhận (http://, đường con…)
    covers: bool  # phủ WORDPRESS_URL

    @property
    def usable(self) -> bool:
        """Chọn được làm thuộc tính của app: đúng dạng, phủ website, quyền đã xác minh."""
        return bool(self.kind) and self.covers and self.permission != "siteUnverifiedUser"


@dataclass(frozen=True)
class SitesResult:
    entries: tuple[SiteEntry, ...]
    skipped: int  # mục sai khuôn (thiếu trường, chữ lạ, quyền lạ, trùng) bị bỏ


@dataclass(frozen=True)
class SearchRow:
    """Một dòng số liệu đã kiểm. ``day``, ``page``, ``query`` có giá trị theo khuôn đã hỏi."""

    clicks: int
    impressions: int
    position: float  # vị trí trung bình; dòng đã gộp: trung bình theo lượt hiển thị
    day: date | None = None  # ngày theo giờ PT
    page: str | None = None  # địa chỉ trang trên website (đã bỏ «#…»)
    query: str | None = None  # từ khóa đã làm sạch, ≤ 200 ký tự

    @property
    def position_sum(self) -> float:
        """Vị trí × lượt hiển thị: cộng dồn được qua nhiều ngày, nhiều dòng."""
        return self.position * self.impressions


@dataclass(frozen=True)
class SearchResult:
    rows: tuple[SearchRow, ...]
    dropped: int  # dòng sai khuôn bị bỏ
    truncated: bool  # đã lật tới trần số dòng của khuôn: có thể còn dòng chưa lấy
    first_incomplete_date: date | None = None  # chỉ khuôn "day_page": từ ngày này trở đi là số tạm
    metadata: str = "missing"  # "ok", "missing" (không có), "bad" (sai dạng)


@dataclass(frozen=True)
class HostCheck:
    """Kết quả «Kiểm tra» phần lượt hiển thị nằm ngoài website (khuôn "hosts", không giữ địa
    chỉ trang): tổng trong website, tổng ngoài website, tối đa 3 tên máy ngoài website."""

    inside_impressions: int
    outside_impressions: int
    hosts: tuple[tuple[str, int], ...]  # (tên máy đã kiểm dạng tên miền, lượt hiển thị)
    dropped: int
    truncated: bool


# ---------------------------------------------------------------- thuộc tính, website


def parse_property(value: object) -> SiteProperty:
    """Thuộc tính từ ``GSC_SITE_URL`` (hay từ ``list_sites``) đã kiểm dạng; sai thì
    ``SearchConsoleError`` câu cố định (LC-T120-17).

    Chỉ nhận ``sc-domain:<tên miền>`` và ``https://<tên máy>/`` (đúng gốc website, có ``/`` cuối):
    chữ thường ASCII, nhãn hợp lệ, không cổng, không địa chỉ IP, không ``@``, không đường con,
    không dấu chấm cuối. ``http://…`` không nhận (website chạy ``https://``)."""
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_SITE_URL_CHARS
        or not value.isascii()
    ):
        raise SearchConsoleError(_MSG_BAD_PROPERTY)
    if value.startswith("sc-domain:"):
        kind, host = "domain", value[len("sc-domain:") :]
    elif value.startswith("https://") and value.endswith("/"):
        kind, host = "prefix", value[len("https://") : -1]
    else:
        raise SearchConsoleError(_MSG_BAD_PROPERTY)
    if not _DOMAIN.fullmatch(host):
        raise SearchConsoleError(_MSG_BAD_PROPERTY)
    return SiteProperty(site_url=value, kind=kind, host=host)


def site_prefix(wordpress_url: object) -> str:
    """Tiền tố mọi trang của website: ``https://<tên máy>[/<đường con>]/`` dựng từ
    ``WORDPRESS_URL``. Sai dạng (không ``https``, có tên/mật khẩu, cổng khác 443, chữ lạ, có
    ``?``/``#``) thì ``SearchConsoleError``."""
    if (
        not isinstance(wordpress_url, str)
        or not wordpress_url
        or len(wordpress_url) > MAX_LINK_CHARS
        or not wordpress_url.isascii()
        or "\\" in wordpress_url
        or any(ch.isspace() or not ch.isprintable() for ch in wordpress_url)
    ):
        raise SearchConsoleError(_MSG_BAD_WORDPRESS)
    try:
        parts = urlsplit(wordpress_url)
        port = parts.port
    except ValueError:
        raise SearchConsoleError(_MSG_BAD_WORDPRESS) from None
    host = parts.hostname or ""
    path = parts.path.rstrip("/")
    if (
        parts.scheme != "https"
        or parts.username is not None
        or parts.password is not None
        or port not in (None, 443)
        or parts.query
        or parts.fragment
        or not _DOMAIN.fullmatch(host)
        or not _PATH.fullmatch(path)
    ):
        raise SearchConsoleError(_MSG_BAD_WORDPRESS)
    return f"https://{host}{path}/"


def page_filter_expression(prefix: str) -> str:
    """Biểu thức RE2 của bộ lọc trang: ``^`` + tiền tố, thoát các ký tự đặc biệt của RE2."""
    return "^" + _RE2_SPECIAL.sub(r"\\\1", prefix)


def covers_site(prop: SiteProperty, wordpress_url: object) -> bool:
    """Thuộc tính ``prop`` có chứa website ``WORDPRESS_URL`` không, so theo từng phần tên miền
    (LC-T120-17): thuộc tính tên miền thì tên máy website **bằng** tên miền hoặc **kết thúc bằng
    «.» + tên miền** (``evilsuachuacuasat.com`` không thuộc ``suachuacuasat.com``); thuộc tính tiền
    tố thì đúng tên máy của website."""
    try:
        host = urlsplit(site_prefix(wordpress_url)).hostname or ""
    except SearchConsoleError:
        return False
    if prop.kind == "domain":
        return host == prop.host or host.endswith("." + prop.host)
    return prop.kind == "prefix" and host == prop.host


def today_pacific(now: datetime | None = None) -> date:
    """Hôm nay theo giờ Thái Bình Dương (ngày Search Console đang ghi). ``now`` phải có múi giờ."""
    moment = datetime.now(PACIFIC) if now is None else now.astimezone(PACIFIC)
    return moment.date()


# ---------------------------------------------------------------- client
class SearchConsoleClient:
    """Đọc thuộc tính và số liệu Hiệu suất bằng tài khoản dịch vụ phạm vi chỉ đọc."""

    def __init__(
        self,
        account: ServiceAccount,
        wordpress_url: str,
        site: SiteProperty | None = None,
        *,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        sleep: Callable[[float], None] = time.sleep,
        today: Callable[[], date] = today_pacific,
        max_requests: int = MAX_REQUESTS,
    ) -> None:
        if not isinstance(account, ServiceAccount) or not _search_console_only(account):
            raise SearchConsoleError(_MSG_SCOPE)
        self._prefix = site_prefix(wordpress_url)
        self._wordpress_url = wordpress_url
        self._filter = page_filter_expression(self._prefix)
        if site is not None:
            if not isinstance(site, SiteProperty):
                raise SearchConsoleError(_MSG_BAD_PROPERTY)
            site = parse_property(site.site_url)  # kiểm lại, không tin đối tượng truyền vào
            if not covers_site(site, wordpress_url):
                raise SearchConsoleError(_MSG_NOT_SITE)
        self._site = site
        self._query_url = (
            f"{SEARCH_CONSOLE_URL}sites/{quote(site.site_url, safe='')}/searchAnalytics/query"
            if site is not None
            else None
        )
        self._account = account
        self._session = session if session is not None else requests.Session()
        # Không theo chuyển hướng ở cả lệnh Search Console lẫn lệnh xin mã (LC-T120-3).
        self._session.max_redirects = 0
        self.timeout = min(float(timeout), DEFAULT_TIMEOUT) if timeout > 0 else DEFAULT_TIMEOUT
        self._sleep = sleep
        self._today = today
        self._token_request = _TokenRequest(self._session, self.timeout)
        if type(max_requests) is not int or not 1 <= max_requests <= MAX_REQUESTS:
            max_requests = MAX_REQUESTS
        self.max_requests = max_requests
        self.request_count = 0  # lệnh Search Console đã gửi (kể cả lần thử lại 429)

    @classmethod
    def from_settings(
        cls,
        settings: Any = None,
        *,
        session: requests.Session | None = None,
        with_property: bool = True,
    ) -> SearchConsoleClient:
        """Client từ ``.env``: kiểm ``WORDPRESS_URL``, thuộc tính (``with_property``) rồi kiểm lại
        file khóa với phạm vi chỉ đọc Search Console (mỗi lần gọi).

        ``with_property=False``: chỉ để «Tìm thuộc tính» (``list_sites``) khi chưa chọn thuộc tính;
        ``GSC_SITE_URL`` không được đọc. Ném ``SearchConsoleError`` hoặc ``ServiceAccountError``."""
        from seo_app import config
        from seo_app.google.service_account import load_service_account

        if settings is None:
            settings = config.load_settings()
        wordpress_url = getattr(settings, "wordpress_url", "")
        site_prefix(wordpress_url)
        site = None
        if with_property:
            site = parse_property(getattr(settings, "gsc_site_url", ""))
            if not covers_site(site, wordpress_url):
                raise SearchConsoleError(_MSG_NOT_SITE)
        account = load_service_account(
            settings.google_service_account_file,
            scope=SEARCH_CONSOLE_SCOPE,
            image_folders=settings.image_folders,
        )
        return cls(account, wordpress_url, site, session=session)

    def __repr__(self) -> str:
        kind = self._site.kind if self._site is not None else "none"
        return f"SearchConsoleClient(property={kind!r}, sent={self.request_count})"

    @property
    def account_email(self) -> str:
        """Email tài khoản dịch vụ (để chủ dự án thêm vào Search Console; chỉ hiện ở Cài đặt)."""
        return self._account.email

    @property
    def site(self) -> SiteProperty | None:
        return self._site

    @property
    def prefix(self) -> str:
        """Tiền tố mọi trang của website (``https://<tên máy>/``)."""
        return self._prefix

    # ------------------------------------------------------------- lệnh công khai
    def list_sites(self) -> SitesResult:
        """Các thuộc tính tài khoản dịch vụ thấy được, kèm quyền và «phủ website hay không»."""
        data = self._send("GET", SITES_URL, None)
        raw_entries = data.get("siteEntry", [])
        if not isinstance(raw_entries, list) or len(raw_entries) > MAX_SITES:
            raise SearchConsoleError(_MSG_BAD_DATA.format(code=200))
        entries: list[SiteEntry] = []
        seen: set[str] = set()
        skipped = 0
        for raw in raw_entries:
            entry = self._site_entry(raw)
            if entry is None or entry.site_url in seen:
                skipped += 1
                continue
            seen.add(entry.site_url)
            entries.append(entry)
        return SitesResult(entries=tuple(entries), skipped=skipped)

    def fetch_day_page(self, start: date, end: date) -> SearchResult:
        """Khuôn Q1: số liệu từng ngày × từng trang (``dataState = all``, ≤ 31 ngày), lật trang."""
        return self._fetch(SHAPES["day_page"], start, end)

    def fetch_page_query(self, start: date, end: date) -> SearchResult:
        """Khuôn Q2: trang × từ khóa của một kỳ (số đã chốt, ≤ 93 ngày), lật trang."""
        return self._fetch(SHAPES["page_query"], start, end)

    def fetch_days(self, start: date, end: date) -> SearchResult:
        """Khuôn Q3 theo ngày: các ngày đã có số liệu chốt (≤ 28 ngày), cho «Kiểm tra»."""
        return self._fetch(SHAPES["days"], start, end)

    def check_hosts(self, start: date, end: date) -> HostCheck:
        """Khuôn Q3 theo trang, **không** lọc: đếm lượt hiển thị trong và ngoài website (thiết kế
        1.2 «Kiểm tra»). Không giữ địa chỉ trang ngoài website, chỉ tên máy đã kiểm dạng."""
        shape = SHAPES["hosts"]
        answer = self._send("POST", self._require_query_url(), self._body(shape, start, end, 0))
        raw_rows = self._raw_rows(answer, shape)
        inside = outside = dropped = 0
        hosts: dict[str, int] = {}
        for raw in raw_rows:
            numbers = _numbers(raw)
            keys = raw.get("keys") if isinstance(raw, dict) else None
            if (
                numbers is None
                or not isinstance(keys, list)
                or len(keys) != 1
                or not isinstance(keys[0], str)
                or len(keys[0]) > MAX_LINK_CHARS
            ):
                dropped += 1
                continue
            impressions = numbers[1]
            if self._page(keys[0]) is not None:
                inside += impressions
                continue
            outside += impressions
            host = _host_of(keys[0])
            if host is not None:
                hosts[host] = hosts.get(host, 0) + impressions
        _check_share(dropped, len(raw_rows))
        top = sorted(hosts.items(), key=lambda item: (-item[1], item[0]))[:MAX_HOSTS]
        return HostCheck(
            inside_impressions=inside,
            outside_impressions=outside,
            hosts=tuple(top),
            dropped=dropped,
            truncated=len(raw_rows) == shape.row_limit,
        )

    # ------------------------------------------------------------- nội bộ
    def _fetch(self, shape: Shape, start: date, end: date) -> SearchResult:
        url = self._require_query_url()
        rows: list[SearchRow] = []
        dropped = 0
        first_incomplete: date | None = None
        metadata = "missing"
        truncated = False
        start_row = 0
        while True:
            answer = self._send("POST", url, self._body(shape, start, end, start_row))
            raw_rows = self._raw_rows(answer, shape)
            page_dropped = 0
            for raw in raw_rows:
                row = self._row(raw, shape, start, end)
                if row is None:
                    page_dropped += 1
                else:
                    rows.append(row)
            _check_share(page_dropped, len(raw_rows))
            dropped += page_dropped
            if start_row == 0 and shape.data_state == "all":
                first_incomplete, metadata = _metadata(answer, start, end)
            if len(raw_rows) < shape.row_limit:
                break
            start_row += shape.row_limit
            if start_row + shape.row_limit > shape.max_rows:
                truncated = True
                break
        return SearchResult(
            rows=tuple(_merge(rows)),
            dropped=dropped,
            truncated=truncated,
            first_incomplete_date=first_incomplete,
            metadata=metadata,
        )

    def _require_query_url(self) -> str:
        if self._query_url is None:
            raise SearchConsoleError(_MSG_BAD_PROPERTY)
        return self._query_url

    def _body(self, shape: Shape, start: date, end: date, start_row: int) -> dict[str, Any]:
        """Thân lệnh ``query`` theo khuôn ``shape``; khoảng ngày sai thì không dựng."""
        today = self._today()
        if type(start) is not date or type(end) is not date or type(today) is not date:
            raise SearchConsoleError(_MSG_BAD_RANGE)
        if (
            start > end
            or end > today
            or (end - start).days + 1 > shape.max_days
            or (today - start).days > MAX_HISTORY_DAYS
        ):
            raise SearchConsoleError(_MSG_BAD_RANGE)
        if (
            type(start_row) is not int
            or start_row < 0
            or start_row % shape.row_limit
            or start_row + shape.row_limit > shape.max_rows
        ):
            raise SearchConsoleError(_MSG_BLOCKED)
        body: dict[str, Any] = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": list(shape.dimensions),
            "type": "web",
            "aggregationType": "byPage",
            "dataState": shape.data_state,
            "rowLimit": shape.row_limit,
            "startRow": start_row,
        }
        if shape.filtered:
            body["dimensionFilterGroups"] = [
                {
                    "groupType": "and",
                    "filters": [
                        {
                            "dimension": "page",
                            "operator": "includingRegex",
                            "expression": self._filter,
                        }
                    ],
                }
            ]
        return body

    def _check_call(self, method: str, url: str, body: object) -> int:
        """Lệnh có trong danh sách cố định không (kiểm TRƯỚC KHI gửi, LC-T120-2, -7). Trả giới
        hạn cỡ câu trả lời; không có thì ``SearchConsoleError`` câu cố định."""
        for name, route_method in _ROUTES:
            if method != route_method:
                continue
            if name == "sites" and url == SITES_URL and body is None:
                return MAX_SITES_BYTES
            if name == "query" and url == self._query_url and self._known_body(body):
                return MAX_QUERY_BYTES
        raise SearchConsoleError(_MSG_BLOCKED)

    def _known_body(self, body: object) -> bool:
        """Thân đúng **nguyên văn** một trong các khuôn (đủ khóa, đủ giá trị, đúng kiểu)."""
        if not isinstance(body, dict):
            return False
        try:
            sent = json.dumps(body, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError):
            return False
        start, end = _iso_day(body.get("startDate")), _iso_day(body.get("endDate"))
        if start is None or end is None:
            return False
        for shape in SHAPES.values():
            try:
                expected = self._body(shape, start, end, body.get("startRow"))
            except SearchConsoleError:
                continue
            if json.dumps(expected, sort_keys=True) == sent:
                return True
        return False

    def _send(self, method: str, url: str, body: object) -> dict[str, Any]:
        limit = self._check_call(method, url, body)
        token = self._access_token()
        for attempt in range(QUERY_RETRIES + 1):
            if self.request_count >= self.max_requests:
                raise SearchConsoleError(_MSG_BUDGET.format(count=self.max_requests))
            self.request_count += 1
            status, data = self._call(method, url, body, token, limit)
            if status == 429 and attempt < QUERY_RETRIES:
                self._sleep(RETRY_DELAY + random.uniform(0, 0.5))
                continue
            return _answer(status, data)
        raise AssertionError("unreachable")  # pragma: no cover

    def _access_token(self) -> str:
        """Mã truy cập (chỉ trong bộ nhớ). Hết hạn thì xin lại qua ``_TokenRequest``."""
        credentials = self._account.credentials
        if not credentials.valid:
            try:
                credentials.refresh(self._token_request)
            except google_exceptions.RefreshError as exc:
                raise SearchConsoleError(_refresh_message(exc)) from None
            except google_exceptions.TransportError:
                raise SearchConsoleError(_MSG_AUTH_NETWORK) from None
            except (
                google_exceptions.GoogleAuthError,
                ValueError,
                TypeError,
                KeyError,
                # Như client Sheets: ``expires_in`` quá lớn (OverflowError), thân lồng sâu
                # (RecursionError). Không bắt ``Exception``: lỗi bộ chặn mạng của test phải lọt ra.
                OverflowError,
                RecursionError,
            ):
                raise SearchConsoleError(_MSG_AUTH) from None
        token = credentials.token
        if not isinstance(token, str) or not _TOKEN.fullmatch(token):
            raise SearchConsoleError(_MSG_AUTH)
        return token

    def _call(
        self, method: str, url: str, body: object, token: str, limit: int
    ) -> tuple[int, bytes]:
        try:
            response = self._session.request(
                method,
                url,
                json=body,
                headers={"Accept": "application/json"},
                timeout=self.timeout,
                allow_redirects=False,
                stream=True,
                auth=_Bearer(token),
                hooks={"response": [_refuse_redirect]},
            )
        except _Redirected as exc:
            # 3xx (có hay không có Location): không đọc thân, không đi theo (LC-T120-3).
            raise SearchConsoleError(
                _MSG_REDIRECT.format(code=exc.status), status_code=exc.status
            ) from None
        except requests.exceptions.TooManyRedirects as exc:
            code = _close_and_status(exc)
            raise SearchConsoleError(
                _MSG_REDIRECT.format(code=code or "3xx"), status_code=code
            ) from None
        except requests.exceptions.SSLError:
            raise SearchConsoleError(_MSG_SSL) from None
        except requests.exceptions.Timeout:
            raise SearchConsoleError(_MSG_TIMEOUT.format(timeout=self.timeout)) from None
        except requests.exceptions.ConnectionError:
            raise SearchConsoleError(_MSG_CONNECTION) from None
        except (requests.RequestException, OSError) as exc:
            raise SearchConsoleError(_MSG_NETWORK.format(kind=type(exc).__name__)) from None
        status = response.status_code
        try:
            if 300 <= status < 400:  # phòng thêm (móc đã chặn mọi 3xx trước khi tới đây)
                raise SearchConsoleError(_MSG_REDIRECT.format(code=status), status_code=status)
            return status, _read_limited(response, limit)
        except _TooLarge:
            raise SearchConsoleError(_MSG_TOO_BIG, status_code=status) from None
        except (requests.RequestException, OSError):
            raise SearchConsoleError(_MSG_CONNECTION, status_code=status) from None
        finally:
            response.close()

    @staticmethod
    def _raw_rows(answer: dict[str, Any], shape: Shape) -> list[Any]:
        aggregation = answer.get("responseAggregationType")
        if aggregation is not None and aggregation != "byPage":
            raise SearchConsoleError(_MSG_BAD_DATA.format(code=200))
        raw_rows = answer.get("rows", [])
        if not isinstance(raw_rows, list) or len(raw_rows) > shape.row_limit:
            raise SearchConsoleError(_MSG_BAD_DATA.format(code=200))
        return raw_rows

    def _row(self, raw: object, shape: Shape, start: date, end: date) -> SearchRow | None:
        """Một dòng đã kiểm (thiết kế 2.4); sai khuôn thì ``None``."""
        numbers = _numbers(raw)
        keys = raw.get("keys") if isinstance(raw, dict) else None
        if (
            numbers is None
            or not isinstance(keys, list)
            or len(keys) != len(shape.dimensions)
            or not all(isinstance(key, str) for key in keys)
        ):
            return None
        fields: dict[str, Any] = {}
        for dimension, key in zip(shape.dimensions, keys, strict=True):
            if dimension == "date":
                fields["day"] = _iso_day(key, start, end)
            elif dimension == "page":
                fields["page"] = self._page(key)
            else:
                fields["query"] = _query_text(key) or None
            if fields[_FIELD[dimension]] is None:
                return None
        clicks, impressions, position = numbers
        return SearchRow(clicks=clicks, impressions=impressions, position=position, **fields)

    def _page(self, value: str) -> str | None:
        """Địa chỉ trang trên đúng website (``is_site_link`` + tiền tố), đã bỏ phần ``#…``."""
        if len(value) > MAX_LINK_CHARS:
            return None
        page = value.split("#", 1)[0]
        if not page.startswith(self._prefix) or not is_site_link(page, self._wordpress_url):
            return None
        return page

    def _site_entry(self, raw: object) -> SiteEntry | None:
        """Một mục ``siteEntry`` đã kiểm; sai khuôn thì ``None`` (đếm là mục bị bỏ)."""
        if not isinstance(raw, dict):
            return None
        url, permission = raw.get("siteUrl"), raw.get("permissionLevel")
        if (
            not isinstance(url, str)
            or not 1 <= len(url) <= MAX_SITE_URL_CHARS
            or not url.isascii()
            or not url.isprintable()
            or " " in url
            or permission not in PERMISSIONS
        ):
            return None
        try:
            prop = parse_property(url)
        except SearchConsoleError:
            return SiteEntry(site_url=url, permission=permission, kind="", covers=False)
        return SiteEntry(
            site_url=url,
            permission=permission,
            kind=prop.kind,
            covers=covers_site(prop, self._wordpress_url),
        )


_FIELD = {"date": "day", "page": "page", "query": "query"}


# ---------------------------------------------------------------- kiểm khuôn dữ liệu
def _search_console_only(account: ServiceAccount) -> bool:
    """Đối tượng xác thực có đúng một phạm vi ``webmasters.readonly`` và không ủy quyền toàn miền
    (LC-T120-1, -16)."""
    credentials = account.credentials
    scopes = getattr(credentials, "scopes", None)
    return (
        isinstance(scopes, list | tuple)
        and list(scopes) == [SEARCH_CONSOLE_SCOPE]
        and getattr(credentials, "_subject", None) is None
    )


def _number(value: object) -> float | None:
    """Số thật (không ``bool``), hữu hạn; số nguyên quá lớn coi như sai khuôn."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return float(value) if -_SAFE_INT <= value <= _SAFE_INT else None
    if isinstance(value, float) and math.isfinite(value):
        return value
    return None


def _count(value: object) -> int | None:
    number = _number(value)
    if number is None or not 0 <= number <= MAX_COUNT or not number.is_integer():
        return None
    return int(number)


def _numbers(raw: object) -> tuple[int, int, float] | None:
    """(click, lượt hiển thị, vị trí) của một dòng; sai khuôn thì ``None``. ``ctr`` có thì phải
    trong 0 … 1, nhưng không dùng (app tự tính lại từ click và lượt hiển thị)."""
    if not isinstance(raw, dict):
        return None
    clicks, impressions = _count(raw.get("clicks")), _count(raw.get("impressions"))
    position = _number(raw.get("position"))
    if clicks is None or impressions is None or position is None:
        return None
    if impressions < 1 or clicks > impressions or not 1 <= position <= MAX_POSITION:
        return None
    if "ctr" in raw:
        ctr = _number(raw["ctr"])
        if ctr is None or not 0 <= ctr <= 1:
            return None
    return clicks, impressions, position


def _check_share(dropped: int, total: int) -> None:
    """Quá 10% số dòng của một câu trả lời sai khuôn: bỏ cả câu trả lời (dữ liệu lạ)."""
    if total and dropped / total > MAX_BAD_ROW_SHARE:
        raise SearchConsoleError(_MSG_BAD_DATA.format(code=200))


def _iso_day(value: object, start: date | None = None, end: date | None = None) -> date | None:
    """Ngày ``YYYY-MM-DD`` hợp lệ (trong ``start`` … ``end`` nếu có); sai thì ``None``."""
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        return None
    try:
        day = date.fromisoformat(value)
    except ValueError:
        return None
    if (start is not None and day < start) or (end is not None and day > end):
        return None
    return day


def _query_text(value: str) -> str:
    """Từ khóa người lạ gõ: làm sạch như chữ kế hoạch (``clean_text``: bỏ ký tự điều khiển, vô
    hình, đảo hướng chữ; NFC; gộp khoảng trắng), cắt ``QUERY_KEEP_CHARS`` ký tự. Rỗng: bỏ dòng."""
    if not 1 <= len(value) <= MAX_QUERY_CHARS:
        return ""
    # Nhập muộn: ``seo_app.plan.model`` kéo theo lớp AI (chậm); chỉ cần khi có từ khóa.
    from seo_app.plan.model import clean_text

    return clean_text(value)[:QUERY_KEEP_CHARS].rstrip()


def _host_of(page: str) -> str | None:
    """Tên máy của một địa chỉ ngoài website, chỉ khi đúng dạng tên miền (để hiện ở «Kiểm tra»)."""
    try:
        host = urlsplit(page).hostname
    except ValueError:
        return None
    return host if isinstance(host, str) and _DOMAIN.fullmatch(host) else None


def _merge(rows: list[SearchRow]) -> list[SearchRow]:
    """Gộp dòng trùng khóa (cùng ngày, trang, từ khóa; xảy ra khi bỏ phần ``#…`` của địa chỉ):
    cộng click, lượt hiển thị; vị trí trung bình theo lượt hiển thị. Giữ thứ tự gặp đầu tiên."""
    totals: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = (row.day, row.page, row.query)
        if key in totals:
            item = totals[key]
            item[0] += row.clicks
            item[1] += row.impressions
            item[2] += row.position_sum
        else:
            totals[key] = [row.clicks, row.impressions, row.position_sum]
    return [
        SearchRow(
            clicks=int(clicks),
            impressions=int(impressions),
            position=position_sum / impressions,
            day=key[0],
            page=key[1],
            query=key[2],
        )
        for key, (clicks, impressions, position_sum) in totals.items()
    ]


def _metadata(answer: dict[str, Any], start: date, end: date) -> tuple[date | None, str]:
    """Ngày đầu tiên còn là số tạm (``metadata.first_incomplete_date``; nhận cả tên dạng
    ``firstIncompleteDate``). Không có: ``"missing"``; sai dạng hay ngoài khoảng: ``"bad"``."""
    meta = answer.get("metadata")
    if meta is None:
        return None, "missing"
    if not isinstance(meta, dict):
        return None, "bad"
    value = meta.get("first_incomplete_date", meta.get("firstIncompleteDate"))
    if value is None:
        return None, "missing"
    day = _iso_day(value, start, end)
    return (day, "ok") if day is not None else (None, "bad")


def _reject_constant(_name: str) -> float:
    raise ValueError("NaN/Infinity không phải số hợp lệ")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("trùng khóa")
        result[key] = value
    return result


def _parse_json(data: bytes) -> Any:
    """JSON của Google, đọc như dữ liệu chưa tin cậy (LC-T120-5): không ``NaN``/``Infinity``,
    không trùng khóa, lồng sâu không làm sập. Đọc không được thì trả ``_BAD``."""
    try:
        return json.loads(
            data.decode("utf-8"),
            parse_constant=_reject_constant,
            object_pairs_hook=_no_duplicate_keys,
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        return _BAD


_BAD = object()


def _reasons(data: bytes) -> set[str]:
    """Mã lý do trong câu lỗi của Google (``error.errors[].reason``, ``error.details[].reason``),
    chỉ chữ ASCII ngắn; dùng để chọn câu cố định, không bao giờ hiện ra (LC-T120-4)."""
    answer = _parse_json(data)
    error = answer.get("error") if isinstance(answer, dict) else None
    if not isinstance(error, dict):
        return set()
    found: set[str] = set()
    for field_name in ("errors", "details"):
        items = error.get(field_name)
        if not isinstance(items, list):
            continue
        for item in items[:20]:
            reason = item.get("reason") if isinstance(item, dict) else None
            if isinstance(reason, str) and _REASON.fullmatch(reason):
                found.add(reason)
    return found


def _answer(status: int, data: bytes) -> dict[str, Any]:
    if status >= 500:
        raise SearchConsoleError(_MSG_SERVER.format(code=status), status_code=status)
    if status >= 400:
        if status == 403 and _reasons(data) & _API_DISABLED:
            raise SearchConsoleError(_MSG_API_OFF, status_code=status)
        message = _MSG_BY_STATUS.get(status, _MSG_REJECTED.format(code=status))
        raise SearchConsoleError(message, status_code=status)
    if status != 200:
        raise SearchConsoleError(_MSG_BAD_DATA.format(code=status), status_code=status)
    answer = _parse_json(data)
    if not isinstance(answer, dict):
        raise SearchConsoleError(_MSG_BAD_DATA.format(code=status), status_code=status)
    return answer

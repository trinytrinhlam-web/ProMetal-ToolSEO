"""📈 Theo dõi trên Google: số liệu Search Console của từng bài, trang trên website (T-125; thiết kế
T-120 mục 1.5–1.7, 4.1, 4.4; chủ dự án 04/11: trang mới giữa Kế hoạch và Cài đặt, chỉ hiện số đã
chốt, ngưỡng mặc định, không kiểm lập chỉ mục trong app).

Chỉ đọc, và **mở trang không gọi mạng** (LC-T120-14, -21): số liệu, danh sách bài đã đăng, kế hoạch
đọc từ bản lưu tạm trong máy, chỉ khi file đã có (mở kho là tạo file: mở trang không ghi gì xuống
đĩa). Chỉ nút «🔄 Lấy số liệu mới» gọi Search Console (``refresh`` của T-124: client mới mỗi lần
bấm, một lần lấy mỗi tiến trình app). Không ``st.cache_data``, ``st.cache_resource``,
``st.fragment``, không tự làm mới. Bản lưu tạm đã đọc giữ trong phiên theo dấu file, đọc và kiểm lại
khi file đổi (SL-T125-1, ``load_cache``).

Hiển thị an toàn (LC-T120-11, -19, -20; Lá Chắn T-123 mục 7, T-124 B.1):

- Chữ từ Google (từ khóa, đường dẫn «Trang khác») và WordPress (tiêu đề bài) chỉ hiện trong ô bảng
  qua ``safe_rows``, trong ô chọn (chữ thuần) hay qua ``escape_markdown``; không
  ``unsafe_allow_html``, không cột link, không dựng link từ chữ đó. Chỉ hiện ``TrackedPage.label``,
  ``KeywordGroup.text``, ``KeywordVariant.text``; không hiện ``PageKey``, ``KeywordGroup.key``.
- Câu của lõi (``report.message``, ``report.notes``, câu lỗi bản lưu tạm) qua ``escape_markdown``.
- Biểu đồ dựng từ khuôn cố định trong code (``CLICK_CHART``, ``POSITION_CHART``): dữ liệu chỉ có
  ngày (code định dạng) và số; tên bài nằm ngoài biểu đồ.
- Từ khóa chỉ hiện ở đây: không vào lời dặn AI, không ghi Google Sheets (LC-T120-13).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

import streamlit as st

from seo_app import ui
from seo_app.config import load_settings
from seo_app.plan import model as plan_model
from seo_app.plan import propose, sync
from seo_app.plan.model import PlanRow
from seo_app.storage import plan_cache, search_cache, site_index
from seo_app.storage.search_cache import (
    CachedQuery,
    CacheScope,
    SearchCache,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.text import escape_markdown
from seo_app.tracking import refresh as tracking_refresh
from seo_app.tracking.flags import LABELS, attention_counts, attention_text, page_flags
from seo_app.tracking.keywords import (
    DEFAULT_ROWS,
    HIDDEN_QUERIES_NOTE,
    MAIN_KEYWORD_TEXT,
    NEW_KEYWORD_TEXT,
    keyword_table,
)
from seo_app.tracking.match import build_tracking, page_key
from seo_app.tracking.model import (
    Comparison,
    Flag,
    FlagKind,
    KeywordTable,
    MatchStatus,
    PageKey,
    PageStats,
    SiteTracking,
    TrackedPage,
)
from seo_app.tracking.periods import (
    DEFAULT_DAYS,
    PRESET_DAYS,
    Period,
    PeriodError,
    custom_period,
    day_text,
    last_days,
    previous_period,
    year_before,
)
from seo_app.tracking.stats import (
    LOW_DATA_IMPRESSIONS,
    LOW_DATA_TEXT,
    aggregate,
    change_text,
    compare,
    ctr_change_text,
    decimal_text,
    number_text,
    rank_change_text,
    round_half_up,
    shown_ctr_percent,
    shown_position,
    site_totals,
    weekly,
)
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import PublishedItem

S = st.session_state

# Khóa phiên của trang (tiền tố «trk-»). Nhãn ô chọn cố định giữa các lần chạy (CLAUDE.md).
RANGE_KEY = "trk-range"
RANGE_LABELS = ("7 ngày", "28 ngày", "3 tháng", "Tùy chọn")
RANGE_DAYS = dict(zip(RANGE_LABELS[:-1], PRESET_DAYS, strict=True))  # 7, 28, 91 ngày
CUSTOM = RANGE_LABELS[-1]
DEFAULT_RANGE = RANGE_LABELS[PRESET_DAYS.index(DEFAULT_DAYS)]
FROM_KEY, TO_KEY = "trk-from", "trk-to"
COMPARE_KEY = "trk-compare"
COMPARE_LABELS = ("Kỳ trước", "Cùng kỳ năm trước")
PLAN_ONLY_KEY = "trk-plan-only"
FLAG_KEY = "trk-flag"
ALL_FLAGS = "all"
FLAG_OPTIONS = (ALL_FLAGS, *(kind.value for kind in FlagKind))
FLAG_TEXT = {ALL_FLAGS: "Mọi bài, trang", **{kind.value: LABELS[kind] for kind in FlagKind}}
PAGE_KEY = "trk-page"
KEYWORD_LIMIT_KEY = "trk-keyword-limit"
VARIANTS_KEY = "trk-variants"
REPORT_KEY = "trk-report"
CLEAR_ASK_KEY = "trk-clear-ask"
FLASH_KEY = "trk-flash"
CACHE_MEMO_KEY = "trk-cache-memo"  # bản lưu tạm đã đọc của phiên, theo dấu file (SL-T125-1)
PLAN_PICK_KEY = "trk-plan-pick"
GOOGLE_HANDOFF_KEY = "plan_google_keywords"  # trang Kế hoạch đọc khóa này (T-127)

KIND_TEXT = {"post": "Bài", "page": "Trang", "other": "Trang khác"}
NO_NUMBER = "—"
OUTCOME_KIND = {
    tracking_refresh.Outcome.DONE: "success",
    tracking_refresh.Outcome.PARTIAL: "warning",
    tracking_refresh.Outcome.RECENT: "info",
    tracking_refresh.Outcome.BUSY: "info",
    tracking_refresh.Outcome.FAILED: "error",
}
UNMATCHED_PLAN = (MatchStatus.NOT_FOUND, MatchStatus.AMBIGUOUS, MatchStatus.DUPLICATE)

MSG_SUBTITLE = (
    "Lượt click, lượt hiển thị, vị trí của từng bài, trang trên Google (Search Console, chỉ đọc)."
)
MSG_NO_PROPERTY = (
    "Chưa chọn thuộc tính Search Console. Vào Cài đặt → 📗 Google → Search Console, bấm «Tìm "
    "thuộc tính», chọn thuộc tính của website rồi lưu."
)
MSG_NO_WORDPRESS = "Chưa khai báo địa chỉ website (WORDPRESS_URL) trong file .env."
MSG_NO_KEY_FILE = (
    "Chưa khai báo file khóa tài khoản dịch vụ Google (GOOGLE_SERVICE_ACCOUNT_FILE) trong file "
    ".env."
)
MSG_FETCH_HELP = (
    "Hỏi Search Console (chỉ đọc) phần số liệu còn thiếu. Lần đầu lấy 16 tháng, khoảng một phút; "
    "các lần sau chỉ lấy vài ngày mới."
)
MSG_FETCHING = (
    "Đang lấy số liệu từ Search Console… Lần đầu khoảng một phút; lệnh xin quyền đọc có thể chờ "
    "thêm vài giây."
)
MSG_NO_FINAL = "Search Console chưa có ngày nào đã chốt số liệu cho website: chưa có gì để hiện."
MSG_RANGE_SHORT = (
    "Số liệu đã lưu chỉ có từ ngày {first} tới {last}, chưa đủ cho khoảng {period}. Chọn khoảng "
    "ngắn hơn, hoặc bấm «Lấy số liệu mới» để lấy tiếp."
)
MSG_COMPARE_MISSING = "Chưa có số liệu của kỳ so sánh ({period}) nên chưa so."
MSG_NO_INDEX = (
    "Chưa có danh sách bài đã đăng trên máy nên số liệu chưa gắn được với bài (mọi địa chỉ nằm ở "
    "«Trang khác»). Kết nối WordPress rồi bấm «Lấy số liệu mới»."
)
MSG_SKIPPED_ITEMS = (
    "{count} bài, trang có địa chỉ không khớp địa chỉ website trong cài đặt (WORDPRESS_URL) nên "
    "không gắn được số liệu."
)
MSG_SKIPPED_ROWS = "{count} dòng số liệu nằm ngoài địa chỉ website nên không tính."
MSG_UNMATCHED_PLAN = (
    "{count} dòng kế hoạch «Đã đăng» chưa nối được với bài trên website (xem ô «Mã bài "
    "WordPress» ở trang Kế hoạch)."
)
MSG_TOTALS_NOTE = (
    "Tổng cộng theo từng trang nên có thể cao hơn chút so với biểu đồ của Search Console (Search "
    "Console tính theo cả website). Chỉ tính số đã chốt."
)
MSG_LOW_DATA_NOTE = (
    f"«{LOW_DATA_TEXT}»: một trong hai kỳ dưới {LOW_DATA_IMPRESSIONS} lượt hiển thị nên chưa so "
    "CTR, vị trí."
)
MSG_TABLE_ORDER = "Bảng xếp theo click nhiều nhất, rồi lượt hiển thị."
MSG_NOTHING_SHOWN = "Không có bài, trang nào khớp bộ lọc."
MSG_INDEXING = (
    "Bài «chưa có lượt hiển thị» có thể chưa được Google lập chỉ mục. Kiểm bằng tay: mở Search "
    "Console → ô «Kiểm tra URL» ở trên cùng → dán địa chỉ bài. Chưa có trên Google thì bấm «Yêu "
    "cầu lập chỉ mục»."
)
MSG_SHORT_PERIOD = "Khoảng ngắn hơn một tuần nên chưa vẽ biểu đồ theo tuần."
MSG_NO_KEYWORDS = (
    "Chưa có từ khóa cho khoảng này. Mỗi lần bấm «Lấy số liệu mới», phần mềm lấy từ khóa của 28 "
    "ngày gần nhất và kỳ trước liền kề."
)
MSG_NO_KEYWORD_ROWS = "Chưa có từ khóa nào của bài này trong khoảng đang xem."
MSG_KEYWORDS_SKIPPED = "{count} dòng từ khóa không đúng dạng bị bỏ."
MSG_PLAN_PICK = f"Chọn từ khóa đưa vào kế hoạch (tối đa {propose.MAX_GOOGLE_KEYWORDS})"
MSG_PLAN_HELP = (
    "Mở trang Kế hoạch: mỗi từ khóa đã chọn thành một đề xuất «Thêm bài» (nguồn Search Console). "
    "Bạn duyệt rồi mới ghi vào Google Sheet."
)
MSG_PLAN_NONE = (
    "Không có từ khóa nào đưa vào kế hoạch được: chỉ nhận chữ, số, khoảng trắng, dấu «-», tối đa "
    f"{propose.GOOGLE_KEYWORD_MAX} ký tự, không có số điện thoại, email, địa chỉ web."
)
MSG_PLAN_LEFT_OUT = (
    "{count} từ khóa không có trong ô chọn: có ký tự khác chữ, số, khoảng trắng, dấu «-», dài quá "
    f"{propose.GOOGLE_KEYWORD_MAX} ký tự, hay có số điện thoại, email, địa chỉ web."
)
MSG_OTHERS_NOTE = (
    "Địa chỉ có số liệu trên Google mà không khớp bài, trang nào trong danh sách đã đăng: trang "
    "chủ, chuyên mục, thẻ, địa chỉ cũ trước khi đổi đường dẫn, trang tìm kiếm."
)
MSG_CACHE_NOTE = (
    "Số liệu đã lấy được lưu tạm trong máy (thư mục data của phần mềm), để mở trang không phải hỏi "
    "Google. Xóa đi thì lần bấm «Lấy số liệu mới» sau lấy lại 16 tháng (khoảng một phút). Chỉ cần "
    "xóa khi phần mềm báo file lưu tạm bị lỗi hay không mở được."
)
MSG_CLEAR_ASK = "Xóa bản lưu tạm số liệu Search Console trên máy này?"
MSG_CLEARED = (
    "Đã xóa bản lưu tạm số liệu Search Console. Bấm «Lấy số liệu mới» để lấy lại (lần đầu 16 "
    "tháng, khoảng một phút)."
)

# Biểu đồ (LC-T120-20): khuôn cố định, chỉ chữ của code; dữ liệu chỉ có ngày và số. Không ``expr``,
# không kênh ``href``, không nguồn dữ liệu ``url``.
_WEEK_X = {"field": "tuan", "type": "ordinal", "title": "Tuần (tới hết ngày)", "sort": None}
_WEEK_TIP = {"field": "tuan", "type": "ordinal", "title": "Tuần tới hết ngày"}
CLICK_CHART = {
    "mark": {"type": "bar"},
    "encoding": {
        "x": _WEEK_X,
        "y": {"field": "click", "type": "quantitative", "title": "Click mỗi tuần"},
        "tooltip": [_WEEK_TIP, {"field": "click", "type": "quantitative", "title": "Click"}],
    },
}
POSITION_CHART = {
    "mark": {"type": "line", "point": True},
    "encoding": {
        "x": _WEEK_X,
        "y": {
            "field": "vi_tri",
            "type": "quantitative",
            "title": "Vị trí trung bình (lên cao là tốt)",
            "scale": {"reverse": True, "zero": False},
        },
        "tooltip": [_WEEK_TIP, {"field": "vi_tri", "type": "quantitative", "title": "Vị trí"}],
    },
}


@dataclass(frozen=True)
class PageView:
    """Một bài, trang trong kỳ đang xem: số so kỳ trước, nhãn, bảng từ khóa (``None``: chưa có
    từ khóa của kỳ này trong bản lưu tạm)."""

    page: TrackedPage
    comparison: Comparison
    flags: tuple[Flag, ...]
    keywords: KeywordTable | None


# ================================================================ chữ hiện ra (chữ thuần)


def plain(text: object) -> str:
    """Chữ (câu báo, chữ dữ liệu) để đưa vào Markdown: escape, không thành link, định dạng."""
    return escape_markdown("" if text is None else str(text))


def show(kind: str, text: str) -> None:
    {"error": st.error, "warning": st.warning, "info": st.info, "success": st.success}.get(
        kind, st.info
    )(text)


def safe_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Ô chữ của bảng: mở đầu bằng ``=``, ``+``, ``-``, ``@``, tab, CR thì thêm một dấu cách đầu
    (``sync.safe_text``): bảng tải về CSV (nút trên thanh công cụ của ``st.dataframe``) mở bằng
    Excel không thành công thức (LC-T101-1, LC-T120-11). Từ khóa như ``=HYPERLINK(…)`` giữ dấu ``=``
    sau khi làm sạch (Lá Chắn T-123 mục 7)."""
    return [
        {
            name: sync.safe_text(value) if isinstance(value, str) else value
            for name, value in row.items()
        }
        for row in rows
    ]


def ctr_text(stats: PageStats) -> str:
    percent = shown_ctr_percent(stats)
    return NO_NUMBER if percent is None else decimal_text(percent) + "%"


def position_text(stats: PageStats) -> str:
    position = shown_position(stats)
    return NO_NUMBER if position is None else decimal_text(position)


def moment_text(moment: datetime, timezone) -> str:
    """«14:05 03/11/2026» theo múi giờ của app (mốc đã kiểm năm ở bản lưu tạm)."""
    try:
        local = moment.astimezone(timezone)
    except (OverflowError, ValueError):
        local = moment
    return f"{local:%H:%M} {day_text(local.date())}"


# ================================================================ đọc bản lưu tạm (không mạng)


def setup_problem(settings) -> str:
    """Câu báo khi chưa khai báo đủ để lấy số liệu; rỗng: đủ."""
    if not settings.gsc_site_url:
        return MSG_NO_PROPERTY
    if not settings.wordpress_url:
        return MSG_NO_WORDPRESS
    if not settings.google_service_account_file:
        return MSG_NO_KEY_FILE
    return ""


def cache_store(settings) -> SearchCacheStore:
    # Đọc đường dẫn lúc chạy (không lúc import) để test trỏ file sang thư mục tạm.
    return SearchCacheStore(
        path=search_cache.DEFAULT_SEARCH_CACHE_FILE, timezone=settings.timezone_name
    )


def site_store(settings) -> site_index.SiteIndexStore:
    return site_index.SiteIndexStore(
        path=site_index.DEFAULT_SITE_INDEX_FILE, timezone=settings.timezone_name
    )


def _memo() -> dict[str, object] | None:
    """Bản lưu tạm đã đọc của phiên (SL-T125-1): ``key`` (dấu file ``SearchCacheStore.stamp``,
    phạm vi, múi giờ lúc đọc), ``cache``; thêm ``inputs``, ``tracking`` khi đã dựng
    ``build_tracking`` trên đúng bản này. Là ``dict`` thường: Streamlit chạy lại cả file trang mỗi
    lần, lớp khai báo ở đây là lớp mới mỗi lần nên không dùng được ``isinstance``."""
    memo = S.get(CACHE_MEMO_KEY)
    return memo if isinstance(memo, dict) else None


def load_cache(settings) -> tuple[SearchCache | None, str]:
    """Số liệu đã lưu của thuộc tính và website đang khai báo (không gọi mạng). Chưa có file thì
    không mở kho (mở kho là tạo file). Lỗi: ``(None, câu cố định)``.

    Chỉ đọc lại khi file đổi (SL-T125-1): mỗi lần chạy lại trang chỉ lấy dấu file (cỡ, giờ sửa, mã
    file, số đếm thay đổi ở đầu file SQLite), không mở SQLite. Dấu, phạm vi hay múi giờ khác lần
    đọc trước (tab khác vừa ghi, «Lấy số liệu mới», xóa, đổi Cài đặt) thì đọc và kiểm lại đủ như
    T-122 (LC-T120-9). Khóa giữ là dấu lấy **trước** khi đọc: file đổi trong lúc đọc thì lần chạy
    sau dấu đã khác, đọc lại. Không ``st.cache_data``, ``st.cache_resource`` (LC-T120-21): bản giữ
    nằm trong phiên, đổi ngay khi file đổi."""
    if not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists():
        S.pop(CACHE_MEMO_KEY, None)
        return None, ""
    store = cache_store(settings)
    scope = CacheScope(settings.gsc_site_url, settings.wordpress_url)
    stamp = store.stamp()
    key = (stamp, scope, store.timezone)
    memo = _memo()
    if stamp is not None and memo is not None and memo["key"] == key:
        return memo["cache"], ""
    S.pop(CACHE_MEMO_KEY, None)
    try:
        cache = store.load(scope)
    except SearchCacheError as exc:
        return None, str(exc)
    if stamp is not None:
        S[CACHE_MEMO_KEY] = {"key": key, "cache": cache}
    return cache, ""


def tracking_for(
    site: str,
    items: tuple[PublishedItem, ...] | None,
    cache: SearchCache,
    plan_rows: tuple[PlanRow, ...],
) -> SiteTracking:
    """``build_tracking`` của bản lưu tạm ``cache``. Dựng lại chỉ khi bản lưu tạm (theo dấu file),
    địa chỉ website, danh sách bài hay dòng kế hoạch đổi (SL-T125-1, Soi Lỗi gợi ý)."""
    memo = _memo()
    held = memo is not None and memo["cache"] is cache
    inputs = (site, items, plan_rows)
    if held and "tracking" in memo and memo["inputs"] == inputs:
        return memo["tracking"]
    tracking = build_tracking(site, items or (), cache.days, plan_rows)
    if held:
        memo["inputs"], memo["tracking"] = inputs, tracking
    return tracking


def cached_items(settings) -> tuple[PublishedItem, ...] | None:
    """Bài, trang đã đăng từ bản lưu tạm (không gọi mạng); ``None``: chưa có."""
    if not site_index.DEFAULT_SITE_INDEX_FILE.exists():
        return None
    try:
        index = site_store(settings).load(settings.wordpress_url)
    except site_index.SiteIndexError:
        return None
    return None if index is None else index.items


def cached_plan_rows(settings) -> tuple[PlanRow, ...]:
    """Dòng kế hoạch từ bản lưu tạm (không gọi Google), để ghi Mã bài và lọc «chỉ bài trong kế
    hoạch». Chưa khai báo Sheet, chưa tải lần nào: rỗng; chưa có file thì không mở kho."""
    if not settings.google_sheet_id or not plan_cache.DEFAULT_PLAN_CACHE_FILE.exists():
        return ()
    store = plan_cache.PlanCacheStore(
        path=plan_cache.DEFAULT_PLAN_CACHE_FILE, timezone=settings.timezone_name
    )
    try:
        cached = store.load(settings.google_sheet_id)
        if cached is None:
            return ()
        plan = sync.parse_sheet(cached.values, fetched_at=cached.fetched_at, from_cache=True)
    except (plan_cache.PlanCacheError, plan_model.PlanKeyError, ValueError):
        return ()
    return tuple(row.plan for row in plan.rows)


def queries_by_page(rows: Iterable[CachedQuery], site: str) -> dict[PageKey, list[CachedQuery]]:
    """Dòng từ khóa của một khoảng, chia theo khóa trang (như ``keywords.page_queries`` cho từng
    trang, nhưng chỉ dựng khóa mỗi địa chỉ một lần)."""
    keys: dict[str, PageKey | None] = {}
    found: dict[PageKey, list[CachedQuery]] = defaultdict(list)
    for row in rows:
        if row.page not in keys:
            keys[row.page] = page_key(row.page, site)
        key = keys[row.page]
        if key is not None:
            found[key].append(row)
    return found


# ================================================================ lấy số liệu (chỉ khi bấm)


def wordpress_source(settings) -> WordPressClient | None:
    """Client WordPress cho đúng lần bấm (tải lại danh sách bài, hỏi ngày đăng; chỉ đọc)."""
    try:
        return WordPressClient.from_settings(settings)
    except WordPressError:
        return None


def fetch_now(settings) -> None:
    """«🔄 Lấy số liệu mới»: chỉ khi bấm (LC-T120-21). ``refresh`` tự tạo client Search Console
    mới, giữ khóa một lần lấy mỗi tiến trình (tab khác đang lấy: «đang lấy ở tab khác»)."""
    S.pop(CLEAR_ASK_KEY, None)
    with st.spinner(MSG_FETCHING):
        report = tracking_refresh.refresh(
            settings,
            cache_store(settings),
            site_index=site_store(settings),
            wordpress=wordpress_source(settings),
        )
    S[REPORT_KEY] = report


def show_report() -> None:
    """Kết quả lần bấm vừa rồi (hiện một lần): câu chính và các câu phụ, đều là câu cố định."""
    report = S.pop(REPORT_KEY, None)
    if not isinstance(report, tracking_refresh.RefreshReport):
        return
    text = plain(report.message)
    if report.notes:
        text += "\n\n" + "\n".join(f"- {plain(note)}" for note in report.notes)
    show(OUTCOME_KIND.get(report.outcome, "info"), text)


# ================================================================ bản lưu tạm


def _ask_clear() -> None:
    S[CLEAR_ASK_KEY] = True


def _cancel_clear() -> None:
    S.pop(CLEAR_ASK_KEY, None)


def _clear_cache() -> None:
    """Xóa file lưu tạm (Lá Chắn T-122 mục 8.2: lối ra khi file báo lỗi lặp lại) qua
    ``clear_cache`` của lõi: xóa trong cùng khóa với «Lấy số liệu mới»; tab khác đang lấy thì không
    xóa, báo «đang lấy ở tab khác» (SL-T125-2)."""
    S.pop(CLEAR_ASK_KEY, None)
    S.pop(REPORT_KEY, None)
    # Bản đã đọc trong phiên tự bỏ ở lần chạy sau khi file mất (``load_cache``); bị từ chối thì giữ.
    result = tracking_refresh.clear_cache(
        SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE)
    )
    if result.ok:
        S[FLASH_KEY] = ("success", MSG_CLEARED)
    else:
        S[FLASH_KEY] = ("warning" if result.busy else "error", result.message)


def show_flash() -> None:
    flash = S.pop(FLASH_KEY, None)
    if flash:
        kind, text = flash
        show(kind, plain(text))


def clear_panel(*, expanded: bool = False) -> None:
    with st.expander("🧹 Bản lưu tạm số liệu trên máy", expanded=expanded):
        st.caption(MSG_CACHE_NOTE)
        if not S.get(CLEAR_ASK_KEY):
            st.button("Xóa bản lưu tạm", key="trk-clear", on_click=_ask_clear)
            return
        st.warning(MSG_CLEAR_ASK)
        yes, no, _ = st.columns([1, 1, 3])
        yes.button("Xóa", key="trk-clear-yes", type="primary", on_click=_clear_cache)
        no.button("Thôi", key="trk-clear-no", on_click=_cancel_clear)


# ================================================================ khoảng ngày


def custom_range(available: Period) -> Period:
    """Hai ô ngày trong phần số liệu đã có (mặc định 28 ngày cuối)."""
    start_default = max(last_days(available.end, DEFAULT_DAYS).start, available.start)
    for key, value in ((FROM_KEY, start_default), (TO_KEY, available.end)):
        chosen = S.get(key)
        if type(chosen) is not date or not available.start <= chosen <= available.end:
            S[key] = value
    first, second, _ = st.columns([1, 1, 2])
    start = first.date_input(
        "Từ ngày",
        key=FROM_KEY,
        min_value=available.start,
        max_value=available.end,
        format="DD/MM/YYYY",
    )
    end = second.date_input(
        "Tới ngày",
        key=TO_KEY,
        min_value=available.start,
        max_value=available.end,
        format="DD/MM/YYYY",
    )
    return custom_period(start, end, available=available)


def choose_periods(cache: SearchCache, *, has_plan: bool) -> tuple[Period, Period | None] | None:
    """Ô chọn khoảng ngày, kỳ so sánh, lọc kế hoạch. ``None``: khoảng chưa dùng được (đã báo)."""
    assert cache.covered_start is not None and cache.final_end is not None
    available = Period(cache.covered_start, cache.final_end)
    if S.get(RANGE_KEY) not in RANGE_LABELS:
        S[RANGE_KEY] = DEFAULT_RANGE
    if S.get(COMPARE_KEY) not in COMPARE_LABELS:
        S[COMPARE_KEY] = COMPARE_LABELS[0]
    if not has_plan:
        S[PLAN_ONLY_KEY] = False  # chưa có kế hoạch trên máy: không lọc (ô bị khóa)
    left, middle, right = st.columns([2.2, 1.3, 1.5], vertical_alignment="bottom")
    label = left.segmented_control("Khoảng", RANGE_LABELS, key=RANGE_KEY, required=True)
    compared = middle.selectbox("So với", COMPARE_LABELS, key=COMPARE_KEY)
    right.checkbox(
        "Chỉ bài trong kế hoạch",
        key=PLAN_ONLY_KEY,
        disabled=not has_plan,
        help=None if has_plan else "Chưa có kế hoạch lưu trên máy: mở trang Kế hoạch để tải.",
    )
    try:
        if label == CUSTOM:
            current = custom_range(available)
        else:
            current = last_days(available.end, RANGE_DAYS.get(label, DEFAULT_DAYS))
    except PeriodError as exc:
        st.error(plain(exc))
        return None
    if not current.inside(available):
        first, last = day_text(available.start), day_text(available.end)
        st.warning(plain(MSG_RANGE_SHORT.format(first=first, last=last, period=current.text)))
        return None
    try:
        previous = (
            previous_period(current) if compared == COMPARE_LABELS[0] else year_before(current)
        )
    except PeriodError:
        previous = None
    if previous is not None and not previous.inside(available):
        st.caption(plain(MSG_COMPARE_MISSING.format(period=previous.text)))
        previous = None
    return current, previous


# ================================================================ số liệu từng bài


def page_views(
    pages: Iterable[TrackedPage],
    cache: SearchCache,
    current: Period,
    previous: Period | None,
    site: str,
) -> list[PageView]:
    """Số kỳ đang xem so kỳ so sánh, nhãn, bảng từ khóa của từng bài, trang đã đăng."""
    queries_now = queries_before = None
    if cache.has_range(current.start, current.end):
        queries_now = queries_by_page(cache.queries_for(current.start, current.end), site)
        if previous is not None and cache.has_range(previous.start, previous.end):
            queries_before = queries_by_page(cache.queries_for(previous.start, previous.end), site)
    views: list[PageView] = []
    for page in pages:
        now = aggregate(page.days, current)
        before = aggregate(page.days, previous) if previous is not None else None
        comparison = compare(now, before)
        table = None
        if queries_now is not None:
            table = keyword_table(
                queries_now.get(page.key, ()),
                None if queries_before is None else queries_before.get(page.key, ()),
                main_keyword=page.plan.keyword if page.plan is not None else "",
            )
        published = None
        if page.item is not None and page.kind == "post":
            published = cache.post_dates.get(page.item.id)
        flags = page_flags(page, comparison, end=current.end, published=published, keywords=table)
        views.append(PageView(page, comparison, flags, table))
    return views


def delta_style(sign: float | None) -> dict[str, str]:
    """Màu và mũi tên của chênh lệch theo dấu (dương là tốt); 0 hay không có: xám, không mũi tên."""
    if not sign:
        return {"delta_color": "gray", "delta_arrow": "off"}
    return {
        "delta_color": "green" if sign > 0 else "red",
        "delta_arrow": "up" if sign > 0 else "down",
    }


def count_metric(column, label: str, now: int, before: int | None) -> None:
    if before is None:
        column.metric(label, number_text(now))
        return
    column.metric(label, number_text(now), change_text(now, before), **delta_style(now - before))


def metrics_row(now: PageStats, before: PageStats | None) -> None:
    """Tổng toàn website: click, hiển thị, CTR, vị trí trung bình, so kỳ trước (thiết kế 1.5)."""
    comparison = compare(now, before)
    clicks, shows, ctr, position = st.columns(4)
    count_metric(clicks, "Lượt click", now.clicks, None if before is None else before.clicks)
    count_metric(
        shows, "Lượt hiển thị", now.impressions, None if before is None else before.impressions
    )
    ctr_delta = ctr_change_text(comparison)
    if ctr_delta in ("", LOW_DATA_TEXT) or before is None:
        ctr.metric("CTR", ctr_text(now))
    else:
        sign = (shown_ctr_percent(now) or 0.0) - (shown_ctr_percent(before) or 0.0)
        ctr.metric("CTR", ctr_text(now), ctr_delta, **delta_style(round_half_up(sign)))
    rank = rank_change_text(comparison)
    shown_before = shown_position(before) if before is not None else None
    shown_now = shown_position(now)
    if rank in ("", LOW_DATA_TEXT) or shown_before is None or shown_now is None:
        position.metric("Vị trí trung bình", position_text(now), help="Số nhỏ là đứng cao.")
    else:
        gain = shown_before - shown_now  # dương là lên hạng (số nhỏ là đứng cao)
        position.metric(
            "Vị trí trung bình",
            position_text(now),
            rank,
            help="Số nhỏ là đứng cao.",
            **delta_style(round_half_up(gain)),
        )
    if before is not None and comparison.low_data:
        st.caption(MSG_LOW_DATA_NOTE)


def page_rows(views: Iterable[PageView]) -> list[dict[str, object]]:
    """Bảng từng bài (thiết kế 4.1): chữ thuần, số viết kiểu Việt Nam, xếp theo click."""
    ordered = sorted(
        views,
        key=lambda view: (
            -view.comparison.current.clicks,
            -view.comparison.current.impressions,
            view.page.label,
        ),
    )
    rows: list[dict[str, object]] = []
    for view in ordered:
        now, before = view.comparison.current, view.comparison.previous
        rows.append(
            {
                "Bài / trang": view.page.label,
                "Loại": KIND_TEXT.get(view.page.kind, ""),
                "Mã KH": view.page.plan.key if view.page.plan is not None else "",
                "Click": number_text(now.clicks),
                "± click": change_text(now.clicks, before.clicks if before else None),
                "Hiển thị": number_text(now.impressions),
                "± hiển thị": change_text(now.impressions, before.impressions if before else None),
                "CTR": ctr_text(now),
                "± CTR": ctr_change_text(view.comparison),
                "Vị trí": position_text(now),
                "± vị trí": rank_change_text(view.comparison),
                "Nhãn": " · ".join(flag.label for flag in view.flags),
            }
        )
    return rows


def other_rows(pages: Iterable[TrackedPage], current: Period) -> list[dict[str, object]]:
    """«Trang khác trên website» có lượt hiển thị trong kỳ: đường dẫn đã làm sạch (chữ thuần, không
    bấm được; LC-T120-19), nhiều click trước."""
    rows = []
    for page in pages:
        stats = aggregate(page.days, current)
        if stats.impressions:
            rows.append((stats, page.label))
    rows.sort(key=lambda entry: (-entry[0].clicks, -entry[0].impressions, entry[1]))
    return [
        {
            "Đường dẫn": label,
            "Click": number_text(stats.clicks),
            "Hiển thị": number_text(stats.impressions),
            "CTR": ctr_text(stats),
            "Vị trí": position_text(stats),
        }
        for stats, label in rows
    ]


# ================================================================ chi tiết một bài


def chart_data(page: TrackedPage, current: Period) -> list[dict[str, object]]:
    """Số từng tuần cho biểu đồ: chỉ ngày (code định dạng) và số (LC-T120-20)."""
    return [
        {
            "tuan": week.end.strftime("%d/%m/%Y"),
            "click": stats.clicks,
            "vi_tri": shown_position(stats),
        }
        for week, stats in weekly(page.days, current)
    ]


def keyword_rows(table: KeywordTable, limit: int) -> list[dict[str, object]]:
    rows = []
    for group in table.groups[:limit]:
        notes = []
        if group.is_main:
            notes.append(MAIN_KEYWORD_TEXT)
        if group.is_new:
            notes.append(NEW_KEYWORD_TEXT)
        if len(group.variants) > 1:
            notes.append(f"gộp {len(group.variants)} cách gõ")
        # Chênh vị trí từng từ khóa: không áp luật «ít dữ liệu» của trang (thiết kế 1.7).
        change = rank_change_text(Comparison(group.current, group.previous))
        rows.append(
            {
                "Từ khóa": group.text,
                "Click": number_text(group.current.clicks),
                "Hiển thị": number_text(group.current.impressions),
                "CTR": ctr_text(group.current),
                "Vị trí": position_text(group.current),
                "± vị trí": change,
                "Ghi chú": ", ".join(notes),
            }
        )
    return rows


def variant_rows(table: KeywordTable, limit: int) -> list[dict[str, object]]:
    return [
        {
            "Từ khóa (đã gộp)": group.text,
            "Cách gõ": variant.text,
            "Click": number_text(variant.stats.clicks),
            "Hiển thị": number_text(variant.stats.impressions),
            "Vị trí": position_text(variant.stats),
        }
        for group in table.groups[:limit]
        if len(group.variants) > 1
        for variant in group.variants
    ]


def _more_keywords() -> None:
    S[KEYWORD_LIMIT_KEY] = int(S.get(KEYWORD_LIMIT_KEY, DEFAULT_ROWS)) + DEFAULT_ROWS


def _reset_keyword_limit() -> None:
    S.pop(KEYWORD_LIMIT_KEY, None)


def keyword_panel(view: PageView, current: Period) -> None:
    """Bảng từ khóa của bài trong kỳ đang xem (thiết kế 1.7): 50 dòng đầu, xem thêm, cách gõ."""
    st.markdown(f"**Từ khóa trên Google ({plain(current.text)})**")
    table = view.keywords
    if table is None:
        st.caption(MSG_NO_KEYWORDS)
        return
    limit = max(DEFAULT_ROWS, int(S.get(KEYWORD_LIMIT_KEY, DEFAULT_ROWS)))
    rows = keyword_rows(table, limit)
    if rows:
        st.dataframe(safe_rows(rows), hide_index=True, width="stretch")
    else:
        st.caption(MSG_NO_KEYWORD_ROWS)
    if len(table.groups) > limit:
        rest = len(table.groups) - limit
        st.button(
            f"Xem thêm {number_text(min(rest, DEFAULT_ROWS))} từ khóa",
            key="trk-more-keywords",
            on_click=_more_keywords,
        )
    variants = variant_rows(table, limit)
    if variants and st.toggle("Xem từng cách gõ của từ khóa đã gộp", key=VARIANTS_KEY):
        st.dataframe(safe_rows(variants), hide_index=True, width="stretch")
    st.caption(HIDDEN_QUERIES_NOTE)
    if table.skipped:
        st.caption(MSG_KEYWORDS_SKIPPED.format(count=number_text(table.skipped)))
    plan_box(table)


def plan_box(table: KeywordTable) -> None:
    """«➕ Đưa vào kế hoạch» (T-127, câu 7 = B; LC-T120-24): ô chọn chỉ có từ khóa qua bộ lọc chặt
    ``propose.google_keyword`` (hiện nguyên văn, chữ thuần), tối đa ``MAX_GOOGLE_KEYWORDS``. Bấm
    thì chuyển danh sách sang trang Kế hoạch; trang đó dựng đề xuất «Thêm» chờ duyệt trên đúng kế
    hoạch hiện tại (lọc lại lần nữa). Không AI, không ghi Sheet ở bước này (LC-T120-13)."""
    allowed = [group.text for group in table.groups if propose.google_keyword(group.text)]
    left_out = len(table.groups) - len(allowed)
    if not allowed:
        st.caption(MSG_PLAN_NONE)
        return
    picked = st.multiselect(
        MSG_PLAN_PICK, allowed, key=PLAN_PICK_KEY, max_selections=propose.MAX_GOOGLE_KEYWORDS
    )
    if left_out:
        st.caption(MSG_PLAN_LEFT_OUT.format(count=number_text(left_out)))
    if st.button("➕ Đưa vào kế hoạch", key="trk-to-plan", disabled=not picked, help=MSG_PLAN_HELP):
        S[GOOGLE_HANDOFF_KEY] = tuple(picked[: propose.MAX_GOOGLE_KEYWORDS])
        st.switch_page("views/plan.py")


def detail_panel(views: list[PageView], current: Period) -> None:
    """Chi tiết một bài, trang: nhãn kèm lý do, gợi ý; biểu đồ tuần; từ khóa."""
    st.markdown("#### Chi tiết một bài, trang")
    by_id = {view.page.item.id: view for view in views if view.page.item is not None}
    if not by_id:
        return
    if S.get(PAGE_KEY) not in by_id:
        S.pop(PAGE_KEY, None)
    chosen = st.selectbox(
        "Bài, trang",
        list(by_id),
        format_func=lambda post_id: by_id[post_id].page.label,
        key=PAGE_KEY,
        on_change=_reset_keyword_limit,
    )
    view = by_id.get(chosen)
    if view is None:
        return
    # Tên bài nằm ngoài biểu đồ, dạng chữ thuần (LC-T120-20).
    st.markdown(f"**{plain(view.page.label)}** · {KIND_TEXT.get(view.page.kind, '')}")
    for flag in view.flags:
        st.markdown(f"{plain(flag.label)}: {plain(flag.reason)}")
        if flag.hint:
            st.caption(plain(flag.hint))
    data = chart_data(view.page, current)
    if data:
        clicks, positions = st.columns(2)
        with clicks:
            st.vega_lite_chart(data, CLICK_CHART, width="stretch")
        with positions:
            st.vega_lite_chart(data, POSITION_CHART, width="stretch")
    else:
        st.caption(MSG_SHORT_PERIOD)
    keyword_panel(view, current)


# ================================================================ trang


def notes_line(tracking: SiteTracking, items: tuple[PublishedItem, ...] | None) -> None:
    if items is None:
        st.info(MSG_NO_INDEX)
    if tracking.skipped_items:
        st.caption(plain(MSG_SKIPPED_ITEMS.format(count=number_text(tracking.skipped_items))))
    if tracking.skipped_rows:
        st.caption(plain(MSG_SKIPPED_ROWS.format(count=number_text(tracking.skipped_rows))))
    unmatched = sum(1 for match in tracking.plan if match.status in UNMATCHED_PLAN)
    if unmatched:
        st.caption(plain(MSG_UNMATCHED_PLAN.format(count=number_text(unmatched))))


def status_line(cache: SearchCache | None, settings) -> None:
    """Mốc số liệu: «Số liệu tới hết ngày … · lấy lúc …», gợi ý lấy số liệu mới (không gọi mạng)."""
    parts = []
    if cache is not None and cache.final_end is not None:
        parts.append(f"Số liệu tới hết ngày {day_text(cache.final_end)} (ngày theo giờ Google)")
    if cache is not None and cache.fetched_at is not None:
        parts.append(f"lấy lúc {moment_text(cache.fetched_at, settings.timezone)}")
    if parts:
        st.caption(plain(" · ".join(parts)))
    hint = tracking_refresh.refresh_hint(cache)
    if hint:
        st.info(plain(hint))


def pages_section(views: list[PageView]) -> list[PageView]:
    """Dòng «Cần chú ý», lọc theo nhãn, bảng từng bài. Trả các dòng đang hiện."""
    attention = attention_text(attention_counts(view.flags for view in views))
    if attention:
        st.markdown(f"**{plain(attention)}**")
    if S.get(FLAG_KEY) not in FLAG_OPTIONS:
        S[FLAG_KEY] = ALL_FLAGS
    left, _ = st.columns([1.3, 3])
    chosen = left.selectbox("Lọc theo nhãn", FLAG_OPTIONS, format_func=FLAG_TEXT.get, key=FLAG_KEY)
    if S.get(PLAN_ONLY_KEY):
        views = [view for view in views if view.page.plan is not None]
    if chosen != ALL_FLAGS:
        views = [view for view in views if any(flag.kind == chosen for flag in view.flags)]
    if not views:
        st.caption(MSG_NOTHING_SHOWN)
        return views
    st.dataframe(safe_rows(page_rows(views)), hide_index=True, width="stretch")
    st.caption(MSG_TABLE_ORDER)
    if any(flag.kind == FlagKind.NO_IMPRESSIONS for view in views for flag in view.flags):
        st.caption(MSG_INDEXING)
    return views


def render() -> None:
    settings = load_settings()
    head, action = st.columns([4, 1.4], vertical_alignment="bottom")
    with head:
        ui.page_header("Theo dõi trên Google", MSG_SUBTITLE)
    problem = setup_problem(settings)
    if action.button(
        "🔄 Lấy số liệu mới",
        key="trk-fetch",
        type="primary",
        width="stretch",
        disabled=bool(problem),
        help=MSG_FETCH_HELP,
    ):
        fetch_now(settings)
    show_report()
    show_flash()
    if problem:
        st.info(plain(problem))
        st.page_link("views/settings.py", label="Mở Cài đặt", icon="⚙️")
        return
    cache, error = load_cache(settings)
    if error:
        st.error(plain(error))
        clear_panel(expanded=True)
        return
    status_line(cache, settings)
    if cache is not None and cache.fetched_at is not None and cache.final_end is None:
        st.info(MSG_NO_FINAL)
    if cache is None or cache.final_end is None:
        clear_panel()
        return
    items = cached_items(settings)
    plan_rows = cached_plan_rows(settings)
    periods = choose_periods(cache, has_plan=bool(plan_rows))
    if periods is None:
        clear_panel()
        return
    current, previous = periods
    site = settings.wordpress_url
    tracking = tracking_for(site, items, cache, plan_rows)
    total_now = site_totals((*tracking.pages, *tracking.others), current)
    total_before = None
    if previous is not None:
        total_before = site_totals((*tracking.pages, *tracking.others), previous)
    metrics_row(total_now, total_before)
    st.caption(MSG_TOTALS_NOTE)
    notes_line(tracking, items)
    views = page_views(tracking.pages, cache, current, previous, site)
    shown = pages_section(views)
    if shown:
        detail_panel(shown, current)
    others = other_rows(tracking.others, current)
    title = f"Trang khác trên website (trang chủ, chuyên mục, địa chỉ cũ…): {len(others)} trang"
    with st.expander(title):
        st.caption(MSG_OTHERS_NOTE)
        if others:
            st.dataframe(safe_rows(others), hide_index=True, width="stretch")
    clear_panel()


render()

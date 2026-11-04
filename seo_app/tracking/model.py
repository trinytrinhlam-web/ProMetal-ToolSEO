"""Kiểu dữ liệu của phần theo dõi bài (T-123; thiết kế T-120 mục 1.4–1.7, 3.1).

- Khuôn số liệu Search Console đọc từ cache (thiết kế 3.1), khai báo bằng ``Protocol``:
  ``CachedDayLike`` (một ngày × một trang, khuôn Q1) và ``CachedQueryLike`` (một trang × một từ
  khóa trong một khoảng, khuôn Q2). Cache (T-122) định nghĩa hai dataclass ``CachedDay``,
  ``CachedQuery`` có **đúng các tên trường này**; gói tính toán chỉ dựa vào tên trường nên hai phiếu
  không phải chờ nhau. Trường khai báo dạng thuộc tính chỉ đọc để dataclass ``frozen`` khớp khuôn.
- Kết quả tính toán: ``PageKey``, ``DayTotal``, ``PageStats``, ``Comparison``, ``Flag``,
  ``TrackedPage``, ``PlanMatch``, ``SiteTracking``, ``KeywordGroup``, ``KeywordTable``.

Chữ trong các kết quả là chữ thuần (đã làm sạch, **chưa escape**): giao diện hiện bằng ô bảng
(``st.dataframe(safe_rows(…))``), ``st.text`` hay ``escape_markdown``, không bao giờ thành link
(LC-T120-11, LC-T120-19).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # chỉ để ghi kiểu
    from seo_app.plan.model import PlanRow
    from seo_app.wordpress.client import PublishedItem


# ------------------------------------------------------------------- khuôn dòng cache (3.1)


class DayNumbers(Protocol):
    """Số của một trang trong một ngày: đủ để cộng dồn theo khoảng ngày."""

    @property
    def day(self) -> date: ...  # ngày theo giờ Google (PT)

    @property
    def clicks(self) -> int: ...  # 0 ≤ clicks ≤ impressions

    @property
    def impressions(self) -> int: ...  # 1 … 10**9

    @property
    def position_sum(self) -> float: ...  # vị trí × lượt hiển thị (≥ impressions)

    @property
    def final(self) -> bool: ...  # False: số tạm (ngày ≥ first_incomplete_date)


class CachedDayLike(DayNumbers, Protocol):
    """Một ngày × một trang (``CachedDay`` của cache T-122, khuôn Q1)."""

    @property
    def page(self) -> str: ...  # địa chỉ đã kiểm: https, đúng website, đã bỏ "#…"


class CachedQueryLike(Protocol):
    """Một trang × một từ khóa trong khoảng ``start``–``end`` (``CachedQuery`` của T-122, khuôn
    Q2). Khoảng là đúng khoảng đã hỏi Google (kỳ đang xem hay kỳ so sánh)."""

    @property
    def start(self) -> date: ...

    @property
    def end(self) -> date: ...

    @property
    def page(self) -> str: ...

    @property
    def query(self) -> str: ...  # đã clean_text, ≤ 200 ký tự

    @property
    def clicks(self) -> int: ...

    @property
    def impressions(self) -> int: ...

    @property
    def position_sum(self) -> float: ...


# ------------------------------------------------------------------------------ kết quả


@dataclass(frozen=True)
class PageKey:
    """Khóa so khớp một trang (thiết kế 1.4): đường dẫn sau tên máy (và sau đường dẫn gốc của
    website) đã giải mã ``%``, chuẩn NFC, bỏ một dấu «/» cuối, trang chủ là ``"/"``; giữ nguyên
    chữ hoa, chữ thường. ``query``: phần sau «?» đã giải mã, ``None`` khi địa chỉ không có «?».
    Trang có ``query`` không bao giờ được gán cho bài (``?s=``, ``?p=``…)."""

    path: str
    query: str | None = None

    def __str__(self) -> str:
        return self.path if self.query is None else f"{self.path}?{self.query}"


@dataclass(frozen=True)
class DayTotal:
    """Số một ngày của một trang trong bảng theo dõi: các dòng cùng khóa trang trong cùng ngày
    (chỉ khác ``#…``, dấu «/» cuối, cách viết ``%``) đã cộng dồn (thiết kế 1.4 bước 2)."""

    day: date
    clicks: int
    impressions: int
    position_sum: float
    final: bool


@dataclass(frozen=True)
class PageStats:
    """Số của một trang (hay một từ khóa, cả website) trong một khoảng ngày (thiết kế 1.5)."""

    clicks: int = 0
    impressions: int = 0
    position_sum: float = 0.0  # Σ(vị trí × lượt hiển thị)

    @property
    def ctr(self) -> float | None:
        """Tỉ lệ click (0 … 1); ``None`` khi không có lượt hiển thị."""
        return self.clicks / self.impressions if self.impressions else None

    @property
    def position(self) -> float | None:
        """Vị trí trung bình theo lượt hiển thị (số nhỏ là đứng cao); ``None`` khi không có lượt
        hiển thị."""
        return self.position_sum / self.impressions if self.impressions else None

    def __add__(self, other: PageStats) -> PageStats:
        return PageStats(
            self.clicks + other.clicks,
            self.impressions + other.impressions,
            self.position_sum + other.position_sum,
        )


@dataclass(frozen=True)
class Comparison:
    """Kỳ đang xem so với kỳ so sánh (thiết kế 1.5), dựng bằng ``stats.compare``.

    ``previous`` ``None``: không có kỳ so sánh (cache chưa phủ kỳ đó). ``low_data``: có kỳ so sánh
    nhưng một trong hai kỳ dưới ``stats.LOW_DATA_IMPRESSIONS`` lượt hiển thị, nên không so CTR, vị
    trí (giao diện ghi «ít dữ liệu»)."""

    current: PageStats
    previous: PageStats | None
    low_data: bool = False

    @property
    def clicks_delta(self) -> int | None:
        return None if self.previous is None else self.current.clicks - self.previous.clicks

    @property
    def impressions_delta(self) -> int | None:
        if self.previous is None:
            return None
        return self.current.impressions - self.previous.impressions

    @property
    def ctr_delta(self) -> float | None:
        """Chênh CTR (tỉ lệ 0 … 1; ``0.003`` là 0,3 điểm phần trăm)."""
        if self.previous is None or self.low_data:
            return None
        now, before = self.current.ctr, self.previous.ctr
        return None if now is None or before is None else now - before

    @property
    def rank_gain(self) -> float | None:
        """Số bậc lên hạng: vị trí kỳ trước trừ vị trí kỳ này (dương là lên, âm là xuống)."""
        if self.previous is None or self.low_data:
            return None
        now, before = self.current.position, self.previous.position
        return None if now is None or before is None else before - now


class FlagKind(StrEnum):
    """Các nhãn đánh dấu bài (thiết kế 1.6), theo thứ tự hiện."""

    RANK_DROP = "rank_drop"
    LOST_CLICKS = "lost_clicks"
    NO_IMPRESSIONS = "no_impressions"
    LOW_CTR = "low_ctr"
    MAIN_KEYWORD = "main_keyword"
    NEW = "new"
    RANK_RISE = "rank_rise"


@dataclass(frozen=True)
class Flag:
    """Một nhãn của bài: ``label`` và ``hint`` là chữ cố định; ``reason`` do code viết, chỉ chèn
    số và ngày (không chèn chữ của Google hay WordPress)."""

    kind: FlagKind
    label: str
    reason: str
    hint: str


class MatchStatus(StrEnum):
    """Kết quả nối một dòng kế hoạch với bài trên website (thiết kế 1.4)."""

    BY_ID = "by_id"  # khớp theo «Mã bài WordPress»
    BY_SLUG = "by_slug"  # dòng «Đã đăng» chưa có mã: khớp slug với đúng một bài
    NOT_LIVE = "not_live"  # Chưa viết, Đang viết, Đã gửi nháp, Đã hẹn giờ: chưa lên website
    NOT_FOUND = "not_found"  # «Đã đăng» mà không thấy bài trong danh sách đã đăng
    AMBIGUOUS = "ambiguous"  # slug trùng nhiều bài: không đoán
    DUPLICATE = "duplicate"  # nhiều dòng kế hoạch cùng một bài: không đoán
    DROPPED = "dropped"  # dòng «Bỏ»: không theo dõi


@dataclass(frozen=True)
class PlanMatch:
    """Một dòng kế hoạch kèm kết quả nối; ``item`` chỉ có khi khớp (``BY_ID``, ``BY_SLUG``)."""

    row: PlanRow
    status: MatchStatus
    item: PublishedItem | None = None


@dataclass(frozen=True)
class TrackedPage:
    """Một trang trên website trong bảng theo dõi.

    - ``item``: bài hay trang trong danh sách đã đăng (``SiteIndex``); ``None``: «Trang khác trên
      website» (trang chủ không phải trang tĩnh, chuyên mục, thẻ, địa chỉ cũ trước khi đổi slug,
      trang tìm kiếm…).
    - ``label``: tiêu đề bài, trang (chữ WordPress) hay đường dẫn đã làm sạch
      (``match.page_label``).
    - ``plan``: dòng kế hoạch nối với bài (chỉ bài, chỉ khi khớp chắc chắn).
    - ``days``: số từng ngày, cũ tới mới; rỗng khi Search Console chưa có lượt hiển thị nào."""

    key: PageKey
    label: str
    item: PublishedItem | None
    plan: PlanRow | None
    days: tuple[DayTotal, ...]

    @property
    def kind(self) -> str:
        """``"post"``, ``"page"`` hay ``"other"`` («Trang khác»)."""
        return self.item.type if self.item is not None else "other"


@dataclass(frozen=True)
class SiteTracking:
    """Số liệu đã khớp với website và kế hoạch (``match.build_tracking``)."""

    pages: tuple[TrackedPage, ...]  # mọi bài, trang đã đăng, kể cả chưa có số liệu
    others: tuple[TrackedPage, ...]  # «Trang khác trên website»: có số liệu, không khớp bài nào
    plan: tuple[PlanMatch, ...]  # mọi dòng kế hoạch, đúng thứ tự đưa vào
    skipped_rows: int = 0  # dòng số liệu bị bỏ («dòng lạ»): ngoài website, sai dạng
    skipped_items: int = 0  # bài, trang không dựng được khóa (địa chỉ ngoài website, có «?», trùng)


@dataclass(frozen=True)
class KeywordVariant:
    """Một cách gõ của từ khóa (chữ đã làm sạch) và số của nó."""

    text: str
    stats: PageStats


@dataclass(frozen=True)
class KeywordGroup:
    """Một dòng của bảng từ khóa: các cách gõ cùng ``fold_key`` gộp lại (thiết kế 1.7).

    - ``text``: cách gõ có nhiều lượt hiển thị nhất; ``variants``: từng cách gõ, nhiều lượt hiển
      thị trước.
    - ``previous``: số của từ khóa ở kỳ so sánh; ``None`` khi chưa lấy từ khóa kỳ đó hay kỳ đó
      không có từ khóa này.
    - ``is_main``: trùng từ khóa chính của dòng kế hoạch. ``is_new``: có ở kỳ này, không có ở kỳ
      trước (chỉ khi đã lấy từ khóa kỳ trước)."""

    key: str
    text: str
    current: PageStats
    previous: PageStats | None
    variants: tuple[KeywordVariant, ...]
    is_main: bool = False
    is_new: bool = False

    @property
    def rank_gain(self) -> float | None:
        """Số bậc lên hạng so kỳ trước (dương là lên); ``None`` khi kỳ trước không có."""
        if self.previous is None:
            return None
        now, before = self.current.position, self.previous.position
        return None if now is None or before is None else before - now


@dataclass(frozen=True)
class KeywordTable:
    """Bảng từ khóa của một trang trong một kỳ (``keywords.keyword_table``)."""

    groups: tuple[KeywordGroup, ...]  # nhiều click trước
    skipped: int = 0  # dòng bị bỏ: số sai dạng, chữ rỗng sau khi làm sạch
    has_previous: bool = False  # đã có từ khóa của kỳ so sánh (để biết «từ khóa mới»)

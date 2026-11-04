"""Nhãn đánh dấu bài (T-123; thiết kế T-120 mục 1.6).

Nhãn do code đặt; câu giải thích do code viết sẵn, chỉ chèn số và ngày (không chèn chữ của Google
hay WordPress); gợi ý là chữ cố định. Ngưỡng là các hằng có tên bên dưới, theo mặc định ở câu hỏi 5
(khuyến nghị A; chủ dự án chưa trả lời): đổi ngưỡng chỉ là sửa hằng, không đổi cách tính.

- Chỉ đặt nhãn cho bài, trang trong danh sách đã đăng, không cho «Trang khác».
- So ngưỡng vị trí, CTR trên số đã làm tròn như khi hiện (``stats.shown_position``,
  ``stats.shown_ctr_percent``), để nhãn khớp số người dùng thấy.
- Gọi khi cache đã phủ kỳ đang xem (và kỳ so sánh, nếu có): ngày không có dòng nào được hiểu là 0
  lượt hiển thị.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date

from seo_app.tracking.keywords import has_keyword
from seo_app.tracking.model import Comparison, Flag, FlagKind, KeywordTable, PageStats, TrackedPage
from seo_app.tracking.periods import day_text, is_day
from seo_app.tracking.stats import (
    change_text,
    decimal_text,
    number_text,
    round_half_up,
    shown_ctr_percent,
    shown_position,
)

# Câu hỏi 5, khuyến nghị A (mặc định của thiết kế). Đổi số ở đây, không phải sửa cách tính.
RANK_MIN_IMPRESSIONS = 30  # tụt/lên hạng: cả hai kỳ có ít nhất chừng này lượt hiển thị
RANK_CHANGE_POSITIONS = 3.0  # … và vị trí trung bình kém đi (tốt lên) ít nhất chừng này bậc
FIRST_PAGE_POSITION = 10.0  # … hoặc rơi khỏi (vào) trang 1: vị trí ≤ 10
CLICK_LOSS_MIN_PREVIOUS = 10  # mất click: kỳ trước có ít nhất chừng này click
CLICK_LOSS_RATIO = 0.5  # … và kỳ này còn không quá một nửa
NEW_POST_DAYS = 14  # bài đăng chưa tới chừng này ngày tính tới ngày cuối kỳ: «mới đăng»
LOW_CTR_MIN_IMPRESSIONS = 200  # nhiều hiển thị, ít click: ít nhất chừng này lượt hiển thị
LOW_CTR_MAX_POSITION = 10.0  # … vị trí trung bình không quá chừng này
LOW_CTR_MAX_PERCENT = 1.0  # … mà CTR dưới chừng này phần trăm
MAIN_KEYWORD_MIN_IMPRESSIONS = 100  # từ khóa chính chưa có: bài có ít nhất chừng này lượt hiển thị

LABELS = {
    FlagKind.RANK_DROP: "🔻 Tụt hạng",
    FlagKind.LOST_CLICKS: "📉 Mất click",
    FlagKind.NO_IMPRESSIONS: "👻 Chưa có lượt hiển thị",
    FlagKind.LOW_CTR: "👀 Nhiều hiển thị, ít click",
    FlagKind.MAIN_KEYWORD: "🎯 Từ khóa chính chưa có",
    FlagKind.NEW: "🌱 Mới đăng",
    FlagKind.RANK_RISE: "🔺 Lên hạng",
}
_CHECK_RANK = (
    "Xem từ khóa nào tụt (bảng từ khóa); kiểm bài còn đúng ý định tìm kiếm, có bài mới của đối thủ."
)
HINTS = {
    FlagKind.RANK_DROP: _CHECK_RANK,
    FlagKind.LOST_CLICKS: _CHECK_RANK + " Kiểm tiêu đề bài có bị đổi.",
    FlagKind.NO_IMPRESSIONS: (
        "Kiểm Google đã lập chỉ mục bài chưa (Search Console → Kiểm tra URL), và đã có link nội bộ "
        "tới bài chưa."
    ),
    FlagKind.LOW_CTR: (
        "Tiêu đề, mô tả SEO có thể chưa hấp dẫn. Sửa trong SiteSEO trên website (phần mềm không "
        "sửa bài đã đăng)."
    ),
    FlagKind.MAIN_KEYWORD: "Bài đang được tìm bằng từ khác: xem bảng từ khóa.",
    FlagKind.NEW: "Chờ thêm: Google cần vài ngày tới vài tuần để đưa bài mới lên kết quả tìm kiếm.",
    FlagKind.RANK_RISE: "",
}
# Nhãn «cần chú ý» ở dòng tóm tắt đầu trang (Mới đăng, Lên hạng chỉ để biết).
ATTENTION = (
    FlagKind.RANK_DROP,
    FlagKind.LOST_CLICKS,
    FlagKind.NO_IMPRESSIONS,
    FlagKind.LOW_CTR,
    FlagKind.MAIN_KEYWORD,
)
ATTENTION_PHRASES = {
    FlagKind.RANK_DROP: "bài tụt hạng",
    FlagKind.LOST_CLICKS: "bài mất click",
    FlagKind.NO_IMPRESSIONS: "bài chưa có lượt hiển thị",
    FlagKind.LOW_CTR: "bài nhiều hiển thị ít click",
    FlagKind.MAIN_KEYWORD: "bài chưa có từ khóa chính",
}
_ORDER = {kind: index for index, kind in enumerate(FlagKind)}


def page_flags(
    page: TrackedPage,
    comparison: Comparison,
    *,
    end: date,
    published: date | None = None,
    keywords: KeywordTable | None = None,
) -> tuple[Flag, ...]:
    """Nhãn của một bài, trang (theo thứ tự ``FlagKind``).

    - ``comparison``: số kỳ đang xem và kỳ so sánh của trang (``stats.compare``).
    - ``end``: ngày cuối kỳ đang xem (E với khoảng 7/28/91 ngày), để tính bài đăng được bao lâu.
    - ``published``: ngày đăng theo giờ PT (``periods.published_day``), chỉ dùng cho bài; ``None``
      khi chưa rõ.
    - ``keywords``: bảng từ khóa của trang **trong kỳ đang xem**; ``None`` khi chưa lấy (khi đó
      không xét «từ khóa chính chưa có»)."""
    if page.item is None:
        return ()
    now, before = comparison.current, comparison.previous
    candidates = [
        _rank(now, before),
        _lost_clicks(now, before),
        _presence(page, now, before, end=end, published=published),
        _low_ctr(now),
        _main_keyword(page, now, keywords),
    ]
    found = [flag for flag in candidates if flag is not None]
    return tuple(sorted(found, key=lambda flag: _ORDER[flag.kind]))


def attention_counts(flag_sets: Iterable[Iterable[Flag]]) -> dict[FlagKind, int]:
    """Số bài có từng nhãn «cần chú ý» (mỗi bài tính một lần cho mỗi nhãn)."""
    counts = dict.fromkeys(ATTENTION, 0)
    for flags in flag_sets:
        for kind in {flag.kind for flag in flags}:
            if kind in counts:
                counts[kind] += 1
    return counts


def attention_text(counts: Mapping[FlagKind, int]) -> str:
    """Dòng tóm tắt đầu trang: «Cần chú ý: 2 bài tụt hạng · 3 bài chưa có lượt hiển thị»;
    chuỗi rỗng khi không có gì cần chú ý."""
    parts = [
        f"{number_text(counts[kind])} {ATTENTION_PHRASES[kind]}"
        for kind in ATTENTION
        if counts.get(kind)
    ]
    return "Cần chú ý: " + " · ".join(parts) if parts else ""


def _flag(kind: FlagKind, reason: str) -> Flag:
    return Flag(kind, LABELS[kind], reason, HINTS[kind])


def _rank(now: PageStats, before: PageStats | None) -> Flag | None:
    """Tụt hạng, lên hạng: cả hai kỳ đủ lượt hiển thị; vị trí đổi ít nhất ``RANK_CHANGE_POSITIONS``
    bậc, hoặc rơi khỏi (vào) trang 1."""
    if before is None or min(now.impressions, before.impressions) < RANK_MIN_IMPRESSIONS:
        return None
    after_position, before_position = shown_position(now), shown_position(before)
    if after_position is None or before_position is None:
        return None
    drop = round_half_up(after_position - before_position)
    left_first_page = before_position <= FIRST_PAGE_POSITION < after_position
    entered_first_page = after_position <= FIRST_PAGE_POSITION < before_position
    positions = (
        f"Vị trí trung bình kỳ trước {decimal_text(before_position)}, kỳ này "
        f"{decimal_text(after_position)}"
    )
    if drop >= RANK_CHANGE_POSITIONS or left_first_page:
        note = "; rơi khỏi trang 1" if left_first_page else ""
        return _flag(FlagKind.RANK_DROP, f"{positions}: xuống {decimal_text(drop)} bậc{note}.")
    if -drop >= RANK_CHANGE_POSITIONS or entered_first_page:
        note = "; vào trang 1" if entered_first_page else ""
        return _flag(FlagKind.RANK_RISE, f"{positions}: lên {decimal_text(-drop)} bậc{note}.")
    return None


def _lost_clicks(now: PageStats, before: PageStats | None) -> Flag | None:
    """Mất click: kỳ trước ít nhất ``CLICK_LOSS_MIN_PREVIOUS`` click, kỳ này còn không quá
    ``CLICK_LOSS_RATIO`` lần kỳ trước."""
    if before is None or before.clicks < CLICK_LOSS_MIN_PREVIOUS:
        return None
    if now.clicks > before.clicks * CLICK_LOSS_RATIO:
        return None
    reason = (
        f"Click kỳ này {number_text(now.clicks)}, kỳ trước {number_text(before.clicks)}: "
        f"{change_text(now.clicks, before.clicks)}."
    )
    return _flag(FlagKind.LOST_CLICKS, reason)


def _presence(
    page: TrackedPage,
    now: PageStats,
    before: PageStats | None,
    *,
    end: date,
    published: date | None,
) -> Flag | None:
    """Mới đăng (bài đăng chưa tới ``NEW_POST_DAYS`` ngày) hay chưa có lượt hiển thị (0 lượt hiển
    thị cả hai kỳ; với bài: đã đăng ít nhất ``NEW_POST_DAYS`` ngày hay chưa rõ ngày đăng)."""
    age = _post_age(page, end, published)
    if age is not None and age[0] < NEW_POST_DAYS:
        days, posted = age
        if days < 0:
            reason = f"Bài đăng ngày {posted}, sau ngày cuối kỳ đang xem."
        else:
            reason = f"Bài đăng ngày {posted} ({days} ngày tính tới {day_text(end)})."
        return _flag(FlagKind.NEW, reason)
    if now.impressions or (before is not None and before.impressions):
        return None
    reason = (
        "0 lượt hiển thị trong kỳ đang xem" if before is None else "0 lượt hiển thị trong cả hai kỳ"
    )
    if age is not None:
        reason += f"; bài đăng ngày {age[1]} ({age[0]} ngày tính tới {day_text(end)})"
    elif page.kind == "post":
        reason += "; chưa rõ ngày đăng"
    return _flag(FlagKind.NO_IMPRESSIONS, reason + ".")


def _post_age(page: TrackedPage, end: date, published: date | None) -> tuple[int, str] | None:
    """(Số ngày từ ngày đăng tới ``end``, ngày đăng viết sẵn) của một bài; ``None`` khi không phải
    bài hay ngày không hợp lệ (kiểm năm trước khi trừ ngày, LC-T120-10)."""
    if page.kind != "post" or published is None or not is_day(published) or not is_day(end):
        return None
    return (end - published).days, day_text(published)


def _low_ctr(now: PageStats) -> Flag | None:
    """Nhiều hiển thị, ít click: nhiều lượt hiển thị, đứng trang 1 mà CTR thấp (kỳ đang xem)."""
    position, ctr = shown_position(now), shown_ctr_percent(now)
    if position is None or ctr is None or now.impressions < LOW_CTR_MIN_IMPRESSIONS:
        return None
    if position > LOW_CTR_MAX_POSITION or ctr >= LOW_CTR_MAX_PERCENT:
        return None
    reason = (
        f"{number_text(now.impressions)} lượt hiển thị, vị trí trung bình "
        f"{decimal_text(position)}, CTR {decimal_text(ctr)}%."
    )
    return _flag(FlagKind.LOW_CTR, reason)


def _main_keyword(page: TrackedPage, now: PageStats, keywords: KeywordTable | None) -> Flag | None:
    """Từ khóa chính chưa có: bài có dòng kế hoạch, đủ lượt hiển thị, đã có bảng từ khóa kỳ này
    mà không dòng nào trùng từ khóa chính (so ``fold_key``)."""
    if page.plan is None or keywords is None or now.impressions < MAIN_KEYWORD_MIN_IMPRESSIONS:
        return None
    if has_keyword(keywords, page.plan.keyword) is not False:
        return None
    reason = (
        f"{number_text(now.impressions)} lượt hiển thị nhưng không từ khóa nào trùng từ khóa chính "
        "của dòng kế hoạch."
    )
    return _flag(FlagKind.MAIN_KEYWORD, reason)

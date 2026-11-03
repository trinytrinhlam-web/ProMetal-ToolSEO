"""Cộng dồn số liệu và so hai kỳ (T-123; thiết kế T-120 mục 1.5).

- Số của một trang trong một kỳ cộng từ các ngày: click = Σ click; hiển thị = Σ lượt hiển thị;
  CTR = click / hiển thị; vị trí trung bình = Σ(vị trí × lượt hiển thị) / Σ lượt hiển thị (trung
  bình theo lượt hiển thị). Search Console tính đúng như vậy là **suy luận** từ định nghĩa; kiểm ở
  lượt thử thật bằng bảng «Trang» của Search Console.
- Chỉ cộng số đã chốt; số tạm không hiện, không tính (câu hỏi 3, khuyến nghị A:
  ``SHOW_PROVISIONAL``). Có hiện số tạm (câu 3 = B) thì vẫn không dùng để so.
- «Ít dữ liệu»: một trong hai kỳ dưới ``LOW_DATA_IMPRESSIONS`` lượt hiển thị thì không so CTR, vị
  trí.
- Tổng toàn website cộng theo từng trang, nên có thể cao hơn chút so với biểu đồ của Search Console
  (tính theo website: một lượt tìm có hai trang của site chỉ tính một lượt hiển thị).
- Số viết kiểu Việt Nam: ``9.800``, ``4,2%``; chênh lệch «+12 (+30%)», «+0,3 điểm», «lên 2,1 bậc».
  Làm tròn kiểu 5 lên (``round_half_up``: 0,25% hiện «0,3%»). Chênh CTR, vị trí tính trên số đã
  làm tròn như khi hiện (1 chữ số thập phân), để chữ khớp số người dùng thấy.

Dòng có số sai dạng (``bool``, số thực ở chỗ số nguyên, ``NaN``, số âm, click lớn hơn lượt hiển thị,
vị trí ngoài 1 … 10.000) không được cộng (``numbers_ok``). Cache và client đã kiểm từng dòng; đây là
lớp chặn thêm để số lạ không lan ra giao diện (LC-T120-5).
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from seo_app.tracking.model import Comparison, DayNumbers, PageStats, TrackedPage
from seo_app.tracking.periods import Period, week_blocks

LOW_DATA_IMPRESSIONS = 30  # mỗi kỳ cần chừng này lượt hiển thị mới so CTR, vị trí
SHOW_PROVISIONAL = False  # câu hỏi 3, khuyến nghị A: không hiện, không tính số tạm
MAX_IMPRESSIONS = 10**9  # một dòng của Google (thiết kế 2.4)
MAX_POSITION = 10_000
DIGITS = 1  # số chữ số thập phân khi hiện vị trí, CTR (phần trăm)
LOW_DATA_TEXT = "ít dữ liệu"


# ------------------------------------------------------------------------- kiểm số một dòng


def numbers_ok(clicks: object, impressions: object, position_sum: object) -> bool:
    """Số của một dòng (hay một ngày đã cộng) dùng được: số nguyên thật (không ``bool``),
    ``0 ≤ click ≤ hiển thị``, hiển thị ≥ 1, ``position_sum`` hữu hạn và vị trí trung bình trong
    1 … ``MAX_POSITION``."""
    if type(clicks) is not int or type(impressions) is not int:
        return False
    if impressions < 1 or not 0 <= clicks <= impressions:
        return False
    if type(position_sum) not in (int, float) or not math.isfinite(position_sum):
        return False
    return impressions <= position_sum <= impressions * MAX_POSITION


def row_numbers_ok(clicks: object, impressions: object, position_sum: object) -> bool:
    """Như ``numbers_ok``, thêm trần lượt hiển thị của một dòng Google (``MAX_IMPRESSIONS``)."""
    if not numbers_ok(clicks, impressions, position_sum):
        return False
    return type(impressions) is int and impressions <= MAX_IMPRESSIONS


# ---------------------------------------------------------------------------- cộng, so kỳ


def aggregate(
    days: Iterable[DayNumbers], period: Period, *, include_provisional: bool = SHOW_PROVISIONAL
) -> PageStats:
    """Cộng số các ngày nằm trong ``period`` (cả hai đầu). Mặc định chỉ số đã chốt
    (``final is True``); dòng có số sai dạng bị bỏ qua."""
    clicks = impressions = 0
    position_sum = 0.0
    for row in days:
        if row.day not in period:
            continue
        if row.final is not True and not include_provisional:
            continue
        if not numbers_ok(row.clicks, row.impressions, row.position_sum):
            continue
        clicks += row.clicks
        impressions += row.impressions
        position_sum += row.position_sum
    return PageStats(clicks, impressions, position_sum)


def compare(current: PageStats, previous: PageStats | None) -> Comparison:
    """So kỳ đang xem với kỳ so sánh (``None``: không có kỳ so sánh)."""
    low = previous is not None and (
        min(current.impressions, previous.impressions) < LOW_DATA_IMPRESSIONS
    )
    return Comparison(current, previous, low)


def site_totals(
    pages: Iterable[TrackedPage], period: Period, *, include_provisional: bool = SHOW_PROVISIONAL
) -> PageStats:
    """Tổng toàn website: cộng theo từng trang (bài, trang và «Trang khác»)."""
    total = PageStats()
    for page in pages:
        total += aggregate(page.days, period, include_provisional=include_provisional)
    return total


def weekly(
    days: Iterable[DayNumbers], period: Period, *, include_provisional: bool = SHOW_PROVISIONAL
) -> tuple[tuple[Period, PageStats], ...]:
    """Số từng tuần của ``period`` (khối 7 ngày kết thúc ở ngày cuối, cũ tới mới; ``week_blocks``)
    cho biểu đồ click và vị trí mỗi tuần (thiết kế 1.7)."""
    rows = tuple(days)
    return tuple(
        (week, aggregate(rows, week, include_provisional=include_provisional))
        for week in week_blocks(period)
    )


# ---------------------------------------------------------------- số viết kiểu Việt Nam


def round_half_up(value: float, digits: int = DIGITS) -> float:
    """Làm tròn kiểu thường dùng, 5 thì lên: ``0.25`` → ``0.3``, ``-1.25`` → ``-1.3`` (``round``
    của Python đưa 5 về số chẵn: ``0.2``). Làm tròn trên chữ số thập phân đúng như số viết ra
    (``repr``), nên ``4.35`` → ``4.4``."""
    if not math.isfinite(value):
        return value
    step = Decimal(1).scaleb(-digits)
    return float(Decimal(repr(value)).quantize(step, rounding=ROUND_HALF_UP))


def number_text(value: int) -> str:
    """Số nguyên kiểu Việt Nam: ``9800`` → ``9.800``."""
    return f"{value:,}".replace(",", ".")


def decimal_text(value: float, digits: int = DIGITS) -> str:
    """Số thập phân kiểu Việt Nam: ``4.25`` → ``4,3``; ``1234.5`` → ``1.234,5``."""
    text = f"{round_half_up(value, digits) + 0.0:,.{digits}f}"  # + 0.0: không ra «-0,0»
    return text.replace(",", " ").replace(".", ",").replace(" ", ".")


def percent_text(ratio: float, digits: int = DIGITS) -> str:
    """Tỉ lệ 0 … 1 thành phần trăm kiểu Việt Nam: ``0.042`` → ``4,2%``."""
    return decimal_text(ratio * 100, digits) + "%"


def shown_position(stats: PageStats) -> float | None:
    """Vị trí trung bình làm tròn như khi hiện (``None``: không có lượt hiển thị)."""
    position = stats.position
    return None if position is None else round_half_up(position)


def shown_ctr_percent(stats: PageStats) -> float | None:
    """CTR theo phần trăm, làm tròn như khi hiện (``None``: không có lượt hiển thị)."""
    ctr = stats.ctr
    return None if ctr is None else round_half_up(ctr * 100)


def signed_number_text(delta: int) -> str:
    """``+12``, ``-1.200``, ``0``."""
    if delta > 0:
        return "+" + number_text(delta)
    if delta < 0:
        return "-" + number_text(-delta)
    return "0"


def signed_decimal_text(value: float, digits: int = DIGITS) -> str:
    """``+0,3``, ``-1,5``, ``0`` (làm tròn trước khi xét dấu)."""
    value = round_half_up(value, digits)
    if value > 0:
        return "+" + decimal_text(value, digits)
    if value < 0:
        return "-" + decimal_text(-value, digits)
    return "0"


def change_text(current: int, previous: int | None) -> str:
    """Chênh số đếm (click, lượt hiển thị) so kỳ trước: ``+12 (+30%)``. Kỳ trước bằng 0 thì
    không ghi phần trăm; không có kỳ so sánh: chuỗi rỗng."""
    if previous is None:
        return ""
    delta = current - previous
    text = signed_number_text(delta)
    if previous:
        text += f" ({signed_number_text(int(round_half_up(delta * 100 / previous, 0)))}%)"
    return text


def ctr_change_text(comparison: Comparison) -> str:
    """Chênh CTR theo điểm phần trăm: ``+0,3 điểm``; «ít dữ liệu»; không có kỳ so sánh: rỗng."""
    if comparison.previous is None:
        return ""
    now, before = shown_ctr_percent(comparison.current), shown_ctr_percent(comparison.previous)
    if comparison.low_data or now is None or before is None:
        return LOW_DATA_TEXT
    return f"{signed_decimal_text(now - before)} điểm"


def rank_change_text(comparison: Comparison) -> str:
    """``lên 2,1 bậc`` / ``xuống 3,4 bậc`` / ``giữ nguyên`` (số nhỏ hơn là đứng cao hơn);
    «ít dữ liệu»; không có kỳ so sánh: chuỗi rỗng."""
    if comparison.previous is None:
        return ""
    now, before = shown_position(comparison.current), shown_position(comparison.previous)
    if comparison.low_data or now is None or before is None:
        return LOW_DATA_TEXT
    gain = round_half_up(before - now)
    if gain > 0:
        return f"lên {decimal_text(gain)} bậc"
    if gain < 0:
        return f"xuống {decimal_text(-gain)} bậc"
    return "giữ nguyên"

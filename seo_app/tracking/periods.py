"""Ngày theo giờ Google và các khoảng ngày (T-123; thiết kế T-120 mục 1.5, 1.7, 2.6).

Search Console ghi số liệu theo ngày **giờ Thái Bình Dương** (PT, California): UTC−8 mùa đông,
UTC−7 mùa hè; năm 2026 đổi giờ ngày 08/03 và 01/11. Một «ngày Google» bắt đầu lúc 15:00 (mùa
đông) hay 14:00 (mùa hè) giờ Việt Nam. Mọi ngày ở đây là ngày PT, chỉ dùng ngày, không giờ phút.

- E (ngày chốt cuối, ngày trước ``first_incomplete_date``) do cache, bước lấy số liệu cung cấp.
- Khoảng N ngày là ``[E − N + 1, E]``; kỳ trước liền kề ``[E − 2N + 1, E − N]``; cùng kỳ năm
  trước lùi 364 ngày để giữ đúng thứ trong tuần. 7, 28, 91 ngày là bội của 7.
- Tuần là khối 7 ngày kết thúc ở ngày cuối của khoảng, để tuần cuối luôn đủ ngày.

Mốc ngày giờ đọc từ ngoài (cache, Google, WordPress) được kiểm khoảng năm **trước** khi đổi múi
giờ hay cộng trừ, và phép đổi múi giờ bắt ``OverflowError``, ``ValueError`` (LC-T120-10; bài học
LC-T113-1, LC-T113-2): sai thì ``None`` hay ``PeriodError`` câu cố định, không để lọt lỗi Python.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

GOOGLE_TIMEZONE = ZoneInfo("America/Los_Angeles")
PRESET_DAYS = (7, 28, 91)  # 7 ngày, 28 ngày (mặc định), 3 tháng (91 ngày, tròn 13 tuần)
DEFAULT_DAYS = 28
MAX_DAYS = 486  # 16 tháng: phần số liệu Google còn giữ
YEAR_SHIFT_DAYS = 364  # «cùng kỳ năm trước»: lùi 52 tuần
WEEK_DAYS = 7
# Năm hợp lệ của mọi ngày dùng để tính: ngoài khoảng này là dữ liệu lạ (giờ máy sai, cache sửa
# tay). Cộng trừ vài năm quanh khoảng này không bao giờ tràn ``date`` (năm 1 … 9999).
YEAR_MIN, YEAR_MAX = 2000, 2200

MSG_BAD_DATE = f"Ngày không hợp lệ (phải là ngày trong khoảng năm {YEAR_MIN}–{YEAR_MAX})."
MSG_ORDER = "Ngày bắt đầu phải trước hoặc bằng ngày kết thúc."
MSG_BAD_DAYS = f"Số ngày của khoảng phải từ 1 tới {MAX_DAYS}."
MSG_TOO_LONG = f"Khoảng ngày dài quá {MAX_DAYS} ngày (16 tháng, phần số liệu Google còn giữ)."
MSG_OUTSIDE = "Khoảng ngày nằm ngoài phần số liệu đã có (từ {first} tới {last})."

_DATE_GMT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
_DATE_GMT_FORMAT = "%Y-%m-%dT%H:%M:%S"


class PeriodError(ValueError):
    """Ngày hay khoảng ngày không hợp lệ; câu tiếng Việt cố định, hiện thẳng được."""


def is_day(value: object) -> bool:
    """``value`` là ngày thuần (``date``, không phải ``datetime``) trong khoảng năm hợp lệ."""
    return type(value) is date and YEAR_MIN <= value.year <= YEAR_MAX


def day_text(day: date) -> str:
    """Ngày viết kiểu Việt Nam: ``31/10/2026``."""
    return f"{day.day:02d}/{day.month:02d}/{day.year}"


def _checked(value: object) -> date:
    if type(value) is not date or not YEAR_MIN <= value.year <= YEAR_MAX:
        raise PeriodError(MSG_BAD_DATE)
    return value


@dataclass(frozen=True)
class Period:
    """Khoảng ngày ``[start, end]`` (cả hai đầu), ngày theo giờ PT. Tự kiểm khi tạo: ngày thuần
    trong khoảng năm hợp lệ, ``start ≤ end``; sai thì ``PeriodError``."""

    start: date
    end: date

    def __post_init__(self) -> None:
        if _checked(self.start) > _checked(self.end):
            raise PeriodError(MSG_ORDER)

    @property
    def days(self) -> int:
        """Số ngày của khoảng."""
        return (self.end - self.start).days + 1

    @property
    def text(self) -> str:
        """``01/10/2026 – 28/10/2026``."""
        return f"{day_text(self.start)} – {day_text(self.end)}"

    def __contains__(self, day: object) -> bool:
        return type(day) is date and self.start <= day <= self.end

    def inside(self, other: Period) -> bool:
        """Khoảng này nằm trọn trong ``other`` (ví dụ: cache đã có đủ số liệu cho khoảng này)."""
        return other.start <= self.start and self.end <= other.end


def last_days(end: date, days: int = DEFAULT_DAYS) -> Period:
    """Khoảng ``days`` ngày kết thúc ở ``end`` (E): ``[E − N + 1, E]``."""
    _checked(end)
    if type(days) is not int or not 1 <= days <= MAX_DAYS:
        raise PeriodError(MSG_BAD_DAYS)
    return Period(end - timedelta(days=days - 1), end)


def previous_period(period: Period) -> Period:
    """Kỳ trước liền kề, cùng số ngày: ``[E − 2N + 1, E − N]`` (mặc định để so)."""
    return Period(period.start - timedelta(days=period.days), period.start - timedelta(days=1))


def year_before(period: Period) -> Period:
    """Cùng kỳ năm trước: lùi 364 ngày để giữ đúng thứ trong tuần. Chỉ dùng khi cache có đủ
    (``year_before(p).inside(đã có)``)."""
    shift = timedelta(days=YEAR_SHIFT_DAYS)
    return Period(period.start - shift, period.end - shift)


def custom_period(start: date, end: date, *, available: Period | None = None) -> Period:
    """Khoảng tự chọn (hai ô ngày): tối đa ``MAX_DAYS`` ngày, nằm trong phần số liệu đã có
    ``available`` (nếu biết)."""
    period = Period(start, end)
    if period.days > MAX_DAYS:
        raise PeriodError(MSG_TOO_LONG)
    if available is not None and not period.inside(available):
        raise PeriodError(
            MSG_OUTSIDE.format(first=day_text(available.start), last=day_text(available.end))
        )
    return period


def week_blocks(period: Period) -> tuple[Period, ...]:
    """Các tuần (khối 7 ngày) của ``period``, cũ tới mới, kết thúc đúng ở ngày cuối của khoảng
    để tuần cuối luôn đủ ngày. Phần đầu không đủ 7 ngày thì bỏ (biểu đồ tuần không có tuần thiếu
    ngày)."""
    count = period.days // WEEK_DAYS
    return tuple(
        Period(
            period.end - timedelta(days=WEEK_DAYS * (count - index) - 1),
            period.end - timedelta(days=WEEK_DAYS * (count - index - 1)),
        )
        for index in range(count)
    )


def google_day(moment: object) -> date | None:
    """Ngày PT của một mốc giờ **có múi giờ**; ``None`` khi không phải ``datetime`` có múi giờ,
    hay năm ngoài khoảng hợp lệ (xét năm trước khi đổi múi giờ, LC-T120-10)."""
    if not isinstance(moment, datetime):
        return None
    try:
        if moment.utcoffset() is None or not YEAR_MIN <= moment.year <= YEAR_MAX:
            return None
        day = moment.astimezone(GOOGLE_TIMEZONE).date()
    except (OverflowError, ValueError, TypeError):
        return None
    return day if is_day(day) else None


def google_today(now: datetime | None = None) -> date:
    """«Hôm nay» theo giờ Google (PT). ``now``: giờ có múi giờ (mặc định: đồng hồ máy). Chỉ lấy
    ngày, nên đồng hồ máy lệch vài phút không ảnh hưởng."""
    day = google_day(datetime.now(GOOGLE_TIMEZONE) if now is None else now)
    if day is None:
        raise PeriodError(MSG_BAD_DATE)
    return day


def published_day(date_gmt: object) -> date | None:
    """Ngày đăng theo giờ PT từ ``date_gmt`` của WordPress (giờ UTC, ``YYYY-MM-DDTHH:MM:SS``, như
    ``PostState.date_gmt``). Sai dạng hay năm ngoài khoảng hợp lệ: ``None``."""
    if type(date_gmt) is not str or not _DATE_GMT.fullmatch(date_gmt):
        return None
    if not YEAR_MIN <= int(date_gmt[:4]) <= YEAR_MAX:  # trước khi dựng giờ, đổi múi giờ
        return None
    try:
        moment = datetime.strptime(date_gmt, _DATE_GMT_FORMAT).replace(tzinfo=UTC)
    except ValueError:  # tháng 13, ngày 30/02, 25 giờ…
        return None
    return google_day(moment)

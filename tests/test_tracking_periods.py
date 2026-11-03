"""T-123 (Thợ Máy): ngày theo giờ Google (PT) và khoảng ngày (``seo_app.tracking.periods``).

Thiết kế T-120 mục 1.5, 1.7, 2.6. Năm 2026 PT đổi giờ ngày 08/03 (PST → PDT, 10:00 UTC) và 01/11
(PDT → PST, 09:00 UTC). Mốc ngày giờ từ ngoài kiểm năm trước khi đổi múi giờ hay cộng trừ
(LC-T120-10): không để lọt ``OverflowError``, ``ValueError``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from seo_app.tracking import periods
from seo_app.tracking.periods import (
    GOOGLE_TIMEZONE,
    MSG_BAD_DATE,
    MSG_BAD_DAYS,
    MSG_ORDER,
    MSG_TOO_LONG,
    Period,
    PeriodError,
    custom_period,
    google_day,
    google_today,
    last_days,
    previous_period,
    published_day,
    week_blocks,
    year_before,
)

VN = ZoneInfo("Asia/Ho_Chi_Minh")
E = date(2026, 10, 31)


# ------------------------------------------------------------------------- ngày theo giờ PT


@pytest.mark.parametrize(
    ("vietnam", "pt_day"),
    [
        # Mùa đông PT (UTC−8, sau 01/11): ngày Google bắt đầu lúc 15:00 giờ Việt Nam.
        (datetime(2026, 11, 3, 14, 59, 59, tzinfo=VN), date(2026, 11, 2)),
        (datetime(2026, 11, 3, 15, 0, tzinfo=VN), date(2026, 11, 3)),
        # Mùa hè PT (UTC−7): bắt đầu lúc 14:00 giờ Việt Nam.
        (datetime(2026, 7, 15, 13, 59, 59, tzinfo=VN), date(2026, 7, 14)),
        (datetime(2026, 7, 15, 14, 0, tzinfo=VN), date(2026, 7, 15)),
        # Sáng sớm giờ Việt Nam luôn là «hôm qua» của Google.
        (datetime(2026, 1, 1, 8, 0, tzinfo=VN), date(2025, 12, 31)),
    ],
)
def test_google_today_from_vietnam_clock(vietnam, pt_day):
    assert google_today(vietnam) == pt_day


@pytest.mark.parametrize(
    ("utc", "pt_day"),
    [
        # 08/03/2026: 02:00 PST nhảy lên 03:00 PDT (10:00 UTC). Ngày 08/03 chỉ có 23 giờ.
        ("2026-03-08T07:59:59", date(2026, 3, 7)),
        ("2026-03-08T08:00:00", date(2026, 3, 8)),  # 00:00 PST
        ("2026-03-08T10:00:00", date(2026, 3, 8)),  # 03:00 PDT
        ("2026-03-09T06:59:59", date(2026, 3, 8)),  # 23:59:59 PDT
        ("2026-03-09T07:00:00", date(2026, 3, 9)),
        # 01/11/2026: 02:00 PDT lùi về 01:00 PST (09:00 UTC). Ngày 01/11 có 25 giờ.
        ("2026-11-01T06:59:59", date(2026, 10, 31)),
        ("2026-11-01T07:00:00", date(2026, 11, 1)),  # 00:00 PDT
        ("2026-11-01T09:30:00", date(2026, 11, 1)),  # 01:30 PST (lần thứ hai)
        ("2026-11-02T07:59:59", date(2026, 11, 1)),  # 23:59:59 PST
        ("2026-11-02T08:00:00", date(2026, 11, 2)),
    ],
)
def test_published_day_across_pt_daylight_saving(utc, pt_day):
    assert published_day(utc) == pt_day
    assert google_day(datetime.fromisoformat(utc).replace(tzinfo=UTC)) == pt_day


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        20261101,
        b"2026-11-01T07:00:00",
        "2026-11-01 07:00:00",  # thiếu «T»
        "2026-11-01T07:00:00Z",
        "2026-11-01T07:00",
        "２０２６-11-01T07:00:00",  # chữ số toàn chiều rộng
        "2026-13-01T00:00:00",
        "2026-02-30T00:00:00",
        "2026-11-01T24:00:00",
        "9999-12-31T23:59:59",  # năm ngoài khoảng: không đổi múi giờ
        "0001-01-01T00:00:00",
        "1999-12-31T23:59:59",
        "2201-01-01T00:00:00",
    ],
)
def test_published_day_rejects_bad_values(value):
    assert published_day(value) is None


def test_google_day_checks_year_before_converting():
    """Đổi năm 1 sang giờ PT tràn ``date`` (năm 0): kiểm năm trước nên chỉ ra ``None``."""
    first = datetime(1, 1, 1, tzinfo=UTC)
    with pytest.raises(OverflowError):  # đối chứng: đổi thẳng thì lỗi Python lọt ra
        first.astimezone(GOOGLE_TIMEZONE)
    assert google_day(first) is None
    assert google_day(datetime(9999, 12, 31, 23, 59, tzinfo=UTC)) is None
    assert google_day(datetime(2026, 11, 1, 12, 0)) is None  # không có múi giờ
    assert google_day(date(2026, 11, 1)) is None
    assert google_day("2026-11-01") is None
    offset = timezone(timedelta(hours=7))
    assert google_day(datetime(2026, 11, 3, 15, 0, tzinfo=offset)) == date(2026, 11, 3)


def test_google_today_bad_clock_gives_fixed_message():
    with pytest.raises(PeriodError, match="Ngày không hợp lệ"):
        google_today(datetime(2026, 11, 3, 15, 0))  # giờ không múi giờ
    with pytest.raises(PeriodError):
        google_today(datetime(1, 1, 1, tzinfo=UTC))
    assert type(google_today()) is date


# --------------------------------------------------------------------------- khoảng ngày


def test_last_days_previous_and_year_before():
    period = last_days(E, 28)
    assert (period.start, period.end, period.days) == (date(2026, 10, 4), E, 28)
    before = previous_period(period)
    assert (before.start, before.end) == (date(2026, 9, 6), date(2026, 10, 3))
    year = year_before(period)
    assert (year.start, year.end, year.days) == (date(2025, 10, 5), date(2025, 11, 1), 28)
    assert year.start.weekday() == period.start.weekday()  # lùi 52 tuần: đúng thứ trong tuần
    assert last_days(E).days == periods.DEFAULT_DAYS == 28
    for days in periods.PRESET_DAYS:
        assert days % 7 == 0  # hai kỳ luôn cùng số ngày thứ Bảy, Chủ nhật
        assert last_days(E, days).end == E


def test_period_contains_and_inside():
    period = Period(date(2026, 10, 1), E)
    assert date(2026, 10, 1) in period and E in period
    assert date(2026, 9, 30) not in period and date(2026, 11, 1) not in period
    assert datetime(2026, 10, 5) not in period  # datetime không phải ngày thuần
    assert period.inside(Period(date(2026, 9, 1), E))
    assert not period.inside(Period(date(2026, 10, 2), E))
    assert period.text == "01/10/2026 – 31/10/2026"


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (date(2026, 11, 1), E, MSG_ORDER),
        (datetime(2026, 10, 1), E, MSG_BAD_DATE),  # datetime là lớp con của date: vẫn từ chối
        ("2026-10-01", E, MSG_BAD_DATE),
        (date(1999, 12, 31), E, MSG_BAD_DATE),
        (date(2026, 10, 1), date(2201, 1, 1), MSG_BAD_DATE),
    ],
)
def test_period_rejects_bad_values(start, end, message):
    with pytest.raises(PeriodError) as caught:
        Period(start, end)
    assert str(caught.value) == message


@pytest.mark.parametrize("days", [0, -1, 487, True, 28.0, "28"])
def test_last_days_rejects_bad_length(days):
    with pytest.raises(PeriodError) as caught:
        last_days(E, days)
    assert str(caught.value) == MSG_BAD_DAYS


@pytest.mark.parametrize("end", [date(1, 1, 1), date.max, date(2000, 1, 3)])
def test_date_arithmetic_never_overflows(end):
    """LC-T120-10: ngày đầu/cuối của ``date`` hay sát năm tối thiểu ra ``PeriodError`` câu cố
    định, không bao giờ ``OverflowError``."""
    with pytest.raises(PeriodError):
        last_days(end, 28)


def test_previous_and_year_before_out_of_range_give_period_error():
    early = Period(date(2000, 1, 1), date(2000, 1, 28))
    with pytest.raises(PeriodError):
        previous_period(early)
    with pytest.raises(PeriodError):
        year_before(early)


def test_custom_period_limits():
    available = Period(date(2025, 7, 3), E)
    assert custom_period(date(2026, 9, 1), date(2026, 9, 30), available=available).days == 30
    assert custom_period(date(2025, 7, 3), date(2026, 10, 31)).days == periods.MAX_DAYS == 486
    with pytest.raises(PeriodError) as caught:
        custom_period(date(2025, 7, 2), E)
    assert str(caught.value) == MSG_TOO_LONG
    with pytest.raises(PeriodError) as caught:
        custom_period(date(2026, 10, 1), date(2026, 11, 2), available=available)
    assert (
        str(caught.value)
        == "Khoảng ngày nằm ngoài phần số liệu đã có (từ 03/07/2025 tới 31/10/2026)."
    )
    with pytest.raises(PeriodError) as caught:
        custom_period(E, date(2026, 10, 1))
    assert str(caught.value) == MSG_ORDER


def test_week_blocks_end_on_last_day():
    quarter = last_days(E, 91)
    weeks = week_blocks(quarter)
    assert len(weeks) == 13
    assert (weeks[-1].start, weeks[-1].end) == (date(2026, 10, 25), E)  # tuần cuối đủ 7 ngày
    assert (weeks[0].start, weeks[0].end) == (quarter.start, date(2026, 8, 8))
    assert all(week.days == 7 for week in weeks)
    assert all(a.end + timedelta(days=1) == b.start for a, b in zip(weeks, weeks[1:], strict=False))
    ten = Period(date(2026, 10, 22), E)  # 10 ngày: 3 ngày đầu không đủ tuần thì bỏ
    assert [(w.start, w.end) for w in week_blocks(ten)] == [(date(2026, 10, 25), E)]
    assert week_blocks(Period(date(2026, 10, 26), E)) == ()  # 6 ngày: chưa đủ một tuần

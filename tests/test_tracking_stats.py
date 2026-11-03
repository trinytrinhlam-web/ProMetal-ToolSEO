"""T-123 (Thợ Máy): cộng dồn, vị trí theo lượt hiển thị, so hai kỳ, số viết kiểu Việt Nam
(``seo_app.tracking.stats``; thiết kế T-120 mục 1.5).
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import pytest
from test_tracking_model import SITE, Day, day_row, item

from seo_app.tracking import stats
from seo_app.tracking.match import build_tracking
from seo_app.tracking.model import PageStats
from seo_app.tracking.periods import Period, last_days, previous_period
from seo_app.tracking.stats import (
    LOW_DATA_TEXT,
    aggregate,
    change_text,
    compare,
    ctr_change_text,
    decimal_text,
    number_text,
    percent_text,
    rank_change_text,
    signed_decimal_text,
    site_totals,
    weekly,
)

E = date(2026, 10, 31)
OCTOBER = Period(date(2026, 10, 1), E)


def test_aggregate_sums_days_inside_period_only():
    rows = [
        day_row(date(2026, 9, 30), "/a/", 9, 90),  # trước kỳ
        day_row(date(2026, 10, 1), "/a/", 1, 10, 2.0),  # ngày đầu kỳ: tính
        day_row(E, "/a/", 2, 30, 6.0),  # ngày cuối kỳ: tính
        day_row(date(2026, 11, 1), "/a/", 9, 90),  # sau kỳ
    ]
    total = aggregate(rows, OCTOBER)
    assert (total.clicks, total.impressions, total.position_sum) == (3, 40, 200.0)
    assert total.position == 5.0  # theo lượt hiển thị: (2×10 + 6×30) / 40, không phải (2+6)/2
    assert total.ctr == 3 / 40


def test_aggregate_skips_provisional_unless_asked():
    rows = [day_row(date(2026, 10, 29), "/a/", 1, 10), day_row(E, "/a/", 5, 20, final=False)]
    assert aggregate(rows, OCTOBER) == PageStats(1, 10, 10.0)  # câu hỏi 3 = A: số tạm không tính
    assert stats.SHOW_PROVISIONAL is False
    assert aggregate(rows, OCTOBER, include_provisional=True) == PageStats(6, 30, 30.0)


@pytest.mark.parametrize(
    "bad",
    [
        Day(E, SITE + "/a/", True, 10, 10.0),
        Day(E, SITE + "/a/", 1, 10, math.nan),
        Day(E, SITE + "/a/", 11, 10, 10.0),
        Day(E, SITE + "/a/", 0, 0, 0.0),
        Day(E, SITE + "/a/", 1, 10, 10.0, final=1),  # «final» không phải True: coi là số tạm
    ],
)
def test_aggregate_never_spreads_bad_numbers(bad):
    total = aggregate([bad, day_row(E, "/a/", 1, 10)], OCTOBER)
    assert total == PageStats(1, 10, 10.0)
    assert math.isfinite(total.position_sum)


def test_empty_period_has_no_ratio():
    total = aggregate([], OCTOBER)
    assert total == PageStats() and total.ctr is None and total.position is None


def test_compare_low_data_threshold():
    assert stats.LOW_DATA_IMPRESSIONS == 30
    enough = compare(PageStats(3, 30, 60.0), PageStats(2, 30, 90.0))
    assert not enough.low_data and enough.rank_gain == 1.0
    thin = compare(PageStats(3, 29, 58.0), PageStats(2, 300, 900.0))
    assert thin.low_data and thin.rank_gain is None and thin.ctr_delta is None
    assert thin.clicks_delta == 1  # click, hiển thị vẫn so
    alone = compare(PageStats(3, 29, 58.0), None)
    assert not alone.low_data and alone.previous is None


def test_change_texts_vietnamese_style():
    assert change_text(52, 40) == "+12 (+30%)"
    assert change_text(40, 52) == "-12 (-23%)"
    assert change_text(12, 0) == "+12"  # kỳ trước 0: không có phần trăm
    assert change_text(0, 0) == "0"
    assert change_text(9800, 1200) == "+8.600 (+717%)"
    assert change_text(5, None) == ""
    up = compare(PageStats(50, 1000, 4200.0), PageStats(47, 1000, 6300.0))
    assert ctr_change_text(up) == "+0,3 điểm"
    assert rank_change_text(up) == "lên 2,1 bậc"
    down = compare(PageStats(10, 500, 3800.0), PageStats(10, 500, 2100.0))
    assert rank_change_text(down) == "xuống 3,4 bậc"
    assert ctr_change_text(down) == "0 điểm"
    same = compare(PageStats(1, 100, 424.0), PageStats(1, 100, 416.0))  # 4,24 và 4,16 đều hiện 4,2
    assert rank_change_text(same) == "giữ nguyên"
    thin = compare(PageStats(1, 10, 20.0), PageStats(1, 100, 200.0))
    assert ctr_change_text(thin) == LOW_DATA_TEXT == "ít dữ liệu"
    assert rank_change_text(thin) == LOW_DATA_TEXT
    alone = compare(PageStats(1, 10, 20.0), None)
    assert ctr_change_text(alone) == "" and rank_change_text(alone) == ""


def test_number_formats():
    assert number_text(9800) == "9.800"
    assert number_text(1234567) == "1.234.567"
    assert number_text(-1200) == "-1.200"
    assert decimal_text(4.2) == "4,2"
    assert decimal_text(1234.5) == "1.234,5"
    assert decimal_text(-0.04) == "0,0"  # không ra «-0,0»
    assert percent_text(0.042) == "4,2%"
    assert percent_text(0.5, 0) == "50%"
    assert signed_decimal_text(0.3) == "+0,3"
    assert signed_decimal_text(-1.25) == "-1,3"  # 5 lên (round của Python ra -1,2)
    assert signed_decimal_text(0.04) == "0"


@pytest.mark.parametrize(
    ("value", "digits", "rounded"),
    [
        (0.25, 1, 0.3),  # round() của Python: 0,2
        (-0.25, 1, -0.3),
        (4.35, 1, 4.4),  # số nhị phân của 4,35 hơi nhỏ hơn 4,35; làm tròn theo chữ viết ra
        (2.0999999999999996, 1, 2.1),  # 6,3 − 4,2
        (12.5, 0, 13.0),
        (7.04, 1, 7.0),
    ],
)
def test_round_half_up(value, digits, rounded):
    assert stats.round_half_up(value, digits) == rounded
    assert math.isnan(stats.round_half_up(math.nan))
    assert percent_text(0.0025) == "0,3%"
    assert decimal_text(4.25) == "4,3"
    assert change_text(9, 8) == "+1 (+13%)"  # 12,5% → 13%


def test_site_totals_add_every_page_and_other_page():
    rows = [
        day_row(E, "/a/", 1, 10, 2.0),
        day_row(E, "/b/", 2, 20, 4.0),
        day_row(E, "/category/x/", 3, 30, 6.0),
        day_row(E - timedelta(days=40), "/a/", 9, 90),  # ngoài kỳ
    ]
    tracking = build_tracking(SITE, [item(1, "/a/"), item(2, "/b/")], rows)
    total = site_totals(tracking.pages + tracking.others, OCTOBER)
    assert total == PageStats(6, 60, 20.0 + 80.0 + 180.0)


def test_weekly_blocks_cover_the_period():
    quarter = last_days(E, 91)
    rows = [day_row(quarter.start + timedelta(days=offset), "/a/", 1, 10) for offset in range(91)]
    weeks = weekly(rows, quarter)
    assert len(weeks) == 13
    assert all(week.days == 7 and total == PageStats(7, 70, 70.0) for week, total in weeks)
    assert sum(total.clicks for _, total in weeks) == aggregate(rows, quarter).clicks == 91
    assert weeks[-1][0].end == E
    before = previous_period(quarter)
    assert aggregate(rows, before) == PageStats()  # kỳ trước không có dòng nào: 0

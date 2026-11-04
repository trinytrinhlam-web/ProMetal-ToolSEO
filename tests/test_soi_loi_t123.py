"""Soi Lỗi T-123 (đầy đủ): lõi tính toán theo dõi bài, gói ``seo_app/tracking/`` (hàm thuần).

Kiểm độc lập với test của Thợ Máy, dùng chung dữ liệu giả của ``tests/test_tracking_model.py``
(``Day``, ``Query`` đúng tên trường ``CachedDay``, ``CachedQuery`` của T-122). Không gọi mạng, không
đọc ghi file. Mọi tham số kèm ``ids=`` ngắn (tên ca dài trên Windows làm pytest in cả biến môi
trường).

Trọng tâm theo tin giao: ngày đổi giờ PT, biên 16 tháng, năm 1 / 9999, ``%E1%BB%AD`` hoa / thường,
dòng chỉ khác ``#…``, bài đổi slug, slug trùng, vị trí 0, click lớn hơn hiển thị, từ khóa toàn ký
tự vô hình, 3 chỗ Thợ Máy tự chọn (khớp mã trước trạng thái, slug chỉ cho dòng «Đã đăng», làm tròn
kiểu 5 lên).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

import pytest
from test_tracking_model import SITE, Day, day_row, item, plan_row, query_row

from seo_app.tracking import flags, keywords, match, periods, stats
from seo_app.tracking.model import FlagKind, MatchStatus, PageKey, PageStats

VN = ZoneInfo("Asia/Ho_Chi_Minh")
E = date(2026, 10, 28)
ZW = "".join(chr(code) for code in (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x202E))


# ====================================================================== lỗi mới (xfail)


@pytest.mark.parametrize(
    ("clicks", "impressions", "shown", "text"),
    [(23, 80, 28.8, "28,8%"), (41, 80, 51.3, "51,3%"), (57, 400, 14.3, "14,3%")],
    ids=["28,75", "51,25", "14,25"],
)
def test_ctr_exact_half_always_rounds_up(clicks, impressions, shown, text):
    """``shown_ctr_percent``, ``percent_text`` nhân CTR với 100 bằng số thực trước khi làm tròn:
    23/80 = 28,75% thành 28,749999…% nên hiện «28,7%», trong khi 1/400 = 0,25% hiện «0,3%»."""
    page = PageStats(clicks, impressions, float(impressions))
    assert stats.shown_ctr_percent(page) == shown
    assert stats.percent_text(page.ctr) == text


def test_every_exact_half_ctr_rounds_up():
    """Mọi CTR đúng nửa ở chữ số thứ hai (lượt hiển thị ≤ 400) hiện theo «5 lên»."""
    wrong = []
    for impressions in range(1, 401):
        for clicks in range(impressions + 1):
            exact = Decimal(clicks) * 100 / Decimal(impressions)
            scaled = exact * 100
            if scaled != scaled.to_integral_value() or scaled % 10 != 5:
                continue
            want = float(exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
            got = stats.shown_ctr_percent(PageStats(clicks, impressions, float(impressions)))
            if got != want:
                wrong.append((clicks, impressions))
    assert wrong == []


@pytest.mark.parametrize(
    "site",
    ["https://Suachuacuasat.com", "https://SUACHUACUASAT.COM", "HTTPS://suachuacuasat.com"],
    ids=["hoa-dau", "hoa-het", "scheme-hoa"],
)
def test_site_url_case_does_not_drop_everything(site):
    """``is_site_link`` so tên máy không phân biệt hoa thường (như HTTP, DNS), nhưng ``page_key``
    còn đòi ``url.startswith(site + "/")`` phân biệt hoa thường: ``WORDPRESS_URL`` gõ có chữ hoa
    (app vẫn kết nối WordPress bình thường) thì bảng theo dõi trống, mọi dòng thành «dòng lạ»."""
    tracking = match.build_tracking(site, [item(1, "/bai-1/")], [day_row(E, "/bai-1/", 1, 10)])
    assert [page.item.id for page in tracking.pages] == [1]
    assert tracking.skipped_rows == 0 and tracking.pages[0].days


# ============================================== LC-T120-6 giữ nguyên khi sửa SL-T123-2


@pytest.mark.parametrize(
    "url",
    [
        "https://staging.suachuacuasat.com/bai-1/",
        "https://STAGING.SUACHUACUASAT.COM/bai-1/",
        "https://www.suachuacuasat.com/bai-1/",
        "http://suachuacuasat.com/bai-1/",
        "https://suachuacuasat.com.evil.example/bai-1/",
        "https://suachuacuasat.com:8443/bai-1/",
    ],
    ids=["staging", "staging-hoa", "www", "http", "duoi-la", "cong-khac"],
)
@pytest.mark.parametrize("site", [SITE, "https://Suachuacuasat.com"], ids=["thuong", "hoa"])
def test_rows_outside_website_stay_dropped_whatever_the_case(url, site):
    """Sửa so hoa thường không được nới lớp chặn staging, ``www.``, ``http://``, tên miền khác."""
    assert match.page_key(url, site) is None


# ============================================================ giờ Google (PT), đổi giờ


@pytest.mark.parametrize(
    ("date_gmt", "day"),
    [
        ("2026-03-08T07:59:59", date(2026, 3, 7)),  # 23:59:59 PST
        ("2026-03-08T08:00:00", date(2026, 3, 8)),  # 00:00 PST, đổi giờ lúc 02:00 cùng ngày
        ("2026-03-09T06:59:59", date(2026, 3, 8)),  # 23:59:59 PDT (UTC−7)
        ("2026-03-09T07:00:00", date(2026, 3, 9)),
        ("2026-11-01T06:59:59", date(2026, 10, 31)),  # 23:59:59 PDT
        ("2026-11-01T07:00:00", date(2026, 11, 1)),  # 00:00 PDT, lùi giờ lúc 02:00 cùng ngày
        ("2026-11-02T07:59:59", date(2026, 11, 1)),  # 23:59:59 PST (UTC−8)
        ("2026-11-02T08:00:00", date(2026, 11, 2)),
    ],
    ids=["0308-truoc", "0308-dau", "0309-truoc", "0309-dau", "1101-truoc", "1101-dau",
         "1102-truoc", "1102-dau"],
)  # fmt: skip
def test_published_day_on_pt_daylight_saving_edges(date_gmt, day):
    assert periods.published_day(date_gmt) == day


@pytest.mark.parametrize(
    ("vietnam", "day"),
    [
        (datetime(2026, 3, 8, 14, 59, 59, tzinfo=VN), date(2026, 3, 7)),
        (datetime(2026, 3, 8, 15, 0, tzinfo=VN), date(2026, 3, 8)),
        (datetime(2026, 3, 9, 13, 59, 59, tzinfo=VN), date(2026, 3, 8)),
        (datetime(2026, 3, 9, 14, 0, tzinfo=VN), date(2026, 3, 9)),
        (datetime(2026, 11, 1, 13, 59, 59, tzinfo=VN), date(2026, 10, 31)),
        (datetime(2026, 11, 1, 14, 0, tzinfo=VN), date(2026, 11, 1)),
        (datetime(2026, 11, 2, 14, 59, 59, tzinfo=VN), date(2026, 11, 1)),
        (datetime(2026, 11, 2, 15, 0, tzinfo=VN), date(2026, 11, 2)),
    ],
    ids=["0308-1459", "0308-1500", "0309-1359", "0309-1400", "1101-1359", "1101-1400",
         "1102-1459", "1102-1500"],
)  # fmt: skip
def test_google_today_from_vietnam_clock_on_dst_edges(vietnam, day):
    """Ngày Google bắt đầu 15:00 (mùa đông) hay 14:00 (mùa hè) giờ Việt Nam, đổi đúng ngày."""
    assert periods.google_today(vietnam) == day


def test_periods_across_dst_count_calendar_days():
    """Kỳ ngày chỉ dùng ngày, không giờ: kỳ 7, 28 ngày qua ngày đổi giờ vẫn đúng số ngày, tuần
    vẫn đủ 7 ngày."""
    for end in (date(2026, 3, 10), date(2026, 11, 3)):
        for days in periods.PRESET_DAYS:
            period = periods.last_days(end, days)
            assert period.days == days == periods.previous_period(period).days
            weeks = periods.week_blocks(period)
            assert all(week.days == 7 for week in weeks) and weeks[-1].end == end


# ========================================================== biên 16 tháng, năm 1 / 9999


def test_sixteen_month_edge():
    assert periods.last_days(E, periods.MAX_DAYS).days == 486
    assert periods.custom_period(E - timedelta(days=485), E).days == 486
    with pytest.raises(periods.PeriodError):
        periods.last_days(E, periods.MAX_DAYS + 1)
    with pytest.raises(periods.PeriodError):
        periods.custom_period(E - timedelta(days=486), E)
    available = periods.Period(E - timedelta(days=485), E)
    assert periods.custom_period(available.start, E, available=available) == available
    with pytest.raises(periods.PeriodError):
        periods.custom_period(available.start - timedelta(days=1), E, available=available)


@pytest.mark.parametrize(
    "value",
    [date(1, 1, 1), date(9999, 12, 31), datetime(2026, 1, 1), "2026-01-01", None, True],
    ids=["nam-1", "nam-9999", "datetime", "chu", "none", "bool"],
)
def test_odd_dates_give_period_error_never_python_errors(value):
    for args in ((value, E), (E, value)):
        with pytest.raises(periods.PeriodError):
            periods.Period(*args)
    with pytest.raises(periods.PeriodError):
        periods.last_days(value, 7)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "moment",
    [
        datetime(1, 1, 1, tzinfo=UTC),
        datetime(9999, 12, 31, 23, 59, 59, tzinfo=UTC),
        datetime.min.replace(tzinfo=periods.GOOGLE_TIMEZONE),
        datetime.max.replace(tzinfo=VN),
        datetime(2026, 1, 1),
    ],
    ids=["nam-1", "nam-9999", "min-pt", "max-vn", "khong-mui-gio"],
)
def test_google_day_never_overflows(moment):
    assert periods.google_day(moment) is None
    with pytest.raises(periods.PeriodError):
        periods.google_today(moment)


@pytest.mark.parametrize(
    "date_gmt",
    ["0001-01-01T00:00:00", "9999-12-31T23:59:59", "1999-12-31T23:59:59", "2201-01-01T00:00:00",
     "2026-02-29T00:00:00", "2026-13-01T00:00:00", "2026-10-28T24:00:00", "2026-10-28 08:00:00",
     "２０２６-10-28T08:00:00"],
    ids=["nam-1", "nam-9999", "1999", "2201", "29-2", "thang-13", "24-gio", "dau-cach", "so-rong"],
)  # fmt: skip
def test_published_day_rejects_odd_values(date_gmt):
    assert periods.published_day(date_gmt) is None


def test_comparison_periods_near_year_limits_raise_period_error():
    first = periods.Period(date(2000, 1, 1), date(2000, 1, 7))
    for shift in (periods.previous_period, periods.year_before):
        with pytest.raises(periods.PeriodError):
            shift(first)
    last = periods.Period(date(2200, 12, 25), date(2200, 12, 31))
    assert periods.previous_period(last).end == date(2200, 12, 24)
    assert periods.year_before(last).start == date(2199, 12, 26)


# ============================================================ khóa trang (page_key)


@pytest.mark.parametrize(
    "url",
    [f"{SITE}/s%E1%BB%ADa-cua/", f"{SITE}/s%e1%bb%ada-cua/", f"{SITE}/s%E1%bb%Ada-cua",
     f"{SITE}/sửa-cua/", f"{SITE}/sửa-cua#tieu-de", f"{SITE}/s%E1%BB%ADa-cua/#a?b=1"],
    ids=["hoa", "thuong", "lan", "chu-that", "ngoac-thang", "ngoac-co-hoi"],
)  # fmt: skip
def test_percent_case_raw_unicode_and_fragment_give_one_key(url):
    assert match.page_key(url, SITE) == PageKey("/sửa-cua")


def test_rows_differing_only_by_fragment_or_percent_case_are_summed():
    """Hai, ba dòng cùng ngày chỉ khác ``#…``, «/» cuối, cách viết ``%``: cộng thành một ngày của
    đúng bài (vị trí trung bình theo lượt hiển thị)."""
    rows = [
        Day(E, f"{SITE}/s%E1%BB%ADa-cua/", 2, 10, 30.0),
        Day(E, f"{SITE}/s%e1%bb%ada-cua/#gia", 1, 20, 100.0),
        Day(E, f"{SITE}/sửa-cua", 0, 10, 20.0),
    ]
    tracking = match.build_tracking(SITE, [item(1, "/s%e1%bb%ada-cua/")], rows)
    (page,) = tracking.pages
    (total,) = page.days
    assert (total.clicks, total.impressions, total.position_sum) == (3, 40, 150.0)
    assert tracking.others == () and tracking.skipped_rows == 0


def test_query_inside_fragment_is_not_a_query_but_real_query_is_other_page():
    assert match.page_key(f"{SITE}/a/#x?s=1", SITE) == PageKey("/a")
    assert match.page_key(f"{SITE}/a/?s=1#x", SITE) == PageKey("/a", "s=1")
    tracking = match.build_tracking(SITE, [item(1, "/a/")], [day_row(E, "/a/?s=1", 1, 5)])
    assert tracking.pages[0].days == () and [p.label for p in tracking.others] == ["/a?s=1"]


# ======================================================= bài đổi slug, slug trùng hai bài


def test_renamed_post_old_address_goes_to_other_pages_plan_by_id_keeps_post():
    rows = [day_row(E, "/cua-cuon-cu/", 5, 100), day_row(E, "/cua-cuon-moi/", 1, 10)]
    post = item(7, "/cua-cuon-moi/")
    plan = [plan_row(status="Đã đăng", wp_post_id=7), plan_row("k2", status="Đã đăng",
                                                                slug="cua-cuon-cu")]  # fmt: skip
    tracking = match.build_tracking(SITE, [post], rows, plan)
    (page,) = tracking.pages
    assert page.plan is plan[0] and [d.clicks for d in page.days] == [1]
    assert [other.label for other in tracking.others] == ["/cua-cuon-cu"]
    assert [m.status for m in tracking.plan] == [MatchStatus.BY_ID, MatchStatus.NOT_FOUND]


def test_two_posts_with_the_same_slug_are_never_guessed():
    posts = [item(1, "/2025/cua-sat/", slug="cua-sat"), item(2, "/2026/cua-sat/", slug="cua-sat")]
    plan = [plan_row(status="Đã đăng", slug="cua-sat"), plan_row("k2", status="Đã đăng",
                                                                  wp_post_id=2)]  # fmt: skip
    found = match.match_plan(plan, posts)
    assert [m.status for m in found] == [MatchStatus.AMBIGUOUS, MatchStatus.BY_ID]
    assert found[0].item is None and found[1].item.id == 2


# =============================================================== số sai dạng, từ khóa lạ


@pytest.mark.parametrize(
    ("clicks", "impressions", "position_sum"),
    [(1, 10, 0.0), (1, 10, 9.99), (11, 10, 30.0), (0, 0, 0.0), (-1, 10, 30.0),
     (1, 10, float("nan")), (True, 10, 30.0), (1, 10, 100_001.0)],
    ids=["vi-tri-0", "vi-tri-duoi-1", "click-hon-hien-thi", "hien-thi-0", "click-am", "nan",
         "bool", "vi-tri-tren-10000"],
)  # fmt: skip
def test_bad_numbers_are_skipped_in_days_and_keywords(clicks, impressions, position_sum):
    tracking = match.build_tracking(
        SITE, [item(1, "/a/")], [Day(E, f"{SITE}/a/", clicks, impressions, position_sum)]
    )
    assert tracking.skipped_rows == 1 and tracking.pages[0].days == ()
    period = periods.last_days(E, 7)
    bad = query_row(period, "/a/", "sửa cửa", 0, 1)
    bad = type(bad)(bad.start, bad.end, bad.page, bad.query, clicks, impressions, position_sum)
    table = keywords.keyword_table([bad])
    assert table.groups == () and table.skipped == 1


def test_invisible_only_keyword_is_dropped_and_never_main():
    period = periods.last_days(E, 28)
    rows = [query_row(period, "/a/", ZW, 5, 50), query_row(period, "/a/", "sửa cửa", 1, 10)]
    table = keywords.keyword_table(rows, main_keyword=ZW)
    assert [group.text for group in table.groups] == ["sửa cửa"] and table.skipped == 1
    assert keywords.has_keyword(table, ZW) is None and not table.groups[0].is_main
    row = plan_row(ZW + "ab", status="Đã đăng", wp_post_id=1)  # từ khóa chính làm sạch còn «ab»
    page = match.build_tracking(SITE, [item(1, "/a/")], [], [row]).pages[0]
    many = stats.compare(PageStats(5, 500, 1000.0), PageStats(5, 500, 1000.0))
    labels = {f.kind for f in flags.page_flags(page, many, end=E, keywords=table)}
    assert FlagKind.MAIN_KEYWORD in labels  # «ab» (từ khóa chính đã làm sạch) không có trong bảng


# ======================================================== 3 chỗ Thợ Máy tự chọn (đồng ý)


@pytest.mark.parametrize(
    "status",
    ["Chưa viết", "Đang viết", "Đã gửi nháp", "Đã hẹn giờ", "Đã đăng"],
    ids=["chua-viet", "dang-viet", "gui-nhap", "hen-gio", "da-dang"],
)
def test_choice_1_post_id_matches_before_status(status):
    """Chọn 1: dòng có mã bài của một bài đã đăng thì khớp, kể cả khi Sheet chưa cập nhật trạng
    thái (bài hẹn giờ tự lên, chủ dự án tự đăng trong trang quản trị); mã sai thì không đoán."""
    posts = [item(5, "/a/")]
    (found,) = match.match_plan([plan_row(status=status, wp_post_id=5)], posts)
    assert found.status is MatchStatus.BY_ID and found.item.id == 5
    (missing,) = match.match_plan([plan_row(status=status, wp_post_id=6, slug="a")], posts)
    assert missing.status in (MatchStatus.NOT_LIVE, MatchStatus.NOT_FOUND) and missing.item is None


@pytest.mark.parametrize(
    "status",
    ["Chưa viết", "Đang viết", "Đã gửi nháp", "Đã hẹn giờ"],
    ids=["chua-viet", "dang-viet", "gui-nhap", "hen-gio"],
)
def test_choice_2_slug_only_for_published_rows(status):
    """Chọn 2: dòng chưa lên website mà slug trùng bài cũ không nhận số của bài cũ."""
    posts = [item(5, "/cua-sat/")]
    (found,) = match.match_plan([plan_row(status=status, slug="cua-sat")], posts)
    assert found.status is MatchStatus.NOT_LIVE and found.item is None
    (published,) = match.match_plan([plan_row(status="Đã đăng", slug="cua-sat")], posts)
    assert published.status is MatchStatus.BY_SLUG and published.item.id == 5


def test_choice_3_id_row_keeps_post_against_slug_row():
    posts = [item(5, "/cua-sat/")]
    rows = [plan_row(status="Đã đăng", slug="cua-sat"), plan_row("k2", status="Đã hẹn giờ",
                                                                  wp_post_id=5)]  # fmt: skip
    assert [m.status for m in match.match_plan(rows, posts)] == [
        MatchStatus.DUPLICATE,
        MatchStatus.BY_ID,
    ]


@pytest.mark.parametrize(
    ("value", "shown"),
    [(0.25, 0.3), (-0.25, -0.3), (4.35, 4.4), (2.5, 2.5), (9.95, 10.0), (0.05, 0.1)],
    ids=["0,25", "-0,25", "4,35", "2,5", "9,95", "0,05"],
)
def test_choice_8_half_up_on_written_digits(value, shown):
    assert stats.round_half_up(value) == shown


def test_choice_8_flags_follow_the_shown_numbers():
    """Ngưỡng so trên số đã làm tròn như khi hiện: «4,0 → 7,0» là xuống đúng 3 bậc; CTR 0,95%
    hiện «1,0%» nên không phải «dưới 1%»."""
    page = match.build_tracking(SITE, [item(1, "/a/")], []).pages[0]
    before, now = PageStats(0, 1000, 3960.0), PageStats(0, 1000, 6960.0)  # 3,96 → 6,96
    labels = {f.kind for f in flags.page_flags(page, stats.compare(now, before), end=E)}
    assert FlagKind.RANK_DROP in labels  # hiện «4,0 → 7,0»
    ctr_095 = PageStats(19, 2000, 2000.0)  # 0,95%, vị trí 1
    labels = {f.kind for f in flags.page_flags(page, stats.compare(ctr_095, None), end=E)}
    assert FlagKind.LOW_CTR not in labels
    ctr_094 = PageStats(188, 20000, 20000.0)  # 0,94%
    labels = {f.kind for f in flags.page_flags(page, stats.compare(ctr_094, None), end=E)}
    assert FlagKind.LOW_CTR in labels

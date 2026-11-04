"""T-123 (Thợ Máy): nhãn đánh dấu bài (``seo_app.tracking.flags``; thiết kế T-120 mục 1.6).

Ngưỡng là hằng có tên theo mặc định ở câu hỏi 5 (khuyến nghị A). Câu giải thích chỉ chèn số và
ngày, không chèn chữ của Google hay WordPress (LC-T120-11).
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from test_tracking_model import item, plan_row, query_row

from seo_app.plan import model as plan_model
from seo_app.tracking import flags
from seo_app.tracking.flags import (
    ATTENTION,
    HINTS,
    LABELS,
    attention_counts,
    attention_text,
    page_flags,
)
from seo_app.tracking.keywords import keyword_table
from seo_app.tracking.match import page_label
from seo_app.tracking.model import FlagKind, PageKey, PageStats, TrackedPage
from seo_app.tracking.periods import last_days
from seo_app.tracking.stats import compare

E = date(2026, 10, 31)
NOW = last_days(E, 28)
HOSTILE = "<script>alert(1)</script> https://evil.example [x](javascript:1)"


def post(*, plan=None, kind="post", title=HOSTILE) -> TrackedPage:
    entry = item(10, "/sua-cua-sat/", kind=kind, title=title, slug="sua-cua-sat")
    return TrackedPage(PageKey("/sua-cua-sat"), entry.title, entry, plan, ())


def at(clicks: int, impressions: int, position: float) -> PageStats:
    return PageStats(clicks, impressions, position * impressions)


def kinds(page, now, before, **kwargs):
    return [flag.kind for flag in page_flags(page, compare(now, before), end=E, **kwargs)]


def test_thresholds_are_named_constants_of_question_5():
    assert (flags.RANK_MIN_IMPRESSIONS, flags.RANK_CHANGE_POSITIONS, flags.FIRST_PAGE_POSITION) == (
        30,
        3.0,
        10.0,
    )
    assert (flags.CLICK_LOSS_MIN_PREVIOUS, flags.CLICK_LOSS_RATIO) == (10, 0.5)
    assert flags.NEW_POST_DAYS == 14
    assert (
        flags.LOW_CTR_MIN_IMPRESSIONS,
        flags.LOW_CTR_MAX_POSITION,
        flags.LOW_CTR_MAX_PERCENT,
    ) == (
        200,
        10.0,
        1.0,
    )
    assert flags.MAIN_KEYWORD_MIN_IMPRESSIONS == 100
    assert set(LABELS) == set(HINTS) == set(FlagKind)


# ------------------------------------------------------------------------- tụt / lên hạng


@pytest.mark.parametrize(
    ("before", "after", "expected"),
    [
        (4.0, 7.0, [FlagKind.RANK_DROP]),  # kém đúng 3 bậc
        (4.0, 6.9, []),
        (4.04, 6.96, [FlagKind.RANK_DROP]),  # hiện 4,0 → 7,0: so trên số đã làm tròn
        (9.8, 10.2, [FlagKind.RANK_DROP]),  # rơi khỏi trang 1
        (10.0, 10.1, [FlagKind.RANK_DROP]),
        (10.1, 12.0, []),  # đã ở ngoài trang 1, kém chưa tới 3 bậc
        (7.0, 4.0, [FlagKind.RANK_RISE]),
        (10.5, 9.9, [FlagKind.RANK_RISE]),  # vào trang 1
        (5.0, 5.0, []),
    ],
)
def test_rank_drop_and_rise(before, after, expected):
    assert kinds(post(), at(5, 100, after), at(5, 100, before)) == expected


def test_rank_needs_enough_impressions_in_both_periods():
    assert kinds(post(), at(1, 30, 9.0), at(1, 30, 4.0)) == [FlagKind.RANK_DROP]
    assert kinds(post(), at(1, 29, 9.0), at(1, 300, 4.0)) == []
    assert kinds(post(), at(10, 300, 9.0), at(1, 29, 4.0)) == []  # CTR 3,3%: không «ít click»
    assert kinds(post(), at(10, 300, 9.0), None) == []  # không có kỳ so sánh


def test_rank_reason_has_numbers_only():
    (flag,) = page_flags(post(), compare(at(5, 100, 11.0), at(5, 100, 9.6)), end=E)
    assert flag.label == "🔻 Tụt hạng"
    assert (
        flag.reason
        == "Vị trí trung bình kỳ trước 9,6, kỳ này 11,0: xuống 1,4 bậc; rơi khỏi trang 1."
    )
    (rise,) = page_flags(post(), compare(at(5, 100, 4.0), at(5, 100, 7.5)), end=E)
    assert rise.reason == "Vị trí trung bình kỳ trước 7,5, kỳ này 4,0: lên 3,5 bậc."


# -------------------------------------------------------------------------------- mất click


@pytest.mark.parametrize(
    ("before", "now", "lost"),
    [(10, 5, True), (10, 6, False), (9, 0, False), (40, 20, True), (40, 21, False), (11, 5, True)],
)
def test_lost_clicks(before, now, lost):
    found = kinds(post(), at(now, 1000, 20.0), at(before, 1000, 20.0))
    assert (FlagKind.LOST_CLICKS in found) is lost


def test_lost_clicks_reason():
    flag = page_flags(post(), compare(at(4, 1000, 20.0), at(12, 1000, 20.0)), end=E)[0]
    assert flag.kind is FlagKind.LOST_CLICKS
    assert flag.reason == "Click kỳ này 4, kỳ trước 12: -8 (-67%)."


# -------------------------------------------------------------- mới đăng / chưa có hiển thị


def test_no_impressions_for_old_post_with_date():
    published = E - timedelta(days=30)
    (flag,) = page_flags(post(), compare(PageStats(), PageStats()), end=E, published=published)
    assert flag.kind is FlagKind.NO_IMPRESSIONS
    assert flag.reason == (
        "0 lượt hiển thị trong cả hai kỳ; bài đăng ngày 01/10/2026 (30 ngày tính tới 31/10/2026)."
    )
    assert "Kiểm tra URL" in flag.hint


@pytest.mark.parametrize("age", [14, 15, 400])
def test_no_impressions_from_14_days(age):
    found = kinds(post(), PageStats(), PageStats(), published=E - timedelta(days=age))
    assert found == [FlagKind.NO_IMPRESSIONS]


@pytest.mark.parametrize("age", [0, 1, 13])
def test_new_post_instead_of_no_impressions(age):
    published = E - timedelta(days=age)
    (flag,) = page_flags(post(), compare(PageStats(), PageStats()), end=E, published=published)
    assert flag.kind is FlagKind.NEW and flag.label == "🌱 Mới đăng"
    assert flag.reason.endswith(f"({age} ngày tính tới 31/10/2026).")


def test_post_published_after_period_end():
    (flag,) = page_flags(
        post(), compare(PageStats(), PageStats()), end=E, published=E + timedelta(days=3)
    )
    assert flag.kind is FlagKind.NEW
    assert flag.reason == "Bài đăng ngày 03/11/2026, sau ngày cuối kỳ đang xem."


def test_no_impressions_unknown_date_page_and_no_previous():
    (unknown,) = page_flags(post(), compare(PageStats(), PageStats()), end=E)
    assert unknown.reason == "0 lượt hiển thị trong cả hai kỳ; chưa rõ ngày đăng."
    (page,) = page_flags(post(kind="page"), compare(PageStats(), PageStats()), end=E, published=E)
    assert page.kind is FlagKind.NO_IMPRESSIONS  # trang: không xét ngày đăng, không «mới đăng»
    assert page.reason == "0 lượt hiển thị trong cả hai kỳ."
    (alone,) = page_flags(post(kind="page"), compare(PageStats(), None), end=E)
    assert alone.reason == "0 lượt hiển thị trong kỳ đang xem."


def test_impressions_in_one_period_is_not_no_impressions():
    assert kinds(post(), PageStats(), at(1, 10, 5.0), published=E - timedelta(days=60)) == []
    assert kinds(post(), at(0, 10, 5.0), PageStats(), published=E - timedelta(days=60)) == []


@pytest.mark.parametrize("published", [date(1, 1, 1), date(9999, 12, 31), "2026-10-01", 20261001])
def test_bad_published_date_never_overflows(published):
    """LC-T120-10: ngày đăng lạ thì coi như chưa rõ, không trừ ngày (không ``OverflowError``)."""
    assert kinds(post(), PageStats(), PageStats(), published=published) == [FlagKind.NO_IMPRESSIONS]


def test_bad_period_end_never_overflows():
    found = page_flags(post(), compare(PageStats(), PageStats()), end=date.max, published=E)
    assert [flag.kind for flag in found] == [FlagKind.NO_IMPRESSIONS]


# --------------------------------------------------------------- nhiều hiển thị, ít click


@pytest.mark.parametrize(
    ("clicks", "impressions", "position", "flagged"),
    [
        (1, 200, 10.0, True),  # 0,5%
        (1, 199, 10.0, False),  # chưa đủ lượt hiển thị
        (1, 200, 10.1, False),  # ngoài trang 1
        (2, 200, 3.0, False),  # CTR đúng 1%
        (24, 2500, 3.0, False),  # 0,96% hiện thành 1,0%: không gắn
        (47, 5000, 3.0, True),  # 0,94% hiện thành 0,9%
        (0, 300, 10.04, True),  # vị trí hiện 10,0
    ],
)
def test_low_ctr(clicks, impressions, position, flagged):
    found = kinds(post(), at(clicks, impressions, position), None)
    assert (FlagKind.LOW_CTR in found) is flagged


def test_low_ctr_reason():
    flag = page_flags(post(), compare(at(3, 1200, 4.5), None), end=E)[0]
    assert flag.reason == "1.200 lượt hiển thị, vị trí trung bình 4,5, CTR 0,3%."
    assert "SiteSEO" in flag.hint


# --------------------------------------------------------------------- từ khóa chính chưa có


def test_main_keyword_missing_only_with_plan_keywords_and_impressions():
    planned = post(plan=plan_row("Sửa cửa sắt", status=plan_model.STATUS_PUBLISHED, wp_post_id=10))
    without_main = keyword_table([query_row(NOW, "/sua-cua-sat/", "cửa sắt giá rẻ", 1, 50)])
    with_main = keyword_table([query_row(NOW, "/sua-cua-sat/", "sua cua sat", 1, 50)])
    busy = at(20, 100, 5.0)
    assert kinds(planned, busy, None, keywords=without_main) == [FlagKind.MAIN_KEYWORD]
    assert kinds(planned, busy, None, keywords=with_main) == []
    assert kinds(planned, at(20, 99, 5.0), None, keywords=without_main) == []
    assert kinds(planned, busy, None) == []  # chưa lấy từ khóa: không kết luận
    assert kinds(post(), busy, None, keywords=without_main) == []  # không có dòng kế hoạch
    foreign = post(plan=plan_row("门窗", status=plan_model.STATUS_PUBLISHED, wp_post_id=10))
    assert kinds(foreign, busy, None, keywords=without_main) == []  # không so được: không gắn


def test_reasons_never_carry_google_or_wordpress_text():
    planned = post(plan=plan_row("Sửa cửa sắt", status=plan_model.STATUS_PUBLISHED, wp_post_id=10))
    table = keyword_table([query_row(NOW, "/sua-cua-sat/", HOSTILE, 1, 50)])
    found = page_flags(planned, compare(at(1, 300, 12.0), at(30, 300, 4.0)), end=E, keywords=table)
    assert {flag.kind for flag in found} == {
        FlagKind.RANK_DROP,
        FlagKind.LOST_CLICKS,
        FlagKind.MAIN_KEYWORD,
    }
    for flag in found:
        for text in (flag.label, flag.reason, flag.hint):
            assert "<" not in text and "evil" not in text and "javascript" not in text
            assert "sắt" not in text.lower()  # không chép tiêu đề, từ khóa chính, từ khóa Google


# -------------------------------------------------------------------- thứ tự, «Trang khác»


def test_order_follows_flag_kind_and_other_pages_get_none():
    found = kinds(post(), at(0, 300, 12.0), at(30, 300, 4.0))
    assert found == [FlagKind.RANK_DROP, FlagKind.LOST_CLICKS]
    other = TrackedPage(PageKey("/category/x"), page_label(PageKey("/category/x")), None, None, ())
    assert page_flags(other, compare(PageStats(), PageStats()), end=E) == ()
    assert page_flags(other, compare(at(0, 300, 12.0), at(30, 300, 4.0)), end=E) == ()


def test_attention_summary():
    drop = page_flags(post(), compare(at(5, 100, 9.0), at(5, 100, 4.0)), end=E)
    ghost = page_flags(post(), compare(PageStats(), PageStats()), end=E)
    rise = page_flags(post(), compare(at(5, 100, 4.0), at(5, 100, 9.0)), end=E)
    new = page_flags(post(), compare(PageStats(), PageStats()), end=E, published=E)
    counts = attention_counts([drop, drop, ghost, rise, new, ()])
    assert counts == {
        FlagKind.RANK_DROP: 2,
        FlagKind.LOST_CLICKS: 0,
        FlagKind.NO_IMPRESSIONS: 1,
        FlagKind.LOW_CTR: 0,
        FlagKind.MAIN_KEYWORD: 0,
    }
    assert set(counts) == set(ATTENTION)  # Mới đăng, Lên hạng không phải «cần chú ý»
    assert attention_text(counts) == "Cần chú ý: 2 bài tụt hạng · 1 bài chưa có lượt hiển thị"
    assert attention_text(attention_counts([rise, new])) == ""

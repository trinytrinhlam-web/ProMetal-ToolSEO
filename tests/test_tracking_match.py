"""T-123 (Thợ Máy): khớp địa chỉ trang với bài, trang WordPress và dòng kế hoạch
(``seo_app.tracking.match``; thiết kế T-120 mục 1.4).

Gồm các ca Soi Lỗi gợi ý ở thiết kế: ``%E1%BB%AD`` hoa, thường; hai dòng chỉ khác ``#…``; dòng
staging khi thuộc tính tên miền; ``bool`` thay cho số; vị trí bằng 0; click lớn hơn hiển thị; bài
đổi slug; dòng kế hoạch có slug trùng hai bài. Điều kiện Lá Chắn: LC-T120-6 (dòng ngoài website bị
bỏ dù Google trả), LC-T120-19 (đường dẫn «Trang khác» làm sạch sau khi giải mã ``%``).
"""

from __future__ import annotations

import math
import unicodedata
from datetime import date, datetime

import pytest
from test_tracking_model import SITE, Day, day_row, item, plan_row

from seo_app.plan import model as plan_model
from seo_app.tracking.match import (
    HOME_LABEL,
    LABEL_CHARS,
    MATCH_TEXT,
    build_tracking,
    match_plan,
    page_key,
    page_label,
)
from seo_app.tracking.model import DayTotal, MatchStatus, PageKey
from seo_app.wordpress.client import PublishedItem

D1, D2 = date(2026, 10, 5), date(2026, 10, 6)
PUBLISHED = plan_model.STATUS_PUBLISHED


# ------------------------------------------------------------------------------- page_key


@pytest.mark.parametrize(
    ("url", "key"),
    [
        (SITE + "/", PageKey("/")),
        (SITE + "/#lien-he", PageKey("/")),
        (SITE + "/sua-cua-sat/", PageKey("/sua-cua-sat")),
        (SITE + "/sua-cua-sat", PageKey("/sua-cua-sat")),
        (SITE + "/sua-cua-sat/#bang-gia", PageKey("/sua-cua-sat")),
        (SITE + "/s%E1%BB%ADa-c%E1%BB%ADa/", PageKey("/sửa-cửa")),  # %E1%BB%AD hoa
        (SITE + "/s%e1%bb%ada-c%e1%bb%ada/", PageKey("/sửa-cửa")),  # … và thường
        (
            SITE + "/su%CC%9B%CC%89a/",
            PageKey("/" + unicodedata.normalize("NFC", "sửa")),
        ),  # NFD → NFC
        (SITE + "/Sua-Cua/", PageKey("/Sua-Cua")),  # giữ chữ hoa
        (SITE + "/a//", PageKey("/a/")),  # chỉ bỏ một «/» cuối
        (SITE + "/?s=c%E1%BB%ADa", PageKey("/", "s=cửa")),
        (SITE + "/?p=123", PageKey("/", "p=123")),
        (SITE + "/a/?", PageKey("/a", "")),
        (SITE + "/a%3Fb/", PageKey("/a?b")),  # «?» đã mã hóa thuộc đường dẫn, không phải tham số
        (SITE + "/a%2Fb/", PageKey("/a/b")),
        (SITE + "/a?x=1#y", PageKey("/a", "x=1")),
    ],
)
def test_page_key_normalizes(url, key):
    assert page_key(url, SITE) == key


@pytest.mark.parametrize(
    "url",
    [
        "https://www.staging-m.suachuacuasat.com/sua-cua-sat/",  # staging (thuộc tính tên miền)
        "https://www.suachuacuasat.com/sua-cua-sat/",
        "http://suachuacuasat.com/sua-cua-sat/",
        "https://suachuacuasat.com.evil.example/sua-cua-sat/",
        "https://evilsuachuacuasat.com/sua-cua-sat/",
        "https://suachuacuasat.com:8443/sua-cua-sat/",
        "https://user@suachuacuasat.com/sua-cua-sat/",
        "https://SUACHUACUASAT.com/sua-cua-sat/",  # đúng tên máy nhưng sai tiền tố đã lọc ở Google
        "HTTPS://suachuacuasat.com/sua-cua-sat/",
        "https://suachuacuasat.com",  # không có «/» sau tên máy
        "https://suachuacuasat.com/a b/",
        "https://suachuacuasat.com/a\x00b/",
        "https://suachuacuasat.com/a\N{RIGHT-TO-LEFT OVERRIDE}b/",  # ký tự đảo hướng để trần
        'https://suachuacuasat.com/a"b/',
        "https://suachuacuasat.com/%E1%BB/",  # UTF-8 hỏng sau khi giải mã
        "https://suachuacuasat.com/%C3%28/",
        SITE + "/" + "a" * 2000,  # quá 2.000 ký tự
        "",
        None,
        123,
        b"https://suachuacuasat.com/a/",
    ],
)
def test_page_key_rejects_rows_outside_website(url):
    assert page_key(url, SITE) is None


def test_page_key_site_with_path_and_trailing_slash():
    blog = "https://example.com/blog"
    assert page_key("https://example.com/blog/", blog) == PageKey("/")
    assert page_key("https://example.com/blog/a/", blog + "/") == PageKey("/a")
    assert page_key("https://example.com/other/", blog) is None  # cùng tên máy, khác tiền tố
    assert page_key("https://example.com/bloga/", blog) is None
    assert page_key(SITE + "/a/", "") is None
    assert page_key(SITE + "/a/", "http://suachuacuasat.com") is None


# ------------------------------------------------------------------------------ page_label


def test_page_label_is_cleaned_plain_text():
    """LC-T120-19: giải mã ``%`` ra ký tự đảo hướng, vô hình, điều khiển: ``clean_text`` bỏ."""
    hostile = page_key(SITE + "/a%E2%80%AEb%E2%80%8Bc%00d%0Ae%E2%81%A6f/", SITE)
    assert hostile == PageKey(
        "/a\N{RIGHT-TO-LEFT OVERRIDE}b\N{ZERO WIDTH SPACE}c\x00d\ne\N{LEFT-TO-RIGHT ISOLATE}f"
    )
    label = page_label(hostile)
    assert label == "/abcd ef"
    assert not any(unicodedata.category(ch) in ("Cc", "Cf") for ch in label)
    assert page_label(PageKey("/")) == HOME_LABEL
    assert page_label(PageKey("/", "s=a")) == "/?s=a"
    long = page_label(PageKey("/" + "đ" * 300))
    assert len(long) == LABEL_CHARS and long.endswith("…")


# --------------------------------------------------------------------------- build_tracking


def test_rows_go_to_posts_pages_and_other_pages():
    items = [
        item(10, "/sua-cua-sat/", title="Sửa cửa sắt tại nhà"),
        item(20, "/sua-cua-keo-tphcm/", kind="page", title="Sửa cửa kéo TP.HCM"),
        item(11, "/cua-cuon/"),  # chưa có số liệu
    ]
    rows = [
        day_row(D1, "/sua-cua-sat/", 2, 10, 3.0),
        day_row(D1, "/sua-cua-sat/#bang-gia", 1, 5, 6.0),  # chỉ khác «#…»: cộng vào cùng ngày
        day_row(D2, "/sua-cua-sat", 0, 4, 5.0),
        day_row(D1, "/sua-cua-keo-tphcm/", 3, 30, 2.0),
        day_row(D1, "/category/cua-sat/", 0, 7, 9.0),
        day_row(D1, "/?s=cua", 0, 1, 4.0),
        day_row(D1, "/", 1, 12, 2.0),
    ]
    tracking = build_tracking(SITE, items, rows)
    assert [page.item.id for page in tracking.pages] == [10, 11, 20]  # mọi bài, trang, theo mã
    post, empty, service = tracking.pages
    assert post.label == "Sửa cửa sắt tại nhà" and post.kind == "post"
    assert post.days == (
        DayTotal(D1, 3, 15, 60.0, True),  # 2+1 click, 10+5 hiển thị, 30+30 tổng vị trí
        DayTotal(D2, 0, 4, 20.0, True),
    )
    assert empty.days == () and empty.kind == "post"
    assert service.kind == "page" and service.days == (DayTotal(D1, 3, 30, 60.0, True),)
    assert [(page.key, page.label, page.kind) for page in tracking.others] == [
        (PageKey("/"), HOME_LABEL, "other"),
        (PageKey("/", "s=cua"), "/?s=cua", "other"),
        (PageKey("/category/cua-sat"), "/category/cua-sat", "other"),
    ]
    assert tracking.skipped_rows == 0 and tracking.skipped_items == 0


def test_static_home_page_is_matched():
    tracking = build_tracking(
        SITE, [item(2, "/", kind="page", title="Trang chủ")], [day_row(D1, "/", 4, 40)]
    )
    assert tracking.pages[0].days[0].clicks == 4 and tracking.others == ()


def test_rows_outside_website_are_dropped_even_if_google_returns_them():
    """LC-T120-6: dòng staging, ``www.``, ``http://``, tên miền khác bị bỏ, đếm «dòng lạ»."""
    outside = [
        "https://www.staging-m.suachuacuasat.com/sua-cua-sat/",
        "https://www.suachuacuasat.com/sua-cua-sat/",
        "http://suachuacuasat.com/sua-cua-sat/",
        "https://suachuacuasat.com.evil.example/sua-cua-sat/",
        "https://evilsuachuacuasat.com/sua-cua-sat/",
    ]
    rows = [Day(D1, url, 5, 50, 50.0) for url in outside] + [day_row(D1, "/sua-cua-sat/", 1, 10)]
    tracking = build_tracking(SITE, [item(10, "/sua-cua-sat/")], rows)
    assert tracking.skipped_rows == len(outside)
    assert tracking.pages[0].days == (DayTotal(D1, 1, 10, 10.0, True),)
    assert tracking.others == ()


@pytest.mark.parametrize(
    "bad",
    [
        Day(D1, SITE + "/a/", True, 10, 10.0),  # bool thay cho số
        Day(D1, SITE + "/a/", 1, True, 1.0),
        Day(D1, SITE + "/a/", 1.0, 10, 10.0),  # số thực ở chỗ số nguyên
        Day(D1, SITE + "/a/", 1, 10.0, 10.0),
        Day(D1, SITE + "/a/", 11, 10, 10.0),  # click lớn hơn hiển thị
        Day(D1, SITE + "/a/", -1, 10, 10.0),
        Day(D1, SITE + "/a/", 0, 0, 0.0),  # 0 lượt hiển thị
        Day(D1, SITE + "/a/", 0, 10, 0.0),  # vị trí 0
        Day(D1, SITE + "/a/", 0, 10, 9.99),  # vị trí dưới 1
        Day(D1, SITE + "/a/", 0, 10, 100_001.0),  # vị trí trên 10.000
        Day(D1, SITE + "/a/", 0, 10, math.nan),
        Day(D1, SITE + "/a/", 0, 10, math.inf),
        Day(D1, SITE + "/a/", 0, 10, True),
        Day(D1, SITE + "/a/", 0, 10, "10"),
        Day(D1, SITE + "/a/", 0, 10**9 + 1, 10.0**9 + 1),  # quá trần một dòng
        Day(D1, SITE + "/a/", 1, 10, 10.0, final=1),  # final không phải bool
        Day(datetime(2026, 10, 5), SITE + "/a/", 1, 10, 10.0),  # datetime thay cho ngày
        Day(date(1999, 12, 31), SITE + "/a/", 1, 10, 10.0),
        Day(date(9999, 12, 31), SITE + "/a/", 1, 10, 10.0),
        Day("2026-10-05", SITE + "/a/", 1, 10, 10.0),
        Day(D1, None, 1, 10, 10.0),
    ],
)
def test_bad_rows_are_skipped_and_counted(bad):
    tracking = build_tracking(SITE, [item(1, "/a/")], [bad, day_row(D2, "/a/", 1, 10)])
    assert tracking.skipped_rows == 1
    assert tracking.pages[0].days == (DayTotal(D2, 1, 10, 10.0, True),)


def test_provisional_flag_is_kept_per_day():
    rows = [day_row(D1, "/a/", 1, 10), day_row(D2, "/a/", 2, 20, final=False)]
    days = build_tracking(SITE, [item(1, "/a/")], rows).pages[0].days
    assert [day.final for day in days] == [True, False]


def test_items_without_usable_key_are_skipped():
    items = [
        item(1, "/a/"),
        item(2, "/?p=2", slug="p-2"),  # địa chỉ có tham số: không gán bài
        item(3, "/a"),  # trùng khóa với bài 1: mã nhỏ hơn giữ khóa
        PublishedItem(id=4, type="post", slug="x", link="https://other.example/x/", title="X"),
    ]
    tracking = build_tracking(SITE, items, [day_row(D1, "/a/", 1, 10)])
    assert [page.item.id for page in tracking.pages] == [1]
    assert tracking.pages[0].days[0].clicks == 1
    assert tracking.skipped_items == 3


def test_renamed_slug_old_address_goes_to_other_pages():
    """Bài đổi slug: số liệu cũ nằm ở địa chỉ cũ («Trang khác»); bài chỉ nhận số ở địa chỉ mới.
    Dòng kế hoạch có mã bài vẫn nối; dòng chỉ có slug cũ thì không thấy."""
    post = item(10, "/sua-cua-sat-gia-re/", slug="sua-cua-sat-gia-re")
    rows = [day_row(D1, "/sua-cua-sat/", 5, 50), day_row(D2, "/sua-cua-sat-gia-re/", 1, 8)]
    by_id = plan_row(key="B-001", status=PUBLISHED, wp_post_id=10, slug="sua-cua-sat")
    by_old_slug = plan_row("cửa sắt giá rẻ", key="B-002", status=PUBLISHED, slug="sua-cua-sat")
    tracking = build_tracking(SITE, [post], rows, [by_id, by_old_slug])
    assert tracking.pages[0].days == (DayTotal(D2, 1, 8, 8.0, True),)
    assert tracking.pages[0].plan == by_id
    assert [(page.label, page.days[0].clicks) for page in tracking.others] == [("/sua-cua-sat", 5)]
    assert [match.status for match in tracking.plan] == [MatchStatus.BY_ID, MatchStatus.NOT_FOUND]


# ------------------------------------------------------------------------------- match_plan


def _statuses(rows, items):
    return [
        (match.status, match.item.id if match.item else None) for match in match_plan(rows, items)
    ]


def test_match_plan_by_id_status_and_slug():
    posts = [item(10, "/sua-cua-sat/"), item(11, "/cua-cuon/"), item(20, "/dich-vu/", kind="page")]
    rows = [
        plan_row(key="B-001", status=PUBLISHED, wp_post_id=10),
        # Sheet chưa cập nhật «Đã đăng» mà bài đã có trong danh sách đã đăng: vẫn khớp theo mã.
        plan_row(key="B-002", status=plan_model.STATUS_SCHEDULED, wp_post_id=11),
        plan_row(key="B-003", status=plan_model.STATUS_NEW, slug="sua-cua-sat"),
        plan_row(key="B-004", status=plan_model.STATUS_WRITING),
        plan_row(key="B-005", status=plan_model.STATUS_DRAFT_SENT, wp_post_id=99),
        plan_row(key="B-006", status=plan_model.STATUS_SCHEDULED, wp_post_id=98),
        plan_row(key="B-007", status=PUBLISHED, wp_post_id=97),  # mã không có trong danh sách
        plan_row(key="B-008", status=PUBLISHED),  # không mã, không slug
        plan_row(key="B-009", status=plan_model.STATUS_DROPPED, wp_post_id=10),
        plan_row(key="B-010", status=PUBLISHED, wp_post_id=20),  # mã của trang, không phải bài
    ]
    assert _statuses(rows, posts) == [
        (MatchStatus.BY_ID, 10),
        (MatchStatus.BY_ID, 11),
        (MatchStatus.NOT_LIVE, None),  # chưa viết: không dùng slug dù trùng bài cũ
        (MatchStatus.NOT_LIVE, None),
        (MatchStatus.NOT_LIVE, None),
        (MatchStatus.NOT_LIVE, None),
        (MatchStatus.NOT_FOUND, None),
        (MatchStatus.NOT_FOUND, None),
        (MatchStatus.DROPPED, None),
        (MatchStatus.NOT_FOUND, None),
    ]


def test_match_plan_slug_needs_exactly_one_post():
    posts = [
        item(10, "/sua-cua-sat/"),
        item(30, "/cua-sat/sua-cua/", slug="sua-cua"),  # cùng slug, khác chuyên mục
        item(31, "/cua-nhom/sua-cua/", slug="sua-cua"),
        item(40, "/sua-cong/", kind="page"),
    ]
    rows = [
        plan_row(key="B-001", status=PUBLISHED, slug="sua-cua-sat"),
        plan_row(key="B-002", status=PUBLISHED, slug="sua-cua"),  # slug trùng hai bài
        plan_row(key="B-003", status=PUBLISHED, slug="sua-cong"),  # chỉ trùng trang, không phải bài
        plan_row(key="B-004", status=PUBLISHED, slug="khong-co"),
    ]
    assert _statuses(rows, posts) == [
        (MatchStatus.BY_SLUG, 10),
        (MatchStatus.AMBIGUOUS, None),
        (MatchStatus.NOT_FOUND, None),
        (MatchStatus.NOT_FOUND, None),
    ]


def test_match_plan_one_post_one_row():
    posts = [item(10, "/a/"), item(11, "/b/"), item(12, "/c/")]
    rows = [
        plan_row(key="B-001", status=PUBLISHED, wp_post_id=10),
        plan_row(key="B-002", status=PUBLISHED, wp_post_id=10),  # hai dòng cùng mã: không đoán
        plan_row(key="B-003", status=PUBLISHED, wp_post_id=11),
        plan_row(key="B-004", status=PUBLISHED, slug="b"),  # slug của bài đã có dòng khớp mã
        plan_row(key="B-005", status=PUBLISHED, slug="c"),
        plan_row(key="B-006", status=PUBLISHED, slug="c"),  # hai dòng cùng slug
    ]
    assert _statuses(rows, posts) == [
        (MatchStatus.DUPLICATE, None),
        (MatchStatus.DUPLICATE, None),
        (MatchStatus.BY_ID, 11),  # dòng khớp mã giữ bài
        (MatchStatus.DUPLICATE, None),
        (MatchStatus.DUPLICATE, None),
        (MatchStatus.DUPLICATE, None),
    ]
    tracking = build_tracking(SITE, posts, [], rows)
    assert [page.plan.key if page.plan else None for page in tracking.pages] == [
        None,
        "B-003",
        None,
    ]


def test_match_text_covers_every_status():
    assert set(MATCH_TEXT) == set(MatchStatus)
    assert MATCH_TEXT[MatchStatus.NOT_LIVE] == "Chưa lên website"

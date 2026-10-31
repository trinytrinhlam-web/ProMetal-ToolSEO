"""Lá Chắn T-113 (rút gọn): nút «Cập nhật trạng thái từ website» ở trang Kế hoạch.

LC-T113-1 (Thấp): website trả ``date_gmt`` đúng khuôn ``YYYY-MM-DDTHH:MM:SS`` nhưng ở cuối năm
9999 (từ ``9999-12-31T17:00:00`` giờ UTC). Đổi sang giờ Việt Nam (+07) là sang năm 10000, nên
``_due_of`` của lõi T-109 ném ``OverflowError`` (không phải ``ValueError``): nút đọc hiện lỗi Python
kèm traceback thay vì câu cố định, cả lần kiểm hỏng; không ghi gì. Hợp đồng của lõi với ngày website
lạ (test T-109 ``test_odd_website_date_changes_status_but_not_date``): vẫn đề xuất đổi Trạng thái,
không đổi ngày, cảnh báo ``ODD_DATE``. Mốc ``9999-12-31T16:59:59`` hôm nay đã đúng: ca đối chứng.

Không gọi Google, WordPress thật: Google Sheets giả qua ``SheetsClient`` thật, WordPress giả đếm
request (fixture của T-101, T-109, T-113); cache ở thư mục tạm.
"""

from __future__ import annotations

import pytest
import test_t101_plan_page as t101
import test_t109_website_status as t109
import test_t113_website_status as t113
from fake_plan_sheet import FakePlanSheet
from test_plan_sync import row

from seo_app.plan.website import WebChangeKind as Kind
from seo_app.plan.website import WebNoticeKind as Notice

env = t101.env
caches = t101.caches
private_key = t101.private_key
google = t101.google
wordpress = t101.wordpress
fake = t109.fake
client = t109.client

EDGE_OK = "9999-12-31T16:59:59"  # sang +07 vẫn là năm 9999: lõi báo ngày lạ đúng (đối chứng)
OVERFLOW = ("9999-12-31T17:00:00", "9999-12-31T23:59:59")  # sang +07 là năm 10000: tràn
DATES = [EDGE_OK, *OVERFLOW]


@pytest.mark.parametrize("date_gmt", DATES)
def test_core_far_future_website_date_is_odd_date_not_overflow(fake, client, date_gmt):
    """Lõi ``check_website``: ngày website ngoài khoảng năm của kế hoạch là ngày lạ, kể cả khi đổi
    múi giờ bị tràn: đề xuất đổi Trạng thái, không đổi ngày, cảnh báo ``ODD_DATE``."""
    FakePlanSheet(fake, t109.rows(row("B-041", "cửa cuốn", status="Đã gửi nháp", wp_post_id=131)))
    result = t109.check(client, {131: t109.state(131, "future", date_gmt)})
    (update,) = result.updates
    assert update.kind is Kind.SCHEDULED and update.fields == ("status",)
    assert update.published_after is None
    assert t109.only(result, Notice.ODD_DATE).wp_post_id == 131
    assert not result.late


@pytest.mark.parametrize("date_gmt", DATES)
def test_far_future_website_date_on_page_is_fixed_text(project_root, google, wordpress, date_gmt):
    """Qua trang Kế hoạch: website trả bài 501 «đã đăng» với ngày cuối năm 9999. Không lỗi Python
    (traceback) trên trang, chữ thuần, không ghi Sheet, chỉ lệnh GET tới WordPress. Sửa ở lõi: bài
    501 chỉ được đề xuất đổi Trạng thái, có cảnh báo ngày lạ; sửa ở giao diện: câu lỗi cố định."""
    answer = t113.site_answer()
    answer[0] = {**answer[0], "date_gmt": date_gmt}  # bài 501 (dòng B-003)
    at, sheet = t113.read_website(project_root, google, wordpress, answer)
    t101.assert_plain(at)  # gồm: không có ``at.exception``
    assert sheet.updates == [] and sheet.appends == [] and sheet.structure == []
    assert {request.method for request in wordpress.requests} == {"GET"}
    if "plan_webcheck" in at.session_state:
        check = at.session_state["plan_webcheck"]
        assert all(u.published_after is None for u in check.updates if u.wp_post_id == 501)
        assert any(n.kind is Notice.ODD_DATE and n.wp_post_id == 501 for n in check.notices)
    else:
        assert at.error

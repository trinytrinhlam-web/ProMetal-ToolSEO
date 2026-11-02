"""Lá Chắn T-113 (rút gọn): nút «Cập nhật trạng thái từ website» ở trang Kế hoạch.

LC-T113-1 (Thấp, đã sửa ở ``c1852c0``): website trả ``date_gmt`` đúng khuôn ``YYYY-MM-DDTHH:MM:SS``
nhưng ở cuối năm 9999 (từ ``9999-12-31T17:00:00`` giờ UTC). Đổi sang giờ Việt Nam (+07) là sang năm
10000, nên ``_due_of`` của lõi T-109 từng ném ``OverflowError``: nút đọc hiện lỗi Python kèm
traceback thay vì câu cố định. Hợp đồng của lõi với ngày website lạ (test T-109
``test_odd_website_date_changes_status_but_not_date``): vẫn đề xuất đổi Trạng thái, không đổi ngày,
cảnh báo ``ODD_DATE``. Mốc ``9999-12-31T16:59:59`` là ca đối chứng.

LC-T113-2 (Thấp, có từ trước: ``site_index`` T-037, ``plan_cache`` T-100): ô ``fetched_at`` của
``data/plan_cache.sqlite``, ``data/site_index.sqlite`` bị sửa tay thành giờ đổi múi giờ bị tràn
(``9999-12-31T17:00:00+00:00``, ``0001-01-01T00:00:00+05:00``…): ``_parse_time`` gọi ``astimezone``
ngoài khối ``try``, ``load()`` ném ``OverflowError`` dù hứa «hỏng hay lạ: None, không ném lỗi»
(LC-T094-29) và không bỏ file, nên trang Bài viết, trang Kế hoạch lỗi mỗi lần mở.

Không gọi Google, WordPress thật: Google Sheets giả qua ``SheetsClient`` thật, WordPress giả đếm
request (fixture của T-101, T-109, T-113); cache ở thư mục tạm.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import pytest
import test_t101_home_page as t101_home
import test_t101_plan_page as t101
import test_t109_website_status as t109
import test_t113_website_status as t113
from fake_google import SHEET_ID
from fake_plan_sheet import FakePlanSheet
from test_plan_sync import row

from seo_app.config import load_settings
from seo_app.plan import model
from seo_app.plan.website import WebChangeKind as Kind
from seo_app.plan.website import WebNoticeKind as Notice
from seo_app.storage import plan_cache
from seo_app.storage import site_index as site_storage
from seo_app.wordpress import WordPressClient

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


# ======================================== LC-T113-2 (giờ tải trong cache trên máy bị sửa tay)

CACHE_TIME_OK = "9999-12-31T16:59:59+00:00"  # đổi sang +07 vẫn được: kho đọc như cũ (đối chứng)
CACHE_TIME_BAD = (
    "9999-12-31T17:00:00+00:00",  # sang +07 là năm 10000
    "9999-12-31T23:59:59-05:00",  # tính ra UTC đã là năm 10000
    "0001-01-01T00:00:00+05:00",  # tính ra UTC là năm 0
)
CACHE_TIMES = [CACHE_TIME_OK, *CACHE_TIME_BAD]
SITE = "https://vi-du.test"


def set_fetched_at(path: Path, value: str) -> None:
    """Sửa tay ô ``fetched_at`` của file cache (như người có quyền vào máy)."""
    conn = sqlite3.connect(path)
    try:
        with conn:
            conn.execute("UPDATE info SET value = ? WHERE key = 'fetched_at'", (value,))
    finally:
        conn.close()


def saved_plan_cache(path: Path | None = None) -> plan_cache.PlanCacheStore:
    store = plan_cache.PlanCacheStore(path=path or plan_cache.DEFAULT_PLAN_CACHE_FILE)
    store.save(SHEET_ID, t113.ROWS, datetime.now(model.TIMEZONE))
    return store


def saved_site_index(site: str, path: Path | None = None) -> site_storage.SiteIndexStore:
    store = site_storage.SiteIndexStore(path=path or site_storage.DEFAULT_SITE_INDEX_FILE)
    store.save(site_storage.SiteIndex(site=site, fetched_at=datetime.now(model.TIMEZONE), items=()))
    return store


@pytest.mark.parametrize("value", CACHE_TIMES)
def test_plan_cache_odd_fetch_time_never_raises(tmp_path, value):
    """``PlanCacheStore.load``: giờ tải đổi múi giờ được thì đọc như cũ; tràn thì bỏ cache
    (``None``), lần ghi sau vẫn được; không lọt ``OverflowError``."""
    store = saved_plan_cache(tmp_path / "plan_cache.sqlite")
    set_fetched_at(store.path, value)
    if value == CACHE_TIME_OK:
        assert store.load(SHEET_ID) is not None
        return
    assert store.load(SHEET_ID) is None
    saved_plan_cache(store.path)
    assert store.load(SHEET_ID) is not None


@pytest.mark.parametrize("value", CACHE_TIMES)
def test_site_index_odd_fetch_time_never_raises(tmp_path, value):
    """``SiteIndexStore.load``: như trên cho cache bài đã đăng."""
    store = saved_site_index(SITE, tmp_path / "site_index.sqlite")
    set_fetched_at(store.path, value)
    if value == CACHE_TIME_OK:
        assert store.load(SITE) is not None
        return
    assert store.load(SITE) is None
    saved_site_index(SITE, store.path)
    assert store.load(SITE) is not None


PAGE_TIMES = [CACHE_TIME_OK, CACHE_TIME_BAD[0]]


@pytest.mark.parametrize("value", PAGE_TIMES)
def test_home_page_opens_with_odd_plan_cache_time(project_root, google, value):
    """Trang Bài viết (trang đầu sau đăng nhập) đọc ``data/plan_cache.sqlite`` khi mở: giờ tải sửa
    tay không làm trang hiện lỗi Python."""
    set_fetched_at(saved_plan_cache().path, value)
    at = t101_home.open_home(project_root)
    assert not at.exception, at.exception


@pytest.mark.parametrize("value", PAGE_TIMES)
@pytest.mark.parametrize("cache", ["plan_cache", "site_index"])
def test_plan_page_opens_with_odd_cache_time(project_root, google, wordpress, cache, value):
    """Trang Kế hoạch đọc cache kế hoạch và cache bài đã đăng khi mở: giờ tải sửa tay không làm
    trang hiện lỗi Python (kế hoạch đọc lại từ Google Sheets giả)."""
    t113.setup(google, wordpress)
    if cache == "plan_cache":
        path = saved_plan_cache().path
    else:
        path = saved_site_index(WordPressClient.from_settings(load_settings()).base_url).path
    set_fetched_at(path, value)
    at = t113.open_plan(project_root)
    t101.assert_plain(at)

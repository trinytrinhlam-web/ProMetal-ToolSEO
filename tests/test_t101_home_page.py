"""Trang Bài viết (T-101; thiết kế T-094 mục 1.6, 1.8; LC-T094-3, -35).

«Tiếp theo trong kế hoạch» đọc cache kế hoạch trên máy (mở trang không gọi Google); «Bắt đầu» chỉ
mở Soạn bài (không gửi gì lên WordPress); «Đã gửi WordPress» lấy mã bài từ kho nháp và cột Mã bài
WordPress, trạng thái website chỉ hỏi khi bấm (chỉ đọc). Google, WordPress giả; không mạng thật.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
import test_t101_plan_page as plan_page
from fake_google import SHEET_ID
from fake_plan_sheet import HEADER, FakePlanSheet
from streamlit.testing.v1 import AppTest

import seo_app.storage.drafts as drafts
from seo_app.plan import model
from seo_app.storage import plan_cache
from seo_app.storage.drafts import DraftSnapshot, DraftStore, SendState

env = plan_page.env
caches = plan_page.caches
private_key = plan_page.private_key
google = plan_page.google
wordpress = plan_page.wordpress
run = plan_page.run
click = plan_page.click
row = plan_page.row
HOSTILE = plan_page.HOSTILE
RLO = plan_page.RLO
NOW = datetime(2026, 10, 30, 9, 0, tzinfo=UTC)

VALUES = [
    HEADER,
    row("B-001", "sửa cửa cuốn kêu to", day=date(2027, 12, 5)),
    row("B-002", "sơn lại cổng sắt", day=date(2027, 11, 20), **{"Ý định": "Tìm hiểu"}),
    row("B-003", "cửa kéo bị kẹt ray", status="Đã gửi nháp", **{"Mã bài WordPress": 501}),
    row("B-004", "lan can kính cường lực", day=None),
    row("B-005", "cổng xếp inox", day=date(2027, 11, 25)),
]


def save_cache(values=VALUES) -> None:
    store = plan_cache.PlanCacheStore(path=plan_cache.DEFAULT_PLAN_CACHE_FILE)
    store.save(SHEET_ID, values, datetime.now(UTC))


def open_home(project_root) -> AppTest:
    return plan_page.pages.open_page(project_root, "home.py")


def test_without_plan_shows_hint(project_root):
    at = open_home(project_root)
    assert any("trang Kế hoạch" in c.value for c in at.caption)
    assert any("Chưa có bài nào phần mềm đã gửi" in c.value for c in at.caption)


def test_typed_keyword_still_starts_new_article(project_root):
    """Ô «Từ khóa» và nút «Bắt đầu» đầu tiên của «Viết bài mới» giữ như cũ (test T-056 dựa vào)."""
    at = open_home(project_root)
    at.text_input[0].input("lan can cầu thang")
    next(b for b in at.button if b.label == "Bắt đầu").click()
    run(at)
    assert at.session_state["keyword"] == "lan can cầu thang"


def test_upcoming_from_cache_sorted_without_google_call(project_root, google):
    """3 bài «Chưa viết» gần nhất từ cache (chưa có ngày xếp cuối); mở trang không gọi Google."""
    save_cache()
    at = open_home(project_root)
    starts = [b.key for b in at.button if (b.key or "").startswith("start-")]
    assert starts == ["start-B-002", "start-B-005", "start-B-001"]
    assert google.requests == []


def test_upcoming_text_is_plain(project_root, google):
    values = [HEADER, row("B-001", "sửa cửa cuốn", **{"Ý định": "Tìm hiểu"})]
    values[1][HEADER.index("Từ khóa chính")] = "sửa cửa [x](javascript:alert(1)) <b>đậm</b>"
    values[1][HEADER.index("Ý định")] = "Tìm hiểu"
    save_cache(values)
    at = open_home(project_root)
    assert at.button(key="start-B-001")  # dòng có chữ lạ vẫn hiện
    plan_page.assert_plain(at_without_demo_cards(at))
    assert any("javascript" in m.value for m in at.markdown)  # chữ vẫn hiện, đã escape


def at_without_demo_cards(at: AppTest) -> AppTest:
    """Khung «Đang viết» (bản demo) dùng HTML cố định đã escape; bộ kiểm chữ thuần bỏ qua khung đó
    bằng cách chỉ xét phần tử không có ``allow_html`` (chữ cố định của demo)."""

    class View:
        exception = at.exception

        def __getattr__(self, kind):
            return [el for el in getattr(at, kind) if not getattr(el.proto, "allow_html", False)]

    return View()


def test_start_from_plan_row_opens_compose_without_wordpress(
    project_root, google, wordpress, monkeypatch
):
    """«Bắt đầu» trên dòng kế hoạch: đọc lại đúng dòng trên Sheet, mở Soạn bài; 0 request
    WordPress (LC-T094-35). Trang Bài viết tự nó chỉ đọc Sheet.

    Sau khi gộp T-102 (R5, Chỉ Huy B duyệt 30/10 19:05): trang Soạn bài ghi «Đang viết» đúng một
    lần qua ``record_status`` (trước đó Sheet chưa có lệnh ghi nào), bỏ ``_start_plan_key``."""
    save_cache()
    sheet = FakePlanSheet(google, [list(line) for line in VALUES])
    writes = plan_page.status_writes(monkeypatch, sheet)
    at = open_home(project_root)
    click(at, "start-B-002")
    assert sheet.reads == 3  # trang Bài viết, trang Soạn bài, ``write_status`` trước khi ghi
    assert at.session_state["keyword"] == "sơn lại cổng sắt"
    assert "_start_plan_key" not in at.session_state
    assert at.session_state["_plan_ref"].key == "B-002"
    assert wordpress.requests == []
    assert writes == [(model.STATUS_WRITING, 0, 0, 0)]
    assert len(sheet.updates) == 1 and sheet.appends == [] and sheet.structure == []
    assert sheet.cell(3, HEADER.index("Trạng thái")) == model.STATUS_WRITING


def test_typed_keyword_never_takes_a_stale_plan_row(project_root, google, wordpress, monkeypatch):
    """G1 Soi Lỗi T-101: Mã bài của một lần bấm cũ còn sót trong phiên (lần chạy mở Soạn bài bị
    ngắt) không bao giờ gắn vào bài gõ tay: không ``DraftPlanRef``, không đọc, không ghi Sheet,
    từ khóa đúng như đã gõ."""
    save_cache()
    sheet = FakePlanSheet(google, [list(line) for line in VALUES])
    writes = plan_page.status_writes(monkeypatch, sheet)
    at = open_home(project_root)
    at.session_state["_start_plan_key"] = "B-002"  # sót lại từ lần bấm «Bắt đầu» trước
    at.text_input[0].input("lan can cầu thang")
    next(b for b in at.button if b.label == "Bắt đầu").click()
    run(at)
    assert at.session_state["keyword"] == "lan can cầu thang"
    assert "_start_plan_key" not in at.session_state and "_plan_ref" not in at.session_state
    assert sheet.reads == 0 and sheet.updates == [] and writes == []
    assert wordpress.requests == []


def test_pick_from_plan_in_new_article_popover(project_root, google):
    save_cache()
    FakePlanSheet(google, [list(line) for line in VALUES])
    at = open_home(project_root)
    at.selectbox[0].select("B-005")
    run(at)
    next(b for b in at.button if b.label == "Bắt đầu").click()
    run(at)
    assert at.session_state["keyword"] == "cổng xếp inox"


def test_sent_list_from_drafts_and_plan_then_website_read_only(project_root, google, wordpress):
    """«Đã gửi WordPress»: mã bài từ kho nháp (trạng thái gửi) và cột Mã bài WordPress; hỏi
    website chỉ khi bấm, chỉ đọc (GET), «Lỡ lịch» khi hẹn giờ quá giờ."""
    save_cache()
    store = DraftStore(drafts.DEFAULT_DRAFTS_FILE)
    saved = store.save(DraftSnapshot(keyword="cửa sắt mỹ thuật", article_title=HOSTILE))
    store.save_send_state(saved.id, SendState(post_id=777, updated_at=NOW))
    late = (datetime.now(UTC) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    wordpress.on(
        "GET",
        "/wp-json/wp/v2/posts",
        [
            {"id": 777, "status": "publish", "date_gmt": "", "modified_gmt": "", "link": ""},
            {"id": 501, "status": "future", "date_gmt": late, "modified_gmt": "", "link": ""},
        ],
    )
    at = open_home(project_root)
    shown = "\n".join(m.value for m in at.markdown)
    assert "\\#777" in shown or "#777" in shown
    assert "#501" in shown
    assert RLO not in shown and "](javascript" not in shown
    assert wordpress.requests == []
    click(at, "home-web")
    shown = "\n".join(m.value for m in at.markdown)
    assert "Đã đăng" in shown and "Lỡ lịch" in shown
    assert {r.method for r in wordpress.requests} == {"GET"}


@pytest.mark.parametrize("status", ["Đang viết", "Bỏ", "Đã đăng"])
def test_only_not_started_rows_are_upcoming(project_root, status):
    save_cache([HEADER, row("B-001", "sửa cửa cuốn", status=status)])
    at = open_home(project_root)
    assert not [b for b in at.button if (b.key or "").startswith("start-")]


@pytest.mark.parametrize("view", ["home.py", "plan.py"])
def test_corrupt_drafts_file_is_left_for_compose_page(project_root, view):
    """File nháp hỏng: trang Bài viết, Kế hoạch không mở kho (không cất file lặng lẽ), để trang
    Soạn bài cất file và báo cho người dùng (``test_app_drafts.py``)."""
    save_cache()
    path = drafts.DEFAULT_DRAFTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"day khong phai sqlite")
    at = plan_page.pages.open_page(project_root, view)
    assert path.read_bytes() == b"day khong phai sqlite"
    run(at.switch_page("views/write.py"))
    assert any("cất sang một bên" in w.value for w in at.warning)


def test_missing_drafts_file_is_not_created(project_root):
    path = drafts.DEFAULT_DRAFTS_FILE
    assert not path.exists()
    open_home(project_root)
    assert not path.exists()


@pytest.mark.parametrize("view", ["home.py", "plan.py"])
def test_opening_page_does_not_create_plan_cache(project_root, monkeypatch, view):
    """Đã khai báo Sheet nhưng chưa đọc được Google (file khóa không có), chưa có bản lưu: mở trang
    không tạo file cache kế hoạch (test cũ khai báo Sheet trong ``.env`` không ghi vào
    ``data/``)."""
    missing_key = f"{plan_cache.DEFAULT_PLAN_CACHE_FILE}.khong-co.json"
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", missing_key)
    at = plan_page.pages.open_page(project_root, view)
    assert not at.exception, at.exception
    assert not plan_cache.DEFAULT_PLAN_CACHE_FILE.exists()

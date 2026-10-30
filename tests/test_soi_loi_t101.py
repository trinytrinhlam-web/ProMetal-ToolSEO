"""Soi Lỗi T-101 (rút gọn): trang Kế hoạch, Cài đặt → Google, trang Bài viết chạy thật.

Kiểm độc lập với test của Họa Sĩ, cùng bộ giả (``FakeGoogle`` + ``FakePlanSheet`` đi qua
``SheetsClient`` thật, ``FakeWordPress``, AI giả); cache kế hoạch, cache bài đã đăng, kho nháp ở thư
mục tạm. Không gọi Google, WordPress, AI thật.

Trọng tâm: «Áp dụng» chỉ ghi qua đường T-100 (hai tab, bấm lại, lệnh thêm «chưa rõ», Sheet đổi giữa
chừng); chỉ mở trang hay chạy lại trang thì không gọi mạng, không gọi AI, không tạo file; chữ lấy từ
Google (tên Sheet) hiện thuần.
"""

from __future__ import annotations

import requests
import test_t101_plan_page as plan_page
import test_t101_settings_google as settings_page
from fake_plan_sheet import HEADER, INFO_URL, READ_URL

import seo_app.storage.drafts as drafts
from seo_app.storage import plan_cache
from seo_app.storage import site_index as site_storage

env = plan_page.env
caches = plan_page.caches
private_key = plan_page.private_key
google = plan_page.google
sheet = plan_page.sheet
wordpress = plan_page.wordpress
plan_ai = plan_page.plan_ai
env_path = settings_page.env_path
open_plan = plan_page.open_plan
paste = plan_page.paste
click = plan_page.click
run = plan_page.run
frame = plan_page.frame
texts = plan_page.texts
assert_plain = plan_page.assert_plain
suggestion = plan_page.suggestion
RLO, ZWSP, HOSTILE = plan_page.RLO, plan_page.ZWSP, plan_page.HOSTILE
NEW_ROW = "Từ khóa chính\tNgày dự kiến\nsửa cửa kéo đài loan\t20/11/2027\n"


def keyword_rows(sheet, keyword: str) -> list[int]:
    column = HEADER.index("Từ khóa chính")
    return [n for n in range(1, len(sheet.grid) + 1) if sheet.cell(n, column) == keyword]


# ======================================================= «Áp dụng»: chỉ qua đường T-100


def test_two_tabs_apply_the_same_new_row_only_once(project_root, sheet):
    """Hai tab cùng đề xuất thêm một bài (cùng Mã bài B-004) rồi lần lượt «Áp dụng»: tab đầu thêm
    dòng, tab sau là xung đột «đã có», không thêm dòng trùng."""
    first = open_plan(project_root)
    second = open_plan(project_root)
    for tab in (first, second):
        paste(tab, NEW_ROW)
        (item,) = tab.session_state["plan_proposals"].items
        assert (item.action.value, item.key) == ("Thêm", "B-004")
    click(first, "plan-apply")
    click(second, "plan-apply")
    assert len(sheet.appends) == 1
    assert keyword_rows(sheet, "sửa cửa kéo đài loan") == [5]
    assert any("chưa ghi" in w.value for w in second.warning)
    assert "B-004" in frame(second, "Vì sao chưa ghi").to_string()
    assert_plain(second)


def test_apply_once_then_reruns_never_write_again(project_root, sheet):
    """Sau «Áp dụng», bộ đề xuất bị bỏ: nút không còn, chạy lại trang không ghi thêm lần nào."""
    at = open_plan(project_root)
    paste(at, NEW_ROW)
    click(at, "plan-apply")
    assert len(sheet.appends) == 1
    assert not [b for b in at.button if b.key == "plan-apply"]
    run(at)
    run(at)
    assert len(sheet.appends) == 1 and sheet.updates == []


def test_unsure_append_then_read_again_adds_nothing(project_root, sheet, google):
    """Lệnh thêm dòng đứt sau khi Google đã thêm, đọc lại cũng lỗi: trang báo «chưa rõ», bảo «Tải
    lại», bỏ bộ đề xuất (không áp dụng lại được). Đọc lại cùng bảng dán: không đề xuất «Thêm» nữa,
    Sheet có đúng một dòng."""
    at = open_plan(project_root)
    reads = []
    real_read = google.routes[("GET", READ_URL)]

    def read(request):
        reads.append(1)
        if len(reads) == 2:  # lần đọc lại ngay sau lệnh thêm lỗi (``_key_present``)
            return (500, {"error": {"message": "MOI-lan-doc-lai"}}, {})
        return real_read(request)

    paste(at, NEW_ROW)
    google.on("GET", READ_URL, read)  # lần đọc 1: ``apply_proposals`` đọc lại trước khi ghi
    sheet.fail("append", requests.exceptions.ConnectionError("đứt"), apply=True)
    click(at, "plan-apply")
    shown = texts(at)
    assert "chưa rõ" in shown and "Tải lại" in shown and "MOI" not in shown
    assert "plan_proposals" not in at.session_state
    assert not [b for b in at.button if b.key == "plan-apply"]
    paste(at, NEW_ROW)
    assert "plan_proposals" not in at.session_state  # không còn gì để thêm
    assert any("Không có thay đổi" in i.value for i in at.info)
    assert len(sheet.appends) == 1
    assert keyword_rows(sheet, "sửa cửa kéo đài loan") == [5]


def test_row_deleted_on_sheet_before_apply_is_not_written_back(project_root, sheet):
    """Sau khi xem đề xuất, dòng B-001 bị xóa trên Google Sheets: «Áp dụng» không ghi, không thêm
    lại dòng; bảng xung đột ghi «(không thấy)»."""
    at = open_plan(project_root)
    paste(at, "Mã bài\tTừ khóa chính\tƯu tiên\nB-001\tsửa cửa cuốn kêu to\tCao\n")
    del sheet.grid[1]  # máy kia xóa dòng B-001
    click(at, "plan-apply")
    assert sheet.updates == [] and sheet.appends == []
    line = frame(at, "Bây giờ trên Sheet").iloc[0]
    assert line["Bây giờ trên Sheet"] == "(không thấy)" and line["Đề xuất"] == "Cao"
    assert_plain(at)


# ============================================== mở trang, chạy lại trang: không gọi gì


def test_reruns_with_fresh_cache_call_nothing(project_root, sheet, wordpress, plan_ai):
    """Trang Kế hoạch đã mở (đọc Sheet một lần): tick, bỏ tick, xem đủ đề xuất, đổi tab nguồn,
    chạy lại trang: không lệnh Google, WordPress nào, không gọi AI."""
    ai = plan_ai([suggestion("them", keyword="sửa cửa kéo")])
    at = open_plan(project_root)
    paste(at, NEW_ROW + "cửa nhôm xingfa\t21/11/2027\n")
    google_calls = len(plan_page.sheet_google(sheet).requests)
    wordpress_calls = len(wordpress.requests)
    round_ = at.session_state["plan_round"]
    at.checkbox(key=f"plan-pick-{round_}-1").uncheck()
    run(at)
    at.checkbox(key=f"plan-pick-{round_}-1").check()
    run(at)
    at.selectbox(key=f"plan-detail-{round_}").select(1)
    run(at)
    at.session_state["plan_source"] = "Google Sheets"
    run(at)
    run(at)
    assert len(plan_page.sheet_google(sheet).requests) == google_calls
    assert len(wordpress.requests) == wordpress_calls
    assert ai.prompts == []
    assert sheet.appends == [] and sheet.updates == []


def test_home_page_opens_without_network_or_new_files(project_root, google, wordpress):
    """Trang mở đầu (Bài viết), đã khai báo Google và WordPress, chưa có bản lưu nào: không lệnh
    Google, WordPress nào; không tạo file cache kế hoạch, cache bài, kho nháp."""
    plan_page.FakePlanSheet(google, [list(line) for line in plan_page.ROWS])
    at = plan_page.pages.open_page(project_root, "home.py")
    run(at)
    assert not at.exception, at.exception
    assert google.requests == [] and wordpress.requests == []
    assert not plan_cache.DEFAULT_PLAN_CACHE_FILE.exists()
    assert not site_storage.DEFAULT_SITE_INDEX_FILE.exists()
    assert not drafts.DEFAULT_DRAFTS_FILE.exists()


# ================================================ chữ lấy từ Google: tên Sheet hiện thuần


def test_sheet_title_from_google_is_plain(project_root, google, env_path):
    """Tên Sheet do Google trả (chủ Sheet đặt, chưa tin cậy) có link Markdown, thẻ HTML, ký tự
    đảo hướng, vô hình: «Kiểm tra kết nối» hiện chữ thuần (LC-T094-3)."""
    found = plan_page.FakePlanSheet(google, [HEADER])
    info = found._info({})
    info["properties"]["title"] = HOSTILE
    google.on("GET", INFO_URL, lambda _request: info)
    at = settings_page.open_settings(project_root)
    click(at, "google-check-btn")
    tab = settings_page.google_tab(at)
    shown = "\n".join(s.value for s in tab.success) + "\n".join(e.value for e in tab.error)
    assert "abc" in shown, "phải có câu báo kết quả kiểm tra, kèm tên Sheet"
    # Client đã bỏ U+202E, U+200B gốc; ký tự rộng 0 còn lại duy nhất là chỗ ``escape_markdown`` cố
    # ý chèn sau «www» để không thành link (T-031).
    assert RLO not in shown and f"ab{ZWSP}c" not in shown
    settings_page.assert_tab_plain(at)

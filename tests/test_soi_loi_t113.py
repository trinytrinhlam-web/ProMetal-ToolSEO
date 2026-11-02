"""Soi Lỗi T-113 (rút gọn): nút «Cập nhật trạng thái từ website» ở trang Kế hoạch (lõi T-109).

Kiểm độc lập với test của Họa Sĩ, cùng bộ giả: Google Sheets giả (``FakePlanSheet`` qua
``SheetsClient`` thật), WordPress giả (đếm request); cache kế hoạch, cache bài đã đăng ở thư mục tạm
(fixture của T-101). Không gọi Google, WordPress thật.

Trọng tâm: điều kiện Lá Chắn T-109 cho lượt nối nút; website lỗi ở lệnh hỏi thứ hai; hai tab cùng
ghi; Sheet đổi giữa chừng (xóa, xếp lại dòng, đổi mã bài website, chép trùng dòng); giờ máy lùi;
chữ Sheet, website lạ vẫn thuần; không lộ mã Sheet, đường dẫn; chạy lại trang không gọi mạng.
"""

from __future__ import annotations

import dataclasses
import re
from datetime import timedelta

import pytest
import test_settings_images as si
import test_t113_website_status as t113
from fake_google import SHEET_ID
from fake_plan_sheet import HEADER, FakePlanSheet
from fake_wordpress import query

from seo_app.plan import model, website

env = t113.env
caches = t113.caches
private_key = t113.private_key
google = t113.google
wordpress = t113.wordpress
run, click, frame, assert_plain, row = t113.run, t113.click, t113.frame, t113.assert_plain, t113.row
setup, open_plan, check_now, pick_keys = t113.setup, t113.open_plan, t113.check_now, t113.pick_keys
read_website, shown = t113.read_website, t113.t101.sl44.shown
STATUS, POST, KEY = t113.STATUS, HEADER.index("Mã bài WordPress"), HEADER.index("Mã bài")
BAIT = "MOI-loi-may-chu"
RLO = chr(0x202E)
_RANGE = re.compile(r"'KeHoach'!([A-Z])([0-9]+)")


def tick(at, *keys: str):
    """Tick các thay đổi của Mã bài ``keys`` (không có ``keys``: tick tất cả)."""
    names = pick_keys(at)
    for number, update in enumerate(check_now(at).updates, start=1):
        if not keys or update.key in keys:
            at.session_state[names[number - 1]] = True
    return run(at)


def rows_per_write(sheet: FakePlanSheet) -> list[set[int]]:
    """Các dòng mỗi lệnh ghi ô chạm tới."""
    found = []
    for data in sheet.updates:
        found.append({int(_RANGE.fullmatch(item["range"]).group(2)) for item in data})
    return found


def errors(at) -> list[str]:
    return [shown(e.value) for e in at.error]


def post_requests(wordpress) -> list:
    return [r for r in wordpress.requests if r.url.split("?")[0].endswith("/wp/v2/posts")]


# ================================================================ website lỗi ở lệnh hỏi sau


def test_website_error_in_a_later_chunk_keeps_no_check(project_root, google, wordpress):
    """150 bài: ``post_statuses`` hỏi 2 lệnh (100 mã mỗi lệnh); lệnh thứ hai lỗi 500 có mồi trong
    lời máy chủ: câu cố định, không có lần kiểm (cả lần kiểm trước đó), không ghi Sheet, chỉ GET."""
    lines = [HEADER] + [
        row(f"B-{100 + n:03d}", f"cửa số {n}", status="Đã gửi nháp",
            **{"Mã bài WordPress": 600 + n})
        for n in range(1, 151)
    ]  # fmt: skip
    sheet = FakePlanSheet(google, lines)
    broken = {"on": False}

    def answer(request):
        ids = [int(value) for value in query(request)["include"][0].split(",")]
        if broken["on"] and max(ids) > 700:
            return (500, {"code": "x", "message": BAIT}, {})
        return [{"id": i, "status": "publish", "date_gmt": "2026-10-29T02:00:00",
                 "modified_gmt": "", "link": ""} for i in ids]  # fmt: skip

    wordpress.on("GET", "/wp-json/wp/v2/posts", answer)
    at = open_plan(project_root)
    click(at, "plan-web")  # lần đầu: được, có lần kiểm 150 thay đổi
    assert len(check_now(at).updates) == 150 and len(post_requests(wordpress)) == 2
    broken["on"] = True
    click(at, "plan-web")
    assert len(post_requests(wordpress)) == 4
    assert {r.method for r in wordpress.requests} == {"GET"}
    assert at.error and not any(BAIT in text for text in errors(at))
    assert "plan_webcheck" not in at.session_state
    assert sheet.updates == [] and sheet.appends == []
    assert_plain(at)


# ============================================================== hai tab, bấm ghi lại


def test_two_tabs_write_each_change_once(project_root, google, wordpress):
    """Hai tab cùng kiểm. Tab đầu ghi B-003; tab sau tick cả B-003, B-004 rồi ghi: B-003 «đã đúng
    sẵn» (không ghi lại), chỉ B-004 được ghi; mỗi lần bấm đúng một lệnh ghi. (B-002 có thêm đề xuất
    «sửa ngày» vì ô ngày trống: không tick.)"""
    sheet = setup(google, wordpress)
    first, second = open_plan(project_root), open_plan(project_root)
    for tab in (first, second):
        click(tab, "plan-web")
    tick(first, "B-003")
    click(first, "plan-web-write")
    tick(second, "B-003", "B-004")
    click(second, "plan-web-write")
    assert rows_per_write(sheet) == [{4}, {5}]  # B-003 ở dòng 4, B-004 ở dòng 5
    message = " ".join(shown(s.value) for s in second.success)
    assert "Đã cập nhật 1 dòng" in message and "1 dòng đã đúng sẵn" in message
    assert {r.method for r in wordpress.requests} == {"GET"}


def test_same_check_applied_again_writes_nothing_more(project_root, google, wordpress):
    """Bấm ghi lần nữa với đúng lần kiểm đó (bấm đúp, tab cũ còn giữ lần kiểm): lõi đọc lại Sheet,
    thấy đã đúng, không gửi lệnh ghi thứ hai."""
    at, sheet = read_website(project_root, google, wordpress)
    old, round_ = check_now(at), at.session_state["plan_webround"]
    tick(at)
    ticked = {key: at.session_state[key] for key in pick_keys(at)}
    click(at, "plan-web-write")
    assert len(sheet.updates) == 1
    at.session_state["plan_webcheck"] = old  # như tab vẫn giữ lần kiểm cũ (dưới 5 phút)
    at.session_state["plan_webround"] = round_
    for key, value in ticked.items():
        at.session_state[key] = value
    run(at)
    click(at, "plan-web-write")
    assert len(sheet.updates) == 1
    assert any("đã đúng sẵn" in shown(s.value) for s in at.success)


# ================================================================== Sheet đổi giữa chừng


@pytest.mark.parametrize("change", ["xoa-dong", "xep-lai", "doi-ma-bai-website", "chep-trung"])
def test_sheet_changed_between_check_and_write(project_root, google, wordpress, change):
    """Sau lần kiểm: xóa dòng B-003, đảo thứ tự các dòng, đổi Mã bài WordPress của B-003, chép
    trùng dòng B-003. Ghi theo Mã bài (không theo số dòng); dòng đổi thì bảng «Vì sao chưa ghi»
    bằng chữ thuần; B-004 vẫn ghi đúng dòng; chỉ 3 cột của app."""
    at, sheet = read_website(project_root, google, wordpress)
    tick(at, "B-003", "B-004")
    if change == "xoa-dong":
        del sheet.grid[3]
    elif change == "xep-lai":
        sheet.grid[1:] = list(reversed(sheet.grid[1:]))
    elif change == "doi-ma-bai-website":
        sheet.set(4, POST, 999)
    else:
        sheet.grid.append(list(sheet.grid[3]))
    click(at, "plan-web-write")
    final = {line[KEY]: line for line in sheet.grid[1:]}
    assert final["B-004"][STATUS] == model.STATUS_SCHEDULED
    assert final["B-001"][STATUS] == model.STATUS_NEW
    allowed = {HEADER.index(t) for t in ("Trạng thái", "Ngày đăng thực tế", "Cập nhật lúc")}
    assert {column for _, column, _ in sheet.written_cells()} <= allowed
    if change == "xep-lai":
        assert final["B-003"][STATUS] == model.STATUS_PUBLISHED
        assert any("Đã cập nhật 2 dòng" in shown(s.value) for s in at.success)
    else:
        assert list(frame(at, "Vì sao chưa ghi")["Dòng"]) == ["B-003 (bài #501)"]
        if change != "xoa-dong":
            assert all(line[STATUS] != model.STATUS_PUBLISHED for line in sheet.grid[1:]
                       if line[KEY] == "B-003")  # fmt: skip
    assert sheet.appends == []
    assert_plain(at)


# =========================================================================== giờ máy lùi


def test_clock_moved_back_is_refused_with_fixed_text(project_root, google, wordpress):
    """Giờ máy lùi hơn 1 phút so với lúc kiểm: giao diện chỉ khóa nút khi quá 5 phút, nhưng lõi từ
    chối (``MSG_STALE``) trước khi đọc Sheet; giao diện hiện câu cố định, bỏ lần kiểm."""
    at, sheet = read_website(project_root, google, wordpress)
    ahead = check_now(at).checked_at + timedelta(minutes=3)
    at.session_state["plan_webcheck"] = dataclasses.replace(check_now(at), checked_at=ahead)
    tick(at)
    reads = sheet.reads
    click(at, "plan-web-write")
    assert website.MSG_STALE in errors(at)
    assert "plan_webcheck" not in at.session_state
    assert sheet.updates == [] and sheet.reads == reads


# ========================================================= chữ lạ, không lộ mã Sheet, đường dẫn


def test_odd_sheet_and_website_data_stay_plain_and_fixed(project_root, google, wordpress):
    """Ô Sheet có mồi (link Markdown, thẻ HTML, U+202E), ô Trạng thái / Ngày gõ chữ tự do, Mã bài
    trùng, một bài ở hai dòng; website trả trạng thái lạ, giờ hỏng: mọi câu báo là câu cố định
    của lõi, không chép chữ ô; trang thuần (không link, không HTML)."""
    hostile = f"[bấm](javascript:alert(1)) <b>đậm</b> {RLO}{BAIT}"
    sheet = FakePlanSheet(google, [
        HEADER,
        row("B-001", f"cửa cuốn {hostile}", status="Xong rồi " + hostile,
            **{"Mã bài WordPress": 501, "Ghi chú của thợ": hostile}),
        row("B-002", "cổng sắt", status="Đã hẹn giờ",
            **{"Mã bài WordPress": 502, "Ngày đăng thực tế": "hôm qua " + hostile}),
        row("B-003", "cửa kéo", status="Đã gửi nháp", **{"Mã bài WordPress": 503}),
        row("b-3", "cửa kéo 2", status="Đã gửi nháp", **{"Mã bài WordPress": 504}),
        row("B-005", "lan can", status="Đã gửi nháp", **{"Mã bài WordPress": 505}),
        row("B-006", "mái tôn", status="Đã gửi nháp", **{"Mã bài WordPress": 505}),
        row("B-007", "cầu thang", status="Đã gửi nháp", **{"Mã bài WordPress": 507}),
    ])  # fmt: skip
    wordpress.on("GET", "/wp-json/wp/v2/posts", [
        {"id": 501, "status": "publish", "date_gmt": "2026-10-29T02:00:00", "modified_gmt": "",
         "link": ""},
        {"id": 502, "status": "publish", "date_gmt": "2026-10-29T02:00:00", "modified_gmt": "",
         "link": ""},
        {"id": 503, "status": "publish", "date_gmt": "x" * 19, "modified_gmt": "", "link": ""},
        {"id": 505, "status": "publish", "date_gmt": "2026-10-29T02:00:00", "modified_gmt": "",
         "link": ""},
        {"id": 507, "status": f"publish{RLO}", "date_gmt": BAIT, "modified_gmt": "", "link": ""},
    ])  # fmt: skip
    at = open_plan(project_root)
    click(at, "plan-web")
    kinds = {notice.kind for notice in check_now(at).notices}
    assert {website.WebNoticeKind.ODD_CELL, website.WebNoticeKind.DUPLICATE_KEY,
            website.WebNoticeKind.SHARED_POST, website.WebNoticeKind.MISSING} <= kinds  # fmt: skip
    warned = [shown(w.value) for w in at.warning]
    for notice in check_now(at).notices:
        assert notice.message in warned
    assert not any(BAIT in text or "javascript" in text or RLO in text for text in warned)
    assert check_now(at).updates == ()  # chỉ cảnh báo, không đề xuất
    assert_plain(at)
    assert sheet.updates == []


def test_sheet_id_and_paths_never_shown(project_root, google, wordpress, tmp_path):
    """Đọc, tick, ghi (một dòng xung đột), rồi lỗi Google khi ghi: không chỗ nào trên trang có mã
    Sheet, đường dẫn file khóa, thư mục tạm hay thư mục dự án."""
    at, sheet = read_website(project_root, google, wordpress)
    tick(at)
    sheet.set(4, STATUS, "Đang viết")
    click(at, "plan-web-write")
    pages = [si.page_strings(at)]
    click(at, "plan-web")
    tick(at)
    sheet.fail("read", (500, {"error": {"message": BAIT}}))
    click(at, "plan-web-write")
    pages.append(si.page_strings(at))
    for page in pages:
        for secret in (SHEET_ID, str(tmp_path), "bi-mat", "du-an-thu-0123abcd", str(project_root),
                       BAIT):  # fmt: skip
            assert secret not in page, secret


# ========================================================= chạy lại trang không gọi mạng


def test_reruns_with_check_and_result_call_nothing(project_root, google, wordpress):
    """Có lần kiểm, rồi có kết quả ghi: chạy lại trang nhiều lần không hỏi website, không đọc hay
    ghi Sheet (cache kế hoạch còn mới), không tạo lần kiểm mới."""
    at, sheet = read_website(project_root, google, wordpress)
    asked, sheets = len(wordpress.requests), len(google.sheets_requests())
    run(at)
    run(at)
    assert len(wordpress.requests) == asked and len(google.sheets_requests()) == sheets
    tick(at, "B-003")
    click(at, "plan-web-write")
    asked, sheets = len(wordpress.requests), len(google.sheets_requests())
    round_ = at.session_state["plan_webround"]
    run(at)
    run(at)
    assert len(wordpress.requests) == asked and len(google.sheets_requests()) == sheets
    assert at.session_state["plan_webround"] == round_ and len(sheet.updates) == 1

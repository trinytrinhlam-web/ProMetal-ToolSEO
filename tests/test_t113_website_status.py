"""Nút «Cập nhật trạng thái từ website» ở trang Kế hoạch (T-113, lõi T-109 ``seo_app.plan.website``;
điều kiện Lá Chắn T-109 cho lượt nối nút, G1/G2 Soi Lỗi T-109) và bảng chuyên mục/thẻ ở trang Kết
nối WordPress trung hòa ô dạng công thức (như LC-T101-1, Ghi nhận 3 Lá Chắn T-102).

Google Sheets giả (``FakePlanSheet`` qua ``SheetsClient`` thật), WordPress giả (đếm request), không
gọi mạng thật; cache kế hoạch, cache bài, kho nháp ở thư mục tạm (fixture của T-101).
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import test_t101_plan_page as t101
from fake_google import SHEET_ID
from fake_plan_sheet import HEADER, FakePlanSheet
from streamlit.testing.v1 import AppTest

from seo_app.plan import model, sync, website
from seo_app.wordpress import Term, WordPressClient

env = t101.env
caches = t101.caches
private_key = t101.private_key
google = t101.google
wordpress = t101.wordpress
run = t101.run
click = t101.click
frame = t101.frame
assert_plain = t101.assert_plain
row = t101.row

PUBLISHED_AT = datetime(2026, 10, 29, 2, 0, tzinfo=UTC)  # 09:00 giờ Việt Nam
ROWS = [
    HEADER,
    row("B-001", "sửa cửa cuốn kêu to"),
    row("B-002", "sơn lại cổng sắt", status="Đã hẹn giờ", **{"Mã bài WordPress": 502}),
    row("B-003", "cửa kéo bị kẹt ray", status="Đã gửi nháp", **{"Mã bài WordPress": 501}),
    row("B-004", "lan can kính", status="Đã gửi nháp", **{"Mã bài WordPress": 503}),
]
STATUS = HEADER.index("Trạng thái")


def gmt(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S")


def site_answer(*, late: datetime | None = None) -> list[dict]:
    """501 đã đăng; 502 hẹn giờ đã quá giờ (Lỡ lịch); 503 đang hẹn giờ trong tương lai."""
    late = late or datetime.now(UTC) - timedelta(hours=2)
    future = datetime.now(UTC) + timedelta(days=3)
    return [
        {"id": 501, "status": "publish", "date_gmt": gmt(PUBLISHED_AT), "modified_gmt": "",
         "link": ""},
        {"id": 502, "status": "future", "date_gmt": gmt(late), "modified_gmt": "", "link": ""},
        {"id": 503, "status": "future", "date_gmt": gmt(future), "modified_gmt": "", "link": ""},
    ]  # fmt: skip


def setup(google, wordpress, answer=None) -> FakePlanSheet:
    sheet = FakePlanSheet(google, [list(line) for line in ROWS])
    wordpress.on("GET", "/wp-json/wp/v2/posts", site_answer() if answer is None else answer)
    return sheet


def open_plan(project_root) -> AppTest:
    return t101.open_plan(project_root)


def check_now(at: AppTest) -> website.WebCheck:
    return at.session_state["plan_webcheck"]


def pick_keys(at: AppTest) -> list[str]:
    round_ = at.session_state["plan_webround"]
    count = len(check_now(at).updates)
    return [f"plan-web-pick-{round_}-{n}" for n in range(1, count + 1)]


def read_website(project_root, google, wordpress, answer=None) -> tuple[AppTest, FakePlanSheet]:
    sheet = setup(google, wordpress, answer)
    at = open_plan(project_root)
    assert wordpress.requests == []  # mở trang không hỏi website
    click(at, "plan-web")
    return at, sheet


# ===================================================================== nút đọc, nút ghi


def test_read_button_only_reads_and_nothing_is_preticked(project_root, google, wordpress):
    """Nút đọc: chỉ lệnh GET tới WordPress, không ghi Sheet; bảng thay đổi, cảnh báo «Lỡ lịch»;
    ô tick không tick sẵn, nút ghi khóa khi chưa tick (điều kiện 1a Lá Chắn T-109)."""
    at, sheet = read_website(project_root, google, wordpress)
    assert {r.method for r in wordpress.requests} == {"GET"}
    assert sheet.updates == [] and sheet.appends == [] and sheet.structure == []
    check = check_now(at)
    kinds = {(u.key, u.status_before, u.status_after) for u in check.updates}
    assert ("B-003", "Đã gửi nháp", "Đã đăng") in kinds
    assert ("B-004", "Đã gửi nháp", "Đã hẹn giờ") in kinds
    assert [n.key for n in check.late] == ["B-002"]
    table = frame(at, "Lý do")
    assert "Đã gửi nháp → Đã đăng" in list(table["Trạng thái"])
    assert [at.checkbox(key=key).value for key in pick_keys(at)] == [False] * len(check.updates)
    assert at.button(key="plan-web-write").disabled
    assert any("Lỡ lịch" in w.value and "B-002" in t101.sl44.shown(w.value) for w in at.warning)
    assert_plain(at)


def test_write_only_ticked_changes(project_root, google, wordpress):
    """Nút ghi: chỉ thay đổi đã tick; ghi RAW đúng ô Trạng thái, Ngày đăng thực tế, Cập nhật lúc;
    không lệnh nào tới WordPress ngoài GET; xong thì tải lại danh sách, bỏ lần kiểm."""
    at, sheet = read_website(project_root, google, wordpress)
    keys = pick_keys(at)
    target = next(n for n, u in enumerate(check_now(at).updates, start=1) if u.key == "B-003")
    at.checkbox(key=keys[target - 1]).check()
    run(at)
    assert not at.button(key="plan-web-write").disabled
    click(at, "plan-web-write")
    assert sheet.cell(4, STATUS) == model.STATUS_PUBLISHED  # dòng B-003 (dòng 4 trên Sheet)
    assert sheet.cell(5, STATUS) == model.STATUS_DRAFT_SENT  # B-004 không tick: giữ nguyên
    written_columns = {column for _, column, _ in sheet.written_cells()}
    allowed = {HEADER.index(t) for t in ("Trạng thái", "Ngày đăng thực tế", "Cập nhật lúc")}
    assert written_columns <= allowed
    assert all(o.get("valueInputOption") == "RAW" for o in sheet.update_options)
    assert {r.method for r in wordpress.requests} == {"GET"}
    assert any("Đã cập nhật 1 dòng" in s.value for s in at.success)
    assert "plan_webcheck" not in at.session_state


def test_pick_all_is_an_explicit_click(project_root, google, wordpress):
    at, sheet = read_website(project_root, google, wordpress)
    click(at, "plan-web-all")
    assert all(at.checkbox(key=key).value for key in pick_keys(at))
    assert sheet.updates == []  # chọn tất cả chưa ghi gì


def test_stale_check_blocks_write_and_asks_to_check_again(project_root, google, wordpress):
    """Lần kiểm cũ quá 5 phút: nút ghi khóa, câu mời kiểm lại; không ghi gì (điều kiện 1c)."""
    at, sheet = read_website(project_root, google, wordpress)
    old = check_now(at).checked_at - timedelta(minutes=6)
    at.session_state["plan_webcheck"] = dataclasses.replace(check_now(at), checked_at=old)
    for key in pick_keys(at):
        at.session_state[key] = True
    run(at)
    assert at.button(key="plan-web-write").disabled
    assert any("đã cũ" in w.value for w in at.warning)
    assert sheet.updates == []


def test_core_refusal_is_fixed_text_and_check_is_dropped(project_root, google, wordpress,
                                                         monkeypatch):  # fmt: skip
    """Lõi từ chối (lần kiểm cũ, Sheet khác): câu cố định, bỏ lần kiểm để người dùng kiểm lại,
    không khung lỗi (điều kiện 1c, 1f)."""
    at, sheet = read_website(project_root, google, wordpress)

    def refuse(*args, **kwargs):
        raise sync.SheetPlanError(website.MSG_OTHER_SHEET)

    monkeypatch.setattr(website, "apply_website_changes", refuse)
    for key in pick_keys(at):
        at.session_state[key] = True
    run(at)
    click(at, "plan-web-write")
    assert any("Google Sheet đang kết nối khác" in e.value for e in at.error)
    assert "plan_webcheck" not in at.session_state
    assert sheet.updates == []


def test_row_changed_elsewhere_is_conflict(project_root, google, wordpress):
    """Dòng bị sửa trên Sheet sau lần kiểm: không ghi dòng đó, báo xung đột bằng bảng chữ thuần."""
    at, sheet = read_website(project_root, google, wordpress)
    keys = pick_keys(at)
    target = next(n for n, u in enumerate(check_now(at).updates, start=1) if u.key == "B-003")
    at.checkbox(key=keys[target - 1]).check()
    run(at)
    sheet.set(4, STATUS, "Đang viết")  # máy kia vừa sửa ô Trạng thái
    click(at, "plan-web-write")
    assert sheet.cell(4, STATUS) == "Đang viết"
    assert sheet.updates == []
    table = frame(at, "Vì sao chưa ghi")
    assert list(table["Dòng"]) == ["B-003 (bài #501)"]
    assert any("chưa ghi" in w.value for w in at.warning)
    assert_plain(at)


def test_sheet_error_while_writing_is_fixed_text(project_root, google, wordpress):
    at, sheet = read_website(project_root, google, wordpress)
    for key in pick_keys(at):
        at.session_state[key] = True
    run(at)
    sheet.fail("read", (500, {"error": {"message": "MOI-loi-may-chu-google"}}))
    click(at, "plan-web-write")
    shown = "\n".join(e.value for e in at.error)
    assert "Chưa ghi gì lên Google Sheet" in shown and "MOI" not in shown
    assert sheet.updates == []


def test_website_error_is_fixed_text(project_root, google, wordpress):
    setup(google, wordpress, (500, {"code": "x", "message": "MOI-loi-may-chu-wordpress"}, {}))
    at = open_plan(project_root)
    click(at, "plan-web")
    shown = "\n".join(e.value for e in at.error)
    assert at.error and "MOI" not in shown
    assert "plan_webcheck" not in at.session_state


def test_check_gets_real_states_and_settings(project_root, google, wordpress, monkeypatch):
    """G2 Soi Lỗi T-109: ``check_website`` nhận thẳng kết quả ``post_statuses`` (``PostState``,
    không phải bộ đôi chữ), đúng các mã đã hỏi, đúng mã Sheet, giờ có múi giờ."""
    seen = {}
    original = website.check_website

    def spy(plan, states, asked, *, sheet_id, now):
        seen.update(states=dict(states), asked=list(asked), sheet_id=sheet_id, now=now)
        return original(plan, states, asked, sheet_id=sheet_id, now=now)

    monkeypatch.setattr(website, "check_website", spy)
    read_website(project_root, google, wordpress)
    from seo_app.wordpress.client import PostState

    assert all(isinstance(state, PostState) for state in seen["states"].values())
    assert sorted(seen["asked"]) == [501, 502, 503]
    assert seen["sheet_id"] == SHEET_ID and seen["now"].tzinfo is not None


def test_reload_forgets_check(project_root, google, wordpress):
    at, _ = read_website(project_root, google, wordpress)
    click(at, "plan-reload")
    assert "plan_webcheck" not in at.session_state


def test_page_rerun_does_not_ask_website_again(project_root, google, wordpress):
    """Chỉ khi bấm: chạy lại trang (rerun) không hỏi website, không ghi Sheet (điều kiện 1a)."""
    at, sheet = read_website(project_root, google, wordpress)
    asked = len(wordpress.requests)
    run(at)
    run(at)
    assert len(wordpress.requests) == asked and sheet.updates == []


# ===================================================================== hằng «Lỡ lịch» dùng chung


def test_late_constant_is_shared_with_core(project_root, google, wordpress, monkeypatch):
    """G1 Soi Lỗi T-109: trang Kế hoạch, Bài viết dùng ``website.LATE_AFTER`` (không hằng riêng):
    đổi hằng của lõi thì nhãn «Lỡ lịch» của cả hai trang đổi theo."""
    for name in ("plan.py", "home.py"):
        source = (project_root / "app" / "views" / name).read_text(encoding="utf-8")
        assert "website.LATE_AFTER" in source and "timedelta(minutes=15)" not in source
    monkeypatch.setattr(website, "LATE_AFTER", timedelta(hours=3))
    at, _ = read_website(project_root, google, wordpress)  # 502 trễ 2 giờ: chưa «Lỡ lịch»
    assert "Lỡ lịch" not in list(frame(at, "Trên website")["Trên website"])
    monkeypatch.setattr(website, "LATE_AFTER", timedelta(minutes=30))
    click(at, "plan-web")
    assert "Lỡ lịch" in list(frame(at, "Trên website")["Trên website"])


# ===================================================================== trang Kết nối WordPress


def test_category_table_neutralizes_formula_cells(project_root, monkeypatch):
    """Bảng chuyên mục, thẻ: ô mở đầu ``=``, ``+``, ``-``, ``@``, tab thêm một dấu cách đầu
    (bảng tải về CSV mở bằng Excel không thành công thức); ô thường giữ nguyên (Ghi nhận 3 Lá
    Chắn T-102, như LC-T101-1)."""
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    categories = [
        Term(3, '=HYPERLINK("https://evil.example","x")', "=cmd", 1),
        Term(4, "+1+1", "-x", 0),
        Term(5, "@SUM(A1)", "\tslug", 0),
        Term(6, "Cửa sắt", "cua-sat", 2),
    ]
    monkeypatch.setattr(WordPressClient, "list_categories", lambda self: categories)
    monkeypatch.setattr(
        WordPressClient, "list_tags", lambda self: [Term(7, "-giam-gia", "inox", 0)]
    )
    at = t101.pages.open_page(project_root, "wordpress.py")
    next(b for b in at.button if b.label == "Tải chuyên mục và thẻ").click()
    run(at)
    cats, tags = (f.value for f in at.dataframe)
    assert list(cats["Tên"]) == [
        ' =HYPERLINK("https://evil.example","x")',
        " +1+1",
        " @SUM(A1)",
        "Cửa sắt",
    ]
    assert list(cats["Slug"]) == [" =cmd", " -x", " \tslug", "cua-sat"]
    assert list(tags["Tên"]) == [" -giam-gia"] and list(tags["Slug"]) == ["inox"]


def test_opening_plan_page_does_not_create_site_index(project_root, wordpress):
    """Đã khai báo WordPress, chưa có bản lưu danh sách bài: mở trang Kế hoạch không tạo file
    cache bài đã đăng (như cache kế hoạch ở T-101; test cũ không trỏ cache này sang thư mục tạm
    thì ghi vào ``data/`` thật)."""
    from seo_app.storage import site_index

    at = open_plan(project_root)
    assert not at.exception, at.exception
    assert not site_index.DEFAULT_SITE_INDEX_FILE.exists()
    assert wordpress.requests == []

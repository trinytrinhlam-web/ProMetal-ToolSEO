"""Trang Kế hoạch (T-101; thiết kế T-094 mục 1.2–1.8; Lá Chắn LC-T094-1 → -3, -32 → -35 và điều
kiện T-097, T-098, T-100 cho T-101).

Google Sheets giả (``FakeGoogle`` + ``FakePlanSheet``: đi qua ``SheetsClient`` thật, đường cố định,
``RAW``), AI giả, WordPress giả; khóa tài khoản dịch vụ sinh lúc chạy test (LC-T094-17). Không gọi
mạng thật; cache kế hoạch, cache bài đã đăng, kho nháp đều ở thư mục tạm.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, date, datetime, timedelta

import pytest
import streamlit
import test_app_pages as pages
import test_soi_loi_t044 as sl44
from fake_google import SHEET_ID, SHEETS, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, FakePlanSheet
from fake_wordpress import FakeWordPress
from fake_wordpress import make_session as wordpress_session
from streamlit.testing.v1 import AppTest

import seo_app.storage.drafts as drafts
from seo_app.ai import registry as ai_registry
from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.google.sheets import SheetsClient
from seo_app.plan import model, parse
from seo_app.storage import plan_cache
from seo_app.storage import site_index as site_storage
from seo_app.storage.drafts import DraftPlanRef, DraftSnapshot, DraftStore, PlanStatusWrite
from seo_app.storage.plan_cache import sheet_hash
from seo_app.wordpress import WordPressClient

env = pages.env  # mật khẩu thử, không có khóa AI thật

TAB_PASTE, TAB_SHEET = "Dán nội dung", "Google Sheets"
RLO = "\N{RIGHT-TO-LEFT OVERRIDE}"
ZWSP = "\N{ZERO WIDTH SPACE}"
HOSTILE = f"[bấm](javascript:alert(1)) <b>đậm</b> {RLO}ab{ZWSP}c www.evil.example"
FUTURE = date(2027, 11, 20)
PAST = date(2025, 1, 10)
OTHER_SHEET = "Sheet-khac-chi-de-thu-00000000000"  # mã giả, đúng dạng


def serial(day: date) -> int:
    """Ngày → số ngày kiểu Google Sheets (ô ngày đọc bằng ``SERIAL_NUMBER``)."""
    return (day - date(1899, 12, 30)).days


def row(key, keyword, *, status="Chưa viết", day=FUTURE, priority="Trung bình", **cells):
    """Một dòng tab «KeHoach» theo ``HEADER`` (16 cột)."""
    line = [""] * len(HEADER)
    values = {
        "Mã bài": key,
        "Từ khóa chính": keyword,
        "Ưu tiên": priority,
        "Ngày dự kiến": serial(day) if day else "",
        "Trạng thái": status,
        **cells,
    }
    for title, value in values.items():
        line[HEADER.index(title)] = value
    return line


ROWS = [
    HEADER,
    row("B-001", "sửa cửa cuốn kêu to", **{"Tiêu đề dự kiến": "Cửa cuốn kêu to: 5 nguyên nhân"}),
    row("B-002", "sơn lại cổng sắt", **{"Ghi chú của thợ": "Khách hay hỏi sơn mấy lớp"}),
    row("B-003", "cửa kéo bị kẹt ray", status="Đã gửi nháp", **{"Mã bài WordPress": 501}),
]


# ============================================================================ chuẩn bị


@pytest.fixture(autouse=True)
def caches(monkeypatch, tmp_path):
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", tmp_path / "plan_cache.sqlite")
    monkeypatch.setattr(site_storage, "DEFAULT_SITE_INDEX_FILE", tmp_path / "site_index.sqlite")


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def google(monkeypatch, tmp_path, private_key) -> FakeGoogle:
    """Google đã khai báo: file khóa (ngoài thư mục dự án) và mã Sheet; mọi ``SheetsClient`` đi qua
    Google giả."""
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    key_file = folder / "du-an-thu-0123abcd.json"
    key_file.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        key_file.chmod(0o600)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    fake = FakeGoogle()
    original = SheetsClient.__init__

    def init(self, spreadsheet_id, account, *, session=None, **kwargs):
        original(self, spreadsheet_id, account, session=session or make_session(fake), **kwargs)

    monkeypatch.setattr(SheetsClient, "__init__", init)
    return fake


@pytest.fixture
def sheet(google) -> FakePlanSheet:
    found = FakePlanSheet(google, [list(line) for line in ROWS])
    found.google = google  # để test đếm mọi lệnh Sheets (``sheet_google``)
    return found


def sheet_google(sheet: FakePlanSheet) -> FakeGoogle:
    return sheet.google


@pytest.fixture
def wordpress(monkeypatch) -> FakeWordPress:
    """WordPress đã khai báo, mọi client đi qua WordPress giả (để đếm request)."""
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    fake = FakeWordPress()
    original = WordPressClient.from_settings.__func__

    def from_settings(cls, settings, **kwargs):
        return original(cls, settings, session=wordpress_session(fake), **kwargs)

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    return fake


class PlanAI:
    """AI giả cho việc ``plan``: ghi lời dặn, trả ``PlanSuggestions`` cố định."""

    def __init__(self, items: list[PlanSuggestion]) -> None:
        self.items = items
        self.prompts: list[str] = []

    def generate(self, task, *, system, prompt, schema, images=()):
        assert schema is PlanSuggestions and task.name == "plan"
        self.prompts.append(prompt)
        return PlanSuggestions(items=self.items)


def suggestion(action: str, *, key: str = "", keyword: str = "", reason: str = "Theo ghi chú.",
               **fields: str) -> PlanSuggestion:  # fmt: skip
    data = {name: "" for name in PlanSuggestion.model_fields}
    data.update(action=action, key=key, keyword=keyword, reason=reason, **fields)
    return PlanSuggestion(**data)


@pytest.fixture
def plan_ai(monkeypatch):
    def install(items: list[PlanSuggestion]) -> PlanAI:
        ai = PlanAI(items)
        monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: ai)
        return ai

    return install


class FakeUpload:
    """Thay cho file người dùng chọn ở ``st.file_uploader`` (AppTest không giả lập tải file)."""

    def __init__(self, name: str, data: bytes, size: int | None = None) -> None:
        self.name = name
        self.data = data
        self.size = len(data) if size is None else size
        self.read = False

    def getvalue(self) -> bytes:
        self.read = True
        return self.data


def choose_file(monkeypatch, upload: FakeUpload | None) -> None:
    monkeypatch.setattr(streamlit, "file_uploader", lambda *args, **kwargs: upload)


def open_plan(project_root) -> AppTest:
    return pages.open_page(project_root, "plan.py")


def run(at: AppTest) -> AppTest:
    at.run()
    assert not at.exception, at.exception
    return at


def click(at: AppTest, key: str) -> AppTest:
    at.button(key=key).click()
    return run(at)


def read(at: AppTest, source: str | None = None) -> AppTest:
    if source is not None:
        at.session_state["plan_source"] = source
    return click(at, "plan-read")


def paste(at: AppTest, text: str) -> AppTest:
    at.session_state["plan_source"] = TAB_PASTE
    at.text_area(key="plan_paste").input(text)
    return read(at)


def picks(at: AppTest) -> list[bool]:
    round_ = at.session_state["plan_round"]
    count = len(at.session_state["plan_proposals"].items)
    return [at.checkbox(key=f"plan-pick-{round_}-{n}").value for n in range(1, count + 1)]


HEADER_HTML = '<p class="page-sub">'  # phụ đề cố định của ``ui.page_header`` (HTML đã escape)


def assert_plain(at: AppTest) -> None:
    """Như ``assert_page_plain`` của Soi Lỗi T-044 (không link, không HTML, không thẻ chưa
    escape), trừ đúng phụ đề cố định của đầu trang (``ui.page_header``, chữ hằng đã escape)."""
    assert not at.exception, at.exception
    for element in sl44.markdown_elements(at):
        if element.value.startswith(HEADER_HTML):
            continue
        assert sl44.cm_problems(element.value) == [], element.value
        assert not getattr(element.proto, "allow_html", False), element.value


def texts(at: AppTest) -> str:
    """Mọi chữ trên trang: Markdown, câu báo, ``st.text``, ô bảng, nhãn ô tick, lựa chọn."""
    found = [str(el.value) for el in sl44.markdown_elements(at)]
    found += [str(el.value) for el in at.text]
    for frame in at.dataframe:
        found.append(frame.value.to_string())
    found += [str(box.label) for box in at.checkbox]
    for box in at.selectbox:
        found += [str(option) for option in box.options]
    return "\n".join(found)


def frame(at: AppTest, column: str):
    """Bảng (``st.dataframe``) đầu tiên có cột ``column``."""
    return next(f.value for f in at.dataframe if column in f.value.columns)


# ======================================================================= chưa có Google


def test_without_google_page_explains_and_proposes_nothing(project_root, plan_ai):
    """Chưa khai báo Google: trang báo cách khai báo; bấm đọc không đề xuất, không gọi AI."""
    ai = plan_ai([suggestion("them", keyword="sửa cửa kéo")])
    at = open_plan(project_root)
    assert any("Cài đặt" in el.value and "Google" in el.value for el in at.info)
    paste(at, "Tháng 11: thêm bài sửa cửa kéo.")
    assert any("Chưa đọc được kế hoạch hiện tại" in w.value for w in at.warning)
    assert "plan_proposals" not in at.session_state and "plan_ai" not in at.session_state
    assert ai.prompts == []
    assert_plain(at)


def test_demo_data_is_gone(project_root):
    """Trang thật: không nhãn «Bản demo», không dữ liệu mẫu kế hoạch (G4: nhãn «Sẵn sàng»)."""
    at = open_plan(project_root)
    assert not any("Bản demo" in c.value for c in at.caption)
    from seo_app import demo

    for name in ("PLAN_ROWS", "PLAN_CHANGES", "PLAN_PASTE_EXAMPLE", "BUSINESS_BRIEF", "plan_rows"):
        assert not hasattr(demo, name), name
    source = (project_root / "app" / "views" / "plan.py").read_text(encoding="utf-8")
    assert "Sẵn sàng" not in source and "demo." not in source


# ======================================================================= danh sách bài


def test_list_reads_sheet_and_shows_plain_text(project_root, sheet):
    """Danh sách bài đọc từ Sheet; chữ Sheet lạ hiện thuần, đã bỏ ký tự đảo hướng, vô hình
    (LC-T094-3, -32)."""
    sheet.set(2, HEADER.index("Tiêu đề dự kiến"), HOSTILE)
    at = open_plan(project_root)
    table = frame(at, "Mã bài")
    assert list(table["Mã bài"]) == ["B-001", "B-002", "B-003"]
    assert list(table["Trạng thái"]) == ["Chưa viết", "Chưa viết", "Đã gửi nháp"]
    shown = table.to_string()
    assert RLO not in shown and ZWSP not in shown
    assert_plain(at)
    assert sheet.reads == 1
    assert not any(SHEET_ID in text for text in texts(at).split("\n"))


def test_list_uses_cache_then_reload(project_root, sheet):
    """Mở lại trong 5 phút: đọc cache, không gọi Google; «Tải lại» đọc Sheet."""
    at = open_plan(project_root)
    assert sheet.reads == 1
    run(at)
    assert sheet.reads == 1
    click(at, "plan-reload")
    assert sheet.reads == 2


def test_sheet_error_message_is_fixed_text(project_root, sheet):
    """Google báo lỗi: câu cố định (LC-T094-2), không khung lỗi, không chép lời máy chủ."""
    sheet.fail("read", (403, {"error": {"message": "BAIMAT-loi-may-chu"}}))
    at = open_plan(project_root)
    shown = texts(at)
    assert "Chưa tải được kế hoạch" in shown and "BAIMAT" not in shown
    assert_plain(at)


def test_key_file_inside_project_is_refused_without_path(project_root, google, monkeypatch):
    """File khóa trong thư mục dự án: câu cố định, không in đường dẫn, không gọi Google."""
    inside = project_root / "tests" / "fake_google.py"
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(inside))
    at = open_plan(project_root)
    shown = texts(at)
    assert at.error and str(inside) not in shown and str(project_root) not in shown
    assert google.requests == []


# ======================================================================= đề xuất từ bảng


def test_pasted_table_proposals_and_default_ticks(project_root, sheet):
    """Bảng dán (chép từ Excel): đề xuất có lý do; «Thêm», «Cập nhật» không cảnh báo tick sẵn;
    «Bỏ» và dòng có cảnh báo (ngày đã qua) không tick sẵn (LC-T094-34)."""
    at = open_plan(project_root)
    paste(
        at,
        "Mã bài\tTừ khóa chính\tNgày dự kiến\tTrạng thái\tƯu tiên\n"
        "\tsửa cửa kéo đài loan\t20/11/2027\t\t\n"
        "B-001\tsửa cửa cuốn kêu to\t\t\tCao\n"
        "B-002\tsơn lại cổng sắt\t\tBỏ\t\n"
        "\tlan can kính cường lực\t10/01/2025\t\t\n",
    )
    items = at.session_state["plan_proposals"].items
    actions = [(p.action.value, p.key) for p in items]
    assert ("Thêm", "B-004") in actions and ("Cập nhật", "B-001") in actions
    assert ("Bỏ", "B-002") in actions
    ticks = dict(zip(actions, picks(at), strict=True))
    assert ticks[("Thêm", "B-004")] is True
    assert ticks[("Cập nhật", "B-001")] is True
    assert ticks[("Bỏ", "B-002")] is False
    past = next(p for p in items if p.after.keyword == "lan can kính cường lực")
    assert past.warnings and ticks[(past.action.value, past.key)] is False
    table = frame(at, "Lý do")
    assert len(table) == len(items)
    assert at.session_state["plan_base"].plan_rows()[0].key == "B-001"  # bản đã xem
    assert sheet.appends == [] and sheet.updates == []  # chưa ghi gì khi chưa bấm


def test_apply_writes_only_ticked_and_shows_result(project_root, sheet):
    """«Áp dụng»: chỉ ghi dòng đã tick, ghi RAW; bỏ tick một dòng thì dòng đó không ghi."""
    at = open_plan(project_root)
    paste(at, "Từ khóa chính\tNgày dự kiến\nsửa cửa kéo đài loan\t20/11/2027\n"
          "cửa nhôm xingfa\t21/11/2027\n")  # fmt: skip
    round_ = at.session_state["plan_round"]
    at.checkbox(key=f"plan-pick-{round_}-2").uncheck()
    run(at)
    click(at, "plan-apply")
    assert len(sheet.appends) == 1 and "sửa cửa kéo đài loan" in sheet.appends[0]
    assert all(option.get("valueInputOption") == "RAW" for option in sheet.update_options)
    assert any("Đã ghi 1 thay đổi" in s.value for s in at.success)
    assert "plan_base" not in at.session_state and "plan_proposals" not in at.session_state
    table = frame(at, "Mã bài")
    assert "sửa cửa kéo đài loan" in list(table["Từ khóa chính"])


def test_conflict_shows_before_now_proposed(project_root, sheet):
    """Dòng bị sửa ở nơi khác sau khi xem đề xuất: không ghi, hiện «trước / bây giờ / đề xuất»
    bằng ô bảng (chữ thuần)."""
    at = open_plan(project_root)
    paste(at, "Mã bài\tTừ khóa chính\tƯu tiên\nB-001\tsửa cửa cuốn kêu to\tCao\n")
    sheet.set(2, HEADER.index("Ưu tiên"), "Thấp")  # máy kia vừa sửa
    click(at, "plan-apply")
    assert sheet.updates == []
    table = frame(at, "Bây giờ trên Sheet")
    line = table.iloc[0]
    assert line["Trước (lúc duyệt)"] == "Trung bình"
    assert line["Bây giờ trên Sheet"] == "Thấp"
    assert line["Đề xuất"] == "Cao"
    assert any("chưa ghi" in w.value for w in at.warning)
    assert_plain(at)


def test_hostile_text_in_proposals_is_plain(project_root, sheet):
    """Chữ lạ trong đề xuất (ghi chú, tiêu đề dự kiến): bảng, ``st.text``, không link, không HTML,
    không ký tự đảo hướng (LC-T094-3, -32); xem đủ chữ (điều kiện (a) Lá Chắn T-100)."""
    at = open_plan(project_root)
    paste(at, f"Từ khóa chính\tGhi chú của thợ\nsửa cửa kéo đài loan\t{HOSTILE}\n")
    assert_plain(at)
    shown = texts(at)
    assert RLO not in shown and ZWSP not in shown
    assert any("[bấm](javascript:alert(1)) <b>đậm</b>" in t.value for t in at.text)


# ======================================================================= tải file


def test_file_too_big_is_refused_before_reading(project_root, sheet, monkeypatch):
    """File quá 1 MB: báo trước khi đọc byte (LC-T094-33)."""
    upload = FakeUpload("ke-hoach.csv", b"", size=model.MAX_FILE_BYTES + 1)
    choose_file(monkeypatch, upload)
    at = read(open_plan(project_root), "Tải file")
    assert any(parse.FILE_TOO_BIG in e.value.replace("\\", "") for e in at.error)
    assert upload.read is False


@pytest.mark.parametrize(
    ("name", "data", "message"),
    [
        ("ke-hoach.xlsx", b"PK\x03\x04", parse.FILE_BAD_TYPE),
        ("ke-hoach.csv", b"MZ\x90\x00\xff\xfe\x00", parse.FILE_BAD_ENCODING),
    ],
    ids=["xlsx", "exe-doi-duoi"],
)
def test_wrong_files_are_refused(project_root, sheet, monkeypatch, name, data, message):
    choose_file(monkeypatch, FakeUpload(name, data))
    at = read(open_plan(project_root), "Tải file")
    assert at.error and "plan_proposals" not in at.session_state
    shown = texts(at)
    assert name not in shown
    assert_plain(at)


def test_csv_file_gives_proposals(project_root, sheet, monkeypatch):
    data = "Từ khóa chính,Ngày dự kiến\nsửa cửa kéo đài loan,20/11/2027\n".encode()
    choose_file(monkeypatch, FakeUpload("ke-hoach.csv", data))
    at = read(open_plan(project_root), "Tải file")
    (item,) = at.session_state["plan_proposals"].items
    assert item.action.value == "Thêm" and item.after.keyword == "sửa cửa kéo đài loan"


# ======================================================================= AI đọc chữ tự do


def test_free_text_waits_for_click_then_ai_proposes(project_root, sheet, plan_ai):
    """Chữ tự do: báo tốn tiền, chỉ gọi AI khi bấm; đề xuất AI hiện như đề xuất bảng."""
    ai = plan_ai([suggestion("them", keyword="sửa cửa cuốn bị kẹt", reason="Ghi chú muốn thêm.")])
    at = paste(open_plan(project_root), "Tháng 11: thêm bài sửa cửa cuốn bị kẹt.")
    assert ai.prompts == []
    assert any("tốn tiền" in i.value for i in at.info)
    click(at, "plan-ai-go")
    assert len(ai.prompts) == 1
    (item,) = at.session_state["plan_proposals"].items
    assert item.source == "AI" and item.after.keyword == "sửa cửa cuốn bị kẹt"
    assert picks(at) == [True]


def test_phone_in_pasted_text_must_be_masked_or_confirmed(project_root, sheet, plan_ai):
    """Số điện thoại trong chữ dán: chưa gửi được khi chưa chọn; «Che rồi gửi» thì AI không thấy
    số (A3, LC-T094-21)."""
    ai = plan_ai([suggestion("them", keyword="sửa cửa cuốn bị kẹt")])
    at = paste(open_plan(project_root), "Anh Tư 0909 123 456 muốn bài sửa cửa cuốn bị kẹt.")
    assert at.button(key="plan-ai-go").disabled
    assert any("1 số điện thoại" in w.value for w in at.warning)
    click(at, "plan-ai-mask")
    assert len(ai.prompts) == 1 and "0909" not in ai.prompts[0]
    assert "123 456" not in ai.prompts[0]


def test_phone_in_plan_keyword_is_named_and_mask_disabled(project_root, sheet, plan_ai):
    """Số nằm ở từ khóa kế hoạch hiện tại (cũng gửi AI): báo rõ dòng nào, «Che» không dùng được,
    «Vẫn gửi» gửi khi người dùng đồng ý (điều kiện 3 Lá Chắn T-098)."""
    sheet.set(3, HEADER.index("Từ khóa chính"), "sơn cổng gọi 0909123456")
    ai = plan_ai([suggestion("them", keyword="sửa cửa cuốn bị kẹt")])
    at = paste(open_plan(project_root), "Thêm bài sửa cửa cuốn bị kẹt.")
    assert any("B-002" in sl44.shown(w.value) for w in at.warning)
    assert at.button(key="plan-ai-mask").disabled and at.button(key="plan-ai-go").disabled
    click(at, "plan-ai-anyway")
    assert len(ai.prompts) == 1


def test_ai_error_is_fixed_text(project_root, sheet, monkeypatch):
    from seo_app.ai import AIError

    class Broken:
        def generate(self, *args, **kwargs):
            raise AIError("Máy chủ AI đang bận. Thử lại sau.")

    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: Broken())
    at = paste(open_plan(project_root), "Thêm bài sửa cửa cuốn bị kẹt.")
    click(at, "plan-ai-go")
    assert any("Máy chủ AI đang bận" in e.value for e in at.error)
    assert "plan_proposals" not in at.session_state


# ======================================================================= link Google Sheets


def test_main_sheet_link_only_reloads(project_root, sheet):
    at = open_plan(project_root)
    at.session_state["plan_source"] = TAB_SHEET
    at.text_input(key="plan_link").input(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    read(at)
    assert sheet.reads == 2  # mở trang + tải lại
    assert "plan_proposals" not in at.session_state
    assert any("tải lại kế hoạch" in s.value for s in at.success)


@pytest.mark.parametrize(
    "link",
    [
        f"https://docs.google.com.evil.example/spreadsheets/d/{SHEET_ID}/edit",
        f"https://x@docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        "https://evil.example/ke-hoach",
    ],
    ids=["ten-may-gia", "co-at", "dia-chi-khac"],
)
def test_bad_sheet_link_is_refused_without_request(project_root, sheet, google, link):
    at = open_plan(project_root)
    before = len(google.requests)
    at.session_state["plan_source"] = TAB_SHEET
    at.text_input(key="plan_link").input(link)
    read(at)
    assert at.error and len(google.requests) == before
    assert "evil" not in texts(at)


def test_other_sheet_is_read_once_as_source(project_root, sheet, google):
    values = [HEADER, row("", "cửa sắt mỹ thuật")]
    read_url = sheet_read_url(OTHER_SHEET)
    google.on("GET", read_url, {"range": "'KeHoach'!A1:Z1001", "values": values})
    at = open_plan(project_root)
    at.session_state["plan_source"] = TAB_SHEET
    at.text_input(key="plan_link").input(f"https://docs.google.com/spreadsheets/d/{OTHER_SHEET}/")
    read(at)
    (item,) = at.session_state["plan_proposals"].items
    assert item.action.value == "Thêm" and item.after.keyword == "cửa sắt mỹ thuật"
    assert not [r for r in google.sheets_requests() if r.method != "GET"]


def sheet_read_url(sheet_id: str) -> str:
    from urllib.parse import quote

    from seo_app.google import sheets

    return f"{SHEETS}{sheet_id}/values/{quote(sheets.READ_RANGE, safe='')}"


# ======================================================================= viết bài, website


def status_writes(monkeypatch, sheet: FakePlanSheet) -> list[tuple[str, int, int, int]]:
    """Ghi lại mọi lần ``record_status`` (trang Soạn bài): trạng thái sẽ ghi, và số lệnh ghi ô,
    thêm dòng, sửa cấu trúc Sheet đã có **ngay trước** lần gọi đó."""
    from seo_app.plan import sync

    calls: list[tuple[str, int, int, int]] = []
    original = sync.record_status

    def spy(client, store, draft_id, write, **kwargs):
        calls.append((write.status, len(sheet.updates), len(sheet.appends), len(sheet.structure)))
        return original(client, store, draft_id, write, **kwargs)

    monkeypatch.setattr(sync, "record_status", spy)
    return calls


def test_write_button_opens_compose_without_wordpress(project_root, sheet, wordpress, monkeypatch):
    """«Viết bài»: đọc lại đúng dòng trên Sheet, mở Soạn bài với từ khóa; 0 request WordPress
    (LC-T094-35). Trang Kế hoạch tự nó chỉ đọc Sheet (Chỉ Huy chọn A, 30/10).

    Sau khi gộp T-102 (R5, Chỉ Huy B duyệt 30/10 19:05): trang Soạn bài mở từ dòng kế hoạch đọc
    lại dòng, ghi «Đang viết» **đúng một lần** qua ``record_status`` (lúc đó Sheet chưa có lệnh ghi
    nào: trang Kế hoạch không ghi), và bỏ ``_start_plan_key`` sau khi dùng."""
    writes = status_writes(monkeypatch, sheet)
    at = open_plan(project_root)
    reads = sheet.reads
    at.selectbox(key="plan-write-pick").select("B-002")
    run(at)
    click(at, "plan-write")
    # Đọc lại Sheet trước khi mở Soạn bài (LC-T094-29): trang Kế hoạch, trang Soạn bài, rồi
    # ``write_status`` đọc lại trước khi ghi.
    assert sheet.reads == reads + 3
    assert at.session_state["keyword"] == "sơn lại cổng sắt"
    assert "_start_plan_key" not in at.session_state and "_start_keyword" not in at.session_state
    assert at.session_state["_plan_ref"].key == "B-002"
    assert wordpress.requests == []
    assert writes == [(model.STATUS_WRITING, 0, 0, 0)]  # trang Kế hoạch không ghi gì trước đó
    assert len(sheet.updates) == 1 and sheet.appends == [] and sheet.structure == []
    assert {column for _row, column, _value in sheet.written_cells()} == {
        HEADER.index("Trạng thái"),
        HEADER.index("Cập nhật lúc"),
    }
    assert sheet.cell(3, HEADER.index("Trạng thái")) == model.STATUS_WRITING
    run(at)  # lần chạy sau: không đọc lại, không ghi lại
    assert len(writes) == 1 and len(sheet.updates) == 1


def test_write_button_reopens_existing_draft(project_root, sheet):
    """Đã có nháp gắn Mã bài này (Sheet đang dùng): mở nháp đó, không tạo nháp thứ hai."""
    store = DraftStore(drafts.DEFAULT_DRAFTS_FILE)
    ref = DraftPlanRef(
        key="B-002", sheet_hash=sheet_hash(SHEET_ID), status="Đang viết",
        opened_at=datetime(2026, 10, 30, 9, 0, tzinfo=model.TIMEZONE),
    )  # fmt: skip
    saved = store.save(DraftSnapshot(keyword="sơn lại cổng sắt", plan=ref))
    at = open_plan(project_root)
    at.session_state["_start_plan_key"] = "B-009"  # khóa của lần bấm trước, chưa ai đọc
    at.selectbox(key="plan-write-pick").select("B-002")
    run(at)
    reads = sheet.reads
    click(at, "plan-write")
    assert at.session_state["draft_id"] == saved.id
    assert len(store.list_drafts().drafts) == 1
    assert "_start_plan_key" not in at.session_state  # không sót Mã bài cũ
    assert sheet.reads == reads and sheet.updates == [] and sheet.appends == []


def test_update_old_kind_cannot_be_written(project_root, sheet):
    sheet.set(2, HEADER.index("Loại trang"), "Cập nhật bài cũ")
    at = open_plan(project_root)
    at.selectbox(key="plan-write-pick").select("B-001")
    run(at)
    assert at.button(key="plan-write").disabled


def test_website_status_is_read_only(project_root, sheet, wordpress):
    """«Trạng thái trên website»: chỉ đọc (GET), nhãn «Lỡ lịch» khi hẹn giờ quá giờ, không ghi
    Sheet, không sửa bài."""
    sheet.set(3, HEADER.index("Trạng thái"), "Đã hẹn giờ")
    late = (datetime.now(UTC) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
    wordpress.on(
        "GET",
        "/wp-json/wp/v2/posts",
        [{"id": 501, "status": "future", "date_gmt": late, "modified_gmt": late, "link": ""}],
    )
    at = open_plan(project_root)
    click(at, "plan-web")
    table = frame(at, "Trên website")
    assert list(table["Trên website"]) == ["", "", "Lỡ lịch"]
    assert {r.method for r in wordpress.requests} == {"GET"}
    assert sheet.updates == [] and sheet.appends == []


def test_pending_status_write_retries_only_sheet(project_root, sheet, wordpress):
    """Việc ghi trạng thái còn nợ: chỉ thử lại khi bấm, chỉ ghi Sheet, không gửi WordPress."""
    store = DraftStore(drafts.DEFAULT_DRAFTS_FILE)
    saved = store.save(DraftSnapshot(keyword="sơn lại cổng sắt"))
    write = PlanStatusWrite(
        key="B-002", sheet_hash=sheet_hash(SHEET_ID), status=model.STATUS_DRAFT_SENT,
        wp_post_id=502, expect_status="Chưa viết",
        created_at=datetime(2026, 10, 30, 9, 0, tzinfo=model.TIMEZONE),
    )  # fmt: skip
    store.save_plan_write(saved.id, write)
    at = open_plan(project_root)
    assert any("chưa ghi được trạng thái" in w.value for w in at.warning)
    assert sheet.updates == []
    click(at, "plan-retry")
    assert sheet.cell(3, HEADER.index("Trạng thái")) == model.STATUS_DRAFT_SENT
    assert wordpress.requests == []


def test_business_profile_is_read_only_plain(project_root):
    at = open_plan(project_root)
    assert any("Thông tin nền" in m.value for m in at.markdown)
    assert at.text and "Pro-Metal" in at.text[0].value
    assert not any(t.label.startswith("Doanh nghiệp") for t in at.text_input)


def test_business_profile_headings_are_plain(project_root, monkeypatch):
    """Tên mục của hồ sơ doanh nghiệp (file chủ dự án tự sửa) hiện bằng ``escape_markdown``: không
    thành link, định dạng; ký tự đảo hướng chữ không qua ``st.markdown`` thô."""
    import dataclasses

    import seo_app.content as content

    original = content.load_rules

    def hostile_rules(*args, **kwargs):
        profile = f"## [bấm](javascript:alert(1)) **đậm** <b>x</b>\n- ý\n## Mục 2 {HOSTILE}\n"
        return dataclasses.replace(original(*args, **kwargs), business_profile=profile)

    monkeypatch.setattr(content, "load_rules", hostile_rules)
    at = open_plan(project_root)
    assert_plain(at)
    assert any("javascript" in m.value for m in at.markdown)  # chữ vẫn hiện, đã escape

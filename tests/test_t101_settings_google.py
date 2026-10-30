"""Cài đặt → 📗 Google (T-101; thiết kế T-094 mục 2.1, 2.4; Lá Chắn LC-T094-12, -15, -31, -34 và
điều kiện 3 Lá Chắn T-097).

Google giả (``FakeGoogle`` + ``FakePlanSheet``), khóa tài khoản dịch vụ sinh lúc chạy test, ``.env``
là file tạm. Không gọi mạng thật.
"""

from __future__ import annotations

import json
import os

import pytest
import test_t101_plan_page as plan_page
from fake_google import EMAIL, SHEET_ID, key_info
from fake_plan_sheet import HEADER, FakePlanSheet
from streamlit.testing.v1 import AppTest

import seo_app.config as config

env = plan_page.env
caches = plan_page.caches
private_key = plan_page.private_key
google = plan_page.google
run = plan_page.run
click = plan_page.click
TAB = "📗 Google"
RLO = plan_page.RLO


@pytest.fixture
def env_path(monkeypatch, tmp_path):
    """``.env`` tạm (không bao giờ đụng ``.env`` thật)."""
    path = tmp_path / ".env"
    path.write_text("APP_TIMEZONE=Asia/Ho_Chi_Minh\n", encoding="utf-8")
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def open_settings(project_root) -> AppTest:
    return plan_page.pages.open_page(project_root, "settings.py")


def google_tab(at: AppTest):
    return next(tab for tab in at.tabs if tab.label == TAB)


def assert_tab_plain(at: AppTest) -> None:
    """Chữ thuần trong tab Google (không link, không HTML; LC-T094-3). Các tab khác có link cố
    định của phiếu cũ (nơi lấy khóa AI) nên không quét cả trang."""
    assert not at.exception, at.exception
    for element in plan_page.sl44.markdown_elements(google_tab(at)):
        assert plan_page.sl44.cm_problems(element.value) == [], element.value
        assert not getattr(element.proto, "allow_html", False), element.value


def everything(at: AppTest) -> str:
    """Mọi chuỗi trong mọi phần tử của trang (cả nhãn, gợi ý, ô nhập, mã), mọi tab."""
    from google.protobuf.json_format import MessageToDict

    found: list[str] = []

    def strings(value):
        if isinstance(value, str):
            found.append(value)
        elif isinstance(value, dict):
            for item in value.values():
                strings(item)
        elif isinstance(value, list):
            for item in value:
                strings(item)

    def walk(node):
        proto = getattr(node, "proto", None)
        if proto is not None:
            strings(MessageToDict(proto))
        for child in getattr(node, "children", {}).values():
            walk(child)

    walk(at.main)
    return "\n".join(found)


def test_tab_order_keeps_existing_tabs(project_root):
    """Tab Google đặt cuối: các tab đã có giữ đúng vị trí (test cũ tìm tab «Kết nối» ở vị trí 3)."""
    at = open_settings(project_root)
    labels = [tab.label for tab in at.tabs]
    assert labels[:4] == ["✍️ Văn phong", "🤖 Mô hình AI", "🖼️ Ảnh", "🔌 Kết nối"]
    assert labels[4] == TAB


def test_not_declared_shows_status_only(project_root):
    at = open_settings(project_root)
    tab = google_tab(at)
    badges = [m.value for m in tab.markdown if "badge" in m.value]
    assert badges == [":gray-badge[⚪ Chưa khai báo]", ":gray-badge[⚪ Chưa khai báo]"]
    assert tab.button(key="google-check-btn").disabled
    assert tab.button(key="google-prepare-btn").disabled


def test_declared_shows_file_name_email_never_path_or_key(project_root, google, private_key):
    """Chỉ tên file khóa, email dịch vụ; không đường dẫn đầy đủ, không nội dung khóa, không mã
    Sheet đầy đủ (LC-T094-12, -15)."""
    at = open_settings(project_root)
    tab = google_tab(at)
    shown = everything(at)
    key_file = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
    assert "du\\-an\\-thu\\-0123abcd\\.json" in shown or "du-an-thu-0123abcd.json" in shown
    assert EMAIL in [c.value for c in tab.code]
    assert key_file not in shown and os.path.dirname(key_file) not in shown
    assert SHEET_ID not in shown and SHEET_ID[-4:] in shown
    info = key_info(private_key)
    pem_header = "BEGIN PRIVATE" + " KEY"  # tách chữ để bộ quét bí mật không bắt nhầm dòng test
    for secret in (info["private_key"][40:80], info["private_key_id"], pem_header):
        assert secret not in shown
    assert not tab.button(key="google-check-btn").disabled
    assert google.requests == []  # mở trang không gọi Google
    assert_tab_plain(at)


def test_key_file_problem_is_fixed_text(project_root, google, monkeypatch, tmp_path):
    """File khóa hỏng có mồi trong nội dung: câu cố định, không chép nội dung file (LC-T094-2)."""
    bad = tmp_path / "bi-mat" / "khoa-hong.json"
    field = "private" + "_key"  # tên trường qua biến: bộ quét bí mật không bắt nhầm mồi giả
    bad.write_text(json.dumps({"type": "user", field: "MOI-BI-MAT-123"}), encoding="utf-8")
    if os.name != "nt":
        bad.chmod(0o600)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(bad))
    at = open_settings(project_root)
    tab = google_tab(at)
    assert tab.error
    shown = everything(at)
    assert "MOI-BI-MAT" not in shown and str(bad) not in shown
    assert tab.button(key="google-check-btn").disabled


def test_file_name_with_odd_characters_is_cleaned(project_root, google, monkeypatch, tmp_path,
                                                  private_key):  # fmt: skip
    """Tên file khóa có ký tự đảo hướng (Mac/Linux đặt được): hiện «�», cô lập, không link."""
    newline = "" if os.name == "nt" else chr(10)  # Windows không cho xuống dòng trong tên file
    name = f"khoa{RLO}nosj.[x](y){newline}.json"
    path = tmp_path / "bi-mat" / name
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(path))
    at = open_settings(project_root)
    shown = everything(at)
    assert RLO not in shown and "](y)" not in shown
    assert_tab_plain(at)


def test_save_sheet_link_writes_env_and_masks_id(project_root, google, env_path):
    """Dán link Sheet: ghi ``GOOGLE_SHEET_ID`` (bộ kiểm riêng), câu báo chỉ 4 ký tự cuối."""
    at = open_settings(project_root)
    at.text_input(key="google-sheet-link").input(
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"
    )
    click(at, "google-sheet-save")
    assert f"GOOGLE_SHEET_ID={SHEET_ID}" in env_path.read_text(encoding="utf-8")
    assert at.text_input(key="google-sheet-link").value == ""
    assert any(SHEET_ID[-4:] in s.value for s in google_tab(at).success)
    assert SHEET_ID not in everything(at)


@pytest.mark.parametrize(
    "link",
    [
        f"https://docs.google.com.evil.example/spreadsheets/d/{SHEET_ID}/edit",
        f"https://x@docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"{SHEET_ID}\nWORDPRESS_URL=https://evil.example",
        'abc"=def',
    ],
    ids=["ten-may-gia", "co-at", "xuong-dong", "dau-nhay"],
)
def test_bad_link_does_not_touch_env(project_root, google, env_path, link):
    before = env_path.read_text(encoding="utf-8")
    at = open_settings(project_root)
    at.text_input(key="google-sheet-link").input(link)
    click(at, "google-sheet-save")
    assert env_path.read_text(encoding="utf-8") == before
    assert google_tab(at).error
    assert "evil" not in everything(at).replace("docs.google.com.evil.example", "")
    assert google.requests == []


def test_check_connection_shows_sheet_title(project_root, google):
    """«Kiểm tra kết nối»: chỉ khi bấm; hiện tên Sheet (chữ thuần) và có tab «KeHoach» chưa."""
    FakePlanSheet(google, [HEADER])
    at = open_settings(project_root)
    assert google.requests == []
    click(at, "google-check-btn")
    texts = [s.value for s in google_tab(at).success]
    assert any("Kế hoạch SEO" in t and "đã có" in t for t in texts)
    assert_tab_plain(at)


def test_check_connection_error_is_fixed_text(project_root, google):
    sheet = FakePlanSheet(google, [HEADER])
    sheet.fail("info", (403, {"error": {"message": "MOI-loi-may-chu"}}))
    at = open_settings(project_root)
    click(at, "google-check-btn")
    tab = google_tab(at)
    assert tab.error and "MOI" not in everything(at)


def test_prepare_sheet_only_on_click_and_add_missing(project_root, google):
    """«Chuẩn bị trang tính»: chỉ khi bấm; tab đã có dữ liệu mà thiếu cột thì báo, «Thêm cột còn
    thiếu» ghi tiêu đề vào cuối dòng 1, không dời cột có sẵn (LC-T094-31)."""
    sheet = FakePlanSheet(google, [["Mã bài", "Từ khóa chính", "Cột riêng"], ["B-001", "a b"]])
    at = open_settings(project_root)
    assert sheet.structure == [] and sheet.updates == []
    click(at, "google-prepare-btn")
    assert sheet.updates == []  # thiếu cột: chỉ báo, chưa ghi tiêu đề
    assert any("còn thiếu" in s.value for s in google_tab(at).success)
    click(at, "google-add-columns")
    assert sheet.cell(1, 0) == "Mã bài" and sheet.cell(1, 2) == "Cột riêng"
    assert sheet.cell(1, 3) == "Từ khóa phụ, ý cần có"
    assert all("deleteSheet" not in str(r) and "deleteDimension" not in str(r)
               for r in sheet.structure)  # fmt: skip


def test_prepare_creates_tab_when_missing(project_root, google):
    sheet = FakePlanSheet(google, [], tabs=[(0, "Trang tính1"), (5, "KeHoach (cũ)")])
    at = open_settings(project_root)
    click(at, "google-prepare-btn")
    assert any("addSheet" in str(r) for r in sheet.structure)
    assert any("Đã tạo trang tính" in s.value for s in google_tab(at).success)

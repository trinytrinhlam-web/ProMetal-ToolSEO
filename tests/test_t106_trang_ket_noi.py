"""Trang Kết nối WordPress: cảnh báo quyền ``unfiltered_html`` (T-106) và bài nháp thử không có
ảnh (T-108, LC-T093-1).

Phần lớn test đi qua client WordPress THẬT với WordPress giả (cách nối của
``tests/test_soi_loi_t044.py``: ``_request``, ``_json``, ``check_connection`` thật); vài ca thay
``check_connection`` để dựng dữ liệu lạ. Không gọi mạng thật.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
import streamlit
import test_soi_loi_t044 as sl44
from streamlit.testing.v1 import AppTest

from seo_app.wordpress import ConnectionInfo, WordPressClient

fake_wp = sl44.fake_wp  # mọi WordPressClient trên trang dùng WordPress giả
ROOT = sl44.ROOT
CAN_WRITE = {"edit_posts": True, "publish_posts": True, "upload_files": True}
USERNAME = "tai-khoan-t106"
APP_PASSWORD = "pass t106 wxyz"

GPS_LOST = "mất vị trí GPS khi xem trên điện thoại"
UNKNOWN = "Chưa biết ảnh trong bài có giữ được vị trí GPS"
ASK_EDITOR = "Biên tập viên (Editor)"
ALREADY_EDITOR = "đã ở vai trò Biên tập viên trở lên"


@pytest.fixture(autouse=True)
def account(fake_wp, monkeypatch):
    """Tên đăng nhập, mật khẩu ứng dụng dễ nhận ra, để kiểm câu báo không chép lại."""
    monkeypatch.setenv("WORDPRESS_USERNAME", USERNAME)
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", APP_PASSWORD)


def me(roles, capabilities) -> dict:
    answer = {"name": "Lâm", "roles": roles}
    if capabilities is not None:
        answer["capabilities"] = capabilities
    return answer


def connect(project_root, fake_wp, answer: dict) -> AppTest:
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", answer)
    at = sl44.open_wordpress_page(project_root)
    sl44.button(at, "Kiểm tra kết nối").click().run()
    sl44.assert_page_plain(at)
    assert len(at.success) == 1  # kết nối thành công
    return at


def gps_notes(at: AppTest) -> list[tuple[str, str]]:
    """Các câu báo về GPS của ảnh trong bài: (loại, chữ người đọc thấy)."""
    return [
        (kind, sl44.shown(el.value))
        for kind in ("warning", "info")
        for el in getattr(at, kind)
        if "GPS" in el.value
    ]


def assert_no_account_details(text: str) -> None:
    """Yêu cầu 4 của T-106: câu báo không có tên đăng nhập, mật khẩu, đường dẫn."""
    for secret in (USERNAME, APP_PASSWORD, "example.com", "https://", "Lâm", "/wp-json"):
        assert secret not in text, secret


# ======================================================================= T-106: unfiltered_html


@pytest.mark.parametrize("role", ["editor", "administrator"])
def test_account_with_unfiltered_html_shows_nothing_more(project_root, fake_wp, role):
    """Có quyền: không thêm câu nào về GPS (yêu cầu 3)."""
    at = connect(project_root, fake_wp, me([role], {**CAN_WRITE, "unfiltered_html": True}))
    assert gps_notes(at) == []
    assert not at.warning and not at.info


@pytest.mark.parametrize(
    "capabilities",
    [
        {**CAN_WRITE, "unfiltered_html": False},
        CAN_WRITE,  # WordPress không liệt kê quyền này: tài khoản không có
        {**CAN_WRITE, "unfiltered_html": "true"},  # sai kiểu: không coi là có
    ],
    ids=["false", "khong-co-khoa", "chuoi"],
)
def test_author_without_unfiltered_html_is_told_to_use_editor(project_root, fake_wp, capabilities):
    """Thiếu quyền, vai thấp hơn Biên tập viên: cảnh báo dễ hiểu (ảnh mất GPS trên điện thoại),
    khuyên vai Biên tập viên, không khuyên Quản trị viên (yêu cầu 1, 4)."""
    at = connect(project_root, fake_wp, me(["author"], capabilities))
    [(kind, text)] = gps_notes(at)
    assert kind == "warning"
    assert GPS_LOST in text and ASK_EDITOR in text
    assert "Không cần, và không nên, nâng lên Quản trị viên." in text
    assert "Quản trị viên (Administrator)" not in text and ALREADY_EDITOR not in text
    assert_no_account_details(text)


@pytest.mark.parametrize("role", ["editor", "administrator"])
def test_editor_without_unfiltered_html_is_told_site_disables_it(project_root, fake_wp, role):
    """Đã là Biên tập viên mà vẫn thiếu (``DISALLOW_UNFILTERED_HTML``, website nhiều site con):
    báo người làm web, không khuyên nâng quyền."""
    at = connect(project_root, fake_wp, me([role], {**CAN_WRITE, "unfiltered_html": False}))
    [(kind, text)] = gps_notes(at)
    assert kind == "warning"
    assert GPS_LOST in text and ALREADY_EDITOR in text and "người làm web" in text
    assert "Đừng nâng tài khoản lên Quản trị viên" in text
    assert ASK_EDITOR not in text
    assert_no_account_details(text)


@pytest.mark.parametrize(
    ("roles", "capabilities"),
    [
        (["editor"], None),  # câu trả lời không có capabilities
        (["editor"], ["unfiltered_html"]),  # capabilities sai kiểu
        (["subscriber"], {"read": True}),  # tài khoản quá thấp để xét
    ],
    ids=["thieu", "sai-kieu", "subscriber"],
)
def test_unknown_permissions_give_neutral_note(project_root, fake_wp, roles, capabilities):
    """Không biết: một câu trung tính (``st.info``), không cảnh báo mất GPS (yêu cầu 2)."""
    at = connect(project_root, fake_wp, me(roles, capabilities))
    [(kind, text)] = gps_notes(at)
    assert kind == "info" and text.startswith(UNKNOWN)
    assert GPS_LOST not in text and "Quản trị viên" not in text
    assert_no_account_details(text)


def test_old_connection_object_without_the_field_is_unknown(project_root, monkeypatch):
    """Đối tượng kết nối không có ``can_unfiltered_html`` (dựng kiểu cũ): coi là không biết, không
    cảnh báo oan (Ghi nhận 4 Soi Lỗi T-091)."""
    info = SimpleNamespace(
        site_name="ProMetal",
        site_url="https://example.com",
        user_name="Lâm",
        roles=("editor",),
        can_edit_posts=True,
        can_publish_posts=True,
        can_upload_files=True,
        siteseo_status="SiteSEO: ghi được",
    )
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at = sl44.open_wordpress_page(project_root)
    sl44.button(at, "Kiểm tra kết nối").click().run()
    assert not at.exception, at.exception
    [(kind, text)] = gps_notes(at)
    assert kind == "info" and text.startswith(UNKNOWN)


def test_odd_roles_do_not_crash_and_editor_is_found(project_root, monkeypatch):
    """Vai trò sai kiểu (số, None, danh sách) không làm vỡ trang; vẫn nhận ra «editor»."""
    info = ConnectionInfo(
        "ProMetal", "https://example.com", "Lâm", (1, None, ["editor"], "editor"),
        True, True, True, can_unfiltered_html=False,
    )  # fmt: skip
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at = sl44.open_wordpress_page(project_root)
    sl44.button(at, "Kiểm tra kết nối").click().run()
    sl44.assert_page_plain(at)
    [(kind, text)] = gps_notes(at)
    assert kind == "warning" and ALREADY_EDITOR in text


def test_page_still_has_no_html(project_root):
    """Câu báo hiện bằng ``st.warning``/``st.info`` (Markdown thường, ``connect`` đã kiểm không
    link, không HTML); trang vẫn không dùng ``unsafe_allow_html`` (U1)."""
    source = (project_root / "app" / "views" / "wordpress.py").read_text(encoding="utf-8")
    assert "unsafe_allow_html" not in source.split('"""', 2)[2]


# ======================================================================== T-108: tạo thử bài nháp


def test_draft_form_has_no_image_field(project_root, fake_wp):
    """Mục «Tạo thử một bài nháp» không còn ô chọn ảnh, ô alt; có lời dặn dùng «Gửi nháp»."""
    at = sl44.open_wordpress_page(project_root)
    assert at.get("file_uploader") == []
    labels = [t.label for t in at.text_input]
    assert labels == ["Tiêu đề"]
    assert any("«Gửi nháp» ở trang Soạn bài" in c.value for c in at.caption)
    source = (project_root / "app" / "views" / "wordpress.py").read_text(encoding="utf-8")
    assert "upload_media" not in source and "file_uploader" not in source


def test_test_draft_is_text_only_and_never_uploads(project_root, fake_wp, monkeypatch):
    """Nút tạo thử vẫn tạo bài nháp chữ thuần (yêu cầu 1); không lệnh nào lên thư viện Media,
    kể cả khi có ``file_uploader`` trả file (W2, F1)."""
    asked = []
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: asked.append(1))
    post = {"id": 42, "status": "draft", "title": {"raw": "Bài thử"}}
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (201, post, {}))
    at = sl44.open_wordpress_page(project_root)
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    at.text_area[0].input("Đoạn một.\n\nĐoạn hai.")
    sl44.button(at, "Tạo bài nháp").click().run()

    sl44.assert_page_plain(at)
    assert sl44.shown(at.success[0].value) == "Đã tạo bài nháp #42: **Bài thử**"
    assert [b.label for b in at.get("link_button")] == ["Mở bài trong trang quản trị WordPress"]
    assert not any("Ảnh đại diện" in m.value for m in at.markdown)
    assert not asked
    paths = [r.url.split("?")[0] for r in fake_wp.requests]
    assert not [p for p in paths if "/wp/v2/media" in p]
    posted = [r for r in fake_wp.requests if r.url.split("?")[0].endswith("/wp/v2/posts")]
    assert len(posted) == 1
    body = json.loads(posted[0].body)
    assert body["status"] == "draft" and body.get("featured_media") is None
    assert body["content"] == "<p>Đoạn một.</p>\n<p>Đoạn hai.</p>"

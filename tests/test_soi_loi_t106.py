"""Soi Lỗi T-106 + T-108 (rút gọn): trang Kết nối WordPress.

Kiểm độc lập (website giả riêng ``_Site``, adapter ``requests`` ghi mọi lệnh gửi đi; không dùng
``FakeWordPress``, hàm mở trang hay bảng kỳ vọng của Họa Sĩ):

1. Trang không còn đường nào tải ảnh lên website: đọc cây cú pháp ``app/views/wordpress.py``
   (mọi lệnh gọi client, mọi ô nhận file), chạy cả trang (kiểm kết nối, tải chuyên mục và thẻ,
   tạo nháp) với ô chọn file giả luôn trả một ảnh, ghi mọi lệnh gửi đi.
2. Nút tạo thử tạo đúng một bài nháp chữ, ``status: draft``, không ``featured_media``.
3. Câu báo quyền ``unfiltered_html``: có quyền, thiếu (theo vai), không biết; câu không chép tên
   đăng nhập, mật khẩu, địa chỉ, tên site, tên tài khoản; không khuyên nâng lên Quản trị viên.

Không gọi website thật (bộ chặn mạng của ``tests/conftest.py`` bật suốt).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests
import streamlit
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict
from streamlit.testing.v1 import AppTest

from seo_app.auth import hash_password
from seo_app.wordpress import WordPressClient
from seo_app.wordpress.client import SITESEO_ABILITY_PATH

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app" / "views" / "wordpress.py"
MAT_KHAU_APP = "soi-loi-t106-dang-nhap"
TEN_DANG_NHAP = "bien-tap-t106"
MAT_KHAU_UNG_DUNG = "t106a bcde fghi jklm"  # Application Password giả
SITE = "https://site-t106.example"
TEN_SITE = "Cửa Sắt T106"
TEN_HIEN = "Người Thử T106"
API = "/wp-json"
WRITE = {"edit_posts": True, "publish_posts": True, "upload_files": True}
CONTRIBUTOR = {"read": True, "edit_posts": True, "delete_posts": True}  # Cộng tác viên lõi
_ABSENT = object()
TEXT_KINDS = ("title", "header", "subheader", "caption", "markdown", "success", "error", "warning",
              "info")


class _Chosen:
    """Như ``UploadedFile``: lỡ trang còn gọi ô chọn file thì nhận ảnh này và tải lên."""

    name = "IMG_0001 so seri.jpg"

    def getvalue(self) -> bytes:
        return b"\xff\xd8\xff\xe1 Exif SERIAL-T106 \xff\xd9"


class _Site(BaseAdapter):
    """WordPress giả: trả lời đúng các đường trang dùng, nhận cả lệnh tải ảnh (201) để nếu trang
    lỡ tải thì lệnh đi trót lọt và nằm trong ``sent``."""

    def __init__(self) -> None:
        super().__init__()
        self.me: dict = {"name": TEN_HIEN, "roles": ["editor"],
                         "capabilities": {**WRITE, "unfiltered_html": True}}
        self.sent: list[requests.PreparedRequest] = []
        self.offered: list[int] = []  # số lần trang gọi ô chọn file

    def send(self, request, **kwargs):
        self.sent.append(request)
        path = urlsplit(request.url).path
        if request.method == "GET" and path == f"{API}/":
            status, body = 200, {"name": TEN_SITE, "home": SITE, "namespaces": ["wp/v2"]}
        elif request.method == "GET" and path == f"{API}/wp/v2/users/me":
            status, body = 200, self.me
        elif request.method == "GET" and path == f"{API}/wp/v2/categories":
            status, body = 200, [{"id": 3, "name": "Cửa sắt", "slug": "cua-sat", "count": 1}]
        elif request.method == "GET" and path == f"{API}/wp/v2/tags":
            status, body = 200, [{"id": 7, "name": "inox", "slug": "inox", "count": 0}]
        elif request.method == "POST" and path == f"{API}/wp/v2/posts":
            sent = json.loads(request.body)
            status, body = 201, {"id": 42, "status": sent.get("status"),
                                 "title": {"raw": sent.get("title")}, "link": f"{SITE}/?p=42"}
        elif request.method == "POST" and path.startswith(f"{API}/wp/v2/media"):
            status, body = 201, {"id": 9, "source_url": f"{SITE}/wp-content/uploads/a.jpg"}
        else:  # Abilities của SiteSEO, mọi đường khác: chưa bật
            status, body = 404, {"code": "rest_no_route", "message": "không có"}
        response = requests.Response()
        response.status_code = status
        response._content = json.dumps(body).encode()
        response.headers = CaseInsensitiveDict({"Content-Type": "application/json; charset=UTF-8"})
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass

    def routes(self) -> set[tuple[str, str]]:
        return {(r.method, urlsplit(r.url).path) for r in self.sent}


@pytest.fixture
def site(monkeypatch) -> _Site:
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(MAT_KHAU_APP, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", SITE)
    monkeypatch.setenv("WORDPRESS_USERNAME", TEN_DANG_NHAP)
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", MAT_KHAU_UNG_DUNG)
    fake = _Site()
    original = WordPressClient.from_settings.__func__

    def from_settings(cls, settings, **kwargs):
        session = requests.Session()
        session.mount("https://", fake)
        return original(cls, settings, session=session, **kwargs)

    def file_uploader(*_args, **_kwargs):
        fake.offered.append(1)
        return _Chosen()

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    monkeypatch.setattr(streamlit, "file_uploader", file_uploader)
    return fake


def open_page(project_root: Path) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(MAT_KHAU_APP)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception, at.exception
    return at


def click(at: AppTest, label: str) -> None:
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception


def texts(at: AppTest) -> list[tuple[str, str]]:
    return [(kind, el.value) for kind in TEXT_KINDS for el in getattr(at, kind)]


def gps_notes(at: AppTest) -> list[tuple[str, str]]:
    return [(kind, value) for kind, value in texts(at)
            if kind in ("warning", "info") and "GPS" in value]


# ================================================================ 1. không còn đường tải ảnh
def _client_calls(tree: ast.AST) -> list[ast.Call]:
    return [node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "client"]


def test_trang_chi_goi_bon_lenh_client_va_khong_co_o_nhan_file():
    tree = ast.parse(PAGE.read_text(encoding="utf-8"))
    assert {call.func.attr for call in _client_calls(tree)} == {
        "check_connection", "list_categories", "list_tags", "create_draft"}
    names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    names |= {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    for banned in ("file_uploader", "camera_input", "upload_media", "upload_media_file",
                   "_post_media", "create_draft_with_images", "set_featured_image", "_request",
                   "getvalue", "requests"):
        assert banned not in names, banned
    [draft] = [call for call in _client_calls(tree) if call.func.attr == "create_draft"]
    assert all(keyword.arg is not None for keyword in draft.keywords)  # không ``**kwargs``
    for keyword in draft.keywords:
        if keyword.arg == "featured_media":
            assert isinstance(keyword.value, ast.Constant) and keyword.value.value is None


def test_ca_app_chi_buoc_gui_nhap_cua_soan_bai_tai_anh():
    hits: dict[str, set[str]] = {}
    for path in sorted((ROOT / "app").rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and node.attr in (
                "upload_media", "upload_media_file", "_post_media", "create_draft_with_images",
                "set_featured_image",
            ):
                hits.setdefault(path.relative_to(ROOT).as_posix(), set()).add(node.attr)
    assert hits == {"app/views/write.py": {"create_draft_with_images"}}


def test_ca_trang_chi_gui_mot_lenh_ghi_la_bai_nhap_chu(project_root, site):
    at = open_page(project_root)
    click(at, "Kiểm tra kết nối")
    click(at, "Tải chuyên mục và thẻ")
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài <b>thử</b> [gallery]")
    at.text_area[0].input("Đoạn một.\n\nĐoạn hai có <img src=x onerror=alert(1)>.")
    at.multiselect[0].select(at.multiselect[0].options[0])
    at.multiselect[1].select(at.multiselect[1].options[0])
    click(at, "Tạo bài nháp")

    assert site.offered == []  # trang không hỏi file nào
    assert site.routes() <= {
        ("GET", f"{API}/"), ("GET", f"{API}/wp/v2/users/me"),
        ("GET", f"{API}{SITESEO_ABILITY_PATH}"), ("GET", f"{API}/wp/v2/categories"),
        ("GET", f"{API}/wp/v2/tags"), ("POST", f"{API}/wp/v2/posts"),
    }
    writes = [r for r in site.sent if r.method != "GET"]
    assert [urlsplit(r.url).path for r in writes] == [f"{API}/wp/v2/posts"]
    body = json.loads(writes[0].body)
    assert body["status"] == "draft"
    assert set(body) <= {"status", "title", "content", "categories", "tags"}
    assert (body["categories"], body["tags"]) == ([3], [7])
    assert "<img" not in body["content"] and "<b>" not in body["title"]
    assert any("Đã tạo bài nháp #42" in value for kind, value in texts(at) if kind == "success")
    for _kind, value in texts(at):
        assert "SERIAL-T106" not in value and "IMG_0001" not in value and "uploads" not in value


# ================================================================ 2. quyền unfiltered_html
CASES = {
    "editor-co": (["editor"], {**WRITE, "unfiltered_html": True}, None),
    "admin-co": (["administrator"], {**WRITE, "unfiltered_html": True}, None),
    "author-duoc-cap-them": (["author"], {**WRITE, "unfiltered_html": True}, None),
    "author-thieu": (["author"], WRITE, "ask"),
    "author-false": (["author"], {**WRITE, "unfiltered_html": False}, "ask"),
    "author-so-1": (["author"], {**WRITE, "unfiltered_html": 1}, "ask"),
    "author-chu-true": (["author"], {**WRITE, "unfiltered_html": "true"}, "ask"),
    "contributor": (["contributor"], CONTRIBUTOR, "ask"),
    "editor-bi-bo": (["editor"], {**WRITE, "unfiltered_html": False}, "already"),
    "admin-bi-bo": (["administrator"], WRITE, "already"),
    "author-va-editor": (["author", "editor"], WRITE, "already"),
    "khong-capabilities": (["editor"], _ABSENT, "unknown"),
    "capabilities-null": (["editor"], None, "unknown"),
    "capabilities-danh-sach": (["editor"], ["edit_posts", "unfiltered_html"], "unknown"),
    "capabilities-chu": (["editor"], "unfiltered_html", "unknown"),
    "capabilities-rong": (["editor"], {}, "unknown"),
    "subscriber": (["subscriber"], {"read": True}, "unknown"),
    "edit-posts-chu": (["author"], {"edit_posts": "true", "unfiltered_html": False}, "unknown"),
}


def _assert_note_is_safe(text: str) -> None:
    for piece in (TEN_DANG_NHAP, MAT_KHAU_UNG_DUNG, MAT_KHAU_UNG_DUNG.replace(" ", ""), SITE,
                  "site-t106", TEN_SITE, TEN_HIEN, "wp-json", "http", "](", "<", "Administrator"):
        assert piece not in text, piece


@pytest.mark.parametrize(("roles", "capabilities", "expected"), CASES.values(), ids=CASES)
def test_cau_bao_unfiltered_html_theo_tung_truong_hop(project_root, site, roles, capabilities,
                                                     expected):
    site.me = {"name": TEN_HIEN, "roles": roles}
    if capabilities is not _ABSENT:
        site.me["capabilities"] = capabilities
    at = open_page(project_root)
    click(at, "Kiểm tra kết nối")
    assert any("Kết nối thành công" in value for kind, value in texts(at) if kind == "success")
    notes = gps_notes(at)
    if expected is None:
        assert notes == []
        return
    [(kind, text)] = notes
    _assert_note_is_safe(text)
    if expected == "unknown":
        assert kind == "info" and "mất vị trí GPS" not in text and "Chưa biết" in text
        return
    assert kind == "warning" and "mất vị trí GPS" in text
    assert "không nên, nâng lên Quản trị viên" in text or "Đừng nâng tài khoản lên Quản trị viên" \
        in text
    if expected == "ask":
        assert "Biên tập viên (Editor)" in text and "người làm web" not in text
    else:
        assert "người làm web" in text and "Biên tập viên (Editor)" not in text


def test_vai_tro_la_tu_website_khong_vao_cau_bao(project_root, site):
    site.me = {"name": TEN_HIEN, "capabilities": WRITE,
               "roles": ["author", "[x](https://evil.example)", "<b>editor</b>", "editor​"]}
    at = open_page(project_root)
    click(at, "Kiểm tra kết nối")
    [(kind, text)] = gps_notes(at)
    assert kind == "warning" and "Biên tập viên (Editor)" in text  # vai lạ không thành «editor»
    _assert_note_is_safe(text)
    assert "evil" not in text


def test_bam_tao_nhap_sau_khi_kiem_khong_doi_cau_bao_va_khong_tai_anh(project_root, site):
    site.me = {"name": TEN_HIEN, "roles": ["author"], "capabilities": WRITE}
    at = open_page(project_root)
    click(at, "Kiểm tra kết nối")
    before = gps_notes(at)
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    click(at, "Tạo bài nháp")
    assert gps_notes(at) == before and len(before) == 1
    assert [r.method for r in site.sent].count("POST") == 1 and site.offered == []


# ================================================================ lỗi tìm ra
@pytest.mark.xfail(
    strict=True,
    reason="SL-T106-1: câu cũ của mục 1 vẫn khuyên «Quản trị viên (Administrator)» cạnh câu mới",
)
@pytest.mark.parametrize(
    ("roles", "capabilities"),
    [(["contributor"], CONTRIBUTOR), (["editor"], _ABSENT)],
    ids=["contributor", "khong-ro-quyen"],
)
def test_sl_t106_1_trang_khong_khuyen_nang_len_quan_tri(project_root, site, roles, capabilities):
    """Cộng tác viên (viết bài được, không tải ảnh, không ``unfiltered_html``): trang hiện câu
    mới «Không cần, và không nên, nâng lên Quản trị viên» **và** câu cũ «Nên dùng tài khoản có vai
    trò Biên tập viên (Editor) hoặc Quản trị viên (Administrator)» (``wordpress.py:121-125``): hai
    lời khuyên ngược nhau trên cùng màn hình, câu cũ trái quyết định dùng tài khoản Biên tập viên
    riêng (README bước 10 còn dặn thấy ``administrator`` là dùng nhầm tài khoản quản trị). Tài
    khoản website không cho biết quyền cũng nhận câu cũ đó."""
    site.me = {"name": TEN_HIEN, "roles": roles}
    if capabilities is not _ABSENT:
        site.me["capabilities"] = capabilities
    at = open_page(project_root)
    click(at, "Kiểm tra kết nối")
    assert gps_notes(at)  # tiền đề: có câu báo về GPS
    assert [value for _kind, value in texts(at) if "Quản trị viên (Administrator)" in value] == []


@pytest.mark.xfail(
    strict=True,
    reason="SL-T108-1: README dòng Trạng thái còn nói trang Kết nối tạo bài nháp có ảnh đại diện",
)
def test_sl_t108_1_readme_trang_thai_khop_trang_ket_noi():
    """README dòng 7 (Trạng thái): «kết nối WordPress (kiểm tra kết nối, xem chuyên mục/thẻ, tạo
    bài nháp có ảnh đại diện)». Sau T-108 trang Kết nối chỉ tạo bài nháp chữ."""
    status = next(line for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
                  if line.startswith("> **Trạng thái:**"))
    start = status.find("kết nối WordPress (")
    part = status[start : status.index(")", start)] if start >= 0 else ""
    assert "ảnh" not in part

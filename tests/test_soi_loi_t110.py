"""Soi Lỗi T-110 (rút gọn): «Gửi nháp» gắn ảnh vừa tải vào bài nháp vừa tạo (LC-T093-2, 1A).

Kiểm độc lập. Website giả riêng ``_ParentSite`` (adapter ``requests``) nhớ bài, ảnh và **bài cha**
của từng ảnh như WordPress: nhận ``?post=`` lúc tải ảnh và ``post`` lúc sửa ảnh, có sẵn ảnh 9 đang
gắn vào bài đã đăng 7. Không dùng ``FakeWordPress``, site giả hay bảng kỳ vọng của Thợ Máy (trừ ca
giao diện cuối, mượn khung «Gửi nháp» của ``test_app_images`` như các file T-086, T-089).

1. Khóa ``post`` chỉ đi được đúng lệnh gắn ảnh: ảnh client vừa tải (201), nháp client vừa tạo,
   thân chỉ một khóa; gọi thẳng ``_request`` ở mọi đường, mọi dạng; mọi hàm công khai.
2. Lỗi khi gắn: không tải lại, không tạo bài trùng, không thử lại, câu báo cố định; khóa gửi trùng.
3. Nội dung, ``srcset``, ảnh đại diện; thứ tự lệnh.
4. ``GPS_PUBLIC_WARNING``; ảnh của lần gửi hỏng trước khi có nháp.

Không gọi website thật (bộ chặn mạng của ``tests/conftest.py`` bật suốt).
"""

from __future__ import annotations

import ast
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import test_app_images as ui
import test_t086_send_state as t86
from PIL import Image
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

import seo_app.wordpress.client as wp
from seo_app.images.html import figure_html
from seo_app.images.process import make_web_image
from seo_app.wordpress.client import DraftImage, DraftImagesError, WordPressClient, WordPressError

BASE = "https://example.com"
API = "/wp-json/wp/v2"
MOI = "MOI-T110 <b>x</b> https://evil.example"
MAT_KHAU_GIA = "abcd efgh ijkl mnop"  # Application Password giả
ROOT = Path(__file__).resolve().parents[1]

# Khung «Gửi nháp» của trang Soạn bài (như test_t086_send_state.py).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site


class _ParentSite(BaseAdapter):
    """WordPress giả có trạng thái: bài, ảnh, bài cha của ảnh. ``inject``: (phương thức, đường) →
    câu trả lời/ngoại lệ, hay hàm ``(request) -> câu trả lời | None`` (``None``: làm như thường)."""

    def __init__(self) -> None:
        super().__init__()
        self.media: dict[int, dict] = {9: {"post": 7, "alt_text": "ảnh cũ"}}  # ảnh có sẵn
        self.posts: dict[int, dict] = {7: {"status": "publish", "featured_media": 9}}
        self.requests: list[requests.PreparedRequest] = []
        self.inject: dict[tuple[str, str], object] = {}
        self.next_media, self.next_post = 101, 42

    def _url(self, media_id: int) -> str:
        return f"{BASE}/wp-content/uploads/anh-{media_id}.webp"

    def _answer(self, request: requests.PreparedRequest):
        parts = urlsplit(request.url)
        path, query = parts.path, parse_qs(parts.query)
        hook = self.inject.get((request.method, path))
        if hook is not None:
            answer = hook(request) if callable(hook) else hook
            if answer is not None:
                return answer
        sent = json.loads(request.body) if request.body and "json" in str(
            request.headers.get("Content-Type", "")) else {}
        if request.method == "POST" and path == f"{API}/media":
            media_id, self.next_media = self.next_media, self.next_media + 1
            self.media[media_id] = {"post": int(query["post"][0]) if "post" in query else None}
            return 201, {"id": media_id, "source_url": self._url(media_id), "alt_text": "",
                         "post": None}
        if request.method == "POST" and path.startswith(f"{API}/media/"):
            media_id = int(path.rsplit("/", 1)[1])
            item = self.media.get(media_id)
            if item is None:
                return 404, {"code": "rest_post_invalid_id", "message": MOI}
            item.update(sent)
            return 200, {"id": media_id, "source_url": self._url(media_id),
                         "alt_text": item.get("alt_text", ""), "post": item["post"]}
        if request.method == "POST" and path == f"{API}/posts":
            post_id, self.next_post = self.next_post, self.next_post + 1
            self.posts[post_id] = {"status": sent.get("status"), "featured_media": 0,
                                   "content": sent.get("content")}
            return 201, {"id": post_id, "status": sent.get("status"),
                         "title": {"raw": sent.get("title")}, "link": f"{BASE}/?p={post_id}"}
        if path.startswith(f"{API}/posts/"):
            post_id = int(path.rsplit("/", 1)[1])
            post = self.posts.get(post_id)
            if post is None:
                return 404, {"code": "rest_post_invalid_id", "message": MOI}
            if request.method == "GET":
                return 200, {"id": post_id, "status": post["status"], "meta": {}}
            post.update({k: v for k, v in sent.items() if k in ("featured_media", "status")})
            return 200, {"id": post_id, "status": post["status"],
                         "featured_media": post["featured_media"], "title": {"raw": "x"}}
        return 404, {"code": "rest_no_route", "message": MOI}

    def send(self, request, **kwargs):
        self.requests.append(request)
        answer = self._answer(request)
        if isinstance(answer, BaseException):
            raise answer
        status, body, *rest = answer
        response = requests.Response()
        response.status_code = status
        response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
        response.headers = CaseInsensitiveDict(
            {"Content-Type": "application/json; charset=UTF-8", **(rest[0] if rest else {})})
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass

    def calls(self) -> list[tuple[str, str]]:
        return [(r.method, urlsplit(r.url).path) for r in self.requests]

    def attaches(self) -> list[requests.PreparedRequest]:
        """Lệnh có thân JSON mang khóa ``post`` (thân byte ảnh thì bỏ qua)."""
        return [r for r in self.requests
                if r.method == "POST" and "json" in str(r.headers.get("Content-Type", ""))
                and "post" in json.loads(r.body)]


def _client(wp_site: _ParentSite) -> WordPressClient:
    session = requests.Session()
    session.mount("https://", wp_site)
    return WordPressClient(BASE, "lam", MAT_KHAU_GIA, session=session)


@pytest.fixture
def wp_site() -> _ParentSite:
    return _ParentSite()


@pytest.fixture
def client(wp_site) -> WordPressClient:
    return _client(wp_site)


@pytest.fixture(scope="module")
def webs():
    images = []
    for color in ((200, 60, 40), (40, 160, 90)):
        buffer = io.BytesIO()
        Image.new("RGB", (80, 60), color).save(buffer, "JPEG")
        images.append(make_web_image(buffer.getvalue()))
    return images


def _parts(webs, *, featured_second: bool = True):
    first = DraftImage(webs[0], alt="Cổng inox trước khi sửa", caption="Trước")
    second = DraftImage(webs[1], alt="Cổng inox sau khi sơn", caption="Sau",
                        featured=featured_second)
    return ["<p>Mở bài.</p>", first, "<p>Giữa bài.</p>", second], first, second


def _body(request) -> dict:
    return json.loads(request.body)


# ================================================================ 3. chạy đúng, thứ tự, nội dung
def test_gui_nhap_gan_dung_tung_anh_vao_bai_vua_tao(wp_site, client, webs):
    parts, first, second = _parts(webs)
    result = client.create_draft_with_images("Sửa cổng inox", parts)
    assert (result.post.id, result.post.status) == (42, "draft")
    assert (result.unattached, result.message, result.featured_media) == ((), "", 102)
    assert wp_site.media[101]["post"] == 42 and wp_site.media[102]["post"] == 42
    assert wp_site.media[9]["post"] == 7  # ảnh có sẵn không bị đụng
    assert wp_site.posts[42]["status"] == "draft" and wp_site.posts[42]["featured_media"] == 102
    assert wp_site.calls() == [
        ("POST", f"{API}/media"), ("POST", f"{API}/media/101"),
        ("POST", f"{API}/media"), ("POST", f"{API}/media/102"),
        ("POST", f"{API}/posts"),
        ("POST", f"{API}/media/101"), ("POST", f"{API}/media/102"),  # gắn ảnh
        ("GET", f"{API}/posts/42"), ("POST", f"{API}/posts/42"),  # kiểm nháp, ảnh đại diện
    ]
    attaches = wp_site.requests[5:7]
    assert [_body(r) for r in attaches] == [{"post": 42}, {"post": 42}]
    assert [parse_qs(urlsplit(r.url).query) for r in attaches] == [{"_fields": ["id,post"]}] * 2
    for request in wp_site.requests:  # lệnh tải ảnh không mang ``post``
        assert "post" not in parse_qs(urlsplit(request.url).query)
    expected = "\n".join([
        "<p>Mở bài.</p>",
        figure_html(src=f"{BASE}/wp-content/uploads/anh-101.webp", alt=first.alt,
                    caption=first.caption, width=webs[0].width, height=webs[0].height),
        "<p>Giữa bài.</p>",
        figure_html(src=f"{BASE}/wp-content/uploads/anh-102.webp", alt=second.alt,
                    caption=second.caption, width=webs[1].width, height=webs[1].height),
    ])
    assert wp_site.posts[42]["content"] == expected and "srcset" in expected


def test_khong_anh_thi_khong_gan(wp_site, client):
    result = client.create_draft_with_images("Bài chữ", ["<p>Chỉ có chữ.</p>"])
    assert result.unattached == () and wp_site.attaches() == []


# ================================================================ 1. khóa ``post`` chỉ một đường
FORGED = {
    "tao-bai": ("POST", "/wp/v2/posts", {"json": {"status": "draft", "title": "x", "post": 42}}),
    "sua-bai": ("POST", "/wp/v2/posts/42", {"json": {"post": 42}}),
    "sua-bai-kem-anh-dai-dien": ("POST", "/wp/v2/posts/42",
                                 {"json": {"featured_media": 101, "post": 42}}),
    "tai-anh-tham-so-post": ("POST", "/wp/v2/media",
                             {"data": b"\xff\xd8\xff", "params": {"post": 42},
                              "headers": {"Content-Type": "image/jpeg"}}),
    "tai-anh-json-post": ("POST", "/wp/v2/media", {"json": {"post": 42}}),
    "kem-alt": ("POST", "/wp/v2/media/101", {"json": {"post": 42, "alt_text": "x"}}),
    "bai-khong-cua-client": ("POST", "/wp/v2/media/101", {"json": {"post": 7}}),
    "anh-co-san": ("POST", "/wp/v2/media/9", {"json": {"post": 42}}),
    "go-bai-cha": ("POST", "/wp/v2/media/101", {"json": {"post": 0}}),
    "post-chu": ("POST", "/wp/v2/media/101", {"json": {"post": "42"}}),
    "post-bool": ("POST", "/wp/v2/media/101", {"json": {"post": True}}),
    "post-so-thuc": ("POST", "/wp/v2/media/101", {"json": {"post": 42.0}}),
    "post-null": ("POST", "/wp/v2/media/101", {"json": {"post": None}}),
    "post-mang": ("POST", "/wp/v2/media/101", {"json": {"post": [42]}}),
    "post-am": ("POST", "/wp/v2/media/101", {"json": {"post": -42}}),
    "post-qua-lon": ("POST", "/wp/v2/media/101", {"json": {"post": 2**63}}),
    "Post-hoa": ("POST", "/wp/v2/media/101", {"json": {"Post": 42}}),
    "post-cach": ("POST", "/wp/v2/media/101", {"json": {"post ": 42}}),
    "post_parent": ("POST", "/wp/v2/media/101", {"json": {"post_parent": 42}}),
    "parent": ("POST", "/wp/v2/media/101", {"json": {"parent": 42}}),
    "tham-so-post": ("POST", "/wp/v2/media/101",
                     {"json": {"post": 42}, "params": {"_fields": "id,post", "post": 42}}),
    "method-tham-so": ("POST", "/wp/v2/media/101",
                       {"json": {"post": 42}, "params": {"_method": "PUT"}}),
    "method-header": ("POST", "/wp/v2/media/101",
                      {"json": {"post": 42}, "headers": {"X-HTTP-Method-Override": "PUT"}}),
    "fields-description": ("POST", "/wp/v2/media/101",
                           {"json": {"post": 42}, "params": {"_fields": "id,post,description"}}),
    "ability": ("POST", wp.SITESEO_ABILITY_RUN_PATH,
                {"json": {"input": {"post_id": 42}, "post": 42}}),
    "get-bai": ("GET", "/wp/v2/posts/42", {"params": {"post": 42}}),
    "get-danh-sach": ("GET", "/wp/v2/posts", {"params": {"parent": 42}}),
}


@pytest.mark.parametrize("method, path, options", FORGED.values(), ids=FORGED)
def test_khoa_post_moi_cach_goi_thang_deu_bi_chan(wp_site, client, webs, method, path, options):
    client.create_draft_with_images("Sửa cổng", _parts(webs)[0])  # client giữ ảnh 101, 102, bài 42
    before = len(wp_site.requests)
    with pytest.raises(WordPressError):
        client._request(method, path, **options)
    assert len(wp_site.requests) == before
    assert wp_site.media[9]["post"] == 7 and wp_site.media[101]["post"] == 42


def test_khoa_post_dung_dang_cua_client_thi_gui_duoc_va_client_khac_bi_chan(wp_site, client, webs):
    client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    before = len(wp_site.requests)
    client._request("POST", "/wp/v2/media/101", json={"post": 42}, params={"_fields": "id,post"})
    assert len(wp_site.requests) == before + 1  # đối chứng: đúng dạng thì qua
    other = _client(wp_site)
    with pytest.raises(WordPressError):
        other._request("POST", "/wp/v2/media/101", json={"post": 42},
                       params={"_fields": "id,post"})
    with pytest.raises(WordPressError):
        other._attach_media(101, 42)
    assert len(wp_site.requests) == before + 1


def test_dau_hen_gio_kem_post_bi_chan(wp_site, client, webs):
    client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    before = len(wp_site.requests)
    with pytest.raises(WordPressError):
        client._request("POST", "/wp/v2/posts/42", json={"status": "publish", "post": 42},
                        params={"_fields": "id,status,date_gmt,link"}, release=wp._RELEASE)
    assert len(wp_site.requests) == before


def test_ham_cong_khai_chi_gui_post_o_lenh_gan_anh(wp_site, client, webs):
    """Mọi hàm ghi công khai (tạo nháp, tải ảnh, ảnh đại diện, gửi nháp kèm ảnh): khóa ``post``
    chỉ có ở hai lệnh gắn ảnh của ``create_draft_with_images``, không ở tham số đường nào."""
    client.create_draft("Bài chữ", "<p>Chữ</p>")  # bài 42
    media = client.upload_media(b"\xff\xd8\xff\xe0 anh", "cong.jpg", alt_text="Cổng")  # ảnh 101
    client.set_featured_image(42, media.id)
    client.create_draft_with_images("Sửa cổng", _parts(webs)[0])  # ảnh 102, 103, bài 43
    attaches = wp_site.attaches()
    assert [(urlsplit(r.url).path, _body(r)) for r in attaches] == [
        (f"{API}/media/102", {"post": 43}), (f"{API}/media/103", {"post": 43})]
    assert wp_site.media[101]["post"] is None  # ảnh tải riêng không tự gắn vào bài nào
    for request in wp_site.requests:
        assert "post" not in parse_qs(urlsplit(request.url).query)


def test_chi_attach_media_co_dict_khoa_post():
    tree = ast.parse((ROOT / "seo_app" / "wordpress" / "client.py").read_text(encoding="utf-8"))
    owners = set()
    for function in ast.walk(tree):
        if isinstance(function, ast.FunctionDef):
            for node in ast.walk(function):
                if isinstance(node, ast.Dict) and any(
                    isinstance(k, ast.Constant) and k.value == "post" for k in node.keys
                ):
                    owners.add(function.name)
    assert owners == {"_attach_media"}


# ================================================================ 2. lỗi khi gắn
ATTACH_FAILURES = {
    "mat-mang": requests.exceptions.ConnectionError(MOI),
    "het-gio": requests.exceptions.ReadTimeout(MOI),
    "301": (301, b"", {"Location": "https://evil.example/"}),
    "302": (302, b""),
    "400": (400, {"code": "rest_invalid_param", "message": MOI}),
    "401": (401, {"code": "x", "message": MOI}),
    "403": (403, {"code": "rest_cannot_edit", "message": MOI}),
    "404": (404, {"code": "rest_post_invalid_id", "message": MOI}),
    "429": (429, {"code": "x", "message": MOI}),
    "500": (500, {"code": "x", "message": MOI}),
    "502-html": (502, MOI.encode()),
    "503": (503, b""),
    "200-khong-json": (200, MOI.encode()),
    "200-danh-sach": (200, []),
    "200-thieu-post": (200, {"id": 101}),
    "200-post-null": (200, {"id": 101, "post": None}),
    "200-post-0": (200, {"id": 101, "post": 0}),
    "200-post-bai-khac": (200, {"id": 101, "post": 7}),
    "200-post-chu": (200, {"id": 101, "post": "42"}),
    "200-post-bool": (200, {"id": 101, "post": True}),
    "200-anh-khac": (200, {"id": 102, "post": 42}),
    "200-ma-chu": (200, {"id": "101", "post": 42}),
    "200-json-long-sau": (200, b"[" * 100_000 + b"]" * 100_000),
}


@pytest.mark.parametrize("answer", ATTACH_FAILURES.values(), ids=ATTACH_FAILURES)
def test_gan_anh_loi_khong_tai_lai_khong_tao_trung_khong_thu_lai(wp_site, client, webs, answer):
    def first_attach(request):
        return answer if _body(request) == {"post": 42} else None

    wp_site.inject[("POST", f"{API}/media/101")] = first_attach
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert (result.post.id, result.unattached) == (42, (101, 102))
    assert result.featured_media == 102 and wp_site.posts[42]["featured_media"] == 102
    assert wp_site.calls().count(("POST", f"{API}/media")) == 2  # không tải lại
    assert wp_site.calls().count(("POST", f"{API}/posts")) == 1  # không tạo bài trùng
    assert len(wp_site.attaches()) == 1  # không thử lại, không gắn tiếp ảnh sau
    assert wp_site.media[102]["post"] is None
    message = result.message
    assert "chưa gắn được 2 ảnh" in message and "Media → Thư viện" in message
    for piece in ("MOI-T110", "evil", BASE, "<b>"):
        assert piece not in message


def test_anh_sau_loi_thi_chi_bao_anh_do(wp_site, client, webs):
    wp_site.inject[("POST", f"{API}/media/102")] = (
        lambda request: (500, {"message": MOI}) if _body(request) == {"post": 42} else None)
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert result.unattached == (102,) and wp_site.media[101]["post"] == 42
    assert "chưa gắn được 1 ảnh" in result.message


def test_gan_va_anh_dai_dien_cung_loi_bao_ca_hai(wp_site, client, webs):
    wp_site.inject[("POST", f"{API}/media/101")] = (
        lambda request: (503, b"") if _body(request) == {"post": 42} else None)
    wp_site.inject[("POST", f"{API}/posts/42")] = (500, {"message": MOI})
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert result.featured_media is None and result.unattached == (101, 102)
    assert "chưa đặt được ảnh đại diện" in result.message and "chưa gắn được" in result.message
    assert MOI not in result.message


def test_gan_anh_loi_o_trang_soan_bai_van_khoa_gui_trung(project_root, root, fake_ai, site):
    """Khóa gửi trùng T-086, T-089: gắn ảnh lỗi thì trang báo đã tạo nháp kèm câu cảnh báo, nháp
    ghi «đã gửi (mã bài)», mở lại vẫn khóa nút «Gửi nháp»; 1 ảnh tải, 1 bài tạo."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    original = site.update_media

    def update(request):
        if ui.body_of(request) == {"post": ui.POST_ID}:
            return (500, {"code": "x", "message": MOI}, {})
        return original(request)

    site.fake.on("POST", f"{ui.MEDIA}/900", update)
    ui.send(at)
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    (warning,) = [w.value.replace("\\", "") for w in at.warning if "chưa gắn được" in w.value]
    assert "Media → Thư viện" in warning and "MOI-T110" not in warning
    state = t86.saved_state(at)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)
    assert len(site.uploads()) == 1 and len(site.posts()) == 1
    fresh = t86.reopen(project_root, t86.draft_id(at))
    assert ui.button(fresh, t86.SEND).disabled


# ================================================================ 4. câu nhắc GPS, lần gửi hỏng
def test_cau_nhac_gps_dung_su_that_moi():
    from app.views import write  # noqa: PLC0415

    text = write.GPS_PUBLIC_WARNING
    for piece in ("xem được công khai", "đường dẫn trực tiếp", "ngay khi tải lên",
                  "danh sách Media công khai", "cho tới khi bài được đăng",
                  "gắn không được thì phần mềm báo", "không tự xóa"):
        assert piece in text, piece


@pytest.mark.parametrize(
    "create, maybe_draft",
    [((400, {"code": "rest_invalid_param", "message": MOI}), False),
     ((500, {"code": "x", "message": MOI}), True)],
    ids=["tu-choi-400", "loi-500"],
)
def test_gui_hong_truoc_khi_co_nhap_anh_khong_duoc_gan(wp_site, client, webs, create, maybe_draft):
    """Gửi hỏng ở lệnh tạo nháp: ảnh đã lên không có bài cha (không lệnh gắn nào), câu báo liệt
    kê ảnh. Thợ Máy nêu ngoài phạm vi; câu báo xem SL-T110-1."""
    wp_site.inject[("POST", f"{API}/posts")] = create
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert [image.id for image in error.value.uploaded] == [101, 102]
    assert error.value.maybe_draft is maybe_draft
    assert wp_site.attaches() == []
    assert wp_site.media[101]["post"] is None and wp_site.media[102]["post"] is None


@pytest.mark.parametrize(
    "create",
    [(400, {"code": "rest_invalid_param", "message": MOI}), (500, {"code": "x", "message": MOI}),
     requests.exceptions.ReadTimeout(MOI)],
    ids=["tu-choi-400", "loi-500", "het-gio"],
)
def test_sl_t110_1_gui_hong_truoc_khi_co_nhap_bao_anh_con_trong_danh_sach_media(
    wp_site, client, webs, create
):
    wp_site.inject[("POST", f"{API}/posts")] = create
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert "danh sách Media" in str(error.value)

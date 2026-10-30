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

Lượt 2 (LC-T110-1 cách A, SL-T110-1), cuối file:

5. ``post`` ở câu trả lời lệnh tải ảnh, viết tay đúng byte JSON: null/0 gắn; số dương từ chối như
   mã khác 201 (không ghi alt, không gắn, không tạo nháp); thiếu hay lạ không gắn. Cả
   ``upload_media``; mọi lệnh tải ảnh đều qua bước xét này.
6. Câu báo ở mọi lối hỏng (trước, sau lệnh tạo nháp, giữa hai ảnh): đúng ảnh nào đã lên, ảnh đó chưa
   gắn bài nào, có nói danh sách Media công khai (lời hứa của câu nhắc GPS), không chép lời máy chủ.

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


# ====================================================================== lượt 2: 5. ``post``
# LC-T110-1, cách A (Chỉ Huy 30/10 20:40). Giá trị ``post`` viết tay đúng byte JSON website gửi
# (``-0``, ``NaN``, ``1E400``… không dựng được bằng ``json.dumps``).
POST_EMPTY = {"null": "null", "0": "0", "am-0": "-0"}
POST_PARENT = {"7": "7", "1": "1", "42": "42", "max": str(wp.MAX_ID)}
POST_ODD = {
    "thieu": None,  # không có khóa ``post``
    "chu-7": '"7"', "chu-rong": '""', "chu-0": '"0"', "chu-null": '"null"',
    "true": "true", "false": "false", "am-1": "-1", "am-2-63": str(-(2**63)),
    "thuc-0": "0.0", "thuc-am-0": "-0.0", "thuc-7": "7.0", "mu-1e2": "1e2", "thuc-1-5": "1.5",
    "qua-max": str(wp.MAX_ID + 1), "2-64": str(2**64), "400-chu-so": "9" * 400,
    "1e400": "1E400", "nan": "NaN", "inf": "Infinity", "am-inf": "-Infinity",
    "mang": "[7]", "mang-rong": "[]", "dict": '{"id": 7}', "dict-rong": "{}",
}
OLD_9 = {"post": 7, "alt_text": "ảnh cũ"}  # ảnh có sẵn của bài đã đăng 7: không được đổi
EXISTING_9 = (
    201,
    {"id": 9, "source_url": f"{BASE}/wp-content/uploads/anh-9.webp", "alt_text": "ảnh cũ",
     "post": 7},
)


def _upload_post(wp_site: _ParentSite, *tokens: str | None, existing: int | None = None) -> None:
    """Lệnh tải ảnh thứ n trả 201 kèm ``"post": tokens[n]`` (token cuối dùng cho các lần sau;
    ``None``: không có khóa). ``existing``: website trả lại ảnh có sẵn mã đó, không tạo ảnh mới."""
    queue = list(tokens)

    def answer(request):
        token = queue.pop(0) if len(queue) > 1 else queue[0]
        media_id = existing
        if media_id is None:
            media_id, wp_site.next_media = wp_site.next_media, wp_site.next_media + 1
            wp_site.media[media_id] = {"post": None}
        text = json.dumps({"id": media_id, "source_url": wp_site._url(media_id), "alt_text": ""})
        if token is not None:
            text = text[:-1] + f', "post": {token}}}'
        return 201, text.encode()

    wp_site.inject[("POST", f"{API}/media")] = answer


def test_l2_lenh_tai_anh_xin_post_lenh_khac_giu_fields(wp_site, client, webs):
    client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    upload, alt, attach = "id,source_url,alt_text,post", "id,source_url,alt_text", "id,post"
    post = "id,status,title,link,featured_media"
    assert [
        (r.method, urlsplit(r.url).path, parse_qs(urlsplit(r.url).query))
        for r in wp_site.requests
    ] == [
        ("POST", f"{API}/media", {"_fields": [upload]}),
        ("POST", f"{API}/media/101", {"_fields": [alt]}),
        ("POST", f"{API}/media", {"_fields": [upload]}),
        ("POST", f"{API}/media/102", {"_fields": [alt]}),
        ("POST", f"{API}/posts", {"_fields": [post]}),
        ("POST", f"{API}/media/101", {"_fields": [attach]}),
        ("POST", f"{API}/media/102", {"_fields": [attach]}),
        ("GET", f"{API}/posts/42", {"context": ["edit"], "_fields": ["id,status,meta"]}),
        ("POST", f"{API}/posts/42", {"_fields": [post]}),
    ]


@pytest.mark.parametrize("token", POST_EMPTY.values(), ids=POST_EMPTY)
def test_l2_post_trong_thi_gan_ca_hai_anh(wp_site, client, webs, token):
    _upload_post(wp_site, token)
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert (result.unattached, result.message, result.featured_media) == ((), "", 102)
    assert [_body(r) for r in wp_site.attaches()] == [{"post": 42}, {"post": 42}]
    assert (wp_site.media[101]["post"], wp_site.media[102]["post"]) == (42, 42)
    assert wp_site.media[9] == OLD_9


@pytest.mark.parametrize("token", POST_PARENT.values(), ids=POST_PARENT)
def test_l2_post_so_duong_dung_ngay_khong_ghi_alt_khong_gan_khong_tao(wp_site, client, webs, token):
    _upload_post(wp_site, token)
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert wp_site.calls() == [("POST", f"{API}/media")]  # không ghi alt, không tạo, không gắn
    assert error.value.uploaded == () and error.value.maybe_draft is False
    assert str(error.value).startswith(wp._MEDIA_NOT_CREATED)
    assert client._uploaded_media_ids == set() and client._created_post_ids == set()
    assert wp_site.media[101] == {"post": None} and wp_site.media[9] == OLD_9


@pytest.mark.parametrize("at_upload", [1, 2], ids=["anh-dau", "anh-sau"])
def test_l2_website_tra_lai_anh_co_san_9_khong_bi_ghi_alt_doi_bai_cha(
    wp_site, client, webs, at_upload
):
    seen = []

    def answer(request):
        seen.append(request)
        return EXISTING_9 if len(seen) == at_upload else None  # None: tạo ảnh mới như thường

    wp_site.inject[("POST", f"{API}/media")] = answer
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert wp_site.media[9] == OLD_9 and ("POST", f"{API}/media/9") not in wp_site.calls()
    assert ("POST", f"{API}/posts") not in wp_site.calls() and wp_site.attaches() == []
    assert [image.id for image in error.value.uploaded] == [101][: at_upload - 1]
    assert 9 not in client._uploaded_media_ids


@pytest.mark.parametrize("token", POST_ODD.values(), ids=POST_ODD)
def test_l2_post_thieu_hay_la_thi_khong_gan_bai_van_tao(wp_site, client, webs, token):
    _upload_post(wp_site, token)
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert (result.post.id, result.unattached, result.featured_media) == (42, (101, 102), 102)
    assert wp_site.attaches() == []  # lệnh gắn bị chặn trước khi gửi
    assert result.message == wp._IMAGES_NOT_ATTACHED.format(count=2)
    assert (wp_site.media[101]["post"], wp_site.media[102]["post"]) == (None, None)
    assert wp_site.media[9] == OLD_9 and client._uploaded_media_ids == set()


@pytest.mark.parametrize(
    "token", [None, '"7"', "[7]", str(wp.MAX_ID + 1), "NaN"],
    ids=["thieu", "chu-7", "mang", "qua-max", "nan"],
)
def test_l2_post_la_ma_la_anh_co_san_thi_khong_doi_bai_cha(wp_site, client, webs, token):
    """Thiếu/lạ mà website trả lại ảnh có sẵn 9: không gắn, bài cha vẫn 7. Alt vẫn ghi như
    trước T-110 (cách A chỉ bỏ bước gắn ở nhánh này; báo cáo lượt 2, G5)."""
    _upload_post(wp_site, token, existing=9)
    result = client.create_draft_with_images(
        "Sửa cổng", ["<p>Mở bài.</p>", DraftImage(webs[0], alt="Cổng inox mới sơn")]
    )
    assert result.unattached == (9,) and wp_site.attaches() == []
    assert wp_site.media[9]["post"] == 7


def test_l2_xet_tung_anh_anh_dau_trong_anh_sau_la(wp_site, client, webs):
    _upload_post(wp_site, "null", '"x"')
    result = client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert result.unattached == (102,)
    assert [_body(r) for r in wp_site.attaches()] == [{"post": 42}]
    assert (wp_site.media[101]["post"], wp_site.media[102]["post"]) == (42, None)
    assert result.message == wp._IMAGES_NOT_ATTACHED.format(count=1)


UPLOAD_ALONE = {
    "null": ("null", "cua-client"), "0": ("0", "cua-client"),
    "7": ("7", "tu-choi"), "max": (str(wp.MAX_ID), "tu-choi"),
    "thieu": (None, "khong-ro"), "chu-7": ('"7"', "khong-ro"), "nan": ("NaN", "khong-ro"),
    "qua-max": (str(wp.MAX_ID + 1), "khong-ro"),
}


@pytest.mark.parametrize("token, kind", UPLOAD_ALONE.values(), ids=UPLOAD_ALONE)
def test_l2_upload_media_rieng_cung_xet_post(wp_site, client, webs, token, kind):
    _upload_post(wp_site, token)
    if kind == "tu-choi":
        with pytest.raises(WordPressError) as error:
            client.upload_media(webs[0].data, "cong-inox.webp", alt_text="Cổng inox")
        assert wp_site.calls() == [("POST", f"{API}/media")]  # không ghi gì vào ảnh đó
        message = str(error.value)
        assert message.startswith(wp._MEDIA_NOT_CREATED) and "Media → Thư viện" in message
        assert "xóa" not in message  # ảnh website vừa trả có thể là ảnh có sẵn
        return
    media = client.upload_media(webs[0].data, "cong-inox.webp", alt_text="Cổng inox")
    assert media.id == 101 and wp_site.media[101]["alt_text"] == "Cổng inox"
    assert wp_site.attaches() == [] and wp_site.media[101]["post"] is None  # không gắn bài nào
    assert client._uploaded_media_ids == ({101} if kind == "cua-client" else set())


def test_l2_upload_media_website_tra_lai_anh_co_san_9_khong_bi_ghi(wp_site, client, webs):
    wp_site.inject[("POST", f"{API}/media")] = EXISTING_9
    with pytest.raises(WordPressError):
        client.upload_media(webs[0].data, "cong-inox.webp", alt_text="Cổng inox mới")
    assert wp_site.calls() == [("POST", f"{API}/media")] and wp_site.media[9] == OLD_9


def test_l2_moi_lenh_tai_anh_deu_xet_post():
    """Chỉ ``_post_media`` gửi ``POST /wp/v2/media``; mọi lần gọi đều ``new_only=True`` (xét
    ``post``); trang (``app/``) chỉ tải ảnh qua «Gửi nháp» (trang Kết nối không còn ô tải ảnh)."""
    tree = ast.parse((ROOT / "seo_app" / "wordpress" / "client.py").read_text(encoding="utf-8"))
    senders, callers = [], []
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef):
            continue
        for node in ast.walk(function):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            values = [arg.value for arg in node.args if isinstance(arg, ast.Constant)]
            if node.func.attr == "_request" and values[:2] == ["POST", "/wp/v2/media"]:
                senders.append(function.name)
            if node.func.attr == "_post_media":
                keywords = [(k.arg, getattr(k.value, "value", None)) for k in node.keywords]
                callers.append((function.name, keywords))
    assert senders == ["_post_media"]
    assert sorted(callers) == [
        ("create_draft_with_images", [("new_only", True)]),
        ("upload_media", [("new_only", True)]),
    ]
    pages = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "app").rglob("*.py")
        if any(
            name in path.read_text(encoding="utf-8")
            for name in ("upload_media", "_post_media", "create_draft_with_images", "/media")
        )
    )
    assert pages == ["app/views/write.py"]


# ====================================================================== lượt 2: 6. câu báo
def _nth(n: int, answer):
    """Lần gọi thứ ``n`` (đếm từ 1) trả ``answer``; các lần khác website làm như thường."""
    seen = []

    def hook(request):
        seen.append(request)
        return answer if len(seen) == n else None

    return hook


def _alt_write(answer):
    """Lệnh ghi alt vào ảnh (không phải lệnh gắn) trả ``answer``."""
    return lambda request: None if "post" in _body(request) else answer


_M, _P = f"{API}/media", f"{API}/posts"
_REFUSED = (400, {"code": "rest_upload_unknown_error", "message": MOI})
_BROKEN = (500, {"code": "x", "message": MOI})
_TIMEOUT = requests.exceptions.ReadTimeout(MOI)
_SAME_ID = (201, {"id": 101, "source_url": f"{BASE}/wp-content/uploads/anh-101.webp", "post": None})
FAIL_PATHS = {  # tên: (đường hỏng, dựng câu trả lời, ảnh đã lên, ảnh đang tải có thể đã lên,
    #                    bài nháp có thể đã có)
    "tai-1-400": (_M, lambda: _nth(1, _REFUSED), [], False, False),
    "tai-1-500": (_M, lambda: _nth(1, _BROKEN), [], True, False),
    "tai-1-het-gio": (_M, lambda: _nth(1, _TIMEOUT), [], True, False),
    "tai-1-mat-mang": (_M, lambda: _nth(1, requests.exceptions.ConnectionError(MOI)), [], True,
                       False),
    "tai-1-201-hong": (_M, lambda: _nth(1, (201, MOI.encode())), [], True, False),
    "tai-1-loi-la": (_M, lambda: _nth(1, ValueError(MOI)), [], True, False),
    "tai-1-200": (_M, lambda: _nth(1, (200, EXISTING_9[1])), [], True, False),
    "tai-1-co-cha": (_M, lambda: _nth(1, EXISTING_9), [], True, False),
    "alt-1-500": (f"{_M}/101", lambda: _alt_write(_BROKEN), [101], False, False),
    "alt-1-het-gio": (f"{_M}/101", lambda: _alt_write(_TIMEOUT), [101], False, False),
    "alt-2-loi-la": (f"{_M}/102", lambda: _alt_write(ValueError(MOI)), [101, 102], False, False),
    "tai-2-400": (_M, lambda: _nth(2, _REFUSED), [101], False, False),
    "tai-2-503": (_M, lambda: _nth(2, (503, b"")), [101], True, False),
    "tai-2-cung-ma": (_M, lambda: _nth(2, _SAME_ID), [101], True, False),
    "tai-2-co-cha": (_M, lambda: _nth(2, EXISTING_9), [101], True, False),
    "tao-400": (_P, lambda: _REFUSED, [101, 102], False, False),
    "tao-500": (_P, lambda: _BROKEN, [101, 102], False, True),
    "tao-het-gio": (_P, lambda: _TIMEOUT, [101, 102], False, True),
    "tao-loi-la": (_P, lambda: ValueError(MOI), [101, 102], False, True),
}


@pytest.mark.parametrize(
    "path, make, uploaded, maybe_image, maybe_draft", FAIL_PATHS.values(), ids=FAIL_PATHS
)
def test_l2_cau_bao_moi_loi_hong_dung_su_that(
    wp_site, client, webs, path, make, uploaded, maybe_image, maybe_draft
):
    wp_site.inject[("POST", path)] = make()
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    exc, message = error.value, str(error.value)
    assert [image.id for image in exc.uploaded] == uploaded
    assert (exc.maybe_uploaded, exc.maybe_draft) == (maybe_image, maybe_draft)
    # «Ảnh đó chưa gắn vào bài nào» đúng: không lệnh gắn nào, ảnh đã lên không có bài cha;
    # phần mềm không xóa, không sửa ảnh có sẵn.
    assert wp_site.attaches() == [] and wp_site.media[9] == OLD_9
    assert all(wp_site.media[media_id]["post"] is None for media_id in uploaded)
    assert {r.method for r in wp_site.requests} <= {"GET", "POST"}
    if uploaded:
        assert f"Đã có {len(uploaded)} ảnh lên thư viện Media" in message
    if uploaded or maybe_image:  # lời hứa của câu nhắc GPS: gửi hỏng trước khi có nháp cũng báo
        assert "danh sách Media" in message and "công khai" in message
    else:
        assert "Chưa có ảnh nào lên thư viện Media" in message and "công khai" not in message
    assert ("Bài nháp có thể vẫn đã được tạo" in message) is maybe_draft
    for piece in ("MOI-T110", "evil", "<b>", "example.com", "wp-content", "anh-10"):
        assert piece not in message


@pytest.mark.xfail(
    strict=True,
    reason="SL-T110-2: website trả lại ảnh có sẵn (201 kèm bài cha, hay mã khác 201) mà câu báo "
    "vẫn nói ảnh «chưa gắn vào bài nào… hãy xóa nếu không dùng» (_DRAFT_IMAGE_MAYBE lượt 2); "
    "tìm trong Media → Thư viện dễ gặp đúng ảnh có sẵn đó (cùng hình) và xóa nhầm (W2)",
)
@pytest.mark.parametrize("answer", [EXISTING_9, (200, EXISTING_9[1])], ids=["201-co-cha", "200"])
def test_sl_t110_2_website_tra_lai_anh_co_san_cau_bao_khong_xui_xoa(wp_site, client, webs, answer):
    wp_site.inject[("POST", f"{API}/media")] = answer
    with pytest.raises(DraftImagesError) as error:
        client.create_draft_with_images("Sửa cổng", _parts(webs)[0])
    assert wp_site.media[9] == OLD_9  # phần mềm không đụng ảnh 9: phần này đã đúng
    message = str(error.value)
    assert "ảnh đó chưa gắn vào bài nào" not in message  # website vừa nói ảnh thuộc bài 7
    assert "hãy xóa nếu không dùng" not in message or "bài khác" in message


def test_l2_cau_bao_cua_trang_noi_anh_chua_gan_hien_cong_khai():
    from app.views import write  # noqa: PLC0415

    for text in (write.MSG_SEND_UNEXPECTED, write.MSG_SEND_INTERRUPTED):
        assert "ảnh chưa gắn vào bài nào thì đang hiện công khai trong danh sách Media" in text
        assert "Bài viết → Nháp" in text and "Media → Thư viện" in text
    assert "lần gửi hỏng trước khi tạo được nháp cũng báo" in write.GPS_PUBLIC_WARNING


def test_l2_trang_soan_bai_tao_nhap_hong_bao_anh_trong_danh_sach_media(
    project_root, root, fake_ai, site
):
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    gps = [w.value for w in at.warning if "xem được công khai" in w.value]
    assert gps and all("lần gửi hỏng trước khi tạo được nháp cũng báo" in text for text in gps)
    site.fake.on(
        "POST", ui.POSTS, lambda _r: (400, {"code": "rest_invalid_param", "message": MOI}, {})
    )
    ui.send(at)
    (error,) = [e.value.replace("\\", "") for e in at.error if "thư viện Media" in e.value]
    assert "Đã có 1 ảnh lên thư viện Media" in error
    assert "danh sách Media" in error and "công khai" in error
    assert "MOI-T110" not in error and "evil" not in error
    assert len(site.uploads()) == 1 and len(site.posts()) == 1
    assert not [body for body in site.media_writes() if "post" in body]  # không lệnh gắn


def test_l2_trang_soan_bai_loi_la_hien_cau_moi(project_root, root, fake_ai, site, monkeypatch):
    from app.views import write  # noqa: PLC0415

    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)

    def broken(self, title, parts, **kwargs):
        raise RuntimeError(MOI)

    monkeypatch.setattr(WordPressClient, "create_draft_with_images", broken)
    ui.send(at)
    shown = [e.value.replace("\\", "") for e in at.error]
    assert write.MSG_SEND_UNEXPECTED in shown
    assert not [text for text in shown if "MOI-T110" in text]


@pytest.mark.xfail(
    strict=True,
    reason="SL-T110-3: lần gửi bị ngắt lúc đang tải ảnh (ảnh đã lên, chưa có nháp), mở lại nháp ở "
    "phiên mới chỉ hiện câu khóa «gửi dở» (unsure_message), không nói ảnh chưa gắn đang hiện công "
    "khai trong danh sách Media; câu nhắc GPS ngay đó hứa lần gửi hỏng trước khi có nháp cũng báo",
)
def test_sl_t110_3_mo_lai_nhap_gui_do_bao_anh_trong_danh_sach_media(
    project_root, root, fake_ai, site
):
    t86.stop_while_uploading(site)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert len(site.uploads()) == 1 and site.posts() == []  # ảnh đã lên, chưa có bài nháp
    fresh = t86.reopen(project_root, t86.draft_id(at))  # tải lại trang, đóng tab, mở lại app
    gps = [w.value for w in fresh.warning if "xem được công khai" in w.value]
    assert gps and "lần gửi hỏng trước khi tạo được nháp cũng báo" in gps[0]
    (error,) = [e.value.replace("\\", "") for e in fresh.error if t86.UNSURE in e.value]
    assert "danh sách Media" in error and "công khai" in error

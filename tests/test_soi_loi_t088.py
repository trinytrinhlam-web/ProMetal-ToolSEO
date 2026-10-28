"""Soi Lỗi · T-088: kiểm lại 4 lỗi Thấp client WordPress sau T-085 (SL-T085-1, -2, -3, LC-T085-1).

Kiểm độc lập, bằng chính cách tái hiện cũ của Soi Lỗi T-085 cộng biến thể:

- SL-T085-1: NUL và mọi khoảng trắng ``trim()`` của PHP ở mọi vị trí, nhiều lớp quanh tên trường
  ``_fields``; thử ngẫu nhiên có NUL. Mô hình WordPress: ``wp_parse_list``, ``trim()`` từng tên,
  giữ tên đúng bằng trường hay có phần đầu là trường (``get_fields_for_response``), dựng
  ``X.rendered`` khi ``rest_is_field_included``.
- SL-T085-2, LC-T085-1: câu trả lời JSON lồng sâu (mảng, đối tượng), hỏng (cụt, rỗng, HTML, UTF-8
  hỏng, BOM, số 5.000 chữ số), mã hóa lạ (charset bịa, khai sai UTF-32), lỗi giải nén, ở **mọi**
  lệnh đọc câu trả lời của mọi hàm công khai, cả mã thành công lẫn mã lỗi: chỉ được ra kết quả
  bình thường hoặc ``WordPressError``.
- SL-T085-3: lệnh tải ảnh của ``upload_media`` lỗi không phải lời từ chối 4xx → dặn kiểm thư viện
  Media; lời từ chối 4xx giữ câu cũ.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật. Test
``xfail(strict=True)`` là lỗi tìm được (SL-T088-n trong ``docs/team/reports/T-088-soi-loi.md``):
sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.
"""

import dataclasses
import io
import json
import random
import re
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session, siteseo_seo_answer
from PIL import Image
from requests.structures import CaseInsensitiveDict
from streamlit.testing.v1 import AppTest

from seo_app.auth import hash_password
from seo_app.images.process import make_web_image
from seo_app.storage.site_index import SiteIndexError, SiteIndexStore
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import SITESEO_ABILITY_PATH, DraftImage

PASSWORD = "Tg5h Jk8l Mn2b Vc4x"
PAGE_PASSWORD = "mat-khau-trang-t088"
BLOCKED = "không có trong danh sách được phép"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
ABILITY = f"/wp-json{SITESEO_ABILITY_PATH}"
PHOTO = b"\xff\xd8\xff\xe0soi-loi-t088"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
JSON_TYPE = "application/json; charset=UTF-8"


def body(request):
    return json.loads(request.body) if request.body else None


def query(request):
    return parse_qs(urlsplit(request.url).query, keep_blank_values=True)


def path(request):
    return urlsplit(request.url).path


# ================================================================ SL-T085-1: NUL trong _fields

PHP_SPLIT = re.compile(r"[ \t\n\x0b\f\r,]+")  # ``\s`` của PCRE không cờ u, và dấu phẩy
PHP_TRIM = " \t\n\r\0\x0b"  # ``trim()`` mặc định của PHP (có NUL)
SCHEMA = {"id", "date", "slug", "status", "link", "title", "content", "excerpt", "author",
          "featured_media", "meta", "description", "caption", "alt_text", "source_url",
          "media_details", "guid", "type", "modified_gmt", "_links"}
RENDERED = ("content", "excerpt", "description", "caption")


def wp_renders(value):
    """WordPress có dựng trường chạy shortcode (hay trả mọi trường, hay nhúng ``_links``/
    ``_embedded``) với ``_fields=value`` không."""
    tokens = [token for token in PHP_SPLIT.split(value) if token]
    if not tokens:
        return True
    tokens = [token.strip(PHP_TRIM) for token in tokens]
    kept = [t for t in tokens + ["id"] if t in SCHEMA or t.split(".")[0] in SCHEMA]

    def included(field):
        return field in kept or any(
            a.startswith(field + ".") or field.startswith(a + ".") for a in kept
        )

    if any(included(f"{name}.rendered") for name in RENDERED):
        return True
    return any(t in ("_links", "_embedded") or t.startswith("_links.") for t in tokens)


def test_ban_python_cua_wordpress_dung_cho_ca_da_biet():
    assert wp_renders("id,\x00content") and wp_renders("\x0b content \x00")
    assert wp_renders("content.rendered") and wp_renders("")
    assert not wp_renders("con\x00tent")  # NUL ở giữa: trim() không cắt
    assert not wp_renders("content\x00.rendered")  # phần đầu «content\x00» không phải trường
    assert not wp_renders("Content") and not wp_renders("\x00")


WHITES = ["\x00", " ", "\t", "\n", "\r", "\x0b"]
FIELD_ROUTES = [
    ("GET", "/wp/v2/posts/42", {"context": "edit"}),
    ("GET", "/wp/v2/posts", {"status": "publish"}),
    ("POST", "/wp/v2/media/9", {}),
]


def nul_variants(name):
    out = set()
    for a in WHITES:
        for b in WHITES:
            out |= {a + name, name + a, a + name + b, a + a + name + b + b, f"id,{a}{name}",
                    f"{a}{name}{b},id", f"{a}{name}.rendered", f"{name}.rendered{a}",
                    f"{a}{b}{a}{name}{b}{a}{b}", f"id {a}{name}{b} title"}
    return sorted(out)


@pytest.mark.parametrize(("method", "route", "extra"), FIELD_ROUTES)
@pytest.mark.parametrize("name", ["content", "excerpt", "description", "caption", "_links"])
def test_nul_va_khoang_trang_trim_quanh_ten_truong_khong_lot(fake_wp, wp_client, method, route,
                                                            extra, name):
    """Mọi vị trí, nhiều lớp: giá trị nào đi ra thì WordPress không dựng trường chạy shortcode.
    (Trước T-088: «\\x00content» đi ra.)"""
    fake_wp.on(method, "/wp-json" + route, {"id": 9})
    variants = nul_variants(name)
    for value in variants:
        fake_wp.requests.clear()
        try:
            wp_client._request(method, route, params={**extra, "_fields": value})
        except WordPressError as exc:
            assert BLOCKED in str(exc) and fake_wp.requests == []
            continue
        sent = query(fake_wp.requests[0])["_fields"][0]
        assert not wp_renders(sent), repr(value)
    assert len(variants) > 150


def test_nul_ngau_nhien_khong_lot():
    rng = random.Random(8888)
    pieces = ["\x00", " ", "\t", "\x0b", "\x0c", ",", ".", "content", "excerpt", "description",
              "caption", "_links", "_embedded", "id", "title", "rendered", "x", " ", "\x1c"]
    fake = FakeWordPress()
    fake.on("GET", "/wp-json/wp/v2/posts/42", {"id": 42})
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    sent_count = 0
    for _ in range(6000):
        value = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 8)))
        fake.requests.clear()
        try:
            client._request("GET", "/wp/v2/posts/42", params={"context": "edit", "_fields": value})
        except WordPressError:
            continue
        sent_count += 1
        assert not wp_renders(query(fake.requests[0])["_fields"][0]), repr(value)
    assert sent_count > 2000


# ================================================================ SL-T085-2, LC-T085-1: JSON lạ


class RawAnswer:
    """Câu trả lời thô (byte, loại, bảng mã tùy ý), không qua ``json.dumps`` của
    ``FakeWordPress``; dùng với ``_send_raw``."""

    def __init__(self, status, content, content_type, encoding):
        self.status, self.content = status, content
        self.content_type, self.encoding = content_type, encoding

    def __call__(self, request):
        response = requests.Response()
        response.status_code = self.status
        response._content = self.content
        response.headers = CaseInsensitiveDict({"Content-Type": self.content_type})
        response.encoding = self.encoding
        response.url = request.url
        response.request = request
        return response


def raw(status, content, content_type=JSON_TYPE, encoding="utf-8"):
    return RawAnswer(status, content, content_type, encoding)


BAD_BODIES = {
    "sau-mang": lambda s: raw(s, b"[" * 100_000 + b"]" * 100_000),
    "sau-doi-tuong": lambda s: raw(s, b'{"a":' * 50_000 + b"1" + b"}" * 50_000),
    "sau-khong-charset": lambda s: raw(s, b"[" * 100_000 + b"]" * 100_000, "application/json",
                                       None),
    "utf8-hong": lambda s: raw(s, b'{"id": 1, "name": "\xff\xfe"}'),
    "utf8-hong-doan": lambda s: raw(s, b'{"id": 1, "name": "\xff\xfe"}', "application/json", None),
    "charset-bia": lambda s: raw(s, b'{"id": 1', "application/json; charset=x-bia", "x-bia"),
    "utf32-khai-sai": lambda s: raw(s, b'{"id": 1}', JSON_TYPE, "utf-32"),
    "bom": lambda s: raw(s, b'\xef\xbb\xbf{"id": 1}'),
    "so-5000-chu-so": lambda s: raw(s, b'{"id": ' + b"9" * 5000 + b"}"),
    "cut": lambda s: raw(s, b'{"id": '),
    "rong": lambda s: raw(s, b""),
    "html": lambda s: raw(s, b"<html><body>evil bao tri</body></html>", "text/html"),
}


def _send_raw(fake):
    """``FakeWordPress`` trả nguyên ``RawAnswer`` (mỗi lệnh gọi handler đúng một lần)."""
    original = fake.send

    def send(request, **kwargs):
        handler = fake.routes.get((request.method, path(request)))
        if isinstance(handler, RawAnswer):
            fake.requests.append(request)
            return handler(request)
        return original(request, **kwargs)

    fake.send = send


def _jpeg():
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), (120, 80, 40)).save(buffer, "JPEG")
    return buffer.getvalue()


def _normal_site(fake):
    counter = iter(range(101, 200))

    def created(_r):
        media_id = next(counter)
        return (201, {"id": media_id, "source_url": f"{UPLOADS}a{media_id}.webp"}, {})

    def updated(r):
        media_id = int(path(r).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": f"{UPLOADS}a{media_id}.webp", **body(r)}

    def post(r):
        sent = body(r) or {}
        return {"id": 42, "status": "draft", "title": {"rendered": "A"},
                "link": f"{BASE_URL}/?p=42", "featured_media": sent.get("featured_media", 0),
                "meta": sent.get("meta", {})}

    fake.on("GET", "/wp-json/", {"name": "S", "home": BASE_URL, "namespaces": ["wp/v2"]})
    fake.on("GET", "/wp-json/wp/v2/users/me",
            {"name": "B", "roles": ["editor"], "capabilities": {}})
    for kind in ("categories", "tags"):
        fake.on("GET", f"/wp-json/wp/v2/{kind}", (200, [{"id": 1, "name": "A", "slug": "a",
                                                         "count": 1, "parent": 0}],
                                                  {"X-WP-TotalPages": "1"}))
    for kind in ("posts", "pages"):
        fake.on("GET", f"/wp-json/wp/v2/{kind}", (200, [], {"X-WP-TotalPages": "1"}))
    fake.on("POST", POSTS, lambda r: (201, post(r), {}))
    fake.on("GET", f"{POSTS}/42", {"id": 42, "status": "draft", "meta": {
        "_siteseo_titles_title": "", "_siteseo_titles_desc": ""}})
    fake.on("POST", f"{POSTS}/42", post)
    fake.on("POST", MEDIA, created)
    for media_id in range(101, 110):
        fake.on("POST", f"{MEDIA}/{media_id}", updated)
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake.on("POST", f"{ABILITY}/run", siteseo_seo_answer)  # khuôn thật (T-059)


CALLS = {
    "check_connection": (lambda c: c.check_connection(),
                         [("GET", "/wp-json/"), ("GET", ABILITY),
                          ("GET", "/wp-json/wp/v2/users/me")]),
    "list_categories": (lambda c: c.list_categories(), [("GET", "/wp-json/wp/v2/categories")]),
    "list_published": (lambda c: c.list_published(),
                       [("GET", POSTS), ("GET", "/wp-json/wp/v2/pages")]),
    "create_draft": (lambda c: c.create_draft("A", "<p>B</p>"), [("POST", POSTS)]),
    "upload_media": (lambda c: c.upload_media(_jpeg(), "a.jpg", alt_text="A"),
                     [("POST", MEDIA), ("POST", f"{MEDIA}/101")]),
    "set_featured_image": (lambda c: c.set_featured_image(42, 101),
                           [("GET", f"{POSTS}/42"), ("POST", f"{POSTS}/42")]),
    "set_seo_meta": (lambda c: c.set_seo_meta(42, title="Cửa sắt", description="Mô tả"),
                     [("GET", ABILITY), ("GET", f"{POSTS}/42"), ("POST", f"{ABILITY}/run")]),
    "gui_nhap_kem_anh": (
        lambda c: c.create_draft_with_images(
            "A", ["<p>x</p>", DraftImage(make_web_image(_jpeg()), alt="Cổng", featured=True)]
        ),
        [("POST", MEDIA), ("POST", f"{MEDIA}/101"), ("POST", POSTS), ("GET", f"{POSTS}/42"),
         ("POST", f"{POSTS}/42")],
    ),
}
CASES = [
    (call, method, route)
    for call, (_fn, targets) in CALLS.items()
    for method, route in targets
]


@pytest.mark.parametrize(("call", "method", "route"), CASES)
@pytest.mark.parametrize("bad", BAD_BODIES)
@pytest.mark.parametrize("status", [200, 500])
def test_moi_lenh_doc_tra_loi_chi_ra_ket_qua_hay_wordpresserror(call, method, route, bad, status):
    """Câu trả lời lạ ở bất kỳ lệnh nào của mọi hàm công khai: không lỗi Python nào lọt ra, câu
    lỗi không chép lời máy chủ. (Trước T-088: JSON lồng sâu làm lọt ``RecursionError``.)"""
    fake = FakeWordPress()
    _normal_site(fake)
    _send_raw(fake)
    fake.on(method, route, BAD_BODIES[bad](status))
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake),
                             write_seo=True)
    client._created_post_ids.add(42)
    try:
        CALLS[call][0](client)
    except WordPressError as exc:
        assert "evil" not in str(exc) and "bao tri" not in str(exc)


@pytest.mark.parametrize("status", [200, 201, 202])
def test_cau_json_doc_khong_duoc_kem_ma_http(fake_wp, wp_client, status):
    _send_raw(fake_wp)
    fake_wp.on("GET", "/wp-json/", raw(status, b"<html>evil</html>", "text/html"))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    assert f"(mã {status}" in str(err.value) and "evil" not in str(err.value)


@pytest.fixture
def page_site(monkeypatch):
    """Trang Kết nối WordPress dùng client thật với site giả (cách của ``test_soi_loi_t044.py``)."""
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PAGE_PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", BASE_URL)
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    fake = FakeWordPress()
    original = WordPressClient.from_settings.__func__

    def from_settings(cls, settings, **kwargs):
        return original(cls, settings, session=make_session(fake), **kwargs)

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    return fake


def open_wordpress_page(project_root):
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=60)
    at.run()
    at.text_input[0].input(PAGE_PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("status", [200, 404, 500])
def test_trang_ket_noi_tra_loi_long_sau_ra_mot_cau_loi(project_root, page_site, status):
    _send_raw(page_site)
    page_site.on("GET", "/wp-json/", raw(status, b"[" * 100_000 + b"]" * 100_000))
    at = open_wordpress_page(project_root)
    next(b for b in at.button if b.label == "Kiểm tra kết nối").click().run()
    assert not at.exception, at.exception
    assert len(at.error) == 1


# ================================================================ SL-T085-3: lỗi ở lệnh tải ảnh

UNSURE_UPLOADS = {
    "500": (500, b"<h1>Fatal error: evil</h1>", {}),
    "502": (502, b"", {}),
    "503": (503, {"code": "x", "message": "evil"}, {}),
    "504": (504, b"", {}),
    "520": (520, b"", {}),
    "301": (301, b"", {"Location": "https://evil.example/"}),
    "het-gio": requests.exceptions.ReadTimeout("evil"),
    "mat-ket-noi": requests.exceptions.ConnectionError("evil"),
    "ssl": requests.exceptions.SSLError("evil"),
    "dut-giua-chung": requests.exceptions.ChunkedEncodingError("evil"),
    "giai-nen-hong": requests.exceptions.ContentDecodingError("evil"),
    "201-html": (201, b"<html>evil</html>", {}),
    "201-thieu-ma": (201, {"source_url": f"{UPLOADS}a.jpg"}, {}),
    "201-ma-chu": (201, {"id": "9"}, {}),
    "201-danh-sach": (201, [{"id": 9}], {}),
    "200": (200, {"id": 9, "source_url": f"{UPLOADS}a.jpg"}, {}),
    "202": (202, {"id": 9}, {}),
}


@pytest.mark.parametrize("name", UNSURE_UPLOADS)
def test_tai_anh_loi_khong_ro_rang_dan_kiem_thu_vien_media(fake_wp, wp_client, name):
    answer = UNSURE_UPLOADS[name]
    fake_wp.on("POST", MEDIA, (lambda _r: answer) if isinstance(answer, Exception) else answer)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    message = str(err.value)
    assert "có thể đã lên thư viện Media" in message and "Media → Thư viện" in message
    assert "evil" not in message and "example.com" not in message
    assert len(fake_wp.requests) == 1  # không có lệnh ghi đè nào


def test_tai_anh_201_long_sau_dan_kiem_thu_vien_media(fake_wp, wp_client):
    _send_raw(fake_wp)
    fake_wp.on("POST", MEDIA, raw(201, b"[" * 100_000 + b"]" * 100_000))
    with pytest.raises(WordPressError, match="Media → Thư viện"):
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert len(fake_wp.requests) == 1


@pytest.mark.parametrize("status", [400, 401, 403, 404, 405, 408, 409, 413, 415, 422, 429])
def test_tai_anh_bi_tu_choi_4xx_khong_doa_anh_da_len(fake_wp, wp_client, status):
    fake_wp.on("POST", MEDIA, (status, {"code": "x", "message": "evil"}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert "thư viện Media" not in str(err.value) and "evil" not in str(err.value)
    assert f"(mã {status})" in str(err.value)
    assert err.value.status_code == status


def test_tai_anh_thanh_cong_khong_doi(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{UPLOADS}cu.jpg"}, {}))
    fake_wp.on("POST", f"{MEDIA}/9",
               lambda r: {"id": 9, "source_url": f"{UPLOADS}a.jpg", **body(r)})
    media = wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert (media.id, media.source_url, media.alt_text) == (9, f"{UPLOADS}a.jpg", "Cổng")
    assert len(fake_wp.requests) == 2


# ================================================================ SL-T088-1: surrogate lẻ

SURROGATE = "Cửa \ud800 sắt \udfff"  # JSON hợp lệ: "\\ud800", WordPress lõi không tự sinh ra


def _strings(value):
    """Mọi chuỗi trong kết quả của client (dataclass, danh sách, tuple, dict lồng nhau)."""
    if isinstance(value, str):
        yield value
    elif dataclasses.is_dataclass(value):
        for field in dataclasses.fields(value):
            yield from _strings(getattr(value, field.name))
    elif isinstance(value, list | tuple):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(key)
            yield from _strings(item)


SURROGATE_SITES = {
    "ten-site": ("check_connection", "GET", "/wp-json/",
                 {"name": SURROGATE, "home": BASE_URL, "namespaces": ["wp/v2"]}),
    "ten-tai-khoan": ("check_connection", "GET", "/wp-json/wp/v2/users/me",
                      {"name": SURROGATE, "roles": ["editor"], "capabilities": {}}),
    "vai-tro": ("check_connection", "GET", "/wp-json/wp/v2/users/me",
                {"name": "B", "roles": [SURROGATE], "capabilities": {}}),
    "chuyen-muc": ("list_categories", "GET", "/wp-json/wp/v2/categories",
                   (200, [{"id": 1, "name": SURROGATE, "slug": "a", "count": 1, "parent": 0}],
                    {"X-WP-TotalPages": "1"})),
    "bai-da-dang": ("list_published", "GET", POSTS,
                    (200, [{"id": 7, "type": "post", "status": "publish", "slug": "bai-7",
                            "link": f"{BASE_URL}/bai-7/", "title": {"rendered": SURROGATE},
                            "modified_gmt": "2026-10-01T00:00:00", "meta": {}}],
                     {"X-WP-TotalPages": "1"})),
    # Câu trả lời lúc tải (``_describe_draft_media`` lấy địa chỉ ở đây trước): ``is_site_link``
    # nhận, địa chỉ vào ``<img src>`` của bài và ``UploadedImage.source_url``.
    "dia-chi-anh-gui-nhap": ("gui_nhap_kem_anh", "POST", MEDIA,
                             (201, {"id": 101, "source_url": f"{UPLOADS}a\ud800.webp"}, {})),
}


@pytest.mark.parametrize("where", SURROGATE_SITES)
def test_sl_t088_1_chu_website_co_surrogate_le_khong_lot_ra(where):
    call, method, route, answer = SURROGATE_SITES[where]
    fake = FakeWordPress()
    _normal_site(fake)
    fake.on(method, route, answer)
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake),
                             write_seo=True)
    try:
        result = CALLS[call][0](client)
    except WordPressError:
        return  # từ chối dữ liệu hỏng là một cách sửa đúng
    for text in _strings(result):
        text.encode("utf-8")  # chữ trả cho trang, cho SQLite phải mã hóa được


def test_sl_t088_1_trang_ket_noi_khong_vo_vi_surrogate(project_root, page_site):
    page_site.on("GET", "/wp-json/", {"name": SURROGATE, "home": BASE_URL,
                                      "namespaces": ["wp/v2"]})
    page_site.on("GET", "/wp-json/wp/v2/users/me", {"name": "B", "roles": ["editor"],
                                                    "capabilities": {}})
    at = open_wordpress_page(project_root)
    next(b for b in at.button if b.label == "Kiểm tra kết nối").click().run()
    assert not at.exception, at.exception


def test_sl_t088_1_luu_tam_danh_sach_bai_khong_vo_vi_surrogate(tmp_path):
    _call, _method, _route, answer = SURROGATE_SITES["bai-da-dang"]
    fake = FakeWordPress()
    fake.on("GET", POSTS, answer)
    fake.on("GET", "/wp-json/wp/v2/pages", (200, [], {"X-WP-TotalPages": "1"}))
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    store = SiteIndexStore(tmp_path / "site_index.sqlite")
    try:
        index = store.refresh(client)
    except (WordPressError, SiteIndexError):
        return
    for item in index.items:
        item.title.encode("utf-8")

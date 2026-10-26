"""Soi Lỗi · T-085: thử phá phần dọn chốt chặn client WordPress sau T-060.

Kiểm độc lập (không dùng lại dữ liệu hay bản PHP của Thợ Máy, Lá Chắn):

- LC-T060-1: khóa thân JSON theo đường trên **mọi** đường được phép; ``status``; kiểu khóa, kiểu
  thân lạ; lớp chặn phụ ``id``/``name`` khi danh sách bị nới.
- LC-T060-2: giá trị ``_fields`` so với bản Python của WordPress: ``wp_parse_list``
  (``preg_split('/[\\s,]+/')`` không cờ ``u``: khoảng trắng ASCII), rồi
  ``get_fields_for_response`` cắt hai đầu mỗi tên bằng ``trim`` của PHP (``" \\t\\n\\r\\0\\x0B"``,
  **có cả NUL**), ``_fields`` rỗng thì trả mọi trường; trường được dựng khi tên đúng bằng tên
  trường hay bắt đầu bằng «tên.» (``rest_is_field_included``). Biến thể hoa thường, khoảng trắng,
  dấu chấm con, mã hóa, lặp; thử ngẫu nhiên.
- LC-T060-3, SL-T060-1: ``upload_media`` mọi kiểu hỏng ở lệnh ghi đè (mã HTTP, chuyển hướng, lỗi
  mạng, câu trả lời sai dạng, mã ảnh sai) → câu cố định có «thư viện Media», mã ảnh 9.
- Không chặn oan: hằng ``_fields`` và thân JSON thật của app vẫn đi ra.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật. Test
``xfail(strict=True)`` là lỗi tìm được (SL-T085-n trong ``docs/team/reports/T-085-soi-loi.md``):
sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.
"""

import json
import random
import re
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session
from streamlit.testing.v1 import AppTest

import seo_app.wordpress.client as client_module
from seo_app.auth import hash_password
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import (
    _MEDIA_FIELDS,
    _POST_FIELDS,
    _POST_META_FIELDS,
    _PUBLISHED_FIELDS,
    ALLOWED_ROUTES,
    SITESEO_ABILITY_PATH,
    SITESEO_ABILITY_RUN_PATH,
)

PASSWORD = "Rk4t Lm2p Qw9z Xc7v"
PAGE_PASSWORD = "mat-khau-trang-t085"
BLOCKED = "không có trong danh sách được phép"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
PHOTO = b"\xff\xd8\xff\xe0soi-loi-t085"
SOURCE_URL = f"{BASE_URL}/wp-content/uploads/2026/10/cong.jpg"
DEEP_JSON = ("[" * 50_000 + "]" * 50_000).encode()  # JSON lồng 50.000 tầng (hợp lệ)

# Một đường cụ thể cho từng mục của ``ALLOWED_ROUTES``, kèm khóa thân JSON app THẬT gửi trên
# đường đó (đọc từ các hàm công khai, không chép ``ALLOWED_JSON_KEYS``).
ROUTE_JSON = {
    ("GET", "/"): set(),
    ("GET", "/wp/v2/users/me"): set(),
    ("GET", "/wp/v2/categories"): set(),
    ("GET", "/wp/v2/tags"): set(),
    ("GET", "/wp/v2/posts"): set(),
    ("GET", "/wp/v2/pages"): set(),
    ("GET", "/wp/v2/posts/42"): set(),
    ("POST", "/wp/v2/posts"): {
        "status", "title", "content", "excerpt", "slug", "categories", "tags", "featured_media",
    },
    ("POST", "/wp/v2/posts/42"): {"featured_media", "meta"},
    ("POST", "/wp/v2/media"): set(),
    ("POST", "/wp/v2/media/9"): {"alt_text", "title", "caption"},
    ("GET", SITESEO_ABILITY_PATH): set(),
    ("POST", SITESEO_ABILITY_RUN_PATH): {"input"},
}


def body(request):
    return json.loads(request.body) if request.body else None


def query(request):
    return parse_qs(urlsplit(request.url).query, keep_blank_values=True)


def path(request):
    return urlsplit(request.url).path


def answer_all(fake):
    """Mọi đường mẫu (và một đường nhạy cảm) đều trả 200: lệnh nào lọt ra là thấy ngay."""
    for method, route in [*ROUTE_JSON, ("POST", "/code-snippets/v1/snippets")]:
        fake.on(method, "/wp-json" + route, {"id": 9, "status": "draft"})


def blocked(fake, call):
    with pytest.raises(WordPressError) as err:
        call()
    assert fake.requests == []
    assert BLOCKED in str(err.value)


def test_mau_duong_phu_du_danh_sach_duong_duoc_phep():
    patterns = [(method, re.compile(pattern)) for method, pattern in ALLOWED_ROUTES]
    for method, route in ROUTE_JSON:
        hits = [p.pattern for m, p in patterns if m == method and p.fullmatch(route)]
        assert len(hits) == 1, (method, route, hits)
    assert len(ROUTE_JSON) == len(ALLOWED_ROUTES)


# ================================================================ LC-T060-1: khóa thân JSON

JSON_KEYS = [
    "id", "ID", "Id", " id", "id ", "name", "NAME", "Name", "status", "Status", "_fields",
    "context", "_method", "rest_route", "_embed", "_envelope", "post", "parent", "author",
    "password", "date", "date_gmt", "sticky", "template", "comment_status", "meta", "input",
    "title", "content", "excerpt", "slug", "categories", "tags", "featured_media", "alt_text",
    "caption", "description", "source_url", "_links", "force",
]


@pytest.mark.parametrize(("method", "route"), list(ROUTE_JSON))
@pytest.mark.parametrize("key", JSON_KEYS)
def test_khoa_json_theo_dung_duong(fake_wp, wp_client, method, route, key):
    """Khóa app thật gửi trên đường đó thì đi ra; mọi khóa khác (và ``id``, ``name`` ở mọi dạng)
    bị chặn trước khi gửi."""
    answer_all(fake_wp)
    payload = {key: "draft" if key == "status" else 1}
    if key in ROUTE_JSON[(method, route)]:
        wp_client._request(method, route, json=payload)
        (request,) = fake_wp.requests
        assert body(request) == payload
    else:
        blocked(fake_wp, lambda: wp_client._request(method, route, json=payload))


@pytest.mark.parametrize(
    "status",
    ["publish", "future", "pending", "private", "trash", "Draft", "DRAFT", "draft ", " draft",
     "draft\x00", "drаft", "", None, 1, True, ["draft"], {"raw": "draft"}],
)
def test_status_chi_dung_chu_draft(fake_wp, wp_client, status):
    answer_all(fake_wp)
    blocked(
        fake_wp,
        lambda: wp_client._request("POST", "/wp/v2/posts", json={"status": status, "title": "A"}),
    )


@pytest.mark.parametrize(
    "payload",
    [
        {1: "x"},
        {None: "x"},
        {("id",): 7},
        {b"title": "A"},
        type("DictCon", (dict,), {})({"title": "A"}),
        [("title", "A")],
        '{"id": 7}',
    ],
)
def test_khoa_hay_than_json_khong_phai_kieu_thuong_bi_chan(fake_wp, wp_client, payload):
    answer_all(fake_wp)
    blocked(fake_wp, lambda: wp_client._request("POST", "/wp/v2/posts", json=payload))


@pytest.mark.parametrize("key", ["id", "Id", "iD", "name", "nAme", "NAME"])
def test_lop_chan_phu_id_name_khi_danh_sach_bi_noi(fake_wp, wp_client, monkeypatch, key):
    loosened = tuple(
        (method, pattern, keys | {key})
        for method, pattern, keys in client_module._ROUTE_JSON_KEYS
    )
    monkeypatch.setattr(client_module, "_ROUTE_JSON_KEYS", loosened)
    answer_all(fake_wp)
    blocked(
        fake_wp,
        lambda: wp_client._request("POST", "/wp/v2/media/9", json={key: 7, "alt_text": "x"}),
    )


# ================================================================ LC-T060-2: giá trị _fields

PHP_SPLIT = re.compile(r"[ \t\n\x0b\f\r,]+")  # ``\s`` của PCRE không cờ u, và dấu phẩy
PHP_TRIM = " \t\n\r\0\x0b"  # ``trim()`` mặc định của PHP
RENDERED = ("content", "excerpt", "description", "caption", "_embedded", "_links")


def wp_renders(value):
    """WordPress có dựng trường chạy shortcode (hay trả mọi trường) với ``_fields=value`` không:
    ``wp_parse_list``, ``array_map('trim', …)`` của ``get_fields_for_response``, rỗng thì lấy
    mọi trường, rồi ``rest_is_field_included``."""
    tokens = [token for token in PHP_SPLIT.split(value) if token]
    if not tokens:
        return True
    tokens = [token.strip(PHP_TRIM) for token in tokens]
    return any(t == name or t.startswith(name + ".") for t in tokens for name in RENDERED)


def test_ban_python_cua_fields_wordpress_dung_cho_ca_da_biet():
    assert wp_renders("id,content")
    assert wp_renders("content.rendered")
    assert wp_renders("") and wp_renders(" , ")
    assert not wp_renders("Content")  # WordPress so đúng chữ hoa thường
    assert not wp_renders("id content")  # U+00A0 không phải khoảng trắng của PCRE (không u)
    assert not wp_renders(".content") and not wp_renders("contents")
    assert wp_renders("id,\x00content")  # trim() của PHP bỏ NUL ở hai đầu tên trường
    assert not wp_renders("con\x00tent")


FIELDS_ROUTES = [
    ("GET", "/wp/v2/posts", {"status": "publish"}),
    ("GET", "/wp/v2/pages", {"status": "publish"}),
    ("GET", "/wp/v2/posts/42", {"context": "edit"}),
    ("GET", "/wp/v2/categories", {}),
    ("GET", "/wp/v2/tags", {}),
    ("POST", "/wp/v2/posts", {}),
    ("POST", "/wp/v2/posts/42", {}),
    ("POST", "/wp/v2/media", {}),
    ("POST", "/wp/v2/media/9", {}),
]
FIELD_VARIANTS = [
    "{f}", "{F}", "{C}", " {f}", "{f} ", "\t{f}", "id,\n{f}", "id\x0b{f}", "id\x0c{f}", "id\r{f}",
    "{f}.rendered", "{f}.raw", "{f}..x", "id,id,{f}", "{f},{f}", "{f},", ",,{f},,", "id {f} id",
    "%{h}", "{f}%2C", "id;{f}", "id+{f}", "id {f}", "{f}\x1c", "​{f}",
]


@pytest.mark.parametrize(("method", "route", "extra"), FIELDS_ROUTES)
@pytest.mark.parametrize("name", RENDERED)
def test_fields_bien_the_khong_lot_truong_chay_shortcode(fake_wp, wp_client, method, route, extra,
                                                       name):
    """Mọi biến thể (hoa thường, khoảng trắng, dấu chấm con, mã hóa, lặp): giá trị đi ra thì
    WordPress (bản Python ở trên) không dựng trường chạy shortcode."""
    answer_all(fake_wp)
    for template in FIELD_VARIANTS:
        value = template.format(
            f=name, F=name.upper(), C=name.capitalize(), h=f"{ord(name[0]):02X}{name[1:]}"
        )
        fake_wp.requests.clear()
        try:
            wp_client._request(method, route, params={**extra, "_fields": value})
        except WordPressError:
            assert fake_wp.requests == []
            continue
        (request,) = fake_wp.requests
        sent = query(request)["_fields"][0]
        assert sent == value
        assert not wp_renders(sent), (template, value)


@pytest.mark.parametrize("value", ["", " ", ",", " , ,", "\t", "\n,\r"])
@pytest.mark.parametrize(("method", "route", "extra"), FIELDS_ROUTES)
def test_fields_rong_bi_chan(fake_wp, wp_client, method, route, extra, value):
    """``_fields`` rỗng: WordPress trả mọi trường, kể cả ``content``."""
    answer_all(fake_wp)
    blocked(
        fake_wp, lambda: wp_client._request(method, route, params={**extra, "_fields": value})
    )


PIECES = ["id", "content", "excerpt", "description", "caption", "_links", "_embedded", "title",
          "link", "status", ",", ".", " ", "\t", "\x0b", " ", "rendered", "raw", "C", "x",
          "%63", "+", ";", "​"]


def test_fields_ngau_nhien_khong_lot():
    """Thử ngẫu nhiên (hạt giống cố định, không có NUL: xem SL-T085-1): giá trị nào đi ra thì
    WordPress không dựng trường chạy shortcode."""
    rng = random.Random(8585)
    fake = FakeWordPress()
    fake.on("GET", "/wp-json/wp/v2/posts/42", {"id": 42})
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    sent_count = 0
    for _ in range(4000):
        value = "".join(rng.choice(PIECES) for _ in range(rng.randint(1, 7)))
        fake.requests.clear()
        try:
            client._request("GET", "/wp/v2/posts/42", params={"context": "edit", "_fields": value})
        except WordPressError:
            continue
        sent_count += 1
        assert not wp_renders(query(fake.requests[0])["_fields"][0]), repr(value)
    assert sent_count > 500  # đủ ca đi ra để phép thử có nghĩa


@pytest.mark.parametrize(
    ("method", "route", "extra", "fields"),
    [
        ("GET", "/wp/v2/posts", {"status": "publish"}, _PUBLISHED_FIELDS),
        ("GET", "/wp/v2/pages", {"status": "publish"}, _PUBLISHED_FIELDS),
        ("GET", "/wp/v2/posts/42", {"context": "edit"}, _POST_META_FIELDS),
        ("GET", "/wp/v2/categories", {}, "id,name,slug,count,parent"),
        ("GET", "/wp/v2/tags", {}, "id,name,slug,count,parent"),
        ("POST", "/wp/v2/posts", {}, _POST_FIELDS),
        ("POST", "/wp/v2/posts/42", {}, _POST_FIELDS),
        ("POST", "/wp/v2/posts/42", {}, _POST_META_FIELDS),
        ("POST", "/wp/v2/media", {}, _MEDIA_FIELDS),
        ("POST", "/wp/v2/media/9", {}, _MEDIA_FIELDS),
    ],
)
def test_hang_fields_cua_app_van_di_ra(fake_wp, wp_client, method, route, extra, fields):
    answer_all(fake_wp)
    wp_client._request(method, route, params={**extra, "_fields": fields})
    (request,) = fake_wp.requests
    assert query(request)["_fields"] == [fields]
    assert not wp_renders(fields)


@pytest.mark.parametrize(
    ("method", "route", "extra"),
    [("GET", "/wp/v2/posts/42", {"context": "edit"}), ("POST", "/wp/v2/media/9", {}),
     ("GET", "/wp/v2/posts", {"status": "publish"})],
)
@pytest.mark.parametrize(
    "value",
    ["\x00content", "content\x00", "id,\x00content", "id,status,\x00content.rendered",
     "\x00\x00excerpt\x00", "id,description\x00", "\x00caption", "_embedded\x00", "id,\x00_links"],
)
def test_sl_t085_1_fields_co_nul_sat_ten_truong_bi_chan(fake_wp, wp_client, method, route, extra,
                                                       value):
    assert wp_renders(value)  # WordPress sẽ dựng trường chạy shortcode
    answer_all(fake_wp)
    blocked(
        fake_wp, lambda: wp_client._request(method, route, params={**extra, "_fields": value})
    )


# ================================================================ LC-T060-3, SL-T060-1: ảnh

TOXIC = {"code": "rest_x", "message": "evil https://evil.example/x.jpg 0912"}
OVERWRITE_FAILURES = {
    "400": (400, TOXIC, {}),
    "401": (401, TOXIC, {}),
    "403": (403, TOXIC, {}),
    "404": (404, TOXIC, {}),
    "409": (409, TOXIC, {}),
    "413": (413, TOXIC, {}),
    "429": (429, TOXIC, {}),
    "500": (500, b"<h1>evil</h1>", {}),
    "502": (502, b"", {}),
    "503": (503, TOXIC, {}),
    "301": (301, b"", {"Location": "https://evil.example/"}),
    "302": (302, b"", {"Location": "https://evil.example/"}),
    "307": (307, b"", {"Location": "https://evil.example/"}),
    "het-gio": requests.exceptions.ReadTimeout("evil"),
    "mat-ket-noi": requests.exceptions.ConnectionError("evil"),
    "ssl": requests.exceptions.SSLError("evil"),
    "dut-giua-chung": requests.exceptions.ChunkedEncodingError("evil"),
    "html-200": (200, b"<html>evil</html>", {}),
    "danh-sach": [{"id": 9}],
    "chuoi": "evil",
    "null": None,
    "so": 9,
    "ma-khac": {"id": 77, "source_url": "https://evil.example/x.jpg", "alt_text": "Ảnh khác"},
    "thieu-ma": {"source_url": "https://evil.example/x.jpg", "alt_text": "Ảnh khác"},
    "ma-chu": {"id": "9", "source_url": SOURCE_URL},
    "ma-true": {"id": True, "source_url": SOURCE_URL},
    "ma-so-thuc": {"id": 9.0, "source_url": SOURCE_URL},
    "ma-0": {"id": 0},
    "ma-am": {"id": -9},
}


@pytest.mark.parametrize("name", OVERWRITE_FAILURES)
def test_ghi_de_hong_moi_kieu_bao_anh_dang_o_thu_vien_media(fake_wp, wp_client, name):
    answer = OVERWRITE_FAILURES[name]
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": SOURCE_URL}, {}))
    handler = (lambda _r: answer) if isinstance(answer, Exception) else answer
    fake_wp.on("POST", f"{MEDIA}/9", handler)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    message = str(err.value)
    assert "thư viện Media" in message and "mã ảnh 9" in message and "Media → Thư viện" in message
    for piece in ("evil", "Ảnh khác", "0912", "<", "example.com", "77"):
        assert piece not in message, piece
    sent = [(r.method, path(r)) for r in fake_wp.requests]
    assert sent == [("POST", MEDIA), ("POST", f"{MEDIA}/9")]
    if isinstance(answer, tuple) and answer[0] >= 300:
        assert err.value.status_code == answer[0]
        assert f"(mã {answer[0]})" in message


def test_ghi_de_dung_anh_tra_ket_qua_cua_chinh_anh_do(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": "https://evil.example/cu.jpg"}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", lambda r: {"id": 9, "source_url": SOURCE_URL, **body(r)})
    media = wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert (media.id, media.source_url, media.alt_text) == (9, SOURCE_URL, "Cổng")


@pytest.mark.parametrize("status", [400, 403, 413])
def test_tai_anh_bi_tu_choi_ro_rang_khong_bao_anh_da_len(fake_wp, wp_client, status):
    """Đối chứng cho SL-T085-3: website từ chối rõ ràng (4xx) thì ảnh chưa lên, câu báo không
    được dọa «ảnh có thể đã lên»."""
    fake_wp.on("POST", MEDIA, (status, TOXIC, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert "thư viện Media" not in str(err.value)
    assert len(fake_wp.requests) == 1


@pytest.mark.parametrize("where", ["check_connection", "upload_media_ghi_de"])
def test_sl_t085_2_json_long_qua_sau_thanh_cau_loi_co_dinh(fake_wp, wp_client, where):
    if where == "check_connection":
        fake_wp.on("GET", "/wp-json/", (200, DEEP_JSON, {}))
        with pytest.raises(WordPressError):
            wp_client.check_connection()
        return
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": SOURCE_URL}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", (200, DEEP_JSON, {}))
    with pytest.raises(WordPressError, match="thư viện Media"):
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")


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


def test_sl_t085_2_trang_ket_noi_khong_vo_vi_json_long_sau(project_root, page_site):
    page_site.on("GET", "/wp-json/", (200, DEEP_JSON, {}))
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=60)
    at.run()
    at.text_input[0].input(PAGE_PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception, at.exception
    next(b for b in at.button if b.label == "Kiểm tra kết nối").click().run()
    assert not at.exception
    assert len(at.error) == 1


@pytest.mark.parametrize(
    "answer",
    [
        (500, b"<h1>Fatal error: Allowed memory size exhausted</h1>", {}),
        (502, b"", {}),
        (503, b"", {}),
        requests.exceptions.ReadTimeout("x"),
        (201, b"<html>ok</html>", {}),
        (201, {"source_url": SOURCE_URL}, {}),
    ],
)
def test_sl_t085_3_tai_anh_loi_ma_anh_co_the_da_len_thi_dan_kiem_thu_vien(fake_wp, wp_client,
                                                                          answer):
    fake_wp.on("POST", MEDIA, (lambda _r: answer) if isinstance(answer, Exception) else answer)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert "thư viện Media" in str(err.value) and "Media → Thư viện" in str(err.value)


# ================================================================ không chặn oan


@pytest.fixture
def real_site(fake_wp):
    def post(request):
        return {"id": 42, "status": "draft", "title": {"raw": "A", "rendered": "A"},
                "link": f"{BASE_URL}/?p=42", **(body(request) or {})}

    fake_wp.on("POST", POSTS, lambda r: (201, post(r), {}))
    fake_wp.on("GET", f"{POSTS}/42", {"id": 42, "status": "draft", "meta": {
        "_siteseo_titles_title": "", "_siteseo_titles_desc": ""}})
    fake_wp.on("POST", f"{POSTS}/42", post)
    return fake_wp


def test_tao_nhap_du_truong_roi_anh_dai_dien_roi_seo_du_phong_van_di_ra(real_site):
    client = WordPressClient(
        BASE_URL, "lam", PASSWORD, session=make_session(real_site), write_seo=True
    )
    post = client.create_draft(
        "Tiêu đề", "<p>Nội dung</p>", categories=[3], tags=[5], excerpt="Tóm tắt",
        slug="tieu-de", featured_media=7,
    )
    client.set_featured_image(post.id, 8)
    result = client.set_seo_meta(post.id, title="Sửa cửa sắt", description="Mô tả ngắn")
    assert result.written
    sent = [(r.method, path(r), sorted(body(r) or {})) for r in real_site.requests]
    assert sent[0] == ("POST", POSTS, ["categories", "content", "excerpt", "featured_media",
                                       "slug", "status", "tags", "title"])
    assert body(real_site.requests[0])["status"] == "draft"
    assert ("POST", f"{POSTS}/42", ["featured_media"]) in sent
    assert ("POST", f"{POSTS}/42", ["meta"]) in sent

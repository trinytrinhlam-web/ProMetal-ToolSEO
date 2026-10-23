"""T-060: dọn lỗi Thấp của client WordPress (Lá Chắn T-042, T-061, T-071).

- LC-T042-1: ``_request`` chỉ nhận tham số theo danh sách của từng đường; không bao giờ gửi
  ``rest_route``, ``_method``, ``_envelope``, ``_jsonp``, header ``X-HTTP-Method-Override``.
- LC-T042-4: câu lỗi cố định kèm mã HTTP, không chép lời máy chủ, không chép ``WORDPRESS_URL``.
- LC-T042-5: ``WORDPRESS_URL`` không được có đoạn đường là file (``.pht``, ``.cgi``…).
- LC-T061-2: chữ SEO có «<» liền ký tự không phải khoảng trắng ASCII bị chặn.
- LC-T061-3, LC-T071-1: ``upload_media`` chỉ nhận ``201``, luôn ghi đè alt, tiêu đề, chú thích.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật.
"""

import json
import re
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session

import seo_app.wordpress.client as client_module
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import ALLOWED_PARAMS, ALLOWED_ROUTES, _seo_text

PASSWORD = "abcd efgh ijkl mnop"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
BLOCKED = "không có trong danh sách được phép"
JPEG = b"\xff\xd8\xff\xe0anh-gia"
SOURCE_URL = f"{BASE_URL}/wp-content/uploads/2026/10/cong.jpg"
# Lời máy chủ (hay plugin) đặt tùy ý: không được lên màn hình (LC-T042-4).
SERVER_TEXT = "Gọi 0909 123 456 để được hỗ trợ https://evil.example/x [x](y) <b>quản trị</b>"


def body(request):
    return json.loads(request.body) if request.body else None


def answer_everything(fake):
    """Mọi đường được phép (và vài đường nhạy cảm) đều trả lời 200: request nào lọt là thấy."""
    for method in ("GET", "POST"):
        for path in (
            "/wp-json/",
            "/wp-json/wp/v2/posts",
            "/wp-json/wp/v2/posts/42",
            "/wp-json/wp/v2/media",
            "/wp-json/wp/v2/media/9",
            "/wp-json/code-snippets/v1/snippets",
        ):
            fake.on(method, path, {"id": 42, "status": "draft"})


# ================================================================ LC-T042-1: tham số, header


def test_moi_duong_duoc_phep_deu_co_danh_sach_tham_so_va_nguoc_lai():
    assert set(ALLOWED_PARAMS) == set(ALLOWED_ROUTES)
    for names in ALLOWED_PARAMS.values():
        assert not names & {"rest_route", "_method", "_envelope", "_jsonp", "_embed"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/"),
        ("GET", "/wp/v2/posts"),
        ("GET", "/wp/v2/posts/42"),
        ("POST", "/wp/v2/posts"),
        ("POST", "/wp/v2/posts/42"),
        ("POST", "/wp/v2/media"),
        ("POST", "/wp/v2/media/9"),
    ],
)
@pytest.mark.parametrize(
    "params",
    [
        {"rest_route": "/code-snippets/v1/snippets"},
        {"_method": "DELETE"},
        {"_envelope": "1"},
        {"_jsonp": "f"},
        {"rest.route": "/code-snippets/v1/snippets"},  # PHP đổi "." trong tên thành "_"
        {"rest route": "/code-snippets/v1/snippets"},
        {"rest_route[]": "/code-snippets/v1/snippets"},
        {"REST_ROUTE": "/code-snippets/v1/snippets"},
        {"_METHOD": "DELETE"},
        {"_embed": "1"},
        {"_fields": "id", "_method": "DELETE"},  # khóa được phép đi kèm khóa cấm
    ],
)
def test_tham_so_doi_duong_hay_phuong_thuc_bi_chan_truoc_khi_gui(
    fake_wp, wp_client, method, path, params
):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError) as err:
        wp_client._request(method, path, params=params)
    assert fake_wp.requests == []
    assert BLOCKED in str(err.value)
    assert "code-snippets" not in str(err.value) and "DELETE" not in str(err.value)


@pytest.mark.parametrize(
    "name",
    [
        "X-HTTP-Method-Override",
        "x-http-method-override",
        "X_HTTP_METHOD_OVERRIDE",
        "X-Method-Override",
        "X-HTTP-Method",
    ],
)
def test_header_doi_phuong_thuc_bi_chan_ca_trong_lenh_lan_trong_session(name):
    fake = FakeWordPress()
    answer_everything(fake)
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    with pytest.raises(WordPressError, match=BLOCKED):
        client._request("POST", "/wp/v2/posts/42", json={"a": 1}, headers={name: "DELETE"})
    client._session.headers[name] = "DELETE"
    with pytest.raises(WordPressError, match=BLOCKED):
        client._request("GET", "/")
    assert fake.requests == []


@pytest.mark.parametrize(
    "options",
    [
        {"files": {"file": ("a.jpg", JPEG)}},  # thân multipart thành $_POST (rest_route)
        {"data": {"rest_route": "/code-snippets/v1/snippets"}},  # thân form thành $_POST
        {"data": "rest_route=/code-snippets/v1/snippets"},
        {"data": JPEG, "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
        {"data": JPEG, "headers": {"Content-Type": "multipart/form-data; boundary=x"}},
        {"data": JPEG, "headers": {"Content-Type": "image/jpeg", "X-Other": "1"}},
        {"data": JPEG, "headers": {"Content-Type": b"image/jpeg"}},
        {"json": [1, 2]},
        {"json": "rest_route"},
        {"verify": False},
        {"auth": ("khac", "khac")},
        {"cookies": {"a": "b"}},
        {"allow_redirects": True},
        {"timeout": 999},
        {"params": [("_fields", "id")]},
        {"params": "_fields=id&rest_route=/x"},
        {"params": {"_fields": ["id", "source_url"]}},
        {"params": {"_fields": True}},
        {"params": {"_fields": None}},
        {"params": {"_fields": {"a": 1}}},
        {"headers": [("Content-Type", "image/jpeg")]},
    ],
)
def test_tuy_chon_la_cua_lenh_bi_chan_truoc_khi_gui(fake_wp, wp_client, options):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request("POST", "/wp/v2/media", **options)
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    ("method", "path", "params"),
    [
        ("GET", "/", {"_fields": "name"}),
        ("GET", "/wp/v2/users/me", {"_fields": "capabilities"}),
        ("POST", "/wp/v2/posts", {"status": "publish"}),
        ("POST", "/wp/v2/posts/42", {"context": "edit"}),
        ("POST", "/wp/v2/media", {"post": "42"}),
        ("POST", "/wp/v2/media/9", {"status": "publish"}),
        ("GET", "/wp/v2/posts/42", {"status": "publish"}),
        ("GET", "/wp/v2/categories", {"status": "draft"}),
        ("GET", "/wp/v2/posts", {"hide_empty": "false"}),
    ],
)
def test_tham_so_cua_duong_khac_bi_chan(fake_wp, wp_client, method, path, params):
    """Danh sách theo TỪNG đường: khóa hợp lệ ở đường này không đi được sang đường khác."""
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request(method, path, params=params)
    assert fake_wp.requests == []


def test_session_co_tham_so_hay_loai_than_rieng_bi_chan():
    fake = FakeWordPress()
    answer_everything(fake)
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    client._session.params = {"rest_route": "/code-snippets/v1/snippets"}
    with pytest.raises(WordPressError, match=BLOCKED):
        client._request("GET", "/")
    client._session.params = {}
    client._session.headers["Content-Type"] = "application/x-www-form-urlencoded"
    with pytest.raises(WordPressError, match=BLOCKED):
        client._request("POST", "/wp/v2/posts/42", json={"featured_media": 1})
    assert fake.requests == []


@pytest.mark.parametrize(
    ("method", "path", "params"),
    [
        ("GET", "/wp/v2/users/me", {"context": "edit"}),
        ("GET", "/wp/v2/categories", {"per_page": 100, "page": 2, "orderby": "name",
                                      "order": "asc", "hide_empty": "false", "_fields": "id"}),
        ("GET", "/wp/v2/pages", {"status": "publish", "per_page": 100, "page": 1,
                                 "orderby": "id", "order": "asc", "_fields": "id,link"}),
        ("GET", "/wp/v2/posts/42", {"context": "edit", "_fields": "id,status,meta"}),
        ("POST", "/wp/v2/posts", {"_fields": "id,status"}),
        ("POST", "/wp/v2/media/9", {"_fields": "id,source_url,alt_text"}),
    ],
)
def test_tham_so_dung_danh_sach_van_gui_nguyen_ven(fake_wp, wp_client, method, path, params):
    for route in ("/", "/wp/v2/users/me", "/wp/v2/categories", "/wp/v2/pages",
                  "/wp/v2/posts/42", "/wp/v2/posts", "/wp/v2/media/9"):
        fake_wp.on(method, "/wp-json" + route, {"id": 9})
    wp_client._request(method, path, params=params)
    (request,) = fake_wp.requests
    assert urlsplit(request.url).path == "/wp-json" + path
    assert parse_qs(urlsplit(request.url).query) == {k: [str(v)] for k, v in params.items()}


def test_tai_anh_van_gui_loai_file_va_ten_file(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": SOURCE_URL}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", {"id": 9, "source_url": SOURCE_URL})
    wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    upload = fake_wp.requests[0]
    assert upload.headers["Content-Type"] == "image/jpeg"
    assert upload.headers["Content-Disposition"] == 'attachment; filename="cong.jpg"'
    assert not [name for name in upload.headers if "method" in name.lower()]


# ================================================================ LC-T042-4: câu lỗi cố định


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (400, "rest_invalid_param"),
        (401, "incorrect_password"),
        (403, "rest_forbidden"),
        (404, "rest_no_route"),
        (404, "rest_post_invalid_id"),
        (409, "conflict"),
        (413, "too_big"),
        (429, "too_many"),
        (500, "internal_server_error"),
        (502, "bad_gateway"),
    ],
)
def test_cau_loi_co_ma_http_khong_chep_loi_may_chu_hay_dia_chi(fake_wp, wp_client, status, code):
    fake_wp.on("GET", "/wp-json/", (status, {"code": code, "message": SERVER_TEXT}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    message = str(err.value)
    assert f"(mã {status})" in message
    for piece in ("0909", "evil", "quản trị", "<b>", "[x]", "example.com", "(WordPress:"):
        assert piece not in message, piece
    assert code not in message
    assert err.value.status_code == status
    assert err.value.code == code  # vẫn giữ để code phân biệt lỗi (không hiện lên màn hình)


@pytest.mark.parametrize(
    "code", [" rest_no_route", "rest no route", "<b>x</b>", "x" * 101, 404, None, ["a"], {"a": 1}]
)
def test_ma_loi_la_cua_may_chu_khong_duoc_giu(fake_wp, wp_client, code):
    fake_wp.on("GET", "/wp-json/", (400, {"code": code, "message": SERVER_TEXT}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    assert err.value.code == ""
    assert str(err.value) == "WordPress báo lỗi (mã 400)."


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.list_categories(),
        lambda c: c.list_published(),
        lambda c: c.create_draft("A", "<p>B</p>"),
        lambda c: c.upload_media(JPEG, "cong.jpg", alt_text="Cổng"),
    ],
)
def test_ham_cong_khai_khong_chep_loi_may_chu(fake_wp, wp_client, call):
    for method, path in (
        ("GET", "/wp-json/wp/v2/categories"),
        ("GET", "/wp-json/wp/v2/posts"),
        ("POST", POSTS),
        ("POST", MEDIA),
    ):
        fake_wp.on(method, path, (400, {"code": "rest_invalid_param", "message": SERVER_TEXT}, {}))
    with pytest.raises(WordPressError) as err:
        call(wp_client)
    assert str(err.value) == "WordPress báo lỗi (mã 400)."


def test_loi_mang_va_chuyen_huong_khong_chep_dia_chi(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", lambda _r: requests.exceptions.ConnectionError("down"))
    with pytest.raises(WordPressError, match="Không kết nối được") as err:
        wp_client.check_connection()
    assert "example.com" not in str(err.value)
    fake_wp.on("GET", "/wp-json/", (302, b"", {"Location": "https://evil.example/"}))
    with pytest.raises(WordPressError, match="chuyển hướng") as err:
        wp_client.check_connection()
    assert "(mã 302)" in str(err.value)
    assert "evil" not in str(err.value) and "example.com" not in str(err.value)


@pytest.mark.parametrize(
    "url",
    [
        "htps://ten:matkhau@suachua.vn",
        "suachua.vn/blog?u=ten&p=matkhau",
        "ten:matkhau@suachua.vn",
        "http://ten:matkhau@suachua.vn",
        "https://ten:matkhau@suachua.vn",
        "https://suachua.vn/a.cgi?p=matkhau",
    ],
)
def test_cau_loi_khoi_tao_khong_chep_wordpress_url(url):
    with pytest.raises(WordPressError) as err:
        WordPressClient(url, "lam", PASSWORD)
    message = str(err.value)
    assert "matkhau" not in message and "suachua" not in message and "ten:" not in message


# ================================================================ LC-T042-5: file chạy được


@pytest.mark.parametrize(
    "path",
    [
        "/x.pht",
        "/x.PHT",
        "/x.phtml",
        "/cgi-bin/x.cgi",
        "/x.shtml",
        "/x.asp",
        "/x.aspx",
        "/x.jsp",
        "/x.php",
        "/x.php5",
        "/x.py",
        "/x.pl",
        "/index.php",
        "/blog/x.cgi/sub",
        "/blog.v2",
    ],
)
def test_wordpress_url_co_doan_la_file_bi_tu_choi(path):
    with pytest.raises(WordPressError) as err:
        WordPressClient(f"https://suachua.vn{path}", "lam", PASSWORD)
    assert "suachua" not in str(err.value) and path not in str(err.value)


@pytest.mark.parametrize(
    "url",
    ["https://example.com/blog", "https://example.com/cgi-bin", "https://example.com/~user/wp_1"],
)
def test_wordpress_url_thu_muc_thuong_van_duoc_nhan(url):
    assert WordPressClient(url, "lam", PASSWORD).base_url == url


# ================================================================ LC-T061-2: «<» trong chữ SEO


@pytest.mark.parametrize(
    "text",
    [
        "[<>code_snippet id=1]",
        "Giá tốt [<1>code_snippet id=1] cửa sắt",
        "[<=>gallery ids=1]",
        "Video [<.>embed] lắp cổng",
        "[<đ>embed]",
        "[<​>embed]",  # ký tự vô hình bị gỡ: còn "<>"
        "Giá <500k",
        "Cửa sắt <",  # "<" ở cuối chữ
        "Cửa < sắt",  # dấu cách không ngắt: không phải khoảng trắng của strip_tags
        "Cửa <　sắt",
        "Cửa ＜1＞ sắt",  # "<" toàn khổ (NFKC thành "<")
        "Cửa ﹤1﹥ sắt",  # "<" nhỏ (NFKC thành "<")
    ],
)
def test_chu_seo_co_dau_nho_hon_lien_ky_tu_bi_chan(text):
    with pytest.raises(WordPressError):
        _seo_text("Tiêu đề SEO", text, 300)


@pytest.mark.parametrize(
    "text", ["Cửa sắt < 2 triệu", "a < b < c", "Giá <\t500k", "Cửa sắt [ 2026 ] bền"]
)
def test_chu_seo_co_dau_nho_hon_va_khoang_trang_van_qua(text):
    assert _seo_text("Tiêu đề SEO", text, 300)


def test_chu_seo_dau_nho_hon_bi_chan_truoc_moi_lenh(fake_wp):
    client = WordPressClient(
        BASE_URL, "lam", PASSWORD, session=make_session(fake_wp), write_seo=True
    )
    client._created_post_ids.add(42)
    with pytest.raises(WordPressError, match="«<»"):
        client.set_seo_meta(42, title="[<>code_snippet id=1] Cửa sắt")
    assert fake_wp.requests == []


def test_mau_shortcode_dung_chung_voi_t056_khong_doi():
    """T-056 dùng lại ``_has_shortcode``, ``_SHORTCODE_OPEN``: phiếu này không đổi hai thứ đó."""
    assert client_module._SHORTCODE_OPEN.pattern == r"\[[\[/]?[^<>&/\[\]=\x00-\x20]"
    assert client_module._has_shortcode("[embed]x")
    assert not client_module._has_shortcode("[<>embed]")  # chặn ở bước «<» riêng của _seo_text


# ================================================================ LC-T061-3, LC-T071-1: ảnh


def media_site(fake, *, status=201):
    fake.on("POST", MEDIA, (status, {"id": 9, "source_url": SOURCE_URL}, {}))
    fake.on("POST", f"{MEDIA}/9", lambda r: {"id": 9, "source_url": SOURCE_URL, **body(r)})


def test_upload_media_luon_ghi_de_ca_ba_o_ke_ca_khi_trong(fake_wp, wp_client):
    """LC-T061-3: ô trống cũng gửi (chuỗi rỗng), tiêu đề trống lấy tên file đã làm sạch; nếu
    không, WordPress lấy tiêu đề, chú thích, alt từ chữ nằm trong file ảnh."""
    media_site(fake_wp)
    media = wp_client.upload_media(JPEG, "Ảnh Cổng Inox.JPG")
    upload, update = fake_wp.requests
    assert urlsplit(upload.url).path == MEDIA
    assert urlsplit(update.url).path == f"{MEDIA}/9"
    assert body(update) == {"alt_text": "", "title": "anh-cong-inox", "caption": ""}
    assert parse_qs(urlsplit(update.url).query) == {"_fields": ["id,source_url,alt_text"]}
    assert media.id == 9 and media.alt_text == ""


@pytest.mark.parametrize(
    ("kwargs", "sent"),
    [
        ({"alt_text": "Cổng"}, {"alt_text": "Cổng", "title": "cong", "caption": ""}),
        ({"title": "Cổng inox"}, {"alt_text": "", "title": "Cổng inox", "caption": ""}),
        ({"caption": "Sau khi sơn"}, {"alt_text": "", "title": "cong", "caption": "Sau khi sơn"}),
    ],
)
def test_upload_media_o_co_chu_giu_nguyen_o_trong_van_ghi_de(fake_wp, wp_client, kwargs, sent):
    media_site(fake_wp)
    wp_client.upload_media(JPEG, "cong.jpg", **kwargs)
    assert body(fake_wp.requests[-1]) == sent


def test_upload_media_o_none_coi_nhu_trong_van_ghi_de(fake_wp, wp_client):
    media_site(fake_wp)
    wp_client.upload_media(JPEG, "cong.jpg", alt_text=None, title=None, caption=None)
    assert body(fake_wp.requests[-1]) == {"alt_text": "", "title": "cong", "caption": ""}


@pytest.mark.parametrize("field", ["alt_text", "title", "caption"])
@pytest.mark.parametrize("value", [5, b"[code_snippet id=1]", ["x"], {"raw": "x"}])
def test_upload_media_o_khong_phai_chu_bi_chan_truoc_khi_tai(fake_wp, wp_client, field, value):
    """Không tải ảnh khi chưa chắc ghi đè được 3 ô: nếu không, chữ trong file ở lại website."""
    media_site(fake_wp)
    with pytest.raises(WordPressError, match="Chưa gửi gì"):
        wp_client.upload_media(JPEG, "cong.jpg", **{field: value})
    assert fake_wp.requests == []


def test_upload_media_ba_o_khong_con_ngoac_vuong_tran(fake_wp, wp_client):
    media_site(fake_wp)
    wp_client.upload_media(
        JPEG,
        "cong.jpg",
        alt_text="[code_snippet id=1]",
        title="[embed]x[/embed]",
        caption="[gallery]",
    )
    sent = body(fake_wp.requests[-1])
    assert set(sent) == {"alt_text", "title", "caption"}
    assert all("[" not in value and "]" not in value for value in sent.values())
    assert sent["alt_text"] == "&#91;code_snippet id=1&#93;"


@pytest.mark.parametrize("status", [200, 202, 203, 204, 206, 207, 208, 226])
def test_upload_media_chi_nhan_201(fake_wp, wp_client, status):
    media_site(fake_wp, status=status)
    with pytest.raises(WordPressError, match="201") as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Alt", title="T", caption="C")
    assert [urlsplit(r.url).path for r in fake_wp.requests] == [MEDIA]
    assert not re.search(r"example\.com|cong\.jpg", str(err.value))

"""Soi Lỗi · T-060: thử phá phần dọn lỗi Thấp của client WordPress (Lá Chắn T-042, T-061, T-071).

Kiểm độc lập (không dùng lại dữ liệu, site giả hay bản PHP của Thợ Máy):

- LC-T042-1: khóa cấm viết khác (hoa thường, ``%5F``, ``[]``, dấu cách) trên **mọi** đường được
  phép; giá trị tham số không tách thành khóa mới; header lạ; đường có truy vấn; ``session``.
- LC-T042-4: thân trả về độc (HTML, chuỗi rất dài, địa chỉ, mật khẩu) với nhiều mã HTTP; lỗi mạng
  có địa chỉ và mật khẩu trong thông điệp; lệnh ghi đè ảnh lỗi.
- LC-T042-5: ``WORDPRESS_URL`` có ``index.php``, dấu chấm cuối, ``%2E``, ``;``, ``::$DATA``…
- LC-T061-2: «<» + ký tự Unicode lạ; thử ngẫu nhiên với bản Python của ``sanitize_text_field``
  (``isspace`` của C, như PHP).
- LC-T061-3, LC-T071-1: ``upload_media`` với 200/202/204, 201 thiếu mã hay mã sai kiểu.
- Không chặn oan: mọi lệnh thật app gửi vẫn đi ra đúng đường, đúng tham số.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật. Test
``xfail(strict=True)`` là lỗi tìm được (SL-T060-n trong ``docs/team/reports/T-060-soi-loi.md``):
sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.
"""

import html
import io
import json
import random
import re
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, make_session, siteseo_seo_answer
from PIL import Image

import seo_app.wordpress.client as client_module
from seo_app.images.process import make_web_image
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import ALLOWED_ROUTES, SITESEO_ABILITY_PATH, DraftImage, _seo_text

PASSWORD = "Qz9x Wv8u Ts7r Pq6o"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
ABILITY = f"/wp-json{SITESEO_ABILITY_PATH}"
BLOCKED = "không có trong danh sách được phép"
PHOTO = b"\xff\xd8\xff\xe0soi-loi-t060"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
SITE = "https://suachua-thu.vn"  # địa chỉ riêng cho test câu lỗi (khác chữ mẫu example.com)

# Một đường cụ thể cho từng mục của ``ALLOWED_ROUTES`` (test đầu tiên chứng minh đủ và đúng).
ROUTE_SAMPLES = [
    ("GET", "/"),
    ("GET", "/wp/v2/users/me"),
    ("GET", "/wp/v2/categories"),
    ("GET", "/wp/v2/tags"),
    ("GET", "/wp/v2/posts"),
    ("GET", "/wp/v2/pages"),
    ("GET", "/wp/v2/posts/42"),
    ("POST", "/wp/v2/posts"),
    ("POST", "/wp/v2/posts/42"),
    ("POST", "/wp/v2/media"),
    ("POST", "/wp/v2/media/9"),
    ("GET", SITESEO_ABILITY_PATH),
    ("POST", f"{SITESEO_ABILITY_PATH}/run"),
]


def body(request):
    return json.loads(request.body) if request.body else None


def query(request):
    return parse_qs(urlsplit(request.url).query, keep_blank_values=True)


def path(request):
    return urlsplit(request.url).path


def answer_all(fake):
    """Mọi đường mẫu (và một đường nhạy cảm) đều trả 200: lệnh nào lọt ra là thấy ngay."""
    for method, route in [*ROUTE_SAMPLES, ("POST", "/code-snippets/v1/snippets")]:
        fake.on(method, "/wp-json" + route, {"id": 9})


def blocked_before_sending(fake, call):
    with pytest.raises(WordPressError) as err:
        call()
    assert fake.requests == []
    assert BLOCKED in str(err.value)
    return str(err.value)


# ================================================================ LC-T042-1: tham số, header


def test_mau_duong_phu_du_danh_sach_duong_duoc_phep():
    patterns = [(method, re.compile(pattern)) for method, pattern in ALLOWED_ROUTES]
    for method, route in ROUTE_SAMPLES:
        hits = [p.pattern for m, p in patterns if m == method and p.fullmatch(route)]
        assert len(hits) == 1, (method, route, hits)
    assert len(ROUTE_SAMPLES) == len(ALLOWED_ROUTES)


# Khóa cấm viết khác: PHP gập "." và dấu cách thành "_", nhưng không gập hoa thường hay "%5F";
# dù vậy client phải chặn hết (danh sách cho phép theo từng đường, so đúng từng chữ).
FORBIDDEN_KEYS = [
    "rest_route", "Rest_Route", "rest%5Froute", "rest%5froute", "rest_route ", " rest_route",
    "rest_route[a]", "_method", "_Method", "%5Fmethod", "_method[]", "_envelope", "_Envelope",
    "_envelope[]", "_jsonp", "_JSONP", "_jsonp[]",
]


@pytest.mark.parametrize(("method", "route"), ROUTE_SAMPLES)
@pytest.mark.parametrize("key", FORBIDDEN_KEYS)
def test_khoa_cam_moi_dang_bi_chan_tren_moi_duong(fake_wp, wp_client, method, route, key):
    answer_all(fake_wp)
    message = blocked_before_sending(
        fake_wp, lambda: wp_client._request(method, route, params={key: "/code-snippets/v1"})
    )
    assert "code-snippets" not in message


@pytest.mark.parametrize(
    "value",
    [
        "id&rest_route=/code-snippets/v1/snippets",
        "id?_method=DELETE",
        "id#_method=DELETE",
        "id;rest_route=/x",
        "id\r\nX-HTTP-Method-Override: DELETE",
        "id%26rest_route%3D%2Fx",
    ],
)
def test_gia_tri_tham_so_khong_tach_thanh_khoa_moi(fake_wp, wp_client, value):
    """Giá trị chữ được gửi nhưng phải được mã hóa: máy chủ chỉ thấy đúng một khóa ``_fields``."""
    answer_all(fake_wp)
    wp_client._request("POST", "/wp/v2/posts", params={"_fields": value})
    (request,) = fake_wp.requests
    assert path(request) == POSTS
    assert query(request) == {"_fields": [value]}
    assert not [name for name in request.headers if "method" in name.lower()]


@pytest.mark.parametrize(
    "name",
    [
        "X-HTTP-Method-Override ",
        "x-hTTp-method-oVERRIDE",
        "X-Original-URL",
        "X-Rewrite-URL",
        "Host",
        "Authorization",
        "Cookie",
        "content-type ",
    ],
)
def test_header_la_cua_lenh_bi_chan(fake_wp, wp_client, name):
    answer_all(fake_wp)
    blocked_before_sending(
        fake_wp,
        lambda: wp_client._request(
            "POST", "/wp/v2/posts/42", json={"featured_media": 9}, headers={name: "DELETE"}
        ),
    )


@pytest.mark.parametrize(
    "content_type",
    ["IMAGE/JPEG", "image/jpeg; charset=utf-8", " image/jpeg", "text/plain", "application/json"],
)
def test_loai_than_khong_dung_loai_anh_bi_chan(fake_wp, wp_client, content_type):
    answer_all(fake_wp)
    blocked_before_sending(
        fake_wp,
        lambda: wp_client._request(
            "POST", "/wp/v2/media", data=PHOTO, headers={"Content-Type": content_type}
        ),
    )


@pytest.mark.parametrize(
    "route",
    [
        "/wp/v2/posts?rest_route=/code-snippets/v1/snippets",
        "/wp/v2/posts/42?_method=DELETE",
        "/?rest_route=/",
        "/wp/v2/posts#x",
        "/wp/v2/posts%3F_method=DELETE",
    ],
)
def test_duong_kem_truy_van_bi_chan(fake_wp, wp_client, route):
    answer_all(fake_wp)
    blocked_before_sending(fake_wp, lambda: wp_client._request("POST", route))


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("params", [("rest_route", "/code-snippets/v1/snippets")]),
        ("params", {"_fields": "id"}),  # khóa được phép cũng không được gắn sẵn vào session
        ("headers", {"x-method-override": "DELETE"}),
        ("headers", {"content-type": "application/x-www-form-urlencoded"}),
    ],
)
def test_session_gan_san_tham_so_hay_header_bi_chan(fake_wp, attribute, value):
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake_wp))
    answer_all(fake_wp)
    if attribute == "params":
        client._session.params = value
    else:
        client._session.headers.update(value)
    blocked_before_sending(fake_wp, lambda: client._request("GET", "/"))


@pytest.mark.parametrize(
    "options",
    [
        {"data": {"rest_route": "/code-snippets/v1/snippets"}},  # thân form: WordPress đọc $_POST
        {"data": [("rest_route", "/code-snippets/v1/snippets")]},
        {"data": bytearray(b"rest_route=/x")},
        {"data": memoryview(b"x")},
        {"files": {"file": ("a.jpg", PHOTO)}},
        {"json": [{"rest_route": "/x"}]},
        {"json": "rest_route"},
        {"stream": True},
        {"proxies": {"https": "http://evil.example:8080"}},
        {"cert": "khoa.pem"},
        {"hooks": {"response": []}},
        {"auth": None},
        {"verify": False},
        {"allow_redirects": True},
    ],
)
def test_tuy_chon_khac_cua_requests_bi_chan(fake_wp, wp_client, options):
    answer_all(fake_wp)
    blocked_before_sending(fake_wp, lambda: wp_client._request("POST", "/wp/v2/media", **options))


@pytest.mark.parametrize(
    "key",
    ["rest_route", "REST_ROUTE", "rest.route", "rest route", "rest_route[]", "_method", "_Method",
     "_envelope", "_jsonp", "_jsonp[x]"],
)
def test_lop_chan_phu_van_chan_khi_danh_sach_cho_phep_bi_noi(fake_wp, wp_client, monkeypatch, key):
    """«Phòng khi ai đó nới danh sách cho phép» (``_FORBIDDEN_PARAMS``): cho ``GET /`` nhận mọi
    khóa thì khóa đổi đường, đổi phương thức vẫn bị chặn."""
    loosened = tuple(
        (method, pattern, names | {key}) for method, pattern, names in client_module._ROUTE_PARAMS
    )
    monkeypatch.setattr(client_module, "_ROUTE_PARAMS", loosened)
    answer_all(fake_wp)
    blocked_before_sending(fake_wp, lambda: wp_client._request("GET", "/", params={key: "/x"}))
    wp_client._request("GET", "/", params={})  # đối chứng: đường vẫn gọi được
    assert len(fake_wp.requests) == 1


# ================================================================ LC-T042-4: câu lỗi cố định

TOXIC_BODIES = {
    "html": (
        "<html><h1>Lỗi</h1><a href='https://evil.example'>bấm</a><script>alert(1)</script></html>"
    ).encode(),
    "rat-dai": {"code": "rest_x", "message": "evil " + "x" * 100_000},
    "dia-chi": {"code": "rest_forbidden", "message": f"{SITE}/wp-admin evil 0912 345 678"},
    "mat-khau": {"code": "incorrect_password", "message": f"Sai {PASSWORD} evil"},
    "code-doc": {"code": "<b>evil</b> https://evil.example", "message": "evil"},
    "danh-sach": ["evil", PASSWORD],
    "chuoi": "evil",
    "null": None,
    "rong": b"",
    "message-dict": {"code": "rest_x", "message": {"x": "evil"}},
}


@pytest.fixture
def own_client(fake_wp):
    """Client có địa chỉ riêng (``SITE``), khác chữ mẫu cố định «https://example.com» trong câu
    hướng dẫn: câu nào chép địa chỉ là thấy ngay."""
    return WordPressClient(SITE, "lam", PASSWORD, session=make_session(fake_wp))


def assert_fixed_message(message, status):
    assert f"(mã {status})" in message
    for piece in ("evil", "Qz9x", "suachua-thu", "wp-admin", "0912", "<", "\n"):
        assert piece not in message, piece
    assert len(message) < 400


STATUSES = [400, 401, 402, 403, 404, 405, 409, 410, 413, 415, 418, 422, 429, 451, 500, 501, 502,
            503, 504, 520]


@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("name", TOXIC_BODIES)
def test_than_tra_ve_doc_khong_len_cau_loi(fake_wp, own_client, status, name):
    """Gồm cả hai nhánh 404 (thân rỗng hay sai kiểu: «không tìm thấy REST API»; còn lại: «không
    tìm thấy dữ liệu»)."""
    fake_wp.on("GET", "/wp-json/", (status, TOXIC_BODIES[name], {"X-Note": "evil"}))
    with pytest.raises(WordPressError) as err:
        own_client.check_connection()
    assert_fixed_message(str(err.value), status)
    assert err.value.status_code == status
    assert re.fullmatch(r"[A-Za-z0-9_-]*", err.value.code)


@pytest.mark.parametrize("status", [300, 301, 302, 303, 307, 308])
def test_chuyen_huong_bao_ma_khong_chep_dia_chi(fake_wp, own_client, status):
    target = f"https://evil.example/wp-json/?u=lam&p={PASSWORD}"
    fake_wp.on("GET", "/wp-json/", (status, b"<a href='https://evil.example'>x</a>",
                                    {"Location": target}))
    with pytest.raises(WordPressError, match="chuyển hướng") as err:
        own_client.check_connection()
    assert_fixed_message(str(err.value), status)
    assert len(fake_wp.requests) == 1  # không đi theo


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.SSLError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.InvalidURL,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ProxyError,
        requests.exceptions.InvalidHeader,
    ],
)
def test_loi_mang_khong_chep_dia_chi_hay_mat_khau(fake_wp, own_client, error):
    leaked = f"HTTPSConnectionPool {SITE}/wp-json/?u=lam&p={PASSWORD} evil"
    fake_wp.on("GET", "/wp-json/", lambda _r: error(leaked))
    with pytest.raises(WordPressError) as err:
        own_client.check_connection()
    message = str(err.value)
    for piece in ("evil", "Qz9x", "HTTPSConnectionPool", "u=lam", "suachua-thu"):
        assert piece not in message, piece


@pytest.mark.parametrize("status", [400, 403, 500])
def test_lenh_ghi_de_anh_loi_bao_cau_co_dinh(fake_wp, own_client, status):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{SITE}/wp-content/a.jpg"}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", (status, TOXIC_BODIES["dia-chi"], {}))
    with pytest.raises(WordPressError) as err:
        own_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert [path(r) for r in fake_wp.requests] == [MEDIA, f"{MEDIA}/9"]
    assert_fixed_message(str(err.value), status)


@pytest.mark.parametrize(
    "url",
    [
        "htps://lam:Qz9xWv8u@suachua-thu.vn",
        "suachua-thu.vn/?p=Qz9x",
        "ftp://lam:Qz9x@suachua-thu.vn",
        "javascript:alert('suachua-thu')",
        "[bấm](https://suachua-thu.vn)",
    ],
)
def test_wordpress_url_sai_dang_khong_chep_lai(url):
    with pytest.raises(WordPressError) as err:
        WordPressClient(url, "lam", PASSWORD)
    for piece in ("suachua-thu", "Qz9x", "lam:", "javascript", "bấm"):
        assert piece not in str(err.value), piece


# ================================================================ LC-T042-5: file chạy được


@pytest.mark.parametrize(
    "tail",
    [
        "/index.php/",
        "/index.php/wp",
        "/INDEX.PHP",
        "/blog/index.php",
        "/x.php.",
        "/x.",
        "/x%2Ephp",
        "/x.php%20",
        "/x;.php",
        "/x.php;a",
        "/x.php::$DATA",
        "/x．php",
        "/x.cfm",
        "/WEB-INF/x.jspx",
        "/.htaccess",
        "/blog?rest_route=/",
        "?rest_route=/wp/v2/posts",
    ],
)
def test_wordpress_url_tro_file_hay_doi_duong_bi_tu_choi(tail):
    with pytest.raises(WordPressError) as err:
        WordPressClient("https://suachua-thu.vn" + tail, "lam", PASSWORD)
    assert "suachua-thu" not in str(err.value)


@pytest.mark.parametrize(
    "url",
    [
        "https://suachuacuasat.com",
        "https://www.suachuacuasat.com/",
        "https://suachua-thu.vn:8443/blog",
        "https://suachua-thu.vn/cgi-bin",
        "https://suachua-thu.vn/index",
        "https://suachua-thu.vn/php",
    ],
)
def test_wordpress_url_thuong_khong_bi_chan_oan(url):
    assert WordPressClient(url, "lam", PASSWORD).base_url == url.rstrip("/")


# ================================================================ LC-T061-2: «<» trong chữ SEO

C_SPACE = " \t\n\r\v\f"  # ``isspace`` của C (PHP), KHÔNG phải ``str.isspace`` của Python
REGISTERED = ("code_snippet", "embed", "gallery", "caption", "audio", "video")


def php_strip_tags(text):
    """``strip_tags`` của PHP 8 (``php_strip_tags_ex``, không có thẻ cho phép), đủ cho chữ một
    dòng: «<» mà ký tự sau là khoảng trắng của C thì giữ; còn lại mở thẻ (cả «<!», «<?», «<» cuối
    chữ) tới «>» (đếm «<» lồng, bỏ qua «>» trong nháy); ký tự NUL bị bỏ."""
    out, depth, quote, in_tag = [], 0, "", False
    for i, ch in enumerate(text):
        nxt = text[i + 1 : i + 2]
        opens = ch == "<" and not (nxt and nxt in C_SPACE)
        if ch == "\0":
            continue
        if in_tag:
            if quote:
                quote = "" if ch == quote else quote
            elif ch in "\"'":
                quote = ch
            elif opens:
                depth += 1
            elif ch == ">":
                depth, in_tag = (depth - 1, True) if depth else (0, False)
        elif opens:
            in_tag = True
        else:
            out.append(ch)
    return "".join(out)


def wp_sanitize_text_field(text):
    """``_sanitize_text_fields`` của WordPress: ``wp_pre_kses_less_than`` («<…» không có «>»
    thành mã ký tự), ``strip_tags``, gộp khoảng trắng, bỏ dạng «%xx»."""
    if "<" in text:
        text = re.sub(
            r"<[^>]*?((?=<)|>|$)",
            lambda m: m.group(0) if ">" in m.group(0) else html.escape(m.group(0)),
            text,
        )
        text = php_strip_tags(text).replace("<\n", "&lt;\n")
    text = re.sub(r"[\r\n\t ]+", " ", text).strip()
    found = False
    while match := re.search(r"%[a-fA-F0-9]{2}", text):
        text, found = text.replace(match.group(0), ""), True
    return re.sub(" +", " ", text).strip() if found else text


def wp_runs_shortcode(content):
    """``get_shortcode_regex`` với vài tên đã đăng ký; dạng thoát ``[[tên]]`` không chạy."""
    pattern = re.compile(
        r"\[(\[?)(" + "|".join(REGISTERED) + r")(?![\w-])"
        r"([^\]/]*(?:/(?!\])[^\]/]*)*?)"
        r"(?:(/)\]|\](?:([^\[]*(?:\[(?!/\2\])[^\[]*)*)\[/\2\])?)(\]?)"
    )
    return any(not (m.group(1) == "[" and m.group(6) == "]") for m in pattern.finditer(content))


def test_ban_python_cua_sanitize_text_field_dung_cho_ca_da_biet():
    assert wp_sanitize_text_field("[<>code_snippet id=1]") == "[code_snippet id=1]"
    assert wp_runs_shortcode(wp_sanitize_text_field("[<1>code_snippet id=1]"))
    assert wp_sanitize_text_field("Giá < 500k") == "Giá &lt; 500k"
    assert wp_sanitize_text_field("Cửa < sắt") == "Cửa &lt; sắt"  # không có «>»
    # U+00A0 không phải khoảng trắng của C: «<» mở thẻ, cả cụm «< sắt>» bị bỏ.
    assert wp_sanitize_text_field("Cửa < sắt> đẹp") == "Cửa đẹp"
    assert not wp_runs_shortcode("[[code_snippet]]")


@pytest.mark.parametrize(
    "char",
    [
        " ",  # ngắt dòng Unicode
        " ",
        " ",  # cách hẹp không ngắt
        " ",
        " ",
        "᠎",  # Cf: bị gỡ ở chữ đã chuẩn hóa, còn ở chữ gốc
        "﻿",
        "̸",  # dấu kết hợp: «<» + U+0338 thành «≮» khi NFC
        "ㅤ",  # ký tự trắng Hangul (mặc định bỏ qua)
        "\x1c",  # Python coi là khoảng trắng, C thì không
        "😀",
        "'",
        "!",
        "?",
    ],
)
@pytest.mark.parametrize("template", ["[<{c}>code_snippet id=1]", "Giá <{c}500k", "Cửa <{c}"])
def test_dau_nho_hon_lien_ky_tu_unicode_la_bi_chan(char, template):
    with pytest.raises(WordPressError):
        _seo_text("Tiêu đề SEO", template.format(c=char), 300)


PIECES = [
    "[", "]", "[[", "]]", "[/", "<", ">", "< ", "<>", "<1>", "＜", "＞", "﹤", "［", "］",
    "code_snippet", "embed", " id=1", " ", " ", "　", "​", "%41", "%2", "1",
    "&", "=", "/", "'", '"', "x", "đ", "!", "?", "-", "\t",
]


def test_chu_seo_qua_bo_kiem_khong_thanh_shortcode_tren_website():
    """Thử ngẫu nhiên (hạt giống cố định): chữ nào qua ``_seo_text`` thì mọi «<» còn lại đều có
    khoảng trắng của C ngay sau (``strip_tags`` không mở thẻ), và sau ``sanitize_text_field``
    không có shortcode nào chạy được."""
    rng = random.Random(6060)
    passed = 0
    for _ in range(6000):
        text = "".join(rng.choice(PIECES) for _ in range(rng.randint(1, 9)))
        try:
            value = _seo_text("Tiêu đề SEO", text, 1000)
        except WordPressError:
            continue
        passed += 1
        assert not re.search(r"<(?![ \t\n\r\v\f])", value), repr(text)
        assert not wp_runs_shortcode(wp_sanitize_text_field(value)), repr(text)
    assert passed > 1000  # đủ ca qua để phép thử có nghĩa


@pytest.mark.parametrize(
    "text",
    [
        "Cửa sắt < 2 triệu, bền 10 năm",
        "Sơn tĩnh điện > sơn dầu?",
        "So sánh cửa sắt & cửa nhôm",
        "Cửa cuốn 24/7, gọi là có",
        "Top 5 mẫu cổng (2026) | Pro-Metal",
        "Cổng inox 100% thép, giá từ 1,2 triệu/m²",
    ],
)
def test_chu_seo_thuong_khong_bi_chan_oan(text):
    assert _seo_text("Tiêu đề SEO", text, 300) == text


# ================================================================ LC-T061-3, LC-T071-1: ảnh


@pytest.mark.parametrize(
    "answer",
    [
        (200, {"id": 9, "source_url": f"{UPLOADS}cong.jpg"}, {}),
        (202, {"id": 9, "source_url": f"{UPLOADS}cong.jpg"}, {}),
        (204, b"", {}),
    ],
)
def test_upload_media_ma_khac_201_khong_ghi_de_gi(fake_wp, wp_client, answer):
    fake_wp.on("POST", MEDIA, answer)
    fake_wp.on("POST", f"{MEDIA}/9", {"id": 9})
    with pytest.raises(WordPressError, match="201"):
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert [path(r) for r in fake_wp.requests] == [MEDIA]


@pytest.mark.parametrize(
    "created",
    [
        {"source_url": f"{UPLOADS}cong.jpg"},
        {"id": "9"},
        {"id": True},
        {"id": 0},
        {"id": -9},
        {"id": 9.0},
        [{"id": 9}],
        b"<html>ok</html>",
    ],
)
def test_upload_media_201_ma_anh_sai_khong_ghi_de_gi(fake_wp, wp_client, created):
    fake_wp.on("POST", MEDIA, (201, created, {}))
    for media_id in (0, 1, 9):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", {"id": media_id})
    with pytest.raises(WordPressError):
        wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    assert [path(r) for r in fake_wp.requests] == [MEDIA]


@pytest.mark.parametrize(
    ("kwargs", "sent"),
    [
        ({}, {"alt_text": "", "title": "anh-cong-sat", "caption": ""}),
        ({"alt_text": "", "title": "", "caption": ""},
         {"alt_text": "", "title": "anh-cong-sat", "caption": ""}),
        ({"alt_text": None, "caption": None},
         {"alt_text": "", "title": "anh-cong-sat", "caption": ""}),
        ({"alt_text": "[code_snippet id=1]", "caption": "[[gallery]]"},
         {"alt_text": "&#91;code_snippet id=1&#93;", "title": "anh-cong-sat",
          "caption": "&#91;&#91;gallery&#93;&#93;"}),
    ],
)
def test_upload_media_lenh_ghi_de_luon_du_ba_o(fake_wp, wp_client, kwargs, sent):
    """LC-T061-3 (kiểm độc lập): ô trống hay ``None`` vẫn gửi chuỗi rỗng, tiêu đề trống lấy tên
    file đã làm sạch, để WordPress không lấy ba ô từ chữ nằm trong file ảnh."""
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{UPLOADS}cong.jpg"}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", lambda r: {"id": 9, "source_url": f"{UPLOADS}cong.jpg",
                                                **body(r)})
    wp_client.upload_media(PHOTO, "Ảnh Cổng Sắt.jpg", **kwargs)
    _upload, update = fake_wp.requests
    assert body(update) == sent
    assert query(update) == {"_fields": ["id,source_url,alt_text"]}


@pytest.mark.parametrize("field", ["alt_text", "title", "caption"])
@pytest.mark.parametrize("value", [1.5, True, ("x",), bytearray(b"[code_snippet id=1]")])
def test_upload_media_o_sai_kieu_khong_tai_gi(fake_wp, wp_client, field, value):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{UPLOADS}cong.jpg"}, {}))
    with pytest.raises(WordPressError):
        wp_client.upload_media(PHOTO, "cong.jpg", **{field: value})
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 77, "source_url": f"{UPLOADS}anh-khac.jpg", "alt_text": "Ảnh khác"},
        {"source_url": "https://evil.example/anh.jpg", "alt_text": "Ảnh lạ"},
    ],
)
def test_sl_t060_1_upload_media_khong_nhan_tra_loi_cua_anh_khac(fake_wp, wp_client, answer):
    """Nhánh gửi nháp kèm ảnh (``_describe_draft_media``) báo lỗi khi câu trả lời lệnh ghi alt
    không đúng mã ảnh vừa tạo; ``upload_media`` (trang Kết nối WordPress) thì nhận luôn: trang hiện
    «Ảnh đại diện đã tải lên: <địa chỉ ảnh khác>», và không biết ba ô của ảnh 9 đã được ghi đè
    chưa (LC-T061-3)."""
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{UPLOADS}cong.jpg"}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", answer)
    try:
        media = wp_client.upload_media(PHOTO, "cong.jpg", alt_text="Cổng")
    except WordPressError:
        return  # báo lỗi là một cách sửa đúng
    assert media.id == 9
    assert media.source_url == f"{UPLOADS}cong.jpg"
    assert media.alt_text == "Cổng"


# ================================================================ không chặn oan


@pytest.fixture
def real_site(fake_wp):
    """Site giả trả lời như WordPress thật cho mọi lệnh app gửi (mã ảnh tăng dần từ 101)."""
    counter = iter(range(101, 200))
    term = [{"id": 1, "name": "Cổng", "slug": "cong", "count": 1, "parent": 0}]
    item = {"id": 7, "link": f"{BASE_URL}/bai-7/", "title": {"rendered": "Bài 7"},
            "slug": "bai-7", "status": "publish", "modified_gmt": "2026-10-01T00:00:00"}

    def created_media(_request):
        media_id = next(counter)
        return (201, {"id": media_id, "source_url": f"{UPLOADS}a{media_id}.webp", "post": None}, {})

    def updated_media(request):
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": f"{UPLOADS}a{media_id}.webp", **body(request)}

    def post(request):
        return {"id": 42, "status": "draft", "title": {"raw": "A", "rendered": "A"},
                "link": f"{BASE_URL}/?p=42", **(body(request) or {})}

    fake_wp.on("GET", "/wp-json/", {"name": "Site", "home": BASE_URL,
                                    "namespaces": ["wp/v2", "wp-abilities/v1"]})
    fake_wp.on("GET", "/wp-json/wp/v2/users/me",
               {"id": 3, "name": "BTV", "roles": ["editor"], "capabilities": {"edit_posts": True}})
    for kind in ("categories", "tags"):
        fake_wp.on("GET", f"/wp-json/wp/v2/{kind}", (200, term, {"X-WP-TotalPages": "1"}))
    for kind in ("posts", "pages"):
        fake_wp.on("GET", f"/wp-json/wp/v2/{kind}", (200, [item], {"X-WP-TotalPages": "1"}))
    fake_wp.on("POST", POSTS, lambda r: (201, post(r), {}))
    fake_wp.on("GET", f"{POSTS}/42", {"id": 42, "status": "draft", "meta": {
        "_siteseo_titles_title": "", "_siteseo_titles_desc": ""}})
    fake_wp.on("POST", f"{POSTS}/42", post)
    fake_wp.on("POST", MEDIA, created_media)
    for media_id in range(101, 110):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", updated_media)
    fake_wp.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake_wp.on("POST", f"{ABILITY}/run", siteseo_seo_answer)  # khuôn thật (T-059)
    return fake_wp


def _jpeg():
    buffer = io.BytesIO()
    Image.new("RGB", (64, 48), (120, 80, 40)).save(buffer, "JPEG")
    return buffer.getvalue()


LIST_KEYS = ["_fields", "hide_empty", "order", "orderby", "page", "per_page"]
PUBLISHED_KEYS = ["_fields", "order", "orderby", "page", "per_page", "status"]
REAL_CALLS = {
    "check_connection": (
        lambda c: c.check_connection(),
        [("GET", "/wp-json/", []), ("GET", ABILITY, []),
         ("GET", "/wp-json/wp/v2/users/me", ["context"])],
    ),
    "list_categories": (
        lambda c: c.list_categories(), [("GET", "/wp-json/wp/v2/categories", LIST_KEYS)]
    ),
    "list_tags": (lambda c: c.list_tags(), [("GET", "/wp-json/wp/v2/tags", LIST_KEYS)]),
    "list_published": (
        lambda c: c.list_published(),
        [("GET", POSTS, PUBLISHED_KEYS), ("GET", "/wp-json/wp/v2/pages", PUBLISHED_KEYS)],
    ),
    "create_draft": (
        lambda c: c.create_draft("Tiêu đề", "<p>Nội dung</p>", categories=[1], tags=[1],
                                 excerpt="Tóm tắt", slug="tieu-de"),
        [("POST", POSTS, ["_fields"])],
    ),
    "upload_media": (
        lambda c: c.upload_media(_jpeg(), "Cổng sắt.jpg", alt_text="Cổng sắt sơn đen"),
        [("POST", MEDIA, ["_fields"]), ("POST", f"{MEDIA}/101", ["_fields"])],
    ),
    "set_featured_image": (
        lambda c: c.set_featured_image(42, 101),
        [("GET", f"{POSTS}/42", ["_fields", "context"]), ("POST", f"{POSTS}/42", ["_fields"])],
    ),
    "set_seo_meta": (
        lambda c: c.set_seo_meta(42, title="Sửa cửa sắt tại nhà", description="Mô tả ngắn",
                                 focus_keyword="sửa cửa sắt"),
        [("GET", ABILITY, []), ("GET", f"{POSTS}/42", ["_fields", "context"]),
         ("POST", f"{ABILITY}/run", [])],
    ),
    "create_draft_with_images": (
        lambda c: c.create_draft_with_images(
            "Bài có ảnh",
            ["<p>Mở bài</p>",
             DraftImage(make_web_image(_jpeg()), alt="Cổng sắt", caption="Sau khi sơn"),
             "<p>Kết</p>"],
        ),
        [("POST", MEDIA, ["_fields"]), ("POST", f"{MEDIA}/101", ["_fields"]),
         ("POST", POSTS, ["_fields"]),
         ("POST", f"{MEDIA}/101", ["_fields"]),  # T-110 (Chỉ Huy duyệt 30/10): gắn ảnh vào bài nháp
         ("GET", f"{POSTS}/42", ["_fields", "context"]),
         ("POST", f"{POSTS}/42", ["_fields"])],
    ),
}


@pytest.mark.parametrize("name", REAL_CALLS)
def test_moi_lenh_that_cua_app_van_di_ra(real_site, name):
    call, expected = REAL_CALLS[name]
    client = WordPressClient(
        BASE_URL, "lam", PASSWORD, session=make_session(real_site), write_seo=True
    )
    client._created_post_ids.add(42)
    call(client)
    sent = [(r.method, path(r), sorted(query(r))) for r in real_site.requests]
    assert sent == expected

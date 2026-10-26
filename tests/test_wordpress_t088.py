"""T-088: lỗi Thấp còn lại của client WordPress sau T-085 (Soi Lỗi, Lá Chắn T-085).

- SL-T085-1: ``_fields`` có NUL (và khoảng trắng kiểu ``trim()`` của PHP: " \\t\\n\\r\\0\\x0b") sát
  tên trường bị chặn như tên trường thường; NUL ở giữa tên (WordPress không cắt) thì không.
- SL-T085-2, LC-T085-1: mọi chỗ đọc JSON trả lời (``_json``, ``_error_from``) không để lọt
  ``RecursionError`` hay lỗi giải mã lạ; câu «thư viện Media» của ``upload_media`` hiện cả khi
  lỗi lạ.
- SL-T085-3: lệnh tải ảnh của ``upload_media`` lỗi mà không phải lời từ chối 4xx rõ ràng thì dặn
  ảnh có thể đã lên thư viện Media, kiểm Media → Thư viện trước khi tải lại.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật.
"""

import random
import re
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session

from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import (
    _MEDIA_FIELDS,
    _POST_FIELDS,
    _POST_META_FIELDS,
    _PUBLISHED_FIELDS,
)

PASSWORD = "abcd efgh ijkl mnop"
BLOCKED = "không có trong danh sách được phép"
MEDIA = "/wp-json/wp/v2/media"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
JPEG = b"\xff\xd8\xff\xe0anh-gia"
DEEP_JSON = b"[" * 60_000 + b"]" * 60_000  # JSON hợp lệ, lồng 60.000 tầng
SERVER_TEXT = "Gọi 0909 123 456 https://evil.example/x <b>quản trị</b>"
RENDERED = ("content", "excerpt", "description", "caption", "_embedded", "_links")


def query(request):
    return parse_qs(urlsplit(request.url).query, keep_blank_values=True)


def wordpress_renders(value: str) -> bool:
    """Bản Python của phía WordPress (độc lập với client): ``wp_parse_list`` tách bằng
    ``preg_split('/[\\s,]+/', …, PREG_SPLIT_NO_EMPTY)`` (PCRE không cờ ``u``: chỉ khoảng trắng
    ASCII " \\t\\n\\x0b\\x0c\\r"), rỗng thì trả MỌI trường; ``get_fields_for_response`` cắt hai đầu
    từng tên bằng ``trim()`` (" \\t\\n\\r\\0\\x0b"); trường được dựng khi tên đúng bằng tên trường
    hay bắt đầu bằng «tên.» (``rest_is_field_included``), so đúng chữ hoa thường."""
    parts = [p for p in re.split(r"[ \t\n\x0b\x0c\r,]+", value) if p]
    if not parts:
        return True
    names = [p.strip(" \t\n\r\0\x0b") for p in parts]
    return any(n == f or n.startswith(f + ".") for n in names for f in RENDERED)


# ================================================================ SL-T085-1: NUL trong _fields

FIELDS_ROUTES = [
    ("GET", "/wp/v2/posts/42", {"context": "edit"}),
    ("GET", "/wp/v2/posts", {"status": "publish"}),
    ("GET", "/wp/v2/categories", {}),
    ("POST", "/wp/v2/posts", {}),
    ("POST", "/wp/v2/media/9", {}),
]


def answer_everything(fake):
    for method, path, _extra in FIELDS_ROUTES:
        fake.on(method, "/wp-json" + path, {"id": 9, "status": "draft"})


@pytest.mark.parametrize(("method", "path", "extra"), FIELDS_ROUTES)
@pytest.mark.parametrize(
    "fields",
    [
        "\x00content",
        "content\x00",
        "\x00content\x00",
        "id,\x00content",
        "id,status,\x00content.rendered",
        "id \x00excerpt",
        "\x00\x00excerpt\x00\x00",
        "description\x00",
        "id,\x00caption.rendered",
        "\x00_embedded",
        "_links\x00",
        "\x00\x0bcontent",
        "\x0b\x00content\x00\x0b",
        "content\x00.rendered",  # WordPress không cắt NUL trước dấu chấm, chặn cho chắc
        "\x00",  # chỉ NUL: coi như rỗng
        "\x00,\x00",
        " \x00 , \x00 ",
    ],
)
def test_fields_co_nul_hay_khoang_trang_kieu_trim_sat_ten_truong_bi_chan(
    fake_wp, wp_client, method, path, extra, fields
):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError) as err:
        wp_client._request(method, path, params={**extra, "_fields": fields})
    assert fake_wp.requests == []
    assert BLOCKED in str(err.value)


@pytest.mark.parametrize(
    "fields",
    ["con\x00tent", "id,con\x00tent", "id,\x00", "\x00id,status", _POST_META_FIELDS + "\x00"],
)
def test_nul_khong_lam_thanh_truong_chay_shortcode_thi_van_gui(fake_wp, wp_client, fields):
    """NUL ở giữa tên (WordPress không cắt) hay sát tên trường thường: không chặn oan."""
    assert not wordpress_renders(fields)
    answer_everything(fake_wp)
    wp_client._request("GET", "/wp/v2/posts/42", params={"context": "edit", "_fields": fields})
    (request,) = fake_wp.requests
    assert query(request)["_fields"] == [fields]


TERM_FIELDS = "id,name,slug,count,parent"  # trường chuyên mục, thẻ (``_list_terms``)


@pytest.mark.parametrize(
    "fields", [_POST_FIELDS, _POST_META_FIELDS, _MEDIA_FIELDS, _PUBLISHED_FIELDS, TERM_FIELDS]
)
def test_hang_fields_cua_app_van_gui(fake_wp, wp_client, fields):
    answer_everything(fake_wp)
    wp_client._request("POST", "/wp/v2/posts", params={"_fields": fields})
    (request,) = fake_wp.requests
    assert query(request)["_fields"] == [fields]


def test_thu_ngau_nhien_co_nul_khong_lot_truong_chay_shortcode():
    """Hạt giống cố định, có NUL và mọi khoảng trắng ASCII: giá trị nào đi ra thì bản Python của
    WordPress ở trên không dựng trường chạy shortcode."""
    pieces = ["id", "content", "excerpt", "description", "caption", "_links", "_embedded",
              "title", "status", "rendered", ",", ".", " ", "\t", "\n", "\r", "\x0b", "\x0c",
              "\x00", "\x00", " ", "​", "%00", "C", "x"]
    rng = random.Random(8808)
    fake = FakeWordPress()
    fake.on("GET", "/wp-json/wp/v2/posts/42", {"id": 42})
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake))
    sent = 0
    for _ in range(5000):
        value = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 7)))
        fake.requests.clear()
        try:
            client._request("GET", "/wp/v2/posts/42", params={"context": "edit", "_fields": value})
        except WordPressError:
            continue
        sent += 1
        assert not wordpress_renders(query(fake.requests[0])["_fields"][0]), repr(value)
    assert sent > 500  # đủ ca đi ra để phép thử có nghĩa


# ================================================================ SL-T085-2, LC-T085-1: JSON lạ


@pytest.mark.parametrize("status", [200, 201])
def test_tra_loi_json_long_qua_sau_thanh_cau_co_dinh(fake_wp, wp_client, status):
    fake_wp.on("GET", "/wp-json/", (status, DEEP_JSON, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    message = str(err.value)
    assert "JSON" in message and f"(mã {status};" in message
    assert err.value.status_code is None  # như mọi lỗi đọc JSON trước đây


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 413, 429, 500, 502])
def test_tra_loi_loi_co_than_json_long_qua_sau_thanh_cau_co_dinh(fake_wp, wp_client, status):
    fake_wp.on("GET", "/wp-json/", (status, DEEP_JSON, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    assert f"(mã {status})" in str(err.value)
    assert err.value.status_code == status and err.value.code == ""


@pytest.mark.parametrize("error", [TypeError("lạ"), RuntimeError("lạ"), MemoryError()])
def test_loi_giai_ma_la_thanh_cau_co_dinh(fake_wp, wp_client, monkeypatch, error):
    """Lỗi giải mã không phải ``ValueError``/``RecursionError`` (thư viện, máy hết bộ nhớ…)."""

    def broken_json(self, **kwargs):
        raise error

    fake_wp.on("GET", "/wp-json/", {"name": "x", "namespaces": ["wp/v2"]})
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (400, {"code": "x"}, {}))
    monkeypatch.setattr(requests.Response, "json", broken_json)
    with pytest.raises(WordPressError, match=r"\(mã 200;"):
        wp_client.check_connection()
    with pytest.raises(WordPressError) as err:  # đường câu trả lời lỗi (_error_from)
        wp_client.create_draft("Bài", "<p>Nội dung</p>")
    assert str(err.value) == "WordPress báo lỗi (mã 400)."


def uploaded(fake, media_id=9):
    fake.on("POST", MEDIA, (201, {"id": media_id, "source_url": f"{UPLOADS}cong.jpg"}, {}))


def assert_in_media_library(message, media_id=9):
    assert "thư viện Media" in message and f"mã ảnh {media_id}" in message
    assert "Media → Thư viện" in message
    for piece in ("0909", "evil", "<b>", "example.com"):
        assert piece not in message, piece


@pytest.mark.parametrize(
    "answer",
    [(200, DEEP_JSON, {}), (500, DEEP_JSON, {}), (403, DEEP_JSON, {})],
    ids=["200", "500", "403"],
)
def test_ghi_de_tra_loi_long_qua_sau_van_bao_anh_da_o_thu_vien(fake_wp, wp_client, answer):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", answer)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert len(fake_wp.requests) == 2
    assert_in_media_library(str(err.value))


@pytest.mark.parametrize("error", [TypeError("evil"), KeyError("evil"), RuntimeError("evil")])
def test_ghi_de_loi_la_van_bao_anh_da_o_thu_vien(fake_wp, wp_client, error):
    """Lỗi lạ (không phải lỗi của ``requests``) ngay ở lệnh ghi đè: câu cố định, không vỡ."""

    def broken(_request):
        raise error

    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", broken)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert len(fake_wp.requests) == 2
    assert_in_media_library(str(err.value))


# ================================================================ SL-T085-3: lệnh tải ảnh lỗi

MAYBE = "Ảnh có thể đã lên thư viện Media"


@pytest.mark.parametrize(
    ("answer", "status"),
    [
        ((500, b"<h1>Fatal error: Allowed memory size exhausted</h1>", {}), 500),
        ((502, b"", {}), 502),
        ((503, {"code": "x", "message": SERVER_TEXT}, {}), 503),
        ((504, b"", {}), 504),
        ((302, b"", {"Location": "https://evil.example/"}), 302),
        (requests.exceptions.ReadTimeout("evil"), None),
        (requests.exceptions.ConnectionError("evil"), None),
        (requests.exceptions.SSLError("evil"), None),
        (requests.exceptions.ChunkedEncodingError("evil"), None),
        ((201, b"<html>evil</html>", {}), None),
        ((201, {"source_url": f"{UPLOADS}cong.jpg"}, {}), None),
        ((201, {"id": "9"}, {}), None),
        ((201, DEEP_JSON, {}), None),
        ((200, {"id": 9}, {}), None),
        ((202, {"id": 9}, {}), None),
    ],
)
def test_tai_anh_loi_khong_ro_rang_thi_dan_kiem_thu_vien(fake_wp, wp_client, answer, status):
    fake_wp.on("POST", MEDIA, answer)  # lỗi mạng: site giả ném lại đúng lỗi đó
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    message = str(err.value)
    assert MAYBE in message and "Media → Thư viện" in message and "trước khi tải lại" in message
    assert [urlsplit(r.url).path for r in fake_wp.requests] == [MEDIA]
    assert err.value.status_code == status
    for piece in ("0909", "evil", "<b>", "example.com", "Fatal"):
        assert piece not in message, piece


@pytest.mark.parametrize("status", [400, 401, 403, 404, 408, 413, 415, 429])
def test_tai_anh_bi_tu_choi_4xx_giu_cau_cu(fake_wp, wp_client, status):
    """Lời từ chối 4xx rõ ràng: ảnh chưa lên, câu báo không dọa «có thể đã lên»."""
    fake_wp.on("POST", MEDIA, (status, {"code": "rest_x", "message": SERVER_TEXT}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert "thư viện Media" not in str(err.value)
    assert f"(mã {status})" in str(err.value) and err.value.status_code == status
    assert len(fake_wp.requests) == 1


def test_tai_anh_loi_la_van_dan_kiem_thu_vien(fake_wp, wp_client):
    def broken(_request):
        raise TypeError("evil")

    fake_wp.on("POST", MEDIA, broken)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    message = str(err.value)
    assert MAYBE in message and "(TypeError)" in message and "evil" not in message


def test_tai_va_ghi_de_thanh_cong_khong_doi(fake_wp, wp_client):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", {"id": 9, "source_url": f"{UPLOADS}cong-1.jpg",
                                      "alt_text": "Cổng"})
    media = wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert (media.id, media.source_url, media.alt_text) == (9, f"{UPLOADS}cong-1.jpg", "Cổng")
    assert len(fake_wp.requests) == 2

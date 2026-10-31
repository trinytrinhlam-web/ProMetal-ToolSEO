"""Lá Chắn T-060: các lỗi Thấp còn lại của ``_request`` và ``upload_media`` sau T-060.

Mỗi test ``xfail(strict=True)`` là một lỗi trong ``docs/team/reports/T-060-la-chan.md``: sửa
xong thì test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.

- LC-T060-1: ``_request`` chưa kiểm khóa thân JSON. WordPress đọc tham số theo thứ tự JSON →
  form → truy vấn → đường (``WP_REST_Request::get_parameter_order``), nên khóa trùng tên tham
  số của đường trong thân JSON thắng giá trị trên đường: ``id`` (bài, ảnh: ``update_item`` dùng
  ``$request['id']``), ``name`` (Abilities ``/run``: ``$request['name']``). Lệnh đi đúng đường
  đã duyệt nhưng sửa bài, ảnh khác hay chạy ability khác. ``status`` khác ``draft`` cũng đi ra.
- LC-T060-2: giá trị ``_fields`` chỉ được kiểm kiểu, nên lệnh hỏi ``content`` (bài) hay
  ``description`` (ảnh) vẫn đi ra: WordPress dựng hai trường đó bằng ``the_content``, tức chạy
  shortcode ngay trong lệnh của app (Lá Chắn T-054, T-061).
- LC-T060-3: ``upload_media`` (trang Kết nối WordPress): ảnh đã lên (``201``) mà lệnh ghi đè
  alt, tiêu đề, chú thích hỏng thì câu báo chỉ theo mã HTTP, không nói ảnh đã nằm trong thư
  viện Media (với chữ WordPress lấy từ file: EXIF, IPTC, XMP, đường LC-T061-3).

Hôm nay chưa có đường tới LC-T060-1, -2: mọi khóa JSON và giá trị ``_fields`` là hằng do code
viết. Ca đối chứng (đang qua): việc thật của app vẫn gửi đúng, để cách sửa không chặn nhầm.
Chỉ dùng site giả (``FakeWordPress``), không gọi mạng.
"""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL

from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import (
    _MEDIA_FIELDS,
    _MEDIA_UPLOAD_FIELDS,
    _POST_FIELDS,
    _POST_META_FIELDS,
    SITESEO_ABILITY,
    SITESEO_ABILITY_PATH,
    SITESEO_ABILITY_RUN_PATH,
)

MEDIA = "/wp-json/wp/v2/media"
SOURCE_URL = f"{BASE_URL}/wp-content/uploads/2026/10/cong-inox.jpg"
NEW_ID = 101
JPEG = b"\xff\xd8\xff\xe0anh-gia"


def _draft(post_id: int, featured: int = 0) -> dict:
    return {
        "id": post_id,
        "status": "draft",
        "title": {"raw": "Bài"},
        "link": f"{BASE_URL}/?p={post_id}",
        "featured_media": featured,
    }


# ================================================================ LC-T060-1: khóa thân JSON


@pytest.mark.parametrize(
    ("path", "payload", "params"),
    [
        pytest.param(
            "/wp/v2/media/9",
            {"id": 7, "alt_text": "Alt"},
            {"_fields": _MEDIA_FIELDS},
            id="anh-9-thanh-anh-7",
        ),
        pytest.param(
            "/wp/v2/posts/42",
            {"id": 5, "featured_media": 9},
            {"_fields": _POST_FIELDS},
            id="bai-42-thanh-bai-5",
        ),
        pytest.param(
            SITESEO_ABILITY_RUN_PATH,
            {"name": "core/ability-khac", "input": {"postId": 42}},
            None,
            id="ability-khac",
        ),
    ],
)
def test_lc_t060_1_khoa_than_json_doi_doi_tuong_bi_chan_truoc_khi_gui(
    fake_wp, wp_client, path, payload, params
):
    fake_wp.on("POST", f"/wp-json{path}", {"id": 1, "status": "draft"})
    options = {"params": params} if params else {}
    with pytest.raises(WordPressError):
        wp_client._request("POST", path, json=payload, **options)
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        pytest.param("/wp/v2/posts", {"title": "Bài", "status": "publish"}, id="tao-publish"),
        pytest.param(
            "/wp/v2/posts",
            {"title": "Bài", "status": "future", "date": "2026-12-01T08:00:00"},
            id="tao-future",
        ),
        pytest.param(
            "/wp/v2/posts/42", {"featured_media": 9, "status": "publish"}, id="nhap-thanh-publish"
        ),
    ],
)
def test_lc_t060_1_status_khac_nhap_bi_chan_truoc_khi_gui(fake_wp, wp_client, path, payload):
    fake_wp.on("POST", f"/wp-json{path}", (201, _draft(42), {}))
    with pytest.raises(WordPressError):
        wp_client._request("POST", path, json=payload, params={"_fields": _POST_FIELDS})
    assert fake_wp.requests == []


# ================================================================ LC-T060-2: giá trị _fields


@pytest.mark.parametrize(
    ("method", "path", "params", "payload"),
    [
        pytest.param(
            "GET",
            "/wp/v2/posts/42",
            {"context": "edit", "_fields": "id,status,content"},
            None,
            id="hoi-content-bai",
        ),
        pytest.param(
            "POST",
            "/wp/v2/posts",
            {"_fields": "id,status,content"},
            {"title": "Bài", "status": "draft"},
            id="tao-nhap-hoi-content",
        ),
        pytest.param(
            "POST",
            "/wp/v2/media/9",
            {"_fields": "id,source_url,description"},
            {"alt_text": "Alt"},
            id="anh-hoi-description",
        ),
    ],
)
def test_lc_t060_2_fields_hoi_truong_chay_shortcode_bi_chan(
    fake_wp, wp_client, method, path, params, payload
):
    fake_wp.on(method, f"/wp-json{path}", _draft(42))
    options = {"json": payload} if payload else {}
    with pytest.raises(WordPressError):
        wp_client._request(method, path, params=params, **options)
    assert fake_wp.requests == []


# ================================================================ đối chứng LC-T060-1, -2


def test_lc_t060_doi_chung_than_json_va_fields_that_cua_app_van_gui(fake_wp, wp_client):
    """Cách sửa LC-T060-1, -2 không được chặn việc thật: tạo nháp, ảnh đại diện, tải ảnh và ghi
    đè ba ô, ghi SEO qua Abilities. Thân JSON và ``_fields`` đi ra đúng như hôm nay."""
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (201, _draft(42), {}))
    fake_wp.on("GET", "/wp-json/wp/v2/posts/42", _draft(42))
    fake_wp.on("POST", "/wp-json/wp/v2/posts/42", _draft(42, NEW_ID))
    fake_wp.on("POST", MEDIA, (201, {"id": NEW_ID, "source_url": SOURCE_URL, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{NEW_ID}", {"id": NEW_ID, "source_url": SOURCE_URL})
    fake_wp.on("GET", f"/wp-json{SITESEO_ABILITY_PATH}", {"name": SITESEO_ABILITY})
    fake_wp.on(
        "POST",
        f"/wp-json{SITESEO_ABILITY_RUN_PATH}",
        lambda r: {"updated": True, "post": json.loads(r.body)["input"]},
    )
    wp_client.write_seo = True

    wp_client.create_draft(
        "Bài", "<p>Nội dung</p>", categories=[3], tags=[4], excerpt="<p>Tóm tắt</p>", slug="bai"
    )
    media = wp_client.upload_media(JPEG, "cong-inox.jpg", alt_text="Cổng inox")
    wp_client.set_featured_image(42, media.id)
    result = wp_client.set_seo_meta(42, title="Sửa cửa sắt", description="Thợ tới trong 2 giờ")

    assert result.written
    assert [_summary(r) for r in fake_wp.requests] == [
        ("POST", "/wp/v2/posts", _CREATE_KEYS, [_POST_FIELDS]),
        # T-110 lượt 2 (Chỉ Huy duyệt 30/10 20:25): lệnh tải ảnh xin thêm ``post``.
        ("POST", "/wp/v2/media", None, [_MEDIA_UPLOAD_FIELDS]),
        ("POST", f"/wp/v2/media/{NEW_ID}", ["alt_text", "caption", "title"], [_MEDIA_FIELDS]),
        ("GET", "/wp/v2/posts/42", None, [_POST_META_FIELDS]),
        ("POST", "/wp/v2/posts/42", ["featured_media"], [_POST_FIELDS]),
        ("GET", SITESEO_ABILITY_PATH, None, None),
        ("GET", "/wp/v2/posts/42", None, [_POST_META_FIELDS]),
        ("POST", SITESEO_ABILITY_RUN_PATH, ["input"], None),
    ]


_CREATE_KEYS = ["categories", "content", "excerpt", "slug", "status", "tags", "title"]


def _summary(request: requests.PreparedRequest) -> tuple:
    """(phương thức, đường sau /wp-json, khóa thân JSON nếu có, giá trị ``_fields``)."""
    parts = urlsplit(request.url)
    is_json = request.headers.get("Content-Type") == "application/json"
    return (
        request.method,
        parts.path.removeprefix("/wp-json"),
        sorted(json.loads(request.body)) if is_json else None,
        parse_qs(parts.query).get("_fields"),
    )


# ================================================================ LC-T060-3: ghi đè hỏng


@pytest.mark.parametrize(
    "answer",
    [
        pytest.param((500, {"code": "internal_server_error", "message": "x"}, {}), id="500"),
        pytest.param((403, {"code": "rest_cannot_edit", "message": "x"}, {}), id="403"),
        pytest.param(requests.exceptions.ReadTimeout("hết giờ"), id="het-gio"),
    ],
)
def test_lc_t060_3_ghi_de_hong_thi_bao_anh_da_o_thu_vien_media(fake_wp, wp_client, answer):
    """Câu báo phải nói ảnh đã ở «thư viện Media» (như các câu báo khác của client) để người
    dùng vào kiểm, xóa ảnh mang chữ lấy từ file; bấm gửi lại chỉ tải thêm một ảnh nữa."""
    fake_wp.on("POST", MEDIA, (201, {"id": NEW_ID, "source_url": SOURCE_URL, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{NEW_ID}", answer)
    with pytest.raises(WordPressError) as caught:
        wp_client.upload_media(JPEG, "cong-inox.jpg")
    assert len(fake_wp.requests) == 2  # ảnh đã lên, lệnh ghi đè đã gửi
    assert "thư viện Media" in str(caught.value)


def test_lc_t060_3_doi_chung_ghi_de_thanh_cong_khong_bao_loi(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": NEW_ID, "source_url": SOURCE_URL, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{NEW_ID}", {"id": NEW_ID, "source_url": SOURCE_URL})
    media = wp_client.upload_media(JPEG, "cong-inox.jpg")
    assert media.id == NEW_ID
    assert len(fake_wp.requests) == 2

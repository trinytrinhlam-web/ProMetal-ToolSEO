"""T-085: chốt chặn còn thiếu của ``_request`` sau T-060 (Lá Chắn T-060).

- LC-T060-1: khóa thân JSON cấp trên cùng theo danh sách của từng đường (``ALLOWED_JSON_KEYS``);
  không bao giờ ``id``, ``name`` (WordPress lấy giá trị trong thân JSON thay cho giá trị trên
  đường); ``status`` chỉ ``"draft"``.
- LC-T060-2: ``_fields`` không rỗng, không hỏi ``content``, ``excerpt``, ``description``,
  ``caption``, ``_embedded``, ``_links`` (WordPress dựng các trường đó bằng ``the_content``, tức
  chạy shortcode ngay trong lệnh của app).
- LC-T060-3, SL-T060-1: ``upload_media`` ảnh đã lên (201) mà lệnh ghi đè alt, tiêu đề, chú thích
  hỏng, hay câu trả lời không nói đúng mã ảnh vừa tạo, thì báo câu cố định: ảnh đang ở thư viện
  Media, mã ảnh, vào Media → Thư viện kiểm hoặc xóa.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật.
"""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, make_session

import seo_app.wordpress.client as client_module
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import (
    _MEDIA_FIELDS,
    _POST_FIELDS,
    _POST_META_FIELDS,
    _PUBLISHED_FIELDS,
    ALLOWED_JSON_KEYS,
    ALLOWED_ROUTES,
    MAX_ID,
    SITESEO_ABILITY_PATH,
    SITESEO_ABILITY_RUN_PATH,
)

PASSWORD = "abcd efgh ijkl mnop"
BLOCKED = "không có trong danh sách được phép"
POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
TERM_FIELDS = "id,name,slug,count,parent"  # trường chuyên mục, thẻ (``_list_terms``)


def body(request):
    return json.loads(request.body) if request.body else None


def answer_everything(fake):
    """Mọi đường được phép đều trả lời 200: lệnh nào lọt là thấy."""
    for method in ("GET", "POST"):
        for path in (
            "/wp-json/",
            "/wp-json/wp/v2/users/me",
            "/wp-json/wp/v2/categories",
            POSTS,
            POST_42,
            "/wp-json/wp/v2/media",
            "/wp-json/wp/v2/media/9",
            f"/wp-json{SITESEO_ABILITY_PATH}",
            f"/wp-json{SITESEO_ABILITY_RUN_PATH}",
        ):
            fake.on(method, path, {"id": 42, "status": "draft"})


# ================================================================ LC-T060-1: khóa thân JSON


def test_moi_duong_co_danh_sach_khoa_json_khong_co_id_name():
    assert set(ALLOWED_JSON_KEYS) == set(ALLOWED_ROUTES)
    for (method, _pattern), keys in ALLOWED_JSON_KEYS.items():
        assert not {key.lower() for key in keys} & {"id", "name"}
        if method == "GET":
            assert keys == frozenset()


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        # tạo nháp: khóa không thuộc create_draft (hẹn giờ, mật khẩu bài, tác giả, ghim…)
        ("/wp/v2/posts", {"title": "Bài", "date": "2026-12-01T08:00:00"}),
        ("/wp/v2/posts", {"title": "Bài", "date_gmt": "2026-12-01T01:00:00"}),
        ("/wp/v2/posts", {"title": "Bài", "password": "x"}),
        ("/wp/v2/posts", {"title": "Bài", "author": 1}),
        ("/wp/v2/posts", {"title": "Bài", "sticky": True}),
        ("/wp/v2/posts", {"title": "Bài", "template": "x"}),
        ("/wp/v2/posts", {"title": "Bài", "meta": {"_siteseo_titles_title": "x"}}),
        ("/wp/v2/posts", {"title": "Bài", "id": 5}),
        ("/wp/v2/posts", {"title": "Bài", "ID": 5}),
        ("/wp/v2/posts", {"title": "Bài", "Title": "x"}),
        ("/wp/v2/posts", {"title": "Bài", " status": "publish"}),
        # sửa bài nháp đã tạo: chỉ ảnh đại diện và meta SEO dự phòng
        ("/wp/v2/posts/42", {"featured_media": 9, "id": 5}),
        ("/wp/v2/posts/42", {"featured_media": 9, "Id": 5}),
        ("/wp/v2/posts/42", {"status": "draft"}),
        ("/wp/v2/posts/42", {"title": "Tên mới"}),
        ("/wp/v2/posts/42", {"content": "x"}),
        # ảnh vừa tải: chỉ alt, tiêu đề, chú thích
        ("/wp/v2/media/9", {"alt_text": "A", "id": 7}),
        ("/wp/v2/media/9", {"alt_text": "A", "post": 42}),
        ("/wp/v2/media/9", {"alt_text": "A", "status": "publish"}),
        ("/wp/v2/media/9", {"alt_text": "A", "description": "x"}),
        ("/wp/v2/media", {"title": "x"}),
        # Abilities: chỉ ``input``
        (SITESEO_ABILITY_RUN_PATH, {"name": "core/ability-khac", "input": {"postId": 42}}),
        (SITESEO_ABILITY_RUN_PATH, {"NAME": "core/ability-khac", "input": {"postId": 42}}),
        (SITESEO_ABILITY_RUN_PATH, {"input": {"postId": 42}, "id": 1}),
    ],
)
def test_khoa_json_ngoai_danh_sach_cua_duong_bi_chan_truoc_khi_gui(
    fake_wp, wp_client, path, payload
):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError) as err:
        wp_client._request("POST", path, json=payload)
    assert fake_wp.requests == []
    assert BLOCKED in str(err.value)


@pytest.mark.parametrize(
    "path", ["/", "/wp/v2/users/me", "/wp/v2/categories", "/wp/v2/posts", "/wp/v2/posts/42",
             SITESEO_ABILITY_PATH],
)
def test_lenh_doc_khong_nhan_khoa_json_nao(fake_wp, wp_client, path):
    """WordPress đọc thân JSON cả ở lệnh ``GET`` (khi loại thân là JSON): ``id`` đổi bài đọc."""
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request("GET", path, json={"id": 5})
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    "status",
    ["publish", "future", "private", "pending", "trash", "Draft", "DRAFT", "draft ", " draft", "",
     None, True, 0, ["draft"], {"draft": True}],
)
def test_status_khac_draft_bi_chan(fake_wp, wp_client, status):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request(
            "POST", "/wp/v2/posts", json={"title": "Bài", "status": status},
            params={"_fields": _POST_FIELDS},
        )
    assert fake_wp.requests == []


def test_status_draft_van_gui(fake_wp, wp_client):
    answer_everything(fake_wp)
    wp_client._request(
        "POST", "/wp/v2/posts", json={"title": "Bài", "status": "draft"},
        params={"_fields": _POST_FIELDS},
    )
    (request,) = fake_wp.requests
    assert body(request) == {"title": "Bài", "status": "draft"}


@pytest.mark.parametrize("key", ["id", "name", "ID", "Name", "iD"])
def test_id_name_van_bi_chan_khi_danh_sach_khoa_bi_noi(fake_wp, wp_client, monkeypatch, key):
    """Phòng khi ai đó nới ``ALLOWED_JSON_KEYS``: ``id``, ``name`` vẫn bị chặn."""
    loosened = tuple(
        (method, pattern, keys | {key}) for method, pattern, keys in client_module._ROUTE_JSON_KEYS
    )
    monkeypatch.setattr(client_module, "_ROUTE_JSON_KEYS", loosened)
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request("POST", "/wp/v2/media/9", json={"alt_text": "A", key: 7})
    wp_client._request("POST", "/wp/v2/media/9", json={"alt_text": "A"})  # đối chứng
    assert [urlsplit(r.url).path for r in fake_wp.requests] == ["/wp-json/wp/v2/media/9"]


def test_khoa_json_khong_phai_chu_bi_chan(fake_wp, wp_client):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request("POST", "/wp/v2/media/9", json={1: "x"})
    assert fake_wp.requests == []


def test_than_json_that_cua_app_van_gui_du(fake_wp):
    """Tạo nháp đủ mọi trường tùy chọn, ghi SEO qua meta dự phòng: thân JSON đi ra nguyên vẹn."""
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake_wp),
                             write_seo=True)
    draft = {"id": 42, "status": "draft", "title": {"raw": "Bài"}, "link": f"{BASE_URL}/?p=42"}
    meta = {"_siteseo_titles_title": "", "_siteseo_titles_desc": ""}
    fake_wp.on("POST", POSTS, (201, draft, {}))
    fake_wp.on("GET", POST_42, {**draft, "meta": meta})
    fake_wp.on("GET", f"/wp-json{SITESEO_ABILITY_PATH}", (404, {"code": "rest_no_route"}, {}))
    fake_wp.on("POST", POST_42, lambda r: {**draft, "meta": body(r)["meta"]})

    client.create_draft("Bài", "<p>Nội dung</p>", categories=[3], tags=[4], excerpt="<p>Tóm</p>",
                        slug="bai", featured_media=9)
    result = client.set_seo_meta(42, title="Sửa cửa sắt", description="Thợ tới trong 2 giờ")

    assert result.written and result.route == "meta"
    create = fake_wp.requests[0]
    assert sorted(body(create)) == ["categories", "content", "excerpt", "featured_media", "slug",
                                    "status", "tags", "title"]
    assert body(create)["status"] == "draft"
    write = fake_wp.requests[-1]
    assert (write.method, urlsplit(write.url).path) == ("POST", POST_42)
    assert list(body(write)) == ["meta"]


# ================================================================ LC-T060-2: giá trị _fields

ROUTES_WITH_FIELDS = [
    ("GET", "/wp/v2/posts/42", {"context": "edit"}),
    ("GET", "/wp/v2/posts", {"status": "publish"}),
    ("GET", "/wp/v2/categories", {}),
    ("POST", "/wp/v2/posts", {}),
    ("POST", "/wp/v2/posts/42", {}),
    ("POST", "/wp/v2/media", {}),
    ("POST", "/wp/v2/media/9", {}),
]


@pytest.mark.parametrize(("method", "path", "extra"), ROUTES_WITH_FIELDS)
@pytest.mark.parametrize(
    "fields",
    [
        "content",
        "id,content",
        "id, content",
        "id content",
        "id\tcontent",
        "id\ncontent",
        "id,,content",
        "content.rendered",
        "content.raw",
        "Content",
        "CONTENT.rendered",
        "excerpt",
        "id,excerpt.rendered",
        "description",
        "id,source_url,description",
        "caption",
        "caption.rendered",
        "_embedded",
        "_links",
        "_links.self",
        "",  # rỗng: WordPress trả MỌI trường, kể cả content
        ",",
        " ",
        " , ,",
    ],
)
def test_fields_hoi_truong_chay_shortcode_hay_rong_bi_chan(
    fake_wp, wp_client, method, path, extra, fields
):
    answer_everything(fake_wp)
    with pytest.raises(WordPressError) as err:
        wp_client._request(method, path, params={**extra, "_fields": fields})
    assert fake_wp.requests == []
    assert BLOCKED in str(err.value)
    assert "content" not in str(err.value).lower()


@pytest.mark.parametrize(
    ("method", "path", "fields"),
    [
        ("GET", "/wp/v2/posts/42", _POST_META_FIELDS),
        ("GET", "/wp/v2/posts", _PUBLISHED_FIELDS),
        ("GET", "/wp/v2/pages", _PUBLISHED_FIELDS),
        ("GET", "/wp/v2/categories", TERM_FIELDS),
        ("GET", "/wp/v2/tags", TERM_FIELDS),
        ("POST", "/wp/v2/posts", _POST_FIELDS),
        ("POST", "/wp/v2/posts/42", _POST_FIELDS),
        ("POST", "/wp/v2/posts/42", _POST_META_FIELDS),
        ("POST", "/wp/v2/media", _MEDIA_FIELDS),
        ("POST", "/wp/v2/media/9", _MEDIA_FIELDS),
        ("GET", "/wp/v2/posts/42", "id,meta._siteseo_titles_title"),
        ("GET", "/wp/v2/posts/42", "id, status"),
    ],
)
def test_fields_hang_cua_app_van_gui(fake_wp, wp_client, method, path, fields):
    for route in ("/wp/v2/posts/42", "/wp/v2/posts", "/wp/v2/pages", "/wp/v2/categories",
                  "/wp/v2/tags", "/wp/v2/media", "/wp/v2/media/9"):
        fake_wp.on(method, "/wp-json" + route, {"id": 9})
    wp_client._request(method, path, params={"_fields": fields})
    (request,) = fake_wp.requests
    assert parse_qs(urlsplit(request.url).query) == {"_fields": [fields]}


@pytest.mark.parametrize("key", ["_FIELDS", " _fields", "_fields[]", "_fields "])
def test_gia_tri_fields_van_bi_kiem_khi_danh_sach_tham_so_bi_noi(
    fake_wp, wp_client, monkeypatch, key
):
    """Phòng khi ai đó nới ``ALLOWED_PARAMS`` (PHP bỏ dấu cách đầu tên tham số, nên " _fields"
    vẫn là ``_fields``): khóa nào có chữ «fields» cũng bị kiểm giá trị."""
    loosened = tuple(
        (method, pattern, names | {key}) for method, pattern, names in client_module._ROUTE_PARAMS
    )
    monkeypatch.setattr(client_module, "_ROUTE_PARAMS", loosened)
    answer_everything(fake_wp)
    with pytest.raises(WordPressError, match=BLOCKED):
        wp_client._request("GET", "/", params={key: "content"})
    wp_client._request("GET", "/", params={key: "name"})  # đối chứng
    assert len(fake_wp.requests) == 1


# ================================================================ LC-T060-3, SL-T060-1: ảnh

MEDIA = "/wp-json/wp/v2/media"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
JPEG = b"\xff\xd8\xff\xe0anh-gia"
SERVER_TEXT = "Gọi 0909 123 456 https://evil.example/x <b>quản trị</b>"


def uploaded(fake, media_id=9):
    """Lệnh tải trả ``201`` với mã ảnh ``media_id``: từ đây ảnh đã ở thư viện Media."""
    fake.on("POST", MEDIA, (201, {"id": media_id, "source_url": f"{UPLOADS}cong.jpg"}, {}))


def assert_says_in_media_library(message, media_id=9):
    assert "thư viện Media" in message
    assert f"mã ảnh {media_id}" in message
    assert "Media → Thư viện" in message
    for piece in ("0909", "evil", "quản trị</b>", "example.com", "anh-khac"):
        assert piece not in message, piece


@pytest.mark.parametrize(
    ("answer", "status"),
    [
        ((400, {"code": "rest_invalid_param", "message": SERVER_TEXT}, {}), 400),
        ((401, {"code": "rest_not_logged_in", "message": SERVER_TEXT}, {}), 401),
        ((403, {"code": "rest_cannot_edit", "message": SERVER_TEXT}, {}), 403),
        ((404, {"code": "rest_post_invalid_id", "message": SERVER_TEXT}, {}), 404),
        ((413, {"code": "too_big", "message": SERVER_TEXT}, {}), 413),
        ((429, {"code": "too_many", "message": SERVER_TEXT}, {}), 429),
        ((500, {"code": "internal_server_error", "message": SERVER_TEXT}, {}), 500),
        ((502, SERVER_TEXT.encode(), {}), 502),
        ((302, b"", {"Location": "https://evil.example/"}), 302),
        ((200, b"<html>trang HTML</html>", {}), None),
        (requests.exceptions.ConnectionError("down"), None),
        (requests.exceptions.ReadTimeout("het gio"), None),
        (requests.exceptions.SSLError("bad cert"), None),
    ],
)
def test_ghi_de_hong_thi_bao_anh_da_o_thu_vien_media(fake_wp, wp_client, answer, status):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", answer)  # lỗi mạng: site giả ném lại đúng lỗi đó
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert [urlsplit(r.url).path for r in fake_wp.requests] == [MEDIA, f"{MEDIA}/9"]
    message = str(err.value)
    assert_says_in_media_library(message)
    assert err.value.status_code == status
    if status:
        assert f"(mã {status})" in message


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 77, "source_url": f"{UPLOADS}anh-khac.jpg", "alt_text": "Ảnh khác"},
        {"source_url": f"{UPLOADS}anh-khac.jpg", "alt_text": "Ảnh khác"},
        {"id": "9", "source_url": f"{UPLOADS}anh-khac.jpg"},
        {"id": 9.0, "source_url": f"{UPLOADS}anh-khac.jpg"},
        {"id": True, "source_url": f"{UPLOADS}anh-khac.jpg"},
        {"id": None},
        {},
        [{"id": 9}],
        "ok",
        None,
        9,
    ],
)
def test_tra_loi_ghi_de_khong_dung_anh_vua_tao_thi_bao_loi(fake_wp, wp_client, answer):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", answer)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert len(fake_wp.requests) == 2
    assert_says_in_media_library(str(err.value))


@pytest.mark.parametrize("media_id", [10**20, 2**63], ids=["10^20", "2^63"])
def test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien(
    fake_wp, wp_client, media_id
):
    """Mã ảnh quá ``MAX_ID`` (2⁶³−1): lệnh ghi đè không bao giờ được gửi, câu báo vẫn nói ảnh
    (có thể) đã ở thư viện Media, dặn kiểm Media → Thư viện (Ghi nhận 4 của Soi Lỗi T-060).
    T-091 (Chỉ Huy duyệt phương án A 28/10): mã quá lớn như mã sai khuôn nên câu báo là câu «có
    thể đã lên thư viện» (SL-T085-3), không còn ghi «mã ảnh {mã}» như trước."""
    uploaded(fake_wp, media_id=media_id)
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong.jpg")
    assert [urlsplit(r.url).path for r in fake_wp.requests] == [MEDIA]
    message = str(err.value)
    assert "có thể đã lên thư viện Media" in message and "Media → Thư viện" in message
    assert str(media_id) not in message
    # Như ``assert_says_in_media_library``: câu báo không chép lời máy chủ, địa chỉ website
    # (T-091 lượt 2, SL-T091-3: trả lại 5 kiểm phương án A không cho nới).
    for piece in ("0909", "evil", "quản trị</b>", "example.com", "anh-khac"):
        assert piece not in message, piece


def test_ma_anh_bang_gioi_han_van_ghi_de_binh_thuong(fake_wp, wp_client):
    """Biên T-091: mã ảnh đúng ``MAX_ID`` (2⁶³−1) vẫn hợp lệ, lệnh ghi đè gửi đúng ảnh đó."""
    uploaded(fake_wp, media_id=MAX_ID)
    fake_wp.on("POST", f"{MEDIA}/{MAX_ID}", lambda r: {"id": MAX_ID, **body(r)})
    media = wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert media.id == MAX_ID
    assert [urlsplit(r.url).path for r in fake_wp.requests] == [MEDIA, f"{MEDIA}/{MAX_ID}"]


def test_ghi_de_thanh_cong_lay_dia_chi_alt_cua_dung_anh(fake_wp, wp_client):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", lambda r: {"id": 9, "source_url": f"{UPLOADS}cong-1.jpg",
                                                "alt_text": body(r)["alt_text"]})
    media = wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert (media.id, media.source_url, media.alt_text) == (9, f"{UPLOADS}cong-1.jpg", "Cổng")


def test_tra_loi_dung_anh_nhung_truong_sai_kieu_khong_vo(fake_wp, wp_client):
    uploaded(fake_wp)
    fake_wp.on("POST", f"{MEDIA}/9", {"id": 9, "source_url": 123, "alt_text": ["x"]})
    media = wp_client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert (media.id, media.source_url, media.alt_text) == (9, "", "Cổng")

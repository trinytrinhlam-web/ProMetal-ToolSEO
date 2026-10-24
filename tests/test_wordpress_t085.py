"""T-085: chốt chặn còn thiếu của ``_request`` sau T-060 (Lá Chắn T-060).

- LC-T060-1: khóa thân JSON cấp trên cùng theo danh sách của từng đường (``ALLOWED_JSON_KEYS``);
  không bao giờ ``id``, ``name`` (WordPress lấy giá trị trong thân JSON thay cho giá trị trên
  đường); ``status`` chỉ ``"draft"``.
- LC-T060-2: ``_fields`` không rỗng, không hỏi ``content``, ``excerpt``, ``description``,
  ``caption``, ``_embedded``, ``_links`` (WordPress dựng các trường đó bằng ``the_content``, tức
  chạy shortcode ngay trong lệnh của app).

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật.
"""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
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

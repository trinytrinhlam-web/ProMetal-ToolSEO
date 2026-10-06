import base64
import json

import pytest
import requests
from fake_wordpress import BASE_URL, query

from seo_app.config import Settings
from seo_app.wordpress import WordPressClient, WordPressError

APP_PASSWORD = "abcd efgh ijkl"

ROOT = {
    "name": "Cửa Sắt &amp; Nhôm ProMetal",
    "home": BASE_URL,
    "namespaces": ["oembed/1.0", "wp/v2"],
}
ME = {
    "name": "Lâm",
    "roles": ["editor"],
    "capabilities": {"edit_posts": True, "publish_posts": True, "upload_files": True},
}


def body(request):
    return json.loads(request.body)


# ------------------------------------------------------------ khởi tạo


@pytest.mark.parametrize("url", ["", "example.com", "ftp://example.com", "https://"])
def test_rejects_invalid_url(url):
    with pytest.raises(WordPressError, match="không hợp lệ"):
        WordPressClient(url, "lam", APP_PASSWORD)


def test_from_settings_requires_all_fields():
    with pytest.raises(WordPressError, match="Chưa khai báo WordPress"):
        WordPressClient.from_settings(Settings(wordpress_url=BASE_URL, wordpress_username="lam"))


def test_from_settings_and_trailing_slash():
    client = WordPressClient.from_settings(
        Settings(
            wordpress_url=BASE_URL + "/",
            wordpress_username="lam",
            wordpress_app_password=APP_PASSWORD,
        )
    )
    assert client.base_url == BASE_URL
    assert client.uses_https


def test_password_never_in_repr(wp_client):
    assert "abcd" not in repr(wp_client)


def test_sends_basic_auth_without_spaces(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", ME)
    wp_client.check_connection()
    header = fake_wp.requests[-1].headers["Authorization"]
    assert base64.b64decode(header.removeprefix("Basic ")).decode() == "lam:abcdefghijkl"


# ------------------------------------------------------------ kết nối


def test_check_connection(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", ME)

    info = wp_client.check_connection()

    assert info.site_name == "Cửa Sắt & Nhôm ProMetal"
    assert info.user_name == "Lâm"
    assert info.roles == ("editor",)
    assert info.can_edit_posts and info.can_publish_posts and info.can_upload_files
    assert query(fake_wp.requests[-1])["context"] == ["edit"]


def test_check_connection_reports_missing_capabilities(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/users/me",
        {"name": "CTV", "roles": ["contributor"], "capabilities": {"edit_posts": True}},
    )
    info = wp_client.check_connection()
    assert info.can_edit_posts
    assert not info.can_upload_files
    assert not info.can_publish_posts


def test_site_without_wp_rest_api(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", {"name": "x", "namespaces": ["oembed/1.0"]})
    with pytest.raises(WordPressError, match="wp/v2"):
        wp_client.check_connection()


def test_wrong_application_password(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/users/me",
        (
            401,
            {
                "code": "incorrect_password",
                "message": "The provided password is an invalid application password.",
            },
            {},
        ),
    )
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    message = str(err.value)
    assert "WORDPRESS_APP_PASSWORD" in message
    assert "invalid application password" in message
    assert "abcd" not in message
    assert err.value.status_code == 401
    assert err.value.code == "incorrect_password"


def test_html_page_instead_of_json(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", (200, b"<html>Trang chu</html>", {}))
    with pytest.raises(WordPressError, match="JSON"):
        wp_client.check_connection()


def test_rest_api_not_found(wp_client):
    with pytest.raises(WordPressError, match="Không tìm thấy REST API"):
        wp_client.check_connection()


def test_forbidden(fake_wp, wp_client):
    fake_wp.on(
        "GET", "/wp-json/", (403, {"code": "rest_forbidden", "message": "<b>Bị chặn</b>"}, {})
    )
    with pytest.raises(WordPressError, match="không đủ quyền") as err:
        wp_client.check_connection()
    assert "<b>" not in str(err.value)
    assert "Bị chặn" in str(err.value)


def test_server_error(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/", (502, b"Bad gateway", {}))
    with pytest.raises(WordPressError, match="mã 502"):
        wp_client.check_connection()


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (requests.exceptions.SSLError("bad cert"), "SSL"),
        (requests.exceptions.ConnectTimeout("slow"), "quá lâu"),
        (requests.exceptions.ConnectionError("down"), "Không kết nối được"),
    ],
)
def test_network_errors(fake_wp, wp_client, exception, expected):
    fake_wp.on("GET", "/wp-json/", lambda _r: exception)
    with pytest.raises(WordPressError, match=expected):
        wp_client.check_connection()


# ------------------------------------------------------ chuyên mục, thẻ


def test_list_categories_reads_all_pages(fake_wp, wp_client):
    pages = {
        "1": [{"id": i, "name": f"Mục {i}", "slug": f"muc-{i}", "count": i} for i in range(100)],
        "2": [{"id": 100, "name": "Cửa &amp; cổng", "slug": "cua-cong", "count": 3, "parent": 5}],
    }

    def handler(request):
        page = query(request)["page"][0]
        return 200, pages[page], {"X-WP-Total": "101", "X-WP-TotalPages": "2"}

    fake_wp.on("GET", "/wp-json/wp/v2/categories", handler)

    categories = wp_client.list_categories()

    assert len(categories) == 101
    assert categories[-1].name == "Cửa & cổng"
    assert categories[-1].parent == 5
    params = query(fake_wp.requests[0])
    assert params["per_page"] == ["100"]
    assert params["hide_empty"] == ["false"]
    assert len(fake_wp.requests) == 2


def test_list_tags_single_page_without_header(fake_wp, wp_client):
    fake_wp.on(
        "GET", "/wp-json/wp/v2/tags", [{"id": 7, "name": "inox", "slug": "inox", "count": 0}]
    )
    tags = wp_client.list_tags()
    assert [t.slug for t in tags] == ["inox"]
    assert len(fake_wp.requests) == 1


# --------------------------------------------------------------- bài nháp


def created_post(request):
    data = body(request)
    return (
        201,
        {
            "id": 42,
            "status": data["status"],
            "title": {"raw": data["title"], "rendered": data["title"]},
            "link": f"{BASE_URL}/?p=42",
            "featured_media": data.get("featured_media", 0),
        },
        {},
    )


def test_create_draft(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/posts", created_post)

    post = wp_client.create_draft(
        "  Cửa sắt 2 cánh  ", "<p>Nội dung</p>", categories=[3], tags=(7, 8), featured_media=9
    )

    sent = body(fake_wp.requests[-1])
    assert sent == {
        "status": "draft",
        "title": "Cửa sắt 2 cánh",
        "content": "<p>Nội dung</p>",
        "categories": [3],
        "tags": [7, 8],
        "featured_media": 9,
    }
    assert post.id == 42
    assert post.status == "draft"
    assert post.featured_media == 9
    assert post.edit_link == f"{BASE_URL}/wp-admin/post.php?post=42&action=edit"


def test_create_draft_minimal_payload(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/posts", created_post)
    wp_client.create_draft("Tiêu đề", "")
    assert set(body(fake_wp.requests[-1])) == {"status", "title", "content"}


def test_create_draft_requires_title(fake_wp, wp_client):
    with pytest.raises(WordPressError, match="Tiêu đề"):
        wp_client.create_draft("   ", "abc")
    assert fake_wp.requests == []


def test_client_has_no_publish_function(wp_client):
    assert not any("publish" in name for name in dir(wp_client))


def test_set_featured_image(fake_wp, wp_client):
    fake_wp.on(
        "POST",
        "/wp-json/wp/v2/posts/42",
        {"id": 42, "status": "draft", "title": {"rendered": "A"}, "featured_media": 9},
    )
    post = wp_client.set_featured_image(42, 9)
    assert body(fake_wp.requests[-1]) == {"featured_media": 9}
    assert post.featured_media == 9


# ------------------------------------------------------------------- ảnh


def test_upload_media_with_alt(fake_wp, wp_client):
    fake_wp.on(
        "POST", "/wp-json/wp/v2/media", (201, {"id": 9, "source_url": "https://x/a.jpg"}, {})
    )
    fake_wp.on(
        "POST",
        "/wp-json/wp/v2/media/9",
        lambda r: {"id": 9, "source_url": "https://x/a.jpg", "alt_text": body(r)["alt_text"]},
    )

    media = wp_client.upload_media(b"JPEGDATA", "Ảnh Cửa Sắt.JPG", alt_text="Cửa sắt sơn đen")

    upload, update = fake_wp.requests
    assert upload.body == b"JPEGDATA"
    assert upload.headers["Content-Type"] == "image/jpeg"
    assert upload.headers["Content-Disposition"] == 'attachment; filename="anh-cua-sat.jpg"'
    assert body(update) == {"alt_text": "Cửa sắt sơn đen"}
    assert media.id == 9
    assert media.alt_text == "Cửa sắt sơn đen"


def test_upload_media_without_metadata_is_one_request(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, {"id": 5, "source_url": "u"}, {}))
    media = wp_client.upload_media(b"x", "!!!.webp")
    assert len(fake_wp.requests) == 1
    assert fake_wp.requests[0].headers["Content-Type"] == "image/webp"
    assert 'filename="anh.webp"' in fake_wp.requests[0].headers["Content-Disposition"]
    assert media.id == 5


def test_upload_media_file(tmp_path, fake_wp, wp_client):
    image = tmp_path / "cổng inox.png"
    image.write_bytes(b"PNGDATA")
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, {"id": 6, "source_url": "u"}, {}))
    wp_client.upload_media_file(image)
    assert fake_wp.requests[0].body == b"PNGDATA"
    assert 'filename="cong-inox.png"' in fake_wp.requests[0].headers["Content-Disposition"]


@pytest.mark.parametrize(("data", "name"), [(b"x", "baocao.pdf"), (b"x", "anh"), (b"", "a.jpg")])
def test_upload_media_rejects_bad_files(fake_wp, wp_client, data, name):
    with pytest.raises(WordPressError):
        wp_client.upload_media(data, name)
    assert fake_wp.requests == []


def test_upload_too_large(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/media", (413, b"Request Entity Too Large", {}))
    with pytest.raises(WordPressError, match="quá lớn"):
        wp_client.upload_media(b"x", "a.jpg")

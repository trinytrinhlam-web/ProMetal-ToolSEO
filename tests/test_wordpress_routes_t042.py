"""T-042: danh sách đường REST được gọi là CỐ ĐỊNH; đường khác bị từ chối trước khi gửi.

Điều kiện Lá Chắn T-037: so khớp toàn chuỗi cặp (phương thức, đường), chặn ``..``, ``%2e``,
``//``, ``/code-snippets/v1``, ``/prometal/v1``. Không gọi site thật: chỉ ``FakeWordPress``.
"""

import pytest

from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import ALLOWED_ROUTES, is_allowed_route

ABILITY = "/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"

# Mọi đường được phép (mỗi mẫu một ví dụ). Thêm đường mới thì test này đỏ: phải qua Lá Chắn.
ALLOWED_EXAMPLES = [
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
    ("GET", ABILITY),
    ("POST", ABILITY + "/run"),
]


def test_allowed_route_list_is_exactly_the_reviewed_one():
    assert [method for method, _ in ALLOWED_ROUTES] == [m for m, _ in ALLOWED_EXAMPLES]
    assert len(ALLOWED_ROUTES) == 13
    assert {method for method, _ in ALLOWED_ROUTES} == {"GET", "POST"}


@pytest.mark.parametrize(("method", "path"), ALLOWED_EXAMPLES)
def test_reviewed_routes_are_allowed(method, path):
    assert is_allowed_route(method, path)


FORBIDDEN_PATHS = [
    # namespace nhạy cảm của site
    "/code-snippets/v1/snippets",
    "/code-snippets/v1/snippets/1",
    "/prometal/v1/deploy-files",
    "/prometal/v1/purge",
    "/Code-Snippets/v1/snippets",
    "/PROMETAL/v1/purge",
    # đi ngược thư mục, mã hóa, gạch đôi
    "/wp/v2/../code-snippets/v1/snippets",
    "/wp/v2/posts/..",
    "/wp/v2/posts/%2e%2e",
    "/wp/v2/posts/%2E%2E/code-snippets",
    "/wp/v2/posts/1%2f..",
    "/wp/v2//posts",
    "//evil.com/wp/v2/posts",
    "/wp/v2/posts/1\\..",
    # tham số, mảnh, khoảng trắng, ký tự lạ trong đường
    "/wp/v2/posts?status=publish",
    "/wp/v2/posts/1?force=true",
    "/wp/v2/posts#x",
    "/wp/v2/posts/1 ",
    " /wp/v2/posts",
    "/wp/v2/posts/1\n",
    "/wp/v2/posts/1\x00",
    "/wp/v2/posts/١",  # chữ số Ả Rập
    "/wp/v2/posts/１",  # "1" toàn khổ
    # mã không hợp lệ
    "/wp/v2/posts/0",
    "/wp/v2/posts/01",
    "/wp/v2/posts/-1",
    "/wp/v2/posts/1.5",
    "/wp/v2/posts/" + "9" * 20,
    # đường con, đường khác của WordPress
    "/wp/v2/posts/1/",
    "/wp/v2/posts/",
    "/wp/v2/posts/1/revisions",
    "/wp/v2/posts/1/autosaves",
    "/wp/v2/pages/1",
    "/wp/v2/users",
    "/wp/v2/users/1",
    "/wp/v2/settings",
    "/wp/v2/plugins",
    "/wp/v2/themes",
    "/wp/v2/comments",
    "/wp/v2/media/9/edit",
    "/WP/V2/POSTS",
    "wp/v2/posts",
    "",
    # ability khác của SiteSEO / Abilities API
    "/wp-abilities/v1/abilities",
    "/wp-abilities/v1/abilities/siteseo-posts/seo-data-get/run",
    "/wp-abilities/v1/abilities/siteseo-settings/get-settings/run",
    ABILITY + "/run/",
    ABILITY + "/",
    ABILITY + "x/run",
]


@pytest.mark.parametrize("path", FORBIDDEN_PATHS)
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_other_paths_are_refused(method, path):
    assert not is_allowed_route(method, path)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("DELETE", "/wp/v2/posts/42"),
        ("PUT", "/wp/v2/posts/42"),
        ("PATCH", "/wp/v2/posts/42"),
        ("OPTIONS", "/"),
        ("HEAD", "/"),
        ("get", "/"),
        ("post", "/wp/v2/posts"),
        ("GET ", "/"),
        ("POST", "/"),
        ("POST", "/wp/v2/users/me"),
        ("POST", "/wp/v2/pages"),
        ("POST", "/wp/v2/categories"),
        ("GET", "/wp/v2/media"),
        ("GET", "/wp/v2/media/9"),
        ("POST", ABILITY),
        ("GET", ABILITY + "/run"),
        (None, "/"),
        ("GET", None),
        ("GET", b"/"),
        ("GET", 1),
    ],
)
def test_wrong_method_or_type_is_refused(method, path):
    assert not is_allowed_route(method, path)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/code-snippets/v1/snippets"),
        ("POST", "/prometal/v1/deploy-files"),
        ("POST", "/prometal/v1/purge"),
        ("DELETE", "/wp/v2/posts/42"),
        ("GET", "/wp/v2/../code-snippets/v1/snippets"),
        ("POST", "/wp/v2/posts/%2e%2e/1"),
        ("GET", "/wp-abilities/v1/abilities/siteseo-posts/seo-data-get/run"),
    ],
)
def test_client_refuses_before_any_request(fake_wp, wp_client, method, path):
    fake_wp.on(method, "/wp-json" + path, {"ok": True})
    with pytest.raises(WordPressError) as err:
        wp_client._request(method, path, json={"code": "<?php echo 1;"})
    assert fake_wp.requests == []
    message = str(err.value)
    assert "không có trong danh sách được phép" in message
    assert path not in message  # câu cố định, không chép đường


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirect_is_not_followed(fake_wp, wp_client, status):
    """Máy chủ chuyển hướng sang /code-snippets hay bài khác: không đi theo, báo lỗi."""
    target = "https://example.com/wp-json/code-snippets/v1/snippets"
    fake_wp.on("POST", "/wp-json/wp/v2/posts/42", (status, b"", {"Location": target}))
    fake_wp.on("POST", "/wp-json/code-snippets/v1/snippets", {"ok": True})
    fake_wp.on("GET", "/wp-json/code-snippets/v1/snippets", {"ok": True})
    with pytest.raises(WordPressError, match="chuyển hướng") as err:
        wp_client._request("POST", "/wp/v2/posts/42", json={"featured_media": 1})
    assert err.value.status_code == status
    assert len(fake_wp.requests) == 1
    assert "code-snippets" not in str(err.value)


def test_public_methods_only_use_allowed_routes(fake_wp, wp_client):
    """Đi qua mọi hàm công khai của client với site giả: mọi request đều nằm trong danh sách."""
    fake_wp.on("GET", "/wp-json/", {"name": "x", "home": "https://example.com",
                                    "namespaces": ["wp/v2"]})
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", {"name": "a", "roles": [], "capabilities": {}})
    fake_wp.on("GET", "/wp-json" + ABILITY, (404, {"code": "rest_no_route"}, {}))
    for path in ("categories", "tags", "posts", "pages"):
        fake_wp.on("GET", f"/wp-json/wp/v2/{path}", [])
    fake_wp.on("POST", "/wp-json/wp/v2/posts", {"id": 42, "status": "draft", "title": "A"})
    fake_wp.on("POST", "/wp-json/wp/v2/posts/42", {"id": 42, "status": "draft"})
    fake_wp.on("GET", "/wp-json/wp/v2/posts/42", {"id": 42, "status": "draft"})
    fake_wp.on(
        "POST", "/wp-json/wp/v2/media",
        (201, {"id": 9, "source_url": "u", "post": None}, {}),
    )
    fake_wp.on("POST", "/wp-json/wp/v2/media/9", {"id": 9, "source_url": "u"})

    wp_client.check_connection()
    wp_client.list_categories()
    wp_client.list_tags()
    wp_client.list_published()
    wp_client.create_draft("A", "B")
    wp_client.set_featured_image(42, 9)
    wp_client.upload_media(b"x", "a.png", alt_text="ảnh")

    assert fake_wp.requests
    for request in fake_wp.requests:
        path = request.path_url.split("?", 1)[0].removeprefix("/wp-json")
        assert is_allowed_route(request.method, path), (request.method, path)

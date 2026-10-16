"""T-037: ``WordPressClient.list_published()`` chỉ trả bài/trang đã đăng, link đúng tên miền."""

import pytest
from fake_wordpress import BASE_URL, make_session, query

from seo_app.wordpress import PublishedItem, WordPressClient, WordPressError, is_site_link
from seo_app.wordpress.client import MAX_META_CHARS, MAX_PAGES, MAX_TITLE_CHARS


def item(id_, *, status="publish", kind="post", link=None, title=None, meta=None, **extra):
    data = {
        "id": id_,
        "type": kind,
        "status": status,
        "slug": f"bai-{id_}",
        "link": link if link is not None else f"{BASE_URL}/bai-{id_}/",
        "title": {"rendered": title if title is not None else f"Bài {id_}"},
        "modified_gmt": "2026-10-01T03:04:05",
    }
    if meta is not None:
        data["meta"] = meta
    data.update(extra)
    return data


def serve(fake_wp, posts=(), pages=()):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", list(posts))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", list(pages))


def test_reads_posts_and_pages_with_meta(fake_wp, wp_client):
    meta = {
        "_siteseo_titles_title": "6 Dấu Hiệu Cần Thay Bánh Xe Cửa Kéo | Pro Metal",
        "_siteseo_titles_desc": "Bánh xe kêu &amp; kẹt? Đây là 6 dấu hiệu.",
        "_siteseo_social_fb_title": "bỏ qua",
    }
    serve(fake_wp, posts=[item(810, meta=meta)], pages=[item(2, kind="page")])

    result = wp_client.list_published()

    assert result == [
        PublishedItem(
            id=810,
            type="post",
            slug="bai-810",
            link=f"{BASE_URL}/bai-810/",
            title="Bài 810",
            meta_title="6 Dấu Hiệu Cần Thay Bánh Xe Cửa Kéo | Pro Metal",
            meta_desc="Bánh xe kêu & kẹt? Đây là 6 dấu hiệu.",
            modified_gmt="2026-10-01T03:04:05",
        ),
        PublishedItem(
            id=2,
            type="page",
            slug="bai-2",
            link=f"{BASE_URL}/bai-2/",
            title="Bài 2",
            modified_gmt="2026-10-01T03:04:05",
        ),
    ]


def test_only_get_on_fixed_paths_with_status_publish(fake_wp, wp_client):
    serve(fake_wp)
    wp_client.list_published()

    assert [r.method for r in fake_wp.requests] == ["GET", "GET"]
    paths = [r.path_url.split("?")[0] for r in fake_wp.requests]
    assert paths == ["/wp-json/wp/v2/posts", "/wp-json/wp/v2/pages"]
    for request in fake_wp.requests:
        params = query(request)
        assert params["status"] == ["publish"]
        assert params["per_page"] == ["100"]
        assert set(params["_fields"][0].split(",")) == {
            "id",
            "type",
            "status",
            "slug",
            "link",
            "title",
            "modified_gmt",
            "meta",
        }
        assert "context" not in params  # không xin context=edit (không cần quyền sửa)


def test_drops_future_draft_private_and_missing_status(fake_wp, wp_client):
    posts = [
        item(1),
        item(2, status="future"),
        item(3, status="draft"),
        item(4, status="private"),
        item(5, status="pending"),
        item(6, status="PUBLISH"),
        {k: v for k, v in item(7).items() if k != "status"},
    ]
    serve(fake_wp, posts=posts, pages=[item(8, kind="page", status="trash")])

    assert [i.id for i in wp_client.list_published()] == [1]


@pytest.mark.parametrize(
    "link",
    [
        "http://example.com/bai/",  # không mã hóa
        "https://evil.com/bai/",
        "https://example.com.evil.com/bai/",
        "https://sub.example.com/bai/",
        "https://evil.com/?u=https://example.com/",
        "https://example.com@evil.com/bai/",
        "https://user@example.com/bai/",
        "https://example.com:8443/bai/",
        "https://example.com:abc/bai/",
        "//example.com/bai/",
        "/bai/",
        "javascript:alert(1)",
        "https://example.com/bai cách/",
        "https://example.com/bai/\n",
        "https:\\\\example.com\\bai",
        "",
        None,
        123,
        "https://example.com/" + "a" * 3000,
    ],
)
def test_drops_items_with_foreign_or_bad_link(fake_wp, wp_client, link):
    bad = item(1)
    bad["link"] = link
    serve(fake_wp, posts=[bad, item(2)])
    assert [i.id for i in wp_client.list_published()] == [2]


def test_host_compare_ignores_case_and_default_port(fake_wp, wp_client):
    serve(
        fake_wp,
        posts=[item(1, link="https://EXAMPLE.com/a/"), item(2, link="https://example.com:443/b/")],
    )
    assert [i.id for i in wp_client.list_published()] == [1, 2]


def test_site_on_custom_port_requires_same_port():
    assert is_site_link("https://example.com:8443/a/", "https://example.com:8443")
    assert not is_site_link("https://example.com/a/", "https://example.com:8443")
    assert not is_site_link("https://example.com/a/", "http://example.com")


def test_title_and_meta_are_plain_text(fake_wp, wp_client):
    meta = {
        "_siteseo_titles_title": "<b>Đậm</b> &amp; <script>x</script>gọn",
        "_siteseo_titles_desc": "Dòng 1\n\tDòng 2\x00",
    }
    serve(
        fake_wp,
        posts=[
            item(1, title="<em>Cửa</em> sắt &#8211; <img src=x onerror=alert(1)>đẹp", meta=meta)
        ],
    )
    (result,) = wp_client.list_published()
    assert result.title == "Cửa sắt – đẹp"
    assert result.meta_title == "Đậm & xgọn"
    assert result.meta_desc == "Dòng 1 Dòng 2"


def test_long_title_and_meta_are_cut(fake_wp, wp_client):
    meta = {"_siteseo_titles_title": "m" * 5000, "_siteseo_titles_desc": "d " * 5000}
    serve(fake_wp, posts=[item(1, title="t" * 5000, meta=meta)])
    (result,) = wp_client.list_published()
    assert len(result.title) == MAX_TITLE_CHARS
    assert len(result.meta_title) == MAX_META_CHARS
    assert len(result.meta_desc) <= MAX_META_CHARS


@pytest.mark.parametrize(
    "meta",
    [None, {}, [], "chuỗi", {"_siteseo_titles_title": None, "_siteseo_titles_desc": 5}],
)
def test_missing_or_odd_meta_is_empty(fake_wp, wp_client, meta):
    raw = item(1)
    if meta is not None:
        raw["meta"] = meta
    serve(fake_wp, posts=[raw])
    (result,) = wp_client.list_published()
    assert (result.meta_title, result.meta_desc) == ("", "")


def test_meta_registered_as_array_uses_first_value(fake_wp, wp_client):
    serve(fake_wp, posts=[item(1, meta={"_siteseo_titles_title": ["Một", "Hai"]})])
    assert wp_client.list_published()[0].meta_title == "Một"


@pytest.mark.parametrize(
    "change",
    [
        {"id": None},
        {"id": "12"},
        {"id": 0},
        {"id": -3},
        {"id": True},
        {"id": 1.5},
    ],
)
def test_drops_items_with_bad_id(fake_wp, wp_client, change):
    serve(fake_wp, posts=[item(1, **change), item(2)])
    assert [i.id for i in wp_client.list_published()] == [2]


def test_odd_slug_title_and_date_are_blanked_not_fatal(fake_wp, wp_client):
    raw = item(1, title=None, slug="<script>", modified_gmt="hôm qua")
    raw["title"] = {"raw": "không có rendered"}
    serve(fake_wp, posts=[raw, "không phải dict", None, 5])
    (result,) = wp_client.list_published()
    assert (result.slug, result.title, result.modified_gmt) == ("", "", "")


def test_title_as_plain_string(fake_wp, wp_client):
    raw = item(1)
    raw["title"] = "Tiêu đề &amp; chuỗi"
    serve(fake_wp, posts=[raw])
    assert wp_client.list_published()[0].title == "Tiêu đề & chuỗi"


def test_duplicates_are_removed(fake_wp, wp_client):
    serve(fake_wp, posts=[item(1), item(1)], pages=[item(1, kind="page")])
    assert [(i.type, i.id) for i in wp_client.list_published()] == [("post", 1), ("page", 1)]


def test_type_comes_from_endpoint_not_from_site(fake_wp, wp_client):
    serve(fake_wp, posts=[item(1, kind="page")], pages=[item(2, kind="attachment")])
    assert [(i.type, i.id) for i in wp_client.list_published()] == [("post", 1), ("page", 2)]


def test_reads_many_pages(fake_wp, wp_client):
    def posts(request):
        page = int(query(request)["page"][0])
        start = (page - 1) * 100 + 1
        data = [item(n) for n in range(start, min(start + 100, 251))]
        return 200, data, {"X-WP-Total": "250", "X-WP-TotalPages": "3"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])

    result = wp_client.list_published()
    assert len(result) == 250
    assert [query(r)["page"] for r in fake_wp.requests] == [["1"], ["2"], ["3"], ["1"]]


def test_page_count_is_capped(fake_wp, wp_client):
    calls = []

    def posts(request):
        calls.append(request)
        page = int(query(request)["page"][0])
        return 200, [item(page)], {"X-WP-TotalPages": "100000"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    wp_client.list_published()
    assert len(calls) == MAX_PAGES


def test_not_a_list_is_vietnamese_error(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", {"code": "lạ"})
    with pytest.raises(WordPressError, match="danh sách"):
        wp_client.list_published()


def test_error_message_has_no_password(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", (401, {"code": "rest_not_logged_in"}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.list_published()
    assert "abcd" not in str(err.value) and "efgh" not in str(err.value)


def test_uses_client_timeout(fake_wp):
    seen = []

    class Recording(type(make_session(fake_wp))):
        def request(self, method, url, **kwargs):
            seen.append(kwargs.get("timeout"))
            return super().request(method, url, **kwargs)

    session = Recording()
    session.mount("https://", fake_wp)
    serve(fake_wp)
    WordPressClient(BASE_URL, "lam", "abcd", session=session, timeout=7).list_published()
    assert seen == [7, 7]


@pytest.mark.parametrize(
    "field, value",
    [
        ("id", 0),
        ("type", "attachment"),
        ("slug", "a b"),
        ("link", ""),
        ("title", "x" * (MAX_TITLE_CHARS + 1)),
        ("meta_desc", "có\x07chuông"),
        ("modified_gmt", "2026-10-01"),
        ("title", 5),
    ],
)
def test_published_item_validates_itself(field, value):
    good = {"id": 1, "type": "post", "slug": "a", "link": f"{BASE_URL}/a/", "title": "A"}
    with pytest.raises(ValueError):
        PublishedItem(**{**good, field: value})

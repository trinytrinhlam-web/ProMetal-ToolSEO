"""T-042 lượt 2: SL-T042-4, -5, -6, khe kiểm-rồi-ghi, LC-T044-1 (dữ liệu sai kiểu từ site).

Chỉ dùng site giả (``FakeWordPress``), không gọi mạng thật.
"""

import json

import pytest
from fake_wordpress import BASE_URL, make_session

from seo_app.wordpress import WordPressClient, WordPressError

POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
TITLE = "Cửa sắt 2 cánh: 6 dấu hiệu cần thay | Pro-Metal"
DESC = "Bánh xe kêu, cửa kẹt, ray mòn? Đây là 6 dấu hiệu cửa sắt nhà bạn cần sửa ngay."
ROOT = {"name": "ProMetal", "home": BASE_URL, "namespaces": ["wp/v2"]}
ME = {"name": "Lâm", "roles": ["editor"], "capabilities": {"edit_posts": True}}


def body(request):
    return json.loads(request.body) if request.body else None


def writes(fake):
    return [r for r in fake.requests if r.method != "GET"]


@pytest.fixture
def client(fake_wp):
    return WordPressClient(
        BASE_URL, "lam", "abcd efgh", session=make_session(fake_wp), write_seo=True
    )


def draft_site(fake, *, status="draft", run=None, ability=True):
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake.on("GET", POST_42, {"id": 42, "status": status, "meta": {}})
    fake.on(
        "GET",
        ABILITY,
        {"name": "siteseo-posts/seo-data-update"} if ability else (404, {"code": "x"}, {}),
    )
    if run is not None:
        fake.on("POST", RUN, run)


# ------------------------------------------------------------ SL-T042-4


@pytest.mark.parametrize("answer_id", [True, False, "7", " 8 ", 7.9, "0042", 0, -3, None, [42]])
def test_create_draft_with_odd_id_raises_and_records_nothing(fake_wp, client, answer_id):
    fake_wp.on("POST", POSTS, (201, {"id": answer_id, "status": "draft"}, {}))
    with pytest.raises(WordPressError, match="không đúng dạng"):
        client.create_draft("A", "B")
    assert client._created_post_ids == set()


@pytest.mark.parametrize("answer", [[], "ok", None, 42, {"status": "draft"}])
def test_create_draft_with_odd_answer_raises(fake_wp, client, answer):
    fake_wp.on("POST", POSTS, (201, answer, {}))
    with pytest.raises(WordPressError):
        client.create_draft("A", "B")
    assert client._created_post_ids == set()


@pytest.mark.parametrize("answer_id", [True, "7", 7.9, 0, -1, None])
def test_upload_media_with_odd_id_raises_without_second_request(fake_wp, client, answer_id):
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, {"id": answer_id, "source_url": "u"}, {}))
    fake_wp.on("POST", "/wp-json/wp/v2/media/1", {"id": 1})
    fake_wp.on("POST", "/wp-json/wp/v2/media/7", {"id": 7})
    with pytest.raises(WordPressError, match="không đúng dạng"):
        client.upload_media(b"x", "a.png", alt_text="ảnh")
    assert len(fake_wp.requests) == 1


@pytest.mark.parametrize("answer", [[], "ok", None])
def test_upload_media_with_odd_answer_raises(fake_wp, client, answer):
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, answer, {}))
    with pytest.raises(WordPressError):
        client.upload_media(b"x", "a.png")


def test_upload_media_odd_fields_are_safe(fake_wp, client):
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, {"id": 5, "source_url": 123}, {}))
    fake_wp.on("POST", "/wp-json/wp/v2/media/5", ["không phải dict"])
    media = client.upload_media(b"x", "a.png", alt_text="ảnh")
    assert (media.id, media.source_url, media.alt_text) == (5, "", "ảnh")


# ------------------------------------------------------------ SL-T042-5


@pytest.mark.parametrize("status", ["publish", "future", "pending", "private", "trash"])
def test_featured_image_refused_when_post_no_longer_draft(fake_wp, client, status):
    draft_site(fake_wp, status=status)
    fake_wp.on("POST", POST_42, {"id": 42, "status": status, "featured_media": 9})
    client.create_draft("A", "B")
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_featured_image(42, 9)
    assert [r.path_url for r in writes(fake_wp)] == [POSTS]
    assert 42 not in client._created_post_ids


def test_featured_image_still_works_on_own_draft(fake_wp, client):
    draft_site(fake_wp)
    fake_wp.on("POST", POST_42, {"id": 42, "status": "draft", "featured_media": 9})
    client.create_draft("A", "B")
    assert client.set_featured_image(42, 9).featured_media == 9
    assert body(writes(fake_wp)[-1]) == {"featured_media": 9}
    methods = [(r.method, r.path_url.split("?")[0]) for r in fake_wp.requests]
    assert methods[-2:] == [("GET", POST_42), ("POST", POST_42)]  # kiểm ngay trước khi ghi


@pytest.mark.parametrize("post_id", [True, 42.0, "42", None])
def test_featured_image_post_id_must_be_int(fake_wp, client, post_id):
    draft_site(fake_wp)
    client.create_draft("A", "B")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_featured_image(post_id, 9)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("media_id", [True, 0, -1, "9", 9.0, None])
def test_featured_image_media_id_must_be_positive_int(fake_wp, client, media_id):
    draft_site(fake_wp)
    client.create_draft("A", "B")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="Mã ảnh"):
        client.set_featured_image(42, media_id)
    assert len(fake_wp.requests) == before


def test_featured_image_check_failure_has_fixed_message(fake_wp, client):
    draft_site(fake_wp)
    fake_wp.on("GET", POST_42, (500, {"code": "x", "message": "<b>BI_MAT_MAY_CHU</b>"}, {}))
    client.create_draft("A", "B")
    with pytest.raises(WordPressError) as err:
        client.set_featured_image(42, 9)
    assert "ảnh đại diện" in str(err.value) and "mã 500" in str(err.value)
    assert "BI_MAT" not in str(err.value) and "<b>" not in str(err.value)
    assert len(writes(fake_wp)) == 1


# ------------------------------------------------------------ khe kiểm-rồi-ghi


@pytest.mark.parametrize("ability", [True, False])
def test_draft_check_is_the_last_request_before_writing(fake_wp, client, ability):
    draft_site(fake_wp, run={"updated": True}, ability=ability)
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {
        "_siteseo_titles_title": "", "_siteseo_titles_desc": ""}})
    fake_wp.on(
        "POST", POST_42, lambda r: {"id": 42, "status": "draft", "meta": body(r)["meta"]}
    )
    client.create_draft("A", "B")
    assert client.set_seo_meta(42, title=TITLE).written
    order = [(r.method, r.path_url.split("?")[0]) for r in fake_wp.requests[1:]]
    assert order[0] == ("GET", ABILITY)  # dò trước
    assert order[-2] == ("GET", POST_42)  # kiểm nháp ngay trước lệnh ghi
    assert order[-1][0] == "POST"


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 43, "status": "draft", "meta": {"_siteseo_titles_title": TITLE}},
        {"id": 42, "status": "publish", "meta": {"_siteseo_titles_title": TITLE}},
        {"id": "42", "status": "draft", "meta": {"_siteseo_titles_title": TITLE}},
        [],
        "ok",
    ],
)
def test_meta_route_write_answer_must_be_same_draft(fake_wp, client, answer):
    draft_site(fake_wp, ability=False)
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {
        "_siteseo_titles_title": "", "_siteseo_titles_desc": ""}})
    fake_wp.on("POST", POST_42, answer)
    client.create_draft("A", "B")
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "error"


# ------------------------------------------------------------ SL-T042-6


@pytest.mark.parametrize(
    "answer",
    [
        {"updated": True, "post": {"title": TITLE, "description": None}},  # khuôn SiteSEO
        {"updated": True},
        {"success": True},
    ],
)
def test_ability_confirmed_answer_is_written(fake_wp, client, answer):
    draft_site(fake_wp, run=answer)
    client.create_draft("A", "B")
    assert client.set_seo_meta(42, title=TITLE).written is True


@pytest.mark.parametrize(
    "answer",
    [
        {"updated": "true"},
        {"updated": 1},
        {"updated": False, "post": {"title": TITLE}},
        {"success": "true"},
        {"updated": True, "code": "forbidden"},
        {"updated": True, "post": {"title": "chữ khác"}},  # site lưu khác chữ đã gửi
        {"updated": True, "post": {"title": TITLE}},  # thiếu mô tả đã gửi
        {"updated": True, "post": "x"},
        {"code": "invalid_post", "message": "Post not found.", "data": {"status": 400}},
        {},
        True,
        1,
    ],
)
def test_ability_answer_not_confirming_is_not_written(fake_wp, client, answer):
    draft_site(fake_wp, run=(200, answer, {}))
    client.create_draft("A", "B")
    result = client.set_seo_meta(42, title=TITLE, description=DESC)
    assert result.written is False
    assert result.reason == "error"
    assert "Post not found" not in result.message


def test_ability_snapshot_must_match_every_sent_field(fake_wp, client):
    snapshot = {"title": TITLE, "description": DESC, "focus_keyphrase": "sửa cửa sắt"}
    draft_site(fake_wp, run={"updated": True, "post": snapshot})
    client.create_draft("A", "B")
    result = client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword="sửa cửa sắt")
    assert result.written is True
    assert result.fields == ("title", "description", "focus_keyword")


# ------------------------------------------------------------ LC-T044-1


@pytest.mark.parametrize("name", [123, None, ["a"], {"x": 1}, True, 1.5])
def test_check_connection_odd_names_do_not_crash(fake_wp, client, name):
    fake_wp.on("GET", "/wp-json/", {**ROOT, "name": name})
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", {**ME, "name": name})
    info = client.check_connection()
    assert isinstance(info.site_name, str) and isinstance(info.user_name, str)
    if name in (123, 1.5):
        assert info.site_name == str(name)
    else:
        assert info.site_name == ""


@pytest.mark.parametrize("me", [[], "ok", None, 5])
def test_check_connection_me_not_dict_raises_fixed_error(fake_wp, client, me):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", (200, me, {}))
    with pytest.raises(WordPressError, match="không đúng dạng"):
        client.check_connection()


@pytest.mark.parametrize("namespaces", ["wp/v2", None, {"wp/v2": 1}, 5])
def test_check_connection_namespaces_must_be_a_list(fake_wp, client, namespaces):
    fake_wp.on("GET", "/wp-json/", {**ROOT, "namespaces": namespaces})
    with pytest.raises(WordPressError, match="wp/v2"):
        client.check_connection()


def test_check_connection_odd_fields_are_safe(fake_wp, client):
    fake_wp.on("GET", "/wp-json/", {**ROOT, "home": 5, "url": ["x"]})
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/users/me",
        {"name": "A", "roles": ["editor", 5, None], "capabilities": {"edit_posts": "true"}},
    )
    info = client.check_connection()
    assert info.site_url == BASE_URL
    assert info.roles == ("editor",)
    assert info.can_edit_posts is False  # chỉ True thật mới tính


@pytest.mark.parametrize("roles", ["editor", None, {"a": 1}])
def test_check_connection_roles_not_list(fake_wp, client, roles):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", {**ME, "roles": roles, "capabilities": []})
    info = client.check_connection()
    assert info.roles == ()
    assert info.can_edit_posts is False


def test_terms_with_odd_items_are_skipped_or_coerced(fake_wp, client):
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/categories",
        [
            {"id": 1, "name": 5, "slug": None, "count": "3", "parent": True},
            {"id": "2", "name": "bỏ"},
            {"id": True, "name": "bỏ"},
            {"id": -1, "name": "bỏ"},
            "không phải dict",
            None,
            {"name": "thiếu id"},
            {"id": 3, "name": "Cửa &amp; cổng", "slug": "cua", "count": 4, "parent": 1},
        ],
    )
    terms = client.list_categories()
    assert [(t.id, t.name, t.slug, t.count, t.parent) for t in terms] == [
        (1, "5", "", 0, 0),
        (3, "Cửa & cổng", "cua", 4, 1),
    ]


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 42, "status": 5, "title": 7, "link": None, "featured_media": "9"},
        {"id": 42, "status": "draft", "title": {"raw": None, "rendered": ["x"]}},
    ],
)
def test_post_answer_odd_fields_are_safe(fake_wp, client, answer):
    fake_wp.on("POST", POSTS, (201, answer, {}))
    post = client.create_draft("A", "B")
    assert post.id == 42
    assert isinstance(post.title, str) and isinstance(post.link, str)
    assert post.featured_media == 0


# ------------------------------------------------------------ SL-T042-3


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/?rest_route=/code-snippets/v1/snippets",
        "https://example.com/wp-json/code-snippets/v1/snippets#",
        "https://example.com/#",
        "https://example.com?",
        "https://example.com/a%2e%2e",
        "https://example.com/../x",
        "https://example.com/./x",
        "https://example.com/wp-json",
        "https://example.com/WP-JSON",
        "https://example.com/prometal/v1/purge",
        "https://example.com/code-snippets",
        "https://example.com/wp-admin",
        "https://lam:abcd@example.com",
        "https://example.com@evil.com",
        "https://example.com//evil",
        "https://example.com/a b",
        "https://example.com/a\b",
        "https://exa_mple.com",
        "https://example.com:99999x",
    ],
)
def test_odd_wordpress_url_is_refused(url):
    with pytest.raises(WordPressError) as err:
        WordPressClient(url, "lam", "abcd")
    assert "abcd" not in str(err.value)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://example.com/",
        "HTTPS://Example.COM/",
        "https://www.suachuacuasat.com",
        "https://example.com:8443",
        "https://example.com/blog",
        "https://example.com/blog/wp",
        "https://xn--sa-cua-st-8za.vn",
    ],
)
def test_normal_wordpress_url_is_accepted(url):
    assert WordPressClient(url, "lam", "abcd").uses_https


# ------------------------------------------------------------ SL-T042-2


@pytest.mark.parametrize(
    "text",
    ["Cửa &ltscript&gt", "&LT;b", "Giá &amp rẻ", "&copy 2026", "&nbspCửa", "&quot", "&reg",
     "&frac12 giá", "&AMP"],
)
def test_legacy_entities_without_semicolon_blocked(fake_wp, client, text):
    draft_site(fake_wp, run={"updated": True})
    client.create_draft("A", "B")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="mã ký tự HTML"):
        client.set_seo_meta(42, title=text)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("text", ["R&D", "AT&T", "A & B", "Q&A", "P&G", "Cửa & cổng", "&Lt"])
def test_plain_ampersand_still_passes(fake_wp, client, text):
    draft_site(fake_wp, run={"updated": True})
    client.create_draft("A", "B")
    assert client.set_seo_meta(42, title=text).written


# ------------------------------------------------------------ SL-T042-7


@pytest.mark.parametrize("char", ["ㅤ", "ᅟ", "ᅠ", "ﾠ", "͏", "️",
                                  "᠋", "឴", "\U000e0100"])
def test_ignorable_not_cf_is_dropped_and_refused(char):
    from seo_app.wordpress import PublishedItem, is_site_link
    from seo_app.wordpress.client import _clean_text

    assert _clean_text(f"Cửa{char} sắt", 50) == "Cửa sắt"
    assert not is_site_link(f"{BASE_URL}/cua{char}sat/", BASE_URL)
    with pytest.raises(ValueError):
        PublishedItem(id=1, type="post", slug="a", link=f"{BASE_URL}/a/", title=f"A{char}B")

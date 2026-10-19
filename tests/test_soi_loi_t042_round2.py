"""Soi Lỗi · T-042 lượt 2: thử phá các chỗ Thợ Máy sửa (SL-T042-1…7, LC-T044-1, dò trước
rồi kiểm nháp ngay trước khi ghi). Chỉ site giả, không mạng thật.

Test ``xfail(strict=True)`` là lỗi lượt 2 (SL-T042-8…11 trong
``docs/team/reports/T-042-soi-loi.md``).
"""

import html.entities
import itertools
import json

import pytest
from fake_wordpress import BASE_URL, FakeWordPress, make_session, query

from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import (
    _LEGACY_ENTITY,
    _ability_confirms,
    _is_plain_site_url,
    _positive_id,
    _seo_text,
)

POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
TITLE = "Cửa sắt 2 cánh | Pro-Metal"


def make(fake, **kwargs):
    return WordPressClient(BASE_URL, "lam", "abcd efgh", session=make_session(fake), **kwargs)


def writes(fake):
    return [r for r in fake.requests if r.method != "GET"]


def site(fake, *, run=None):
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake.on("POST", RUN, run if run is not None else {"updated": True})


# ================================================================ SL-T042-2: _LEGACY_ENTITY


def test_legacy_entity_list_is_the_106_html_names_without_semicolon():
    names = [n for n in html.entities.html5 if not n.endswith(";")]
    assert len(names) == 106
    for name in names:
        assert _LEGACY_ENTITY.search("&" + name), name


@pytest.mark.parametrize(
    "text",
    ["R&D", "AT&T", "Q&A", "P&G", "H&M", "M&E", "A&B", "Sale&off", "Cửa&cổng", "Sắt&Inox",
     "Black&White", "Mua&bán", "&Lt", "&Notice", "& lt", "&"],
)
def test_ordinary_ampersands_still_pass(text):
    assert _seo_text("T", text, 200) == text


@pytest.mark.parametrize(
    "text",
    [
        "&​lt",  # ký tự vô hình chen giữa: bỏ đi thì thành &lt
        "&l​t",
        "＆lt",  # & toàn khổ
        "&ETH",
        "&ltd",  # trình duyệt giải mã "&lt" rồi chữ "d" (trong nội dung, không trong thuộc tính)
        "&notice",  # "&not" + "ice": trình duyệt hiện "¬ice" -> chặn là đúng nếu in nguyên văn
        "Tom&amp",
    ],
)
def test_legacy_entity_variants_are_blocked(text):
    with pytest.raises(WordPressError, match="mã ký tự HTML"):
        _seo_text("T", text, 200)


# ================================================================ SL-T042-3: _is_plain_site_url


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/Wp-Admin",
        "https://example.com/WP-JSON",
        "https://example.com/blog/wp-json2",
        "https://example.com/;x",
        "https://example.com/a;b",
        "https://example.com/a/./b",
        "https://example.com/a/../b",
        "https://example.com/.well-known",
        "https://example.com//blog",
        "https://user@example.com",
        "https://user:pass@example.com",
        "https://example.com\\@evil.com",
        "https://example.com%2F@evil.com",
        "https://suachuacửa.com",  # tên miền chưa đổi sang punycode
        "https://[::1]",
        "https://example.com.",
        "https://-example.com",
        "https://example.com:/",
        "https://example.com:port",
        "https://example.com/a b",
        "https://example.com/blog?x",
        "https://example.com/blog#x",
        "https://example.com/Code-Snippets",
        "https://example.com/ProMetal",
        "http://example.com",
        "ftp://example.com",
    ],
)
def test_bad_wordpress_urls_are_refused(url):
    with pytest.raises(WordPressError) as err:
        WordPressClient(url, "lam", "abcd")
    assert "evil" not in str(err.value) and "pass" not in str(err.value)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://EXAMPLE.com",
        "https://example.com/blog",
        "https://example.com/blog/",
        "https://example.com/~user",
        "https://example.com:8443",
        "https://127.0.0.1",
        "https://xn--sachuacuast-x9a.com",
    ],
)
def test_normal_wordpress_urls_are_accepted(url):
    assert _is_plain_site_url(url.rstrip("/"))


@pytest.mark.xfail(strict=True, reason="SL-T042-9: tab/xuống dòng giữa WORDPRESS_URL vẫn qua")
@pytest.mark.parametrize(
    "url", ["https://exa\tmple.com", "https://exam\nple.com", "https://example.com/blo\tg"]
)
def test_wordpress_url_with_inner_tab_or_newline_is_refused(url):
    """``urlsplit`` âm thầm bỏ ``\\t``, ``\\n``, ``\\r`` nên ``_is_plain_site_url`` xét một
    địa chỉ khác với chuỗi thật được dùng để gọi (``https://example.com/blo%09g/wp-json/…``).
    Báo cáo Thợ Máy ghi là từ chối khoảng trắng. Hiện vô hại (tên máy lạ thì requests báo lỗi,
    thư mục lạ thì 404) nhưng chốt chặn không đúng như mô tả."""
    with pytest.raises(WordPressError):
        WordPressClient(url, "lam", "abcd")


@pytest.mark.xfail(strict=True, reason="SL-T042-10: WORDPRESS_URL trỏ thẳng vào một file .php")
@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/wp-content/plugins/x/run.php",
        "https://example.com/xmlrpc.php",
        "https://example.com/wp-login.php",
    ],
)
def test_wordpress_url_pointing_at_php_file_is_refused(url):
    """Request thật thành ``POST …/run.php/wp-json/wp/v2/posts``: chạy file PHP đó (với
    PATH_INFO), không phải REST API của WordPress. Chỉ ``.env`` mới đặt được."""
    with pytest.raises(WordPressError):
        WordPressClient(url, "lam", "abcd")


# ================================================================ SL-T042-4: _positive_id


class IntChild(int):
    pass


@pytest.mark.parametrize(
    "value", [True, False, 0, -1, -42, IntChild(5), "5", " 5", 5.0, 5.5, None, [5], {"id": 5}]
)
def test_positive_id_refuses_everything_but_positive_int(value):
    assert _positive_id(value) is None


@pytest.mark.parametrize("value", [1, 42, 2**31, 2**62])
def test_positive_id_accepts_positive_int(value):
    assert _positive_id(value) == value


# ================================================================ SL-T042-5: ảnh đại diện


@pytest.mark.parametrize("status", ["publish", "future", "private", "pending", "trash", None])
def test_featured_image_draft_published_between_create_and_set(fake_wp, status):
    client = make(fake_wp)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": status})
    fake_wp.on("POST", POST_42, {"id": 42, "status": "draft", "featured_media": 7})
    client.create_draft("A", "B")
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_featured_image(42, 7)
    assert [r.path_url for r in writes(fake_wp)] == [POSTS]
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):  # đã bỏ id
        client.set_featured_image(42, 7)


@pytest.mark.parametrize("media_id", [True, 0, -7, "7", 7.0, None, IntChild(7)])
def test_featured_image_odd_media_id_refused_without_request(fake_wp, media_id):
    client = make(fake_wp)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    client.create_draft("A", "B")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError):
        client.set_featured_image(42, media_id)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("post_id", [True, 42.0, "42", IntChild(42)])
def test_featured_image_odd_post_id_refused_without_request(fake_wp, post_id):
    client = make(fake_wp)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    client.create_draft("A", "B")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_featured_image(post_id, 7)
    assert len(fake_wp.requests) == before


def test_featured_image_check_is_the_request_right_before_write(fake_wp):
    client = make(fake_wp)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft"})
    fake_wp.on("POST", POST_42, {"id": 42, "status": "draft", "featured_media": 7})
    client.create_draft("A", "B")
    client.set_featured_image(42, 7)
    tail = [(r.method, r.path_url.split("?")[0]) for r in fake_wp.requests[-2:]]
    assert tail == [("GET", POST_42), ("POST", POST_42)]
    assert json.loads(fake_wp.requests[-1].body) == {"featured_media": 7}


@pytest.mark.xfail(strict=True, reason="SL-T042-11: câu trả lời của lệnh đặt ảnh không được soát")
@pytest.mark.parametrize(
    "answer",
    [
        {"id": 43, "status": "draft", "featured_media": 7},
        {"id": 42, "status": "publish", "featured_media": 7},
    ],
)
def test_featured_image_answer_for_other_or_published_post_is_reported(fake_wp, answer):
    """Đường meta dự phòng đã soát ``id``/``status`` trong câu trả lời của lệnh ghi (lượt 2),
    ``set_featured_image`` thì chưa: trả ``Post`` của bài 43, hay bài đã đăng, như thành công."""
    client = make(fake_wp)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft"})
    fake_wp.on("POST", POST_42, answer)
    client.create_draft("A", "B")
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 7)


# ================================================================ SL-T042-6: _ability_confirms


@pytest.mark.parametrize(
    "answer",
    [
        {"updated": True},
        {"updated": True, "post": {"title": TITLE, "description": "khác", "robots": "x"}},
        {"success": True},
    ],
)
def test_ability_siteseo_shapes_are_written(fake_wp, answer):
    client = make(fake_wp, write_seo=True)
    site(fake_wp, run=answer)
    client.create_draft("A", "B")
    assert client.set_seo_meta(42, title=TITLE).written


@pytest.mark.parametrize(
    "answer",
    [
        {"updated": True, "post": {"title": TITLE + " "}},
        {"updated": True, "post": {"description": TITLE}},
        {"updated": True, "post": []},
        {"updated": True, "post": "ok"},
        {"updated": True, "code": "forbidden"},
        {"updated": True, "code": None},
        {"updated": "true"},
        {"updated": 1},
        {"success": 1},
        {"updated": None},
        {},
    ],
)
def test_ability_unconfirmed_shapes_are_not_written(fake_wp, answer):
    client = make(fake_wp, write_seo=True)
    site(fake_wp, run=answer)
    client.create_draft("A", "B")
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False and result.reason == "error"


def test_ability_snapshot_checks_keyword_field_name():
    assert _ability_confirms({"updated": True, "post": {"focus_keyphrase": "k"}},
                             {"focus_keyword": "k"})
    assert not _ability_confirms({"updated": True, "post": {"focus_keyword": "k"}},
                                 {"focus_keyword": "k"})


@pytest.mark.xfail(strict=True, reason="SL-T042-8: false rõ ràng bị true ở khóa kia lấn át")
@pytest.mark.parametrize(
    "answer", [{"updated": False, "success": True}, {"updated": True, "success": False}]
)
def test_ability_explicit_false_wins(fake_wp, answer):
    """Câu trả lời tự mâu thuẫn: có một khóa nói rõ ``False`` thì không được báo đã ghi."""
    client = make(fake_wp, write_seo=True)
    site(fake_wp, run=answer)
    client.create_draft("A", "B")
    assert client.set_seo_meta(42, title=TITLE).written is False


# ================================================================ SL-T042-1: phân trang


def raw_post(id_):
    return {"id": id_, "status": "publish", "slug": f"b-{id_}", "link": f"{BASE_URL}/b-{id_}/",
            "title": {"rendered": "x"}}


def test_out_of_range_after_header_said_more_pages_raises(fake_wp):
    client = make(fake_wp)

    def handler(request):
        if query(request)["page"] == ["1"]:
            return 200, [raw_post(i) for i in range(1, 101)], {"X-WP-TotalPages": "3"}
        return 400, {"code": "rest_post_invalid_page_number", "message": "x"}, {}

    fake_wp.on("GET", POSTS, handler)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    with pytest.raises(WordPressError):
        client.list_published()


def test_out_of_range_without_header_ends_the_list(fake_wp):
    client = make(fake_wp)

    def handler(request):
        if query(request)["page"] == ["1"]:
            return 200, [raw_post(i) for i in range(1, 101)], {}
        return 400, {"code": "rest_post_invalid_page_number", "message": "x"}, {}

    fake_wp.on("GET", POSTS, handler)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = client.list_published()
    assert len(items) == 100 and items.truncated is False


@pytest.mark.parametrize("header", ["2", "50", "999", None, "abc"])
def test_repeated_page_flags_truncated_with_or_without_header(fake_wp, header):
    client = make(fake_wp)
    headers = {} if header is None else {"X-WP-TotalPages": header}
    fake_wp.on("GET", POSTS, (200, [raw_post(i) for i in range(1, 101)], headers))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = client.list_published()
    assert len(items) == 100 and items.truncated is True
    assert sum(1 for r in fake_wp.requests if r.path_url.startswith(POSTS)) == 2


# ================================================================ LC-T044-1: dữ liệu sai kiểu

ODD = [None, True, False, 0, -1, 1.5, float("nan"), "", "x", "<b>x</b>", [], ["wp/v2"],
       [None, 1, "a"], {}, {"a": 1}, {"raw": 5}, 10**30]


@pytest.mark.parametrize(
    ("key", "value"),
    list(itertools.product(["root", "namespaces", "name", "home", "me", "me_name", "roles",
                            "caps", "cap_value", "probe"], ODD)),
)
def test_check_connection_odd_data_never_crashes(key, value):
    fake = FakeWordPress()
    root = {"name": "S", "home": BASE_URL, "namespaces": ["wp/v2"]}
    me = {"name": "U", "roles": ["editor"], "capabilities": {"edit_posts": True}}
    probe = {"name": "siteseo-posts/seo-data-update"}
    if key == "root":
        root = value
    elif key in ("namespaces", "name", "home"):
        root[key] = value
    elif key == "me":
        me = value
    elif key == "me_name":
        me["name"] = value
    elif key == "roles":
        me["roles"] = value
    elif key == "caps":
        me["capabilities"] = value
    elif key == "cap_value":
        me["capabilities"] = {"edit_posts": value}
    else:
        probe = value
    fake.on("GET", "/wp-json/", root)
    fake.on("GET", "/wp-json/wp/v2/users/me", me)
    fake.on("GET", ABILITY, probe)
    try:
        info = make(fake).check_connection()
    except WordPressError:
        return
    assert isinstance(info.site_name, str) and isinstance(info.site_url, str)
    assert isinstance(info.user_name, str) and isinstance(info.siteseo_status, str)
    assert all(isinstance(role, str) for role in info.roles)
    assert info.can_edit_posts in (True, False)
    if key == "cap_value":
        assert info.can_edit_posts is (value is True)


@pytest.mark.parametrize(
    ("field", "value"),
    list(itertools.product(["item", "id", "name", "slug", "count", "parent"], ODD)),
)
def test_terms_odd_data_never_crashes(field, value):
    fake = FakeWordPress()
    item = {"id": 3, "name": "A", "slug": "a", "count": 1, "parent": 0}
    if field == "item":
        item = value
    else:
        item[field] = value
    fake.on("GET", "/wp-json/wp/v2/categories", [item])
    for term in make(fake).list_categories():
        assert type(term.id) is int and term.id >= 0
        assert isinstance(term.name, str) and isinstance(term.slug, str)
        assert type(term.count) is int and type(term.parent) is int


@pytest.mark.parametrize(
    ("field", "value"),
    list(itertools.product(["body", "id", "status", "title", "link", "featured_media"], ODD)),
)
def test_post_and_media_answers_odd_data_never_crash(field, value):
    fake = FakeWordPress()
    answer = {"id": 42, "status": "draft", "title": {"raw": "T"}, "link": BASE_URL + "/?p=42",
              "featured_media": 0, "source_url": BASE_URL + "/a.jpg"}
    if field == "body":
        answer = value
    else:
        answer[field] = value
    for method, path in (("POST", POSTS), ("POST", POST_42), ("POST", "/wp-json/wp/v2/media"),
                         ("POST", "/wp-json/wp/v2/media/42")):
        fake.on(method, path, (201, answer, {}))
    fake.on("GET", POST_42, {"id": 42, "status": "draft"})
    client = make(fake)
    try:
        post = client.create_draft("T", "x")
        assert type(post.id) is int and post.id > 0
        assert isinstance(post.status, str) and isinstance(post.title, str)
        assert isinstance(post.link, str) and type(post.featured_media) is int
        if post.id in client._created_post_ids:
            client.set_featured_image(42, 9)
    except WordPressError:
        pass
    try:
        media = client.upload_media(b"x", "a.jpg", alt_text="alt", title="t")
        assert type(media.id) is int and media.id > 0
        assert isinstance(media.source_url, str) and isinstance(media.alt_text, str)
    except WordPressError:
        pass

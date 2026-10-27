"""Soi Lỗi · T-042: thử phá ``set_seo_meta``, danh sách đường REST, chặn chữ SEO, phân trang.

Chỉ dùng site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật. Test đánh dấu
``xfail(strict=True)`` là lỗi Soi Lỗi tìm thấy (mã SL-T042-n trong
``docs/team/reports/T-042-soi-loi.md``); Thợ Máy sửa xong thì bỏ dấu ``xfail``.
"""

import json
from contextlib import suppress
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session, siteseo_seo_answer

from seo_app.wordpress import WordPressClient, WordPressError, is_allowed_route

ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
META_KEYS = {"_siteseo_titles_title": "", "_siteseo_titles_desc": ""}
PASSWORD = "abcd efgh ijkl mnop"
SECRET = "<b>bí mật máy chủ</b> /home/site/wp-config.php DB_PASSWORD=xyz"
TITLE = "Cửa sắt 2 cánh: 6 dấu hiệu cần thay | Pro-Metal"
DESC = "Bánh xe kêu, cửa kẹt, ray mòn? Đây là 6 dấu hiệu cửa sắt nhà bạn cần sửa."


def body(request):
    return json.loads(request.body) if request.body else None


def writes(fake):
    return [r for r in fake.requests if r.method != "GET"]


def wp_path(request):
    return request.path_url.split("?")[0]


@pytest.fixture
def client(fake_wp):
    return WordPressClient(
        BASE_URL, "lam", PASSWORD, session=make_session(fake_wp), write_seo=True
    )


def site(fake, *, status="draft", meta=None, ability=True, run=None, meta_answer=None):
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake.on("GET", POST_42, {"id": 42, "status": status, "meta": dict(META_KEYS) if meta is None
                             else meta})
    if ability is True:
        fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    else:
        fake.on("GET", ABILITY, (404, {"code": "rest_no_route", "message": SECRET}, {}))
    # T-059: mặc định là khuôn thật của SiteSEO 1.4.2 (đo trên site 27/10), không còn
    # ``{"success": True}``.
    fake.on("POST", RUN, run if run is not None else siteseo_seo_answer)
    if meta_answer is not None:
        fake.on("POST", POST_42, meta_answer)


def created(client):
    assert client.create_draft("Tiêu đề", "<p>Nội dung</p>").id == 42
    return 42


# ================================================================ trạng thái bài đổi giữa các bước


def test_draft_published_after_first_write_is_refused_on_second(fake_wp, client):
    """Ghi lần 1 khi còn nháp; người dùng bấm Đăng; ghi lần 2 phải hỏi lại và từ chối."""
    state = {"status": "draft"}
    site(fake_wp)
    fake_wp.on("GET", POST_42, lambda _r: {"id": 42, "status": state["status"], "meta": {}})
    created(client)
    assert client.set_seo_meta(42, title=TITLE).written
    state["status"] = "publish"
    runs_before = sum(1 for r in fake_wp.requests if wp_path(r) == RUN)
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_seo_meta(42, title=TITLE)
    assert sum(1 for r in fake_wp.requests if wp_path(r) == RUN) == runs_before
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 7)


@pytest.mark.parametrize("route", ["abilities", "meta"])
@pytest.mark.parametrize("status", ["publish", "future", "private", "pending", "draft "])
def test_draft_at_creation_published_at_write_time_no_write(fake_wp, client, route, status):
    site(fake_wp, status=status, ability=route == "abilities", meta_answer={"id": 42})
    created(client)
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword="sửa cửa sắt")
    assert [wp_path(r) for r in writes(fake_wp)] == [POSTS]  # chỉ lệnh tạo nháp


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 42.0, "status": "draft"},
        {"id": False, "status": "draft"},
        {"id": None, "status": "draft"},
        {"id": [42], "status": "draft"},
        {"id": {"value": 42}, "status": "draft"},
        {"id": 42, "status": ["draft"]},
        {"id": 42, "status": {"raw": "draft"}},
        {"id": 42, "status": "DRAFT"},
        {"id": 42, "status": "draft​"},
        {"id": 42},
        {},
        [],
        42,
        None,
        True,
    ],
)
def test_odd_draft_check_answers_are_refused(fake_wp, client, answer):
    site(fake_wp)
    fake_wp.on("GET", POST_42, (200, answer, {}))
    created(client)
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_seo_meta(42, title=TITLE)
    assert len(writes(fake_wp)) == 1
    assert 42 not in client._created_post_ids


def test_draft_check_html_answer_is_refused_with_fixed_message(fake_wp, client):
    site(fake_wp)
    fake_wp.on("GET", POST_42, (200, b"<html>" + SECRET.encode() + b"</html>", {}))
    created(client)
    with pytest.raises(WordPressError) as err:
        client.set_seo_meta(42, title=TITLE)
    assert "bí mật" not in str(err.value) and "wp-config" not in str(err.value)
    assert len(writes(fake_wp)) == 1


@pytest.mark.parametrize("post_id", [42.5, 42 + 0j, "0x2a", b"42", (42,), {42}, 2**63 + 42])
def test_post_id_odd_types_never_reach_the_site(fake_wp, client, post_id):
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_seo_meta(post_id, title=TITLE)
    assert len(fake_wp.requests) == before


def test_int_subclass_post_id_is_refused(fake_wp, client):
    class Sneaky(int):
        def __str__(self):  # đường ghép từ str() sẽ khác số đã kiểm
            return "42/../../code-snippets/v1/snippets"

    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError):
        client.set_seo_meta(Sneaky(42), title=TITLE)
    assert len(fake_wp.requests) == before


def test_post_created_by_other_client_is_refused(fake_wp):
    site(fake_wp)
    first = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake_wp),
                            write_seo=True)
    second = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake_wp),
                             write_seo=True)
    created(first)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        second.set_seo_meta(42, title=TITLE)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("status", ["draft ", "auto-draft", "", None, ["draft"], 0])
def test_create_draft_odd_status_answer_is_not_recorded(fake_wp, client, status):
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": status}, {}))
    client.create_draft("A", "B")
    assert client._created_post_ids == set()


@pytest.mark.parametrize("answer_id", [True, "7", " 8 ", 7.9, "0042"])
def test_create_draft_odd_id_answer_is_not_recorded(fake_wp, client, answer_id):
    """Site trả ``id`` sai kiểu: ``int(True)`` là 1, ``int(7.9)`` là 7, nên bài 1 hay bài 7
    (có thể là bài đã đăng của người khác) bị ghi nhận là "bài app tạo"."""
    fake_wp.on("POST", POSTS, (201, {"id": answer_id, "status": "draft"}, {}))
    with suppress(WordPressError):
        client.create_draft("A", "B")
    assert client._created_post_ids == set()


def test_featured_image_is_not_set_on_post_published_after_creation(fake_wp, client):
    """Báo cáo Thợ Máy: "không có đường nào ghi vào bài đã đăng". ``set_featured_image`` vẫn
    ``POST /wp/v2/posts/<id>`` mà không hỏi lại bài còn là nháp."""
    site(fake_wp, status="publish")
    fake_wp.on("POST", POST_42, {"id": 42, "status": "publish", "featured_media": 7})
    created(client)
    with suppress(WordPressError):
        client.set_featured_image(42, 7)
    assert [wp_path(r) for r in writes(fake_wp)] == [POSTS]


# ================================================================ đường dự phòng meta


def test_meta_route_sends_only_meta_with_two_known_keys(fake_wp, client):
    site(fake_wp, ability=False, meta_answer={
        "id": 42, "status": "draft", "meta": {"_siteseo_titles_title": TITLE,
                                              "_siteseo_titles_desc": DESC}})
    created(client)
    result = client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword="sửa cửa")
    assert result.written and result.route == "meta"
    sent = body(writes(fake_wp)[-1])
    assert set(sent) == {"meta"}
    assert sent["meta"] == {"_siteseo_titles_title": TITLE, "_siteseo_titles_desc": DESC}
    assert "focus_keyword" not in result.fields
    assert "chép tay" in result.message  # báo từ khóa chính chưa ghi


@pytest.mark.parametrize(
    "saved",
    [
        {"_siteseo_titles_title": TITLE + " "},
        {"_siteseo_titles_title": TITLE.upper()},
        {"_siteseo_titles_title": [TITLE]},
        {"_siteseo_titles_title": None},
        {},
    ],
)
def test_meta_route_compares_exactly_after_write(fake_wp, client, saved):
    site(fake_wp, ability=False, meta_answer={"id": 42, "status": "draft", "meta": saved})
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "unavailable"


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.ConnectionError("https://lam:abcdefghijklmnop@example.com"),
        requests.exceptions.Timeout("read timeout"),
        requests.exceptions.TooManyRedirects("loop"),
    ],
)
def test_meta_route_network_error_is_not_raised(fake_wp, client, error):
    site(fake_wp, ability=False)
    fake_wp.on("POST", POST_42, lambda _r: error)
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False and result.reason == "error"
    assert "abcd" not in result.message


def test_meta_route_non_json_answer_is_not_raised(fake_wp, client):
    site(fake_wp, ability=False)
    fake_wp.on("POST", POST_42, (200, b"<html>" + SECRET.encode(), {}))
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert "bí mật" not in result.message


def test_probe_server_error_falls_back_to_meta_only_with_two_keys(fake_wp, client):
    site(fake_wp, meta_answer={"id": 42, "meta": {"_siteseo_titles_title": TITLE}})
    fake_wp.on("GET", ABILITY, (500, {"message": SECRET}, {}))
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.route == "meta"
    assert all(wp_path(r) != RUN for r in fake_wp.requests)
    assert set(body(writes(fake_wp)[-1])) == {"meta"}


# ================================================================ câu lỗi cố định


def _all_failures(fake, client):
    """Chạy mọi nhánh lỗi của set_seo_meta, gom câu báo (exception hoặc result.message)."""
    messages = []
    scenarios = [
        {"GET " + POST_42: (500, {"code": "x", "message": SECRET}, {})},
        {"GET " + POST_42: (403, {"code": "rest_forbidden", "message": SECRET}, {})},
        {"POST " + RUN: (500, {"code": "x", "message": SECRET}, {})},
        {"POST " + RUN: (403, {"code": "x", "message": SECRET}, {})},
        {"POST " + RUN: (200, {"success": False, "message": SECRET}, {})},
        {"GET " + ABILITY: (404, {"message": SECRET}, {}),
         "POST " + POST_42: (500, {"message": SECRET}, {})},
        {"GET " + ABILITY: (404, {"message": SECRET}, {}),
         "POST " + POST_42: (403, {"message": SECRET}, {})},
        {"POST " + RUN: (302, {"message": SECRET}, {"Location": "/wp-json/code-snippets/v1"})},
    ]
    for scenario in scenarios:
        fake.routes.clear()
        site(fake)
        for key, answer in scenario.items():
            method, path = key.split(" ", 1)
            fake.on(method, path, answer)
        client._created_post_ids = set()
        client._siteseo_ok = None
        created(client)
        try:
            result = client.set_seo_meta(42, title=TITLE, description=DESC)
        except WordPressError as exc:
            messages.append(str(exc))
        else:
            assert not result.written
            messages.append(result.message)
    return messages


def test_seo_failure_messages_never_copy_server_or_password(fake_wp, client):
    messages = _all_failures(fake_wp, client)
    assert len(messages) == 8
    for message in messages:
        for leak in ("bí mật", "wp-config", "DB_PASSWORD", "<b>", "abcdefghijklmnop",
                     "abcd efgh", "code-snippets", "_siteseo_titles"):
            assert leak not in message, (leak, message)


# ================================================================ danh sách đường REST


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/wp/v2/posts/42/"),
        ("GET", "/wp/v2/posts/0042"),
        ("GET", "/wp/v2/posts/４２"),  # chữ số toàn khổ
        ("GET", "/wp/v2/posts/٤٢"),  # chữ số Ả Rập
        ("GET", "/wp/v2/posts/42;x"),
        ("GET", "/wp/v2/posts/42\n"),
        ("GET", "/wp/v2/posts/42\x00"),
        ("GET", "/wp/v2/posts/42?context=edit"),
        ("GET", "/wp/v2/posts/42#x"),
        ("POST", "/wp/v2/posts/42/revisions"),
        ("POST", "/wp/v2/posts/42/autosaves"),
        ("GET", "/wp/v2/users/me/application-passwords"),
        ("POST", "/wp/v2/users/me"),
        ("POST", "/wp/v2/settings"),
        ("POST", "/wp/v2/plugins"),
        ("DELETE", "/wp/v2/posts/42"),
        ("PUT", "/wp/v2/posts/42"),
        ("PATCH", "/wp/v2/posts/42"),
        ("OPTIONS", "/"),
        ("HEAD", "/"),
        ("get", "/wp/v2/posts"),
        ("Post", "/wp/v2/posts"),
        ("GET", ""),
        ("GET", "wp/v2/posts"),
        ("GET", "/∕wp/v2/posts"),  # gạch chéo Unicode
        ("GET", "/wp⁄v2/posts"),
        ("POST", "/wp-abilities/v1/abilities/siteseo-posts/seo-data-update/run/"),
        ("POST", "/wp-abilities/v1/abilities/siteseo-posts/seo-data-get/run"),
        ("GET", "/wp-abilities/v1/abilities/siteseo-posts/seo-data-update/run"),
        ("POST", "/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"),
        ("GET", "/wp-abilities/v1/abilities"),
        ("POST", "/wp-abilities/v1/abilities/code-snippets/run/run"),
        ("POST", "/wp-abilities/v1/abilities/siteseo-posts%2Fseo-data-update/run"),
        ("POST", "/wp/v2/posts/42/../../../code-snippets/v1/snippets"),
        ("POST", "/Code-Snippets/v1/snippets"),
        ("POST", "/PROMETAL/v1/purge"),
        ("POST", "/prometal/v1/deploy-files"),
        ("POST", "/wp/v2/posts/42/%2e%2e/%2E%2E/prometal/v1/purge"),
        ("POST", "/wp/v2/posts/４２"),
        ("GET", "/wp/v2/posts\\42"),
        ("GET", "//example.org/wp/v2/posts"),
        ("GET", "/wp/v2/posts/42 "),
        ("GET", " /wp/v2/posts/42"),
        ("GET", "/wp/v2/posts/42​"),
        ("GET", "/wp/v2/posts/42‮"),
    ],
)
def test_more_routes_are_refused(method, path):
    assert is_allowed_route(method, path) is False


def test_plain_ascii_route_still_allowed():
    assert is_allowed_route("GET", "/wp/v2/posts") is True
    assert is_allowed_route("POST", "/wp/v2/posts/42") is True


@pytest.mark.parametrize("method", [b"GET", None, 1, ("GET",)])
def test_route_check_non_string_method(method):
    assert is_allowed_route(method, "/") is False


@pytest.mark.parametrize("status", [300, 301, 302, 303, 304, 307, 308, 399])
@pytest.mark.parametrize("step", ["draft_check", "probe", "run", "meta"])
def test_redirects_in_seo_steps_are_never_followed(fake_wp, client, status, step):
    """3xx ở mọi bước của ``set_seo_meta``: không có request thứ hai theo ``Location``."""
    redirect = (status, {}, {"Location": BASE_URL + "/wp-json/code-snippets/v1/snippets"})
    site(fake_wp, ability=step != "meta")
    fake_wp.on("POST", "/wp-json/code-snippets/v1/snippets", {"id": 1})
    target = {"draft_check": ("GET", POST_42), "probe": ("GET", ABILITY), "run": ("POST", RUN),
              "meta": ("POST", POST_42)}[step]
    fake_wp.on(*target, redirect)
    created(client)
    try:
        result = client.set_seo_meta(42, title=TITLE)
    except WordPressError:
        result = None
    assert all("code-snippets" not in r.url for r in fake_wp.requests)
    assert sum(1 for r in fake_wp.requests if (r.method, wp_path(r)) == target) == 1
    if result is not None and step in ("run", "meta"):
        assert result.written is False


@pytest.mark.parametrize(
    "base_url",
    [
        "https://example.com/wp-json/code-snippets/v1/snippets#",
        "https://example.com/?rest_route=/code-snippets/v1/snippets&x=",
        "https://example.com/wp-json/prometal/v1/purge?",
    ],
)
def test_base_url_cannot_turn_allowed_route_into_another(base_url):
    """Đường được kiểm là phần ghép SAU ``base_url``; ``base_url`` có ``#`` hay ``?`` thì
    phần đó thành fragment/query và request thật đi tới đường nhạy cảm."""
    fake = FakeWordPress()
    for path in ("/wp-json/code-snippets/v1/snippets", "/wp-json/prometal/v1/purge", "/"):
        fake.on("POST", path, {"id": 5, "status": "draft"})
    try:
        client = WordPressClient(base_url, "lam", PASSWORD, session=make_session(fake))
        client.create_draft("A", "<p>B</p>")
    except WordPressError:
        pass
    for request in fake.requests:
        # T-061: lệnh tạo nháp có thêm ``?_fields=`` cố định; LC-T061-5: so cả đường và truy vấn.
        url = urlsplit(request.url)
        assert url.path == "/wp-json/wp/v2/posts", request.url
        assert parse_qs(url.query) == {"_fields": ["id,status,title,link,featured_media"]}, url


# ================================================================ chặn chữ SEO


@pytest.mark.parametrize(
    "text",
    [
        "Giảm 10&#037; hôm nay",
        "Giảm 10&#x0025; hôm nay",
        "Giảm 10&#x25 hôm nay",
        "&percnt;&percnt;sitetitle&percnt;&percnt;",
        "Cửa &LT;b&GT;",
        "Cửa ＆#37;",  # & toàn khổ
        "Cửa &＃37;",  # # toàn khổ
        "Giảm 10&#３７; hôm nay",  # chữ số toàn khổ (NFKC thành &#37;)
        "%​%sitetitle%​%",  # ký tự vô hình chen giữa
        "%­%",  # gạch nối mềm
        "﹪﹪",  # % nhỏ
        "%ㅤ%",  # ký tự trắng Hangul (bị normalize_meta bỏ)
        "<ㅤscript>",
        "<­script>",
        "﹤script﹥",  # < > nhỏ
        "Cửa\x07sắt",
        "Cửa\x1bsắt",
        "Cửa\x9bsắt",
    ],
)
@pytest.mark.parametrize("field", ["title", "description", "focus_keyword"])
def test_more_bad_text_is_blocked_before_any_request(fake_wp, client, text, field):
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError) as err:
        client.set_seo_meta(42, **{field: text})
    assert len(fake_wp.requests) == before
    assert text not in str(err.value)


@pytest.mark.parametrize("text", ["Cửa &ltscript&gt", "Cửa &lt b &gt", "Giá &amp rẻ", "&copy 2026"])
def test_legacy_entities_without_semicolon_are_blocked(fake_wp, client, text):
    """Trình duyệt vẫn giải mã ``&lt``, ``&gt``, ``&amp``, ``&copy``… thiếu ``;`` (danh sách
    tên cũ của HTML), như ``&#37`` mà Thợ Máy đã chặn. Điều kiện LC-T036-3 là chặn thực thể."""
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError):
        client.set_seo_meta(42, title=text)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("text", ["R&D", "A & B", "a&#", "Giá & ưu đãi", "AT&T"])
def test_ampersand_without_entity_still_passes(fake_wp, client, text):
    site(fake_wp)
    created(client)
    assert client.set_seo_meta(42, title=text).written


def test_whitespace_like_control_chars_become_spaces_not_sent_raw(fake_wp, client):
    """\\x1c-\\x1f, U+2028 là khoảng trắng với ``str.split``: được đổi thành dấu cách."""
    site(fake_wp)
    created(client)
    assert client.set_seo_meta(42, title="Cửa\x1csắt Pro").written
    assert body(writes(fake_wp)[-1])["input"]["title"] == "Cửa sắt Pro"


# ================================================================ kết quả Abilities mơ hồ


@pytest.mark.parametrize(
    "answer",
    [
        {"success": "false"},
        {"success": 0},
        {"code": "rest_forbidden", "message": "x", "data": {"status": 403}},
        [],
        "ok",
        None,
    ],
)
def test_ability_answer_without_confirmation_is_not_written(fake_wp, client, answer):
    """``_seo_via_abilities`` chỉ coi là lỗi khi ``success is False``. Câu trả lời 200 dạng
    lỗi WP (``code``/``message``), ``"false"``, ``0``, rỗng… vẫn thành "Đã ghi SEO" nên
    người dùng không chép tay và bài đăng thiếu SEO."""
    site(fake_wp, run=(200, answer, {}))
    created(client)
    assert client.set_seo_meta(42, title=TITLE).written is False

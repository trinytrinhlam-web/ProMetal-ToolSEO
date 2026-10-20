"""T-042: ``WordPressClient.set_seo_meta`` ghi meta SEO (SiteSEO) lên bài NHÁP app vừa tạo.

Chỉ dùng site giả (``FakeWordPress``), không bao giờ gọi WordPress thật. Trọng tâm (Lá Chắn):
- chỉ bài trong ``_created_post_ids`` và site xác nhận còn là nháp; bài đã đăng thì từ chối;
- không bao giờ gửi ``null``, không gửi ``status``;
- chặn thẻ HTML, mã ký tự HTML, ``%%`` trước khi gửi;
- câu lỗi cố định, không chép lời máy chủ;
- ghi SEO là tùy chọn, mặc định tắt; site chưa cho ghi thì quay về chép tay, không ném lỗi.
"""

import json

import pytest
import requests
from fake_wordpress import BASE_URL, make_session, query

from seo_app.wordpress import SeoWriteResult, WordPressClient, WordPressError, is_allowed_route

ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
POST_42 = "/wp-json/wp/v2/posts/42"
SERVER_SECRET = "<b>chuỗi lạ từ máy chủ</b> /home/site/wp-config.php"
META_KEYS = {"_siteseo_titles_title": "", "_siteseo_titles_desc": ""}
TITLE = "Cửa sắt 2 cánh: 6 dấu hiệu cần thay | Pro-Metal"
DESC = "Bánh xe kêu, cửa kẹt, ray mòn? Đây là 6 dấu hiệu cho thấy cửa sắt nhà bạn cần sửa ngay."
KEYWORD = "sửa cửa sắt"


def body(request):
    return json.loads(request.body) if request.body else None


def writes(fake_wp):
    return [r for r in fake_wp.requests if r.method != "GET"]


@pytest.fixture
def client(fake_wp):
    return WordPressClient(
        BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp), write_seo=True
    )


def site(fake_wp, *, status="draft", meta=None, ability=None, run=None):
    """Site giả: bài nháp 42 do app tạo; ability bật (mặc định) hoặc theo tham số."""
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (201, {"id": 42, "status": "draft"}, {}))
    fake_wp.on(
        "GET",
        POST_42,
        {"id": 42, "status": status, "meta": dict(META_KEYS) if meta is None else meta},
    )
    fake_wp.on("GET", ABILITY, ability if ability is not None else {"name": "siteseo-posts/"
                                                                     "seo-data-update"})
    fake_wp.on("POST", RUN, run if run is not None else {"success": True})


def created(client):
    post = client.create_draft("Tiêu đề", "<p>Nội dung</p>")
    assert post.id == 42
    return post.id


def walk(value):
    """Mọi giá trị lồng trong JSON."""
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


# ------------------------------------------------------------ tùy chọn mặc định tắt


def test_seo_write_is_off_by_default(fake_wp, wp_client):
    site(fake_wp)
    created(wp_client)
    before = len(fake_wp.requests)
    result = wp_client.set_seo_meta(42, title=TITLE, description=DESC)
    assert result == SeoWriteResult(False, reason="disabled", message=result.message)
    assert "chép" in result.message
    assert len(fake_wp.requests) == before  # không gửi gì thêm
    assert wp_client.write_seo is False


@pytest.mark.parametrize("value", [1, "yes", "true", [True]])
def test_only_real_true_turns_seo_write_on(value):
    client = WordPressClient(BASE_URL, "lam", "abcd", write_seo=value)
    assert client.write_seo is False


def test_from_settings_passes_write_seo():
    from seo_app.config import Settings

    settings = Settings(
        wordpress_url=BASE_URL, wordpress_username="lam", wordpress_app_password="abcd"
    )
    assert WordPressClient.from_settings(settings).write_seo is False
    assert WordPressClient.from_settings(settings, write_seo=True).write_seo is True


# ------------------------------------------------------------ chỉ bài app tạo


@pytest.mark.parametrize("post_id", [810, 1, 43, 0, -42])
def test_post_not_created_by_app_is_refused_without_any_request(fake_wp, client, post_id):
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_seo_meta(post_id, title=TITLE)
    assert len(fake_wp.requests) == before


@pytest.mark.parametrize("post_id", ["42", 42.0, True, None, [42]])
def test_post_id_must_be_a_real_int(fake_wp, client, post_id):
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError):
        client.set_seo_meta(post_id, title=TITLE)
    assert len(fake_wp.requests) == before


def test_refused_even_when_option_is_off(fake_wp, wp_client):
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        wp_client.set_seo_meta(810, title=TITLE)
    assert fake_wp.requests == []


def test_new_client_knows_no_post(fake_wp, client):
    """Bài app tạo ở lần làm việc trước (client khác) cũng không ghi được."""
    site(fake_wp)
    with pytest.raises(WordPressError):
        client.set_seo_meta(42, title=TITLE)
    assert fake_wp.requests == []


@pytest.mark.parametrize("status", ["publish", "future", "pending", "private", "trash", "Draft"])
def test_create_draft_answer_not_draft_is_not_recorded(fake_wp, client, status):
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (201, {"id": 42, "status": status}, {}))
    client.create_draft("A", "B")
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_seo_meta(42, title=TITLE)
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 9)
    assert len(fake_wp.requests) == 1


# ------------------------------------------------------------ không ghi bài đã đăng


@pytest.mark.parametrize(
    "status", ["publish", "future", "pending", "private", "trash", "Draft", " draft", None, 1]
)
def test_post_no_longer_draft_on_site_is_refused(fake_wp, client, status):
    """Người dùng đã đăng bài trong trang quản trị giữa chừng: không ghi gì."""
    site(fake_wp, status=status)
    created(client)
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword=KEYWORD)
    assert [r.method for r in writes(fake_wp)] == ["POST"]  # chỉ lệnh tạo nháp
    assert all(r.path_url != RUN for r in fake_wp.requests)
    # Từ đó bài này không còn được coi là "bài app được sửa", kể cả ảnh đại diện.
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        client.set_seo_meta(42, title=TITLE)
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 9)


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 810, "status": "draft"},
        {"id": "42", "status": "draft"},
        {"id": True, "status": "draft"},
        {"status": "draft"},
        [{"id": 42, "status": "draft"}],
        "draft",
    ],
)
def test_site_answer_for_other_post_is_refused(fake_wp, client, answer):
    site(fake_wp)
    fake_wp.on("GET", POST_42, answer)
    created(client)
    with pytest.raises(WordPressError, match="không còn là bản nháp"):
        client.set_seo_meta(42, title=TITLE)
    assert len(writes(fake_wp)) == 1


def test_draft_check_reads_edit_context_only(fake_wp, client):
    site(fake_wp)
    created(client)
    client.set_seo_meta(42, title=TITLE)
    check = next(r for r in fake_wp.requests if r.method == "GET" and r.path_url.startswith(
        POST_42))
    assert query(check)["context"] == ["edit"]
    assert query(check)["_fields"] == ["id,status,meta"]
    assert check.body is None


@pytest.mark.parametrize("status", [401, 403, 404, 500, 502])
def test_draft_check_failure_raises_fixed_message(fake_wp, client, status):
    site(fake_wp)
    fake_wp.on("GET", POST_42, (status, {"code": "x", "message": SERVER_SECRET}, {}))
    created(client)
    with pytest.raises(WordPressError) as err:
        client.set_seo_meta(42, title=TITLE)
    message = str(err.value)
    assert "chuỗi lạ" not in message and "wp-config" not in message and "<b>" not in message
    assert f"mã {status}" in message
    assert err.value.status_code == status
    assert len(writes(fake_wp)) == 1


def test_draft_check_network_error_raises_fixed_message(fake_wp, client):
    site(fake_wp)
    fake_wp.on(
        "GET", POST_42, lambda _r: requests.exceptions.ConnectionError("https://lam:abcd@x")
    )
    created(client)
    with pytest.raises(WordPressError) as err:
        client.set_seo_meta(42, title=TITLE)
    assert "abcd" not in str(err.value)
    assert len(writes(fake_wp)) == 1


# ------------------------------------------------------------ đường chính: Abilities


def test_writes_through_abilities(fake_wp, client):
    site(fake_wp)
    created(client)
    result = client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword=KEYWORD)

    assert result.written is True
    assert result.route == "abilities"
    assert result.fields == ("title", "description", "focus_keyword")
    assert result.reason == ""
    run = writes(fake_wp)[-1]
    assert run.path_url == RUN
    assert body(run) == {
        "input": {
            "postId": 42,
            "title": TITLE,
            "description": DESC,
            "focus_keyphrase": KEYWORD,
        }
    }
    # Không có lệnh ghi nào vào wp/v2/posts/42 khi đi đường Abilities. (T-061: lệnh tạo nháp có
    # thêm ``?_fields=`` cố định, nên so phần đường.)
    assert [r.path_url.split("?")[0] for r in writes(fake_wp)] == ["/wp-json/wp/v2/posts", RUN]


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"title": TITLE}, {"title": TITLE}),
        ({"description": DESC}, {"description": DESC}),
        ({"focus_keyword": KEYWORD}, {"focus_keyphrase": KEYWORD}),
        ({"title": TITLE, "description": "", "focus_keyword": None}, {"title": TITLE}),
        ({"title": "   ", "description": DESC}, {"description": DESC}),
        ({"title": "​\n", "focus_keyword": KEYWORD}, {"focus_keyphrase": KEYWORD}),
    ],
)
def test_only_fields_with_text_are_sent(fake_wp, client, kwargs, expected):
    site(fake_wp)
    created(client)
    result = client.set_seo_meta(42, **kwargs)
    assert result.written
    assert body(writes(fake_wp)[-1]) == {"input": {"postId": 42, **expected}}


@pytest.mark.parametrize("kwargs", [{}, {"title": ""}, {"title": None, "description": "  "}])
def test_nothing_to_write_is_refused(fake_wp, client, kwargs):
    site(fake_wp)
    created(client)
    with pytest.raises(WordPressError, match="Chưa có"):
        client.set_seo_meta(42, **kwargs)
    assert len(fake_wp.requests) == 1


def test_text_is_normalized_before_sending(fake_wp, client):
    site(fake_wp)
    created(client)
    nfd = "Cửa sắt"  # "Cửa sắt" dạng tổ hợp (dán từ Mac)
    client.set_seo_meta(42, title=f"  {nfd}\n​ 2 cánh  ")
    assert body(writes(fake_wp)[-1])["input"]["title"] == "Cửa sắt 2 cánh"


ALL_COMBOS = [
    {"title": TITLE},
    {"description": DESC},
    {"focus_keyword": KEYWORD},
    {"title": TITLE, "description": DESC, "focus_keyword": KEYWORD},
    {"title": None, "description": DESC, "focus_keyword": ""},
]


@pytest.mark.parametrize("kwargs", ALL_COMBOS)
@pytest.mark.parametrize("route", ["abilities", "meta"])
def test_never_sends_null_or_status(fake_wp, client, kwargs, route):
    """Gửi ``null`` cho SiteSEO là xóa meta; gửi ``status`` có thể đổi trạng thái bài."""
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}) if route == "meta" else None)
    fake_wp.on("POST", POST_42, lambda r: {"id": 42, "status": "draft", **body(r)})
    created(client)
    client.set_seo_meta(42, **kwargs)
    for request in writes(fake_wp)[1:]:
        sent = body(request)
        assert all(value is not None for value in walk(sent)), sent
        assert all(
            "status" not in value for value in walk(sent) if isinstance(value, dict)
        ), sent
        assert "canonical_url" not in json.dumps(sent) and "robots" not in json.dumps(sent)


def test_ability_detection_is_remembered(fake_wp, client):
    site(fake_wp)
    created(client)
    client.set_seo_meta(42, title=TITLE)
    client.set_seo_meta(42, description=DESC)
    detections = [r for r in fake_wp.requests if r.method == "GET" and r.path_url == ABILITY]
    assert len(detections) == 1
    assert detections[0].body is None


@pytest.mark.parametrize(
    "ability",
    [
        {"name": "siteseo-posts/seo-data-get"},
        {"name": "khac"},
        {},
        [],
        "siteseo-posts/seo-data-update",
        (404, {"code": "rest_ability_not_found", "message": SERVER_SECRET}, {}),
        (403, {"code": "rest_forbidden", "message": SERVER_SECRET}, {}),
        (401, {"code": "rest_forbidden", "message": SERVER_SECRET}, {}),
    ],
)
def test_no_ability_means_no_ability_call(fake_wp, client, ability):
    site(fake_wp, ability=ability, meta={})
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "unavailable"
    assert all(r.path_url != RUN for r in fake_wp.requests)
    assert len(writes(fake_wp)) == 1  # meta chưa mở: không gửi gì


@pytest.mark.parametrize("status", [400, 403, 404, 500, 503])
def test_ability_error_gives_fixed_message(fake_wp, client, status):
    site(fake_wp, run=(status, {"code": "x", "message": SERVER_SECRET}, {}))
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "error"
    assert result.route == "abilities"
    assert result.status_code == status
    assert f"mã {status}" in result.message
    assert "chuỗi lạ" not in result.message and "wp-config" not in result.message


def test_ability_network_error_gives_fixed_message(fake_wp, client):
    site(fake_wp, run=lambda _r: requests.exceptions.ReadTimeout("Authorization: Basic abcd"))
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.reason == "error"
    assert "abcd" not in result.message


@pytest.mark.parametrize(
    "run", [{"success": False, "message": SERVER_SECRET}, (200, b"<html>", {})]
)
def test_ability_answer_saying_failure_is_an_error(fake_wp, client, run):
    site(fake_wp, run=run)
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "error"
    assert "chuỗi lạ" not in result.message


def test_ability_detection_server_error_is_retried_later(fake_wp, client):
    site(fake_wp, ability=(500, {"code": "x"}, {}), meta={})
    created(client)
    assert client.set_seo_meta(42, title=TITLE).reason == "unavailable"
    fake_wp.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    assert client.set_seo_meta(42, title=TITLE).written is True


# ------------------------------------------------------------ đường dự phòng: meta


def echo_meta(request):
    return {"id": 42, "status": "draft", "meta": {**META_KEYS, **body(request)["meta"]}}


def test_falls_back_to_meta_when_abilities_off(fake_wp, client):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on("POST", POST_42, echo_meta)
    created(client)
    result = client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword=KEYWORD)
    assert result.written is True
    assert result.route == "meta"
    assert result.fields == ("title", "description")
    assert "Từ khóa chính chưa ghi được" in result.message
    assert body(writes(fake_wp)[-1]) == {
        "meta": {"_siteseo_titles_title": TITLE, "_siteseo_titles_desc": DESC}
    }


def test_meta_route_only_sends_given_field(fake_wp, client):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on("POST", POST_42, echo_meta)
    created(client)
    result = client.set_seo_meta(42, description=DESC)
    assert result.written and result.fields == ("description",)
    assert result.message == "Đã ghi SEO vào hộp SiteSEO của bài nháp."
    assert body(writes(fake_wp)[-1]) == {"meta": {"_siteseo_titles_desc": DESC}}


@pytest.mark.parametrize(
    "meta", [{}, None, [], {"_siteseo_titles_title": ""}, {"_siteseo_titles_desc": ""}]
)
def test_meta_route_needs_both_keys_open(fake_wp, client, meta):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": meta})
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.reason == "unavailable"
    assert len(writes(fake_wp)) == 1


def test_meta_route_cannot_write_keyword_alone(fake_wp, client):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    created(client)
    assert client.set_seo_meta(42, focus_keyword=KEYWORD).reason == "unavailable"
    assert len(writes(fake_wp)) == 1


@pytest.mark.parametrize("status", [400, 401, 403])
def test_meta_route_refused_by_site_falls_back_silently(fake_wp, client, status):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on(
        "POST", POST_42, (status, {"code": "rest_cannot_update", "message": SERVER_SECRET}, {})
    )
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "unavailable"
    assert "chuỗi lạ" not in result.message


@pytest.mark.parametrize("status", [404, 500, 502])
def test_meta_route_server_error_gives_fixed_message(fake_wp, client, status):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on("POST", POST_42, (status, {"code": "x", "message": SERVER_SECRET}, {}))
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.reason == "error"
    assert result.route == "meta"
    assert "chuỗi lạ" not in result.message and "wp-config" not in result.message


@pytest.mark.parametrize(
    "answer",
    [
        {"id": 42, "status": "draft", "meta": dict(META_KEYS)},  # không lưu
        {"id": 42, "status": "draft"},
        {"id": 42, "status": "draft", "meta": {"_siteseo_titles_title": "khác"}},
    ],
)
def test_meta_route_not_saved_is_not_reported_as_written(fake_wp, client, answer):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}))
    fake_wp.on("POST", POST_42, answer)
    created(client)
    result = client.set_seo_meta(42, title=TITLE)
    assert result.written is False
    assert result.reason == "unavailable"


# ------------------------------------------------------------ chặn chữ trước khi gửi


@pytest.mark.parametrize(
    "text",
    [
        "&#37;&#37;sitetitle&#37;&#37;",
        "Cửa &lt;script&gt;alert(1)&lt;/script&gt;",
        "Cửa sắt &amp; nhôm",
        "Giảm 10&#x25; hôm nay",
        "Giảm 10&#37 hôm nay",  # thiếu ";" trình duyệt vẫn giải mã
        "Giảm 10&#X25 hôm nay",
        "Cửa ＆lt;b＞",  # "&" toàn khổ (NFKC thành "&")
        "Cửa &nbsp; sắt",
        "<b>Cửa sắt</b>",
        "Cửa <script>alert(1)</script>",
        "Cửa ＜script＞",  # "<" toàn khổ
        "<​script>",  # ký tự vô hình chen giữa
        "%%sitetitle%%",
        "％％sitetitle％％",
        "Cửa\x00sắt",
        "Cửa\x7fsắt",
    ],
)
@pytest.mark.parametrize("field", ["title", "description", "focus_keyword"])
def test_bad_text_is_blocked_before_any_request(fake_wp, client, text, field):
    site(fake_wp)
    created(client)
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError) as err:
        client.set_seo_meta(42, **{field: text})
    assert len(fake_wp.requests) == before
    assert text not in str(err.value)  # câu cố định, không chép chữ người dùng


@pytest.mark.parametrize(
    ("field", "limit"), [("title", 200), ("description", 500), ("focus_keyword", 200)]
)
def test_too_long_text_is_blocked(fake_wp, client, field, limit):
    site(fake_wp)
    created(client)
    with pytest.raises(WordPressError, match="quá dài"):
        client.set_seo_meta(42, **{field: "a" * (limit + 1)})
    assert client.set_seo_meta(42, **{field: "a" * limit}).written


@pytest.mark.parametrize("value", [123, b"bytes", ["a"], {"a": 1}])
def test_non_text_is_blocked(fake_wp, client, value):
    site(fake_wp)
    created(client)
    with pytest.raises(WordPressError, match="phải là chữ"):
        client.set_seo_meta(42, title=value)
    assert len(fake_wp.requests) == 1


@pytest.mark.parametrize(
    "text",
    [
        "Giá cửa sắt < 5 triệu? Xem ngay",
        "Cửa sắt & nhôm Pro-Metal",
        "Giảm 10% hôm nay",
        "Q&A: sửa cửa sắt",
        "Cửa sắt 2 cánh | Pro-Metal",
    ],
)
def test_ordinary_text_passes(fake_wp, client, text):
    site(fake_wp)
    created(client)
    assert client.set_seo_meta(42, title=text).written
    assert body(writes(fake_wp)[-1])["input"]["title"] == text


# ------------------------------------------------------------ check_connection


ROOT = {"name": "ProMetal", "home": BASE_URL, "namespaces": ["wp/v2", "wp-abilities/v1"]}
ME = {"name": "Phần mềm SEO", "roles": ["editor"], "capabilities": {"edit_posts": True}}


@pytest.mark.parametrize(
    ("ability", "expected", "label"),
    [
        ({"name": "siteseo-posts/seo-data-update"}, True, "ghi được"),
        ((404, {"code": "rest_ability_not_found"}, {}), False, "chưa bật"),
        ((404, {"code": "rest_no_route"}, {}), False, "chưa bật"),
        ((403, {"code": "rest_forbidden"}, {}), False, "chưa bật"),
        ({"name": "khac"}, False, "chưa bật"),
        ((500, {"code": "x", "message": SERVER_SECRET}, {}), None, "chưa dò được"),
        (lambda _r: requests.exceptions.ConnectionError("abcd"), None, "chưa dò được"),
        ((200, b"<html>", {}), None, "chưa dò được"),
    ],
)
def test_check_connection_reports_siteseo(fake_wp, wp_client, ability, expected, label):
    fake_wp.on("GET", "/wp-json/", ROOT)
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", ME)
    fake_wp.on("GET", ABILITY, ability)
    info = wp_client.check_connection()
    assert info.siteseo_writable is expected
    assert info.siteseo_status.startswith("SiteSEO: ")
    assert label in info.siteseo_status
    assert "chuỗi lạ" not in info.siteseo_status
    assert all(r.method == "GET" for r in fake_wp.requests)


def test_connection_info_default_siteseo_unknown():
    from seo_app.wordpress import ConnectionInfo

    info = ConnectionInfo("a", "b", "c", (), True, True, True)
    assert info.siteseo_writable is None
    assert "chưa dò được" in info.siteseo_status


# ------------------------------------------------------------ chỉ đi đường được phép


@pytest.mark.parametrize("route", ["abilities", "meta"])
def test_every_request_is_on_the_allowed_list(fake_wp, client, route):
    site(fake_wp, ability=(404, {"code": "rest_no_route"}, {}) if route == "meta" else None)
    fake_wp.on("POST", POST_42, echo_meta)
    created(client)
    client.set_seo_meta(42, title=TITLE, description=DESC, focus_keyword=KEYWORD)
    for request in fake_wp.requests:
        path = request.path_url.split("?", 1)[0].removeprefix("/wp-json")
        assert is_allowed_route(request.method, path), (request.method, path)
        assert "code-snippets" not in request.url and "prometal" not in request.url

"""T-115 (Thợ Máy): ``release_draft`` so ``modified_gmt`` ngay trước lệnh chuyển (LC-T094-23).

Client nhớ ``modified_gmt`` website trả sau mỗi lệnh ghi của **chính nó** vào bài nháp (tạo nháp,
ảnh đại diện, ghi meta SEO dự phòng); lệnh ``GET`` kiểm nháp ngay trước lệnh chuyển so lại. Khác,
thiếu, sai dạng, hay bài bị sửa ngoài app giữa hai lệnh ghi → ``ReleaseError`` câu cố định, bài vẫn
là nháp, **không** gửi lệnh chuyển. Chỉ site giả (``FakeWordPress``), không gọi WordPress thật.
"""

from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL, FakeWordPress, make_session, query, siteseo_seo_answer
from test_wordpress_release import (  # noqa: F401  (``fixed_clock``: fixture tự dùng, đồng hồ máy cố định)
    LINK,
    NOW,
    POST_42,
    POSTS,
    STAMP,
    TOMORROW,
    body,
    fixed_clock,
    http_date,
)

from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import _RELEASE_CHANGED, ReleaseError

T1 = "2026-11-02T00:50:00"  # giờ sửa sau khi tạo nháp
T2 = "2026-11-02T00:55:00"  # sau lệnh ghi thứ hai của app
T_OTHER = "2026-11-02T00:58:30"  # ai đó sửa ngoài app
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
MEDIA_7 = 7


@pytest.fixture
def fake() -> FakeWordPress:
    return FakeWordPress()


def make_client(fake: FakeWordPress, **kwargs) -> WordPressClient:
    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake), **kwargs)


@pytest.fixture
def client(fake) -> WordPressClient:
    return make_client(fake)


def created(client: WordPressClient, fake: FakeWordPress, modified: object = T1) -> int:
    answer = {"id": 42, "status": "draft", "title": {"raw": "Bài"}}
    if modified is not None:
        answer["modified_gmt"] = modified
    fake.on("POST", POSTS, answer)
    assert client.create_draft("Bài", "<p>Nội dung</p>").id == 42
    fake.requests.clear()
    return 42


class Site:
    """Bài 42 trên site giả có trạng thái: ``GET`` trả ``modified`` hiện tại, mỗi lệnh ghi của app
    (ảnh đại diện, meta) đổi ``modified`` sang giá trị kế tiếp trong ``after_writes``; lệnh chuyển
    trả đúng trạng thái đã gửi."""

    def __init__(self, fake: FakeWordPress, modified: object = T1, after_writes=(T2,)) -> None:
        self.modified = modified
        self.after = list(after_writes)
        self.released = 0
        fake.on("GET", POST_42, self._get)
        fake.on("POST", POST_42, self._post)

    def _answer(self, extra=None):
        data = {"id": 42, "status": "draft", **(extra or {})}
        if self.modified is not None:
            data["modified_gmt"] = self.modified
        return data

    def _get(self, request):
        meta = {"_siteseo_titles_title": "", "_siteseo_titles_desc": ""}
        return 200, self._answer({"meta": meta}), {"Date": http_date(NOW)}

    def _post(self, request):
        sent = body(request)
        if "status" in sent:  # lệnh chuyển
            self.released += 1
            return {"id": 42, "link": LINK, "date_gmt": sent.get("date_gmt", STAMP), **sent}
        if self.after:
            self.modified = self.after.pop(0)
        extra = {"meta": sent["meta"]} if "meta" in sent else {"featured_media": MEDIA_7}
        return self._answer(extra)


def methods(fake: FakeWordPress) -> list[tuple[str, str]]:
    return [(r.method, urlsplit(r.url).path) for r in fake.requests]


def release(client: WordPressClient):
    return client.release_draft(42, mode="future", when_utc=TOMORROW)


def assert_refused_still_draft(client: WordPressClient, site: Site) -> None:
    with pytest.raises(ReleaseError) as info:
        release(client)
    error = info.value
    assert str(error) == _RELEASE_CHANGED
    assert not error.unsure and not error.went_public
    assert site.released == 0  # không gửi lệnh chuyển
    with pytest.raises(ReleaseError):  # không trả mã: không chuyển lại được từ client này
        release(client)
    assert site.released == 0


# ============================================================== chuyển khi bài không bị sửa


def test_release_goes_ahead_when_draft_unchanged_since_create(client, fake):
    created(client, fake)
    site = Site(fake, modified=T1)
    done = release(client)
    assert done.status == "future" and site.released == 1
    check = fake.requests[0]
    assert query(check) == {"context": ["edit"], "_fields": ["id,status,modified_gmt"]}


def test_featured_image_and_meta_writes_update_the_remembered_time(client, fake):
    """Lệnh ghi xen giữa cập nhật giá trị nhớ đúng thứ tự (yêu cầu 3)."""
    created(client, fake)
    site = Site(fake, modified=T1, after_writes=(T2, T_OTHER))
    client.set_featured_image(42, MEDIA_7)  # T1 → T2
    assert site.modified == T2
    meta = make_client(fake, write_seo=True)  # client khác: không dùng chung giá trị nhớ
    with pytest.raises(WordPressError):
        meta.set_seo_meta(42, title="Tiêu đề")
    seo = client
    seo.write_seo = True
    fake.on("GET", ABILITY, (404, {}, {}))  # chưa bật Abilities: ghi meta dự phòng
    assert seo.set_seo_meta(42, title="Cửa sắt đẹp").written  # T2 → T_OTHER
    assert site.modified == T_OTHER
    assert release(client).status == "future" and site.released == 1


# ======================================================= không chuyển: bị sửa hay không biết


def test_edited_outside_app_after_last_write_is_not_released(client, fake):
    created(client, fake)
    site = Site(fake, modified=T_OTHER)  # ai đó sửa trong trang quản trị sau khi app tạo nháp
    assert_refused_still_draft(client, site)
    assert methods(fake) == [("GET", POST_42)]  # chỉ lệnh kiểm, không lệnh chuyển


@pytest.mark.parametrize(
    "value",
    [None, "", "2026-11-02 00:50:00", "2026-11-02T00:50:00Z", "2026-11-02T00:50", 1730508600,
     "２０２６-11-02T00:50:00", ["2026-11-02T00:50:00"], {"raw": T1}],
    ids=["thieu", "rong", "dau-cach", "duoi-Z", "thieu-giay", "so", "chu-so-rong", "list", "dict"],
)  # fmt: skip
def test_odd_modified_on_release_check_is_not_released(client, fake, value):
    created(client, fake)
    site = Site(fake, modified=value)
    assert_refused_still_draft(client, site)


@pytest.mark.parametrize("value", [None, "", "2026-11-02 00:50:00", 0])
def test_create_answer_without_modified_means_unknown(client, fake, value):
    created(client, fake, modified=value)
    site = Site(fake, modified=T1)
    assert_refused_still_draft(client, site)


def test_edit_between_app_writes_is_not_laundered_by_next_write(client, fake):
    """Bị sửa ngoài app giữa lúc tạo nháp và lúc đặt ảnh đại diện: lệnh ghi sau trả giờ mới, nhưng
    không được xóa dấu vết lần sửa ngoài app (lần kiểm trước lệnh ghi đã thấy giờ lạ)."""
    created(client, fake)
    site = Site(fake, modified=T_OTHER, after_writes=(T2,))
    client.set_featured_image(42, MEDIA_7)  # ghi vẫn được (bài còn là nháp của app)
    assert site.modified == T2
    assert_refused_still_draft(client, site)


def test_failed_featured_write_means_unknown(client, fake):
    created(client, fake)
    site = Site(fake, modified=T1)
    fake.on("POST", POST_42, (503, {}, {}))
    with pytest.raises(WordPressError):
        client.set_featured_image(42, MEDIA_7)
    fake.on("POST", POST_42, site._post)
    assert_refused_still_draft(client, site)


def test_failed_meta_write_means_unknown(client, fake):
    created(client, fake)
    site = Site(fake, modified=T1)
    client.write_seo = True
    fake.on("GET", ABILITY, (404, {}, {}))
    fake.on("POST", POST_42, (502, {}, {}))
    assert not client.set_seo_meta(42, title="Cửa sắt đẹp").written
    fake.on("POST", POST_42, site._post)
    assert_refused_still_draft(client, site)


def test_abilities_write_keeps_remembered_time(client, fake):
    """Ghi SEO qua Abilities: câu trả lời không có ``modified_gmt``, client giữ giá trị nhớ. Nếu
    Abilities làm đổi ``modified_gmt`` thì lệnh chuyển bị từ chối (an toàn): phải kiểm khi thử thật
    (báo cáo T-115)."""
    created(client, fake)
    site = Site(fake, modified=T1)
    client.write_seo = True
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake.on("POST", ABILITY + "/run", siteseo_seo_answer)
    assert client.set_seo_meta(42, title="Cửa sắt đẹp").written
    assert release(client).status == "future"

    other = make_client(fake, write_seo=True)
    created(other, fake)
    site = Site(fake, modified=T1)
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake.on("POST", ABILITY + "/run", siteseo_seo_answer)
    assert other.set_seo_meta(42, title="Cửa sắt đẹp").written
    site.modified = T2  # giả sử Abilities có đổi giờ sửa: không chuyển (an toàn)
    assert_refused_still_draft(other, site)


def test_two_drafts_and_two_clients_keep_separate_times(fake):
    first, second = make_client(fake), make_client(fake)
    fake.on("POST", POSTS, {"id": 42, "status": "draft", "title": {"raw": "A"},
                            "modified_gmt": T1})  # fmt: skip
    first.create_draft("A", "<p>a</p>")
    fake.on("POST", POSTS, {"id": 43, "status": "draft", "title": {"raw": "B"},
                            "modified_gmt": T2})  # fmt: skip
    first.create_draft("B", "<p>b</p>")
    assert first._modified == {42: T1, 43: T2}
    assert second._modified == {}  # client khác (tab khác) không thấy giá trị của client này


def test_write_fields_ask_for_modified_but_never_rendered_content():
    for fields in (client_module._POST_FIELDS, client_module._POST_META_FIELDS,
                   client_module._RELEASE_CHECK_FIELDS):  # fmt: skip
        assert "modified_gmt" in fields.split(",")
        assert not client_module._asks_rendered_fields(fields)


def test_changed_message_is_fixed_and_says_still_draft():
    assert "bài vẫn là nháp" in _RELEASE_CHANGED
    assert "{" not in _RELEASE_CHANGED and BASE_URL not in _RELEASE_CHANGED

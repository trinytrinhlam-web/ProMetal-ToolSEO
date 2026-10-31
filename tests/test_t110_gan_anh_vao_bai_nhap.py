"""T-110: gắn ảnh «Gửi nháp» vào bài nháp vừa tạo (LC-T093-2, chủ dự án chọn 1A).

Ảnh không gắn bài nào thì WordPress cho người chưa đăng nhập đọc qua danh sách Media
(``GET /wp-json/wp/v2/media``); ảnh của bài nháp thì không, tới khi bài được đăng. Sau khi tạo
nháp và đặt ảnh đại diện, client gửi cho từng ảnh vừa tải một lệnh ``POST /wp/v2/media/<mã>`` thân
chỉ ``{"post": <mã bài nháp>}``.

- Chỉ ảnh chính client vừa tải, chỉ bài nháp chính client vừa tạo; khóa ``post`` chỉ ở đúng
  dạng lệnh gắn ảnh (lớp chặn ``_is_media_attach``).
- Lỗi khi gắn: không tải lại ảnh, không tạo bài thứ hai, không thử lại; kết quả vẫn trả về (bài
  nháp đã có, khóa gửi trùng T-086, T-089 không đổi) kèm câu báo cố định.
- Ảnh đại diện, nội dung, ``srcset`` (T-059) không đổi.

Site giả của Soi Lỗi T-054 (``test_soi_loi_t054.Site``), không gọi WordPress thật.
"""

from __future__ import annotations

import ast
import json
import re

import pytest
import requests
import test_soi_loi_t054 as sl54
from fake_wordpress import BASE_URL, make_session, query

from seo_app.config import PROJECT_ROOT
from seo_app.images.process import make_web_image
from seo_app.images.tags import ImageTags
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import (
    _DRAFT_IMAGE_MAYBE,
    _DRAFT_IMAGE_RETURNED,
    _FEATURED_NOT_SET,
    _IMAGES_NOT_ATTACHED,
    _MEDIA_HAS_PARENT,
    _MEDIA_NOT_CREATED,
    _MEDIA_PARENT_FIELDS,
    _MEDIA_PARENT_UNKNOWN,
    _MEDIA_UPLOAD_FIELDS,
    _ROUTE_BLOCKED,
    DraftImage,
    DraftImagesError,
)

MEDIA = sl54.MEDIA
POSTS = sl54.POSTS
POST_42 = f"{POSTS}/42"
BAIT = "MỒI-máy-chủ <b>evil</b>"


def image(alt: str, *, featured: bool = False) -> DraftImage:
    web = make_web_image(sl54._jpeg(gps=sl54.GPS_NE))
    tags = ImageTags(category="Cổng inox", area="Tân Phú")
    return DraftImage(web, alt=alt, tags=tags, featured=featured)


def two_images() -> list[object]:
    return [
        "<p>Cổng trước khi sửa.</p>",
        image("Cổng inox trước khi sửa"),
        "<p>Cổng sau khi sửa.</p>",
        image("Cổng inox sau khi sửa", featured=True),
    ]


def send(client: WordPressClient, parts=None):
    return client.create_draft_with_images("Sửa cổng inox Tân Phú", parts or two_images())


def attaches(fake_wp) -> list[requests.PreparedRequest]:
    """Lệnh gắn ảnh: ``POST /wp/v2/media/<mã>`` có khóa ``post`` trong thân."""
    return [r for r in sl54.describes(fake_wp) if "post" in (sl54.body(r) or {})]


def steps(fake_wp) -> list[str]:
    names = []
    for request in fake_wp.requests:
        path = sl54.path(request)
        if request.method == "POST" and path == MEDIA:
            names.append("tải ảnh")  # thân là byte ảnh
        elif request.method == "POST" and path.startswith(MEDIA + "/"):
            names.append("gắn ảnh" if "post" in (sl54.body(request) or {}) else "ghi alt")
        elif request.method == "POST" and path == POSTS:
            names.append("tạo nháp")
        elif request.method == "GET" and path == POST_42:
            names.append("kiểm nháp")
        elif request.method == "POST" and path == POST_42:
            names.append("ảnh đại diện")
        else:
            names.append(f"{request.method} {path}")
    return names


@pytest.fixture
def site(fake_wp):
    return sl54.Site(fake_wp)


# ====================================================================== chạy đúng


def test_gan_tung_anh_vao_bai_nhap_truoc_anh_dai_dien(site, fake_wp, wp_client):
    result = send(wp_client)
    assert steps(fake_wp) == [
        "tải ảnh", "ghi alt", "tải ảnh", "ghi alt", "tạo nháp", "gắn ảnh", "gắn ảnh",
        "kiểm nháp", "ảnh đại diện",
    ]
    ids = [img.id for img in result.images]
    assert ids == [101, 102]
    sent = attaches(fake_wp)
    assert [int(sl54.path(r).rsplit("/", 1)[1]) for r in sent] == ids
    for request in sent:
        assert sl54.body(request) == {"post": 42}  # chỉ khóa post, không alt, tiêu đề, trạng thái
        assert query(request) == {"_fields": [_MEDIA_PARENT_FIELDS]}
    assert result.unattached == () and result.message == ""
    assert result.featured_media == 102


def test_noi_dung_srcset_anh_dai_dien_khong_doi(site, fake_wp, wp_client):
    result = send(wp_client)
    content = sl54.sent_content(fake_wp)
    for uploaded in result.images:
        assert f'srcset="{uploaded.source_url} 1x"' in content
    featured = [r for r in fake_wp.requests if r.method == "POST" and sl54.path(r) == POST_42]
    assert [sl54.body(r) for r in featured] == [{"featured_media": 102}]
    assert len(sl54.uploads(fake_wp)) == 2 and len(sl54.creates(fake_wp)) == 1


def test_khong_co_anh_thi_khong_gan_gi(site, fake_wp, wp_client):
    result = send(wp_client, ["<p>Chỉ có chữ.</p>"])
    assert steps(fake_wp) == ["tạo nháp"]
    assert result.unattached == () and result.message == ""


def test_mot_anh_dung_nhieu_lan_chi_gan_mot_lan(site, fake_wp, wp_client):
    same = image("Cổng inox")
    send(wp_client, ["<p>a</p>", same, "<p>b</p>", same])
    assert len(sl54.uploads(fake_wp)) == 1 and len(attaches(fake_wp)) == 1


# ====================================================================== lỗi khi gắn


def _attach_answers(fake_wp, site, answer):
    """Lệnh ghi alt trả như site T-054; lệnh gắn ảnh trả ``answer``."""

    def media(request):
        if "post" in (sl54.body(request) or {}):
            if isinstance(answer, Exception):
                raise answer
            return answer(request) if callable(answer) else answer
        return site.update_media(request)

    for media_id in range(sl54.FIRST_ID, sl54.FIRST_ID + 5):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", media)


@pytest.mark.parametrize(
    "answer",
    [
        pytest.param((403, {"code": "rest_cannot_edit", "message": BAIT}, {}), id="403"),
        pytest.param((400, {"code": "rest_invalid_param", "message": BAIT}, {}), id="400"),
        pytest.param((500, {"code": "x", "message": BAIT}, {}), id="500"),
        pytest.param((302, {}, {"Location": "https://evil.example/"}), id="302"),
        pytest.param(requests.exceptions.ReadTimeout(BAIT), id="het-gio"),
        pytest.param(requests.exceptions.ConnectionError(BAIT), id="mat-mang"),
        pytest.param((200, b"<html>ok</html>", {}), id="khong-phai-json"),
        pytest.param({"id": 101}, id="thieu-post"),
        pytest.param({"id": 101, "post": 0}, id="post-0"),
        pytest.param({"id": 101, "post": 43}, id="post-khac"),
        pytest.param({"id": 101, "post": "42"}, id="post-chu"),
        pytest.param({"id": 999, "post": 42}, id="anh-khac"),
        pytest.param([{"id": 101, "post": 42}], id="danh-sach"),
    ],
)
def test_gan_loi_thi_van_tra_bai_nhap_bao_cau_co_dinh(site, fake_wp, wp_client, answer):
    _attach_answers(fake_wp, site, answer)
    result = send(wp_client)
    assert result.post.id == 42 and result.featured_media == 102
    assert result.unattached == (101, 102)  # dừng ở ảnh đầu, không thử ảnh sau
    assert result.message == _IMAGES_NOT_ATTACHED.format(count=2)
    assert BAIT not in result.message and BASE_URL not in result.message
    assert len(attaches(fake_wp)) == 1  # không thử lại
    assert len(sl54.uploads(fake_wp)) == 2 and len(sl54.creates(fake_wp)) == 1  # không tải lại


def test_gan_anh_sau_loi_thi_bao_dung_so_anh_chua_gan(site, fake_wp, wp_client):
    calls = []

    def second_fails(request):
        calls.append(request)
        if len(calls) == 2:
            return (503, {"code": "x"}, {})
        return site.update_media(request)

    _attach_answers(fake_wp, site, second_fails)
    result = send(wp_client)
    assert result.unattached == (102,)
    assert result.message == _IMAGES_NOT_ATTACHED.format(count=1)


def test_loi_la_khi_gan_khong_thanh_loi_gui_nhap(site, fake_wp, wp_client, monkeypatch):
    original = wp_client._session.request

    def boom(method, url, **kwargs):
        if "post" in (kwargs.get("json") or {}):
            raise RuntimeError(BAIT)
        return original(method, url, **kwargs)

    monkeypatch.setattr(wp_client._session, "request", boom)
    result = send(wp_client)
    assert result.unattached == (101, 102) and BAIT not in result.message


def test_anh_dai_dien_loi_va_gan_duoc_thi_chi_bao_anh_dai_dien(site, fake_wp, wp_client):
    fake_wp.on("POST", POST_42, (500, {"code": "x"}, {}))
    result = send(wp_client)
    assert result.featured_media is None and result.unattached == ()
    assert result.message.startswith(_FEATURED_NOT_SET.split("{reason}")[0])
    assert _IMAGES_NOT_ATTACHED.format(count=2) not in result.message


@pytest.mark.parametrize("status", ["publish", "future", "pending", "private", ""])
def test_site_tao_bai_khong_phai_nhap_thi_khong_gan_anh(fake_wp, wp_client, status):
    """Website trả bài vừa tạo không phải nháp: client không coi là bài của mình, nên không gắn
    ảnh vào bài đó (0 lệnh gắn, 0 lệnh nào sau lệnh tạo); câu báo nói cả hai việc."""
    sl54.Site(fake_wp, post_status=status)
    result = send(wp_client)
    assert attaches(fake_wp) == []
    assert fake_wp.requests[-1] is sl54.creates(fake_wp)[0]
    assert result.unattached == (101, 102) and result.featured_media is None
    assert result.message.startswith(_FEATURED_NOT_SET.split("{reason}")[0])
    assert result.message.endswith(_IMAGES_NOT_ATTACHED.format(count=2))


def test_bai_bi_dang_sau_luc_gan_thi_anh_dai_dien_bao_loi(fake_wp, wp_client):
    """Ảnh gắn ngay sau lệnh tạo; lệnh kiểm nháp trước ảnh đại diện thấy bài đã bị đăng ngoài app:
    không đặt ảnh đại diện, báo như cũ."""
    sl54.Site(fake_wp)
    fake_wp.on("GET", POST_42, {"id": 42, "status": "publish"})
    result = send(wp_client)
    assert len(attaches(fake_wp)) == 2 and result.unattached == ()
    assert result.featured_media is None
    assert result.message.startswith(_FEATURED_NOT_SET.split("{reason}")[0])
    assert _IMAGES_NOT_ATTACHED.format(count=2) not in result.message


# ====================================================================== chỉ ảnh, bài của client


def test_chi_gan_anh_client_vua_tai_vao_bai_client_vua_tao(site, fake_wp, wp_client):
    send(wp_client)
    fake_wp.requests.clear()
    for media_id, post_id in [(999, 42), (101, 43), (101, True), (True, 42), ("101", 42)]:
        with pytest.raises(WordPressError, match="vừa tải vào bài nháp"):
            wp_client._attach_media(media_id, post_id)
    other = WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))
    with pytest.raises(WordPressError, match="vừa tải vào bài nháp"):
        other._attach_media(101, 42)
    assert fake_wp.requests == []


def test_anh_khong_duoc_xac_nhan_vua_tao_thi_khong_thanh_anh_cua_client(fake_wp, wp_client):
    """Website trả mã khác 201 (ảnh có sẵn, plugin trả lại ảnh trùng): không vào tập ảnh gắn."""
    fake_wp.on("POST", MEDIA, (200, {"id": 7, "source_url": f"{sl54.UPLOADS}a.webp"}, {}))
    with pytest.raises(WordPressError):
        wp_client._post_media(b"x", "a.webp", "image/webp", new_only=True)
    assert wp_client._uploaded_media_ids == set()
    # Lệnh tải không đòi «vừa tạo» (new_only tắt) cũng không làm ảnh thành ảnh gắn được.
    fake_wp.on("POST", MEDIA, (201, {"id": 8, "source_url": f"{sl54.UPLOADS}b.webp"}, {}))
    assert wp_client._post_media(b"x", "b.webp", "image/webp")[0] == 8
    assert wp_client._uploaded_media_ids == set()


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        pytest.param("/wp/v2/media/9", {"post": 42, "alt_text": "x"}, id="kem-alt"),
        pytest.param("/wp/v2/media/9", {"post": 42, "status": "draft"}, id="kem-status"),
        pytest.param("/wp/v2/media/9", {"post": "42"}, id="chu"),
        pytest.param("/wp/v2/media/9", {"post": True}, id="bool"),
        pytest.param("/wp/v2/media/9", {"post": 0}, id="khong"),
        pytest.param("/wp/v2/media/9", {"post": -1}, id="am"),
        pytest.param("/wp/v2/media/9", {"post": 2**63}, id="qua-lon"),
        pytest.param("/wp/v2/media/9", {"post": 4.0}, id="so-thuc"),
        pytest.param("/wp/v2/media/9", {"post": None}, id="null"),
        pytest.param("/wp/v2/media/9", {"post": [42]}, id="mang"),
        pytest.param("/wp/v2/media/9", {"Post": 42}, id="hoa"),
        pytest.param("/wp/v2/media/9", {"post_parent": 42}, id="post-parent"),
        pytest.param("/wp/v2/media", {"post": 42}, id="duong-tai-anh"),
        pytest.param("/wp/v2/posts/42", {"post": 41}, id="duong-bai"),
        pytest.param("/wp/v2/posts", {"title": "x", "post": 41}, id="tao-bai"),
        pytest.param(client_module.SITESEO_ABILITY_RUN_PATH, {"post": 42}, id="ability"),
    ],
)
def test_khoa_post_chi_o_dung_dang_lenh_gan_anh(fake_wp, wp_client, path, payload):
    """Ảnh 9 và bài 41, 42 là của client: vẫn chặn vì sai dạng, sai đường (không phải vì sở hữu)."""
    wp_client._uploaded_media_ids.add(9)
    wp_client._created_post_ids.update({41, 42})
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        wp_client._request("POST", path, json=payload)
    assert fake_wp.requests == []


def _own(client: WordPressClient) -> None:
    client._uploaded_media_ids.add(9)
    client._created_post_ids.add(42)


def test_lenh_gan_anh_dung_dang_cua_client_qua_lop_chan(fake_wp, wp_client):
    _own(wp_client)
    fake_wp.on("POST", f"{MEDIA}/9", {"id": 9, "post": 42})
    wp_client._request(
        "POST", "/wp/v2/media/9", json={"post": 42}, params={"_fields": _MEDIA_PARENT_FIELDS}
    )
    (request,) = fake_wp.requests
    assert json.loads(request.body) == {"post": 42}


@pytest.mark.parametrize(
    ("path", "post"),
    [
        pytest.param("/wp/v2/media/10", 42, id="anh-khong-phai-client-tai"),
        pytest.param("/wp/v2/media/9", 43, id="bai-khong-phai-client-tao"),
        pytest.param("/wp/v2/media/10", 43, id="ca-hai-la"),
        pytest.param("/wp/v2/media/9", 9, id="ma-anh-thay-ma-bai"),
    ],
)
def test_lop_chan_chi_nhan_anh_va_bai_cua_chinh_client(fake_wp, wp_client, path, post):
    """Điều kiện 2 của Chỉ Huy (30/10): chặn ngay ở ``_request``, trước khi gửi, không chỉ ở
    ``_attach_media``."""
    _own(wp_client)
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        wp_client._request("POST", path, json={"post": post})
    assert fake_wp.requests == []


def test_client_khac_khong_gan_duoc_anh_bai_cua_client_nay(fake_wp, wp_client):
    _own(wp_client)
    other = WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        other._request("POST", "/wp/v2/media/9", json={"post": 42})
    assert fake_wp.requests == []


def test_chi_attach_media_gui_khoa_post():
    """Đọc mã nguồn client: dict có khóa ``"post"`` chỉ nằm trong ``_attach_media``."""
    source = (PROJECT_ROOT / "seo_app" / "wordpress" / "client.py").read_text(encoding="utf-8")
    found = set()
    for function in ast.walk(ast.parse(source)):
        if not isinstance(function, ast.FunctionDef):
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Dict) and any(
                isinstance(key, ast.Constant) and key.value == "post" for key in node.keys
            ):
                found.add(function.name)
    assert found == {"_attach_media"}


# ====================================================================== lượt 2: LC-T110-1
# Lệnh tải ảnh xin thêm ``post`` (bài cha). Chỉ ảnh website trả ``post`` null/0 (ảnh mới, chưa có
# bài cha) mới là ảnh của client, được gắn; thiếu hay lạ: không gắn (câu báo); số dương (ảnh có
# sẵn thuộc bài khác): từ chối như mã khác 201 (Chỉ Huy duyệt 30/10 20:40, cách A).


def _upload_parent(fake_wp, site, parent, *, drop=False):
    """Lệnh tải ảnh của site T-054, đổi ``post`` thành ``parent`` (``drop``: bỏ hẳn khóa)."""
    create = site.create_media

    def answer(request):
        status, data, headers = create(request)
        data = dict(data)
        if drop:
            data.pop("post", None)
        else:
            data["post"] = parent
        return status, data, headers

    fake_wp.on("POST", MEDIA, answer)


def _describes_only(fake_wp) -> list[dict]:
    return [sl54.body(r) for r in sl54.describes(fake_wp) if "post" not in (sl54.body(r) or {})]


def test_lenh_tai_anh_xin_them_post(site, fake_wp, wp_client):
    send(wp_client)
    for upload in sl54.uploads(fake_wp):
        assert query(upload) == {"_fields": [_MEDIA_UPLOAD_FIELDS]}
    assert _MEDIA_UPLOAD_FIELDS == "id,source_url,alt_text,post"


@pytest.mark.parametrize("parent", [None, 0])
def test_post_null_hay_0_thi_gan(site, fake_wp, wp_client, parent):
    _upload_parent(fake_wp, site, parent)
    result = send(wp_client)
    assert result.unattached == () and result.message == ""
    assert [sl54.body(r) for r in attaches(fake_wp)] == [{"post": 42}, {"post": 42}]


def test_thieu_post_thi_dung_khong_ghi_alt_khong_gan(site, fake_wp, wp_client):
    """T-110 lượt 3 (Chỉ Huy duyệt 31/10 00:45), G4: thiếu ``post`` là ảnh chưa xác nhận của
    client, dừng như số dương."""
    _upload_parent(fake_wp, site, None, drop=True)
    with pytest.raises(DraftImagesError) as caught:
        send(wp_client)
    message = str(caught.value)
    assert message.startswith(_MEDIA_PARENT_UNKNOWN) and _DRAFT_IMAGE_RETURNED in message
    assert sl54.describes(fake_wp) == [] and sl54.creates(fake_wp) == []
    assert len(sl54.uploads(fake_wp)) == 1 and wp_client._uploaded_media_ids == set()


@pytest.mark.parametrize("parent", [7, 1, client_module.MAX_ID])
def test_post_so_duong_la_anh_co_san_tu_choi_nhu_ma_khac_201(site, fake_wp, wp_client, parent):
    """Ảnh website trả về đã thuộc bài ``parent``: không ghi alt, không gắn, không tạo nháp."""
    _upload_parent(fake_wp, site, parent)
    with pytest.raises(DraftImagesError) as caught:
        send(wp_client)
    # T-110 lượt 3 (Chỉ Huy duyệt 31/10 00:45): câu riêng cho ảnh có bài cha.
    assert str(caught.value).startswith(_MEDIA_HAS_PARENT)
    assert sl54.describes(fake_wp) == [] and sl54.creates(fake_wp) == []
    assert len(sl54.uploads(fake_wp)) == 1  # dừng ngay ở ảnh đầu
    assert wp_client._uploaded_media_ids == set()


def test_post_so_duong_o_upload_media_rieng_cung_tu_choi(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": f"{sl54.UPLOADS}a.jpg", "post": 7}, {}))
    # T-110 lượt 3 (Chỉ Huy duyệt 31/10 00:45): câu riêng cho ảnh có bài cha.
    with pytest.raises(WordPressError, match=re.escape(_MEDIA_HAS_PARENT.split(".")[0])):
        wp_client.upload_media(b"\xff\xd8 anh", "a.jpg", alt_text="A")
    assert [sl54.path(r) for r in fake_wp.requests] == [MEDIA]  # không ghi gì vào ảnh 9


@pytest.mark.parametrize(
    "parent",
    ["7", "", "0", True, False, -1, 1.5, 0.0, 2**63, [7], {"id": 7}],
    ids=["chu", "chu-rong", "chu-0", "true", "false", "am", "so-thuc", "0-thuc", "qua-2-63", "mang",
         "dict"],
)
def test_post_sai_kieu_thi_dung_khong_ghi_alt_khong_gan(site, fake_wp, wp_client, parent):
    # T-110 lượt 3 (Chỉ Huy duyệt 31/10 00:45), G4: giá trị lạ dừng như số dương.
    _upload_parent(fake_wp, site, parent)
    with pytest.raises(DraftImagesError) as caught:
        send(wp_client)
    assert str(caught.value).startswith(_MEDIA_PARENT_UNKNOWN)
    assert attaches(fake_wp) == [] and sl54.describes(fake_wp) == []
    assert sl54.creates(fake_wp) == [] and wp_client._uploaded_media_ids == set()


# ====================================================================== lượt 3: SL-T110-2
# Website trả lại ảnh không xác nhận là ảnh mới: câu báo chỉ dặn kiểm, không bảo xóa (ảnh có thể
# là ảnh có sẵn của bài khác). Lỗi mạng, 5xx ở lệnh tải ảnh giữ câu cũ (ảnh mới có thể đã lên).


@pytest.mark.parametrize(
    ("answer", "start"),
    [
        pytest.param((200, {"id": 9, "post": 7}), _MEDIA_NOT_CREATED, id="200"),
        pytest.param((201, {"id": 9, "post": 7}), _MEDIA_HAS_PARENT, id="201-co-cha"),
        pytest.param((201, {"id": 9}), _MEDIA_PARENT_UNKNOWN, id="201-thieu-post"),
    ],
)
def test_anh_website_tra_lai_chi_dan_kiem_khong_bao_xoa(fake_wp, wp_client, answer, start):
    status, data = answer
    fake_wp.on("POST", MEDIA, (status, {**data, "source_url": f"{sl54.UPLOADS}a.webp"}, {}))
    with pytest.raises(DraftImagesError) as caught:
        send(wp_client)
    message = str(caught.value)
    assert message.startswith(start) and message.endswith(_DRAFT_IMAGE_RETURNED)
    assert "xóa" not in message and "cần mã 201" not in message.replace(_MEDIA_NOT_CREATED, "")
    assert caught.value.maybe_uploaded is True and caught.value.uploaded == ()
    assert [sl54.path(r) for r in fake_wp.requests] == [MEDIA]  # không ghi gì vào ảnh 9


def test_loi_may_chu_o_lenh_tai_anh_giu_cau_cu(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (502, {"code": "x"}, {}))
    with pytest.raises(DraftImagesError) as caught:
        send(wp_client)
    assert str(caught.value).endswith(_DRAFT_IMAGE_MAYBE)


# ====================================================================== câu nhắc GPS


def test_cau_nhac_gps_noi_dung_su_that_moi():
    source = (PROJECT_ROOT / "app" / "views" / "write.py").read_text(encoding="utf-8")
    (assign,) = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "GPS_PUBLIC_WARNING" for t in node.targets)
    ]
    text = ast.literal_eval(assign.value)
    assert "xem được công khai" in text  # các test giao diện cũ tìm cụm này ngay trước nút gửi
    assert "đường dẫn trực tiếp" in text
    assert "danh sách Media công khai" in text and "cho tới khi bài được đăng" in text
    assert "không tự xóa" in text

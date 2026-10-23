"""Soi Lỗi · T-071: thử phá phần dọn lỗi Thấp của «gửi nháp kèm ảnh» (sau T-054).

Kiểm độc lập yêu cầu 1–6 của phiếu T-071 (không dùng lại site giả, dữ liệu của Thợ Máy). Chỉ site
giả (``FakeWordPress``), không gọi WordPress thật; ảnh là ảnh giả tạo trong bộ nhớ, tên khách là
tên giả.

Test ``xfail(strict=True)`` là lỗi tìm được (SL-T071-n trong
``docs/team/reports/T-071-soi-loi.md``): sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ
cần xóa dòng ``@pytest.mark.xfail``.
"""

import contextlib
import html
import io
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.images import html as image_html
from seo_app.images.alt import AltSuggestion, clean_suggestion
from seo_app.images.folders import ImageRef
from seo_app.images.naming import image_file_name
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags, TagError, tags_for_image
from seo_app.sanitize import clean_ai_text
from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import DraftImage, DraftImagesError

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@contextlib.contextmanager
def _pillow_state_kept():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif (``make_web_image`` đăng ký
    HEIF khi mở ảnh), như ``tests/test_soi_loi_t054.py``."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _PILLOW_REGISTRIES}
    options = {name: getattr(heif_options, name) for name in _HEIF_OPTIONS}
    try:
        yield
    finally:
        for name, value in saved.items():
            current = getattr(Image, name)
            current.clear()
            if isinstance(current, dict):
                current.update(value)
            else:
                current.extend(value)
        for name, value in options.items():
            setattr(heif_options, name, value)


@pytest.fixture(autouse=True)
def _pillow_state_restored():
    with _pillow_state_kept():
        yield


# ----- dữ liệu giả ---------------------------------------------------------------------------

POSTS = "/wp-json/wp/v2/posts"
MEDIA = "/wp-json/wp/v2/media"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
FIRST_ID = 101
POST_ID = 42
KHOA_GIA = "abcd efgh ijkl"  # khóa giả của fixture ``wp_client``
MAYBE_DRAFT = "Bài nháp có thể vẫn đã được tạo"
NOT_CREATED = "chưa tạo bài nháp"  # so trên chữ đã ``casefold``


def _jpeg(size, color):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG", quality=85)
    return buffer.getvalue()


@pytest.fixture(scope="module")
def images():
    """Ba ảnh WebP do phần mềm tạo (khác cỡ, khác màu)."""
    with _pillow_state_kept():
        return tuple(
            make_web_image(_jpeg(size, color))
            for size, color in (
                ((240, 180), (200, 80, 40)),
                ((180, 240), (30, 120, 200)),
                ((200, 200), (90, 200, 90)),
            )
        )


def path(request):
    return urlsplit(request.url).path


def body(request):
    return json.loads(request.body) if request.body else None


def calls(fake_wp):
    return [(r.method, path(r)) for r in fake_wp.requests]


def created_posts(fake_wp):
    return [r for r in fake_wp.requests if (r.method, path(r)) == ("POST", POSTS)]


def sent_content(fake_wp):
    sent = created_posts(fake_wp)
    assert len(sent) == 1
    return body(sent[0])["content"]


def media_writes(fake_wp, media_id):
    route = ("POST", f"{MEDIA}/{media_id}")
    return [body(r) for r in fake_wp.requests if (r.method, path(r)) == route]


def file_names(fake_wp):
    names = []
    for request in fake_wp.requests:
        if (request.method, path(request)) == ("POST", MEDIA):
            disposition = request.headers["Content-Disposition"]
            names.append(re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1))
    return names


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def json_strings(fake_wp):
    """Mọi chuỗi trong mọi lệnh JSON gửi WordPress (nội dung, tiêu đề, alt, chú thích…)."""
    for request in fake_wp.requests:
        if "json" in request.headers.get("Content-Type", ""):
            yield from _strings(body(request))


class _Page(HTMLParser):
    """Đọc HTML như trình duyệt: thuộc tính ``<img>`` (đã giải mã) và chữ trong ``<figcaption>``."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.imgs = []
        self.captions = []
        self._caption = None
        self.feed(content)
        self.close()

    @property
    def alts(self):
        return [img.get("alt") for img in self.imgs]

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.imgs.append(dict(attrs))
        elif tag == "figcaption":
            self._caption = []

    def handle_data(self, data):
        if self._caption is not None:
            self._caption.append(data)

    def handle_endtag(self, tag):
        if tag == "figcaption" and self._caption is not None:
            self.captions.append("".join(self._caption))
            self._caption = None


class Site:
    """Site giả: Media cấp mã từ 101, bài nháp 42.

    ``faults``: lỗi cài sẵn theo bước, khóa ``("upload", n)`` (lệnh tải ảnh thứ n),
    ``("describe", n)`` (lệnh ghi alt thứ n), ``("create",)`` (lệnh tạo nháp). Giá trị là ngoại lệ
    (ném ra như lỗi mạng) hoặc câu trả lời ``(mã, nội dung, header)``.
    """

    def __init__(self, fake_wp, faults=None):
        self.faults = dict(faults or {})
        self.next_id = FIRST_ID
        self.counts = {"upload": 0, "describe": 0}
        self.files = {}
        fake_wp.on("POST", MEDIA, self.create_media)
        for media_id in range(FIRST_ID, FIRST_ID + 10):
            fake_wp.on("POST", f"{MEDIA}/{media_id}", self.update_media)
        fake_wp.on("POST", POSTS, self.create_post)
        fake_wp.on("GET", f"{POSTS}/{POST_ID}", lambda _r: {"id": POST_ID, "status": "draft"})
        fake_wp.on("POST", f"{POSTS}/{POST_ID}", self.update_post)

    def _fault(self, step):
        if step not in self.faults:
            return None
        answer = self.faults[step]
        if isinstance(answer, BaseException):
            raise answer
        return answer

    def source_url(self, media_id):
        return f"{UPLOADS}{self.files.get(media_id, 'anh-cu.webp')}"

    def create_media(self, request):
        self.counts["upload"] += 1
        fault = self._fault(("upload", self.counts["upload"]))
        if fault is not None:
            return fault
        disposition = request.headers["Content-Disposition"]
        name = re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1)
        media_id, self.next_id = self.next_id, self.next_id + 1
        self.files[media_id] = name
        return (201, {"id": media_id, "source_url": self.source_url(media_id)}, {})

    def update_media(self, request):
        self.counts["describe"] += 1
        fault = self._fault(("describe", self.counts["describe"]))
        if fault is not None:
            return fault
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": self.source_url(media_id), **body(request)}

    def create_post(self, _request):
        fault = self._fault(("create",))
        if fault is not None:
            return fault
        return (201, {"id": POST_ID, "status": "draft", "title": {"raw": "T"}}, {})

    def update_post(self, request):
        return {"id": POST_ID, "status": "draft", **body(request)}


@pytest.fixture
def site(fake_wp):
    return Site(fake_wp)


def send(client, parts, title="Sửa cổng inox Tân Phú"):
    return client.create_draft_with_images(title, parts)


# ===== Yêu cầu 1 (LC-T054-2): lỗi ở từng bước, bài nháp "có thể đã có" =======================

STEPS = {
    "tải ảnh 1": ("upload", 1),
    "ghi alt ảnh 1": ("describe", 1),
    "tải ảnh 2": ("upload", 2),
    "ghi alt ảnh 2": ("describe", 2),
    "tạo nháp": ("create",),
}
# Ảnh đã lên thư viện (mã) trước khi bước đó lỗi; lệnh cuối cùng phải là lệnh của bước lỗi.
UPLOADED_BEFORE = {
    ("upload", 1): [],
    ("describe", 1): [FIRST_ID],
    ("upload", 2): [FIRST_ID],
    ("describe", 2): [FIRST_ID, FIRST_ID + 1],
    ("create",): [FIRST_ID, FIRST_ID + 1],
}
LAST_CALL = {
    ("upload", 1): ("POST", MEDIA),
    ("describe", 1): ("POST", f"{MEDIA}/{FIRST_ID}"),
    ("upload", 2): ("POST", MEDIA),
    ("describe", 2): ("POST", f"{MEDIA}/{FIRST_ID + 1}"),
    ("create",): ("POST", POSTS),
}
FAULTS = {
    "hết giờ": lambda: requests.exceptions.ReadTimeout("hết giờ"),
    "hết giờ lúc nối": lambda: requests.exceptions.ConnectTimeout("hết giờ"),
    "mất mạng": lambda: requests.exceptions.ConnectionError("mất mạng"),
    "lỗi SSL": lambda: requests.exceptions.SSLError("ssl"),
    "đứt giữa chừng": lambda: requests.exceptions.ChunkedEncodingError("đứt"),
    "500": lambda: (500, {"code": "internal_server_error", "message": "lỗi"}, {}),
    "503 trang HTML": lambda: (503, b"<html>Service Unavailable</html>", {}),
    "302": lambda: (302, b"", {"Location": f"{BASE_URL}/khac"}),
    "200 trang HTML": lambda: (200, b"<html>ok</html>", {}),
    "400": lambda: (400, {"code": "rest_invalid_param", "message": "sai"}, {}),
    "403": lambda: (403, {"code": "rest_forbidden", "message": "cấm"}, {}),
    "404": lambda: (404, {"code": "rest_no_route", "message": "không có"}, {}),
    "429": lambda: (429, {"code": "too_many", "message": "chậm lại"}, {}),
    "lỗi lạ": lambda: RuntimeError("bất ngờ"),
}
CLEAR_REFUSALS = {"400", "403", "404", "429"}  # lời từ chối 4xx rõ ràng: website không làm
STATUS = {"500": 500, "503 trang HTML": 503, "302": 302, "400": 400, "403": 403, "404": 404,
          "429": 429}  # fmt: skip


@pytest.mark.parametrize("fault", list(FAULTS))
@pytest.mark.parametrize("step", list(STEPS))
def test_loi_o_tung_buoc_bao_dung_bai_nhap_va_anh(fake_wp, wp_client, images, step, fault):
    where = STEPS[step]
    Site(fake_wp, faults={where: FAULTS[fault]()})
    parts = ["<p>Mở bài</p>", DraftImage(images[0], alt="Cổng inox"),
             DraftImage(images[1], alt="Cửa cuốn")]  # fmt: skip
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, parts)
    err = error.value
    message = str(err)
    refused = fault in CLEAR_REFUSALS
    at_create = where == ("create",)

    assert [image.id for image in err.uploaded] == UPLOADED_BEFORE[where]
    assert err.maybe_draft is (at_create and not refused)
    assert err.maybe_uploaded is (where[0] == "upload" and not refused)
    assert err.status_code == STATUS.get(fault)
    # Không bao giờ vừa "có thể đã có" vừa "chưa tạo bài nháp" trong cùng một câu báo.
    assert not (MAYBE_DRAFT in message and NOT_CREATED in message.casefold())
    if at_create and refused:
        assert NOT_CREATED in message.casefold() and MAYBE_DRAFT not in message
    elif at_create:
        assert MAYBE_DRAFT in message and "Bài viết → Nháp" in message
    else:
        assert MAYBE_DRAFT not in message
    if fault == "lỗi lạ" and not at_create:
        assert NOT_CREATED in message.casefold()
    if err.uploaded:
        assert f"{len(err.uploaded)} ảnh lên thư viện Media" in message
    for secret in (KHOA_GIA, KHOA_GIA.replace(" ", "")):
        assert secret not in message
    # Lệnh lỗi là lệnh cuối: ảnh lỗi thì không tạo nháp, nháp lỗi thì không đặt ảnh đại diện.
    assert calls(fake_wp)[-1] == LAST_CALL[where]
    assert len(created_posts(fake_wp)) == (1 if at_create else 0)
    assert {method for method, _ in calls(fake_wp)} <= {"GET", "POST"}
    # Bài chưa chắc do app tạo (không có mã bài): không ghi gì vào bài 42.
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError):
        wp_client.set_featured_image(POST_ID, FIRST_ID)
    assert len(fake_wp.requests) == before


def test_bai_khong_co_anh_tao_nhap_het_gio_van_bao_co_the_da_co(fake_wp, wp_client, images):
    Site(fake_wp, faults={("create",): requests.exceptions.ReadTimeout("hết giờ")})
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, ["<p>Bài chỉ có chữ</p>"])
    err = error.value
    assert err.maybe_draft is True and err.uploaded == () and err.maybe_uploaded is False
    assert MAYBE_DRAFT in str(err) and NOT_CREATED not in str(err).casefold()
    assert calls(fake_wp) == [("POST", POSTS)]


# ===== Yêu cầu 2 (LC-T054-3): alt, chú thích ảnh AI mở đầu «[…]:» không còn "\" ===============

AI_LABELS = [
    ("[Sau khi sửa]: cổng inox bóng", "[Mẹo]: lau bằng khăn mềm"),
    ("[Bước 1]: cạo gỉ [Bước 2]: sơn lót", "[Bước 3]: sơn phủ hai lớp"),
    ("[Cửa cuốn]: khe thoáng mới", "[Chú ý] [mẫu 2026]: sơn tĩnh điện"),
]


@pytest.mark.parametrize(("alt", "caption"), AI_LABELS)
def test_anh_ai_nhan_dau_dong_len_website_khong_con_gach_cheo(
    fake_wp, wp_client, site, images, alt, caption
):
    suggestion = clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)
    assert "\\" in suggestion.alt + suggestion.caption  # tiền đề: gợi ý còn escape Markdown
    image = DraftImage(
        images[0], alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    send(wp_client, [image])
    want_alt, want_caption = f"Minh họa {alt}", f"Ảnh minh họa (AI): {caption}"

    page = _Page(sent_content(fake_wp))
    assert page.alts == [want_alt] and page.captions == [want_caption]
    update = media_writes(fake_wp, FIRST_ID)[0]
    assert html.unescape(update["alt_text"]) == want_alt
    assert html.unescape(update["caption"]) == want_caption
    assert html.unescape(update["title"]) == f"[AI] {want_alt}"
    for text in json_strings(fake_wp):  # T-061 không nới: không "[" "]" trần ở đâu cả
        assert "\\" not in text and "[" not in text and "]" not in text


def test_nguoi_dung_sua_tay_them_chu_truoc_nhan_khong_con_gach_cheo(
    fake_wp, wp_client, site, images
):
    alt = "Ảnh thật, " + clean_ai_text("[Trước khi sơn]: cổng gỉ nặng")
    caption = "Khách duyệt: " + clean_ai_text("[Ghi chú]: sơn lót chống gỉ")
    assert "\\" in alt and "\\" in caption  # tiền đề
    send(wp_client, [DraftImage(images[0], alt=alt, caption=caption)])
    page = _Page(sent_content(fake_wp))
    assert page.alts == ["Ảnh thật, [Trước khi sơn]: cổng gỉ nặng"]
    assert page.captions == ["Khách duyệt: [Ghi chú]: sơn lót chống gỉ"]
    for text in json_strings(fake_wp):
        assert "\\" not in text


@pytest.mark.parametrize(
    "caption",
    [
        "[code_snippet id=1]: chạy thử",
        "[/code_snippet]: đóng lại",
        "[[code_snippet id=1]]: chạy thử",
        "[embed]https://e.com/v[/embed]: video",
    ],
)
def test_shortcode_trong_chu_thich_anh_ai_van_bi_vo_hieu_sau_khi_go_gach_cheo(
    fake_wp, wp_client, site, images, caption
):
    suggestion = clean_suggestion(
        AltSuggestion(alt="Cổng sắt sơn đen", caption=caption), ai_generated=True
    )
    image = DraftImage(
        images[0], alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    send(wp_client, [image])
    # Người đọc thấy đúng chữ (ngoặc vuông hiện như chữ), WordPress không thấy "[" trần nào.
    assert _Page(sent_content(fake_wp)).captions == [f"Ảnh minh họa (AI): {caption}"]
    update = media_writes(fake_wp, FIRST_ID)[0]
    assert html.unescape(update["caption"]) == f"Ảnh minh họa (AI): {caption}"
    for text in json_strings(fake_wp):
        assert "[" not in text and "]" not in text and "\\" not in text


@pytest.mark.xfail(
    strict=True,
    reason="SL-T071-1: AI tự viết tiền tố «Minh họa» trong ngoặc vuông rồi «:» hay «[» "
    "(«[Minh họa]: …») thì alt, chú thích ảnh AI lên website còn dấu «\\»",
)
@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        ("[Minh họa]: Cổng inox 2 cánh sơn tĩnh điện", "[Ảnh minh họa (AI)]: cổng sau khi sơn"),
        ("[Minh họa][cổng sắt] sơn đen mờ", "[Minh họa][Lưu ý] sơn hai lớp"),
    ],
)
def test_sl_t071_1_anh_ai_tien_to_trong_ngoac_vuong_con_gach_cheo(
    fake_wp, wp_client, site, images, alt, caption
):
    suggestion = clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)
    image = DraftImage(
        images[0], alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    send(wp_client, [image])
    page = _Page(sent_content(fake_wp))
    assert page.alts[0].startswith("Minh họa ")
    assert page.captions[0].startswith("Ảnh minh họa (AI): ")
    assert "\\" not in page.alts[0] and "\\" not in page.captions[0]
    for text in json_strings(fake_wp):  # alt_text, title, caption gửi REST
        assert "\\" not in text


# ===== Yêu cầu 3 (LC-T054-5): tải ảnh phải 201, mã ảnh trùng thì dừng ========================


@pytest.mark.parametrize("code", [200, 202, 203, 206, 207])
def test_tai_anh_khong_phai_201_dung_truoc_khi_ghi_alt(fake_wp, wp_client, images, code):
    old = (code, {"id": 55, "source_url": f"{UPLOADS}anh-cu.webp"}, {})  # có thể là ảnh có sẵn
    Site(fake_wp, faults={("upload", 1): old})
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(images[0], alt="Cổng mới")])
    err = error.value
    assert err.uploaded == () and err.maybe_uploaded is True and err.maybe_draft is False
    assert "201" in str(err)
    assert calls(fake_wp) == [("POST", MEDIA)]  # không ghi alt cho ảnh 55, không tạo nháp


def test_anh_thu_ba_trung_ma_anh_dau_thi_dung_khong_ghi_de_alt(fake_wp, wp_client, images):
    reused = (201, {"id": FIRST_ID, "source_url": f"{UPLOADS}anh-khac.webp"}, {})
    Site(fake_wp, faults={("upload", 3): reused})
    parts = [DraftImage(images[0], alt="Ảnh một"), "<p>giữa</p>",
             DraftImage(images[1], alt="Ảnh hai"), DraftImage(images[2], alt="Ảnh ba")]  # fmt: skip
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, parts)
    err = error.value
    assert [image.id for image in err.uploaded] == [FIRST_ID, FIRST_ID + 1]
    assert err.maybe_uploaded is True and err.maybe_draft is False
    assert [write["alt_text"] for write in media_writes(fake_wp, FIRST_ID)] == ["Ảnh một"]
    assert [write["alt_text"] for write in media_writes(fake_wp, FIRST_ID + 1)] == ["Ảnh hai"]
    assert not created_posts(fake_wp) and calls(fake_wp)[-1] == ("POST", MEDIA)


def test_cung_mot_anh_dat_hai_cho_khong_bi_coi_la_trung_ma(fake_wp, wp_client, site, images):
    image = DraftImage(images[0], alt="Cổng inox")
    result = send(wp_client, [image, "<p>giữa</p>", image])
    assert [uploaded.id for uploaded in result.images] == [FIRST_ID]
    assert calls(fake_wp).count(("POST", MEDIA)) == 1
    assert _Page(sent_content(fake_wp)).alts == ["Cổng inox", "Cổng inox"]


# ===== Yêu cầu 4 (LC-T054-6): chốt cuối của figure_html chỉ đọc thẻ <img> ===================

SRC = f"{UPLOADS}cong-inox.webp"
TRICKY_CAPTION = f'ảnh src="{SRC}" alt="giả"'  # chữ chú thích giống thuộc tính của ảnh
BROKEN_FILTERS = {
    "src thành data-src": lambda out: out.replace(' src="', ' data-src="', 1),
    "đổi địa chỉ ảnh": lambda out: out.replace(SRC, f"{UPLOADS}khac.webp", 1),
    "alt thành title": lambda out: out.replace(' alt="', ' title="', 1),
    "thẻ ảnh thành chữ": lambda out: out.replace("<img ", "&lt;img ", 1),
}


@pytest.mark.parametrize("broken", list(BROKEN_FILTERS))
def test_bo_loc_lam_hong_the_anh_thi_bao_loi_du_chu_thich_giong_thuoc_tinh(monkeypatch, broken):
    real = image_html.sanitize_html
    monkeypatch.setattr(image_html, "sanitize_html", lambda t: BROKEN_FILTERS[broken](real(t)))
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=SRC, alt="Cổng", width=10, height=10, caption=TRICKY_CAPTION)


def test_bo_loc_hong_the_anh_thi_khong_tao_nhap_va_liet_ke_anh(
    fake_wp, wp_client, site, images, monkeypatch
):
    real = image_html.sanitize_html
    monkeypatch.setattr(
        image_html, "sanitize_html", lambda t: BROKEN_FILTERS["src thành data-src"](real(t))
    )
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(images[0], alt="Cổng inox", caption=TRICKY_CAPTION)])
    err = error.value
    assert site.source_url(FIRST_ID) == SRC  # tiền đề: chú thích nhắc đúng địa chỉ ảnh
    assert [image.id for image in err.uploaded] == [FIRST_ID]
    assert err.maybe_draft is False and not created_posts(fake_wp)


def test_chu_thich_co_the_anh_dang_chu_van_chi_mot_anh():
    caption = f'<img src="{SRC}" alt="x"> ảnh mẫu'
    out = image_html.figure_html(src=SRC, alt="Cổng", width=10, height=10, caption=caption)
    page = _Page(out)
    assert len(page.imgs) == 1 and page.imgs[0]["src"] == SRC
    assert page.captions == [caption]


# ===== Yêu cầu 5 (LC-T054-4): DraftImage nhận ImageTags, ảnh AI theo tags.source ==============


@pytest.mark.parametrize(
    ("field", "value"),
    [("ai_generated", True), ("category", "Cổng inox"), ("area", "Tân Phú"),
     ("project_code", "CT012")],
)  # fmt: skip
def test_draft_image_khong_con_nhan_truong_chu_tu_do(images, field, value):
    with pytest.raises(TypeError):
        DraftImage(images[0], alt="Cổng", **{field: value})


def test_anh_ai_chi_theo_nguon_trong_the(fake_wp, wp_client, site, images):
    looks_ai = DraftImage(images[0], alt="Minh họa cổng inox")  # chữ giống ảnh AI, thẻ ảnh thật
    ai = DraftImage(images[1], alt="Cổng inox", tags=ImageTags(source=SOURCE_AI))
    send(wp_client, [looks_ai, ai])
    assert file_names(fake_wp) == ["minh-hoa-cong-inox.webp", "minh-hoa-ai-cong-inox.webp"]
    titles = [html.unescape(media_writes(fake_wp, n)[0]["title"]) for n in (101, 102)]
    assert titles == ["Minh họa cổng inox", "[AI] Cổng inox"]


def test_anh_ai_trong_thu_muc_cong_trinh_khong_mang_ma_va_khu_vuc(fake_wp, wp_client, site, images):
    real_tags = tags_for_image(ImageRef(0, "CT012 - Cổng inox - Tân Phú/truoc/cong.jpg")).tags
    ai_tags = tags_for_image(ImageRef(0, "CT012 - Cổng inox - Tân Phú/minh họa/cong.png")).tags
    assert ai_tags.is_ai and not (ai_tags.project_code or ai_tags.area or ai_tags.phase)
    send(
        wp_client,
        [
            DraftImage(images[0], alt="Cổng inox sau khi sửa", tags=real_tags),
            DraftImage(images[1], alt="Minh họa cổng inox", tags=ai_tags),
        ],
    )
    assert file_names(fake_wp) == ["cong-inox-tan-phu-ct012.webp", "minh-hoa-ai-cong-inox.webp"]
    about_ai = json.dumps(media_writes(fake_wp, FIRST_ID + 1), ensure_ascii=False)
    for word in ("CT012", "ct012", "Tân Phú", "tan-phu"):
        assert word not in about_ai


def _tampered(tags, **changes):
    """``ImageTags`` hợp lệ lúc tạo, rồi bị sửa thẳng (bỏ qua bước kiểm của lớp đóng băng)."""
    for name, value in changes.items():
        object.__setattr__(tags, name, value)
    return tags


TAMPERED = {
    "ảnh AI thêm mã công trình": lambda: _tampered(
        ImageTags(source=SOURCE_AI, category="Cổng inox"), project_code="CT012"
    ),
    "ảnh AI thêm khu vực": lambda: _tampered(ImageTags(source=SOURCE_AI), area="Tân Phú"),
    "ảnh AI thêm trước/sau": lambda: _tampered(ImageTags(source=SOURCE_AI), phase="truoc"),
    "ảnh thật có khu vực đổi thành AI": lambda: _tampered(ImageTags(area="Tân Phú"), source="ai"),
    "nguồn viết hoa": lambda: _tampered(ImageTags(), source="AI"),
    "nguồn có dấu cách": lambda: _tampered(ImageTags(), source=" ai"),
    "nguồn có ký tự vô hình": lambda: _tampered(ImageTags(), source="ai\u200b"),
    "mã công trình là số": lambda: _tampered(ImageTags(), project_code=12),
    "mã công trình chữ số toàn khổ": lambda: _tampered(ImageTags(), project_code="CT１２"),
    "khu vực là None": lambda: _tampered(ImageTags(), area=None),
    "hạng mục là bytes": lambda: _tampered(ImageTags(), category=b"Cong inox"),
    "hạng mục có xuống dòng": lambda: _tampered(
        ImageTags(category="Cổng inox"), category="Cổng inox\r\nX-Evil: 1"
    ),
    "hạng mục là tên khách": lambda: _tampered(ImageTags(), category="Nhà anh Tuấn"),
    "thẻ thư mục (FolderTags)": lambda: tags_for_image(
        ImageRef(0, "CT012 - Cổng inox - Tân Phú/truoc/cong.jpg")
    ),
}


@pytest.mark.parametrize("case", list(TAMPERED))
def test_the_anh_thu_hai_bi_sua_thi_chan_truoc_moi_lenh(fake_wp, wp_client, site, images, case):
    good = DraftImage(images[0], alt="Cổng inox", tags=ImageTags(category="Cổng inox"))
    bad = DraftImage(images[1], alt="Cổng inox", tags=TAMPERED[case]())
    with pytest.raises(WordPressError) as error:
        send(wp_client, [good, "<p>x</p>", bad])
    assert not isinstance(error.value, DraftImagesError)
    assert str(error.value) == "Thẻ của ảnh thứ 2 không hợp lệ. Chưa gửi gì lên website."
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    "fields",
    [
        {"source": SOURCE_AI, "project_code": "CT012"},
        {"source": SOURCE_AI, "area": "Tân Phú"},
        {"source": SOURCE_AI, "phase": "sau"},
    ],
)
def test_the_anh_ai_khong_tao_duoc_voi_ma_khu_vuc_truoc_sau(fields):
    with pytest.raises(TagError):
        ImageTags(**fields)
    with pytest.raises(TagError):
        ImageTags.from_input(**fields)


# ===== Soát R5: chuỗi độc vẫn được kiểm ở tầng đặt tên file ==================================
# Test ``test_ten_file_khong_the_chen_header_hay_doi_duoi`` (T-054) nay đưa 7 chuỗi độc qua alt,
# nên ``image_file_name`` chỉ nhận chữ đã qua ``plain_image_text``. Giữ một lớp kiểm thẳng ở hàm
# đặt tên với chữ thô (như trước T-071), phòng sau này có đường khác đưa chữ vào tên file.

POISON = [
    'x"; filename="shell.php',
    "a\r\nX-Evil: 1",
    "../../wp-config.php",
    r"C:\Users\An\Ảnh\CT012 - Nhà anh Tuấn\cong.php",
    "%2e%2e%2fshell.php",
    "<script>alert(1)</script>",
    "\u202egnp.php",
]


@pytest.mark.parametrize("value", POISON)
@pytest.mark.parametrize("field", ["category", "area", "alt"])
def test_ten_file_tu_chu_doc_tho_van_dung_khuon(field, value):
    for ai_generated in (False, True):
        name = image_file_name(**{field: value}, ai_generated=ai_generated)
        assert re.fullmatch(r"[a-z0-9-]+\.webp", name)


@pytest.mark.parametrize("value", POISON)
def test_anh_ai_alt_doc_khong_chen_duoc_header(fake_wp, wp_client, site, images, value):
    send(wp_client, [DraftImage(images[0], alt=value, tags=ImageTags(source=SOURCE_AI))])
    (name,) = file_names(fake_wp)
    assert re.fullmatch(r"minh-hoa-ai-[a-z0-9-]+\.webp", name)

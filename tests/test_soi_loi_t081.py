"""Soi Lỗi · T-081: thử phá bước bỏ dấu «\\» sót ở alt, chú thích ảnh AI (SL-T071-1).

Kiểm độc lập yêu cầu 1–4 của phiếu T-081 (không dùng lại dữ liệu, site giả của Thợ Máy): AI tự
viết tiền tố «Minh họa» trong ngoặc vuông («[Minh họa]: …», «[Minh họa][…]», «[Minh họa](…)»)
thì alt, chú thích lên website không còn dấu «\\»; mọi «[» «]» trần vẫn bị vô hiệu trước khi gửi
WordPress (T-061, W3); dấu «\\» ở chỗ khác giữ nguyên; ảnh thật giữ nguyên cách xử lý.

Chỉ site giả (``FakeWordPress``), không gọi WordPress hay AI thật; ảnh là ảnh giả tạo trong bộ
nhớ. Test ``xfail(strict=True)`` (nếu có) là lỗi tìm được (SL-T081-n trong
``docs/team/reports/T-081-soi-loi.md``): sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ
cần xóa dòng ``@pytest.mark.xfail``.
"""

import contextlib
import html
import io
import json
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.ai.base import AIError
from seo_app.content import OutlineItem
from seo_app.images.alt import EMPTY_ALT_MESSAGE, AltSuggestion, clean_suggestion
from seo_app.images.html import figure_html, plain_image_text
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.sanitize import escape_link_syntax
from seo_app.storage.drafts import DraftImage as SavedImage
from seo_app.storage.drafts import DraftPart, DraftSnapshot, clean_loaded
from seo_app.wordpress.client import DraftImage

BS = "\\"
ALT_BODY = "Cửa cuốn khe thoáng màu ghi sáng"
CAPTION_BODY = "lá cửa khe thoáng giúp nhà thông gió khi đóng"
ALT = "Minh họa cửa cuốn khe thoáng màu ghi sáng"
CAPTION = "Ảnh minh họa (AI): lá cửa khe thoáng giúp nhà thông gió khi đóng"

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@contextlib.contextmanager
def _pillow_state_kept():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif (``make_web_image`` đăng ký
    HEIF khi mở ảnh), như ``tests/test_soi_loi_t071.py``."""
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


def ai(alt, caption=""):
    return clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)


def sent_text(suggestion):
    """Alt, chú thích đúng như chữ gửi WordPress (trước khi escape HTML, vô hiệu «[» «]»)."""
    return plain_image_text(suggestion.alt), plain_image_text(suggestion.caption)


# ===== Yêu cầu 1, 2: đủ biến thể ra «Minh họa …», «Ảnh minh họa (AI): …», không «\» ==========

# 7 biến thể của phiếu (mục Bối cảnh), với phần thân khác của Thợ Máy.
TICKET_VARIANTS = [
    (f"[Minh họa]: {ALT_BODY}", f"[Ảnh minh họa (AI)]: {CAPTION_BODY}"),
    (f"[Ảnh minh họa]: {ALT_BODY}", f"[Ảnh minh họa]: {CAPTION_BODY}"),
    (f"[Hình minh họa]: {ALT_BODY}", f"[Hình minh họa]: {CAPTION_BODY}"),
    (f"[Minh hoạ]: {ALT_BODY}", f"[Minh hoạ]: {CAPTION_BODY}"),
    (f"[MINH HỌA]: {ALT_BODY}", f"[MINH HỌA]: {CAPTION_BODY}"),
    (f"[Minh họa]:{ALT_BODY}", f"[Minh họa]:{CAPTION_BODY}"),
]


@pytest.mark.parametrize(("alt", "caption"), TICKET_VARIANTS)
def test_bien_the_cua_phieu_ra_dung_chu_khong_gach_cheo(alt, caption):
    result = ai(alt, caption)
    assert (result.alt, result.caption) == (ALT, CAPTION)
    assert sent_text(result) == (ALT, CAPTION)


def test_bien_the_ngoac_mo_cua_phieu_giu_ngoac_cua_than_la_chu():
    result = ai("[Minh họa][lá cửa] khe thoáng màu ghi", "[Minh họa][Lưu ý] tra dầu ray")
    assert sent_text(result) == (
        "Minh họa [lá cửa] khe thoáng màu ghi",
        "Ảnh minh họa (AI): [Lưu ý] tra dầu ray",
    )
    assert BS not in result.alt + result.caption


# Ký tự vô hình, khoảng trắng lạ, viết hoa, «Minh hoạ»/«Minh họa», chữ dạng NFD, ngoặc lồng:
# kết quả phải bằng đúng khi AI viết «Minh họa: …» (không ngoặc), không còn «\» nào.
SAME_AS_PLAIN = [
    f"[Minh họa]\u200b: {ALT_BODY}",
    f"[\u200bMinh họa\u2060]: {ALT_BODY}",
    f"\ufeff[Minh họa]\u00ad:{ALT_BODY}",
    f"[Minh\u200c họa]\u200d: {ALT_BODY}",
    f"[Minh họa]\u00a0: {ALT_BODY}",
    f"[Minh họa]:\u3000{ALT_BODY}",
    f"[Minh họa]\t:\n{ALT_BODY}",
    f"[Minh\u00a0họa]:\u2003{ALT_BODY}",
    f"  [ Minh họa ]: {ALT_BODY}",
    f"[minh hoạ]: {ALT_BODY}",
    f"[Ảnh Minh Hoạ (ai)]: {ALT_BODY}",
    f"[Bức ảnh minh họa]: {ALT_BODY}",
    unicodedata.normalize("NFD", f"[Minh họa]: {ALT_BODY}"),
    f"[[Minh họa]]: {ALT_BODY}",
    f"[**Hình minh họa**]: {ALT_BODY}",
    f"[“Minh họa”]: {ALT_BODY}",
    f"[(Ảnh minh họa (AI))]: {ALT_BODY}",
    f"[Minh họa…]: {ALT_BODY}",
    f"[Minh họa]: [Minh hoạ]: {ALT_BODY}",
    f"[Minh họa][Minh họa]: {ALT_BODY}",
]


@pytest.mark.parametrize("alt", SAME_AS_PLAIN)
def test_tien_to_ngoac_vuong_bien_the_la_giong_khong_ngoac(alt):
    result = ai(alt, alt)
    assert result == ai(f"Minh họa: {ALT_BODY}", f"Minh họa: {ALT_BODY}")
    assert BS not in "".join(sent_text(result))


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        ("[Minh họa](cửa cuốn) khe thoáng", "Minh họa (cửa cuốn) khe thoáng"),
        ("[Minh họa]( cửa cuốn ) khe thoáng", "Minh họa ( cửa cuốn ) khe thoáng"),
        ("[Minh họa](cửa (cuốn) khe) thoáng", "Minh họa (cửa (cuốn) khe) thoáng"),
        ("[Minh họa](cửa cuốn khe thoáng", "Minh họa (cửa cuốn khe thoáng"),
        ("[Minh họa](AI vẽ): cửa cuốn", "Minh họa (AI vẽ): cửa cuốn"),
        ("[[Minh họa]](cửa cuốn) khe", "Minh họa (cửa cuốn) khe"),
        ("[*Minh họa*][lá cửa] khe", "Minh họa [lá cửa] khe"),
        ("[Minh họa][[lá cửa]] khe", "Minh họa [[lá cửa]] khe"),
    ],
)
def test_tien_to_ngoac_vuong_roi_ngoac_tron_hay_vuong_khong_gach_cheo(alt, expected):
    result = ai(alt)
    assert sent_text(result)[0] == expected
    assert BS not in result.alt


def test_nhan_thu_hai_nhieu_chu_giu_nhan_khong_gach_cheo():
    result = ai(f"[Minh họa]: [Cấu tạo]: {ALT_BODY}", f"[Minh họa][Lưu ý]: {CAPTION_BODY}")
    assert sent_text(result) == (
        f"Minh họa [Cấu tạo]: {ALT_BODY}",
        f"Ảnh minh họa (AI): [Lưu ý]: {CAPTION_BODY}",
    )


@pytest.mark.parametrize(("max_chars", "caption_max_chars"), [(18, 24), (25, 33), (31, 40)])
def test_cat_do_dai_sau_khi_bo_gach_cheo(max_chars, caption_max_chars):
    raw = AltSuggestion(alt=f"[Minh họa]: {ALT_BODY}", caption=f"[Minh họa]: {CAPTION_BODY}")
    result = clean_suggestion(
        raw, ai_generated=True, max_chars=max_chars, caption_max_chars=caption_max_chars
    )
    plain = AltSuggestion(alt=f"Minh họa: {ALT_BODY}", caption=f"Minh họa: {CAPTION_BODY}")
    assert result == clean_suggestion(
        plain, ai_generated=True, max_chars=max_chars, caption_max_chars=caption_max_chars
    )
    assert len(result.alt) <= max_chars and len(result.caption) <= caption_max_chars
    assert BS not in result.alt + result.caption


# ===== Yêu cầu 3: «\» ở chỗ khác giữ nguyên; ảnh thật như trước ================================


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        (f"[Minh họa]: cửa {BS}[lá] cuốn", f"Minh họa cửa {BS}[lá] cuốn"),
        (f"[Minh họa] {BS}: cửa cuốn", f"Minh họa {BS}: cửa cuốn"),  # dấu cách trước «\»
        (f"[Minh họa]{BS}{BS}(x) cửa cuốn", f"Minh họa {BS}{BS}(x) cửa cuốn"),
        (f"[Minh họa]: cửa cuốn 1{BS}2", f"Minh họa cửa cuốn 1{BS}2"),
        # Ngoặc đóng không phải «]»: «\» chỉ có thể do AI gõ, không phải của escape_link_syntax.
        (f"(Minh họa){BS}: cửa cuốn", f"Minh họa {BS}: cửa cuốn"),
        (f"**Minh họa**{BS}[lá] cửa", f"Minh họa {BS}[lá] cửa"),
    ],
)
def test_gach_cheo_ai_go_o_cho_khac_giu_nguyen(alt, expected):
    assert sent_text(ai(alt))[0] == expected


@pytest.mark.parametrize(
    ("alt", "stored", "sent"),
    [
        ("[Ảnh minh họa]: cửa cuốn", f"[Ảnh minh họa]{BS}: cửa cuốn", "[Ảnh minh họa]: cửa cuốn"),
        ("[MINH HỌA][lá] cửa", f"[MINH HỌA]{BS}[lá] cửa", "[MINH HỌA][lá] cửa"),
        ("[Minh hoạ](cửa cuốn) khe", f"[Minh hoạ]{BS}(cửa cuốn) khe", "[Minh hoạ](cửa cuốn) khe"),
    ],
)
def test_anh_that_khong_bo_tien_to_va_giu_escape_nhu_truoc(alt, stored, sent):
    result = clean_suggestion(AltSuggestion(alt=alt, caption=alt))
    assert result.alt == result.caption == stored
    assert sent_text(result) == (sent, sent)


# ===== W3 / 2.3: bỏ «\» không mở lại link Markdown, thẻ HTML, shortcode ========================

AFTER_PREFIX = [
    "[Minh họa][code_snippet id=1] cửa cuốn",
    "[Minh họa]:[code_snippet id=1] cửa cuốn",
    "[Minh họa]: [[code_snippet id=1]] cửa cuốn",
    "[Minh họa][[code_snippet id=1]]",
    "[Minh họa][embed]https://example.test/v[/embed] cửa",
    "[Minh họa]: [/code_snippet] cửa cuốn khe thoáng",
    "[Minh họa]([code_snippet id=1]) cửa cuốn",
    "[Minh họa][caption]cửa[/caption] cuốn",
    "[Minh họa][gallery ids=1,2] cửa cuốn",
    "[Minh họa][code\u200b_snippet id=1] cửa cuốn",
    "[Minh họa][<b>code_snippet</b> id=1] cửa cuốn",
    "[Minh họa][x](https://example.test/a) cửa cuốn",
    "[Minh họa]([x](https://example.test/a)) cửa cuốn",
    "[Minh họa][[x](javascript:alert(1))] cửa cuốn",
    "[Minh họa]: <a href='https://example.test'>cửa</a> cuốn khe",
    "[Minh họa](<img src=x onerror=alert(1)>) cửa cuốn",
    "[Minh họa][x]: [y] cửa cuốn",
    f"[Minh họa][x]{BS}(https://example.test/a) cửa cuốn",
]


@pytest.mark.parametrize("alt", AFTER_PREFIX)
def test_chu_da_luu_khong_con_cu_phap_link_hay_the_song(alt):
    # Chữ lưu trong nháp, hiện trên Streamlit: không còn «](», «][», «]:» đầu dòng chưa escape
    # (``escape_link_syntax`` không đổi gì), không có thẻ HTML.
    result = ai(alt, alt)
    for text in (result.alt, result.caption):
        assert escape_link_syntax(text) == text
        assert "<" not in text and "href" not in text and "javascript" not in text.casefold()
    assert clean_suggestion(result, ai_generated=True) == result


@pytest.mark.parametrize("alt", AFTER_PREFIX)
def test_html_anh_khong_con_ngoac_vuong_tran_hay_the_la(alt):
    result = ai(alt, alt)
    src = f"{BASE_URL}/wp-content/uploads/2026/10/a.webp"
    figure = figure_html(src=src, alt=result.alt, caption=result.caption, width=10, height=10)
    assert "[" not in figure and "]" not in figure and BS not in figure
    page = _Page(figure)
    assert page.tags <= {"figure", "img", "figcaption"}
    assert page.alts == [sent_text(result)[0]]


# ----- gửi site giả --------------------------------------------------------------------------

MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
FIRST_ID = 101


def _path(request):
    return urlsplit(request.url).path


def _body(request):
    return json.loads(request.body) if request.body else None


@pytest.fixture(scope="module")
def image():
    buffer = io.BytesIO()
    Image.new("RGB", (200, 150), (60, 60, 70)).save(buffer, "JPEG", quality=80)
    with _pillow_state_kept():
        return make_web_image(buffer.getvalue())


@pytest.fixture
def site(fake_wp):
    """Site giả: một ảnh mã 101 (trả 201), bài nháp 42."""
    url = f"{BASE_URL}/wp-content/uploads/2026/10/minh-hoa.webp"
    fake_wp.on("POST", MEDIA, (201, {"id": FIRST_ID, "source_url": url}, {}))
    fake_wp.on("POST", f"{MEDIA}/{FIRST_ID}", lambda r: {"id": FIRST_ID, "source_url": url})
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    fake_wp.on("GET", f"{POSTS}/42", lambda _r: {"id": 42, "status": "draft"})
    fake_wp.on("POST", f"{POSTS}/42", lambda r: {"id": 42, "status": "draft", **_body(r)})
    return fake_wp


class _Page(HTMLParser):
    """Đọc HTML như trình duyệt: mọi thẻ, alt của ``<img>``, chữ trong ``<figcaption>``."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.tags, self.alts, self.captions, self._caption = set(), [], [], None
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        if tag == "img":
            self.alts.append(dict(attrs).get("alt"))
        elif tag == "figcaption":
            self._caption = []

    def handle_data(self, data):
        if self._caption is not None:
            self._caption.append(data)

    def handle_endtag(self, tag):
        if tag == "figcaption" and self._caption is not None:
            self.captions.append("".join(self._caption))
            self._caption = None


def _json_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _json_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _json_strings(item)


def _send(client, image, suggestion):
    part = DraftImage(
        image, alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    client.create_draft_with_images("Cửa cuốn khe thoáng", [part])


def _sent(fake_wp):
    """(nội dung bài, lệnh ghi alt/tiêu đề/chú thích của ảnh 101, mọi chuỗi JSON gửi đi)."""
    posts = [_body(r) for r in fake_wp.requests if (r.method, _path(r)) == ("POST", POSTS)]
    route = ("POST", f"{MEDIA}/{FIRST_ID}")
    writes = [_body(r) for r in fake_wp.requests if (r.method, _path(r)) == route]
    assert len(posts) == 1 and len(writes) == 1
    strings = [
        text
        for r in fake_wp.requests
        if "json" in r.headers.get("Content-Type", "")
        for text in _json_strings(_body(r))
    ]
    return posts[0]["content"], writes[0], strings


@pytest.mark.parametrize(("alt", "caption"), TICKET_VARIANTS)
def test_gui_site_gia_alt_chu_thich_dung_chu_khong_gach_cheo(site, wp_client, image, alt, caption):
    _send(wp_client, image, ai(alt, caption))
    content, write, strings = _sent(site)
    page = _Page(content)
    assert (page.alts, page.captions) == ([ALT], [CAPTION])
    assert html.unescape(write["alt_text"]) == ALT
    assert html.unescape(write["title"]) == f"[AI] {ALT}"
    assert html.unescape(write["caption"]) == CAPTION
    for text in strings:
        assert BS not in text and "[" not in text and "]" not in text


@pytest.mark.parametrize("alt", AFTER_PREFIX)
def test_gui_site_gia_shortcode_link_the_sau_tien_to_van_bi_vo_hieu(site, wp_client, image, alt):
    suggestion = ai(alt, alt)
    _send(wp_client, image, suggestion)
    content, write, strings = _sent(site)
    page = _Page(content)
    expected_alt, expected_caption = sent_text(suggestion)
    # Người đọc thấy đúng chữ (ngoặc vuông hiện như chữ), không «\», không thẻ lạ.
    assert page.alts == [expected_alt] and BS not in expected_alt
    assert page.captions == [expected_caption] and BS not in expected_caption
    assert page.tags <= {"figure", "img", "figcaption"}
    assert html.unescape(write["alt_text"]) == expected_alt
    # WordPress không thấy «[» «]» trần nào (không shortcode nào chạy được), không thẻ <a>, <img>
    # lạ, không «javascript:».
    for text in strings:
        assert "[" not in text and "]" not in text and BS not in text
        assert "<a " not in text and "onerror" not in text and "javascript:" not in text


# ===== Yêu cầu 4 / Rủi ro Thợ Máy: «[Minh họa]: [nhãn]: một-chữ» ==============================


@pytest.mark.parametrize(
    "alt",
    [
        "[Minh họa]: [Lưu ý]: Cửa",
        "[Ảnh minh họa (AI)]:[Cấu tạo]: Inox",
        "[Minh họa][Mẹo]: cổng",
        # Cách phần mềm vẫn xử lý từ trước (bản ``main``): dạng không ngoặc vuông, tiền tố trong
        # ngoặc vuông rồi đúng một chữ (cả dòng là «[nhãn]: một-chữ» ngay từ đầu).
        "Minh họa: [Lưu ý]: Cửa",
        "[Minh họa] [Lưu ý]: Cửa",
        "[Minh họa]: Cửa",
    ],
)
def test_nhan_roi_dung_mot_chu_bao_loi_nhu_dang_khong_ngoac(alt):
    with pytest.raises(AIError) as error:
        ai(alt)
    assert str(error.value) == EMPTY_ALT_MESSAGE


def test_nhan_mot_chu_o_anh_that_cung_bao_loi_tu_truoc():
    with pytest.raises(AIError):
        clean_suggestion(AltSuggestion(alt="[Lưu ý]: Cửa", caption=""))


def test_chu_thich_nhan_roi_mot_chu_chi_con_tien_to_nhu_dang_khong_ngoac():
    # Chú thích không báo lỗi: phần thân «[nhãn]: một-chữ» bị coi là dòng khai báo link và bỏ,
    # chú thích chỉ còn tiền tố, như «Minh họa: [Lưu ý]: cổng» từ trước.
    result = ai(ALT_BODY, "[Minh họa]: [Lưu ý]: cổng")
    assert result.caption == "Ảnh minh họa (AI)"
    assert result == ai(ALT_BODY, "Minh họa: [Lưu ý]: cổng")


@pytest.mark.parametrize(
    "alt",
    [
        "[Minh họa]: [Lưu ý]: cửa cuốn",
        "[Minh họa]: [Cấu tạo]: ray và bánh xe cửa cổng trượt",
        "[Minh họa]: Cửa cuốn",
        "[Minh họa]: [Lưu ý] Cửa",
    ],
)
def test_cau_thuong_gap_van_ra_alt(alt):
    result = ai(alt)
    assert result.alt.startswith("Minh họa ") and BS not in sent_text(result)[0]


# ===== Mở lại nháp: ảnh AI lưu alt AI tự viết «[Minh họa]: …» (``clean_loaded``, T-055) ========


def test_mo_lai_nhap_anh_ai_tien_to_ngoac_vuong_khong_gach_cheo():
    saved = SavedImage(
        source=SOURCE_AI,
        prompt="Cửa cuốn khe thoáng trước nhà phố",
        alt=f"[Minh họa]: {ALT_BODY}",
        caption=f"[Ảnh minh họa (AI)][Lưu ý] {CAPTION_BODY}",
    )
    snapshot = DraftSnapshot(
        step=2,
        keyword="cửa cuốn khe thoáng",
        outline=[OutlineItem(heading="Mục 1", points=["lá cửa"], image="ảnh cửa cuốn")],
        parts=[DraftPart(heading="Mục 1", versions=["Thân."], image="ảnh", chosen_image=saved)],
    )
    image = clean_loaded(snapshot).parts[0].chosen_image
    assert image.alt == ALT
    assert plain_image_text(image.caption) == f"Ảnh minh họa (AI): [Lưu ý] {CAPTION_BODY}"
    assert BS not in plain_image_text(image.alt) + plain_image_text(image.caption)


# ===== Lỗi tìm thấy (có từ trước, ngoài phạm vi T-081) =========================================


@pytest.mark.parametrize(
    "text",
    [
        "[Minh họa] (AI): Cổng inox 2 cánh",
        "**Ảnh minh họa** (AI): Cổng inox 2 cánh",
        "«Minh họa» (AI) Cổng inox 2 cánh",
        "Minh họa: (AI) Cổng inox 2 cánh",
        "[Minh họa]: (AI) Cổng inox 2 cánh",
    ],
)
def test_sl_t081_1_ai_tach_khoi_tien_to_khong_bi_lap(text):
    # Như khi AI viết liền «Minh họa (AI): …» (``_AI_PREFIX`` nhận cả «(AI)» đứng ngay sau):
    # alt «Minh họa cổng inox 2 cánh», chú thích «Ảnh minh họa (AI): cổng inox 2 cánh».
    expected = ai("Minh họa (AI): Cổng inox 2 cánh", "Ảnh minh họa (AI): Cổng inox 2 cánh")
    assert ai(text, text) == expected

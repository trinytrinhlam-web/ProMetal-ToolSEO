"""Soi Lỗi · T-083: thử phá phần dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI (SL-T068-1, -2, -3,
LC-T068-1, SL-T081-1).

Kiểm độc lập (không dùng lại dữ liệu của Thợ Máy): 5 lỗi đóng đúng ý; C6 giữ (ảnh AI luôn có
«Minh họa» / «Ảnh minh họa (AI)», alt chỉ có tiền tố thì từ chối); chặn link, shortcode của T-061,
T-062, T-081 giữ nguyên với các kiểu tiền tố mới; kết quả bất động; ảnh thật như trước.

Chỉ site giả (``FakeWordPress``), không gọi WordPress hay AI thật; ảnh là ảnh giả tạo trong bộ
nhớ. Test ``xfail(strict=True)`` là lỗi tìm được (SL-T083-n trong
``docs/team/reports/T-083-soi-loi.md``): sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ
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
from fake_wordpress import BASE_URL
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.ai.base import AIError
from seo_app.images.alt import (
    AI_ALT_PREFIX,
    AI_CAPTION_PREFIX,
    EMPTY_ALT_MESSAGE,
    AltSuggestion,
    clean_suggestion,
)
from seo_app.images.html import figure_html, plain_image_text
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.sanitize import escape_link_syntax
from seo_app.wordpress.client import DraftImage

BS = "\\"
BODY = "khung bảo vệ cửa sổ sắt mỹ thuật"
CAPTION_BODY = "sơn lót chống gỉ trước khi sơn màu"
ALT = f"{AI_ALT_PREFIX} {BODY}"
CAPTION = f"{AI_CAPTION_PREFIX}: {CAPTION_BODY}"

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@contextlib.contextmanager
def _pillow_state_kept():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif (``make_web_image`` đăng ký
    HEIF khi mở ảnh), như ``tests/test_soi_loi_t081.py``."""
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


def ai(alt, caption="", **limits):
    return clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True, **limits)


def sent(result):
    """Alt, chú thích đúng như chữ gửi WordPress (trước khi escape HTML, vô hiệu «[» «]»)."""
    return plain_image_text(result.alt), plain_image_text(result.caption)


# ===== 5 lỗi của phiếu đóng đúng ý ============================================================

# SL-T068-1 (không dấu, gạch nối, «AI» không ngoặc, gọi khác), SL-T068-2 (Markdown, dấu đầu dòng,
# số thứ tự), SL-T081-1 («(AI)» tách rời): mỗi dạng ở cả alt lẫn chú thích.
PREFIX_STYLES = [
    "MINH HOA -",
    "minh-hoạ:",
    "Hình‐minh‑họa (ai)",
    "Buc tranh minh hoa:",
    "Hinh ve minh hoa AI –",
    "Tranh vẽ minh hoạ!",
    "Ảnh   minh   họa   (  AI  ):",
    "- **Minh họa**:",
    "1. `Minh họa`:",
    "• Ảnh minh họa (AI) –",
    "2) _Minh hoạ_",
    "10. __Minh họa__:",
    "- [Minh họa]:",
    "(AI) Minh họa:",
    "Minh họa – (AI)",
    "[Ảnh minh họa] ( AI ) :",
    "Minh họa (AI) (AI)",
    "AI: «Ảnh minh họa»",
]


@pytest.mark.parametrize("prefix", PREFIX_STYLES)
def test_tien_to_kieu_la_chi_con_mot_tien_to_chuan(prefix):
    result = ai(f"{prefix} {BODY}", f"{prefix} {CAPTION_BODY}")
    assert (result.alt, result.caption) == (ALT, CAPTION)
    assert sent(result) == (ALT, CAPTION)


@pytest.mark.parametrize("prefix", PREFIX_STYLES)
def test_alt_chi_co_tien_to_kieu_la_bi_tu_choi(prefix):
    with pytest.raises(AIError) as raised:
        ai(prefix)
    assert str(raised.value) == EMPTY_ALT_MESSAGE
    assert ai(BODY, prefix).caption == AI_CAPTION_PREFIX


LONG_CAPTIONS = [
    "Lá cửa cuốn khe thoáng, ray dưới mòn nhẹ, cần tra dầu bánh xe mỗi quý",
    # Chữ ngắn rồi một chữ rất dài: cách cắt của alt sẽ cụt giữa chữ dài (chỗ cắt ở dấu cách quá
    # gần đầu), chú thích ảnh AI thì không.
    "Ở cửacuốnnhàphốmởmộtnửa có khe thoáng giúp nhà thông gió",
]


@pytest.mark.parametrize("limit", range(17, 75))
@pytest.mark.parametrize("long_caption", LONG_CAPTIONS)
def test_chu_thich_anh_ai_khong_bao_gio_cut_giua_chu(long_caption, limit):
    words = (long_caption[:1].lower() + long_caption[1:]).split(" ")
    caption = ai(BODY, long_caption, caption_max_chars=limit).caption
    assert caption.startswith(AI_CAPTION_PREFIX) and len(caption) <= limit
    body = caption.removeprefix(AI_CAPTION_PREFIX).removeprefix(": ")
    got = body.split(" ") if body else []
    # Mỗi chữ là một chữ trọn của câu gốc (chữ cuối có thể mất dấu phẩy), theo đúng thứ tự.
    assert [w.rstrip(",") for w in got] == [w.rstrip(",") for w in words[: len(got)]]


@pytest.mark.parametrize(
    ("alt", "limit"),
    [
        ("?? cửacuốnnhàphố khe thoáng", 20),
        ("[code_snippet id=1] cổng sắt", 20),
        ("Minh họa: www.cuacuon-nhapho.test cổng", 30),
    ],
)
def test_alt_chu_dau_qua_dai_bi_tu_choi_khong_ra_mau_cut(alt, limit):
    # Chữ đầu của phần thân dài hơn chỗ còn sau «Minh họa »: cắt ra chỉ còn mẩu chữ cụt
    # («Minh họa cửacuốnnhàp», «Minh họa [code_snipp»), không mô tả gì: báo như alt «???».
    with pytest.raises(AIError) as raised:
        ai(alt, max_chars=limit)
    assert str(raised.value) == EMPTY_ALT_MESSAGE


@pytest.mark.parametrize("limit", range(1, 10))
def test_gioi_han_alt_duoi_10_bao_loi_khong_cat_tien_to(limit):
    with pytest.raises(ValueError) as raised:
        ai(BODY, CAPTION_BODY, max_chars=limit)
    assert BODY not in str(raised.value)


@pytest.mark.parametrize("limit", range(1, 17))
def test_gioi_han_chu_thich_duoi_17_bao_loi_khong_cat_tien_to(limit):
    with pytest.raises(ValueError) as raised:
        ai(BODY, CAPTION_BODY, caption_max_chars=limit)
    assert CAPTION_BODY not in str(raised.value)


# ===== C6 và giới hạn: mọi cặp giới hạn nhỏ, tiền tố luôn còn, không quá giới hạn ================

C6_TEXTS = [
    "Minh hoa: khung cửa sổ",
    "- **Minh họa**: khung bảo vệ",
    "[Minh họa] (AI): Cổng inox 2 cánh",
    "?????????? khung",
    "ở",
    "AI",
    "1. `Minh hoa`",
    "Minh họa [code_snippet id=1] cửa",
]


@pytest.mark.parametrize("caption_limit", [17, 18, 19, 20, 21, 25, 31])
@pytest.mark.parametrize("alt_limit", [10, 11, 12, 15, 19, 20, 24, 33])
@pytest.mark.parametrize("text", C6_TEXTS)
def test_c6_moi_gioi_han_nho_tien_to_con_nguyen(text, alt_limit, caption_limit):
    limits = {"max_chars": alt_limit, "caption_max_chars": caption_limit}
    try:
        result = ai(text, text, **limits)
    except AIError:
        return  # alt không còn chữ mô tả nào (đúng C6: không nhận alt chỉ có tiền tố)
    alt, caption = sent(result)
    assert alt.startswith(f"{AI_ALT_PREFIX} ") and len(result.alt) <= alt_limit
    assert caption == AI_CAPTION_PREFIX or caption.startswith(f"{AI_CAPTION_PREFIX}: ")
    assert len(result.caption) <= caption_limit
    assert ai(result.alt, result.caption, **limits) == result  # bất động ở cả giới hạn nhỏ


# ===== Kết quả bất động ========================================================================

ODD = [
    "Minh họa: Minh hoa - 1. Minh họa: `Minh họa` khung cửa",
    "[Minh họa]\\: (AI) [lá] cửa",
    "«Minh họa» (AI) – : khung",
    "Minh họa: AI-generated cổng",
    "Minh hoa sen trên cổng",
    "Ảnh minh họa: (Ai) cửa",
    "__Minh hoa__ [x](y z) cổng",
    "1. Minh họa 2) Minh họa khung",
    "Minh họa " + "lá cửa, " * 40,
    "khung " + "cửacuốnnhàphố" * 12,
    "Minh họa www.e.test/cua-cuon a@e.test",
    # Cắt theo giới hạn còn «2) Minh-hoa»: lộ ra tiền tố mới, phải bỏ tiếp ngay lần đầu.
    "2) Minh-hoaXYZ cổng sắt",
]


@pytest.mark.parametrize(
    "limits", [(10, 17), (11, 18), (20, 20), (37, 44), (125, 200), (500, 1000)]
)
@pytest.mark.parametrize("text", ODD)
def test_chay_lai_khong_doi_chu(text, limits):
    kw = {"max_chars": limits[0], "caption_max_chars": limits[1]}
    try:
        result = ai(text, text, **kw)
    except AIError:
        return
    assert ai(result.alt, result.caption, **kw) == result


# ===== Chữ không phải tiền tố được giữ; ảnh thật như trước ====================================


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        ("Minh Hóa: cửa sổ sắt", f"{AI_ALT_PREFIX} minh Hóa: cửa sổ sắt"),
        ("Hoa văn lá sen trên cổng", f"{AI_ALT_PREFIX} hoa văn lá sen trên cổng"),
        ("Tranh vẽ cổng sắt hai cánh", f"{AI_ALT_PREFIX} tranh vẽ cổng sắt hai cánh"),
        ("Hình vẽ kỹ thuật cổng trượt", f"{AI_ALT_PREFIX} hình vẽ kỹ thuật cổng trượt"),
        ("Bức tranh cổng sắt", f"{AI_ALT_PREFIX} bức tranh cổng sắt"),
        ("3.5 mét cổng trượt", f"{AI_ALT_PREFIX} 3.5 mét cổng trượt"),
        ("Minh họa: 2) lá cửa", f"{AI_ALT_PREFIX} 2) lá cửa"),
        ("Minh họa AIRBLADE máy sấy", f"{AI_ALT_PREFIX} AIRBLADE máy sấy"),
    ],
)
def test_chu_that_dau_alt_anh_ai_duoc_giu(alt, expected):
    assert ai(alt).alt == expected


@pytest.mark.parametrize(
    ("alt", "caption", "limits", "expected"),
    [
        # Ảnh thật: không bỏ tiền tố, giữ escape Markdown, không báo lỗi ở giới hạn nhỏ, chú thích
        # vẫn được cắt giữa chữ như trước (không có tiền tố cần giữ).
        ("- Minh hoa: cửa", "1. `Minh họa`: ray", {}, ("- Minh hoa: cửa", "1. `Minh họa`: ray")),
        ("[Minh họa]: (AI) Cổng", "(AI) cổng", {}, (f"[Minh họa]{BS}: (AI) Cổng", "(AI) cổng")),
        ("Cửa cuốn", "cửacuốnnhàphố", {"max_chars": 5, "caption_max_chars": 6},
         ("Cửa", "cửacuố")),
        ("AI vẽ cổng", "AI: ray", {}, ("AI vẽ cổng", "AI: ray")),
    ],
)  # fmt: skip
def test_anh_that_nhu_truoc(alt, caption, limits, expected):
    result = clean_suggestion(AltSuggestion(alt=alt, caption=caption), **limits)
    assert (result.alt, result.caption) == expected


# ===== W3 / mục 2.3: shortcode, link, thẻ sau tiền tố kiểu mới =================================

TAILS = [
    "[code_snippet id=1] khung",
    "[[code_snippet id=1]] khung",
    "[embed]https://example.test/v[/embed] khung",
    "[gallery ids=1,2] khung",
    "[x](https://example.test/a) khung",
    "<a href='https://example.test'>khung</a> cửa",
    "<img src=x onerror=alert(1)> khung",
    f"{BS}[code_snippet id=1{BS}] khung",
]
NEW_STYLES = [
    "- **Minh họa**:",
    "1. `Minh hoa`",
    "(AI) Minh họa:",
    "Hình‐minh‑họa AI",
    "__Minh họa__",
]


@pytest.mark.parametrize("tail", TAILS)
@pytest.mark.parametrize("style", NEW_STYLES)
def test_chu_luu_va_html_anh_khong_mo_lai_link_the_shortcode(style, tail):
    result = ai(f"{style} {tail}", f"{style} {tail}")
    for stored in (result.alt, result.caption):
        assert escape_link_syntax(stored) == stored
        assert "<" not in stored and "href" not in stored and "javascript" not in stored
    src = f"{BASE_URL}/wp-content/uploads/2026/10/a.webp"
    figure = figure_html(src=src, alt=result.alt, caption=result.caption, width=10, height=10)
    assert "[" not in figure and "]" not in figure
    assert set(re.findall(r"</?([a-z]+)", figure)) <= {"figure", "img", "figcaption"}
    if BS not in tail:
        assert BS not in figure


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
    Image.new("RGB", (160, 120), (90, 70, 50)).save(buffer, "JPEG", quality=80)
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
    """Đọc HTML như trình duyệt: alt của ``<img>``, chữ trong ``<figcaption>``."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.alts, self.captions, self._caption = [], [], None
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
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


@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        (
            "- **Minh hoa**: [code_snippet id=1] khung",
            "1. `Ảnh minh họa (AI)`: [[gallery ids=1]] ray",
        ),
        (
            "(AI) Minh họa – [embed]https://e.test/v[/embed] khung",
            "[Ảnh minh họa] ( AI ) : [/x] ray",
        ),
        (
            "Hình‐minh‑họa AI: [x](https://e.test) khung",
            "__Minh hoa__ <a href='https://e.test'>ray</a>",
        ),
    ],
)
def test_gui_site_gia_tien_to_kieu_moi_van_vo_hieu_shortcode(site, wp_client, image, alt, caption):
    result = ai(alt, caption)
    part = DraftImage(
        image, alt=result.alt, caption=result.caption, tags=ImageTags(source=SOURCE_AI)
    )
    wp_client.create_draft_with_images("Khung bảo vệ cửa sổ", [part])
    posts = [_body(r) for r in site.requests if (r.method, _path(r)) == ("POST", POSTS)]
    writes = [
        _body(r) for r in site.requests if (r.method, _path(r)) == ("POST", f"{MEDIA}/{FIRST_ID}")
    ]
    assert len(posts) == 1 and len(writes) == 1
    page = _Page(posts[0]["content"])
    expected_alt, expected_caption = sent(result)
    assert page.alts == [expected_alt] and expected_alt.startswith(f"{AI_ALT_PREFIX} ")
    assert page.captions == [expected_caption]
    assert expected_caption.startswith(f"{AI_CAPTION_PREFIX}: ")
    assert expected_alt.lower().count("minh h") == 1
    assert html.unescape(writes[0]["alt_text"]) == expected_alt
    for request in site.requests:
        if "json" in request.headers.get("Content-Type", ""):
            for text in _json_strings(_body(request)):
                assert "[" not in text and "]" not in text and BS not in text
                assert "<a " not in text and "href" not in text


# ===== Lỗi tìm thấy ============================================================================


@pytest.mark.xfail(
    strict=True,
    reason="SL-T083-1: dấu đầu dòng Markdown «+ » và dấu trích dẫn «> » trước tiền tố AI tự viết "
    "chưa được bỏ: alt «Minh họa + Minh họa …», alt chỉ «+ Minh họa» vẫn được nhận",
)
@pytest.mark.parametrize("marker", ["+ ", "> ", ">> ", "+ **"])
def test_sl_t083_1_dau_dau_dong_cong_va_trich_dan_truoc_tien_to(marker):
    closer = "**" if marker.endswith("**") else ""
    result = ai(
        f"{marker}Minh họa{closer}: {BODY}", f"{marker}Ảnh minh họa (AI){closer}: {CAPTION_BODY}"
    )
    assert (result.alt, result.caption) == (ALT, CAPTION)
    with pytest.raises(AIError):
        ai(f"{marker}Minh họa{closer}")

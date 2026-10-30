"""T-081: ảnh AI, AI tự viết tiền tố trong ngoặc vuông («[Minh họa]: …») thì alt, chú thích lên
website không còn dấu «\\» (Soi Lỗi SL-T071-1).

``escape_link_syntax`` thêm «\\» ngay sau «]» khi theo sau là «:», «[», «(»; ``_strip_ai_prefix``
bỏ «]» của tiền tố thì bỏ luôn dấu đó. Kiểm: đủ biến thể của phiếu, qua ``clean_suggestion`` và
qua ``DraftImage`` gửi site giả; chặn link, shortcode của T-061, T-062 không nới (không còn «[»
«]» trần nào gửi WordPress); dấu «\\» ở chỗ khác giữ nguyên; ảnh thật không đổi.

Chỉ site giả (``FakeWordPress``), không gọi WordPress hay AI thật; ảnh giả tạo trong bộ nhớ.
"""

import contextlib
import html
import io
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.images.alt import AI_ALT_PREFIX, AI_CAPTION_PREFIX, AltSuggestion, clean_suggestion
from seo_app.images.html import plain_image_text
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.sanitize import escape_shortcodes
from seo_app.wordpress.client import DraftImage

BS = "\\"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
FIRST_ID = 101
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"

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


@pytest.fixture(scope="module")
def image():
    buffer = io.BytesIO()
    Image.new("RGB", (240, 180), (200, 80, 40)).save(buffer, "JPEG", quality=85)
    with _pillow_state_kept():
        return make_web_image(buffer.getvalue())


def _path(request):
    return urlsplit(request.url).path


def _body(request):
    return json.loads(request.body) if request.body else None


@pytest.fixture
def site(fake_wp):
    """Site giả: Media cấp mã từ 101 (trả 201), bài nháp 42."""
    files = {}

    def create_media(request):
        media_id = FIRST_ID + len(files)
        files[media_id] = request.headers["Content-Disposition"]
        return (201, {"id": media_id, "source_url": f"{UPLOADS}{media_id}.webp"}, {})

    def update_media(request):
        media_id = int(_path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": f"{UPLOADS}{media_id}.webp"}

    fake_wp.on("POST", MEDIA, create_media)
    for media_id in range(FIRST_ID, FIRST_ID + 5):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", update_media)
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    fake_wp.on("GET", POST_42, lambda _r: {"id": 42, "status": "draft"})
    fake_wp.on("POST", POST_42, lambda r: {"id": 42, "status": "draft", **_body(r)})
    return files


class _Page(HTMLParser):
    """Đọc nội dung bài như trình duyệt: alt của ``<img>`` và chữ trong ``<figcaption>``."""

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


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _send_ai_image(fake_wp, client, image, suggestion):
    """Gửi một ảnh AI với alt, chú thích đã lọc; trả (trang, lệnh ghi alt, mọi chuỗi JSON)."""
    part = DraftImage(
        image, alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    client.create_draft_with_images("Sửa cổng inox", [part])
    creates = [r for r in fake_wp.requests if (r.method, _path(r)) == ("POST", POSTS)]
    assert len(creates) == 1
    route = ("POST", f"{MEDIA}/{FIRST_ID}")
    writes = [_body(r) for r in fake_wp.requests if (r.method, _path(r)) == route]
    # T-110 (Chỉ Huy duyệt 30/10): lệnh thứ hai là gắn ảnh vào bài nháp, thân đúng {"post": 42}.
    assert len(writes) == 2 and writes[1] == {"post": 42}
    strings = [
        text
        for r in fake_wp.requests
        if "json" in r.headers.get("Content-Type", "")
        for text in _strings(_body(r))
    ]
    return _Page(_body(creates[0])["content"]), writes[0], strings


def _ai(alt, caption=""):
    return clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)


# ----- yêu cầu 1, 2: đủ biến thể của phiếu ra «Minh họa cổng…», không «\» ---------------------

# Tiền tố AI tự viết trong ngoặc vuông: 5 dạng của phiếu, thêm «(AI)» và ngoặc lồng bên trong
# (ngoặc đóng «*]», «»]», «)]» vẫn kết thúc bằng «]», nên vẫn có «\» sau nó).
BRACKET_PREFIXES = [
    "[Minh họa]",
    "[Ảnh minh họa]",
    "[Hình minh họa]",
    "[Minh hoạ]",
    "[MINH HỌA]",
    "[Ảnh minh họa (AI)]",
    "[*Minh họa*]",
    "[«Minh họa»]",
    "[(Minh họa)]",
]


@pytest.mark.parametrize("sep", [": ", ":"])
@pytest.mark.parametrize("prefix", BRACKET_PREFIXES)
def test_tien_to_ngoac_vuong_roi_hai_cham_khong_con_gach_cheo(prefix, sep):
    raw = AltSuggestion(
        alt=f"{prefix}{sep}Cổng inox 2 cánh sơn tĩnh điện", caption=f"{prefix}{sep}cổng sau khi sơn"
    )
    result = clean_suggestion(raw, ai_generated=True)
    assert result.alt == "Minh họa cổng inox 2 cánh sơn tĩnh điện"
    assert result.caption == "Ảnh minh họa (AI): cổng sau khi sơn"
    # Như khi AI viết «Minh họa: …» (không ngoặc vuông), và chạy lại không đổi.
    assert result == _ai("Minh họa: Cổng inox 2 cánh sơn tĩnh điện", "Minh họa: cổng sau khi sơn")
    assert clean_suggestion(result, ai_generated=True) == result


@pytest.mark.parametrize(
    ("alt", "same_as", "expected"),
    [
        # Dạng «[»: «\» của «][» bị bỏ cùng «]»; ngoặc vuông của phần thân giữ nguyên là chữ.
        ("[Minh họa][cổng sắt] sơn đen mờ", "[Minh họa] [cổng sắt] sơn đen mờ",
         "Minh họa [cổng sắt] sơn đen mờ"),
        ("[MINH HỌA][cổng sắt] sơn đen mờ", "Minh họa [cổng sắt] sơn đen mờ",
         "Minh họa [cổng sắt] sơn đen mờ"),
        ("[[Minh họa]][cổng sắt] sơn đen mờ", "[[Minh họa]] [cổng sắt] sơn đen mờ",
         "Minh họa [cổng sắt] sơn đen mờ"),
        # Dạng «(»: «\» của «](» cũng bỏ.
        ("[Minh họa](cổng sắt) sơn đen mờ", "[Minh họa] (cổng sắt) sơn đen mờ",
         "Minh họa (cổng sắt) sơn đen mờ"),
        # Tiền tố lặp: bỏ tới khi hết, mỗi lần bỏ «]» thì bỏ cả «\» theo sau.
        ("[Minh họa][Minh họa]: cổng inox", "Minh họa: cổng inox", "Minh họa cổng inox"),
        ("[Minh họa]: [Minh họa]: cổng inox", "Minh họa: cổng inox", "Minh họa cổng inox"),
    ],
)  # fmt: skip
def test_tien_to_ngoac_vuong_roi_ngoac_mo_khong_con_gach_cheo(alt, same_as, expected):
    result = _ai(alt, alt)
    assert result.alt == expected
    assert result.caption == f"{AI_CAPTION_PREFIX}: {expected.removeprefix(f'{AI_ALT_PREFIX} ')}"
    assert result == _ai(same_as, same_as)
    assert BS not in plain_image_text(result.alt) + plain_image_text(result.caption)
    assert clean_suggestion(result, ai_generated=True) == result


def test_tien_to_ngoac_vuong_bi_cat_do_dai_van_khong_con_gach_cheo():
    raw = "[Minh họa]: Cổng inox 2 cánh sơn tĩnh điện màu đen mờ"
    result = clean_suggestion(
        AltSuggestion(alt=raw, caption=raw), ai_generated=True, max_chars=30, caption_max_chars=40
    )
    assert result.alt == "Minh họa cổng inox 2 cánh sơn"
    assert result.caption == "Ảnh minh họa (AI): cổng inox 2 cánh sơn"
    assert BS not in result.alt + result.caption


# Mọi tổ hợp ngoặc mở × tiền tố × chỗ nối, phần thân không có «\»: alt, chú thích sau
# ``plain_image_text`` (đúng chữ gửi WordPress) không còn «\» nào, luôn đúng một tiền tố chuẩn.
_OPENERS = ["", "[", "[[", "[*", "[«", "[(", "[“", "«[", "*[", "**[", '"[', "(["]
_PREFIXES = [
    "Minh họa", "Ảnh minh họa", "Hình minh họa", "Minh hoạ", "MINH HỌA", "Ảnh minh họa (AI)",
]  # fmt: skip
_JOINS = ["", ":", ": ", " ", "[x] ", "(x) ", "[x]: ", ": [x] "]
_CLOSE = {"[": "]", "*": "*", "«": "»", "(": ")", "“": "”", '"': '"'}


def test_moi_to_hop_tien_to_ngoac_vuong_khong_con_gach_cheo():
    bad = []
    for opener in _OPENERS:
        closer = "".join(_CLOSE[ch] for ch in reversed(opener))
        for prefix in _PREFIXES:
            for join in _JOINS:
                if not opener and not join:
                    continue  # «Minh họaCổng»: chữ dính, không phải tiền tố
                raw = f"{opener}{prefix}{closer}{join}Cổng inox 2 cánh sơn tĩnh điện"
                result = _ai(raw, raw)
                alt, caption = plain_image_text(result.alt), plain_image_text(result.caption)
                if (
                    BS in alt + caption
                    or not alt.startswith(f"{AI_ALT_PREFIX} ")
                    or not caption.startswith(f"{AI_CAPTION_PREFIX}: ")
                    or alt.lower().count("minh họa") != 1
                ):
                    bad.append((raw, alt, caption))
    assert bad == []


# ----- yêu cầu 3: dấu «\» ở chỗ khác giữ nguyên, ảnh thật không đổi -----------------------------


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        # «\» AI gõ trong phần thân: giữ nguyên như trước.
        (f"[Minh họa]: cổng {BS} rào", f"Minh họa cổng {BS} rào"),
        (f"[Minh họa]: cổng {BS}[x] sơn", f"Minh họa cổng {BS}[x] sơn"),
        (f"Minh họa: cổng [a]{BS}: b", f"Minh họa cổng [a]{BS}: b"),
        # «\» AI tự gõ sau dấu «:» của nhãn: không phải dấu của ``escape_link_syntax``, giữ.
        (f"[Minh họa]:{BS}: cổng", f"Minh họa {BS}: cổng"),
        # «\\» (AI escape chính dấu «\»): không phải «\» trước «:», «[», «(»; giữ nguyên như trước.
        (f"[Minh họa]{BS}{BS}: cổng", f"Minh họa {BS}{BS}: cổng"),
        # Ngoặc đóng không phải «]»: không có «\» nào để bỏ.
        (f"«Minh họa»{BS}: cổng", f"Minh họa {BS}: cổng"),
    ],
)
def test_gach_cheo_o_cho_khac_giu_nguyen(alt, expected):
    assert _ai(alt).alt == expected


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        ("[Minh họa]: Cổng inox 2 cánh", f"[Minh họa]{BS}: Cổng inox 2 cánh"),
        ("[Minh họa][cổng sắt] sơn đen", f"[Minh họa]{BS}[cổng sắt] sơn đen"),
        ("[Ảnh minh họa (AI)](cổng sắt) sơn", f"[Ảnh minh họa (AI)]{BS}(cổng sắt) sơn"),
    ],
)
def test_anh_that_khong_doi(alt, expected):
    # Ảnh thật không bỏ tiền tố: escape Markdown giữ nguyên, ``plain_image_text`` gỡ khi gửi.
    result = clean_suggestion(AltSuggestion(alt=alt, caption=alt))
    assert result.alt == result.caption == expected
    assert BS not in plain_image_text(result.alt)


# ----- gửi site giả: alt trong <img>, chú thích, alt_text/tiêu đề/chú thích REST ----------------


@pytest.mark.parametrize(
    ("alt", "caption", "expected_alt", "expected_caption"),
    [
        ("[Minh họa]: Cổng inox 2 cánh sơn tĩnh điện", "[Ảnh minh họa (AI)]: cổng sau khi sơn",
         "Minh họa cổng inox 2 cánh sơn tĩnh điện", "Ảnh minh họa (AI): cổng sau khi sơn"),
        ("[Ảnh minh họa]: Cổng inox", "[Hình minh họa]: cổng inox",
         "Minh họa cổng inox", "Ảnh minh họa (AI): cổng inox"),
        ("[Minh hoạ]:Cổng inox", "[MINH HỌA]:cổng inox",
         "Minh họa cổng inox", "Ảnh minh họa (AI): cổng inox"),
        ("[Minh họa][cổng sắt] sơn đen mờ", "[Minh họa][Lưu ý] sơn hai lớp",
         "Minh họa [cổng sắt] sơn đen mờ", "Ảnh minh họa (AI): [Lưu ý] sơn hai lớp"),
        ("[Minh họa](cổng sắt) sơn đen", "[Minh họa](Lưu ý) sơn hai lớp",
         "Minh họa (cổng sắt) sơn đen", "Ảnh minh họa (AI): (Lưu ý) sơn hai lớp"),
    ],
)  # fmt: skip
def test_gui_site_gia_alt_chu_thich_anh_ai_khong_gach_cheo(
    fake_wp, wp_client, site, image, alt, caption, expected_alt, expected_caption
):
    page, write, strings = _send_ai_image(fake_wp, wp_client, image, _ai(alt, caption))
    assert page.alts == [expected_alt]
    assert page.captions == [expected_caption]
    assert html.unescape(write["alt_text"]) == expected_alt
    assert html.unescape(write["title"]) == f"[AI] {expected_alt}"
    assert html.unescape(write["caption"]) == expected_caption
    for text in strings:  # mọi chuỗi JSON gửi WordPress: không «\», không «[» «]» trần (T-061)
        assert BS not in text and "[" not in text and "]" not in text


@pytest.mark.parametrize(
    "alt",
    [
        "[Minh họa][code_snippet id=1] cổng",
        "[Minh họa]:[code_snippet id=1] cổng",
        "[Minh họa]: [/code_snippet] cổng inox",
        "[Minh họa][[code_snippet id=1]] cổng",
        "[Minh họa]: [embed]https://example.test/a[/embed] cổng",
        "[Minh họa][x](https://example.test/a) cổng",
        "[Minh họa](https://example.test/a) cổng",
        "[Minh họa]: <a href='https://example.test'>cổng</a> inox",
    ],
)
def test_bo_gach_cheo_khong_mo_lai_shortcode_hay_link(fake_wp, wp_client, site, image, alt):
    # Bỏ «\» làm «[», «(» của phần thân đứng trần: vẫn qua ``clean_ai_text`` lần nữa, rồi mọi
    # «[» «]» thành ``&#91;`` ``&#93;`` trước khi gửi (T-061, T-062 không nới).
    suggestion = _ai(alt, alt)
    for text in (suggestion.alt, suggestion.caption):
        assert "](" not in text.replace(f"]{BS}(", "") and "href" not in text
    page, write, strings = _send_ai_image(fake_wp, wp_client, image, suggestion)
    assert page.alts[0].startswith(f"{AI_ALT_PREFIX} ") and BS not in page.alts[0]
    assert page.captions[0].startswith(f"{AI_CAPTION_PREFIX}: ") and BS not in page.captions[0]
    assert write["alt_text"] == escape_shortcodes(page.alts[0])
    for text in strings:
        assert BS not in text and "[" not in text and "]" not in text and "<a " not in text

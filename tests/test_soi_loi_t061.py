"""Soi Lỗi T-061: kiểm độc lập việc vô hiệu shortcode WordPress trong mọi chữ app gửi lên site.

Không gọi WordPress thật: site giả ``FakeWordPress``; hành vi WordPress mô phỏng theo mã nguồn
kho ``wordpress-develop`` nhánh trunk (đọc ngày 2026-10-20, ghi dòng trong báo cáo
``docs/team/reports/T-061-soi-loi.md``). Ảnh giả tạo trong bộ nhớ.

Test ``xfail(strict=True)`` là lỗi tìm được (SL-T061-1, SL-T061-2 trong báo cáo): sửa xong thì
test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.
"""

import html
import io
import json
import random
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import pytest
from fake_wordpress import BASE_URL, query
from PIL import Image
from pillow_heif import options as heif_options

import seo_app.wordpress.client as client_module
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.sanitize import sanitize_html
from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import DraftImage

POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
MEDIA = "/wp-json/wp/v2/media"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")

# ----- bản Python của các hàm WordPress liên quan ---------------------------------------------

REGISTERED = ("code_snippet", "code-snippet_x", "embed", "gallery", "caption")
_WP_TAG_NAME = re.compile(r"\[([^<>&/\[\]\x00-\x20=]+)")


def wp_runs_shortcode(content):
    """``do_shortcode`` (``shortcodes.php``): không có "[" trần thì dừng; tên ứng viên phải đã
    đăng ký; ``get_shortcode_regex`` khớp và không phải dạng thoát ``[[tên]]``."""
    if "[" not in content:
        return False
    names = sorted(set(_WP_TAG_NAME.findall(content)) & set(REGISTERED))
    if not names:
        return False
    pattern = re.compile(
        r"\[(\[?)(" + "|".join(map(re.escape, names)) + r")(?![\w-])"
        r"([^\]/]*(?:/(?!\])[^\]/]*)*?)"
        r"(?:(/)\]|\](?:([^\[]*(?:\[(?!/\2\])[^\[]*)*)\[/\2\])?)(\]?)",
        re.ASCII,
    )
    return any(not (m.group(1) == "[" and m.group(6) == "]") for m in pattern.finditer(content))


def php_strip_tags(text):
    """``strip_tags`` của PHP (``php_strip_tags_ex``, phần dùng ở đây): "<" mà ký tự sau không
    phải khoảng trắng mở một thẻ, bỏ hết tới ">" (kể cả "<>", "<1>", "<=>"); hết chuỗi mà chưa
    gặp ">" thì bỏ tới cuối; ký tự NUL bị bỏ."""
    out, depth, i, in_tag = [], 0, 0, False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if ch == "\0":
            pass
        elif not in_tag:
            if ch == "<" and not nxt.isspace():
                in_tag = True
            else:
                out.append(ch)
        elif ch == "<" and not nxt.isspace():
            depth += 1
        elif ch == ">":
            if depth:
                depth -= 1
            else:
                in_tag = False
        i += 1
    return "".join(out)


def wp_sanitize_text_field(text):
    """``sanitize_text_field`` (``formatting.php`` ``_sanitize_text_fields``): có "<" thì
    ``wp_pre_kses_less_than`` (đoạn "<…" không có ">" thành mã ký tự) rồi ``wp_strip_all_tags``
    (``strip_tags`` của PHP); gộp khoảng trắng; bỏ dạng "%xx"."""
    if "<" in text:
        text = re.sub(
            r"<[^>]*?((?=<)|>|$)",
            lambda m: m.group(0) if ">" in m.group(0) else html.escape(m.group(0)),
            text,
        )
        text = php_strip_tags(text).strip()
    text = re.sub(r"[\r\n\t ]+", " ", text).strip()
    found = False
    while match := re.search(r"%[a-fA-F0-9]{2}", text):
        text = text.replace(match.group(0), "")
        found = True
    if found:
        text = re.sub(" +", " ", text).strip()
    return text


class _Seen(HTMLParser):
    """Chữ và thuộc tính như trình duyệt thấy (đã giải mã mã ký tự)."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.text, self.attrs = [], []
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.attrs.extend(attrs)

    def handle_data(self, data):
        self.text.append(data)


# ----- site giả --------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def web():
    """WebP do app dựng từ ảnh giả; trả nguyên trạng thái Pillow, pillow-heif như cũ."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _PILLOW_REGISTRIES}
    options = {name: getattr(heif_options, name) for name in _HEIF_OPTIONS}
    buffer = io.BytesIO()
    Image.new("RGB", (320, 240), (40, 120, 200)).save(buffer, "JPEG", quality=85)
    try:
        return make_web_image(buffer.getvalue())
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


def path(request):
    return urlsplit(request.url).path


def body(request):
    return json.loads(request.body) if request.body else None


@pytest.fixture
def site(fake_wp):
    """Bài nháp 42; Media cấp mã từ 101, lệnh sửa ảnh trả lại đúng chữ đã ghi."""
    state = {"next": 101}

    def create_media(_request):
        media_id = state["next"]
        state["next"] += 1
        return (201, {"id": media_id, "source_url": f"{UPLOADS}anh-{media_id}.webp"}, {})

    def update_media(request):
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": f"{UPLOADS}anh-{media_id}.webp", **body(request)}

    def create_post(request):
        return (201, {"id": 42, "status": "draft", "title": {"raw": body(request)["title"]}}, {})

    fake_wp.on("POST", MEDIA, create_media)
    for media_id in range(101, 111):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", update_media)
    fake_wp.on("POST", POSTS, create_post)
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake_wp.on("POST", POST_42, lambda r: {"id": 42, "status": "draft", **body(r)})
    return fake_wp


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def bare_brackets(fake_wp):
    """Mọi chỗ có "[" hay "]" trần trong các lệnh đã gửi: địa chỉ, header, chữ trong JSON."""
    found = []
    for request in fake_wp.requests:
        parts = urlsplit(request.url)
        if set(unquote(f"{parts.path}?{parts.query}")) & set("[]"):
            found.append(("url", request.url))
        for name, value in request.headers.items():
            if name.lower() != "authorization" and set(value) & set("[]"):
                found.append(("header", name, value))
        if "json" in request.headers.get("Content-Type", ""):
            found += [
                ("json", request.method, path(request), text)
                for text in _strings(body(request))
                if set(text) & set("[]")
            ]
    return found


# ===== 1. Mọi lệnh ghi: không còn "[" / "]" trần ở bất cứ đâu ===============================

NASTY = [
    "[code_snippet id=1]",
    "[[code_snippet id=1]]",
    "[code-snippet_x id=1]",  # tên có gạch nối, gạch dưới
    '[code_snippet id="1" php="true"]echo 1;[/code_snippet]',
    "[code​_snippet id=1]",  # ký tự rộng 0 chen trong tên
    "[‮code_snippet id=1]",  # ký tự đảo chiều
    "[code⁠_snippet­ id=1]",
    "[code_snippetㅤ id=1]",  # ký tự trống Hangul (bị gỡ như ký tự vô hình)
    "&#91;code_snippet id=1&#93;",
    "&lsqb;code_snippet id=1&rsqb;",
    "&#x5B;code_snippet id=1&#x5D;",
    "&#091;embed&#093;https://e.com/v&#091;/embed&#093;",
    "［code_snippet id=1］",  # ngoặc toàn khổ: WordPress không đọc là "["
    "[Lưu ý] Sơn chống gỉ",
]


@pytest.mark.parametrize("text", NASTY)
def test_moi_lenh_ghi_khong_con_ngoac_vuong_tran(fake_wp, wp_client, site, web, text):
    chu = f"Cổng sắt {text} mới"
    wp_client.create_draft(chu, f"<p>{chu}</p><img src='https://e.com/a.webp' alt='{chu}'>",
                           excerpt=f"<p>{chu}</p>")
    wp_client.upload_media(b"\xff\xd8 anh gia", "cong.jpg", alt_text=chu, title=chu, caption=chu)
    wp_client.set_featured_image(42, 101)
    wp_client.create_draft_with_images(
        chu,
        [f"<p>{chu}</p>", DraftImage(web, alt=chu, caption=chu, tags=ImageTags(source=SOURCE_AI))],
        excerpt=chu,
    )
    # Không qua oan: đủ 2 lệnh tạo nháp, 2 lệnh tải ảnh, 2 lệnh ghi chữ ảnh, 2 lệnh ghi bài 42.
    methods = [(r.method, path(r)) for r in fake_wp.requests]
    assert methods.count(("POST", POSTS)) == 2 and methods.count(("POST", MEDIA)) == 2
    assert methods.count(("POST", f"{MEDIA}/101")) == 1
    # T-110 (Chỉ Huy duyệt 30/10): ảnh 102 có thêm lệnh gắn vào bài nháp, thân đúng {"post": 42}.
    assert methods.count(("POST", f"{MEDIA}/102")) == 2
    to_102 = [r for r in fake_wp.requests if (r.method, path(r)) == ("POST", f"{MEDIA}/102")]
    assert body(to_102[-1]) == {"post": 42}
    assert methods.count(("POST", POST_42)) == 2
    assert bare_brackets(fake_wp) == []
    for request in fake_wp.requests:
        if "json" in request.headers.get("Content-Type", ""):
            assert not any(wp_runs_shortcode(s) for s in _strings(body(request)))


def test_chu_seo_ghi_qua_ca_hai_duong_khong_con_ngoac_vuong_tran(fake_wp, wp_client, site):
    """Chữ SEO có ngoặc vuông thường đi qua được; dạng shortcode thì chặn trước khi gửi."""
    meta = {client_module.SITESEO_TITLE_KEY: "", client_module.SITESEO_DESC_KEY: ""}
    fake_wp.on("GET", ABILITY, (404, {"code": "rest_no_route", "message": "x"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": meta})
    wp_client.write_seo = True
    wp_client.create_draft("Sửa cổng", "<p>Bài</p>")
    for text in NASTY:
        if "[" in text or "［" in text:
            with pytest.raises(WordPressError):
                wp_client.set_seo_meta(42, title=f"Cổng {text}")
    assert wp_client.set_seo_meta(42, title="Giá [ 2026 ] cửa sắt").written
    assert [s for r in fake_wp.requests if r.method == "POST" and path(r) == POST_42
            for s in _strings(body(r)) if wp_runs_shortcode(s)] == []


# ===== 2. Câu trả lời của WordPress không dựng nội dung (không chạy shortcode) ================

# Trường app được phép xin trong lệnh ghi: không trường nào WordPress dựng bằng ``the_content``
# hay ``the_excerpt`` (``content``, ``excerpt`` của bài; ``description``, ``caption`` của ảnh).
SAFE_FIELDS = {
    "id", "status", "title", "link", "featured_media", "meta", "source_url", "alt_text",
    "post",  # T-110 (Chỉ Huy duyệt 30/10): lệnh gắn ảnh vào bài nháp
    "modified_gmt",  # T-115 (Chỉ Huy duyệt 31/10): giờ sửa cuối, không dựng nội dung
}  # fmt: skip


def test_moi_lenh_ghi_wp_v2_deu_co_fields_an_toan(fake_wp, wp_client, site, web):
    meta = {client_module.SITESEO_TITLE_KEY: "", client_module.SITESEO_DESC_KEY: ""}
    fake_wp.on("GET", ABILITY, (404, {"code": "rest_no_route", "message": "x"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": meta})
    wp_client.write_seo = True
    wp_client.upload_media(b"\xff\xd8 anh gia", "cong.jpg", alt_text="Cổng", caption="c")
    wp_client.create_draft_with_images("Sửa cổng", ["<p>Bài</p>", DraftImage(web, alt="Cổng")])
    wp_client.set_featured_image(42, 101)
    assert wp_client.set_seo_meta(42, title="Cửa sắt", description="Mô tả ngắn.").written

    writes = [r for r in fake_wp.requests if r.method == "POST"]
    # tải ảnh ×2, ghi chữ ảnh ×2, tạo nháp, gắn ảnh vào bài nháp, đặt ảnh đại diện ×2, ghi meta
    # dự phòng (T-110 (Chỉ Huy duyệt 30/10): thêm lệnh gắn ảnh, `_fields=id,post`)
    assert len(writes) == 9
    for request in writes:
        assert path(request).startswith("/wp-json/wp/v2/")
        fields = query(request).get("_fields")
        assert fields is not None and len(fields) == 1, request.url
        assert set(fields[0].split(",")) <= SAFE_FIELDS, request.url


def test_lenh_ghi_dung_nguyen_dia_chi_ke_ca_truy_van(fake_wp, wp_client, site, web):
    """Bổ sung cho các test cũ T-042, T-044 nay chỉ so phần đường (``split("?")[0]``, R5): địa
    chỉ đầy đủ của mỗi lệnh ghi là cố định, không có tham số nào khác ngoài ``_fields`` (ví dụ
    ``rest_route``, ``_method`` sẽ làm test này hỏng)."""
    wp_client.create_draft_with_images("Sửa cổng", ["<p>Bài</p>", DraftImage(web, alt="Cổng")])
    post_fields = "?_fields=id%2Cstatus%2Ctitle%2Clink%2Cfeatured_media%2Cmodified_gmt"  # T-115
    media_fields = "?_fields=id%2Csource_url%2Calt_text"
    assert [(r.method, r.path_url) for r in fake_wp.requests] == [
        ("POST", MEDIA + media_fields),
        ("POST", f"{MEDIA}/101" + media_fields),
        ("POST", POSTS + post_fields),
        # T-110 (Chỉ Huy duyệt 30/10): gắn ảnh vào bài nháp.
        ("POST", f"{MEDIA}/101" + "?_fields=id%2Cpost"),
        ("GET", POST_42 + "?context=edit&_fields=id%2Cstatus%2Cmeta%2Cmodified_gmt"),  # T-115
        ("POST", POST_42 + post_fields),
    ]


# ===== 3. sanitize_html: ngẫu nhiên, chạy lại không đổi, người đọc thấy đúng chữ ==============

_ATOMS = [
    "[", "]", "[[", "]]", "[/", "&#91;", "&#93;", "&#x5B;", "&#x5d;", "&#091;", "&lsqb;", "&rsqb;",
    "&lbrack;", "&rbrack;", "&#91", "&#93", "&amp;", "&", ";", "<", ">", "/", "=", '"', "'", " ",
    "\n", "code_snippet", "embed", "x", "Cổng", "​", "‮", "­", "［", "<p>",
    "</p>", '<p title="', '<img src="https://e.com/a.webp" alt="', '">', "'>", "<!--", "-->",
    "<![CDATA[", "]]>", "<script>", "</script>", "<pre>", "</pre>", "<?", "?>", "<b", "</",
    '<a href="https://e.com/', "<td colspan='", "&#", "\\", "\x00",
]  # fmt: skip


def test_sanitize_html_ngau_nhien_khong_con_ngoac_vuong_va_on_dinh():
    rnd = random.Random(20261020)
    for _ in range(3000):
        raw = "".join(rnd.choice(_ATOMS) for _ in range(rnd.randint(1, 25)))
        out = sanitize_html(raw)
        assert "[" not in out and "]" not in out, raw
        assert sanitize_html(out) == out, raw


def test_chu_thuong_ngau_nhien_nguoi_doc_van_thay_nguyen():
    """Chữ thường (đã escape HTML như app làm) qua bộ lọc: trình duyệt hiện y như cũ."""
    chars = list("[]()\\:;!*_#&<>\"' \n") + list("aăâđêôơưÁẢÃẠcổngsắt0123456789")
    rnd = random.Random(61)
    for _ in range(2000):
        text = "".join(rnd.choice(chars) for _ in range(rnd.randint(1, 40)))
        out = sanitize_html(f"<p>{html.escape(text)}</p>")
        assert "[" not in out and "]" not in out
        assert "".join(_Seen(out).text) == text.replace("\r", "")


@pytest.mark.parametrize(
    ("raw", "text", "attrs"),
    [
        ("<h2>[Lưu ý] Bảo trì cửa cuốn</h2>", "[Lưu ý] Bảo trì cửa cuốn", {}),
        ("<blockquote><em>[Khách hỏi]</em> giá?</blockquote>", "[Khách hỏi] giá?", {}),
        ("<table><tr><td>[2026]</td></tr></table>", "[2026]", {}),
        (
            '<a href="https://e.com/tim?q=[cua-sat]&amp;p[]=1">[Xem bảng giá]</a>',
            "[Xem bảng giá]",
            {"href": "https://e.com/tim?q=[cua-sat]&p[]=1"},
        ),
        (
            '<img src="https://[2001:db8::1]/a.webp" alt="Cổng [mẫu 2026]">',
            "",
            {"src": "https://[2001:db8::1]/a.webp", "alt": "Cổng [mẫu 2026]"},
        ),
    ],
)
def test_ngoac_vuong_trong_the_khac_va_dia_chi_van_hien_dung(raw, text, attrs):
    out = sanitize_html(raw)
    assert "[" not in out and "]" not in out
    seen = _Seen(out)
    assert "".join(seen.text) == text
    assert dict(seen.attrs).items() >= attrs.items()
    assert sanitize_html(out) == out


# ===== 4. SL-T061-1: chữ SEO thành shortcode sau khi WordPress bỏ thẻ ========================

# "[" rồi một cụm "<…>" mà ``has_html`` của app không coi là thẻ (sau "<" không phải chữ cái,
# "/", "!", "?"), nhưng ``strip_tags`` của PHP bỏ: còn lại "[tên …]" liền mạch.
SEO_AFTER_STRIP = [
    "[<>code_snippet id=1]",
    "Giá tốt [<1>code_snippet id=1] cửa sắt",
    "[<=>gallery ids=1]",
    "Video [<.>embed] lắp cổng",
]


@pytest.mark.parametrize("text", SEO_AFTER_STRIP)
def test_ban_python_sanitize_text_field_cua_wordpress(text):
    """Điều kiện của SL-T061-1 (để test xfail dưới không qua oan): sau ``sanitize_text_field``,
    chữ thành shortcode WordPress chạy được; chữ thường thì giữ nguyên."""
    assert not wp_runs_shortcode(text)
    assert wp_runs_shortcode(wp_sanitize_text_field(text))
    assert wp_sanitize_text_field("Giá [ 2026 ] cửa sắt") == "Giá [ 2026 ] cửa sắt"
    assert wp_sanitize_text_field("a<b>c</b> d") == "ac d"


@pytest.mark.parametrize("text", SEO_AFTER_STRIP)
def test_sl_t061_1_chu_seo_co_cum_the_rong_bi_chan(text):
    with pytest.raises(WordPressError):
        client_module._seo_text("Tiêu đề SEO", text, 300)


# ===== 5. SL-T061-2: chữ nằm trong file ảnh người dùng tải lên ==============================

_XMP_ALT = (
    '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF '
    'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description '
    'xmlns:Iptc4xmpCore="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/">'
    "<Iptc4xmpCore:AltTextAccessibility><rdf:Alt><rdf:li xml:lang=\"x-default\">{alt}</rdf:li>"
    "</rdf:Alt></Iptc4xmpCore:AltTextAccessibility></rdf:Description></rdf:RDF></x:xmpmeta>"
)
_XMP_LI = re.compile(rb"AltTextAccessibility>\s*<rdf:Alt>\s*<rdf:li[^>]*>(.*?)</rdf:li>", re.S)


def photo_with_text(description, alt):
    """JPEG như ảnh người dùng chọn: EXIF ImageDescription và alt XMP (chuẩn IPTC) có chữ."""
    exif = Image.Exif()
    exif[0x010E] = description
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (90, 90, 90)).save(
        buffer, "JPEG", exif=exif, xmp=_XMP_ALT.format(alt=alt).encode("utf-8")
    )
    return buffer.getvalue()


def wp_read_image_metadata(data):
    """``wp_read_image_metadata`` (``wp-admin/includes/image.php``): EXIF ImageDescription làm
    chú thích, và tiêu đề khi ngắn hơn 80 byte; alt lấy từ XMP ``AltTextAccessibility``
    (``wp_get_image_alttext``, ``@since 7.0.0``, đọc mọi loại ảnh)."""
    description = str(Image.open(io.BytesIO(data)).getexif().get(0x010E, "")).strip()
    match = _XMP_LI.search(data)
    return {
        "title": description if len(description.encode("utf-8")) < 80 else "",
        "caption": description,
        "alt": html.unescape(match.group(1).decode("utf-8")) if match else "",
    }


@pytest.fixture
def media_site(fake_wp):
    """Thư viện Media mô phỏng ``WP_REST_Attachments_Controller``: tải ảnh không kèm tiêu đề,
    chú thích thì lấy từ file (``insert_attachment``), alt từ XMP qua ``sanitize_text_field``;
    lệnh sửa ảnh ghi đè trường có trong lệnh, kể cả chữ rỗng (``update_item``)."""
    stored = {}

    def create(request):
        meta = wp_read_image_metadata(request.body)
        stored.update(
            title=meta["title"] or "cong",
            caption=meta["caption"],
            alt_text=wp_sanitize_text_field(meta["alt"]),
        )
        return (201, {"id": 101, "source_url": f"{UPLOADS}cong.jpg", **stored}, {})

    def update(request):
        for key in ("title", "caption", "alt_text"):
            if key in body(request):
                stored[key] = body(request)[key]
        return {"id": 101, "source_url": f"{UPLOADS}cong.jpg", **stored}

    fake_wp.on("POST", MEDIA, create)
    fake_wp.on("POST", f"{MEDIA}/101", update)
    return stored


def test_ban_python_doc_chu_trong_file_anh_cua_wordpress():
    """Điều kiện của SL-T061-2: WordPress lấy được chữ dạng shortcode ra từ file ảnh."""
    meta = wp_read_image_metadata(photo_with_text("[code_snippet id=2]", "[code_snippet id=1]"))
    assert meta == {
        "title": "[code_snippet id=2]",
        "caption": "[code_snippet id=2]",
        "alt": "[code_snippet id=1]",
    }
    assert wp_runs_shortcode(f'<img alt="{meta["alt"]}">')  # prepend_attachment → do_shortcode


@pytest.mark.parametrize("alt_text", ["", "Cổng sắt mới sơn"])
def test_sl_t061_2_chu_trong_file_anh_khong_thanh_chu_media(
    fake_wp, wp_client, media_site, alt_text
):
    """Trang Kết nối WordPress gọi ``upload_media(file, tên, alt_text=…)``, không có tiêu đề,
    chú thích; ô alt để trống được."""
    data = photo_with_text("[code_snippet id=2]", "[code_snippet id=1]")
    wp_client.upload_media(data, "cong.jpg", alt_text=alt_text)
    for field in ("title", "caption", "alt_text"):
        assert "[" not in media_site[field], (field, media_site[field])

"""T-061: shortcode WordPress trong chữ AI, chữ SEO, alt và chú thích ảnh không chạy được.

Không gọi WordPress thật: kiểm bằng bản Python của bộ đọc shortcode WordPress (chép theo mã nguồn
``wp-includes/shortcodes.php``, nhánh trunk của ``wordpress-develop``, đọc ngày 2026-10-20) và
site giả ``FakeWordPress``. Mỗi nhóm kiểm hai chiều: shortcode bị vô hiệu, còn chữ có ngoặc
vuông thường ("[Lưu ý]") người đọc vẫn thấy y như cũ.
"""

import html
import io
import json
import re
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL, query
from PIL import Image
from pillow_heif import options as heif_options

import seo_app.wordpress.client as client_module
from seo_app.images.html import figure_html, plain_image_text
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.sanitize import escape_shortcodes, sanitize_html
from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import DraftImage

# ----- bản Python của bộ đọc shortcode WordPress ---------------------------------------------
# ``do_shortcode()`` (dòng 247-299): không có "[" trần thì trả nguyên nội dung (dòng 250); tên
# ứng viên lấy bằng ``@\[([^<>&/\[\]\x00-\x20=]++)@``, chỉ giữ tên đã đăng ký; rồi chạy
# ``get_shortcode_regex()`` (dòng 330-396). ``do_shortcode_tag()`` (dòng 398): ``[[tên]]`` là
# thoát (in ra "[tên]", không chạy). ``do_shortcodes_in_html_tags()`` chạy cùng biểu thức trong
# từng thuộc tính (kể cả có dấu nháy). PCRE của WordPress không có cờ /u: ``\w`` chỉ là ASCII.

REGISTERED = (
    "code_snippet", "code_snippet_source", "embed", "caption", "gallery", "contact-form-7",
    "audio", "video",
)  # fmt: skip
_WP_TAG_NAME = re.compile(r"\[([^<>&/\[\]\x00-\x20=]+)")


def _wp_shortcode_regex(tagnames):
    names = "|".join(re.escape(name) for name in tagnames)
    return re.compile(
        r"\[(\[?)(" + names + r")(?![\w-])"
        r"([^\]/]*(?:/(?!\])[^\]/]*)*?)"
        r"(?:(/)\]|\](?:([^\[]*(?:\[(?!/\2\])[^\[]*)*)\[/\2\])?)"
        r"(\]?)",
        re.ASCII,
    )


def wp_runs_shortcode(content, registered=REGISTERED):
    """Như ``do_shortcode``: WordPress có gọi shortcode đã đăng ký nào trong ``content`` không.

    Quét cả chuỗi (chữ lẫn thuộc tính) nên có thể báo thừa, không báo thiếu."""
    if "[" not in content:
        return False
    names = sorted(set(_WP_TAG_NAME.findall(content)) & set(registered))
    if not names:
        return False
    return any(
        not (match.group(1) == "[" and match.group(6) == "]")
        for match in _wp_shortcode_regex(names).finditer(content)
    )


def _drop_cf(text):
    """Bỏ ký tự vô hình loại Cf (như ``plain_image_text``, ``normalize_meta`` làm trước khi gửi)."""
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")


class _Seen(HTMLParser):
    """Chữ và thuộc tính như trình duyệt thấy (đã giải mã mã ký tự)."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.attrs = []
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.attrs.extend(attrs)

    def handle_data(self, data):
        self.text.append(data)


def seen_text(content):
    return "".join(_Seen(content).text)


def seen_attrs(content):
    return dict(_Seen(content).attrs)


def assert_disarmed(content):
    """Không còn "[" hay "]" trần: ``do_shortcode`` trả nguyên nội dung ngay dòng đầu."""
    assert "[" not in content and "]" not in content, content
    assert not wp_runs_shortcode(content)


# ===== bộ đọc WordPress bản Python bắt đúng (để các test dưới không qua oan) ================


def test_ban_python_cua_bo_doc_wordpress():
    assert wp_runs_shortcode("<p>[code_snippet id=1]</p>")
    assert wp_runs_shortcode('<img alt="[code_snippet id=1 php=true]">')  # trong thuộc tính
    assert wp_runs_shortcode("[embed]https://www.youtube.com/watch?v=x[/embed]")
    assert wp_runs_shortcode("[code_snippet]chữ không có thẻ đóng")
    assert wp_runs_shortcode("[gallery/]")
    assert wp_runs_shortcode("[[code_snippet id=1]")  # thiếu "]" thứ hai: không phải thoát
    assert not wp_runs_shortcode("[[code_snippet id=1]]")  # WordPress tự thoát (một lượt)
    assert not wp_runs_shortcode("[/code_snippet]")  # chỉ thẻ đóng
    assert not wp_runs_shortcode("[Lưu ý] [2026]")  # tên chưa đăng ký
    assert not wp_runs_shortcode("[code_snippet-x] [code_snippetx]")  # tên khác
    assert not wp_runs_shortcode("[code​_snippet id=1]")  # ký tự vô hình làm tên khác
    assert not wp_runs_shortcode("&#91;code_snippet id=1&#93;")  # không có "[" trần


# ===== sanitize_html: vô hiệu ở bước in ra, phủ chữ và mọi thuộc tính ========================

# (HTML gửi vào, chữ người đọc thấy, WordPress có chạy nếu gửi chữ đó sau khi gỡ ký tự vô hình)
TEXT_FORMS = [
    ("[code_snippet id=1]", "[code_snippet id=1]", True),
    ("[code_snippet id=1 php=true]echo 1;[/code_snippet]",
     "[code_snippet id=1 php=true]echo 1;[/code_snippet]", True),
    ("[code_snippet_source id=3]", "[code_snippet_source id=3]", True),
    ("[embed]https://www.youtube.com/watch?v=x[/embed]",
     "[embed]https://www.youtube.com/watch?v=x[/embed]", True),
    ("[[code_snippet id=1]]", "[[code_snippet id=1]]", False),
    ("[[code_snippet id=1]", "[[code_snippet id=1]", True),
    ("[/code_snippet]", "[/code_snippet]", False),
    ('[contact-form-7 id="5" title="Liên hệ"]', '[contact-form-7 id="5" title="Liên hệ"]', True),
    ('[gallery ids="1,2"/]', '[gallery ids="1,2"/]', True),
    ("[caption]thu[/caption]", "[caption]thu[/caption]", True),
    ("[code​_snippet id=1]", "[code​_snippet id=1]", True),
    ("[​code_snippet id=1]", "[​code_snippet id=1]", True),
    ("[‮code_snippet id=1]", "[‮code_snippet id=1]", True),
    ("[code_snippet\nid=1]", "[code_snippet\nid=1]", True),
    ("&#91;code_snippet id=1&#93;", "[code_snippet id=1]", True),
    ("&#x5B;code_snippet id=1&#x5d;", "[code_snippet id=1]", True),
    ("&#091;code_snippet id=1&#093;", "[code_snippet id=1]", True),
    ("&lsqb;code_snippet id=1&rsqb;", "[code_snippet id=1]", True),
    ("&lbrack;code_snippet id=1&rbrack;", "[code_snippet id=1]", True),
    ("&#91code_snippet id=1&#93", "[code_snippet id=1]", True),
    ("&#91;embed&#93;https://x.example/v&#91;/embed&#93;",
     "[embed]https://x.example/v[/embed]", True),
]  # fmt: skip


@pytest.mark.parametrize(("html_in", "shown", "runs"), TEXT_FORMS)
def test_shortcode_trong_chu_bi_vo_hieu_nguoi_doc_van_thay_nguyen(html_in, shown, runs):
    # Chiều 1: chữ này tới WordPress nguyên dạng (bộ lọc cũ giải mã "&#91;") là chạy được.
    assert wp_runs_shortcode(_drop_cf(shown)) is runs
    out = sanitize_html(f"<p>{html_in}</p>")
    assert_disarmed(out)
    assert seen_text(out) == shown
    assert sanitize_html(out) == out


ATTR_CASES = [
    '<img src="https://example.com/a.webp" alt="{v}" title="{v}" class="{v}" id="{v}" '
    'lang="{v}" dir="{v}" width="{v}" height="{v}" loading="{v}" sizes="{v}">',
    "<img src='https://example.com/a.webp' alt='{v}'>",
    '<img src="https://example.com/a.webp" srcset="https://example.com/{v}.webp 2x" alt="a">',
    '<a href="https://example.com/?q={v}" rel="{v}">x</a>',
    '<blockquote cite="https://example.com/{v}">x</blockquote>',
    '<table><tr><th colspan="{v}" rowspan="{v}" scope="{v}">x</th>'
    '<td colspan="{v}" rowspan="{v}">y</td></tr></table>',
    '<ol start="{v}" reversed="{v}" type="{v}"><li>x</li></ol>',
    '<q cite="https://example.com/{v}">x</q><abbr title="{v}">y</abbr>',
]
ATTR_VALUES = [
    "[code_snippet id=1]",
    "[code_snippet id=1 php=true]x[/code_snippet]",
    "[[code_snippet id=1]]",
    "[code​_snippet id=1]",
    "&#91;code_snippet id=1&#93;",
    "&lsqb;embed&rsqb;https://x.example/v&lsqb;/embed&rsqb;",
    "&#x5b;gallery&#x5D;",
]


@pytest.mark.parametrize("case", ATTR_CASES)
@pytest.mark.parametrize("value", ATTR_VALUES)
def test_shortcode_trong_moi_thuoc_tinh_bi_vo_hieu(case, value):
    raw = case.format(v=value)
    out = sanitize_html(raw)
    assert_disarmed(out)
    # Mọi thuộc tính vẫn còn, trình duyệt đọc ra đúng giá trị cũ.
    assert seen_attrs(out) == seen_attrs(raw)
    assert sanitize_html(out) == out


def test_thuoc_tinh_co_shortcode_toi_wordpress_la_chay_neu_khong_vo_hieu():
    """Chiều 1 của test trên: thuộc tính đã giải mã (như bộ lọc cũ in ra) là WordPress chạy."""
    for value in ("[code_snippet id=1]", "&#91;code_snippet id=1&#93;", "&lsqb;embed&rsqb;x"):
        decoded = html.unescape(value)
        assert wp_runs_shortcode(f'<img src="https://example.com/a.webp" alt="{decoded}">')


NORMAL_TEXTS = [
    "[Lưu ý] Sơn chống gỉ 2 lớp trước khi sơn màu.",
    "Bảng giá [cập nhật 10/2026]",
    "[Gọi thợ](https://prometal.vn) hoặc nhắn Zalo",
    "Mảng a[0] = b[1]",
    "[[Ghi chú]]",
    "[ ] chưa làm, [x] đã làm",
    "Dấu ] và [ đứng lẻ",
    "[Trước khi sửa]\\: cổng sắt gỉ",
]


@pytest.mark.parametrize("text", NORMAL_TEXTS)
def test_ngoac_vuong_thuong_nguoi_doc_van_thay_nguyen(text):
    """Chiều 2: chữ có ngoặc vuông thường (Markdown, ghi chú) hiện y như cũ, cả trong thuộc tính."""
    for wrapper in (
        "<p>{}</p>",
        '<figure class="wp-block-image"><figcaption>{}</figcaption></figure>',
        "<pre><code>{}</code></pre>",
        "<ul><li><strong>{}</strong></li></ul>",
    ):
        out = sanitize_html(wrapper.format(html.escape(text)))
        assert seen_text(out) == text
        assert "[" not in out and "]" not in out
    out = sanitize_html(
        f'<img src="https://example.com/a.webp" alt="{html.escape(text)}" '
        f'title="{html.escape(text)}">'
    )
    assert seen_attrs(out)["alt"] == text
    assert seen_attrs(out)["title"] == text


def test_chay_lai_khong_doi_ca_bai():
    doc = "".join(f"<p>{form}</p>" for form, _, _ in TEXT_FORMS)
    doc += "".join(case.format(v=value) for case in ATTR_CASES for value in ATTR_VALUES)
    doc += "".join(f"<p>{html.escape(text)}</p>" for text in NORMAL_TEXTS)
    once = sanitize_html(doc)
    assert_disarmed(once)
    assert sanitize_html(once) == once
    assert sanitize_html(sanitize_html(once)) == once


def test_escape_shortcodes_chay_lai_khong_doi():
    assert escape_shortcodes("[a]] [[b]]") == "&#91;a&#93;&#93; &#91;&#91;b&#93;&#93;"
    for text in [form for form, _, _ in TEXT_FORMS] + NORMAL_TEXTS:
        once = escape_shortcodes(text)
        assert "[" not in once and "]" not in once
        assert escape_shortcodes(once) == once
        assert html.unescape(once) == html.unescape(text)


def test_khong_doi_html_khong_co_ngoac_vuong():
    """Bài không có ngoặc vuông ra y như trước T-061 (chỉ "[", "]" bị đổi)."""
    doc = (
        "<h2>Sửa cổng</h2><p>Giá <strong>2 triệu</strong> &amp; công.</p>"
        '<img src="https://example.com/a.webp" alt="Cổng &quot;inox&quot;">'
    )
    assert sanitize_html(doc) == doc


# ===== client WordPress: mọi đường app gửi chữ lên website ==================================

POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
MEDIA = "/wp-json/wp/v2/media"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
POST_FIELDS = {"_fields": ["id,status,title,link,featured_media"]}
MEDIA_FIELDS = {"_fields": ["id,source_url,alt_text"]}
# T-110 lượt 2 (Chỉ Huy duyệt 30/10 20:25): lệnh tải ảnh xin thêm ``post``.
UPLOAD_FIELDS = {"_fields": ["id,source_url,alt_text,post"]}
_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@pytest.fixture(scope="module")
def web():
    """Ảnh WebP do app tạo từ ảnh giả trong bộ nhớ; trả nguyên trạng thái Pillow, pillow-heif
    (``make_web_image`` đăng ký HEIF, như ``tests/test_soi_loi_t054.py``)."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _PILLOW_REGISTRIES}
    options = {name: getattr(heif_options, name) for name in _HEIF_OPTIONS}
    buffer = io.BytesIO()
    Image.new("RGB", (320, 240), (200, 80, 40)).save(buffer, "JPEG", quality=85)
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


def posts_of(fake_wp, method, route):
    return [r for r in fake_wp.requests if r.method == method and path(r) == route]


@pytest.fixture
def site(fake_wp):
    """Site giả: Media cấp mã từ 101 và trả lại đúng chữ đã ghi; bài nháp 42."""
    state = {"next": 101}

    def create_media(_request):
        media_id = state["next"]
        state["next"] += 1
        answer = {"id": media_id, "source_url": f"{UPLOADS}anh-{media_id}.webp", "post": None}
        return (201, answer, {})

    def update_media(request):
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": f"{UPLOADS}anh-{media_id}.webp", **body(request)}

    def create_post(request):
        sent = body(request)
        return (201, {"id": 42, "status": "draft", "title": {"raw": sent["title"]}}, {})

    fake_wp.on("POST", MEDIA, create_media)
    for media_id in range(101, 111):
        fake_wp.on("POST", f"{MEDIA}/{media_id}", update_media)
    fake_wp.on("POST", POSTS, create_post)
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake_wp.on("POST", POST_42, lambda r: {"id": 42, "status": "draft", **body(r)})
    return fake_wp


def wp_prepend_attachment(alt_text):
    """Nội dung WordPress dựng cho trang ảnh (``prepend_attachment``, ``post-template.php``):
    ``<img>`` có ``alt`` lấy từ ``alt_text`` qua ``esc_attr`` (không mã hóa "[", không giải mã
    "&#91;"), rồi ``do_shortcode`` chạy trên cả khối (``the_content`` ưu tiên 11)."""
    return (
        f'<p class="attachment"><a href=\'{UPLOADS}a.webp\'><img width="300" height="225" '
        f'src="{UPLOADS}a-300x225.webp" alt="{alt_text}" /></a></p>\n'
    )


def test_tao_nhap_tieu_de_noi_dung_trich_doan_khong_con_shortcode(fake_wp, wp_client, site):
    title = "[code_snippet id=1] Sửa cổng [Lưu ý]"
    content = (
        "<p>[code_snippet id=1 php=true]echo 1;[/code_snippet] &#91;embed&#93;x&#91;/embed&#93;</p>"
        '<img src="https://example.com/a.webp" alt="&lsqb;code_snippet id=2&rsqb;">'
    )
    excerpt = '<p>[gallery ids="1"] [Lưu ý]</p>'
    post = wp_client.create_draft(title, content, excerpt=excerpt)

    [create] = posts_of(fake_wp, "POST", POSTS)
    sent = body(create)
    for field in ("title", "content", "excerpt"):
        assert_disarmed(sent[field])
    # Người đọc (và màn hình của app) vẫn thấy đúng chữ.
    assert html.unescape(sent["title"]) == title
    assert post.title == title
    shown = "[code_snippet id=1 php=true]echo 1;[/code_snippet] [embed]x[/embed]"
    assert seen_text(sent["content"]) == shown
    assert seen_attrs(sent["content"])["alt"] == "[code_snippet id=2]"
    assert seen_text(sent["excerpt"]) == '[gallery ids="1"] [Lưu ý]'
    # Câu trả lời không có content/excerpt: WordPress không dựng chúng (không chạy shortcode).
    assert query(create) == POST_FIELDS


# (chữ alt/chú thích, WordPress có chạy nếu gửi chữ đã làm sạch như T-054 đã gửi)
IMAGE_TEXTS = [
    ("[code_snippet id=1] cổng", True),
    ("[code_snippet id=1 php=true]x[/code_snippet]", True),
    ("[[code_snippet id=1]] cổng", False),
    ("[code​_snippet id=1] cổng", True),  # gỡ ký tự rộng 0 rồi thành shortcode liền mạch
    ("[‮code_snippet id=1] cổng", True),  # ký tự đảo chiều: người duyệt thấy chữ lộn xộn
    ("[code_⁠snippet­ id=1]", True),
    ("[embed]https://www.youtube.com/watch?v=x[/embed]", True),
    ('[contact-form-7 id="5"] cổng', True),
    ("[caption]thu[/caption]", True),
    ("&#91;code_snippet id=1&#93; cổng", False),  # người dùng gõ mã ký tự: hiện nguyên như gõ
]


@pytest.mark.parametrize(("text", "runs"), IMAGE_TEXTS)
def test_nhap_kem_anh_alt_chu_thich_va_truong_media_khong_con_shortcode(
    fake_wp, wp_client, site, web, text, runs
):
    plain = plain_image_text(text)
    # Chiều 1: chữ đã làm sạch (như T-054 gửi) tới WordPress là chạy, ở bài lẫn trang ảnh.
    assert wp_runs_shortcode(f'<img alt="{plain}"><figcaption>{plain}</figcaption>') is runs
    assert wp_runs_shortcode(wp_prepend_attachment(plain)) is runs

    wp_client.create_draft_with_images("Sửa cổng", [DraftImage(web, alt=text, caption=text)])

    [create] = posts_of(fake_wp, "POST", POSTS)
    content = body(create)["content"]
    assert_disarmed(content)
    assert seen_attrs(content)["alt"] == plain
    assert seen_text(content) == plain  # chữ duy nhất của bài là chú thích
    # T-110 (Chỉ Huy duyệt 30/10): lệnh thứ hai là gắn ảnh vào bài nháp, thân đúng {"post": 42}.
    [describe, attach] = posts_of(fake_wp, "POST", f"{MEDIA}/101")
    assert body(attach) == {"post": 42}
    update = body(describe)
    for field in ("alt_text", "title", "caption"):
        assert_disarmed(update[field])
    assert update["alt_text"] == escape_shortcodes(plain)
    assert html.unescape(update["title"]) == plain
    assert html.unescape(update["caption"]) == plain
    assert not wp_runs_shortcode(wp_prepend_attachment(update["alt_text"]))


def test_ngoac_vuong_thuong_trong_alt_chu_thich_van_hien_dung(fake_wp, wp_client, site, web):
    """Chiều 2: alt, chú thích có ngoặc vuông thường hiện đúng như người dùng đã duyệt."""
    alt = "Cổng [mẫu 2026] sơn tĩnh điện"
    caption = "[Lưu ý] sơn lại cổng sau 3 năm"
    image = DraftImage(web, alt=alt, caption=caption, tags=ImageTags(source=SOURCE_AI))
    wp_client.create_draft_with_images("Sửa cổng", [image])

    content = body(posts_of(fake_wp, "POST", POSTS)[0])["content"]
    assert seen_attrs(content)["alt"] == alt
    assert seen_text(content) == caption
    update = body(posts_of(fake_wp, "POST", f"{MEDIA}/101")[0])
    assert html.unescape(update["alt_text"]) == alt
    assert html.unescape(update["title"]) == f"[AI] {alt}"
    assert html.unescape(update["caption"]) == caption


def test_upload_media_truong_media_khong_con_shortcode(fake_wp, wp_client, site):
    texts = {
        "alt_text": "[code_snippet id=1] cổng [Lưu ý]",
        "title": "[embed]https://x.example/v[/embed]",
        "caption": "[[gallery]] [caption]x[/caption]",
    }
    media = wp_client.upload_media(b"\xff\xd8 anh gia", "cong.jpg", **texts)

    [upload] = posts_of(fake_wp, "POST", MEDIA)
    [update] = posts_of(fake_wp, "POST", f"{MEDIA}/101")
    sent = body(update)
    for field, text in texts.items():
        assert_disarmed(sent[field])
        assert html.unescape(sent[field]) == text
    assert html.unescape(media.alt_text) == texts["alt_text"]
    assert query(upload) == UPLOAD_FIELDS  # T-110 lượt 2 (Chỉ Huy duyệt 30/10 20:25)
    assert query(update) == MEDIA_FIELDS


SEO_SHORTCODES = [
    "[code_snippet_source id=3]",
    "Sửa cổng [code_snippet id=1] giá tốt",
    "[gallery]",
    "[[code_snippet id=1]]",
    "Giá [/code_snippet] tốt]",
    "[code-snippet id=1]",
    "[code​_snippet id=1]",  # ký tự vô hình bị gỡ trước khi gửi: xét sau khi gỡ
    "［code_snippet id=1］",  # dấu ngoặc toàn khổ (NFKC)
    "[2026] Giá cửa sắt",  # WordPress nhận mọi tên đã đăng ký: không đoán được tên nào an toàn
    "[Lưu ý] sơn lại cổng",
]


@pytest.mark.parametrize("field", ["title", "description", "focus_keyword"])
@pytest.mark.parametrize("text", SEO_SHORTCODES)
def test_chu_seo_dang_shortcode_bi_chan_truoc_khi_gui(fake_wp, wp_client, site, field, text):
    wp_client.write_seo = True
    wp_client.create_draft("Sửa cổng", "<p>Bài</p>")
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="shortcode") as caught:
        wp_client.set_seo_meta(42, **{field: text})
    assert len(fake_wp.requests) == before  # chưa gửi gì, kể cả lệnh dò hay kiểm nháp
    assert "code_snippet" not in str(caught.value)  # câu báo cố định, không chép chữ


SEO_NORMAL = [
    "Cửa sắt 2 cánh: 6 dấu hiệu cần thay | Pro-Metal",
    "Cửa sắt (mẫu 2026) giá tốt",
    "Giá [ 2026 ] cửa sắt",  # dấu cách sau "[": WordPress không nhận là tên shortcode
    "Giá [từ 2 triệu, chưa gồm VAT",  # không có "]" phía sau
    "Cổng ] và [ rào",
    "Mảng [] rỗng",
    "[ Lưu ý ] sơn lại cổng",
]


@pytest.mark.parametrize("text", SEO_NORMAL)
def test_chu_seo_ngoac_vuong_khong_phai_shortcode_van_gui(text):
    """Chiều 2: chữ có ngoặc vuông mà WordPress không thể đọc thành shortcode vẫn gửi nguyên."""
    assert client_module._seo_text("Tiêu đề SEO", text, 200) == text
    assert not wp_runs_shortcode(text, registered=REGISTERED + ("2026", "Lưu", "từ"))


def test_chu_seo_ngoac_vuong_ghi_qua_meta_du_phong(fake_wp, wp_client, site):
    """Chiều 2 trọn đường: ghi qua meta dự phòng, chữ tới site nguyên văn; ``_fields`` cố định."""
    meta = {client_module.SITESEO_TITLE_KEY: "", client_module.SITESEO_DESC_KEY: ""}
    fake_wp.on("GET", ABILITY, (404, {"code": "rest_no_route", "message": "x"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": meta})
    wp_client.write_seo = True
    wp_client.create_draft("Sửa cổng", "<p>Bài</p>")
    result = wp_client.set_seo_meta(42, title="Giá [ 2026 ] cửa sắt", description="Mô tả ngắn.")
    assert result.written
    [write] = posts_of(fake_wp, "POST", POST_42)
    assert body(write)["meta"][client_module.SITESEO_TITLE_KEY] == "Giá [ 2026 ] cửa sắt"
    assert query(write) == {"_fields": ["id,status,meta"]}


def test_kiem_dang_shortcode_chay_tuyen_tinh():
    """Chữ rất dài toàn "[" (AI bị dụ trả về) không làm treo app."""
    assert not client_module._has_shortcode("[a" * 300_000)
    assert not client_module._has_shortcode("[" * 300_000)
    assert client_module._has_shortcode("[a" * 300_000 + "]")


def test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung(fake_wp, wp_client, site, web):
    parts = ["<p>[code_snippet id=1]</p>", DraftImage(web, alt="[embed]x[/embed]", caption="c")]
    result = wp_client.create_draft_with_images("Sửa cổng", parts)
    assert result.featured_media == 101

    # Danh sách thay cho dict: ảnh 101 có hai lệnh khác ``_fields`` (T-110 (Chỉ Huy duyệt 30/10)).
    expected = [
        ("POST", MEDIA, UPLOAD_FIELDS),  # T-110 lượt 2 (Chỉ Huy duyệt 30/10 20:25)
        ("POST", f"{MEDIA}/101", MEDIA_FIELDS),
        ("POST", POSTS, POST_FIELDS),
        ("POST", f"{MEDIA}/101", {"_fields": ["id,post"]}),  # gắn ảnh vào bài nháp
        ("GET", POST_42, {"context": ["edit"], "_fields": ["id,status,meta"]}),
        ("POST", POST_42, POST_FIELDS),  # đặt ảnh đại diện
    ]
    assert [(r.method, path(r), query(r)) for r in fake_wp.requests] == expected
    for request in fake_wp.requests:
        fields = set(query(request)["_fields"][0].split(","))
        assert not fields & {"content", "excerpt", "description", "caption"}


def test_figure_html_go_ky_tu_vo_hinh_roi_moi_vo_hieu():
    """``plain_image_text`` nối lại tên bị ký tự vô hình chen giữa; bộ lọc chạy SAU nên vẫn chặn."""
    assert plain_image_text("[code​_snippet id=1]") == "[code_snippet id=1]"
    out = figure_html(
        src=f"{UPLOADS}a[1].webp",
        alt="[code​_snippet id=1]",
        caption="[‮code_snippet id=1] [Lưu ý]",
        width=320,
        height=240,
    )
    assert_disarmed(out)
    assert seen_attrs(out)["alt"] == "[code_snippet id=1]"
    assert seen_attrs(out)["src"] == f"{UPLOADS}a[1].webp"
    assert seen_text(out) == "[code_snippet id=1] [Lưu ý]"
    assert sanitize_html(out) == out

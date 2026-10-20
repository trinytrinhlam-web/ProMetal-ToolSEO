"""T-061: shortcode WordPress trong chữ AI, chữ SEO, alt và chú thích ảnh không chạy được.

Không gọi WordPress thật: kiểm bằng bản Python của bộ đọc shortcode WordPress (chép theo mã nguồn
``wp-includes/shortcodes.php``, nhánh trunk của ``wordpress-develop``, đọc ngày 2026-10-20) và
site giả ``FakeWordPress``. Mỗi nhóm kiểm hai chiều: shortcode bị vô hiệu, còn chữ có ngoặc
vuông thường ("[Lưu ý]") người đọc vẫn thấy y như cũ.
"""

import html
import re
import unicodedata
from html.parser import HTMLParser

import pytest

from seo_app.sanitize import escape_shortcodes, sanitize_html

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

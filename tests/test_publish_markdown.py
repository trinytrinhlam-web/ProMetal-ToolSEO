"""T-096: bộ chuyển Markdown → HTML (``seo_app/publish/markdown.py``).

Điều kiện Lá Chắn: LC-T094-4 (không bao giờ sinh ``<a>``, ``<img>``, ``<iframe>``, HTML thô, chú
thích HTML; mọi chữ qua ``html.escape`` rồi ``escape_shortcodes``), LC-T094-10 (thân phần không có
``<h1>``, ``<h2>``), board «Việc bắt buộc khi làm Giai đoạn 5» (hiểu dấu ``\\``, chuẩn hóa xuống
dòng, không xử lý link tham chiếu, không autolink). Không gọi mạng.
"""

from __future__ import annotations

import random
import re
from html.parser import HTMLParser

import pytest

from seo_app.onpage.links import markdown_blocks
from seo_app.publish.markdown import MAX_DEPTH, inline_html, markdown_to_html
from seo_app.sanitize import clean_ai_text, escape_link_syntax, sanitize_html, unbreak_autolinks
from tests.timing import assert_scales_linearly

# Thẻ bộ chuyển được phép sinh. Không có a, img, iframe, h1, h2, div, span…
CONVERTER_TAGS = frozenset(
    {"p", "h3", "h4", "h5", "h6", "strong", "em", "code", "pre", "br", "hr", "ul", "ol", "li",
     "table", "thead", "tbody", "tr", "th", "td", "blockquote"}
)  # fmt: skip
VOID = frozenset({"br", "hr"})


class _Tags(HTMLParser):
    """Thẻ, chú thích, khai báo trong HTML; kiểm thẻ lồng đúng."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.attrs: list[tuple[str, str, str | None]] = []
        self.other: list[str] = []  # chú thích, <!…>, <?…?>
        self.stack: list[str] = []
        self.balanced = True

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.extend((tag, name, value) for name, value in attrs)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.tags.append(tag)
        self.other.append(f"<{tag}/>")

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.balanced = False
        else:
            self.stack.pop()

    def handle_comment(self, data):
        self.other.append("comment")

    def handle_decl(self, decl):
        self.other.append("decl")

    def handle_pi(self, data):
        self.other.append("pi")

    def unknown_decl(self, data):
        self.other.append("unknown")


def tags_of(html_text: str) -> _Tags:
    parser = _Tags()
    parser.feed(html_text)
    parser.close()
    return parser


def assert_safe(html_text: str) -> None:
    """Chỉ thẻ của bộ chuyển, lồng đúng, không thuộc tính nào ngoài ``start`` của ``<ol>``, không
    chú thích, không "[" "]" trần, không ký tự ngắt rộng 0 của T-031."""
    parsed = tags_of(html_text)
    assert set(parsed.tags) <= CONVERTER_TAGS, set(parsed.tags) - CONVERTER_TAGS
    assert all(tag == "ol" and name == "start" for tag, name, _ in parsed.attrs), parsed.attrs
    assert parsed.other == []
    assert parsed.balanced and parsed.stack == []
    assert "[" not in html_text and "]" not in html_text
    assert "<!--" not in html_text
    # Bộ chuyển đã ra HTML "sạch": bộ lọc không còn gì để đổi.
    assert sanitize_html(html_text) == html_text


# ------------------------------------------------------------------ LC-T094-4: mẫu đối kháng

# Mẫu của T-015, T-031, T-061 và các dạng link/thẻ khác: mọi thứ phải ra chữ thường.
HOSTILE = [
    "[bấm](javascript:alert(1))",
    "[bấm](data:text/html;base64,PHNjcmlwdD4=)",
    "[bấm](&#106;avascript:alert(1))",
    "[x][1]\n\n[1]: https://evil.example",
    '[x]\n\n[x]: https://evil.example "tiêu đề"',
    '[r]: https://evil.example "a\\"b"',
    "[x](https://evil.example)",
    "[x](<https://evil.example> 'tiêu đề')",
    "![ảnh](https://evil.example/a.png)",
    "<https://evil.example>",
    "<mailto:a@evil.example>",
    "https://evil.example/x www.evil.example a@evil.example",
    "https:\u200b//evil.example www\u200b.evil.example a\u200b@evil.example",
    "\\[x\\](https://evil.example) \\<script\\>",
    "<script>alert(1)</script>",
    '<img src=x onerror="alert(1)">',
    '<iframe src="https://evil.example"></iframe>',
    '<a href="https://evil.example">x</a>',
    '<!-- wp:core/rss {"feedURL":"https://evil.example"} /-->',
    "<![CDATA[x]]> <?php echo 1; ?> <!DOCTYPE html>",
    "&lt;script&gt;alert(1)&lt;/script&gt; &#60;b&#62;",
    "[code_snippet id=1] [[caption]] [/embed] [embed]https://evil.example[/embed]",
    "| a | [x](javascript:alert(1)) |\n|---|---|\n| <b>c</b> | ![i](x) |",
    "- [x](https://evil.example)\n- <a href=x>y</a>",
    "> [x](https://evil.example)\n> <script>",
    "```\n<script>alert(1)</script>\n[x](https://evil.example)\n```",
    "`<a href=x>` ``[x](y)``",
    "**[x](https://evil.example)** *<b>*",
]


@pytest.mark.parametrize("raw", HOSTILE)
def test_hostile_markdown_never_makes_links_or_raw_html(raw):
    for text in (raw, clean_ai_text(raw), unbreak_autolinks(clean_ai_text(raw))):
        out = markdown_to_html(text)
        assert_safe(out)
        lowered = out.lower()
        # Chữ «src=», «href=» có thể còn dạng chữ đã escape; thẻ và thuộc tính thật đã kiểm ở
        # ``assert_safe`` (chỉ thẻ của bộ chuyển, không thuộc tính nào ngoài ``start``).
        for bad in ("<a", "<img", "<iframe", "<script"):
            assert bad not in lowered


def test_link_syntax_shows_as_plain_text_without_backslashes():
    # Chữ người dùng sửa tay được lưu qua escape_link_syntax ("]\\("): người đọc thấy đúng
    # "[x](url)", không có dấu "\\", không có link. Chữ AI thì clean_ai_text đã bỏ hẳn link.
    raw = "Xem [bảng giá](https://evil.example) nhé"
    out = markdown_to_html(unbreak_autolinks(escape_link_syntax(raw)))
    assert out == "<p>Xem &#91;bảng giá&#93;(https://evil.example) nhé</p>"
    assert markdown_to_html(clean_ai_text(raw)) == "<p>Xem bảng giá nhé</p>"


def test_reference_definition_is_plain_text():
    out = markdown_to_html("[x][1]\n\n[1]: https://evil.example")
    assert out == "<p>&#91;x&#93;&#91;1&#93;</p>\n<p>&#91;1&#93;: https://evil.example</p>"


def test_entities_are_decoded_then_escaped_again():
    out = markdown_to_html("&#106;avascript: &lt;b&gt; &amp;amp; &#91;x&#93; &bogus; &#0;")
    assert out == "<p>javascript: &lt;b&gt; &amp;amp; &#91;x&#93; &amp;bogus; �</p>"


def test_backslash_escapes_follow_commonmark():
    out = markdown_to_html("\\*không nghiêng\\* \\_x\\_ \\\\ \\a \\[")
    assert out == "<p>*không nghiêng* _x_ \\ \\a &#91;</p>"


def test_dropped_characters():
    # Ký tự điều khiển, điều khiển hướng chữ, nửa cặp UTF-16 lẻ bị bỏ; dấu cách rộng 0 khác giữ.
    out = markdown_to_html("a\x00b\x07c\u202ed\u2066e\ud800f\u200dg")
    assert out == "<p>abcdef\u200dg</p>"


# ------------------------------------------------------------------ khối


def test_paragraphs_and_line_breaks_have_no_newline_inside():
    out = markdown_to_html("dòng một\ndòng hai  \ndòng ba\\\ndòng bốn\n\nđoạn hai")
    assert out == "<p>dòng một dòng hai<br>dòng ba<br>dòng bốn</p>\n<p>đoạn hai</p>"
    for block in out.split("\n"):
        assert "\n" not in block


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_all_newline_styles_are_the_same(newline):
    text = newline.join(["# Tiêu đề", "", "- một", "- hai", "", "đoạn", "tiếp"])
    assert markdown_to_html(text) == markdown_to_html(text.replace(newline, "\n"))
    assert "\r" not in markdown_to_html(text)


def test_headings_never_h1_or_h2():
    body = "# một\n## hai\n### ba\n#### bốn\n##### năm\n###### sáu\nSetext\n===\nCon\n---"
    out = markdown_to_html(body)
    assert "<h1" not in out and "<h2" not in out
    assert out == (
        "<h3>một</h3>\n<h3>hai</h3>\n<h3>ba</h3>\n<h4>bốn</h4>\n<h5>năm</h5>\n<h6>sáu</h6>\n"
        "<h3>Setext</h3>\n<h3>Con</h3>"
    )


def test_heading_closing_hashes_and_inline():
    assert markdown_to_html("### **Đậm** ###") == "<h3><strong>Đậm</strong></h3>"
    assert markdown_to_html("### Lập trình C#") == "<h3>Lập trình C#</h3>"
    assert markdown_to_html("#không-phải-tiêu-đề") == "<p>#không-phải-tiêu-đề</p>"


def test_thematic_break():
    assert markdown_to_html("a\n\n---\n\nb") == "<p>a</p>\n<hr>\n<p>b</p>"
    assert markdown_to_html("* * *") == "<hr>"


def test_lists_nested_and_ordered():
    out = markdown_to_html("- một\n- hai\n  - con\n  - con 2\n- ba\n\n3. c\n4. d")
    assert out == (
        "<ul>\n<li>một</li>\n<li>hai<ul>\n<li>con</li>\n<li>con 2</li>\n</ul></li>\n<li>ba</li>\n"
        '</ul>\n<ol start="3">\n<li>c</li>\n<li>d</li>\n</ol>'
    )


def test_list_lazy_continuation_and_loose_items():
    assert markdown_to_html("- một\ntiếp\n- hai") == "<ul>\n<li>một tiếp</li>\n<li>hai</li>\n</ul>"
    loose = markdown_to_html("- một\n\n  đoạn hai của mục\n- hai")
    assert loose == "<ul>\n<li><p>một</p><p>đoạn hai của mục</p></li>\n<li>hai</li>\n</ul>"


def test_list_ends_at_other_blocks():
    out = markdown_to_html("- một\n### Tiêu đề\n- hai\n\nĐoạn")
    assert (
        out == "<ul>\n<li>một</li>\n</ul>\n<h3>Tiêu đề</h3>\n<ul>\n<li>hai</li>\n</ul>\n<p>Đoạn</p>"
    )


@pytest.mark.parametrize("space", ["\u3000", "\xa0", "\u2003"])
def test_list_line_after_unicode_space_does_not_crash(space):
    # ``_is_list_item`` xét ``line.strip()`` (bỏ cả khoảng trắng Unicode): dấu mục phải đọc đúng.
    assert markdown_to_html(f"{space}- một\n{space}- hai") == (
        "<ul>\n<li>một</li>\n<li>hai</li>\n</ul>"
    )
    assert_safe(markdown_to_html(f"đoạn\n{space}1. mục\n{space}\t2) mục"))


def test_table():
    out = markdown_to_html("| Loại | Ghi chú |\n|:---|---:|\n| inox | **bền** |\n| sắt \\| thép |")
    assert out == (
        "<table>\n<thead>\n<tr><th>Loại</th><th>Ghi chú</th></tr>\n</thead>\n<tbody>\n"
        "<tr><td>inox</td><td><strong>bền</strong></td></tr>\n"
        "<tr><td>sắt | thép</td><td></td></tr>\n</tbody>\n</table>"
    )


def test_pipe_lines_without_delimiter_are_paragraphs():
    assert markdown_to_html("| a | b |\n| c | d |") == "<p>| a | b |</p>\n<p>| c | d |</p>"


def test_blockquote_and_fence():
    out = markdown_to_html("> trích **dẫn**\n> dòng hai\n\n```python\n<x> & [y]\n  thụt\n```")
    assert out == (
        "<blockquote>\n<p>trích <strong>dẫn</strong> dòng hai</p>\n</blockquote>\n"
        "<pre><code>&lt;x&gt; &amp; &#91;y&#93;\n  thụt</code></pre>"
    )


def test_unclosed_fence_runs_to_end():
    assert markdown_to_html("```\na\nb") == "<pre><code>a\nb</code></pre>"


def test_deep_nesting_is_limited():
    deep = "\n".join("  " * level + "- mục" for level in range(MAX_DEPTH + 5))
    out = markdown_to_html(deep)
    assert_safe(out)
    assert out.count("<ul>") <= MAX_DEPTH
    quotes = markdown_to_html(">" * (MAX_DEPTH + 5) + " sâu")
    assert_safe(quotes)
    assert quotes.count("<blockquote>") <= MAX_DEPTH


# ------------------------------------------------------------------ trong dòng


@pytest.mark.parametrize(
    ("text", "html_text"),
    [
        ("**đậm** và *nghiêng*", "<strong>đậm</strong> và <em>nghiêng</em>"),
        ("__đậm__ và _nghiêng_", "<strong>đậm</strong> và <em>nghiêng</em>"),
        ("***cả hai***", "<em><strong>cả hai</strong></em>"),
        ("**đậm *lồng* đậm**", "<strong>đậm <em>lồng</em> đậm</strong>"),
        ("ten_bien_dai và 2*3*4", "ten_bien_dai và 2<em>3</em>4"),
        ("* không nghiêng *", "* không nghiêng *"),
        ("**chưa đóng", "**chưa đóng"),
        ("*a **b* c**", "<em>a <em><em>b</em> c</em></em>"),
        ("`mã **không đậm**`", "<code>mã **không đậm**</code>"),
        ("`` có ` bên trong ``", "<code>có ` bên trong</code>"),
        ("`chưa đóng", "`chưa đóng"),
    ],
)
def test_inline(text, html_text):
    assert inline_html(text) == html_text


def test_emphasis_always_balanced_fuzz():
    rng = random.Random(96)
    pieces = ["*", "**", "***", "_", "__", "a", " ", "b_c", "`", "\\*", "[", "]", "&amp;", "\n"]
    for _ in range(3000):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 25)))
        out = markdown_to_html(text)
        assert_safe(out)


def test_blocks_fuzz_stay_safe():
    rng = random.Random(9601)
    lines = [
        "# h", "## h2", "- a", "  - b", "1. c", "2) d", "| x | y |", "|---|---|", "> q", "```",
        "~~~", "---", "===", "", "chữ **đậm**", "[x](javascript:1)", "<b>", "https://x.vn",
        "    thụt", "\t- tab", "* * *", "&#91;", "\\", "`", "\u3000- rộng", "\xa01. nbsp",
    ]  # fmt: skip
    for _ in range(2000):
        text = "\n".join(rng.choice(lines) for _ in range(rng.randint(1, 15)))
        assert_safe(markdown_to_html(text))


# ------------------------------------------------------------------ khớp markdown_blocks


SAMPLE_BODY = """Cửa kéo bị kẹt thường do ray bẩn hoặc bánh xe mòn.

### Kiểm tra ray

- Lau sạch bụi trên ray dưới
- Tra dầu cho bánh xe trên
  1. Tháo nắp che
  2. Bôi mỡ chịu nhiệt

| Hiện tượng | Nguyên nhân |
|---|---|
| Kêu rít | Bánh xe khô dầu |

> Khách ở Tân Phú hay hỏi có cần thay ray không.

Nếu đã thử mà vẫn kẹt
thì nên gọi thợ kiểm tra tận nơi."""


def test_every_markdown_block_text_is_findable_in_html():
    """Chữ của mỗi khối ``markdown_blocks`` (bỏ dấu Markdown) có trong HTML: link AI gợi ý ở
    bước SEO tìm được đúng đoạn khi dựng bài."""
    html_text = markdown_to_html(SAMPLE_BODY)
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_text))
    for block in markdown_blocks(SAMPLE_BODY):
        words = re.sub(r"[#>|*_`-]|^\s*\d+[.)]", " ", block).split()
        if not words or set("".join(words)) <= set(":"):
            continue
        assert " ".join(words[:3]) in visible, block


# ------------------------------------------------------------------ tốc độ


@pytest.mark.parametrize(
    "unit",
    [
        "*a _b ",
        "**x* ",
        "`",
        "``a` ",
        "[x](y) ",
        "&#91;",
        "- a\n  - b\n",
        "| a | b |\n",
        "> q\n",
        "a  \n",
        "\\*",
    ],
)
def test_converter_scales_linearly(unit):
    assert_scales_linearly(markdown_to_html, lambda k: unit * (500 * k), label=unit)


# ------------------------------------------------------------------ lượt 2: đọc như bộ chuyển


@pytest.mark.parametrize(
    "body, block",
    [
        # Xuống dòng cứng: HTML có <br>, cụm từ không vắt qua được (SL-T096-2).
        ("Gọi dịch vụ sửa  \ncửa kéo", "Gọi dịch vụ sửa  \x00cửa kéo"),
        ("Gọi dịch vụ sửa\\\ncửa kéo", "Gọi dịch vụ sửa\x00cửa kéo"),
        # Mã ký tự, "\\" escape: như người đọc thấy.
        ("sửa cửa k&eacute;o \\*x\\* &bogus;", "sửa cửa kéo *x* &bogus;"),
        # Chỉ che đúng các đoạn `mã` (không che cả quãng giữa hai đoạn mã).
        ("Dùng `a` hoặc dịch vụ `b` nhé", "Dùng \x00\x00\x00 hoặc dịch vụ \x00\x00\x00 nhé"),
        ("``x ` y`` z", "\x00" * len("``x ` y``") + " z"),
        ("\\`không phải mã`", "`không phải mã`"),
    ],
)
def test_markdown_blocks_text_is_what_reader_sees(body, block):
    assert markdown_blocks(body) == [block]


def test_markdown_blocks_drop_extra_table_cells_like_gfm():
    body = "| Lỗi | Cách |\n|---|---|\n| Kẹt | Lau ray | gọi thợ kiểm tra |"
    blocks = markdown_blocks(body)
    assert blocks == ["| Lỗi | Cách |", "|---|---|", "| Kẹt | Lau ray |"]
    assert "gọi thợ" not in markdown_to_html(body)


@pytest.mark.parametrize("first", ["```lệnh``` là lệnh.", "``` aa ```", "```` `x`"])
def test_backtick_line_with_backticks_after_is_paragraph_in_both(first):
    body = f"{first}\n\nĐoạn sau."
    assert markdown_blocks(body)[-1] == "Đoạn sau."
    assert markdown_to_html(body).endswith("<p>Đoạn sau.</p>")
    assert "<pre>" not in markdown_to_html(body)


def test_real_fence_still_hides_code_in_both():
    body = "```python\nx = 1\n```\nĐoạn sau."
    assert markdown_blocks(body) == ["Đoạn sau."]
    assert markdown_to_html(body) == "<pre><code>x = 1</code></pre>\n<p>Đoạn sau.</p>"


def test_quote_lazy_line_joins_paragraph():
    out = markdown_to_html("> Kéo cửa thật chậm\nđể nghe tiếng kêu.\n\nĐoạn mới.")
    assert out == (
        "<blockquote>\n<p>Kéo cửa thật chậm để nghe tiếng kêu.</p>\n</blockquote>\n<p>Đoạn mới.</p>"
    )

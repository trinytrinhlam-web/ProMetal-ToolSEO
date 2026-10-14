"""Bộ lọc kết quả AI (T-004): bỏ HTML/link ở ranh giới nhận kết quả AI và lọc HTML
trước khi gửi WordPress (security.md 2.3, W3, A2). Không gọi mạng."""

import json
from html.parser import HTMLParser

import pytest
from fake_ai import OUTLINE, RESEARCH, SCORES, FakeProvider

from seo_app.ai import AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter
from seo_app.content.models import Draft, Flag, Review, Section, SectionText
from seo_app.content.rules import ContentRules
from seo_app.sanitize import clean_ai_text, is_safe_url, sanitize_html, strip_tags

MALICIOUS = [
    "<script>alert('xss')</script>",
    '<img src="x" onerror="alert(1)">',
    '<a href="javascript:alert(1)">bấm</a>',
    '<iframe src="https://evil.example"></iframe>',
    "<svg onload=alert(1)>",
    "<scr<script>ipt>alert(1)</script>",
    "<IMG SRC=x OnError=alert(1)>",
    '<img src=x onerror="alert(1)"',  # thẻ không đóng
    "<!--<img src=x onerror=alert(1)>-->",
    '<object data="x.swf"></object><embed src="x.swf">',
    '<form action="https://evil.example"><input name="p"></form>',
    "<style>body{display:none}</style>",
    "<details open ontoggle=alert(1)>",
]
BAD = ("<script", "<img", "<iframe", "<svg", "<object", "<embed", "<form", "<style", "<detail")


def _tags(markup: str) -> list[tuple[str, list]]:
    """Các thẻ thật mà trình duyệt sẽ dựng từ chuỗi HTML."""
    found: list[tuple[str, list]] = []

    class Collector(HTMLParser):
        def handle_starttag(self, tag, attrs):
            found.append((tag, attrs))

    Collector().feed(markup)
    return found


# ------------------------------------------------------- chữ Markdown từ AI


@pytest.mark.parametrize("payload", MALICIOUS)
def test_clean_ai_text_removes_every_tag(payload):
    out = clean_ai_text(f"Cổng sắt gỉ sau 2 năm. {payload} Hết.").lower()
    for bad in BAD:
        assert bad not in out
    assert out.startswith("cổng sắt gỉ sau 2 năm.")


def test_clean_ai_text_drops_script_content_and_keeps_vietnamese():
    out = clean_ai_text("Giá **3 triệu**.<script>alert(1)</script>\n\n- Ý một\n- Ý hai")
    assert out == "Giá **3 triệu**.\n\n- Ý một\n- Ý hai"


def test_clean_ai_text_keeps_harmless_angle_brackets():
    assert clean_ai_text("Cổng <5 m, độ dày > 1,2 mm") == "Cổng <5 m, độ dày > 1,2 mm"
    # "<" trước chữ cái không bao giờ còn là mở thẻ
    assert "<b" not in clean_ai_text("a<b c")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Xem [bảng giá](https://evil.example) nhé.", "Xem bảng giá nhé."),
        ("Bấm [đây](javascript:alert(1)).", "Bấm đây."),
        ("Ảnh ![cổng](https://evil.example/x.png) đẹp.", "Ảnh cổng đẹp."),
        ("Xem [đây][1].\n\n[1]: https://evil.example", "Xem [đây][1]."),
        ("Giá [cần bổ sung: giá cổng 2 cánh]", "Giá [cần bổ sung: giá cổng 2 cánh]"),
    ],
)
def test_clean_ai_text_strips_markdown_links(text, expected):
    assert clean_ai_text(text) == expected


def test_strip_tags_handles_nested_tricks():
    assert "<script" not in strip_tags("<scr<script>ipt>alert(1)</scr</script>ipt>").lower()


# ------------------------------------------------------ HTML gửi WordPress


@pytest.mark.parametrize("payload", MALICIOUS)
def test_sanitize_html_blocks_dangerous_markup(payload):
    out = sanitize_html(f"<p>Bài viết</p>{payload}")
    tags = _tags(out)
    assert {t for t, _ in tags} <= {"p", "img", "a", "div", "span"}, tags
    for _, attrs in tags:
        for name, value in attrs:
            assert not name.startswith("on") and name != "style"
            assert "javascript:" not in (value or "").lower()
    assert "<script" not in out.lower() and "onerror" not in out.lower()
    assert out.startswith("<p>Bài viết</p>")


@pytest.mark.parametrize(
    "href",
    [
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        " javascript:alert(1)",
        "java\tscript:alert(1)",
        "java&#x09;script:alert(1)",
        "&#106;avascript:alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "vbscript:msgbox(1)",
        "\\\\evil.example",
    ],
)
def test_sanitize_html_drops_unsafe_links(href):
    out = sanitize_html(f'<p><a href="{href}">bấm</a></p>')
    assert out == "<p><a>bấm</a></p>"
    assert not is_safe_url(href)


@pytest.mark.parametrize("url", ["https://suachuacuasat.com/bai", "/lien-he", "#muc-1", "tel:090"])
def test_safe_links_are_kept(url):
    assert is_safe_url(url)
    assert f'href="{url}"' in sanitize_html(f'<a href="{url}">x</a>')


def test_sanitize_html_keeps_normal_article_markup():
    article = (
        '<h2 id="gia">Giá cổng</h2>\n<p>Cổng <strong>inox 304</strong> &amp; sơn tĩnh điện.</p>'
        "\n<ul><li>Ý một</li><li>Ý hai</li></ul>\n"
        '<figure><img src="https://site.vn/a.webp" alt="Cổng sắt" width="800">'
        "<figcaption>Ảnh thật</figcaption></figure>\n"
        '<table><tr><th scope="col">Loại</th></tr><tr><td colspan="2">201</td></tr></table>'
    )
    assert sanitize_html(article) == article


def test_sanitize_html_removes_style_and_event_attributes():
    out = sanitize_html('<p style="background:url(javascript:x)" onclick="x()" class="a">A</p>')
    assert out == '<p class="a">A</p>'


def test_sanitize_html_keeps_escaped_text_escaped():
    out = sanitize_html("<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>")
    assert out == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"


def test_sanitize_html_closes_unbalanced_tags_and_drops_comments():
    assert sanitize_html("<p><strong>A<!-- wp:html --></p>") == "<p><strong>A</strong></p>"
    assert sanitize_html("A</div></p>") == "A"


def test_unclosed_dangerous_tag_drops_the_rest():
    assert sanitize_html("<p>A</p><iframe><p>B</p>") == "<p>A</p>"


# --------------------------------------------- ranh giới nhận kết quả AI


TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
    for name in ("research", "outline", "write", "rewrite", "review")
}
RULES = ContentRules(business_profile="", address="", tone="", banned=(), checklist=())
XSS = '<img src="x" onerror="alert(1)">'


class EvilProvider(FakeProvider):
    """AI bị trang đối thủ "dụ" chèn HTML và link vào mọi chỗ."""

    def generate(self, task, *, system, prompt, schema):
        self.calls.append((task.name, system, prompt))
        if schema is Draft:
            return Draft(
                title="Tiêu đề<script>x()</script>",
                intro=f"Mở bài. {XSS} Xem [đây](https://evil.example).",
                sections=[
                    Section(heading=f"{i.heading}<b>", body="Thân bài.<script>alert(2)</script>")
                    for i in OUTLINE.items
                ],
            )
        if schema is SectionText:
            return SectionText(body="Bản mới. <iframe src='https://evil.example'></iframe>")
        if schema is Review:
            flag = Flag(
                section=0,
                sentence="Mở bài.",
                reason="Thiếu <i>ví dụ</i>",
                replacement='Mở bài cụ thể. <a href="javascript:alert(1)">bấm</a>',
            )
            return Review(scores=SCORES, flags=[flag], summary="<b>Ổn</b>")
        return super().generate(task, system=system, prompt=prompt, schema=schema)


@pytest.fixture
def writer(monkeypatch):
    provider = EvilProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return ContentWriter(AIRouter(TASKS, Settings()), RULES)


def _assert_clean(text: str) -> None:
    lower = text.lower()
    for bad in ("<script", "<img", "<iframe", "<a ", "<b>", "<i>", "onerror", "javascript:", "]("):
        assert bad not in lower, text


def test_write_cleans_title_intro_headings_and_bodies(writer):
    title, parts = writer.write("cửa sắt", RESEARCH, {}, OUTLINE)
    _assert_clean(title)
    assert title == "Tiêu đề"
    assert parts[0].body == "Mở bài.  Xem đây."
    for part in parts:
        _assert_clean(part.heading)
        _assert_clean(part.body)


def test_rewrite_section_is_cleaned(writer):
    _, parts = writer.write("cửa sắt", RESEARCH, {}, OUTLINE)
    body = writer.rewrite_section("cửa sắt", "t", parts, 1)
    assert body == "Bản mới."


def test_review_replacement_reason_and_summary_are_cleaned(writer):
    _, parts = writer.write("cửa sắt", RESEARCH, {}, OUTLINE)
    review = writer.review("cửa sắt", "t", parts)
    assert review.summary == "Ổn"
    flag = review.flags[0]
    assert flag.replacement == "Mở bài cụ thể. bấm"
    assert flag.reason == "Thiếu ví dụ"


def test_write_and_review_applies_only_cleaned_replacements(writer):
    _, parts, _, fixed = writer.write_and_review("cửa sắt", RESEARCH, {}, OUTLINE)
    assert fixed == 1
    for part in parts:
        _assert_clean(part.body)


# ------------------------------------------------- client WordPress


def test_create_draft_sanitizes_content_excerpt_and_title(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/posts", {"id": 1, "status": "draft", "title": "A"})
    wp_client.create_draft(
        "Cổng <script>x()</script>sắt",
        f"<p>Bài</p>{XSS}<script>alert(1)</script>",
        excerpt='<p onclick="x()">Tóm tắt</p><iframe src="https://evil.example"></iframe>',
    )
    body = json.loads(fake_wp.requests[-1].body)
    assert body["status"] == "draft"
    assert body["title"] == "Cổng sắt"
    assert body["content"] == '<p>Bài</p><img src="x">'
    assert body["excerpt"] == "<p>Tóm tắt</p>"


def test_create_draft_rejects_title_that_is_only_markup(wp_client):
    from seo_app.wordpress import WordPressError

    with pytest.raises(WordPressError):
        wp_client.create_draft("<script>alert(1)</script>", "<p>A</p>")

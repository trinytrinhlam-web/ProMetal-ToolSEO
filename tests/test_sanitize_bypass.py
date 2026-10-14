"""Soi Lỗi thử LÁCH bộ lọc của T-004 (``seo_app/sanitize.py``) và T-005 (``ui.highlight``).

Test qua = bộ lọc đứng vững trước cách lách đó. Test ``xfail(strict=True)`` = lách được
(lỗi đã ghi trong ``docs/team/reports/T-004-T-005-soi-loi.md``); khi sửa xong, test sẽ báo
XPASS và phải gỡ dấu ``xfail``. Không gọi mạng.
"""

import re
from html.parser import HTMLParser

import pytest

from seo_app.sanitize import ALLOWED_TAGS, clean_ai_text, is_safe_url, sanitize_html
from seo_app.ui import highlight

# Ký tự trình duyệt bỏ qua khi đọc scheme của URL (đầu/cuối: C0 + dấu cách; giữa: tab/xuống dòng).
_BROWSER_STRIP = re.compile(r"[\x00-\x20]")
_BAD_SCHEMES = ("javascript:", "vbscript:", "data:", "livescript:")


def _browser_tags(markup: str) -> list[tuple[str, dict[str, str]]]:
    """Thẻ và thuộc tính mà trình duyệt dựng từ chuỗi HTML (đọc độc lập với bộ lọc)."""
    found: list[tuple[str, dict[str, str]]] = []

    class Collector(HTMLParser):
        def handle_starttag(self, tag, attrs):
            found.append((tag, {k: v or "" for k, v in attrs}))

        handle_startendtag = handle_starttag

    Collector(convert_charrefs=True).feed(markup)
    return found


def _assert_harmless_html(out: str) -> None:
    for tag, attrs in _browser_tags(out):
        assert tag in ALLOWED_TAGS, (tag, out)
        for name, value in attrs.items():
            assert not name.startswith("on"), (name, out)
            assert name not in {"style", "srcdoc", "formaction", "xlink:href", "background"}
            compact = _BROWSER_STRIP.sub("", value).lower()
            assert not compact.startswith(_BAD_SCHEMES), (name, value, out)


# ------------------------------------------------------ sanitize_html: cách lách bị chặn

SANITIZE_PAYLOADS = [
    "<ScRiPt>alert(1)</sCrIpT>",
    "<IMG SRC=x OnErRoR=alert(1)>",
    "<img/src=x/onerror=alert(1)>",
    "<img src=x:alert(alt) onerror=eval(src) alt=0>",
    "<a href=javascript:alert(1)>a</a>",  # thuộc tính không ngoặc
    '<a href="jav&#x09;ascript:alert(1)">a</a>',  # mã hex có dấu chấm phẩy
    # mã thập phân thiếu dấu chấm phẩy
    '<a href="&#106&#97&#118&#97&#115&#99&#114&#105&#112&#116&#58alert(1)">a</a>',
    '<a href="&#0000106avascript:alert(1)">a</a>',  # số 0 đệm
    '<a href="&#x6A;avascript:alert(1)">a</a>',
    '<a href="javas&#99ript:alert(1)">a</a>',
    '<a href="java&Tab;script:alert(1)">a</a>',
    '<a href="javascript&NewLine;:alert(1)">a</a>',
    '<a href="JaVaScRiPt&colon;alert(1)">a</a>',
    '<a href="\x01javascript:alert(1)">a</a>',  # ký tự điều khiển ở đầu
    '<a href=" &#14;javascript:alert(1)">a</a>',
    '<a href="java\nscript:alert(1)">a</a>',
    '<a href="javascript\x00:alert(1)">a</a>',
    '<a href="java script:alert(1)">a</a>',  # khoảng trắng Unicode
    '<a href="vbscript:msgbox(1)">a</a>',
    '<a href="data:text/html,<script>alert(1)</script>">a</a>',
    '<a href="feed:javascript:alert(1)">a</a>',
    '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
    "<div srcdoc=x>t</div>",
    "<svg><script>alert(1)</script></svg>",
    "<svg/onload=alert(1)>",
    '<math><mi xlink:href="javascript:alert(1)">x</mi></math>',
    '<a href="https://vi.wikipedia.org"><a href="javascript:alert(1)">lồng</a></a>',
    "<!--[if IE]><script>alert(1)</script><![endif]-->",
    "<![CDATA[<script>alert(1)</script>]]>",
    "<img src=x onerror=alert(1)",  # thẻ không đóng
    "<scr<script>ipt>alert(1)</script>",
    "< script>alert(1)</script>",  # "<" không chuẩn
    '<a href="https://vi.wikipedia.org" onclick=alert(1)>x</a>',
    '<img src="https://a.example/b.png" srcset="javascript:alert(1) 1x">',
    '<p style="background:url(javascript:alert(1))">x</p>',
    '<base href="javascript:/">',
    '<noscript><p title="</noscript><img src=x onerror=alert(1)>"></noscript>',
    "<style><img src=x onerror=alert(1)></style>",
    "<title><img src=x onerror=alert(1)></title>",
    "<xmp><img src=x onerror=alert(1)></xmp>",
    "<details open ontoggle=alert(1)>x</details>",
    '<p title="a&quot;onmouseover=alert(1)">x</p>',
    '<table background="javascript:alert(1)"><tr><td>x</td></tr></table>',
    '<form><button formaction="javascript:alert(1)">b</button></form>',
]


@pytest.mark.parametrize("payload", SANITIZE_PAYLOADS)
def test_sanitize_html_resists_bypass(payload):
    _assert_harmless_html(sanitize_html(f"<p>Trước</p>{payload}<p>Sau</p>"))


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        " JAVASCRIPT:alert(1)",
        "java\tscript:alert(1)",
        "\x00javascript:alert(1)",
        "&#106;avascript:alert(1)",
        "&#x6a&#x61vascript:alert(1)",
        "vbscript:x",
        "data:image/svg+xml,<svg onload=alert(1)>",
        "\\\\evil.example",
    ],
)
def test_is_safe_url_rejects(url):
    assert not is_safe_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://vi.wikipedia.org/wiki/Thép",
        "/bai-viet/cong-sat",
        "#muc-2",
        "mailto:a@b.vn",
        "tel:0909",
    ],
)
def test_is_safe_url_accepts_normal_links(url):
    assert is_safe_url(url)


def test_sanitize_html_keeps_normal_vietnamese_article():
    article = (
        "<h2>Cổng sắt mỹ thuật: chọn loại nào?</h2>"
        "<p>Đoạn văn có <strong>đậm</strong>, <em>nghiêng</em> &amp; ký hiệu &lt;3.</p>"
        '<ul><li>Một</li><li>Hai</li></ul><ol start="3"><li>Ba</li></ol>'
        '<p><a href="https://vi.wikipedia.org/wiki/Thép?a=1&amp;b=2" rel="noopener">Thép</a></p>'
        '<figure><img src="https://a.example/cổng.webp" alt="Cổng sắt sơn tĩnh điện">'
        "<figcaption>Ảnh thật</figcaption></figure>"
    )
    out = sanitize_html(article)
    assert out == article
    _assert_harmless_html(out)


# Thẻ "rỗng" (không có thẻ đóng) nằm trong danh sách nguy hiểm nhưng thiếu trong VOID_TAGS
# (seo_app/sanitize.py:90, :154) → bộ lọc chờ thẻ đóng không bao giờ tới và nuốt hết phần sau.
@pytest.mark.xfail(
    strict=True,
    reason="Soi Lỗi T-004 #3: <embed>/<input>/<link>/<meta>/<base> làm mất toàn bộ nội dung sau",
)
@pytest.mark.parametrize(
    "void",
    [
        '<embed src="x.swf">',
        '<input name="p">',
        '<link rel="x">',
        "<meta charset=utf-8>",
        "<base href=/>",
    ],
)
def test_dangerous_void_tag_does_not_swallow_rest_of_article(void):
    out = sanitize_html(f"<p>Mở bài</p>{void}<p>Nội dung phía sau rất quan trọng</p>")
    assert "Nội dung phía sau rất quan trọng" in out


# ------------------------------------------------------ clean_ai_text: thẻ HTML

AI_TAG_PAYLOADS = [
    "<ScRiPt>alert(1)</sCrIpT>",
    "<img src=x onerror=alert(1)",
    '<img src=x alt=">" onerror=alert(1)>',
    "<javascript:alert(1)>",  # autolink Markdown
    '<a\nhref="javascript:alert(1)">x</a>',
    "<!--[if IE]><img src=x onerror=1><![endif]-->",
    "<![CDATA[<img src=x onerror=1>]]>",
    "<<script>script>alert(1)<</script>/script>",
    "<svg><style><img src=x onerror=1></style></svg>",
    "<math><mi xlink:href=javascript:alert(1)>x</mi></math>",
]


@pytest.mark.parametrize("payload", AI_TAG_PAYLOADS)
def test_clean_ai_text_leaves_no_tag(payload):
    out = clean_ai_text(f"Cổng sắt gỉ sau 2 năm. {payload} Hết.")
    assert not re.search(r"<[A-Za-z/!?]", out), out
    assert out.startswith("Cổng sắt gỉ sau 2 năm.")


@pytest.mark.parametrize(
    "payload",
    [
        "[x](javascript:alert(1))",
        "[x]( <javascript:alert(1)> )",
        "[x](<javascript:alert(1)>)",
        '[x](javascript:alert(1) "a(b)")',
        "[x](javascript:alert\\(1\\))",
        "![a](javascript:alert(1))",
        "[a [b](javascript:1)](javascript:2)",
        "[x][r]\n\n[r]: javascript:alert(1)",
        "[x][r]\n\n[r]: <javascript:alert(1)>",
        "[r]\n\n   [r]: javascript:alert(1)",
        "\t[x]:javascript:alert(1)\n\n[y][x]",
        '[x](https://evil.example "t")',
    ],
)
def test_clean_ai_text_drops_markdown_link_targets(payload):
    out = clean_ai_text(payload)
    assert "javascript" not in out and "evil.example" not in out, out


# Các dạng link hợp lệ theo CommonMark (Streamlit và hầu hết bộ chuyển Markdown → HTML đều
# dựng thành link) nhưng regex ở seo_app/sanitize.py:39-43 không nhận ra → link ẩn lọt qua.
MARKDOWN_LINK_BYPASS = [
    pytest.param("[x](https://evil.example/a(b(c)))", id="ngoac-long-2-cap"),
    pytest.param("[a [b] c](https://evil.example)", id="nhan-co-ngoac-vuong"),
    pytest.param("[a\\]b](https://evil.example)", id="nhan-co-ngoac-escape"),
    pytest.param("[Xem bảng\ngiá](https://evil.example)", id="nhan-2-dong"),
    pytest.param("[x](\nhttps://evil.example)", id="dia-chi-xuong-dong"),
    pytest.param('[x](https://evil.example\n"t")', id="tieu-de-xuong-dong"),
    pytest.param("[x][r]\n\n[r]:\n  https://evil.example", id="tham-chieu-dia-chi-dong-sau"),
    pytest.param("![a][i]\n\n[i]:\n https://evil.example/t.png", id="anh-tham-chieu-dong-sau"),
    pytest.param("[x](javascript:a(b(c)))", id="javascript-ngoac-long"),
]


@pytest.mark.xfail(
    strict=True,
    reason="Soi Lỗi T-004 #1, #2: link Markdown hợp lệ CommonMark lọt qua strip_markdown_links",
)
@pytest.mark.parametrize("payload", MARKDOWN_LINK_BYPASS)
def test_clean_ai_text_drops_commonmark_link_variants(payload):
    out = clean_ai_text(payload)
    assert "evil.example" not in out and "javascript" not in out, out


def test_clean_ai_text_keeps_normal_vietnamese_markdown():
    text = (
        "## Chọn cổng sắt\n\nĐoạn **đậm** và *nghiêng*, giá 1 < 2 và 5 > 3.\n\n"
        "- Một\n- Hai\n\n1. Bước một\n2. Bước hai\n\n[cần bổ sung: giá thực tế]"
    )
    assert clean_ai_text(text) == text


# ------------------------------------------------------ ui.highlight (T-005)

HIGHLIGHT_PAYLOADS = [
    "<ScRiPt>alert(1)</sCrIpT>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    '"><img src=x onerror=alert(1)>',
    "<!--><img src=x onerror=alert(1)>-->",
    "<![CDATA[><img src=x onerror=alert(1)>]]>",
    "&lt;script&gt;alert(1)&lt;/script&gt;",
    "<a href=javascript:alert(1)>x</a>",
    "<javascript:alert(1)>",
]


@pytest.mark.parametrize("payload", HIGHLIGHT_PAYLOADS)
def test_highlight_only_emits_mark_tags(payload):
    text = f"Cổng sắt gỉ sau 2 năm. {payload} Hết."
    out = highlight(text, tone=[payload, "Cổng sắt"], missing=["2 năm", payload[:5]])
    tags = _browser_tags(out)
    assert all(tag == "mark" for tag, _ in tags), out
    assert all(attrs in ({"class": "tone"}, {"class": "missing"}) for _, attrs in tags), out


def test_highlight_marks_tone_and_missing_on_vietnamese():
    out = highlight("Giá “3 triệu” & bền.", tone=["Giá “3 triệu”"], missing=["bền"])
    assert out == '<mark class="tone">Giá “3 triệu”</mark> &amp; <mark class="missing">bền</mark>.'

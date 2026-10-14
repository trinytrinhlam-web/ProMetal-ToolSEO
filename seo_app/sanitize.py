"""Lọc nội dung chưa tin cậy (kết quả AI) trước khi hiển thị hoặc gửi lên WordPress.

Hai lớp, chỉ dùng thư viện chuẩn (security.md mục 2.3, 2.4):

- ``clean_ai_text``: dùng ngay khi nhận chữ Markdown từ AI. Bỏ MỌI thẻ HTML, bỏ địa chỉ của
  link/ảnh Markdown (giữ chữ), vì AI không được tự chèn link hay mã vào bài.
- ``sanitize_html``: dùng ngay trước khi gửi HTML lên WordPress. Chỉ giữ các thẻ và thuộc tính
  trong danh sách cho phép; bỏ hẳn ``<script>``, ``<iframe>``, ``<object>``, ``<embed>``,
  ``<form>``, ``<style>``…, mọi thuộc tính ``on*=``/``style``, link ``javascript:``/``data:``.
"""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser

# Thẻ bị bỏ CẢ nội dung bên trong (không chỉ bỏ thẻ).
DANGEROUS_TAGS = frozenset(
    {
        "script", "style", "iframe", "frame", "frameset", "object", "embed", "applet",
        "form", "input", "button", "select", "textarea", "option", "noscript", "template",
        "svg", "math", "base", "link", "meta", "title", "head", "noembed", "noframes",
        "xmp", "plaintext", "portal",
    }
)  # fmt: skip

# ---------------------------------------------------------------- chữ Markdown từ AI

_DANGEROUS_BLOCK = re.compile(
    r"<\s*(" + "|".join(sorted(DANGEROUS_TAGS)) + r")\b[^>]*>.*?<\s*/\s*\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
_TAG = re.compile(r"<[A-Za-z/!?][^<>]*>")
# "<" ngay trước chữ cái, "/", "!" hoặc "?" là chỗ trình duyệt bắt đầu một thẻ.
_TAG_OPEN = re.compile(r"<(?=[A-Za-z/!?])")
# ![chữ](địa chỉ) và [chữ](địa chỉ); không đụng tới [cần bổ sung: ...] vì không có "(".
_MD_URL = r"\((?:[^()\n]|\([^()\n]*\))*\)"  # cho phép một cặp ngoặc trong địa chỉ
_MD_IMAGE = re.compile(r"!\[([^\]\n]*)\]" + _MD_URL)
_MD_LINK = re.compile(r"\[([^\]\n]*)\]" + _MD_URL)
# [nhãn]: https://... (link kiểu tham chiếu)
_MD_LINK_DEF = re.compile(r"^[ \t]*\[[^\]\n]+\]:[ \t]*\S+.*$", re.MULTILINE)


def strip_tags(text: str) -> str:
    """Bỏ mọi thẻ HTML (kể cả lồng nhau kiểu ``<scr<script>ipt>``) và nội dung thẻ nguy hiểm.

    Dấu "<" còn sót mà trình duyệt có thể hiểu là mở thẻ được tách bằng một dấu cách
    ("<img" thành "< img"), nên không bao giờ thành thẻ thật.
    """
    previous = None
    while previous != text:
        previous = text
        text = _DANGEROUS_BLOCK.sub("", text)
        text = _COMMENT.sub("", text)
        text = _TAG.sub("", text)
    return _TAG_OPEN.sub("< ", text)


def strip_markdown_links(text: str) -> str:
    """``[chữ](url)`` thành ``chữ``; ảnh Markdown và dòng khai báo link bị bỏ.

    AI không được tự chèn link: link nội bộ do app gắn ở bước sau, link ra ngoài phải được
    người dùng thêm và nhìn thấy (security.md 2.3).
    """
    previous = None
    while previous != text:
        previous = text
        text = _MD_IMAGE.sub(r"\1", text)
        text = _MD_LINK.sub(r"\1", text)
    return _MD_LINK_DEF.sub("", text)


def clean_ai_text(text: str) -> str:
    """Làm sạch một đoạn Markdown do AI viết: không còn thẻ HTML, không còn link ẩn."""
    return strip_markdown_links(strip_tags(text)).strip()


# --------------------------------------------------------------- HTML gửi WordPress

ALLOWED_TAGS = frozenset(
    {
        "p", "br", "hr", "h2", "h3", "h4", "h5", "h6", "strong", "b", "em", "i", "u", "s",
        "sub", "sup", "mark", "small", "code", "pre", "blockquote", "q", "cite", "abbr",
        "ul", "ol", "li", "dl", "dt", "dd", "a", "img", "figure", "figcaption",
        "table", "caption", "thead", "tbody", "tfoot", "tr", "th", "td", "div", "span",
    }
)  # fmt: skip
VOID_TAGS = frozenset({"br", "hr", "img"})
GLOBAL_ATTRS = frozenset({"class", "id", "title", "lang", "dir"})
TAG_ATTRS = {
    "a": frozenset({"href", "rel"}),
    "img": frozenset({"src", "alt", "width", "height", "loading", "srcset", "sizes"}),
    "th": frozenset({"colspan", "rowspan", "scope"}),
    "td": frozenset({"colspan", "rowspan"}),
    "ol": frozenset({"start", "reversed", "type"}),
    "blockquote": frozenset({"cite"}),
    "q": frozenset({"cite"}),
    "abbr": frozenset({"title"}),
}
URL_ATTRS = frozenset({"href", "src", "cite"})
SAFE_SCHEMES = frozenset({"http", "https", "mailto", "tel"})
_SCHEME = re.compile(r"^([a-z][a-z0-9+.\-]*):")
# Trình duyệt bỏ qua ký tự điều khiển và khoảng trắng khi đọc "java\tscript:".
_IGNORED_IN_URL = re.compile(r"[\x00-\x20\x7f-\x9f\u00ad\u200b-\u200f\u2028\u2029\ufeff]")


def is_safe_url(url: str) -> bool:
    """Chỉ cho http(s), mailto, tel và đường dẫn tương đối (``/bai-viet``, ``#muc``)."""
    compact = _IGNORED_IN_URL.sub("", html.unescape(url)).lower()
    match = _SCHEME.match(compact)
    if match is None:
        # Không có "tên:" ở đầu → tương đối. Chặn thêm "\\evil" (trình duyệt hiểu là //evil).
        return not compact.startswith("\\")
    return match.group(1) in SAFE_SCHEMES


def _is_safe_srcset(value: str) -> bool:
    return all(is_safe_url(item.strip().split(" ")[0]) for item in value.split(",") if item.strip())


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.open: list[str] = []
        self.skip_tag: str | None = None
        self.skip_depth = 0

    def _attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        allowed = GLOBAL_ATTRS | TAG_ATTRS.get(tag, frozenset())
        parts = []
        seen: set[str] = set()
        for name, value in attrs:
            name = name.lower()
            if name not in allowed or name in seen:
                continue
            value = value or ""
            if name in URL_ATTRS and not is_safe_url(value):
                continue
            if name == "srcset" and not _is_safe_srcset(value):
                continue
            seen.add(name)
            parts.append(f' {name}="{html.escape(value, quote=True)}"')
        return "".join(parts)

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], *, closed: bool) -> None:
        if self.skip_tag is not None:
            if tag == self.skip_tag and not closed:
                self.skip_depth += 1
            return
        if tag in DANGEROUS_TAGS:
            if not closed and tag not in VOID_TAGS:
                self.skip_tag, self.skip_depth = tag, 1
            return
        if tag not in ALLOWED_TAGS:
            return  # bỏ thẻ lạ, giữ chữ bên trong
        self.out.append(f"<{tag}{self._attrs(tag, attrs)}>")
        if tag not in VOID_TAGS and not closed:
            self.open.append(tag)
        elif tag not in VOID_TAGS:
            self.out.append(f"</{tag}>")

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, closed=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, closed=True)

    def handle_endtag(self, tag):
        if self.skip_tag is not None:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            return
        if tag in VOID_TAGS or tag not in self.open:
            return
        # Đóng cả các thẻ con còn mở để HTML luôn cân.
        while self.open:
            last = self.open.pop()
            self.out.append(f"</{last}>")
            if last == tag:
                break

    def handle_data(self, data):
        if self.skip_tag is None:
            self.out.append(html.escape(data, quote=False))

    # Bình luận, <!DOCTYPE>, <?...?> và CDATA đều bị bỏ.
    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def unknown_decl(self, data):
        pass

    def result(self) -> str:
        self.close()
        while self.open:
            self.out.append(f"</{self.open.pop()}>")
        return "".join(self.out)


def sanitize_html(content: str) -> str:
    """Lọc HTML theo danh sách cho phép trước khi gửi lên WordPress (security.md 2.3)."""
    parser = _Sanitizer()
    parser.feed(content)
    return parser.result()

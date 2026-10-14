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
#
# Mọi hàm ở đây chạy trong thời gian tuyến tính theo độ dài chữ: AI có thể bị trang đối thủ
# dụ trả về bài rất dài toàn "<script>" hoặc "[" để làm treo app (Lá Chắn T-004 #1).

_DANGEROUS_OPEN = re.compile(r"<\s*(" + "|".join(sorted(DANGEROUS_TAGS)) + r")\b", re.IGNORECASE)
_DANGEROUS_CLOSE = {
    tag: re.compile(r"<\s*/\s*" + tag + r"\s*>", re.IGNORECASE) for tag in DANGEROUS_TAGS
}
_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
_TAG = re.compile(r"<[A-Za-z/!?][^<>]*>")
# "<" ngay trước chữ cái, "/", "!" hoặc "?" là chỗ trình duyệt bắt đầu một thẻ.
_TAG_OPEN = re.compile(r"<(?=[A-Za-z/!?])")
# Số lượt bóc thẻ lồng nhau (``<scr<script>ipt>`` cần 2 lượt). Lồng sâu hơn thì phần "<" còn
# sót vẫn bị ``_TAG_OPEN`` vô hiệu hóa, nên giới hạn này chỉ ảnh hưởng tới chữ thừa, không
# ảnh hưởng an toàn.
_MAX_PASSES = 8


def _drop_dangerous_blocks(text: str) -> str:
    """Bỏ ``<script …>…</script>`` (và các thẻ nguy hiểm khác) cùng nội dung bên trong.

    Thẻ mở không có thẻ đóng thì giữ lại để ``_TAG`` bỏ riêng thẻ. Chạy một lượt từ trái sang
    phải: mỗi đoạn chữ chỉ được quét một lần.
    """
    out: list[str] = []
    pos = 0
    next_gt = -1  # vị trí ">" gần nhất đã tìm (dùng lại, tránh quét lại cùng một đoạn)
    no_close: set[str] = set()  # thẻ đã biết là không còn thẻ đóng nào phía sau
    while (match := _DANGEROUS_OPEN.search(text, pos)) is not None:
        if next_gt < match.end():
            next_gt = text.find(">", match.end())
            if next_gt == -1:
                break  # không còn ">" nào: không còn thẻ mở hoàn chỉnh
        tag = match.group(1).lower()
        close = None
        if tag not in no_close:
            close = _DANGEROUS_CLOSE[tag].search(text, next_gt + 1)
        if close is None:
            no_close.add(tag)
            out.append(text[pos : match.end()])
            pos = match.end()
            continue
        out.append(text[pos : match.start()])
        pos = next_gt = close.end()
    out.append(text[pos:])
    return "".join(out)


def strip_tags(text: str) -> str:
    """Bỏ mọi thẻ HTML (kể cả lồng nhau kiểu ``<scr<script>ipt>``) và nội dung thẻ nguy hiểm.

    Dấu "<" còn sót mà trình duyệt có thể hiểu là mở thẻ được tách bằng một dấu cách
    ("<img" thành "< img"), nên không bao giờ thành thẻ thật.
    """
    for _ in range(_MAX_PASSES):
        previous = text
        text = _drop_dangerous_blocks(text)
        text = _COMMENT.sub("", text)
        text = _TAG.sub("", text)
        if text == previous:
            break
    return _TAG_OPEN.sub("< ", text)


# Ký tự Markdown cho phép escape bằng "\" (CommonMark: mọi dấu câu ASCII).
_ESCAPABLE = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
# Dòng trống: kết thúc đoạn văn, link Markdown không bao giờ vượt qua.
_BLANK_LINE_AFTER = re.compile(r"[ \t]*\n")
# [nhãn]: địa chỉ (link kiểu tham chiếu). Rộng hơn CommonMark cho chắc: nhãn nhiều dòng, địa
# chỉ ở dòng sau, nằm trong trích dẫn (">") hoặc danh sách ("-", "1.").
_MD_LINK_DEF = re.compile(
    r"^[ \t>*+\-\d.)]*\[(?:[^\[\]\\]|\\.)+\]:[ \t]*\n?[ \t]*\S.*$", re.MULTILINE
)


def _is_blank_line_start(text: str, newline: int) -> bool:
    """Ký tự ``text[newline]`` là "\n" và dòng ngay sau nó là dòng trống."""
    return _BLANK_LINE_AFTER.match(text, newline + 1) is not None


def _matching_parens(text: str) -> dict[int, int]:
    """Vị trí "(" → vị trí ")" khớp với nó (bỏ qua ngoặc escape, không vượt dòng trống)."""
    pairs: dict[int, int] = {}
    stack: list[int] = []
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            i += 2
            continue
        if char == "(":
            stack.append(i)
        elif char == ")" and stack:
            pairs[stack.pop()] = i
        elif char == "\n" and stack and _is_blank_line_start(text, i):
            stack.clear()
        i += 1
    return pairs


def strip_markdown_links(text: str) -> str:
    """``[chữ](url)`` thành ``chữ``; ảnh Markdown và dòng khai báo link bị bỏ.

    AI không được tự chèn link: link nội bộ do app gắn ở bước sau, link ra ngoài phải được
    người dùng thêm và nhìn thấy (security.md 2.3).

    Không đoán link bằng một biểu thức chính quy (dễ sót các dạng CommonMark ít gặp: ngoặc
    lồng nhiều tầng, nhãn có "[ ]", nhãn hoặc địa chỉ xuống dòng). Thay vào đó đọc một lượt:
    hễ có ``](`` mà dấu "(" có ")" khớp (cùng đoạn văn) thì bỏ cả phần ``](…)``, cùng "[" mở
    nhãn và "!" của ảnh. Cách này bắt rộng hơn CommonMark: có thể bỏ thừa một địa chỉ vốn
    hiện thành chữ, nhưng không để sót link nào.
    """
    pairs = _matching_parens(text)
    n = len(text)
    drop = bytearray(n)  # 1 = bỏ ký tự này
    openers: list[int] = []  # vị trí các "[" chưa đóng
    i = 0
    while i < n:
        char = text[i]
        if char == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            i += 2
            continue
        if char == "[":
            openers.append(i)
        elif char == "\n" and openers and _is_blank_line_start(text, i):
            openers.clear()
        elif char == "]":
            opener = openers.pop() if openers else None
            close = pairs.get(i + 1)
            if close is not None:
                drop[i : close + 1] = b"\x01" * (close + 1 - i)
                if opener is not None:
                    drop[opener] = 1
                    bang = opener - 1  # "!" của ảnh, trừ khi đã escape "\\!"
                    if bang >= 0 and text[bang] == "!" and text[max(bang - 1, 0) : bang] != "\\":
                        drop[bang] = 1
                i = close + 1
                continue
        i += 1
    if any(drop):
        text = "".join(char for char, dropped in zip(text, drop, strict=True) if not dropped)
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
# Thẻ nguy hiểm theo chuẩn HTML không bao giờ có thẻ đóng: chỉ bỏ thẻ, không chờ thẻ đóng
# (nếu chờ thì mất toàn bộ phần bài phía sau, Soi Lỗi T-004 #3).
DANGEROUS_VOID_TAGS = frozenset({"input", "base", "link", "meta", "embed", "frame"})
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
        # Không có "tên:" ở đầu → tương đối. Trình duyệt coi dấu \ như "/", nên //evil,
        # /\evil, \/evil, \\evil đều là link ra ngoài tới evil (cùng giao thức), dù
        # nhìn giống link nội bộ: chặn hết, chỉ cho "/đường-dẫn", "#mục", "?q=", "tên-file".
        return not compact.startswith(("//", "/\\", "\\"))
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
            if not closed and tag not in DANGEROUS_VOID_TAGS:
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

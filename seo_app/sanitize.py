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
from bisect import bisect_right
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
# [nhãn]: địa chỉ ["tiêu đề"] (link kiểu tham chiếu). Rộng hơn CommonMark cho chắc: nhãn nhiều
# dòng, địa chỉ ở dòng sau, nằm trong trích dẫn (">") hoặc danh sách ("-", "1."). Nhưng sau địa
# chỉ chỉ được có tiêu đề rồi hết dòng, đúng như CommonMark: dòng chữ thường kiểu
# "[Lưu ý]: cần đo khe ray…" không phải khai báo link nên được giữ (Soi Lỗi SL-4).
_MD_LINK_DEF = re.compile(
    r"^[ \t>*+\-\d.)]*\[(?:[^\[\]\\]|\\.)+\]:[ \t]*(?:\n[ \t>]*)?(?:<[^<>\n]*>|\S+)[ \t]*"
    r"(?:(?:\n[ \t>]*)?(?:\"[^\"]*\"|'[^']*'|\([^()]*\))[ \t]*)?$",
    re.MULTILINE,
)
# Chỗ AI đánh dấu thiếu số liệu: "[cần bổ sung: …]" không bao giờ là nhãn link, kể cả khi
# ngay sau là "(…)" (Soi Lỗi R3-4). Phải khớp ``MISSING_PATTERN`` trong content/rules.py.
_MISSING_LABEL = re.compile(r"cần bổ sung:", re.IGNORECASE)
# Ký tự có thể đứng trước "[" của một dòng khai báo link "[nhãn]: địa chỉ": thụt lề, dấu trích
# dẫn ">", dấu danh sách "-", "*", "+", "1.", "1)". Lấy rộng (mọi khoảng trắng Unicode, mọi chữ
# số) cho chắc: escape thừa chỉ thêm một "\" không hiện ra.
_DEF_PREFIX_CHARS = frozenset(">*+-.)")
# Số lượt lọc (bỏ thẻ + bỏ link) tối đa. Bỏ một link có thể ghép phần còn lại thành link hoặc
# thẻ mới (SL-2, SL-3), nên lặp tới khi chữ không đổi; quá số lượt thì dùng bước dự phòng.
_MAX_CLEAN_PASSES = 4


def _is_blank_line_start(text: str, newline: int) -> bool:
    """Ký tự ``text[newline]`` là "\n" và dòng ngay sau nó là dòng trống."""
    return _BLANK_LINE_AFTER.match(text, newline + 1) is not None


def _matching_parens(text: str) -> tuple[dict[int, int], list[int], list[int]]:
    """Ghép ngoặc tròn trong từng đoạn văn (bỏ qua ngoặc escape, không vượt dòng trống).

    Trả về (vị trí "(" → ")" khớp, vị trí cuối mỗi đoạn, vị trí ")" cuối cùng của mỗi đoạn
    hoặc -1).
    """
    pairs: dict[int, int] = {}
    para_ends: list[int] = []
    para_last_close: list[int] = []
    stack: list[int] = []
    last_close = -1
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            i += 2
            continue
        if char == "(":
            stack.append(i)
        elif char == ")":
            last_close = i
            if stack:
                pairs[stack.pop()] = i
        elif char == "\n" and _is_blank_line_start(text, i):
            stack.clear()
            para_ends.append(i)
            para_last_close.append(last_close)
            last_close = -1
        i += 1
    para_ends.append(n)
    para_last_close.append(last_close)
    return pairs, para_ends, para_last_close


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
    pairs, para_ends, para_last_close = _matching_parens(text)
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
            if opener is not None and _MISSING_LABEL.match(text, opener + 1):
                i += 1  # "[cần bổ sung: …](…)": giữ cả hai, bước escape làm "(" thành chữ
                continue
            close = pairs.get(i + 1)
            if close is None and i + 1 < n and text[i + 1] == "(":
                # "(" không có ")" khớp, ví dụ tiêu đề link chứa "(" lẻ: [x](url "(") (SL-1).
                # Bắt rộng: bỏ tới ")" cuối cùng của đoạn văn. Không có ")" thì không phải link.
                last = para_last_close[bisect_right(para_ends, i)]
                close = last if last > i else None
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


def escape_link_syntax(text: str) -> str:
    """Làm cho chữ KHÔNG THỂ thành link Markdown, dù link viết theo kiểu nào.

    Mọi link CommonMark/GFM đều cần dấu "]" (không escape) đứng sát ngay trước một trong ba
    ký tự: "(" (link/ảnh nội dòng), "[" (link tham chiếu đầy đủ/rút gọn) hoặc ":" (dòng khai báo
    "[nhãn]: địa chỉ"; link kiểu "[nhãn]" trơn chỉ thành link khi có dòng khai báo). Hàm này
    thêm "\\" trước ký tự đó: Markdown hiện ra y như cũ ("](", "][", "]:") nhưng không còn
    là link. Vì không cần nhận ra link, các dạng lạ (ngoặc lồng, tiêu đề có escape, xuống dòng
    "\\r") cũng không lọt.

    Dấu ":" chỉ escape khi "[" mở nhãn đứng đầu dòng (sau thụt lề, ">", "-", "1."…), vì khai
    báo link chỉ có ở đầu khối; nhờ vậy câu thường kiểu "Giá [cần bổ sung: giá]: …" giữ nguyên.
    Chạy một lượt (tuyến tính), chạy lại không đổi gì (idempotent). Dấu "[" và "]" giữ nguyên
    nên chỗ "[cần bổ sung: …]" vẫn nhận diện được.
    """
    out: list[str] = []
    start = 0  # đầu đoạn chưa chép sang ``out``
    at_line_prefix = True  # từ đầu dòng tới đây chỉ có thụt lề / dấu trích dẫn / dấu danh sách
    label_at_line_start = False  # "[" đang mở gần nhất đứng ở đầu dòng
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            at_line_prefix = False
            i += 2
            continue
        if char == "\n":
            at_line_prefix = True
        elif char == "[":
            label_at_line_start = at_line_prefix
            at_line_prefix = False
        elif char == "]":
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt in ("(", "[") or (nxt == ":" and label_at_line_start):
                out.append(text[start : i + 1])
                out.append("\\")
                start = i + 1
            label_at_line_start = False
            at_line_prefix = False
        elif at_line_prefix and not (
            char.isspace() or char.isdigit() or char in _DEF_PREFIX_CHARS
        ):
            at_line_prefix = False
        i += 1
    if not out:
        return text
    out.append(text[start:])
    return "".join(out)


def unescape_link_syntax(text: str) -> str:
    """Nghịch đảo của ``escape_link_syntax``: bỏ đúng những dấu "\\" mà hàm đó đã thêm.

    Dùng khi đưa chữ vào ô cho người dùng sửa (ô «Sửa trực tiếp», tiêu đề dàn ý), để không
    hiện dấu "\\" lạ. Khi lưu lại PHẢI gọi ``escape_link_syntax`` lần nữa. Quét cùng một
    cách với ``escape_link_syntax``: bỏ "\\" nằm giữa "]" (không escape) và "(" hoặc "[",
    hoặc ":" khi "[" mở nhãn đứng đầu dòng. Bảo đảm
    ``escape_link_syntax(unescape_link_syntax(t)) == t`` với mọi ``t`` đã escape.
    """
    out: list[str] = []
    start = 0
    at_line_prefix = True
    label_at_line_start = False
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            at_line_prefix = False
            i += 2
            continue
        if char == "\n":
            at_line_prefix = True
        elif char == "[":
            label_at_line_start = at_line_prefix
            at_line_prefix = False
        elif char == "]":
            if text.startswith("\\", i + 1) and i + 2 < n:
                nxt = text[i + 2]
                if nxt in ("(", "[") or (nxt == ":" and label_at_line_start):
                    out.append(text[start : i + 1])
                    start = i + 2  # bỏ dấu "\\"; ký tự sau được xét ở vòng tiếp theo
                    i += 2
                    label_at_line_start = False
                    at_line_prefix = False
                    continue
            label_at_line_start = False
            at_line_prefix = False
        elif at_line_prefix and not (
            char.isspace() or char.isdigit() or char in _DEF_PREFIX_CHARS
        ):
            at_line_prefix = False
        i += 1
    if not out:
        return text
    out.append(text[start:])
    return "".join(out)

def clean_ai_text(text: str) -> str:
    """Làm sạch một đoạn Markdown do AI viết: không còn thẻ HTML, không còn link.

    1. Đổi xuống dòng "\\r\\n" và "\\r" thành "\\n" (Markdown coi cả ba là xuống dòng).
    2. Lặp "bỏ thẻ → bỏ link" tới khi chữ không đổi, vì bỏ một phần có thể ghép phần còn lại
       thành thẻ mới (``<[](x)script>``). Bước này chỉ để chữ gọn (bỏ địa chỉ thừa); chữ cố
       tình lồng sâu hơn số lượt cho phép thì tách "<" khỏi chữ cái (không còn là thẻ).
    3. ``escape_link_syntax``: bước quyết định an toàn. Link nào còn sót (bộ đọc ở bước 2
       không nhận ra) cũng bị vô hiệu hóa, không phụ thuộc việc nhận ra link.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for _ in range(_MAX_CLEAN_PASSES):
        previous = text
        text = strip_markdown_links(strip_tags(text))
        if text == previous:
            break
    else:
        text = _TAG_OPEN.sub("< ", text)
    return escape_link_syntax(text.strip())


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
# Thẻ nguy hiểm chỉ "bọc" nội dung bình thường (trình duyệt vẫn hiện chữ bên trong và phía sau
# khi thiếu thẻ đóng): chỉ bỏ thẻ, giữ chữ; thẻ con nguy hiểm (script…) vẫn bị bỏ riêng (SL-5).
DANGEROUS_CONTAINER_TAGS = frozenset({"form", "button", "select", "option", "svg", "math"})
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
            if not closed and tag not in DANGEROUS_VOID_TAGS | DANGEROUS_CONTAINER_TAGS:
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

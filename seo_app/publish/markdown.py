"""Markdown của bài → HTML gửi WordPress (T-096, thiết kế ``docs/team/reports/T-094-tho-may.md``
mục 3.5, 4; điều kiện Lá Chắn LC-T094-4, -10).

Chỉ hiểu phần nhỏ của Markdown mà AI và người dùng viết trong bài:

- khối: đoạn văn, tiêu đề con (``#`` → ``######``, dòng gạch dưới ``===``/``---``), danh sách
  gạch đầu dòng và đánh số (lồng nhau theo thụt lề), bảng GFM (dòng bắt đầu bằng ``|``, dòng
  thứ hai là ``|---|``), trích dẫn ``>``, kẻ ngang, khối mã ```` ``` ````/``~~~``;
- trong dòng: đậm, nghiêng (``**``, ``__``, ``*``, ``_``), đoạn `mã`, dấu ``\\`` trước dấu câu
  ASCII (bỏ dấu ``\\``), mã ký tự ``&…;`` (giải mã rồi escape lại), xuống dòng cứng (hai dấu cách
  hay ``\\`` cuối dòng).

**Không bao giờ** sinh ``<a>``, ``<img>``, ``<iframe>``, HTML thô hay chú thích HTML: link
``[x](url)``, ảnh ``![x](url)``, ``<https://…>``, khai báo link tham chiếu ``[1]: url``, địa chỉ
trần, thẻ ``<…>`` đều ra **chữ thường**. Mọi chữ qua ``html.escape`` rồi ``escape_shortcodes``
(T-061). Link chỉ do ``apply_links`` chèn sau (bài trong danh sách đã đăng).

Chia khối dùng đúng quy tắc của ``markdown_blocks`` (``seo_app/onpage/links.py``: tiêu đề,
dòng gạch dưới, kẻ ngang, mục danh sách, dòng bảng, khối mã) để link nội bộ AI gợi ý ở bước SEO
tìm thấy đúng đoạn. Chỗ hai bên đọc khác nhau thì ``apply_links`` không thấy cụm từ và báo bỏ
qua, không chèn sai chỗ.

Hợp đồng với ``apply_links`` (LC-T039 đk 3b): thân một phần không có ``<h1>``, ``<h2>``; tiêu đề
con trong thân là ``<h3>`` trở xuống. Trong một đoạn không có ký tự xuống dòng (WordPress chạy
``wpautop`` khi hiện bài: xuống dòng đơn thành ``<br>``); các khối cách nhau một dòng.

Đầu vào là chữ thô (bộ dựng đã gỡ ký tự ngắt rộng 0 của T-031): coi là chưa tin cậy. Ký tự điều
khiển, ký tự điều khiển hướng chữ (U+202A–U+202E, U+2066–U+2069) và nửa cặp UTF-16 lẻ bị bỏ.
Chạy gần tuyến tính theo độ dài; độ sâu lồng và số dấu mở xét lại có giới hạn.
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field

from seo_app.onpage.links import (
    MAX_TABLE_COLUMNS,
    _code_spans,
    _fence_open,
    _is_atx_heading,
    _is_list_item,
    _is_rule,
    _is_thematic_break,
    _table_cells,
    _table_width,
)
from seo_app.sanitize import _ENTITY, _ESCAPABLE, _entity_value, escape_shortcodes

MAX_DEPTH = 6  # danh sách, trích dẫn lồng quá mức này thì phần trong là chữ thường
MAX_LOOKBACK = 100  # số dấu mở đậm/nghiêng xét lại cho một dấu đóng
MAX_COLUMNS = MAX_TABLE_COLUMNS  # số cột tối đa của bảng (dùng chung với ``markdown_blocks``)

# Ký tự bỏ khỏi chữ: điều khiển C0/C1 (trừ tab, xuống dòng), điều khiển hướng chữ, nửa cặp lẻ.
_DROPPED = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f‪-‮⁦-⁩\ud800-\udfff]")
_LINES = re.compile(r"\r\n|\r|\n")
_PLAIN = re.compile(r"[^\\\n`&*_]+")
_CLOSING_HASHES = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
_ORDERED = re.compile(r"([0-9]{1,9})[.)]")


def escape_text(value: str) -> str:
    """Chữ trong HTML: bỏ ký tự lạ, escape, vô hiệu shortcode (LC-T094-4)."""
    return escape_shortcodes(html.escape(_DROPPED.sub("", value), quote=False))


def _is_punctuation(ch: str) -> bool:
    return ch in _ESCAPABLE or unicodedata.category(ch)[:1] in ("P", "S")


# ------------------------------------------------------------------ trong dòng


@dataclass(eq=False)
class _Delimiter:
    """Một dãy ``*`` hay ``_`` liền nhau (CommonMark: delimiter run)."""

    char: str
    length: int  # độ dài ban đầu
    count: int  # số dấu còn lại chưa ghép (in ra thành chữ)
    can_open: bool
    can_close: bool
    opens: list[str] = field(default_factory=list)  # thẻ mở, theo thứ tự ghép (trong ra ngoài)
    closes: list[str] = field(default_factory=list)  # thẻ đóng, theo thứ tự ghép

    def render(self) -> str:
        return (
            "".join(f"</{tag}>" for tag in self.closes)
            + escape_text(self.char * self.count)
            + "".join(f"<{tag}>" for tag in reversed(self.opens))
        )


def _flanking(prev: str, nxt: str) -> tuple[bool, bool]:
    left = not nxt.isspace() and (
        not _is_punctuation(nxt) or prev.isspace() or _is_punctuation(prev)
    )
    right = not prev.isspace() and (
        not _is_punctuation(prev) or nxt.isspace() or _is_punctuation(nxt)
    )
    return left, right


def _rule_of_three(opener: _Delimiter, closer: _Delimiter) -> bool:
    """CommonMark: dấu vừa mở vừa đóng được thì tổng độ dài không chia hết cho 3 (trừ khi cả hai
    chia hết). Đúng: không được ghép."""
    return (
        (opener.can_close or closer.can_open)
        and (opener.length + closer.length) % 3 == 0
        and not (opener.length % 3 == 0 and closer.length % 3 == 0)
    )


def _match_emphasis(tokens: list[str | _Delimiter]) -> None:
    """Ghép dấu mở và dấu đóng thành ``<strong>``/``<em>`` (lối của CommonMark, rút gọn).

    Dấu đóng ghép với dấu mở gần nhất cùng loại; các dấu mở nằm giữa bị bỏ (thành chữ), nên thẻ
    luôn lồng đúng. Mỗi dấu đóng chỉ xét lại tối đa ``MAX_LOOKBACK`` dấu mở."""
    stack: list[_Delimiter] = []
    for token in tokens:
        if not isinstance(token, _Delimiter):
            continue
        if token.can_close:
            while token.count:
                found = None
                for k in range(len(stack) - 1, max(-1, len(stack) - 1 - MAX_LOOKBACK), -1):
                    opener = stack[k]
                    if opener.char == token.char and not _rule_of_three(opener, token):
                        found = k
                        break
                if found is None:
                    break
                opener = stack[found]
                use = 2 if opener.count >= 2 and token.count >= 2 else 1
                tag = "strong" if use == 2 else "em"
                opener.count -= use
                token.count -= use
                opener.opens.append(tag)
                token.closes.append(tag)
                del stack[found + 1 :]
                if not opener.count:
                    stack.pop()
        if token.can_open and token.count:
            stack.append(token)


def inline_html(text: str) -> str:
    """Chữ trong một khối (các dòng nối bằng ``\\n``) → HTML trong dòng. Không có thẻ nào ngoài
    ``<strong>``, ``<em>``, ``<code>``, ``<br>``. Đoạn `mã` tìm bằng ``_code_spans``, cùng hàm
    với ``markdown_blocks`` (bước SEO che đúng các đoạn mã này)."""
    text = text.strip()
    tokens: list[str | _Delimiter] = []
    buffer: list[str] = []
    code_spans = _code_spans(text)

    def flush() -> None:
        if buffer:
            tokens.append(escape_text("".join(buffer)))
            buffer.clear()

    i, n = 0, len(text)
    while i < n:
        plain = _PLAIN.match(text, i)
        if plain is not None:
            buffer.append(plain.group())
            i = plain.end()
            continue
        char = text[i]
        if char == "\\":
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt == "\n":  # "\" cuối dòng: xuống dòng cứng
                flush()
                tokens.append("<br>")
                i += 2
                while i < n and text[i] in " \t":
                    i += 1
            elif nxt and nxt in _ESCAPABLE:
                buffer.append(nxt)
                i += 2
            else:
                buffer.append("\\")
                i += 1
        elif char == "\n":
            pending = "".join(buffer)
            buffer.clear()
            kept = pending.rstrip(" \t")
            hard = len(pending) - len(pending.rstrip(" ")) >= 2
            buffer.append(kept)
            flush()
            tokens.append("<br>" if hard else " ")
            i += 1
            while i < n and text[i] in " \t":
                i += 1
        elif char == "`":
            if i not in code_spans:  # không có dãy đóng cùng độ dài: chữ thường
                end = i
                while end < n and text[end] == "`":
                    end += 1
                buffer.append(text[i:end])
                i = end
                continue
            end, size = code_spans[i]
            code = text[i + size : end - size].replace("\n", " ")
            if len(code) >= 2 and code[0] == " " and code[-1] == " " and code.strip(" "):
                code = code[1:-1]
            flush()
            tokens.append(f"<code>{escape_text(code)}</code>")
            i = end
        elif char == "&":
            match = _ENTITY.match(text, i)
            value = _entity_value(match) if match is not None else None
            if value is None:
                buffer.append("&")
                i += 1
            else:
                buffer.append(value)
                i = match.end()
        else:  # "*" hoặc "_"
            end = i
            while end < n and text[end] == char:
                end += 1
            prev = text[i - 1] if i > 0 else " "
            nxt = text[end] if end < n else " "
            left, right = _flanking(prev, nxt)
            if char == "*":
                can_open, can_close = left, right
            else:  # "_" giữa chữ (ten_bien) không phải nghiêng
                can_open = left and (not right or _is_punctuation(prev))
                can_close = right and (not left or _is_punctuation(nxt))
            flush()
            tokens.append(_Delimiter(char, end - i, end - i, can_open, can_close))
            i = end
    flush()
    _match_emphasis(tokens)
    return "".join(t if isinstance(t, str) else t.render() for t in tokens)


# ------------------------------------------------------------------ khối


def _indent(line: str) -> int:
    """Số cột thụt lề (tab tính 4 cột)."""
    width = 0
    for char in line:
        if char == " ":
            width += 1
        elif char == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def _dedent(line: str, columns: int) -> str:
    """Bỏ tối đa ``columns`` cột thụt lề ở đầu dòng."""
    width = 0
    i = 0
    while i < len(line) and width < columns and line[i] in " \t":
        width += 1 if line[i] == " " else 4 - width % 4
        i += 1
    return line[i:]


def _heading_tag(level: int) -> str:
    """``#``, ``##``, ``###`` trong thân một phần đều là ``<h3>`` (``<h2>`` là tiêu đề phần)."""
    return f"h{max(3, level)}"


def _table(rows: list[str]) -> list[str]:
    """Các dòng bắt đầu bằng "|": bảng nếu dòng 2 là dòng kẻ cùng số cột (``_table_width``, cùng
    hàm với ``markdown_blocks``), không thì mỗi dòng một đoạn (mỗi dòng bảng là một khối)."""
    width = _table_width(rows)
    if width is None:
        return [f"<p>{inline_html(row)}</p>" for row in rows]
    header = _table_cells(rows[0])
    lines = [
        "<table>",
        "<thead>",
        "<tr>" + "".join(f"<th>{inline_html(cell)}</th>" for cell in header) + "</tr>",
        "</thead>",
    ]
    if len(rows) > 2:
        lines.append("<tbody>")
        for row in rows[2:]:
            cells = (_table_cells(row) + [""] * width)[:width]
            lines.append("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in cells) + "</tr>")
        lines.append("</tbody>")
    lines.append("</table>")
    return ["\n".join(lines)]


@dataclass(frozen=True)
class _Marker:
    ordered: bool
    kind: str  # "-", "*", "+" hoặc "." / ")" của danh sách đánh số
    number: int
    indent: int  # cột của dấu
    content: int  # cột bắt đầu chữ của mục
    text: str  # chữ sau dấu


def _marker(line: str) -> _Marker | None:
    """Dấu mục danh sách của dòng, đọc trên đúng chữ ``_is_list_item`` xét (``line.strip()``:
    khoảng trắng Unicode đầu dòng như dấu cách toàn khổ cũng bỏ). Không phải mục: None."""
    body = line.strip()
    if not body or not _is_list_item(body):
        return None
    indent = _indent(line)
    if body[0] in "-*+":
        width, kind, number, ordered = 1, body[0], 0, False
    else:
        match = _ORDERED.match(body)
        if match is None:
            return None
        width, kind, number, ordered = match.end(), body[match.end() - 1], int(match.group(1)), True
    rest = body[width:]
    gap = len(rest) - len(rest.lstrip(" \t"))
    return _Marker(
        ordered, kind, number, indent, indent + width + max(1, min(gap, 4)), rest.strip()
    )


def _spaces(line: str) -> int:
    """Số dấu cách đầu dòng, đúng cách ``markdown_blocks`` đo khi nhận tiêu đề ``#``."""
    return len(line) - len(line.lstrip(" "))


def _is_special(line: str) -> bool:
    """Dòng mở một khối mới (không nối tiếp được đoạn văn của mục danh sách, của trích dẫn)."""
    stripped = line.strip()
    return bool(
        _fence_open(stripped)
        or stripped.startswith(("|", ">"))
        or _is_atx_heading(stripped, _spaces(line))
        or _is_thematic_break(stripped)
    )


def _list(lines: list[str], start: int, depth: int) -> tuple[str, int]:
    """Một danh sách bắt đầu ở dòng ``start``. Trả (HTML, dòng kế tiếp sau danh sách)."""
    first = _marker(lines[start])
    if first is None:  # người gọi đã kiểm (``_blocks``); phòng hờ: dòng thành đoạn văn
        return f"<p>{inline_html(lines[start])}</p>", start + 1
    items: list[tuple[list[str], bool]] = []  # (các dòng của mục, có dòng trống bên trong)
    i = start
    while i < len(lines):
        marker = _marker(lines[i])
        if (
            marker is None
            or marker.ordered != first.ordered
            or marker.kind != first.kind
            or marker.indent > first.indent + 3
            or marker.indent < first.indent
        ):
            break
        content = [marker.text]
        loose = False
        i += 1
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                # Dòng trống: mục còn tiếp nếu dòng có chữ sau đó thụt vào trong mục.
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and _indent(lines[j]) >= marker.content:
                    content.extend([""] * (j - i))
                    loose = True
                    i = j
                    continue
                break
            if _indent(line) >= marker.content:
                content.append(_dedent(line, marker.content))
            elif _marker(line) is None and not _is_special(line) and content[-1].strip():
                content.append(line.strip())  # dòng nối tiếp (lazy) của đoạn văn trong mục
            else:
                break
            i += 1
        items.append((content, loose))
        # Dòng trống giữa hai mục cùng danh sách.
        j = i
        while j < len(lines) and not lines[j].strip():
            j += 1
        next_marker = _marker(lines[j]) if j < len(lines) else None
        if j > i and (
            next_marker is None
            or next_marker.ordered != first.ordered
            or next_marker.kind != first.kind
            or not first.indent <= next_marker.indent <= first.indent + 3
        ):
            break
        i = j
    tag = "ol" if first.ordered else "ul"
    attrs = f' start="{first.number}"' if first.ordered and first.number != 1 else ""
    rendered = [f"<{tag}{attrs}>"]
    for content, loose in items:
        if depth + 1 >= MAX_DEPTH:
            inner = inline_html("\n".join(line.strip() for line in content if line.strip()))
        else:
            blocks = _blocks(content, depth + 1)
            inner = "".join(
                body if kind == "p" and not loose else html_text for kind, html_text, body in blocks
            )
        rendered.append(f"<li>{inner}</li>")
    rendered.append(f"</{tag}>")
    return "\n".join(rendered), i


def _blocks(lines: list[str], depth: int) -> list[tuple[str, str, str]]:
    """Các khối: (loại, HTML, HTML bên trong ``<p>`` nếu là đoạn văn)."""
    out: list[tuple[str, str, str]] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            body = inline_html("\n".join(paragraph))
            paragraph.clear()
            if body:
                out.append(("p", f"<p>{body}</p>", body))

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = _indent(line)
        if fence := _fence_open(stripped):  # «```chữ```» không mở khối mã (SL-T096-7)
            flush()
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                code.append(lines[i])
                i += 1
            i += 1  # dòng đóng khối (nếu có)
            out.append(("pre", f"<pre><code>{escape_text(chr(10).join(code))}</code></pre>", ""))
            continue
        if not stripped:
            flush()
        elif _is_atx_heading(stripped, _spaces(line)):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            content = _CLOSING_HASHES.sub("", stripped[level:].strip())
            tag = _heading_tag(level)
            body = inline_html(content)
            if body:
                out.append(("h", f"<{tag}>{body}</{tag}>", ""))
        elif paragraph and _is_rule(stripped, "=-"):
            body = inline_html("\n".join(paragraph))  # dòng gạch dưới: đoạn phía trên là tiêu đề
            paragraph.clear()
            if body:
                out.append(("h", f"<h3>{body}</h3>", ""))
        elif _is_thematic_break(stripped):
            flush()
            out.append(("hr", "<hr>", ""))
        elif stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            out.extend(
                ("p" if block.startswith("<p>") else "table", block, block[3:-4])
                for block in _table(rows)
            )
            continue
        elif _marker(line) is not None:
            flush()
            block, i = _list(lines, i, depth)
            out.append(("list", block, ""))
            continue
        elif stripped.startswith(">") and indent <= 3:
            flush()
            quoted = []
            while i < len(lines):
                current = lines[i]
                if current.strip().startswith(">") and _indent(current) <= 3:
                    inner = current.lstrip(" \t")[1:]
                    quoted.append(inner[1:] if inner.startswith(" ") else inner)
                elif (
                    current.strip()
                    and quoted[-1].strip()
                    and _marker(current) is None
                    and not _is_special(current)
                ):
                    # Dòng nối tiếp (lazy) của đoạn văn trong trích dẫn, như CommonMark và như
                    # ``markdown_blocks`` (cùng một khối): «> Kéo cửa…⏎để nghe…» (SL-T096-2).
                    quoted.append(current.strip())
                else:
                    break
                i += 1
            if depth + 1 >= MAX_DEPTH:
                body = inline_html("\n".join(q.strip() for q in quoted if q.strip()))
                inner_html = f"<p>{body}</p>" if body else ""
            else:
                inner_html = "\n".join(block for _kind, block, _body in _blocks(quoted, depth + 1))
            out.append(("quote", f"<blockquote>\n{inner_html}\n</blockquote>", ""))
            continue
        else:
            paragraph.append(line.lstrip(" \t"))
        i += 1
    flush()
    return out


def markdown_to_html(markdown: str) -> str:
    """Thân một phần của bài (Markdown, chữ thô) → HTML, các khối cách nhau ``\\n``.

    Chưa qua ``sanitize_html``: bộ dựng bài (``seo_app.publish.render``) lọc tiếp. Không phải
    chữ thì báo ``TypeError``."""
    if not isinstance(markdown, str):
        raise TypeError("markdown phải là chữ")
    lines = _LINES.split(_DROPPED.sub("", markdown))
    return "\n".join(block for _kind, block, _body in _blocks(lines, 0))


__all__ = [
    "MAX_COLUMNS",
    "MAX_DEPTH",
    "MAX_LOOKBACK",
    "escape_text",
    "inline_html",
    "markdown_to_html",
]

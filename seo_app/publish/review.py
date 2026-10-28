"""Dữ liệu cho màn hình xác nhận trước khi gửi bài (T-096; thiết kế T-094 mục 3.5; Lá Chắn
LC-T094-6, -7).

Mọi hàm ở đây **chỉ đọc** HTML cuối do bộ dựng (``seo_app.publish.render``) tạo, không sửa gì.

- ``link_rows``: mọi ``href`` của HTML cuối, kèm kết quả ``check_links`` và cờ tên máy (dạng
  ASCII ``xn--…``, chữ ngoài ASCII, «@», «\\», «//» đầu, cổng lạ, khác website).
- ``bare_addresses``: địa chỉ web, ``www.``, email còn dạng chữ trong bài (sau khi gỡ ký tự ngắt
  rộng 0 của T-031 chúng liền mạch lại; không bấm được, nhưng người dùng phải thấy).
- ``embedded_urls``: địa chỉ WordPress sẽ **nhúng** (oEmbed) khi hiện bài: áp đúng hai biểu thức
  của ``WP_Embed::autoembed`` (dòng chỉ có địa chỉ, sau khi đổi ``\\n`` nằm trong thẻ như
  ``wp_replace_in_html_tags``; ``<p>`` chỉ có địa chỉ), cộng một lớp chặt hơn: khối (``<li>``,
  ``<td>``…) mà cả chữ chỉ là một địa chỉ.
- ``block_texts``: chữ (đã giải mã) của từng khối HTML, để tìm đoạn dạng shortcode.

Chữ trả về là **chữ thô** từ bài (chữ AI, chữ người dùng gõ, tiêu đề bài trên site): giao diện
phải hiện bằng ô bảng, ``st.text`` hay ``escape_markdown``, không bao giờ ``st.markdown`` thô hay
``unsafe_allow_html``; link không bấm được (bất biến của board: chữ sau ``unbreak_autolinks``
không vào ``st.markdown``).
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlsplit

from seo_app.onpage.links import LinkCheck, LinkKind, LinkReport, _browser_host, _hosts
from seo_app.onpage.meta import Level

MAX_LISTED = 200  # số địa chỉ trần, chỗ nhúng liệt kê tối đa (bài bình thường chỉ vài cái)

# Cờ tên máy (LC-T094-7, LC-T039-1). Chữ cố định, hiện cạnh địa chỉ trên màn hình xác nhận.
FLAG_NON_ASCII = "Tên máy có chữ ngoài ASCII: dễ nhầm với tên website, xem dạng xn--"
FLAG_PUNYCODE = "Tên máy viết dạng mã xn-- (chữ ngoài ASCII)"
FLAG_AT = "Có «@» trong phần tên máy (dạng giả địa chỉ)"
FLAG_BACKSLASH = "Có dấu «\\» (trình duyệt hiểu như «/»)"
FLAG_PROTOCOL_RELATIVE = "Bắt đầu bằng «//» (link ra ngoài trông như link nội bộ)"
FLAG_PORT = "Cổng lạ (không phải 80, 443)"
FLAG_OTHER_SITE = "Khác website"
FLAG_MALFORMED = "Địa chỉ sai dạng"

# Hai đầu link: trình duyệt bỏ dấu cách và ký tự điều khiển C0 (như ``links._URL_TRIM``).
_URL_TRIM = "".join(map(chr, range(0x21)))
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
# ``\s`` của PCRE (PHP, không cờ /u): chỉ khoảng trắng ASCII. ``\s`` của Python còn khớp dấu
# cách không ngắt…, nên viết rõ.
_SPACE = r"[ \t\n\r\f\v]"
_PCRE_SPACE = " \t\n\r\f\v"
_NOT_SPACE_URL = r"[^ \t\n\r\f\v<>\"]"
# ``WP_Embed::autoembed`` (``wp-includes/class-wp-embed.php``), WordPress 6.9:
#   '|^(\s*)(https?://[^\s<>"]+)(\s*)$|im'   và   '|(<p(?: [^>]*)?>\s*)(https?://[^\s<>"]+)(\s*<\/p>)|i'
# Biểu thức thứ nhất (dòng chỉ có một địa chỉ) xét từng dòng bằng ``_URL_ALONE`` cho cùng kết quả mà
# không quay lui qua các dòng trống (SL-T096-1). Biểu thức thứ hai dùng lượng từ chiếm hữu ``*+``.
_URL_ALONE = re.compile(rf"https?://{_NOT_SPACE_URL}++", re.IGNORECASE)
_EMBED_PARAGRAPH = re.compile(
    rf"(<p(?: [^>]*+)?>{_SPACE}*+)(https?://{_NOT_SPACE_URL}++)({_SPACE}*+</p>)", re.IGNORECASE
)
_IN_TAG = re.compile(r"<[^>]*>")  # thẻ, chú thích (gần đúng ``wp_html_split``)
_LINE_BREAK_MARK = "<!-- wp-line-break -->"
_ONLY_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_HTTPS = "https://"
# ``getFilename`` có đuôi tệp (ảnh, video…) thì khối Embed bỏ qua; ``htm``, ``html``, ``php`` vẫn
# là trang. Đúng biểu thức Gutenberg (phân biệt hoa thường: «.MP4» không khớp nên vẫn Chặn).
_FILE_EXTENSION = re.compile(r"\.(?!(html?|php)$)[a-z0-9]++$")
# ``String.prototype.trim`` của JavaScript (khoảng trắng và xuống dòng theo ECMAScript): trình soạn
# khối (Gutenberg, khối Embed, «Chuyển thành khối») bỏ các ký tự này ở hai đầu đoạn rồi xét đoạn
# có phải đúng một địa chỉ không. Gồm cả dấu cách không ngắt, BOM, khoảng trắng Unicode;
# không gồm ký tự rộng 0 (U+200B) (LC-T096-4).
_JS_TRIM = "".join(
    map(
        chr,
        [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680, *range(0x2000, 0x200B), 0x2028,
         0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF],
    )
)  # fmt: skip

# Địa chỉ trần trong chữ (đã giải mã). Dừng ở khoảng trắng, "<", ">", dấu nháy kép. Phần tên
# email chỉ bắt đầu ở đầu một dãy (nhìn lùi) và mọi lượng từ chiếm hữu: tuyến tính (SL-T096-1).
_BARE_URL = re.compile(r"https?://[^\s<>\"]++", re.IGNORECASE)
_BARE_WWW = re.compile(r"(?<![\w./@-])www\.[^\s<>\"]++", re.IGNORECASE)
_BARE_EMAIL = re.compile(r"(?<![\w.%+-])[\w.%+-]++@[\w-]++(?:\.[\w-]++)+")
_TRAILING = ".,;:!?)]}»”’'\"…"

# Khối chữ: mỗi khối một đoạn khi tìm shortcode, chỗ nhúng (như ``links._PARAGRAPH_TAGS``).
_TEXT_BLOCKS = frozenset(
    {"p", "li", "dd", "dt", "td", "th", "blockquote", "pre", "figcaption", "caption",
     "h2", "h3", "h4", "h5", "h6"}
)  # fmt: skip


@dataclass(frozen=True)
class LinkRow:
    """Một ``href`` của HTML cuối. ``href``, ``text``: chữ thô (phải escape khi hiện).
    ``ascii_host``: tên máy như trình duyệt đọc (punycode), rỗng với link tương đối."""

    href: str
    text: str
    kind: LinkKind
    level: Level
    message: str
    post_id: int | None
    host: str
    ascii_host: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class BareAddress:
    """Địa chỉ web, ``www.`` hay email còn dạng chữ trong bài. ``kind``: "url", "www", "email"."""

    text: str
    kind: str
    ascii_host: str
    flags: tuple[str, ...]


def address_flags(
    address: str, site: str, *, bare: bool = False
) -> tuple[str, str, tuple[str, ...]]:
    """(tên máy, tên máy dạng ASCII, cờ) của một địa chỉ. Không gọi mạng, không giải tên.

    ``bare``: địa chỉ không có giao thức (``www.…``, phần sau «@» của email) thì phần đầu là tên
    máy. Không ``bare`` thì như trình duyệt đọc ``href``: không giao thức là link tương đối.
    Giao thức khác http(s) (``mailto:``, ``tel:``) thì không có tên máy."""
    value = address.strip(_URL_TRIM)
    flags: list[str] = []
    if "\\" in value:
        flags.append(FLAG_BACKSLASH)
    if value.startswith("//"):
        flags.append(FLAG_PROTOCOL_RELATIVE)
    scheme = _SCHEME.match(value)
    if scheme is not None and scheme.group().lower() not in ("http:", "https:"):
        return "", "", tuple(flags)
    if bare and scheme is None and not value.startswith("//"):
        value = f"//{value}"
    try:
        parts = urlsplit(value)
        host = (parts.hostname or "").rstrip(".")
        port = parts.port
    except ValueError:
        return "", "", (*flags, FLAG_MALFORMED)
    if "@" in parts.netloc:
        flags.append(FLAG_AT)
    if port is not None and port not in (80, 443):
        flags.append(FLAG_PORT)
    if not host:
        return "", "", tuple(flags)
    ascii_host = _browser_host(host)
    if not host.isascii() or "%" in host:
        flags.append(FLAG_NON_ASCII)
    elif any(label.startswith("xn--") for label in host.split(".")):
        flags.append(FLAG_PUNYCODE)
    site_hosts = _hosts(site)
    if ascii_host not in site_hosts:
        flags.append(FLAG_OTHER_SITE)
    return host, ascii_host, tuple(flags)


class _Anchors(HTMLParser):
    """``href`` (thuộc tính đầu tiên, như trình duyệt) và chữ của từng ``<a href>``, theo đúng
    thứ tự ``check_links`` đọc."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[list[str]] = []
        self.depth = 0  # đang ở trong mấy thẻ <a> có href

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = next((value or "" for name, value in attrs if name == "href"), None)
        if href is not None:
            self.links.append([href, ""])
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        if tag == "a" and any(name == "href" for name, _ in attrs):
            href = next(value or "" for name, value in attrs if name == "href")
            self.links.append([href, ""])

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and self.links:
            self.links[-1][1] += data


def link_rows(html_text: str, report: LinkReport, site: str) -> tuple[LinkRow, ...]:
    """Mọi ``href`` của ``html_text`` (HTML cuối), ghép với ``report = check_links(html_text…)``
    theo thứ tự. Đếm lệch (không nên có) thì vẫn liệt kê đủ link của ``report``, chữ để trống."""
    reader = _Anchors()
    reader.feed(html_text)
    reader.close()
    texts = (
        [" ".join(text.split()) for _href, text in reader.links]
        if [href for href, _text in reader.links] == [c.href for c in report.links]
        else [""] * len(report.links)
    )
    rows = []
    for check, text in zip(report.links, texts, strict=True):
        rows.append(_row(check, text, site))
    return tuple(rows)


def _row(check: LinkCheck, text: str, site: str) -> LinkRow:
    host, ascii_host, flags = address_flags(check.href, site)
    return LinkRow(
        href=check.href,
        text=text,
        kind=check.kind,
        level=check.level,
        message=check.message,
        post_id=check.post_id,
        host=host,
        ascii_host=ascii_host,
        flags=flags,
    )


class _BlockTexts(HTMLParser):
    """Chữ (đã giải mã) của từng khối trong ``_TEXT_BLOCKS``, khối trong cùng nhận chữ."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.stack: list[list[str]] = []
        self.loose: list[str] = []  # chữ không nằm trong khối nào

    def handle_starttag(self, tag, attrs):
        if tag in _TEXT_BLOCKS:
            self.stack.append([])

    def handle_endtag(self, tag):
        if tag in _TEXT_BLOCKS and self.stack:
            self.blocks.append("".join(self.stack.pop()))

    def handle_data(self, data):
        (self.stack[-1] if self.stack else self.loose).append(data)

    def result(self) -> list[str]:
        self.close()
        while self.stack:
            self.blocks.append("".join(self.stack.pop()))
        loose = "".join(self.loose).strip()
        return [*self.blocks, loose] if loose else self.blocks


def block_texts(html_text: str) -> list[str]:
    """Chữ người đọc thấy của từng khối (đoạn, mục danh sách, ô bảng, tiêu đề…), đã giải mã
    ``&#91;`` thành "[", theo thứ tự đóng khối."""
    reader = _BlockTexts()
    reader.feed(html_text)
    return reader.result()


def _trim(address: str) -> str:
    return address.rstrip(_TRAILING)


def bare_addresses(
    html_text: str, site: str, *, texts: Iterable[str] = ()
) -> tuple[BareAddress, ...]:
    """Địa chỉ web, ``www.``, email còn dạng chữ (không phải ``href``) trong ``html_text`` rồi
    trong ``texts`` (chữ thường ngoài thân bài: tiêu đề, đoạn trích, alt, chú thích ảnh;
    SL-T096-4), theo thứ tự, không lặp, tối đa ``MAX_LISTED``."""
    found: list[BareAddress] = []
    seen: set[str] = set()

    def add(text: str, kind: str) -> None:
        if not text or text in seen or len(found) >= MAX_LISTED:
            return
        seen.add(text)
        target = text.rsplit("@", 1)[-1] if kind == "email" else text
        _host, ascii_host, flags = address_flags(target, site, bare=kind != "url")
        found.append(BareAddress(text, kind, ascii_host, flags))

    for text in [*block_texts(html_text), *texts]:
        covered = text
        for match in _BARE_URL.finditer(text):
            add(_trim(match.group()), "url")
        covered = _BARE_URL.sub(" ", covered)
        for match in _BARE_WWW.finditer(covered):
            add(_trim(match.group()), "www")
        covered = _BARE_WWW.sub(" ", covered)
        for match in _BARE_EMAIL.finditer(covered):
            add(_trim(match.group()), "email")
    return tuple(found)


def embedded_urls(html_text: str) -> tuple[str, ...]:
    """Địa chỉ WordPress sẽ nhúng (oEmbed) khi hiện bài (LC-T094-6). Rỗng: không có chỗ nào.

    Hai biểu thức của ``WP_Embed::autoembed`` áp trên ``html_text`` sau khi đổi ``\\n`` nằm trong
    thẻ thành dấu giữ chỗ (như ``wp_replace_in_html_tags``), cộng một lớp chặt hơn cho trình soạn
    khối («Chuyển thành khối»): khối có chữ chỉ là một địa chỉ (``<li>https://…</li>``…), hay
    bắt đầu bằng đúng một địa chỉ ``https://`` rồi tới chữ (``_block_editor_embeds``), sau khi bỏ
    khoảng trắng hai đầu như ``trim()`` của JavaScript (cả ``&nbsp;``, BOM: LC-T096-4, -5)."""
    content = _IN_TAG.sub(lambda m: m.group().replace("\n", _LINE_BREAK_MARK), html_text)
    urls: list[str] = []  # chữ thô (đã giải mã ``&amp;``): một địa chỉ chỉ một mục (SL-T096-3)
    for line in content.split("\n"):  # '|^(\s*)(https?://…)(\s*)$|im', từng dòng
        stripped = line.strip(_PCRE_SPACE)
        if _URL_ALONE.fullmatch(stripped):
            urls.append(html.unescape(stripped))
    urls.extend(html.unescape(m.group(2)) for m in _EMBED_PARAGRAPH.finditer(content))
    for text in block_texts(html_text):
        stripped = text.strip(_JS_TRIM)  # như ``textContent.trim()`` của trình soạn khối
        if _ONLY_URL.fullmatch(stripped) or _block_editor_embeds(stripped):
            urls.append(stripped)
    return tuple(dict.fromkeys(urls))[:MAX_LISTED]


def _block_editor_embeds(text: str) -> bool:
    """Trình soạn khối coi cả đoạn ``text`` (đã bỏ khoảng trắng hai đầu như ``trim()``) là một
    địa chỉ và nhúng khi «Chuyển thành khối» (LC-T096-5). Theo điều kiện ``isMatch`` của khối
    Embed, biến đổi ``raw`` (Gutenberg ``packages/block-library/src/embed/transforms.js``):
    ``isURL`` là ``new URL(chữ)``, nhận cả dấu cách trong đường dẫn, nên «https://… vài chữ» cũng
    là một địa chỉ. Đủ cả bốn điều kiện thì nhúng:

    - bắt đầu bằng ``https://`` (không phân biệt hoa thường);
    - có đúng một ``https://``;
    - tên máy (trước «/», «?», «#» đầu tiên) không rỗng, không có khoảng trắng;
    - tên file cuối đường dẫn (dấu cách tính như ``%20``) không phải đuôi tệp, trừ ``htm``,
      ``html``, ``php`` (``getFilename``).
    """
    lowered = text.lower()
    if not lowered.startswith(_HTTPS) or lowered.count(_HTTPS) != 1:
        return False
    rest = text[len(_HTTPS) :]
    cut = min((i for i in (rest.find(c) for c in "/?#") if i >= 0), default=len(rest))
    host = rest[:cut]
    if not host or any(char.isspace() for char in host):
        return False
    path = rest[cut:] if rest[cut : cut + 1] == "/" else ""
    path = path.split("?", 1)[0].split("#", 1)[0]
    filename = path.rsplit("/", 1)[-1].replace(" ", "%20")
    return _FILE_EXTENSION.search(filename) is None


__all__ = [
    "FLAG_AT",
    "FLAG_BACKSLASH",
    "FLAG_MALFORMED",
    "FLAG_NON_ASCII",
    "FLAG_OTHER_SITE",
    "FLAG_PORT",
    "FLAG_PROTOCOL_RELATIVE",
    "FLAG_PUNYCODE",
    "MAX_LISTED",
    "BareAddress",
    "LinkRow",
    "address_flags",
    "bare_addresses",
    "block_texts",
    "embedded_urls",
    "link_rows",
]

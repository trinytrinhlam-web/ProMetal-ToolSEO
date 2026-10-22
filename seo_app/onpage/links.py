"""Liên kết nội bộ: chọn bài đích, kiểm gợi ý anchor của AI, chèn link, kiểm link trong bài.

Thiết kế: ``docs/team/reports/T-033-tho-may.md`` mục 4.2 → 4.5 (YC-601 → YC-604).

Nguyên tắc: **AI không bao giờ viết link.**

1. ``select_candidates``: code chọn bài đích từ danh sách bài **đã đăng** (``SiteIndex``): link
   bắt buộc theo phiếu giao bài luôn có mặt, thêm 2–3 bài cùng nhóm (trùng từ không dấu giữa
   tiêu đề).
2. AI chỉ nhận ID + tiêu đề (không địa chỉ) trong khung dữ liệu
   (``prompts.internal_links_prompt``) và trả ``LinkSuggestions``:
   ``[{post_id, section, anchor}]``.
3. ``check_suggestions``: code kiểm từng gợi ý, sai thì **bỏ**, không sửa giùm. Gợi ý đạt được
   lưu riêng thành ``InternalLink`` (không nhét vào chữ Markdown).
4. ``apply_links`` (khi dựng HTML, Giai đoạn 5): duyệt **nút chữ** bằng ``html.parser``, bọc lần
   xuất hiện đầu tiên của anchor ở đúng phần bằng ``<a href>``; địa chỉ lấy từ ``SiteIndex``,
   không bao giờ từ AI, escape bằng ``html.escape(quote=True)``. Sau đó HTML vẫn phải qua
   ``sanitize_html`` như mọi HTML gửi lên WordPress (security.md 2.3).
5. ``check_links``: kiểm mọi link trên HTML cuối: link nháp/hỏng thì Chặn, link ra ngoài chỉ
   liệt kê (không tự gọi tới).

Chữ lấy từ site (tiêu đề, link) và chữ AI là dữ liệu chưa tin cậy. Câu báo ở đây là chữ thuần
(có thể chứa tiêu đề bài trên site, không bao giờ chứa chữ AI): giao diện phải hiện bằng widget
chữ thường hoặc ``html.escape`` (U1). Mọi hàm chạy tuyến tính theo độ dài bài; số gợi ý, số link
được xét có giới hạn.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from encodings.idna import ToASCII, nameprep
from enum import StrEnum
from html.parser import HTMLParser
from itertools import islice
from urllib.parse import parse_qsl, unquote, urlsplit

from pydantic import BaseModel, Field

from seo_app.content.models import Section
from seo_app.content.rules import IGNORABLE_NOT_CF
from seo_app.onpage.meta import SLUG_TRAILING_STOPWORDS, Level, has_link, worst
from seo_app.sanitize import DANGEROUS_TAGS, is_safe_url
from seo_app.storage.site_index import SiteIndex
from seo_app.text import remove_accents
from seo_app.wordpress.client import PublishedItem, is_site_link

MAX_LINKS = 5  # tổng số link nội bộ tối đa trong một bài
MAX_RELATED = 3  # bài cùng nhóm tối đa (YC-602: 2–3 bài)
MIN_SHARED_WORDS = 2  # số từ chung (không dấu) tối thiểu giữa hai tiêu đề để coi là cùng nhóm
MIN_ANCHOR_WORDS = 2
MAX_ANCHOR_WORDS = 8
MAX_ANCHOR_CHARS = 100
# Số gợi ý AI / link / link bắt buộc được xét tối đa: AI bị dụ trả hàng nghìn gợi ý thì phần
# thừa bị bỏ, không làm chậm app (mỗi gợi ý phải tìm trong cả phần bài).
MAX_CONSIDERED = 30


class ArticleKind(StrEnum):
    """Loại bài theo phiếu giao bài (YC-602)."""

    GUIDE = "huong_dan"  # → trang dịch vụ đích + 2–3 bài cùng nhóm
    SERVICE = "dich_vu"  # → 2–3 bài hướng dẫn liên quan
    AREA = "khu_vuc"  # → trang dịch vụ chính + trang tổng "Khu vực phục vụ" (ghi trong phiếu)


class LinkKind(StrEnum):
    INTERNAL = "noi_bo"
    EXTERNAL = "ra_ngoai"
    ANCHOR = "neo"  # "#muc" trong chính bài
    OTHER = "khac"  # mailto:, tel:, giao thức lạ


@dataclass(frozen=True)
class Notice:
    """Một điều cần báo người dùng, kèm mức (Nên / Cảnh báo / Chặn)."""

    level: Level
    message: str


# ------------------------------------------------------------------ dữ liệu link


@dataclass(frozen=True)
class InternalLink:
    """Một link nội bộ đã kiểm, lưu riêng khỏi chữ Markdown (T-033 mục 4.3, bước 1).

    ``section``: số thứ tự phần (0 = mở bài, như ``Flag.section``). ``anchor``: cụm từ có sẵn
    trong thân phần đó (dạng NFC, khoảng trắng đã gộp thành một dấu cách). ``post_id``: ID bài
    đích trong danh sách bài đã đăng. **Không có địa chỉ**: địa chỉ chỉ lấy từ ``SiteIndex`` lúc
    chèn.
    Dữ liệu đọc lại từ file nháp cũng là chưa tin cậy: ``apply_links`` kiểm lại từ đầu.
    """

    section: int
    anchor: str
    post_id: int

    def __post_init__(self) -> None:
        if type(self.section) is not int or self.section < 0:
            raise ValueError("section phải là số nguyên không âm")
        if type(self.post_id) is not int or self.post_id <= 0:
            raise ValueError("post_id phải là số nguyên dương")
        if not isinstance(self.anchor, str) or not 0 < len(self.anchor) <= MAX_ANCHOR_CHARS:
            raise ValueError("anchor sai kiểu hoặc dài quá")


class LinkSuggestion(BaseModel):
    # ``strict``: AI trả ``true``, ``"1"``, ``1.0`` thì khuôn báo sai, không tự đổi thành số 1
    # (sai thì bỏ, không sửa giùm; SL-T039-5). Khuôn JSON gửi AI vẫn là "integer".
    post_id: int = Field(strict=True, description="ID bài đích, đúng một ID trong <danh_sach_bai>")
    section: int = Field(strict=True, description="Số phần chứa cụm từ, như [Phần N]: 0 = mở bài")
    anchor: str = Field(description="Cụm 2-8 từ chép NGUYÊN VĂN từ thân phần đó")


class LinkSuggestions(BaseModel):
    """Khuôn AI trả về khi gợi ý liên kết nội bộ. Code kiểm từng gợi ý (``check_suggestions``)."""

    links: list[LinkSuggestion] = Field(description="Tối đa 5 gợi ý, mỗi bài đích tối đa một")


# ------------------------------------------------------------------ chuẩn hóa link


def _hosts(site: str) -> frozenset[str]:
    """Tên máy của site, cả dạng có và không có "www." (cùng một site)."""
    try:
        host = (urlsplit(site).hostname or "").rstrip(".")
    except ValueError:
        return frozenset()
    if not host:
        return frozenset()
    bare = host.removeprefix("www.")
    return frozenset({bare, "www." + bare})


def path_key(path: str) -> str:
    """Đường dẫn để so với danh sách bài: giải mã ``%``, NFC, chữ thường, xử lý ``.``/``..``,
    bỏ ``/`` thừa và ``/`` cuối. ``/Sua-Cua/``, ``/sua-cua``, ``//sua-cua/./`` là một."""
    text = unicodedata.normalize("NFC", unquote(path)).casefold()
    segments: list[str] = []
    for segment in text.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if segments:
                segments.pop()
            continue
        segments.append(segment)
    return "/" + "/".join(segments)


def _items_by_id(index: SiteIndex) -> dict[int, PublishedItem]:
    """Bài đã đăng theo ID. Link phải đúng site (kiểm lại, ``SiteIndex`` có thể dựng tay).
    Một ID xuất hiện hai lần (bài và trang trùng số) thì không biết là bài nào: bỏ cả hai."""
    seen: dict[int, PublishedItem | None] = {}
    for item in index.items:
        if is_site_link(item.link, index.site):
            seen[item.id] = None if item.id in seen else item
    return {post_id: item for post_id, item in seen.items() if item is not None}


def _items_by_path(index: SiteIndex) -> dict[str, PublishedItem]:
    """Bài đã đăng theo đường dẫn đã chuẩn hóa (``by_link()`` so nguyên văn nên không dùng)."""
    keys: dict[str, PublishedItem] = {}
    for item in index.items:
        if not is_site_link(item.link, index.site):
            continue
        parts = urlsplit(item.link)
        if not parts.query and not parts.fragment:  # link dạng "?p=…" không phải đường dẫn đẹp
            keys.setdefault(path_key(parts.path), item)
    return keys


# Tham số của link bài nháp / xem trước (YC-603): "?p=12", "?page_id=3", "preview=true"…, và
# "?name=", "?pagename=": WordPress mở bài/trang theo slug (bài nháp thì người đọc gặp trang 404).
_DRAFT_PARAMS = frozenset(
    {"p", "page_id", "preview", "preview_id", "preview_nonce", "name", "pagename"}
)
# PHP đổi " ", "." và "[" (không đóng) trong tên tham số thành "_" (SL-T039-3).
_PHP_NAME = str.maketrans(" .[", "___")


def _php_name(name: str) -> str:
    """Tên tham số như PHP (WordPress) đọc: cắt ở ký tự NUL, bỏ dấu cách đầu; "[" có "]" phía sau
    là biến dạng mảng nên tên dừng ở "[" ("?p[]=", "?p[0]=" là "p", SL-T039-9); còn lại đổi " ",
    ".", "[" thành "_". "?%20p=", "?page.id=" chính là "?p=", "?page_id=" với WordPress."""
    name = name.partition("\x00")[0].lstrip(" ")
    head, bracket, rest = name.partition("[")
    if bracket and "]" in rest:
        name = head
    return name.translate(_PHP_NAME).casefold()


def _is_draft_query(query: str) -> bool:
    return any(_php_name(name) in _DRAFT_PARAMS for name, _ in parse_qsl(query, True))


def _is_admin_path(key: str) -> bool:
    return key == "/wp-admin" or key.startswith("/wp-admin/") or key == "/wp-login.php"


# ------------------------------------------------------------------ chọn bài đích (YC-601, 602)


@dataclass(frozen=True)
class Candidate:
    """Một bài đích được phép link tới. ``required``: link bắt buộc theo phiếu giao bài."""

    item: PublishedItem
    required: bool = False


@dataclass(frozen=True)
class Candidates:
    items: tuple[Candidate, ...]
    notices: tuple[Notice, ...] = ()

    @property
    def required_ids(self) -> frozenset[int]:
        return frozenset(c.item.id for c in self.items if c.required)

    @property
    def level(self) -> Level:
        return worst(n.level for n in self.notices)

    def for_prompt(self) -> list[tuple[int, str]]:
        """(ID, tiêu đề) gửi AI: không có địa chỉ (T-033 mục 4.2)."""
        return [(c.item.id, c.item.title) for c in self.items]


_WORD = re.compile(r"[^\W_]+")
# Từ không mang chủ đề, bỏ trước khi so hai tiêu đề. Xét trên chữ CÓ DẤU ("của" khác "cửa").
_STOPWORDS = SLUG_TRAILING_STOPWORDS | frozenset(
    {"bị", "cách", "được", "cần", "đã", "sẽ", "đang", "rất", "nhất", "nhiều", "ra", "lên"}
)


def topic_words(text: str) -> frozenset[str]:
    """Từ không dấu, chữ thường, đã bỏ từ nối: dùng để tìm bài cùng nhóm."""
    words = _WORD.findall(unicodedata.normalize("NFC", text).lower())
    return frozenset(remove_accents(w) for w in words if w not in _STOPWORDS)


def _resolve_required(
    entry: object, by_id: dict[int, PublishedItem], by_path: dict[str, PublishedItem], hosts
) -> tuple[PublishedItem | None, str]:
    """Một link bắt buộc trong phiếu (ID, địa chỉ đầy đủ, đường dẫn hoặc slug) → bài đã đăng.

    Trả (bài, "") hoặc (None, lý do: "ngoai", "nhap", "sai", "khong_co")."""
    if type(entry) is int:
        item = by_id.get(entry)
        return (item, "") if item else (None, "khong_co")
    if not isinstance(entry, str) or not entry.strip() or len(entry) > 2000:
        return None, "sai"
    try:
        parts = urlsplit(entry.strip())
        host = (parts.hostname or "").rstrip(".")
    except ValueError:
        return None, "sai"
    path = parts.path
    if parts.scheme or parts.netloc:
        if parts.scheme.lower() not in ("http", "https", "") or host not in hosts:
            return None, "ngoai"
    else:  # "suachuacuasat.com/sua-cua/" (gõ thiếu "https://")
        first, _, rest = path.lstrip("/").partition("/")
        if first.lower().rstrip(".") in hosts:
            path = "/" + rest
    if _is_draft_query(parts.query):
        return None, "nhap"
    item = by_path.get(path_key(path))
    return (item, "") if item else (None, "khong_co")


def select_candidates(
    index: SiteIndex,
    *,
    kind: ArticleKind | str,
    title: str,
    keyword: str = "",
    required: Iterable[int | str] = (),
    current_id: int | None = None,
    max_related: int = MAX_RELATED,
) -> Candidates:
    """Chọn bài đích cho AI gợi ý anchor (T-033 mục 4.2 bước 1).

    - ``required``: link bắt buộc theo phiếu giao bài (YC-601: trang dịch vụ đích + link khác),
      cho bằng ID, địa chỉ đầy đủ, đường dẫn (``/sua-cua-keo-tphcm/``) hoặc slug. Luôn có mặt
      nếu có trong danh sách đã đăng; không có thì báo Chặn (danh sách chưa tải đủ thì Cảnh báo).
    - Bài hướng dẫn và trang dịch vụ: thêm tối đa ``max_related`` bài (``post``) cùng nhóm, tức
      có ít nhất ``MIN_SHARED_WORDS`` từ không dấu chung với tiêu đề và từ khóa (YC-602).
    - Trang khu vực: chỉ dùng link trong phiếu (trang dịch vụ chính, trang "Khu vực phục vụ").
    - Chỉ lấy từ ``index`` (bài ``publish``): bài nháp, hẹn giờ không bao giờ là bài đích (YC-603).
    """
    kind = ArticleKind(kind)
    by_id = _items_by_id(index)
    by_path = _items_by_path(index)
    hosts = _hosts(index.site)
    missing = Level.WARN if index.truncated else Level.BLOCK
    notices: list[Notice] = []
    chosen: list[Candidate] = []
    taken: set[int] = set()
    entries = list(islice(required, MAX_CONSIDERED + 1))
    if len(entries) > MAX_CONSIDERED:
        notices.append(
            Notice(Level.WARN, f"Phiếu có quá nhiều link bắt buộc; chỉ xét {MAX_CONSIDERED}.")
        )
    for entry in entries[:MAX_CONSIDERED]:
        item, why = _resolve_required(entry, by_id, by_path, hosts)
        shown = entry if type(entry) is int else " ".join(str(entry).split())[:120]
        if item is None:
            notices.append(_required_notice(why, shown, missing))
        elif item.id == current_id:
            notices.append(Notice(Level.WARN, f"Link bắt buộc «{shown}» trỏ tới chính bài này."))
        elif item.id not in taken:
            taken.add(item.id)
            chosen.append(Candidate(item, required=True))
    if len(taken) > MAX_LINKS:
        notices.append(
            Notice(
                Level.WARN, f"Phiếu có {len(taken)} link bắt buộc, bài chỉ chèn tối đa {MAX_LINKS}."
            )
        )
    # Thiếu trang đích trong phiếu: chỉ Cảnh báo ở bước chọn (app chưa nhập phiếu giao bài,
    # YC-101). Bước Chặn thật là ``check_links(..., required_ids)`` trên HTML cuối (M7 #11).
    if not taken and kind is ArticleKind.GUIDE:
        notices.append(
            Notice(
                Level.WARN, "Bài hướng dẫn chưa có trang dịch vụ đích (ghi trong phiếu giao bài)."
            )
        )
    if not taken and kind is ArticleKind.AREA:
        notices.append(
            Notice(
                Level.WARN,
                "Trang khu vực cần link tới trang dịch vụ chính và trang «Khu vực phục vụ» "
                "(ghi trong phiếu giao bài).",
            )
        )
    if kind is not ArticleKind.AREA and max_related > 0:
        related = _related(by_id, title, keyword, taken, current_id)[:max_related]
        chosen += [Candidate(item) for item in related]
    return Candidates(tuple(chosen), tuple(notices))


def _required_notice(why: str, shown: object, level: Level) -> Notice:
    if why == "ngoai":
        return Notice(Level.BLOCK, f"Link bắt buộc «{shown}» không thuộc website.")
    if why == "nhap":
        return Notice(
            Level.BLOCK,
            f"Link bắt buộc «{shown}» là link dạng bài nháp, xem trước hoặc mở theo mã số/slug "
            "(?p=, ?name=…): ghi đường dẫn đầy đủ của bài.",
        )
    if why == "sai":
        return Notice(Level.BLOCK, f"Link bắt buộc «{shown}» sai dạng.")
    return Notice(
        level,
        f"Trang đích bắt buộc «{shown}» chưa đăng hoặc không có trong danh sách bài trên site.",
    )


def _related(
    by_id: dict[int, PublishedItem],
    title: str,
    keyword: str,
    taken: set[int],
    current_id: int | None,
) -> list[PublishedItem]:
    """Bài (``post``) cùng nhóm, nhiều từ chung nhất trước; hòa thì tỉ lệ chung cao hơn, rồi ID."""
    words = topic_words(f"{title} {keyword}")
    if not words:
        return []
    scored = []
    for item in by_id.values():
        if item.type != "post" or item.id in taken or item.id == current_id:
            continue
        other = topic_words(item.title)
        shared = len(words & other)
        if shared >= MIN_SHARED_WORDS:
            scored.append((-shared, -2 * shared / (len(words) + len(other)), item.id, item))
    scored.sort(key=lambda row: row[:3])
    return [row[3] for row in scored]


# ------------------------------------------------------------------ anchor

# Ký tự Markdown/HTML: cụm từ có chúng thì chữ trong bài và chữ hiện ra khác nhau (``**``, ``[``,
# ``<``…), hoặc là chỗ "[cần bổ sung: …]". Gợi ý có chúng bị bỏ.
_MARKUP_CHARS = frozenset("*_`\\[]<>|~")
_HIDDEN_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn"})


def _anchor_words(anchor: object) -> tuple[list[str], str]:
    """Các từ (dạng NFC) của anchor, hoặc ([], lý do bỏ). Kiểm độ dài TRƯỚC mọi bước khác
    (tuyến tính)."""
    if not isinstance(anchor, str):
        return [], "cụm từ không phải chữ"
    if len(anchor) > 2 * MAX_ANCHOR_CHARS:
        return [], "cụm từ dài quá"
    # NFC: chữ có dấu dựng sẵn và chữ tổ hợp (dán từ máy Mac) nhìn y hệt nhau là một (SL-T039-1).
    words = unicodedata.normalize("NFC", anchor).split()
    text = " ".join(words)
    if not text:
        return [], "cụm từ trống"
    if len(text) > MAX_ANCHOR_CHARS:
        return [], "cụm từ dài quá"
    if any(unicodedata.category(ch) in _HIDDEN_CATEGORIES for ch in text) or (
        IGNORABLE_NOT_CF.search(text)
    ):
        return [], "cụm từ có ký tự vô hình hoặc ký tự điều khiển"
    if any(ch in _MARKUP_CHARS for ch in text):
        return [], "cụm từ có ký tự định dạng ([ ] * _ ` < > | ~ \\)"
    counted = sum(1 for w in words if any(ch.isalnum() for ch in w))
    if counted < MIN_ANCHOR_WORDS or len(words) > MAX_ANCHOR_WORDS:
        return [], f"cụm từ phải dài {MIN_ANCHOR_WORDS}–{MAX_ANCHOR_WORDS} từ"
    if has_link(text):
        return [], "cụm từ trông như địa chỉ web hoặc email"
    return words, ""


def _anchor_pattern(words: Sequence[str]) -> re.Pattern[str]:
    """Tìm đúng các từ theo thứ tự; giữa hai từ là khoảng trắng bất kỳ (dấu cách, xuống dòng,
    dấu cách không ngắt), vì trình duyệt hiện mọi dãy khoảng trắng thành một dấu cách."""
    return re.compile(r"\s+".join(re.escape(w) for w in words))


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_" or unicodedata.combining(ch) > 0


def _find(text: str, pattern: re.Pattern[str]) -> tuple[int, int] | None:
    """Lần xuất hiện đầu tiên đứng trọn từ ("cửa cuốn" không khớp trong "xcửa cuốnx")."""
    pos = 0
    while (match := pattern.search(text, pos)) is not None:
        start, end = match.span()
        if (start == 0 or not _is_word_char(text[start - 1])) and (
            end == len(text) or not _is_word_char(text[end])
        ):
            return start, end
        pos = start + 1
    return None


def _mask_brackets(text: str) -> str:
    """Thay "[…]" (cả hai dấu ngoặc) bằng ký tự "\\x00", giữ nguyên độ dài: chỗ
    "[cần bổ sung: …]" không được làm chữ của link. "[" không có "]" thì che tới hết."""
    if "[" not in text:
        return text
    out: list[str] = []
    pos = 0
    while (start := text.find("[", pos)) != -1:
        end = text.find("]", start + 1)
        stop = len(text) if end == -1 else end + 1
        out.append(text[pos:start])
        out.append("\x00" * (stop - start))
        pos = stop
    out.append(text[pos:])
    return "".join(out)


# ------------------------------------------------------------------ đoạn văn trong Markdown


def _mask_code(line: str) -> str:
    """Che chữ từ dấu "`" đầu tới dấu "`" cuối của dòng (đoạn `mã`; che rộng cho chắc)."""
    first = line.find("`")
    last = line.rfind("`")
    if first == last:
        return line
    return line[:first] + "\x00" * (last + 1 - first) + line[last + 1 :]


def _is_atx_heading(stripped: str, indent: int) -> bool:
    if indent > 3 or not stripped.startswith("#"):
        return False
    level = len(stripped) - len(stripped.lstrip("#"))
    return level <= 6 and (len(stripped) == level or stripped[level] in " \t")


def _is_rule(stripped: str, chars: str) -> bool:
    """Dòng chỉ có một loại ký tự trong ``chars`` (bỏ dấu cách): gạch ngang, gạch dưới tiêu đề."""
    compact = stripped.replace(" ", "").replace("\t", "")
    return bool(compact) and compact[0] in chars and compact == compact[0] * len(compact)


def _is_list_item(stripped: str) -> bool:
    if stripped[:1] in "-*+":
        return stripped[1:2] in (" ", "\t")
    digits = len(stripped) - len(stripped.lstrip("0123456789"))
    return (
        0 < digits <= 9
        and stripped[digits : digits + 1] in (".", ")")
        and (stripped[digits + 1 : digits + 2] in (" ", "\t"))
    )


def markdown_blocks(body: str) -> list[str]:
    """Các đoạn văn (khối) chèn link được trong thân một phần, theo thứ tự.

    Mỗi đoạn văn, mỗi mục danh sách, mỗi dòng bảng là một khối. Bỏ hẳn: tiêu đề con (``###``,
    dòng gạch dưới ``===``/``---``), khối mã (```` ``` ````, ``~~~``). Đoạn `mã` và chỗ "[…]" bị
    che. Đọc gần đúng như bộ chuyển Markdown; chỗ đọc khác thì ``apply_links`` không tìm thấy cụm
    từ và báo bỏ qua (không bao giờ chèn sai chỗ).
    """
    blocks: list[str] = []
    current: list[str] = []
    fence = ""

    def flush() -> None:
        if current:
            blocks.append(_mask_brackets("\n".join(current)))
            current.clear()

    for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if fence:
            if stripped.startswith(fence):
                fence = ""
            continue
        if stripped.startswith(("```", "~~~")):
            flush()
            fence = stripped[:3]
        elif not stripped or _is_atx_heading(stripped, indent):
            flush()
        elif current and _is_rule(stripped, "=-"):
            current.clear()  # dòng gạch dưới: cả khối phía trên là tiêu đề
        elif _is_rule(stripped, "-*_") and len(stripped.replace(" ", "")) >= 3:
            flush()  # đường kẻ ngang
        else:
            table_row = stripped.startswith("|")
            if table_row or _is_list_item(stripped):
                flush()
            current.append(_mask_code(line))
            if table_row:
                flush()
    flush()
    return blocks


# ------------------------------------------------------------------ kiểm gợi ý của AI (A2)


@dataclass(frozen=True)
class LinkReview:
    """Kết quả kiểm gợi ý AI. ``rejected``: mỗi gợi ý bị bỏ một câu (không chép chữ AI).
    ``missing_required``: ID bài bắt buộc chưa có gợi ý đạt (AI không tìm được cụm từ)."""

    links: tuple[InternalLink, ...]
    rejected: tuple[str, ...]
    missing_required: tuple[int, ...]


def _field(raw: object, name: str) -> object:
    if isinstance(raw, Mapping):
        return raw.get(name)
    return getattr(raw, name, None)


def check_suggestions(
    raw: LinkSuggestions | Iterable[object], parts: Sequence[Section], candidates: Candidates
) -> LinkReview:
    """Kiểm từng gợi ý anchor của AI; sai thì bỏ, không sửa giùm (T-033 mục 4.2 bước 4).

    Gợi ý đạt khi: ``post_id`` nằm trong ``candidates``; ``section`` có trong bài; ``anchor``
    dài 2–8 từ, không ký tự định dạng hay vô hình, không giống địa chỉ web, có nguyên văn (đứng
    trọn từ) trong **thân** phần đó (không tính tiêu đề, tiêu đề con, mã, chỗ "[…]"), không trùng
    anchor khác; mỗi bài đích tối đa 1 link, tổng tối đa ``MAX_LINKS``; không 2 link trong cùng
    một đoạn văn. Gợi ý cho bài bắt buộc được xét trước để không bị gợi ý khác chiếm chỗ.
    """
    items = list(islice(raw.links if isinstance(raw, LinkSuggestions) else raw, MAX_CONSIDERED + 1))
    extra = len(items) > MAX_CONSIDERED
    items = items[:MAX_CONSIDERED]
    allowed = {c.item.id for c in candidates.items}
    required = candidates.required_ids

    def is_required(k: int) -> bool:
        post_id = _field(items[k], "post_id")
        return type(post_id) is int and post_id in required

    order = sorted(range(len(items)), key=lambda k: not is_required(k))
    blocks: dict[int, list[str]] = {}
    used_targets: set[int] = set()
    used_anchors: set[str] = set()
    used_blocks: set[tuple[int, int]] = set()
    links: list[InternalLink] = []
    rejected: list[tuple[int, str]] = []
    for k in order:
        post_id = _field(items[k], "post_id")
        section = _field(items[k], "section")
        problem = ""
        if type(post_id) is not int or post_id not in allowed:
            problem = "bài đích không có trong danh sách được chọn"
        elif post_id in used_targets:
            problem = "bài đích đã có link khác (mỗi bài tối đa một link)"
        elif len(links) >= MAX_LINKS:
            problem = f"bài đã đủ {MAX_LINKS} link"
        elif type(section) is not int or not 0 <= section < len(parts):
            problem = "số phần không có trong bài"
        else:
            words, problem = _anchor_words(_field(items[k], "anchor"))
            anchor = " ".join(words)
            if not problem and anchor.casefold() in used_anchors:
                problem = "cụm từ trùng với link khác"
            if not problem:
                if section not in blocks:  # so ở dạng NFC như cụm từ (``_anchor_words``)
                    body = unicodedata.normalize("NFC", parts[section].body)
                    blocks[section] = markdown_blocks(body)
                pattern = _anchor_pattern(words)
                hits = [b for b, text in enumerate(blocks[section]) if _find(text, pattern)]
                free = [b for b in hits if (section, b) not in used_blocks]
                if not hits:
                    problem = "cụm từ không có nguyên văn trong thân phần đó"
                elif not free:
                    problem = "đoạn văn chứa cụm từ đã có link khác"
                else:
                    used_blocks.add((section, free[0]))
                    used_targets.add(post_id)
                    used_anchors.add(anchor.casefold())
                    links.append(InternalLink(section=section, anchor=anchor, post_id=post_id))
        if problem:
            rejected.append((k, f"Gợi ý {k + 1}: {problem}."))
    rejected.sort()
    if extra:
        rejected.append((len(items), f"Bỏ các gợi ý sau gợi ý thứ {MAX_CONSIDERED} (quá nhiều)."))
    missing = tuple(sorted(required - used_targets))
    return LinkReview(tuple(links), tuple(message for _, message in rejected), missing)


# ------------------------------------------------------------------ chèn link vào HTML

_VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "frame", "hr", "img", "input", "keygen", "link",
     "meta", "param", "source", "track", "wbr"}
)  # fmt: skip
# Không bao giờ chèn link bên trong các thẻ này (link lồng link, tiêu đề, mã, chú thích ảnh…),
# cả các thẻ bộ lọc HTML bỏ luôn nội dung (``DANGEROUS_TAGS``: script, xmp, plaintext…).
_NO_LINK_TAGS = DANGEROUS_TAGS | frozenset(
    {"a", "h1", "h2", "h3", "h4", "h5", "h6", "code", "pre", "kbd", "samp", "var", "label",
     "figcaption", "caption"}
)  # fmt: skip
# Thẻ coi là một "đoạn văn" (mỗi đoạn tối đa một link).
_PARAGRAPH_TAGS = frozenset(
    {"p", "li", "dd", "dt", "td", "th", "blockquote", "div", "section", "article", "aside",
     "header", "footer", "main", "nav", "figure", "address", "details", "summary", "pre",
     "figcaption", "caption", "h1", "h2", "h3", "h4", "h5", "h6"}
)  # fmt: skip
# Thẻ khối: chữ nằm ngay dưới gốc (không trong đoạn nào) bị các thẻ này chia thành đoạn khác nhau.
_BLOCK_TAGS = _PARAGRAPH_TAGS | {"ul", "ol", "dl", "table", "thead", "tbody", "tfoot", "tr", "hr"}
# Thẻ định dạng cấm chèn mà trình duyệt tự MỞ LẠI ở chữ phía sau khi bị đóng ngầm
# ("<p><a href=x>chữ</p><p>chữ sau" thì "chữ sau" vẫn là link): coi như còn mở tới thẻ đóng
# đúng tên (hoặc "<a>" mới).
_REOPENED_TAGS = frozenset({"a", "code"})


@dataclass(frozen=True)
class _Run:
    """Một nút chữ: vị trí trong HTML gốc, chữ đã giải mã, phần, đoạn văn, chèn được không, có
    nằm trong ``<code>`` không."""

    start: int
    end: int
    text: str
    section: int
    paragraph: tuple[str, int]
    allowed: bool
    in_code: bool


class _TextRuns(HTMLParser):
    """Đọc HTML một lượt, ghi lại các nút chữ (không sửa gì).

    Phần: ``<h2>`` thứ k mở đầu phần k (phần 0 là mở bài, trước ``<h2>`` đầu tiên). Vị trí của
    nút chữ lấy từ ``getpos()``; nút chữ nào giải mã lại từ HTML gốc không ra đúng chữ đã đọc
    (cấu trúc lạ bộ đọc bỏ qua) thì không chèn vào đó.

    Biến và hàm riêng của lớp này đặt tên ``__x`` (Python đổi thành ``_TextRuns__x``) để không
    bao giờ trùng tên riêng của ``HTMLParser``: thư viện chuẩn thêm tên riêng ở cả bản vá nhỏ
    (Python 3.12.15 thêm bộ đệm ``_pending``, trùng biến cũ của lớp này: SL-T039-6). Ngoài các
    hàm cố ý ghi đè (``handle_*``, ``unknown_decl``), tên công khai (``runs``, ``linked``,
    ``read``) không có trong ``HTMLParser``. Test canh: ``test_html_readers_never_shadow_*``.
    """

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.__source = source
        self.runs: list[_Run] = []
        self.linked: set[tuple[str, int]] = set()  # đoạn văn đã có sẵn <a href>
        self.__line_starts = [0]
        newline = source.find("\n")
        while newline != -1:
            self.__line_starts.append(newline + 1)
            newline = source.find("\n", newline + 1)
        # Thẻ đang mở, kèm đoạn văn chứa nó (None: chưa ở trong đoạn nào). Đếm sẵn số thẻ mở
        # theo tên và số thẻ cấm chèn để mỗi bước O(1): HTML lồng rất sâu không làm chậm.
        self.__stack: list[tuple[str, tuple[str, int] | None]] = []
        self.__open: dict[str, int] = {}
        self.__serial = 0
        self.__blocked = 0  # số thẻ cấm chèn đang mở
        self.__dangling: set[str] = set()  # thẻ trong _REOPENED_TAGS bị đóng ngầm
        self.__section = 0
        self.__root_block = 0
        self.__text_start = -1  # nút chữ đang đọc dở: vị trí đầu và các mẩu chữ
        self.__text_parts: list[str] = []

    def __pos(self) -> int:
        line, column = self.getpos()
        return self.__line_starts[line - 1] + column

    def __paragraph(self) -> tuple[str, int]:
        if self.__stack and self.__stack[-1][1] is not None:
            return self.__stack[-1][1]
        return "", self.__root_block

    def __flush(self, end: int) -> None:
        if self.__text_start < 0:
            return
        start, text = self.__text_start, "".join(self.__text_parts)
        self.__text_start, self.__text_parts = -1, []
        allowed = (
            not self.__blocked
            and not self.__dangling
            and html.unescape(self.__source[start:end]) == text
        )
        # Chỉ tính "<code>" đang mở: "<code>" bị đóng ngầm thì bộ lọc HTML đóng hẳn ở đó, chữ
        # phía sau trong HTML gửi đi không còn là mã.
        in_code = bool(self.__open.get("code"))
        self.runs.append(
            _Run(start, end, text, self.__section, self.__paragraph(), allowed, in_code)
        )

    def handle_starttag(self, tag, attrs):
        self.__flush(self.__pos())
        if tag == "h2":
            self.__section += 1
        if tag in _BLOCK_TAGS:
            self.__root_block += 1
        if tag == "a":
            self.__dangling.discard("a")  # "<a>" mới đóng hẳn link cũ
            if any(name == "href" for name, _ in attrs):
                self.linked.add(self.__paragraph())
        if tag not in _VOID_TAGS:  # "<a/>" vẫn là thẻ mở với trình duyệt
            self.__serial += 1
            if tag in _PARAGRAPH_TAGS:
                paragraph = (tag, self.__serial)
            else:
                paragraph = self.__stack[-1][1] if self.__stack else None
            self.__stack.append((tag, paragraph))
            self.__open[tag] = self.__open.get(tag, 0) + 1
            self.__blocked += tag in _NO_LINK_TAGS

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        self.__flush(self.__pos())
        self.__dangling.discard(tag)
        # Thẻ đóng lạc (không có thẻ mở) thì bỏ qua, kể cả không tách đoạn: bộ lọc HTML bỏ hẳn
        # thẻ này nên chữ hai bên vẫn là một đoạn ("[" trước nó vẫn che chữ sau nó).
        if self.__open.get(tag):
            if tag in _BLOCK_TAGS:
                self.__root_block += 1
            while self.__stack:
                name, _ = self.__stack.pop()
                self.__open[name] -= 1
                self.__blocked -= name in _NO_LINK_TAGS
                if name == tag:
                    break
                if name in _REOPENED_TAGS:
                    self.__dangling.add(name)

    def handle_data(self, data):
        if self.__text_start < 0:
            self.__text_start = self.__pos()
        self.__text_parts.append(data)

    def __boundary(self, _data=None) -> None:
        self.__flush(self.__pos())

    handle_comment = handle_decl = handle_pi = unknown_decl = __boundary

    def read(self) -> _TextRuns:
        self.feed(self.__source)
        self.close()
        self.__flush(len(self.__source))
        return self


def _masked_runs(runs: Sequence[_Run]) -> list[str]:
    """Chữ của từng nút chữ, che chỗ "[…]" theo **đoạn văn** chứ không theo nút chữ: "[cần bổ
    sung: <strong>giá</strong> thay ray mới]" bị thẻ cắt thành nhiều nút chữ vẫn bị che hết
    (SL-T039-2). Như ``markdown_blocks``: "[" không có "]" thì che tới hết đoạn, và dấu ngoặc
    trong ``<code>`` không tính (``_mask_code`` che `mã` trước khi che "[…]": SL-T039-8). Dấu
    ngoặc ở mọi nút chữ khác người đọc thấy đều tính, cả nút không chèn được (link có sẵn…)."""
    unclosed: set[tuple[str, int]] = set()  # đoạn văn còn "[" chưa đóng
    masked: list[str] = []
    for run in runs:
        if run.in_code:  # không chèn vào mã; ngoặc trong mã không mở, không đóng "[…]"
            masked.append("\x00" * len(run.text))
            continue
        carried = run.paragraph in unclosed
        text = "[" + run.text if carried else run.text  # che tiếp từ đầu nút chữ
        last = text.rfind("[")
        if last != -1 and text.find("]", last) == -1:
            unclosed.add(run.paragraph)
        else:
            unclosed.discard(run.paragraph)
        text = _mask_brackets(text)
        masked.append(text[1:] if carried else text)
    return masked


def _nfc_offsets(text: str) -> tuple[str, dict[int, int] | None]:
    """``text`` dạng NFC, kèm vị trí trong ``text`` của đầu mỗi cụm (chữ cái + dấu tổ hợp đi sau)
    theo vị trí trong chữ NFC. ``None``: ``text`` đã là NFC, vị trí như nhau."""
    if unicodedata.is_normalized("NFC", text):
        return text, None
    pieces: list[str] = []
    offsets: dict[int, int] = {}
    size = start = 0
    for end in range(1, len(text) + 1):
        if end == len(text) or not unicodedata.combining(text[end]):
            offsets[size] = start
            piece = unicodedata.normalize("NFC", text[start:end])
            pieces.append(piece)
            size += len(piece)
            start = end
    offsets[size] = len(text)
    return "".join(pieces), offsets


def _find_in_run(
    text: str,
    normalized: tuple[str, dict[int, int] | None],
    pattern: re.Pattern[str],
    words: Sequence[str],
) -> tuple[int, int] | None:
    """Vị trí trong ``text`` (chữ gốc của nút chữ) của lần xuất hiện đầu tiên của cụm từ, tìm
    trên chữ NFC (``normalized``: chữ đã che "[…]" rồi qua ``_nfc_offsets``). Chữ gốc dạng tổ
    hợp NFD (dán từ máy Mac) vẫn tìm được cụm từ NFC của AI và ngược lại (SL-T039-1); chữ trong
    link là chữ gốc, kiểm lại phải đúng các từ của cụm từ."""
    norm, offsets = normalized
    span = _find(norm, pattern)
    if span is None or offsets is None:
        return span
    start, end = offsets.get(span[0]), offsets.get(span[1])
    if start is None or end is None:
        return None
    if unicodedata.normalize("NFC", text[start:end]).split() != list(words):
        return None
    return start, end


@dataclass(frozen=True)
class LinkPlacement:
    """Kết quả chèn: HTML mới, link đã chèn, câu báo cho từng link bỏ qua."""

    html: str
    applied: tuple[InternalLink, ...]
    skipped: tuple[str, ...]


def place_links(html_text: str, links: Iterable[InternalLink], index: SiteIndex) -> LinkPlacement:
    """Chèn link nội bộ vào HTML bài (T-033 mục 4.3 bước 2). Xem ``apply_links``."""
    by_id = _items_by_id(index)
    reader = _TextRuns(html_text).read()
    runs = reader.runs
    by_section: dict[int, list[int]] = {}
    for r, run in enumerate(runs):
        if run.allowed and run.paragraph not in reader.linked:
            by_section.setdefault(run.section, []).append(r)
    masked = _masked_runs(runs)
    normalized: dict[int, tuple[str, dict[int, int] | None]] = {}
    taken: set[tuple[str, int]] = set()
    used_targets: set[int] = set()
    used_anchors: set[str] = set()
    inserts: dict[int, tuple[int, int, str]] = {}
    applied: list[InternalLink] = []
    skipped: list[str] = []
    for number, link in enumerate(islice(links, MAX_CONSIDERED), start=1):
        if not isinstance(link, InternalLink):
            skipped.append(f"Link {number}: dữ liệu sai khuôn.")
            continue
        item = by_id.get(link.post_id)
        words, problem = _anchor_words(link.anchor)
        anchor = " ".join(words).casefold()
        if item is None:
            problem = "bài đích không có trong danh sách bài đã đăng (chưa đăng, về nháp, đã xóa)"
        elif link.post_id in used_targets:
            problem = "bài đích đã có link khác"
        elif len(applied) >= MAX_LINKS:
            problem = f"bài đã đủ {MAX_LINKS} link"
        elif not problem and anchor in used_anchors:
            problem = "cụm từ trùng với link khác"
        hit = None
        if not problem:
            pattern = _anchor_pattern(words)
            for r in by_section.get(link.section, ()):
                if runs[r].paragraph not in taken:
                    if r not in normalized:
                        normalized[r] = _nfc_offsets(masked[r])
                    span = _find_in_run(runs[r].text, normalized[r], pattern, words)
                    if span is not None:
                        hit = (r, *span)
                        break
            if hit is None:
                problem = (
                    f"không thấy cụm từ ở chỗ chèn được trong phần {link.section} (không tính "
                    "tiêu đề, mã, link có sẵn, đoạn đã có link)"
                )
        if problem:
            skipped.append(f"Link {number} (bài #{link.post_id}): {problem}.")
            continue
        r, start, end = hit
        inserts[r] = (start, end, item.link)
        taken.add(runs[r].paragraph)
        used_targets.add(link.post_id)
        used_anchors.add(anchor)
        applied.append(link)
    out: list[str] = []
    previous = 0
    for r in sorted(inserts):
        run = runs[r]
        start, end, href = inserts[r]
        out.append(html_text[previous : run.start])
        out.append(html.escape(run.text[:start], quote=False))
        out.append(f'<a href="{html.escape(href, quote=True)}">')
        out.append(html.escape(run.text[start:end], quote=False))
        out.append("</a>")
        out.append(html.escape(run.text[end:], quote=False))
        previous = run.end
    out.append(html_text[previous:])
    return LinkPlacement("".join(out), tuple(applied), tuple(skipped))


def apply_links(html_text: str, links: Iterable[InternalLink], index: SiteIndex) -> str:
    """HTML bài có thêm link nội bộ, chỉ do code chèn (T-033 mục 4.3).

    Duyệt **nút chữ** bằng ``html.parser`` (không dùng biểu thức chính quy trên HTML), bọc lần
    xuất hiện đầu tiên (đứng trọn từ) của anchor trong phần ``link.section`` bằng ``<a href>``.
    ``href`` lấy từ ``index`` theo ``post_id`` (không bao giờ từ AI), escape bằng
    ``html.escape(quote=True)``. Không chèn bên trong ``<a>``, tiêu đề ``<h1>``–``<h6>``,
    ``<code>``, ``<pre>``, chú thích ảnh…, không chèn vào đoạn đã có link, không chèn vào chỗ
    "[…]". Link nào không chèn được thì bỏ qua (xem ``place_links`` để biết lý do).

    Phần k bắt đầu ở thẻ ``<h2>`` thứ k: Giai đoạn 5 dựng mỗi phần thành một ``<h2>`` + thân,
    tiêu đề con trong thân là ``<h3>`` trở xuống. HTML trả về **vẫn phải** qua ``sanitize_html``
    trước khi gửi lên WordPress. Nên gọi trên HTML **đã** qua ``sanitize_html`` (bộ lọc bỏ thẻ lạ
    như ``<section>``, nội dung ``<script>``…): khi đó đoạn văn và chỗ "[…]" hàm này thấy đúng
    như HTML gửi đi.
    """
    return place_links(html_text, links, index).html


# ------------------------------------------------------------------ kiểm link trên HTML cuối


@dataclass(frozen=True)
class LinkCheck:
    """Kết quả kiểm một link. ``href``: nguyên văn trong bài (đã giải mã ``&amp;``…), chưa
    escape: giao diện phải hiện bằng chữ thường hoặc ``html.escape`` (U1)."""

    href: str
    kind: LinkKind
    level: Level
    message: str
    post_id: int | None = None


@dataclass(frozen=True)
class LinkReport:
    links: tuple[LinkCheck, ...]
    missing: tuple[Notice, ...]  # link bắt buộc chưa có trong bài

    @property
    def level(self) -> Level:
        return worst([*(c.level for c in self.links), *(n.level for n in self.missing)])

    @property
    def external(self) -> tuple[str, ...]:
        """Link ra ngoài, để liệt kê cho người dùng xem trước khi gửi (không tự gọi tới)."""
        return tuple(c.href for c in self.links if c.kind is LinkKind.EXTERNAL)


class _Anchors(HTMLParser):
    """Lấy ``href`` của mọi thẻ ``<a>`` và mọi ``id`` (cho link neo ``#muc``)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        href = None
        for name, value in attrs:
            if name == "id" or (name == "name" and tag == "a"):
                self.ids.add(value or "")
            elif name == "href" and href is None and tag == "a":
                href = value or ""  # trình duyệt dùng thuộc tính đầu tiên khi bị lặp
        if href is not None:
            self.hrefs.append(href)

    handle_startendtag = handle_starttag


# Trình duyệt chỉ bỏ dấu cách và ký tự điều khiển C0 ở hai đầu link (không bỏ dấu cách không
# ngắt: " https://…" là link tương đối, sẽ bị Chặn).
_URL_TRIM = "".join(map(chr, range(0x21)))
_MSG_PUBLISHED = "Link tới bài đã đăng."
_MSG_NOT_PUBLISHED = (
    "Link nội bộ tới trang chưa đăng, đã xóa hoặc gõ sai (không có trong danh sách bài đã đăng)."
)
_MSG_UNKNOWN = "Danh sách bài trên site chưa tải đủ nên chưa kết luận được link này còn hay hỏng."
_MSG_DRAFT = (
    "Link dạng bài nháp, xem trước hoặc mở theo mã số/slug (?p=, ?page_id=, ?name=, preview=…): "
    "người đọc có thể không mở được, dùng đường dẫn đầy đủ của bài đã đăng."
)
# Cổng chuẩn của giao thức kia: "https://…:80", "http://…:443" không mở được.
_WRONG_PORT = {"http": 443, "https": 80}
# Dấu chấm giữa các nhãn của tên máy theo IDNA (RFC 3490 mục 3.1): ".", "。", "．", "｡".
_HOST_DOTS = re.compile("[.。．｡]")
_MAX_LABEL = 63  # nhãn dài nhất của một tên máy


def _browser_host(host: str) -> str:
    """Tên máy như trình duyệt đọc: giải mã "%", rồi từng nhãn theo IDNA (``nameprep``: bỏ ký tự
    vô nghĩa, đổi chữ toàn khổ, chữ hoa…), dấu chấm "。" cũng là dấu chấm ("suachuacuasat%2Ecom",
    "ｓｕａ….com" là chính site). Không đổi được thì giữ nguyên.

    Nhãn vẫn còn chữ không phải ASCII sau ``nameprep`` mà dài quá 63 ký tự thì không là tên máy
    thật: giữ nguyên tên máy, không mã punycode (punycode của Python chạy bậc hai theo độ dài
    nhãn: SL-T039-7). Không chặn theo độ dài chữ gốc: ``nameprep`` có thể bỏ bớt ký tự."""
    if host.isascii() and "%" not in host:
        return host
    labels = _HOST_DOTS.split(unquote(host))
    if len(labels) > 1 and not labels[-1]:
        labels.pop()  # một dấu chấm cuối
    out: list[str] = []
    try:
        for label in labels:
            if not label.isascii():
                label = nameprep(label)
                if not label.isascii() and len(label) > _MAX_LABEL:
                    return host
            out.append(ToASCII(label).decode("ascii"))
    except UnicodeError:
        return host
    return ".".join(out).lower()


def _classify(
    href: str,
    hosts: frozenset[str],
    by_path: dict[str, PublishedItem],
    ids: set[str],
    truncated: bool,
) -> LinkCheck:
    def result(kind, level, message, post_id=None) -> LinkCheck:
        return LinkCheck(href, kind, level, message, post_id)

    value = href.strip(_URL_TRIM)
    if not value:
        return result(LinkKind.OTHER, Level.WARN, "Link rỗng (trỏ về chính trang này).")
    if any(ch.isspace() or unicodedata.category(ch) in _HIDDEN_CATEGORIES for ch in value) or (
        "\\" in value
    ):
        return result(
            LinkKind.OTHER,
            Level.BLOCK,
            "Link có dấu cách, ký tự vô hình hoặc dấu \\: trình duyệt hiểu khác điều ta thấy.",
        )
    if not is_safe_url(value):
        return result(
            LinkKind.OTHER,
            Level.BLOCK,
            "Link không an toàn (javascript:, data:, «//»…): bộ lọc HTML sẽ bỏ link này.",
        )
    try:
        parts = urlsplit(value)
        port = parts.port
        host = (parts.hostname or "").rstrip(".")
    except ValueError:
        return result(LinkKind.OTHER, Level.BLOCK, "Link sai dạng.")
    scheme = parts.scheme.lower()
    if scheme in ("mailto", "tel"):
        return result(LinkKind.OTHER, Level.GOOD, "Link email hoặc điện thoại.")
    if parts.netloc:
        if "@" in parts.netloc:
            return result(
                LinkKind.EXTERNAL, Level.BLOCK, "Link có «@» trong tên máy (dạng giả địa chỉ)."
            )
        if host not in hosts and _browser_host(host) in hosts:  # SL-T039-4
            return result(
                LinkKind.INTERNAL,
                Level.BLOCK,
                "Tên website viết dạng lạ (mã %, chữ toàn khổ, dấu «。»…): trình duyệt hiểu "
                "khác điều ta thấy, dùng đúng tên website.",
            )
        if host in hosts and port == _WRONG_PORT.get(scheme):
            return result(
                LinkKind.INTERNAL,
                Level.BLOCK,
                "Link tới website qua cổng của giao thức khác (https…:80, http…:443): người đọc "
                "không mở được.",
            )
        if host not in hosts or port not in (None, 80, 443):
            return result(
                LinkKind.EXTERNAL,
                Level.WARN,
                "Link ra ngoài: xem lại bằng mắt trước khi gửi (phần mềm không tự mở link này).",
            )
    elif not value.startswith(("/", "#", "?")):
        return result(
            LinkKind.INTERNAL,
            Level.BLOCK,
            "Link tương đối không rõ trỏ tới đâu: dùng đường dẫn đầy đủ.",
        )
    if value.startswith("#"):
        fragment = parts.fragment
        if fragment in ids or unquote(fragment) in ids:
            return result(LinkKind.ANCHOR, Level.GOOD, "Neo tới một mục trong bài.")
        return result(LinkKind.ANCHOR, Level.WARN, "Neo trong bài không trỏ tới mục nào.")
    if _is_draft_query(parts.query):
        return result(LinkKind.INTERNAL, Level.BLOCK, _MSG_DRAFT)
    if value.startswith("?"):
        return result(LinkKind.INTERNAL, Level.WARN, "Link chỉ có tham số: trỏ về chính trang này.")
    key = path_key(parts.path)
    if _is_admin_path(key):
        return result(LinkKind.INTERNAL, Level.BLOCK, "Link vào trang quản trị WordPress.")
    item = by_path.get(key)
    if item is not None:
        if scheme == "http":
            return result(
                LinkKind.INTERNAL,
                Level.WARN,
                "Link nội bộ dùng http://, nên dùng https://.",
                item.id,
            )
        return result(LinkKind.INTERNAL, Level.GOOD, _MSG_PUBLISHED, item.id)
    if key == "/":
        return result(LinkKind.INTERNAL, Level.GOOD, "Link về trang chủ.")
    if key.startswith("/wp-content/uploads/"):
        return result(
            LinkKind.INTERNAL,
            Level.WARN,
            "Link tới file trong thư viện Media: phần mềm chưa kiểm được file còn hay không.",
        )
    if truncated:
        return result(LinkKind.INTERNAL, Level.WARN, _MSG_UNKNOWN)
    return result(LinkKind.INTERNAL, Level.BLOCK, _MSG_NOT_PUBLISHED)


def check_links(html_text: str, index: SiteIndex, required_ids: Iterable[int] = ()) -> LinkReport:
    """Kiểm mọi link ``<a href>`` trong HTML cuối của bài (YC-603, YC-604; M7 #11).

    ``html_text`` là HTML cuối, **đã** qua ``sanitize_html`` (đọc trước bộ lọc thì link trong
    ``<noscript>``, ``<template>`` vẫn được tính dù bộ lọc bỏ hẳn). ``index`` phải vừa tải lại
    từ site (``SiteIndexStore.refresh``) ngay trước khi gửi nháp.

    - Nội bộ (cùng tên miền, có hoặc không "www.", hoặc đường dẫn ``/…``): so với danh sách bài
      đã đăng sau khi chuẩn hóa (``path_key``). Không có trong danh sách → Chặn (bài nháp, hẹn giờ,
      đã xóa, gõ sai); ``index.truncated`` thì chỉ Cảnh báo, không kết luận "link hỏng".
      Dạng ``?p=``, ``?page_id=``, ``?name=``, ``?pagename=``, ``preview=…`` (cả dạng PHP tự đổi
      tên như ``?page.id=``), trang quản trị, tên website viết dạng lạ (``%2E``, chữ toàn khổ),
      ``https://…:80`` → Chặn.
    - Ra ngoài → Cảnh báo, chỉ liệt kê (``LinkReport.external``): **không gọi tới** link nào.
    - ``#muc``: phải có ``id`` tương ứng trong bài, không có → Cảnh báo.
    - ``required_ids`` (link bắt buộc theo phiếu, ``Candidates.required_ids``): bài nào chưa có
      link đạt trong HTML → Chặn.
    """
    reader = _Anchors()
    reader.feed(html_text)
    reader.close()
    hosts = _hosts(index.site)
    by_path = _items_by_path(index)
    checks = tuple(
        _classify(href, hosts, by_path, reader.ids, index.truncated) for href in reader.hrefs
    )
    linked = {c.post_id for c in checks if c.post_id is not None and c.level is not Level.BLOCK}
    by_id = _items_by_id(index)
    missing: list[Notice] = []
    for post_id in dict.fromkeys(islice(required_ids, MAX_CONSIDERED)):
        item = by_id.get(post_id)
        if item is None:
            level = Level.WARN if index.truncated else Level.BLOCK
            missing.append(
                Notice(
                    level, f"Trang đích bắt buộc #{post_id} không có trong danh sách bài đã đăng."
                )
            )
        elif post_id not in linked:
            missing.append(Notice(Level.BLOCK, f"Thiếu link bắt buộc tới «{item.title}»."))
    return LinkReport(checks, tuple(missing))


__all__ = [
    "MAX_ANCHOR_WORDS",
    "MAX_CONSIDERED",
    "MAX_LINKS",
    "MAX_RELATED",
    "MIN_ANCHOR_WORDS",
    "MIN_SHARED_WORDS",
    "ArticleKind",
    "Candidate",
    "Candidates",
    "InternalLink",
    "LinkCheck",
    "LinkKind",
    "LinkPlacement",
    "LinkReport",
    "LinkReview",
    "LinkSuggestion",
    "LinkSuggestions",
    "Notice",
    "apply_links",
    "check_links",
    "check_suggestions",
    "markdown_blocks",
    "path_key",
    "place_links",
    "select_candidates",
    "topic_words",
]

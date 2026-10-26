"""Meta title, meta description, slug: chuẩn hóa, đếm độ dài, kiểm (không cần AI).

Thiết kế: ``docs/team/reports/T-033-tho-may.md`` mục 5. Mọi hàm ở đây là hàm thuần, chạy
tuyến tính theo độ dài chữ (và theo số bài khi kiểm trùng).

- Chữ Việt có thể đến ở dạng tổ hợp (NFD, hay gặp khi dán trên Mac): "ữ" thành 3 ký tự. Luôn
  chuẩn hóa NFC trước khi đếm và trước khi gửi đi (``normalize_meta``).
- SiteSEO hiểu ``%%tên%%`` là biến, nên chữ của phần mềm không được chứa ``%%``.
- Từ khóa chính có thể chứa chữ về giá hay cụm nên tránh («giá sửa cửa sắt», «sửa cửa uy tín»):
  bộ dò giá và cụm nên tránh bỏ qua chỗ khớp nằm trọn trong từ khóa, chỗ vắt qua mép từ khóa vẫn
  tính (LC-T040-1).
"""

from __future__ import annotations

import functools
import re
import unicodedata
from bisect import bisect_right
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING
from urllib.parse import unquote

from seo_app.content.rules import IGNORABLE_NOT_CF, find_banned
from seo_app.sanitize import clean_ai_text, strip_tags
from seo_app.text import remove_accents, slugify

if TYPE_CHECKING:  # chỉ để ghi kiểu: storage → drafts → content.workflow → meta (vòng nhập)
    from seo_app.storage.site_index import SiteIndex


class Level(StrEnum):
    """Mức kết quả kiểm: Nên (ổn), Cảnh báo (vẫn dùng được), Chặn (không được dùng)."""

    GOOD = "nen"
    WARN = "canh_bao"
    BLOCK = "chan"


_SEVERITY = {Level.GOOD: 0, Level.WARN: 1, Level.BLOCK: 2}


def worst(levels) -> Level:
    """Mức nặng nhất trong các mức (không có mức nào thì là Nên)."""
    return max(levels, key=_SEVERITY.__getitem__, default=Level.GOOD)


@dataclass(frozen=True)
class FieldCheck:
    """Kết quả kiểm một trường. ``value`` là chữ đã chuẩn hóa (đem đi dùng), ``length`` đếm
    trên ``value``. ``messages``: câu giải thích tiếng Việt, mỗi câu một vấn đề."""

    field: str  # "title" | "description" | "slug"
    value: str
    length: int
    level: Level
    messages: tuple[str, ...]


@dataclass(frozen=True)
class Limits:
    """Ngưỡng độ dài (ký tự NFC): Nên trong [good_min, good_max]; Cảnh báo khi dưới warn_min
    hoặc trên warn_max. Khoảng giữa (ví dụ title 30–49) vẫn dùng được, có lời nhắc."""

    good_min: int
    good_max: int
    warn_min: int
    warn_max: int


# Bảng ngưỡng mục 5.1 (khớp YC-401 và demo đã duyệt).
TITLE_LIMITS = Limits(good_min=50, good_max=60, warn_min=30, warn_max=65)
DESCRIPTION_LIMITS = Limits(good_min=120, good_max=155, warn_min=70, warn_max=160)
SLUG_MAX_LENGTH = 60
SLUG_GOOD_WORDS = (3, 7)

_FIELD_NAMES = {"title": "Meta title", "description": "Meta description", "slug": "Slug"}

# ------------------------------------------------------------------ chuẩn hóa, đếm

# Ký tự bị bỏ khỏi chữ meta (LC-T036-1): Cf (vô hình: U+200B, BOM, gạch nối mềm…), Cc (điều khiển:
# NUL, ESC, DEL…), Cs (surrogate lẻ, không ghi được ra UTF-8), Co (ký tự riêng), Cn (ký tự chưa
# gán). Khoảng trắng loại Cc (tab, xuống dòng, U+001C–U+001F, U+0085) thì giữ để gộp thành dấu cách.
_DROPPED_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn"})


def normalize_meta(text: str) -> str:
    """Chữ meta để đếm và gửi đi: NFC, bỏ ký tự vô hình và ký tự lạ, mọi khoảng trắng (kể cả
    xuống dòng, dấu cách không ngắt) gộp thành một dấu cách, bỏ khoảng trắng đầu cuối.

    Bỏ: Unicode loại Cf, Cc (trừ khoảng trắng), Cs, Co, Cn (``_DROPPED_CATEGORIES``) và các ký tự
    "mặc định bỏ qua" khác (``IGNORABLE_NOT_CF``), ở cả chữ AI lẫn chữ người dùng gõ (LC-T036-1).
    NFC chạy cả trước (để bỏ ký tự vô hình không tách chữ) lẫn sau (ghép lại chữ với dấu bị ký tự
    vô hình chen giữa).
    """
    text = unicodedata.normalize("NFC", text)
    text = "".join(
        ch for ch in text if ch.isspace() or unicodedata.category(ch) not in _DROPPED_CATEGORIES
    )
    text = IGNORABLE_NOT_CF.sub("", text)
    return " ".join(unicodedata.normalize("NFC", text).split())


def meta_length(text: str) -> int:
    """Số ký tự như Google thấy: đếm trên chữ đã chuẩn hóa (NFD dài gấp đôi khi đếm thô)."""
    return len(normalize_meta(text))


def has_html(text: str) -> bool:
    """Có thẻ HTML (hay "<" ngay trước chữ cái, có thể thành thẻ)."""
    return strip_tags(text) != text


def has_variable(text: str) -> bool:
    """Có ``%%`` (SiteSEO hiểu ``%%tên%%`` là biến)."""
    return "%%" in normalize_meta(text)


# ------------------------------------------------------------------ title, description


def _check_text(field: str, raw: str, limits: Limits) -> FieldCheck:
    name = _FIELD_NAMES[field]
    value = normalize_meta(raw)
    length = len(value)
    if not value:
        return FieldCheck(field, value, 0, Level.BLOCK, (f"{name} đang trống.",))
    blocks = []
    # Xét cả chữ gốc lẫn chữ đã chuẩn hóa: "<" + ký tự vô hình + "script>" chỉ thành thẻ thật
    # SAU khi bỏ ký tự vô hình, mà chữ gửi đi là ``value`` (SL-T036-1).
    if has_html(raw) or has_html(value):
        blocks.append(f"{name} có thẻ HTML (dấu < ngay trước chữ). Bỏ thẻ đi.")
    if "%%" in value:
        blocks.append(f"{name} có «%%»: plugin SiteSEO hiểu đó là biến. Bỏ «%%» đi.")
    if blocks:
        return FieldCheck(field, value, length, Level.BLOCK, tuple(blocks))
    good = f"nên {limits.good_min}–{limits.good_max} ký tự"
    if length < limits.warn_min:
        return FieldCheck(
            field, value, length, Level.WARN, (f"{name} quá ngắn: {length} ký tự, {good}.",)
        )
    if length > limits.warn_max:
        return FieldCheck(
            field,
            value,
            length,
            Level.WARN,
            (f"{name} quá dài: {length} ký tự, Google sẽ cắt bớt; {good}.",),
        )
    if length < limits.good_min:
        note = f"{name} hơi ngắn: {length} ký tự, {good}."
    elif length > limits.good_max:
        note = f"{name} hơi dài: {length} ký tự, {good}."
    else:
        note = f"{name} dài vừa: {length} ký tự."
    return FieldCheck(field, value, length, Level.GOOD, (note,))


def check_title(title: str, suffix: object = None) -> FieldCheck:
    """Kiểm meta title **sẽ dùng**: ``with_brand(title, suffix)``. ``suffix``: hậu tố thương hiệu
    đang dùng (như ``with_brand``; ``None`` là mặc định « | Pro-Metal», ``""`` là không gắn).

    - Ô sửa title (chưa gắn hậu tố) được chấm như title gửi đi: còn chỗ thì tính cả hậu tố
      (SL-T041-2), câu báo ghi «tính cả đuôi thương hiệu». ``value``, ``length`` là của title đó.
      Muốn chấm đúng chữ đưa vào (không gắn gì): ``suffix=""``.
    - Title không có hậu tố vì không đủ chỗ (cộng hậu tố thì quá ``TITLE_LIMITS.good_max``, ví dụ
      49 ký tự với « | Pro-Metal») được ghi «dài vừa» thay vì «hơi ngắn» (SL-T040-1).
    - Chữ có thẻ HTML, ``%%``, trống: Chặn, xét trên chữ đưa vào.
    """
    given = _check_text("title", title, TITLE_LIMITS)
    if given.level is Level.BLOCK:
        return given
    brand = resolve_brand_suffix(suffix)
    final = with_brand(given.value, suffix)
    check = given if final == given.value else _check_text("title", final, TITLE_LIMITS)
    if check.level is Level.BLOCK:
        return check
    if brand and strip_brand(final, suffix) != final:  # title dùng có hậu tố
        if final == given.value:
            return check
        # Hậu tố do phần mềm gắn (ô sửa chưa có): câu báo nói rõ độ dài đã tính cả hậu tố.
        notes = tuple(f"{message[:-1]} (tính cả đuôi thương hiệu)." for message in check.messages)
        return FieldCheck("title", check.value, check.length, check.level, notes)
    if (
        check.level is Level.GOOD
        and brand
        and check.length < TITLE_LIMITS.good_min
        and check.length + len(brand) > TITLE_LIMITS.good_max
    ):
        note = f"Meta title dài vừa: {check.length} ký tự (không còn chỗ gắn đuôi thương hiệu)."
        return FieldCheck("title", check.value, check.length, Level.GOOD, (note,))
    return check


def check_description(description: str) -> FieldCheck:
    return _check_text("description", description, DESCRIPTION_LIMITS)


# ------------------------------------------------------------------ hậu tố thương hiệu

# Câu hỏi 3 cho chủ dự án (chưa trả lời): tiêu đề SEO có gắn tên thương hiệu ở cuối không.
# Mặc định theo phương án đề xuất A: thêm " | Pro-Metal" khi tiêu đề còn chỗ. Chủ dự án chọn B
# (không gắn) thì đổi hằng số này thành "" (hoặc truyền ``suffix=""``), không phải sửa chỗ khác.
BRAND_SUFFIX = " | Pro-Metal"
BRAND_SUFFIX_MAX_LENGTH = 25
# Các dạng hậu tố đang có trên site hoặc AI hay viết: " | Pro Metal", " - Pro-Metal", "– ProMetal",
# "| Pro‑Metal" (gạch nối không ngắt U+2011), "| Pro-Metal." (SL-T036-4).
_HYPHENS = "\\-\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
_BRAND_TAIL = re.compile(
    rf"\s*[|¦:·•/{_HYPHENS}]\s*pro[\s{_HYPHENS}]?metal\s*\.?\s*$", re.IGNORECASE
)
# Số lần gỡ hậu tố lặp ở cuối ("… | Pro-Metal | Pro Metal", SL-T036-2). Có giới hạn để chữ cố
# tình lặp hàng nghìn lần không làm chậm theo bình phương.
_MAX_BRAND_STRIPS = 5


def resolve_brand_suffix(value: object = None) -> str:
    """Hậu tố dùng thật. Không có cấu hình (``None``) hoặc cấu hình sai (không phải chữ, có thẻ,
    có ``%%``, dài quá ``BRAND_SUFFIX_MAX_LENGTH``) thì dùng ``BRAND_SUFFIX``, không báo lỗi.
    Chữ rỗng (kể cả chỉ có khoảng trắng hay ký tự vô hình, SL-T036-4) là chủ ý "không gắn
    thương hiệu"."""
    if not isinstance(value, str):
        return BRAND_SUFFIX
    if not normalize_meta(value):
        return ""
    if has_html(value) or "%%" in value:
        return BRAND_SUFFIX
    suffix = " " + normalize_meta(value)
    return suffix if len(suffix) <= BRAND_SUFFIX_MAX_LENGTH else BRAND_SUFFIX


def _strip_custom(text: str, brand: str) -> tuple[str, bool]:
    """Bỏ ``brand`` (hậu tố đang dùng, đã bỏ dấu cách đầu) nếu nó đứng trọn ở cuối ``text``."""
    if not brand or len(text) < len(brand) or text[-len(brand) :].lower() != brand.lower():
        return text, False
    before = text[: -len(brand)]
    if before and before[-1].isalnum() and brand[0].isalnum():
        return text, False  # "xPro-Metal": không phải hậu tố riêng
    return before.rstrip(), True


def strip_brand(title: str, suffix: object = None) -> str:
    """Bỏ hậu tố thương hiệu ở cuối: mọi dạng " | Pro Metal", " - Pro-Metal"…, và cả hậu tố
    đang dùng (``suffix``, mặc định ``BRAND_SUFFIX``) khi nó khác dạng Pro-Metal (SL-T036-3).
    Hậu tố lặp nhiều lần ở cuối cũng bỏ hết (tối đa ``_MAX_BRAND_STRIPS`` lần)."""
    text = normalize_meta(title)
    brand = resolve_brand_suffix(suffix).strip()
    for _ in range(_MAX_BRAND_STRIPS):
        stripped = _BRAND_TAIL.sub("", text).strip()
        stripped, _ = _strip_custom(stripped, brand)
        if stripped == text:
            break
        text = stripped
    return text


def with_brand(title: str, suffix: object = None, max_length: int = TITLE_LIMITS.good_max) -> str:
    """Tiêu đề kèm hậu tố thương hiệu nếu còn chỗ (tổng không quá ``max_length`` ký tự).

    Hậu tố cũ ở cuối (mọi dạng, kể cả hậu tố đang dùng) được bỏ trước để chỉ còn một dạng
    thống nhất. Không đủ chỗ hoặc hậu tố rỗng thì trả tiêu đề không hậu tố.
    """
    base = strip_brand(title, suffix)
    brand = resolve_brand_suffix(suffix)
    if base and brand and len(base) + len(brand) <= max_length:
        return base + brand
    return base


# ------------------------------------------------------------------ slug

# Từ nối đứng cuối slug không mang nghĩa ("cach-chon-cua-cho" → "cach-chon-cua"). Xét trên
# chữ CÓ DẤU, vì sau khi bỏ dấu "của" và "cửa" đều thành "cua".
SLUG_TRAILING_STOPWORDS = frozenset(
    {
        "và", "với", "cho", "của", "là", "ở", "tại", "thế", "nào", "gì", "như", "hay",
        "hoặc", "để", "khi", "thì", "mà", "nhưng", "các", "những", "một", "từ", "đến",
        "trong", "về", "bằng", "có", "không", "nên", "sao", "này", "đó", "the", "a", "an",
        "of", "and", "for", "to", "in", "on",
    }
)  # fmt: skip
_WORD = re.compile(r"[^\W_]+")
_SLUG_CHARS = re.compile(r"[a-z0-9-]+")
_SLUG_SHAPE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_NO_LIMIT = 10**9  # slug người dùng đưa vào: không cắt


def make_slug(text: str, given: str | None = None, max_length: int = SLUG_MAX_LENGTH) -> str:
    """Slug không dấu cho bài.

    ``given`` (slug người dùng gõ hoặc slug trong phiếu giao bài) luôn thắng slug tự sinh: chỉ
    được chuyển về dạng không dấu (``slugify``), không cắt từ, để giữ ý người dùng; dài quá thì
    ``check_slug`` cảnh báo. Slug tự sinh từ ``text`` (thường là từ khóa hoặc tiêu đề) cắt ở
    ranh giới từ trong ``max_length`` ký tự, rồi bỏ từ nối vô nghĩa ở cuối.
    """
    if given is not None and given.strip():
        return slugify(normalize_meta(given), max_length=_NO_LIMIT)
    pieces: list[tuple[str, str]] = []  # (từ có dấu, phần slug)
    length = 0
    for word in _WORD.findall(normalize_meta(text).lower()):
        piece = slugify(word, max_length=max_length)
        if not piece:
            continue
        added = len(piece) + (1 if pieces else 0)
        if length + added > max_length:
            break
        pieces.append((word, piece))
        length += added
    trimmed = list(pieces)
    while trimmed and trimmed[-1][0] in SLUG_TRAILING_STOPWORDS:
        trimmed.pop()
    chosen = trimmed or pieces  # toàn từ nối: giữ nguyên còn hơn slug rỗng
    if not chosen:
        return slugify(normalize_meta(text), max_length=max_length)
    return "-".join(piece for _, piece in chosen)


def check_slug(slug: str) -> FieldCheck:
    value = slug.strip()
    length = len(value)
    if not value:
        return FieldCheck("slug", value, 0, Level.BLOCK, ("Slug đang trống.",))
    if not _SLUG_CHARS.fullmatch(value):
        return FieldCheck(
            "slug",
            value,
            length,
            Level.BLOCK,
            ("Slug chỉ được có chữ thường không dấu (a-z), chữ số và dấu gạch ngang «-».",),
        )
    warns = []
    if not _SLUG_SHAPE.fullmatch(value):
        warns.append("Slug có «-» ở đầu, ở cuối hoặc hai dấu «-» liền nhau.")
    words = len([w for w in value.split("-") if w])
    if length > SLUG_MAX_LENGTH:
        warns.append(f"Slug dài {length} ký tự, nên không quá {SLUG_MAX_LENGTH}.")
    low, high = SLUG_GOOD_WORDS
    if words > high:
        warns.append(f"Slug có {words} từ, nên {low}–{high} từ.")
    if warns:
        return FieldCheck("slug", value, length, Level.WARN, tuple(warns))
    note = f"Slug có {words} từ, nên {low}–{high} từ." if words < low else "Slug gọn, đúng chuẩn."
    return FieldCheck("slug", value, length, Level.GOOD, (note,))


# ------------------------------------------------------------------ kiểm trùng với bài khác


@dataclass(frozen=True)
class SitePost:
    """Một bài trên site để so trùng (T-037 sẽ đưa dữ liệu thật từ cache vào).

    Chữ đến từ site là dữ liệu chưa tin cậy: giao diện phải escape khi hiện (U1).
    """

    id: int
    title: str = ""
    meta_title: str = ""
    meta_description: str = ""
    slug: str = ""


# Tỉ lệ từ chung (hệ số Dice trên tập từ không dấu) từ mức này trở lên là "giống nhiều".
SIMILARITY_WARN = 0.8
# Số tên bài bị trùng/giống nêu trong một câu báo (còn lại ghi "và N bài khác").
_MAX_NAMED = 3
_PUNCTUATION = re.compile(r"[^\w\s]|_")


def compare_key(text: str) -> str:
    """Chữ để so trùng: chuẩn hóa như ``normalize_meta``, bỏ hậu tố thương hiệu, chữ thường,
    bỏ dấu câu, gộp khoảng trắng. Giữ dấu tiếng Việt ("cửa" khác "của")."""
    base = strip_brand(text).lower()
    return " ".join(_PUNCTUATION.sub(" ", base).split())


def _word_set(key: str) -> frozenset[str]:
    return frozenset(remove_accents(key).split())


def similarity(a: frozenset[str], b: frozenset[str]) -> float:
    """Hệ số Dice: 2·|chung| / (|a| + |b|). 1 là cùng tập từ, 0 là không chung từ nào."""
    if not a or not b:
        return 0.0
    return 2 * len(a & b) / (len(a) + len(b))


def _names(posts: list[SitePost]) -> str:
    shown = [f"«{normalize_meta(p.title) or f'bài #{p.id}'}»" for p in posts[:_MAX_NAMED]]
    more = len(posts) - _MAX_NAMED
    return ", ".join(shown) + (f" và {more} bài khác" if more > 0 else "")


def _duplicate_check(
    field: str, value: str, candidates: list[tuple[SitePost, list[str]]]
) -> FieldCheck:
    """So ``value`` với các chữ của từng bài (``candidates``: bài, các chữ của bài đó)."""
    name = _FIELD_NAMES[field]
    shown = normalize_meta(value)
    key = compare_key(value)
    if not key:
        return FieldCheck(field, shown, len(shown), Level.GOOD, ())
    words = _word_set(key)
    same: list[SitePost] = []
    alike: list[SitePost] = []
    for post, texts in candidates:
        keys = {compare_key(t) for t in texts if t}
        keys.discard("")
        if key in keys:
            same.append(post)
        elif any(similarity(words, _word_set(k)) >= SIMILARITY_WARN for k in keys):
            alike.append(post)
    if same:
        return FieldCheck(
            field,
            shown,
            len(shown),
            Level.BLOCK,
            (f"{name} trùng hệt bài {_names(same)}. Hai trang giống nhau tranh nhau trên Google.",),
        )
    if alike:
        return FieldCheck(
            field,
            shown,
            len(shown),
            Level.WARN,
            (f"{name} rất giống bài {_names(alike)}. Nên viết khác đi cho rõ bài này nói gì.",),
        )
    return FieldCheck(field, shown, len(shown), Level.GOOD, ())


def _others(posts, current_id: int | None) -> list[SitePost]:
    return [p for p in posts if current_id is None or p.id != current_id]


def check_title_duplicates(title: str, posts, current_id: int | None = None) -> FieldCheck:
    """So meta title với bài khác. Bài chưa có meta title thì SiteSEO dùng tiêu đề bài, nên so
    với cả tiêu đề bài lẫn meta title của từng bài. Bỏ qua bài ``current_id`` (bài đang sửa)."""
    return _duplicate_check(
        "title", title, [(p, [p.meta_title, p.title]) for p in _others(posts, current_id)]
    )


def check_description_duplicates(
    description: str, posts, current_id: int | None = None
) -> FieldCheck:
    """So meta description với meta description của bài khác (bài để trống thì bỏ qua)."""
    return _duplicate_check(
        "description",
        description,
        [(p, [p.meta_description]) for p in _others(posts, current_id)],
    )


def _slug_key(slug: str) -> str:
    return unquote(slug).strip().strip("/").lower()


def check_slug_duplicates(slug: str, posts, current_id: int | None = None) -> FieldCheck:
    """Slug trùng bài khác thì WordPress tự thêm "-2" (hai trang cùng nhắm một từ khóa): Chặn."""
    value = slug.strip()
    key = _slug_key(value)
    same = [p for p in _others(posts, current_id) if key and _slug_key(p.slug) == key]
    if same:
        return FieldCheck(
            "slug",
            value,
            len(value),
            Level.BLOCK,
            (f"Slug trùng bài {_names(same)}. Đổi slug khác.",),
        )
    return FieldCheck("slug", value, len(value), Level.GOOD, ())


# ------------------------------------------------------------------ kiểm gợi ý của AI (A2)

# Số gợi ý tối đa giữ lại (khuôn trả về: 3 title, 2 description).
MAX_TITLE_SUGGESTIONS = 3
MAX_DESCRIPTION_SUGGESTIONS = 2

# Link hay địa chỉ: giao thức ("https:", "javascript:", "x://"), "www.", link Markdown, email,
# tên miền trần ("suachuacuasat.com"). Xét trên chữ đã NFKC ("ｗｗｗ．" cũng là "www.").
_LINK = re.compile(
    r"[a-z][a-z0-9+.\-]*://|\b(?:https?|javascript|data|vbscript|file|mailto|tel|zalo):"
    r"|www\.|\]\s*[(\[]|@[\w-]+\.|\b[\w-]+\.(?:com|vn|net|org|info|io|me|biz|xyz|co|site|link)\b",
    re.IGNORECASE,
)
# Nêu giá dưới mọi dạng (BAN-GIAO.md 7.4: không nói giá, kể cả rẻ/đắt; "báo giá qua Zalo" thì
# được). Xét trên chữ NFKC ("５００ｋ" thành "500k"), chữ thường, đã bỏ từ khóa chính (từ khóa có
# thể chứa chữ "giá"). Gồm: số + đơn vị tiền ("200.000đ", "500k", "1tr5", "500 đô"), chữ số viết
# bằng chữ + đơn vị ("năm trăm nghìn", "hai triệu đồng", "vài trăm ngàn"), ký hiệu tiền, và các
# cụm nói về giá. Đơn vị có loại trừ những từ ghép hay gặp không phải tiền ("đồng hồ", "đô thị",
# "tỉ lệ") để không bỏ oan gợi ý (SL-T036-5).
_MONEY_UNIT = (
    r"(?:đồng(?!\s+(?:hồ|bộ|thời|loạt|đều|màu|nghiệp|ý|nát|tâm))|vnđ|vnd|đô(?:\s+la)?(?!\s+thị)"
    r"|đ|k|nghìn|ngàn|triệu|tr|tỷ(?!\s+lệ)|tỉ(?!\s+lệ)|usd|xu(?!\s+hướng))"
)  # «7 xu hướng» không phải giá: chỉ loại trừ đúng «xu hướng» (SL-T036-10)
_NUMBER_WORD = (
    r"(?:một|hai|ba|bốn|tư|năm|lăm|sáu|bảy|bẩy|tám|chín|mười|mươi|trăm|chục|vài|mấy|rưỡi|nửa)"
)
_PRICE = re.compile(
    r"\d[\d.,]*\s*" + _MONEY_UNIT + r"\d*(?!\w)"
    r"|\b" + _NUMBER_WORD + r"\s+" + _MONEY_UNIT + r"(?!\w)"
    r"|\b(?:nghìn|ngàn|triệu|tỷ|tỉ)\s+đồng\b"
    r"|[$€₫¥£]"
    r"|\b(?:giá|chi phí)\s+(?:rẻ|tốt|chỉ|từ|gốc|sỉ|ưu đãi|cạnh tranh|hợp lý|phải chăng|thấp"
    r"|mềm|bình dân|bao nhiêu)\b"
    r"|\b(?:rẻ|đắt|bảng giá|giảm giá|khuyến mãi|miễn phí|ưu đãi|trọn gói)\b"
)


def _plain_words(text: str) -> str:
    """Chữ không dấu, chữ thường, chỉ còn từ, bọc dấu cách hai đầu (để so trọn từ)."""
    words = _WORD.findall(remove_accents(normalize_meta(text)).lower())
    return " " + " ".join(words) + " "


def has_keyword(text: str, keyword: str) -> bool:
    """Có từ khóa chính (trọn từ, không phân biệt hoa thường; so bản không dấu nên AI viết
    thiếu dấu, sai dấu vẫn được nhận). Từ khóa rỗng thì coi như có."""
    key = _plain_words(keyword)
    return not key.strip() or key in _plain_words(text)


# Tên miền trần có đuôi bất kỳ ("bit.ly/abc", "pro-metal.shop", "abc.asia", SL-T036-6). Phân
# biệt hoa thường (đuôi chữ thường) để "TP.HCM" không bị coi là tên miền; nhãn phải có chữ cái
# để "1.2mm" không bị bắt; chữ ngay sau đuôi không được là chữ cái (kể cả chữ có dấu), để câu
# thiếu dấu cách kiểu "xong.tiếp" không bị bắt.
_BARE_DOMAIN = re.compile(
    r"(?<![\w.])(?=[A-Za-z0-9-]*[A-Za-z])[A-Za-z0-9-]+\.(?!hcm(?![\w-]))[a-z]{2,12}(?![\w-])"
)
# Mã ký tự HTML ("&amp;", "&#38;", "&#x26;"): SiteSEO/WordPress có thể in nguyên văn (SL-T036-7).
_ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);", re.IGNORECASE)


# Chữ dài hơn mức này (sau chuẩn hóa) thì ``has_link``, ``mentions_price`` không dò mà coi như CÓ
# (SL-T036-12): các biểu thức dò quay lui nên chạy bậc hai với chuỗi rất dài, còn meta và anchor
# không bao giờ dài thế (title tối đa 90, description 160, anchor 100 ký tự). Coi như có là hướng
# an toàn: gợi ý bị bỏ, giao diện gọi với chữ người dùng dán dài bao nhiêu cũng không bị treo.
MAX_SCAN_CHARS = 1000


def _scan_text(text: str) -> str | None:
    """Chữ để dò (NFKC của chữ đã chuẩn hóa: "ｗｗｗ．" là "www."), hoặc ``None`` nếu dài quá
    ``MAX_SCAN_CHARS`` (NFKC có thể làm chữ dài ra, nên đo cả sau NFKC). Chạy tuyến tính."""
    value = normalize_meta(text)
    if len(value) > MAX_SCAN_CHARS:
        return None
    folded = unicodedata.normalize("NFKC", value)
    return folded if len(folded) <= MAX_SCAN_CHARS else None


def has_link(text: str) -> bool:
    visible = _scan_text(text)
    if visible is None:
        return True
    return _LINK.search(visible) is not None or _BARE_DOMAIN.search(visible) is not None


@functools.lru_cache(maxsize=4096)
def _fold_char(ch: str) -> str:
    """Một ký tự bỏ dấu («ử» → «u», «đ» → «d»), luôn đúng **một** ký tự để vị trí không đổi."""
    if ch in "đĐ":
        return "d" if ch == "đ" else "D"
    base = "".join(c for c in unicodedata.normalize("NFD", ch) if not unicodedata.combining(c))
    return base if len(base) == 1 else ch


def _fold(text: str) -> str:
    return "".join(_fold_char(ch) for ch in text)


class _KeywordSpans:
    """Các lần xuất hiện của từ khóa chính trong chữ đang dò (cùng cách chuẩn hóa).

    So **không dấu** (như ``has_keyword``): từ khóa gõ không dấu («sua cua uy tin hcm», như cột
    từ khóa trong file kế hoạch) vẫn che được «Sửa cửa uy tín HCM» trong câu (SL-T041-3). Bỏ dấu
    từng ký tự giữ nguyên độ dài nên vị trí khớp trên chữ có dấu không đổi."""

    def __init__(self, text: str, keyword: str) -> None:
        text, keyword = _fold(text), _fold(keyword)
        self._length = len(keyword)
        self._starts: list[int] = []
        start = text.find(keyword) if keyword else -1
        while start != -1:
            self._starts.append(start)
            start = text.find(keyword, start + 1)

    def covers(self, start: int, end: int) -> bool:
        """Đoạn [``start``, ``end``) nằm trọn trong một lần xuất hiện của từ khóa. Các lần xuất
        hiện dài bằng nhau nên chỉ cần xét lần bắt đầu muộn nhất mà không sau ``start``."""
        k = bisect_right(self._starts, start) - 1
        return k >= 0 and end <= self._starts[k] + self._length


def mentions_price(text: str, keyword: str = "") -> bool:
    """Có nói về giá (``_PRICE``), không tính chỗ nằm trọn trong từ khóa chính.

    Không xóa từ khóa khỏi câu rồi mới dò (LC-T040-1): như vậy chỗ nói giá vắt qua mép từ khóa
    («làm cổng sắt báo giá» + «… báo giá tốt») mất theo. Dò ở **mọi vị trí** của câu, chỉ bỏ qua
    chỗ khớp nằm trọn trong một lần xuất hiện của từ khóa. Chữ dài quá ``MAX_SCAN_CHARS``: coi
    như có (SL-T036-12).
    """
    folded = _scan_text(text)
    if folded is None:
        return True
    lowered = folded.lower()
    keyword_scan = _scan_text(keyword) if isinstance(keyword, str) else None
    spans = _KeywordSpans(lowered, (keyword_scan or "").lower())
    for pos in range(len(lowered)):
        found = _PRICE.match(lowered, pos)
        if found is not None and not spans.covers(*found.span()):
            return True
    return False


def _avoid_pattern(phrase: str) -> re.Pattern[str] | None:
    """Cụm nên tránh đứng trọn từ (như ``find_banned``): chỉ đòi ranh giới ở đầu (cuối) khi cụm
    bắt đầu (kết thúc) bằng chữ cái/chữ số, nên «100%», «24/7» vẫn khớp."""
    folded = _scan_text(phrase) if isinstance(phrase, str) else None
    if not folded:
        return None
    words = folded.lower()
    before = r"(?<!\w)" if re.match(r"\w", words) else ""
    after = r"(?!\w)" if re.search(r"\w$", words) else ""
    return re.compile(before + re.escape(words) + after)


def find_avoided(text: str, phrases: Iterable[str], keyword: str = "") -> list[str]:
    """Các cụm nên tránh (``[meta].avoid`` của ``config/content.toml``) có trong ``text``.

    So trên chữ đã chuẩn hóa, NFKC, chữ thường. Như ``mentions_price``: chỗ khớp nằm trọn trong
    từ khóa chính thì bỏ qua (từ khóa «sửa cửa uy tín hcm» không làm mọi gợi ý bị bỏ), chỗ vắt
    qua mép từ khóa vẫn tính (LC-T040-1, đề xuất 2 Soi Lỗi T-040). Chữ dài quá
    ``MAX_SCAN_CHARS``: coi như có hết.
    """
    patterns = [(p, pattern) for p in phrases if (pattern := _avoid_pattern(p)) is not None]
    folded = _scan_text(text)
    if folded is None:
        return [p for p, _ in patterns]
    lowered = folded.lower()
    keyword_scan = _scan_text(keyword) if isinstance(keyword, str) else None
    spans = _KeywordSpans(lowered, (keyword_scan or "").lower())
    return [
        phrase
        for phrase, pattern in patterns
        if any(not spans.covers(*m.span()) for m in pattern.finditer(lowered))
    ]


def _ai_text(raw: object, keyword: str, banned, max_length: int, avoid=()) -> str | None:
    """Kiểm chung cho một gợi ý: trả chữ đã chuẩn hóa, hoặc None nếu phải bỏ.

    Gợi ý dài quá ``max_length`` bị bỏ NGAY sau khi chuẩn hóa (bước tuyến tính), trước mọi
    biểu thức soát link/giá: các biểu thức đó quay lui nên chậm theo bình phương với chuỗi dài
    không có dấu cách mà AI bị dụ trả về (SL-T036-9).
    """
    if not isinstance(raw, str) or has_html(raw):
        return None
    value = normalize_meta(raw)
    if not value or len(value) > max_length:
        return None
    folded = unicodedata.normalize("NFKC", value)  # "％％" toàn khổ cũng là "%%" (SL-T036-7)
    if "%%" in folded or _ENTITY.search(folded) or has_link(value):
        return None
    if find_banned(value, tuple(banned)) or find_avoided(value, avoid, keyword):
        return None
    if mentions_price(value, keyword):
        return None
    return value


def _final(value: str, check: FieldCheck, limits: Limits) -> str | None:
    """Gợi ý cuối: không bị Chặn, độ dài trong ngưỡng Cảnh báo, lọc ``clean_ai_text`` (U1)
    không đổi chữ (chữ được đếm chính là chữ được gửi đi), và client WordPress ghi được lên
    SiteSEO (``seo_write_problem``: shortcode, «<» liền ký tự… bị bỏ, SL-T041-1)."""
    if check.level is Level.BLOCK or not limits.warn_min <= check.length <= limits.warn_max:
        return None
    cleaned = " ".join(clean_ai_text(value).split())
    if cleaned != value or seo_write_problem("Gợi ý", value):
        return None
    return value


def _dedupe(values, limit: int) -> list[str]:
    seen: set[str] = set()
    out = []
    for value in values:
        key = compare_key(value)
        if value and key not in seen:
            seen.add(key)
            out.append(value)
    return out[:limit]


def accept_ai_title(
    raw: object, keyword: str, banned=(), suffix: object = None, avoid=()
) -> str | None:
    """Một meta title AI gợi ý, đã kiểm và gắn hậu tố thương hiệu; None nếu phải bỏ.

    ``banned``: cụm cấm (``[voice].banned``); ``avoid``: cụm nên tránh trong meta
    (``[meta].avoid``, không tính chỗ nằm trọn trong từ khóa chính)."""
    # AI có thể tự gắn hậu tố cũ (bỏ đi rồi gắn lại), nên cho thêm chỗ cho hậu tố.
    value = _ai_text(raw, keyword, banned, TITLE_LIMITS.warn_max + BRAND_SUFFIX_MAX_LENGTH, avoid)
    if value is None or not has_keyword(strip_brand(value), keyword):
        return None
    titled = with_brand(value, suffix)
    return _final(titled, check_title(titled, suffix), TITLE_LIMITS)


def accept_ai_description(raw: object, keyword: str, banned=(), avoid=()) -> str | None:
    """Một meta description AI gợi ý, đã kiểm; None nếu phải bỏ (``avoid`` như title)."""
    value = _ai_text(raw, keyword, banned, DESCRIPTION_LIMITS.warn_max, avoid)
    if value is None or not has_keyword(value, keyword):
        return None
    return _final(value, check_description(value), DESCRIPTION_LIMITS)


def filter_ai_titles(raws, keyword: str, banned=(), suffix: object = None, avoid=()) -> list[str]:
    accepted = (accept_ai_title(r, keyword, banned, suffix, avoid) for r in raws)
    return _dedupe((a for a in accepted if a), MAX_TITLE_SUGGESTIONS)


def filter_ai_descriptions(raws, keyword: str, banned=(), avoid=()) -> list[str]:
    accepted = (accept_ai_description(r, keyword, banned, avoid) for r in raws)
    return _dedupe((a for a in accepted if a), MAX_DESCRIPTION_SUGGESTIONS)


# ------------------------------------------------------------------ dùng ở bước SEO (T-041)


def site_posts(index: SiteIndex | None) -> list[SitePost]:
    """Bài/trang đã đăng (``SiteIndex`` của ``seo_app.storage.site_index``) → ``SitePost`` để kiểm
    trùng title, description, slug. Chưa có danh sách (chưa kết nối WordPress): danh sách rỗng,
    các hàm kiểm trùng trả Nên. Chữ lấy từ site là dữ liệu chưa tin cậy (U1)."""
    if index is None:
        return []
    return [
        SitePost(
            id=item.id,
            title=item.title,
            meta_title=item.meta_title,
            meta_description=item.meta_desc,
            slug=item.slug,
        )
        for item in index.items
    ]


def seo_write_problem(label: str, text: str) -> str:
    """Câu lý do client WordPress (``set_seo_meta``) sẽ **từ chối** ghi ``text`` vào SiteSEO; chuỗi
    rỗng nếu ghi được. Dùng chính bộ kiểm của client (``client._seo_text``: thẻ HTML, mã ký tự HTML
    kể cả thiếu «;», ``%%``, dạng shortcode WordPress, «<» liền ký tự khác, ký tự điều khiển) để
    đường chép tay, gợi ý AI và đường ghi qua phần mềm luôn giống nhau (SL-T041-1). Câu lý do là chữ
    cố định của client, không chép ``text``. Không xét độ dài (bộ kiểm meta lo)."""
    # Nhập muộn: client nhập muộn module này trong ``_seo_text`` (tránh vòng nhập lúc khởi động).
    from seo_app.wordpress.client import WordPressError, _seo_text

    try:
        _seo_text(label, text, _NO_LIMIT)
    except WordPressError as exc:
        return str(exc)
    return ""


@dataclass(frozen=True)
class SiteSeoCopy:
    """Chữ để chép, dán tay vào hộp SiteSEO của bài nháp (khi chưa bật ghi SEO lên site).

    ``title`` đã gắn hậu tố thương hiệu (``with_brand``), ``description`` và ``slug`` đã chuẩn
    hóa. Trường bị Chặn (trống, có thẻ HTML, có ``%%``, slug sai ký tự, hoặc chữ mà client WordPress
    từ chối ghi: shortcode, «<» liền ký tự, mã ký tự HTML) là ``None``: giao diện không cho chép,
    hiện ``checks`` (câu báo chữ thuần) để người dùng sửa.
    """

    title: str | None
    description: str | None
    slug: str | None
    checks: tuple[FieldCheck, ...]


def _writable(check: FieldCheck, label: str) -> FieldCheck:
    """``check`` nâng lên Chặn nếu client WordPress từ chối ghi chữ đó (SL-T041-1)."""
    if check.level is Level.BLOCK:
        return check
    problem = seo_write_problem(label, check.value)
    if not problem:
        return check
    return FieldCheck(check.field, check.value, check.length, Level.BLOCK, (problem,))


def siteseo_copy(title: str, description: str, slug: str, *, suffix: object = None) -> SiteSeoCopy:
    """Title (kèm hậu tố), description, slug cuối cùng để chép sang SiteSEO."""
    title_check = _writable(check_title(title, suffix), "Meta title")
    description_check = _writable(check_description(description), "Meta description")
    slug_check = check_slug(slug)
    checks = (title_check, description_check, slug_check)
    title_value, description_value, slug_value = (
        None if check.level is Level.BLOCK else check.value for check in checks
    )
    return SiteSeoCopy(title_value, description_value, slug_value, checks)

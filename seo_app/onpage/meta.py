"""Meta title, meta description, slug: chuẩn hóa, đếm độ dài, kiểm (không cần AI).

Thiết kế: ``docs/team/reports/T-033-tho-may.md`` mục 5. Mọi hàm ở đây là hàm thuần, chạy
tuyến tính theo độ dài chữ (và theo số bài khi kiểm trùng).

- Chữ Việt có thể đến ở dạng tổ hợp (NFD, hay gặp khi dán trên Mac): "ữ" thành 3 ký tự. Luôn
  chuẩn hóa NFC trước khi đếm và trước khi gửi đi (``normalize_meta``).
- SiteSEO hiểu ``%%tên%%`` là biến, nên chữ của phần mềm không được chứa ``%%``.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from seo_app.content.rules import IGNORABLE_NOT_CF
from seo_app.sanitize import strip_tags
from seo_app.text import slugify


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


def normalize_meta(text: str) -> str:
    """Chữ meta để đếm và gửi đi: NFC, bỏ ký tự vô hình, mọi khoảng trắng (kể cả xuống dòng,
    dấu cách không ngắt) gộp thành một dấu cách, bỏ khoảng trắng đầu cuối.

    Ký tự vô hình: Unicode loại Cf (U+200B, BOM, gạch nối mềm…) và các ký tự "mặc định bỏ qua"
    khác (``IGNORABLE_NOT_CF``). NFC chạy cả trước (để bỏ ký tự vô hình không tách chữ) lẫn sau
    (ghép lại chữ với dấu bị ký tự vô hình chen giữa).
    """
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
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
    if has_html(raw):
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


def check_title(title: str) -> FieldCheck:
    return _check_text("title", title, TITLE_LIMITS)


def check_description(description: str) -> FieldCheck:
    return _check_text("description", description, DESCRIPTION_LIMITS)


# ------------------------------------------------------------------ hậu tố thương hiệu

# Câu hỏi 3 cho chủ dự án (chưa trả lời): tiêu đề SEO có gắn tên thương hiệu ở cuối không.
# Mặc định theo phương án đề xuất A: thêm " | Pro-Metal" khi tiêu đề còn chỗ. Chủ dự án chọn B
# (không gắn) thì đổi hằng số này thành "" (hoặc truyền ``suffix=""``), không phải sửa chỗ khác.
BRAND_SUFFIX = " | Pro-Metal"
BRAND_SUFFIX_MAX_LENGTH = 25
# Các dạng hậu tố đang có trên site hoặc AI hay viết: " | Pro Metal", " - Pro-Metal", "– ProMetal".
_BRAND_TAIL = re.compile(r"\s*[|\-–—:·•]\s*pro[\s\-]?metal\s*$", re.IGNORECASE)


def resolve_brand_suffix(value: object = None) -> str:
    """Hậu tố dùng thật. Không có cấu hình (``None``) hoặc cấu hình sai (không phải chữ, có thẻ,
    có ``%%``, dài quá ``BRAND_SUFFIX_MAX_LENGTH``) thì dùng ``BRAND_SUFFIX``, không báo lỗi.
    Chữ rỗng là chủ ý "không gắn thương hiệu"."""
    if not isinstance(value, str):
        return BRAND_SUFFIX
    if not value.strip():
        return ""
    if has_html(value) or "%%" in value:
        return BRAND_SUFFIX
    suffix = " " + normalize_meta(value)
    return suffix if len(suffix) <= BRAND_SUFFIX_MAX_LENGTH else BRAND_SUFFIX


def strip_brand(title: str) -> str:
    """Bỏ hậu tố thương hiệu ở cuối (mọi dạng " | Pro Metal", " - Pro-Metal"…)."""
    return _BRAND_TAIL.sub("", normalize_meta(title)).strip()


def with_brand(title: str, suffix: object = None, max_length: int = TITLE_LIMITS.good_max) -> str:
    """Tiêu đề kèm hậu tố thương hiệu nếu còn chỗ (tổng không quá ``max_length`` ký tự).

    Hậu tố cũ ở cuối (mọi dạng) được bỏ trước để chỉ còn một dạng thống nhất. Không đủ chỗ
    hoặc hậu tố rỗng thì trả tiêu đề không hậu tố.
    """
    base = strip_brand(title)
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

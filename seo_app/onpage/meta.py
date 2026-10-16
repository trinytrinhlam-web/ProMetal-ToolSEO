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
from urllib.parse import unquote

from seo_app.content.rules import IGNORABLE_NOT_CF, find_banned
from seo_app.sanitize import clean_ai_text, strip_tags
from seo_app.text import remove_accents, slugify


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
    r"|đ|k|nghìn|ngàn|triệu|tr|tỷ(?!\s+lệ)|tỉ(?!\s+lệ)|usd|xu)"
)
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


def has_link(text: str) -> bool:
    return _LINK.search(unicodedata.normalize("NFKC", normalize_meta(text))) is not None


def mentions_price(text: str, keyword: str = "") -> bool:
    lowered = unicodedata.normalize("NFKC", normalize_meta(text)).lower()
    kw = unicodedata.normalize("NFKC", normalize_meta(keyword)).lower()
    if kw:
        lowered = lowered.replace(kw, " ")
    return _PRICE.search(lowered) is not None


def _ai_text(raw: object, keyword: str, banned, max_length: int) -> str | None:
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
    if "%%" in value or has_link(value):
        return None
    if find_banned(value, tuple(banned)) or mentions_price(value, keyword):
        return None
    return value


def _final(value: str, check: FieldCheck, limits: Limits) -> str | None:
    """Gợi ý cuối: không bị Chặn, độ dài trong ngưỡng Cảnh báo, và lọc ``clean_ai_text`` (U1)
    không đổi chữ (chữ được đếm chính là chữ được gửi đi)."""
    if check.level is Level.BLOCK or not limits.warn_min <= check.length <= limits.warn_max:
        return None
    cleaned = " ".join(clean_ai_text(value).split())
    return cleaned if cleaned == value else None


def _dedupe(values, limit: int) -> list[str]:
    seen: set[str] = set()
    out = []
    for value in values:
        key = compare_key(value)
        if value and key not in seen:
            seen.add(key)
            out.append(value)
    return out[:limit]


def accept_ai_title(raw: object, keyword: str, banned=(), suffix: object = None) -> str | None:
    """Một meta title AI gợi ý, đã kiểm và gắn hậu tố thương hiệu; None nếu phải bỏ."""
    # AI có thể tự gắn hậu tố cũ (bỏ đi rồi gắn lại), nên cho thêm chỗ cho hậu tố.
    value = _ai_text(raw, keyword, banned, TITLE_LIMITS.warn_max + BRAND_SUFFIX_MAX_LENGTH)
    if value is None or not has_keyword(strip_brand(value), keyword):
        return None
    titled = with_brand(value, suffix)
    return _final(titled, check_title(titled), TITLE_LIMITS)


def accept_ai_description(raw: object, keyword: str, banned=()) -> str | None:
    """Một meta description AI gợi ý, đã kiểm; None nếu phải bỏ."""
    value = _ai_text(raw, keyword, banned, DESCRIPTION_LIMITS.warn_max)
    if value is None or not has_keyword(value, keyword):
        return None
    return _final(value, check_description(value), DESCRIPTION_LIMITS)


def filter_ai_titles(raws, keyword: str, banned=(), suffix: object = None) -> list[str]:
    accepted = (accept_ai_title(r, keyword, banned, suffix) for r in raws)
    return _dedupe((a for a in accepted if a), MAX_TITLE_SUGGESTIONS)


def filter_ai_descriptions(raws, keyword: str, banned=()) -> list[str]:
    accepted = (accept_ai_description(r, keyword, banned) for r in raws)
    return _dedupe((a for a in accepted if a), MAX_DESCRIPTION_SUGGESTIONS)

"""Khuôn một dòng kế hoạch (``PlanRow``) và bộ làm sạch chung (T-098).

Thiết kế: ``docs/team/reports/T-094-tho-may.md`` mục 1.3 (trường, kiểm) và 2.4 (cột của tab
«KeHoach» trên Google Sheets). Mọi dữ liệu kế hoạch (file tải lên, chữ dán, Google Sheets, cache,
kết quả AI) là dữ liệu **chưa tin cậy** và đi qua đúng một bộ làm sạch: dựng ``PlanRow``
(điều kiện Lá Chắn LC-T094-18). ``PlanRow`` tự làm sạch và tự kiểm khi tạo; sai thì báo
``ValueError`` (pydantic ``ValidationError``), không cắt ngầm.

Chữ trong ``PlanRow`` đã bỏ ký tự điều khiển, ký tự vô hình và ký tự đảo hướng chữ (U+202A–U+202E,
U+2066–U+2069) nhưng **chưa escape**: giao diện phải hiện bằng ô bảng, ``st.text`` hay
``escape_markdown`` (U1, LC-T094-3).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator

from seo_app.content.rules import IGNORABLE_NOT_CF
from seo_app.text import remove_accents, slugify

if TYPE_CHECKING:  # chỉ để ghi kiểu: onpage.links → storage → drafts → workflow (vòng nhập)
    from seo_app.onpage.links import ArticleKind

# Giới hạn dữ liệu kế hoạch (thiết kế T-094 mục 1.2, 2.4; LC-T094-18).
MAX_FILE_BYTES = 1_000_000  # file tải lên, kiểm theo byte trước khi giải mã
MAX_PASTE_CHARS = 20_000  # chữ dán, và chữ tự do gửi AI
MAX_ROWS = 1_000  # dòng dữ liệu (không tính dòng tiêu đề)
MAX_COLUMNS = 26
MAX_CELL_CHARS = 2_000
KEYWORD_MIN, KEYWORD_MAX = 2, 120
SECONDARY_MAX = 500
TITLE_MAX = 200
SLUG_MAX = 200
NOTES_MAX = MAX_CELL_CHARS
# Ngày kế hoạch hợp lý: số ngày kiểu Google Sheets hay ngày gõ tay ngoài khoảng này là gõ nhầm.
YEAR_MIN, YEAR_MAX = 2020, 2035
# Mã bài WordPress là số nguyên dương 32 bit (cột BIGINT UNSIGNED, nhưng site nhỏ không vượt).
MAX_POST_ID = 2_147_483_647

TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

# Nhãn cố định (đúng 3 nhãn ý định của giao diện demo). Ngòi Bút có thể chỉnh chữ ở T-103.
INTENTS = ("Tìm hiểu", "So sánh trước khi mua", "Mua hàng")
KIND_GUIDE = "Hướng dẫn"
KIND_SERVICE = "Dịch vụ"
KIND_AREA = "Khu vực"
KIND_PROJECT = "Công trình thực tế"
KIND_UPDATE_OLD = "Cập nhật bài cũ"  # chưa hỗ trợ ở Giai đoạn 5 (câu hỏi 6A)
KINDS = (KIND_GUIDE, KIND_SERVICE, KIND_AREA, KIND_PROJECT, KIND_UPDATE_OLD)
PRIORITIES = ("Cao", "Trung bình", "Thấp")
STATUS_NEW = "Chưa viết"
STATUS_WRITING = "Đang viết"
STATUS_DRAFT_SENT = "Đã gửi nháp"
STATUS_SCHEDULED = "Đã hẹn giờ"
STATUS_PUBLISHED = "Đã đăng"
STATUS_DROPPED = "Bỏ"
STATUSES = (
    STATUS_NEW,
    STATUS_WRITING,
    STATUS_DRAFT_SENT,
    STATUS_SCHEDULED,
    STATUS_PUBLISHED,
    STATUS_DROPPED,
)
# Trạng thái app ghi sau khi gửi WordPress (thiết kế 1.7): đề xuất từ file hay AI không đổi được.
APP_STATUSES = (STATUS_DRAFT_SENT, STATUS_SCHEDULED, STATUS_PUBLISHED)

# Cách gọi khác của nhãn (so trên chữ không dấu, chữ thường, bỏ dấu câu).
INTENT_ALIASES = {
    "thong tin": "Tìm hiểu",
    "informational": "Tìm hiểu",
    "so sanh": "So sánh trước khi mua",
    "commercial": "So sánh trước khi mua",
    "commercial investigation": "So sánh trước khi mua",
    "mua": "Mua hàng",
    "transactional": "Mua hàng",
}
KIND_ALIASES = {
    "huong dan": KIND_GUIDE,
    "guide": KIND_GUIDE,
    "how to": KIND_GUIDE,
    "service": KIND_SERVICE,
    "service page": KIND_SERVICE,
    "trang dich vu": KIND_SERVICE,
    "location": KIND_AREA,
    "trang khu vuc": KIND_AREA,
    "cong trinh": KIND_PROJECT,
    "case study": KIND_PROJECT,
    "cap nhat": KIND_UPDATE_OLD,
}
PRIORITY_ALIASES = {"high": "Cao", "tb": "Trung bình", "medium": "Trung bình", "low": "Thấp"}
STATUS_ALIASES = {
    "chua lam": STATUS_NEW,
    "moi": STATUS_NEW,
    "dang lam": STATUS_WRITING,
    "da dang bai": STATUS_PUBLISHED,
    "da xuat ban": STATUS_PUBLISHED,
    "huy": STATUS_DROPPED,
    "khong lam": STATUS_DROPPED,
}

# Cột của tab «KeHoach» (thiết kế 2.4), theo thứ tự: (tên trường, tiêu đề cột trên Sheet).
SHEET_TAB = "KeHoach"
SHEET_COLUMNS = (
    ("key", "Mã bài"),
    ("keyword", "Từ khóa chính"),
    ("secondary", "Từ khóa phụ, ý cần có"),
    ("intent", "Ý định"),
    ("kind", "Loại trang"),
    ("priority", "Ưu tiên"),
    ("planned_date", "Ngày dự kiến"),
    ("planned_time", "Giờ đăng"),
    ("status", "Trạng thái"),
    ("title_hint", "Tiêu đề dự kiến"),
    ("slug", "Slug"),
    ("target_id", "Trang dịch vụ đích"),
    ("notes", "Ghi chú của thợ"),
    ("wp_post_id", "Mã bài WordPress"),
    ("published_at", "Ngày đăng thực tế"),
    ("updated_at", "Cập nhật lúc"),
)
FIELD_LABELS = dict(SHEET_COLUMNS)

_DROPPED_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn"})
_KEY_RE = re.compile(r"([A-Z]{1,3})-([0-9]{1,5})")
_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_FOLD_DROP = re.compile(r"[^0-9a-z]+")
# Số ngày kiểu Google Sheets / Excel: ngày 0 là 30/12/1899.
_SHEETS_EPOCH = date(1899, 12, 30)
_SERIAL_RE = re.compile(r"\d{5}(?:\.0+)?")
_DMY_RE = re.compile(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})")
_YMD_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
_TIME_RE = re.compile(r"(\d{1,2})\s*(?::|h|g|giờ)\s*(\d{2})?\s*(?:phút)?", re.IGNORECASE)
_DATE_TIME_RE = re.compile(r"(.+?)(?:\s+|T)(\d{1,2}\s*(?::|h|g).*)$", re.IGNORECASE)


# ---------------------------------------------------------------------------------- làm sạch


def clean_text(value: object, *, multiline: bool = False) -> str:
    """Chữ kế hoạch đã làm sạch: NFC; bỏ ký tự điều khiển (trừ khoảng trắng), ký tự vô hình, ký tự
    đảo hướng chữ, surrogate lẻ, ký tự riêng, ký tự chưa gán (Unicode Cc, Cf, Cs, Co, Cn, như
    ``normalize_meta`` của T-041) và các ký tự «mặc định bỏ qua» khác; gộp khoảng trắng.

    ``multiline``: giữ xuống dòng (mỗi dòng gộp khoảng trắng riêng, gộp dòng trống liên tiếp),
    dùng cho «Ghi chú của thợ» và chữ tự do. Không phải chữ thì là chuỗi rỗng."""
    if not isinstance(value, str):
        return ""
    text = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    text = "".join(
        ch for ch in text if ch.isspace() or unicodedata.category(ch) not in _DROPPED_CATEGORIES
    )
    text = unicodedata.normalize("NFC", IGNORABLE_NOT_CF.sub("", text))
    if not multiline:
        return " ".join(text.split())
    lines: list[str] = []
    for line in text.split("\n"):
        line = " ".join(line.split())
        if line or (lines and lines[-1]):
            lines.append(line)
    return "\n".join(lines).strip()


def fold_key(value: object) -> str:
    """Chữ để so khớp (nhãn, tên cột, từ khóa): đã làm sạch, bỏ dấu, chữ thường, mọi thứ không phải
    chữ cái Latin hay chữ số thành một dấu cách."""
    text = remove_accents(clean_text(value)).lower()
    return " ".join(_FOLD_DROP.sub(" ", text).split())


def keyword_key(keyword: object) -> str:
    """Khóa so trùng từ khóa giữa các dòng (thiết kế 1.4: chữ thường, bỏ dấu, gộp khoảng trắng)."""
    return fold_key(keyword)


def match_label(
    value: object, labels: Iterable[str], aliases: Mapping[str, str] | None = None
) -> str:
    """Nhãn chuẩn trong ``labels`` ứng với ``value`` (so không dấu, chữ thường; nhận cả cách gọi
    khác trong ``aliases``). Ô trống là ``""``. Không nhận ra thì ``ValueError``."""
    key = fold_key(value)
    if not key:
        return ""
    for label in labels:
        if fold_key(label) == key:
            return label
    if aliases and key in aliases:
        return aliases[key]
    raise ValueError("nhãn không thuộc danh sách")


def _in_range(day: date) -> date:
    if not YEAR_MIN <= day.year <= YEAR_MAX:
        raise ValueError(f"ngày phải trong khoảng năm {YEAR_MIN}-{YEAR_MAX}")
    return day


def parse_plan_date(value: object) -> date | None:
    """Ngày dự kiến: ô trống là ``None``. Nhận ``date``, số ngày kiểu Google Sheets (ví dụ 46337),
    ``dd/mm/yyyy`` (cả ``d/m/yyyy``, ``dd-mm-yyyy``, ``dd.mm.yyyy``), ``yyyy-mm-dd``. **Không**
    nhận kiểu Mỹ ``mm/dd`` (``11/25/2026`` là tháng 25: báo lỗi), không nhận ngày thiếu năm. Năm
    ngoài ``YEAR_MIN``-``YEAR_MAX`` hay chữ không đọc được: ``ValueError``."""
    if value is None:
        return None
    if isinstance(value, datetime):
        raise ValueError("ngày không được có giờ")
    if isinstance(value, date):
        return _in_range(value)
    if isinstance(value, bool):
        raise ValueError("ngày sai kiểu")
    if isinstance(value, int | float):
        if isinstance(value, float) and not value.is_integer():
            raise ValueError("số ngày phải là số nguyên")
        return _serial_date(int(value))
    text = clean_text(value)
    if not text:
        return None
    if _SERIAL_RE.fullmatch(text):
        return _serial_date(int(float(text)))
    try:
        if found := _DMY_RE.fullmatch(text):
            day, month, year = (int(g) for g in found.groups())
            return _in_range(date(year, month, day))
        if found := _YMD_RE.fullmatch(text):
            year, month, day = (int(g) for g in found.groups())
            return _in_range(date(year, month, day))
    except ValueError:
        raise ValueError("ngày không có thật") from None
    raise ValueError("không đọc được ngày")


def _serial_date(serial: int) -> date:
    try:
        return _in_range(_SHEETS_EPOCH + timedelta(days=serial))
    except OverflowError:
        raise ValueError("số ngày ngoài khoảng") from None


def parse_plan_time(value: object) -> str:
    """Giờ đăng ``HH:MM`` (giờ Việt Nam). Nhận ``8:00``, ``08:30``, ``8h``, ``8h30``, ``8 giờ``. Ô
    trống là ``""``; sai (giờ 25, phút 61, chữ lạ) là ``ValueError``."""
    text = clean_text(value)
    if not text:
        return ""
    found = _TIME_RE.fullmatch(text)
    if not found:
        raise ValueError("không đọc được giờ")
    hour, minute = int(found.group(1)), int(found.group(2) or 0)
    if hour > 23 or minute > 59:
        raise ValueError("giờ không có thật")
    return f"{hour:02d}:{minute:02d}"


def split_date_time(value: object) -> tuple[str, str]:
    """Ô «ngày giờ» (``20/11/2026 08:00``, ``2026-11-20T08:00``) thành (phần ngày, phần giờ)."""
    text = clean_text(value)
    found = _DATE_TIME_RE.fullmatch(text)
    return (found.group(1), found.group(2)) if found else (text, "")


def parse_plan_datetime(value: object) -> datetime | None:
    """Thời điểm app ghi (ngày đăng thực tế, cập nhật lúc): luôn có múi giờ. Nhận ``datetime`` có
    múi giờ, chữ ISO 8601 (``2026-11-20T08:00:00+07:00``), hay ``dd/mm/yyyy HH:MM`` (giờ Việt
    Nam). Không có múi giờ thì hiểu là giờ Việt Nam. Ô trống là ``None``."""
    if value is None:
        return None
    if isinstance(value, datetime):
        moment = value
    else:
        text = clean_text(value)
        if not text:
            return None
        try:
            moment = datetime.fromisoformat(text)
        except ValueError:
            day_text, time_text = split_date_time(text)
            day = parse_plan_date(day_text)
            if day is None or not time_text:
                raise ValueError("không đọc được thời điểm") from None
            hour, minute = (int(part) for part in parse_plan_time(time_text).split(":"))
            moment = datetime(day.year, day.month, day.day, hour, minute)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=TIMEZONE)
    _in_range(moment.date())
    return moment


def today_vn() -> date:
    """Ngày hôm nay theo giờ Việt Nam (không theo múi giờ của máy)."""
    return datetime.now(TIMEZONE).date()


def parse_key(value: object) -> str:
    """Mã bài (``B-001``, ``KV-12``): chữ hoa, đúng dạng ``[A-Z]{1,3}-[0-9]{1,5}``. Ô trống là
    ``""``; sai dạng là ``ValueError``."""
    key = clean_text(value).upper()
    if key and not _KEY_RE.fullmatch(key):
        raise ValueError("mã bài phải có dạng B-001")
    return key


def next_key(existing: Iterable[str], prefix: str = "B") -> str:
    """Mã bài kế tiếp cho dòng mới: số lớn nhất của ``prefix`` cộng 1, ít nhất 3 chữ số
    (``B-001``, ``B-024``)."""
    numbers = [
        int(found.group(2))
        for key in existing
        if isinstance(key, str) and (found := _KEY_RE.fullmatch(key)) and found.group(1) == prefix
    ]
    number = max(numbers, default=0) + 1
    if number > 99_999:
        raise ValueError("hết mã bài")
    return f"{prefix}-{number:03d}"


def article_kind(kind: str) -> ArticleKind | None:
    """Loại trang của kế hoạch thành ``ArticleKind`` của quy tắc chọn link (YC-602). «Công trình
    thực tế» chọn link như bài hướng dẫn; «Cập nhật bài cũ» và ô trống: ``None``."""
    from seo_app.onpage.links import ArticleKind  # nhập muộn: links → storage → … (vòng nhập)

    return {
        KIND_GUIDE: ArticleKind.GUIDE,
        KIND_PROJECT: ArticleKind.GUIDE,
        KIND_SERVICE: ArticleKind.SERVICE,
        KIND_AREA: ArticleKind.AREA,
    }.get(kind)


# --------------------------------------------------- dữ liệu cá nhân của khách (A3, LC-T094-21)

MASK = "[đã ẩn]"
# Số điện thoại Việt Nam: 0 hay +84/84 rồi 9-10 chữ số, cho phép dấu cách, chấm, gạch xen giữa.
_PHONE_RE = re.compile(r"(?<![\w+])(?:\+84|84|0)(?:[ .\-]?\d){9,10}(?![\w])")
_EMAIL_RE = re.compile(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")


def personal_info(text: object) -> tuple[int, int]:
    """Số (số điện thoại, email) tìm thấy trong ``text`` (đã làm sạch: ký tự vô hình chen giữa
    không che được số). Chỉ đếm, không trả lại chữ tìm thấy."""
    visible = clean_text(text, multiline=True)
    return len(_PHONE_RE.findall(visible)), len(_EMAIL_RE.findall(visible))


def mask_personal_info(text: object) -> str:
    """``text`` đã làm sạch, số điện thoại và email thay bằng ``MASK``."""
    visible = clean_text(text, multiline=True)
    return _PHONE_RE.sub(MASK, _EMAIL_RE.sub(MASK, visible))


# ------------------------------------------------------------------------------------ khuôn


def _clean_limited(value: object, limit: int, *, multiline: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError("phải là chữ")
    text = clean_text(value, multiline=multiline)
    if len(text) > limit:
        raise ValueError(f"dài quá {limit} ký tự")
    return text


class PlanRow(BaseModel):
    """Một dòng kế hoạch (một bài). Tự làm sạch và tự kiểm khi tạo (LC-T094-18).

    - ``key``: Mã bài (``B-001``); ``""`` là dòng mới chưa cấp mã.
    - ``keyword``: Từ khóa chính, bắt buộc, một dòng, ``KEYWORD_MIN``-``KEYWORD_MAX`` ký tự; dấu
      «» đổi thành ‹› (từ khóa nằm trong lời dặn AI, như tiêu đề mục ở ``rewrite_prompt``).
    - ``intent``, ``kind``, ``priority``, ``status``: nhãn thuộc danh sách cố định (hay ``""``).
    - ``planned_date``, ``planned_time``: ngày dự kiến, giờ đăng ``HH:MM`` giờ Việt Nam.
    - ``target_id``: **mã bài** của trang dịch vụ đích trong danh sách bài đã đăng (không giữ địa
      chỉ web: thiết kế 1.3, LC-T094-20).
    - ``wp_post_id``, ``published_at``, ``updated_at``: app ghi sau khi gửi WordPress.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str = ""
    keyword: str
    secondary: str = ""
    intent: str = ""
    kind: str = ""
    priority: str = ""
    planned_date: date | None = None
    planned_time: str = ""
    status: str = STATUS_NEW
    title_hint: str = ""
    slug: str = ""
    target_id: int | None = Field(default=None, strict=True, gt=0, le=MAX_POST_ID)
    notes: str = ""
    wp_post_id: int | None = Field(default=None, strict=True, gt=0, le=MAX_POST_ID)
    published_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("key", mode="before")
    @classmethod
    def _key(cls, value: object) -> str:
        return parse_key(_clean_limited(value, 9))

    @field_validator("keyword", mode="before")
    @classmethod
    def _keyword(cls, value: object) -> str:
        keyword = _clean_limited(value, KEYWORD_MAX).replace("«", "‹").replace("»", "›")
        if len(keyword) < KEYWORD_MIN:
            raise ValueError(f"từ khóa phải có ít nhất {KEYWORD_MIN} ký tự")
        return keyword

    @field_validator("secondary", mode="before")
    @classmethod
    def _secondary(cls, value: object) -> str:
        return _clean_limited(value, SECONDARY_MAX)

    @field_validator("title_hint", mode="before")
    @classmethod
    def _title(cls, value: object) -> str:
        return _clean_limited(value, TITLE_MAX)

    @field_validator("notes", mode="before")
    @classmethod
    def _notes(cls, value: object) -> str:
        return _clean_limited(value, NOTES_MAX, multiline=True)

    @field_validator("intent", mode="before")
    @classmethod
    def _intent(cls, value: object) -> str:
        return match_label(_clean_limited(value, MAX_CELL_CHARS), INTENTS, INTENT_ALIASES)

    @field_validator("kind", mode="before")
    @classmethod
    def _kind(cls, value: object) -> str:
        return match_label(_clean_limited(value, MAX_CELL_CHARS), KINDS, KIND_ALIASES)

    @field_validator("priority", mode="before")
    @classmethod
    def _priority(cls, value: object) -> str:
        return match_label(_clean_limited(value, MAX_CELL_CHARS), PRIORITIES, PRIORITY_ALIASES)

    @field_validator("status", mode="before")
    @classmethod
    def _status(cls, value: object) -> str:
        label = match_label(_clean_limited(value, MAX_CELL_CHARS), STATUSES, STATUS_ALIASES)
        return label or STATUS_NEW

    @field_validator("planned_date", mode="before")
    @classmethod
    def _date(cls, value: object) -> date | None:
        return parse_plan_date(value)

    @field_validator("planned_time", mode="before")
    @classmethod
    def _time(cls, value: object) -> str:
        return parse_plan_time(_clean_limited(value, 20))

    @field_validator("slug", mode="before")
    @classmethod
    def _slug(cls, value: object) -> str:
        slug = _clean_limited(value, SLUG_MAX)
        if slug and not _SLUG_RE.fullmatch(slug):
            raise ValueError("slug chỉ gồm chữ thường không dấu, chữ số và dấu gạch")
        return slug

    @field_validator("published_at", "updated_at", mode="before")
    @classmethod
    def _moment(cls, value: object) -> datetime | None:
        return parse_plan_datetime(value)


def make_slug(value: object) -> str:
    """Slug người dùng gõ («Sửa cửa cuốn Q7») thành dạng hợp lệ (``sua-cua-cuon-q7``); không cắt
    từ (slug của phiếu luôn thắng slug tự sinh, T-033 mục 5.2). Không còn gì thì ``""``."""
    return slugify(clean_text(value), max_length=SLUG_MAX + 1)

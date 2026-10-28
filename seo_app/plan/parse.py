"""Đọc kế hoạch người dùng đưa vào: file CSV/TSV/TXT/MD và chữ dán (T-098).

Thiết kế: ``docs/team/reports/T-094-tho-may.md`` mục 1.2. Chủ dự án chọn câu 2A: chỉ nhận CSV và
chữ thường; Excel, Word, PDF thì chép vùng ô hay đoạn chữ rồi dán (bảng chép từ Excel có dấu tab).

- Bảng có dòng tiêu đề và có cột từ khóa: code tự đọc, ghép cột theo **tên cột** (danh sách tên
  đồng nghĩa), mỗi dòng dựng thành ``PlanRow``.
- Không nhận ra bảng hay cột từ khóa: là chữ tự do (ghi chú định hướng), để AI đọc
  (``ContentWriter.plan_changes``).

An toàn (LC-T094-18): giới hạn kiểm **trước khi** đọc (file theo byte trước khi giải mã, chữ dán
theo ký tự); chỉ ``utf-8``, ``utf-8-sig``, không đoán bảng mã khác; CSV đọc bằng ``csv`` của thư
viện chuẩn. Câu báo là câu cố định (LC-T094-2): chỉ nêu số dòng và **tên cột chuẩn**, không chép
chữ trong ô hay tên file.
"""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import ValidationError

from seo_app.plan import model
from seo_app.plan.model import (
    FIELD_LABELS,
    MAX_CELL_CHARS,
    MAX_COLUMNS,
    MAX_FILE_BYTES,
    MAX_PASTE_CHARS,
    MAX_ROWS,
    PlanRow,
    clean_text,
    fold_key,
)

if TYPE_CHECKING:
    from seo_app.storage.site_index import SiteIndex

ALLOWED_SUFFIXES = (".csv", ".tsv", ".txt", ".md")

FILE_TOO_BIG = f"File lớn quá {MAX_FILE_BYTES // 1_000_000} MB. Chia nhỏ file rồi tải lại."
FILE_BAD_TYPE = (
    "Chỉ nhận file .csv, .tsv, .txt, .md. File Excel, Word, PDF: mở file, chép vùng ô hoặc đoạn "
    "chữ rồi dán vào ô «Dán nội dung», hoặc dán link Google Sheets."
)
FILE_BAD_ENCODING = (
    "Không đọc được chữ trong file (không phải UTF-8). Trong Excel chọn Lưu thành (Save As) → "
    "«CSV UTF-8 (Comma delimited)», rồi tải lại."
)
PASTE_TOO_LONG = f"Nội dung dán dài quá {MAX_PASTE_CHARS:,} ký tự. Chia nhỏ rồi dán từng phần."
TEXT_TOO_LONG = (
    f"Chữ tự do dài quá {MAX_PASTE_CHARS:,} ký tự (AI chỉ đọc tới mức đó). Chia nhỏ, hoặc đưa kế "
    "hoạch về dạng bảng có cột «Từ khóa chính»."
)
TOO_MANY_ROWS = f"Bảng có hơn {MAX_ROWS:,} dòng. Chia nhỏ bảng rồi đưa vào từng phần."
TOO_MANY_COLUMNS = f"Bảng có hơn {MAX_COLUMNS} cột. Bỏ bớt cột không cần rồi đưa vào lại."
BAD_TABLE = "Không đọc được bảng (ô quá dài hoặc dấu ngoặc kép không đóng). Kiểm tra lại file."
EMPTY = "Không có nội dung nào để đọc."
OUTSIDE_TABLE = "Chỉ đọc bảng; phần chữ ngoài bảng không được đọc (muốn AI đọc thì dán riêng)."


class PlanSourceError(Exception):
    """Không đọc được nguồn kế hoạch. ``str(err)`` là câu tiếng Việt cố định, hiện thẳng được."""


@dataclass(frozen=True)
class ParsedPlan:
    """Kết quả đọc một nguồn kế hoạch.

    - ``rows``: các dòng đọc được từ bảng (đã qua ``PlanRow``).
    - ``free_text``: chữ tự do đã làm sạch (khi không phải bảng có cột từ khóa), để AI đọc.
    - ``warnings``: câu báo cố định (số dòng, tên cột chuẩn), không chép chữ trong ô.
    - ``skipped``: số dòng bỏ qua (không có từ khóa, mã bài trùng, không dựng được ``PlanRow``).
    """

    rows: tuple[PlanRow, ...] = ()
    free_text: str = ""
    warnings: tuple[str, ...] = ()
    skipped: int = 0

    @property
    def is_table(self) -> bool:
        return not self.free_text


# Tên cột đồng nghĩa (so trên chữ không dấu, chữ thường, bỏ dấu câu: ``fold_key``). So **trọn**
# tên, không so một phần: «Ngày đăng» là ngày dự kiến, «Ngày đăng thực tế» là cột app ghi.
_HEADER_NAMES = {
    "key": ("ma bai", "ma"),
    "keyword": ("tu khoa chinh", "tu khoa", "keyword", "main keyword", "focus keyword"),
    "secondary": (
        "tu khoa phu y can co", "tu khoa phu", "y can co", "secondary keywords",
        "secondary keyword",
    ),
    "intent": ("y dinh", "y dinh tim kiem", "search intent", "intent"),
    "kind": ("loai trang", "loai bai", "loai"),
    "priority": ("uu tien", "do uu tien", "priority"),
    "planned_date": (
        "ngay du kien", "ngay", "ngay dang", "ngay gio dang", "ngay phat hanh", "phat hanh",
        "publish date",
    ),
    "planned_time": ("gio dang", "gio"),
    "status": ("trang thai", "tinh trang", "status"),
    "title_hint": ("tieu de du kien", "tieu de", "title"),
    "slug": ("slug", "duong dan"),
    "target_id": ("trang dich vu dich", "trang dich", "trang dich vu", "target url"),
    "notes": ("ghi chu cua tho", "ghi chu", "notes"),
    "wp_post_id": ("ma bai wordpress", "wordpress id", "id wordpress"),
    "published_at": ("ngay dang thuc te",),
    "updated_at": ("cap nhat luc",),
}  # fmt: skip
_HEADERS = {name: field_name for field_name, names in _HEADER_NAMES.items() for name in names}
# Dòng phân cách của bảng Markdown: «|---|:---:|».
_MD_SEPARATOR = re.compile(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?")
_DIGITS = re.compile(r"\d{1,10}")


# ------------------------------------------------------------------------------- vào


def read_file(data: bytes, filename: str, *, index: SiteIndex | None = None) -> ParsedPlan:
    """Đọc file tải lên. Kiểm kích thước theo byte **trước khi** giải mã (≤ ``MAX_FILE_BYTES``),
    rồi đuôi file (``ALLOWED_SUFFIXES``), rồi bảng mã (``utf-8``, ``utf-8-sig``; không đoán).
    ``.csv`` (dấu phân cách «,», «;» hay tab theo dòng đầu), ``.tsv``: bảng. ``.txt``, ``.md``:
    như chữ dán (nhận bảng tab, bảng Markdown, hoặc chữ tự do). ``index``: danh sách bài đã đăng,
    để đổi cột «Trang dịch vụ đích» thành mã bài. Lỗi: ``PlanSourceError``."""
    if not isinstance(data, bytes | bytearray):
        raise PlanSourceError(EMPTY)
    if len(data) > MAX_FILE_BYTES:
        raise PlanSourceError(FILE_TOO_BIG)
    name = filename if isinstance(filename, str) else ""
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED_SUFFIXES:
        raise PlanSourceError(FILE_BAD_TYPE)
    try:
        text = bytes(data).decode("utf-8-sig")  # nhận cả UTF-8 có BOM («CSV UTF-8» của Excel)
    except UnicodeDecodeError:
        raise PlanSourceError(FILE_BAD_ENCODING) from None
    text = _newlines(text)
    if not text.strip():
        raise PlanSourceError(EMPTY)
    if suffix == ".csv":
        return _read_table(text, _csv_delimiter(text), index, free_if_unknown=True)
    if suffix == ".tsv":
        return _read_table(text, "\t", index, free_if_unknown=True)
    return _read_text(text, index)


def read_paste(text: str, *, index: SiteIndex | None = None) -> ParsedPlan:
    """Đọc chữ dán (≤ ``MAX_PASTE_CHARS`` ký tự): bảng chép từ Excel/Google Sheets (có dấu tab
    trên đa số dòng), bảng Markdown, hoặc chữ tự do. Lỗi: ``PlanSourceError``."""
    if not isinstance(text, str) or not text.strip():
        raise PlanSourceError(EMPTY)
    if len(text) > MAX_PASTE_CHARS:
        raise PlanSourceError(PASTE_TOO_LONG)
    return _read_text(_newlines(text), index)


def _newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _csv_delimiter(text: str) -> str:
    """Dấu phân cách CSV theo dòng đầu: «,» (mặc định), «;» (Excel máy đặt vùng châu Âu), tab."""
    first = text.split("\n", 1)[0]
    counts = {sep: first.count(sep) for sep in (",", ";", "\t")}
    best = max(counts, key=lambda sep: counts[sep])
    return best if counts[best] else ","


def _read_text(text: str, index: SiteIndex | None) -> ParsedPlan:
    lines = [line for line in text.split("\n") if line.strip()]
    tabbed = sum("\t" in line for line in lines)
    if len(lines) >= 2 and tabbed >= max(2, 0.6 * len(lines)):
        return _read_table(text, "\t", index, free_if_unknown=True)
    tables = _markdown_tables(text)
    for table in tables:
        result = _rows_to_plan(table, index)
        if result is not None:
            if _outside_tables(text):
                warnings = (*result.warnings, OUTSIDE_TABLE)
                return ParsedPlan(result.rows, "", warnings, result.skipped)
            return result
    return _free_text(text)


def _free_text(text: str) -> ParsedPlan:
    cleaned = clean_text(text, multiline=True)
    if not cleaned:
        raise PlanSourceError(EMPTY)
    if len(cleaned) > MAX_PASTE_CHARS:
        raise PlanSourceError(TEXT_TOO_LONG)
    return ParsedPlan(free_text=cleaned)


# ------------------------------------------------------------------------------- bảng


def _read_table(
    text: str, delimiter: str, index: SiteIndex | None, *, free_if_unknown: bool
) -> ParsedPlan:
    try:
        table = _limited_rows(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))
    except csv.Error:
        raise PlanSourceError(BAD_TABLE) from None
    result = _rows_to_plan(table, index)
    if result is not None:
        return result
    if free_if_unknown:
        return _free_text(text)
    raise PlanSourceError(BAD_TABLE)


def _limited_rows(rows) -> list[list[str]]:
    """Các dòng không trống của bảng (bỏ ô trống ở cuối dòng), kiểm giới hạn **trong lúc** đọc:
    quá ``MAX_ROWS`` dòng dữ liệu hay ``MAX_COLUMNS`` cột thì dừng ngay."""
    table: list[list[str]] = []
    for row in rows:
        while row and not row[-1].strip():
            row.pop()
        if not row:
            continue
        if len(row) > MAX_COLUMNS:
            raise PlanSourceError(TOO_MANY_COLUMNS)
        table.append(row)
        if len(table) > MAX_ROWS + 1:  # +1: dòng tiêu đề
            raise PlanSourceError(TOO_MANY_ROWS)
    return table


def _markdown_tables(text: str) -> list[list[list[str]]]:
    """Các bảng Markdown (dòng mở đầu bằng «|»), bỏ dòng phân cách «|---|»."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|"):
            if not _MD_SEPARATOR.fullmatch(stripped):
                cells = stripped.strip("|").split("|")
                if len(cells) > MAX_COLUMNS:
                    raise PlanSourceError(TOO_MANY_COLUMNS)
                current.append([cell.strip() for cell in cells])
                if len(current) > MAX_ROWS + 1:
                    raise PlanSourceError(TOO_MANY_ROWS)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _outside_tables(text: str) -> bool:
    """Có chữ (ngoài tiêu đề Markdown «#…») nằm ngoài bảng không."""
    return any(
        line.strip() and not line.strip().startswith(("|", "#")) for line in text.split("\n")
    )


def _header_map(header: Sequence[str]) -> tuple[dict[str, int], list[str]]:
    """Cột → chỉ số, theo tên cột đồng nghĩa. Cột trùng nghĩa: lấy cột đầu, báo."""
    columns: dict[str, int] = {}
    warnings: list[str] = []
    for position, title in enumerate(header):
        field_name = _HEADERS.get(fold_key(title[:MAX_CELL_CHARS]))
        if field_name is None:
            continue
        if field_name in columns:
            warnings.append(f"Có hơn một cột «{FIELD_LABELS[field_name]}»: chỉ đọc cột đầu tiên.")
            continue
        columns[field_name] = position
    return columns, warnings


@dataclass
class _Notes:
    """Gom câu báo theo loại, kèm số dòng (không chép chữ trong ô)."""

    rows: dict[str, list[int]] = field(default_factory=dict)

    def add(self, message: str, line: int) -> None:
        self.rows.setdefault(message, []).append(line)

    def render(self) -> list[str]:
        out = []
        for message, lines in self.rows.items():
            shown = ", ".join(str(n) for n in lines[:5]) + (", …" if len(lines) > 5 else "")
            out.append(f"{message} ({len(lines)} dòng: dòng {shown}).")
        return out


def _rows_to_plan(table: list[list[str]], index: SiteIndex | None) -> ParsedPlan | None:
    """Bảng (dòng đầu là tiêu đề) thành ``ParsedPlan``; ``None`` nếu không có cột từ khóa."""
    if not table:
        return None
    columns, warnings = _header_map(table[0])
    if "keyword" not in columns:
        return None
    if len(table) - 1 > MAX_ROWS:
        raise PlanSourceError(TOO_MANY_ROWS)
    notes = _Notes()
    rows: list[PlanRow] = []
    seen_keys: set[str] = set()
    skipped = 0
    for line, cells in enumerate(table[1:], start=2):
        row = _row(cells, columns, line, index, notes)
        if row is None:
            skipped += 1
            continue
        if row.key and row.key in seen_keys:
            notes.add("Mã bài trùng với một dòng phía trên nên bỏ qua dòng này", line)
            skipped += 1
            continue
        if row.key:
            seen_keys.add(row.key)
        rows.append(row)
    return ParsedPlan(tuple(rows), "", tuple(warnings + notes.render()), skipped)


def _cell(cells: Sequence[str], columns: dict[str, int], name: str, line: int, notes) -> str:
    position = columns.get(name)
    if position is None or position >= len(cells):
        return ""
    value = cells[position]
    if len(value) > MAX_CELL_CHARS:
        notes.add(f"Ô «{FIELD_LABELS[name]}» dài quá {MAX_CELL_CHARS:,} ký tự, đã cắt", line)
        value = value[:MAX_CELL_CHARS]
    return value


# Cách đổi chữ trong ô thành giá trị của từng trường (``ValueError`` khi sai).
_LABELS = {
    "intent": (model.INTENTS, model.INTENT_ALIASES),
    "kind": (model.KINDS, model.KIND_ALIASES),
    "priority": (model.PRIORITIES, model.PRIORITY_ALIASES),
    "status": (model.STATUSES, model.STATUS_ALIASES),
}


def _converters() -> dict[str, object]:
    converters: dict[str, object] = {
        name: (lambda raw, c=choices, a=aliases: model.match_label(raw, c, a))
        for name, (choices, aliases) in _LABELS.items()
    }
    converters.update(
        key=model.parse_key,
        planned_time=model.parse_plan_time,
        title_hint=lambda raw: _limit(raw, model.TITLE_MAX),
        secondary=lambda raw: _limit(raw, model.SECONDARY_MAX),
        notes=lambda raw: clean_text(raw, multiline=True),
        slug=_slug,
        wp_post_id=_post_id,
        published_at=model.parse_plan_datetime,
        updated_at=model.parse_plan_datetime,
    )
    return converters


def _row(cells, columns, line: int, index: SiteIndex | None, notes: _Notes) -> PlanRow | None:
    """Một dòng của bảng thành ``PlanRow``. Ô sai thì bỏ trống ô đó và báo; từ khóa thiếu hay sai
    độ dài thì bỏ cả dòng."""
    values = {name: _cell(cells, columns, name, line, notes) for name in columns}
    keyword = clean_text(values.pop("keyword", ""))
    if not keyword:
        notes.add("Dòng không có từ khóa chính nên bỏ qua", line)
        return None
    if not model.KEYWORD_MIN <= len(keyword) <= model.KEYWORD_MAX:
        notes.add(
            f"Từ khóa chính phải dài {model.KEYWORD_MIN}-{model.KEYWORD_MAX} ký tự nên bỏ qua", line
        )
        return None
    fields: dict[str, object] = {"keyword": keyword}

    def bad(name: str) -> None:
        notes.add(f"Ô «{FIELD_LABELS[name]}» không đọc được, đã bỏ trống ô đó", line)

    day_text, time_text = model.split_date_time(values.pop("planned_date", ""))
    if day_text:
        try:
            fields["planned_date"] = model.parse_plan_date(day_text)
        except ValueError:
            bad("planned_date")
    if time_text and not clean_text(values.get("planned_time", "")):
        values["planned_time"] = time_text  # ô «Ngày giờ đăng»: lấy giờ khi không có cột giờ
    target = values.pop("target_id", "")
    if clean_text(target):
        target_id = resolve_target(target, index)
        if target_id is None:
            notes.add(
                "Ô «Trang dịch vụ đích» không phải bài đã đăng trên website, đã bỏ trống ô đó", line
            )
        else:
            fields["target_id"] = target_id
    converters = _converters()
    for name, raw in values.items():
        if not clean_text(raw):
            continue
        try:
            fields[name] = converters[name](raw)
        except ValueError:
            bad(name)
    try:
        return PlanRow.model_validate(fields)
    except ValidationError:
        notes.add("Dòng không đọc được nên bỏ qua", line)
        return None


def _limit(raw: str, limit: int) -> str:
    text = clean_text(raw)
    if len(text) > limit:
        raise ValueError("dài quá")
    return text


def _slug(raw: str) -> str:
    slug = model.make_slug(raw)
    if not slug or len(slug) > model.SLUG_MAX:
        raise ValueError("slug sai")
    return slug


def _post_id(raw: str) -> int:
    text = clean_text(raw)
    if not _DIGITS.fullmatch(text) or not 0 < int(text) <= model.MAX_POST_ID:
        raise ValueError("mã bài WordPress sai")
    return int(text)


def resolve_target(value: object, index: SiteIndex | None) -> int | None:
    """Ô «Trang dịch vụ đích» (link một trang trên website, hoặc mã bài) thành **mã bài** có trong
    danh sách bài đã đăng; không có ``index``, không phải link của chính site, hay không có trong
    danh sách: ``None``. App chỉ giữ mã bài, không bao giờ giữ hay mở địa chỉ lấy từ kế hoạch
    (thiết kế 1.3, LC-T094-20)."""
    if index is None:
        return None
    text = clean_text(value)
    if _DIGITS.fullmatch(text):
        post_id = int(text)
        return post_id if any(item.id == post_id for item in index.items) else None
    from seo_app.wordpress.client import is_site_link  # nhập muộn: gói wordpress nặng

    if not is_site_link(text, index.site):
        return None
    wanted = {text, text.rstrip("/"), text.rstrip("/") + "/"}
    return next((item.id for item in index.items if item.link in wanted), None)

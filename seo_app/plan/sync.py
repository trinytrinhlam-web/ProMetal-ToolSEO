"""Đồng bộ kế hoạch với Google Sheets (T-100; thiết kế T-094 mục 1.5–1.7, 2.4–2.6).

- **Đọc** (``get_plan``, ``read_sheet``, ``parse_sheet``): tab «KeHoach» (một lệnh), tìm cột
  **theo tên** ở dòng 1 (đổi thứ tự cột, thêm cột riêng đều được), mọi dòng qua ``PlanRow`` (dữ
  liệu chưa tin cậy, LC-T094-18). Cache ``data/plan_cache.sqlite`` (``PlanCacheStore``) để vẽ trang
  ngay và khi mất mạng; cũ hơn 5 phút thì tải lại.
- **Áp dụng đề xuất đã duyệt** (``apply_proposals``, thiết kế 1.5, 2.5): đọc lại cả tab, tìm dòng
  theo **Mã bài** (không theo số dòng), so từng ô sắp ghi và ô Mã bài, Từ khóa với **bản gốc**
  (bản người dùng đã xem khi duyệt): khác thì không ghi dòng đó, trả «trước / bây giờ / đề xuất».
  Mã bài có ở hai dòng: không ghi. Các ô còn lại ghi trong **một** lệnh (Google áp dụng trọn hoặc
  không), chỉ đúng các ô đổi. Dòng mới: lệnh thêm dòng, không bao giờ tự thử lại; không chắc đã
  thêm thì đọc lại xem Mã bài đã có chưa, để **không thêm trùng**. Không bao giờ xóa dòng, cột.
- **Ghi trạng thái sau khi gửi** (``write_status``, ``record_status``, ``retry_pending``, thiết kế
  1.7, câu hỏi 4A): chỉ 4 ô Trạng thái, Mã bài WordPress, Ngày đăng thực tế, Cập nhật lúc của đúng
  dòng; chỉ ghi khi dòng còn ở trạng thái «trước» hợp lệ (không lùi trạng thái). Việc ghi còn nợ
  (mất mạng) nằm trong kho nháp ``drafts.sqlite``; thử lại **chỉ** ghi Sheet, không bao giờ gửi
  lại WordPress, vẫn kiểm như trên (LC-T094-30).
- **Chuẩn bị trang tính** (``prepare_sheet``, chỉ khi người dùng bấm, LC-T094-31): tạo tab
  «KeHoach», tiêu đề cột thiếu ghi vào **cuối** dòng 1 (không dời cột có sẵn), cố định dòng 1,
  định dạng cột ngày, danh sách chọn là hằng của code.

An toàn khi ghi (LC-T094-28): chỉ các cột app được ghi (``SHEET_COLUMNS``, thiết kế 2.4), không
bao giờ cột lạ; mọi ô ``RAW`` (client chặn ``USER_ENTERED``); chữ bắt đầu bằng ``=``, ``+``, ``-``,
``@``, tab, CR được thêm một dấu cách đầu (``safe_text``) để file tải về mở bằng Excel không thành
công thức; giờ ghi là giờ Việt Nam có ``+07:00`` (``datetime.now(ZoneInfo(…))``). Câu báo là câu
cố định (LC-T094-2): chỉ nêu Mã bài và tên cột chuẩn, không chép chữ ô Sheet hay lời máy chủ.

Khe hở còn lại (thiết kế 2.5, Lá Chắn T-094 ghi nhận 2): hai máy ghi **cùng một ô** trong khoảng
1–2 giây giữa lần đọc lại và lệnh ghi thì bản ghi sau thắng. Sheets không có lệnh ghi có điều kiện.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol

from seo_app.google.sheets import (
    MAX_CELL_CHARS as SHEET_CELL_CHARS,
)
from seo_app.google.sheets import (
    MAX_COLUMNS,
    MAX_ROWS,
    MAX_UPDATES,
    PLAN_TAB,
    CellUpdate,
    CellValue,
    SheetsError,
    SpreadsheetInfo,
)
from seo_app.plan import model, parse
from seo_app.plan.model import FIELD_LABELS, SHEET_COLUMNS, PlanRow, clean_text
from seo_app.plan.propose import Action, Proposal
from seo_app.storage.drafts import DraftError, DraftPlanRef, PlanStatusWrite
from seo_app.storage.plan_cache import PlanCacheError, PlanCacheStore, sheet_hash

if TYPE_CHECKING:
    from seo_app.storage.drafts import DraftStore
    from seo_app.storage.site_index import SiteIndex

Values = tuple[tuple[CellValue, ...], ...]

_SHEETS_EPOCH = date(1899, 12, 30)  # số ngày 0 của Google Sheets
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
# Ô so khi áp dụng đề xuất: Mã bài, Từ khóa và các ô sắp ghi. «Cập nhật lúc» app ghi kèm mọi lần
# ghi nên không so (hai máy sửa hai cột khác nhau của cùng dòng không chặn nhau).
_ALWAYS_COMPARED = ("key", "keyword")
# Trạng thái app ghi theo thứ tự bước (thiết kế 1.6, 1.7); «Bỏ» không nằm trong thứ tự.
_STATUS_ORDER = (
    model.STATUS_NEW,
    model.STATUS_WRITING,
    model.STATUS_DRAFT_SENT,
    model.STATUS_SCHEDULED,
    model.STATUS_PUBLISHED,
)
_DATE_PATTERN = "dd/mm/yyyy"
# Danh sách chọn của «Chuẩn bị trang tính»: hằng của code (LC-T094-31).
_CHOICES = {
    "intent": model.INTENTS,
    "kind": model.KINDS,
    "priority": model.PRIORITIES,
    "status": model.STATUSES,
}

# ------------------------------------------------------------------- câu báo cố định (LC-T094-2)
MSG_NO_KEYWORD_COLUMN = (
    "Trang tính «KeHoach» chưa có cột «Từ khóa chính» nên chưa đọc được kế hoạch. Bấm «Chuẩn bị "
    "trang tính» ở trang Cài đặt."
)
MSG_DUPLICATE_KEYS = (
    "Mã bài {keys} có ở nhiều dòng: phần mềm chỉ đọc dòng đầu và không ghi gì vào các dòng đó. "
    "Sửa cho mỗi bài một mã."
)
MSG_NOT_CONNECTED = "Chưa kết nối Google Sheets nên chưa đọc được kế hoạch."
MSG_CACHED_AT = "Đang hiện bản lưu lúc {time}."
MSG_NO_COLUMNS = (
    "Trang tính «KeHoach» thiếu cột {columns}: bấm «Chuẩn bị trang tính» ở trang Cài đặt rồi thử "
    "lại."
)
MSG_ROW_MISSING = "Không còn thấy dòng {key} trên Google Sheet (có thể đã bị xóa hay đổi Mã bài)."
MSG_ROW_UNREADABLE = "Dòng {key} trên Google Sheet không đọc được (thiếu hay sai từ khóa chính)."
MSG_TAB_NOT_CREATED = "Google chưa tạo được trang tính «KeHoach». Thử lại sau."
MSG_NO_ROOM = (
    "Dòng tiêu đề của trang tính «KeHoach» không còn đủ cột trống (tối đa 26 cột, A–Z) để thêm "
    "{count} cột còn thiếu. Bỏ bớt cột không dùng rồi thử lại."
)

CONFLICT_CHANGED = "Dòng vừa bị sửa ở nơi khác ({fields}) nên chưa ghi."
CONFLICT_MISSING = "Không còn thấy dòng này trên Google Sheet (có thể đã bị xóa hay đổi Mã bài)."
CONFLICT_DUPLICATE = "Mã bài {key} có ở nhiều dòng trên Google Sheet nên chưa ghi."
CONFLICT_AMBIGUOUS = "Có nhiều dòng chưa có Mã bài cùng từ khóa này nên chưa ghi."
CONFLICT_EXISTS = "Mã bài {key} đã có trên Google Sheet (có thể vừa thêm ở máy khác) nên chưa thêm."
CONFLICT_COLUMNS = "Trang tính thiếu cột {columns} nên chưa ghi."
CONFLICT_UNKNOWN_ROW = (
    "Không còn thấy dòng này trong bản kế hoạch đã xem. Đề xuất lại trên bản mới."
)

STATUS_WRITTEN = "Đã cập nhật trạng thái dòng {key} trên Google Sheet."
STATUS_ALREADY = "Dòng {key} trên Google Sheet đã đúng trạng thái."
STATUS_LATER = "Dòng {key} trên Google Sheet đã ở bước sau nên không đổi trạng thái."
STATUS_CONFLICT = "Chưa ghi trạng thái vào dòng {key}: {reason}"
STATUS_CHANGED = (
    "trạng thái hay Mã bài WordPress trên Sheet đã khác lúc mở bài (sửa ở nơi khác). Kiểm tra lại "
    "dòng đó trên Google Sheet."
)
STATUS_FAILED = (
    "Chưa ghi được trạng thái dòng {key} vào Google Sheet. {error} Phần mềm sẽ thử lại khi mở "
    "trang Kế hoạch (chỉ ghi Sheet, không gửi lại bài)."
)
STATUS_UNSURE = (
    "Chưa rõ đã ghi trạng thái dòng {key} vào Google Sheet chưa. {error} Phần mềm sẽ đọc lại Sheet "
    "rồi thử lại khi mở trang Kế hoạch (chỉ ghi Sheet, không gửi lại bài)."
)


class SheetPlanError(Exception):
    """Lỗi đồng bộ kế hoạch; ``str(err)`` là câu tiếng Việt cố định."""


class SheetsLike(Protocol):
    """Phần của ``SheetsClient`` (T-097) mà đồng bộ dùng; test thay bằng Sheet giả."""

    def get_info(self) -> SpreadsheetInfo: ...

    def read_plan_values(self) -> Values: ...

    def update_cells(self, updates: Sequence[CellUpdate]) -> int | None: ...

    def append_row(self, values: Sequence[CellValue]) -> int | None: ...

    def batch_update(
        self, requests_: Sequence[Mapping[str, Any]]
    ) -> tuple[dict[str, Any], ...]: ...


# ===================================================================================== đọc


@dataclass(frozen=True)
class SheetRow:
    """Một dòng kế hoạch đọc được: số dòng trên Sheet (dòng 1 là tiêu đề), ``PlanRow`` đã kiểm, và
    đúng các ô Google trả (bản gốc để so xung đột)."""

    number: int
    plan: PlanRow
    cells: tuple[CellValue, ...]


@dataclass(frozen=True)
class SheetPlan:
    """Tab «KeHoach» đã đọc. ``rows``: dòng đọc được, mỗi Mã bài một dòng (dòng đầu); ``columns``:
    trường → chỉ số cột (A = 0) theo tên ở dòng 1; ``key_rows``: Mã bài → các số dòng mang mã đó
    (đọc thẳng ô Mã bài, kể cả dòng không đọc được); ``values``: mọi ô (bản gốc, ghi cache).

    Chữ trong ``PlanRow`` đã làm sạch nhưng chưa escape: giao diện hiện bằng ô bảng, ``st.text``
    (LC-T094-3). ``warnings`` là câu cố định (chỉ số dòng, Mã bài, tên cột chuẩn)."""

    rows: tuple[SheetRow, ...]
    columns: Mapping[str, int]
    fetched_at: datetime
    values: Values = ()
    key_rows: Mapping[str, tuple[int, ...]] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    skipped: int = 0
    from_cache: bool = False

    @property
    def missing(self) -> tuple[str, ...]:
        """Các trường thiết kế 2.4 chưa có cột trên Sheet."""
        return tuple(name for name, _ in SHEET_COLUMNS if name not in self.columns)

    @property
    def duplicate_keys(self) -> frozenset[str]:
        return frozenset(key for key, numbers in self.key_rows.items() if len(numbers) > 1)

    def plan_rows(self) -> tuple[PlanRow, ...]:
        """Kế hoạch hiện tại cho ``propose.compare_rows`` / ``from_ai``."""
        return tuple(row.plan for row in self.rows)

    def find(self, key: str) -> SheetRow | None:
        """Dòng đọc được mang Mã bài ``key`` (đã chuẩn hóa, ví dụ ``B-001``)."""
        return next((row for row in self.rows if key and row.plan.key == key), None)

    def cells_of(self, number: int) -> tuple[CellValue, ...]:
        return self.values[number - 1] if 1 <= number <= len(self.values) else ()

    def plan_at(self, number: int) -> PlanRow | None:
        return next((row.plan for row in self.rows if row.number == number), None)

    def locate(self, before: PlanRow) -> SheetRow | None:
        """Dòng của bản này ứng với ``before`` (``Proposal.before``): theo Mã bài; dòng chưa có mã
        thì dòng chưa mã duy nhất bằng đúng ``before``."""
        if before.key:
            return self.find(before.key)
        found = [row for row in self.rows if not row.plan.key and row.plan == before]
        return found[0] if len(found) == 1 else None


def parse_sheet(
    values: Sequence[Sequence[CellValue]],
    *,
    fetched_at: datetime,
    index: SiteIndex | None = None,
    from_cache: bool = False,
) -> SheetPlan:
    """Các ô của tab «KeHoach» (dòng 1 là tiêu đề) thành ``SheetPlan``. Mọi dòng qua ``PlanRow``
    bằng đúng bộ đọc bảng của T-098 (ô sai thì bỏ trống ô đó và báo; thiếu từ khóa thì bỏ dòng).
    ``index``: danh sách bài đã đăng, để đổi «Trang dịch vụ đích» thành mã bài."""
    table = tuple(tuple(row) for row in values)
    header = table[0] if table else ()
    columns, header_notes = parse._header_map([_cell_text(cell) for cell in header])
    warnings = list(header_notes)
    if "keyword" not in columns:
        warnings.append(MSG_NO_KEYWORD_COLUMN)
        return SheetPlan((), columns, fetched_at, table, {}, tuple(warnings), 0, from_cache)
    fields_at = {position: name for name, position in columns.items()}
    notes = parse._Notes()
    key_rows: dict[str, list[int]] = {}
    rows: list[SheetRow] = []
    seen: set[str] = set()
    skipped = 0
    for number, cells in enumerate(table[1:], start=2):
        texts = [_cell_text(cell, fields_at.get(position)) for position, cell in enumerate(cells)]
        if not any(text.strip() for text in texts):
            continue  # dòng trống trên Sheet: bỏ qua, không báo
        key = _key_of(cells, columns.get("key"))
        if key:
            key_rows.setdefault(key, []).append(number)
        plan = parse._row(texts, columns, number, index, notes)
        if plan is None:
            skipped += 1
            continue
        if plan.key and plan.key in seen:
            notes.add("Mã bài trùng với một dòng phía trên nên bỏ qua dòng này", number)
            skipped += 1
            continue
        seen.add(plan.key)
        rows.append(SheetRow(number, plan, cells))
    duplicates = sorted(key for key, numbers in key_rows.items() if len(numbers) > 1)
    if duplicates:
        shown = ", ".join(duplicates[:5]) + (", …" if len(duplicates) > 5 else "")
        warnings.append(MSG_DUPLICATE_KEYS.format(keys=shown))
    warnings.extend(notes.render())
    return SheetPlan(
        rows=tuple(rows),
        columns=dict(columns),
        fetched_at=fetched_at,
        values=table,
        key_rows={key: tuple(numbers) for key, numbers in key_rows.items()},
        warnings=tuple(warnings),
        skipped=skipped,
        from_cache=from_cache,
    )


def read_sheet(
    client: SheetsLike, *, index: SiteIndex | None = None, now: datetime | None = None
) -> SheetPlan:
    """Đọc lại cả tab «KeHoach» từ Google (một lệnh). Lỗi: ``SheetsError`` câu cố định."""
    values = client.read_plan_values()
    return parse_sheet(values, fetched_at=now or _now(), index=index)


@dataclass(frozen=True)
class PlanListing:
    """Kế hoạch cho trang Kế hoạch. ``plan`` là ``None`` khi chưa đọc được lần nào; ``notice``:
    câu báo cố định (chữ thường), rỗng khi bình thường."""

    plan: SheetPlan | None
    notice: str = ""


def get_plan(
    store: PlanCacheStore,
    sheet_id: str,
    client: SheetsLike | None,
    *,
    index: SiteIndex | None = None,
    refresh: bool = False,
    now: datetime | None = None,
) -> PlanListing:
    """Kế hoạch từ cache nếu còn mới (≤ ``store.max_age_minutes``) và không bấm «Tải lại»; không
    thì đọc lại Sheet rồi ghi cache. Đọc Sheet lỗi mà có cache thì hiện bản lưu kèm câu báo.
    ``client`` là ``None``: chưa khai báo Google (hay file khóa lỗi), chỉ hiện bản lưu nếu có."""
    now = now or _now()
    cached = store.load(sheet_id)
    cached_plan = (
        parse_sheet(cached.values, fetched_at=cached.fetched_at, index=index, from_cache=True)
        if cached is not None
        else None
    )
    if cached_plan is not None and not refresh and not store.is_stale(cached, now=now):
        return PlanListing(cached_plan)
    if client is None:
        if cached_plan is not None:
            return PlanListing(cached_plan, f"{MSG_NOT_CONNECTED} {_cached_at(cached_plan)}")
        return PlanListing(None, MSG_NOT_CONNECTED)
    try:
        plan = read_sheet(client, index=index, now=now)
    except SheetsError as exc:
        if cached_plan is not None:
            return PlanListing(
                cached_plan, f"Chưa tải lại được kế hoạch. {exc} {_cached_at(cached_plan)}"
            )
        return PlanListing(None, f"Chưa tải được kế hoạch từ Google Sheets. {exc}")
    try:
        store.save(sheet_id, plan.values, plan.fetched_at)
    except PlanCacheError as exc:
        return PlanListing(plan, str(exc))
    return PlanListing(plan)


def _cached_at(plan: SheetPlan) -> str:
    moment = plan.fetched_at.astimezone(model.TIMEZONE)
    return MSG_CACHED_AT.format(time=moment.strftime("%H:%M %d/%m/%Y"))


# ====================================================================== áp dụng đề xuất


@dataclass(frozen=True)
class Conflict:
    """Một đề xuất **không** ghi vì dòng trên Sheet đã khác bản gốc (hay không tìm thấy, trùng
    mã, thiếu cột). ``now``: dòng bây giờ trên Sheet (``None`` nếu không còn hay không đọc được),
    để hiện «trước / bây giờ / đề xuất»; ``fields``: các trường bị sửa ở nơi khác."""

    proposal: Proposal
    reason: str
    fields: tuple[str, ...] = ()
    now: PlanRow | None = None

    @property
    def label(self) -> str:
        """«B-012 (Ngày dự kiến)»: Mã bài và tên cột chuẩn, không chép chữ trong ô."""
        key = self.proposal.key or (self.proposal.before.key if self.proposal.before else "")
        name = key or "dòng chưa có mã"
        if not self.fields:
            return name
        return f"{name} ({', '.join(FIELD_LABELS[f] for f in self.fields)})"


@dataclass(frozen=True)
class ApplyResult:
    """Kết quả «Áp dụng thay đổi». ``unsure``: lệnh ghi lỗi giữa chừng mà có thể đã chạy trên
    Google (mất mạng, hết giờ): phải đọc lại («Tải lại») trước khi áp dụng lại. ``error``: câu lỗi
    khiến dừng giữa chừng; ``not_written``: đề xuất chưa ghi vì dừng."""

    written: tuple[Proposal, ...] = ()
    conflicts: tuple[Conflict, ...] = ()
    unsure: tuple[Proposal, ...] = ()
    not_written: tuple[Proposal, ...] = ()
    error: str = ""

    @property
    def message(self) -> str:
        parts: list[str] = []
        if self.written:
            parts.append(f"Đã ghi {len(self.written)} thay đổi.")
        if self.conflicts:
            shown = ", ".join(c.label for c in self.conflicts[:5])
            more = ", …" if len(self.conflicts) > 5 else ""
            parts.append(
                f"{len(self.conflicts)} thay đổi chưa ghi vì dòng trên Google Sheet đã khác bản "
                f"đã xem: {shown}{more}."
            )
        if self.unsure:
            parts.append(
                f"{len(self.unsure)} thay đổi chưa rõ đã ghi chưa (lỗi giữa chừng): bấm «Tải lại» "
                "để xem bản mới trước khi áp dụng lại."
            )
        if self.error:
            parts.append(self.error)
        if self.not_written:
            parts.append(f"{len(self.not_written)} thay đổi chưa ghi.")
        return " ".join(parts) or "Không có thay đổi nào để ghi."


def apply_proposals(
    client: SheetsLike,
    base: SheetPlan,
    proposals: Sequence[Proposal],
    *,
    index: SiteIndex | None = None,
    now: datetime | None = None,
) -> ApplyResult:
    """Ghi các đề xuất người dùng đã tick lên Sheet (thiết kế 1.5, 2.5; LC-T094-28).

    ``base``: bản kế hoạch người dùng đã xem khi duyệt (đề xuất dựng từ ``base.plan_rows()``).
    Đọc lại cả tab trước khi ghi; dòng khác bản gốc thì không ghi (``Conflict``). Lỗi đọc lại:
    ``SheetsError``; tab thiếu cột Mã bài hay Từ khóa: ``SheetPlanError`` (cả hai: chưa ghi gì).
    ``index``: để ghi «Trang dịch vụ đích» bằng link của bài."""
    now = now or _now()
    fresh = read_sheet(client, index=index, now=now)
    missing = [name for name in _ALWAYS_COMPARED if name not in fresh.columns]
    if missing:
        raise SheetPlanError(MSG_NO_COLUMNS.format(columns=_labels(missing)))
    stamp = _moment_text(now)
    conflicts: list[Conflict] = []
    updates: list[tuple[Proposal, list[CellUpdate]]] = []
    additions: list[tuple[Proposal, list[CellValue]]] = []
    written: list[Proposal] = []
    for proposal in proposals:
        if proposal.action is Action.ADD:
            planned = _addition(proposal, fresh, index, stamp)
            if isinstance(planned, Conflict):
                conflicts.append(planned)
            else:
                additions.append((proposal, planned))
            continue
        planned_cells = _update(proposal, base, fresh, index, stamp)
        if isinstance(planned_cells, Conflict):
            conflicts.append(planned_cells)
        elif planned_cells:
            updates.append((proposal, planned_cells))
        else:
            written.append(proposal)  # ô trên Sheet đã đúng giá trị đề xuất (lần ghi trước)
    unsure: list[Proposal] = []
    not_written: list[Proposal] = []
    error = ""
    for batch in _batches(updates):
        if error:
            not_written.extend(proposal for proposal, _ in batch)
            continue
        try:
            client.update_cells([cell for _, cells in batch for cell in cells])
        except SheetsError as exc:
            error = str(exc)
            (unsure if exc.unsure else not_written).extend(proposal for proposal, _ in batch)
            continue
        written.extend(proposal for proposal, _ in batch)
    for proposal, row in additions:
        if error:
            not_written.append(proposal)
            continue
        try:
            client.append_row(row)
        except SheetsError as exc:
            error = str(exc)
            if not exc.unsure:
                not_written.append(proposal)
                continue
            # Có thể Google đã thêm dòng: đọc lại xem Mã bài đã có chưa, không bao giờ thêm lại.
            present = _key_present(client, proposal.key)
            if present is True:
                written.append(proposal)
            elif present is False:
                not_written.append(proposal)
            else:
                unsure.append(proposal)
            continue
        written.append(proposal)
    return ApplyResult(tuple(written), tuple(conflicts), tuple(unsure), tuple(not_written), error)


def _addition(
    proposal: Proposal, fresh: SheetPlan, index: SiteIndex | None, stamp: str
) -> list[CellValue] | Conflict:
    """Các ô của dòng mới (theo cột của bản vừa đọc), hay ``Conflict``."""
    after = proposal.after
    if after.key in fresh.key_rows:
        return Conflict(proposal, CONFLICT_EXISTS.format(key=after.key))
    fields = [name for name, _ in SHEET_COLUMNS if _value(after, name) not in ("", None)]
    fields = [name for name in fields if name not in ("published_at", "updated_at")]
    if after.status == model.STATUS_NEW and "status" not in fresh.columns:
        fields.remove("status")  # ô Trạng thái trống là «Chưa viết»: không cần cột đó
    missing = [name for name in fields if name not in fresh.columns]
    if missing:
        return Conflict(proposal, CONFLICT_COLUMNS.format(columns=_labels(missing)), tuple(missing))
    cells = {fresh.columns[name]: to_cell(name, _value(after, name), index) for name in fields}
    if "updated_at" in fresh.columns:
        cells[fresh.columns["updated_at"]] = stamp
    row: list[CellValue] = [""] * (max(cells) + 1)
    for position, value in cells.items():
        row[position] = value
    return row


def _update(
    proposal: Proposal,
    base: SheetPlan,
    fresh: SheetPlan,
    index: SiteIndex | None,
    stamp: str,
) -> list[CellUpdate] | Conflict:
    """Các ô sẽ ghi cho «Cập nhật» / «Bỏ» (rỗng: Sheet đã đúng), hay ``Conflict``."""
    before = proposal.before
    original = base.locate(before) if before is not None else None
    if before is None or original is None:
        return Conflict(proposal, CONFLICT_UNKNOWN_ROW)
    changes = list(proposal.changes)
    missing = [name for name in changes if name not in fresh.columns]
    if missing:
        return Conflict(proposal, CONFLICT_COLUMNS.format(columns=_labels(missing)), tuple(missing))
    found = _fresh_row(before, original, base, fresh)
    if isinstance(found, str):
        return Conflict(proposal, found)
    number = found
    now_cells = fresh.cells_of(number)
    now_plan = fresh.plan_at(number)
    new_key = proposal.after.key
    if new_key and new_key != before.key and new_key in fresh.key_rows:  # mã mới cấp đã có
        return Conflict(proposal, CONFLICT_EXISTS.format(key=proposal.after.key), (), now_plan)
    wanted = {name: to_cell(name, _value(proposal.after, name), index) for name in changes}
    changed: list[str] = []
    applied = True
    for name in dict.fromkeys([*_ALWAYS_COMPARED, *changes]):
        old = _cell_at(original.cells, base.columns.get(name))
        new = _cell_at(now_cells, fresh.columns.get(name))
        if _same(old, new):
            if name in wanted and not _same(new, wanted[name]):
                applied = False
            continue
        if name in wanted and _same(new, wanted[name]):
            continue  # lần ghi trước (không rõ kết quả) đã ghi đúng ô này
        changed.append(name)
    if changed:
        fields = tuple(name for name in changed if name in FIELD_LABELS)
        return Conflict(proposal, CONFLICT_CHANGED.format(fields=_labels(fields)), fields, now_plan)
    if applied:
        return []
    cells = [CellUpdate(number, fresh.columns[name], value) for name, value in wanted.items()]
    if "updated_at" in fresh.columns:
        cells.append(CellUpdate(number, fresh.columns["updated_at"], stamp))
    return cells


def _fresh_row(before: PlanRow, original: SheetRow, base: SheetPlan, fresh: SheetPlan) -> int | str:
    """Số dòng trên bản vừa đọc ứng với dòng gốc, hay câu xung đột. Có mã: theo Mã bài (đúng một
    dòng). Chưa có mã: dòng chưa mã duy nhất có ô Từ khóa y như bản gốc."""
    if before.key:
        numbers = fresh.key_rows.get(before.key, ())
        if not numbers:
            return CONFLICT_MISSING
        if len(numbers) > 1:
            return CONFLICT_DUPLICATE.format(key=before.key)
        return numbers[0]
    key_cell = _cell_at(original.cells, base.columns.get("key"))
    keyword = _cell_at(original.cells, base.columns.get("keyword"))
    key_col, keyword_col = fresh.columns.get("key"), fresh.columns["keyword"]
    found = [
        number
        for number, cells in enumerate(fresh.values[1:], start=2)
        if not _key_of(cells, key_col)
        and _same(_cell_at(cells, key_col), key_cell)
        and _same(_cell_at(cells, keyword_col), keyword)
    ]
    if not found:
        return CONFLICT_MISSING
    if len(found) > 1:
        return CONFLICT_AMBIGUOUS
    return found[0]


def _batches(
    updates: list[tuple[Proposal, list[CellUpdate]]],
) -> list[list[tuple[Proposal, list[CellUpdate]]]]:
    """Gói các đề xuất thành lệnh ghi ≤ ``MAX_UPDATES`` ô; một đề xuất không bao giờ bị tách."""
    batches: list[list[tuple[Proposal, list[CellUpdate]]]] = []
    size = 0
    for item in updates:
        if not batches or size + len(item[1]) > MAX_UPDATES:
            batches.append([])
            size = 0
        batches[-1].append(item)
        size += len(item[1])
    return batches


def _key_present(client: SheetsLike, key: str) -> bool | None:
    """Mã bài ``key`` đã có trên Sheet chưa (đọc lại); đọc lỗi thì ``None`` (chưa rõ)."""
    try:
        values = client.read_plan_values()
    except SheetsError:
        return None
    return key in parse_sheet(values, fetched_at=_now()).key_rows


# ======================================================= ghi trạng thái sau khi gửi (1.6, 1.7)


class WriteOutcome(StrEnum):
    WRITTEN = "written"  # đã ghi
    ALREADY = "already"  # Sheet đã đúng (lần trước đã ghi)
    LATER = "later"  # dòng đã ở bước sau: không đổi (không lùi trạng thái)
    CONFLICT = "conflict"  # dòng đã khác lúc mở bài, không thấy, trùng mã, thiếu cột: không ghi
    FAILED = "failed"  # lỗi Google, mạng: chưa ghi, giữ việc còn nợ để thử lại
    UNSURE = "unsure"  # lệnh ghi lỗi giữa chừng: có thể đã ghi; thử lại sẽ đọc lại trước


@dataclass(frozen=True)
class StatusResult:
    outcome: WriteOutcome
    message: str

    @property
    def finished(self) -> bool:
        """Không cần thử lại nữa (đã ghi, đã đúng, hay không được ghi vì dòng đã khác)."""
        return self.outcome not in (WriteOutcome.FAILED, WriteOutcome.UNSURE)


def status_write(
    ref: DraftPlanRef,
    status: str,
    *,
    wp_post_id: int | None = None,
    published_at: datetime | None = None,
    now: datetime | None = None,
) -> PlanStatusWrite:
    """Việc ghi trạng thái cho dòng nháp ``ref`` gắn với (thiết kế 1.7): trạng thái mới, Mã bài
    WordPress, ngày đăng thực tế (giờ hẹn hay giờ đăng); kèm trạng thái, mã bài lúc mở bài."""
    return PlanStatusWrite(
        key=ref.key,
        sheet_hash=ref.sheet_hash,
        status=status,
        wp_post_id=wp_post_id,
        published_at=published_at,
        expect_status=ref.status,
        expect_post_id=ref.wp_post_id,
        created_at=now or _now(),
    )


def write_status(
    client: SheetsLike, write: PlanStatusWrite, *, now: datetime | None = None
) -> StatusResult:
    """Ghi tối đa 4 ô của dòng ``write.key`` (Trạng thái, Mã bài WordPress, Ngày đăng thực tế,
    Cập nhật lúc), có kiểm (thiết kế 1.7, 2.5 cuối; LC-T094-28, -30):

    - đọc lại Sheet; dòng theo Mã bài, đúng một dòng;
    - trạng thái hiện tại phải là trạng thái «trước» hợp lệ (``Chưa viết`` → ``Đang viết`` →
      ``Đã gửi nháp`` → ``Đã hẹn giờ`` → ``Đã đăng``) hay chính nó; ở bước sau thì không đổi
      (không bao giờ lùi); «Bỏ», chữ lạ: không ghi;
    - Mã bài WordPress hiện tại phải trống, bằng mã lúc mở bài, hay bằng mã sắp ghi.

    Không bao giờ ném ``SheetsError``: lỗi thành ``FAILED`` / ``UNSURE`` (giữ việc còn nợ)."""
    now = now or _now()
    try:
        fresh = read_sheet(client, now=now)
    except SheetsError as exc:
        return StatusResult(
            WriteOutcome.FAILED, STATUS_FAILED.format(key=write.key, error=str(exc))
        )
    columns = fresh.columns
    missing = [name for name in ("key", "status") if name not in columns]
    if missing:
        return _conflict(write, MSG_NO_COLUMNS.format(columns=_labels(missing)))
    numbers = fresh.key_rows.get(write.key, ())
    if not numbers:
        return _conflict(write, MSG_ROW_MISSING.format(key=write.key))
    if len(numbers) > 1:
        return _conflict(write, CONFLICT_DUPLICATE.format(key=write.key))
    number = numbers[0]
    cells = fresh.cells_of(number)
    status = _status_of(_cell_at(cells, columns["status"]))
    post_id = _post_id_of(_cell_at(cells, columns.get("wp_post_id")))
    if status is None or post_id is False:
        return _conflict(write, STATUS_CHANGED)
    known_posts = (None, write.expect_post_id, write.wp_post_id)
    if status == write.status and (write.wp_post_id is None or post_id == write.wp_post_id):
        return StatusResult(WriteOutcome.ALREADY, STATUS_ALREADY.format(key=write.key))
    if status in _STATUS_ORDER and _STATUS_ORDER.index(status) > _STATUS_ORDER.index(write.status):
        return StatusResult(WriteOutcome.LATER, STATUS_LATER.format(key=write.key))
    if status not in _STATUS_ORDER or post_id not in known_posts:
        return _conflict(write, STATUS_CHANGED)
    updates = [CellUpdate(number, columns["status"], write.status)]
    if write.wp_post_id is not None and "wp_post_id" in columns:
        updates.append(CellUpdate(number, columns["wp_post_id"], write.wp_post_id))
    if write.published_at is not None and "published_at" in columns:
        updates.append(
            CellUpdate(number, columns["published_at"], _moment_text(write.published_at))
        )
    if "updated_at" in columns:
        updates.append(CellUpdate(number, columns["updated_at"], _moment_text(now)))
    try:
        client.update_cells(updates)
    except SheetsError as exc:
        outcome = WriteOutcome.UNSURE if exc.unsure else WriteOutcome.FAILED
        template = STATUS_UNSURE if exc.unsure else STATUS_FAILED
        return StatusResult(outcome, template.format(key=write.key, error=str(exc)))
    return StatusResult(WriteOutcome.WRITTEN, STATUS_WRITTEN.format(key=write.key))


def record_status(
    client: SheetsLike | None,
    store: DraftStore,
    draft_id: str,
    write: PlanStatusWrite,
    *,
    now: datetime | None = None,
) -> StatusResult:
    """Sau khi gửi WordPress xong (thiết kế 1.7): **lưu việc ghi vào kho nháp trước**, rồi thử ghi
    Sheet; xong (hay không được ghi vì dòng đã khác) thì bỏ việc đó. ``client`` là ``None`` (chưa
    kết nối Google): chỉ lưu, thử lại sau. Lỗi kho nháp: ``DraftError``."""
    store.save_plan_write(draft_id, write)
    if client is None:
        return StatusResult(
            WriteOutcome.FAILED,
            STATUS_FAILED.format(key=write.key, error=MSG_NOT_CONNECTED),
        )
    result = write_status(client, write, now=now)
    if result.finished:
        store.save_plan_write(draft_id, None, expected=write)
    return result


@dataclass(frozen=True)
class RetryItem:
    draft_id: str
    key: str
    result: StatusResult


def retry_pending(
    client: SheetsLike, store: DraftStore, sheet_id: str, *, now: datetime | None = None
) -> tuple[RetryItem, ...]:
    """Thử lại các việc ghi trạng thái còn nợ của Sheet ``sheet_id`` (mở trang Kế hoạch / Bài
    viết, nút «Thử ghi lại»). **Chỉ** ghi Sheet, không bao giờ gửi lại WordPress; vẫn kiểm như
    ``write_status``. Việc xong thì bỏ (so rồi xóa: việc vừa bị thay ở tab khác thì giữ). Gặp lỗi
    Google, mạng thì dừng, để lần sau. Việc của Sheet khác (đổi ``GOOGLE_SHEET_ID``) giữ nguyên."""
    wanted = sheet_hash(sheet_id)
    items: list[RetryItem] = []
    for draft_id, write in store.list_plan_writes():
        if write.sheet_hash != wanted:
            continue
        result = write_status(client, write, now=now)
        if result.finished:
            # Không bỏ được: lần sau thử lại, kết quả là «đã đúng».
            with suppress(DraftError):
                store.save_plan_write(draft_id, None, expected=write)
        items.append(RetryItem(draft_id, write.key, result))
        if not result.finished:
            break
    return tuple(items)


def open_row(
    client: SheetsLike,
    key: str,
    *,
    index: SiteIndex | None = None,
    now: datetime | None = None,
) -> SheetRow:
    """Nút «Viết bài» (thiết kế 1.6, LC-T094-29): **đọc lại** Sheet, trả đúng dòng Mã bài ``key``
    (bản mới nhất) để điền sẵn Soạn bài. Không thấy, trùng mã, không đọc được: ``SheetPlanError``.
    Lỗi Google: ``SheetsError``."""
    fresh = read_sheet(client, index=index, now=now)
    numbers = fresh.key_rows.get(key, ())
    if not numbers:
        raise SheetPlanError(MSG_ROW_MISSING.format(key=key))
    if len(numbers) > 1:
        raise SheetPlanError(CONFLICT_DUPLICATE.format(key=key))
    row = fresh.find(key)
    if row is None or row.number != numbers[0]:
        raise SheetPlanError(MSG_ROW_UNREADABLE.format(key=key))
    return row


def plan_ref(row: SheetRow, sheet_id: str, *, now: datetime | None = None) -> DraftPlanRef:
    """``DraftSnapshot.plan`` cho nháp mở từ dòng ``row`` (thiết kế 1.6): Mã bài, mã băm Sheet,
    trạng thái và Mã bài WordPress lúc mở (để ghi trạng thái sau này có kiểm)."""
    return DraftPlanRef(
        key=row.plan.key,
        sheet_hash=sheet_hash(sheet_id),
        status=row.plan.status,
        wp_post_id=row.plan.wp_post_id,
        opened_at=now or _now(),
    )


def _conflict(write: PlanStatusWrite, reason: str) -> StatusResult:
    return StatusResult(WriteOutcome.CONFLICT, STATUS_CONFLICT.format(key=write.key, reason=reason))


def _status_of(value: CellValue) -> str | None:
    """Nhãn trạng thái chuẩn của ô (trống là «Chưa viết»); chữ lạ: ``None``."""
    try:
        label = model.match_label(_cell_text(value)[:100], model.STATUSES, model.STATUS_ALIASES)
    except ValueError:
        return None
    return label or model.STATUS_NEW


def _post_id_of(value: CellValue) -> int | None | bool:
    """Mã bài WordPress của ô (trống: ``None``); sai: ``False``."""
    text = clean_text(_cell_text(value)[:30])
    if not text:
        return None
    try:
        return parse._post_id(text)
    except ValueError:
        return False


# ============================================================== chuẩn bị trang tính (2.4)


@dataclass(frozen=True)
class PrepareResult:
    """Kết quả «Chuẩn bị trang tính». ``missing``: cột còn thiếu (tab đã có dữ liệu; chờ người dùng
    bấm «Thêm cột còn thiếu»); ``added``: cột vừa thêm tiêu đề ở cuối dòng 1."""

    created_tab: bool
    added: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()

    @property
    def message(self) -> str:
        parts = []
        if self.created_tab:
            parts.append("Đã tạo trang tính «KeHoach».")
        if self.added:
            parts.append(f"Đã thêm {len(self.added)} cột: {_labels(self.added)}.")
        if self.missing:
            parts.append(
                f"Trang tính còn thiếu {len(self.missing)} cột: {_labels(self.missing)}. Bấm «Thêm "
                "cột còn thiếu» để thêm vào cuối dòng tiêu đề (không dời cột có sẵn)."
            )
        parts.append("Đã cố định dòng tiêu đề, định dạng cột ngày và danh sách chọn.")
        return " ".join(parts)


def prepare_sheet(client: SheetsLike, *, add_missing: bool = False) -> PrepareResult:
    """Nút «Chuẩn bị trang tính» (chỉ khi người dùng bấm; thiết kế 2.4, LC-T094-31).

    Chưa có tab «KeHoach» (tên đúng từng chữ): tạo tab, ghi cả dòng tiêu đề. Có rồi mà dòng 1 trống:
    ghi cả dòng tiêu đề. Có rồi mà thiếu cột: báo thiếu (``missing``); ``add_missing`` (nút «Thêm
    cột còn thiếu») thì ghi tiêu đề vào **cuối** dòng 1, sau ô có chữ cuối cùng (không dời, không
    ghi đè cột có sẵn). Sau đó: cố định dòng 1, định dạng cột ngày, cột giờ là chữ, danh sách chọn
    (hằng của code) cho Ý định, Loại trang, Ưu tiên, Trạng thái. Chỉ 4 loại yêu cầu của thiết kế,
    trên đúng tab vừa đọc (client kiểm lại). Lỗi: ``SheetsError``, ``SheetPlanError``."""
    info = client.get_info()
    created = False
    if info.plan_tab is None:
        client.batch_update(
            [{"addSheet": {"properties": {"title": PLAN_TAB, "gridProperties": {
                "frozenRowCount": 1}}}}]
        )  # fmt: skip
        created = True
        info = client.get_info()  # client bắt đọc lại sau mỗi lệnh sửa cấu trúc
        if info.plan_tab is None:
            raise SheetPlanError(MSG_TAB_NOT_CREATED)
        header: tuple[CellValue, ...] = ()
    else:
        values = client.read_plan_values()
        header = tuple(values[0]) if values else ()
    texts = [_cell_text(cell) for cell in header]
    columns, _ = parse._header_map(texts)
    columns = dict(columns)
    missing = [name for name, _ in SHEET_COLUMNS if name not in columns]
    filled = len(texts)
    while filled and not texts[filled - 1].strip():
        filled -= 1
    added: list[str] = []
    if missing and (created or add_missing or not filled):
        if filled + len(missing) > MAX_COLUMNS:
            raise SheetPlanError(MSG_NO_ROOM.format(count=len(missing)))
        client.update_cells(
            [CellUpdate(1, filled + i, FIELD_LABELS[name]) for i, name in enumerate(missing)]
        )
        columns.update({name: filled + i for i, name in enumerate(missing)})
        added, missing = missing, []
    client.batch_update(_format_requests(info.plan_tab.sheet_id, columns))
    return PrepareResult(created, tuple(added), tuple(missing))


def _format_requests(sheet_id: int, columns: Mapping[str, int]) -> list[dict[str, Any]]:
    def data_range(position: int) -> dict[str, int]:
        return {
            "sheetId": sheet_id,
            "startRowIndex": 1,  # bỏ dòng tiêu đề
            "endRowIndex": MAX_ROWS,
            "startColumnIndex": position,
            "endColumnIndex": position + 1,
        }

    requests_: list[dict[str, Any]] = [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        }
    ]
    formats = {
        "planned_date": {"type": "DATE", "pattern": _DATE_PATTERN},
        "planned_time": {"type": "TEXT"},  # «08:00» giữ là chữ, không thành số giờ
    }
    for name, number_format in formats.items():
        if name in columns:
            requests_.append(
                {
                    "repeatCell": {
                        "range": data_range(columns[name]),
                        "cell": {"userEnteredFormat": {"numberFormat": number_format}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                }
            )
    for name, choices in _CHOICES.items():
        if name in columns:
            requests_.append(
                {
                    "setDataValidation": {
                        "range": data_range(columns[name]),
                        "rule": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [{"userEnteredValue": choice} for choice in choices],
                            },
                            "strict": False,  # gõ cách gọi khác vẫn được (app đọc cả tên gọi khác)
                            "showCustomUi": True,
                        },
                    }
                }
            )
    return requests_


# =========================================================================== chuyển giá trị


def safe_text(text: str) -> str:
    """Chữ ghi lên Sheet: bắt đầu bằng ``=``, ``+``, ``-``, ``@``, tab, CR thì thêm một dấu cách
    đầu (file tải về mở bằng Excel không thành công thức, LC-T094-28); không còn chỗ (ô tối đa
    ``SHEET_CELL_CHARS`` ký tự) thì bỏ các ký tự đó ở đầu."""
    if not text.startswith(_FORMULA_START):
        return text
    if len(text) < SHEET_CELL_CHARS:
        return " " + text
    return text.lstrip("".join(_FORMULA_START))


def to_cell(name: str, value: object, index: SiteIndex | None = None) -> CellValue:
    """Giá trị trường ``name`` của ``PlanRow`` thành ô ghi ``RAW``: ngày dự kiến là số ngày của
    Sheets (vẫn là ô ngày thật), mã bài là số, thời điểm là chữ giờ Việt Nam có ``+07:00``, trang
    đích là link của bài trong danh sách bài đã đăng (không có thì mã bài); còn lại là chữ đã qua
    ``safe_text``."""
    if value is None or value == "":
        return ""
    if name == "planned_date" and isinstance(value, date):
        return (value - _SHEETS_EPOCH).days
    if name in ("published_at", "updated_at") and isinstance(value, datetime):
        return _moment_text(value)
    if name == "target_id" and isinstance(value, int):
        link = next((item.link for item in index.items if item.id == value), "") if index else ""
        return safe_text(link) if link else value
    if name == "wp_post_id" and isinstance(value, int):
        return value
    return safe_text(str(value))


def _value(row: PlanRow, name: str) -> object:
    return getattr(row, name)


def _moment_text(moment: datetime) -> str:
    """Giờ Việt Nam ghi rõ múi giờ: ``2026-11-03 08:00+07:00`` (``parse_plan_datetime`` đọc lại
    được). Giờ không múi giờ là lỗi lập trình."""
    if moment.tzinfo is None:
        raise ValueError("thời điểm phải có múi giờ")
    return moment.astimezone(model.TIMEZONE).isoformat(sep=" ", timespec="minutes")


def _cell_text(value: CellValue, name: str | None = None) -> str:
    """Ô Google trả (``UNFORMATTED_VALUE``) thành chữ cho bộ đọc bảng. Số nguyên viết không có
    ``.0``; ô giờ là số (Sheets tự đổi «08:00» thành phần của ngày) thì thành ``HH:MM``."""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if name == "planned_time" and 0 <= value < 1:
            minutes = min(round(value * 24 * 60), 24 * 60 - 1)
            return f"{minutes // 60:02d}:{minutes % 60:02d}"
        return str(int(value)) if value.is_integer() and abs(value) < 2**53 else repr(value)
    return value if isinstance(value, str) else ""


def _cell_at(cells: Sequence[CellValue], position: int | None) -> CellValue:
    if position is None or position >= len(cells):
        return ""
    return cells[position]


def _same(first: CellValue, second: CellValue) -> bool:
    """Hai ô như nhau (ô trống và ô thiếu là một; ``True`` khác ``1``)."""
    if first == "" or second == "":
        return first == second
    return (
        type(first) is type(second)
        and first == second
        or (
            isinstance(first, int | float)
            and isinstance(second, int | float)
            and not isinstance(first, bool)
            and not isinstance(second, bool)
            and first == second
        )
    )


def _key_of(cells: Sequence[CellValue], position: int | None) -> str:
    """Mã bài (đã chuẩn hóa) của ô Mã bài; trống hay sai dạng: ``""``."""
    text = _cell_text(_cell_at(cells, position))[:30]
    try:
        return model.parse_key(text)
    except ValueError:
        return ""


def _labels(names: Sequence[str]) -> str:
    return ", ".join(f"«{FIELD_LABELS[name]}»" for name in names)


def _now() -> datetime:
    return datetime.now(model.TIMEZONE)


__all__ = [
    "ApplyResult",
    "Conflict",
    "PlanListing",
    "PrepareResult",
    "RetryItem",
    "SheetPlan",
    "SheetPlanError",
    "SheetRow",
    "SheetsLike",
    "StatusResult",
    "WriteOutcome",
    "apply_proposals",
    "get_plan",
    "open_row",
    "parse_sheet",
    "plan_ref",
    "prepare_sheet",
    "read_sheet",
    "record_status",
    "retry_pending",
    "safe_text",
    "status_write",
    "to_cell",
    "write_status",
]

"""Cập nhật trạng thái kế hoạch từ website (T-109; thiết kế T-094 mục 1.7 «Đồng bộ từ WordPress»).

Hai bước, để giao diện cho người dùng xem rồi mới bấm ghi:

- ``check_website`` (thuần, không mạng): so kết quả ``WordPressClient.post_statuses`` với các dòng
  kế hoạch đã nối bài (cột «Mã bài WordPress», T-100), trả ``WebCheck``: các thay đổi đề xuất
  (``WebUpdate``: dòng nào, ô nào, cũ → mới, lý do) và các cảnh báo không ghi gì (``WebNotice``:
  lỡ lịch, bài không còn thấy, bài về nháp…). Chỉ đi **tới** (``Chưa viết`` → ``Đang viết`` →
  ``Đã gửi nháp`` → ``Đã hẹn giờ`` → ``Đã đăng``), không bao giờ lùi trạng thái; dòng «Bỏ», dòng
  chưa có Mã bài, Mã bài trùng, một bài nối nhiều dòng: chỉ cảnh báo.
- ``apply_website_changes``: ghi các thay đổi người dùng đã chọn qua đúng đường ghi của T-100:
  so mã băm Sheet (Sheet đang nối phải là Sheet đã xem), **đọc lại** cả tab, tìm dòng theo Mã bài,
  so từng ô sắp ghi với bản đã xem (khác thì không ghi dòng đó), ghi ``RAW`` chỉ các ô Trạng thái,
  Ngày đăng thực tế, Cập nhật lúc trong lệnh ``update_cells`` (không thêm dòng, không xóa gì).
  Lệnh ghi lỗi giữa chừng (``unsure``): không tự ghi lại; lần sau đọc lại rồi so như trên.

Dữ liệu website và Sheet là dữ liệu chưa tin cậy (LC-T094 «Chung»): trạng thái website chỉ nhận
5 giá trị đã biết, giờ ``date_gmt`` đúng khuôn và trong khoảng năm của kế hoạch; mục sai khuôn coi
như không thấy. Câu báo là câu cố định (LC-T094-2): chỉ nêu Mã bài, mã bài WordPress (số), số dòng,
nhãn trạng thái chuẩn và giờ do app định dạng; không chép chữ ô Sheet hay lời website. Giá trị ghi
lên Sheet là nhãn trạng thái của code và giờ do app dựng, nên không thể thành công thức
(LC-T101-1, LC-T094-28).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING

from seo_app.google.sheets import MAX_UPDATES, CellUpdate, CellValue, SheetsError
from seo_app.plan import model
from seo_app.plan.sync import (
    CONFLICT_DUPLICATE,
    MSG_NO_COLUMNS,
    MSG_ROW_MISSING,
    MSG_ROW_UNREADABLE,
    SheetPlan,
    SheetPlanError,
    SheetsLike,
    _cell_at,
    _connected_hash,
    _labels,
    _moment_text,
    _now,
    _post_id_of,
    _reader_text,
    _status_of,
    read_sheet,
    to_cell,
)
from seo_app.storage.plan_cache import sheet_hash
from seo_app.wordpress.client import POST_STATUSES

if TYPE_CHECKING:
    from seo_app.wordpress.client import PostState

# Bài hẹn giờ quá giờ chừng này mà website vẫn báo ``future``: «Lỡ lịch» (thiết kế 1.7, 3.1).
LATE_AFTER = timedelta(minutes=15)
# Lần kiểm dùng để ghi tối đa chừng này phút (G4 của Soi Lỗi, điều kiện 1c của Lá Chắn T-109):
# cũ hơn thì website có thể đã đổi (bài về nháp…), phải kiểm lại rồi mới ghi.
CHECK_MAX_AGE = timedelta(minutes=5)
# Giờ trên Sheet lệch giờ website chừng này coi như cùng giờ (G6): «Đăng ngay» ghi giờ máy lúc
# nhận trả lời, đồng hồ máy được lệch website tới 2 phút (thiết kế T-094 mục 3.1).
DATE_TOLERANCE = timedelta(minutes=2)
_DATE_GMT = "%Y-%m-%dT%H:%M:%S"
_ORDER = (
    model.STATUS_NEW,
    model.STATUS_WRITING,
    model.STATUS_DRAFT_SENT,
    model.STATUS_SCHEDULED,
    model.STATUS_PUBLISHED,
)
# Trạng thái website → trạng thái kế hoạch tương ứng (``private`` không có: chỉ cảnh báo).
_PLAN_STATUS = {
    "draft": model.STATUS_DRAFT_SENT,
    "pending": model.STATUS_DRAFT_SENT,
    "future": model.STATUS_SCHEDULED,
    "publish": model.STATUS_PUBLISHED,
}
_WEB_LABELS = {
    "draft": "bản nháp",
    "pending": "chờ duyệt",
    "future": "hẹn giờ",
    "publish": "đã đăng",
    "private": "riêng tư",
}

REASON_DRAFT = "Bài #{post} đã có bản nháp trên website."
REASON_SCHEDULED = "Bài #{post} đang hẹn giờ trên website{at}."
REASON_PUBLISHED = "Bài #{post} đã đăng trên website{at}."
REASON_DATE = "Giờ đăng của bài #{post} trên website là {at}, khác ô «Ngày đăng thực tế»."

NOTICE_LATE = (
    "Lỡ lịch: bài #{post} (dòng {key}) hẹn giờ lúc {at} đã quá giờ mà chưa lên. WordPress chỉ đăng "
    "bài hẹn giờ khi có người vào website; nhờ người làm web bật lịch chạy thật (cron) trên "
    "hosting, hoặc mở bài trong trang quản trị WordPress rồi bấm Đăng."
)
NOTICE_MISSING = (
    "Không thấy bài #{post} (dòng {key}) trên website: bài đã bị xóa, đang trong thùng rác, hoặc "
    "tài khoản của phần mềm không còn quyền xem. Phần mềm không tự sửa Google Sheet."
)
NOTICE_BACK_TO_DRAFT = (
    "Bài #{post} (dòng {key}) đang là {web} trên website trong khi Google Sheet ghi «{status}». "
    "Phần mềm không tự sửa Google Sheet."
)
NOTICE_AHEAD = (
    "Bài #{post} (dòng {key}) đang hẹn giờ trên website trong khi Google Sheet ghi «Đã đăng». "
    "Phần mềm không tự sửa Google Sheet."
)
NOTICE_PRIVATE = (
    "Bài #{post} (dòng {key}) đang để riêng tư trên website: khách không xem được. Phần mềm không "
    "tự sửa Google Sheet."
)
NOTICE_DROPPED = (
    "Dòng {key} ghi «Bỏ» nhưng bài #{post} vẫn còn trên website ({web}). Phần mềm không tự sửa "
    "Google Sheet."
)
NOTICE_SHARED_POST = (
    "Mã bài WordPress {post} có ở nhiều dòng trên Google Sheet nên chưa đề xuất gì cho các dòng đó."
)
NOTICE_DUPLICATE_KEY = "Mã bài {key} có ở nhiều dòng trên Google Sheet nên chưa đề xuất gì."
NOTICE_NO_KEY = (
    "Dòng {number} có Mã bài WordPress {post} nhưng chưa có Mã bài nên chưa đề xuất gì (thêm "
    "Mã bài cho dòng đó trước)."
)
NOTICE_ODD_DATE = (
    "Giờ đăng của bài #{post} (dòng {key}) trên website không đọc được nên không ghi ô «Ngày đăng "
    "thực tế»."
)

NOTICE_ODD_CELL = (
    "Ô «{field}» của dòng {key} trên Google Sheet không đọc được nên chưa đề xuất gì cho bài "
    "#{post}. Sửa ô đó cho đúng (ví dụ «Đã hẹn giờ», «03/11/2026 08:00») rồi kiểm lại."
)
NOTICE_UNSURE_ROW = (
    "Không xác định được đúng một dòng cho Mã bài {key} trên Google Sheet nên chưa đề xuất gì."
)
MSG_STALE = (
    "Lần kiểm trạng thái đã cũ (quá 5 phút) nên chưa ghi gì: bấm «Cập nhật trạng thái từ "
    "website» lại rồi ghi."
)
MSG_OTHER_SHEET = (
    "Google Sheet đang kết nối khác Sheet lúc kiểm trạng thái (có thể vừa đổi trong Cài đặt) nên "
    "chưa ghi gì. Bấm «Cập nhật trạng thái từ website» lại."
)
MSG_NOT_IN_CHECK = "thay đổi không thuộc lần kiểm này"
CONFLICT_CHANGED = "Dòng vừa bị sửa ở nơi khác ({fields}) nên chưa ghi."
CONFLICT_FULL = (
    "Không thấy dòng này trong 1.000 dòng đầu của Google Sheet (phần mềm chỉ đọc tới đó) nên chưa "
    "ghi."
)


class WebChangeKind(StrEnum):
    DRAFT = "draft"  # dòng chưa gửi mà bài đã có nháp: → «Đã gửi nháp»
    SCHEDULED = "scheduled"  # bài đang hẹn giờ (kể cả tự hẹn trong trang quản trị): → «Đã hẹn giờ»
    PUBLISHED = "published"  # bài đã lên: → «Đã đăng»
    DATE = "date"  # trạng thái đã đúng, chỉ «Ngày đăng thực tế» khác giờ trên website


class WebNoticeKind(StrEnum):
    LATE = "late"  # «Lỡ lịch»
    MISSING = "missing"  # không thấy: xóa, thùng rác, không còn quyền xem
    BACK_TO_DRAFT = "back_to_draft"  # website là nháp mà Sheet đã ở «Đã hẹn giờ»/«Đã đăng»
    AHEAD = "ahead"  # Sheet «Đã đăng» mà website còn hẹn giờ
    PRIVATE = "private"
    DROPPED = "dropped"  # Sheet «Bỏ» mà bài vẫn còn trên website
    SHARED_POST = "shared_post"  # một mã bài WordPress ở nhiều dòng
    DUPLICATE_KEY = "duplicate_key"
    NO_KEY = "no_key"
    ODD_DATE = "odd_date"
    ODD_CELL = "odd_cell"  # ô Trạng thái / Ngày đăng thực tế gõ chữ không đọc được (SL-T109-3)
    UNSURE_ROW = "unsure_row"  # Mã bài không ứng đúng một dòng (SL-T109-1)


@dataclass(frozen=True)
class WebUpdate:
    """Một thay đổi đề xuất cho dòng ``key`` (đúng một dòng nối bài ``wp_post_id``). ``*_before``:
    giá trị người dùng đang thấy (đã qua ``PlanRow``), dùng để so khi ghi; ``reason``: câu cố
    định. ``row_number`` chỉ để hiện: lúc ghi tìm dòng theo Mã bài."""

    kind: WebChangeKind
    key: str
    wp_post_id: int
    row_number: int
    status_before: str
    status_after: str
    published_before: datetime | None
    published_after: datetime | None
    reason: str

    @property
    def fields(self) -> tuple[str, ...]:
        """Các trường đổi (``status``, ``published_at``)."""
        names = []
        if self.status_after != self.status_before:
            names.append("status")
        if not _same_moment(self.published_after, self.published_before):
            names.append("published_at")
        return tuple(names)

    @property
    def label(self) -> str:
        return f"{self.key} (bài #{self.wp_post_id})"


@dataclass(frozen=True)
class WebNotice:
    kind: WebNoticeKind
    message: str
    key: str = ""
    wp_post_id: int | None = None


@dataclass(frozen=True)
class WebCheck:
    """Kết quả kiểm: đề xuất ghi, cảnh báo, mã băm Sheet đã xem (ghi chỉ vào đúng Sheet đó)."""

    updates: tuple[WebUpdate, ...]
    notices: tuple[WebNotice, ...]
    sheet_hash: str
    checked_at: datetime

    @property
    def late(self) -> tuple[WebNotice, ...]:
        return tuple(n for n in self.notices if n.kind is WebNoticeKind.LATE)


def check_website(
    plan: SheetPlan,
    states: Mapping[int, PostState],
    asked: Iterable[int],
    *,
    sheet_id: str,
    now: datetime | None = None,
) -> WebCheck:
    """So trạng thái website với kế hoạch (thuần, không mạng).

    ``states``: kết quả ``post_statuses(asked)``; ``asked``: các mã đã hỏi (mã đã hỏi mà không có
    trong ``states`` là bài không còn thấy). ``sheet_id``: Sheet của ``plan`` (lưu mã băm để khi ghi
    so với Sheet đang nối). Chỉ xét dòng có Mã bài WordPress nằm trong ``asked``."""
    if not isinstance(sheet_id, str) or not sheet_id:
        raise ValueError("cần mã Google Sheet")
    now = now or _now()
    if now.tzinfo is None:
        raise ValueError("thời điểm phải có múi giờ")
    missing = [name for name in ("key", "status", "wp_post_id") if name not in plan.columns]
    if missing:  # G5: báo ngay lúc kiểm, không đề xuất «Chưa viết → …» rồi mới báo lúc ghi
        raise SheetPlanError(MSG_NO_COLUMNS.format(columns=_labels(missing)))
    asked_ids = {value for value in asked if _is_post_id(value)}
    known = _known_states(states, asked_ids)
    shared = {post for post, count in _post_counts(plan).items() if count > 1}
    updates: list[WebUpdate] = []
    notices: list[WebNotice] = []
    noted_shared: set[int] = set()
    duplicates = plan.duplicate_keys
    for sheet_row in plan.rows:
        row = sheet_row.plan
        post = row.wp_post_id
        if post is None or post not in asked_ids:
            continue
        if not row.key:
            notices.append(_notice(WebNoticeKind.NO_KEY, NOTICE_NO_KEY, "", post,
                                   number=sheet_row.number))  # fmt: skip
            continue
        if row.key in duplicates:
            notices.append(
                _notice(WebNoticeKind.DUPLICATE_KEY, NOTICE_DUPLICATE_KEY, row.key, post)
            )
            continue
        if plan.key_rows.get(row.key) != (sheet_row.number,):
            # Bộ đọc bảng và cách tìm dòng lúc ghi không ra cùng một dòng (SL-T109-1).
            notices.append(_notice(WebNoticeKind.UNSURE_ROW, NOTICE_UNSURE_ROW, row.key, post))
            continue
        if post in shared:
            if post not in noted_shared:
                noted_shared.add(post)
                notices.append(_notice(WebNoticeKind.SHARED_POST, NOTICE_SHARED_POST, "", post))
            continue
        # Đọc ô Trạng thái, Ngày đăng thực tế bằng đúng hàm lúc ghi (SL-T109-3): ô không đọc được
        # thì chỉ cảnh báo (bộ đọc bảng coi là trống, lúc ghi lại coi là «đã khác»).
        status = _status_of(_cell_at(sheet_row.cells, plan.columns["status"]))
        published = _moment_of(_cell_at(sheet_row.cells, plan.columns.get("published_at")))
        state = known.get(post)
        if state is None:
            if status != model.STATUS_DROPPED:  # G3: dòng «Bỏ» mà bài đã xóa: không cần báo
                notices.append(_notice(WebNoticeKind.MISSING, NOTICE_MISSING, row.key, post))
            continue
        bad = "status" if status is None else "published_at" if published is False else ""
        if bad:
            field = model.FIELD_LABELS[bad]
            notices.append(
                _notice(WebNoticeKind.ODD_CELL, NOTICE_ODD_CELL, row.key, post, field=field)
            )
            continue
        web_status, due, odd_date = state
        update, notice = _compare(sheet_row.number, row.key, post, status, published,
                                  web_status, due)  # fmt: skip
        if update is not None:
            updates.append(update)
        if notice is not None:
            notices.append(notice)
        # G6 (Chỉ Huy duyệt 31/10): bài hẹn giờ / đã đăng mà website không cho giờ
        # (``post_statuses`` đổi giờ sai khuôn thành rỗng) cũng là giờ lạ. Dòng chỉ có cảnh báo
        # («Bỏ», riêng tư…) thì không báo thêm.
        odd_date = odd_date or due is None
        if odd_date and web_status in ("future", "publish") and notice is None:
            notices.append(_notice(WebNoticeKind.ODD_DATE, NOTICE_ODD_DATE, row.key, post))
        if web_status == "future" and due is not None and now - due > LATE_AFTER:
            notices.append(_notice(WebNoticeKind.LATE, NOTICE_LATE, row.key, post, at=due))
    return WebCheck(tuple(updates), tuple(notices), sheet_hash(sheet_id), now)


def _compare(
    number: int,
    key: str,
    post: int,
    status: str,
    before: datetime | None,
    web_status: str,
    due: datetime | None,
) -> tuple[WebUpdate | None, WebNotice | None]:
    """Một dòng (đã nối bài ``post``; ``status``, ``before``: ô Trạng thái, Ngày đăng thực tế đọc
    như lúc ghi) → thay đổi đề xuất và/hoặc cảnh báo."""
    web = _WEB_LABELS[web_status]
    if status == model.STATUS_DROPPED:
        return None, _notice(WebNoticeKind.DROPPED, NOTICE_DROPPED, key, post, web=web)
    if web_status == "private":
        return None, _notice(WebNoticeKind.PRIVATE, NOTICE_PRIVATE, key, post)
    target = _PLAN_STATUS[web_status]
    here, there = _ORDER.index(status), _ORDER.index(target)
    if here > there:
        if web_status == "future":
            return None, _notice(WebNoticeKind.AHEAD, NOTICE_AHEAD, key, post)
        return None, _notice(
            WebNoticeKind.BACK_TO_DRAFT, NOTICE_BACK_TO_DRAFT, key, post, web=web, status=status
        )
    after = before
    if web_status in ("future", "publish") and due is not None and not _close(due, before):
        after = due
    if here < there:
        kind = {
            model.STATUS_DRAFT_SENT: WebChangeKind.DRAFT,
            model.STATUS_SCHEDULED: WebChangeKind.SCHEDULED,
            model.STATUS_PUBLISHED: WebChangeKind.PUBLISHED,
        }[target]
    elif not _same_moment(after, before):
        kind = WebChangeKind.DATE
    else:
        return None, None
    at = _time_text(due) if due is not None else ""
    if kind is WebChangeKind.DATE:
        reason = REASON_DATE.format(post=post, at=at)
    else:
        template = {
            WebChangeKind.DRAFT: REASON_DRAFT,
            WebChangeKind.SCHEDULED: REASON_SCHEDULED,
            WebChangeKind.PUBLISHED: REASON_PUBLISHED,
        }[kind]
        reason = template.format(post=post, at=f" lúc {at}" if at else "")
    update = WebUpdate(kind, key, post, number, status, target if here < there else status,
                       before, after, reason)  # fmt: skip
    return update, None


# ================================================================================ ghi


@dataclass(frozen=True)
class WebConflict:
    update: WebUpdate
    reason: str


@dataclass(frozen=True)
class WebApplyResult:
    """Kết quả ghi. ``already``: Sheet đã đúng (lần ghi trước, hay máy khác vừa ghi); ``unsure``:
    lệnh ghi lỗi giữa chừng, có thể đã ghi (không tự ghi lại: kiểm lại rồi mới ghi tiếp);
    ``not_written``: chưa ghi vì lỗi (``error``)."""

    written: tuple[WebUpdate, ...] = ()
    already: tuple[WebUpdate, ...] = ()
    conflicts: tuple[WebConflict, ...] = ()
    unsure: tuple[WebUpdate, ...] = ()
    not_written: tuple[WebUpdate, ...] = ()
    error: str = ""

    @property
    def message(self) -> str:
        parts: list[str] = []
        if self.written:
            parts.append(f"Đã cập nhật {len(self.written)} dòng trên Google Sheet.")
        if self.already:
            parts.append(f"{len(self.already)} dòng đã đúng sẵn.")
        if self.conflicts:
            shown = ", ".join(c.update.label for c in self.conflicts[:5])
            more = ", …" if len(self.conflicts) > 5 else ""
            parts.append(
                f"{len(self.conflicts)} dòng chưa ghi vì trên Google Sheet đã khác bản đã xem: "
                f"{shown}{more}."
            )
        if self.unsure:
            parts.append(
                f"{len(self.unsure)} dòng chưa rõ đã ghi chưa (lỗi giữa chừng): bấm «Cập nhật "
                "trạng thái từ website» lại để kiểm trước khi ghi tiếp."
            )
        if self.error:
            parts.append(self.error)
        if self.not_written:
            parts.append(f"{len(self.not_written)} dòng chưa ghi.")
        return " ".join(parts) or "Không có thay đổi nào để ghi."


def apply_website_changes(
    client: SheetsLike,
    check: WebCheck,
    updates: Sequence[WebUpdate] | None = None,
    *,
    sheet_id: str,
    now: datetime | None = None,
) -> WebApplyResult:
    """Ghi các thay đổi ``updates`` (mặc định: mọi thay đổi của ``check``) lên Sheet.

    ``updates`` phải là thay đổi của chính ``check`` (giao diện không tự dựng ``WebUpdate``):
    khác thì ``ValueError``, chưa ghi gì. Sheet đang nối (``client.sheet_hash``, ``sheet_id``) khác
    Sheet đã kiểm: ``SheetPlanError``, chưa đọc, chưa ghi. Lỗi đọc lại: ``SheetsError``; tab thiếu
    cột Mã bài, Trạng thái, Mã bài WordPress: ``SheetPlanError`` (cả hai: chưa ghi gì)."""
    chosen = check.updates if updates is None else tuple(updates)
    if any(update not in check.updates for update in chosen) or len(set(chosen)) != len(chosen):
        raise ValueError(MSG_NOT_IN_CHECK)
    if _connected_hash(client, sheet_id) != check.sheet_hash:
        raise SheetPlanError(MSG_OTHER_SHEET)
    if not chosen:
        return WebApplyResult()
    now = now or _now()
    age = now - check.checked_at
    if age > CHECK_MAX_AGE or age < -timedelta(minutes=1):  # G4; giờ máy lùi cũng coi là cũ
        raise SheetPlanError(MSG_STALE)
    fresh = read_sheet(client, now=now)
    missing = [name for name in ("key", "status", "wp_post_id") if name not in fresh.columns]
    if missing:
        raise SheetPlanError(MSG_NO_COLUMNS.format(columns=_labels(missing)))
    stamp = _moment_text(now)
    planned: list[tuple[WebUpdate, list[CellUpdate]]] = []
    already: list[WebUpdate] = []
    conflicts: list[WebConflict] = []
    for update in chosen:
        result = _cells_for(update, fresh, stamp)
        if isinstance(result, WebConflict):
            conflicts.append(result)
        elif result:
            planned.append((update, result))
        else:
            already.append(update)
    written: list[WebUpdate] = []
    unsure: list[WebUpdate] = []
    not_written: list[WebUpdate] = []
    error = ""
    for batch in _batches(planned):
        if error:
            not_written.extend(update for update, _ in batch)
            continue
        try:
            client.update_cells([cell for _, cells in batch for cell in cells])
        except SheetsError as exc:
            error = str(exc)
            (unsure if exc.unsure else not_written).extend(update for update, _ in batch)
            continue
        written.extend(update for update, _ in batch)
    return WebApplyResult(
        tuple(written), tuple(already), tuple(conflicts), tuple(unsure), tuple(not_written), error
    )


def _cells_for(update: WebUpdate, fresh: SheetPlan, stamp: str) -> list[CellUpdate] | WebConflict:
    """Các ô ghi cho ``update`` trên bản vừa đọc lại; ``[]``: Sheet đã đúng; ``WebConflict``: dòng
    không còn, trùng mã, hay đã khác bản người dùng đã xem."""
    columns = fresh.columns
    numbers = fresh.key_rows.get(update.key, ())
    if not numbers:
        return WebConflict(update, CONFLICT_FULL if fresh.full else
                           MSG_ROW_MISSING.format(key=update.key))  # fmt: skip
    if len(numbers) > 1:
        return WebConflict(update, CONFLICT_DUPLICATE.format(key=update.key))
    number = numbers[0]
    # Dòng tìm được phải đúng là dòng bộ đọc bảng nhận cho Mã bài này (như ``sync.open_row``,
    # SL-T109-1): khác thì không biết người dùng đã xem dòng nào, không ghi.
    seen = fresh.find(update.key)
    if seen is None:
        return WebConflict(update, MSG_ROW_UNREADABLE.format(key=update.key))
    if seen.number != number:
        return WebConflict(update, CONFLICT_DUPLICATE.format(key=update.key))
    cells = fresh.cells_of(number)
    status = _status_of(_cell_at(cells, columns["status"]))
    post = _post_id_of(_cell_at(cells, columns["wp_post_id"]))
    published = _moment_of(_cell_at(cells, columns.get("published_at")))
    changed: list[str] = []
    if post != update.wp_post_id:
        changed.append("wp_post_id")
    if status != update.status_before:
        changed.append("status")
    if published is False or not _same_moment(published, update.published_before):
        changed.append("published_at")
    if (
        "wp_post_id" not in changed
        and status == update.status_after
        and published is not False
        and _same_moment(published, update.published_after)
    ):
        return []
    if changed:
        return WebConflict(update, CONFLICT_CHANGED.format(fields=_labels(changed)))
    writes: list[CellUpdate] = []
    if update.status_after != update.status_before:
        writes.append(CellUpdate(number, columns["status"], to_cell("status", update.status_after)))
    if "published_at" in update.fields and update.published_after is not None:
        if "published_at" in columns:
            moment = _moment_text(update.published_after)
            writes.append(CellUpdate(number, columns["published_at"], moment))
        elif not writes:  # chỉ đổi ngày mà trang tính không có cột đó
            return WebConflict(update, MSG_NO_COLUMNS.format(columns=_labels(["published_at"])))
    if not writes:
        return []
    if "updated_at" in columns:
        writes.append(CellUpdate(number, columns["updated_at"], stamp))
    return writes


def _batches(
    planned: list[tuple[WebUpdate, list[CellUpdate]]],
) -> list[list[tuple[WebUpdate, list[CellUpdate]]]]:
    """Gói thành lệnh ghi ≤ ``MAX_UPDATES`` ô; các ô của một dòng không bao giờ bị tách."""
    batches: list[list[tuple[WebUpdate, list[CellUpdate]]]] = []
    size = 0
    for item in planned:
        if not batches or size + len(item[1]) > MAX_UPDATES:
            batches.append([])
            size = 0
        batches[-1].append(item)
        size += len(item[1])
    return batches


# ============================================================================ phụ trợ


def _is_post_id(value: object) -> bool:
    return type(value) is int and 0 < value <= model.MAX_POST_ID


def _known_states(
    states: Mapping[int, PostState], asked: set[int]
) -> dict[int, tuple[str, datetime | None, bool]]:
    """Mục website dùng được: mã đã hỏi, đúng mã của mục, trạng thái đã biết. Giá trị: (trạng thái,
    giờ đăng / giờ hẹn UTC hay ``None``, giờ có mà sai khuôn hay ngoài khoảng năm). Mục sai khuôn bị
    bỏ (coi như không thấy)."""
    known: dict[int, tuple[str, datetime | None, bool]] = {}
    try:
        items = list(states.items())
    except (AttributeError, TypeError):
        return known
    for post, state in items:
        if not _is_post_id(post) or post not in asked:
            continue
        status = getattr(state, "status", None)
        if getattr(state, "id", None) != post or type(status) is not str:
            continue
        if status not in POST_STATUSES or status not in _WEB_LABELS:
            continue
        due, odd = _due_of(getattr(state, "date_gmt", ""))
        known[post] = (status, due, odd)
    return known


def _due_of(value: object) -> tuple[datetime | None, bool]:
    """``date_gmt`` của website (UTC, ``YYYY-MM-DDTHH:MM:SS``) → giờ có múi giờ. Rỗng: ``(None,
    False)``; sai khuôn hay ngoài khoảng năm của kế hoạch: ``(None, True)``."""
    if not isinstance(value, str) or not value:
        return None, False
    if len(value) != len("2026-11-03T01:00:00"):
        return None, True
    try:
        moment = datetime.strptime(value, _DATE_GMT).replace(tzinfo=UTC)
    except ValueError:
        return None, True
    # LC-T113-1: xét năm theo giờ UTC **trước** khi đổi sang giờ Việt Nam: cuối năm 9999 cộng 7 giờ
    # là năm 10000, ``astimezone`` ném ``OverflowError``. Năm UTC trong khoảng thì đổi múi giờ an
    # toàn, rồi xét lại theo năm giờ Việt Nam (đúng khoảng ô Sheet đọc lại được).
    if not model.YEAR_MIN - 1 <= moment.year <= model.YEAR_MAX:
        return None, True
    if not model.YEAR_MIN <= moment.astimezone(model.TIMEZONE).year <= model.YEAR_MAX:
        return None, True
    return moment, False


def _post_counts(plan: SheetPlan) -> Counter[int]:
    """Số dòng mang mỗi mã bài WordPress, đếm trên **mọi** ô Sheet đã đọc (cả dòng trùng Mã bài,
    dòng không đọc được), để một bài nối nhiều dòng không được ghi vào dòng nào."""
    position = plan.columns.get("wp_post_id")
    counts: Counter[int] = Counter()
    if plan.values and position is not None:
        for cells in plan.values[1:]:
            post = _post_id_of(_cell_at(cells, position))
            if _is_post_id(post):
                counts[post] += 1
        return counts
    for sheet_row in plan.rows:
        if sheet_row.plan.wp_post_id is not None:
            counts[sheet_row.plan.wp_post_id] += 1
    return counts


def _moment_of(value: CellValue) -> datetime | None | bool:
    """Ô «Ngày đăng thực tế» → thời điểm; trống: ``None``; không đọc được: ``False``."""
    try:
        return model.parse_plan_datetime(_reader_text(value))
    except ValueError:
        return False


def _same_moment(first: datetime | None | bool, second: datetime | None | bool) -> bool:
    """Cùng thời điểm tới phút (ô Sheet ghi tới phút); ``None`` chỉ bằng ``None``."""
    if not isinstance(first, datetime) or not isinstance(second, datetime):
        return first is second
    return first.astimezone(UTC).replace(second=0, microsecond=0) == second.astimezone(UTC).replace(
        second=0, microsecond=0
    )


def _close(due: datetime, before: datetime | None) -> bool:
    """Giờ trên Sheet lệch giờ website không quá ``DATE_TOLERANCE`` (G6)."""
    return isinstance(before, datetime) and abs(due - before) <= DATE_TOLERANCE


def _time_text(moment: datetime) -> str:
    return moment.astimezone(model.TIMEZONE).strftime("%d/%m/%Y %H:%M")


def _notice(
    kind: WebNoticeKind,
    template: str,
    key: str,
    post: int,
    *,
    number: int = 0,
    web: str = "",
    status: str = "",
    field: str = "",
    at: datetime | None = None,
) -> WebNotice:
    message = template.format(
        key=key, post=post, number=number, web=web, status=status, field=field,
        at=_time_text(at) if at is not None else "",
    )  # fmt: skip
    return WebNotice(kind, message, key, post)


__all__ = [
    "CHECK_MAX_AGE",
    "DATE_TOLERANCE",
    "LATE_AFTER",
    "WebApplyResult",
    "WebChangeKind",
    "WebCheck",
    "WebConflict",
    "WebNotice",
    "WebNoticeKind",
    "WebUpdate",
    "apply_website_changes",
    "check_website",
]

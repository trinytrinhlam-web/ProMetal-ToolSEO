"""Đề xuất thay đổi kế hoạch kèm lý do (T-098, thiết kế T-094 mục 1.4).

Hai nguồn, cùng một khuôn ``Proposal``:

1. **Code so bảng** (``compare_rows``): bảng từ file, chữ dán, Sheet khác so với kế hoạch hiện
   tại. Khớp theo Mã bài, không có mã thì theo từ khóa (chữ thường, bỏ dấu). Bảng **không bao
   giờ** sinh «Bỏ», trừ dòng ghi Trạng thái «Bỏ».
2. **AI đọc chữ tự do** (``from_ai``): kết quả ``PlanSuggestions`` là dữ liệu chưa tin cậy
   (LC-T094-20): tối đa ``MAX_AI_ITEMS`` mục, mục sai bị bỏ (chỉ đếm, không chép chữ AI vào câu
   báo); «Cập nhật», «Bỏ» phải nói đúng Mã bài có thật; AI không đặt được slug, trang đích hay
   trạng thái nào khác «Bỏ».

Mọi đề xuất qua cùng một bộ kiểm (chỉ thêm cảnh báo, không tự sửa): trùng từ khóa trong kế hoạch,
trùng bài đã đăng, ngày đã qua, bài đã hẹn giờ/đăng bị đổi, nguy cơ trang cửa ngõ. «Bỏ» và đề
xuất có cảnh báo không tick sẵn (``preselected``). Không đường nào xóa dòng: «Bỏ» chỉ đổi Trạng
thái thành «Bỏ».
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from pydantic import ValidationError

from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.onpage.meta import compare_key, has_html, similarity
from seo_app.plan import model
from seo_app.plan.model import FIELD_LABELS, PlanRow, clean_text, fold_key, keyword_key
from seo_app.text import slugify

MAX_AI_ITEMS = 100
REASON_MAX = 300
# Từ trùng tối thiểu để coi từ khóa «nằm trọn» trong tiêu đề bài đã đăng là trùng (từ khóa ngắn
# như «cửa cuốn» nằm trong rất nhiều tiêu đề, không có nghĩa là trùng bài).
_MIN_SHARED_WORDS = 3
# Số từ khóa chỉ khác địa danh để cảnh báo «nguy cơ trang cửa ngõ» (review_ke_hoach_v1.md L5).
DOORWAY_MIN = 3

# Trường đề xuất (từ bảng hay AI) được đổi. Trạng thái chỉ đổi qua «Bỏ»; Mã bài WordPress, ngày
# đăng thực tế, cập nhật lúc chỉ app ghi sau khi gửi WordPress.
EDITABLE = (
    "keyword", "secondary", "intent", "kind", "priority", "planned_date", "planned_time",
    "title_hint", "slug", "target_id", "notes",
)  # fmt: skip
# Trường AI được đề xuất (không slug, không trang đích: AI không đưa địa chỉ nào vào kế hoạch).
AI_FIELDS = (
    "keyword", "secondary", "intent", "kind", "priority", "planned_date", "planned_time",
    "title_hint", "notes",
)  # fmt: skip
_SHOWN_VALUES = frozenset({"intent", "kind", "priority", "planned_date", "planned_time"})

# Câu cảnh báo cố định (LC-T094-2): chỉ nêu mã bài, không chép chữ từ kế hoạch hay website.
WARN_PAST = "Ngày dự kiến đã qua."
WARN_DUPLICATE_ROW = "Từ khóa trùng dòng {key} trong kế hoạch."
WARN_DUPLICATE_POST = (
    "Có thể trùng bài đã đăng (mã bài {post_id}): hai trang nhắm cùng từ khóa tranh nhau trên "
    "Google. Cân nhắc cập nhật bài cũ thay vì viết bài mới."
)
WARN_RELEASED = (
    "Bài này đã hẹn giờ hoặc đã đăng trên website: đổi ở đây không đổi lịch hay bài trên website."
)
WARN_UPDATE_OLD = "Loại «Cập nhật bài cũ» chưa hỗ trợ: app chưa sửa bài đã đăng."
NOTE_DUPLICATES = "{count} dòng trùng một bài đã khớp ở dòng trên nên bỏ qua."
NOTE_AI_DROPPED = "{count} đề xuất của AI không hợp lệ nên đã bỏ."
WARN_DOORWAY = (
    "Nhiều từ khóa chỉ khác tên quận, phường (cùng một khuôn thay địa danh): nguy cơ bị Google coi "
    "là trang cửa ngõ, nội dung hàng loạt. Chỉ giữ trang nào có nội dung riêng thật."
)


class Action(StrEnum):
    ADD = "Thêm"
    UPDATE = "Cập nhật"
    DROP = "Bỏ"


SOURCE_TABLE = "bảng"
SOURCE_AI = "AI"
# Chữ ``action`` AI trả về (so không dấu, chữ thường) → loại đề xuất.
_AI_ACTIONS = {"them": Action.ADD, "cap nhat": Action.UPDATE, "bo": Action.DROP}


@dataclass(frozen=True)
class Proposal:
    """Một thay đổi đề xuất cho kế hoạch.

    ``after`` là dòng sẽ ghi (dòng mới đã có mã bài kế tiếp; «Bỏ» là dòng cũ đổi Trạng thái);
    ``before`` là dòng hiện tại (``None`` với «Thêm»). ``reason``: lý do (code viết, hay chữ AI
    đã làm sạch). Mọi chữ là chữ thuần chưa escape: giao diện hiện bằng ô bảng (LC-T094-3)."""

    action: Action
    key: str
    after: PlanRow
    before: PlanRow | None = None
    reason: str = ""
    warnings: tuple[str, ...] = ()
    source: str = SOURCE_TABLE

    @property
    def changes(self) -> tuple[str, ...]:
        """Các trường đổi so với dòng hiện tại (rỗng với «Thêm»)."""
        if self.before is None:
            return ()
        return tuple(
            name
            for name in (*EDITABLE, "status")
            if getattr(self.before, name) != getattr(self.after, name)
        )

    @property
    def preselected(self) -> bool:
        """Tick sẵn: chỉ «Thêm», «Cập nhật» không có cảnh báo (thiết kế 1.4)."""
        return self.action is not Action.DROP and not self.warnings


@dataclass(frozen=True)
class ProposalSet:
    """Danh sách đề xuất. ``dropped``: số mục AI bị bỏ vì sai; ``notes``: câu báo cố định."""

    items: tuple[Proposal, ...] = ()
    dropped: int = 0
    notes: tuple[str, ...] = ()


# ------------------------------------------------------------------------------ so bảng


def compare_rows(
    current: Sequence[PlanRow],
    incoming: Sequence[PlanRow],
    *,
    posts: Iterable[object] = (),
    today: date | None = None,
) -> ProposalSet:
    """Đề xuất từ một bảng (``incoming``, ví dụ ``ParsedPlan.rows``) so với kế hoạch hiện tại.

    Khớp: dòng có Mã bài thì theo mã (mã chưa có trong kế hoạch là dòng mới giữ mã đó); dòng không
    có mã thì theo từ khóa. Ô trống trong bảng không xóa giá trị đang có. Dòng mới chưa có mã được
    cấp mã kế tiếp (``next_key``). ``posts``: bài đã đăng (``SiteIndex.items``) để cảnh báo trùng.
    """
    by_key = {row.key: row for row in current if row.key}
    by_keyword: dict[str, PlanRow] = {}
    for row in current:
        by_keyword.setdefault(keyword_key(row.keyword), row)
    keys = [row.key for row in current if row.key]
    matched: set[str] = set()
    proposals: list[Proposal] = []
    duplicates = 0
    for row in incoming:
        match = by_key.get(row.key) if row.key else by_keyword.get(keyword_key(row.keyword))
        if match is not None:
            ident = match.key or keyword_key(match.keyword)
            if ident in matched:
                duplicates += 1
                continue
            matched.add(ident)
            proposal = _table_change(match, row, by_key=bool(row.key))
            if proposal is not None:
                proposals.append(proposal)
            continue
        if row.status == model.STATUS_DROPPED:
            continue  # «Bỏ» một bài chưa có trong kế hoạch: không có gì để bỏ
        key = row.key if row.key and row.key not in keys else model.next_key(keys)
        keys.append(key)
        new = _new_row(row, key)
        proposals.append(
            Proposal(Action.ADD, key, new, reason="Bài mới trong bảng, chưa có trong kế hoạch.")
        )
    notes = (NOTE_DUPLICATES.format(count=duplicates),) if duplicates else ()
    checked = check_proposals(proposals, current, posts=posts, today=today)
    return ProposalSet(tuple(checked), 0, notes)


def _new_row(row: PlanRow, key: str) -> PlanRow:
    """Dòng mới: chỉ các trường đề xuất được, Trạng thái «Chưa viết» hay «Đang viết»."""
    data = {name: getattr(row, name) for name in EDITABLE}
    status = row.status if row.status in (model.STATUS_NEW, model.STATUS_WRITING) else None
    return PlanRow.model_validate({**data, "key": key, "status": status or model.STATUS_NEW})


def _merge(base: PlanRow, values: dict[str, object]) -> PlanRow:
    return PlanRow.model_validate({**base.model_dump(), **values})


def _table_change(current: PlanRow, row: PlanRow, *, by_key: bool) -> Proposal | None:
    """Đề xuất cho một dòng bảng đã khớp dòng ``current``. Khớp theo từ khóa (``by_key`` sai) thì
    không đổi từ khóa: hai cách viết chỉ khác hoa thường hay dấu («sua cua», «Sửa cửa») là cùng
    một bài, giữ cách viết đang có."""
    if row.status == model.STATUS_DROPPED:
        if current.status == model.STATUS_DROPPED:
            return None
        after = _merge(current, {"status": model.STATUS_DROPPED})
        return Proposal(Action.DROP, current.key, after, current, "Trạng thái trong bảng là «Bỏ».")
    fields = EDITABLE if by_key else tuple(name for name in EDITABLE if name != "keyword")
    values = {
        name: getattr(row, name)
        for name in fields
        if getattr(row, name) not in ("", None) and getattr(row, name) != getattr(current, name)
    }
    if not values:
        return None
    after = _merge(current, values)
    return Proposal(
        Action.UPDATE, current.key, after, current, _change_reason(current, after) + " (theo bảng)."
    )


def _shown(name: str, value: object) -> str:
    if value in ("", None):
        return "(trống)"
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return str(value)


def _change_reason(before: PlanRow, after: PlanRow) -> str:
    """Lý do do code viết: tên trường, và giá trị cũ → mới với nhãn, ngày, giờ (giá trị đã chuẩn
    hóa của code). Trường chữ tự do chỉ nêu tên, không chép chữ."""
    parts = []
    for name in EDITABLE:
        old, new = getattr(before, name), getattr(after, name)
        if old == new:
            continue
        label = FIELD_LABELS[name]
        if name in _SHOWN_VALUES:
            parts.append(f"{label} {_shown(name, old)} → {_shown(name, new)}")
        else:
            parts.append(f"{label} đổi")
    return "; ".join(parts) or "Không đổi"


# ------------------------------------------------------------------------------ AI


def from_ai(
    raw: object,
    current: Sequence[PlanRow],
    *,
    posts: Iterable[object] = (),
    today: date | None = None,
) -> ProposalSet:
    """Đề xuất từ kết quả AI (``PlanSuggestions``), kiểm từng mục (LC-T094-20). Mục sai bị bỏ và
    chỉ được đếm (``dropped``): hành động lạ, thiếu lý do hay lý do dài quá ``REASON_MAX`` ký tự,
    chữ có HTML, nhãn ngoài danh sách, ngày không đọc được hay ngoài khoảng, «Thêm» không có từ
    khóa hay có Mã bài, «Cập nhật»/«Bỏ» nói Mã bài không có thật, hai mục cùng một Mã bài, quá
    ``MAX_AI_ITEMS`` mục. «Cập nhật» không đổi gì thì bỏ qua (không tính là sai)."""
    if not isinstance(raw, PlanSuggestions):
        raise TypeError("cần PlanSuggestions")
    items = list(raw.items)
    dropped = max(len(items) - MAX_AI_ITEMS, 0)
    by_key = {row.key: row for row in current if row.key}
    keys = [row.key for row in current if row.key]
    touched: set[str] = set()
    proposals: list[Proposal] = []
    for item in items[:MAX_AI_ITEMS]:
        proposal = _ai_item(item, by_key, keys, touched)
        if proposal is _INVALID:
            dropped += 1
        elif proposal is not None:
            proposals.append(proposal)
    checked = check_proposals(proposals, current, posts=posts, today=today)
    notes = (NOTE_AI_DROPPED.format(count=dropped),) if dropped else ()
    return ProposalSet(tuple(checked), dropped, notes)


_INVALID = object()


def _ai_values(item: PlanSuggestion) -> dict[str, object] | None:
    """Các trường AI đề xuất đã kiểm; ``None`` nếu có trường sai (cả mục bị bỏ)."""
    values: dict[str, object] = {}
    for name in AI_FIELDS:
        raw = getattr(item, name)
        if not isinstance(raw, str):
            return None
        if has_html(raw):
            return None
        if not clean_text(raw):
            continue
        values[name] = raw
    try:
        # Dựng thử để kiểm từng trường bằng đúng bộ làm sạch của PlanRow.
        checked = PlanRow.model_validate({"keyword": values.get("keyword", "xx"), **values})
    except ValidationError:
        return None
    return {name: getattr(checked, name) for name in values}


def _ai_item(item: object, by_key, keys: list[str], touched: set[str]):
    if not isinstance(item, PlanSuggestion):
        return _INVALID
    action = _AI_ACTIONS.get(fold_key(item.action))
    reason = clean_text(item.reason)
    if action is None or not reason or len(reason) > REASON_MAX or has_html(item.reason):
        return _INVALID
    values = _ai_values(item)
    if values is None:
        return _INVALID
    key = clean_text(item.key).upper()
    if action is Action.ADD:
        if key or "keyword" not in values:
            return _INVALID
        new_key = model.next_key(keys)
        keys.append(new_key)
        row = PlanRow.model_validate({**values, "key": new_key})
        return Proposal(Action.ADD, new_key, row, reason=reason, source=SOURCE_AI)
    current = by_key.get(key)
    if current is None or key in touched:
        return _INVALID
    touched.add(key)
    if action is Action.DROP:
        if current.status == model.STATUS_DROPPED:
            return None
        after = _merge(current, {"status": model.STATUS_DROPPED})
        return Proposal(Action.DROP, key, after, current, reason, source=SOURCE_AI)
    changed = {name: value for name, value in values.items() if getattr(current, name) != value}
    if not changed:
        return None
    return Proposal(Action.UPDATE, key, _merge(current, changed), current, reason, source=SOURCE_AI)


# ------------------------------------------------------------------------------ cảnh báo


def check_proposals(
    proposals: Sequence[Proposal],
    current: Sequence[PlanRow],
    *,
    posts: Iterable[object] = (),
    today: date | None = None,
) -> list[Proposal]:
    """Thêm cảnh báo cho từng đề xuất (thiết kế 1.4); không sửa đề xuất nào."""
    today = today or model.today_vn()
    posts = list(posts)
    replaced = {p.before.key for p in proposals if p.before is not None}
    final = [row for row in current if row.key not in replaced] + [p.after for p in proposals]
    doorway = _doorway_templates(row.keyword for row in final if row.status != model.STATUS_DROPPED)
    checked = []
    for proposal in proposals:
        warnings = list(proposal.warnings)
        after, before = proposal.after, proposal.before
        if proposal.action is not Action.DROP:
            if after.planned_date is not None and after.planned_date < today:
                warnings.append(WARN_PAST)
            same = keyword_key(after.keyword)
            twin = next(
                (
                    other
                    for other in final
                    if other is not after
                    and other.status != model.STATUS_DROPPED
                    and keyword_key(other.keyword) == same
                ),
                None,
            )
            if twin is not None:
                warnings.append(WARN_DUPLICATE_ROW.format(key=twin.key or "mới"))
            post_id = _duplicate_post(after, posts)
            if post_id is not None:
                warnings.append(WARN_DUPLICATE_POST.format(post_id=post_id))
            if after.kind == model.KIND_UPDATE_OLD:
                warnings.append(WARN_UPDATE_OLD)
            if _location_template(after.keyword) in doorway:
                warnings.append(WARN_DOORWAY)
        if before is not None and before.status in (model.STATUS_SCHEDULED, model.STATUS_PUBLISHED):
            moved = {"planned_date", "planned_time", "status"} & set(proposal.changes)
            if moved:
                warnings.append(WARN_RELEASED)
        checked.append(
            Proposal(
                proposal.action,
                proposal.key,
                after,
                before,
                proposal.reason,
                tuple(dict.fromkeys(warnings)),
                proposal.source,
            )
        )
    return checked


def _words(text: str) -> frozenset[str]:
    return frozenset(fold_key(text).split())


def _duplicate_post(row: PlanRow, posts: Sequence[object]) -> int | None:
    """Mã bài đã đăng nhắm cùng từ khóa (như kiểm trùng T-036): slug bằng slug của từ khóa, tiêu
    đề rất giống từ khóa (hệ số Dice ≥ 0,8 trên tập từ không dấu), hoặc mọi từ của từ khóa (ít
    nhất 3 từ) nằm trong tiêu đề. Bỏ qua chính bài của dòng này (``wp_post_id``)."""
    keyword_words = _words(row.keyword)
    keyword_slug = slugify(row.keyword)
    if not keyword_words:
        return None
    for post in posts:
        post_id = getattr(post, "id", None)
        if not isinstance(post_id, int) or post_id == row.wp_post_id:
            continue
        title = getattr(post, "title", "")
        slug = getattr(post, "slug", "")
        title_words = _words(compare_key(title)) if isinstance(title, str) else frozenset()
        if (
            (isinstance(slug, str) and slug and slug == keyword_slug)
            or similarity(keyword_words, title_words) >= 0.8
            or (len(keyword_words) >= _MIN_SHARED_WORDS and keyword_words <= title_words)
        ):
            return post_id
    return None


# Địa danh TP.HCM trong từ khóa (chữ không dấu): «quận 7», «q7», «phường Tân Định», «p.12» và tên
# quận, huyện cũ không có chữ «quận» đứng trước.
_DISTRICTS = (
    "binh thanh", "tan binh", "tan phu", "go vap", "phu nhuan", "binh tan", "thu duc", "nha be",
    "can gio", "cu chi", "hoc mon", "binh chanh",
)  # fmt: skip
_LOCATION = re.compile(
    r"\b(?:quan|q|phuong|p|huyen|xa)\s*\.?\s*(?:\d{1,2}\b|[a-z]+(?:\s+[a-z]+)?)"
    r"|\b(?:" + "|".join(_DISTRICTS) + r")\b"
)


def _location_template(keyword: str) -> str | None:
    """Từ khóa bỏ địa danh (khuôn chung), hay ``None`` nếu từ khóa không có địa danh."""
    folded = fold_key(keyword)
    template = " ".join(_LOCATION.sub(" ", folded).split())
    return template if template and template != folded else None


def _doorway_templates(keywords: Iterable[str]) -> set[str]:
    """Các khuôn có từ ``DOORWAY_MIN`` từ khóa trở lên chỉ khác địa danh."""
    places: dict[str, set[str]] = {}
    for keyword in keywords:
        template = _location_template(keyword)
        if template is not None:
            places.setdefault(template, set()).add(fold_key(keyword))
    return {template for template, found in places.items() if len(found) >= DOORWAY_MIN}

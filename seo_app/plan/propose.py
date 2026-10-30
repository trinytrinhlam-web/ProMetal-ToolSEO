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
thái thành «Bỏ». Mọi bước chạy tuyến tính theo số dòng (kế hoạch tới ``MAX_ROWS`` dòng).
"""

from __future__ import annotations

import functools
import re
import unicodedata
from bisect import bisect_left
from collections.abc import Iterable, Iterator, Sequence
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
# AI đề xuất nhiều hơn số này một lần thì mọi đề xuất AI có cảnh báo (không tick sẵn): AI bị dụ
# đề xuất hàng loạt thì người dùng phải xem từng dòng (góp ý G8 Soi Lỗi T-098).
AI_MANY = 20
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
_AI_TEXT_FIELDS = ("keyword", "secondary", "title_hint", "notes")
_SHOWN_VALUES = frozenset({"intent", "kind", "priority", "planned_date", "planned_time"})
_RELEASED = (model.STATUS_SCHEDULED, model.STATUS_PUBLISHED)

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
WARN_DOORWAY = (
    "Nhiều từ khóa chỉ khác tên quận, phường (cùng một khuôn thay địa danh): nguy cơ bị Google coi "
    "là trang cửa ngõ, nội dung hàng loạt. Chỉ giữ trang nào có nội dung riêng thật."
)
WARN_PERSONAL = (
    "Đề xuất của AI có số điện thoại hoặc email: kiểm tra trước khi đưa vào kế hoạch (có thể là "
    "thông tin của khách)."
)
WARN_PRICE = (
    "Đề xuất của AI có nhắc tới giá: Pro-Metal không công bố giá. Kiểm tra trước khi đưa vào kế "
    "hoạch (ghi chú của thợ sẽ thành chất liệu thật của bài)."
)
WARN_MANY_AI = "AI đề xuất {count} thay đổi cùng lúc: xem kỹ từng dòng trước khi tick."
NOTE_DUPLICATES = "{count} dòng trùng một bài đã khớp ở dòng trên nên bỏ qua."
NOTE_AI_DROPPED = "{count} đề xuất của AI không hợp lệ nên đã bỏ."
REASON_NEW = "Bài mới trong bảng, chưa có trong kế hoạch."
REASON_DROP = "Trạng thái trong bảng là «Bỏ»."
REASON_NEW_KEY = "Cấp mã bài {key} cho dòng chưa có mã"


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

    ``after`` là dòng sẽ ghi (dòng mới đã có mã bài kế tiếp; «Bỏ» là dòng cũ đổi Trạng thái; dòng
    cũ chưa có mã được cấp mã); ``before`` là dòng hiện tại (``None`` với «Thêm»). ``reason``: lý
    do (code viết, hay chữ AI đã làm sạch). Mọi chữ là chữ thuần chưa escape: giao diện hiện bằng ô
    bảng (LC-T094-3)."""

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
            for name in ("key", *EDITABLE, "status")
            if getattr(self.before, name) != getattr(self.after, name)
        )

    @property
    def preselected(self) -> bool:
        """Tick sẵn: chỉ «Thêm», «Cập nhật» không có cảnh báo (thiết kế 1.4)."""
        return self.action is not Action.DROP and not self.warnings

    def with_warnings(self, warnings: Iterable[str]) -> Proposal:
        """Bản sao có thêm ``warnings`` (bỏ câu trùng, giữ thứ tự)."""
        merged = tuple(dict.fromkeys([*self.warnings, *warnings]))
        return Proposal(
            self.action, self.key, self.after, self.before, self.reason, merged, self.source
        )


@dataclass(frozen=True)
class ProposalSet:
    """Danh sách đề xuất. ``dropped``: số mục AI bị bỏ vì sai; ``notes``: câu báo cố định."""

    items: tuple[Proposal, ...] = ()
    dropped: int = 0
    notes: tuple[str, ...] = ()


class _Keys:
    """Cấp Mã bài cho dòng mới: không trùng mã đã có, số lớn nhất cộng 1 (như ``next_key``), mỗi
    lần không phải quét lại danh sách (Soi Lỗi SL-T098-11).

    Dựng không bao giờ báo lỗi, kể cả khi kế hoạch có mã ``B-99999`` (gõ tay trên Sheet: dữ liệu
    chưa tin cậy); chỉ khi cần cấp mã mới mà đã quá ``MAX_KEY_NUMBER`` thì tìm số trống từ đầu
    (kế hoạch tối đa ``MAX_ROWS`` dòng nên luôn còn), hết thật mới báo ``PlanKeyError`` câu cố định
    (Soi Lỗi SL-T098-17)."""

    def __init__(self, existing: Iterable[str], prefix: str = "B") -> None:
        self.used = {key for key in existing if key}
        self.prefix = prefix
        numbers = (model.key_number(key, prefix) for key in self.used)
        self.number = max((n for n in numbers if n is not None), default=0)

    def take(self, key: str) -> bool:
        """Giữ mã ``key`` (đúng dạng) cho một dòng mới; ``False`` nếu mã đã có."""
        if key in self.used:
            return False
        self.used.add(key)
        number = model.key_number(key, self.prefix)
        if number is not None:
            self.number = max(self.number, number)
        return True

    def new(self) -> str:
        """Mã kế tiếp chưa dùng (``B-001``…, ít nhất 3 chữ số)."""
        for _ in range(2):  # lần hai: hết số phía trên thì tìm số trống từ 1
            while self.number < model.MAX_KEY_NUMBER:
                self.number += 1
                key = f"{self.prefix}-{self.number:03d}"
                if key not in self.used:
                    self.used.add(key)
                    return key
            self.number = 0
        raise model.PlanKeyError(model.KEYS_EXHAUSTED.format(prefix=self.prefix))


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
    có mã thì theo từ khóa. Ô trống trong bảng không xóa giá trị đang có. Dòng mới chưa có mã, và
    dòng cũ chưa có mã được đề xuất đổi, được cấp mã kế tiếp, sau khi đã giữ mọi mã mới ghi sẵn
    trong bảng (dòng ghi «B-004» đứng sau một dòng chưa có mã vẫn giữ «B-004», Soi Lỗi SL-T098-20).
    ``posts``: bài đã đăng (``SiteIndex.items``) để cảnh báo trùng.
    """
    by_key = {row.key: row for row in current if row.key}
    by_keyword: dict[str, PlanRow] = {}
    for row in current:
        by_keyword.setdefault(keyword_key(row.keyword), row)
    keys = _Keys(row.key for row in current)
    written = {
        row.key
        for row in incoming
        if row.key and row.key not in by_key and row.status != model.STATUS_DROPPED
    }
    for key in written:
        keys.take(key)
    matched: set[int] = set()
    proposals: list[Proposal] = []
    duplicates = 0
    for row in incoming:
        match = by_key.get(row.key) if row.key else by_keyword.get(keyword_key(row.keyword))
        if match is not None:
            if id(match) in matched:
                duplicates += 1
                continue
            matched.add(id(match))
            proposal = _table_change(match, row, by_key=bool(row.key), keys=keys)
            if proposal is not None:
                proposals.append(proposal)
            continue
        if row.status == model.STATUS_DROPPED:
            continue  # «Bỏ» một bài chưa có trong kế hoạch: không có gì để bỏ
        if row.key in written:
            written.discard(row.key)  # dòng sau ghi trùng mã này thì được cấp mã mới
            key = row.key
        else:
            key = keys.new()
        proposals.append(Proposal(Action.ADD, key, _new_row(row, key), reason=REASON_NEW))
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


def _table_change(current: PlanRow, row: PlanRow, *, by_key: bool, keys: _Keys) -> Proposal | None:
    """Đề xuất cho một dòng bảng đã khớp dòng ``current``. Khớp theo từ khóa (``by_key`` sai) thì
    không đổi từ khóa: hai cách viết chỉ khác hoa thường hay dấu («sua cua», «Sửa cửa») là cùng
    một bài, giữ cách viết đang có. Dòng cũ chưa có mã được cấp mã (T-100 ghi Sheet theo mã)."""
    if row.status == model.STATUS_DROPPED:
        if current.status == model.STATUS_DROPPED:
            return None
        values: dict[str, object] = {"status": model.STATUS_DROPPED}
        reasons = [REASON_DROP]
        action = Action.DROP
    else:
        fields = EDITABLE if by_key else tuple(name for name in EDITABLE if name != "keyword")
        values = {
            name: getattr(row, name)
            for name in fields
            if getattr(row, name) not in ("", None) and getattr(row, name) != getattr(current, name)
        }
        if not values:
            return None
        reasons = []
        action = Action.UPDATE
    if not current.key:
        values["key"] = keys.new()
        reasons.insert(0, REASON_NEW_KEY.format(key=values["key"]))
    after = _merge(current, values)
    if action is Action.UPDATE:
        reasons.append(_change_reason(current, after) + " (theo bảng).")
    return Proposal(action, after.key, after, current, "; ".join(reasons))


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
    chữ có HTML (kiểm trên chữ đã làm sạch, cả bản NFKC: ký tự vô hình hay chữ toàn chiều rộng
    không che được thẻ), nhãn ngoài danh sách, ngày không đọc được hay ngoài khoảng, «Thêm» không
    có từ khóa hay có Mã bài, «Cập nhật»/«Bỏ» nói Mã bài không có thật, hai mục cùng một Mã bài,
    quá ``MAX_AI_ITEMS`` mục. «Cập nhật» không đổi gì thì bỏ qua (không tính là sai).

    Thêm cảnh báo: chữ AI có số điện thoại, email (A3); chữ AI đưa vào dòng có giá (LC-T103-1); AI
    đề xuất quá ``AI_MANY`` thay đổi."""
    if not isinstance(raw, PlanSuggestions):
        raise TypeError("cần PlanSuggestions")
    items = list(raw.items)
    dropped = max(len(items) - MAX_AI_ITEMS, 0)
    by_key = {row.key: row for row in current if row.key}
    keys = _Keys(by_key)
    touched: set[str] = set()
    proposals: list[Proposal] = []
    for item in items[:MAX_AI_ITEMS]:
        proposal = _ai_item(item, by_key, keys, touched)
        if proposal is _INVALID:
            dropped += 1
        elif proposal is not None:
            proposals.append(proposal)
    many = [WARN_MANY_AI.format(count=len(proposals))] if len(proposals) > AI_MANY else []
    proposals = [
        proposal.with_warnings(
            [
                *many,
                *([WARN_PERSONAL] if _has_personal(proposal) else []),
                *([WARN_PRICE] if _has_price(proposal) else []),
            ]
        )
        for proposal in proposals
    ]
    checked = check_proposals(proposals, current, posts=posts, today=today)
    notes = (NOTE_AI_DROPPED.format(count=dropped),) if dropped else ()
    return ProposalSet(tuple(checked), dropped, notes)


_INVALID = object()


def _has_html_text(raw: str) -> bool:
    """Chữ có thẻ HTML sau khi làm sạch (bỏ ký tự vô hình chen sau «<») hay sau NFKC («＜b＞»):
    kiểm trên đúng chữ sẽ được dùng, không trên chữ thô (Soi Lỗi SL-T098-1, bài học T-041)."""
    cleaned = clean_text(raw, multiline=True)
    return has_html(cleaned) or has_html(unicodedata.normalize("NFKC", cleaned))


def _has_personal(proposal: Proposal) -> bool:
    """Chữ **do AI đưa** (lý do; với «Thêm» mọi trường chữ, với «Cập nhật» chỉ trường AI đổi) có số
    điện thoại, email. Chữ cũ của dòng không tính: ghi chú có số khách là chuyện thường (Soi Lỗi
    SL-T098-15)."""
    texts = [proposal.reason, *_ai_texts(proposal)]
    return any(any(model.personal_info(text)) for text in texts if text)


# ------------------------------------------------------------- dò giá (LC-T103-1, LC-T100-2)
#
# Dò riêng cho chữ kế hoạch (không dùng ``mentions_price`` của bước SEO). Đây là lưới an toàn
# **mềm**: lời dặn AI đã cấm giá, người dùng còn duyệt; báo thừa theo hướng an toàn dễ chấp nhận
# hơn bỏ lọt. Cách dò:
#
# - Chữ đã làm sạch (``clean_text``), NFKC («５００ｋ» là «500k»), chữ thường.
# - **So theo chữ có dấu** (Soi Lỗi SL-T100-12, -14, -15): chữ có dấu thì từ nói tiền phải viết
#   đúng dấu («trả» không phải «tra» trong «kiểm tra», «tư» không phải «từ», «đ» không phải «d»
#   trong «3d»). Chỉ khi cả chữ **không có dấu nào** (gõ không dấu) mới dò theo từ không dấu («gia
#   500.000», «2 trieu»).
# - Quy tắc chung, ít phụ thuộc danh sách từ đứng trước: số tiền viết có dấu phân nghìn từ 10.000
#   trở lên là giá, trừ khi ngay sau là đơn vị đo, «x» (kích thước), đơn vị thời gian hay đơn vị đếm
#   («2.500 mm», «12.000 điểm hàn», «15.000 bộ», «10.000 lượt tìm»). Bắt được «đặt cọc / thanh
#   toán / chuyển khoản / mất 1.500.000» (SL-T100-13), «Giá nhập 800.000» (SL-T100-12) mà không
#   cần kể hết các chữ đứng trước.
# - Số nhỏ hơn (1.000–9.999) hay số không dấu phân nghìn (từ 5 chữ số) chỉ là giá khi đứng sau chữ
#   nói tiền («giá», «phí», «tiền», «trả»…), trong vòng 3 từ.
# - Dò trên **cả** chữ, không cắt khúc (SL-T100-3); từ khóa chính tìm trên bản bỏ dấu (SL-T100-8),
#   so «nằm trong từ khóa» bằng chia đôi (SL-T100-10); chỗ khớp bị bỏ qua thì dò tiếp từ ký tự kế.
#   Mọi biểu thức không lồng lượng từ: chạy tuyến tính.


def _alternation(*words: str) -> str:
    return "|".join(words)


_UNITS = {
    True: ("đồng", "vnđ", "vnd", "usd", r"đô\s+la", "đô", "nghìn", "ngàn", "triệu", "tỷ", "tỉ",
           "tr", "đ", "k"),
    False: ("dong", "vnd", "usd", r"do\s+la", "nghin", "ngan", "trieu", "ty", "ti", "tr", "d", "k"),
}  # fmt: skip
# Số viết bằng chữ; khi gõ không dấu, bỏ các chữ nhiều nghĩa («tu đồng» là «tự động», «nam», «sau»,
# «may», «bay», «tam»).
_NUMBER_WORDS = {
    True: ("một", "hai", "ba", "bốn", "tư", "năm", "lăm", "sáu", "bảy", "bẩy", "tám", "chín",
           "mười", "mươi", "trăm", "chục", "vài", "mấy", "rưỡi", "nửa"),
    False: ("mot", "hai", "ba", "bon", "lam", "chin", "muoi", "tram", "chuc", "vai", "ruoi", "nua"),
}  # fmt: skip
_WORD_UNITS = {
    True: ("nghìn", "ngàn", "triệu", "tỷ", "tỉ", "đồng", r"đô\s+la"),
    False: ("nghin", "ngan", "trieu", "ty", "ti", "dong", r"do\s+la"),
}
# Chữ nói tiền đứng trước số tiền không đơn vị (LC-T100-2, SL-T100-9, -13).
_LABELS = {
    True: ("giá", "phí", "tiền công", "tiền", "công thợ", "hết", "tốn", "trả", "đặt cọc", "cọc",
           "thanh toán", "chuyển khoản", "mất"),
    False: ("gia", "phi", "tien cong", "tien", "cong tho", "het", "ton", "tra", "dat coc", "coc",
            "thanh toan", "chuyen khoan", "mat"),
}  # fmt: skip
_PHRASE_HEADS = {True: ("giá", "chi phí"), False: ("gia", "chi phi")}
_PHRASE_TAILS = {
    True: ("rẻ", "tốt", "chỉ", "từ", "gốc", "sỉ", "ưu đãi", "cạnh tranh", "hợp lý", "phải chăng",
           "thấp", "mềm", "bình dân", "bao nhiêu"),
    False: ("re", "tot", "chi", "tu", "goc", "si", "uu dai", "canh tranh", "hop ly", "phai chang",
            "thap", "mem", "binh dan", "bao nhieu"),
}  # fmt: skip
# Cụm nói giá đứng riêng; «rẻ», «đắt» chỉ khi có dấu (không dấu nhiều nghĩa: «đặt», «đất»).
_PHRASES_ALONE = {
    True: ("bảng giá", "giảm giá", "khuyến mãi", "khuyến mại", "miễn phí", "ưu đãi", "trọn gói",
           "rẻ", "đắt"),
    False: ("bang gia", "giam gia", "khuyen mai", "mien phi", "uu dai", "tron goi"),
}  # fmt: skip
_THOUSANDS = r"\d{1,3}(?:[.,]\d{3})+"


def _patterns(accented: bool) -> dict[str, re.Pattern[str]]:
    units = _alternation(*_UNITS[accented])
    big_units = _alternation(*_WORD_UNITS[accented][:5])  # nghìn, ngàn, triệu, tỷ, tỉ
    dong = "đồng" if accented else "dong"
    return {
        # Số + đơn vị tiền: «150.000đ», «500k», «1,5 triệu», «1tr5», «2-3 triệu».
        "amount": re.compile(
            rf"(?<![\w.,])(?P<num>\d+(?:[.,]\d+)*)(?P<space>\s*)(?P<unit>{units})\d*(?!\w)"
        ),
        # Số viết bằng chữ + đơn vị: «hai triệu», «vài trăm ngàn», «năm trăm nghìn đồng».
        "words": re.compile(
            rf"(?<!\w)(?:{_alternation(*_NUMBER_WORDS[accented])})\s+"
            rf"(?P<unit>{_alternation(*_WORD_UNITS[accented])})(?!\w)"
        ),
        # Số có dấu phân nghìn đứng riêng (quy tắc chung, xét giá trị ≥ 10.000 ở nơi dùng).
        "big": re.compile(rf"(?<![\w.,])(?P<num>{_THOUSANDS})(?![\d\w])"),
        # Chữ nói tiền rồi số, cách tối đa 3 từ: «Giá thay motor 1.200.000», «Phí khảo sát 5.000».
        "label": re.compile(
            rf"(?<!\w)(?P<label>{_alternation(*_LABELS[accented])})(?!\w)(?:\s*:\s*|\s+)"
            rf"(?:[^\s\d:]+\s+){{0,3}}?:?\s*(?P<num>{_THOUSANDS}|\d{{5,}})(?![\d\w])"
        ),
        # Đơn vị tiền đứng trước số: «VNĐ 500.000», «USD 50».
        "currency": re.compile(r"(?<!\w)(?:vnđ|vnd|usd)\s*:?\s*\d"),
        "phrase": re.compile(
            rf"(?<!\w)(?P<label>{_alternation(*_PHRASE_HEADS[accented])})\s+"
            rf"(?:{_alternation(*_PHRASE_TAILS[accented])})(?!\w)"
            rf"|(?<!\w)(?:{_alternation(*_PHRASES_ALONE[accented])})(?!\w)"
            rf"|(?<!\w)(?:{big_units})\s+{dong}(?!\w)"
        ),
    }


_PATTERNS = {True: _patterns(True), False: _patterns(False)}
_PRICE_SYMBOL = re.compile(r"[$€₫¥£]")
_BIG_AMOUNT = 10_000

# Các danh sách dưới đây so trên chữ **bỏ dấu** của từ đứng cạnh chỗ khớp (đủ cho cả hai cách gõ).
# Đơn vị tiền mà từ đứng sau cho thấy không phải tiền («2 đồng hồ», «đồng thau», «đô thị», «tỷ lệ»).
_NOT_MONEY_AFTER = {
    "dong": ("ho", "bo", "thoi", "loat", "deu", "mau", "nghiep", "y", "nat", "tam", "phuc",
             "huong", "chi", "ruong", "bang", "co", "thau"),
    "do": ("thi",),
    "ty": ("le",),
    "ti": ("le",),
}  # fmt: skip
# «nghìn», «triệu», «k»… rồi danh từ chỉ số đông là số đếm (SL-T100-2): «2 nghìn công trình», «10k
# lượt xem». Chỉ danh từ số đông: «300 nghìn lần đầu», «15 triệu nhà anh Tuấn» là giá (SL-T100-6).
_COUNT_UNITS = frozenset({"nghin", "ngan", "trieu", "ty", "ti", "tr", "k"})
_CROWD_NOUNS = (
    "luot", "khach", "nguoi", "cong trinh", "truy cap", "view", "thanh vien", "hoc vien",
)  # fmt: skip
# Số (không đơn vị tiền) mà ngay sau là đơn vị đo, «x» (kích thước), đơn vị thời gian: không phải
# tiền («2.500 mm», «1.200 x 600», «12.000 m2»).
_MEASURE_NEXT = (
    "mm", "cm", "m", "m2", "m3", "km", "kg", "g", "ly", "w", "kw", "v", "lit", "tan", "ta", "x",
    "%", "do", "gio", "phut", "giay", "ngay", "tuan", "thang", "nam",
)  # fmt: skip
# Số dưới 1.000.000 mà ngay sau là đơn vị đếm: số lượng, không phải tiền («12.000 điểm hàn», «15.000
# bộ», «10.000 hộ», «10.000 lượt tìm»). Từ 1.000.000 trở lên thì vẫn coi là tiền (đếm hàng triệu
# bộ, điểm thì hiếm). Không có «lần», «nhà», «căn» (hay đứng ngay sau giá: «300.000 lần đầu»).
_COUNT_NEXT = (
    *_CROWD_NOUNS, "bo", "cai", "chiec", "ho", "diem", "san pham", "don", "cay", "tam", "cuon",
    "bai", "du an", "mau", "ban", "doi", "cap", "vien", "con", "hop", "thung", "kien", "sp", "pcs",
)  # fmt: skip
_COUNT_LIMIT = 1_000_000
# Chữ nói tiền nằm trong từ ghép không nói tiền: «đánh giá tốt», «mặt tiền», «trả lời», «hết hạn»,
# và khi gõ không dấu: «kiem tra», «dieu tra», «tra cuu».
_LABEL_NOT_BEFORE = {"gia": ("danh",), "tien": ("mat",), "tra": ("kiem", "dieu")}
_LABEL_NOT_AFTER = {"tra": ("loi", "cuu"), "het": ("han",)}
_WORD = re.compile(r"\w+")


@functools.cache
def _fold_char(char: str) -> str:
    """Một ký tự bỏ dấu, vẫn đúng một ký tự (giữ vị trí): «ế» → «e», «đ» → «d»."""
    if char in "đĐ":
        return "d" if char == "đ" else "D"
    base = "".join(c for c in unicodedata.normalize("NFD", char) if not unicodedata.combining(c))
    return base[:1] if len(base) == 1 else char


def _lower_keep(text: str) -> str:
    """Chữ thường mà độ dài không đổi (ký tự nào thành hai ký tự khi viết thường thì giữ nguyên)."""
    return "".join(low if len(low := char.lower()) == 1 else char for char in text)


def _fold(text: str) -> str:
    return "".join(_fold_char(char) for char in text)


def _all_matches(pattern: re.Pattern[str], text: str) -> Iterator[re.Match[str]]:
    """Mọi chỗ khớp, kể cả gối lên nhau: chỗ khớp bị bỏ qua thì dò tiếp từ ký tự kế."""
    pos = 0
    while (found := pattern.search(text, pos)) is not None:
        yield found
        pos = found.start() + 1


class _PriceText:
    """Chữ để dò giá: ``original`` (chữ thường, giữ dấu), ``folded`` (bỏ dấu, cùng độ dài),
    ``accented`` (chữ có ít nhất một dấu), vị trí các lần xuất hiện của từ khóa chính."""

    def __init__(self, text: str, keyword: str) -> None:
        visible = unicodedata.normalize("NFKC", clean_text(text, multiline=True))
        self.visible = visible
        self.original = _lower_keep(visible)
        self.folded = _fold(self.original)
        self.accented = self.folded != self.original
        key = " ".join(
            _fold(_lower_keep(unicodedata.normalize("NFKC", clean_text(keyword)))).split()
        )
        self.key_length = len(key)
        self.key_starts: list[int] = []
        start = self.folded.find(key) if key else -1
        while start >= 0:
            self.key_starts.append(start)
            start = self.folded.find(key, start + 1)

    def in_keyword(self, found: re.Match[str]) -> bool:
        """Chỗ khớp nằm trọn trong một lần xuất hiện của từ khóa chính."""
        start, end = found.span()
        index = bisect_left(self.key_starts, end - self.key_length)
        return index < len(self.key_starts) and self.key_starts[index] <= start

    def word_before(self, start: int) -> str:
        words = _WORD.findall(self.folded[max(0, start - 20) : start])
        return words[-1] if words else ""

    def words_after(self, end: int) -> str:
        return " ".join(self.folded[end : end + 40].split())


def _starts_with_word(text: str, words: Iterable[str]) -> bool:
    """``text`` bắt đầu bằng một trong ``words``, trọn từ (không dính chữ cái sau)."""
    for word in words:
        if text.startswith(word) and not _WORD.match(text[len(word) : len(word) + 1]):
            return True
    return False


def _number_value(number: str) -> int:
    digits = re.sub(r"[.,]", "", number)
    return int(digits[:15]) if digits.isdigit() else 0


def _not_amount(text: _PriceText, end: int, value: int) -> bool:
    """Số (không đơn vị tiền) kết thúc ở ``end`` là số đo, kích thước, thời gian hay số lượng."""
    after = text.words_after(end)
    if _starts_with_word(after, _MEASURE_NEXT):
        return True
    return value < _COUNT_LIMIT and _starts_with_word(after, _COUNT_NEXT)


def _is_amount(text: _PriceText, found: re.Match[str]) -> bool:
    """Số + đơn vị (mẫu ``amount``, ``words``) có thật là tiền không."""
    unit = " ".join(text.folded[found.start("unit") : found.end("unit")].split())
    unit_end = found.end("unit")
    after = text.words_after(found.end())
    if _starts_with_word(after, _NOT_MONEY_AFTER.get(unit, ())):
        return False
    groups = found.groupdict()
    number = groups.get("num") or ""
    # «3d», «2d»: số nhỏ dính «d» là bản vẽ, ảnh, không phải tiền (SL-T100-15).
    if unit == "d" and number and _number_value(number) < 100:
        return False
    # Tên đường, kiệt viết tắt sau số nhà (SL-T100-1, -5): số nhà ngắn, không dấu phân nghìn, dấu
    # cách rồi «đ.»/«k.» và chữ («45 đ. số 7», «12 K. Lê Duẩn»). Số có dấu phân nghìn («150.000 Đ.»)
    # luôn là tiền.
    if (
        unit in ("d", "k")
        and groups.get("space")
        and number.isdigit()
        and len(number) <= 4
        and text.folded[unit_end : unit_end + 1] == "."
        and text.folded[unit_end + 1 : unit_end + 8].lstrip()[:1].isalpha()
    ):
        return False
    return not (unit in _COUNT_UNITS and _starts_with_word(after, _CROWD_NOUNS))


def _label_ok(text: _PriceText, found: re.Match[str]) -> bool:
    """Chữ nói tiền không nằm trong từ ghép không nói tiền («đánh giá tốt», «mặt tiền»…)."""
    head = _fold(found.group("label")).split()[0]
    if text.word_before(found.start()) in _LABEL_NOT_BEFORE.get(head, ()):
        return False
    after = text.words_after(found.end("label"))
    return not _starts_with_word(after, _LABEL_NOT_AFTER.get(head, ()))


def mentions_plan_price(text: str, keyword: str = "") -> bool:
    """Chữ kế hoạch có nói giá không (chữ có dấu, hay gõ không dấu); chỗ khớp nằm trọn trong một
    lần xuất hiện của từ khóa chính thì không tính («cửa sắt giá rẻ» là từ khóa, không phải lời nói
    giá)."""
    seen = _PriceText(text, keyword)
    patterns = _PATTERNS[seen.accented]
    source = seen.original

    def counts(found: re.Match[str]) -> bool:
        return not seen.in_keyword(found)

    for name in ("amount", "words"):
        if any(counts(f) and _is_amount(seen, f) for f in _all_matches(patterns[name], source)):
            return True
    for found in _all_matches(patterns["big"], source):
        value = _number_value(found.group("num"))
        if value >= _BIG_AMOUNT and counts(found) and not _not_amount(seen, found.end(), value):
            return True
    for found in _all_matches(patterns["label"], source):
        value = _number_value(found.group("num"))
        if (
            counts(found)
            and _label_ok(seen, found)
            and not _not_amount(seen, found.end("num"), value)
        ):
            return True
    for found in _all_matches(patterns["phrase"], source):
        if counts(found) and (found.group("label") is None or _label_ok(seen, found)):
            return True
    for pattern, where in ((patterns["currency"], source), (_PRICE_SYMBOL, seen.visible)):
        if any(counts(found) for found in _all_matches(pattern, where)):
            return True
    return False


def _ai_texts(proposal: Proposal) -> list[str]:
    """Chữ **do AI đưa** trong dòng đề xuất: với «Thêm» mọi trường chữ, với «Cập nhật» chỉ trường
    AI đổi (Soi Lỗi SL-T098-15)."""
    if proposal.action is Action.ADD:
        names: Iterable[str] = _AI_TEXT_FIELDS
    else:
        names = [name for name in _AI_TEXT_FIELDS if name in proposal.changes]
    return [text for name in names if (text := getattr(proposal.after, name))]


def _has_price(proposal: Proposal) -> bool:
    """Chữ AI đưa vào dòng kế hoạch nói về giá (Lá Chắn LC-T103-1, LC-T100-2; Soi Lỗi SL-T100-1 →
    -3): ``mentions_plan_price``, không tính chỗ nằm trong từ khóa chính. Pro-Metal không công bố
    giá; ghi chú của thợ thành «Kinh nghiệm của xưởng» ở Soạn bài, nơi số liệu được coi là thật."""
    keyword = proposal.after.keyword
    return any(mentions_plan_price(text, keyword) for text in _ai_texts(proposal))


def _ai_values(item: PlanSuggestion) -> dict[str, object] | None:
    """Các trường AI đề xuất đã kiểm; ``None`` nếu có trường sai (cả mục bị bỏ)."""
    values: dict[str, object] = {}
    for name in AI_FIELDS:
        raw = getattr(item, name)
        if not isinstance(raw, str) or _has_html_text(raw):
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


def _ai_item(item: object, by_key, keys: _Keys, touched: set[str]):
    if not isinstance(item, PlanSuggestion):
        return _INVALID
    action = _AI_ACTIONS.get(fold_key(item.action))
    reason = clean_text(item.reason)
    if action is None or not reason or len(reason) > REASON_MAX or _has_html_text(item.reason):
        return _INVALID
    values = _ai_values(item)
    if values is None:
        return _INVALID
    try:
        key = model.parse_key(item.key)
    except ValueError:
        return _INVALID
    if action is Action.ADD:
        if key or "keyword" not in values:
            return _INVALID
        new_key = keys.new()
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


@dataclass(frozen=True)
class _Post:
    id: int
    slug: str
    words: frozenset[str]


def check_proposals(
    proposals: Sequence[Proposal],
    current: Sequence[PlanRow],
    *,
    posts: Iterable[object] = (),
    today: date | None = None,
) -> list[Proposal]:
    """Thêm cảnh báo cho từng đề xuất (thiết kế 1.4); không sửa đề xuất nào. Khóa từ khóa, khuôn
    địa danh, tập từ của bài đã đăng tính **một lần** mỗi dòng (tuyến tính, SL-T098-11)."""
    today = today or model.today_vn()
    post_index = _post_index(posts)
    replaced = {id(p.before) for p in proposals if p.before is not None}
    final = [row for row in current if id(row) not in replaced] + [p.after for p in proposals]
    keyword_of = {id(row): keyword_key(row.keyword) for row in final}
    owners: dict[str, list[PlanRow]] = {}
    places: dict[str, set[str]] = {}
    template_of: dict[int, str | None] = {}
    for row in final:
        if row.status == model.STATUS_DROPPED:
            continue
        key = keyword_of[id(row)]
        owners.setdefault(key, []).append(row)
        template = template_of[id(row)] = _location_template(key)
        if template is not None:
            places.setdefault(template, set()).add(key)
    doorway = {template for template, found in places.items() if len(found) >= DOORWAY_MIN}
    checked = []
    for proposal in proposals:
        warnings: list[str] = []
        after, before = proposal.after, proposal.before
        changes = set(proposal.changes)
        if proposal.action is not Action.DROP:
            if (
                after.planned_date is not None
                and after.planned_date < today
                and (proposal.action is Action.ADD or "planned_date" in changes)
            ):
                warnings.append(WARN_PAST)
            same = keyword_of[id(after)]
            twin = next((row for row in owners.get(same, ()) if row is not after), None)
            if twin is not None:
                warnings.append(WARN_DUPLICATE_ROW.format(key=twin.key or "mới"))
            post_id = _duplicate_post(after, same, post_index)
            if post_id is not None:
                warnings.append(WARN_DUPLICATE_POST.format(post_id=post_id))
            if after.kind == model.KIND_UPDATE_OLD:
                warnings.append(WARN_UPDATE_OLD)
            if template_of.get(id(after)) in doorway:
                warnings.append(WARN_DOORWAY)
        if before is not None and before.status in _RELEASED and changes:
            # Mọi thay đổi ở bài đã hẹn giờ/đã đăng (góp ý G4): chỉ đổi kế hoạch, không đổi bài.
            warnings.append(WARN_RELEASED)
        checked.append(proposal.with_warnings(warnings))
    return checked


def _post_index(posts: Iterable[object]) -> list[_Post]:
    index = []
    for post in posts:
        post_id = getattr(post, "id", None)
        if not isinstance(post_id, int) or isinstance(post_id, bool):
            continue
        title = getattr(post, "title", "")
        slug = getattr(post, "slug", "")
        words = fold_key(compare_key(title)).split() if isinstance(title, str) else ()
        index.append(_Post(post_id, slug if isinstance(slug, str) else "", frozenset(words)))
    return index


def _duplicate_post(row: PlanRow, folded: str, posts: Sequence[_Post]) -> int | None:
    """Mã bài đã đăng nhắm cùng từ khóa (như kiểm trùng T-036): slug bằng slug của từ khóa, tiêu
    đề rất giống từ khóa (hệ số Dice ≥ 0,8 trên tập từ không dấu), hoặc mọi từ của từ khóa (ít
    nhất 3 từ) nằm trong tiêu đề. Bỏ qua chính bài của dòng này (``wp_post_id``)."""
    keyword_words = frozenset(folded.split())
    if not keyword_words or not posts:
        return None
    keyword_slug = slugify(row.keyword)
    for post in posts:
        if post.id == row.wp_post_id:
            continue
        if (
            (post.slug and post.slug == keyword_slug)
            or similarity(keyword_words, post.words) >= 0.8
            or (len(keyword_words) >= _MIN_SHARED_WORDS and keyword_words <= post.words)
        ):
            return post.id
    return None


# Địa danh TP.HCM trong từ khóa (chữ không dấu): «quận 7», «q7», «q.7», «phường 12», «p.12»,
# «phường Tân Định», «huyện Nhà Bè», «xã …» và tên quận, huyện cũ không có chữ «quận» đứng trước.
# Chạy trên chữ đã ``keyword_key`` (dấu chấm đã thành dấu cách: «P. Tân Định» là «p tan dinh»).
# Viết tắt «q», «p» chỉ nhận khi **đứng riêng** (rồi số hay tên): «phụ kiện» («phu»), «quay chậm»,
# «xài lâu» không phải địa danh (Soi Lỗi SL-T098-8, -14).
_DISTRICTS = (
    "binh thanh", "tan binh", "tan phu", "go vap", "phu nhuan", "binh tan", "thu duc", "nha be",
    "can gio", "cu chi", "hoc mon", "binh chanh",
)  # fmt: skip
_LOCATION = re.compile(
    r"\b(?:quan|q|phuong|p|huyen|xa)\s*\.?\s*\d{1,2}\b"
    r"|\b(?:quan|phuong|huyen|xa|thi tran)\s+[a-z]+(?:\s+[a-z]+)?"
    r"|\b(?:q|p)\s+[a-z]+(?:\s+[a-z]+)?"
    r"|\b(?:" + "|".join(_DISTRICTS) + r")\b"
)


def _location_template(folded: str) -> str | None:
    """Từ khóa (đã ``keyword_key``) bỏ địa danh (khuôn chung); ``None`` nếu không có địa danh."""
    template = " ".join(_LOCATION.sub(" ", folded).split())
    return template if template and template != folded else None

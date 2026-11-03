"""Từ khóa của một bài (T-123; thiết kế T-120 mục 1.7).

- Bảng: từ khóa (chữ thuần), click, hiển thị, CTR, vị trí, chênh vị trí so kỳ trước (nếu kỳ trước
  có). Mặc định ``DEFAULT_ROWS`` dòng đầu theo click; dưới bảng có ghi chú cố định
  ``HIDDEN_QUERIES_NOTE``.
- Gộp cách gõ có dấu, không dấu: các từ khóa cùng ``fold_key`` («sửa cửa sắt», «sua cua sat»,
  «Sửa  cửa sắt») thành một dòng: cộng click, hiển thị; vị trí trung bình theo lượt hiển thị; giữ
  từng cách gõ để mở xem. Từ khóa không có chữ Latin, chữ số nào (``fold_key`` rỗng) không gộp với
  từ khóa khác.
- Dòng trùng **từ khóa chính** của dòng kế hoạch (so ``fold_key``) gắn nhãn «từ khóa chính».
- «Từ khóa mới»: có ở kỳ này, không có ở kỳ trước (chỉ khi đã lấy từ khóa của kỳ trước).

Từ khóa là chữ người lạ gõ (dữ liệu chưa tin cậy): làm sạch lại bằng ``clean_text`` (bỏ ký tự điều
khiển, ký tự vô hình, ký tự đảo hướng chữ; NFC), cắt ``MAX_QUERY_CHARS`` ký tự; rỗng sau khi làm
sạch thì bỏ. Chỉ hiện dạng chữ thuần (LC-T120-11); không đưa vào lời dặn AI hay Google Sheets
(LC-T120-13).
"""

from __future__ import annotations

from collections.abc import Iterable

from seo_app.plan.model import clean_text, fold_key
from seo_app.tracking.match import page_key
from seo_app.tracking.model import (
    CachedQueryLike,
    KeywordGroup,
    KeywordTable,
    KeywordVariant,
    PageKey,
    PageStats,
)
from seo_app.tracking.periods import Period
from seo_app.tracking.stats import row_numbers_ok

MAX_RAW_QUERY_CHARS = 2048  # dài hơn là dòng lạ (thiết kế 2.4)
MAX_QUERY_CHARS = 200
DEFAULT_ROWS = 50
MAIN_KEYWORD_TEXT = "từ khóa chính"
NEW_KEYWORD_TEXT = "từ khóa mới"
HIDDEN_QUERIES_NOTE = (
    "Google ẩn từ khóa hiếm và từ khóa có thông tin cá nhân, nên cộng các dòng ở đây ít hơn tổng "
    "của bài."
)


def query_text(value: object) -> str:
    """Từ khóa đã làm sạch để hiện và gộp; ``""`` khi không dùng được."""
    if not isinstance(value, str) or len(value) > MAX_RAW_QUERY_CHARS:
        return ""
    return clean_text(value)[:MAX_QUERY_CHARS]


def keyword_key(text: str) -> str:
    """Khóa gộp các cách gõ: ``fold_key`` (bỏ dấu, chữ thường, dấu câu thành dấu cách). Chữ không
    có chữ Latin, chữ số nào thì giữ riêng theo đúng chữ (không gộp chung một dòng rỗng)."""
    return fold_key(text) or "=" + text


def page_queries(
    rows: Iterable[CachedQueryLike], *, site: str, key: PageKey, period: Period
) -> list[CachedQueryLike]:
    """Các dòng từ khóa của trang ``key`` (cùng khóa ``match.page_key``: gồm cả địa chỉ chỉ khác
    ``#…``, «/» cuối) trong đúng khoảng đã lấy ``period``."""
    keys: dict[str, PageKey | None] = {}
    found: list[CachedQueryLike] = []
    for row in rows:
        if row.start != period.start or row.end != period.end or not isinstance(row.page, str):
            continue
        if row.page not in keys:
            keys[row.page] = page_key(row.page, site)
        if keys[row.page] == key:
            found.append(row)
    return found


def keyword_table(
    current: Iterable[CachedQueryLike],
    previous: Iterable[CachedQueryLike] | None = None,
    *,
    main_keyword: str = "",
) -> KeywordTable:
    """Bảng từ khóa của một trang: ``current`` là các dòng của kỳ đang xem, ``previous`` của kỳ
    so sánh (``None``: chưa lấy kỳ đó), ``main_keyword``: từ khóa chính của dòng kế hoạch."""
    now, skipped = _collect(current)
    before, skipped_before = ({}, 0) if previous is None else _collect(previous)
    main = fold_key(main_keyword)
    groups: list[KeywordGroup] = []
    for key, variants in now.items():
        ordered = sorted(
            variants.items(), key=lambda entry: (-entry[1].impressions, -entry[1].clicks, entry[0])
        )
        earlier = before.get(key)
        groups.append(
            KeywordGroup(
                key=key,
                text=ordered[0][0],
                current=_total(variants.values()),
                previous=None if earlier is None else _total(earlier.values()),
                variants=tuple(KeywordVariant(text, stats) for text, stats in ordered),
                is_main=bool(main) and key == main,
                is_new=previous is not None and earlier is None,
            )
        )
    groups.sort(key=lambda group: (-group.current.clicks, -group.current.impressions, group.text))
    return KeywordTable(tuple(groups), skipped + skipped_before, previous is not None)


def has_keyword(table: KeywordTable, keyword: str) -> bool | None:
    """Bảng có từ khóa trùng ``keyword`` (so ``fold_key``); ``None`` khi ``keyword`` không có chữ
    Latin, chữ số nào để so (khi đó không kết luận được gì)."""
    key = fold_key(keyword)
    if not key:
        return None
    return any(group.key == key for group in table.groups)


def _collect(rows: Iterable[CachedQueryLike]) -> tuple[dict[str, dict[str, PageStats]], int]:
    """Gộp các dòng theo khóa từ khóa rồi theo cách gõ; dòng sai dạng bị bỏ và đếm."""
    groups: dict[str, dict[str, PageStats]] = {}
    skipped = 0
    for row in rows:
        text = query_text(row.query)
        if not text or not row_numbers_ok(row.clicks, row.impressions, row.position_sum):
            skipped += 1
            continue
        stats = PageStats(row.clicks, row.impressions, float(row.position_sum))
        variants = groups.setdefault(keyword_key(text), {})
        variants[text] = variants[text] + stats if text in variants else stats
    return groups, skipped


def _total(parts: Iterable[PageStats]) -> PageStats:
    total = PageStats()
    for part in parts:
        total += part
    return total

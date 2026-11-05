"""Khớp địa chỉ trang của Search Console với bài, trang WordPress và dòng kế hoạch (T-123; thiết
kế T-120 mục 1.4).

``page_key`` dựng khóa so khớp theo 5 bước:

1. Địa chỉ phải qua ``is_site_link`` (``https://``, đúng tên máy và cổng của ``WORDPRESS_URL``)
   **và** bắt đầu bằng tiền tố của website (``site_base`` + ``/``: ``WORDPRESS_URL`` với scheme,
   tên máy viết thường, như bộ lọc client Search Console T-121 gửi Google). Sai thì là «dòng lạ»,
   bị bỏ dù Google có trả (staging, ``www.``, ``http://``, tên miền khác; LC-T120-6).
2. Bỏ phần ``#…`` (vẫn là cùng một trang); các dòng trùng khóa sau khi bỏ được cộng dồn.
3. Có ``?…`` (``?s=``, ``?p=``…): giữ riêng, xếp vào «Trang khác», không gán cho bài.
4. Đường dẫn giải mã ``%`` (UTF-8 hỏng là dòng lạ), chuẩn NFC, bỏ một «/» cuối (trừ trang chủ),
   giữ nguyên chữ hoa, chữ thường.
5. Link của mọi bài, trang trong danh sách đã đăng (``SiteIndex``) chuẩn hóa cùng cách để tra.

``build_tracking`` gán số liệu từng ngày cho bài, trang; địa chỉ có số liệu mà không khớp bài, trang
nào vào «Trang khác trên website» (trang chủ không phải trang tĩnh, chuyên mục, thẻ, địa chỉ cũ
trước khi đổi slug, trang tìm kiếm…); nối dòng kế hoạch với bài (``match_plan``). Địa chỉ luôn lấy
từ danh sách đã đăng (WordPress) và Search Console, cả hai qua ``is_site_link``; **không bao giờ**
từ Google Sheets (Sheet chỉ giữ mã bài, LC-T094-20).

Đường dẫn để hiện (``page_label``) đã giải mã ``%`` rồi qua ``clean_text`` (bỏ ký tự điều khiển,
ký tự vô hình, ký tự đảo hướng chữ), cắt ``LABEL_CHARS`` ký tự. Đó là chữ thuần: giao diện không
bao giờ dựng link từ nó (LC-T120-19).
"""

from __future__ import annotations

import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import date
from urllib.parse import unquote

from seo_app.plan import model as plan_model
from seo_app.plan.model import PlanRow, clean_text
from seo_app.tracking.model import (
    CachedDayLike,
    DayTotal,
    MatchStatus,
    PageKey,
    PlanMatch,
    SiteTracking,
    TrackedPage,
)
from seo_app.tracking.periods import is_day
from seo_app.tracking.stats import row_numbers_ok
from seo_app.wordpress.client import (
    MAX_LINK_CHARS,
    PublishedItem,
    is_site_link,
    site_base,
    site_link,
)

MAX_PAGE_CHARS = MAX_LINK_CHARS  # 2.000 ký tự, như kiểm câu trả lời Google (thiết kế 2.4)
LABEL_CHARS = 120
HOME = PageKey("/")
HOME_LABEL = "/ (trang chủ)"
# Trạng thái kế hoạch cho biết bài đã lên website; Chưa viết, Đang viết, Đã gửi nháp, Đã hẹn giờ
# là chưa lên (thiết kế 1.4), «Bỏ» thì không theo dõi.
LIVE_STATUSES = frozenset({plan_model.STATUS_PUBLISHED})
# Câu cố định cho từng kết quả nối dòng kế hoạch (giao diện hiện cạnh Mã bài).
MATCH_TEXT = {
    MatchStatus.BY_ID: "Khớp theo mã bài WordPress",
    MatchStatus.BY_SLUG: "Khớp theo slug",
    MatchStatus.NOT_LIVE: "Chưa lên website",
    MatchStatus.NOT_FOUND: "Không thấy bài trong danh sách bài đã đăng",
    MatchStatus.AMBIGUOUS: "Slug trùng nhiều bài: chưa nối, ghi «Mã bài WordPress» để nối",
    MatchStatus.DUPLICATE: "Nhiều dòng kế hoạch cùng một bài: chưa nối",
    MatchStatus.DROPPED: "Dòng «Bỏ»: không theo dõi",
}


def page_key(url: object, site: str) -> PageKey | None:
    """Khóa so khớp của địa chỉ ``url`` trên website ``site`` (``WORDPRESS_URL``); ``None``: dòng
    lạ (ngoài website, quá dài, ``%`` giải mã ra UTF-8 hỏng)."""
    if not isinstance(url, str) or not isinstance(site, str) or len(url) > MAX_PAGE_CHARS:
        return None
    base = site_base(site)
    prefix = base + "/"
    if not url.startswith(prefix) or not is_site_link(url, base):
        return None
    rest = url[len(prefix) :].split("#", 1)[0]
    raw_path, mark, raw_query = rest.partition("?")
    try:
        path = unquote(raw_path, errors="strict")
        query = unquote(raw_query, errors="strict") if mark else None
    except UnicodeDecodeError:
        return None
    path = unicodedata.normalize("NFC", path)
    if path.endswith("/"):
        path = path[:-1]
    if query is not None:
        query = unicodedata.normalize("NFC", query)
    return PageKey("/" + path, query)


def page_label(key: PageKey) -> str:
    """Đường dẫn để hiện (chữ thuần): đã làm sạch, cắt ``LABEL_CHARS`` ký tự; trang chủ là
    ``HOME_LABEL``."""
    if key == HOME:
        return HOME_LABEL
    text = clean_text(str(key))
    return text if len(text) <= LABEL_CHARS else text[: LABEL_CHARS - 1] + "…"


def match_plan(rows: Iterable[PlanRow], items: Iterable[PublishedItem]) -> tuple[PlanMatch, ...]:
    """Nối từng dòng kế hoạch với một bài (``type == "post"``) trong danh sách đã đăng.

    1. Dòng «Bỏ»: không theo dõi.
    2. «Mã bài WordPress» là mã của một bài trong danh sách: khớp, kể cả khi trạng thái trên Sheet
       chưa cập nhật (bài có trong danh sách đã đăng thì đã lên website).
    3. Trạng thái chưa lên website (Chưa viết, Đang viết, Đã gửi nháp, Đã hẹn giờ): «Chưa lên
       website», không có số liệu. Dòng «Đã đăng» có mã mà không thấy bài, hay không có cả mã lẫn
       slug: «không thấy».
    4. Dòng «Đã đăng» chưa có mã: so slug, chỉ nhận khi đúng **một** bài khớp; nhiều bài: «slug
       trùng», không đoán.
    5. Một bài chỉ nối một dòng: nhiều dòng cùng mã bài thì các dòng đó đều «trùng»; dòng khớp
       slug với bài đã có dòng khớp mã (hay với bài mà dòng khác cũng khớp slug) cũng «trùng».
    """
    posts = [item for item in items if item.type == "post"]
    by_id = {item.id: item for item in posts}
    by_slug: dict[str, list[PublishedItem]] = defaultdict(list)
    for item in posts:
        if item.slug:
            by_slug[item.slug].append(item)
    found: list[PlanMatch] = []
    for row in rows:
        if row.status == plan_model.STATUS_DROPPED:
            found.append(PlanMatch(row, MatchStatus.DROPPED))
        elif row.wp_post_id is not None and row.wp_post_id in by_id:
            found.append(PlanMatch(row, MatchStatus.BY_ID, by_id[row.wp_post_id]))
        elif row.status not in LIVE_STATUSES:
            found.append(PlanMatch(row, MatchStatus.NOT_LIVE))
        elif row.wp_post_id is not None or not row.slug:
            found.append(PlanMatch(row, MatchStatus.NOT_FOUND))
        else:
            candidates = by_slug.get(row.slug, [])
            if len(candidates) == 1:
                found.append(PlanMatch(row, MatchStatus.BY_SLUG, candidates[0]))
            else:
                status = MatchStatus.AMBIGUOUS if candidates else MatchStatus.NOT_FOUND
                found.append(PlanMatch(row, status))
    id_claims = Counter(match.item.id for match in found if match.status is MatchStatus.BY_ID)
    slug_claims = Counter(match.item.id for match in found if match.status is MatchStatus.BY_SLUG)
    return tuple(
        PlanMatch(match.row, MatchStatus.DUPLICATE)
        if _taken(match, id_claims, slug_claims)
        else match
        for match in found
    )


def build_tracking(
    site: str,
    items: Iterable[PublishedItem],
    days: Iterable[CachedDayLike],
    plan_rows: Iterable[PlanRow] = (),
) -> SiteTracking:
    """Khớp số liệu từng ngày (cache Search Console) với bài, trang đã đăng của ``site`` và với
    dòng kế hoạch. Mọi bài, trang đều có trong ``pages`` (kể cả chưa có số liệu, để nhận nhãn
    «chưa có lượt hiển thị»); dòng số liệu ngoài website hay sai dạng bị bỏ và đếm."""
    tracked: dict[PageKey, PublishedItem] = {}
    skipped_items = 0
    for item in sorted(items, key=lambda entry: entry.id):
        link = item.link
        if is_site_link(link, site):
            # LC-T123-1: ô «Địa chỉ trang» của WordPress gõ chữ hoa thì link bài viết hoa tên máy.
            # ``is_site_link`` đã chứng minh cùng tên máy, cùng cổng: viết thường để so tiền tố.
            link = site_link(link)
        key = page_key(link, site)
        # WordPress không cho hai bài cùng địa chỉ; dữ liệu lạ có trùng thì mã nhỏ hơn giữ khóa.
        if key is None or key.query is not None or key in tracked:
            skipped_items += 1
            continue
        tracked[key] = item

    sums: dict[PageKey, dict[date, DayTotal]] = defaultdict(dict)
    keys: dict[str, PageKey | None] = {}  # mỗi địa chỉ chỉ dựng khóa một lần
    skipped_rows = 0
    for row in days:
        if not _day_row_ok(row):
            skipped_rows += 1
            continue
        if row.page not in keys:
            keys[row.page] = page_key(row.page, site)
        key = keys[row.page]
        if key is None:
            skipped_rows += 1
            continue
        per_day = sums[key]
        before = per_day.get(row.day)
        if before is None:
            per_day[row.day] = DayTotal(
                row.day, row.clicks, row.impressions, float(row.position_sum), row.final
            )
        else:
            per_day[row.day] = DayTotal(
                row.day,
                before.clicks + row.clicks,
                before.impressions + row.impressions,
                before.position_sum + row.position_sum,
                before.final and row.final,
            )

    matches = match_plan(plan_rows, tracked.values())
    plan_of = {match.item.id: match.row for match in matches if match.item is not None}
    pages = tuple(
        TrackedPage(
            key,
            item.title or page_label(key),
            item,
            plan_of.get(item.id),
            _ordered(sums.pop(key, {})),
        )
        for key, item in tracked.items()
    )
    others = tuple(
        TrackedPage(key, page_label(key), None, None, _ordered(per_day))
        for key, per_day in sorted(sums.items(), key=lambda entry: _sort_key(entry[0]))
    )
    return SiteTracking(pages, others, matches, skipped_rows, skipped_items)


def _taken(match: PlanMatch, id_claims: Counter[int], slug_claims: Counter[int]) -> bool:
    """Bài của ``match`` còn dòng kế hoạch khác giành (bước 5 của ``match_plan``)."""
    if match.item is None:
        return False
    post = match.item.id
    if match.status is MatchStatus.BY_ID:
        return id_claims[post] > 1
    return id_claims[post] > 0 or slug_claims[post] > 1


def _day_row_ok(row: CachedDayLike) -> bool:
    """Dòng «ngày × trang» đúng khuôn 3.1 (kiểm thêm, sau cache): ngày thuần trong khoảng năm,
    địa chỉ là chữ, ``final`` là ``bool``, số đúng dạng (thiết kế 2.4)."""
    return (
        is_day(row.day)
        and isinstance(row.page, str)
        and type(row.final) is bool
        and row_numbers_ok(row.clicks, row.impressions, row.position_sum)
    )


def _ordered(per_day: dict[date, DayTotal]) -> tuple[DayTotal, ...]:
    return tuple(per_day[day] for day in sorted(per_day))


def _sort_key(key: PageKey) -> tuple[str, bool, str]:
    return key.path, key.query is not None, key.query or ""

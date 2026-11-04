"""T-122 (Thợ Máy): cache số liệu Search Console trong máy (``seo_app.storage.search_cache``;
thiết kế T-120 mục 3.1–3.4).

- Ghi theo đoạn, phần đã lấy liền mạch, ngày tạm đầu tiên, giữ 16 tháng, ≤ 6 khoảng từ khóa, trần.
- LC-T120-9: cấu trúc file và từng dòng kiểm khi đọc như ``plan_cache``; một dòng sai, mã băm phạm
  vi khác là bỏ cả cache; ``data/`` là liên kết thì không tạo, không mở (``dir_has_link``, T-117);
  chính file hay file nhật ký là liên kết thì chỉ gỡ liên kết; SQL chỉ dùng tham số ``?``.
- LC-T120-10: mốc ngày giờ kiểm năm trước khi đổi múi giờ hay cộng trừ; không lọt
  ``OverflowError``, ``ValueError``.
- LC-T120-15: không gọi mạng (bộ chặn của ``conftest.py``); các ca biên của thiết kế 2.4 với dữ
  liệu đọc lại từ file.

Liên kết thật: junction trên Windows (``_winapi.CreateJunction``, không cần quyền quản trị),
symlink trên Mac/Linux; hard link bằng ``os.link``. Mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import ast
import dataclasses
import os
import sqlite3
from contextlib import closing
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from seo_app.images.data_dir import MSG_DATA_DIR_LINK
from seo_app.storage import search_cache
from seo_app.storage.search_cache import (
    KEEP_DAYS,
    MAX_QUERY_RANGES,
    MSG_BAD_DATA,
    MSG_BAD_RANGE,
    MSG_BAD_SCOPE,
    MSG_BUSY,
    MSG_FULL,
    CachedDay,
    CachedQuery,
    CacheScope,
    SearchCacheError,
    SearchCacheStore,
)

IS_WINDOWS = os.name == "nt"
VN = ZoneInfo("Asia/Ho_Chi_Minh")
SITE = "https://suachuacuasat.com"
SCOPE = CacheScope("sc-domain:suachuacuasat.com", SITE)
TODAY = date(2026, 11, 3)  # hôm nay theo giờ PT trong các ví dụ
NOW = datetime(2026, 11, 3, 15, 0, tzinfo=VN)
OCT = (date(2026, 10, 4), date(2026, 10, 31))  # 28 ngày


def day(when: date, path: str = "/a/", clicks: int = 1, impressions: int = 10, *, final=True):
    return CachedDay(when, SITE + path, clicks, impressions, 2.0 * impressions, final)


def query(text: str, path: str = "/a/", clicks: int = 1, impressions: int = 10, span=OCT):
    return CachedQuery(span[0], span[1], SITE + path, text, clicks, impressions, 3.0 * impressions)


def days_between(start: date, end: date, **kwargs) -> list[CachedDay]:
    return [day(start + timedelta(days=n), **kwargs) for n in range((end - start).days + 1)]


def link_dir(link: Path, target: Path) -> None:
    """Liên kết thư mục không cần quyền quản trị: junction trên Windows, symlink trên Mac/Linux."""
    if IS_WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả; ``PROJECT_ROOT`` của module trỏ vào đó."""
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def store(project: Path) -> SearchCacheStore:
    return SearchCacheStore(path=project / "data" / "search_cache.sqlite")


def save_october(store: SearchCacheStore, **kwargs) -> None:
    """Ghi 28 ngày tháng 10 (đã chốt), mỗi ngày một dòng trang /a/."""
    store.save_days(
        SCOPE,
        days_between(*OCT, **kwargs),
        start=OCT[0],
        end=OCT[1],
        first_provisional=None,
        fetched_at=NOW,
        today=TODAY,
    )


def save_tail(store: SearchCacheStore, rows, *, start, end=TODAY, first=None, today=TODAY):
    store.save_days(
        SCOPE, rows, start=start, end=end, first_provisional=first, fetched_at=NOW, today=today
    )


def run_sql(store: SearchCacheStore, sql: str, params: tuple = ()) -> None:
    """Sửa tay file cache (giả lập file bị sửa, ngoài app)."""
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute(sql, params)


# ===================================================================== ghi, đọc lại


def test_empty_cache_is_none(store):
    assert store.load(SCOPE) is None
    assert store.path.is_file()  # file trống đã có bảng, chưa có thông tin


def test_round_trip_types_match_tracking_protocols(store):
    """Kiểu đọc ra khớp hai ``Protocol`` của gói tính toán (T-123): đúng tên trường thiết kế 3.1,
    ``date`` thuần, ``bool`` thật, số ``int``/``float`` thật."""
    save_october(store)
    store.save_queries(
        SCOPE, [query("sửa cửa sắt")], start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False
    )
    cache = store.load(SCOPE)
    assert [f.name for f in dataclasses.fields(CachedDay)] == [
        "day",
        "page",
        "clicks",
        "impressions",
        "position_sum",
        "final",
    ]
    assert [f.name for f in dataclasses.fields(CachedQuery)] == [
        "start",
        "end",
        "page",
        "query",
        "clicks",
        "impressions",
        "position_sum",
    ]
    first = cache.days[0]
    assert first == CachedDay(OCT[0], SITE + "/a/", 1, 10, 20.0, True)
    assert type(first.day) is date and type(first.final) is bool
    assert type(first.clicks) is int and type(first.impressions) is int
    assert type(first.position_sum) is float
    (row,) = cache.queries
    assert row == CachedQuery(*OCT, SITE + "/a/", "sửa cửa sắt", 1, 10, 30.0)
    assert type(row.start) is date and type(row.end) is date
    assert len(cache.days) == 28
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (*OCT, None)
    assert cache.final_end == OCT[1]
    assert cache.fetched_at == NOW and cache.fetched_at.tzinfo is not None


def test_fetched_at_is_stored_in_vietnam_time(store):
    utc = datetime(2026, 11, 3, 8, 0, tzinfo=UTC)
    store.save_days(
        SCOPE, [], start=TODAY, end=TODAY, first_provisional=TODAY, fetched_at=utc, today=TODAY
    )
    fetched = store.load(SCOPE).fetched_at
    assert fetched == datetime(2026, 11, 3, 15, 0, tzinfo=VN)
    assert fetched.utcoffset() == timedelta(hours=7)


def test_chunks_extend_coverage_and_track_provisional_days(store):
    """Lần đầu: các đoạn nối nhau từ cũ tới mới. Đoạn mới nhất có số tạm; ngày tạm không có dòng
    nào thì E vẫn đúng (ngày trước ngày tạm đầu tiên)."""
    save_october(store)
    save_tail(store, [day(date(2026, 11, 1))], start=date(2026, 11, 1), first=date(2026, 11, 2))
    cache = store.load(SCOPE)
    assert (cache.covered_start, cache.covered_end) == (OCT[0], TODAY)
    assert cache.first_provisional == date(2026, 11, 2)
    assert cache.final_end == date(2026, 11, 1)  # 02/11, 03/11 là số tạm (không có dòng nào)
    # Hôm sau: lấy lại từ ngày tạm đầu tiên; số tạm cũ bị thay.
    save_tail(
        store,
        [day(date(2026, 11, 2), clicks=5), day(date(2026, 11, 4), final=False)],
        start=date(2026, 11, 2),
        end=date(2026, 11, 4),
        first=date(2026, 11, 3),
        today=date(2026, 11, 4),
    )
    cache = store.load(SCOPE)
    assert cache.covered_end == date(2026, 11, 4) and cache.final_end == date(2026, 11, 2)
    tail = [(row.day, row.clicks, row.final) for row in cache.days if row.day > OCT[1]]
    assert tail == [
        (date(2026, 11, 1), 1, True),
        (date(2026, 11, 2), 5, True),
        (date(2026, 11, 4), 1, False),
    ]


def test_whole_chunk_provisional_and_first_after_end(store):
    """Ngày tạm trước đoạn: cả đoạn là số tạm; ngày tạm sau đoạn: cả đoạn đã chốt."""
    save_tail(store, [day(TODAY, final=False)], start=TODAY, first=date(2026, 10, 1))
    cache = store.load(SCOPE)
    assert cache.first_provisional == TODAY and cache.final_end is None  # chưa có ngày đã chốt
    with pytest.raises(SearchCacheError) as caught:  # đoạn cũ hơn, không nối từ phía mới nhất
        save_october(store)
    assert str(caught.value) == MSG_BAD_RANGE
    store.clear()
    store.save_days(
        SCOPE,
        days_between(*OCT),
        start=OCT[0],
        end=OCT[1],
        first_provisional=TODAY,  # sau đoạn: cả đoạn đã chốt
        fetched_at=NOW,
        today=TODAY,
    )
    cache = store.load(SCOPE)
    assert cache.first_provisional is None and cache.final_end == OCT[1]


def test_older_final_chunk_inside_coverage_is_replaced(store):
    save_october(store)
    save_tail(store, [], start=date(2026, 11, 1), first=date(2026, 11, 2))
    inside = (date(2026, 10, 10), date(2026, 10, 12))
    store.save_days(
        SCOPE,
        days_between(*inside, clicks=9),
        start=inside[0],
        end=inside[1],
        first_provisional=None,
        fetched_at=NOW,
        today=TODAY,
    )
    cache = store.load(SCOPE)
    assert [row.clicks for row in cache.days if inside[0] <= row.day <= inside[1]] == [9, 9, 9]
    assert (cache.covered_start, cache.covered_end) == (OCT[0], TODAY)
    assert cache.first_provisional == date(2026, 11, 2)


@pytest.mark.parametrize(
    ("start", "end", "first"),
    [
        (date(2026, 11, 2), date(2026, 11, 3), None),  # để hở 01/11 (sau covered_end + 1)
        (date(2026, 10, 20), date(2026, 10, 25), date(2026, 10, 24)),  # số tạm giữa phần đã chốt
        (date(2026, 9, 1), date(2026, 9, 20), None),  # trước phần đã lưu, không nối liền
        (date(2026, 9, 25), date(2026, 10, 5), None),  # lấn ra trước, không tới covered_end
    ],
    ids=["ho-sau", "tam-o-giua", "truoc-ho", "lan-truoc"],
)
def test_chunk_must_join_the_stored_range(store, start, end, first):
    save_october(store)
    before = store.load(SCOPE)
    with pytest.raises(SearchCacheError) as caught:
        save_tail(store, [], start=start, end=end, first=first)
    assert str(caught.value) == MSG_BAD_RANGE
    assert store.load(SCOPE) == before  # lỗi thì không ghi gì


def test_refresh_must_start_at_first_provisional_day(store):
    save_october(store)
    save_tail(store, [], start=date(2026, 11, 1), first=date(2026, 11, 2))
    with pytest.raises(SearchCacheError) as caught:  # bỏ sót số tạm 02/11
        save_tail(
            store, [], start=date(2026, 11, 3), end=date(2026, 11, 4), today=date(2026, 11, 4)
        )
    assert str(caught.value) == MSG_BAD_RANGE


def test_retention_keeps_16_months(store):
    """Mỗi lần ghi bỏ ngày cũ hơn ``KEEP_DAYS`` ngày; phần đã lấy liền mạch co theo."""
    save_october(store)
    later = OCT[0] + timedelta(days=KEEP_DAYS + 9)  # ngày 04/10 đã quá 16 tháng + 9 ngày
    cutoff = later - timedelta(days=KEEP_DAYS - 1)
    with pytest.raises(SearchCacheError):  # phần đã lưu quá cũ, đoạn mới không nối liền
        save_tail(store, [], start=later, end=later, today=later)
    first_ok = OCT[1] + timedelta(days=1)
    gap_free = days_between(first_ok, first_ok + timedelta(days=30))
    save_tail(store, gap_free, start=first_ok, end=first_ok + timedelta(days=30), today=later)
    cache = store.load(SCOPE)
    assert cache.covered_start == cutoff and min(row.day for row in cache.days) == cutoff
    assert cache.covered_end == first_ok + timedelta(days=30)


def test_too_old_cache_restarts_from_new_chunk(store):
    save_october(store)
    far = OCT[1] + timedelta(days=KEEP_DAYS + 40)
    save_tail(store, [day(far, final=False)], start=far, end=far, first=far, today=far)
    cache = store.load(SCOPE)
    assert (cache.covered_start, cache.covered_end) == (far, far)
    assert [row.day for row in cache.days] == [far]


def test_duplicate_pages_after_fragment_are_merged(store):
    rows = [
        day(OCT[0], "/a/", 1, 10),
        day(OCT[0], "/a/#bang-gia", 2, 30),
        day(OCT[0], "/b/", 1, 5),
    ]
    store.save_days(
        SCOPE, rows, start=OCT[0], end=OCT[0], first_provisional=None, fetched_at=NOW, today=TODAY
    )
    cache = store.load(SCOPE)
    assert [(row.page, row.clicks, row.impressions, row.position_sum) for row in cache.days] == [
        (SITE + "/a/", 3, 40, 80.0),
        (SITE + "/b/", 1, 5, 10.0),
    ]


BAD_DAY_ROWS = {
    "click-bool": CachedDay(OCT[0], SITE + "/a/", True, 10, 20.0, True),
    "hien-thi-so-thuc": CachedDay(OCT[0], SITE + "/a/", 1, 10.0, 20.0, True),
    "click-lon-hon-hien-thi": CachedDay(OCT[0], SITE + "/a/", 11, 10, 20.0, True),
    "hien-thi-0": CachedDay(OCT[0], SITE + "/a/", 0, 0, 0.0, True),
    "vi-tri-0": CachedDay(OCT[0], SITE + "/a/", 0, 10, 0.0, True),
    "vi-tri-nan": CachedDay(OCT[0], SITE + "/a/", 0, 10, float("nan"), True),
    "vi-tri-vo-cung": CachedDay(OCT[0], SITE + "/a/", 0, 10, float("inf"), True),
    "qua-1-ty": CachedDay(OCT[0], SITE + "/a/", 0, 10**9 + 1, 2.0e9, True),
    "final-so": CachedDay(OCT[0], SITE + "/a/", 1, 10, 20.0, 1),
    "final-sai-tam": CachedDay(OCT[0], SITE + "/a/", 1, 10, 20.0, False),
    "ngay-datetime": CachedDay(datetime(2026, 10, 4), SITE + "/a/", 1, 10, 20.0, True),
    "ngay-ngoai-doan": CachedDay(date(2026, 9, 1), SITE + "/a/", 1, 10, 20.0, True),
    "staging": CachedDay(OCT[0], "https://www.staging-m.suachuacuasat.com/a/", 1, 10, 20.0, True),
    "www": CachedDay(OCT[0], "https://www.suachuacuasat.com/a/", 1, 10, 20.0, True),
    "http": CachedDay(OCT[0], "http://suachuacuasat.com/a/", 1, 10, 20.0, True),
    "ten-mien-khac": CachedDay(
        OCT[0], "https://suachuacuasat.com.evil.example/a/", 1, 10, 20.0, True
    ),
    "qua-2000-ky-tu": CachedDay(OCT[0], SITE + "/" + "a" * 2000, 1, 10, 20.0, True),
    "trang-none": CachedDay(OCT[0], None, 1, 10, 20.0, True),
    "khong-phai-dong": "khong-phai-dong",
}


@pytest.mark.parametrize("bad", list(BAD_DAY_ROWS.values()), ids=list(BAD_DAY_ROWS))
def test_bad_rows_are_refused_and_nothing_is_written(store, bad):
    save_october(store)
    before = store.load(SCOPE)
    with pytest.raises(SearchCacheError) as caught:
        store.save_days(
            SCOPE,
            [day(OCT[0]), bad],
            start=OCT[0],
            end=OCT[1],
            first_provisional=None,
            fetched_at=NOW,
            today=TODAY,
        )
    assert str(caught.value) == MSG_BAD_DATA
    assert store.load(SCOPE) == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"start": OCT[1], "end": OCT[0]},  # ngược
        {"start": date(2026, 9, 1), "end": date(2026, 10, 2)},  # 32 ngày
        {"start": TODAY, "end": TODAY + timedelta(days=1)},  # sau hôm nay
        {"start": TODAY - timedelta(days=KEEP_DAYS), "end": TODAY - timedelta(days=KEEP_DAYS)},
        {"start": datetime(2026, 10, 4), "end": OCT[1]},
        {"start": date(1, 1, 1), "end": OCT[1]},  # không tràn khi trừ ngày
        {"start": OCT[0], "end": OCT[1], "today": date.max},
        {"start": OCT[0], "end": OCT[1], "first_provisional": "2026-10-30"},
        {
            "start": OCT[0],
            "end": OCT[1],
            "fetched_at": datetime(2026, 11, 3, 15, 0),
        },  # không múi giờ
        {"start": OCT[0], "end": OCT[1], "fetched_at": datetime(1, 1, 1, tzinfo=UTC)},
        {"start": OCT[0], "end": OCT[1], "fetched_at": datetime(9999, 12, 31, tzinfo=UTC)},
        {"start": OCT[0], "end": OCT[1], "fetched_at": "2026-11-03T15:00:00+07:00"},
    ],
    ids=[
        "nguoc",
        "32-ngay",
        "tuong-lai",
        "qua-16-thang",
        "datetime",
        "nam-1",
        "today-max",
        "tam-la-chu",
        "khong-mui-gio",
        "gio-nam-1",
        "gio-nam-9999",
        "gio-la-chu",
    ],
)
def test_bad_chunk_arguments_give_fixed_message(store, kwargs):
    """LC-T120-10: mọi ngày, mốc giờ lạ ra câu cố định; không lọt ``OverflowError``,
    ``ValueError``."""
    args = {"first_provisional": None, "fetched_at": NOW, "today": TODAY, **kwargs}
    with pytest.raises(SearchCacheError) as caught:
        store.save_days(SCOPE, [], **args)
    assert str(caught.value) == MSG_BAD_DATA


def test_scope_must_be_valid(store):
    for scope in (None, CacheScope("", SITE), CacheScope("sc-domain:a\nb", SITE)):
        with pytest.raises(SearchCacheError) as caught:
            store.load(scope)
        assert str(caught.value) == MSG_BAD_SCOPE


# ===================================================================== từ khóa, ngày đăng


def test_query_ranges_replace_and_keep_newest_six(store):
    spans = [
        (date(2026, 10, 1) + timedelta(days=n), date(2026, 10, 28) + timedelta(days=n))
        for n in range(8)
    ]
    for n, span in enumerate(spans):
        store.save_queries(
            SCOPE,
            [query(f"từ khóa {n}", span=span)],
            start=span[0],
            end=span[1],
            fetched_at=NOW + timedelta(minutes=n),
            truncated=n == 3,
        )
    cache = store.load(SCOPE)
    assert [(item.start, item.end) for item in cache.ranges] == spans[2:]  # bỏ hai khoảng lâu nhất
    assert len(cache.ranges) == MAX_QUERY_RANGES
    assert [item.truncated for item in cache.ranges] == [False, True, False, False, False, False]
    assert [row.query for row in cache.queries_for(*spans[2])] == ["từ khóa 2"]
    assert cache.queries_for(*spans[0]) == () and not cache.has_range(*spans[0])
    # Lấy lại khoảng cũ nhất còn giữ: thay dòng, khoảng đó thành mới nhất.
    store.save_queries(
        SCOPE,
        [query("mới", span=spans[2]), query("mới", "/b/", span=spans[2])],
        start=spans[2][0],
        end=spans[2][1],
        fetched_at=NOW + timedelta(hours=1),
        truncated=False,
    )
    cache = store.load(SCOPE)
    assert (cache.ranges[-1].start, cache.ranges[-1].row_count) == (spans[2][0], 2)
    assert [row.page for row in cache.queries_for(*spans[2])] == [SITE + "/a/", SITE + "/b/"]


def test_query_rows_merge_and_validate(store):
    rows = [query("cửa sắt", "/a/", 1, 10), query("cửa sắt", "/a/#x", 2, 20), query("cửa cuốn")]
    store.save_queries(SCOPE, rows, start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False)
    cache = store.load(SCOPE)
    assert [(row.query, row.clicks, row.impressions) for row in cache.queries] == [
        ("cửa cuốn", 1, 10),
        ("cửa sắt", 3, 30),
    ]
    assert cache.ranges[0].row_count == 2


@pytest.mark.parametrize(
    "bad",
    [
        query("c\N{RIGHT-TO-LEFT OVERRIDE}ửa"),  # chưa làm sạch
        query("cửa  sắt"),  # hai dấu cách: chưa làm sạch
        query(""),
        query("x" * 201),
        query("cửa", span=(OCT[0], date(2026, 10, 30))),  # khác khoảng đang ghi
        query("cửa", path="/a/", clicks=11, impressions=10),
        CachedQuery(*OCT, "https://www.suachuacuasat.com/a/", "cửa", 1, 10, 30.0),
        CachedQuery(*OCT, SITE + "/a/", None, 1, 10, 30.0),
        CachedQuery(*OCT, SITE + "/a/", "cửa", 1, 10, float("nan")),
    ],
    ids=[
        "dao-huong",
        "hai-dau-cach",
        "rong",
        "201-ky-tu",
        "khac-khoang",
        "click-lon",
        "www",
        "none",
        "nan",
    ],
)
def test_bad_query_rows_are_refused(store, bad):
    with pytest.raises(SearchCacheError) as caught:
        store.save_queries(SCOPE, [bad], start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False)
    assert str(caught.value) == MSG_BAD_DATA


@pytest.mark.parametrize(
    "kwargs",
    [
        {"start": OCT[1], "end": OCT[0]},
        {"start": date(2026, 7, 1), "end": date(2026, 10, 2)},  # 94 ngày
        {"truncated": 1},
        {"fetched_at": datetime(2026, 11, 3)},
    ],
    ids=["nguoc", "94-ngay", "truncated-so", "khong-mui-gio"],
)
def test_bad_query_range_arguments(store, kwargs):
    args = {"start": OCT[0], "end": OCT[1], "fetched_at": NOW, "truncated": False, **kwargs}
    with pytest.raises(SearchCacheError) as caught:
        store.save_queries(SCOPE, [], **args)
    assert str(caught.value) == MSG_BAD_DATA


def test_post_dates_keep_only_posts_still_listed(store):
    store.save_post_dates(SCOPE, {12: date(2026, 9, 1), 13: date(2026, 10, 30)})
    store.save_post_dates(SCOPE, {14: date(2026, 11, 1)}, keep=[13, 14])
    assert dict(store.load(SCOPE).post_dates) == {13: date(2026, 10, 30), 14: date(2026, 11, 1)}


@pytest.mark.parametrize(
    "dates",
    [
        {0: TODAY},
        {True: TODAY},
        {2**31: TODAY},
        {"12": TODAY},
        {12: datetime(2026, 9, 1)},
        {12: "x"},
    ],
    ids=["ma-0", "bool", "qua-2-31", "chu", "datetime", "ngay-chu"],
)
def test_bad_post_dates(store, dates):
    with pytest.raises(SearchCacheError) as caught:
        store.save_post_dates(SCOPE, dates)
    assert str(caught.value) == MSG_BAD_DATA


# ===================================================================== trần (thiết kế 3.2)


def test_day_row_cap(store, monkeypatch):
    save_october(store)
    monkeypatch.setattr(search_cache, "MAX_DAY_ROWS", 30)
    before = store.load(SCOPE)
    with pytest.raises(SearchCacheError) as caught:  # 28 + 3 dòng > 30
        save_tail(
            store,
            [day(date(2026, 11, 1)), day(date(2026, 11, 2)), day(TODAY)],
            start=date(2026, 11, 1),
        )
    assert str(caught.value) == MSG_FULL
    assert store.load(SCOPE) == before  # giữ phần đang có
    with pytest.raises(SearchCacheError) as caught:  # một đoạn đã quá trần: không mở file
        monkeypatch.setattr(search_cache, "MAX_DAY_ROWS", 2)
        save_tail(store, days_between(date(2026, 11, 1), TODAY), start=date(2026, 11, 1))
    assert str(caught.value) == MSG_FULL


def test_query_row_cap(store, monkeypatch):
    monkeypatch.setattr(search_cache, "MAX_QUERY_ROWS", 2)
    rows = [query("a"), query("b"), query("c")]
    with pytest.raises(SearchCacheError) as caught:
        store.save_queries(SCOPE, rows, start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=True)
    assert str(caught.value) == MSG_FULL


def test_file_size_cap_refuses_write(store, monkeypatch):
    save_october(store)
    size = store.path.stat().st_size
    monkeypatch.setattr(search_cache, "MAX_FILE_BYTES", size)
    big = [day(OCT[0] + timedelta(days=n), f"/trang-{k}/") for n in range(28) for k in range(40)]
    with pytest.raises(SearchCacheError) as caught:
        store.save_days(
            SCOPE,
            big,
            start=OCT[0],
            end=OCT[1],
            first_provisional=None,
            fetched_at=NOW,
            today=TODAY,
        )
    assert str(caught.value) == MSG_FULL
    assert len(store.load(SCOPE).days) == 28  # phần cũ còn nguyên


def test_too_large_file_is_dropped(store, monkeypatch):
    save_october(store)
    monkeypatch.setattr(search_cache, "MAX_FILE_BYTES", 1024)
    assert store.load(SCOPE) is None and store.reset_count == 1


# ===================================================================== phạm vi (LC-T120-9)


def test_other_scope_drops_the_cache_on_load(store):
    save_october(store)
    other = CacheScope("https://suachuacuasat.com/", SITE)  # đổi thuộc tính
    assert store.load(other) is None
    assert store.reset_count == 1 and not store.path.exists()
    assert store.load(SCOPE) is None  # dữ liệu cũ đã bỏ hẳn


def test_other_scope_wipes_old_data_on_save(store):
    save_october(store)
    store.save_post_dates(SCOPE, {12: TODAY})
    store.save_queries(
        SCOPE, [query("a")], start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False
    )
    other = CacheScope(SCOPE.site_url, "https://example.com")  # đổi WORDPRESS_URL
    store.save_post_dates(other, {99: TODAY})
    cache = store.load(other)
    assert cache.days == () and cache.ranges == () and dict(cache.post_dates) == {99: TODAY}
    assert cache.covered_start is None and cache.final_end is None


def test_trailing_slash_of_wordpress_url_is_same_scope(store):
    save_october(store)
    assert store.load(CacheScope(SCOPE.site_url, SITE + "/")) is not None


def test_file_keeps_no_property_or_secret(store):
    save_october(store)
    data = store.path.read_bytes()
    assert b"sc-domain" not in data and SCOPE.digest.encode() in data


# ============================================================ đọc file bị sửa (LC-T120-9)

TAMPERS = {
    "click-chu": "UPDATE page_day SET clicks = 'abc'",
    "click-le": "UPDATE page_day SET clicks = 1.5",
    "click-am": "UPDATE page_day SET clicks = -1",
    "click-lon": "UPDATE page_day SET clicks = 11",
    "hien-thi-0": "UPDATE page_day SET impressions = 0, clicks = 0",
    "hien-thi-qua-tran": "UPDATE page_day SET impressions = 1000000001, position_sum = 2e9",
    "vi-tri-0": "UPDATE page_day SET position_sum = 0",
    "vi-tri-vo-cung": "UPDATE page_day SET position_sum = 1e999",
    "vi-tri-chu": "UPDATE page_day SET position_sum = 'x'",
    "final-2": "UPDATE page_day SET final = 2",
    "final-chu": "UPDATE page_day SET final = 'co'",  # '1' thì SQLite tự đổi thành số 1
    "final-sai-tam": "UPDATE page_day SET final = 0",
    "trang-staging": "UPDATE page_day SET page = 'https://www.staging-m.suachuacuasat.com/a/'",
    "trang-co-thang": "UPDATE page_day SET page = 'https://suachuacuasat.com/a/#x'",
    "trang-so": "UPDATE page_day SET page = 5",
    "ngay-sai": "UPDATE page_day SET day = '2026-13-01' WHERE day = '2026-10-04'",
    "ngay-chu-so-la": "UPDATE page_day SET day = '２０２６-10-04' WHERE day = '2026-10-04'",
    "ngay-nam-9999": "UPDATE page_day SET day = '9999-12-31' WHERE day = '2026-10-04'",
    "ngay-ngoai-phan-da-lay": "UPDATE page_day SET day = '2026-09-01' WHERE day = '2026-10-04'",
    "info-thua-khoa": "INSERT INTO info (key, value) VALUES ('la', 'x')",
    "info-thieu-khoa": "DELETE FROM info WHERE key = 'covered_end'",
    "phien-ban": "UPDATE info SET value = '2' WHERE key = 'schema_version'",
    "phan-da-lay-nguoc": "UPDATE info SET value = '2026-12-01' WHERE key = 'covered_start'",
    "phan-da-lay-qua-dai": "UPDATE info SET value = '2024-01-01' WHERE key = 'covered_start'",
    "tam-ngoai-phan-da-lay": "UPDATE info SET value = '2027-01-01' WHERE key = 'first_provisional'",
    "phan-da-lay-nam-1": "UPDATE info SET value = '0001-01-01' WHERE key = 'covered_start'",
    "tam-nam-1": "UPDATE info SET value = '0001-01-01' WHERE key = 'first_provisional'",
    "gio-khong-mui-gio": "UPDATE info SET value = '2026-11-03T15:00:00' WHERE key = 'fetched_at'",
    "gio-nam-9999": "UPDATE info SET value = '9999-12-31T23:59:59-12:00' WHERE key = 'fetched_at'",
    "gio-nam-1": "UPDATE info SET value = '0001-01-01T00:00:00+14:00' WHERE key = 'fetched_at'",
    "gio-rong-khi-co-ngay": "UPDATE info SET value = '' WHERE key = 'fetched_at'",
    "ngay-dang-ma-0": "INSERT INTO post_date (post_id, published) VALUES (0, '2026-10-01')",
    "ngay-dang-sai": "INSERT INTO post_date (post_id, published) VALUES (7, '2026-02-30')",
    "khoang-dem-sai": "UPDATE query_range SET row_count = 5",
    "khoang-truncated-2": "UPDATE query_range SET truncated = 2",
    "khoang-nguoc": "UPDATE query_range SET start_day = '2026-12-01'",
    "khoang-qua-dai": "UPDATE query_range SET start_day = '2026-01-01'",
    "tu-khoa-mo-coi": "UPDATE page_query SET range_id = 999",
    "tu-khoa-chua-sach": "UPDATE page_query SET query = 'a  b'",
    "tu-khoa-dai": "UPDATE page_query SET query = printf('%.201c', 'x')",
    "tu-khoa-click-lon": "UPDATE page_query SET clicks = 11",
}


@pytest.mark.parametrize("sql", list(TAMPERS.values()), ids=list(TAMPERS))
def test_one_bad_value_drops_the_whole_cache(store, sql):
    save_october(store)
    save_tail(store, [day(date(2026, 11, 1))], start=date(2026, 11, 1), first=date(2026, 11, 2))
    store.save_queries(
        SCOPE, [query("cửa")], start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False
    )
    store.save_post_dates(SCOPE, {12: date(2026, 9, 1)})
    assert store.load(SCOPE) is not None
    run_sql(store, sql)
    assert store.load(SCOPE) is None
    assert store.reset_count == 1 and not store.path.exists()


def test_fetched_at_year_is_checked_before_converting():
    """Đối chứng LC-T120-10: đổi thẳng năm 1 (+14:00) sang giờ Việt Nam thì tràn ``datetime``."""
    with pytest.raises(OverflowError):
        datetime.fromisoformat("0001-01-01T00:00:00+14:00").astimezone(VN)


SCHEMA_TAMPERS = {
    "bang-la": "CREATE TABLE la (x)",
    "khung-nhin": "CREATE VIEW v AS SELECT * FROM page_day",
    "trigger": "CREATE TRIGGER t AFTER INSERT ON post_date BEGIN DELETE FROM info; END",
    "chi-muc": "CREATE INDEX i ON page_query (range_id)",
    "mat-bang": "DROP TABLE post_date",
}


@pytest.mark.parametrize("sql", list(SCHEMA_TAMPERS.values()), ids=list(SCHEMA_TAMPERS))
def test_schema_changes_drop_the_cache(store, sql):
    save_october(store)
    run_sql(store, sql)
    assert store.load(SCOPE) is None and store.reset_count == 1
    save_october(store)  # ghi lại được trên file mới
    assert len(store.load(SCOPE).days) == 28


def test_not_a_database_is_dropped_then_write_works(store):
    store.path.parent.mkdir(parents=True)
    store.path.write_bytes(b"day la chu, khong phai SQLite" * 100)
    save_october(store)  # file lạ bị bỏ rồi ghi trên file mới
    assert store.reset_count == 1 and len(store.load(SCOPE).days) == 28


def test_corrupt_info_on_save_retries_on_a_fresh_file(store):
    save_october(store)
    run_sql(store, "UPDATE info SET value = '2' WHERE key = 'schema_version'")
    store.save_post_dates(SCOPE, {12: TODAY})
    cache = store.load(SCOPE)
    assert store.reset_count == 1 and dict(cache.post_dates) == {12: TODAY} and cache.days == ()


# ===================================================================== liên kết (T-117)


def test_data_dir_link_is_never_opened(project, store, tmp_path):
    outside = tmp_path / "ngoai-du-an"
    outside.mkdir()
    link_dir(project / "data", outside)
    for action in (
        lambda: store.load(SCOPE),
        lambda: save_october(store),
        lambda: store.save_post_dates(SCOPE, {12: TODAY}),
        store.clear,
    ):
        with pytest.raises(SearchCacheError) as caught:
            action()
        assert str(caught.value) == MSG_DATA_DIR_LINK
    assert list(outside.iterdir()) == []  # không tạo, không ghi gì qua liên kết


@pytest.mark.parametrize("suffix", ["", "-journal", "-wal"], ids=["file", "journal", "wal"])
def test_hard_link_at_cache_path_is_removed_not_followed(store, tmp_path, suffix):
    outside = tmp_path / "ngoai.bin"
    outside.write_bytes(b"du lieu ngoai du an")
    store.path.parent.mkdir(parents=True)
    target = store.path.with_name(store.path.name + suffix)
    os.link(outside, target)
    save_october(store)
    assert outside.read_bytes() == b"du lieu ngoai du an"
    assert outside.stat().st_nlink == 1  # tên trong data/ đã gỡ
    assert len(store.load(SCOPE).days) == 28


def test_symlink_at_cache_path_is_removed_not_followed(store, tmp_path):
    outside = tmp_path / "ngoai.sqlite"
    outside.write_bytes(b"")
    store.path.parent.mkdir(parents=True)
    try:
        os.symlink(outside, store.path)
    except OSError:
        pytest.skip("máy này không cho tạo symlink file (Windows cần quyền Developer Mode)")
    save_october(store)
    assert outside.read_bytes() == b"" and not store.path.is_symlink()


# ===================================================================== bận, xóa, SQL


def test_busy_file_gives_fixed_message_and_reads_still_work(store):
    save_october(store)
    with closing(sqlite3.connect(store.path, isolation_level=None)) as other:
        other.execute("BEGIN IMMEDIATE")  # tab khác đang ghi
        with pytest.raises(SearchCacheError) as caught:
            store.save_post_dates(SCOPE, {12: TODAY})
        assert str(caught.value) == MSG_BUSY
        assert len(store.load(SCOPE).days) == 28  # đọc vẫn được
        other.execute("ROLLBACK")


def test_clear_removes_file(store):
    save_october(store)
    store.clear()
    assert not store.path.exists() and store.load(SCOPE) is None


def test_sql_only_uses_constant_text_and_parameters():
    """Mọi câu ``execute``/``executemany`` là chữ cố định hay biến trỏ tới hằng của module; không
    f-string, không ``%``, không ``.format`` (SQL chỉ dùng tham số ``?``)."""
    tree = ast.parse(Path(search_cache.__file__).read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("execute", "executemany")
    ]
    assert len(calls) >= 20
    for call in calls:
        first = call.args[0]
        if isinstance(first, ast.IfExp):  # "BEGIN IMMEDIATE" if write else "BEGIN"
            branches = (first.body, first.orelse)
            assert all(isinstance(part, ast.Constant) for part in branches), ast.unparse(first)
            continue
        assert isinstance(first, ast.Constant | ast.Name), ast.unparse(first)
        if isinstance(first, ast.Name):  # vòng lặp qua ``_CREATE_TABLES``, ``_WIPE``
            assert first.id in ("sql", "_MASTER_SQL"), first.id

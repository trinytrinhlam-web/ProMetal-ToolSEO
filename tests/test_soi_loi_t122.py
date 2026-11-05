"""T-122 Soi Lỗi (đầy đủ): cache số liệu Search Console (``seo_app.storage.search_cache``).

Bổ sung cho ``tests/test_search_cache.py`` (Thợ Máy), theo trọng tâm Chỉ Huy B giao:

- Một dòng sai ở **bất kỳ chỗ nào** (dòng cuối, dòng giữa, một khoảng từ khóa, một ngày đăng) là
  bỏ cả cache; giá trị đúng mà SQLite tự đổi kiểu thì vẫn đọc ra đúng kiểu của hai ``Protocol``
  T-123 (``day`` là ``date``, ``final`` là ``bool`` thật).
- Năm ngoài 2000–2200 ở mọi bảng; mốc giờ ở biên năm (SL-T122-2).
- ``data/`` là liên kết treo; chính file, ``-shm`` là liên kết; hard link tới một cache hợp lệ.
- File ở chế độ WAL do chương trình khác đặt, nhật ký nóng sau khi chương trình ghi tắt ngang,
  khóa độc quyền, hai luồng cùng ghi và một luồng đọc.
- Biên giữ 16 tháng, khoảng từ khóa thứ 7.
- ``WORDPRESS_URL`` viết hoa ở tên máy, có cổng 443 (SL-T122-1); surrogate lẻ (SL-T122-3).
- Ghép thật với gói tính toán T-123 (chạy khi nhánh đã có ``seo_app.tracking``).

Lỗi mới để ``xfail(strict=True)`` kèm mã SL-T122-n. Tham số lớn luôn có ``ids=`` ngắn. Mọi file
nằm trong ``tmp_path``; không gọi mạng.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import threading
import time
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from test_search_cache import (
    NOW,
    OCT,
    SCOPE,
    SITE,
    TODAY,
    day,
    days_between,
    link_dir,
    query,
    save_october,
    save_tail,
)

from seo_app.images.data_dir import MSG_DATA_DIR_LINK, is_link
from seo_app.storage import search_cache
from seo_app.storage.search_cache import (
    KEEP_DAYS,
    MAX_QUERY_RANGES,
    MSG_BAD_DATA,
    MSG_BAD_SCOPE,
    MSG_BUSY,
    CachedDay,
    CachedQuery,
    CacheScope,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.wordpress.client import PublishedItem

SURROGATE = chr(0xD800)  # surrogate lẻ: json.loads của Google trả được ("\ud800")
TAIL = (date(2026, 11, 1), TODAY)  # đoạn mới nhất, số tạm từ 02/11
SPAN_2 = (date(2026, 10, 5), date(2026, 11, 1))  # khoảng từ khóa thứ hai


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả; ``PROJECT_ROOT`` của module trỏ vào đó (như test Thợ Máy)."""
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def store(project: Path) -> SearchCacheStore:
    return SearchCacheStore(path=project / "data" / "search_cache.sqlite")


def fill(store: SearchCacheStore) -> None:
    """Cache đủ bốn loại số liệu: tháng 10 đã chốt (trang /a/), đoạn 01–03/11 (02/11 trở đi là số
    tạm), hai khoảng từ khóa, ba ngày đăng."""
    save_october(store)
    save_tail(
        store,
        [day(TAIL[0]), day(TODAY, "/b/", final=False)],
        start=TAIL[0],
        first=TAIL[0] + timedelta(days=1),
    )
    store.save_queries(
        SCOPE,
        [query("cửa sắt"), query("cửa cuốn", "/b/")],
        start=OCT[0],
        end=OCT[1],
        fetched_at=NOW,
        truncated=False,
    )
    store.save_queries(
        SCOPE,
        [query("cổng", span=SPAN_2), query("cửa kéo", "/c/", span=SPAN_2)],
        start=SPAN_2[0],
        end=SPAN_2[1],
        fetched_at=NOW,
        truncated=True,
    )
    store.save_post_dates(
        SCOPE, {12: date(2026, 9, 1), 13: date(2026, 10, 2), 14: date(2026, 10, 30)}
    )


def run_one(store: SearchCacheStore, sql: str, params: tuple = ()) -> None:
    """Sửa tay đúng **một** dòng của file cache (giả lập file bị sửa ngoài app)."""
    with closing(sqlite3.connect(store.path)) as conn, conn:
        assert conn.execute(sql, params).rowcount == 1, sql


def protocol_ok(row: CachedDay) -> bool:
    """Điều kiện ``match._day_row_ok`` của T-123 (chép lại để chạy được trên nhánh này): dòng sai
    kiểu bị T-123 bỏ lặng lẽ, mọi bài thành «chưa có lượt hiển thị»."""
    return (
        type(row.day) is date
        and 2000 <= row.day.year <= 2200
        and type(row.page) is str
        and type(row.final) is bool
        and type(row.clicks) is int
        and type(row.impressions) is int
        and type(row.position_sum) is float
        and 0 <= row.clicks <= row.impressions <= 10**9
        and row.impressions >= 1
        and row.impressions <= row.position_sum <= row.impressions * 10_000
    )


# ============================================== kiểu đọc ra khớp Protocol T-123 (trọng tâm 6)

# Cùng giá trị, ghi bằng kiểu khác: SQLite đổi theo kiểu cột (INTEGER, REAL) nên đọc ra vẫn đúng.
SAME_VALUE_OTHER_TYPE = {
    "final-chu-1": "UPDATE page_day SET final = '1' WHERE final = 1",
    "final-so-thuc": "UPDATE page_day SET final = 1.0 WHERE final = 1",
    "final-true": "UPDATE page_day SET final = TRUE WHERE final = 1",
    "final-chu-0": "UPDATE page_day SET final = '0' WHERE final = 0",
    "click-so-thuc": "UPDATE page_day SET clicks = 1.0",
    "click-chu": "UPDATE page_day SET clicks = '1'",
    "hien-thi-chu": "UPDATE page_day SET impressions = ' 10'",
    "vi-tri-so-nguyen": "UPDATE page_day SET position_sum = 20",
    "vi-tri-chu-mu": "UPDATE page_day SET position_sum = '2e1'",
    "tu-khoa-click-so-thuc": "UPDATE page_query SET clicks = 1.0",
    "tu-khoa-vi-tri-so-nguyen": "UPDATE page_query SET position_sum = 30",
    "ma-khoang-chu": "UPDATE page_query SET range_id = CAST(range_id AS TEXT)",
    "ma-bai-chu": "UPDATE post_date SET post_id = '12' WHERE post_id = 12",
    "truncated-chu": "UPDATE query_range SET truncated = '1' WHERE truncated = 1",
}


@pytest.mark.parametrize(
    "sql", list(SAME_VALUE_OTHER_TYPE.values()), ids=list(SAME_VALUE_OTHER_TYPE)
)
def test_same_value_other_storage_type_reads_back_with_protocol_types(store, sql):
    fill(store)
    before = store.load(SCOPE)
    with closing(sqlite3.connect(store.path)) as conn, conn:
        assert conn.execute(sql).rowcount >= 1
    cache = store.load(SCOPE)
    assert cache == before and store.reset_count == 0
    assert len(cache.days) == 30 and all(protocol_ok(row) for row in cache.days)
    assert [row.final for row in cache.days if row.day > OCT[1]] == [True, False]
    for row in cache.queries:
        assert type(row.start) is date and type(row.end) is date and type(row.query) is str
        assert type(row.clicks) is int and type(row.impressions) is int
        assert type(row.position_sum) is float
    assert all(
        type(item.truncated) is bool and type(item.row_count) is int for item in cache.ranges
    )
    assert all(type(key) is int and type(value) is date for key, value in cache.post_dates.items())
    assert type(cache.fetched_at) is datetime and cache.fetched_at.utcoffset() is not None


# ======================================= một dòng sai ở bất kỳ đâu là bỏ cả cache (trọng tâm 1)

ONE_BAD_ROW = {
    "ngay-dong-cuoi": "UPDATE page_day SET clicks = 11 WHERE day = '2026-11-03'",
    "ngay-dong-giua": "UPDATE page_day SET position_sum = 9.5 WHERE day = '2026-10-17'",
    "final-sai-1-dong": "UPDATE page_day SET final = 1 WHERE day = '2026-11-03'",
    "trang-hoa-1-dong": (
        "UPDATE page_day SET page = 'https://SUACHUACUASAT.com/a/' WHERE day = '2026-10-20'"
    ),
    "tu-khoa-dong-cuoi": (
        "UPDATE page_query SET impressions = 0 WHERE rowid = (SELECT MAX(rowid) FROM page_query)"
    ),
    "tu-khoa-khoang-2": "UPDATE page_query SET query = ' cổng' WHERE query = 'cổng'",
    "khoang-2-truncated": (
        "UPDATE query_range SET truncated = 2 WHERE id = (SELECT MAX(id) FROM query_range)"
    ),
    "ngay-dang-cuoi": "UPDATE post_date SET published = '2026-10-32' WHERE post_id = 14",
    # Năm ngoài 2000–2200 nhưng là ngày hợp lệ của Python: chỉ phép kiểm năm bắt được.
    "ngay-dang-1999": "UPDATE post_date SET published = '1999-12-31' WHERE post_id = 14",
    "ngay-dang-2201": "UPDATE post_date SET published = '2201-01-01' WHERE post_id = 13",
    "khoang-nam-2201": (
        "UPDATE query_range SET start_day = '2201-01-01', end_day = '2201-01-28' "
        "WHERE id = (SELECT MIN(id) FROM query_range)"
    ),
    "gio-nam-2500": "UPDATE info SET value = '2500-01-01T00:00:00+07:00' WHERE key = 'fetched_at'",
    "gio-khoang-1999": (
        "UPDATE query_range SET fetched_at = '1999-12-31T23:00:00+07:00' "
        "WHERE id = (SELECT MAX(id) FROM query_range)"
    ),
    # Byte lạ: UTF-8 hỏng, BLOB, NUL.
    "trang-utf8-hong": (
        "UPDATE page_day SET page = CAST(X'68747470733A2F2FFF' AS TEXT) WHERE day = '2026-10-31'"
    ),
    "tu-khoa-utf8-hong": "UPDATE page_query SET query = CAST(X'C3' AS TEXT) WHERE query = 'cổng'",
    "info-utf8-hong": "UPDATE info SET value = CAST(X'FF' AS TEXT) WHERE key = 'fetched_at'",
    "ngay-blob": "UPDATE page_day SET day = CAST(day AS BLOB) WHERE day = '2026-10-31'",
    "trang-blob": "UPDATE page_day SET page = CAST(page AS BLOB) WHERE day = '2026-10-31'",
    "final-blob": "UPDATE page_day SET final = X'01' WHERE day = '2026-10-31'",
    "click-blob": "UPDATE page_day SET clicks = X'01' WHERE day = '2026-10-31'",
    "trang-nul": "UPDATE page_day SET page = page || char(0) WHERE day = '2026-10-31'",
    "tu-khoa-nul": "UPDATE page_query SET query = query || char(0) WHERE query = 'cổng'",
    "ngay-dang-blob": "UPDATE post_date SET published = CAST(published AS BLOB) WHERE post_id = 12",
    "khoa-info-blob": "UPDATE info SET key = CAST(key AS BLOB) WHERE key = 'fetched_at'",
}


@pytest.mark.parametrize("sql", list(ONE_BAD_ROW.values()), ids=list(ONE_BAD_ROW))
def test_one_bad_row_anywhere_drops_the_whole_cache(store, sql):
    fill(store)
    assert store.load(SCOPE) is not None
    run_one(store, sql)
    assert store.load(SCOPE) is None
    assert store.reset_count == 1 and not store.path.exists()
    save_october(store)  # lần lấy sau ghi lại được trên file mới
    assert len(store.load(SCOPE).days) == 28


# ============================================================ liên kết (trọng tâm 3, T-117)


@pytest.mark.parametrize(
    "suffix", ["", "-journal", "-wal", "-shm"], ids=["file", "journal", "wal", "shm"]
)
def test_directory_link_at_cache_or_journal_path_is_removed(store, tmp_path, suffix):
    """Junction (Windows) hay symlink thư mục (Mac/Linux) đặt đúng tên file hay file nhật ký: chỉ
    gỡ liên kết, không tạo gì ở chỗ nó trỏ tới; sau khi ghi, file cache là file thường."""
    outside = tmp_path / "ngoai"
    outside.mkdir()
    store.path.parent.mkdir(parents=True)
    link = store.path.with_name(store.path.name + suffix)
    link_dir(link, outside)
    save_october(store)
    assert list(outside.iterdir()) == []
    assert not is_link(store.path) and store.path.is_file()
    assert suffix == "" or not os.path.lexists(link)
    assert len(store.load(SCOPE).days) == 28


def test_hard_link_at_shm_is_removed_not_followed(store, tmp_path):
    outside = tmp_path / "ngoai.bin"
    outside.write_bytes(b"du lieu ngoai du an")
    store.path.parent.mkdir(parents=True)
    os.link(outside, store.path.with_name(store.path.name + "-shm"))
    save_october(store)
    assert outside.read_bytes() == b"du lieu ngoai du an" and outside.stat().st_nlink == 1


def test_hard_link_to_a_valid_cache_elsewhere_is_never_read(store, tmp_path):
    """Hard link tới một cache hợp lệ nằm ngoài ``data/`` (số liệu do người khác dựng): ``load`` gỡ
    tên trong ``data/``, không đọc số liệu qua liên kết, không đụng file kia."""
    other = SearchCacheStore(path=tmp_path / "khac" / "search_cache.sqlite")
    save_october(other)
    store.path.parent.mkdir(parents=True)
    os.link(other.path, store.path)
    assert store.load(SCOPE) is None
    assert other.path.stat().st_nlink == 1 and len(other.load(SCOPE).days) == 28


def test_dangling_data_link_is_refused_and_not_recreated(project, store, tmp_path):
    target = tmp_path / "dich-da-xoa"
    target.mkdir()
    link_dir(project / "data", target)
    target.rmdir()  # liên kết treo
    for action in (
        lambda: store.load(SCOPE),
        store.clear,
        lambda: store.save_post_dates(SCOPE, {12: TODAY}),
    ):
        with pytest.raises(SearchCacheError) as caught:
            action()
        assert str(caught.value) == MSG_DATA_DIR_LINK
    assert not target.exists()


# =============================================== file do chương trình khác đụng tới (trọng tâm 8)


def test_wal_mode_set_by_another_program_keeps_working(store):
    fill(store)
    before = store.load(SCOPE)
    with closing(sqlite3.connect(store.path)) as conn:
        assert conn.execute("PRAGMA journal_mode = WAL").fetchone() == ("wal",)
    assert store.load(SCOPE) == before and store.reset_count == 0
    with closing(sqlite3.connect(store.path, isolation_level=None)) as reader:
        reader.execute("BEGIN")
        reader.execute("SELECT COUNT(*) FROM page_day").fetchone()  # chương trình khác đang đọc
        store.save_post_dates(SCOPE, {15: TODAY})
        reader.execute("ROLLBACK")
    assert store.load(SCOPE).post_dates[15] == TODAY and store.reset_count == 0
    store.clear()
    assert list(store.path.parent.iterdir()) == []  # cả -wal, -shm


CRASH = r"""
import os, sqlite3, sys
conn = sqlite3.connect(sys.argv[1], isolation_level=None)
conn.execute("PRAGMA cache_size = 2")  # bộ nhớ đệm nhỏ: SQLite phải ghi dở vào file
conn.execute("BEGIN IMMEDIATE")
for n in range(4000):
    conn.execute(
        "INSERT INTO page_day VALUES (?, ?, 5, 9, 1.0, 7)",
        ("2026-10-%02d" % (1 + n % 28), "rac-%d-" % n + "x" * 300),
    )
conn.execute("UPDATE info SET value = 'hong' WHERE key = 'scope_hash'")
os._exit(3)  # tắt ngang: không COMMIT, không ROLLBACK, còn nhật ký nóng
"""


def test_hot_journal_after_a_crash_is_rolled_back_not_dropped(store):
    """Chương trình đang ghi thì tắt ngang (mất điện, tắt cửa sổ): lần mở sau SQLite tự hoàn tác
    theo ``-journal``; cache trở lại đúng như trước, không bị coi là hỏng mà bỏ."""
    fill(store)
    before = store.load(SCOPE)
    size = store.path.stat().st_size
    done = subprocess.run(
        [sys.executable, "-c", CRASH, str(store.path)], capture_output=True, timeout=120
    )
    assert done.returncode == 3, done.stderr[-300:]
    journal = store.path.with_name(store.path.name + "-journal")
    assert journal.stat().st_size > 0 and store.path.stat().st_size > size  # đã ghi dở
    assert store.load(SCOPE) == before and store.reset_count == 0
    assert not journal.exists()


def test_exclusive_lock_is_busy_not_corrupt(store):
    """File bị chương trình khác khóa độc quyền: báo «đang bận», không bỏ cache."""
    save_october(store)
    with closing(sqlite3.connect(store.path, isolation_level=None)) as other:
        other.execute("BEGIN EXCLUSIVE")
        for action in (
            lambda: store.load(SCOPE),
            lambda: store.save_post_dates(SCOPE, {12: TODAY}),
        ):
            with pytest.raises(SearchCacheError) as caught:
                action()
            assert str(caught.value) == MSG_BUSY
        other.execute("ROLLBACK")
    assert store.reset_count == 0 and len(store.load(SCOPE).days) == 28


def test_two_writers_and_a_reader_never_drop_the_cache(project):
    """Hai tab cùng ghi (đoạn ngày mới nhất, từ khóa), một tab đọc, trong 3 giây: lỗi duy nhất được
    phép là «đang bận»; không lần nào cache bị coi là hỏng mà bỏ (trọng tâm 7)."""
    path = project / "data" / "search_cache.sqlite"
    seed = SearchCacheStore(path=path)
    save_october(seed)
    save_tail(seed, [], start=TAIL[0], first=TAIL[0] + timedelta(days=1))
    stores = [SearchCacheStore(path=path) for _ in range(3)]
    problems: list[str] = []
    stop = time.monotonic() + 3

    def work(n: int) -> None:
        tab = stores[n]
        k = 0
        while time.monotonic() < stop:
            k += 1
            try:
                if n == 2:
                    cache = tab.load(SCOPE)
                    assert cache is not None and cache.covered_end == TODAY
                    assert cache.first_provisional == TAIL[0] + timedelta(days=1)
                elif k % 2:
                    rows = [day(TAIL[0], f"/p{i}/") for i in range(1 + (k * 7 + n) % 60)]
                    save_tail(tab, rows, start=TAIL[0], first=TAIL[0] + timedelta(days=1))
                else:
                    tab.save_queries(
                        SCOPE,
                        [query(f"từ khóa {n} {i}") for i in range((k * 13) % 90)],
                        start=OCT[0],
                        end=OCT[1],
                        fetched_at=NOW,
                        truncated=False,
                    )
            except SearchCacheError as exc:
                if str(exc) != MSG_BUSY:
                    problems.append(f"{n}: {exc}")
            except Exception as exc:  # mọi lỗi khác (kể cả assert ở trên) là lỗi của ca này
                problems.append(f"{n}: {exc!r}")

    threads = [threading.Thread(target=work, args=(n,)) for n in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert problems == []
    assert [tab.reset_count for tab in stores] == [0, 0, 0]
    final = seed.load(SCOPE)
    assert final is not None and (final.covered_start, final.covered_end) == (OCT[0], TODAY)


# ====================================================== giữ 16 tháng, ≤ 6 khoảng (trọng tâm 4)


def test_first_chunk_may_start_exactly_16_months_back_not_a_day_more(store):
    cutoff = TODAY - timedelta(days=KEEP_DAYS - 1)
    end = cutoff + timedelta(days=5)
    save_tail(store, days_between(cutoff, end), start=cutoff, end=end)
    assert store.load(SCOPE).covered_start == cutoff
    store.clear()
    early = cutoff - timedelta(days=1)
    with pytest.raises(SearchCacheError) as caught:
        save_tail(store, [], start=early, end=early + timedelta(days=5))
    assert str(caught.value) == MSG_BAD_DATA


@pytest.mark.parametrize(
    ("days", "kept"), [(KEEP_DAYS - 1, True), (KEEP_DAYS, False)], ids=["486-ngay", "487-ngay"]
)
def test_coverage_longer_than_16_months_in_file_drops_cache(store, days, kept):
    save_october(store)
    start = OCT[1] - timedelta(days=days)
    run_one(store, "UPDATE info SET value = ? WHERE key = 'covered_start'", (start.isoformat(),))
    assert (store.load(SCOPE) is not None) is kept


def test_seventh_query_range_written_by_hand_drops_cache(store):
    for n in range(MAX_QUERY_RANGES):
        span = (date(2026, 10, 1) + timedelta(days=n), date(2026, 10, 28) + timedelta(days=n))
        store.save_queries(
            SCOPE,
            [query("cửa", span=span)],
            start=span[0],
            end=span[1],
            fetched_at=NOW,
            truncated=False,
        )
    assert len(store.load(SCOPE).ranges) == MAX_QUERY_RANGES
    run_one(
        store,
        "INSERT INTO query_range (start_day, end_day, fetched_at, row_count, truncated) "
        "VALUES ('2026-09-01', '2026-09-28', '2026-11-03T15:00:00+07:00', 0, 0)",
    )
    assert store.load(SCOPE) is None and store.reset_count == 1


# ================================================ SL-T122-1: WORDPRESS_URL chữ hoa, cổng 443


@pytest.mark.parametrize(
    "wordpress_url",
    ["https://Suachuacuasat.com", "https://suachuacuasat.com:443", "HTTPS://suachuacuasat.com/"],
    ids=["ten-may-hoa", "cong-443", "scheme-hoa"],
)
def test_sl_t122_1_google_pages_are_saved_whatever_the_case_of_wordpress_url(store, wordpress_url):
    """Google (và client T-121) trả địa chỉ viết thường, không cổng. ``WORDPRESS_URL`` gõ khác
    (chữ hoa ở tên máy, cổng 443, ``HTTPS://``) vẫn là cùng website: lưu và đọc lại được."""
    scope = CacheScope(SCOPE.site_url, wordpress_url)
    store.save_days(
        scope,
        days_between(*OCT),
        start=OCT[0],
        end=OCT[1],
        first_provisional=None,
        fetched_at=NOW,
        today=TODAY,
    )
    store.save_queries(
        scope, [query("cửa sắt")], start=OCT[0], end=OCT[1], fetched_at=NOW, truncated=False
    )
    cache = store.load(scope)
    assert len(cache.days) == 28 and [row.page for row in cache.queries] == [SITE + "/a/"]


@pytest.mark.parametrize(
    ("wordpress_url", "page"),
    [
        ("https://Suachuacuasat.com", "https://www.suachuacuasat.com/a/"),
        ("https://Suachuacuasat.com", "http://suachuacuasat.com/a/"),
        ("https://suachuacuasat.com/Blog", "https://suachuacuasat.com/blog/a/"),
        ("https://suachuacuasat.com:443", "https://suachuacuasat.com:8443/a/"),
    ],
    ids=["www", "http", "duong-dan-hoa", "cong-khac"],
)
def test_pages_off_the_site_stay_refused_whatever_wordpress_url_looks_like(
    store, wordpress_url, page
):
    """Đối chứng cho bản sửa SL-T122-1: chỉ chuẩn hóa scheme, tên máy, cổng 443 của
    ``WORDPRESS_URL``; ``www.``, ``http://``, cổng khác, đường dẫn khác chữ hoa vẫn bị từ chối
    (LC-T120-6)."""
    scope = CacheScope(SCOPE.site_url, wordpress_url)
    with pytest.raises(SearchCacheError) as caught:
        store.save_days(
            scope,
            [CachedDay(OCT[0], page, 1, 10, 20.0, True)],
            start=OCT[0],
            end=OCT[0],
            first_provisional=None,
            fetched_at=NOW,
            today=TODAY,
        )
    assert str(caught.value) == MSG_BAD_DATA


# ================================================== SL-T122-2: mốc giờ ở biên năm (trọng tâm 5)

EDGE_STAMPS = {
    "2000-mui-cong-14": (
        datetime(2000, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=14))),
        date(2000, 1, 1),
    ),
    "2200-mui-tru-12": (
        datetime(2200, 12, 31, 23, 0, tzinfo=timezone(timedelta(hours=-12))),
        date(2200, 12, 31),
    ),
}


@pytest.mark.parametrize(("moment", "today"), list(EDGE_STAMPS.values()), ids=list(EDGE_STAMPS))
def test_sl_t122_2_fetched_at_that_was_saved_can_be_read_back(store, moment, today):
    """Ghi được thì đọc lại được; không được thì phải từ chối ngay lúc ghi (câu cố định)."""
    try:
        store.save_days(
            SCOPE,
            [day(today)],
            start=today,
            end=today,
            first_provisional=None,
            fetched_at=moment,
            today=today,
        )
        store.save_queries(SCOPE, [], start=today, end=today, fetched_at=moment, truncated=False)
    except SearchCacheError as exc:
        assert str(exc) == MSG_BAD_DATA
        return
    assert store.load(SCOPE) is not None and store.reset_count == 0


# ======================================================= SL-T122-3: surrogate lẻ lọt lỗi Python


@pytest.mark.parametrize("case", ["ngay", "tu-khoa", "doc-pham-vi", "ghi-pham-vi"])
def test_sl_t122_3_lone_surrogate_gives_the_fixed_message(store, case):
    page = SITE + "/a" + SURROGATE + "/"
    bad_scope = CacheScope(SCOPE.site_url, SITE + "/x" + SURROGATE)
    save_october(store)
    before = store.load(SCOPE)
    with pytest.raises(SearchCacheError) as caught:
        if case == "ngay":
            store.save_days(
                SCOPE,
                [CachedDay(OCT[0], page, 1, 10, 20.0, True)],
                start=OCT[0],
                end=OCT[0],
                first_provisional=None,
                fetched_at=NOW,
                today=TODAY,
            )
        elif case == "tu-khoa":
            store.save_queries(
                SCOPE,
                [CachedQuery(*OCT, page, "cửa", 1, 10, 30.0)],
                start=OCT[0],
                end=OCT[1],
                fetched_at=NOW,
                truncated=False,
            )
        elif case == "doc-pham-vi":
            store.load(bad_scope)
        else:
            store.save_post_dates(bad_scope, {12: TODAY})
    assert str(caught.value) in (MSG_BAD_DATA, MSG_BAD_SCOPE)
    assert store.load(SCOPE) == before


def test_lone_surrogate_in_query_text_is_refused(store):
    """Đối chứng: từ khóa có surrogate lẻ thì ``clean_text`` đổi chữ nên đã bị từ chối đúng câu."""
    with pytest.raises(SearchCacheError) as caught:
        store.save_queries(
            SCOPE,
            [query("c" + SURROGATE)],
            start=OCT[0],
            end=OCT[1],
            fetched_at=NOW,
            truncated=False,
        )
    assert str(caught.value) == MSG_BAD_DATA


# ============================================== ghép thật với gói tính toán T-123 (trọng tâm 6)


def test_cache_rows_go_through_t123_without_being_dropped(store):
    """Sau khi gộp T-123: dòng đọc từ file đi qua ``build_tracking``, ``aggregate``,
    ``page_queries``, ``keyword_table`` mà không dòng nào bị bỏ (T-123 bỏ lặng lẽ dòng sai kiểu).
    Nhánh chưa có ``seo_app.tracking`` thì bỏ qua (đã chạy trên bản gộp tạm T-122 + T-123)."""
    match = pytest.importorskip("seo_app.tracking.match")
    keywords = pytest.importorskip("seo_app.tracking.keywords")
    periods = pytest.importorskip("seo_app.tracking.periods")
    stats = pytest.importorskip("seo_app.tracking.stats")
    slug = "/s%E1%BB%ADa-c%E1%BB%ADa-s%E1%BA%AFt/"  # sửa-cửa-sắt
    paths = [slug, "/cua-cuon/", "/cua-cuon/#bang-gia", "/", "/?s=cua"]
    october = [
        day(OCT[0] + timedelta(days=n), path, n % 3, 10 + k)
        for n in range(28)
        for k, path in enumerate(paths)
    ]
    store.save_days(
        SCOPE,
        october,
        start=OCT[0],
        end=OCT[1],
        first_provisional=None,
        fetched_at=NOW,
        today=TODAY,
    )
    save_tail(
        store, [day(TODAY, slug, final=False)], start=TAIL[0], first=TAIL[0] + timedelta(days=1)
    )
    store.save_queries(
        SCOPE,
        [
            query(text, path)
            for text in ("sửa cửa sắt", "sua cua sat", "cửa cuốn")
            for path in paths[:3]
        ],
        start=OCT[0],
        end=OCT[1],
        fetched_at=NOW,
        truncated=False,
    )
    cache = store.load(SCOPE)
    items = [
        PublishedItem(
            id=11, type="post", slug=slug.strip("/"), link=SITE + slug, title="Sửa cửa sắt"
        ),
        PublishedItem(
            id=12, type="post", slug="cua-cuon", link=SITE + "/cua-cuon/", title="Cửa cuốn"
        ),
    ]
    tracking = match.build_tracking(SITE, items, cache.days)
    assert tracking.skipped_rows == 0 and tracking.skipped_items == 0
    period = periods.Period(*OCT)
    seen = [stats.aggregate(page.days, period) for page in (*tracking.pages, *tracking.others)]
    assert sum(part.clicks for part in seen) == sum(row.clicks for row in october)
    assert sum(part.impressions for part in seen) == sum(row.impressions for row in october)
    cuon = next(page for page in tracking.pages if page.item.id == 12)
    rows = keywords.page_queries(cache.queries, site=SITE, key=cuon.key, period=period)
    assert len(rows) == 3 and keywords.keyword_table(rows).skipped == 0


# ============================ lượt 2: chuẩn hóa WORDPRESS_URL không nới lớp chặn (SL-T122-1 đã sửa)

SPELLINGS = [
    "https://suachuacuasat.com",
    "https://Suachuacuasat.com",
    "HTTPS://SUACHUACUASAT.COM/",
    "https://suachuacuasat.com:443",
    "https://SuaChuaCuaSat.com:443/",
    "Https://suachuacuasat.com//",
]
OFF_SITE = [
    "https://www.staging-m.suachuacuasat.com/a/",  # staging
    "https://staging.suachuacuasat.com/a/",
    "https://www.suachuacuasat.com/a/",  # www.
    "http://suachuacuasat.com/a/",
    "HTTP://suachuacuasat.com/a/",
    "https://suachuacuasat.com:8443/a/",  # cổng khác
    "https://suachuacuasat.com:80/a/",
    "https://suachuacuasat.com:443/a/",  # Google không viết cổng; client T-121 cũng bỏ
    "https://user@suachuacuasat.com/a/",  # tên người dùng
    "https://user:"
    + "pw@suachuacuasat.com/a/",  # tách chuỗi: mật khẩu giả, detect-secrets khỏi báo
    "https://suachuacuasat.com@evil.example/a/",
    "https://evilsuachuacuasat.com/a/",  # tên miền giống
    "https://suachuacuasat.com.evil.example/a/",
    "https://suachuacuasat.com-evil.com/a/",
    "https://suachuacuas" + chr(0x0430) + "t.com/a/",  # chữ «а» Kirin
    "https://SUACHUACUASAT.com/a/",  # Google luôn viết thường; client T-121 cũng bỏ
]


def saves(store: SearchCacheStore, wordpress_url: str, page: str) -> bool:
    """Cache nhận địa chỉ ``page`` khi ``WORDPRESS_URL`` viết là ``wordpress_url`` không."""
    try:
        store.save_days(
            CacheScope(SCOPE.site_url, wordpress_url),
            [CachedDay(OCT[0], page, 1, 10, 20.0, True)],
            start=OCT[0],
            end=OCT[0],
            first_provisional=None,
            fetched_at=NOW,
            today=TODAY,
        )
    except SearchCacheError as exc:
        assert str(exc) == MSG_BAD_DATA
        return False
    return True


def test_lan_2_off_site_pages_stay_refused_for_every_spelling(store):
    """Lượt 2: với mọi cách viết ``WORDPRESS_URL`` của website thật, cache vẫn loại staging,
    ``www.``, ``http://``, cổng khác, tên người dùng, tên miền giống; trang thật thì lưu được."""
    taken = [(wp, page) for wp in SPELLINGS for page in OFF_SITE if saves(store, wp, page)]
    assert taken == []
    assert [wp for wp in SPELLINGS if not saves(store, wp, SITE + "/a/")] == []


def test_lan_2_site_rules_match_t121_and_t123(store):
    """Lượt 2: ba bản chuẩn hóa ``WORDPRESS_URL`` (``site_prefix`` của client T-121,
    ``site_base`` của gói T-123, của cache) cho cùng tiền tố; địa chỉ T-123 nhận thì cache nhận và
    ngược lại. Chạy khi nhánh đã có cả ``seo_app.google.search_console`` và ``seo_app.tracking``
    (đã chạy trên bản gộp tạm T-121 + T-122 + T-123); thiếu gói nào thì bỏ qua. Gom ba bản về một
    hàm (T-124) thì ca vẫn đúng."""
    console = pytest.importorskip("seo_app.google.search_console")
    match = pytest.importorskip("seo_app.tracking.match")
    pages = [*OFF_SITE, SITE + "/a/", SITE + "/", SITE + "/blog/a/", SITE + "/Blog/a/"]
    pages += [SITE + "/a/#x", SITE + "/?s=x"]
    for wp in [*SPELLINGS, "https://suachuacuasat.com/blog", "https://Suachuacuasat.com/Blog/"]:
        base = CacheScope(SCOPE.site_url, wp).base
        assert base == match.site_base(wp) and base + "/" == console.site_prefix(wp), wp
        for page in pages:
            assert saves(store, wp, page) == (match.page_key(page, wp) is not None), (wp, page)

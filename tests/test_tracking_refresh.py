"""T-124 (Thợ Máy): lấy số liệu Search Console, kiểm kết nối, lưu thuộc tính
(``seo_app/tracking/refresh.py``; thiết kế T-120 mục 1.2, 1.3, 2.4–2.6, 3.3).

- Khoảng cần lấy, chia đoạn ≤ 31 ngày (cũ tới mới, đoạn mới nhất là 31 ngày cuối), đánh dấu số
  tạm, từ khóa hai kỳ, ngày đăng qua ``post_statuses``, dừng ở lỗi đầu tiên và giữ phần đã lưu.
- LC-T120-8: hết trần lệnh của client thì dừng, giữ phần đã ghi, lần bấm sau lấy tiếp.
- LC-T120-12, -23: chỉ lưu thuộc tính vừa tìm thấy và dùng được; báo biến môi trường đè ``.env``.
- LC-T120-13, -21: module không nhập Streamlit, AI, Google Sheets; nạp module không gọi mạng.
- LC-T120-22: khóa cấp module (một lần lấy mỗi tiến trình); một client mỗi lần bấm.
- GN-2 Soi Lỗi T-122: mốc lấy ở tương lai coi như cũ; đồng hồ chỉnh lùi thì bỏ cache (Lá Chắn
  T-122 mục 8).
- Thử chung: ``CachedDay``, ``CachedQuery`` thật của T-122 đi qua ``Protocol`` của T-123.

Google giả: ``tests/fake_google.py`` (bộ chặn mạng của ``conftest.py`` vẫn bật), khóa RSA sinh lúc
chạy test. WordPress giả ở file này. Mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import os
import threading
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fake_google import EMAIL, SC_SITES, SEARCH_CONSOLE, FakeGoogle, key_info, make_session
from fake_google import new_private_key as make_private_key

from seo_app.config import Settings, load_settings
from seo_app.google import search_console
from seo_app.google.search_console import (
    SearchConsoleClient,
    SearchConsoleError,
    SearchResult,
    SiteEntry,
    parse_property,
)
from seo_app.google.service_account import SEARCH_CONSOLE_SCOPE, load_service_account
from seo_app.storage import search_cache
from seo_app.storage.search_cache import (
    CachedDay,
    CachedQuery,
    CacheScope,
    SearchCache,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.storage.site_index import SiteIndex, SiteIndexStore
from seo_app.tracking import refresh as refresh_module
from seo_app.tracking.flags import page_flags
from seo_app.tracking.keywords import keyword_table, page_queries
from seo_app.tracking.match import build_tracking
from seo_app.tracking.model import FlagKind
from seo_app.tracking.periods import day_text, last_days, previous_period
from seo_app.tracking.refresh import (
    HOST_SAME_SITE,
    MSG_ALL_INSIDE,
    MSG_BUSY,
    MSG_CLOCK_BACK,
    MSG_DONE,
    MSG_EMPTY_CACHE,
    MSG_FAILED,
    MSG_KEYWORDS_FAILED,
    MSG_KEYWORDS_TRUNCATED,
    MSG_LAST_DAY,
    MSG_LISTED,
    MSG_MAY_HAVE_NEW,
    MSG_MOSTLY_OUTSIDE,
    MSG_NO_IMPRESSIONS,
    MSG_NO_RECENT_DATA,
    MSG_NOT_LISTED,
    MSG_NOT_OFFERED,
    MSG_OVERRIDDEN,
    MSG_PARTIAL,
    MSG_PERMISSION_HIGH,
    MSG_POST_DATES_FAILED,
    MSG_PROVISIONAL,
    MSG_RECENT,
    MSG_SAVED,
    MSG_SITE_INDEX_NONE,
    MSG_SITE_INDEX_OLD,
    MSG_STUCK,
    MSG_UNVERIFIED,
    HostShare,
    Outcome,
    PropertyList,
    check_connection,
    find_properties,
    refresh,
    refresh_hint,
    save_property,
)
from seo_app.tracking.stats import aggregate, compare
from seo_app.wordpress.client import PostState, PublishedItem, WordPressError

PT = ZoneInfo("America/Los_Angeles")
VN = ZoneInfo("Asia/Ho_Chi_Minh")
T = date(2026, 11, 3)  # hôm nay theo giờ PT
NOW = datetime(2026, 11, 3, 9, 0, tzinfo=PT)
WORDPRESS = "https://suachuacuasat.com"
DOMAIN = "sc-domain:suachuacuasat.com"
PREFIX_PROPERTY = "https://suachuacuasat.com/"
STAGING = "https://www.staging-m.suachuacuasat.com/"
QUERY_URL = SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com/searchAnalytics/query"
PREFIX_QUERY_URL = SEARCH_CONSOLE + "sites/https%3A%2F%2Fsuachuacuasat.com%2F/searchAnalytics/query"
PAGE_A = WORDPRESS + "/sua-cua-keo/"
PAGE_B = WORDPRESS + "/bai-moi/"
PAGE_C = WORDPRESS + "/lien-he/"
KEYWORDS = ("sửa cửa kéo", "cửa kéo bị kẹt")
FIRST_PROVISIONAL = T + timedelta(days=-2)  # ngày tạm đầu tiên mặc định của Google giả


def d(days: int) -> date:
    """Ngày T + ``days`` (âm: trước hôm nay)."""
    return T + timedelta(days=days)


# ---------------------------------------------------------------- Search Console giả


class Search:
    """Search Console giả gắn vào ``FakeGoogle``: mỗi ngày một dòng cho ``PAGE_A``; ``metadata``
    tự tính từ ``incomplete`` (ngày tạm đầu tiên) hay đặt riêng từng đoạn qua ``override``."""

    def __init__(self, fake: FakeGoogle) -> None:
        self.incomplete: date | None = d(-2)
        self.metadata = "auto"  # "auto", "missing", "bad"
        self.override: dict[tuple[date, date], object] = {}  # đoạn → giá trị (None: không có)
        self.fail: dict[int, tuple[int, dict, dict]] = {}  # lệnh query thứ n (từ 1) → trả lỗi
        self.bodies: list[dict] = []
        self.last_final = d(-3)  # «Kiểm tra»: ngày cuối có số liệu đã chốt
        self.sites = [{"siteUrl": DOMAIN, "permissionLevel": "siteRestrictedUser"}]
        self.host_rows = [(PAGE_A, 90), (STAGING + "x/", 6), ("http://suachuacuasat.com/y/", 4)]
        self.bad_rows = 0  # dòng sai dạng thêm vào mỗi câu trả lời Q1
        self.entered = threading.Event()
        self.release: threading.Event | None = None  # đặt thì lệnh query đầu tiên chờ
        fake.on("POST", QUERY_URL, self.query)
        fake.on("POST", PREFIX_QUERY_URL, self.query)
        fake.on("GET", SC_SITES, lambda _request: {"siteEntry": self.sites})

    def day_ranges(self) -> list[tuple[date, date]]:
        return [
            (date.fromisoformat(body["startDate"]), date.fromisoformat(body["endDate"]))
            for body in self.bodies
            if body["dimensions"] == ["date", "page"]
        ]

    def keyword_ranges(self) -> list[tuple[date, date]]:
        return [
            (date.fromisoformat(body["startDate"]), date.fromisoformat(body["endDate"]))
            for body in self.bodies
            if body["dimensions"] == ["page", "query"]
        ]

    def query(self, request):
        body = json.loads(request.body)
        self.bodies.append(body)
        self.entered.set()
        if self.release is not None:
            self.release.wait(10)
        failure = self.fail.get(len(self.bodies))
        if failure is not None:
            return failure
        start = date.fromisoformat(body["startDate"])
        end = date.fromisoformat(body["endDate"])
        dimensions = body["dimensions"]
        if dimensions == ["date", "page"]:
            days = [start + timedelta(days=n) for n in range((end - start).days + 1)]
            rows = [row([day.isoformat(), PAGE_A]) for day in days]
            bad = row([start.isoformat(), PAGE_B], clicks=11, impressions=10)
            result = answer(rows + [bad] * self.bad_rows)
            meta = self._metadata(start, end)
            if meta is not None:
                result["metadata"] = meta
            return result
        if dimensions == ["page", "query"]:
            return answer(
                [row([PAGE_A, KEYWORDS[0]], clicks=3), row([PAGE_A, KEYWORDS[1]], clicks=1)]
            )
        if dimensions == ["date"]:
            last = min(end, self.last_final)
            days = [start + timedelta(days=n) for n in range((last - start).days + 1)]
            return answer([row([day.isoformat()]) for day in days])
        return answer([row([url], impressions=count, clicks=0) for url, count in self.host_rows])

    def _metadata(self, start: date, end: date) -> dict | None:
        if (start, end) in self.override:
            value = self.override[(start, end)]
            return None if value is None else {"first_incomplete_date": value}
        if self.metadata == "missing" or self.incomplete is None or self.incomplete > end:
            return None
        if self.metadata == "bad":
            return {"first_incomplete_date": "không phải ngày"}
        return {"first_incomplete_date": max(self.incomplete, start).isoformat()}


def row(keys, *, clicks=1, impressions=10, position=3.5):
    return {
        "keys": keys,
        "clicks": clicks,
        "impressions": impressions,
        "ctr": clicks / impressions,
        "position": position,
    }


def answer(rows):
    return {"rows": rows, "responseAggregationType": "byPage"}


# ---------------------------------------------------------------- WordPress giả


def post(post_id: int, link: str, kind: str = "post") -> PublishedItem:
    return PublishedItem(post_id, kind, f"bai-{post_id}", link, f"Bài {post_id}")


@dataclass
class FakeWordPress:
    base_url: str = WORDPRESS
    items: list[PublishedItem] = field(
        default_factory=lambda: [post(1, PAGE_A), post(2, PAGE_B), post(3, PAGE_C, "page")]
    )
    states: dict[int, PostState] = field(
        default_factory=lambda: {
            1: PostState(1, "publish", "2026-01-05T02:00:00"),
            2: PostState(2, "publish", "2026-10-30T03:00:00"),  # 20:00 29/10 giờ PT
        }
    )
    fail_list: bool = False
    fail_status: bool = False
    listed: int = 0
    asked: list[list[int]] = field(default_factory=list)

    def list_published(self):
        self.listed += 1
        if self.fail_list:
            raise WordPressError("Lỗi mạng khi gọi WordPress. Thử lại sau.")
        return list(self.items)

    def post_statuses(self, post_ids):
        ids = list(post_ids)
        self.asked.append(ids)
        if self.fail_status:
            raise WordPressError("Lỗi mạng khi gọi WordPress. Thử lại sau.")
        return {post_id: self.states[post_id] for post_id in ids if post_id in self.states}


# ---------------------------------------------------------------- fixture


@pytest.fixture(scope="module")
def private_key():
    return make_private_key()


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def key_file(tmp_path, private_key):
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    path = folder / "du-an-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    return path


@pytest.fixture
def account(key_file, project):
    return load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def google(fake):
    return Search(fake)


@pytest.fixture
def settings(key_file):
    return Settings(
        wordpress_url=WORDPRESS, gsc_site_url=DOMAIN, google_service_account_file=key_file
    )


@pytest.fixture
def store(project):
    return SearchCacheStore(path=project / "data" / "search_cache.sqlite")


@pytest.fixture
def index_store(project, monkeypatch):
    store = SiteIndexStore(path=project / "data" / "site_index.sqlite")
    monkeypatch.setattr(store, "_now", lambda: NOW)  # mốc tải danh sách theo giờ của test
    return store


@pytest.fixture
def wordpress():
    return FakeWordPress()


class Factory:
    """Dựng client như ``from_settings`` nhưng dùng Google giả, ngày PT ``today`` của test."""

    def __init__(self, account, fake, **options):
        self.account = account
        self.fake = fake
        self.options = options
        self.today = T
        self.created: list[SearchConsoleClient] = []
        self.calls: list[dict] = []

    def __call__(self, settings, *, with_property=True):
        self.calls.append({"with_property": with_property})
        site = parse_property(settings.gsc_site_url) if with_property else None
        client = SearchConsoleClient(
            self.account,
            settings.wordpress_url,
            site,
            session=make_session(self.fake),
            today=lambda: self.today,
            sleep=lambda _seconds: None,
            **self.options,
        )
        self.created.append(client)
        return client


@pytest.fixture
def factory(account, fake):
    return Factory(account, fake)


def run(settings, store, factory, *, now=NOW, **kwargs):
    factory.today = (now.astimezone(PT)).date()
    return refresh(settings, store, client_factory=factory, now=now, **kwargs)


def scope(settings) -> CacheScope:
    return CacheScope(settings.gsc_site_url, settings.wordpress_url)


def first_fetch_ranges() -> list[tuple[date, date]]:
    """16 đoạn của lần lấy đầu: 15 đoạn cũ (14 đoạn 31 ngày + 1 đoạn 21 ngày), rồi 31 ngày cuối."""
    ranges = [(d(-485 + 31 * n), d(-455 + 31 * n)) for n in range(14)]
    return [*ranges, (d(-51), d(-31)), (d(-30), d(0))]


# ================================================================ lần lấy đầu, chia đoạn


def test_lan_dau_lay_16_thang_chia_doan_cu_toi_moi(settings, store, factory, google):
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == first_fetch_ranges()
    for start, end in google.day_ranges():
        assert (end - start).days < 31
    # Từ khóa: kỳ 28 ngày tới E và kỳ trước liền kề (E = ngày trước ngày tạm đầu tiên).
    assert google.keyword_ranges() == [(d(-30), d(-3)), (d(-58), d(-31))]
    assert report.requests == 18 == len(google.bodies)
    assert report.final_end == d(-3)
    assert report.message == (
        f"{MSG_DONE.format(day=day_text(d(-3)))} {MSG_PROVISIONAL.format(count=3)}"
    )
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (d(-485), T, d(-2))
    assert len(cache.days) == 486
    assert all(row.final is (row.day < d(-2)) for row in cache.days)
    assert {(item.start, item.end) for item in cache.ranges} == {(d(-30), d(-3)), (d(-58), d(-31))}
    assert {row.query for row in cache.queries} == set(KEYWORDS)


def test_lan_sau_chi_lay_tu_ngay_tam_dau_tien(settings, store, factory, google):
    run(settings, store, factory)
    google.bodies.clear()
    google.incomplete = d(-1)  # một ngày nữa đã chốt
    report = run(settings, store, factory, now=NOW + timedelta(days=1))
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == [(d(-2), d(1))]
    assert google.keyword_ranges() == [(d(-29), d(-2)), (d(-57), d(-30))]
    assert report.requests == 3
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (
        d(-484),
        d(1),
        d(-1),
    )
    assert report.final_end == d(-2)


def test_lay_tiep_sau_nhieu_ngay_doan_dau_toi_het_phan_da_luu(settings, store, factory, google):
    run(settings, store, factory)
    google.bodies.clear()
    later = NOW + timedelta(days=40)
    google.incomplete = d(38)
    report = run(settings, store, factory, now=later)
    assert report.outcome is Outcome.DONE
    # Đoạn đầu bắt đầu ở ngày tạm cũ (T-2), tới ít nhất T (luật nối liền của cache), dừng trước
    # 31 ngày cuối; đoạn sau là 31 ngày cuối.
    assert google.day_ranges() == [(d(-2), d(9)), (d(10), d(40))]
    cache = store.load(scope(settings))
    assert (cache.covered_end, cache.first_provisional) == (d(40), d(38))


@pytest.mark.parametrize(
    ("start", "reach", "end"),
    [
        (d(-3), None, T),
        (d(-30), None, T),
        (d(-31), None, d(-31)),
        (d(-485), None, d(-455)),
        (d(-51), None, d(-31)),
        (d(-42), d(-40), d(-31)),
        (d(-33), d(-5), d(-5)),
        (d(-33), T, d(-3)),
        (d(-2), T, T),
    ],
    ids=[
        "3-ngay",
        "31-ngay",
        "32-ngay",
        "dau-16-thang",
        "doan-ngan",
        "reach-truoc",
        "reach-trong",
        "reach-hom-nay",
        "reach-ngan",
    ],
)
def test_ngay_cuoi_cua_doan(start, reach, end):
    assert refresh_module._chunk_end(start, T, reach) == end


@pytest.mark.parametrize(
    ("metadata", "first", "end", "expected"),
    [
        ("ok", d(-2), T, d(-2)),
        ("ok", d(-40), d(-31), d(-40)),
        ("missing", None, d(-31), None),
        ("missing", None, T, d(-2)),
        ("bad", None, d(-31), d(-33)),
        ("bad", None, T, d(-2)),
    ],
    ids=["ok-moi", "ok-cu", "thieu-cu", "thieu-moi", "sai-cu", "sai-moi"],
)
def test_ngay_tam_dau_tien_cua_doan(metadata, first, end, expected):
    result = SearchResult((), 0, False, first_incomplete_date=first, metadata=metadata)
    assert refresh_module._first_provisional(result, end - timedelta(days=30), end, T) == expected


def test_doan_mot_ngay_thieu_metadata_ca_doan_la_so_tam():
    result = SearchResult((), 0, False, metadata="missing")
    assert refresh_module._first_provisional(result, T, T, T) == T


# ================================================================ số tạm (thiết kế 2.4)


@pytest.mark.parametrize("value", [None, "2026-13-01"], ids=["thieu", "sai-dang"])
def test_doan_moi_nhat_thieu_hay_sai_metadata_3_ngay_cuoi_la_tam(
    settings, store, factory, google, value
):
    google.override[(d(-30), T)] = value
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    cache = store.load(scope(settings))
    assert cache.first_provisional == d(-2)
    assert report.final_end == d(-3)


def test_doan_cu_metadata_sai_dang_lay_lai_tu_ngay_tam(settings, store, factory, google):
    google.override[(d(-51), d(-31))] = "2026-02-30"
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    assert google.day_ranges()[-3:] == [(d(-51), d(-31)), (d(-33), d(-3)), (d(-2), T)]
    assert report.requests == 19
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (d(-485), T, d(-2))
    assert all(row.final is (row.day < d(-2)) for row in cache.days)


def test_doan_cu_bao_so_tam_hon_31_ngay_dung_khong_lap(settings, store, factory, google):
    google.incomplete = d(-40)  # Google báo số tạm từ 40 ngày trước: không tiến được
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL
    assert report.notes[0] == MSG_STUCK
    assert google.day_ranges()[-2:] == [(d(-51), d(-31)), (d(-40), d(-10))]
    assert len(google.day_ranges()) == 16  # không lặp mãi
    assert google.keyword_ranges() == []
    cache = store.load(scope(settings))
    assert (cache.covered_end, cache.first_provisional) == (d(-10), d(-40))
    assert report.message == MSG_PARTIAL.format(day=day_text(d(-41)))
    assert all(row.final is (row.day < d(-40)) for row in cache.days)


def test_sau_khi_ket_lan_bam_sau_lay_tiep_duoc(settings, store, factory, google):
    # Phần đã lưu tới T-10, ngày tạm từ T-40: đoạn đầu lần sau phải tới hết T-10 (luật nối liền
    # của cache), không dừng trước 31 ngày cuối như thường lệ.
    google.incomplete = d(-40)
    run(settings, store, factory)
    google.bodies.clear()
    google.incomplete = d(-2)  # Google đã chốt các ngày đó
    report = run(settings, store, factory, now=NOW + timedelta(minutes=1))
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == [(d(-40), d(-10)), (d(-9), T)]
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (d(-485), T, d(-2))
    assert all(row.final is (row.day < d(-2)) for row in cache.days)


def test_chua_co_ngay_nao_da_chot(settings, store, factory, google):
    google.incomplete = d(-485)
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL  # đoạn đầu cả đoạn là số tạm: không tiến được
    assert report.final_end is None
    assert report.message == refresh_module.MSG_PARTIAL_NO_DAY


# ================================================================ chặn bấm lại


def test_bam_lai_trong_10_phut_khong_gui_lenh(settings, store, factory, google):
    run(settings, store, factory)
    sent = len(google.bodies)
    report = run(settings, store, factory, now=NOW + timedelta(minutes=9))
    assert report.outcome is Outcome.RECENT
    assert report.requests == 0
    assert len(google.bodies) == sent
    stamp = NOW.astimezone(VN)
    assert report.message == MSG_RECENT.format(time=f"{stamp:%H:%M} {day_text(stamp.date())}")
    assert report.final_end == d(-3)
    assert len(factory.created) == 2  # vẫn một client mỗi lần bấm (kiểm lại cấu hình)


def test_bam_lai_sau_10_phut_chi_lay_doan_tam(settings, store, factory, google):
    run(settings, store, factory)
    google.bodies.clear()
    report = run(settings, store, factory, now=NOW + timedelta(minutes=10))
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == [(d(-2), T)]
    assert google.keyword_ranges() == []  # đã có từ khóa hai kỳ
    assert report.requests == 1


def test_moc_lay_o_tuong_lai_coi_nhu_cu(settings, store, factory, google):
    run(settings, store, factory, now=NOW + timedelta(hours=2))  # đồng hồ máy từng chạy nhanh
    google.bodies.clear()
    report = run(settings, store, factory, now=NOW)
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == [(d(-2), T)]


def test_moc_lay_lech_vai_phut_van_chan(settings, store, factory, google):
    run(settings, store, factory, now=NOW + timedelta(minutes=3))
    report = run(settings, store, factory, now=NOW)
    assert report.outcome is Outcome.RECENT


def test_sang_ngay_moi_khong_chan(settings, store, factory, google):
    late = datetime(2026, 11, 3, 23, 58, tzinfo=PT)
    run(settings, store, factory, now=late)
    google.bodies.clear()
    report = run(settings, store, factory, now=late + timedelta(minutes=4))
    assert report.outcome is Outcome.DONE
    assert google.day_ranges() == [(d(-2), d(1))]


def test_dong_ho_chinh_lui_bo_cache_lay_lai(settings, store, factory, google):
    run(settings, store, factory)
    google.bodies.clear()
    google.incomplete = d(-7)
    report = run(settings, store, factory, now=NOW - timedelta(days=5))
    assert report.outcome is Outcome.DONE
    assert MSG_CLOCK_BACK in report.notes
    assert store.reset_count == 1
    assert google.day_ranges()[0] == (d(-490), d(-460))
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end) == (d(-490), d(-5))


# ================================================================ lỗi, trần lệnh


def test_het_tran_lenh_dung_giu_phan_da_luu_lan_sau_lay_tiep(
    settings, store, account, fake, google
):
    factory = Factory(account, fake, max_requests=5)
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL
    assert report.notes[0] == search_console._MSG_BUDGET.format(count=5)
    assert report.requests == 5
    assert report.message == MSG_PARTIAL.format(day=day_text(d(-331)))
    assert store.load(scope(settings)).covered_end == d(-331)
    google.bodies.clear()
    report = run(settings, store, factory, now=NOW + timedelta(minutes=1))
    assert google.day_ranges()[0] == (d(-330), d(-300))
    assert report.outcome is Outcome.PARTIAL
    for _ in range(2):
        report = run(settings, store, factory, now=NOW + timedelta(minutes=2))
    assert report.outcome is Outcome.DONE
    cache = store.load(scope(settings))
    assert (cache.covered_start, cache.covered_end, cache.first_provisional) == (d(-485), T, d(-2))
    assert len(cache.ranges) == 2


def test_tran_20_lenh_cua_client_that(settings, store, factory, google):
    # Lần đầu cần 18 lệnh. Google trả 429 năm lần (mỗi lần client thử lại một lần, lần thử lại
    # qua): 5 lệnh thêm nên lệnh thứ 21 (đoạn 16) chạm trần 20 của client thật (LC-T120-8).
    google.fail = {n: (429, {"error": {"code": 429}}, {}) for n in (3, 5, 7, 9, 11)}
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL
    assert report.requests == 20 == len(google.bodies)
    assert report.notes[0] == search_console._MSG_BUDGET.format(count=20)
    assert report.message == MSG_PARTIAL.format(day=day_text(d(-31)))
    cache = store.load(scope(settings))
    assert (cache.covered_end, cache.first_provisional) == (d(-31), None)
    assert google.keyword_ranges() == []


def test_loi_giua_chung_dung_o_loi_dau_tien(settings, store, factory, google):
    google.fail = {3: (500, {"error": {"code": 500, "message": "LOI-MAY-CHU"}}, {})}
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL
    assert len(google.bodies) == 3  # không gửi thêm lệnh nào sau lỗi
    assert report.requests == 3
    assert report.message == MSG_PARTIAL.format(day=day_text(d(-424)))
    assert "LOI-MAY-CHU" not in " ".join(report.notes)
    assert store.load(scope(settings)).covered_end == d(-424)


def test_loi_ngay_lenh_dau_khong_luu_gi(settings, store, factory, google):
    google.fail = {1: (403, {"error": {"code": 403, "message": "LOI-MAY-CHU"}}, {})}
    report = run(settings, store, factory)
    assert report.outcome is Outcome.FAILED
    assert report.message == MSG_FAILED
    assert "403" in report.notes[0] and "LOI-MAY-CHU" not in report.notes[0]
    assert report.final_end is None
    assert store.load(scope(settings)) is None


def test_loi_tu_khoa_giu_so_lieu_ngay(settings, store, factory, google):
    google.fail = {17: (500, {"error": {"code": 500}}, {})}
    report = run(settings, store, factory)
    assert report.outcome is Outcome.PARTIAL
    assert report.message.startswith(MSG_DONE.format(day=day_text(d(-3))))
    assert report.notes[0].startswith(MSG_KEYWORDS_FAILED)
    google.bodies.clear()
    google.fail = {}
    report = run(settings, store, factory, now=NOW + timedelta(minutes=1))
    assert report.outcome is Outcome.DONE  # thiếu từ khóa: không bị chặn bấm lại
    assert google.day_ranges() == [(d(-2), T)]
    assert google.keyword_ranges() == [(d(-30), d(-3)), (d(-58), d(-31))]


def test_dong_sai_dang_bi_bo_va_dem(settings, store, factory, google):
    google.bad_rows = 1  # 1/32 dòng mỗi đoạn: dưới ngưỡng 10% nên client chỉ bỏ dòng đó
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    assert report.notes == (MSG_SITE_INDEX_NONE, refresh_module.MSG_DROPPED.format(count=16))
    assert all(row.page == PAGE_A for row in store.load(scope(settings)).days)


def test_doan_ngay_cham_tran_dong_ghi_chu_mot_lan(settings, store, factory, google, monkeypatch):
    original = SearchConsoleClient.fetch_day_page

    def truncated(self, start, end):
        return dataclasses.replace(original(self, start, end), truncated=True)

    monkeypatch.setattr(SearchConsoleClient, "fetch_day_page", truncated)
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    # Ghi chú một lần dù cả 16 đoạn đều chạm trần.
    assert report.notes == (refresh_module.MSG_TRUNCATED, MSG_SITE_INDEX_NONE)


def test_tu_khoa_cham_tran_ghi_chu(settings, store, factory, google, monkeypatch):
    def truncated(self, start, end):
        return SearchResult((), 0, True)

    monkeypatch.setattr(SearchConsoleClient, "fetch_page_query", truncated)
    report = run(settings, store, factory)
    assert report.outcome is Outcome.DONE
    assert MSG_KEYWORDS_TRUNCATED in report.notes
    assert all(item.truncated for item in store.load(scope(settings)).ranges)


def test_file_khoa_hong_bao_failed_khong_gui_lenh(settings, store, google, fake, key_file):
    key_file.write_text("{}", encoding="utf-8")
    report = refresh(settings, store, now=NOW)  # client mặc định: from_settings
    assert report.outcome is Outcome.FAILED
    assert report.requests == 0
    assert fake.requests == []


def test_cache_loi_bao_cau_co_dinh(settings, store, factory, google, monkeypatch):
    def broken(self, scope):
        raise SearchCacheError(search_cache.MSG_BUSY)

    monkeypatch.setattr(SearchCacheStore, "load", broken)
    report = run(settings, store, factory)
    assert report.outcome is Outcome.FAILED
    assert report.notes == (search_cache.MSG_BUSY,)
    assert google.bodies == []


def test_gio_may_khong_hop_le(settings, store, factory, google):
    report = refresh(settings, store, client_factory=factory, now=datetime(1, 1, 1, tzinfo=UTC))
    assert report.outcome is Outcome.FAILED
    assert report.notes == (refresh_module.MSG_CLOCK,)
    assert factory.created == []


# ================================================================ khóa, một client mỗi lần bấm


def test_khoa_dang_giu_tab_khac_bao_ban(settings, store, factory, google):
    # Tab khác đang giữ khóa. Lần bấm này chạy ở luồng riêng, có hạn chờ: bản lỗi chờ khóa thì
    # test hỏng (không treo cả lượt chạy test).
    results = []
    assert refresh_module._FETCH_LOCK.acquire(blocking=False)
    try:
        worker = threading.Thread(target=lambda: results.append(run(settings, store, factory)))
        worker.start()
        worker.join(10)
        finished = not worker.is_alive()
    finally:
        refresh_module._FETCH_LOCK.release()
        worker.join(30)
    assert finished, "refresh phải trả BUSY ngay, không chờ khóa"
    (report,) = results
    assert (report.outcome, report.message, report.requests) == (Outcome.BUSY, MSG_BUSY, 0)
    assert factory.created == []
    assert google.bodies == []


def test_hai_tab_cung_bam_chi_mot_lan_lay(settings, store, factory, google):
    google.release = threading.Event()
    results = []
    worker = threading.Thread(target=lambda: results.append(run(settings, store, factory)))
    worker.start()
    try:
        assert google.entered.wait(10)
        other = refresh(settings, store, client_factory=factory, now=NOW)
        assert other.outcome is Outcome.BUSY
        assert len(factory.created) == 1
    finally:
        google.release.set()
        worker.join(30)
    assert results[0].outcome is Outcome.DONE
    assert not refresh_module._FETCH_LOCK.locked()


def test_khoa_nha_ca_khi_loi_bat_ngo(settings, store, factory, monkeypatch):
    def crash(self, *args, **kwargs):
        raise RuntimeError("lỗi bất ngờ")

    monkeypatch.setattr(refresh_module._Refresh, "go", crash)
    with pytest.raises(RuntimeError):
        run(settings, store, factory)
    assert not refresh_module._FETCH_LOCK.locked()


def test_moi_lan_bam_mot_client_tu_from_settings(
    settings, store, account, fake, google, monkeypatch
):
    built = []

    def from_settings(cls, settings, *, session=None, with_property=True):
        built.append(with_property)
        return SearchConsoleClient(
            account,
            settings.wordpress_url,
            parse_property(settings.gsc_site_url),
            session=make_session(fake),
            today=lambda: T,
        )

    monkeypatch.setattr(SearchConsoleClient, "from_settings", classmethod(from_settings))
    refresh(settings, store, now=NOW)
    refresh(settings, store, now=NOW + timedelta(minutes=1))
    assert built == [True, True]


# ================================================================ từ khóa, ngày đăng


def test_ngay_dang_chi_hoi_bai_khong_co_luot_hien_thi(
    settings, store, factory, google, index_store, wordpress
):
    report = run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert report.outcome is Outcome.DONE
    assert wordpress.asked == [[2]]  # bài 1 có lượt hiển thị; mục 3 là trang, không phải bài
    cache = store.load(scope(settings))
    assert dict(cache.post_dates) == {2: date(2026, 10, 29)}  # 03:00 UTC = 20:00 giờ PT hôm trước
    assert wordpress.listed == 1
    run(
        settings,
        store,
        factory,
        now=NOW + timedelta(minutes=11),
        site_index=index_store,
        wordpress=wordpress,
    )
    assert wordpress.asked == [[2]]  # đã có ngày đăng: không hỏi lại
    assert wordpress.listed == 1  # danh sách chưa quá 6 giờ: không tải lại


def test_danh_sach_bai_cu_hon_6_gio_tai_lai(
    settings, store, factory, google, index_store, wordpress
):
    index_store.save(SiteIndex(WORDPRESS, NOW - timedelta(hours=7), (post(1, PAGE_A),)))
    run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert wordpress.listed == 1
    assert {item.id for item in index_store.load(WORDPRESS).items} == {1, 2, 3}


def test_wordpress_loi_dung_danh_sach_cu(settings, store, factory, google, index_store, wordpress):
    old = NOW - timedelta(hours=7)
    index_store.save(SiteIndex(WORDPRESS, old, (post(2, PAGE_B),)))
    wordpress.fail_list = True
    report = run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert report.outcome is Outcome.DONE
    stamp = old.astimezone(VN)
    assert MSG_SITE_INDEX_OLD.format(time=f"{stamp:%H:%M} {day_text(stamp.date())}") in report.notes
    assert wordpress.asked == [[2]]


def test_wordpress_loi_khong_co_danh_sach_cu(
    settings, store, factory, google, index_store, wordpress
):
    wordpress.fail_list = True
    report = run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert report.outcome is Outcome.DONE
    assert MSG_SITE_INDEX_NONE in report.notes
    assert wordpress.asked == []


def test_hoi_ngay_dang_loi_chi_ghi_chu(settings, store, factory, google, index_store, wordpress):
    wordpress.fail_status = True
    report = run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert report.outcome is Outcome.DONE
    assert MSG_POST_DATES_FAILED in report.notes
    assert dict(store.load(scope(settings)).post_dates) == {}


def test_chua_ket_noi_wordpress_dung_danh_sach_da_luu(
    settings, store, factory, google, index_store
):
    index_store.save(SiteIndex(WORDPRESS, NOW, (post(2, PAGE_B),)))
    report = run(settings, store, factory, site_index=index_store)
    assert report.outcome is Outcome.DONE
    assert MSG_SITE_INDEX_NONE not in report.notes
    assert dict(store.load(scope(settings)).post_dates) == {}


def test_khong_co_kho_danh_sach_bai(settings, store, factory, google, wordpress):
    report = run(settings, store, factory, wordpress=wordpress)
    assert MSG_SITE_INDEX_NONE in report.notes
    assert wordpress.asked == []


def test_ngay_dang_cua_bai_da_go_bi_bo(settings, store, factory, google, index_store, wordpress):
    run(settings, store, factory)  # tạo cache cùng phạm vi
    store.save_post_dates(scope(settings), {99: d(-100), 2: d(-5)})
    run(
        settings,
        store,
        factory,
        now=NOW + timedelta(minutes=11),
        site_index=index_store,
        wordpress=wordpress,
    )
    assert dict(store.load(scope(settings)).post_dates) == {2: d(-5)}
    assert wordpress.asked == []  # bài 2 đã có ngày đăng


def test_ngay_dang_wordpress_sai_dang_bi_bo(
    settings, store, factory, google, index_store, wordpress
):
    wordpress.states[2] = PostState(2, "publish", "")
    run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    assert dict(store.load(scope(settings)).post_dates) == {}


# ================================================================ thử chung T-122 × T-123


def test_dataclass_that_cua_cache_qua_protocol_cua_loi_theo_doi(
    settings, store, factory, google, index_store, wordpress
):
    run(settings, store, factory, site_index=index_store, wordpress=wordpress)
    cache = store.load(scope(settings))
    assert all(type(row) is CachedDay for row in cache.days)
    assert all(type(row.final) is bool and type(row.day) is date for row in cache.days)
    assert all(type(row) is CachedQuery for row in cache.queries)
    current = last_days(cache.final_end)
    previous = previous_period(current)
    items = index_store.load(WORDPRESS).items
    tracking = build_tracking(WORDPRESS, items, cache.days)
    assert tracking.skipped_rows == 0 and tracking.skipped_items == 0
    pages = {page.item.id: page for page in tracking.pages}
    stats_a = aggregate(pages[1].days, current)
    assert (stats_a.clicks, stats_a.impressions) == (28, 280)
    table = keyword_table(
        page_queries(cache.queries, site=WORDPRESS, key=pages[1].key, period=current),
        page_queries(cache.queries, site=WORDPRESS, key=pages[1].key, period=previous),
        main_keyword="Sửa cửa kéo",
    )
    assert [group.text for group in table.groups] == list(KEYWORDS)
    assert table.groups[0].is_main and table.has_previous
    quiet = pages[2]
    comparison = compare(aggregate(quiet.days, current), aggregate(quiet.days, previous))
    flags = page_flags(quiet, comparison, end=current.end, published=cache.post_dates[2])
    assert [flag.kind for flag in flags] == [FlagKind.NEW]


# ================================================================ gợi ý (thiết kế 3.3)


def cache_with(*, fetched_at, covered_end=T, first_provisional=FIRST_PROVISIONAL):
    return SearchCache(fetched_at, d(-485), covered_end, first_provisional, (), (), (), {})


@pytest.mark.parametrize(
    ("cache", "expected"),
    [
        (None, MSG_EMPTY_CACHE),
        (cache_with(fetched_at=NOW), ""),
        (cache_with(fetched_at=NOW - timedelta(hours=23)), ""),
        (cache_with(fetched_at=NOW - timedelta(hours=25)), MSG_MAY_HAVE_NEW),
        (cache_with(fetched_at=NOW + timedelta(hours=1)), MSG_MAY_HAVE_NEW),
        (cache_with(fetched_at=NOW, covered_end=d(-1), first_provisional=d(-2)), ""),
        (cache_with(fetched_at=NOW, covered_end=d(-1), first_provisional=d(-3)), MSG_MAY_HAVE_NEW),
        (cache_with(fetched_at=NOW, covered_end=d(-3), first_provisional=None), ""),
        (cache_with(fetched_at=NOW, covered_end=d(-4), first_provisional=None), MSG_MAY_HAVE_NEW),
        (cache_with(fetched_at=NOW, first_provisional=d(-485)), MSG_MAY_HAVE_NEW),
    ],
    ids=[
        "trong",
        "vua-lay",
        "23-gio",
        "25-gio",
        "tuong-lai",
        "e-3-ngay",
        "e-4-ngay",
        "het-tam-3",
        "het-tam-4",
        "chua-chot",
    ],
)
def test_goi_y_co_the_da_co_so_lieu_moi(cache, expected):
    assert refresh_hint(cache, now=NOW) == expected


def test_goi_y_khong_goi_mang(fake):
    assert refresh_hint(cache_with(fetched_at=datetime.now(UTC))) in ("", MSG_MAY_HAVE_NEW)
    assert fake.requests == []


# ================================================================ «Kiểm tra»


def test_kiem_tra_thuoc_tinh_ten_mien(settings, factory, google):
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert result.ok
    assert result.permission == "siteRestrictedUser"
    assert result.last_day == d(-3)
    assert result.outside_share == pytest.approx(0.1)
    assert result.hosts == (
        HostShare("www.staging-m.suachuacuasat.com", 6),
        HostShare("suachuacuasat.com", 4, HOST_SAME_SITE),
    )
    assert result.messages == (
        MSG_LISTED.format(permission="Hạn chế"),
        MSG_LAST_DAY.format(day=day_text(d(-3))),
        refresh_module.MSG_OUTSIDE.format(share="10,0%", days=28),
    )
    assert result.requests == 3
    days_body, hosts_body = google.bodies
    assert (days_body["startDate"], days_body["endDate"]) == (d(-9).isoformat(), T.isoformat())
    assert (hosts_body["startDate"], hosts_body["endDate"]) == (d(-27).isoformat(), T.isoformat())
    assert "dimensionFilterGroups" not in hosts_body


def test_kiem_tra_quyen_cao_canh_bao(settings, factory, google):
    google.sites = [{"siteUrl": DOMAIN, "permissionLevel": "siteOwner"}]
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert result.ok
    assert result.messages[:2] == (MSG_LISTED.format(permission="Chủ sở hữu"), MSG_PERMISSION_HIGH)


@pytest.mark.parametrize(
    ("sites", "message"),
    [
        ([{"siteUrl": DOMAIN, "permissionLevel": "siteUnverifiedUser"}], MSG_UNVERIFIED),
        ([{"siteUrl": STAGING, "permissionLevel": "siteRestrictedUser"}], MSG_NOT_LISTED),
        ([], MSG_NOT_LISTED),
    ],
    ids=["chua-xac-minh", "chi-thay-staging", "khong-thay"],
)
def test_kiem_tra_thuoc_tinh_khong_doc_duoc(settings, factory, google, sites, message):
    google.sites = sites
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert not result.ok
    assert message in result.messages
    assert result.requests == 1
    assert google.bodies == []


def test_kiem_tra_thuoc_tinh_tien_to_khong_dem_ten_may(key_file, factory, google):
    settings = Settings(
        wordpress_url=WORDPRESS, gsc_site_url=PREFIX_PROPERTY, google_service_account_file=key_file
    )
    google.sites = [{"siteUrl": PREFIX_PROPERTY, "permissionLevel": "siteRestrictedUser"}]
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert result.ok
    assert result.requests == 2
    assert result.outside_share is None and result.hosts == ()


@pytest.mark.parametrize(
    ("host_rows", "messages", "share"),
    [
        (
            [(PAGE_A, 5), (STAGING + "x/", 95)],
            (refresh_module.MSG_OUTSIDE.format(share="95,0%", days=28), MSG_MOSTLY_OUTSIDE),
            0.95,
        ),
        ([(PAGE_A, 50)], (MSG_ALL_INSIDE.format(days=28),), 0.0),
        ([], (MSG_NO_IMPRESSIONS.format(days=28),), None),
    ],
    ids=["gan-het-ngoai", "het-trong", "chua-co"],
)
def test_kiem_tra_phan_ngoai_website(settings, factory, google, host_rows, messages, share):
    google.host_rows = host_rows
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert result.ok
    assert result.messages[2:] == messages
    assert result.outside_share == share


def test_kiem_tra_chua_co_so_lieu_gan_day(settings, factory, google):
    google.last_final = d(-30)
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert result.last_day is None
    assert MSG_NO_RECENT_DATA.format(days=10) in result.messages


def test_kiem_tra_loi_google_cau_co_dinh(settings, factory, google):
    google.fail = {1: (403, {"error": {"code": 403, "message": "LOI-MAY-CHU"}}, {})}
    result = check_connection(settings, client_factory=factory, now=NOW)
    assert not result.ok
    assert "403" in result.messages[-1] and "LOI-MAY-CHU" not in result.messages[-1]
    assert result.requests == 2


def test_kiem_tra_file_khoa_hong(settings, key_file, fake):
    key_file.write_text("{}", encoding="utf-8")
    result = check_connection(settings, now=NOW)
    assert not result.ok and result.requests == 0
    assert fake.requests == []


# ================================================================ tìm, lưu thuộc tính


@pytest.fixture
def found(key_file, factory, google):
    google.sites = [
        {"siteUrl": DOMAIN, "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": PREFIX_PROPERTY, "permissionLevel": "siteUnverifiedUser"},
        {"siteUrl": STAGING, "permissionLevel": "siteRestrictedUser"},
    ]
    settings = Settings(wordpress_url=WORDPRESS, google_service_account_file=key_file)
    return find_properties(settings, client_factory=factory)


def test_tim_thuoc_tinh_khong_can_gsc_site_url(found, factory):
    assert factory.calls == [{"with_property": False}]
    assert found.account_email == EMAIL and found.message == ""
    assert [entry.site_url for entry in found.entries] == [DOMAIN, PREFIX_PROPERTY, STAGING]
    assert found.usable_site_urls == (DOMAIN,)


def test_tim_thuoc_tinh_mac_dinh_tu_from_settings(key_file, monkeypatch):
    calls = []

    def from_settings(cls, settings, *, session=None, with_property=True):
        calls.append(with_property)
        raise SearchConsoleError("thử")

    monkeypatch.setattr(SearchConsoleClient, "from_settings", classmethod(from_settings))
    result = find_properties(
        Settings(wordpress_url=WORDPRESS, google_service_account_file=key_file)
    )
    assert calls == [False]
    assert result.message == "thử" and result.entries == ()


@pytest.fixture
def env_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text("WORDPRESS_URL=https://suachuacuasat.com\nGSC_SITE_URL=\n", encoding="utf-8")
    return path


def test_luu_thuoc_tinh_vua_tim_thay(found, env_file):
    result = save_property(DOMAIN, found, env_file=env_file, environ={})
    assert result == refresh_module.SaveResult(True, MSG_SAVED)
    assert env_file.read_text(encoding="utf-8") == (
        "WORDPRESS_URL=https://suachuacuasat.com\nGSC_SITE_URL=sc-domain:suachuacuasat.com\n"
    )
    assert load_settings(env_file, environ={}).gsc_site_url == DOMAIN


@pytest.mark.parametrize(
    "site_url",
    [PREFIX_PROPERTY, STAGING, "sc-domain:khac.com", DOMAIN + " ", DOMAIN.upper(), None, 1],
    ids=["chua-xac-minh", "staging", "go-tay", "dau-cach", "chu-hoa", "none", "so"],
)
def test_luu_thuoc_tinh_khong_duoc_chon_bi_tu_choi(found, env_file, site_url):
    before = env_file.read_bytes()
    result = save_property(site_url, found, env_file=env_file, environ={})
    assert result == refresh_module.SaveResult(False, MSG_NOT_OFFERED)
    assert env_file.read_bytes() == before


@pytest.mark.parametrize(
    "found_value",
    [[DOMAIN], (DOMAIN,), {DOMAIN}, DOMAIN, None],
    ids=["list", "tuple", "set", "chuoi", "none"],
)
def test_luu_thuoc_tinh_phai_tu_ket_qua_tim(env_file, found_value):
    before = env_file.read_bytes()
    result = save_property(DOMAIN, found_value, env_file=env_file, environ={})
    assert not result.ok
    assert env_file.read_bytes() == before


def test_luu_thuoc_tinh_muc_gia_mao_qua_bo_kiem_chat(env_file):
    # SiteEntry dựng tay (không qua client) với giá trị có xuống dòng: parse_property và bộ kiểm
    # của env_file đều chặn; file .env không đổi.
    sneaky = DOMAIN + "\nAPP_PASSWORD_HASH=x"
    fake_found = PropertyList((SiteEntry(sneaky, "siteRestrictedUser", "domain", True),))
    before = env_file.read_bytes()
    result = save_property(sneaky, fake_found, env_file=env_file, environ={})
    assert not result.ok
    assert "APP_PASSWORD_HASH" not in result.message and "\n" not in result.message
    assert env_file.read_bytes() == before


@pytest.mark.parametrize("value", ["", "sc-domain:khac.com"], ids=["rong", "co-gia-tri"])
def test_luu_thuoc_tinh_bao_bien_moi_truong_de_env(found, env_file, value):
    result = save_property(DOMAIN, found, env_file=env_file, environ={"GSC_SITE_URL": value})
    assert result.ok and result.overridden
    assert result.message == f"{MSG_SAVED} {MSG_OVERRIDDEN}"
    assert value == "" or value not in result.message
    assert load_settings(env_file, environ={"GSC_SITE_URL": value}).gsc_site_url == value


def test_luu_thuoc_tinh_mac_dinh_doc_os_environ(found, env_file, monkeypatch):
    monkeypatch.setenv("GSC_SITE_URL", "")
    assert save_property(DOMAIN, found, env_file=env_file).overridden
    monkeypatch.delenv("GSC_SITE_URL")
    assert not save_property(DOMAIN, found, env_file=env_file).overridden


# ================================================================ không nhập thứ không cần


MODULE_TREE = ast.parse(Path(refresh_module.__file__).read_text(encoding="utf-8"))
FORBIDDEN_MODULES = (
    "streamlit",
    "app",
    "seo_app.ai",
    "seo_app.google.sheets",
    "seo_app.plan",
    "anthropic",
    "openai",
    "google.genai",
    "requests",
)


def test_module_khong_nhap_giao_dien_ai_sheets():
    # LC-T120-13, -21: từ khóa không đi vào AI hay Google Sheets; lõi không có giao diện.
    names = set()
    for node in ast.walk(MODULE_TREE):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    bad = [
        name
        for name in names
        for item in FORBIDDEN_MODULES
        if name == item or name.startswith(item + ".")
    ]
    assert bad == []


def test_nap_module_khong_goi_ham_nao_ngoai_hang_so():
    # LC-T120-21: nạp module chỉ định nghĩa hằng, lớp, hàm (không client, không mạng, không file).
    allowed = {"timedelta", "threading.Lock"}
    calls = []
    for node in MODULE_TREE.body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                calls.append(ast.unparse(inner.func))
    assert set(calls) <= allowed

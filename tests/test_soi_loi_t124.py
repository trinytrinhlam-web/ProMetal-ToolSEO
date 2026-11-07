"""T-124 Soi Lỗi (đầy đủ): lấy số liệu Search Console (``seo_app/tracking/refresh.py``), lưu
thuộc tính (``env_file``), một hàm chuẩn hóa ``WORDPRESS_URL`` dùng chung (``site_base`` ở
``seo_app.wordpress.client``).

Bổ sung cho test của Thợ Máy (``tests/test_tracking_refresh.py``, ``tests/test_env_file_gsc.py``,
``tests/test_t124_chuan_hoa_va_cache.py``), theo trọng tâm Chỉ Huy B giao:

- Hàm chuẩn hóa dùng chung không nới lọc: ba nơi so địa chỉ trang (client T-121, cache T-122, lõi
  T-123) nhận đúng cùng một tập địa chỉ, và chỉ địa chỉ của website, với mọi cách viết
  ``WORDPRESS_URL``. Link bài viết hoa tên máy (LC-T123-1) không mở cửa cho địa chỉ ngoài website.
- Mô phỏng nhiều tháng bấm «Lấy số liệu mới» với Search Console giả sát thật (ngày chốt chỉ tiến,
  độ trễ 1–5 ngày, đồng hồ máy lùi, bỏ lâu không mở, lỗi chèn): chia đoạn ≤ 31 ngày, ≤ 20 lệnh,
  không bao giờ chốt nhầm số tạm, cache không từ chối đoạn nào, chặn bấm lại không gửi lệnh.
- Ghép thật client T-121 → cache T-122: dòng client nhận thì cache phải ghi được (SL-T124-1).

Lỗi mới để ``xfail(strict=True)`` kèm mã SL-T124-n. Tham số lớn luôn có ``ids=`` ngắn. Không gọi
mạng (Google giả ``tests/fake_google.py``, client giả trong file); mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import json
import os
import random
import types
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pytest
from fake_google import FakeGoogle, key_info
from fake_google import new_private_key as make_private_key
from test_tracking_refresh import (
    DOMAIN,
    NOW,
    QUERY_URL,
    WORDPRESS,
    Factory,
    FakeWordPress,
    Search,
    post,
    row,
    run,
    scope,
)

from seo_app import env_file
from seo_app.config import Settings
from seo_app.google.search_console import (
    SearchConsoleClient,
    SearchConsoleError,
    SearchResult,
    SearchRow,
    SiteEntry,
    site_prefix,
)
from seo_app.google.service_account import SEARCH_CONSOLE_SCOPE, load_service_account
from seo_app.storage import search_cache
from seo_app.storage.search_cache import MSG_BAD_DATA, MSG_BAD_RANGE, CacheScope, SearchCacheStore
from seo_app.storage.site_index import SiteIndexStore
from seo_app.tracking import match
from seo_app.tracking import refresh as rf
from seo_app.wordpress.client import (
    MAX_STATUS_LOOKUP,
    PostState,
    PublishedItem,
    WordPressError,
    is_site_link,
    site_base,
)

PT = ZoneInfo("America/Los_Angeles")
SURROGATE = chr(0xD800)  # surrogate lẻ: json.loads trả được từ chuỗi thoát trong câu trả lời
BACKSLASH = chr(0x5C)


# ---------------------------------------------------------------- fixture (như test Thợ Máy)


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
def key_file(tmp_path: Path, private_key) -> Path:
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    path = folder / "khoa-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    return path


@pytest.fixture
def fake() -> FakeGoogle:
    return FakeGoogle()


@pytest.fixture
def google(fake: FakeGoogle) -> Search:
    return Search(fake)


@pytest.fixture
def factory(key_file: Path, project: Path, fake: FakeGoogle) -> Factory:
    account = load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)
    return Factory(account, fake)


@pytest.fixture
def settings(key_file: Path) -> Settings:
    return Settings(
        wordpress_url=WORDPRESS, gsc_site_url=DOMAIN, google_service_account_file=key_file
    )


@pytest.fixture
def store(project: Path) -> SearchCacheStore:
    return SearchCacheStore(path=project / "data" / "search_cache.sqlite")


# ======================================= hàm chuẩn hóa dùng chung không nới lọc (trọng tâm 3)

# Cách viết WORDPRESS_URL mà client WordPress và client Search Console đều nhận (config đã bỏ «/»
# cuối): chữ hoa ở scheme, tên máy; cổng 443 viết ra; website ở thư mục con.
SPELLINGS = [
    "https://suachuacuasat.com",
    "https://Suachuacuasat.com",
    "HTTPS://SUACHUACUASAT.COM",
    "https://suachuacuasat.com:443",
    "https://suachuacuasat.com/blog",
    "https://SuaChuaCuaSat.com:443/Blog",
]
HOST = "suachuacuasat.com"
SITE_PAGES = [  # trang của website ở gốc tên miền
    f"https://{HOST}/",
    f"https://{HOST}/a/",
    f"https://{HOST}/blog/a/",
    f"https://{HOST}/Blog/a/",
    f"https://{HOST}/blog",
    f"https://{HOST}/blog2/a/",
    f"https://{HOST}/a/#bang-gia",
    f"https://{HOST}/?s=cua",
    f"https://{HOST}/s%E1%BB%ADa-c%E1%BB%ADa/",
]
OFF_SITE = [  # ngoài website: ba nơi đều phải loại, với mọi cách viết WORDPRESS_URL
    f"https://www.staging-m.{HOST}/a/",
    f"https://staging.{HOST}/a/",
    f"https://www.{HOST}/a/",
    f"http://{HOST}/a/",
    f"HTTP://{HOST}/a/",
    f"https://{HOST}:8443/a/",
    f"https://{HOST}:80/a/",
    f"https://{HOST}:443/a/",  # Google không viết cổng: client T-121 cũng bỏ
    f"https://{HOST}:/a/",
    f"https://user@{HOST}/a/",
    "https://user:" + f"pw@{HOST}/a/",  # tách chuỗi: mật khẩu giả, detect-secrets khỏi báo
    f"https://{HOST}@evil.example/a/",
    f"https://evil.example@{HOST}/a/",
    f"https://evil{HOST}/a/",
    f"https://EVIL{HOST.upper()}/a/",
    f"https://{HOST}.evil.example/a/",
    f"https://{HOST}-evil.com/a/",
    "https://suachuacuasat.co/a/",
    "https://suachuacuas" + chr(0x0430) + "t.com/a/",  # chữ «а» Kirin
    f"https://{HOST}./a/",
    f"https://{HOST.upper()}/a/",  # Google luôn viết thường tên máy: client T-121 cũng bỏ
    f"https://{HOST}" + BACKSLASH + "@evil.example/a/",
    f"ftp://{HOST}/a/",
]
ODD_PAGES = [f"https://{HOST}/blog/../a/", f"https://{HOST}//evil.example/"]  # đường lạ, cùng máy


def cache_page(page: str, wordpress_url: str) -> str | None:
    return search_cache._page(page, CacheScope(DOMAIN, wordpress_url).base)


def client_page(page: str, wordpress_url: str) -> str | None:
    """Bộ lọc dòng Google của client T-121 (``SearchConsoleClient._page``), dựng như client thật."""
    me = types.SimpleNamespace(_prefix=site_prefix(wordpress_url), _wordpress_url=wordpress_url)
    return SearchConsoleClient._page(me, page)


def on_site(page: str, wordpress_url: str) -> bool:
    """Đúng ``https``, đúng tên máy, không cổng lạ, không tên người dùng, bắt đầu bằng tiền tố."""
    base = site_base(wordpress_url)
    want, got = urlsplit(base), urlsplit(page)
    return (
        page.startswith(base + "/")
        and got.scheme == "https"
        and got.hostname == want.hostname
        and got.port == want.port
        and got.username is None
        and "@" not in got.netloc
    )


def test_three_filters_take_the_same_pages_and_only_on_site_pages():
    """Ba nơi so địa chỉ trang dùng chung một hàm: client T-121 và cache T-122 nhận đúng cùng chuỗi,
    lõi T-123 nhận cùng tập; trang được nhận luôn là trang của website. So chéo mở rộng ở báo cáo:
    15.015 địa chỉ × 41 cách viết, so cây trước T-124 với cây T-124."""
    problems = []
    for wp in SPELLINGS:
        assert site_prefix(wp) == site_base(wp) + "/" == match.site_base(wp) + "/", wp
        for page in [*SITE_PAGES, *OFF_SITE, *ODD_PAGES]:
            cached, client = cache_page(page, wp), client_page(page, wp)
            if client != cached:
                problems.append(("cache khác client", wp, page, cached, client))
            if (match.page_key(page, wp) is not None) != (cached is not None):
                problems.append(("lõi khác cache", wp, page))
            if cached is not None and not on_site(cached, wp):
                problems.append(("nhận địa chỉ ngoài website", wp, page))
            if page in OFF_SITE and cached is not None:
                problems.append(("nhận địa chỉ phải loại", wp, page))
        if urlsplit(site_base(wp)).path == "":  # website ở gốc tên miền: mọi trang thật đều nhận
            problems += [("bỏ trang thật", wp, p) for p in SITE_PAGES if cache_page(p, wp) is None]
    assert problems == []


@pytest.mark.parametrize(
    "link",
    [
        f"https://{HOST.upper()}/a/",
        f"HTTPS://{HOST}/a/",
        f"https://{HOST}:443/a/",
        "Https://SuaChuaCuaSat.Com:443/a/",
    ],
    ids=["ten-may-hoa", "scheme-hoa", "cong-443", "tron"],
)
def test_lc_t123_1_same_site_link_spellings_are_matched(link):
    """LC-T123-1: link bài viết hoa tên máy, cổng 443 vẫn là bài của website (nhận số liệu)."""
    item = PublishedItem(id=7, type="post", slug="a", link=link, title="Bài 7")
    tracking = match.build_tracking(WORDPRESS, [item], [])
    assert tracking.skipped_items == 0 and str(tracking.pages[0].key) == "/a"


@pytest.mark.parametrize(
    "link",
    [
        f"https://WWW.{HOST.upper()}/a/",
        f"https://www.staging-m.{HOST}/a/",
        f"http://{HOST.upper()}/a/",
        f"https://{HOST.upper()}:8443/a/",
        f"https://EVIL{HOST.upper()}/a/",
        f"https://{HOST.upper()}.EVIL.EXAMPLE/a/",
        "https://SUACHUACUAS" + chr(0x0410) + "T.COM/a/",  # chữ «А» Kirin viết hoa
        f"https://user@{HOST.upper()}/a/",  # tên người dùng: site_link sẽ bỏ phần này nếu chạy
        "https://user:" + f"pw@{HOST}/a/",  # tách chuỗi: mật khẩu giả, detect-secrets khỏi báo
    ],
    ids=[
        "www",
        "staging",
        "http",
        "cong-khac",
        "giong",
        "ten-mien-con",
        "kirin",
        "user",
        "user-pw",
    ],
)
def test_lc_t123_1_case_fix_does_not_admit_other_sites(link):
    """Viết thường tên máy chỉ sau ``is_site_link``: link website khác vẫn bị bỏ, dù viết hoa."""
    try:
        item = PublishedItem(id=7, type="post", slug="a", link=link, title="Bài 7")
    except ValueError:
        return  # client WordPress đã không nhận link này
    assert not is_site_link(link, WORDPRESS)
    assert match.build_tracking(WORDPRESS, [item], []).skipped_items == 1


# ============================================= mô phỏng nhiều tháng bấm «Lấy số liệu mới»


class _World:
    """Search Console giả sát thật: ngày chốt chỉ tiến lên; số tạm là 0, số chốt theo ngày."""

    def __init__(self) -> None:
        self.real_today = date(2026, 11, 3)
        self.machine_today = self.real_today
        self.first_inc = self.real_today - timedelta(days=2)
        self.newest_meta = "ok"
        self.fail_at: set[int] = set()

    def advance(self, days: int, lag: int) -> None:
        self.real_today += timedelta(days=days)
        self.machine_today = self.real_today
        self.first_inc = max(self.first_inc, self.real_today - timedelta(days=lag - 1))

    def value(self, day: date) -> int:
        return 0 if day >= self.first_inc else 1 + day.toordinal() % 5


class _SimClient:
    """Client giả (đúng các lệnh ``refresh`` dùng): trần 20 lệnh, lỗi chèn theo thứ tự lệnh."""

    def __init__(self, world: _World, log: list) -> None:
        self.world = world
        self.request_count = 0
        self.site = None
        self.log = log

    def _tick(self) -> None:
        if self.request_count >= 20:
            raise SearchConsoleError("Đã gửi đủ 20 lệnh")
        self.request_count += 1
        if self.request_count in self.world.fail_at:
            raise SearchConsoleError("Máy chủ Search Console đang lỗi (mã 503).")

    def fetch_day_page(self, start: date, end: date) -> SearchResult:
        self._tick()
        self.log.append(("day", start, end))
        page = WORDPRESS + "/a/"
        days = [start + timedelta(days=n) for n in range((end - start).days + 1)]
        rows = tuple(
            SearchRow(
                clicks=self.world.value(day), impressions=10, position=2.0, day=day, page=page
            )
            for day in days
        )
        first = self.world.first_inc
        if first > end:
            return SearchResult(rows, 0, False, None, "missing")
        if end >= self.world.machine_today and self.world.newest_meta != "ok":
            return SearchResult(rows, 0, False, None, self.world.newest_meta)
        return SearchResult(rows, 0, False, max(first, start), "ok")

    def fetch_page_query(self, start: date, end: date) -> SearchResult:
        self._tick()
        self.log.append(("query", start, end))
        found = SearchRow(1, 10, 2.0, page=WORDPRESS + "/a/", query="cửa sắt")
        return SearchResult((found,), 0, False)


def _client_factory(world: _World, log: list):
    return lambda _settings, **_options: _SimClient(world, log)


@pytest.mark.parametrize("seed", [3, 17, 29], ids=["h3", "h17", "h29"])
def test_many_months_of_clicks_keep_every_invariant(project, seed):
    """Mỗi lần bấm: đoạn ≤ 31 ngày trong 16 tháng, ≤ 20 lệnh; không chèn lỗi thì DONE hay RECENT,
    cache không từ chối đoạn nào; RECENT không gửi lệnh; ngày «đã chốt» trong cache luôn đúng số
    thật (không chốt nhầm số tạm, kể cả khi thiếu metadata); DONE thì phần đã lấy tới hôm nay."""
    rng = random.Random(seed)
    world = _World()
    settings = Settings(wordpress_url=WORDPRESS, gsc_site_url=DOMAIN)
    store = SearchCacheStore(path=project / "data" / "search_cache.sqlite")
    problems: list[str] = []
    for step in range(30):
        jump = rng.choice(["same", "minutes", "hours", "day", "day", "days", "long", "back"])
        lag = rng.choice([1, 2, 3, 3, 3, 4, 5])
        days = {"day": 1, "days": rng.randint(2, 40)}.get(jump, 0)
        if jump == "long" and rng.random() < 0.25:
            days = rng.randint(400, 600)
        world.advance(days, lag)
        if jump == "back":
            world.machine_today = world.real_today - timedelta(days=rng.randint(1, 6))
        true_lag = (world.real_today - world.first_inc).days + 1
        world.newest_meta = rng.choice(["ok"] * 6 + ["missing", "bad"]) if true_lag <= 3 else "ok"
        world.fail_at = {rng.randint(1, 18)} if rng.random() < 0.15 else set()
        minute = rng.randint(0, 50) if jump in ("same", "minutes") else rng.randint(0, 600)
        start_of_day = datetime.combine(world.machine_today, datetime.min.time(), PT)
        now = start_of_day + timedelta(hours=9, minutes=minute)
        log: list = []
        report = rf.refresh(settings, store, client_factory=_client_factory(world, log), now=now)
        today = world.machine_today
        tag = f"bước {step} ({jump}, trễ {true_lag}, {world.newest_meta})"
        oldest = today - timedelta(days=485)
        for kind, start, end in log:
            if kind == "day" and not (oldest <= start <= end <= today and (end - start).days < 31):
                problems.append(f"{tag}: đoạn {start}..{end}")
        text = " ".join((report.message, *report.notes))
        if len(log) > 20 or MSG_BAD_RANGE in text or MSG_BAD_DATA in text:
            problems.append(f"{tag}: {len(log)} lệnh, {report.outcome}: {text[:100]}")
        if not world.fail_at and report.outcome not in (rf.Outcome.DONE, rf.Outcome.RECENT):
            problems.append(f"{tag}: không chèn lỗi mà {report.outcome}")
        if report.outcome is rf.Outcome.RECENT and log:
            problems.append(f"{tag}: RECENT mà gửi {len(log)} lệnh")
        cache = store.load(CacheScope(DOMAIN, WORDPRESS))
        if cache is None:
            continue
        if any(day.final and day.clicks != world.value(day.day) for day in cache.days):
            problems.append(f"{tag}: có ngày «đã chốt» mang số tạm")
        if report.outcome is rf.Outcome.DONE and cache.covered_end != today:
            problems.append(f"{tag}: DONE mà phần đã lấy tới {cache.covered_end}")
    assert problems == []


# ===================== ghép thật client T-121 → cache T-122: dòng lạ không làm hỏng lần lấy


def test_google_row_with_lone_surrogate_is_dropped_and_counted(
    settings, store, factory, google, fake
):
    """Dòng Google có surrogate lẻ ở địa chỉ trang (cache không ghi được chữ này, SL-T122-3): client
    bỏ và đếm (T-121 lượt 2), lần lấy đầu vẫn xong, cache không có chữ đó (GN-3 Soi Lỗi T-122)."""
    bad_page = WORDPRESS + "/a" + SURROGATE + "/"

    def with_bad_row(request):
        answer = google.query(request)
        body = json.loads(request.body)
        if isinstance(answer, dict) and body["dimensions"] == ["date", "page"]:
            answer["rows"].append(row([body["startDate"], bad_page]))
        return answer

    fake.on("POST", QUERY_URL, with_bad_row)
    report = run(settings, store, factory)
    assert report.outcome is rf.Outcome.DONE, (report.outcome, report.notes)
    assert rf.MSG_DROPPED.format(count="16") in report.notes  # một dòng lạ mỗi đoạn, 16 đoạn
    cache = store.load(scope(settings))
    assert len(cache.days) == 486 and all(SURROGATE not in day.page for day in cache.days)


def test_control_without_bad_row_finishes_with_18_requests(settings, store, factory, google):
    """Đối chứng: cùng Google giả, không có dòng lạ, lần lấy đầu xong với 18 lệnh."""
    report = run(settings, store, factory)
    dropped = rf.MSG_DROPPED.split("}", 1)[1]  # « dòng số liệu không đúng dạng bị bỏ.»
    assert report.outcome is rf.Outcome.DONE and report.requests == 18
    assert not any(dropped in note for note in report.notes)


# ================================================ lưu thuộc tính: hai lớp kiểm đều phải có mặt


@pytest.mark.parametrize(
    "value",
    ["https://a..b/", "sc-domain:-bad-.com", "sc-domain:a.b-", "https://.example.com/"],
    ids=["hai-cham", "nhan-gach", "gach-cuoi", "cham-dau"],
)
def test_forged_usable_entry_must_still_pass_parse_property(tmp_path, value):
    """Mục «dùng được» dựng tay (không qua client) với giá trị **qua** bộ kiểm chữ của ``.env``
    nhưng sai dạng tên miền: ``save_property`` phải chặn bằng ``parse_property`` (lớp thứ hai),
    ``.env`` không đổi. Ca của Thợ Máy chỉ dùng giá trị mà cả hai lớp cùng chặn."""
    assert env_file.GSC_SITE_URL_PATTERN.fullmatch(value)
    path = tmp_path / ".env"
    path.write_text("WORDPRESS_URL=https://suachuacuasat.com\n", encoding="utf-8")
    forged = rf.PropertyList((SiteEntry(value, "siteRestrictedUser", "domain", True),))
    result = rf.save_property(value, forged, env_file=path, environ={})
    assert not result.ok and value not in result.message
    assert path.read_text(encoding="utf-8") == "WORDPRESS_URL=https://suachuacuasat.com\n"


# =============================== ngày đăng: hỏi tối đa 1.000 bài mỗi lần, lần sau hỏi tiếp


class _LimitedWordPress(FakeWordPress):
    """WordPress giả giữ đúng giới hạn của client thật: ``post_statuses`` quá 1.000 mã thì lỗi."""

    def post_statuses(self, post_ids):
        ids = list(post_ids)
        if len(ids) > MAX_STATUS_LOOKUP:
            raise WordPressError("Quá nhiều mã bài trong một lần hỏi.")
        return super().post_statuses(ids)


def test_more_than_1000_quiet_posts_are_asked_in_batches(
    settings, store, factory, google, project, monkeypatch
):
    """Website nhiều bài chưa có lượt hiển thị (quá ``MAX_STATUS_LOOKUP``): mỗi lần bấm hỏi tối đa
    1.000 bài, lần bấm sau hỏi nốt; không lần nào hỏi quá giới hạn của client WordPress."""
    count = MAX_STATUS_LOOKUP + 50
    items = [post(n, f"{WORDPRESS}/bai-so-{n}/") for n in range(1, count + 1)]
    states = {n: PostState(n, "publish", "2026-01-05T02:00:00") for n in range(1, count + 1)}
    wordpress = _LimitedWordPress(items=items, states=states)
    index = SiteIndexStore(path=project / "data" / "site_index.sqlite")
    monkeypatch.setattr(index, "_now", lambda: NOW)
    first = run(settings, store, factory, site_index=index, wordpress=wordpress)
    again = run(
        settings, store, factory, site_index=index, wordpress=wordpress, now=NOW + timedelta(days=1)
    )
    assert rf.MSG_POST_DATES_FAILED not in (*first.notes, *again.notes)
    assert [len(ids) for ids in wordpress.asked] == [MAX_STATUS_LOOKUP, 50]
    assert len(store.load(scope(settings)).post_dates) == count

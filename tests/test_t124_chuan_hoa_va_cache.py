"""T-124 (Thợ Máy): một hàm chuẩn hóa ``WORDPRESS_URL``, một luật đường con, và các điều kiện Lá
Chắn chuyển sang phiếu này.

- Gom ``site_base`` của cache (T-122) và của lõi theo dõi (T-123) về ``seo_app.wordpress.client``;
  ``site_prefix`` của client Search Console (T-121) dùng cùng hàm và cùng luật đường con
  ``site_path_ok`` với cửa vào client WordPress (Lá Chắn T-121 ghi nhận 1, điều kiện B.2). Bảng ca
  chung cho cả ba nơi gọi cũ.
- LC-T123-1: link bài WordPress viết hoa tên máy vẫn nhận số liệu.
- LC-T122-1: file cache sửa tay (UTF-8 hỏng trong ``sqlite_master``, «schema format» 5) bị bỏ, ghi
  lại được. LC-T122-2: ``clear()`` không để lọt ``PermissionError``.
- G1 Lá Chắn T-122: ``_parse_time`` kiểm năm cả sau khi đổi múi giờ. G2: 4 ca ghim. G2 Lá Chắn
  T-123: ``google_day`` kiểm năm trước khi đổi múi giờ.

Không gọi mạng; mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from seo_app.google import search_console
from seo_app.google.search_console import SearchConsoleError, site_prefix
from seo_app.storage import search_cache
from seo_app.storage.search_cache import (
    MSG_BAD_DATA,
    MSG_IO,
    CachedDay,
    CacheScope,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.tracking import match
from seo_app.tracking.match import build_tracking
from seo_app.tracking.periods import google_day
from seo_app.wordpress import client
from seo_app.wordpress.client import (
    PublishedItem,
    WordPressClient,
    WordPressError,
    site_base,
    site_link,
    site_path_ok,
)

SITE = "https://suachuacuasat.com"
SCOPE = CacheScope("sc-domain:suachuacuasat.com", SITE)
TODAY = date(2026, 11, 3)
NOW = datetime(2026, 11, 3, 15, 0, tzinfo=timezone(timedelta(hours=7)))
OCT = (date(2026, 10, 4), date(2026, 10, 31))
MINUS_23 = timezone(timedelta(hours=-23))


# ================================================================ một hàm, bảng ca chung

# Bảng của T-122 lượt 2 (``SITE_BASE_CASES``) và T-123 lượt 2, thêm vài ca biên. Cột cuối: tiền tố
# của ``site_prefix`` (T-121) khi địa chỉ dùng được để lấy số liệu, ``None`` khi bị từ chối.
CASES = {
    "hoa-dau": ("https://Suachuacuasat.com", SITE, SITE + "/"),
    "hoa-het": ("HTTPS://SUACHUACUASAT.COM/", SITE, SITE + "/"),
    "cong-443": ("https://suachuacuasat.com:443", SITE, SITE + "/"),
    "duong-dan-hoa": (
        "https://Example.com/Blog/",
        "https://example.com/Blog",
        "https://example.com/Blog/",
    ),
    "cong-khac": ("https://example.com:8443/", "https://example.com:8443", None),
    "rong": ("", "", None),
    "chu-la": ("khong-phai-dia-chi", "khong-phai-dia-chi", None),
    "nhieu-gach-cuoi": ("https://suachuacuasat.com///", SITE, SITE + "/"),
    "duong-con": ("https://suachuacuasat.com/blog", SITE + "/blog", SITE + "/blog/"),
    "duong-con-443": ("https://SuaChuaCuaSat.com:443/Blog_2/", SITE + "/Blog_2", SITE + "/Blog_2/"),
    "duong-con-cham": ("https://suachuacuasat.com/b.log", SITE + "/b.log", None),
    "http": ("http://SuaChuaCuaSat.com", "http://suachuacuasat.com", None),
}


@pytest.mark.parametrize(("url", "base", "prefix"), list(CASES.values()), ids=list(CASES))
def test_mot_ham_cho_ca_ba_noi_goi_cu(url, base, prefix):
    assert site_base(url) == base
    assert match.site_base is site_base  # lõi theo dõi T-123
    assert search_cache.site_base is site_base  # cache T-122
    assert CacheScope(SCOPE.site_url, url).base == base
    if prefix is None:
        with pytest.raises(SearchConsoleError):
            site_prefix(url)
    else:
        assert site_prefix(url) == prefix == base + "/"  # client Search Console T-121


def test_khong_con_ban_chuan_hoa_rieng():
    for module in (search_cache, match, search_console):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "def site_base" not in source, module.__name__
    assert "_PATH = re.compile" not in Path(search_console.__file__).read_text(encoding="utf-8")


# ================================================================ một luật đường con

PATHS = [
    "",
    "/blog",
    "/Blog_2/a-b~c",
    "/a/b/c",
    "/b.log",
    "/..",
    "/.",
    "/blog/../x",
    "/index.php",
    "/wp-json",
    "/a/WP-JSON",
    "/wp-admin",
    "/code-snippets",
    "/Prometal-x",
    "/a%20b",
    "/a b",
    "//x",
    "/a//b",
    "/ü",
    "/a;b",
    "/a:b",
    "/a@b",
    "/a+b",
    "/a(b)",
]


@pytest.mark.parametrize("path", PATHS, ids=[f"p{n:02d}" for n in range(len(PATHS))])
def test_mot_luat_duong_con_cho_wordpress_va_search_console(path):
    url = "https://example.com" + path
    expected = site_path_ok(path)
    try:
        WordPressClient(url, "bien-tap-vien", "abcd efgh ijkl mnop")
        wordpress_ok = True
    except WordPressError:
        wordpress_ok = False
    try:
        site_prefix(url)
        console_ok = True
    except SearchConsoleError:
        console_ok = False
    assert wordpress_ok is expected
    assert console_ok is expected


@pytest.mark.parametrize(
    ("path", "ok"),
    [
        ("", True),
        ("/blog", True),
        ("/Blog_2/a-b~c", True),
        ("/b.log", False),
        ("/blog/", False),  # nơi gọi bỏ «/» cuối trước khi kiểm
        ("/WP-Admin", False),
        ("blog", False),
        (None, False),
        (b"/blog", False),
    ],
    ids=[
        "rong",
        "blog",
        "ky-tu-cho-phep",
        "cham",
        "gach-cuoi",
        "tu-cam-hoa",
        "thieu-gach",
        "none",
        "bytes",
    ],
)
def test_luat_duong_con(path, ok):
    assert site_path_ok(path) is ok


def test_luat_duong_con_dung_bieu_thuc_cua_client_wordpress():
    assert client._SITE_PATH.pattern == r"(?:/[A-Za-z0-9_~-]+)*"
    assert client._SITE_PATH_FORBIDDEN == ("wp-json", "code-snippets", "prometal", "wp-admin")


# ================================================================ site_link, LC-T123-1


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        ("https://SuaChuaCuaSat.com/Bai-1/", SITE + "/Bai-1/"),
        ("HTTPS://suachuacuasat.com:443/a/?X=1#Y", SITE + "/a/?X=1#Y"),
        ("https://SuaChuaCuaSat.com:8443/a", "https://suachuacuasat.com:8443/a"),
        ("https://suachuacuasat.com", SITE),
        ("khong-phai-dia-chi", "khong-phai-dia-chi"),
        ("https://suachuacuasat.com:99999/a", "https://suachuacuasat.com:99999/a"),
    ],
    ids=["hoa", "hoa-443-query", "cong-khac", "goc", "chu-la", "cong-sai"],
)
def test_site_link_viet_thuong_scheme_va_ten_may(link, expected):
    assert site_link(link) == expected


def day(path: str, when: date = date(2026, 10, 20)) -> CachedDay:
    return CachedDay(when, SITE + path, 1, 10, 30.0, True)


def test_link_bai_viet_hoa_ten_may_van_nhan_so_lieu():
    # LC-T123-1: ô «Địa chỉ trang» của WordPress gõ chữ hoa thì link bài viết hoa tên máy.
    items = [PublishedItem(1, "post", "bai-1", "https://SuaChuaCuaSat.com/bai-1/", "Bài 1")]
    tracking = build_tracking(SITE, items, [day("/bai-1/")])
    assert tracking.skipped_items == 0
    assert tracking.others == ()
    (page,) = tracking.pages
    assert page.item.id == 1
    assert [(row.day, row.impressions) for row in page.days] == [(date(2026, 10, 20), 10)]


def test_link_hoa_cua_may_khac_van_bi_bo():
    items = [
        PublishedItem(1, "post", "bai-1", "https://Evil.com/bai-1/", "Bài 1"),
        PublishedItem(2, "post", "bai-2", "https://SuaChuaCuaSat.com:8443/bai-2/", "Bài 2"),
        PublishedItem(3, "post", "bai-3", "http://SuaChuaCuaSat.com/bai-3/", "Bài 3"),
    ]
    tracking = build_tracking(SITE, items, [day("/bai-1/")])
    assert tracking.pages == ()
    assert tracking.skipped_items == 3


def test_duong_dan_hoa_cua_link_giu_nguyen():
    # Chỉ scheme và tên máy viết thường; đường dẫn khác hoa thường là trang khác (Google cũng vậy).
    items = [PublishedItem(1, "post", "bai-1", "https://SuaChuaCuaSat.com/Bai-1/", "Bài 1")]
    tracking = build_tracking(SITE, items, [day("/bai-1/")])
    assert tracking.pages[0].days == ()
    assert [page.label for page in tracking.others] == ["/bai-1"]


# ================================================================ cache: LC-T122-1, -2, G1, G2


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def store(project: Path) -> SearchCacheStore:
    return SearchCacheStore(path=project / "data" / "search_cache.sqlite")


def save_october(store: SearchCacheStore) -> None:
    days = [day("/a/", OCT[0] + timedelta(days=n)) for n in range((OCT[1] - OCT[0]).days + 1)]
    store.save_days(
        SCOPE, days, start=OCT[0], end=OCT[1], first_provisional=None, fetched_at=NOW, today=TODAY
    )


def break_utf8_in_master(path: Path) -> None:
    """Byte UTF-8 hỏng trong câu tạo bảng (chú thích cuối câu), như sửa tay bằng công cụ khác."""
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA writable_schema = ON")
        conn.execute(
            "UPDATE sqlite_master SET sql = CAST(sql || X'202D2D20FF' AS TEXT) "
            "WHERE name = 'page_day'"
        )
        conn.commit()


def schema_format_5(path: Path) -> None:
    """Số «schema format» (byte 44–47 đầu file) thành 5: SQLite báo «unsupported file format»."""
    data = bytearray(path.read_bytes())
    data[44:48] = (5).to_bytes(4, "big")
    path.write_bytes(bytes(data))


@pytest.mark.parametrize(
    "damage", [break_utf8_in_master, schema_format_5], ids=["utf8", "schema-5"]
)
def test_file_sua_tay_bi_bo_va_ghi_lai_duoc(store, damage):
    save_october(store)
    damage(store.path)
    assert store.load(SCOPE) is None  # trước đây: SearchCacheError «không mở được» mãi
    assert store.reset_count == 1
    save_october(store)
    cache = store.load(SCOPE)
    assert (cache.covered_start, cache.covered_end) == OCT
    assert store.reset_count == 1


@pytest.mark.parametrize(
    "damage", [break_utf8_in_master, schema_format_5], ids=["utf8", "schema-5"]
)
def test_file_sua_tay_ghi_truoc_khi_doc(store, damage):
    save_october(store)
    damage(store.path)
    store.save_post_dates(SCOPE, {7: date(2026, 10, 1)})  # ghi trên file mới, không báo lỗi
    assert store.reset_count == 1
    assert dict(store.load(SCOPE).post_dates) == {7: date(2026, 10, 1)}


def test_file_dang_ban_van_bao_ban_khong_xoa(store):
    save_october(store)
    with closing(sqlite3.connect(store.path, isolation_level=None)) as other:
        other.execute("BEGIN EXCLUSIVE")
        try:
            with pytest.raises(SearchCacheError):
                store.load(SCOPE)
        finally:
            other.execute("ROLLBACK")
    assert store.reset_count == 0
    assert store.load(SCOPE) is not None


def test_clear_loi_quyen_khi_kiem_lien_ket(store, monkeypatch):
    # LC-T122-2: Windows từ chối lstat một tầng thư mục.
    def denied(*_args, **_kwargs):
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(search_cache, "dir_has_link", denied)
    with pytest.raises(SearchCacheError) as error:
        store.clear()
    assert str(error.value) == MSG_IO.format(detail="Access is denied")
    assert error.value.__cause__ is None


def test_clear_loi_xoa_file_cung_cau_co_dinh(store, monkeypatch):
    save_october(store)

    def locked(self, missing_ok=False):
        raise PermissionError(32, "The process cannot access the file")

    monkeypatch.setattr(Path, "unlink", locked)
    with pytest.raises(SearchCacheError, match="Không đọc, ghi được"):
        store.clear()


def set_info(path: Path, key: str, value: str) -> None:
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("UPDATE info SET value = ? WHERE key = ?", (value, key))
        conn.commit()


@pytest.mark.parametrize(
    "stamp",
    ["2000-01-01T00:00:00+23:59", "2200-12-31T23:00:00-10:00"],
    ids=["1999-gio-vn", "2201-gio-vn"],
)
def test_moc_lay_doi_mui_gio_ra_ngoai_khoang_nam_bi_bo(store, stamp):
    # G1: năm hợp lệ ở múi giờ ghi trong file nhưng ra ngoài khoảng khi đổi sang giờ Việt Nam.
    save_october(store)
    set_info(store.path, "fetched_at", stamp)
    assert store.load(SCOPE) is None
    assert store.reset_count == 1


def test_moc_lay_hop_le_doi_mui_gio_van_doc_duoc(store):
    save_october(store)
    set_info(store.path, "fetched_at", "2026-11-03T08:00:00+00:00")
    assert store.load(SCOPE).fetched_at == datetime(2026, 11, 3, 15, 0, tzinfo=NOW.tzinfo)


def test_ghim_trigger_cai_ngay_sau_prepare(store, monkeypatch):
    # G2 (N04): file bị thêm trigger giữa lần kiểm ở _prepare và giao dịch đọc: bị bắt, bỏ file.
    save_october(store)
    original = SearchCacheStore._prepare

    def prepare_then_add_trigger(self):
        original(self)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                "CREATE TRIGGER chen AFTER INSERT ON post_date BEGIN DELETE FROM page_day; END"
            )
            conn.commit()

    monkeypatch.setattr(SearchCacheStore, "_prepare", prepare_then_add_trigger)
    assert store.load(SCOPE) is None
    assert store.reset_count == 1
    assert not store.path.exists()


def test_ghim_save_days_hom_nay_nam_1(store):
    # G2 (N17): năm kiểm trước mọi phép trừ ngày; không lọt OverflowError.
    with pytest.raises(SearchCacheError) as error:
        store.save_days(
            SCOPE,
            [],
            start=OCT[0],
            end=OCT[1],
            first_provisional=None,
            fetched_at=NOW,
            today=date(1, 1, 1),
        )
    assert str(error.value) == MSG_BAD_DATA
    assert error.value.__cause__ is None


def test_ghim_save_post_dates_nam_1_giu_cache_cu(store):
    # G2 (N17): ngày năm 1 không được ghi (nếu ghi, lần đọc sau bỏ cả cache).
    save_october(store)
    before = store.load(SCOPE)
    with pytest.raises(SearchCacheError, match="không đúng dạng"):
        store.save_post_dates(SCOPE, {7: date(1, 1, 1)})
    after = store.load(SCOPE)
    assert after == before
    assert store.reset_count == 0


def test_ghim_save_queries_moc_1999_mui_tru_23(store):
    # G2 (N14): năm kiểm TRƯỚC khi đổi múi giờ: 1999-12-31T23:00 −23:00 là năm 2000 giờ Việt Nam
    # nhưng vẫn bị chặn vì năm ghi trong mốc là 1999.
    moment = datetime(1999, 12, 31, 23, 0, tzinfo=MINUS_23)
    assert moment.astimezone(NOW.tzinfo).year == 2000
    with pytest.raises(SearchCacheError) as error:
        store.save_queries(SCOPE, [], start=OCT[0], end=OCT[1], fetched_at=moment, truncated=False)
    assert str(error.value) == MSG_BAD_DATA


def test_ghim_google_day_kiem_nam_truoc_khi_doi_mui_gio():
    # G2 Lá Chắn T-123 (M12a): đổi sang giờ PT là 01/01/2000 (hợp lệ) nhưng năm ghi là 1999.
    moment = datetime(1999, 12, 31, 23, 0, tzinfo=MINUS_23)
    assert google_day(moment) is None


def test_cung_website_viet_khac_la_mot_cache(store):
    save_october(store)
    for spelled in ("HTTPS://SuaChuaCuaSat.com:443/", "https://suachuacuasat.com///"):
        cache = store.load(CacheScope(SCOPE.site_url, spelled))
        assert cache is not None and cache.covered_end == OCT[1]
    assert store.reset_count == 0
    assert urlsplit(SITE).hostname == "suachuacuasat.com"

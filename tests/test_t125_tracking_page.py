"""T-125 (Họa Sĩ): trang «📈 Theo dõi» (``app/views/tracking.py``; thiết kế T-120 mục 1.5–1.7, 4.1,
4.4; LC-T120-11, -13, -14, -19, -20, -21; Lá Chắn T-123 mục 7, T-124 B.1).

- Mở trang, đổi khoảng ngày, chọn bài **không gọi mạng**: client Search Console, WordPress giả
  báo lỗi ngay nếu bị tạo hay gọi; bộ chặn mạng của ``conftest.py`` vẫn bật (LC-T120-21).
- Số liệu đọc từ bản lưu tạm (cache T-122, danh sách bài, kế hoạch) dựng sẵn trong thư mục tạm;
  mở trang khi chưa có file không tạo file nào.
- Chữ từ Google, WordPress hiện chữ thuần: ô bảng qua ``safe_rows``, ô chọn, ``escape_markdown``;
  biểu đồ chỉ có ngày và số, khuôn cố định (LC-T120-11, -19, -20).
- Nút «Lấy số liệu mới» chỉ gọi khi bấm: Google giả của ``test_tracking_refresh``; tab khác đang
  lấy thì báo bận; lỗi ra câu cố định. «Xóa bản lưu tạm» hỏi lại rồi mới xóa.
"""

from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import pytest
import test_app_pages as pages
import test_t101_plan_page as plan_page
import test_tracking_refresh as trk
from fake_google import SHEET_ID, FakeGoogle, key_info
from fake_google import new_private_key as make_private_key
from fake_plan_sheet import HEADER
from streamlit.testing.v1 import AppTest

from seo_app.google.search_console import SearchConsoleClient, SearchConsoleError
from seo_app.google.service_account import SEARCH_CONSOLE_SCOPE, load_service_account
from seo_app.storage import plan_cache, search_cache, site_index
from seo_app.storage.search_cache import (
    CachedDay,
    CachedQuery,
    CacheScope,
    SearchCacheError,
    SearchCacheStore,
)
from seo_app.storage.site_index import SiteIndex, SiteIndexStore
from seo_app.text import escape_markdown
from seo_app.tracking import refresh as refresh_module
from seo_app.tracking.flags import LABELS
from seo_app.tracking.keywords import HIDDEN_QUERIES_NOTE
from seo_app.tracking.model import FlagKind
from seo_app.tracking.periods import Period, google_today, last_days, previous_period
from seo_app.wordpress.client import PublishedItem, WordPressClient

env = pages.env

WORDPRESS = "https://suachuacuasat.com"
DOMAIN = "sc-domain:suachuacuasat.com"
DAYS = 120  # 31 + 31 + 31 + 27: đoạn cuối chứa cả 2 ngày tạm
PROVISIONAL = 2
EVIL = "https://evil.example"
HOSTILE_TITLE = f"**Đậm** [bấm]({EVIL}) <b>x</b>"
FORMULA_QUERY = f'=HYPERLINK("{EVIL}")'
MARKDOWN_QUERY = f"**đậm** [x]({EVIL})"
SEARCH_PAGE = WORDPRESS + "/?s=%5Bx%5D(" + EVIL + ")"
RLO_PAGE = WORDPRESS + "/%E2%80%AEexe.txt/"
OTHER_KEYWORDS = 55  # cộng 3 nhóm ở trên (hai cách gõ gộp một): 58 nhóm > 50 dòng đầu


def link(path: str) -> str:
    return WORDPRESS + path


POSTS = (
    PublishedItem(11, "post", "sua-cua-keo", link("/sua-cua-keo/"), "Sửa cửa kéo bị kẹt ray"),
    PublishedItem(12, "post", "cong-sat", link("/cong-sat-xe-canh/"), "Cổng sắt bị xệ cánh"),
    PublishedItem(
        13, "page", "sua-cua-keo-tphcm", link("/sua-cua-keo-tphcm/"), "Sửa cửa kéo TP.HCM"
    ),
    PublishedItem(14, "post", "lan-can", link("/lan-can-cau-thang/"), "Lan can cầu thang bị gỉ"),
    PublishedItem(15, "post", "bai-doc", link("/bai-doc/"), HOSTILE_TITLE),
    PublishedItem(
        16, "post", "bai-p", link("/?p=16"), "Bài có địa chỉ ?p="
    ),  # không dựng được khóa
)
PLAN_VALUES = [
    HEADER,
    plan_page.row("B-012", "sửa cửa kéo bị kẹt", status="Đã đăng", **{"Mã bài WordPress": 11}),
    plan_page.row("B-007", "cổng sắt bị xệ cánh", status="Đã đăng", **{"Mã bài WordPress": 12}),
    plan_page.row("B-020", "cổng lùa kẹt ray", status="Đã đăng", **{"Mã bài WordPress": 99}),
]


@dataclass(frozen=True)
class Seeded:
    today: date
    end: date  # E: ngày chốt cuối
    current: Period  # 28 ngày tới E
    previous: Period


# ---------------------------------------------------------------- fixture


@pytest.fixture(scope="module")
def private_key():
    return make_private_key()


@pytest.fixture(autouse=True)
def data_files(tmp_path, monkeypatch):
    """Mọi file lưu tạm trong thư mục tạm (không đụng ``data/`` thật)."""
    root = tmp_path / "du-an"
    (root / "data").mkdir(parents=True)
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", root)
    monkeypatch.setattr(search_cache, "DEFAULT_SEARCH_CACHE_FILE", root / "data" / "sc.sqlite")
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", root / "data" / "site.sqlite")
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", root / "data" / "plan.sqlite")
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
def configured(monkeypatch, key_file):
    """Đã khai báo website, thuộc tính Search Console, file khóa, Sheet kế hoạch."""
    monkeypatch.setenv("WORDPRESS_URL", WORDPRESS)
    monkeypatch.setenv("GSC_SITE_URL", DOMAIN)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    return key_file


class NetworkCalls:
    """Đếm lần tạo client, gọi lệnh rồi ném ``error``: mặc định ``AssertionError`` (trang lỗi
    ngay); ca đối chứng dùng ``SearchConsoleError`` để trang báo lỗi như thường."""

    def __init__(self, error: type[Exception] = AssertionError) -> None:
        self.count = 0
        self.error = error

    def __call__(self, *args, **kwargs):
        self.count += 1
        raise self.error("không được gọi Search Console, WordPress khi chỉ mở trang")


@pytest.fixture
def no_network(monkeypatch) -> NetworkCalls:
    """Giả client đếm lệnh (LC-T120-21): mọi đường tạo client Search Console và mọi lệnh đọc
    WordPress đều đếm rồi báo lỗi."""
    calls = NetworkCalls()
    monkeypatch.setattr(refresh_module, "_default_client", calls)
    monkeypatch.setattr(SearchConsoleClient, "from_settings", classmethod(calls))
    for name in ("list_published", "post_statuses", "check_connection"):
        monkeypatch.setattr(WordPressClient, name, calls)
    return calls


# ---------------------------------------------------------------- dữ liệu mẫu


def day_rows(day: date, current: Period) -> list[tuple[str, int, int, float]]:
    """Số một ngày: (địa chỉ, click, lượt hiển thị, Σ vị trí × lượt hiển thị)."""
    recent = day >= current.start  # kỳ đang xem và các ngày tạm sau đó
    rows = [
        (link("/sua-cua-keo/"), 2, 40, 240.0),  # vị trí 6
        (link("/sua-cua-keo-tphcm/"), 1, 30, 90.0),  # vị trí 3
        (link("/bai-doc/"), 1, 10, 80.0),  # vị trí 8
        (link("/"), 5, 50, 75.0),  # trang chủ: «Trang khác»
        # Cổng sắt: kỳ trước vị trí 5, 1 click/ngày; kỳ này vị trí 14, không click (tụt hạng)
        (link("/cong-sat-xe-canh/"), 0, 15, 210.0)
        if recent
        else (link("/cong-sat-xe-canh/"), 1, 20, 100.0),
    ]
    if day == current.end:
        rows += [(SEARCH_PAGE, 0, 3, 9.0), (RLO_PAGE, 0, 2, 4.0)]
    return rows


def keyword_rows(current: Period, previous: Period) -> tuple[list[CachedQuery], list[CachedQuery]]:
    page = link("/sua-cua-keo/")
    now = [
        CachedQuery(current.start, current.end, page, "sửa cửa kéo bị kẹt", 20, 500, 3200.0),
        CachedQuery(current.start, current.end, page, "sua cua keo bi ket", 3, 100, 700.0),
        CachedQuery(current.start, current.end, page, FORMULA_QUERY, 10, 200, 1000.0),
        CachedQuery(current.start, current.end, page, MARKDOWN_QUERY, 9, 150, 900.0),
        *(
            CachedQuery(current.start, current.end, page, f"cửa kéo mẫu {n:02d}", 0, 5, 50.0)
            for n in range(OTHER_KEYWORDS)
        ),
    ]
    before = [
        CachedQuery(previous.start, previous.end, page, "sửa cửa kéo bị kẹt", 15, 400, 3000.0)
    ]
    return now, before


def seed(*, queries: bool = True, index: bool = True, plan: bool = True) -> Seeded:
    """Bản lưu tạm như sau một lần «Lấy số liệu mới»: 120 ngày, 2 ngày cuối là số tạm."""
    today = google_today()
    first_provisional = today - timedelta(days=PROVISIONAL - 1)
    end = first_provisional - timedelta(days=1)
    current = last_days(end, 28)
    previous = previous_period(current)
    store = SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE)
    scope = CacheScope(DOMAIN, WORDPRESS)
    now = datetime.now(UTC)
    chunk = today - timedelta(days=DAYS - 1)
    while chunk <= today:
        last = min(chunk + timedelta(days=30), today)
        rows = []
        day = chunk
        while day <= last:
            final = day < first_provisional
            rows += [CachedDay(day, *row, final) for row in day_rows(day, current)]
            day += timedelta(days=1)
        provisional = first_provisional if first_provisional <= last else None
        store.save_days(
            scope,
            rows,
            start=chunk,
            end=last,
            first_provisional=provisional,
            fetched_at=now,
            today=today,
        )
        chunk = last + timedelta(days=1)
    if queries:
        now_rows, before_rows = keyword_rows(current, previous)
        for period, rows in ((current, now_rows), (previous, before_rows)):
            store.save_queries(
                scope, rows, start=period.start, end=period.end, fetched_at=now, truncated=False
            )
    store.save_post_dates(
        scope,
        {14: end - timedelta(days=40), 12: end - timedelta(days=300)},
        keep=[item.id for item in POSTS],
    )
    if index:
        SiteIndexStore(path=site_index.DEFAULT_SITE_INDEX_FILE).save(
            SiteIndex(WORDPRESS, now, POSTS)
        )
    if plan:
        plan_cache.PlanCacheStore(path=plan_cache.DEFAULT_PLAN_CACHE_FILE).save(
            SHEET_ID, PLAN_VALUES, now
        )
    return Seeded(today, end, current, previous)


# ---------------------------------------------------------------- tiện ích AppTest


def open_tracking(project_root) -> AppTest:
    return pages.open_page(project_root, "tracking.py")


def run(target) -> AppTest:
    """Chạy lại trang (``target``: ``AppTest`` hay ô vừa đổi giá trị); không được có lỗi."""
    at = target.run()
    assert not at.exception, at.exception
    return at


def texts(at: AppTest, kind: str) -> list[str]:
    return [element.value for element in getattr(at, kind)]


def everything(at: AppTest) -> str:
    """Mọi chữ Markdown hiện ra (markdown, caption, info, warning, error, success)."""
    kinds = ("markdown", "caption", "info", "warning", "error", "success")
    return "\n".join(value for kind in kinds for value in texts(at, kind))


def table(at: AppTest, column: str):
    """Bảng đầu tiên có cột ``column`` (pandas DataFrame)."""
    for frame in at.dataframe:
        value = frame.value
        if column in value.columns:
            return value
    raise AssertionError(f"Không thấy bảng có cột {column!r}")


def metric(at: AppTest, label: str):
    return next(item for item in at.metric if item.proto.label == label)


def charts(at: AppTest):
    return at.get("vega_lite_chart")


# ================================================================ không gọi mạng (LC-T120-21)


def test_mo_trang_va_doi_moi_o_khong_goi_mang(project_root, configured, no_network):
    """Mở trang, đổi khoảng ngày, kỳ so sánh, lọc, chọn bài, xem cách gõ: 0 client, 0 lệnh."""
    seeded = seed()
    at = open_tracking(project_root)
    run(at.segmented_control(key="trk-range").set_value("7 ngày"))
    run(at.selectbox(key="trk-compare").set_value("Cùng kỳ năm trước"))
    run(at.segmented_control(key="trk-range").set_value("Tùy chọn"))
    run(at.date_input(key="trk-from").set_value(seeded.current.start))
    run(at.segmented_control(key="trk-range").set_value("28 ngày"))
    run(at.selectbox(key="trk-compare").set_value("Kỳ trước"))
    run(at.checkbox(key="trk-plan-only").check())
    run(at.selectbox(key="trk-flag").set_value(FlagKind.RANK_DROP.value))
    run(at.selectbox(key="trk-flag").set_value("all"))
    run(at.selectbox(key="trk-page").set_value(11))
    run(at.toggle(key="trk-variants").set_value(True))
    run(at.button(key="trk-more-keywords").click())
    assert no_network.count == 0


def test_doi_chung_bam_nut_thi_bo_dem_bat_duoc(project_root, configured, monkeypatch):
    """Đối chứng của các ca «0 lệnh»: cùng cách giả, bấm «Lấy số liệu mới» thì bộ đếm lên 1 (đường
    gọi mạng của nút đúng là đường bộ đếm canh)."""
    calls = NetworkCalls(SearchConsoleError)
    monkeypatch.setattr(refresh_module, "_default_client", calls)
    at = open_tracking(project_root)
    assert calls.count == 0
    run(at.button(key="trk-fetch").click())
    assert calls.count == 1
    assert any(escape_markdown(refresh_module.MSG_FAILED) in text for text in texts(at, "error"))


def test_mo_cai_dat_khong_goi_mang(project_root, configured, no_network):
    seed()
    at = pages.open_page(project_root, "settings.py")
    assert any(button.key == "gsc-find-btn" for button in at.button)
    assert no_network.count == 0


def test_chua_co_file_thi_mo_trang_khong_tao_file(project_root, configured, no_network, data_files):
    at = open_tracking(project_root)
    assert any("Chưa có số liệu" in text for text in texts(at, "info"))
    assert list((data_files / "data").iterdir()) == []
    assert no_network.count == 0


def test_chua_dang_nhap_thi_khong_mo_duoc_trang(project_root, configured, no_network):
    """LC-T120-14: trang theo dõi kiểm đăng nhập như mọi trang (qua ``app/main.py``)."""
    seed()
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    run(at)
    run(at.switch_page("views/tracking.py"))
    assert [title.value for title in at.title] == ["Đăng nhập"]
    assert not any(button.key == "trk-fetch" for button in at.button)
    assert not at.dataframe and not at.metric
    assert no_network.count == 0


def test_chua_chon_thuoc_tinh_thi_huong_dan_cai_dat_va_khoa_nut(project_root, no_network):
    at = open_tracking(project_root)
    assert any("Chưa chọn thuộc tính Search Console" in text for text in texts(at, "info"))
    assert at.button(key="trk-fetch").disabled
    assert no_network.count == 0


def test_trang_khong_nhap_ai_sheets_khong_html_khong_cache_tu_lam_moi(project_root):
    """LC-T120-11, -13, -21 (đọc mã): trang không nhập lớp AI, client Google Sheets; không
    ``unsafe_allow_html``, ``st.html``, cột link; không ``st.cache_data``, ``st.cache_resource``,
    ``st.fragment``, ``run_every``."""
    source = (project_root / "app" / "views" / "tracking.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    for banned in ("seo_app.ai", "seo_app.google.sheets", "anthropic", "openai", "google.genai"):
        assert not any(name and name.startswith(banned) for name in imported), banned
    used = set()  # chỉ mã thật (tham số, thuộc tính, tên), không xét chữ trong docstring
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg:
            used.add(node.arg)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
        elif isinstance(node, ast.Name):
            used.add(node.id)
    for banned in (
        "unsafe_allow_html",
        "html",
        "LinkColumn",
        "cache_data",
        "cache_resource",
        "fragment",
        "run_every",
    ):
        assert banned not in used, banned


# ================================================================ số liệu, bảng, nhãn


def test_moc_so_lieu_tong_website_va_so_ky_truoc(project_root, configured, no_network):
    seeded = seed()
    at = open_tracking(project_root)
    shown = everything(at)
    expected = f"Số liệu tới hết ngày {seeded.end:%d/%m/%Y} (ngày theo giờ Google)"
    assert escape_markdown(expected) in shown  # câu hiện qua escape_markdown
    assert "lấy lúc" in shown
    clicks = metric(at, "Lượt click")
    # Kỳ này: 56 + 28 + 28 + 140 = 252; kỳ trước thêm 28 click của bài Cổng sắt: 280
    assert clicks.value == "252"
    assert clicks.proto.delta == "-28 (-10%)"
    position = metric(at, "Vị trí trung bình")
    assert position.proto.delta.startswith("xuống")


def test_bang_tung_bai_nhan_ma_ke_hoach_va_so_kieu_viet_nam(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    frame = table(at, "Bài / trang")
    rows = {row["Bài / trang"]: row for row in frame.to_dict("records")}
    keo = rows["Sửa cửa kéo bị kẹt ray"]
    assert (keo["Mã KH"], keo["Click"], keo["Hiển thị"], keo["CTR"], keo["Vị trí"]) == (
        "B-012",
        "56",
        "1.120",
        "5,0%",
        "6,0",
    )
    cong = rows["Cổng sắt bị xệ cánh"]
    assert (
        LABELS[FlagKind.RANK_DROP] in cong["Nhãn"] and LABELS[FlagKind.LOST_CLICKS] in cong["Nhãn"]
    )
    assert cong["± vị trí"] == "xuống 9,0 bậc"
    assert rows["Sửa cửa kéo TP.HCM"]["Loại"] == "Trang"
    assert LABELS[FlagKind.NO_IMPRESSIONS] in rows["Lan can cầu thang bị gỉ"]["Nhãn"]
    assert list(frame["Bài / trang"])[0] == "Sửa cửa kéo bị kẹt ray"  # nhiều click nhất trước
    shown = everything(at)
    attention = "Cần chú ý: 1 bài tụt hạng · 1 bài mất click · 1 bài chưa có lượt hiển thị"
    assert escape_markdown(attention) in shown
    assert "Kiểm tra URL" in shown  # hướng dẫn kiểm lập chỉ mục bằng tay (câu 6 = A)


def test_bai_dia_chi_la_va_dong_ke_hoach_chua_noi_co_cau_bao(project_root, configured, no_network):
    """LC-T123-1 phần T-125: ``skipped_items > 0`` có câu cố định, không im lặng."""
    seed()
    at = open_tracking(project_root)
    shown = everything(at)
    assert "1 bài, trang có địa chỉ không khớp địa chỉ website trong cài đặt" in shown
    assert "1 dòng kế hoạch «Đã đăng» chưa nối được" in shown


def test_loc_theo_nhan_va_chi_bai_trong_ke_hoach(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    run(at.selectbox(key="trk-flag").set_value(FlagKind.RANK_DROP.value))
    assert list(table(at, "Bài / trang")["Bài / trang"]) == ["Cổng sắt bị xệ cánh"]
    run(at.selectbox(key="trk-flag").set_value("all"))
    run(at.checkbox(key="trk-plan-only").check())
    assert sorted(table(at, "Bài / trang")["Mã KH"]) == ["B-007", "B-012"]


def test_chua_co_ke_hoach_thi_o_loc_ke_hoach_bi_khoa(project_root, configured, no_network):
    seed(plan=False)
    at = open_tracking(project_root)
    assert at.checkbox(key="trk-plan-only").disabled
    assert set(table(at, "Bài / trang")["Mã KH"]) == {""}


def test_trang_khac_hien_duong_dan_da_lam_sach_chu_thuan(project_root, configured, no_network):
    """LC-T120-19: đường dẫn «Trang khác» đã giải mã, bỏ ký tự đảo hướng, hiện trong ô bảng."""
    seed()
    at = open_tracking(project_root)
    expander = next(
        item for item in at.expander if item.label.startswith("Trang khác trên website")
    )
    assert expander.label.endswith(": 3 trang")
    paths = list(table(at, "Đường dẫn")["Đường dẫn"])
    assert paths[0] == "/ (trang chủ)"
    assert f"/?s=[x]({EVIL})" in paths and "/exe.txt" in paths
    assert not any("\N{RIGHT-TO-LEFT OVERRIDE}" in path for path in paths)
    assert EVIL not in everything(at)  # không thành link, không vào Markdown


def test_chua_co_danh_sach_bai_thi_moi_dia_chi_vao_trang_khac(project_root, configured, no_network):
    seed(index=False)
    at = open_tracking(project_root)
    assert any("Chưa có danh sách bài đã đăng" in text for text in texts(at, "info"))
    assert "/sua-cua-keo" in list(table(at, "Đường dẫn")["Đường dẫn"])


# ================================================================ chữ thuần (LC-T120-11, -19)


def test_tieu_de_wordpress_va_tu_khoa_google_hien_chu_thuan(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    assert HOSTILE_TITLE in list(table(at, "Bài / trang")["Bài / trang"])
    run(at.selectbox(key="trk-page").set_value(15))
    assert HOSTILE_TITLE in at.selectbox(key="trk-page").options  # ô chọn: chữ thuần
    assert any(escape_markdown(HOSTILE_TITLE) in text for text in texts(at, "markdown"))
    run(at.selectbox(key="trk-page").set_value(11))
    words = list(table(at, "Từ khóa")["Từ khóa"])
    assert " " + FORMULA_QUERY in words  # safe_rows: không thành công thức khi tải CSV
    assert MARKDOWN_QUERY in words
    assert EVIL not in everything(at)
    assert not any(
        column.lower().startswith(("link", "url"))
        for frame in at.dataframe
        for column in frame.value
    )


def test_bieu_do_khuon_co_dinh_chi_ngay_va_so(project_root, configured, no_network):
    """LC-T120-20: đặc tả Vega-Lite không có chữ của Google/WordPress, không ``expr``, ``href``,
    ``url``; tên bài nằm ngoài biểu đồ."""
    seed()
    at = open_tracking(project_root)
    run(at.selectbox(key="trk-page").set_value(15))
    found = charts(at)
    assert len(found) == 2
    for chart in found:
        spec = chart.proto.spec
        for banned in ("expr", "href", '"url"', "Đậm", "bấm", EVIL, "evil"):
            assert banned not in spec
        assert json.loads(spec)["encoding"]["x"]["field"] == "tuan"


def test_bang_tu_khoa_gop_cach_go_tu_khoa_chinh_xem_them(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    run(at.selectbox(key="trk-page").set_value(11))
    frame = table(at, "Từ khóa")
    assert len(frame) == 50
    main = frame[frame["Từ khóa"] == "sửa cửa kéo bị kẹt"].iloc[0]
    assert "từ khóa chính" in main["Ghi chú"] and "gộp 2 cách gõ" in main["Ghi chú"]
    assert main["± vị trí"] == "lên 1,0 bậc"  # 7,5 → 6,5 (hai cách gõ cộng lại)
    assert "từ khóa mới" in frame[frame["Từ khóa"] == MARKDOWN_QUERY].iloc[0]["Ghi chú"]
    assert HIDDEN_QUERIES_NOTE in texts(at, "caption")
    run(at.button(key="trk-more-keywords").click())
    assert len(table(at, "Từ khóa")) == 3 + OTHER_KEYWORDS
    run(at.toggle(key="trk-variants").set_value(True))
    assert set(table(at, "Cách gõ")["Cách gõ"]) == {"sửa cửa kéo bị kẹt", "sua cua keo bi ket"}
    placeholder = at.button(key="trk-to-plan")  # chỗ cho T-127
    assert placeholder.disabled


def test_chua_co_tu_khoa_cua_khoang_thi_noi_ro(project_root, configured, no_network):
    seed(queries=False)
    at = open_tracking(project_root)
    run(at.selectbox(key="trk-page").set_value(11))
    assert any("Chưa có từ khóa cho khoảng này" in text for text in texts(at, "caption"))


# ================================================================ khoảng ngày


def test_khoang_tu_chon_sai_thu_tu_bao_loi(project_root, configured, no_network):
    seeded = seed()
    at = open_tracking(project_root)
    run(at.segmented_control(key="trk-range").set_value("Tùy chọn"))
    run(at.date_input(key="trk-from").set_value(seeded.end))
    run(at.date_input(key="trk-to").set_value(seeded.end - timedelta(days=3)))
    assert any("Ngày bắt đầu phải trước" in text for text in texts(at, "error"))
    assert not at.metric


def test_khoang_dai_hon_so_lieu_da_luu_va_cung_ky_nam_truoc(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    run(at.selectbox(key="trk-compare").set_value("Cùng kỳ năm trước"))
    assert any("Chưa có số liệu của kỳ so sánh" in text for text in texts(at, "caption"))
    assert metric(at, "Lượt click").proto.delta == ""
    run(at.segmented_control(key="trk-range").set_value("3 tháng"))
    assert len(table(at, "Bài / trang")) == 5  # 91 ngày vẫn trong 118 ngày đã chốt
    store = SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE)
    store.clear()
    seed_short()
    run(at)
    assert any("chưa đủ cho khoảng" in text for text in texts(at, "warning"))


def seed_short() -> None:
    """Bản lưu tạm chỉ có 31 ngày gần nhất (ví dụ lần lấy đầu dừng giữa chừng)."""
    today = google_today()
    first_provisional = today - timedelta(days=PROVISIONAL - 1)
    start = today - timedelta(days=30)
    current = last_days(first_provisional - timedelta(days=1), 28)
    rows = []
    day = start
    while day <= today:
        rows += [CachedDay(day, *row, day < first_provisional) for row in day_rows(day, current)]
        day += timedelta(days=1)
    SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE).save_days(
        CacheScope(DOMAIN, WORDPRESS),
        rows,
        start=start,
        end=today,
        first_provisional=first_provisional,
        fetched_at=datetime.now(UTC),
        today=today,
    )


# ================================================================ «Lấy số liệu mới»


@pytest.fixture
def google(monkeypatch, configured, data_files):
    """Client Search Console mỗi lần bấm đi qua Google giả (``test_tracking_refresh.Search``)."""
    account = load_service_account(configured, scope=SEARCH_CONSOLE_SCOPE, project_root=data_files)
    fake = FakeGoogle()
    search = trk.Search(fake)
    today = google_today()
    search.incomplete = today - timedelta(days=PROVISIONAL)
    search.last_final = today - timedelta(days=PROVISIONAL + 1)
    factory = trk.Factory(account, fake)
    factory.today = today
    monkeypatch.setattr(refresh_module, "_default_client", factory)
    return factory


def test_bam_lay_so_lieu_moi_hien_ket_qua_roi_hien_so_lieu(project_root, google):
    at = open_tracking(project_root)
    run(at.button(key="trk-fetch").click())
    assert len(google.created) == 1  # một client cho đúng lần bấm
    assert any("Đã lấy số liệu tới hết ngày" in text for text in texts(at, "success"))
    assert "/sua-cua-keo" in list(table(at, "Đường dẫn")["Đường dẫn"])
    run(at)  # kết quả lần bấm chỉ hiện một lần
    assert not any("Đã lấy số liệu tới hết ngày" in text for text in texts(at, "success"))
    run(at.button(key="trk-fetch").click())  # vừa lấy: không gửi lệnh
    assert any("Vừa lấy số liệu lúc" in text for text in texts(at, "info"))
    assert len(google.created) == 2 and google.created[-1].request_count == 0


def test_tab_khac_dang_lay_thi_bao_ban(project_root, google):
    at = open_tracking(project_root)
    assert refresh_module._FETCH_LOCK.acquire(blocking=False)
    try:
        run(at.button(key="trk-fetch").click())
    finally:
        refresh_module._FETCH_LOCK.release()
    assert any("Đang lấy số liệu Search Console ở tab khác" in text for text in texts(at, "info"))
    assert google.created == []


def test_loi_lay_so_lieu_ra_cau_co_dinh_da_escape(project_root, configured, monkeypatch):
    def broken(settings, **kwargs):
        raise SearchConsoleError("Google từ chối: **chưa thêm** email [x](https://evil.example).")

    monkeypatch.setattr(refresh_module, "_default_client", broken)
    at = open_tracking(project_root)
    run(at.button(key="trk-fetch").click())
    errors = texts(at, "error")
    assert any(escape_markdown(refresh_module.MSG_FAILED) in text for text in errors)
    assert any(escape_markdown("**chưa thêm**") in text for text in errors)


# ================================================================ bản lưu tạm


def test_xoa_ban_luu_tam_hoi_lai_roi_moi_xoa(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    run(at.button(key="trk-clear").click())
    assert any("Xóa bản lưu tạm số liệu Search Console" in text for text in texts(at, "warning"))
    run(at.button(key="trk-clear-no").click())
    assert search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    run(at.button(key="trk-clear").click())
    run(at.button(key="trk-clear-yes").click())
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    assert any("Đã xóa bản lưu tạm" in text for text in texts(at, "success"))
    assert no_network.count == 0


def test_loi_mo_ban_luu_tam_bao_cau_co_dinh_va_mo_san_nut_xoa(
    project_root, configured, no_network, monkeypatch
):
    """Lá Chắn T-122 mục 8.2: file báo lỗi lặp lại thì có lối ra «Xóa bản lưu tạm»."""
    seed()

    def busy(self, scope):
        raise SearchCacheError(search_cache.MSG_OPEN)

    monkeypatch.setattr(SearchCacheStore, "load", busy)
    at = open_tracking(project_root)
    assert any(escape_markdown(search_cache.MSG_OPEN) in text for text in texts(at, "error"))
    assert any(item.label.startswith("🧹") and item.proto.expanded for item in at.expander)
    run(at.button(key="trk-clear").click())
    run(at.button(key="trk-clear-yes").click())
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()

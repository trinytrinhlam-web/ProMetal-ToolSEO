"""T-138 yêu cầu 6 (Thợ Máy): test không bao giờ ghi vào ``data/`` thật của thư mục dự án.

``tests/conftest.py`` trỏ mọi file kho trong ``seo_app/storage`` (nháp, thẻ ảnh, danh sách bài
đã đăng, kế hoạch, số liệu Search Console) sang thư mục tạm riêng cho từng test. Ở đây:

- mọi hằng ``DEFAULT_…_FILE`` của mọi module trong ``seo_app/storage`` đang trỏ ra ngoài thư mục dự
  án (kho mới thêm sau mà quên trỏ thì ca này hỏng);
- một luồng có WordPress giả (tải danh sách bài đã đăng, rồi mở lại như trang Soạn bài đọc cache),
  ghi kế hoạch, ghi số liệu: không file nào trong ``data/`` thật được tạo hay đổi, mà file nằm
  đúng chỗ đã trỏ;
- đối chứng: trỏ các hằng về ``data/`` của một thư mục dự án giả (như khi không có fixture) thì
  cùng luồng đó tạo file ở đó.
"""

from __future__ import annotations

import importlib
import pkgutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

import seo_app.storage as storage_package
from seo_app.config import PROJECT_ROOT
from seo_app.storage import plan_cache, search_cache, site_index
from seo_app.storage.plan_cache import PlanCacheStore
from seo_app.storage.search_cache import CacheScope, SearchCacheStore
from seo_app.storage.site_index import SiteIndexStore
from seo_app.wordpress import PublishedItem

DATA = PROJECT_ROOT / "data"
BASE_URL = "https://suachuacuasat.com"
NOW = datetime(2026, 11, 18, 9, 0, tzinfo=UTC)


class FakeSite:
    """WordPress giả cho kho danh sách bài (``PublishedSource``): không gọi mạng."""

    base_url = BASE_URL

    def __init__(self) -> None:
        self.calls = 0

    def list_published(self) -> list[PublishedItem]:
        self.calls += 1
        return [PublishedItem(7, "post", "cua-cuon", f"{BASE_URL}/cua-cuon/", "Cửa cuốn")]


def data_snapshot() -> dict[str, tuple[int, int]]:
    """Mọi file trong ``data/`` thật: đường dẫn tương đối → (cỡ, giờ sửa). Chưa có thư mục: rỗng."""
    if not DATA.exists():
        return {}
    return {
        str(path.relative_to(DATA)): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in DATA.rglob("*")
        if path.is_file()
    }


def run_flow() -> FakeSite:
    """Luồng dùng ba kho lưu tạm qua đường mặc định (như các trang): tải danh sách bài từ WordPress
    giả rồi đọc lại cache, ghi rồi đọc kế hoạch, ghi ngày đăng của số liệu Google."""
    site = FakeSite()
    listing = site_index.site_listing(SiteIndexStore(), site)
    assert listing.index is not None and [item.id for item in listing.index.items] == [7]
    assert SiteIndexStore().load(BASE_URL) is not None  # như cached_site_index của Soạn bài
    PlanCacheStore().save("sheet-thu", [["Mã bài", "Từ khóa chính"]], NOW)
    assert PlanCacheStore().load("sheet-thu") is not None
    scope = CacheScope("sc-domain:suachuacuasat.com", BASE_URL)
    SearchCacheStore().save_post_dates(scope, {7: date(2026, 11, 1)}, keep=[7])
    return site


def default_files() -> dict[str, Path]:
    """Mọi hằng ``DEFAULT_…_FILE`` (``Path``) của mọi module trong ``seo_app/storage``."""
    found = {}
    for info in pkgutil.iter_modules(storage_package.__path__):
        module = importlib.import_module(f"{storage_package.__name__}.{info.name}")
        for name, value in vars(module).items():
            if name.startswith("DEFAULT_") and name.endswith("_FILE") and isinstance(value, Path):
                found[f"{info.name}.{name}"] = value
    return found


def test_every_storage_default_file_points_outside_the_project():
    files = default_files()
    assert {
        "drafts.DEFAULT_DRAFTS_FILE",
        "image_tags.DEFAULT_IMAGE_TAGS_FILE",
        "site_index.DEFAULT_SITE_INDEX_FILE",
        "plan_cache.DEFAULT_PLAN_CACHE_FILE",
        "search_cache.DEFAULT_SEARCH_CACHE_FILE",
    } <= set(files)
    inside = {name: path for name, path in files.items() if path.is_relative_to(PROJECT_ROOT)}
    assert inside == {}, "conftest chưa trỏ các file kho này sang thư mục tạm"


def test_flow_with_fake_wordpress_never_writes_real_data_folder():
    before = data_snapshot()
    site = run_flow()
    assert site.calls == 1  # lần đầu tải từ «website», lần đọc sau lấy cache
    assert data_snapshot() == before
    for path in (
        site_index.DEFAULT_SITE_INDEX_FILE,
        plan_cache.DEFAULT_PLAN_CACHE_FILE,
        search_cache.DEFAULT_SEARCH_CACHE_FILE,
    ):
        assert path.is_file() and not path.is_relative_to(PROJECT_ROOT)


def test_control_without_redirect_the_flow_writes_into_data(tmp_path, monkeypatch):
    # Như khi không có fixture: các hằng trỏ về data/ của một thư mục dự án (giả, để không đụng
    # data/ thật) thì cùng luồng tạo file ở đó.
    data = tmp_path / "du-an" / "data"
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", data / "site_index.sqlite")
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", data / "plan_cache.sqlite")
    monkeypatch.setattr(search_cache, "DEFAULT_SEARCH_CACHE_FILE", data / "search_cache.sqlite")
    monkeypatch.setattr(site_index, "PROJECT_ROOT", tmp_path / "du-an")
    monkeypatch.setattr(plan_cache, "PROJECT_ROOT", tmp_path / "du-an")
    monkeypatch.setattr(search_cache, "PROJECT_ROOT", tmp_path / "du-an")
    run_flow()
    created = {path.name for path in data.iterdir() if path.suffix == ".sqlite"}
    assert created == {"site_index.sqlite", "plan_cache.sqlite", "search_cache.sqlite"}


@pytest.mark.parametrize(
    "fixture",
    ["_never_touch_real_drafts", "_never_touch_real_image_tags", "_never_touch_real_caches"],
)
def test_conftest_redirects_are_autouse(request, fixture):
    assert fixture in request.fixturenames

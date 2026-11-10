"""T-125 lượt 2 (Thợ Máy): trang «📈 Theo dõi» không đọc lại bản lưu tạm khi file không đổi
(SL-T125-1), nút «Xóa bản lưu tạm» xóa trong cùng khóa với «Lấy số liệu mới» (SL-T125-2).

- ``SearchCacheStore.stamp``: dấu file đổi sau mỗi lần ghi (kể cả cùng cỡ, cùng giờ sửa), không
  đổi khi chỉ đọc; không mở SQLite, không tạo gì; liên kết, thư mục: ``None``.
- ``refresh.clear_cache``: tab khác đang lấy thì không xóa (``MSG_BUSY``); đang xóa thì lần lấy ở
  tab khác nhận BUSY; khóa luôn được nhả.
- Trang: chỉ đọc, kiểm lại bản lưu tạm khi dấu file, phạm vi đổi (LC-T120-9); ``build_tracking``
  chỉ dựng lại khi bản lưu tạm, danh sách bài, kế hoạch đổi; bản giữ nằm trong phiên (không
  ``st.cache_data``, ``st.cache_resource``: LC-T120-21), không gọi mạng.

Không gọi mạng (bộ chặn của ``conftest.py``, client giả đếm lệnh của test trang); mọi file lưu tạm
nằm trong thư mục tạm.
"""

from __future__ import annotations

import ast
import os
import shutil
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import test_app_pages as pages
import test_t125_tracking_page as page_tests
from test_t125_tracking_page import DOMAIN, POSTS, WORDPRESS, open_tracking, run, seed, texts

from seo_app.config import Settings
from seo_app.images.data_dir import MSG_DATA_DIR_LINK
from seo_app.storage import search_cache, site_index
from seo_app.storage.search_cache import CacheScope, SearchCacheError, SearchCacheStore
from seo_app.storage.site_index import SiteIndex, SiteIndexStore
from seo_app.text import escape_markdown
from seo_app.tracking import match
from seo_app.tracking import refresh as refresh_module
from seo_app.tracking.refresh import MSG_BUSY, ClearResult, clear_cache
from seo_app.wordpress.client import PublishedItem

env = pages.env
private_key = page_tests.private_key
key_file = page_tests.key_file
data_files = page_tests.data_files  # autouse: mọi file lưu tạm trong thư mục tạm
configured = page_tests.configured
no_network = page_tests.no_network

PAGE_FILE = Path(__file__).resolve().parents[1] / "app" / "views" / "tracking.py"


def store() -> SearchCacheStore:
    return SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE)


def scope() -> CacheScope:
    return CacheScope(DOMAIN, WORDPRESS)


class Counter:
    """Đếm số lần gọi một hàm (giữ nguyên việc hàm làm)."""

    def __init__(self, monkeypatch, owner, name: str) -> None:
        self.count = 0
        original = getattr(owner, name)

        def counted(*args, **kwargs):
            self.count += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(owner, name, counted)


# ================================================================ dấu file (SL-T125-1)


def test_stamp_is_none_without_a_file_and_creates_nothing():
    path = search_cache.DEFAULT_SEARCH_CACHE_FILE.parent / "con" / "chua-co.sqlite"
    assert SearchCacheStore(path=path).stamp() is None
    assert not path.parent.exists()


def test_stamp_is_the_same_after_reading_only():
    seed(queries=False, index=False, plan=False)
    before = store().stamp()
    assert before is not None
    assert store().load(scope()) is not None
    assert store().stamp() == before


@pytest.mark.parametrize("write", ["ngay", "tu-khoa", "ngay-dang"])
def test_stamp_changes_after_every_write(write):
    seed(queries=False, index=False, plan=False)
    before = store().stamp()
    today = page_tests.google_today()
    if write == "ngay":
        cache = store().load(scope())
        store().save_days(
            scope(), [], start=cache.first_provisional, end=cache.covered_end,
            first_provisional=cache.first_provisional, fetched_at=datetime.now(UTC), today=today,
        )  # fmt: skip
    elif write == "tu-khoa":
        day = today - timedelta(days=40)
        store().save_queries(
            scope(), [], start=day, end=day, fetched_at=datetime.now(UTC), truncated=False
        )
    else:
        store().save_post_dates(scope(), {11: today - timedelta(days=9)})
    assert store().stamp() != before


def test_stamp_sees_a_write_with_the_same_size_and_time():
    """Hai lần ghi trong cùng một nhịp đồng hồ, cỡ file không đổi: «số đếm thay đổi» ở đầu file
    SQLite vẫn khác (giờ sửa đặt lại y như trước để mô phỏng)."""
    seed(queries=False, index=False, plan=False)
    path = search_cache.DEFAULT_SEARCH_CACHE_FILE
    store().save_post_dates(scope(), {11: page_tests.google_today()})
    before = store().stamp()
    info = os.stat(path)
    store().save_post_dates(scope(), {11: page_tests.google_today() - timedelta(days=1)})
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
    after = store().stamp()
    assert os.stat(path).st_size == info.st_size and os.stat(path).st_mtime_ns == info.st_mtime_ns
    assert after != before


def test_stamp_sees_a_file_replaced_by_a_copy():
    """Tab khác (hay người dùng) thay file bằng bản chép y hệt nội dung, cùng giờ sửa: mã file khác
    nên vẫn đọc lại."""
    seed(queries=False, index=False, plan=False)
    path = search_cache.DEFAULT_SEARCH_CACHE_FILE
    before = store().stamp()
    info = os.stat(path)
    copy = path.with_name("ban-chep.sqlite")
    shutil.copyfile(path, copy)
    os.replace(copy, path)
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
    assert store().stamp() != before


def test_stamp_sees_a_wal_file():
    seed(queries=False, index=False, plan=False)
    path = search_cache.DEFAULT_SEARCH_CACHE_FILE
    before = store().stamp()
    wal = path.with_name(path.name + "-wal")
    wal.write_bytes(b"x" * 32)
    try:
        assert store().stamp() != before
    finally:
        wal.unlink()
    assert store().stamp() == before


def test_stamp_of_a_folder_or_link_is_none(tmp_path):
    folder = tmp_path / "la-thu-muc.sqlite"
    folder.mkdir()
    assert SearchCacheStore(path=folder).stamp() is None
    target = tmp_path / "that.sqlite"
    target.write_bytes(b"SQLite format 3\x00" + b"\x00" * 84)
    link = tmp_path / "lien-ket.sqlite"
    try:
        os.symlink(target, link)
    except OSError:
        pytest.skip("máy này không cho tạo symlink file (Windows cần quyền Developer Mode)")
    assert SearchCacheStore(path=link).stamp() is None


# ================================================================ clear_cache (SL-T125-2)


def test_clear_cache_refuses_while_a_fetch_holds_the_lock():
    seed(queries=False, index=False, plan=False)
    assert refresh_module._FETCH_LOCK.acquire(blocking=False)
    try:
        result = clear_cache(store())
    finally:
        refresh_module._FETCH_LOCK.release()
    assert result == ClearResult(False, MSG_BUSY, busy=True)
    assert search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()


def test_clear_cache_holds_the_lock_while_clearing():
    """Đang xóa thì «Lấy số liệu mới» ở tab khác nhận BUSY, không ghi vào file đang bị xóa."""
    seed(queries=False, index=False, plan=False)
    seen = []

    class Watching(SearchCacheStore):
        def clear(self) -> None:
            seen.append(refresh_module._FETCH_LOCK.locked())
            settings = Settings(wordpress_url=WORDPRESS, gsc_site_url=DOMAIN)
            other = refresh_module.refresh(settings, self)
            seen.append(other.outcome)
            super().clear()

    result = clear_cache(Watching(path=search_cache.DEFAULT_SEARCH_CACHE_FILE))
    assert result == ClearResult(True)
    assert seen == [True, refresh_module.Outcome.BUSY]
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    assert not refresh_module._FETCH_LOCK.locked()


def test_clear_cache_error_is_a_fixed_message_and_releases_the_lock(monkeypatch):
    seed(queries=False, index=False, plan=False)
    monkeypatch.setattr(search_cache, "dir_has_link", lambda *_args: True)
    assert clear_cache(store()) == ClearResult(False, MSG_DATA_DIR_LINK)
    assert search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    assert not refresh_module._FETCH_LOCK.locked()


def test_clear_cache_releases_the_lock_on_unexpected_errors():
    class Broken(SearchCacheStore):
        def clear(self) -> None:
            raise RuntimeError("lỗi bất ngờ")

    with pytest.raises(RuntimeError):
        clear_cache(Broken(path=search_cache.DEFAULT_SEARCH_CACHE_FILE))
    assert not refresh_module._FETCH_LOCK.locked()


def test_clear_cache_from_two_threads_never_runs_twice_at_once():
    seed(queries=False, index=False, plan=False)
    inside = threading.Event()
    release = threading.Event()
    results = []

    class Slow(SearchCacheStore):
        def clear(self) -> None:
            inside.set()
            release.wait(10)
            super().clear()

    worker = threading.Thread(
        target=lambda: results.append(
            clear_cache(Slow(path=search_cache.DEFAULT_SEARCH_CACHE_FILE))
        )
    )
    worker.start()
    try:
        assert inside.wait(10)
        assert clear_cache(store()) == ClearResult(False, MSG_BUSY, busy=True)
    finally:
        release.set()
        worker.join(30)
    assert results == [ClearResult(True)]


# ================================================================ trang: giữ bản đã đọc trong phiên


def test_reruns_reuse_the_tracking_table_too(project_root, configured, no_network, monkeypatch):
    seed()
    builds = Counter(monkeypatch, match, "build_tracking")
    at = open_tracking(project_root)
    assert builds.count == 1
    run(at.segmented_control(key="trk-range").set_value("7 ngày"))
    run(at.selectbox(key="trk-page").set_value(11))
    run(at.selectbox(key="trk-compare").set_value("Cùng kỳ năm trước"))
    assert builds.count == 1
    assert no_network.count == 0


def test_new_post_list_rebuilds_the_tracking_table(
    project_root, configured, no_network, monkeypatch
):
    seed()
    builds = Counter(monkeypatch, match, "build_tracking")
    loads = Counter(monkeypatch, SearchCacheStore, "load")
    at = open_tracking(project_root)
    extra = PublishedItem(17, "post", "bai-moi", WORDPRESS + "/bai-moi/", "Bài mới đăng hôm qua")
    SiteIndexStore(path=site_index.DEFAULT_SITE_INDEX_FILE).save(
        SiteIndex(WORDPRESS, datetime.now(UTC), (*POSTS, extra))
    )
    run(at)
    assert (loads.count, builds.count) == (1, 2)  # bản lưu tạm số liệu không đổi: không đọc lại
    assert "Bài mới đăng hôm qua" in at.selectbox(key="trk-page").options


def test_changed_property_reads_the_file_again(project_root, configured, no_network, monkeypatch):
    seed()
    loads = Counter(monkeypatch, SearchCacheStore, "load")
    at = open_tracking(project_root)
    assert loads.count == 1
    monkeypatch.setenv("GSC_SITE_URL", "https://suachuacuasat.com/")
    run(at)
    assert loads.count == 2  # phạm vi khác: đọc lại (kho bỏ bản của thuộc tính cũ, GN-2 Soi Lỗi)
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()


def test_file_written_during_reading_is_read_again(
    project_root, configured, no_network, monkeypatch
):
    """Tab khác ghi đúng lúc trang đang đọc: không giữ bản vừa đọc (có thể đã cũ), lần chạy sau
    đọc lại."""
    seed()
    original = SearchCacheStore.load
    calls = []

    def load_then_other_tab_writes(self, cache_scope):
        calls.append(cache_scope)
        cache = original(self, cache_scope)
        if len(calls) == 1:
            store().save_post_dates(scope(), {11: page_tests.google_today()})
        return cache

    monkeypatch.setattr(SearchCacheStore, "load", load_then_other_tab_writes)
    at = open_tracking(project_root)
    run(at.segmented_control(key="trk-range").set_value("7 ngày"))
    run(at.selectbox(key="trk-page").set_value(11))
    assert len(calls) == 2  # lần sau đọc lại một lần, rồi giữ


def test_clearing_drops_the_session_copy(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    run(at.button(key="trk-clear").click())
    run(at.button(key="trk-clear-yes").click())
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    assert any("Đã xóa bản lưu tạm" in text for text in texts(at, "success"))
    assert "trk-cache-memo" not in at.session_state
    run(at)
    assert "trk-cache-memo" not in at.session_state


def test_clear_refused_shows_a_warning_and_keeps_the_numbers(project_root, configured, no_network):
    seed()
    at = open_tracking(project_root)
    assert refresh_module._FETCH_LOCK.acquire(blocking=False)
    try:
        run(at.button(key="trk-clear").click())
        run(at.button(key="trk-clear-yes").click())
    finally:
        refresh_module._FETCH_LOCK.release()
    assert any(escape_markdown(MSG_BUSY) in text for text in texts(at, "warning"))
    assert search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    run(at)
    assert at.session_state["trk-cache-memo"]["cache"] is not None


def test_a_new_session_reads_the_file_itself(project_root, configured, no_network, monkeypatch):
    """Bản giữ nằm trong phiên (tab), không dùng chung qua bộ nhớ tiến trình."""
    seed()
    loads = Counter(monkeypatch, SearchCacheStore, "load")
    open_tracking(project_root)
    open_tracking(project_root)
    assert loads.count == 2


def test_page_has_no_streamlit_cache_and_reads_errors_each_time(
    project_root, configured, no_network, monkeypatch
):
    """LC-T120-21: không ``st.cache_data``, ``st.cache_resource``. Lỗi đọc (file bận) không được
    giữ: lần chạy sau thử lại."""
    tree = ast.parse(PAGE_FILE.read_text(encoding="utf-8"))
    names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not names & {"cache_data", "cache_resource", "fragment", "experimental_memo"}
    seed()
    original = SearchCacheStore.load
    calls = []

    def busy_once(self, cache_scope):
        calls.append(cache_scope)
        if len(calls) == 1:
            raise SearchCacheError(search_cache.MSG_BUSY)
        return original(self, cache_scope)

    monkeypatch.setattr(SearchCacheStore, "load", busy_once)
    at = open_tracking(project_root)
    assert any("đang bận" in text for text in texts(at, "error"))
    run(at)
    assert len(calls) == 2 and not texts(at, "error")

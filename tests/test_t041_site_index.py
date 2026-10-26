"""T-041 (Thợ Máy): danh sách bài cho bước SEO.

- SL-T037-5 (phần còn lại): chương trình khác đang ghi dở file cache (giữ khóa ghi nhưng vẫn cho
  đọc) thì ``get``/``refresh`` không chờ đủ 5 giây ở bước ghi; trả danh sách vừa tải kèm "đang bận".
  (Ca khóa hẳn ``BEGIN EXCLUSIVE`` đã sửa ở T-042, xem ``tests/test_site_index_t042.py``.)
- ``site_listing``: chưa kết nối WordPress thì báo nhẹ, không ném lỗi; lỗi tải, danh sách bị cắt,
  ghi cache lỗi đều thành câu báo.

Chỉ nguồn giả, không gọi mạng.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fake_wordpress import BASE_URL

import seo_app.storage.site_index as site_index
from seo_app.storage.site_index import (
    MSG_NOT_CONNECTED,
    MSG_TRUNCATED,
    SiteIndexError,
    SiteIndexStore,
    site_listing,
)
from seo_app.wordpress import PublishedItem, WordPressError
from seo_app.wordpress.client import PublishedList

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def published(id_):
    return PublishedItem(
        id=id_, type="post", slug=f"bai-{id_}", link=f"{BASE_URL}/bai-{id_}/", title=f"Bài {id_}"
    )


class Source:
    def __init__(self, items, error=None):
        self.base_url = BASE_URL
        self.items = items
        self.error = error
        self.calls = 0

    def list_published(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.items


@pytest.fixture
def store(tmp_path):
    return SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")


def later() -> datetime:
    return datetime.now(TZ) + timedelta(hours=7)


# ------------------------------------------------------------------ SL-T037-5: khóa ghi


@pytest.mark.parametrize("call", ["get", "refresh"])
def test_pending_write_elsewhere_does_not_hang(store, call):
    """Kết nối khác giữ khóa ghi (``BEGIN IMMEDIATE`` rồi ghi, chưa xong): đọc vẫn được, chỉ
    bước ghi phải chờ. Trước T-041 ``get`` khi cache cũ chờ khoảng 5,5 giây trên Windows."""
    store.refresh(Source([published(1)]))
    holder = sqlite3.connect(store.path, isolation_level=None)
    try:
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("UPDATE info SET value = value WHERE key = 'site'")
        source = Source([published(2)])
        start = time.monotonic()
        index = store.get(source, now=later()) if call == "get" else store.refresh(source)
        elapsed = time.monotonic() - start
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert [i.id for i in index.items] == [2]
    assert "đang bận" in index.cache_error
    assert source.calls == 1
    assert store.reset_count == 0
    assert elapsed < site_index._SQLITE_TIMEOUT  # một lần chờ ngắn (~1 giây)
    assert [i.id for i in store.load(BASE_URL).items] == [1]  # cache cũ còn nguyên


def test_write_wait_is_short():
    assert site_index._WRITE_TIMEOUT <= site_index._HEALTH_TIMEOUT < site_index._SQLITE_TIMEOUT


# ------------------------------------------------------------------ site_listing


def test_not_connected_is_a_gentle_notice(store):
    listing = site_listing(store, None)
    assert listing.index is None
    assert listing.notice == MSG_NOT_CONNECTED
    assert "chưa kết nối" in listing.notice.lower() and "vẫn dùng" in listing.notice


def test_listing_uses_cache_then_refresh_on_demand(store):
    source = Source([published(1)])
    first = site_listing(store, source)
    second = site_listing(store, source)
    assert [i.id for i in first.index.items] == [1] and first.notice == ""
    assert second.index.from_cache and source.calls == 1  # cache còn mới: không gọi mạng
    source.items = [published(1), published(3)]
    again = site_listing(store, source, refresh=True)  # nút «Tải lại danh sách bài»
    assert [i.id for i in again.index.items] == [1, 3] and source.calls == 2


def test_wordpress_error_becomes_notice(store):
    error = WordPressError("WordPress trả lỗi 500 khi đọc danh sách bài.", status_code=500)
    listing = site_listing(store, Source([], error=error))
    assert listing.index is None
    assert "Chưa tải được danh sách bài" in listing.notice and "lỗi 500" in listing.notice


def test_truncated_list_is_noted(store):
    items = PublishedList([published(1)])
    items.truncated = True
    listing = site_listing(store, Source(items))
    assert listing.index.truncated
    assert MSG_TRUNCATED in listing.notice


def test_cache_write_error_is_noted_but_list_kept(store, monkeypatch):
    def broken_save(self, index):
        raise SiteIndexError("Không ghi được file lưu tạm danh sách bài (lỗi đọc/ghi).")

    monkeypatch.setattr(SiteIndexStore, "save", broken_save)
    listing = site_listing(store, Source([published(5)]))
    assert [i.id for i in listing.index.items] == [5]
    assert "Không ghi được file lưu tạm" in listing.notice

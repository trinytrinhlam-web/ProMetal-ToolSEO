"""T-125 Soi Lỗi (đầy đủ): trang «📈 Theo dõi» (``app/views/tracking.py``) và mục Search Console
ở Cài đặt → 📗 Google (``app/views/settings.py``).

Bổ sung cho test của Họa Sĩ (``tests/test_t125_tracking_page.py``,
``tests/test_t125_settings_search_console.py``), theo trọng tâm Chỉ Huy B giao:

- Mọi chữ Markdown trên trang (markdown, chú thích, ô báo, tên ô mở rộng) không có link hay chữ
  đậm dựng từ chữ Google, WordPress, kể cả khi xem chi tiết bài có tiêu đề lạ và từng cách gõ.
- Cài đặt: sau khi đã bấm «Tìm thuộc tính», «Kiểm tra», các lần chạy lại (đổi ô chọn) không gửi
  thêm lệnh nào; mỗi nút một lần gọi.
- Trang đọc lại số liệu mới khi file lưu tạm đổi (đối chứng cho bản sửa SL-T125-1).
- SL-T125-1: mỗi lần bấm trên trang, bản lưu tạm được đọc và kiểm lại toàn bộ dù file không đổi.
- SL-T125-2: «Xóa bản lưu tạm» không xét lần lấy số liệu đang chạy ở tab khác.

Lỗi mới để ``xfail(strict=True)`` kèm mã SL-T125-n. Không gọi mạng (bộ chặn của ``conftest.py``,
client giả đếm lệnh của Họa Sĩ); mọi file lưu tạm nằm trong thư mục tạm.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
import test_app_pages as pages
import test_t125_settings_search_console as settings_tests
import test_t125_tracking_page as page_tests
from test_t125_tracking_page import (
    EVIL,
    HOSTILE_TITLE,
    MARKDOWN_QUERY,
    WORDPRESS,
    everything,
    open_tracking,
    run,
    seed,
    table,
    texts,
)

from seo_app.storage import search_cache
from seo_app.storage.search_cache import CachedQuery, CacheScope, SearchCacheStore
from seo_app.tracking import refresh as refresh_module
from seo_app.tracking.periods import last_days
from seo_app.tracking.refresh import ConnectionCheck, HostShare

env = pages.env
private_key = page_tests.private_key
key_file = page_tests.key_file
data_files = page_tests.data_files  # autouse: mọi file lưu tạm trong thư mục tạm
configured = page_tests.configured
no_network = page_tests.no_network
ready = settings_tests.ready

DOMAIN = page_tests.DOMAIN
RAW_MARKUP = (f"]({EVIL}", "[bấm](", "**Đậm**", "**đậm**", "[x](")


def raw_markup(text: str) -> list[str]:
    """Đoạn Markdown dựng từ chữ Google, WordPress còn nguyên (chưa thoát) trong ``text``."""
    return [piece for piece in RAW_MARKUP if piece in text]


# ======================================= chữ Google, WordPress không thành Markdown (trọng tâm 2)


def test_no_markup_from_google_or_wordpress_text_anywhere_on_the_page(
    project_root, configured, no_network
):
    """Quét **mọi** chữ Markdown trên trang ở các trạng thái có chữ lạ: bài có từ khóa dạng công
    thức, dạng Markdown (xem từng cách gõ), bài có tiêu đề Markdown/HTML, «Trang khác» có
    ``?s=[x](…)``. Không chỗ nào còn link hay chữ đậm chưa thoát; tên ô mở rộng, nhãn số liệu không
    chứa chữ ngoài."""
    seed()
    at = open_tracking(project_root)
    states = []
    run(at.selectbox(key="trk-page").set_value(11))  # bài có từ khóa lạ
    run(at.toggle(key="trk-variants").set_value(True))
    states.append(("tu-khoa", everything(at)))
    assert MARKDOWN_QUERY in set(table(at, "Từ khóa")["Từ khóa"])  # chữ thuần trong ô bảng
    run(at.selectbox(key="trk-page").set_value(15))  # bài có tiêu đề Markdown/HTML
    states.append(("tieu-de", everything(at)))
    assert HOSTILE_TITLE in at.selectbox(key="trk-page").options  # ô chọn: chữ thuần
    problems = [(name, raw_markup(text)) for name, text in states if raw_markup(text)]
    labels = [item.label for item in at.expander] + [item.proto.label for item in at.metric]
    problems += [("nhan", label) for label in labels if raw_markup(label) or EVIL in label]
    assert problems == []
    assert no_network.count == 0


# ============================================ Cài đặt: chạy lại không gửi lệnh (trọng tâm 1, 4)


def test_settings_reruns_after_find_and_check_send_no_more_requests(
    project_root, ready, monkeypatch
):
    """Bấm «Tìm thuộc tính», «Kiểm tra» mỗi nút một lần; sau đó đổi ô chọn thuộc tính và chạy lại
    trang nhiều lần: không gọi thêm ``find_properties``, ``check_connection`` (kết quả đọc từ
    phiên), và lần lưu dùng đúng đối tượng của lần tìm."""
    monkeypatch.setenv("GSC_SITE_URL", DOMAIN)
    find = settings_tests.Spy(settings_tests.FOUND)
    check = settings_tests.Spy(
        ConnectionCheck(
            True,
            (refresh_module.MSG_LISTED.format(permission="Hạn chế"),),
            permission="siteRestrictedUser",
            hosts=(HostShare("www.staging-m.suachuacuasat.com", 6),),
            requests=3,
        )
    )
    save = settings_tests.Spy(refresh_module.SaveResult(True, refresh_module.MSG_SAVED))
    monkeypatch.setattr(refresh_module, "find_properties", find)
    monkeypatch.setattr(refresh_module, "check_connection", check)
    monkeypatch.setattr(refresh_module, "save_property", save)
    at = settings_tests.open_settings(project_root)
    run(at.button(key="gsc-find-btn").click())
    run(at.button(key="gsc-check-btn").click())
    assert (len(find.calls), len(check.calls)) == (1, 1)
    choice = at.selectbox(key="gsc-choice")
    run(choice.set_value(settings_tests.PREFIX))
    run(at)
    run(at.button(key="gsc-save").click())
    run(at)
    assert (len(find.calls), len(check.calls)) == (1, 1)
    ((site_url, found), _), *_ = save.calls
    assert site_url == settings_tests.PREFIX and found is settings_tests.FOUND


# =============================================== đọc lại bản lưu tạm (SL-T125-1 và đối chứng)


class CountLoads:
    """Đếm số lần trang đọc bản lưu tạm số liệu (``SearchCacheStore.load``)."""

    def __init__(self, monkeypatch) -> None:
        self.count = 0
        original = SearchCacheStore.load

        def counted(store, scope):
            self.count += 1
            return original(store, scope)

        monkeypatch.setattr(SearchCacheStore, "load", counted)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T125-1: load_cache đọc và kiểm lại toàn bộ bản lưu tạm ở mỗi lần chạy lại trang (đổi "
        "khoảng, chọn bài, bật xem cách gõ…), dù file không đổi; với website cỡ thật (200 trang × "
        "486 ngày) mỗi lần bấm mất 2,2–2,9 giây, 1,25 giây là đọc bản lưu tạm"
    ),
)
def test_sl_t125_1_reruns_do_not_reload_an_unchanged_cache(
    project_root, configured, no_network, monkeypatch
):
    """Thợ Máy T-122 (Đề xuất cho T-125): giữ bản đã đọc trong phiên, kèm giờ sửa và cỡ file; chỉ
    đọc lại khi một trong hai đổi."""
    seed()
    loads = CountLoads(monkeypatch)
    at = open_tracking(project_root)
    assert loads.count >= 1
    loads.count = 0
    run(at.segmented_control(key="trk-range").set_value("7 ngày"))
    run(at.selectbox(key="trk-page").set_value(11))
    run(at.selectbox(key="trk-compare").set_value("Cùng kỳ năm trước"))
    assert loads.count == 0


def test_page_shows_new_data_after_the_cache_file_changes(project_root, configured, no_network):
    """Đối chứng cho bản sửa SL-T125-1: tab khác (hay lần bấm «Lấy số liệu mới») ghi thêm số liệu
    thì lần chạy lại sau trang phải thấy, không giữ bản cũ."""
    seeded = seed()
    at = open_tracking(project_root)
    run(at.segmented_control(key="trk-range").set_value("7 ngày"))
    run(at.selectbox(key="trk-page").set_value(11))
    week = last_days(seeded.end, 7)
    assert not any("cửa kéo tuần này" in text for text in everything(at).splitlines())
    SearchCacheStore(path=search_cache.DEFAULT_SEARCH_CACHE_FILE).save_queries(
        CacheScope(DOMAIN, WORDPRESS),
        [
            CachedQuery(
                week.start, week.end, WORDPRESS + "/sua-cua-keo/", "cửa kéo tuần này", 1, 9, 27.0
            )
        ],
        start=week.start,
        end=week.end,
        fetched_at=datetime.now(UTC),
        truncated=False,
    )
    run(at)
    assert "cửa kéo tuần này" in set(table(at, "Từ khóa")["Từ khóa"])


# ======================================== SL-T125-2: xóa bản lưu tạm khi tab khác đang lấy số liệu


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T125-2: _clear_cache gọi thẳng SearchCacheStore.clear(), không xét khóa lấy số liệu "
        "của refresh; tab đang lấy viết tiếp các đoạn sau vào file mới rồi báo xong, bản lưu tạm "
        "mất phần đầu 16 tháng và lần bấm sau không lấy bù"
    ),
)
def test_sl_t125_2_clearing_is_refused_while_another_tab_fetches(
    project_root, configured, no_network
):
    seed()
    at = open_tracking(project_root)
    assert refresh_module._FETCH_LOCK.acquire(blocking=False)  # tab khác đang «Lấy số liệu mới»
    try:
        run(at.button(key="trk-clear").click())
        run(at.button(key="trk-clear-yes").click())
    finally:
        refresh_module._FETCH_LOCK.release()
    assert search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    shown = texts(at, "info") + texts(at, "warning") + texts(at, "error")
    assert any("tab khác" in text for text in shown)


def test_clearing_still_works_when_no_fetch_is_running(project_root, configured, no_network):
    """Đối chứng cho bản sửa SL-T125-2: không có lần lấy nào đang chạy thì xóa được ngay."""
    seed()
    at = open_tracking(project_root)
    assert not refresh_module._FETCH_LOCK.locked()
    run(at.button(key="trk-clear").click())
    run(at.button(key="trk-clear-yes").click())
    assert not search_cache.DEFAULT_SEARCH_CACHE_FILE.exists()
    assert any("Đã xóa bản lưu tạm" in text for text in texts(at, "success"))

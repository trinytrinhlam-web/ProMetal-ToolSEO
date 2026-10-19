"""Soi Lỗi · T-042: phân trang (SL-T037-3), link/chữ lấy từ site (LC-T037-1), file cache bị
chương trình khác giữ trên Windows (SL-T037-4, SL-T037-5). Chỉ site giả, không mạng thật.

Test ``xfail(strict=True)`` là lỗi Soi Lỗi tìm thấy (``docs/team/reports/T-042-soi-loi.md``).
"""

import sys
import time

import pytest
from fake_wordpress import BASE_URL, query

from seo_app.storage.site_index import SiteIndexStore
from seo_app.wordpress import PublishedItem, WordPressError, is_site_link
from seo_app.wordpress.client import MAX_PAGES, PER_PAGE, _clean_text, _total_pages

POSTS = "/wp-json/wp/v2/posts"
PAGES = "/wp-json/wp/v2/pages"


def raw_post(id_):
    return {
        "id": id_,
        "status": "publish",
        "slug": f"bai-{id_}",
        "link": f"{BASE_URL}/bai-{id_}/",
        "title": {"rendered": f"Bài {id_}"},
    }


def site_with(total, *, header, ignore_page=False, cycle=False):
    """Site có ``total`` bài. ``header``: giá trị X-WP-TotalPages (None: không gửi)."""

    def handler(request):
        page = int(query(request)["page"][0])
        if ignore_page:
            page = 1
        elif cycle:
            page = 1 + (page - 1) % 2
        start = (page - 1) * PER_PAGE
        rows = [raw_post(i + 1) for i in range(start, min(start + PER_PAGE, total))]
        headers = {} if header is None else {"X-WP-TotalPages": header}
        return 200, rows, headers

    return handler


# ================================================================ SL-T037-3, phân trang


@pytest.mark.parametrize("header", ["2", "3", "5"])
def test_valid_header_but_server_ignores_page_is_not_silently_complete(
    fake_wp, wp_client, header
):
    """Bộ đệm trang (plugin cache, CDN) bỏ qua chuỗi truy vấn: trang nào cũng trả trang 1 kèm
    đúng header của trang 1. App đọc đủ số trang theo header, nhận 100 bài lặp lại, bỏ trùng
    còn 100 bài, ``truncated`` vẫn ``False``: thiếu bài lặng lẽ (đúng loại lỗi SL-T037-3)."""
    total = PER_PAGE * int(header)
    fake_wp.on("GET", POSTS, site_with(total, header=header, ignore_page=True))
    fake_wp.on("GET", PAGES, (200, [], {"X-WP-TotalPages": "1"}))
    items = wp_client.list_published()
    assert len(items) == total or items.truncated is True


def test_server_cycling_pages_without_header_stops_and_flags(fake_wp, wp_client):
    """Máy chủ trả xen kẽ trang 1, 2, 1, 2… (không header): không lặp vô hạn, bỏ trùng, cờ
    "chưa đủ" bật."""
    fake_wp.on("GET", POSTS, site_with(10 * PER_PAGE, header=None, cycle=True))
    fake_wp.on("GET", PAGES, [])
    items = wp_client.list_published()
    assert len(items) == 2 * PER_PAGE
    assert items.truncated is True
    assert sum(1 for r in fake_wp.requests if r.path_url.startswith(POSTS)) <= MAX_PAGES


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3", 3),
        (" 3 ", 3),
        ("003", 3),
        ("3, 3", None),  # header lặp bị proxy gộp
        ("3,3", None),
        ("+3", None),
        ("3.0", None),
        ("0x3", None),
        ("Infinity", None),
        ("NaN", None),
        ("-1", None),
        ("3\x00", None),
        ("３", None),  # 3 toàn khổ
        ("٣", None),  # 3 Ả Rập
        ("9" * 40, 10**9),
        (3, None),
        (None, None),
        (b"3", None),
    ],
)
def test_total_pages_header_parsing(value, expected):
    assert _total_pages(value) == expected


@pytest.mark.parametrize("header", ["3, 3", "+3", "Infinity", "３"])
def test_odd_header_reads_on_until_short_page(fake_wp, wp_client, header):
    fake_wp.on("GET", POSTS, site_with(2 * PER_PAGE + 7, header=header))
    fake_wp.on("GET", PAGES, [])
    items = wp_client.list_published()
    assert len(items) == 2 * PER_PAGE + 7
    assert items.truncated is False


def test_huge_header_stops_at_max_pages_and_flags(fake_wp, wp_client):
    fake_wp.on("GET", POSTS, site_with((MAX_PAGES + 3) * PER_PAGE, header="9" * 30))
    fake_wp.on("GET", PAGES, [])
    items = wp_client.list_published()
    assert len(items) == MAX_PAGES * PER_PAGE
    assert items.truncated is True


@pytest.mark.parametrize(
    "answer",
    [
        (404, {"code": "rest_no_route", "message": "x"}, {}),
        (200, {"posts": []}, {}),
        (200, b"<html>", {}),
        (500, {"message": "x"}, {}),
    ],
)
def test_bad_second_page_without_header_raises_not_silent(fake_wp, wp_client, answer):
    """Trang 2 hỏng khi không có header: báo lỗi rõ, không trả danh sách thiếu như đủ."""

    def handler(request):
        if query(request)["page"] == ["1"]:
            return 200, [raw_post(i + 1) for i in range(PER_PAGE)], {}
        return answer

    fake_wp.on("GET", POSTS, handler)
    fake_wp.on("GET", PAGES, [])
    with pytest.raises(WordPressError):
        wp_client.list_published()


# ================================================================ LC-T037-1, ký tự vô hình

# Ký tự "mặc định bỏ qua" mà KHÔNG thuộc loại Cf: ``normalize_meta`` của meta.py coi là vô
# hình (``IGNORABLE_NOT_CF``), nhưng ``is_site_link`` và ``_clean_text`` chỉ xét loại Cf.
IGNORABLE_NOT_CF = ["ㅤ", "ᅟ", "ᅠ", "ﾠ", "͏", "️", "᠋"]


@pytest.mark.xfail(strict=True, reason="SL-T042-7: ký tự vô hình không thuộc Cf lọt link từ site")
@pytest.mark.parametrize("char", IGNORABLE_NOT_CF)
def test_site_link_refuses_ignorable_not_cf(char):
    assert not is_site_link(f"{BASE_URL}/cua{char}sat/", BASE_URL)


@pytest.mark.xfail(strict=True, reason="SL-T042-7: ký tự vô hình không thuộc Cf còn trong chữ")
@pytest.mark.parametrize("char", IGNORABLE_NOT_CF)
def test_clean_text_drops_ignorable_not_cf(char):
    assert _clean_text(f"Cửa{char} sắt", 50) == "Cửa sắt"


@pytest.mark.parametrize(
    "char", ["​", "‌", "‍", "⁠", "⁦", "‮", "﻿", "­",
             "\U000e0001", "؜", "᠎"]
)
def test_cf_characters_are_dropped_and_refused(char):
    assert _clean_text(f"Cửa{char} sắt", 50) == "Cửa sắt"
    assert not is_site_link(f"{BASE_URL}/cua{char}sat/", BASE_URL)


@pytest.mark.parametrize(
    "link",
    [
        BASE_URL + "/a%3Cscript%3E/",  # đã mã hóa: an toàn, phải qua
        BASE_URL + "/c%E1%BB%ADa/",
        BASE_URL + "/?p=42&preview=true",
    ],
)
def test_encoded_links_still_pass(link):
    assert is_site_link(link, BASE_URL)


@pytest.mark.parametrize(
    "link",
    [
        BASE_URL + "/＜script＞/",  # < > toàn khổ
    ],
)
def test_fullwidth_brackets_are_not_html_and_pass(link):
    """``＜`` ``＞`` không phải dấu của HTML, không thoát được ``href``: ghi nhận hành vi."""
    assert is_site_link(link, BASE_URL)


# ================================================================ SL-T037-4/5 trên Windows


def published(id_):
    return PublishedItem(
        id=id_, type="post", slug=f"bai-{id_}", link=f"{BASE_URL}/bai-{id_}/", title=f"Bài {id_}"
    )


class Source:
    def __init__(self, items):
        self.base_url = BASE_URL
        self.items = items

    def list_published(self):
        return list(self.items)


@pytest.fixture
def store(tmp_path):
    return SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")


GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
SHARE_READ, SHARE_WRITE, SHARE_DELETE = 1, 2, 4


def _kernel32():
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
        wintypes.DWORD, wintypes.HANDLE,
    ]

    class Overlapped(ctypes.Structure):
        _fields_ = [
            ("Internal", ctypes.c_void_p),
            ("InternalHigh", ctypes.c_void_p),
            ("Offset", wintypes.DWORD),
            ("OffsetHigh", wintypes.DWORD),
            ("hEvent", wintypes.HANDLE),
        ]

    kernel32.LockFileEx.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(Overlapped),
    ]
    return ctypes, wintypes, kernel32, Overlapped


def _open(path, access, share, *, lock_shared_bytes=False):
    ctypes, wintypes, kernel32, overlapped = _kernel32()
    handle = kernel32.CreateFileW(str(path), access, share, None, 3, 0, None)
    assert handle not in (None, wintypes.HANDLE(-1).value), ctypes.get_last_error()
    if lock_shared_bytes:
        # Chương trình khác (không phải SQLite) khóa vùng byte SQLite dùng để khóa đọc.
        ov = overlapped()
        ov.Offset = 0x40000000  # PENDING_BYTE của SQLite
        assert kernel32.LockFileEx(handle, 3, 0, 512 + 2, 0, ctypes.byref(ov))
    return lambda: kernel32.CloseHandle(handle)


@pytest.mark.skipif(sys.platform != "win32", reason="chế độ chia sẻ file chỉ có trên Windows")
@pytest.mark.parametrize(
    ("access", "share", "lock"),
    [
        (GENERIC_READ, 0, False),  # giữ độc quyền
        (GENERIC_READ, SHARE_READ, False),  # chỉ cho đọc
        (GENERIC_READ, SHARE_READ | SHARE_DELETE, False),
        (GENERIC_READ, SHARE_DELETE, False),
        (GENERIC_WRITE, SHARE_WRITE, False),
        (GENERIC_READ | GENERIC_WRITE, SHARE_READ | SHARE_WRITE, False),  # không cho xóa
        (GENERIC_READ | GENERIC_WRITE, SHARE_READ | SHARE_WRITE | SHARE_DELETE, True),
    ],
    ids=["excl", "read", "read-delete", "delete", "write", "read-write", "byte-lock"],
)
def test_cache_held_by_other_program_is_never_deleted_and_get_is_quick(
    store, access, share, lock
):
    store.refresh(Source([published(1)]))
    close = _open(store.path, access, share, lock_shared_bytes=lock)
    try:
        start = time.monotonic()
        store.load(BASE_URL)
        index = store.get(Source([published(2)]))
        store.refresh(Source([published(3)]))
        elapsed = time.monotonic() - start
    finally:
        close()
    assert store.reset_count == 0
    assert store.path.exists()
    assert [i.id for i in index.items] in ([1], [2])  # cache cũ đọc được, hoặc tải từ site
    # Trước T-042: khoảng 14 giây cho mỗi get. Giờ ~1,5 giây mỗi lần SQLite thử mở lại.
    assert elapsed < 15
    reread = store.load(BASE_URL)
    assert reread is not None and [i.id for i in reread.items] in ([1], [3])


@pytest.mark.skipif(sys.platform != "win32", reason="chế độ chia sẻ file chỉ có trên Windows")
def test_byte_locked_cache_get_reports_busy_without_second_wait(store):
    store.refresh(Source([published(1)]))
    close = _open(store.path, GENERIC_READ | GENERIC_WRITE,
                  SHARE_READ | SHARE_WRITE | SHARE_DELETE, lock_shared_bytes=True)
    try:
        start = time.monotonic()
        index = store.get(Source([published(2)]))
        elapsed = time.monotonic() - start
    finally:
        close()
    assert [i.id for i in index.items] == [2]
    assert "đang bận" in index.cache_error
    assert elapsed < 5  # một lần chờ ngắn, không phải 2 × 5 giây

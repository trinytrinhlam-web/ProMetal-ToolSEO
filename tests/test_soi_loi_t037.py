"""Soi Lỗi · T-037: thử phá ``list_published``, ``is_site_link`` và cache ``site_index``.

Lỗi chưa sửa đánh ``xfail(strict=True)`` kèm mã ``SL-T037-n`` (xem
``docs/team/reports/T-037-soi-loi.md``). Không gọi site thật: chỉ ``FakeWordPress`` hoặc nguồn giả.
"""

from __future__ import annotations

import ast
import os
import sqlite3
import stat
import subprocess
import sys
import threading
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pytest
from fake_wordpress import BASE_URL, make_session, query
from timing import assert_scales_linearly

import seo_app.storage.site_index as site_index
import seo_app.wordpress.client as client_module
from seo_app.config import PROJECT_ROOT
from seo_app.storage.site_index import SiteIndexStore
from seo_app.wordpress import PublishedItem, WordPressClient, is_site_link
from seo_app.wordpress.client import MAX_PAGES, PER_PAGE

SITE = "https://suachuacuasat.com"
TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def raw_item(id_, *, status="publish", link=None, title=None, meta=None):
    data = {
        "id": id_,
        "status": status,
        "slug": f"bai-{id_}",
        "link": link if link is not None else f"{BASE_URL}/bai-{id_}/",
        "title": {"rendered": title if title is not None else f"Bài {id_}"},
        "modified_gmt": "2026-10-01T03:04:05",
    }
    if meta is not None:
        data["meta"] = meta
    return data


def published(id_, kind="post"):
    return PublishedItem(
        id=id_,
        type=kind,
        slug=f"bai-{id_}",
        link=f"{BASE_URL}/bai-{id_}/",
        title=f"Bài {id_} – cửa sắt",
        meta_title=f"Meta {id_}",
        modified_gmt="2026-10-01T03:04:05",
    )


class Source:
    def __init__(self, items, base_url=BASE_URL):
        self.base_url = base_url
        self.items = items
        self.calls = 0

    def list_published(self):
        self.calls += 1
        return list(self.items)


@pytest.fixture
def store(tmp_path):
    return SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")


# ================================================================ 1. tiêu chí phiếu


@pytest.mark.parametrize("status", ["future", "draft", "private", "pending", "trash", "Publish"])
def test_only_publish_survives_each_status(fake_wp, wp_client, status):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", [raw_item(1), raw_item(2, status=status)])
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [raw_item(3, status=status)])
    assert [i.id for i in wp_client.list_published()] == [1]


def test_status_publish_sent_to_both_endpoints_get_only(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", [])
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    wp_client.list_published()
    assert [r.method for r in fake_wp.requests] == ["GET", "GET"]
    for request in fake_wp.requests:
        params = query(request)
        assert params["status"] == ["publish"]
        assert "context" not in params  # không xin context=edit
        assert request.body is None


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("<b>Cửa</b> &amp; <i>cổng</i>", "Cửa & cổng"),
        ("Giá&nbsp;rẻ&#8211;bền", "Giá\xa0rẻ–bền".replace("\xa0", " ")),
        ("<img src=x onerror=alert(1)>Bài", "Bài"),
        ("Dòng 1<br>\n\tDòng 2", "Dòng 1 Dòng 2"),
        ("&#x1b;[31mđỏ", "[31mđỏ"),
    ],
)
def test_title_html_and_entities_become_one_plain_line(fake_wp, wp_client, title, expected):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", [raw_item(1, title=title)])
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    (item,) = wp_client.list_published()
    assert item.title == expected
    assert "\x1b" not in item.title and "\n" not in item.title


@pytest.mark.parametrize("meta", [None, {}, [], "chuỗi", {"_siteseo_titles_title": None}])
def test_missing_meta_is_empty_not_error(fake_wp, wp_client, meta):
    data = raw_item(1)
    if meta is not None:
        data["meta"] = meta
    fake_wp.on("GET", "/wp-json/wp/v2/posts", [data])
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    (item,) = wp_client.list_published()
    assert (item.meta_title, item.meta_desc) == ("", "")


def test_many_pages_of_posts_and_pages(fake_wp, wp_client):
    def pager(offset):
        def handler(request):
            page = int(query(request)["page"][0])
            ids = range(offset + (page - 1) * 3 + 1, offset + page * 3 + 1)
            return 200, [raw_item(i) for i in ids], {"X-WP-TotalPages": "4"}

        return handler

    fake_wp.on("GET", "/wp-json/wp/v2/posts", pager(0))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", pager(1000))
    items = wp_client.list_published()
    assert len(items) == 24
    assert [i.type for i in items].count("page") == 12


# ================================================================ 2. thử phá is_site_link


@pytest.mark.parametrize(
    "link",
    [
        "https://suachuacuasat.com.evil.tld/",
        "https://suachuacuasat.com@evil.tld/",
        "https://evil.tld@suachuacuasat.com/",
        "https://user:pw@suachuacuasat.com/",
        "https://xn--suachuacuasat-9za.com/",
        "https://xn--suachuacuast-xyz.com/",
        "https://suachuacuasat.ⅽom/",  # chữ c La Mã: trình duyệt chuẩn hóa thành .com
        "https://suachuacuasat.com./bai/",  # dấu chấm cuối: từ chối (an toàn hơn nhận)
        "https://suachuacuasat.com:8443/",
        "https://suachuacuasat.com:80/",
        "https://suachuacuasat.com:99999/",
        "https://suachuacuasat.com:abc/",
        "https://suachuacuasat.com\\@evil.tld/",
        "https://suachuacuasat.com\\bai",
        "https:\\\\suachuacuasat.com\\bai",
        "javascript:alert(1)",
        "javascript://suachuacuasat.com/%0aalert(1)",
        "//evil.tld",
        "//suachuacuasat.com/bai",
        "/bai-viet/",
        "http://suachuacuasat.com/",
        "ftp://suachuacuasat.com/",
        "https:suachuacuasat.com/bai",
        "https:///suachuacuasat.com/",
        "https://sub.suachuacuasat.com/",
        "https://suachuacuasat.co/",
        "https://suachuacuasat.com%2eevil.tld/",
        "https://suachuacuasat.com​/",
        "https://suachuacuasat.com /",
        "https://suachuacuasat.com/\nSet-Cookie:x",
        "https://suachuacuasat.com/\x00",
        "https://[::1]/",
        "https://127.0.0.1/",
        "",
        None,
        123,
        b"https://suachuacuasat.com/",
        "https://suachuacuasat.com/" + "a" * 2001,
    ],
)
def test_is_site_link_rejects_attacks(link):
    assert is_site_link(link, SITE) is False


@pytest.mark.parametrize(
    "link",
    [
        "https://suachuacuasat.com/",
        "https://SUACHUACUASAT.COM/bai/",
        "HTTPS://suachuacuasat.com/bai/",
        "https://suachuacuasat.com:443/bai/",
        "https://suachuacuasat.com/?p=123",
        "https://suachuacuasat.com/s%E1%BB%ADa-c%E1%BB%ADa/",
        "https://suachuacuasat.com/bai#@evil.tld",  # @ sau dấu # là mảnh, không phải tên máy
    ],
)
def test_is_site_link_accepts_real_site_links(link):
    assert is_site_link(link, SITE) is True


def test_is_site_link_needs_https_base():
    assert is_site_link("https://suachuacuasat.com/", "http://suachuacuasat.com") is False


def test_bad_link_drops_item_not_whole_list(fake_wp, wp_client):
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/posts",
        [raw_item(1, link="https://example.com.evil.tld/x"), raw_item(2)],
    )
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [raw_item(3, link="javascript:alert(1)")])
    assert [i.id for i in wp_client.list_published()] == [2]


# ================================================================ 3. cache


def test_tampered_link_in_cache_drops_cache(store):
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE pages SET link = 'https://example.com.evil.tld/x'")
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1


def test_wrong_column_type_in_one_row_drops_cache(store):
    store.refresh(Source([published(1), published(2)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE pages SET id = 1.5 WHERE id = 2")
    assert store.load(BASE_URL) is None


def test_other_site_cache_is_not_returned_and_is_overwritten(store):
    store.refresh(Source([published(1)]))
    other = Source([], base_url="https://khac.example")
    assert store.load(other.base_url) is None
    index = store.get(other)
    assert other.calls == 1 and index.items == ()
    assert store.load(BASE_URL) is None  # cache cũ của site kia đã bị ghi đè


def test_stale_after_six_hours_reloads(store):
    source = Source([published(1)])
    first = store.get(source)
    assert store.get(source, now=first.fetched_at + timedelta(hours=5, minutes=59)).from_cache
    assert source.calls == 1
    store.get(source, now=first.fetched_at + timedelta(hours=6, seconds=1))
    assert source.calls == 2


def test_fetched_at_saved_with_vietnam_offset(store):
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn:
        (value,) = conn.execute("SELECT value FROM info WHERE key = 'fetched_at'").fetchone()
    assert value.endswith("+07:00")
    loaded = store.load(BASE_URL)
    assert loaded.fetched_at.utcoffset() == timedelta(hours=7)


def test_fetched_at_from_utc_machine_still_compares(store):
    store.refresh(Source([published(1)]))
    utc_now = datetime.now(ZoneInfo("UTC"))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute(
            "UPDATE info SET value = ? WHERE key = 'fetched_at'",
            ((utc_now - timedelta(hours=7)).isoformat(),),
        )
    assert store.is_stale(BASE_URL) is True
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute(
            "UPDATE info SET value = ? WHERE key = 'fetched_at'",
            ((utc_now - timedelta(hours=5)).isoformat(),),
        )
    assert store.is_stale(BASE_URL) is False


def test_unwritable_file_still_returns_list(store, monkeypatch):
    """Thư mục chỉ đọc: giả bằng sqlite3.connect lỗi (chạy bằng root thì chmod vô hiệu)."""

    def refuse(*_args, **_kwargs):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(site_index.sqlite3, "connect", refuse)
    source = Source([published(1)])
    index = store.get(source)
    assert [i.id for i in index.items] == [1]
    assert index.cache_error and "unable" not in index.cache_error


def test_two_refreshes_at_once_both_succeed(tmp_path):
    """Hai tab cùng bấm "Tải lại": không lỗi, không coi nhau là file hỏng, cache trọn vẹn."""
    path = tmp_path / "data" / "site_index.sqlite"
    sets = [[published(i) for i in range(1, 301)], [published(i) for i in range(1001, 1201)]]
    stores = [SiteIndexStore(path=path), SiteIndexStore(path=path)]
    errors: list[BaseException] = []
    results = []
    start = threading.Barrier(2)

    def run(n):
        try:
            start.wait()
            for _ in range(15):
                results.append(stores[n].refresh(Source(sets[n])))
        except BaseException as exc:  # pragma: no cover - chỉ để báo
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(n,)) for n in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert all(r.cache_error == "" for r in results)
    assert sum(s.reset_count for s in stores) == 0
    final = SiteIndexStore(path=path).load(BASE_URL)
    ids = [i.id for i in final.items]
    assert ids in ([i.id for i in sets[0]], [i.id for i in sets[1]])


def test_locked_file_is_busy_not_corrupt(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    holder = sqlite3.connect(store.path, isolation_level=None)
    try:
        holder.execute("BEGIN EXCLUSIVE")
        store.load(BASE_URL)
        # Mong đợi: file đang bận thì để yên (báo "đang bận"), không xóa.
        assert store.reset_count == 0
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert [i.id for i in store.load(BASE_URL).items] == [1]


@pytest.mark.parametrize("damage", ["garbage", "row", "clear"])
def test_every_connection_closed_before_delete(store, monkeypatch, damage):
    """Windows không xóa được file còn mở: mọi kết nối phải đóng trước khi xóa."""
    store.refresh(Source([published(1)]))
    if damage == "garbage":
        store.path.write_bytes(b"khong phai sqlite" * 100)
    elif damage == "row":
        with closing(sqlite3.connect(store.path)) as conn, conn:
            conn.execute("UPDATE pages SET type = 'attachment'")

    opened: list[sqlite3.Connection] = []
    real_connect = sqlite3.connect

    def tracking_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        opened.append(conn)
        return conn

    def still_open():
        alive = 0
        for conn in opened:
            try:
                conn.total_changes  # noqa: B018 - đóng rồi thì ném ProgrammingError
                alive += 1
            except sqlite3.ProgrammingError:
                pass
        return alive

    real_unlink = Path.unlink
    deletes = []

    def checking_unlink(self, *args, **kwargs):
        if self == store.path:
            deletes.append(still_open())
        return real_unlink(self, *args, **kwargs)

    monkeypatch.setattr(site_index.sqlite3, "connect", tracking_connect)
    monkeypatch.setattr(Path, "unlink", checking_unlink)
    if damage == "clear":
        store.load(BASE_URL)
        store.clear()
    else:
        assert store.load(BASE_URL) is None
    assert deletes and all(n == 0 for n in deletes)
    assert still_open() == 0


def test_delete_between_calls_recreates(store):
    source = Source([published(1)])
    store.get(source)
    store.path.unlink()
    assert store.get(source).items[0].id == 1
    assert source.calls == 2 and store.path.exists()


def test_journal_leftover_does_not_break(store):
    store.refresh(Source([published(1)]))
    journal = store.path.with_name(store.path.name + "-journal")
    journal.write_bytes(b"rac")
    loaded = store.load(BASE_URL)
    # File rác cạnh cache không làm app chết; hoặc đọc được, hoặc bỏ cache để tải lại.
    assert loaded is None or [i.id for i in loaded.items] == [1]


# ================================================================ 4. MAX_PAGES


def test_more_than_max_pages_is_cut_but_flagged(fake_wp, wp_client):
    """SL-T037-2 (đã sửa lượt 2): vẫn chỉ đọc ``MAX_PAGES`` trang nhưng có cờ ``truncated``."""

    def posts(request):
        page = int(query(request)["page"][0])
        start = (page - 1) * 2
        return 200, [raw_item(start + 1), raw_item(start + 2)], {"X-WP-TotalPages": "60"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == 2 * MAX_PAGES  # 20 mục của 10 trang cuối không được đọc
    assert items.truncated is True


def test_server_ignoring_per_page_gives_cache_error_not_crash(store):
    too_many = [published(i) for i in range(1, site_index.MAX_ITEMS + 2)]
    index = store.refresh(Source(too_many))
    assert len(index.items) == len(too_many)
    assert "quá dài" in index.cache_error


# ================================================================ 5. test chặn hàm "publish"


def _publish_names(names):
    return {n for n in names if "publish" in n.lower()}


def test_client_instance_publish_names_case_insensitive(wp_client):
    """Mạnh hơn test cũ: bắt cả ``Publish``/``PUBLISH``."""
    assert _publish_names(dir(wp_client)) == {"list_published"}


def test_client_module_publish_names_are_read_only_helpers():
    # PublishedList: kiểu kết quả chỉ đọc của list_published (T-037 lượt 2, SL-T037-2).
    allowed = {
        "PublishedItem",
        "PublishedList",
        "PUBLISHED_TYPES",
        "_PUBLISHED_FIELDS",
        "_published_from",
    }
    assert _publish_names(dir(client_module)) <= allowed


def test_name_check_would_catch_new_publish_methods():
    for name in ["publish_post", "_publish", "republish", "schedule_publish", "Publish_now"]:
        assert _publish_names(["list_published", name]) != {"list_published"}


def test_status_publish_or_future_only_in_list_published():
    """Khóa ``status`` khác ``draft`` (publish, future…) chỉ được nằm trong hàm đọc."""
    source = (PROJECT_ROOT / "seo_app" / "wordpress" / "client.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for node in ast.walk(func):
            values = []
            if isinstance(node, ast.Dict):
                values = [
                    v
                    for k, v in zip(node.keys, node.values, strict=True)
                    if isinstance(k, ast.Constant) and k.value == "status"
                ]
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.slice, ast.Constant)
                        and target.slice.value == "status"
                    ):
                        values.append(node.value)
            for value in values:
                if not (isinstance(value, ast.Constant) and value.value == "draft"):
                    offenders.append((func.name, ast.unparse(value)))
    assert offenders == [("list_published", "'publish'")]


# ================================================================ 6. tốc độ


def _client_with(n):
    from fake_wordpress import FakeWordPress

    fake = FakeWordPress()
    data = [raw_item(i, meta={"_siteseo_titles_title": f"Meta {i}"}) for i in range(1, n + 1)]

    def posts(request):
        page = int(query(request)["page"][0])
        total = max(1, -(-n // PER_PAGE))
        chunk = data[(page - 1) * PER_PAGE : page * PER_PAGE]
        return 200, chunk, {"X-WP-TotalPages": str(total)}

    fake.on("GET", "/wp-json/wp/v2/posts", posts)
    fake.on("GET", "/wp-json/wp/v2/pages", [])
    return WordPressClient(BASE_URL, "lam", "abcd", session=make_session(fake))


def test_list_published_5000_is_linear():
    clients = {k: _client_with(1250 * k) for k in (1, 4)}

    class Sized(list):
        pass

    def make(k):
        marker = Sized(range(1250 * k))
        marker.client = clients[k]
        return marker

    assert_scales_linearly(lambda m: m.client.list_published(), make, label="list_published")


def test_cache_save_load_5000_is_linear(tmp_path):
    def make(k):
        return [published(i) for i in range(1, 1250 * k + 1)]

    counter = iter(range(10**9))

    def round_trip(items):
        store = SiteIndexStore(path=tmp_path / f"c{next(counter)}.sqlite")
        store.refresh(Source(items))
        loaded = store.load(BASE_URL)
        assert len(loaded.items) == len(items)

    assert_scales_linearly(round_trip, make, label="cache 5000")


# ================================================================ Lượt 2 (sau khi Thợ Máy sửa)


def _paged(total, per=1):
    def handler(request):
        page = int(query(request)["page"][0])
        start = (page - 1) * per
        rows = [raw_item(start + i + 1) for i in range(per)]
        return 200, rows, {"X-WP-TotalPages": str(total)}

    return handler


@pytest.mark.parametrize(
    ("posts_total", "pages_total", "expected"),
    [
        (1, 1, False),
        (MAX_PAGES - 1, 1, False),
        (MAX_PAGES, MAX_PAGES, False),  # đúng bằng giới hạn: đủ, không bật
        (MAX_PAGES + 1, 1, True),
        (1, MAX_PAGES + 1, True),  # chỉ phía trang vượt cũng bật
        (10**9, 1, True),
    ],
)
def test_r2_truncated_flag_boundaries(fake_wp, wp_client, posts_total, pages_total, expected):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", _paged(posts_total))

    def pages(request):
        page = int(query(request)["page"][0])
        return 200, [raw_item(100000 + page)], {"X-WP-TotalPages": str(pages_total)}

    fake_wp.on("GET", "/wp-json/wp/v2/pages", pages)
    items = wp_client.list_published()
    assert items.truncated is expected
    assert len(fake_wp.requests) <= 2 * MAX_PAGES
    assert {r.method for r in fake_wp.requests} == {"GET"}


def test_r2_truncated_round_trips_through_cache(store, fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", _paged(MAX_PAGES + 5))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    fresh = store.get(wp_client)
    assert fresh.truncated is True and fresh.from_cache is False
    cached = store.get(wp_client)
    assert cached.from_cache is True and cached.truncated is True
    assert len(cached.items) == MAX_PAGES


def test_r2_not_truncated_round_trips_as_false(store):
    store.refresh(Source([published(1)]))  # nguồn trả list thường: không có cờ
    assert store.load(BASE_URL).truncated is False


def test_r2_truncated_kept_when_cache_cannot_be_written(store, monkeypatch):
    def refuse(*_args, **_kwargs):
        raise sqlite3.OperationalError("unable to open database file")

    items = client_module.PublishedList([published(1)])
    items.truncated = True

    class Direct(Source):
        def list_published(self):
            return self.items  # giữ nguyên PublishedList (list(...) sẽ làm mất cờ)

    monkeypatch.setattr(site_index.sqlite3, "connect", refuse)
    index = store.refresh(Direct(items))
    assert index.cache_error and index.truncated is True


@pytest.mark.parametrize("value", ["2", "true", "True", "", " 1", "1 ", "yes", "0.0", None])
def test_r2_odd_or_missing_truncated_value_drops_cache(store, value):
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        if value is None:
            conn.execute("DELETE FROM info WHERE key = 'truncated'")
        else:
            conn.execute("UPDATE info SET value = ? WHERE key = 'truncated'", (value,))
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1


def test_r2_truncated_integer_is_text_by_column_affinity(store):
    """Cột ``value`` kiểu TEXT: số 1 ghi tay thành chuỗi "1", đọc ra đúng (không phải lỗi)."""
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE info SET value = 1 WHERE key = 'truncated'")
    assert store.load(BASE_URL).truncated is True


def test_r2_schema_v1_cache_is_dropped_and_rebuilt(store):
    """Cache ghi ở lượt 1 (``schema_version`` 1, chưa có ``truncated``) bị bỏ và tạo lại."""
    store.refresh(Source([published(1)]))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE info SET value = '1' WHERE key = 'schema_version'")
        conn.execute("DELETE FROM info WHERE key = 'truncated'")
    source = Source([published(7)])
    index = store.get(source)
    assert source.calls == 1 and [i.id for i in index.items] == [7]
    assert store.reset_count == 1
    assert [i.id for i in store.load(BASE_URL).items] == [7]
    with closing(sqlite3.connect(store.path)) as conn:
        (version,) = conn.execute("SELECT value FROM info WHERE key = 'schema_version'").fetchone()
    assert version == site_index.SCHEMA_VERSION == "2"


def _hold_lock_with_journal(path):
    """Kết nối khác mở giao dịch ghi dở (có file -journal) và giữ khóa độc quyền."""
    holder = sqlite3.connect(path, isolation_level=None)
    holder.execute("BEGIN EXCLUSIVE")
    holder.execute("DELETE FROM pages")
    return holder


def test_r2_locked_file_and_journal_are_not_deleted(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    journal = store.path.with_name(store.path.name + "-journal")
    holder = _hold_lock_with_journal(store.path)
    try:
        assert journal.exists()
        inode = store.path.stat().st_ino
        journal_bytes = journal.read_bytes()
        assert store.load(BASE_URL) is None
        assert store.is_stale(BASE_URL) is True
        index = store.refresh(Source([published(2)]))
        assert [i.id for i in index.items] == [2]
        assert "bận" in index.cache_error
        assert store.reset_count == 0
        assert store.path.exists() and store.path.stat().st_ino == inode
        assert journal.exists() and journal.read_bytes() == journal_bytes
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    # Nhả khóa: giao dịch dở được hoàn tác, cache cũ đọc lại bình thường.
    loaded = store.load(BASE_URL)
    assert [i.id for i in loaded.items] == [1]
    assert store.reset_count == 0


def test_r2_after_lock_released_refresh_writes_normally(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    holder = _hold_lock_with_journal(store.path)
    try:
        assert store.refresh(Source([published(2)])).cache_error
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    index = store.refresh(Source([published(3)]))
    assert index.cache_error == ""
    assert [i.id for i in store.load(BASE_URL).items] == [3]


def test_r2_get_under_lock_raises_nothing(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    holder = _hold_lock_with_journal(store.path)
    try:
        source = Source([published(5)])
        index = store.get(source)  # không ném lỗi: tải từ site, báo cache đang bận
        assert source.calls == 1 and [i.id for i in index.items] == [5]
        assert "bận" in index.cache_error
    finally:
        holder.execute("ROLLBACK")
        holder.close()


def test_r2_real_corruption_still_resets(store):
    """Sửa SL-T037-1 không được làm mất việc dọn file hỏng thật."""
    store.refresh(Source([published(1)]))
    store.path.write_bytes(b"SQLite format 3\x00" + b"\xff" * 4096)
    assert store.load(BASE_URL) is None
    assert store.reset_count == 1
    assert store.refresh(Source([published(2)])).cache_error == ""


def test_r2_published_list_is_plain_read_only_data():
    """``PublishedList`` chỉ là ``list`` có thêm cờ ``truncated``: không có hàm nào mới."""
    cls = client_module.PublishedList
    assert issubclass(cls, list)
    extra = set(vars(cls)) - {"__module__", "__doc__", "__dict__", "__weakref__"}
    extra -= {"__annotations__", "__annotate__", "__annotate_func__", "__static_attributes__"}
    extra -= {"__firstlineno__", "__orig_bases__", "__qualname__"}
    assert extra == {"truncated"}
    assert cls.truncated is False
    assert not any(callable(getattr(cls, n)) for n in extra)


def test_r2_allowlist_still_blocks_other_names(monkeypatch):
    allowed_test = test_client_module_publish_names_are_read_only_helpers
    for name in ["publish_post", "PublishNow", "_publish_draft", "PublishedWriter"]:
        monkeypatch.setattr(client_module, name, lambda: None, raising=False)
        with pytest.raises(AssertionError):
            allowed_test()
        monkeypatch.delattr(client_module, name)
    allowed_test()


# ======================================== Lượt 2 (tiếp): khóa thật, quyền, phân trang

_HOLDER_SCRIPT = (
    "import sqlite3, sys\n"
    "conn = sqlite3.connect(sys.argv[1], isolation_level=None)\n"
    "conn.execute('BEGIN EXCLUSIVE')\n"
    "conn.execute('DELETE FROM pages')\n"
    "print('locked', flush=True)\n"
    "sys.stdin.readline()\n"
    "conn.execute('ROLLBACK')\n"
    "conn.close()\n"
)


def test_r2_lock_held_by_another_process_is_left_alone(store, monkeypatch):
    """SL-T037-1 với tiến trình khác thật (như DB Browser đang mở file, chưa lưu)."""
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    journal = store.path.with_name(store.path.name + "-journal")
    holder = subprocess.Popen(
        [sys.executable, "-c", _HOLDER_SCRIPT, str(store.path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout.readline().strip() == "locked"
        assert journal.exists()
        before = store.path.read_bytes()
        assert store.load(BASE_URL) is None
        index = store.get(Source([published(2)]))
        assert [i.id for i in index.items] == [2]
        assert "bận" in index.cache_error
        assert store.reset_count == 0
        assert store.path.read_bytes() == before
        assert journal.exists()
    finally:
        holder.communicate("\n", timeout=30)
    assert holder.returncode == 0
    assert [i.id for i in store.load(BASE_URL).items] == [1]
    assert store.reset_count == 0


def test_r2_short_lock_in_other_thread_is_waited_out(store):
    """Khóa ngắn hơn timeout (5 giây): chờ rồi đọc được, không báo bận, không xóa."""
    store.refresh(Source([published(1)]))
    locked, release = threading.Event(), threading.Event()
    errors: list[BaseException] = []

    def hold():
        try:
            conn = sqlite3.connect(store.path, isolation_level=None)
            conn.execute("BEGIN EXCLUSIVE")
            locked.set()
            release.wait(10)
            conn.execute("ROLLBACK")
            conn.close()
        except BaseException as exc:  # pragma: no cover - chỉ để báo
            errors.append(exc)
            locked.set()

    thread = threading.Thread(target=hold)
    thread.start()
    assert locked.wait(10)
    timer = threading.Timer(0.3, release.set)
    timer.start()
    try:
        loaded = store.load(BASE_URL)
    finally:
        release.set()
        timer.cancel()
        thread.join(10)
    assert errors == []
    assert loaded is not None and [i.id for i in loaded.items] == [1]
    assert store.reset_count == 0


def test_r2_long_lock_in_other_thread_is_busy_not_deleted(store, monkeypatch):
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    locked, release = threading.Event(), threading.Event()

    def hold():
        conn = sqlite3.connect(store.path, isolation_level=None)
        conn.execute("BEGIN EXCLUSIVE")
        conn.execute("DELETE FROM pages")
        locked.set()
        release.wait(10)
        conn.execute("ROLLBACK")
        conn.close()

    thread = threading.Thread(target=hold)
    thread.start()
    try:
        assert locked.wait(10)
        assert store.load(BASE_URL) is None
        assert store.is_stale(BASE_URL) is True
        assert "bận" in store.refresh(Source([published(2)])).cache_error
        with pytest.raises(site_index.SiteIndexError, match="bận"):
            store.save(store.refresh(Source([published(3)])))
    finally:
        release.set()
        thread.join(10)
    assert store.reset_count == 0
    assert [i.id for i in store.load(BASE_URL).items] == [1]


def test_r2_lock_taken_between_health_check_and_read(store, monkeypatch):
    """Kết nối khác chiếm khóa ngay sau ``_prepare`` (khe giữa kiểm và đọc): vẫn không xóa."""
    store.refresh(Source([published(1)]))
    monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)
    original = SiteIndexStore._prepare
    holders: list[sqlite3.Connection] = []

    def prepare_then_lock(self):
        original(self)
        holder = sqlite3.connect(self.path, isolation_level=None)
        holder.execute("BEGIN EXCLUSIVE")
        holders.append(holder)

    monkeypatch.setattr(SiteIndexStore, "_prepare", prepare_then_lock)
    try:
        assert store.load(BASE_URL) is None
        with pytest.raises(site_index.SiteIndexError, match="bận"):
            store.save(_index_of(published(2)))
    finally:
        for holder in holders:
            holder.execute("ROLLBACK")
            holder.close()
        monkeypatch.setattr(SiteIndexStore, "_prepare", original)
    assert store.reset_count == 0
    assert [i.id for i in store.load(BASE_URL).items] == [1]


def _index_of(*items):
    return site_index.SiteIndex(site=BASE_URL, fetched_at=datetime.now(TZ), items=items)


@pytest.fixture
def read_only_cache(store):
    """File cache chỉ đọc thật (Windows: thuộc tính Read-only; Mac/Linux: chmod 444)."""
    store.refresh(Source([published(1)]))
    os.chmod(store.path, stat.S_IREAD)
    try:
        if os.access(store.path, os.W_OK):  # chạy bằng root: chmod vô hiệu
            pytest.skip("máy này vẫn ghi được file chỉ đọc (root)")
        yield store
    finally:
        os.chmod(store.path, stat.S_IREAD | stat.S_IWRITE)


def test_r2_read_only_cache_is_read_and_kept(read_only_cache):
    store = read_only_cache
    assert [i.id for i in store.load(BASE_URL).items] == [1]
    index = store.refresh(Source([published(2)]))
    assert [i.id for i in index.items] == [2]  # vẫn dùng được danh sách vừa tải
    assert index.cache_error
    assert store.reset_count == 0
    assert [i.id for i in store.load(BASE_URL).items] == [1]  # cache cũ nguyên vẹn


def test_r2_read_only_old_schema_cache_does_not_crash(read_only_cache):
    """Cache cũ (schema 1) và chỉ đọc: không xóa được, không ghi được, vẫn không chết."""
    store = read_only_cache
    os.chmod(store.path, stat.S_IREAD | stat.S_IWRITE)
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE info SET value = '1' WHERE key = 'schema_version'")
    os.chmod(store.path, stat.S_IREAD)
    assert store.load(BASE_URL) is None
    source = Source([published(3)])
    index = store.get(source)
    assert source.calls == 1 and [i.id for i in index.items] == [3]
    # Windows không xóa được file chỉ đọc: báo không ghi được. Mac/Linux xóa được (thư mục
    # ghi được) nên tạo lại sạch. Cả hai đều không chết.
    os.chmod(store.path, stat.S_IREAD | stat.S_IWRITE)
    assert index.cache_error or [i.id for i in store.load(BASE_URL).items] == [3]


@pytest.mark.parametrize(
    "status",
    [
        " publish",
        "publish ",
        "PUBLISH",
        "publish\x00",
        "publіsh",
        ["publish"],
        None,
        1,
        True,
        {"raw": "publish"},
        "missing",
    ],
)
def test_r2_status_allowlist_is_exact_publish(fake_wp, wp_client, status):
    bad = raw_item(2, status=status)
    if status == "missing":
        del bad["status"]
    fake_wp.on("GET", "/wp-json/wp/v2/posts", [raw_item(1), bad])
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [dict(bad, id=3)])
    assert [i.id for i in wp_client.list_published()] == [1]


def test_r2_every_page_request_is_get_publish_on_fixed_paths(fake_wp, wp_client):
    """Phân trang mới (``_get_pages_checked``): mọi trang đều GET, ``status=publish``, lọc lại."""

    def posts(request):
        page = int(query(request)["page"][0])
        rows = [raw_item(page * 10 + 1)]
        if page == 2:
            rows += [
                raw_item(90, status="future"),
                raw_item(91, status="draft"),
                raw_item(92, link="https://example.com.evil.tld/x/"),
                raw_item(93, link="http://example.com/x/"),
            ]
        return 200, rows, {"X-WP-TotalPages": "3"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", _paged(2))
    items = wp_client.list_published()
    assert [(i.type, i.id) for i in items] == [
        ("post", 11),
        ("post", 21),
        ("post", 31),
        ("page", 1),
        ("page", 2),
    ]
    assert items.truncated is False
    assert len(fake_wp.requests) == 5
    paths = []
    for request in fake_wp.requests:
        assert request.method == "GET" and request.body is None
        params = query(request)
        assert params["status"] == ["publish"]
        assert "context" not in params
        assert params["_fields"] == [client_module._PUBLISHED_FIELDS]
        paths.append((urlsplit(request.url).path, params["page"][0]))
    assert paths == [
        ("/wp-json/wp/v2/posts", "1"),
        ("/wp-json/wp/v2/posts", "2"),
        ("/wp-json/wp/v2/posts", "3"),
        ("/wp-json/wp/v2/pages", "1"),
        ("/wp-json/wp/v2/pages", "2"),
    ]


@pytest.mark.parametrize("failure", [500, 401, "not-a-list"])
def test_r2_error_mid_pagination_keeps_old_cache(store, fake_wp, wp_client, failure):
    """Trang 2 lỗi: không ghi danh sách dở vào cache, cache cũ còn nguyên, lỗi báo lên."""
    store.refresh(Source([published(1)]))

    def posts(request):
        page = int(query(request)["page"][0])
        if page == 2:
            if failure == "not-a-list":
                return 200, {"code": "x"}, {"X-WP-TotalPages": "3"}
            return failure, {"code": "err", "message": "lỗi"}, {}
        return 200, [raw_item(page * 10)], {"X-WP-TotalPages": "3"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    later = datetime.now(TZ) + timedelta(hours=7)
    with pytest.raises(client_module.WordPressError):
        store.get(wp_client, now=later)
    assert [i.id for i in store.load(BASE_URL).items] == [1]
    assert store.reset_count == 0


@pytest.mark.parametrize("header", [None, "", "abc", "60.0"])
def test_r2_missing_total_pages_header_is_not_silently_complete(fake_wp, wp_client, header):
    """Proxy/plugin bỏ header ``X-WP-TotalPages`` mà trang đầy (100 mục): không được vừa thiếu
    mục vừa báo ``truncated=False`` (Giai đoạn 5 sẽ báo nhầm "link hỏng")."""

    def posts(request):
        page = int(query(request)["page"][0])
        rows = (
            [raw_item((page - 1) * PER_PAGE + k + 1) for k in range(PER_PAGE)] if page <= 3 else []
        )
        return 200, rows, {} if header is None else {"X-WP-TotalPages": header}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == 3 * PER_PAGE or items.truncated is True


@pytest.mark.skipif(sys.platform != "win32", reason="chế độ chia sẻ file chỉ có trên Windows")
def test_r2_file_opened_by_other_program_share_delete_is_not_deleted(store):
    """Chương trình khác mở file với chế độ chỉ cho xóa (không cho đọc/ghi): SQLite báo
    "unable to open", ``_is_healthy`` coi là hỏng và xóa được file người khác đang mở."""
    import ctypes
    from ctypes import wintypes

    store.refresh(Source([published(1)]))
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    generic_read, file_share_delete, open_existing = 0x80000000, 0x4, 3
    handle = kernel32.CreateFileW(
        str(store.path), generic_read, file_share_delete, None, open_existing, 0, None
    )
    assert handle not in (None, wintypes.HANDLE(-1).value), ctypes.get_last_error()
    try:
        store.load(BASE_URL)
        store.refresh(Source([published(2)]))
    finally:
        kernel32.CloseHandle(handle)
    assert store.reset_count == 0

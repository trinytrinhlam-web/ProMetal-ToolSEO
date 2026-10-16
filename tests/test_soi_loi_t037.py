"""Soi Lỗi · T-037: thử phá ``list_published``, ``is_site_link`` và cache ``site_index``.

Lỗi chưa sửa đánh ``xfail(strict=True)`` kèm mã ``SL-T037-n`` (xem
``docs/team/reports/T-037-soi-loi.md``). Không gọi site thật: chỉ ``FakeWordPress`` hoặc nguồn giả.
"""

from __future__ import annotations

import ast
import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
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


def test_more_than_max_pages_is_cut_silently(fake_wp, wp_client):
    """Ghi nhận hành vi hiện tại (SL-T037-2, đề xuất): bị cắt mà không có dấu hiệu nào."""

    def posts(request):
        page = int(query(request)["page"][0])
        start = (page - 1) * 2
        return 200, [raw_item(start + 1), raw_item(start + 2)], {"X-WP-TotalPages": "60"}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", posts)
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == 2 * MAX_PAGES  # 20 mục của 10 trang cuối bị bỏ, không báo


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

"""Soi Lỗi T-131 (rút gọn, phần 1–3): ``site_index``, ``plan_cache`` kiểm file như ``search_cache``.

- **SL-T131-1** (Thấp): ``plan_cache._prepare`` gỡ liên kết ở tên file nhật ký (``-journal``,
  ``-wal``, ``-shm``) **sau** bước kiểm file ``_is_healthy``, mà bước này đã mở file bằng SQLite.
  ``site_index`` và ``search_cache`` gỡ **trước** khi mở. Hậu quả đo được: file cache ở chế độ WAL
  có tên ``…-shm`` là hard link tới một file ngoài thì chỉ mở trang Kế hoạch là file ngoài bị cắt
  và ghi đè; tên ``…-wal``/``…-shm`` là junction (symlink trên Mac/Linux) thì cache kế hoạch kẹt
  mãi (đọc ra rỗng, ghi báo «Không mở được…», liên kết không bao giờ được gỡ).
- Chốt chặn (qua): ``data/`` là junction tới thư mục có file cache **hợp lệ** thì không một lần
  ``sqlite3.connect`` nào vào đó; file sửa tay kiểu lạ (UTF-8 hỏng, «unsupported file format», đầu
  file sai, file cụt, rác) không làm cache kẹt: lần đọc bỏ file, lần ghi sau ghi lại được.

Không gọi mạng; mọi file nằm trong ``tmp_path``. Liên kết thư mục: junction trên Windows (không cần
quyền quản trị), symlink trên Mac/Linux; hard link bằng ``os.link``.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from seo_app.images.data_dir import MSG_DATA_DIR_LINK, is_link
from seo_app.storage import plan_cache, search_cache, site_index
from seo_app.wordpress.client import PublishedItem

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
NOW = datetime(2026, 11, 7, 9, 0, tzinfo=TZ)
SITE = "https://suachuacuasat.com"
SHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-soi"
VALUES = (("Mã bài", "Từ khóa chính"), ("B-001", "sửa cửa cuốn"))
OUTSIDE_BYTES = b"FILE-NGOAI-DU-AN-" * 4000  # 68 KB, lớn hơn vùng chỉ mục WAL (32 KB)
SL_T131_1 = pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T131-1 (soi-loi, Thấp): plan_cache._prepare gỡ liên kết ở tên file nhật ký sau "
        "_is_healthy (đã mở file bằng SQLite); site_index, search_cache gỡ trước khi mở"
    ),
)
KINDS = [
    pytest.param("site-index", id="site-index"),
    pytest.param("plan-cache", id="plan-cache", marks=SL_T131_1),
    pytest.param("search-cache", id="search-cache-mau"),  # mẫu đối chiếu (T-122)
]


def published(post_id: int) -> PublishedItem:
    return PublishedItem(
        post_id, "post", f"bai-{post_id}", f"{SITE}/bai-{post_id}/", f"Bài {post_id}"
    )


class Source:
    base_url = SITE

    def __init__(self) -> None:
        self.calls = 0

    def list_published(self) -> list[PublishedItem]:
        self.calls += 1
        return [published(7)]


def link_dir(link: Path, target: Path) -> None:
    """Liên kết thư mục không cần quyền quản trị: junction trên Windows, symlink trên Mac/Linux."""
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def unlink_dir_link(link: Path) -> None:
    with contextlib.suppress(OSError):
        if os.name == "nt":
            os.rmdir(link)  # gỡ chính junction, không đụng thư mục đích
        else:
            os.unlink(link)


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "du-an"
    (root / "data").mkdir(parents=True)
    for module in (site_index, plan_cache, search_cache):
        monkeypatch.setattr(module, "PROJECT_ROOT", root)
    return root


class Kho:
    """Một kho với hai thao tác chung: ``read`` (đúng hàm trang gọi khi mở), ``write``."""

    def __init__(self, kind: str, path: Path) -> None:
        self.kind = kind
        self.path = path
        if kind == "site-index":
            self.store = site_index.SiteIndexStore(path=path)
        elif kind == "plan-cache":
            self.store = plan_cache.PlanCacheStore(path=path)
        else:
            self.store = search_cache.SearchCacheStore(path=path)
            self.scope = search_cache.CacheScope("sc-domain:suachuacuasat.com", SITE)

    def read(self):
        if self.kind == "site-index":
            return self.store.load(SITE)
        if self.kind == "plan-cache":
            return self.store.load(SHEET_ID)
        return self.store.load(self.scope)

    def write(self) -> None:
        if self.kind == "site-index":
            self.store.save(site_index.SiteIndex(SITE, NOW, (published(1),)))
        elif self.kind == "plan-cache":
            self.store.save(SHEET_ID, VALUES, NOW)
        else:
            self.read()  # kho số liệu: mở là tạo file, tạo bảng

    def has_data(self, value) -> bool:
        if self.kind == "site-index":
            return value is not None and [item.id for item in value.items] == [1]
        if self.kind == "plan-cache":
            return value is not None and value.values == VALUES
        return value is None  # kho số liệu chưa ghi số nào: đọc ra None, không lỗi


def make_store(project: Path, kind: str) -> Kho:
    return Kho(kind, project / "data" / f"{kind}.sqlite")


def to_wal(path: Path) -> None:
    """Đổi file sang chế độ WAL (byte 18, 19 của đầu file = 2), như một chương trình khác làm."""
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
    assert path.read_bytes()[18:20] == b"\x02\x02"
    for end in ("-wal", "-shm"):  # SQLite tự xóa khi đóng kết nối cuối
        assert not path.with_name(path.name + end).exists()


def hard_link_or_skip(target: Path, link: Path) -> None:
    try:
        os.link(target, link)
    except OSError:
        pytest.skip("ổ này không cho tạo hard link")


# ================================================================ SL-T131-1


@pytest.mark.parametrize("kind", KINDS)
def test_sl_t131_1_wal_index_hard_link_is_never_written_through(project, tmp_path, kind):
    """File cache ở chế độ WAL, tên ``…-shm`` là hard link tới file ngoài dự án: mở kho để đọc
    không được ghi gì vào file ngoài. Bản lỗi: SQLite mở ``-shm`` trong ``_is_healthy`` (trước khi
    kho gỡ liên kết), cắt file ngoài còn 32 KB và ghi chỉ mục WAL vào đó."""
    kho = make_store(project, kind)
    kho.write()
    to_wal(kho.path)
    outside = tmp_path / "ngoai" / "tai-lieu.bin"
    outside.parent.mkdir()
    outside.write_bytes(OUTSIDE_BYTES)
    shm = kho.path.with_name(kho.path.name + "-shm")
    hard_link_or_skip(outside, shm)
    kho.read()
    assert outside.read_bytes() == OUTSIDE_BYTES
    assert not shm.exists() or os.lstat(shm).st_nlink == 1


@pytest.mark.parametrize("suffix", ["-journal", "-wal", "-shm"])
@pytest.mark.parametrize("kind", KINDS)
def test_sl_t131_1_linked_journal_name_is_removed_before_sqlite_opens(
    project, tmp_path, monkeypatch, kind, suffix
):
    """Tên file nhật ký là liên kết thư mục (junction, symlink): kho gỡ liên kết **trước** mọi lần
    SQLite mở file cache, rồi chạy bình thường. Bản lỗi: mở file khi liên kết còn đó; với file WAL
    thì kẹt mãi (đọc ra rỗng, ghi báo «Không mở được…», liên kết còn nguyên)."""
    kho = make_store(project, kind)
    kho.write()
    if suffix != "-journal":
        to_wal(kho.path)
    outside = tmp_path / "ngoai"
    outside.mkdir()
    (outside / "giu.txt").write_bytes(b"giu nguyen")
    link = kho.path.with_name(kho.path.name + suffix)
    link_dir(link, outside)
    journals = [kho.path.with_name(kho.path.name + end) for end in ("-journal", "-wal", "-shm")]
    opened_while_linked: list[str] = []
    real_connect = sqlite3.connect

    def spy(database, *args, **kwargs):
        if Path(str(database)) == kho.path:
            opened_while_linked.extend(p.name for p in journals if is_link(p))
        return real_connect(database, *args, **kwargs)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(sqlite3, "connect", spy)
            kho.read()
        assert opened_while_linked == []
        assert not os.path.lexists(link)
        kho.write()  # ghi được (bản lỗi: «Không mở được file lưu tạm…» mãi)
        assert kho.has_data(kho.read())
    finally:
        if os.path.lexists(link):
            unlink_dir_link(link)
    assert sorted(path.name for path in outside.iterdir()) == ["giu.txt"]
    assert (outside / "giu.txt").read_bytes() == b"giu nguyen"


# ================================================================ chốt chặn (qua)


def snapshot(folder: Path) -> dict[str, tuple[str, int]]:
    return {
        path.name: (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
        for path in sorted(folder.iterdir())
    }


def test_data_link_to_valid_caches_is_never_opened(project, tmp_path, monkeypatch):
    """``data/`` là liên kết tới thư mục có sẵn file cache **hợp lệ** (người dùng dời ``data/`` sang
    ổ khác rồi đặt lối tắt): không một lần ``sqlite3.connect`` nào vào đó, không đổi tên, nội dung,
    giờ sửa của file nào; danh sách vừa tải vẫn dùng được, câu báo cố định."""
    outside = tmp_path / "o-khac" / "data-cu"
    outside.mkdir(parents=True)
    site_index.SiteIndexStore(path=outside / "site_index.sqlite").save(
        site_index.SiteIndex(SITE, NOW, (published(1),))
    )
    plan_cache.PlanCacheStore(path=outside / "plan_cache.sqlite").save(SHEET_ID, VALUES, NOW)
    before = snapshot(outside)
    (project / "data").rmdir()
    link_dir(project / "data", outside)
    opened: list[str] = []
    real_connect = sqlite3.connect

    def spy(database, *args, **kwargs):
        opened.append(str(database))
        return real_connect(database, *args, **kwargs)

    index_store = site_index.SiteIndexStore(path=project / "data" / "site_index.sqlite")
    plan_store = plan_cache.PlanCacheStore(path=project / "data" / "plan_cache.sqlite")
    source = Source()
    refused = (
        (lambda: index_store.save(site_index.SiteIndex(SITE, NOW, ())), site_index.SiteIndexError),
        (index_store.clear, site_index.SiteIndexError),
        (lambda: plan_store.save(SHEET_ID, VALUES, NOW), plan_cache.PlanCacheError),
        (plan_store.clear, plan_cache.PlanCacheError),
    )
    try:
        with monkeypatch.context() as patch:
            patch.setattr(sqlite3, "connect", spy)
            assert index_store.load(SITE) is None and index_store.is_stale(SITE)
            for index in (index_store.get(source), index_store.refresh(source)):
                assert [item.id for item in index.items] == [7]
                assert index.cache_error == MSG_DATA_DIR_LINK
            listing = site_index.site_listing(index_store, source)
            assert listing.index is not None and MSG_DATA_DIR_LINK in listing.notice
            assert plan_store.load(SHEET_ID) is None
            for action, error in refused:
                with pytest.raises(error) as caught:
                    action()
                assert str(caught.value) == MSG_DATA_DIR_LINK
    finally:
        unlink_dir_link(project / "data")
    assert [name for name in opened if name != ":memory:"] == []
    assert index_store.reset_count == plan_store.reset_count == 0
    assert snapshot(outside) == before


def _set_bytes(offset: int, value: bytes):
    def damage(path: Path) -> None:
        data = bytearray(path.read_bytes())
        data[offset : offset + len(value)] = value
        path.write_bytes(bytes(data))

    return damage


def _bad_utf8_in_master(path: Path) -> None:
    """Chữ trong ``sqlite_master`` không phải UTF-8 (SQLite vẫn đọc được câu lệnh)."""
    with closing(sqlite3.connect(path)) as conn:
        (sql,) = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'info'").fetchone()
        broken = sql.encode("utf-8").replace(b"value", b"val" + bytes([0xFF]) + b"e", 1)
        assert broken != sql.encode("utf-8")
        conn.execute("PRAGMA writable_schema = ON")
        conn.execute(
            "UPDATE sqlite_master SET sql = CAST(? AS TEXT) WHERE name = 'info'", (broken,)
        )
        conn.commit()


DAMAGES = {
    "utf8-master": _bad_utf8_in_master,
    "unsupported-format": _set_bytes(44, (5).to_bytes(4, "big")),  # «schema format» 5
    "ban-ghi-3": _set_bytes(19, b"\x03"),  # phiên bản ghi lạ
    "co-trang-sai": _set_bytes(16, b"\x03\x00"),
    "cut-nua": lambda path: path.write_bytes(path.read_bytes()[: len(path.read_bytes()) // 2]),
    "rac": lambda path: path.write_bytes(b"khong phai sqlite " * 100),
}


@pytest.mark.parametrize("damage", list(DAMAGES), ids=list(DAMAGES))
@pytest.mark.parametrize("kind", ["site-index", "plan-cache"])
def test_hand_edited_file_never_leaves_the_cache_stuck(project, kind, damage):
    """Mẫu LC-T122-1 cho cả hai kho, thêm các kiểu sửa tay khác: lần đọc ra ``None`` (bỏ file), lần
    ghi sau ghi được, lần đọc tiếp có đúng dữ liệu (trước T-131, hai kiểu đầu làm kho kẹt mãi)."""
    kho = make_store(project, kind)
    kho.write()
    DAMAGES[damage](kho.path)
    assert kho.read() is None
    assert kho.store.reset_count == 1
    kho.write()
    assert kho.has_data(kho.read())

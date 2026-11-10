"""T-131 lượt 2 (Thợ Máy): kho nháp (``drafts.py``) kiểm file như ``search_cache``, kho thẻ ảnh.

- SL-T117-1: ``data/`` là liên kết thì kho nháp không tạo, không mở, không đổi tên gì.
- LC-T129-1 (rà kho nháp cùng kiểu): ``sqlite_master`` phải khớp đúng các bảng app tạo, kiểm trước
  khi dùng file và trong cùng giao dịch với mỗi thao tác; ``trusted_schema = OFF``, trần số bước,
  trần độ dài. Tên file nhật ký là liên kết thì gỡ, chỗ đặt file là liên kết thì đổi tên sang một
  bên, **trước** mọi lần SQLite mở file (bài học SL-T131-1).
- Phiếu yêu cầu 4: kho giữ khóa chống gửi trùng (T-086, T-089, T-092, T-130), nên **không làm mất
  trạng thái gửi**: file nháp cũ (trước T-086, trước T-100) mở được, giữ nguyên; file lạ, hỏng thì
  đổi tên sang một bên (giữ lại), không xóa; file bận thì báo, không đổi tên.

Liên kết thật: junction trên Windows (không cần quyền quản trị), symlink trên Mac/Linux; hard link
bằng ``os.link``. Không gọi mạng; mọi file nằm trong ``tmp_path``.
"""

from __future__ import annotations

import contextlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from seo_app.images.data_dir import MSG_DATA_DIR_LINK, is_link
from seo_app.storage import drafts
from seo_app.storage.drafts import DraftError, DraftSnapshot, DraftStore, SendState

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
BUSY = "File nháp đang bận (có thể app mở ở tab khác đang lưu). Thử lại sau giây lát."
BROKEN = "File nháp bị lỗi nên không đọc/ghi được. Thử tải lại trang."
OUTSIDE_BYTES = b"FILE-NGOAI-DU-AN-" * 4000  # 68 KB, lớn hơn vùng chỉ mục WAL (32 KB)
# Câu tạo bảng của các bản trước, chép nguyên văn (T-016, T-086, T-100): file cũ phải dùng tiếp.
OLD_DRAFTS = (
    "CREATE TABLE IF NOT EXISTS drafts ("
    "id TEXT PRIMARY KEY, title TEXT NOT NULL, keyword TEXT NOT NULL, "
    "saved_at TEXT NOT NULL, saved_ts REAL NOT NULL, data TEXT NOT NULL)"
)
OLD_SEND_STATES = "CREATE TABLE IF NOT EXISTS send_states (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
OLD_PLAN_WRITES = (
    "CREATE TABLE IF NOT EXISTS plan_writes ("
    "id TEXT PRIMARY KEY, data TEXT NOT NULL, saved_ts REAL NOT NULL)"
)
OLD_SHAPES = {
    "t016": (OLD_DRAFTS,),
    "t086": (OLD_DRAFTS, OLD_SEND_STATES),
    "t100": (OLD_DRAFTS, OLD_SEND_STATES, OLD_PLAN_WRITES),
}


# ------------------------------------------------------------------ dụng cụ


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


def hard_link_or_skip(target: Path, link: Path) -> None:
    try:
        os.link(target, link)
    except OSError:
        pytest.skip("ổ này không cho tạo hard link")


def raw_sql(path: Path, *statements: str) -> None:
    with closing(sqlite3.connect(path)) as conn, conn:
        for sql in statements:
            conn.execute(sql)


def rows(path: Path, sql: str) -> list[tuple]:
    with closing(sqlite3.connect(path)) as conn:
        return conn.execute(sql).fetchall()


def names_in(path: Path) -> set[str]:
    return {name for (name,) in rows(path, "SELECT name FROM sqlite_master WHERE type = 'table'")}


def moved_files(folder: Path) -> list[str]:
    return sorted(path.name for path in folder.iterdir() if ".hong-" in path.name)


def snapshot(folder: Path) -> dict[str, tuple[int, bytes]]:
    return {path.name: (path.stat().st_size, path.read_bytes()) for path in folder.iterdir()}


def sent(post_id: int = 501) -> SendState:
    return SendState.now(pending=False, post_id=post_id)


def seeded(path: Path) -> tuple[str, SendState]:
    """File nháp hợp lệ (tạo bằng kho hiện tại): một nháp, một trạng thái «đã gửi»."""
    store = DraftStore(path=path)
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    state = sent()
    store.save_send_state(snap.id, state)
    return snap.id, state


def old_file(path: Path, shape: str) -> tuple[str, SendState | None]:
    """File nháp do bản cũ tạo: đúng câu tạo bảng của bản đó, một nháp, và trạng thái gửi nếu bản
    đó có bảng ``send_states``."""
    raw_sql(path, *OLD_SHAPES[shape])
    snap = DraftSnapshot(keyword="nháp cũ", saved_at=datetime(2026, 10, 20, 9, 0, tzinfo=TZ))
    assert snap.saved_at is not None
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute(
            "INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?)",
            (
                snap.id,
                snap.title,
                snap.keyword,
                snap.saved_at.isoformat(),
                snap.saved_at.timestamp(),
                snap.model_dump_json(),
            ),
        )
        state = None
        if shape != "t016":
            state = sent(77)
            conn.execute(
                "INSERT INTO send_states VALUES (?, ?)", (snap.id, state.model_dump_json())
            )
    return snap.id, state


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả; ``PROJECT_ROOT`` của kho nháp trỏ vào đó."""
    root = tmp_path / "du-an"
    (root / "data").mkdir(parents=True)
    monkeypatch.setattr(drafts, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def path(project: Path) -> Path:
    return project / "data" / "drafts.sqlite"


class ConnectSpy:
    """Ghi mọi lần ``sqlite3.connect`` (đường dẫn), và tên file nhật ký còn là liên kết lúc mở."""

    def __init__(self, monkeypatch, watched: Path | None = None) -> None:
        self.paths: list[Path] = []
        self.linked_at_open: list[str] = []
        self.watched = watched
        real = sqlite3.connect

        def spy(database, *args, **kwargs):
            opened = Path(str(database))
            self.paths.append(opened)
            if self.watched is not None and opened == self.watched:
                self.linked_at_open += [p.name for p in drafts._journal_paths(opened) if is_link(p)]
            return real(database, *args, **kwargs)

        monkeypatch.setattr(sqlite3, "connect", spy)


# ================================================================ 1. không làm mất trạng thái gửi


@pytest.mark.parametrize("shape", list(OLD_SHAPES), ids=list(OLD_SHAPES))
def test_file_nhap_cu_mo_duoc_giu_nguyen_trang_thai_gui(path, shape):
    """File nháp tạo bởi bản trước T-086 (chỉ bảng ``drafts``), trước T-100 (chưa có
    ``plan_writes``), và bản T-100 → T-130: không bị coi là lạ, không đổi tên; nháp, trạng thái gửi
    còn nguyên; bảng còn thiếu được tạo thêm, đúng câu của app."""
    draft_id, state = old_file(path, shape)
    store = DraftStore(path=path)
    assert store.load(draft_id).keyword == "nháp cũ"
    assert store.load_send_state(draft_id) == state
    assert store.send_state_if_exists(draft_id) == (state, False)
    assert store.recovered_from is None and moved_files(path.parent) == []
    assert names_in(path) == {"drafts", "send_states", "plan_writes"}
    with closing(sqlite3.connect(":memory:")) as memory:
        for sql in OLD_SHAPES["t100"]:
            memory.execute(sql)
        expected = set(memory.execute("SELECT type, name, tbl_name, sql FROM sqlite_master"))
    assert set(rows(path, "SELECT type, name, tbl_name, sql FROM sqlite_master")) == expected
    newer = sent(9)
    assert store.save_send_state(draft_id, newer, expected=(state, False))
    assert DraftStore(path=path).load_send_state(draft_id) == newer


def test_trang_thai_gui_con_nguyen_qua_lan_mo_lai(path):
    """Kho mới (app chạy lại) đọc đúng nháp, trạng thái gửi, dòng mồ côi (T-130) của kho cũ."""
    draft_id, state = seeded(path)
    store = DraftStore(path=path)
    orphan = store.save(DraftSnapshot(keyword="sẽ xóa"))
    store.save_send_state(orphan.id, sent(8))
    assert store.delete(orphan.id)
    again = DraftStore(path=path)
    assert again.load_send_state(draft_id) == state
    assert again.load_send_state(orphan.id) is not None  # dòng mồ côi giữ khóa (T-130)
    assert again.recovered_from is None and moved_files(path.parent) == []


def test_nhap_gan_tran_kich_thuoc_van_mo_duoc(path):
    """Một nháp gần ``MAX_DRAFT_BYTES`` (5 MB): trần độ dài giá trị của kết nối còn rộng."""
    store = DraftStore(path=path)
    saved = store.save(DraftSnapshot(keyword="nháp lớn", material={"kinh_nghiem": "x" * 4_900_000}))
    again = DraftStore(path=path)
    assert len(again.load(saved.id).material["kinh_nghiem"]) == 4_900_000
    assert again.recovered_from is None


def test_file_ban_luc_kiem_khong_bi_doi_ten(path, monkeypatch):
    """File đang bị chương trình khác khóa đúng lúc kho mở lần đầu: báo «đang bận», **không** đổi
    tên file (trước T-131: lỗi khóa bị coi là file hỏng, file bị cất sang một bên cùng mọi trạng
    thái gửi trong đó, hay ra câu lỗi đổi tên trên Windows)."""
    draft_id, state = seeded(path)
    monkeypatch.setattr(drafts, "_SQLITE_TIMEOUT", 0.2)
    other = sqlite3.connect(path, isolation_level=None)
    try:
        other.execute("BEGIN EXCLUSIVE")
        store = DraftStore(path=path)
        with pytest.raises(DraftError) as caught:
            store.list_drafts()
        assert str(caught.value) == BUSY
        assert store.recovered_from is None and moved_files(path.parent) == []
    finally:
        other.execute("ROLLBACK")
        other.close()
    assert store.load_send_state(draft_id) == state
    assert store.recovered_from is None


# ================================================================ 2. cấu trúc lạ


FOREIGN = {
    "trigger-xoa-khoa": (
        "CREATE TRIGGER t AFTER INSERT ON drafts BEGIN DELETE FROM send_states; END"
    ),
    "trigger-sua-khoa": (
        "CREATE TRIGGER t AFTER UPDATE ON drafts BEGIN UPDATE send_states SET data = '{}'; END"
    ),
    "khung-nhin": "CREATE VIEW v AS SELECT * FROM drafts",
    "bang-la": "CREATE TABLE la (x TEXT)",
    "chi-muc": "CREATE INDEX i ON drafts (keyword)",
    "analyze": "ANALYZE",
}


@pytest.mark.parametrize("sql", FOREIGN.values(), ids=FOREIGN.keys())
def test_cau_truc_la_thi_doi_ten_sang_mot_ben_trigger_khong_chay(path, sql):
    """Bảng, khung nhìn, trigger, chỉ mục lạ (chương trình khác cài vào): file đổi tên sang một bên
    (giữ lại), app dùng file mới; không câu SQL nào của app chạy trên file lạ, nên trigger xóa khóa
    gửi trùng không bao giờ chạy (trạng thái gửi trong file cũ còn nguyên)."""
    draft_id, state = seeded(path)
    raw_sql(path, sql)
    store = DraftStore(path=path)
    fresh = store.save(DraftSnapshot(keyword="nháp mới"))
    assert store.recovered_from is not None and store.recovered_from.parent == path.parent
    assert [d.id for d in store.list_drafts().drafts] == [fresh.id]
    kept = rows(store.recovered_from, "SELECT id, data FROM send_states")
    assert kept == [(draft_id, state.model_dump_json())]


SAME_COLUMNS_OTHER_TEXT = {
    "them-cot": OLD_DRAFTS[:-1] + ", them TEXT)",
    "khong-rowid": OLD_DRAFTS + " WITHOUT ROWID",
    "khac-chu": OLD_DRAFTS.replace("IF NOT EXISTS drafts (", "IF NOT EXISTS drafts("),
    "check": OLD_DRAFTS[:-1] + ", CHECK (length(data) > 0))",
}


@pytest.mark.parametrize("sql", SAME_COLUMNS_OTHER_TEXT.values(), ids=SAME_COLUMNS_OTHER_TEXT)
def test_bang_khac_cau_tao_la_file_la(path, sql):
    """App chỉ từng tạo bảng bằng đúng ba câu (mọi bản): câu khác (thêm cột, ``WITHOUT ROWID``,
    ``CHECK``, khác chữ dù cùng cột) là file lạ."""
    raw_sql(path, sql)
    store = DraftStore(path=path)
    store.list_drafts()
    assert store.recovered_from is not None


def test_utf8_hong_trong_sqlite_master_la_file_la(path):
    """Như LC-T122-1: chữ trong ``sqlite_master`` không phải UTF-8 thì là file lạ (đổi tên, dùng
    file mới), không phải lỗi giải mã làm kho kẹt."""
    seeded(path)
    with closing(sqlite3.connect(path)) as conn:
        (sql,) = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'drafts'").fetchone()
        broken = sql.encode("utf-8").replace(b"keyword", b"keyw" + bytes([0xFF]) + b"rd", 1)
        conn.execute("PRAGMA writable_schema = ON")
        conn.execute(
            "UPDATE sqlite_master SET sql = CAST(? AS TEXT) WHERE name = 'drafts'", (broken,)
        )
        conn.commit()
    store = DraftStore(path=path)
    saved = store.save(DraftSnapshot(keyword="mới"))
    assert store.recovered_from is not None
    assert store.load(saved.id).keyword == "mới"


def test_file_bi_cai_trigger_khi_dang_chay_thi_khong_ghi(path):
    """File bị cài trigger khi app đang chạy (kho đã mở): lần ghi kế tiếp bị chặn ngay trong giao
    dịch, chưa ghi gì (trigger không chạy); lần mở sau đổi tên file lạ sang một bên."""
    draft_id, state = seeded(path)
    store = DraftStore(path=path)
    assert store.load_send_state(draft_id) == state  # kho đã sẵn sàng
    raw_sql(path, FOREIGN["trigger-xoa-khoa"])
    with pytest.raises(DraftError) as caught:
        store.save(DraftSnapshot(keyword="ghi khi file lạ"))
    assert str(caught.value) == BROKEN
    assert rows(path, "SELECT id FROM send_states") == [(draft_id,)]
    assert len(rows(path, "SELECT id FROM drafts")) == 1
    store.list_drafts()
    assert store.recovered_from is not None
    assert rows(store.recovered_from, "SELECT id FROM send_states") == [(draft_id,)]


@pytest.mark.parametrize(
    "operation",
    ["save", "save_send_state", "send_state_if_exists", "load", "delete", "list_plan_writes"],
)
def test_kiem_cau_truc_trong_cung_giao_dich_voi_thao_tac(path, monkeypatch, operation):
    """Khe giữa lần kiểm file (``_prepare``) và thao tác: file bị cài trigger đúng lúc đó vẫn bị
    bắt trong giao dịch của thao tác, trước câu SQL đầu tiên của thao tác."""
    draft_id, state = seeded(path)
    store = DraftStore(path=path)
    store.list_drafts()
    original = store._prepare

    def prepare_then_tamper() -> None:
        original()
        raw_sql(path, FOREIGN["trigger-xoa-khoa"])

    monkeypatch.setattr(store, "_prepare", prepare_then_tamper)
    calls = {
        "save": lambda: store.save(DraftSnapshot(keyword="x")),
        "save_send_state": lambda: store.save_send_state(
            draft_id, sent(3), expected=(state, False)
        ),
        "send_state_if_exists": lambda: store.send_state_if_exists(draft_id),
        "load": lambda: store.load(draft_id),
        "delete": lambda: store.delete(draft_id),
        "list_plan_writes": store.list_plan_writes,
    }
    with pytest.raises(DraftError) as caught:
        calls[operation]()
    assert str(caught.value) == BROKEN
    assert rows(path, "SELECT id, data FROM send_states") == [(draft_id, state.model_dump_json())]
    assert rows(path, "SELECT id FROM drafts") == [(draft_id,)]


# ================================================================ 3. liên kết


def test_data_la_lien_ket_khong_mo_khong_ghi_khong_doi_ten(project, tmp_path, monkeypatch):
    """``data/`` là junction (symlink) tới thư mục có sẵn file nháp **hợp lệ**: mọi thao tác báo câu
    cố định, 0 lần SQLite mở file ở đó, không tạo, không đổi tên, không xóa gì (SL-T117-1)."""
    outside = tmp_path / "o-khac"
    outside.mkdir()
    draft_id, _state = seeded(outside / "drafts.sqlite")
    before = snapshot(outside)
    data = project / "data"
    data.rmdir()
    link_dir(data, outside)
    try:
        spy = ConnectSpy(monkeypatch)
        store = DraftStore(path=data / "drafts.sqlite")
        for call in (
            store.list_drafts,
            lambda: store.save(DraftSnapshot()),
            lambda: store.load(draft_id),
            lambda: store.load_send_state(draft_id),
            lambda: store.save_send_state(draft_id, sent()),
            lambda: store.delete(draft_id),
            store.list_plan_writes,
        ):
            with pytest.raises(DraftError) as caught:
                call()
            assert str(caught.value) == MSG_DATA_DIR_LINK
        assert spy.paths == []
        assert store.recovered_from is None
    finally:
        unlink_dir_link(data)
    assert snapshot(outside) == before


def test_cho_dat_file_la_hard_link_thi_doi_ten_khong_ghi_xuyen(path, tmp_path):
    """``data/drafts.sqlite`` là hard link tới một file nháp hợp lệ ngoài dự án: kho không mở nó,
    đổi tên chính tên đó sang một bên (giữ lại, báo người dùng), tạo file mới; file ngoài nguyên
    vẹn."""
    outside = tmp_path / "ngoai" / "drafts.sqlite"
    outside.parent.mkdir()
    seeded(outside)
    before = outside.read_bytes()
    hard_link_or_skip(outside, path)
    store = DraftStore(path=path)
    saved = store.save(DraftSnapshot(keyword="trong dự án"))
    assert store.recovered_from is not None and moved_files(path.parent) != []
    assert os.lstat(path).st_nlink == 1
    assert [d.id for d in store.list_drafts().drafts] == [saved.id]
    assert outside.read_bytes() == before


def test_cho_dat_file_la_junction_thi_doi_ten_khong_dung_dich(path, tmp_path):
    """Chỗ đặt file là junction (symlink) tới thư mục ngoài: đổi tên chính liên kết, thư mục đích
    không bị đụng, kho dùng file mới."""
    outside = tmp_path / "thu-muc-ngoai"
    outside.mkdir()
    (outside / "giu.txt").write_bytes(b"giu nguyen")
    link_dir(path, outside)
    store = DraftStore(path=path)
    try:
        saved = store.save(DraftSnapshot(keyword="mới"))
        assert store.recovered_from is not None and is_link(store.recovered_from)
        assert not is_link(path) and store.load(saved.id).keyword == "mới"
    finally:
        if store.recovered_from is not None:
            unlink_dir_link(store.recovered_from)
    assert sorted(p.name for p in outside.iterdir()) == ["giu.txt"]


def to_wal(path: Path) -> None:
    """Đổi file sang chế độ WAL (byte 18, 19 của đầu file = 2), như một chương trình khác làm."""
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
    assert path.read_bytes()[18:20] == b"\x02\x02"


def test_shm_la_hard_link_khong_bao_gio_ghi_xuyen(path, tmp_path):
    """Như SL-T131-1 (``plan_cache``): file nháp ở chế độ WAL, tên ``…-shm`` là hard link tới file
    ngoài dự án: mở kho không ghi gì vào file ngoài (gỡ liên kết trước khi SQLite mở file)."""
    draft_id, state = seeded(path)
    to_wal(path)
    outside = tmp_path / "ngoai" / "tai-lieu.bin"
    outside.parent.mkdir()
    outside.write_bytes(OUTSIDE_BYTES)
    shm = path.with_name(path.name + "-shm")
    hard_link_or_skip(outside, shm)
    store = DraftStore(path=path)
    assert store.load_send_state(draft_id) == state
    assert outside.read_bytes() == OUTSIDE_BYTES
    assert not shm.exists() or os.lstat(shm).st_nlink == 1
    assert store.recovered_from is None


@pytest.mark.parametrize("suffix", ["-journal", "-wal", "-shm"])
def test_ten_nhat_ky_la_lien_ket_go_truoc_khi_sqlite_mo(path, tmp_path, monkeypatch, suffix):
    """Tên file nhật ký là liên kết thư mục: kho gỡ chính liên kết **trước** mọi lần SQLite mở file
    nháp, rồi chạy bình thường; nháp, trạng thái gửi còn nguyên, thư mục ngoài không bị đụng."""
    draft_id, state = seeded(path)
    if suffix != "-journal":
        to_wal(path)
    outside = tmp_path / "ngoai"
    outside.mkdir()
    (outside / "giu.txt").write_bytes(b"giu nguyen")
    link = path.with_name(path.name + suffix)
    link_dir(link, outside)
    try:
        spy = ConnectSpy(monkeypatch, watched=path)
        store = DraftStore(path=path)
        assert store.load_send_state(draft_id) == state
        assert spy.linked_at_open == [] and path in spy.paths
        assert not os.path.lexists(link)
        store.save(DraftSnapshot(keyword="ghi được"))
        assert store.recovered_from is None
    finally:
        if os.path.lexists(link):
            unlink_dir_link(link)
    assert sorted(p.name for p in outside.iterdir()) == ["giu.txt"]


def test_doi_ten_sang_mot_ben_mang_theo_file_nhat_ky(path):
    """``_move_aside`` đổi tên file cùng mọi file nhật ký đi kèm (nhật ký của file cũ mà để lại thì
    SQLite «khôi phục» nó vào file mới), không ghi đè tên đã có. Thử thẳng hàm: khi kho mở file,
    SQLite tự xử lý nhật ký lạ trước, nên ca qua kho không cố định được nhật ký nào còn lại."""
    path.write_bytes(b"file cu")
    for suffix in drafts._JOURNAL_SUFFIXES:
        path.with_name(path.name + suffix).write_bytes(suffix.encode())
    store = DraftStore(path=path)
    first = store._move_aside()
    path.write_bytes(b"file cu 2")
    second = store._move_aside()
    assert (
        first != second and first.read_bytes() == b"file cu" and second.read_bytes() == b"file cu 2"
    )
    for suffix in drafts._JOURNAL_SUFFIXES:
        assert first.with_name(first.name + suffix).read_bytes() == suffix.encode()
        assert not path.with_name(path.name + suffix).exists()
    assert not path.exists()


# ================================================================ 4. lớp phòng sau


def test_ket_noi_kho_nhap_duoc_rao(path, monkeypatch):
    """Mọi kết nối: ``trusted_schema = OFF``, trần độ dài giá trị (lớp phòng sau lớp kiểm cấu
    trúc). Đo trên kết nối của thao tác thật."""
    draft_id, _state = seeded(path)
    seen = []
    original = drafts._read_send_state

    def spying(conn, wanted):
        seen.append(conn.execute("PRAGMA trusted_schema").fetchone()[0])
        seen.append(conn._conn.getlimit(sqlite3.SQLITE_LIMIT_LENGTH))
        return original(conn, wanted)

    monkeypatch.setattr(drafts, "_read_send_state", spying)
    DraftStore(path=path).load_send_state(draft_id)
    assert seen == [0, drafts._MAX_SQLITE_LENGTH]
    assert drafts._MAX_SQLITE_LENGTH >= 4 * drafts.MAX_DRAFT_BYTES


def test_qua_so_buoc_la_file_la(path, monkeypatch):
    """Trần số bước có trên kết nối kiểm file: quá mức (ở đây hạ trần thật thấp) thì kiểm ra «lạ»,
    không treo. Trần thật (50 triệu) thì file hợp lệ qua."""
    seeded(path)
    assert drafts._is_healthy(path)
    monkeypatch.setattr(drafts, "_PROGRESS_EVERY", 1)  # bộ đếm chạy sau mỗi bước
    monkeypatch.setattr(drafts, "_MAX_VM_STEPS", 10)
    assert not drafts._is_healthy(path)


def test_o_dai_qua_tran_la_file_la(path, monkeypatch):
    """Ô dài quá trần độ dài (app không bao giờ ghi, ở đây hạ trần): file đổi tên sang một bên,
    không để danh sách nháp kẹt mãi ở câu lỗi."""
    seeded(path)
    raw_sql(path, "UPDATE drafts SET title = hex(randomblob(3000))")
    monkeypatch.setattr(drafts, "_MAX_SQLITE_LENGTH", 4000)
    store = DraftStore(path=path)
    assert store.list_drafts().drafts == []
    assert store.recovered_from is not None


def test_cho_dat_file_la_thu_muc_thi_bao_khong_doi_ten(path):
    path.mkdir()
    store = DraftStore(path=path)
    with pytest.raises(DraftError, match="đang là một thư mục"):
        store.list_drafts()
    assert path.is_dir() and moved_files(path.parent) == []

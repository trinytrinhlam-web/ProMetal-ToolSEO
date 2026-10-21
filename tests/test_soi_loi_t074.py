"""Soi Lỗi T-074 (rút gọn): dọn thẻ ảnh lượt 2 (sau T-070).

Thử lại trên bản sửa các cách lách của T-070 và biến thể mới: dòng lặp hay dòng bị thay trong
``sqlite_master`` (thử T1 của Lá Chắn T-070, kiểu của Soi Lỗi T-070); kiểm và dùng trong cùng giao
dịch (thử T2 với kẻ tấn công chờ khóa thay vì bỏ cuộc, file ở chế độ WAL); lỗi giữa thao tác không
để khóa lại; file thẻ do bản T-070 ghi vẫn mở được. Phần tên: tên file nay tách chỗ chữ dính số;
tên ảnh của máy ảnh, điện thoại, ứng dụng chat và tên người đặt có số dính liền vẫn là ảnh thật.

Tên khách, địa chỉ đều là giả. File SQLite dựng trong ``tmp_path``, không gọi mạng. Lỗi tìm thấy
được đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T074-n`` (xem
``docs/team/reports/T-074-soi-loi.md``): sửa xong thì test tự báo XPASS để gỡ dấu.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from contextlib import closing
from pathlib import Path

import pytest

import seo_app.storage.image_tags as image_tags_module
from seo_app.images.folders import ImageRef
from seo_app.images.tags import SOURCE_AI, ImageTags, is_ai_name, tags_for_image
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError, _is_healthy

REF = ImageRef(0, "CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg")
FOLDER = "CT012 - Cổng inox - Tân Phú/truoc"
BASE = "CT012 - Cổng inox - Quận 7/truoc"
REAL = ImageTags(project_code="CT012", category="Cổng inox", area="Quận 7", phase="truoc")
AI_ONLY = ImageTags(source=SOURCE_AI, category="Cổng inox")
# Trigger sửa khu vực vừa lưu: chạy được thì đọc lại ra "Quận 1" thay vì khu vực đã lưu.
MUTATING_TRIGGER = (
    "CREATE TRIGGER IF NOT EXISTS t AFTER INSERT ON manual_tags BEGIN "
    "UPDATE manual_tags SET area = 'Quận 1'; END"
)


@pytest.fixture(autouse=True)
def _never_touch_real_tag_file(monkeypatch, tmp_path_factory):
    """Không bao giờ đọc/ghi file thẻ thật ``data/image_tags.sqlite``."""
    folder = tmp_path_factory.mktemp("soi-loi-t074")
    monkeypatch.setattr(image_tags_module, "DEFAULT_IMAGE_TAGS_FILE", folder / "image_tags.sqlite")


@pytest.fixture
def store(tmp_path) -> ImageTagStore:
    """Kho đã tạo file và lưu sẵn một thẻ (REF ở Quận 7)."""
    store = ImageTagStore(path=tmp_path / "data" / "image_tags.sqlite")
    store.set(REF, ImageTags(area="Quận 7"))
    return store


def raw_area(path: Path) -> str | None:
    """Khu vực của REF đọc thẳng từ file (không qua app)."""
    with closing(sqlite3.connect(path)) as conn:
        row = conn.execute(
            "SELECT area FROM manual_tags WHERE rel_path = ?", (REF.rel_path,)
        ).fetchone()
    return row and row[0]


def trigger_count(path: Path) -> int:
    with closing(sqlite3.connect(path)) as conn:
        row = conn.execute("SELECT count(*) FROM sqlite_master WHERE type = 'trigger'").fetchone()
    return row[0]


def lock_is_free(path: Path) -> bool:
    """Kết nối khác (không chờ) lấy ngay được khóa ghi độc quyền: không còn giao dịch nào mở."""
    with closing(sqlite3.connect(path, timeout=0, isolation_level=None)) as conn:
        try:
            conn.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError:
            return False
        conn.execute("ROLLBACK")
        return True


def edit_master(path: Path, *statements: str) -> None:
    """Sửa thẳng ``sqlite_master`` (``writable_schema``), như một chương trình lạ có thể làm."""
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA writable_schema = ON")
        for statement in statements:
            conn.execute(statement)
        conn.commit()


# ===== LC-T070-1 (= SL-T070-1) · dòng lặp, dòng bị thay trong sqlite_master =====================


def _trigger_row(name: str) -> str:
    body = (
        f"CREATE TRIGGER {name} AFTER INSERT ON manual_tags BEGIN "
        "UPDATE manual_tags SET area = ''Quận 1''; END"
    )
    return (
        "INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) "
        f"VALUES ('trigger', '{name}', 'manual_tags', 0, '{body}')"
    )


def _copy_row(name: str, new_name: str = "name") -> str:
    return (
        f"INSERT INTO sqlite_master SELECT type, {new_name}, tbl_name, rootpage, sql "
        f"FROM sqlite_master WHERE name = '{name}'"
    )


# Ngoài 5 kiểu của Thợ Máy (``test_t074_duplicate_master_row_is_a_strange_file``) và 3 test
# SL-T070-1: dòng lặp viết khác hoa/thường (SQLite không phân biệt khi tra tên); giữ đúng 4 dòng
# bằng cách thay dòng chỉ mục bằng trigger (kể cả trigger mang đúng tên chỉ mục); bỏ cả bảng info
# để lấy chỗ cho dòng lặp và trigger.
MASTER_TRICKS = {
    "lap-khac-hoa-thuong": (_copy_row("sqlite_autoindex_info_1", "upper(name)"), _trigger_row("t")),
    "thay-chi-muc-bang-trigger-giu-4-dong": (
        "DELETE FROM sqlite_master WHERE name = 'sqlite_autoindex_info_1'",
        _trigger_row("t"),
    ),
    "trigger-mang-ten-chi-muc": (
        "DELETE FROM sqlite_master WHERE name = 'sqlite_autoindex_info_1'",
        _trigger_row("sqlite_autoindex_info_1"),
    ),
    "bo-bang-info-lap-chi-muc-them-trigger": (
        "DELETE FROM sqlite_master WHERE tbl_name = 'info'",
        _copy_row("sqlite_autoindex_manual_tags_1"),
        _trigger_row("t"),
    ),
}


@pytest.mark.parametrize("case", list(MASTER_TRICKS))
def test_master_row_tricks_are_strange_files_and_trigger_never_runs(store, case):
    edit_master(store.path, *MASTER_TRICKS[case])
    hostile = store.path.read_bytes()
    with closing(sqlite3.connect(store.path)) as conn:
        conn.text_factory = bytes
        image_tags_module._guard(conn)
        assert image_tags_module._app_tables(conn) is None
    assert _is_healthy(store.path) is False
    for _ in range(2):  # lần 2: như khởi động lại app
        fresh = ImageTagStore(path=store.path)
        fresh.set(REF, ImageTags(area="Tân Phú"))
        assert fresh.get(REF).tags.area == "Tân Phú"
    moved = sorted(store.path.parent.glob("image_tags.hong-*.sqlite"))
    assert len(moved) == 1 and moved[0].read_bytes() == hostile


# ===== LC-T070-2 · kiểm và dùng trong cùng giao dịch: thử T2 thêm biến thể ======================


def _attack_right_after_check(monkeypatch, path: Path, *, patient: bool):
    """Ngay sau lần app kiểm ``sqlite_master``, "chương trình khác" thêm một trigger sửa dữ liệu.
    ``patient``: kẻ tấn công chờ khóa (busy timeout 10 giây, ở luồng riêng) thay vì bỏ cuộc ngay
    như test của Thợ Máy; app giữ giao dịch thêm 0,3 giây để kẻ tấn công kịp chen vào."""
    real_app_tables = image_tags_module._app_tables
    outcomes: list[str] = []
    threads: list[threading.Thread] = []

    def attack() -> None:
        timeout = 10 if patient else 0
        with closing(sqlite3.connect(path, timeout=timeout, isolation_level=None)) as attacker:
            try:
                attacker.execute(MUTATING_TRIGGER)
                outcomes.append("da-them")
            except sqlite3.OperationalError as exc:
                outcomes.append("bi-chan" if "locked" in str(exc) else str(exc))

    def check_then_attack(conn):
        result = real_app_tables(conn)
        if patient:
            thread = threading.Thread(target=attack)
            thread.start()
            threads.append(thread)
            time.sleep(0.3)
        else:
            attack()
        return result

    monkeypatch.setattr(image_tags_module, "_app_tables", check_then_attack)
    return outcomes, threads


def _use_wal(path: Path) -> None:
    """Chế độ WAL ghi vào file (chương trình khác đặt sẵn); app không tự bật."""
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("PRAGMA journal_mode = WAL").fetchone() == ("wal",)


@pytest.mark.parametrize("journal", ["nhat-ky-thuong", "wal"])
def test_patient_attacker_cannot_slip_a_trigger_into_a_save(store, monkeypatch, journal):
    """Kẻ tấn công chờ được khóa thì chỉ thêm được trigger **sau** khi lần lưu xong: trigger không
    chạy trong lần lưu; lần sau app bắt được trước khi ghi, đổi tên file lạ (giữ lại)."""
    if journal == "wal":
        _use_wal(store.path)
    with monkeypatch.context() as patch:
        outcomes, threads = _attack_right_after_check(patch, store.path, patient=True)
        store.set(REF, ImageTags(area="Tân Phú"))
        for thread in threads:
            thread.join(timeout=30)
    assert outcomes == ["da-them"]
    assert raw_area(store.path) == "Tân Phú"  # trigger không chạy trong lần lưu
    assert trigger_count(store.path) == 1
    with pytest.raises(ImageTagStoreError):
        store.set(REF, ImageTags(area="Quận 8"))
    assert raw_area(store.path) == "Tân Phú"
    store.set(REF, ImageTags(area="Quận 8"))
    assert store.get(REF).tags.area == "Quận 8"
    assert store.recovered_from is not None
    assert raw_area(store.recovered_from) == "Tân Phú"


def test_wal_attacker_blocked_on_save_and_read_keeps_checked_snapshot(store, monkeypatch):
    """File ở chế độ WAL: lần lưu giữ quyền ghi nên kẻ tấn công (không chờ) bị chặn; lần đọc thì
    WAL cho người khác ghi song song, nhưng lần đọc vẫn đọc đúng bản đã kiểm (ảnh chụp từ câu kiểm
    ``sqlite_master``), và lần lưu sau bắt được trigger trước khi ghi."""
    _use_wal(store.path)
    with monkeypatch.context() as patch:
        outcomes, _ = _attack_right_after_check(patch, store.path, patient=False)
        store.set(REF, ImageTags(area="Tân Phú"))
        assert outcomes == ["bi-chan"]
        assert store.get(REF).tags.area == "Tân Phú"
        assert outcomes == ["bi-chan", "da-them"]
    with pytest.raises(ImageTagStoreError):
        store.set(REF, ImageTags(area="Quận 8"))
    assert raw_area(store.path) == "Tân Phú"  # trigger chưa bao giờ chạy
    store.set(REF, ImageTags(area="Quận 8"))
    assert store.get(REF).tags.area == "Quận 8"
    assert store.recovered_from is not None


def test_file_swapped_right_after_health_check_is_caught_before_create(store, monkeypatch):
    """File lạ thay vào ngay sau ``_is_healthy`` (trước kết nối tạo bảng): ``_prepare`` kiểm lại
    trong giao dịch ghi, chưa ghi gì; lần sau đổi tên file lạ, dùng lại được."""
    real_is_healthy = image_tags_module._is_healthy

    def healthy_then_swap(path):
        result = real_is_healthy(path)
        with closing(sqlite3.connect(path)) as conn:
            conn.execute(MUTATING_TRIGGER)
        return result

    store._ready = False  # như lần mở đầu sau khi khởi động app
    with monkeypatch.context() as patch:
        patch.setattr(image_tags_module, "_is_healthy", healthy_then_swap)
        with pytest.raises(ImageTagStoreError):
            store.set(REF, ImageTags(area="Tân Phú"))
    assert store._ready is False
    assert raw_area(store.path) == "Quận 7"
    assert lock_is_free(store.path)
    store.set(REF, ImageTags(area="Tân Phú"))
    assert store.get(REF).tags.area == "Tân Phú"
    assert store.recovered_from is not None


# ===== Lỗi giữa thao tác không để giao dịch mở, khóa còn giữ =====================================


class _Stop(BaseException):
    """Như Ctrl+C hay luồng bị dừng giữa chừng (không phải ``Exception``)."""


@pytest.mark.parametrize("error", [RuntimeError("giữa chừng"), _Stop()], ids=["loi", "dung-ngang"])
def test_error_while_reading_rows_leaves_no_lock(store, monkeypatch, error):
    def boom(self, row):
        raise error

    monkeypatch.setattr(ImageTagStore, "_row_to_tag", boom)
    with pytest.raises(type(error)):
        store.get(REF)
    assert lock_is_free(store.path)


def test_error_inside_a_save_rolls_back_and_leaves_no_lock(store):
    with pytest.raises(RuntimeError), store._connect(write=True) as conn:
        conn.execute("UPDATE manual_tags SET area = 'Quận 1'")
        raise RuntimeError("giữa chừng")
    assert lock_is_free(store.path)
    assert store.get(REF).tags.area == "Quận 7"


def test_save_stopped_by_step_limit_rolls_back_and_leaves_no_lock(store, monkeypatch):
    monkeypatch.setattr(image_tags_module, "_MAX_VM_STEPS", 200_000)
    with pytest.raises(ImageTagStoreError), store._connect(write=True) as conn:
        conn.execute("UPDATE manual_tags SET area = 'Quận 1'")
        conn.execute(
            "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n "
            "WHERE x < 100000000) SELECT count(*) FROM n"
        ).fetchone()
    assert lock_is_free(store.path)
    assert store.get(REF).tags.area == "Quận 7"
    assert store.recovered_from is None  # file hợp lệ: không đổi tên


def test_strange_structure_found_mid_run_leaves_no_lock(store):
    with closing(sqlite3.connect(store.path)) as conn:
        conn.execute(MUTATING_TRIGGER)
    with pytest.raises(ImageTagStoreError):
        store.get(REF)
    assert lock_is_free(store.path)


def test_huge_create_statement_swapped_in_while_running_resets_then_recovers(store):
    """Câu ``CREATE`` dài quá giới hạn độ dài thay vào khi app đang chạy: lần đọc báo lỗi cố định
    (không đường dẫn), đặt lại ``_ready``, không để khóa; lần sau đổi tên file, dùng lại được."""
    store.path.unlink()
    with closing(sqlite3.connect(store.path)) as conn, conn:
        for sql in image_tags_module._CREATE_TABLES:
            conn.execute(sql)
        conn.execute(f"CREATE TABLE khac (x /* {'c' * 1_200_000} */)")
    with pytest.raises(ImageTagStoreError) as info:
        store.list_manual()
    assert str(info.value) == image_tags_module._MSG_BROKEN
    assert store._ready is False
    assert lock_is_free(store.path)
    assert store.list_manual().items == ()
    assert store.recovered_from is not None


# ===== File thẻ do bản T-070 ghi vẫn mở được ====================================================

# Câu CREATE của bản T-070 (``da87dbf``), chép nguyên văn: file người dùng đang có trên máy.
T070_CREATE = (
    "CREATE TABLE IF NOT EXISTS manual_tags ("
    "root_index INTEGER NOT NULL, ref_key TEXT NOT NULL, rel_path TEXT NOT NULL, "
    "source TEXT NOT NULL, project_code TEXT NOT NULL, category TEXT NOT NULL, "
    "area TEXT NOT NULL, phase TEXT NOT NULL, saved_at TEXT NOT NULL, "
    "saved_ts REAL NOT NULL, PRIMARY KEY (root_index, ref_key))",
    "CREATE TABLE IF NOT EXISTS info (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
)
LONG_REF = ImageRef(0, "/".join(["Thư mục rất dài có dấu"] * 30) + "/ảnh.jpg")
T070_TAGS = {
    REF: ImageTags(project_code="CT012", category="Cổng inox", area="Tân Phú", phase="truoc"),
    ImageRef(0, "CT015 - Lan can - Quận 7/sau/ảnh 2.jpg"): ImageTags(area="Quận 8"),
    ImageRef(1, "Ảnh AI/x.png"): ImageTags(source="ai", category="Cổng inox"),
    LONG_REF: ImageTags(area="Quận 1"),
}


def _t070_file(path: Path) -> None:
    """File như bản T-070 ghi (``_prepare`` rồi ``set`` từng thẻ): hai bảng, phiên bản 1."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as conn, conn:
        for sql in T070_CREATE:
            conn.execute(sql)
        conn.execute("INSERT OR IGNORE INTO info (key, value) VALUES ('schema_version', '1')")
        for number, (ref, tags) in enumerate(T070_TAGS.items(), start=1):
            conn.execute(
                "INSERT OR REPLACE INTO manual_tags (root_index, ref_key, rel_path, source, "
                "project_code, category, area, phase, saved_at, saved_ts) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ref.root_index,
                    image_tags_module.ref_key(ref),
                    ref.rel_path,
                    tags.source,
                    tags.project_code,
                    tags.category,
                    tags.area,
                    tags.phase,
                    f"2026-10-20T1{number}:00:00+07:00",
                    1_760_000_000.0 + number,
                ),
            )


def test_file_written_by_t070_is_accepted_and_reads_do_not_rewrite_it(tmp_path):
    path = tmp_path / "data" / "image_tags.sqlite"
    _t070_file(path)
    before = path.read_bytes()
    assert _is_healthy(path) is True
    store = ImageTagStore(path=path)
    found = store.get_many(T070_TAGS)
    assert {ref: item.tags for ref, item in found.items()} == T070_TAGS
    listed = store.list_manual()
    assert len(listed.items) == len(T070_TAGS) and listed.skipped == 0
    assert listed.items[0].ref == LONG_REF  # mới nhất trước
    assert path.read_bytes() == before  # mở và đọc không ghi gì vào file cũ
    store.set(ImageRef(0, "moi.jpg"), ImageTags(area="Quận 3"))
    assert store.recovered_from is None
    assert list(path.parent.glob("*hong*")) == []
    assert len(store.list_manual().items) == len(T070_TAGS) + 1


# ===== SL-T070-3: tên file tách chỗ chữ dính số, ảnh thật không thành ảnh AI ====================

# Tên file ảnh thật hay gặp (máy ảnh, điện thoại, ứng dụng chat, phần mềm sửa ảnh, tên người đặt có
# số dính liền). Ngoài 16 tên của Thợ Máy. Thử thêm 20.000 tên ngẫu nhiên mỗi loại (báo cáo, E5).
REAL_FILE_NAMES = [
    "IMG_20250315_102030",
    "IMG20250315102030",
    "IMG_20250315_102030_HDR",
    "IMG_20250315_102030_BURST001",
    "IMG-20250315-WA0001",
    "IMG_0001 (1)",
    "IMG_0001~2",
    "IMG_0001-edited",
    "IMG_E0001",
    "MVIMG_20250315_102030",
    "PXL_20250315_102030123.MP",
    "PXL_20250315_102030123.PORTRAIT",
    "20250315_102030(0)",
    "20250315_102030_001",
    "DSC_0001",
    "_DSC0001",
    "DSC00001",
    "DSCF0001",
    "DSCN0001",
    "P1000123",
    "P3150001",
    "_MG_0001",
    "GOPR0001",
    "GH010001",
    "G0010001",
    "DJI_0001",
    "DJI_20250315102030_0001_D",
    "PANO_20250315_102030",
    "Screenshot_20250315-102030",
    "Screenshot_20250315_102030_Zalo",
    "Screenshot_2025-03-15-10-20-30-123_com.zing.zalo",
    "Screenshot 2025-03-15 102030",
    "Screen Shot 2025-03-15 at 10.20.30 AM",
    "WIN_20250315_10_20_30_Pro",
    "received_1234567890123456",
    "FB_IMG_1710000000000",
    "438291234_1234567890123456_1234567890123456789_n",
    "z5432123456789_7f3a2b9c0d1e4f5a6b7c8d9e0f1a2b3c",
    "z5432123456789_7f3a2b9c0d1e4f5a6b7c8d9e0f1a2b3c_2",
    "Zalo_20250315_102030",
    "viber_image_2025-03-15_10-20-30-123",
    "photo_2025-03-15_10-20-30",
    "Ảnh chụp màn hình 2025-03-15 102030",
    "Ảnh màn hình 2025-03-15 lúc 10.20.30",
    "Messenger_creation_5F3A2B9C-0D1E-4F5A-8B7C-8D9E0F1A2B3C",
    "mmexport1710000000000",
    "wx_camera_1710000000000",
    "B612_20250315_102030_123",
    "SNOW_20250315_102030_123",
    "MTXX_20250315102030",
    "Camera360_20250315_102030",
    "CameraZOOM-20250315102030123",
    "KakaoTalk_20250315_102030123",
    "LINE_P20250315102030_123",
    "Picsart_25-03-15_10-20-30-123",
    "InShot_20250315_102030123",
    "CamScanner 03-15-2025 10.20",
    "5f3a2b9c-0d1e-4f5a-8b7c-8d9e0f1a2b3c",
    "deadbeefdeadbeefdeadbeefdeadbeef",  # tên kiểu mã băm (chỉ chữ số hex): không thể có "ai"
    "cong-sat-q7-01",
    "CongSatQ7_02",
    "nha-chi-Mai2",
    "Hai3",
    "Thai1",
    "TRAI2",
    "khai5",
    "anh-Hoai-04",
    "lan-can-inox-304",
    "mai-ton-2lop",
    "cua-cuon-A1",
    "khung-bao-ve-cua-so-2",
    "IMG_0001_chi-Thao",
    "Cổng2cánh",
    "cong2canh",
    "Mô tơ cổng cuốn 1",
    "Nhà anh Phong 3",
    "Mộ Phong",
    "Cửa phòng ngủ 2",
    "Mở rộng phòng khách 01",
    "Mô hình cổng 3",
    "quan7-cong01",
    "Tai1",
    "Lai2",
    "Chai3",
    "Sai4",
    "MAI1",
    "PHAI2",
    "aia2",
    "kai3",
]


@pytest.mark.parametrize("name", REAL_FILE_NAMES)
def test_real_photo_file_names_stay_real_after_digit_split(name):
    assert tags_for_image(ImageRef(0, f"{BASE}/{name}.jpg")).tags == REAL


# Tên thư mục gần "mô phỏng" (SL-T070-5) mà là ảnh thật, có dấu và không dấu.
REAL_FOLDERS_NEAR_SIMULATED = [
    "Cửa phòng ngủ",
    "Mở rộng phòng khách",
    "Mô tơ cổng cuốn",
    "Mô hình cổng",
    "Ảnh mờ",
    "Nhà chị Mơ",
    "Cua phong ngu",
    "Mo rong phong khach",
    "Mo to cong cuon",
    "Nha chi Mo",
    "Ảnh dựng khung",
    "Anh dung khung",
]


@pytest.mark.parametrize("folder", REAL_FOLDERS_NEAR_SIMULATED)
def test_folders_near_simulated_stay_real(folder):
    tags = tags_for_image(ImageRef(0, f"{BASE}/{folder}/IMG_0001.jpg")).tags
    assert not tags.is_ai and tags.project_code == "CT012" and tags.area == "Quận 7"


# ===== Lỗi mới ===================================================================================


def _other_tab_saves(path: Path) -> str:
    """Tab khác (kết nối khác, không chờ) lưu một thẻ: ghi thật một dòng rồi commit."""
    with closing(sqlite3.connect(path, timeout=0, isolation_level=None)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE manual_tags SET area = 'Quận 4' WHERE rel_path = ?", (REF.rel_path,)
            )
            conn.execute("COMMIT")
            return "da-luu"
        except sqlite3.OperationalError as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            return "bi-chan" if "locked" in str(exc) else str(exc)


def test_sl_t074_1_save_in_other_tab_does_not_wait_for_row_processing(store, monkeypatch):
    refs = [REF, *(ImageRef(0, f"{FOLDER}/IMG_{n:04d}.jpg") for n in range(2, 5))]
    for ref in refs[1:]:
        store.set(ref, ImageTags(area="Quận 3"))
    real_tags_for_image = image_tags_module.tags_for_image
    outcomes: list[str] = []

    def save_elsewhere_then_tags(ref):
        if not outcomes:  # lúc app bắt đầu xử lý các dòng đã đọc
            outcomes.append(_other_tab_saves(store.path))
        return real_tags_for_image(ref)

    monkeypatch.setattr(image_tags_module, "tags_for_image", save_elsewhere_then_tags)
    found = store.get_many(refs)
    assert len(found) == len(refs)
    assert outcomes == ["da-luu"]


# Tên công cụ AI một từ mà người gõ viết hoa ở giữa (kiểu CamelCase). Lá Chắn T-055 thấy
# "MidJourney" trên ``main``; tôi thử thêm mọi tên công cụ một từ ở mọi chỗ viết hoa (E10).
CAMEL_CASE_AI_FOLDERS = [
    "MidJourney",
    "Ảnh MidJourney",
    "MidJourney V6",
    "FireFly",
    "Adobe FireFly",
    "SeeDream",
    "SeeDream 4.0",
    "HaiLuo",
    "JiMeng",
    "CoPilot",
    "IdeoGram",
    "ReCraft",
    "RunWay",
]


@pytest.mark.parametrize("folder", CAMEL_CASE_AI_FOLDERS)
def test_sl_t074_2_camel_case_tool_name_in_folder_is_ai(folder):
    assert tags_for_image(ImageRef(0, f"{BASE}/{folder}/IMG_0001.jpg")).tags == AI_ONLY


@pytest.mark.parametrize("folder", ["MidJourney", "FireFly", "SeeDream", "HaiLuo", "CoPilot"])
def test_sl_t074_2_camel_case_tool_name_as_root_folder_is_ai(folder):
    assert is_ai_name(f"G:/My Drive/{folder}") is True


# Đối chứng (đang đúng): cùng các tên ở tên file (không tách chữ hoa) và ở kiểu viết thường gặp.
@pytest.mark.parametrize("name", ["MidJourney", "MidJourney6", "FireFly", "SeeDream", "HaiLuo"])
def test_camel_case_tool_name_in_file_name_is_ai(name):
    assert tags_for_image(ImageRef(0, f"{BASE}/{name}_0001.png")).tags == AI_ONLY


USUAL_CASE_AI_FOLDERS = [
    "midjourney",
    "Midjourney",
    "MIDJOURNEY",
    "Firefly",
    "FIREFLY",
    "Seedream",
    "copilot",
]


@pytest.mark.parametrize("folder", USUAL_CASE_AI_FOLDERS)
def test_tool_name_in_usual_case_in_folder_is_ai(folder):
    assert tags_for_image(ImageRef(0, f"{BASE}/{folder}/IMG_0001.jpg")).tags == AI_ONLY

"""Soi Lỗi T-137 (đầy đủ): nhắc chống gửi trùng sau khi file nháp bị cất sang một bên (SL-T136-1,
G4). Kiểm độc lập (mọi ca, mọi kiểm là của Soi Lỗi), WordPress giả, AI giả, mọi file trong thư mục
tạm, không gọi mạng thật.

1. Dò tên: tên do **chính kho** đặt khi cất ba lần trong cùng một giây (``-2``, ``-3``), mới nhất
   trước; chỗ đặt file nháp là liên kết bị cất cũng tính; tên gần giống khác (của Soi Lỗi) không
   tính; không mở file nào (móc kiểm của Python, ``sys.addaudithook``).
2. G4 trên kho đang dùng: đầu file bị sửa lúc kho đã «sẵn sàng» thì đọc vẫn được (khóa gửi trùng
   còn đọc được), lần ghi báo «bị lỗi» (không «chỉ đọc»), thao tác sau cất file; đối chứng «chỉ đọc»
   thật: báo «chỉ đọc», không cất.
3. Trang: đường 1 ở **Đăng ngay** (tab mở bài trước lần gửi ở tab khác; trang Bài viết của phiên
   khác cất file); đổi hình thức sau khi tick thì phải tick lại; đường 2 sau khi tắt mở lại app
   (viết lại bài): trang Bài viết nhắc ở mọi lần vẽ, cú bấm lọt không gửi gì, tick rồi gửi đúng một
   bài, sau đó khóa T-086 thay cổng; tab biết bài đã gửi: không có cổng mới, khóa cũ giữ nguyên.
"""

from __future__ import annotations

import contextlib
import os
import sqlite3
import stat
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pytest
import streamlit as st
import test_app_images as ui
import test_soi_loi_t112 as sl112
import test_t086_send_state as t86
import test_t092_nhap_bi_xoa as t92
import test_t102_publish as t102
from streamlit.testing.v1 import AppTest
from test_t131_kho_nhap import link_dir, unlink_dir_link

from seo_app.storage import drafts, plan_cache, site_index
from seo_app.storage.drafts import (
    DraftError,
    DraftSnapshot,
    DraftStore,
    SendState,
    moved_aside_names,
)

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả.
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live

run_ok = ui.run_ok
button = ui.button
send_button = t102.send_button

GATE = "_wp_moved_ok"
GATE_LABEL = "Tôi đã xem trên WordPress: bài này chưa có trên website"
GATE_TEXT = "nên app không biết bài này đã có trên website chưa"
RESET_TEXT = "sau lần bạn tick «Tôi đã xem trên WordPress…»"
HOME_TEXT = "nên danh sách này có thể thiếu bài"
EMPTY = "Chưa có bài nào phần mềm đã gửi lên WordPress."
RECOVERED = "File nháp cũ bị hỏng nên đã được cất sang một bên"
AGAIN_DRAFT = "Tạo thêm một bài nháp mới"
AGAIN_PUBLISH = "Tạo thêm một bài mới và đăng công khai ngay bài mới đó"
GOOD = "drafts.hong-20261112-143622.sqlite"


@pytest.fixture(autouse=True)
def caches(monkeypatch, tmp_path_factory):
    """Bản lưu kế hoạch, danh sách bài đã đăng ở thư mục tạm (không ghi ``data/`` thư mục chạy)."""
    folder = tmp_path_factory.mktemp("cache-sl137")
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", folder / "plan_cache.sqlite")
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", folder / "site_index.sqlite")


@pytest.fixture
def path(tmp_path: Path, monkeypatch) -> Path:
    """File nháp trong thư mục dự án giả (``PROJECT_ROOT`` của kho nháp trỏ vào đó)."""
    folder = tmp_path / "du-an"
    (folder / "data").mkdir(parents=True)
    monkeypatch.setattr(drafts, "PROJECT_ROOT", folder)
    return folder / "data" / "drafts.sqlite"


def damage(file: Path, offset: int = 18, value: int = 3) -> None:
    """Chương trình khác sửa một byte đầu file (byte 18 = 3: SQLite coi file là «chỉ đọc»)."""
    data = bytearray(file.read_bytes())
    data[offset] = value
    file.write_bytes(bytes(data))


# ============================================================ dò tên file đã cất


class Frozen(datetime):
    """Đồng hồ đứng yên cho kho nháp: mọi lần cất rơi vào cùng một giây."""

    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 11, 12, 14, 36, 22, tzinfo=tz)


def test_ten_kho_dat_khi_cat_ba_lan_cung_giay_moi_nhat_truoc(path, monkeypatch):
    """Kho cất file hỏng ba lần trong cùng một giây: tên ``…-143622``, ``…-2``, ``…-3`` do chính
    ``_move_aside`` đặt đều được nhận, mới nhất trước (cùng giây thì số thứ tự lớn hơn là mới
    hơn); mỗi lần, kho mới vẫn dùng được."""
    monkeypatch.setattr(drafts, "datetime", Frozen)
    made = []
    for n in range(3):
        DraftStore(path=path).save(DraftSnapshot(keyword=f"bài {n}"))
        damage(path)
        fresh = DraftStore(path=path)
        assert fresh.list_drafts().drafts == []
        made.append(fresh.recovered_from.name)
    base = "drafts.hong-20261112-143622"
    assert made == [f"{base}.sqlite", f"{base}-2.sqlite", f"{base}-3.sqlite"]
    assert moved_aside_names(path) == tuple(reversed(made))


def test_cho_dat_file_la_lien_ket_bi_cat_cung_tinh(path, tmp_path):
    """Chỗ đặt file nháp là liên kết (junction trên Windows): kho cất chính liên kết sang một bên
    (tên ``drafts.hong-…``); dấu «đã gửi» có thể ở nơi nó trỏ tới, nên tên đó cũng tính (chỉ xét
    tên, không hỏi đó là file hay thư mục)."""
    outside = tmp_path / "noi-khac"
    outside.mkdir()
    try:
        link_dir(path, outside)
    except OSError:
        pytest.skip("máy không tạo được liên kết thư mục")
    try:
        store = DraftStore(path=path)
        assert store.list_drafts().drafts == []
        moved = store.recovered_from
        assert moved is not None and moved.name.startswith("drafts.hong-")
        assert moved_aside_names(path) == (moved.name,)
    finally:
        for entry in path.parent.iterdir():
            if entry.name.startswith("drafts.hong-"):
                unlink_dir_link(entry)  # gỡ chính liên kết, không đụng nơi nó trỏ tới
    assert outside.is_dir()


NEAR_MISS = {
    "duoi-them": GOOD + ".bak",
    "nhat-ky-wal": GOOD + "-wal",
    "so-thu-tu-1": "drafts.hong-20261112-143622-1.sqlite",
    "so-thu-tu-02": "drafts.hong-20261112-143622-02.sqlite",
    "so-thu-tu-10000": "drafts.hong-20261112-143622-10000.sqlite",
    "ngay-7-so": "drafts.hong-2026111-143622.sqlite",
    "gach-duoi": "drafts.hong-20261112_143622.sqlite",
    "gio-24": "drafts.hong-20261112-240000.sqlite",
    "30-thang-2": "drafts.hong-20260230-120000.sqlite",
    "chu-hoa": "drafts.HONG-20261112-143622.sqlite",
    "cach-dau": " " + GOOD,
    "chu-an": GOOD.replace(".sqlite", chr(0x200B) + ".sqlite"),
    "so-a-rap": "drafts.hong-"
    + "".join(chr(0x0660 + int(c)) for c in "20261112")
    + "-143622.sqlite",
    # Chữ số lạ chỉ ở năm: ``strptime`` (``%Y`` là ``\d{4}``) vẫn đọc ra năm 2026, nên chỉ khuôn
    # ``[0-9]`` chặn được (đột biến «\d»).
    "nam-a-rap": "drafts.hong-"
    + "".join(chr(0x0660 + int(c)) for c in "2026")
    + "1112-143622.sqlite",
    "nam-toan-khoi": "drafts.hong-"
    + "".join(chr(0xFF10 + int(c)) for c in "2026")
    + "1112-143622.sqlite",
    "duoi-khac": "drafts.hong-20261112-143622.db",
    "kho-the-anh": "image_tags.hong-20261112-143622.sqlite",
    "tien-to": "x" + GOOD,
}


@pytest.mark.parametrize("name", list(NEAR_MISS.values()), ids=list(NEAR_MISS))
def test_ten_gan_giong_khong_tinh(path, name):
    """Tên gần giống mà kho không bao giờ đặt (thêm đuôi, nhật ký, số thứ tự lạ, ngày giờ không có
    thật, chữ hoa, khoảng trắng, ký tự ẩn, chữ số không phải ASCII, kho khác): không nhắc oan."""
    (path.parent / name).write_bytes(b"")
    assert moved_aside_names(path) == ()


@pytest.mark.parametrize(
    "name",
    [GOOD, "drafts.hong-20261112-143622-2.sqlite", "drafts.hong-20261112-143622-9999.sqlite"],
    ids=["goc", "so-2", "so-9999"],
)
def test_ten_dung_khuon_duoc_tinh(path, name):
    """Đối chứng của ca trên: đúng khuôn kho đặt thì được nhận."""
    (path.parent / name).write_bytes(b"")
    assert moved_aside_names(path) == (name,)


_WATCHED: list[tuple[str, tuple]] | None = None


def _audit(event: str, args: tuple) -> None:
    if _WATCHED is not None:
        _WATCHED.append((event, args))


sys.addaudithook(_audit)  # móc chỉ ghi khi đang đo (``_WATCHED``), ngoài lúc đó không làm gì


def test_do_ten_khong_mo_file_nao(path):
    """Móc kiểm của Python ghi mọi sự kiện trong lúc dò: không có sự kiện mở file («open», cả
    ``os.open``), không mở SQLite; có đúng việc liệt kê thư mục ``data``."""
    global _WATCHED
    (path.parent / GOOD).write_bytes(b"")
    (path.parent / (GOOD + "-journal")).write_bytes(b"")
    assert moved_aside_names(path) == (GOOD,)  # lần đầu: nạp trước các mô-đun dùng muộn
    _WATCHED = []
    try:
        names = moved_aside_names(path)
    finally:
        seen, _WATCHED = _WATCHED, None
    assert names == (GOOD,)
    data = str(path.parent)
    opened = [args for event, args in seen if event == "open" and str(args[0]).startswith(data)]
    assert opened == []
    assert "sqlite3.connect" not in [event for event, _args in seen]
    assert {"os.listdir", "os.scandir"} & {event for event, _args in seen}


# ============================================================ G4 trên kho đang dùng


def test_g4_kho_dang_dung_doc_duoc_ghi_bao_hong_roi_cat(path):
    """Kho đã «sẵn sàng» (không kiểm lại file mỗi lần): chương trình khác sửa byte 18. Đọc vẫn được
    (SQLite mở chỉ đọc), khóa gửi trùng vẫn đọc ra «đã gửi 501», chưa có dấu hiệu cất file. Lần ghi
    báo «bị lỗi» (không «chỉ đọc»); thao tác sau kho cất file, ``moved_aside_names`` thấy đúng tên
    đó; dấu «đã gửi» nằm nguyên trong file đã cất."""
    store = DraftStore(path=path)
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    state = SendState.now(pending=False, post_id=501)
    store.save_send_state(snap.id, state)
    damage(path)
    assert [d.id for d in store.list_drafts().drafts] == [snap.id]
    assert store.load_send_state(snap.id) == state
    assert moved_aside_names(path) == ()
    with pytest.raises(DraftError) as caught:
        store.save(snap.model_copy(update={"keyword": "sửa sau khi hỏng"}), must_exist=True)
    assert str(caught.value) == drafts._MSG_BROKEN and "chỉ đọc" not in str(caught.value)
    assert store.list_drafts().drafts == []
    moved = store.recovered_from
    assert moved is not None and moved_aside_names(path) == (moved.name,)
    with closing(sqlite3.connect(f"file:{moved.as_posix()}?mode=ro", uri=True)) as conn:
        (kept,) = conn.execute("SELECT data FROM send_states WHERE id = ?", (snap.id,)).fetchone()
    assert '"post_id":501' in kept


def test_g4_doi_chung_chi_doc_that_khong_cat(path):
    """Đối chứng: file đặt «chỉ đọc» thật (đầu file đúng): vẫn báo «chỉ đọc», file không bị cất,
    không có dấu hiệu file đã cất."""
    store = DraftStore(path=path)
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    os.chmod(path, stat.S_IREAD)
    try:
        if os.access(path, os.W_OK):
            pytest.skip("tài khoản này vẫn ghi được file chỉ đọc (root)")
        with pytest.raises(DraftError) as caught:
            store.save(snap.model_copy(update={"keyword": "sửa"}), must_exist=True)
        assert str(caught.value) == drafts._MSG_READONLY
        with contextlib.suppress(DraftError):
            store.list_drafts()
        assert store.recovered_from is None and moved_aside_names(path) == ()
        assert path.is_file()
    finally:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


# ============================================================ trang


def login(project_root) -> AppTest:
    """Một phiên mới (tab mới, F5) đăng nhập, dừng ở trang mặc định sau đăng nhập (Bài viết)."""
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(ui.pages.PASSWORD)
    at.button[0].click().run()
    return run_ok(at)


def gate(at):
    """Ô «Tôi đã xem trên WordPress…» (``None``: không hiện)."""
    return next((box for box in at.checkbox if box.key == GATE), None)


def tick_gate(at):
    return run_ok(at.checkbox(key=GATE).check().run())


class Leak:
    """Cú bấm lọt qua nút gửi đang khóa (bấm đúp đúng lúc nút vừa khóa, SL-T056-1): AppTest không
    cho bấm nút khóa nên giả ở ``st.button`` theo khóa ``wp-send``, chỉ khi ``on``."""

    on = False


@pytest.fixture
def leak(monkeypatch):
    original = st.button

    def patched(label, *args, **kwargs):
        clicked = original(label, *args, **kwargs)
        return True if Leak.on and kwargs.get("key") == "wp-send" else clicked

    monkeypatch.setattr(st, "button", patched)
    Leak.on = False
    yield Leak
    Leak.on = False


def leaked_run(at) -> None:
    Leak.on = True
    try:
        run_ok(at.run())
    finally:
        Leak.on = False


def test_duong_1_dang_ngay_tab_mo_truoc_lan_gui_o_tab_khac(
    project_root, root, fake_ai, live, monkeypatch
):
    """Đường 1 ở Đăng ngay: tab B mở bài trước khi tab A gửi (bài 501); chương trình khác sửa byte
    18; một phiên khác đăng nhập, trang Bài viết cất file (nhắc cả hai câu). Tab B: khung T-092
    «tab không biết», cổng mới không tick sẵn, nút khóa dù đã tick «Tôi đã đọc lại…». Tick cổng
    thì mở (cổng là chốt duy nhất còn lại); gửi thì đúng một bài mới, sau đó khóa «đã gửi» thay
    cổng."""
    sl112.seo_like_client(monkeypatch, [])
    tab_a, _pid = ui.ready_image(project_root)
    draft = tab_a.session_state["draft_id"]
    tab_b = t86.reopen(project_root, draft)
    ui.to_publish(tab_a)
    ui.send(tab_a)
    assert len(live.site.posts()) == 1
    damage(drafts.DEFAULT_DRAFTS_FILE)
    home = login(project_root)
    texts = [w.value for w in home.warning]
    assert any(RECOVERED in t for t in texts) and any(HOME_TEXT in t for t in texts)
    sl112.set_seo(tab_b)
    t102.to_mode(tab_b, "Đăng ngay")
    run_ok(tab_b.toggle(key="seo_write").set_value(True).run())
    t102.confirm(tab_b)
    assert t92.NOT_KNOWN in t92.notice(tab_b)
    box = gate(tab_b)
    assert box is not None and box.label == GATE_LABEL and box.value is False
    assert any(GATE_TEXT in w.value for w in tab_b.warning)
    assert send_button(tab_b).disabled
    tick_gate(tab_b)
    assert not send_button(tab_b).disabled
    assert len(live.site.posts()) == 1
    run_ok(send_button(tab_b).click().run())
    assert len(live.site.posts()) == 2
    assert gate(tab_b) is None and t92.box(tab_b, AGAIN_PUBLISH) is not None
    assert send_button(tab_b).disabled


def test_doi_hinh_thuc_sau_khi_tick_phai_tick_lai(project_root, root, fake_ai, live):
    """Có file đã cất, bài chưa gửi: tick cổng ở Nháp rồi đổi sang Hẹn giờ: app bỏ tick, nói vì
    sao; tick «Tôi đã đọc lại…» chưa đủ; tick lại cổng thì mở. Không gửi gì."""
    (drafts.DEFAULT_DRAFTS_FILE.parent / GOOD).write_bytes(b"")
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    assert gate(at) is not None and send_button(at).disabled
    tick_gate(at)
    assert not send_button(at).disabled
    t102.to_mode(at, "Hẹn giờ")
    assert gate(at).value is False
    assert any(RESET_TEXT in w.value for w in at.warning)
    t102.confirm(at)
    assert send_button(at).disabled
    tick_gate(at)
    assert not send_button(at).disabled
    assert live.site.posts() == []


def test_duong_2_mo_lai_app_viet_lai_bai(project_root, root, fake_ai, site, leak):
    """Đường 2: bài đã gửi (bài 501); file nháp bị sửa byte 18; tắt mở lại app (kho dùng chung tạo
    lại), đăng nhập: trang Bài viết cất file và nhắc, lần vẽ sau và phiên sau vẫn nhắc, không còn
    «Chưa có bài nào…». Viết lại bài (nháp mới): cổng không tick sẵn, nút khóa, cú bấm lọt không
    gửi gì. Đối chứng: tick rồi cú bấm lọt gửi đúng một bài; sau đó khóa «đã gửi» thay cổng, cú bấm
    lọt nữa không gửi."""
    first, _pid = ui.ready_image(project_root)
    ui.to_publish(first)
    ui.send(first)
    assert len(site.posts()) == 1
    damage(drafts.DEFAULT_DRAFTS_FILE)
    st.cache_resource.clear()
    for _ in range(2):
        home = login(project_root)
        for _again in range(2):
            assert any(HOME_TEXT in w.value for w in home.warning)
            assert not any(EMPTY in c.value for c in home.caption)
            run_ok(home.run())
    again, _pid = ui.ready_image(project_root)
    ui.to_publish(again)
    box = gate(again)
    assert box is not None and box.value is False and send_button(again).disabled
    leaked_run(again)
    assert len(site.posts()) == 1
    tick_gate(again)
    leaked_run(again)
    assert len(site.posts()) == 2
    assert gate(again) is None and t92.box(again, AGAIN_DRAFT) is not None
    leaked_run(again)
    assert len(site.posts()) == 2


def test_g4_bam_gui_luc_file_vua_hong_khong_gui_gi(project_root, root, fake_ai, site):
    """Bài chưa gửi ở Xuất bản, chưa có file đã cất (chưa có cổng); chương trình khác sửa byte 18
    rồi người dùng bấm «📤 Gửi nháp». App không ghi được «đang gửi» nên không gửi gì lên website;
    câu báo nói «bị lỗi» (không «chỉ đọc»). Kho cất file ngay trong lần chạy đó (trang vẽ lại sau
    lần bấm): có ``MSG_RECOVERED``, cổng mới, nút khóa; lần chạy sau vẫn khóa."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    assert gate(at) is None and not send_button(at).disabled
    damage(drafts.DEFAULT_DRAFTS_FILE)
    ui.send(at)
    assert [r for r in site.fake.requests if r.method != "GET"] == []
    texts = [e.value for e in (*at.error, *at.warning)]
    reason = "chưa ghi được trạng thái gửi vào nháp"
    assert any(reason in t and "File nháp bị lỗi" in t for t in texts)
    assert not any("chỉ đọc" in t for t in texts)
    assert any(RECOVERED in t for t in texts) and len(moved_aside_names()) == 1
    assert gate(at) is not None and send_button(at).disabled
    run_ok(at.run())
    assert gate(at) is not None and send_button(at).disabled
    assert site.posts() == []


def test_tab_biet_da_gui_khong_co_cong_moi_khoa_cu_giu(project_root, root, fake_ai, site, leak):
    """Tab A tự gửi (bài 501); chương trình khác sửa byte 18; tab A sửa bài (sang bước SEO): lần tự
    lưu báo «bị lỗi» (không «chỉ đọc»); về Xuất bản: kho cất file, trang báo ``MSG_RECOVERED``,
    khung T-092 «tab này biết bài đã gửi». Không có cổng mới; khóa «đã gửi» (ô «Tạo thêm…») giữ
    nguyên; cú bấm lọt không gửi gì."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    damage(drafts.DEFAULT_DRAFTS_FILE)
    at.session_state["step"] = 3
    run_ok(at.run())
    problems = [c.value for c in at.caption if "Chưa lưu được nháp" in c.value]
    assert problems and drafts._MSG_BROKEN in problems[0]
    ui.to_publish(at)
    assert any(RECOVERED in w.value for w in at.warning)
    assert t92.KNOWN_SENT in t92.notice(at)
    assert len(moved_aside_names()) == 1
    assert gate(at) is None
    assert t92.box(at, AGAIN_DRAFT) is not None and send_button(at).disabled
    leaked_run(at)
    assert len(site.posts()) == 1

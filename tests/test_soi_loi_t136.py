"""Soi Lỗi T-136 (rút gọn): gom kiểm file 5 kho SQLite, LC-T131-1, câu báo kho nháp.

Kiểm độc lập (mọi ca, mọi kiểm là của Soi Lỗi), mọi file trong ``tmp_path``, không gọi mạng:

1. LC-T131-1 (b) ở kho nháp: file có byte 18 lạ bị cất sang một bên, dấu «đã gửi» vẫn nằm nguyên
   trong file cất đi (B.2 chọn câu báo, không chép sang file mới).
2. LC-T131-1 (a): ô tiêu đề có UTF-8 hỏng chỉ làm nháp đó vắng khỏi danh sách; khóa gửi trùng của nó
   vẫn đọc được; lần lưu kế của tab đang mở bài (so rồi đặt) ghi lại dòng, nháp hiện lại.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from seo_app.storage import drafts
from seo_app.storage.drafts import MSG_RECOVERED, DraftSnapshot, DraftStore, SendState


@pytest.fixture
def path(tmp_path: Path, monkeypatch) -> Path:
    """File nháp trong thư mục dự án giả (``PROJECT_ROOT`` của kho nháp trỏ vào đó)."""
    root = tmp_path / "du-an"
    root.mkdir()
    monkeypatch.setattr(drafts, "PROJECT_ROOT", root)
    return root / "data" / "drafts.sqlite"


def sent_draft(path: Path) -> tuple[DraftSnapshot, SendState]:
    store = DraftStore(path=path)
    snap = store.save(DraftSnapshot(keyword="cổng inox", article_title="Sửa cổng inox Tân Phú"))
    state = SendState.now(pending=False, post_id=501)
    store.save_send_state(snap.id, state)
    return snap, state


def test_byte_18_la_kho_nhap_cat_di_dau_da_gui_con_trong_file_cu(path):
    snap, _state = sent_draft(path)
    data = bytearray(path.read_bytes())
    data[18] = 3
    path.write_bytes(bytes(data))
    store = DraftStore(path=path)
    assert store.list_drafts().drafts == []  # file mới
    moved = store.recovered_from
    assert moved is not None and moved.exists() and moved.name.startswith("drafts.hong-")
    with closing(sqlite3.connect(f"file:{moved.as_posix()}?mode=ro", uri=True)) as conn:
        (kept,) = conn.execute("SELECT data FROM send_states WHERE id = ?", (snap.id,)).fetchone()
    assert '"post_id":501' in kept  # dấu «đã gửi» nằm nguyên trong file cất đi
    message = MSG_RECOVERED.format(name=moved.name)
    assert moved.name in message and "đã gửi" in message and "WordPress" in message
    assert "lối tắt" in message


def test_o_tieu_de_utf8_hong_chi_vang_khoi_danh_sach_khoa_con_luu_lai_thi_hien(path):
    snap, state = sent_draft(path)
    other = DraftStore(path=path).save(DraftSnapshot(keyword="bài khác"))
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute(
            "UPDATE drafts SET title = CAST(X'5375C3FF61' AS TEXT) WHERE id = ?", (snap.id,)
        )
    store = DraftStore(path=path)
    listing = store.list_drafts()
    assert [d.id for d in listing.drafts] == [other.id] and listing.skipped == 1
    assert store.recovered_from is None  # chỉ bỏ dòng, không cất cả file
    assert store.load_send_state(snap.id) == state  # khóa gửi trùng vẫn đọc được
    assert store.send_state_if_exists(snap.id) == (state, False)  # tab đang mở: nháp «còn»
    store.save(snap, must_exist=True)  # lần tự lưu kế của tab đang mở bài
    assert sorted(d.id for d in store.list_drafts().drafts) == sorted([snap.id, other.id])
    assert store.load_send_state(snap.id) == state

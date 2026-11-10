"""Lá Chắn T-131 (Fable 5.1): kho nháp sau khi kiểm file như ``search_cache``.

LC-T131-1 (Thấp, có từ trước T-131): file nháp bị chương trình khác sửa tay theo hai kiểu mà
bước kiểm file không nhận ra, làm một thao tác của kho báo «File nháp bị lỗi…» **mãi**, file không
được cất sang một bên, người dùng không có cách nào trong app để thoát:

- một ô TEXT của bảng ``drafts`` chứa UTF-8 hỏng: ``list_drafts`` lỗi ở mọi lần (danh sách nháp
  trống hẳn), dù ``load``, trạng thái gửi vẫn đọc được;
- byte 18 của đầu file («file format write version») lớn hơn 2: SQLite mở file **chỉ đọc**,
  đọc được nhưng mọi lần lưu báo «bị lỗi» (mã ``SQLITE_READONLY`` giữ file, đúng ý; nhưng câu báo
  sai và không bao giờ tự thoát), cùng lớp GN-1 của Soi Lỗi T-131 ở các kho lưu tạm.

Kỳ vọng (một trong hai cách đều được): thao tác không lỗi (bỏ qua dòng hỏng, báo câu), hay lần mở
sau cất file sang một bên (giữ lại) rồi dùng file mới. Không gọi mạng; mọi file trong ``tmp_path``.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

import pytest
import test_t131_kho_nhap as kho

from seo_app.storage.drafts import DraftError, DraftSnapshot, DraftStore

project = kho.project
path = kho.path


def utf8_hong_trong_o(file, draft_id: str) -> None:
    with closing(sqlite3.connect(file)) as conn, conn:
        conn.execute(
            "UPDATE drafts SET title = CAST(? AS TEXT) WHERE id = ?", (b"\xff\xfe x", draft_id)
        )


def byte_18_la_3(file, _draft_id: str) -> None:
    data = bytearray(file.read_bytes())
    data[18] = 3
    file.write_bytes(bytes(data))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "LC-T131-1 (la-chan, Thấp, có từ trước): ô TEXT có UTF-8 hỏng làm list_drafts lỗi mãi; "
        "byte 18 của đầu file > 2 làm mọi lần lưu lỗi mãi; file không được cất sang một bên"
    ),
)
@pytest.mark.parametrize(
    "damage", [utf8_hong_trong_o, byte_18_la_3], ids=["utf8-hong-trong-o", "byte-18-la-3"]
)
def test_lc_t131_1_hand_edited_draft_file_does_not_stay_stuck(path, damage):
    draft_id, _state = kho.seeded(path)
    damage(path, draft_id)
    store = DraftStore(path=path)
    failures = 0
    for _attempt in (1, 2):
        try:
            store.list_drafts()
            store.save(DraftSnapshot(keyword="nháp mới"))
        except DraftError:
            failures += 1
    # Lần hai phải qua (file đã cất đi và kho dùng file mới), hay không lỗi ngay từ đầu.
    assert failures < 2, "kho kẹt mãi ở câu báo lỗi, file không được cất sang một bên"

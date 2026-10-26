"""T-086: kho nháp nhớ trạng thái «Gửi nháp» (``SendState``, bảng riêng ``send_states``).

Lần tự lưu nháp không ghi đè trạng thái gửi; file nháp cũ (chưa có bảng) vẫn mở được; dòng trạng
thái hỏng là lỗi, không đoán; xóa hay dọn nháp thì bỏ trạng thái theo. Giao diện dùng trạng thái
này: ``tests/test_t086_send_state.py``.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing

import pytest

from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import MAX_SEND_STATE_BYTES, DraftError, SendState

STAMP = "2026-10-26T10:00:00+07:00"


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "drafts.sqlite")


def test_send_state_kept_apart_from_autosave(store):
    """Trạng thái gửi nằm ở bảng riêng: lần tự lưu nháp (``save``) không ghi đè nó, nó không đổi nội
    dung nháp; ``None`` thì xóa."""
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    assert store.load_send_state(snap.id) is None
    store.save_send_state(snap.id, SendState.now(pending=True, post_id=None))
    store.save(snap.model_copy(update={"keyword": "cổng inox Tân Phú"}))
    state = store.load_send_state(snap.id)
    assert state.pending and state.post_id is None and state.updated_at.utcoffset() is not None
    store.save_send_state(snap.id, SendState.now(pending=False, post_id=501))
    assert store.load_send_state(snap.id).post_id == 501
    assert store.load(snap.id).keyword == "cổng inox Tân Phú"
    store.save_send_state(snap.id, None)
    assert store.load_send_state(snap.id) is None


def test_old_draft_file_without_send_states_opens(tmp_path):
    """Yêu cầu 6: file nháp tạo trước T-086 (chỉ có bảng ``drafts``) mở được như trước, không bị
    cất sang một bên; nháp cũ không có trạng thái gửi; bảng mới được tạo thêm khi cần."""
    path = tmp_path / "drafts.sqlite"
    snap = DraftStore(path=path).save(DraftSnapshot(keyword="nháp cũ"))
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("DROP TABLE send_states")
    store = DraftStore(path=path)
    assert store.load(snap.id).keyword == "nháp cũ"
    assert store.load_send_state(snap.id) is None
    assert store.recovered_from is None
    store.save_send_state(snap.id, SendState.now(pending=False, post_id=7))
    assert store.load_send_state(snap.id).post_id == 7


@pytest.mark.parametrize(
    "data",
    [
        "không phải json",
        json.dumps({"pending": "true", "updated_at": STAMP}),  # chữ, không phải đúng/sai
        json.dumps({"post_id": "501", "updated_at": STAMP}),
        json.dumps({"post_id": True, "updated_at": STAMP}),  # không thành bài số 1
        json.dumps({"post_id": 501.0, "updated_at": STAMP}),
        json.dumps({"post_id": 0, "updated_at": STAMP}),
        json.dumps({"post_id": 2**63, "updated_at": STAMP}),
        json.dumps({"updated_at": "2026-10-26T10:00:00"}),  # thiếu múi giờ
        json.dumps({"pending": False}),  # thiếu giờ
        json.dumps({"pending": False, "updated_at": STAMP, "link": "https://evil.example"}),
        "x" * (MAX_SEND_STATE_BYTES + 1),
        b"\xff\xfe\x00",
    ],
)
def test_broken_send_state_is_an_error_not_a_guess(store, data):
    """Dòng trạng thái gửi sửa tay, hỏng: ``DraftError`` câu cố định (không chép gì từ file), không
    đoán; giao diện coi như chưa rõ kết quả (khóa nút, test ``…_in_draft_locks``)."""
    snap = store.save(DraftSnapshot())
    store.save_send_state(snap.id, SendState.now(pending=False, post_id=1))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE send_states SET data = ? WHERE id = ?", (data, snap.id))
    with pytest.raises(DraftError) as caught:
        store.load_send_state(snap.id)
    assert str(caught.value) == "Trạng thái gửi ghi trong nháp bị hỏng nên không đọc được."


def test_send_state_removed_with_its_draft(tmp_path):
    """Xóa nháp, hay nháp bị dọn (quá ``max_drafts``): trạng thái gửi của đúng nháp đó bỏ theo;
    trạng thái của nháp còn lại giữ nguyên."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_drafts=2)
    first = store.save(DraftSnapshot(keyword="một"))
    second = store.save(DraftSnapshot(keyword="hai"))
    for snap in (first, second):
        store.save_send_state(snap.id, SendState.now(pending=False, post_id=9))
    store.save(DraftSnapshot(keyword="ba"))  # dọn «một»
    with closing(sqlite3.connect(store.path)) as conn:
        kept = {row[0] for row in conn.execute("SELECT id FROM send_states")}
    assert kept == {second.id}
    assert store.delete(second.id)
    assert store.load_send_state(second.id) is None


def test_wrong_send_states_table_moves_file_aside(tmp_path):
    """Bảng ``send_states`` sai cột (sửa tay): như bảng ``drafts`` sai, file được cất sang bên."""
    path = tmp_path / "drafts.sqlite"
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("CREATE TABLE send_states (x TEXT)")
    store = DraftStore(path=path)
    store.save(DraftSnapshot())
    assert store.recovered_from is not None

"""T-130 (Họa Sĩ): giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa (khép khoảng hở cuối của
T-092).

Xóa nháp (hay kho đầy bỏ bớt) không còn xóa trạng thái gửi của nó: dòng đó ở lại thành dòng «mồ
côi» (không có nháp đi kèm), nên nháp được lưu lại ở **bất kỳ** tab nào, kể cả tab chưa từng thấy
lần gửi, vẫn khóa gửi trùng. Dòng mồ côi cũ được dọn: chỉ dòng không có nháp, giữ
``max_orphan_send_states`` dòng ghi gần nhất. Popover «🗑️ Xóa» của nháp đã gửi nhắc xóa nháp
không xóa bài trên website.

Ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; kho nháp trong thư mục tạm; không
gọi mạng thật.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

import pytest
import test_app_images as ui
import test_t086_send_state as t86
import test_t092_nhap_bi_xoa as t92

from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import MAX_ORPHAN_SEND_STATES, SendState

# Fixture dùng chung (mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL
notice = t92.notice
saved_ids = t92.saved_ids
KNOWN_SENT = t92.KNOWN_SENT
RECREATE = t92.RECREATE
AGAIN = "Tạo thêm một bài nháp mới"
NOT_ON_SITE = "Xóa nháp **không** xóa"


# ============================================================ kho nháp


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "drafts.sqlite")


def send_rows(store: DraftStore) -> dict[str, str]:
    """Mọi dòng trạng thái gửi, nguyên chữ trong file (kể cả dòng hỏng, dòng mồ côi)."""
    with closing(sqlite3.connect(store.path)) as conn:
        return dict(conn.execute("SELECT id, data FROM send_states").fetchall())


def sent_draft(store: DraftStore, keyword: str, post_id: int | None = 501, *, pending=False):
    """Một nháp kèm trạng thái gửi; trả (nháp, trạng thái)."""
    snap = store.save(DraftSnapshot(keyword=keyword))
    state = SendState.now(pending=pending, post_id=post_id)
    store.save_send_state(snap.id, state)
    return snap, state


STATES = {
    "da-gui": {"pending": False, "post_id": 501},
    "gui-do": {"pending": True, "post_id": None},
    "gui-tiep-chua-ro": {"pending": True, "post_id": 501},
}


@pytest.mark.parametrize("kind", [*STATES, "dong-hong"])
def test_delete_keeps_send_state_as_orphan(store, kind):
    """Xóa nháp đã gửi, đang gửi, gửi dở (hay dòng trạng thái gửi hỏng): dòng trạng thái gửi ở lại
    nguyên chữ, không có nháp đi kèm (``send_state_if_exists``: nháp không còn). Nháp được lưu
    lại (cùng mã) thì gắn lại đúng dòng đó."""
    spec = STATES.get(kind, STATES["da-gui"])
    snap, state = sent_draft(store, "cổng inox", spec["post_id"], pending=spec["pending"])
    if kind == "dong-hong":
        t92.break_send_state(store, snap.id)
    before = send_rows(store)
    assert store.delete(snap.id)
    assert store.list_drafts().drafts == []
    assert send_rows(store) == before
    assert store.send_state_if_exists(snap.id) is None
    store.save(snap)  # một tab còn mở bài này bấm «Lưu lại thành nháp»
    expected = (None, True) if kind == "dong-hong" else (state, False)
    assert store.send_state_if_exists(snap.id) == expected


def test_delete_unsent_draft_leaves_nothing(store):
    """Nháp chưa gửi: xóa như cũ, không có dòng trạng thái gửi nào."""
    snap = store.save(DraftSnapshot(keyword="chưa gửi"))
    assert store.delete(snap.id)
    assert send_rows(store) == {}
    assert store.load_send_state(snap.id) is None


def test_prune_keeps_send_state_of_pruned_draft(tmp_path):
    """Kho đầy bỏ bớt nháp cũ (``max_drafts``): trạng thái gửi của nháp bị bỏ cũng ở lại."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_drafts=2)
    old, state = sent_draft(store, "cũ nhất")
    store.save(DraftSnapshot(keyword="hai"))
    store.save(DraftSnapshot(keyword="ba"))
    assert old.id not in {d.id for d in store.list_drafts().drafts}
    assert store.load_send_state(old.id) == state


def test_orphans_trimmed_to_newest(tmp_path):
    """Dòng mồ côi quá giới hạn: giữ đúng các dòng ghi gần nhất, bỏ dòng cũ hơn."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_orphan_send_states=3)
    drafts = [sent_draft(store, f"bài {n}")[0] for n in range(5)]
    for snap in drafts:
        assert store.delete(snap.id)
    assert set(send_rows(store)) == {snap.id for snap in drafts[2:]}


def test_trim_never_touches_send_state_of_existing_draft(tmp_path):
    """Dọn dòng mồ côi không bao giờ đụng trạng thái gửi của nháp còn trong kho, kể cả khi dòng
    đó cũ hơn mọi dòng mồ côi (ghi trước tiên) hay hỏng."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_orphan_send_states=1)
    keep, keep_state = sent_draft(store, "còn trong kho")
    broken, _ = sent_draft(store, "còn, dòng hỏng")
    t92.break_send_state(store, broken.id)
    orphans = [sent_draft(store, f"xóa {n}")[0] for n in range(3)]
    for snap in orphans:
        assert store.delete(snap.id)
    rows = send_rows(store)
    assert set(rows) == {keep.id, broken.id, orphans[-1].id}
    assert store.send_state_if_exists(keep.id) == (keep_state, False)
    assert store.send_state_if_exists(broken.id) == (None, True)


def test_trim_order_follows_last_write(tmp_path):
    """Thứ tự dọn theo lần ghi gần nhất: dòng mồ côi vừa được ghi lại (kết quả lần gửi ghi sau lúc
    xóa, SL-T089-2) là dòng mới nhất, được giữ; dòng cũ hơn bị dọn ở lần lưu, lần xóa kế tiếp."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_orphan_send_states=1)
    first, _ = sent_draft(store, "một")
    second, _ = sent_draft(store, "hai")
    assert store.delete(second.id)  # dòng «hai» mồ côi
    assert store.delete(first.id)  # dòng «một» mồ côi, ghi trước «hai» nên bị dọn ngay
    assert set(send_rows(store)) == {second.id}
    result = SendState.now(pending=False, post_id=777)
    store.save_send_state(first.id, result)  # lần gửi đang chạy ghi kết quả sau lúc xóa
    store.save(DraftSnapshot(keyword="nháp khác"))  # lần lưu nào đó dọn dòng mồ côi
    assert set(send_rows(store)) == {first.id}
    assert store.load_send_state(first.id) == result


def test_trim_zero_keeps_no_orphan(tmp_path):
    """Giới hạn 0: xóa nháp là bỏ luôn trạng thái gửi (như trước T-130); không âm."""
    for keep in (0, -5):
        store = DraftStore(path=tmp_path / f"drafts{keep}.sqlite", max_orphan_send_states=keep)
        snap, _ = sent_draft(store, "cổng")
        assert store.delete(snap.id)
        assert send_rows(store) == {}


def test_trim_skips_when_drafts_table_has_null_id(store):
    """Bảng nháp bị sửa tay có dòng mã ``NULL``: ``NOT IN`` không bao giờ đúng nên không dọn gì
    (hướng an toàn: thừa dòng, không mất khóa); bỏ dòng lạ đó thì dọn lại như thường."""
    store.max_orphan_send_states = 1
    store.save(DraftSnapshot(keyword="tạo bảng"))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute(
            "INSERT INTO drafts (id, title, keyword, saved_at, saved_ts, data) "
            "VALUES (NULL, 't', 'k', '2026-11-05T00:00:00+07:00', 0, '{}')"
        )
    orphans = [sent_draft(store, f"xóa {n}")[0] for n in range(3)]
    for snap in orphans:
        assert store.delete(snap.id)
    assert {snap.id for snap in orphans} <= set(send_rows(store))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("DELETE FROM drafts WHERE id IS NULL")
    store.save(DraftSnapshot(keyword="lần lưu sau"))
    assert set(send_rows(store)) == {orphans[-1].id}


def test_default_orphan_limit():
    """Giới hạn mặc định như việc ghi Sheet còn nợ (T-100): 200 dòng."""
    assert MAX_ORPHAN_SEND_STATES == 200
    assert DraftStore().max_orphan_send_states == MAX_ORPHAN_SEND_STATES


# ============================================================ trang Soạn bài


def test_unknowing_tab_saves_back_and_stays_locked(project_root, root, fake_ai, site):
    """Khoảng hở cuối của T-092: tab 1 mở nháp từ trước, chưa từng thấy lần gửi; tab 2 gửi xong
    (bài 777) rồi xóa nháp. Tab 1 làm tiếp: khung báo nói tab biết bài đã gửi (đọc dòng giữ lại).
    Bấm «Lưu lại thành nháp»: nháp có lại kèm đúng «đã gửi 777»; bước Xuất bản của tab 1 và phiên
    mới mở nháp đều khóa (phải tick «Tạo thêm…»); website không có bài thứ hai."""
    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    other = SendState.now(pending=False, post_id=777)
    ui.store().save_send_state(draft, other)  # tab 2 gửi xong …
    assert ui.store().delete(draft)  # … rồi xóa nháp, trước khi tab 1 chạy lại
    at.session_state["step"] = 1
    run_ok(at.run())
    assert draft not in saved_ids()
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert draft in saved_ids()
    assert ui.store().load_send_state(draft) == other
    ui.to_publish(at)
    assert button(at, SEND).disabled
    assert any(box.label == AGAIN for box in at.checkbox)
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
    assert any(box.label == AGAIN for box in fresh.checkbox)
    assert site.posts() == []


def test_draft_saved_back_by_unknowing_tab_locks_fresh_session(project_root, root, fake_ai, site):
    """G1 của Soi Lỗi T-092 với phiên mới: tab đã biết «đã gửi 777»; nháp bị xóa, tab khác (không
    biết) lưu lại nháp. Nay dòng giữ lại gắn lại theo mã nháp: kho có «đã gửi 777», tab đã biết và
    phiên mới mở nháp đều khóa."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = t92.seen_sent_elsewhere(at)
    snap = ui.store().load(draft)
    assert ui.store().delete(draft)
    ui.store().save(snap)  # tab khác bấm «Lưu lại thành nháp», không biết bài đã gửi
    run_ok(at.run())
    assert notice(at) == "" and button(at, SEND).disabled
    assert ui.store().load_send_state(draft).post_id == 777
    assert button(t86.reopen(project_root, draft), SEND).disabled
    assert site.posts() == []


def test_recreate_does_not_overwrite_row_written_in_between(
    project_root, root, fake_ai, site, monkeypatch
):
    """«Lưu lại thành nháp» đọc dòng giữ lại (tab biết «đã gửi 501») rồi mới ghi điều tab biết,
    so rồi đặt với «chưa gửi»: tab khác ghi kết quả mới (bài 888) đúng giữa hai bước đó thì lần
    ghi không đè, nháp có lại mang đúng kết quả mới. Từ T-130, đây là đường duy nhất còn để dòng
    trong kho mới hơn điều tab biết lúc lưu lại (``test_recreate_keeps_newer_row_written_after_
    delete`` của T-092 nay đọc được dòng mới trước khi ghi)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)  # tab này biết «đã gửi 501»
    draft = at.session_state["draft_id"]
    assert ui.store().delete(draft)
    at.session_state["step"] = 2
    run_ok(at.run())
    newer = SendState.now(pending=False, post_id=888)
    original = DraftStore.save_send_state
    raced: list[str] = []

    def write_in_between(self, draft_id, state, **kwargs):
        if not raced:
            raced.append(draft_id)
            original(self, draft_id, newer)  # tab khác ghi kết quả mới đúng lúc này
        return original(self, draft_id, state, **kwargs)

    monkeypatch.setattr(DraftStore, "save_send_state", write_in_between)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert raced == [draft]
    assert draft in saved_ids()
    assert ui.store().load_send_state(draft) == newer


def delete_popovers(at) -> dict[str, list[str]]:
    """Câu nhắc trong popover «🗑️ Xóa» của từng nháp: {mã nháp: [câu cảnh báo]}."""
    found: dict[str, list[str]] = {}
    for popover in at.get("popover"):
        if popover.proto.popover.label != "🗑️ Xóa":
            continue
        (delete,) = [b for b in popover.button if b.label == "Xóa hẳn"]
        found[delete.key.removeprefix("del-")] = [w.value for w in popover.warning]
    return found


def test_delete_popover_warns_for_sent_draft(project_root):
    """Đề xuất 2 (T-092): popover «🗑️ Xóa» của nháp đã gửi nhắc bài đã lên website (mã bài) và xóa
    nháp không xóa bài trên website; gửi dở, chưa rõ kết quả, dòng hỏng: nhắc có thể đã có bài;
    nháp chưa gửi: không nhắc. Bấm «Xóa hẳn» nháp đã gửi: nháp mất, trạng thái gửi ở lại."""
    store = ui.store()
    sent, sent_state = sent_draft(store, "đã gửi", 501)
    unsure, _ = sent_draft(store, "gửi dở", None, pending=True)
    released = store.save(DraftSnapshot(keyword="hẹn giờ chưa rõ"))
    store.save_send_state(
        released.id,
        SendState.now(pending=False, post_id=502, mode="publish", release_unknown=True),
    )
    broken, _ = sent_draft(store, "dòng hỏng", 503)
    t92.break_send_state(store, broken.id)
    fresh = store.save(DraftSnapshot(keyword="chưa gửi"))
    at = ui.pages.open_page(project_root, "write.py")
    found = delete_popovers(at)
    assert found[fresh.id] == []
    (warning,) = found[sent.id]
    assert "đã gửi lên website (bài mã 501)" in warning and NOT_ON_SITE in warning
    for other in (unsure, released, broken):
        (warning,) = found[other.id]
        assert "chưa rõ kết quả" in warning and NOT_ON_SITE in warning
        assert "bài mã" not in warning
    run_ok(button(at, "Xóa hẳn", key=f"del-{sent.id}").click().run())
    assert sent.id not in saved_ids()
    assert ui.store().load_send_state(sent.id) == sent_state
    assert sent.id not in delete_popovers(at)

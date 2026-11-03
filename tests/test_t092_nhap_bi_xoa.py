"""T-092 (Họa Sĩ): nháp bị xóa ở một tab trong khi tab khác còn mở bài đó.

Trước T-092, lần tự lưu của tab còn mở lặng lẽ tạo lại nháp (``INSERT OR REPLACE``) mà không có
trạng thái gửi (``delete`` xóa cả hai): bài đã gửi mất khóa gửi trùng. Nay kho nháp ghi đè kiểu so
rồi đặt (``DraftStore.save(..., must_exist=True)``), đọc trạng thái gửi kèm kiểm nháp còn
(``send_state_if_exists``); trang báo rõ, hỏi «💾 Lưu lại thành nháp» / «🗑️ Bỏ bài này»; lưu lại
thì ghi lại trạng thái gửi tab đó biết. Kèm yêu cầu 3 (nháp cũ vẫn mở được) và yêu cầu 5 (chú
thích «Chép sang SiteSEO», ``.env.example``).

Ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; kho nháp trong thư mục tạm; không
gọi mạng thật.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing, contextmanager
from types import SimpleNamespace

import pytest
import test_app_images as ui
import test_drafts_images as old_drafts
import test_t041_seo_ui as t41
import test_t086_send_state as t86

from seo_app.storage import DraftSnapshot, DraftStore, new_draft_id
from seo_app.storage.drafts import SCHEMA_VERSION, DraftError, DraftGoneError, SendState

# Fixture dùng chung (mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả,
# cache danh sách bài đã đăng tạm).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
site_cache = t41.site_cache

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL
UNSURE = t86.UNSURE
GONE = "không còn trong kho nháp"
KNOWN_SENT = "Tab này biết bài đã gửi"
NOT_KNOWN = "Nếu bài đã được gửi lên website ở tab khác"
RECREATE = "💾 Lưu lại thành nháp"
MSG_GONE = "Nháp này không còn trong kho nháp (có thể vừa bị xóa ở tab khác)."


# ============================================================ kho nháp


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "drafts.sqlite")


def send_rows(store: DraftStore) -> dict[str, str]:
    with closing(sqlite3.connect(store.path)) as conn:
        return dict(conn.execute("SELECT id, data FROM send_states").fetchall())


def break_send_state(store: DraftStore, draft_id: str) -> None:
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE send_states SET data = ? WHERE id = ?", ("{hỏng", draft_id))


def test_must_exist_does_not_recreate_deleted_draft(store):
    """Nháp đã bị xóa (cả trạng thái gửi): lần ghi đè so rồi đặt không ghi gì, báo lỗi riêng (một
    dạng ``DraftError``, câu cố định)."""
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    store.save_send_state(snap.id, SendState.now(pending=False, post_id=501))
    assert store.delete(snap.id)
    with pytest.raises(DraftGoneError) as caught:
        store.save(snap.model_copy(update={"keyword": "sửa sau khi xóa"}), must_exist=True)
    assert isinstance(caught.value, DraftError)
    assert str(caught.value) == MSG_GONE
    assert store.list_drafts().drafts == []
    assert send_rows(store) == {}


def test_must_exist_overwrites_draft_still_there(store):
    """Nháp còn: ghi đè như cũ, không đụng trạng thái gửi."""
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    state = SendState.now(pending=False, post_id=501)
    store.save_send_state(snap.id, state)
    store.save(snap.model_copy(update={"keyword": "cổng inox Tân Phú"}), must_exist=True)
    assert store.load(snap.id).keyword == "cổng inox Tân Phú"
    assert store.load_send_state(snap.id) == state


def test_must_exist_after_prune_or_drafts_file_removed(tmp_path):
    """Nháp bị bỏ vì kho đầy, hay cả file nháp bị xóa khi app đang chạy: cũng không tạo lại. Lần
    lưu thường (không ``must_exist``) vẫn tạo mới như trước (nháp mới, Soi Lỗi R8-1)."""
    store = DraftStore(path=tmp_path / "data" / "drafts.sqlite", max_drafts=2)
    first = store.save(DraftSnapshot(keyword="một"))
    store.save(DraftSnapshot(keyword="hai"))
    store.save(DraftSnapshot(keyword="ba"))  # dọn «một»
    with pytest.raises(DraftGoneError):
        store.save(first, must_exist=True)
    assert "một" not in [d.keyword for d in store.list_drafts().drafts]
    kept = store.save(DraftSnapshot(keyword="bốn"))
    store.path.unlink()
    with pytest.raises(DraftGoneError):
        store.save(kept, must_exist=True)
    assert store.list_drafts().drafts == []
    again = store.save(kept)
    assert [d.id for d in store.list_drafts().drafts] == [again.id]


def test_send_state_if_exists(store):
    """Trạng thái gửi kèm kiểm nháp còn: ``(trạng thái, hỏng)`` như ``expected`` của
    ``save_send_state``; ``None`` khi nháp không còn, kể cả khi còn dòng trạng thái gửi không có
    nháp đi kèm (kết quả lần gửi ghi sau lúc xóa, SL-T089-2)."""
    snap = store.save(DraftSnapshot(keyword="cổng"))
    assert store.send_state_if_exists(snap.id) == (None, False)
    state = SendState.now(pending=True, post_id=None)
    store.save_send_state(snap.id, state)
    assert store.send_state_if_exists(snap.id) == (state, False)
    break_send_state(store, snap.id)
    assert store.send_state_if_exists(snap.id) == (None, True)
    assert store.delete(snap.id)
    assert store.send_state_if_exists(snap.id) is None
    store.save_send_state(snap.id, state)  # dòng mồ côi
    assert store.send_state_if_exists(snap.id) is None
    assert store.send_state_if_exists(new_draft_id()) is None
    with pytest.raises(DraftError):
        store.send_state_if_exists("../nhap")


class RacingConnection:
    """Kết nối thật; đọc xong dòng của lần kiểm «nháp còn» thì chạy ``after_check`` (tab khác bấm
    «Xóa hẳn» đúng lúc đó), rồi mới làm tiếp."""

    def __init__(self, conn: sqlite3.Connection, after_check) -> None:
        self.conn, self.after_check = conn, after_check

    def execute(self, sql: str, params=()):
        cursor = self.conn.execute(sql, params)
        if not sql.startswith("SELECT 1 FROM drafts"):
            return cursor
        row = cursor.fetchone()
        self.after_check()
        return SimpleNamespace(fetchone=lambda: row)


def racing(store: DraftStore, draft_id: str) -> list[str]:
    """Mỗi lần kiểm «nháp còn», một kết nối khác (như tab khác) thử xóa nháp và trạng thái gửi
    của nó, chờ khóa rất ngắn. Trả danh sách kết quả các lần thử."""
    attempts: list[str] = []
    connect = store._connect

    def delete_now() -> None:
        try:
            with closing(sqlite3.connect(store.path, timeout=0.1)) as other, other:
                other.execute("DELETE FROM send_states WHERE id = ?", (draft_id,))
                other.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            attempts.append("đã xóa")
        except sqlite3.OperationalError:
            attempts.append("bận")

    @contextmanager
    def racing_connect():
        with connect() as conn:
            yield RacingConnection(conn, delete_now)

    store._connect = racing_connect
    return attempts


def test_must_exist_check_and_write_in_one_write_transaction(store):
    """So rồi đặt giữ khóa ghi từ trước lần kiểm: tab khác xóa đúng lúc giữa lần kiểm và lần ghi
    thì phải đợi (ở đây: báo bận), không có chuyện xóa xong rồi nháp lại được ghi."""
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    attempts = racing(store, snap.id)
    store.save(snap.model_copy(update={"keyword": "đã sửa"}), must_exist=True)
    assert attempts == ["bận"]
    assert store.load(snap.id).keyword == "đã sửa"


def test_send_state_if_exists_reads_in_one_transaction(store):
    """Kiểm nháp còn và đọc trạng thái gửi trong một giao dịch đọc: lần xóa ở tab khác không chen
    vào giữa, nên không đọc ra «nháp còn, chưa gửi» cho nháp đã gửi."""
    snap = store.save(DraftSnapshot(keyword="cổng inox"))
    state = SendState.now(pending=False, post_id=501)
    store.save_send_state(snap.id, state)
    attempts = racing(store, snap.id)
    assert store.send_state_if_exists(snap.id) == (state, False)
    assert attempts == ["bận"]


# ============================================================ trang Soạn bài, hai tab


def notice(at) -> str:
    """Câu báo nháp không còn trong kho (rỗng: không có)."""
    return next((w.value for w in at.warning if GONE in w.value), "")


def saved_ids() -> list[str]:
    return [d.id for d in ui.store().list_drafts().drafts]


def saved_captions(at) -> list[str]:
    return [c.value for c in at.caption if c.value.startswith("💾 Đã lưu lúc")]


def test_autosave_does_not_recreate_draft_deleted_in_other_tab(project_root):
    """Tab 1 mở nháp; tab 2 bấm «🗑️ Xóa» → «Xóa hẳn» đúng nháp đó. Tab 1 làm tiếp: không lặng lẽ
    tạo lại nháp; trang báo rõ (thay cho «💾 Đã lưu lúc»), hỏi lưu lại hay bỏ. Tab 1 chưa từng thấy
    trạng thái gửi nào nên nhắc: gửi ở tab khác thì tab này không biết."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    other = ui.pages.open_page(project_root, "write.py")
    run_ok(button(other, "Xóa hẳn", key=f"del-{draft}").click().run())
    assert saved_ids() == []
    at.session_state["step"] = 1
    run_ok(at.run())
    assert saved_ids() == []
    text = notice(at)
    assert NOT_KNOWN in text and KNOWN_SENT not in text
    assert button(at, RECREATE, key="draft-recreate")
    assert button(at, "Bỏ hẳn", key="draft-discard")
    assert saved_captions(at) == []
    run_ok(at.run())  # chạy lại không sửa gì: vẫn báo, vẫn không tạo lại
    assert notice(at) and saved_ids() == []


def test_recreate_on_request_keeps_content(project_root):
    """Bấm «💾 Lưu lại thành nháp»: nháp có lại đúng mã cũ, đúng nội dung tab đang có; hết báo, lại
    «💾 Đã lưu lúc»; sửa tiếp thì tự lưu như thường."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    assert ui.store().delete(draft)
    at.session_state["step"] = 1
    run_ok(at.run())
    assert notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert saved_ids() == [draft]
    assert ui.store().load(draft).step == 1
    assert ui.store().load_send_state(draft) is None  # tab không biết gì: không bịa trạng thái
    assert notice(at) == "" and saved_captions(at)
    at.session_state["step"] = 0
    run_ok(at.run())
    assert ui.store().load(draft).step == 0


def test_recreate_keeps_sent_state_this_tab_knows(project_root, root, fake_ai, site):
    """Tab 1 gửi xong (bài 501), tab 2 xóa nháp. Tab 1 làm tiếp: báo nháp không còn, nói tab này
    biết bài đã gửi. Lưu lại: nháp có lại kèm đúng «đã gửi 501»; phiên mới mở nháp vẫn khóa nút
    (phải tick «Tạo thêm một bài nháp mới»), website vẫn chỉ có một bài."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    draft = at.session_state["draft_id"]
    sent = ui.store().load_send_state(draft)
    assert sent is not None and sent.post_id == ui.POST_ID and not sent.pending
    assert ui.store().delete(draft)  # tab 2 bấm «Xóa hẳn»
    at.session_state["step"] = 2
    run_ok(at.run())
    assert draft not in saved_ids()
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert draft in saved_ids()
    assert ui.store().load_send_state(draft) == sent
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
    assert any(box.label == "Tạo thêm một bài nháp mới" for box in fresh.checkbox)
    assert len(site.posts()) == 1


def test_sent_state_seen_at_publish_step_is_known(project_root, root, fake_ai, site, monkeypatch):
    """Tab khác gửi xong (bài 777); tab này đang ở bước Xuất bản, vẽ lại thì thấy «đã gửi 777» (chỉ
    lần đọc ở đó, ``_wp_seen``, biết: tab này không gửi gì, lần tự lưu trước đọc ra «chưa gửi»).
    Nháp bị xóa ngay sau lần đọc đó, trước lần tự lưu của lần chạy. Tab vẫn biết «đã gửi 777»,
    vẽ lại bước Xuất bản (đọc ra «chưa gửi» vì dòng đã bị xóa cùng nháp) vẫn nhớ; lưu lại vẫn
    khóa."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    other = SendState.now(pending=False, post_id=777)
    ui.store().save_send_state(draft, other)  # tab khác gửi xong
    original = DraftStore.send_state_if_exists
    deleted: list[str] = []

    def delete_before_autosave(self, draft_id):
        if not deleted:
            deleted.append(draft_id)
            self.delete(draft_id)  # tab khác xóa nháp ngay sau lần đọc ở bước Xuất bản
        return original(self, draft_id)

    monkeypatch.setattr(DraftStore, "send_state_if_exists", delete_before_autosave)
    run_ok(at.run())
    assert deleted == [draft]
    assert any("đã gửi lên WordPress" in i.value for i in at.info)  # bước Xuất bản thấy «777»
    assert draft not in saved_ids()
    assert KNOWN_SENT in notice(at)
    run_ok(at.run())  # vẽ lại bước Xuất bản: lần đọc ở đó ra «chưa gửi», tab vẫn nhớ
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert ui.store().load_send_state(draft) == other
    assert button(t86.reopen(project_root, draft), SEND).disabled
    assert site.posts() == []


def test_own_send_known_when_deleted_before_any_read(
    project_root, root, fake_ai, site, monkeypatch
):
    """Nháp bị xóa ngay khi lần gửi của tab này vừa ghi «đã gửi 501», trước mọi lần đọc sau đó
    (cả ở bước Xuất bản): không lần đọc nào thấy gì, nhưng tab biết chính nó đã gửi bài 501
    (``_wp_sent``, kết quả lần gửi). Tab vẫn đứng ở bước Xuất bản, vẽ lại nhiều lần (mỗi lần đọc
    ra «chưa gửi»): lưu lại vẫn khóa «đã gửi 501»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    original = DraftStore.load_send_state
    deleted: list[str] = []

    def delete_then_read(self, draft_id):
        state = original(self, draft_id)
        if not deleted and state is not None and not state.pending:
            deleted.append(draft_id)
            self.delete(draft_id)  # tab 2 xóa đúng lúc lần gửi vừa ghi xong
            return original(self, draft_id)
        return state

    monkeypatch.setattr(DraftStore, "load_send_state", delete_then_read)
    ui.send(at)
    assert deleted == [draft]
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    assert KNOWN_SENT in notice(at)
    run_ok(at.run())  # vẽ lại bước Xuất bản: đọc ra «chưa gửi», tab vẫn nhớ
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    state = ui.store().load_send_state(draft)
    assert state is not None and state.post_id == ui.POST_ID and not state.pending
    assert button(t86.reopen(project_root, draft), SEND).disabled


@pytest.mark.parametrize("kind", ["gửi dở", "dòng hỏng"])
def test_recreate_keeps_unsure_lock(project_root, root, fake_ai, site, kind):
    """Tab này thấy khóa «gửi dở» (lần gửi trước chưa rõ kết quả, hay dòng trạng thái gửi hỏng)
    rồi nháp bị xóa ở tab khác: lưu lại thì nháp vẫn khóa «gửi dở» (dòng hỏng thành «chưa rõ kết
    quả»), phiên mới phải xác nhận đã kiểm trang quản trị mới gửi được."""
    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=True, post_id=None))
    if kind == "dòng hỏng":
        break_send_state(ui.store(), draft)
    ui.to_publish(at)
    assert button(at, SEND).disabled
    assert ui.store().delete(draft)
    at.session_state["step"] = 2
    run_ok(at.run())
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    state = ui.store().load_send_state(draft)
    assert state is not None and state.pending and state.post_id is None
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
    assert any(UNSURE in e.value for e in fresh.error)
    assert site.posts() == []


def test_recreate_keeps_newer_row_written_after_delete(project_root, root, fake_ai, site):
    """Dòng trạng thái gửi ghi sau lúc xóa (kết quả lần gửi ở tab khác, SL-T089-2) mới hơn cái tab
    này biết: lưu lại không ghi đè (so rồi đặt với «chưa gửi»)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    draft = at.session_state["draft_id"]
    at.session_state["step"] = 2
    run_ok(at.run())  # tab này biết «đã gửi 501»
    assert ui.store().delete(draft)
    newer = SendState.now(pending=False, post_id=777)
    ui.store().save_send_state(draft, newer)
    run_ok(at.run())
    assert notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert draft in saved_ids()
    assert ui.store().load_send_state(draft) == newer


@pytest.mark.parametrize("failing", ["save_send_state", "save"])
def test_recreate_writes_send_state_before_draft(
    project_root, root, fake_ai, site, monkeypatch, failing
):
    """«Lưu lại thành nháp» ghi trạng thái gửi trước rồi mới tạo lại nháp: hỏng ở bước nào thì
    cũng không có nháp tạo lại thiếu khóa (hỏng ở bước sau chỉ còn dòng trạng thái gửi, vô hại).
    Trang vẫn báo và hỏi, kèm lý do; bấm lại khi hết lỗi thì được."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    draft = at.session_state["draft_id"]
    assert ui.store().delete(draft)
    at.session_state["step"] = 2
    run_ok(at.run())
    original = getattr(DraftStore, failing)

    def busy(self, *args, **kwargs):
        raise DraftError(t86.BUSY)

    monkeypatch.setattr(DraftStore, failing, busy)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert draft not in saved_ids()
    state = ui.store().load_send_state(draft)
    if failing == "save":
        assert state is not None and state.post_id == ui.POST_ID
    else:
        assert state is None
    text = notice(at)
    assert "Chưa lưu lại được" in text and "File nháp đang bận" in text
    monkeypatch.setattr(DraftStore, failing, original)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert draft in saved_ids()
    assert ui.store().load_send_state(draft).post_id == ui.POST_ID


def test_deleted_between_check_and_save_is_not_recreated(project_root, monkeypatch):
    """Tab khác xóa nháp ngay sau lần kiểm «nháp còn» của lần tự lưu, trước lần ghi: lần ghi so
    rồi đặt từ chối (``DraftGoneError``), trang báo như trên, không tạo lại."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    original = DraftStore.send_state_if_exists

    def check_then_delete(self, draft_id):
        found = original(self, draft_id)
        self.delete(draft_id)
        return found

    monkeypatch.setattr(DraftStore, "send_state_if_exists", check_then_delete)
    at.session_state["step"] = 1
    run_ok(at.run())
    assert draft not in saved_ids()
    assert notice(at)


def test_discard_clears_page_and_never_recreates(project_root):
    """«🗑️ Bỏ bài này» → «Bỏ hẳn»: trang trống như khi xóa đúng nháp đang mở; sang trang khác rồi
    quay lại không làm sống lại bài, không tạo lại nháp."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    assert ui.store().delete(draft)
    run_ok(at.run())
    assert notice(at)
    run_ok(button(at, "Bỏ hẳn", key="draft-discard").click().run())
    assert notice(at) == ""
    assert at.session_state["keyword"] == ""
    assert "draft_id" not in at.session_state
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert saved_ids() == []
    assert at.session_state["keyword"] == ""


def test_two_tabs_editing_same_draft_still_autosave(project_root):
    """Hai tab cùng mở một nháp còn trong kho, cùng sửa: cả hai vẫn tự lưu (tab lưu sau ghi đè,
    như trước T-092), không báo nhầm «không còn trong kho»."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    other = ui.pages.open_page(project_root, "write.py")
    run_ok(button(other, "Mở", key=f"open-{draft}").click().run())
    at.session_state["step"] = 1
    run_ok(at.run())
    assert ui.store().load(draft).step == 1
    other.session_state["step"] = 0
    run_ok(other.run())
    assert ui.store().load(draft).step == 0
    run_ok(at.run())
    assert notice(at) == "" and notice(other) == ""
    assert saved_captions(at) and saved_captions(other)
    assert saved_ids() == [draft]


def test_new_draft_first_save_still_creates(project_root):
    """Bài mới (chưa có nháp): lần tự lưu đầu vẫn tạo nháp, không bị coi là «không còn»."""
    at = ui.pages.open_page(project_root, "write.py")
    run_ok(at.text_input(key="keyword").input("sửa cổng inox Tân Phú").run())
    (draft,) = saved_ids()
    assert at.session_state["draft_id"] == draft
    assert notice(at) == "" and saved_captions(at)


def test_old_draft_still_opens_and_saves(project_root):
    """Yêu cầu 3: nháp khuôn cũ (khuôn 1, trước T-055) vẫn mở được; sửa thì lần tự lưu so rồi đặt
    ghi được (nháp còn), nâng lên khuôn mới; không báo nhầm."""
    data = old_drafts.v1_draft(new_draft_id())
    old_drafts.put_v1(ui.store(), data)
    at = ui.pages.open_page(project_root, "write.py")
    run_ok(button(at, "Mở", key=f"open-{data['id']}").click().run())
    assert at.session_state["article_title"] == data["article_title"]
    assert notice(at) == ""
    at.session_state["step"] = 1
    run_ok(at.run())
    stored = json.loads(old_drafts.read_row(ui.store(), data["id"]))
    assert stored["schema_version"] == SCHEMA_VERSION and stored["step"] == 1
    assert notice(at) == "" and saved_captions(at)


# ============================================================ yêu cầu 5


def test_siteseo_caption_says_where_each_box_goes(project_root):
    """Chú thích «Chép sang SiteSEO» (Lá Chắn T-095): tiêu đề, mô tả dán vào hộp SiteSEO; đường dẫn
    dán vào ô đường dẫn (slug) của bài, khớp README mục 10."""
    at = t41.to_seo(project_root)
    caption = next(c.value for c in at.caption if c.value.startswith("Bấm biểu tượng ở góc"))
    where = "tiêu đề, mô tả dán vào hộp SiteSEO; đường dẫn dán vào ô đường dẫn (slug) của bài"
    assert where in caption
    assert where in (project_root / "README.md").read_text(encoding="utf-8")
    assert "dán vào hộp SiteSEO của bài nháp" not in caption


def comment_above(lines: list[str], name: str) -> str:
    """Các dòng chú thích liền ngay trên dòng ``NAME=`` của ``.env.example``, nối thành một câu."""
    index = next(i for i, line in enumerate(lines) if line.startswith(f"{name}="))
    block: list[str] = []
    for line in reversed(lines[:index]):
        if not line.startswith("#"):
            break
        block.insert(0, line.lstrip("# "))
    return " ".join(block)


def test_env_example_names_the_editor_account(project_root):
    """Chú thích hai dòng WordPress (Lá Chắn T-095, đúng chỗ đã nhầm hôm 27/10): tên đăng nhập của
    tài khoản Biên tập viên riêng, không phải tên đặt cho mật khẩu ứng dụng; mật khẩu ứng dụng tạo
    trên chính tài khoản đó."""
    lines = (project_root / ".env.example").read_text(encoding="utf-8").splitlines()
    user = comment_above(lines, "WORDPRESS_USERNAME")
    assert "Tên đăng nhập của tài khoản Biên tập viên riêng" in user
    assert "không phải tên đặt cho Application Password" in user
    assert "tạo trên chính tài khoản đó" in comment_above(lines, "WORDPRESS_APP_PASSWORD")

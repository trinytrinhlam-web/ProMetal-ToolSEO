"""T-089: dọn lỗi Thấp của «Gửi nháp» sau T-086 (LC-T086-1, SL-T086-1, SL-T086-2) và lưu băm ảnh
đã duyệt trong nháp (Ghi nhận 1 của Lá Chắn T-086).

- LC-T086-1: website trả mã bài ngoài khoảng nháp ghi được: câu cố định, trang không lỗi, vẫn khóa.
- SL-T086-1: «đang gửi» ghi kiểu so rồi đặt trong một giao dịch SQLite (``save_send_state`` có
  ``expected``): tab thứ hai cùng bài bị khóa, có câu nhắc; xác nhận đã tick sẵn không dùng được cho
  trạng thái mới do tab khác ghi.

Dùng lại ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; không gọi mạng thật.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from contextlib import closing

import pytest
import test_app_images as ui
import test_soi_loi_t056 as sl
import test_t086_send_state as t86

import seo_app.storage.drafts as drafts
from seo_app.images.folders import ImageLibrary
from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import SendState

# Fixture dùng chung (mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL
UNSURE = "bài nháp có thể đã có trên website"
HUGE_ID = 2**63
NOTE = "website trả mã bài nháp lớn bất thường, app không ghi được vào nháp"
ELSEWHERE = "Chưa gửi gì lên website: bài này vừa được gửi (hoặc đang gửi) ở một tab khác của app"


def draft_id(at) -> str:
    return at.session_state["draft_id"]


# ================================================================== LC-T086-1: mã bài lạ


def huge_post_id(site) -> None:
    site.fake.on(
        "POST",
        ui.POSTS,
        lambda _r: (201, {"id": HUGE_ID, "status": "draft", "title": {"raw": "T"}}, {}),
    )


def assert_huge_id_reported_and_locked(at, site) -> None:
    assert len(site.posts()) == 1
    assert any(NOTE in w.value for w in at.warning)  # câu cố định, không dấu vết lỗi
    assert any(f"mã {HUGE_ID}" in s.value for s in at.success)
    assert ui.store().load_send_state(draft_id(at)).pending  # nháp giữ «đang gửi»
    assert button(at, SEND).disabled
    for _ in range(2):  # các lần chạy sau không lỗi lại, vẫn khóa, không gửi thêm
        run_ok(at.run())
        assert button(at, SEND).disabled
    assert len(site.posts()) == 1


def test_huge_post_id_fixed_note_and_lock(project_root, root, fake_ai, site):
    """LC-T086-1: ``SendState`` dựng trong khối bắt lỗi của ``record_outcome``: trang hiện kết quả
    kèm câu cố định «chưa ghi được kết quả vào nháp», nháp giữ «đang gửi», nút khóa."""
    at, _pid = ui.open_article(project_root)
    ui.to_publish(at)
    huge_post_id(site)
    ui.send(at)
    assert "_wp_sending" not in at.session_state
    assert_huge_id_reported_and_locked(at, site)


def test_huge_post_id_when_run_interrupted(project_root, root, fake_ai, site, monkeypatch):
    """Như trên, nhưng lần chạy bị ngắt trong lúc gửi: ``finish_send`` thử ghi lại kết quả ở lần
    chạy sau, cũng ra câu cố định (không lặp lỗi ở mọi lần chạy như trước), bỏ dấu «đang gửi»."""
    sl.interrupt_while_sending(monkeypatch)
    at, _pid = ui.open_article(project_root)
    ui.to_publish(at)
    huge_post_id(site)
    ui.send(at)
    assert "_wp_sending" not in at.session_state
    assert any(UNSURE in e.value for e in at.error)
    assert_huge_id_reported_and_locked(at, site)


# ======================================================= SL-T086-1: so rồi đặt (kho nháp)


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "drafts.sqlite")


def pending(post_id: int | None = None) -> SendState:
    return SendState.now(pending=True, post_id=post_id)


def test_expected_state_unchanged_is_written(store):
    """Trạng thái trong nháp vẫn như người dùng thấy (chưa gửi, hay đúng dòng đã đọc): ghi."""
    draft = store.save(DraftSnapshot()).id
    first = pending()
    assert store.save_send_state(draft, first, expected=(None, False))
    seen = store.load_send_state(draft)
    assert seen == first
    done = SendState.now(pending=False, post_id=501)
    assert store.save_send_state(draft, done, expected=(seen, False))
    assert store.load_send_state(draft) == done


def test_changed_state_is_not_overwritten(store):
    """Tab khác vừa ghi «đang gửi» (hay «đã gửi»): không ghi gì, trả ``False``. Cùng ``pending``,
    cùng mã bài nhưng ghi lúc khác cũng là trạng thái khác (lần gửi khác)."""
    draft = store.save(DraftSnapshot()).id
    old = pending()
    store.save_send_state(draft, old)
    time.sleep(0.05)  # đồng hồ Windows nhảy 15,6 ms một lần: hai lần ghi khác giờ
    other = pending()  # tab khác bắt đầu một lần gửi mới
    store.save_send_state(draft, other)
    assert not store.save_send_state(draft, pending(), expected=(None, False))
    assert not store.save_send_state(draft, pending(), expected=(old, False))
    assert not store.save_send_state(draft, pending(), expected=(None, True))
    assert store.load_send_state(draft) == other


def broken_row(store: DraftStore, draft: str) -> None:
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("INSERT OR REPLACE INTO send_states (id, data) VALUES (?, ?)", (draft, "hỏng"))


def test_broken_row_seen_as_broken(store):
    """Người dùng thấy «không đọc được trạng thái gửi» và xác nhận: ghi được khi dòng vẫn hỏng;
    dòng hỏng mà người dùng thấy trạng thái khác (hay ngược lại) thì không ghi."""
    draft = store.save(DraftSnapshot()).id
    broken_row(store, draft)
    assert not store.save_send_state(draft, pending(), expected=(None, False))
    assert store.save_send_state(draft, pending(), expected=(None, True))
    assert store.load_send_state(draft).pending
    assert not store.save_send_state(draft, pending(), expected=(None, True))


def test_only_one_tab_wins(store, monkeypatch):
    """Nhiều tab cùng ghi «đang gửi» từ cùng trạng thái «chưa gửi»: đúng một tab ghi được, các tab
    khác đợi giao dịch kia xong rồi thấy trạng thái mới (không báo lỗi «file bận»). Đọc chậm lại
    để mọi tab cùng đọc trước khi có tab nào ghi (nếu đọc và ghi không cùng một giao dịch giữ khóa
    ghi, nhiều tab cùng ghi được)."""
    draft = store.save(DraftSnapshot()).id
    original = drafts._read_send_state

    def slow_read(conn, draft_id):
        state = original(conn, draft_id)
        time.sleep(0.2)
        return state

    monkeypatch.setattr(drafts, "_read_send_state", slow_read)
    start = threading.Barrier(4)
    results: list[object] = []

    def tab() -> None:
        start.wait()
        try:
            results.append(store.save_send_state(draft, pending(), expected=(None, False)))
        except Exception as exc:  # hỏng thì hiện lỗi trong câu kiểm, không nuốt lỗi
            results.append(exc)

    threads = [threading.Thread(target=tab) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
    assert sorted(results, key=repr) == [False, False, False, True]


# ===================================================== SL-T086-1: hai tab trên trang Soạn bài


def other_tab_sends_while_preparing(monkeypatch, draft: str) -> None:
    """«Tab 1» ghi «đang gửi» vào nháp đúng lúc tab này đọc ảnh để nén (sau khi đã bấm gửi)."""
    original = ImageLibrary.read_image_bytes
    once = [True]

    def read(self, ref):
        if once:
            once.pop()
            ui.store().save_send_state(draft, pending())
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", read)


def test_second_tab_locked_with_clear_message(project_root, root, fake_ai, site, monkeypatch):
    """Tab khác ghi «đang gửi» trong lúc tab này kiểm lại, nén ảnh: tab này không gửi gì, không ghi
    đè trạng thái của tab kia, báo rõ, khóa «gửi dở» (ô xác nhận chưa tick)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other_tab_sends_while_preparing(monkeypatch, draft)
    ui.send(at)
    assert site.fake.requests == []
    state = ui.store().load_send_state(draft)
    assert state.pending and state.post_id is None  # vẫn là «đang gửi» của tab kia
    assert any(ELSEWHERE in e.value.replace("\\", "") for e in at.error)
    assert any(UNSURE in e.value and "cửa sổ khác" in e.value for e in at.error)
    assert at.checkbox(key="_wp_checked").value is False
    assert button(at, SEND).disabled


def test_ticked_confirmation_not_reused_for_new_send_elsewhere(project_root, root, fake_ai, site):
    """Tab này đang khóa «gửi dở» (lần gửi trước chưa rõ), người dùng đã tick «Tôi đã kiểm tra…».
    Trước khi bấm, tab khác bắt đầu một lần gửi mới (trạng thái «đang gửi» khác). Bấm gửi: không
    gửi (xác nhận là cho lần gửi người dùng đã thấy), báo rõ, khóa lại."""
    at, _pid = ui.ready_image(project_root)
    draft = draft_id(at)
    ui.store().save_send_state(draft, pending())
    ui.to_publish(at)
    run_ok(at.checkbox(key="_wp_checked").check().run())
    assert not button(at, SEND).disabled
    time.sleep(0.05)  # đồng hồ Windows nhảy 15,6 ms một lần: hai lần ghi khác giờ
    ui.store().save_send_state(draft, pending())  # tab khác: lần gửi mới
    ui.send(at)
    assert site.fake.requests == []
    assert any(ELSEWHERE in e.value.replace("\\", "") for e in at.error)
    assert button(at, SEND).disabled


def test_two_sessions_create_more_only_once(project_root, root, fake_ai, site):
    """Hai tab (hai phiên) cùng bài đã gửi; cả hai tick «Tạo thêm một bài nháp mới». Tab 1 gửi
    trước; tab 2 bấm sau (vẫn thấy lần gửi cũ): không tạo bài thứ ba, báo rõ."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    other = t86.reopen(project_root, draft_id(at))  # tab 2
    run_ok(other.checkbox(key="_wp_again").check().run())
    run_ok(at.checkbox(key="_wp_again").check().run())
    ui.send(at)
    assert len(site.posts()) == 2
    button(other, SEND).click().run()
    run_ok(other)
    assert len(site.posts()) == 2
    assert any(ELSEWHERE in e.value.replace("\\", "") for e in other.error)
    assert button(other, SEND).disabled

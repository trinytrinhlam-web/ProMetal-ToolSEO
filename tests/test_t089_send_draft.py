"""T-089: dọn lỗi Thấp của «Gửi nháp» sau T-086 (LC-T086-1, SL-T086-1, SL-T086-2) và lưu băm ảnh
đã duyệt trong nháp (Ghi nhận 1 của Lá Chắn T-086).

- LC-T086-1: website trả mã bài ngoài khoảng nháp ghi được: câu cố định, trang không lỗi, vẫn khóa.
- SL-T086-1: «đang gửi» ghi kiểu so rồi đặt trong một giao dịch SQLite (``save_send_state`` có
  ``expected``): tab thứ hai cùng bài bị khóa, có câu nhắc; xác nhận đã tick sẵn không dùng được cho
  trạng thái mới do tab khác ghi.
- SL-T086-2: khung ảnh đã chọn hiện ảnh xem trước dựng từ đúng byte đã băm.
- Yêu cầu 4: băm nội dung file lúc duyệt alt lưu trong ``DraftImage`` (``approved_sha256``); mở lại
  nháp mà ảnh khác băm thì bắt duyệt lại; nháp cũ (không có băm) vẫn mở được, phải duyệt lại.
- Lượt 2, SL-T089-1: chỉ lần gửi đã ghi được «đang gửi» (``holder["claimed"]``) mới ghi kết quả,
  và ghi kiểu so rồi đặt với đúng dấu đó: lần gửi không ghi được «đang gửi» rồi bị ngắt không ghi
  gì; tab khác cố ý gửi tiếp trong lúc tab này đang gửi thì kết quả tab này không ghi đè.

Dùng lại ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; không gọi mạng thật.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from contextlib import closing

import pytest
import streamlit as st
import test_app_images as ui
import test_soi_loi_t056 as sl
import test_t086_send_state as t86
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData

import seo_app.storage.drafts as drafts
from seo_app.images import process as image_process
from seo_app.images.folders import ImageLibrary
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL
from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import DraftError, DraftImage, SendState

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
ELSEWHERE = "Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi"


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


# ========================================= SL-T086-2: ảnh xem trước dựng từ đúng byte đã băm


def test_chosen_preview_built_from_hashed_bytes(project_root, root, fake_ai, monkeypatch):
    """Khung ảnh đã chọn hiện ảnh xem trước dựng từ **đúng** byte đã băm để gắn với lần duyệt (cùng
    lần đọc file với dòng GPS), không lấy từ cache theo cỡ, giờ sửa (SL-T086-2)."""
    made: list[tuple[str, bytes]] = []
    original_make = image_process.make_preview

    def make(data, **kwargs):
        preview = original_make(data, **kwargs)
        made.append((hashlib.sha256(data).hexdigest(), preview))
        return preview

    monkeypatch.setattr(image_process, "make_preview", make)
    shown: list[object] = []
    original_image = st.image

    def image(data, *args, **kwargs):
        shown.append(data)
        return original_image(data, *args, **kwargs)

    monkeypatch.setattr(st, "image", image)
    at, pid = ui.ready_image(project_root)
    shown.clear()
    run_ok(at.run())
    (preview,) = [data for data in shown if isinstance(data, bytes)]
    approved = at.session_state[f"altsha-{pid}"]
    assert (approved, preview) in made
    assert approved == hashlib.sha256((root / ui.REAL_FILE).read_bytes()).hexdigest()


# ============================================== băm ảnh đã duyệt lưu trong nháp (yêu cầu 4)


DIGEST = "a" * 64
CHANGED = "Ảnh này khác bản bạn đã duyệt trước đó"
OLD_APPROVAL = "ảnh có alt đã duyệt nhưng nháp không có «dấu vân tay»"


def real_image(**changes) -> DraftImage:
    data = dict(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=ui.REAL_FILE,
        alt="Bản lề cổng inox bị gỉ",
        alt_approved=True,
        approved_sha256=DIGEST,
    )
    data.update(changes)
    return DraftImage(**data)


def raw_image(store: DraftStore, draft: str) -> dict:
    with closing(sqlite3.connect(store.path)) as conn:
        (raw,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft,)).fetchone()
    return json.loads(raw)["parts"][1]["chosen_image"]


def test_hash_kept_with_approval(store):
    """Băm đi cùng lần duyệt: lưu, mở lại giữ nguyên; JSON chỉ có khóa băm khi có băm (nháp không
    có băm vẫn đúng khuôn cũ)."""
    snap = store.save(ui.article(real_image()))
    assert store.load(snap.id).parts[1].chosen_image.approved_sha256 == DIGEST
    assert raw_image(store, snap.id)["approved_sha256"] == DIGEST
    plain = store.save(ui.article(real_image(alt_approved=False)))
    assert "approved_sha256" not in raw_image(store, plain.id)


@pytest.mark.parametrize(
    "changes",
    [
        {"alt_approved": False},  # chưa duyệt: không có băm
        {"alt": ""},  # alt trống thì không thể «đã duyệt»
        {"root_index": None, "rel_path": "", "source": SOURCE_AI},  # ảnh AI chưa có file
        {"approved_sha256": "A" * 64},  # chữ hoa: không phải dạng app ghi
        {"approved_sha256": "a" * 63},
        {"approved_sha256": "a" * 65},
        {"approved_sha256": " " + "a" * 64},
        {"approved_sha256": "g" * 64},
        {"approved_sha256": 12345},
        {"approved_sha256": None},
        {"approved_sha256": ["a" * 64]},
    ],
)
def test_hash_only_valid_with_approval(changes):
    """Nháp là dữ liệu chưa tin cậy: băm chỉ nhận đúng 64 chữ số hex thường, chỉ đi cùng lần duyệt
    của ảnh trong thư mục ảnh; sai dạng thì bỏ băm (ảnh vẫn giữ, giao diện bắt duyệt lại)."""
    assert real_image(**changes).approved_sha256 == ""


def test_hand_edited_hash_drops_hash_not_image(store):
    """Băm trong file nháp bị sửa tay sai dạng: ảnh vẫn mở được (không bị bỏ như ảnh hỏng), chỉ mất
    băm (giao diện bắt duyệt lại)."""
    snap = store.save(ui.article(real_image()))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        (raw,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (snap.id,)).fetchone()
        conn.execute(
            "UPDATE drafts SET data = ? WHERE id = ?", (raw.replace(DIGEST, "<b>x</b>"), snap.id)
        )
    loaded = store.load(snap.id)
    image = loaded.parts[1].chosen_image
    assert loaded.dropped_images == 0
    assert (image.rel_path, image.alt_approved, image.approved_sha256) == (ui.REAL_FILE, True, "")


def test_old_draft_without_hash_opens(store):
    """Nháp lưu trước T-089 (ảnh đã duyệt, không có trường băm) vẫn mở được, ảnh giữ nguyên."""
    snap = store.save(ui.article(real_image(approved_sha256="")))
    image = store.load(snap.id).parts[1].chosen_image
    assert (image.alt_approved, image.approved_sha256) == (True, "")


def file_hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_approval_hash_saved_and_restored(project_root, root, fake_ai, site):
    """Duyệt alt: nháp lưu băm của đúng file đã xem. Phiên mới mở lại (file không đổi), gửi thẳng ở
    bước Xuất bản (không xem lại khung ảnh): vẫn «đã duyệt», so được với băm trong nháp, gửi."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    assert ui.saved_image(at).approved_sha256 == file_hash(root / ui.REAL_FILE)
    fresh = t86.reopen(project_root, draft_id(at))
    pid = fresh.session_state["part_ids"][1]
    assert fresh.session_state[f"altok-{pid}"] is True
    assert fresh.session_state[f"altsha-{pid}"] == file_hash(root / ui.REAL_FILE)
    ui.send(fresh)
    assert ui.counts(site) == (1, 1)


def test_reopened_draft_file_replaced_stops_send(project_root, root, fake_ai, site):
    """Duyệt xong, đóng app; file bị thay tại chỗ (cùng cỡ, giờ sửa). Phiên mới mở lại nháp rồi gửi
    thẳng ở bước Xuất bản: byte sắp tải khác băm lưu trong nháp nên dừng, chưa gửi gì, bắt duyệt
    lại (phần còn lại của SL-T056-2)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    t86.replace_in_place(root / ui.REAL_FILE)
    fresh = t86.reopen(project_root, draft_id(at))
    pid = fresh.session_state["part_ids"][1]
    assert not button(fresh, SEND).disabled  # cỡ, giờ sửa, định danh như cũ: chỉ băm mới bắt được
    ui.send(fresh)
    assert site.fake.requests == []
    problems = [m.value.replace("\\", "") for m in fresh.markdown]
    assert any("nội dung file khác bản bạn đã xem và duyệt" in p for p in problems)
    assert fresh.session_state[f"altok-{pid}"] is False
    assert button(fresh, SEND).disabled


def reopen_at_write_step(project_root, draft: str):
    """Phiên mới mở lại nháp lưu ở bước Viết & kiểm tra: khung ảnh hiện ngay."""
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    assert fresh.session_state["step"] == 2
    return fresh, fresh.session_state["part_ids"][1]


def test_reopened_draft_file_replaced_unapproved_on_view(project_root, root, fake_ai):
    """Như trên nhưng người dùng xem khung ảnh: ảnh đang hiện (file mới) khác bản đã duyệt nên bỏ
    «Đã duyệt», báo rõ; duyệt lại thì nháp lưu băm của file mới."""
    at, _pid = ui.ready_image(project_root)
    t86.replace_in_place(root / ui.REAL_FILE)
    fresh, pid = reopen_at_write_step(project_root, draft_id(at))
    assert fresh.session_state[f"altok-{pid}"] is False
    assert any(CHANGED in w.value for w in fresh.warning)
    ui.approve(fresh, pid)
    assert not any(CHANGED in w.value for w in fresh.warning)
    assert ui.saved_image(fresh).approved_sha256 == file_hash(root / ui.REAL_FILE)


def test_reopened_draft_same_file_stays_approved(project_root, root, fake_ai):
    """Đối chứng: file không đổi thì mở lại nháp, xem khung ảnh vẫn «Đã duyệt», không nhắc gì."""
    at, _pid = ui.ready_image(project_root)
    fresh, pid = reopen_at_write_step(project_root, draft_id(at))
    assert fresh.session_state[f"altok-{pid}"] is True
    assert not any(CHANGED in w.value or OLD_APPROVAL in w.value for w in fresh.warning)


def test_old_draft_without_hash_needs_new_approval(project_root, root, fake_ai):
    """Nháp cũ (alt đã duyệt, chưa có băm): mở được, chữ giữ nguyên, nhưng không so được ảnh với lúc
    duyệt nên bỏ «Đã duyệt», báo một lần; duyệt lại thì lưu băm."""
    chosen = real_image(approved_sha256="")
    at, pid = ui.open_article(project_root, ui.article(chosen))
    assert at.session_state[f"altok-{pid}"] is False
    assert f"altsha-{pid}" not in at.session_state
    assert any(OLD_APPROVAL in w.value for w in at.warning)
    assert at.session_state[f"alt-{pid}"] == chosen.alt
    ui.approve(at, pid)
    assert at.session_state[f"altok-{pid}"] is True
    assert not any(OLD_APPROVAL in w.value for w in at.warning)
    assert ui.saved_image(at).approved_sha256 == file_hash(root / ui.REAL_FILE)


# ======================================== Lượt 2, SL-T089-1: chỉ lần đã ghi «đang gửi» ghi kết quả


OTHER_TAB = "một tab khác của app vừa ghi trạng thái gửi mới cho bài này, app không ghi đè"
BUSY = t86.BUSY


def test_expected_delete_only_own_state(store):
    """Ghi «chưa gửi» (xóa dòng) kiểu so rồi đặt: chỉ xóa khi trạng thái trong nháp vẫn đúng như
    ``expected``; tab khác vừa ghi trạng thái mới thì giữ nguyên."""
    draft = store.save(DraftSnapshot()).id
    mine = pending()
    store.save_send_state(draft, mine)
    time.sleep(0.05)  # đồng hồ Windows nhảy 15,6 ms một lần: hai lần ghi khác giờ
    other = pending()
    store.save_send_state(draft, other)
    assert not store.save_send_state(draft, None, expected=(mine, False))
    assert store.load_send_state(draft) == other
    assert store.save_send_state(draft, None, expected=(other, False))
    assert store.load_send_state(draft) is None


def interrupt_now() -> None:
    """Người dùng bấm gì đó đúng lúc này: lần chạy dừng ở chỗ dừng kế tiếp (yêu cầu chạy lại)."""
    ctx = get_script_run_ctx()
    ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))


def test_pending_not_written_then_interrupted_writes_nothing(
    project_root, root, fake_ai, site, monkeypatch
):
    """Tab khác vừa ghi «đang gửi» và đang giữ file nháp, nên tab này ghi «đang gửi» hỏng (file nháp
    bận): không gửi gì; lần chạy bị ngắt ngay sau đó. Lần chạy sau ``finish_send`` không ghi gì vào
    nháp (tab này chưa ghi được «đang gửi»): nháp giữ đúng «đang gửi» của tab kia, phiên mới vẫn
    khóa (biến thể «file nháp bận» của SL-T089-1)."""
    other = pending()
    original = DraftStore.save_send_state
    fired: list[str] = []

    def save(self, draft, state, *, expected=None):
        if expected is None or fired:
            return original(self, draft, state, expected=expected)
        original(self, draft, other)  # tab khác ghi «đang gửi» trước
        fired.append(draft)
        interrupt_now()
        raise DraftError(BUSY)

    monkeypatch.setattr(DraftStore, "save_send_state", save)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    ui.send(at)
    run_ok(at.run())
    assert fired == [draft]
    assert site.fake.requests == []
    assert ui.store().load_send_state(draft) == other
    assert "_wp_sending" not in at.session_state
    assert button(at, SEND).disabled
    fresh = t86.reopen(project_root, draft)
    assert any(UNSURE in e.value for e in fresh.error) and button(fresh, SEND).disabled


def other_tab_sends_during_request(site, draft: str, other: SendState) -> None:
    """Trong lúc website đang tạo bài nháp của tab này, tab khác (người dùng cố ý tick «Tôi đã kiểm
    tra…») ghi «đang gửi» mới của nó (Ghi nhận 1 của Lá Chắn T-089)."""
    original = site.create_post

    def create_post(request):
        ui.store().save_send_state(draft, other)
        return original(request)

    site.fake.on("POST", ui.POSTS, create_post)


def test_outcome_does_not_overwrite_other_tab_new_send(project_root, root, fake_ai, site):
    """Kết quả lần gửi này ghi kiểu so rồi đặt với «đang gửi» chính nó đã ghi: tab khác đã ghi
    «đang gửi» mới thì không ghi đè (nháp giữ khóa «gửi dở» của tab kia, không đoán). Trang vẫn
    hiện kết quả (bài 501) và báo chưa ghi được vào nháp, nút khóa."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = pending()
    other_tab_sends_during_request(site, draft, other)
    ui.send(at)
    assert len(site.posts()) == 1
    assert ui.store().load_send_state(draft) == other
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    assert any(OTHER_TAB in w.value for w in at.warning)
    assert any(UNSURE in e.value for e in at.error) and button(at, SEND).disabled


def test_retry_in_finish_send_also_compares(project_root, root, fake_ai, site, monkeypatch):
    """Lần ghi kết quả đầu hỏng (file nháp bận) và lần chạy bị ngắt; trước khi ``finish_send`` thử
    ghi lại, tab khác cố ý gửi tiếp (ghi «đang gửi» mới). Lần thử lại cũng so rồi đặt: không ghi
    đè, báo; nháp giữ trạng thái tab kia."""
    original = DraftStore.save_send_state
    other = pending()
    outcome_calls: list[bool] = []

    def save(self, draft, state, *, expected=None):
        if expected is None or expected[0] is None:  # lần ghi «đang gửi» của tab này: ghi thật
            return original(self, draft, state, expected=expected)
        outcome_calls.append(True)
        if len(outcome_calls) == 1:  # ghi kết quả lần đầu: file nháp bận, rồi bị ngắt
            original(self, draft, other)  # tab khác gửi tiếp trước khi tab này thử lại
            interrupt_now()
            raise DraftError(BUSY)
        return original(self, draft, state, expected=expected)

    monkeypatch.setattr(DraftStore, "save_send_state", save)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    ui.send(at)
    run_ok(at.run())
    assert len(outcome_calls) == 2  # lần đầu trong lúc gửi, lần thử lại ở ``finish_send``
    assert len(site.posts()) == 1
    assert ui.store().load_send_state(draft) == other
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    assert any(OTHER_TAB in w.value for w in at.warning)
    assert button(at, SEND).disabled


# ============================== Lượt 3, SL-T089-2: nháp mất dòng trạng thái gửi lúc đang gửi


KEPT = "nháp giữ trạng thái gửi của tab kia"
STALE_TAIL = "sẽ thấy nhắc «chưa có kết quả»"


def on_request(site, path: str, before, reply=None) -> None:
    """Website giả: ngay khi nhận lệnh ``POST path`` của tab này, chạy ``before()`` (việc ở tab khác
    trong lúc tab này đang gửi), rồi trả lời như thường (hay ``reply``)."""
    original = site.create_post if path == ui.POSTS else site.create_media

    def handler(request):
        before()
        return original(request) if reply is None else reply

    site.fake.on("POST", path, handler)


def test_outcome_recorded_when_send_state_row_gone(project_root, root, fake_ai, site):
    """SL-T089-2: trong lúc tab này đang gửi, dòng trạng thái gửi của nháp mất (lần gửi cố ý ở tab
    khác hỏng trước khi gửi gì nên ghi «chưa gửi»). Kết quả lần này (bài 501) vẫn được ghi vì nháp
    trống: khóa «đã gửi», không báo thừa; phiên mới phải tick «Tạo thêm»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    on_request(site, ui.POSTS, lambda: ui.store().save_send_state(draft, None))
    ui.send(at)
    state = ui.store().load_send_state(draft)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)
    assert not any("Chưa ghi được kết quả" in w.value for w in at.warning)
    assert button(at, SEND).disabled
    fresh = t86.reopen(project_root, draft)
    assert any(f"mã {ui.POST_ID}" in i.value.replace("\\", "") for i in fresh.info)
    assert button(fresh, SEND).disabled


def test_kept_other_message_names_this_post(project_root, root, fake_ai, site):
    """Ghi nhận L2-1 của Soi Lỗi: tab khác ghi trạng thái mới trong lúc tab này đang gửi. Câu báo
    nói nháp giữ trạng thái của tab kia và bài của lần này (mã 501) cũng đã lên; không còn nói «sẽ
    thấy nhắc chưa có kết quả» (sai khi tab kia đã gửi xong)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = SendState.now(pending=False, post_id=777)  # tab kia đã gửi xong bài 777
    on_request(site, ui.POSTS, lambda: ui.store().save_send_state(draft, other))
    ui.send(at)
    assert ui.store().load_send_state(draft) == other
    (warning,) = [w.value for w in at.warning if OTHER_TAB in w.value]
    assert KEPT in warning and f"mã {ui.POST_ID}" in warning
    assert STALE_TAIL not in warning
    assert button(at, SEND).disabled


def test_kept_other_message_when_result_unsure(project_root, root, fake_ai, site):
    """Như trên nhưng lần gửi này lỗi đúng lúc tạo nháp (không rõ bài đã lên chưa): câu báo nói bài
    của lần này «có thể» đã lên, không có mã bài; trang không lỗi; nháp giữ trạng thái tab kia."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = pending()
    bad_gateway = (502, {"code": "x", "message": "Bad gateway"}, {})
    on_request(site, ui.POSTS, lambda: ui.store().save_send_state(draft, other), bad_gateway)
    ui.send(at)
    assert ui.store().load_send_state(draft) == other
    (warning,) = [w.value for w in at.warning if OTHER_TAB in w.value]
    assert KEPT in warning and "có thể cũng đã có trên website" in warning
    assert STALE_TAIL not in warning
    assert button(at, SEND).disabled


def test_nothing_created_and_other_tab_wrote_no_note(project_root, root, fake_ai, site):
    """Lần gửi này hỏng trước khi tạo gì (website từ chối ảnh), trong lúc đó tab khác ghi «đang gửi»
    mới: không có gì để ghi, nháp giữ «đang gửi» của tab kia, không báo «chưa ghi được kết quả»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = pending()
    bad_request = (400, {"code": "x", "message": "Bad request"}, {})
    on_request(site, ui.MEDIA, lambda: ui.store().save_send_state(draft, other), bad_request)
    ui.send(at)
    assert ui.counts(site) == (0, 1)
    assert ui.store().load_send_state(draft) == other
    assert not any("Chưa ghi được kết quả" in w.value for w in at.warning)
    assert any(UNSURE in e.value for e in at.error) and button(at, SEND).disabled

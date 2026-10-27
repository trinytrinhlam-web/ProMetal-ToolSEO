"""Soi Lỗi T-089: dọn lỗi Thấp của «Gửi nháp» sau T-086 (``app/views/write.py``,
``seo_app/storage/drafts.py``).

Kiểm lại LC-T086-1, SL-T086-1, SL-T086-2 và băm ảnh đã duyệt lưu trong nháp bằng biến thể ngoài
test của Họa Sĩ:

- mã bài website trả rất lớn (2⁶⁴, 10³⁰), lớn nhất còn ghi được (2⁶³ − 1), âm, 0, chữ, số thực,
  ``null``, ``true``; ngắt lần chạy ở từng lần ghi sau khi website trả mã lạ;
- hai phiên cùng một nháp gửi luân phiên nhiều vòng; tab kia gửi **trọn** một lần (bài thật trên
  website giả) trong lúc tab này nén ảnh; luồng một tab bình thường không bị chặn oan;
- băm trong nháp bị sửa tay (nhiều dạng sai, đúng dạng nhưng khác file, nằm trên ảnh chưa duyệt);
  file bị thay tại chỗ giữa lúc xem và lúc duyệt; nháp cũ không có băm chỉ bị bắt duyệt lại một lần.

Lỗi tìm được: ``xfail(strict=True)`` mã SL-T089-x (``docs/team/reports/T-089-soi-loi.md``). Test
dùng ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; không gọi mạng thật.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing

import pytest
import test_app_images as ui
import test_soi_loi_t056 as sl
import test_soi_loi_t086 as sl86
import test_t086_send_state as t86
from streamlit.runtime import Runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData
from streamlit.runtime.state.safe_session_state import SafeSessionState

from seo_app.images.folders import ImageLibrary
from seo_app.storage import DraftStore
from seo_app.storage.drafts import DraftError, SendState
from seo_app.wordpress.client import WordPressClient, WordPressError

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
SUCCESS = "Đã tạo bài nháp trên WordPress"
NOTE = "website trả mã bài nháp lớn bất thường, app không ghi được vào nháp"
ELSEWHERE = "Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi"
CHANGED = "Ảnh này khác bản bạn đã duyệt trước đó"
OLD_APPROVAL = "ảnh có alt đã duyệt nhưng nháp không có «dấu vân tay»"
REPLACED = "nội dung file khác bản bạn đã xem và duyệt"


def draft_id(at) -> str:
    return at.session_state["draft_id"]


def errors(at) -> list[str]:
    return [e.value.replace("\\", "") for e in at.error]


def post_returns(site, post_id: object) -> None:
    """Website giả tạo bài nháp nhưng trả mã bài ``post_id`` (giá trị JSON bất kỳ)."""
    site.fake.on(
        "POST",
        ui.POSTS,
        lambda _r: (201, {"id": post_id, "status": "draft", "title": {"raw": "T"}}, {}),
    )


def file_hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edit_chosen_image(draft: str, **changes) -> None:
    """Sửa tay ảnh đã chọn trong file nháp (SQLite): đặt (hay bỏ, giá trị ``...``) các khóa."""
    with closing(sqlite3.connect(ui.store().path)) as conn, conn:
        (raw,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft,)).fetchone()
        data = json.loads(raw)
        image = data["parts"][1]["chosen_image"]
        for key, value in changes.items():
            if value is ...:
                image.pop(key, None)
            else:
                image[key] = value
        conn.execute(
            "UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(data, ensure_ascii=False), draft)
        )


def send_in_other_session(other) -> None:
    """Phiên kia bấm gửi và gửi xong ngay giữa lần chạy của phiên này. AppTest lồng nhau: lần chạy
    bên trong bỏ ``Runtime`` giả của lần chạy bên ngoài khi xong, nên đặt lại."""
    outer = Runtime._instance
    try:
        ui.send(other)
    finally:
        Runtime._instance = outer


def reopen_at_write_step(project_root, draft: str):
    """Phiên mới (tải lại trang, tab khác) mở lại nháp lưu ở bước Viết & kiểm tra."""
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    assert fresh.session_state["step"] == 2
    return fresh, fresh.session_state["part_ids"][1]


# ============================================================ LC-T086-1: mã bài lạ từ website


@pytest.mark.parametrize("post_id", [2**64, 10**30], ids=["2^64", "10^30"])
def test_post_id_far_out_of_range_fixed_note(project_root, root, fake_ai, site, post_id):
    """Biến thể của 2⁶³: mã vượt cả BIGINT UNSIGNED (2⁶⁴) và mã 31 chữ số. Trang không lỗi, có câu
    cố định, nháp giữ «đang gửi», nút khóa; các lần chạy sau không lỗi lại, không gửi thêm."""
    post_returns(site, post_id)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert any(NOTE in w.value for w in at.warning)
    assert any(f"mã {post_id}" in s.value for s in at.success)
    for _ in range(2):
        run_ok(at.run())
        assert button(at, SEND).disabled
    assert ui.store().load_send_state(draft_id(at)).pending
    assert len(site.posts()) == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_post_id_out_of_range_interrupted_at_each_write(
    project_root, root, fake_ai, site, monkeypatch, n
):
    """Website trả mã 2⁶³; người dùng bấm gì đó đúng lúc app ghi khóa thứ ``n`` vào phiên sau khi
    website trả lời (``apply_send``): lần chạy sau ``finish_send`` ghi lại kết quả, lại gặp mã lạ,
    ra câu cố định chứ không lỗi trang; vẫn khóa, một bài."""
    site.create_post = lambda _r: (
        201,
        {"id": 2**63, "status": "draft", "title": {"raw": "T"}},
        {},
    )
    fired = sl86.interrupt_at_write_after_post(monkeypatch, site, n)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert fired
    for _ in range(2):
        run_ok(at.run())
        assert button(at, SEND).disabled
    assert any(NOTE in w.value for w in at.warning)
    assert ui.store().load_send_state(draft_id(at)).pending
    assert "_wp_sending" not in at.session_state
    assert len(site.posts()) == 1


def test_largest_post_id_still_recorded(project_root, root, fake_ai, site):
    """Đối chứng biên: mã 2⁶³ − 1 vẫn ghi được vào nháp (không ra câu «mã lớn bất thường»); phiên
    mới mở lại thấy «đã gửi», phải tick «Tạo thêm» mới gửi."""
    post_returns(site, 2**63 - 1)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert not any(NOTE in w.value for w in at.warning)
    state = ui.store().load_send_state(draft_id(at))
    assert (state.pending, state.post_id) == (False, 2**63 - 1)
    fresh = t86.reopen(project_root, draft_id(at))
    assert button(fresh, SEND).disabled
    run_ok(fresh.checkbox(key="_wp_again").check().run())
    assert not button(fresh, SEND).disabled


@pytest.mark.parametrize(
    "post_id",
    [-5, 0, "501", 501.5, None, True, "9223372036854775808"],
    ids=["am", "0", "chu-so", "so-thuc", "null", "true", "chu-2^63"],
)
def test_malformed_post_id_locks_unsure(project_root, root, fake_ai, site, post_id):
    """Mã bài âm, 0, chữ, số thực, ``null``, ``true``: client từ chối (bài có thể đã lên website):
    trang không lỗi, khóa «gửi dở», nháp giữ «đang gửi», không gửi thêm."""
    post_returns(site, post_id)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    for _ in range(2):
        run_ok(at.run())
        assert button(at, SEND).disabled
    assert any(UNSURE in e for e in errors(at))
    assert ui.store().load_send_state(draft_id(at)).pending
    assert len(site.posts()) == 1


# =================================================== SL-T086-1: hai phiên cùng một nháp


def test_two_sessions_take_turns_one_post_per_round(project_root, root, fake_ai, site):
    """Hai phiên cùng bài, luân phiên ba vòng: mỗi vòng cả hai tick «Tạo thêm», một phiên gửi, phiên
    kia bấm sau (vẫn thấy trạng thái cũ): mỗi vòng đúng một bài; phiên bấm sau được nhắc rõ, bị
    khóa; vòng sau chính phiên đó tick lại và gửi được (không bị chặn oan)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    other = t86.reopen(project_root, draft_id(at))
    ui.send(at)  # vòng 0: phiên kia bấm sau thì nút đã khóa «đã gửi», không gửi
    button(other, SEND).click().run()
    run_ok(other)
    assert len(site.posts()) == 1
    assert button(other, SEND).disabled
    tabs = [at, other]
    for round_, (first, second) in enumerate([(1, 0), (0, 1), (1, 0)], start=2):
        for tab in tabs:
            run_ok(tab.checkbox(key="_wp_again").check().run())
            assert not button(tab, SEND).disabled
        ui.send(tabs[first])
        assert len(site.posts()) == round_
        assert not any(ELSEWHERE in e for e in errors(tabs[first]))
        button(tabs[second], SEND).click().run()
        run_ok(tabs[second])
        assert len(site.posts()) == round_
        assert any(ELSEWHERE in e for e in errors(tabs[second]))
        assert button(tabs[second], SEND).disabled


def test_other_session_completes_send_while_this_one_prepares(
    project_root, root, fake_ai, site, monkeypatch
):
    """Hai phiên cùng bài, chưa gửi. Phiên này bấm «Gửi nháp»; trong lúc nó đọc ảnh để nén, phiên
    kia gửi **trọn** một lần (bài 501 lên website giả, nháp ghi «đã gửi»). Phiên này: không gửi,
    nhắc rõ, khóa; trạng thái «đã gửi» của phiên kia còn nguyên trong nháp."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = t86.reopen(project_root, draft)
    original = ImageLibrary.read_image_bytes
    once = [True]

    def read(self, ref):
        if once:
            once.pop()
            send_in_other_session(other)  # gửi xong trước khi phiên này nén xong
            assert len(site.posts()) == 1
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", read)
    ui.send(at)
    run_ok(at.run())
    assert not once
    assert len(site.posts()) == 1
    assert any(ELSEWHERE in e for e in errors(at))
    assert button(at, SEND).disabled
    state = ui.store().load_send_state(draft)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)


def test_one_session_create_more_three_times_not_refused(project_root, root, fake_ai, site):
    """Luồng một tab bình thường: gửi, tick «Tạo thêm», gửi, tick, gửi: ba bài, không lần nào bị
    nhắc «trạng thái gửi vừa thay đổi» (so rồi đặt không chặn oan)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    for count in (2, 3):
        run_ok(at.checkbox(key="_wp_again").check().run())
        ui.send(at)
        assert len(site.posts()) == count
        assert not any(ELSEWHERE in e for e in errors(at))
    state = ui.store().load_send_state(draft_id(at))
    assert (state.pending, state.post_id) == (False, ui.POST_ID)


def test_unsure_lock_confirmed_then_sent_not_refused(
    project_root, root, fake_ai, site, monkeypatch
):
    """Lần gửi bị ngắt (khóa «gửi dở»), người dùng tick «Tôi đã kiểm tra…» rồi gửi: gửi được, không
    bị nhắc «trạng thái gửi vừa thay đổi»; nháp ghi «đã gửi»."""
    sl.interrupt_while_sending(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert button(at, SEND).disabled
    run_ok(at.checkbox(key="_wp_checked").check().run())
    ui.send(at)
    assert len(site.posts()) == 2
    assert not any(ELSEWHERE in e for e in errors(at))
    state = ui.store().load_send_state(draft_id(at))
    assert (state.pending, state.post_id) == (False, ui.POST_ID)


# ======================================== băm ảnh đã duyệt trong nháp, ảnh xem trước (SL-T086-2)


@pytest.mark.parametrize(
    "value",
    ["A" * 64, "a" * 63, "g" * 64, 12345, None, [], {"x": 1}, "a" * 64 + "\n", "a" * 100_000],
    ids=["chu-hoa", "63-ky-tu", "khong-hex", "so", "null", "list", "dict", "xuong-dong", "100k"],
)
def test_hand_edited_hash_reopened_in_app(project_root, root, fake_ai, value):
    """Băm trong file nháp bị sửa tay sai dạng (kể cả chuỗi 100.000 ký tự): mở lại nháp trong app
    không lỗi, ảnh vẫn giữ, bỏ «Đã duyệt» và nhắc; duyệt lại thì nháp lưu băm của đúng file."""
    at, _pid = ui.ready_image(project_root)
    edit_chosen_image(draft_id(at), approved_sha256=value)
    fresh, pid = reopen_at_write_step(project_root, draft_id(at))
    assert f"pick-{pid}" in fresh.session_state
    assert fresh.session_state[f"altok-{pid}"] is False
    assert any(OLD_APPROVAL in w.value for w in fresh.warning)
    ui.approve(fresh, pid)
    assert ui.saved_image(fresh).approved_sha256 == file_hash(root / ui.REAL_FILE)


def test_valid_but_wrong_hash_stops_send_without_viewing(project_root, root, fake_ai, site):
    """Băm đúng dạng nhưng không phải của file (sửa tay, hay nháp chép từ máy khác): phiên mới mở
    lại, gửi thẳng ở bước Xuất bản: dừng, chưa gửi gì, bỏ duyệt; xem khung ảnh thì có câu nhắc."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    edit_chosen_image(draft_id(at), approved_sha256="0" * 64)
    fresh = t86.reopen(project_root, draft_id(at))
    pid = fresh.session_state["part_ids"][1]
    ui.send(fresh)
    assert site.fake.requests == []
    assert any(REPLACED in m.value.replace("\\", "") for m in fresh.markdown)
    assert fresh.session_state[f"altok-{pid}"] is False
    assert button(fresh, SEND).disabled


def test_wrong_hash_seen_on_write_step(project_root, root, fake_ai):
    """Như trên nhưng người dùng mở lại ở bước Viết & kiểm tra: bỏ «Đã duyệt», câu nhắc «khác bản
    bạn đã duyệt»."""
    at, _pid = ui.ready_image(project_root)
    edit_chosen_image(draft_id(at), approved_sha256="0" * 64)
    fresh, pid = reopen_at_write_step(project_root, draft_id(at))
    assert fresh.session_state[f"altok-{pid}"] is False
    assert any(CHANGED in w.value for w in fresh.warning)


def test_hash_on_unapproved_image_ignored(project_root, root, fake_ai):
    """Băm sửa tay nằm trên ảnh **chưa duyệt**: bị bỏ khi mở (không nhắc gì); duyệt thì gắn băm của
    đúng file đang hiện chứ không phải băm sửa tay."""
    at, pid = ui.ready_image(project_root)
    run_ok(at.checkbox(key=f"altok-{pid}").uncheck().run())
    edit_chosen_image(draft_id(at), alt_approved=False, approved_sha256="0" * 64)
    fresh, pid = reopen_at_write_step(project_root, draft_id(at))
    assert f"altsha-{pid}" not in fresh.session_state
    assert not any(OLD_APPROVAL in w.value or CHANGED in w.value for w in fresh.warning)
    ui.approve(fresh, pid)
    assert ui.saved_image(fresh).approved_sha256 == file_hash(root / ui.REAL_FILE)


def test_file_replaced_between_view_and_approval(project_root, root, fake_ai, site):
    """File bị thay tại chỗ (cùng cỡ, giờ sửa) **sau khi** khung ảnh hiện, **trước khi** tick duyệt:
    lần duyệt gắn với bản đã hiện (băm cũ, lưu vào nháp). Phiên mới mở lại: ảnh trên máy khác bản
    đã duyệt nên bỏ duyệt, nhắc. Phiên cũ gửi: dừng, chưa gửi gì."""
    at, pid = ui.open_article(project_root)
    ui.choose_real(at, pid)
    ui.write_alt(at, pid)
    shown = file_hash(root / ui.REAL_FILE)
    t86.replace_in_place(root / ui.REAL_FILE)
    ui.approve(at, pid)
    assert at.session_state[f"altsha-{pid}"] == shown
    assert ui.saved_image(at).approved_sha256 == shown
    fresh, fresh_pid = reopen_at_write_step(project_root, draft_id(at))
    assert fresh.session_state[f"altok-{fresh_pid}"] is False
    assert any(CHANGED in w.value for w in fresh.warning)
    ui.to_publish(at)
    ui.send(at)
    assert site.fake.requests == []
    assert any(REPLACED in m.value.replace("\\", "") for m in at.markdown)


def test_old_draft_without_hash_asks_only_once(project_root, root, fake_ai):
    """Nháp cũ (alt đã duyệt, không có khóa băm): lần mở đầu bỏ duyệt, nhắc; duyệt lại thì lưu băm;
    các lần mở sau (phiên mới) giữ «Đã duyệt», không nhắc lại."""
    at, _pid = ui.ready_image(project_root)
    edit_chosen_image(draft_id(at), approved_sha256=...)
    first, pid = reopen_at_write_step(project_root, draft_id(at))
    assert first.session_state[f"altok-{pid}"] is False
    assert any(OLD_APPROVAL in w.value for w in first.warning)
    ui.approve(first, pid)
    again, pid = reopen_at_write_step(project_root, draft_id(at))
    assert again.session_state[f"altok-{pid}"] is True
    assert not any(OLD_APPROVAL in w.value or CHANGED in w.value for w in again.warning)


# ==================================================== SL-T089-1: tab thua so rồi đặt bị ngắt


def lose_and_get_interrupted(monkeypatch, other_tab: SendState | None) -> list[bool]:
    """Tab này đã bấm gửi, đang nén ảnh. Đúng lúc tab này ghi «đang gửi» kiểu so rồi đặt: tab kia
    vừa ghi ``other_tab`` (nếu có) nên tab này thua; ngay sau đó người dùng bấm gì đó ở tab này
    (yêu cầu chạy lại thật): lần chạy dừng ở chỗ dừng kế tiếp, trước khi ``apply_send`` bỏ dấu
    ``_wp_sending``. Trả kết quả lần so rồi đặt của tab này."""
    original = DraftStore.save_send_state
    results: list[bool] = []

    def save(self, draft, state, *, expected=None):
        if expected is None or results:
            return original(self, draft, state, expected=expected)
        if other_tab is not None:
            original(self, draft, other_tab)
        results.append(original(self, draft, state, expected=expected))
        ctx = get_script_run_ctx()
        ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))
        return results[-1]

    monkeypatch.setattr(DraftStore, "save_send_state", save)
    return results


def test_lost_tab_interrupted_keeps_other_tab_sending(
    project_root, root, fake_ai, site, monkeypatch
):
    """Tab 1 đang gửi (nháp ghi «đang gửi»); tab 2 thua so rồi đặt (đúng: không gửi gì) nhưng lần
    chạy của tab 2 bị ngắt ngay sau đó (bấm đúp, bấm nút khác). Lần chạy sau ``finish_send`` thấy
    ``holder`` chưa «saved» nên ``record_outcome`` ghi trạng thái **của tab 2** (chưa gửi gì) vào
    nháp **không so**: xóa «đang gửi» của tab 1. Tải lại trang (hay tab 3) lúc tab 1 còn đang gửi:
    nút bật, không nhắc, gửi được bài thứ hai. Mong đợi: tab chưa ghi «đang gửi» thì không ghi gì
    vào nháp; nháp giữ «đang gửi» của tab 1, phiên mới vẫn khóa «gửi dở»."""
    sending = SendState.now(pending=True, post_id=None)
    lost = lose_and_get_interrupted(monkeypatch, sending)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    ui.send(at)
    run_ok(at.run())
    assert lost == [False]  # tab 2 thua so rồi đặt: không gửi gì
    assert site.fake.requests == []
    assert button(at, SEND).disabled
    state = ui.store().load_send_state(draft)
    assert state is not None and state.pending  # «đang gửi» của tab 1 phải còn
    fresh = t86.reopen(project_root, draft)
    assert any(UNSURE in e for e in errors(fresh))
    assert button(fresh, SEND).disabled


def test_lost_tab_interrupted_keeps_other_tab_sent(project_root, root, fake_ai, site, monkeypatch):
    """Ca hay gặp nhất của SL-T086-1 (hai tab bấm cách nhau một giây, ảnh lớn): tab 1 gửi **trọn**
    (bài 501, nháp ghi «đã gửi») trong lúc tab 2 nén ảnh; tab 2 thua so rồi đặt, lần chạy bị ngắt
    ngay sau đó. ``finish_send`` ghi trạng thái tab 2 thấy lúc bấm («chưa gửi») vào nháp: **xóa**
    «đã gửi» của bài 501, vĩnh viễn (không chỉ trong lúc đang gửi). Mở lại nháp: không còn khóa
    «đã gửi», không cần tick «Tạo thêm», bấm là ra bài thứ hai. Mong đợi: nháp vẫn ghi bài 501,
    phiên mới phải tick «Tạo thêm»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = t86.reopen(project_root, draft)
    original = ImageLibrary.read_image_bytes
    once = [True]
    lost: list[list[bool]] = []

    def read(self, ref):
        if once:
            once.pop()
            send_in_other_session(other)  # tab 1 gửi xong trong lúc tab 2 nén ảnh
            lost.append(lose_and_get_interrupted(monkeypatch, None))  # từ đây mới tới lượt tab 2
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", read)
    ui.send(at)
    run_ok(at.run())
    assert lost == [[False]]
    assert len(site.posts()) == 1
    state = ui.store().load_send_state(draft)
    assert state is not None and state.post_id == ui.POST_ID  # «đã gửi» của tab 1 phải còn
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled


# ================================================= lượt 2: kiểm lại bản sửa SL-T089-1 (claimed)

POST_2 = 502
OTHER_TAB = "một tab khác của app vừa ghi trạng thái gửi mới cho bài này, app không ghi đè"


def in_other_session(work):
    """Chạy ``work()`` (các lần chạy của một phiên khác) ngay giữa lần chạy của phiên này, rồi đặt
    lại ``Runtime`` giả của lần chạy bên ngoài (xem ``send_in_other_session``)."""
    outer = Runtime._instance
    try:
        return work()
    finally:
        Runtime._instance = outer


def interrupt() -> None:
    ctx = get_script_run_ctx()
    ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))


def lose_then_interrupt(monkeypatch, *, busy: bool, at_cas: bool, at_write: int | None) -> list:
    """Đúng lúc tab này ghi «đang gửi» kiểu so rồi đặt, tab kia vừa gửi xong (nháp ghi «đã gửi»
    bài 501). Tab này thua so rồi đặt (``busy``: hay ghi hỏng vì file nháp bận). Người dùng bấm gì
    đó ngay sau đó (``at_cas``) và/hoặc đúng lúc app sắp ghi (hay xóa) khóa thứ ``at_write`` vào
    phiên sau khi thua, kể cả ở lần chạy sau. Trả các lần ngắt."""
    original = DraftStore.save_send_state
    lost: list[str] = []
    fired: list[str] = []

    def save(self, draft, state, *, expected=None):
        if expected is None or lost:
            return original(self, draft, state, expected=expected)
        original(self, draft, SendState.now(pending=False, post_id=ui.POST_ID))  # tab kia
        lost.append(draft)
        if at_cas:
            fired.append("so rồi đặt")
            interrupt()
        if busy:
            raise DraftError(t86.BUSY)
        return original(self, draft, state, expected=expected)

    monkeypatch.setattr(DraftStore, "save_send_state", save)
    writes: list[str] = []
    original_set, original_del = SafeSessionState.__setitem__, SafeSessionState.__delitem__

    def maybe_fire(name: str) -> None:
        ctx = get_script_run_ctx()
        if not lost or at_write is None or ctx is None or ctx.script_requests is None:
            return
        writes.append(name)
        if len(writes) == at_write:
            fired.append(name)
            interrupt()

    def setitem(self, name, value):
        maybe_fire(name)
        return original_set(self, name, value)

    def delitem(self, name):
        maybe_fire(name)
        return original_del(self, name)

    monkeypatch.setattr(SafeSessionState, "__setitem__", setitem)
    monkeypatch.setattr(SafeSessionState, "__delitem__", delitem)
    return fired


@pytest.mark.parametrize(
    ("busy", "at_cas", "at_write", "times"),
    [
        (False, False, 1, 1),
        (False, False, 2, 1),
        (False, True, 1, 2),
        (True, True, None, 1),
        (True, True, 1, 2),
        (True, False, 2, 1),
    ],
    ids=["thua-ghi-1", "thua-ghi-2", "thua-hai-lan", "ban", "ban-hai-lan", "ban-ghi-2"],
)
def test_lost_or_busy_tab_interrupted_keeps_other_tab_sent(
    project_root, root, fake_ai, site, monkeypatch, busy, at_cas, at_write, times
):
    """SL-T089-1 kiểm lại bằng biến thể: tab này thua so rồi đặt (hay ghi «đang gửi» hỏng vì file
    nháp bận) đúng lúc tab kia vừa gửi xong bài 501; lần chạy bị ngắt ở các chỗ khác nhau sau đó,
    có ca ngắt hai lần liên tiếp. Tab này không gửi, không ghi gì vào nháp: nháp giữ «đã gửi 501»
    của tab kia, phiên mới phải tick «Tạo thêm»; không còn dấu sót."""
    fired = lose_then_interrupt(monkeypatch, busy=busy, at_cas=at_cas, at_write=at_write)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    ui.send(at)
    for _ in range(2):
        run_ok(at.run())
    assert len(fired) == times
    assert site.fake.requests == []
    state = ui.store().load_send_state(draft)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)
    assert "_wp_sending" not in at.session_state
    assert button(at, SEND).disabled
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
    run_ok(fresh.checkbox(key="_wp_again").check().run())
    assert not button(fresh, SEND).disabled  # chỉ khóa «đã gửi», không khóa oan


def confirm_and_send_in_other_tab(other):
    """Tab 2 (phiên khác, đã mở nháp từ trước) vẽ lại trong lúc tab 1 đang gửi: thấy khóa «gửi dở»,
    người dùng cố ý tick «Tôi đã kiểm tra…» rồi bấm «Gửi nháp» (Ghi nhận 1 của Lá Chắn T-089).
    Lồng trong lần chạy của tab 1 thì không gán ``session_state`` từ test (Streamlit xét theo lần
    chạy của tab 1), chỉ vẽ lại, tick, bấm."""

    def work():
        run_ok(other.run())
        assert button(other, SEND).disabled
        run_ok(other.checkbox(key="_wp_checked").check().run())
        ui.send(other)

    in_other_session(work)


def test_confirmed_send_in_other_tab_keeps_its_record(project_root, root, fake_ai, site):
    """Ghi nhận 1 bằng hai phiên thật: trong lúc website đang tạo bài 501 cho tab 1, tab 2 xác nhận
    và gửi trọn bài 502. Kết quả tab 1 không ghi đè: nháp giữ «đã gửi 502» của tab 2; tab 1 vẫn hiện
    bài 501, báo chưa ghi được vào nháp, khóa; phiên mới thấy «đã gửi» bài 502."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = t86.reopen(project_root, draft)  # tab 2 mở nháp từ trước
    site.fake.on("GET", f"{ui.POSTS}/{POST_2}", lambda _r: {"id": POST_2, "status": "draft"})
    site.fake.on(
        "POST",
        f"{ui.POSTS}/{POST_2}",
        lambda r: {"id": POST_2, "status": "draft", **ui.body_of(r)},
    )
    original = site.create_post
    tab2: list[str] = []

    def create_post(request):
        if tab2:  # bài của tab 2
            return (201, {"id": POST_2, "status": "draft", "title": {"raw": "T"}}, {})
        tab2.append("bắt đầu")
        confirm_and_send_in_other_tab(other)
        tab2.append("xong")  # lỗi trong lúc lồng bị client nuốt: chỉ tin khi tới được đây
        return original(request)  # bài 501 của tab 1

    site.fake.on("POST", ui.POSTS, create_post)
    ui.send(at)
    assert tab2 == ["bắt đầu", "xong"]
    assert len(site.posts()) == 2
    assert any(f"mã {POST_2}" in s.value for s in other.success)
    state = ui.store().load_send_state(draft)
    assert (state.pending, state.post_id) == (False, POST_2)
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    assert any(OTHER_TAB in w.value for w in at.warning)
    assert button(at, SEND).disabled
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
    assert any(f"mã {POST_2}" in i.value for i in fresh.info)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T089-2: nháp không còn dòng trạng thái gửi thì kết quả gửi bị bỏ (bài đã tạo)",
)
def test_confirmed_send_in_other_tab_failing_first_keeps_this_post(
    project_root, root, fake_ai, site, monkeypatch
):
    """Như trên nhưng lần gửi tab 2 lỗi trước khi có request nào (``WordPressError``, ví dụ kiểm sai
    trước khi gửi): tab 2 ghi «chưa gửi» (xóa dòng, đúng «đang gửi» của nó). Tab 1 tạo xong bài 501
    nhưng ``record_outcome`` so với «đang gửi» của tab 1, thấy nháp không còn dòng nào, coi là «tab
    khác vừa ghi trạng thái mới» nên **không ghi**: nháp không còn dấu vết bài 501, phiên mới mở
    nháp nút bật, không nhắc, bấm là ra bài thứ hai. Lượt 1 (ghi không so) giữ được «đã gửi 501».
    Mong đợi: kết quả có bài (hay chưa rõ) vẫn được ghi khi nháp không còn dòng trạng thái nào."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    other = t86.reopen(project_root, draft)  # tab 2 mở nháp từ trước
    original_create = WordPressClient.create_draft_with_images
    calls: list[int] = []

    def create(self, title, parts, **kwargs):
        calls.append(1)
        if len(calls) == 2:  # lần gửi của tab 2
            raise WordPressError("Lỗi thử: kiểm sai trước khi gửi, chưa gửi gì.")
        return original_create(self, title, parts, **kwargs)

    monkeypatch.setattr(WordPressClient, "create_draft_with_images", create)
    original = site.create_post
    tab2: list[str] = []

    def create_post(request):
        if not tab2:
            tab2.append("bắt đầu")
            confirm_and_send_in_other_tab(other)
            tab2.append("xong")
        return original(request)

    site.fake.on("POST", ui.POSTS, create_post)
    ui.send(at)
    assert tab2 == ["bắt đầu", "xong"]
    assert any("Lỗi thử" in e.value for e in other.error)  # tab 2: lỗi, chưa gửi gì
    assert len(calls) == 2 and len(site.posts()) == 1
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    state = ui.store().load_send_state(draft)
    assert state is not None and state.post_id == ui.POST_ID  # bài 501 phải còn dấu trong nháp
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled


@pytest.mark.xfail(
    strict=True,
    reason="SL-T089-2: nháp bị xóa ở tab khác lúc đang gửi, tự lưu tạo lại thì không còn khóa",
)
def test_draft_deleted_elsewhere_while_sending_comes_back_locked(project_root, root, fake_ai, site):
    """Trong lúc tab 1 đang gửi, tab 2 bấm «🗑️ Xóa» nháp này (``DraftStore.delete`` xóa cả dòng
    trạng thái gửi). Tab 1 tạo xong bài 501 nhưng không ghi được kết quả (so rồi đặt thấy không còn
    dòng nào; câu báo nói «một tab khác vừa ghi trạng thái gửi mới», không đúng). Tab 1 làm tiếp:
    lần tự lưu tạo lại nháp, **không** kèm «đã gửi 501». Phiên mới mở nháp: nút bật, không nhắc.
    Lượt 1 ghi «đã gửi 501» nên nháp tạo lại vẫn khóa. Mong đợi: như lượt 1."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    original = site.create_post

    def create_post(request):
        assert ui.store().delete(draft)  # tab 2 xóa nháp (như ``delete_draft``)
        return original(request)

    site.fake.on("POST", ui.POSTS, create_post)
    ui.send(at)
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    at.session_state["step"] = 2  # tab 1 làm tiếp: lần tự lưu tạo lại nháp
    run_ok(at.run())
    assert draft in [d.id for d in ui.store().list_drafts().drafts]
    state = ui.store().load_send_state(draft)
    assert state is not None and state.post_id == ui.POST_ID
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled

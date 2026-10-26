"""T-086: trạng thái gửi nháp không chỉ nằm trong phiên (SL-T056-8 → -11, LC-T056-1).

Kho nháp nhớ «đang gửi / đã gửi (mã bài)» (``SendState``, test ở ``test_storage_send_state.py``);
trang Soạn bài ghi «đang gửi» trước khi gửi, ghi kết quả ngay khi có, đọc lại mỗi lần vẽ nút gửi;
đối tượng giữ kết quả; thứ tự khóa đơn điệu; băm nội dung ảnh lúc duyệt và ngay trước khi tải; lỗi
lạ khi kiểm lại ảnh ra câu cố định. Dùng lại ảnh giả, WordPress giả, AI giả của
``tests/test_app_images.py``; không gọi mạng thật, không dùng ảnh thật.
"""

from __future__ import annotations

import io
import os
import sqlite3
import threading
import time
from contextlib import closing
from pathlib import Path

import streamlit as st
import test_app_images as ui
import test_la_chan_t056 as lc
import test_soi_loi_t056 as sl
from fake_ai import FakeProvider
from PIL import ExifTags, Image
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner_utils.exceptions import StopException
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData
from streamlit.runtime.state.safe_session_state import SafeSessionState

import seo_app.storage.drafts as drafts
from seo_app.ai import AIError
from seo_app.ai import registry as ai_registry
from seo_app.images.folders import ImageLibrary
from seo_app.storage import DraftStore
from seo_app.storage.drafts import DraftError, SendState
from seo_app.text import escape_markdown

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
BUSY = "File nháp đang bận (có thể app mở ở tab khác đang lưu). Thử lại sau giây lát."


# ======================================================== trang Soạn bài: ghi trước, đọc lại


def draft_id(at) -> str:
    return at.session_state["draft_id"]


def saved_state(at) -> SendState | None:
    return ui.store().load_send_state(draft_id(at))


def reopen(project_root, draft: str):
    """Phiên mới (tải lại trang, đóng tab rồi mở lại), cùng kho nháp: mở nháp, sang Xuất bản."""
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    return ui.to_publish(fresh)


def stop_while_uploading(site) -> None:
    """Lần chạy dừng ngay trong lúc tải ảnh (lệnh tải chưa trả lời): ảnh đã lên website."""
    original = site.create_media

    def stopped(request):
        original(request)
        raise StopException()

    site.fake.on("POST", ui.MEDIA, stopped)


def test_pending_written_before_first_request(project_root, root, fake_ai, site):
    """Yêu cầu 1 (SL-T056-11): «đang gửi» đã nằm trong nháp **trước** request đầu tiên tới
    website; gửi xong nháp ghi «đã gửi» kèm mã bài."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = draft_id(at)
    seen: list[SendState | None] = []
    original = site.create_media

    def media(request):
        seen.append(ui.store().load_send_state(draft))
        return original(request)

    site.fake.on("POST", ui.MEDIA, media)
    ui.send(at)
    (before,) = seen
    assert before.pending and before.post_id is None
    after = saved_state(at)
    assert (after.pending, after.post_id) == (False, ui.POST_ID)


def link_urls(at) -> list[str]:
    return [element.proto.url for element in at.get("link_button")]


def test_reopened_sent_draft_needs_new_draft_confirmation(project_root, root, fake_ai, site):
    """SL-T056-8, -11: gửi xong, phiên mới mở lại nháp: nhắc «đã gửi (mã 501)», có link mở bài
    nháp trong trang quản trị, nút khóa tới khi tick «Tạo thêm một bài nháp mới»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    fresh = reopen(project_root, draft_id(at))
    assert button(fresh, SEND).disabled
    (info,) = [i.value for i in fresh.info if "đã gửi lên WordPress" in i.value]
    assert f"mã {ui.POST_ID}" in info.replace("\\", "")
    assert link_urls(fresh) == [f"{ui.BASE_URL}/wp-admin/post.php?post={ui.POST_ID}&action=edit"]
    run_ok(fresh.checkbox(key="_wp_again").check().run())
    assert not button(fresh, SEND).disabled
    ui.send(fresh)
    assert len(site.posts()) == 2


def test_reopened_pending_draft_is_unsure(project_root, root, fake_ai, site):
    """Yêu cầu 1: nháp có «đang gửi» mà chưa có kết quả (tải lại trang khi phiên cũ còn đang gửi,
    hay đã bị ngắt) là «gửi dở»: nhắc kiểm Bài viết → Nháp và Media, khóa tới khi xác nhận."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.store().save_send_state(draft_id(at), SendState.now(pending=True, post_id=None))
    fresh = reopen(project_root, draft_id(at))
    (error,) = [e.value for e in fresh.error if UNSURE in e.value]
    assert "chưa có kết quả" in error and "Media → Thư viện" in error
    assert button(fresh, SEND).disabled and site.fake.requests == []
    run_ok(fresh.checkbox(key="_wp_checked").check().run())
    assert not button(fresh, SEND).disabled


def test_broken_send_state_in_draft_locks(project_root, root, fake_ai, site):
    """Trạng thái gửi trong nháp hỏng: không đoán, coi như chưa rõ kết quả (khóa, nhắc)."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    with closing(sqlite3.connect(drafts.DEFAULT_DRAFTS_FILE)) as conn, conn:
        conn.execute("INSERT INTO send_states (id, data) VALUES (?, ?)", (draft_id(at), "hỏng"))
    run_ok(at.run())
    assert any("Không đọc được trạng thái gửi" in e.value and UNSURE in e.value for e in at.error)
    assert button(at, SEND).disabled


def test_stop_inside_request_keeps_pending_in_draft(project_root, root, fake_ai, site):
    """Lần chạy dừng ngay trong lúc gửi: nháp vẫn ghi «đang gửi»; phiên mới mở lại nháp vẫn khóa
    «gửi dở» (SL-T056-11)."""
    stop_while_uploading(site)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert ui.counts(site) == (0, 1)
    assert saved_state(at).pending
    fresh = reopen(project_root, draft_id(at))
    assert any(UNSURE in e.value for e in fresh.error)
    assert button(fresh, SEND).disabled


def test_real_stop_after_send_records_post_in_draft(project_root, root, fake_ai, site, monkeypatch):
    """Ngắt thật (yêu cầu chạy lại tới trong lúc gửi): kết quả nằm trong đối tượng giữ kết quả và
    trong nháp (đã gửi, mã 501) dù lần chạy dừng ngay sau lệnh gửi (SL-T056-9). Trang hiện kết quả
    kèm lời báo bị ngắt, vẫn khóa «gửi dở». Mở bài khác (không bị khóa) rồi mở lại: khóa «đã gửi»
    (SL-T056-8)."""
    sl.interrupt_while_sending(monkeypatch)
    other = ui.article(keyword="bài khác", article_title="Bài khác")
    ui.store().save(other)
    at, _pid = ui.ready_image(project_root)
    first = draft_id(at)
    ui.to_publish(at)
    ui.send(at)
    state = saved_state(at)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert any("bị ngắt giữa chừng" in c.value for c in at.caption)
    assert any(UNSURE in e.value for e in at.error) and button(at, SEND).disabled
    sl.open_draft_by_id(at, other.id)
    assert not button(at, SEND).disabled  # khóa theo nháp, không theo phiên
    sl.open_draft_by_id(at, first)
    assert button(at, SEND).disabled
    assert any(f"mã {ui.POST_ID}" in i.value.replace("\\", "") for i in at.info)


def test_second_stop_while_locking_without_result_keeps_lock(
    project_root, root, fake_ai, site, monkeypatch
):
    """LC-T056-1 (a), nhánh không có kết quả: lần chạy dừng ngay trong lúc gửi, lần chạy sau lại bị
    dừng đúng lúc ghi câu «gửi dở». Khóa đã dựng trước câu đó, dấu bỏ sau cùng: vẫn khóa."""
    stop_while_uploading(site)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    fired = lc.interrupt_while_marking(monkeypatch)
    run_ok(at.run())
    assert fired == ["_wp_result"]  # đã ngắt đúng chỗ
    assert "_wp_sending" not in at.session_state
    assert any(UNSURE in e.value for e in at.error)
    assert button(at, SEND).disabled


def interrupt_at_first_write(monkeypatch, key: str) -> list[str]:
    """Yêu cầu chạy lại tới đúng lúc ghi ``key`` vào ``st.session_state`` lần đầu (cú bấm tiếp theo
    của người dùng bấm liên tục): lần chạy dừng ngay trước khi ghi."""
    original = SafeSessionState.__setitem__
    fired: list[str] = []

    def setitem(self, name, value):
        if not fired and name == key:
            fired.append(name)
            ctx = get_script_run_ctx()
            ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))
        return original(self, name, value)

    monkeypatch.setattr(SafeSessionState, "__setitem__", setitem)
    return fired


def test_second_stop_at_first_lock_write_keeps_result(
    project_root, root, fake_ai, site, monkeypatch
):
    """LC-T056-1 (a): lần chạy sau lần gửi bị ngắt lại bị dừng ngay ở dòng đầu tiên dựng khóa. Dấu
    «đang gửi» chỉ bỏ sau cùng nên lần sau làm lại từ đầu: vẫn hiện kết quả (SL-T056-9), vẫn khóa.
    Bỏ dấu trước (như trước khi sửa) thì kết quả mất ở bước này."""
    sl.interrupt_while_sending(monkeypatch)
    fired = interrupt_at_first_write(monkeypatch, "_wp_maybe_draft")
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert fired == ["_wp_maybe_draft"]  # đã ngắt đúng chỗ
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert "_wp_sending" not in at.session_state
    assert button(at, SEND).disabled


def running_send(draft: str) -> dict:
    """Đối tượng giữ kết quả của một lần gửi **đang chạy** ở luồng khác (như ``send_draft`` đặt)."""
    return {"draft": draft, "result": None, "state": None, "done": threading.Event()}


def test_new_run_waits_for_send_still_running(project_root, root, fake_ai, site):
    """Streamlit chạy lần mới **ngay**, song song với lần đang gửi (``runner.fastReruns``, mặc định;
    thấy trên trình duyệt thật). Lần mới thấy dấu «đang gửi» khi chưa có kết quả: đợi lần gửi xong
    rồi hiện kết quả (không báo nhầm «không biết kết quả»), vẫn khóa «gửi dở»."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    holder = running_send(draft_id(at))
    at.session_state["_wp_sending"] = holder

    def finish() -> None:
        time.sleep(1)
        holder["result"] = {
            "ok": True,
            "post_id": 777,
            "status": "draft",
            "edit_link": f"{ui.BASE_URL}/wp-admin/post.php?post=777&action=edit",
            "uploaded": [],
            "message": "",
        }
        holder["state"] = (False, 777)
        holder["saved"] = True
        holder["done"].set()

    threading.Thread(target=finish, daemon=True).start()
    run_ok(at.run())
    assert any("mã 777" in s.value for s in at.success)
    assert "_wp_sending" not in at.session_state
    assert any(UNSURE in e.value for e in at.error) and button(at, SEND).disabled


class NeverDone(threading.Event):
    """Lần gửi vẫn chạy quá thời gian đợi (website rất chậm): đợi bao lâu cũng chưa xong."""

    def wait(self, timeout=None):
        return False


def test_send_still_running_after_wait_keeps_mark(project_root, root, fake_ai, site):
    """Đợi hết giờ mà lần gửi song song vẫn chạy: giữ dấu «đang gửi» (lần chạy sau đợi tiếp), báo
    vẫn đang chạy, khóa nút; lần gửi xong thì lần chạy kế tiếp hiện kết quả."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    holder = running_send(draft_id(at))
    holder["done"] = NeverDone()
    at.session_state["_wp_sending"] = holder
    run_ok(at.run())
    assert at.session_state["_wp_sending"] is holder
    assert any("vẫn đang chạy" in e.value for e in at.error)
    assert button(at, SEND).disabled and site.fake.requests == []
    holder["result"] = {"ok": False, "message": "Website báo lỗi 502."}
    holder["state"] = (True, None)
    holder["done"].set()
    run_ok(at.run())
    assert "_wp_sending" not in at.session_state
    assert any("Website báo lỗi 502" in e.value for e in at.error)
    assert button(at, SEND).disabled


def test_result_not_saved_to_draft_is_reported_and_stays_unsure(
    project_root, root, fake_ai, site, monkeypatch
):
    """Ghi kết quả vào nháp hỏng (file nháp đang bận…): trang vẫn hiện kết quả và báo chưa ghi được;
    nháp giữ «đang gửi» nên phiên mới mở lại vẫn khóa «gửi dở» (hướng an toàn)."""
    original = DraftStore.save_send_state
    calls: list[SendState | None] = []

    def flaky(self, draft, state):
        calls.append(state)
        if len(calls) > 1:
            raise DraftError(BUSY)
        return original(self, draft, state)

    monkeypatch.setattr(DraftStore, "save_send_state", flaky)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert len(site.posts()) == 1
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert any("Chưa ghi được kết quả gửi vào nháp" in w.value for w in at.warning)
    assert button(at, SEND).disabled
    monkeypatch.setattr(DraftStore, "save_send_state", original)
    fresh = reopen(project_root, draft_id(at))
    assert any(UNSURE in e.value for e in fresh.error) and button(fresh, SEND).disabled


def test_cannot_write_pending_does_not_send(project_root, root, fake_ai, site, monkeypatch):
    """Chưa ghi được «đang gửi» vào nháp: không gửi gì (thiếu dấu đó, tải lại trang lúc đang gửi là
    mất khóa chống gửi trùng), báo rõ; kho nháp ổn lại thì gửi được."""

    def busy(self, draft, state):
        raise DraftError(BUSY)

    monkeypatch.setattr(DraftStore, "save_send_state", busy)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert site.fake.requests == []
    assert any("Chưa gửi gì lên website" in e.value for e in at.error)
    assert not button(at, SEND).disabled


def test_error_before_any_draft_clears_pending(project_root, root, fake_ai, site):
    """Website từ chối ảnh (4xx, chắc chắn chưa tạo bài nháp): nháp không giữ «đang gửi», trang và
    phiên mới không khóa."""
    site.fake.on("POST", ui.MEDIA, lambda _r: (400, {"code": "x", "message": "Bad request"}, {}))
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert ui.counts(site) == (0, 1)
    assert saved_state(at) is None
    assert not button(at, SEND).disabled
    fresh = reopen(project_root, draft_id(at))
    assert not button(fresh, SEND).disabled


# ============================================================== băm nội dung ảnh (yêu cầu 4)


def replace_in_place(path: Path) -> None:
    """Thay file tại chỗ bằng ảnh khác (có GPS) **cùng cỡ**, rồi đặt lại giờ sửa cũ (Ghi nhận 1 của
    Lá Chắn T-056): cỡ, giờ sửa, định danh trên ổ đều như cũ, chỉ nội dung khác."""
    before = path.stat()
    new = ui.jpeg((64, 48), (10, 10, 10), gps=True)
    assert len(new) < before.st_size
    path.write_bytes(new + b"\x00" * (before.st_size - len(new)))  # JPEG bỏ qua phần đệm sau EOI
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    after = path.stat()
    assert (after.st_size, after.st_mtime_ns, after.st_ino) == (
        before.st_size,
        before.st_mtime_ns,
        before.st_ino,
    )


def test_file_replaced_in_place_stops_and_shows_new_file(
    project_root, root, fake_ai, site, monkeypatch
):
    """Yêu cầu 4: file bị thay tại chỗ bằng ảnh khác cùng cỡ, giờ sửa đặt lại như cũ (lần kiểm lại
    theo cỡ, giờ sửa, định danh không thấy gì): băm byte sắp tải khác bản đã duyệt → dừng, chưa gửi
    gì, bỏ duyệt. Khung ảnh hiện đúng file mới (dòng GPS tính lại, ảnh xem trước dựng từ file chứ
    không lấy bản cũ trong cache); duyệt lại rồi gửi đúng file mới."""
    shown: list[object] = []
    original_image = st.image

    def image(data, *args, **kwargs):
        shown.append(data)
        return original_image(data, *args, **kwargs)

    monkeypatch.setattr(st, "image", image)
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, ui.PROJECT)
    ui.open_sub(at, "sau")
    ui.choose(at, "IMG_0002.jpg")
    ui.write_alt(at, pid)
    ui.approve(at, pid)
    assert any(c.value == "Ảnh không có vị trí GPS." for c in at.caption)
    ui.to_publish(at)
    replace_in_place(root / ui.PROJECT / "sau" / "IMG_0002.jpg")
    ui.send(at)
    assert site.fake.requests == []
    problems = [m.value.replace("\\", "") for m in at.markdown]
    assert any("nội dung file khác bản bạn đã xem và duyệt" in p for p in problems)
    assert at.session_state[f"altok-{pid}"] is False
    assert button(at, SEND).disabled
    at.session_state["step"] = 2
    shown.clear()
    run_ok(at.run())
    assert any(c.value.startswith("📍 Ảnh có vị trí GPS") for c in at.caption)
    sizes = [Image.open(io.BytesIO(data)).size for data in shown if isinstance(data, bytes)]
    assert sizes == [(64, 48)]  # ảnh xem trước của file mới
    ui.approve(at, pid)
    ui.to_publish(at)
    ui.send(at)
    (upload,) = site.uploads()
    with Image.open(io.BytesIO(upload.body)) as web:
        assert web.size == (64, 48) and web.getexif().get_ifd(ExifTags.IFD.GPSInfo)


def test_approval_bound_to_shown_version(project_root, root, fake_ai, site):
    """Lần duyệt gắn với băm của bản ảnh đang hiện; sửa alt (bỏ duyệt) thì bỏ băm; duyệt lại thì
    gắn lại; chọn ảnh khác thì bỏ."""
    at, pid = ui.ready_image(project_root)
    first = at.session_state[f"altsha-{pid}"]
    assert len(first) == 64
    run_ok(at.text_input(key=f"alt-{pid}").input("Bản lề cổng inox bị gỉ").run())
    assert f"altsha-{pid}" not in at.session_state
    ui.approve(at, pid)
    assert at.session_state[f"altsha-{pid}"] == first
    run_ok(ui.by_key(at, f"unpick-{pid}").click().run())
    assert f"altsha-{pid}" not in at.session_state


# ======================================================= lỗi lạ, chữ hiện ra (yêu cầu 5)


def test_unexpected_error_in_image_check_fixed_message(
    project_root, root, fake_ai, site, monkeypatch
):
    """Ghi nhận 2 của Lá Chắn T-056: lỗi lạ khi kiểm lại ảnh (trong luồng quét, hay lúc chọn ảnh)
    hiện câu cố định; không dấu vết lỗi, không đường dẫn; không gọi AI, không gửi gì."""
    at, pid = ui.ready_image(project_root)
    ai_calls = len(fake_ai.image_calls)

    def boom(*args, **kwargs):
        raise RuntimeError(r"C:\Users\bi-mat\anh.jpg")

    monkeypatch.setattr(drafts, "check_chosen_image", boom)
    run_ok(ui.by_key(at, f"altai-{pid}").click().run())  # «AI viết lại alt»
    assert any("Chưa kiểm lại được ảnh này" in e.value for e in at.error)
    assert len(fake_ai.image_calls) == ai_calls
    ui.to_publish(at)
    ui.send(at)
    assert site.fake.requests == []
    assert any("Chưa kiểm lại được ảnh này" in m.value for m in at.markdown)
    at.session_state["step"] = 2
    run_ok(at.run())
    ui.browse(at, pid)
    ui.choose(at, "IMG_0001.jpg")
    assert any("Chưa kiểm lại được ảnh này" in w.value for w in at.warning)
    assert not at.exception
    assert not any("bi-mat" in text for text in ui.texts(at))


def test_ai_error_and_folder_notice_are_escaped(project_root, root, monkeypatch):
    """Ghi nhận 3 của Lá Chắn T-056: câu lỗi AI, câu báo của lần quét hiện qua ``escape_markdown``
    như mọi chỗ khác (không thành link, chữ đậm)."""
    message = "Lỗi [bấm đây](https://evil.example) **gấp**"

    class Failing(FakeProvider):
        def generate(self, task, **kwargs):
            raise AIError(message)

    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: Failing())
    notice = "Thư mục [lạ](https://evil.example) _rất_ nhiều mục"
    original = ImageLibrary.list_folder

    def noisy(self, *args, **kwargs):
        listing = original(self, *args, **kwargs)
        return ui.dataclasses.replace(listing, notice=notice)

    monkeypatch.setattr(ImageLibrary, "list_folder", noisy)
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    assert escape_markdown(notice) in [w.value for w in at.warning]
    ui.open_sub(at, ui.PROJECT)
    ui.open_sub(at, "truoc")
    ui.choose(at, "IMG_0001.jpg")
    ui.write_alt(at, pid)
    assert escape_markdown(message) in [e.value for e in at.error]

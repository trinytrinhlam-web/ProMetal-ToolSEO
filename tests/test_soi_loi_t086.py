"""Soi Lỗi T-086: trạng thái gửi nháp không chỉ nằm trong phiên (``app/views/write.py``,
``seo_app/storage/drafts.py``).

Kiểm lại SL-T056-8 → -11 và LC-T056-1 sau bản sửa của Họa Sĩ, thêm:

- ngắt lần chạy thật (yêu cầu chạy lại qua ``ScriptRequests.request_rerun``, đúng đường một cú bấm
  trên trình duyệt) ở **từng** lần ghi ``st.session_state`` sau khi website trả lời, và ngắt hai lần
  liên tiếp: lần nào cũng đúng một bài, vẫn khóa, vẫn hiện kết quả, kho nháp ghi đúng;
- trạng thái gửi trong nháp bị sửa tay (kiểu sai, giá trị lạ, quá lớn): khóa «gửi dở», không đoán;
- hai tab cùng một nháp; ảnh xem trước cũ trong cache khi file bị thay tại chỗ.

Lỗi tìm được: ``xfail(strict=True)`` mã SL-T086-x (``docs/team/reports/T-086-soi-loi.md``). Test
dùng ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; không gọi mạng thật.
"""

from __future__ import annotations

import io
import sqlite3
from contextlib import closing

import pytest
import streamlit as st
import test_app_images as ui
import test_soi_loi_t056 as sl
import test_t086_send_state as t86
from PIL import Image
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData
from streamlit.runtime.state.safe_session_state import SafeSessionState

import seo_app.storage.drafts as drafts
from seo_app.images.folders import ImageLibrary
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
SUCCESS = "Đã tạo bài nháp trên WordPress"


def interrupt_at_write_after_post(monkeypatch, site, n: int) -> list[tuple[str, str]]:
    """Cú bấm của người dùng tới đúng lúc app sắp ghi (hay xóa) khóa thứ ``n`` vào
    ``st.session_state`` **sau khi** website đã tạo bài nháp: lần chạy dừng ngay trước lần ghi đó
    (``SafeSessionState`` xét yêu cầu chạy lại trước mỗi thao tác). Trả khóa đã ngắt."""
    created: list[int] = []
    original_post = site.create_post

    def create_post(request):
        created.append(1)
        return original_post(request)

    site.fake.on("POST", ui.POSTS, create_post)
    writes: list[tuple[str, str]] = []
    fired: list[tuple[str, str]] = []
    original_set, original_del = SafeSessionState.__setitem__, SafeSessionState.__delitem__

    def maybe_fire(kind: str, name: str) -> None:
        ctx = get_script_run_ctx()
        if not created or fired or ctx is None or ctx.script_requests is None:
            return
        writes.append((kind, name))
        if len(writes) == n:
            fired.append((kind, name))
            ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))

    def setitem(self, name, value):
        maybe_fire("ghi", name)
        return original_set(self, name, value)

    def delitem(self, name):
        maybe_fire("xóa", name)
        return original_del(self, name)

    monkeypatch.setattr(SafeSessionState, "__setitem__", setitem)
    monkeypatch.setattr(SafeSessionState, "__delitem__", delitem)
    return fired


def assert_one_post_locked_with_result(at, site) -> None:
    """Sau mọi kiểu ngắt: đúng một bài, một ảnh; vẫn hiện kết quả; nút khóa; nháp ghi «đã gửi»
    đúng mã; không còn dấu «đang gửi» sót."""
    for _ in range(2):  # lần chạy kế tiếp (người dùng bấm gì đó)
        run_ok(at.run())
    assert (len(site.posts()), len(site.uploads())) == (1, 1)
    assert any(SUCCESS in s.value for s in at.success)
    assert button(at, SEND).disabled
    state = ui.store().load_send_state(at.session_state["draft_id"])
    assert (state.pending, state.post_id) == (False, ui.POST_ID)
    assert "_wp_sending" not in at.session_state


# ============================================================ ngắt lần chạy ở từng lần ghi


@pytest.mark.parametrize("n", [1, 2, 3, 4, 13])
def test_interrupt_at_each_write_after_send(project_root, root, fake_ai, site, monkeypatch, n):
    """Lần chạy gửi bị ngắt ở lần ghi thứ ``n`` sau khi website đã tạo bài (1–3: ngay trong lúc
    dựng kết quả, khóa; sau đó: lần chạy lại trang). SL-T056-1, -9, LC-T056-1."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    fired = interrupt_at_write_after_post(monkeypatch, site, n)
    ui.send(at)
    assert fired  # đã ngắt đúng một lần
    assert_one_post_locked_with_result(at, site)


@pytest.mark.parametrize("n", list(range(1, 8)))
def test_double_interrupt_each_write(project_root, root, fake_ai, site, monkeypatch, n):
    """Ngắt hai lần liên tiếp (người dùng bấm liên tục): lần một trong lúc lệnh gửi đang chạy, lần
    hai ở lần ghi thứ ``n`` của các lần chạy sau (dựng khóa «gửi dở», hiện kết quả, bỏ dấu). Thứ tự
    «khóa trước, bỏ dấu sau» giữ đúng ở mọi chỗ (LC-T056-1)."""
    sl.interrupt_while_sending(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    fired = interrupt_at_write_after_post(monkeypatch, site, n)
    ui.send(at)
    assert fired
    assert_one_post_locked_with_result(at, site)
    assert any(UNSURE in e.value for e in at.error)  # đã bị ngắt: vẫn đòi xác nhận


# ======================================================= trạng thái gửi trong nháp bị sửa tay


BROKEN_STATES = [
    '{"pending": "yes", "post_id": null, "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": 0, "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": -5, "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": 1.5, "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": "501", "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": 9223372036854775808, "updated_at": "2026-10-26T10:00:00+07:00"}',
    '{"pending": false, "post_id": 501, "updated_at": "2026-10-26T10:00:00"}',
    '{"pending": false, "post_id": 501, "updated_at": "2026-10-26T10:00:00+07:00", "x": 1}',
    '{"pending": false, "post_id": 501}',
    "[]",
    "null",
    "x" * 5000,
    12345,
    b"\xff\xfe",
]


@pytest.mark.parametrize("data", BROKEN_STATES, ids=range(len(BROKEN_STATES)))
def test_tampered_send_state_locks(project_root, root, fake_ai, site, data):
    """Trạng thái gửi trong nháp bị sửa tay (kiểu sai, số không hợp lệ, giờ không múi, trường lạ,
    thiếu trường, không phải đối tượng, quá 4 KB, kiểu cột lạ, byte lạ): trang không lỗi, khóa
    «gửi dở» kèm câu báo, không đoán, không gửi gì."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    with closing(sqlite3.connect(drafts.DEFAULT_DRAFTS_FILE)) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO send_states (id, data) VALUES (?, ?)",
            (at.session_state["draft_id"], data),
        )
    run_ok(at.run())
    assert any("Không đọc được trạng thái gửi" in e.value and UNSURE in e.value for e in at.error)
    assert button(at, SEND).disabled
    assert site.fake.requests == []


@pytest.mark.parametrize(
    "data",
    [
        '{"pending": false, "post_id": 501, "updated_at": "9999-12-31T23:59:59+14:00"}',
        '{"pending": false, "post_id": 501, "updated_at": "0001-01-01T00:00:00-12:00"}',
        '{"pending": false, "post_id": 9223372036854775807, "updated_at": "2026-10-26T10:00:00Z"}',
    ],
)
def test_extreme_but_valid_send_state_shows_sent(project_root, root, fake_ai, site, data):
    """Giá trị hợp lệ mà cực đoan (giờ năm 9999, năm 1, mã bài lớn nhất): khóa «đã gửi», hiện số và
    giờ, trang không lỗi."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    with closing(sqlite3.connect(drafts.DEFAULT_DRAFTS_FILE)) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO send_states (id, data) VALUES (?, ?)",
            (at.session_state["draft_id"], data),
        )
    run_ok(at.run())
    assert any("đã gửi lên WordPress" in i.value for i in at.info)
    assert button(at, SEND).disabled


# ================================================================== hai tab cùng một nháp


def test_other_tab_after_send_is_locked(project_root, root, fake_ai, site):
    """Tab 2 mở cùng nháp từ trước (nút gửi đang bật); tab 1 gửi xong; người dùng bấm «Gửi nháp» ở
    tab 2: lần chạy đó đọc lại trạng thái trong nháp, khóa «đã gửi», không gửi thêm."""
    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    other = t86.reopen(project_root, draft)  # tab 2, phiên riêng
    assert not button(other, SEND).disabled
    ui.to_publish(at)
    ui.send(at)
    assert len(site.posts()) == 1
    button(other, SEND).click().run()
    assert len(site.posts()) == 1
    assert button(other, SEND).disabled


def test_other_tab_starts_sending_while_this_tab_prepares(
    project_root, root, fake_ai, site, monkeypatch
):
    """Tab 2 bấm «Gửi nháp» (nút bật vì lúc đó nháp chưa có trạng thái gửi), rồi kiểm lại và nén ảnh
    (vài giây với ảnh lớn); trong lúc đó tab 1 ghi «đang gửi» vào nháp. Tab 2 không đọc lại, ghi đè
    «đang gửi» của mình và gửi: website có hai bài nháp, hai lần tải ảnh. Thấy trên trình duyệt thật
    (WordPress giả, ảnh 28 MB, hai tab bấm cách nhau 1 giây: bài 501 và 502, không tab nào nhắc).
    Ở đây «tab 1» ghi «đang gửi» đúng lúc tab 2 đọc ảnh để nén. Mong đợi: ghi «đang gửi» kiểu so rồi
    đặt (trong một giao dịch SQLite: trạng thái trong nháp vẫn như lúc người dùng xác nhận thì mới
    ghi); khác thì dừng, chưa gửi gì, nhắc nháp vừa được gửi ở cửa sổ khác."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    original = ImageLibrary.read_image_bytes
    pending = [True]

    def read(self, ref):
        if pending:
            pending.pop()
            ui.store().save_send_state(draft, SendState.now(pending=True, post_id=None))  # tab 1
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", read)
    ui.send(at)
    assert site.fake.requests == []


# ========================================================= ảnh xem trước cũ, băm nội dung mới


def test_preview_shown_matches_approved_content(project_root, root, fake_ai, site, monkeypatch):
    """Lưới ảnh đã tạo ảnh xem trước của ``IMG_0002.jpg`` (cache trên ổ, khóa theo cỡ và giờ sửa).
    File bị thay tại chỗ bằng ảnh khác cùng cỡ, giờ sửa đặt lại như cũ, **có GPS**. Chọn ảnh: khung
    vẫn hiện ảnh xem trước của bản cũ (cache), nhưng dòng GPS và băm gắn với lần duyệt
    (``web_info``) là của file mới. Duyệt, gửi: băm khớp nên ảnh mới (64×48, có GPS) lên website,
    người dùng chưa từng thấy nó. Mong đợi: ảnh xem trước dựng từ đúng byte đã băm (hoặc lần gửi
    dừng)."""
    shown: list[object] = []
    original_image = st.image

    def image(data, *args, **kwargs):
        shown.append(data)
        return original_image(data, *args, **kwargs)

    monkeypatch.setattr(st, "image", image)
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, ui.PROJECT)
    ui.open_sub(at, "sau")  # lưới: ảnh xem trước của bản cũ vào cache
    t86.replace_in_place(root / ui.PROJECT / "sau" / "IMG_0002.jpg")
    shown.clear()
    ui.choose(at, "IMG_0002.jpg")
    previews = [Image.open(io.BytesIO(d)).size for d in shown if isinstance(d, bytes)]
    assert any(c.value.startswith("📍 Ảnh có vị trí GPS") for c in at.caption)  # dòng GPS: file mới
    ui.write_alt(at, pid)
    ui.approve(at, pid)
    ui.to_publish(at)
    ui.send(at)
    uploaded = [Image.open(io.BytesIO(u.body)).size for u in site.uploads()]
    assert previews == [(64, 48)] or uploaded == [], (previews, uploaded)

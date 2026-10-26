"""T-089: dọn lỗi Thấp của «Gửi nháp» sau T-086 (LC-T086-1, SL-T086-1, SL-T086-2) và lưu băm ảnh
đã duyệt trong nháp (Ghi nhận 1 của Lá Chắn T-086).

- LC-T086-1: website trả mã bài ngoài khoảng nháp ghi được: câu cố định, trang không lỗi, vẫn khóa.

Dùng lại ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``; không gọi mạng thật.
"""

from __future__ import annotations

import test_app_images as ui
import test_soi_loi_t056 as sl

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

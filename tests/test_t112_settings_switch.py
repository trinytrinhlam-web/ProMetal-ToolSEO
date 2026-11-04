"""T-112 yêu cầu 2 (Chỉ Huy B chọn A 31/10 09:55): công tắc Hẹn giờ / Đăng ngay ở Cài đặt →
«📅 Hẹn giờ, đăng» (LC-T094-41).

- Mặc định tắt; bật phải tick «Tôi hiểu: bài sẽ được hẹn giờ/đăng công khai thật…» trước; bỏ tick
  là tắt.
- **Chỉ trong phiên** (``st.session_state``): phiên mới (mở lại app, tải lại trang) là tắt; không
  ghi file nào; tham số địa chỉ, file nháp sửa tay không bật được.
- Bước Xuất bản của Soạn bài đọc đúng công tắc này (cùng khóa ``_release_enabled``).

Không gọi WordPress, Google, AI thật.
"""

from __future__ import annotations

import test_app_images as ui
import test_app_pages as pages
import test_soi_loi_t041 as sl41

import seo_app.config as config

env = pages.env
previews = ui.previews

SWITCH = "_release_enabled"  # khóa công tắc của bước Xuất bản (``RELEASE_SWITCH``)
ACK, TOGGLE = "release_ack", "release_toggle"


def run(target):
    """Chạy lại trang (``target``: AppTest hay phần tử vừa đổi giá trị); không lỗi."""
    at = target.run()
    assert not at.exception, at.exception
    return at


def open_settings(project_root):
    return pages.open_page(project_root, "settings.py")


def turn_on(at):
    run(at.checkbox(key=ACK).check())
    run(at.toggle(key=TOGGLE).set_value(True))
    return at


def switch_on(at) -> bool:
    return at.session_state[SWITCH] is True if SWITCH in at.session_state else False


def test_default_off_and_toggle_needs_ack(project_root):
    at = open_settings(project_root)
    assert not switch_on(at)
    toggle = at.toggle(key=TOGGLE)
    assert toggle.value is False and toggle.disabled  # chưa tick «Tôi hiểu…»
    assert at.checkbox(key=ACK).value is False
    assert any("đang **tắt** (mặc định)" in i.value for i in at.info)
    assert any("mỗi lần mở app, tải lại trang là tắt" in i.value for i in at.info)


def test_turn_on_reaches_publish_step_and_survives_page_change(project_root):
    at = turn_on(open_settings(project_root))
    assert switch_on(at)
    assert any("đang **bật**" in w.value and "tự tắt" in w.value for w in at.warning)
    at.switch_page("views/write.py")
    run(at)
    at.session_state["step"] = 4
    run(at)
    run(at.segmented_control(key="_wp_mode").set_value("Hẹn giờ"))
    assert not any("Hẹn giờ và Đăng ngay đang **tắt**" in i.value for i in at.info)
    at.switch_page("views/settings.py")
    run(at)
    assert at.toggle(key=TOGGLE).value is True and at.checkbox(key=ACK).value is True


def test_untick_ack_turns_off(project_root):
    at = turn_on(open_settings(project_root))
    run(at.checkbox(key=ACK).uncheck())
    assert not switch_on(at)
    toggle = at.toggle(key=TOGGLE)
    assert toggle.value is False and toggle.disabled


def test_publish_step_tells_where_to_turn_on(project_root):
    at = pages.open_page(project_root, "write.py")
    at.session_state["step"] = 4
    run(at)
    run(at.segmented_control(key="_wp_mode").set_value("Đăng ngay"))
    assert any("Cài đặt → 📅 Hẹn giờ, đăng" in i.value for i in at.info)
    assert not any(b.key == "wp-send" for b in at.button)


def test_new_session_is_off_and_nothing_is_written(project_root):
    """Chỉ trong phiên: mở lại app (phiên mới) là tắt; không ghi ``.env`` hay file nào để nhớ."""
    turn_on(open_settings(project_root))
    assert not config.DEFAULT_ENV_FILE.exists()
    fresh = open_settings(project_root)
    assert not switch_on(fresh)
    assert fresh.toggle(key=TOGGLE).value is False


def test_query_params_cannot_turn_on(project_root):
    at = open_settings(project_root)
    for name in (SWITCH, ACK, TOGGLE):
        at.query_params[name] = "true"
    run(at)
    assert not switch_on(at)
    assert at.toggle(key=TOGGLE).value is False


def test_hand_edited_draft_cannot_turn_on(project_root):
    """File nháp sửa tay thêm khóa công tắc: không bật được (nháp không mang công tắc)."""

    def sneak(obj):
        obj[SWITCH] = True
        obj["release_enabled"] = True

    draft_id = sl41._saved_and_edited(ui.article(), sneak)
    at = pages.open_page(project_root, "write.py")
    open_buttons = [b for b in at.button if b.key == f"open-{draft_id}"]
    if open_buttons:
        run(open_buttons[0].click())
    assert not switch_on(at)
    at.session_state["step"] = 4
    run(at)
    run(at.segmented_control(key="_wp_mode").set_value("Hẹn giờ"))
    assert any("Hẹn giờ và Đăng ngay đang **tắt**" in i.value for i in at.info)

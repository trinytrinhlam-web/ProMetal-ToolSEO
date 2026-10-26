"""Lá Chắn T-086: trạng thái «Gửi nháp» lưu trong nháp (SL-T056-8 → -11, LC-T056-1).

Bổ sung cho ``tests/test_t086_send_state.py`` (Họa Sĩ) và ``tests/test_soi_loi_t086.py`` (Soi
Lỗi), dùng lại ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``. Không gọi mạng thật.

- **LC-T086-1** (Thấp): website trả mã bài từ 2⁶³ trở lên (client nhận mọi số nguyên dương,
  ``_positive_id``) thì ``record_outcome`` dựng ``SendState`` **ngoài** khối bắt lỗi: lỗi
  ``ValidationError`` thoát ra, trang in dấu vết lỗi (có đường dẫn mã nguồn trên máy), và mọi lần
  chạy sau của phiên cũng lỗi vì ``finish_send`` gọi lại ``record_outcome``. Khóa vẫn giữ (nháp còn
  «đang gửi»). Đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu.
- Đối chứng (đang qua): mã bài ghi trong nháp (dữ liệu chưa tin cậy, có thể bị sửa tay) chỉ dùng
  để hiện và dựng link «Mở bài nháp» bằng ``client.edit_link``; gửi lại không ghi gì vào bài đó
  trên website (W2).
"""

from __future__ import annotations

import pytest
import test_app_images as ui

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
HUGE_ID = 2**63  # WordPress lưu mã bài kiểu BIGINT UNSIGNED: tới 2⁶⁴ − 1 vẫn là số hợp lệ của site


@pytest.mark.xfail(
    strict=True,
    reason="LC-T086-1: mã bài website trả từ 2⁶³ làm record_outcome ném lỗi ngoài khối bắt",
)
def test_lc_t086_1_huge_post_id_from_site_does_not_break_page(project_root, root, fake_ai, site):
    """Website trả mã bài 2⁶³ (site hỏng hay bị chiếm; client không giới hạn trên). Mong đợi: trang
    không lỗi, vẫn khóa nút (nháp còn «đang gửi» hay đã ghi kết quả), lần chạy sau cũng không lỗi.
    Thực tế: ``SendState.now(post_id=2⁶³)`` ném ``ValidationError`` ngoài ``try`` của
    ``record_outcome``: lỗi thoát lên trang, và ``finish_send`` gọi lại ở mọi lần chạy sau."""
    at, _pid = ui.open_article(project_root)  # bài có chỗ cần ảnh nhưng chưa chọn ảnh
    ui.to_publish(at)
    site.fake.on(
        "POST",
        ui.POSTS,
        lambda _r: (201, {"id": HUGE_ID, "status": "draft", "title": {"raw": "T"}}, {}),
    )
    assert not button(at, SEND).disabled
    button(at, SEND).click().run()
    assert len(site.posts()) == 1  # bài nháp đã lên website
    state = ui.store().load_send_state(at.session_state["draft_id"])
    assert state is not None and state.pending  # khóa vẫn giữ trong nháp
    assert not at.exception, "trang in dấu vết lỗi"
    at.run()
    assert not at.exception, "lần chạy sau vẫn lỗi"
    assert button(at, SEND).disabled


def test_saved_post_id_never_used_to_write_to_wordpress(project_root, root, fake_ai, site):
    """Nháp ghi «đã gửi, bài 777» (ví dụ bị sửa tay trỏ tới một bài có sẵn trên website). Mở lại:
    khóa «đã gửi», link «Mở bài nháp» là ``client.edit_link(777)``; tick «Tạo thêm…», gửi: chỉ tạo
    bài mới (``POST /wp/v2/posts``) và tải ảnh, không lệnh nào tới bài 777; nháp ghi bài mới."""
    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=777))
    fresh = ui.pages.open_page(project_root, "write.py")  # phiên mới, cùng kho nháp
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    ui.to_publish(fresh)
    assert button(fresh, SEND).disabled
    shown = "\n".join(info.value for info in fresh.info)
    assert "bài nháp mã 777" in shown
    links = [el.proto.url for el in fresh.get("link_button")]
    assert links == [f"{ui.BASE_URL}/wp-admin/post.php?post=777&action=edit"]
    run_ok(fresh.checkbox(key="_wp_again").check().run())
    run_ok(button(fresh, SEND).click().run())
    paths = [ui.path_of(request) for request in site.fake.requests]
    assert not any(path.endswith("/777") for path in paths), paths
    assert paths.count(ui.POSTS) == 1
    state = ui.store().load_send_state(draft)
    assert (state.pending, state.post_id) == (False, ui.POST_ID)

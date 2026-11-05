"""Soi Lỗi T-092 (rút gọn): nháp bị xóa ở một tab khi tab khác còn mở bài đó.

Kiểm độc lập, mượn khung trang Soạn bài, ảnh giả, WordPress giả, AI giả của
``tests/test_app_images.py`` và WordPress giả cho Hẹn giờ (``live``) của
``tests/test_t102_publish.py`` như file của Họa Sĩ; mọi ca, mọi kiểm là của Soi Lỗi. Không gọi
WordPress, Google, AI thật.

1. Tab còn mở **biết** bài đã gửi (thấy «đã gửi» trong kho) mà nháp bị xóa ở tab khác: bước Xuất
   bản không còn khóa gửi trùng (SL-T092-1), kèm đối chứng tab tự gửi.
2. Biến thể của yêu cầu 1: nháp được tab khác lưu lại, file nháp bị xóa khi app đang chạy.
"""

from __future__ import annotations

import test_app_images as ui
import test_t041_seo_ui as t41
import test_t102_publish as t102

from seo_app.storage.drafts import SendState

env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live
site_cache = t41.site_cache

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL
GONE = "không còn trong kho nháp"
KNOWN_SENT = "Tab này biết bài đã gửi"
RECREATE = "💾 Lưu lại thành nháp"
OTHER_TAB_POST = 777  # bài tab khác đã gửi


def notice(at) -> str:
    """Câu báo nháp không còn trong kho (rỗng: không có)."""
    return next((w.value for w in at.warning if GONE in w.value), "")


def saved_ids() -> list[str]:
    return [d.id for d in ui.store().list_drafts().drafts]


def again_box(at) -> bool:
    """Ô «Tạo thêm một bài …» (khóa gửi trùng của T-086) đang hiện."""
    return any("Tạo thêm" in box.label for box in at.checkbox)


def sent_elsewhere_then_deleted(at) -> str:
    """Tab khác gửi xong bài 777 (tab này vẽ lại, thấy «đã gửi 777», khóa gửi trùng), rồi tab khác
    xóa nháp; tab này vẽ lại hai lần (báo «Tab này biết bài đã gửi»)."""
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=OTHER_TAB_POST))
    run_ok(at.run())
    assert again_box(at)  # trước khi xóa: phải tick «Tạo thêm…» mới gửi được
    assert ui.store().delete(draft)
    run_ok(at.run())
    run_ok(at.run())
    assert KNOWN_SENT in notice(at) and draft not in saved_ids()
    return draft


# ====================================================================== 1. khóa gửi trùng
def test_sl_t092_1_tab_biet_da_gui_nhap_bi_xoa_khong_gui_trung(project_root, root, fake_ai, site):
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    sent_elsewhere_then_deleted(at)
    if not button(at, SEND).disabled:
        ui.send(at)
    assert site.posts() == []  # không tạo bài thứ hai trên website


def test_sl_t092_1_hen_gio_cung_mo_khoa(project_root, root, fake_ai, live):
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, "Hẹn giờ")
    sent_elsewhere_then_deleted(at)
    t102.confirm(at)
    if not t102.send_button(at).disabled:
        run_ok(t102.send_button(at).click().run())
    assert live.site.posts() == [] and t102.release_bodies(live.site) == []


def test_doi_chung_tab_tu_gui_van_khoa_sau_khi_nhap_bi_xoa(project_root, root, fake_ai, site):
    """Đối chứng: tab **tự** gửi bài (``_wp_sent``) thì sau khi nháp bị xóa ở tab khác vẫn phải
    tick «Tạo thêm…» mới gửi được; website vẫn một bài."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    draft = at.session_state["draft_id"]
    assert ui.store().delete(draft)
    run_ok(at.run())
    run_ok(at.run())
    assert KNOWN_SENT in notice(at)
    assert again_box(at) and button(at, SEND).disabled
    assert len(site.posts()) == 1


def test_doi_chung_nhap_con_thi_van_khoa(project_root, root, fake_ai, site):
    """Đối chứng: nháp **còn** (không ai xóa), tab thấy «đã gửi 777»: nút khóa qua nhiều lần vẽ."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=OTHER_TAB_POST))
    for _ in range(3):
        run_ok(at.run())
        assert again_box(at) and button(at, SEND).disabled
    assert site.posts() == []


# ====================================================================== 2. biến thể yêu cầu 1
def test_nhap_duoc_tab_khac_luu_lai_thi_het_bao_va_tu_luu_tiep(project_root):
    """Nháp bị xóa rồi được tab khác lưu lại (cùng mã): tab này hết báo, tự lưu tiếp như hai tab
    cùng sửa một nháp (tab lưu sau thắng), không tạo nháp thứ hai."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    snap = ui.store().load(draft)
    assert ui.store().delete(draft)
    at.session_state["step"] = 1
    run_ok(at.run())
    assert notice(at) and saved_ids() == []
    ui.store().save(snap)  # tab khác bấm «Lưu lại thành nháp»
    run_ok(at.run())
    assert notice(at) == ""
    assert saved_ids() == [draft] and ui.store().load(draft).step == 1  # bản của tab này
    at.session_state["step"] = 0
    run_ok(at.run())
    assert saved_ids() == [draft] and ui.store().load(draft).step == 0


def test_file_nhap_bi_xoa_khi_app_dang_chay(project_root):
    """Cả file nháp bị xóa khi app đang chạy: không lặng lẽ tạo lại; bấm lưu lại thì có lại."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    ui.store().path.unlink()
    at.session_state["step"] = 1
    run_ok(at.run())
    assert notice(at) and saved_ids() == []
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert saved_ids() == [draft] and ui.store().load(draft).step == 1
    assert notice(at) == ""

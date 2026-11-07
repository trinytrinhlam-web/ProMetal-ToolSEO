"""Soi Lỗi T-130 (rút gọn): giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa.

Kiểm độc lập, mượn khung trang Soạn bài, ảnh giả, WordPress giả, AI giả của
``tests/test_app_images.py`` và các hàm của ``tests/test_t086_send_state.py``,
``tests/test_t092_nhap_bi_xoa.py`` như file của Họa Sĩ; mọi ca, mọi kiểm là của Soi Lỗi. Không gọi
WordPress, Google, AI thật.

1. G1 của Soi Lỗi T-092 (ba tab) chạy hết bằng giao diện: tab không biết bấm «Lưu lại thành nháp»,
   tab đã biết và phiên mới vẫn khóa, bấm gửi không ra bài thứ hai.
2. «Bỏ bài này» ở tab thấy nháp không còn không xóa dòng giữ lại; nháp «gửi dở» bị xóa rồi lưu lại
   ở tab không biết vẫn khóa «gửi dở».
3. Popover «🗑️ Xóa» của bài đã hẹn giờ, đã đăng.
4. Dọn dòng mồ côi khi kho đầy: không đụng trạng thái gửi của nháp còn, giữ đúng dòng ghi gần nhất.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta

import pytest
import test_app_images as ui
import test_t041_seo_ui as t41
import test_t086_send_state as t86
import test_t092_nhap_bi_xoa as t92

from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import SendState

env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
site_cache = t41.site_cache

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL
notice = t92.notice
saved_ids = t92.saved_ids
KNOWN_SENT = t92.KNOWN_SENT
RECREATE = t92.RECREATE
AGAIN = "Tạo thêm một bài nháp mới"
CHECKED = "Tôi đã kiểm tra trang quản trị, vẫn muốn gửi"


def box(at, label: str):
    return next((b for b in at.checkbox if b.label == label), None)


def try_send(at) -> None:
    """Bấm «Gửi nháp» nếu nút đang mở (nút khóa thì AppTest không cho bấm)."""
    if not button(at, SEND).disabled:
        ui.send(at)


# ====================================================================== 1. ba tab (G1 T-092)
def test_g1_ba_tab_tab_khong_biet_luu_lai_moi_tab_van_khoa(project_root, root, fake_ai, site):
    """Tab A đứng ở bước Xuất bản, thấy «đã gửi 777» (tab khác gửi). Tab B mở bài từ trước lần
    gửi, chưa vẽ lại. Nháp bị xóa. Tab B làm tiếp: khung báo nói tab biết bài đã gửi (đọc dòng giữ
    lại), bấm «Lưu lại thành nháp»: nháp có lại kèm «đã gửi 777». Tab A, tab B, phiên mới đều khóa
    gửi trùng; bấm gửi không ra bài nào (T-092 lúc trước: tab A mất khóa, ra bài thứ hai)."""
    tab_a, _pid = ui.ready_image(project_root)
    ui.to_publish(tab_a)
    draft = tab_a.session_state["draft_id"]
    tab_b = t86.reopen(project_root, draft)  # mở bài trước lần gửi
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=777))  # tab khác gửi
    run_ok(tab_a.run())
    assert box(tab_a, AGAIN) is not None and button(tab_a, SEND).disabled
    assert ui.store().delete(draft)
    tab_b.session_state["step"] = 2
    run_ok(tab_b.run())
    assert KNOWN_SENT in notice(tab_b)
    run_ok(button(tab_b, RECREATE, key="draft-recreate").click().run())
    assert draft in saved_ids() and ui.store().load_send_state(draft).post_id == 777
    for _ in range(2):
        run_ok(tab_a.run())
    assert notice(tab_a) == "" and box(tab_a, AGAIN) is not None
    try_send(tab_a)
    ui.to_publish(tab_b)
    assert box(tab_b, AGAIN) is not None
    try_send(tab_b)
    assert button(t86.reopen(project_root, draft), SEND).disabled
    assert site.posts() == []


# ====================================================================== 2. bỏ bài, gửi dở
def test_bo_bai_nay_khong_xoa_dong_giu_lai(project_root, root, fake_ai, site):
    """Tab A thấy nháp không còn, chọn «🗑️ Bỏ bài này» → «Bỏ hẳn»: chỉ xóa trắng trang tab A, dòng
    trạng thái gửi giữ lại vẫn còn; tab B (mở bài từ trước, chưa biết) lưu lại thì vẫn khóa."""
    tab_a, _pid = ui.ready_image(project_root)
    ui.to_publish(tab_a)
    ui.send(tab_a)
    draft = tab_a.session_state["draft_id"]
    state = ui.store().load_send_state(draft)
    tab_b = ui.pages.open_page(project_root, "write.py")
    run_ok(button(tab_b, "Mở", key=f"open-{draft}").click().run())
    assert ui.store().delete(draft)
    run_ok(tab_a.run())
    assert notice(tab_a)
    run_ok(button(tab_a, "Bỏ hẳn", key="draft-discard").click().run())
    assert "draft_id" not in tab_a.session_state and notice(tab_a) == ""
    assert ui.store().load_send_state(draft) == state  # «Bỏ hẳn» không xóa gì trong kho
    tab_b.session_state["step"] = 2
    run_ok(tab_b.run())
    run_ok(button(tab_b, RECREATE, key="draft-recreate").click().run())
    assert ui.store().load_send_state(draft) == state
    ui.to_publish(tab_b)
    assert box(tab_b, AGAIN) is not None and button(tab_b, SEND).disabled
    assert len(site.posts()) == 1


def test_gui_do_bi_xoa_tab_khong_biet_luu_lai_van_khoa_gui_do(project_root, root, fake_ai, site):
    """Nháp «gửi dở» (lần gửi chưa rõ kết quả, chưa có mã) bị xóa; tab mở bài từ trước, chưa biết,
    lưu lại: nháp có lại kèm «gửi dở», bước Xuất bản đòi tick «Tôi đã kiểm tra trang quản trị…»."""
    at, _pid = ui.open_article(project_root)
    draft = at.session_state["draft_id"]
    unsure = SendState.now(pending=True, post_id=None)
    ui.store().save_send_state(draft, unsure)
    assert ui.store().delete(draft)
    at.session_state["step"] = 1
    run_ok(at.run())
    assert KNOWN_SENT in notice(at)
    run_ok(button(at, RECREATE, key="draft-recreate").click().run())
    assert ui.store().load_send_state(draft) == unsure
    ui.to_publish(at)
    assert box(at, CHECKED) is not None and button(at, SEND).disabled
    assert site.posts() == []


# ====================================================================== 3. popover «Xóa»
def popover_warnings(at, draft: str) -> list[str]:
    for popover in at.get("popover"):
        if popover.proto.popover.label != "🗑️ Xóa":
            continue
        if any(b.key == f"del-{draft}" for b in popover.button):
            return [w.value for w in popover.warning]
    raise AssertionError(f"không thấy popover «Xóa» của nháp {draft}")


@pytest.mark.parametrize("mode", ["future", "publish"], ids=["da-hen-gio", "da-dang"])
def test_popover_bai_da_hen_gio_hay_da_dang_noi_ma_bai(project_root, mode):
    """Bài đã hẹn giờ hay đã đăng (lệnh chuyển xong): nhắc «đã gửi lên website (bài mã …)», xóa nháp
    không xóa bài trên website (không nhắc như «chưa rõ kết quả»)."""
    store = ui.store()
    snap = store.save(DraftSnapshot(keyword=f"cổng {mode}"))
    when = datetime.now(UTC) + timedelta(days=1) if mode == "future" else None
    store.save_send_state(
        snap.id,
        SendState.now(pending=False, post_id=4321, mode=mode, scheduled_for=when, released=True),
    )
    at = ui.pages.open_page(project_root, "write.py")
    (warning,) = popover_warnings(at, snap.id)
    assert "đã gửi lên website (bài mã 4321)" in warning and "**không** xóa" in warning
    assert "chưa rõ kết quả" not in warning


# ====================================================================== 4. dọn dòng mồ côi
def rows(store: DraftStore) -> list[str]:
    """Mã nháp của mọi dòng trạng thái gửi, theo thứ tự ghi (``rowid``)."""
    with closing(sqlite3.connect(store.path)) as conn:
        return [row[0] for row in conn.execute("SELECT id FROM send_states ORDER BY rowid")]


def test_kho_day_va_nhieu_dong_mo_coi_khong_dung_trang_thai_nhap_con(tmp_path):
    """Kho đầy (``max_drafts``) mọi nháp đều đã gửi, cùng nhiều dòng mồ côi hơn giới hạn: mỗi lần
    lưu, xóa chỉ dọn dòng mồ côi cũ; trạng thái gửi của mọi nháp còn trong kho nguyên vẹn; dòng mồ
    côi vừa được ghi lại (kết quả lần gửi ghi sau lúc xóa, SL-T089-2) là mới nhất nên ở lại."""
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_drafts=4, max_orphan_send_states=3)
    gone = []
    for n in range(6):  # 6 nháp đã gửi rồi bị xóa: 6 dòng mồ côi (dọn còn 3)
        snap = store.save(DraftSnapshot(keyword=f"đã xóa {n}"))
        store.save_send_state(snap.id, SendState.now(pending=False, post_id=100 + n))
        assert store.delete(snap.id)
        gone.append(snap.id)
    assert rows(store) == gone[-3:]
    live = []
    for n in range(4):  # kho đầy: 4 nháp còn, đều đã gửi
        snap = store.save(DraftSnapshot(keyword=f"còn {n}"))
        store.save_send_state(snap.id, SendState.now(pending=False, post_id=200 + n))
        live.append(snap.id)
    # Kết quả lần gửi của nháp đã xóa lâu nhất còn giữ ghi lại sau lúc xóa: thành dòng mới nhất.
    store.save_send_state(gone[3], SendState.now(pending=False, post_id=999))
    store.save(DraftSnapshot(keyword="mới"))  # kho đầy bỏ «còn 0»: trạng thái của nó thành mồ côi
    kept = rows(store)
    for draft in live[1:]:
        assert draft in kept and store.load_send_state(draft).post_id >= 200
    orphans = [draft for draft in kept if draft not in live[1:]]
    # 3 dòng mồ côi ghi gần nhất, theo thứ tự ghi: «đã xóa 5», «còn 0» (bị dọn lúc kho đầy, dòng
    # ghi trước), «đã xóa 3» (ghi lại sau cùng); «đã xóa 4» cũ nhất bị dọn.
    assert orphans == [gone[5], live[0], gone[3]]
    assert gone[4] not in kept
    assert store.load_send_state(gone[3]).post_id == 999

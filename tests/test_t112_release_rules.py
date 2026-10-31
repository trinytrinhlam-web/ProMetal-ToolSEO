"""T-112 (Họa Sĩ): chuẩn bị bật Hẹn giờ / Đăng ngay (công tắc vẫn mặc định tắt).

- Một luật chung cho SL-T102-1 và LC-T102-1 (LC-T094-38, -39): **Đăng ngay** chỉ gửi lệnh đăng khi
  ảnh đại diện (bài có ảnh) và SEO (bật «Ghi SEO lên website») đã lên website; thiếu thì bài vẫn là
  nháp, câu báo cố định nói phần nào chưa lên. **Hẹn giờ**: vẫn hẹn giờ, cảnh báo rõ (còn sửa được
  trước giờ đăng). Ca hỏng gốc: ``tests/test_la_chan_t102.py``, ``tests/test_soi_loi_t102.py``.
- Lệnh chuyển không rõ kết quả: không ghi trạng thái vào dòng kế hoạch (G1 Lá Chắn T-102).
- Ô «gửi lại» nói đúng việc sẽ làm khi đang chọn Hẹn giờ / Đăng ngay.
- Lúc bấm gửi xét lại công tắc (G2 Lá Chắn T-102).

Khung test (WordPress giả ``live``, Google Sheet giả ``plan``, công tắc bật trong test) mượn của
``tests/test_t102_publish.py``. Không gọi WordPress, Google, AI thật.
"""

from __future__ import annotations

import streamlit as st
import test_app_images as ui
import test_t102_publish as t102

from seo_app.storage.plan_cache import sheet_hash
from seo_app.text import escape_markdown
from seo_app.wordpress.client import SeoWriteResult, WordPressClient

# Fixture dùng chung (mật khẩu thử, ảnh, AI giả, WordPress giả, Google Sheet giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live
site_cache = t102.site_cache
private_key = t102.private_key
plan = t102.plan

SCHEDULE, PUBLISH = "Hẹn giờ", "Đăng ngay"
HELD = "Chưa đăng bài: "
FEATURED = "ảnh đại diện"
SEO = "SEO (tiêu đề, mô tả, từ khóa chính trong hộp SiteSEO)"


def seo_answer(monkeypatch, written: bool) -> None:
    def seo(self, post_id, **fields):
        if written:
            return SeoWriteResult(True, route="meta", message="Đã ghi SEO vào hộp SiteSEO.")
        return SeoWriteResult(False, reason="unavailable", message="SiteSEO chưa cho ghi SEO.")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)


def featured_answer(live, status: int) -> None:
    """Lệnh đặt ảnh đại diện trả ``status``; lệnh khác vào bài 501 (đăng, hẹn giờ) như site giả."""

    def post_post(request):
        body = ui.body_of(request) or {}
        if "featured_media" in body and status != 200:
            return (status, {"code": "internal_server_error", "message": t102.BAIT}, {})
        return {"id": t102.POST_ID, "status": "draft", **body}

    live.site.fake.on("POST", t102.POST, post_post)


def send(project_root, mode: str, *, seo_write: bool = False):
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, mode)
    if seo_write:
        t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    assert not t102.send_button(at).disabled
    return t102.run_ok(t102.send_button(at).click().run())


def warnings(at) -> str:
    return "\n".join(w.value for w in at.warning)


# ============================================================ Đăng ngay: luật chung


def test_publish_held_when_featured_and_seo_missing_names_both(
    project_root, root, fake_ai, live, monkeypatch
):
    """Ảnh đại diện hỏng **và** SEO không ghi được: không lệnh đăng; câu báo nêu cả hai phần, bài
    vẫn là nháp; nháp ghi «đã gửi nháp, chưa đăng» (không khóa «không rõ»), không lời lỗi gốc."""
    seo_answer(monkeypatch, written=False)
    featured_answer(live, 500)
    at = send(project_root, PUBLISH, seo_write=True)
    assert t102.release_bodies(live.site) == []
    shown = warnings(at)
    held = escape_markdown(f"{HELD}{FEATURED}, {SEO} chưa lên website lúc gửi")
    assert held in shown and f"mã {t102.POST_ID}" in shown
    assert not any(t102.BAIT in text for text in ui.texts(at))
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.mode, saved.released, saved.release_unknown, saved.pending) == (
        "publish",
        False,
        False,
        False,
    )
    t102.run_ok(at.run())
    assert any("chưa hẹn giờ/đăng" in i.value for i in at.info)
    assert not any("có thể đã" in e.value for e in at.error)


def test_publish_held_when_only_seo_missing(project_root, root, fake_ai, live, monkeypatch):
    """SEO không ghi được, ảnh đại diện đặt được: không đăng, câu báo chỉ nêu phần SEO."""
    seo_answer(monkeypatch, written=False)
    at = send(project_root, PUBLISH, seo_write=True)
    assert t102.release_bodies(live.site) == []
    shown = warnings(at)
    assert escape_markdown(f"{HELD}{SEO} chưa lên website") in shown
    assert escape_markdown(f"{HELD}{FEATURED}") not in shown


def test_publish_goes_when_everything_landed(project_root, root, fake_ai, live, monkeypatch):
    """Đối chứng: ảnh đại diện đặt được, SEO ghi được thì vẫn đăng (không chặn oan)."""
    seo_answer(monkeypatch, written=True)
    at = send(project_root, PUBLISH, seo_write=True)
    assert t102.release_bodies(live.site) == [{"status": "publish"}]
    assert any("Đã đăng bài công khai" in s.value for s in at.success)
    assert HELD not in warnings(at)


# ============================================================ Hẹn giờ: cảnh báo, người dùng quyết


def test_schedule_goes_on_but_warns_what_is_missing(project_root, root, fake_ai, live):
    """Hẹn giờ mà ảnh đại diện hỏng: vẫn hẹn giờ (còn sửa được trước giờ đăng), cảnh báo rõ phần
    chưa lên và việc cần làm trước giờ đăng."""
    featured_answer(live, 500)
    at = send(project_root, SCHEDULE)
    when = t102.tomorrow_8am_utc()
    assert t102.release_bodies(live.site) == [
        {"status": "future", "date_gmt": t102.date_gmt_text(when)}
    ]
    assert any("Đã hẹn giờ đăng bài" in s.value for s in at.success)
    assert escape_markdown(f"Bài đã hẹn giờ nhưng {FEATURED} chưa lên website") in warnings(at)


def test_schedule_without_missing_parts_has_no_extra_warning(project_root, root, fake_ai, live):
    at = send(project_root, SCHEDULE)
    assert len(t102.release_bodies(live.site)) == 1
    assert "Bài đã hẹn giờ nhưng" not in warnings(at)


# ============================================================ dòng kế hoạch (G1)


def test_unsure_release_does_not_write_plan_status(project_root, live, plan):
    """G1 Lá Chắn T-102: lệnh hẹn giờ không rõ kết quả (504): không ghi gì vào dòng kế hoạch (cả
    «Đã gửi nháp»), không để việc còn nợ; câu báo cố định."""
    live.answers = [t102.answer(504, {"code": "gateway_timeout", "message": t102.BAIT})]
    at = t102.open_snap(project_root, t102.plan_article("9" * 32))
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    t102.run_ok(t102.send_button(at).click().run())
    assert len(t102.release_bodies(live.site)) == 1
    assert plan.reads == 0 and plan.updates == []
    assert ui.store().list_plan_writes() == []
    message = escape_markdown("Chưa ghi trạng thái vào dòng kế hoạch B-001: chưa rõ bài")
    assert any(message in i.value for i in at.info)
    assert at.session_state["_plan_ref"].sheet_hash == sheet_hash(t102.SHEET_ID)


def test_held_publish_writes_draft_sent_to_plan(project_root, live, plan, monkeypatch):
    """Đăng ngay bị giữ là nháp (SEO chưa lên): dòng kế hoạch ghi đúng «Đã gửi nháp»."""
    seo_answer(monkeypatch, written=False)
    at = t102.open_snap(project_root, t102.plan_article("a" * 31 + "9"))
    t102.to_mode(at, PUBLISH)
    t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    t102.run_ok(t102.send_button(at).click().run())
    assert t102.release_bodies(live.site) == []
    assert plan.cell(2, t102.COL["status"]) == t102.plan_model.STATUS_DRAFT_SENT


# ============================================================ ô «gửi lại», công tắc lúc bấm


def test_again_box_says_what_it_will_do(project_root, root, fake_ai, live, monkeypatch):
    """Ghi nhận 2 Lá Chắn T-102: bài đã gửi, đang chọn Đăng ngay thì ô «gửi lại» nói rõ sẽ tạo bài
    mới **và đăng công khai ngay**; chọn Hẹn giờ thì nói hẹn giờ; Nháp giữ chữ cũ."""
    seo_answer(monkeypatch, written=True)
    at = send(project_root, PUBLISH, seo_write=True)
    box = at.checkbox(key="_wp_again")
    assert box.label == "Tạo thêm một bài mới và đăng công khai ngay bài mới đó"
    assert any("**đăng công khai ngay** bài đó" in i.value for i in at.info)
    t102.run_ok(at.segmented_control(key="_wp_mode").set_value(SCHEDULE).run())
    assert at.checkbox(key="_wp_again").label == "Tạo thêm một bài mới và hẹn giờ đăng bài mới đó"
    t102.run_ok(at.segmented_control(key="_wp_mode").set_value("Nháp").run())
    assert at.checkbox(key="_wp_again").label == "Tạo thêm một bài nháp mới"


def test_switch_turned_off_at_click_sends_nothing(project_root, root, fake_ai, live, monkeypatch):
    """G2 Lá Chắn T-102: công tắc bị tắt đúng lúc bấm (tab khác, Cài đặt) sau khi màn hình xác nhận
    đã hiện: ``send_draft`` xét lại công tắc, không gửi gì lên website, báo rõ."""
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    label = t102.send_button(at).label
    original = st.button

    def click_after_switch_off(text, *args, **kwargs):
        clicked = original(text, *args, **kwargs)
        if text == label:
            st.session_state[t102.SWITCH] = False  # tab khác vừa tắt công tắc
            return True
        return clicked

    monkeypatch.setattr(st, "button", click_after_switch_off)
    t102.run_ok(at.run())
    assert live.site.fake.requests == []
    assert any("Hẹn giờ và Đăng ngay đang tắt" in e.value for e in at.error)

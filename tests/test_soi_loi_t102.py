"""Soi Lỗi T-102 (rút gọn): bước Xuất bản thật (Nháp, Hẹn giờ, Đăng ngay), màn hình xác nhận.

Kiểm độc lập các đường tới ``future``/``publish``. Mượn khung trang Soạn bài và WordPress giả
(``live``: bài 501 trả header ``Date``, tài khoản có quyền đăng) của ``test_t102_publish.py``,
``test_app_images.py``, ``test_t086_send_state.py`` như các file T-086, T-089; mọi ca, mọi kiểm
là của Soi Lỗi. Không gọi WordPress, Google, AI thật.

1. Công tắc tắt (kể cả giá trị «gần đúng»): không nút gửi, không lệnh nào, không đường tới
   ``release_draft``; đọc mã nguồn: chuỗi gọi duy nhất qua ``publish_panel``.
2. Bật trong test: sửa bài rồi bấm **trong cùng một lần chạy**, hay sửa sau khi tick: không gửi.
3. Giờ: giờ hẹn đã qua trong ngày, đồng hồ website lệch: không chuyển, bài vẫn là nháp.
4. Kết quả không rõ: mở lại ở phiên mới vẫn khóa; lệnh chuyển luôn là lệnh cuối.
5. Đăng ngay mà lệnh ghi SEO hỏng lúc gửi (LC-T094-39): xem SL-T102-1.
"""

from __future__ import annotations

import ast
from datetime import UTC, datetime, time, timedelta
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import test_app_images as ui
import test_t086_send_state as t86
import test_t102_publish as t102

from seo_app.wordpress.client import SeoWriteResult, WordPressClient, WordPressError

# Khung dùng chung (mật khẩu thử, cache ảnh xem trước, AI giả, thư mục ảnh, WordPress giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live

WRITE = Path(__file__).resolve().parents[1] / "app" / "views" / "write.py"
SCHEDULE, PUBLISH = "Hẹn giờ", "Đăng ngay"


def spy_release(monkeypatch) -> list[tuple]:
    """Ghi lại mọi lần gọi ``release_draft`` (vẫn chạy bản thật)."""
    calls: list[tuple] = []
    original = WordPressClient.release_draft

    def release(self, post_id, **kwargs):
        calls.append((post_id, kwargs.get("mode")))
        return original(self, post_id, **kwargs)

    monkeypatch.setattr(WordPressClient, "release_draft", release)
    return calls


def writes(site) -> list[tuple[str, str]]:
    return [(r.method, ui.path_of(r)) for r in site.fake.requests if r.method != "GET"]


# ================================================================ 1. công tắc tắt
@pytest.mark.parametrize("value", [1, "True", [True]], ids=["so-1", "chu-True", "danh-sach"])
@pytest.mark.parametrize("mode", [SCHEDULE, PUBLISH])
def test_cong_tac_chi_bat_khi_dung_true(project_root, root, fake_ai, live, monkeypatch, value,
                                        mode):
    calls = spy_release(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    at.session_state[t102.SWITCH] = value  # giá trị «gần đúng» không bật được công tắc
    t102.to_mode(at, mode, switch=False)
    assert not any(b.key == "wp-send" for b in at.button)
    assert any("đang **tắt**" in i.value for i in at.info)
    assert calls == [] and live.site.fake.requests == []


def _callers(tree: ast.AST, name: str) -> set[str]:
    found = set()
    for function in ast.walk(tree):
        if isinstance(function, ast.FunctionDef):
            for node in ast.walk(function):
                if isinstance(node, ast.Call):
                    target = node.func
                    called = target.attr if isinstance(target, ast.Attribute) else getattr(
                        target, "id", None)
                    if called == name:
                        found.add(function.name)
    return found


def test_duong_duy_nhat_toi_release_draft_di_qua_cong_tac():
    tree = ast.parse(WRITE.read_text(encoding="utf-8"))
    assert _callers(tree, "release_draft") == {"release_post"}
    assert _callers(tree, "release_post") == {"send_and_record"}
    assert _callers(tree, "send_and_record") == {"send_draft"}
    assert _callers(tree, "send_draft") == {"publish_panel"}
    assert _callers(tree, "create_draft_with_images") == {"send_and_record"}
    assert _callers(tree, "create_draft") == set()
    panel = next(n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == "publish_panel")
    lines = {
        name: min(node.lineno for node in ast.walk(panel) if isinstance(node, ast.Call)
                  and getattr(node.func, "id", getattr(node.func, "attr", None)) == name)
        for name in ("release_enabled", "send_draft", "wordpress_client")
    }
    # Công tắc xét trước cả việc tạo client, trước lệnh gửi.
    assert lines["release_enabled"] < lines["wordpress_client"] < lines["send_draft"]
    source = WRITE.read_text(encoding="utf-8")
    assert "paragraphs_to_html" not in source  # không còn đường ghép HTML cũ


# ================================================================ 2. mã băm xác nhận
def _change(at, what: str) -> None:
    if what == "tieu-de":
        at.session_state["article_title"] = "Tiêu đề khác hẳn bài đã xem"
    elif what == "slug":
        at.session_state["seo_slug"] = "duong-dan-khac"
    else:
        first = at.session_state["part_ids"][0]
        at.session_state[f"texts-{first}"] = ["Đoạn đã sửa sau khi xem."]
        at.session_state[f"ver-{first}"] = 0


@pytest.mark.parametrize("what", ["tieu-de", "slug", "chu-bai"])
def test_sua_roi_bam_trong_cung_lan_chay_khong_gui(project_root, root, fake_ai, live, monkeypatch,
                                                   what):
    """Đổi bài và bấm gửi tới trong **cùng** một lần chạy (ô chữ mất tiêu điểm đúng lúc bấm):
    mã băm lúc tick khác bài đang có: bỏ tick, không lệnh ghi nào, không ``release_draft``."""
    calls = spy_release(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    assert not t102.send_button(at).disabled
    _change(at, what)
    ui.run_ok(t102.send_button(at).click().run())
    assert calls == [] and writes(live.site) == []
    assert at.session_state["_wp_confirm"] is False
    assert t102.send_button(at).disabled


@pytest.mark.parametrize("what", ["tieu-de", "slug"])
def test_sua_sau_khi_tick_thi_bo_tick(project_root, root, fake_ai, live, monkeypatch, what):
    calls = spy_release(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, PUBLISH)
    ui.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    _change(at, what)
    ui.run_ok(at.run())
    assert at.session_state["_wp_confirm"] is False and t102.send_button(at).disabled
    assert any("bỏ tick" in w.value for w in at.warning)
    assert calls == [] and writes(live.site) == []


# ================================================================ 3. giờ
def test_gio_hen_da_qua_trong_ngay_bi_chan(project_root, root, fake_ai, live, monkeypatch):
    calls = spy_release(monkeypatch)
    now = datetime.now(ZoneInfo(t102.TIMEZONE))
    if now.hour == 0 and now.minute < 5:
        pytest.skip("sát nửa đêm: không còn giờ nào đã qua trong ngày")
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    at.session_state["_wp_day"] = now.date()
    at.session_state["_wp_time"] = time(max(now.hour - 1, 0), 0)
    ui.run_ok(at.run())
    t102.confirm(at)
    assert t102.send_button(at).disabled
    assert any("đã qua" in e.value for e in at.error)
    assert calls == [] and writes(live.site) == []


def test_dong_ho_website_lech_thi_khong_chuyen_bai_van_la_nhap(project_root, root, fake_ai, live):
    skewed = format_datetime(datetime.now(UTC) + timedelta(minutes=5), usegmt=True)
    draft = {"id": t102.POST_ID, "status": "draft", "modified_gmt": ui.MODIFIED}  # T-115
    live.site.fake.on("GET", t102.POST, lambda _r: (200, draft, {"Date": skewed}))
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    ui.run_ok(t102.send_button(at).click().run())
    assert t102.release_bodies(live.site) == []  # chặn trước lệnh chuyển
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.released, saved.release_unknown, saved.pending) == (False, False, False)
    assert saved.post_id == t102.POST_ID
    shown = "\n".join(e.value for e in at.error) + "\n".join(w.value for w in at.warning)
    assert "lệch giờ website" in shown
    ui.run_ok(at.run())
    assert t102.send_button(at).disabled  # bài nháp đã có: gửi lại phải xác nhận bài mới
    assert t102.release_bodies(live.site) == []


# ================================================================ 4. không rõ kết quả, thứ tự
def test_khong_ro_ket_qua_mo_lai_o_phien_moi_van_khoa(project_root, root, fake_ai, live):
    live.answers = [t102.answer(504, {"code": "gateway_timeout", "message": t102.BAIT})]
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    ui.run_ok(t102.send_button(at).click().run())
    fresh = t86.reopen(project_root, t86.draft_id(at))
    assert t102.send_button(fresh).disabled
    assert any("có thể đã" in e.value for e in fresh.error)
    assert not any(t102.BAIT in text for text in ui.texts(fresh))
    assert len(t102.release_bodies(live.site)) == 1


def test_lenh_chuyen_la_lenh_cuoi_sau_moi_lenh_anh(project_root, root, fake_ai, live):
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, SCHEDULE)
    t102.confirm(at)
    ui.run_ok(t102.send_button(at).click().run())
    requests = live.site.fake.requests
    release = [i for i, r in enumerate(requests)
               if (r.method, ui.path_of(r)) == ("POST", t102.POST)
               and "status" in (ui.body_of(r) or {})]
    assert release == [len(requests) - 1]  # đúng một lệnh chuyển, là lệnh cuối
    media = [i for i, r in enumerate(requests) if ui.path_of(r).startswith(t102.MEDIA)]
    assert media and max(media) < release[0]  # tải ảnh, ghi alt (và gắn ảnh nếu có) đều trước


# ================================================================ 5. SL-T102-1
@pytest.mark.xfail(
    strict=True,
    reason="SL-T102-1: Đăng ngay mà lệnh ghi SEO hỏng lúc gửi vẫn đăng công khai (LC-T094-39)",
)
@pytest.mark.parametrize("failure", ["loi-500", "khong-ghi-duoc", "chua-bat-abilities"])
def test_sl_t102_1_dang_ngay_ma_seo_ghi_hong_thi_khong_dang(project_root, root, fake_ai, live,
                                                           monkeypatch, failure):
    """LC-T094-39: «Đăng ngay khi SEO chưa ghi lên website → Chặn». Bộ dựng chỉ xét công tắc
    «Ghi SEO lên website» (ý định); lúc gửi, lệnh ghi SEO hỏng (5xx, website từ chối, SiteSEO
    chưa cho ghi) thì ``release_post`` vẫn đăng: bài lên công khai với SEO mặc định."""
    def seo(self, post_id, **fields):
        if failure == "loi-500":
            raise WordPressError("Máy chủ WordPress đang gặp lỗi (mã 500). Thử lại sau.",
                                 status_code=500)
        if failure == "khong-ghi-duoc":
            return SeoWriteResult(False, route="abilities", reason="error",
                                  message="Ghi SEO lỗi (mã 500).", status_code=500)
        return SeoWriteResult(False, reason="unavailable", message="SiteSEO chưa cho ghi SEO.")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, PUBLISH)
    ui.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    ui.run_ok(t102.send_button(at).click().run())
    assert t102.release_bodies(live.site) == []

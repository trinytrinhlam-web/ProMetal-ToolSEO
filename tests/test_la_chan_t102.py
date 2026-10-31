"""Lá Chắn T-102 (đầy đủ): bước Xuất bản thật (Nháp, Hẹn giờ, Đăng ngay).

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T102-1** (Thấp, cùng loại SL-T102-1 của Soi Lỗi): «Đăng ngay» mà lệnh đặt ảnh đại diện hỏng
  lúc gửi (website lỗi 500…) thì ``release_post`` vẫn gửi lệnh đăng: bài lên công khai **không có
  ảnh đại diện** người dùng đã thấy và tick xác nhận (ảnh đại diện nằm trong mã băm, LC-T094-8).
  LC-T094-38: ``release_draft`` chỉ sau khi tải ảnh, tạo nháp, **ảnh đại diện**, ghi SEO đã xong
  trong cùng lần bấm. Chỉ gặp khi bật công tắc Hẹn giờ/Đăng ngay. Cách sửa gợi ý (chung với
  SL-T102-1): với Đăng ngay, chỉ gọi ``release_draft`` khi mọi phần đã xác nhận đã lên website (ảnh
  đại diện đặt được, SEO ghi được); thiếu thì bài vẫn là nháp, nháp ghi «đã gửi nháp» (không khóa),
  câu báo nói rõ chưa đăng vì sao. Hẹn giờ: Cảnh báo như thiết kế (còn sửa được trước giờ đăng).

Khung test (trang Soạn bài, WordPress giả ``live``, công tắc bật trong test) mượn của
``tests/test_t102_publish.py`` (Họa Sĩ). Không gọi WordPress, Google, AI thật.
"""

from __future__ import annotations

import test_app_images as ui
import test_t102_publish as t102

from seo_app.wordpress.client import SeoWriteResult, WordPressClient

# Fixture dùng chung (mật khẩu thử, ảnh, AI giả, WordPress giả, Hẹn giờ/Đăng ngay).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live


def _seo_written(monkeypatch) -> None:
    def seo(self, post_id, **fields):
        return SeoWriteResult(True, route="meta", message="Đã ghi SEO vào hộp SiteSEO.")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)


def _featured_answer(live, status: int) -> None:
    """Lệnh đặt ảnh đại diện (``POST`` bài 501 có ``featured_media``) trả ``status``; lệnh khác
    vào bài 501 (đăng, ghi meta) trả như site giả ``live``."""

    def post_post(request):
        body = ui.body_of(request) or {}
        if "featured_media" in body and status != 200:
            return (status, {"code": "internal_server_error", "message": "MỒI"}, {})
        return {"id": t102.POST_ID, "status": "draft", **body}

    live.site.fake.on("POST", t102.POST, post_post)


def _publish_now(project_root):
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, "Đăng ngay")
    t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    assert not t102.send_button(at).disabled
    return t102.run_ok(t102.send_button(at).click().run())


def test_lc_t102_1_dang_ngay_ma_anh_dai_dien_hong_thi_khong_dang(
    project_root, root, fake_ai, live, monkeypatch
):
    _seo_written(monkeypatch)
    _featured_answer(live, 500)
    _publish_now(project_root)
    assert t102.release_bodies(live.site) == []


def test_lc_t102_1_tien_de_anh_dai_dien_hong_van_bao(
    project_root, root, fake_ai, live, monkeypatch
):
    """Tiền đề của ca xfail (đúng cả trước và sau khi sửa): lệnh đặt ảnh đại diện có đi và hỏng,
    bài nháp vẫn tạo, trang báo «chưa đặt được ảnh đại diện»."""
    _seo_written(monkeypatch)
    _featured_answer(live, 500)
    at = _publish_now(project_root)
    featured = [
        r
        for r in live.site.fake.requests
        if (r.method, ui.path_of(r)) == ("POST", t102.POST)
        and "featured_media" in (ui.body_of(r) or {})
    ]
    assert len(featured) == 1
    assert any("chưa đặt được ảnh đại diện" in w.value for w in at.warning)


def test_lc_t102_1_doi_chung_anh_dai_dien_dat_duoc_thi_dang(
    project_root, root, fake_ai, live, monkeypatch
):
    """Cách sửa không được chặn oan: ảnh đại diện đặt được, SEO ghi được thì vẫn đăng."""
    _seo_written(monkeypatch)
    _featured_answer(live, 200)
    at = _publish_now(project_root)
    assert t102.release_bodies(live.site) == [{"status": "publish"}]
    assert any("Đã đăng bài công khai" in s.value for s in at.success)

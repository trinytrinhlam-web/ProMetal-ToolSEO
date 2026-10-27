"""Lá Chắn T-041 (rút gọn, cả phiếu): test chứng minh lỗi tìm thấy và quyết định SL-T041-8.

- LC-T041-1 (Thấp, ``xfail(strict=True)`` tới khi sửa): khung «Xem trước trên Google» ở bước SEO
  lấy tên miền bằng ``urlsplit(WORDPRESS_URL).netloc``, nên ``WORDPRESS_URL`` khai sai kiểu
  ``https://tên:mật-khẩu@site`` thì tên đăng nhập và mật khẩu hiện lên màn hình (security.md 2.1).
  Client WordPress từ chối địa chỉ này (``_is_plain_site_url``) và mọi câu lỗi của nó không chép địa
  chỉ (LC-T042-4), chỉ chỗ xem trước này đọc thẳng cấu hình.
- SL-T041-8 (Soi Lỗi; Lá Chắn quyết **giữ Chặn**): ký tự «chưa gán» (Cn) với Python 3.12, gồm emoji
  Unicode 16, vẫn bị Chặn như điều kiện LC-T036-1, vì ``normalize_meta`` và client WordPress bỏ hẳn
  ký tự này: cho qua bộ kiểm mà không đổi hai chỗ kia là quay lại lỗi «lặng lẽ bỏ ký tự rồi ghi»
  (T-041 lượt 3). Chỉ sửa câu báo cho đúng (emoji nhìn thấy được, không phải «không nhìn thấy»).

AI giả, WordPress chưa khai báo (không gọi mạng); dùng chung fixture của
``tests/test_t041_seo_ui.py``.
"""

from __future__ import annotations

import unicodedata

import pytest
import test_t041_seo_ui as seo_ui

from seo_app.onpage.meta import Level, check_description, check_title, normalize_meta
from seo_app.wordpress.client import WordPressError, _seo_text

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm, cache danh sách bài tạm, AI giả.
env = seo_ui.env
previews = seo_ui.previews
site_cache = seo_ui.site_cache
seo_ai = seo_ui.seo_ai

FAKE_USER = "ten-dang-nhap-gia"
FAKE_SECRET = "MAT-KHAU-GIA-T041"  # chuỗi mồi, không phải mật khẩu thật

# Ký tự Cn với Python 3.12 (bảng Unicode 15.0): emoji Unicode 16 (U+1FAE9 mặt có bọng mắt, U+1FAC6
# dấu vân tay), ký tự «không phải ký tự» U+FDD0, ký tự chưa gán U+0378. Kèm Co (U+E000), Cc (ESC).
ODD = [chr(0x1FAE9), chr(0x1FAC6), chr(0xFDD0), chr(0x0378), chr(0xE000), chr(0x1B)]
NEW_EMOJI = [chr(0x1FAE9), chr(0x1FAC6)]


def serp_blocks(at) -> list[str]:
    return [block for block in seo_ui.html_blocks(at) if 'class="serp"' in block]


# ============================================================ LC-T041-1


def test_lc1_serp_preview_never_shows_credentials_of_wordpress_url(
    project_root, seo_ai, monkeypatch
):
    monkeypatch.setenv("WORDPRESS_URL", f"https://{FAKE_USER}:{FAKE_SECRET}@suachuacuasat.com")
    at = seo_ui.to_seo(project_root)
    blocks = serp_blocks(at)
    assert blocks  # khung xem trước có trên trang
    shown = "\n".join(blocks)
    assert FAKE_SECRET not in shown
    assert FAKE_USER not in shown


def test_serp_preview_shows_plain_host(project_root, seo_ai, monkeypatch):
    """Canh: địa chỉ đúng dạng thì khung xem trước vẫn hiện tên miền (cách sửa LC-T041-1 không
    được làm mất tên miền)."""
    monkeypatch.setenv("WORDPRESS_URL", "https://suachuacuasat.com")
    at = seo_ui.to_seo(project_root)
    assert any("suachuacuasat.com" in block for block in serp_blocks(at))


# ============================================================ SL-T041-8: quyết định giữ Chặn


@pytest.mark.parametrize("ch", ODD, ids=[f"U+{ord(c):04X}" for c in ODD])
def test_odd_char_is_never_judged_good_then_silently_dropped(ch):
    """Canh quyết định SL-T041-8: chữ có ký tự lạ (kể cả emoji mới mà Python 3.12 coi là Cn) mà bộ
    kiểm cho qua thì chữ đó phải còn nguyên ký tự ấy trong chữ sẽ ghi (``normalize_meta``) và client
    WordPress ghi được nguyên văn. Hôm nay: bộ kiểm Chặn. Ai nới bộ kiểm mà không sửa cả hai chỗ kia
    thì test này hỏng (quay lại lỗi «lặng lẽ bỏ ký tự rồi ghi»)."""
    title = f"Sửa cửa sắt bị xệ {ch} tự kiểm tra tại nhà"
    description = (
        f"Cửa sắt bị xệ {ch} cạ nền khi đóng mở thường do bản lề mòn. Xem cách tự kiểm tra bản lề, "
        "lúc nào chỉnh được và lúc nào nên gọi thợ hàn lại."
    )
    for check in (check_title(title, ""), check_description(description)):
        if check.level is Level.BLOCK:
            continue
        assert ch in normalize_meta(check.value)
        try:
            sent = _seo_text("Meta", check.value, 10_000)
        except WordPressError:
            continue  # client từ chối: không ghi gì, không lặng lẽ sửa
        assert ch in sent


@pytest.mark.skipif(
    any(unicodedata.category(c) != "Cn" for c in NEW_EMOJI),
    reason="Python này đã biết emoji Unicode 16 (không còn là ký tự chưa gán)",
)
@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-8 (Lá Chắn quyết giữ Chặn): câu báo emoji mới nói «không nhìn thấy»",
)
@pytest.mark.parametrize("emoji", NEW_EMOJI, ids=[f"U+{ord(c):04X}" for c in NEW_EMOJI])
def test_sl8_new_emoji_stays_blocked_with_accurate_message(emoji):
    """Cách sửa SL-T041-8 theo quyết định Lá Chắn: vẫn Chặn, câu báo không được nói ký tự «không
    nhìn thấy» (emoji nhìn thấy rõ); câu nói phần mềm chưa nhận ra ký tự đó."""
    check = check_title(f"Cửa sắt bị xệ {emoji} tự kiểm tra hay nên gọi thợ?", "")
    assert check.level is Level.BLOCK
    message = " ".join(check.messages)
    assert "không nhìn thấy" not in message
    assert "chưa nhận ra" in message

"""Lá Chắn T-085: phần còn lại của SL-T085-2 ở đường câu trả lời LỖI.

``xfail(strict=True)`` là lỗi trong ``docs/team/reports/T-085-la-chan.md``: sửa xong thì test
thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.

- LC-T085-1 (cùng gốc SL-T085-2): ``_error_from`` đọc thân câu trả lời 4xx/5xx bằng
  ``response.json()`` và chỉ bắt ``ValueError``. Thân JSON lồng quá sâu làm lọt
  ``RecursionError`` (lỗi Python, không phải ``WordPressError``) ở MỌI lệnh, kể cả lệnh ghi đè ba
  ô của ``upload_media`` (ảnh đã lên mà câu «thư viện Media» không hiện). Test của Soi Lỗi
  (``tests/test_soi_loi_t085.py``) chỉ thử câu trả lời ``200`` đi qua ``_json``; sửa riêng
  ``_json`` thì test này vẫn hỏng.

Đối chứng (đang qua): thân lỗi JSON thường vẫn ra câu cố định kèm mã HTTP. Chỉ dùng site giả
(``FakeWordPress``), không gọi mạng.
"""

from __future__ import annotations

import pytest
from fake_wordpress import BASE_URL

from seo_app.wordpress import WordPressError

MEDIA = "/wp-json/wp/v2/media"
SOURCE_URL = f"{BASE_URL}/wp-content/uploads/2026/10/cong-inox.jpg"
JPEG = b"\xff\xd8\xff\xe0anh-gia"
DEEP_JSON = b"[" * 100_000 + b"]" * 100_000


@pytest.mark.xfail(
    strict=True,
    reason="LC-T085-1: câu trả lời lỗi (4xx/5xx) có thân JSON lồng quá sâu làm _error_from để lọt "
    "RecursionError thay vì WordPressError câu cố định",
)
@pytest.mark.parametrize("status", [400, 404, 500])
def test_lc_t085_1_tra_loi_loi_long_qua_sau_thanh_cau_co_dinh(fake_wp, wp_client, status):
    fake_wp.on("GET", "/wp-json/", (status, DEEP_JSON, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    assert f"mã {status}" in str(err.value)


@pytest.mark.xfail(
    strict=True,
    reason="LC-T085-1: lệnh ghi đè ba ô của upload_media trả lỗi có thân JSON lồng quá sâu: "
    "RecursionError lọt ra, không có câu «thư viện Media» dù ảnh đã lên",
)
def test_lc_t085_1_ghi_de_loi_long_qua_sau_van_bao_anh_da_o_thu_vien(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": 9, "source_url": SOURCE_URL}, {}))
    fake_wp.on("POST", f"{MEDIA}/9", (500, DEEP_JSON, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.upload_media(JPEG, "cong-inox.jpg", alt_text="Cổng inox")
    assert "thư viện Media" in str(err.value)
    assert "mã ảnh 9" in str(err.value)


@pytest.mark.parametrize("status", [400, 404, 500])
def test_lc_t085_1_doi_chung_than_loi_thuong_van_ra_cau_co_dinh(fake_wp, wp_client, status):
    fake_wp.on("GET", "/wp-json/", (status, {"code": "rest_no_route", "message": "x"}, {}))
    with pytest.raises(WordPressError) as err:
        wp_client.check_connection()
    assert f"mã {status}" in str(err.value)

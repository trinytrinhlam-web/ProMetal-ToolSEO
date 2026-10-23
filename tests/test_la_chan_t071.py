"""Lá Chắn T-071 (rút gọn): phần còn lại của LC-T054-5 ở ``upload_media``.

T-071 cho phần gửi nháp kèm ảnh chỉ nhận ``201 Created`` khi tải ảnh
(``_post_media(new_only=True)``): mã khác có thể là một ảnh **đã có** trên website (plugin
trả lại ảnh trùng byte), ghi alt vào mã đó là sửa ảnh có sẵn (R3). Phiếu chỉ được sửa phần
gửi nháp, nên ``upload_media`` (trang Kết nối WordPress, ``app/views/wordpress.py``) vẫn nhận
mọi mã 2xx rồi ghi alt, tiêu đề, chú thích vào mã website trả. Ghi là LC-T071-1 (xem
``docs/team/reports/T-071-la-chan.md``), đánh dấu ``xfail(strict=True)``: sửa xong thì test
tự báo XPASS để gỡ dấu.

Đối chứng (đang qua): website trả ``201`` thì ``upload_media`` vẫn tải và ghi alt như cũ, để
cách sửa không chặn nhầm lần tải bình thường. Chỉ dùng site giả (``FakeWordPress``), không
gọi mạng.
"""

from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL

from seo_app.wordpress import WordPressError

MEDIA = "/wp-json/wp/v2/media"
SOURCE_URL = f"{BASE_URL}/wp-content/uploads/2026/10/cong-inox.jpg"
EXISTING_ID = 7  # ảnh "đã có sẵn" trên website
NEW_ID = 101
JPEG = b"\xff\xd8\xff\xe0anh-gia"


def _writes(fake_wp, media_id):
    return [r for r in fake_wp.requests if urlsplit(r.url).path == f"{MEDIA}/{media_id}"]


@pytest.mark.parametrize("status", [200, 202])
def test_lc_t071_1_upload_media_khong_ghi_vao_anh_website_khong_xac_nhan_vua_tao(
    fake_wp, wp_client, status
):
    fake_wp.on("POST", MEDIA, (status, {"id": EXISTING_ID, "source_url": SOURCE_URL}, {}))
    fake_wp.on(
        "POST",
        f"{MEDIA}/{EXISTING_ID}",
        {"id": EXISTING_ID, "source_url": SOURCE_URL, "alt_text": "Alt mới"},
    )

    with pytest.raises(WordPressError):
        wp_client.upload_media(
            JPEG, "cong-inox.jpg", alt_text="Alt mới", title="Tiêu đề mới", caption="Chú thích"
        )
    assert _writes(fake_wp, EXISTING_ID) == []


def test_lc_t071_1_doi_chung_upload_media_201_van_tai_va_ghi_alt(fake_wp, wp_client):
    fake_wp.on("POST", MEDIA, (201, {"id": NEW_ID, "source_url": SOURCE_URL}, {}))
    fake_wp.on(
        "POST", f"{MEDIA}/{NEW_ID}", {"id": NEW_ID, "source_url": SOURCE_URL, "alt_text": "Alt mới"}
    )

    media = wp_client.upload_media(JPEG, "cong-inox.jpg", alt_text="Alt mới")

    assert media.id == NEW_ID
    assert media.alt_text == "Alt mới"
    assert len(_writes(fake_wp, NEW_ID)) == 1

"""Lá Chắn T-110 (rút gọn): gắn ảnh «Gửi nháp» vào bài nháp vừa tạo (khóa ``post``).

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T110-1** (Thấp, = G1 của Soi Lỗi): lệnh gắn ảnh tin mã ``201 Created`` của lệnh tải. Website
  (plugin chống trùng ảnh…) trả ``201`` kèm mã một ảnh **có sẵn** đang thuộc bài khác thì client
  coi là ảnh mình vừa tải và gửi ``{"post": <mã nháp>}`` vào ảnh đó: ảnh có sẵn bị chuyển khỏi
  bài cũ sang bài nháp (trái W2: không sửa dữ liệu đã có trên website). Trước T-110, cùng điều
  kiện đó đã làm ghi đè alt, tiêu đề (LC-T071-1 chặn được mã khác ``201``, không chặn được
  ``201`` sai); T-110 thêm việc đổi bài cha. Cách sửa gợi ý: xin thêm ``post`` ở lệnh tải ảnh
  (``_fields``), chỉ coi là ảnh của client khi ``post`` trống (ảnh mới tải qua REST chưa có bài
  cha), không thì không gắn.

Không gọi WordPress thật: site giả của Soi Lỗi T-054 (bộ chặn mạng của ``tests/conftest.py`` bật).
"""

from __future__ import annotations

import contextlib

import pytest
import test_soi_loi_t054 as sl54

from seo_app.images.process import make_web_image
from seo_app.images.tags import ImageTags
from seo_app.wordpress.client import DraftImage, DraftImagesError

MEDIA = sl54.MEDIA
UPLOADS = sl54.UPLOADS


def _image(alt: str) -> DraftImage:
    web = make_web_image(sl54._jpeg(gps=sl54.GPS_NE))
    return DraftImage(web, alt=alt, tags=ImageTags(category="Cổng inox", area="Tân Phú"))


def _send(client):
    return client.create_draft_with_images("Sửa cổng inox", ["<p>Cổng.</p>", _image("Cổng mới")])


class _ExistingMediaSite(sl54.Site):
    """Lệnh tải ảnh trả mã ảnh **có sẵn** 9 (bài cha 7, bài đã đăng) với ``status`` cho trước.

    Câu trả lời mang cả bản ghi của ảnh 9 (``post`` = 7) như plugin trả lại ảnh trùng; lệnh sửa ảnh
    9 cập nhật bản ghi đó.
    """

    def __init__(self, fake_wp, status: int) -> None:
        super().__init__(fake_wp)
        self.existing = {"id": 9, "post": 7, "alt_text": "Alt cũ", "source_url": f"{UPLOADS}cu.jpg"}
        self.status = status
        fake_wp.on("POST", MEDIA, self.create_existing)
        fake_wp.on("POST", f"{MEDIA}/9", self.update_existing)

    def create_existing(self, _request):
        return (self.status, dict(self.existing), {})

    def update_existing(self, request):
        self.existing.update(sl54.body(request) or {})
        return dict(self.existing)


def _writes_to_9(fake_wp) -> list[dict]:
    target = f"{MEDIA}/9"
    return [sl54.body(r) for r in fake_wp.requests if r.method == "POST" and sl54.path(r) == target]


def test_lc_t110_1_anh_co_san_site_tra_201_khong_bi_chuyen_bai_cha(fake_wp, wp_client):
    site = _ExistingMediaSite(fake_wp, status=201)
    with contextlib.suppress(DraftImagesError):  # cách sửa từ chối ảnh ngay lúc tải cũng được
        _send(wp_client)
    assert {"post": 42} not in _writes_to_9(fake_wp)
    assert site.existing["post"] == 7


def test_lc_t110_1_doi_chung_anh_moi_chua_co_bai_cha_van_gan_vao_nhap(fake_wp, wp_client):
    """Cách sửa không được làm mất điều này: ảnh mới tải (``post`` trống, như WordPress lõi trả)
    vẫn gắn vào bài nháp."""
    site = sl54.Site(fake_wp)
    create = site.create_media

    def create_with_parent_field(request):
        status, data, headers = create(request)
        return (status, {**data, "post": None}, headers)

    fake_wp.on("POST", MEDIA, create_with_parent_field)
    result = _send(wp_client)
    assert result.unattached == ()
    attach = [
        sl54.body(r)
        for r in fake_wp.requests
        if r.method == "POST" and sl54.path(r) == f"{MEDIA}/101" and "post" in (sl54.body(r) or {})
    ]
    assert attach == [{"post": 42}]


def test_lc_t110_1_doi_chung_anh_co_san_tra_200_khong_bi_dung(fake_wp, wp_client):
    """LC-T071-1 giữ: site trả mã khác 201 (ảnh có sẵn) thì không ghi gì vào ảnh đó."""
    site = _ExistingMediaSite(fake_wp, status=200)
    with pytest.raises(DraftImagesError):
        _send(wp_client)
    assert _writes_to_9(fake_wp) == []
    assert site.existing["post"] == 7 and site.existing["alt_text"] == "Alt cũ"

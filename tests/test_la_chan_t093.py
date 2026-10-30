"""Lá Chắn T-093: rà soát toàn bộ Giai đoạn 3 (ảnh) trước khi đóng giai đoạn.

Lỗi tìm được ở chỗ nối giữa các phiếu (``docs/team/reports/T-093-la-chan.md``), đánh dấu
``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu. Không gọi mạng thật (WordPress
giả của ``tests/fake_wordpress.py``, client và trang được thay hàm).

- **LC-T093-1** (Trung bình): trang Kết nối WordPress, mục «Tạo thử một bài nháp», tải **nguyên
  file** người dùng chọn lên thư viện Media (``upload_media(image.getvalue(), image.name)``). Đường
  này không qua đường ảnh của Giai đoạn 3 (``make_web_image``), nên số seri máy, tên chủ máy,
  MakerNote, XMP, chú thích, IPTC, ảnh nhỏ IFD1 trong file đều lên website, công khai ngay: trái
  quyết định 2A. Trang và README chỉ nói «khách không thấy bài», không nhắc ảnh (kể cả GPS) xem
  được công khai ngay khi tải. Phần còn lại của T-001 #3 (kiểm định dạng thật, giới hạn cỡ) đã dời
  sang Giai đoạn 3 nhưng chưa làm cho chính đường này.
- **LC-T093-2** (Thấp): ảnh «Gửi nháp» tải lên không được gắn vào bài nháp vừa tạo (không gửi
  ``post``). WordPress coi ảnh không có bài cha là công khai (``check_read_permission``: trạng
  thái ``inherit`` không có bài cha thì đọc được), nên ``GET /wp-json/wp/v2/media`` không cần đăng
  nhập liệt kê được mọi ảnh app đã tải (đường dẫn file còn GPS), kể cả của bài chưa đăng.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
import streamlit as st
import test_app_wordpress as wp_page
import test_images_process as tp
import test_soi_loi_t054 as sl54

from seo_app.images.process import make_web_image
from seo_app.images.tags import ImageTags
from seo_app.wordpress import Media, Post, WordPressClient
from seo_app.wordpress.client import DraftImage

# Mật khẩu thử, WordPress khai báo sẵn cho trang Kết nối WordPress (như test của trang đó).
env = wp_page.env

# Dấu của mọi loại metadata quyết định 2A bỏ (GPS thì giữ, không xét ở đây).
JPEG_MARKERS = tuple(marker for marker in tp.BI_MAT if not marker.startswith(b"PNG-"))


class _ChosenFile:
    """Như ``UploadedFile`` của Streamlit: tên file gốc trên máy người dùng và byte của file."""

    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


@pytest.mark.xfail(
    strict=True,
    reason="LC-T093-1: trang Kết nối WordPress tải nguyên file ảnh, bỏ qua quyết định 2A",
)
def test_lc_t093_1_wordpress_page_upload_follows_decision_2a(project_root, monkeypatch):
    """Mong đợi: ảnh từ trang Kết nối WordPress lên website cũng theo quyết định 2A như ảnh của
    «Gửi nháp» (không số seri, tên chủ máy, MakerNote, XMP, chú thích, IPTC, ảnh nhỏ IFD1), hoặc
    trang không còn tải ảnh. Thực tế: ``upload_media`` nhận đúng byte người dùng chọn."""
    original = tp._jpeg_day_du()
    assert len([marker for marker in JPEG_MARKERS if marker in original]) >= 10  # tiền đề
    asked, uploaded = [], []

    def file_uploader(*_args, **_kwargs):
        asked.append(True)
        return _ChosenFile("IMG_0001 nha khach.jpg", original)

    def upload_media(self, data, filename, **_kwargs):
        uploaded.append(data)
        return Media(9, "https://example.com/wp-content/uploads/2026/10/anh-thu.jpg")

    def create_draft(self, title, content, **_kwargs):
        return Post(42, "draft", title, "", self.edit_link(42))

    monkeypatch.setattr(st, "file_uploader", file_uploader)
    monkeypatch.setattr(WordPressClient, "upload_media", upload_media)
    monkeypatch.setattr(WordPressClient, "create_draft", create_draft)
    at = wp_page.open_wordpress_page(project_root)
    buttons = [b for b in at.button if b.label == "Tạo bài nháp"]
    if not buttons:  # trang bỏ hẳn mục tạo bài thử: không còn đường tải ảnh này
        assert not asked
        return
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    at.text_area[0].input("Đoạn thử.")
    buttons[0].click().run()
    assert not at.exception
    for data in uploaded:
        assert [marker for marker in JPEG_MARKERS if marker in data] == []


class _ParentSite(sl54.Site):
    """Site giả của Soi Lỗi T-054, nhớ thêm bài cha (``post``) của từng ảnh như WordPress: gắn
    lúc tải (``POST /wp/v2/media?post=…``) hay ghi sau (``POST /wp/v2/media/<mã>`` có ``post``)."""

    def __init__(self, fake_wp) -> None:
        self.parents: dict[int, object] = {}
        super().__init__(fake_wp)

    def create_media(self, request):
        status, data, headers = super().create_media(request)
        post = parse_qs(urlsplit(request.url).query).get("post")
        if post:
            self.parents[data["id"]] = int(post[0])
        return status, data, headers

    def update_media(self, request):
        answer = super().update_media(request)
        post = (sl54.body(request) or {}).get("post")
        if post is not None:
            self.parents[int(sl54.path(request).rsplit("/", 1)[1])] = post
        return answer


@pytest.mark.xfail(
    strict=True,
    reason="LC-T093-2: ảnh gửi nháp không gắn vào bài nháp, REST liệt kê công khai",
)
def test_lc_t093_2_uploaded_images_attached_to_new_draft(fake_wp, wp_client):
    """Mong đợi: gửi nháp xong, mọi ảnh vừa tải có bài cha là đúng bài nháp vừa tạo (WordPress
    không cho người chưa đăng nhập đọc ảnh của bài chưa đăng qua REST). Thực tế: không lệnh nào
    gửi ``post``, ảnh không có bài cha."""
    site = _ParentSite(fake_wp)
    web = make_web_image(sl54._jpeg(gps=sl54.GPS_NE))
    result = wp_client.create_draft_with_images(
        "Sửa cổng inox Tân Phú",
        [
            "<p>Cổng sau khi sửa.</p>",
            DraftImage(web, alt="Cổng inox", tags=ImageTags(category="Cổng inox", area="Tân Phú")),
        ],
    )
    media_ids = [image.id for image in result.images]
    assert media_ids and result.post.id == site.post_id  # tiền đề: một ảnh, bài nháp 42
    assert {media_id: site.parents.get(media_id) for media_id in media_ids} == {
        media_id: site.post_id for media_id in media_ids
    }

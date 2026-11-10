"""T-132 · SL-T106-1: trang Kết nối WordPress, câu báo thiếu quyền viết bài hay tải ảnh chỉ khuyên
tài khoản riêng ở vai Biên tập viên (quyết định 2A), không khuyên Quản trị viên.

Đi qua client WordPress thật với WordPress giả (cách nối của ``tests/test_t106_trang_ket_noi.py``).
Ca «không có chữ Quản trị viên (Administrator)» của Soi Lỗi ở ``tests/test_soi_loi_t106.py``; ở
đây canh thêm: câu vẫn còn, khuyên đúng vai, chỉ hiện khi thiếu quyền.
"""

from __future__ import annotations

import pytest
import test_soi_loi_t044 as sl44
import test_t106_trang_ket_noi as t106

fake_wp = sl44.fake_wp  # mọi WordPressClient trên trang dùng WordPress giả
account = t106.account  # tên đăng nhập, mật khẩu ứng dụng dễ nhận ra (tự dùng cho mọi ca)

MISSING = "Tài khoản thiếu quyền viết bài hoặc tải ảnh"
WRITE_ONLY = {"edit_posts": True, "publish_posts": False, "upload_files": False}


def missing_rights(at) -> list[str]:
    return [sl44.shown(w.value) for w in at.warning if MISSING in w.value]


@pytest.mark.parametrize(
    ("roles", "capabilities"),
    [
        (["contributor"], WRITE_ONLY),
        (["subscriber"], {"edit_posts": False, "upload_files": False}),
        (["author"], {"edit_posts": True, "upload_files": False}),
        (["editor"], None),  # website không cho biết quyền
    ],
    ids=["contributor", "subscriber", "author-khong-tai-anh", "khong-ro-quyen"],
)
def test_thieu_quyen_chi_khuyen_bien_tap_vien(project_root, fake_wp, roles, capabilities):
    at = t106.connect(project_root, fake_wp, t106.me(roles, capabilities))
    [text] = missing_rights(at)
    assert "Biên tập viên (Editor)" in text and "tài khoản riêng" in text
    assert "Quản trị viên" not in text and "Administrator" not in text
    t106.assert_no_account_details(text)


@pytest.mark.parametrize("role", ["editor", "administrator"])
def test_du_quyen_thi_khong_co_cau_thieu_quyen(project_root, fake_wp, role):
    at = t106.connect(
        project_root, fake_wp, t106.me([role], {**t106.CAN_WRITE, "unfiltered_html": True})
    )
    assert missing_rights(at) == []

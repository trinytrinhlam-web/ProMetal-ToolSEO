"""T-049: xử lý ảnh (xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch, ảnh xem trước) và tên file.

Mọi ảnh trong test là ảnh giả tạo ngay trong bộ nhớ hoặc thư mục tạm (không commit ảnh thật,
không gọi mạng). Tọa độ GPS là tọa độ giả.
"""

import re

import pytest

from seo_app.images import naming

# ----- tên file (naming.py) ----------------------------------------------------------------


def test_ten_file_theo_the_khong_dau():
    ten = naming.image_file_name(category="Cổng inox", area="Tân Phú", project_code="CT012")
    assert ten == "cong-inox-tan-phu-ct012.webp"


def test_ten_file_chi_gom_chu_thuong_so_va_gach_noi():
    ten = naming.image_file_name(category="Cửa sắt 2 cánh!!", area="Đà Nẵng / Hải Châu")
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.webp", ten)
    assert ten == "cua-sat-2-canh-da-nang-hai-chau.webp"


def test_thieu_the_thi_dung_alt_roi_toi_anh():
    assert naming.image_file_name(alt="Bản lề cổng sắt bị gỉ") == "ban-le-cong-sat-bi-gi.webp"
    assert naming.image_file_name() == "anh.webp"
    assert naming.image_file_name(category="  ", alt="!!!") == "anh.webp"


def test_ma_cong_trinh_sai_mau_bi_bo():
    # Mã công trình là chữ tự do từ tên thư mục: chỉ nhận đúng mẫu CT + số.
    ten = naming.image_file_name(category="Cổng inox", project_code="Nhà anh Tuấn 12 Lê Lợi")
    assert ten == "cong-inox.webp"
    assert naming.image_file_name(project_code="ct7") == "ct7.webp"


def test_ten_file_toi_da_60_ky_tu_cat_dung_ranh_gioi_tu():
    dai = "Cửa cuốn khe thoáng " * 10
    ten = naming.image_file_name(category=dai)
    goc = ten.removesuffix(".webp")
    assert len(goc) <= naming.MAX_NAME_CHARS
    assert not goc.endswith("-")
    assert "cua-cuon-khe-thoang" in goc


def test_tranh_trung_ten_them_so():
    da_dung = []
    for _ in range(3):
        da_dung.append(naming.image_file_name(category="Cổng inox", taken=da_dung))
    assert da_dung == ["cong-inox.webp", "cong-inox-2.webp", "cong-inox-3.webp"]


def test_tranh_trung_khong_phan_biet_hoa_thuong_va_duoi():
    ten = naming.image_file_name(category="Cổng inox", taken=["CONG-INOX.WEBP", "cong-inox-2"])
    assert ten == "cong-inox-3.webp"


def test_ten_dai_bi_trung_van_khong_qua_60_ky_tu():
    dai = "Sửa cửa cuốn khe thoáng nhà phố quận Tân Bình " * 3
    ten1 = naming.image_file_name(category=dai)
    ten2 = naming.image_file_name(category=dai, taken=[ten1])
    assert ten2 != ten1
    assert ten2.endswith("-2.webp")
    assert len(ten2.removesuffix(".webp")) <= naming.MAX_NAME_CHARS


def test_anh_ai_co_tien_to_va_khong_mang_ma_cong_trinh():
    ten = naming.image_file_name(category="Cổng inox", project_code="CT012", ai_generated=True)
    assert ten == "minh-hoa-ai-cong-inox.webp"
    assert naming.image_file_name(ai_generated=True) == "minh-hoa-ai-anh.webp"
    dai = naming.image_file_name(category="Cửa cuốn khe thoáng " * 10, ai_generated=True)
    assert len(dai.removesuffix(".webp")) <= naming.MAX_NAME_CHARS


def test_ten_thiet_bi_windows_khong_thanh_ten_file():
    assert naming.image_file_name(alt="CON") == "con-anh.webp"
    assert naming.image_file_name(alt="nul") == "nul-anh.webp"


def test_ham_dat_ten_khong_nhan_ten_thu_muc_hay_ten_file_goc():
    # Góp ý Lá Chắn T-046 số 3: không có đường nào đưa tên thư mục/tên file gốc vào tên file.
    with pytest.raises(TypeError):
        naming.image_file_name(folder="Nha anh Tuan - 12 Le Loi/truoc")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        naming.image_file_name("IMG_0001.HEIC")  # type: ignore[misc]


def test_qua_nhieu_anh_trung_ten_thi_bao_loi():
    da_dung = ["anh"] + [f"anh-{n}" for n in range(2, naming.MAX_DUPLICATES + 1)]
    with pytest.raises(ValueError, match="trùng tên"):
        naming.image_file_name(taken=da_dung)

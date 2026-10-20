"""T-047: Pillow và pillow-heif đã cài, Pillow mở được ảnh HEIC (ảnh iPhone).

Ảnh HEIC trong test là ảnh giả, tạo ngay trong thư mục tạm (không commit ảnh thật, không gọi mạng).
Việc đăng ký HEIC vào Pillow được hoàn tác sau mỗi test để không ảnh hưởng test khác.
"""

import pillow_heif
import pytest
from PIL import Image, UnidentifiedImageError

# Các bảng đăng ký định dạng của Pillow mà ``register_heif_opener`` ghi vào.
_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")


@pytest.fixture
def heif_registry_restored():
    """Chụp lại bảng định dạng của Pillow, trả nguyên trạng sau test."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _REGISTRIES}
    yield
    for name, value in saved.items():
        current = getattr(Image, name)
        current.clear()
        if isinstance(current, dict):
            current.update(value)
        else:
            current.extend(value)


def _go_heif_khoi_bang():
    """Gỡ HEIF khỏi mọi bảng định dạng của Pillow, như chưa từng gọi ``register_heif_opener``.

    Module ảnh (T-049) đăng ký HEIF khi mở ảnh lần đầu, nên trong một lượt chạy test HEIF có thể
    đã có sẵn trong bảng (điều kiện 6 Lá Chắn T-047).
    """
    Image.init()
    while "HEIF" in Image.ID:
        Image.ID.remove("HEIF")
    for name in ("OPEN", "MIME", "SAVE", "SAVE_ALL"):
        getattr(Image, name).pop("HEIF", None)
    for extension in [ext for ext, fmt in Image.EXTENSION.items() if fmt == "HEIF"]:
        del Image.EXTENSION[extension]


@pytest.fixture
def heif_chua_dang_ky(heif_registry_restored):
    """HEIF chưa đăng ký trong suốt test (gỡ nếu có sẵn), bảng định dạng trả nguyên sau test."""
    _go_heif_khoi_bang()
    yield


def _make_fake_heic(path, size=(64, 48)):
    """Tạo ảnh HEIC giả một màu bằng bộ mã hóa đi kèm pillow-heif."""
    image = Image.new("RGB", size, (200, 120, 40))
    pillow_heif.from_pillow(image).save(path, quality=80)
    return path


def test_libheif_kem_bo_giai_ma_hevc():
    info = pillow_heif.libheif_info()
    assert pillow_heif.libheif_version()
    # libde265 giải mã ảnh iPhone (HEVC); thiếu nó thì không đọc được HEIC.
    assert "libde265" in info["decoders"]


def test_chua_dang_ky_thi_pillow_khong_mo_duoc_heic(tmp_path, heif_chua_dang_ky):
    path = _make_fake_heic(tmp_path / "anh.heic")
    assert "HEIF" not in Image.OPEN
    with pytest.raises(UnidentifiedImageError):
        Image.open(path)


def test_go_heif_khi_da_dang_ky_san_roi_tra_lai(tmp_path, heif_registry_restored):
    # Fixture ``heif_chua_dang_ky`` vẫn đúng khi HEIF đã đăng ký từ trước (không còn phải skip).
    path = _make_fake_heic(tmp_path / "anh.heic")
    pillow_heif.register_heif_opener()
    with Image.open(path) as image:
        assert image.format == "HEIF"
    _go_heif_khoi_bang()
    with pytest.raises(UnidentifiedImageError):
        Image.open(path)
    assert Image.registered_extensions().get(".heic") is None


def test_dang_ky_roi_mo_lai_heic_dung_kich_thuoc(tmp_path, heif_registry_restored):
    pillow_heif.register_heif_opener()
    assert "HEIF" in Image.OPEN
    assert Image.registered_extensions().get(".heic") == "HEIF"

    path = _make_fake_heic(tmp_path / "anh.heic", size=(64, 48))
    with Image.open(path, formats=["HEIF"]) as image:
        assert image.format == "HEIF"
        assert image.size == (64, 48)
        image.load()  # giải mã thật, không chỉ đọc phần đầu file
        assert image.getpixel((10, 10))[0] > 150

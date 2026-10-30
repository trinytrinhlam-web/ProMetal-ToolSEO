"""Test thêm của Soi Lỗi T-107: đường mở HEIC sau khi giải mã một luồng (LC-T093-3).

- SL-T107-1: lỗi ``RuntimeError`` của libheif lúc giải mã (ví dụ «Security limit exceeded» khi mô
  tả lưới khai cỡ đầu ra rất lớn) lọt ra khỏi ``process``, trái lời hứa «mọi lỗi thành
  ``ImageProcessError``». Trang Soạn bài không sập (có ``except Exception`` với câu chung), nhưng
  người dùng không thấy đúng câu báo.
- SL-T107-2: phép kiểm lưới trước khi giải mã (T-107) không so cỡ đầu ra của lưới với cỡ ảnh Pillow
  báo lúc mở (``ispe``) hay với giới hạn 80 triệu điểm ảnh. Lưới lớn mà mọi ô trỏ cùng một mục mã
  hóa (file khoảng 20 kB) qua mọi phép kiểm, libheif giải mã hết lưới rồi mới báo cỡ không khớp
  (đo trên máy: lưới 31 × 31 ô 512, 11–14 giây và thêm 250 MB mỗi lần mở; xem báo cáo).

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T107-x. Ảnh dựng bằng bộ mã hóa đi kèm
pillow-heif, không gọi mạng.
"""

from __future__ import annotations

import io
import struct

import pillow_heif
import pytest
import test_images_process as tp
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.images import process

# T-107 lượt 3 (Chỉ Huy duyệt 30/10, chủ dự án chọn tạm không nhận HEIC): app tắt HEIC bằng
# công tắc ``folders.HEIC_ENABLED``; file này bật lại công tắc để đường HEIC vẫn được kiểm cho
# lúc bật lại (fixture ``heic_enabled`` trong ``tests/conftest.py``).
pytestmark = pytest.mark.usefixtures("heic_enabled")

_REGISTRIES = ("OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_OPTIONS = ("DECODE_THREADS", "THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")
MAKERS = [process.open_image, process.make_preview, process.make_web_image, process.make_ai_image]
MAKER_IDS = ["open_image", "make_preview", "make_web_image", "make_ai_image"]


@pytest.fixture(autouse=True)
def _heif_state_restored(monkeypatch):
    Image.init()
    monkeypatch.setattr(Image, "ID", list(Image.ID))
    for name in _REGISTRIES:
        monkeypatch.setattr(Image, name, dict(getattr(Image, name)))
    for name in _OPTIONS:
        monkeypatch.setattr(heif_options, name, getattr(heif_options, name))


@pytest.fixture(scope="module")
def grid_heic():
    """Lưới 3 × 2 ô 512 (ảnh 1100 × 800), như ảnh iPhone thu nhỏ."""
    buffer = io.BytesIO()
    pillow_heif.from_pillow(tp._anh_bon_mau((1100, 800))).save(buffer, quality=60, tile_size=512)
    return buffer.getvalue()


def _fixed_messages() -> set[str]:
    return {
        process._MSG_BROKEN,
        process._MSG_HEIF_GRID,
        process._MSG_NOT_IMAGE,
        str(process._too_many_pixels()),
    }


def _with_grid_output(data: bytes, width: int, height: int) -> bytes:
    """Sửa cỡ đầu ra trong mô tả lưới (``ImageGrid``: 00 00 hàng-1 cột-1 rộng cao, 16 bit)."""
    pattern = bytes([0, 0, 1, 2]) + struct.pack(">HH", 1100, 800)
    at = data.find(pattern)
    if at < 0 or data.find(pattern, at + 1) >= 0:
        pytest.skip("bộ mã hóa pillow-heif ghi mô tả lưới khác dạng")
    changed = bytearray(data)
    struct.pack_into(">HH", changed, at + 4, width, height)
    return bytes(changed)


# ----- SL-T107-1: RuntimeError của libheif lúc giải mã -----------------------------------------


@pytest.mark.parametrize("make", MAKERS, ids=MAKER_IDS)
def test_sl_t107_1_libheif_runtime_error_becomes_fixed_message(grid_heic, make):
    """File thật: mô tả lưới khai đầu ra 65535 × 65535 (cỡ ảnh lúc mở vẫn 1100 × 800). libheif từ
    chối cấp bộ nhớ lúc giải mã bằng ``RuntimeError``. Mong đợi: câu báo cố định của app."""
    data = _with_grid_output(grid_heic, 65535, 65535)
    with pytest.raises(process.ImageProcessError) as info:
        make(data)
    assert str(info.value) in _fixed_messages()


# ----- SL-T107-2: lưới lớn hơn cỡ ảnh qua phép kiểm, giải mã hết rồi mới báo ----------------------


@pytest.mark.parametrize(
    ("columns", "rows", "tile"),
    [(24, 24, 512), (31, 31, 512), (31, 31, 1024)],
    ids=["24x24-o512-151mp", "31x31-o512-252mp", "31x31-o1024-1007mp"],
)
def test_sl_t107_2_grid_larger_than_image_rejected_before_decode(
    grid_heic, monkeypatch, columns, rows, tile
):
    """Thông tin lưới đúng như libheif 1.23.6 báo lúc mở file dựng (đo trên máy): ``columns ×
    rows`` ô cỡ ``tile``, đầu ra ``columns·tile × rows·tile``, trong khi Pillow báo cỡ ảnh nhỏ
    (``ispe``). libheif nhận tối đa 1000 tham chiếu ô nên 31 × 31 là lưới lớn nhất mở được. Số ô
    vừa đủ phủ đầu ra nên qua phép «thừa ô», ô ≥ 64 qua phép «ô nhỏ». Mong đợi: từ chối trước
    khi giải mã (``load`` không được gọi), câu báo cố định."""
    real_open = process._pillow_open
    loads: list[str] = []
    real_load = pillow_heif.HeifImageFile.load

    def open_with_big_grid(data, formats):
        image = real_open(data, formats)
        image.info["tiling"] = {
            "num_columns": columns,
            "num_rows": rows,
            "tile_width": tile,
            "tile_height": tile,
            "image_width": columns * tile,
            "image_height": rows * tile,
        }
        return image

    def counting_load(self):
        loads.append("load")
        return real_load(self)

    monkeypatch.setattr(process, "_pillow_open", open_with_big_grid)
    monkeypatch.setattr(pillow_heif.HeifImageFile, "load", counting_load)
    with pytest.raises(process.ImageProcessError) as info:
        process.make_preview(grid_heic)
    assert str(info.value) in _fixed_messages()
    assert loads == []


# ----- Bổ sung test (thử đột biến M1): HEIF đã đăng ký sẵn, số luồng bị đặt lại ----------------


class _LoadFileSpy:
    """Thay ``_pillow_heif`` trong ``pillow_heif.heif``: ghi số luồng giải mã của mỗi lần mở."""

    def __init__(self, real):
        self._real = real
        self.threads: list[int] = []

    def load_file(self, data, threads, *args):
        self.threads.append(threads)
        return self._real.load_file(data, threads, *args)

    def __getattr__(self, name):
        return getattr(self._real, name)


@pytest.mark.parametrize("who_registered", ["app", "thu-vien-khac"])
def test_already_registered_heif_open_still_single_thread(grid_heic, monkeypatch, who_registered):
    """HEIF đã có trong bảng định dạng (app mở ảnh trước đó, hay mã khác gọi
    ``register_heif_opener()`` không tham số như ``import pillow_heif.HeifImagePlugin``), rồi số
    luồng bị đặt lại 4 (mặc định pillow-heif). Lần mở sau của app vẫn phải truyền 0 cho libheif:
    ``_register_heif`` đặt lại ``DECODE_THREADS`` mỗi lần, không chỉ lúc đăng ký. Test T-107 cũ
    không phủ ca này (fixture trả bảng định dạng về chưa đăng ký trước mỗi test)."""
    import pillow_heif.heif as heif_module

    if who_registered == "app":
        process.open_image(grid_heic)
    else:
        pillow_heif.register_heif_opener()
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile
    heif_options.DECODE_THREADS = 4
    spy = _LoadFileSpy(heif_module._pillow_heif)
    monkeypatch.setattr(heif_module, "_pillow_heif", spy)
    process.open_image(grid_heic)
    assert spy.threads == [process.HEIF_DECODE_THREADS] == [0]


def test_grid_output_equal_to_image_size_still_accepted(grid_heic):
    """Đối chứng (qua): lưới thật của bộ mã hóa (đầu ra đúng bằng cỡ ảnh) vẫn đọc được."""
    process._register_heif()
    with Image.open(io.BytesIO(grid_heic), formats=["HEIF"]) as image:
        tiling = image.info["tiling"]
        assert (tiling["image_width"], tiling["image_height"]) == image.size
    assert process.open_image(grid_heic).size == (1100, 800)

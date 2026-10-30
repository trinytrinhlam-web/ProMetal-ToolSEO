"""T-107 (Thợ Máy): HEIC giải mã một luồng (LC-T093-3) và kiểm lưới ô trước khi giải mã.

- libheif 1.23.6 (trong pillow-heif 1.8.1) dùng vùng nhớ đã giải phóng khi giải mã song song các
  ô ảnh lưới (GHSA-35mc-3887-rr37). App đặt ``DECODE_THREADS = 0`` ở ``_register_heif``, nên mọi
  lần mở ảnh đều truyền 0 xuống ``_pillow_heif.load_file``.
- Ảnh lưới có ô nhỏ hơn 64 điểm ảnh hay thừa ô bị từ chối trước khi giải mã (giảm lỗi «làm treo
  CPU», GHSA-48p4-gj45-w9v6).

Ảnh HEIC trong test dựng bằng bộ mã hóa đi kèm pillow-heif theo kiểu ảnh iPhone (ô 512 × 512),
không có ảnh thật nào trong repo.
"""

from __future__ import annotations

import io
from types import SimpleNamespace

import pillow_heif
import pillow_heif.heif as heif_module
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


@pytest.fixture(autouse=True)
def _heif_state_restored(monkeypatch):
    """Bảng định dạng của Pillow và tùy chọn pillow-heif trả nguyên sau mỗi test."""
    Image.init()
    monkeypatch.setattr(Image, "ID", list(Image.ID))
    for name in _REGISTRIES:
        monkeypatch.setattr(Image, name, dict(getattr(Image, name)))
    for name in _OPTIONS:
        monkeypatch.setattr(heif_options, name, getattr(heif_options, name))


def _grid_heic(size=(1100, 800), orientation=1, *, gps=True):
    """HEIC chia lưới ô 512 × 512 như ảnh iPhone, có EXIF (GPS, chiều xoay) và XMP."""
    params = {"exif": tp._exif_day_du(orientation, gps=gps).tobytes(), "xmp": tp.XMP}
    buffer = io.BytesIO()
    pillow_heif.from_pillow(tp._anh_bon_mau(size)).save(buffer, quality=90, tile_size=512, **params)
    return buffer.getvalue()


@pytest.fixture(scope="module")
def grid_heic():
    return _grid_heic()


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


@pytest.fixture
def load_file_spy(monkeypatch):
    spy = _LoadFileSpy(heif_module._pillow_heif)
    monkeypatch.setattr(heif_module, "_pillow_heif", spy)
    return spy


# ------------------------------------------------------------------ yêu cầu 1: một luồng


def test_grid_heic_is_really_a_grid(grid_heic):
    process._register_heif()
    with Image.open(io.BytesIO(grid_heic), formats=["HEIF"]) as image:
        assert image.info["tiling"]["num_columns"] * image.info["tiling"]["num_rows"] == 6


def test_register_heif_sets_single_thread_every_call():
    heif_options.DECODE_THREADS = 4  # ai đó đặt lại số luồng: lần mở sau đặt về 0
    heif_options.THUMBNAILS = True
    process._register_heif()
    assert heif_options.DECODE_THREADS == process.HEIF_DECODE_THREADS == 0
    assert heif_options.THUMBNAILS is False
    assert heif_options.DEPTH_IMAGES is False and heif_options.AUX_IMAGES is False
    assert heif_options.DISABLE_SECURITY_LIMITS is False
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile


def test_first_registration_also_single_thread(monkeypatch):
    # Như lúc app mới chạy: HEIF chưa có trong bảng định dạng.
    monkeypatch.setattr(Image, "ID", [name for name in Image.ID if name != "HEIF"])
    for name in _REGISTRIES:
        table = {k: v for k, v in getattr(Image, name).items() if k != "HEIF" and v != "HEIF"}
        monkeypatch.setattr(Image, name, table)
    seen = {}
    real = pillow_heif.register_heif_opener

    def register(**kwargs):
        seen.update(kwargs)
        real(**kwargs)

    monkeypatch.setattr(pillow_heif, "register_heif_opener", register)
    heif_options.DECODE_THREADS = 4
    process._register_heif()
    assert seen["decode_threads"] == 0
    assert seen["thumbnails"] is False and seen["depth_images"] is False
    assert seen["aux_images"] is False
    assert heif_options.DECODE_THREADS == 0
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile


@pytest.mark.parametrize(
    "make",
    [process.open_image, process.make_web_image, process.make_ai_image, process.make_preview],
    ids=["open_image", "make_web_image", "make_ai_image", "make_preview"],
)
def test_every_open_passes_zero_threads_to_libheif(grid_heic, load_file_spy, make):
    heif_options.DECODE_THREADS = 4
    make(grid_heic)
    assert load_file_spy.threads and set(load_file_spy.threads) == {0}


# ------------------------------------------------------------------ yêu cầu 3: ảnh vẫn đúng


def test_grid_heic_rotated_keeps_gps_and_turns_once(load_file_spy):
    data = _grid_heic((1100, 800), orientation=6)
    web = process.make_web_image(data)
    assert set(load_file_spy.threads) == {0}
    assert tp._gps_doc_lai(web.data) == tp.GPS_MONG_DOI
    anh = tp._mo(web.data)
    assert anh.size == (800, 1100)  # xoay theo irot đúng một lần, cạnh dài 1100 < 1600
    mong_doi = tp._anh_bon_mau((1100, 800)).transpose(Image.Transpose.ROTATE_270)
    for thuc, dung in zip(tp._bon_goc(anh), tp._bon_goc(mong_doi), strict=True):
        assert tp._mau_gan(thuc, dung)
    for bi_mat in tp.BI_MAT:
        assert bi_mat not in web.data


def test_grid_heic_pixels_same_as_parallel_decode(grid_heic):
    """Giải mã một luồng ra đúng từng điểm ảnh như giải mã 4 luồng (chỉ đổi cách chạy)."""
    single = process.open_image(grid_heic).tobytes()
    heif_options.DECODE_THREADS = 4
    with Image.open(io.BytesIO(grid_heic), formats=["HEIF"]) as image:
        image.load()
        parallel = image.tobytes()
    assert single == parallel


# ------------------------------------------------------------------ yêu cầu 2: lưới ô lạ


def _tiling(columns, rows, tile_w, tile_h, width, height):
    return {
        "num_columns": columns,
        "num_rows": rows,
        "tile_width": tile_w,
        "tile_height": tile_h,
        "image_width": width,
        "image_height": height,
    }


def _grid(tiling, size=None):
    """Ảnh giả chỉ có những gì ``_check_heif_grid`` đọc. Mặc định cỡ ảnh lúc mở (``ispe``) đúng
    bằng đầu ra của lưới, như ảnh thật của bộ mã hóa."""
    if size is None:
        try:
            size = (int(tiling["image_width"]), int(tiling["image_height"]))
        except (KeyError, TypeError, ValueError):
            size = (1, 1)
    return SimpleNamespace(format="HEIF", info={"tiling": tiling}, size=size)


@pytest.mark.parametrize(
    ("tiling", "size"),
    [
        (_tiling(8, 6, 512, 512, 4032, 3024), None),  # iPhone 12 MP
        (_tiling(6, 8, 512, 512, 3024, 4032), None),  # iPhone 12 MP chụp dọc (đã xoay)
        (_tiling(16, 12, 512, 512, 8064, 6048), None),  # iPhone 48 MP
        (_tiling(19, 14, 512, 512, 9248, 6936), None),  # điện thoại 64 MP
        (_tiling(3, 2, 512, 512, 1100, 800), None),
        (_tiling(1, 1, 64, 64, 64, 64), None),  # ô nhỏ nhất hợp lệ
        (_tiling(8, 12, 512, 256, 4032, 3024), None),  # ô chữ nhật, libheif chưa xoay cỡ ô
        (_tiling(12, 8, 512, 256, 4032, 3024), None),
        (_tiling(8, 6, 512, 512, 4032, 3024), (3024, 4032)),  # cỡ ảnh đã xoay, lưới chưa
        (_tiling(8, 6, 512, 512, 4032, 3024), (4030, 3022)),  # clap cắt phần thừa của ô
        (_tiling(8, 6, 512, 512, 4032, 3024), (3521, 2513)),  # cắt dưới một ô mỗi chiều
    ],
    ids=["12mp", "12mp-doc", "48mp", "64mp", "nho", "o-64", "o-chu-nhat-a", "o-chu-nhat-b",
         "anh-xoay-luoi-chua", "clap-it", "clap-duoi-mot-o"],
)  # fmt: skip
def test_real_phone_grids_accepted(tiling, size):
    process._check_heif_grid(_grid(tiling, size))


@pytest.mark.parametrize(
    "tiling",
    [
        _tiling(31, 31, 1, 1, 31, 31),  # dạng file làm treo CPU: lưới ô 1 × 1
        _tiling(4, 4, 63, 63, 252, 252),
        _tiling(4, 2, 512, 512, 1100, 800),  # thừa một cột
        _tiling(3, 3, 512, 512, 1100, 800),  # thừa một hàng
        _tiling(30, 30, 64, 64, 64, 64),  # 900 ô cho ảnh một ô
        _tiling(0, 1, 512, 512, 512, 512),
        _tiling(1, 1, 512, 512, 0, 512),
        {"num_columns": 3},  # thiếu khóa
        _tiling("ba", 2, 512, 512, 1100, 800),
        _tiling(None, 2, 512, 512, 1100, 800),
    ],
    ids=["o-1x1", "o-63", "thua-cot", "thua-hang", "900-o", "0-cot", "rong-0", "thieu-khoa",
         "chu", "none"],
)  # fmt: skip
def test_strange_grids_rejected_before_decode(tiling):
    with pytest.raises(process.ImageProcessError) as info:
        process._check_heif_grid(_grid(tiling))
    assert str(info.value) == process._MSG_HEIF_GRID


@pytest.mark.parametrize(
    ("tiling", "size"),
    [
        # SL-T107-2: lưới lớn, mọi ô trỏ cùng một mục, cỡ ảnh khai nhỏ (qua giới hạn 80 MP).
        (_tiling(24, 24, 512, 512, 12288, 12288), (1100, 800)),
        (_tiling(31, 31, 512, 512, 15872, 15872), (1100, 800)),
        (_tiling(31, 31, 1024, 1024, 31744, 31744), (1100, 800)),
        (_tiling(31, 31, 512, 512, 15872, 15872), (4032, 3024)),
        # Lớn hơn cỡ ảnh đúng một ô, hay nhỏ hơn cỡ ảnh.
        (_tiling(9, 6, 512, 512, 4544, 3024), (4032, 3024)),
        (_tiling(8, 6, 512, 512, 4032, 3024), (4100, 3024)),
        # Một ô rất lớn cho ảnh nhỏ: phải giải mã 268 triệu điểm ảnh.
        (_tiling(1, 1, 16384, 16384, 100, 100), (100, 100)),
        # Sát 80 MP, phần thừa của ô đẩy tổng điểm ảnh phải giải mã lên 88 triệu.
        (_tiling(21, 16, 512, 512, 10328, 7744), (10328, 7744)),
    ],
    ids=["24x24-o512", "31x31-o512", "31x31-o1024", "31x31-anh-12mp", "thua-dung-mot-o",
         "nho-hon-anh", "mot-o-khong-lo", "sat-80mp-tong-o"],
)  # fmt: skip
def test_grid_not_matching_image_size_rejected(tiling, size):
    with pytest.raises(process.ImageProcessError) as info:
        process._check_heif_grid(_grid(tiling, size))
    assert str(info.value) == process._MSG_HEIF_GRID


def test_grid_check_only_for_heif():
    bad = _tiling(31, 31, 1, 1, 31, 31)
    process._check_heif_grid(SimpleNamespace(format="PNG", info={"tiling": bad}, size=(31, 31)))
    process._check_heif_grid(SimpleNamespace(format="HEIF", info={}, size=(31, 31)))


def test_open_rejects_strange_grid_without_decoding(grid_heic, monkeypatch):
    """Đường thật: ``_open`` đọc phần đầu file, thấy lưới lạ thì dừng, không giải mã ô nào."""
    real_open = process._pillow_open
    loads: list[str] = []
    real_load = pillow_heif.HeifImageFile.load

    def open_with_bad_grid(data, formats):
        image = real_open(data, formats)
        image.info["tiling"] = _tiling(31, 31, 1, 1, 31, 31)
        return image

    def counting_load(self):
        loads.append("load")
        return real_load(self)

    monkeypatch.setattr(process, "_pillow_open", open_with_bad_grid)
    monkeypatch.setattr(pillow_heif.HeifImageFile, "load", counting_load)
    with pytest.raises(process.ImageProcessError) as info:
        process.make_web_image(grid_heic)
    assert str(info.value) == process._MSG_HEIF_GRID
    assert loads == []


def test_grid_message_is_fixed_vietnamese():
    message = process._MSG_HEIF_GRID
    assert message.startswith("Ảnh HEIC") and "\\" not in message and "/" not in message


# ------------------------------------------------------------------ lượt 3: alpha (LC-T107-1)


def _heic(mode, size=(64, 48)):
    buffer = io.BytesIO()
    pillow_heif.from_pillow(Image.new(mode, size)).save(buffer, quality=80)
    return buffer.getvalue()


@pytest.mark.parametrize("mode", ["RGBA", "LA"])
@pytest.mark.parametrize(
    "make",
    [process.open_image, process.make_web_image, process.make_ai_image, process.make_preview],
    ids=["open_image", "make_web_image", "make_ai_image", "make_preview"],
)
def test_heic_with_alpha_rejected_before_decode(monkeypatch, make, mode):
    loads: list[str] = []
    real_load = pillow_heif.HeifImageFile.load

    def counting_load(self):
        loads.append("load")
        return real_load(self)

    monkeypatch.setattr(pillow_heif.HeifImageFile, "load", counting_load)
    with pytest.raises(process.ImageProcessError) as info:
        make(_heic(mode))
    assert str(info.value) == process._MSG_HEIF_ALPHA
    assert loads == []


@pytest.mark.parametrize(
    ("image_format", "mode", "rejected"),
    [
        ("HEIF", "RGBA", True),
        ("HEIF", "RGBa", True),
        ("HEIF", "LA", True),
        ("HEIF", "La", True),
        ("HEIF", "RGB", False),
        ("HEIF", "L", False),
        ("HEIF", "I;16", False),
        ("PNG", "RGBA", False),
        ("WEBP", "RGBA", False),
        ("JPEG", "RGB", False),
    ],
)
def test_alpha_check_only_for_heif(image_format, mode, rejected):
    image = SimpleNamespace(format=image_format, mode=mode)
    if rejected:
        with pytest.raises(process.ImageProcessError):
            process._check_heif_alpha(image)
    else:
        process._check_heif_alpha(image)


@pytest.mark.parametrize("image_format", ["PNG", "WEBP"])
def test_png_webp_with_alpha_still_accepted(image_format):
    data = tp._luu(Image.new("RGBA", (64, 48), (10, 20, 30, 100)), image_format)
    assert tp._mo(process.make_web_image(data).data).mode == "RGBA"


@pytest.mark.parametrize("mode", ["RGB", "L"])
def test_heic_without_alpha_still_accepted(mode):
    assert process.open_image(_heic(mode)).size == (64, 48)

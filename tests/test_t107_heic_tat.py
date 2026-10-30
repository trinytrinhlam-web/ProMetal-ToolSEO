"""T-107 lượt 3 (Thợ Máy): app tạm không nhận ảnh HEIC (chủ dự án chọn 30/10, LC-T107-2).

Công tắc duy nhất ``seo_app.images.folders.HEIC_ENABLED`` (đang ``False``) cho tới khi pillow-heif
mang libheif từ 1.23.7. Khi tắt:

- ``"HEIF"`` không nằm trong định dạng được mở, app không đăng ký HEIF với Pillow, libheif không
  được gọi ở mọi đường (xem trước, gửi AI, gửi WordPress);
- file HEIC nhận theo **nội dung** (hộp ``ftyp``), kể cả khi đổi đuôi ``.jpg``: câu báo cố định;
- thư mục ảnh không liệt kê ``.heic``, ``.heif``.

File này chạy ở cấu hình mặc định (không dùng fixture ``heic_enabled``). Ảnh HEIC dựng bằng bộ
mã hóa đi kèm pillow-heif, không gọi mạng.
"""

from __future__ import annotations

import io

import pillow_heif
import pillow_heif.heif as heif_module
import pytest
import test_images_process as tp
from PIL import Image

from seo_app.images import folders, process
from seo_app.images.folders import ImageLibrary

_REGISTRIES = ("OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
MAKERS = [process.open_image, process.make_preview, process.make_ai_image, process.make_web_image]
MAKER_IDS = ["open_image", "make_preview", "make_ai_image", "make_web_image"]
HEIC_OFF = "Tạm chưa nhận ảnh HEIC của iPhone, hãy dùng ảnh JPEG."


@pytest.fixture(autouse=True)
def _heif_not_registered(monkeypatch):
    """Như lúc app mới chạy: HEIF chưa có trong bảng định dạng của Pillow (trả lại sau test)."""
    Image.init()
    monkeypatch.setattr(Image, "ID", [name for name in Image.ID if name != "HEIF"])
    for name in _REGISTRIES:
        table = {k: v for k, v in getattr(Image, name).items() if k != "HEIF" and v != "HEIF"}
        monkeypatch.setattr(Image, name, table)


@pytest.fixture(scope="module")
def heic():
    buffer = io.BytesIO()
    pillow_heif.from_pillow(tp._anh_bon_mau((64, 48))).save(
        buffer, quality=80, exif=tp._exif_day_du(6).tobytes()
    )
    return buffer.getvalue()


class _Spy:
    def __init__(self, real):
        self._real = real
        self.calls = 0

    def load_file(self, *args):
        self.calls += 1
        return self._real.load_file(*args)

    def __getattr__(self, name):
        return getattr(self._real, name)


@pytest.fixture
def libheif_calls(monkeypatch):
    """Đếm số lần pillow-heif gọi libheif đọc file, và số lần đăng ký HEIF với Pillow."""
    spy = _Spy(heif_module._pillow_heif)
    monkeypatch.setattr(heif_module, "_pillow_heif", spy)
    registered: list[dict] = []
    monkeypatch.setattr(pillow_heif, "register_heif_opener", lambda **kw: registered.append(kw))
    return spy, registered


def test_switch_is_off_by_default():
    assert folders.HEIC_ENABLED is False
    assert "HEIF" not in process.ALLOWED_FORMATS
    assert "HEIF" not in process._allowed_formats()
    assert not folders.IMAGE_EXTENSIONS & {".heic", ".heif"}
    assert process._MSG_HEIC_OFF == HEIC_OFF
    assert "HEIC" not in process._MSG_NOT_IMAGE


@pytest.mark.parametrize("make", MAKERS, ids=MAKER_IDS)
def test_every_path_rejects_heic_without_libheif(heic, libheif_calls, make):
    spy, registered = libheif_calls
    with pytest.raises(process.ImageProcessError) as info:
        make(heic)
    assert str(info.value) == HEIC_OFF
    assert spy.calls == 0 and registered == []
    assert "HEIF" not in Image.OPEN


@pytest.mark.parametrize("make", MAKERS, ids=MAKER_IDS)
def test_other_formats_open_without_registering_heif(libheif_calls, make):
    spy, registered = libheif_calls
    make(tp._luu(tp._anh_bon_mau((64, 48)), "JPEG"))
    assert spy.calls == 0 and registered == []
    assert "HEIF" not in Image.OPEN


def test_heic_renamed_jpg_in_folder_rejected_by_content(tmp_path, heic, libheif_calls):
    """Đường thật: file HEIC đổi đuôi .jpg vẫn được liệt kê (theo đuôi), nhưng lúc dựng ảnh xem
    trước, ảnh gửi AI, ảnh gửi WordPress thì bị từ chối theo nội dung."""
    spy, _registered = libheif_calls
    root = tmp_path / "anh"
    (root / "CT012 - Cổng inox - Quận 7").mkdir(parents=True)
    (root / "CT012 - Cổng inox - Quận 7" / "IMG_0001.jpg").write_bytes(heic)
    library = ImageLibrary([root])
    (entry,) = library.list_folder(0, "CT012 - Cổng inox - Quận 7").images
    data = library.read_image_bytes(entry.ref)
    for make in MAKERS:
        with pytest.raises(process.ImageProcessError) as info:
            make(data)
        assert str(info.value) == HEIC_OFF
    assert spy.calls == 0


def test_folder_does_not_list_heic(tmp_path, monkeypatch):
    root = tmp_path / "anh"
    root.mkdir()
    all_names = ["IMG_0001.HEIC", "IMG_0002.heic", "IMG_0003.heif", "IMG_0004.HEIF", "a.jpg"]
    for name in all_names:
        (root / name).write_bytes(b"x")
    names = [e.name for e in ImageLibrary([root]).list_folder(0, "").images]
    assert names == ["a.jpg"]
    monkeypatch.setattr(folders, "HEIC_ENABLED", True)  # bật lại thì liệt kê như cũ
    names = [e.name for e in ImageLibrary([root]).list_folder(0, "").images]
    assert sorted(names) == all_names


def _ftyp(major: bytes, *compatible: bytes) -> bytes:
    body = b"ftyp" + major + b"\x00\x00\x00\x00" + b"".join(compatible)
    return (len(body) + 4).to_bytes(4, "big") + body + b"\x00" * 64


@pytest.mark.parametrize(
    ("data", "is_heic"),
    [
        (_ftyp(b"heic", b"mif1", b"heic"), True),  # iPhone
        (_ftyp(b"mif1", b"mif1", b"heic"), True),  # nhãn HEIC nằm ở nhãn tương thích
        (_ftyp(b"heix", b"mif1"), True),
        (_ftyp(b"hevc", b"msf1"), True),
        (_ftyp(b"avif", b"avif", b"mif1", b"miaf"), False),
        (_ftyp(b"mif1", b"mif1", b"miaf"), False),
        (b"\xff\xd8\xff\xe0" + b"\x00" * 60, False),  # JPEG
        (b"\x89PNG\r\n\x1a\n" + b"\x00" * 60, False),
        (b"\x00\x00\x00\x18ftyp", False),  # cụt
        (b"\xff\xff\xff\xffftypheic" + b"\x00" * 8, True),  # cỡ hộp khai bừa vẫn không đọc quá
    ],
    ids=["iphone", "mif1-heic", "heix", "hevc", "avif", "mif1", "jpeg", "png", "cut", "co-bua"],
)
def test_heic_container_detection(data, is_heic):
    assert process._is_heic_container(data) is is_heic


def test_avif_still_gets_not_image_message():
    with pytest.raises(process.ImageProcessError) as info:
        process.make_preview(_ftyp(b"avif", b"avif", b"mif1", b"miaf"))
    assert str(info.value) == process._MSG_NOT_IMAGE


def test_switching_on_reopens_heic_path(heic, monkeypatch):
    """Bật công tắc (như khi nâng thư viện) là đường HEIC chạy lại, vẫn giải mã một luồng."""
    monkeypatch.setattr(folders, "HEIC_ENABLED", True)
    assert process.open_image(heic).size == (48, 64)  # xoay 6
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile
    assert pillow_heif.options.DECODE_THREADS == 0

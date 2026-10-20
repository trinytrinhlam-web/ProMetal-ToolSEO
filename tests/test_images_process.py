"""T-049: xử lý ảnh (xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch, ảnh xem trước) và tên file.

Mọi ảnh trong test là ảnh giả tạo ngay trong bộ nhớ hoặc thư mục tạm (không commit ảnh thật,
không gọi mạng). Tọa độ GPS là tọa độ giả.
"""

import ast
import io
import os
import random
import re
import shutil
import struct
import subprocess
import warnings
import zlib
from fractions import Fraction
from pathlib import Path

import PIL
import pillow_heif
import pytest
from PIL import ExifTags, Image, ImageOps, PngImagePlugin
from PIL import features as pil_features
from PIL.TiffImagePlugin import IFDRational
from pillow_heif import options as heif_options
from streamlit.testing.v1 import AppTest

from seo_app.config import PROJECT_ROOT
from seo_app.images import naming, process
from seo_app.images.folders import ImageLibrary, ImageRef

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@pytest.fixture(autouse=True)
def _pillow_state_restored():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif sau mỗi test.

    Module ảnh đăng ký HEIF khi mở ảnh lần đầu; không trả lại thì test "chưa đăng ký" của T-047
    (``tests/test_pillow_heif_setup.py``) sẽ bị bỏ qua khi chạy sau file này.
    """
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _PILLOW_REGISTRIES}
    options = {name: getattr(heif_options, name) for name in _HEIF_OPTIONS}
    yield
    for name, value in saved.items():
        current = getattr(Image, name)
        current.clear()
        if isinstance(current, dict):
            current.update(value)
        else:
            current.extend(value)
    for name, value in options.items():
        setattr(heif_options, name, value)

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


# ----- dữ liệu giả ---------------------------------------------------------------------------

R = IFDRational
GPS_LAT = (R(16, 1), R(3, 1), R(1959, 100))  # 16°03'19,59" (giả)
GPS_LON = (R(108, 1), R(12, 1), R(792, 100))  # 108°12'07,92" (giả)
GPS_ALT = R(1234, 100)
# GPS mong đợi sau khi nén, so theo giá trị (phân số), không theo cách viết trong file.
GPS_MONG_DOI = {
    0: b"\x02\x02\x00\x00",
    1: "N",
    2: (Fraction(16), Fraction(3), Fraction(1959, 100)),
    3: "E",
    4: (Fraction(108), Fraction(12), Fraction(792, 100)),
    5: b"\x00",
    6: Fraction(1234, 100),
    7: (Fraction(3), Fraction(15), Fraction(20)),
    29: "2026:10:01",
}
BI_MAT = (
    b"SERIAL-BODY-123",
    b"SERIAL-LENS-456",
    b"Nguyen Van Chu May",
    b"MAKERNOTE-RIENG",
    b"Tac Gia Anh",
    b"PHAN-MEM-SUA",
    b"XMP-BI-MAT",
    b"CHU-THICH-BI-MAT",
    b"ANH-NHO-IFD1",
    b"PHOTOSHOP-IPTC",
    b"APP15-RIENG",
    b"PNG-TEXT-BI-MAT",
    b"PNG-ITXT-BI-MAT",
    b"PNG-ZTXT-BI-MAT",
    b"GPS-PROCESSING",
)
XMP = (
    b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF><rdf:Description '
    b'xmlns:exif="http://ns.adobe.com/exif/1.0/" exif:GPSLatitude="16,3.3265N">XMP-BI-MAT'
    b"</rdf:Description></rdf:RDF></x:xmpmeta>"
)
MAU = {"TL": (220, 30, 30), "TR": (30, 200, 30), "BL": (30, 30, 220), "BR": (230, 220, 30)}


def _anh_bon_mau(size=(400, 300), mode="RGB"):
    """Ảnh 4 góc 4 màu, để biết ảnh đã xoay/lật đúng chưa."""
    w, h = size
    image = Image.new("RGB", size)
    image.paste(MAU["TL"], (0, 0, w // 2, h // 2))
    image.paste(MAU["TR"], (w // 2, 0, w, h // 2))
    image.paste(MAU["BL"], (0, h // 2, w // 2, h))
    image.paste(MAU["BR"], (w // 2, h // 2, w, h))
    return image.convert(mode) if mode != "RGB" else image


def _exif_day_du(orientation=1, *, gps=True):
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "Apple"
    exif[ExifTags.Base.Model] = "iPhone 15 Pro"
    exif[ExifTags.Base.Orientation] = orientation
    exif[ExifTags.Base.DateTime] = "2026:10:01 10:15:20"
    exif[ExifTags.Base.Artist] = "Tac Gia Anh"
    exif[ExifTags.Base.Software] = "PHAN-MEM-SUA"
    sub = exif.get_ifd(ExifTags.IFD.Exif)
    sub[ExifTags.Base.DateTimeOriginal] = "2026:10:01 10:15:20"
    sub[ExifTags.Base.OffsetTimeOriginal] = "+07:00"
    sub[ExifTags.Base.BodySerialNumber] = "SERIAL-BODY-123"
    sub[ExifTags.Base.LensSerialNumber] = "SERIAL-LENS-456"
    sub[ExifTags.Base.CameraOwnerName] = "Nguyen Van Chu May"
    sub[ExifTags.Base.MakerNote] = b"MAKERNOTE-RIENG" * 8
    if gps:
        g = exif.get_ifd(ExifTags.IFD.GPSInfo)
        g[0] = b"\x02\x02\x00\x00"
        g[1], g[2], g[3], g[4] = "N", GPS_LAT, "E", GPS_LON
        g[5], g[6] = b"\x00", GPS_ALT
        g[7] = (R(3, 1), R(15, 1), R(20, 1))
        g[27] = b"ASCII\x00\x00\x00GPS-PROCESSING"
        g[29] = "2026:10:01"
    return exif


def _them_ifd1(exif_bytes, thumbnail=b"\xff\xd8ANH-NHO-IFD1\xff\xd9"):
    """Gắn thêm IFD1 (ảnh nhỏ nhúng trong EXIF) vào EXIF do Pillow tạo (Pillow không tự ghi)."""
    assert exif_bytes.startswith(b"Exif\x00\x00MM")
    tiff = bytearray(exif_bytes[6:])
    count = int.from_bytes(tiff[8:10], "big")
    next_pointer = 8 + 2 + 12 * count
    assert tiff[next_pointer : next_pointer + 4] == b"\x00\x00\x00\x00"
    if len(tiff) % 2:
        tiff += b"\x00"
    ifd1 = len(tiff)
    thumb_at = ifd1 + 2 + 3 * 12 + 4
    tiff[next_pointer : next_pointer + 4] = ifd1.to_bytes(4, "big")
    tiff += (3).to_bytes(2, "big")
    tiff += struct.pack(">HHIHH", 0x0103, 3, 1, 6, 0)
    tiff += struct.pack(">HHII", 0x0201, 4, 1, thumb_at)
    tiff += struct.pack(">HHII", 0x0202, 4, 1, len(thumbnail))
    tiff += b"\x00\x00\x00\x00" + thumbnail
    return b"Exif\x00\x00" + bytes(tiff)


def _chen_khoi_jpeg(data, *segments):
    """Chèn khối JPEG thô ngay sau SOI."""
    raw = b"".join(
        bytes([0xFF, marker]) + (len(body) + 2).to_bytes(2, "big") + body
        for marker, body in segments
    )
    return data[:2] + raw + data[2:]


def _jpeg_day_du(size=(400, 300), orientation=1, *, gps=True, icc=None):
    """JPEG có đủ: EXIF (GPS, số seri, MakerNote, IFD1), XMP, chú thích COM, APP13, APP15."""
    params = {
        "exif": _them_ifd1(_exif_day_du(orientation, gps=gps).tobytes()),
        "comment": b"CHU-THICH-BI-MAT",
        "xmp": XMP,
        "quality": 92,
    }
    if icc:
        params["icc_profile"] = icc
    return _chen_khoi_jpeg(
        _luu(_anh_bon_mau(size), "JPEG", **params),
        (0xED, b"Photoshop 3.0\x00PHOTOSHOP-IPTC"),
        (0xEF, b"APP15-RIENG"),
    )


def _png_chunk(name, body):
    return struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body))


def _png_day_du(size=(64, 48), mode="RGBA"):
    info = PngImagePlugin.PngInfo()
    info.add_text("Comment", "PNG-TEXT-BI-MAT")
    info.add_itxt("XML:com.adobe.xmp", XMP.decode())
    info.add_itxt("Author", "PNG-ITXT-BI-MAT")
    info.add_text("Description", "PNG-ZTXT-BI-MAT", zip=True)
    return _luu(
        _anh_bon_mau(size, mode),
        "PNG",
        pnginfo=info,
        exif=_exif_day_du(6).tobytes(),
        icc_profile=_icc_srgb(),
    )


def _heic(size=(64, 48), orientation=1, *, noise=False, metadata=True):
    image = Image.effect_noise(size, 60).convert("RGB") if noise else _anh_bon_mau(size)
    params = {"exif": _exif_day_du(orientation).tobytes(), "xmp": XMP} if metadata else {}
    buffer = io.BytesIO()
    pillow_heif.from_pillow(image).save(buffer, quality=90, **params)
    return buffer.getvalue()


def _icc_srgb():
    from PIL import ImageCms

    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def _luu(image, fmt, **params):
    buffer = io.BytesIO()
    image.save(buffer, fmt, **params)
    return buffer.getvalue()


def _mo(data):
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def _gia_tri(value):
    if isinstance(value, IFDRational):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, tuple):
        return tuple(_gia_tri(v) for v in value)
    return value


def _gps_doc_lai(data):
    """GPS đọc độc lập bằng Pillow (không dùng hàm của module), theo giá trị."""
    exif = _mo(data).getexif()
    return {tag: _gia_tri(v) for tag, v in exif.get_ifd(ExifTags.IFD.GPSInfo).items()}


def _webp_chunks(data):
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    names, pos = [], 12
    while pos < len(data):
        size = int.from_bytes(data[pos + 4 : pos + 8], "little")
        names.append(data[pos : pos + 4])
        pos += 8 + size + (size & 1)
    assert pos == len(data)
    return names


def _jpeg_segments(data):
    """Liệt kê khối JPEG tới SOS (độc lập với ``process.jpeg_layout``)."""
    assert data[:2] == b"\xff\xd8"
    names, pos = [], 2
    while True:
        marker = data[pos + 1]
        length = int.from_bytes(data[pos + 2 : pos + 4], "big")
        names.append((marker, data[pos + 4 : pos + 4 + min(length - 2, 5)]))
        pos += 2 + length
        if marker == 0xDA:
            return names


def _mau_gan(a, b, sai=45):
    return all(abs(x - y) <= sai for x, y in zip(a[:3], b[:3], strict=True))


def _bon_goc(image):
    w, h = image.size
    image = image.convert("RGB")
    diem = ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75))
    return [image.getpixel((int(w * x), int(h * y))) for x, y in diem]


CAU_LOI_CO_DINH = {
    process._MSG_OLD_PILLOW,
    process._MSG_EMPTY,
    process._MSG_NOT_IMAGE,
    process._MSG_BROKEN,
    process._MSG_ENCODE,
    process._MSG_GPS_LOST,
}


def _loi(func, *args, **kwargs):
    with pytest.raises(process.ImageProcessError) as info:
        func(*args, **kwargs)
    # Không chép câu lỗi gốc (có thể chứa đường dẫn): ngoại lệ gốc bị cắt khỏi chuỗi lỗi.
    assert info.value.__cause__ is None
    assert info.value.__suppress_context__ or info.value.__context__ is None
    return str(info.value)


# ----- mở ảnh an toàn ------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ham", [process.open_image, process.make_web_image, process.make_ai_image, process.make_preview]
)
def test_tu_choi_khi_pillow_duoi_13(monkeypatch, ham):
    # LC-T058-3: quay về Pillow 12.x thì báo câu cố định, không xử lý ảnh.
    data = _luu(_anh_bon_mau(), "JPEG")
    monkeypatch.setattr(PIL, "__version__", "12.3.0")
    assert _loi(ham, data) == process._MSG_OLD_PILLOW
    monkeypatch.setattr(PIL, "__version__", "13.0.0")
    ham(data)


def test_dang_ky_heif_mot_cho_tat_anh_phu():
    heif_options.THUMBNAILS = True  # ai đó bật lại: lần mở sau đặt lại
    heif_options.DEPTH_IMAGES = True
    process.make_preview(_heic())
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile
    assert heif_options.THUMBNAILS is False
    assert heif_options.DEPTH_IMAGES is False
    assert heif_options.AUX_IMAGES is False
    assert heif_options.DISABLE_SECURITY_LIMITS is False


def _ma_nguon_khong_chu_thich(path):
    """Mã nguồn đã bỏ docstring và chú thích (để dò lệnh thật, không dò lời giải thích)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
        ):
            body.pop(0)
    return ast.unparse(tree)


def test_ma_nguon_dang_ky_heif_mot_cho_khong_arrow_khong_alignment():
    seo_app = PROJECT_ROOT / "seo_app"
    goi_dang_ky = []
    for path in sorted(seo_app.rglob("*.py")):
        code = _ma_nguon_khong_chu_thich(path)
        goi_dang_ky += [path.name] * code.count("register_heif_opener(")
        assert "load_libheif_plugin" not in code
        assert "DISABLE_SECURITY_LIMITS = True" not in code
        # LC-T058-1: không xuất ảnh sang Arrow, không đặt/đọc PILLOW_ALIGNMENT.
        for chu in ("__arrow_c_array__", "__arrow_c_schema__", "fromarrow", "pyarrow"):
            assert chu not in code, (path.name, chu)
        assert "PILLOW_ALIGNMENT" not in code, path.name
    assert goi_dang_ky == ["process.py"]
    code = _ma_nguon_khong_chu_thich(seo_app / "images" / "process.py")
    # Không ghi file HEIC; "MPO" chỉ dùng để nhận diện ảnh đã mở, không có trong ``formats``.
    assert ", 'HEIF'" not in code.replace("('JPEG', 'PNG', 'WEBP', 'HEIF')", "")
    assert "MPO" not in code.replace("('JPEG', 'MPO')", "")


def test_mo_anh_chi_voi_bon_dinh_dang(monkeypatch):
    goi = []
    mo_that = Image.open

    def mo_gian_diep(fp, mode="r", formats=None):
        goi.append(formats)
        return mo_that(fp, mode, formats)

    monkeypatch.setattr(Image, "open", mo_gian_diep)
    process.make_ai_image(_luu(_anh_bon_mau(), "PNG"))
    assert goi[0] == ["JPEG", "PNG", "WEBP", "HEIF"]
    assert all("MPO" not in f for f in goi)


@pytest.mark.parametrize("dinh_dang", ["BMP", "GIF", "TIFF", "ICO", "PPM", "TGA"])
def test_dinh_dang_khac_bi_tu_choi_theo_noi_dung(dinh_dang):
    data = _luu(_anh_bon_mau((32, 32)), dinh_dang)
    assert _loi(process.make_web_image, data) == process._MSG_NOT_IMAGE


@pytest.mark.skipif(not pil_features.check("avif"), reason="Pillow không có AVIF")
def test_avif_bi_tu_choi():
    data = _luu(_anh_bon_mau((32, 32)), "AVIF")
    assert _loi(process.make_ai_image, data) == process._MSG_NOT_IMAGE


@pytest.mark.parametrize(
    "data", [b"<?php system($_GET['c']); ?>", b"\x89PNG\r\n\x1a\n" + b"\x00" * 40, b"\xff\xd8\xff"]
)
def test_file_gia_anh_bi_tu_choi(data):
    assert _loi(process.make_preview, data) in {process._MSG_NOT_IMAGE, process._MSG_BROKEN}


def test_kiem_dung_luong_truoc_khi_mo(monkeypatch):
    goi = []
    monkeypatch.setattr(Image, "open", lambda *a, **k: goi.append(1))
    monkeypatch.setattr(process, "MAX_IMAGE_BYTES", 1000)
    cau = _loi(process.make_web_image, b"\xff\xd8" + b"\x00" * 999)
    assert cau.startswith("Ảnh quá lớn") and "tối đa 0,0 MB" in cau
    assert _loi(process.make_web_image, b"") == process._MSG_EMPTY
    assert goi == []


@pytest.mark.parametrize("sai", ["anh.jpg", Path("anh.jpg"), None, 123])
def test_khong_nhan_duong_dan_chi_nhan_byte(sai):
    # Byte ảnh phải lấy qua ImageLibrary.read_image_bytes; module không tự mở đường dẫn.
    assert _loi(process.make_web_image, sai) == process._MSG_NOT_IMAGE


def _png_khai_lon_du_lieu_hong(width, height):
    head = b"\x89PNG\r\n\x1a\n" + _png_chunk(
        b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    )
    return head + _png_chunk(b"IDAT", b"khong-phai-zlib") + _png_chunk(b"IEND", b"")


@pytest.mark.parametrize("dinh_dang", ["PNG", "JPEG", "WEBP", "HEIF"])
def test_qua_so_diem_anh_bi_chan_truoc_khi_giai_ma(monkeypatch, dinh_dang):
    monkeypatch.setattr(process, "MAX_IMAGE_PIXELS", 1000)
    if dinh_dang == "PNG":
        data = _png_khai_lon_du_lieu_hong(100, 100)  # giải mã là hỏng ngay
    elif dinh_dang == "HEIF":
        full = _heic((256, 192), noise=True, metadata=False)
        data = full[: int(len(full) * 0.7)]  # HEIC cụt: chỉ hỏng lúc load (ValueError)
    else:
        full = _luu(Image.effect_noise((64, 64), 60).convert("RGB"), dinh_dang)
        data = full[: len(full) // 2]
    # Câu "quá nhiều điểm ảnh" (không phải "ảnh hỏng"): đã chặn trước khi giải mã.
    assert "quá nhiều điểm ảnh" in _loi(process.make_web_image, data)


@pytest.mark.parametrize("loai", ["VP8X", "VP8L", "VP8 "])
def test_webp_khai_khung_lon_bi_chan_truoc_khi_tao_bo_giai_ma(monkeypatch, loai):
    # Pillow tạo bộ giải mã WebP (cấp bộ nhớ cả khung) ngay lúc mở, chỉ chặn khi vượt gấp đôi
    # giới hạn chung: 10000 × 9000 = 90 triệu điểm ảnh lọt qua Pillow nhưng phải bị app chặn.
    goi = []
    monkeypatch.setattr(Image, "open", lambda *a, **k: goi.append(1))
    w, h = (10000, 9000) if loai == "VP8X" else (9999, 9000)
    if loai == "VP8X":
        body = b"\x00" * 4 + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")
    elif loai == "VP8L":
        body = b"\x2f" + ((w - 1) | ((h - 1) << 14)).to_bytes(4, "little") + b"\x00" * 5
    else:
        body = b"\x00\x00\x00\x9d\x01\x2a" + w.to_bytes(2, "little") + h.to_bytes(2, "little")
    data = b"WEBP" + loai.encode() + len(body).to_bytes(4, "little") + body
    data = b"RIFF" + len(data).to_bytes(4, "little") + data
    assert "quá nhiều điểm ảnh (90 triệu)" in _loi(process.make_preview, data)
    assert goi == []


@pytest.mark.parametrize(
    ("mode", "params"),
    [("RGB", {}), ("RGB", {"lossless": True}), ("RGBA", {}), ("RGB", {"exif": b"Exif\x00\x00"})],
)
def test_doc_kich_thuoc_webp_dung_voi_file_that(mode, params):
    data = _luu(Image.new(mode, (321, 123)), "WEBP", **params)
    assert process._webp_canvas_pixels(data) == 321 * 123
    assert process._webp_canvas_pixels(b"RIFF\x00\x00\x00\x00WEBPXXXX" + b"\x00" * 20) is None


@pytest.mark.parametrize("dinh_dang", ["PNG", "HEIF"])
def test_canh_bao_bom_giai_nen_cua_pillow_thanh_loi(monkeypatch, dinh_dang):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1000)
    monkeypatch.setattr(process, "MAX_IMAGE_PIXELS", 10**9)
    for size in ((40, 30), (50, 50)):  # vượt 1 lần: cảnh báo; vượt 2 lần: DecompressionBombError
        image = _anh_bon_mau(size)
        if dinh_dang == "HEIF":
            buffer = io.BytesIO()
            pillow_heif.from_pillow(image).save(buffer, quality=80)
            data = buffer.getvalue()
        else:
            data = _luu(image, "PNG")
        bo_loc = list(warnings.filters)
        assert "quá nhiều điểm ảnh" in _loi(process.make_ai_image, data)
        assert list(warnings.filters) == bo_loc  # không để lại bộ lọc cảnh báo


def test_khong_doi_gioi_han_chung_cua_pillow():
    # Giữ test T-058 (``test_gioi_han_bom_giai_nen_mac_dinh_khong_doi``) đúng sau khi app chạy.
    process.make_web_image(_jpeg_day_du())
    assert Image.MAX_IMAGE_PIXELS == 89_478_485
    assert process.MAX_IMAGE_PIXELS < Image.MAX_IMAGE_PIXELS


def test_jpeg_png_cut_bao_anh_hong():
    for fmt in ("JPEG", "PNG"):
        full = _luu(Image.effect_noise((128, 96), 60).convert("RGB"), fmt)
        assert _loi(process.make_preview, full[: len(full) // 2]) == process._MSG_BROKEN


def test_heic_cut_chi_hong_luc_load_van_bat_duoc():
    # Soi Lỗi T-047: HEIC cụt mở được, chỉ nổ ``ValueError`` ở ``load``.
    full = _heic((256, 192), noise=True, metadata=False)
    assert _loi(process.make_web_image, full[: int(len(full) * 0.7)]) == process._MSG_BROKEN


def test_mpo_chi_dung_khung_dau(monkeypatch):
    from PIL import MpoImagePlugin

    data = _luu(
        _anh_bon_mau((64, 48)),
        "MPO",
        save_all=True,
        append_images=[Image.new("RGB", (64, 48), "green")],
    )
    assert _mo(data).format == "MPO"
    seek_that = MpoImagePlugin.MpoImageFile.seek

    def seek_chi_khung_dau(self, frame):
        assert frame == 0, "không được sang khung thứ hai"
        return seek_that(self, frame)

    monkeypatch.setattr(MpoImagePlugin.MpoImageFile, "seek", seek_chi_khung_dau)
    web = _mo(process.make_web_image(data).data)
    assert _mau_gan(_bon_goc(web)[0], MAU["TL"])
    assert getattr(web, "n_frames", 1) == 1


# ----- ảnh đăng web: xoay, thu nhỏ, EXIF, GPS ---------------------------------------------


@pytest.mark.parametrize("orientation", range(1, 9))
def test_xoay_dung_chieu_ca_8_huong(orientation):
    data = _jpeg_day_du((400, 300), orientation)
    mong_doi = ImageOps.exif_transpose(_mo(data))
    web = _mo(process.make_web_image(data).data)
    assert web.size == mong_doi.size
    for thuc, dung in zip(_bon_goc(web), _bon_goc(mong_doi), strict=True):
        assert _mau_gan(thuc, dung)
    assert web.getexif()[ExifTags.Base.Orientation] == 1


@pytest.mark.parametrize(
    ("size", "orientation", "canh", "mong_doi"),
    [
        ((4000, 3000), 1, 1600, (1600, 1200)),
        ((4000, 3000), 6, 1600, (1200, 1600)),
        ((3000, 4000), 1, 1600, (1200, 1600)),
        ((800, 600), 1, 1600, (800, 600)),  # không phóng to
        ((4000, 3000), 8, 1000, (750, 1000)),
    ],
)
def test_thu_canh_dai_khong_phong_to(size, orientation, canh, mong_doi):
    web = process.make_web_image(_jpeg_day_du(size, orientation), max_edge_px=canh)
    assert (web.width, web.height) == mong_doi
    anh = _mo(web.data)
    assert anh.format == "WEBP" and anh.size == mong_doi
    assert _gps_doc_lai(web.data) == GPS_MONG_DOI


def test_f2_webp_con_gps_dung_tung_gia_tri():
    """F2 (bắt buộc): ảnh đăng web còn đúng vị trí GPS của ảnh gốc sau khi nén."""
    data = _jpeg_day_du((1200, 900), 6)
    goc = _gps_doc_lai(data)
    web = process.make_web_image(data)
    assert b"EXIF" in _webp_chunks(web.data)
    ra = _gps_doc_lai(web.data)
    assert ra == {tag: value for tag, value in goc.items() if tag != 27}
    assert ra == GPS_MONG_DOI
    assert web.has_gps
    assert web.gps == process.GpsCoordinates(latitude=16.0554417, longitude=108.2022)
    assert web.notice == ""


def test_2a_giu_ngay_hang_doi_may_bo_seri_chu_may_makernote_ifd1():
    data = _jpeg_day_du()
    goc = _mo(data).getexif()
    assert goc.get_ifd(ExifTags.IFD.IFD1)  # ảnh gốc có ảnh nhỏ IFD1 thật
    assert goc.get_ifd(ExifTags.IFD.Exif)[ExifTags.Base.BodySerialNumber] == "SERIAL-BODY-123"
    web = process.make_web_image(data)
    exif = _mo(web.data).getexif()
    assert {k: v for k, v in exif.items() if k not in (34665, 34853)} == {
        ExifTags.Base.Make: "Apple",
        ExifTags.Base.Model: "iPhone 15 Pro",
        ExifTags.Base.Orientation: 1,
        ExifTags.Base.DateTime: "2026:10:01 10:15:20",
    }
    assert exif.get_ifd(ExifTags.IFD.Exif) == {
        ExifTags.Base.DateTimeOriginal: "2026:10:01 10:15:20",
        ExifTags.Base.OffsetTimeOriginal: "+07:00",
    }
    assert exif.get_ifd(ExifTags.IFD.IFD1) == {}
    for bi_mat in BI_MAT:
        assert bi_mat not in web.data, bi_mat
    assert set(_webp_chunks(web.data)) <= {b"VP8X", b"VP8 ", b"VP8L", b"ALPH", b"EXIF", b"ICCP"}


def test_kiem_gps_sau_nen_bat_duoc_khi_quen_chep_exif(monkeypatch):
    # Thiết kế T-046 thử 2: quên tham số ``exif=`` là mất GPS. Lớp kiểm sau nén phải bắt được.
    data = _jpeg_day_du()
    luu_that = Image.Image.save

    def luu_quen_exif(self, fp, format=None, **params):
        params.pop("exif", None)
        return luu_that(self, fp, format, **params)

    monkeypatch.setattr(Image.Image, "save", luu_quen_exif)
    assert _loi(process.make_web_image, data) == process._MSG_GPS_LOST


def test_kiem_gps_sau_nen_so_gia_tri_khong_chi_co_the(monkeypatch):
    # Góp ý Lá Chắn T-046 số 2: còn thẻ GPS nhưng sai giá trị cũng phải dừng.
    data = _jpeg_day_du()
    to_bytes_that = process._KeptExif.to_bytes

    def lech_vi_do(self):
        gps = dict(self.gps)
        gps[ExifTags.GPS.GPSLatitude] = (R(16, 1), R(3, 1), R(1960, 100))
        return to_bytes_that(process._KeptExif(self.base, self.exif, gps))

    monkeypatch.setattr(process._KeptExif, "to_bytes", lech_vi_do)
    assert _loi(process.make_web_image, data) == process._MSG_GPS_LOST


def test_anh_chup_man_hinh_khong_exif_van_chay():
    # Yêu cầu 7: ảnh chụp màn hình PNG trong suốt, không EXIF.
    image = Image.new("RGBA", (1920, 1080), (40, 90, 200, 255))
    image.paste((0, 0, 0, 0), (0, 0, 200, 200))
    web = process.make_web_image(_luu(image, "PNG"))
    assert (web.width, web.height) == (1600, 900)
    assert web.gps is None and web.notice == ""
    assert b"EXIF" not in _webp_chunks(web.data)
    anh = _mo(web.data)
    assert anh.mode == "RGBA" and anh.getpixel((5, 5))[3] == 0
    assert not anh.getexif()
    jpeg = process.make_web_image(_luu(_anh_bon_mau(), "JPEG"))
    assert jpeg.gps is None and b"EXIF" not in _webp_chunks(jpeg.data)


def test_png_co_exif_gps_va_chunk_chu():
    data = _png_day_du()
    assert _mo(data).info.get("Comment") == "PNG-TEXT-BI-MAT"
    web = process.make_web_image(data)
    assert _gps_doc_lai(web.data) == GPS_MONG_DOI
    assert (web.width, web.height) == (48, 64)  # Orientation 6 trong eXIf
    for bi_mat in BI_MAT:
        assert bi_mat not in web.data


def test_f2_heic_co_gps_giu_gps_xoay_mot_lan():
    data = _heic((64, 48), orientation=6)
    web = process.make_web_image(data)
    assert _gps_doc_lai(web.data) == GPS_MONG_DOI
    # pillow-heif đã xoay theo khung irot và đặt Orientation = 1: app không xoay thêm lần nữa.
    mong_doi = _anh_bon_mau((64, 48)).transpose(Image.Transpose.ROTATE_270)
    anh = _mo(web.data)
    assert anh.size == (48, 64)
    for thuc, dung in zip(_bon_goc(anh), _bon_goc(mong_doi), strict=True):
        assert _mau_gan(thuc, dung)
    for bi_mat in BI_MAT:
        assert bi_mat not in web.data


def test_webp_dau_vao_co_gps():
    data = _luu(_anh_bon_mau(), "WEBP", exif=_exif_day_du(3).tobytes(), xmp=XMP)
    web = process.make_web_image(data)
    assert _gps_doc_lai(web.data) == GPS_MONG_DOI
    assert b"XMP " not in _webp_chunks(web.data)


def _jpeg_voi_exif_tho(exif_bytes):
    return _luu(_anh_bon_mau((64, 48)), "JPEG", exif=exif_bytes)


def test_exif_hong_van_xu_ly_duoc_va_bao_cho_nguoi_dung():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Pillow cảnh báo "Corrupt EXIF data"
        rac = process.make_web_image(_jpeg_voi_exif_tho(b"Exif\x00\x00MM\x00*\x00\x00\x00\x08\xff"))
    assert rac.gps is None

    exif = _exif_day_du()
    exif.get_ifd(ExifTags.IFD.GPSInfo)[2] = (R(16, 1), R(3, 1))  # vĩ độ thiếu giây: sai khuôn
    web = process.make_web_image(_jpeg_voi_exif_tho(exif.tobytes()))
    assert web.gps is None
    assert web.notice == process._NOTICE_GPS_BROKEN
    assert _gps_doc_lai(web.data) == {}
    assert _mo(web.data).getexif()[ExifTags.Base.Make] == "Apple"  # phần còn lại vẫn giữ


def test_exif_hong_ngau_nhien_khong_lam_sap():
    base = _exif_day_du().tobytes()
    rng = random.Random(49)
    loi = set()
    co_gps = 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for _ in range(150):
            data = bytearray(base)
            for _ in range(rng.randint(1, 6)):
                data[rng.randrange(6, len(data))] = rng.randrange(256)
            source = _jpeg_voi_exif_tho(bytes(data))
            try:
                web = process.make_web_image(source)
            except process.ImageProcessError as exc:
                loi.add(str(exc))
                continue
            if web.has_gps:
                # Có GPS thì phải đúng từng giá trị GPS đọc được ở ảnh gốc.
                co_gps += 1
                goc = _gps_doc_lai(source)
                ra = _gps_doc_lai(web.data)
                assert ra.items() <= goc.items()
                assert ra[2] == goc[2] and ra[4] == goc[4]
    assert loi <= CAU_LOI_CO_DINH
    assert co_gps > 20


def test_toa_do_nam_tay_am():
    exif = _exif_day_du()
    gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
    gps[1], gps[3] = "S", "W"
    web = process.make_web_image(_jpeg_voi_exif_tho(exif.tobytes()))
    assert web.gps == process.GpsCoordinates(latitude=-16.0554417, longitude=-108.2022)


def test_khoi_gps_khong_co_toa_do_thi_bo_khong_bao_hong():
    # Máy tắt định vị có thể chỉ ghi phiên bản GPS: không có vị trí để giữ, không báo "hỏng".
    exif = _exif_day_du(gps=False)
    exif.get_ifd(ExifTags.IFD.GPSInfo)[0] = b"\x02\x02\x00\x00"
    web = process.make_web_image(_jpeg_voi_exif_tho(exif.tobytes()))
    assert web.gps is None and web.notice == ""
    assert _gps_doc_lai(web.data) == {}


def test_toa_do_ngoai_pham_vi_thi_bo_va_bao():
    exif = _exif_day_du()
    exif.get_ifd(ExifTags.IFD.GPSInfo)[2] = (R(95, 1), R(0, 1), R(0, 1))  # vĩ độ 95°
    web = process.make_web_image(_jpeg_voi_exif_tho(exif.tobytes()))
    assert web.gps is None and web.notice == process._NOTICE_GPS_BROKEN
    assert _gps_doc_lai(web.data) == {}


def test_che_do_mau_va_ho_so_mau():
    icc = _icc_srgb()
    # RGB có hồ sơ màu RGB: ảnh web giữ hồ sơ (màu không lệch), bản AI thì không.
    data = _jpeg_day_du(icc=icc)
    web = process.make_web_image(data)
    assert b"ICCP" in _webp_chunks(web.data)
    assert _mo(web.data).info.get("icc_profile") == icc
    assert "icc_profile" not in _mo(process.make_ai_image(data).data).info
    # CMYK kèm hồ sơ RGB (không khớp): đổi sang RGB, bỏ hồ sơ.
    cmyk = _luu(Image.new("CMYK", (40, 30), (0, 200, 200, 0)), "JPEG", icc_profile=icc)
    web = process.make_web_image(cmyk)
    assert b"ICCP" not in _webp_chunks(web.data)
    assert _mo(web.data).mode == "RGB"
    # Bảng màu có trong suốt, xám, xám + trong suốt, 1 bit.
    p = Image.new("P", (20, 20), 1)
    p.putpalette([255, 0, 0, 0, 255, 0] + [0] * 762)
    p.paste(0, (0, 0, 10, 10))  # màu số 0 là trong suốt
    assert _mo(process.make_web_image(_luu(p, "PNG", transparency=0)).data).mode == "RGBA"
    for mode in ("L", "LA", "1"):
        anh = _mo(process.make_web_image(_luu(Image.new(mode, (20, 20)), "PNG")).data)
        assert anh.mode in ("RGB", "RGBA")


def test_anh_16_bit_doi_ve_8_bit_dung_do_sang():
    # SL-T058-1: xám 16 bit giá trị 40000 phải thành khoảng 156, không bị cắt thành trắng 255.
    data = _luu(Image.new("I;16", (40, 30), 40000), "PNG")
    assert _mo(data).mode == "I;16"
    outputs = (
        process.make_preview(data),
        process.make_ai_image(data).data,
        process.make_web_image(data).data,
    )
    for out in outputs:
        anh = _mo(out)
        assert anh.mode in ("RGB", "RGBA")
        assert abs(anh.getpixel((10, 10))[0] - 156) <= 3


@pytest.mark.parametrize(
    ("ten", "gia_tri"),
    [
        ("webp_quality", 0),
        ("webp_quality", 101),
        ("webp_quality", "80"),
        ("webp_quality", True),
        ("max_edge_px", 0),
        ("max_edge_px", 10_000),
        ("max_edge_px", 1600.0),
    ],
)
def test_cau_hinh_khong_hop_le(ten, gia_tri):
    cau = _loi(process.make_web_image, _luu(_anh_bon_mau(), "JPEG"), **{ten: gia_tri})
    assert ten in cau


def test_chat_luong_webp_mac_dinh_80_va_nhan_tham_so(monkeypatch):
    goi = []
    luu_that = Image.Image.save

    def luu_gian_diep(self, fp, format=None, **params):
        goi.append((format, params.get("quality"), params.get("method")))
        return luu_that(self, fp, format, **params)

    monkeypatch.setattr(Image.Image, "save", luu_gian_diep)
    data = _luu(_anh_bon_mau(), "JPEG")
    process.make_web_image(data)
    process.make_web_image(data, webp_quality=60)
    assert [g for g in goi if g[0] == "WEBP"] == [("WEBP", 80, 6), ("WEBP", 60, 6)]


# ----- bản gửi AI ----------------------------------------------------------------------------


def _kiem_ban_ai_sach(ai):
    assert ai.mime == "image/jpeg"
    khoi = _jpeg_segments(ai.data)
    # Danh sách cho phép (gợi ý SL-T050-2): APP0 JFIF, bảng lượng tử, khung ảnh, bảng mã, SOS.
    assert {marker for marker, _ in khoi} <= {0xE0, 0xDB, 0xC4, 0xC0, 0xC2, 0xDA}, khoi
    assert [marker for marker, _ in khoi].count(0xE0) == 1
    assert next(body for marker, body in khoi if marker == 0xE0) == b"JFIF\x00"
    assert ai.data.endswith(b"\xff\xd9")
    for chu in (b"Exif", b"http://ns.adobe.com", b"ICC_PROFILE", b"Photoshop", *BI_MAT):
        assert chu not in ai.data, chu
    anh = _mo(ai.data)
    assert not anh.getexif()
    assert not {"exif", "xmp", "comment", "icc_profile", "photoshop"} & set(anh.info)
    assert max(anh.size) <= process.AI_MAX_EDGE_PX
    process.jpeg_layout(ai.data)


def test_f2_ban_ai_tu_jpeg_day_du_khong_con_metadata():
    """F2/A3 (bắt buộc): ảnh gốc đủ EXIF + GPS + XMP + COM + APP13 + ICC → bản AI sạch."""
    data = _jpeg_day_du((2000, 1500), 6, icc=_icc_srgb())
    assert {"exif", "xmp", "comment", "icc_profile", "photoshop"} <= set(_mo(data).info)
    ai = process.make_ai_image(data)
    _kiem_ban_ai_sach(ai)
    assert (ai.width, ai.height) == (768, 1024)  # xoay đúng chiều, cạnh dài 1024
    mong_doi = ImageOps.exif_transpose(_mo(data))
    for thuc, dung in zip(_bon_goc(_mo(ai.data)), _bon_goc(mong_doi), strict=True):
        assert _mau_gan(thuc, dung)


def test_f2_ban_ai_tu_png_co_chunk_chu():
    _kiem_ban_ai_sach(process.make_ai_image(_png_day_du()))


def test_f2_ban_ai_tu_heic_co_gps():
    _kiem_ban_ai_sach(process.make_ai_image(_heic()))


def test_ban_ai_tu_webp_co_exif_xmp():
    data = _luu(_anh_bon_mau(), "WEBP", exif=_exif_day_du().tobytes(), xmp=XMP)
    _kiem_ban_ai_sach(process.make_ai_image(data))


def test_ban_ai_anh_trong_suot_lot_nen_trang():
    ai = process.make_ai_image(_luu(Image.new("RGBA", (50, 40), (0, 0, 0, 0)), "PNG"))
    assert _mau_gan(_mo(ai.data).getpixel((5, 5)), (255, 255, 255), sai=5)


def test_ban_ai_bi_chan_neu_pillow_lo_chep_metadata(monkeypatch):
    data = _luu(_anh_bon_mau(), "PNG")
    luu_that = Image.Image.save

    def luu_kem_chu_thich(self, fp, format=None, **params):
        return luu_that(self, fp, format, comment=b"lo-chep", **params)

    monkeypatch.setattr(Image.Image, "save", luu_kem_chu_thich)
    assert _loi(process.make_ai_image, data) == process._MSG_ENCODE


@pytest.mark.parametrize(
    "khoi",
    [
        (0xE1, b"Exif\x00\x00MM"),
        (0xFE, b"chu thich"),
        (0xE2, b"ICC_PROFILE\x00\x01\x01"),
        (0xED, b"Photoshop 3.0\x00"),
        (0xE0, b"JFXX\x00\x10"),
        (0xEB, b"rieng"),
    ],
)
def test_jpeg_layout_tu_choi_khoi_ngoai_danh_sach(khoi):
    sach = process.make_preview(_luu(_anh_bon_mau(), "PNG"))
    process.jpeg_layout(sach)
    with pytest.raises(ValueError):
        process.jpeg_layout(_chen_khoi_jpeg(sach, khoi))
    with pytest.raises(ValueError):
        process.jpeg_layout(sach + b"du-lieu-sau-EOI")
    with pytest.raises(ValueError):
        process.jpeg_layout(sach[:-2] + b"\xff\xfeXX" + sach[-2:])


# ----- ảnh xem trước, st.image -------------------------------------------------------------


def test_anh_xem_truoc_jpeg_khong_metadata_xoay_dung():
    data = _jpeg_day_du((1200, 900), 6)
    preview = process.make_preview(data)
    assert process.jpeg_layout(preview) == (240, 320)
    for bi_mat in (b"Exif", *BI_MAT):
        assert bi_mat not in preview
    # LC-T058-2: luôn là byte do app tạo, kể cả khi ảnh gốc đã là JPEG nhỏ, sạch.
    nho = _luu(_anh_bon_mau((100, 80)), "JPEG")
    assert process.make_preview(nho) != nho


def _trang_anh_xem_truoc(data):
    import streamlit as st

    from seo_app.images import process

    st.image(process.make_preview(data), caption="xem-truoc")


def test_st_image_nhan_anh_xem_truoc():
    at = AppTest.from_function(_trang_anh_xem_truoc, args=(_heic(),)).run(timeout=60)
    assert not at.exception, at.exception
    anh = at.get("image")
    assert len(anh) == 1 and anh[0].captions == ["xem-truoc"]
    assert anh[0].proto.imgs[0].url.endswith(".jpg")


def _thu_vien(tmp_path):
    goc = tmp_path / "anh"
    thu_muc = goc / "CT012 - Cong inox - Tan Phu" / "truoc"
    thu_muc.mkdir(parents=True)
    path = thu_muc / "IMG_0001.jpg"
    path.write_bytes(_jpeg_day_du((800, 600), 6))
    ref = ImageRef(0, "CT012 - Cong inox - Tan Phu/truoc/IMG_0001.jpg")
    return ImageLibrary([goc]), ref, path


def test_cache_mac_dinh_nam_trong_data_da_gitignore():
    assert process.PREVIEW_CACHE_DIR == PROJECT_ROOT / "data" / "image_previews"
    assert process.PreviewCache().enabled
    assert "data/" in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    git = shutil.which("git")
    if git and (PROJECT_ROOT / ".git").exists():
        ket_qua = subprocess.run(
            [git, "check-ignore", "-q", "data/image_previews/abc.jpg"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert ket_qua.returncode == 0


def test_cache_trong_du_an_ngoai_data_thi_khong_ghi(tmp_path):
    thu_muc = PROJECT_ROOT / "seo_app" / "images" / "_t049_khong_duoc_tao"
    cache = process.PreviewCache(thu_muc)
    assert not cache.enabled
    library, ref, _path = _thu_vien(tmp_path)
    assert process.jpeg_layout(cache.get(library, ref))
    assert not thu_muc.exists()


def test_cache_bi_go_khoi_gitignore_thi_khong_ghi(monkeypatch):
    monkeypatch.setattr(process, "_gitignore_lines", lambda: ["data/", "!data/image_previews/"])
    assert not process.PreviewCache().enabled
    monkeypatch.setattr(process, "_gitignore_lines", lambda: [".env"])
    assert not process.PreviewCache().enabled


def test_cache_ghi_doc_lai_va_tao_lai_khi_anh_doi(tmp_path, monkeypatch):
    library, ref, path = _thu_vien(tmp_path)
    cache_dir = tmp_path / "cache"
    cache = process.PreviewCache(cache_dir)
    assert cache.enabled and "cache" not in repr(cache)
    doc = []
    doc_that = ImageLibrary.read_image_bytes

    def doc_gian_diep(self, r):
        doc.append(r)
        return doc_that(self, r)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", doc_gian_diep)
    lan1 = cache.get(library, ref)
    files = list(cache_dir.iterdir())
    assert len(files) == 1 and re.fullmatch(r"[0-9a-f]{64}\.jpg", files[0].name)
    assert files[0].read_bytes() == lan1
    assert cache.get(library, ref) == lan1
    assert doc == [ref]  # lần 2 lấy từ cache, không đọc lại ảnh gốc
    path.write_bytes(_jpeg_day_du((900, 600), 1))
    os.utime(path, (1_800_000_000, 1_800_000_000))
    lan3 = cache.get(library, ref)
    assert lan3 != lan1 and len(doc) == 2
    assert process.jpeg_layout(lan3) == (320, 213)


@pytest.mark.parametrize("hong", ["rac", "jpeg_co_exif", "qua_lon"])
def test_cache_hong_thi_tao_lai(tmp_path, hong):
    library, ref, _path = _thu_vien(tmp_path)
    cache = process.PreviewCache(tmp_path / "cache")
    dung = cache.get(library, ref)
    (file,) = (tmp_path / "cache").iterdir()
    if hong == "jpeg_co_exif":
        file.write_bytes(_jpeg_day_du((100, 80)))
    elif hong == "qua_lon":
        file.write_bytes(process.make_preview(_jpeg_day_du((900, 600)), max_edge_px=900))
    else:
        file.write_bytes(b"rac")
    assert cache.get(library, ref) == dung
    assert file.read_bytes() == dung


def test_ket_qua_khong_in_byte_anh_trong_repr():
    data = _jpeg_day_du()
    assert "data=" not in repr(process.make_web_image(data))
    assert "data=" not in repr(process.make_ai_image(data))

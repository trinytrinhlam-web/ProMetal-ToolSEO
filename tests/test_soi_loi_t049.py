"""Soi Lỗi T-049: xử lý ảnh (xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch, tên file).

Thử thêm ngoài test của Thợ Máy (``tests/test_images_process.py``):

- F2: GPS **đúng từng giá trị** sau nén với JPEG, PNG, WebP, HEIC; 4 cặp bán cầu, độ cao trên và
  dưới mặt biển, EXIF big/little endian, 3 cách viết tọa độ (độ-phút-giây, phút thập phân, độ
  thập phân). Thẻ 2A giữ/bỏ đúng với cả 4 định dạng (kể cả ảnh nhỏ IFD1, chữ tự do của GPS).
- Bản gửi AI: từ mọi loại nguồn (hồ sơ màu chở chữ, CMYK, 16 bit, MPO, WebP động, HEIC trong
  suốt…) đều qua ``prepare_images`` (T-050) và tới đúng 3 hãng (mạng giả) không kèm metadata.
- Mở ảnh an toàn: biên giới hạn điểm ảnh, bom thật (không đổi giới hạn), giả đuôi qua
  ``ImageLibrary``, HEIC cụt ở nhiều điểm cắt, đột biến ngẫu nhiên cả file, xoay 8 hướng với
  PNG/WebP/HEIC, ảnh không EXIF; câu lỗi không lộ đường dẫn.
- Không ``ImageCms``, không Arrow khi chạy thật (bẫy hàm), không đặt ``PILLOW_ALIGNMENT``.
- Điều kiện 6 Lá Chắn T-047: gỡ HEIF khỏi bảng định dạng rồi module ảnh tự đăng ký lại.

Ảnh đều tạo ngay trong test (không có ảnh thật, không gọi mạng; 3 thư viện AI chạy với
``MockTransport`` qua fixture ``network`` của ``test_ai_images``). Tọa độ GPS là tọa độ giả.

Lỗi tìm thấy đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T049-n`` (xem
``docs/team/reports/T-049-soi-loi.md``): sửa xong thì test tự báo XPASS để gỡ dấu.
"""

import base64
import functools
import io
import json
import os
import random
import re
import struct
import threading
import unicodedata
import warnings
import zlib
from fractions import Fraction

import PIL
import pillow_heif
import pytest
from PIL import ExifTags, Image, ImageCms, ImageFile, PngImagePlugin, UnidentifiedImageError
from PIL.TiffImagePlugin import IFDRational as R
from pillow_heif import options as heif_options

from seo_app.ai import AIError
from seo_app.ai.base import ImageInput, prepare_images
from seo_app.images import naming, process
from seo_app.images.folders import ImageLibrary, ImageRef
from tests.test_ai_images import VENDORS, network, run  # noqa: F401  (fixture dùng chung)
from tests.test_images_process import CHU_TRONG_ICC, XMP, _icc_co_chu, _them_ifd1
from tests.test_pillow_heif_setup import _go_heif_khoi_bang

_BANG = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_TUY_CHON_HEIF = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@pytest.fixture(autouse=True)
def _tra_nguyen_trang_pillow():
    """Module ảnh (và test) đăng ký HEIF khi mở ảnh: trả nguyên bảng định dạng sau mỗi test."""
    Image.init()
    bang = {ten: getattr(Image, ten).copy() for ten in _BANG}
    tuy_chon = {ten: getattr(heif_options, ten) for ten in _TUY_CHON_HEIF}
    yield
    for ten, gia_tri in bang.items():
        hien = getattr(Image, ten)
        hien.clear()
        if isinstance(hien, dict):
            hien.update(gia_tri)
        else:
            hien.extend(gia_tri)
    for ten, gia_tri in tuy_chon.items():
        setattr(heif_options, ten, gia_tri)


# ----- dữ liệu giả ---------------------------------------------------------------------------

MAU = [(220, 30, 30), (30, 200, 30), (30, 30, 220), (230, 220, 30)]
# Cùng một vị trí (10°46'34,56" , 106°41'12,3456", giả) viết theo 3 cách máy ảnh hay dùng.
VI_DO = {
    "dms": (R(10, 1), R(46, 1), R(3456, 100)),
    "phut_thap_phan": (R(10, 1), R(465760, 10000), R(0, 1)),
    "do_thap_phan": (R(107762667, 10000000), R(0, 1), R(0, 1)),
}
KINH_DO = {
    "dms": (R(106, 1), R(41, 1), R(123456, 10000)),
    "phut_thap_phan": (R(106, 1), R(4120576, 100000), R(0, 1)),
    "do_thap_phan": (R(1066867627, 10000000), R(0, 1), R(0, 1)),
}
BI_MAT = (
    b"SERIAL-BODY-123",
    b"SERIAL-LENS-456",
    b"Nguyen Van Chu May",
    b"MAKERNOTE-RIENG",
    b"Tac Gia Anh",
    b"PHAN-MEM-SUA",
    b"Nha anh Tuan 12 Le Loi",
    b"BAN-QUYEN-RIENG",
    b"MAY-TINH-RIENG",
    b"BINH-LUAN-RIENG",
    b"MA-ANH-RIENG-0001",
    b"LENS-MODEL-X",
    b"GPS-PROCESSING",
    b"GPS-KHU-VUC",
    b"ANH-NHO-IFD1",
    b"XMP-BI-MAT",
    b"CHU-THICH-BI-MAT",
    b"PNG-TEXT-BI-MAT",
)
# Chuỗi không được có trong bản gửi AI (ngoài các bí mật trên).
DAU_METADATA = (b"Exif", b"ICC_PROFILE", b"acsp", b"<x:xmpmeta", b"http://ns.adobe.com", b"GPS")


def _anh_bon_mau(size=(80, 60), mode="RGB"):
    """Ảnh 4 góc 4 màu, để biết ảnh đã xoay/lật đúng chưa."""
    w, h = size
    image = Image.new("RGB", size)
    image.paste(MAU[0], (0, 0, w // 2, h // 2))
    image.paste(MAU[1], (w // 2, 0, w, h // 2))
    image.paste(MAU[2], (0, h // 2, w // 2, h))
    image.paste(MAU[3], (w // 2, h // 2, w, h))
    return image if mode == "RGB" else image.convert(mode)


def _luu(image, fmt, **params):
    buffer = io.BytesIO()
    if fmt == "HEIF":
        pillow_heif.from_pillow(image).save(buffer, quality=90, **params)
    else:
        image.save(buffer, fmt, **params)
    return buffer.getvalue()


def _mo(data):
    pillow_heif.register_heif_opener()  # để test tự đọc ảnh HEIC gốc (fixture trả lại bảng)
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def _gia_tri(value):
    if isinstance(value, R):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, tuple):
        return tuple(_gia_tri(v) for v in value)
    return value


def _gps(data):
    """GPS đọc độc lập bằng Pillow (không dùng hàm của module), so theo giá trị."""
    exif = _mo(data).getexif()
    return {tag: _gia_tri(v) for tag, v in exif.get_ifd(ExifTags.IFD.GPSInfo).items()}


def _exif_gps(lat_ref="N", lon_ref="E", alt_ref=b"\x00", *, endian=">", kieu="dms"):
    """EXIF có hãng, đời máy, ngày chụp và đủ các thẻ GPS điện thoại hay ghi."""
    exif = Image.Exif()
    if endian == "<":
        exif.endian = "<"
    exif[ExifTags.Base.Make] = "samsung"
    exif[ExifTags.Base.Model] = "SM-S918B"
    exif[ExifTags.Base.DateTime] = "2026:10:01 10:15:20"
    g = exif.get_ifd(ExifTags.IFD.GPSInfo)
    g[0] = b"\x02\x03\x00\x00"
    g[1], g[2], g[3], g[4] = lat_ref, VI_DO[kieu], lon_ref, KINH_DO[kieu]
    g[5], g[6] = alt_ref, R(5321, 1000)
    g[7] = (R(3, 1), R(15, 1), R(2012, 100))
    g[12], g[13] = "K", R(0, 1)
    g[16], g[17] = "T", R(2345678, 10000)
    g[18] = "WGS-84"
    g[23], g[24] = "M", R(1234567, 10000)
    g[29] = "2026:10:01"
    g[31] = R(35, 1)
    return exif


def _nguon(dinh_dang, exif_bytes, size=(64, 48), **params):
    return _luu(_anh_bon_mau(size), dinh_dang, exif=exif_bytes, **params)


def _do(dms):
    return float(dms[0] + dms[1] / 60 + dms[2] / 3600)


def _kiem_toa_do(web, goc):
    """Tọa độ module báo cho người dùng khớp tọa độ tính độc lập từ ảnh gốc (kể cả dấu)."""
    lat = _do(goc[2]) * (-1 if goc[1] == "S" else 1)
    lon = _do(goc[4]) * (-1 if goc[3] == "W" else 1)
    assert web.gps is not None and web.notice == ""
    assert web.gps.latitude == pytest.approx(lat, abs=1e-6)
    assert web.gps.longitude == pytest.approx(lon, abs=1e-6)


def _goc_mau(image):
    w, h = image.size
    image = image.convert("RGB")
    diem = ((0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75))
    return [image.getpixel((int(w * x), int(h * y))) for x, y in diem]


def _mau_gan(a, b, sai=45):
    return all(abs(x - y) <= sai for x, y in zip(a[:3], b[:3], strict=True))


def _loi(func, *args, **kwargs):
    with pytest.raises(process.ImageProcessError) as info:
        func(*args, **kwargs)
    assert info.value.__cause__ is None  # không chép câu lỗi gốc (có thể chứa đường dẫn)
    return str(info.value)


CAU_LOI_CO_DINH = {
    process._MSG_EMPTY,
    process._MSG_NOT_IMAGE,
    process._MSG_BROKEN,
    process._MSG_ENCODE,
    process._MSG_GPS_LOST,
}


def _cau_loi_hop_le(cau):
    return cau in CAU_LOI_CO_DINH or cau.startswith("Ảnh có quá nhiều điểm ảnh")


def _png_chunk(name, body):
    return struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body))


def _png_tay(width, height, bit_depth, color_type, rows):
    """PNG viết tay (Pillow không ghi được PNG màu 16 bit)."""
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(rows))
        + _png_chunk(b"IEND", b"")
    )


@functools.cache
def _heic_nhieu(size=(256, 192)):
    """HEIC nhiễu (đủ dài để cắt ở nhiều chỗ), có EXIF GPS."""
    image = Image.effect_noise(size, 60).convert("RGB")
    return _luu(image, "HEIF", exif=_exif_gps().tobytes())


def _thu_vien(tmp_path, files):
    """Thư mục ảnh giả, tên thư mục kiểu khách hàng (không được lộ trong câu lỗi)."""
    goc = tmp_path / "anh"
    thu_muc = goc / "Nha anh Tuan 12 Le Loi" / "truoc"
    thu_muc.mkdir(parents=True)
    refs = {}
    for ten, data in files.items():
        (thu_muc / ten).write_bytes(data)
        refs[ten] = ImageRef(0, f"Nha anh Tuan 12 Le Loi/truoc/{ten}")
    return ImageLibrary([goc]), refs


# ----- F2: GPS đúng từng giá trị sau nén ---------------------------------------------------


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
@pytest.mark.parametrize("ban_cau", ["NE", "SW", "NW", "SE"])
@pytest.mark.parametrize("do_cao", [b"\x00", b"\x01"], ids=["tren-mat-bien", "duoi-mat-bien"])
def test_f2_gps_dung_tung_gia_tri_moi_dinh_dang_ban_cau_do_cao(dinh_dang, ban_cau, do_cao):
    """F2 (bắt buộc): độ, phút, giây, hướng Bắc/Nam/Đông/Tây, độ cao còn đúng sau khi nén."""
    data = _nguon(dinh_dang, _exif_gps(ban_cau[0], ban_cau[1], do_cao).tobytes())
    goc = _gps(data)
    assert (goc[1], goc[3], goc[5]) == (ban_cau[0], ban_cau[1], do_cao)  # nguồn đúng như dựng
    assert len(goc) == 17
    web = process.make_web_image(data)
    assert _gps(web.data) == goc  # mọi thẻ GPS (đều thuộc danh sách giữ) còn đúng giá trị
    _kiem_toa_do(web, goc)


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
@pytest.mark.parametrize("endian", [">", "<"], ids=["MM", "II"])
@pytest.mark.parametrize("kieu", ["dms", "phut_thap_phan", "do_thap_phan"])
def test_f2_gps_dung_gia_tri_moi_cach_viet_exif(dinh_dang, endian, kieu):
    # Điện thoại Android hay ghi EXIF "II" (little endian); có máy ghi phút hoặc độ thập phân.
    exif = _exif_gps("S", "W", b"\x01", endian=endian, kieu=kieu)
    assert exif.tobytes()[6:8] == (b"II" if endian == "<" else b"MM")
    data = _nguon(dinh_dang, exif.tobytes())
    goc = _gps(data)
    web = process.make_web_image(data)
    assert _gps(web.data) == goc
    _kiem_toa_do(web, goc)
    # Ba cách viết là cùng một vị trí.
    assert web.gps.latitude == pytest.approx(-10.7762667, abs=1e-6)
    assert web.gps.longitude == pytest.approx(-106.6867627, abs=1e-6)


def _exif_2a():
    """EXIF đủ loại thẻ: thẻ 2A giữ và thẻ phải bỏ (số seri, chủ máy, MakerNote, chữ tự do…)."""
    exif = _exif_gps()
    exif[ExifTags.Base.Orientation] = 1
    exif[ExifTags.Base.Artist] = "Tac Gia Anh"
    exif[ExifTags.Base.Software] = "PHAN-MEM-SUA"
    exif[ExifTags.Base.ImageDescription] = "Nha anh Tuan 12 Le Loi"
    exif[ExifTags.Base.Copyright] = "BAN-QUYEN-RIENG"
    exif[ExifTags.Base.HostComputer] = "MAY-TINH-RIENG"
    sub = exif.get_ifd(ExifTags.IFD.Exif)
    sub[ExifTags.Base.DateTimeOriginal] = "2026:10:01 10:15:20"
    sub[ExifTags.Base.DateTimeDigitized] = "2026:10:01 10:15:21"
    sub[ExifTags.Base.OffsetTime] = "+07:00"
    sub[ExifTags.Base.OffsetTimeOriginal] = "+07:00"
    sub[ExifTags.Base.OffsetTimeDigitized] = "+07:00"
    sub[ExifTags.Base.BodySerialNumber] = "SERIAL-BODY-123"
    sub[ExifTags.Base.LensSerialNumber] = "SERIAL-LENS-456"
    sub[ExifTags.Base.CameraOwnerName] = "Nguyen Van Chu May"
    sub[ExifTags.Base.MakerNote] = b"MAKERNOTE-RIENG" * 8
    sub[ExifTags.Base.UserComment] = b"ASCII\x00\x00\x00BINH-LUAN-RIENG"
    sub[ExifTags.Base.ImageUniqueID] = "MA-ANH-RIENG-0001"
    sub[ExifTags.Base.LensModel] = "LENS-MODEL-X"
    g = exif.get_ifd(ExifTags.IFD.GPSInfo)
    g[27] = b"ASCII\x00\x00\x00GPS-PROCESSING"
    g[28] = b"ASCII\x00\x00\x00GPS-KHU-VUC"
    return _them_ifd1(exif.tobytes())


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
def test_2a_giu_bo_dung_the_voi_moi_dinh_dang(dinh_dang):
    """Quyết định 2A với cả HEIC, PNG, WebP (test của Thợ Máy chỉ đếm đủ thẻ với JPEG)."""
    data = _nguon(dinh_dang, _exif_2a())
    goc = _mo(data).getexif()
    assert goc.get_ifd(ExifTags.IFD.IFD1)  # ảnh gốc có ảnh nhỏ IFD1
    assert goc.get_ifd(ExifTags.IFD.Exif)[ExifTags.Base.BodySerialNumber] == "SERIAL-BODY-123"
    web = process.make_web_image(data)
    exif = _mo(web.data).getexif()
    co_so = {k: v for k, v in exif.items() if k not in (ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo)}
    assert co_so == {
        ExifTags.Base.Make: "samsung",
        ExifTags.Base.Model: "SM-S918B",
        ExifTags.Base.Orientation: 1,
        ExifTags.Base.DateTime: "2026:10:01 10:15:20",
    }
    assert exif.get_ifd(ExifTags.IFD.Exif) == {
        ExifTags.Base.DateTimeOriginal: "2026:10:01 10:15:20",
        ExifTags.Base.DateTimeDigitized: "2026:10:01 10:15:21",
        ExifTags.Base.OffsetTime: "+07:00",
        ExifTags.Base.OffsetTimeOriginal: "+07:00",
        ExifTags.Base.OffsetTimeDigitized: "+07:00",
    }
    assert exif.get_ifd(ExifTags.IFD.IFD1) == {}
    goc_gps = _gps(data)
    assert {27, 28} <= set(goc_gps)
    assert _gps(web.data) == {k: v for k, v in goc_gps.items() if k not in (27, 28)}
    for bi_mat in BI_MAT:
        assert bi_mat not in web.data, bi_mat


def test_mpo_giu_gps_khung_dau_ban_ai_sach():
    exif = _exif_gps("N", "E").tobytes()
    data = _luu(
        _anh_bon_mau((64, 48)),
        "MPO",
        save_all=True,
        append_images=[Image.new("RGB", (64, 48), "green")],
        exif=exif,
    )
    assert _mo(data).format == "MPO"
    web = process.make_web_image(data)
    assert _gps(web.data) == _gps(data)
    assert _mau_gan(_goc_mau(_mo(web.data))[0], MAU[0])
    ai = process.make_ai_image(data)
    (gui,) = prepare_images([ImageInput(data=ai.data, mime=ai.mime)])
    assert gui.data == ai.data


def test_anh_dang_web_co_gps_khong_bao_gio_qua_bo_kiem_gui_ai():
    # Đối chứng: bộ kiểm của T-050 chạy thật, bản đăng web (còn GPS) không thể gửi nhầm cho AI.
    web = process.make_web_image(_nguon("JPEG", _exif_gps().tobytes()))
    with pytest.raises(AIError):
        prepare_images([ImageInput(data=web.data, mime=web.mime)])


# SL-T049-1 (GPSLatitudeRef/GPSLongitudeRef chữ thường bị bỏ lặng lẽ, đổi bán cầu): sửa ở T-067.
def test_gps_ref_sai_khuon_khong_lang_le_doi_ban_cau():
    data = _nguon("JPEG", _exif_gps("s", "w").tobytes())
    assert _gps(data)[1] == "s"  # ảnh gốc ghi Nam/Tây bằng chữ thường (sai chuẩn EXIF)
    web = process.make_web_image(data)
    # Chấp nhận một trong hai cách: giữ đúng bán cầu, hoặc bỏ GPS và báo "GPS hỏng".
    giu_dung = (
        web.gps is not None
        and web.gps.latitude < 0
        and web.gps.longitude < 0
        and (_gps(web.data).get(1), _gps(web.data).get(3)) == ("S", "W")
    )
    bo_va_bao = web.gps is None and web.notice == process._NOTICE_GPS_BROKEN
    assert giu_dung or bo_va_bao, (web.gps, web.notice, _gps(web.data))


# ----- bản gửi AI: mọi loại nguồn, qua prepare_images, tới 3 hãng --------------------------


def _nguon_ai(loai):
    exif = _exif_2a()
    icc = _icc_co_chu()
    anh = _anh_bon_mau((600, 400))
    if loai == "jpeg-icc-chu":
        return _luu(anh, "JPEG", exif=exif, icc_profile=icc, comment=b"CHU-THICH-BI-MAT", xmp=XMP)
    if loai == "png-icc-chu":
        info = PngImagePlugin.PngInfo()
        info.add_text("Comment", "PNG-TEXT-BI-MAT")
        info.add_itxt("XML:com.adobe.xmp", XMP.decode())
        info.add_text("Description", "Nha anh Tuan 12 Le Loi", zip=True)
        return _luu(anh, "PNG", pnginfo=info, exif=exif, icc_profile=icc)
    if loai == "webp-icc-chu":
        return _luu(anh, "WEBP", exif=exif, xmp=XMP, icc_profile=icc)
    if loai == "heic-icc-chu":
        anh.info["icc_profile"] = icc
        return _luu(anh, "HEIF", exif=exif, xmp=XMP)
    if loai == "jpeg-cmyk":
        return _luu(Image.new("CMYK", (300, 200), (0, 200, 200, 0)), "JPEG", exif=exif)
    if loai == "png-16-bit":
        return _luu(Image.new("I;16", (300, 200), 40000), "PNG", exif=exif)
    if loai == "mpo":
        khung2 = Image.new("RGB", anh.size, "green")
        return _luu(anh, "MPO", save_all=True, append_images=[khung2], exif=exif)
    if loai == "webp-dong":
        khung = [Image.new("RGB", (64, 48), mau) for mau in ("red", "green", "blue")]
        return _luu(khung[0], "WEBP", save_all=True, append_images=khung[1:], exif=exif)
    if loai == "heic-trong-suot":
        return _luu(Image.new("RGBA", (64, 48), (10, 20, 30, 100)), "HEIF", exif=exif, xmp=XMP)
    if loai == "png-bang-mau":
        p = Image.new("P", (40, 40), 1)
        p.putpalette([255, 0, 0, 0, 255, 0] + [0] * 762)
        info = PngImagePlugin.PngInfo()
        info.add_text("Comment", "PNG-TEXT-BI-MAT")
        return _luu(p, "PNG", transparency=0, pnginfo=info, exif=exif)
    assert loai == "chup-man-hinh"
    return _luu(Image.new("RGBA", (1920, 1080), (40, 90, 200, 255)), "PNG")


NGUON_AI = [
    "jpeg-icc-chu",
    "png-icc-chu",
    "webp-icc-chu",
    "heic-icc-chu",
    "jpeg-cmyk",
    "png-16-bit",
    "mpo",
    "webp-dong",
    "heic-trong-suot",
    "png-bang-mau",
    "chup-man-hinh",
]


def _kiem_khong_metadata(data):
    for chu in BI_MAT + DAU_METADATA + (CHU_TRONG_ICC, b"16.0544", b"Le Loi"):
        assert chu not in data, chu


@pytest.mark.parametrize("loai", NGUON_AI)
def test_ban_ai_moi_loai_nguon_qua_prepare_images(loai):
    """A3, Lá Chắn T-050 điều kiện 2: bản AI từ mọi nguồn qua bộ kiểm "danh sách cho phép"."""
    ai = process.make_ai_image(_nguon_ai(loai))
    assert ai.mime == "image/jpeg" and max(ai.width, ai.height) <= process.AI_MAX_EDGE_PX
    _kiem_khong_metadata(ai.data)
    (gui,) = prepare_images([ImageInput(data=ai.data, mime=ai.mime)])
    assert gui.data == ai.data and gui.mime == "image/jpeg"
    # Ảnh xem trước cũng sạch (LC-T058-2).
    _kiem_khong_metadata(process.make_preview(_nguon_ai(loai)))


@pytest.mark.parametrize(
    ("loai", "mime"),
    [("jpeg-icc-chu", "image/jpeg"), ("png-icc-chu", "image/png"), ("webp-icc-chu", "image/webp")],
)
def test_nguon_con_metadata_thi_bo_kiem_t050_tu_choi(loai, mime):
    # Đối chứng cho test trên: ảnh gốc gửi thẳng thì bị chặn, tức bộ kiểm không "cho qua hết".
    with pytest.raises(AIError):
        prepare_images([ImageInput(data=_nguon_ai(loai), mime=mime)])


def _anh_trong_yeu_cau(vendor, body):
    """Byte ảnh trong yêu cầu gửi hãng AI, và phần còn lại của yêu cầu (đã bỏ dữ liệu ảnh)."""
    body = json.loads(json.dumps(body))
    if vendor == "anthropic":
        nguon = body["messages"][0]["content"][0]["source"]
        assert nguon["type"] == "base64" and nguon["media_type"] == "image/jpeg"
        data = base64.b64decode(nguon.pop("data"))
    elif vendor == "openai":
        phan = body["input"][0]["content"][0]
        prefix = "data:image/jpeg;base64,"
        assert phan["image_url"].startswith(prefix)
        data = base64.b64decode(phan.pop("image_url")[len(prefix) :])
    else:
        phan = body["contents"][0]["parts"][0]
        inline = phan.get("inlineData") or phan.get("inline_data")
        data = base64.urlsafe_b64decode(inline.pop("data"))
    return data, json.dumps(body, ensure_ascii=False)


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize("loai", ["jpeg-icc-chu", "png-icc-chu", "webp-icc-chu", "heic-icc-chu"])
def test_ban_ai_toi_ca_3_hang_dung_byte_khong_metadata(network, vendor, loai):  # noqa: F811
    """Bản AI tới máy chủ (giả) của cả 3 hãng đúng byte đã kiểm, không kèm metadata hay tên."""
    ai = process.make_ai_image(_nguon_ai(loai))
    _, _request, body = run(network, vendor, [ImageInput(data=ai.data, mime=ai.mime)])
    data, phan_con_lai = _anh_trong_yeu_cau(vendor, body)
    assert data == ai.data
    _kiem_khong_metadata(data)
    for chu in ("16.0544", "Le Loi", "Tuan", "SERIAL", "samsung", "SM-S918B", "xmpmeta"):
        assert chu not in phan_con_lai, chu


# ----- mở ảnh an toàn ------------------------------------------------------------------------


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
def test_bien_gioi_han_diem_anh_dung_bang_qua_mot_bi_chan(monkeypatch, dinh_dang):
    monkeypatch.setattr(process, "MAX_IMAGE_PIXELS", 1000)
    vua = _luu(Image.new("RGB", (40, 25), "red"), dinh_dang)
    assert (process.make_web_image(vua).width, process.make_ai_image(vua).height) == (40, 25)
    qua = _luu(Image.new("RGB", (7, 143), "red"), dinh_dang)  # 1001 điểm ảnh
    for ham in (process.make_web_image, process.make_ai_image, process.make_preview):
        assert _loi(ham, qua).startswith("Ảnh có quá nhiều điểm ảnh")


def test_bom_png_that_khong_doi_gioi_han_bi_chan_truoc_khi_giai_ma(monkeypatch):
    # PNG 9000 × 9000 (81 triệu điểm ảnh, ~243 MB khi giải mã) mà file chỉ vài KB.
    hang = b"\x00" + b"\x00" * 9000 * 3
    data = _png_tay(9000, 9000, 8, 2, hang * 10)
    assert len(data) < 10_000
    goi_load = []
    monkeypatch.setattr(ImageFile.ImageFile, "load", lambda self: goi_load.append(1))
    cau = _loi(process.make_web_image, data)
    assert cau.startswith("Ảnh có quá nhiều điểm ảnh (81 triệu)")
    assert goi_load == []  # chặn trước khi giải mã (không cấp bộ nhớ cho cả ảnh)


def test_bom_jpeg_khai_kich_thuoc_lon_bi_chan():
    sach = _luu(Image.new("RGB", (16, 16)), "JPEG")
    sof = sach.find(b"\xff\xc0")
    data = sach[: sof + 5] + (9000).to_bytes(2, "big") + (10000).to_bytes(2, "big")
    data += sach[sof + 9 :]
    assert _mo_kich_thuoc(data) == (10000, 9000)
    for ham in (process.make_web_image, process.make_ai_image, process.make_preview):
        assert _loi(ham, data).startswith("Ảnh có quá nhiều điểm ảnh")


def _mo_kich_thuoc(data):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", Image.DecompressionBombWarning)  # chỉ đọc phần đầu file
        with Image.open(io.BytesIO(data)) as image:
            return image.size


def test_gia_duoi_qua_thu_vien_anh_nhan_theo_noi_dung_cau_loi_khong_lo_duong_dan(tmp_path):
    png = _luu(_anh_bon_mau((120, 90)), "PNG")
    library, refs = _thu_vien(
        tmp_path,
        {
            "IMG_0001.jpg": png,  # PNG đặt đuôi .jpg: vẫn là ảnh dùng được
            "IMG_0002.jpg": _luu(Image.new("RGB", (20, 20)), "GIF"),
            # Chữ thường (chuỗi PHP kiểu webshell ghi ra ổ bị Windows Defender chặn mở file).
            "IMG_0003.heic": b"day la file chu, khong phai anh HEIC",
            "IMG_0004.webp": b"<script>alert(1)</script>",
            "IMG_0005.png": _luu(Image.new("RGB", (20, 20)), "BMP"),
        },
    )
    cache = process.PreviewCache(tmp_path / "cache")
    assert process.jpeg_layout(cache.get(library, refs["IMG_0001.jpg"])) == (120, 90)
    for ten in ("IMG_0002.jpg", "IMG_0003.heic", "IMG_0004.webp", "IMG_0005.png"):
        cau = _loi(cache.get, library, refs[ten])
        assert cau == process._MSG_NOT_IMAGE, ten
        for chu in ("Tuan", "Le Loi", "IMG_", str(tmp_path), "\\", "/"):
            assert chu not in cau, (ten, chu)


@pytest.mark.parametrize("ti_le", [0.02, 0.1, 0.3, 0.5, 0.8, 0.95, 0.999])
def test_heic_cut_o_nhieu_diem_chi_bao_cau_co_dinh(ti_le):
    # Soi Lỗi T-047: HEIC cụt mở được, lỗi chỉ nổ ở ``load()`` và là ``ValueError``.
    full = _heic_nhieu()
    data = full[: int(len(full) * ti_le)]
    for ham in (process.make_web_image, process.make_ai_image, process.make_preview):
        assert _loi(ham, data) in {process._MSG_BROKEN, process._MSG_NOT_IMAGE}


def _dot_bien(rng, data):
    data = bytearray(data)
    kieu = rng.random()
    if kieu < 0.6:
        for _ in range(rng.randint(1, 8)):
            data[rng.randrange(len(data))] = rng.randrange(256)
    elif kieu < 0.8:
        data = data[: rng.randrange(8, len(data))]
    elif kieu < 0.9:
        at = rng.randrange(len(data))
        data[at:at] = bytes(rng.randrange(256) for _ in range(rng.randint(1, 16)))
    else:
        at = rng.randrange(len(data))
        del data[at : at + rng.randint(1, 64)]
    return bytes(data)


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
def test_dot_bien_ngau_nhien_ca_file_khong_lot_loi_tho(dinh_dang):
    """Thử ngoài test (4 × 400 file, 3 hàm): 0 lỗi thô. Bản thu nhỏ với hạt giống cố định."""
    goc = Image.effect_noise((96, 64), 40).convert("RGB")
    params = {"exif": _exif_gps().tobytes()}
    if dinh_dang != "HEIF":
        params["icc_profile"] = _icc_co_chu()
    data = _luu(goc, dinh_dang, **params)
    rng = random.Random(f"T-049-{dinh_dang}")
    thanh_cong = 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Pillow cảnh báo "Corrupt EXIF data"
        for _ in range(40):
            hong = _dot_bien(rng, data)
            for ham in (process.make_web_image, process.make_ai_image, process.make_preview):
                try:
                    ra = ham(hong)
                except process.ImageProcessError as exc:
                    assert exc.__cause__ is None
                    assert _cau_loi_hop_le(str(exc)), str(exc)
                    continue
                thanh_cong += 1
                if ham is process.make_ai_image:
                    prepare_images([ImageInput(data=ra.data, mime=ra.mime)])
    assert thanh_cong or dinh_dang == "PNG"  # PNG kiểm CRC nên hầu như mọi đột biến đều hỏng


@pytest.mark.parametrize("dinh_dang", ["PNG", "WEBP", "HEIF"])
@pytest.mark.parametrize("orientation", range(1, 9))
def test_xoay_dung_ca_8_huong_voi_png_webp_heic(dinh_dang, orientation):
    # Thợ Máy thử đủ 8 hướng với JPEG; ở đây PNG (eXIf), WebP (EXIF), HEIC (irot/imir).
    exif = Image.Exif()
    exif[ExifTags.Base.Orientation] = orientation
    data = _luu(_anh_bon_mau(), dinh_dang, exif=exif.tobytes())
    mong_doi = _anh_bon_mau()
    if orientation in process._TRANSPOSE:
        mong_doi = mong_doi.transpose(process._TRANSPOSE[orientation])
    ra = (
        process.make_web_image(data).data,
        process.make_ai_image(data).data,
        process.make_preview(data),
    )
    for out in ra:
        anh = _mo(out)
        assert anh.size == mong_doi.size
        for thuc, dung in zip(_goc_mau(anh), _goc_mau(mong_doi), strict=True):
            assert _mau_gan(thuc, dung), (thuc, dung)
    assert _mo(ra[0]).getexif().get(ExifTags.Base.Orientation, 1) == 1


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
def test_anh_khong_exif_xu_ly_binh_thuong_moi_dinh_dang(dinh_dang):
    # Yêu cầu 7 (ảnh chụp màn hình, ảnh đã bị mạng xã hội xóa EXIF) với cả 4 định dạng.
    data = _luu(_anh_bon_mau((400, 300)), dinh_dang)
    web = process.make_web_image(data)
    assert (web.width, web.height) == (400, 300)
    assert web.gps is None and web.notice == ""
    assert b"EXIF" not in web.data[12:] and not _mo(web.data).getexif()
    _kiem_khong_metadata(process.make_ai_image(data).data)


def test_png_16_bit_mau_va_trong_suot_dung_mau():
    # SL-T058-1: PNG màu 16 bit (RGB và xám + trong suốt) viết tay, đổi về 8 bit đúng màu.
    rgb = _png_tay(20, 10, 16, 2, (b"\x00" + b"\xff\xff\x80\x00\x00\x00" * 20) * 10)
    la = _png_tay(20, 10, 16, 4, (b"\x00" + b"\x80\x00\xff\xff" * 20) * 10)
    assert _mo(rgb).mode == "RGB" and _mo(la).mode == "RGBA"
    for data, mau in ((rgb, (255, 128, 0)), (la, (128, 128, 128))):
        for out in (process.make_web_image(data).data, process.make_ai_image(data).data):
            assert _mau_gan(_mo(out).getpixel((5, 5)), mau, sai=6)


def test_jpeg_cmyk_adobe_dao_mau_ra_dung_mau():
    data = _luu(Image.new("CMYK", (30, 20), (0, 255, 255, 0)), "JPEG")  # Pillow ghi Adobe APP14
    assert b"Adobe" in data
    ra = (
        process.make_web_image(data).data,
        process.make_ai_image(data).data,
        process.make_preview(data),
    )
    for out in ra:
        assert _mau_gan(_mo(out).getpixel((5, 5)), (255, 0, 0), sai=20)


@pytest.mark.parametrize("dinh_dang", ["JPEG", "PNG", "WEBP", "HEIF"])
def test_khong_imagecms_khong_arrow_khong_alignment_khi_chay_that(monkeypatch, dinh_dang):
    """Bẫy hàm lúc chạy (bổ sung test dò mã nguồn của Thợ Máy): ảnh có hồ sơ màu chở chữ."""

    def cam(*_args, **_kwargs):
        raise AssertionError("module ảnh không được gọi hàm này")

    for ten in ("profileToProfile", "buildTransform", "applyTransform", "getOpenProfile"):
        monkeypatch.setattr(ImageCms, ten, cam)
    monkeypatch.setattr(ImageCms.ImageCmsProfile, "__init__", cam)
    monkeypatch.setattr(Image.Image, "__arrow_c_array__", cam, raising=False)
    monkeypatch.setattr(Image.Image, "__arrow_c_schema__", cam, raising=False)
    monkeypatch.setattr(Image, "fromarrow", cam, raising=False)
    moi_truong = dict(os.environ)
    anh = _anh_bon_mau((120, 90))
    anh.info["icc_profile"] = _icc_co_chu()
    if dinh_dang == "HEIF":
        data = _luu(anh, "HEIF", exif=_exif_gps().tobytes())
    else:
        data = _luu(anh, dinh_dang, exif=_exif_gps().tobytes(), icc_profile=_icc_co_chu())
    process.make_web_image(data)
    process.make_ai_image(data)
    process.make_preview(data)
    assert dict(os.environ) == moi_truong
    assert "PILLOW_ALIGNMENT" not in os.environ


# ----- Pillow dưới 13, nhiều luồng ---------------------------------------------------------


def test_pillow_duoi_13_khong_cache_thi_tu_choi(tmp_path, monkeypatch):
    library, refs = _thu_vien(tmp_path, {"a.jpg": _luu(_anh_bon_mau((200, 150)), "JPEG")})
    monkeypatch.setattr(PIL, "__version__", "12.3.0")
    cau = _loi(process.PreviewCache(tmp_path / "cache").get, library, refs["a.jpg"])
    assert cau == process._MSG_OLD_PILLOW
    assert not (tmp_path / "cache").exists()


# SL-T049-2 (PreviewCache.get trả ảnh có sẵn trong cache mà không kiểm Pillow >= 13): sửa ở T-067.
def test_pillow_duoi_13_co_cache_cung_tu_choi(tmp_path, monkeypatch):
    library, refs = _thu_vien(tmp_path, {"a.jpg": _luu(_anh_bon_mau((200, 150)), "JPEG")})
    cache = process.PreviewCache(tmp_path / "cache")
    cache.get(library, refs["a.jpg"])  # tạo sẵn khi còn Pillow 13
    monkeypatch.setattr(PIL, "__version__", "12.3.0")  # máy quay về Pillow 12 (uv sync lệch…)
    assert _loi(cache.get, library, refs["a.jpg"]) == process._MSG_OLD_PILLOW


@pytest.mark.xfail(
    strict=True,
    reason="SL-T049-3: warnings.catch_warnings không an toàn nhiều luồng; hai phiên Streamlit "
    "mở ảnh cùng lúc để lại bộ lọc 'DecompressionBombWarning thành lỗi' cho cả chương trình",
)
def test_hai_luong_mo_anh_cung_luc_khong_de_lai_bo_loc_canh_bao(monkeypatch):
    png = _luu(Image.new("RGB", (20, 20)), "PNG")
    a_vao, b_vao, a_ra = threading.Event(), threading.Event(), threading.Event()
    mo_that = Image.open
    thu_tu = []
    khoa = threading.Lock()

    def mo_cho(fp, mode="r", formats=None):
        with khoa:
            thu_tu.append(1)
            lan = len(thu_tu)
        if lan == 1:  # luồng A đang ở trong khối đổi cảnh báo thành lỗi: chờ B vào khối
            a_vao.set()
            b_vao.wait(10)
        elif lan == 2:  # luồng B đã vào khối: chờ A ra khỏi khối
            b_vao.set()
            a_ra.wait(10)
        return mo_that(fp, mode, formats)

    monkeypatch.setattr(Image, "open", mo_cho)
    loi = []

    def chay(xong=None):
        try:
            process.make_preview(png)
        except BaseException as exc:  # noqa: BLE001
            loi.append(exc)
        finally:
            if xong is not None:
                xong.set()

    with warnings.catch_warnings():  # test tự dọn bộ lọc, lỗi có thật cũng không lan sang test khác
        truoc = list(warnings.filters)
        luong_a = threading.Thread(target=chay, args=(a_ra,))
        luong_a.start()
        assert a_vao.wait(10)
        luong_b = threading.Thread(target=chay)
        luong_b.start()
        luong_a.join(30)
        luong_b.join(30)
        sau = list(warnings.filters)
    assert loi == [] and len(thu_tu) == 2
    assert sau == truoc, [bo_loc for bo_loc in sau if bo_loc not in truoc]


# ----- điều kiện 6 Lá Chắn T-047: gỡ HEIF khỏi bảng ---------------------------------------


def test_go_heif_khoi_bang_roi_module_anh_tu_dang_ky_lai():
    heic = _luu(_anh_bon_mau((64, 48)), "HEIF")
    process.make_preview(heic)  # module đăng ký HEIF lúc mở ảnh lần đầu
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile
    _go_heif_khoi_bang()
    assert "HEIF" not in Image.ID and "HEIF" not in Image.OPEN
    assert "HEIF" not in Image.EXTENSION.values()
    with pytest.raises(UnidentifiedImageError):
        Image.open(io.BytesIO(heic))
    # Module ảnh không phụ thuộc HEIF đã đăng ký sẵn: tự đăng ký lại, tắt ảnh phụ.
    assert process.jpeg_layout(process.make_preview(heic)) == (64, 48)
    assert Image.OPEN["HEIF"][0] is pillow_heif.HeifImageFile
    assert heif_options.THUMBNAILS is False and heif_options.DEPTH_IMAGES is False


# ----- tên file --------------------------------------------------------------------------


def test_ten_file_tu_ten_nfd_cua_mac_giong_nfc():
    # Tên thư mục trên Mac ở dạng NFD (dấu tách rời): thẻ lấy từ đó vẫn ra cùng tên file.
    nfc = naming.image_file_name(category="Cổng inox Ổ khóa Ưu đãi", area="Thủ Đức")
    nfd = naming.image_file_name(
        category=unicodedata.normalize("NFD", "Cổng inox Ổ khóa Ưu đãi"),
        area=unicodedata.normalize("NFD", "Thủ Đức"),
    )
    assert nfc == nfd == "cong-inox-o-khoa-uu-dai-thu-duc.webp"


@pytest.mark.parametrize(
    "ma", ["CT 012", "Nhà anh Tuấn", "CT012/../x", "../CT012", "CT0123456", "CT012 - Le Loi"]
)
def test_ma_cong_trinh_sai_mau_khong_vao_ten_file(ma):
    # Góp ý Lá Chắn T-046 số 3: chữ tự do từ tên thư mục không bao giờ thành tên file công khai.
    assert naming.image_file_name(category="Cửa sắt", project_code=ma) == "cua-sat.webp"


@pytest.mark.parametrize(
    "alt",
    [
        'Cổng <script>alert(1)</script> "x" onerror=1',
        "C:\\Anh\\IMG_0001.HEIC",
        "../../etc/passwd",
        "Ảnh\u200bcổng\u00adinox\n\t",
        "ｆｕｌｌ ｗｉｄｔｈ ①②",
    ],
)
def test_ten_file_chi_gom_chu_thuong_so_gach_noi(alt):
    ten = naming.image_file_name(alt=alt)
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.webp", ten), ten
    assert len(ten.removesuffix(".webp")) <= naming.MAX_NAME_CHARS


def test_nhieu_anh_cung_the_khong_trung_ten():
    the = "Sửa cửa cuốn khe thoáng " * 4
    da_dung = []
    for _ in range(60):
        da_dung.append(naming.image_file_name(category=the, taken=da_dung))
    assert len({ten.casefold() for ten in da_dung}) == 60
    assert all(len(ten.removesuffix(".webp")) <= naming.MAX_NAME_CHARS for ten in da_dung)

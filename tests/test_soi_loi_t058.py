"""Soi Lỗi T-058: tìm chỗ hỏng khi chạy Pillow 13 (Streamlit 1.65 khai báo ``pillow<13``).

Ba nhóm:

1. Mọi nhánh Streamlit dùng Pillow trong ``st.image``: ảnh Pillow (RGB, RGBA, P, L, LA, ảnh mở
   từ file), bytes/BytesIO (PNG có alpha, JPEG, WEBP, GIF động), mảng numpy (xám, RGB, RGBA,
   số thực, BGR), ảnh rất nhỏ, ảnh rộng hơn khung (Streamlit thu nhỏ bằng ``resize``), danh sách
   ảnh, đường dẫn file, logo SVG của app. Bắt các byte Streamlit thật sự gửi ra trình duyệt rồi
   mở lại bằng Pillow để xem đúng định dạng, kích thước, kênh alpha.
2. ``st.cache_data`` băm tham số là ảnh Pillow (Streamlit gọi ``tobytes``/``getpalette``).
3. Đường T-049 sẽ đi: ảnh có GPS (JPEG, HEIC) lưu sang WebP với ``exif=`` vẫn giữ GPS; không
   truyền ``exif=`` thì GPS mất; xóa thẻ GPS rồi lưu thì GPS mất mà thẻ khác còn.

Mọi ảnh là ảnh giả tạo trong bộ nhớ hoặc thư mục tạm. Không gọi mạng. Cảnh báo "sắp bỏ"
(DeprecationWarning) của Pillow bị đổi thành lỗi trong các test này để lộ API Pillow 13 đã đổi.
"""

import io
import warnings
from pathlib import Path

import numpy as np
import pillow_heif
import pytest
from PIL import ExifTags, Image, ImageOps
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
from streamlit.testing.v1 import AppTest

ASSETS = Path(__file__).parent.parent / "app" / "assets"
# streamlit/elements/lib/image_utils.py: MAXIMUM_CONTENT_WIDTH = 2 * 730
KHUNG_TOI_DA = 1460

GPS = {
    ExifTags.GPS.GPSLatitudeRef: "N",
    ExifTags.GPS.GPSLatitude: (10.0, 45.0, 30.5),
    ExifTags.GPS.GPSLongitudeRef: "E",
    ExifTags.GPS.GPSLongitude: (106.0, 40.0, 12.25),
}


@pytest.fixture
def media_ra(monkeypatch):
    """Ghi lại mọi file media Streamlit cất (byte + mimetype) trong lúc AppTest chạy."""
    da_cat: list[tuple[bytes, str]] = []
    goc = MemoryMediaFileStorage.load_and_get_id

    def ghi_lai(self, path_or_data, mimetype, kind, filename=None):
        data = path_or_data if isinstance(path_or_data, bytes) else Path(path_or_data).read_bytes()
        da_cat.append((data, mimetype))
        return goc(self, path_or_data, mimetype, kind, filename)

    monkeypatch.setattr(MemoryMediaFileStorage, "load_and_get_id", ghi_lai)
    return da_cat


@pytest.fixture
def canh_bao_la_loi():
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        yield


def _png(mode="RGBA", size=(40, 30), color=(10, 20, 30, 128)) -> bytes:
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, "PNG")
    return buf.getvalue()


def _anh(fmt, mode="RGB", size=(40, 30), color=(200, 30, 30), **kw) -> bytes:
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, fmt, **kw)
    return buf.getvalue()


def _gif_dong(size=(40, 30), so_khung=3) -> bytes:
    # Mỗi khung một màu khác hẳn, nếu không Pillow gộp các khung giống nhau làm một.
    khung = [Image.new("RGB", size, (i * 60, 255 - i * 60, 0)) for i in range(so_khung)]
    buf = io.BytesIO()
    khung[0].save(buf, "GIF", save_all=True, append_images=khung[1:], duration=100, loop=0)
    return buf.getvalue()


def _trang_hien_anh(kieu, data, tham_so):
    """Trang Streamlit tối giản: dựng ảnh theo ``kieu`` rồi gọi ``st.image``."""
    import io

    import numpy as np
    import streamlit as st
    from PIL import Image

    if kieu == "pil":
        mode, size, color = data
        anh = Image.new(mode, tuple(size), color)
        if mode == "P":
            anh.info["transparency"] = 0
    elif kieu == "pil_tu_file":
        anh = Image.open(io.BytesIO(data))
    elif kieu == "bytes":
        anh = data
    elif kieu == "bytesio":
        anh = io.BytesIO(data)
    elif kieu == "numpy":
        dtype, shape, fill = data
        anh = np.full(tuple(shape), fill, dtype=dtype)
    elif kieu == "nhieu":
        anh = [Image.new("RGB", (20, 10), (i * 50, 0, 0)) for i in range(3)]
    else:  # đường dẫn file
        anh = data
    st.image(anh, caption=None if kieu == "nhieu" else "anh", **tham_so)


def _chay(kieu, data, **tham_so) -> AppTest:
    at = AppTest.from_function(_trang_hien_anh, args=(kieu, data, tham_so)).run(timeout=30)
    assert not at.exception, at.exception
    return at


def _mo(data: bytes) -> Image.Image:
    anh = Image.open(io.BytesIO(data))
    anh.load()
    return anh


# --- 1. st.image với ảnh Pillow -------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "color", "dinh_dang", "mime"),
    [
        ("RGB", (200, 30, 30), "JPEG", "image/jpeg"),
        ("L", 128, "JPEG", "image/jpeg"),
        ("RGBA", (10, 20, 30, 77), "PNG", "image/png"),
        ("LA", (100, 77), "PNG", "image/png"),
        ("P", 5, "PNG", "image/png"),
        ("CMYK", (0, 255, 255, 0), "JPEG", "image/jpeg"),
    ],
)
def test_st_image_anh_pillow_moi_che_do_mau(
    media_ra, canh_bao_la_loi, mode, color, dinh_dang, mime
):
    _chay("pil", (mode, (40, 30), color))
    assert len(media_ra) == 1
    data, mimetype = media_ra[0]
    assert mimetype == mime
    ra = _mo(data)
    assert ra.format == dinh_dang
    assert ra.size == (40, 30)


def test_st_image_anh_16_bit_phai_chon_png(media_ra, canh_bao_la_loi):
    # Chế độ tự động, Streamlit chọn JPEG cho ảnh xám 16 bit ("I;16") và Pillow báo
    # "cannot write mode I;16 as JPEG". Lỗi này có y hệt ở Pillow 12.3.0 (giới hạn của
    # Streamlit, không do T-058). Chỉ ra PNG thì chạy.
    _chay("pil", ("I;16", (40, 30), 3000), output_format="PNG")
    ra = _mo(media_ra[0][0])
    assert ra.format == "PNG"
    assert ra.size == (40, 30)


def test_st_image_png_alpha_giu_do_trong_suot(media_ra, canh_bao_la_loi):
    _chay("pil", ("RGBA", (40, 30), (10, 20, 30, 77)))
    ra = _mo(media_ra[0][0])
    assert ra.mode == "RGBA"
    assert ra.getpixel((5, 5)) == (10, 20, 30, 77)


def test_st_image_rgba_ep_jpeg_bo_alpha_khong_loi(media_ra, canh_bao_la_loi):
    _chay("pil", ("RGBA", (40, 30), (10, 20, 30, 77)), output_format="JPEG")
    data, mimetype = media_ra[0]
    assert mimetype == "image/jpeg"
    ra = _mo(data)
    assert ra.format == "JPEG"
    assert ra.mode == "RGB"


@pytest.mark.parametrize("size", [(1, 1), (1, 500), (500, 1)])
def test_st_image_anh_rat_nho_hoac_rat_det(media_ra, canh_bao_la_loi, size):
    _chay("pil", ("RGB", size, (1, 2, 3)))
    assert _mo(media_ra[0][0]).size == size


def test_st_image_anh_rong_hon_khung_bi_thu_nho(media_ra, canh_bao_la_loi):
    _chay("pil", ("RGB", (3000, 600), (40, 90, 160)))
    ra = _mo(media_ra[0][0])
    assert ra.size == (KHUNG_TOI_DA, 292)
    r, g, b = ra.getpixel((700, 100))
    assert abs(r - 40) < 8 and abs(g - 90) < 8 and abs(b - 160) < 8


def test_st_image_width_nho_hon_anh_thu_nho_dung_ti_le(media_ra, canh_bao_la_loi):
    _chay("pil", ("RGBA", (400, 200), (1, 2, 3, 200)), width=100)
    ra = _mo(media_ra[0][0])
    assert ra.format == "PNG"
    assert ra.size == (100, 50)


def test_st_image_anh_lon_8_megapixel(media_ra, canh_bao_la_loi):
    _chay("pil", ("RGB", (4032, 3024), (90, 90, 90)))  # cỡ ảnh iPhone 12 MP thu gọn
    assert _mo(media_ra[0][0]).width == KHUNG_TOI_DA


def test_st_image_anh_mo_tu_file_jpeg(media_ra, canh_bao_la_loi):
    _chay("pil_tu_file", _anh("JPEG", size=(64, 48)))
    ra = _mo(media_ra[0][0])
    assert ra.format == "JPEG"
    assert ra.size == (64, 48)


def test_st_image_nhieu_anh_mot_luc(media_ra, canh_bao_la_loi):
    at = _chay("nhieu", None)
    assert len(at.get("image")[0].proto.imgs) == 3
    assert len(media_ra) == 3
    assert {_mo(d).size for d, _ in media_ra} == {(20, 10)}


# --- 1b. st.image với bytes / BytesIO / file --------------------------------------------------


@pytest.mark.parametrize(
    ("kieu", "data", "dinh_dang"),
    [
        ("bytes", _png(), "PNG"),
        ("bytesio", _png(), "PNG"),
        ("bytes", _anh("JPEG"), "JPEG"),
        ("bytes", _anh("WEBP"), "JPEG"),  # Streamlit đổi WEBP không alpha sang JPEG
        ("bytes", _anh("WEBP", mode="RGBA", color=(1, 2, 3, 40)), "PNG"),
        ("bytes", _anh("BMP"), "JPEG"),
        ("bytes", _anh("TIFF"), "JPEG"),
        ("bytes", _gif_dong(), "GIF"),
    ],
)
def test_st_image_bytes_cac_dinh_dang(media_ra, canh_bao_la_loi, kieu, data, dinh_dang):
    _chay(kieu, data)
    ra = _mo(media_ra[0][0])
    assert ra.format == dinh_dang
    assert ra.size == (40, 30)


def test_st_image_gif_dong_nho_giu_nguyen_moi_khung(media_ra, canh_bao_la_loi):
    goc = _gif_dong(so_khung=4)
    _chay("bytes", goc)
    data, mimetype = media_ra[0]
    assert mimetype == "image/gif"
    assert data == goc
    assert getattr(_mo(data), "n_frames", 1) == 4


def test_st_image_gif_dong_qua_rong_van_ra_anh(media_ra, canh_bao_la_loi):
    _chay("bytes", _gif_dong(size=(2000, 50)))
    ra = _mo(media_ra[0][0])
    assert ra.format == "GIF"
    assert ra.width == KHUNG_TOI_DA


def test_st_image_duong_dan_file_png(media_ra, canh_bao_la_loi, tmp_path):
    path = tmp_path / "ảnh thử.png"  # tên có dấu và khoảng trắng
    path.write_bytes(_png())
    _chay("path", str(path))
    assert _mo(media_ra[0][0]).format == "PNG"


def test_st_image_logo_svg_cua_app_khong_qua_pillow(media_ra):
    at = _chay("path", str(ASSETS / "logo.svg"), width=220)
    assert at.get("image")[0].proto.imgs[0].url.startswith("data:image/svg+xml;base64,")
    assert media_ra == []


def test_st_image_bytes_rac_bao_loi_ro_rang():
    at = AppTest.from_function(_trang_hien_anh, args=("bytes", b"khong phai anh", {})).run(
        timeout=30
    )
    assert at.exception  # Pillow 13 vẫn báo UnidentifiedImageError, không treo/sập tiến trình
    assert "UnidentifiedImageError" in str(at.exception[0].value) or at.exception[0].message


# --- 1c. st.image với numpy ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("dtype", "shape", "fill", "tham_so", "dinh_dang", "mode"),
    [
        ("uint8", (30, 40), 128, {}, "JPEG", "L"),
        ("uint8", (30, 40, 1), 128, {}, "JPEG", "L"),
        ("uint8", (30, 40, 3), 200, {}, "JPEG", "RGB"),
        ("uint8", (30, 40, 4), 90, {}, "PNG", "RGBA"),
        ("float32", (30, 40, 3), 0.5, {}, "JPEG", "RGB"),
        ("float64", (30, 40, 3), 3.0, {"clamp": True}, "JPEG", "RGB"),
        ("uint8", (30, 40, 3), 10, {"channels": "BGR"}, "JPEG", "RGB"),
        ("uint8", (30, 40, 3), 10, {"output_format": "PNG"}, "PNG", "RGB"),
    ],
)
def test_st_image_mang_numpy(
    media_ra, canh_bao_la_loi, dtype, shape, fill, tham_so, dinh_dang, mode
):
    _chay("numpy", (dtype, shape, fill), **tham_so)
    ra = _mo(media_ra[0][0])
    assert ra.format == dinh_dang
    assert ra.mode == mode
    assert ra.size == (40, 30)


def test_st_image_numpy_bgr_dao_kenh_mau(media_ra):
    arr = np.zeros((10, 10, 3), dtype=np.uint8)
    arr[..., 0] = 255  # theo BGR đây là kênh xanh dương

    def trang(a):
        import streamlit as st

        st.image(a, channels="BGR", output_format="PNG")

    at = AppTest.from_function(trang, args=(arr,)).run(timeout=30)
    assert not at.exception
    assert _mo(media_ra[0][0]).getpixel((5, 5)) == (0, 0, 255)


# --- 2. st.cache_data băm ảnh Pillow ----------------------------------------------------------


def _trang_cache_anh():
    import streamlit as st
    from PIL import Image

    @st.cache_data
    def kich_thuoc(anh):
        st.session_state["so_lan_tinh"] = st.session_state.get("so_lan_tinh", 0) + 1
        return anh.size

    p = Image.new("P", (8, 8), 1)
    p.putpalette([0, 0, 0, 255, 0, 0] + [0] * 762)
    st.write(kich_thuoc(Image.new("RGB", (8, 8), (1, 2, 3))))
    st.write(kich_thuoc(Image.new("RGB", (8, 8), (1, 2, 3))))  # trùng: lấy từ cache
    st.write(kich_thuoc(p))


def test_cache_data_bam_duoc_anh_pillow(canh_bao_la_loi):
    at = AppTest.from_function(_trang_cache_anh).run(timeout=30)
    assert not at.exception, at.exception
    assert at.session_state["so_lan_tinh"] == 2


# --- 3. Đường T-049: lưu WebP giữ / bỏ GPS ----------------------------------------------------


def _exif_co_gps() -> Image.Exif:
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "MayGia"
    exif[ExifTags.Base.Orientation] = 6
    exif[ExifTags.IFD.GPSInfo] = dict(GPS)
    return exif


def _jpeg_co_gps() -> Image.Image:
    buf = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 200, 30)).save(buf, "JPEG", exif=_exif_co_gps())
    return Image.open(io.BytesIO(buf.getvalue()))


def _luu_webp(anh: Image.Image, **kw) -> Image.Image:
    buf = io.BytesIO()
    anh.save(buf, "WEBP", quality=80, **kw)
    return Image.open(io.BytesIO(buf.getvalue()))


def _gps(anh: Image.Image) -> dict:
    return dict(anh.getexif().get_ifd(ExifTags.IFD.GPSInfo))


def test_jpeg_gia_co_gps_doc_lai_duoc(canh_bao_la_loi):
    assert _gps(_jpeg_co_gps()) == GPS


@pytest.mark.parametrize("cach", ["getexif", "info_bytes"])
def test_webp_co_exif_giu_gps_va_the_khac(canh_bao_la_loi, cach):
    goc = _jpeg_co_gps()
    exif = goc.getexif() if cach == "getexif" else goc.info["exif"]
    ra = _luu_webp(goc, exif=exif)
    assert ra.format == "WEBP"
    assert _gps(ra) == GPS
    assert ra.getexif()[ExifTags.Base.Make] == "MayGia"
    assert ra.getexif()[ExifTags.Base.Orientation] == 6


def test_webp_khong_truyen_exif_thi_mat_gps(canh_bao_la_loi):
    ra = _luu_webp(_jpeg_co_gps())
    assert _gps(ra) == {}
    assert ExifTags.Base.Make not in ra.getexif()


def test_webp_xoa_the_gps_thi_chi_mat_gps(canh_bao_la_loi):
    goc = _jpeg_co_gps()
    exif = goc.getexif()
    del exif[ExifTags.IFD.GPSInfo]
    ra = _luu_webp(goc, exif=exif)
    assert _gps(ra) == {}
    assert ra.getexif()[ExifTags.Base.Make] == "MayGia"


def test_webp_sau_exif_transpose_van_giu_gps(canh_bao_la_loi):
    goc = _jpeg_co_gps()
    xoay = ImageOps.exif_transpose(goc)
    assert xoay.size == (48, 64)  # Orientation 6: xoay 90 độ
    ra = _luu_webp(xoay, exif=xoay.getexif())
    assert _gps(ra) == GPS
    assert ExifTags.Base.Orientation not in ra.getexif()  # đã xoay thì bỏ thẻ hướng


@pytest.fixture
def heif_dang_ky():
    Image.init()
    bang = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
    luu = {ten: getattr(Image, ten).copy() for ten in bang}
    pillow_heif.register_heif_opener()
    yield
    for ten, gia_tri in luu.items():
        hien = getattr(Image, ten)
        hien.clear()
        if isinstance(hien, dict):
            hien.update(gia_tri)
        else:
            hien.extend(gia_tri)


def test_heic_co_gps_sang_webp_giu_gps(tmp_path, heif_dang_ky, canh_bao_la_loi):
    path = tmp_path / "iphone.heic"
    anh = Image.new("RGB", (64, 48), (200, 120, 40))
    pillow_heif.from_pillow(anh).save(path, quality=80, exif=_exif_co_gps().tobytes())
    with Image.open(path, formats=["HEIF"]) as heic:
        heic.load()
        assert _gps(heic) == GPS
        ra = _luu_webp(heic, exif=heic.getexif())
    assert _gps(ra) == GPS


def test_heic_hien_bang_st_image(tmp_path, heif_dang_ky, media_ra):
    path = tmp_path / "iphone.heic"
    pillow_heif.from_pillow(Image.new("RGB", (64, 48), (200, 120, 40))).save(path, quality=80)

    def trang(p):
        import pillow_heif
        import streamlit as st
        from PIL import Image

        pillow_heif.register_heif_opener()
        st.image(Image.open(p, formats=["HEIF"]))

    at = AppTest.from_function(trang, args=(str(path),)).run(timeout=30)
    assert not at.exception, at.exception
    ra = _mo(media_ra[0][0])
    assert ra.format == "JPEG"
    assert ra.size == (64, 48)


def test_gioi_han_bom_giai_nen_van_bat():
    assert Image.MAX_IMAGE_PIXELS == 89_478_485

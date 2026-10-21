"""Soi Lỗi T-067: dọn lỗi Thấp xử lý ảnh sau T-049 (kiểm rút gọn).

Thử thêm ngoài test của Thợ Máy (``tests/test_images_process.py``):

- LC-T049-1: thẻ Ref GPS sai khuôn nhiều kiểu (chữ thường, rỗng, có dấu cách, là số, hai chữ,
  10 thẻ Ref, ghi sai kiểu TIFF như bytes, SHORT, LONG, ASCII đệm null) với cả 4 định dạng ảnh
  → bỏ cả khối GPS và báo ``WebImage.notice``. Đối chứng: ảnh có đủ 10 thẻ Ref đúng khuôn giữ
  GPS đúng từng giá trị.
- LC-T049-2: ``PreviewCache.get`` từ chối mọi phiên bản Pillow dưới 13 kể cả khi cache tắt hay
  ảnh đã có trong cache, không đụng thư mục ảnh; Pillow 13, 14 vẫn dùng được.
- LC-T049-3: nhiều luồng mở ảnh thật cùng lúc (không làm chậm ``Image.open``): mỗi ảnh giữ đúng
  GPS của mình, cảnh báo "bom giải nén" luôn thành lỗi ở mọi luồng, bộ lọc chung không đổi, khóa
  được trả kể cả khi ``Image.open`` ném ``BaseException``, không treo.
- N1, N4 (Thợ Máy làm thêm): biên của ``GPSMapDatum``/``GPSSatellites``; ``memoryview`` nhiều
  kiểu phần tử, nhiều chiều, không liền mạch.

Ảnh đều tạo ngay trong test, tọa độ GPS là tọa độ giả, không gọi mạng.

Lỗi tìm thấy đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T067-n`` (xem
``docs/team/reports/T-067-soi-loi.md``): sửa xong thì test tự báo XPASS để gỡ dấu.
"""

import struct
import threading
import time
import warnings

import PIL
import pytest
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational as R

from seo_app.images import process
from seo_app.images.folders import ImageLibrary
from tests.test_soi_loi_t049 import (  # noqa: F401  (fixture tự dùng: trả nguyên bảng Pillow)
    KINH_DO,
    VI_DO,
    _anh_bon_mau,
    _exif_gps,
    _gps,
    _kiem_toa_do,
    _loi,
    _luu,
    _mo,
    _nguon,
    _thu_vien,
    _tra_nguyen_trang_pillow,
)

G = ExifTags.GPS
DINH_DANG = ["JPEG", "PNG", "WEBP", "HEIF"]


def _khong_con_gps(web):
    """Ảnh ra không còn khối GPS; phần còn lại (hãng, đời máy) vẫn giữ."""
    assert web.gps is None and not web.has_gps
    assert web.notice == process._NOTICE_GPS_BROKEN
    exif = _mo(web.data).getexif()
    assert ExifTags.IFD.GPSInfo not in exif
    assert exif[ExifTags.Base.Make] == "samsung"


def _exif_du_10_the_ref(ban_cau="SW", do_cao=b"\x01"):
    """EXIF có đủ 10 thẻ Ref của chuẩn GPS (đúng khuôn) cùng giá trị đi kèm."""
    exif = _exif_gps(ban_cau[0], ban_cau[1], do_cao)
    g = exif.get_ifd(ExifTags.IFD.GPSInfo)
    g[G.GPSTrackRef], g[G.GPSTrack] = "M", R(1805, 10)
    g[G.GPSDestLatitudeRef], g[G.GPSDestLatitude] = ban_cau[0], VI_DO["dms"]
    g[G.GPSDestLongitudeRef], g[G.GPSDestLongitude] = ban_cau[1], KINH_DO["dms"]
    g[G.GPSDestDistanceRef], g[G.GPSDestDistance] = "N", R(25, 10)
    return exif


# ----- LC-T049-1: thẻ Ref GPS sai khuôn ------------------------------------------------------

REF_DU_10 = (
    G.GPSLatitudeRef,
    G.GPSLongitudeRef,
    G.GPSAltitudeRef,
    G.GPSSpeedRef,
    G.GPSTrackRef,
    G.GPSImgDirectionRef,
    G.GPSDestLatitudeRef,
    G.GPSDestLongitudeRef,
    G.GPSDestBearingRef,
    G.GPSDestDistanceRef,
)

REF_SAI = {
    "vi-do-s-thuong": (G.GPSLatitudeRef, "s"),
    "kinh-do-w-thuong": (G.GPSLongitudeRef, "w"),
    "kinh-do-e-thuong": (G.GPSLongitudeRef, "e"),
    "vi-do-rong": (G.GPSLatitudeRef, ""),
    "vi-do-co-dau-cach": (G.GPSLatitudeRef, "N "),
    "vi-do-la-so": (G.GPSLatitudeRef, "1"),
    "vi-do-hai-chu": (G.GPSLatitudeRef, "SS"),
    "vi-do-chu-khac": (G.GPSLatitudeRef, "X"),
    # Không dùng 2, 3: ExifTool (bảng GPS hiện hành) ghi 2, 3 là "mức nước biển" (Exif 3.0), xem
    # ghi nhận trong báo cáo Soi Lỗi T-067. 4 và 255 sai ở mọi phiên bản.
    "do-cao-4": (G.GPSAltitudeRef, b"\x04"),
    "do-cao-ff": (G.GPSAltitudeRef, b"\xff"),
    "do-cao-hai-byte": (G.GPSAltitudeRef, b"\x00\x01"),
    "huong-di-t-thuong": (G.GPSTrackRef, "t"),
    "huong-anh-x": (G.GPSImgDirectionRef, "X"),
    "toc-do-kmh-viet-thuong": (G.GPSSpeedRef, "km"),
    "kinh-do-dich-w-thuong": (G.GPSDestLongitudeRef, "w"),
    "goc-dich-m-thuong": (G.GPSDestBearingRef, "m"),
    "khoang-cach-dich-k-thuong": (G.GPSDestDistanceRef, "k"),
}


def _nguon_ref_sai(dinh_dang, ten):
    the, gia_tri = REF_SAI[ten]
    exif = _exif_du_10_the_ref()
    exif.get_ifd(ExifTags.IFD.GPSInfo)[the] = gia_tri
    data = _nguon(dinh_dang, exif.tobytes())
    assert _gps(data)[the] == gia_tri  # ảnh gốc mang đúng thẻ sai khuôn
    return data


@pytest.mark.parametrize("ten", list(REF_SAI))
def test_ref_sai_khuon_nhieu_kieu_bo_ca_khoi_gps_va_bao(ten):
    _khong_con_gps(process.make_web_image(_nguon_ref_sai("JPEG", ten)))


@pytest.mark.parametrize("dinh_dang", ["PNG", "WEBP", "HEIF"])
@pytest.mark.parametrize(
    "ten", ["vi-do-s-thuong", "vi-do-co-dau-cach", "do-cao-4", "huong-di-t-thuong"]
)
def test_ref_sai_khuon_moi_dinh_dang_bo_ca_khoi_gps_va_bao(dinh_dang, ten):
    _khong_con_gps(process.make_web_image(_nguon_ref_sai(dinh_dang, ten)))


def _ghi_tho(exif_bytes, the, cu, moi):
    """Sửa thẳng một mục của khối GPS trong EXIF (kiểu, số phần tử, 4 byte giá trị).

    Pillow luôn ghi đúng kiểu theo chuẩn, nên ảnh "ghi sai kiểu" phải dựng bằng cách sửa byte.
    """
    truoc = struct.pack(">HHI", the, *cu[:2]) + cu[2]
    sau = struct.pack(">HHI", the, *moi[:2]) + moi[2]
    assert exif_bytes[6:8] == b"MM" and exif_bytes.count(truoc) == 1
    return exif_bytes.replace(truoc, sau)


_VI_DO_S = (2, 2, b"S\x00\x00\x00")  # ASCII, 2 ký tự ("S" + null)
_DO_CAO_1 = (1, 1, b"\x01\x00\x00\x00")  # BYTE, 1 byte
GHI_SAI_KIEU = {
    # tên: (thẻ, mục gốc, mục sửa, giá trị Pillow đọc lại từ ảnh gốc)
    "vi-do-kieu-undefined": (G.GPSLatitudeRef, _VI_DO_S, (7, 1, b"S\x00\x00\x00"), b"S"),
    "vi-do-kieu-byte": (G.GPSLatitudeRef, _VI_DO_S, (1, 1, b"S\x00\x00\x00"), b"S"),
    "vi-do-kieu-short": (G.GPSLatitudeRef, _VI_DO_S, (3, 1, b"\x00\x53\x00\x00"), 83),
    "vi-do-dem-null": (G.GPSLatitudeRef, _VI_DO_S, (2, 4, b"S\x00\x00\x00"), "S\x00\x00"),
    "do-cao-undefined-2-byte": (G.GPSAltitudeRef, _DO_CAO_1, (7, 2, _DO_CAO_1[2]), b"\x01\x00"),
    "do-cao-byte-2-phan-tu": (G.GPSAltitudeRef, _DO_CAO_1, (1, 2, _DO_CAO_1[2]), b"\x01\x00"),
    "do-cao-ascii": (G.GPSAltitudeRef, _DO_CAO_1, (2, 2, b"1\x00\x00\x00"), "1"),
    "do-cao-sbyte": (G.GPSAltitudeRef, _DO_CAO_1, (6, 1, b"\x01\x00\x00\x00"), 1),
    "do-cao-long": (G.GPSAltitudeRef, _DO_CAO_1, (4, 1, b"\x00\x00\x00\x01"), 1),
}


@pytest.mark.parametrize("dinh_dang", DINH_DANG)
@pytest.mark.parametrize("ten", list(GHI_SAI_KIEU))
def test_ref_ghi_sai_kieu_tiff_bo_ca_khoi_gps_va_bao(dinh_dang, ten):
    the, cu, moi, doc_lai = GHI_SAI_KIEU[ten]
    exif = _ghi_tho(_exif_gps("S", "W", b"\x01").tobytes(), the, cu, moi)
    data = _nguon(dinh_dang, exif)
    assert _gps(data)[the] == doc_lai
    _khong_con_gps(process.make_web_image(data))


@pytest.mark.parametrize("dinh_dang", DINH_DANG)
@pytest.mark.parametrize("ban_cau", ["NE", "SW"])
def test_du_10_the_ref_dung_khuon_giu_gps_dung_tung_gia_tri(dinh_dang, ban_cau):
    # Đối chứng: lớp kiểm mới không làm mất GPS của ảnh ghi đúng chuẩn (quyết định 2A).
    do_cao = b"\x00" if ban_cau == "NE" else b"\x01"
    data = _nguon(dinh_dang, _exif_du_10_the_ref(ban_cau, do_cao).tobytes())
    goc = _gps(data)
    assert all(the in goc for the in REF_DU_10)
    web = process.make_web_image(data)
    assert _gps(web.data) == goc
    _kiem_toa_do(web, goc)
    assert (web.gps.latitude < 0) == (ban_cau == "SW")


def test_ref_ghi_kieu_ascii_mot_ky_tu_khong_null_van_giu():
    # Có phần mềm ghi "S" không kèm null (1 ký tự): Pillow đọc ra "S", vẫn đúng khuôn.
    exif = _ghi_tho(
        _exif_gps("S", "W", b"\x01").tobytes(), G.GPSLatitudeRef, _VI_DO_S, (2, 1, b"S\x00\x00\x00")
    )
    data = _nguon("JPEG", exif)
    goc = _gps(data)
    assert goc[G.GPSLatitudeRef] == "S"
    web = process.make_web_image(data)
    assert _gps(web.data) == goc
    _kiem_toa_do(web, goc)


def _exif_khong_toa_do(the, gia_tri):
    """Máy tắt định vị: khối GPS chỉ có phiên bản và một thẻ phụ (không có vĩ độ, kinh độ)."""
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "samsung"
    g = exif.get_ifd(ExifTags.IFD.GPSInfo)
    g[G.GPSVersionID] = b"\x02\x03\x00\x00"
    g[the] = gia_tri
    return exif.tobytes()


def _gps_khong_toa_do(the, gia_tri):
    data = _nguon("JPEG", _exif_khong_toa_do(the, gia_tri))
    goc = _gps(data)
    assert goc[the] == gia_tri
    assert G.GPSLatitude not in goc and G.GPSLongitude not in goc
    web = process.make_web_image(data)
    assert web.gps is None and _gps(web.data) == {}  # không có vị trí nào để giữ
    return web


@pytest.mark.parametrize(("the", "gia_tri"), [(G.GPSAltitudeRef, b"\x00"), (G.GPSSpeedRef, "K")])
def test_khong_co_toa_do_ref_phu_dung_khuon_khong_bao_hong(the, gia_tri):
    assert _gps_khong_toa_do(the, gia_tri).notice == ""


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="SL-T067-1: ảnh không có tọa độ (máy tắt định vị) mà có thẻ Ref phụ sai khuôn bị báo "
    "'GPS hỏng'; T-049 chỉ báo khi ảnh gốc có ghi tọa độ (process.py:502-507)",
)
@pytest.mark.parametrize(
    ("the", "gia_tri"),
    [
        (G.GPSSpeedRef, "k"),
        (G.GPSAltitudeRef, b"\x04"),
        (G.GPSImgDirectionRef, "t"),
        (G.GPSDestLatitudeRef, "s"),
    ],
)
def test_khong_co_toa_do_ma_ref_phu_sai_khuon_khong_bao_hong(the, gia_tri):
    # Như ``test_khoi_gps_khong_co_toa_do_thi_bo_khong_bao_hong`` (T-049): không có vị trí để giữ
    # thì không báo "hỏng". Thẻ Ref phụ sai khuôn ở đây không làm sai vị trí nào (không có vị trí);
    # câu "Thông tin GPS của ảnh gốc bị hỏng" làm chủ dự án tưởng máy ghi định vị lỗi.
    assert _gps_khong_toa_do(the, gia_tri).notice == ""


# ----- LC-T049-2: PreviewCache.get kiểm Pillow trước cache ------------------------------------


@pytest.mark.parametrize("phien_ban", ["12.3.0", "12.99.99", "9.5.0", "11.0", "0.1"])
def test_cache_moi_phien_ban_duoi_13_tu_choi_ca_khi_cache_tat(tmp_path, monkeypatch, phien_ban):
    library, refs = _thu_vien(tmp_path, {"a.jpg": _luu(_anh_bon_mau((200, 150)), "JPEG")})
    co_cache = process.PreviewCache(tmp_path / "cache")
    assert co_cache.enabled
    dung = co_cache.get(library, refs["a.jpg"])  # cache có sẵn
    tat_cache = process.PreviewCache(tmp_path / "cache-tat")
    tat_cache.enabled = False
    goi = []
    with monkeypatch.context() as m:
        m.setattr(ImageLibrary, "stat_image", lambda *a: goi.append("stat"))
        m.setattr(ImageLibrary, "read_image_bytes", lambda *a: goi.append("doc"))
        m.setattr(PIL, "__version__", phien_ban)
        for cache in (co_cache, tat_cache):
            assert _loi(cache.get, library, refs["a.jpg"]) == process._MSG_OLD_PILLOW
    assert goi == []  # không đụng thư mục ảnh
    assert not (tmp_path / "cache-tat").exists()
    assert co_cache.get(library, refs["a.jpg"]) == dung  # Pillow 13 trở lại: dùng lại cache


@pytest.mark.parametrize("phien_ban", ["13.0.0", "13.2.1", "14.0.0", "20.1.0.dev0"])
def test_cache_pillow_13_tro_len_van_tra_anh(tmp_path, monkeypatch, phien_ban):
    library, refs = _thu_vien(tmp_path, {"a.jpg": _luu(_anh_bon_mau((200, 150)), "JPEG")})
    cache = process.PreviewCache(tmp_path / "cache")
    dung = cache.get(library, refs["a.jpg"])
    monkeypatch.setattr(PIL, "__version__", phien_ban)
    assert cache.get(library, refs["a.jpg"]) == dung


# ----- LC-T049-3: nhiều luồng mở ảnh cùng lúc ------------------------------------------------


def _chay_song_song(viec, cong_viec, so_luong=8, cho=120):
    """Chạy ``viec(x)`` cho mọi ``x`` trên ``so_luong`` luồng nền; luồng treo thì test hỏng.

    Không dùng ``ThreadPoolExecutor``: nếu khóa bị giữ mãi thì nó chờ luồng mãi (test treo).
    """
    hang = list(enumerate(cong_viec))
    khoa = threading.Lock()
    ket_qua, loi = {}, []

    def chay():
        while True:
            with khoa:
                if not hang:
                    return
                so, x = hang.pop()
            try:
                ket_qua[so] = viec(x)
            except BaseException as exc:  # noqa: BLE001
                loi.append((x, exc))

    luong = [threading.Thread(target=chay, daemon=True) for _ in range(so_luong)]
    for t in luong:
        t.start()
    for t in luong:
        t.join(cho)
    assert not any(t.is_alive() for t in luong), "có luồng treo (khóa không được trả?)"
    return [ket_qua[so] for so in sorted(ket_qua)], loi


def _lam_cham_image_open(monkeypatch, giay=0.002):
    """``Image.open`` chậm đi chút (đĩa USB, máy yếu) để các luồng kịp chen nhau trong khối."""
    mo_that = Image.open

    def mo_cham(*args, **kwargs):
        time.sleep(giay)
        try:
            return mo_that(*args, **kwargs)
        finally:
            time.sleep(giay)

    monkeypatch.setattr(Image, "open", mo_cham)


def _exif_vi_tri(i):
    """Mỗi ảnh một vị trí riêng (giả) để biết luồng này không lấy nhầm GPS của luồng kia."""
    exif = _exif_gps("S" if i % 2 else "N", "W" if i % 3 == 0 else "E")
    g = exif.get_ifd(ExifTags.IFD.GPSInfo)
    g[G.GPSLatitude] = (R(10, 1), R(i, 1), R(1000 + i, 100))
    g[G.GPSLongitude] = (R(106, 1), R(59 - i, 1), R(2000 + 7 * i, 100))
    return exif.tobytes()


def test_nhieu_luong_anh_that_moi_anh_giu_dung_gps_cua_minh_khong_treo(monkeypatch):
    nguon = [_nguon(DINH_DANG[i % 4], _exif_vi_tri(i)) for i in range(24)]
    goc = [_gps(data) for data in nguon]
    _lam_cham_image_open(monkeypatch)

    def viec(i):
        data = nguon[i]
        web = process.make_web_image(data)
        ai = process.make_ai_image(data)
        xem = process.make_preview(data)
        return i, web, ai, xem

    with warnings.catch_warnings():  # có lỗi thật thì bộ lọc thừa không lan sang test khác
        truoc = list(warnings.filters)
        ket_qua, loi = _chay_song_song(viec, [i for i in range(24) for _ in range(3)])
        sau = list(warnings.filters)
    assert loi == []
    assert sau == truoc
    assert not process._WARNINGS_LOCK.locked()
    assert len(ket_qua) == 72
    for i, web, ai, xem in ket_qua:
        assert _gps(web.data) == goc[i]
        _kiem_toa_do(web, goc[i])
        assert b"GPS" not in ai.data and b"Exif" not in ai.data
        assert process.jpeg_layout(xem) == (64, 48)


def test_nhieu_luong_canh_bao_bom_luon_thanh_loi_o_moi_luong(monkeypatch):
    # Hạ giới hạn của Pillow: ảnh 40×30 (1.200 điểm ảnh) chỉ gây ``DecompressionBombWarning``
    # (chưa tới 2 lần giới hạn nên chưa phải ``DecompressionBombError``). Phép so của app được nới
    # để chỉ còn bộ lọc "cảnh báo thành lỗi" chặn. Luồng nào lỡ mở ảnh lúc bộ lọc bị luồng khác
    # gỡ (LC-T049-3 (b)) sẽ xử lý được ảnh thay vì báo lỗi.
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1000)
    monkeypatch.setattr(process, "MAX_IMAGE_PIXELS", 10**9)
    bom = {d: _luu(_anh_bon_mau((40, 30)), d) for d in DINH_DANG}
    nho = _luu(_anh_bon_mau((20, 20)), "PNG")  # 400 điểm ảnh: mở bình thường
    _lam_cham_image_open(monkeypatch)

    def viec(ten):
        if ten == "nho":
            return ten, process.jpeg_layout(process.make_preview(nho))
        with pytest.raises(process.ImageProcessError) as info:
            process.make_preview(bom[ten])
        return ten, str(info.value)

    cong_viec = [ten for _ in range(40) for ten in [*DINH_DANG, "nho"]]
    with warnings.catch_warnings():
        truoc = list(warnings.filters)
        ket_qua, loi = _chay_song_song(viec, cong_viec)
        sau = list(warnings.filters)
    assert loi == []
    assert sau == truoc
    assert not process._WARNINGS_LOCK.locked()
    assert len(ket_qua) == len(cong_viec)
    for ten, ra in ket_qua:
        if ten == "nho":
            assert ra == (20, 20)
        else:
            assert ra.startswith("Ảnh có quá nhiều điểm ảnh"), (ten, ra)


class _DungGiuaChung(BaseException):
    """Lỗi kiểu ``BaseException`` (như ``KeyboardInterrupt``, ``SystemExit``) giữa lúc mở ảnh."""


def test_image_open_nem_base_exception_van_tra_khoa_va_bo_loc(monkeypatch):
    data = _luu(_anh_bon_mau((20, 20)), "PNG")
    truoc = list(warnings.filters)

    def nem(*_args, **_kwargs):
        raise _DungGiuaChung

    with monkeypatch.context() as m:
        m.setattr(Image, "open", nem)
        with pytest.raises(_DungGiuaChung):
            process.make_preview(data)
    assert not process._WARNINGS_LOCK.locked()
    assert list(warnings.filters) == truoc
    # Lần mở sau (luồng khác) không treo.
    ket_qua, loi = _chay_song_song(process.make_preview, [data] * 4, so_luong=2, cho=30)
    assert loi == [] and all(process.jpeg_layout(x) == (20, 20) for x in ket_qua)


# ----- N1, N4 (Thợ Máy làm thêm) -------------------------------------------------------------


@pytest.mark.parametrize(
    ("the", "gia_tri", "giu"),
    [
        (G.GPSMapDatum, "A" * 16, True),
        (G.GPSMapDatum, "A" * 17, False),
        (G.GPSMapDatum, "WGS84", True),
        (G.GPSMapDatum, "WGS-84\n", False),
        (G.GPSMapDatum, "WGS_84", False),
        (G.GPSMapDatum, "", False),
        (G.GPSSatellites, "1,2,3", True),
        (G.GPSSatellites, "9" * 64, True),
        (G.GPSSatellites, "9" * 65, False),
        (G.GPSSatellites, "05 ", False),
        (G.GPSSatellites, "", False),
    ],
)
def test_n1_bien_the_chu_gps_chi_bo_the_do_vi_tri_van_giu(the, gia_tri, giu):
    exif = _exif_gps("S", "W", b"\x01")
    exif.get_ifd(ExifTags.IFD.GPSInfo)[the] = gia_tri
    data = _nguon("JPEG", exif.tobytes())
    goc = _gps(data)
    assert goc[the] == gia_tri
    web = process.make_web_image(data)
    _kiem_toa_do(web, goc)  # vị trí vẫn giữ, không báo hỏng
    ra = _gps(web.data)
    assert (the in ra) == giu
    assert ra == ({k: v for k, v in goc.items() if k != the} | ({the: gia_tri} if giu else {}))


def _png_dem(boi):
    """PNG thật, thêm byte 0 sau IEND cho tròn bội ``boi`` (Pillow bỏ qua phần sau IEND)."""
    png = _luu(_anh_bon_mau((40, 30)), "PNG")
    return png + b"\x00" * (-len(png) % boi)


@pytest.mark.parametrize("kieu", ["B", "H", "I", "Q", "2-chieu"])
def test_n4_memoryview_moi_kieu_phan_tu_mo_dung_va_do_theo_byte(monkeypatch, kieu):
    data = _png_dem(8)
    if kieu == "2-chieu":
        view = memoryview(data).cast("B", shape=[len(data) // 8, 8])
    else:
        view = memoryview(data).cast(kieu)
    assert view.nbytes == len(data)
    assert process.jpeg_layout(process.make_preview(view)) == (40, 30)
    monkeypatch.setattr(process, "MAX_IMAGE_BYTES", len(data) - 1)
    assert _loi(process.make_preview, view).startswith("Ảnh quá lớn")
    monkeypatch.setattr(process, "MAX_IMAGE_BYTES", len(data))
    assert process.jpeg_layout(process.make_preview(view)) == (40, 30)


def test_n4_memoryview_khong_lien_mach_bao_cau_co_dinh():
    view = memoryview(_png_dem(8))[::2]  # mỗi byte lấy một: không còn là PNG
    assert view.nbytes == len(bytes(view))
    assert _loi(process.make_preview, view) in {process._MSG_NOT_IMAGE, process._MSG_BROKEN}

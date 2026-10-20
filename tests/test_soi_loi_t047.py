"""Soi Lỗi T-047: ảnh HEIC hỏng hoặc giả mạo không làm treo hay sập tiến trình.

Mọi ảnh là ảnh giả tạo trong ``tmp_path`` (không commit ảnh thật, không gọi mạng).
Bảng định dạng của Pillow được trả nguyên trạng sau mỗi test (xem ``heif_registry_restored``
trong ``test_pillow_heif_setup.py``; ở đây chép lại để file chạy độc lập).

Ghi nhận cho G3-3 (code mở ảnh thật): file HEIC **bị cắt cụt** vẫn qua ``Image.open`` (chỉ đọc
phần đầu), lỗi chỉ nổ ra ở ``load()`` và là ``ValueError`` của pillow-heif, **không phải**
``OSError`` như ảnh JPEG cắt cụt. Code thật phải bắt cả hai.
"""

import io
import json
import subprocess
import sys
import textwrap

import pillow_heif
import pytest
from PIL import Image, UnidentifiedImageError

_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")

# Lỗi mà code mở ảnh được phép gặp với file hỏng (đều bắt được, không sập tiến trình).
_LOI_BINH_THUONG = (OSError, ValueError)


@pytest.fixture
def heif_registered():
    """Đăng ký HEIF vào Pillow trong phạm vi một test, sau đó trả lại bảng định dạng cũ."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _REGISTRIES}
    pillow_heif.register_heif_opener()
    yield
    for name, value in saved.items():
        current = getattr(Image, name)
        current.clear()
        if isinstance(current, dict):
            current.update(value)
        else:
            current.extend(value)


def _anh_mau(size=(320, 240)):
    """Ảnh RGB có hoa văn (để HEVC phải mã hóa dữ liệu thật, file đủ dài để cắt)."""
    image = Image.new("RGB", size, (200, 120, 40))
    for x in range(0, size[0], 7):
        for y in range(0, size[1], 5):
            image.putpixel((x, y), (x % 256, y % 256, 50))
    return image


def _heic_bytes(size=(320, 240)):
    buf = io.BytesIO()
    pillow_heif.from_pillow(_anh_mau(size)).save(buf, quality=80)
    return buf.getvalue()


def _bytes_theo_dinh_dang(fmt):
    buf = io.BytesIO()
    _anh_mau().save(buf, fmt)
    return buf.getvalue()


def _mo_va_giai_ma(path, formats=None):
    with Image.open(path, formats=formats) as image:
        image.load()
        return image.format, image.size


# --- HEIC hỏng / cắt cụt -------------------------------------------------------------------


@pytest.mark.parametrize(
    "cat",
    [
        pytest.param(lambda b: b"", id="file_rong"),
        pytest.param(lambda b: b[:12], id="chi_12_byte_dau"),
        pytest.param(lambda b: b[:100], id="100_byte_dau"),
        pytest.param(lambda b: b[: len(b) // 2], id="mot_nua"),
        pytest.param(lambda b: b[:-10], id="thieu_10_byte_cuoi"),
        pytest.param(lambda b: b[:40] + b"\x00" * 5000, id="dau_that_than_toan_so_0"),
    ],
)
def test_heic_cat_cut_bao_loi_binh_thuong(tmp_path, heif_registered, cat):
    path = tmp_path / "hong.heic"
    path.write_bytes(cat(_heic_bytes()))
    with pytest.raises(_LOI_BINH_THUONG):
        _mo_va_giai_ma(path, formats=["HEIF"])


def test_heic_cat_cut_qua_duoc_open_chi_hong_o_load(tmp_path, heif_registered):
    """Ghi nhận hành vi cho G3-3: phải gọi ``load()`` trong khối bắt lỗi, không chỉ ``open``."""
    data = _heic_bytes()
    path = tmp_path / "mot_nua.heic"
    path.write_bytes(data[: len(data) // 2])
    with Image.open(path, formats=["HEIF"]) as image:
        assert image.format == "HEIF"
        with pytest.raises(_LOI_BINH_THUONG):
            image.load()


def test_heic_hong_du_lieu_giua_file_khong_treo(tmp_path, heif_registered):
    """Đảo bit giữa phần dữ liệu ảnh: bộ giải mã có thể ra ảnh rác hoặc báo lỗi, không được treo."""
    data = bytearray(_heic_bytes())
    giua = len(data) // 2
    for i in range(giua, giua + 200):
        data[i] ^= 0xFF
    path = tmp_path / "dao_bit.heic"
    path.write_bytes(bytes(data))
    try:
        fmt, size = _mo_va_giai_ma(path, formats=["HEIF"])
    except _LOI_BINH_THUONG:
        return
    assert fmt == "HEIF"
    assert size == (320, 240)


# --- File không phải HEIC nhưng mang đuôi .heic -------------------------------------------


@pytest.mark.parametrize("fmt", ["JPEG", "PNG", "WEBP"])
def test_anh_khac_doi_duoi_heic_khong_bi_nhan_la_heif(tmp_path, heif_registered, fmt):
    path = tmp_path / "gia.heic"
    path.write_bytes(_bytes_theo_dinh_dang(fmt))
    # Pillow nhận theo nội dung, không theo đuôi file.
    assert _mo_va_giai_ma(path) == (fmt, (320, 240))
    # Chỉ cho phép HEIF thì phải từ chối.
    with pytest.raises(UnidentifiedImageError):
        _mo_va_giai_ma(path, formats=["HEIF"])


@pytest.mark.parametrize(
    "noi_dung",
    [
        pytest.param("xin chào <script>alert(1)</script>".encode(), id="chu_tieng_viet_html"),
        pytest.param(bytes(range(256)) * 20, id="byte_ngau_nhien"),
        pytest.param(b"%PDF-1.7\n" + b"0" * 2000, id="pdf"),
        pytest.param(b"\x00\x00\x00\x18ftypheic" + b"\xff" * 2000, id="ftyp_heic_gia"),
    ],
)
def test_file_rac_doi_duoi_heic_bi_tu_choi(tmp_path, heif_registered, noi_dung):
    path = tmp_path / "rac.heic"
    path.write_bytes(noi_dung)
    with pytest.raises(UnidentifiedImageError):
        _mo_va_giai_ma(path)
    with pytest.raises(UnidentifiedImageError):
        _mo_va_giai_ma(path, formats=["HEIF"])


# --- Không sập tiến trình (lỗi C trong libheif/libde265 sẽ giết cả pytest) -----------------

_SCRIPT_TIEN_TRINH_CON = textwrap.dedent(
    """
    import json, pathlib, sys
    from PIL import Image
    import pillow_heif

    pillow_heif.register_heif_opener()
    ket_qua = {}
    for path in sorted(pathlib.Path(sys.argv[1]).glob("*.heic")):
        try:
            with Image.open(path, formats=["HEIF"]) as image:
                image.load()
            ket_qua[path.name] = "ok"
        except Exception as exc:
            ket_qua[path.name] = type(exc).__name__
    print(json.dumps(ket_qua))
    """
)


def test_heic_hong_khong_lam_sap_hay_treo_tien_trinh(tmp_path):
    data = _heic_bytes()
    dao_bit = bytearray(data)
    for i in range(len(data) // 3, len(data) // 3 + 500):
        dao_bit[i] ^= 0x5A
    mau = {
        "rong.heic": b"",
        "mot_nua.heic": data[: len(data) // 2],
        "thieu_cuoi.heic": data[:-1],
        "dao_bit.heic": bytes(dao_bit),
        "duoi_so_0.heic": data[: len(data) - 2000] + b"\x00" * 2000,
        "jpeg_doi_duoi.heic": _bytes_theo_dinh_dang("JPEG"),
    }
    thu_muc = tmp_path / "mau"
    thu_muc.mkdir()
    for ten, noi_dung in mau.items():
        (thu_muc / ten).write_bytes(noi_dung)

    proc = subprocess.run(
        [sys.executable, "-I", "-c", _SCRIPT_TIEN_TRINH_CON, str(thu_muc)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    ket_qua = json.loads(proc.stdout.strip().splitlines()[-1])
    assert set(ket_qua) == set(mau)
    # Mọi lỗi đều là lỗi Python bắt được, thuộc nhóm lỗi bình thường.
    cho_phep = {"ok", "UnidentifiedImageError", "OSError", "ValueError", "SyntaxError"}
    assert set(ket_qua.values()) <= cho_phep, ket_qua
    for ten in ("rong.heic", "mot_nua.heic", "thieu_cuoi.heic", "jpeg_doi_duoi.heic"):
        assert ket_qua[ten] != "ok", ket_qua

"""Xử lý ảnh thật trước khi dùng (phiếu T-049, thiết kế T-046 mục 2, ``security.md`` F2, A3).

Ba loại ảnh ra, đều **dựng lại từ điểm ảnh** (không chép khối dữ liệu nào của file gốc):

- Ảnh đăng web (``make_web_image``): xoay đúng chiều, cạnh dài tối đa 1600 px (quyết định 5A),
  WebP, kèm EXIF đã lọc theo quyết định 2A: giữ GPS, ngày chụp, hãng và đời máy; bỏ mọi thứ
  khác (số seri, tên chủ máy, MakerNote, ảnh nhỏ IFD1…). Sau khi nén, đọc lại file WebP và so
  **từng giá trị** GPS với ảnh gốc; lệch là dừng (sổ rủi ro ``security.md`` mục 6: giữ GPS có
  chủ đích; góp ý Lá Chắn T-046 số 2).
- Bản gửi AI viết alt (``make_ai_image``): cạnh dài 1024 px, JPEG, không EXIF, XMP, chú thích,
  hồ sơ màu ICC (A3; góp ý Lá Chắn T-046 số 1; SL-T050-5). Kiểm lại danh sách khối của file JPEG
  trước khi trả.
- Ảnh xem trước trong máy (``make_preview``, ``PreviewCache``): cạnh dài 320 px, JPEG 8 bit, không
  metadata. Đây là thứ duy nhất được đưa vào ``st.image`` (LC-T058-2): Streamlit tự mở byte ảnh
  bằng Pillow không giới hạn định dạng, nên không bao giờ đưa byte gốc hay đường dẫn.

Mở ảnh an toàn (điều kiện Lá Chắn T-047 mục 7, T-048, T-058):

- Từ chối khi Pillow dưới 13 (LC-T058-3).
- Byte ảnh lấy qua ``ImageLibrary.read_image_bytes`` (module này không tự mở đường dẫn ảnh);
  kiểm dung lượng trước khi mở.
- Chỉ nhận ``ALLOWED_FORMATS``: Pillow nhận dạng theo nội dung, không theo đuôi file. Không ghi
  ``"MPO"`` (gây ``KeyError``): ảnh MPO đi qua bộ mở JPEG, và chỉ dùng khung đầu (không ``seek``).
- Giới hạn số điểm ảnh ``MAX_IMAGE_PIXELS`` (kể cả HEIC): tự so ``rộng × cao`` ngay sau khi đọc
  phần đầu file, trước khi giải mã; ``DecompressionBombWarning`` của Pillow cũng thành lỗi.
- Bắt lỗi quanh cả ``open`` lẫn ``load``: ``OSError``, ``ValueError`` (HEIC cụt), và
  ``DecompressionBombError`` (không phải con của ``OSError``). Câu báo tiếng Việt cố định, không
  chép câu lỗi gốc hay đường dẫn.
- HEIF đăng ký ở đúng một chỗ (``_register_heif``), tắt ảnh nhỏ, ảnh độ sâu, ảnh phụ; không gọi
  ``load_libheif_plugin``, không bật ``DISABLE_SECURITY_LIMITS``, không ghi file HEIC.
- Không xuất ảnh sang Arrow, không đặt hay đọc ``PILLOW_ALIGNMENT`` (LC-T058-1).
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import struct
import tempfile
import threading
import warnings
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import PIL
import pillow_heif
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from pillow_heif import options as heif_options

from seo_app.config import PROJECT_ROOT
from seo_app.images.folders import MAX_IMAGE_BYTES, ImageLibrary, ImageRef

MIN_PILLOW_MAJOR = 13  # T-058: Pillow 13 vá các khuyến cáo của 12.3.0
# Định dạng được mở (Lá Chắn T-047 điều kiện 4). Không có AVIF: máy ảnh, điện thoại của đội không
# chụp AVIF, thêm vào là thêm thư viện giải mã phải lo.
ALLOWED_FORMATS = ("JPEG", "PNG", "WEBP", "HEIF")
# 80 triệu điểm ảnh: đủ cho máy 48–64 MP (iPhone 48 MP = 8064 × 6048). Thấp hơn ngưỡng cảnh báo
# mặc định của Pillow (89.478.485) nên luôn là phép so của module này quyết định, câu báo rõ ràng.
MAX_IMAGE_PIXELS = 80_000_000

WEB_MAX_EDGE_PX = 1600  # quyết định 5A; T-051 đưa vào config/content.toml [images] max_edge_px
WEB_WEBP_QUALITY = 80  # T-051: config/content.toml [images] webp_quality
WEB_WEBP_METHOD = 6  # nén kỹ nhất (chậm hơn một chút, file nhỏ hơn)
AI_MAX_EDGE_PX = 1024
AI_JPEG_QUALITY = 85
PREVIEW_MAX_EDGE_PX = 320
PREVIEW_JPEG_QUALITY = 80
MIN_EDGE_PX = 16
MAX_EDGE_PX = 4096
MAX_ICC_BYTES = 1024 * 1024  # hồ sơ màu lớn hơn thì bỏ (hồ sơ của máy ảnh chỉ vài KB)

# Thư mục cache ảnh xem trước: nằm trong ``data/`` (đã có trong ``.gitignore``, góp ý Lá Chắn
# T-046 số 9). ``PreviewCache`` kiểm lại điều này mỗi khi tạo (xem ``_cache_dir_is_ignored``).
PREVIEW_CACHE_DIR = PROJECT_ROOT / "data" / "image_previews"
_PREVIEW_CACHE_VERSION = 1  # đổi cách làm ảnh xem trước thì tăng số này để bỏ cache cũ
_MAX_CACHED_PREVIEW_BYTES = 2 * 1024 * 1024

# LC-T049-3: ``warnings.catch_warnings`` sửa bộ lọc cảnh báo của cả chương trình rồi trả lại bản
# đã lưu khi ra khối, nên không an toàn khi nhiều luồng (Python 3.12; Streamlit chạy mỗi phiên
# một luồng): luồng ra sau trả lại bộ lọc của luồng kia. Khóa giữ mỗi lúc chỉ một luồng trong khối.
_WARNINGS_LOCK = threading.Lock()

_MSG_OLD_PILLOW = (
    "Thư viện ảnh Pillow đang là bản cũ (dưới 13) nên app không xử lý ảnh để tránh lỗ hổng đã "
    "biết. Hãy tắt app rồi mở lại bằng run.bat hoặc run.command để cập nhật thư viện."
)
_MSG_EMPTY = "File ảnh rỗng (0 byte)."
_MSG_NOT_IMAGE = (
    "File này không phải ảnh JPEG, PNG, WebP hoặc HEIC đọc được (có thể bị đổi đuôi hoặc hỏng)."
)
_MSG_BROKEN = "Ảnh bị hỏng hoặc chưa tải xong (Google Drive chưa đồng bộ?), app không đọc được."
_MSG_ENCODE = "Không nén được ảnh này. Hãy thử ảnh khác."
_MSG_GPS_LOST = (
    "Ảnh gốc có vị trí GPS nhưng bản nén không giữ được đúng vị trí, nên app dừng lại "
    "(không dùng ảnh này)."
)
_NOTICE_EXIF_UNREADABLE = (
    "Không đọc được thông tin EXIF của ảnh gốc (có thể đã hỏng): ảnh nén không có vị trí GPS."
)
_NOTICE_GPS_BROKEN = "Thông tin GPS của ảnh gốc bị hỏng nên ảnh nén không có vị trí GPS."


class ImageProcessError(Exception):
    """Lỗi xử lý ảnh; câu tiếng Việt hiện thẳng được, không chứa đường dẫn hay câu lỗi gốc."""


def _format_mb(size: int) -> str:
    return f"{size / (1024 * 1024):.1f}".replace(".", ",")


def _format_megapixels(pixels: int) -> str:
    return f"{pixels / 1_000_000:.0f}"


# ----- mở ảnh an toàn ------------------------------------------------------------------------


def _require_pillow_13() -> None:
    """LC-T058-3: quay về Pillow 12.x thì từ chối xử lý ảnh (câu báo cố định)."""
    if int(PIL.__version__.split(".")[0]) < MIN_PILLOW_MAJOR:
        raise ImageProcessError(_MSG_OLD_PILLOW)


def _register_heif() -> None:
    """Chỗ duy nhất đăng ký HEIF với Pillow (Lá Chắn T-047 điều kiện 3).

    Gọi trước mỗi lần mở ảnh: tùy chọn của pillow-heif là biến dùng chung cả chương trình nên
    được đặt lại mỗi lần (ai đó bật lại cũng không ăn); bảng định dạng của Pillow chỉ được ghi
    khi HEIF chưa có trong bảng.
    """
    heif_options.THUMBNAILS = False
    heif_options.DEPTH_IMAGES = False
    heif_options.AUX_IMAGES = False
    heif_options.DISABLE_SECURITY_LIMITS = False
    if Image.OPEN.get("HEIF", (None,))[0] is not pillow_heif.HeifImageFile:
        pillow_heif.register_heif_opener(thumbnails=False, depth_images=False, aux_images=False)


def _too_many_pixels(pixels: int | None = None) -> ImageProcessError:
    limit = _format_megapixels(MAX_IMAGE_PIXELS)
    if pixels is None:
        return ImageProcessError(f"Ảnh có quá nhiều điểm ảnh, tối đa {limit} triệu điểm ảnh.")
    return ImageProcessError(
        f"Ảnh có quá nhiều điểm ảnh ({_format_megapixels(pixels)} triệu), tối đa {limit} triệu. "
        "Hãy thu nhỏ ảnh trước."
    )


def _check_source_size(data: object) -> bytes:
    if not isinstance(data, bytes | bytearray | memoryview):
        raise ImageProcessError(_MSG_NOT_IMAGE)
    # N4 (Lá Chắn T-049): ``len`` của ``memoryview`` đếm phần tử, không đếm byte.
    size = data.nbytes if isinstance(data, memoryview) else len(data)
    if size == 0:
        raise ImageProcessError(_MSG_EMPTY)
    if size > MAX_IMAGE_BYTES:
        raise ImageProcessError(
            f"Ảnh quá lớn ({_format_mb(size)} MB), tối đa {_format_mb(MAX_IMAGE_BYTES)} MB."
        )
    return bytes(data)


def _webp_canvas_pixels(data: bytes) -> int | None:
    """Số điểm ảnh khai trong phần đầu file WebP (None nếu không phải WebP đọc được).

    Bộ mở WebP của Pillow tạo bộ giải mã (cấp bộ nhớ cho cả khung ảnh) ngay trong ``Image.open``,
    và lúc đó Pillow chỉ chặn ảnh vượt **gấp đôi** giới hạn chung. Nên phải so trước khi mở.
    """
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":  # 24 bit rộng − 1, 24 bit cao − 1
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
    elif chunk == b"VP8L" and data[20] == 0x2F:  # 14 bit rộng − 1, 14 bit cao − 1
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
    elif chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":  # 14 bit rộng, 14 bit cao
        width = int.from_bytes(data[26:28], "little") & 0x3FFF
        height = int.from_bytes(data[28:30], "little") & 0x3FFF
    else:
        return None
    return width * height


def _pillow_open(data: bytes, formats: tuple[str, ...]) -> Image.Image:
    """``Image.open`` với ``DecompressionBombWarning`` thành lỗi (Lá Chắn T-047 điều kiện 2).

    Khóa ``_WARNINGS_LOCK`` bọc cả khối đổi bộ lọc cảnh báo (LC-T049-3). Với 4 định dạng được mở,
    Pillow chỉ kiểm "bom giải nén" trong ``Image.open`` (``load`` không kiểm), nên khóa chỉ bọc lời
    gọi này: phần giải mã ảnh của các phiên khác nhau vẫn chạy song song.
    """
    with _WARNINGS_LOCK, warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        return Image.open(io.BytesIO(data), formats=list(formats))


def _open(
    data: object, formats: tuple[str, ...] = ALLOWED_FORMATS, draft_edge: int | None = None
) -> Image.Image:
    """Mở và giải mã khung đầu của ảnh; mọi lỗi thành ``ImageProcessError``."""
    _require_pillow_13()
    data = _check_source_size(data)
    canvas = _webp_canvas_pixels(data)
    if canvas is not None and canvas > MAX_IMAGE_PIXELS:
        raise _too_many_pixels(canvas)
    _register_heif()
    try:
        image = _pillow_open(data, formats)
        try:
            pixels = image.width * image.height
            if pixels > MAX_IMAGE_PIXELS:
                raise _too_many_pixels(pixels)
            if draft_edge and image.format in ("JPEG", "MPO"):
                # Giải mã JPEG ở 1/2, 1/4, 1/8 kích thước khi ảnh lớn hơn nhiều so với cần (vẫn
                # không nhỏ hơn ``draft_edge`` ở cả hai cạnh): đỡ RAM, đỡ thời gian.
                image.draft(None, (draft_edge, draft_edge))
            image.load()
        except BaseException:
            image.close()
            raise
    except ImageProcessError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise _too_many_pixels() from None
    except Image.UnidentifiedImageError:
        raise ImageProcessError(_MSG_NOT_IMAGE) from None
    except (OSError, ValueError, SyntaxError, EOFError, struct.error):
        # OSError: JPEG cụt, PNG hỏng; ValueError: HEIC cụt (chỉ nổ lúc ``load``).
        raise ImageProcessError(_MSG_BROKEN) from None
    return image


def open_image(data: bytes) -> Image.Image:
    """Mở an toàn một ảnh (byte từ ``ImageLibrary.read_image_bytes``), trả ảnh đã giải mã.

    Ảnh MPO chỉ có khung đầu. Ảnh trả về vẫn mang metadata gốc trong ``info``: dùng để đọc
    thông tin, **không** đưa thẳng vào ``st.image`` hay lưu lại (dùng ``make_preview``).
    """
    return _open(data)


# ----- EXIF ----------------------------------------------------------------------------------

# Lỗi có thể gặp khi Pillow đọc EXIF hỏng (file ảnh là dữ liệu chưa tin cậy).
_EXIF_ERRORS = (
    SyntaxError,
    ValueError,
    TypeError,
    KeyError,
    IndexError,
    AttributeError,
    OverflowError,
    ZeroDivisionError,
    RecursionError,
    struct.error,
    OSError,
    EOFError,
)

# Cùng bảng với ``PIL.ImageOps.exif_transpose``. Không gọi thẳng hàm đó: nó ghi lại toàn bộ EXIF
# gốc (``exif.tobytes()``) vào ảnh trả về, và nổ ``struct.error``/``TypeError``/``AttributeError``
# với EXIF hỏng (đã thử). Ở đây chỉ cần chiều xoay; EXIF ghi ra được dựng mới (``_KeptExif``).
_TRANSPOSE = {
    2: Image.Transpose.FLIP_LEFT_RIGHT,
    3: Image.Transpose.ROTATE_180,
    4: Image.Transpose.FLIP_TOP_BOTTOM,
    5: Image.Transpose.TRANSPOSE,
    6: Image.Transpose.ROTATE_270,
    7: Image.Transpose.TRANSVERSE,
    8: Image.Transpose.ROTATE_90,
}

_POINTER_TAGS = frozenset({ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo, ExifTags.IFD.Interop})
_DATE_TIME = re.compile(r"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}")
_UTC_OFFSET = re.compile(r"[+-]\d{2}:\d{2}")
_GPS_DATE = re.compile(r"\d{4}:\d{2}:\d{2}")
_MAX_TEXT_CHARS = 64

# Quyết định 2A: giữ hãng, đời máy, ngày chụp. Danh sách cho phép: thẻ nào không có ở đây thì bỏ
# (số seri thân máy và ống kính, CameraOwnerName, Artist, MakerNote, Software, ảnh nhỏ IFD1…).
_BASE_KEEP = {
    ExifTags.Base.Make: "text",
    ExifTags.Base.Model: "text",
    ExifTags.Base.DateTime: "datetime",
}
_EXIF_IFD_KEEP = {
    ExifTags.Base.DateTimeOriginal: "datetime",
    ExifTags.Base.DateTimeDigitized: "datetime",
    ExifTags.Base.OffsetTime: "offset",
    ExifTags.Base.OffsetTimeOriginal: "offset",
    ExifTags.Base.OffsetTimeDigitized: "offset",
}
# GPS: giữ mọi thẻ chuẩn (EXIF 2.32) có giá trị đúng kiểu, để "giữ nguyên GPS". Bỏ 2 thẻ chữ tự do
# GPSProcessingMethod (27), GPSAreaInformation (28) và thẻ lạ ngoài chuẩn: chúng chở được chữ bất
# kỳ (kể cả địa chỉ viết tay), điện thoại hầu như không ghi.
_GPS_KEEP = {
    ExifTags.GPS.GPSVersionID: "version",
    ExifTags.GPS.GPSLatitudeRef: "NS",
    ExifTags.GPS.GPSLatitude: "rational3",
    ExifTags.GPS.GPSLongitudeRef: "EW",
    ExifTags.GPS.GPSLongitude: "rational3",
    ExifTags.GPS.GPSAltitudeRef: "byte01",
    ExifTags.GPS.GPSAltitude: "rational",
    ExifTags.GPS.GPSTimeStamp: "rational3",
    ExifTags.GPS.GPSSatellites: "text",
    ExifTags.GPS.GPSStatus: "AV",
    ExifTags.GPS.GPSMeasureMode: "23",
    ExifTags.GPS.GPSDOP: "rational",
    ExifTags.GPS.GPSSpeedRef: "KMN",
    ExifTags.GPS.GPSSpeed: "rational",
    ExifTags.GPS.GPSTrackRef: "TM",
    ExifTags.GPS.GPSTrack: "rational",
    ExifTags.GPS.GPSImgDirectionRef: "TM",
    ExifTags.GPS.GPSImgDirection: "rational",
    ExifTags.GPS.GPSMapDatum: "text",
    ExifTags.GPS.GPSDestLatitudeRef: "NS",
    ExifTags.GPS.GPSDestLatitude: "rational3",
    ExifTags.GPS.GPSDestLongitudeRef: "EW",
    ExifTags.GPS.GPSDestLongitude: "rational3",
    ExifTags.GPS.GPSDestBearingRef: "TM",
    ExifTags.GPS.GPSDestBearing: "rational",
    ExifTags.GPS.GPSDestDistanceRef: "KMN",
    ExifTags.GPS.GPSDestDistance: "rational",
    ExifTags.GPS.GPSDateStamp: "gpsdate",
    ExifTags.GPS.GPSDifferential: "short01",
    ExifTags.GPS.GPSHPositioningError: "rational",
}
# Thẻ "Ref" cho biết nghĩa của thẻ đi kèm: bán cầu, trên hay dưới mặt biển, đơn vị, hướng thật hay
# hướng từ. Thiếu thẻ Ref thì trình đọc ảnh hiểu theo mặc định (Bắc, Đông, trên mặt biển, km/h…).
_GPS_REF_TAGS = (
    ExifTags.GPS.GPSLatitudeRef,
    ExifTags.GPS.GPSLongitudeRef,
    ExifTags.GPS.GPSAltitudeRef,
    ExifTags.GPS.GPSSpeedRef,
    ExifTags.GPS.GPSTrackRef,
    ExifTags.GPS.GPSImgDirectionRef,
    ExifTags.GPS.GPSDestLatitudeRef,
    ExifTags.GPS.GPSDestLongitudeRef,
    ExifTags.GPS.GPSDestBearingRef,
    ExifTags.GPS.GPSDestDistanceRef,
)
_GPS_LOCATION_TAGS = (ExifTags.GPS.GPSLatitude, ExifTags.GPS.GPSLongitude)
_GPS_COORDINATE_TAGS = (
    ExifTags.GPS.GPSLatitudeRef,
    ExifTags.GPS.GPSLatitude,
    ExifTags.GPS.GPSLongitudeRef,
    ExifTags.GPS.GPSLongitude,
)


def _is_rational(value: object) -> bool:
    return (
        isinstance(value, IFDRational)
        and isinstance(value.numerator, int)
        and isinstance(value.denominator, int)
        and value.numerator >= 0
        and value.denominator > 0
    )


def _is_text(value: object) -> bool:
    # Chỉ chữ ASCII in được: EXIF ghi chữ dạng ASCII, ký tự khác bị Pillow đổi thành "?" khi ghi.
    return (
        isinstance(value, str)
        and 0 < len(value) <= _MAX_TEXT_CHARS
        and all(" " <= ch <= "~" for ch in value)
    )


def _valid(kind: str, value: object) -> bool:
    """Giá trị có đúng kiểu mong đợi không (EXIF hỏng hay dựng cố ý thì bỏ thẻ đó)."""
    if kind == "text":
        return _is_text(value)
    if kind == "datetime":
        return isinstance(value, str) and _DATE_TIME.fullmatch(value) is not None
    if kind == "offset":
        return isinstance(value, str) and _UTC_OFFSET.fullmatch(value) is not None
    if kind == "gpsdate":
        return isinstance(value, str) and _GPS_DATE.fullmatch(value) is not None
    if kind == "rational":
        return _is_rational(value)
    if kind == "rational3":
        return isinstance(value, tuple) and len(value) == 3 and all(map(_is_rational, value))
    if kind == "version":
        return isinstance(value, bytes) and len(value) == 4
    if kind == "byte01":
        return value in (b"\x00", b"\x01")
    if kind == "short01":
        return type(value) is int and value in (0, 1)
    # Các thẻ "Ref": một chữ trong tập cho phép (``NS``, ``EW``, ``TM``…).
    return isinstance(value, str) and len(value) == 1 and value in kind


def _read_exif(image: Image.Image) -> Image.Exif | None:
    """EXIF của ảnh gốc, hoặc None nếu đọc không được (EXIF hỏng)."""
    try:
        exif = image.getexif()
        exif.get_ifd(ExifTags.IFD.Exif)
        exif.get_ifd(ExifTags.IFD.GPSInfo)
    except _EXIF_ERRORS:
        return None
    return exif


def _orientation(exif: Image.Exif | None) -> int:
    value = None if exif is None else exif.get(ExifTags.Base.Orientation)
    return value if type(value) is int and value in _TRANSPOSE else 1


def _pick(source: dict, keep: dict[int, str]) -> dict[int, object]:
    return {tag: value for tag, value in source.items() if tag in keep and _valid(keep[tag], value)}


def _normalize(value: object) -> object:
    """Dạng so sánh được của một giá trị EXIF (phân số so theo giá trị, không theo cách viết)."""
    if isinstance(value, IFDRational):
        if value.denominator == 0:
            return ("rational", value.numerator, 0)
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, tuple):
        return tuple(_normalize(item) for item in value)
    return value


def _normalize_dict(values: dict) -> dict:
    return {tag: _normalize(value) for tag, value in values.items()}


@dataclass(frozen=True)
class GpsCoordinates:
    """Vị trí GPS dạng độ thập phân (âm là Nam/Tây). Chỉ để hiện cho người dùng xem."""

    latitude: float
    longitude: float


def _degrees(dms: tuple, ref: object, negative: str, limit: float) -> float | None:
    parts = zip(dms, (1, 60, 3600), strict=True)
    value = sum(float(Fraction(r.numerator, r.denominator)) / factor for r, factor in parts)
    if value > limit:
        return None
    return round(-value if ref == negative else value, 7)


def _coordinates(gps: dict[int, object]) -> GpsCoordinates | None:
    if not all(tag in gps for tag in _GPS_LOCATION_TAGS):
        return None
    latitude = _degrees(
        gps[ExifTags.GPS.GPSLatitude], gps.get(ExifTags.GPS.GPSLatitudeRef), "S", 90.0
    )
    longitude = _degrees(
        gps[ExifTags.GPS.GPSLongitude], gps.get(ExifTags.GPS.GPSLongitudeRef), "W", 180.0
    )
    if latitude is None or longitude is None:
        return None
    return GpsCoordinates(latitude=latitude, longitude=longitude)


@dataclass(frozen=True)
class _KeptExif:
    """Phần EXIF được giữ theo quyết định 2A (đã kiểm kiểu từng giá trị)."""

    base: dict[int, object]
    exif: dict[int, object]
    gps: dict[int, object]
    notice: str = ""

    @classmethod
    def from_source(cls, exif: Image.Exif | None) -> _KeptExif:
        if exif is None:
            return cls({}, {}, {}, notice=_NOTICE_EXIF_UNREADABLE)
        try:
            exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            kept = cls(
                base=_pick(dict(exif), _BASE_KEEP),
                exif=_pick(exif_ifd, _EXIF_IFD_KEEP),
                gps=_pick(gps_ifd, _GPS_KEEP),
            )
        except _EXIF_ERRORS:
            return cls({}, {}, {}, notice=_NOTICE_EXIF_UNREADABLE)
        if any(tag in gps_ifd and tag not in kept.gps for tag in _GPS_REF_TAGS):
            # LC-T049-1: ảnh gốc có thẻ Ref mà sai khuôn (``"s"``, ``"w"`` chữ thường;
            # GPSAltitudeRef sai kiểu…). Bỏ riêng thẻ đó thì giá trị đi kèm bị hiểu theo mặc định
            # (Nam thành Bắc, dưới mặt biển thành trên), mà đoán lại thì có thể sai: coi cả khối
            # GPS hỏng, không đăng tọa độ có thể sai, và báo người dùng.
            return cls(kept.base, kept.exif, {}, notice=_NOTICE_GPS_BROKEN)
        if _coordinates(kept.gps) is None:
            # Không có vĩ độ và kinh độ đúng kiểu, đúng phạm vi thì không có "vị trí" nào để giữ:
            # bỏ hết phần GPS còn lại (giờ GPS đứng một mình không có ích). Chỉ báo người dùng khi
            # ảnh gốc có ghi tọa độ (máy tắt định vị có thể chỉ ghi phiên bản GPS).
            had_location = any(tag in gps_ifd for tag in _GPS_COORDINATE_TAGS)
            kept = cls(kept.base, kept.exif, {}, notice=_NOTICE_GPS_BROKEN if had_location else "")
        return kept

    @property
    def is_empty(self) -> bool:
        return not (self.base or self.exif or self.gps)

    def expected(self) -> dict[str, dict]:
        """EXIF mà file ra phải có, đúng từng giá trị (để so sau khi nén)."""
        return {
            "base": _normalize_dict({ExifTags.Base.Orientation: 1, **self.base}),
            "exif": _normalize_dict(self.exif),
            "gps": _normalize_dict(self.gps),
            "ifd1": {},
        }

    def to_bytes(self) -> bytes:
        exif = Image.Exif()
        exif[ExifTags.Base.Orientation] = 1  # điểm ảnh đã được xoay đúng chiều
        for tag, value in self.base.items():
            exif[tag] = value
        if self.exif:
            exif.get_ifd(ExifTags.IFD.Exif).update(self.exif)
        if self.gps:
            exif.get_ifd(ExifTags.IFD.GPSInfo).update(self.gps)
        return exif.tobytes()


def _exif_snapshot(exif: Image.Exif) -> dict[str, dict]:
    """EXIF đọc lại từ file ra, cùng dạng với ``_KeptExif.expected``."""
    base = {tag: value for tag, value in exif.items() if tag not in _POINTER_TAGS}
    return {
        "base": _normalize_dict(base),
        "exif": _normalize_dict(exif.get_ifd(ExifTags.IFD.Exif)),
        "gps": _normalize_dict(exif.get_ifd(ExifTags.IFD.GPSInfo)),
        "ifd1": _normalize_dict(exif.get_ifd(ExifTags.IFD.IFD1)),
    }


# ----- điểm ảnh ------------------------------------------------------------------------------


def _to_8bit(image: Image.Image, *, keep_alpha: bool) -> Image.Image:
    """Đổi về RGB (hoặc RGBA nếu có trong suốt và được giữ), 8 bit mỗi kênh (SL-T058-1)."""
    if image.mode in ("I", "F") or image.mode.startswith("I;16"):
        # Ảnh xám 16 bit (PNG): chia 256 để về 0–255. ``convert("L")`` thẳng sẽ cắt mọi giá trị
        # trên 255 thành trắng.
        image = image.convert("I").point(lambda value: value * (1 / 256)).convert("L")
    if image.has_transparency_data:
        rgba = image.convert("RGBA")
        if keep_alpha:
            return rgba
        flat = Image.new("RGB", rgba.size, (255, 255, 255))
        flat.paste(rgba, mask=rgba.getchannel("A"))
        return flat
    return image if image.mode == "RGB" else image.convert("RGB")


def _rgb_icc_profile(image: Image.Image) -> bytes | None:
    """Hồ sơ màu RGB của ảnh gốc, nếu dùng được cho ảnh web (màu ảnh iPhone Display P3 không lệch).

    Bỏ khi: ảnh gốc không phải ảnh màu RGB (CMYK, xám: điểm ảnh đã đổi sang RGB, hồ sơ cũ sai),
    hồ sơ không đúng khuôn ở phần đầu, hoặc quá lớn.
    """
    icc = image.info.get("icc_profile")
    if image.mode not in ("RGB", "RGBA", "RGBX", "P", "PA") or not isinstance(icc, bytes):
        return None
    if not 132 <= len(icc) <= MAX_ICC_BYTES:
        return None
    if int.from_bytes(icc[:4], "big") != len(icc) or icc[36:40] != b"acsp":
        return None
    return icc if icc[16:20] == b"RGB " else None


@dataclass(frozen=True)
class _Prepared:
    image: Image.Image  # ảnh mới dựng từ điểm ảnh: không ``info``, không EXIF
    exif: _KeptExif
    icc_profile: bytes | None


def _prepare(data: object, max_edge: int, *, keep_alpha: bool) -> _Prepared:
    """Mở, đọc EXIF, đổi về 8 bit, xoay đúng chiều, thu cạnh dài về ``max_edge`` (không phóng to).

    Kết quả là ảnh **mới** dựng lại từ điểm ảnh (``Image.frombytes``): không còn ``info`` (chú
    thích, XMP, chunk chữ, EXIF…) mà Pillow có thể tự chép khi lưu.
    """
    image = _open(data, draft_edge=max_edge)
    try:
        exif = _read_exif(image)
        kept = _KeptExif.from_source(exif)
        icc = _rgb_icc_profile(image)
        try:
            pixels = _to_8bit(image, keep_alpha=keep_alpha)
            method = _TRANSPOSE.get(_orientation(exif))
            if method is not None:
                pixels = pixels.transpose(method)
            pixels.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
            clean = Image.frombytes(pixels.mode, pixels.size, pixels.tobytes())
        except (OSError, ValueError):
            raise ImageProcessError(_MSG_BROKEN) from None
    finally:
        image.close()
    return _Prepared(image=clean, exif=kept, icc_profile=icc)


def _check_edge(value: object, name: str) -> int:
    if type(value) is not int or not MIN_EDGE_PX <= value <= MAX_EDGE_PX:
        raise ImageProcessError(
            f"Cấu hình ảnh không hợp lệ: {name} phải là số nguyên từ {MIN_EDGE_PX} đến "
            f"{MAX_EDGE_PX}."
        )
    return value


def _check_quality(value: object) -> int:
    if type(value) is not int or not 1 <= value <= 100:
        raise ImageProcessError(
            "Cấu hình ảnh không hợp lệ: webp_quality phải là số nguyên từ 1 đến 100."
        )
    return value


# ----- kiểm file ra --------------------------------------------------------------------------

_WEBP_ALLOWED_CHUNKS = frozenset({b"VP8 ", b"VP8L", b"VP8X", b"ALPH", b"ICCP", b"EXIF"})
# Khối JPEG được phép trong ảnh do app tạo: bảng lượng tử, bảng mã, khung ảnh, khoảng khởi động
# lại. Ngoài ra chỉ có đúng một khối APP0 "JFIF" (không ảnh nhỏ) trước các khối này.
_JPEG_TABLE_MARKERS = frozenset({0xDB, 0xC4, 0xDD})
_JPEG_FRAME_MARKERS = frozenset({0xC0, 0xC1})  # baseline; app không ghi JPEG progressive


def webp_chunks(data: bytes) -> list[bytes]:
    """Tên các chunk của file WebP; file sai khuôn (dư byte, khai sai độ dài) thì báo lỗi."""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("không phải WebP")
    if int.from_bytes(data[4:8], "little") != len(data) - 8:
        raise ValueError("RIFF khai sai độ dài")
    chunks = []
    position = 12
    while position < len(data):
        if position + 8 > len(data):
            raise ValueError("chunk cụt")
        name = data[position : position + 4]
        size = int.from_bytes(data[position + 4 : position + 8], "little")
        position += 8 + size + (size & 1)
        if position > len(data):
            raise ValueError("chunk dài quá file")
        chunks.append(name)
    return chunks


def jpeg_layout(data: bytes) -> tuple[int, int]:
    """Kiểm file JPEG chỉ có các khối trong danh sách cho phép, trả (rộng, cao).

    Cho phép: SOI, đúng một APP0 ``JFIF`` 14 byte, DQT, DHT, DRI, đúng một SOF0/SOF1, đúng một
    SOS, dữ liệu ảnh (chỉ có byte đệm ``FF 00`` và mã RST), rồi EOI ở cuối file. Mọi thứ khác
    (APP1 EXIF/XMP, APP2 ICC, APP13, COM, dữ liệu sau EOI…) thì báo lỗi.
    """
    if data[:2] != b"\xff\xd8":
        raise ValueError("không phải JPEG")
    position = 2
    seen_app0 = False
    size = None
    while True:
        if position + 4 > len(data) or data[position] != 0xFF:
            raise ValueError("khối JPEG sai khuôn")
        marker = data[position + 1]
        length = int.from_bytes(data[position + 2 : position + 4], "big")
        body = data[position + 4 : position + 2 + length]
        if length < 2 or len(body) != length - 2:
            raise ValueError("khối JPEG khai sai độ dài")
        position += 2 + length
        if marker == 0xE0 and not seen_app0 and size is None:
            if len(body) != 14 or body[:5] != b"JFIF\x00" or body[12:14] != b"\x00\x00":
                raise ValueError("APP0 sai khuôn")
            seen_app0 = True
        elif marker in _JPEG_TABLE_MARKERS:
            pass
        elif marker in _JPEG_FRAME_MARKERS and size is None:
            if len(body) < 6:
                raise ValueError("SOF sai khuôn")
            size = (int.from_bytes(body[3:5], "big"), int.from_bytes(body[1:3], "big"))
        elif marker == 0xDA and size is not None:
            break
        else:
            raise ValueError(f"khối JPEG không được phép: {marker:#04x}")
    # Dữ liệu ảnh sau SOS: chỉ cho byte đệm FF 00 và mã RST FF D0–D7; EOI đúng ở cuối file.
    end = len(data) - 2
    if data[end:] != b"\xff\xd9":
        raise ValueError("thiếu EOI ở cuối file")
    found = data.find(b"\xff", position)
    while found != -1 and found < end:
        if data[found + 1] != 0x00 and not 0xD0 <= data[found + 1] <= 0xD7:
            raise ValueError("dữ liệu ảnh có khối lạ")
        found = data.find(b"\xff", found + 2)
    return size


def _encode_clean_jpeg(image: Image.Image, quality: int) -> bytes:
    buffer = io.BytesIO()
    try:
        # Chỉ truyền đúng chất lượng: không exif, icc_profile, comment, xmp, dpi.
        image.save(buffer, "JPEG", quality=quality)
    except (OSError, ValueError):
        raise ImageProcessError(_MSG_ENCODE) from None
    data = buffer.getvalue()
    try:
        jpeg_layout(data)
    except ValueError:
        raise ImageProcessError(_MSG_ENCODE) from None
    return data


# ----- ảnh đăng web --------------------------------------------------------------------------


@dataclass(frozen=True)
class WebImage:
    """Ảnh WebP để tải lên WordPress (file đầy đủ, quyết định 5A)."""

    data: bytes = field(repr=False)
    width: int
    height: int
    gps: GpsCoordinates | None  # vị trí còn trong file (đã kiểm sau khi nén); None: không có
    notice: str = ""  # câu báo cho người dùng khi GPS của ảnh gốc hỏng, không đọc được
    mime: str = "image/webp"

    @property
    def has_gps(self) -> bool:
        return self.gps is not None


def _verify_web_image(data: bytes, kept: _KeptExif, size: tuple[int, int]) -> None:
    """Mở lại file WebP vừa nén: đúng khuôn, đúng cỡ, EXIF đúng từng giá trị đã giữ (F2)."""
    try:
        chunks = webp_chunks(data)
    except ValueError:
        raise ImageProcessError(_MSG_ENCODE) from None
    if not set(chunks) <= _WEBP_ALLOWED_CHUNKS:
        raise ImageProcessError(_MSG_ENCODE)
    image = _open(data, formats=("WEBP",))
    try:
        if image.size != size:
            raise ImageProcessError(_MSG_ENCODE)
        exif = _read_exif(image)
        actual = (
            {"base": {}, "exif": {}, "gps": {}, "ifd1": {}}
            if exif is None or b"EXIF" not in chunks
            else _exif_snapshot(exif)
        )
    finally:
        image.close()
    expected = (
        {"base": {}, "exif": {}, "gps": {}, "ifd1": {}} if kept.is_empty else kept.expected()
    )
    if actual["gps"] != expected["gps"]:
        raise ImageProcessError(_MSG_GPS_LOST)
    if actual != expected:
        raise ImageProcessError(_MSG_ENCODE)


def make_web_image(
    data: bytes,
    *,
    max_edge_px: int = WEB_MAX_EDGE_PX,
    webp_quality: int = WEB_WEBP_QUALITY,
) -> WebImage:
    """Ảnh đăng web: xoay đúng chiều, cạnh dài ≤ ``max_edge_px``, WebP, EXIF đã lọc giữ GPS.

    ``data``: byte ảnh gốc (từ ``ImageLibrary.read_image_bytes``) hoặc ảnh AI trả về. Ảnh không
    có EXIF (ảnh chụp màn hình) thì file ra không có EXIF. Ảnh gốc có vị trí GPS mà file ra
    không còn đúng từng giá trị thì báo ``ImageProcessError`` (không bao giờ trả ảnh mất GPS).
    """
    max_edge_px = _check_edge(max_edge_px, "max_edge_px")
    webp_quality = _check_quality(webp_quality)
    prepared = _prepare(data, max_edge_px, keep_alpha=True)
    params: dict[str, object] = {"quality": webp_quality, "method": WEB_WEBP_METHOD}
    if not prepared.exif.is_empty:
        try:
            params["exif"] = prepared.exif.to_bytes()
        except _EXIF_ERRORS:
            raise ImageProcessError(_MSG_GPS_LOST if prepared.exif.gps else _MSG_ENCODE) from None
    if prepared.icc_profile is not None:
        params["icc_profile"] = prepared.icc_profile
    buffer = io.BytesIO()
    try:
        prepared.image.save(buffer, "WEBP", **params)
    except (OSError, ValueError):
        raise ImageProcessError(_MSG_ENCODE) from None
    output = buffer.getvalue()
    _verify_web_image(output, prepared.exif, prepared.image.size)
    return WebImage(
        data=output,
        width=prepared.image.width,
        height=prepared.image.height,
        gps=_coordinates(prepared.exif.gps),
        notice=prepared.exif.notice,
    )


# ----- bản gửi AI ----------------------------------------------------------------------------


@dataclass(frozen=True)
class AiImage:
    """Ảnh gửi AI viết alt: JPEG không metadata (A3). Dùng làm ``data``/``mime`` cho lớp AI."""

    data: bytes = field(repr=False)
    width: int
    height: int
    mime: str = "image/jpeg"


def make_ai_image(data: bytes, *, max_edge_px: int = AI_MAX_EDGE_PX) -> AiImage:
    """Bản gửi AI: xoay đúng chiều, cạnh dài ≤ ``max_edge_px``, JPEG dựng lại từ điểm ảnh.

    Không EXIF/GPS, XMP, chú thích, chunk chữ, hồ sơ màu (ảnh trong suốt được lót nền trắng).
    Không đổi màu bằng ImageCms (khuyến nghị Lá Chắn T-050: không đọc hồ sơ màu của file lạ).
    """
    max_edge_px = _check_edge(max_edge_px, "max_edge_px")
    prepared = _prepare(data, max_edge_px, keep_alpha=False)
    output = _encode_clean_jpeg(prepared.image, AI_JPEG_QUALITY)
    return AiImage(data=output, width=prepared.image.width, height=prepared.image.height)


# ----- ảnh xem trước -------------------------------------------------------------------------


def make_preview(data: bytes, *, max_edge_px: int = PREVIEW_MAX_EDGE_PX) -> bytes:
    """Ảnh xem trước trong máy: JPEG 8 bit, không metadata, xoay đúng chiều.

    Byte trả về là thứ được đưa vào ``st.image`` (LC-T058-2): do app tạo, không phải byte gốc.
    """
    max_edge_px = _check_edge(max_edge_px, "max_edge_px")
    prepared = _prepare(data, max_edge_px, keep_alpha=False)
    return _encode_clean_jpeg(prepared.image, PREVIEW_JPEG_QUALITY)


def _gitignore_lines() -> list[str]:
    try:
        text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return [line.strip() for line in text.splitlines()]


def _cache_dir_is_ignored(directory: Path) -> bool:
    """Thư mục cache không bị commit nhầm (góp ý Lá Chắn T-046 số 9, kiểm bằng code).

    Ngoài thư mục dự án thì git không thấy. Trong thư mục dự án thì phải nằm trong ``data/`` và
    ``.gitignore`` phải có dòng ``data/`` (không có dòng ``!`` nào gỡ lại).
    """
    try:
        target = directory.resolve()
        root = PROJECT_ROOT.resolve()
    except (OSError, RuntimeError):
        return False
    if not target.is_relative_to(root):
        return True
    if not target.is_relative_to(root / "data"):
        return False
    lines = _gitignore_lines()
    ignored = any(line in ("data/", "/data/", "data", "/data") for line in lines)
    unignored = any(line.startswith("!") and "data" in line for line in lines)
    return ignored and not unignored


class PreviewCache:
    """Cache ảnh xem trước trên ổ của máy đang dùng (xóa đi vẫn tạo lại được).

    Tên file là mã băm (không chứa tên ảnh hay tên thư mục). Khóa gồm ``ImageRef`` (lấy từ kết
    quả quét, ghi chú Lá Chắn T-048), dung lượng và thời điểm sửa file: ảnh đổi thì tạo lại.
    File đọc từ cache được kiểm lại khuôn JPEG sạch trước khi trả; sai thì tạo lại.
    """

    def __init__(
        self,
        directory: Path | str = PREVIEW_CACHE_DIR,
        *,
        max_edge_px: int = PREVIEW_MAX_EDGE_PX,
    ) -> None:
        self._dir = Path(directory)
        self._max_edge = _check_edge(max_edge_px, "max_edge_px")
        # Thư mục có thể bị commit nhầm thì không ghi cache (vẫn trả ảnh xem trước bình thường).
        self.enabled = _cache_dir_is_ignored(self._dir)

    def __repr__(self) -> str:
        return f"PreviewCache(enabled={self.enabled})"  # không in đường dẫn

    def _key(self, ref: ImageRef, size: int, modified: float) -> str:
        text = "|".join(
            (
                str(_PREVIEW_CACHE_VERSION),
                str(self._max_edge),
                str(ref.root_index),
                ref.rel_path,
                str(size),
                repr(modified),
            )
        )
        return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()

    def _read(self, path: Path) -> bytes | None:
        try:
            if path.stat().st_size > _MAX_CACHED_PREVIEW_BYTES:
                return None
            data = path.read_bytes()
            width, height = jpeg_layout(data)
        except (OSError, ValueError, IndexError):
            return None
        if max(width, height) > self._max_edge:
            return None
        return data

    def _write(self, path: Path, data: bytes) -> None:
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(dir=self._dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
                os.replace(temp, path)
            except BaseException:
                Path(temp).unlink(missing_ok=True)
                raise
        except OSError:
            pass  # cache chỉ để nhanh hơn: ghi không được thì thôi

    def get(self, library: ImageLibrary, ref: ImageRef) -> bytes:
        """Ảnh xem trước (JPEG do app tạo) của một ảnh trong thư mục ảnh.

        Lỗi: ``ImageFolderError`` (ảnh không đọc được từ thư mục) hoặc ``ImageProcessError``
        (nội dung không phải ảnh dùng được); cả hai đều là câu tiếng Việt hiện thẳng được.
        """
        # LC-T049-2: kiểm trước cả khi trả ảnh có sẵn trong cache (byte trả về vào ``st.image``,
        # được Pillow của máy giải mã).
        _require_pillow_13()
        entry = library.stat_image(ref)
        path = self._dir / f"{self._key(ref, entry.size, entry.modified)}.jpg"
        if self.enabled:
            cached = self._read(path)
            if cached is not None:
                return cached
        preview = make_preview(library.read_image_bytes(ref), max_edge_px=self._max_edge)
        if self.enabled:
            self._write(path, preview)
        return preview

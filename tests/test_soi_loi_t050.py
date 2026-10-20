"""Soi Lỗi T-050: tìm đường cho metadata, tên file, đường dẫn lọt tới AI; app gọi sang máy chủ
khác; chữ AI trả về thành link/HTML.

Ảnh đều tạo ngay trong test (bytes viết tay hoặc Pillow), không có ảnh thật. Không gọi mạng
thật: 3 thư viện chạy với ``MockTransport`` qua fixture ``network`` của ``test_ai_images``.

Lỗi tìm thấy được đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T050-n`` (xem
``docs/team/reports/T-050-soi-loi.md``): sửa xong thì test tự báo XPASS để gỡ dấu.
"""

import base64
import io
import json
import struct
import unicodedata

import pytest
from PIL import Image, ImageCms

from seo_app.ai import AIError
from seo_app.ai import anthropic_provider as anthropic_module
from seo_app.ai.base import (
    IMAGE_BROKEN_MESSAGE,
    IMAGE_METADATA_MESSAGE,
    IMAGE_MIME_MESSAGE,
    MAX_IMAGE_BYTES,
    MAX_IMAGES,
    MAX_TOTAL_IMAGE_BYTES,
    ImageInput,
    prepare_images,
)
from seo_app.images.alt import (
    ALT_MAX_LENGTH,
    CAPTION_MAX_LENGTH,
    AltSuggestion,
    alt_prompt,
    clean_alt_text,
    reference_lines,
    suggest_alt,
)
from tests.fake_ai import FakeProvider
from tests.test_ai_images import (
    ANTHROPIC_KEY,
    IDAT,
    IEND,
    IHDR,
    JFIF,
    JPEG,
    KEYS,
    PNG,
    SCAN,
    SERVER_TEXT,
    SOS,
    VENDORS,
    WEBP,
    Answer,
    Returns,
    Router,
    assert_official,
    jpeg_segment,
    make,
    make_jpeg,
    make_png,
    make_webp,
    network,  # noqa: F401  (fixture mạng giả dùng chung)
    ok_response,
    png_chunk,
    task,
    webp_chunk,
)

# Thông tin riêng giấu trong ảnh: không bao giờ được tới AI.
SECRET = b"GPS 16.0544N 108.2022E; D:/Anh/Nha anh Tuan 12 Le Loi/IMG_0001.jpg"
# EXIF thô dạng TIFF (không có đầu "Exif\0\0"): cách PNG eXIf, WebP EXIF hay ghi.
RAW_TIFF = b"MM\x00*\x00\x00\x00\x08" + SECRET


def accepted(data, mime):
    """``prepare_images`` nhận ảnh (True) hay từ chối (False)."""
    try:
        prepare_images([ImageInput(data=data, mime=mime)])
    except AIError:
        return False
    return True


def pillow(fmt, size=(16, 12), **save_args):
    out = io.BytesIO()
    Image.new("RGB", size, (180, 40, 40)).save(out, fmt, **save_args)
    return out.getvalue()


def srgb_icc():
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def jpeg_of_size(size):
    """JPEG hợp lệ về cấu trúc, dài đúng ``size`` byte (đệm bằng dữ liệu nén, không thêm khối)."""
    base = len(make_jpeg(scan=b""))
    return make_jpeg(scan=b"\x12" * (size - base))


# ================================================================== 1. metadata giấu chỗ lạ


@pytest.mark.parametrize(
    "data",
    [
        # Khối APP1 (EXIF) nằm giữa hai lượt quét của ảnh progressive.
        b"\xff\xd8" + JFIF + SOS + SCAN
        + jpeg_segment(0xE1, b"Exif\x00\x00" + RAW_TIFF) + SOS + SCAN + b"\xff\xd9",
        # XMP giữa các lượt quét.
        b"\xff\xd8" + JFIF + SOS + SCAN
        + jpeg_segment(0xE1, b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta/>")
        + SOS + SCAN + b"\xff\xd9",
        # COM (chú thích) giữa các lượt quét.
        b"\xff\xd8" + JFIF + SOS + SCAN + jpeg_segment(0xFE, SECRET) + SOS + SCAN + b"\xff\xd9",
        # IPTC (APP13) đặt sau bảng mã, trước khung ảnh.
        make_jpeg(jpeg_segment(0xED, b"Photoshop 3.0\x00" + SECRET)),
        # Chuỗi "Exif\0\0" giấu trong dữ liệu nén (không phải khối riêng).
        make_jpeg(scan=b"\x12Exif\x00\x00" + RAW_TIFF + b"\x34"),
        # Gói XMP giấu trong khối APP15.
        make_jpeg(jpeg_segment(0xEF, b"<x:xmpmeta xmlns:x='adobe:ns:meta/'>" + SECRET)),
    ],
    ids=["app1-giua-luot-quet", "xmp-giua-luot-quet", "com-giua-luot-quet", "app13",
         "exif-trong-du-lieu-nen", "xmp-trong-app15"],  # fmt: skip
)
def test_jpeg_metadata_in_odd_places_is_rejected(data):
    with pytest.raises(AIError) as info:
        prepare_images([ImageInput(data=data, mime="image/jpeg")])
    assert str(info.value) == IMAGE_METADATA_MESSAGE


@pytest.mark.parametrize(
    "tail",
    [b"\x00", b"\xff", b"\xff\xd9", SECRET, b"\xff\xd8" + JFIF + SOS + SCAN + b"\xff\xd9"],
    ids=["1-byte", "ff", "eoi-lap", "chu", "anh-thu-hai"],
)
def test_jpeg_anything_after_eoi_is_rejected(tail):
    with pytest.raises(AIError) as info:
        prepare_images([ImageInput(data=make_jpeg(tail=tail), mime="image/jpeg")])
    assert str(info.value) == IMAGE_BROKEN_MESSAGE


def test_pillow_mpo_second_frame_is_rejected():
    out = io.BytesIO()
    first = Image.new("RGB", (8, 8), "red")
    first.save(out, "MPO", save_all=True, append_images=[Image.new("RGB", (8, 8), "blue")])
    assert not accepted(out.getvalue(), "image/jpeg")


@pytest.mark.parametrize(
    "data",
    [
        # Khai chiều dài chunk lớn hơn file.
        b"\x89PNG\r\n\x1a\n" + IHDR + struct.pack(">I", 999) + b"tEXt" + SECRET,
        # tEXt nằm sau IDAT, trước IEND.
        b"\x89PNG\r\n\x1a\n" + IHDR + IDAT + png_chunk(b"tEXt", b"Comment\x00" + SECRET) + IEND,
        # Chuỗi XMP giấu trong chunk riêng.
        make_png(png_chunk(b"prVt", b"<x:xmpmeta>" + SECRET)),
        # Dữ liệu nối sau IEND.
        make_png() + SECRET,
    ],
    ids=["khai-dai-qua", "text-sau-idat", "xmp-trong-chunk-rieng", "sau-iend"],
)
def test_png_hidden_metadata_or_wrong_size_is_rejected(data):
    assert not accepted(data, "image/png")


def _riff(body):
    return b"RIFF" + struct.pack("<I", len(body)) + body


@pytest.mark.parametrize(
    "data",
    [
        make_webp(webp_chunk(b"EXIF", RAW_TIFF)),
        make_webp(webp_chunk(b"XMP ", b"<x:xmpmeta>" + SECRET)),
        # Khai kích thước RIFF lớn hơn file.
        WEBP[:4] + struct.pack("<I", len(WEBP)) + WEBP[8:],
        # Khai kích thước RIFF nhỏ hơn file: phần thừa là chỗ giấu dữ liệu.
        WEBP + SECRET,
        # Chunk khai dài quá phần còn lại.
        _riff(b"WEBP" + webp_chunk(b"VP8L", b"\x2f\x00\x00\x00\x00") + b"META"
              + struct.pack("<I", 9999) + SECRET),
    ],
    ids=["exif", "xmp", "riff-lon", "riff-nho", "chunk-khai-dai"],
)
def test_webp_metadata_or_wrong_size_is_rejected(data):
    assert not accepted(data, "image/webp")


# Ảnh sạch thật do Pillow tạo (kể cả có hồ sơ màu ICC) vẫn phải qua: lớp kiểm không được chặn
# nhầm bản gửi AI hợp lệ của T-049.
@pytest.mark.parametrize(
    ("fmt", "mime", "args"),
    [
        ("JPEG", "image/jpeg", {"icc_profile": True}),
        ("JPEG", "image/jpeg", {"progressive": True, "quality": 85, "icc_profile": True}),
        ("JPEG", "image/jpeg", {"quality": 95, "subsampling": 0, "optimize": True}),
        ("PNG", "image/png", {"icc_profile": True}),
        ("WEBP", "image/webp", {"icc_profile": True}),
        ("WEBP", "image/webp", {"lossless": True}),
    ],
)
def test_clean_pillow_images_with_icc_pass(fmt, mime, args):
    if args.get("icc_profile") is True:
        args = {**args, "icc_profile": srgb_icc()}
    data = pillow(fmt, size=(64, 48), **args)
    (prepared,) = prepare_images([ImageInput(data=data, mime=mime)])
    assert prepared.data == data and prepared.mime == mime


# --- SL-T050-2: khối/chunk không nằm trong danh sách chặn vẫn qua, dù chứa GPS, đường dẫn.
# Cách kiểm hiện tại là "danh sách chặn" (APP1, APP13, COM; eXIf/tEXt/zTXt/iTXt; EXIF/XMP).
# Bản gửi AI của T-049 không có lý do mang các khối dưới đây; ExifTool đọc nhiều khối trong số
# này (Kodak "Meta" ở APP3, Ricoh "RMETA" ở APP5, GoPro ở APP6, "PictureInfo"/"Ducky" ở APP12).

SL2 = pytest.mark.xfail(
    strict=True,
    reason="SL-T050-2: chỉ chặn theo danh sách đen, khối/chunk lạ chứa GPS, đường dẫn vẫn qua",
)


@SL2
@pytest.mark.parametrize("app", [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15])
def test_jpeg_other_app_segments_with_private_data_are_rejected(app):
    data = make_jpeg(jpeg_segment(0xE0 + app, b"Meta\x00\x00" + RAW_TIFF))
    assert not accepted(data, "image/jpeg")


@SL2
@pytest.mark.parametrize("kind", [b"zxIf", b"exIf", b"prVt", b"gpSl"])
def test_png_unknown_chunks_with_raw_exif_are_rejected(kind):
    assert not accepted(make_png(png_chunk(kind, RAW_TIFF)), "image/png")


@SL2
@pytest.mark.parametrize("kind", [b"exif", b"xmp ", b"XMP\x00", b"META"])
def test_webp_unknown_chunks_with_private_data_are_rejected(kind):
    assert not accepted(make_webp(webp_chunk(kind, RAW_TIFF)), "image/webp")


def test_split_exif_marker_across_segments_is_not_seen_as_exif():
    """Ghi nhận: "Exif\\0\\0" bị tách đôi qua hai khối APP15 không bị dò chuỗi bắt (cũng không
    trình đọc EXIF nào ghép lại). Chặn được hay không phụ thuộc SL-T050-2 (chặn APP15)."""
    data = make_jpeg(jpeg_segment(0xEF, b"..Exi"), jpeg_segment(0xEF, b"f\x00\x00" + RAW_TIFF))
    assert b"Exif\x00\x00" not in data


# ================================================================== 2. giới hạn số ảnh, dung lượng


def test_image_of_exactly_max_bytes_passes_and_one_more_byte_fails():
    exact = jpeg_of_size(MAX_IMAGE_BYTES)
    assert len(exact) == MAX_IMAGE_BYTES
    assert accepted(exact, "image/jpeg")
    with pytest.raises(AIError) as info:
        prepare_images([ImageInput(data=jpeg_of_size(MAX_IMAGE_BYTES + 1), mime="image/jpeg")])
    assert "quá lớn" in str(info.value) and "5,0 MB" in str(info.value)


def test_total_of_exactly_max_passes_and_one_more_byte_fails():
    assert MAX_TOTAL_IMAGE_BYTES == 2 * MAX_IMAGE_BYTES
    half = jpeg_of_size(MAX_IMAGE_BYTES)
    assert len(prepare_images([ImageInput(data=half, mime="image/jpeg")] * 2)) == 2
    quarter = jpeg_of_size(MAX_TOTAL_IMAGE_BYTES // 4)
    assert len(prepare_images([ImageInput(data=quarter, mime="image/jpeg")] * 4)) == 4
    with pytest.raises(AIError) as info:
        prepare_images(
            [
                ImageInput(data=half, mime="image/jpeg"),
                ImageInput(data=jpeg_of_size(MAX_IMAGE_BYTES - 1), mime="image/jpeg"),
                ImageInput(data=jpeg_of_size(200), mime="image/jpeg"),
            ]
        )
    assert "Tổng dung lượng" in str(info.value)


def test_four_images_pass_five_fail_even_if_fifth_is_tiny():
    image = ImageInput(data=JPEG, mime="image/jpeg")
    assert len(prepare_images([image] * MAX_IMAGES)) == MAX_IMAGES == 4
    with pytest.raises(AIError) as info:
        prepare_images([image] * 5)
    assert "tối đa 4 ảnh" in str(info.value)


def test_too_many_images_checked_before_reading_any_of_them():
    class Exploding:
        """Không phải ImageInput; nếu bị đọc trước khi đếm thì sẽ ra câu khác."""

    with pytest.raises(AIError) as info:
        prepare_images([Exploding()] * 5)
    assert "tối đa 4 ảnh" in str(info.value)


def test_generator_or_set_of_images_is_rejected_not_consumed():
    image = ImageInput(data=JPEG, mime="image/jpeg")
    for images in (iter([image]), {image}, (x for x in [image])):
        with pytest.raises(AIError):
            prepare_images(images)


@pytest.mark.parametrize("vendor", VENDORS)
def test_max_size_image_goes_inline_to_official_host(network, vendor):  # noqa: F811
    exact = jpeg_of_size(MAX_IMAGE_BYTES)
    network.reply = lambda request: ok_response(vendor, '{"text": "ok"}')
    make(vendor).generate(
        task(vendor), system="s", prompt="p", schema=Answer,
        images=[ImageInput(data=exact, mime="image/jpeg")],
    )  # fmt: skip
    (request,) = network.seen
    assert_official(vendor, request)
    path = request.url.path.lower()
    assert "upload" not in path and "/files" not in path
    assert base64.b64encode(exact[:3000])[:3000] in request.content.replace(b"_", b"/").replace(
        b"-", b"+"
    )


def test_bytearray_changed_after_check_does_not_change_what_is_sent(network, monkeypatch):  # noqa: F811
    """Ảnh là ``bytearray``; ngay sau khi ``prepare_images`` kiểm xong, có code khác sửa nó
    (chèn EXIF). Yêu cầu gửi đi vẫn phải là bản đã kiểm."""
    buffer = bytearray(JPEG)
    real_prepare = anthropic_module.prepare_images

    def prepare_then_tamper(images):
        prepared = real_prepare(images)
        buffer[2:2] = jpeg_segment(0xE1, b"Exif\x00\x00" + RAW_TIFF)
        return prepared

    monkeypatch.setattr(anthropic_module, "prepare_images", prepare_then_tamper)
    network.reply = lambda request: ok_response("anthropic", '{"text": "ok"}')
    make("anthropic").generate(
        task("anthropic"), system="s", prompt="p", schema=Answer,
        images=[ImageInput(data=buffer, mime="image/jpeg")],
    )  # fmt: skip
    body = json.loads(network.seen[0].content)
    sent = base64.b64decode(body["messages"][0]["content"][0]["source"]["data"])
    assert sent == JPEG and bytes(buffer) != JPEG


def test_suggest_alt_sends_immutable_copy_of_bytearray():
    buffer = bytearray(JPEG)
    fake = FakeProvider()
    suggest_alt(Router(fake), ImageInput(data=buffer, mime="image/jpeg"))
    buffer[:] = b"x"
    ((_, (image,)),) = fake.image_calls
    assert type(image.data) is bytes and image.data == JPEG


@pytest.mark.parametrize(
    "mime",
    ["image/jpeg; name=IMG_0001.jpg", "image/jpeg\nX-Evil: 1", "image/svg+xml", "text/html",
     "image/heic", "image/gif", ""],  # fmt: skip
)
def test_mime_with_file_name_or_header_is_rejected_without_echo(mime):
    with pytest.raises(AIError) as info:
        prepare_images([ImageInput(data=JPEG, mime=mime)])
    assert str(info.value) == IMAGE_MIME_MESSAGE
    assert "IMG_0001" not in str(info.value) and "Evil" not in str(info.value)


def test_alias_mime_is_sent_as_canonical_name(network):  # noqa: F811
    network.reply = lambda request: ok_response("openai", '{"text": "ok"}')
    make("openai").generate(
        task("openai"), system="s", prompt="p", schema=Answer,
        images=[ImageInput(data=JPEG, mime=" IMAGE/JPG ")],
    )  # fmt: skip
    body = json.loads(network.seen[0].content)
    assert body["input"][0]["content"][0]["image_url"].startswith("data:image/jpeg;base64,")


def test_png_declared_as_webp_and_webp_as_png_are_rejected():
    assert not accepted(PNG, "image/webp")
    assert not accepted(WEBP, "image/png")
    assert not accepted(JPEG, "image/png")


def _unused():  # giữ tên đã nhập cho các phần sau (ruff F401)
    return (ALT_MAX_LENGTH, CAPTION_MAX_LENGTH, AltSuggestion, alt_prompt, clean_alt_text,
            reference_lines, Returns, KEYS, ANTHROPIC_KEY, SERVER_TEXT, unicodedata)  # fmt: skip

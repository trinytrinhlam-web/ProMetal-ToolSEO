"""Soi Lỗi T-066 (rút gọn): lớp kiểm ảnh gửi AI sau khi siết (``prepare_images`` trong
``seo_app/ai/base.py``): hồ sơ màu luôn bị từ chối, khối được nhận đúng khuôn, không lặp.

1. Bản gửi AI thật (``make_ai_image``, ``make_preview`` của T-049) từ các nguồn chưa có trong test
   của Thợ Máy và T-049: MPO nhiều khung, PNG động, WebP động, PNG RGB 16 bit có ``iCCP``, đủ 8
   hướng xoay EXIF, ảnh 1×1. Phải qua, và không còn hồ sơ màu, EXIF, XMP hay chữ của ảnh gốc.
2. Hồ sơ màu nhét vào khối/chunk khác loại hay sai chỗ (chú thích, APP15, APP2 tên viết thường,
   APP2 giữa hai lượt quét, sau EOI; chunk riêng, ``ICCP`` viết hoa trong PNG, ``iCCP`` sau IDAT,
   ``cICP``, sau IEND; ``iccp`` viết thường, ``ICCP`` sau chunk ảnh trong WebP): bị từ chối.
3. Trọng tài Pillow: ảnh Pillow bị đột biến (chèn khối metadata ở chỗ bất kỳ, lặp, xóa, đổi chỗ
   khối, sửa trường độ dài, lật byte, cắt cụt). Ảnh nào ``prepare_images`` nhận thì Pillow cũng
   không đọc ra hồ sơ màu, EXIF, XMP hay chữ; không có ngoại lệ nào khác ``AIError``.

Ảnh đều tạo ngay trong test (hạt giống cố định); không gọi AI hay mạng.
"""

import contextlib
import io
import random
import struct
import zlib

import pytest
from PIL import Image

from seo_app.ai.base import (
    IMAGE_BROKEN_MESSAGE,
    IMAGE_METADATA_MESSAGE,
    AIError,
    ImageInput,
    prepare_images,
)
from seo_app.images import process
from tests.test_ai_images import (  # noqa: F401  (pillow_state_restored: fixture dùng chung)
    ICC_SECRET,
    IDAT,
    IEND,
    IHDR,
    JFIF,
    SCAN,
    SECRET_TEXT,
    SOS,
    XMP_PACKET,
    icc_with_text,
    jpeg_segment,
    make_jpeg,
    make_png,
    make_webp,
    pillow_state_restored,
    png_chunk,
    webp_chunk,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PROFILE = icc_with_text()  # hồ sơ màu RGB đúng khuôn hoàn toàn, chở chữ trong thẻ ``desc``
ARTIST = "Nha anh Tuan 12 Le Loi"


def noisy(mode, size, seed=66):
    """Ảnh có nhiễu (hạt giống cố định) và dải màu: dữ liệu nén có đủ loại byte, cả 0xFF."""
    width, height = size
    noise = Image.frombytes("L", size, random.Random(seed).randbytes(width * height))
    gradients = [Image.linear_gradient("L").resize(size), Image.radial_gradient("L").resize(size)]
    image = Image.merge("RGB", [noise, *gradients])
    if mode == "RGBA":  # độ trong suốt thật (không phải alpha 255 khắp nơi)
        image = image.convert("RGBA")
        image.putalpha(Image.linear_gradient("L").resize(size))
        return image
    return image.convert(mode)


def save(image, fmt, **args):
    buffer = io.BytesIO()
    image.save(buffer, fmt, **args)
    return buffer.getvalue()


def exif_with(orientation):
    exif = Image.Exif()
    exif[0x010F] = "Apple"  # Make
    exif[0x0110] = "iPhone 15 Pro"  # Model
    exif[0x0112] = orientation
    exif[0x013B] = ARTIST  # Artist
    exif.get_ifd(0x8825).update({1: "N", 2: (16.0, 3.0, 15.84), 3: "E", 4: (108.0, 12.0, 7.92)})
    return exif.tobytes()


# ================================================================== 1. bản gửi AI thật


def png_rgb_16_bit(size=(96, 64)):
    """PNG RGB 16 bit (Pillow không tự ghi được), kèm ``iCCP`` chở chữ và ``tEXt``."""
    width, height = size
    rows = b"".join(
        b"\x00" + bytes((x * 7 + y * 3) % 256 for x in range(width * 6)) for y in range(height)
    )
    header = struct.pack(">IIBBBBB", width, height, 16, 2, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + png_chunk(b"IHDR", header)
        + png_chunk(b"iCCP", b"ICC Profile\x00\x00" + zlib.compress(PROFILE))
        + png_chunk(b"tEXt", b"Comment\x00" + SECRET_TEXT)
        + png_chunk(b"IDAT", zlib.compress(rows))
        + png_chunk(b"IEND", b"")
    )


def ai_source(kind):
    image = noisy("RGB", (240, 160))
    frames = [image.rotate(90), image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]
    if kind == "mpo-3-khung":
        return save(image, "MPO", save_all=True, append_images=frames, exif=exif_with(6),
                    icc_profile=PROFILE)  # fmt: skip
    if kind == "png-dong-3-khung":
        return save(image, "PNG", save_all=True, append_images=frames, icc_profile=PROFILE)
    if kind == "webp-dong-3-khung":
        return save(image, "WEBP", save_all=True, append_images=frames, icc_profile=PROFILE,
                    exif=exif_with(3), xmp=XMP_PACKET)  # fmt: skip
    if kind == "png-rgb-16-bit":
        return png_rgb_16_bit()
    assert kind == "jpeg-1x1"
    return save(Image.new("RGB", (1, 1), (200, 10, 10)), "JPEG", exif=exif_with(6),
                icc_profile=PROFILE, comment=SECRET_TEXT, xmp=XMP_PACKET)  # fmt: skip


def assert_clean_ai_copies(data):
    """``make_ai_image`` và ``make_preview`` qua ``prepare_images``, không còn dấu ảnh gốc."""
    ai = process.make_ai_image(data)
    (prepared,) = prepare_images([ImageInput(data=ai.data, mime=ai.mime)])
    assert prepared.data == ai.data and prepared.mime == "image/jpeg"
    preview = process.make_preview(data)
    assert prepare_images([ImageInput(data=preview, mime="image/jpeg")])[0].data == preview
    for copy in (ai.data, preview):  # chuỗi dài: dữ liệu nén không tình cờ chứa được
        for marker in (b"ICC_PROFILE", b"Exif\x00\x00", b"<x:xmpmeta", ICC_SECRET, SECRET_TEXT,
                       ARTIST.encode(), b"iPhone 15 Pro"):  # fmt: skip
            assert marker not in copy, marker
    return ai


@pytest.mark.parametrize(
    "kind",
    ["mpo-3-khung", "png-dong-3-khung", "webp-dong-3-khung", "png-rgb-16-bit", "jpeg-1x1"],
)
def test_real_ai_copy_from_more_sources_passes(kind, pillow_state_restored):  # noqa: F811
    data = ai_source(kind)
    with Image.open(io.BytesIO(data)) as source:  # ảnh gốc mang đúng hồ sơ màu chở chữ
        assert source.info.get("icc_profile") == PROFILE
    assert_clean_ai_copies(data)


@pytest.mark.parametrize("orientation", range(1, 9))
def test_real_ai_copy_of_rotated_photo_passes(orientation, pillow_state_restored):  # noqa: F811
    data = save(noisy("RGB", (240, 160)), "JPEG", exif=exif_with(orientation), icc_profile=PROFILE,
                xmp=XMP_PACKET)  # fmt: skip
    ai = assert_clean_ai_copies(data)
    # Hướng 5–8 là xoay 90°: bản gửi AI đã xoay đúng chiều (đổi rộng, cao) mà vẫn qua lớp kiểm.
    assert (ai.width, ai.height) == ((160, 240) if orientation >= 5 else (240, 160))


# ================================================================== 2. hồ sơ màu ở khối khác


VP8L = webp_chunk(b"VP8L", b"\x2f\x00\x00\x00\x00")
VP8X_ICC = webp_chunk(b"VP8X", b"\x20" + b"\x00" * 9)  # cờ "có hồ sơ màu"
ICC_APP2 = jpeg_segment(0xE2, b"ICC_PROFILE\x00\x01\x01" + PROFILE)
PNG_ICCP = png_chunk(b"iCCP", b"ICC Profile\x00\x00" + zlib.compress(PROFILE))


@pytest.mark.parametrize(
    ("data", "mime", "message"),
    [
        (make_jpeg(jpeg_segment(0xFE, PROFILE)), "image/jpeg", IMAGE_METADATA_MESSAGE),
        (make_jpeg(jpeg_segment(0xEF, b"ICC_PROFILE\x00\x01\x01" + PROFILE)), "image/jpeg",
         IMAGE_METADATA_MESSAGE),
        (make_jpeg(jpeg_segment(0xE2, b"icc_profile\x00\x01\x01" + PROFILE)), "image/jpeg",
         IMAGE_METADATA_MESSAGE),
        (b"\xff\xd8" + JFIF + SOS + SCAN + ICC_APP2 + SOS + SCAN + b"\xff\xd9", "image/jpeg",
         IMAGE_METADATA_MESSAGE),
        (make_jpeg(tail=ICC_APP2), "image/jpeg", IMAGE_BROKEN_MESSAGE),
        (make_png(png_chunk(b"prVt", PROFILE)), "image/png", IMAGE_METADATA_MESSAGE),
        (make_png(png_chunk(b"ICCP", PROFILE)), "image/png", IMAGE_METADATA_MESSAGE),
        (PNG_SIGNATURE + IHDR + IDAT + PNG_ICCP + IEND, "image/png", IMAGE_METADATA_MESSAGE),
        (make_png(png_chunk(b"cICP", b"\x01\x0d\x00\x01")), "image/png", IMAGE_METADATA_MESSAGE),
        (make_png() + PNG_ICCP, "image/png", IMAGE_BROKEN_MESSAGE),
        (make_webp(webp_chunk(b"iccp", PROFILE), VP8L, first=VP8X_ICC), "image/webp",
         IMAGE_METADATA_MESSAGE),
        (make_webp(VP8L, webp_chunk(b"ICCP", PROFILE), first=VP8X_ICC), "image/webp",
         IMAGE_METADATA_MESSAGE),
    ],
    ids=["jpeg-chu-thich", "jpeg-app15", "jpeg-app2-ten-viet-thuong", "jpeg-app2-giua-luot-quet",
         "jpeg-sau-eoi", "png-chunk-rieng", "png-ICCP-viet-hoa", "png-iccp-sau-idat", "png-cicp",
         "png-sau-iend", "webp-iccp-viet-thuong", "webp-iccp-sau-anh"],
)  # fmt: skip
def test_icc_profile_hidden_in_other_blocks_is_rejected(data, mime, message):
    with pytest.raises(AIError) as info:
        prepare_images([ImageInput(data=data, mime=mime)])
    assert str(info.value) == message


# ================================================================== 3. trọng tài Pillow

# Khóa ``info`` Pillow đặt cho ảnh sạch (đã thử với ảnh Pillow tự ghi); khóa khác là metadata.
SAFE_INFO = {
    "image/jpeg": {"jfif", "jfif_version", "jfif_unit", "jfif_density", "dpi", "adobe",
                   "adobe_transform", "progressive", "progression"},
    "image/png": {"dpi", "aspect", "gamma", "srgb", "transparency"},
    "image/webp": {"loop", "background", "duration", "timestamp"},
}  # fmt: skip
RAW_TIFF = exif_with(1)[6:]  # EXIF không có đầu "Exif\0\0" (bộ dò chuỗi không thấy)
XMP_BARE = XMP_PACKET.replace(b"<x:xmpmeta", b"<x:xmp")  # XMP không có dấu "<x:xmpmeta"
META_BLOCKS = {
    "image/jpeg": [
        jpeg_segment(0xE1, b"Exif\x00\x00" + RAW_TIFF), ICC_APP2, jpeg_segment(0xFE, SECRET_TEXT),
        jpeg_segment(0xE1, b"http://ns.adobe.com/xap/1.0/\x00" + XMP_BARE),
        jpeg_segment(0xED, b"Photoshop 3.0\x00" + SECRET_TEXT),
    ],
    "image/png": [
        PNG_ICCP, png_chunk(b"eXIf", RAW_TIFF), png_chunk(b"tEXt", b"Comment\x00" + SECRET_TEXT),
        png_chunk(b"zTXt", b"Comment\x00\x00" + zlib.compress(SECRET_TEXT)),
        png_chunk(b"iTXt", b"XML:com.adobe.xmp\x00\x00\x00\x00\x00" + XMP_BARE),
        png_chunk(b"bKGD", b"\x00\x01\x00\x02\x00\x03"), png_chunk(b"cHRM", ICC_SECRET[:32]),
    ],
    "image/webp": [
        webp_chunk(b"ICCP", PROFILE), webp_chunk(b"EXIF", RAW_TIFF), webp_chunk(b"XMP ", XMP_BARE),
    ],
}  # fmt: skip
BARE_DATA = [PROFILE[:200], RAW_TIFF, XMP_BARE, SECRET_TEXT, ICC_APP2[:80]]


def corpus():
    items = []
    for size in ((8, 8), (33, 17)):
        for mode in ("RGB", "L", "CMYK"):
            for args in ({}, {"progressive": True}, {"restart_marker_blocks": 1}):
                items.append(("image/jpeg", save(noisy(mode, size), "JPEG", **args)))
        for mode, args in (("RGB", {}), ("RGBA", {}), ("P", {"transparency": 1}), ("1", {}),
                           ("I;16", {}), ("RGB", {"dpi": (72, 72)})):  # fmt: skip
            items.append(("image/png", save(noisy(mode, size), "PNG", **args)))
        for mode, args in (("RGB", {}), ("RGBA", {}), ("RGBA", {"lossless": True})):
            items.append(("image/webp", save(noisy(mode, size), "WEBP", **args)))
    return items


def blocks(mime, data):
    """(đầu, cuối) các khối JPEG trước lượt quét đầu, các chunk PNG, các chunk WebP."""
    found = []
    if mime == "image/jpeg":
        i = 2
        while i + 4 <= len(data) and data[i] == 0xFF and data[i + 1] not in (0xDA, 0xD9):
            end = i + 2 + int.from_bytes(data[i + 2 : i + 4], "big")
            found.append((i, end))
            i = end
    elif mime == "image/png":
        i = len(PNG_SIGNATURE)
        while i + 12 <= len(data):
            end = i + 12 + int.from_bytes(data[i : i + 4], "big")
            found.append((i, end))
            i = end
    else:
        i = 12
        while i + 8 <= len(data):
            size = int.from_bytes(data[i + 4 : i + 8], "little")
            end = i + 8 + size + (size & 1)
            found.append((i, min(end, len(data))))
            i = end
    return found


def length_field(mime, start):
    """(vị trí, số byte, thứ tự byte) của trường độ dài trong khối bắt đầu ở ``start``."""
    if mime == "image/jpeg":
        return start + 2, 2, "big"
    if mime == "image/png":
        return start, 4, "big"
    return start + 4, 4, "little"


def mutate(rng, mime, data):
    data = bytearray(data)
    for _ in range(rng.randint(1, 3)):
        if len(data) < 12:
            break
        found = blocks(mime, bytes(data))
        kind = rng.randrange(9) if found else rng.choice([0, 3, 5, 7])
        if kind == 0:  # khối metadata chèn ở chỗ bất kỳ (kể cả giữa dữ liệu nén)
            at = rng.randrange(2, len(data) + 1)
            data[at:at] = rng.choice(META_BLOCKS[mime])
        elif kind == 1:  # khối metadata chèn đúng ranh giới khối
            at = rng.choice(found)[rng.randrange(2)]
            data[at:at] = rng.choice(META_BLOCKS[mime])
        elif kind == 2:  # lặp một khối
            start, end = rng.choice(found)
            at = rng.choice(found)[1]
            data[at:at] = data[start:end]
        elif kind == 3:  # lật vài byte
            for _ in range(rng.randint(1, 6)):
                data[rng.randrange(len(data))] = rng.randrange(256)
        elif kind == 4:  # sửa trường độ dài
            at, size, order = length_field(mime, rng.choice(found)[0])
            value = int.from_bytes(data[at : at + size], order) + rng.choice([-4, -1, 1, 3, 16])
            data[at : at + size] = max(0, min(value, 256**size - 1)).to_bytes(size, order)
        elif kind == 5:  # cắt cụt
            del data[rng.randrange(8, len(data)) :]
        elif kind == 6:  # xóa một khối
            start, end = rng.choice(found)
            del data[start:end]
        elif kind == 7:  # dữ liệu metadata trần, không bọc trong khối
            at = rng.randrange(2, len(data) + 1)
            data[at:at] = rng.choice(BARE_DATA)
        elif len(found) >= 2:  # đổi chỗ hai khối
            (a, b), (c, d) = sorted(rng.sample(found, 2))
            if b <= c:
                data[a:d] = data[c:d] + data[b:c] + data[a:b]
    if mime == "image/webp" and len(data) >= 8 and rng.random() < 0.8:
        data[4:8] = (len(data) - 8).to_bytes(4, "little")  # sửa lại độ dài RIFF cho khớp
    return bytes(data)


def pillow_metadata(data, mime):
    """Khóa ``info`` ngoài ``SAFE_INFO`` và EXIF mà Pillow đọc ra (Pillow không mở được: rỗng)."""
    try:
        image = Image.open(io.BytesIO(data))
    except Exception:  # file đột biến: Pillow báo đủ loại lỗi
        return set()
    with image:
        with contextlib.suppress(Exception):
            image.load()  # PNG: chunk sau IDAT chỉ được đọc khi load
        found = set(image.info) - SAFE_INFO[mime]
        with contextlib.suppress(Exception):
            if len(image.getexif()):
                found.add("exif")
    return found


def test_pillow_oracle_sees_metadata_in_unchecked_files():
    """Đối chứng cho trọng tài: ảnh sạch không có khóa lạ; chèn khối metadata thì Pillow thấy."""
    for mime, data in corpus():
        assert pillow_metadata(data, mime) == set(), mime
    jpeg = save(noisy("RGB", (8, 8)), "JPEG")
    assert "exif" in pillow_metadata(jpeg[:2] + META_BLOCKS["image/jpeg"][0] + jpeg[2:],
                                     "image/jpeg")  # fmt: skip
    png = save(noisy("RGB", (8, 8)), "PNG")
    assert "icc_profile" in pillow_metadata(png[:33] + PNG_ICCP + png[33:], "image/png")
    simple = save(noisy("RGB", (8, 8)), "WEBP")  # dạng đơn giản: RIFF, WEBP, một chunk VP8
    canvas = (7).to_bytes(3, "little") * 2  # 8 × 8 (lưu rộng − 1, cao − 1)
    body = webp_chunk(b"VP8X", b"\x20\x00\x00\x00" + canvas) + webp_chunk(b"ICCP", PROFILE)
    webp = b"RIFF" + (len(simple) - 8 + len(body)).to_bytes(4, "little") + simple[8:12] + body
    assert "icc_profile" in pillow_metadata(webp + simple[12:], "image/webp")


def test_mutated_images_accepted_by_check_carry_no_metadata_pillow_reads():
    rng = random.Random(20261023)
    items = corpus()
    for mime, data in items:  # ảnh gốc của kho đều qua
        assert prepare_images([ImageInput(data=data, mime=mime)])
    accepted, leaks = 0, []
    for _ in range(4000):
        mime, base = rng.choice(items)
        data = mutate(rng, mime, base)
        try:
            prepare_images([ImageInput(data=data, mime=mime)])
        except AIError:  # ngoại lệ khác AIError làm test hỏng ngay
            continue
        accepted += 1
        if found := pillow_metadata(data, mime):
            leaks.append((mime, sorted(found), data[:48].hex()))
    assert accepted > 200  # test có thử thật đường "nhận", không phải mọi ảnh đều bị từ chối
    assert leaks == []

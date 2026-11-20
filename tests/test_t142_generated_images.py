"""T-142: ảnh Cloudflare trả về → WebP sạch, thẻ ảnh AI, kho ``data/ai_images/``
(LC-T140-5, -6, -13). Ảnh giả dựng trong test, không ảnh thật, không mạng."""

from __future__ import annotations

import hashlib
import io
import os
import struct
import sys
import time
import traceback
import zlib
from pathlib import Path

import PIL
import pytest
from PIL import ExifTags, Image, ImageCms, PngImagePlugin

from seo_app.ai.base import _check_webp
from seo_app.config import PROJECT_ROOT
from seo_app.images import generated as gen
from seo_app.images import process
from seo_app.images.data_dir import MSG_DATA_DIR_LINK
from seo_app.images.process import ImageProcessError, webp_chunks
from seo_app.images.tags import SOURCE_AI, ImageTags

XMP = (
    b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF><rdf:Description '
    b'xmlns:exif="http://ns.adobe.com/exif/1.0/" exif:GPSLatitude="16,3.3265N">XMP-BI-MAT'
    b"</rdf:Description></rdf:RDF></x:xmpmeta>"
)
# Dấu vết đủ dài (≥ 6 byte) để không trùng ngẫu nhiên với dữ liệu ảnh đã nén.
DAU_VET = (b"BI-MAT", b"XMP-BI-MAT", b"Exif\x00\x00", b"xmpmeta", b"iPhone 15", b"TAC-GIA")


def _noise(size=(512, 512)) -> Image.Image:
    return Image.effect_noise(size, 80).convert("RGB")


def _save(image: Image.Image, fmt: str, **params) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, fmt, **params)
    return buffer.getvalue()


def _exif() -> bytes:
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "Apple"
    exif[ExifTags.Base.Model] = "iPhone 15 Pro"
    exif[ExifTags.Base.Artist] = "TAC-GIA-BI-MAT"
    gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
    gps[1], gps[2] = "N", (16.0, 3.0, 20.0)
    gps[3], gps[4] = "E", (108.0, 12.0, 30.0)
    return exif.tobytes()


def _icc() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def _dirty(fmt: str, size=(640, 480)) -> bytes:
    image = _noise(size)
    if fmt == "JPEG":
        return _save(
            image, "JPEG", exif=_exif(), xmp=XMP, icc_profile=_icc(), comment=b"COM-BI-MAT"
        )
    if fmt == "PNG":
        info = PngImagePlugin.PngInfo()
        info.add_text("Comment", "PNG-TEXT-BI-MAT")
        info.add_itxt("XML:com.adobe.xmp", XMP.decode())
        return _save(image, "PNG", pnginfo=info, exif=_exif(), icc_profile=_icc())
    return _save(image, "WEBP", exif=_exif(), xmp=XMP, icc_profile=_icc())


# ------------------------------------------------------------------ ảnh về → WebP sạch


def test_clean_image_becomes_clean_webp_without_upscaling():
    web = gen.make_generated_web_image(_save(_noise((1024, 1024)), "JPEG"))
    assert web.mime == "image/webp"
    assert (web.width, web.height) == (1024, 1024)  # không phóng to
    assert web.gps is None
    assert _check_webp(web.data) is None


@pytest.mark.parametrize("fmt", ["JPEG", "PNG", "WEBP"], ids=["jpg", "png", "webp"])
def test_dirty_image_comes_out_without_any_metadata(fmt):
    data = _dirty(fmt)
    assert any(mark in data for mark in (b"BI-MAT", b"Exif", b"ICC")), "ảnh vào phải bẩn thật"
    web = gen.make_generated_web_image(data)
    assert _check_webp(web.data) is None
    assert set(webp_chunks(web.data)) <= {b"VP8 ", b"VP8L", b"VP8X", b"ALPH"}
    for mark in DAU_VET:
        assert mark not in web.data, mark
    with Image.open(io.BytesIO(web.data)) as image:
        assert not {"exif", "xmp", "icc_profile", "comment"} & set(image.info)


def test_large_image_is_reduced_to_the_web_edge():
    web = gen.make_generated_web_image(_save(_noise((1800, 1000)), "PNG"))
    assert max(web.width, web.height) == 1600


def test_web_settings_are_passed_through():
    web = gen.make_generated_web_image(
        _save(_noise((1024, 1024)), "JPEG"), max_edge_px=800, webp_quality=60
    )
    assert (web.width, web.height) == (800, 800)


def _animated(fmt: str) -> bytes:
    frames = [_noise((300, 300)), _noise((300, 300))]
    return _save(frames[0], fmt, save_all=True, append_images=frames[1:], duration=100)


@pytest.mark.parametrize("fmt", ["WEBP", "PNG"], ids=["webp", "apng"])
def test_animated_image_is_refused(fmt):
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(_animated(fmt))
    assert str(info.value) == gen.MSG_ANIMATED


@pytest.mark.parametrize(
    "size", [(4096, 256), (2049, 512), (255, 512), (200, 200)], ids=["4096", "2049", "255", "200"]
)
def test_odd_size_is_refused(size):
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(_save(_noise(size), "PNG"))
    assert str(info.value) == gen.MSG_SIZE.format(width=size[0], height=size[1])


def test_size_limits_are_accepted():
    small = gen.make_generated_web_image(_save(_noise((256, 256)), "PNG"))
    assert (small.width, small.height) == (256, 256)
    large = gen.make_generated_web_image(_save(_noise((2048, 256)), "PNG"))
    assert large.width == 1600


def _almost_one_color() -> Image.Image:
    image = Image.new("RGB", (512, 512), (120, 121, 122))
    for x in range(0, 512, 7):
        image.putpixel((x, x), (126, 127, 128))  # chênh 6 ≤ BLANK_SPREAD
    return image


@pytest.mark.parametrize(
    "image",
    [
        Image.new("RGB", (512, 512), (0, 0, 0)),
        Image.new("RGB", (512, 512), (255, 255, 255)),
        _almost_one_color(),
    ],
    ids=["den", "trang", "gan-mot-mau"],
)
def test_blank_image_is_refused(image):
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(_save(image, "PNG"))
    assert str(info.value) == gen.MSG_BLANK


def test_image_with_some_contrast_is_not_blank():
    image = _almost_one_color()
    image.putpixel((3, 5), (140, 120, 120))  # một kênh chênh 20
    web = gen.make_generated_web_image(_save(image, "PNG"))
    assert _check_webp(web.data) is None


# ------------------------------------------------------------------ câu báo của ảnh AI (SL-T142-2)

# Chữ chỉ có trong câu của ảnh trong thư mục (``process``): ảnh Cloudflare không được báo các câu
# này (người dùng sẽ đi kiểm nhầm Google Drive, đuôi file, iPhone).
PHOTO_HINTS = ("Google Drive", "đổi đuôi", "iPhone", "HEIC", "thu nhỏ", "File này", "File ảnh")
AI_MESSAGES = (gen.MSG_BROKEN, gen.MSG_FORMAT, gen.MSG_TOO_BIG, gen.MSG_ENCODE)


def _png_header(width: int, height: int) -> bytes:
    """PNG chỉ có phần đầu khai cỡ ảnh (không có điểm ảnh)."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunks = [(b"IHDR", ihdr), (b"IEND", b"")]
    return b"\x89PNG\r\n\x1a\n" + b"".join(
        struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body))
        for name, body in chunks
    )


def _photo_hints(error: BaseException) -> list[str]:
    """Chữ của ảnh trong thư mục có trong câu báo hay dấu vết lỗi đầy đủ."""
    text = "".join(traceback.format_exception(error))
    return [hint for hint in PHOTO_HINTS if hint in text]


_JPEG = _save(_noise((300, 300)), "JPEG")
NOT_USABLE = {
    "rong": (b"", gen.MSG_BROKEN),
    "png-hong": (b"\x89PNG\r\n\x1a\n" + b"rac" * 200, gen.MSG_BROKEN),
    "jpeg-cut": (_JPEG[: len(_JPEG) // 2], gen.MSG_BROKEN),
    "chu": (b"khong phai anh", gen.MSG_FORMAT),
    "khong-byte": ("khong phai byte", gen.MSG_FORMAT),
    "gif": (_save(_noise((300, 300)), "GIF"), gen.MSG_FORMAT),
    "bmp": (_save(_noise((300, 300)), "BMP"), gen.MSG_FORMAT),
    "heic": (b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"\x00" * 64, gen.MSG_FORMAT),
    "svg": (b'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300"/>', gen.MSG_FORMAT),
    "81-trieu": (_png_header(9000, 9000), gen.MSG_TOO_BIG),
    "900-trieu": (_png_header(30000, 30000), gen.MSG_TOO_BIG),
}


@pytest.mark.parametrize("data, message", list(NOT_USABLE.values()), ids=list(NOT_USABLE))
def test_not_an_allowed_image_is_refused(data, message):
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(data)
    assert str(info.value) == message
    assert not _photo_hints(info.value)  # cả câu cũ cũng không nằm trong dấu vết lỗi


def test_file_too_large_gets_the_ai_message(monkeypatch):
    data = _save(_noise((300, 300)), "PNG")
    monkeypatch.setattr(process, "MAX_IMAGE_BYTES", len(data) - 1)
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(data)
    assert str(info.value) == gen.MSG_TOO_BIG
    assert not _photo_hints(info.value)


def _process_messages() -> dict[str, str]:
    """Mọi câu lỗi cố định của ``process`` (``_MSG_*``, kể cả câu thêm sau này) cộng hai câu số
    điểm ảnh. Câu cỡ file: ``test_file_too_large_gets_the_ai_message``."""
    found = {
        name: value
        for name, value in vars(process).items()
        if name.startswith("_MSG_") and isinstance(value, str)
    }
    found["nhieu-diem-anh"] = str(process._too_many_pixels())
    found["nhieu-diem-anh-so"] = str(process._too_many_pixels(81_000_000))
    return found


PROCESS_MESSAGES = _process_messages()
EXPECTED = {
    "_MSG_NOT_IMAGE": gen.MSG_FORMAT,
    "_MSG_HEIC_OFF": gen.MSG_FORMAT,
    "_MSG_HEIF_GRID": gen.MSG_FORMAT,
    "_MSG_HEIF_ALPHA": gen.MSG_FORMAT,
    "_MSG_BROKEN": gen.MSG_BROKEN,
    "_MSG_EMPTY": gen.MSG_BROKEN,
    "_MSG_GPS_LOST": gen.MSG_BROKEN,
    "_MSG_ENCODE": gen.MSG_ENCODE,
    "nhieu-diem-anh": gen.MSG_TOO_BIG,
    "nhieu-diem-anh-so": gen.MSG_TOO_BIG,
}


def test_expected_table_matches_process_messages():
    assert set(EXPECTED) | {"_MSG_OLD_PILLOW"} <= set(PROCESS_MESSAGES)


@pytest.mark.parametrize("name", list(PROCESS_MESSAGES))
def test_process_messages_become_ai_image_messages(name):
    original = ImageProcessError(PROCESS_MESSAGES[name])
    converted = gen._ai_image_error(original)
    if name == "_MSG_OLD_PILLOW":  # không nói về ảnh: mở lại app bằng run.bat mới sửa được
        assert converted is original
        return
    assert str(converted) == EXPECTED.get(name, gen.MSG_BROKEN)
    assert str(converted) in AI_MESSAGES
    assert not _photo_hints(converted)


def test_unknown_process_message_never_leaks():
    converted = gen._ai_image_error(ImageProcessError("Câu mới của ảnh trong thư mục Google Drive"))
    assert str(converted) == gen.MSG_BROKEN


def test_old_pillow_message_is_kept(monkeypatch):
    monkeypatch.setattr(PIL, "__version__", "12.3.0")
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(_save(_noise((300, 300)), "PNG"))
    assert str(info.value) == process._MSG_OLD_PILLOW


@pytest.mark.parametrize(
    "raised, message",
    [
        (process._MSG_BROKEN, gen.MSG_BROKEN),
        (process._MSG_ENCODE, gen.MSG_ENCODE),
        (process._MSG_GPS_LOST, gen.MSG_BROKEN),
    ],
    ids=["hong", "nen", "gps"],
)
def test_web_step_errors_get_ai_messages(monkeypatch, raised, message):
    def broken_web(_data: bytes, **_kwargs) -> process.WebImage:
        raise ImageProcessError(raised)

    monkeypatch.setattr(gen, "make_web_image", broken_web)
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(_save(_noise((300, 300)), "PNG"))
    assert str(info.value) == message
    assert not _photo_hints(info.value)


@pytest.mark.parametrize(
    "kwargs, name",
    [
        ({"max_edge_px": 10}, "max_edge_px"),
        ({"max_edge_px": True}, "max_edge_px"),
        ({"webp_quality": 0}, "webp_quality"),
        ({"webp_quality": "80"}, "webp_quality"),
    ],
    ids=["canh-nho", "canh-bool", "chat-0", "chat-chu"],
)
@pytest.mark.parametrize("data", [_JPEG, b"rac"], ids=["anh", "rac"])
def test_bad_image_settings_keep_their_own_message(kwargs, name, data):
    """Cấu hình sai: câu cấu hình (tạo lại không sửa được), báo trước khi mở ảnh."""
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(data, **kwargs)
    assert str(info.value).startswith(f"Cấu hình ảnh không hợp lệ: {name}")


def test_wrap_generated_tags_are_set_by_code():
    wrapped = gen.wrap_generated(_dirty("JPEG"), category="cổng INOX")
    assert wrapped.sha256 == hashlib.sha256(wrapped.data).hexdigest()
    assert wrapped.tags == ImageTags(source=SOURCE_AI, category="Cổng inox")
    assert wrapped.tags.is_ai
    assert not (wrapped.tags.project_code or wrapped.tags.area or wrapped.tags.phase)


@pytest.mark.parametrize("category", ["Nhà anh Tuấn", "x" * 500, ""], ids=["khach", "dai", "rong"])
def test_unknown_category_is_dropped_not_kept(category):
    assert gen.ai_image_tags(category) == ImageTags(source=SOURCE_AI)


def test_file_name_always_marks_ai():
    name = gen.generated_file_name(gen.ai_image_tags("cổng inox"), alt="Minh họa bản lề")
    assert name.startswith("minh-hoa-ai-")
    assert name.endswith(".webp")


# ------------------------------------------------------------------ kho data/ai_images/


@pytest.fixture
def webp() -> bytes:
    return gen.make_generated_web_image(_save(_noise((300, 300)), "PNG")).data


@pytest.fixture
def store(tmp_path) -> gen.AIImageStore:
    return gen.AIImageStore(tmp_path / "data" / "ai_images")


def _files(store_dir: Path) -> list[str]:
    return sorted(path.name for path in store_dir.iterdir()) if store_dir.exists() else []


def test_save_and_load_by_hash(store, webp, tmp_path):
    sha = store.save(webp)
    assert sha == hashlib.sha256(webp).hexdigest()
    assert _files(tmp_path / "data" / "ai_images") == [f"{sha}.webp"]
    assert store.load(sha) == webp
    assert store.save(webp) == sha  # lưu lại: giữ đúng một file, không file tạm sót lại
    assert _files(tmp_path / "data" / "ai_images") == [f"{sha}.webp"]
    assert repr(store) == "AIImageStore()"


@pytest.mark.parametrize("bad", ["../x", "A" * 64, "0" * 63, "", None, "0" * 64 + ".webp"])
def test_load_refuses_odd_names(store, bad):
    with pytest.raises(gen.AIImageStoreError) as info:
        store.load(bad)
    assert str(info.value) == gen.MSG_STORE_BAD


def test_load_missing_image(store):
    with pytest.raises(gen.AIImageStoreError) as info:
        store.load("0" * 64)
    assert str(info.value) == gen.MSG_STORE_MISSING


def test_load_detects_a_changed_file(store, webp, tmp_path):
    sha = store.save(webp)
    path = tmp_path / "data" / "ai_images" / f"{sha}.webp"
    other = gen.make_generated_web_image(_save(_noise((300, 300)), "PNG")).data
    path.write_bytes(other)
    with pytest.raises(gen.AIImageStoreError) as info:
        store.load(sha)
    assert str(info.value) == gen.MSG_STORE_CHANGED
    path.write_bytes(b"RIFF" + b"\x00" * 30)
    with pytest.raises(gen.AIImageStoreError):
        store.load(sha)


def test_load_detects_dirty_webp_with_matching_name(store, tmp_path):
    dirty = _save(_noise((300, 300)), "WEBP", exif=_exif())
    sha = hashlib.sha256(dirty).hexdigest()
    folder = tmp_path / "data" / "ai_images"
    folder.mkdir(parents=True)
    (folder / f"{sha}.webp").write_bytes(dirty)
    with pytest.raises(gen.AIImageStoreError) as info:
        store.load(sha)
    assert str(info.value) == gen.MSG_STORE_CHANGED


def test_load_refuses_too_large_file(store, tmp_path, monkeypatch, webp):
    sha = store.save(webp)
    monkeypatch.setattr(gen, "MAX_STORED_BYTES", 10)
    with pytest.raises(gen.AIImageStoreError) as info:
        store.load(sha)
    assert str(info.value) == gen.MSG_STORE_CHANGED


@pytest.mark.parametrize(
    "data",
    [b"", b"khong phai webp", "chu", _save(_noise((300, 300)), "WEBP", exif=b"Exif\x00\x00x")],
    ids=["rong", "chu-byte", "chu", "co-exif"],
)
def test_save_refuses_anything_but_clean_webp(store, data, tmp_path):
    with pytest.raises(gen.AIImageStoreError) as info:
        store.save(data)
    assert str(info.value) == gen.MSG_STORE_BAD
    assert _files(tmp_path / "data" / "ai_images") == []


def test_save_refuses_oversized_webp(store, webp, monkeypatch):
    monkeypatch.setattr(gen, "MAX_STORED_BYTES", len(webp) - 1)
    with pytest.raises(gen.AIImageStoreError):
        store.save(webp)


def test_save_refuses_folder_that_git_would_commit(webp):
    folder = PROJECT_ROOT / "khong-nam-trong-data-t142"
    with pytest.raises(gen.AIImageStoreError) as info:
        gen.AIImageStore(folder).save(webp)
    assert str(info.value) == gen.MSG_STORE_NOT_IGNORED
    assert not folder.exists()


def test_default_folder_is_ignored_by_git():
    from seo_app.images.process import _cache_dir_is_ignored

    assert gen.AI_IMAGES_DIR == PROJECT_ROOT / "data" / "ai_images"
    assert _cache_dir_is_ignored(gen.AI_IMAGES_DIR)


def _make_link(link: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def test_data_folder_link_is_never_read_or_written(tmp_path, webp):
    outside = tmp_path / "ngoai"
    _make_link(tmp_path / "data", outside)
    store = gen.AIImageStore(tmp_path / "data" / "ai_images")
    with pytest.raises(gen.AIImageStoreError) as info:
        store.save(webp)
    assert str(info.value) == MSG_DATA_DIR_LINK
    assert list(outside.iterdir()) == []
    with pytest.raises(gen.AIImageStoreError):
        store.load(hashlib.sha256(webp).hexdigest())
    assert store.cleanup([]) == 0


# ------------------------------------------------------------------ dọn kho


def _put(folder: Path, name: str, *, age_days: float, size: int = 100) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(b"x" * size)
    moment = time.time() - age_days * 24 * 60 * 60
    os.utime(path, (moment, moment))
    return path


def _sha(n: int) -> str:
    return hashlib.sha256(str(n).encode()).hexdigest()


def test_cleanup_drops_only_old_unreferenced_matching_files(tmp_path):
    folder = tmp_path / "data" / "ai_images"
    store = gen.AIImageStore(folder)
    old = _put(folder, f"{_sha(1)}.webp", age_days=20)
    kept = _put(folder, f"{_sha(2)}.webp", age_days=20)
    fresh = _put(folder, f"{_sha(3)}.webp", age_days=2)
    others = [
        _put(folder, "ghi-chu.txt", age_days=30),
        _put(folder, f"{_sha(4).upper()}.webp", age_days=30),
        _put(folder, f"{_sha(5)}.webp.tmp", age_days=30),
        _put(folder, "tmpabc.tmp", age_days=30),
    ]
    (folder / f"{_sha(6)}.webp").mkdir()  # thư mục trùng mẫu tên: không phải file thường
    assert store.cleanup([_sha(2), "khong-phai-bam"]) == 1
    assert not old.exists()
    assert kept.exists() and fresh.exists()
    assert all(path.exists() for path in others)
    assert (folder / f"{_sha(6)}.webp").is_dir()


def test_cleanup_respects_file_count_limit_oldest_first(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "MAX_FILES", 3)
    folder = tmp_path / "data" / "ai_images"
    paths = [_put(folder, f"{_sha(n)}.webp", age_days=5 - n * 0.5) for n in range(6)]
    assert gen.AIImageStore(folder).cleanup([_sha(0)]) == 3
    assert paths[0].exists()  # cũ nhất nhưng còn được nháp nhắc tới
    assert [p.exists() for p in paths[1:]] == [False, False, False, True, True]


def test_cleanup_respects_total_size_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "MAX_TOTAL_BYTES", 250)
    folder = tmp_path / "data" / "ai_images"
    paths = [_put(folder, f"{_sha(n)}.webp", age_days=5 - n, size=100) for n in range(4)]
    assert gen.AIImageStore(folder).cleanup([]) == 2
    assert [p.exists() for p in paths] == [False, False, True, True]


def test_cleanup_of_missing_folder_is_quiet(tmp_path):
    assert gen.AIImageStore(tmp_path / "chua-co").cleanup([]) == 0


# ------------------------------------------------------------------ đầu vào PNG lạ


def _png_with_chunk(name: bytes, body: bytes) -> bytes:
    data = _save(_noise((300, 300)), "PNG")
    chunk = struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body))
    return data[:33] + chunk + data[33:]


def test_png_private_chunk_never_reaches_the_webp():
    data = _png_with_chunk(b"prVt", b"KHOI-RIENG-BI-MAT")
    web = gen.make_generated_web_image(data)
    assert b"KHOI-RIENG-BI-MAT" not in web.data
    assert _check_webp(web.data) is None

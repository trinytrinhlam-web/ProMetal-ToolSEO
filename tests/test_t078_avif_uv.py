"""T-078 (Thợ Máy): ``uv`` tối thiểu 0.13.4 (LC-T075-1, GHSA-hq85-5cpj-mr62) và bỏ ``.avif`` khỏi
danh sách đuôi ảnh (app không mở được AVIF: ``process.ALLOWED_FORMATS`` không có, từ T-047).

- ``pyproject.toml`` khai ``[tool.uv] required-version = ">=0.13.4"``: uv cũ hơn từ chối chạy.
- Khung chọn ảnh không liệt kê file ``.avif``; file AVIF đổi đuôi ``.jpg`` vẫn được liệt kê (theo
  đuôi) nhưng bị từ chối theo nội dung, đúng câu «không phải ảnh JPEG, PNG hoặc WebP».

Ảnh AVIF dựng bằng bộ mã hóa AVIF có sẵn trong Pillow 13 (không có thì dùng phần đầu file AVIF
viết tay). Không gọi mạng.
"""

from __future__ import annotations

import io
import tomllib

import pytest
from PIL import Image
from PIL import features as pil_features
from test_app_images import (  # noqa: F401  (``env``, ``previews``: fixture tự dùng)
    PROJECT,
    REAL_FILE,
    browse,
    by_key,
    env,
    jpeg,
    listing,
    open_article,
    open_sub,
    previews,
    write,
)

from seo_app.config import PROJECT_ROOT
from seo_app.images import folders, process
from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef
from seo_app.text import escape_markdown

NOT_IMAGE = "File này không phải ảnh JPEG, PNG hoặc WebP đọc được (có thể bị đổi đuôi hoặc hỏng)."
MAKERS = [process.open_image, process.make_preview, process.make_ai_image, process.make_web_image]
MAKER_IDS = ["open_image", "make_preview", "make_ai_image", "make_web_image"]


def _avif() -> bytes:
    if pil_features.check("avif"):
        buffer = io.BytesIO()
        Image.new("RGB", (64, 48), (200, 80, 40)).save(buffer, "AVIF", quality=60)
        data = buffer.getvalue()
        assert data[4:12] == b"ftypavif"
        return data
    body = b"ftypavif" + b"\x00\x00\x00\x00" + b"avifmif1miaf"
    return (len(body) + 4).to_bytes(4, "big") + body + b"\x00" * 200


# ================================================================ uv tối thiểu (yêu cầu 1)


def test_pyproject_requires_uv_0_13_4():
    data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["tool"]["uv"]["required-version"] == ">=0.13.4"


# ============================================================== bỏ .avif (yêu cầu 2)


def test_avif_is_not_an_image_extension():
    assert ".avif" not in folders.IMAGE_EXTENSIONS
    assert "AVIF" not in process.ALLOWED_FORMATS and "AVIF" not in process._allowed_formats()


@pytest.mark.parametrize("name", ["x.avif", "x.AVIF", "CT012/truoc/IMG_0001.avif"])
def test_image_ref_rejects_avif_name(name, monkeypatch):
    with pytest.raises(ImageFolderError) as info:
        ImageRef(0, name)
    assert (
        str(info.value) == "Chỉ nhận ảnh JPEG, PNG hoặc WebP (tạm chưa nhận ảnh HEIC của iPhone)."
    )
    monkeypatch.setattr(folders, "HEIC_ENABLED", True)  # bật lại HEIC cũng không nhận AVIF
    with pytest.raises(ImageFolderError) as info:
        ImageRef(0, name)
    assert str(info.value) == "Chỉ nhận ảnh JPEG, PNG, WebP hoặc HEIC/HEIF."


def test_folder_does_not_list_avif(tmp_path):
    root = tmp_path / "anh"
    for name in ("IMG_0001.avif", "IMG_0002.AVIF", "IMG_0003.Avif"):
        write(root / name, _avif())
    write(root / "IMG_0004.jpg", jpeg())
    listing_ = ImageLibrary([root]).list_folder(0, "")
    assert [entry.name for entry in listing_.images] == ["IMG_0004.jpg"]


@pytest.mark.parametrize("make", MAKERS, ids=MAKER_IDS)
def test_avif_renamed_jpg_rejected_by_content(tmp_path, make):
    root = tmp_path / "anh"
    write(root / "IMG_0005.jpg", _avif())
    library = ImageLibrary([root])
    (entry,) = library.list_folder(0, "").images  # đuôi .jpg: vẫn được liệt kê
    with pytest.raises(process.ImageProcessError) as info:
        make(library.read_image_bytes(entry.ref))
    assert str(info.value) == NOT_IMAGE == process._MSG_NOT_IMAGE


def test_picker_page_hides_avif_and_blocks_renamed_avif(project_root, tmp_path, monkeypatch):
    """Đường thật trên trang Soạn bài: ``.avif`` không có trong khung chọn ảnh; AVIF đổi đuôi
    ``.jpg`` có trong khung nhưng nút «Chọn» bị khóa, câu báo đúng."""
    root = tmp_path / "Anh cong trinh"
    write(root / REAL_FILE, jpeg())
    write(root / PROJECT / "truoc" / "IMG_0007.avif", _avif())
    write(root / PROJECT / "truoc" / "IMG_0008.jpg", _avif())
    monkeypatch.setenv("IMAGE_FOLDERS", str(root))
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "truoc")
    names = [entry.name for entry in listing(at).images]
    assert names == ["IMG_0001.jpg", "IMG_0008.jpg"]
    assert by_key(at, f"choose-{names.index('IMG_0008.jpg')}").disabled
    assert not by_key(at, f"choose-{names.index('IMG_0001.jpg')}").disabled
    assert escape_markdown(NOT_IMAGE) in [c.value for c in at.caption]

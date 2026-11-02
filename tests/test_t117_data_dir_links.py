"""T-117 (Thợ Máy): thư mục ``data/`` là liên kết thì cache ảnh xem trước và kho thẻ ảnh không ghi
ra ngoài thư mục dự án (LC-T116-1, Lá Chắn T-116 nhóm 1).

- Hàm dùng chung ``seo_app.images.data_dir``: ``lstat`` từng tầng từ ngay dưới gốc dự án xuống,
  không đi theo liên kết. ``PreviewCache`` kiểm trước mỗi lần đọc, ghi (gặp liên kết thì chỉ không
  dùng cache, ảnh xem trước vẫn có); ``ImageTagStore`` kiểm mỗi lần mở (gặp liên kết thì báo câu cố
  định, không tạo thư mục, không mở SQLite).
- Liên kết thật: junction trên Windows (``_winapi.CreateJunction``, không cần quyền quản trị),
  symlink trên Mac/Linux. Nhánh Mac/Linux và các loại reparse point được giả lập bằng kết quả
  ``lstat`` giả cho đúng một đường dẫn, nên chạy được trên mọi máy.

Không gọi mạng; mọi thư mục nằm trong ``tmp_path``, không đụng ``data/`` thật của dự án.
"""

from __future__ import annotations

import io
import os
import shutil
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from seo_app.images import process
from seo_app.images.data_dir import MSG_DATA_DIR_LINK, dir_has_link, is_link
from seo_app.images.folders import ImageLibrary, ImageRef
from seo_app.images.process import PreviewCache
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.storage import image_tags
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError

IS_WINDOWS = os.name == "nt"
# Reparse tag trên Windows: có bit «name surrogate» (0x20000000) là trỏ đi chỗ khác.
TAG_SYMLINK = 0xA000000C
TAG_MOUNT_POINT = 0xA0000003  # junction
TAG_LX_SYMLINK = 0xA000001D  # symlink tạo từ WSL
TAG_CLOUD = 0x9000601A  # file/thư mục «chỉ trực tuyến» của OneDrive (không phải liên kết)


def link_dir(link: Path, target: Path) -> None:
    """Liên kết thư mục không cần quyền quản trị: junction trên Windows, symlink trên Mac/Linux."""
    if IS_WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def jpeg(color: tuple[int, int, int], size: tuple[int, int] = (40, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG")
    return buffer.getvalue()


def files_in(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*") if p.is_file())


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả (``.gitignore`` chặn ``data/`` như thật); ``PROJECT_ROOT`` của hai module
    trỏ vào đó."""
    root = tmp_path / "du-an"
    root.mkdir()
    (root / ".gitignore").write_text("data/\n", encoding="utf-8")
    monkeypatch.setattr(process, "PROJECT_ROOT", root)
    monkeypatch.setattr(image_tags, "PROJECT_ROOT", root)
    return root


@pytest.fixture
def outside(tmp_path: Path) -> Path:
    folder = tmp_path / "ngoai-du-an"
    folder.mkdir()
    return folder


@pytest.fixture
def library(tmp_path: Path) -> ImageLibrary:
    root = tmp_path / "anh"
    root.mkdir()
    (root / "cong.jpg").write_bytes(jpeg((90, 120, 150)))
    (root / "cua.jpg").write_bytes(jpeg((150, 90, 60)))
    return ImageLibrary([root])


def fake_lstat(monkeypatch, path: Path, **fields) -> None:
    """``os.lstat`` của đúng ``path`` trả kết quả giả (giả lập Mac/Linux hay một loại reparse
    point); mọi đường dẫn khác vẫn là ``lstat`` thật."""
    real = os.lstat
    wanted = os.path.normcase(os.path.abspath(path))

    def lstat(p, *args, **kwargs):
        if os.path.normcase(os.path.abspath(os.fspath(p))) == wanted:
            return SimpleNamespace(**{"st_mode": stat.S_IFDIR | 0o755, **fields})
        return real(p, *args, **kwargs)

    monkeypatch.setattr(os, "lstat", lstat)


# ================================================================ hàm dùng chung


def test_real_dirs_have_no_link(project):
    (project / "data" / "image_previews").mkdir(parents=True)
    (project / "data" / "image_tags.sqlite").write_bytes(b"")
    assert not dir_has_link(project / "data" / "image_previews", project)
    assert not dir_has_link(project / "data", project)
    assert not is_link(project / "data" / "image_tags.sqlite")


def test_missing_levels_stop_without_error(project):
    """Chưa có ``data/`` (lần chạy đầu): không phải liên kết, app sẽ tự tạo thư mục thường."""
    assert not dir_has_link(project / "data" / "image_previews", project)
    assert not is_link(project / "data" / "image_previews" / "x.jpg")


@pytest.mark.parametrize("level", ["data", "data/image_previews"])
def test_real_link_at_any_level_is_found(project, outside, level):
    """Liên kết thật (junction trên Windows, symlink trên Mac/Linux) ở tầng ``data`` hay tầng
    con."""
    link = project / level
    link.parent.mkdir(parents=True, exist_ok=True)
    link_dir(link, outside)
    assert dir_has_link(project / "data" / "image_previews", project)
    assert is_link(link)


def test_root_reached_through_a_link_is_not_flagged(tmp_path, outside):
    """Thư mục cài app nằm dưới một lối tắt hợp lệ của máy: gốc và các tầng trên gốc không xét,
    chỉ xét từ ``data`` trở xuống."""
    real_root = tmp_path / "that"
    (real_root / "data").mkdir(parents=True)
    alias = tmp_path / "loi-tat"
    link_dir(alias, real_root)
    assert not dir_has_link(alias / "data", alias)


def test_outside_root_checks_dir_and_its_parent(tmp_path, outside):
    """Thư mục nằm ngoài gốc dự án (chỉ có trong test): xét chính nó và thư mục cha của nó."""
    other = tmp_path / "khac"
    other.mkdir()
    link_dir(other / "data", outside)
    assert dir_has_link(other / "data" / "image_previews", Path(__file__).parent)
    assert dir_has_link(other / "data", Path(__file__).parent)
    assert not dir_has_link(tmp_path / "thuong" / "data", Path(__file__).parent)


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"st_mode": stat.S_IFLNK | 0o777}, True),  # symlink trên Mac/Linux
        ({"st_file_attributes": stat.FILE_ATTRIBUTE_REPARSE_POINT, "st_reparse_tag": TAG_SYMLINK},
         True),
        ({"st_file_attributes": stat.FILE_ATTRIBUTE_REPARSE_POINT,
          "st_reparse_tag": TAG_MOUNT_POINT}, True),
        ({"st_file_attributes": stat.FILE_ATTRIBUTE_REPARSE_POINT,
          "st_reparse_tag": TAG_LX_SYMLINK}, True),
        ({"st_file_attributes": stat.FILE_ATTRIBUTE_REPARSE_POINT, "st_reparse_tag": TAG_CLOUD},
         False),
        ({}, False),
    ],
    ids=["symlink-posix", "symlink-windows", "junction", "symlink-wsl", "onedrive", "thu-muc"],
)  # fmt: skip
def test_simulated_link_kinds(project, monkeypatch, fields, expected):
    """Giả lập kết quả ``lstat`` của ``data``: symlink Mac/Linux, các reparse point trỏ đi chỗ khác
    là liên kết; thư mục «chỉ trực tuyến» của OneDrive/Drive và thư mục thường thì không."""
    (project / "data").mkdir()
    fake_lstat(monkeypatch, project / "data", **fields)
    assert dir_has_link(project / "data" / "image_previews", project) is expected


# ================================================================ cache ảnh xem trước


def test_preview_cache_normal_dirs_still_cache(project, library):
    """Canh: thư mục thường thì cache vẫn ghi và vẫn dùng lại như trước."""
    cache = PreviewCache(project / "data" / "image_previews")
    assert cache.enabled
    first = cache.get(library, ImageRef(0, "cong.jpg"))
    cached = files_in(project / "data" / "image_previews")
    assert len(cached) == 1
    cached[0].write_bytes(jpeg((1, 2, 3)))  # cache trả lại đúng file đã lưu
    assert cache.get(library, ImageRef(0, "cong.jpg")) == cached[0].read_bytes() != first


@pytest.mark.parametrize("level", ["data", "data/image_previews"])
def test_preview_cache_never_writes_through_link(project, outside, library, level):
    """``data`` hay ``data/image_previews`` là liên kết: ảnh xem trước vẫn có, không file nào được
    ghi ra nơi liên kết trỏ tới (gọi nhiều lần, nhiều ảnh)."""
    link = project / level
    link.parent.mkdir(parents=True, exist_ok=True)
    link_dir(link, outside)
    cache = PreviewCache(project / "data" / "image_previews")
    for name in ("cong.jpg", "cua.jpg", "cong.jpg"):
        assert cache.get(library, ImageRef(0, name))[:2] == b"\xff\xd8"
    assert files_in(outside) == []


def test_preview_cache_link_put_in_while_running(project, outside, library):
    """Cache đang chạy (đối tượng sống suốt phiên app), rồi ``data`` bị thay bằng liên kết: lần sau
    không ghi ra ngoài, và không đọc file đặt sẵn ở nơi liên kết trỏ tới."""
    cache = PreviewCache(project / "data" / "image_previews")
    ref = ImageRef(0, "cong.jpg")
    real = cache.get(library, ref)
    name = files_in(project / "data" / "image_previews")[0].name
    shutil.rmtree(project / "data")
    planted = jpeg((250, 0, 0))
    (outside / "image_previews").mkdir()
    (outside / "image_previews" / name).write_bytes(planted)
    link_dir(project / "data", outside)
    again = cache.get(library, ref)
    assert again != planted and again == real
    assert files_in(outside) == [outside / "image_previews" / name]  # không thêm file nào
    assert cache.get(library, ImageRef(0, "cua.jpg"))[:2] == b"\xff\xd8"
    assert len(files_in(outside)) == 1


def test_preview_cache_file_link_not_read(project, library, monkeypatch):
    """Chính file cache là liên kết (giả lập symlink Mac/Linux): không đọc nó, dựng lại ảnh; cũng
    không ghi đè qua nó."""
    cache = PreviewCache(project / "data" / "image_previews")
    ref = ImageRef(0, "cong.jpg")
    real = cache.get(library, ref)
    cached = files_in(project / "data" / "image_previews")[0]
    planted = jpeg((0, 250, 0))
    cached.write_bytes(planted)
    fake_lstat(monkeypatch, cached, st_mode=stat.S_IFLNK | 0o777)
    assert cache.get(library, ref) == real
    assert cached.read_bytes() == planted  # không ghi đè qua liên kết


def test_preview_cache_simulated_posix_link_at_data(project, library, monkeypatch):
    """Giả lập Mac/Linux: ``data`` là symlink. Không tạo thư mục, không ghi file nào."""
    (project / "data").mkdir()
    fake_lstat(monkeypatch, project / "data", st_mode=stat.S_IFLNK | 0o777)
    cache = PreviewCache(project / "data" / "image_previews")
    assert cache.get(library, ImageRef(0, "cong.jpg"))[:2] == b"\xff\xd8"
    assert not (project / "data" / "image_previews").exists()


# ================================================================ kho thẻ ảnh sửa tay


def test_tag_store_refuses_link_with_fixed_message(project, outside):
    """``data`` là liên kết: ghi thẻ báo đúng câu cố định (không đường dẫn), không tạo file nào ở
    nơi liên kết trỏ tới; đọc thẻ vẫn trả thẻ lấy từ tên thư mục kèm câu báo (app vẫn chạy)."""
    link_dir(project / "data", outside)
    store = ImageTagStore(project / "data" / "image_tags.sqlite")
    ref = ImageRef(0, "cong.jpg")
    with pytest.raises(ImageTagStoreError) as info:
        store.set(ref, ImageTags(source=SOURCE_AI))
    assert str(info.value) == MSG_DATA_DIR_LINK
    assert str(outside) not in str(info.value) and str(project) not in str(info.value)
    resolved = store.resolve(ref)
    assert resolved.error == MSG_DATA_DIR_LINK and not resolved.manual
    assert files_in(outside) == []


def test_tag_store_link_put_in_after_first_use(project, outside):
    """Kho đã dùng (file thật trong ``data/``), rồi ``data`` bị thay bằng liên kết: lần mở sau báo
    câu cố định, không tạo file ở nơi liên kết trỏ tới; file thật cũ không bị đụng."""
    store = ImageTagStore(project / "data" / "image_tags.sqlite")
    ref = ImageRef(0, "cong.jpg")
    store.set(ref, ImageTags(source=SOURCE_AI))
    kept = project.parent / "data-cu"
    (project / "data").rename(kept)
    before = (kept / "image_tags.sqlite").read_bytes()
    link_dir(project / "data", outside)
    with pytest.raises(ImageTagStoreError) as info:
        store.set(ImageRef(0, "cua.jpg"), ImageTags(source=SOURCE_AI))
    assert str(info.value) == MSG_DATA_DIR_LINK
    assert files_in(outside) == []
    assert (kept / "image_tags.sqlite").read_bytes() == before


def test_tag_store_simulated_posix_link_at_data(project, monkeypatch):
    """Giả lập Mac/Linux: ``data`` là symlink. Báo câu cố định trước khi tạo file SQLite."""
    (project / "data").mkdir()
    fake_lstat(monkeypatch, project / "data", st_mode=stat.S_IFLNK | 0o777)
    store = ImageTagStore(project / "data" / "image_tags.sqlite")
    with pytest.raises(ImageTagStoreError) as info:
        store.set(ImageRef(0, "cong.jpg"), ImageTags(source=SOURCE_AI))
    assert str(info.value) == MSG_DATA_DIR_LINK
    assert files_in(project / "data") == []


def test_tag_store_works_again_after_link_replaced_by_folder(project, outside):
    """Người dùng làm theo câu báo (thay lối tắt bằng thư mục thường): kho dùng lại được ngay,
    không cần mở lại app."""
    link_dir(project / "data", outside)
    store = ImageTagStore(project / "data" / "image_tags.sqlite")
    ref = ImageRef(0, "cong.jpg")
    with pytest.raises(ImageTagStoreError):
        store.set(ref, ImageTags(source=SOURCE_AI))
    os.rmdir(project / "data") if IS_WINDOWS else (project / "data").unlink()
    (project / "data").mkdir()
    store.set(ref, ImageTags(source=SOURCE_AI))
    assert store.get(ref) is not None
    assert (project / "data" / "image_tags.sqlite").is_file()
    assert files_in(outside) == []

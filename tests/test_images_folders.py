"""Test đọc thư mục ảnh an toàn (T-048): ``seo_app/images/folders.py``.

Ảnh trong test là bytes giả, tạo trong ``tmp_path`` (không commit ảnh thật). Junction chạy thật
trên Windows; symlink chạy trên Mac/Linux (và trên Windows nếu máy cho phép tạo symlink).
"""

from __future__ import annotations

import errno
import os
import stat
import sys
import unicodedata
from pathlib import Path
from types import SimpleNamespace

import pytest

from seo_app.images import folders
from seo_app.images.folders import (
    DEFAULT_MAX_ENTRIES,
    IMAGE_EXTENSIONS,
    MAX_PAGE_SIZE,
    FolderListing,
    ImageFolderError,
    ImageLibrary,
    ImageRef,
    SkipCounts,
    _is_link_stat,
    _match_disk_name,
)

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="junction chỉ có trên Windows")
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="chỉ tạo được trên Mac/Linux")


# ----- tiện ích ----------------------------------------------------------------------------


def write(path: Path, data: bytes = b"\xff\xd8\xff fake jpeg") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def make_junction(link: Path, target: Path) -> None:
    """Tạo junction Windows (không cần quyền quản trị)."""
    try:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    except (ImportError, AttributeError):  # pragma: no cover - dự phòng
        import subprocess

        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True)
    assert link.is_junction()


def make_symlink(link: Path, target: Path) -> None:
    """Tạo symlink; Windows không bật Developer Mode thì bỏ qua (đã có test junction thay)."""
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError as exc:
        if IS_WINDOWS:
            pytest.skip(
                f"Máy Windows này không cho tạo symlink (lỗi {exc.winerror}); xem test junction"
            )
        raise


def snapshot(folder: Path) -> dict[str, tuple[int, int]]:
    """Ảnh chụp cây thư mục (không theo liên kết): tên → (cỡ, thời điểm sửa)."""
    result = {}
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in dirnames + filenames:
            st = os.lstat(Path(dirpath, name))
            result[str(Path(dirpath, name).relative_to(folder))] = (st.st_size, st.st_mtime_ns)
    return result


def assert_no_abs_path(text: str, *paths: Path) -> None:
    for path in paths:
        for form in {str(path), str(path.resolve()), path.as_posix(), path.resolve().as_posix()}:
            assert form not in text, f"lộ đường dẫn tuyệt đối: {form!r}"


def raises_safely(func, *paths: Path) -> ImageFolderError:
    """Gọi ``func``, bắt buộc ``ImageFolderError`` có câu không chứa đường dẫn tuyệt đối."""
    with pytest.raises(ImageFolderError) as info:
        func()
    exc = info.value
    assert str(exc)
    assert_no_abs_path(str(exc), *paths)
    # Không xích theo lỗi hệ điều hành (OSError có chứa đường dẫn đầy đủ).
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__
    return exc


@pytest.fixture
def tree(tmp_path: Path) -> dict[str, Path]:
    """root/ (thư mục ảnh) và outside/ (ngoài phạm vi, có ảnh "bí mật")."""
    root = tmp_path / "anh"
    outside = tmp_path / "ngoai"
    write(root / "a.jpg", b"AAAA")
    write(root / "B.PNG", b"BB")
    write(root / "c.webp")
    write(root / "ghi-chu.txt", b"note")
    write(root / "dong.gif")
    write(root / "rong.jpg", b"")
    write(root / ".an.jpg")
    write(root / "CT012 - Cổng inox - Hải Châu" / "truoc" / "IMG_0001.HEIC")
    write(root / "CT012 - Cổng inox - Hải Châu" / "sau" / "IMG_0002.jpeg")
    write(outside / "bi-mat.jpg", b"SECRET")
    return {"root": root, "outside": outside, "tmp": tmp_path}


# ----- ImageRef: kiểm dạng đường dẫn -------------------------------------------------------


@pytest.mark.parametrize(
    "rel",
    [
        "a.jpg",
        "x.JPEG",
        "x.png",
        "x.webp",
        "x.heic",
        "x.HEIF",
        "x.avif",
        "CT012 - Cổng inox - Hải Châu/truoc/IMG_0001.jpg",
        "a b/c-d_e (1).jpg",
        "ảnh.tar.jpg",
    ],
)
def test_image_ref_accepts_normal_relative_paths(rel):
    ref = ImageRef(0, rel)
    assert ref.rel_path == rel
    assert ref.name == rel.split("/")[-1]


@pytest.mark.parametrize(
    "rel",
    [
        "",
        "..",
        "../a.jpg",
        "a/../b.jpg",
        "a/../../b.jpg",
        "./a.jpg",
        "a/./b.jpg",
        "a//b.jpg",
        "a/",
        "/etc/a.jpg",
        "//server/share/a.jpg",
        "\\\\server\\share\\a.jpg",
        "C:/a.jpg",
        "C:a.jpg",
        "c:\\a.jpg",
        "\\a.jpg",
        "a\\b.jpg",
        "..\\a.jpg",
        "a.jpg:stream",
        "a.jpg::$DATA",
        "CON.jpg",
        "nul",
        "aux.jpg",
        "COM1.jpg",
        "lpt9.png",
        "com¹.jpg",
        "a /b.jpg",
        "a./b.jpg",
        "a.jpg.",
        "a.jpg ",
        ".an.jpg",
        "a/.git/b.jpg",
        "a\x00.jpg",
        "a\nb.jpg",
        "a\x7fb.jpg",
        "x\ud800y.jpg",  # surrogate lẻ (L2, lượt 2)
        "a\udcff/b.jpg",
        "anh\u202egpj.jpg",  # ký tự điều khiển hướng chữ (lượt 2)
        "a\u2066b.jpg",
        "a\u2069/b.jpg",
        "x?.jpg",
        "*.jpg",
        "a<b.jpg",
        'a"b.jpg',
        "a|b.jpg",
        "x" * 300 + ".jpg",
        "/".join(["thu-muc"] * 200) + "/a.jpg",
    ],
)
def test_image_ref_rejects_unsafe_paths(rel):
    with pytest.raises(ImageFolderError):
        ImageRef(0, rel)


@pytest.mark.parametrize("rel", ["a.gif", "a.bmp", "a.tif", "a.lnk", "a.txt", "a", "a.jpg.exe"])
def test_image_ref_rejects_non_image_extensions(rel):
    with pytest.raises(ImageFolderError, match="Chỉ nhận ảnh"):
        ImageRef(0, rel)


@pytest.mark.parametrize("index", [-1, True, False, "0", 1.0, None])
def test_image_ref_rejects_bad_root_index(index):
    with pytest.raises(ImageFolderError):
        ImageRef(index, "a.jpg")


@pytest.mark.parametrize("rel", [None, 1, b"a.jpg", Path("a.jpg"), ["a.jpg"]])
def test_image_ref_rejects_non_string_paths(rel):
    with pytest.raises(ImageFolderError):
        ImageRef(0, rel)


def test_image_extensions_match_design():
    assert {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif"} == IMAGE_EXTENSIONS


# ----- thư mục gốc -------------------------------------------------------------------------


def test_roots_report_label_and_availability(tree):
    missing = tree["tmp"] / "usb-chua-cam"
    lib = ImageLibrary([tree["root"], missing, Path("tuong-doi")])
    roots = lib.roots()
    assert [r.index for r in roots] == [0, 1, 2]
    assert roots[0].label == "anh" and roots[0].available and roots[0].message == ""
    assert roots[1].label == "usb-chua-cam" and not roots[1].available
    assert "Chưa thấy thư mục ảnh số 2" in roots[1].message
    assert not roots[2].available and "đường dẫn đầy đủ" in roots[2].message
    for info in roots:
        assert_no_abs_path(repr(info), tree["tmp"], missing)


def test_root_that_is_a_file_is_not_available(tree):
    lib = ImageLibrary([tree["root"] / "a.jpg"])
    (info,) = lib.roots()
    assert not info.available and "không phải là thư mục" in info.message


def test_library_repr_hides_paths(tree):
    lib = ImageLibrary([tree["root"], tree["outside"]])
    assert repr(lib) == "ImageLibrary(2 thư mục)"
    assert len(lib) == 2
    assert_no_abs_path(repr(lib) + str(lib), tree["tmp"])


def test_from_settings_uses_image_folders(tree):
    class FakeSettings:
        image_folders = (tree["root"],)

    lib = ImageLibrary.from_settings(FakeSettings(), max_entries=10)
    assert lib.list_folder(0).total_images == 3


def test_unknown_root_index_is_rejected(tree):
    lib = ImageLibrary([tree["root"]])
    for index in (1, -1, True, "0"):
        raises_safely(lambda index=index: lib.list_folder(index), tree["tmp"])
    raises_safely(lambda: lib.read_image_bytes(ImageRef(5, "a.jpg")), tree["tmp"])


def test_missing_root_gives_friendly_error(tree):
    missing = tree["tmp"] / "o-G-chua-chay"
    lib = ImageLibrary([missing])
    exc = raises_safely(lambda: lib.list_folder(0), missing)
    assert "Google Drive" in str(exc)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "a.jpg")), missing)


def test_root_becomes_available_later(tree):
    """USB cắm sau: không cần tạo lại ImageLibrary."""
    later = tree["tmp"] / "usb"
    lib = ImageLibrary([later])
    assert not lib.roots()[0].available
    write(later / "x.jpg")
    assert lib.roots()[0].available
    assert lib.list_folder(0).total_images == 1


# ----- xem thư mục -------------------------------------------------------------------------


def test_list_folder_returns_images_subfolders_and_skips(tree):
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0)
    assert isinstance(listing, FolderListing)
    assert [e.name for e in listing.images] == ["a.jpg", "B.PNG", "c.webp"]
    assert [e.ref for e in listing.images] == [
        ImageRef(0, "a.jpg"),
        ImageRef(0, "B.PNG"),
        ImageRef(0, "c.webp"),
    ]
    assert listing.images[0].size == 4
    assert listing.images[0].modified > 0
    assert [(s.rel_path, s.name) for s in listing.subfolders] == [
        ("CT012 - Cổng inox - Hải Châu", "CT012 - Cổng inox - Hải Châu")
    ]
    assert listing.skipped == SkipCounts(hidden=1, other_files=2, empty=1)
    assert listing.total_images == 3 and listing.page == 1 and listing.page_count == 1
    assert not listing.truncated and listing.notice == ""
    assert listing.rel_dir == ""
    assert_no_abs_path(repr(listing), tree["tmp"])


def test_list_subfolder_gives_paths_relative_to_root(tree):
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0, "CT012 - Cổng inox - Hải Châu")
    assert listing.images == ()
    assert [s.rel_path for s in listing.subfolders] == [
        "CT012 - Cổng inox - Hải Châu/sau",
        "CT012 - Cổng inox - Hải Châu/truoc",
    ]
    inner = lib.list_folder(0, listing.subfolders[1].rel_path)
    assert [e.ref.rel_path for e in inner.images] == [
        "CT012 - Cổng inox - Hải Châu/truoc/IMG_0001.HEIC"
    ]


def test_list_folder_recursive_collects_whole_project(tree):
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0, "CT012 - Cổng inox - Hải Châu", recursive=True)
    assert [e.ref.rel_path for e in listing.images] == [
        "CT012 - Cổng inox - Hải Châu/sau/IMG_0002.jpeg",
        "CT012 - Cổng inox - Hải Châu/truoc/IMG_0001.HEIC",
    ]
    # Thư mục con trả về vẫn chỉ là tầng trực tiếp.
    assert len(listing.subfolders) == 2


def test_recursive_depth_limit(tmp_path):
    root = tmp_path / "anh"
    write(root / "1" / "2" / "3" / "sau.jpg")
    write(root / "1" / "tang1.jpg")
    lib = ImageLibrary([root])
    listing = lib.list_folder(0, recursive=True, max_depth=2)
    assert [e.ref.rel_path for e in listing.images] == ["1/tang1.jpg"]
    assert listing.skipped.too_deep == 1
    full = lib.list_folder(0, recursive=True)
    assert len(full.images) == 2


def test_list_folder_rejects_file_and_bad_dir(tree):
    lib = ImageLibrary([tree["root"]])
    raises_safely(lambda: lib.list_folder(0, "a.jpg"), tree["tmp"])
    raises_safely(lambda: lib.list_folder(0, "khong-co"), tree["tmp"])
    for bad in ("..", "../ngoai", "/", "C:/", str(tree["outside"]), "a/../..", None):
        raises_safely(lambda bad=bad: lib.list_folder(0, bad), tree["tmp"])


def test_too_large_files_are_skipped(tmp_path):
    root = tmp_path / "anh"
    write(root / "nho.jpg", b"x" * 10)
    write(root / "lon.jpg", b"x" * 11)
    lib = ImageLibrary([root], max_file_bytes=10)
    listing = lib.list_folder(0)
    assert [e.name for e in listing.images] == ["nho.jpg"]
    assert listing.skipped.too_large == 1


def test_sorting_is_case_insensitive(tmp_path):
    root = tmp_path / "anh"
    for name in ("b.jpg", "A.jpg", "c.jpg", "Ă.jpg"):
        write(root / name)
    names = [e.name for e in ImageLibrary([root]).list_folder(0).images]
    assert names[:3] == ["A.jpg", "b.jpg", "c.jpg"]


@posix_only
def test_odd_names_are_skipped_on_posix(tmp_path):
    root = tmp_path / "anh"
    write(root / "ok.jpg")
    for name in ("a\\b.jpg", "x?.jpg", "x:y.jpg", "dong\nmoi.jpg", "CON.jpg", "cuoi.jpg "):
        write(root / name)
    (root / "a\\thu-muc").mkdir()
    listing = ImageLibrary([root]).list_folder(0)
    assert [e.name for e in listing.images] == ["ok.jpg"]
    assert listing.subfolders == ()
    assert listing.skipped.bad_names == 7


@posix_only
def test_fifo_is_not_an_image(tmp_path):
    root = tmp_path / "anh"
    root.mkdir()
    os.mkfifo(root / "ong.jpg")
    lib = ImageLibrary([root])
    assert lib.list_folder(0).skipped.other_files == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "ong.jpg")), tmp_path)


@windows_only
def test_hidden_and_system_files_are_skipped_on_windows(tmp_path):
    import ctypes

    root = tmp_path / "anh"
    hidden = write(root / "an.jpg")
    system = write(root / "he-thong.jpg")
    write(root / "thuong.jpg")
    set_attrs = ctypes.windll.kernel32.SetFileAttributesW
    assert set_attrs(str(hidden), stat.FILE_ATTRIBUTE_HIDDEN)
    assert set_attrs(str(system), stat.FILE_ATTRIBUTE_SYSTEM)
    lib = ImageLibrary([root])
    listing = lib.list_folder(0)
    assert [e.name for e in listing.images] == ["thuong.jpg"]
    assert listing.skipped.hidden == 2
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "an.jpg")), tmp_path)


# ----- phân trang ---------------------------------------------------------------------------


@pytest.fixture
def ten_images(tmp_path):
    root = tmp_path / "anh"
    for i in range(10):
        write(root / f"anh-{i:02d}.jpg")
    return ImageLibrary([root])


def test_pagination(ten_images):
    first = ten_images.list_folder(0, page_size=3)
    assert first.page_count == 4 and first.total_images == 10
    assert [e.name for e in first.images] == ["anh-00.jpg", "anh-01.jpg", "anh-02.jpg"]
    assert first.has_next_page and not first.has_previous_page
    last = ten_images.list_folder(0, page=4, page_size=3)
    assert [e.name for e in last.images] == ["anh-09.jpg"]
    assert not last.has_next_page and last.has_previous_page


def test_page_beyond_end_is_clamped(ten_images):
    listing = ten_images.list_folder(0, page=99, page_size=3)
    assert listing.page == 4 and [e.name for e in listing.images] == ["anh-09.jpg"]


def test_empty_folder_has_one_empty_page(tmp_path):
    root = tmp_path / "anh"
    root.mkdir()
    listing = ImageLibrary([root]).list_folder(0)
    assert listing.images == () and listing.page == 1 and listing.page_count == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"page": 0},
        {"page": -1},
        {"page": "1"},
        {"page": True},
        {"page_size": 0},
        {"page_size": MAX_PAGE_SIZE + 1},
        {"page_size": 2.5},
        {"max_depth": -1},
    ],
)
def test_bad_paging_arguments(ten_images, kwargs):
    with pytest.raises(ImageFolderError):
        ten_images.list_folder(0, **kwargs)


# ----- ngân sách quét -----------------------------------------------------------------------


def test_entry_budget_stops_and_says_more(tmp_path):
    root = tmp_path / "anh"
    for i in range(20):
        write(root / f"anh-{i:02d}.jpg")
    listing = ImageLibrary([root], max_entries=5).list_folder(0)
    assert listing.truncated
    assert listing.total_images == 5
    assert "còn nữa" in listing.notice and "5 mục" in listing.notice


def test_entry_budget_counts_non_images_too(tmp_path):
    root = tmp_path / "anh"
    for i in range(20):
        write(root / f"ghi-chu-{i}.txt")
    listing = ImageLibrary([root], max_entries=5).list_folder(0)
    assert listing.truncated and listing.skipped.other_files == 5


def test_entry_budget_applies_across_subfolders(tmp_path):
    root = tmp_path / "anh"
    for d in range(5):
        for i in range(5):
            write(root / f"ct{d}" / f"{i}.jpg")
    listing = ImageLibrary([root], max_entries=12).list_folder(0, recursive=True)
    assert listing.truncated
    assert listing.total_images + len(listing.subfolders) <= 12


def test_default_budget_is_5000_entries():
    assert DEFAULT_MAX_ENTRIES == 5000


def test_time_budget_stops_and_says_more(tmp_path):
    """Đồng hồ giả: mỗi lần hỏi giờ tăng 1 giây, ngân sách 3 giây."""
    root = tmp_path / "anh"
    for i in range(20):
        write(root / f"anh-{i:02d}.jpg")
    ticks = iter(range(10_000))
    lib = ImageLibrary([root], max_seconds=3, clock=lambda: float(next(ticks)))
    listing = lib.list_folder(0)
    assert listing.truncated
    assert 0 < listing.total_images < 20
    assert "còn nữa" in listing.notice and "3 giây" in listing.notice


def test_slow_directory_iteration_is_cut_off(tmp_path, monkeypatch):
    """Ổ mạng chậm: mỗi mục tốn 1 giây (giả) thì dừng đúng hạn, không đọc hết."""
    root = tmp_path / "anh"
    for i in range(50):
        write(root / f"anh-{i:02d}.jpg")
    now = [0.0]
    real_scandir = os.scandir

    class SlowIterator:
        def __init__(self, inner):
            self.inner = inner

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.inner.close()

        def __iter__(self):
            return self

        def __next__(self):
            now[0] += 1.0
            return next(self.inner)

    monkeypatch.setattr(
        "seo_app.images.folders.os.scandir", lambda path: SlowIterator(real_scandir(path))
    )
    lib = ImageLibrary([root], max_seconds=10, clock=lambda: now[0])
    listing = lib.list_folder(0)
    assert listing.truncated and listing.total_images <= 11


def test_unreadable_subfolder_is_counted_not_fatal(tmp_path, monkeypatch):
    """Thư mục con không có quyền đọc: quét cả cây vẫn xong, đếm vào ``unreadable``. Nhận thư mục
    khóa theo định danh trên ổ (không theo tên): Windows quét theo đường dẫn, Mac/Linux quét bằng
    ``os.scandir(fd)`` (SL-T063-1: bản cũ so ``Path(path).name`` nên hỏng trên Mac/Linux)."""
    root = tmp_path / "anh"
    write(root / "ok" / "a.jpg")
    write(root / "khoa" / "b.jpg")
    locked = os.stat(root / "khoa")
    real_scandir = os.scandir

    def fake_scandir(target):
        st = os.fstat(target) if isinstance(target, int) else os.stat(target)
        if (st.st_dev, st.st_ino) == (locked.st_dev, locked.st_ino):
            raise PermissionError(13, "Access denied", str(target))
        return real_scandir(target)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", fake_scandir)
    lib = ImageLibrary([root])
    listing = lib.list_folder(0, recursive=True)
    assert [e.ref.rel_path for e in listing.images] == ["ok/a.jpg"]
    assert listing.skipped.unreadable == 1
    raises_safely(lambda: lib.list_folder(0, "khoa"), tmp_path)


# ----- đọc một ảnh --------------------------------------------------------------------------


def test_read_image_bytes_returns_exact_content(tree):
    lib = ImageLibrary([tree["root"]])
    assert lib.read_image_bytes(ImageRef(0, "a.jpg")) == b"AAAA"
    data = lib.read_image_bytes(ImageRef(0, "CT012 - Cổng inox - Hải Châu/sau/IMG_0002.jpeg"))
    assert data.startswith(b"\xff\xd8")


def test_read_listed_images_round_trip(tree):
    lib = ImageLibrary([tree["root"]])
    for entry in lib.list_folder(0, recursive=True).images:
        assert len(lib.read_image_bytes(entry.ref)) == entry.size
        assert lib.stat_image(entry.ref) == entry


def test_read_rejects_too_large_and_empty(tmp_path):
    root = tmp_path / "anh"
    write(root / "lon.jpg", b"x" * 11)
    write(root / "rong.jpg", b"")
    lib = ImageLibrary([root], max_file_bytes=10)
    assert "quá lớn" in str(raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "lon.jpg"))))
    assert "rỗng" in str(raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "rong.jpg"))))
    raises_safely(lambda: lib.stat_image(ImageRef(0, "lon.jpg")))


def test_read_rejects_file_growing_after_check(tmp_path, monkeypatch):
    """File to ra giữa lúc kiểm và lúc đọc: vẫn không đọc quá giới hạn."""
    root = tmp_path / "anh"
    path = write(root / "a.jpg", b"x" * 5)
    lib = ImageLibrary([root], max_file_bytes=10)
    real_fstat = os.fstat

    def grow_then_fstat(fd):
        path.write_bytes(b"x" * 50)
        result = real_fstat(fd)
        monkeypatch.setattr("seo_app.images.folders.os.fstat", real_fstat)
        return result

    monkeypatch.setattr("seo_app.images.folders.os.fstat", grow_then_fstat)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "a.jpg")), tmp_path)


def test_read_detects_swapped_file(tmp_path, monkeypatch):
    """File bị tráo (khác file đã kiểm) ngay trước khi mở: báo lỗi, không trả nội dung."""
    root = tmp_path / "anh"
    write(root / "a.jpg", b"AAAA")
    other = write(tmp_path / "khac.jpg", b"OTHER")
    lib = ImageLibrary([root])
    real_open = os.open

    def open_other(path, flags, *args, **kwargs):
        # Chỉ tráo chính file ảnh. Mac/Linux mở thư mục từng tầng rồi mở ``a.jpg`` trong thư mục
        # đã mở (``dir_fd``), Windows mở theo đường dẫn: cả hai đều nhận file khác.
        if os.fsdecode(path).endswith("a.jpg"):
            return real_open(other, flags)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr("seo_app.images.folders.os.open", open_other)
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "a.jpg")), tmp_path)
    assert "thay đổi" in str(exc)


def test_read_rejects_directory_named_like_image(tmp_path):
    root = tmp_path / "anh"
    (root / "thu-muc.jpg").mkdir(parents=True)
    lib = ImageLibrary([root])
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "thu-muc.jpg")), tmp_path)
    assert lib.list_folder(0).subfolders[0].name == "thu-muc.jpg"


def test_read_missing_file(tree):
    lib = ImageLibrary([tree["root"]])
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "khong-co.jpg")), tree["tmp"])
    assert "Không tìm thấy" in str(exc)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "a.jpg/x.jpg")), tree["tmp"])


@pytest.mark.parametrize("ref", [None, "a.jpg", ("0", "a.jpg"), {"root_index": 0}])
def test_read_requires_image_ref(tree, ref):
    lib = ImageLibrary([tree["root"]])
    raises_safely(lambda: lib.read_image_bytes(ref), tree["tmp"])
    raises_safely(lambda: lib.stat_image(ref), tree["tmp"])


def test_second_root_is_independent(tree):
    lib = ImageLibrary([tree["root"], tree["outside"]])
    assert lib.read_image_bytes(ImageRef(1, "bi-mat.jpg")) == b"SECRET"
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "bi-mat.jpg")), tree["tmp"])


# ----- chỉ đọc -------------------------------------------------------------------------------


def test_library_never_changes_image_folder(tree):
    before = snapshot(tree["tmp"])
    lib = ImageLibrary([tree["root"]])
    lib.roots()
    for entry in lib.list_folder(0, recursive=True).images:
        lib.read_image_bytes(entry.ref)
        lib.stat_image(entry.ref)
    for bad in ("../ngoai/bi-mat.jpg", "khong-co.jpg"):
        with pytest.raises(ImageFolderError):
            lib.read_image_bytes(ImageRef(0, bad))
    assert snapshot(tree["tmp"]) == before


def test_module_has_no_write_calls():
    """Đọc mã nguồn: không có lời gọi tạo/sửa/xóa file (bảo đảm thêm cho quyết định 3A)."""
    source = Path(sys.modules[ImageLibrary.__module__].__file__).read_text(encoding="utf-8")
    for word in (
        "write_bytes",
        "write_text",
        "mkdir",
        "unlink",
        "rmdir",
        "rename(",
        "os.replace",
        "os.remove",
        "shutil",
        "touch(",
        "O_WRONLY",
        "O_RDWR",
        "O_CREAT",
        '"w',
        '"a',
        "pickle",
        "eval(",
    ):
        assert word not in source, word


# ----- nhận diện liên kết từ kết quả lstat (chạy trên mọi hệ điều hành) ----------------------


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"st_mode": stat.S_IFLNK | 0o777}, True),  # symlink Mac/Linux
        ({"st_mode": stat.S_IFREG | 0o644}, False),
        ({"st_mode": stat.S_IFDIR | 0o755}, False),
        # Windows: junction (IO_REPARSE_TAG_MOUNT_POINT), symlink, symlink WSL
        (
            {"st_mode": stat.S_IFDIR, "st_file_attributes": 0x410, "st_reparse_tag": 0xA0000003},
            True,
        ),
        (
            {"st_mode": stat.S_IFREG, "st_file_attributes": 0x420, "st_reparse_tag": 0xA000000C},
            True,
        ),
        (
            {"st_mode": stat.S_IFREG, "st_file_attributes": 0x420, "st_reparse_tag": 0xA000001D},
            True,
        ),
        # File "chỉ trực tuyến" OneDrive (IO_REPARSE_TAG_CLOUD_*): không phải liên kết
        (
            {"st_mode": stat.S_IFREG, "st_file_attributes": 0x420, "st_reparse_tag": 0x9000001A},
            False,
        ),
        ({"st_mode": stat.S_IFREG, "st_file_attributes": 0x20, "st_reparse_tag": 0}, False),
    ],
)
def test_is_link_stat(fields, expected):
    assert _is_link_stat(SimpleNamespace(**fields)) is expected


# ----- junction Windows (chạy thật trên máy Windows) ---------------------------------------


@windows_only
def test_junction_to_outside_is_not_listed(tree):
    make_junction(tree["root"] / "loi-tat", tree["outside"])
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0)
    assert "loi-tat" not in [s.name for s in listing.subfolders]
    assert listing.skipped.links == 1
    recursive = lib.list_folder(0, recursive=True)
    assert all("bi-mat" not in e.name for e in recursive.images)


@windows_only
def test_junction_to_outside_cannot_be_opened(tree):
    make_junction(tree["root"] / "loi-tat", tree["outside"])
    lib = ImageLibrary([tree["root"]])
    ref = ImageRef(0, "loi-tat/bi-mat.jpg")
    exc = raises_safely(lambda: lib.read_image_bytes(ref), tree["tmp"])
    assert "liên kết" in str(exc)
    raises_safely(lambda: lib.stat_image(ref), tree["tmp"])
    raises_safely(lambda: lib.list_folder(0, "loi-tat"), tree["tmp"])


@windows_only
def test_resolve_check_alone_blocks_junction_outside(tree, monkeypatch):
    """Lớp chặn thứ hai: dù bỏ kiểm liên kết, ``resolve`` + ``is_relative_to`` vẫn chặn."""
    make_junction(tree["root"] / "loi-tat", tree["outside"])
    monkeypatch.setattr("seo_app.images.folders._is_link_stat", lambda st: False)
    monkeypatch.setattr(Path, "is_junction", lambda self: False)
    lib = ImageLibrary([tree["root"]])
    exc = raises_safely(
        lambda: lib.read_image_bytes(ImageRef(0, "loi-tat/bi-mat.jpg")), tree["tmp"]
    )
    assert "ngoài thư mục" in str(exc)


@windows_only
def test_junction_pointing_inside_root_is_also_refused(tree):
    """Không đi qua liên kết, kể cả liên kết trỏ vào trong gốc (giữ quy tắc đơn giản)."""
    make_junction(tree["root"] / "vong", tree["root"] / "CT012 - Cổng inox - Hải Châu")
    lib = ImageLibrary([tree["root"]])
    assert lib.list_folder(0).skipped.links == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "vong/sau/IMG_0002.jpeg")), tree["tmp"])


@windows_only
def test_junction_loop_does_not_hang(tree):
    make_junction(tree["root"] / "vong-lap", tree["root"])
    listing = ImageLibrary([tree["root"]]).list_folder(0, recursive=True)
    assert not listing.truncated and listing.skipped.links == 1


@windows_only
def test_root_configured_as_junction_is_allowed(tree):
    """Gốc do chủ dự án khai báo là junction: dùng thư mục thật mà nó trỏ tới."""
    link_root = tree["tmp"] / "goc-la-junction"
    make_junction(link_root, tree["root"])
    lib = ImageLibrary([link_root])
    assert lib.roots()[0].available
    assert lib.read_image_bytes(ImageRef(0, "a.jpg")) == b"AAAA"


# ----- symlink (Mac/Linux; Windows nếu được phép) -----------------------------------------


def test_symlinked_dir_to_outside_is_refused(tree):
    make_symlink(tree["root"] / "lien-ket", tree["outside"])
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0, recursive=True)
    assert "lien-ket" not in [s.name for s in listing.subfolders]
    assert listing.skipped.links == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "lien-ket/bi-mat.jpg")), tree["tmp"])
    raises_safely(lambda: lib.list_folder(0, "lien-ket"), tree["tmp"])


def test_symlinked_file_to_outside_is_refused(tree):
    make_symlink(tree["root"] / "tat.jpg", tree["outside"] / "bi-mat.jpg")
    lib = ImageLibrary([tree["root"]])
    listing = lib.list_folder(0)
    assert "tat.jpg" not in [e.name for e in listing.images]
    assert listing.skipped.links == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "tat.jpg")), tree["tmp"])
    raises_safely(lambda: lib.stat_image(ImageRef(0, "tat.jpg")), tree["tmp"])


def test_symlinked_file_inside_root_is_refused(tree):
    make_symlink(tree["root"] / "ban-sao.jpg", tree["root"] / "a.jpg")
    lib = ImageLibrary([tree["root"]])
    assert lib.list_folder(0).skipped.links == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "ban-sao.jpg")), tree["tmp"])


def test_resolve_check_alone_blocks_symlink_outside(tree, monkeypatch):
    make_symlink(tree["root"] / "tat.jpg", tree["outside"] / "bi-mat.jpg")
    monkeypatch.setattr("seo_app.images.folders._is_link_stat", lambda st: False)
    lib = ImageLibrary([tree["root"]])
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "tat.jpg")), tree["tmp"])
    assert "ngoài thư mục" in str(exc)


# ----- lượt 2 · L1: thư mục bị tráo giữa lúc kiểm và lúc quét (Windows) ----------------------


def _swap_to_junction(directory: Path, target: Path, park: Path) -> None:
    os.rename(directory, park)
    make_junction(directory, target)


@pytest.fixture
def swap_tree(tmp_path):
    root = tmp_path / "anh"
    write(root / "album" / "a.jpg", b"AAAA")
    write(root / "khac" / "b.jpg", b"BB")
    write(tmp_path / "ngoai" / "bi-mat.jpg", b"SECRET")
    return root, tmp_path / "ngoai", tmp_path


@windows_only
def test_held_directory_and_parents_cannot_be_renamed_during_scan(swap_tree, monkeypatch):
    """Trong lúc quét, Windows không cho đổi tên thư mục đang quét lẫn thư mục cha."""
    root, _outside, tmp = swap_tree
    real_scandir = os.scandir
    attempts = []

    def try_renames(path):
        for src in (root / "album", root):
            try:
                os.rename(src, tmp / f"doi-{src.name}")
            except OSError as exc:
                attempts.append(exc.winerror)
            else:
                attempts.append("đổi được")
        return real_scandir(path)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", try_renames)
    listing = ImageLibrary([root]).list_folder(0, "album")
    assert attempts == [32, 5]  # đang dùng / bị từ chối
    assert [e.name for e in listing.images] == ["a.jpg"]


@windows_only
def test_fallback_without_hold_discards_swapped_directory(swap_tree, monkeypatch):
    """Ổ không giữ được thư mục: kiểm trước/sau khi quét vẫn bắt được thư mục bị tráo."""
    import contextlib

    root, outside, tmp = swap_tree

    @contextlib.contextmanager
    def no_hold(path):
        yield None

    monkeypatch.setattr("seo_app.images.folders._win_hold_dir", no_hold)
    real_scandir = os.scandir

    def swap_then_scandir(path):
        if Path(path).name == "album":
            monkeypatch.setattr("seo_app.images.folders.os.scandir", real_scandir)
            _swap_to_junction(root / "album", outside, tmp / "album-cu")
        return real_scandir(path)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", swap_then_scandir)
    lib = ImageLibrary([root])
    exc = raises_safely(lambda: lib.list_folder(0, "album"), tmp)
    assert "thay đổi" in str(exc) or "liên kết" in str(exc)


@windows_only
def test_fallback_recursive_keeps_other_folders(swap_tree, monkeypatch):
    """Quét cả cây: thư mục bị tráo bị bỏ hết kết quả, thư mục khác vẫn còn."""
    import contextlib

    root, outside, tmp = swap_tree

    @contextlib.contextmanager
    def no_hold(path):
        yield None

    monkeypatch.setattr("seo_app.images.folders._win_hold_dir", no_hold)
    real_scandir = os.scandir

    class SwapAfter:
        def __init__(self, inner):
            self.inner = inner

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.inner.close()
            _swap_to_junction(root / "album", outside, tmp / "album-cu")

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.inner)

    def scandir(path):
        if Path(path).name == "album":
            monkeypatch.setattr("seo_app.images.folders.os.scandir", real_scandir)
            return SwapAfter(real_scandir(path))
        return real_scandir(path)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", scandir)
    listing = ImageLibrary([root]).list_folder(0, recursive=True)
    names = [e.ref.rel_path for e in listing.images]
    assert names == ["khac/b.jpg"]  # a.jpg của album (quét trước khi tráo) cũng bị bỏ
    assert listing.skipped.links == 1


@windows_only
def test_held_directory_with_other_final_path_is_refused(swap_tree, monkeypatch):
    root, _outside, tmp = swap_tree
    monkeypatch.setattr("seo_app.images.folders._win_final_path", lambda fd: str(tmp / "ngoai"))
    raises_safely(lambda: ImageLibrary([root]).list_folder(0, "album"), tmp)


@windows_only
def test_junction_set_in_place_during_scan_is_refused(swap_tree, monkeypatch):
    """Thư mục đang giữ bị đặt junction tại chỗ trong lúc quét: bỏ kết quả."""
    root, _outside, tmp = swap_tree
    answers = iter([False, True])
    monkeypatch.setattr("seo_app.images.folders._win_handle_is_link", lambda fd: next(answers))
    raises_safely(lambda: ImageLibrary([root]).list_folder(0, "album"), tmp)


@windows_only
def test_scan_of_deep_tree_is_fast(tmp_path):
    """Kiểm đường đi mỗi thư mục là O(1) lệnh hệ thống trên Windows, cây sâu không chậm."""
    import time

    root = tmp_path / "anh"
    deep = root
    for _ in range(100):
        deep = deep / "d"
    write(deep / "day.jpg")
    started = time.perf_counter()
    listing = ImageLibrary([root]).list_folder(0, recursive=True, max_depth=1000)
    assert listing.total_images == 1 and not listing.truncated
    assert time.perf_counter() - started < 5


# ----- tên trên ổ (T-076, LC-T055-1, LC-T076-1) ----------------------------------------------
#
# "CongAI" là thư mục ảnh AI nhờ tách chữ hoa, "congai" thì không (T-052): ``ImageRef`` trả ra phải
# theo tên trên ổ, không theo chữ đã gõ, dù ổ Windows/Mac tìm ra cùng một thư mục. Tên lấy từ thư
# mục cha, không từ ``resolve``: ổ Google Drive for Desktop của Windows trả lại chữ đã gõ khi
# ``resolve`` (LC-T076-1).

PROJECT = "CT012 - Cổng inox - Tân Phú"
ON_DISK = f"{PROJECT}/CongAI/Cong.PNG"
TYPED = "ct012 - cổng INOX - tân phú/congai/cong.png"


def case_insensitive(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir()
    try:
        return (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


def typed_resolve(self: Path, strict: bool = False) -> Path:
    """Như ``resolve`` của ổ Google Drive for Desktop trên Windows (đo trên máy chủ dự án,
    LC-T076-1): trả lại đúng chữ đã gõ; danh sách thư mục vẫn cho tên trên ổ."""
    if strict:
        os.lstat(self)  # không có thì FileNotFoundError, như resolve thật
    return Path(os.path.abspath(self))


@pytest.fixture(params=["he-dieu-hanh", "xem-thu-muc-cha", "resolve-tra-chu-da-go"])
def name_source(request, monkeypatch) -> str:
    """Chạy mọi cách lấy tên trên ổ trên mọi máy: cách của hệ điều hành đang chạy (Windows: hỏi thư
    mục cha từng mục), cách của Mac/Linux (đọc tên trong thư mục cha từng tầng), và cách của hệ
    điều hành đang chạy trên ổ trả lại chữ đã gõ khi ``resolve`` (như Google Drive for Desktop)."""
    if request.param == "xem-thu-muc-cha":
        monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    elif request.param == "resolve-tra-chu-da-go":
        monkeypatch.setattr(Path, "resolve", typed_resolve)
    return request.param


@pytest.fixture
def camel(tmp_path: Path) -> Path:
    root = tmp_path / "anh"
    write(root / ON_DISK, b"\x89PNG anh AI")
    write(root / PROJECT / "truoc" / "IMG_0001.jpg")
    return root


def test_stat_image_returns_disk_names(camel, name_source):
    """``ref`` gõ khác hoa thường vẫn tìm ra ảnh (ổ không phân biệt hoa thường), nhưng
    ``ImageEntry.ref`` và ``name`` theo tên trên ổ, cả tên thư mục lẫn tên file."""
    lib = ImageLibrary([camel])
    exact = lib.stat_image(ImageRef(0, ON_DISK))
    assert exact.ref == ImageRef(0, ON_DISK) and exact.name == "Cong.PNG"
    if not case_insensitive(camel):
        raises_safely(lambda: lib.stat_image(ImageRef(0, TYPED)), camel)
        return
    entry = lib.stat_image(ImageRef(0, TYPED))
    assert entry.ref == ImageRef(0, ON_DISK) and entry.name == "Cong.PNG"
    assert (entry.size, entry.modified) == (exact.size, exact.modified)
    assert lib.read_image_bytes(entry.ref) == b"\x89PNG anh AI"


def test_list_folder_returns_disk_names(camel, name_source):
    """``rel_dir`` gõ khác hoa thường: ``rel_dir``, ``SubFolder.rel_path`` và ``ImageRef`` trả ra
    theo tên trên ổ (để "mở thư mục chứa ảnh" theo đường dẫn ghi trong nháp không ra ảnh thật)."""
    lib = ImageLibrary([camel])
    typed_dir = TYPED.rsplit("/", 2)[0]
    if not case_insensitive(camel):
        raises_safely(lambda: lib.list_folder(0, typed_dir), camel)
        return
    listing = lib.list_folder(0, typed_dir, recursive=True)
    assert listing.rel_dir == PROJECT
    assert [sub.rel_path for sub in listing.subfolders] == [f"{PROJECT}/CongAI", f"{PROJECT}/truoc"]
    assert [entry.ref.rel_path for entry in listing.images] == [
        ON_DISK,
        f"{PROJECT}/truoc/IMG_0001.jpg",
    ]
    inner = lib.list_folder(0, TYPED.rsplit("/", 1)[0])
    assert inner.rel_dir == f"{PROJECT}/CongAI"
    assert [entry.ref for entry in inner.images] == [ImageRef(0, ON_DISK)]


NFC_AREA = "Tân Phú"
NFD_AREA = unicodedata.normalize("NFD", NFC_AREA)


@pytest.mark.parametrize(
    ("names", "typed", "expected"),
    [
        (["CongAI", "congai"], "congai", "congai"),  # ổ phân biệt hoa thường: trùng hẳn thắng
        (["congai", "CongAI"], "CongAI", "CongAI"),
        (["Ảnh khác", "CongAI"], "congai", "CongAI"),  # ổ không phân biệt: tên trên ổ
        ([NFD_AREA], "tân phú", NFD_AREA),  # Mac lưu tên dạng NFD
        ([NFC_AREA, NFD_AREA], NFD_AREA, NFD_AREA),  # NTFS, ext4: hai thư mục khác nhau
    ],
)
def test_match_disk_name(names, typed, expected):
    assert _match_disk_name(iter(names), typed, lambda: False) == expected


@pytest.mark.parametrize(
    ("names", "message"),
    [([], "Không tìm thấy"), (["Ảnh khác"], "Không tìm thấy"), (["CongAI", "CONGAI"], "tên khác")],
    ids=["rong", "khong-co", "hai-ten-cung-khoa"],
)
def test_match_disk_name_refuses_when_unsure(names, message):
    exc = raises_safely(lambda: _match_disk_name(iter(names), "congai", lambda: False))
    assert message in str(exc)


def test_match_disk_name_stops_at_exact_name_and_on_time():
    def names():
        yield "CongAI"
        yield "congai"
        raise AssertionError("không đọc tiếp sau tên trùng hẳn")

    assert _match_disk_name(names(), "congai", lambda: False) == "congai"
    exc = raises_safely(lambda: _match_disk_name(iter(["a", "congai"]), "congai", lambda: True))
    assert "chậm" in str(exc)


def test_disk_names_are_not_limited_by_entry_budget(tmp_path, name_source):
    """LC-T055-3 (T-076): xem tên trong thư mục cha không bị ngân sách số mục của lần quét: ảnh
    trong thư mục con của gốc rất nhiều mục (ở đây ngân sách 3 mục) vẫn kiểm được, tên trên ổ."""
    root = tmp_path / "anh"
    for number in range(30):
        write(root / f"{number:04d}.jpg")
    write(root / "Zz Cong trinh" / "a.jpg")
    lib = ImageLibrary([root], max_entries=3)
    assert lib.list_folder(0).truncated
    assert lib.stat_image(ImageRef(0, "Zz Cong trinh/a.jpg")).ref.rel_path == "Zz Cong trinh/a.jpg"
    if case_insensitive(root):
        found = lib.stat_image(ImageRef(0, "zz cong trinh/a.jpg"))
        assert found.ref.rel_path == "Zz Cong trinh/a.jpg"


def test_disk_name_lookup_has_time_limit(tmp_path, monkeypatch):
    """Cách của Mac/Linux có giới hạn thời gian (ổ mạng, Drive chậm): quá giờ thì báo lỗi."""
    monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    root = tmp_path / "anh"
    for number in range(20):
        write(root / f"{number:04d}.jpg")
    write(root / "Zz" / "a.jpg")
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'zz' không trỏ tới 'Zz'")
    ticks = iter(range(10_000))
    lib = ImageLibrary([root], max_seconds=3, clock=lambda: float(next(ticks)))
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, "zz/a.jpg")), tmp_path)
    assert "chậm" in str(exc)


def test_disk_name_lookup_lists_only_folders_on_the_path(camel, monkeypatch):
    """Cách của Mac/Linux chỉ đọc tên của đúng các thư mục trên đường đi (mỗi tầng một lần), bên
    trong gốc, và không mở file ảnh nào."""
    monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    listed: list[object] = []
    opened: list[str] = []
    real_scandir, real_open = os.scandir, os.open

    def spy_scandir(target):
        listed.append(target)
        return real_scandir(target)

    def spy_open(path, *args, **kwargs):
        opened.append(os.fsdecode(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", spy_scandir)
    monkeypatch.setattr("seo_app.images.folders.os.open", spy_open)
    ImageLibrary([camel]).stat_image(ImageRef(0, ON_DISK))
    assert len(listed) == 3  # gốc, thư mục công trình, CongAI
    root = camel.resolve()
    for target in listed:
        assert isinstance(target, int) or Path(target).is_relative_to(root)
    assert not [path for path in opened if path.lower().endswith((".png", ".jpg"))]


@pytest.mark.parametrize(
    "call",
    [
        lambda lib: lib.stat_image(ImageRef(0, "album/a.jpg")),
        lambda lib: lib.list_folder(0, "album"),
    ],
    ids=["stat_image", "list_folder"],
)
def test_entry_swapped_during_name_lookup_is_refused(tmp_path, monkeypatch, name_source, call):
    """LC-T055-2 (T-076): ngay sau khi kiểm đường đi, thư mục bị đổi tên đi và một thư mục khác
    được đổi tên thành tên đó: báo lỗi, không trả tên của mục này kèm số liệu của mục kia."""
    root = tmp_path / "anh"
    write(root / "album" / "a.jpg", b"AAAA")
    write(root / "khac" / "a.jpg", b"KHAC, dai hon")
    original = ImageLibrary._resolve_inside

    def check_then_swap(self, root_path, parts):
        result = original(self, root_path, parts)
        if parts[:1] == ("album",) and not (root / "album-cu").exists():
            os.rename(root / "album", root / "album-cu")
            os.rename(root / "khac", root / "album")
        return result

    monkeypatch.setattr(ImageLibrary, "_resolve_inside", check_then_swap)
    exc = raises_safely(lambda: call(ImageLibrary([root])), tmp_path)
    assert "thay đổi" in str(exc)


@windows_only
def test_windows_asks_the_parent_folder_one_entry_per_level(camel, monkeypatch):
    """LC-T076-1: Windows hỏi thư mục cha đúng một mục mỗi tầng (``FindFirstFileW``), tầng sau đi
    theo tên trên ổ của tầng trước; không đọc cả thư mục (``os.scandir``), không lấy tên từ
    ``resolve``. Ổ trả lại chữ đã gõ khi ``resolve`` vẫn ra tên trên ổ."""
    if not case_insensitive(camel):
        pytest.skip("thư mục tạm bật phân biệt hoa thường")
    asked: list[str] = []
    real_lookup = folders._win_listed_name

    def spy_lookup(path):
        asked.append(Path(path).relative_to(camel).as_posix())
        return real_lookup(path)

    def no_scandir(target):
        raise AssertionError("không đọc cả thư mục để lấy tên")

    monkeypatch.setattr(folders, "_win_listed_name", spy_lookup)
    monkeypatch.setattr("seo_app.images.folders.os.scandir", no_scandir)
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    entry = ImageLibrary([camel]).stat_image(ImageRef(0, TYPED))
    assert entry.ref == ImageRef(0, ON_DISK) and entry.name == "Cong.PNG"
    assert asked == [
        "ct012 - cổng INOX - tân phú",
        f"{PROJECT}/congai",
        f"{PROJECT}/CongAI/cong.png",
    ]


@windows_only
@pytest.mark.parametrize("source", ["hoi-tung-muc", "doc-thu-muc-cha"])
def test_short_8_3_name_refused_when_resolve_keeps_typed_text(tmp_path, monkeypatch, source):
    """Ổ trả lại chữ đã gõ khi ``resolve`` thì phép chặn tên ngắn 8.3 của ``_resolve_inside`` (so
    với tên ``resolve`` trả) không bắt được; bước lấy tên trên ổ vẫn từ chối, vì thư mục cha chỉ
    liệt kê tên dài: một file không có hai ``ImageRef``."""
    import ctypes

    def short_path(path: Path) -> str:
        buffer = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, 1024)
        return buffer.value

    root = tmp_path / "anh"
    target = write(root / "Thu muc dai ten lam nhe" / "Anh rat dai ten.jpg")
    short_file, short_root = short_path(target), short_path(root)
    if "~" not in Path(short_file).relative_to(short_root).as_posix():
        pytest.skip("ổ này tắt tên ngắn 8.3")
    rel = Path(short_file).relative_to(short_root).as_posix()
    if source == "doc-thu-muc-cha":
        monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    lib = ImageLibrary([root])
    assert lib.stat_image(ImageRef(0, "Thu muc dai ten lam nhe/Anh rat dai ten.jpg"))
    raises_safely(lambda: lib.stat_image(ImageRef(0, rel)), tmp_path)
    raises_safely(lambda: lib.list_folder(0, rel.split("/")[0]), tmp_path)


@windows_only
@pytest.mark.parametrize(
    ("error", "message"),
    [(2, "Không tìm thấy"), (3, "Không tìm thấy"), (5, "Không đọc được")],
    ids=["khong-co-file", "khong-co-duong-dan", "khong-co-quyen"],
)
def test_windows_lookup_failure_is_a_plain_message(camel, monkeypatch, error, message):
    """Ổ không trả lời được khi hỏi tên (mục vừa mất, không có quyền đọc thư mục cha): báo lỗi gọn,
    không có đường dẫn máy, không quay về chữ đã gõ."""
    import ctypes

    def failing(path, data):
        ctypes.set_last_error(error)
        return ctypes.c_void_p(-1).value

    monkeypatch.setattr(folders._kernel32(), "FindFirstFileW", failing)
    exc = raises_safely(lambda: ImageLibrary([camel]).stat_image(ImageRef(0, ON_DISK)), camel)
    assert message in str(exc)


# ----- T-079: đọc, ``stat`` một ảnh qua chính mục đã mở (SL-T063-2, -3, -5; LC-T076-3) --------
#
# ``read_image_bytes``, ``stat_image`` không đi theo chuỗi đường dẫn đã kiểm: Mac/Linux mở thư mục
# cha từng tầng từ gốc (``O_NOFOLLOW``) rồi mở/``stat`` file trong chính thư mục đã mở; Windows hỏi
# đường dẫn thật của chính handle vừa mở. Ca tráo "luôn thắng" của Soi Lỗi, Lá Chắn T-063 nằm ở
# ``tests/test_images_folders_t063.py``.


def _read_swapped(lib: ImageLibrary) -> bytes:
    return lib.read_image_bytes(ImageRef(0, "x/bi-mat.jpg"))


def _stat_swapped(lib: ImageLibrary):
    return lib.stat_image(ImageRef(0, "x/bi-mat.jpg"))


SWAP_CALLS = pytest.mark.parametrize(
    "call", [_read_swapped, _stat_swapped], ids=["read_image_bytes", "stat_image"]
)


@pytest.fixture
def x_tree(tmp_path: Path) -> tuple[Path, Path]:
    """``anh/x/bi-mat.jpg`` (ảnh mồi, 3 byte) và ``ngoai/bi-mat.jpg`` (ngoài gốc, khác cỡ)."""
    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", b"moi")
    write(tmp_path / "ngoai" / "bi-mat.jpg", b"SECRET ngoai goc, dai hon")
    return root, tmp_path / "ngoai"


@pytest.mark.parametrize(
    ("error", "message", "is_link"),
    [
        (FileNotFoundError(2, "x"), "Không tìm thấy", False),
        (PermissionError(13, "x"), "Không đọc được", False),
        (NotADirectoryError(20, "x"), "vừa bị thay đổi", True),
        (OSError(errno.ELOOP, "x"), "vừa bị thay đổi", True),
    ],
    ids=["khong-co", "khong-co-quyen", "enotdir", "eloop"],
)
def test_open_error_message(error, message, is_link):
    """Lỗi khi mở từng tầng (Mac/Linux) thành câu báo. Tầng vừa được kiểm là thư mục, nên ENOTDIR
    (Linux trả cho symlink khi mở bằng ``O_DIRECTORY | O_NOFOLLOW``, SL-T063-5) và ELOOP là "vừa bị
    thay đổi", quét thì đếm vào ``links``; không báo "không có quyền"."""
    exc = folders._open_error(error)
    assert message in str(exc)
    assert isinstance(exc, folders._LinkError) is is_link


def test_stat_image_gives_file_id_of_the_checked_file(tree):
    """``stat_image`` trả định danh của file (``file_id``); kết quả quét không có. Hai
    ``ImageEntry`` so như cũ (không tính ``file_id``), ``repr`` không hiện."""
    lib = ImageLibrary([tree["root"]])
    entry = lib.stat_image(ImageRef(0, "a.jpg"))
    st = os.stat(tree["root"] / "a.jpg")
    assert entry.file_id == (st.st_dev, st.st_ino)
    (listed,) = [e for e in lib.list_folder(0).images if e.name == "a.jpg"]
    assert listed.file_id is None and listed == entry
    assert "file_id" not in repr(entry)


@windows_only
@SWAP_CALLS
def test_windows_unknown_final_path_is_refused(x_tree, monkeypatch, call):
    """Không hỏi được đường dẫn thật của handle vừa mở thì không đọc, không trả số liệu (an toàn
    trước; ổ nào ``resolve(strict=True)`` được thì trả lời được câu hỏi này)."""
    root, _outside = x_tree
    monkeypatch.setattr(folders, "_win_final_path", lambda fd: None)
    exc = raises_safely(lambda: call(ImageLibrary([root])), root.parent)
    assert "thay đổi" in str(exc)


@windows_only
def test_windows_stat_handle_opened_through_swapped_folder_is_refused(x_tree, monkeypatch):
    """SL-T063-3 (Windows): kẻ tráo thắng cả lúc ``lstat`` mục cuối lẫn lúc mở handle hỏi thuộc
    tính (``x`` là junction ra ngoài đúng hai lúc đó), nên so định danh không phân biệt được. Đường
    dẫn thật của handle (ngoài gốc) phải chặn: không trả cỡ file ngoài gốc."""
    root, outside = x_tree
    park = root.parent / "cat-tam"
    real_lstat, real_win_open = os.lstat, folders._win_open

    def swapped(call, path, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) != "bi-mat.jpg":
            return call(path, *args, **kwargs)
        os.rename(root / "x", park)
        make_junction(root / "x", outside)
        try:
            return call(path, *args, **kwargs)
        finally:
            os.rmdir(root / "x")
            os.rename(park, root / "x")

    def lstat(path, *args, **kwargs):
        return swapped(real_lstat, path, *args, **kwargs)

    def win_open(path, access):
        return swapped(real_win_open, path, access)

    lib = ImageLibrary([root])
    assert _stat_swapped(lib).size == 3  # chưa bị tấn công
    monkeypatch.setattr("seo_app.images.folders.os.lstat", lstat)
    monkeypatch.setattr(folders, "_win_open", win_open)
    exc = raises_safely(lambda: _stat_swapped(lib), root.parent)
    assert "thay đổi" in str(exc)


@windows_only
def test_windows_stat_image_asks_attributes_only(tree, monkeypatch):
    """``stat_image`` trên Windows mở chính file ảnh chỉ để hỏi thuộc tính (như ``os.lstat``), không
    có quyền đọc nội dung: Drive "chỉ trực tuyến" không bị tải về."""
    opened: list[tuple[str, int]] = []
    real_win_open = folders._win_open

    def spy(path, access):
        opened.append((Path(path).name, access))
        return real_win_open(path, access)

    monkeypatch.setattr(folders, "_win_open", spy)
    assert ImageLibrary([tree["root"]]).stat_image(ImageRef(0, "a.jpg")).size == 4
    assert opened == [("a.jpg", folders._FILE_READ_ATTRIBUTES)]


@posix_only
def test_posix_image_is_opened_inside_the_opened_folder(tree, monkeypatch):
    """Mac/Linux: ảnh mở bằng tên trong thư mục cha đã mở (``dir_fd``), không theo đường dẫn;
    ``stat_image`` không mở file ảnh."""
    calls: list[tuple[str, object]] = []
    real_open = os.open

    def spy(path, flags, *args, **kwargs):
        calls.append((os.fsdecode(path), kwargs.get("dir_fd")))
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr("seo_app.images.folders.os.open", spy)
    lib = ImageLibrary([tree["root"]])
    rel = "CT012 - Cổng inox - Hải Châu/sau/IMG_0002.jpeg"
    assert lib.stat_image(ImageRef(0, rel)).size > 0
    assert not [path for path, _dir_fd in calls if path.endswith(".jpeg")]
    calls.clear()
    assert lib.read_image_bytes(ImageRef(0, rel)).startswith(b"\xff\xd8")
    image_opens = [(path, dir_fd) for path, dir_fd in calls if path.endswith(".jpeg")]
    assert [path for path, _dir_fd in image_opens] == ["IMG_0002.jpeg"]
    assert isinstance(image_opens[0][1], int)


@posix_only
@SWAP_CALLS
def test_posix_folder_swapped_before_opening_levels_is_refused(x_tree, monkeypatch, call):
    """Ngay sau khi kiểm đường đi, ``x`` bị tráo thành symlink ra ngoài trước khi app mở từng tầng:
    ``openat(O_DIRECTORY | O_NOFOLLOW)`` từ chối, câu báo "vừa bị thay đổi" (SL-T063-5), không
    lọt nội dung hay số liệu ngoài gốc."""
    root, outside = x_tree
    real_open_dir = folders._posix_open_dir

    def swap_then_open(root_path, parts):
        if parts == ("x",) and not (root / "x").is_symlink():
            os.rename(root / "x", root.parent / "x-cu")
            (root / "x").symlink_to(outside, target_is_directory=True)
        return real_open_dir(root_path, parts)

    monkeypatch.setattr(folders, "_posix_open_dir", swap_then_open)
    exc = raises_safely(lambda: call(ImageLibrary([root])), root.parent)
    assert "thay đổi" in str(exc)


@posix_only
@SWAP_CALLS
def test_posix_file_swapped_to_symlink_after_folder_is_opened(x_tree, monkeypatch, call):
    """Thư mục cha đã mở xong thì file ảnh bị tráo thành symlink ra ngoài: mở, ``stat`` file trong
    thư mục đã mở đều không đi theo symlink (``O_NOFOLLOW``, ``follow_symlinks=False``)."""
    root, outside = x_tree
    image = root / "x" / "bi-mat.jpg"
    real_open_dir = folders._posix_open_dir

    def open_then_swap(root_path, parts):
        fd = real_open_dir(root_path, parts)
        if parts == ("x",) and not image.is_symlink():
            os.rename(image, root.parent / "cu.jpg")
            image.symlink_to(outside / "bi-mat.jpg")
        return fd

    monkeypatch.setattr(folders, "_posix_open_dir", open_then_swap)
    exc = raises_safely(lambda: call(ImageLibrary([root])), root.parent)
    assert "SECRET" not in str(exc)

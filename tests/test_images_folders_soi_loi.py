"""Soi Lỗi kiểm thử T-048 (đọc thư mục ảnh an toàn): các đòn tấn công bổ sung.

Bổ sung cho ``tests/test_images_folders.py`` (Thợ Máy). Mọi file thử nằm trong ``tmp_path``.
Test ``xfail(strict=True)`` là lỗi đã ghi trong ``docs/team/reports/T-048-soi-loi.md``: khi
sửa xong, test chuyển sang "XPASS" và báo hỏng, lúc đó bỏ dấu ``xfail``.
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from pathlib import Path

import pytest

from seo_app.images.folders import (
    MAX_IMAGE_BYTES,
    MAX_PAGE_SIZE,
    FolderListing,
    ImageEntry,
    ImageFolderError,
    ImageLibrary,
    ImageRef,
    RootInfo,
    SkipCounts,
    SubFolder,
)

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="junction chỉ có trên Windows")


# ----- tiện ích ----------------------------------------------------------------------------


def write(path: Path, data: bytes = b"\xff\xd8\xff fake jpeg") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def make_junction(link: Path, target: Path) -> None:
    import _winapi

    _winapi.CreateJunction(str(target), str(link))
    assert link.is_junction()


def abs_forms(*paths: Path) -> set[str]:
    forms: set[str] = set()
    for path in paths:
        for p in (path, path.resolve()):
            forms |= {str(p), p.as_posix()}
            if IS_WINDOWS:
                forms.add("\\\\?\\" + str(p))
    return forms


def assert_no_abs_path(text: str, *paths: Path) -> None:
    for form in abs_forms(*paths):
        assert form not in text, f"lộ đường dẫn tuyệt đối: {form!r}"


def raises_safely(func, *paths: Path) -> ImageFolderError:
    with pytest.raises(ImageFolderError) as info:
        func()
    exc = info.value
    assert str(exc)
    assert_no_abs_path(str(exc), *paths)
    assert_no_abs_path(repr(exc), *paths)
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__
    return exc


def listed_names(listing: FolderListing) -> list[str]:
    return [entry.name for entry in listing.images]


def swap_dir_for_junction(directory: Path, target: Path, park: Path) -> None:
    """Đổi thư mục thật thành junction trỏ ra ngoài (người có quyền ghi vào thư mục ảnh)."""
    os.rename(directory, park)
    make_junction(directory, target)


@pytest.fixture
def tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "anh"
    outside = tmp_path / "ngoai"
    write(root / "album" / "a.jpg", b"AAAA")
    write(outside / "bi-mat.jpg", b"SECRET")
    write(outside / "a.jpg", b"SECRET-A")
    return {"root": root, "outside": outside, "tmp": tmp_path}


# ----- 1. Junction lồng nhau, mount point, đường dẫn dài, ổ ánh xạ ------------------------


@windows_only
def test_nested_junction_chain_is_refused(tree):
    """j1 (junction trong gốc) → thư mục thật trong gốc chứa j2 → ngoài: đều bị chặn."""
    root, outside = tree["root"], tree["outside"]
    (root / "that").mkdir()
    make_junction(root / "that" / "j2", outside)
    make_junction(root / "j1", root / "that")
    lib = ImageLibrary([root])
    listing = lib.list_folder(0, recursive=True)
    assert "bi-mat.jpg" not in listed_names(listing)
    assert listing.skipped.links == 2
    for rel in ("j1/j2/bi-mat.jpg", "that/j2/bi-mat.jpg", "j1/j2/a.jpg"):
        raises_safely(lambda rel=rel: lib.read_image_bytes(ImageRef(0, rel)), tree["tmp"])
    raises_safely(lambda: lib.list_folder(0, "that/j2"), tree["tmp"])


def _volume_guid_path(drive: str) -> str | None:
    buf = ctypes.create_unicode_buffer(100)
    ok = ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW(drive, buf, 100)
    return buf.value if ok else None


@windows_only
def test_volume_mount_point_style_junction_is_refused(tree):
    """Junction trỏ thẳng vào ổ đĩa (``\\\\?\\Volume{...}\\``), cùng loại với mount point."""
    root = tree["root"]
    drive = Path(root.resolve().anchor)
    volume = _volume_guid_path(str(drive))
    if not volume:
        pytest.skip("không lấy được tên volume GUID của ổ chứa tmp_path")
    link = root / "o-dia"
    make_junction(link, Path(volume))
    try:
        lib = ImageLibrary([root])
        listing = lib.list_folder(0, recursive=True)
        assert listing.skipped.links == 1
        assert all(not n.startswith("o-dia") for n in (s.rel_path for s in listing.subfolders))
        assert all(not e.ref.rel_path.startswith("o-dia/") for e in listing.images)
        raises_safely(lambda: lib.list_folder(0, "o-dia"), tree["tmp"])
        raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "o-dia/x.jpg")), tree["tmp"])
    finally:
        os.rmdir(link)  # chỉ gỡ junction, không đụng vào ổ đĩa


@windows_only
def test_path_longer_than_260_chars_works_or_fails_safely(tmp_path):
    root = tmp_path / "anh"
    parts: list[str] = []
    deep = root
    while len(str(deep)) < 420:
        parts.append("thu-muc-dai-" + "d" * 40)
        deep = deep / parts[-1]
    try:
        write(deep / "x.jpg", b"LONG")
    except OSError:
        pytest.skip("Windows này chưa bật đường dẫn dài (LongPathsEnabled)")
    assert len(str(deep / "x.jpg")) > 260
    lib = ImageLibrary([root])
    rel = "/".join([*parts, "x.jpg"])
    assert lib.read_image_bytes(ImageRef(0, rel)) == b"LONG"
    listing = lib.list_folder(0, recursive=True, max_depth=50)
    assert [e.ref.rel_path for e in listing.images] == [rel]
    assert lib.list_folder(0, "/".join(parts)).total_images == 1
    # Gốc nằm sẵn ở đường dẫn dài cũng dùng được.
    deep_lib = ImageLibrary([deep])
    assert deep_lib.roots()[0].available
    assert deep_lib.read_image_bytes(ImageRef(0, "x.jpg")) == b"LONG"
    raises_safely(lambda: deep_lib.read_image_bytes(ImageRef(0, "khong.jpg")), tmp_path)


@windows_only
def test_extended_length_prefixed_root(tmp_path):
    """IMAGE_FOLDERS ghi dạng ``\\\\?\\C:\\...``: dùng được, câu lỗi không lộ đường dẫn."""
    root = tmp_path / "anh"
    write(root / "a.jpg", b"AAAA")
    write(tmp_path / "ngoai" / "a.jpg", b"SECRET")
    make_junction(root / "j", tmp_path / "ngoai")
    lib = ImageLibrary(["\\\\?\\" + str(root.resolve())])
    assert lib.roots()[0].available
    assert lib.read_image_bytes(ImageRef(0, "a.jpg")) == b"AAAA"
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "j/a.jpg")), tmp_path)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "khong.jpg")), tmp_path)


def _admin_share(path: Path) -> str | None:
    resolved = path.resolve()
    if not resolved.drive.endswith(":"):
        return None
    unc = "\\\\localhost\\" + str(resolved).replace(":", "$", 1)
    try:
        return unc if os.path.isdir(unc) else None
    except OSError:
        return None


@windows_only
def test_unc_network_root_blocks_junction_and_hides_paths(tree):
    """Gốc là đường dẫn mạng UNC (giống ổ mạng ánh xạ, resolve ra UNC)."""
    root = tree["root"]
    unc = _admin_share(root)
    if unc is None:
        pytest.skip("máy này không mở được ổ chia sẻ \\\\localhost\\C$ (cần quyền quản trị)")
    make_junction(root / "j", tree["outside"])
    lib = ImageLibrary([unc])
    assert lib.roots()[0].available
    assert lib.read_image_bytes(ImageRef(0, "album/a.jpg")) == b"AAAA"
    listing = lib.list_folder(0, recursive=True)
    assert listing.skipped.links == 1
    assert "bi-mat.jpg" not in listed_names(listing)
    for func in (
        lambda: lib.read_image_bytes(ImageRef(0, "j/bi-mat.jpg")),
        lambda: lib.list_folder(0, "j"),
        lambda: lib.read_image_bytes(ImageRef(0, "khong.jpg")),
    ):
        exc = raises_safely(func, tree["tmp"])
        assert "localhost" not in str(exc) and "C$" not in str(exc)


# ----- 2. Ký tự Unicode đặc biệt trong tên -------------------------------------------------


def _make_undecodable_name(folder: Path) -> str:
    """Tạo file có tên không mã hóa được UTF-8 (surrogate lẻ); trả tên Python thấy khi quét."""
    folder.mkdir(parents=True, exist_ok=True)
    try:
        if IS_WINDOWS:
            name = "x\ud800y.jpg"  # NTFS nhận UTF-16 lẻ cặp
            (folder / name).write_bytes(b"S")
            return name
        raw = os.path.join(os.fsencode(folder), b"x\xffy.jpg")  # byte sai UTF-8
        with open(raw, "wb") as handle:
            handle.write(b"S")
        return os.fsdecode(b"x\xffy.jpg")
    except (OSError, UnicodeError):
        pytest.skip("hệ thống file này không cho tạo tên sai UTF-8 (ví dụ APFS)")


def test_listing_never_returns_names_that_cannot_be_utf8_encoded(tmp_path):
    root = tmp_path / "anh"
    write(root / "a.jpg")
    _make_undecodable_name(root)
    listing = ImageLibrary([root]).list_folder(0)
    for entry in listing.images:
        entry.name.encode("utf-8")
        entry.ref.rel_path.encode("utf-8")
    assert listed_names(listing) == ["a.jpg"]
    assert listing.skipped.bad_names == 1


@pytest.mark.parametrize("rel", ["x\ud800y.jpg", "a\udcff/b.jpg"])
def test_image_ref_rejects_lone_surrogates(rel):
    with pytest.raises(ImageFolderError):
        ImageRef(0, rel)


def test_lone_surrogate_name_is_still_safe_to_read_or_rejected(tmp_path):
    """Dù tên lạ lọt qua, đọc vẫn không ra ngoài gốc và không lỗi lạ."""
    root = tmp_path / "anh"
    name = _make_undecodable_name(root)
    lib = ImageLibrary([root])
    try:
        data = lib.read_image_bytes(ImageRef(0, name))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert data == b"S"


@pytest.mark.parametrize(
    "name",
    [
        "anh\u202egpj.exe",  # RLO: hiện thành "anhexe.jpg" nhưng đuôi thật là .exe
        "anh\u202egnp.txt",
        "a\u200b.jpg\u200b",  # ký tự rộng 0 sau đuôi
        "anh.jpg\u202e",
    ],
)
def test_bidi_and_zero_width_cannot_disguise_extension(tmp_path, name):
    root = tmp_path / "anh"
    write(root / "that.jpg")
    write(root / name)
    listing = ImageLibrary([root]).list_folder(0)
    assert listed_names(listing) == ["that.jpg"]
    # Lượt 2 (Thợ Máy): tên có ký tự điều khiển hướng chữ bị loại sớm hơn, đếm vào bad_names.
    assert listing.skipped.other_files + listing.skipped.bad_names == 1
    with pytest.raises(ImageFolderError):
        ImageRef(0, name)


def test_format_characters_in_names_stay_inside_root(tmp_path):
    """Ký tự định dạng (Cf) và ký tự giống dấu chấm/gạch chéo không giúp thoát khỏi gốc."""
    root = tmp_path / "anh"
    write(root / "a.jpg")
    write(tmp_path / "ngoai" / "bi-mat.jpg", b"SECRET")
    lib = ImageLibrary([root])
    for rel in (
        "\uff0e\uff0e/ngoai/bi-mat.jpg",  # dấu chấm toàn khổ
        "\u2024\u2024/ngoai/bi-mat.jpg",  # one dot leader
        "\u202e../ngoai/bi-mat.jpg",
        "\u200b../ngoai/bi-mat.jpg",
        "x\u2215..\u2215ngoai\u2215bi-mat.jpg",  # division slash
        "x\uff0f..\uff0fngoai\uff0fbi-mat.jpg",  # gạch chéo toàn khổ
        "x\u29f5..\u29f5bi-mat.jpg",  # reverse solidus operator
    ):
        try:
            ref = ImageRef(0, rel)
        except ImageFolderError:
            continue
        raises_safely(lambda ref=ref: lib.read_image_bytes(ref), tmp_path)


# ----- 3. Tráo thư mục/file giữa lúc kiểm và lúc dùng (TOCTOU) -----------------------------


@windows_only
def test_read_detects_parent_dir_swapped_to_junction_before_open(tree, monkeypatch):
    """Thư mục ở giữa bị thay bằng junction ra ngoài ngay trước ``os.open``: phải báo lỗi."""
    root, outside = tree["root"], tree["outside"]
    lib = ImageLibrary([root])
    real_open = os.open

    def swap_then_open(path, flags, *args):
        monkeypatch.setattr("seo_app.images.folders.os.open", real_open)
        swap_dir_for_junction(root / "album", outside, tree["tmp"] / "album-cu")
        return real_open(path, flags, *args)

    monkeypatch.setattr("seo_app.images.folders.os.open", swap_then_open)
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "album/a.jpg")), tree["tmp"])
    assert "SECRET" not in str(exc)


@windows_only
def test_read_detects_file_replaced_by_directory_junction(tree, monkeypatch):
    """File ảnh bị đổi thành junction (tên ``a.jpg``) trỏ ra thư mục ngoài: không đọc được."""
    root = tree["root"]
    lib = ImageLibrary([root])
    real_open = os.open

    def swap_then_open(path, flags, *args):
        monkeypatch.setattr("seo_app.images.folders.os.open", real_open)
        os.rename(root / "album" / "a.jpg", tree["tmp"] / "a-cu.jpg")
        make_junction(root / "album" / "a.jpg", tree["outside"])
        return real_open(path, flags, *args)

    monkeypatch.setattr("seo_app.images.folders.os.open", swap_then_open)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "album/a.jpg")), tree["tmp"])


@windows_only
def test_list_folder_dir_swapped_to_junction_after_check(tree, monkeypatch):
    root, outside = tree["root"], tree["outside"]
    lib = ImageLibrary([root])
    real_scandir = os.scandir

    def swap_then_scandir(path):
        monkeypatch.setattr("seo_app.images.folders.os.scandir", real_scandir)
        swap_dir_for_junction(root / "album", outside, tree["tmp"] / "album-cu")
        return real_scandir(path)

    monkeypatch.setattr("seo_app.images.folders.os.scandir", swap_then_scandir)
    try:
        listing = lib.list_folder(0, "album")
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tree["tmp"])
        return
    assert "bi-mat.jpg" not in listed_names(listing)


class _SwapWhenDone:
    """Bọc iterator của ``os.scandir``: đọc hết thì chạy ``action`` (tráo thư mục)."""

    def __init__(self, inner, action):
        self.inner = inner
        self.action = action

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.inner.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.inner)
        except StopIteration:
            action, self.action = self.action, None
            if action:
                action()
            raise


@windows_only
def test_recursive_scan_subdir_swapped_to_junction_before_its_turn(tree, monkeypatch):
    root, outside = tree["root"], tree["outside"]
    lib = ImageLibrary([root])
    real_scandir = os.scandir
    calls = []

    def scandir(path):
        calls.append(path)
        inner = real_scandir(path)
        if len(calls) == 1:  # lần đầu: thư mục gốc, chỉ có "album/"
            return _SwapWhenDone(
                inner,
                lambda: swap_dir_for_junction(root / "album", outside, tree["tmp"] / "album-cu"),
            )
        return inner

    monkeypatch.setattr("seo_app.images.folders.os.scandir", scandir)
    listing = lib.list_folder(0, recursive=True)
    assert "bi-mat.jpg" not in listed_names(listing)


# ----- 4. Hard link (ghi nhận giới hạn) -----------------------------------------------------


def test_hard_link_limitation_is_documented(tmp_path):
    """Hard link trỏ tới file ngoài gốc thì KHÔNG phát hiện được (giới hạn đã ghi nhận).

    Test này chỉ ghi lại hành vi hiện tại để ai đổi cách xử lý (ví dụ từ chối ``st_nlink > 1``)
    thì biết cập nhật báo cáo. Muốn tạo hard link phải có quyền ghi vào thư mục ảnh.
    """
    root = tmp_path / "anh"
    root.mkdir()
    secret = write(tmp_path / "ngoai" / "bi-mat.jpg", b"SECRET")
    try:
        os.link(secret, root / "lien-ket.jpg")
    except OSError:
        pytest.skip("hệ thống file không hỗ trợ hard link")
    lib = ImageLibrary([root])
    assert lib.read_image_bytes(ImageRef(0, "lien-ket.jpg")) == b"SECRET"
    assert os.lstat(root / "lien-ket.jpg").st_nlink == 2


# ----- 5. Ngân sách và tham số lạ ---------------------------------------------------------


def test_real_folder_with_more_than_5000_entries_stops_quickly(tmp_path):
    root = tmp_path / "anh"
    root.mkdir()
    for i in range(5005):
        (root / f"anh-{i:05d}.jpg").write_bytes(b"x")
    lib = ImageLibrary([root])
    started = time.monotonic()
    listing = lib.list_folder(0, page=10**9, page_size=MAX_PAGE_SIZE)
    elapsed = time.monotonic() - started
    assert listing.truncated
    assert listing.total_images == 5000
    assert listing.page == listing.page_count == 25
    assert len(listing.images) == MAX_PAGE_SIZE
    assert "5.000" in listing.notice and "còn nữa" in listing.notice
    assert elapsed < 10  # dưới ngân sách thời gian mặc định


def test_entry_budget_notice_keeps_sentence_comma(tmp_path):
    root = tmp_path / "anh"
    for i in range(8):
        write(root / f"{i}.jpg")
    notice = ImageLibrary([root], max_entries=5).list_folder(0).notice
    assert "mục đầu, còn nữa" in notice


def test_folder_with_exactly_budget_entries_is_not_truncated(tmp_path):
    root = tmp_path / "anh"
    for i in range(3):
        write(root / f"{i}.jpg")
    listing = ImageLibrary([root], max_entries=3).list_folder(0)
    assert listing.total_images == 3
    assert not listing.truncated
    assert listing.notice == ""


def test_folder_with_one_less_than_budget_is_not_truncated(tmp_path):
    root = tmp_path / "anh"
    for i in range(3):
        write(root / f"{i}.jpg")
    listing = ImageLibrary([root], max_entries=4).list_folder(0)
    assert listing.total_images == 3 and not listing.truncated


def test_very_deep_tree_does_not_recurse_or_hang(tmp_path):
    root = tmp_path / "anh"
    deep = root
    for _ in range(120):
        deep = deep / "d"
    write(deep / "day.jpg")
    write(root / "d" / "nong.jpg")
    lib = ImageLibrary([root])
    shallow = lib.list_folder(0, recursive=True)  # mặc định 8 tầng
    assert [e.name for e in shallow.images] == ["nong.jpg"]
    assert shallow.skipped.too_deep == 1
    full = lib.list_folder(0, recursive=True, max_depth=10**9)
    assert sorted(e.name for e in full.images) == ["day.jpg", "nong.jpg"]
    assert not full.truncated
    assert lib.list_folder(0, "/".join(["d"] * 120)).total_images == 1


def test_rel_path_over_limit_in_deep_tree_is_skipped_not_crash(tmp_path):
    root = tmp_path / "anh"
    deep = root
    for _ in range(110):  # 110 * 10 ký tự > 1024
        deep = deep / "thu-muc-xx"
    try:
        write(deep / "xa.jpg")
    except OSError:
        pytest.skip("hệ điều hành không cho đường dẫn dài như vậy")
    listing = ImageLibrary([root]).list_folder(0, recursive=True, max_depth=500)
    assert listing.total_images == 0
    assert listing.skipped.bad_names == 1


def _sized_file(path: Path, size: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(b"\xff\xd8")
        handle.truncate(size)
    return path


def test_file_exactly_40mb_is_accepted_and_one_byte_more_is_not(tmp_path):
    root = tmp_path / "anh"
    _sized_file(root / "vua.jpg", MAX_IMAGE_BYTES)
    _sized_file(root / "qua.jpg", MAX_IMAGE_BYTES + 1)
    lib = ImageLibrary([root])
    listing = lib.list_folder(0)
    assert listed_names(listing) == ["vua.jpg"]
    assert listing.skipped.too_large == 1
    assert lib.stat_image(ImageRef(0, "vua.jpg")).size == MAX_IMAGE_BYTES
    assert len(lib.read_image_bytes(ImageRef(0, "vua.jpg"))) == MAX_IMAGE_BYTES
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "qua.jpg")), tmp_path)
    assert "40,0 MB" in str(exc)
    raises_safely(lambda: lib.stat_image(ImageRef(0, "qua.jpg")), tmp_path)


@pytest.fixture
def small_lib(tmp_path):
    root = tmp_path / "anh"
    for i in range(5):
        write(root / f"{i}.jpg")
    write(root / "thu-muc" / "x.jpg")
    return ImageLibrary([root])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"page": False},
        {"page": 1.0},
        {"page": None},
        {"page": -(10**30)},
        {"page_size": -1},
        {"page_size": True},
        {"page_size": 10**30},
        {"page_size": None},
        {"page_size": "48"},
        {"max_depth": True},
        {"max_depth": 1.5},
        {"max_depth": None},
    ],
)
def test_more_bad_paging_arguments(small_lib, tmp_path, kwargs):
    raises_safely(lambda: small_lib.list_folder(0, **kwargs), tmp_path)


def test_huge_page_is_clamped(small_lib):
    listing = small_lib.list_folder(0, page=10**30, page_size=2)
    assert listing.page == listing.page_count == 3
    assert listed_names(listing) == ["4.jpg"]
    assert not listing.has_next_page and listing.has_previous_page


@pytest.mark.parametrize("index", [-1, 1, 10**30, True, False, 0.0, "0", None, [0]])
def test_bad_root_index_everywhere(small_lib, tmp_path, index):
    raises_safely(lambda: small_lib.list_folder(index), tmp_path)
    if type(index) is int and index >= 0:  # ImageRef nhận, thư viện từ chối
        ref = ImageRef(index, "0.jpg")
        raises_safely(lambda: small_lib.read_image_bytes(ref), tmp_path)
        raises_safely(lambda: small_lib.stat_image(ref), tmp_path)
    else:
        with pytest.raises(ImageFolderError):
            ImageRef(index, "0.jpg")


@pytest.mark.parametrize(
    "rel_dir",
    [
        "thu-muc/../thu-muc",
        "./thu-muc",
        "thu-muc/.",
        "thu-muc//",
        "thu-muc/",
        "/thu-muc",
        "C:thu-muc",
        "C:",
        "\\\\server\\share",
        "//server/share",
        "\\\\?\\C:\\",
        "\\\\.\\PhysicalDrive0",
        "//./PhysicalDrive0",
        "CON",
        "nul",
        "thu-muc.",
        "thu-muc ",
        "thu-muc:stream",
        "thu-muc\\x",
        "CON/x",
        "nul.txt",
        "~",
        "%USERPROFILE%",
        "$HOME",
        "\x00",
    ],
)
def test_list_folder_rejects_odd_rel_dir(small_lib, tmp_path, rel_dir):
    if rel_dir in ("~", "%USERPROFILE%", "$HOME"):
        # Tên hợp lệ, không được khai triển thành thư mục nhà: chỉ là "không tìm thấy".
        exc = raises_safely(lambda: small_lib.list_folder(0, rel_dir), tmp_path)
        assert "Không tìm thấy" in str(exc)
        return
    raises_safely(lambda: small_lib.list_folder(0, rel_dir), tmp_path)


def test_rel_dir_happy_path_and_case_variant(small_lib):
    """Đối chứng cho test trên: tên thường dùng được (Windows không phân biệt hoa thường)."""
    assert listed_names(small_lib.list_folder(0, "thu-muc")) == ["x.jpg"]
    if IS_WINDOWS:
        assert listed_names(small_lib.list_folder(0, "THU-MUC")) == ["x.jpg"]


# ----- 6. repr/str không lộ đường dẫn tuyệt đối ---------------------------------------------


def test_repr_and_str_of_every_result_object_hide_absolute_paths(tmp_path):
    root = tmp_path / "anh"
    write(root / "thu-muc" / "a.jpg", b"AAAA")
    write(root / "b.jpg", b"BB")
    lib = ImageLibrary([root, tmp_path / "khong-co", root / "b.jpg", "tuong-doi"])
    listing = lib.list_folder(0, recursive=True)
    entry = lib.stat_image(ImageRef(0, "thu-muc/a.jpg"))
    objects: list[object] = [
        lib,
        listing,
        entry,
        entry.ref,
        listing.skipped,
        *listing.images,
        *listing.subfolders,
        *lib.roots(),
    ]
    assert {type(o) for o in objects} >= {
        ImageLibrary,
        FolderListing,
        ImageEntry,
        ImageRef,
        SkipCounts,
        SubFolder,
        RootInfo,
    }
    for obj in objects:
        assert_no_abs_path(repr(obj), tmp_path)
        assert_no_abs_path(str(obj), tmp_path)
    for index in (1, 2, 3):
        raises_safely(lambda index=index: lib.list_folder(index), tmp_path)
        assert_no_abs_path(lib.roots()[index].message, tmp_path)


def test_error_messages_hide_paths_for_every_failure_kind(tmp_path, monkeypatch):
    root = tmp_path / "anh"
    write(root / "a.jpg", b"AAAA")
    (root / "thu-muc.jpg").mkdir()
    write(root / "rong.jpg", b"")
    lib = ImageLibrary([root])
    for func in (
        lambda: lib.read_image_bytes(ImageRef(0, "khong.jpg")),
        lambda: lib.read_image_bytes(ImageRef(0, "thu-muc.jpg")),
        lambda: lib.read_image_bytes(ImageRef(0, "rong.jpg")),
        lambda: lib.list_folder(0, "a.jpg"),
        lambda: lib.list_folder(0, "khong"),
    ):
        raises_safely(func, tmp_path)

    def denied(*args, **kwargs):
        raise PermissionError(13, "Access is denied", str(root / "a.jpg"))

    monkeypatch.setattr("seo_app.images.folders.os.open", denied)
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "a.jpg")), tmp_path)
    monkeypatch.setattr("seo_app.images.folders.os.scandir", denied)
    raises_safely(lambda: lib.list_folder(0), tmp_path)
    monkeypatch.setattr("seo_app.images.folders.os.lstat", denied)
    raises_safely(lambda: lib.stat_image(ImageRef(0, "a.jpg")), tmp_path)


# ----- 7. Thư mục ẩn, tên 8.3 (Windows) -----------------------------------------------------


def _set_hidden(path: Path) -> None:
    FILE_ATTRIBUTE_HIDDEN = 0x2
    assert ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_HIDDEN)


def _short_name(path: Path) -> str | None:
    buf = ctypes.create_unicode_buffer(1024)
    if not ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, 1024):
        return None
    short = Path(buf.value).name
    return short if short != path.name else None


@windows_only
def test_hidden_directory_cannot_be_reached_by_crafted_ref(tmp_path):
    root = tmp_path / "anh"
    write(root / "an" / "q.jpg", b"HIDDEN")
    _set_hidden(root / "an")
    lib = ImageLibrary([root])
    assert lib.list_folder(0).subfolders == ()  # quét: bị bỏ
    with pytest.raises(ImageFolderError):
        lib.read_image_bytes(ImageRef(0, "an/q.jpg"))


@windows_only
def test_short_8dot3_alias_cannot_reach_dot_directory(tmp_path):
    root = tmp_path / "anh"
    write(root / ".bi-mat" / "p.jpg", b"HIDDEN")
    short = _short_name(root / ".bi-mat")
    if short is None:
        pytest.skip("ổ chứa tmp_path không tạo tên ngắn 8.3")
    lib = ImageLibrary([root])
    with pytest.raises(ImageFolderError):
        lib.read_image_bytes(ImageRef(0, f"{short}/p.jpg"))


def test_python_version_supports_is_junction():
    """Code dùng ``Path.is_junction``/``DirEntry.is_junction`` (Python 3.12+)."""
    assert sys.version_info >= (3, 12)

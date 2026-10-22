"""Test thêm của Soi Lỗi T-063: đọc thư mục ảnh (``seo_app/images/folders.py``) trên Mac/Linux.

Phiếu T-063 chạy bộ test T-048 trên Linux lần đầu (cả đội trước đó chỉ có Windows). File này thêm
các ca chỉ có trên Mac/Linux: quét bằng ``os.scandir(fd)``, symlink thật, quyền POSIX, tên sai
UTF-8, ổ phân biệt hoa thường, thư mục bị tráo thành symlink giữa lúc kiểm và lúc đọc.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T063-x (xem
``docs/team/reports/T-063-soi-loi.md``). Mọi test dùng thư mục tạm, ảnh giả, không gọi mạng.
"""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import pytest

from seo_app.images import folders
from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef
from seo_app.storage.drafts import SOURCE_REAL, DraftImage, check_chosen_image

IS_WINDOWS = os.name == "nt"
IS_ROOT = getattr(os, "geteuid", lambda: -1)() == 0
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="symlink, quyền POSIX: thử trên Mac/Linux")
SECRET = b"\xff\xd8 SECRET-NGOAI-GOC"
DECOY = b"\xff\xd8 moi"


def write(path: Path, data: bytes = b"\xff\xd8\xff fake jpeg") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


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
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__
    return exc


def listed(listing) -> list[str]:
    return [e.ref.rel_path for e in listing.images] + [s.rel_path for s in listing.subfolders]


def case_sensitive(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir(parents=True)
    try:
        return not (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


# ----- SL-T063-1: test T-048 giả lỗi quyền chỉ đúng với Windows ---------------------------------


def test_unreadable_subfolder_is_counted_when_scandir_gets_fd(tmp_path, monkeypatch):
    """Bản chạy được trên mọi máy của ``test_unreadable_subfolder_is_counted_not_fatal``.

    Test gốc (``tests/test_images_folders.py``) giả ``os.scandir`` bằng ``Path(path).name``: đúng
    trên Windows (quét theo tên) nhưng trên Mac/Linux app quét bằng ``os.scandir(fd)`` nên test gốc
    hỏng vì ``Path(int)`` (SL-T063-1, lỗi của test, không phải của app). Ở đây nhận thư mục bị khóa
    theo định danh trên ổ, nên chạy được cả hai cách quét.
    """
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


@pytest.mark.skipif(
    IS_WINDOWS or IS_ROOT, reason="cần quyền POSIX thật và người dùng thường (root đọc được hết)"
)
def test_real_posix_permissions_are_counted_not_fatal(tmp_path):
    """Thư mục khóa quyền thật (chạy bằng người dùng thường): quét không hỏng, câu lỗi sạch.

    ``000``, ``300`` (không có quyền đọc danh sách): không mở được thư mục. ``600`` (đọc được danh
    sách nhưng không vào được): mở được, nhưng ``stat`` từng mục lỗi. ``500``: đọc bình thường.
    """
    root = tmp_path / "anh"
    write(root / "ok" / "a.jpg")
    modes = {"khoa000": 0o000, "khoa300": 0o300, "khoa600": 0o600, "khoa500": 0o500}
    for name in modes:
        write(root / name / "b.jpg")
    try:
        for name, mode in modes.items():
            os.chmod(root / name, mode)
        lib = ImageLibrary([root])
        listing = lib.list_folder(0, recursive=True)
        assert [e.ref.rel_path for e in listing.images] == ["khoa500/b.jpg", "ok/a.jpg"]
        assert listing.skipped.unreadable == 3
        assert sorted(s.name for s in listing.subfolders) == [*sorted(modes), "ok"]
        raises_safely(lambda: lib.list_folder(0, "khoa000"), tmp_path)
        raises_safely(lambda: lib.list_folder(0, "khoa300"), tmp_path)
        raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "khoa000/b.jpg")), tmp_path)
        raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "khoa600/b.jpg")), tmp_path)
    finally:
        for name in modes:
            os.chmod(root / name, 0o700)


# ----- Mac/Linux: quét bằng fd, symlink thật (các ca này qua) --------------------------------


@posix_only
def test_folder_swapped_to_symlink_after_check_is_not_scanned(tmp_path, monkeypatch):
    """Ngay sau khi kiểm đường đi, thư mục bị đổi thành symlink ra ngoài gốc: ``openat`` với
    ``O_DIRECTORY | O_NOFOLLOW`` từ chối, không liệt kê tên ngoài gốc. Bản Mac/Linux của các test
    tráo thư mục chỉ chạy trên Windows (``tests/test_images_folders.py``, ``swap_tree``)."""
    root = tmp_path / "anh"
    write(root / "x" / "a.jpg")
    outside = write(tmp_path / "ngoai" / "chi-ngoai.jpg", SECRET).parent
    original = ImageLibrary._resolve_inside

    def check_then_swap(self, root_path, parts):
        result = original(self, root_path, parts)
        if parts == ("x",) and not (root / "x").is_symlink():
            os.rename(root / "x", tmp_path / "x-cu")
            (root / "x").symlink_to(outside, target_is_directory=True)
        return result

    monkeypatch.setattr(ImageLibrary, "_resolve_inside", check_then_swap)
    exc = raises_safely(lambda: ImageLibrary([root]).list_folder(0, "x"), tmp_path)
    assert "chi-ngoai" not in str(exc)


def _swap_x_before_open(monkeypatch, root: Path, outside: Path, park: Path) -> None:
    """Thư mục ``x`` bị tráo thành symlink ra ``outside`` ngay trước khi app mở nó (``openat``)."""
    real_open_dir = folders._posix_open_dir

    def swap_then_open(root_path, parts):
        if parts == ("x",) and not (root / "x").is_symlink():
            os.rename(root / "x", park)
            (root / "x").symlink_to(outside, target_is_directory=True)
        return real_open_dir(root_path, parts)

    monkeypatch.setattr(folders, "_posix_open_dir", swap_then_open)


@posix_only
def test_subfolder_swapped_during_recursive_scan_is_skipped(tmp_path, monkeypatch):
    """Quét cả cây: thư mục con bị tráo thành symlink ngay trước khi mở thì bị bỏ, không lọt tên
    ngoài gốc, các thư mục khác vẫn quét được. (Đếm vào mục nào: xem SL-T063-5.)"""
    root = tmp_path / "anh"
    write(root / "khac" / "b.jpg")
    write(root / "x" / "a.jpg")
    outside = write(tmp_path / "ngoai" / "chi-ngoai.jpg", SECRET).parent
    _swap_x_before_open(monkeypatch, root, outside, tmp_path / "x-cu")
    listing = ImageLibrary([root]).list_folder(0, recursive=True)
    assert not any("chi-ngoai" in name for name in listed(listing))
    assert [e.ref.rel_path for e in listing.images] == ["khac/b.jpg"]
    assert listing.skipped.links + listing.skipped.unreadable == 1


@posix_only
@pytest.mark.xfail(
    sys.platform.startswith("linux"),
    strict=True,
    reason="SL-T063-5: Linux trả ENOTDIR (không phải ELOOP) cho openat(O_DIRECTORY | O_NOFOLLOW) "
    "trên symlink, nên thư mục bị tráo thành symlink bị báo 'không có quyền / ổ bị ngắt' và đếm "
    "vào unreadable",
)
def test_sl_t063_5_swapped_folder_is_reported_as_link_not_unreadable(tmp_path, monkeypatch):
    """Mong đợi (như chú thích ``_scan_by_fd``: "ELOOP: một tầng là symlink"): thư mục bị tráo
    thành symlink đếm vào ``links``; xem thẳng thư mục đó thì báo "vừa bị thay đổi" hay "liên kết
    tắt", không báo "không có quyền hoặc ổ đĩa vừa bị ngắt". Chưa kiểm trên Mac (có thể trả ELOOP;
    test này không đánh xfail trên Mac nên sẽ cho biết)."""
    root = tmp_path / "anh"
    write(root / "khac" / "b.jpg")
    write(root / "x" / "a.jpg")
    outside = write(tmp_path / "ngoai" / "chi-ngoai.jpg", SECRET).parent
    _swap_x_before_open(monkeypatch, root, outside, tmp_path / "x-cu")
    listing = ImageLibrary([root]).list_folder(0, recursive=True)
    assert (listing.skipped.links, listing.skipped.unreadable) == (1, 0)
    (root / "x").unlink()
    os.rename(tmp_path / "x-cu", root / "x")
    exc = raises_safely(lambda: ImageLibrary([root]).list_folder(0, "x"), tmp_path)
    assert "không có quyền" not in str(exc)


@posix_only
def test_root_configured_as_symlink_is_allowed_but_links_inside_are_not(tmp_path):
    """Bản Mac/Linux của ``test_root_configured_as_junction_is_allowed``: gốc khai báo là symlink
    (thiết kế T-048 cho phép), nhãn là tên đã khai báo; symlink bên trong vẫn bị chặn."""
    real_root = write(tmp_path / "anh" / "a.jpg", b"AAAA").parent
    outside = write(tmp_path / "ngoai" / "bi-mat.jpg", SECRET).parent
    link_root = tmp_path / "anh-lien-ket"
    link_root.symlink_to(real_root, target_is_directory=True)
    (real_root / "ra-ngoai").symlink_to(outside, target_is_directory=True)
    lib = ImageLibrary([link_root])
    (info,) = lib.roots()
    assert info.available and info.label == "anh-lien-ket"
    assert lib.read_image_bytes(ImageRef(0, "a.jpg")) == b"AAAA"
    assert lib.list_folder(0, recursive=True).skipped.links == 1
    raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "ra-ngoai/bi-mat.jpg")), tmp_path)


@posix_only
def test_folder_with_invalid_utf8_name_is_not_entered(tmp_path):
    """Thư mục tên sai UTF-8 (đĩa ext4, USB do máy Linux ghi): không đi vào, đếm ``bad_names``;
    mọi tên trả về ghi được ra UTF-8."""
    root = tmp_path / "anh"
    write(root / "ok.jpg")
    bad_dir = os.path.join(os.fsencode(root), b"thu-muc-\xc3\x28")
    try:
        os.mkdir(bad_dir)
        with open(os.path.join(bad_dir, b"ben-trong.jpg"), "wb") as handle:
            handle.write(b"\xff\xd8 ben trong")
        with open(os.path.join(os.fsencode(root), b"anh-\xff\xfe.jpg"), "wb") as handle:
            handle.write(b"\xff\xd8 ten hong")
    except OSError:
        pytest.skip("hệ thống file này không cho tạo tên sai UTF-8 (ví dụ APFS)")
    listing = ImageLibrary([root]).list_folder(0, recursive=True)
    assert listed(listing) == ["ok.jpg"]
    assert listing.skipped.bad_names == 2
    for name in listed(listing):
        name.encode("utf-8")


@posix_only
def test_unix_socket_named_like_image_is_not_an_image(tmp_path):
    root = tmp_path / "anh"
    root.mkdir()
    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.bind(str(root / "o-cam.jpg"))
        lib = ImageLibrary([root])
        assert lib.list_folder(0).skipped.other_files == 1
        raises_safely(lambda: lib.read_image_bytes(ImageRef(0, "o-cam.jpg")), tmp_path)
    finally:
        sock.close()


# ----- SL-T063-2, SL-T063-3: thư mục bị tráo thành symlink giữa lúc kiểm và lúc đọc ------------


@pytest.fixture
def swap_world(tmp_path, monkeypatch):
    """``anh/x/bi-mat.jpg`` (ảnh mồi) và ``ngoai/bi-mat.jpg`` (file ngoài gốc, cùng tên, khác cỡ).

    Mô phỏng một chương trình khác trên máy liên tục tráo thư mục ``x`` với một symlink ra
    ``ngoai`` (đo thật trên Linux: lọt nội dung hàng trăm lần trong 10 giây, xem báo cáo T-063).
    Ở đây "chương trình" luôn thắng: mỗi lần app ``lstat`` hay ``open`` một đường dẫn tận cùng là
    ``bi-mat.jpg``, ``x`` đang là symlink; mọi lời gọi khác thấy ``x`` là thư mục thật.
    """
    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    outside = write(tmp_path / "ngoai" / "bi-mat.jpg", SECRET).parent
    park = tmp_path / "cat-tam"
    real_lstat, real_open = os.lstat, os.open

    def basename(path) -> str:
        try:
            return os.path.basename(os.fsdecode(path))
        except TypeError:
            return ""

    def while_swapped(call, path, *args, **kwargs):
        os.rename(root / "x", park)
        os.symlink(outside, root / "x", target_is_directory=True)
        try:
            return call(path, *args, **kwargs)
        finally:
            os.unlink(root / "x")
            os.rename(park, root / "x")

    def fake_lstat(path, *args, **kwargs):
        if basename(path) == "bi-mat.jpg":
            return while_swapped(real_lstat, path, *args, **kwargs)
        return real_lstat(path, *args, **kwargs)

    def fake_open(path, *args, **kwargs):
        if basename(path) == "bi-mat.jpg":
            return while_swapped(real_open, path, *args, **kwargs)
        return real_open(path, *args, **kwargs)

    def attack() -> None:
        monkeypatch.setattr("seo_app.images.folders.os.lstat", fake_lstat)
        monkeypatch.setattr("seo_app.images.folders.os.open", fake_open)

    return root, attack


@posix_only
@pytest.mark.xfail(
    strict=True,
    reason="SL-T063-2: thư mục bị tráo thành symlink hai lần (lúc lstat mục cuối và lúc open) "
    "thì read_image_bytes đọc được nội dung file ngoài gốc",
)
def test_sl_t063_2_folder_swapped_twice_cannot_read_outside_content(swap_world, tmp_path):
    """Đường đi: ``_resolve_inside`` lấy ``lstat`` của mục cuối qua ``x`` lúc ``x`` là symlink
    (ra file ngoài gốc), ``resolve`` lúc ``x`` là thư mục thật (vẫn trong gốc), rồi ``os.open``
    lúc ``x`` lại là symlink (``O_NOFOLLOW`` chỉ chặn tầng cuối). File mở được là file ngoài gốc,
    đúng định danh với ``lstat`` đã lấy, nên phép so ``(st_dev, st_ino)`` không bắt được.
    Mong đợi: báo lỗi gọn hoặc ra ảnh mồi, không bao giờ ra nội dung file ngoài gốc (F1)."""
    root, attack = swap_world
    lib = ImageLibrary([root])
    assert lib.read_image_bytes(ImageRef(0, "x/bi-mat.jpg")) == DECOY  # chưa bị tấn công
    attack()
    try:
        data = lib.read_image_bytes(ImageRef(0, "x/bi-mat.jpg"))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert data != SECRET, "đọc được nội dung file ngoài thư mục ảnh"


@posix_only
@pytest.mark.xfail(
    strict=True,
    reason="SL-T063-3: thư mục bị tráo thành symlink lúc lstat mục cuối thì stat_image trả cỡ, "
    "giờ sửa của file ngoài gốc",
)
def test_sl_t063_3_folder_swapped_during_stat_gives_no_outside_size(swap_world, tmp_path):
    """``stat_image`` không mở file nhưng trả cỡ, giờ sửa lấy từ ``lstat`` đi qua ``x`` lúc ``x`` là
    symlink. Mong đợi: báo lỗi gọn hoặc trả số liệu của ảnh mồi, không của file ngoài gốc."""
    root, attack = swap_world
    lib = ImageLibrary([root])
    assert lib.stat_image(ImageRef(0, "x/bi-mat.jpg")).size == len(DECOY)
    attack()
    try:
        entry = lib.stat_image(ImageRef(0, "x/bi-mat.jpg"))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert entry.size != len(SECRET), "trả cỡ của file ngoài thư mục ảnh"


# ----- SL-T063-4: ổ phân biệt hoa thường, nháp đổi sang ảnh khác qua kết quả quét --------------


@pytest.mark.parametrize(
    ("files", "rel_path"),
    [
        (
            {"CongAI/cong.png": b"\x89PNG anh AI", "congai/cong.png": b"\x89PNG anh that"},
            "congai/cong.png",
        ),
        ({"x/A.jpg": b"\xff\xd8 chu hoa", "x/a.jpg": b"\xff\xd8 chu thuong"}, "x/a.jpg"),
    ],
    ids=["thu-muc-khac-hoa-thuong", "file-khac-hoa-thuong"],
)
@pytest.mark.xfail(
    strict=True,
    reason="SL-T063-4: trên ổ phân biệt hoa thường, check_chosen_image(scanned=...) đổi ảnh nháp "
    "sang file khác chỉ khác hoa thường (T-076 sửa; gộp T-076 thì bỏ xfail này)",
)
def test_sl_t063_4_scanned_case_sibling_does_not_replace_draft_image(tmp_path, files, rel_path):
    """Ổ phân biệt hoa thường (Linux; Mac khi định dạng APFS phân biệt hoa thường): ``CongAI`` và
    ``congai`` là hai thư mục khác nhau. Nháp chọn ảnh trong ``congai``; giao diện truyền kết quả
    quét cả cây làm ``scanned``. Mong đợi: vẫn đúng file đã chọn, nội dung của nó."""
    root = tmp_path / "anh"
    root.mkdir()
    if not case_sensitive(root):
        pytest.skip("ổ không phân biệt hoa thường: không có hai mục chỉ khác hoa thường")
    for rel, data in files.items():
        write(root / rel, data)
    lib = ImageLibrary([root])
    scanned = lib.list_folder(0, recursive=True).images
    assert len(scanned) == 2
    image = DraftImage(source=SOURCE_REAL, root_index=0, rel_path=rel_path, category="Cổng inox")
    result = check_chosen_image(image, lib, scanned=scanned)
    assert result.available
    assert result.ref.rel_path == rel_path
    assert lib.read_image_bytes(result.ref) == files[rel_path]


# ----- Lá Chắn T-063: cùng lỗ hổng SL-T063-2/-3 trên WINDOWS (ép kẻ tấn công "luôn thắng") -------
#
# Soi Lỗi đo SL-T063-2 trên Linux (tráo nguyên tử ``renameat2(RENAME_EXCHANGE)``). Lá Chắn thử trên
# Windows: cách tráo thật (đổi tên thư mục ↔ junction ``_winapi.CreateJunction``, nhiều luồng, người
# dùng thường) KHÔNG lọt nội dung lần nào (>15.000 lần đọc; Lá Chắn T-048 cũng 0/11.192) vì Windows
# không đổi chỗ nguyên tử được và khóa file chặn đổi tên khi app đang giữ handle. NHƯNG khi ép trạng
# thái (như fixture ``swap_world`` của POSIX: x là junction đúng lúc ``lstat``/``open`` mục cuối),
# Windows **vẫn lọt nội dung và cỡ** — tức là lỗ hổng nằm trong CODE, Windows chỉ được cứu nhờ đặc
# tính hệ điều hành (đua khó thắng), không nhờ ``folders.py``. Hai test này ép trạng thái để chứng
# minh lỗ hổng CODE trên Windows; dùng junction nên không cần admin. (Biên bản: T-063-la-chan.)


@pytest.fixture
def win_swap_world(tmp_path, monkeypatch):
    """Windows: ``anh/x/bi-mat.jpg`` (mồi) và ``ngoai/bi-mat.jpg`` (ngoài gốc, khác cỡ).

    Kẻ tấn công "luôn thắng": mỗi lần app ``lstat`` hay ``open`` một đường dẫn tận cùng là
    ``bi-mat.jpg``, ``x`` được tráo thành junction ra ``ngoai`` (``rename`` + ``CreateJunction``,
    không cần admin), xong thì trả lại thư mục thật; mọi lời gọi khác thấy ``x`` là thư mục thật.
    """
    import _winapi

    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    outside = write(tmp_path / "ngoai" / "bi-mat.jpg", SECRET).parent
    park = tmp_path / "cat-tam"
    real_lstat, real_open = os.lstat, os.open

    def basename(path) -> str:
        try:
            return os.path.basename(os.fsdecode(path))
        except TypeError:
            return ""

    def while_swapped(call, path, *args, **kwargs):
        os.rename(root / "x", park)
        _winapi.CreateJunction(str(outside), str(root / "x"))
        try:
            return call(path, *args, **kwargs)
        finally:
            os.rmdir(root / "x")
            os.rename(park, root / "x")

    def fake_lstat(path, *args, **kwargs):
        if basename(path) == "bi-mat.jpg":
            return while_swapped(real_lstat, path, *args, **kwargs)
        return real_lstat(path, *args, **kwargs)

    def fake_open(path, *args, **kwargs):
        if basename(path) == "bi-mat.jpg":
            return while_swapped(real_open, path, *args, **kwargs)
        return real_open(path, *args, **kwargs)

    def attack() -> None:
        monkeypatch.setattr("seo_app.images.folders.os.lstat", fake_lstat)
        monkeypatch.setattr("seo_app.images.folders.os.open", fake_open)

    return root, attack


@pytest.mark.skipif(not IS_WINDOWS, reason="cách tráo junction của Windows: thử trên Windows")
@pytest.mark.xfail(
    strict=True,
    reason="SL-T063-2 (Windows): lỗ hổng nằm trong code đọc chung mọi hệ điều hành; khi kẻ tấn "
    "công thắng hai lần tráo thì read_image_bytes trả nội dung file ngoài gốc. Thực tế đua này "
    "gần như không thắng được trên Windows (biên bản); T-079 phải vá / giải trình.",
)
def test_sl_t063_2_windows_swap_cannot_read_outside_content(win_swap_world, tmp_path):
    """Như ``test_sl_t063_2_...`` nhưng dùng junction của Windows. Mong đợi: báo lỗi gọn hoặc ra ảnh
    mồi, không bao giờ ra nội dung file ngoài gốc (F1)."""
    root, attack = win_swap_world
    lib = ImageLibrary([root])
    assert lib.read_image_bytes(ImageRef(0, "x/bi-mat.jpg")) == DECOY  # chưa bị tấn công
    attack()
    try:
        data = lib.read_image_bytes(ImageRef(0, "x/bi-mat.jpg"))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert data != SECRET, "đọc được nội dung file ngoài thư mục ảnh (Windows)"


@pytest.mark.skipif(not IS_WINDOWS, reason="cách tráo junction của Windows: thử trên Windows")
@pytest.mark.xfail(
    strict=True,
    reason="SL-T063-3 (Windows): stat_image trả cỡ, giờ sửa của file ngoài gốc khi x bị tráo thành "
    "junction đúng lúc lstat mục cuối. Cùng gốc với SL-T063-2; T-079 vá cùng.",
)
def test_sl_t063_3_windows_swap_gives_no_outside_size(win_swap_world, tmp_path):
    """Như ``test_sl_t063_3_...`` nhưng dùng junction của Windows."""
    root, attack = win_swap_world
    lib = ImageLibrary([root])
    assert lib.stat_image(ImageRef(0, "x/bi-mat.jpg")).size == len(DECOY)
    attack()
    try:
        entry = lib.stat_image(ImageRef(0, "x/bi-mat.jpg"))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert entry.size != len(SECRET), "trả cỡ của file ngoài thư mục ảnh (Windows)"

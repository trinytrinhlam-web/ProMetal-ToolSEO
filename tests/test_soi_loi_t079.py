"""Test thêm của Soi Lỗi T-079: đọc, ``stat`` một ảnh qua chính mục đã mở (``folders.py``).

T-079 vá SL-T063-2, -3 (thư mục con bị tráo thành liên kết đúng lúc đọc thì đọc được file ngoài
thư mục ảnh): Mac/Linux mở thư mục cha từng tầng (``O_NOFOLLOW``) rồi mở, ``stat`` file trong chính
thư mục đã mở; Windows hỏi đường dẫn thật của chính handle vừa mở, phải đúng là ``gốc/parts``.
File này thêm:

- SL-T079-1: Windows so đường dẫn thật bằng ``_path_key`` (gộp dạng Unicode NFC rồi ``casefold``),
  lỏng hơn cách ổ phân biệt tên. Thư mục "anh em" của gốc có tên trông như tên gốc nhưng chỉ khác
  dạng Unicode (NFD), khác ``ß``/``ss``, dấu Kelvin, hay chỉ khác hoa thường trong thư mục bật phân
  biệt hoa thường, là một thư mục KHÁC trên ổ mà vẫn qua phép so. Ép kẻ tấn công "luôn thắng" (như
  Lá Chắn T-063) với đích junction nằm trong thư mục anh em đó thì vẫn đọc được nội dung, cỡ file
  nằm ngoài thư mục ảnh.
- Mỗi lớp mới phải tự đứng được khi lớp khác không che: file bị thay tại chỗ, đổi cỡ, thành ẩn, bị
  xóa giữa lúc kiểm và lúc mở hay ``stat`` (so định danh, kiểm lại trên mục đã mở); Mac/Linux: thư
  mục bị tráo ngay trước bước ``stat`` từng tầng, file thành symlink ngay trước ``stat``
  (``follow_symlinks=False``). Các ca Mac/Linux tự bỏ qua trên Windows.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T079-x (xem
``docs/team/reports/T-079-soi-loi.md``). Mọi test dùng thư mục tạm, ảnh giả, không gọi mạng.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import stat
import subprocess
import unicodedata
from pathlib import Path

import pytest

from seo_app.images import folders
from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="junction, handle: thử trên Windows")
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="symlink, mở theo fd: thử trên Mac/Linux")
SECRET = b"\xff\xd8 SECRET-NGOAI-GOC, dai hon anh moi"
DECOY = b"\xff\xd8 moi"
REF = "x/bi-mat.jpg"


def write(path: Path, data: bytes = b"\xff\xd8\xff anh gia") -> Path:
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


def basename(path) -> str:
    try:
        return os.path.basename(os.fsdecode(path))
    except TypeError:  # fd, không phải đường dẫn
        return ""


def before_opened_stat(monkeypatch, action) -> None:
    """Chạy ``action`` ngay trước bước lấy số liệu trên mục đã mở của ``stat_image`` (sau khi đã
    kiểm đường đi và lấy tên trên ổ)."""
    original = ImageLibrary._opened_stat

    def wrapped(self, root, parts, expected):
        action()
        return original(self, root, parts, expected)

    monkeypatch.setattr(ImageLibrary, "_opened_stat", wrapped)


def before_open_image(monkeypatch, action) -> None:
    """Chạy ``action`` ngay trước khi ``read_image_bytes`` mở file (sau khi đã kiểm đường đi)."""
    original = ImageLibrary._open_image

    def wrapped(self, root, parts, path):
        action()
        return original(self, root, parts, path)

    monkeypatch.setattr(ImageLibrary, "_open_image", wrapped)


# ----- SL-T079-1: Windows so đường dẫn thật lỏng hơn ổ (NFC, casefold) --------------------------

ROOT_NFC = "Ảnh công trình"
LOOKALIKES = [
    pytest.param(ROOT_NFC, None, False, id="dich-ngoai-goc-thuong"),
    pytest.param(ROOT_NFC, unicodedata.normalize("NFD", ROOT_NFC), False, id="anh-em-nfd"),
    pytest.param("Strasse", "Straße", False, id="anh-em-sharp-s"),
    pytest.param("Kho", "Kho", False, id="anh-em-dau-kelvin"),
    pytest.param("Anh", "ANH", True, id="anh-em-khac-hoa-thuong"),
]


def case_insensitive(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir()
    try:
        return (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


def lookalike_world(
    tmp_path: Path, root_name: str, sibling_name: str | None, case_sensitive_parent: bool
) -> tuple[Path, Path]:
    """Gốc ``cha/<root_name>`` có ``x/bi-mat.jpg`` (ảnh mồi). Đích của junction: thư mục ngoài gốc
    bình thường (``sibling_name`` là ``None``), hay ``x`` trong thư mục anh em
    ``cha/<sibling_name>`` (tên trông như tên gốc, nhưng ổ coi là thư mục khác). Đích có
    ``bi-mat.jpg`` khác cỡ."""
    parent = tmp_path / "cha"
    parent.mkdir()
    if case_sensitive_parent:
        fsutil = shutil.which("fsutil")
        if fsutil:
            with contextlib.suppress(OSError, subprocess.TimeoutExpired):
                subprocess.run(
                    [fsutil, "file", "setCaseSensitiveInfo", str(parent), "enable"],
                    capture_output=True,
                    timeout=30,
                    check=False,
                )
        if case_insensitive(parent):
            pytest.skip("không bật được phân biệt hoa thường cho thư mục tạm")
    root = parent / root_name
    write(root / REF, DECOY)
    if sibling_name is None:
        target = tmp_path / "ngoai"
    else:
        sibling = parent / sibling_name
        sibling.mkdir()  # ổ coi hai tên là một thì báo FileExistsError: test sai, không phải app
        assert not sibling.samefile(root)
        target = sibling / "x"
    write(target / "bi-mat.jpg", SECRET)
    return root, target


def attack_always_wins(monkeypatch, root: Path, target: Path, park: Path) -> None:
    """Kẻ tấn công "luôn thắng" (như ``win_swap_world`` của Lá Chắn T-063): mỗi lần app ``lstat``,
    ``open`` hay mở handle (``_win_open``) một đường dẫn tận cùng là ``bi-mat.jpg``, ``x`` là
    junction trỏ tới ``target`` (``rename`` + ``CreateJunction``, không cần quyền quản trị); mọi lời
    gọi khác thấy ``x`` là thư mục thật."""
    import _winapi

    def while_swapped(call, path, *args, **kwargs):
        os.rename(root / "x", park)
        _winapi.CreateJunction(str(target), str(root / "x"))
        try:
            return call(path, *args, **kwargs)
        finally:
            os.rmdir(root / "x")
            os.rename(park, root / "x")

    def swapping(call):
        def wrapper(path, *args, **kwargs):
            if basename(path) == "bi-mat.jpg":
                return while_swapped(call, path, *args, **kwargs)
            return call(path, *args, **kwargs)

        return wrapper

    monkeypatch.setattr("seo_app.images.folders.os.lstat", swapping(os.lstat))
    monkeypatch.setattr("seo_app.images.folders.os.open", swapping(os.open))
    monkeypatch.setattr(folders, "_win_open", swapping(folders._win_open))


@windows_only
@pytest.mark.parametrize(("root_name", "sibling_name", "case_sensitive_parent"), LOOKALIKES)
def test_sl_t079_1_junction_into_lookalike_sibling_cannot_read_outside_content(
    tmp_path, monkeypatch, root_name, sibling_name, case_sensitive_parent
):
    """Junction ``x`` trỏ vào thư mục anh em có tên trông như gốc: đường dẫn thật của handle khác
    ``gốc/x/bi-mat.jpg`` trên ổ nhưng ``_path_key`` coi là một. Mong đợi: báo lỗi gọn hoặc ra ảnh
    mồi, không bao giờ ra nội dung file ngoài thư mục ảnh (F1). Ca ``dich-ngoai-goc-thuong`` là đối
    chứng: đích ngoài gốc bình thường, T-079 đã chặn."""
    root, target = lookalike_world(tmp_path, root_name, sibling_name, case_sensitive_parent)
    lib = ImageLibrary([root])
    assert lib.read_image_bytes(ImageRef(0, REF)) == DECOY  # chưa bị tấn công
    attack_always_wins(monkeypatch, root, target, tmp_path / "cat-tam")
    try:
        data = lib.read_image_bytes(ImageRef(0, REF))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert data != SECRET, "đọc được nội dung file ngoài thư mục ảnh"


@windows_only
@pytest.mark.parametrize(("root_name", "sibling_name", "case_sensitive_parent"), LOOKALIKES)
def test_sl_t079_1_junction_into_lookalike_sibling_gives_no_outside_size(
    tmp_path, monkeypatch, root_name, sibling_name, case_sensitive_parent
):
    """Như trên với ``stat_image``: không trả cỡ của file ngoài thư mục ảnh."""
    root, target = lookalike_world(tmp_path, root_name, sibling_name, case_sensitive_parent)
    lib = ImageLibrary([root])
    assert lib.stat_image(ImageRef(0, REF)).size == len(DECOY)
    attack_always_wins(monkeypatch, root, target, tmp_path / "cat-tam")
    try:
        entry = lib.stat_image(ImageRef(0, REF))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        assert entry.size != len(SECRET), "trả cỡ của file ngoài thư mục ảnh"


# ----- mỗi lớp kiểm trên mục đã mở tự đứng được (mọi hệ điều hành) ------------------------------


@pytest.fixture
def x_root(tmp_path: Path) -> Path:
    root = tmp_path / "anh"
    write(root / REF, DECOY)
    return root


def test_read_refuses_file_replaced_in_place_before_open(x_root, tmp_path, monkeypatch):
    """Ngay trước khi mở, file ảnh bị thay tại chỗ bằng file khác (cùng đường dẫn, nên đường dẫn
    thật của handle vẫn đúng): phép so định danh trên fd đã mở phải bắt được ("phải đúng là file vừa
    kiểm"), không trả nội dung file thay vào."""
    other = write(tmp_path / "khac.jpg", b"\xff\xd8 FILE THAY TAI CHO")
    before_open_image(monkeypatch, lambda: os.replace(other, x_root / REF))
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.read_image_bytes(ImageRef(0, REF)), tmp_path)
    assert "thay đổi" in str(exc)


def test_stat_refuses_file_replaced_in_place_before_opened_stat(x_root, tmp_path, monkeypatch):
    """Như trên với ``stat_image``: số liệu lấy trên mục đã mở phải cùng định danh với mục vừa kiểm;
    file bị thay tại chỗ thì báo "vừa bị thay đổi", không trả cỡ của file thay vào."""
    other = write(tmp_path / "khac.jpg", b"\xff\xd8 FILE THAY TAI CHO, dai hon han")
    before_opened_stat(monkeypatch, lambda: os.replace(other, x_root / REF))
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert "thay đổi" in str(exc)


def test_stat_numbers_come_from_the_opened_file(x_root, monkeypatch):
    """Số liệu ``stat_image`` trả (cỡ, giờ sửa, ``file_id``) lấy trên chính mục đã mở, không từ lần
    ``lstat`` theo đường dẫn lúc kiểm: file (cùng định danh) đổi cỡ, giờ sửa ngay trước bước đó thì
    kết quả theo số mới."""
    image = x_root / REF
    data = b"\xff\xd8 moi, dai hon"
    before = os.stat(image)

    def rewrite() -> None:
        image.write_bytes(data)
        os.utime(image, (1_700_000_000, 1_700_000_000))

    before_opened_stat(monkeypatch, rewrite)
    entry = ImageLibrary([x_root]).stat_image(ImageRef(0, REF))
    now = os.stat(image)
    assert (now.st_dev, now.st_ino) == (before.st_dev, before.st_ino)  # vẫn là file đó
    assert (len(data), 1_700_000_000) != (len(DECOY), before.st_mtime)
    assert (entry.size, entry.modified) == (len(data), 1_700_000_000)
    assert entry.file_id == (now.st_dev, now.st_ino)


@pytest.mark.parametrize(
    ("new_size", "message"), [(40, "quá lớn"), (0, "rỗng")], ids=["to-ra", "thanh-rong"]
)
def test_stat_checks_size_on_the_opened_file(x_root, tmp_path, monkeypatch, new_size, message):
    """File (cùng định danh) to ra quá giới hạn hay thành rỗng ngay trước bước lấy số liệu trên mục
    đã mở: ``stat_image`` báo theo cỡ mới, không trả ``ImageEntry`` có cỡ vượt giới hạn hay 0
    byte."""

    def resize() -> None:
        with open(x_root / REF, "r+b") as handle:
            handle.truncate(new_size)

    before_opened_stat(monkeypatch, resize)
    lib = ImageLibrary([x_root], max_file_bytes=16)
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert message in str(exc)


def test_stat_refuses_item_turned_into_folder_on_disk_without_file_ids(
    x_root, tmp_path, monkeypatch
):
    """Ổ không cho biết định danh (``st_ino`` bằng 0: ổ ảo, một số ổ FAT) thì phép so định danh
    không có tác dụng (``_same_file`` luôn đúng). File ảnh bị thay bằng thư mục cùng tên ngay trước
    bước lấy số liệu trên mục đã mở: vẫn phải bị từ chối nhờ kiểm "file thường" trên mục đã mở."""
    monkeypatch.setattr(folders, "_same_file", lambda a, b: True)

    def to_folder() -> None:
        os.remove(x_root / REF)
        (x_root / REF).mkdir()

    before_opened_stat(monkeypatch, to_folder)
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert "thay đổi" in str(exc)


def test_file_id_is_unknown_on_disk_without_inode_numbers():
    """Ổ không có số inode (``st_ino`` bằng 0): ``file_id`` là ``None`` (không biết), không phải
    ``(số ổ, 0)``; nếu không, mọi file trên ổ đó có cùng "định danh" và bước hỏi lại tên của nháp
    nhận bản sao như cùng một file (LC-T076-3)."""
    fields = (stat.S_IFREG | 0o644, 0, 7, 1, 0, 0, 10, 0, 0, 0)  # mode, ino=0, dev=7, ...
    assert folders._file_id(os.stat_result(fields)) is None
    assert folders._file_id(os.stat_result((stat.S_IFREG | 0o644, 5, *fields[2:]))) == (7, 5)


def test_stat_of_file_deleted_before_opened_stat_is_a_plain_error(x_root, tmp_path, monkeypatch):
    """File bị xóa ngay trước bước lấy số liệu trên mục đã mở: lỗi gọn, không xích lỗi hệ điều
    hành, không lộ đường dẫn (Mac/Linux "không tìm thấy"; Windows "không đọc được")."""
    before_opened_stat(monkeypatch, lambda: os.remove(x_root / REF))
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert "Không tìm thấy" in str(exc) or "Không đọc được" in str(exc)


def _make_hidden(path: Path) -> None:
    if IS_WINDOWS:
        import ctypes

        attributes = os.stat(path).st_file_attributes | stat.FILE_ATTRIBUTE_HIDDEN
        assert ctypes.windll.kernel32.SetFileAttributesW(str(path), attributes)
    else:
        os.chflags(path, stat.UF_HIDDEN)


@pytest.mark.skipif(
    not IS_WINDOWS and not (hasattr(os, "chflags") and hasattr(stat, "UF_HIDDEN")),
    reason="thuộc tính ẩn chỉ có trên Windows, Mac",
)
def test_stat_refuses_file_turned_hidden_before_opened_stat(x_root, tmp_path, monkeypatch):
    """File thành ẩn ngay trước bước lấy số liệu trên mục đã mở: ``stat_image`` không nhận (theo
    đúng luật quét: mục ẩn bị bỏ qua)."""
    before_opened_stat(monkeypatch, lambda: _make_hidden(x_root / REF))
    lib = ImageLibrary([x_root])
    raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)


@windows_only
def test_windows_stat_item_that_cannot_be_opened_is_unreadable(x_root, tmp_path, monkeypatch):
    """Windows: không mở được handle hỏi thuộc tính của ảnh thì báo lỗi gọn, không quay về số liệu
    ``lstat`` theo đường dẫn."""
    monkeypatch.setattr(folders, "_win_open", lambda path, access: None)
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert "Không đọc được" in str(exc)


# ----- Mac/Linux: bước ``stat`` trên thư mục đã mở --------------------------------------------


@posix_only
def test_posix_folder_swapped_right_before_opened_stat_is_refused(x_root, tmp_path, monkeypatch):
    """Đã kiểm đường đi và lấy tên xong, ``x`` mới bị tráo thành symlink ra ngoài, ngay trước bước
    mở thư mục từng tầng của ``stat_image``: ``openat(O_DIRECTORY | O_NOFOLLOW)`` từ chối, câu báo
    "vừa bị thay đổi" (ELOOP trên Mac, ENOTDIR trên Linux: SL-T063-5), không trả cỡ file ngoài
    gốc."""
    outside = write(tmp_path / "ngoai" / "bi-mat.jpg", SECRET).parent

    def swap() -> None:
        os.rename(x_root / "x", tmp_path / "x-cu")
        (x_root / "x").symlink_to(outside, target_is_directory=True)

    before_opened_stat(monkeypatch, swap)
    lib = ImageLibrary([x_root])
    exc = raises_safely(lambda: lib.stat_image(ImageRef(0, REF)), tmp_path)
    assert "thay đổi" in str(exc)


@posix_only
def test_posix_image_turned_into_symlink_is_not_followed_by_stat(x_root, tmp_path, monkeypatch):
    """Ép kẻ tấn công "luôn thắng" ở bước kiểm đường đi (như ``swap_world`` của Soi Lỗi T-063:
    ``x`` là symlink ra ngoài đúng lúc ``lstat`` một đường dẫn tận cùng là ``bi-mat.jpg``, nên mục
    vừa kiểm là file ngoài gốc), rồi ngay trước bước ``stat`` trên thư mục đã mở, chính file ảnh
    trong ``x`` thật bị thay bằng symlink tới file ngoài gốc đó. ``stat`` trên thư mục đã mở không
    được đi theo symlink (``follow_symlinks=False``): đi theo thì cùng định danh với mục vừa kiểm và
    trả cỡ file ngoài gốc."""
    outside = write(tmp_path / "ngoai" / "bi-mat.jpg", SECRET).parent
    park = tmp_path / "cat-tam"
    real_lstat = os.lstat

    def fake_lstat(path, *args, **kwargs):
        if basename(path) != "bi-mat.jpg":
            return real_lstat(path, *args, **kwargs)
        os.rename(x_root / "x", park)
        os.symlink(outside, x_root / "x", target_is_directory=True)
        try:
            return real_lstat(path, *args, **kwargs)
        finally:
            os.unlink(x_root / "x")
            os.rename(park, x_root / "x")

    def image_to_symlink() -> None:
        os.rename(x_root / REF, tmp_path / "anh-cu.jpg")
        os.symlink(outside / "bi-mat.jpg", x_root / REF)

    lib = ImageLibrary([x_root])
    assert lib.stat_image(ImageRef(0, REF)).size == len(DECOY)  # chưa bị tấn công
    monkeypatch.setattr("seo_app.images.folders.os.lstat", fake_lstat)
    before_opened_stat(monkeypatch, image_to_symlink)
    try:
        entry = lib.stat_image(ImageRef(0, REF))
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
        assert "thay đổi" in str(exc)
    else:
        assert entry.size != len(SECRET), "trả cỡ của file ngoài thư mục ảnh"

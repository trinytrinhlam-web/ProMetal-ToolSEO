"""Test thêm của Soi Lỗi T-079 (cloud Linux): đọc, ``stat`` ảnh qua thư mục đã mở từng tầng.

T-079 vá SL-T063-2, -3: trên Mac/Linux ``read_image_bytes`` và ``stat_image`` mở thư mục cha từng
tầng từ gốc (``O_NOFOLLOW``) rồi mở/``stat`` file trong chính thư mục đã mở. Thợ Máy chỉ chạy được
bộ giả lập trên Windows, nên chưa thử được tính chất chính: **thư mục đã mở vẫn là thư mục thật dù
tên của nó bị tráo ngay sau đó**. File này khóa tính chất đó bằng symlink thật (chỉ Mac/Linux), kèm
một lượt tráo thật ngắn bằng ``renameat2(RENAME_EXCHANGE)`` (chỉ Linux).

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T079-L-x. Mọi test dùng thư mục tạm, ảnh
giả, không gọi mạng. Kết quả đo dài hơn: báo cáo ``docs/team/reports/T-079-soi-loi-linux.md``.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from seo_app.images import folders
from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef

IS_WINDOWS = os.name == "nt"
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="symlink thật, mở thư mục từng tầng: Mac/Linux")
SECRET = b"\xff\xd8 SECRET-NGOAI-GOC, dai hon anh moi"
DECOY = b"\xff\xd8 moi"


def write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def assert_safe_error(exc: ImageFolderError, base: Path) -> None:
    text = str(exc)
    assert text
    for form in {str(base), str(base.resolve()), "ngoai", "SECRET"}:
        assert form not in text, f"câu lỗi lộ {form!r}"
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__


def open_fds() -> int | None:
    """Số fd đang mở của tiến trình (Linux ``/proc/self/fd``, Mac ``/dev/fd``)."""
    for folder in ("/proc/self/fd", "/dev/fd"):
        try:
            return len(os.listdir(folder))
        except OSError:
            continue
    return None


@pytest.fixture
def deep_tree(tmp_path: Path) -> dict:
    """``anh/a/b/bi-mat.jpg`` (ảnh mồi) và ``ngoai/...`` cùng cấu trúc (file ngoài gốc, khác cỡ)."""
    root = tmp_path / "anh"
    write(root / "a" / "b" / "bi-mat.jpg", DECOY)
    outside = tmp_path / "ngoai"
    write(outside / "b" / "bi-mat.jpg", SECRET)
    write(outside / "bi-mat.jpg", SECRET)
    return {"base": tmp_path, "root": root, "outside": outside}


def swap_after_open(monkeypatch, deep_tree: dict, level: str) -> list[str]:
    """Ngay sau khi app mở xong các tầng thư mục để đọc/``stat`` ảnh, tầng ``level`` (``a`` hay
    ``a/b``) bị tráo thành symlink ra ngoài (thư mục thật dời sang chỗ khác). Chỉ tráo ở bước mở
    để đọc (``_open_image``) hay lấy số liệu (``_opened_stat``), không ở bước kiểm tên trước đó."""
    root, outside = deep_tree["root"], deep_tree["outside"]
    real_open_dir = folders._posix_open_dir
    swapped: list[str] = []

    def open_then_swap(root_path, parts):
        fd = real_open_dir(root_path, parts)
        caller = sys._getframe(1).f_code.co_name
        if caller in ("_open_image", "_opened_stat") and not swapped:
            link = root / level
            os.rename(link, deep_tree["base"] / "da-doi")
            link.symlink_to(outside, target_is_directory=True)
            swapped.append(caller)
        return fd

    monkeypatch.setattr(folders, "_posix_open_dir", open_then_swap)
    return swapped


@posix_only
@pytest.mark.parametrize("level", ["a", "a/b"], ids=["tang-tren", "tang-giua"])
def test_folder_swapped_right_after_levels_opened_still_reads_checked_image(
    deep_tree, monkeypatch, level
):
    """Tầng thư mục bị tráo thành symlink ra ngoài **sau khi** app đã mở nó: app đọc trong chính
    thư mục đã mở (thư mục thật, đã dời đi), nên ra đúng ảnh đã kiểm, không ra file ngoài gốc.
    Đây là điều bộ giả lập trên Windows của Thợ Máy không thử được."""
    swapped = swap_after_open(monkeypatch, deep_tree, level)
    lib = ImageLibrary([deep_tree["root"]])
    data = lib.read_image_bytes(ImageRef(0, "a/b/bi-mat.jpg"))
    assert swapped == ["_open_image"]
    assert data == DECOY


@posix_only
@pytest.mark.parametrize("level", ["a", "a/b"], ids=["tang-tren", "tang-giua"])
def test_folder_swapped_right_after_levels_opened_still_stats_checked_image(
    deep_tree, monkeypatch, level
):
    """Như trên cho ``stat_image``: cỡ, giờ sửa, định danh của ảnh đã kiểm, không của file ngoài."""
    swapped = swap_after_open(monkeypatch, deep_tree, level)
    lib = ImageLibrary([deep_tree["root"]])
    expected = os.stat(deep_tree["root"] / "a" / "b" / "bi-mat.jpg")
    entry = lib.stat_image(ImageRef(0, "a/b/bi-mat.jpg"))
    assert swapped == ["_opened_stat"]
    assert entry.size == len(DECOY)
    assert entry.file_id == (expected.st_dev, expected.st_ino)


@posix_only
@pytest.mark.parametrize("level", ["a", "a/b"], ids=["tang-tren", "tang-giua"])
@pytest.mark.parametrize("call", ["read_image_bytes", "stat_image"])
def test_level_swapped_before_opening_is_refused_without_fd_leak(
    deep_tree, monkeypatch, level, call
):
    """Tầng ``a`` hay ``a/b`` bị tráo thành symlink ngay trước khi app mở từng tầng: từ chối, câu
    báo "vừa bị thay đổi" (SL-T063-5: Linux trả ENOTDIR), không lộ đường dẫn, không rò fd."""
    root, outside = deep_tree["root"], deep_tree["outside"]
    real_open_dir = folders._posix_open_dir

    def swap_then_open(root_path, parts):
        caller = sys._getframe(1).f_code.co_name
        link = root / level
        if caller in ("_open_image", "_opened_stat") and not link.is_symlink():
            os.rename(link, deep_tree["base"] / "da-doi")
            link.symlink_to(outside, target_is_directory=True)
        return real_open_dir(root_path, parts)

    monkeypatch.setattr(folders, "_posix_open_dir", swap_then_open)
    lib = ImageLibrary([root])
    before = open_fds()
    with pytest.raises(ImageFolderError) as info:
        getattr(lib, call)(ImageRef(0, "a/b/bi-mat.jpg"))
    assert "thay đổi" in str(info.value)
    assert_safe_error(info.value, deep_tree["base"])
    assert open_fds() == before


# ----- tráo thật, liên tục (Linux) -------------------------------------------------------------

# Tiến trình tráo riêng (như một chương trình khác trên máy): đổi chỗ nguyên tử ``x`` với symlink
# ra ngoài cho tới khi thấy file dừng, trả ``x`` về thư mục thật, in số lần tráo.
_SWAPPER = """
import ctypes, os, sys
swap, link, stop = (os.fsencode(a) for a in sys.argv[1:4])
renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
done = 0
while not os.path.exists(stop):
    for _ in range(200):
        if renameat2(-100, swap, -100, link, 2) == 0:  # AT_FDCWD, RENAME_EXCHANGE
            done += 1
if done % 2:
    renameat2(-100, swap, -100, link, 2)
print(done)
"""


def _has_renameat2() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    try:
        return hasattr(ctypes.CDLL(None), "renameat2")
    except OSError:
        return False


linux_exchange = pytest.mark.skipif(
    not _has_renameat2(), reason="đổi chỗ nguyên tử renameat2(RENAME_EXCHANGE): chỉ Linux"
)


@linux_exchange
def test_real_atomic_swap_race_never_leaks_outside_content_or_size(tmp_path):
    """Dựng lại ca 8a của Soi Lỗi T-063 trong 1,5 giây: một tiến trình khác đổi chỗ nguyên tử liên
    tục thư mục ``x`` với symlink ra ngoài; app đọc, ``stat`` ảnh liên tục. Bản trước T-079 (thử
    trên máy cloud) lọt nội dung, cỡ hàng trăm lần trong 1,5 giây; bản T-079 không được lọt lần nào
    (nội dung, cỡ, định danh), câu lỗi không lộ đường dẫn, không rò fd."""
    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    outside = tmp_path / "ngoai"
    secret_st = os.stat(write(outside / "bi-mat.jpg", SECRET))
    spare = tmp_path / "spare"
    spare.mkdir()
    (spare / "lk").symlink_to(outside, target_is_directory=True)
    stop = tmp_path / "dung"
    lib = ImageLibrary([root])
    ref = ImageRef(0, "x/bi-mat.jpg")
    assert lib.read_image_bytes(ref) == DECOY  # chưa bị tấn công
    before = open_fds()
    leaks: list[str] = []
    seen = {"read_ok": 0, "stat_ok": 0, "errors": 0}
    args = [sys.executable, "-c", _SWAPPER, str(root / "x"), str(spare / "lk"), str(stop)]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
    try:
        time.sleep(0.1)
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline:
            try:
                data = lib.read_image_bytes(ref)
                if data == SECRET:
                    leaks.append("nội dung")
                else:
                    assert data == DECOY
                    seen["read_ok"] += 1
            except ImageFolderError as exc:
                assert_safe_error(exc, tmp_path)
                seen["errors"] += 1
            try:
                entry = lib.stat_image(ref)
                file_id = getattr(entry, "file_id", None)  # chạy được cả trên bản trước T-079
                if entry.size == len(SECRET) or file_id == (secret_st.st_dev, secret_st.st_ino):
                    leaks.append("cỡ")
                else:
                    seen["stat_ok"] += 1
            except ImageFolderError as exc:
                assert_safe_error(exc, tmp_path)
                seen["errors"] += 1
    finally:
        stop.touch()
        out, _ = proc.communicate(timeout=30)
    swaps = int(out.strip() or 0)
    assert swaps > 1000, "tiến trình tráo không chạy được"
    assert not leaks, f"lọt {len(leaks)} lần ({sorted(set(leaks))}), {seen}"
    assert open_fds() == before
    assert lib.read_image_bytes(ref) == DECOY


# ----- SL-T079-L-1 (Thấp): ``resolve`` gặp tầng vừa đổi lại thành thư mục thì báo "không có quyền"


@posix_only
@pytest.mark.xfail(
    strict=True,
    reason="SL-T079-L-1 (soi-loi): _resolve_inside đổi OSError(EINVAL) của resolve(strict=True) "
    "(tầng vừa là symlink lúc resolve lstat, vừa thành thư mục lại lúc readlink) thành 'Không đọc "
    "được mục này (không có quyền…)' thay vì 'vừa bị thay đổi'. An toàn, chỉ sai câu báo",
)
@pytest.mark.parametrize("call", ["read_image_bytes", "stat_image", "list_folder"])
def test_sl_t079_l_1_resolve_race_is_reported_as_changed(tmp_path, monkeypatch, call):
    """Đo thật trên cloud (ca 8a, 8 giây): khoảng 1.100 lần mỗi việc báo "Không đọc được mục này
    (không có quyền hoặc ổ đĩa vừa bị ngắt)" trong lúc bị tráo, lỗi gốc ``OSError(22)`` ở
    ``_resolve_inside`` (bước ``resolve(strict=True)``). Ở đây kẻ tráo "luôn thắng": ``x`` thành
    symlink ngay trước khi ``resolve`` xem ``x``, rồi thành thư mục thật lại ngay trước khi
    ``resolve`` đọc đích của symlink (``readlink`` trên thư mục: EINVAL thật của hệ điều hành).
    Vòng ``lstat`` trước đó vừa thấy ``x`` là thư mục thật, nên đây là "vừa bị thay đổi"."""
    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    outside = tmp_path / "ngoai"
    write(outside / "bi-mat.jpg", SECRET)
    park = tmp_path / "cat-tam"
    real_realpath, real_readlink = os.path.realpath, os.readlink
    x = root / "x"

    def readlink_after_swap_back(path, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) == "x" and x.is_symlink():
            x.unlink()
            park.rename(x)
        return real_readlink(path, *args, **kwargs)

    def racing_realpath(path, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) not in ("bi-mat.jpg", "x"):
            return real_realpath(path, *args, **kwargs)
        x.rename(park)
        x.symlink_to(outside, target_is_directory=True)
        monkeypatch.setattr(os, "readlink", readlink_after_swap_back)
        try:
            return real_realpath(path, *args, **kwargs)
        finally:
            monkeypatch.setattr(os, "readlink", real_readlink)
            if x.is_symlink():
                x.unlink()
                park.rename(x)

    lib = ImageLibrary([root])
    target = (
        (lambda: lib.list_folder(0, "x"))
        if call == "list_folder"
        else (lambda: getattr(lib, call)(ImageRef(0, "x/bi-mat.jpg")))
    )
    target()  # chưa bị tấn công
    monkeypatch.setattr(os.path, "realpath", racing_realpath)
    with pytest.raises(ImageFolderError) as info:
        target()
    assert_safe_error(info.value, tmp_path)
    assert x.is_dir() and not x.is_symlink()
    assert "thay đổi" in str(info.value)

"""Đọc ảnh trong các thư mục khai báo ở ``IMAGE_FOLDERS``: an toàn, chỉ đọc, không treo.

Nguyên tắc (phiếu T-048, thiết kế T-046 mục 1, ``security.md`` mục 2.6 và F1):

- Mỗi ảnh được nhận diện bằng ``ImageRef`` = (số thứ tự thư mục gốc, đường dẫn tương đối dạng
  ``a/b/anh.jpg``). Đường dẫn tuyệt đối chỉ nằm bên trong ``ImageLibrary`` (thuộc tính riêng),
  không có trong kết quả trả về, ``repr`` hay câu báo lỗi.
- Đường dẫn tương đối là dữ liệu chưa tin cậy (có thể đến từ nháp đã lưu): từ chối ``..``,
  ``.``, phần rỗng, gốc tuyệt đối, ổ đĩa (``C:``), đường dẫn mạng UNC, dấu gạch ngược, dấu hai
  chấm, ký tự điều khiển, surrogate lẻ, ký tự điều khiển hướng chữ, tên thiết bị của Windows
  (``CON``, ``NUL``…), tên kết thúc bằng dấu chấm hoặc khoảng trắng.
- Không đi qua liên kết: từng phần của đường dẫn được ``lstat`` và từ chối nếu là symlink hay
  junction Windows (``os.scandir`` coi junction là thư mục thường nên phải kiểm riêng). Sau đó
  ``resolve(strict=True)`` và bắt buộc ``is_relative_to(gốc)``. Mục ẩn/hệ thống và tên ngắn
  8.3 cũng bị từ chối, để ``ImageRef`` theo đúng luật của lúc quét.
- ``ImageRef`` trả ra (``list_folder``, ``stat_image``) theo tên trên ổ, không theo chữ người gọi
  gõ (T-076, LC-T055-1): ổ Windows, Mac không phân biệt hoa thường nên ``congai`` vẫn mở được thư
  mục ``CongAI``, còn thẻ ảnh đọc từ tên thư mục thì phân biệt. Tên trên ổ lấy từ thư mục cha (tên
  ổ liệt kê ra), không từ ``resolve``: ổ Google Drive for Desktop của Windows trả lại đúng chữ đã
  gõ khi ``resolve`` (LC-T076-1).
- Khi quét, thư mục được "giữ" để không bị tráo giữa lúc kiểm và lúc đọc (xem phần "giữ thư
  mục trong lúc quét").
- Đọc một ảnh, lấy số liệu một ảnh (``read_image_bytes``, ``stat_image``) không đi theo chuỗi đường
  dẫn đã kiểm (T-079, SL-T063-2, -3): một tầng giữa bị tráo thành liên kết ngay sau lúc kiểm thì
  đường dẫn đi xuyên ra ngoài gốc. Mac/Linux mở thư mục cha từng tầng từ gốc (``O_NOFOLLOW``) rồi
  mở/``stat`` file trong chính thư mục đã mở; Windows hỏi đường dẫn thật của chính handle vừa mở
  (phải trùng từng chữ với gốc và tên trên ổ, LC-T079-1). Số liệu, nội dung và câu báo lỗi (cỡ,
  loại file) lấy từ mục đã mở, không từ ``lstat`` theo tên (LC-T079-2).
- Chỉ nhận đuôi ảnh đã biết (``IMAGE_EXTENSIONS``) và file không quá ``MAX_IMAGE_BYTES``. Ảnh
  HEIC/HEIF chỉ được liệt kê khi bật ``HEIC_ENABLED`` (tạm tắt, T-107 lượt 3).
- Quét có ngân sách (số mục, số giây), phân trang; vượt ngân sách thì dừng và báo "còn nữa".
- Chỉ đọc: module không tạo, sửa, đổi tên hay xóa gì trong thư mục ảnh (quyết định 3A).
- Tên file, tên thư mục trả về là dữ liệu chưa tin cậy (góp ý Lá Chắn số 3): module chỉ trả
  nguyên tên, không diễn giải thành thẻ (việc của T-052); giao diện phải escape khi hiện.
"""

from __future__ import annotations

import contextlib
import ctypes
import errno
import functools
import math
import os
import stat
import time
import unicodedata
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath

# Công tắc HEIC duy nhất (T-107 lượt 3, LC-T107-2): chủ dự án chọn 30/10 tạm không nhận ảnh
# HEIC/HEIF vì libheif 1.23.6 trong pillow-heif 1.8.1 còn lỗi làm treo máy đã công bố. Đổi thành
# ``True`` khi nâng pillow-heif lên bản mang libheif từ 1.23.7 (chủ dự án đã duyệt nâng, Lá Chắn
# quét trước). ``process.py`` đọc công tắc này lúc mở ảnh.
HEIC_ENABLED = False
HEIC_EXTENSIONS = frozenset({".heic", ".heif"})
# JPEG, PNG, WebP; HEIC/HEIF (iPhone, quyết định 1A) khi ``HEIC_ENABLED``. Không nhận GIF, BMP,
# TIFF, .lnk. Không nhận AVIF (T-078): ``process.py`` không mở AVIF (``ALLOWED_FORMATS``) nên
# khung chọn ảnh không liệt kê ``.avif``.
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"}) | (
    HEIC_EXTENSIONS if HEIC_ENABLED else frozenset()
)
MAX_IMAGE_BYTES = 40 * 1024 * 1024  # 40 MB/file (thiết kế T-046 mục 1)
MAX_REL_PATH_CHARS = 1024
MAX_NAME_CHARS = 255
DEFAULT_PAGE_SIZE = 48
MAX_PAGE_SIZE = 200
DEFAULT_MAX_ENTRIES = 5000  # số mục tối đa mỗi lần quét
DEFAULT_MAX_SECONDS = 10.0  # số giây tối đa mỗi lần quét
DEFAULT_MAX_DEPTH = 8  # số tầng thư mục con tối đa khi quét cả cây

_FORBIDDEN_CHARS = frozenset('\\/:<>"|?*')
# Ký tự điều khiển hướng chữ (LRE, RLE, PDF, LRO, RLO, LRI, RLI, FSI, PDI): tên ảnh thật không
# cần, chỉ dùng để hiện tên đánh lừa (``anh<RLO>gpj.exe`` hiện thành ``anhexe.jpg``).
_BIDI_CONTROLS = frozenset("\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
# Loại ký tự bị từ chối: Cc (điều khiển) và Cs (surrogate lẻ: tên UTF-16 lẻ cặp trên NTFS, tên
# sai UTF-8 trên Linux). Surrogate không mã hóa được UTF-8 nên giao diện sẽ lỗi khi hiện (L2).
_FORBIDDEN_CATEGORIES = frozenset({"Cc", "Cs"})
_WINDOWS_DEVICE_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    | {f"{dev}{n}" for dev in ("COM", "LPT") for n in (*"123456789", "¹", "²", "³")}
)
# Bit "name surrogate" của reparse tag: reparse point trỏ tới một chỗ khác (symlink, junction,
# ổ gắn vào thư mục, symlink WSL). File "chỉ trực tuyến" của OneDrive/Drive không có bit này.
_REPARSE_NAME_SURROGATE = 0x20000000
_UF_HIDDEN = getattr(stat, "UF_HIDDEN", 0)
# Cách lấy tên trên ổ (T-076). Không máy nào lấy tên từ ``resolve``: trên Mac/Linux, và trên ổ
# Google Drive for Desktop của Windows (đo trên máy chủ dự án, LC-T076-1), ``resolve`` trả lại đúng
# chữ đã gõ. ``True`` (Windows): hỏi thư mục cha đúng mục đó, từng tầng (``FindFirstFileW``).
# ``False`` (Mac/Linux): đọc tên trong thư mục cha (``_listed_names``). Tên hằng có từ lượt 1 (khi
# Windows còn lấy tên từ ``resolve``), giữ lại vì test đặt hằng này để chạy cách của Mac/Linux.
_NAMES_FROM_RESOLVE = os.name == "nt"
_ERROR_FILE_NOT_FOUND = 2
_ERROR_PATH_NOT_FOUND = 3
_ERROR_ACCESS_DENIED = 5  # cả khi mục đang chờ xóa (junction vừa bị xóa)
_ERROR_CANT_RESOLVE_FILENAME = 1921  # vòng liên kết (symlink, junction trỏ vòng)

_MSG_BAD_PATH = "Đường dẫn ảnh không hợp lệ."
_MSG_NOT_FOUND = (
    "Không tìm thấy ảnh hoặc thư mục này (có thể đã đổi tên, đã xóa hoặc chưa đồng bộ xong)."
)
_MSG_LINK = "Đường dẫn đi qua liên kết tắt (symlink/junction), app không đọc qua liên kết."
_MSG_UNREADABLE = "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)."
_MSG_HIDDEN = "App không đọc thư mục hay file ẩn, file hệ thống."
_MSG_ALIAS = "Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục)."
_MSG_SLOW = "Ổ đĩa đang chậm nên chưa kiểm được tên thư mục, hãy thử lại."
_MSG_IMAGE_CHANGED = "Ảnh vừa bị thay đổi trong lúc đọc, hãy thử lại."
_MSG_CANNOT_OPEN = "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)."


class ImageFolderError(Exception):
    """Lỗi đọc thư mục ảnh; câu tiếng Việt hiện thẳng được, không chứa đường dẫn tuyệt đối."""


class _LinkError(ImageFolderError):
    """Đường dẫn đi qua liên kết hoặc ra ngoài gốc (khi quét: đếm vào ``skipped.links``)."""


class _ChangedError(_LinkError):
    """Thư mục bị tráo giữa lúc kiểm và lúc quét (L1)."""

    def __init__(self) -> None:
        super().__init__("Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại.")


def _is_safe_name(name: str) -> bool:
    """Một phần của đường dẫn (tên file hoặc tên thư mục) có an toàn và dùng được không."""
    if not name or len(name) > MAX_NAME_CHARS or name in (".", ".."):
        return False
    if name.startswith(".") or name[-1] in ". ":
        # Tên ẩn (``.DS_Store``, ``._IMG.jpg`` của Mac) và tên mà Windows tự cắt dấu chấm,
        # khoảng trắng cuối (hai tên khác nhau trỏ cùng một file).
        return False
    for ch in name:
        if (
            ch in _FORBIDDEN_CHARS
            or ch in _BIDI_CONTROLS
            or unicodedata.category(ch) in _FORBIDDEN_CATEGORIES
        ):
            return False
    return name.split(".")[0].rstrip(" ").upper() not in _WINDOWS_DEVICE_NAMES


def _parse_rel(rel_path: object, *, allow_empty: bool) -> tuple[str, ...]:
    """Tách đường dẫn tương đối dạng ``a/b/c`` thành các phần; từ chối mọi dạng lạ."""
    if not isinstance(rel_path, str):
        raise ImageFolderError(_MSG_BAD_PATH)
    if rel_path == "":
        if allow_empty:
            return ()
        raise ImageFolderError(_MSG_BAD_PATH)
    if len(rel_path) > MAX_REL_PATH_CHARS:
        raise ImageFolderError(_MSG_BAD_PATH)
    # Kiểm theo cả kiểu Windows lẫn kiểu Mac/Linux, bất kể app đang chạy trên máy nào.
    if (
        rel_path.startswith("/")
        or PurePosixPath(rel_path).is_absolute()
        or PureWindowsPath(rel_path).drive
        or PureWindowsPath(rel_path).anchor
    ):
        raise ImageFolderError(_MSG_BAD_PATH)
    parts = tuple(rel_path.split("/"))
    if not all(_is_safe_name(part) for part in parts):
        raise ImageFolderError(_MSG_BAD_PATH)
    return parts


def _name_key(name: str) -> str:
    """Khóa so tên: không phân biệt hoa thường, cùng dạng Unicode (Mac lưu tên dạng NFD)."""
    return unicodedata.normalize("NFC", name).casefold()


def _match_disk_name(names: Iterable[str], name: str, time_is_up: Callable[[], bool]) -> str:
    """Tên trên ổ của ``name``, tìm trong danh sách tên của thư mục cha (T-076).

    Trùng hẳn thì là chính nó (ổ phân biệt hoa thường có thể có cả ``CongAI`` lẫn ``congai``: hai
    thư mục khác nhau). Không thì phải có đúng một tên trùng không phân biệt hoa thường và dạng
    Unicode (Mac không phân biệt cả hai, và có thể lưu tên dạng NFD).
    """
    key = _name_key(name)
    found: list[str] = []
    for on_disk in names:
        if on_disk == name:
            return name
        if _name_key(on_disk) == key:
            found.append(on_disk)
        if time_is_up():
            raise ImageFolderError(_MSG_SLOW)
    if len(found) != 1:
        raise ImageFolderError(_MSG_ALIAS if found else _MSG_NOT_FOUND)
    return found[0]


def _is_image_name(name: str) -> bool:
    # Đọc ``HEIC_ENABLED`` lúc gọi (test bật lại đường HEIC chỉ cần đổi công tắc).
    suffix = PurePosixPath(name).suffix.lower()
    return suffix in IMAGE_EXTENSIONS or (HEIC_ENABLED and suffix in HEIC_EXTENSIONS)


def _is_link_stat(st: os.stat_result) -> bool:
    """Kết quả ``lstat`` là symlink hoặc junction (hay reparse point khác trỏ đi chỗ khác)."""
    if stat.S_ISLNK(st.st_mode):
        return True
    attributes = getattr(st, "st_file_attributes", 0)  # chỉ có trên Windows
    if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        return bool(getattr(st, "st_reparse_tag", 0) & _REPARSE_NAME_SURROGATE)
    return False


def _is_hidden_stat(st: os.stat_result) -> bool:
    attributes = getattr(st, "st_file_attributes", 0)
    if attributes & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
        return True
    return bool(_UF_HIDDEN and getattr(st, "st_flags", 0) & _UF_HIDDEN)


def _same_file(a: os.stat_result, b: os.stat_result) -> bool:
    """Hai kết quả ``stat`` là cùng một mục trên ổ (ổ không có số inode thì không so được)."""
    if not a.st_ino or not b.st_ino:
        return True
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def _file_id(st: os.stat_result) -> tuple[int, int] | None:
    """Định danh của mục trên ổ (số ổ, số inode); ổ không có số inode thì ``None``."""
    return (st.st_dev, st.st_ino) if st.st_ino else None


# ----- giữ thư mục trong lúc quét (L1) ------------------------------------------------------
#
# Kiểm đường dẫn rồi mới ``scandir`` theo tên thì có khe: thư mục bị tráo thành junction ở giữa
# sẽ bị quét xuyên ra ngoài gốc. Cách đóng khe:
# - Mac/Linux: mở từng tầng từ gốc xuống bằng ``openat(fd_cha, tên, O_DIRECTORY | O_NOFOLLOW)``
#   rồi ``os.scandir(fd)``: quét đúng thư mục đã mở qua toàn thư mục thật, tráo tên sau đó không
#   còn tác dụng.
# - Windows: ``os.scandir`` không nhận fd. Mở handle thư mục (không đi theo reparse point) với
#   quyền đọc danh sách và KHÔNG cho chia sẻ quyền xóa: trong lúc giữ handle, Windows không cho
#   đổi tên hay xóa chính thư mục đó lẫn mọi thư mục cha (đã thử trên NTFS: lỗi 32 và 5). Rồi
#   hỏi chính handle đường dẫn thật của nó (``GetFinalPathNameByHandleW``): trùng từng chữ với
#   ``gốc/parts`` (``_same_win_path``) thì thư mục đang giữ nằm trong gốc và cả đường đi bị khóa
#   cho tới khi nhả.
# - Ổ không cho giữ thư mục (Windows, ổ lạ): kiểm cả đường đi trước và sau khi quét, so định danh.

_SCANDIR_BY_FD = os.scandir in os.supports_fd  # Mac/Linux có, Windows không
# Mở, ``stat`` một mục trong thư mục đã mở (``openat``, ``fstatat``): Mac/Linux có, Windows không.
_OPEN_BY_DIR_FD = os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd
_FILE_LIST_DIRECTORY = 0x0001
_FILE_READ_ATTRIBUTES = 0x0080
_FILE_SHARE_READ_WRITE = 0x0001 | 0x0002  # cố ý không có FILE_SHARE_DELETE (0x0004)
_OPEN_EXISTING = 3
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000  # cần để mở thư mục
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000  # mở chính junction, không đi theo
_FILE_ATTRIBUTE_TAG_INFO = 9  # FILE_INFO_BY_HANDLE_CLASS.FileAttributeTagInfo
_FINAL_PATH_CHARS = 32768


class _FileAttributeTagInfo(ctypes.Structure):
    _fields_ = [("FileAttributes", ctypes.c_uint32), ("ReparseTag", ctypes.c_uint32)]


@functools.cache
def _kernel32():  # chỉ gọi trên Windows
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL
    k32.GetFileInformationByHandleEx.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    k32.GetFileInformationByHandleEx.restype = wintypes.BOOL
    k32.GetFinalPathNameByHandleW.argtypes = [
        wintypes.HANDLE,
        wintypes.LPWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
    ]
    k32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
    k32.FindFirstFileW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.WIN32_FIND_DATAW)]
    k32.FindFirstFileW.restype = wintypes.HANDLE
    k32.FindClose.argtypes = [wintypes.HANDLE]
    k32.FindClose.restype = wintypes.BOOL
    return k32


def _win_open(path: Path, access: int) -> int | None:
    """Mở chính mục ``path`` trên Windows (tầng cuối là reparse point thì mở chính nó, không đi
    theo), không chia sẻ quyền xóa; trả fd (``os.close`` đóng luôn handle), hoặc None nếu không mở
    được. Mở hỏng thì mã lỗi Windows còn ở ``ctypes.get_last_error()`` (chỗ gọi cần mã lỗi thì đặt
    về 0 trước khi gọi, để mã lỗi của lần gọi trước không lẫn vào)."""
    import msvcrt

    k32 = _kernel32()
    handle = k32.CreateFileW(
        str(path),
        access,
        _FILE_SHARE_READ_WRITE,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT,
        None,
    )
    if handle in (None, 0, ctypes.c_void_p(-1).value):
        return None
    try:
        return msvcrt.open_osfhandle(handle, os.O_RDONLY)
    except OSError:
        k32.CloseHandle(handle)
        return None


@contextlib.contextmanager
def _win_hold_dir(path: Path) -> Iterator[int | None]:
    """Mở và giữ thư mục trên Windows; trả fd, hoặc None nếu ổ không cho mở kiểu này."""
    fd = _win_open(path, _FILE_LIST_DIRECTORY | _FILE_READ_ATTRIBUTES)
    try:
        yield fd
    finally:
        if fd is not None:
            os.close(fd)  # đóng luôn handle


def _win_handle_is_link(fd: int) -> bool:
    """Thư mục đang giữ là reparse point trỏ đi chỗ khác (junction, kể cả đặt tại chỗ)."""
    import msvcrt

    info = _FileAttributeTagInfo()
    ok = _kernel32().GetFileInformationByHandleEx(
        msvcrt.get_osfhandle(fd), _FILE_ATTRIBUTE_TAG_INFO, ctypes.byref(info), ctypes.sizeof(info)
    )
    if not ok:  # không hỏi được: có thuộc tính reparse là coi như liên kết (an toàn trước)
        attributes = getattr(os.fstat(fd), "st_file_attributes", 0)
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    if not info.FileAttributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        return False
    return bool(info.ReparseTag & _REPARSE_NAME_SURROGATE)


def _win_final_path(fd: int) -> str | None:
    """Đường dẫn thật của thư mục đang giữ (hỏi từ chính handle, không theo tên)."""
    import msvcrt

    buffer = ctypes.create_unicode_buffer(_FINAL_PATH_CHARS)
    length = _kernel32().GetFinalPathNameByHandleW(
        msvcrt.get_osfhandle(fd), buffer, _FINAL_PATH_CHARS, 0
    )
    if not 0 < length < _FINAL_PATH_CHARS:
        return None
    return buffer.value


def _win_handle_at(fd: int, path: Path) -> bool:
    """Mục đang mở (hỏi đường dẫn thật từ chính handle, không theo tên) đúng là ``path``.

    Mở theo đường dẫn thì Windows đi xuyên junction, symlink ở các tầng giữa: tầng giữa vừa bị tráo
    thì đường dẫn thật của handle nằm chỗ khác (SL-T063-2). ``path`` phải ghép từ gốc đã ``resolve``
    (cùng cách hỏi đường dẫn thật) và tên trên ổ (``_same_win_path``). Không hỏi được thì coi như
    không đúng (an toàn trước): ổ nào ``resolve(strict=True)`` được (``_resolve_inside``) thì ổ đó
    trả lời được câu hỏi này.
    """
    final = _win_final_path(fd)
    return final is not None and _same_win_path(final, path)


def _win_listed_name(path: Path) -> str:
    """Tên của mục cuối ``path`` do thư mục cha liệt kê ra (Windows, ``FindFirstFileW``).

    Hỏi thư mục cha đúng một mục: không đọc cả thư mục, không mở file (Drive "chỉ trực tuyến"
    không bị tải về). Ổ trả tên đã lưu (``cFileName``) cả khi ``resolve`` trả lại chữ đã gõ (ổ
    Google Drive for Desktop, LC-T076-1); thư mục bật phân biệt hoa thường thì chỉ khớp đúng chữ.
    Tên đã qua ``_is_safe_name`` nên không có ký tự đại diện (``*``, ``?``, ``<``, ``>``, ``"``);
    ổ còn khớp cả tên ngắn 8.3 (trả tên dài), chỗ gọi so khóa tên để loại.
    """
    from ctypes import wintypes

    k32 = _kernel32()
    data = wintypes.WIN32_FIND_DATAW()
    handle = k32.FindFirstFileW(str(path), ctypes.byref(data))
    if handle in (None, 0, ctypes.c_void_p(-1).value):
        missing = ctypes.get_last_error() in (_ERROR_FILE_NOT_FOUND, _ERROR_PATH_NOT_FOUND)
        raise ImageFolderError(_MSG_NOT_FOUND if missing else _MSG_UNREADABLE)
    k32.FindClose(handle)
    return data.cFileName


def _same_win_path(final: str, path: Path) -> bool:
    """Đường dẫn thật ``final`` (của một handle) trùng từng chữ với ``path`` (LC-T079-1).

    Không gộp hoa thường, dạng Unicode (NFC/NFD), ``ß``/``ss``, dấu Kelvin: ổ coi các tên đó là mục
    khác nhau (NTFS không gộp dạng Unicode; thư mục bật phân biệt hoa thường thì cả hoa thường),
    nên gộp là để lọt thư mục anh em tên trông y hệt. ``path`` ghép từ gốc đã ``resolve`` (cùng
    hàm hỏi đường dẫn thật) và tên trên ổ (``_disk_names``, tên trong danh sách thư mục): ổ trả
    đường dẫn thật theo tên đã lưu (NTFS) hay theo đúng chữ đã mở (Google Drive for Desktop) thì
    đều trùng. Chỉ bỏ tiền tố đường dẫn dài (``\\\\?\\``, ``\\\\?\\UNC\\``) và dấu ``\\`` cuối.
    """

    def plain(text: str) -> str:
        if text.startswith("\\\\?\\UNC\\"):
            text = "\\\\" + text[8:]
        elif text.startswith("\\\\?\\"):
            text = text[4:]
        return text.rstrip("\\")

    return plain(final) == plain(str(path))


def _posix_open_dir(root: Path, parts: tuple[str, ...]) -> int:
    """Mở thư mục ``gốc/parts`` từng tầng một, không đi theo liên kết nào (Mac/Linux).

    Cần quyền đọc danh sách mỗi tầng (thư mục chỉ có quyền "đi qua" thì không mở được, như khi
    quét). Lỗi ``OSError`` để chỗ gọi đổi thành câu báo (``_open_error``).
    """
    flags = os.O_RDONLY
    for name in ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC", "O_NONBLOCK"):
        flags |= getattr(os, name, 0)
    fd = os.open(root, flags)
    try:
        for part in parts:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
    except BaseException:
        os.close(fd)
        raise
    return fd


def _open_error(exc: OSError) -> ImageFolderError:
    """Câu báo cho lỗi khi mở thư mục từng tầng (``_posix_open_dir``) hay đọc tên trong đó.

    Các tầng vừa được kiểm là thư mục thật, nên ``ELOOP`` (một tầng là symlink) và ``ENOTDIR`` đều
    là thư mục vừa bị thay đổi, không phải "không có quyền": Linux trả ``ENOTDIR`` thay ``ELOOP``
    khi mở symlink bằng ``O_DIRECTORY | O_NOFOLLOW`` (SL-T063-5), và tầng vừa thành file cũng vậy.
    """
    if isinstance(exc, FileNotFoundError):
        return ImageFolderError(_MSG_NOT_FOUND)
    if isinstance(exc, PermissionError):
        return ImageFolderError(_MSG_UNREADABLE)
    return _ChangedError()


def _changed_while_resolving(exc: OSError | RuntimeError) -> bool:
    """Lỗi của ``resolve(strict=True)`` cho biết đường dẫn vừa bị tráo (LC-T079-3, SL-T079-L-1).

    ``_resolve_inside`` vừa ``lstat`` từng tầng, không thấy liên kết nào, nên ``resolve`` gặp liên
    kết là đường dẫn vừa bị thay đổi, không phải "không có quyền hoặc ổ đĩa vừa bị ngắt":

    - vòng liên kết: ``RuntimeError`` (Python 3.12), ELOOP, lỗi Windows 1921;
    - Mac/Linux: EINVAL (một tầng là symlink lúc ``resolve`` xem, thành thư mục lại lúc ``resolve``
      đọc đích của nó), ENOTDIR (một tầng vừa thành file).

    Lỗi Windows khác (ổ mạng, ổ vừa rút…) không xét theo ``errno``: Python đổi mọi lỗi Windows lạ
    thành EINVAL.
    """
    if isinstance(exc, RuntimeError):
        return True
    winerror = exc.winerror if os.name == "nt" else None  # mã lỗi Windows, chỉ Windows có
    if winerror is not None:
        return winerror == _ERROR_CANT_RESOLVE_FILENAME
    return exc.errno in (errno.EINVAL, errno.ELOOP, errno.ENOTDIR)


def _still_same_entry(path: Path, expected: os.stat_result) -> bool:
    """Mục ở ``path`` (``lstat``: tầng cuối không đi theo liên kết) vẫn là mục ``expected``.

    Chỉ dùng để chọn câu báo cho một lần từ chối: không còn, không hỏi được, là liên kết hay khác
    định danh đều là "không phải nó" (mục vừa ``lstat`` được ngay trước đó). Ổ không có số inode thì
    coi như vẫn là nó (``_same_file``), giữ câu báo cũ.
    """
    try:
        now = os.lstat(path)
    except OSError:
        return False
    return not _is_link_stat(now) and _same_file(now, expected)


def _levels_changed(root: Path, parts: tuple[str, ...], seen: list[os.stat_result]) -> bool:
    """Có tầng nào của ``gốc/parts`` vừa mất, thành liên kết hay thành mục khác so với ``seen``
    (``lstat`` từng tầng của vòng kiểm trong ``_resolve_inside``)."""
    return not all(
        _still_same_entry(root.joinpath(*parts[: depth + 1]), before)
        for depth, before in enumerate(seen)
    )


def _format_mb(size: int) -> str:
    return f"{size / (1024 * 1024):.1f}".replace(".", ",")


@dataclass(frozen=True)
class ImageRef:
    """Chỉ tới một ảnh: số thứ tự thư mục gốc (từ 0) và đường dẫn tương đối ``a/b/anh.jpg``.

    Tạo ``ImageRef`` từ dữ liệu ngoài (nháp đã lưu) là an toàn: giá trị sai bị từ chối ngay
    bằng ``ImageFolderError``. Đây mới là kiểm tra dạng chữ; ``ImageLibrary`` còn kiểm liên kết
    và vị trí thật trên ổ đĩa mỗi lần đọc.
    """

    root_index: int
    rel_path: str

    def __post_init__(self) -> None:
        if type(self.root_index) is not int or self.root_index < 0:
            raise ImageFolderError("Số thứ tự thư mục ảnh không hợp lệ.")
        parts = _parse_rel(self.rel_path, allow_empty=False)
        if not _is_image_name(parts[-1]):
            raise ImageFolderError(
                "Chỉ nhận ảnh JPEG, PNG, WebP hoặc HEIC/HEIF."
                if HEIC_ENABLED
                else "Chỉ nhận ảnh JPEG, PNG hoặc WebP (tạm chưa nhận ảnh HEIC của iPhone)."
            )

    @property
    def parts(self) -> tuple[str, ...]:
        return tuple(self.rel_path.split("/"))

    @property
    def name(self) -> str:
        return self.parts[-1]


@dataclass(frozen=True)
class RootInfo:
    """Một thư mục gốc trong ``IMAGE_FOLDERS``. ``label`` chỉ là tên thư mục cuối."""

    index: int
    label: str
    available: bool
    message: str = ""


@dataclass(frozen=True)
class ImageEntry:
    ref: ImageRef
    name: str
    size: int  # byte
    modified: float  # thời điểm sửa (giây kể từ epoch), dùng làm khóa cache ảnh xem trước
    # Định danh của file trên ổ (số ổ, số inode), chỉ ``stat_image`` điền: so hai lần hỏi xem có
    # phải cùng một file không (bản sao cùng cỡ, cùng giờ sửa vẫn khác định danh; LC-T076-3).
    # ``None``: không biết (kết quả quét, ổ không có số inode). Không tính khi so ``ImageEntry``.
    file_id: tuple[int, int] | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class SubFolder:
    rel_path: str  # tương đối so với thư mục gốc, dạng ``a/b``
    name: str


@dataclass(frozen=True)
class SkipCounts:
    """Số mục bị bỏ qua khi quét, để giao diện báo cho người dùng."""

    links: int = 0  # symlink, junction
    hidden: int = 0  # tên bắt đầu bằng dấu chấm, file ẩn/hệ thống
    bad_names: int = 0  # tên có ký tự lạ, tên thiết bị Windows, quá dài
    other_files: int = 0  # không phải ảnh được nhận (``.gif``, ``.txt``, ``.lnk``…)
    empty: int = 0  # file 0 byte
    too_large: int = 0  # quá giới hạn dung lượng
    unreadable: int = 0  # không có quyền đọc, ổ bị ngắt
    too_deep: int = 0  # thư mục con sâu hơn giới hạn tầng (chỉ khi quét cả cây)


@dataclass(frozen=True)
class FolderListing:
    """Kết quả xem một thư mục: thư mục con, một trang ảnh, và có còn nữa hay không."""

    root_index: int
    rel_dir: str
    subfolders: tuple[SubFolder, ...]
    images: tuple[ImageEntry, ...]  # chỉ trang đang xem
    total_images: int  # tổng số ảnh tìm thấy trong phạm vi ngân sách
    page: int
    page_size: int
    page_count: int
    truncated: bool  # hết ngân sách quét: còn mục chưa xem
    skipped: SkipCounts
    notice: str = ""  # câu báo tiếng Việt khi ``truncated``

    @property
    def has_next_page(self) -> bool:
        return self.page < self.page_count

    @property
    def has_previous_page(self) -> bool:
        return self.page > 1


class ImageLibrary:
    """Truy cập chỉ đọc vào các thư mục ảnh đã khai báo.

    Thư mục gốc được ``resolve`` lại mỗi lần dùng, nên USB cắm sau hay Google Drive chạy sau
    vẫn nhận mà không cần mở lại app.
    """

    def __init__(
        self,
        folders: Iterable[Path | str],
        *,
        max_file_bytes: int = MAX_IMAGE_BYTES,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        max_seconds: float = DEFAULT_MAX_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._folders = tuple(Path(folder) for folder in folders)
        self._max_file_bytes = max_file_bytes
        self._max_entries = max_entries
        self._max_seconds = max_seconds
        self._clock = clock

    @classmethod
    def from_settings(cls, settings, **kwargs) -> ImageLibrary:
        """Tạo từ ``Settings`` (``settings.image_folders`` đọc từ ``IMAGE_FOLDERS``)."""
        return cls(settings.image_folders, **kwargs)

    def __repr__(self) -> str:
        # Không in đường dẫn tuyệt đối (lỡ ``st.write`` hay ghi log cũng không lộ).
        return f"ImageLibrary({len(self._folders)} thư mục)"

    def __len__(self) -> int:
        return len(self._folders)

    # ----- thư mục gốc -------------------------------------------------------------------

    def roots(self) -> tuple[RootInfo, ...]:
        """Danh sách thư mục gốc, kèm trạng thái có dùng được trên máy này không."""
        infos = []
        for index, folder in enumerate(self._folders):
            label = folder.name or f"Thư mục ảnh {index + 1}"
            try:
                self._root(index)
            except ImageFolderError as exc:
                infos.append(RootInfo(index, label, available=False, message=str(exc)))
            else:
                infos.append(RootInfo(index, label, available=True))
        return tuple(infos)

    def _root(self, index: object) -> Path:
        if type(index) is not int or not 0 <= index < len(self._folders):
            raise ImageFolderError("Không có thư mục ảnh với số thứ tự này.")
        number = index + 1
        folder = self._folders[index]
        with contextlib.suppress(RuntimeError):  # không tìm được thư mục nhà
            folder = folder.expanduser()
        if not folder.is_absolute():
            raise ImageFolderError(
                f"Thư mục ảnh số {number} phải ghi đường dẫn đầy đủ trong IMAGE_FOLDERS."
            )
        try:
            root = folder.resolve(strict=True)
        except (OSError, RuntimeError):
            raise ImageFolderError(
                f"Chưa thấy thư mục ảnh số {number} trên máy này "
                "(USB chưa cắm hoặc Google Drive chưa chạy?)."
            ) from None
        if not root.is_dir():
            raise ImageFolderError(f"Thư mục ảnh số {number} không phải là thư mục.")
        return root

    def _resolve_inside(self, root: Path, parts: tuple[str, ...]) -> tuple[Path, os.stat_result]:
        """Ghép ``parts`` vào gốc, không đi qua liên kết, và chắc chắn vẫn nằm trong gốc.

        Trả (đường dẫn ``resolve`` trả, ``lstat`` mục cuối). Đường dẫn đó **chỉ để so chuỗi**, chỗ
        gọi không được mở, ``stat`` hay liệt kê nó (Lá Chắn T-080, Việc 4): trên Windows
        ``is_relative_to`` so theo chữ thường (dấu Kelvin thành ``k``), nên một tầng vừa bị tráo thì
        nó có thể nằm trong thư mục anh em tên trông y hệt gốc. Đọc, ``stat``, xem thư mục đi qua
        ``_disk_names``, ``_opened_stat``, ``_open_image``, ``_Scan`` (so đường dẫn thật từng chữ
        hay mở từng tầng).

        Vòng ``lstat`` vừa thấy mọi tầng là mục thật (không liên kết), tên an toàn (không ``..``),
        gốc đã ``resolve``: ``resolve`` ra ngoài gốc, hay ra một mục khác mục cuối vừa ``lstat``,
        chỉ vì một tầng vừa bị tráo thành liên kết, nên báo "vừa bị thay đổi" (SL-T080-L-1), vẫn từ
        chối (``_ChangedError`` là ``_LinkError``); thư mục vừa bị đổi tên (chữ đã gõ không còn trỏ
        tới mục) cũng vậy. Tên ngắn 8.3 của Windows (cùng mục, tên khác) vẫn là "tên ngắn hoặc tên
        khác".
        """
        current = root
        last: os.stat_result | None = None
        seen: list[os.stat_result] = []  # ``lstat`` từng tầng, để kiểm lại khi ``resolve`` lỗi 5
        for part in parts:
            current = current / part
            try:
                last = os.lstat(current)
            except FileNotFoundError:
                raise ImageFolderError(_MSG_NOT_FOUND) from None
            except OSError:
                raise ImageFolderError(_MSG_UNREADABLE) from None
            # ``lstat`` không đi theo symlink, junction. ``_is_link_stat`` bắt cả hai: nó đọc
            # reparse tag như ``Path.is_junction()`` nhưng không tốn thêm một lần ``lstat``.
            if _is_link_stat(last):
                raise _LinkError(_MSG_LINK)
            # Theo đúng luật của quét: quét bỏ qua mục ẩn/hệ thống (ví dụ ``$RECYCLE.BIN``)
            # thì ``ImageRef`` gõ sẵn cũng không đi qua được (L5).
            if _is_hidden_stat(last):
                raise ImageFolderError(_MSG_HIDDEN)
            seen.append(last)
        try:
            resolved = current.resolve(strict=True)
            if last is None:
                last = os.lstat(resolved)
        except FileNotFoundError:
            raise ImageFolderError(_MSG_NOT_FOUND) from None
        except (OSError, RuntimeError) as exc:
            # Lỗi Windows 5: không có quyền, hay mục đang chờ xóa (junction vừa bị xóa, SL-T080-1).
            # Tầng nào vừa mất, thành liên kết hay thành mục khác thì là vừa bị thay đổi.
            if _changed_while_resolving(exc) or (
                os.name == "nt"
                and isinstance(exc, OSError)
                and exc.winerror == _ERROR_ACCESS_DENIED
                and _levels_changed(root, parts, seen)
            ):
                raise _ChangedError() from None
            raise ImageFolderError(_MSG_UNREADABLE) from None
        if not resolved.is_relative_to(root):
            raise _ChangedError()  # vòng ``lstat`` vừa thấy không tầng nào là liên kết
        # Tên thật trên ổ phải trùng tên đã gõ (không phân biệt hoa thường). Chặn tên ngắn 8.3
        # của Windows (``SECRET~1`` cho ``.secret``): đi vòng luật tên và làm một file có hai
        # ``ImageRef`` (L5).
        actual = resolved.relative_to(root).parts
        if len(actual) != len(parts) or any(
            _name_key(a) != _name_key(b) for a, b in zip(actual, parts, strict=False)
        ):
            # Tên ngắn là tên khác của chính mục vừa ``lstat``: cả tên ``resolve`` trả lẫn chữ đã
            # gõ vẫn trỏ tới mục đó. ``resolve`` ra mục khác (hay mục không còn) là một tầng vừa
            # bị tráo; chữ đã gõ không còn trỏ tới mục là thư mục vừa bị đổi tên (SL-T082-2).
            # Hỏi mục theo tên ghép vào gốc, không theo ``resolved`` (có thể nằm trong thư mục anh
            # em của gốc).
            if _still_same_entry(root.joinpath(*actual), last) and _still_same_entry(current, last):
                raise ImageFolderError(_MSG_ALIAS)
            raise _ChangedError()
        return resolved, last

    def _disk_names(
        self, root: Path, parts: tuple[str, ...], last: os.stat_result
    ) -> tuple[str, ...]:
        """Tên trên ổ của ``parts`` (đã qua ``_resolve_inside``; ``last`` là ``lstat`` mục cuối).

        ``ImageRef`` trả ra phải theo tên trên ổ, không theo chữ người gọi gõ (T-076, LC-T055-1):
        thẻ ảnh đọc từ tên thư mục phân biệt hoa thường ("CongAI" là thư mục ảnh AI nhờ tách chữ
        hoa, "congai" thì không), còn ổ Windows, Mac thì không. Tên lấy từ thư mục cha từng tầng,
        không từ ``resolve`` (ổ Google Drive for Desktop của Windows trả lại đúng chữ đã gõ,
        LC-T076-1):

        - Windows: hỏi thư mục cha đúng mục đó (``_found_names``).
        - Mac/Linux: đọc tên trong thư mục cha (``_listed_names``).

        Không lấy được tên thì báo lỗi, không quay về chữ đã gõ. Rồi kiểm mục ở tên trên ổ đúng là
        mục ``last`` (so định danh): bị tráo giữa chừng thì báo lỗi, không trả tên của mục này kèm
        số liệu của mục khác (LC-T055-2).
        """
        if not parts:
            return parts
        if _NAMES_FROM_RESOLVE:
            real = self._found_names(root, parts)
        else:
            real = self._listed_names(root, parts)
        if len("/".join(real)) > MAX_REL_PATH_CHARS or not all(map(_is_safe_name, real)):
            raise ImageFolderError(_MSG_BAD_PATH)
        try:
            again = os.lstat(root.joinpath(*real))
        except FileNotFoundError:
            raise _ChangedError() from None
        except OSError:
            raise ImageFolderError(_MSG_UNREADABLE) from None
        if _is_link_stat(again) or not _same_file(again, last):
            raise _ChangedError()
        return real

    def _found_names(self, root: Path, parts: tuple[str, ...]) -> tuple[str, ...]:
        """Windows: tên trên ổ của từng phần, hỏi thư mục cha đúng mục đó từ gốc xuống (T-076).

        Mỗi tầng một lần hỏi ổ (``_win_listed_name``), không đọc cả thư mục. Cùng luật chọn tên như
        ``_listed_names`` (``_match_disk_name``): tên ổ trả về phải trùng hẳn, hoặc trùng không phân
        biệt hoa thường và dạng Unicode; tên ngắn 8.3 (ổ trả tên dài, khác khóa) bị từ chối.
        """
        real: list[str] = []
        for part in parts:
            listed = _win_listed_name(root.joinpath(*real, part))
            real.append(_match_disk_name((listed,), part, lambda: False))
        return tuple(real)

    def _listed_names(self, root: Path, parts: tuple[str, ...]) -> tuple[str, ...]:
        """Mac/Linux: tên trên ổ của từng phần, xem trong thư mục cha từ gốc xuống (T-076).

        Chỉ đọc tên, không ``stat``, không mở file. Không giới hạn số mục như khi quét (ảnh trong
        thư mục con của gốc hơn 5.000 mục vẫn kiểm được, LC-T055-3), chỉ giới hạn thời gian. Thư
        mục cha mở từng tầng không đi theo liên kết (``O_NOFOLLOW``), như khi quét.
        """
        deadline = self._clock() + self._max_seconds

        def time_is_up() -> bool:
            return self._clock() > deadline

        real: list[str] = []
        for part in parts:
            fd = None
            try:
                if _SCANDIR_BY_FD:
                    fd = _posix_open_dir(root, tuple(real))
                with os.scandir(root.joinpath(*real) if fd is None else fd) as entries:
                    names = (entry.name for entry in entries)
                    real.append(_match_disk_name(names, part, time_is_up))
            except OSError as exc:  # ELOOP, ENOTDIR: một tầng vừa bị tráo thành symlink
                raise _open_error(exc) from None
            finally:
                if fd is not None:
                    os.close(fd)
        return tuple(real)

    # ----- xem thư mục -------------------------------------------------------------------

    def list_folder(
        self,
        root_index: int,
        rel_dir: str = "",
        *,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        recursive: bool = False,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> FolderListing:
        """Xem một thư mục: thư mục con trực tiếp và một trang ảnh (sắp theo tên).

        ``recursive=True`` gom cả ảnh trong các thư mục con (tối đa ``max_depth`` tầng), ví dụ
        ảnh ở ``truoc/`` và ``sau/`` của một công trình. Không mở file ảnh nào khi quét (chỉ đọc
        tên và ``stat``), nên không làm Google Drive tải file "chỉ trực tuyến" về.

        ``rel_dir`` gõ khác hoa thường (hay khác dạng Unicode, trên Mac) vẫn mở được thư mục,
        nhưng ``FolderListing.rel_dir``, ``SubFolder.rel_path`` và ``ImageRef`` trả ra đều theo tên
        trên ổ (T-076), kể cả trên ổ trả lại chữ đã gõ khi ``resolve`` (LC-T076-1).
        """
        if type(page) is not int or page < 1:
            raise ImageFolderError("Số trang không hợp lệ.")
        if type(page_size) is not int or not 1 <= page_size <= MAX_PAGE_SIZE:
            raise ImageFolderError(f"Số ảnh mỗi trang phải từ 1 đến {MAX_PAGE_SIZE}.")
        if type(max_depth) is not int or max_depth < 0:
            raise ImageFolderError("Số tầng thư mục không hợp lệ.")
        root = self._root(root_index)
        parts = _parse_rel(rel_dir, allow_empty=True)
        _path, dir_stat = self._resolve_inside(root, parts)  # đường dẫn chỉ để so, không dùng
        if not stat.S_ISDIR(dir_stat.st_mode):
            raise ImageFolderError("Đây không phải là thư mục.")
        parts = self._disk_names(root, parts, dir_stat)

        scan = _Scan(
            root_index=root_index,
            max_file_bytes=self._max_file_bytes,
            max_entries=self._max_entries,
            deadline=self._clock() + self._max_seconds,
            clock=self._clock,
            recursive=recursive,
            max_depth=max_depth,
            root=root,
            verify=lambda dir_parts: self._resolve_inside(root, dir_parts),
        )
        scan.run(parts)

        images = sorted(scan.images, key=lambda e: (e.ref.rel_path.casefold(), e.ref.rel_path))
        subfolders = sorted(scan.subfolders, key=lambda s: (s.name.casefold(), s.name))
        total = len(images)
        page_count = max(1, math.ceil(total / page_size))
        page = min(page, page_count)
        start = (page - 1) * page_size

        notice = ""
        if scan.stop_reason == "entries":
            count = f"{self._max_entries:,}".replace(",", ".")  # 5.000 (chỉ đổi dấu trong số)
            notice = (
                f"Thư mục có rất nhiều mục: mới xem {count} mục đầu, còn nữa chưa xem. "
                "Hãy chọn một thư mục con nhỏ hơn."
            )
        elif scan.stop_reason == "time":
            notice = (
                f"Quét quá {self._max_seconds:g} giây nên đã tạm dừng, còn nữa chưa xem (ổ mạng "
                "hoặc Google Drive có thể đang chậm). Hãy chọn thư mục con hoặc bấm quét lại."
            )

        return FolderListing(
            root_index=root_index,
            rel_dir="/".join(parts),
            subfolders=tuple(subfolders),
            images=tuple(images[start : start + page_size]),
            total_images=total,
            page=page,
            page_size=page_size,
            page_count=page_count,
            truncated=scan.stop_reason is not None,
            skipped=scan.skip_counts(),
            notice=notice,
        )

    # ----- một ảnh -----------------------------------------------------------------------

    def _checked_file(self, ref: object) -> tuple[Path, os.stat_result, bool]:
        """Kiểm ``ref`` là file ảnh dùng được; trả (gốc, ``lstat``, ``resolve`` có trả đúng
        ``gốc/ref.parts`` từng chữ không).

        Không trả đường dẫn ``resolve`` trả: nó có thể nằm trong thư mục anh em của gốc (xem
        ``_resolve_inside``), chỉ để so, nên chỉ so ngay ở đây, chỗ gọi không thể lỡ mở hay ``stat``
        nó (Lá Chắn T-080, Việc 4). Đọc, ``stat`` ảnh đi theo gốc và tên (``_disk_names``,
        ``_opened_stat``, ``_open_image``).

        ``lstat`` đi theo chuỗi đường dẫn: một tầng giữa vừa bị tráo thành liên kết thì nó tả một
        mục ngoài thư mục ảnh. Nên kiểm hỏng thì câu báo tả mục lấy lại trong thư mục ảnh
        (``_opened_stat``, phải cùng định danh, không thì "vừa bị thay đổi"), không tả ``lstat``:
        câu báo không nói cỡ, loại của file ngoài thư mục ảnh (LC-T079-2).
        """
        if not isinstance(ref, ImageRef):
            raise ImageFolderError(_MSG_BAD_PATH)
        root = self._root(ref.root_index)
        path, lst = self._resolve_inside(root, ref.parts)
        exact = str(path) == str(root.joinpath(*ref.parts))
        with contextlib.suppress(ImageFolderError):
            self._check_file(lst)
            return root, lst, exact
        # Báo ngoài khối bắt lỗi ở trên, để câu báo không mang theo lỗi tả ``lstat``.
        real = self._disk_names(root, ref.parts, lst)
        self._check_file(self._opened_stat(root, real, lst))
        raise ImageFolderError(_MSG_IMAGE_CHANGED)  # mục trong thư mục ảnh dùng được: vừa đổi

    def _check_file(self, st: os.stat_result) -> None:
        """Mục ``st`` là file ảnh dùng được: file thường, không ẩn, cỡ trong giới hạn."""
        if not stat.S_ISREG(st.st_mode):
            raise ImageFolderError("Đây không phải là file ảnh.")
        if _is_hidden_stat(st):
            raise ImageFolderError("App không đọc file ẩn hoặc file hệ thống.")
        self._check_size(st.st_size)

    def _check_size(self, size: int) -> None:
        if size <= 0:
            raise ImageFolderError("File ảnh rỗng (0 byte).")
        if size > self._max_file_bytes:
            limit = _format_mb(self._max_file_bytes)
            raise ImageFolderError(f"Ảnh quá lớn ({_format_mb(size)} MB), tối đa {limit} MB.")

    def stat_image(self, ref: ImageRef) -> ImageEntry:
        """Kiểm một ảnh (ví dụ ảnh lưu trong nháp) còn dùng được không, không mở file.

        ``ImageEntry.ref`` theo tên trên ổ (T-076), như ``ImageRef`` của ``list_folder``: ``ref``
        gõ khác hoa thường (hay khác dạng Unicode, trên Mac) vẫn tìm ra ảnh, nhưng kết quả mang
        tên thật, kể cả trên ổ trả lại chữ đã gõ khi ``resolve`` (LC-T076-1). Dùng ``entry.ref``
        (không dùng ``ref`` đã đưa vào) làm khóa, để đọc thẻ ảnh.

        Số liệu (cỡ, giờ sửa, ``file_id``) lấy từ chính mục trong thư mục ảnh (``_opened_stat``),
        không từ ``lstat`` theo chuỗi đường dẫn (SL-T063-3).
        """
        root, lst, _exact = self._checked_file(ref)
        real = self._disk_names(root, ref.parts, lst)
        st = self._opened_stat(root, real, lst)
        if not stat.S_ISREG(st.st_mode) or _is_hidden_stat(st):
            raise ImageFolderError(_MSG_IMAGE_CHANGED)  # ``lstat`` vừa thấy file thường, không ẩn
        self._check_size(st.st_size)
        found = ref if real == ref.parts else ImageRef(ref.root_index, "/".join(real))
        return ImageEntry(
            ref=found,
            name=found.name,
            size=st.st_size,
            modified=st.st_mtime,
            file_id=_file_id(st),
        )

    def _opened_stat(
        self, root: Path, parts: tuple[str, ...], expected: os.stat_result
    ) -> os.stat_result:
        """Số liệu của mục ``gốc/parts`` lấy từ chính mục nằm trong thư mục ảnh (SL-T063-3).

        ``lstat`` theo chuỗi đường dẫn (``_resolve_inside``) đi xuyên một tầng giữa vừa bị tráo
        thành liên kết, nên không lấy số liệu từ đó. Không mở file để đọc (Drive "chỉ trực tuyến"
        không bị tải về):

        - Mac/Linux: mở thư mục cha từng tầng từ gốc (``_posix_open_dir``, ``O_NOFOLLOW``), rồi
          ``stat`` mục cuối trong chính thư mục đã mở, không đi theo symlink.
        - Windows: mở chính mục cuối chỉ để hỏi thuộc tính (như ``os.lstat`` của Python trên
          Windows), đường dẫn thật của handle phải trùng từng chữ với ``gốc/parts`` (``parts`` là
          tên trên ổ, ``_win_handle_at``), rồi lấy số liệu trên handle đó.

        Mục không được là liên kết, phải cùng định danh với ``expected`` (mục vừa kiểm theo đường
        dẫn): khác là bị tráo giữa chừng. Loại, cỡ do chỗ gọi kiểm trên số liệu trả về.
        """
        if _OPEN_BY_DIR_FD:
            try:
                fd = _posix_open_dir(root, parts[:-1])
            except OSError as exc:
                raise _open_error(exc) from None
            try:
                st = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                raise ImageFolderError(_MSG_NOT_FOUND) from None
            except OSError:
                raise ImageFolderError(_MSG_UNREADABLE) from None
            finally:
                os.close(fd)
        else:
            path = root.joinpath(*parts)
            ctypes.set_last_error(0)
            fd = _win_open(path, _FILE_READ_ATTRIBUTES)
            if fd is None:
                # Ổ báo không thấy mục (hay một thư mục trên đường đi) mà ``_disk_names`` vừa thấy:
                # mục vừa bị dời đi hay xóa, không phải "không có quyền" (SL-T080-1). Báo như bản
                # Mac/Linux của bước này.
                if ctypes.get_last_error() in (_ERROR_FILE_NOT_FOUND, _ERROR_PATH_NOT_FOUND):
                    raise ImageFolderError(_MSG_NOT_FOUND)
                raise ImageFolderError(_MSG_UNREADABLE)
            try:
                if not _win_handle_at(fd, path) or _win_handle_is_link(fd):
                    raise ImageFolderError(_MSG_IMAGE_CHANGED)
                st = os.fstat(fd)
            finally:
                os.close(fd)
        if _is_link_stat(st) or not _same_file(st, expected):
            raise ImageFolderError(_MSG_IMAGE_CHANGED)
        return st

    def _open_image(self, root: Path, parts: tuple[str, ...], path: Path) -> int:
        """Mở file ảnh ``gốc/parts`` (``path`` = ``gốc/parts``) để đọc; chắc chắn file đã mở nằm
        trong thư mục ảnh (SL-T063-2). Trả fd.

        - Mac/Linux: mở thư mục cha từng tầng từ gốc (``O_NOFOLLOW`` mỗi tầng), rồi mở file trong
          chính thư mục đó, cũng ``O_NOFOLLOW``: không tầng nào đi theo symlink.
        - Windows (``os`` không mở được file trong thư mục đã mở): mở theo ``path``, rồi hỏi đường
          dẫn thật của chính handle vừa mở; phải trùng từng chữ với ``gốc/parts`` (``parts`` viết
          đúng như ổ báo tên, xem ``read_image_bytes``; LC-T079-1), không thì một tầng vừa bị tráo
          thành junction (hay symlink) và file đã mở nằm chỗ khác.
        """
        flags = os.O_RDONLY
        names = ("O_BINARY", "O_NOINHERIT", "O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK", "O_NOCTTY")
        for name in names:
            # O_NOFOLLOW: file bị tráo thành symlink ngay trước khi mở thì báo lỗi.
            # O_NONBLOCK: file bị tráo thành FIFO thì không treo (file thường không bị ảnh hưởng).
            # O_NOCTTY: file bị tráo thành thiết bị đầu cuối thì không thành terminal của app.
            flags |= getattr(os, name, 0)
        if _OPEN_BY_DIR_FD:
            try:
                dir_fd = _posix_open_dir(root, parts[:-1])
            except OSError as exc:
                raise _open_error(exc) from None
            try:
                return os.open(parts[-1], flags, dir_fd=dir_fd)
            except OSError:
                raise ImageFolderError(_MSG_CANNOT_OPEN) from None
            finally:
                os.close(dir_fd)
        try:
            fd = os.open(path, flags)
        except OSError:
            raise ImageFolderError(_MSG_CANNOT_OPEN) from None
        if not _win_handle_at(fd, root.joinpath(*parts)):
            os.close(fd)
            raise ImageFolderError(_MSG_IMAGE_CHANGED)
        return fd

    def read_image_bytes(self, ref: ImageRef) -> bytes:
        """Đọc nguyên nội dung một ảnh (không quá giới hạn dung lượng).

        Trả bytes thay vì đường dẫn hay đối tượng file, để đường dẫn tuyệt đối không ra khỏi
        module. Chưa kiểm nội dung có đúng là ảnh không: việc đó của bước mở ảnh (T-046 mục 2).
        File mở qua ``_open_image`` (không đi theo chuỗi đường dẫn, SL-T063-2), phải đúng là file
        vừa kiểm (so định danh trên fd đã mở).
        """
        root, lst, exact = self._checked_file(ref)
        parts = ref.parts
        # Windows so đường dẫn thật của file đã mở với gốc và tên trên ổ, từng chữ (LC-T079-1).
        # ``resolve`` vừa trả đúng ``gốc/parts`` (``exact``; thường gặp: ``ref`` lấy từ danh sách
        # thư mục, hay ổ trả lại chữ đã mở) thì ổ báo tên đúng như ``parts``: khỏi hỏi lại tên từng
        # tầng (Google Drive: khoảng 8 ms mỗi ảnh).
        if not _OPEN_BY_DIR_FD and not exact:
            parts = self._disk_names(root, parts, lst)
        fd = self._open_image(root, parts, root.joinpath(*parts))
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            same_file = (opened.st_dev, opened.st_ino) == (lst.st_dev, lst.st_ino)
            if not stat.S_ISREG(opened.st_mode) or (lst.st_ino and not same_file):
                raise ImageFolderError(_MSG_IMAGE_CHANGED)
            self._check_size(opened.st_size)
            try:
                data = handle.read(self._max_file_bytes + 1)
            except OSError:
                raise ImageFolderError(_MSG_UNREADABLE) from None
        if len(data) > self._max_file_bytes:
            self._check_size(len(data))
        return data


class _Scan:
    """Một lần quét thư mục theo chiều rộng, dừng khi hết ngân sách số mục hoặc thời gian."""

    def __init__(
        self,
        *,
        root_index: int,
        max_file_bytes: int,
        max_entries: int,
        deadline: float,
        clock: Callable[[], float],
        recursive: bool,
        max_depth: int,
        root: Path,
        verify: Callable[[tuple[str, ...]], tuple[Path, os.stat_result]],
    ) -> None:
        self.root_index = root_index
        self.root = root  # gốc đã resolve
        self.verify = verify  # kiểm đường đi (không liên kết, nằm trong gốc), trả (path, lstat)
        self.max_file_bytes = max_file_bytes
        self.max_entries = max_entries
        self.deadline = deadline
        self.clock = clock
        self.recursive = recursive
        self.max_depth = max_depth
        self.images: list[ImageEntry] = []
        self.subfolders: list[SubFolder] = []
        self.examined = 0
        self.stop_reason: str | None = None  # None, "entries" hoặc "time"
        self.counts = dict.fromkeys(SkipCounts.__dataclass_fields__, 0)

    def skip_counts(self) -> SkipCounts:
        return SkipCounts(**self.counts)

    def _time_is_up(self) -> bool:
        if self.clock() > self.deadline:
            self.stop_reason = "time"
        return self.stop_reason is not None

    def _entries_used_up(self) -> bool:
        """Gọi khi **còn** mục chưa xem: đã xem đủ ngân sách thì dừng và báo "còn nữa"."""
        if self.examined >= self.max_entries:
            self.stop_reason = "entries"
        return self.stop_reason is not None

    def run(self, parts: tuple[str, ...]) -> None:
        pending: deque[tuple[tuple[str, ...], int]] = deque([(parts, 0)])
        while pending and not self._entries_used_up() and not self._time_is_up():
            dir_parts, depth = pending.popleft()
            try:
                children = self._scan_dir(dir_parts, depth)
            except _LinkError:
                if depth == 0:
                    raise
                self.counts["links"] += 1
                continue
            except ImageFolderError:
                if depth == 0:
                    raise
                self.counts["unreadable"] += 1
                continue
            pending.extend(children)

    def _scan_dir(self, parts: tuple[str, ...], depth: int) -> list[tuple[tuple[str, ...], int]]:
        """Quét một thư mục, không để khe giữa lúc kiểm và lúc đọc (L1, xem phần "giữ thư mục").

        Lỗi giữa chừng thì trả lại đúng trạng thái trước khi quét thư mục này (kết quả của nó
        bị bỏ hết), chỉ giữ số mục đã tiêu vào ngân sách.
        """
        path = self.root.joinpath(*parts)
        saved = (len(self.images), len(self.subfolders), dict(self.counts))
        try:
            if _SCANDIR_BY_FD:
                children = self._scan_by_fd(parts, depth)
            else:
                children = self._scan_held(path, parts, depth)
        except ImageFolderError:
            del self.images[saved[0] :]
            del self.subfolders[saved[1] :]
            self.counts = saved[2]
            raise
        return children

    def _scan_by_fd(self, parts: tuple[str, ...], depth: int) -> list[tuple[tuple[str, ...], int]]:
        try:
            fd = _posix_open_dir(self.root, parts)
        except OSError as exc:  # ELOOP, ENOTDIR: một tầng là symlink (SL-T063-5)
            raise _open_error(exc) from None
        try:
            return self._read_entries(fd, parts, depth)
        finally:
            os.close(fd)

    def _scan_held(
        self, path: Path, parts: tuple[str, ...], depth: int
    ) -> list[tuple[tuple[str, ...], int]]:
        with _win_hold_dir(path) as fd:
            final = None if fd is None else _win_final_path(fd)
            if fd is not None and final is not None:
                # ``parts`` là tên trên ổ (tên ``_disk_names`` trả, tên trong danh sách thư mục).
                if _win_handle_is_link(fd) or not _same_win_path(final, path):
                    raise _ChangedError()
                children = self._read_entries(path, parts, depth)
                if _win_handle_is_link(fd):  # bị đặt junction tại chỗ trong lúc quét
                    raise _ChangedError()
                return children
            # Không giữ được thư mục: kiểm cả đường đi trước và sau khi quét, so định danh.
            _path, expected = self.verify(parts)
            if not stat.S_ISDIR(expected.st_mode):
                raise _ChangedError()
            children = self._read_entries(path, parts, depth)
            if not _same_file(self.verify(parts)[1], expected):
                raise _ChangedError()
            return children

    def _read_entries(
        self, target: int | Path, parts: tuple[str, ...], depth: int
    ) -> list[tuple[tuple[str, ...], int]]:
        try:
            iterator = os.scandir(target)
        except FileNotFoundError:
            # Thư mục vừa được kiểm (giữ được, hay kiểm đường đi khi không giữ được) mà nay không
            # thấy: vừa bị dời đi hay xóa (SL-T080-2), không phải "không có quyền".
            raise _ChangedError() from None
        except OSError:
            raise ImageFolderError(
                "Không đọc được thư mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)."
            ) from None
        children = []
        with iterator:
            while not self._time_is_up():
                try:
                    entry = next(iterator)
                except StopIteration:
                    break
                except OSError:
                    self.counts["unreadable"] += 1
                    break
                # Lấy mục kế tiếp trước rồi mới kiểm ngân sách số mục: thư mục có đúng
                # ``max_entries`` mục không bị báo "còn nữa" (L4).
                if self._entries_used_up():
                    break
                self.examined += 1
                child = self._visit(entry, parts, depth)
                if child is not None:
                    children.append(child)
        return children

    def _visit(
        self, entry: os.DirEntry, dir_parts: tuple[str, ...], depth: int
    ) -> tuple[tuple[str, ...], int] | None:
        name = entry.name
        try:
            # ``is_junction`` phải kiểm riêng: ``os.scandir`` báo junction là thư mục thường.
            if entry.is_symlink() or entry.is_junction():
                self.counts["links"] += 1
                return None
            st = entry.stat(follow_symlinks=False)
        except OSError:
            self.counts["unreadable"] += 1
            return None
        if _is_link_stat(st):
            self.counts["links"] += 1
            return None
        if name.startswith(".") or _is_hidden_stat(st):
            self.counts["hidden"] += 1
            return None
        child_parts = (*dir_parts, name)
        rel_path = "/".join(child_parts)
        if not _is_safe_name(name) or len(rel_path) > MAX_REL_PATH_CHARS:
            self.counts["bad_names"] += 1
            return None
        if stat.S_ISDIR(st.st_mode):
            if depth == 0:
                self.subfolders.append(SubFolder(rel_path=rel_path, name=name))
            if not self.recursive:
                return None
            if depth + 1 > self.max_depth:
                self.counts["too_deep"] += 1
                return None
            return child_parts, depth + 1
        if not stat.S_ISREG(st.st_mode) or not _is_image_name(name):
            self.counts["other_files"] += 1
            return None
        if st.st_size <= 0:
            self.counts["empty"] += 1
            return None
        if st.st_size > self.max_file_bytes:
            self.counts["too_large"] += 1
            return None
        ref = ImageRef(self.root_index, rel_path)
        self.images.append(ImageEntry(ref=ref, name=name, size=st.st_size, modified=st.st_mtime))
        return None

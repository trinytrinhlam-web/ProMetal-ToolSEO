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
- Khi quét, thư mục được "giữ" để không bị tráo giữa lúc kiểm và lúc đọc (xem phần "giữ thư
  mục trong lúc quét").
- Chỉ nhận đuôi ảnh đã biết (``IMAGE_EXTENSIONS``) và file không quá ``MAX_IMAGE_BYTES``.
- Quét có ngân sách (số mục, số giây), phân trang; vượt ngân sách thì dừng và báo "còn nữa".
- Chỉ đọc: module không tạo, sửa, đổi tên hay xóa gì trong thư mục ảnh (quyết định 3A).
- Tên file, tên thư mục trả về là dữ liệu chưa tin cậy (góp ý Lá Chắn số 3): module chỉ trả
  nguyên tên, không diễn giải thành thẻ (việc của T-052); giao diện phải escape khi hiện.
"""

from __future__ import annotations

import contextlib
import ctypes
import functools
import math
import os
import stat
import time
import unicodedata
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

# JPEG, PNG, WebP, HEIC/HEIF (iPhone, quyết định 1A), AVIF. Không nhận GIF, BMP, TIFF, .lnk.
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif"})
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

_MSG_BAD_PATH = "Đường dẫn ảnh không hợp lệ."
_MSG_NOT_FOUND = (
    "Không tìm thấy ảnh hoặc thư mục này (có thể đã đổi tên, đã xóa hoặc chưa đồng bộ xong)."
)
_MSG_LINK = "Đường dẫn đi qua liên kết tắt (symlink/junction), app không đọc qua liên kết."
_MSG_OUTSIDE = "Đường dẫn nằm ngoài thư mục ảnh được phép."
_MSG_UNREADABLE = "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)."
_MSG_HIDDEN = "App không đọc thư mục hay file ẩn, file hệ thống."
_MSG_ALIAS = "Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục)."


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


def _is_image_name(name: str) -> bool:
    return PurePosixPath(name).suffix.lower() in IMAGE_EXTENSIONS


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
#   hỏi chính handle đường dẫn thật của nó (``GetFinalPathNameByHandleW``): trùng ``gốc/parts``
#   thì thư mục đang giữ nằm trong gốc và cả đường đi bị khóa cho tới khi nhả.
# - Ổ không cho giữ thư mục (Windows, ổ lạ): kiểm cả đường đi trước và sau khi quét, so định danh.

_SCANDIR_BY_FD = os.scandir in os.supports_fd  # Mac/Linux có, Windows không
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
    return k32


@contextlib.contextmanager
def _win_hold_dir(path: Path) -> Iterator[int | None]:
    """Mở và giữ thư mục trên Windows; trả fd, hoặc None nếu ổ không cho mở kiểu này."""
    import msvcrt

    k32 = _kernel32()
    handle = k32.CreateFileW(
        str(path),
        _FILE_LIST_DIRECTORY | _FILE_READ_ATTRIBUTES,
        _FILE_SHARE_READ_WRITE,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT,
        None,
    )
    fd = None
    if handle not in (None, 0, ctypes.c_void_p(-1).value):
        try:
            fd = msvcrt.open_osfhandle(handle, os.O_RDONLY)
        except OSError:
            k32.CloseHandle(handle)
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


def _path_key(path: str) -> str:
    """Khóa so đường dẫn Windows: bỏ tiền tố đường dẫn dài, không phân biệt hoa thường."""
    if path.startswith("\\\\?\\UNC\\"):
        path = "\\\\" + path[8:]
    elif path.startswith("\\\\?\\"):
        path = path[4:]
    return _name_key(path.rstrip("\\"))


def _posix_open_dir(root: Path, parts: tuple[str, ...]) -> int:
    """Mở thư mục ``gốc/parts`` từng tầng một, không đi theo liên kết nào (Mac/Linux)."""
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
            raise ImageFolderError("Chỉ nhận ảnh JPEG, PNG, WebP, HEIC/HEIF hoặc AVIF.")

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
        """Ghép ``parts`` vào gốc, không đi qua liên kết, và chắc chắn vẫn nằm trong gốc."""
        current = root
        last: os.stat_result | None = None
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
        try:
            resolved = current.resolve(strict=True)
            if last is None:
                last = os.lstat(resolved)
        except FileNotFoundError:
            raise ImageFolderError(_MSG_NOT_FOUND) from None
        except (OSError, RuntimeError):
            raise ImageFolderError(_MSG_UNREADABLE) from None
        if not resolved.is_relative_to(root):
            raise _LinkError(_MSG_OUTSIDE)
        # Tên thật trên ổ phải trùng tên đã gõ (không phân biệt hoa thường). Chặn tên ngắn 8.3
        # của Windows (``SECRET~1`` cho ``.secret``): đi vòng luật tên và làm một file có hai
        # ``ImageRef`` (L5).
        actual = resolved.relative_to(root).parts
        if len(actual) != len(parts) or any(
            _name_key(a) != _name_key(b) for a, b in zip(actual, parts, strict=False)
        ):
            raise ImageFolderError(_MSG_ALIAS)
        return resolved, last

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
        """
        if type(page) is not int or page < 1:
            raise ImageFolderError("Số trang không hợp lệ.")
        if type(page_size) is not int or not 1 <= page_size <= MAX_PAGE_SIZE:
            raise ImageFolderError(f"Số ảnh mỗi trang phải từ 1 đến {MAX_PAGE_SIZE}.")
        if type(max_depth) is not int or max_depth < 0:
            raise ImageFolderError("Số tầng thư mục không hợp lệ.")
        root = self._root(root_index)
        parts = _parse_rel(rel_dir, allow_empty=True)
        directory, dir_stat = self._resolve_inside(root, parts)
        if not stat.S_ISDIR(dir_stat.st_mode):
            raise ImageFolderError("Đây không phải là thư mục.")

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

    def _checked_file(self, ref: object) -> tuple[Path, os.stat_result]:
        if not isinstance(ref, ImageRef):
            raise ImageFolderError(_MSG_BAD_PATH)
        root = self._root(ref.root_index)
        path, lst = self._resolve_inside(root, ref.parts)
        if not stat.S_ISREG(lst.st_mode):
            raise ImageFolderError("Đây không phải là file ảnh.")
        if _is_hidden_stat(lst):
            raise ImageFolderError("App không đọc file ẩn hoặc file hệ thống.")
        self._check_size(lst.st_size)
        return path, lst

    def _check_size(self, size: int) -> None:
        if size <= 0:
            raise ImageFolderError("File ảnh rỗng (0 byte).")
        if size > self._max_file_bytes:
            limit = _format_mb(self._max_file_bytes)
            raise ImageFolderError(f"Ảnh quá lớn ({_format_mb(size)} MB), tối đa {limit} MB.")

    def stat_image(self, ref: ImageRef) -> ImageEntry:
        """Kiểm một ảnh (ví dụ ảnh lưu trong nháp) còn dùng được không, không mở file."""
        _path, lst = self._checked_file(ref)
        return ImageEntry(ref=ref, name=ref.name, size=lst.st_size, modified=lst.st_mtime)

    def read_image_bytes(self, ref: ImageRef) -> bytes:
        """Đọc nguyên nội dung một ảnh (không quá giới hạn dung lượng).

        Trả bytes thay vì đường dẫn hay đối tượng file, để đường dẫn tuyệt đối không ra khỏi
        module. Chưa kiểm nội dung có đúng là ảnh không: việc đó của bước mở ảnh (T-046 mục 2).
        """
        path, lst = self._checked_file(ref)
        flags = os.O_RDONLY
        for name in ("O_BINARY", "O_NOINHERIT", "O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK"):
            # O_NOFOLLOW: file bị tráo thành symlink ngay trước khi mở thì báo lỗi.
            # O_NONBLOCK: file bị tráo thành FIFO thì không treo (file thường không bị ảnh hưởng).
            flags |= getattr(os, name, 0)
        try:
            fd = os.open(path, flags)
        except OSError:
            raise ImageFolderError(
                "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)."
            ) from None
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            same_file = (opened.st_dev, opened.st_ino) == (lst.st_dev, lst.st_ino)
            if not stat.S_ISREG(opened.st_mode) or (lst.st_ino and not same_file):
                raise ImageFolderError("Ảnh vừa bị thay đổi trong lúc đọc, hãy thử lại.")
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
        except FileNotFoundError:
            raise ImageFolderError(_MSG_NOT_FOUND) from None
        except (NotADirectoryError, PermissionError):
            raise ImageFolderError(_MSG_UNREADABLE) from None
        except OSError:  # ELOOP: một tầng là symlink
            raise _ChangedError() from None
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
                if _win_handle_is_link(fd) or _path_key(final) != _path_key(str(path)):
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

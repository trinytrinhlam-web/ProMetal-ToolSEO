"""Kiểm file khóa tài khoản dịch vụ Google (service account) trước khi dùng (T-097).

Thiết kế T-094 mục 2.1, điều kiện Lá Chắn LC-T094-11, -12, -14. File khóa JSON cho ai có nó
đọc/sửa mọi Google Sheet đã chia sẻ cho tài khoản dịch vụ, nên trước **mỗi** lần tạo client
Sheets (``SheetsClient.from_settings``) app kiểm lại từ đầu:

- Đường dẫn tuyệt đối, có thật. So **đường dẫn thật** (``resolve(strict=True)``, đi theo symlink,
  junction) và cả đường dẫn đã gõ: từ chối nếu nằm trong thư mục dự án (``.gitignore`` chỉ chặn tên
  có chữ ``service-account``; file Google tải về tên kiểu ``ten-project-1a2b3c.json`` sẽ lọt vào
  git) hay trong một thư mục ảnh ``IMAGE_FOLDERS`` (thường là thư mục Drive đồng bộ).
- Đường dẫn có đoạn của thư mục đồng bộ (Google Drive, OneDrive, Dropbox, iCloud): Cảnh báo.
- Mở **một lần** rồi đọc từ chính handle đó: file thường (``fstat``), ≤ 64 KB, đúng file đã kiểm
  vị trí (cùng thiết bị, cùng số file). Mac/Linux: người khác đọc được thì Cảnh báo kèm
  ``chmod 600``.
- JSON là object, không trùng khóa; ``type == "service_account"``; ``client_email`` đuôi
  ``.iam.gserviceaccount.com``; ``private_key`` dạng PEM; ``token_uri`` **đúng**
  ``https://oauth2.googleapis.com/token`` và ``universe_domain`` trống hoặc ``googleapis.com``
  (``google-auth`` gửi lệnh xin mã tới ``token_uri`` lấy nguyên văn từ file, không kiểm).
- Xác thực **chỉ** bằng ``Credentials.from_service_account_info`` với dict đã kiểm (chỉ các
  trường cần) và đúng một phạm vi ``SHEETS_SCOPE``. Không ``google.auth.default()`` (không đọc
  ``GOOGLE_APPLICATION_CREDENTIALS``, cấu hình ``gcloud``, máy chủ metadata), không
  ``with_subject``, không phạm vi Drive.

Mọi câu báo là câu cố định: không chép nội dung file, đường dẫn đầy đủ hay lời của thư viện
(``from None``). Đối tượng ``ServiceAccount`` chỉ lộ email dịch vụ (cần để chia sẻ Sheet) và
**tên** file; ``repr`` không có khóa, email hay đường dẫn. Mã truy cập chỉ nằm trong bộ nhớ.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import stat
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from seo_app import config

SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
TOKEN_URI = "https://oauth2.googleapis.com/token"
UNIVERSE_DOMAIN = "googleapis.com"
SERVICE_ACCOUNT_TYPE = "service_account"
MAX_KEY_FILE_BYTES = 64 * 1024
MAX_PRIVATE_KEY_CHARS = 8 * 1024

# Email tài khoản dịch vụ: "<tên>@<mã-project>.iam.gserviceaccount.com" (mã project kiểu cũ có
# thể có dấu chấm, ví dụ "example.com:..." đổi thành "example.com").
_EMAIL = re.compile(r"[a-z0-9][a-z0-9-]{0,62}@[a-z0-9][a-z0-9.-]{0,98}\.iam\.gserviceaccount\.com")
_KEY_ID = re.compile(r"[A-Za-z0-9_-]{1,100}")
# Dấu đầu/cuối khối PEM, ghép từ hai nửa để bộ quét bí mật không nhận nhầm code là khóa thật.
_PEM_BEGIN = "-----BEGIN " + "PRIVATE KEY-----"
_PEM_END = "-----END " + "PRIVATE KEY-----"
# Đoạn đường dẫn của thư mục đồng bộ lên mây (so chữ thường, NFC). Google Drive for Desktop gắn
# ổ ảo có «My Drive», «Shared drives», «Other computers» (tiếng Việt: «Drive của tôi», «Bộ nhớ
# dùng chung», «Máy tính khác»; tên tiếng Việt của hai thư mục sau chưa xác minh trên máy chủ dự
# án, SL-T097-4).
_SYNC_MARKERS = (
    "google drive",
    "googledrive",
    "my drive",
    "drive của tôi",
    "shared drives",
    "other computers",
    "bộ nhớ dùng chung",
    "drive dùng chung",
    "máy tính khác",
    "onedrive",
    "dropbox",
    "icloud",
    "clouddocs",
)

_MSG_MISSING = "Chưa khai báo file khóa Google (GOOGLE_SERVICE_ACCOUNT_FILE trong .env)."
_MSG_NOT_ABSOLUTE = (
    "Đường dẫn file khóa Google phải là đường dẫn đầy đủ (ví dụ C:/Users/ten-ban/bi-mat/khoa.json)."
)
_MSG_NOT_FOUND = "Không tìm thấy file khóa Google theo đường dẫn trong GOOGLE_SERVICE_ACCOUNT_FILE."
_MSG_IN_PROJECT = (
    "File khóa Google đang nằm trong thư mục phần mềm: dễ lọt lên GitHub. Hãy chuyển file ra "
    "ngoài (ví dụ một thư mục «bi-mat» riêng), sửa GOOGLE_SERVICE_ACCOUNT_FILE rồi thử lại."
)
_MSG_IN_IMAGES = (
    "File khóa Google đang nằm trong thư mục ảnh (thường được đồng bộ lên mây). Hãy chuyển file "
    "ra ngoài, sửa GOOGLE_SERVICE_ACCOUNT_FILE rồi thử lại."
)
_MSG_NOT_FILE = "Đường dẫn trong GOOGLE_SERVICE_ACCOUNT_FILE không phải là một file thường."
_MSG_TOO_BIG = (
    f"File khóa Google lớn bất thường (quá {MAX_KEY_FILE_BYTES // 1024} KB). Hãy tải lại file "
    "khóa JSON từ Google Cloud."
)
_MSG_UNREADABLE = "Không đọc được file khóa Google. Kiểm tra file còn đó và quyền đọc file."
_MSG_CHANGED = "File khóa Google vừa bị đổi trong lúc đọc. Thử lại."
_MSG_NOT_JSON = (
    "File khóa Google không phải JSON đọc được. Hãy tải lại file khóa JSON từ Google Cloud."
)
_MSG_NOT_SA = (
    "File không phải khóa tài khoản dịch vụ Google (cần loại «service_account»). Hãy tải khóa "
    "JSON của tài khoản dịch vụ trong Google Cloud."
)
_MSG_BAD_EMAIL = "File khóa Google thiếu hoặc sai email tài khoản dịch vụ (client_email)."
_MSG_BAD_KEY = (
    "Khóa riêng trong file khóa Google không đọc được (private_key). Hãy tải lại file khóa JSON."
)
_MSG_BAD_TOKEN_URI = (
    "File khóa Google ghi địa chỉ lấy mã truy cập (token_uri) không phải của Google, nên phần "
    "mềm không dùng file này. Hãy tải lại file khóa JSON từ Google Cloud."
)
_MSG_BAD_UNIVERSE = (
    "File khóa Google dành cho hệ thống Google khác (universe_domain), phần mềm không dùng. Hãy "
    "tải lại file khóa JSON từ Google Cloud."
)
_MSG_LIBRARY = "Thiếu thư viện google-auth hoặc sai phiên bản. Chạy lại run.bat / run.command."
_WARN_SYNC = (
    "File khóa Google đang nằm trong thư mục đồng bộ lên mây (Google Drive, OneDrive, Dropbox, "
    "iCloud). Nên chuyển ra một thư mục chỉ có trên máy này."
)
_WARN_MODE = (
    "Người khác trên máy này đọc được file khóa Google «{name}». Mở Terminal, chạy: "
    "chmod 600 <đường dẫn file khóa>"
)


class ServiceAccountError(ValueError):
    """File khóa Google không dùng được. ``str(err)`` là câu tiếng Việt cố định (không chép nội
    dung file, đường dẫn đầy đủ hay lời của thư viện)."""


@dataclass(frozen=True, repr=False)
class ServiceAccount:
    """Tài khoản dịch vụ đã kiểm. ``credentials``: đối tượng của ``google-auth`` (chỉ client Sheets
    dùng, không in, không lưu). ``in_sync_folder``: file khóa nằm trong thư mục đồng bộ lên mây
    (dấu hiệu cho giao diện; câu Cảnh báo tương ứng có trong ``warnings``, SL-T097-4)."""

    email: str
    file_name: str
    warnings: tuple[str, ...]
    credentials: Any = field(compare=False)
    in_sync_folder: bool = False

    def __repr__(self) -> str:
        # Không email, không đường dẫn, không khóa (LC-T094-12).
        return f"ServiceAccount(file_name={self.file_name!r}, warnings={len(self.warnings)})"


def load_service_account(
    path: Path | str | None,
    *,
    image_folders: Iterable[Path | str] = (),
    project_root: Path | None = None,
) -> ServiceAccount:
    """Đọc và kiểm file khóa ``path``; trả ``ServiceAccount`` hoặc ném ``ServiceAccountError``.

    ``image_folders``: gốc các thư mục ảnh (``Settings.image_folders``). ``project_root``: thư mục
    dự án (mặc định ``config.PROJECT_ROOT``, test đổi được).
    """
    if path is None or not str(path).strip():
        raise ServiceAccountError(_MSG_MISSING)
    given = Path(str(path).strip()).expanduser()
    if not given.is_absolute():
        # Đường tương đối tính từ thư mục đang chạy app, tức thường là chính thư mục dự án.
        raise ServiceAccountError(_MSG_NOT_ABSOLUTE)
    try:
        real = given.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):  # không có, vòng symlink, ký tự NUL…
        raise ServiceAccountError(_MSG_NOT_FOUND) from None

    root = config.PROJECT_ROOT if project_root is None else Path(project_root)
    candidates = (given, real)
    if any(_is_within(candidate, root) for candidate in candidates):
        raise ServiceAccountError(_MSG_IN_PROJECT)
    for folder in image_folders:
        if any(_is_within(candidate, Path(folder).expanduser()) for candidate in candidates):
            raise ServiceAccountError(_MSG_IN_IMAGES)

    warnings: list[str] = []
    synced = any(_in_sync_folder(candidate) for candidate in candidates)
    if synced:
        warnings.append(_WARN_SYNC)

    data, mode = _read_key_file(real)
    if os.name != "nt" and mode & 0o077:
        warnings.append(_WARN_MODE.format(name=real.name))
    info = _parse_key(data)
    credentials = _credentials(info)
    return ServiceAccount(
        email=info["client_email"],
        file_name=real.name,
        warnings=tuple(warnings),
        credentials=credentials,
        in_sync_folder=synced,
    )


def _norm(path: Path) -> str:
    """Đường dẫn tuyệt đối dạng chuẩn để so (Windows: chữ thường, dấu "\\")."""
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def _is_within(candidate: Path, base: Path) -> bool:
    """``candidate`` là ``base`` hay nằm trong ``base``.

    So hai cách, một cách khớp là đủ:

    1. **Danh tính thư mục** (SL-T097-3): ``base`` hay một thư mục cha của ``candidate`` có cùng
       ``(st_dev, st_ino)``. Bắt mọi cách viết cùng một thư mục: ``\\\\?\\D:\\…``,
       ``\\\\?\\Volume{…}\\…``, ``\\\\?\\GLOBALROOT\\??\\D:\\…``, ``\\\\localhost\\D$\\…``,
       symlink, junction, chữ hoa thường trên Mac.
    2. Chuỗi đường dẫn chuẩn hóa (``normcase``), cả ``base`` gõ và ``base`` thật: khi hệ thống
       không cho số file (``st_ino == 0``, ví dụ vài ổ FAT, ổ mạng) hay thư mục chưa có.
    """
    if _inside_by_identity(candidate, base):
        return True
    bases = {_norm(base)}
    with contextlib.suppress(OSError, RuntimeError, ValueError):
        bases.add(_norm(base.resolve(strict=False)))
    target = _norm(candidate)
    for item in bases:
        prefix = item if item.endswith(os.sep) else item + os.sep
        if target == item or target.startswith(prefix):
            return True
    return False


def _identity(path: Path) -> tuple[int, int] | None:
    """``(st_dev, st_ino)`` của ``path`` (đi theo symlink, junction); ``None`` khi không đọc được
    hay hệ thống không cho số file (``st_ino == 0``, như ``seo_app/images/folders.py``)."""
    try:
        info = os.stat(path)
    except (OSError, ValueError):
        return None
    return (info.st_dev, info.st_ino) if info.st_ino else None


def _inside_by_identity(candidate: Path, base: Path) -> bool:
    """Một trong các thư mục cha của đường **thật** của ``candidate`` (kể cả chính nó) là đúng thư
    mục ``base``.

    Đi ngược theo đường thật (``resolve``: không còn ``..``, symlink, junction), không theo chữ của
    đường gõ: «<dự án>\\..\\ngoai\\k.json» không có thư mục cha nào là thư mục dự án (Soi Lỗi
    SL-T097-5). Hai đường thật ở **hai ổ có chữ khác nhau** (``H:\\``, ``I:\\``) thì không tin danh
    tính: ổ Google Drive for Desktop cho mọi ổ cùng số nhận dạng thư mục (Soi Lỗi T-097, ghi nhận
    lượt 2 số 1). Cách viết khác của cùng một ổ (``\\\\localhost\\D$\\…``, ``\\\\?\\Volume{…}``)
    vẫn so danh tính (SL-T097-3)."""
    target = _identity(base)
    if target is None:
        return False
    try:
        current = candidate.resolve(strict=False)
        base_drive = base.resolve(strict=False).drive
    except (OSError, RuntimeError, ValueError):
        return False
    if _other_drive_letter(current.drive, base_drive):
        return False
    for _ in range(512):  # đường dẫn sâu bất thường: dừng (phép so chuỗi vẫn chạy)
        if _identity(current) == target:
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent
    return False


def _other_drive_letter(first: str, second: str) -> bool:
    """Hai ổ đều viết bằng chữ ổ (``C:``, ``H:``) và khác chữ: chắc chắn là hai ổ khác nhau."""
    letters = [drive.casefold() for drive in (first, second)]
    return all(len(d) == 2 and d[1] == ":" for d in letters) and letters[0] != letters[1]


def _in_sync_folder(path: Path) -> bool:
    parts = [
        unicodedata.normalize("NFC", part).casefold()
        for part in Path(os.path.normpath(path)).parts
    ]
    return any(marker in part for part in parts for marker in _SYNC_MARKERS)


def _read_key_file(real: Path) -> tuple[bytes, int]:
    """Mở ``real`` một lần, kiểm bằng ``fstat`` trên chính handle, đọc tối đa 64 KB."""
    if not real.is_file():  # chỉ để câu báo rõ hơn; chốt thật là fstat bên dưới
        raise ServiceAccountError(_MSG_NOT_FILE)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(real, flags)
    except (OSError, ValueError):
        raise ServiceAccountError(_MSG_UNREADABLE) from None
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ServiceAccountError(_MSG_NOT_FILE)
        if opened.st_size > MAX_KEY_FILE_BYTES:
            raise ServiceAccountError(_MSG_TOO_BIG)
        try:
            now = os.stat(real)
        except (OSError, ValueError):
            raise ServiceAccountError(_MSG_UNREADABLE) from None
        if (now.st_dev, now.st_ino) != (opened.st_dev, opened.st_ino):
            # File ở đường đã kiểm vị trí không còn là file vừa mở (bị thay giữa chừng).
            raise ServiceAccountError(_MSG_CHANGED)
        chunks: list[bytes] = []
        total = 0
        while total <= MAX_KEY_FILE_BYTES:
            chunk = os.read(fd, MAX_KEY_FILE_BYTES + 1 - total)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if total > MAX_KEY_FILE_BYTES:
            raise ServiceAccountError(_MSG_TOO_BIG)
        return b"".join(chunks), opened.st_mode
    except OSError:
        raise ServiceAccountError(_MSG_UNREADABLE) from None
    finally:
        os.close(fd)


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _parse_key(data: bytes) -> dict[str, str]:
    """Kiểm nội dung file khóa; trả dict **chỉ** gồm các trường ``google-auth`` cần."""
    try:
        raw = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, ValueError, RecursionError):
        # Không bao giờ dùng exc.doc, exc.args: có thể chứa nội dung file (LC-T094-2).
        raise ServiceAccountError(_MSG_NOT_JSON) from None
    if not isinstance(raw, dict) or raw.get("type") != SERVICE_ACCOUNT_TYPE:
        raise ServiceAccountError(_MSG_NOT_SA)
    email = raw.get("client_email")
    if not isinstance(email, str) or len(email) > 200 or not _EMAIL.fullmatch(email):
        raise ServiceAccountError(_MSG_BAD_EMAIL)
    key = raw.get("private_key")
    if not _looks_like_pem(key):
        raise ServiceAccountError(_MSG_BAD_KEY)
    if raw.get("token_uri") != TOKEN_URI:
        raise ServiceAccountError(_MSG_BAD_TOKEN_URI)
    if raw.get("universe_domain") not in (None, "", UNIVERSE_DOMAIN):
        raise ServiceAccountError(_MSG_BAD_UNIVERSE)
    key_id = raw.get("private_key_id")
    if key_id is not None and not (isinstance(key_id, str) and _KEY_ID.fullmatch(key_id)):
        raise ServiceAccountError(_MSG_BAD_KEY)
    info = {
        "type": SERVICE_ACCOUNT_TYPE,
        "client_email": email,
        "private_key": key,
        "token_uri": TOKEN_URI,
        "universe_domain": UNIVERSE_DOMAIN,
    }
    if key_id:
        info["private_key_id"] = key_id
    return info


def _looks_like_pem(key: object) -> bool:
    if not isinstance(key, str) or len(key) > MAX_PRIVATE_KEY_CHARS or "\x00" in key:
        return False
    body = key.strip()
    return body.startswith(_PEM_BEGIN) and body.endswith(_PEM_END)


def _credentials(info: dict[str, str]) -> Any:
    """Đối tượng xác thực của ``google-auth`` từ dict đã kiểm, đúng một phạm vi Sheets."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        raise ServiceAccountError(_MSG_LIBRARY) from None
    try:
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=[SHEETS_SCOPE]
        )
    except Exception:  # khóa PEM hỏng, thư viện lệch phiên bản…: lời thư viện có thể chép dữ liệu
        raise ServiceAccountError(_MSG_BAD_KEY) from None
    if getattr(credentials, "service_account_email", None) != info["client_email"]:
        raise ServiceAccountError(_MSG_LIBRARY)
    return credentials

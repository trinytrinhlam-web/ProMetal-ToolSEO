"""Ghi/xóa khóa API AI trong file ``.env`` từ giao diện app (phiếu T-020).

Khóa vẫn chỉ nằm trong ``.env`` (quyết định đã chốt); module này chỉ là chỗ ghi vào đó, an
toàn hơn sửa file bằng tay:

- Chỉ nhận đúng ba biến ``ALLOWED_KEYS``. Không biến nào khác (ví dụ ``APP_PASSWORD_HASH``)
  sửa được qua ``set_api_key``, ``clear_api_key``.
- Giá trị bị kiểm tra chặt (``validate_key_value``): không xuống dòng, không ký tự điều khiển,
  không dấu nháy, ``#``, ``$``, dấu cách… nên không ai chèn thêm được một biến khác vào file.
- Mọi dòng khác, chú thích và thứ tự trong ``.env`` được giữ nguyên.
- Ghi ra file tạm cùng thư mục rồi thay thế (``os.replace``); Mac/Linux đặt quyền ``600``.

Riêng ``GOOGLE_SHEET_ID`` (T-097, LC-T094-15) có hàm ghi riêng ``set_google_sheet_id`` với bộ
kiểm riêng ``validate_sheet_id`` (chỉ ``[A-Za-z0-9_-]{25,100}``, chặt hơn khóa AI). Đường dẫn
file khóa Google (``GOOGLE_SERVICE_ACCOUNT_FILE``) **không** ghi được từ giao diện.

Mã băm mật khẩu ``APP_PASSWORD_HASH`` chỉ ghi qua ``set_password_hash``, cho script
``set_password`` (T-104), không từ giao diện; ``password_hash_overridden`` cho biết biến môi trường
của máy có đè ``.env`` không (T-105).

Không hàm nào ở đây trả về, in ra hay ghi log giá trị khóa (security.md 2.1); câu báo về mã
Sheet cũng không chép mã (mã Sheet là thông tin cần giữ, LC-T094-15).
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from dotenv import dotenv_values
from dotenv.parser import parse_stream

from seo_app import config

ALLOWED_KEYS = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")
MAX_VALUE_LENGTH = 512
# Ký tự được phép trong khóa: chữ/số ASCII và vài dấu thường gặp trong khóa API
# (Anthropic/OpenAI "sk-…", Gemini "AIza…"). Không có dấu nháy, "#", "$", "\", "=", dấu cách.
_ALLOWED_VALUE = re.compile(r"[A-Za-z0-9_\-.:+/~]+")
_BOM = chr(0xFEFF)  # dấu BOM đầu file «UTF-8 with BOM»
# Thời gian chờ tối đa (giây) khi kiểm tra khóa với máy chủ AI.
CHECK_TIMEOUT_SECONDS = 15.0

# Mã Google Sheet (đoạn giữa "/d/" và "/edit" trong link): chỉ chữ, số ASCII, "-", "_" (T-097,
# LC-T094-15). Dùng chung cho mọi nơi kiểm mã Sheet (``seo_app/google/sheets.py``).
SHEET_ID_VAR = "GOOGLE_SHEET_ID"
SHEET_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{25,100}")

# Mã băm mật khẩu đăng nhập (``set_password``, T-104): chữ, số ASCII và ":" (dạng
# ``pbkdf2_sha256:lặp:muối:băm`` của ``seo_app.auth``), giới hạn độ dài.
PASSWORD_HASH_VAR = "APP_PASSWORD_HASH"
_PASSWORD_HASH_VALUE = re.compile(r"[A-Za-z0-9_:]{1,512}")


class EnvFileError(ValueError):
    """Không ghi được ``.env`` hoặc giá trị không hợp lệ. Thông điệp tiếng Việt, không chứa khóa."""


class EnvFileReadError(EnvFileError):
    """Không đọc được ``.env``: ``not_utf8`` (sai bảng mã) hoặc lỗi hệ thống ``error_name``
    (tên loại lỗi, ví dụ ``PermissionError``). Chưa ghi gì."""

    def __init__(self, message: str, *, error_name: str = "", not_utf8: bool = False) -> None:
        super().__init__(message)
        self.error_name = error_name
        self.not_utf8 = not_utf8


class EnvFileWriteError(EnvFileError):
    """Không ghi được ``.env`` (``error_name``: tên loại lỗi). Lỗi xảy ra trước hoặc ngay ở bước
    ``os.replace``, nên file ``.env`` cũ **chưa bị thay**, còn nguyên (T-104, LC-T090-2)."""

    def __init__(self, message: str, *, error_name: str) -> None:
        super().__init__(message)
        self.error_name = error_name


class EnvFileFormatError(EnvFileError):
    """Nội dung mới không khớp cách python-dotenv đọc: không ghi, hoặc đã trả lại bản cũ."""


class EnvFileReadBackError(EnvFileError):
    """Đã thay ``.env`` nhưng **không đọc lại được** để kiểm (``error_name``: tên loại lỗi; ví dụ
    chương trình khác giữ file đúng lúc đó; SL-T104-1, T-105). Khác ``EnvFileFormatError`` (đọc lại
    được mà nội dung khác). ``restored``: đã bỏ bản vừa ghi (trả bản cũ, hay xóa file vừa tạo khi
    trước đó chưa có), ``.env`` như trước khi ghi; ``False``: không bỏ được, ``.env`` có thể đang
    mang giá trị mới chưa được kiểm."""

    def __init__(self, *, error_name: str, restored: bool) -> None:
        message = _READBACK_RESTORED if restored else _READBACK_UNSURE
        super().__init__(message.format(error=error_name))
        self.error_name = error_name
        self.restored = restored


def _resolve_env_file(env_file: Path | None) -> Path:
    # Tra DEFAULT_ENV_FILE lúc gọi (như load_settings) để test trỏ sang file tạm được.
    return Path(config.DEFAULT_ENV_FILE if env_file is None else env_file)


def _check_name(name: str) -> None:
    if name not in ALLOWED_KEYS:
        allowed = ", ".join(ALLOWED_KEYS)
        raise EnvFileError(f"Chỉ được ghi các biến: {allowed}.")


def validate_key_value(value: str) -> str:
    """Bỏ khoảng trắng hai đầu và kiểm tra giá trị khóa. Trả về giá trị đã làm sạch.

    Thông báo lỗi không bao giờ chứa giá trị (kể cả một phần).
    """
    if not isinstance(value, str):
        raise EnvFileError("Khóa phải là chữ.")
    cleaned = value.strip()
    if not cleaned:
        raise EnvFileError("Chưa nhập khóa.")
    if len(cleaned) > MAX_VALUE_LENGTH:
        raise EnvFileError(f"Khóa dài bất thường (quá {MAX_VALUE_LENGTH} ký tự). Kiểm tra lại.")
    if any(ch in cleaned for ch in "\r\n"):
        raise EnvFileError("Khóa không được có xuống dòng. Hãy dán đúng một dòng.")
    if any(ch.isspace() for ch in cleaned):
        raise EnvFileError("Khóa không được có dấu cách ở giữa. Kiểm tra lại khi sao chép.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in cleaned):
        raise EnvFileError("Khóa có ký tự điều khiển (ký tự ẩn). Hãy sao chép lại.")
    if any(ch in cleaned for ch in "\"'`"):
        raise EnvFileError("Khóa không được có dấu nháy.")
    if "#" in cleaned:
        raise EnvFileError("Khóa không được có dấu #.")
    if not _ALLOWED_VALUE.fullmatch(cleaned):
        raise EnvFileError(
            "Khóa có ký tự lạ (chỉ nhận chữ không dấu, số và các dấu - _ . : + / ~)."
        )
    return cleaned


def _key_line_pattern(name: str) -> re.Pattern[str]:
    # Dòng hỏng (dotenv không đọc được) mà bắt đầu bằng "NAME=", "export NAME =", "'NAME'=".
    return re.compile(rf"^\s*(?:export[^\S\r\n]+)?'?{re.escape(name)}'?[^\S\r\n]*=")


def _parse(text: str) -> dict[str, str | None]:
    """Đọc ``.env`` đúng như python-dotenv (không thế biến ``${…}``, để so sánh chính xác)."""
    return dict(dotenv_values(stream=io.StringIO(text), interpolate=False))


def _read_env_text(path: Path) -> str | None:
    """Nội dung ``.env`` (giữ nguyên BOM và kiểu xuống dòng), ``None`` nếu chưa có file."""
    if path.is_symlink():
        # Không ghi qua liên kết tắt: không biết file thật nằm ở đâu (Lá Chắn T-016-020 #3).
        raise EnvFileError(
            "File .env đang là liên kết tắt (symlink) nên app không ghi vào. "
            "Hãy thay nó bằng một file .env thường."
        )
    if not path.exists():
        return None
    if not path.is_file():
        raise EnvFileError("Đường dẫn .env không phải là một file.")
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError as exc:
        raise EnvFileReadError(
            "File .env không đọc được dạng UTF-8. Mở và lưu lại bằng UTF-8.", not_utf8=True
        ) from exc
    except OSError as exc:
        name = type(exc).__name__
        raise EnvFileReadError(f"Không đọc được file .env ({name}).", error_name=name) from exc


def _build_content(name: str, value: str, text: str, *, add_if_missing: bool) -> str | None:
    """Nội dung mới của ``.env``; ``None`` nếu không cần ghi.

    Tách file đúng bằng bộ đọc của python-dotenv (``parse_stream``), nên ranh giới từng dòng
    gán biến, giá trị nhiều dòng, nháy và ký tự thoát khớp với cách app đọc lại sau này. Mọi
    đoạn không phải biến ``name`` được chép lại nguyên văn.
    """
    has_bom = text.startswith(_BOM)
    body = text[len(_BOM) :] if has_bom else text
    pattern = _key_line_pattern(name)
    new_line_text = f"{name}={value}"

    out: list[str] = []
    found = False
    for binding in parse_stream(io.StringIO(body)):
        original = binding.original.string
        if binding.error and pattern.match(original):
            # Ví dụ: ANTHROPIC_API_KEY="sk-cu (quên đóng nháy). Không đoán, không ghi gì.
            raise EnvFileError(
                f"Dòng {name} trong file .env đang sai định dạng (thường là thiếu dấu nháy "
                "đóng). Hãy mở .env, sửa hoặc xóa dòng đó rồi lưu lại."
            )
        if binding.key != name:
            out.append(original)
            continue
        found = True
        # Giữ các dòng trống phía trước (dotenv gộp chúng vào đoạn này), bỏ thụt đầu dòng.
        lead = re.match(r"\s*", original)
        blank = lead.group(0) if lead else ""
        prefix = blank[: max(blank.rfind("\n"), blank.rfind("\r")) + 1]
        ending_match = re.search(r"(?:\r\n|\n|\r)$", original)
        ending = ending_match.group(0) if ending_match else ""
        out.append(prefix + new_line_text + ending)

    if not found:
        if not add_if_missing:
            return None
        newline_match = re.search(r"\r\n|\n|\r", body)
        newline = newline_match.group(0) if newline_match else "\n"
        if out and not out[-1].endswith(("\n", "\r")):
            out[-1] += newline
        out.append(new_line_text + newline)

    return (_BOM if has_bom else "") + "".join(out)


_FORMAT_ERROR = (
    "File .env có định dạng lạ nên app không ghi khóa vào được (đã giữ nguyên file cũ). "
    "Hãy mở .env và sửa tay."
)
_RESTORE_FAILED = (
    "File .env vừa ghi đọc lại thấy sai và không trả lại được bản cũ ({error}). Hãy mở .env "
    "kiểm tra từng dòng."
)
# Không đọc lại được file vừa ghi (SL-T104-1, T-105): nói đúng nguyên nhân, không nói tới định dạng.
_READBACK_RESTORED = (
    "Không đọc lại được file .env để kiểm sau khi ghi ({error}) nên đã bỏ bản vừa ghi, file .env "
    "vẫn như trước khi lưu. Đóng chương trình đang mở file .env (ví dụ phần mềm diệt virus hay "
    "đồng bộ thư mục) rồi thử lại."
)
_READBACK_UNSURE = (
    "Không đọc lại được file .env để kiểm sau khi ghi ({error}), cũng không bỏ được bản vừa ghi: "
    "file .env có thể đã mang giá trị mới nhưng chưa được kiểm. Đóng chương trình đang mở file "
    ".env (ví dụ phần mềm diệt virus hay đồng bộ thư mục) rồi lưu lại lần nữa."
)


def _write_value(
    name: str, value: str, env_file: Path | None, *, add_if_missing: bool = True
) -> None:
    path = _resolve_env_file(env_file)
    if not path.parent.is_dir():
        raise EnvFileError("Không tìm thấy thư mục chứa file .env.")

    old_text = _read_env_text(path)
    text = old_text or ""
    content = _build_content(name, value, text, add_if_missing=add_if_missing)
    if content is None:
        return

    # Mọi biến khác phải giữ nguyên, biến ``name`` phải đúng giá trị mới.
    expected = _parse(text)
    expected[name] = value
    if _parse(content) != expected:
        raise EnvFileFormatError(_FORMAT_ERROR)

    _atomic_write(path, content)

    # Đọc lại từ đĩa bằng python-dotenv để chắc chắn. Không đọc lại được hay đọc ra khác thì bỏ
    # bản vừa ghi, rồi báo đúng nguyên nhân: hai trường hợp không gộp (SL-T104-1, T-105).
    try:
        written = _read_env_text(path)
    except EnvFileError as exc:
        written, read_error = None, _read_error_name(exc)
    else:
        read_error = "FileNotFoundError" if written is None else None
    if written is not None and _parse(written) == expected:
        return
    discard_error = _discard_written(path, old_text)
    if read_error is not None:
        raise EnvFileReadBackError(error_name=read_error, restored=discard_error is None)
    if discard_error is not None:
        # File đã bị thay mà không trả lại được: không được báo «file cũ còn nguyên».
        raise EnvFileError(_RESTORE_FAILED.format(error=discard_error))
    raise EnvFileFormatError(_FORMAT_ERROR)


def _read_error_name(exc: EnvFileError) -> str:
    """Tên loại lỗi khi đọc lại ``.env`` (cho câu báo: không đường dẫn, không nội dung)."""
    if isinstance(exc, EnvFileReadError):
        if exc.error_name:
            return exc.error_name
        if exc.not_utf8:
            return "UnicodeDecodeError"
    return type(exc).__name__


def _discard_written(path: Path, old_text: str | None) -> str | None:
    """Bỏ bản vừa ghi: trả bản cũ, hay xóa file vừa tạo (trước đó chưa có ``.env``). Trả tên loại
    lỗi nếu không bỏ được (khi đó ``.env`` có thể vẫn mang bản vừa ghi), ``None`` nếu bỏ được."""
    try:
        if old_text is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_write(path, old_text)
    except EnvFileWriteError as exc:
        return exc.error_name
    except OSError as exc:
        return type(exc).__name__
    return None


def _is_windows() -> bool:
    return os.name == "nt"


def _atomic_write(path: Path, content: str) -> None:
    tmp_name: str | None = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=".env.", suffix=".tmp", dir=path.parent)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        if not _is_windows():
            os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
        tmp_name = None
    except OSError as exc:
        # Không đưa đường dẫn máy hay nội dung vào thông báo. Lỗi ở đây là trước hoặc ngay ở
        # ``os.replace`` (thay nguyên tử): file đích chưa bị đụng tới.
        name = type(exc).__name__
        raise EnvFileWriteError(
            f"Không ghi được file .env ({name}). Kiểm tra quyền ghi thư mục app.", error_name=name
        ) from exc
    finally:
        if tmp_name is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)


def set_api_key(name: str, value: str, env_file: Path | None = None) -> None:
    """Ghi khóa ``name`` vào ``.env`` (mặc định ``config.DEFAULT_ENV_FILE``, tra lúc gọi).

    Có biến rồi thì thay đúng dòng đó, chưa có thì thêm vào cuối, chưa có file thì tạo mới.
    """
    _check_name(name)
    cleaned = validate_key_value(value)
    _write_value(name, cleaned, env_file)


def clear_api_key(name: str, env_file: Path | None = None) -> None:
    """Xóa khóa ``name``: để trống giá trị (``NAME=``), giữ nguyên dòng và vị trí của nó.

    Chưa có file hoặc chưa có dòng của biến thì không làm gì.
    """
    _check_name(name)
    _write_value(name, "", env_file, add_if_missing=False)


def validate_sheet_id(value: object) -> str:
    """Kiểm mã Google Sheet sẽ ghi vào ``.env`` (bộ kiểm riêng, LC-T094-15). Trả mã đã bỏ
    khoảng trắng hai đầu.

    Chỉ nhận đúng ``SHEET_ID_PATTERN`` (toàn chuỗi): không xuống dòng, ``=``, dấu nháy, ``#``,
    dấu cách, ký tự ngoài ASCII…, nên không chèn được biến khác vào ``.env``. Câu báo không bao
    giờ chép mã (kể cả một phần).
    """
    if not isinstance(value, str):
        raise EnvFileError("Mã Google Sheet phải là chữ.")
    cleaned = value.strip()
    if not cleaned:
        raise EnvFileError("Chưa có mã Google Sheet.")
    if not SHEET_ID_PATTERN.fullmatch(cleaned):
        raise EnvFileError(
            "Mã Google Sheet không đúng dạng (25–100 ký tự, chỉ chữ không dấu, số, «-» và «_»). "
            "Hãy dán lại link Sheet."
        )
    return cleaned


def set_google_sheet_id(value: str, env_file: Path | None = None) -> None:
    """Ghi ``GOOGLE_SHEET_ID`` vào ``.env`` (mặc định ``config.DEFAULT_ENV_FILE``, tra lúc gọi).

    Cùng cách ghi với khóa AI: thay đúng dòng của biến (hoặc thêm vào cuối), giữ nguyên mọi dòng
    khác, ghi nguyên tử, Mac/Linux quyền ``600``, đọc lại để chắc chắn.
    """
    _write_value(SHEET_ID_VAR, validate_sheet_id(value), env_file)


def clear_google_sheet_id(env_file: Path | None = None) -> None:
    """Để trống ``GOOGLE_SHEET_ID`` (``GOOGLE_SHEET_ID=``), giữ nguyên dòng và vị trí của nó.

    Chưa có file hoặc chưa có dòng của biến thì không làm gì.
    """
    _write_value(SHEET_ID_VAR, "", env_file, add_if_missing=False)


def set_password_hash(value: str, env_file: Path | None = None) -> None:
    """Ghi ``APP_PASSWORD_HASH`` vào ``.env`` cho ``set_password`` (T-104, LC-T090-1, -2).

    Cùng bộ ghi với khóa API (``_write_value``): tách ``.env`` bằng python-dotenv (bỏ BOM, chỉ CR,
    LF là xuống dòng), thay **mọi** dòng của biến (kể cả dòng lặp, ``export``, có dấu cách quanh
    «=»: app dùng dòng cuối), chép nguyên văn mọi đoạn khác, ghi file tạm rồi ``os.replace``, đọc
    lại để kiểm. Giá trị chỉ nhận chữ, số ASCII và các dấu của mã băm (``pbkdf2_sha256:…``): không
    xuống dòng, dấu cách, nháy, ``#``, ``=``. Lỗi: ``EnvFileReadError``, ``EnvFileWriteError`` (file
    cũ còn nguyên), ``EnvFileFormatError``, ``EnvFileError``; câu báo không chứa giá trị.
    """
    if not isinstance(value, str) or not _PASSWORD_HASH_VALUE.fullmatch(value):
        raise EnvFileError("Mã băm mật khẩu không đúng định dạng.")
    _write_value(PASSWORD_HASH_VAR, value, env_file)


def overridden_by_os_environ(name: str, environ: Mapping[str, str] | None = None) -> bool:
    """Biến ``name`` cũng được đặt trong biến môi trường hệ điều hành.

    Khi đó ``load_settings`` dùng giá trị của hệ điều hành, khóa ghi vào ``.env`` không có hiệu
    lực. Chỉ trả về đúng/sai, không bao giờ trả về giá trị.
    """
    _check_name(name)
    env = os.environ if environ is None else environ
    return name in env


def password_hash_overridden(environ: Mapping[str, str] | None = None) -> bool:
    """``APP_PASSWORD_HASH`` có trong biến môi trường hệ điều hành (SL-T104-2, T-105).

    Cùng điều kiện với ``load_settings``: biến có mặt (kể cả rỗng) là app dùng giá trị đó, bỏ qua
    ``.env``, nên mã băm ``set_password`` ghi vào ``.env`` không có hiệu lực. Hàm riêng vì
    ``overridden_by_os_environ`` chỉ nhận tên khóa AI. Chỉ trả về đúng/sai, không bao giờ trả về
    giá trị.
    """
    env = os.environ if environ is None else environ
    return PASSWORD_HASH_VAR in env


# ---------------------------------------------------------------------------
# Kiểm tra khóa
# ---------------------------------------------------------------------------

CheckStatus = Literal["ok", "invalid", "unknown", "unsupported", "missing"]


@dataclass(frozen=True)
class KeyCheckResult:
    """Kết quả kiểm tra khóa. ``message`` viết tiếng Việt, đã che chuỗi giống khóa."""

    status: CheckStatus
    message: str

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def check_api_key(
    name: str,
    *,
    api_key: str | None = None,
    client: Any | None = None,
    timeout: float = CHECK_TIMEOUT_SECONDS,
) -> KeyCheckResult:
    """Kiểm tra khóa ``name`` có dùng được không.

    ``api_key=None``: lấy khóa đang có hiệu lực từ ``load_settings()`` (``.env`` + biến môi
    trường), để giao diện không phải giữ khóa trong bộ nhớ. ``client`` chỉ dùng cho test.
    Mỗi hãng gọi lệnh rẻ nhất (lấy danh sách mô hình, không tốn token), có ``timeout`` và chỉ
    gọi một lần (không tự thử lại).
    """
    _check_name(name)
    label, field, checker = _CHECKERS[name]
    if api_key is None:
        try:
            api_key = getattr(config.load_settings(), field)
        except config.ConfigError:
            return KeyCheckResult("unknown", "Cấu hình .env đang có lỗi, chưa kiểm tra được khóa.")
    api_key = (api_key or "").strip()
    if not api_key:
        return KeyCheckResult("missing", f"Chưa khai báo khóa {label}.")
    try:
        return checker(api_key, client=client, timeout=timeout)
    except _CALL_LIBRARY_ERRORS:
        # Thư viện đổi tên lớp lỗi (bỏ anthropic.AuthenticationError…): chính câu
        # "except anthropic.AuthenticationError" ném AttributeError, lọt khỏi khối try bên trong
        # (Soi Lỗi SL-T026-2). Bắt ở đây để vẫn ra câu "uv sync".
        return _library_result(label)


def _result(status: CheckStatus, message: str) -> KeyCheckResult:
    from seo_app.ai.base import redact_secrets

    return KeyCheckResult(status, redact_secrets(message))


def _library_result(label: str) -> KeyCheckResult:
    """Thư viện của hãng cài thiếu hoặc sai phiên bản (nâng ngoài uv.lock): nhắc chạy uv sync."""
    from seo_app.ai.base import library_message

    return _result("unknown", library_message(label))


def _other_result(label: str, vendor: str, exc: Exception) -> KeyCheckResult:
    """Lỗi không khớp nhánh nào của hãng (T-028).

    - Máy chủ trả mã 200 nhưng nội dung hỏng (trang HTML, JSON hỏng, thiếu trường), thư viện để
      lọt lỗi khi đọc: câu cố định "dữ liệu lạ", không chép thông điệp thô.
    - Lỗi kiểu Python nảy ra lúc gọi thư viện (lệch phiên bản): câu "uv sync".
    - Lỗi lạ khác: chỉ nêu tên lỗi, không làm sập trang.
    """
    from seo_app.ai.base import bad_response_message, is_bad_response, network_error_kind

    if network_error_kind(exc) == "decode" or is_bad_response(exc):
        return _result("unknown", bad_response_message(vendor))
    if isinstance(exc, _CALL_LIBRARY_ERRORS):
        return _library_result(label)
    return _result("unknown", f"Lỗi khi kiểm tra khóa ({type(exc).__name__}).")


def _bad_response(vendor: str) -> str:
    from seo_app.ai.base import bad_response_message

    return bad_response_message(vendor)


def _listing_ok(listing: Any, field: str, *, allow_empty: bool = True) -> bool:
    """Kết quả lấy danh sách mô hình có đúng dạng không (máy chủ trả ``{}`` thì không).

    ``field``: tên thuộc tính chứa danh sách trong kiểu của thư viện (``data`` với anthropic,
    openai; ``page`` với google-genai). Đối tượng không có thuộc tính đó (client giả trong test,
    bản thư viện khác) thì không xét.
    """
    items = getattr(listing, field, _MISSING)
    if items is _MISSING:
        return True
    return isinstance(items, list) and (allow_empty or bool(items))


_MISSING = object()


# Lúc gọi kiểm tra: lỗi kiểu Python do thư viện lệch phiên bản (đổi tên hàm, tham số). KeyError
# không tính vào đây (có thể do dữ liệu trả về lạ), vẫn chỉ nêu tên lỗi như mọi lỗi lạ khác.
_CALL_LIBRARY_ERRORS = (ImportError, AttributeError, TypeError)


def _check_anthropic(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    from seo_app.ai.base import (
        ANTHROPIC_URL,
        SETUP_ERRORS,
        caused_by_decoding,
        ignoring_custom_headers,
    )

    try:
        import anthropic

        if client is None:
            # max_retries=0: chỉ gọi một lần, người dùng biết kết quả ngay. base_url cố định:
            # biến môi trường ANTHROPIC_BASE_URL không có tác dụng (W4). Bỏ qua
            # ANTHROPIC_CUSTOM_HEADERS (T-028).
            with ignoring_custom_headers():
                client = anthropic.Anthropic(
                    api_key=api_key, base_url=ANTHROPIC_URL, timeout=timeout, max_retries=0
                )
    except SETUP_ERRORS:
        return _library_result("Claude")
    try:
        # Gọi rẻ nhất: lấy danh sách mô hình, 1 mục. Không tốn token.
        listing = client.models.list(limit=1, timeout=timeout)
    except anthropic.AuthenticationError:
        return _result("invalid", "Khóa Claude không đúng hoặc đã bị thu hồi.")
    except anthropic.PermissionDeniedError:
        return _result("invalid", "Khóa Claude không có quyền truy cập. Kiểm tra trong Console.")
    except anthropic.RateLimitError:
        return _result("unknown", "Anthropic đang giới hạn số lần gọi. Đợi một phút rồi thử lại.")
    except anthropic.APITimeoutError:
        return _result("unknown", f"Anthropic không trả lời sau {timeout:g} giây. Thử lại sau.")
    except anthropic.APIConnectionError as exc:
        if caused_by_decoding(exc):
            # Nội dung nén gzip/br hỏng: thư viện bọc thành lỗi kết nối (LC-T028-3).
            return _result("unknown", _bad_response("Anthropic"))
        return _result("unknown", "Không kết nối được tới Anthropic. Kiểm tra mạng Internet.")
    except anthropic.APIStatusError as exc:
        return _result("unknown", f"Anthropic báo lỗi {exc.status_code}. Thử lại sau ít phút.")
    except anthropic.AnthropicError as exc:
        # Không chép thông điệp thô của thư viện (có thể chứa header/URL).
        return _result("unknown", f"Lỗi khi kiểm tra khóa ({type(exc).__name__}).")
    except Exception as exc:
        # Dữ liệu trả về hỏng, thư viện lệch phiên bản, hoặc lỗi lạ khác (lọt ra từ tầng mạng…).
        return _other_result("Claude", "Anthropic", exc)
    if not _listing_ok(listing, "data"):
        return _result("unknown", _bad_response("Anthropic"))
    return _result("ok", "Khóa Claude dùng được.")


def _check_openai(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    from seo_app.ai.base import (
        OPENAI_URL,
        SETUP_ERRORS,
        caused_by_decoding,
        ignoring_custom_headers,
    )

    try:
        import openai

        if client is None:
            # max_retries=0: chỉ gọi một lần, người dùng biết kết quả ngay. base_url cố định:
            # biến môi trường OPENAI_BASE_URL không có tác dụng (W4). Bỏ qua
            # OPENAI_CUSTOM_HEADERS (T-028).
            with ignoring_custom_headers():
                client = openai.OpenAI(
                    api_key=api_key, base_url=OPENAI_URL, timeout=timeout, max_retries=0
                )
    except SETUP_ERRORS:
        return _library_result("ChatGPT")
    try:
        # Gọi rẻ nhất: lấy danh sách mô hình. Không tốn token.
        listing = client.models.list(timeout=timeout)
    except openai.AuthenticationError:
        return _result("invalid", "Khóa ChatGPT không đúng hoặc đã bị thu hồi.")
    except openai.PermissionDeniedError:
        return _result(
            "invalid", "Khóa ChatGPT không có quyền truy cập. Kiểm tra trên trang OpenAI."
        )
    except openai.RateLimitError:
        return _result("unknown", "OpenAI đang giới hạn số lần gọi. Đợi một phút rồi thử lại.")
    except openai.APITimeoutError:
        return _result("unknown", f"OpenAI không trả lời sau {timeout:g} giây. Thử lại sau.")
    except openai.APIConnectionError as exc:
        if caused_by_decoding(exc):
            # Nội dung nén gzip/br hỏng: thư viện bọc thành lỗi kết nối (LC-T028-3).
            return _result("unknown", _bad_response("OpenAI"))
        return _result("unknown", "Không kết nối được tới OpenAI. Kiểm tra mạng Internet.")
    except openai.APIStatusError as exc:
        return _result("unknown", f"OpenAI báo lỗi {exc.status_code}. Thử lại sau ít phút.")
    except Exception as exc:
        # Các lỗi còn lại (dữ liệu trả về hỏng, thư viện lệch phiên bản, lỗi của thư viện hay
        # lọt ra từ tầng mạng): không chép thông điệp thô (có thể chứa header/URL).
        return _other_result("ChatGPT", "OpenAI", exc)
    if not _listing_ok(listing, "data"):
        return _result("unknown", _bad_response("OpenAI"))
    return _result("ok", "Khóa ChatGPT dùng được.")


def _check_gemini(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    from seo_app.ai.base import GEMINI_URL, SETUP_ERRORS

    try:
        import httpx
        from google import genai
        from google.genai import errors, types

        from seo_app.ai.gemini_provider import no_debug_config

        if client is None:
            # attempts=1: chỉ gọi một lần. Thời gian chờ của thư viện tính bằng mili giây.
            # base_url cố định: biến môi trường GOOGLE_GEMINI_BASE_URL không có tác dụng (W4).
            client = genai.Client(
                api_key=api_key,
                vertexai=False,
                http_options=types.HttpOptions(
                    base_url=GEMINI_URL,
                    timeout=int(timeout * 1000),
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
                # Không đọc biến GOOGLE_GENAI_CLIENT_MODE… (chế độ ghi/phát lại, T-028).
                debug_config=no_debug_config(),
            )
    except SETUP_ERRORS:
        return _library_result("Gemini")
    try:
        # Gọi rẻ nhất: lấy danh sách mô hình, 1 mục. Không tốn token.
        listing = client.models.list(config={"page_size": 1})
    except errors.APIError as exc:
        details = f"{exc.status} {exc.message} {exc.details}".lower()
        # Google trả 400 (không phải 401) khi khóa sai: lý do API_KEY_INVALID.
        if exc.code == 401 or "api_key_invalid" in details or "api key not valid" in details:
            return _result("invalid", "Khóa Gemini không đúng hoặc đã bị thu hồi.")
        if exc.code == 403:
            return _result(
                "invalid", "Khóa Gemini không có quyền truy cập. Kiểm tra trong Google AI Studio."
            )
        if exc.code == 429:
            return _result("unknown", "Gemini đang giới hạn số lần gọi. Đợi một phút rồi thử lại.")
        return _result("unknown", f"Gemini báo lỗi {exc.code}. Thử lại sau ít phút.")
    except httpx.TimeoutException:
        return _result("unknown", f"Gemini không trả lời sau {timeout:g} giây. Thử lại sau.")
    except httpx.TransportError:
        return _result("unknown", "Không kết nối được tới Gemini. Kiểm tra mạng Internet.")
    except Exception as exc:
        # google-genai không gom mọi lỗi về một lớp chung (Anthropic/OpenAI thì có): dữ liệu trả
        # về hỏng, thư viện lệch phiên bản, lỗi lạ khác. Không chép thông điệp thô.
        return _other_result("Gemini", "Gemini", exc)
    # google-genai đổi trường "models" thiếu thành danh sách rỗng, mà khóa đúng luôn thấy ít nhất
    # một mô hình: danh sách rỗng nghĩa là máy chủ trả về thứ khác.
    if not _listing_ok(listing, "page", allow_empty=False):
        return _result("unknown", _bad_response("Gemini"))
    return _result("ok", "Khóa Gemini dùng được.")


# Biến trong .env -> (tên hiển thị, trường trong Settings, hàm kiểm tra)
_CHECKERS = {
    "ANTHROPIC_API_KEY": ("Claude", "anthropic_api_key", _check_anthropic),
    "OPENAI_API_KEY": ("ChatGPT", "openai_api_key", _check_openai),
    "GEMINI_API_KEY": ("Gemini", "gemini_api_key", _check_gemini),
}

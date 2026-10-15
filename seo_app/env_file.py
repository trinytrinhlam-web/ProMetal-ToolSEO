"""Ghi/xóa khóa API AI trong file ``.env`` từ giao diện app (phiếu T-020).

Khóa vẫn chỉ nằm trong ``.env`` (quyết định đã chốt); module này chỉ là chỗ ghi vào đó, an
toàn hơn sửa file bằng tay:

- Chỉ nhận đúng ba biến ``ALLOWED_KEYS``. Không biến nào khác (ví dụ ``APP_PASSWORD_HASH``)
  sửa được qua đây.
- Giá trị bị kiểm tra chặt (``validate_key_value``): không xuống dòng, không ký tự điều khiển,
  không dấu nháy, ``#``, ``$``, dấu cách… nên không ai chèn thêm được một biến khác vào file.
- Mọi dòng khác, chú thích và thứ tự trong ``.env`` được giữ nguyên.
- Ghi ra file tạm cùng thư mục rồi thay thế (``os.replace``); Mac/Linux đặt quyền ``600``.

Không hàm nào ở đây trả về, in ra hay ghi log giá trị khóa (security.md 2.1).
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
_BOM = "﻿"
# Thời gian chờ tối đa (giây) khi kiểm tra khóa với máy chủ AI.
CHECK_TIMEOUT_SECONDS = 15.0


class EnvFileError(ValueError):
    """Không ghi được ``.env`` hoặc giá trị không hợp lệ. Thông điệp tiếng Việt, không chứa khóa."""


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
        raise EnvFileError(
            "File .env không đọc được dạng UTF-8. Mở và lưu lại bằng UTF-8."
        ) from exc
    except OSError as exc:
        raise EnvFileError(f"Không đọc được file .env ({type(exc).__name__}).") from exc


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
        raise EnvFileError(_FORMAT_ERROR)

    _atomic_write(path, content)

    # Đọc lại từ đĩa bằng python-dotenv để chắc chắn; sai thì trả lại bản cũ.
    try:
        written = _read_env_text(path)
    except EnvFileError:
        written = None
    if written is None or _parse(written) != expected:
        if old_text is None:
            with contextlib.suppress(OSError):
                path.unlink()
        else:
            _atomic_write(path, old_text)
        raise EnvFileError(_FORMAT_ERROR)


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
        # Không đưa đường dẫn máy hay nội dung vào thông báo.
        raise EnvFileError(
            f"Không ghi được file .env ({type(exc).__name__}). Kiểm tra quyền ghi thư mục app."
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


def overridden_by_os_environ(name: str, environ: Mapping[str, str] | None = None) -> bool:
    """Biến ``name`` cũng được đặt trong biến môi trường hệ điều hành.

    Khi đó ``load_settings`` dùng giá trị của hệ điều hành, khóa ghi vào ``.env`` không có hiệu
    lực. Chỉ trả về đúng/sai, không bao giờ trả về giá trị.
    """
    _check_name(name)
    env = os.environ if environ is None else environ
    return name in env


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
    return checker(api_key, client=client, timeout=timeout)


def _result(status: CheckStatus, message: str) -> KeyCheckResult:
    from seo_app.ai.base import redact_secrets

    return KeyCheckResult(status, redact_secrets(message))


def _check_anthropic(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    import anthropic

    try:
        if client is None:
            # max_retries=0: chỉ gọi một lần, người dùng biết kết quả ngay.
            client = anthropic.Anthropic(api_key=api_key, timeout=timeout, max_retries=0)
        # Gọi rẻ nhất: lấy danh sách mô hình, 1 mục. Không tốn token.
        client.models.list(limit=1, timeout=timeout)
    except anthropic.AuthenticationError:
        return _result("invalid", "Khóa Claude không đúng hoặc đã bị thu hồi.")
    except anthropic.PermissionDeniedError:
        return _result("invalid", "Khóa Claude không có quyền truy cập. Kiểm tra trong Console.")
    except anthropic.RateLimitError:
        return _result("unknown", "Anthropic đang giới hạn số lần gọi. Đợi một phút rồi thử lại.")
    except anthropic.APITimeoutError:
        return _result("unknown", f"Anthropic không trả lời sau {timeout:g} giây. Thử lại sau.")
    except anthropic.APIConnectionError:
        return _result("unknown", "Không kết nối được tới Anthropic. Kiểm tra mạng Internet.")
    except anthropic.APIStatusError as exc:
        return _result("unknown", f"Anthropic báo lỗi {exc.status_code}. Thử lại sau ít phút.")
    except anthropic.AnthropicError as exc:
        # Không chép thông điệp thô của thư viện (có thể chứa header/URL).
        return _result("unknown", f"Lỗi khi kiểm tra khóa ({type(exc).__name__}).")
    return _result("ok", "Khóa Claude dùng được.")


def _check_openai(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    import openai

    try:
        if client is None:
            # max_retries=0: chỉ gọi một lần, người dùng biết kết quả ngay.
            client = openai.OpenAI(api_key=api_key, timeout=timeout, max_retries=0)
        # Gọi rẻ nhất: lấy danh sách mô hình. Không tốn token.
        client.models.list(timeout=timeout)
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
    except openai.APIConnectionError:
        return _result("unknown", "Không kết nối được tới OpenAI. Kiểm tra mạng Internet.")
    except openai.APIStatusError as exc:
        return _result("unknown", f"OpenAI báo lỗi {exc.status_code}. Thử lại sau ít phút.")
    except Exception as exc:
        # Các lỗi còn lại (của thư viện hay lọt ra từ tầng mạng khi không thử lại): chỉ nêu
        # tên lỗi, không chép thông điệp thô (có thể chứa header/URL); không làm sập trang.
        return _result("unknown", f"Lỗi khi kiểm tra khóa ({type(exc).__name__}).")
    return _result("ok", "Khóa ChatGPT dùng được.")


def _check_gemini(api_key: str, *, client: Any | None, timeout: float) -> KeyCheckResult:
    import httpx
    from google import genai
    from google.genai import errors, types

    try:
        if client is None:
            # attempts=1: chỉ gọi một lần. Thời gian chờ của thư viện tính bằng mili giây.
            client = genai.Client(
                api_key=api_key,
                vertexai=False,
                http_options=types.HttpOptions(
                    timeout=int(timeout * 1000),
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        # Gọi rẻ nhất: lấy danh sách mô hình, 1 mục. Không tốn token.
        client.models.list(config={"page_size": 1})
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
        # google-genai không gom mọi lỗi về một lớp chung (Anthropic/OpenAI thì có). Chỉ nêu
        # tên lỗi, không chép thông điệp thô (có thể chứa header/URL); không làm sập trang.
        return _result("unknown", f"Lỗi khi kiểm tra khóa ({type(exc).__name__}).")
    return _result("ok", "Khóa Gemini dùng được.")


# Biến trong .env -> (tên hiển thị, trường trong Settings, hàm kiểm tra)
_CHECKERS = {
    "ANTHROPIC_API_KEY": ("Claude", "anthropic_api_key", _check_anthropic),
    "OPENAI_API_KEY": ("ChatGPT", "openai_api_key", _check_openai),
    "GEMINI_API_KEY": ("Gemini", "gemini_api_key", _check_gemini),
}

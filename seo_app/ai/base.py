"""Phần chung của mọi hãng AI: cấu hình theo việc, lỗi, và giao diện provider."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

EFFORTS = ("low", "medium", "high", "xhigh", "max")


# Chuỗi trông giống khóa/mật khẩu:
# - khóa Anthropic/OpenAI (sk-…), Google (AIza…), kể cả khi dính sau "_" (x_sk-…);
# - token sau "Bearer"/"Basic" (cách bằng dấu cách, xuống dòng hoặc ":", kể cả "Bearer:xyz");
# - giá trị sau "x-api-key", "api_key"/"apiKey", "authorization", "password"/"passwd",
#   "token", "secret" (cả "client_secret"), "private_key" kèm ":" hoặc "=": che tới hết dòng
#   (hoặc tới dấu nháy đóng), vì mật khẩu có thể chứa dấu cách;
# - "người-dùng:mật-khẩu@" trong địa chỉ (https://admin:matkhau@site…);
# - tham số "key=" trong địa chỉ (Google hay để khóa ở "…?key=…"): che tới "&", dấu cách
#   hoặc dấu nháy;
# - giá trị của trường tên đúng "key" trong JSON/dict ("key": "…", 'key': '…').
_SECRET_NAMES = (
    "x-api-key", "api_key", "api-key", "apikey", "authorization", "password", "passwd",
    "token", "secret", "private_key", "private-key", "privatekey",
)  # fmt: skip
_SECRET_LIKE = re.compile(
    r"(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_\-]{8,}|AIza[0-9A-Za-z_\-]{16,})"
    r"|(?:(?<=bearer)|(?<=basic))(?:\s*:\s*|\s+)[A-Za-z0-9._~+/=\-]{6,}"
    r"|(?:" + "|".join(f"(?<={re.escape(name)})" for name in _SECRET_NAMES) + r")"
    r"[\"']?[ \t]*[:=][ \t]*[\"']?[^\n\"']{4,}"
    r"|(?<=://)[^/\s:@]+:[^/\s@]+(?=@)"
    r"|(?<=[?&]key=)[^&\s\"'#]+"
    r"|(?:(?<=\"key\")|(?<='key'))[ \t]*:[ \t]*[\"'][^\"'\n]+(?=[\"'])",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> str:
    """Che các chuỗi giống khóa trong thông báo lỗi lấy từ máy chủ/thư viện (security.md 2.1)."""
    return _SECRET_LIKE.sub("[đã ẩn]", text)


class AIError(RuntimeError):
    """Lỗi khi gọi AI. Thông điệp viết bằng tiếng Việt để hiện thẳng cho người dùng."""


# Địa chỉ máy chủ chính thức của từng hãng (security.md W4, mục 2.7). Luôn truyền rõ khi tạo
# client: thư viện chỉ đọc biến môi trường (OPENAI_BASE_URL, ANTHROPIC_BASE_URL,
# GOOGLE_GEMINI_BASE_URL) khi không được truyền địa chỉ, nên phần mềm khác trên máy không lái
# được khóa và bài viết sang máy chủ lạ.
ANTHROPIC_URL = "https://api.anthropic.com"
OPENAI_URL = "https://api.openai.com/v1"
GEMINI_URL = "https://generativelanguage.googleapis.com/"

# Lỗi Python do thư viện của hãng lệch phiên bản (nâng/hạ ngoài uv.lock): thiếu module, hằng,
# hàm (ImportError, AttributeError), đổi tham số (TypeError), đổi dạng dữ liệu (KeyError).
LIBRARY_ERRORS: tuple[type[Exception], ...] = (ImportError, AttributeError, TypeError, KeyError)
# Lúc nhập module hãng và tạo client: thêm lỗi kiểm tham số của pydantic (google-genai dựng
# HttpOptions, HttpRetryOptions… bằng pydantic, không nhận trường lạ).
SETUP_ERRORS: tuple[type[Exception], ...] = (*LIBRARY_ERRORS, ValidationError)


def library_message(label: str) -> str:
    """Câu báo thư viện của hãng ``label`` cài thiếu hoặc sai phiên bản (nhắc chạy uv sync)."""
    return (
        f"Thư viện của {label} chưa cài hoặc sai phiên bản. Đóng app, chạy lại run.bat / "
        "run.command (hoặc lệnh uv sync) để cài đúng phiên bản."
    )


def library_error(label: str) -> AIError:
    return AIError(library_message(label))


# Mã lỗi ngắn của máy chủ (invalid_value, INVALID_ARGUMENT, max_output_tokens…): chỉ chữ cái
# không dấu, nối bằng "_" hoặc ".". Không có số, dấu cách hay ký tự Markdown, nên không thể là
# khóa API hay câu thô của máy chủ.
_SAFE_CODE = re.compile(r"[A-Za-z]+(?:[_.][A-Za-z]+)*")
# Câu lỗi hiện bằng st.error (Markdown có GFM). Với bộ ký tự trên, http(s):// và email không thể
# có (thiếu ":", "/", "@"), nhưng "www.x.y" tự thành link bấm được, kể cả khi đứng sau "_"
# (Soi Lỗi SL-T026-1). Bỏ mọi mã có "www."; bỏ thêm mã có dạng tên miền (đuôi là tên miền cấp
# cao quen thuộc) phòng khi câu được hiện ở nơi tự biến "ten.com" thành link. Mã thật của 3 hãng
# không có dạng này; bỏ nhầm thì chỉ mất phần gợi ý, câu báo vẫn đúng.
_LINK_TLDS = frozenset((
    "com", "net", "org", "edu", "gov", "int", "mil", "io", "vn", "co", "info", "biz", "xyz",
    "app", "dev", "ai", "me", "us", "uk", "tv", "cc", "ly", "to", "gg", "sh", "site", "online",
    "top", "club", "shop", "store", "link", "click", "example", "test", "local", "localhost",
    "invalid",
))  # fmt: skip


def _looks_like_link(value: str) -> bool:
    lower = value.lower()
    if "www." in lower:
        return True
    return "." in lower and lower.rsplit(".", 1)[1] in _LINK_TLDS


def safe_code(value: object) -> str | None:
    """``value`` nếu là mã lỗi ngắn an toàn để hiện ra (xem ``_SAFE_CODE``), ngược lại ``None``.

    Không bao giờ trả về thứ có thể thành link (``www.…``, ``ten.com``).
    """
    if (
        isinstance(value, str)
        and len(value) <= 40
        and _SAFE_CODE.fullmatch(value)
        and not _looks_like_link(value)
    ):
        return value
    return None


def bad_request_error(
    vendor: str,
    task: TaskConfig,
    code: object = None,
    param: object = None,
    *,
    hint: str | None = None,
) -> AIError:
    """Lỗi 400 (máy chủ không nhận yêu cầu): câu cố định, không bao giờ chép câu của máy chủ.

    Chỉ kèm mã lỗi 400, tên mô hình, và (nếu có) mã lỗi / tên tham số ngắn đã lọc bằng
    ``safe_code`` để người dùng biết sửa chỗ nào trong ``config/ai.toml`` (security S2).
    ``hint``: câu gợi ý viết sẵn trong code cho một lỗi đã biết (không lấy từ máy chủ).
    """
    extra = [f"mã {c}" for c in [safe_code(code)] if c]
    extra += [f"tham số {p}" for p in [safe_code(param)] if p]
    note = f"; {', '.join(extra)}" if extra else ""
    advice = hint or (
        f"Kiểm tra tên mô hình và các thông số (max_tokens, effort, web_search) của việc "
        f"«{task.name}» trong config/ai.toml rồi thử lại."
    )
    return AIError(
        f"{vendor} không nhận yêu cầu (lỗi 400{note}) với mô hình «{task.model}». {advice}"
    )


@dataclass(frozen=True)
class TaskConfig:
    """Mô hình dùng cho một việc (đọc từ ``config/ai.toml``)."""

    name: str
    provider: str
    model: str
    effort: str = "medium"
    web_search: bool = False
    max_tokens: int = 16000


class AIProvider(Protocol):
    """Một hãng AI. Mỗi lần gọi trả về dữ liệu đúng khuôn ``schema`` (đã kiểm tra)."""

    def generate(self, task: TaskConfig, *, system: str, prompt: str, schema: type[T]) -> T: ...

"""Phần chung của mọi hãng AI: cấu hình theo việc, lỗi, và giao diện provider."""

from __future__ import annotations

import json
import os
import re
import threading
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
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


# --------------------------------------------- máy chủ trả mã 200 nhưng nội dung hỏng (T-028)


def bad_response_message(vendor: str) -> str:
    """Câu báo máy chủ ``vendor`` trả về thứ không đọc được (câu cố định, không chép dữ liệu)."""
    return (
        f"Máy chủ {vendor} trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy). Kiểm tra mạng "
        "rồi thử lại."
    )


def bad_response_error(vendor: str) -> AIError:
    return AIError(bad_response_message(vendor))


def connection_lost_message(vendor: str) -> str:
    return f"Mất kết nối tới {vendor} giữa chừng. Kiểm tra mạng Internet rồi bấm thử lại."


# Thư viện của 3 hãng. Chỉ lỗi nảy ra trong code của chúng mới được xét là "đang đọc trả lời".
_VENDOR_PACKAGES = ("anthropic", "openai", "google.genai")
# Hàm của thư viện chỉ chạy khi đã nhận được trả lời mã 2xx và đang đọc nó:
# - anthropic, openai: _process_response (đọc JSON thường), __stream__ (đọc luồng SSE),
#   accumulate_event (ghép luồng thành bài);
# - google-genai: _from_response, …_from_mldev / …_from_vertex (đổi JSON sang kiểu của thư viện).
_READ_FUNCTIONS = frozenset(
    {"_process_response", "__stream__", "accumulate_event", "_from_response"}
)
_READ_SUFFIXES = ("_from_mldev", "_from_vertex")
# Kiểu dữ liệu trả về của anthropic, openai (Message, Response…): thuộc tính tính từ dữ liệu
# máy chủ, lỗi trong đó là do dữ liệu hỏng.
_READ_MODULES = ("anthropic.types", "openai.types")


def _in_package(module: str, packages: tuple[str, ...]) -> bool:
    return any(module == p or module.startswith(p + ".") for p in packages)


def is_bad_response(exc: BaseException) -> bool:
    """``exc`` là lỗi khi thư viện của hãng đọc một trả lời hỏng (mã 200 nhưng là trang HTML,
    JSON hỏng, luồng SSE hỏng hay thiếu trường), không phải do thư viện lệch phiên bản.

    Chỉ xét lỗi nảy ra trong code thư viện của hãng (lỗi từ chỗ khác, như client giả trong test,
    giữ nguyên cách báo cũ):

    - ``json.JSONDecodeError``, ``UnicodeDecodeError``, ``AssertionError``: thư viện chỉ ném khi
      đọc dữ liệu, nên tính là dữ liệu hỏng.
    - Lỗi khác (``TypeError``, ``AttributeError``, ``KeyError``, ``ValueError``, ``RuntimeError``…):
      chỉ tính khi nảy ra bên trong hàm đọc trả lời của thư viện (``_READ_FUNCTIONS``…). Lỗi do
      thư viện lệch phiên bản (đổi tên tham số, hàm, thuộc tính) nảy ra lúc **gọi** thư viện,
      trước khi có trả lời, nên vẫn ra câu "uv sync".
    """
    if isinstance(exc, AIError):
        return False
    decode_error = isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError, AssertionError))
    for frame, _ in traceback.walk_tb(exc.__traceback__):
        module = str(frame.f_globals.get("__name__", ""))
        if not _in_package(module, _VENDOR_PACKAGES):
            continue
        name = frame.f_code.co_name
        if (
            decode_error
            or name in _READ_FUNCTIONS
            or name.endswith(_READ_SUFFIXES)
            or _in_package(module, _READ_MODULES)
        ):
            return True
    return False


def network_error_kind(exc: BaseException) -> str | None:
    """Loại lỗi mạng của httpx/httpx2 (thư viện các hãng dùng để gọi) mà thư viện hãng để lọt ra
    khi đang đọc luồng trả lời: ``"timeout"``, ``"decode"`` (dữ liệu nén hỏng), ``"network"``
    (đứt kết nối giữa chừng), hoặc ``None`` nếu không phải lỗi mạng.

    So theo tên lớp để nhận cả ``httpx`` lẫn ``httpx2`` mà không phải nhập thêm thư viện.
    """
    names = {
        cls.__name__
        for cls in type(exc).__mro__
        if cls.__module__.split(".")[0] in ("httpx", "httpx2")
    }
    if "TimeoutException" in names:
        return "timeout"
    if "DecodingError" in names:
        return "decode"
    if "RequestError" in names:
        return "network"
    return None


def unreadable_error(exc: BaseException, vendor: str) -> AIError | None:
    """``AIError`` (câu cố định) cho lỗi khi đọc trả lời của ``vendor``: dữ liệu hỏng
    (``is_bad_response``), hoặc mạng đứt / quá giờ giữa lúc đọc luồng. ``None`` nếu không phải.
    """
    kind = network_error_kind(exc)
    if kind == "timeout":
        return AIError(f"{vendor} trả lời quá lâu. Bấm thử lại.")
    if kind == "network":
        return AIError(connection_lost_message(vendor))
    if kind == "decode" or is_bad_response(exc):
        return bad_response_error(vendor)
    return None


# Biến môi trường mà thư viện đọc lúc tạo client để chèn header vào **mọi** lời gọi. Dự án không
# dùng, nên bỏ qua (Lá Chắn LC-T026-2, Soi Lỗi SL-T028-2):
# - *_CUSTOM_HEADERS: header tùy ý, kể cả Authorization (openai/_client.py:317-331);
# - OPENAI_ORG_ID, OPENAI_PROJECT_ID: header OpenAI-Organization / OpenAI-Project
#   (openai/_client.py:281-286, :659-660). Biến sót từ công cụ OpenAI khác làm khóa đúng bị máy
#   chủ từ chối, hoặc tính tiền vào tổ chức/dự án khác.
# Không cần thêm: ANTHROPIC_AUTH_TOKEN (thư viện bỏ qua khi app truyền api_key), OPENAI_ADMIN_KEY
# (chỉ gửi ở lời gọi quản trị, app không dùng), *_WEBHOOK_* (không gửi đi). google-genai không có
# biến tương tự khi vertexai=False. Proxy và chứng chỉ (HTTPS_PROXY, SSL_CERT_FILE…) vẫn giữ:
# mạng công ty có thể cần.
IGNORED_ENV = (
    "ANTHROPIC_CUSTOM_HEADERS",
    "OPENAI_CUSTOM_HEADERS",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT_ID",
)
_ENV_LOCK = threading.Lock()


@contextmanager
def ignoring_custom_headers() -> Iterator[None]:
    """Tạm ẩn ``IGNORED_ENV`` trong lúc tạo client (thư viện chỉ đọc chúng trong ``__init__``).

    Khóa ``_ENV_LOCK`` để hai trang tạo client cùng lúc không trả biến về sai giá trị. Xong thì trả
    lại như cũ: chỉ client của app không thấy biến, phần còn lại của máy không bị đụng.
    """
    with _ENV_LOCK:
        saved = {name: os.environ.pop(name) for name in IGNORED_ENV if name in os.environ}
        try:
            yield
        finally:
            os.environ.update(saved)


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

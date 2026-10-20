"""Phần chung của mọi hãng AI: cấu hình theo việc, lỗi, và giao diện provider."""

from __future__ import annotations

import json
import os
import re
import threading
import traceback
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
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


class TokenLimitError(AIError):
    """Câu trả lời bị cắt vì chạm giới hạn ``max_tokens`` của việc.

    Lớp riêng để nơi gọi (ví dụ thử mù, nơi giới hạn không đọc từ ``config/ai.toml``) thay câu
    gợi ý cho đúng cách người dùng sửa được.
    """


def token_limit_error(task: TaskConfig) -> TokenLimitError:
    return TokenLimitError(
        f"Bài dài quá giới hạn ({task.max_tokens} token). Tăng max_tokens của việc "
        f"«{task.name}» trong config/ai.toml."
    )


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


def caused_by_decoding(exc: BaseException) -> bool:
    """``exc`` (hoặc lỗi gốc của nó) là lỗi giải nén của httpx (nội dung ``gzip``/``br`` hỏng).

    Thư viện anthropic, openai bọc lỗi này thành ``APIConnectionError``, nên phải lần theo chuỗi
    ``__cause__`` / ``__context__`` (Lá Chắn LC-T028-3). Có giới hạn số bước, phòng chuỗi vòng.
    """
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen and len(seen) < 20:
        if network_error_kind(current) == "decode":
            return True
        seen.add(id(current))
        current = current.__cause__ or current.__context__
    return False


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
# Module của thư viện đọc các biến trên lúc tạo client (anthropic/_client.py:244,
# openai/_client.py:281-317, đều qua ``os.environ.get``).
_CLIENT_MODULES = ("anthropic._client", "openai._client")


class _ReentrantLock:
    """``threading.RLock`` có thêm ``locked()`` (RLock chỉ có hàm này từ Python 3.14).

    Gọi lồng trong cùng một luồng không tự treo (Lá Chắn LC-T028-1).
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._depth = 0

    def __enter__(self) -> None:
        self._lock.acquire()
        self._depth += 1

    def __exit__(self, *exc_info: object) -> None:
        self._depth -= 1
        self._lock.release()

    def locked(self) -> bool:
        """Có luồng nào (kể cả luồng đang gọi) đang giữ khóa không."""
        if not self._lock.acquire(blocking=False):
            return True
        try:
            return self._depth > 0
        finally:
            self._lock.release()


_ENV_LOCK = _ReentrantLock()


class _EnvironWithoutIgnored(Mapping[str, str]):
    """``os.environ`` nhìn qua một lớp lọc: đọc như thật nhưng không thấy ``IGNORED_ENV``.

    Chỉ đọc. Không chép giá trị ra: mỗi lần đọc đều hỏi ``os.environ`` thật.
    """

    def __getitem__(self, name: str) -> str:
        if name in IGNORED_ENV:
            raise KeyError(name)
        return os.environ[name]

    def __iter__(self) -> Iterator[str]:
        return (name for name in list(os.environ) if name not in IGNORED_ENV)

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def copy(self) -> dict[str, str]:
        return dict(self)


class _OsWithoutIgnored:
    """Thay cho module ``os`` bên trong module tạo client của thư viện: mọi thứ như ``os`` thật,
    riêng ``environ`` là ``_EnvironWithoutIgnored``.
    """

    environ = _EnvironWithoutIgnored()

    def __getattr__(self, name: str) -> object:
        return getattr(os, name)

    def getenv(self, name: str, default: str | None = None) -> str | None:
        return self.environ.get(name, default)


_OS_WITHOUT_IGNORED = _OsWithoutIgnored()


@contextmanager
def ignoring_custom_headers() -> Iterator[None]:
    """Thư viện không thấy ``IGNORED_ENV`` trong lúc tạo client (chỉ đọc chúng trong ``__init__``).

    Không gỡ biến khỏi ``os.environ`` (Soi Lỗi SL-T019-5): luồng khác đang duyệt ``os.environ``
    (httpx tìm proxy, ``dict(os.environ)``) sẽ gặp ``KeyError`` nếu biến biến mất giữa chừng. Thay
    vào đó, tên ``os`` bên trong ``anthropic._client`` và ``openai._client`` được tạm trỏ sang
    ``_OsWithoutIgnored``; phần còn lại của máy (và của chính thư viện) vẫn thấy ``os`` thật.

    Nếu một bản thư viện khác không đọc biến qua ``os`` của module đó (không có tên ``os`` trỏ
    tới module ``os`` thật), thì quay về cách cũ: tạm gỡ biến khỏi ``os.environ``, để header lạ
    không bao giờ tới client.

    Khóa ``_ENV_LOCK`` để các luồng cùng tạo client không trả ``os`` / biến về sai.
    """
    import importlib
    import sys

    with _ENV_LOCK:
        patched: list[tuple[object, object]] = []
        fallback = False
        for module_name in _CLIENT_MODULES:
            module = sys.modules.get(module_name)
            if module is None:
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    # Gói chưa cài: không có client nào của nó được tạo. Gói vẫn cài mà mất
                    # module ``_client`` (thư viện đổi cấu trúc): không biết nó đọc biến ở đâu,
                    # nên gỡ biến như cách cũ (Soi Lỗi SL-T034-2).
                    try:
                        importlib.import_module(module_name.split(".")[0])
                    except ImportError:
                        continue
                    fallback = True
                    continue
            current = getattr(module, "os", None)
            if current is os or current is _OS_WITHOUT_IGNORED:
                patched.append((module, current))
                module.os = _OS_WITHOUT_IGNORED  # type: ignore[attr-defined]
            else:
                fallback = True
        saved = (
            {name: os.environ.pop(name) for name in IGNORED_ENV if name in os.environ}
            if fallback
            else {}
        )
        try:
            yield
        finally:
            os.environ.update(saved)
            for module, original in reversed(patched):
                module.os = original  # type: ignore[attr-defined]


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


# ------------------------------------------------------------------ ảnh gửi kèm (T-050)

# Chỉ nhận 3 định dạng cả 3 hãng đều đọc được (T-046 mục 3). Không nhận GIF (có thể là ảnh động),
# HEIC (chỉ Gemini đọc được): ảnh gửi AI là bản đã chuẩn bị sẵn (T-049), thường là JPEG.
IMAGE_MIMES = ("image/jpeg", "image/png", "image/webp")
_MIME_ALIASES = {"image/jpg": "image/jpeg", "image/pjpeg": "image/jpeg"}
# Giới hạn trước khi gửi (bản gửi AI khoảng 1024 px, thường vài trăm KB):
# - mỗi ảnh tối đa 5 MB: dưới giới hạn 10 MB/ảnh (sau base64) của Anthropic;
# - tối đa 4 ảnh, tổng tối đa 10 MB: base64 làm dài thêm 1/3, nên tổng yêu cầu vẫn dưới 20 MB
#   (giới hạn gửi thẳng của Gemini).
MAX_IMAGES = 4
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_IMAGE_BYTES = 10 * 1024 * 1024

IMAGE_TYPE_MESSAGE = (
    "Ảnh gửi AI phải là dữ liệu ảnh đã chuẩn bị sẵn trong bộ nhớ; phần mềm không gửi tên file "
    "hay đường dẫn."
)
IMAGE_MIME_MESSAGE = "Ảnh gửi AI chỉ nhận JPEG, PNG hoặc WebP."
IMAGE_EMPTY_MESSAGE = "Ảnh gửi AI bị rỗng (không có dữ liệu)."
IMAGE_BROKEN_MESSAGE = "Ảnh gửi AI bị hỏng hoặc không đúng định dạng đã khai báo."
IMAGE_METADATA_MESSAGE = (
    "Ảnh gửi AI vẫn còn thông tin kèm theo (EXIF, XMP hoặc chú thích, có thể có vị trí GPS). "
    "Phần mềm không gửi ảnh này cho AI."
)


@dataclass(frozen=True)
class ImageInput:
    """Một ảnh gửi kèm lời gọi AI: chỉ có bytes ảnh và kiểu MIME.

    Cố ý không có tên file, đường dẫn hay thẻ (security A3): tên thư mục có thể chứa tên, địa
    chỉ khách. Bytes phải là bản gửi AI đã bỏ hết metadata (T-049); ``prepare_images`` kiểm lại.
    ``repr`` không in bytes (ảnh vài trăm KB làm ngập log, traceback).
    """

    data: bytes = field(repr=False)
    mime: str

    def __repr__(self) -> str:
        size = len(self.data) if isinstance(self.data, (bytes, bytearray)) else "?"
        return f"ImageInput(mime={self.mime!r}, {size} bytes)"


def _mb(size: int) -> str:
    return f"{size / (1024 * 1024):.1f}".replace(".", ",")


def prepare_images(images: Sequence[ImageInput]) -> tuple[ImageInput, ...]:
    """Kiểm ảnh trước khi gửi AI; trả bản sao bất biến (bytes) để gửi đúng thứ đã kiểm.

    Báo ``AIError`` (câu tiếng Việt cố định, không chép dữ liệu ảnh) khi: không phải
    ``ImageInput`` (ví dụ chuỗi đường dẫn), quá ``MAX_IMAGES`` ảnh, ảnh rỗng, quá
    ``MAX_IMAGE_BYTES`` / ``MAX_TOTAL_IMAGE_BYTES``, MIME ngoài ``IMAGE_MIMES``, nội dung không
    đúng MIME hoặc hỏng cấu trúc, hoặc còn metadata (EXIF, XMP, chú thích).
    Ảnh là dữ liệu chưa tin cậy: chỉ đọc cấu trúc khối, không giải nén ảnh.
    """
    if isinstance(images, (str, bytes, bytearray, memoryview, ImageInput)) or not isinstance(
        images, Sequence
    ):
        raise AIError(IMAGE_TYPE_MESSAGE)
    if len(images) > MAX_IMAGES:
        raise AIError(f"Mỗi lần chỉ gửi AI tối đa {MAX_IMAGES} ảnh.")
    prepared: list[ImageInput] = []
    total = 0
    for image in images:
        if not isinstance(image, ImageInput) or not isinstance(image.mime, str):
            raise AIError(IMAGE_TYPE_MESSAGE)
        if not isinstance(image.data, (bytes, bytearray)):
            raise AIError(IMAGE_TYPE_MESSAGE)
        data = bytes(image.data)  # chép ra: bytearray bị sửa sau khi kiểm cũng không ảnh hưởng
        mime = image.mime.strip().lower()
        mime = _MIME_ALIASES.get(mime, mime)
        if mime not in IMAGE_MIMES:
            raise AIError(IMAGE_MIME_MESSAGE)
        if not data:
            raise AIError(IMAGE_EMPTY_MESSAGE)
        if len(data) > MAX_IMAGE_BYTES:
            raise AIError(
                f"Ảnh gửi AI quá lớn ({_mb(len(data))} MB, tối đa {_mb(MAX_IMAGE_BYTES)} MB). "
                "Dùng bản ảnh thu nhỏ để gửi AI."
            )
        total += len(data)
        if total > MAX_TOTAL_IMAGE_BYTES:
            raise AIError(
                f"Tổng dung lượng ảnh gửi AI quá lớn (tối đa {_mb(MAX_TOTAL_IMAGE_BYTES)} MB "
                "mỗi lần). Gửi ít ảnh hơn."
            )
        problem = _IMAGE_CHECKS[mime](data)
        if problem == "metadata" or _has_metadata_marker(data):
            raise AIError(IMAGE_METADATA_MESSAGE)
        if problem is not None:
            raise AIError(IMAGE_BROKEN_MESSAGE)
        prepared.append(ImageInput(data=data, mime=mime))
    return tuple(prepared)


# Dấu hiệu của khối metadata ở bất kỳ đâu trong file (kể cả ảnh thứ hai nối sau ảnh chính, như
# ảnh MPO): đầu khối EXIF trong JPEG/WebP, gói XMP. Xác suất dữ liệu ảnh nén tình cờ chứa đúng
# các chuỗi này là không đáng kể; nếu có thì chỉ là từ chối nhầm (an toàn).
_METADATA_MARKERS = (b"Exif\x00\x00", b"http://ns.adobe.com/xap/1.0/", b"<x:xmpmeta")


def _has_metadata_marker(data: bytes) -> bool:
    return any(marker in data for marker in _METADATA_MARKERS)


# JPEG: APP1 (EXIF, XMP), APP13 (Photoshop/IPTC: tên người, địa điểm), COM (chú thích tự do).
_JPEG_METADATA = frozenset({0xE1, 0xED, 0xFE})
_JPEG_STANDALONE = frozenset({0x01, *range(0xD0, 0xD8)})


def _check_jpeg(data: bytes) -> str | None:
    """Đi qua mọi khối JPEG, kể cả giữa các lượt quét của ảnh progressive, tới mã kết thúc (EOI)
    ở đúng cuối file. ``"format"``: sai cấu trúc hoặc có dữ liệu nối sau EOI; ``"metadata"``: có
    khối metadata; ``None``: ổn."""
    if not data.startswith(b"\xff\xd8\xff"):
        return "format"
    i, n = 2, len(data)
    seen_scan = False
    while True:
        if i >= n or data[i] != 0xFF:
            return "format"
        while i < n and data[i] == 0xFF:  # byte đệm 0xFF trước mã khối
            i += 1
        if i >= n:
            return "format"
        marker = data[i]
        i += 1
        if marker == 0xD9:  # EOI: chỉ hợp lệ sau khối ảnh và ở đúng cuối file
            return None if seen_scan and i == n else "format"
        if marker in _JPEG_STANDALONE:
            continue
        if marker in (0x00, 0xD8) or i + 2 > n:
            return "format"
        length = int.from_bytes(data[i : i + 2], "big")
        if length < 2 or i + length > n:
            return "format"
        if marker in _JPEG_METADATA:
            return "metadata"
        i += length
        if marker == 0xDA:  # SOS: tiếp theo là dữ liệu ảnh nén, đi tới mã khối kế tiếp
            seen_scan = True
            i = _skip_entropy(data, i)


def _skip_entropy(data: bytes, i: int) -> int:
    """Vị trí mã khối đầu tiên sau dữ liệu nén bắt đầu ở ``i`` (hoặc ``len(data)``).

    Trong dữ liệu nén, 0xFF chỉ đứng trước 0x00 (byte đệm), mã RST (0xD0–0xD7) hoặc 0xFF khác.
    """
    n = len(data)
    while True:
        i = data.find(b"\xff", i)
        if i < 0 or i + 1 >= n:
            return n
        following = data[i + 1]
        if following == 0x00 or 0xD0 <= following <= 0xD7:
            i += 2
        elif following == 0xFF:
            i += 1
        else:
            return i


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# eXIf: EXIF; tEXt/zTXt/iTXt: chữ tự do (tác giả, chú thích, XMP, cả EXIF dạng chữ).
_PNG_METADATA = frozenset({b"eXIf", b"tEXt", b"zTXt", b"iTXt"})


def _check_png(data: bytes) -> str | None:
    """Đi qua các chunk PNG tới ``IEND``; chunk đầu phải là ``IHDR``."""
    if not data.startswith(_PNG_SIGNATURE):
        return "format"
    i, n, first = len(_PNG_SIGNATURE), len(data), True
    while i + 12 <= n:
        length = int.from_bytes(data[i : i + 4], "big")
        kind = data[i + 4 : i + 8]
        if not kind.isalpha() or i + 12 + length > n:
            return "format"
        if first and kind != b"IHDR":
            return "format"
        if kind in _PNG_METADATA:
            return "metadata"
        if kind == b"IEND":
            # Không nhận dữ liệu nối sau IEND (chỗ giấu được bất cứ thứ gì).
            return None if i + 12 + length == n else "format"
        first = False
        i += 12 + length
    return "format"


_WEBP_IMAGE_CHUNKS = frozenset({b"VP8 ", b"VP8L", b"VP8X"})
_WEBP_METADATA = frozenset({b"EXIF", b"XMP "})


def _check_webp(data: bytes) -> str | None:
    """Đi qua các chunk RIFF của WebP; chunk đầu phải là ``VP8 ``/``VP8L``/``VP8X``."""
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return "format"
    end = 8 + int.from_bytes(data[4:8], "little")
    if end != len(data) or end < 20:  # không nhận dữ liệu nối sau khối RIFF
        return "format"
    i, first = 12, True
    while i < end:
        if i + 8 > end:
            return "format"
        kind = data[i : i + 4]
        size = int.from_bytes(data[i + 4 : i + 8], "little")
        if i + 8 + size > end:
            return "format"
        if first and kind not in _WEBP_IMAGE_CHUNKS:
            return "format"
        if kind in _WEBP_METADATA:
            return "metadata"
        first = False
        i += 8 + size + (size & 1)  # chunk lẻ có 1 byte đệm
    return None


_IMAGE_CHECKS = {"image/jpeg": _check_jpeg, "image/png": _check_png, "image/webp": _check_webp}


class AIProvider(Protocol):
    """Một hãng AI. Mỗi lần gọi trả về dữ liệu đúng khuôn ``schema`` (đã kiểm tra).

    ``images``: ảnh gửi kèm (bytes + MIME, xem ``ImageInput``), gửi thẳng trong yêu cầu, không
    qua Files API hay đường dẫn URL. Mỗi hãng gọi ``prepare_images`` trước khi gửi.
    """

    def generate(
        self,
        task: TaskConfig,
        *,
        system: str,
        prompt: str,
        schema: type[T],
        images: Sequence[ImageInput] = (),
    ) -> T: ...

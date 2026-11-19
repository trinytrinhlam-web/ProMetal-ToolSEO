"""Client Cloudflare Workers AI tạo ảnh minh họa (T-142; thiết kế T-140 mục 2, T-141 mục 1.7).

An toàn (Lá Chắn T-140: LC-T140-1 → -8; Lá Chắn T-141: LC-T141-9, -12):

- **Đường gọi cố định:** chỉ máy chủ ``api.cloudflare.com``, hai đường: ``accounts/<mã tài
  khoản>/ai/run/<mô hình>`` (tạo ảnh) và ``user/tokens/verify`` (kiểm token). Mã tài khoản đúng
  32 ký tự hex thường; mô hình lấy từ danh sách cho phép trong mã (``ALLOWED_MODELS``), chữ trong
  ``config/ai.toml`` chỉ để chọn. Không query, không header lấy từ cấu hình hay biến môi trường;
  token gắn qua ``_Bearer`` (``repr`` che token). Không bao giờ đi qua AI Gateway.
- **Không theo chuyển hướng** (``allow_redirects=False``, phiên ``max_redirects = 0``, móc
  ``_refuse_redirect``: 3xx đóng ngay, không đọc thân); giờ chờ ≤ 60 giây; thân trả lời đọc theo
  luồng, tối đa 16 MB (``_read_limited``). Lớp vận chuyển dùng chung với client Google Sheets và
  Search Console (LC-T120-18).
- **Thân lệnh** đúng hai trường ``prompt`` (1–2048 ký tự; dài hơn thì báo lỗi, không cắt) và
  ``steps`` (1–8, không nhận ``bool``). Không ``seed``, ``width``, ``height``.
- **Câu trả lời:** chỉ HTTP 200 + JSON đọc chặt (không ``NaN``/``Infinity``, không trùng khóa,
  lồng sâu không làm sập); ``success`` đúng là ``true``; ảnh chỉ nhận dạng base64 trong
  ``result.image`` (≤ 12.000.000 ký tự trước khi giải, ``validate=True``, ≤ 9 MB sau khi giải);
  có trường ``url`` thì từ chối, không bao giờ tải ảnh theo địa chỉ. Mã lỗi Cloudflare chỉ đọc
  khi là số nguyên trong danh sách đã biết; chữ ``message`` của máy chủ không bao giờ lên trang.
- **Lỗi** là ``CloudflareImageError`` (lớp con của ``AIError``): câu tiếng Việt cố định (không chép
  URL: chuỗi lỗi của ``requests`` chứa mã tài khoản) và ``kind`` cho lượt chạy tự động (bảng 2.4
  của thiết kế T-141). **Không tự thử lại**: mỗi lệnh tạo ảnh tốn neuron (LC-T140-7), lượt chạy
  quyết thử lại hay dừng.
- Không ``logging``, không nhập ``streamlit``: gọi được từ luồng nền (LC-T141-9).

Byte ảnh trả về chưa dùng thẳng được: ``seo_app.images.generated`` dựng lại thành WebP sạch.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests

from seo_app.ai.base import AIError
from seo_app.ai.registry import (
    AI_CONFIG_FILE,
    IMAGE_STEPS_DEFAULT,
    IMAGE_TASK,
    image_steps,
    load_ai_config,
)
from seo_app.config import Settings, load_settings
from seo_app.google.sheets import (  # lớp vận chuyển dùng chung (LC-T120-18, thiết kế T-140 2.2)
    _Bearer,
    _close_and_status,
    _read_limited,
    _Redirected,
    _refuse_redirect,
    _TooLarge,
)

PROVIDER = "cloudflare"
API_HOST = "api.cloudflare.com"
API_BASE = f"https://{API_HOST}/client/v4/"
VERIFY_PATH = "user/tokens/verify"
FLUX_SCHNELL = "@cf/black-forest-labs/flux-1-schnell"
ALLOWED_MODELS = (FLUX_SCHNELL,)  # đợt này một mục; đổi mô hình phải qua Lá Chắn
MAX_PROMPT_CHARS = 2048  # khuôn đầu vào của mô hình (minLength 1, maxLength 2048)
TIMEOUT_SECONDS = 60
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_VERIFY_RESPONSE_BYTES = 64 * 1024
MAX_IMAGE_CHARS = 12_000_000  # chiều dài chuỗi base64, kiểm trước khi giải mã
MAX_IMAGE_BYTES = 9 * 1024 * 1024  # byte ảnh sau khi giải mã
TOKEN_STATUSES = ("active", "disabled", "expired")

# Mã lỗi Cloudflare đã biết (trang mã lỗi Workers AI, đọc 18/11): 3003 tham số sai, 3023 tài
# khoản bị chặn, 3036 hết hạn mức ngày, 3040 quá tải, 3042 không có mô hình, 5004 khuôn đầu vào
# sai, 5007 không có mô hình (HTTP 400), 5028 mô hình đã ngừng.
KNOWN_ERROR_CODES = frozenset({3003, 3023, 3036, 3040, 3042, 5004, 5007, 5028})
CODE_DAILY_LIMIT = 3036
CODE_CAPACITY = 3040
CODE_ACCOUNT_BLOCKED = 3023

# Loại lỗi cho lượt chạy tự động: đúng tên bảng 2.4 của thiết kế T-141 (``AIError.kind`` chung do
# T-148 thêm cùng đợt; lớp lỗi ở đây dùng cùng tên thuộc tính ``kind``).
KIND_BUSY = "busy"
KIND_RATE = "rate"
KIND_QUOTA_DAY = "quota_day"
KIND_NETWORK = "network"
KIND_TIMEOUT = "timeout"
KIND_AUTH = "auth"
KIND_BAD_REQUEST = "bad_request"
KIND_SHAPE = "shape"

# Mã tài khoản: 32 ký tự hex thường. Token: chỉ ký tự của mã truy cập Cloudflare (dạng mới
# «cfut_…» và dạng cũ 40 ký tự); ký tự khác (dấu cách, ngoặc kép, xuống dòng) là dán nhầm.
_ACCOUNT_ID = re.compile(r"[0-9a-f]{32}")
_TOKEN = re.compile(r"[A-Za-z0-9_-]{20,256}")

# Câu báo cố định (thiết kế T-140 bảng 2.4): không chép lời máy chủ, URL, mã tài khoản, token.
MSG_NO_KEYS = (
    "Chưa khai báo Cloudflare: điền CLOUDFLARE_ACCOUNT_ID và CLOUDFLARE_API_TOKEN trong file .env "
    "(xem chú thích trong .env.example), rồi mở lại app."
)
MSG_BAD_ACCOUNT = (
    "CLOUDFLARE_ACCOUNT_ID trong file .env không đúng dạng (phải là 32 ký tự gồm số 0–9 và chữ "
    "a–f). Chép lại mã tài khoản từ trang Cloudflare."
)
MSG_BAD_TOKEN = (
    "CLOUDFLARE_API_TOKEN trong file .env không đúng dạng (có dấu cách, ngoặc kép hay ký tự lạ). "
    "Dán lại mã truy cập Cloudflare."
)
MSG_AUTH = (
    "Mã truy cập Cloudflare không dùng được (sai, hết hạn hoặc thiếu quyền Workers AI). Xem lại "
    "CLOUDFLARE_API_TOKEN trong file .env."
)
MSG_QUOTA = (
    "Hôm nay đã hết lượt tạo ảnh miễn phí của Cloudflare. Lượt mới có lúc 7 giờ sáng (giờ Việt "
    "Nam)."
)
MSG_BUSY = "Cloudflare đang quá tải. Thử lại sau ít phút."
MSG_REJECTED = (
    "Cloudflare từ chối lệnh tạo ảnh (mã HTTP {code}). Thử sửa prompt; vẫn lỗi thì báo Chỉ Huy."
)
MSG_NETWORK = "Không nhận được ảnh từ Cloudflare (mạng chậm hoặc mất mạng). Thử lại."
MSG_SSL = "Lỗi chứng chỉ bảo mật (SSL) khi kết nối Cloudflare. Kiểm tra giờ máy và mạng."
MSG_NETWORK_OTHER = "Lỗi mạng khi gọi Cloudflare ({kind}). Thử lại sau."
MSG_SERVER = "Máy chủ Cloudflare đang lỗi (mã HTTP {code}). Thử lại sau ít phút."
MSG_BAD_DATA = "Cloudflare trả về dữ liệu không đúng dạng (mã HTTP {code}). Thử lại sau."
MSG_TOO_BIG = "Câu trả lời của Cloudflare lớn bất thường nên app không đọc. Thử lại sau."
MSG_REDIRECT = "Cloudflare trả lời chuyển hướng (mã {code}); app không đi theo. Thử lại sau."
MSG_NO_IMAGE = "Cloudflare không trả về ảnh (câu trả lời không có ảnh dạng base64). Thử lại."
MSG_IMAGE_TOO_BIG = "Ảnh Cloudflare trả về lớn bất thường nên app không nhận. Thử lại."
MSG_BLOCKED = "Lệnh gọi Cloudflare này không nằm trong danh sách được phép, app không gửi."
MSG_MODEL = (
    "Mô hình tạo ảnh trong [tasks.image] của config/ai.toml chưa được hỗ trợ. Ghi model = "
    f'"{FLUX_SCHNELL}".'
)
MSG_STEPS = "Số bước tạo ảnh (steps) phải là số nguyên từ 1 đến 8."
MSG_PROMPT_EMPTY = "Prompt tạo ảnh đang trống."
MSG_PROMPT_LONG = (
    "Prompt tạo ảnh dài quá 2.048 ký tự (Cloudflare không nhận). Rút gọn prompt rồi tạo lại."
)
MSG_NO_IMAGE_TASK = (
    "config/ai.toml chưa có mục [tasks.image] (tạo ảnh minh họa). Mục này chỉ bật sau lần gọi thử "
    "Cloudflare cùng chủ dự án."
)
MSG_NOT_CLOUDFLARE = (
    "Việc tạo ảnh trong app chỉ dùng Cloudflare: trong [tasks.image] của config/ai.toml ghi "
    'provider = "cloudflare".'
)
MSG_CONFIG_CHANGED = "Không đọc lại được mục [tasks.image] của config/ai.toml. Tải lại trang."

# Câu báo cho «Kiểm tra kết nối» (Cài đặt, T-146): lệnh kiểm token không chứng minh quyền
# Workers AI (LC-T140-8).
TOKEN_MESSAGES = {
    "active": (
        "Mã truy cập Cloudflare hợp lệ. Quyền tạo ảnh (Workers AI) sẽ biết ở lần tạo ảnh đầu tiên."
    ),
    "disabled": "Mã truy cập Cloudflare đã bị tắt. Tạo mã mới theo hướng dẫn trong README.",
    "expired": "Mã truy cập Cloudflare đã hết hạn. Tạo mã mới theo hướng dẫn trong README.",
}


class CloudflareImageError(AIError):
    """Lỗi khi gọi Cloudflare: câu tiếng Việt cố định, hiện thẳng được.

    ``kind``: loại lỗi cho lượt chạy tự động (``busy``, ``rate``, ``quota_day``, ``network``,
    ``timeout``, ``auth``, ``bad_request``, ``shape``). ``status_code``: mã HTTP (nếu có).
    ``error_code``: mã lỗi Cloudflare đã biết (``KNOWN_ERROR_CODES``), hay ``None``.
    """

    def __init__(
        self,
        message: str,
        *,
        kind: str,
        status_code: int | None = None,
        error_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.status_code = status_code
        self.error_code = error_code


@dataclass(frozen=True)
class CloudflareImage:
    """Ảnh Cloudflare trả về: byte đã giải base64, **chưa** dùng thẳng được (dựng lại ở
    ``seo_app.images.generated``; byte gốc không lưu, không gửi đi)."""

    data: bytes = field(repr=False)
    model: str
    steps: int
    prompt: str = field(repr=False)  # đúng prompt đã gửi


@dataclass(frozen=True)
class ImageTask:
    """Mục ``[tasks.image]`` của ``config/ai.toml`` khi dùng Cloudflare."""

    model: str
    steps: int


# ------------------------------------------------------------------ kiểm đầu vào


def check_model(model: object) -> str:
    """Tên mô hình phải nằm trong danh sách cho phép (``ALLOWED_MODELS``)."""
    if not isinstance(model, str) or model not in ALLOWED_MODELS:
        raise CloudflareImageError(MSG_MODEL, kind=KIND_BAD_REQUEST)
    return model


def check_steps(steps: object) -> int:
    """Số bước 1–8; ``True``/``False`` không phải số (LC-T140-3)."""
    if type(steps) is not int or not 1 <= steps <= 8:
        raise CloudflareImageError(MSG_STEPS, kind=KIND_BAD_REQUEST)
    return steps


def check_prompt(prompt: object) -> str:
    """Prompt cuối 1–2048 ký tự, không toàn khoảng trắng. Dài hơn thì báo lỗi, không cắt."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise CloudflareImageError(MSG_PROMPT_EMPTY, kind=KIND_BAD_REQUEST)
    if len(prompt) > MAX_PROMPT_CHARS:
        raise CloudflareImageError(MSG_PROMPT_LONG, kind=KIND_BAD_REQUEST)
    return prompt


def load_image_task(path: Path = AI_CONFIG_FILE) -> ImageTask:
    """Mô hình và số bước của ``[tasks.image]`` (Cloudflare). Kiểm cả file như
    ``load_ai_config`` (câu lỗi tiếng Việt), rồi kiểm hãng, mô hình, số bước."""
    task = load_ai_config(path).get(IMAGE_TASK)
    if task is None:
        raise AIError(MSG_NO_IMAGE_TASK)
    if task.provider != PROVIDER:
        raise AIError(MSG_NOT_CLOUDFLARE)
    model = check_model(task.model)
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8-sig"))["tasks"][IMAGE_TASK]
        value = raw.get("steps", IMAGE_STEPS_DEFAULT)
    except (
        OSError,
        UnicodeDecodeError,
        tomllib.TOMLDecodeError,
        KeyError,
        TypeError,
        AttributeError,
    ):
        raise AIError(MSG_CONFIG_CHANGED) from None
    return ImageTask(model=model, steps=image_steps(IMAGE_TASK, value))


# ------------------------------------------------------------------ đọc câu trả lời


def _reject_constant(_name: str) -> float:
    raise ValueError("NaN/Infinity không phải số hợp lệ")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("trùng khóa")
        result[key] = value
    return result


_BAD = object()


def _parse_json(data: bytes) -> Any:
    """JSON của Cloudflare, đọc như dữ liệu chưa tin cậy (như client Search Console, LC-T120-5):
    không ``NaN``/``Infinity``, không trùng khóa, lồng sâu không làm sập. Hỏng thì ``_BAD``."""
    try:
        return json.loads(
            data.decode("utf-8"),
            parse_constant=_reject_constant,
            object_pairs_hook=_no_duplicate_keys,
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        return _BAD


def _known_code(answer: Any) -> int | None:
    """Mã lỗi Cloudflare đầu tiên đã biết trong ``errors[].code`` (chỉ số nguyên đúng kiểu)."""
    errors = answer.get("errors") if isinstance(answer, dict) else None
    if not isinstance(errors, list):
        return None
    for item in errors[:20]:
        code = item.get("code") if isinstance(item, dict) else None
        if type(code) is int and code in KNOWN_ERROR_CODES:
            return code
    return None


def _error_for(status: int, code: int | None) -> CloudflareImageError:
    """Câu báo cố định theo mã HTTP và mã lỗi Cloudflare đã biết (thiết kế T-140 bảng 2.4)."""
    if code == CODE_DAILY_LIMIT:
        return CloudflareImageError(
            MSG_QUOTA, kind=KIND_QUOTA_DAY, status_code=status, error_code=code
        )
    if status in (401, 403) or code == CODE_ACCOUNT_BLOCKED:
        return CloudflareImageError(MSG_AUTH, kind=KIND_AUTH, status_code=status, error_code=code)
    if code == CODE_CAPACITY:
        return CloudflareImageError(MSG_BUSY, kind=KIND_BUSY, status_code=status, error_code=code)
    if status == 429:
        return CloudflareImageError(MSG_BUSY, kind=KIND_RATE, status_code=status, error_code=code)
    if status == 408:
        return CloudflareImageError(
            MSG_NETWORK, kind=KIND_TIMEOUT, status_code=status, error_code=code
        )
    if status >= 500:
        return CloudflareImageError(
            MSG_SERVER.format(code=status), kind=KIND_BUSY, status_code=status, error_code=code
        )
    if 400 <= status < 500 or code is not None:
        return CloudflareImageError(
            MSG_REJECTED.format(code=status),
            kind=KIND_BAD_REQUEST,
            status_code=status,
            error_code=code,
        )
    return CloudflareImageError(
        MSG_BAD_DATA.format(code=status), kind=KIND_SHAPE, status_code=status
    )


def _is_json(content_type: str) -> bool:
    return content_type.split(";", 1)[0].strip().lower() == "application/json"


def _answer(status: int, data: bytes, content_type: str) -> dict[str, Any]:
    """Câu trả lời đúng khuôn chung của Cloudflare: HTTP 200, JSON object, ``success`` là
    ``true``. Mọi trường hợp khác thành ``CloudflareImageError`` câu cố định."""
    answer = _parse_json(data)
    if status != 200:
        raise _error_for(status, _known_code(answer))
    if not _is_json(content_type) or not isinstance(answer, dict):
        raise CloudflareImageError(
            MSG_BAD_DATA.format(code=status), kind=KIND_SHAPE, status_code=status
        )
    if answer.get("success") is not True:
        code = _known_code(answer)
        if code is not None:
            raise _error_for(status, code)
        raise CloudflareImageError(
            MSG_BAD_DATA.format(code=status), kind=KIND_SHAPE, status_code=status
        )
    return answer


def _image_bytes(answer: dict[str, Any], status: int) -> bytes:
    """Byte ảnh trong ``result.image`` (chỉ base64). Có trường ``url`` hay ``image`` không phải
    base64 thì từ chối: không bao giờ tải ảnh theo địa chỉ (góp ý Lá Chắn T-046 số 6)."""
    result = answer.get("result")
    if not isinstance(result, dict) or "url" in answer or "url" in result:
        raise CloudflareImageError(MSG_NO_IMAGE, kind=KIND_SHAPE, status_code=status)
    image = result.get("image")
    if not isinstance(image, str) or not image:
        raise CloudflareImageError(MSG_NO_IMAGE, kind=KIND_SHAPE, status_code=status)
    if len(image) > MAX_IMAGE_CHARS:
        raise CloudflareImageError(MSG_IMAGE_TOO_BIG, kind=KIND_SHAPE, status_code=status)
    try:
        data = base64.b64decode(image, validate=True)
    except (binascii.Error, ValueError):
        raise CloudflareImageError(MSG_NO_IMAGE, kind=KIND_SHAPE, status_code=status) from None
    if not data:
        raise CloudflareImageError(MSG_NO_IMAGE, kind=KIND_SHAPE, status_code=status)
    if len(data) > MAX_IMAGE_BYTES:
        raise CloudflareImageError(MSG_IMAGE_TOO_BIG, kind=KIND_SHAPE, status_code=status)
    return data


# ------------------------------------------------------------------ client


class CloudflareImageClient:
    """Gọi Cloudflare Workers AI: tạo một ảnh từ một prompt, kiểm token. Tạo mới cho từng lượt
    dùng (không giữ trong ``st.session_state``, không ``st.cache_resource``)."""

    def __init__(
        self,
        account_id: str,
        token: str,
        *,
        session: requests.Session | None = None,
        timeout: float = TIMEOUT_SECONDS,
    ) -> None:
        if not isinstance(account_id, str) or not _ACCOUNT_ID.fullmatch(account_id):
            raise CloudflareImageError(MSG_BAD_ACCOUNT, kind=KIND_AUTH)
        if not isinstance(token, str) or not _TOKEN.fullmatch(token):
            raise CloudflareImageError(MSG_BAD_TOKEN, kind=KIND_AUTH)
        self._account_id = account_id
        self._auth = _Bearer(token)
        self._session = session if session is not None else requests.Session()
        self._session.max_redirects = 0  # không theo chuyển hướng (LC-T140-1)
        self.timeout = min(float(timeout), TIMEOUT_SECONDS) if timeout > 0 else TIMEOUT_SECONDS

    def __repr__(self) -> str:
        return "CloudflareImageClient(***)"  # không in mã tài khoản, token

    @classmethod
    def from_settings(
        cls, settings: Settings | None = None, *, session: requests.Session | None = None
    ) -> CloudflareImageClient:
        """Client từ ``.env``. Thiếu mã tài khoản hay token: ``CloudflareImageError`` (chỉ báo
        khi tạo ảnh hay kiểm kết nối, không báo khi mở trang)."""
        settings = settings if settings is not None else load_settings()
        if not settings.cloudflare_account_id or not settings.cloudflare_api_token:
            raise CloudflareImageError(MSG_NO_KEYS, kind=KIND_AUTH)
        return cls(settings.cloudflare_account_id, settings.cloudflare_api_token, session=session)

    def generate(
        self, prompt: str, *, model: str = FLUX_SCHNELL, steps: int = IMAGE_STEPS_DEFAULT
    ) -> CloudflareImage:
        """Tạo một ảnh. Một lần gọi là một lệnh tới Cloudflare (tốn neuron), không tự thử lại."""
        model = check_model(model)
        steps = check_steps(steps)
        prompt = check_prompt(prompt)
        path = f"accounts/{self._account_id}/ai/run/{model}"
        status, data, content_type = self._call(
            "POST", path, {"prompt": prompt, "steps": steps}, MAX_RESPONSE_BYTES
        )
        answer = _answer(status, data, content_type)
        return CloudflareImage(
            data=_image_bytes(answer, status), model=model, steps=steps, prompt=prompt
        )

    def verify_token(self) -> str:
        """«Kiểm tra kết nối» (chỉ khi người dùng bấm, không tốn neuron): trạng thái token
        (``active``, ``disabled``, ``expired``). Chỉ đúng với token của người dùng (My Profile →
        API Tokens); không chứng minh quyền Workers AI (LC-T140-8)."""
        status, data, content_type = self._call("GET", VERIFY_PATH, None, MAX_VERIFY_RESPONSE_BYTES)
        answer = _answer(status, data, content_type)
        result = answer.get("result")
        state = result.get("status") if isinstance(result, dict) else None
        if not isinstance(state, str) or state not in TOKEN_STATUSES:
            raise CloudflareImageError(
                MSG_BAD_DATA.format(code=status), kind=KIND_SHAPE, status_code=status
            )
        return state

    def _call(self, method: str, path: str, body: object, limit: int) -> tuple[int, bytes, str]:
        url = API_BASE + path
        if urlsplit(url).hostname != API_HOST:  # phòng thêm: đường ghép từ hằng và giá trị đã kiểm
            raise CloudflareImageError(MSG_BLOCKED, kind=KIND_BAD_REQUEST)
        try:
            response = self._session.request(
                method,
                url,
                json=body,
                timeout=self.timeout,
                allow_redirects=False,
                stream=True,
                auth=self._auth,
                hooks={"response": [_refuse_redirect]},
            )
        except _Redirected as exc:
            # 3xx (có hay không có Location): đã đóng, không đọc thân, không đi theo.
            raise CloudflareImageError(
                MSG_REDIRECT.format(code=exc.status), kind=KIND_SHAPE, status_code=exc.status
            ) from None
        except requests.exceptions.TooManyRedirects as exc:
            code = _close_and_status(exc)
            raise CloudflareImageError(
                MSG_REDIRECT.format(code=code or "3xx"), kind=KIND_SHAPE, status_code=code
            ) from None
        except requests.exceptions.SSLError:
            raise CloudflareImageError(MSG_SSL, kind=KIND_NETWORK) from None
        except requests.exceptions.Timeout:
            raise CloudflareImageError(MSG_NETWORK, kind=KIND_TIMEOUT) from None
        except requests.exceptions.ConnectionError:
            raise CloudflareImageError(MSG_NETWORK, kind=KIND_NETWORK) from None
        except (requests.RequestException, OSError, ValueError) as exc:
            # Tên lớp lỗi là chữ cố định; không chép ``str(exc)`` (chứa URL, tức mã tài khoản).
            raise CloudflareImageError(
                MSG_NETWORK_OTHER.format(kind=type(exc).__name__), kind=KIND_NETWORK
            ) from None
        status = response.status_code
        try:
            if 300 <= status < 400:  # phòng thêm (móc đã chặn mọi 3xx trước khi tới đây)
                raise CloudflareImageError(
                    MSG_REDIRECT.format(code=status), kind=KIND_SHAPE, status_code=status
                )
            content_type = str(response.headers.get("Content-Type", ""))
            return status, _read_limited(response, limit), content_type
        except _TooLarge:
            raise CloudflareImageError(MSG_TOO_BIG, kind=KIND_SHAPE, status_code=status) from None
        except (requests.RequestException, OSError):
            raise CloudflareImageError(MSG_NETWORK, kind=KIND_NETWORK, status_code=status) from None
        finally:
            response.close()

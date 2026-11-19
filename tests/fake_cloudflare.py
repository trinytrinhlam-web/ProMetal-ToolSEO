"""Cloudflare Workers AI giả cho test (T-142): lệnh tạo ảnh ``ai/run`` và lệnh kiểm token.

Gắn vào ``requests.Session`` như ``FakeGoogle``; không gọi mạng thật (bộ chặn mạng của
``tests/conftest.py`` vẫn bật). Tìm đường theo **địa chỉ đầy đủ** (máy chủ + đường, bỏ ``?…``), ghi
lại cả tùy chọn gửi (``timeout``, ``allow_redirects``, ``stream``), trả thân qua ``raw`` (đọc theo
luồng như thật). Mã tài khoản, mã truy cập là chữ bịa đúng dạng.
"""

from __future__ import annotations

import base64
import io
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import requests
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

ACCOUNT = "ab" * 16  # mã tài khoản giả, đúng dạng 32 hex (chuỗi đơn điệu: không giống bí mật)
MA_GIA = "cfut_ma-truy-cap-gia-chi-de-thu-0001"  # mã truy cập giả, đúng bộ ký tự
API = "https://api.cloudflare.com/client/v4/"
RUN_URL = f"{API}accounts/{ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell"
VERIFY_URL = f"{API}user/tokens/verify"

Handler = Callable[[requests.PreparedRequest], Any]


def ok_image(data: bytes) -> dict[str, Any]:
    """Câu trả lời đúng khuôn của lệnh tạo ảnh: ảnh base64 trong ``result.image``."""
    image = base64.b64encode(data).decode("ascii")
    return {"success": True, "errors": [], "messages": [], "result": {"image": image}}


def failed(code: int | object, message: str = "loi may chu") -> dict[str, Any]:
    """Câu trả lời lỗi kiểu Cloudflare: ``errors[].code`` và ``message``."""
    return {"success": False, "errors": [{"code": code, "message": message}], "result": None}


def token_status(status: str) -> dict[str, Any]:
    return {
        "success": True,
        "errors": [],
        "messages": [{"code": 10000, "message": "This API Token is valid and active"}],
        "result": {"id": "ma-token-bia", "status": status},
    }


def json_body(request: requests.PreparedRequest) -> Any:
    return json.loads(request.body) if request.body else None


class FakeCloudflare(BaseAdapter):
    """Đăng ký (phương thức, địa chỉ không có ``?…``); handler trả thân hoặc (mã, thân, header),
    hay ném lỗi ``requests``. Thân ``bytes`` gửi nguyên, còn lại thành JSON."""

    def __init__(self) -> None:
        super().__init__()
        self.routes: dict[tuple[str, str], Handler] = {}
        self.calls: list[tuple[requests.PreparedRequest, dict[str, Any]]] = []

    @property
    def requests(self) -> list[requests.PreparedRequest]:
        return [request for request, _ in self.calls]

    def on(self, method: str, url: str, handler: Handler | Any) -> None:
        self.routes[(method, url)] = handler if callable(handler) else (lambda _r: handler)

    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        self.calls.append((request, kwargs))
        parts = urlsplit(request.url)
        key = (request.method, f"{parts.scheme}://{parts.netloc}{parts.path}")
        handler = self.routes.get(key)
        if handler is None:
            result: Any = (404, {"success": False, "errors": [{"code": 7003}]}, {})
        else:
            result = handler(request)
        if isinstance(result, BaseException):
            raise result
        status, body, headers = result if isinstance(result, tuple) else (200, result, {})
        content = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        response = requests.Response()
        response.status_code = status
        response.raw = io.BytesIO(content)  # đọc theo luồng (stream=True) như urllib3
        response.headers = CaseInsensitiveDict({"Content-Type": "application/json", **headers})
        response.url = request.url
        response.request = request
        response.encoding = "utf-8"
        return response

    def close(self) -> None:
        pass


def make_session(fake: FakeCloudflare) -> requests.Session:
    session = requests.Session()
    session.mount("https://", fake)
    session.mount("http://", fake)
    return session

"""Google giả cho test (T-097): máy chủ mã ``oauth2.googleapis.com`` và Sheets REST v4.

Gắn vào ``requests.Session`` như ``FakeWordPress``; không gọi mạng thật (bộ chặn mạng của
``tests/conftest.py`` vẫn bật). Khác ``FakeWordPress``: tìm đường theo **địa chỉ đầy đủ** (máy chủ
+ đường), ghi lại cả tùy chọn gửi (``timeout``, ``allow_redirects``, ``stream``), và trả thân qua
``raw`` (đọc theo luồng như thật). Khóa RSA sinh lúc chạy test (LC-T094-17), không có khóa cố
định trong repo.
"""

from __future__ import annotations

import base64
import io
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlsplit

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets/"
SHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-xyz"  # mã giả, đúng dạng
EMAIL = "seo-app@du-an-thu.iam.gserviceaccount.com"  # email giả
ACCESS_TOKEN = "ya29.ma-truy-cap-gia"

Handler = Callable[[requests.PreparedRequest], Any]


def new_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def pem(key: rsa.RSAPrivateKey) -> str:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("ascii")


def key_info(key: rsa.RSAPrivateKey, **changes: Any) -> dict[str, Any]:
    """Nội dung file khóa JSON đúng khuôn Google tải về (giá trị bịa, khóa sinh lúc chạy)."""
    info = {
        "type": "service_account",
        "project_id": "du-an-thu",
        "private_key_id": "0123456789abcdef0123456789abcdef01234567",
        "private_key": pem(key),
        "client_email": EMAIL,
        "client_id": "123456789012345678901",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": TOKEN_URL,
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/seo-app",
        "universe_domain": "googleapis.com",
    }
    info.update(changes)
    return {key_: value for key_, value in info.items() if value is not None}


def jwt_claims(assertion: str) -> dict[str, Any]:
    """Phần thân (claims) của JWT, không kiểm chữ ký (test kiểm chữ ký riêng)."""
    payload = assertion.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def form(request: requests.PreparedRequest) -> dict[str, str]:
    body = request.body.decode() if isinstance(request.body, bytes) else request.body or ""
    return {name: values[0] for name, values in parse_qs(body).items()}


def json_body(request: requests.PreparedRequest) -> Any:
    return json.loads(request.body) if request.body else None


def token_ok(_request: requests.PreparedRequest) -> dict[str, Any]:
    return {"access_token": ACCESS_TOKEN, "expires_in": 3599, "token_type": "Bearer"}


class FakeGoogle(BaseAdapter):
    """Đăng ký (phương thức, địa chỉ không có ``?…``); handler trả thân hoặc
    (mã, thân, header). Thân ``bytes`` gửi nguyên, còn lại thành JSON."""

    def __init__(self) -> None:
        super().__init__()
        self.routes: dict[tuple[str, str], Handler] = {}
        self.calls: list[tuple[requests.PreparedRequest, dict[str, Any]]] = []
        self.on("POST", TOKEN_URL, token_ok)

    @property
    def requests(self) -> list[requests.PreparedRequest]:
        return [request for request, _ in self.calls]

    def sheets_requests(self) -> list[requests.PreparedRequest]:
        return [r for r in self.requests if r.url.startswith(SHEETS)]

    def token_requests(self) -> list[requests.PreparedRequest]:
        return [r for r in self.requests if r.url == TOKEN_URL]

    def on(self, method: str, url: str, handler: Handler | Any) -> None:
        self.routes[(method, url)] = handler if callable(handler) else (lambda _r: handler)

    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        self.calls.append((request, kwargs))
        parts = urlsplit(request.url)
        key = (request.method, f"{parts.scheme}://{parts.netloc}{parts.path}")
        handler = self.routes.get(key)
        if handler is None:
            result: Any = (404, {"error": {"code": 404, "message": "Not found"}}, {})
        else:
            result = handler(request)
        if isinstance(result, requests.RequestException):
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


def make_session(fake: FakeGoogle) -> requests.Session:
    session = requests.Session()
    session.mount("https://", fake)
    session.mount("http://", fake)
    return session

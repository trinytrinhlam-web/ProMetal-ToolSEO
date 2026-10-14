"""WordPress giả cho test: chặn mọi request của `requests`, không gọi mạng thật."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlsplit

import requests
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

BASE_URL = "https://example.com"

Handler = Callable[[requests.PreparedRequest], Any]


class FakeWordPress(BaseAdapter):
    """Đăng ký route theo (method, path); handler trả về body hoặc (status, body, headers)."""

    def __init__(self) -> None:
        super().__init__()
        self.routes: dict[tuple[str, str], Handler] = {}
        self.requests: list[requests.PreparedRequest] = []

    def on(self, method: str, path: str, handler: Handler | Any) -> None:
        self.routes[(method, path)] = handler if callable(handler) else (lambda _r: handler)

    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        self.requests.append(request)
        path = urlsplit(request.url).path
        handler = self.routes.get((request.method, path))
        if handler is None:
            result: Any = (404, {"code": "rest_no_route", "message": "No route"}, {})
        else:
            result = handler(request)
        if isinstance(result, requests.RequestException):
            raise result
        status, body, headers = result if isinstance(result, tuple) else (200, result, {})

        response = requests.Response()
        response.status_code = status
        if isinstance(body, bytes):
            response._content = body
            content_type = "text/html"
        else:
            response._content = json.dumps(body).encode("utf-8")
            content_type = "application/json"
        response.headers = CaseInsensitiveDict({"Content-Type": content_type, **headers})
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass


def query(request: requests.PreparedRequest) -> dict[str, list[str]]:
    return parse_qs(urlsplit(request.url).query)


def make_session(fake: FakeWordPress) -> requests.Session:
    session = requests.Session()
    session.mount("https://", fake)
    session.mount("http://", fake)
    return session

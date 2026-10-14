import socket
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RealNetworkBlocked(RuntimeError):
    """Test lỡ gọi mạng thật (WordPress, AI, Google). Hãy dùng fake_wordpress / fake_ai."""


@pytest.fixture(autouse=True)
def _block_real_network(monkeypatch):
    """Chặn mọi kết nối mạng ra ngoài trong lúc chạy test (quy tắc R4, mục D3).

    Chỉ chặn socket mạng (IPv4/IPv6); socket nội bộ (AF_UNIX) vẫn được dùng.
    """

    def guarded_connect(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
        return original_connect(self, address, *args, **kwargs)

    def guarded_getaddrinfo(host, *args, **kwargs):
        raise RealNetworkBlocked(f"Test không được tra tên miền thật: {host!r}")

    def guarded_create_connection(address, *args, **kwargs):
        raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")

    original_connect = socket.socket.connect
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def fake_wp():
    from fake_wordpress import FakeWordPress

    return FakeWordPress()


@pytest.fixture
def wp_client(fake_wp):
    from fake_wordpress import BASE_URL, make_session

    from seo_app.wordpress import WordPressClient

    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))

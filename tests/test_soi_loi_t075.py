"""Soi Lỗi T-075 (rút gọn): kết nối của app dùng đúng bộ chứng chỉ ``certifi`` đã vá.

``tests/test_certifi_version.py`` (Thợ Máy) kiểm file ``certifi.where()``. File này đi tiếp một
bước: dựng client WordPress và provider Gemini của app như khi chạy thật, đi tới đúng lúc bắt tay
TLS, rồi xem ``SSLContext`` mà thư viện mạng dùng để kiểm chứng chỉ website. Ngữ cảnh đó phải bắt
buộc kiểm chứng chỉ, chứa **đúng** các gốc của ``certifi`` (không thêm kho của hệ điều hành) và
không còn gốc «emSign ECC Root CA - G3» (GHSA-6q48-6c7w-9gw2).

Không gọi mạng: bước nối TCP được thay bằng một socket chưa nối (bộ chặn mạng trong ``conftest.py``
vẫn bật), bước bắt tay thay bằng lỗi «chứng chỉ không hợp lệ» ngay khi thư viện gọi
``SSLContext.wrap_socket``. Mật khẩu ứng dụng và khóa Gemini đều là giả.

Lỗi tìm thấy (nếu có) đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T075-n``
(xem ``docs/team/reports/T-075-soi-loi.md``).
"""

from __future__ import annotations

import hashlib
import socket
import ssl

import certifi
import httpcore._backends.sync as httpcore_sync
import httpx
import pytest
import tenacity
import urllib3.util.connection as urllib3_connection

from seo_app.ai.gemini_provider import RETRY, GeminiProvider
from seo_app.wordpress.client import WordPressClient, WordPressError

MAT_KHAU_GIA = "abcd EFGH ijkl MNOP qrst UVWX"
KHOA_GIA = "AIzaSy-khoa-gia-cua-soi-loi-T075"
# Cùng giá trị với ``tests/test_certifi_version.py``: SHA-256 của gốc «emSign ECC Root CA - G3».
_VAN_TAY_BI_LO = (
    "86:a1:ec:ba:08:9c:4a:8d:3b:be:27:34:c6:12:ba:34:"
    "1d:81:3e:04:3c:f9:e8:a8:62:cd:5c:57:a3:6b:be:6b"
).replace(":", "")
# Biến môi trường làm thư viện bỏ ``certifi`` hoặc đi qua proxy. Gỡ hết để test kiểm đường mặc
# định, chạy giống nhau trên mọi máy (việc biến này thắng ``certifi`` đã ghi sổ: security.md mục 6).
_BIEN_CHUNG_CHI = ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE", "SSL_CERT_DIR")
_BIEN_PROXY = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")


def _van_tay(ctx: ssl.SSLContext) -> set[str]:
    return {hashlib.sha256(der).hexdigest() for der in ctx.get_ca_certs(binary_form=True)}


def _van_tay_certifi() -> set[str]:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cafile=certifi.where())
    return _van_tay(ctx)


@pytest.fixture
def bat_tay(monkeypatch):
    """Thay bước nối TCP và bắt tay TLS; trả danh sách ``(SSLContext, tên máy)`` đã thấy."""
    for ten in _BIEN_CHUNG_CHI + _BIEN_PROXY:
        monkeypatch.delenv(ten, raising=False)
        monkeypatch.delenv(ten.lower(), raising=False)
    # NO_PROXY=* để urllib (trên Windows: registry, trên Mac: cài đặt hệ thống) không đưa proxy vào.
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")

    sockets: list[socket.socket] = []

    def socket_chua_noi(*args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets.append(sock)
        return sock

    def connect_tcp_gia(self, host, port, *args, **kwargs):
        return httpcore_sync.SyncStream(socket_chua_noi())

    da_thay: list[tuple[ssl.SSLContext, str | None]] = []

    def wrap_socket_gia(self, sock, *args, server_hostname=None, **kwargs):
        da_thay.append((self, server_hostname))
        raise ssl.SSLCertVerificationError(
            1, "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (giả, T-075)"
        )

    monkeypatch.setattr(urllib3_connection, "create_connection", socket_chua_noi)
    monkeypatch.setattr(httpcore_sync.SyncBackend, "connect_tcp", connect_tcp_gia)
    monkeypatch.setattr(ssl.SSLContext, "wrap_socket", wrap_socket_gia)
    yield da_thay
    for sock in sockets:
        sock.close()


def _kiem_ngu_canh(da_thay, ten_may: str) -> None:
    assert da_thay, "thư viện không đi tới bước bắt tay TLS"
    goc_certifi = _van_tay_certifi()
    assert len(goc_certifi) > 100 and _VAN_TAY_BI_LO not in goc_certifi
    for ctx, may in da_thay:
        assert may == ten_may
        assert ctx.verify_mode == ssl.CERT_REQUIRED
        # Đúng bằng bộ certifi: không thiếu gốc nào, không thêm kho của hệ điều hành.
        assert _van_tay(ctx) == goc_certifi
        assert _VAN_TAY_BI_LO not in _van_tay(ctx)


def test_client_wordpress_bat_tay_bang_bo_certifi_da_va(bat_tay):
    client = WordPressClient("https://suachuacuasat.com", "bien-tap-vien", MAT_KHAU_GIA)
    with pytest.raises(WordPressError) as loi:
        client.check_connection()
    # Chứng chỉ bị từ chối thì người dùng thấy câu lỗi SSL cố định, không lộ mật khẩu.
    assert "Lỗi chứng chỉ bảo mật (SSL)" in str(loi.value)
    assert MAT_KHAU_GIA.replace(" ", "") not in str(loi.value)
    _kiem_ngu_canh(bat_tay, "suachuacuasat.com")
    assert len(bat_tay) == 1  # requests không tự thử lại


def test_gemini_bat_tay_bang_bo_certifi_da_va(bat_tay):
    provider = GeminiProvider(KHOA_GIA)
    api = provider._client._api_client
    # Giữ số lần thử lại thật của app (``RETRY``), chỉ bỏ thời gian chờ giữa các lần.
    api._retry.wait = tenacity.wait_none()
    with pytest.raises(httpx.ConnectError):
        provider._client.models.generate_content(model="gemini-2.5-flash", contents="xin chào")
    _kiem_ngu_canh(bat_tay, "generativelanguage.googleapis.com")
    assert len(bat_tay) == RETRY.attempts  # lần thử lại nào cũng dùng cùng bộ chứng chỉ

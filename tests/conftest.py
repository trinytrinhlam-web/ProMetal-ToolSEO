import functools
import socket
import threading
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Địa chỉ mà ``socket._fallback_socketpair`` dùng để nối hai đầu của cặp socket nội bộ.
_SOCKETPAIR_HOSTS = {socket.AF_INET: "127.0.0.1", socket.AF_INET6: "::1"}


class RealNetworkBlocked(RuntimeError):
    """Test lỡ gọi mạng thật (WordPress, AI, Google). Hãy dùng fake_wordpress / fake_ai."""


@pytest.fixture(autouse=True)
def _block_real_network(monkeypatch):
    """Chặn mọi kết nối mạng ra ngoài trong lúc chạy test (quy tắc R4, mục D3).

    Chỉ chặn socket mạng (IPv4/IPv6); socket nội bộ (AF_UNIX) vẫn được dùng.

    Ngoại lệ duy nhất (T-027): cặp socket nội bộ do ``socket.socketpair()`` tạo. Trên Windows
    không có AF_UNIX cho việc này nên Python tự nối hai socket qua ``127.0.0.1`` (hoặc ``::1``),
    và ``asyncio`` cần cặp này để tạo vòng lặp sự kiện (Streamlit ``AppTest``). Kết nối chỉ được
    cho qua khi hội đủ cả bốn điều kiện:

    1. đang ở **bên trong** lời gọi ``socket.socketpair()`` (hoặc ``socket._fallback_socketpair``)
       của **chính luồng đó**;
    2. socket cùng họ địa chỉ và là ``SOCK_STREAM``, như cặp socketpair;
    3. địa chỉ đích đúng là ``127.0.0.1`` (IPv4) hoặc ``::1`` (IPv6), dạng tuple;
    4. đích là một socket vừa ``listen()`` ngay trong lời gọi socketpair đó (cùng luồng).

    Ngoài lời gọi socketpair, ``connect`` tới ``127.0.0.1``, ``localhost``, ``::1`` hay bất kỳ
    đâu vẫn bị chặn; ``connect_ex``, ``getaddrinfo``, ``create_connection`` và đường nối riêng
    của asyncio trên Windows (``IocpProactor.connect``) luôn bị chặn.
    """

    state = threading.local()

    def _pair_listeners():
        return getattr(state, "listeners", None)

    def _is_socketpair_link(sock, address):
        listeners = _pair_listeners()
        if listeners is None:  # không ở trong socketpair() của luồng này
            return False
        if sock.type != socket.SOCK_STREAM or sock.family not in _SOCKETPAIR_HOSTS:
            return False
        if not isinstance(address, tuple) or len(address) < 2:
            return False
        host, port = address[0], address[1]
        if host != _SOCKETPAIR_HOSTS[sock.family]:
            return False
        return (sock.family, host, port) in listeners

    def guarded_connect(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _is_socketpair_link(
            self, address
        ):
            raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
        return original_connect(self, address, *args, **kwargs)

    def guarded_connect_ex(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
        return original_connect_ex(self, address, *args, **kwargs)

    def guarded_listen(self, *args, **kwargs):
        result = original_listen(self, *args, **kwargs)
        listeners = _pair_listeners()
        if listeners is not None and self.family in _SOCKETPAIR_HOSTS:
            host, port = self.getsockname()[:2]
            listeners.add((self.family, host, port))
        return result

    def allow_own_link(original):
        @functools.wraps(original)
        def guarded_socketpair(*args, **kwargs):
            outer = _pair_listeners()
            state.listeners = set()
            try:
                return original(*args, **kwargs)
            finally:
                state.listeners = outer

        return guarded_socketpair

    def guarded_getaddrinfo(host, *args, **kwargs):
        raise RealNetworkBlocked(f"Test không được tra tên miền thật: {host!r}")

    def guarded_create_connection(address, *args, **kwargs):
        raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_listen = socket.socket.listen
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket.socket, "listen", guarded_listen)
    monkeypatch.setattr(socket, "socketpair", allow_own_link(socket.socketpair))
    if hasattr(socket, "_fallback_socketpair"):
        # Linux/Mac có socketpair AF_UNIX thật; bọc cả bản dự phòng để test được đường Windows.
        fallback = allow_own_link(socket._fallback_socketpair)
        monkeypatch.setattr(socket, "_fallback_socketpair", fallback)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)

    # Windows: vòng lặp asyncio mặc định (Proactor) nối socket bằng ConnectEx/WSAConnect của
    # ``_overlapped``, không đi qua ``socket.connect``. Khi vòng lặp đã tạo được (nhờ ngoại lệ
    # socketpair ở trên) thì đường này phải bị chặn riêng, nếu không ``asyncio.open_connection``
    # tới một địa chỉ IP sẽ lọt ra mạng thật.
    try:
        from asyncio import windows_events
    except ImportError:  # Mac/Linux không có IocpProactor
        return

    def guarded_proactor_connect(self, conn, address, *args, **kwargs):
        if conn.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
        return original_proactor_connect(self, conn, address, *args, **kwargs)

    original_proactor_connect = windows_events.IocpProactor.connect
    monkeypatch.setattr(windows_events.IocpProactor, "connect", guarded_proactor_connect)


@pytest.fixture(autouse=True)
def _never_read_real_env(monkeypatch, tmp_path_factory):
    """Test không bao giờ đọc file ``.env`` thật hay khóa thật trong biến môi trường máy
    (Lá Chắn T-001 #5): ``load_settings()`` trỏ sang một file không tồn tại, các biến của app
    bị xóa khỏi môi trường. Test cần giá trị thì tự đặt bằng ``monkeypatch.setenv``.
    """
    import seo_app.config as config

    missing = tmp_path_factory.getbasetemp() / "khong-co-env-that.env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", missing)
    for name in config.ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _never_touch_real_drafts(monkeypatch, tmp_path_factory):
    """Test không bao giờ đọc/ghi kho nháp thật ``data/drafts.sqlite``: trang Soạn bài đọc
    ``seo_app.storage.drafts.DEFAULT_DRAFTS_FILE`` lúc chạy, nên trỏ nó sang thư mục tạm riêng
    cho từng test. Test cần kho nháp thì đọc ``seo_app.storage.drafts.DEFAULT_DRAFTS_FILE``.
    """
    import seo_app.storage.drafts as drafts

    folder = tmp_path_factory.mktemp("nhap")
    monkeypatch.setattr(drafts, "DEFAULT_DRAFTS_FILE", folder / "drafts.sqlite")


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

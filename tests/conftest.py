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
    4. đích là socket **đầu tiên** gọi ``listen()`` trong lời gọi socketpair đó (cùng luồng), và
       mỗi lời gọi socketpair chỉ được cho qua **một lần** ``connect`` (T-029).

    Ngoài lời gọi socketpair, ``connect`` tới ``127.0.0.1``, ``localhost``, ``::1`` hay bất kỳ
    đâu vẫn bị chặn. Luôn bị chặn với socket IPv4/IPv6: ``connect_ex``, gửi UDP không kết nối
    (``sendto``, ``sendmsg``; T-029). Luôn bị chặn: tra tên ``getaddrinfo``, ``gethostbyname``,
    ``gethostbyname_ex``, ``gethostbyaddr``, ``getnameinfo`` (kéo theo ``getfqdn``,
    ``loop.getaddrinfo``, ``loop.getnameinfo``), ``create_connection``, và đường riêng của
    asyncio trên Windows (``IocpProactor.connect``, ``IocpProactor.sendto``, tức
    ``loop.sock_connect``, ``loop.sock_sendto``, ``transport.sendto`` của UDP).
    """

    state = threading.local()

    def _pair_call():
        """Trạng thái lời gọi socketpair() đang chạy trên luồng này, hoặc None."""
        return getattr(state, "pair_call", None)

    def _is_socketpair_link(sock, address):
        call = _pair_call()
        if call is None:  # không ở trong socketpair() của luồng này
            return False
        if call["used"] or call["listener"] is None:  # đã dùng lượt connect duy nhất
            return False
        if sock.type != socket.SOCK_STREAM or sock.family not in _SOCKETPAIR_HOSTS:
            return False
        if not isinstance(address, tuple) or len(address) < 2:
            return False
        host, port = address[0], address[1]
        if host != _SOCKETPAIR_HOSTS[sock.family]:
            return False
        return (sock.family, host, port) == call["listener"]

    def guarded_connect(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            if not _is_socketpair_link(self, address):
                raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
            _pair_call()["used"] = True  # chỉ một lần, kể cả khi connect báo lỗi
        return original_connect(self, address, *args, **kwargs)

    def guarded_connect_ex(self, address, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
        return original_connect_ex(self, address, *args, **kwargs)

    def guarded_listen(self, *args, **kwargs):
        result = original_listen(self, *args, **kwargs)
        call = _pair_call()
        # Chỉ ghi nhận socket nghe ĐẦU TIÊN của lời gọi socketpair (đúng socket của cặp).
        if call is not None and call["listener"] is None and self.family in _SOCKETPAIR_HOSTS:
            host, port = self.getsockname()[:2]
            call["listener"] = (self.family, host, port)
        return result

    def allow_own_link(original):
        @functools.wraps(original)
        def guarded_socketpair(*args, **kwargs):
            outer = _pair_call()
            state.pair_call = {"listener": None, "used": False}
            try:
                return original(*args, **kwargs)
            finally:
                state.pair_call = outer

        return guarded_socketpair

    def guarded_sendto(self, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gửi gói tin mạng thật: {args[-1:]!r}")
        return original_sendto(self, *args, **kwargs)

    def guarded_sendmsg(self, *args, **kwargs):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RealNetworkBlocked(f"Test không được gửi gói tin mạng thật: {args[3:4]!r}")
        return original_sendmsg(self, *args, **kwargs)

    def block_name_lookup(name):
        def guarded_lookup(host, *args, **kwargs):
            raise RealNetworkBlocked(f"Test không được tra tên miền thật ({name}): {host!r}")

        return guarded_lookup

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
        # Python 3.12.4+/3.13 có bản dự phòng (đường Windows) trên mọi hệ điều hành; bọc cả nó.
        # Bản cũ hơn chỉ có nó trên Windows, và khi đó nó chính là ``socket.socketpair``.
        fallback = allow_own_link(socket._fallback_socketpair)
        monkeypatch.setattr(socket, "_fallback_socketpair", fallback)
    original_sendto = socket.socket.sendto
    monkeypatch.setattr(socket.socket, "sendto", guarded_sendto)
    if hasattr(socket.socket, "sendmsg"):  # Mac/Linux; Windows không có sendmsg
        original_sendmsg = socket.socket.sendmsg
        monkeypatch.setattr(socket.socket, "sendmsg", guarded_sendmsg)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    for name in ("gethostbyname", "gethostbyname_ex", "gethostbyaddr", "getnameinfo"):
        monkeypatch.setattr(socket, name, block_name_lookup(name))
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)

    # Windows: vòng lặp asyncio mặc định (Proactor) nối socket bằng ConnectEx/WSAConnect và gửi
    # UDP bằng WSASendTo của ``_overlapped``, không đi qua ``socket.connect``/``socket.sendto``.
    # Khi vòng lặp đã tạo được (nhờ ngoại lệ socketpair ở trên) thì các đường này phải bị chặn
    # riêng, nếu không ``asyncio.open_connection`` tới một địa chỉ IP hay ``loop.sock_sendto``,
    # ``transport.sendto`` của UDP sẽ lọt ra mạng thật.
    try:
        from asyncio import windows_events
    except ImportError:  # Mac/Linux không có IocpProactor
        windows_events = None

    if windows_events is not None:

        def guarded_proactor_connect(self, conn, address, *args, **kwargs):
            if conn.family in (socket.AF_INET, socket.AF_INET6):
                raise RealNetworkBlocked(f"Test không được gọi mạng thật: {address!r}")
            return original_proactor_connect(self, conn, address, *args, **kwargs)

        def guarded_proactor_sendto(self, conn, buf, flags=0, addr=None, *args, **kwargs):
            if conn.family in (socket.AF_INET, socket.AF_INET6):
                raise RealNetworkBlocked(f"Test không được gửi gói tin mạng thật: {addr!r}")
            return original_proactor_sendto(self, conn, buf, flags, addr, *args, **kwargs)

        original_proactor_connect = windows_events.IocpProactor.connect
        original_proactor_sendto = windows_events.IocpProactor.sendto
        monkeypatch.setattr(windows_events.IocpProactor, "connect", guarded_proactor_connect)
        monkeypatch.setattr(windows_events.IocpProactor, "sendto", guarded_proactor_sendto)

    # Cho fixture ``fallback_socketpair`` dùng đúng cách bọc ngoại lệ ở trên (T-030).
    return allow_own_link


@pytest.fixture
def fallback_socketpair(_block_real_network):
    """Đường ``socketpair()`` của Windows (nối qua ``127.0.0.1``/``::1``), đã qua bộ chặn mạng.

    Python có ``socket._fallback_socketpair`` (3.12.4 trở lên, 3.13; mọi hệ điều hành) thì dùng
    chính nó, bản đã bọc ở trên. Không có (ví dụ Python 3.12.3 trên Linux/Mac, nơi
    ``socket.socketpair`` là AF_UNIX gốc, không đi qua ``listen``/``connect``) thì dùng bản chép
    nguyên của CPython trong ``tests/windows_socketpair.py``, bọc bằng cùng ngoại lệ. Nhờ vậy các
    test "trong socketpair vẫn chặn" chạy đủ trên Windows, Linux và Mac (T-030).
    """
    if hasattr(socket, "_fallback_socketpair"):
        return socket._fallback_socketpair
    from windows_socketpair import copied_fallback_socketpair

    return _block_real_network(copied_fallback_socketpair)


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

"""T-029: bộ chặn mạng chặn thêm UDP không kết nối, các hàm tra tên cũ, và siết ngoại lệ
socketpair (D3, R4; lỗi Thấp #1, #2 trong ``docs/team/reports/T-027-la-chan.md``).

Mọi phép thử gửi UDP chỉ nhắm tới bộ nhận UDP ở loopback do chính test mở; mọi phép thử tra
tên chỉ dùng ``localhost``/``127.0.0.1``. Nếu bộ chặn hỏng, gói tin rơi vào bộ nhận của test
(và test đỏ) chứ không đi ra ngoài máy.
"""

import _socket
import asyncio
import contextlib
import socket

import pytest
from conftest import RealNetworkBlocked

QUIET = 0.3  # giây chờ xem bộ nhận có nhận được gì không


def _ipv6_loopback_usable():
    if not socket.has_ipv6:
        return False
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
            s.bind(("::1", 0))
    except OSError:
        return False
    return True


FAMILIES = {"ipv4": (socket.AF_INET, "127.0.0.1")}
if _ipv6_loopback_usable():
    FAMILIES["ipv6"] = (socket.AF_INET6, "::1")


@contextlib.contextmanager
def _udp_receiver(family=socket.AF_INET, host="127.0.0.1"):
    """Bộ nhận UDP ở loopback; bind/recv không bị chặn, chỉ chặn đường gửi."""
    r = socket.socket(family, socket.SOCK_DGRAM)
    try:
        r.bind((host, 0))
        r.settimeout(QUIET)
        yield r
    finally:
        r.close()


def _assert_nothing_arrived(receiver):
    with pytest.raises(TimeoutError):
        data = receiver.recv(64)
        pytest.fail(f"gói tin đã lọt tới bộ nhận: {data!r}")


@contextlib.contextmanager
def _listener(host="127.0.0.1"):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind((host, 0))
        srv.listen()
        yield srv
    finally:
        srv.close()


LOOP_FACTORIES = {
    # Windows: Proactor (gửi UDP bằng WSASendTo); Mac/Linux: Selector (bằng socket.sendto).
    "vong-lap-mac-dinh": asyncio.new_event_loop,
    "vong-lap-selector": asyncio.SelectorEventLoop,
}


def _run_on(factory, coro):
    loop = factory()
    errors = []
    loop.set_exception_handler(lambda _loop, context: errors.append(context))
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ------------------------------------------------------------------ UDP không kết nối


@pytest.mark.parametrize("family, host", FAMILIES.values(), ids=FAMILIES.keys())
def test_udp_sendto_blocked(family, host):
    with _udp_receiver(family, host) as r:
        s = socket.socket(family, socket.SOCK_DGRAM)
        with s:
            with pytest.raises(RealNetworkBlocked):
                s.sendto(b"lot", r.getsockname())
            with pytest.raises(RealNetworkBlocked):
                s.sendto(b"lot", 0, r.getsockname())  # dạng có flags
        _assert_nothing_arrived(r)


def test_sendto_blocked_on_tcp_socket_too():
    with _listener() as srv:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with s, pytest.raises(RealNetworkBlocked):
            s.sendto(b"lot", srv.getsockname())


@pytest.mark.parametrize("family, host", FAMILIES.values(), ids=FAMILIES.keys())
def test_udp_sendmsg_blocked(family, host):
    if not hasattr(socket.socket, "sendmsg"):
        # Windows không có sendmsg, nên không có đường này để lọt.
        assert not hasattr(_socket.socket, "sendmsg")
        return
    with _udp_receiver(family, host) as r:
        s = socket.socket(family, socket.SOCK_DGRAM)
        with s, pytest.raises(RealNetworkBlocked):
            s.sendmsg([b"lot"], [], 0, r.getsockname())
        _assert_nothing_arrived(r)


def test_sendto_and_sendmsg_are_wrapped():
    assert socket.socket.sendto is not _socket.socket.sendto
    if hasattr(_socket.socket, "sendmsg"):
        assert socket.socket.sendmsg is not _socket.socket.sendmsg


def test_socketpair_still_talks_after_udp_block():
    a, b = socket.socketpair()
    with a, b:
        a.sendall(b"van chay")
        assert b.recv(16) == b"van chay"


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
@pytest.mark.parametrize("family, host", FAMILIES.values(), ids=FAMILIES.keys())
def test_asyncio_sock_sendto_blocked(factory, family, host):
    async def main(target):
        loop = asyncio.get_running_loop()
        with socket.socket(family, socket.SOCK_DGRAM) as s:
            s.setblocking(False)
            await loop.sock_sendto(s, b"lot", target)

    with _udp_receiver(family, host) as r:
        with pytest.raises(RealNetworkBlocked):
            _run_on(factory, main(r.getsockname()))
        _assert_nothing_arrived(r)


class _RecordingProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.lost = []
        self.errors = []
        self.closed = None

    def connection_made(self, transport):
        self.closed = asyncio.get_running_loop().create_future()

    def error_received(self, exc):
        self.errors.append(exc)

    def connection_lost(self, exc):
        self.lost.append(exc)
        if not self.closed.done():
            self.closed.set_result(None)


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
@pytest.mark.parametrize("family, host", FAMILIES.values(), ids=FAMILIES.keys())
def test_asyncio_datagram_transport_sendto_blocked(factory, family, host):
    """``create_datagram_endpoint(local_addr=...)`` rồi ``transport.sendto(data, addr)``.

    asyncio không ném lỗi ra chỗ gọi ``sendto`` mà coi là lỗi nặng và đóng transport; lỗi
    ``RealNetworkBlocked`` phải tới ``connection_lost`` (hoặc ``error_received``).
    """

    async def main(target):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            _RecordingProtocol, local_addr=(host, 0), family=family
        )
        try:
            transport.sendto(b"lot", target)
            await asyncio.wait_for(protocol.closed, timeout=5)
        finally:
            transport.close()
        return protocol

    with _udp_receiver(family, host) as r:
        protocol = _run_on(factory, main(r.getsockname()))
        _assert_nothing_arrived(r)
    reasons = protocol.lost + protocol.errors
    assert any(isinstance(e, RealNetworkBlocked) for e in reasons), reasons


def test_proactor_sendto_is_wrapped_on_windows():
    try:
        from asyncio import windows_events
    except ImportError:  # Mac/Linux không có IocpProactor; đường gửi đi qua socket.sendto
        return
    assert windows_events.IocpProactor.sendto.__name__ == "guarded_proactor_sendto"
    assert windows_events.IocpProactor.connect.__name__ == "guarded_proactor_connect"


# --------------------------------------------------------------------- hàm tra tên cũ


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda: socket.gethostbyname("localhost"), id="gethostbyname"),
        pytest.param(lambda: socket.gethostbyname_ex("localhost"), id="gethostbyname_ex"),
        pytest.param(lambda: socket.gethostbyaddr("127.0.0.1"), id="gethostbyaddr"),
        pytest.param(lambda: socket.getnameinfo(("127.0.0.1", 80), 0), id="getnameinfo"),
        pytest.param(lambda: socket.getfqdn("localhost"), id="getfqdn"),
        pytest.param(lambda: socket.getaddrinfo("localhost", 80), id="getaddrinfo"),
    ],
)
def test_name_lookups_blocked(call):
    with pytest.raises(RealNetworkBlocked):
        call()


@pytest.mark.parametrize(
    "name", ["gethostbyname", "gethostbyname_ex", "gethostbyaddr", "getnameinfo", "getaddrinfo"]
)
def test_name_lookups_are_wrapped(name):
    assert getattr(socket, name) is not getattr(_socket, name)


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
def test_asyncio_name_lookups_blocked(factory):
    async def lookup_name():
        await asyncio.get_running_loop().getnameinfo(("127.0.0.1", 80))

    async def lookup_addr():
        await asyncio.get_running_loop().getaddrinfo("localhost", 80)

    with pytest.raises(RealNetworkBlocked):
        _run_on(factory, lookup_name())
    with pytest.raises(RealNetworkBlocked):
        _run_on(factory, lookup_addr())


def test_gethostname_still_works():
    """Tên máy là thông tin cục bộ, không tra mạng: không chặn."""
    assert socket.gethostname()


# ------------------------------------------------------- siết ngoại lệ socketpair (#1)


def test_second_listener_inside_socketpair_is_blocked(monkeypatch):
    """Lỗi Thấp #1: trong lúc socketpair() chạy, mở thêm một socket nghe ở 127.0.0.1 rồi nối
    tới nó. Trước T-029 lọt; nay chỉ listener đầu tiên (của cặp) được tính.
    """
    guarded_listen = socket.socket.listen
    seen = []
    busy = []

    def listen_and_open_another(self, *args, **kwargs):
        result = guarded_listen(self, *args, **kwargs)
        if busy:
            return result
        busy.append(1)
        try:
            with _listener() as extra:
                probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    probe.connect(extra.getsockname())
                except RealNetworkBlocked:
                    seen.append("chặn")
                else:
                    seen.append("lọt")
                finally:
                    probe.close()
        finally:
            busy.clear()
        return result

    monkeypatch.setattr(socket.socket, "listen", listen_and_open_another)
    a, b = socket._fallback_socketpair(socket.AF_INET)
    with a, b:
        a.sendall(b"x")
        assert b.recv(1) == b"x"
    assert seen == ["chặn"]


def test_second_connect_to_pair_listener_is_blocked(monkeypatch):
    """Mỗi lời gọi socketpair() chỉ được một lần connect: socket thứ hai nối tới đúng cổng
    của cặp vẫn bị chặn, còn cặp vẫn tạo được.
    """
    original_accept = socket.socket.accept
    seen = []

    def accept_after_extra_connect(self):
        if not seen:
            probe = socket.socket(self.family, socket.SOCK_STREAM)
            try:
                probe.connect(self.getsockname()[:2])
            except RealNetworkBlocked:
                seen.append("chặn")
            else:
                seen.append("lọt")
            finally:
                probe.close()
        return original_accept(self)

    monkeypatch.setattr(socket.socket, "accept", accept_after_extra_connect)
    a, b = socket._fallback_socketpair(socket.AF_INET)
    with a, b:
        a.sendall(b"x")
        assert b.recv(1) == b"x"
    assert seen == ["chặn"]


def test_listener_after_nested_socketpair_is_blocked(monkeypatch):
    """Lồng một socketpair() khác bên trong rồi mở socket nghe mới: vẫn bị chặn."""
    guarded_listen = socket.socket.listen
    seen = []
    busy = []

    def listen_nest_then_open(self, *args, **kwargs):
        result = guarded_listen(self, *args, **kwargs)
        if busy:
            return result
        busy.append(1)
        try:
            inner_a, inner_b = socket._fallback_socketpair(socket.AF_INET)
            inner_a.close()
            inner_b.close()
            with _listener() as extra:
                probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    probe.connect(extra.getsockname())
                except RealNetworkBlocked:
                    seen.append("chặn")
                else:
                    seen.append("lọt")
                finally:
                    probe.close()
        finally:
            busy.clear()
        return result

    monkeypatch.setattr(socket.socket, "listen", listen_nest_then_open)
    a, b = socket._fallback_socketpair(socket.AF_INET)
    a.close()
    b.close()
    assert seen == ["chặn"]


def test_socketpair_fails_loudly_if_first_listener_is_not_its_own(monkeypatch):
    """Nếu có socket khác ``listen()`` trước socket của cặp, cặp không được cho qua: socketpair
    báo ``RealNetworkBlocked`` (hỏng to tiếng) chứ không âm thầm mở cửa cho socket lạ.
    """
    guarded_listen = socket.socket.listen
    extra = []

    def open_another_first(self, *args, **kwargs):
        if not extra:
            other = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            extra.append(other)
            other.bind(("127.0.0.1", 0))
            guarded_listen(other)
        return guarded_listen(self, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "listen", open_another_first)
    try:
        with pytest.raises(RealNetworkBlocked):
            socket._fallback_socketpair(socket.AF_INET)
    finally:
        for s in extra:
            s.close()


def test_consecutive_socketpairs_each_get_their_own_connect():
    pairs = [socket._fallback_socketpair(socket.AF_INET) for _ in range(3)]
    for a, b in pairs:
        with a, b:
            a.sendall(b"ok")
            assert b.recv(2) == b"ok"


def test_event_loops_still_work_after_t029():
    for factory in LOOP_FACTORIES.values():
        assert _run_on(factory, asyncio.sleep(0, result="xong")) == "xong"

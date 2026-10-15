"""T-027: bộ test chạy xanh trên Windows mà bộ chặn mạng vẫn chặn đúng (D3, R4).

Chiều "được phép": cặp socket nội bộ do ``socket.socketpair()`` tạo (trên Windows Python nối
hai đầu qua ``127.0.0.1``/``::1``), và ``asyncio.new_event_loop()`` cần cặp đó.
Chiều "vẫn bị chặn": mọi ``connect`` khác tới ``127.0.0.1``, ``localhost``, ``::1``, địa chỉ
ngoài, kể cả khi có một socket đang nghe thật trên loopback; ``getaddrinfo`` và
``create_connection`` luôn bị chặn.

Các test chạy giống nhau trên Windows, Mac, Linux: trên Mac/Linux ``socket.socketpair`` dùng
AF_UNIX nên thêm các test gọi thẳng ``socket._fallback_socketpair`` (đúng đường Windows đi).
"""

import asyncio
import contextlib
import socket
import threading

import pytest
from conftest import RealNetworkBlocked


def _ipv6_loopback_usable():
    if not socket.has_ipv6:
        return False
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.bind(("::1", 0))
    except OSError:
        return False
    return True


def _assert_pair_talks(a, b):
    a.sendall("xin chào".encode())
    assert b.recv(64) == "xin chào".encode()
    b.sendall(b"ok")
    assert a.recv(8) == b"ok"


@contextlib.contextmanager
def _listener(family=socket.AF_INET, host="127.0.0.1"):
    """Một socket đang nghe thật trên loopback (bind/listen không bị chặn, chỉ connect)."""
    srv = socket.socket(family, socket.SOCK_STREAM)
    try:
        srv.bind((host, 0))
        srv.listen()
        yield srv
    finally:
        srv.close()


# ------------------------------------------------------------- chiều "được phép"


def test_socketpair_works_in_tests():
    a, b = socket.socketpair()
    with a, b:
        _assert_pair_talks(a, b)


def test_fallback_socketpair_ipv4_works_in_tests():
    """Đường Windows: hai socket nối qua 127.0.0.1 bên trong socketpair()."""
    a, b = socket._fallback_socketpair(socket.AF_INET)
    with a, b:
        assert a.family == socket.AF_INET
        assert a.getsockname()[0] == "127.0.0.1"
        _assert_pair_talks(a, b)


@pytest.mark.skipif(not _ipv6_loopback_usable(), reason="máy không có IPv6 loopback")
def test_fallback_socketpair_ipv6_works_in_tests():
    a, b = socket._fallback_socketpair(socket.AF_INET6)
    with a, b:
        assert a.getsockname()[0] == "::1"
        _assert_pair_talks(a, b)


def test_new_event_loop_works_in_tests():
    loop = asyncio.new_event_loop()
    try:
        assert loop.run_until_complete(asyncio.sleep(0, result="xong")) == "xong"
    finally:
        loop.close()


def test_asyncio_run_works_in_tests():
    async def main():
        await asyncio.sleep(0)
        return 42

    assert asyncio.run(main()) == 42


def test_socketpair_works_in_another_thread():
    """AppTest/asyncio có thể tạo vòng lặp ở luồng khác; ngoại lệ phải đi theo từng luồng."""
    result = {}

    def work():
        try:
            loop = asyncio.new_event_loop()
            loop.close()
            a, b = socket.socketpair()
            with a, b:
                _assert_pair_talks(a, b)
            result["ok"] = True
        except BaseException as error:  # noqa: BLE001 - đưa lỗi về luồng chính
            result["error"] = error

    t = threading.Thread(target=work)
    t.start()
    t.join(timeout=30)
    assert result == {"ok": True}


def test_streamlit_apptest_can_start():
    """Đúng triệu chứng gốc: AppTest không chạy được trên Windows vì bộ chặn."""
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string("import streamlit as st\nst.write('chào')").run(timeout=30)
    assert not at.exception
    assert at.markdown[0].value == "chào"


# ----------------------------------------------------------- chiều "vẫn bị chặn"


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "0.0.0.0", "93.184.215.14"])
def test_ipv4_connect_still_blocked(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with s, pytest.raises(RealNetworkBlocked):
        s.connect((host, 443))


@pytest.mark.parametrize("host", ["::1", "2606:2800:21f:cb07:6820:80da:af6b:8b2c"])
def test_ipv6_connect_still_blocked(host):
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    with s, pytest.raises(RealNetworkBlocked):
        s.connect((host, 443, 0, 0))
    s2 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    with s2, pytest.raises(RealNetworkBlocked):
        s2.connect((host, 443))


def test_connect_to_real_loopback_listener_still_blocked():
    """Có một socket đang nghe thật ở 127.0.0.1 (giống cách socketpair làm) vẫn không được nối."""
    with _listener() as srv:
        port = srv.getsockname()[1]
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect(("127.0.0.1", port))


def test_connect_ex_to_loopback_listener_still_blocked():
    with _listener() as srv:
        port = srv.getsockname()[1]
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect_ex(("127.0.0.1", port))


def test_ipv6_loopback_listener_still_blocked():
    if not _ipv6_loopback_usable():
        pytest.skip("máy không có IPv6 loopback")
    with _listener(socket.AF_INET6, "::1") as srv:
        port = srv.getsockname()[1]
        c = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect(("::1", port))


def test_nonblocking_connect_still_blocked():
    """socketpair dùng connect không chặn; ngoài socketpair, connect không chặn vẫn bị chặn."""
    with _listener() as srv:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.setblocking(False)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect(srv.getsockname())


def test_udp_connect_still_blocked():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with s, pytest.raises(RealNetworkBlocked):
        s.connect(("8.8.8.8", 53))


def test_connect_after_socketpair_is_blocked_again():
    """Ngoại lệ chỉ sống bên trong lời gọi socketpair(); gọi xong là chặn lại như cũ."""
    with _listener() as srv:
        a, b = socket.socketpair()
        a.close()
        b.close()
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect(srv.getsockname())


def test_connect_after_event_loop_is_blocked_again():
    loop = asyncio.new_event_loop()
    try:
        with _listener() as srv:
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with c, pytest.raises(RealNetworkBlocked):
                c.connect(srv.getsockname())
    finally:
        loop.close()


def test_failed_socketpair_does_not_leave_door_open():
    """socketpair() báo lỗi (tham số sai) thì ngoại lệ cũng phải đóng lại."""
    with pytest.raises((ValueError, OSError)):
        socket.socketpair(socket.AF_INET, socket.SOCK_DGRAM)
    with _listener() as srv:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with c, pytest.raises(RealNetworkBlocked):
            c.connect(srv.getsockname())


def test_other_thread_inside_socketpair_does_not_open_this_thread(monkeypatch):
    """Một luồng đang ở giữa socketpair() không làm luồng khác được phép nối loopback."""
    inside = threading.Event()
    release = threading.Event()
    original_accept = socket.socket.accept

    def slow_accept(self):
        if threading.current_thread().name == "dang-tao-cap":
            inside.set()
            release.wait(timeout=30)
        return original_accept(self)

    monkeypatch.setattr(socket.socket, "accept", slow_accept)
    errors = []

    def make_pair():
        try:
            a, b = socket._fallback_socketpair(socket.AF_INET)
            a.close()
            b.close()
        except BaseException as error:  # noqa: BLE001
            errors.append(error)

    t = threading.Thread(target=make_pair, name="dang-tao-cap")
    t.start()
    try:
        assert inside.wait(timeout=30)
        with _listener() as srv:
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with c, pytest.raises(RealNetworkBlocked):
                c.connect(srv.getsockname())
    finally:
        release.set()
        t.join(timeout=30)
    assert errors == []


@pytest.mark.parametrize(
    "address", [("10.0.0.1", 80), ("127.0.0.2", 80), "127.0.0.1", ("localhost", 80)]
)
def test_inside_socketpair_only_its_own_listener_is_allowed(monkeypatch, address):
    """Kể cả khi đang ở trong socketpair(), connect tới đích khác cặp của nó vẫn bị chặn.

    Giả lập bằng cách cho ``listen`` của socketpair kèm một lần connect lạ ngay trong lời gọi.
    """
    seen = []
    original_listen = socket.socket.listen  # bản đã được bộ chặn bọc

    def listen_then_try_elsewhere(self, *args, **kwargs):
        result = original_listen(self, *args, **kwargs)
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.connect(address)
        except RealNetworkBlocked:
            seen.append("chặn")
        except Exception as error:  # noqa: BLE001
            seen.append(f"lọt: {error!r}")
        else:
            seen.append("lọt")
        finally:
            probe.close()
        return result

    monkeypatch.setattr(socket.socket, "listen", listen_then_try_elsewhere)
    a, b = socket._fallback_socketpair(socket.AF_INET)
    a.close()
    b.close()
    assert seen == ["chặn"]


def test_inside_socketpair_other_loopback_listener_is_blocked(monkeypatch):
    """Trong socketpair(), một socket khác nghe ở 127.0.0.1 (không phải của cặp) vẫn bị chặn."""
    seen = []
    original_accept = socket.socket.accept

    with _listener() as outsider:
        target = outsider.getsockname()

        def accept_then_try_outsider(self):
            probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                probe.connect(target)
            except RealNetworkBlocked:
                seen.append("chặn")
            else:
                seen.append("lọt")
            finally:
                probe.close()
            return original_accept(self)

        monkeypatch.setattr(socket.socket, "accept", accept_then_try_outsider)
        a, b = socket._fallback_socketpair(socket.AF_INET)
        a.close()
        b.close()
    assert seen == ["chặn"]


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "example.com", "::1"])
def test_getaddrinfo_still_blocked(host):
    with pytest.raises(RealNetworkBlocked):
        socket.getaddrinfo(host, 443)


@pytest.mark.parametrize(
    "address", [("127.0.0.1", 8501), ("localhost", 8501), ("::1", 8501), ("example.com", 443)]
)
def test_create_connection_still_blocked(address):
    with pytest.raises(RealNetworkBlocked):
        socket.create_connection(address, timeout=1)


LOOP_FACTORIES = {
    # Windows: Proactor (nối bằng ConnectEx); Mac/Linux: Selector (nối bằng socket.connect).
    "vong-lap-mac-dinh": asyncio.new_event_loop,
    "vong-lap-selector": asyncio.SelectorEventLoop,
}


def _run_on(factory, coro):
    loop = factory()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
@pytest.mark.parametrize("host", ["127.0.0.1", "93.184.215.14", "localhost"])
def test_asyncio_open_connection_still_blocked(factory, host):
    """Địa chỉ IP thì asyncio bỏ qua getaddrinfo và nối thẳng (Windows: ConnectEx, không qua
    ``socket.connect``); vẫn phải bị chặn, kể cả khi có socket đang nghe thật ở loopback.
    """
    with _listener() as srv:
        port = srv.getsockname()[1]
        with pytest.raises(RealNetworkBlocked):
            _run_on(factory, asyncio.open_connection(host, port))


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
def test_asyncio_sock_connect_still_blocked(factory):
    async def main():
        loop = asyncio.get_running_loop()
        with _listener() as srv, socket.socket() as c:
            c.setblocking(False)
            await loop.sock_connect(c, srv.getsockname())

    with pytest.raises(RealNetworkBlocked):
        _run_on(factory, main())


@pytest.mark.parametrize("factory", LOOP_FACTORIES.values(), ids=LOOP_FACTORIES.keys())
def test_asyncio_udp_with_remote_addr_still_blocked(factory):
    async def main():
        loop = asyncio.get_running_loop()
        await loop.create_datagram_endpoint(asyncio.DatagramProtocol, remote_addr=("8.8.8.8", 53))

    with pytest.raises(RealNetworkBlocked):
        _run_on(factory, main())


# ------------------------------------------- tên test không vượt giới hạn của Windows


def test_every_test_id_fits_windows_environment_limit(request):
    """pytest đặt ``PYTEST_CURRENT_TEST=<tên test> (<giai đoạn>)``; Windows giới hạn cả chuỗi
    ``tên=giá trị`` ở 32.767 ký tự. Test có tham số dài phải đặt ``ids=`` ngắn (T-027).
    """
    too_long = [
        item.nodeid[:120] + "…"
        for item in request.session.items
        if len(f"PYTEST_CURRENT_TEST={item.nodeid} (teardown)") > 32_767
    ]
    assert too_long == []


def test_bad_json_case_keeps_100k_data():
    """Đặt tên ngắn nhưng dữ liệu thử 100.000 ký tự vẫn giữ nguyên."""
    import test_soi_loi_t016_t020 as module

    test = module.test_bad_json_in_row_gives_draft_error
    marks = [m for m in test.pytestmark if m.name == "parametrize"]
    data = marks[0].args[1]
    assert "{" * 100_000 in data
    assert '{"keyword": ' + "[" * 100_000 + "]" * 100_000 + "}" in data
    assert max(len(i) for i in marks[0].kwargs["ids"]) < 50

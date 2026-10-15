"""Bản sao đường ``socket.socketpair()`` mà Python đi trên Windows (T-030).

Trên Windows không có AF_UNIX cho ``socketpair`` nên Python tự nối hai socket TCP qua
``127.0.0.1``/``::1`` bằng ``listen`` / ``connect`` / ``accept``. Đó chính là đường mà bộ chặn mạng
trong ``conftest.py`` phải cho qua (đúng một lần) mà vẫn chặn mọi thứ khác.

Bản Python mới (3.12.4 trở lên, 3.13) giữ đường này ở ``socket._fallback_socketpair`` trên mọi
hệ điều hành, nên Linux/Mac gọi thẳng được. Bản cũ hơn (ví dụ 3.12.3 mà ``uv`` chọn trên máy
cloud) chỉ định nghĩa nó trên Windows, nên trên Linux/Mac test dùng bản sao dưới đây. Hàm chép
nguyên từ ``Lib/socket.py`` của CPython 3.13 (giấy phép PSF), chỉ đổi tên cho khớp và dùng
``contextlib.suppress`` thay ``try/except/pass``. Nó gọi ``socket.socket(...).listen``, ``connect``,
``accept`` nên đi qua đúng các hàm đã bị bộ chặn bọc.

Test lấy hàm qua fixture ``fallback_socketpair`` (``conftest.py``), không gọi file này trực tiếp.
"""

import contextlib
import socket


def copied_fallback_socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    if family == socket.AF_INET:
        host = "127.0.0.1"
    elif family == socket.AF_INET6:
        host = "::1"
    else:
        raise ValueError("Only AF_INET and AF_INET6 socket address families are supported")
    if type != socket.SOCK_STREAM:
        raise ValueError("Only SOCK_STREAM socket type is supported")
    if proto != 0:
        raise ValueError("Only protocol zero is supported")

    lsock = socket.socket(family, type, proto)
    try:
        lsock.bind((host, 0))
        lsock.listen()
        addr, port = lsock.getsockname()[:2]
        csock = socket.socket(family, type, proto)
        try:
            csock.setblocking(False)
            with contextlib.suppress(BlockingIOError, InterruptedError):
                csock.connect((addr, port))
            csock.setblocking(True)
            ssock, _ = lsock.accept()
        except BaseException:
            csock.close()
            raise
    finally:
        lsock.close()

    try:
        if ssock.getsockname() != csock.getpeername() or csock.getsockname() != ssock.getpeername():
            raise ConnectionError("Unexpected peer connection")
    except BaseException:
        ssock.close()
        csock.close()
        raise
    return (ssock, csock)

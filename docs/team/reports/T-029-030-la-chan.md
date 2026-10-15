# Biên bản bảo mật T-029 + T-030 · Bộ chặn mạng của test: UDP, tra tên, chạy được trên Linux/Mac

> **Model:** lần này Lá Chắn chạy **tạm bằng Claude Opus 5.5**, không phải Fable 5.1 như hồ sơ vai yêu cầu (Fable bị giới hạn tới 01/11; chủ dự án đã duyệt). Đề nghị kiểm lại bằng Fable sau 01/11 cùng đợt với T-018/T-022/T-024/T-027.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-029](../tickets/T-029-bo-chan-mang-udp-va-dns.md), [T-030](../tickets/T-030-test-t027-chay-tren-linux-mac.md) |
| Phạm vi | `git diff origin/main...team/T-029 -- tests/` (gốc `main` `3681140`; nhánh sau khi gộp `main`: `e11f152`). Code T-029: `89e6e8c`, `3628608`; T-030: `24c9b47`; báo cáo Soi Lỗi `efc0529` |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: không có lỗi Nghiêm trọng/Cao/Trung bình. Điều kiện **trước khi gộp vào `main`**: chạy `uv run pytest` 2 lần trên Windows, 0 hỏng (các đường chỉ có trên Windows chưa ai chạy được); thêm dòng bản quyền PSF vào `tests/windows_socketpair.py` (lỗi #1). Xem mục "Điều kiện" |

## Tóm tắt (cho chủ dự án)

Bộ test có một "hàng rào" để không test nào lỡ gọi ra mạng thật (WordPress, AI, Google). Hai phiếu này chỉ sửa hàng rào và test, **không đụng code của app**: vá nốt hai khe nhỏ tôi ghi ở T-027 (gửi gói UDP, tra tên miền kiểu cũ), thu hẹp chỗ ngoại lệ nội bộ của Python, và làm các test chạy được trên Linux/Mac. Tôi đã tự thử 17 cách lách trên hai bản Python, tất cả đều bị chặn; cả bộ test xanh trên Linux. Chỉ còn thiếu một lượt chạy trên máy Windows (phần riêng của Windows không chạy được trên máy cloud) và bổ sung một dòng ghi bản quyền cho đoạn code chép từ Python.

## Xác nhận phạm vi

```
$ git diff origin/main...HEAD --stat
 docs/team/reports/T-029-soi-loi.md | 123 ++++++++++++
 tests/conftest.py                  | 123 +++++++++---
 tests/test_soi_loi_t027.py         | 118 ++++++++++--
 tests/test_soi_loi_t029.py         | 384 +++++++++++++++++++++++++++++++++++++
 tests/windows_socketpair.py        |  58 ++++++
$ git diff origin/main...HEAD --stat -- seo_app app scripts config pyproject.toml uv.lock .claude
(trống)
```

Không có code ứng dụng, cấu hình, thư viện hay `.claude/` nào bị sửa.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp (giấy phép, không phải bảo mật) | Bản chép `_fallback_socketpair` của CPython ghi nguồn "CPython 3.13 (giấy phép PSF)" nhưng **thiếu dòng bản quyền PSF**. Điều 2 của PSF License Agreement yêu cầu bản phái sinh giữ "Copyright (c) 2001 Python Software Foundation; All Rights Reserved" (và thỏa thuận giấy phép). Điều 3 yêu cầu tóm tắt thay đổi: có, nhưng chưa đủ (ngoài đổi tên và `contextlib.suppress`, bản chép còn bỏ nhánh `sys.platform != "wasi"`, bỏ chú thích gốc, đổi `except:` thành `except BaseException:`; về hành vi trên Windows/Linux/Mac thì tương đương, đã so với `inspect.getsource(socket._fallback_socketpair)` của Python 3.13.16) | `tests/windows_socketpair.py:9-12` | Không có đường tấn công. Rủi ro là tuân thủ giấy phép nếu repo được chia sẻ ra ngoài | Thêm vào docstring: dòng bản quyền PSF nguyên văn, đường dẫn nguồn (`Lib/socket.py`, CPython 3.13, link `https://docs.python.org/3/license.html`), và liệt kê đủ ba thay đổi ở cột Mô tả. Chỉ sửa docstring, không cần Lá Chắn kiểm lại |
| 2 | Thấp | Bộ chặn chỉ xét socket họ `AF_INET`/`AF_INET6`. Các họ khác vẫn gửi/nối được: `AF_PACKET` (Linux, gửi khung Ethernet thô), `AF_BLUETOOTH`, `AF_VSOCK`, `AF_TIPC`, `AF_CAN`… Docstring `tests/conftest.py:22` nói rõ phạm vi này. Có từ trước, không phải do phiếu này | `tests/conftest.py:67,74,100,105,156,161` | **Không có đường đi vô tình.** WordPress, AI, Google đều cần IP (TCP + HTTPS); không thư viện nào trong `.venv` tự mở các họ trên. `AF_PACKET` cần quyền root/`CAP_NET_RAW`, máy Windows/Mac không có họ này. Chỉ test **cố ý** mở các họ lạ mới dùng được, ngang với lách bằng `_socket` (đã ghi ở T-027) | Không bắt buộc. Lần tới có dịp sửa `conftest.py` thì đảo cách xét cho chặt hơn: chặn mọi họ **trừ** `AF_UNIX` (danh sách cho phép thay vì danh sách chặn). Không đề nghị lập phiếu riêng |

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình. Hai lỗi Thấp của T-027 (listener thừa trong `socketpair`; UDP và tra tên cũ) **đã đóng**, xem D3.

## Phép thử lách bộ chặn

Tôi viết 17 phép thử riêng trong thư mục tạm (không thêm vào repo), chép `conftest.py` + `windows_socketpair.py` hiện tại; chỉ nhắm tới socket nghe ở loopback do chính phép thử mở. Chạy trên **Python 3.12.3** (máy cloud, không có `socket._fallback_socketpair`, test đi bản chép) và **Python 3.13.16** (có hàm thật, môi trường `uv run --isolated` tạm, không đụng `.venv`/`uv.lock`): cả hai **17/17 bị chặn**.

| Phép thử | Kết quả (3.12.3 / 3.13.16) |
|---|---|
| Trong `socketpair()`, nối tới đúng cổng của cặp bằng tên `localhost` | Chặn / Chặn |
| Trong `socketpair()`, socket UDP `connect` tới cổng của cặp | Chặn / Chặn |
| Trong `socketpair()`, `connect_ex` tới cổng của cặp | Chặn / Chặn |
| Trong `socketpair()`, `socket.create_connection` tới cổng của cặp | Chặn / Chặn |
| Luồng B đang trong `socketpair()` riêng, nối tới listener khác của tiến trình | Chặn / Chặn |
| `socketpair()` có listener đầu tiên bị ép bind `0.0.0.0` (không khớp `127.0.0.1`) | Chặn, `socketpair` hỏng to tiếng / như vậy |
| Sau `socketpair()` xong, hoặc hỏng giữa chừng (`accept` ném `OSError`), nối loopback | Chặn / Chặn |
| TCP Fast Open: `sendto(data, MSG_FASTOPEN, addr)` | Chặn / Chặn |
| `ssl.SSLSocket.connect` (lớp con của `socket.socket`) | Chặn / Chặn |
| Socket tạo bằng `dup()`, `socket.fromfd()` | Chặn / Chặn |
| `asyncio.open_connection("127.0.0.1", port)`, vòng lặp mặc định và Selector | Chặn / Chặn |
| `create_datagram_endpoint(remote_addr=...)`, cả hai vòng lặp | Chặn / Chặn |
| `urllib.request.urlopen` (http IP, https tên miền), `requests.get`, `httpx.get` | Chặn / Chặn |

Ngoài ra Soi Lỗi đã thử 6 đột biến (cố ý làm hỏng bộ chặn), test đỏ ở mọi đột biến trên cả hai bản Python (báo cáo Soi Lỗi, mục "Thử đột biến"). Tôi đã đọc lại các test tương ứng và xác nhận chúng kiểm đúng hậu quả (gói tin không tới bộ nhận, `RealNetworkBlocked` được ném), không chỉ kiểm tên hàm.

Soát thêm thư viện trong `.venv`: không có `from socket import getaddrinfo/gethostbyname/getnameinfo/gethostbyaddr/create_connection/socketpair` (kiểu giữ bản gốc lúc import, lách được vá theo thuộc tính module), không có lời gọi thẳng `_socket.socket.connect/sendto`; không có `uvloop`/`gevent`/`eventlet`/`trio`.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff chỉ có test và báo cáo; `detect-secrets` trên 5 file: 0 kết quả; soát `git log -p origin/main..HEAD`: không có khóa/mật khẩu/token |
| S2 | Đạt | Thông báo `RealNetworkBlocked` chỉ in địa chỉ đích hoặc tên miền thử (`tests/conftest.py:69,75,101,106,111,116,119,157,162`), không có header hay khóa. Không đổi code in lỗi của app |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như trên |
| W3 | Không áp dụng | Như trên |
| W4 | Không áp dụng | Như trên; không có `verify=False` (R5) |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | Không đụng lớp AI |
| A3 | Không áp dụng | Như trên |
| U1 | Không áp dụng | Không đụng giao diện |
| U2 | Không áp dụng | Như trên |
| U3 | Không áp dụng | Như trên |
| F1 | Không áp dụng | Không đọc/ghi file người dùng; test chỉ dùng `tmp_path_factory` (không đổi) |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Không có `eval`/`pickle`/`yaml.load`; `windows_socketpair.py` chỉ được import qua fixture (`tests/conftest.py:186`), không đọc file |
| D1 | Đạt | Không đổi `pyproject.toml`/`uv.lock`; chỉ dùng thư viện chuẩn (`contextlib`, `socket`, `threading`, `functools`, `_socket` trong test) |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt (kèm lỗi Thấp #2, có từ trước) | Xem chi tiết dưới |

### D3 / R4 chi tiết

**1. Ngoại lệ `socketpair`: đúng một listener, một lần connect, đúng luồng.**
- Trạng thái theo luồng: `threading.local()` (`tests/conftest.py:45-49`); mỗi lời gọi `socketpair` tạo dict riêng `{"listener": None, "used": False}` và trả lại trạng thái ngoài trong `finally` (`:89-95`), nên lồng nhau hay hỏng giữa chừng đều không để cửa mở.
- Chỉ ghi listener **đầu tiên** của lời gọi, họ IPv4/IPv6 (`:82`, điều kiện `call["listener"] is None`).
- Cho qua khi: đang trong lời gọi, chưa dùng lượt, `SOCK_STREAM`, đích là tuple, host đúng `127.0.0.1`/`::1` theo họ, và `(họ, host, cổng)` trùng listener đó (`:51-64`). Đánh dấu `used = True` **trước** khi gọi `connect` gốc (`:70`), nên kể cả `connect` không chặn ném `BlockingIOError` thì lượt cũng đã hết.
- `connect_ex` luôn bị chặn (`:73-76`), `create_connection` và tra tên luôn bị chặn.
- Test: `test_second_listener_inside_socketpair_is_blocked`, `test_second_connect_to_pair_listener_is_blocked`, `test_listener_after_nested_socketpair_is_blocked`, `test_socketpair_fails_loudly_if_first_listener_is_not_its_own`, `test_other_thread_cannot_borrow_pair_listener_mid_socketpair` (luồng chính nối tới đúng cổng của cặp ở luồng khác: chặn). Lỗi Thấp #1 của T-027: **đóng**.
- Trường hợp xấu nhất còn lại: test **cố ý** vá `listen`/`accept` để chen vào trong `socketpair` thì cũng chỉ nối được tới **chính listener của cặp**, tức một cổng loopback trong tiến trình; không ra khỏi máy.

**2. Bản chép `tests/windows_socketpair.py` không mở đường mới.**
- So từng dòng với `socket._fallback_socketpair` của Python 3.13.16: cùng logic (kiểm họ/kiểu/proto, `bind` host loopback cổng 0, `listen`, `connect` không chặn, `accept`, kiểm `getsockname`/`getpeername` hai đầu). Khác biệt: xem lỗi #1, không đổi hành vi.
- Nó gọi `socket.socket(...)`, tức lớp đã bị vá; mọi `listen`/`connect`/`accept` đi qua bộ chặn.
- Chỉ dùng được qua fixture `fallback_socketpair` (`tests/conftest.py:174-188`), luôn được bọc bằng **cùng** `allow_own_link` (cùng trạng thái theo luồng) như hàm thật. Có hàm của Python thì fixture trả **chính hàm đó** (đã bọc), không dùng bản chép (`test_fallback_fixture_uses_python_own_function_when_present`).
- App và `socket.socketpair()` không bao giờ gọi bản chép; nó không được đăng ký vào module `socket`.
- `_block_real_network` nay trả về `allow_own_link` (`:171`). Test nào xin fixture này có thể bọc một hàm bất kỳ, nhưng hàm bọc vẫn chỉ được **một** lần nối tới **listener đầu tiên** của chính nó ở loopback; không thêm khả năng ra mạng.

**3. Nhánh theo hệ điều hành / `hasattr`.**
- `hasattr(socket, "_fallback_socketpair")` (`:128`): thiếu thì không có gì để bọc; `socket.socketpair` vẫn được bọc ở `:127`. Trên Linux/Mac 3.12.3, `socketpair` là AF_UNIX gốc, không đi `connect` IPv4/IPv6. Không có đường mở.
- `hasattr(socket.socket, "sendmsg")` (`:135`): thiếu (Windows) thì `_socket.socket` cũng thiếu, không có đường (`test_udp_sendmsg_blocked` khẳng định điều này).
- `from asyncio import windows_events` (`:148-151`): Linux/Mac ném `ImportError` vì không có `_overlapped`; ở đó vòng lặp asyncio đi Selector, dùng `socket.connect`/`socket.sendto` đã bị chặn (phép thử `asyncio.open_connection`, `sock_sendto`, `transport.sendto` trên cả hai vòng lặp: chặn). Trên Windows, đổi `return` sớm (bản T-027) thành `if` không bỏ sót dòng chặn nào: mọi dòng chặn chung nằm **trước** khối này; `return allow_own_link` nằm sau.
- `IocpProactor`: bọc `connect` (ConnectEx, và `WSAConnect` cho UDP nằm trong chính `connect`) và `sendto` (WSASendTo). Các phương thức còn lại (`send`, `sendfile`, `recv*`, `accept`) chỉ dùng được trên socket **đã** nối, tức phải qua `connect` đã chặn. `connect_pipe` là named pipe cục bộ. **Không kiểm được trên Linux** (xem mục "Phần chưa kiểm được").

**4. UDP và tra tên (lỗi Thấp #2 của T-027): đóng.**
- `socket.socket.sendto`, `sendmsg` chặn mọi socket IPv4/IPv6, có hay không có địa chỉ (`:99-107,133-137`): chặt hơn yêu cầu, và bộ test vẫn xanh nên không test nào cần chúng.
- `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo` (`:139-140`), `getaddrinfo` (`:138`); kéo theo `getfqdn`, `loop.getaddrinfo`, `loop.getnameinfo` (test `test_name_lookups_blocked`, `test_asyncio_name_lookups_blocked`). `gethostname` (cục bộ) vẫn chạy.
- Test UDP dùng bộ nhận loopback tự mở, kiểm cả "ném lỗi" lẫn "không có gói nào tới" (`_assert_nothing_arrived`).

**R5 (không nới lỏng):** không test nào bị xóa, tắt hay `xfail` mới. Bỏ qua chỉ theo tính năng có thật:

| Test | Điều kiện | Hợp lý? | Test thay thế chạy mọi máy |
|---|---|---|---|
| `test_fallback_socketpair_ipv6_works_in_tests`, `test_ipv6_loopback_listener_still_blocked` (có từ T-027) | `_ipv6_loopback_usable()` | Có: không bind được `::1` thì không có đường IPv6 loopback | — (kiểm "đường Windows chạy được" và "loopback bị chặn" bằng IPv4 ở các test khác) |
| `test_ipv6_connect_still_blocked[*]` (mới) | `_ipv6_sockets_available()`: tạo được socket `AF_INET6` | Có: không tạo được socket IPv6 thì không có gì để lọt | `test_ipv6_connect_blocked_by_family_check_on_any_machine[*]`: socket giả họ AF_INET6, kiểm `connect` (có/không flowinfo) và `connect_ex`; nếu lọt thì `connect` gốc ném `TypeError` (test đỏ, không nối thật) |
| Tham số `ipv6` trong `test_soi_loi_t029.py` | `FAMILIES` chỉ thêm `ipv6` khi bind được `::1` (`tests/test_soi_loi_t029.py:31-33`) | Có. Ghi chú: trên máy không IPv6 các tham số này **vắng mặt** chứ không hiện là "bỏ qua", nên khó thấy hơn. Không phải lỗi | IPv4 chạy mọi máy |
| `test_udp_sendmsg_blocked`, `test_proactor_sendto_is_wrapped_on_windows` | `return` sớm khi không có `sendmsg` / `windows_events` | Có, và nhánh `sendmsg` còn khẳng định `_socket` cũng không có | — |

Trên Linux cloud: 4 bỏ qua, đúng 4 test IPv6 ở trên (`pytest -rs`). Trên Windows/Mac có IPv6 thì cả 4 chạy.

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy: phiếu không đổi `pyproject.toml`/`uv.lock` (Chỉ Huy cho phép bỏ) | — |
| bandit | `-r tests/conftest.py tests/windows_socketpair.py`: **0 vấn đề** (224 dòng). Chạy thêm trên `tests/test_soi_loi_t027.py`, `tests/test_soi_loi_t029.py`: 39 × B101 (`assert` trong test), 1 × B104 (`tests/test_soi_loi_t027.py:127`, có từ T-027) | Có, báo nhầm (dưới) |
| detect-secrets | `scan` trên 4 file test + báo cáo Soi Lỗi: `results: {}` | Có |
| Soát lịch sử git | `git log -p origin/main..HEAD \| grep -inE "api[_-]?key\|password\|secret\|token\|sk-ant\|AIza"`: 0 dòng | Có |
| pytest (Linux, Python 3.12.3) | `uv run pytest`: **2758 passed, 4 skipped, 9 xfailed** in 139s (số lớn hơn báo cáo Soi Lỗi vì nhánh đã gộp `main` mới, có test T-026). 4 bỏ qua = 4 test IPv6; 9 xfailed là lỗi đã biết từ trước, ngoài phiếu này | Có |
| pytest (Python 3.13.16, hàm thật) | `tests/test_soi_loi_t027.py`, `test_soi_loi_t029.py`, `test_safety.py`: **114 passed, 4 skipped** (môi trường `uv run --isolated` tạm) | Có |
| ruff | `uv run ruff check .`: All checks passed! (`ruff format --check` báo `tests/test_soi_loi_t029.py:348` và 10 file khác của repo chưa định dạng; dự án không bắt buộc `ruff format`, không phải lỗi) | Có |

## Báo nhầm đã loại

- **B101** (`assert` trong test): cách viết chuẩn của pytest, test không chạy với `-O`.
- **B104** `tests/test_soi_loi_t027.py:127` (có từ T-027): chuỗi `"0.0.0.0"` là **đích bị chặn** trong test `connect`, không phải bind ra mọi giao diện.

## Phần chưa kiểm được trên Linux

Máy cloud là Linux, Python 3.12.3, không có IPv6. Những phần sau **chưa ai chạy thật** (Soi Lỗi cũng chưa):

1. **`IocpProactor.connect`/`sendto` bị bọc (`tests/conftest.py:153-168`)**: chỉ import được trên Windows. Test liên quan: `test_proactor_sendto_is_wrapped_on_windows`, `test_asyncio_sock_sendto_blocked[*-vong-lap-mac-dinh]`, `test_asyncio_datagram_transport_sendto_blocked[*-vong-lap-mac-dinh]` (trên Linux tham số "mặc định" là Selector, nên chưa kiểm đường Proactor). Theo mã nguồn CPython 3.12, `_ProactorDatagramTransport` gửi bằng `self._loop._proactor.sendto(...)` và `loop.sock_sendto` gọi `self._proactor.sendto(...)`, nên bọc ở lớp `IocpProactor` là đủ; lỗi `RealNetworkBlocked` (là `RuntimeError`) sẽ đi vào `_fatal_error` → `connection_lost`, đúng điều test chờ. Đây là suy luận từ mã nguồn, chưa chạy.
2. **Đổi `return` sớm thành `if` trong `_block_real_network`** (đường Windows): đọc kỹ thấy đúng, chưa chạy.
3. **`socket.socketpair` trên Windows** đi qua bản bọc `allow_own_link` mới (listener đầu tiên + một lần connect), dùng cho vòng lặp asyncio và Streamlit `AppTest`: nếu sai thì hàng loạt test giao diện trên Windows sẽ đỏ (hỏng to tiếng, không lọt mạng).
4. **Test IPv6 thật** (4 test bỏ qua trên cloud) và tham số `ipv6` của `test_soi_loi_t029.py`.
5. **Mac**: chưa có máy. Theo mã nguồn giống Linux (AF_UNIX, có `sendmsg`, không có `windows_events`), khác là thường có IPv6.

**Đề xuất cách Chỉ Huy A (hoặc chủ dự án) kiểm trên Windows trước khi gộp** (trên nhánh `team/T-029`, máy Windows):

```
git fetch origin
git switch team/T-029
git pull
uv run pytest -q -rs
uv run pytest -q -rs
uv run pytest -q tests/test_soi_loi_t027.py tests/test_soi_loi_t029.py tests/test_safety.py -v -k "proactor or vong-lap-mac-dinh or ipv6 or socketpair"
uv run ruff check .
```

Đạt khi: cả hai lượt 0 hỏng, 0 lỗi; dòng `-rs` **không** có bỏ qua IPv6 nào (Windows có `::1`), hoặc nếu có thì lý do đúng là máy tắt IPv6; lệnh thứ ba cho thấy `test_proactor_sendto_is_wrapped_on_windows` và các tham số `vong-lap-mac-dinh` đều **PASSED** (không phải bỏ qua). Ghi kết quả (số qua/bỏ qua, phiên bản Python `uv run python -VV`) vào `docs/team/dong-bo.md` hoặc phần bổ sung của báo cáo Soi Lỗi. Hỏng ở đây thì **không gộp**, giao lại Soi Lỗi.

## Ghi chú thêm (không phải lỗi)

- Soi Lỗi đề xuất ghim cùng bản vá Python trên mọi máy (`.python-version` hiện là `3.12`: cloud 3.12.3, Windows 3.12.15). Về bảo mật tôi đồng ý: hai máy chạy cùng một đường `socketpair` thì test chứng minh đúng thứ chạy thật. Việc này đổi môi trường, cần chủ dự án duyệt; không phải điều kiện của phiếu này.
- Trên máy có `socket._fallback_socketpair`, fixture dùng hàm thật của Python; bản chép chỉ chạy trên Python cũ (3.12.3 Linux/Mac). Nếu sau này ghim Python ≥ 3.12.4 trên mọi máy thì có thể bỏ hẳn `tests/windows_socketpair.py` (và cả lỗi #1).

## Điều kiện

Phiếu được **gộp vào `main`** khi đủ cả hai:

1. **Chạy trên Windows** theo hướng dẫn ở mục trên: 2 lượt `uv run pytest`, 0 hỏng, các test Proactor và IPv6 thật sự chạy. (Đây cũng là tiêu chí xong của chính phiếu T-029.)
2. **Lỗi #1 (Thấp):** Soi Lỗi thêm dòng bản quyền PSF và tóm tắt đủ thay đổi vào docstring `tests/windows_socketpair.py`, trên nhánh `team/T-029`. Chỉ sửa docstring thì không cần Lá Chắn kiểm lại; Chỉ Huy đối chiếu bằng `git diff` là đủ.

Lỗi #2 (Thấp, có từ trước): không cần phiếu riêng; ghi vào bảng việc để làm khi có dịp sửa `tests/conftest.py`.

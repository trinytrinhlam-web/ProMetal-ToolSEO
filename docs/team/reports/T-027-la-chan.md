# Biên bản bảo mật T-027 · Bộ test chạy xanh trên Windows

> **Lưu ý về model:** lần kiểm định này chạy **tạm bằng Opus 5.5** (`claude-opus-5-5`), vì tài khoản hiện không dùng được Fable 5.1 (cần mua thêm lượt dùng). Chủ dự án đã duyệt cho Lá Chắn chạy tạm Opus 5.5 tới 01/11. **Sau 01/11 phải kiểm lại bằng Fable** (Chỉ Huy giữ việc này trên bảng việc).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm thay Fable 5.1, xem lưu ý trên) |
| Phiếu được kiểm | [T-027](../tickets/T-027-test-chay-tren-windows.md) |
| Phạm vi | `git diff origin/main...team/T-027`, HEAD lúc kiểm `b87d3a4` (code), máy Windows 11, Python 3.12.15 (uv). File đổi: `tests/conftest.py`, `tests/test_soi_loi_t016_t020.py`, `tests/test_soi_loi_t027.py` (mới), `docs/team/reports/T-027-soi-loi.md`. Không đụng `seo_app/`, `app/`, `scripts/`, `config/`, `uv.lock`, `pyproject.toml`, `.gitignore` |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT** (không có lỗi Nghiêm trọng/Cao/Trung bình; 2 lỗi Thấp ghi sổ, đề nghị một phiếu nhỏ cho lỗi #2). Được gộp vào `main`. |

## Tóm tắt (cho chủ dự án)

Bộ test giờ chạy xanh trên Windows (2.358 qua, 0 hỏng, tôi chạy lại 2 lần), và hàng rào ngăn test gọi mạng thật **vẫn chắc**. Chỗ được nới chỉ là một việc nội bộ của Python (nối hai đầu một "ống" ngay trong chương trình, qua địa chỉ của chính máy). Tôi đã thử hơn 20 cách để lợi dụng chỗ nới đó: gọi vào máy mình qua các địa chỉ khác, gọi ngay sau lúc nới, gọi từ luồng khác, gọi qua `requests`, `httpx`, `asyncio`, SSL. Mọi cách đều bị chặn. Không có đường nào để test gọi tới WordPress, AI hay Google thật.

Còn một lỗ nhỏ có từ trước: test vẫn **gửi được gói tin UDP** và **tra được tên miền** bằng vài hàm cũ của Python. Tôi đã cho chạy cả bộ test kèm một "máy ghi" theo dõi: **không test nào** dùng tới các đường này, và không thư viện nào của app dùng chúng. Vì vậy rủi ro thấp. Tôi vẫn đề nghị một phiếu nhỏ để bịt nốt, vì sửa rất ít.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp | Trong lúc đang chạy `socketpair()`, **mọi** socket gọi `listen()` ở `127.0.0.1`/`::1` trên cùng luồng đều được ghi vào danh sách cho qua, không chỉ socket nghe của cặp. Điều kiện 4 trong docstring ("đích là socket vừa `listen()` trong lời gọi socketpair đó") đúng như code viết, nhưng rộng hơn mức cần | `tests/conftest.py:70-76` (`guarded_listen` thêm mọi listener), `tests/conftest.py:56` | Đã thử (bộ nhận loopback tự mở): vá `socket.socket.listen` để trong lúc `socket._fallback_socketpair()` chạy thì mở thêm một socket nghe ở `127.0.0.1` rồi `connect` tới nó → **lọt**. Tương tự khi lồng một `socketpair()` khác bên trong rồi mở socket nghe mới → **lọt**. Chỉ code chạy **bên trong** `socketpair()` trên **cùng luồng** mới làm được, tức là test **cố ý** vá `listen`/`accept`. Đích chỉ có thể là một cổng loopback do **chính tiến trình test** đang nghe (host phải đúng `127.0.0.1`/`::1`, cổng phải của socket vừa `listen()` trong tiến trình). Không ra được mạng, không tới được WordPress/AI/Google. Soi Lỗi đã nêu một dạng gần giống (rủi ro 3 trong báo cáo) | Không bắt buộc. Khi tiện thì siết: chỉ ghi listener **đầu tiên** trong mỗi lời gọi socketpair (`if listeners is not None and not listeners: ...`) và cho qua **một lần** (`listeners.discard(key)` ngay trước khi gọi `original_connect`). Thêm test cho hai kịch bản ở cột bên trái |
| 2 | Thấp | Bộ chặn **không chặn** gửi UDP không cần `connect` (`socket.sendto`, `loop.sock_sendto`, `IocpProactor.sendto`, `transport.sendto` của `create_datagram_endpoint(local_addr=...)`; `sendmsg` không có trên Windows nhưng có trên Mac) và **không chặn** các hàm tra tên cũ `socket.gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo` (kéo theo `socket.getfqdn`, `loop.getnameinfo`). Có từ trước T-027. Trên Windows, T-027 làm đường asyncio UDP có thể chạm tới được (trước đây vòng lặp asyncio không tạo nổi), nhưng `socket.sendto` thường thì vốn đã lọt | `tests/conftest.py:96-108` (không có dòng nào cho `sendto`/`sendmsg`/`gethostby*`/`getnameinfo`), `tests/conftest.py:119-125` (chỉ vá `IocpProactor.connect`) | Đã thử bằng bộ nhận UDP loopback tự mở: `sendto`, `loop.sock_sendto` (Proactor), `create_datagram_endpoint` + `sendto` đều **lọt** (gói tới bộ nhận). Bốn hàm tra tên vẫn là bản gốc của `_socket` (đã kiểm `socket.gethostbyname is _socket.gethostbyname`; không gọi với tên miền thật). **Đường đi vô tình hiện nay: không có.** Bằng chứng: (a) chạy toàn bộ 2.358 test kèm plugin ghi lại mọi lời gọi `sendto`/`sendmsg`/`IocpProactor.sendto`/`gethostby*`/`getnameinfo`/`getfqdn`: **0 lời gọi** (plugin đã được kiểm là bắt được, xem mục D3); (b) `requests`/`urllib3`/`httpx`/`httpcore`/`anyio`, `anthropic`, `openai`, `google-genai` đều đi TCP và tra tên qua `getaddrinfo` (đã chặn); `anyio` chỉ gửi UDP khi app tự tạo socket UDP (app không có); `seo_app/`, `app/`, `scripts/`, `tests/` không có `sendto`/`SOCK_DGRAM`/`gethostbyname`; (c) trên Python 3.12, `urllib.request.proxy_bypass_registry` (Windows, `requests` gọi khi có proxy hệ thống) không còn tra DNS. Hậu quả nếu sau này có test hay thư viện vô tình dùng: một gói UDP hoặc một truy vấn DNS (lộ tên miền cho máy chủ DNS), **không** phải một lệnh gọi WordPress/AI/Google (các dịch vụ này cần TCP + HTTPS) | Phiếu nhỏ (Soi Lỗi, Lá Chắn kiểm): trong `_block_real_network` vá thêm `socket.socket.sendto` và `sendmsg` (nếu có) → `RealNetworkBlocked` với socket `AF_INET`/`AF_INET6`; trên Windows vá `IocpProactor.sendto` (và `sendto_into` nếu có) giống cách vá `connect`; vá `socket.gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo` giống `getaddrinfo`. Kèm test dùng bộ nhận UDP loopback (`sendto`, `sock_sendto` trên cả Proactor lẫn Selector, `create_datagram_endpoint` + `sendto`) và test cho bốn hàm tra tên. Cập nhật docstring `tests/conftest.py:20-38` cho đúng phạm vi |

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình.

**Về mức của lỗi #2:** Soi Lỗi đề xuất Trung bình. Tôi xếp **Thấp** vì `security.md` mục 3 yêu cầu có đường đi thật: hiện không có test hay thư viện nào đi đường này (đã đo trên toàn bộ bộ test), và đường này không dẫn tới tài sản cần bảo vệ (khóa, site WordPress, AI, Google). Tuy vậy, sửa chỉ mất khoảng 20 dòng và làm hàng rào khớp đúng lời mô tả của nó, nên tôi vẫn đề nghị lập phiếu.

### Các điểm Soi Lỗi tự báo, đã đánh giá

- **(a) UDP không kết nối:** xem lỗi #2.
- **(b) Lách cố ý bằng `_socket`, `_overlapped`, tiến trình con:** xác nhận `_socket.socket.connect(s, addr)` lọt (đã thử với bộ nhận loopback). Đây là giới hạn cố hữu của cách vá bằng `monkeypatch`: hàng rào bắt gọi mạng **lỡ tay**, không chống test **cố tình** phá. Test do đội tự viết và đều qua Soi Lỗi/Lá Chắn, nên không xếp thành lỗi. Không đề nghị phiếu.
- **(c) Phụ thuộc tên thuộc tính của Python 3.12:** chấp nhận được, hỏng theo hướng an toàn. Nếu Python sau đổi tên `IocpProactor.connect` thì `monkeypatch.setattr` báo `AttributeError` ở mọi test (đỏ hết, không âm thầm mất chặn). Nếu Python thêm một đường ConnectEx mới không qua `IocpProactor.connect` thì `test_asyncio_open_connection_still_blocked` sẽ đỏ, vì test có một socket nghe thật ở loopback nên kết nối lọt sẽ thành công và `pytest.raises` báo hỏng. Nếu `socket._fallback_socketpair` đổi tên thì `hasattr` (`tests/conftest.py:103`) bỏ qua, nhưng trên Windows `socket.socketpair` **chính là** bản dự phòng (đã kiểm `socket.socketpair is socket._fallback_socketpair` → `True`) và đã được bọc ở dòng 102. Nếu một thư viện giữ bản `socketpair` chưa bọc (`from socket import socketpair`) thì `connect` bên trong bị chặn, tức là hỏng theo hướng **đóng**, không theo hướng mở.

## Phép thử lách bộ chặn (bộ nhận loopback tự mở, không gọi mạng ngoài)

Chạy bằng file test tạm ngoài repo (thư mục nháp của phiên), nạp đúng `tests/conftest.py` của nhánh (`-p conftest`). Kết quả:

| Phép thử | Kết quả |
|---|---|
| TCP `connect` tới socket đang nghe ở `127.0.0.2` | Chặn |
| TCP tới `::ffff:127.0.0.1` (IPv4 viết dạng IPv6) và `0.0.0.0` | Chặn |
| TCP tới socket nghe thật ở loopback **ngay sau** `socketpair()`, cùng luồng và luồng khác | Chặn |
| TCP sau một `socketpair()` bị lỗi giữa chừng (`accept` ném `OSError`) | Chặn (trạng thái `threading.local` được trả về đúng) |
| `requests.get("http://127.0.0.1:<cổng>")`, `requests.get("http://localhost:<cổng>")` | Chặn |
| `httpx.get(...)` (đồng bộ) | Chặn |
| `httpx.AsyncClient().get(...)` trên vòng lặp Proactor và Selector | Chặn (`RealNetworkBlocked` nằm trong `ExceptionGroup` của `anyio`, ném ra từ `guarded_proactor_connect` / `guarded_connect`) |
| `loop.create_connection` (Proactor), `asyncio.open_connection("::1", ...)` (Proactor) | Chặn |
| `loop.sock_connect` với socket UDP (Proactor, `WSAConnect`) | Chặn |
| `ssl.SSLContext.wrap_socket(...).connect(...)` | Chặn |
| Bên trong `socketpair()`, mở thêm socket nghe rồi nối tới (cố ý vá `listen`), có và không lồng `socketpair()` | **Lọt** tới loopback trong tiến trình (lỗi #1, Thấp) |
| UDP `sendto`, `loop.sock_sendto`, `create_datagram_endpoint` + `sendto` | **Lọt** (lỗi #2, Thấp) |
| `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo` | Không bị vá (lỗi #2, Thấp; chỉ kiểm bằng `is`, không gọi tên thật) |
| `_socket.socket.connect` (lách cố ý) | Lọt, giới hạn cố hữu (điểm b) |

Các phép thử Soi Lỗi đã viết thành test trong `tests/test_soi_loi_t027.py:127-375` (127.0.0.1, localhost, 0.0.0.0, ::1, IP ngoài, socket nghe thật, `connect_ex`, không chặn, UDP `connect`, luồng khác giữa lúc `socketpair()`, `getaddrinfo`, `create_connection`, `open_connection`/`sock_connect`/UDP `remote_addr` trên cả Proactor lẫn Selector) đều qua trên máy này.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `git log -p origin/main..team/T-027` lọc `api_key/password/secret/token/sk-ant/AIza/BEGIN PRIVATE`: 0 dòng. `detect-secrets` trên 4 file của diff: `"results": {}` |
| S2 | Đạt | Thông báo `RealNetworkBlocked` chỉ in địa chỉ đích (`tests/conftest.py:62,67,121`), không có khóa hay header. Không đổi code in lỗi của app |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đổi code WordPress (`seo_app/`, `app/` không nằm trong diff) |
| W2 | Không áp dụng | Như trên |
| W3 | Không áp dụng | Như trên |
| W4 | Không áp dụng | Như trên; test vẫn dùng `fake_wordpress` (`tests/conftest.py:159-172` không đổi) |
| A1 | Không áp dụng | Không đổi prompt hay lớp AI |
| A2 | Không áp dụng | Như trên |
| A3 | Không áp dụng | Như trên |
| U1 | Không áp dụng | Không đổi giao diện |
| U2 | Không áp dụng | Như trên |
| U3 | Không áp dụng | Như trên |
| F1 | Không áp dụng | Diff không đọc/ghi file theo đường dẫn người dùng |
| F2 | Không áp dụng | Không đổi phần ảnh |
| F3 | Đạt | Test mới không đọc/ghi file, không `eval`/`pickle`/`yaml.load`. Dữ liệu 100.000 ký tự của `test_bad_json_in_row_gives_draft_error` còn nguyên: so với `origin/main`, danh sách tham số không đổi một ký tự, chỉ thêm `ids=` (`tests/test_soi_loi_t016_t020.py:703-725`); 7 `ids` khớp 7 tham số, thu thập ra đủ 7 test (`[null]` … `[so-qua-lon]`); `test_bad_json_case_keeps_100k_data` (`tests/test_soi_loi_t027.py:393-402`) khóa điều này. Tên test dài nhất cả bộ: 16.449 ký tự, dưới giới hạn 32.767 |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi; test mới chỉ dùng thư viện chuẩn, `pytest`, `streamlit` (đã có). `pip-audit` trên đúng danh sách khóa (`uv export --frozen`, 202 dòng): `No known vulnerabilities found` |
| D2 | Đạt | `.gitignore` không đổi, vẫn chặn `.env`, `.env.*`, `*service-account*.json`, `*.sqlite`, cache (`.gitignore:2-24`) |
| D3 | Đạt (kèm lỗi Thấp #1, #2) | Chỗ nới chỉ cho `connect` khi: đang trong `socketpair()` của cùng luồng (`threading.local`, `tests/conftest.py:40-43,78-88`, khôi phục trong `finally`), `SOCK_STREAM`, host đúng `127.0.0.1`/`::1` (`:49-55`), cổng thuộc socket vừa `listen()` trong lời gọi đó (`:56,70-76`). `connect_ex` chặn hẳn (`:65-68`), `getaddrinfo`/`create_connection` chặn (`:90-94`), ConnectEx/WSAConnect của Proactor chặn (`:114-125`). 14 phép thử lách ở bảng trên bị chặn; 2 đường lọt đều không tới được mạng thật qua TCP và không có test nào dùng. Plugin ghi lại `sendto`/`sendmsg`/`IocpProactor.sendto`/`gethostby*`/`getnameinfo`/`getfqdn` trên toàn bộ bộ test: 0 lời gọi; chạy plugin trên phép thử UDP của tôi thì ghi được 3 lời gọi, chứng tỏ plugin hoạt động. `tests/test_safety.py` (bao gồm `test_real_network_is_blocked_in_tests`, `test_requests_without_fake_adapter_cannot_reach_internet`) và `tests/test_soi_loi_t027.py`: 84 qua |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uvx pip-audit`: `No known vulnerabilities found`; chạy thêm trên danh sách khóa của dự án (`uv export --format requirements-txt --no-hashes --no-emit-project --frozen` → `uvx pip-audit -r … --no-deps --disable-pip`): `No known vulnerabilities found` | Có |
| bandit | `-r seo_app app scripts`: 1 Thấp, B101 `assert` ở `seo_app/storage/drafts.py:203` (ngoài diff, đã ghi ở các biên bản trước). Chạy thêm trên `tests/conftest.py` và `tests/test_soi_loi_t027.py`: 18 × B101 (`assert` trong test, đúng cách viết test), 1 × B104 ở `tests/test_soi_loi_t027.py:127` | Có, cả hai là báo nhầm (xem dưới) |
| detect-secrets | `--all-files`: trong mã của dự án chỉ có `tests/test_config.py:34` (mật khẩu giả `"abcd efgh"`, ngoài diff, đã biết). Các báo khác đều nằm trong `.venv/` (thư viện bên thứ ba, không commit). 4 file của diff: không có báo nào | Có |
| Soát lịch sử git | `git log -p origin/main..team/T-027` (3 commit trước biên bản này), lọc như S1: 0 dòng | Có |
| pytest | Windows 11, worktree, chạy 2 lần (lúc này một Soi Lỗi khác cũng đang chạy test trên máy): `2358 passed, 10 skipped, 5 xfailed in 249.35s` và `2358 passed, 10 skipped, 5 xfailed in 249.77s` (lần 2 kèm plugin theo dõi UDP/DNS). Không test đo tốc độ nào chập chờn | Có |
| ruff | `uv run ruff check .`: `All checks passed!` | Có |

## Báo nhầm đã loại

- **bandit B104** (`tests/test_soi_loi_t027.py:127`): chuỗi `"0.0.0.0"` là **đích `connect`** mà test kiểm là bị chặn, không phải `bind` ra mọi giao diện mạng.
- **bandit B101** trong test: `assert` là cách viết test của pytest. Ở `seo_app/storage/drafts.py:203`: ngoài diff, đã xét ở các biên bản trước.
- **detect-secrets** `tests/test_config.py:34`: mật khẩu giả cho test cấu hình, không phải bí mật thật. Các báo trong `.venv/` là mã của thư viện, nằm ngoài kho mã (`.venv` bị `.gitignore` chặn).

## Ghi chú thêm (không phải lỗi)

- `test_every_test_id_fits_windows_environment_limit` (`tests/test_soi_loi_t027.py:381-390`) chỉ đo các test **trong lượt chạy hiện tại**. Khi chạy một file lẻ thì nó chỉ kiểm file đó, chạy cả bộ mới kiểm hết. Không ảnh hưởng an toàn.
- `test_streamlit_apptest_can_start` chứng minh triệu chứng gốc đã hết; 150 test đỏ lúc giao phiếu nay qua.

## Điều kiện

Không có điều kiện bắt buộc (kết luận ĐẠT). Đề nghị Chỉ Huy:

1. Lập **một phiếu nhỏ** cho lỗi #2 (chặn `sendto`/`sendmsg`/`IocpProactor.sendto` và các hàm tra tên cũ trong `tests/conftest.py`, kèm test với bộ nhận loopback). Có thể gộp phần siết lỗi #1 vào cùng phiếu. Mức Thấp, không cần làm trước khi gộp T-027.
2. Ghi lỗi #1 và #2 vào sổ rủi ro/bảng việc cho tới khi phiếu trên xong.
3. Sau 01/11: kiểm lại biên bản này bằng Fable.

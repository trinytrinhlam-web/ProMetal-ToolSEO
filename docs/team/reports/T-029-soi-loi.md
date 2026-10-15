# Báo cáo T-029 + T-030 · Bộ chặn mạng: UDP, tra tên, và chạy được trên Linux/Mac

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-029](../tickets/T-029-bo-chan-mang-udp-va-dns.md), [T-030](../tickets/T-030-test-t027-chay-tren-linux-mac.md) |
| Nhánh | `team/T-029` (code T-029: `89e6e8c`, `3628608`; T-030: `24c9b47`) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành trên Linux. **Chưa chạy trên Windows và Mac** (xem mục cuối) |

## Tóm tắt (cho chủ dự án)

Bộ test có một "hàng rào" chặn mọi kết nối mạng thật. T-029 vá nốt hai khe hở Lá Chắn đã ghi (gửi gói tin UDP, tra tên miền kiểu cũ) và siết chỗ ngoại lệ dành cho Python nội bộ. T-030 sửa các test của T-027 vốn chỉ chạy được trên Windows: trên máy Linux của cloud, `main` đang báo 9 test đỏ oan. Nay cả bộ test chạy xanh trên Linux (2.398 qua, 0 hỏng, 2 lần). Không sửa code ứng dụng, không nới lỏng hay bỏ qua test nào vô điều kiện.

## T-030 · Test của T-027 chạy được trên Linux/Mac

### Nguyên nhân (đã tái hiện trên `aece268`, Linux, Python 3.12.3)

```
$ uv run pytest tests/test_soi_loi_t027.py tests/test_soi_loi_t029.py -q
14 failed, 61 passed, 2 skipped
```

9 test của T-027 + 5 test của T-029 (cùng lỗi):

1. `AttributeError: module 'socket' has no attribute '_fallback_socketpair'` (12 test). Hàm này là đường `socketpair()` của Windows (nối hai socket qua `127.0.0.1`). Python 3.12.4+ và 3.13 có nó trên mọi hệ điều hành; Python 3.12.3 chỉ có trên Windows (máy Windows của Chỉ Huy A dùng 3.12.15 nên không thấy lỗi). Test `test_other_thread_inside_socketpair_does_not_open_this_thread` đỏ vì cùng lỗi này xảy ra trong luồng phụ.
2. `OSError: [Errno 97] Address family not supported by protocol` (2 test `test_ipv6_connect_still_blocked`): máy cloud tắt IPv6, không tạo nổi socket IPv6.

Bộ chặn trong `conftest.py` đã có sẵn `hasattr(socket, "_fallback_socketpair")`, nên **không có đường mạng nào mở** khi thiếu hàm đó; chỉ test là hỏng.

### Cách sửa

| File | Thay đổi |
|---|---|
| `tests/windows_socketpair.py` | Mới. Bản chép nguyên `_fallback_socketpair` của CPython 3.13 (giấy phép PSF), đi qua đúng `listen`/`connect`/`accept` đã bị bộ chặn bọc. |
| `tests/conftest.py` | Fixture mới `fallback_socketpair`: Python có `socket._fallback_socketpair` thì trả **chính nó** (bản đã bọc); không có thì trả bản chép, bọc bằng **cùng** hàm ngoại lệ `allow_own_link`. `_block_real_network` trả về `allow_own_link`; phần chặn riêng Windows đổi từ `return` sớm sang `if`. Không đổi logic chặn nào. |
| `tests/test_soi_loi_t027.py` | 6 test (và tham số) dùng fixture thay vì gọi thẳng `socket._fallback_socketpair`. IPv6: test socket thật chạy khi **máy tạo được socket IPv6** (`_ipv6_sockets_available`, có lý do); thêm test chạy trên mọi máy bằng socket giả họ AF_INET6. Thêm 2 test (dưới). |
| `tests/test_soi_loi_t029.py` | 5 test dùng fixture thay vì gọi thẳng `socket._fallback_socketpair`. |

Test mới:

- `test_ipv6_connect_blocked_by_family_check_on_any_machine[*]`: bộ chặn xét họ AF_INET6 trước khi nối (`connect` có/không có flowinfo, `connect_ex`). Nếu lọt, `connect` gốc nhận đối tượng lạ và ném `TypeError`: test đỏ, không có kết nối thật.
- `test_other_thread_cannot_borrow_pair_listener_mid_socketpair`: luồng A dừng ngay sau `listen()` của socketpair; luồng chính nối tới **đúng cổng của cặp** vẫn bị chặn. Phát hiện khi thử đột biến: từ khi T-029 siết listener, test luồng cũ không còn bắt được nếu trạng thái ngoại lệ bị dùng chung giữa các luồng (đột biến M3 dưới đây qua hết).
- `test_fallback_fixture_uses_python_own_function_when_present`: có hàm của Python thì fixture dùng đúng nó; bản chép chỉ dùng khi thiếu, và luôn đã được bọc.

### Bỏ qua theo tính năng (không phải "skip để qua")

| Test | Điều kiện | Trên Linux cloud |
|---|---|---|
| `test_fallback_socketpair_ipv6_works_in_tests` | có IPv6 loopback (có từ T-027) | bỏ qua |
| `test_ipv6_loopback_listener_still_blocked` | có IPv6 loopback (có từ T-027) | bỏ qua |
| `test_ipv6_connect_still_blocked[*]` (2) | tạo được socket IPv6 (mới) | bỏ qua; thay bằng test socket giả ở trên, chạy được |

Khi máy có IPv6 (Windows, Mac thường có), cả 4 test chạy đủ như trước.

## T-029 · Chặn UDP, tra tên; siết listener trong socketpair

Code của phiên trước (`89e6e8c`, `3628608`) đã đọc lại, không phải sửa logic. Kiểm thêm trên Linux:

- `sendto`/`sendmsg` bị chặn với mọi socket IPv4/IPv6 (kể cả không có địa chỉ đích): chặt hơn yêu cầu. Cả bộ test không có chỗ nào cần chúng (2.398 qua), vì socket IPv4/IPv6 không thể kết nối ngoài cặp socketpair.
- `sendmsg` không có trên Windows: bọc theo `hasattr` (`conftest.py`), test kiểm đúng điều đó.
- `IocpProactor.sendto`/`connect` chỉ bọc khi import được `asyncio.windows_events` (Windows). Trên Linux phần này không chạy; `test_proactor_sendto_is_wrapped_on_windows` chỉ kiểm khi có.
- Tra tên: `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo`, `getaddrinfo` (kéo theo `getfqdn`, `loop.getaddrinfo`, `loop.getnameinfo`) bị chặn; `gethostname` (tên máy, cục bộ) vẫn chạy. Không test nào của dự án dùng chúng.

### Thử đột biến (cố ý làm hỏng bộ chặn, test phải đỏ)

Chạy `tests/test_soi_loi_t027.py` + `tests/test_soi_loi_t029.py` với `conftest.py` bị sửa tạm, sau đó trả lại nguyên bản:

| Đột biến | Python 3.12.3 (bản chép) | Python 3.13.16 (hàm thật) |
|---|---|---|
| M1 bỏ giới hạn một lần `connect` | 1 hỏng | 1 hỏng |
| M2 ghi nhận mọi listener | 3 hỏng | 3 hỏng |
| M3 trạng thái dùng chung giữa luồng | 1 hỏng (trước khi thêm test mới: 0) | 1 hỏng |
| M4 bỏ chặn `sendto` | 7 hỏng | (không chạy) |
| M5 fixture trả bản chép chưa bọc | 13 hỏng | không áp dụng |
| M6 bỏ kiểm địa chỉ đích | 6 hỏng | 6 hỏng |

Bản gốc: 77 qua, 4 bỏ qua (cả 3.12.3 và 3.13.16). Python 3.13 chạy trong môi trường ảo riêng ở thư mục tạm, không đụng `.venv`/`uv.lock`.

## Bằng chứng

```
$ uv run pytest            # lần 1, Linux, Python 3.12.3
2398 passed, 4 skipped, 5 xfailed in 137.20s (0:02:17)

$ uv run pytest            # lần 2
2398 passed, 4 skipped, 5 xfailed in 128.93s (0:02:08)

$ uv run ruff check .
All checks passed!
```

4 bỏ qua là 4 test IPv6 ở bảng trên. 5 xfailed là lỗi thật đã biết từ trước (`xfail` trong `test_soi_loi_round4.py`, `test_soi_loi_t003_t009.py`, `test_ai_openai_gemini_soi_loi.py`), không liên quan phiếu này.

## Đối chiếu tiêu chí xong

T-030:
- [x] Linux: `uv run pytest` 0 hỏng (2 lần), `uv run ruff check .` sạch
- [x] Không test nào bị bỏ qua mà không có điều kiện tính năng rõ ràng (bảng "Bỏ qua theo tính năng")
- [x] Báo cáo (file này, gộp với T-029)

T-029:
- [ ] `uv run pytest` trên **Windows**: 0 hỏng (2 lần). **Chưa chạy** (máy cloud là Linux). Linux: đạt.
- [x] Có test cho từng đường chặn mới và phần siết listener (`tests/test_soi_loi_t029.py`)
- [x] Báo cáo `docs/team/reports/T-029-soi-loi.md`

## Rủi ro và điểm cần chú ý

- **Chưa chạy trên Windows và Mac.** Cần chạy lại trên Windows trước khi gộp (`uv run pytest` 2 lần), nhất là:
  - `IocpProactor.sendto` (chỉ có trên Windows): `test_asyncio_sock_sendto_blocked[*-vong-lap-mac-dinh]`, `test_asyncio_datagram_transport_sendto_blocked[*-vong-lap-mac-dinh]`, `test_proactor_sendto_is_wrapped_on_windows`.
  - Phần tách `return` sớm thành `if` trong `_block_real_network` (đường Windows).
  - Các test IPv6 (Windows có IPv6 nên sẽ chạy thật, trên Linux cloud đều bỏ qua).
  - Thời gian chờ: test UDP chờ 0,3 giây để chắc gói tin không tới; Windows chậm hơn vẫn chỉ làm test lâu hơn, không làm test qua oan.
- Mac: chưa có máy để chạy. Theo mã nguồn, Mac giống Linux (socketpair AF_UNIX, có `sendmsg`), khác ở chỗ thường có IPv6 nên 4 test IPv6 sẽ chạy.
- Bản chép trong `tests/windows_socketpair.py` cần giữ giống CPython; nếu Python đổi đường này, hàm thật (3.12.4+/3.13) vẫn là thứ được test ở máy có nó. Suy luận: `uv` trên Windows/Mac đang chọn 3.12 bản mới, nên ở đó test chạy trên hàm thật.

## Đề xuất

- Ghim bản vá Python: `.python-version` = `3.12` nên máy cloud dùng 3.12.3, máy Windows dùng 3.12.15. Ghim cùng bản (ví dụ `3.12.15`) giúp hai máy chạy giống nhau. Việc của Chỉ Huy/Thợ Máy, cần chủ dự án duyệt nếu coi là đổi môi trường.

## Câu hỏi cho chủ dự án

Không có.

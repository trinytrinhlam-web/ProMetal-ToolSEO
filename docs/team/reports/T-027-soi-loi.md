# Báo cáo T-027 · Bộ test chạy xanh trên Windows

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-027](../tickets/T-027-test-chay-tren-windows.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trên Windows, bộ test trước đây báo 150 test đỏ oan; nay chạy xanh hết (2.358 qua, 0 hỏng, 0 lỗi, chạy 3 lần đều vậy). Bộ chặn mạng chỉ cho qua đúng một việc nội bộ của Python (nối hai đầu một "ống" trong cùng chương trình), mọi kết nối khác, kể cả tới chính máy mình (`127.0.0.1`), vẫn bị chặn. Trong lúc làm, phát hiện và chặn thêm một đường lọt mạng riêng của Windows mà việc nới lỏng có thể mở ra. Không sửa code ứng dụng, không bỏ qua test nào.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/conftest.py` | `_block_real_network`: cho qua đúng cặp socket của `socket.socketpair()`; chặn thêm `IocpProactor.connect` (asyncio Windows); `connect_ex` chặn hẳn. |
| `tests/test_soi_loi_t016_t020.py` | `test_bad_json_in_row_gives_draft_error`: thêm `ids=` ngắn, dữ liệu thử giữ nguyên (vẫn 100.000 ký tự). |
| `tests/test_soi_loi_t027.py` | Mới, 47 test: chiều "được phép", chiều "vẫn bị chặn", giới hạn tên test của Windows. |

### Cách nới bộ chặn (`tests/conftest.py:19-125`)

`connect` của socket IPv4/IPv6 chỉ được cho qua khi hội đủ **cả bốn** điều kiện (`_is_socketpair_link`, dòng 45):

1. Đang ở **bên trong** lời gọi `socket.socketpair()` (hoặc `socket._fallback_socketpair`) **của chính luồng đó**: hai hàm này được bọc (dòng 78-88, 102-106), trạng thái để trong `threading.local`, ra khỏi lời gọi (kể cả khi lỗi) là đóng lại.
2. Socket là `SOCK_STREAM`, họ IPv4 hoặc IPv6.
3. Đích là tuple có host **đúng** `127.0.0.1` (IPv4) hoặc `::1` (IPv6); không nhận `localhost`, `127.0.0.2`, `0.0.0.0`, chuỗi trần.
4. Đích là một socket vừa `listen()` **ngay trong lời gọi socketpair đó, cùng luồng** (`guarded_listen`, dòng 70). Một socket khác đang nghe thật ở `127.0.0.1` không được tính.

Ngoài ra (dòng 110-125): trên Windows, vòng lặp asyncio mặc định (Proactor) nối socket bằng `ConnectEx`/`WSAConnect` của `_overlapped`, **không** đi qua `socket.connect`. Trước đây đường này không với tới được vì vòng lặp không tạo nổi; khi đã cho vòng lặp chạy thì `asyncio.open_connection("<địa chỉ IP>", cổng)` lọt ra mạng thật (đã tái hiện: test đỏ trước khi thêm phần chặn này). Nay `IocpProactor.connect` bị chặn cho mọi socket IPv4/IPv6.

## Bằng chứng

Trước khi sửa (`main` `ed0324e`, Windows 11, Python 3.12.15):

```
$ uv run pytest
145 failed, 2161 passed, 10 skipped, 5 xfailed, 63 warnings, 7 errors in 237.43s (0:03:57)
```

(150 test khác nhau: 145 hỏng + 5 lỗi; 2 test JSON 100k bị tính lỗi 2 lần, lúc chuẩn bị và lúc dọn.)

Sau khi sửa (commit `158442f`), chạy 3 lần:

```
$ uv run pytest
=========== 2358 passed, 10 skipped, 5 xfailed in 229.70s (0:03:49) ===========
$ uv run pytest -q
2358 passed, 10 skipped, 5 xfailed in 229.74s (0:03:49)
$ uv run pytest -q -rs
2358 passed, 10 skipped, 5 xfailed in 229.93s (0:03:49)

$ uv run ruff check .
All checks passed!
```

Đối chiếu: 2.326 test cũ (2.161 qua + 150 đỏ + 10 bỏ qua + 5 xfail) + 47 test mới = 2.373 = 2.358 + 10 + 5. Cả 150 test đỏ lúc giao phiếu nay qua. Test đo tốc độ (T-025) không chập chờn trong 3 lần chạy.

10 test bỏ qua là có sẵn từ trước, không do phiếu này: `skipif(os.name == "nt")` cho symlink và quyền tệp kiểu POSIX (`test_env_file.py:291,586,607`, `test_soi_loi_t016_t020.py:232,260,273,333`).

Tái hiện đường lọt ConnectEx (trước khi thêm dòng 110-125): `test_asyncio_open_connection_still_blocked` đỏ, lỗi đi ra từ hệ điều hành chứ không phải `RealNetworkBlocked`, tức là kết nối đã thật sự được gửi đi.

## Đối chiếu tiêu chí xong

- [x] `uv run pytest` trên Windows: 0 hỏng, 0 lỗi (3 lần, dòng tổng kết ở trên).
- [x] `uv run ruff check .` sạch.
- [x] Chiều "được phép": `test_socketpair_works_in_tests`, `test_fallback_socketpair_ipv4_works_in_tests`, `test_fallback_socketpair_ipv6_works_in_tests`, `test_new_event_loop_works_in_tests`, `test_asyncio_run_works_in_tests`, `test_socketpair_works_in_another_thread`, `test_streamlit_apptest_can_start` (`tests/test_soi_loi_t027.py:55-124`). Các test gọi thẳng `_fallback_socketpair` nên trên Mac/Linux cũng thử đúng đường Windows đi.
- [x] Chiều "vẫn bị chặn" (`tests/test_soi_loi_t027.py:128-378`): `connect` tới `127.0.0.1`, `localhost`, `0.0.0.0`, `::1`, IP ngoài (IPv4/IPv6); tới socket đang nghe thật ở loopback (IPv4/IPv6, chặn và không chặn); `connect_ex`; UDP `connect`; ngay sau `socketpair()`/sau khi tạo vòng lặp; sau `socketpair()` lỗi; luồng khác đang ở giữa `socketpair()`; bên trong `socketpair()` nhưng nối tới đích khác hoặc tới socket nghe khác; `getaddrinfo` và `create_connection` (cả loopback); `asyncio.open_connection`, `loop.sock_connect`, UDP `create_datagram_endpoint(remote_addr=...)` trên cả vòng lặp mặc định (Proactor) lẫn Selector.
- [x] Test có sẵn trong `tests/test_safety.py` vẫn qua.
- [x] Yêu cầu 3: `ids=` ngắn, dữ liệu giữ nguyên; `test_bad_json_case_keeps_100k_data` kiểm tra dữ liệu 100.000 ký tự vẫn còn.
- [x] Yêu cầu 4: đã đo tên mọi test thu thập được; sau khi sửa, dài nhất là 16.449 ký tự (`test_corrupt_files_never_crash[...]`), kế đến khoảng 10.100 (`test_soi_loi_round4.py`), đều dưới giới hạn. Thêm `test_every_test_id_fits_windows_environment_limit` để chặn tái phát ngay cả khi chạy trên Linux.
- [x] Báo cáo nộp tại `docs/team/reports/T-027-soi-loi.md`.

## Rủi ro và điểm cần chú ý (cho Lá Chắn soi)

1. **Lỗ có sẵn từ trước, ngoài phạm vi (đề xuất mức Trung bình):** bộ chặn không chặn gửi UDP không cần kết nối (`sendto`, `sendmsg`, asyncio `sock_sendto`/`IocpProactor.sendto`). Tái hiện: trong một test, `socket.socket(AF_INET, SOCK_DGRAM).sendto(b"x", ("127.0.0.1", cổng))` gửi được (đã thử với bộ nhận UDP cục bộ, không gửi ra ngoài). Mong đợi: `RealNetworkBlocked`. Thực tế: gói tin đi. Không có đường thực tế nào để lỡ gọi WordPress/AI/Google bằng UDP (các thư viện đó dùng TCP và tên miền, tên miền đã bị chặn ở `getaddrinfo`), nên không sửa trong phiếu này.
2. **Lách cố ý vẫn được** (giới hạn cố hữu của cách vá bằng `monkeypatch`, có từ trước): gọi thẳng lớp C `_socket.socket.connect`, `_overlapped`, hay chạy tiến trình con (`curl`). Bộ chặn nhằm bắt gọi mạng **lỡ tay**, không chống test cố tình phá.
3. **Bên trong `socketpair()` cùng luồng**: một socket khác cũng có thể nối tới đúng cổng của cặp đó. Chỉ code chạy giữa lời gọi `socketpair()` (tức chính hàm của Python, hoặc test cố tình vá bên trong) mới làm được, đích chỉ là socket đang nghe trong cùng chương trình ở loopback, và cặp sẽ bị Python từ chối vì kiểm tra hai đầu không khớp. Không ra được mạng thật.
4. Phần chặn `IocpProactor.connect` dựa vào tên thuộc tính trong thư viện chuẩn Python 3.12. Nếu bản Python sau đổi tên, `monkeypatch.setattr` sẽ báo lỗi ngay (không im lặng mất chặn), và `test_asyncio_open_connection_still_blocked` sẽ đỏ.
5. Hai test IPv6 loopback có `skipif` khi máy không bật được `::1` (thiếu khả năng của môi trường, không theo hệ điều hành). Trên máy Windows này chúng chạy và qua.

## Đề xuất

- Chỉ Huy cân nhắc lập phiếu nhỏ cho Soi Lỗi/Lá Chắn: chặn thêm `socket.socket.sendto`/`sendmsg` (và `IocpProactor.sendto`) với địa chỉ IPv4/IPv6 trong `tests/conftest.py`, kèm test (rủi ro 1).
- Hai tên test còn dài (16.449 và ~10.100 ký tự) chưa vượt giới hạn nhưng làm báo cáo pytest khó đọc; có thể đặt `ids=` ngắn khi có dịp sửa các file đó.

## Câu hỏi cho chủ dự án

Không có.

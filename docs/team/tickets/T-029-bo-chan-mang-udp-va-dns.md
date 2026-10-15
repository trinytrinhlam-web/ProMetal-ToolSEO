# T-029 · Bộ chặn mạng của test: chặn thêm UDP và các hàm tra tên còn hở

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-027 (đã gộp vào `main` `e4107f2`) |
| Trạng thái | Đã giao |

## Mục tiêu

Bộ chặn mạng trong `tests/conftest.py` không còn đường hở nào đã biết, ngoài các cách lách cố ý vốn không chặn được bằng monkeypatch.

## Bối cảnh

Lá Chắn kết luận T-027 **ĐẠT**, ghi 2 lỗi Thấp (`docs/team/reports/T-027-la-chan.md`):

1. `tests/conftest.py` khoảng dòng 70–76: trong lúc `socket.socketpair()` đang chạy, **mọi** socket gọi `listen()` ở loopback trên cùng luồng đều được cho nối tới, không chỉ socket của cặp.
2. `tests/conftest.py` khoảng dòng 96–125 (có từ trước T-027): gửi UDP không kết nối (`socket.sendto`, `sendmsg`, `loop.sock_sendto`, `IocpProactor.sendto`, `transport.sendto`) vẫn lọt; các hàm `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo` không bị chặn.

Lá Chắn đã chạy cả bộ test kèm plugin ghi lời gọi: hiện **0 lời gọi** tới các hàm trên, nên không có gì đang lọt. Phiếu này đóng cửa trước khi có test nào lỡ dùng.

## Phạm vi

- **Được sửa:** `tests/conftest.py`, `tests/test_soi_loi_t027.py` hoặc file test mới `tests/test_soi_loi_t029.py`.
- **Không được sửa:** code ứng dụng, các test khác.

## Yêu cầu

1. Chặn `sendto`, `sendmsg` của socket IPv4/IPv6, `IocpProactor.sendto`, và các đường asyncio gửi UDP; chặn `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, `getnameinfo`. Lỗi ném ra là `RealNetworkBlocked`.
2. Siết lỗi #1: trong `socketpair()` chỉ ghi nhận listener đầu tiên và chỉ cho qua đúng một lần `connect`.
3. Test cho từng đường chặn mới, dùng bộ nhận UDP ở loopback do test tự mở (không gửi gì ra ngoài); test cho phần siết lỗi #1. Mọi test của T-027 vẫn qua.
4. `socket.socketpair()` và `asyncio.new_event_loop()` vẫn chạy trên Windows.

## Yêu cầu bảo mật riêng

D3, R4, R5.

## Tiêu chí xong

- [ ] `uv run pytest` trên Windows: 0 hỏng, 0 lỗi (chạy 2 lần); `uv run ruff check .` sạch
- [ ] Có test cho từng đường chặn mới và cho phần siết listener
- [ ] Báo cáo nộp tại `docs/team/reports/T-029-soi-loi.md`

## Kiểm thử và kiểm định

- Soi Lỗi: là agent làm phiếu này.
- Lá Chắn: Có (D3).

## Ghi chú của Chỉ Huy

- Làm trên nhánh tạm `team/T-029`, tạo từ `main`. Không đụng file với T-026 hay T-028, nên chạy song song được khi còn chỗ.

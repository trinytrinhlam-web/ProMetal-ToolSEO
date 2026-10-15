# T-030 · Test của T-027 chạy được trên Linux và Mac

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (`main` đang đỏ trên Linux: mọi lượt kiểm trên cloud đều thấy 9 test hỏng oan) |
| Phụ thuộc | T-027 (đã gộp vào `main` `e4107f2`). Làm chung nhánh với T-029 vì cùng sửa `tests/conftest.py`, `tests/test_soi_loi_t027.py` |
| Trạng thái | Đã giao |

## Mục tiêu

`uv run pytest` xanh trên cả Windows, Linux và Mac, như hồ sơ Soi Lỗi yêu cầu. Bộ chặn mạng vẫn chặn đủ trên mọi máy.

## Bối cảnh

T-027 sửa bộ test cho Windows, đã gộp vào `main` lúc Chỉ Huy A chạy trên Windows. Chỉ Huy B chạy `main` (`f33d399`) trên Linux cloud (Python 3.12.3 do `uv` chọn theo `.python-version` = 3.12): **9 test trong `tests/test_soi_loi_t027.py` hỏng**.

- `AttributeError: module 'socket' has no attribute '_fallback_socketpair'` (dòng khoảng 309): hàm nội bộ này chỉ có ở một số bản Python (có trên Windows của A và trên Python 3.13; không có trên Linux Python 3.12.3).
  - Hỏng: `test_fallback_socketpair_ipv4_works_in_tests`, `test_inside_socketpair_only_its_own_listener_is_allowed[*]` (4 trường hợp), `test_inside_socketpair_other_loopback_listener_is_blocked`.
- `test_other_thread_inside_socketpair_does_not_open_this_thread` (dòng khoảng 244): `threading.Event.wait(timeout=30)` trả `False`. Có thể cùng nguyên nhân (trên Linux `socket.socketpair()` dùng AF_UNIX gốc, không gọi `listen`/`connect`).
- `test_ipv6_connect_still_blocked[*]` (2 trường hợp): `OSError: [Errno 97] Address family not supported by protocol`. Máy không có IPv6, nên tạo socket IPv6 hỏng trước khi tới bộ chặn.

Code ứng dụng không lỗi; lỗi nằm ở cách viết test.

## Phạm vi

- **Được sửa:** `tests/conftest.py`, `tests/test_soi_loi_t027.py`, test của T-029.
- **Không được sửa:** code ứng dụng.

## Yêu cầu

1. Test nào chỉ có nghĩa trên một loại máy thì xét **theo tính năng có thật** (ví dụ `hasattr(socket, "_fallback_socketpair")`, máy có IPv6 hay không), kèm lý do rõ. Đó không phải "skip để qua": khi tính năng có mặt, test vẫn chạy đủ và vẫn phải bắt được lỗi.
2. Nếu bộ chặn mạng trong `conftest.py` có dựa vào `_fallback_socketpair`, phải chạy đúng cả khi hàm đó không tồn tại. Không được để mở đường kết nối mạng thật trên Linux/Mac.
3. Phần kiểm "bộ chặn vẫn chặn" phải còn hiệu lực trên Linux: thêm test tương đương dùng đường có sẵn trên Linux nếu cần.
4. Chạy `uv run pytest` trên Linux (cloud) 2 lần: 0 hỏng. Ghi rõ trong báo cáo những gì **chưa chạy được trên Windows/Mac**, để Chỉ Huy A hoặc chủ dự án chạy lại trên Windows trước khi gộp.

## Yêu cầu bảo mật riêng

D3, R4 (test không gọi mạng thật trên bất kỳ máy nào), R5 (không nới lỏng).

## Tiêu chí xong

- [ ] Linux: `uv run pytest` 0 hỏng (2 lần), `uv run ruff check .` sạch
- [ ] Không test nào bị bỏ qua mà không có điều kiện tính năng rõ ràng
- [ ] Báo cáo `docs/team/reports/T-030-soi-loi.md` (có thể gộp chung với báo cáo T-029, ghi rõ phần nào của phiếu nào)

## Kiểm thử và kiểm định

- Soi Lỗi: là agent làm phiếu.
- Lá Chắn: Có (D3, R5), kiểm chung với T-029.
- Trước khi gộp: chạy lại trên Windows (Chỉ Huy A hoặc chủ dự án).

## Ghi chú của Chỉ Huy

- Làm trên nhánh `team/T-029` cùng phiếu T-029, trong phiên **"Soi Lỗi · T-029 + T-030 Bộ chặn mạng"**.

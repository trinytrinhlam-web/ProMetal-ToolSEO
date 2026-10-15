# T-027 · Bộ test chạy xanh trên Windows

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (app chạy trên Windows; test đỏ oan làm mọi lượt kiểm trên máy chủ dự án vô nghĩa) |
| Phụ thuộc | Không |
| Trạng thái | Đã giao |

## Mục tiêu

`uv run pytest` trên Windows xanh như trên Linux, mà bộ chặn mạng vẫn chặn đúng mọi kết nối thật.

## Bối cảnh

Chỉ Huy A chạy `uv run pytest` trên Windows 11 (Python 3.12 do uv cài), `main` `958a93e`: **2.161 qua, 145 hỏng, 7 lỗi**. Trên Linux (cloud) mọi test đều qua. Code ứng dụng không sai; cả hai nguyên nhân nằm ở bộ test.

**Nguyên nhân 1 (148 test, mọi test dùng `AppTest` của Streamlit):** `tests/conftest.py::_block_real_network` chặn mọi `connect` của socket IPv4/IPv6. Trên Windows, `asyncio` tạo vòng lặp sự kiện bằng `socket.socketpair()`. Windows không có `AF_UNIX` cho việc này, nên Python tự nối hai socket qua `127.0.0.1` (`socket.py` `_fallback_socketpair`). Bộ chặn coi đó là gọi mạng thật:

```
asyncio/proactor_events.py: _make_self_pipe → socket.socketpair()
socket.py:623 _fallback_socketpair → csock.connect((addr, port))
conftest.RealNetworkBlocked: Test không được gọi mạng thật: ('127.0.0.1', 54533)
```

**Nguyên nhân 2 (4 test):** `tests/test_soi_loi_t016_t020.py::test_bad_json_in_row_gives_draft_error` có tham số dài 100.000 ký tự (`"{" * 100_000`, chuỗi `[` lồng nhau). pytest ghi tên test, gồm cả tham số, vào biến môi trường `PYTEST_CURRENT_TEST`. Windows giới hạn biến môi trường 32.767 ký tự → `ValueError: the environment variable is longer than 32767 characters` ngay lúc chuẩn bị test.

Danh sách test hỏng lúc giao phiếu: Chỉ Huy A dán vào mục "Ghi chú" bên dưới (đếm theo file).

## Phạm vi

- **Được sửa:** `tests/conftest.py`, `tests/test_soi_loi_t016_t020.py`, test mới cho phần mình làm (ví dụ thêm vào `tests/test_safety.py`).
- **Không được sửa:** code ứng dụng (`seo_app/**`, `app/**`), `tests/timing.py` và `tests/test_soi_loi_t025.py` (đang thuộc T-025).
- **Ngoài phạm vi:** test đo tốc độ chập chờn (T-025); các lỗi thật khác nếu tìm thấy (ghi vào báo cáo, Chỉ Huy lập phiếu).

## Yêu cầu

1. Bộ chặn mạng cho phép **đúng** cặp socket nội bộ mà `socket.socketpair()` tạo ra trên Windows. Không mở cửa chung cho `127.0.0.1` hay `localhost`: một test tự `connect(("127.0.0.1", <cổng bất kỳ>))` vẫn phải bị chặn.
2. Thêm test chứng minh cả hai chiều: `socket.socketpair()` và `asyncio.new_event_loop()` chạy được trong test; còn `connect` tới `127.0.0.1`, `::1` và địa chỉ ngoài vẫn bị `RealNetworkBlocked`, `getaddrinfo` và `create_connection` vẫn bị chặn. Các test có sẵn trong `tests/test_safety.py` phải vẫn qua.
3. `test_bad_json_in_row_gives_draft_error` chạy được trên Windows mà **giữ nguyên** dữ liệu thử (vẫn 100.000 ký tự). Cách đề xuất: đặt `ids=` ngắn cho `parametrize`. Không bỏ qua (`skip`) theo hệ điều hành.
4. Rà mọi `parametrize` khác trong `tests/` xem còn tham số nào làm tên test dài quá 32.767 ký tự không; có thì sửa cùng cách.
5. Chạy toàn bộ `uv run pytest` **trên Windows**: 0 hỏng, 0 lỗi (trừ `xfail` có chủ đích). Chạy thêm một lần nữa để chắc không chập chờn.

## Yêu cầu bảo mật riêng

D3 và R4: bộ chặn mạng là hàng rào chính để test không bao giờ gọi WordPress, AI hay Google thật. Nới lỏng sai chỗ là lỗi Cao. R5: không tắt, bỏ qua hay xóa test.

## Tiêu chí xong

- [ ] `uv run pytest` trên Windows: 0 hỏng, 0 lỗi; dán dòng tổng kết vào báo cáo
- [ ] `uv run ruff check .` sạch
- [ ] Có test cho cả chiều "được phép" (socketpair) và chiều "vẫn bị chặn" (loopback, ngoài)
- [ ] Báo cáo nộp tại `docs/team/reports/T-027-soi-loi.md`

## Kiểm thử và kiểm định

- Soi Lỗi: là agent làm phiếu này.
- Lá Chắn: **Có**, tập trung vào bộ chặn mạng (D3): thử mọi cách lách qua chỗ đã nới.

## Ghi chú của Chỉ Huy

- Làm trên nhánh tạm `team/T-027`, tạo từ `main` `d91a80d`. Commit và đẩy lên nhánh sau từng phần lớn.
- Lúc giao, số test hỏng theo file: `test_soi_loi_t023.py` 44 · `test_settings_keys.py` 21 · `test_app_drafts.py` 18 · `test_app_pages.py` 17 · `test_soi_loi_t021_t017.py` 9 · `test_content_edge_cases.py` 9 · `test_soi_loi_t016_t020.py` 7 (4 do biến môi trường) · `test_edit_unescape.py` 6 · `test_app.py` 5 · `test_app_wordpress.py` 4 · `test_soi_loi_t003_t009.py` 3 · `test_ui_escape.py` 2 · `test_soi_loi_round3.py` 2 · `test_config_tolerance.py` 2 · `test_soi_loi_round4.py`, `test_soi_loi_round5.py`, `test_phase2_fixes.py` mỗi file 1.

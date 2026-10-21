# T-073 · Ổn định test khóa chờ của kho danh sách bài (T-037)

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 4 (test của T-037) |
| Mức ưu tiên | Trung bình (test hỏng oan làm Chỉ Huy mất thời gian mỗi lần gộp) |
| Phụ thuộc | Không |
| Trạng thái | Mới |

## Mục tiêu

`tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` không còn hỏng oan khi máy bận, mà vẫn kiểm đúng điều nó kiểm.

## Bối cảnh

Ngày 20/10 test này hỏng 2 lần khi chạy toàn bộ trên Windows lúc 3 agent cùng chạy test, và hỏng 2/3 lần khi chạy riêng file lúc máy bận ("DID NOT RAISE SiteIndexError"). Chạy lúc máy rảnh thì qua. Phỏng đoán của Chỉ Huy: luồng giữ khóa chỉ chờ `release.wait(10)`; khi máy chậm, các bước kiểm phía chính chạy quá 10 giây nên khóa tự nhả và `store.save` không còn bị chặn. Cần xác nhận.

## Phạm vi

- **Được sửa:** `tests/test_soi_loi_t037.py` (test này và các test cùng kiểu nếu có).
- **Không được sửa:** `seo_app/**`.

## Yêu cầu

1. Xác nhận nguyên nhân (ví dụ chạy dưới tải giả: nhiều tiến trình đốt CPU cùng lúc).
2. Sửa để luồng giữ khóa chỉ nhả khi phía chính đã kiểm xong (không dựa vào thời gian chờ cố định ngắn), vẫn có giới hạn để test không treo mãi; điều kiện kiểm (`load` trả `None`, `is_stale`, câu "bận", `SiteIndexError`, không xóa kho) giữ nguyên.
3. Soát các test khác dùng khung thời gian ngắn kiểu này (`release.wait(…)`, `_SQLITE_TIMEOUT` nhỏ) và sửa cùng cách nếu cần.
4. Chạy file test 20 lần dưới tải giả: 0 lần hỏng.

## Yêu cầu bảo mật riêng

Không có (chỉ test).

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên
- [ ] Test liên quan qua, `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-073-soi-loi.md`

## Kiểm thử và kiểm định

- Lá Chắn: Rút gọn (chỉ soát test không bị làm yếu, R5).

## Ghi chú của Chỉ Huy

- Lập theo ghi nhận ngày 20/10 (dong-bo 17:05, 18:24). Làm trên nhánh tạm `team/T-073`, tạo từ `main`.

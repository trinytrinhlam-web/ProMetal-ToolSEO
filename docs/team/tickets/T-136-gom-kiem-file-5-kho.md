# T-136 · Gom kiểm file 5 kho SQLite, sửa LC-T131-1, câu báo kho nháp

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-10 |
| Giai đoạn | Chung (dọn sau T-131) |
| Mức ưu tiên | Thấp (không chặn bản 1.0) |
| Phụ thuộc | T-131 đã gộp `main` |
| Trạng thái | Đang làm |

## Mục tiêu

Làm các điều kiện B.1, B.2, B.4 của Lá Chắn T-131 (`docs/team/reports/T-131-la-chan.md`): gom phần kiểm file của 5 kho SQLite (`drafts`, `site_index`, `plan_cache`, `search_cache`, kho thẻ ảnh) về một chỗ, sửa LC-T131-1, câu báo rõ hơn.

## Yêu cầu

1. **LC-T131-1 (Thấp):** (a) một ô chữ trong bảng nháp có UTF-8 hỏng thì `list_drafts` bỏ dòng hỏng, không báo «File nháp bị lỗi» mãi; (b) byte 18–19 đầu file > 2 coi là file lạ (đổi tên sang một bên như ca file lạ khác). Gỡ 2 `xfail` của `tests/test_la_chan_t131.py` (R5: chỉ xóa dấu).
2. Soi Lỗi T-131 GN-1, GN-2, GN-3 (xem `docs/team/reports/T-131-soi-loi.md`).
3. Gom `_guard`, `_app_tables`, `_is_healthy`, `_is_link` dùng chung cho 5 kho (không đổi hành vi đã qua Lá Chắn).
4. **B.2:** khi cất file nháp hỏng sang một bên, chép các dòng trạng thái gửi (qua khuôn `SendState`) sang file mới, hoặc câu báo nói rõ dấu «đã gửi» nằm trong file đã cất.
5. **B.4:** câu «file nháp cũ bị hỏng…» nói thêm trường hợp lối tắt; khi SQLite báo READONLY thì nói «chỉ đọc».

## Phạm vi

- **Được sửa:** `seo_app/storage/**`, `seo_app/images/data_dir.py`, kho thẻ ảnh, test. Không đổi khối SEO, trạng thái gửi ngoài việc chép khi cất file.

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: rút gọn (đầy đủ nếu đụng logic trạng thái gửi).

## Ghi chú của Chỉ Huy

- Lập 2026-11-10 theo điều kiện B.1, B.2, B.4 của Lá Chắn T-131. B.3 (chạy test T-131 trên Mac) gom với các ca Mac.
- 2026-11-12 13:56 (Chỉ Huy B): Thợ Máy `c48aedd`, `81a3016` (B.2 chọn câu báo, không chép `send_states`). Soi Lỗi rút gọn `52edfa1` ĐẠT. Giao Lá Chắn rút gọn, chạy Opus 5.5 (Fable hết hạn mức tuần).
- 2026-11-12 (Chỉ Huy B): Lá Chắn rút gọn (Opus 5.5) `2e43ebb` ĐẠT CÓ ĐIỀU KIỆN, gộp được. B.1 (LC-T136-1 Thấp, Mac/Linux: FIFO làm treo khi mở 3 kho lưu tạm; cùng gốc Soi Lỗi G1) → Thợ Máy lượt 2 trên nhánh này, Lá Chắn rút gọn lại. B.2 (ca FIFO) gom ca Mac. B.3 (thêm ca «file nháp bị cất rồi thử gửi lại» vào kịch bản T-128) → Soi Lỗi thử cục bộ và soạn. Gộp `main` sau buổi thử thật (app của chủ dự án chạy từ thư mục `main`).

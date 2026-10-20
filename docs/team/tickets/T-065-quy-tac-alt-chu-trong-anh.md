# T-065 · Quy tắc alt: chữ trong ảnh không chép vào alt lẫn chú thích

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi gộp T-056, chậm nhất trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-051 đã gộp (`config/content.toml` mục `[alt]`) |
| Trạng thái | Mới |

## Mục tiêu

Quy tắc viết alt và chú thích trong `config/content.toml` cấm chép thông tin đọc được trong ảnh (biển hiệu, số điện thoại, tên người…) vào **cả** alt lẫn chú thích, không chỉ alt.

## Bối cảnh

Biên bản Lá Chắn T-051 (`docs/team/reports/T-051-la-chan.md`), lỗi **LC-T051-1** (Thấp), điều kiện **C10**: quy tắc chữ trong ảnh hiện chỉ cấm chép vào alt, trong khi quy tắc chú thích lại bảo "bổ sung điều alt chưa nói", nên AI có thể đưa số điện thoại hay tên cửa hàng vào chú thích. Phần trong code (`ALT_SYSTEM`) sẽ được siết ở T-062 (điều kiện C2); phiếu này sửa phần cấu hình.

## Phạm vi

- **Được sửa:** `config/content.toml` (chỉ mục `[alt]`).
- **Không được sửa:** `seo_app/**`, `app/**`, test.

## Yêu cầu

1. Dòng quy tắc chữ trong ảnh (`config/content.toml` khoảng dòng 112 trên bản T-051) đổi thành: «Chữ đọc được trong ảnh (biển hiệu, tên cửa hàng, số điện thoại, số nhà, biển số xe, tên người) không chép vào alt hay chú thích».
2. Quy tắc chú thích (khoảng dòng 117) thêm: «không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt».
3. Khoảng dòng 110: bỏ chữ «phường».
4. Cân nhắc luôn góp ý nội dung SL-T051-7 của Soi Lỗi (ví dụ 1 «gỉ sét làm cánh cổng xệ» là đoán nguyên nhân; ví dụ 4 «sau khi sửa» với hạng mục sơn).

## Yêu cầu bảo mật riêng

A1.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên
- [ ] `uv run pytest` (0 hỏng trên Windows), nhất là `tests/test_soi_loi_t051.py`; `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-065-ngoi-but.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn (chạy lại `tests/test_soi_loi_t051.py`). Lá Chắn: Rút gọn (A1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện C10 của Lá Chắn T-051. Làm trên nhánh tạm `team/T-065`, tạo từ `main` sau khi T-051 gộp.

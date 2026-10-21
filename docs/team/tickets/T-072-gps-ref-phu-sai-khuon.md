# T-072 · GPS: thẻ Ref phụ sai khuôn không làm mất vị trí (sau T-067)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi gộp T-056) |
| Phụ thuộc | T-067 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Ảnh có vị trí đúng nhưng thẻ phụ (độ cao, hướng) ghi sai chuẩn vẫn giữ vị trí GPS; ảnh không có tọa độ không bị báo "GPS hỏng".

## Bối cảnh

Biên bản Lá Chắn T-067 (`docs/team/reports/T-067-la-chan.md`, LC-T067-1 = SL-T067-1, điều kiện 1, mục "Đánh giá SL-T067-1", phương án b) và báo cáo Soi Lỗi T-067 (`docs/team/reports/T-067-soi-loi.md`).

## Phạm vi

- **Được sửa:** `seo_app/images/process.py`, `tests/test_images_process.py`, đổi kỳ vọng các ca Ref phụ trong `tests/test_soi_loi_t049.py`, gỡ `xfail` trong `tests/test_soi_loi_t067.py`.
- **Không được sửa:** các file khác.

## Yêu cầu

1. Theo phương án (b) của Lá Chắn: Ref vĩ độ, kinh độ sai khuôn → bỏ cả khối GPS và báo (như T-067); Ref phụ sai khuôn → bỏ cả cặp thẻ phụ đó, **giữ** vị trí, không báo; không nhận `GPSAltitudeRef` 2, 3.
2. Ảnh không có tọa độ mà có Ref phụ sai khuôn: không báo "GPS hỏng".
3. Thêm test `GPSAltitudeRef` = 3; đổi kỳ vọng các ca Ref phụ trong test của Thợ Máy và Soi Lỗi như biên bản ghi; gỡ 4 `xfail` SL-T067-1 khi XPASS.

## Yêu cầu bảo mật riêng

F2 (GPS đúng giá trị sau nén theo 2A).

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_soi_loi_t067.py tests/test_ai_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-072-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (F2).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-067. Làm trên nhánh tạm `team/T-072`, tạo từ `main` sau khi T-067 gộp.

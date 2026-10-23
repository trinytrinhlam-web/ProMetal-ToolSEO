# T-080 · Dọn lỗi Thấp đọc ảnh sau T-079 (LC-T079-1, -2, -3)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-23 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 3; không chặn T-056) |
| Phụ thuộc | T-079 đã gộp |
| Trạng thái | Chờ chủ dự án chọn: sửa hay ghi sổ rủi ro |

## Mục tiêu

Đóng 3 lỗi Thấp Lá Chắn T-079 để lại ở `seo_app/images/folders.py`.

## Bối cảnh

Biên bản Lá Chắn T-079 (`docs/team/reports/T-079-la-chan.md`, điều kiện 1), báo cáo Soi Lỗi T-079 (Windows: SL-T079-1; Linux: SL-T079-L-1):
- **LC-T079-1 (= SL-T079-1, chỉ Windows):** so "đường dẫn thật" của handle bằng NFC + casefold lỏng hơn cách ổ phân biệt tên; thư mục "anh em" tên trông y hệt cạnh thư mục ảnh + thắng cuộc đua tráo thì đọc được file ngoài (thử >8.000 lượt trên Windows: 0 lần thắng). Sửa ở cả `_win_handle_at` lẫn `_scan_held`.
- **LC-T079-2:** khi bị tráo, câu báo lỗi có thể nói số liệu của file bên ngoài (ví dụ "Ảnh quá lớn (523 MB)").
- **LC-T079-3 (gồm SL-T079-L-1):** câu báo đôi khi sai nghĩa ("không có quyền" thay "vừa bị thay đổi").

## Phạm vi

- **Được sửa:** `seo_app/images/folders.py`, `tests/test_images_folders.py`; gỡ `xfail` trong `tests/test_soi_loi_t079.py` (8 ca), `tests/test_la_chan_t079.py` (7 ca), `tests/test_soi_loi_t079_linux.py` (3 ca, chỉ XPASS trên Linux/Mac: cần lượt cloud Linux hoặc gỡ tay có ghi lý do).
- **Không được sửa:** `app/**`, `config/**`, `seo_app/storage/**`.

## Yêu cầu

Theo cách sửa trong bảng lỗi của biên bản Lá Chắn T-079. Thử lại ổ Google Drive for Desktop thật (chỉ đọc thuộc tính) và ổ mạng nếu có.

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (F1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-079. Nếu chủ dự án chọn không sửa thì ghi sổ rủi ro theo mẫu trong biên bản (chủ dự án ký).

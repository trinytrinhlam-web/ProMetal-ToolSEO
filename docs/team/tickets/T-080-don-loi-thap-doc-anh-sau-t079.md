# T-080 · Dọn lỗi Thấp đọc ảnh sau T-079 (LC-T079-1, -2, -3)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-23 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 3; không chặn T-056) |
| Phụ thuộc | T-079 đã gộp (trên máy, đang chạy toàn bộ test) |
| Trạng thái | Soi Lỗi xong, chờ Lá Chắn rút gọn |

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
- 2026-10-23 08:17 (Chỉ Huy B): **chủ dự án chọn sửa** (không ghi sổ rủi ro cho LC-T079-1..3). Nhánh `team/T-080` tạo từ `main` sau khi gộp T-079.
- 2026-10-23 09:36 (Chỉ Huy B): **Thợ Máy xong** (`a88c4e8`): LC-T079-1 so đường dẫn thật từng chữ (phép ép thắng của Lá Chắn: bản cũ lọt 5/7 kiểu, bản mới chặn 7/7); LC-T079-2 câu báo chỉ tả mục trong thư mục ảnh; LC-T079-3 "vừa bị thay đổi" thay "không có quyền". Gỡ 15 `xfail` (8 SL-T079-1, 7 LC-T079); 1.223 test liên quan qua; thử thật NTFS, ổ mạng, 2 ổ Google Drive (chỉ đọc thuộc tính). Còn: 3 ca SL-T079-L-1 cần lượt cloud Linux; **câu hỏi chủ dự án**: cho thử ổ USB `F:` (FAT32), chỉ đọc thuộc tính, không in tên.
- 2026-10-23 09:40 (Chỉ Huy B): chủ dự án **đồng ý thử ổ USB `F:` (FAT32)**: chỉ đọc thuộc tính, không mở nội dung, không ghi tên file ra, không ghi gì vào ổ. Thợ Máy thử trước; xong mới giao Soi Lỗi rút gọn. Lượt cloud Linux (3 ca SL-T079-L-1) chạy song song, đẩy lên nhánh riêng `team/T-080-linux`.
- 2026-10-23 13:51 (Chỉ Huy B): **Soi Lỗi Linux (cloud) ĐẠT** (`133774c`): gỡ `xfail` 3 ca SL-T079-L-1; 0 lọt qua hơn 3,4 triệu vòng tráo; thêm SL-T080-L-1 (Thấp, câu báo "nằm ngoài thư mục ảnh" thay "vừa bị thay đổi", có từ trước). **Soi Lỗi Windows ĐẠT CÓ ĐIỀU KIỆN** (`51b1ddb`): ép thắng 0/380, tráo thật 0 lọt qua 21.541 lần (bản cũ lọt nội dung 61 lần với thư mục anh em dấu Kelvin); 2 Thấp mới SL-T080-1, -2 (chỉ sai câu báo, có từ trước); SL-T080-L-1 cũng có trên Windows. Đã gộp `team/T-080-linux` vào `team/T-080` (`170f7a3`), xóa nhánh Linux. Chờ Lá Chắn rút gọn (F1). SL-T080-1, -2, -L-1: phiếu dọn sau hoặc ghi nhận, chờ chủ dự án.
- 2026-10-23 13:53 (Chỉ Huy B): chủ dự án duyệt: giao Lá Chắn rút gọn; SL-T080-1, -2, -L-1 làm ở phiếu **T-082** (sau T-056).
- 2026-10-23 14:32 (Chỉ Huy B): **Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`8869baf`): LC-T079-1, -2, -3 đóng; 0 lỗi mới. Lá Chắn nâng LC-T079-1 trên bản `main` cũ lên **Cao** (Soi Lỗi khai thác được thật 61 lần) → gộp ngay, trước T-056. Điều kiện: T-082 thêm ghi chú/làm chặt `_resolve_inside`, `_checked_file` (bỏ `tests/test_la_chan_t080.py` khỏi lệnh test của T-082: không có file này); Mac chạy test thật trước khi dùng; kiểm lại bằng Fable sau 01/11. Đã gộp vào `main` trên máy (`3eba83a`), đang chạy toàn bộ test.

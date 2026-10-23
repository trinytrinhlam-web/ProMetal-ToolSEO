# T-079 · Đọc ảnh bằng thư mục đã mở từng tầng (SL-T063-2: đọc được file ngoài thư mục ảnh trên Linux/Mac)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-22 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | **Cao** (Soi Lỗi T-063 đề xuất Cao; chờ Lá Chắn xếp mức). **Chặn gộp T-056** |
| Phụ thuộc | T-076, T-063 đã gộp; Lá Chắn T-063 đã xét mức |
| Trạng thái | Đang làm |

## Mục tiêu

`read_image_bytes` và `stat_image` không bao giờ trả nội dung hay số liệu của file nằm ngoài thư mục ảnh, kể cả khi một chương trình khác trên máy tráo thư mục con thành lối tắt (symlink) đúng lúc app đọc.

## Bối cảnh

Báo cáo Soi Lỗi T-063 (`docs/team/reports/T-063-soi-loi.md` trên nhánh `team/T-063`, chạy trên cloud Ubuntu 24.04, Python 3.12.3):
- **SL-T063-2 (đề xuất Cao):** thư mục con bị tráo thành symlink hai lần (lúc `lstat` mục cuối và lúc `open`) thì `read_image_bytes` trả nội dung file ngoài gốc. `folders.py:487` (`lstat` theo đường dẫn), `:501`/`:508` (`resolve`), `:636` (`os.open(path)`: `O_NOFOLLOW` chỉ chặn tầng cuối), `:643-644` (so định danh với chính `lstat` đã đi xuyên). Đo thật: lọt 1.062/35.125 lần (root), 634/16.256 (`nobody`). Có test `xfail` tái hiện chắc chắn.
- SL-T063-3 (Thấp): như trên ở `stat_image` (lọt cỡ, giờ sửa).
- SL-T063-5 (Thấp): Linux trả `ENOTDIR` thay `ELOOP` cho `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink, nên đếm nhầm vào `unreadable`.
- SL-T063-1 (Thấp, lỗi test): `test_unreadable_subfolder_is_counted_not_fatal` giả `os.scandir` bằng `Path(path).name`, hỏng trên Mac/Linux.
- SL-T076-2 (Thấp, Soi Lỗi T-076 lượt 2): đổi tên rồi đổi lại đúng lúc kiểm thì bản sao có thể được dùng; cân nhắc đóng cùng nếu cách sửa đi bằng fd.

## Phạm vi

- **Được sửa:** `seo_app/images/folders.py`, `tests/test_images_folders.py` (sửa SL-T063-1 không làm yếu điều kiện), gỡ `xfail` trong `tests/test_images_folders_t063.py` (sau khi T-063 gộp).
- **Không được sửa:** `app/**`, `config/**`, `seo_app/storage/**` (trừ khi Chỉ Huy cho).

## Yêu cầu (định hướng, Lá Chắn có thể chỉnh)

1. Mac/Linux: đọc và `stat` bằng chuỗi thư mục đã mở từng tầng (`openat(dir_fd, tên, O_NOFOLLOW | O_DIRECTORY)` cho mỗi tầng, `openat(…, O_NOFOLLOW)` cho file, `fstat` trên fd đã mở), không đi theo chuỗi đường dẫn; so định danh với fd đã mở.
2. Windows: giữ các lớp chặn hiện có; xét lại theo kết quả Lá Chắn thử cách tráo nhanh trên Windows.
3. SL-T063-5: coi `ENOTDIR` từ `openat(O_DIRECTORY | O_NOFOLLOW)` là "liên kết/vừa bị thay đổi" khi mục là symlink.
4. SL-T063-1: viết lại test để chạy được mọi máy.
5. Có test chạy được trên Windows lẫn Linux; gỡ `xfail` SL-T063-2, -3, -5 khi XPASS.

## Yêu cầu bảo mật riêng

F1, F3.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (cả lượt chạy lại trên cloud Linux). Lá Chắn: Có (F1).

## Ghi chú của Chỉ Huy

- Lập theo báo cáo Soi Lỗi T-063 (cloud, 2026-10-22). Chờ T-076 gộp và Lá Chắn xét mức SL-T063-2 rồi mới giao.
- 2026-10-22 10:16 (Chỉ Huy B): **Lá Chắn T-063** (`docs/team/reports/T-063-la-chan.md`, nhánh `team/T-063`): SL-T063-2 **Cao trên Mac/Linux, Thấp trên Windows** (thử tráo thật trên Windows >15.000 lần đọc: 0 lọt nội dung, 0 lọt cỡ; nhưng khi ép kẻ tấn công luôn thắng thì Windows cũng lọt, tức lỗi nằm trong code). **Bắt buộc trước khi app chạy trên Mac hoặc Linux** (kể cả phiên cloud Linux); Lá Chắn kiểm lại, gỡ 2 test `xfail` Windows của Lá Chắn và các `xfail` POSIX khi XPASS. Thêm vào phạm vi: **LC-T076-3** (= SL-T076-2, Thấp: bước hỏi lại tên cũ không so định danh file giữa các lần hỏi; biên bản Lá Chắn T-076 lượt 2), và xóa dấu `xfail` SL-T063-4 trong `tests/test_images_folders_t063.py` (T-076 đã sửa; chỉ hiện trên Linux/Mac).
- 2026-10-22 13:10 (Chỉ Huy B): **Chủ dự án chọn cách A**: làm T-079 trước, rồi mới gộp T-056. Nhánh `team/T-079` tạo từ `main` sau khi gộp T-076, T-063.
- 2026-10-22 18:07 (Chỉ Huy B): **Soi Lỗi Windows ĐẠT CÓ ĐIỀU KIỆN** (`79b55e7`: phép ép thắng của Lá Chắn T-063 không còn lọt; 1 Thấp SL-T079-1: so đường dẫn thật bằng NFC + casefold lỏng hơn cách ổ phân biệt tên). **Soi Lỗi Linux (cloud) ĐẠT** (`e7fdebd` trên `team/T-079-linux`: dựng lại cách tráo T-063, hơn 1,3 triệu lượt đọc, 0 lọt nội dung, 0 lọt cỡ, 0 lọt tên; 1 Thấp SL-T079-L-1: đôi khi báo "không có quyền" thay "vừa bị thay đổi"). Chỉ Huy đã gộp `team/T-079-linux` vào `team/T-079` (`089d115`). Giao Lá Chắn.
- 2026-10-23 07:57 (Chỉ Huy B): **Lá Chắn ĐẠT CÓ ĐIỀU KIỆN** (`f915841`): SL-T063-2, -3 đóng (Windows: phép ép thắng nay bị chặn; Linux: 0 lọt qua hơn 1,3 triệu lượt); 3 Thấp LC-T079-1, -2, -3 → **T-080** (lập mới; hoặc ghi sổ rủi ro nếu chủ dự án chọn); điều kiện "T-079 trước Mac/Linux" bỏ được khi gộp; Mac vẫn phải chạy test trên máy Mac thật trước khi dùng; sổ rủi ro ca "thư mục thật được dời vào gốc" chờ chủ dự án quyết. **Gộp được ngay.**

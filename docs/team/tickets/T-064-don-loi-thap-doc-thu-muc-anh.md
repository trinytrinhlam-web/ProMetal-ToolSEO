# T-064 · Dọn lỗi Thấp của phần đọc thư mục ảnh (sau T-048)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-048 đã gộp; nên làm sau T-063 (nếu T-063 tìm ra lỗi Mac/Linux thì gộp vào phiếu này) |
| Trạng thái | Mới |

## Mục tiêu

Sửa các lỗi Thấp Lá Chắn và Soi Lỗi ghi ở T-048, để thư mục ảnh không còn khe lộ **tên** file ngoài thư mục gốc.

## Bối cảnh

Biên bản Lá Chắn T-048 (`docs/team/reports/T-048-la-chan.md`), mục "Lỗi phát hiện" và "Điều kiện" 2, 3; báo cáo Soi Lỗi T-048 lượt 2 (R2-1, R2-2).

## Phạm vi

- **Được sửa:** `seo_app/images/folders.py`, test liên quan (bỏ `xfail` khi đã sửa; cập nhật test `sl:1093-1110` nếu đổi quy tắc ký tự).
- **Không được sửa:** `app/**`, `config/**`.

## Yêu cầu

1. **LC-T048-2 (= R2-1) và LC-T048-3:** liệt kê thư mục qua **chính handle đang giữ** (`GetFileInformationByHandleEx`, lớp `FileIdBothDirectoryInfo` hoặc `FileFullDirectoryInfo`) thay cho `os.scandir(tên)`, cả ở nhánh chính và nhánh dự phòng (nhánh dự phòng mở lại handle có chia sẻ quyền xóa). Mục tiêu: junction bật/tắt tại chỗ không còn làm lộ tên, cỡ, ngày sửa của file ngoài gốc. Bỏ `xfail` R2-1 (`tests/test_images_folders_soi_loi.py:903`); cập nhật test ghi nhận khe "tráo rồi tráo lại" của nhánh dự phòng (khoảng `:1004`) cho đúng hành vi mới.
2. **LC-T048-4 mục c:** `_is_safe_name` từ chối thêm Zl, Zp (U+2028, U+2029), khối ký tự thẻ U+E0000–E007F, U+FFF9–FFFB; giữ ZWJ/ZWNJ cho emoji và chữ ghép.
3. **LC-T048-5 (= R2-2):** quét cả cây đủ `max_entries` mục mà còn thư mục con rỗng thì không báo "còn nữa" thừa; bỏ `xfail` `:1041`.
4. Bọc `os.fstat` ở `folders.py:268` như các lời gọi hệ thống khác (lỗi thành câu tiếng Việt, không lộ đường dẫn).

## Yêu cầu bảo mật riêng

F1, U2.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test (kể cả test junction bật/tắt tại chỗ chạy thật trên Windows)
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-064-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (thử lại cách đánh tráo junction của Lá Chắn T-048). Lá Chắn: Có (F1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 2, 3 của Lá Chắn T-048. Lá Chắn khuyên **sửa** LC-T048-2/-3 thay vì ghi sổ rủi ro; Chỉ Huy B chọn sửa, trừ khi chủ dự án muốn chấp nhận rủi ro.
- **LC-T048-6** (hard link; ổ không có số inode) không nằm trong phiếu này: Lá Chắn không khuyên sửa (chặn `st_nlink > 1` sẽ chặn nhầm ảnh do phần mềm sao lưu tạo). Chờ chủ dự án đồng ý ghi vào sổ rủi ro `docs/team/security.md` mục 6.

# T-087 · README: chọn ảnh, ảnh AI, ảnh công khai khi gửi nháp

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-26 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-056 đã gộp |
| Trạng thái | Thư Ký xong, chờ Lá Chắn rút gọn |

## Mục tiêu

Chủ dự án đọc README là biết cách chọn ảnh thật trên trang Soạn bài, cách làm ảnh AI, và những gì công khai khi bấm «Gửi nháp».

## Bối cảnh

- T-056 (màn hình chọn ảnh, nút «Gửi nháp» kèm ảnh) vừa gộp. Báo cáo Họa Sĩ `docs/team/reports/T-056-hoa-si.md` (mục Đề xuất cho Thư Ký), biên bản Lá Chắn `docs/team/reports/T-056-la-chan.md` (điều kiện 3, 4), biên bản Lá Chắn T-069 `docs/team/reports/T-069-la-chan.md` (LC-T069-2).
- README đã có phần ảnh từ T-069 (khai báo `IMAGE_FOLDERS`, thư mục, ảnh gửi hãng AI).

## Phạm vi

- **Được sửa:** `README.md`.
- **Không được sửa:** code, `config/**`, `.env.example` (nếu thấy thiếu biến thì ghi vào báo cáo).

## Yêu cầu

1. Cách chọn ảnh ở chỗ cần ảnh: mở thư mục, chọn, Ảnh thật/Ảnh AI (kèm lý do), GPS, «AI viết alt» (chỉ ảnh đã chọn, bản đã bỏ thông tin máy), tick «Đã duyệt».
2. Ảnh AI: tạo ngoài app (ví dụ Gemini), lưu vào thư mục có chữ «AI»/«minh họa»; nút «Đây là ảnh AI» không đổi lại được trong app; xóa `data/image_tags.sqlite` thì mất dấu «ảnh AI» đã gắn tay (LC-T069-2).
3. «Gửi nháp»: chỉ tạo bài nháp; ảnh (kể cả GPS) xem được công khai ngay khi tải lên, kể cả bài nháp; app không tự xóa ảnh; danh sách đoạn `[...]` nên xóa; khi có lỗi giữa chừng thì kiểm Bài viết → Nháp và Media → Thư viện trước khi gửi lại.
4. Lời dặn tạm (tới khi T-086 xong): bấm «Gửi nháp» rồi đợi app báo kết quả, không tải lại trang, không bấm nút khác. Lần gửi thật đầu tiên: một bài, một ảnh, tải ảnh về kiểm GPS.
5. Viết lời thường, tiếng Việt, không đường dẫn máy thật, không khóa; giữ giọng và bố cục README hiện có.

## Yêu cầu bảo mật riêng

D1 (không lộ bí mật trong tài liệu).

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Báo cáo nộp tại `docs/team/reports/T-087-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Không. Lá Chắn: Rút gọn (đọc README).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 4 Lá Chắn T-056 và LC-T069-2; chủ dự án duyệt 2026-10-26.
- 2026-10-26 09:18 (Chỉ Huy B): **Thư Ký xong** (`4fbd6f6`): README mục 9 mới «Chọn ảnh cho bài» và phần gửi bài nháp lên WordPress; quét bí mật 0. Chờ Lá Chắn rút gọn (đọc README).

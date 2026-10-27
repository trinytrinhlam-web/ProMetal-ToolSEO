# T-095 · README: bước SEO trên trang Soạn bài, tài khoản WordPress cho app

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-041 đã gộp; thử thật T-059 |
| Trạng thái | Đang làm |

## Mục tiêu

Chủ dự án đọc README là biết dùng bước 4 «SEO» của trang Soạn bài và biết cài tài khoản WordPress cho app đúng cách (tránh lỗi đã gặp khi thử thật 27/10).

## Bối cảnh

- T-041 (đã gộp): bước 4 SEO chạy thật. Báo cáo `docs/team/reports/T-041-hoa-si.md` (mục Tóm tắt cho chủ dự án), `T-041-tho-may.md`, biên bản `T-041-la-chan.md`.
- T-059 (ghi chú trong `docs/team/tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md`, 27/10): lỗi 401 do điền **tên của mật khẩu ứng dụng** vào `WORDPRESS_USERNAME` thay vì tên đăng nhập; tài khoản Biên tập viên riêng; SiteSEO phải từ bản 1.4.0 trở lên, mục «AI Abilities» trong menu SiteSEO, bật công tắc; Kiểm tra kết nối phải thấy «SiteSEO: ghi được»; trình sửa `.htaccess` của SiteSEO Pro làm hỏng file khi lưu (không dùng).
- T-084 (đang gộp): tab Ảnh của trang Cài đặt chỉ hiện tên ngắn thư mục.

## Phạm vi

- **Được sửa:** `README.md`.
- **Không được sửa:** code, `config/**`, `.env.example` (thấy thiếu thì ghi vào báo cáo).

## Yêu cầu

1. Mục dùng bước 4 «SEO»: AI gợi ý tiêu đề, mô tả; viết lại từng ô, quay lại bản trước; nhãn Nên/Cảnh báo/Chặn; slug; kiểm trùng bài đã đăng; liên kết nội bộ; schema hỏi đáp; nút chép sang SiteSEO; công tắc «Ghi SEO lên website» (mặc định tắt, chỉ ghi vào bài nháp app vừa tạo).
2. Mục Kết nối WordPress: tạo tài khoản vai **Biên tập viên** riêng; tạo mật khẩu ứng dụng **trên chính tài khoản đó**; `WORDPRESS_USERNAME` là **tên đăng nhập**, không phải tên đặt cho mật khẩu ứng dụng; bật «AI Abilities» trong SiteSEO (bản 1.4.0 trở lên); Kiểm tra kết nối thấy vai `editor` và «SiteSEO: ghi được»; bảng xử lý lỗi thêm ca «từ chối đăng nhập (401)» → kiểm tên đăng nhập trước.
3. Lưu ý website: không dùng trình sửa `.htaccess` của SiteSEO Pro (xóa dòng `<…>` khi lưu); gỡ mật khẩu ứng dụng không còn dùng trên tài khoản quản trị.
4. Lời thường, tiếng Việt, không đường dẫn máy thật, không khóa; giữ giọng, bố cục README; tên nút, câu nhắc khớp code trên `main`.

## Yêu cầu bảo mật riêng

D1 (không lộ bí mật trong tài liệu).

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Báo cáo nộp tại `docs/team/reports/T-095-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Không. Lá Chắn: Rút gọn (đọc README).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo «cứ làm liên tục, không cần hỏi».

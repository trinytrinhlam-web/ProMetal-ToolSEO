# T-061 · Shortcode WordPress trong chữ AI và chữ SEO

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 4 (phải xong trước Giai đoạn 5 gửi bài lên WordPress) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-042 đã gộp; kết quả bước 4 của T-059 (SiteSEO có chạy shortcode trong meta không) |
| Trạng thái | Mới |

## Mục tiêu

Chữ do AI viết (bài, meta) không thể chèn shortcode WordPress chạy được trên site.

## Bối cảnh

Lá Chắn T-042 (`docs/team/reports/T-042-la-chan.md`):

- **LC-T042-3:** chữ SEO dạng shortcode (`[code_snippet_source …]`) không bị chặn ở `_seo_text`.
- Ngoài phạm vi T-042, **suy luận chưa xác minh**: `sanitize_html` không bỏ shortcode trong nội dung bài AI viết, mà site có plugin **Code Snippets** (shortcode của plugin này có thể chạy mã trên site). Kết quả AI là dữ liệu chưa tin cậy (`security.md` 2.3, 2.4).

## Phạm vi

- **Được sửa:** `seo_app/sanitize.py` (phần vô hiệu shortcode), `seo_app/wordpress/client.py` (`_seo_text`), test mới.
- **Không được sửa:** `app/**`, `config/**`.

## Yêu cầu

1. Vô hiệu hóa mọi dạng shortcode WordPress (`[tên …]`, `[tên]…[/tên]`, `[[tên]]` thoát) trong chữ AI trước khi gửi lên site, ở cả nội dung bài và meta SEO. Cách làm do Thợ Máy chọn (ví dụ thoát `[` thành `&#91;` ở HTML gửi đi, hoặc chặn), nhưng người đọc vẫn thấy chữ bình thường.
2. Không phá Markdown/ngoặc vuông thường dùng trong bài (ví dụ "[Lưu ý]"); có test cả hai chiều.
3. Ghi rõ trong báo cáo cách đã xác minh (bộ đọc shortcode của WordPress là regex `get_shortcode_regex`, đọc mã nguồn, không gọi site thật).

## Yêu cầu bảo mật riêng

A2, W3, `security.md` 2.3.

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A2, 2.3).

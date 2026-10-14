# T-004 · Lọc HTML và link trong kết quả AI, bộ lọc trước khi gửi WordPress

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 (bắt buộc trước khi nối bài AI sang WordPress) |
| Mức ưu tiên | **Cao** |
| Phụ thuộc | Không |
| Trạng thái | Xong |

## Mục tiêu

HTML hoặc JavaScript do AI chèn vào bài (ví dụ vì trang đối thủ cài lệnh) không bao giờ chạy trong app và không bao giờ lên website.

## Bối cảnh

- Lỗi #1 trong [T-001-la-chan.md](../reports/T-001-la-chan.md), lỗi #1 và #3 trong [T-002-soi-loi.md](../reports/T-002-soi-loi.md).
- Các test `xfail` đã viết sẵn: `test_highlight_escapes_ai_text`, `test_html_in_ai_article_is_not_rendered_as_html`, `test_html_sent_to_wordpress_is_sanitized`.

## Phạm vi

- **Được sửa:** `seo_app/content/workflow.py`, `seo_app/wordpress/client.py`, thêm module lọc trong `seo_app/` nếu cần; bỏ dấu `xfail` của các test liên quan khi đã sửa xong.
- **Không được sửa:** `app/`, `seo_app/ui.py` (thuộc T-005).

## Yêu cầu

1. Tại ranh giới nhận kết quả AI (`Draft.intro`, `Section.body`, `SectionText.body`, `Flag.replacement`): bỏ mọi thẻ HTML; link Markdown ra ngoài bị bỏ hoặc đánh dấu để người dùng thấy.
2. Trước khi gửi nội dung lên WordPress: bộ lọc theo danh sách ở `security.md` mục 2.3, dùng thư viện chuẩn của Python (không thêm thư viện).
3. Test cho cả hai chỗ với `<script>`, `<img onerror>`, `javascript:`, `<iframe>`.

## Yêu cầu bảo mật riêng

W3, U1, A2.

## Tiêu chí xong

- [ ] Ba test `xfail` ở trên chuyển thành `passed`
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-004-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (thử nhiều cách lách bộ lọc)
- Lá Chắn: Có

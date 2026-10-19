# T-051 · Prompt alt và cấu hình việc ảnh (G3-5)

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không (chạy song song) |
| Trạng thái | Mới |

## Mục tiêu

Có quy tắc viết alt tiếng Việt tốt cho SEO; `config/ai.toml` có mục `[tasks.alt]` (Claude Sonnet) và `[tasks.image]` (Gemini) theo quyết định 4A; chất lượng WebP trong `config/content.toml`.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `config/ai.toml`, `config/content.toml`, file prompt alt mới trong `config/`.
- **Không được sửa:** `seo_app/**`, `app/**`.

## Yêu cầu

1. Alt: mô tả đúng nội dung ảnh, ngắn (giới hạn ký tự rõ ràng), tự nhiên, không nhồi từ khóa, không bịa địa điểm hay tên khách; ảnh AI không bao giờ được mô tả như "công trình thật".
2. Sửa luôn chú thích đầu `config/ai.toml` đã cũ (thêm openai, gemini; không có hãng mặc định).
3. Tên mô hình lấy theo báo cáo T-046 (ghi rõ mô hình nào chưa xác minh); file cấu hình chịu lỗi như cũ (T-010).

## Yêu cầu bảo mật riêng

A1 (lời dặn AI không cho AI quyền hơn mức cần).

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-051-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn (cấu hình đọc được, test cấu hình qua). Lá Chắn: Rút gọn (A1).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-051`, tạo từ `main`.

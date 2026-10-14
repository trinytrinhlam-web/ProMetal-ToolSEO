# T-003 · Rà soát prompt và quy tắc nội dung của Giai đoạn 2

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-001 (để gộp đề xuất về prompt injection) |
| Trạng thái | Mới |

## Mục tiêu

Prompt viết bài cho ra bài đúng "Quy trình nội dung" trong `CLAUDE.md`: có ích thật, đúng văn phong, không câu sáo rỗng, không bịa, an toàn trước dữ liệu ngoài.

## Bối cảnh

- Prompt: `seo_app/content/prompts.py`. Quy tắc: `config/content.toml`. Mô hình theo việc: `config/ai.toml`. Hồ sơ doanh nghiệp: `config/business_profile.md` (PR #3, có thể chưa nằm trên `main`).
- Plugin SEO là SiteSEO. Không có site thử nghiệm.

## Phạm vi

- **Được sửa:** `config/content.toml`, và tạo `docs/team/reports/T-003-ngoi-but.md`.
- **Không được sửa:** code Python (đề xuất sửa `prompts.py` ghi trong báo cáo để Thợ Máy làm).

## Yêu cầu

1. Đối chiếu từng prompt với 7 bước Quy trình nội dung và danh sách "Cấm" trong `CLAUDE.md`.
2. Kiểm tra checklist chất lượng trong `config/content.toml` có đủ tiêu chí văn phong: thân thiện, tự nhiên, dễ đọc, cụ thể, chuẩn SEO.
3. Kiểm tra prompt tách dữ liệu ngoài khỏi chỉ thị (`security.md` mục 2.4).
4. Đề xuất bản sửa cụ thể, kèm ví dụ đầu vào → đầu ra mong muốn cho một từ khóa thật của doanh nghiệp (ví dụ "sửa cửa cuốn quận 7").

## Tiêu chí xong

- [ ] Báo cáo có bảng đối chiếu từng prompt
- [ ] Đề xuất sửa cụ thể cho Thợ Máy (nếu có)
- [ ] `uv run pytest` vẫn qua sau khi sửa `config/content.toml`

## Kiểm thử và kiểm định

- Soi Lỗi: Có nếu `config/content.toml` thay đổi
- Lá Chắn: Có (prompt AI)

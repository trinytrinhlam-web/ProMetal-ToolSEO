# T-050 · Lớp AI đọc ảnh và gợi ý alt (G3-4)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không (nhận bytes; chạy song song với T-048, T-049) |
| Trạng thái | Mới |

## Mục tiêu

Lớp provider của 3 hãng nhận thêm ảnh (bytes) để AI viết gợi ý alt; kết quả qua bộ lọc chữ AI.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/ai/base.py`, `seo_app/ai/*_provider.py`, `seo_app/ai/registry.py`, `seo_app/images/alt.py`, `tests/fake_ai.py`, `tests/test_ai_images.py`.
- **Không được sửa:** `seo_app/images/__init__.py`, `app/**`, `config/**` (Ngòi Bút làm T-051).

## Yêu cầu

1. Tham số `images` cho 3 hãng; khuôn `AltSuggestion`; hàm gợi ý alt có giới hạn độ dài, kết quả qua `clean_ai_text`.
2. Chỉ gửi bytes bản gửi AI (không EXIF, không tên file gốc, không đường dẫn) (A3). Không dùng Files API hay URL.
3. Giữ địa chỉ máy chủ chính thức cố định (T-026), không đọc lại `*_CUSTOM_HEADERS` (T-028, T-034). Nếu phải nâng `google-genai` thì dừng, ghi đề xuất (D1).
4. Mô hình cho việc `alt` đọc từ `config/ai.toml` mục `[tasks.alt]`; thiếu mục thì báo lỗi tiếng Việt dễ hiểu, không sập.

## Yêu cầu bảo mật riêng

A1, A2, A3, S2; góp ý Lá Chắn T-046 số 5.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-050-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1–A3).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-050`, tạo từ `main`.

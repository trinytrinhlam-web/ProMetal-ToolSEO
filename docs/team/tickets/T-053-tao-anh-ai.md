# T-053 · Tạo ảnh AI, đánh dấu ảnh AI (G3-7)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-049, **T-050** đã gộp (cùng file provider) |
| Trạng thái | Mới |

## Mục tiêu

App tạo ảnh bằng Gemini (quyết định 4A; có đường OpenAI nếu khai báo), kiểm ảnh trả về, đánh dấu rõ là ảnh AI.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/ai/images.py` (mới), `seo_app/ai/openai_provider.py`, `seo_app/ai/gemini_provider.py`, `tests/test_ai_image_gen.py`.
- **Không được sửa:** `app/**`, `config/**`, `seo_app/images/__init__.py`.

## Yêu cầu

1. Chỉ nhận ảnh dạng base64 trong phản hồi; **không tải ảnh theo URL** do máy chủ AI đưa về; giới hạn độ dài chuỗi trước khi giải base64, rồi mở bằng Pillow có giới hạn điểm ảnh (góp ý Lá Chắn số 6).
2. Ảnh AI không có GPS, không thẻ công trình thật; tên file, alt, metadata đánh dấu AI.
3. Prompt ảnh xem, sửa, sao chép được (trả về cùng ảnh). Ước tính giá mỗi ảnh để hiện cho người dùng (ghi "ước tính").
4. Giữ địa chỉ máy chủ chính thức (T-026), không đọc `*_CUSTOM_HEADERS`. Nếu phải nâng `google-genai` thì dừng, ghi đề xuất (D1).

## Yêu cầu bảo mật riêng

A2, S2, D1; góp ý Lá Chắn T-046 số 5, 6.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-053-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A2, kiểm ảnh trả về).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-053`, tạo từ `main`.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-051** (`docs/team/reports/T-051-la-chan.md`), trước khi bỏ dấu `#` ở `[tasks.image]` trong `config/ai.toml`:
  - C7: T-062 đã gộp (provider chỉ tạo khi cần; từ chối `provider = "anthropic"` cho việc ảnh).
  - C8: xác minh tên mô hình tạo ảnh (tài liệu Google mới nhất, hoặc một lần gọi thử do chủ dự án làm ngoài bộ test) rồi sửa chú thích «CHƯA XÁC MINH». Không thêm `base_url` hay địa chỉ máy chủ nào vào `config/ai.toml`; client Gemini giữ địa chỉ chính thức cố định (T-026).
  - C9: chỉ tạo ảnh khi người dùng bấm, mỗi lần một ảnh; không tự tạo hàng loạt (chi phí).
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-049** (điều kiện 5): ảnh AI trả về đi qua `make_web_image` (mở an toàn, giới hạn điểm ảnh); tên file `image_file_name(..., ai_generated=True)`. Nếu thêm đánh dấu EXIF cho ảnh AI (`ImageDescription`/`Software`) thì đó là sửa danh sách cho phép 2A trong `process.py`: Lá Chắn soát riêng; đánh dấu chỉ là chữ cố định do code viết, không lấy từ prompt hay phản hồi AI.

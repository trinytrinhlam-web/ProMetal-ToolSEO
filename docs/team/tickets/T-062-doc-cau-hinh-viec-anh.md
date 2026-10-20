# T-062 · Đọc cấu hình việc ảnh: tạo provider khi cần, chịu lỗi, nhãn hiển thị

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (phải xong trước khi bật `[tasks.image]`, tức trước T-053) |
| Phụ thuộc | T-050, T-051 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Bật được mục `[tasks.image]` (Gemini) trong `config/ai.toml` mà trang Soạn bài không đòi khóa Gemini khi chỉ viết bài; cấu hình ảnh và alt đọc chịu lỗi.

## Bối cảnh

Ngòi Bút T-051 (`docs/team/reports/T-051-ngoi-but.md`) đã thêm `[tasks.alt]`, `[tasks.image]` (đang để chú thích, tắt), `[images]`, `[alt]`. Khi thử bật `[tasks.image]`:

- `tests/test_ai.py::test_project_ai_config_is_valid` hỏng vì test đòi mọi việc là anthropic.
- Trang Soạn bài đòi `GEMINI_API_KEY` dù chỉ viết bài, vì `AIRouter` tạo provider cho mọi việc ngay lúc mở trang.

## Phạm vi

- **Được sửa:** `seo_app/ai/registry.py`, `seo_app/content/rules.py` hoặc nơi đọc `config/content.toml` (phần `[images]`, `[alt]`), `seo_app/content/blind_test.py` (chỉ `TASK_LABELS`), test liên quan (kể cả sửa `test_project_ai_config_is_valid` cho đúng ý: kiểm từng việc, không đòi mọi việc là anthropic).
- **Không được sửa:** `config/**` (Ngòi Bút), `app/**`.

## Yêu cầu

1. `AIRouter` chỉ tạo provider khi việc đó được gọi (lười); thiếu khóa của hãng chỉ báo lỗi khi gọi đúng việc dùng hãng đó.
2. Từ chối `provider = "anthropic"` cho việc `image` (Claude không tạo được ảnh), câu lỗi tiếng Việt.
3. Thử mù không gợi ý mô hình tạo ảnh; thêm nhãn tiếng Việt cho `alt`, `meta`, `image` trong `TASK_LABELS`.
4. Đọc `[images]` (`webp_quality`, `max_edge_px`) và `[alt]` (`max_chars`, `caption_max_chars`, quy tắc; đúng tên khóa trong `config/content.toml` của T-051) kiểu chịu lỗi như T-010: thiếu mục thì dùng mặc định 80/1600/125/200; sai dạng thì báo tiếng Việt, không sập.
5. Code tự bảo đảm, không trông vào AI (đề xuất 4 của Ngòi Bút): alt gộp một dòng, bỏ dấu chấm cuối, cắt theo ranh giới từ; ảnh AI thì code tự thêm «Minh họa» (alt) và «Ảnh minh họa (AI)» (chú thích) nếu thiếu. Nếu phần này nằm trong `seo_app/images/alt.py` (T-050) thì được sửa file đó.
6. Test cấu hình cho `[images]`, `[alt]`, và cho việc bật `[tasks.image]`.

## Yêu cầu bảo mật riêng

A1 (prompt alt đề xuất của Ngòi Bút: thẻ ảnh và chữ trong ảnh là dữ liệu), S2.

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Rút gọn (A1, S2).

## Ghi chú của Chỉ Huy

- Prompt alt đề xuất có trong báo cáo Ngòi Bút T-051; đưa vào code ở phiếu này nếu T-050 chưa có.
- 2026-10-20 (Chỉ Huy B), theo Soi Lỗi T-051 (`docs/team/reports/T-051-soi-loi.md`):
  - SL-T051-5: đã sửa tên khóa ở yêu cầu 4 cho khớp `config/content.toml` (`max_chars`, `caption_max_chars`).
  - Làm xong thì gỡ 5 dấu `xfail` SL-T051-1 → 4 trong `tests/test_soi_loi_t051.py` (bật `[tasks.image]` không đòi khóa Gemini; từ chối `anthropic` cho việc ảnh; nhãn `alt`/`meta`; thử mù không gợi ý mô hình tạo ảnh).
  - SL-T051-6: `alt_system()` của T-050 cắt lời dặn ở 4.000 ký tự (`GUIDANCE_MAX_LENGTH`), quy tắc `[alt]` kèm 6 ví dụ dài khoảng 4.263 ký tự. Khi nối `[alt]` vào prompt: đưa quy tắc vào lời dặn, để ví dụ riêng, hoặc nâng giới hạn có lý do; không cắt giữa câu.

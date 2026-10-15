# Biên bản bảo mật T-028 · Máy chủ AI trả mã 200 nhưng nội dung hỏng

> **ĐANG KIỂM, chưa kết luận.** Bản dở dang, commit sớm để không mất việc nếu phiên bị dừng.

> **Lưu ý về model:** lần kiểm định này chạy **tạm bằng Opus 5.5** (`claude-opus-5-5`), vì tài khoản hiện không dùng được Fable 5.1. Chủ dự án đã duyệt cho Lá Chắn chạy tạm Opus 5.5 tới 01/11. **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm thay Fable 5.1) |
| Phiếu được kiểm | [T-028](../tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) |
| Phạm vi | `git diff origin/main...team/T-028`, HEAD `1c300f5` |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐANG KIỂM** |

## Đã làm tới đâu

- Đã đọc phiếu, báo cáo Thợ Máy (2 lượt), báo cáo Soi Lỗi, biên bản T-026, sổ rủi ro trên `main`.
- Đã đọc toàn bộ diff code: `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`.
- Đang chạy `uv run pytest` trên Windows; còn lại: thử tay, công cụ quét, 19 dòng kiểm tra.

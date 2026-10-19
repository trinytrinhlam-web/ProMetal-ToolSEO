# Biên bản bảo mật T-047 · Khai báo Pillow và pillow-heif

> **BẢN DỞ** (commit sớm để giữ tiến độ). Bản hoàn chỉnh sẽ thay thế file này.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (chạy tạm vì tài khoản không dùng được Fable, chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.** |
| Phiếu được kiểm | [T-047](../tickets/T-047-khai-bao-pillow-va-pillow-heif.md) |
| Phạm vi | diff `origin/main...team/T-047` tại `82b37ce` |
| Ngày | 2026-10-19 |
| **Kết luận** | (đang viết; dự kiến ĐẠT CÓ ĐIỀU KIỆN) |

## Đã làm xong (ghi tạm)

- D1: `uv.lock` chỉ thêm đúng 1 gói `pillow-heif 1.8.1` (phụ thuộc duy nhất `pillow`); 49/49 mã băm `pillow-heif`, 64/64 mã băm `pillow` khớp PyPI JSON API; mọi nguồn là `pypi.org` / `files.pythonhosted.org`.
- pip-audit 2.10.1 (nguồn PyPI và nguồn OSV) trên 69 gói: không có lỗ hổng đã biết.
- **Phát hiện chính:** kho `python-pillow/Pillow` công bố 53 khuyến cáo bảo mật (GHSA) ngày 2026-10-17 ảnh hưởng Pillow ≤ 12.3.0, bản vá chỉ ở 13.0.0. pip-audit chưa thấy vì cơ sở dữ liệu chưa cập nhật. Streamlit 1.65 và 1.66 đều khóa `pillow<13`.
- libheif 1.23.6, libde265 1.1.3, x265 4.3: đều là bản mới nhất; mọi GHSA/CVE đã biết có bản vá ≤ bản đi kèm (đang viết chi tiết).
- `uv run pytest`: 5643 qua, 11 bỏ qua, 35 xfail, 0 hỏng. `uv run ruff check .`: sạch.

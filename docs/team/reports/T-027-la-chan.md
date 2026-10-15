# Biên bản bảo mật T-027 · Bộ test chạy xanh trên Windows

> **ĐANG KIỂM, chưa kết luận.** Bản dở dang, commit sớm để không mất việc nếu phiên bị dừng. Kết luận sẽ ghi ở bản cuối.

> **Lưu ý về model:** lần kiểm định này chạy **tạm bằng Opus 5.5** (`claude-opus-5-5`), vì tài khoản hiện không dùng được Fable 5.1 (cần mua thêm lượt dùng). Chủ dự án đã duyệt cho Lá Chắn chạy tạm Opus 5.5 tới 01/11. **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm thay Fable 5.1, xem lưu ý trên) |
| Phiếu được kiểm | [T-027](../tickets/T-027-test-chay-tren-windows.md) |
| Phạm vi | `git diff origin/main...team/T-027`, HEAD `b87d3a4`: `tests/conftest.py`, `tests/test_soi_loi_t016_t020.py`, `tests/test_soi_loi_t027.py` (mới), báo cáo Soi Lỗi |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐANG KIỂM** |

## Đã làm tới đâu

- Đã đọc toàn bộ diff và mã nguồn thư viện chuẩn liên quan (`socket._fallback_socketpair`, `IocpProactor.connect`, `urllib.request.proxy_bypass_registry`) trên Python 3.12.15 của máy.
- `uv run pytest -q` lần 1 (Windows 11, worktree): `2358 passed, 10 skipped, 5 xfailed in 249.35s`.
- Dữ liệu 100.000 ký tự của `test_bad_json_in_row_gives_draft_error` còn nguyên; 7 `ids` khớp 7 tham số.
- Còn lại: thử lách bằng bộ nhận loopback tự mở, UDP, công cụ quét mục 5, 19 dòng kiểm tra.

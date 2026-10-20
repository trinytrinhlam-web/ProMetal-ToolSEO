# Biên bản bảo mật T-048 · Đọc thư mục ảnh an toàn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

> **BẢN DỞ** (đang kiểm định, chưa có kết luận). Phần 1: phạm vi, công cụ quét, ghi chú gộp. Lá Chắn phiên trước (dưới Chỉ Huy A) chỉ kịp tạo khung lúc 08:02; phiên này kiểm định lại từ đầu.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable) |
| Phiếu được kiểm | [T-048](../tickets/T-048-doc-thu-muc-anh-an-toan.md) |
| Phạm vi | diff `origin/main...team/T-048` (gốc chung `5e38bb8`, code tới `882dc18`, test Soi Lỗi tới `e366dc5`, HEAD lúc kiểm `5993812`) và code xung quanh (`seo_app/config.py`, `app/views/settings.py`, `.gitignore`, `.streamlit/config.toml`, `tests/conftest.py`) |
| Ngày | 2026-10-20 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (junction, tên 8.3, `\\localhost\C$` chạy thật). Không có WSL, Docker, máy Mac: nhánh Mac/Linux **chưa chạy** |
| **Kết luận** | _đang kiểm_ |

## Phạm vi diff

`git diff --stat origin/main...team/T-048`: 7 file, 3.423 dòng thêm, 0 dòng xóa.

| File | Dòng | Ghi chú |
|---|---|---|
| `seo_app/images/__init__.py` | 6 | Mới, chỉ docstring |
| `seo_app/images/folders.py` | 847 | Mới: `ImageRef`, `ImageLibrary`, `_Scan`, gọi Windows API qua `ctypes` |
| `tests/test_images_folders.py` | 962 | Mới (Thợ Máy) |
| `tests/test_images_folders_soi_loi.py` | 1.193 | Mới (Soi Lỗi) |
| `docs/team/reports/T-048-*.md` | 415 | Báo cáo |

Không đổi: `pyproject.toml`, `uv.lock`, `.gitignore`, `.env.example`, `.streamlit/`, `config/`, `app/` (`git diff origin/main...team/T-048 -- uv.lock pyproject.toml .gitignore .env.example .streamlit config app` rỗng). Chưa trang nào gọi `ImageLibrary` (grep `seo_app.images` trong `app/`: không có).

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt --no-hashes --frozen` (68 gói ghim, đúng `uv.lock` của nhánh, `pillow==12.3.0`) → `uvx pip-audit --no-deps --disable-pip -r …`: **No known vulnerabilities found**. Gói `-e .` (`seo-app`) bị bỏ qua vì không có trên PyPI, bình thường. Nhánh không đổi `uv.lock`; `main` đã đổi `uv.lock` (T-058, Pillow 13.0.0) sau gốc chung, kết quả quét bản gộp ở mục "Ghi chú cho Chỉ Huy khi gộp" | Có |
| bandit | `uvx bandit -r seo_app app scripts`: 1 Low (B101 `assert` ở `seo_app/storage/drafts.py:203`, có từ T-016, không thuộc phiếu). Riêng `seo_app/images/folders.py` + `__init__.py` (702 dòng): **No issues identified** | Có |
| detect-secrets | `uvx detect-secrets scan` trên 7 file của diff: `"results": {}`. Toàn bộ patch `git log -p origin/main..team/T-048` (4.120 dòng) quét riêng: `"results": {}` | Có |
| Soát lịch sử git | Patch của nhánh lọc `api[_-]?key\|password\|secret\|token`: 18 dòng, đều là dữ liệu test (`b"SECRET"`, `SECRET~1`, `.secret`, `os.link(secret, …)`) và chữ trong báo cáo. Toàn lịch sử (`git log -p --all`) lọc dạng khóa thật (`sk-ant-…`, `sk-proj-…`, `AIza…`, `BEGIN PRIVATE KEY`): chỉ có khóa giả có từ trước (`…KhoaGia…`, `ThuNghiemKhongPhaiKhoaThat`, `BIMAT_KHONG_DUOC_IN`, `AAAA…`), không dòng nào thuộc T-048 | Có |
| ruff | `uv run ruff check .`: **All checks passed!** `ruff format --check` 4 file Python của diff: đã đúng định dạng | Có |
| pytest | _đang chạy (toàn bộ, nền)_ | |

## Ghi chú cho Chỉ Huy khi gộp

- **`seo_app/images/__init__.py` cũng được T-050 tạo** (file rỗng, blob `e69de29`). T-048 tạo cùng file, có docstring. Tôi thử gộp không đụng thư mục làm việc (`git merge-tree --write-tree`):
  - `origin/main` + `team/T-048`: **sạch**, không xung đột (cây `ff133e4`).
  - `team/T-048` + `team/T-050`: **sạch**; bản gộp lấy đúng docstring của T-048 (blob `04c33dd`), đúng như bảng việc đã chốt. Lý do: git gộp "cùng thêm một file" mà một bên rỗng thì lấy bên có nội dung. Thứ tự gộp nào cũng ra cùng kết quả.
  - Docstring T-048 ghi "chỉ phiếu T-048 tạo nó" là chưa đúng hẳn (T-050 cũng tạo), không ảnh hưởng bảo mật.
- `main` đã đi xa gốc chung `5e38bb8` (49 file, có `uv.lock` của T-058). Code T-048 chỉ dùng thư viện chuẩn (`ctypes`, `msvcrt`, `os`, `stat`, `unicodedata`), không phụ thuộc phần `main` mới đổi.

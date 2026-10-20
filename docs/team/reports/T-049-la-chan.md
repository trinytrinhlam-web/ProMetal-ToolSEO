# Biên bản bảo mật T-049 · Xử lý ảnh: xoay, thu cạnh dài 1600 px, nén WebP giữ GPS, bản gửi AI sạch, tên file (G3-3)

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-049](../tickets/T-049-xu-ly-anh-webp-giu-gps.md) |
| Phạm vi | Diff `origin/main...team/T-049` tại `1f2f403` (gốc chung `132a73d`): `seo_app/images/process.py` (906 dòng, mới), `seo_app/images/naming.py` (85 dòng, mới), `tests/test_images_process.py` (Thợ Máy), `tests/test_soi_loi_t049.py` và `tests/test_pillow_heif_setup.py` (Soi Lỗi), 2 báo cáo. Đọc thêm code xung quanh: `seo_app/images/folders.py` (`read_image_bytes`, `stat_image`), `seo_app/text.py` (`slugify`), `seo_app/ai/base.py` (`prepare_images`), `tests/conftest.py`, `.gitignore`, `.streamlit/config.toml` |
| Ngày | 2026-10-20 |
| **Kết luận** | _(đang kiểm, điền ở phần cuối)_ |

## Tóm tắt (cho chủ dự án)

_(điền ở phần cuối)_

## Kết quả công cụ quét

Chạy trên máy Windows của chủ dự án, trong worktree `wt-T-049`, tại `1f2f403`, ngày 2026-10-20 13:50–14:10.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (`pillow==13.0.0`, `pillow-heif==1.8.1`). Nguồn PyPI: `No known vulnerabilities found`. Nguồn OSV (`-s osv`): `No known vulnerabilities found`. Môi trường đã cài (`--path .venv/Lib/site-packages`): `No known vulnerabilities found` (bỏ qua `seo-app` vì là chính dự án) | Có. `uv.lock`, `pyproject.toml` không đổi so với `main` (`git diff --quiet` đúng), nên kết quả giống `main`. Vẫn còn lưu ý LC-T058-4: cơ sở dữ liệu của pip-audit có thể chưa có khuyến cáo Pillow mới nhất |
| bandit 1.9.4 | `process.py` + `naming.py`: **No issues identified** (798 dòng). Toàn bộ `seo_app app scripts`: 9.639 dòng, 1 mục Thấp B101 (`assert`, `seo_app/storage/drafts.py:203`). File test của phiếu (chạy thêm, bỏ B101): B404/B603 (`subprocess` ở `tests/test_images_process.py:14`, `:1088`), B311 (`random` ở `tests/test_images_process.py:764`, `tests/test_soi_loi_t049.py:609`) | Có. B101 có từ trước, ngoài phạm vi. Mục ở file test là báo nhầm (xem "Báo nhầm đã loại") |
| detect-secrets 1.5.0 | **Bắt buộc `PYTHONUTF8=1` trên Windows** (LC-T049-4). Với `PYTHONUTF8=1`: 7 file của diff: **0**. Toàn bộ patch của nhánh (`git log -p origin/main..team/T-049`, 15 commit, 222 KB) kèm 2 chuỗi mồi (khóa AWS giả, `password = "…"`) trong cùng file: bắt **đủ 2 mồi, 0 mục khác**. Toàn bộ lịch sử mọi nhánh (`git log -p --all`, 7,5 MB): khoảng 100 mục, **tất cả là dữ liệu giả** của test hoặc câu trong biên bản cũ (xem "Soát lịch sử git") | Có. Không đặt `PYTHONUTF8=1` thì công cụ **bỏ qua lặng lẽ** mọi file có chữ tiếng Việt: quét các file git đang theo dõi chỉ ra 1 file (`tests/test_config.py`), đặt `PYTHONUTF8=1` thì ra 59 file. Chi tiết ở LC-T049-4 |
| Soát lịch sử git | Lệnh ở `security.md` mục 5 (`grep -inE "api[_-]?key\|password\|secret\|token"`) trên `git log -p origin/main..team/T-049`: **0 dòng**. `git diff --numstat`: không có file nhị phân, không có ảnh nào được commit (ảnh trong test đều tạo bằng Pillow lúc chạy) | Có. Đối chiếu từng mục detect-secrets của toàn lịch sử với tên file: khóa giả có chữ `KhoaGia`, `SoiLoi…`, `T026…`, `BIMAT_KHONG_DUOC_IN`; mật khẩu giả `abcd efgh…`, `mat-khau-thu-123`; địa chỉ `user:pass@example.com`; câu mô tả mẫu khóa trong biên bản Lá Chắn cũ. Không có khóa thật |
| pytest (test liên quan, theo quy tắc mới) | `uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_ai_images.py tests/test_pillow_heif_setup.py tests/test_images_folders.py -q -rsxX`: **659 passed, 6 skipped, 3 xfailed in 55.18s**, mã thoát 0 | Có. 6 bỏ qua đều ở `test_images_folders.py` (symlink cần Developer Mode, nhánh Mac/Linux), có từ T-048. 3 xfail đúng là SL-T049-1, 2, 3 (`strict=True`). Test "chưa đăng ký HEIF" của T-047 **chạy thật**, không còn `skip`. Toàn bộ pytest do Chỉ Huy chạy khi gộp |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| Thử gộp | `git merge-tree --write-tree origin/main team/T-049` (không đụng thư mục làm việc) với `main` `a06982f`: **sạch**, cây `2bc9e54`, mã thoát 0 | Có (chạy lại với `main` mới nhất ở phần cuối) |

### Soát lịch sử git (chi tiết)

- Nhánh `team/T-049` có 15 commit riêng (`a293a1c` → `1f2f403`) và 1 commit gộp `main` (`8e76b54`). Mọi commit chỉ đụng 7 file của diff.
- Toàn bộ lịch sử mọi nhánh, quét lại với `PYTHONUTF8=1`: các mục rơi vào `tests/test_ai_*.py`, `tests/test_env_file.py`, `tests/test_settings_keys.py`, `tests/test_soi_loi_*.py`, `tests/test_storage_drafts.py`, `tests/test_config.py` (khóa, mật khẩu giả để kiểm câu lỗi không chép khóa) và các biên bản `T-002`, `T-003…`, `T-008r3…`, `T-015`, `T-016…`, `T-038`, `T-042`, `T-048`, `T-051`, `T-062` (câu mô tả mẫu khóa, lệnh mẫu với `sk-test`). `seo_app/ai/base.py:29` là chú thích mô tả mẫu `người-dùng:mật-khẩu@` mà hàm che khóa nhận ra. Không có Application Password, khóa API, file service account thật.

## Thử độc lập của Lá Chắn

Script trong thư mục tạm của phiên (không commit), ảnh giả tạo bằng Pillow, không mạng, gọi thẳng `seo_app.images.process` và `seo_app.ai.base.prepare_images` của nhánh.

**T1 · Đầu WebP lạ (soát `_webp_canvas_pixels`, `process.py:160-181`)**

| Ca | Tiền kiểm | Kết quả |
|---|---|---|
| Chunk lạ `JUNK` đứng trước `VP8 ` | không đọc được (None) | "không phải ảnh JPEG, PNG, WebP hoặc HEIC" (libwebp từ chối, không cấp bộ nhớ khung) |
| `ALPH` đứng trước `VP8 ` | None | như trên |
| `VP8X` khai khung 100 × 100, bên trong ảnh `VP8 ` thật 640 × 480 | 10.000 | "Ảnh bị hỏng…" |
| `VP8X` khai khung 20.000 × 20.000 | 400 triệu | "Ảnh có quá nhiều điểm ảnh (400 triệu)…", chặn **trước** `Image.open` |
| `VP8L` sai chữ ký | None | "Ảnh bị hỏng…" |

Không tìm được cách đi vòng bước tiền kiểm: chunk đầu không phải `VP8 `/`VP8L`/`VP8X` thì libwebp từ chối ngay, còn khung khai nhỏ hơn ảnh thật thì hỏng lúc giải mã.

**T2 · Bản gửi AI và ảnh xem trước (A3).** Nguồn JPEG, PNG (RGBA), WebP, HEIC 1200 × 900, mỗi nguồn gắn mốc chữ riêng ở mọi chỗ chứa metadata: EXIF `ImageDescription`, `Artist`, `BodySerialNumber`, `CameraOwnerName`, MakerNote, `UserComment`, `LensSerialNumber`, `GPSProcessingMethod`, GPS (10°46'34,56" B, 106°41'12,34" Đ, cao 12,34 m), Orientation = 6; XMP có tọa độ; chú thích COM (JPEG); `tEXt`, `iTXt` nén và không nén (PNG); hồ sơ màu RGB có chữ "địa chỉ khách" trong thẻ `desc`. Nguồn chứa 11–16 mốc. Kết quả: bản AI (`make_ai_image`) và ảnh xem trước (`make_preview`) của cả 4 nguồn **không còn mốc nào**, không còn chuỗi `Exif`, `ICC_PROFILE`, `acsp`, `GPS`, `http://ns.adobe.com`; cả 8 file qua `prepare_images` (T-050).

**T3 · Ảnh đăng web (F2, quyết định 2A).** Cùng 4 nguồn → `make_web_image`: ảnh xoay đúng (1200 × 900 → 900 × 1200), GPS đọc lại độc lập **đúng từng giá trị** (vĩ độ `(10, 46, 34.56)`, kinh độ đúng, `N`/`E`, độ cao 12,34), `web.gps` = (10,7762667; 106,6867611). Thẻ IFD0 chỉ còn `Make`, `Model`, `Orientation`, `DateTime`; Exif IFD chỉ `DateTimeOriginal`; không IFD1. Trong byte WebP không còn mốc số seri, chủ máy, MakerNote, `UserComment`, XMP, COM, chunk chữ PNG, `GPSProcessingMethod`. Hồ sơ màu giữ nguyên byte (đúng điều kiện 2 của Lá Chắn T-050; xem ghi nhận N3).

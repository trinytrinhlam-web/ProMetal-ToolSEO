# Báo cáo T-078 (phần Thợ Máy) · `uv` tối thiểu 0.13.4, bỏ `.avif` khỏi danh sách đuôi ảnh

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | T-078 `T-078-nang-uv.md` (phần Thợ Máy; Chỉ Huy B giao 30/10 22:45, mở rộng thêm việc bỏ `.avif`) |
| Nhánh | `team/T-078` (từ `origin/main` `a416e74`) |
| Ngày nộp | 2026-10-30 22:45 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Phần mềm nay **không chạy với công cụ `uv` cũ hơn 0.13.4**. Bản cũ còn tin một chứng chỉ đã bị lộ khóa, nên kẻ xấu có thể giả kho thư viện Python để cài mã độc. Máy nào còn `uv` cũ thì khi mở app, `uv` báo bằng tiếng Anh và dừng. Cách xử lý: chạy `uv self update` rồi mở lại app. Thư Ký sẽ ghi hướng dẫn này vào README.
- Máy Windows của anh/chị đã là `uv 0.13.4` (kiểm 30/10), nên không thấy gì khác.
- Khung chọn ảnh **không còn liệt kê ảnh `.avif`**. Phần mềm chưa bao giờ mở được ảnh AVIF; trước đây ảnh hiện ra rồi mới báo «không phải ảnh». File AVIF bị đổi đuôi thành `.jpg` vẫn bị từ chối với câu báo cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `pyproject.toml` | `[tool.uv]` có sẵn: thêm `required-version = ">=0.13.4"`, kèm chú thích tiếng Việt (T-078, LC-T075-1, GHSA-hq85-5cpj-mr62, câu báo của `uv`, cách xử lý `uv self update`). `uv.lock` **không đổi** (`git diff uv.lock` rỗng; `uv lock --check` đạt) |
| `seo_app/images/folders.py` | `IMAGE_EXTENSIONS` bỏ `.avif` (nay `.jpg .jpeg .png .webp`; `.heic .heif` vẫn theo công tắc T-107). Chú thích ghi lý do. Câu báo của `ImageRef` bỏ chữ AVIF: «Chỉ nhận ảnh JPEG, PNG hoặc WebP (tạm chưa nhận ảnh HEIC của iPhone).», còn khi bật HEIC: «Chỉ nhận ảnh JPEG, PNG, WebP hoặc HEIC/HEIF.» |
| `tests/test_images_folders.py` | 2 ca đổi kỳ vọng (bảng dưới) |
| `tests/test_t078_avif_uv.py` (mới) | 11 ca (mục Kiểm thử) |

Không sửa: `README.md` (phần Thư Ký), `uv.lock`, `.claude/hooks/`, `app/**`, `process.py`.

### Ca test cũ đổi kỳ vọng (Chỉ Huy duyệt 30/10, R5: chỉ bỏ `.avif` khỏi danh sách mong đợi, không nới kiểm nào)

| Ca | Cũ | Mới |
|---|---|---|
| `test_images_folders.py::test_image_ref_accepts_normal_relative_paths` | 9 tên được nhận, có `x.avif` | 8 tên: bỏ `x.avif` (tên này nay bị từ chối; kiểm ở test mới `test_image_ref_rejects_avif_name`) |
| `test_images_folders.py::test_image_extensions_match_design` | `IMAGE_EXTENSIONS == {.jpg, .jpeg, .png, .webp, .avif}` | `IMAGE_EXTENSIONS == {.jpg, .jpeg, .png, .webp}`; hai điều kiện HEIC giữ nguyên |

Đã tìm mọi chỗ nhắc AVIF trong `seo_app/`, `app/`, `tests/`, `scripts/` (`grep -rni avif`):
- `process.py`: chỉ có chú thích, ghi app không mở AVIF.
- `test_images_process.py::test_avif_bi_tu_choi`, `test_t107_heic_tat.py` (nhận dạng hộp `ftyp` AVIF, câu «không phải ảnh»): vẫn đúng, không đổi.
- `seo_app/wordpress/client.py`: `IMAGE_TYPES` còn `.avif` → `image/avif`. Đây là danh sách loại file **tải lên** WordPress; app chỉ tải ảnh WebP do `make_web_image` dựng. Không thuộc phạm vi (không sửa `wordpress/**`), không ảnh hưởng.

## Câu báo của `uv` khi quá cũ (yêu cầu 2)

Không hạ cấp máy thật. Để thấy cơ chế, tôi dựng một dự án thử trong thư mục tạm với `required-version = ">=99.0"` và chạy bằng `uv 0.13.4` trên máy. `uv sync`, `uv run`, `uv lock` đều dừng ngay, chưa cài hay chạy gì, với câu:

```
error: Required uv version `>=99.0` does not match the running version `0.13.4`. Update `uv` by running `uv self update`.
```

Với dự án này, máy còn `uv 0.12.23` sẽ thấy câu dạng: «Required uv version `>=0.13.4` does not match the running version `0.12.23` …». Phần đuôi gợi ý «Update `uv` by running `uv self update`» là câu của bản 0.13.4; tôi chưa đối chiếu được câu của bản 0.12.x, vì không hạ cấp máy. Thư Ký nên ghi trong README theo phần đầu câu («Required uv version»), cách xử lý là `uv self update`.

Với `uv 0.13.4` thật trên máy, dự án vẫn chạy bình thường: `uv sync` (cài lại đúng gói dự án), `uv run python`, `uv lock --check`, và mọi test dưới đây qua.

- **Khi chạy `run.bat` / `run.command`:** lệnh `uv` báo lỗi trên và dừng, app không mở. Thư Ký ghi vào mục «Xử lý sự cố».
- **`uv` cài qua `pip` (không phải bộ cài riêng):** `uv self update` báo không tự nâng được; khi đó nâng bằng `pip install --upgrade uv` hoặc cài lại theo hướng dẫn chính thức. Thư Ký nên ghi một dòng cho trường hợp này.

## Rủi ro: môi trường cloud (SessionStart hook)

`.claude/hooks/session-start.sh` chạy `uv sync` khi `CLAUDE_CODE_REMOTE=true`, có `set -euo pipefail`. Nếu `uv` cài sẵn trên máy cloud cũ hơn 0.13.4:
- `uv sync` dừng với câu báo trên, nên hook lỗi và thư viện không được cài;
- trong phiên cloud, `uv run pytest`, `uv run ruff` cũng dừng cùng câu, nên không chạy được test.

Không mất dữ liệu, không lộ gì; chỉ là phiên cloud không làm việc được tới khi nâng `uv`. Tôi không chạy cloud nên chưa biết bản `uv` ở đó.

Đề xuất (phiếu sau, cần Chỉ Huy và Lá Chắn duyệt vì hook sẽ tải công cụ từ mạng): trước `uv sync`, hook kiểm `uv --version`; thấp hơn 0.13.4 thì chạy `uv self update`, không được thì `pip install --upgrade "uv>=0.13.4"`, rồi mới `uv sync`. Cách khác, ít đụng hơn: lần tới chạy phiên cloud (T-063 lượt Linux), Chỉ Huy chạy `uv --version` đầu phiên và nâng tay nếu cần. Tôi **không** sửa hook ở phiếu này (ngoài phạm vi).

## Kiểm thử

- `tests/test_t078_avif_uv.py`: **11 qua**.
  - `pyproject.toml` khai đúng `required-version = ">=0.13.4"` (đọc bằng `tomllib`).
  - `.avif` không nằm trong `IMAGE_EXTENSIONS`; AVIF không nằm trong định dạng được mở.
  - `ImageRef` tên `.avif`, `.AVIF` bị từ chối đúng câu, cả khi bật lại công tắc HEIC (3 ca).
  - Thư mục có `.avif`, `.AVIF`, `.Avif` và một ảnh JPEG: chỉ JPEG được liệt kê.
  - File AVIF thật (dựng bằng bộ mã hóa AVIF của Pillow 13) đổi đuôi `.jpg`: vẫn được liệt kê, nhưng cả 4 đường (`open_image`, `make_preview`, `make_ai_image`, `make_web_image`) báo đúng câu «File này không phải ảnh JPEG, PNG hoặc WebP đọc được …» (4 ca).
  - Trang Soạn bài thật (AppTest): khung chọn ảnh không có `IMG_0007.avif`; `IMG_0008.jpg` (AVIF đổi đuôi) có trong khung nhưng nút «Chọn» bị khóa, câu báo đúng.
- Test liên quan: 49 file. Gồm mọi file test nhắc `IMAGE_EXTENSIONS`, `ImageRef`, `list_folder`, `ImageLibrary`, `seo_app.images.folders`, HEIC/HEIF hay AVIF (ảnh, thư mục, thẻ ảnh, HEIC T-107, T-047/T-049/T-058/T-080, trang ảnh), cộng `test_app_pages.py`. Kết quả: **4797 qua, 51 bỏ qua, 19 xfail, 0 hỏng, không XPASS** (36 phút).
  - 19 xfail đều là dấu có từ trước của phiếu khác.
  - 51 bỏ qua: ca chỉ chạy trên Linux/Mac.
- `uv run ruff check .`: All checks passed. `ruff format --check` các file đã sửa: sạch.

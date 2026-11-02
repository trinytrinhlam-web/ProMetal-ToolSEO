# Báo cáo T-078 (phần còn lại) · `uv` tối thiểu 0.13.4, bỏ AVIF · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-078 `docs/team/tickets/T-078-nang-uv.md` (đọc ở bản trên `main`) · mức kiểm **rút gọn**, Windows. Không chạy cloud, không đụng website |
| Ngày nộp | 2026-10-31 |
| Máy kiểm | Windows 11 Pro 10.0.26300, `uv 0.13.4` (một bản duy nhất, ở `%USERPROFILE%\.local\bin\uv.exe`, cũng là bản `run.bat` dùng), Python 3.12.15, Pillow 13.0.0 (có bộ mã AVIF). Máy đang chạy toàn bộ test trên `main` |
| Mã nguồn | `team/T-078` tại `10d33f4` (Thợ Máy `1ebf679`, Thư Ký `10d33f4`, gốc `origin/main` `a416e74`). Gộp thử với `main` cục bộ `3cdd096` (đã có T-102) |
| Kết quả | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Khung chọn ảnh không còn liệt kê `.avif` ở mọi đường; AVIF đổi đuôi bị từ chối đúng câu; HEIC tắt không đổi. Không test nào trên nhánh hay trên `main` còn ghim danh sách đuôi hay câu báo cũ; R5 đúng danh sách Chỉ Huy duyệt. `required-version` chặn `uv` cũ ở mọi lệnh dự án, câu README khớp câu thật. Gộp `main` `3cdd096` sạch. **1 ghi nhận chuyển Lá Chắn (GN-1):** `required-version` không chặn `uvx` / `uv tool run` |

## Tóm tắt (cho chủ dự án)

- **Chặn `uv` cũ hoạt động đúng.** Với `uv` cũ hơn 0.13.4, lệnh mở app (`uv sync`, `uv run`) dừng ngay, chưa cài hay chạy gì, kèm câu báo khớp README. Máy Windows (`uv 0.13.4`) vẫn chạy bình thường.
- **Khung chọn ảnh không còn hiện ảnh AVIF.** Đã thử mọi đường; file AVIF bị đổi đuôi `.jpg` vẫn bị từ chối đúng câu. HEIC vẫn tạm tắt như cũ.
- **Không có lỗi mới.** Có 1 ghi nhận nên chuyển Lá Chắn: lệnh `uvx` (agent dùng để chạy công cụ kiểm tra) **không** bị chặn khi `uv` cũ. Máy Windows đã nâng `uv` nên không bị ảnh hưởng; cần chú ý khi chạy phiên cloud hay có máy Mac.
- Gộp với `main` mới nhất trên máy: không xung đột.

## Việc 1 · AVIF không còn được liệt kê ở mọi đường — **đạt**

`sl078_avif.py`: thư mục ảnh thật trong thư mục tạm, với các file:
- AVIF thật (bộ mã AVIF của Pillow 13) tên `.avif`, `.AVIF`, `.Avif`; một file `.avif` nằm trong thư mục con, để thử quét đệ quy;
- AVIF đổi đuôi `.jpg`, `.png`, `.webp`;
- HEIC tên `.heic`, HEIC đổi đuôi `.avif` và `.jpg`;
- một JPEG thật.

| Đường | Kết quả |
|---|---|
| Liệt kê thư mục | Chỉ còn `anh-that.jpg` và 4 file đổi đuôi (`.jpg/.png/.webp`). `.avif/.AVIF/.Avif` và `.heic` không hiện, được đếm vào «file khác bị bỏ qua» (`other_files` = 5), khớp câu README «file khác (kể cả ảnh AVIF `.avif`) bị bỏ qua (khung ghi số mục bỏ qua)» |
| Quét đệ quy cả công trình | Như trên; `sau/IMG_0009.avif` không hiện, `other_files` = 6 |
| `ImageRef` tên `x.avif`, `x.AVIF` | «Chỉ nhận ảnh JPEG, PNG hoặc WebP (tạm chưa nhận ảnh HEIC của iPhone).» Bật HEIC: «Chỉ nhận ảnh JPEG, PNG, WebP hoặc HEIC/HEIF.» (test Thợ Máy) |
| AVIF tên `.avif` hay đổi đuôi `.jpg/.png/.webp`, qua `open_image`, `make_preview`, `make_ai_image`, `make_web_image`, `PreviewCache.get` | Cả 5 đường: «File này không phải ảnh JPEG, PNG hoặc WebP đọc được (có thể bị đổi đuôi hoặc hỏng).» |
| Trang Soạn bài (AppTest của Thợ Máy) | `IMG_0007.avif` không có trong khung; `IMG_0008.jpg` (AVIF đổi đuôi) có, nhưng nút «Chọn» khóa, câu báo đúng |
| HEIC (T-107 lượt 3) | Không đổi: `.heic` không hiện; HEIC đổi đuôi `.avif` hay `.jpg` báo «Tạm chưa nhận ảnh HEIC của iPhone, hãy dùng ảnh JPEG.» ở cả 5 đường |
| Nháp cũ đã chọn file `.avif` | Không có được qua giao diện: trước T-078, ảnh `.avif` hiện trong khung nhưng nút «Chọn» khóa vì không dựng được ảnh xem trước. Thử bằng nháp **sửa tay** trỏ `.avif`: ảnh bị bỏ như «ảnh hỏng» (`dropped_images = 1`), phần chữ còn. Cùng cơ chế với SL-T107-3 (đã báo ở T-107). Không cần sửa riêng cho AVIF |
| Kho thẻ ảnh sửa tay có dòng `.avif` | Dòng đó chỉ bị bỏ qua khi đọc; kho **không** bị coi là hỏng (`recovered_from` = `None`), đọc ảnh khác bình thường |
| Cài đặt → Ảnh | Không dùng danh sách đuôi: tab chỉ liệt kê thư mục gốc (`ImageLibrary.roots()`), không bị ảnh hưởng |

## Việc 2 · Tìm mọi chỗ còn `avif`/`AVIF` — **đạt**

Đã chạy `git grep -i avif` trên `tests/ app/ seo_app/ README.md config/ scripts/ .claude/`, **cả trên nhánh lẫn trên `main` `3cdd096`** (bài học T-101). Trên nhánh còn:
- `README.md:336`: câu mới «(kể cả ảnh AVIF `.avif`) bị bỏ qua». Đúng.
- `seo_app/images/folders.py:60–61`, `process.py:64–65, 283`: chú thích, đúng.
- `seo_app/wordpress/client.py:626`: `".avif": "image/avif"` trong danh sách loại file **tải lên** WordPress. App chỉ tải WebP do `make_web_image` dựng, nên không ảnh hưởng (ngoài phạm vi, như Thợ Máy và Chỉ Huy đã nêu).
- Test: `test_images_process.py::test_avif_bi_tu_choi` (AVIF bị từ chối), `test_t107_heic_tat.py` (nhận dạng `ftyp` AVIF, câu «không phải ảnh»), `test_t078_avif_uv.py`. Cả ba vẫn đúng ý.

Test ghim danh sách đuôi hay câu báo cũ:
- Trên `main`, ngoài 2 dòng T-078 đã sửa có Chỉ Huy duyệt (`x.avif` trong `test_image_ref_accepts_normal_relative_paths`, tập `IMAGE_EXTENSIONS` trong `test_image_extensions_match_design`), không file test nào ghim `IMAGE_EXTENSIONS` hay câu «… hoặc AVIF …».
- `test_images_folders.py:199` chỉ khớp «Chỉ nhận ảnh». `:230` khớp «tạm chưa nhận ảnh HEIC của iPhone», vẫn có trong câu mới.
- Các file test `main` thêm sau `a416e74` (T-101, T-102…) đều không nhắc AVIF. Chỉ `test_app_images.py` và `test_t102_publish.py` dùng thư mục ảnh; cả hai đã chạy trên bản gộp thử (Việc 4).

R5: diff test của nhánh chỉ có 2 chỗ sửa trong `test_images_folders.py`, đúng danh sách Chỉ Huy duyệt:
- bỏ `x.avif` khỏi danh sách tên được nhận, chuyển sang test từ chối `test_image_ref_rejects_avif_name`;
- bỏ `.avif` khỏi tập mong đợi; hai điều kiện HEIC giữ nguyên.

Không nới kiểm nào; còn lại là file test mới `test_t078_avif_uv.py`. Các test mới ghim **giá trị chính xác**: tập đuôi, câu báo đủ chữ, chuỗi `required-version` đọc bằng `tomllib`. Đổi bất cứ giá trị nào là test hỏng.

## Việc 3 · `required-version` — **đạt**, kèm ghi nhận GN-1

- Trên nhánh với `uv 0.13.4` thật: `uv lock --check` đạt (`uv.lock` không đổi), `uv run --frozen python` chạy, và mọi test dưới đây chạy bằng môi trường của nhánh.
- Câu báo thật khi `uv` cũ hơn yêu cầu. Thử trong thư mục tạm: chép `pyproject.toml` + `uv.lock` của nhánh, sửa thành `>=0.13.5` để `uv 0.13.4` đóng vai bản cũ, không hạ cấp máy. Kết quả:
  - `uv sync`, `uv run`, `uv run --frozen`, `uv run --with six`, `uv lock --check`, `uv pip list` đều dừng ngay, không tạo `.venv`;
  - câu báo: ``error: Required uv version `>=0.13.5` does not match the running version `0.13.4`. Update `uv` by running `uv self update`.``
- Đối chiếu README:
  - Mục 2, mục 3 và dòng mục 13 («`error: Required uv version … does not match the running version …`», «chỉ cần câu bắt đầu bằng `Required uv version`») **khớp** câu thật.
  - `run.bat` và `run.command` in câu này rồi in «Cài thư viện bị lỗi…». Trên Windows, chữ trong cửa sổ không dấu: «Cai thu vien bi loi», có từ trước, giống dòng cũ của README.
  - `set_password.bat` / `.command` gọi `uv run`, nên cũng báo câu này như README ghi.
- Số mục README trỏ đúng: «xem mục 13», «cuối mục 2 (Windows) / cuối mục 3 (Mac)», mục 12.
- `run.bat`/`run.command` chỉ cài `uv` khi `where uv` / `command -v uv` không thấy, nên **không tự nâng** bản đã có, đúng như README.
- Đường dẫn README gợi ý khi không thấy lệnh `uv`:
  - Windows: `%USERPROFILE%\.local\bin\uv.exe`, đúng chỗ bộ cài đặt và `run.bat` (`set PATH=%USERPROFILE%\.local\bin;…`) dùng.
  - Mac: `~/.local/bin/uv`, như `run.command`.
- Hook SessionStart cloud (`.claude/hooks/session-start.sh`, đọc mã, **không chạy cloud**):
  - Hook có `set -euo pipefail` rồi `uv sync`. Nếu `uv` trên máy cloud cũ hơn 0.13.4, hook dừng với câu trên, và trong phiên đó `uv run pytest`, `uv run ruff` cũng dừng.
  - Không mất dữ liệu, không lộ gì. Đúng như rủi ro Thợ Máy ghi; đề nghị đầu phiên cloud chạy `uv --version` và nâng nếu cần.
  - Không có CI (`.github` không có).

## Việc 4 · Gộp thử với `main` `3cdd096` — **sạch**

- `main` chứa `a416e74`. Từ đó tới `3cdd096`, `main` **không** sửa `README.md`, `pyproject.toml`, `uv.lock`, `seo_app/images/`, `tests/test_images_folders.py` hay `.claude/`.
- `git merge-tree --write-tree main team/T-078`: **không xung đột** (cây `eb41bde`).
- Gộp thật ở worktree tạm tách rời (commit treo `b3b78c4`, không đẩy; đã kiểm `seo_app` nạp từ chính worktree tạm, `IMAGE_EXTENSIONS` không có `.avif`). Chạy `test_t078_avif_uv`, `test_images_folders`, `test_app_images`, `test_t102_publish`, `test_t107_heic_tat`, `test_drafts_images`: **606 qua, 12 bỏ qua, 0 hỏng, 0 xfail, không XPASS** (12 phút, máy bận). Chạy lại sáng 31/10: lượt đầu bị dừng khi máy tắt lúc 00:45.
- Worktree tạm đã gỡ.

## Test chọn lọc trên nhánh

11 file: `test_t078_avif_uv`, `test_images_folders`, `test_t107_heic_tat`, `test_images_process`, `test_app_images`, `test_drafts_images`, `test_images_tags`, `test_soi_loi_t056`, `test_soi_loi_t080`, `test_la_chan_t093`, `test_la_chan_t107`. Kết quả: **1324 qua, 13 bỏ qua, 4 xfail, 0 hỏng, không XPASS** (8 phút, máy bận). 4 xfail đều có từ trước, của phiếu khác. 13 bỏ qua là ca chỉ chạy trên Linux/Mac.

## Lỗi mới

Không có.

## Ghi nhận (không phải lỗi)

- **GN-1 (chuyển Lá Chắn, D1): `required-version` không chặn `uvx` / `uv tool run`.**
  - Cùng thư mục thử ở Việc 3 (khai `>=0.13.5`), `uvx --offline detect-secrets --version` và `uv tool run --offline detect-secrets --version` vẫn **chạy** (in `1.5.0`), không báo gì. `uv` không đọc `required-version` của dự án cho lệnh công cụ.
  - Phiếu nêu mục tiêu bảo vệ cả lúc agent chạy `uvx`. Với `uv` cũ, `uvx` vẫn tải gói từ mạng bằng bộ chứng chỉ cũ. `uv run --with` và `uv lock --upgrade-package` thì có bị chặn.
  - Máy Windows đã 0.13.4 nên không bị. Chỗ còn hở: phiên cloud, máy Mac sau này.
  - Câu «bản cũ hơn bị từ chối» trong README (mục «Dành cho người phát triển») và chú thích `pyproject.toml` đúng với lệnh dự án, chưa đúng với `uvx`.
  - Đề nghị: quy tắc cho agent, trước `uvx` chạy `uv --version` (hay kiểm trong hook cloud như Thợ Máy đề xuất). Có thể thêm nửa câu vào README phần người phát triển. Không sửa được bằng mã trong phạm vi phiếu.
- **GN-2:** nháp sửa tay trỏ ảnh `.avif` bị bỏ ảnh như «ảnh hỏng». Cùng cơ chế SL-T107-3 (Thấp, đã báo ở T-107). Không có được qua giao diện, vì nút «Chọn» luôn khóa với ảnh AVIF.
- **GN-3:** `uv` rất cũ, có từ trước khi có khóa `required-version`, sẽ không hiểu khóa này. Không kiểm vì không hạ cấp máy. Máy Windows đã 0.13.4, chưa có máy Mac, nên chưa có máy nào ở trường hợp này.
- **GN-4:** máy có nhiều bản `uv` thì `uv --version` gõ trong cửa sổ lệnh có thể là bản khác bản `run.bat` dùng, vì `run.bat` đặt `%USERPROFILE%\.local\bin` lên đầu `PATH`. Máy Windows hiện chỉ có một bản. Gợi ý cho Thư Ký nếu sửa README lần sau: bảo người dùng gõ thẳng `%USERPROFILE%\.local\bin\uv.exe --version` khi bản đã nâng mà app vẫn báo `Required uv version`.

## Tệp và cách chạy lại

- Script (thư mục ghi chú chung, `T-107-soi-loi-scripts/`, chạy từ worktree bằng `.venv/Scripts/python.exe -X utf8 <script>`): `sl078_avif.py`, AVIF ở mọi đường, nháp và kho thẻ có dòng `.avif`.
- Thử `required-version`: chép `pyproject.toml`, `uv.lock` vào thư mục tạm, sửa thành `>=0.13.5`, chạy `uv sync`, `uv run python -c "print(1)"`, `uvx --offline detect-secrets --version`.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): báo cáo **0** phát hiện; file mồi 2 phát hiện. Soi Lỗi không thêm hay sửa file test nào ở phiếu này.

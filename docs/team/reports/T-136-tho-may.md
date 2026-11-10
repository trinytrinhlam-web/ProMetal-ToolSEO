# Báo cáo T-136 · Gom kiểm file 5 kho SQLite, sửa LC-T131-1, câu báo kho nháp

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-136](../tickets/T-136-gom-kiem-file-5-kho.md) · Lá Chắn T-131 B.1, B.2, B.4, LC-T131-1 · Soi Lỗi T-131 GN-1 → GN-3 |
| Nhánh | `team/T-136`, từ `main` `71322c4`; mã và test `c48aedd`, báo cáo ở commit ngay sau |
| Ngày nộp | 2026-11-10 (giờ máy, +07) |
| Kết quả | Hoàn thành: yêu cầu 1–5 |

## Tóm tắt (cho chủ dự án)

- Năm kho dữ liệu trong máy dùng chung **một** bộ kiểm file. Năm kho là: nháp, thẻ ảnh sửa tay, danh sách bài đã đăng, kế hoạch, số liệu Google. Trước đây mỗi kho có một bản chép riêng, nên sửa một chỗ dễ sót chỗ khác.
- Hai kiểu file bị chương trình khác sửa tay trước đây làm app báo lỗi mãi. Nay app tự thoát được:
  - **một ô chữ trong file nháp bị hỏng mã**: chỉ nháp đó bị bỏ khỏi danh sách, các nháp khác vẫn hiện;
  - **đầu file ghi «phiên bản» lạ**: file được cất sang một bên (nháp, thẻ ảnh) hay bỏ đi (ba kho lưu tạm), rồi app tạo file mới. Cả 5 kho làm như vậy.
- Câu «File nháp cũ bị hỏng nên đã được cất sang một bên…» nói thêm hai ý:
  - trường hợp chỗ đặt file là **lối tắt**;
  - dấu «đã gửi» nằm trong file cũ, nên trước khi gửi lại một bài hãy xem trên WordPress bài đó đã có chưa.
- File nháp ở chế độ chỉ đọc thì câu báo nói **«chỉ đọc»**, không nói «bị lỗi».
- Không đổi gì khác trên giao diện, không thêm thư viện.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/sqlite_file.py` (mới) | <ul><li>Phần kiểm file chung: `journal_paths`, `is_link` (liên kết tắt hay hard link), `remove_link`, `guard` (giới hạn truyền vào).</li><li>So cấu trúc: `schema_rows` / `app_rows` (ba kho lưu tạm: đủ bộ dòng `sqlite_master`, file trống thì được), `schema_by_table` / `app_table_names` (nháp, thẻ ảnh: từng bảng khớp, bảng thiếu thì được). Cả hai đọc danh sách có `LIMIT`.</li><li>**Mới:** `newer_file_format` (byte 18 hay 19 của đầu file lớn hơn 2).</li><li>`is_healthy` (nháp và ba kho lưu tạm), `create_tables` (ba kho lưu tạm: tạo mọi bảng trong một giao dịch ghi có kiểm lại).</li><li>`code`, `is_busy`, `keeps_file`, `KEEP_FILE_CODES` (có 13).</li></ul> Không nhập gì từ gói `seo_app.storage` |
| `seo_app/storage/search_cache.py` | <ul><li>Hàm cùng tên (`_guard`, `_is_link`, `_journal_paths`, `_expected_schema`, `_app_tables`, `_is_healthy`, `_code`, `_is_busy`) thành lớp mỏng gọi `sqlite_file`, truyền hằng số của kho lúc gọi.</li><li>Tạo bảng trong `_prepare` dùng `sqlite_file.create_tables`.</li><li>**GN-3:** `_KEEP_FILE_CODES` là bộ chung, có thêm 13 (đầy ổ).</li></ul> |
| `seo_app/storage/site_index.py` | Như trên; `_create_tables` gọi `sqlite_file.create_tables` |
| `seo_app/storage/plan_cache.py` | Như trên. **GN-2:** `_prepare` tạo hai bảng bằng `_create_tables` (một giao dịch ghi, kiểm lại cấu trúc trong giao dịch đó, như `site_index`). Trước đây hai câu `CREATE TABLE IF NOT EXISTS` tự ghi từng câu |
| `seo_app/storage/drafts.py` | <ul><li>Lớp mỏng như trên. `_is_healthy` gọi `sqlite_file.is_healthy`, kèm phần riêng của kho (`_no_oversized_cells`).</li><li>**LC-T131-1 (a):** `_Checked.keep_bad_text()` cho ô chữ có UTF-8 hỏng đọc ra một giá trị đánh dấu, thay vì làm cả câu SQL lỗi. `list_drafts` bỏ dòng đó và đếm vào `skipped`. `find_plan_draft`, `list_plan_writes` (mã nháp hỏng mã chữ) cũng bỏ qua dòng đó.</li><li>**LC-T131-1 (b):** đầu file byte 18–19 lớn hơn 2 thì `_is_healthy` trả `False`, nên file được cất sang một bên.</li><li>**B.4:** `_db_message` gặp mã 8 (`SQLITE_READONLY`) thì trả `_MSG_READONLY`.</li><li>**B.2, B.4:** câu chung `MSG_RECOVERED`, có trong `__all__`.</li></ul> |
| `seo_app/storage/image_tags.py` | <ul><li>Lớp mỏng cho `_guard`, `_is_link`, `_remove_link`, `_journal_paths`, `_expected_schema`, `_app_tables`, `_is_busy`.</li><li>`_is_healthy` giữ quy tắc riêng của kho, thêm kiểm byte 18–19 ở đầu (mục chọn 2).</li></ul> |
| `app/views/home.py`, `app/views/plan.py`, `app/views/write.py` | Ba trang dùng chung `drafts.MSG_RECOVERED` (trước đây ba bản chép). Trang Soạn bài nay thoát Markdown tên file như hai trang kia. Ngoài danh sách «Được sửa» của phiếu, nhưng yêu cầu 5 đòi sửa đúng câu này, mà câu nằm ở ba trang |
| `tests/test_la_chan_t131.py` | Gỡ dấu `xfail` của ca LC-T131-1 (R5, chỉ xóa dấu) |
| `tests/test_t136_kiem_file_chung.py` (mới) | Bảng ca chung cho 5 kho, 54 ca (mục Đối chiếu) |

### Chỗ để ngỏ, tôi đã chọn

1. **Mỗi kho giữ hàm cùng tên làm lớp mỏng**, chuyển hằng số của kho vào lúc gọi.
   - Test hiện có vá `_app_tables`, `_is_healthy`, `_is_busy`, `_MAX_VM_STEPS`, `_SQLITE_TIMEOUT`… của từng kho. Gọi thẳng hàm chung thì các chỗ vá đó mất tác dụng.
   - Hai kiểu so cấu trúc giữ nguyên như đã qua Lá Chắn: đủ bộ dòng (ba kho lưu tạm), từng bảng (nháp, thẻ ảnh).
2. **Kho thẻ ảnh giữ `_is_healthy` riêng.** Kho này có quy tắc lỗi riêng: chỉ «hỏng», «quá số bước», «quá dài» là file lạ, lỗi khác ném lại. Kho còn kiểm phiên bản trong bảng `info`. Gộp vào hàm chung sẽ đổi hành vi, nên tôi chỉ thêm hai thứ:
   - kiểm byte 18–19 (cùng lớp lỗi LC-T131-1 b);
   - định nghĩa liên kết chung của 4 kho kia (`data_dir.is_link`). Trước đây kho này chỉ xét symlink, junction, hard link; nay thêm reparse point trỏ đi chỗ khác. File «chỉ trực tuyến» của OneDrive, Google Drive vẫn không tính.
3. **B.2: chọn cách câu báo**, không chép dòng `send_states` từ file đã cất sang file mới (phiếu cho chọn một trong hai).
   - File bị cất vì đã bị coi là lạ: có thể có trigger, khung nhìn, ô hỏng. Đọc thêm từ nó đi ngược cách phòng thủ của kho.
   - Chép dòng gửi là đụng logic trạng thái gửi, nên Lá Chắn phải kiểm đầy đủ.
   - Câu báo nói rõ dấu «đã gửi» nằm trong file cũ và nhắc xem WordPress trước khi gửi lại. Bài trùng (nếu có) vẫn chỉ là **bài nháp**, vì W1 vẫn giữ.
4. **LC-T131-1 (a): chỉ bỏ dòng có ô chữ hỏng**, không cất cả file. Một ô hỏng không làm mất đường vào các nháp khác. Nháp hỏng ô `data` vẫn báo lỗi khi mở đúng nháp đó, như trước.
5. **Ngưỡng byte 18–19 là «lớn hơn 2».** Đã thử SQLite 3.53.1:
   - byte 18 bằng 3 hay 255 → đọc được, ghi lỗi mã 8 (kẹt mãi);
   - byte 19 bằng 3 hay 255 → mã 26 «not a database» (đã là file lạ từ trước);
   - bằng 0 → chạy bình thường.
6. **Câu báo `_MSG_READONLY`** chỉ cho kho nháp, đúng điều kiện B.4. Ba kho lưu tạm vốn đã nói «… hoặc không có quyền ghi».

## Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới |
|---|---|---|
| `test_la_chan_t131.py::test_lc_t131_1_hand_edited_draft_file_does_not_stay_stuck[utf8-hong-trong-o]` và `[byte-18-la-3]` | `xfail(strict=True)` | Bỏ dấu (đã XPASS); thân test không đổi |

Không đổi ca test cũ nào khác. Ca `test_app_drafts.py::test_corrupt_drafts_file_is_reported` vẫn qua: câu mới giữ đoạn «bị hỏng nên đã được cất sang một bên».

## Bằng chứng

```text
# Windows 11, Python 3.12.15, SQLite 3.53.1, ruff 0.16.10. Chạy trên đúng commit c48aedd
# (git status chỉ còn file báo cáo này chưa commit).

uv run pytest -q -p no:randomly tests/test_t136_kiem_file_chung.py tests/test_la_chan_t131.py
  56 passed            # 54 ca mới + 2 ca LC-T131-1 đã gỡ xfail (trước khi gỡ: 2 XPASS strict)

# 122 file test: mọi file nhập 5 kho, sqlite_file hay mở ba trang Bài viết, Kế hoạch, Soạn bài,
# cộng mọi test quét cả cây mã nguồn (glob, rglob, iterdir trên seo_app).
uv run pytest -q -p no:randomly -rfEsxX <122 file>
  11336 passed, 33 skipped, 13 xfailed in 4875.12s
  # 0 hỏng.
  # 33 bỏ qua, đều do máy Windows:
  #   - tạo symlink (chưa bật Developer Mode);
  #   - quyền kiểu POSIX, chmod 600, os.environb (chỉ có trên Mac/Linux);
  #   - một ca cần ổ phân biệt hoa thường.
  # 13 xfail: dấu có từ trước ở test_images_folders_soi_loi, test_soi_loi_round4,
  #   test_soi_loi_t070, test_soi_loi_t107; không ca nào XPASS.

# Đột biến (script ở thư mục nháp; mỗi lần trả file về đúng byte, kiểm SHA-256):
#   mỗi đột biến làm ít nhất một ca hỏng.
#   M1  newer_file_format luôn False             → 10 ca hỏng (byte 18 ở 5 kho, test_newer_file_format, ca Lá Chắn)
#   M2  keep_bad_text không làm gì               → 3 ca hỏng (2 ca kho nháp, ca Lá Chắn utf8-hong-trong-o)
#   M3  mã 8 vẫn báo «bị lỗi»                    → 2 ca hỏng
#   M4  plan_cache tạo bảng từng câu như cũ      → 1 ca hỏng (vết câu SQL)
#   M5  bộ mã chung thiếu 13                     → 16 ca hỏng

uv run ruff check .                     → All checks passed!
uv run ruff format --check              → 11 file đã đúng khuôn

# Quét bí mật: 11 file lấy từ c48aedd (git show) ở thư mục nháp, PYTHONUTF8=1, detect-secrets --all-files.
#   Có khóa AWS giả đối chứng → bắt được.
#   Chỉ còn app/views/write.py:2692 «Basic Auth Credentials»: docstring có từ commit 7aa4dbd, tả kiểu
#   «https://…:…@…», không phải dòng của phiếu này (diff ở write.py chỉ quanh dòng 4500).
# Ký tự ẩn, CR, NFC: 0 trong 11 file.
# Gộp thử: git merge-tree --write-tree với main 01fc45c (đã có T-131) → không xung đột.
#   Từ 71322c4, main chỉ sửa tài liệu (CLAUDE.md, TIEN-DO.md, board, 3 phiếu), không file nào của phiếu này.
```

## Đối chiếu tiêu chí

| Yêu cầu | Đáp ứng | Test |
|---|---|---|
| 1. LC-T131-1 (a), (b); gỡ 2 `xfail` | `keep_bad_text`; `newer_file_format` trong `is_healthy` | `test_la_chan_t131.py` (2 ca, gỡ dấu); `test_broken_text_cell_only_skips_that_draft`, `test_broken_id_does_not_break_plan_lookups`, `test_draft_with_newer_header_can_be_saved_again` |
| 2. Soi Lỗi GN-1, GN-2, GN-3 | GN-1: byte 18–19 ở cả 5 kho; GN-2: `plan_cache` tạo bảng một giao dịch; GN-3: bộ mã chung có 13 | `test_newer_header_is_a_foreign_file_in_every_store` (5 kho × 2 byte), `test_newer_file_format` (8 ca), `test_plan_cache_creates_both_tables_in_one_write_transaction` (vết câu SQL: hai `CREATE` nằm giữa `BEGIN IMMEDIATE` và `COMMIT`), `test_environment_errors_keep_the_file` (4 kho × 4 mã) |
| 3. Gom `_guard`, `_app_tables`, `_is_healthy`, `_is_link` (thêm `_journal_paths`, `_remove_link`), không đổi hành vi | `sqlite_file`, lớp mỏng ở từng kho | `test_every_store_uses_the_shared_checks`, `test_lowered_step_limit_still_stops_queries` (5 kho), `test_hard_link_and_plain_file`, `test_shared_module_only_runs_constant_sql`; toàn bộ test cũ của 5 kho (mục Bằng chứng) |
| 4. B.2 | Câu báo nói dấu «đã gửi» nằm trong file đã cất (mục chọn 3) | `test_recovered_message_tells_about_links_and_sent_marks`, `test_write_page_shows_the_shared_recovered_message` |
| 5. B.4 | Câu nói thêm lối tắt; mã 8 → «chỉ đọc» | Hai ca trên; `test_read_only_draft_file_says_read_only` (file thật đặt chỉ đọc), `test_db_message_cases` |

## Rủi ro và điểm cần chú ý

- **Kho thẻ ảnh nhận ra nhiều loại liên kết hơn** (mục chọn 2): reparse point trỏ đi chỗ khác ở chỗ đặt file thẻ nay bị gỡ, như 4 kho kia.
- **Kiểm byte 18–19 đọc 20 byte đầu file** trước khi SQLite mở. Chỉ chạy ở bước kiểm file, không chạy ở mỗi thao tác.
- **B.2:** dấu «đã gửi» không chép sang file mới. Người dùng phải xem WordPress trước khi gửi lại; câu báo có nhắc.
- **Mac:** ca symlink của T-131 và T-136 vẫn bỏ qua trên Windows (B.3, chạy khi có máy Mac).

## Đề xuất

- Soi Lỗi kiểm rút gọn; Lá Chắn kiểm rút gọn (phiếu ghi: đầy đủ nếu đụng logic trạng thái gửi — phiếu này không đụng).

## Câu hỏi cho chủ dự án

Không có.

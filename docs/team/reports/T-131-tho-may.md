# Báo cáo T-131 · Dọn kho dữ liệu phụ: kiểm file và chặn `data/` là liên kết

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-131](../tickets/T-131-don-kho-du-lieu-phu.md) |
| Nhánh | `team/T-131`, từ `main` cục bộ `f6a6e64`; phần 1–3: mã và test `e53ee48`, báo cáo ở commit ngay sau |
| Ngày nộp | Phần 1–3: mã commit 2026-11-05, báo cáo 2026-11-07 (giờ máy, +07). Lượt 2 (phần 4, SL-T131-1, docstring `set_gsc_site_url`): 2026-11-10 12:44 |
| Kết quả | Lượt 1: `site_index`, `plan_cache` xong. **Lượt 2: hoàn thành** (kho nháp, SL-T131-1, docstring) |

## Tóm tắt (cho chủ dự án)

- Hai file lưu tạm trong máy (danh sách bài đã đăng, kế hoạch đọc từ Google Sheets) nay được kiểm như file lưu tạm số liệu Google:
  - Thư mục `data` (hay thư mục con của nó) là lối tắt trỏ ra chỗ khác thì phần mềm không ghi, không xóa gì ở đó, báo một câu tiếng Việt. Danh sách bài, kế hoạch vừa tải vẫn dùng được.
  - File lưu tạm bị chương trình khác cài thêm bảng, trigger (đoạn lệnh tự chạy) thì phần mềm bỏ file và tải lại, không để trigger chạy làm treo máy.
  - File bị sửa tay kiểu lạ không còn làm phần mềm báo «không mở được» mãi: file tự bỏ và tạo lại.
- Không đổi gì trên giao diện, không đổi cách dùng. File lưu tạm cũ trên máy vẫn dùng tiếp, không bị bỏ.
- Phần kho nháp bài viết (`drafts.py`) làm sau, khi phiếu T-130 của Họa Sĩ (cùng file) đã gộp.

## Đã thay đổi (phần 1–3)

| File | Thay đổi |
|---|---|
| `seo_app/storage/site_index.py` | LC-T129-1, SL-T117-1, theo mẫu `search_cache`. <ul><li>`_prepare`: `dir_has_link` trước mọi việc (`SiteIndexError(MSG_DATA_DIR_LINK)`, không tạo thư mục, không mở). Chính file là liên kết (symlink, junction, reparse point, **hard link**) thì bỏ; file nhật ký là liên kết thì gỡ.</li><li>`_is_healthy`: so trọn `sqlite_master` với `_expected_schema` (dựng từ `_CREATE_TABLES` trong bộ nhớ), `quick_check`, đọc bằng `_decode_text`. Giữ file chỉ khi lỗi do môi trường (`_KEEP_FILE_CODES`).</li><li>`_create_tables`: chỉ tạo bảng khi file còn trống, kiểm lại trong giao dịch ghi.</li><li>`_connect`: `_guard` (`trusted_schema = OFF`, `_MAX_VM_STEPS`, `_MAX_SQLITE_LENGTH`), giao dịch tường minh, so cấu trúc **trong cùng giao dịch** trước mọi truy vấn khác. Quá số bước, giá trị quá dài thành `_Corrupt`.</li><li>`save`: gặp file lạ thì bỏ rồi ghi lại một lần trên file mới.</li><li>`clear`: kiểm liên kết; xóa cả file nhật ký.</li><li>Câu tạo bảng giữ nguyên chữ cũ, nên file cache cũ trên máy vẫn khớp.</li></ul> |
| `seo_app/storage/plan_cache.py` | SL-T117-1 và mẫu LC-T122-1. <ul><li>`_prepare`, `clear`: `dir_has_link` trước mọi việc. Chính file là liên kết (kể cả hard link) thì bỏ; nhật ký là liên kết thì gỡ.</li><li>`_is_healthy`: đọc `sqlite_master` bằng `_decode_text`, coi `_Corrupt` và mọi lỗi SQLite không thuộc `_KEEP_FILE_CODES` (gồm «unsupported file format») là file lạ.</li></ul> |
| `tests/test_t131_kho_du_lieu_phu.py` | Mới, 64 ca (2 ca symlink file bỏ qua trên máy không cho tạo symlink) |
| `tests/test_site_index.py` | Đổi kỳ vọng 1 ca theo R5 (bảng ngay dưới) |
| `tests/test_soi_loi_t117.py` | Gỡ dấu `xfail` của 2 tham số đã XPASS (R5), giữ dấu cho kho nháp |
| `docs/team/reports/T-131-tho-may.md` | Báo cáo này |

Không sửa `drafts.py`, `search_cache.py`, giao diện. Không thêm thư viện.

### Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới | Lý do |
|---|---|---|---|
| `test_site_index.py::test_extra_table_does_not_break_cache` (T-037) → đổi tên `test_extra_table_drops_the_cache` | Thêm bảng lạ vào file: cache vẫn đọc được | Bảng lạ là file lạ: `load` trả `None`, `reset_count == 1`, lần sau tải lại và lưu được | LC-T129-1 yêu cầu so trọn `sqlite_master` (bảng lạ, trigger, khung nhìn bị từ chối), như `search_cache`, `plan_cache`, kho thẻ ảnh |
| `test_soi_loi_t117.py::test_sl_t117_1_other_data_stores_never_write_through_link[cache-ke-hoach]`, `[danh-sach-bai-da-dang]` | `xfail(strict=True)` (SL-T117-1) | Gỡ dấu: hai tham số XPASS sau khi sửa. Dấu chuyển xuống riêng tham số `[kho-nhap]` | R5: ca XPASS thì chỉ gỡ dấu, không đổi kỳ vọng. Kho nháp làm ở phần 4 |

### Chỗ để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Mã lỗi giữ file | `_KEEP_FILE_CODES = {3, 5, 6, 7, 8, 10, 13, 14, 15}`: thêm 13 (`SQLITE_FULL`, đầy ổ) so với bản T-124 của `search_cache` | Test T-042 ghim «đầy ổ là không mở được, không xóa file». Bỏ file khi ổ đầy cũng không giúp gì. Đề xuất: thêm 13 cho `search_cache` (mục Đề xuất) |
| 2 | Trần số bước `site_index` | `_MAX_VM_STEPS = 50.000.000` (như `plan_cache`) | Đo: danh sách lớn nhất (10.000 dòng, chữ dài tối đa, file 41 MB) dùng tối đa 340.000 bước mỗi kết nối, chưa tới 1% trần |
| 3 | Trần độ dài | `_MAX_SQLITE_LENGTH = 1.000.000` byte | Một dòng hợp lệ dài nhất khoảng 48 KB (6 ô chữ, mỗi ô tối đa 8 KB). Có ca ghim trần ≥ 8 lần cỡ ô lớn nhất |
| 4 | Chính file là liên kết | `site_index`, `plan_cache` vẫn tính `reset_count` (như trước, khi chỉ xét symlink) | Giữ hành vi cũ đã có test |
| 5 | `plan_cache` tạo bảng | Giữ cách cũ (`CREATE TABLE IF NOT EXISTS` sau khi kiểm file) | Phiếu chỉ đòi phần `dir_has_link` và `_is_healthy`; `_connect` đã so cấu trúc trong giao dịch từ T-100 |

## Bằng chứng

```
# Windows 11, Python 3.12.15, ruff 0.16.10.

# 1) 3 file test mới, sửa (trên cây làm việc, trước commit)
$ uv run pytest -q tests/test_t131_kho_du_lieu_phu.py
62 passed, 2 skipped                     ← 2 ca symlink file: máy không cho tạo symlink

# 2) Trên đúng commit e53ee48 (git status chỉ còn file báo cáo này chưa commit): 61 file
#    = mọi file test nhắc site_index / SiteIndex / plan_cache / PlanCache, mọi test quét cả gói,
#    cả cây mã nguồn (grep rglob( / glob("*.py") / "seo_app" / / "storage"), test kế hoạch,
#    test theo dõi, test thẻ ảnh (cùng dùng data_dir), test_t131_kho_du_lieu_phu.py
$ uv run pytest -q -rfEsxX <61 file>
5544 passed, 8 skipped, 3 xfailed in 2769.80s (0:46:09)
#    0 hỏng. 8 bỏ qua đều do Windows (symlink cần Developer Mode, quyền kiểu chmod).
#    3 xfail: SL-T106-1 (2 ca, có từ trước, chờ T-132) và SL-T117-1 [kho-nhap] (phần 4).

$ uv run ruff check .                    # toàn repo
All checks passed!
$ uv run ruff format --check <5 file mới, sửa>
5 files already formatted

# Quét bí mật: bản sao 5 file đổi ở thư mục nháp, PYTHONUTF8=1, detect-secrets --all-files
results: {}
# Đối chứng: thêm một khóa giả vào bản sao site_index.py → bắt được (Secret Keyword). Đã xóa.

# Ký tự ẩn, CR (script ở thư mục nháp): 0 trong 5 file.
# Gộp thử: git merge-tree với main mới 06a1b0e (đã có T-124): không xung đột, không trùng file.
```

**Đo** (script ở thư mục nháp, file trong thư mục tạm):

- Số bước máy ảo SQLite mỗi kết nối, cỡ lớn nhất:
  - `site_index`: 10.000 dòng, chữ dài tối đa, file 41,2 MB. Ghi tối đa 320.000 bước, đọc tối đa 340.000. Trần 50.000.000.
  - `plan_cache`: 1.001 dòng × 26 ô, file 12,3 MB. Tối đa 21.000 bước. Trần 50.000.000.
- Thời gian đọc `site_index`, đo xen kẽ bản cũ (`f6a6e64`) và bản mới, lấy lần nhanh nhất:
  - cỡ lớn nhất: 12,24 s (cũ), 12,48 s (mới);
  - 200 bài link ngắn: 20 ms (cũ), 24 ms (mới).
  - Thời gian ở cỡ lớn nhất có từ trước: cProfile cho thấy gần hết nằm ở bước kiểm từng dòng `PublishedItem` (`_has_invisible`, `is_site_link` của client WordPress), T-131 không đụng.

**Thử đột biến** (script ở thư mục nháp: sửa cố ý một chỗ, chạy `test_t131_kho_du_lieu_phu.py`, `test_site_index.py`, `test_soi_loi_t117.py`, trả file về nguyên văn và kiểm SHA-256):

- Thay cả hai file bằng bản ở `main` `f6a6e64`: bị bắt.
- 16 đột biến: **13 bị bắt**, 3 sống.

| Mã | Đột biến | Kết quả |
|---|---|---|
| M01–M04 | Bỏ `dir_has_link` ở `_prepare`, `clear` của từng kho | Bị bắt cả 4 |
| M05, M06 | `site_index`: bỏ so cấu trúc trong giao dịch; bỏ `_guard` | Bị bắt cả 2 |
| M08–M10 | `_is_healthy` giữ mọi lỗi (bản cũ) ở `plan_cache`, `site_index`; bỏ mã 13 | Bị bắt cả 3 |
| M11, M12 | Bỏ nhận hard link ở chính file | Bị bắt. Lần đầu sống: file ngoài trong ca test không phải SQLite nên kiểu gì cũng bị bỏ. Đã sửa ca: đích hard link là file cache **hợp lệ** |
| M14, M15 | `save` không thử lại; quá số bước không coi là file lạ | Bị bắt cả 2 |
| M07 | `site_index._is_healthy` bỏ `text_factory` | **Sống, tương đương**: không có `text_factory` thì lỗi giải mã ra `OperationalError` không mã SQLite, vẫn rơi vào nhánh «file lạ» (như M12 của T-124). Giữ dòng cho rõ ý |
| M16 | `_create_tables` bỏ phép kiểm lần đầu | **Sống, tương đương**: phép kiểm lần hai trong giao dịch ghi vẫn chặn. Lần đầu chỉ để không phải xin quyền ghi |
| M13 | Bỏ gỡ liên kết ở file nhật ký | **Sống trên máy này**: với hard link, SQLite tự xóa nhật ký «không nóng» khi mở, nên kết quả như nhau. Chỗ chặn cần cho **symlink** (Mac/Linux): đã thêm `test_symlinked_journal_is_removed_not_followed`, bị bỏ qua trên Windows chưa bật Developer Mode |

## Đối chiếu tiêu chí xong

- [x] **Yêu cầu 1** (LC-T129-1, `site_index` kiểm file như `search_cache`):
  - trigger (nặng, chèn link lạ), bảng lạ, khung nhìn, chỉ mục, sai cột, đổi tên bảng thì bỏ file và tải lại: `test_site_index_file_with_foreign_structure_is_dropped` (7 ca);
  - trigger không chạy khi ghi: `test_site_index_trigger_never_runs_when_saving`;
  - kiểm lại trong giao dịch, khi đọc và khi ghi: `test_site_index_structure_checked_again_inside_transaction`;
  - `trusted_schema = OFF`, trần độ dài: `test_site_index_connections_are_guarded`;
  - quá số bước, giá trị quá dài là file lạ: `test_site_index_too_many_steps_counts_as_foreign_file`, `test_site_index_value_longer_than_limit_counts_as_foreign_file`;
  - trần còn dư cho cache lớn nhất: `test_site_index_steps_limit_has_room_for_the_biggest_cache`;
  - file cũ trước T-131 dùng tiếp: `test_site_index_old_file_from_before_t131_still_reads`.
- [x] **Yêu cầu 2** (SL-T117-1, phần `site_index`, `plan_cache`):
  - `data/` hay thư mục con là liên kết thì không tạo, không mở, không xóa, danh sách vừa tải vẫn dùng được: `test_site_index_never_opens_or_deletes_through_linked_data`, `test_plan_cache_never_opens_or_deletes_through_linked_data`, `test_linked_subfolder_of_data_is_also_refused`, `test_soi_loi_t117.py` hai tham số đã gỡ `xfail`;
  - lỗi quyền khi kiểm ra câu cố định: `test_permission_error_while_checking_links_is_a_fixed_message`;
  - chính file, nhật ký là liên kết: `test_hard_linked_cache_file_is_unlinked_not_followed`, `test_hard_linked_journal_is_unlinked_not_followed`, `test_symlinked_journal_is_removed_not_followed`;
  - kiểm trước khi tạo thư mục, trước khi xóa: `test_store_checks_linked_data_before_creating_and_before_clearing`.
  - Phần `drafts`: chờ T-130 (phần 4).
- [x] **Yêu cầu 3** (mẫu LC-T122-1, `plan_cache._is_healthy`, áp cả cho `site_index`):
  - UTF-8 hỏng trong `sqlite_master`, «schema format» 5 thì bỏ file và ghi lại được: `test_plan_cache_hand_edited_file_is_dropped_and_rewritable`, `test_site_index_hand_edited_file_is_dropped_and_rewritable`;
  - chỉ giữ file khi lỗi do môi trường: bảng 15 mã × 2 kho trong `test_health_check_keeps_file_only_on_environment_errors`, `test_health_check_without_code_is_foreign_file`.
- [ ] **Yêu cầu 4** (`drafts.py`): chờ T-130 gộp `main` (Chỉ Huy báo). Cùng lúc làm docstring `set_gsc_site_url` (Lá Chắn T-124 điều kiện 4).
- [x] **Yêu cầu 5**: test ghim từng phần (ở trên); chạy mọi nơi gọi và mọi test quét cả gói, cả cây mã nguồn (mục Bằng chứng, 61 file). `uv run ruff check .` sạch
- [x] Báo cáo phần 1–3

## Rủi ro và điểm cần chú ý

- **Hành vi đổi:** file danh sách bài có bảng, trigger, khung nhìn lạ nay bị bỏ một lần (trước đây vẫn đọc). File app tự tạo không có những thứ đó; file cũ đúng cấu trúc vẫn dùng tiếp (có ca test).
- **Symlink ở chính file, file nhật ký**: chỉ thử được trên Mac/Linux hay Windows bật Developer Mode; máy này bỏ qua 2 ca. Junction, hard link đã thử thật.
- **Danh sách bài cỡ lớn nhất đọc mất khoảng 12 giây** (có từ trước, mục Đo). Website thật vài trăm bài: khoảng 20 ms.
- Các kho giờ có mã kiểm file gần giống nhau ở 4 nơi (`search_cache`, `plan_cache`, `site_index`, kho thẻ ảnh); sửa một nơi nên rà các nơi kia.

## Đề xuất

- **Phần 4 (sau khi T-130 gộp):** gộp `main` vào nhánh, rồi làm hai việc.
  - `drafts.py`: thêm `dir_has_link`, gỡ liên kết, `_guard`, so cấu trúc. Kho nháp **giữ dữ liệu người dùng** nên vẫn đổi tên file hỏng sang một bên, không xóa. Cấu trúc phải nhận các bộ bảng của file cũ: thiếu `send_states` (trước T-086), thiếu `plan_writes` (trước T-100).
  - Docstring `set_gsc_site_url`: ghi rõ phải gọi sau `parse_property`.
- **`search_cache._KEEP_FILE_CODES` thêm 13** (`SQLITE_FULL`) cho khớp `site_index`, `plan_cache`. Một dòng, đổi khi tiện, có thể ở phần 4 nếu Chỉ Huy đồng ý.
- **Phiếu dọn sau (Thấp):** gom phần kiểm file SQLite dùng chung (`_guard`, `_app_tables`, `_is_healthy`, `_is_link`) về một module cho 5 kho, có bảng ca test chung.
- **Phiếu dọn sau (Thấp):** bước kiểm từng dòng `PublishedItem` (`_has_invisible` duyệt từng ký tự) là phần chậm khi đọc danh sách rất lớn.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (phần 4 · kho nháp, SL-T131-1, docstring `set_gsc_site_url`)

Thợ Máy khác (phiên này, model Claude Opus 5.5) làm tiếp theo tin Chỉ Huy B ngày 2026-11-10. Nhánh `team/T-131` đã gộp `main` cục bộ `7153f0a` (có T-130, T-132) ở commit `cd575a9` trước khi sửa; gộp sạch, không xung đột.

### Tóm tắt (cho chủ dự án)

- **Kho nháp bài viết** nay được kiểm như các file lưu tạm. Kho này giữ bài đang soạn và dấu «đã gửi» chống gửi trùng.
  - Thư mục `data` là lối tắt trỏ ra chỗ khác: phần mềm không mở, không ghi, không đổi tên gì ở đó, báo một câu tiếng Việt.
  - File nháp bị chương trình khác cài thêm bảng, trigger (đoạn lệnh tự chạy): phần mềm cất file sang một bên (giữ lại, **không xóa**), dùng file mới. Trigger không bao giờ được chạy.
  - File nháp do các bản trước tạo vẫn mở được như cũ, mọi dấu «đã gửi» còn nguyên.
- **Sửa thêm một chỗ có từ trước:** đúng lúc mở app mà file nháp đang bị chương trình khác khóa, phần mềm từng coi là hỏng. Trên Mac, Linux nó cất file sang một bên (mất khỏi app cả dấu «đã gửi»); trên Windows nó báo lỗi lạ. Nay chỉ báo «đang bận», file giữ nguyên.
- **Lỗi nhỏ SL-T131-1** (file lưu tạm kế hoạch gỡ lối tắt ở file phụ chậm một bước) đã sửa.
- Không đổi giao diện, không thêm thư viện.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/plan_cache.py` | **SL-T131-1:** `_prepare` gỡ liên kết ở chính file và ở tên file nhật ký **trước** `_is_healthy` (lần SQLite mở file đầu tiên), đúng thứ tự `site_index`, `search_cache` |
| `seo_app/storage/drafts.py` | **Phần 4** (yêu cầu 2, 4), chỉ phần mở kho, kiểm file (chi tiết ở bảng dưới). Không sửa khối SEO, không sửa hàm trạng thái gửi (`save`, `save_send_state`, `send_state_if_exists`, `save_plan_write`… giữ nguyên từng dòng, kể cả `BEGIN IMMEDIATE` chúng tự mở) |
| `seo_app/env_file.py` | Docstring `set_gsc_site_url`: nơi gọi phải kiểm bằng `parse_property` **trước** (Lá Chắn T-124, ghi nhận 1, điều kiện 4). Đã thử: `validate_gsc_site_url` cho qua `sc-domain:a..b`, `sc-domain:-a.com`; `parse_property` từ chối; `save_property` gọi đúng thứ tự |
| `tests/test_t131_kho_nhap.py` | Mới, 36 ca (mục Test) |
| `tests/test_soi_loi_t131.py` | Gỡ dấu `xfail` SL-T131-1 (bảng R5) |
| `tests/test_soi_loi_t117.py` | Gỡ dấu `xfail` tham số `[kho-nhap]` của SL-T117-1 (bảng R5) |
| `docs/team/reports/T-131-tho-may.md` | Mục này |

`drafts.py`, theo mẫu kho thẻ ảnh (cùng giữ dữ liệu người dùng: file lạ đổi tên sang một bên, không xóa) và `search_cache`:

| Lớp | Cách làm |
|---|---|
| `data/` là liên kết (SL-T117-1) | `_prepare` gọi `dir_has_link` đầu tiên, ở **mỗi** lần mở: `DraftError(MSG_DATA_DIR_LINK)`, không tạo thư mục, không mở SQLite, không đổi tên gì |
| Liên kết ở tên file nhật ký | `-journal`, `-wal`, `-shm` là liên kết (symlink, junction, reparse point, hard link) thì gỡ chính liên kết, ở mỗi lần mở, **trước** mọi lần SQLite mở file (bài học SL-T131-1) |
| Chỗ đặt file là liên kết | **Đổi tên** chính liên kết sang một bên (`drafts.hong-….sqlite`, `recovered_from`), không xóa, không mở; file nó trỏ tới không bị đụng. Khác các kho lưu tạm (xóa liên kết): kho nháp giữ nháp và dấu «đã gửi», tên đổi giữ lại lối vào dữ liệu đó, trang báo người dùng như file hỏng |
| So trọn `sqlite_master` | `_app_tables`: mọi dòng phải khớp đúng `_expected_schema` (dựng trong bộ nhớ bằng chính ba câu tạo bảng); bảng thiếu thì được (file cũ). Đọc thành byte (UTF-8 hỏng là «khác», LC-T122-1), đọc vào danh sách có `LIMIT` (dòng lặp, thừa dòng là «khác», LC-T070-1). Câu tạo bảng giữ đúng chữ: đối chiếu **cả 21 bản** `drafts.py` trong lịch sử git, chỉ có đúng 3 câu, chưa từng đổi |
| Kiểm trong cùng giao dịch với thao tác | `_connect` trả `_Checked`: mọi câu của thao tác trong **một** giao dịch, cấu trúc kiểm ngay sau `BEGIN`, trước câu đầu tiên của thao tác. Thao tác tự mở `BEGIN IMMEDIATE` (so rồi đặt) thì giữ nguyên; câu đầu là câu ghi thì `BEGIN IMMEDIATE`; câu đọc thì `BEGIN`. Cấu trúc khác: `DraftError` câu cố định, chưa đọc, chưa ghi gì; lần mở sau kiểm lại từ đầu, đổi tên file lạ |
| `trusted_schema = OFF`, trần số bước, trần độ dài | `_guard` trên **mọi** kết nối (kiểm, tạo bảng, thao tác). 50 triệu bước; độ dài 20 MB (gấp 4 lần `MAX_DRAFT_BYTES`, chưa từng đổi từ T-016) |
| Kiểm file (`_is_healthy`) | Cấu trúc trước mọi truy vấn khác; rồi `quick_check`; rồi đọc thử mọi ô (ô dài quá trần thì lạ, như kho thẻ ảnh T-074). **Chỉ** trả «lạ» khi chắc chắn; bận, khóa, không mở được, chỉ đọc, đầy ổ (`_KEEP_FILE_CODES`, như `site_index`) thì báo lỗi, **giữ file** |
| Tạo bảng (`_create_tables`) | Đủ bảng thì chỉ đọc, không xin quyền ghi. Thiếu bảng (file mới, file trước T-086, T-100) thì tạo trong giao dịch ghi, kiểm lại cấu trúc trong giao dịch đó |
| Đổi tên sang một bên (`_move_aside`) | Đổi tên cả file nhật ký đi kèm (như kho thẻ ảnh): nhật ký cũ để lại thì SQLite «khôi phục» vào file mới |

### Chỗ để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Cách đặt giao dịch có kiểm cấu trúc | Lớp bọc `_Checked` (mở giao dịch ở câu đầu tiên), không đổi chữ ký `_connect()` | `test_t092_nhap_bi_xoa.py` thay `store._connect` bằng hàm không nhận tham số; thêm tham số `write=` sẽ phải sửa test cũ (R5). Lớp bọc giữ nguyên cách khóa của T-089, T-092 (so rồi đặt giữ khóa ghi **trước** câu kiểm «nháp còn») |
| 2 | Chỗ đặt file là liên kết | Đổi tên, không xóa | Xem bảng trên. Câu báo «File nháp cũ bị hỏng nên đã được cất sang một bên…» ở `home.py`, `plan.py`, `write.py` không đổi (ngoài phạm vi) |
| 3 | Câu ghi đầu tiên | `BEGIN IMMEDIATE` từ đầu | Trước đây `BEGIN` hoãn ngay trước câu ghi đầu. Nay câu kiểm cấu trúc chạy trước câu ghi; mở hoãn thì một lần ghi chen giữa có thể làm thao tác báo «bận» ngay, không chờ. Khóa sớm hơn vài câu, cùng thời gian chờ 5 giây |
| 4 | Câu đọc | Mọi câu của một lần đọc nằm trong một giao dịch đọc | Trước đây mỗi câu tự mở, tự đóng; nay cùng một ảnh chụp file (`load` đọc độ dài rồi đọc nội dung cùng một lúc) |
| 5 | Ô `data` trong lần kiểm ô quá dài | Đọc thử cả ô `data` (tới 5 MB mỗi nháp) | `find_plan_draft` quét `data` mọi nháp: một ô quá dài làm việc mở bài từ kế hoạch kẹt mãi. Chỉ chạy ở lần mở đầu (và sau lỗi); đo ở mục Đo |
| 6 | `search_cache._KEEP_FILE_CODES` thêm 13 | Không làm | Không có trong tin giao (Soi Lỗi GN-3 đồng ý đề xuất; để phiếu gom kiểm file) |

### Gỡ dấu xfail (R5: chỉ xóa dấu, Chỉ Huy đã cho)

| File | Ca | Dấu đã xóa | Bằng chứng trước khi xóa |
|---|---|---|---|
| `tests/test_soi_loi_t131.py` | `test_sl_t131_1_wal_index_hard_link_is_never_written_through[plan-cache]`, `test_sl_t131_1_linked_journal_name_is_removed_before_sqlite_opens[plan-cache--journal]`, `[plan-cache--wal]`, `[plan-cache--shm]` | `marks=SL_T131_1` ở tham số `plan-cache` của `KINDS`, và hằng `SL_T131_1` (chỉ dùng cho dấu đó) | `4 failed, 21 passed`: cả 4 ca `[XPASS(strict)]` |
| `tests/test_soi_loi_t117.py` | `test_sl_t117_1_other_data_stores_never_write_through_link[kho-nhap]` | `marks=pytest.mark.xfail(…SL-T117-1…)` (dòng chú thích phía trên sửa theo) | `[XPASS(strict)]` |

Không đổi thân test, tham số hay kỳ vọng nào của test cũ. Không sửa `test_t092_nhap_bi_xoa.py` (xem chỗ để ngỏ 1).

### Test

`tests/test_t131_kho_nhap.py` (36 ca):

- **Không làm mất trạng thái gửi:**
  - file do bản T-016 (chỉ `drafts`), T-086 (thêm `send_states`), T-100 (đủ ba bảng) tạo bằng đúng câu của bản đó: mở được, không đổi tên, nháp và trạng thái gửi còn nguyên; bảng thiếu được tạo thêm đúng câu; so rồi đặt vẫn chạy;
  - kho mới (app chạy lại) đọc đúng trạng thái gửi và dòng mồ côi T-130;
  - nháp gần 5 MB mở được;
  - file đang bị khóa lúc mở lần đầu: «đang bận», không đổi tên, mở được sau đó.
- **Cấu trúc lạ:**
  - trigger xóa, sửa dấu «đã gửi», khung nhìn, bảng lạ, chỉ mục, `ANALYZE`: file đổi tên, trạng thái gửi trong file cũ còn nguyên (trigger không chạy);
  - câu tạo bảng khác (thêm cột, `WITHOUT ROWID`, `CHECK`, khác chữ): lạ;
  - UTF-8 hỏng trong `sqlite_master`: lạ;
  - file bị cài trigger khi app đang chạy: lần ghi kế bị chặn, chưa ghi gì; lần mở sau đổi tên;
  - khe giữa `_prepare` và thao tác (6 thao tác): bị bắt trong giao dịch, chưa đọc, chưa ghi gì.
- **Liên kết:**
  - `data/` là junction tới thư mục có file nháp hợp lệ: 7 thao tác đều báo câu cố định, **0** lần `sqlite3.connect`, thư mục đích nguyên từng byte;
  - chỗ đặt file là hard link, junction: đổi tên, file/thư mục đích nguyên vẹn, kho dùng file mới;
  - file WAL có `-shm` là hard link tới file ngoài: file ngoài nguyên vẹn;
  - tên `-journal`, `-wal`, `-shm` là junction: gỡ trước mọi lần SQLite mở file (đếm bằng bộ đếm `sqlite3.connect`);
  - `_move_aside` mang theo file nhật ký, không ghi đè tên đã có.
- **Lớp phòng sau:** kết nối thật có `trusted_schema = 0`, trần độ dài 20 MB; quá số bước, ô dài quá trần là lạ; chỗ đặt file là thư mục thì báo, không đổi tên.

**Đối chứng:** tạm đặt lại `drafts.py` của HEAD (bản `main`, trước lượt 2) rồi chạy `test_t131_kho_nhap.py` cùng ca SL-T117-1. Trả lại bản mới, mã băm SHA-256 khớp trước và sau.

- **30 hỏng, 9 qua.** 29 ca mới hỏng, cùng ca `[kho-nhap]`.
- **7 ca mới qua cả trên bản cũ**, đúng ý: đó là các ca canh **không làm mất dữ liệu**, phải qua ở cả hai bản. Gồm file nháp ba đời, mở lại giữ trạng thái gửi, nháp gần 5 MB, UTF-8 hỏng (bản cũ cũng cất file nhờ `quick_check`), chỗ đặt file là junction (bản cũ mở không được nên cũng cất).
- 2 ca còn lại là hai tham số kho lưu tạm của SL-T117-1.

```
# Windows 11, Python 3.12.15. Không chạy toàn bộ pytest.

$ uv run pytest <60 file: mọi file test nhắc DraftStore / drafts.sqlite / DEFAULT_DRAFTS_FILE /
#                 seo_app.storage (kho nháp, gửi nháp, T-086, T-089, T-092, T-130, kế hoạch,
#                 plan_cache, site_index, Soi Lỗi T-117, T-131, test mới)> -q -rfEX   # 11:26 → 12:25
4425 passed, 22 skipped, 1 xfailed in 3505.74s (0:58:25)
#   0 hỏng, 0 XPASS. 22 bỏ qua đều do Windows (symlink cần Developer Mode, quyền kiểu chmod).
#   1 xfail có từ trước (test_soi_loi_t107, ảnh HEIC).

$ uv run pytest <39 file thêm: mọi test quét cả gói (rglob/glob "*.py"), mọi nơi gọi env_file,
#                 set_gsc_site_url, save_property, plan_cache chưa có ở trên, test_app_pages> -q -rfEX
3502 passed, 9 skipped, 4 xfailed, 1 warning in 896.71s (0:14:56)        # 12:27 → 12:42
#   0 hỏng, 0 XPASS. 4 xfail có từ trước (test_soi_loi_t026, test_soi_loi_t028: lớp AI).

$ uv run pytest tests/test_t131_kho_nhap.py
36 passed

$ uv run ruff check .                     # toàn repo
All checks passed!
$ uv run ruff format --check <5 file mã, test đổi>
5 files already formatted
#   env_file.py lệch định dạng 4 dòng ở chữ ký def set_gsc_site_url: có từ trước (HEAD cũng
#   lệch đúng 4 dòng), mình chỉ sửa docstring.

# Quét bí mật: bản sao 7 file đổi ở thư mục nháp, PYTHONUTF8=1, detect-secrets --all-files
# (đứng trong thư mục quét): 1 báo nhầm có từ trước, env_file.py dòng 70
# PASSWORD_HASH_VAR = "APP_PASSWORD_HASH" (tên biến, không phải bí mật; diff mình bắt đầu ở
# dòng 458). Đối chứng: thêm file mồi có khóa giả vào cùng thư mục → bắt được. Đã xóa mồi.
```

### Đo

Kho nháp đầy dựng bằng script ở thư mục nháp, file trong thư mục tạm:

- 30 nháp, mỗi nháp 4,9 MB (sát `MAX_DRAFT_BYTES`);
- 230 dòng trạng thái gửi (30 của nháp còn, 200 dòng mồ côi T-130);
- file 147,3 MB.

Thời gian (mỗi thao tác chạy một lần sau khi kho đã mở):

| Thao tác | Thời gian |
|---|---|
| `list_drafts` | 5,2 ms |
| `load` một nháp 4,9 MB | 50,0 ms |
| `send_state_if_exists` | 3,1 ms |
| `save_send_state` so rồi đặt | 14,1 ms |
| `find_plan_draft` | 662 ms (có từ trước: quét `data` mọi nháp bằng `instr`) |
| `list_plan_writes` | 2,8 ms |
| `save` khi kho đầy (dọn bớt nháp cũ) | 110,8 ms |
| `_is_healthy` (kiểm file, chỉ ở lần mở đầu và sau lỗi), nhanh nhất trong 3 lần | **823,5 ms** mới, 424,5 ms bản cũ (nạp từ `git show HEAD`): thêm phần đọc thử mọi ô |

- **Số bước máy ảo nhiều nhất mỗi kết nối:** 6.500 (lúc lưu kèm dọn dòng mồ côi), bằng 0,013% trần 50 triệu.
- **Nháp thật** thường vài chục KB, nên kiểm file mất vài mili giây.

### Rủi ro và điểm cần chú ý

- **Hành vi đổi:**
  - file nháp có bảng, trigger, khung nhìn, chỉ mục lạ, hay bị `ANALYZE` (bảng `sqlite_stat1`) nay bị đổi tên sang một bên (trước đây vẫn dùng);
  - chỗ đặt file là liên kết nay bị đổi tên (trước đây đi theo liên kết).
  - App không bao giờ tạo những thứ đó; file nháp app tạo ở mọi bản đều khớp (có ca test cho cả ba đời).
- **Đổi tên sang một bên** (file lạ, liên kết) làm nháp, dấu «đã gửi» trong file đó biến khỏi app (vẫn nằm trong file đổi tên).
  - Tab đang mở bài sẽ gặp «nháp không còn» (T-092) và hỏi lưu lại; lưu lại thì nháp mới không có khóa gửi trùng.
  - Như file hỏng trước đây; chỉ xảy ra khi file bị chương trình khác sửa.
- **Lớp bọc `_Checked`** nhận diện câu ghi theo chữ đầu câu (`INSERT`, `DELETE`, `UPDATE`, `REPLACE`). Mọi câu của kho là hằng trong `drafts.py`; thêm loại câu ghi khác sau này thì phải thêm vào `_WRITE_HEADS`.
- **Symlink** ở `data/`, chính file, file nhật ký: máy này chưa bật Developer Mode nên thử bằng junction, hard link. Cần chạy lại trên Mac/Linux (như lượt 1).

### Đề xuất

- **Phiếu gom kiểm file 5 kho** (đã đề xuất ở lượt 1; nay thêm kho nháp): `_guard`, `_app_tables`, `_is_healthy`, `_is_link`, `_journal_paths` gần giống nhau ở `search_cache`, `plan_cache`, `site_index`, kho thẻ ảnh, kho nháp. Gộp kèm Soi Lỗi GN-1 (đầu file «phiên bản đọc» lớn hơn 2), GN-2, GN-3.
- **Câu báo khi đổi tên vì liên kết:** câu chung hiện nói «File nháp cũ bị hỏng…». Phiếu chữ sau có thể nói rõ hơn («là lối tắt nên đã được cất sang một bên»).

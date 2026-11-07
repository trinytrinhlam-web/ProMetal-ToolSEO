# Báo cáo T-131 · Dọn kho dữ liệu phụ: kiểm file và chặn `data/` là liên kết

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-131](../tickets/T-131-don-kho-du-lieu-phu.md) |
| Nhánh | `team/T-131`, từ `main` cục bộ `f6a6e64`; phần 1–3: mã và test `e53ee48`, báo cáo ở commit ngay sau |
| Ngày nộp | Phần 1–3: mã commit 2026-11-05, báo cáo 2026-11-07 (giờ máy, +07). Phần `drafts.py` và docstring `set_gsc_site_url` nộp sau, khi T-130 đã gộp |
| Kết quả | Hoàn thành một phần: `site_index`, `plan_cache` xong; `drafts.py` chờ T-130 |

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

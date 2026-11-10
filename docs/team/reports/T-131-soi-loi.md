# Báo cáo T-131 · Dọn kho dữ liệu phụ, phần 1–3 (`site_index`, `plan_cache`) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-131](../tickets/T-131-don-kho-du-lieu-phu.md), nhánh `team/T-131`: mã và test Thợ Máy `e53ee48`, báo cáo `f3e5c32` (gốc `main` `f6a6e64`). Chỉ phần 1–3; phần `drafts.py` (chờ T-130) không tính |
| Ngày nộp | 2026-11-10 (10:20 +07:00; soi từ 2026-11-07, chờ hạn mức). **Lượt 2** (kho nháp `drafts.py`, SL-T131-1): 2026-11-10, mục «Lượt 2» cuối báo cáo: **ĐẠT**, 0 lỗi mới, SL-T131-1 đóng |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (SL-T131-1). Cả bốn trọng tâm Chỉ Huy giao: `site_index` kiểm file đúng như `search_cache`; `data/` là liên kết thì không mở, không ghi, không xóa (đo: 0 lần `sqlite3.connect` vào thư mục đích có file cache thật); `plan_cache._is_healthy` coi lỗi giải mã và «unsupported file format» là file lạ; không lùi chức năng (bản gộp thử với `main`, 76 file test nơi gọi và quét cả gói: 7053 qua, 0 hỏng). **SL-T131-1:** `plan_cache` gỡ liên kết ở tên file nhật ký (`-journal`, `-wal`, `-shm`) **sau** bước kiểm file, mà bước này đã mở file bằng SQLite; `site_index`, `search_cache` gỡ **trước**. Thử thật: file ngoài dự án bị cắt và ghi đè; hay cache kế hoạch kẹt mãi. Sửa: đổi chỗ 3 dòng (bản sửa nháp: 4 ca `xfail` thành XPASS, mọi ca khác qua). Điều kiện: sửa SL-T131-1 cùng lượt phần 4 (`drafts.py`), trước Lá Chắn đầy đủ |

## Tóm tắt (cho chủ dự án)

- **Hai file lưu tạm (danh sách bài đã đăng, kế hoạch) nay được kiểm như file lưu tạm số liệu Google. Phần này đúng.**
  - Thư mục `data` là lối tắt trỏ ra chỗ khác: phần mềm không mở, không ghi, không xóa gì ở đó. Tôi thử cả khi chỗ lối tắt trỏ tới có sẵn file lưu tạm thật: phần mềm không chạm vào. Danh sách bài vừa tải vẫn dùng được, kèm một câu báo.
  - File lưu tạm bị chương trình khác cài thêm bảng, trigger, hay bị sửa tay hỏng: phần mềm bỏ file rồi tạo lại, không kẹt.
  - File lưu tạm cũ trên máy dùng tiếp được: cách tạo bảng giống hệt mọi bản trước.
- **Lỗi nhỏ (SL-T131-1):** với file lưu tạm kế hoạch, phần mềm gỡ «lối tắt» ở các file phụ đi kèm (file nhật ký) chậm một bước: mở file trước rồi mới gỡ.
  - Chỉ xảy ra khi có chương trình lạ cố tình đặt lối tắt đó trong thư mục `data` (phải chiếm máy trước).
  - Khi đó có thể làm hỏng một file khác trên máy, hoặc làm file lưu tạm kế hoạch không dùng được nữa. Trang Kế hoạch vẫn chạy, chỉ phải đọc lại Google Sheets mỗi lần.
  - File danh sách bài đang làm đúng thứ tự. Sửa file kế hoạch theo cách đó chỉ là đổi chỗ 3 dòng.
- **Không có việc gì cần chủ dự án quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t131.py` | Mới: **25 ca: 21 qua, 4 `xfail(strict=True)`** của SL-T131-1. Không gọi mạng; mọi file trong thư mục tạm; liên kết thật (junction trên Windows, symlink trên Mac/Linux, hard link) |
| `docs/team/reports/T-131-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác.

## 1. Bốn trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả |
|---|---|---|
| 1 | **`site_index`, `plan_cache` kiểm file đúng như `search_cache`** | `site_index`: **đúng** từng lớp (bảng ở mục 2). `plan_cache`: **đúng** hai việc phiếu đòi (`dir_has_link`, `_is_healthy`), **nhưng** vòng gỡ liên kết ở tên file nhật ký đặt sau bước kiểm file: **SL-T131-1**. Hai chỗ khác mẫu khác là chọn lựa đã nêu của Thợ Máy (GN-2, GN-3) |
| 2 | **`data/` là junction, symlink hay hard link thì không mở, không ghi, không xóa** | **Đúng.** <ul><li>Junction thật `du-an/data` → thư mục ở «ổ khác» có sẵn `site_index.sqlite`, `plan_cache.sqlite` **hợp lệ** (người dùng dời `data/` rồi đặt lối tắt). Gọi mọi hàm công khai của hai kho và `site_listing`: **0 lần** `sqlite3.connect` vào đó; tên, nội dung, giờ sửa của mọi file nguyên; `reset_count` 0; `save`, `clear` ra đúng câu cố định `MSG_DATA_DIR_LINK`; `get`, `refresh`, `site_listing` vẫn trả danh sách vừa tải kèm câu báo (`test_data_link_to_valid_caches_is_never_opened`).</li><li>Ca của Thợ Máy (junction ở `data/`, thư mục con của `data/`, lỗi quyền khi `lstat`, kiểm trước `mkdir`, trước xóa) qua.</li><li>Hard link: thư mục không có hard link (hệ điều hành không cho); hard link ở chính file: chỉ gỡ tên, không ghi xuyên (ca Thợ Máy qua).</li><li>Symlink: máy này không tạo được (chưa bật Developer Mode), 2 ca symlink của Thợ Máy bị bỏ qua. `data_dir` dùng chung `_is_link_stat` với lớp đọc ảnh (T-048, T-079), coi symlink là liên kết; nên chạy lại trên Mac/Linux.</li></ul> |
| 3 | **`plan_cache._is_healthy` coi lỗi giải mã và «unsupported file format» là file lạ** | **Đúng.** So bản cũ `f6a6e64` và bản mới trên cùng file (mục 3): bản cũ kẹt mãi (đọc ra `None`, mỗi lần ghi «Không mở được file lưu tạm kế hoạch…», file không bao giờ bị bỏ); bản mới bỏ file, lần ghi sau ghi được, đọc lại đúng. `site_index` cũng vậy. Tôi thêm 4 kiểu sửa tay khác cho cả hai kho (phiên bản ghi lạ, cỡ trang sai, file cụt, rác): không kẹt (`test_hand_edited_file_never_leaves_the_cache_stuck`, 12 ca). Còn một kiểu có từ trước, ở cả `search_cache`: GN-1 |
| 4 | **Không lùi chức năng: danh sách bài đã đăng, cache kế hoạch, mọi nơi gọi** | **Đúng.** <ul><li>Nơi gọi (`app/views/plan.py`, `write.py`, `home.py`, `seo_app/plan/sync.py`, `site_listing`) đều bắt `SiteIndexError`/`PlanCacheError` hay nhận `None`; không nơi nào gọi `clear()`.</li><li>Câu tạo bảng `site_index` giống hệt chữ ở cả 7 phiên bản trước (`0d0b9f4` T-037 → `bb3f51f`): file cũ khớp `_expected_schema`, dùng tiếp.</li><li>So bản cũ, bản mới 16 kiểu file × 2 kho: chỉ khác ở đúng chỗ phiếu muốn đổi (mục 3).</li><li>Test mọi nơi gọi và test quét cả gói trên **bản gộp thử** với `main` `e25afa1` (76 file): **7053 qua, 0 hỏng** (10 bỏ qua do Windows, 10 `xfail` có từ trước). Gộp thêm `main` mới `f084f5c` (T-125: trang Theo dõi cũng gọi hai kho; T-130: kho nháp): nơi gọi mới và test T-131 **415 qua, 0 hỏng** (mục 6).</li></ul> |

R5: `test_site_index.py::test_extra_table_does_not_break_cache` đổi thành `test_extra_table_drops_the_cache` (kỳ vọng ngược lại) là đúng: LC-T129-1 đòi bảng lạ là file lạ, như `search_cache`, `plan_cache`; ca mới còn chặt hơn (đếm `reset_count`, tải lại đúng 1 lần, lần sau đọc từ cache). `test_soi_loi_t117.py`: chỉ chuyển dấu `xfail` xuống riêng tham số `kho-nhap`, thân test và mã ca giữ nguyên; hai tham số đã sửa qua thật. Không ca nào bị làm yếu.

## 2. Đối chiếu với mẫu `search_cache`

| Lớp | `search_cache` (mẫu T-122, T-124) | `site_index` (T-131) | `plan_cache` (T-131) |
|---|---|---|---|
| `dir_has_link` trước mọi việc ở `_prepare`, `clear` | Có | Có | Có |
| Chính file là liên kết (symlink, junction, hard link): chỉ gỡ, trước khi mở | Có | Có | Có |
| Tên file nhật ký là liên kết: chỉ gỡ, **trước khi mở** | Có | Có | **Không: gỡ sau `_is_healthy` (SL-T131-1)** |
| So trọn `sqlite_master` trước khi mở và trong cùng giao dịch | Có | Có | Có (từ T-100) |
| `trusted_schema = OFF`, trần số bước, trần độ dài | Có | Có (50 triệu bước, 1 MB) | Có (từ T-100) |
| Đọc `sqlite_master` bằng bộ giải mã có bắt lỗi | Có (T-124) | Có | Có |
| `_is_healthy` chỉ giữ file khi lỗi do môi trường | `{3, 5, 6, 7, 8, 10, 14, 15}` | Thêm 13 (đầy ổ) | Thêm 13 (GN-3) |
| Tạo bảng trong một giao dịch ghi, kiểm lại trước khi tạo | Có | Có | Không: hai câu `CREATE TABLE IF NOT EXISTS` tự ghi từng câu (GN-2) |
| `save` gặp file lạ: bỏ rồi ghi lại một lần | Có | Có | Bỏ file, báo câu; lần ghi sau ghi được (chỉ gặp khi file bị thay giữa hai lần kiểm) |
| Trần cỡ file trước khi mở | Có (`MAX_FILE_BYTES`) | Không (phiếu không đòi) | Không (phiếu không đòi) |

## 3. So bản cũ (`f6a6e64`) và bản mới trên 16 kiểu file

File hợp lệ có dữ liệu, tạo bằng bản mới, rồi sửa theo từng kiểu. Mỗi bản: đọc, ghi dữ liệu đúng, đọc lại.

| Kiểu file | `site_index` cũ → mới | `plan_cache` cũ → mới |
|---|---|---|
| Nguyên vẹn; WAL; mã chữ lạ (byte 56 = 4) | Đọc được, như nhau | Như nhau |
| Bảng lạ, trigger, khung nhìn, chỉ mục lạ | Cũ đọc tiếp (bỏ qua phần lạ) → mới **bỏ file**, tải lại (đúng LC-T129-1) | Như nhau (đã bỏ từ T-100) |
| UTF-8 hỏng trong `sqlite_master` | Cũ **kẹt** (ghi: «Không mở được…» mãi) → mới bỏ file, ghi lại được | Như `site_index` |
| «Schema format» 5 (unsupported file format) | Cũ **kẹt** → mới bỏ file, ghi lại được | Như `site_index` |
| UTF-8 hỏng trong giá trị; phiên bản ghi 3; cỡ trang sai; file cụt; rác; file 0 byte | Bỏ file (hay tạo bảng), ghi lại được, như nhau | Như nhau |
| Phiên bản đọc 3 (byte 18) | Như nhau: đọc được, ghi báo lỗi mãi (GN-1) | Như nhau (GN-1) |

## 4. Lỗi mới

### SL-T131-1 · Thấp · `plan_cache` gỡ liên kết ở tên file nhật ký sau khi đã mở file

- **Ở đâu:** `seo_app/storage/plan_cache.py:257-262` (`_prepare`). Thứ tự hiện nay: chính file là liên kết hay file hỏng (`_is_healthy`, mở file bằng SQLite) → bỏ file; **sau đó** mới gỡ liên kết ở `-journal`, `-wal`, `-shm`. `site_index.py:346-363` và `search_cache._prepare` gỡ liên kết ở mọi tên **trước** khi `_is_healthy` mở file.
- **Đầu vào 1:** `data/plan_cache.sqlite` hợp lệ, ở chế độ WAL (byte 18–19 của đầu file = 2); tên `plan_cache.sqlite-shm` là hard link tới một file 68 KB ngoài dự án.
  - **Đã chạy:** `PlanCacheStore.load` (trang Kế hoạch, trang chủ gọi khi mở). `_is_healthy` mở file; SQLite mở `-shm` theo hard link, cắt file ngoài còn **32.768 byte** và ghi chỉ mục WAL vào đó. Vòng gỡ liên kết chạy sau, đã muộn.
  - **Đối chứng:** cùng đầu vào với `site_index`, `search_cache`: file ngoài nguyên 68 KB.
- **Đầu vào 2:** tên `plan_cache.sqlite-wal` hay `-shm` là junction (Mac/Linux: symlink), file ở chế độ WAL.
  - **Đã chạy:** SQLite không mở được tên đó, `_is_healthy` ném lỗi «không mở được» (mã 14, giữ file), `_prepare` dừng **trước** vòng gỡ. Mỗi lần đọc ra `None`, mỗi lần ghi báo «Không mở được file lưu tạm kế hoạch…», junction không bao giờ được gỡ.
  - **Đối chứng:** `site_index`, `search_cache` gỡ junction rồi đọc, ghi bình thường.
- **Đầu vào 3:** tên `-journal` là junction, file thường. `_is_healthy` vẫn mở file khi junction còn đó; vòng gỡ chạy sau nên lần này kho vẫn chạy được.
- **Hậu quả:**
  - Trái yêu cầu của chính phiếu: tên file nhật ký là liên kết thì chỉ gỡ, không đi theo.
  - Ghi xuyên ra file ngoài dự án (cắt, ghi đè), cùng loại F1 mà T-117, T-131 muốn đóng.
  - Hay cache kế hoạch kẹt: trang vẫn chạy, kế hoạch đọc thẳng từ Google, kèm câu báo mỗi lần.
- **Mức Thấp:** phải ghi được vào `data/` mới đặt được file WAL và liên kết (app không bao giờ tự bật WAL). Cùng lớp «phải chiếm máy trước» như SL-T117-1, LC-T116-1.
- **Vì sao test của Thợ Máy không bắt:** `test_hard_linked_journal_is_unlinked_not_followed` chỉ thử `-journal` của file thường; SQLite tự xóa nhật ký «không nóng» khi mở, nên bỏ vòng gỡ cũng ra cùng kết quả (đột biến M13 của Thợ Máy). Báo cáo Thợ Máy ghi chỗ này «chỉ thử được bằng symlink (Mac/Linux)». Thực ra trên Windows, junction hay `-shm` của file WAL làm lộ ngay (mục 5).
- **Gợi ý sửa:** đưa vòng gỡ liên kết ở tên file nhật ký lên trước `_is_healthy`, như `site_index._prepare`:

  ```python
  if _is_link(self.path):
      self._reset()  # chỉ xóa chính liên kết (F1)
  for path in _journal_paths(self.path):
      if _is_link(path):
          path.unlink()  # chỉ gỡ chính liên kết
  if self.path.exists() and not _is_healthy(self.path):
      self._reset()
  ```

  Phần 4 (`drafts.py`) nên theo đúng thứ tự này: gỡ liên kết ở chính file và mọi tên nhật ký trước mọi lần mở.
- **Test** (`tests/test_soi_loi_t131.py`, 4 ca `xfail(strict=True)`):
  - `test_sl_t131_1_wal_index_hard_link_is_never_written_through[plan-cache]`;
  - `test_sl_t131_1_linked_journal_name_is_removed_before_sqlite_opens[plan-cache--journal]`, `[plan-cache--wal]`, `[plan-cache--shm]`.
  - `--runxfail`: hỏng đúng chỗ (file ngoài bị đổi từ byte đầu; mở file khi tên nhật ký còn là liên kết).
  - Cùng ca cho `site-index` và `search-cache-mau` (mẫu đối chiếu): qua.
- **Bản sửa nháp** (worktree tạm, chỉ đổi chỗ như trên): 4 ca thành XPASS. `test_soi_loi_t131.py`, `test_t131_kho_du_lieu_phu.py`, `test_plan_cache.py`, `test_soi_loi_t117.py`: 115 qua, 2 bỏ qua (symlink), 1 `xfail` (kho nháp, SL-T117-1), 0 hỏng.

## 5. Thử đột biến (bổ sung cho mục đột biến của Thợ Máy)

Sửa cố ý một chỗ trên bản đã sửa SL-T131-1 (worktree tạm), chạy `test_t131_kho_du_lieu_phu.py` và `test_soi_loi_t131.py` với `--runxfail`, trả file về nguyên văn (so SHA-256). Đối chứng: không đột biến thì 87 qua, 2 bỏ qua.

| Mã | Đột biến | Test Thợ Máy | Test Soi Lỗi |
|---|---|---|---|
| MS1 | `site_index`: kiểm file trước, gỡ liên kết nhật ký sau (như `plan_cache` bản lỗi) | Sống | Bắt (`…[site-index]`, `…[site-index--journal]`) |
| MS2 | `plan_cache`: bỏ vòng gỡ liên kết nhật ký | Sống | Bắt (`…[plan-cache]`, `…[plan-cache--journal]`) |
| MS3 | `site_index`: bỏ vòng gỡ liên kết nhật ký (M13 của Thợ Máy) | Sống | Bắt (`…[site-index]`, `…[site-index--journal]`) |

## 6. Bằng chứng

```
# Windows 11, Python 3.12.15, SQLite 3.53.1, ruff 0.16.10. Không chạy toàn bộ pytest.

# 1) Test Soi Lỗi trên nhánh (team/T-131 + file test mới)
$ uv run pytest -q tests/test_soi_loi_t131.py -rxX
21 passed, 4 xfailed                       ← 4 xfail: SL-T131-1
$ uv run pytest -q tests/test_soi_loi_t131.py --runxfail -k "plan-cache and sl_t131"
4 failed                                   ← đúng chỗ (mục 4)

# 2) Bản sửa nháp SL-T131-1 (worktree tạm, gộp T-131 + main e25afa1)
4 XPASS(strict); 115 passed, 2 skipped, 1 xfailed (kho nháp)

# 3) Gộp thử T-131 + main e25afa1 (git merge-tree: không xung đột), worktree tạm tách rời,
#    seo_app nạp từ chính worktree tạm. 76 file: mọi file test nhắc site_index / SiteIndex /
#    plan_cache / PlanCache, mọi test quét cả gói (rglob, glob("*.py"), "seo_app" /), mọi test
#    data_dir và kho thẻ ảnh, test kế hoạch, test theo dõi, test Search Console, test T-131
7053 passed, 10 skipped, 10 xfailed in 3866.70s (1:04:26)
#    0 hỏng, không XPASS. 10 bỏ qua đều do Windows (symlink cần Developer Mode, quyền kiểu
#    chmod). 10 xfail đều có từ trước: SL-T070-4 (7), SL-T106-1 (2), SL-T117-1 [kho-nhap] (1).

$ uv run ruff check .                       # cây gộp
All checks passed!

# 4) Gộp thử lần hai với main mới f084f5c (đã có T-125: trang Theo dõi gọi cả SiteIndexStore,
#    PlanCacheStore, search_cache thêm stamp(); T-130: drafts.py, write.py): git merge-tree
#    không xung đột. Chạy lại phần nơi gọi mới và test T-131, chia 3 lượt:
$ pytest test_soi_loi_t131 test_t131_kho_du_lieu_phu test_search_cache test_tracking_refresh \
         test_t125_tho_may test_soi_loi_t117
349 passed, 4 skipped, 5 xfailed           ← 4 SL-T131-1, 1 SL-T117-1 [kho-nhap]; bỏ qua: symlink
$ pytest test_soi_loi_t125 test_t125_tracking_page test_t125_settings_search_console
47 passed
$ pytest test_app_pages
19 passed
$ uv run ruff check .                       # cây gộp
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t131.py
1 file already formatted

# 5) Ký tự ẩn, CR: 0 trong file test mới và báo cáo này.
# 6) Quét bí mật: bản sao file test mới và báo cáo này ở thư mục nháp, PYTHONUTF8=1,
#    detect-secrets --all-files (đứng trong thư mục quét): results {}.
#    Đối chứng: thêm file mồi có khóa giả (chữ tiếng Việt) vào cùng thư mục → bắt được
#    (Secret Keyword). Đã xóa mồi.
```

Script thăm dò (thư mục nháp của phiên Soi Lỗi): `probe_shm.py` (hard link ở `-shm`, `-wal`, `-journal`, 3 kho), `probe_junction_journal.py` (junction ở tên nhật ký, 3 kho), `probe_data_junction.py` (đếm `sqlite3.connect` khi `data/` là junction), `diff_old_new.py` (16 kiểu file × 2 kho × 2 bản), `probe_readonly_header.py` (GN-1, 3 kho), `fix_draft.py`, `mutate.py`.

## 7. Ghi nhận (không phải lỗi của phiếu, không chặn)

- **GN-1 (có từ trước, cả `search_cache`):** byte «phiên bản đọc» (byte 18 của đầu file) lớn hơn 2 thì SQLite mở file ở chế độ chỉ đọc.
  - Bước kiểm file qua, đọc vẫn ra dữ liệu cũ, nhưng mỗi lần ghi báo «Không mở được file lưu tạm…» (mã 8, coi là lỗi môi trường nên giữ file). Thử thật: `site_index`, `plan_cache`, `search_cache` đều vậy.
  - Trang vẫn chạy (tải lại từ website, Google mỗi lần cache cũ), nhưng cache không bao giờ cập nhật.
  - Câu «file bị sửa tay kiểu lạ không còn làm phần mềm báo «không mở được» mãi» trong báo cáo Thợ Máy đúng cho các kiểu phiếu nêu, chưa đúng cho kiểu này. Phải có chương trình lạ sửa đầu file.
  - Gợi ý: gộp vào phiếu dọn «gom kiểm file 5 kho» Thợ Máy đề xuất: coi byte 18 hay 19 lớn hơn 2 là file lạ.
- **GN-2 (Thợ Máy đã nêu, chỗ để ngỏ 5):** `plan_cache._prepare` tạo hai bảng bằng hai câu tự ghi từng câu, không trong một giao dịch ghi có kiểm lại như `search_cache`, `site_index`.
  - Khe (đọc mã, chưa thử): lần đầu tạo file, tab khác kiểm đúng lúc mới có một bảng thì `_is_healthy` trả `False` (coi là file lạ) và kho tìm cách bỏ file đang tạo.
  - Hậu quả nhỏ (lần đó không có cache hay báo lỗi một lần, lần sau tạo lại). Đồng ý giữ trong phiếu này; nên làm khi gom kiểm file.
- **GN-3:** `_KEEP_FILE_CODES` của hai kho có thêm 13 (đầy ổ) so với `search_cache` trên `main`. Lý do Thợ Máy nêu hợp lý (test T-042 ghim «đầy ổ không xóa file»). Đồng ý đề xuất thêm 13 cho `search_cache` để bốn kho giống nhau.
- **GN-4:** mục đột biến của báo cáo Thợ Máy ghi M13 «chỉ thử được bằng symlink (Mac/Linux)». Thực ra trên Windows thử được bằng junction hay `-shm` của file WAL; test mới bắt cả 3 đột biến cùng nhóm (mục 5).

## 8. Đề xuất cho Chỉ Huy

- Giao Thợ Máy sửa SL-T131-1 cùng lượt phần 4 (`drafts.py`), rồi gỡ 4 dấu `xfail` (R5: chỉ gỡ dấu, không đổi kỳ vọng). Khi làm kho nháp, thêm kho nháp vào `KINDS` của `test_soi_loi_t131.py`, hay viết ca tương đương.
- Lá Chắn đầy đủ sau phần 4: xem thêm GN-1.
- Chạy lại `test_t131_kho_du_lieu_phu.py`, `test_soi_loi_t131.py` trên Mac/Linux khi có máy (ca symlink bị bỏ qua trên máy này).

## Lượt 2 (2026-11-10): kho nháp `drafts.py`, SL-T131-1

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B (phiên khác lượt 1; phiên đã soi T-092, T-130) |
| Nhánh | `team/T-131` tại `147c9f1` (Thợ Máy lượt 2; đã gộp `main` `7153f0a` có T-130, T-132 ở `cd575a9`). Thử gộp với `main` cục bộ `03b5881`, rồi `d4a015e` (chỉ thêm phiếu, tài liệu): **không xung đột**, cây `cd4b38a`, `23554b7` |
| **Kết luận lượt 2** | **ĐẠT**: 0 lỗi mới. **SL-T131-1 đóng.** `drafts.py` chỉ đổi phần mở kho, kiểm file; trạng thái gửi và khối SEO không đổi dòng nào. Các ca liên kết, file lạ, file hỏng, file bận đúng như báo cáo Thợ Máy. Lớp bọc `_Checked` giữ nguyên so rồi đặt của T-089, T-092 (thêm ca hai kho chạy thật song song). Nháp cũ trước T-086, T-100 mở được. Không ca nào mất dấu «đã gửi» khỏi file. Thời gian kiểm file chấp nhận được. Cây gộp, 62 file mọi nơi gọi kho nháp và các kho lưu tạm: **4.381 qua, 0 hỏng**. 3 ghi nhận, không chặn |

### Tóm tắt (cho chủ dự án)

- **Kho nháp bài viết nay được kiểm kỹ như các file lưu tạm. Phần này đúng.**
  - Thư mục `data` là lối tắt: phần mềm không mở, không ghi gì ở đó.
  - File nháp bị chương trình khác sửa (cài trigger, bảng lạ) hay là lối tắt: phần mềm **cất sang một bên, không xóa**, rồi dùng file mới.
  - File nháp đang bị khóa lúc mở app: phần mềm chỉ báo «đang bận», file giữ nguyên (trước đây có thể bị cất đi cùng dấu «đã gửi»).
- **Dấu «đã gửi» chống gửi trùng không mất** trong mọi ca tôi thử: hai tab cùng gửi một bài, xóa nháp đúng lúc tab kia đang lưu, file nháp các bản cũ, file nháp bị chương trình khác chuyển chế độ lưu (WAL). File bị cất sang một bên vẫn giữ nguyên dấu đó bên trong.
- **Lỗi nhỏ lượt trước (SL-T131-1) đã sửa đúng.**
- **Tốc độ:** kho nháp bình thường (30 bài, mỗi bài khoảng 50 KB) kiểm mất khoảng 20 phần nghìn giây, gần như cũ. Chỉ kho cực lớn (gần 150 MB) mới mất khoảng 1 giây. Chấp nhận được.
- **Việc của bạn:** không có.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t131.py` | Thêm mục «lượt 2: kho nháp»: **4 ca, qua cả 4** (hai kho giành «đang gửi» cùng lúc; lưu so rồi đặt và xóa cùng lúc; file hợp lệ chế độ WAL sau `VACUUM`; chỗ đặt file là hard link: file cất đi còn dấu «đã gửi»). Không đổi ca nào của lượt 1. Cả file: 29 ca, qua cả 29 |
| `docs/team/reports/T-131-soi-loi.md` | Mục «Lượt 2» này |

Không sửa code ứng dụng, không sửa test của Thợ Máy, không commit file phiếu.

### 1. SL-T131-1 đóng

`plan_cache._prepare` (`seo_app/storage/plan_cache.py:249`) nay gỡ liên kết ở chính file và ở tên file nhật ký **trước** `_is_healthy`, đúng thứ tự `site_index`, `search_cache`. 4 ca SL-T131-1 của lượt 1 (gỡ dấu `xfail`) qua trên cây gộp (lô 1).

### 2. `drafts.py` chỉ đổi phần mở kho, kiểm file

Các khối đổi (`git diff cd575a9..147c9f1`): chú thích đầu file, `import`, hằng kiểm file, `_connect`, `_prepare`, `_move_aside`, các hàm mới sau `_check_images` (`_Checked`, `_journal_paths`, `_is_link`, `_remove_link`, `_guard`, `_expected_schema`, `_app_tables`, `_create_tables`, `_is_healthy`, `_is_busy`, `_code`, `_db_message`). **Không khối nào** chạm `save`, `delete`, `load_send_state`, `send_state_if_exists`, `save_send_state`, `_trim_orphan_send_states`, việc ghi Sheet còn nợ hay khối SEO. Ba câu tạo bảng chuyển vào `_CREATE_TABLES` giữ đúng từng chữ.

### 3. Các ca kiểm

36 ca của Thợ Máy (`tests/test_t131_kho_nhap.py`) qua trên cây gộp. Đối chiếu từng ca Chỉ Huy giao:

| Ca | Kết quả |
|---|---|
| `data/` là liên kết | `_prepare` gọi `dir_has_link` đầu tiên ở mọi lần mở: báo câu cố định, 0 lần `sqlite3.connect`, không đổi tên gì (ca Thợ Máy, ca SL-T117-1 `[kho-nhap]` gỡ dấu) |
| Tên file nhật ký là liên kết | Gỡ chính liên kết **trước** mọi lần SQLite mở file (ca đếm `sqlite3.connect` của Thợ Máy; `-shm` hard link ở chế độ WAL: file ngoài nguyên vẹn) |
| Chỗ đặt file là liên kết | **Đổi tên** chính liên kết sang một bên, không xóa, không đi theo. Ca thêm của tôi: hard link tới file nháp ngoài dự án có «đã gửi 501»: kho dùng file mới, file ngoài nguyên từng byte, file cất đi (đọc chỉ đọc) **còn dòng «đã gửi 501»** |
| File lạ, hỏng | Trigger, khung nhìn, bảng, chỉ mục lạ, `ANALYZE`, câu tạo bảng khác chữ, UTF-8 hỏng: đổi tên sang một bên, trigger không chạy (ca Thợ Máy). Đọc mã `_app_tables`: so trọn `sqlite_master` (loại, tên, bảng, câu lệnh) với lược đồ dựng bằng chính ba câu tạo bảng, kể cả chỉ mục tự sinh của khóa chính; bảng thiếu thì được; dòng thừa, lặp là «khác» |
| File bận lúc mở lần đầu | `_is_healthy` ném lại lỗi bận, khóa (`_KEEP_FILE_CODES`): báo «đang bận», không đổi tên; lần sau mở được, trạng thái gửi còn nguyên (ca Thợ Máy với `BEGIN EXCLUSIVE` của kết nối khác) |

### 4. Lớp bọc `_Checked` và so rồi đặt (T-089, T-092), kể cả hai tab

Đọc mã: tôi liệt kê câu SQL theo thứ tự trong cả 11 thao tác của kho. Thao tác nào đọc rồi mới ghi (`save` với `must_exist`, `save_send_state` và `save_plan_write` với `expected`) đều **tự mở `BEGIN IMMEDIATE` ở câu đầu**: `_Checked` chạy đúng câu đó, rồi kiểm cấu trúc trong giao dịch ấy, nên khóa ghi vẫn giữ **trước** câu kiểm «nháp còn», trạng thái cũ. Thao tác chỉ ghi: câu đầu là câu ghi, `_Checked` mở `BEGIN IMMEDIATE`. Thao tác chỉ đọc: `BEGIN`. Không thao tác nào đọc trong giao dịch hoãn rồi mới ghi (kiểu dễ bị SQLite trả «bận» ngay khi tab khác đang ghi), không câu `BEGIN` nào nằm giữa thao tác.

| Thử (ca mới của tôi, hai kho riêng như hai tab, hai luồng thật, 12 lần mỗi ca) | Kết quả |
|---|---|
| Hai kho cùng giành «đang gửi» một nháp (so rồi đặt với «chưa gửi») | Mỗi lần đúng một bên thắng, bên kia không ghi gì, không bên nào báo lỗi; kho mang đúng trạng thái bên thắng |
| Tab A xóa nháp «đã gửi 501» đúng lúc tab B tự lưu kiểu so rồi đặt | Mọi thứ tự: không có nháp tạo lại sau lần xóa; tab B (nếu thua) báo `DraftGoneError`; dòng «đã gửi 501» luôn còn (dòng mồ côi T-130) |

Các file T-089, T-092, T-130 (cả của Soi Lỗi, Lá Chắn) qua trên cây gộp (lô 1, 2).

### 5. Nháp cũ trước T-086, T-100

Ca của Thợ Máy dựng file đúng câu của bản T-016 (chỉ bảng `drafts`), T-086 (thêm `send_states`), T-100 (đủ ba bảng): mở được, không đổi tên, bảng thiếu được tạo thêm, nháp và trạng thái gửi còn nguyên; `test_drafts_images.py`, `test_t100_drafts_plan.py` (khuôn nháp 1, 2) qua. Ca thêm của tôi: file nháp app tạo, bị chương trình khác chuyển sang chế độ WAL và `VACUUM`: vẫn dùng được, không đổi tên, ghi tiếp được.

### 6. Không mất dấu «đã gửi»

Chỉ có hai đường xóa dòng trạng thái gửi, đều không đổi ở lượt này: lần gửi chưa tạo gì trả về «chưa gửi» (nháp còn), và dọn dòng mồ côi quá 200 (T-130). Các đường T-131 thêm: file bận thì giữ file; cấu trúc lạ phát hiện giữa thao tác thì cuộn lại, chưa ghi gì; file lạ hay chỗ đặt file là liên kết thì **đổi tên**, không xóa (dấu «đã gửi» còn trong file cất đi, ca của tôi ở mục 3). Riêng ca đổi tên: app không còn thấy dấu đó (xem G2).

### 7. Thời gian kiểm file lần đầu

Đo lại trên máy này (đang chạy song song việc khác), nhanh nhất trong 3 lần, kho có 230 dòng trạng thái gửi:

| Kho | Bản mới | Bản cũ (`cd575a9`) |
|---|---|---|
| Thực tế: 30 nháp × 50 KB (1,6 MB) | 19,7 ms | 16,4 ms |
| Lớn: 30 nháp × 1 MB (30 MB) | 305 ms | 138 ms |
| Trần: 30 nháp × 4,9 MB (147 MB) | 1.228 ms | 552 ms |

Bản mới chậm khoảng gấp đôi ở kho lớn vì đọc thử mọi ô; với kho thực tế chênh vài mili giây. **Chấp nhận được.** Lưu ý: trang Soạn bài dùng lại một kho cho cả phiên (`st.cache_resource`) nên chỉ kiểm lần đầu, còn trang Bài viết, Kế hoạch tạo kho mới mỗi lần gọi, nên bước kiểm chạy ở **mỗi lần vẽ** hai trang đó (G1).

### 8. R5

Chỉ xóa dấu `xfail`, đúng phần Chỉ Huy cho: 4 ca SL-T131-1 (`marks=SL_T131_1` và hằng `SL_T131_1`, `tests/test_soi_loi_t131.py`), ca `[kho-nhap]` của SL-T117-1 (`tests/test_soi_loi_t117.py`, kèm sửa dòng chú thích). Không đổi thân test, tham số hay kỳ vọng.

### 9. Gộp thử, chạy chọn lọc

Cây gộp `cd4b38a` (`main` `03b5881` + `147c9f1`), qua `run_list.sh` (kiểm danh sách, thiếu file thì dừng; dòng đầu mỗi lô đã xem), 6 lô nối tiếp, mỗi lúc một tiến trình. Danh sách: mọi file test nhắc `DraftStore`, `drafts.sqlite`, `DEFAULT_DRAFTS_FILE`, kho nháp (`ui.store()`, `draft_store`), cộng các kho lưu tạm (`plan_cache`, `site_index`, `search_cache`) và trang Kế hoạch, Theo dõi:

| Lô | Nội dung | Kết quả |
|---|---|---|
| 1 | T-131 (cả hai phần), kho nháp, T-092, T-130, SL-T117 (13 file) | 503 passed, 3 skipped |
| 2 | T-086, T-089, Soi Lỗi T-016–T-021 (8 file) | 267 passed, 6 skipped |
| 3 | Ảnh, chọn ảnh, gửi nháp kèm ảnh (10 file) | 1.769 passed, 11 skipped, 1 xfailed (SL-T107-3, có từ trước) |
| 4 | Bước SEO T-041 (6 file) | 351 passed |
| 5 | Xuất bản T-102, T-112, T-115, kế hoạch, trang Bài viết, Kế hoạch, T-127 (15 file) | 869 passed |
| 6 | Kho lưu tạm, khóa T-037, trang Theo dõi (10 file) | 622 passed, 2 skipped |

Cộng: **4.381 passed, 22 skipped, 1 xfailed, 0 failed, 0 XPASS**. Ca bỏ qua đều do Windows (symlink cần Developer Mode, quyền kiểu `chmod`). `main` `d4a015e` (mới nhất) so với `03b5881` chỉ thêm phiếu, ghi việc: không đổi file code, test nào, nên kết quả trên đúng cho cây gộp `23554b7`.

### 10. Đột biến (của tôi)

5 đột biến trong bản sao `seo_app/storage/drafts.py` (`147c9f1`; script `mutate131.py`), mỗi lượt chạy 40 ca (36 ca `test_t131_kho_nhap.py` của Thợ Máy, 4 ca lượt 2 của tôi), dừng ở ca hỏng đầu: **5/5 bị bắt**. Bản sao trả nguyên sau mỗi lượt (so với `git show 147c9f1`: khớp).

| Đột biến | Ca bắt đầu tiên |
|---|---|
| R1 `_Checked` mở `BEGIN` thường thay cho `BEGIN IMMEDIATE` của thao tác so rồi đặt | `test_soi_loi_t131.py::test_l2_hai_kho_gianh_dang_gui_cung_luc_chi_mot_thang` (của tôi) |
| R2 `_Checked` không kiểm cấu trúc trong giao dịch | `test_t131_kho_nhap.py::test_file_bi_cai_trigger_khi_dang_chay_thi_khong_ghi` |
| R3 file bận lúc kiểm bị coi là hỏng (đổi tên) | `test_t131_kho_nhap.py::test_file_ban_luc_kiem_khong_bi_doi_ten` |
| R4 chỗ đặt file là liên kết thì xóa liên kết thay vì đổi tên | `test_soi_loi_t131.py::test_l2_cho_dat_file_la_hard_link_file_cat_di_con_dau_da_gui` (của tôi) |
| R5 đổi tên sang một bên không mang theo file nhật ký | `test_t131_kho_nhap.py::test_doi_ten_sang_mot_ben_mang_theo_file_nhat_ky` |

### Lỗi mới

Không có.

### Ghi nhận (không tính lỗi, không chặn)

- **G1 · Trang Bài viết, Kế hoạch kiểm file nháp mỗi lần vẽ:** `app/views/home.py:49`, `app/views/plan.py:140` tạo `DraftStore` mới mỗi lần gọi (không `st.cache_resource` như trang Soạn bài), nên `_is_healthy` chạy ở mỗi lần vẽ hai trang đó: khoảng 20 ms với kho thực tế, tới khoảng 1,2 giây với kho cực lớn. Có từ trước T-131 (bản cũ: 16–550 ms). Đề xuất phiếu sau: dùng lại một kho như trang Soạn bài.
- **G2 · File bị cất sang một bên thì app không còn thấy dấu «đã gửi»:** khi file nháp lạ hay chỗ đặt file là liên kết, file bị đổi tên (giữ nguyên, có thể lấy lại bằng tay) nhưng tab đang mở bài sẽ gặp «nháp không còn» (T-092), lưu lại thì nháp mới không có khóa gửi trùng. Chỉ xảy ra khi chương trình khác sửa file; Thợ Máy đã nêu. Nếu muốn chặt hơn: phiếu sau có thể chép các dòng trạng thái gửi (đọc qua khuôn `SendState`) từ file cất đi sang file mới.
- **G3 · Ca symlink chưa chạy trên máy này** (Windows chưa bật Developer Mode): đã thử bằng junction, hard link. Cần chạy lại `test_t131_kho_nhap.py`, `test_soi_loi_t131.py` trên Mac/Linux khi có máy.

### Lệnh đã chạy (lượt 2)

- `pytest tests/test_soi_loi_t131.py -k l2` (cây nhánh): 4 passed. Cả file chạy trong lô 1 trên cây gộp: 29 passed.
- Đo `_is_healthy` (`probe_time.py`, nạp bản cũ từ `git show cd575a9:…`): mục 7.
- Cây gộp `cd4b38a`, 6 lô chọn lọc, 62 file: 4.381 passed, 22 skipped, 1 xfailed, 0 failed (mục 9).
- Đột biến: mục 10.
- `uv run ruff check .`: sạch.
- `detect-secrets` (`PYTHONUTF8=1`), quét bản sao trong thư mục ngoài git cùng file mồi tiếng Việt: sạch (chỉ file mồi bị báo; file test và báo cáo không có gì).
- Script: thư mục ghi chú chung `T-131-soi-loi-l2-scripts/` (`run_list.sh`, `mutate131.py`, `probe_time.py`).

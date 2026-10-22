# Báo cáo T-076 · Thư mục ảnh trả tên theo tên trên ổ (sau T-055)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-076](../tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) |
| Ngày nộp | 2026-10-21 (lượt 1) · 2026-10-22 (lượt 2, mục cuối) |
| Kết quả | Lượt 1: đủ yêu cầu 1–4, LC-T055-3 sửa được gọn, không cần ghi sổ rủi ro (mục 3). Lượt 2: sửa LC-T076-1 và LC-T076-2 (= SL-T076-1), gỡ 7 ca `xfail` (mục "Lượt 2") |

## Tóm tắt (cho chủ dự án)

Trước đây, nếu bài nháp ghi tên thư mục ảnh khác chữ hoa/thường với tên thật trên ổ (ví dụ nháp ghi `congai`, trên ổ là `CongAI`), có một cách mở thư mục làm app tưởng ảnh AI là **ảnh công trình thật**. Nay phần đọc thư mục ảnh luôn trả **đúng tên như trên ổ**, dù người dùng hay nháp gõ kiểu chữ nào. Ảnh trong thư mục `CongAI` luôn là ảnh AI, câu mô tả ảnh (alt) luôn có «Minh họa» và phải duyệt lại, kể cả khi mở thư mục theo đúng đường dẫn ghi trong nháp. Màn hình chọn ảnh (T-056) không còn phải mang ràng buộc "chỉ được đi từ thư mục gốc xuống".

Hai lỗi nhỏ đi kèm cũng đã sửa: thư mục bị đổi tên đúng lúc app đang kiểm thì app báo "chưa kiểm được", không còn lẫn sang một ảnh khác; thư mục ảnh có hơn 5.000 mục thì ảnh ở các thư mục bên trong **vẫn dùng được** (trước đây báo "chưa kiểm được").

Người dùng chưa thấy gì khác trên giao diện: chưa màn hình nào dùng phần này (T-056 sẽ dùng). Câu báo khi ảnh chưa kiểm được nay khuyên "mở lại từ thư mục ảnh gốc rồi chọn lại ảnh".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/folders.py` | Hàm mới `_disk_names` (`:548`): tên trên ổ của từng phần đường dẫn, rồi so định danh mục ở tên đó với mục vừa kiểm; `_listed_names` (`:582`, cách của Mac/Linux) và `_match_disk_name` (`:147`); cờ `_NAMES_FROM_RESOLVE` (`:71`), câu `_MSG_SLOW` (`:82`). `list_folder` (`:647`) và `stat_image` (`:718`) trả `ImageRef` theo tên trên ổ. `_checked_file` trả thêm thư mục gốc. Docstring module, `list_folder`, `stat_image` |
| `seo_app/storage/drafts.py` | `_check_images` dùng `entry.ref` của `stat_image` (`:915-935`); `_FolderNames` thành lớp phòng thứ hai, biết danh sách bị cắt (`:740-793`); `stat_image` lại khi đổi tên, so cỡ và giờ sửa (`:930`); `scanned` chỉ so trùng hẳn (`:894`); câu `_MSG_FOLDER_NAME` mới (`:109`); docstring module, `CheckedImage`, `check_draft_images` (điều kiện của `scanned`). Bỏ `_image_key`, `ref_key`, `replace` không còn dùng |
| `tests/test_images_folders.py` | 21 ca test mới (mục "tên trên ổ (T-076)", từ `:968`) |
| `tests/test_drafts_images.py` | Thêm 14 ca test (188 ca, trước 174); sửa 5 test cũ của chính Thợ Máy (T-055) và lớp giả `FakeDisk` theo nghĩa mới, xem mục 5 |
| `tests/test_soi_loi_t055.py` | Chỉ gỡ 3 khối `@pytest.mark.xfail(...)` (4 test: SL-T055-4 ×3, SL-T055-5): 12 dòng xóa, 0 dòng thêm; không đổi thân test, `assert`, `parametrize` |
| `docs/team/reports/T-076-tho-may.md` | Báo cáo này |

`git diff --stat d9e279f..HEAD`: đúng 5 file trên (+ báo cáo). Không sửa `app/**`, `config/**`, `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`. Không thêm thư viện.

## Cách sửa từng mục

### 1. LC-T055-1 · `list_folder`, `stat_image` trả `ImageRef` theo tên trên ổ

- **Windows:** tên lấy từ đường đã `resolve` mà `_resolve_inside` vốn có (Windows hỏi chính handle của mục, như phép chặn tên 8.3). Đã thử trên máy này: `resolve` của `ct012 - cỔNG/congai/cong.png` ra `CT012 - Cổng/CongAI/Cong.PNG`, cả tên file (script nháp, không commit).
- **Mac/Linux:** `resolve` giữ nguyên chữ đã gõ, nên `_listed_names` xác nhận từng tầng bằng tên trong thư mục cha: trùng hẳn thì dùng; không thì phải có **đúng một** tên trùng không phân biệt hoa thường và dạng Unicode (Mac lưu NFD), không có hay có hai thì báo lỗi. Thư mục cha mở từng tầng bằng `O_NOFOLLOW` như khi quét, chỉ đọc tên.
- Sau khi có tên trên ổ, `_disk_names` `lstat` lại mục ở tên đó và so định danh với mục vừa kiểm (`_same_file`); khác thì báo "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại." Tên trên ổ cũng phải qua `_is_safe_name` và giới hạn 1.024 ký tự như lúc quét.
- `list_folder(0, "…/congai")` nay trả `rel_dir`, `SubFolder.rel_path`, `ImageRef` đều theo `CongAI`; `stat_image(ImageRef(0, "…/congai/cong.png")).ref` là `…/CongAI/cong.png`. Ổ phân biệt hoa thường: tên khác là thư mục khác, như trước.
- **Lớp chặn T-048 giữ nguyên:** `_resolve_inside` (chặn `..`, symlink, junction, ẩn, ngoài gốc, tên 8.3) không đổi một dòng và vẫn chạy **trước** bước lấy tên; `_checked_file` giữ đủ phép kiểm (file thường, ẩn, cỡ), chỉ trả thêm thư mục gốc; `read_image_bytes` (`O_NOFOLLOW`, so inode, giới hạn cỡ) chỉ đổi dòng nhận kết quả của `_checked_file`; quét (`_Scan`, giữ thư mục) không đổi, chỉ nhận đường dẫn đã là tên trên ổ. Mọi test cũ của T-048 (Thợ Máy và Soi Lỗi) qua, không sửa test nào.
- `drafts.py`: `_check_images` lấy `ref = entry.ref` ngay sau `stat_image`, nên thẻ luôn đọc từ tên trên ổ.
- **Điều kiện của `scanned`** ghi trong docstring `check_draft_images`: `scanned` phải lấy từ `ImageLibrary.list_folder` (tên trên ổ) và **chỉ** dùng để bỏ bước đối chiếu tên thư mục cho ảnh mà `ImageRef` do `stat_image` trả trùng hẳn một `ImageRef` trong `scanned`. `scanned` không còn đổi ảnh được kiểm hay thẻ (trước đây ảnh "trùng không phân biệt hoa thường" với kết quả quét thì lấy luôn `ImageRef` của kết quả quét, trên ổ phân biệt hoa thường hay NTFS có cả "Tân Phú" NFC lẫn NFD là trỏ sang file khác). `ImageRef` dựng từ chữ trong nháp hay kết quả quét cũ chỉ là không trùng, ảnh vẫn được đối chiếu.
- `_MSG_FOLDER_NAME`: "…Hãy mở lại từ thư mục ảnh gốc rồi chọn lại ảnh."
- Test yêu cầu 1: `test_lc_t055_1_case_variant_stays_ai_whatever_scanned_is` (5 ca: không quét, `scanned` từ `list_folder` theo thư mục ghi trong nháp, `ImageRef` và `ImageEntry` dựng từ chữ trong nháp, quét từ gốc): ảnh AI, không mã công trình, alt bắt đầu «Minh họa », không còn "đã duyệt", chú thích có «Ảnh minh họa (AI)»; `test_lc_t055_1_folder_opened_by_draft_path_lists_disk_names` (mở thư mục theo đường dẫn trong nháp rồi chọn lại ảnh: `DraftImage.from_library` ra nguồn AI). Ở thư mục ảnh: `test_stat_image_returns_disk_names`, `test_list_folder_returns_disk_names`, `test_match_disk_name` (+2 test từ chối, dừng sớm), `test_entry_swapped_during_name_lookup_is_refused`.
- Mỗi test có tham số `name_source` chạy **cả hai cách** lấy tên trên mọi máy: cách của hệ điều hành đang chạy và cách của Mac/Linux (trên Windows đi qua `os.scandir` theo đường dẫn), nên phần Mac đã chạy thật trên NTFS ở đây; phần mở thư mục bằng `fd` chỉ chạy trên Mac/Linux (T-063).

### 2. LC-T055-2 · `stat_image` lại tên thật; danh sách bị cắt

- Lớp `_FolderNames` (đối chiếu tên thư mục với `list_folder`) **giữ lại làm lớp phòng thứ hai**, cho ổ trả lại đúng chữ đã gõ (xem "Rủi ro"). Nay nó nhận tên do `stat_image` trả (tên trên ổ), nên trên ổ thường luôn thấy tên trùng hẳn và không đổi gì.
- Danh sách cho tên khác (`real != ref`): gọi `library.stat_image(real)`; khác cỡ **hoặc** giờ sửa so với lần kiểm đầu thì ảnh không dùng được (`_MSG_FOLDER_NAME`); giống thì dùng `ref` và `entry` của **lần kiểm mới**, không còn ghép `ref` mới với số liệu cũ (`replace(entry, ref=real)` đã bỏ).
- Danh sách `truncated` mà chưa thấy tên trùng hẳn: **không** nhận tên chỉ trùng không phân biệt hoa thường (có thể là thư mục khác trên ổ phân biệt hoa thường), giữ tên của `stat_image`.
- Danh sách xem hết mà không có tên trùng hẳn và không có đúng một tên trùng không phân biệt hoa thường (thư mục vừa đổi tên, bị xóa, bị tráo junction): không dùng được, như T-055.
- Ở `folders.py` còn một lớp nữa cho cùng loại lỗi: tên trên ổ phải trỏ đúng mục vừa kiểm (mục 1).
- Test: `test_lc_t055_2_name_from_listing_must_be_the_checked_file` (khác cỡ, khác giờ sửa), `test_lc_t055_2_cut_listing_keeps_name_from_stat_image` (chưa thấy tên, chỉ thấy tên trùng không phân biệt hoa thường), `test_single_case_insensitive_match_takes_real_name` (kiểm `stat_image` được gọi lại đúng ở tên mới), `test_exact_folder_name_wins_on_case_sensitive_disk` (thêm ca danh sách bị cắt). 3 test SL-T055-4 của Soi Lỗi nay qua.

### 3. LC-T055-3 · thư mục cha hơn 5.000 mục

**Sửa được gọn, không cần ghi sổ rủi ro.**

- Windows: `stat_image` không xem thư mục cha (tên từ `resolve`).
- Mac/Linux: `_listed_names` không dùng ngân sách 5.000 mục của lần quét, chỉ giới hạn thời gian (`max_seconds`, mặc định 10 giây), dừng ngay khi thấy tên trùng hẳn.
- `drafts.py`: danh sách thư mục cha bị cắt thì giữ tên `stat_image` trả (mục 2), không báo "chưa kiểm được" nữa.
- Test: `test_lc_t055_3_image_under_crowded_root_is_still_checked` (ổ thật, gốc bị cắt: ảnh thật dùng được, CT012; ảnh `congai` vẫn là ảnh AI), `test_disk_names_are_not_limited_by_entry_budget` (cả hai cách lấy tên), `test_disk_name_lookup_has_time_limit`. Test SL-T055-5 của Soi Lỗi nay qua.

### 4. Gỡ `xfail` SL-T055-4, SL-T055-5

- Chạy trước khi gỡ: đúng 4 test báo `XPASS(strict)` (`test_sl_t055_4_real_name_must_point_to_the_checked_file` ×2, `test_sl_t055_4_folder_swapped_during_check_on_real_disk`, `test_sl_t055_5_plain_real_image_usable_when_parent_listing_is_cut`).
- Gỡ đúng 3 khối decorator (4 dòng mỗi khối); `git diff d9e279f -- tests/test_soi_loi_t055.py`: 12 dòng xóa, 0 dòng thêm. Câu `assert_ai_only_by_case` đặt sẵn trong test SL-T055-4 nay có hiệu lực (Soi Lỗi lượt 3 đã ghi).
- Ghi chú cho Soi Lỗi: `test_sl_t055_4_folder_swapped_during_check_on_real_disk` vẫn tráo thư mục ở lần `list_folder(0, "")` của lớp phòng thứ hai; nay lần kiểm lại bằng `stat_image` thấy khác cỡ (30 ≠ 16) nên báo không dùng được. Ca tráo **trong** `stat_image` có test riêng ở `folders.py` (`test_entry_swapped_during_name_lookup_is_refused`).

### 5. Test cũ của Thợ Máy đã đổi (không đụng test Soi Lỗi ngoài việc gỡ `xfail`)

| Test (T-055) | Vì sao đổi | Nay kiểm |
|---|---|---|
| `test_scanned_ref_becomes_the_key` → `test_ref_is_the_disk_name_with_or_without_scan` | `ref` nay là tên trên ổ cả tên file; `scanned` không còn đổi file | Có hay không có `scanned`: `ref` = `entry.ref` = tên trên ổ, thẻ CT012; ổ phân biệt hoa thường: không dùng được, không đổi sang file của kết quả quét |
| `test_scanned_refs_match_other_unicode_form` → `test_scanned_ref_never_switches_to_another_file` | Trước: nháp NFD được đổi sang file NFC của kết quả quét. Trên NTFS đó là **file khác** (hai tên khác nhau) | NTFS: không dùng được; Mac: cùng file, `ref` theo tên trên ổ. Thêm `test_scanned_sibling_with_other_unicode_form_is_not_used` (có cả hai thư mục NFC, NFD: dùng đúng file bên NFD) |
| `FakeDisk` (giả `stat_image`, `list_folder`) | Danh sách thật có `truncated`; cần giả cỡ, giờ sửa riêng | Thêm `truncated`, `files`, ghi lại các lần `stat_image` |
| `test_exact_folder_name_wins_on_case_sensitive_disk` | `FakeDisk` mới | Như cũ, thêm ca danh sách bị cắt |
| `test_single_case_insensitive_match_takes_real_name` | `FakeDisk` mới | Như cũ, thêm: `stat_image` được gọi lại đúng ở tên mới, `entry.ref` là tên mới (LC-T055-2) |
| `test_unconfirmed_folder_name_is_unavailable` | Ca "quét chưa tới" (danh sách bị cắt) nay **dùng được** (LC-T055-3) | Chỉ còn ca danh sách xem hết; kiểm thêm câu "mở lại từ thư mục ảnh gốc". Ca bị cắt chuyển sang `test_lc_t055_2_cut_listing_keeps_name_from_stat_image` |

### Thử đột biến (script nháp ngoài repo, không commit)

| Đột biến | Test bắt được |
|---|---|
| Bỏ so định danh ở tên trên ổ (`_same_file` luôn đúng) | 4 (`test_entry_swapped_during_name_lookup_is_refused`, cả 2 cách lấy tên × `stat_image`/`list_folder`) |
| `stat_image`, `list_folder` trả lại chữ đã gõ (như trước T-076) | 19 (12 ở thư mục ảnh, 7 ở nháp, gồm 3 ca `scanned` theo đường dẫn nháp của yêu cầu 1) |
| `_FolderNames` không xem `truncated` (như T-055) | 4 (2 test LC-T055-2 bị cắt, LC-T055-3, SL-T055-5 của Soi Lỗi) |

## Bằng chứng

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_app_pages.py tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py
1435 passed, 9 skipped, 7 xfailed in 206.97s (0:03:26)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/images/folders.py seo_app/storage/drafts.py tests/test_images_folders.py tests/test_drafts_images.py tests/test_soi_loi_t055.py docs/team/reports/T-076-tho-may.md
"results": {}   (0 phát hiện)
```

- 9 bỏ qua đều do máy Windows: symlink cần quyền (6), phần chỉ chạy trên Mac/Linux (3).
- 7 `xfail` có từ trước, không thuộc phiếu này: R2-1 ×2, R2-2 (T-048, `test_images_folders_soi_loi.py`), SL-T067-1 ×4 (T-067). Không còn `xfail` nào của SL-T055.
- Không có file `tests/test_soi_loi_t048*.py`; test Soi Lỗi của T-048 nằm ở `tests/test_images_folders_soi_loi.py` (đã chạy, không sửa). Thêm `test_images_process.py`, `test_soi_loi_t052.py`, `test_soi_loi_t067.py` vì có gọi `stat_image`/`list_folder`.
- Lượt chạy trước khi gỡ `xfail` và sửa test (4 file thư mục ảnh và nháp): 11 hỏng, gồm đúng 4 `XPASS(strict)` của SL-T055-4, -5 và 7 ca test cũ của Thợ Máy phải đổi theo nghĩa mới (mục 5); không test nào của Soi Lỗi hay T-048 hỏng.
- Kiểm lại ca tráo thư mục của Soi Lỗi bằng script nháp: lần `stat_image` đầu ra `Congai/cong.png` 16 byte, lần kiểm lại ra `CongAI/cong.png` 30 byte, ảnh không dùng được với câu "…Hãy mở lại từ thư mục ảnh gốc rồi chọn lại ảnh."

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1 (LC-T055-1): `folders.py:548`, `:647`, `:718`; docstring `scanned` và `_MSG_FOLDER_NAME` (`drafts.py:109`); test `test_lc_t055_1_case_variant_stays_ai_whatever_scanned_is` (5 ca)
- [x] Yêu cầu 2 (LC-T055-2): `drafts.py:784`, `:930`; test `test_lc_t055_2_*`
- [x] Yêu cầu 3 (LC-T055-3): sửa được, không cần sổ rủi ro; test `test_lc_t055_3_*`, `test_disk_names_are_not_limited_by_entry_budget`
- [x] Yêu cầu 4: gỡ 4 `xfail`, không đổi điều kiện kiểm
- [x] Giữ mọi lớp chặn T-048: `_resolve_inside`, `read_image_bytes`, `_Scan` không đổi; test T-048 qua không sửa
- [x] Test liên quan qua, `ruff check .` sạch (mục Bằng chứng)
- [x] Báo cáo này

## Rủi ro và điểm cần chú ý

- **Ổ trả lại đúng chữ đã gõ (suy luận, chưa thử được).** Trên Windows tên trên ổ lấy từ `resolve`; với NTFS, FAT, exFAT thì đúng (đã thử NTFS). Một số ổ mạng (SMB) hay ổ ảo có thể trả lại đúng chữ đã gõ thay vì tên thật. Khi đó: nháp vẫn được lớp phòng thứ hai bắt (đối chiếu với danh sách thư mục, tên do thư mục liệt kê ra là tên thật), trừ khi danh sách thư mục cha bị cắt (hơn 5.000 mục); còn `list_folder` theo đường dẫn gõ tay thì `rel_dir` có thể theo chữ đã gõ. Chưa thử được Google Drive for Desktop trên Windows (không muốn đụng Drive thật của chủ dự án). Nếu cần chắc: Windows có `FindFirstFileW` cho tên thật của từng tầng mà không phải xem cả thư mục (thêm vài chục dòng `ctypes`), hoặc T-056 vẫn ưu tiên đi từ gốc xuống.
- **Mac chậm hơn một chút.** Mỗi lần `stat_image` trên Mac/Linux đọc tên các thư mục trên đường đi tới ảnh (dừng ngay khi thấy tên trùng hẳn), kể cả thư mục chứa ảnh. `PreviewCache.get` (T-049) gọi `stat_image` cho mỗi ảnh xem trước. Đo trên NTFS máy này (script nháp, lấy lần nhanh nhất trong 3 lần, máy đang chạy song song agent khác): 48 lần `stat_image` rải trong thư mục 3.000 ảnh, gốc 201 thư mục: **0,39 giây** theo cách Mac/Linux, 0,13 giây theo cách Windows. Chưa đo trên Mac thật; T-063 nên đo với thư mục Drive thật.
- **Giới hạn thời gian mới trên Mac/Linux.** Đọc tên thư mục cha quá `max_seconds` (10 giây) thì `stat_image` báo "Ổ đĩa đang chậm nên chưa kiểm được tên thư mục, hãy thử lại." Trước T-076 `stat_image` không đọc thư mục nên không có câu báo này.
- **`checked.ref` đổi cả tên file theo ổ** (trước chỉ đổi tên thư mục). Thẻ sửa tay, khóa thẻ không phân biệt hoa thường nên không ảnh hưởng. `PreviewCache` dùng `ref` người gọi đưa vào làm khóa cache, nên hai cách viết của cùng một ảnh có thể tạo hai ảnh xem trước trong cache (chỉ tốn chỗ, không sai).
- **Đổi hành vi có chủ đích:** nháp ghi tên khác dạng Unicode (NFD) với tên trên NTFS (NFC) nay **không dùng được** trên Windows, thay vì lấy file NFC trong kết quả quét (mục 5). Nháp do app lưu luôn ghi đúng tên trên ổ, nên chỉ gặp khi nháp bị sửa tay.
- Gợi ý tùy chọn của Lá Chắn ("là ảnh AI nếu tên trong nháp **hoặc** tên trên ổ nói AI") chưa làm: không thuộc yêu cầu của phiếu; chỉ có tác dụng khi nháp sửa tay ghi tên AI mà tên trên ổ không phải.

## Đề xuất

- **T-056 (Họa Sĩ):** điều kiện 2a của Lá Chắn T-055 (chỉ đi từ gốc) không còn bắt buộc vì lý do LC-T055-1, nhưng vẫn nên ưu tiên đi từ gốc (xem rủi ro "ổ trả lại đúng chữ đã gõ"). Khi lưu lại ảnh còn dùng được, lưu theo `checked.ref` (tên trên ổ) để lần mở sau khỏi đối chiếu.
- **T-063:** chạy thêm trên Mac `tests/test_images_folders.py -k "disk_name or returns_disk or swapped_during_name or match_disk"` (phần mở thư mục bằng `fd` của `_listed_names` chỉ chạy trên Mac/Linux) và đo thời gian xem trước một thư mục lớn trong Drive.
- Soi Lỗi có thể thêm ca: tráo thư mục đúng giữa `_resolve_inside` và `_listed_names` trên ổ Mac thật; tên trên ổ dài hơn 255 ký tự khi đổi sang NFD.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-22): LC-T076-1, LC-T076-2

Theo biên bản Lá Chắn `docs/team/reports/T-076-la-chan.md` (điều kiện 1) và báo cáo Soi Lỗi `docs/team/reports/T-076-soi-loi.md` (SL-T076-1). Commit: `3930e94` (LC-T076-1), `491609b` (LC-T076-2).

### Tóm tắt (cho chủ dự án)

Lá Chắn thử trên ổ Google Drive for Desktop của máy này và thấy ổ Drive trả lại **đúng chữ đã gõ** khi app hỏi "tên thật của thư mục là gì", nên trên ổ Drive (chỗ chủ dự án để ảnh) lỗi cũ vẫn còn: ảnh AI có thể bị coi là ảnh công trình thật. Nay app hỏi tên ngay ở **thư mục chứa nó** (cách Windows liệt kê thư mục, đúng trên cả ổ Drive), nên trên ổ Drive, ổ C, D, USB đều ra tên thật: ảnh trong thư mục `CongAI` luôn là ảnh AI, alt có «Minh họa». Máy Windows không chậm hơn.

Lỗi nhỏ của Soi Lỗi cũng đã sửa: nếu đúng lúc app đang kiểm, thư mục ảnh AI bị đổi tên và một **bản sao y hệt** ở thư mục khác được đổi thành tên gần giống, app nay báo "chưa kiểm được, hãy mở lại từ thư mục ảnh gốc" thay vì dùng bản sao như ảnh thật.

Có **một chỗ Chỉ Huy cần biết** (mục "LC-T076-2"): cách sửa đúng chữ mà Soi Lỗi đề xuất buộc phải đổi điều kiện một test của Soi Lỗi ở T-055, trái lời giao. Tôi làm cách cho **cùng kết quả trên ổ thật** mà không phải đổi test đó.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `seo_app/images/folders.py` | Hàm mới `_win_listed_name` (hỏi thư mục cha một mục bằng `FindFirstFileW`) và `ImageLibrary._found_names` (từng tầng, cùng luật `_match_disk_name`); `_disk_names` bỏ nhánh lấy tên từ `resolve` và tham số `resolved`; `_kernel32` khai báo thêm `FindFirstFileW`, `FindClose`; mã lỗi `_ERROR_FILE_NOT_FOUND`, `_ERROR_PATH_NOT_FOUND`; sửa chú thích `_NAMES_FROM_RESOLVE` và docstring module, `_match_disk_name`, `_disk_names`, `list_folder`, `stat_image` |
| `seo_app/storage/drafts.py` | `_check_images`: trước khi nhận tên của danh sách thư mục, hỏi lại tên cũ bằng `stat_image`; docstring `_FolderNames`, `check_draft_images` |
| `tests/test_images_folders.py` | `name_source` thêm kiểu thứ ba "`resolve` trả chữ đã gõ" (`typed_resolve`, như của Lá Chắn), nên 4 test tên trên ổ chạy thêm kiểu này (5 ca); 3 test mới chỉ chạy trên Windows (6 ca): hỏi một mục mỗi tầng, tên 8.3 khi `resolve` trả chữ đã gõ, lỗi của `FindFirstFileW` |
| `tests/test_drafts_images.py` | Test mới `test_lc_t076_2_folder_renamed_between_checks_is_unavailable`; `test_single_case_insensitive_match_takes_real_name` (của tôi): thêm lần hỏi lại tên cũ vào danh sách lần gọi `stat_image` (mục LC-T076-2) |
| `tests/test_la_chan_t076.py` | Chỉ gỡ `xfail`: 5 dòng `@XFAIL` và hằng `XFAIL` (7 dòng); không đổi `assert`, dữ liệu thử |
| `tests/test_soi_loi_t076.py` | Chỉ gỡ khối `@pytest.mark.xfail(...)` của SL-T076-1 (4 dòng) |

Không sửa `app/**`, `config/**`, `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, không thêm thư viện. `_resolve_inside`, `_Scan`, `read_image_bytes` không đổi.

### LC-T076-1 · Windows lấy tên từ thư mục cha, không từ `resolve`

- **Cách làm:** cách (a) của Lá Chắn. Mỗi tầng hỏi thư mục cha đúng một mục bằng `FindFirstFileW` (`cFileName` là tên ổ liệt kê ra), tầng sau đi theo tên trên ổ của tầng trước; tên ổ trả về phải trùng hẳn, hoặc trùng không phân biệt hoa thường và dạng Unicode (cùng hàm `_match_disk_name` với cách của Mac/Linux). Hỏi không được (mục vừa mất, không có quyền đọc thư mục cha) thì báo lỗi gọn (`Không tìm thấy…`, `Không đọc được…`), **không quay về chữ đã gõ**. Giữ nguyên bước `lstat` ở tên mới và so định danh.
- **Thử trên máy này** (script nháp, thư mục tạm): thư mục thường: `congai` → `CongAI`, `CONGAI/cong.png` → `Cong.PNG`; thư mục bật phân biệt hoa thường (`fsutil`) có cả `CongAI` lẫn `congai`: mỗi tên ra đúng chính nó, `CONGAI`, `Congai` không tìm thấy; thư mục chỉ có `CongAI` (phân biệt hoa thường): `congai` không tìm thấy; "Tân Phú" NFC và NFD cạnh nhau: ra đúng từng cái; tên ngắn `THUMUC~1` → ổ trả tên dài (khác khóa, bị từ chối); tên có `[ ] ( ) { }` khớp đúng chữ. Lá Chắn đã đo trên ổ Drive thật: `FindFirstFileW` cho tên trên ổ 6/6. Tôi **không** thử trên ổ Drive của chủ dự án (không đụng Drive thật).
- **Vì sao không dùng nguyên cách của Mac (đọc cả thư mục cha bằng `os.scandir`) cho Windows:** đã thử (ép `_NAMES_FROM_RESOLVE = False` khi chạy test): 6 ca của Lá Chắn qua nhưng test T-048 `test_held_directory_and_parents_cannot_be_renamed_during_scan` hỏng. Test đó thử đổi tên thư mục ở lần `os.scandir` đầu tiên, mà lần đó nay là bước đọc tên thư mục cha (chưa "giữ" thư mục), nên đổi tên được. Muốn dùng cách này phải sửa test T-048. `FindFirstFileW` không gọi `os.scandir`, hỏi một mục mỗi tầng (không đọc cả thư mục 3.000 ảnh), nên test T-048 giữ nguyên.
- **Tên ngắn 8.3:** phép chặn 8.3 của `_resolve_inside` so với tên `resolve` trả, nên trên ổ trả lại chữ đã gõ nó không bắt được (Lá Chắn đã ghi). Nay bước lấy tên cũng chặn 8.3 riêng: ổ trả tên dài, khác khóa với tên ngắn (cách hỏi một mục), hoặc danh sách thư mục không có tên ngắn (cách của Mac/Linux). Test `test_short_8_3_name_refused_when_resolve_keeps_typed_text` (2 cách).
- **Hằng `_NAMES_FROM_RESOLVE`:** giữ tên (test T-076 của Soi Lỗi đặt hằng này để chạy cách của Mac/Linux; đổi tên thì test đó hỏng). Chú thích nay ghi đúng: `True` (Windows) là hỏi từng mục bằng `FindFirstFileW`, `False` là đọc thư mục cha; không chỗ nào lấy tên từ `resolve` nữa.
- **Test:** `name_source` (của tôi) thêm kiểu "`resolve` trả chữ đã gõ" (`typed_resolve` như của Lá Chắn): các test tên trên ổ, tráo thư mục, ngân sách chạy cả 3 kiểu. Thêm `test_windows_asks_the_parent_folder_one_entry_per_level` (hỏi đúng 3 lần cho 3 tầng, theo tên trên ổ của tầng trước; không `os.scandir`; `resolve` trả chữ đã gõ vẫn ra `CongAI/Cong.PNG`), `test_windows_lookup_failure_is_a_plain_message` (3 ca). 6 ca `xfail` LC-T076-1 của Lá Chắn nay qua, đã gỡ dấu.

### LC-T076-2 (= SL-T076-1) · không nhận bản sao ở tên khác

- **Vướng khi làm đúng chữ cách (a) của Soi Lỗi** ("danh sách xem hết mà không có đúng tên `stat_image` trả thì không dùng được; bỏ hẳn bước đổi tên"): test Soi Lỗi T-055 `test_mac_nfd_folder_names_keep_ai_and_real_tags` (`tests/test_soi_loi_t055.py`) giả một ổ mà `stat_image` **trả lại chữ đã gõ** và đòi ảnh "dùng được, ảnh AI, tên NFD" nhờ đổi sang tên của danh sách thư mục. Cách (a) đúng chữ làm test đó hỏng (Soi Lỗi đã ghi: "2 test … phải đổi theo"). Lời giao lượt 2 cấm đổi điều kiện kiểm của test nào, và phạm vi của tôi ở `tests/test_soi_loi_t055.py` chỉ là gỡ `xfail`.
- **Cách đã làm** (`drafts.py:930-944`): khi danh sách thư mục cho tên khác tên `stat_image` vừa trả, **hỏi lại tên cũ** bằng `stat_image`. Khác kết quả lần trước thì thư mục vừa đổi tên: ảnh không dùng được (`_MSG_FOLDER_NAME`), không hỏi tới ảnh ở tên mới. Chỉ khi hỏi lại vẫn ra đúng kết quả cũ (thư viện không cho biết tên trên ổ, như ổ giả trong test T-055) mới kiểm ảnh ở tên của danh sách như trước (cùng tên, cùng cỡ, cùng giờ sửa).
- **Với `ImageLibrary` thật, cách này cho đúng kết quả của cách (a):** từ lượt 2, tên `stat_image` trả và tên của danh sách thư mục đều do chính thư mục cha liệt kê ra. Hai tên chỉ khác nhau khi thư mục đổi tên giữa hai lần xem, và khi đó hỏi lại tên cũ thì ổ trả tên mới (ổ không phân biệt hoa thường) hoặc không tìm thấy (ổ phân biệt hoa thường), nên ảnh "không dùng được" (khe còn lại: xem "Rủi ro"). Ca SL-T076-1 trên ổ thật: lần hỏi lại ra `…/Congai/cong.png` (bản sao), khác `…/CongAI/cong.png` → không dùng được, thẻ theo tên đã kiểm (ảnh AI, alt «Minh họa»).
- **Nếu Chỉ Huy muốn đúng chữ cách (a):** thay nhánh đổi tên (vài dòng ở `drafts.py:938-944`) bằng câu báo `_MSG_FOLDER_NAME` và đổi 2 test dùng ổ giả "trả lại chữ đã gõ": `test_mac_nfd_folder_names_keep_ai_and_real_tags` (Soi Lỗi T-055) và `test_single_case_insensitive_match_takes_real_name` (của tôi), sang "không dùng được". Kết quả trên ổ thật không khác.
- **Test:** `test_sl_t076_1_swapped_copy_with_same_size_and_time_is_not_used` của Soi Lỗi nay qua, đã gỡ `xfail`. Thêm `test_lc_t076_2_folder_renamed_between_checks_is_unavailable` (hỏi lại tên cũ ra tên mới: không dùng được, không hỏi tới tên của danh sách, thẻ ảnh AI). `test_single_case_insensitive_match_takes_real_name` (của tôi, ổ giả trả lại chữ đã gõ): kết quả giữ nguyên (dùng tên của danh sách, ảnh AI), danh sách lần gọi `stat_image` thêm một lần hỏi lại tên cũ: `["congai/cong.png", "congai/cong.png", "CongAI/cong.png"]`.

### Thử đột biến (lượt 2; plugin, bản sao code ở thư mục nháp, không commit)

| Đột biến | Test hỏng |
|---|---|
| Windows lấy tên theo chữ đã gõ (như lượt 1 trên ổ Drive) | 34 (11 thư mục ảnh của tôi, 7 nháp của tôi, 9 Soi Lỗi T-076, 7 Lá Chắn T-076). Trong đó có SL-T076-1: bước hỏi lại tên cũ của LC-T076-2 chỉ có tác dụng khi `stat_image` cho tên trên ổ, nên hai cách sửa phải đi cùng nhau |
| Cách hỏi một mục không so khóa tên (nhận cả tên dài khi gõ tên 8.3) | 1 (`test_short_8_3_name_refused_when_resolve_keeps_typed_text`) |
| Bỏ bước hỏi lại tên cũ (bản sao code, đã kiểm `seo_app` nạp từ bản sao) | 3 (SL-T076-1 của Soi Lỗi, 2 test nháp của tôi) |

### Bằng chứng (lượt 2)

```
$ uv run pytest tests/test_images_folders.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_app_pages.py tests/test_images_folders_soi_loi.py tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py
1503 passed, 9 skipped, 7 xfailed in 166.91s (0:02:46)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/images/folders.py seo_app/storage/drafts.py tests/test_images_folders.py tests/test_drafts_images.py tests/test_la_chan_t076.py tests/test_soi_loi_t076.py docs/team/reports/T-076-tho-may.md
"results": {}   (0 phát hiện)
```

- 12 file: 8 file của lời giao lượt 2, thêm 4 file đã chạy ở lượt 1 (`test_images_folders_soi_loi.py` là test Soi Lỗi của T-048; `test_images_process.py`, `test_soi_loi_t052.py`, `test_soi_loi_t067.py` có gọi `stat_image`/`list_folder`). 0 hỏng.
- 9 bỏ qua đều do máy Windows: symlink cần quyền (6), phần chỉ chạy trên Mac/Linux (3), như lượt 1. 7 `xfail` có từ trước, không thuộc phiếu: R2-1 ×2, R2-2 (T-048), SL-T067-1 ×4 (T-067). Không còn `xfail` nào của T-076 (LC-T076-1 ×6, SL-T076-1 nay qua).
- Số khớp với lượt chạy của Lá Chắn trên cùng nhánh (1.480 qua, 8 `xfail`, không có `tests/test_la_chan_t076.py`): thêm 10 ca của Lá Chắn (6 ca trước là `xfail`), SL-T076-1 từ `xfail` thành qua, 12 ca mới của tôi (5 ca kiểu "`resolve` trả chữ đã gõ", 6 ca chỉ Windows, 1 ca LC-T076-2): 1.480 + 10 + 1 + 12 = 1.503.
- Trước khi gỡ `xfail`: đúng 6 ca LC-T076-1 và 1 ca SL-T076-1 báo `XPASS(strict)`; ngoài ra chỉ `test_single_case_insensitive_match_takes_real_name` (của tôi) hỏng vì thêm một lần gọi `stat_image` (mục LC-T076-2).

### Đo thời gian (Windows, ổ NTFS máy này)

Script nháp `perf_l2.py`: gốc 201 thư mục, thư mục chứa ảnh 3.000 ảnh; 48 lần `stat_image` rải khắp thư mục (như một trang xem trước); lấy lần nhanh nhất trong 3 lần.

| Cách lấy tên | Tên đúng như trên ổ | Gõ khác hoa thường |
|---|---|---|
| Lượt 2, Windows (`FindFirstFileW` từng tầng) | 0,139 giây | 0,135 giây |
| Lượt 1 (`resolve`, sai trên ổ Drive) | 0,129 giây | 0,137 giây |
| Đọc thư mục cha (cách của Mac/Linux) | 0,288 giây | 0,516 giây |

Cách mới trên Windows nhanh ngang lượt 1 và không phụ thuộc số ảnh trong thư mục (mỗi tầng một lần hỏi). Chưa đo trên ổ Drive thật.

### Đối chiếu lời giao lượt 2

- [x] LC-T076-1 (bắt buộc): Windows lấy tên từ thư mục cha (`FindFirstFileW` từng tầng), không từ `resolve`; sửa chú thích, docstring; thêm kiểu ổ "`resolve` trả chữ đã gõ" vào test; gỡ `@XFAIL` ở `tests/test_la_chan_t076.py` (6 ca qua)
- [x] LC-T076-2 (nên làm cùng): SL-T076-1 đóng, gỡ `xfail`; cách làm cho cùng kết quả cách (a) trên ổ thật, không đổi test Soi Lỗi T-055 (xem mục LC-T076-2, Chỉ Huy quyết nếu muốn đúng chữ (a))
- [x] Giữ mọi lớp chặn T-048 (`_resolve_inside`, `_Scan`, `read_image_bytes` không đổi; test T-048 qua, không sửa); không đổi `assert` của test Soi Lỗi, Lá Chắn (chỉ gỡ `xfail`); chỉ sửa file trong phạm vi phiếu
- [x] Test liên quan qua, `ruff check .` sạch

### Rủi ro và điểm cần chú ý (lượt 2)

- **Ổ ảo lạ:** cách hỏi một mục tin tên mà ổ trả cho truy vấn `FindFirstFileW`. NTFS, ổ chia sẻ Windows, ổ Google Drive for Desktop (Lá Chắn đo) trả tên đã lưu. Một ổ ảo tự viết (WinFsp, Dokan) về lý thuyết có thể trả lại chữ của truy vấn; khi đó lớp phòng thứ hai của nháp vẫn đối chiếu với danh sách thư mục (đọc cả thư mục, ổ không có chữ đã gõ để trả lại), trừ khi danh sách thư mục cha bị cắt.
- **Khe còn lại của LC-T076-2 (suy luận, chưa thử):** nếu hai thư mục bị đổi tên qua lại nhiều lần, mỗi lần đúng vào khe giữa các lần hỏi (vài mili giây), và có bản sao cùng cỡ, cùng giờ sửa, lớp phòng thứ hai về lý thuyết vẫn có thể nhận tên của danh sách. Hẹp hơn SL-T076-1 nhiều (SL-T076-1 chỉ cần một lần tráo); không đọc được gì ngoài thư mục ảnh (F1 giữ).
- **Tên hằng `_NAMES_FROM_RESOLVE`** nay không đúng nghĩa (giữ vì test Soi Lỗi đặt nó); chú thích đã ghi rõ. Khi Soi Lỗi sửa test T-076 lần sau có thể đổi tên hằng.
- **T-056, điều kiện 2a của Lá Chắn T-055:** Lá Chắn T-076 ghi 2a hạ xuống khuyến nghị khi LC-T076-1 sửa xong và T-063 qua; Lá Chắn T-076 lượt 2 xác nhận.
- Mac/Linux không đổi so với lượt 1 (vẫn đọc thư mục cha); phần mở bằng `fd` vẫn chờ T-063.

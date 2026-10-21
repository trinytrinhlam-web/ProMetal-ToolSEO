# Báo cáo T-076 · Thư mục ảnh trả tên theo tên trên ổ (sau T-055)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-076](../tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành: đủ yêu cầu 1–4. LC-T055-3 sửa được gọn, không cần ghi sổ rủi ro (xem mục 3) |

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

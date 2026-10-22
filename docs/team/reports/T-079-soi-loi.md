# Báo cáo T-079 · Đọc ảnh bằng thư mục đã mở từng tầng (vá SL-T063-2) · Soi Lỗi (phần Windows)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus (phiên bắt đầu ở 5.5, kết ở 4.8) |
| Phiếu | [T-079](../tickets/T-079-doc-anh-bang-fd-tung-tang.md) |
| Ngày nộp | 2026-10-22 |
| Máy kiểm | **Windows 11 Pro 10.0.26300**, Python 3.12.15 (uv 0.13.4), người dùng thường (không admin). Máy đang chạy song song agent khác. Ổ thử: NTFS cục bộ, ổ chia sẻ `\\localhost\C$`, ổ Google Drive for Desktop H:/I: (chỉ đọc thuộc tính). Mức kiểm **đầy đủ**, phần **Windows** |
| Mã nguồn | Nhánh `team/T-079` tại `c7b2394` (gốc `main` `fa2cc39`). Thêm `tests/test_soi_loi_t079.py` |
| Kết quả | Hoàn thành phần Windows. **Kết luận Windows: ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao trên Windows, 0 Trung bình, **1 Thấp mới: SL-T079-1**). Chuyển Lá Chắn được. Phần Linux (nơi SL-T063-2 là **Cao**) do một phiên cloud Linux riêng chạy — **chưa có ở báo cáo này** |

## Tóm tắt (cho chủ dự án)

Lỗ hổng chính Soi Lỗi T-063 tìm ra trên Linux (một chương trình lạ trên máy tráo thư mục con thành "lối tắt" đúng lúc app đọc ảnh thì app đọc nhầm một file nằm ngoài thư mục ảnh) **đã được vá**, cho cả Windows lẫn Mac/Linux (tôi đọc kỹ phần Mac/Linux dù máy này không chạy được). Tôi dựng lại đúng cách tấn công của Lá Chắn T-063 trên máy Windows này, nhiều luồng, hàng nghìn lần đọc: **không lần nào app đọc được nội dung hay cỡ của file ngoài thư mục ảnh**. Các bước kiểm mới (hỏi lại "anh đang thật sự nằm ở đâu", đi từng bước vào đúng thư mục đã kiểm) đều vững khi tôi tắt từng lớp để thử. Đọc ảnh bình thường không chậm đi, ổ Google Drive của máy vẫn đọc được thông tin ảnh như trước (tôi chỉ đọc thông tin, không mở nội dung, không ghi tên file nào ra).

Tôi tìm được **một lỗ hổng nhỏ mới (SL-T079-1, mức Thấp)** nằm ngay trong cách vá của Windows: cách app đối chiếu "đường dẫn thật" bỏ qua một số khác biệt rất nhỏ trong tên thư mục (chữ có dấu gõ theo hai cách, chữ hoa/thường ở một số ổ, vài chữ Latin đặc biệt). Nếu kẻ tấn công đặt được một thư mục "anh em" cạnh thư mục ảnh có tên **trông y hệt** nhưng khác ở những chỗ đó, rồi **thắng được cuộc đua tráo**, thì vẫn đọc được file bên ngoài. Trên Windows cuộc đua này **gần như không thắng được trên thực tế** (như chính lỗ hổng gốc, biên bản Lá Chắn T-063), nên nguy cơ thật là Thấp; nhưng nó cho thấy phần vá cho Windows **vẫn còn dựa vào may mắn của hệ điều hành** ở trường hợp "thư mục anh em trông giống nhau", đúng điều phiếu muốn tránh. Cách sửa nhỏ (đối chiếu tên y như hệ điều hành); tôi đã thử trên bản sao code: đóng được lỗ này, không hỏng test nào khác. Lá Chắn xếp mức cuối và quyết sửa ngay hay ghi sổ.

Phần code chạy trên Mac/Linux (nơi lỗ hổng gốc ở mức **Cao**) tôi **chưa chạy được ở máy này**; cần phiên cloud Linux chạy như lần T-063.

## Phạm vi đã kiểm và cách kiểm

Diff `git diff fa2cc39..team/T-079`: `seo_app/images/folders.py` (+209/−39), `seo_app/storage/drafts.py` (+18/−... phần LC-T076-3), 6 file test (3 chỉ gỡ `xfail`). Tôi:

1. Đọc toàn bộ diff và so **thân từng hàm** (AST, bỏ docstring) giữa `main` `fa2cc39` và `team/T-079` (`sl79_ast_same.py`).
2. Dựng lại cách tráo thật của Lá Chắn T-063 (thư mục con ↔ junction trỏ ra ngoài, **tiến trình riêng**, nhiều luồng) và phép **ép "luôn thắng"**; đếm lọt nội dung, cỡ, tên.
3. Thử đột biến 17 kiểu: tắt từng lớp chặn mới, xem test nào bắt.
4. Đo tốc độ trước/sau trên thư mục 300 ảnh (cục bộ và SMB).
5. Ổ Google Drive thật: chỉ đọc thuộc tính, chỉ in Đúng/Sai, không in tên, không mở nội dung.
6. Soát 3 file chỉ gỡ `xfail`; thêm `tests/test_soi_loi_t079.py`.

## Xác nhận từng lỗi đã sửa

### SL-T063-2, -3 (đọc / lộ cỡ file ngoài gốc khi tráo thư mục)

**Cách vá đúng hướng.** Lớp mới không đi theo chuỗi đường dẫn:

- **Mac/Linux** (`_open_image`, `_opened_stat`, nhánh `_OPEN_BY_DIR_FD`): `_posix_open_dir(gốc, parts[:-1])` mở thư mục cha **từng tầng** bằng `openat(O_DIRECTORY | O_NOFOLLOW)` rồi `os.open(tên, O_NOFOLLOW…, dir_fd=)` / `os.stat(tên, dir_fd=, follow_symlinks=False)`. Không tầng nào đi xuyên liên kết. Tôi đọc kỹ (máy này không chạy được): hàm `_posix_open_dir` đóng fd cũ sau mỗi tầng, lỗi đổi qua `_open_error`. **Chờ phiên cloud Linux chạy thật** (5 ca `posix_only` trong file của tôi + các ca của Thợ Máy).
- **Windows** (đọc): `os.open(path)` như cũ rồi `_win_handle_at` — `GetFinalPathNameByHandleW` hỏi **đường dẫn thật của chính handle vừa mở**, phải khớp `gốc/parts`. `stat`: `_win_open(path, FILE_READ_ATTRIBUTES)` (handle chỉ hỏi thuộc tính, như `os.lstat`, Drive không tải file về) + `_win_handle_at` + `_win_handle_is_link` + `os.fstat`.
- Sau đó: so định danh với mục vừa kiểm (`_resolve_inside`), kiểm file thường, không ẩn, không quá cỡ. Số liệu (cỡ, giờ sửa, `file_id`) lấy **từ mục đã mở**, không từ `lstat` theo tên.

**Thử trên Windows (tráo thật, tiến trình riêng, nhiều luồng):** đổi tên thư mục `x` ↔ junction trỏ ra `ngoai`, 2 tiến trình kẻ tấn công, 3 luồng app, 2 lượt 30 giây (một lượt thêm độ trễ nới rộng khe như máy bận):

| Lượt | Code | Vòng read+stat+list+tree | **Lọt nội dung** | **Lọt cỡ** | **Lọt tên** | Lộ đường dẫn / xích lỗi / lỗi lạ |
|---|---|---|---|---|---|---|
| rename, 2 kẻ, 3 luồng, 30s | T-079 | 2.478 | **0** | **0** | **0** | 0 / 0 / 0 |
| rename, 2 kẻ, 3 luồng, 30s, nới khe | T-079 | 2.795 | **0** | **0** | **0** | 0 / 0 / 0 |
| rename, 2 kẻ, 3 luồng, 30s, nới khe | main | 2.307 | **0** | **0** | **0** | 0 / 0 / 0 |

Hơn **5.000** lần đọc/stat của T-079 trong lúc bị tấn công: **0 lọt nội dung, 0 lọt cỡ, 0 lọt tên** (khớp Lá Chắn T-063: 0/>15.000, T-048: 0/11.192). Mọi câu báo là `ImageFolderError` cố định, không đường dẫn tuyệt đối, không xích lỗi hệ điều hành. Phân bố lỗi ("Không tìm thấy", "liên kết tắt", "nằm ngoài thư mục ảnh", "vừa bị thay đổi") cho thấy tráo có kích hoạt thật.

**Đối chứng dương (harness có bắt được lọt thật không):** đặt/gỡ junction **tại chỗ** trên `x` rỗng (= LC-T048-2 / R2-1), 4 luồng, 20 giây:

| Code | Tráo | Vòng | Lọt nội dung | Lọt cỡ | **Lọt TÊN** |
|---|---|---|---|---|---|
| T-079 | 62.643 | 22.047 | 0 | 0 | **973** (299 xem `x` + 674 quét cả cây) |
| main | 63.882 | 22.101 | 0 | 0 | **1.050** (325 + 725) |

Đây đúng là **LC-T048-2** (lọt **tên**, không nội dung, mức Thấp, đã biết từ T-048): đường **liệt kê** giữ handle nhưng `os.scandir` theo tên. **T-079 không đụng đường quét** nên con số cùng mức `main`; đối chứng này chứng minh bộ đếm của tôi **bắt được lọt khi có thật**, nên "0 lọt nội dung/cỡ" ở phần tráo thật là thật.

**Ép "luôn thắng" (như Lá Chắn T-063, chứng lỗ hổng trong CODE):** monkeypatch để `x` chắc chắn là junction đúng lúc `lstat`/`open`/`_win_open` mục cuối. Đích junction **nằm ngoài gốc bình thường**: T-079 **chặn được** (read, stat đều "Ảnh vừa bị thay đổi"), kể cả khi ép cả `_win_open` — tức bản vá Windows **đóng được** SL-T063-2/-3 cho trường hợp thường (test `tests/test_images_folders_t063.py::test_sl_t063_2/3_windows_...`, đã gỡ `xfail` của Lá Chắn, nay **XPASS → qua**). Trên `main` thì lọt cả nội dung lẫn cỡ (giữ nguyên lỗ hổng). **Nhưng** khi đích junction là **thư mục "anh em" trông giống gốc** → **SL-T079-1** (bên dưới).

### SL-T063-5 (ENOTDIR bị đếm là "không đọc được")

`_open_error(exc)`: `FileNotFoundError` → "Không tìm thấy"; `PermissionError` → "Không đọc được"; mọi `OSError` khác khi mở một tầng **vừa được kiểm là thư mục** (ELOOP, và ENOTDIR mà Linux trả cho symlink có `O_DIRECTORY`) → `_ChangedError` (quét đếm vào `links`). Dùng chung ở `_posix_open_dir` callers, `_scan_by_fd`, `_listed_names`. Test `test_open_error_message` (4 ca) bắt đủ trên Windows; ca `posix_only` SL-T063-5 (gỡ `xfail`) **chờ cloud Linux**.

### SL-T063-1 (test cũ chỉ đúng với Windows)

`test_unreadable_subfolder_is_counted_not_fatal` viết lại: nhận thư mục khóa theo **định danh trên ổ** (`os.fstat(fd)` khi quét bằng fd, `os.stat(path)` khi quét theo tên) thay vì `Path(path).name`. Các `assert` giữ nguyên. Qua trên Windows; bản mọi-máy `..._when_scandir_gets_fd` của T-063 Soi Lỗi đã qua trên Linux.

### SL-T063-4 (gỡ xfail)

Chỉ xóa dấu `xfail`. Test tự bỏ qua trên NTFS thường. Tôi chạy bằng thư mục tạm **bật phân biệt hoa thường** (`fsutil setCaseSensitiveInfo`, như Lá Chắn T-076): **2/2 ca qua** trên Windows (`thu-muc-khac-hoa-thuong`, `file-khac-hoa-thuong`).

### LC-T076-3 (= SL-T076-2, nháp nhận bản sao ở tên khác)

`ImageEntry.file_id` (`compare=False, repr=False`, chỉ `stat_image` điền). Trong `_check_images` (`drafts.py:943-953`): lần hỏi lại tên cũ phải ra đúng kết quả cũ **và cùng `file_id`**; ảnh ở tên mới phải cùng cỡ, cùng giờ sửa **và cùng `file_id`**. Bản sao (khác file) → "không dùng được". Ổ không có định danh (`file_id = None` cả hai) → như trước (chỉ cỡ, giờ sửa). Tôi kiểm:
- `file_id` **không ra ngoài**: `repr(ImageEntry)` không có, so hai `ImageEntry` không tính (test `test_stat_image_gives_file_id_of_the_checked_file` của Thợ Máy; đột biến MM "tính khi so" → `test_read_listed_images_round_trip` hỏng).
- Gỡ `xfail` SL-T076-2 ×2 (`test_soi_loi_t076.py`), LC-T076-3 (`test_la_chan_t076.py`): nay **qua** trên Windows.

## Lỗi mới

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T079-1 | **Thấp** (Windows; **không áp dụng Mac/Linux**) | `_win_handle_at` so "đường dẫn thật" của handle với `gốc/parts` bằng `_path_key` = **NFC + casefold** (`folders.py:358`, `:382-388`). Phép so này **lỏng hơn** cách ổ phân biệt tên: thư mục "anh em" của gốc có tên chỉ khác **dạng Unicode** (NFC/NFD), khác **`ß`/`ss`**, **dấu Kelvin U+212A/`K`**, hay **hoa thường** (trên thư mục bật phân biệt hoa thường) là **thư mục khác trên ổ** (NTFS không gộp dạng Unicode) nhưng **qua** phép so. Khi kẻ tấn công thắng cuộc đua với junction `x` trỏ vào thư mục anh em đó, `read_image_bytes`/`stat_image` trả nội dung/cỡ file **ngoài thư mục ảnh** | `folders.py:349-358` (`_win_handle_at`), `:382-388` (`_path_key` dùng `_name_key` = NFC+casefold) | `tests/test_soi_loi_t079.py::test_sl_t079_1_...` (`xfail(strict)`, ép "luôn thắng" với đích là thư mục anh em NFD / `ß` / Kelvin / hoa thường). Ca đối chứng `dich-ngoai-goc-thuong` (đích ngoài gốc tên thường): **qua** (T-079 chặn) | Báo lỗi gọn / ra ảnh mồi, không ra nội dung ngoài gốc (F1) | Trả nội dung và cỡ file ngoài gốc (ép thắng). Đích ngoài gốc tên thường thì T-079 chặn được |

**Vì sao Thấp (trên Windows):**
- Giống SL-T063-2 trên Windows: cuộc đua tráo thật **không thắng được** (bảng tráo thật phía trên: 0 lọt; Windows không đổi chỗ nguyên tử + khóa file). Chỉ lọt khi **ép thắng**, tức lỗ hổng trong CODE được hệ điều hành cứu — đúng tầng mức Lá Chắn T-063 đặt cho SL-T063-2 Windows.
- Điều kiện thêm so với SL-T063-2: phải có **thư mục anh em cạnh gốc** tên gần trùng (NFD/`ß`/Kelvin trên NTFS thường, hoặc hoa thường trên ổ phân biệt hoa thường) và kẻ tấn công **ghi được** vào thư mục cha của gốc.
- **Không áp dụng Mac/Linux:** đường đọc/stat của Mac/Linux đi bằng `dir_fd` (`openat O_NOFOLLOW` từng tầng), **không gọi `_win_handle_at`**, không so chuỗi đường dẫn. Một tầng giữa thành liên kết → `openat O_NOFOLLOW` từ chối bất kể tên đích. Nên **SL-T079-1 không mở lại mức Cao của SL-T063-2** trên các nền đó.

**Ý nghĩa:** phiếu muốn Windows "vá thẳng, không dựa vào may mắn hệ điều hành". Bản vá đóng được SL-T063-2/-3 cho **đích thường**, nhưng với **đích anh em trông giống** thì `_win_handle_at` vẫn để lọt và chỉ còn "đua khó thắng" đỡ — đúng thứ phiếu muốn tránh, chỉ ở một trường hợp hẹp hơn.

**Cách sửa (đã thử trên bản sao code):** `_win_handle_at` so **từng phần tên** y như hệ điều hành — gốc trùng đúng cách Windows (dùng lại chính API/handle), các phần sau so bằng `CompareStringOrdinal(…, bIgnoreCase=True)` (không gộp dạng Unicode, không gộp `ß`/Kelvin), không dùng `_path_key`. Thử trên bản sao: **8 ca SL-T079-1 thành XPASS**, 716 test khác **không hỏng**. (Lá Chắn quyết sửa ở T-079 hay ghi sổ.)

## Thử đột biến (plugin `sl79_mutate.py`, thư mục nháp, không commit)

Chép `seo_app` ra thư mục nháp, tắt từng lớp mới, chạy các file test liên quan (có `test_soi_loi_t079.py`). Mỗi lớp mới có ít nhất một test bắt:

| Đột biến | Test bắt |
|---|---|
| Đọc: bỏ so định danh trên fd đã mở | `test_read_refuses_file_replaced_in_place_before_open` (SL-T079) |
| Đọc (Windows): bỏ hỏi đường dẫn thật của handle | `test_windows_unknown_final_path...[read]`, SL-T063-2 Windows, SL-T079-1 đối chứng |
| `stat` (Windows): bỏ hỏi đường dẫn thật | `test_windows_unknown_final_path...[stat]`, `test_windows_stat_handle_opened_through_swapped_folder`, SL-T079-1 đối chứng |
| `stat`: bỏ so định danh với mục vừa kiểm | `test_stat_refuses_file_replaced_in_place_before_opened_stat` |
| `stat`: bỏ kiểm ẩn | `test_stat_refuses_file_turned_hidden...` |
| `stat`: bỏ kiểm cỡ trên mục đã mở | `test_stat_checks_size_on_the_opened_file` ×2 |
| `stat`: bỏ kiểm "file thường" | `test_stat_refuses_item_turned_into_folder_on_disk_without_file_ids` (SL-T079) |
| `stat`: lấy số liệu từ `lstat` theo tên như cũ | `test_stat_numbers_come_from_the_opened_file` (SL-T079) |
| Windows: so đường dẫn thật chỉ theo tên file | SL-T063-2 Windows, `test_windows_stat_handle_opened_through_swapped_folder`, SL-T079-1 đối chứng |
| `stat` handle xin quyền đọc nội dung | `test_windows_stat_image_asks_attributes_only` (Thợ Máy) |
| `_file_id` tính cả khi `st_ino = 0` | `test_file_id_is_unknown_on_disk_without_inode_numbers` (SL-T079) |
| `ImageEntry` tính `file_id` khi so | `test_read_listed_images_round_trip`, `test_stat_image_gives_file_id` |
| nháp: bỏ so `file_id` ở lần hỏi tên cũ | `test_lc_t076_3_old_name_asked_again_must_be_the_same_file` |
| nháp: bỏ so `file_id` ở tên của danh sách | `test_lc_t076_3_file_at_listing_name`, SL-T076-2 ×2, LC-T076-3 |
| `_open_error`: `PermissionError` → "vừa bị thay đổi" | `test_open_error_message[khong-co-quyen]` |

**Hai đột biến "sống sót"** (không hỏng test nào), **đã xác minh là thừa lớp, không phải lỗ hổng:** bỏ `_win_handle_is_link(fd)` hoặc bỏ `_is_link_stat(st)` trên đường `stat` của Windows. Lý do: `_win_open` mở với `FILE_FLAG_OPEN_REPARSE_POINT` nên handle là chính junction/symlink; `GetFinalPathNameByHandleW` giải ra đích **ngoài `gốc/parts`** → `_win_handle_at` **đã** từ chối trước. Hai lớp kia là phòng thủ chồng (giữ được, không hại). Đã đọc code xác nhận.

## Soát 3 file chỉ gỡ xfail (không đổi điều kiện kiểm)

`git diff fa2cc39..team/T-079` ba file: **chỉ có dòng xóa** (các khối `@pytest.mark.xfail(...)` và `import sys`, decorator `@SL_T076_2`), **0 dòng thêm**, không đổi `assert` nào:
- `tests/test_images_folders_t063.py`: −34 (gỡ `xfail` SL-T063-2/-3 POSIX+Windows, -4, -5; bỏ `import sys`).
- `tests/test_la_chan_t076.py`: −7 (gỡ `xfail` LC-T076-3).
- `tests/test_soi_loi_t076.py`: −11 (gỡ `SL_T076_2` ×2).

Các test mới (`tests/test_images_folders.py`, `tests/test_drafts_images.py` của Thợ Máy) đọc kỹ: kiểm đúng ý (mở trong thư mục đã mở, hỏi thuộc tính only, `file_id` đúng/None, bản sao khác định danh bị từ chối). `test_read_detects_swapped_file` đổi hàm giả `os.open` để chỉ tráo file ảnh (Mac/Linux mở `dir_fd`, Windows mở theo path), `assert "thay đổi"` giữ nguyên — không yếu đi.

## Bằng chứng

Máy Windows 11 Pro 10.0.26300, Python 3.12.15, worktree `wt-T-079`, `team/T-079` tại `c7b2394`. Máy chạy song song agent khác.

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py \
    tests/test_images_folders_t063.py tests/test_drafts_images.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py \
    tests/test_images_tags.py tests/test_images_process.py tests/test_app_pages.py \
    tests/test_soi_loi_t079.py -rxX
1464 passed, 26 skipped, 11 xfailed in 121.88s
  11 xfail = 3 cũ (R2-1 ×2, R2-2 của T-048) + 8 SL-T079-1 (file của tôi, Windows)
  so mốc nhánh (không có file tôi): 1452 qua/24 bỏ qua/3 xfail → +12 qua, +2 bỏ qua (POSIX), +8 xfail

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t079.py
1 file already formatted
```

- **File mới `tests/test_soi_loi_t079.py`** (22 ca): 12 qua, 2 bỏ qua (POSIX, chờ Linux), 8 `xfail(strict)` SL-T079-1. Chạy `--runxfail`: 8 ca hỏng đúng ở câu "đọc được / trả cỡ file ngoài thư mục ảnh".
- **Không rò handle:** `sl79_handle_leak.py`, 9.000 vòng (đọc, stat, cả nhánh lỗi mới và ép thắng): handle tiến trình chênh +4 rồi −2.
- **Tốc độ** (`sl79_perf.py`, 300 ảnh 60 KB, 3 lượt xen kẽ, lấy lần nhanh nhất):

| Việc | main | T-079 |
|---|---|---|
| `list_folder` 300 ảnh | 0,018–0,022 s | 0,018–0,021 s |
| 300 `stat_image` | 0,62–0,90 s | 0,75–0,89 s |
| 300 `read_image_bytes` | 4,06–4,66 s | 4,27–4,82 s |
| nháp 300 ảnh / 300 thư mục | 1,63–1,98 s | 1,79–2,20 s |
| SMB `\\localhost\C$`: 300 `stat_image` | 5,1–5,6 s | 6,0 s |
| SMB: nháp 300 ảnh | 10,3 s | 10,8–11,1 s |

Cùng mức, không chậm rõ (chênh trong dao động của máy đang bận; `stat_image` thêm một lần mở handle thuộc tính nên nhỉnh hơn chút, như Lá Chắn T-076 ghi nhận).

- **Ổ Google Drive thật** (`sl79_drivefs_probe.py`, chỉ đọc thuộc tính, chỉ in Đúng/Sai): H: (6 ảnh), I: (6 ảnh). `stat_image` bản T-079 được, cỡ/giờ sửa/`file_id` **trùng `lstat`**, kết quả **giống main**, đường dẫn thật của handle **khớp** `gốc/parts`, gốc trùng từng chữ cả khi gõ đúng lẫn gõ thường. `list_folder` cùng số ảnh với main (2/2, 10/10). Không gọi `read_image_bytes` trên Drive.
- **Quét bí mật:** `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trên thư mục riêng (`tests/test_soi_loi_t079.py`, patch `git diff fa2cc39`, 1 file mồi tiếng Việt): mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`), **0 mục ở file thật**. Đã xóa mồi.

## Đối chiếu tiêu chí xong (phần Windows)

- [x] (1) SL-T063-2, -3 vá, gỡ `xfail`: 2 test Windows của Lá Chắn **XPASS → qua**; tráo thật 0 lọt nội dung/cỡ; **ép thắng đích thường bị chặn**. Phần Mac/Linux đọc code kỹ, **chờ cloud Linux**
- [x] (2) SL-T063-5: `_open_error`, test `test_open_error_message` qua; ca `posix_only` chờ Linux
- [x] (3) SL-T063-1: viết lại, qua trên Windows, không yếu đi
- [x] (4) SL-T063-4: gỡ `xfail`; chạy trên thư mục phân biệt hoa thường của Windows **2/2 qua**
- [x] (5) LC-T076-3: `file_id` giữa các lần hỏi; gỡ `xfail` SL-T076-2 ×2, LC-T076-3, nay qua
- [x] (6) Lớp chặn T-048, T-076 giữ nguyên (so AST: `_resolve_inside`, `_disk_names`, `_found_names`, `_Scan._scan_held`, `_is_link_stat`, `_win_final_path`, `_win_handle_is_link`, `_win_listed_name`, `_path_key`, `_posix_open_dir`, `_match_disk_name`… **GIỮ NGUYÊN**); câu báo cố định, không đường dẫn; tráo thật 0 lộ đường dẫn / xích lỗi
- [x] 3 file chỉ gỡ `xfail`: chỉ xóa dòng, không đổi `assert`
- [x] Lỗi mới: SL-T079-1 thêm `tests/test_soi_loi_t079.py`, `xfail(strict=True)`; không sửa code app
- [x] Test liên quan + `ruff check .` (mục Bằng chứng)

## Phần chưa kiểm được ở máy này (Linux/Mac — do phiên cloud riêng)

- 3 test SL-T063-2/-3/-5 `posix_only` (đã gỡ `xfail`), SL-T063-4 trên ổ phân biệt hoa thường thật, và 7 ca `posix_only` (5 của Thợ Máy + 2 của tôi: `test_posix_folder_swapped_right_before_opened_stat`, `test_posix_image_turned_into_symlink_is_not_followed_by_stat`). **SL-T063-2 là mức Cao trên Linux/Mac** — phần quyết định có đạt cho Mac/Linux nằm ở đây.
- Đo tráo thật liên tục (ca 8a/8b/8c của Soi Lỗi T-063) trên Linux với bản sửa: nếu vá đúng thì 0 lọt nội dung; nếu sai thì các test `posix_only` **hỏng** (không còn `xfail` che).
- Mã lỗi macOS cho `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink (ELOOP hay ENOTDIR): `_open_error` nhận cả hai.

## Rủi ro và điểm cần chú ý

- **SL-T079-1 không chặn phần Windows** (Thấp, Windows-only, không mở lại mức Cao của Mac/Linux). Nhưng là **lỗ còn lại trong chính bản vá Windows**: Lá Chắn nên xếp mức cuối và quyết sửa ngay (cách ở mục SL-T079-1, 8 XPASS trên bản sao) hay ghi sổ rủi ro.
- **Hai đột biến "thừa lớp" (bỏ `_win_handle_is_link` / `_is_link_stat` trên đường stat)** không có test riêng vì `_win_handle_at` đã che; nếu Lá Chắn sửa `_win_handle_at` (SL-T079-1) thì nên rà lại hai lớp này còn che đủ không.
- Phần **Mac/Linux là nơi mức Cao**: báo cáo này **không kết luận cho Mac/Linux**. Cần phiên cloud Linux chạy đủ như T-063 trước khi chuyển Lá Chắn kết luận chung và trước khi app chạy trên Mac/Linux.
- Số **"tráo thành công"** của kẻ tấn công trong phần tráo thật không lấy được (bộ đo phụ của tiến trình con bị cắt khi kết thúc); **số lọt (đo ở phía app) là 0 và tin cậy**, phân bố lỗi + đối chứng dương (lọt 973–1.050 tên) xác nhận tráo có xảy ra và bộ đếm bắt được lọt thật.
- `_NAMES_FROM_RESOLVE` sai nghĩa với tên (Lá Chắn T-076, Thợ Máy ghi nhận): ngoài phạm vi, chưa đổi.

## Đề xuất

- **Phiên cloud Linux:** chạy `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_soi_loi_t079.py -rsxX` (root và `nobody`) và bước 8a/8b/8c tráo thật như T-063. 8 test SL-T079-1 `xfail` tự bỏ qua trên Linux (chúng `windows_only`).
- **Lá Chắn:** xếp mức SL-T079-1; nếu sửa thì theo cách ở mục trên (so tên từng phần như hệ điều hành) — tôi đã thử XPASS trên bản sao, không hỏng test khác.
- **Thợ Máy** (nếu Chỉ Huy giao sửa SL-T079-1): `_win_handle_at` nhận `(root, parts)` thay `path`, so gốc trùng đúng cách Windows và từng phần sau bằng `CompareStringOrdinal(bIgnoreCase=True)`.

## Câu hỏi cho chủ dự án

Không có.

## Kết luận phần Windows: **ĐẠT CÓ ĐIỀU KIỆN**

Trên Windows, bản vá T-079 **đóng được** SL-T063-2/-3 cho trường hợp thường (ép thắng đích ngoài gốc → bị chặn; tráo thật 0 lọt nội dung/cỡ/tên qua >5.000 lần đọc), vá SL-T063-5, -1, -4 và LC-T076-3; lớp chặn T-048/T-076 giữ nguyên; không rò handle, không chậm rõ, câu báo không lộ đường dẫn; 3 file chỉ gỡ `xfail` không đổi điều kiện kiểm. **Còn 1 lỗi Thấp mới SL-T079-1** (Windows-only, không mở lại mức Cao của Mac/Linux): bản vá Windows vẫn dựa vào "đua khó thắng" ở trường hợp thư mục anh em trông giống gốc.

**Chuyển Lá Chắn được** (Lá Chắn xếp mức SL-T079-1 và kiểm F1). **Phần Linux — nơi SL-T063-2 ở mức Cao — chờ phiên cloud Linux**; chưa nên kết luận chung ĐẠT và chưa nên chạy app trên Mac/Linux cho tới khi phần đó chạy xong.

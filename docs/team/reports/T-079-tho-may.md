# Báo cáo T-079 · Đọc ảnh bằng thư mục đã mở từng tầng (vá SL-T063-2) · Thợ Máy

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-079](../tickets/T-079-doc-anh-bang-fd-tung-tang.md) |
| Ngày nộp | 2026-10-22 |
| Nhánh | `team/T-079` (tạo từ `main` `fa2cc39`). Commit: `29a6f69` (sửa `folders.py`, gỡ `xfail` T-063, SL-T063-1), `5a34ccc` (LC-T076-3), `ffe95ec` (test mới), commit báo cáo |
| Kết quả | Hoàn thành phần code và test. **Phần Mac/Linux chưa chạy được trên máy này** (Windows 11, không có WSL, không có máy Mac): đã viết test, chạy thử luồng code bằng bộ giả lập trên Windows; Soi Lỗi cần chạy lại trên cloud Linux |

## Tóm tắt (cho chủ dự án)

Lỗ hổng Soi Lỗi tìm ra (một chương trình lạ trên máy tráo thư mục con thành "lối tắt" đúng lúc app đọc ảnh thì app đọc nhầm một file nằm ngoài thư mục ảnh) **đã được vá trong code, cho cả Windows lẫn Mac/Linux**. Cách vá: app không còn đọc ảnh theo "địa chỉ" của nó nữa, mà đi từng bước vào đúng các thư mục đã kiểm (Mac/Linux), hoặc mở ảnh xong thì hỏi lại chính file đã mở "anh đang thật sự nằm ở đâu" và từ chối nếu không nằm trong thư mục ảnh (Windows). Phép thử "ép kẻ tấn công luôn thắng" của Lá Chắn, trước đây làm Windows lọt nội dung, nay chỉ ra câu báo lỗi gọn.

Người dùng không thấy gì khác khi dùng bình thường. Tôi đã thử trên ổ Google Drive của máy này (chỉ đọc thông tin file, không mở nội dung, không ghi tên file nào ra): app vẫn đọc được thông tin ảnh như trước. Thêm một chỗ nhỏ: khi kiểm lại ảnh trong bản nháp mà thư mục vừa bị đổi tên, app nay so cả "số căn cước" của file, nên một **bản sao** y hệt nằm ở thư mục khác không còn bị nhận nhầm là ảnh đã chọn.

Còn lại: phần chạy trên Mac/Linux tôi chỉ chạy được bằng giả lập trên Windows; cần Soi Lỗi chạy lại trên máy Linux (cloud) như lần T-063 trước khi gộp.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/folders.py` | `read_image_bytes` mở ảnh qua `_open_image`, `stat_image` lấy số liệu qua `_opened_stat` (không đi theo chuỗi đường dẫn); `_open_error` (ENOTDIR = vừa bị thay đổi); `_win_open` (tách từ `_win_hold_dir`, không đổi hành vi giữ thư mục), `_win_handle_at`; `ImageEntry.file_id` |
| `seo_app/storage/drafts.py` | Chỉ phần LC-T076-3: bước hỏi lại tên cũ và hỏi ở tên mới so cả `file_id` (`drafts.py:943-953`) |
| `tests/test_images_folders.py` | Viết lại `test_unreadable_subfolder_is_counted_not_fatal` (SL-T063-1); hàm giả `os.open` của `test_read_detects_swapped_file` chỉ tráo đúng file ảnh; thêm 8 test T-079 (14 ca; 3 test, 5 ca chỉ chạy trên Mac/Linux) |
| `tests/test_drafts_images.py` | Thêm 3 test LC-T076-3 (5 ca: `file_id` trên ổ giả và ổ thật) |
| `tests/test_images_folders_t063.py` | Chỉ gỡ `xfail` SL-T063-2, -3 (Mac/Linux và Windows), -4, -5; bỏ `import sys` không còn dùng (ruff) |
| `tests/test_soi_loi_t076.py`, `tests/test_la_chan_t076.py` | Chỉ gỡ `xfail` SL-T076-2 ×2, LC-T076-3 |
| `docs/team/reports/T-079-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `config/**`, không thêm thư viện.

## Cách sửa từng lỗi

### SL-T063-2 (đọc nội dung file ngoài gốc) và SL-T063-3 (lộ cỡ, giờ sửa)

Gốc lỗi: `_resolve_inside` kiểm bằng `lstat`/`resolve` **theo chuỗi đường dẫn**, rồi `read_image_bytes` lại `os.open(đường dẫn)`: tầng giữa bị tráo thành liên kết ngay sau lúc kiểm thì cả `lstat` mục cuối lẫn `open` đi xuyên ra ngoài, và phép so định danh so hai thứ cùng nằm ngoài nên khớp. Các lớp chặn cũ (`_resolve_inside`, `_disk_names`, so định danh) **giữ nguyên**; thêm một lớp không đi theo tên:

| | Mac/Linux (`_OPEN_BY_DIR_FD`) | Windows |
|---|---|---|
| Đọc (`_open_image`, `folders.py:892`) | `_posix_open_dir(gốc, parts[:-1])`: mở từng tầng từ gốc bằng `openat(fd_cha, tên, O_DIRECTORY \| O_NOFOLLOW)`; rồi `os.open(tên_file, O_NOFOLLOW \| O_NONBLOCK \| O_NOCTTY \| O_CLOEXEC, dir_fd=fd)`. Không tầng nào đi theo symlink; thư mục đã mở là chính thư mục thật dù tên bị tráo sau đó | `os.open(đường dẫn)` như cũ, rồi `_win_handle_at`: hỏi đường dẫn thật **của chính handle vừa mở** (`GetFinalPathNameByHandleW`, đã có `_win_final_path`), phải đúng là `gốc/parts` (so khóa không phân biệt hoa thường như `_scan_held`). Tầng giữa vừa là junction/symlink thì handle nằm chỗ khác → "Ảnh vừa bị thay đổi…". Không hỏi được → từ chối (ổ nào `resolve(strict=True)` được thì hỏi được, vì `resolve` của Python dùng đúng hàm này) |
| `stat` (`_opened_stat`, `folders.py:840`) | Như trên rồi `os.stat(tên_file, dir_fd=fd, follow_symlinks=False)`: không mở file | `_win_open(đường dẫn, FILE_READ_ATTRIBUTES)`: mở chính file **chỉ để hỏi thuộc tính** (như `os.lstat` của Python làm bên trong; không có quyền đọc nội dung, Drive không tải file về), `_win_handle_at` + `_win_handle_is_link`, rồi `os.fstat` trên handle đó |
| Sau đó | Đọc: `fstat` trên fd đã mở phải là file thường, cùng định danh với mục vừa kiểm (như cũ). `stat`: mục phải là file thường, không phải liên kết, không ẩn, không quá giới hạn, **cùng định danh** với `lstat` của `_resolve_inside`; khác → "Ảnh vừa bị thay đổi…". Số liệu (cỡ, giờ sửa, `file_id`) lấy từ mục đã mở, không từ `lstat` theo tên | (như cột trái) |

Câu báo mới là hằng cố định (`_MSG_IMAGE_CHANGED`, `_MSG_CANNOT_OPEN` = câu cũ), ném `from None`, không có đường dẫn máy.

### SL-T063-5 (ENOTDIR bị đếm là "không đọc được")

`_open_error` (`folders.py:412`) dùng chung cho `_scan_by_fd`, `_listed_names` và hai hàm mới: `FileNotFoundError` → "Không tìm thấy…"; `PermissionError` → "Không đọc được…"; mọi lỗi khác khi mở một tầng **vừa được kiểm là thư mục** (ELOOP, và ENOTDIR mà Linux trả cho symlink khi có `O_DIRECTORY`, hay tầng vừa thành file) → `_ChangedError` ("Thư mục vừa bị thay đổi…", quét thì đếm vào `links`). Trước đây ENOTDIR được xếp chung với "không có quyền".

### SL-T063-1 (test chỉ đúng trên Windows)

`test_unreadable_subfolder_is_counted_not_fatal` nhận thư mục khóa theo **định danh trên ổ** (`os.fstat(fd)` khi app quét bằng fd, `os.stat(path)` khi quét theo đường dẫn) thay vì `Path(path).name`. Các `assert` giữ nguyên.

### SL-T063-4

T-076 đã sửa; chỉ xóa dấu `xfail`. Test này **tự bỏ qua trên Windows** (NTFS không phân biệt hoa thường), nên **chưa chạy được ở máy này**: chỉ máy Linux/Mac phân biệt hoa thường mới chạy (Lá Chắn T-076 đã thấy XPASS trên thư mục tạm bật phân biệt hoa thường).

### LC-T076-3 (= SL-T076-2) · nháp nhận bản sao ở tên khác

`ImageEntry` có thêm `file_id` = (số ổ, số inode) của file, **chỉ `stat_image` điền** (lấy trên mục đã mở; ổ không có số inode thì `None`); kết quả quét để `None`. Trường này `compare=False, repr=False`: so hai `ImageEntry` và `repr` như cũ (test cũ `lib.stat_image(entry.ref) == entry` vẫn đúng). Trong `_check_images` (`drafts.py:943-953`), khi danh sách thư mục cho tên khác: lần hỏi lại tên cũ phải ra đúng kết quả cũ **và cùng `file_id`**; ảnh ở tên mới phải cùng cỡ, cùng giờ sửa **và cùng `file_id`** với lần hỏi đầu. Bản sao (khác file, dù cùng cỡ, cùng giờ sửa) → "không dùng được". Ổ không cho biết định danh (`None` cả hai lần, ví dụ các ổ giả trong test của T-055, T-076) thì chỉ so được cỡ, giờ sửa như trước.

### Test cũ đã chạm (không đổi điều kiện kiểm)

- `test_read_detects_swapped_file`: hàm giả cũ `lambda path, flags: real_open(other, flags)` thay **mọi** `os.open`; trên Mac/Linux app nay mở thư mục gốc rồi mở `a.jpg` với `dir_fd=…` (hàm giả cũ không nhận đối số này). Hàm giả mới chỉ tráo khi mở chính file ảnh (`…a.jpg`), cả hai cách mở. `assert "thay đổi" in str(exc)` giữ nguyên.
- `test_unreadable_subfolder_is_counted_not_fatal`: như mục SL-T063-1.
- Không sửa test của Soi Lỗi, Lá Chắn ngoài việc xóa dấu `xfail` (và dòng `import sys` mà chỉ dấu `xfail` SL-T063-5 dùng).

## Bằng chứng

Máy Windows 11 Pro 10.0.26300 của chủ dự án, Python 3.12.15, worktree `wt-T-079`. Máy đang chạy song song agent khác.

```
# Mốc trước khi sửa (main fa2cc39, 11 file test liên quan):
1433 passed, 19 skipped, 8 xfailed in 210.51s
  8 xfail: R2-1 x2, R2-2 (T-048, giữ), SL-T063-2/-3 Windows, SL-T076-2 x2, LC-T076-3

# Sau khi sửa (11 file như lời giao):
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_images_process.py tests/test_app_pages.py -rxX
1452 passed, 24 skipped, 3 xfailed in 131.60s (0:02:11)
  3 xfail còn lại: R2-1 x2, R2-2 (T-048, không thuộc phiếu này)
  So với mốc: +19 ca mới (14 qua, 5 ca Mac/Linux tự bỏ qua), 5 ca xfail thành qua, 0 hỏng

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check <7 file đã sửa>
… already formatted
```

### Thử đột biến (plugin `mutate_t079.py`, thư mục nháp, không commit)

Tắt từng lớp mới, chạy 6 file test (`test_images_folders`, `_t063`, `_soi_loi`, `test_drafts_images`, `test_soi_loi_t076`, `test_la_chan_t076`):

| Đột biến | Test hỏng |
|---|---|
| Windows không hỏi đường dẫn thật của handle (`_win_handle_at` luôn đúng) | 4: SL-T063-2 Windows của Lá Chắn, 2 ca "không hỏi được đường dẫn thật", ca `stat` qua junction |
| `stat_image` lấy số liệu từ `lstat` theo tên như cũ | 4: SL-T063-3 Windows của Lá Chắn, ca `stat` qua junction, ca "không hỏi được" (stat), ca "chỉ hỏi thuộc tính" |
| `stat_image` không trả `file_id` (nháp chỉ so cỡ, giờ sửa) | 5: SL-T076-2 ×2, LC-T076-3, 2 test `file_id` mới |
| ENOTDIR lại thành "không đọc được" | 1 trên Windows (`test_open_error_message[enotdir]`); trên Linux thêm SL-T063-5 và 2 ca tráo mới |

### Nhánh Mac/Linux chạy bằng giả lập trên Windows (plugin `posix_sim.py`, không commit)

Bật `_OPEN_BY_DIR_FD`, giả `os.open`/`os.stat`/`os.close` có `dir_fd` (fd giả nhớ đường dẫn thư mục) và `_posix_open_dir`, kiểm không còn fd thư mục nào chưa đóng sau mỗi test. Chạy 8 file test (thư mục ảnh, nháp, xử lý ảnh): **841 qua**, 5 hỏng đều do bộ giả: 3 test chỉ dành cho nhánh Windows (`_win_final_path`, `_win_open`) và 2 test Windows của Soi Lỗi T-048 có hàm giả `os.open(path, flags, *args)` không nhận `dir_fd` (trên Mac/Linux thật hai test này tự bỏ qua). Bộ giả chỉ thử **luồng code** (gọi đúng hàm, đóng fd, đổi lỗi thành câu báo), không giả được tính chất "fd giữ đúng thư mục đã mở", nên **không thay** được lượt chạy trên Linux thật.

### Ổ Google Drive for Desktop thật (chỉ đọc thuộc tính, chỉ in Đúng/Sai, không in tên)

Script `probe_drivefs_ids.py`, `probe_drivefs_stat.py` (thư mục nháp): ổ H: (`My Drive` và 2 ảnh), ổ I: (`My Drive`, không thấy ảnh trong giới hạn thử); ổ G: không có `My Drive`.

```
H thư mục My Drive: (mở được handle thuộc tính, định danh trùng lstat, đường thật khớp resolve) = (True, True, True)
H 2 ảnh: (True, True, True) x2
I thư mục My Drive: (True, True, True)
stat_image (bản T-079) trên 2 ảnh ở H:: được, cỡ trùng lstat, có file_id, file_id trùng lstat (x2)
```

Không thử `read_image_bytes` trên Drive (sẽ đọc nội dung, có thể làm Drive tải file về).

### Đo thời gian

Script `perf_t079.py` (thư mục nháp): cùng cây tạm 3.000 ảnh trên ổ NTFS, 48 lần mỗi việc, `main` `fa2cc39` và bản T-079, 3 lượt xen kẽ. Máy đang bận nên số dao động; lượt 2–3: `stat_image` 0,15–0,21 s (`main`) và 0,17 s (T-079); `read_image_bytes` 0,65–1,11 s (`main`) và 0,92–1,07 s (T-079). Cùng mức. (Lượt 1 của T-079 có một lần `stat_image` 1,03 s, các lượt sau không lặp lại.)

### Quét bí mật

`PYTHONUTF8=1 uvx detect-secrets scan --all-files` trong thư mục riêng chứa 8 file của phiếu, patch `git diff fa2cc39` và 1 file mồi có chữ tiếng Việt (khóa AWS giả, `password = …`): chỉ file mồi có mục, bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`); **0 mục ở file thật**. Đã xóa file mồi.

## Đối chiếu tiêu chí xong

- [x] (1) SL-T063-2, -3: đọc, `stat` không đi theo chuỗi đường dẫn; Mac/Linux mở từng tầng bằng `O_DIRECTORY | O_NOFOLLOW` từ fd gốc, file `O_NOFOLLOW`, số liệu từ mục đã mở, so định danh với mục đã mở; Windows giữ lớp cũ + hỏi đường dẫn thật của handle (cách "ép luôn thắng" của Lá Chắn không lọt). Đã gỡ 2 `xfail` Windows của Lá Chắn (qua trên máy này) và `xfail` SL-T063-2, -3 Mac/Linux (**chưa chạy trên Linux ở máy này**)
- [x] (2) SL-T063-5: `_open_error`; gỡ `xfail` (chỉ đánh trên Linux; **chưa chạy trên Linux ở máy này**)
- [x] (3) SL-T063-1: viết lại, giữ nguyên `assert`; qua trên Windows; trên Mac/Linux là cùng cách của test `…_when_scandir_gets_fd` mà Soi Lỗi đã chạy qua trên Linux
- [x] (4) SL-T063-4: xóa `xfail`; tự bỏ qua trên Windows, **chưa chạy được trên Linux ở máy này**
- [x] (5) LC-T076-3: so `file_id` giữa các lần hỏi; gỡ `xfail` SL-T076-2 ×2, LC-T076-3 (qua trên máy này)
- [x] (6) Giữ lớp chặn T-048, T-076 (`_parse_rel`, `_is_safe_name`, `_resolve_inside`, `_checked_file`, `_disk_names`, `_Scan` không đổi trừ cách đổi lỗi ENOTDIR); câu báo cố định, không đường dẫn; `assert` của test cũ không đổi
- [x] Test liên quan + `ruff check .` (mục Bằng chứng)

## Phần chưa kiểm được ở máy này (Linux/Mac)

- 8 test chỉ chạy trên Mac/Linux đang chờ: SL-T063-2, -3, -5 (đã gỡ `xfail`), SL-T063-4 (cần ổ phân biệt hoa thường), và 5 test mới (`test_posix_image_is_opened_inside_the_opened_folder`, `test_posix_folder_swapped_before_opening_levels_is_refused` ×2, `test_posix_file_swapped_to_symlink_after_folder_is_opened` ×2). Nếu cách sửa đúng, chúng qua; nếu sai, chúng **hỏng** (không còn `xfail` che).
- Mã lỗi của macOS cho `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink (ELOOP hay ENOTDIR): cách sửa nhận cả hai.
- Đo tráo thật liên tục (bước 3 ca 8a/8b của Soi Lỗi T-063) trên Linux với bản sửa.

## Rủi ro và điểm cần chú ý

- **Mac/Linux: thư mục chỉ có quyền "đi qua"** (`--x`, không có quyền đọc danh sách) nay không đọc được ảnh bên trong (mở thư mục cần quyền đọc). Trước đây đọc được theo đường dẫn; quét và `stat_image` (từ T-076) vốn đã không được. Chặt hơn, không lỏng hơn.
- **Windows `stat_image` mở chính file ảnh** (handle chỉ hỏi thuộc tính, không có quyền đọc nội dung), giống việc `os.lstat`, `resolve` của Python vốn làm trên từng ảnh. Đã thử đúng trên ổ Drive thật (mục Bằng chứng). Test `test_check_opens_no_image_file` của Soi Lỗi T-055 theo dõi `os.open`, `open`, `_win_hold_dir` nên không thấy lần mở này; test mới `test_windows_stat_image_asks_attributes_only` khóa lại: chỉ đúng một lần mở, chỉ quyền `FILE_READ_ATTRIBUTES`.
- Windows: ổ không trả lời được câu "đường dẫn thật của handle" thì không đọc được ảnh (an toàn trước). Chưa thấy ổ nào như vậy mà vẫn `resolve` được.
- Ổ không có số inode (`st_ino = 0`): `file_id` là `None`, nháp quay về so cỡ, giờ sửa (như trước); các phép so định danh trong `folders.py` bỏ qua như cũ (`_same_file`). Lớp chặn mới (fd từng tầng, đường dẫn thật của handle) **không** phụ thuộc số inode. Hard link (LC-T048-6, sổ rủi ro) không đổi.
- Lá Chắn T-076 ghi nhận (không bắt buộc): tên ngắn 8.3 trên ổ "resolve trả chữ đã gõ" ở đường đọc. Tôi không đổi phần này.

## Đề xuất

- **Soi Lỗi (cloud Linux):** chạy lại `tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py -rs` và bước 3 ca 8a/8b/8c (tráo thật liên tục, root và `nobody`) trên nhánh này.
- **Lá Chắn:** chạy lại `t063_win_probe.py` (tráo thật trên Windows) với bản sửa nếu muốn có số đo; xét `_win_open` mở file chỉ để hỏi thuộc tính trong `stat_image`.
- Hằng `_NAMES_FROM_RESOLVE` sai nghĩa với tên (Lá Chắn T-076 ghi nhận): chưa đổi vì test của Soi Lỗi T-076 đặt hằng này (ngoài phạm vi sửa của tôi).

## Câu hỏi cho chủ dự án

Không có.

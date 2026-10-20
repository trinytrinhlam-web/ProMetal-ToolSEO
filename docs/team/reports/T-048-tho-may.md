# Báo cáo T-048 · Đọc thư mục ảnh an toàn (G3-2)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-048](../tickets/T-048-doc-thu-muc-anh-an-toan.md) |
| Ngày nộp | 2026-10-19 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

App đã có phần "đọc thư mục ảnh" (chưa có giao diện, Họa Sĩ làm ở phiếu sau). Phần này chỉ **đọc** ảnh trong các thư mục ghi ở `IMAGE_FOLDERS`. Nó không đọc ra ngoài các thư mục đó, kể cả khi trong thư mục có lối tắt (symlink, junction) trỏ ra chỗ khác. Thư mục rất lớn hay Google Drive chậm thì app tự dừng sau 5.000 mục hoặc 10 giây và báo "còn nữa, hãy chọn thư mục con" chứ không treo. App không tạo, sửa hay xóa gì trong thư mục ảnh.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/__init__.py` | Mới, chỉ có docstring (phiếu sau import thẳng module con, không sửa file này) |
| `seo_app/images/folders.py` | Mới: `ImageRef`, `ImageLibrary` (xem thư mục, kiểm và đọc một ảnh), các khuôn kết quả |
| `tests/test_images_folders.py` | Mới: 138 test (132 chạy trên Windows, 6 bỏ qua có lý do) |

## API đã viết (`seo_app/images/folders.py`)

| Tên | Vai trò |
|---|---|
| `ImageRef(root_index, rel_path)` | Chỉ tới một ảnh: số thứ tự thư mục gốc (từ 0) và đường dẫn tương đối `a/b/anh.jpg`. Kiểm ngay lúc tạo, an toàn khi tạo từ nháp đã lưu (`folders.py:133`) |
| `ImageLibrary(folders, *, max_file_bytes, max_entries, max_seconds, clock)` / `ImageLibrary.from_settings(settings)` | Truy cập chỉ đọc. Đường dẫn tuyệt đối chỉ nằm trong thuộc tính riêng; `repr` chỉ in "ImageLibrary(N thư mục)" (`folders.py:223`, `:250`) |
| `.roots() -> tuple[RootInfo]` | Mỗi gốc có `label` (chỉ tên thư mục cuối), `available`, `message` (ví dụ "Chưa thấy thư mục ảnh số 2… USB chưa cắm hoặc Google Drive chưa chạy?") |
| `.list_folder(root_index, rel_dir="", *, page=1, page_size=48, recursive=False, max_depth=8) -> FolderListing` | Thư mục con trực tiếp, một trang ảnh sắp theo tên, `total_images`, `page_count`, `has_next_page`, `truncated` + `notice` ("còn nữa"), `skipped: SkipCounts` (liên kết, ẩn, tên lạ, file khác, rỗng, quá lớn, không đọc được, quá sâu). Không mở file ảnh khi quét |
| `.stat_image(ref) -> ImageEntry` | Kiểm một ảnh (ví dụ ảnh trong nháp) còn dùng được, không mở file |
| `.read_image_bytes(ref) -> bytes` | Đọc nguyên nội dung (không quá 40 MB). Trả bytes chứ không trả đường dẫn hay đối tượng file |
| `ImageFolderError` | Mọi lỗi; câu tiếng Việt, không chứa đường dẫn tuyệt đối, không xích theo lỗi hệ điều hành (`from None`) |
| Hằng số | `IMAGE_EXTENSIONS` (`.jpg .jpeg .png .webp .heic .heif .avif`), `MAX_IMAGE_BYTES = 40 MB`, `DEFAULT_MAX_ENTRIES = 5000`, `DEFAULT_MAX_SECONDS = 10`, `DEFAULT_PAGE_SIZE = 48`, `MAX_PAGE_SIZE = 200` (`folders.py:36-43`) |

## Bằng chứng

Máy Windows 11, Python 3.12.15, worktree `wt-T-048`, nhánh `team/T-048` tại `ca32762`, 2026-10-19 13:17 (+07).

```
$ uv run pytest -q -p no:cacheprovider
5756 passed, 17 skipped, 35 xfailed, 1 warning in 583.11s (0:09:43)

$ uv run pytest tests/test_images_folders.py -q -p no:cacheprovider -rs
SKIPPED [1] tests\test_images_folders.py:363: chỉ tạo được trên Mac/Linux      (tên file lạ)
SKIPPED [1] tests\test_images_folders.py:376: chỉ tạo được trên Mac/Linux      (FIFO)
SKIPPED [4] tests\test_images_folders.py:62: Máy Windows này không cho tạo symlink (lỗi 1314); xem test junction
132 passed, 6 skipped in 10.14s

$ uv run ruff check .
All checks passed!
```

Cảnh báo duy nhất (Pydantic serializer, thư viện `anthropic`) có từ trước, không liên quan phiếu này. Các test junction (6 test) chạy **thật** trên máy này. Symlink cần quyền đặc biệt trên Windows (lỗi 1314) nên 4 test symlink tự bỏ qua trên Windows và chạy trên Mac/Linux. Phần nhận diện symlink được kiểm thêm bằng `test_is_link_stat`, chạy trên mọi hệ điều hành.

## Đối chiếu yêu cầu phiếu

- [x] **YC1. Nhận diện bằng (chỉ số gốc, đường dẫn tương đối), không lưu, không hiện đường dẫn tuyệt đối.** `ImageRef` (`folders.py:133`); kết quả trả về chỉ chứa tên và đường dẫn tương đối dạng `/`. Mọi test lỗi đi qua `raises_safely` để kiểm câu lỗi không chứa `tmp_path` (cả dạng `\` lẫn `/`) và không xích lỗi OS. Có kiểm `repr` của `ImageLibrary`, `RootInfo`, `FolderListing` (`test_library_repr_hides_paths`, `test_roots_report_label_and_availability`, `test_list_folder_returns_images_subfolders_and_skips`).
- [x] **YC2. Chặn `..`, tuyệt đối, ổ đĩa, UNC, symlink, junction.** Có ba lớp chặn:
  1. Kiểm dạng chữ (`_parse_rel`, `_is_safe_name`, `folders.py:69-104`) theo cả kiểu Windows lẫn kiểu Mac. Từ chối `..`, `.`, phần rỗng, `/…`, `//server`, `\\server`, `C:/`, `C:a.jpg`, dấu `\`, dấu `:` (gồm luồng NTFS `a.jpg::$DATA`), ký tự điều khiển, `<>"|?*`, tên thiết bị `CON/NUL/AUX/COMn/LPTn` (cả `COM¹`), tên kết thúc bằng dấu chấm hoặc khoảng trắng, tên ẩn bắt đầu bằng `.`, tên quá dài. Có 42 trường hợp trong `test_image_ref_rejects_unsafe_paths`.
  2. `lstat` **từng phần** của đường dẫn. Từ chối symlink, junction và mọi reparse point có bit "name surrogate" (bit này nghĩa là trỏ sang chỗ khác). Có kiểm thêm `Path.is_junction()` (`folders.py:307`). Khi quét thì kiểm `DirEntry.is_symlink()`, `is_junction()` và reparse tag (`folders.py:524`).
  3. `resolve(strict=True)` rồi bắt buộc `is_relative_to(gốc)` (`folders.py:317`). Lớp này được thử **riêng**: tắt lớp 2 bằng monkeypatch thì vẫn chặn được junction và symlink ra ngoài (`test_resolve_check_alone_blocks_junction_outside`, `..._symlink_outside`).
  Test junction: `test_junction_to_outside_is_not_listed`, `..._cannot_be_opened`, `test_junction_pointing_inside_root_is_also_refused`, `test_junction_loop_does_not_hang`.
- [x] **YC3. Đuôi file và giới hạn dung lượng.** Nhận JPEG, PNG, WebP, HEIC/HEIF, AVIF. Không nhận GIF, BMP, TIFF, `.lnk`, `.jpg.exe`. Giới hạn 40 MB được kiểm 3 lần: khi quét (`stat`), trước khi mở (`lstat`) và sau khi mở (`fstat`). App chỉ đọc tối đa `giới hạn + 1` byte, nên file có to ra giữa chừng cũng không đọc quá giới hạn (`test_read_rejects_file_growing_after_check`). File 0 byte bị loại.
- [x] **YC4. Ngân sách và phân trang.** Ngân sách mặc định là 5.000 mục và 10 giây cho mỗi lần quét. Hết ngân sách thì `truncated=True` và `notice` báo "còn nữa…". Kiểm bằng đồng hồ giả (`test_time_budget_stops_and_says_more`) và bằng ổ chậm giả, mỗi mục tốn 1 giây (`test_slow_directory_iteration_is_cut_off`). Ngân sách tính cả file không phải ảnh và cả thư mục con. Phân trang: 1–200 ảnh mỗi trang; số trang vượt cuối thì đưa về trang cuối (`test_pagination`, `test_page_beyond_end_is_clamped`). Khi quét không mở file nào, nên không làm Drive tải file "chỉ trực tuyến" về.
- [x] **YC5. Tên thư mục là dữ liệu chưa tin cậy.** Module chỉ trả nguyên tên, không suy ra thẻ (để T-052). Tên có ký tự điều khiển hay ký tự lạ bị bỏ qua và đếm vào `skipped.bad_names`.
- [x] **YC6. Junction chạy trên Windows, symlink trên Mac/Linux.** Test junction có `skipif(not Windows)`. Test symlink chỉ tự bỏ qua khi Windows không cho tạo symlink. Lớp kiểm bảo mật không có nhánh nào bị tắt theo hệ điều hành.
- [x] **Chỉ đọc (quyết định 3A).** `test_library_never_changes_image_folder` so ảnh chụp cây thư mục (tên, cỡ, thời điểm sửa đến ns) trước và sau khi dùng. `test_module_has_no_write_calls` dò mã nguồn: không có `write_*`, `mkdir`, `unlink`, `rename(`, `os.replace`, `O_WRONLY/O_RDWR/O_CREAT`, `pickle`, `eval(`.
- [x] **F1** (như trên). **F3**: không đọc file văn bản nào, không `eval`/`pickle`. **U2**: phiếu không thêm trang giao diện nào. **Lá Chắn số 3**: xem YC5. **Lá Chắn số 9**: câu lỗi không có đường dẫn tuyệt đối; phần cache ảnh xem trước thuộc G3-3.
- [x] `uv run pytest` (0 hỏng, 0 lỗi trên Windows), `uv run ruff check .` sạch.

## Rủi ro và điểm cần chú ý

- **Khoảng hở giữa lúc kiểm và lúc mở (TOCTOU).** Có người tráo một thư mục ở giữa thành liên kết đúng lúc app kiểm xong và trước khi mở, thì về lý thuyết vẫn lọt. Đã có ba lớp giảm rủi ro: `O_NOFOLLOW` (Mac/Linux), so `(st_dev, st_ino)` của file đã mở với file đã kiểm (`folders.py:441`), và `O_NONBLOCK` để không treo nếu file bị tráo thành FIFO. Muốn khai thác thì phải có quyền ghi vào thư mục ảnh (Drive của công ty). Mức rủi ro thấp (suy luận).
- **Hard link** trỏ ra file ngoài thư mục thì không phát hiện được (bản chất của hard link). Muốn tạo hard link cũng cần quyền ghi vào thư mục ảnh.
- **Ngân sách thời gian không cắt ngang được một lệnh hệ điều hành đang bị kẹt.** Nếu một lần `scandir`/`next` bị Drive giữ rất lâu thì app chỉ dừng sau khi lệnh đó trả về. Muốn cắt hẳn thì giao diện phải chạy quét trong luồng riêng (G3-10).
- **Bỏ qua cả tên hợp lệ trên Mac** nhưng không dùng được trên Windows (có `\ : ? * < > | "`, tên kết thúc bằng dấu chấm). Đây là chủ ý, để một ảnh thấy được ở máy này thì máy kia cũng mở được. Các tên này được đếm vào `skipped.bad_names` để giao diện báo cho người dùng.
- **Gốc khai báo là junction hay symlink thì được phép.** App dùng thư mục thật mà gốc trỏ tới (`test_root_configured_as_junction_is_allowed`). Gốc ghi đường dẫn tương đối thì bị từ chối, vì kết quả sẽ phụ thuộc thư mục đang chạy app.
- **File ẩn và file hệ thống của Windows** bị bỏ qua (ví dụ `desktop.ini`, `$RECYCLE.BIN`). Riêng thuộc tính `UF_HIDDEN` trên Mac đã có trong code nhưng chưa thử trên Mac thật.
- **Chuẩn hóa Unicode tên file (NFC/NFD giữa Mac và Windows).** Code không chuẩn hóa. APFS không phân biệt hai dạng nên vẫn mở được (suy luận, chưa thử trên Mac). Phiếu G3-9 (nháp lưu ảnh) cần để ý điểm này.
- `read_image_bytes` chưa kiểm nội dung có đúng là ảnh hay không. Việc đó thuộc G3-3 (`Image.open(formats=…)`).

## Đề xuất: điểm Soi Lỗi và Lá Chắn nên thử

1. Chạy `tests/test_images_folders.py` trên **Mac**, để 4 test symlink, test tên lạ và test FIFO chạy thật.
2. Junction lồng nhau, ổ gắn vào thư mục (mount point), thư mục `\\?\` dài hơn 260 ký tự, ổ mạng ánh xạ thành ký tự ổ đĩa (resolve ra UNC).
3. Thư mục Google Drive for Desktop thật: file "chỉ trực tuyến" có bị coi là liên kết không (code kỳ vọng là không, vì reparse tag cloud không có bit name surrogate), và tốc độ quét 5.000 mục.
4. Tên Unicode đặc biệt: ký tự đảo chiều RLO (`U+202E`, hiện ngược thành `gpj.exe`), ký tự rộng 0. Code chỉ chặn ký tự điều khiển loại Cc, chưa chặn loại Cf. Giao diện phải escape khi hiện tên.
5. Tráo file hay thư mục giữa lúc kiểm và lúc đọc (TOCTOU) trên Mac/Linux.
6. Lá Chắn soát `ImageRef` tạo từ dữ liệu nháp (G3-9) và xác nhận giao diện (G3-10) không dùng thẳng `ImageLibrary._folders`.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (sửa theo Soi Lỗi, 2026-10-19)

Soi Lỗi kết luận ĐẠT CÓ ĐIỀU KIỆN ([T-048-soi-loi.md](T-048-soi-loi.md)). Lượt này sửa đủ 5 lỗi L1–L5 và bỏ đúng 9 dấu `xfail` tương ứng trong `tests/test_images_folders_soi_loi.py`. Hard link chỉ ghi nhận, không sửa (Chỉ Huy đưa vào sổ rủi ro).

### Đã thay đổi

| Commit | Lỗi | Thay đổi |
|---|---|---|
| `17ac948` | L2 | `_is_safe_name` từ chối thêm ký tự loại `Cs` (surrogate lẻ) và 9 ký tự điều khiển hướng chữ U+202A–U+202E, U+2066–U+2069 (`folders.py`, `_BIDI_CONTROLS`, `_FORBIDDEN_CATEGORIES`). Áp cho cả lúc quét lẫn `ImageRef` |
| `172ebf5` | L3, L4 | Chỉ đổi dấu phẩy trong con số ("5.000"), câu giữ nguyên dấu phẩy. Lấy mục kế tiếp trước rồi mới kiểm ngân sách số mục: có mục thứ `max_entries + 1` mới báo "còn nữa" |
| `f0c835f` | L5 | `_resolve_inside` từ chối mọi phần đường dẫn là mục ẩn hoặc hệ thống (theo đúng luật lúc quét). Sau `resolve()`, tên thật trên ổ phải trùng tên đã gõ (so không phân biệt hoa thường, cùng dạng NFC), nên chặn được tên ngắn 8.3 (`SECRET~1`): một file chỉ còn một `ImageRef` |
| `525e769` | L1 | Quét thư mục không còn khe giữa lúc kiểm và lúc đọc (chi tiết bên dưới) |
| `882dc18` | — | Ghi các ký tự hướng chữ trong mã nguồn bằng mã `\u…` thay vì ký tự vô hình (tránh kiểu "Trojan Source"); cập nhật docstring |

### Cách sửa L1

Trước đây `list_folder` kiểm thư mục theo tên rồi mới `os.scandir(tên)`; thư mục bị tráo thành junction ở giữa thì bị quét xuyên ra ngoài gốc. Bây giờ mỗi thư mục được quét qua `_Scan._scan_dir`:

- **Windows** (`_scan_held`, `_win_hold_dir`, `_win_final_path`):
  1. Mở handle của thư mục với quyền đọc danh sách (`FILE_LIST_DIRECTORY`). Handle mở bằng `FILE_FLAG_OPEN_REPARSE_POINT` (không đi theo junction) và **không** cho chia sẻ quyền xóa.
  2. Trong lúc còn giữ handle, Windows không cho đổi tên hay xóa chính thư mục đó lẫn mọi thư mục cha. Tôi đã thử trên NTFS: đổi tên thư mục bị lỗi 32, đổi tên thư mục cha bị lỗi 5 (có test `test_held_directory_and_parents_cannot_be_renamed_during_scan`).
  3. Hỏi **chính handle** đường dẫn thật của nó (`GetFinalPathNameByHandleW`) và kiểm reparse tag. Đường dẫn phải trùng `gốc/parts` và thư mục không được là junction; lệch thì từ chối. Qua được bước này thì thư mục đang giữ chắc chắn nằm trong gốc, và cả đường đi bị khóa cho tới khi nhả.
  4. Quét xong, kiểm lại thư mục chưa bị đặt junction tại chỗ.
- **Mac/Linux** (`_scan_by_fd`, `_posix_open_dir`): mở từng tầng từ gốc xuống bằng `os.open(tên, O_DIRECTORY | O_NOFOLLOW, dir_fd=fd_cha)` rồi `os.scandir(fd)`. App quét đúng thư mục đã mở, đi qua toàn thư mục thật; tráo tên sau đó không còn tác dụng.
- **Ổ không giữ được thư mục** (Windows, ổ lạ: `CreateFileW` hoặc `GetFinalPathNameByHandleW` lỗi): kiểm cả đường đi trước và sau khi quét, so định danh `(st_dev, st_ino)`.
- Phát hiện tráo thì **bỏ toàn bộ kết quả của thư mục đó**: trả lại danh sách ảnh, thư mục con và bộ đếm như trước khi quét nó, rồi đếm vào `skipped.links`. Thư mục đang xem (tầng 0) bị tráo thì báo "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại."
- Nhờ hỏi đường dẫn thật từ handle, mỗi thư mục chỉ tốn vài lệnh hệ thống, không phải kiểm lại cả đường đi. Cây sâu 120 tầng quét hết trong 0,37 giây. Bản đầu tiên kiểm cả đường đi cho từng thư mục mất 6,9 giây và làm 2 test cây sâu của Soi Lỗi hết giờ, nên tôi đã bỏ cách đó.

### Cách sửa L2

Thêm loại `Cs` vào nhóm ký tự bị từ chối (trước chỉ có `Cc`). Tên có surrogate lẻ bị bỏ qua khi quét (đếm vào `skipped.bad_names`), và `ImageRef` từ chối ngay khi tạo. Tôi chặn thêm 9 ký tự điều khiển hướng chữ theo đề nghị của Soi Lỗi, vì tên ảnh thật không cần chúng. Hệ quả: test `test_bidi_and_zero_width_cannot_disguise_extension` của Soi Lỗi giờ đếm tên có RLO vào `bad_names` thay vì `other_files`. Tôi đổi một dòng kiểm thành `other_files + bad_names == 1` (có ghi chú trong test); ý của test giữ nguyên.

### Các xfail đã bỏ (9 ca, trong `tests/test_images_folders_soi_loi.py`)

- L1: `test_list_folder_dir_swapped_to_junction_after_check`, `test_recursive_scan_subdir_swapped_to_junction_before_its_turn`
- L2: `test_listing_never_returns_names_that_cannot_be_utf8_encoded`, `test_image_ref_rejects_lone_surrogates` (2 ca)
- L3: `test_entry_budget_notice_keeps_sentence_comma`
- L4: `test_folder_with_exactly_budget_entries_is_not_truncated`
- L5: `test_hidden_directory_cannot_be_reached_by_crafted_ref`, `test_short_8dot3_alias_cannot_reach_dot_directory`

### Test mới (`tests/test_images_folders.py`)

- 5 ca mới trong `test_image_ref_rejects_unsafe_paths`: surrogate lẻ và ký tự hướng chữ.
- `test_held_directory_and_parents_cannot_be_renamed_during_scan`: đang quét thì đổi tên thư mục bị lỗi 32, đổi tên thư mục cha bị lỗi 5.
- `test_fallback_without_hold_discards_swapped_directory`, `test_fallback_recursive_keeps_other_folders`: khi không giữ được thư mục, kiểm hai lần vẫn bắt được thư mục bị tráo; kết quả của thư mục đó bị bỏ, thư mục khác giữ nguyên.
- `test_held_directory_with_other_final_path_is_refused`: đường dẫn thật của handle khác `gốc/parts` thì từ chối.
- `test_junction_set_in_place_during_scan_is_refused`: thư mục bị đặt junction tại chỗ trong lúc quét thì bỏ kết quả.
- `test_scan_of_deep_tree_is_fast`: cây 100 tầng quét dưới 5 giây.

### Bằng chứng lượt 2

Máy Windows 11, Python 3.12.15, nhánh `team/T-048`.

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py -q -p no:cacheprovider
222 passed, 6 skipped in 28.90s          (0 xfail: cả 9 lỗi đã sửa)

$ uv run pytest -q -p no:cacheprovider
5846 passed, 17 skipped, 35 xfailed, 1 warning in 636.87s (0:10:36)
                                  (35 xfail đều có từ trước; 9 xfail của Soi Lỗi đã hết; chạy ở 7405d3a, code giống 882dc18)

$ uv run ruff check .
All checks passed!
```

### Rủi ro còn lại

- **Nhánh Mac/Linux (`_scan_by_fd`, `_posix_open_dir`) chưa chạy được trên máy này** (Windows, không có WSL). Code dùng API chuẩn (`os.open` với `dir_fd`, `os.scandir(fd)`), nhưng cần Soi Lỗi chạy `tests/test_images_folders*.py` trên Mac.
- **Windows: khe rất hẹp còn lại.** Kẻ tấn công có quyền ghi phải làm đủ ba bước ngay giữa lúc app đang quét: xóa hết file trong thư mục, đặt junction ngay tại thư mục đó, rồi gỡ junction trước khi app kiểm lần cuối. Mới đó app mới liệt kê được tên file ngoài gốc. Muốn đóng hẳn khe này thì phải tự liệt kê thư mục qua handle (`GetFileInformationByHandleEx`, `FileIdBothDirectoryInfo`), tức là viết lại một phần `os.scandir` bằng ctypes. Tôi chưa làm vì phức tạp và rủi ro lỗi cao hơn lợi ích. Đề nghị ghi vào sổ rủi ro.
- **Ổ không giữ được thư mục** thì quay về cách kiểm hai lần, vẫn còn khe "tráo rồi tráo lại".
- **Trong lúc quét (tối đa 10 giây), Windows không cho đổi tên hay xóa thư mục đang quét và các thư mục cha.** Google Drive for Desktop đồng bộ đúng lúc đó có thể phải thử lại. Chưa thử với Drive thật.
- **Nội dung file:** `read_image_bytes` vẫn chặn như lượt 1, gồm kiểm cả đường đi và so `(st_dev, st_ino)` sau khi mở.
- **Hard link:** như lượt 1, chỉ ghi nhận.

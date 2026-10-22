# Báo cáo T-063 · Chạy test đọc thư mục ảnh (T-048) trên Linux · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-063](../tickets/T-063-chay-test-t048-tren-mac-linux.md) |
| Ngày nộp | 2026-10-22 |
| Máy kiểm | Phiên Claude Code trên cloud: **Ubuntu 24.04.5 LTS**, nhân Linux 6.18.44 (x86_64), thư mục tạm trên ổ **ext4** (phân biệt hoa thường, phân biệt NFC/NFD); **Python 3.12.3** (máy Windows của đội: 3.12.15); **uv 0.11.32**; pytest 9.1.1; ruff 0.16.10. Phiên chạy bằng **root**, nên phần quyền đọc thật chạy thêm bằng người dùng thường `nobody` (uid 65534) qua `setpriv` |
| Mã nguồn | `main` tại `400fa8c` (nhánh `team/T-063` tách từ đây); nhánh `team/T-076` tại `006b13b` (worktree `/tmp/t076`, chỉ đọc) |
| Kết quả | Hoàn thành phần Linux. **Kết luận phần Linux: KHÔNG ĐẠT** (1 lỗi đề xuất mức **Cao**: SL-T063-2). Phần chỉ có trên Mac: chưa kiểm, chờ máy Mac |

## Tóm tắt (cho chủ dự án)

Lần đầu tiên bộ test đọc thư mục ảnh chạy trên máy không phải Windows. Phần **xem danh sách ảnh** trên Mac/Linux làm đúng như thiết kế: 6 test chỉ chạy được trên Mac/Linux nay đều chạy và qua; lối tắt (symlink) đặt sẵn trong thư mục ảnh, lối tắt trỏ ra ngoài, tên file hỏng mã chữ, thư mục bị khóa quyền đều bị chặn hoặc báo lỗi gọn, câu báo lỗi không lộ đường dẫn trên máy. Tôi cho một chương trình khác liên tục biến thư mục ảnh thành lối tắt trỏ ra ngoài trong lúc app xem và đọc ảnh hàng trăm nghìn lần: **danh sách ảnh không lần nào lọt tên file bên ngoài**, câu báo lỗi không lần nào lộ đường dẫn.

Nhưng tôi tìm được **một lỗ hổng ở bước đọc nội dung ảnh**: nếu có một chương trình đang chạy trên máy, có quyền ghi vào thư mục ảnh và liên tục tráo một thư mục con thành lối tắt, thì app **đọc được nội dung một file nằm ngoài thư mục ảnh** (đo được hàng trăm lần trong 10–20 giây; có cách tái hiện chắc chắn). Trên Windows, Lá Chắn T-048 đo 0 lần với cách tráo chậm hơn; tôi không có máy Windows để thử cách tráo nhanh. Theo bảng mức của dự án, "đọc được file ngoài thư mục ảnh" là mức **Cao**, nên tôi đề nghị **chưa gộp màn hình chọn ảnh (T-056)** cho tới khi Thợ Máy sửa và Lá Chắn kiểm lại (hoặc anh/chị quyết định chấp nhận rủi ro). Người dùng bình thường không gặp lỗi này; nó chỉ xảy ra khi máy đã có chương trình lạ đang chạy.

Ngoài ra có 4 lỗi nhỏ (Thấp): một test cũ chỉ viết cho Windows nên hỏng trên Mac/Linux; khi bị tráo thư mục thì app hiện cỡ file bên ngoài (không phải nội dung); trên ổ phân biệt hoa thường nháp có thể đổi sang ảnh khác tên gần giống (nhánh T-076 đã sửa); và trên Linux câu báo lỗi khi bị tráo thư mục ghi nhầm là "không có quyền".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_images_folders_t063.py` | Mới: 7 test qua (1 test chỉ chạy bằng người dùng thường), 5 test `xfail(strict=True)` ghi SL-T063-2 → 5 |
| `docs/team/reports/T-063-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng (`seo_app/**`, `app/**`), không sửa test có sẵn. Script thử tấn công nằm trong thư mục tạm của phiên, không commit (mô tả ở bước 3).

## Kết quả từng bước

### Bước 1 · Test T-048 trên Linux (`main` `400fa8c`)

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py -rs
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
collected 260 items
...
FAILED tests/test_images_folders.py::test_unreadable_subfolder_is_counted_not_fatal
  tests/test_images_folders.py:548: in fake_scandir
      if Path(path).name == "khoa":
  E   TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'int'
=========================== short test summary info ============================
SKIPPED [1] tests/test_images_folders.py:391: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:724: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:735: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:746: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:759: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:768: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:775: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:840: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:863: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:889: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:933: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:940: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders.py:949: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:101: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:123: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:145: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:171: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:196: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:315: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:332: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:349: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:395: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:712: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:723: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:862: junction chỉ có trên Windows
SKIPPED [2] tests/test_images_folders_soi_loi.py:874: junction chỉ có trên Windows
SKIPPED [2] tests/test_images_folders_soi_loi.py:902: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:934: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:947: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:969: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:1003: junction chỉ có trên Windows
SKIPPED [3] tests/test_images_folders_soi_loi.py:1117: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:1134: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:1148: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:1171: junction chỉ có trên Windows
SKIPPED [1] tests/test_images_folders_soi_loi.py:1182: junction chỉ có trên Windows
============= 1 failed, 218 passed, 40 skipped, 1 xfailed in 2.25s =============
```

- **6 test Mac/Linux đều chạy và qua** (`-v`): `test_odd_names_are_skipped_on_posix` (`:369`), `test_fifo_is_not_an_image` (`:382`), 4 test symlink `test_symlinked_dir_to_outside_is_refused` (`:788`), `test_symlinked_file_to_outside_is_refused` (`:798`), `test_symlinked_file_inside_root_is_refused` (`:808`), `test_resolve_check_alone_blocks_symlink_outside` (`:815`). Cả các test tên sai UTF-8 / surrogate của Soi Lỗi T-048 (`sl:238`, `:250`, `:256`) chạy với tên hỏng mã thật trên ext4 và qua.
- 40 bỏ qua **đều** là "junction chỉ có trên Windows". Không còn test nào bị bỏ qua vì "chỉ tạo được trên Mac/Linux". Tổng 260 = 218 + 40 + 1 + 1, khớp 260 test Lá Chắn T-048 đếm trên Windows.
- 1 xfail: R2-2 (`sl:1041`, đã biết từ T-048).
- **1 hỏng: SL-T063-1** (lỗi của test, không phải của app, xem mục Lỗi). Chạy bằng `nobody`: kết quả y hệt (225 qua khi tính cả file mới), nên không do quyền root.

### Bước 2 · Điều kiện Lá Chắn T-052, T-055, T-075 (`main`)

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_drafts_images.py \
    tests/test_soi_loi_t055.py tests/test_certifi_version.py -rs
=========================== short test summary info ============================
SKIPPED [1] tests/test_images_tags.py:1784: junction chỉ có trên Windows
SKIPPED [1] tests/test_soi_loi_t052.py:392: khóa file kiểu Windows (không chia sẻ) chỉ có trên Windows
SKIPPED [1] tests/test_soi_loi_t052.py:544: junction chỉ có trên Windows
SKIPPED [1] tests/test_drafts_images.py:621: junction chỉ có trên Windows
SKIPPED [2] tests/test_drafts_images.py:911: ổ phân biệt hoa thường: 'congai' là thư mục khác, không trỏ tới 'CongAI'
SKIPPED [1] tests/test_soi_loi_t055.py:383: ổ phân biệt hoa thường: tên khác hoa thường là file khác
SKIPPED [1] tests/test_soi_loi_t055.py:396: thuộc tính ẩn, tên ngắn 8.3 của Windows
SKIPPED [1] tests/test_soi_loi_t055.py:412: thuộc tính ẩn, tên ngắn 8.3 của Windows
SKIPPED [2] tests/test_soi_loi_t055.py:487: ổ phân biệt hoa thường: tên khác hoa thường là file khác
SKIPPED [1] tests/test_soi_loi_t055.py:501: ổ phân biệt hoa thường: tên khác hoa thường là file khác
SKIPPED [1] tests/test_soi_loi_t055.py:516: ổ phân biệt hoa thường: tên khác hoa thường là file khác
SKIPPED [1] tests/test_soi_loi_t055.py:802: ổ phân biệt hoa thường: nháp 'congai' không trỏ tới 'Congai'
SKIPPED [1] tests/test_soi_loi_t055.py:898: ổ phân biệt hoa thường: 'congai' là thư mục khác
SKIPPED [1] tests/test_soi_loi_t055.py:958: thuộc tính ẩn, tên ngắn 8.3 của Windows
SKIPPED [1] tests/test_soi_loi_t055.py:1017: ổ phân biệt hoa thường: 'congai' là thư mục khác
SKIPPED [1] tests/test_soi_loi_t055.py:1030: ổ phân biệt hoa thường: 'congai' là thư mục khác
=========== 894 passed, 18 skipped, 3 xfailed, 91 warnings in 15.48s ===========
```

- **0 hỏng.** Hai ca symlink của Lá Chắn T-052 (điều kiện 5) **chạy thật và qua**: `test_images_tags.py::test_symlink_at_file_path_is_replaced_without_touching_target` (`:1770`) và `test_soi_loi_t052.py::test_sl_t052_7_symlink_placed_after_first_use_does_not_write_outside` (`:529`). Ca symlink của T-055: `test_drafts_images.py::test_image_through_symlink_is_unavailable` (`:634`) chạy và qua.
- Ca chỉ chạy trên ổ phân biệt hoa thường (bị bỏ qua trên Windows) chạy và qua: `test_exact_folder_name_wins_on_case_sensitive_disk`, `test_single_case_insensitive_match_takes_real_name`, `test_unconfirmed_folder_name_is_unavailable[hai-ten-cung-khoa]`.
- 18 bỏ qua: 4 junction/khóa file Windows, 3 thuộc tính ẩn/8.3 Windows, 11 cần ổ **không** phân biệt hoa thường (Windows NTFS, Mac APFS): Linux không kiểm được, **chờ máy Mac** (điều kiện Lá Chắn T-055 số 4 về APFS).
- 3 xfail: SL-T055-4 (×2), SL-T055-5, đã biết; nhánh T-076 sửa (bước 4).
- `test_certifi_version.py`: 4 qua; `certifi` trong môi trường là **2026.10.19** (T-075).
- 91 cảnh báo: `DeprecationWarning` của `sqlite3` ở hàm giả trong test (`tests/test_images_tags.py:1900`, `:2060`: tham số tên `?1` truyền bằng tuple; Python 3.14 sẽ thành lỗi). Không thuộc app, ghi nhận.

### Bước 3 · Thử tấn công bằng script (thư mục tạm, không commit)

Script `t063_probe.py` (thư mục tạm của phiên): dựng cây thư mục giả trong `/tmp`, gọi `ImageLibrary` như app, kiểm: không có tên/nội dung ngoài gốc, mọi lỗi là `ImageFolderError` có câu không chứa `/tmp` hay đường dẫn tuyệt đối và không xích lỗi hệ điều hành. Chạy trên `main` và trên `team/T-076`, bằng **root** và bằng **`nobody`**.

| # | Ca thử | Kết quả `main` (root và `nobody`) |
|---|---|---|
| 1 | Symlink đặt sẵn trong gốc: thư mục → ngoài, file → ngoài, file → trong gốc, đích tương đối `../ngoai`, symlink gãy, symlink vòng `vong → vong`, symlink ở tầng sâu `album/lk` | **Đạt.** Quét không trả mục nào qua liên kết (đếm `links` = 6, cả cây = 7). Đọc, `stat_image`, xem thư mục qua từng liên kết: lỗi gọn "Đường dẫn đi qua liên kết tắt…". Ảnh thật vẫn đọc được |
| 2 | Thư mục gốc là symlink; gốc có tầng cha là symlink; gốc là symlink gãy | **Đạt.** Gốc symlink dùng được (thiết kế T-048), nhãn là tên khai báo (`anh-lien-ket`), đọc được ảnh; symlink **bên trong** gốc-symlink vẫn bị chặn. Gốc gãy: "Chưa thấy thư mục ảnh số 3…", không lộ đường dẫn; `repr` chỉ "ImageLibrary(3 thư mục)" |
| 3 | Tên sai UTF-8 thật trên ext4: `anh-\xff\xfe.jpg`, `\xed\xa0\x80.jpg`, `\xc3\x28.png`, thư mục `thu-muc-\xc3\x28/` có ảnh bên trong | **Đạt.** Chỉ còn `ok.jpg`; 4 tên lạ đếm `bad_names`; không đi vào thư mục tên hỏng; mọi tên trả về ghi được UTF-8; `ImageRef` dựng từ tên hỏng bị từ chối "Đường dẫn ảnh không hợp lệ." |
| 4 | Quyền đọc thật (`nobody`): thư mục `000`, `300` (chỉ đi qua), `600` (chỉ đọc danh sách), `500`; file `000`; gốc `000` | **Đạt.** Quét cả cây không hỏng: ảnh `khoa500/b.jpg`, `ok/a.jpg`, `unreadable` = 3. Xem `khoa000`, `khoa300`, gốc `000`: lỗi gọn "Không đọc được mục này…". Đọc file `000`: "Không mở được ảnh…". Ghi nhận (không phải lỗi): ảnh trong thư mục `300` không hiện khi quét nhưng `ImageRef` gõ sẵn đọc được (quyền "đi qua" của POSIX, vẫn trong gốc); `roots()` báo gốc `000` "dùng được" rồi xem mới báo lỗi. Chạy bằng root: root đọc được hết, đúng như mong đợi |
| 5 | Hai thư mục chỉ khác hoa thường (`CongAI/`, `congai/`), hai file `x/A.jpg`, `x/a.jpg` | `ImageLibrary` **đạt**: hiện đủ cả hai, mỗi `ImageRef` đọc ra đúng file của nó, `stat_image` trả đúng `ref`, tên gõ khác cả hai (`CONGAI`) bị từ chối. **`check_chosen_image(scanned=…)` hỏng: SL-T063-4** (nháp `congai/cong.png` thành `CongAI/cong.png`, nội dung ảnh AI; nháp `x/a.jpg` thành `x/A.jpg`). Không truyền `scanned` thì đúng |
| 6 | File đặc biệt tên `.jpg`: FIFO, socket UNIX, thiết bị ký tự (`/dev/null`, chỉ root tạo được) | **Đạt.** Đếm `other_files`; đọc: "Đây không phải là file ảnh.", không treo |
| 7 | Tên NFD trên ext4 (`Cổng-Tân-Phú.jpg` dạng NFD) | **Đạt.** Liệt kê nguyên dạng, đọc bằng `ref` liệt kê ra được; `ref` NFC: "Không tìm thấy…" (Linux phân biệt NFC/NFD; Mac thì không, **chờ máy Mac**) |
| 8a | Tiến trình khác tráo **thư mục** `x` ↔ symlink ra ngoài (`renameat2(RENAME_EXCHANGE)`, nguyên tử), app gọi liên tục `list_folder(0,"x")`, quét cả cây, `read_image_bytes`, `stat_image` trên `x/bi-mat.jpg` (trong gốc là ảnh mồi `DECOY`, ngoài gốc là `SECRET`, khác cỡ). 20 giây (root), 10 giây (`nobody`) | Liệt kê lọt tên: **0**/37.032 (cả cây: **0**). Câu lỗi lộ đường dẫn: **0**. **Đọc lọt nội dung ngoài gốc: 1.253/37.032 lần (root), 512/18.731 (`nobody`) → SL-T063-2.** `stat_image` trả cỡ file ngoài gốc: 3.095/37.032 → SL-T063-3 |
| 8b | Như 8a nhưng tráo **không nguyên tử** (đổi tên, tạo symlink, gỡ, trả tên; như Lá Chắn T-048 kiểu 4) | Liệt kê lọt: **0**. **Đọc lọt nội dung: 153/33.661 (root), 81/18.350 (`nobody`).** `stat_image` lọt cỡ: 1.482/33.661 |
| 8c | Tráo chính **file** `x/bi-mat.jpg` ↔ symlink ra ngoài (nguyên tử) | **Đạt.** Lọt tên 0, lọt nội dung **0**/25.281, lọt cỡ 0 (`O_NOFOLLOW` ở tầng cuối và `lstat` từng phần chặn được) |

Cùng script trên **`team/T-076`**: ca 1–4, 6, 7 như `main`; ca 5 **đạt hết** (T-076 sửa SL-T063-4); ca 8a: liệt kê lọt 0, **đọc lọt nội dung 1.062/35.125** (root), 634/16.256 (`nobody`), `stat_image` lọt cỡ 363/35.125 (giảm nhờ phép so định danh mới, chưa hết); ca 8b: đọc lọt 68/37.885, cỡ 21/37.885; ca 8c: 0.

### Bước 4 · Nhánh `team/T-076` (`006b13b`, worktree `/tmp/t076`, chỉ đọc)

```
$ cd /tmp/t076 && uv run pytest tests/test_images_folders.py tests/test_soi_loi_t076.py \
    tests/test_la_chan_t076.py tests/test_drafts_images.py tests/test_soi_loi_t055.py -rs
FAILED tests/test_images_folders.py::test_unreadable_subfolder_is_counted_not_fatal   (SL-T063-1, như main)
=========================== short test summary info ============================
(17 dòng "junction chỉ có trên Windows", tổng 20 test, lược bớt)
SKIPPED [1] tests/test_images_folders.py:1114: ổ phân biệt hoa thường: 'zz' không trỏ tới 'Zz'
SKIPPED [8] tests/test_soi_loi_t076.py:218: ổ phân biệt hoa thường: 'congai' là thư mục khác, không trỏ tới 'CongAI'
SKIPPED [4] tests/test_soi_loi_t076.py:331: ổ phân biệt hoa thường: 'ALBUM' không trỏ tới 'Album'
SKIPPED [4] tests/test_soi_loi_t076.py:366: ổ phân biệt hoa thường: 'ALBUM' không trỏ tới 'album'
SKIPPED [1] tests/test_soi_loi_t076.py:396: ổ phân biệt hoa thường: nháp 'congai' không trỏ tới 'Congai'
SKIPPED [1] tests/test_soi_loi_t076.py:449: ổ phân biệt hoa thường: 'congai' không trỏ tới 'CongAI'
SKIPPED [2] tests/test_soi_loi_t076.py:467: ổ phân biệt hoa thường
SKIPPED [1] tests/test_soi_loi_t076.py:493: ổ phân biệt hoa thường: cần ổ tìm tên không phân biệt hoa thường
SKIPPED [10] tests/test_la_chan_t076.py:92-167: chỉ cách lấy tên của Windows dùng resolve; Mac/Linux xem thư mục cha
SKIPPED [8] tests/test_drafts_images.py:941/964/990: ổ phân biệt hoa thường: 'congai' là thư mục khác, …
SKIPPED [12] tests/test_soi_loi_t055.py:383-1018: ổ phân biệt hoa thường … / thuộc tính ẩn, tên ngắn 8.3 của Windows
================== 1 failed, 484 passed, 72 skipped in 7.09s ===================
```

| File | Qua | Bỏ qua | Hỏng |
|---|---|---|---|
| `test_images_folders.py` | 160 | 20 (19 junction, 1 cần ổ không phân biệt hoa thường) | 1 (SL-T063-1) |
| `test_soi_loi_t076.py` | 25 | 21 (cần ổ không phân biệt hoa thường) | 0 |
| `test_la_chan_t076.py` | 0 | 10 (cách lấy tên của Windows) | 0 |
| `test_drafts_images.py` | 180 | 9 | 0 |
| `test_soi_loi_t055.py` | 119 | 12 | 0 (T-076 đã gỡ 3 xfail SL-T055-4, -5) |

- **Phần `fd` của `_listed_names` với symlink thật chạy và qua:** `test_soi_loi_t076.py::test_link_swapped_in_after_path_check` 4 ca "tên đúng" (`he-dieu-hanh-…`, `xem-thu-muc-cha-…` × `stat_image`/`list_folder`): ngay sau khi kiểm đường đi, thư mục bị đổi thành symlink ra ngoài thì `openat(…, O_NOFOLLOW)` từ chối, câu báo không có "ngoai". Bốn test symlink T-048 cũng qua trên nhánh này.
- Các ca "khác hoa thường" của T-076 (đúng phần sửa LC-T055-1) **cần ổ không phân biệt hoa thường** nên Linux không kiểm được: **chờ máy Mac** (điều kiện Lá Chắn T-076 số 3).
- Chạy thêm file mới của tôi trên mã T-076: SL-T063-2, -3, -5 vẫn `xfail`; **SL-T063-4 thành XPASS(strict)** (T-076 đã sửa).

### Bước 5 · Toàn bộ test và ruff (`main` `400fa8c`)

```
$ uv run pytest -q -rs
1 failed, 10528 passed, 73 skipped, 90 xfailed, 111 warnings in 449.02s (0:07:29)
FAILED tests/test_images_folders.py::test_unreadable_subfolder_is_counted_not_fatal   (SL-T063-1)

$ uv run ruff check .
All checks passed!
```

73 bỏ qua: 43 junction, 9 chế độ chia sẻ file Windows, 1 khóa file Windows, 3 thuộc tính ẩn/8.3, 11 cần ổ không phân biệt hoa thường, 2 "máy vẫn ghi được file chỉ đọc (root)", 4 IPv6 (cloud không có IPv6). Cảnh báo: `DeprecationWarning` `sqlite3` trong test (như bước 2) và 1 `UserWarning` Pydantic có từ trước.

Nhánh `team/T-063` (thêm file test mới): kết quả ở mục "Bằng chứng".

### Bước 6 · Phần chỉ kiểm được trên Mac: **chưa kiểm, chờ máy Mac**

- Cờ ẩn `UF_HIDDEN` (`folders.py:68`, `_is_hidden_stat`): Linux không có `st_flags`.
- APFS không phân biệt hoa thường: 11 test ở bước 2, 39 test ở bước 4 tự bỏ qua trên Linux.
- Tên NFD thật (APFS coi NFC và NFD là một tên): bước 3 ca 7 chỉ cho thấy Linux phân biệt hai dạng.
- Google Drive for Desktop của Mac (đo `stat_image`, nháp nhiều ảnh: điều kiện Lá Chắn T-076 số 3).
- Mã lỗi của macOS cho `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink (SL-T063-5): test SL-T063-5 **không** đánh `xfail` trên Mac nên chạy trên Mac sẽ cho biết.
- SL-T063-2 trên Mac: cùng đoạn code, macOS có đổi chỗ nguyên tử (`renamex_np(RENAME_SWAP)`); **suy luận** là cũng bị, chưa chạy.

## Lỗi phát hiện

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T063-2 | **Cao** (bảng `security.md` mục 3: "đọc được file ngoài thư mục ảnh") | Thư mục con bị tráo thành symlink **hai lần** (lúc `lstat` mục cuối và lúc `open`) thì `read_image_bytes` trả **nội dung file ngoài gốc** | `folders.py:487` (`lstat` theo đường dẫn, đi xuyên tầng giữa), `:501`/`:508` (`resolve` lúc thư mục là thật), `:636` (`os.open(path)`: `O_NOFOLLOW` chỉ chặn tầng cuối), `:643-644` (so định danh với chính `lstat` đã đi xuyên nên khớp) | (1) Chắc chắn: `tests/test_images_folders_t063.py::test_sl_t063_2_…` (giả kẻ tấn công thắng hai lần tráo). (2) Thật: bước 3 ca 8a/8b, một tiến trình riêng tráo liên tục; lọt sau vài giây, cả khi app chạy bằng người dùng thường | Lỗi gọn hoặc ra ảnh mồi; không bao giờ ra nội dung ngoài gốc (F1) | Trả `b"…SECRET-NGOAI-GOC"`. Còn nguyên trên `team/T-076` (T-076 không đụng đường đọc) |
| SL-T063-1 | Thấp (lỗi của test) | `test_unreadable_subfolder_is_counted_not_fatal` giả `os.scandir` bằng `Path(path).name`; trên Mac/Linux app quét bằng `os.scandir(fd)` nên test hỏng `TypeError` trước khi kiểm được gì. Chưa từng chạy ngoài Windows | `tests/test_images_folders.py:548` | `uv run pytest tests/test_images_folders.py -k unreadable_subfolder` trên Linux | Qua (app xử lý đúng: bản viết lại chạy được mọi máy `test_unreadable_subfolder_is_counted_when_scandir_gets_fd` qua; quyền thật bằng `nobody` qua) | Hỏng → `uv run pytest` không 0 hỏng trên Mac/Linux |
| SL-T063-3 | Thấp | Như SL-T063-2 nhưng ở `stat_image`: trả **cỡ, giờ sửa** của file ngoài gốc cùng tên (không phải nội dung) | `folders.py:487`, `:621` | `test_sl_t063_3_…`; bước 3 ca 8a (3.095/37.032), 8b | Lỗi gọn hoặc số liệu của ảnh trong gốc | Cỡ của file ngoài gốc. T-076 giảm (363/35.125) nhưng chưa hết: lần `lstat` kiểm lại (`folders.py:607` trên T-076) cũng đi theo đường dẫn |
| SL-T063-4 | Thấp | Trên ổ **phân biệt hoa thường**, `check_chosen_image(scanned=…)` đổi ảnh nháp sang **file khác** chỉ khác hoa thường (khóa `casefold` + `setdefault` giữ mục đầu) | `drafts.py:886`, `:903-905` | `test_sl_t063_4_…` (2 ca); bước 3 ca 5 | Giữ đúng file đã chọn | `congai/cong.png` → `CongAI/cong.png` (ảnh khác, thành ảnh AI); `x/a.jpg` → `x/A.jpg`. Chỉ xảy ra trên Linux hay Mac định dạng phân biệt hoa thường. **Đã sửa trên `team/T-076`** |
| SL-T063-5 | Thấp | Linux trả `ENOTDIR` (không phải `ELOOP`) cho `openat(O_DIRECTORY \| O_NOFOLLOW)` trên symlink, nên thư mục bị tráo thành symlink bị báo "**Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)**" và đếm vào `unreadable`, không vào `links`. Vẫn an toàn (không đọc qua liên kết), chỉ sai câu báo và số đếm | `folders.py:744` (`NotADirectoryError` → `_MSG_UNREADABLE`), `:746` (chú thích "ELOOP"); trên T-076 còn `_listed_names` `:652-654` | `test_sl_t063_5_…`; thử trực tiếp: `os.open("l", O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW, dir_fd=…)` → `NotADirectoryError 20`, bỏ `O_DIRECTORY` → `ELOOP 40` | Đếm `links`, báo "vừa bị thay đổi"/"liên kết tắt" | Đếm `unreadable`, báo "không có quyền…" |

Không có lỗi Nghiêm trọng. Mọi câu lỗi trong mọi ca (12 lượt thử tráo trên `main` và T-076, tổng 287.821 vòng, mỗi vòng 4 lần gọi): **0 lần lộ đường dẫn**, 0 lỗi lạ ngoài `ImageFolderError`.

### Vì sao SL-T063-2 đề xuất Cao

- Lá Chắn T-048 xếp LC-T048-2/-3 (lọt **tên**) mức Thấp vì "nội dung vẫn bị chặn, đọc nội dung lọt 0/11.192". Trên Linux điều đó không còn đúng: lọt **nội dung**.
- Điều kiện khai thác giống LC-T048-2: phải có chương trình đang chạy trên máy, có quyền ghi vào một thư mục con của thư mục ảnh, tráo đúng lúc người dùng xem/chọn ảnh. Google Drive không đồng bộ symlink, USB có symlink đặt sẵn thì bị chặn, nên không có đường khai thác từ xa.
- Hậu quả nếu khai thác được: ảnh xem trước, ảnh gửi AI viết alt và ảnh tải lên thư viện Media của WordPress (file Media có đường dẫn công khai dù bài là nháp) là một file khác trên máy mà người dùng không chọn (phải là ảnh thì Pillow mới mở được ở bước T-049). Trên máy dùng chung nhiều tài khoản (Mac), tài khoản khác có quyền ghi vào thư mục ảnh dùng chung có thể làm app (chạy bằng quyền chủ máy) đọc file mà tài khoản đó không tự đọc được.
- Lá Chắn có thể xét hạ mức theo mô hình đe dọa (như LC-T048-2); khi đó cần chủ dự án ghi sổ rủi ro.

## Ghi nhận (không phải lỗi)

- Thư mục chỉ có quyền "đi qua" (`300`): quét không thấy ảnh nhưng `ImageRef` gõ sẵn đọc được (đúng luật quyền POSIX, vẫn trong gốc). Trên T-076, `stat_image` cần đọc danh sách thư mục cha nên ảnh đó báo lỗi ở `stat_image` mà `read_image_bytes` vẫn đọc được. Không ảnh hưởng người dùng.
- `roots()` báo gốc không có quyền đọc (`000`) là "dùng được", lỗi chỉ hiện khi mở. Giao diện T-056 nên hiện câu lỗi của `list_folder`.
- Cloud chạy Python 3.12.3, Windows 3.12.15: khác bản vá, không thấy khác hành vi trong các test này.
- Test dùng tham số `?1` của `sqlite3` với tuple (`tests/test_images_tags.py:1900`, `:2060`): Python 3.14 sẽ báo lỗi.

## Bằng chứng

```
$ uv run pytest tests/test_images_folders_t063.py -v -rsx            # main, root
6 passed, 1 skipped, 5 xfailed
  SKIPPED test_real_posix_permissions_are_counted_not_fatal: cần quyền POSIX thật và người dùng thường

$ setpriv --reuid=65534 --regid=65534 --clear-groups .venv/bin/python -m pytest \
    tests/test_images_folders_t063.py -k "permissions or unreadable" -v -p no:cacheprovider --basetemp=…
test_unreadable_subfolder_is_counted_when_scandir_gets_fd PASSED
test_real_posix_permissions_are_counted_not_fatal PASSED

$ uv run pytest tests/test_images_folders_t063.py --runxfail          # xfail hỏng đúng chỗ mong đợi
test_sl_t063_5: assert (0, 1) == (1, 0)                               # (links, unreadable)
test_sl_t063_2: AssertionError: đọc được nội dung file ngoài thư mục ảnh
test_sl_t063_3: AssertionError: trả cỡ của file ngoài thư mục ảnh
test_sl_t063_4[thu-muc…]: assert 'CongAI/cong.png' == 'congai/cong.png'
test_sl_t063_4[file…]:    assert 'x/A.jpg' == 'x/a.jpg'

$ (mã T-076) uv run pytest <file mới> -rsx
2 failed (SL-T063-4 ×2: XPASS(strict)), 6 passed, 1 skipped, 3 xfailed

$ uv run pytest -q -rs                                                 # nhánh team/T-063
1 failed, 10534 passed, 74 skipped, 95 xfailed, 118 warnings in 417.81s (0:06:57)
FAILED tests/test_images_folders.py::test_unreadable_subfolder_is_counted_not_fatal   (SL-T063-1)
# so với main: +6 qua, +1 bỏ qua (test quyền thật, chạy bằng root), +5 xfail (SL-T063-2 → 5); cảnh báo thêm đều là DeprecationWarning sqlite3 của tests/test_images_tags.py, không từ file mới

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_images_folders_t063.py
1 file already formatted
```

## Đối chiếu tiêu chí xong

- [x] 6 test Mac/Linux chạy thật và qua (bước 1: `test:369`, `:382`, `:788`, `:798`, `:808`, `:815` PASSED; 40 bỏ qua đều là junction Windows)
- [ ] `uv run pytest` 0 hỏng trên máy kiểm: **1 hỏng** (SL-T063-1, lỗi của test cũ chỉ viết cho Windows; app xử lý đúng). `uv run ruff check .` sạch
- [x] Báo cáo nộp tại `docs/team/reports/T-063-soi-loi.md`, ghi rõ hệ điều hành, bản Python
- [x] Điều kiện Lá Chắn T-052 (2 ca symlink chạy thật), T-055 (symlink; phần APFS/NFD chờ Mac), T-076 (phần `fd` của `_listed_names`, symlink thật; phần hoa thường/NFD/Drive chờ Mac), T-075 (`certifi` 2026.10.19)
- [ ] Thử thêm: "không đọc được nội dung ngoài gốc" **không đạt** khi thư mục bị tráo (SL-T063-2); câu lỗi không lộ đường dẫn: đạt

## Kết luận phần Linux: **KHÔNG ĐẠT**

Nhánh quét thư mục của Mac/Linux (`_scan_by_fd`, `openat` + `O_NOFOLLOW`, `os.scandir(fd)`) **đạt**: chạy thật, không lọt tên ngoài gốc kể cả khi bị tráo liên tục; tên sai UTF-8, quyền POSIX, symlink đặt sẵn, gốc là symlink đều đúng; câu lỗi sạch. Nhưng đường **đọc ảnh** (`read_image_bytes`, dùng chung mọi hệ điều hành) có SL-T063-2 (đề xuất **Cao**), nên điều kiện LC-T048-1 ("có lỗi thì Thợ Máy sửa và Lá Chắn kiểm lại phần đó") **chưa xong**: chưa nên gộp T-056 cho tới khi SL-T063-2 được sửa và Lá Chắn kiểm lại, hoặc Lá Chắn hạ mức và chủ dự án ghi sổ rủi ro.

## Rủi ro và điểm cần chú ý

- **SL-T063-4 và nhánh T-076:** test SL-T063-4 là `xfail(strict=True)` trên `main`; T-076 sửa lỗi này nên **gộp T-076 thì phải xóa dấu `xfail` của SL-T063-4** (`tests/test_images_folders_t063.py`). Trên Windows test này **tự bỏ qua** (NTFS không phân biệt hoa thường) nên lần chạy toàn bộ trên Windows **không** báo; chỉ máy Linux/Mac phân biệt hoa thường mới thấy XPASS. Gộp theo thứ tự nào cũng phải làm việc này.
- Test SL-T063-2/-3 giả kẻ tấn công "luôn thắng" bằng cách thay `os.lstat`/`os.open` của module `os` trong lúc test (như các test có sẵn thay `os.scandir`); chỉ tác động lên đường dẫn tận cùng là `bi-mat.jpg`. Cách sửa đúng (bên dưới) làm hai test này qua; cách sửa chỉ thu hẹp khe (kiểm lại thêm một lần theo đường dẫn) sẽ không qua, đó là chủ ý.
- Test SL-T063-2, -3, -5 và các test symlink mới chỉ chạy trên Mac/Linux (`posix_only`). Chưa thử phiên bản junction trên Windows (xem Đề xuất).
- `test_real_posix_permissions_are_counted_not_fatal` tự bỏ qua khi chạy bằng root (cloud) và trên Windows; tôi đã chạy nó bằng `nobody`.

## Đề xuất

1. **Thợ Máy (sửa SL-T063-2, -3):** trên Mac/Linux, `read_image_bytes` và `stat_image` không đi theo đường dẫn mà mở thư mục cha bằng `_posix_open_dir(gốc, parts[:-1])` (đã có, `O_NOFOLLOW` từng tầng), rồi `os.stat(tên, dir_fd=fd, follow_symlinks=False)` và `os.open(tên, O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC, dir_fd=fd)`, so `fstat` với `stat` đó. Không còn tầng nào bị đi xuyên. Windows: hỏi chính handle file vừa mở đường dẫn thật (`GetFinalPathNameByHandleW`, đã có `_win_final_path`) và bắt buộc nằm trong gốc, hoặc giữ handle các thư mục cha như `_scan_held`. Sửa xong bỏ `xfail` SL-T063-2, -3.
2. **Lá Chắn:** xét mức SL-T063-2; thử bản Windows của `test_sl_t063_2_…` với junction (`_winapi.CreateJunction`) và cách tráo nhanh (đổi tên thư mục ↔ junction liên tục), vì đường đọc Windows dùng cùng logic (`_resolve_inside` + `os.open(path)`).
3. **SL-T063-1:** cho phép sửa test cũ `tests/test_images_folders.py:548` (phiếu này chỉ cho thêm test): nhận thư mục khóa theo định danh như `test_unreadable_subfolder_is_counted_when_scandir_gets_fd` (`os.fstat(fd)` nếu là số, `os.stat(path)` nếu là đường dẫn).
4. **SL-T063-5:** `_scan_by_fd` (và `_listed_names` của T-076) coi `NotADirectoryError` khi mở tầng `parts` là thư mục bị tráo (`_ChangedError`), vì `_resolve_inside` vừa xác nhận đó là thư mục; sửa chú thích "ELOOP".
5. **SL-T063-4:** đã sửa ở T-076; khi gộp T-076 nhớ bỏ `xfail` (mục Rủi ro).
6. Khi có máy Mac: chạy `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_drafts_images.py tests/test_soi_loi_t055.py -rs` (thêm `tests/test_soi_loi_t076.py`, `tests/test_la_chan_t076.py` nếu T-076 đã gộp) và các mục ở bước 6.

## Câu hỏi cho chủ dự án

Không có câu hỏi trực tiếp. Nếu Lá Chắn giữ mức Cao cho SL-T063-2 thì T-056 chờ phiếu sửa; nếu Lá Chắn hạ mức thì Chỉ Huy hỏi anh/chị có ghi sổ rủi ro không.

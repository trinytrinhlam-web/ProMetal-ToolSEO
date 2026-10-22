# Báo cáo T-079 · Chạy kiểm tra trên Linux thật (đọc ảnh bằng thư mục đã mở từng tầng) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · phiên Claude Code trên cloud |
| Phiếu | [T-079](../tickets/T-079-doc-anh-bang-fd-tung-tang.md) (lượt chạy lại trên Linux mà Thợ Máy đề nghị) |
| Ngày nộp | 2026-10-22 |
| Máy kiểm | **Ubuntu 24.04.5 LTS**, nhân Linux 6.18.44 (x86_64, 4 CPU), thư mục tạm trên ổ **ext4** (phân biệt hoa thường, phân biệt NFC/NFD). **Python 3.12.3** (môi trường `.venv` do `uv sync` tạo; máy Windows của đội: 3.12.15), **uv 0.11.32**, pytest 9.1.1, ruff 0.16.10. Phiên chạy bằng **root**; phần quyền đọc thật và mọi lượt tráo chạy thêm bằng người dùng thường **`nobody`** (uid 65534) qua `setpriv`. `fs.protected_symlinks=0`, `fs.protected_hardlinks=1` |
| Mã nguồn | Nhánh `team/T-079` tại **`c7b2394`** (nhánh `team/T-079-linux` tách từ đây). Đối chứng: `main` tại **`fa2cc39`** (bản ngay trước T-079; worktree tạm, chỉ đọc) |
| Nhánh nộp | `team/T-079-linux` (không push lên `team/T-079`) |
| Kết quả | Hoàn thành. **Kết luận phần Linux: ĐẠT** (0 lọt nội dung, 0 lọt cỡ, 0 lọt tên; 1 lỗi mới mức Thấp, không chặn: SL-T079-L-1). Phần chỉ có trên Mac: chưa kiểm, chờ máy Mac |

## Tóm tắt (cho chủ dự án)

Lỗ hổng lần trước tìm ra trên Linux (một chương trình lạ liên tục tráo thư mục ảnh thành "lối tắt" thì app đọc nhầm file nằm ngoài thư mục ảnh) **đã được vá thật**. Tôi dựng lại đúng cách tấn công lần trước, cho app đọc và xem ảnh **hơn 1,3 triệu lượt** trong lúc bị tráo liên tục (hơn 50 triệu lần tráo), bằng cả tài khoản quản trị lẫn tài khoản thường: **không lần nào đọc được nội dung hay số liệu của file bên ngoài**, câu báo lỗi không lần nào lộ đường dẫn trên máy. Cùng cách thử đó trên bản cũ (trước khi vá) lọt hàng nghìn lần, nên tôi chắc cách thử của mình bắt được lỗi khi lỗi còn.

Mọi test liên quan chạy qua trên Linux (0 hỏng), toàn bộ bộ test cũng qua. Dùng bình thường không thấy gì khác, tốc độ đọc ảnh như cũ. Chỉ có một khác biệt nhỏ đúng như Thợ Máy báo trước: thư mục bị khóa quyền kiểu "chỉ được đi qua" nay không đọc được ảnh bên trong (chặt hơn, an toàn hơn).

Tôi tìm thêm **một lỗi nhỏ (Thấp), không chặn việc gộp**: khi đang bị tráo, đôi khi app báo "không có quyền hoặc ổ đĩa vừa bị ngắt" thay vì "vừa bị thay đổi, hãy thử lại". Chỉ sai câu chữ, vẫn an toàn, và chỉ xảy ra khi máy đang bị tấn công. Phần chỉ kiểm được trên máy Mac vẫn chờ máy Mac.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t079_linux.py` | Mới: 9 test qua (khóa tính chất "thư mục đã mở vẫn là thư mục thật dù tên bị tráo", tầng trên và tầng giữa, đọc và `stat`; không rò fd; một lượt tráo thật 1,5 giây bằng tiến trình riêng, chỉ Linux) + 3 test `xfail(strict=True)` ghi **SL-T079-L-1** |
| `docs/team/reports/T-079-soi-loi-linux.md` | Báo cáo này |

Không sửa code ứng dụng (`seo_app/**`, `app/**`), không sửa test có sẵn. Script thử tấn công (`t079_probe.py`, `t079_static.py`, `t079_perf.py`, `t079_origin.py`, `t079_emfile.py`) nằm trong thư mục tạm của phiên, không commit; cách làm ghi ở từng bước.

## Kết quả từng bước

### Bước 1 · Test liên quan trên Linux (`team/T-079` `c7b2394`)

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py \
    tests/test_images_folders_t063.py tests/test_drafts_images.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py -rsxX
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
...
XFAIL tests/test_images_folders_soi_loi.py::test_r2_exact_budget_with_pending_empty_subfolder_is_not_truncated
  - R2-2 (soi-loi): quét cả cây, vừa đủ max_entries mục mà còn thư mục con RỖNG chờ quét thì vẫn báo 'còn nữa' (phần còn lại của L4)
========== 1155 passed, 126 skipped, 1 xfailed, 82 warnings in 14.86s ==========
```

- **0 hỏng, 0 XPASS.** 1 xfail còn lại là R2-2 (T-048, đã biết, không thuộc phiếu này).
- **Các test SL-T063 đều chạy và qua** (`tests/test_images_folders_t063.py -v`, không còn `xfail`):

```
test_sl_t063_5_swapped_folder_is_reported_as_link_not_unreadable PASSED
test_sl_t063_2_folder_swapped_twice_cannot_read_outside_content PASSED
test_sl_t063_3_folder_swapped_during_stat_gives_no_outside_size PASSED
test_sl_t063_4_scanned_case_sibling_does_not_replace_draft_image[thu-muc-khac-hoa-thuong] PASSED
test_sl_t063_4_scanned_case_sibling_does_not_replace_draft_image[file-khac-hoa-thuong] PASSED
test_sl_t063_2_windows_swap_cannot_read_outside_content SKIPPED (cách tráo junction của Windows)
test_sl_t063_3_windows_swap_gives_no_outside_size SKIPPED (cách tráo junction của Windows)
11 passed, 3 skipped
```

  SL-T063-1 (`tests/test_images_folders.py::test_unreadable_subfolder_is_counted_not_fatal`, bản viết lại) **PASSED**. SL-T063-4 chạy thật trên ext4 phân biệt hoa thường: **PASSED, không XPASS(strict)** (dấu `xfail` đã được Thợ Máy xóa đúng).
- **5 test Mac/Linux mới của Thợ Máy chạy thật và qua:** `test_posix_image_is_opened_inside_the_opened_folder`, `test_posix_folder_swapped_before_opening_levels_is_refused` ×2, `test_posix_file_swapped_to_symlink_after_folder_is_opened` ×2; cùng `test_open_error_message` ×4, `test_read_detects_swapped_file`, `test_entry_swapped_during_name_lookup_is_refused` ×6.
- **Chạy bằng `nobody`** (9 file, gồm cả file mới của tôi lúc đó có 9 test): `1165 passed, 125 skipped, 1 xfailed`, 0 hỏng. Thêm 1 qua so với root là `test_real_posix_permissions_are_counted_not_fatal` (tự bỏ qua khi chạy bằng root).
- 126 bỏ qua (root): junction / cách hỏi tên / thuộc tính ẩn, 8.3 của Windows, và các ca cần ổ **không** phân biệt hoa thường (Windows NTFS, Mac APFS): Linux không kiểm được.

### Bước 2 · Dựng lại cách tấn công của T-063 (bước 3 ca 8a/8b) và thêm ca

Script `t079_probe.py` (thư mục tạm): dựng cây giả trong thư mục tạm, gốc `anh/` có ảnh mồi `x/bi-mat.jpg` (8 byte), ngoài gốc `ngoai/bi-mat.jpg` (220 byte, giờ sửa khác) và `ngoai/chi-ngoai.jpg` (tên chỉ có ngoài gốc). Một **tiến trình riêng** tráo liên tục; app gọi liên tục `list_folder(0, "x")`, `read_image_bytes`, `stat_image` trên `x/bi-mat.jpg` (lượt 4 luồng thêm quét cả cây mỗi 10 vòng). Đếm: **lọt tên** (`chi-ngoai.jpg` xuất hiện), **lọt nội dung** (bytes = file ngoài), **lọt cỡ** (cỡ, giờ sửa hoặc `file_id` = file ngoài), đọc qua liên kết tới file khác trong gốc (ca 8f), câu lỗi chứa đường dẫn thư mục tạm / `/tmp` / `ngoai` / `SECRET`, lỗi không phải `ImageFolderError`, lỗi xích lỗi hệ điều hành, số fd trước/sau. Chạy trên **T-079** và trên **bản cũ `fa2cc39`** (đối chứng), bằng **root** và **`nobody`**.

| Ca | Cách tráo |
|---|---|
| 8a | Thư mục `x` ↔ symlink ra ngoài, **nguyên tử** (`renameat2(RENAME_EXCHANGE)`), như T-063 |
| 8b | `x` ↔ symlink ra ngoài, **không nguyên tử** (đổi tên đi, tạo symlink, gỡ, trả tên), như T-063; thêm 2 biến thể giữ mỗi trạng thái 20 µs và 200 µs |
| 8c | Chính file `x/bi-mat.jpg` ↔ symlink ra ngoài, nguyên tử |
| 8d | Tầng trên `a` (ảnh ở `a/b/bi-mat.jpg`) ↔ symlink ra ngoài, nguyên tử (mới) |
| 8e | Tầng giữa `a/b` ↔ symlink ra ngoài, nguyên tử (mới) |
| 8f | `x` ↔ symlink tới thư mục **khác trong gốc** (`y/`, ảnh khác), nguyên tử (mới: đọc qua liên kết dù không ra ngoài gốc) |
| 8g | `x` ↔ **thư mục thật** ở ngoài gốc (không phải symlink), nguyên tử (mới, xem "Ghi nhận") |

**Kết quả (mỗi vòng = 1 lần `list_folder` + 1 lần `read_image_bytes` + 1 lần `stat_image`):**

| Người chạy | Ca | Thời gian | **T-079**: vòng · lọt nội dung · lọt cỡ · lọt tên | **Bản cũ `fa2cc39`**: vòng · lọt nội dung · lọt cỡ · lọt tên |
|---|---|---|---|---|
| root | 8a | 20 s | 63.850 · **0** · **0** · 0 | 68.215 · **2.717** · 1.457 · 0 |
| root | 8b | 20 s | 142.006 · **0** · **0** · 0 | 138.714 · 1 · 0 · 0 |
| root | 8b, giữ 20 µs | 20 s | 100.329 · **0** · **0** · 0 | 100.082 · 0 · 0 · 0 |
| root | 8b, giữ 200 µs | 20 s | 102.672 · **0** · **0** · 0 | 103.843 · 0 · 0 · 0 |
| root | 8c | 20 s | 45.981 · **0** · **0** · 0 | 45.370 · 0 · 0 · 0 |
| root | 8d (tầng trên) | 20 s | 60.318 · **0** · **0** · 0 | 60.524 · **2.599** · 818 · 0 |
| root | 8e (tầng giữa) | 20 s | 58.569 · **0** · **0** · 0 | 56.776 · **1.729** · 873 · 0 |
| root | 8f (liên kết trong gốc) | 20 s | 63.350 · đọc qua liên kết **0**, `stat` qua liên kết **0** | 61.261 · đọc qua liên kết **2.094**, `stat` 1.065 |
| root | 8a, 4 luồng app + quét cả cây | 30 s | 23.067 (+2.305 lần quét cả cây) · **0** · **0** · 0 | (không chạy) |
| root | 8b, 4 luồng app + quét cả cây | 30 s | 38.788 (+3.878 lần quét cả cây) · **0** · **0** · 0 | (không chạy) |
| `nobody` | 8a | 20 s (cũ: 10 s) | 76.056 · **0** · **0** · 0 | 37.710 · **1.219** · 702 · 0 |
| `nobody` | 8b | 20 s (cũ: 10 s) | 143.223 · **0** · **0** · 0 | 64.221 · 6 · 1 · 0 |
| `nobody` | 8b, giữ 20 µs | 20 s | 75.363 · **0** · **0** · 0 | 78.419 · 3 · 1 · 0 |
| `nobody` | 8b, giữ 200 µs | 20 s | 99.241 · **0** · **0** · 0 | 98.118 · 0 · 0 · 0 |
| `nobody` | 8c / 8d / 8e / 8f | 20 s mỗi ca | 45.995 / 72.448 / 64.909 / 73.494 · **0** · **0** · 0 (8f: đọc qua liên kết 0) | (không chạy) |

- **Tổng trên T-079 (ca 8a–8f): 1.349.659 vòng** (root 698.930, `nobody` 650.729), khoảng 4 triệu lần gọi, 54 triệu lần tráo: **0 lọt nội dung, 0 lọt cỡ/giờ sửa/định danh, 0 lọt tên, 0 lần đọc qua liên kết**. Câu lỗi lộ đường dẫn: **0**. Lỗi lạ (không phải `ImageFolderError`): **0**. Lỗi xích lỗi hệ điều hành: **0**. Số fd sau mỗi lượt bằng trước (4 = 4), sau khi dừng tráo app vẫn đọc đúng ảnh mồi.
- **So với T-063:** T-063 đo lọt nội dung 1.062/35.125 vòng (root, mã T-076) và 634/16.256 (`nobody`). Cùng cách tráo trên bản cũ ở máy này lọt 2.717/68.215 (root) và 1.219/37.710 (`nobody`), cùng tỉ lệ cỡ 3–4 %, nên cách thử của tôi tương đương lần trước và **bắt được lỗi khi lỗi còn**. Trên T-079: **0/63.850** (root) và **0/76.056** (`nobody`).
- Ca 8b (không nguyên tử): trên máy này bản cũ cũng chỉ lọt rải rác (tổng 10 lần qua 6 lượt), ít hơn T-063 (153/33.661): thư mục bị tráo kiểu này phần lớn thời gian "không tồn tại", app chỉ báo "Không tìm thấy…". T-079: 0 qua 7 lượt (hơn 700.000 vòng).
- Ca 8d, 8e (mới): bản cũ lọt cả khi tầng bị tráo là tầng trên hay tầng giữa của đường dẫn 3 tầng; T-079 không. Ca 8f (mới): bản cũ đọc **qua liên kết** sang ảnh khác trong gốc 2.094 lần (trái nguyên tắc "app không đọc qua liên kết" của T-048, dù không ra ngoài gốc); T-079: 0.
- Câu báo khi bị tráo trên T-079 (ca 8a, root, 20 s): "Đường dẫn đi qua liên kết tắt…", "Đường dẫn nằm ngoài thư mục ảnh được phép.", "Thư mục vừa bị thay đổi…", "Ảnh vừa bị thay đổi…", và "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." (câu cuối là **SL-T079-L-1**, xem mục Lỗi).

### Bước 3 · Thử thêm (đặt sẵn, không tráo), so với bản cũ

Script `t079_static.py` (thư mục tạm) chạy cùng các ca trên T-079 và `fa2cc39`, bằng root và `nobody`, ghi từng kết quả (`ok:…` / câu lỗi), kiểm câu lỗi không chứa đường dẫn thư mục tạm, `/tmp`, `ngoai`, `SECRET`, không xích lỗi, không rò fd sau mỗi lần gọi. **0 vi phạm ở cả 4 lượt.** So từng dòng kết quả T-079 với bản cũ: **giống hệt**, trừ 2 điểm đã biết trước (dưới bảng).

| # | Ca | Kết quả T-079 (root và `nobody`) |
|---|---|---|
| 1 | Symlink đặt sẵn: thư mục → ngoài, file → ngoài, file → trong gốc, đích tương đối `../ngoai`, symlink gãy, vòng `vong → vong`, tầng sâu `album/lk`, đi tiếp qua `album/lk/trong/b.jpg` | **Đạt.** Quét không trả mục nào qua liên kết (`links` = 7). Xem/đọc/`stat` qua từng liên kết: "Đường dẫn đi qua liên kết tắt (symlink/junction), app không đọc qua liên kết." Ảnh thật vẫn đọc được |
| 2 | Gốc là symlink; gốc có tầng cha là symlink; gốc là symlink gãy | **Đạt.** Gốc symlink dùng được (thiết kế T-048), nhãn là tên khai báo, đọc/`stat` được ảnh kể cả tầng con; symlink **bên trong** gốc-symlink bị chặn. Gốc gãy: "Chưa thấy thư mục ảnh số 3…", không lộ đường dẫn; `repr` = "ImageLibrary(3 thư mục)" |
| 3 | Tên sai UTF-8 thật trên ext4 (`anh-\xff\xfe.jpg`, `\xed\xa0\x80.jpg`, `\xc3\x28.png`, thư mục `thu-muc-\xc3\x28/`) | **Đạt.** Chỉ còn `ok.jpg`, `bad_names` = 4, không đi vào thư mục tên hỏng; `ImageRef` dựng từ tên hỏng: "Đường dẫn ảnh không hợp lệ." |
| 4 | Quyền thật (`nobody`): thư mục `000`, `300` (chỉ đi qua), `600`, `500`; file `000`; gốc `000` | **Đạt.** Quét cả cây không hỏng (`unreadable` = 3, còn `khoa500/b.jpg`, `ok/a.jpg`, `file000.jpg`). Xem thư mục `000`, `300`, gốc `000`: "Không đọc được mục này…"; xem `600`: danh sách rỗng, `unreadable` = 1; đọc/`stat` ảnh trong `000`, `300`, `600`, gốc `000`: "Không đọc được mục này…"; đọc file `000`: "Không mở được ảnh…". **Khác bản cũ:** ảnh trong thư mục `300` (và `chi-di-qua/sau/d.jpg` với tầng giữa `300`) nay **không đọc được** (bản cũ đọc được bằng `ImageRef` gõ sẵn). Đúng như Thợ Máy ghi ở mục Rủi ro: mở thư mục cần quyền đọc danh sách; chặt hơn, khớp với quét và `stat_image` (vốn đã báo lỗi từ T-076). Root: đọc được hết, như mong đợi |
| 5 | Hai thư mục chỉ khác hoa thường (`CongAI/`, `congai/`), hai file `x/A.jpg`, `x/a.jpg` | **Đạt.** Quét hiện đủ; mỗi `ImageRef` đọc ra đúng file của nó, `stat_image` trả đúng `ref`; `CONGAI/cong.png` bị từ chối "Không tìm thấy…"; `check_chosen_image(scanned=…)` giữ đúng `congai/cong.png` và `x/a.jpg` (SL-T063-4 không tái diễn) |
| 6 | File đặc biệt mang đuôi ảnh: FIFO, socket UNIX, thiết bị ký tự (`/dev/null`, chỉ root tạo được), thư mục tên `thu-muc.jpg` | **Đạt.** Quét đếm `other_files`; đọc/`stat`: "Đây không phải là file ảnh.", không treo |
| 7 | Tên NFD (`Cổng-Tân-Phú.jpg` dạng NFD) | **Đạt.** Liệt kê nguyên dạng, đọc/`stat` bằng `ref` liệt kê ra được; `ref` NFC: "Không tìm thấy…" (Linux phân biệt NFC/NFD; Mac thì không, chờ máy Mac) |
| 8 | Thêm cho T-079: ảnh ngay ở gốc (không có tầng cha), cây 8 tầng, tên 255 ký tự, `file_id` | **Đạt.** Đọc/`stat` được cả ba. `stat_image().file_id` = `(st_dev, st_ino)` thật; kết quả quét có `file_id = None`; `stat_image(ref) == entry` của quét (so không tính `file_id`) |

- **Hết fd** (`t079_emfile.py`, hạ `RLIMIT_NOFILE`): còn 0–1 fd trống thì đọc/`stat`/xem báo lỗi gọn "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại." (câu chưa đúng nghĩa nhưng vô hại), không treo, **không rò fd**; còn 2 fd trống thì chạy được. Bản cũ cũng báo câu này cho `stat`/xem. Ghi nhận, không phải lỗi mới.
- **Hiệu năng** (`t079_perf.py`): cùng cây 3.000 ảnh (20 KB, đường dẫn 3 tầng thư mục `cong-trinh/ctNN/truoc/`), 500 ảnh ngẫu nhiên mỗi việc, 3 lượt xen kẽ bản cũ / T-079, mỗi lượt một tiến trình mới. Thời gian **mỗi lần gọi**:

| Việc | Bản cũ `fa2cc39` (3 lượt) | T-079 (3 lượt) |
|---|---|---|
| `stat_image` | 0,26 / 0,28 / 0,23 ms | 0,27 / 0,27 / 0,27 ms |
| `read_image_bytes` | 0,23 / 0,19 / 0,22 ms | 0,21 / 0,21 / 0,20 ms |
| `list_folder` (100 ảnh) | 2,8 / 2,2 / 2,7 ms | 2,9 / 2,2 / 2,7 ms |
| Quét cả cây (3.000 ảnh) | 75 / 59 / 75 ms | 72 / 62 / 78 ms |

  **Không chậm rõ:** nhanh nhất `stat_image` chậm hơn khoảng 0,03 ms/lần (mở thêm 4 thư mục), `read_image_bytes` như cũ; xem thư mục và quét không đổi (không thuộc phần sửa).

### Bước 4 · Toàn bộ test và ruff (nhánh `team/T-079-linux`)

```
$ uv run pytest -q -rfEX            # trên team/T-079 c7b2394 + file test mới (9 test, trước khi thêm 3 xfail)
10656 passed, 143 skipped, 87 xfailed, 111 warnings in 365.20s (0:06:05)
(0 FAILED, 0 ERROR, 0 XPASS)

$ uv run pytest -q -rsxX            # đúng trạng thái commit (file mới đủ 9 test + 3 xfail)
10656 passed, 143 skipped, 90 xfailed, 118 warnings in 352.52s (0:05:52)
(0 FAILED, 0 ERROR, 0 XPASS; +3 xfail so với lượt 1 = đúng 3 ca SL-T079-L-1)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t079_linux.py
1 file already formatted
```

143 bỏ qua: 86 chỉ có trên Windows (53 junction, 11 cách lấy tên bằng `resolve`, 9 chế độ chia sẻ file, 7 cách hỏi từng mục, 3 thuộc tính ẩn/8.3, 2 cách tráo junction của Lá Chắn, 1 khóa file), 50 cần ổ **không** phân biệt hoa thường (Windows NTFS, Mac APFS), 3 do chạy bằng root (2 "vẫn ghi được file chỉ đọc", 1 quyền POSIX thật: đã chạy bằng `nobody` ở bước 1), 4 IPv6 (cloud không có IPv6). So với T-063 trên `main` cũ (1 hỏng SL-T063-1, 10.528 qua): nay **0 hỏng**. Cảnh báo: `DeprecationWarning` của `sqlite3` (tham số `?1` truyền bằng tuple, có cả trong `seo_app/storage/image_tags.py:644`; Python 3.14 sẽ thành lỗi) và 1 `UserWarning` Pydantic, đều có từ trước, không từ file mới.

### File test mới chạy trên bản cũ (để chắc test bắt được lỗi)

Chép tạm `tests/test_soi_loi_t079_linux.py` sang worktree `fa2cc39` (không commit ở đó):

```
$ (bản cũ) pytest tests/test_soi_loi_t079_linux.py -k race     # 3 lần
AssertionError: lọt 279 lần (['cỡ', 'nội dung']), {'read_ok': 563, 'stat_ok': 304, 'errors': 13512}
AssertionError: lọt 213 lần (['cỡ', 'nội dung']), {'read_ok': 561, 'stat_ok': 351, 'errors': 14767}
AssertionError: lọt 381 lần (['cỡ', 'nội dung']), {'read_ok': 543, 'stat_ok': 307, 'errors': 13733}
$ (T-079) pytest tests/test_soi_loi_t079_linux.py              # 5 lần
9 passed (x5) ; sau khi thêm SL-T079-L-1: 9 passed, 3 xfailed
```

Các test cấu trúc (tráo ngay sau khi mở từng tầng) hỏng trên bản cũ vì bản cũ không mở từng tầng (đúng như mong đợi). Lượt tráo thật 1,5 giây chỉ chạy trên Linux (`renameat2`), tự bỏ qua trên Windows và Mac; các test còn lại chạy được trên Mac.

## Lỗi phát hiện

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T079-L-1 | Thấp (chỉ sai câu báo, an toàn; không chặn gộp T-079, T-056) | Trong lúc bị tráo, bước `resolve(strict=True)` của `_resolve_inside` gặp tầng `x` vừa là symlink (lúc `resolve` xem `x`) rồi thành thư mục thật lại (lúc `resolve` đọc đích symlink): hệ điều hành trả `EINVAL`, app đổi thành "**Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt).**" thay vì "vừa bị thay đổi, hãy thử lại". Cùng loại với SL-T063-5 nhưng ở chỗ T-079 không sửa (code T-048, không đổi từ `fa2cc39`) | `seo_app/images/folders.py:617` (`current.resolve(strict=True)`), `:622-623` (`except (OSError, RuntimeError)` → `_MSG_UNREADABLE`) | (1) Chắc chắn: `tests/test_soi_loi_t079_linux.py::test_sl_t079_l_1_resolve_race_is_reported_as_changed` ×3 (`read_image_bytes`, `stat_image`, `list_folder`; kẻ tráo "luôn thắng" hai lần quanh `os.path.realpath`/`os.readlink`, `EINVAL` là lỗi thật của hệ điều hành). (2) Thật: bước 2 ca 8a; script `t079_origin.py` (lấy lỗi gốc ở `__context__`) đo 8 giây: 1.088 lần (`read`), 1.115 (`stat`), 1.208 (`list`) báo câu này, lỗi gốc `OSError(22)` tại `_resolve_inside:623` | Câu "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại." (như `_ChangedError`); quyền thật bị khóa (EACCES) vẫn báo "Không đọc được…" | Báo "không có quyền hoặc ổ đĩa vừa bị ngắt"; người dùng tưởng lỗi quyền/ổ đĩa. Không đọc gì ngoài gốc, không lộ đường dẫn |

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Các điều kiện an toàn của phiếu (không đọc nội dung, không trả số liệu của file ngoài thư mục ảnh; câu lỗi cố định, không đường dẫn) **đạt** trên Linux.

## Ghi nhận (không phải lỗi của T-079)

- **Ca 8g, thư mục thật được dời vào gốc:** khi một chương trình **đổi chỗ cả thư mục thật** ở ngoài vào chỗ `x` (không phải symlink), lúc đó thư mục đó **thật sự nằm trong thư mục ảnh**, nên cả bản cũ lẫn T-079 đều đọc được (T-079: 7.322 lần đọc nội dung, 7.270 lần thấy tên `chi-ngoai.jpg` / 29.259 vòng; bản cũ: 7.352 / 29.570). Không phải đường dẫn đi ra ngoài gốc: cách sửa T-079 đảm bảo "file đọc được nằm trong thư mục ảnh, đến qua các thư mục thật, lúc mở", không đảm bảo "file chưa từng ở chỗ khác". Muốn làm được, kẻ tấn công phải có **quyền ghi vào thư mục cha của thư mục bí mật** (để dời nó đi), tức đã có quyền gần bằng chủ thư mục. Cùng loại với hard link (LC-T048-6, sổ rủi ro): hard link tới file ngoài gốc vẫn đọc được như trước (đã thử; Ubuntu mặc định `protected_hardlinks=1` chỉ cho tạo hard link tới file của chính mình hoặc file mình đọc/ghi được). Đề nghị Lá Chắn ghi ca này cạnh LC-T048-6.
- Thư mục chỉ có quyền "đi qua" (`300`): ảnh bên trong nay không đọc được (bước 3 ca 4). Đúng như Thợ Máy báo.
- `roots()` vẫn báo gốc không có quyền đọc (`000`) là "dùng được", lỗi chỉ hiện khi mở (như T-063 đã ghi). Giao diện T-056 nên hiện câu lỗi của `list_folder`.
- Máy cloud có `fs.protected_symlinks=0` (Ubuntu thường là 1). Không ảnh hưởng kết quả: app không đi theo symlink nào; ghi lại để lượt sau dựng lại đúng điều kiện.
- Cloud chạy Python 3.12.3, Windows 3.12.15: không thấy khác hành vi trong các ca này.

## Đối chiếu tiêu chí xong

- [x] (1) 8 file test liên quan trên Linux: **0 hỏng**; SL-T063-1 → -5 qua, không còn `xfail`; SL-T063-4 không XPASS(strict) (bước 1)
- [x] (2) Dựng lại tráo thật T-063 (8a nguyên tử, 8b không nguyên tử; root và `nobody`) với `list_folder`, `read_image_bytes`, `stat_image`: **0 lọt nội dung, 0 lọt cỡ** (cả tên: 0) trên T-079; bản cũ cùng cách thử lọt 2.717/68.215 (bước 2)
- [x] (3) Symlink đặt sẵn, gốc là symlink, tên sai UTF-8, thư mục không quyền đọc, hai thư mục khác hoa thường: kết quả như bản cũ (trừ thư mục `300`, đã biết trước), câu lỗi không lộ đường dẫn; hiệu năng không chậm rõ (bước 3)
- [x] (4) Toàn bộ `uv run pytest`: 0 hỏng; `uv run ruff check .`: sạch (bước 4)
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T079-L-1 trong `tests/test_soi_loi_t079_linux.py`; không sửa code ứng dụng
- [x] Báo cáo ghi rõ hệ điều hành, bản Python; push lên `team/T-079-linux`

## Kết luận phần Linux: **ĐẠT**

Cách vá của T-079 (mở thư mục từng tầng từ gốc bằng `O_DIRECTORY | O_NOFOLLOW`, mở/`stat` file trong chính thư mục đã mở) **chạy đúng trên Linux thật**: tính chất Thợ Máy không giả lập được trên Windows ("thư mục đã mở vẫn là thư mục thật dù tên bị tráo") đã được thử bằng symlink thật và hơn 1,3 triệu vòng tráo thật, không lọt gì. SL-T063-2 (Cao trên Mac/Linux) và SL-T063-3 **đã đóng trên Linux**. SL-T079-L-1 (Thấp) không chặn gộp; nên dọn ở một phiếu dọn lỗi sau.

## Rủi ro và điểm cần chú ý

- **Mac chưa kiểm** (ngoài phạm vi lượt này): mã lỗi của macOS cho `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink (code nhận cả ELOOP lẫn ENOTDIR), APFS không phân biệt hoa thường, NFD, `UF_HIDDEN`, `renamex_np(RENAME_SWAP)`. 8 test cấu trúc và 3 test SL-T079-L-1 trong file mới chạy được trên Mac; lượt tráo thật 1,5 giây chỉ chạy trên Linux.
- Test `test_real_atomic_swap_race_never_leaks_outside_content_or_size` là test có yếu tố thời gian (1,5 giây, tiến trình riêng). Trên bản đúng nó luôn qua (không thể lọt); nếu code bị sửa sai sau này, nó hỏng với xác suất rất cao (bản cũ: hỏng 3/3 lần, 213–381 lần lọt). Có kiểm "tiến trình tráo chạy được hơn 1.000 lần", nên máy quá chậm sẽ báo rõ thay vì qua oan.
- Hai test cấu trúc dùng `sys._getframe(1)` để chỉ tráo đúng ở bước mở để đọc/`stat` (`_open_image`, `_opened_stat`). Đổi tên hai hàm này thì test hỏng ở `assert swapped == [...]` (báo rõ, không qua oan).
- Khi SL-T079-L-1 được sửa: 3 test `xfail(strict=True)` thành XPASS(strict) và **phải xóa dấu `xfail`**.

## Đề xuất

1. **Chỉ Huy:** phần Linux ĐẠT, chuyển Lá Chắn kiểm T-079 (F1). Gộp `team/T-079-linux` (file test mới + báo cáo) cùng `team/T-079`.
2. **Thợ Máy (phiếu dọn lỗi sau, không chặn):** SL-T079-L-1: trong `_resolve_inside`, vòng `lstat` vừa xác nhận mọi tầng là thư mục thật, nên `OSError` từ `resolve(strict=True)` có mã `EINVAL`, `ELOOP`, `ENOTDIR` là "vừa bị thay đổi" (`_ChangedError`); giữ `PermissionError` là "Không đọc được…". Có thể xét luôn `EMFILE`/`ENFILE` ("máy đang mở quá nhiều file").
3. **Lá Chắn:** ghi ca 8g (thư mục thật được dời vào gốc) vào sổ rủi ro cạnh LC-T048-6; kiểm lại T-079 trên Windows như biên bản T-063 đề nghị.
4. **Khi có máy Mac:** chạy 8 file test ở bước 1 cùng `tests/test_soi_loi_t079_linux.py -rsxX`, và cách tráo nguyên tử bằng `renamex_np(RENAME_SWAP)`.

## Câu hỏi cho chủ dự án

Không có.

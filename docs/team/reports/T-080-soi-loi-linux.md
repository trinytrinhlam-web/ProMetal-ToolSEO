# Báo cáo T-080 · Chạy kiểm tra trên Linux thật (dọn 3 lỗi Thấp đọc ảnh sau T-079) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · phiên Claude Code trên cloud |
| Phiếu | [T-080](../tickets/T-080-don-loi-thap-doc-anh-sau-t079.md) (lượt chạy trên Linux mà Thợ Máy đề nghị, mục "Phần chưa kiểm được trên Linux/Mac") |
| Ngày nộp | 2026-10-23 |
| Máy kiểm | **Ubuntu 24.04.5 LTS**, nhân Linux 6.18.44 (x86_64, 4 CPU), thư mục tạm trên ổ **ext4** (phân biệt hoa thường, phân biệt NFC/NFD). **Python 3.12.3** (`.venv` do `uv sync` tạo; máy Windows của đội: 3.12.15); chạy thêm **Python 3.12.13** (bản uv tự tải, môi trường riêng ngoài repo). **uv 0.11.32**, pytest 9.1.1, ruff 0.16.10. Phiên chạy bằng **root**; mọi lượt tráo và bộ test liên quan chạy thêm bằng người dùng thường **`nobody`** (uid 65534) qua `setpriv`. `fs.protected_symlinks=0`, `fs.protected_hardlinks=1` (như lượt T-079) |
| Mã nguồn | Nhánh `team/T-080` tại **`a88c4e8`** (nhánh `team/T-080-linux` tách từ đây). Đối chứng (worktree tạm, chỉ đọc): **`417efea`** (`main` ngay trước T-080, đã có T-079) và **`fa2cc39`** (trước T-079) |
| Nhánh nộp | `team/T-080-linux` (không push lên `team/T-080`). Commit `abdf1f5` (gỡ `xfail` SL-T079-L-1) và commit báo cáo này |
| Kết quả | Hoàn thành. **Kết luận phần Linux: ĐẠT** (0 lọt nội dung, 0 lọt cỡ, 0 lọt tên; 0 câu báo tả file ngoài; 0 câu "không có quyền" khi bị tráo). **Đã gỡ `xfail` SL-T079-L-1** (3 ca XPASS thật). 1 lỗi mới mức Thấp, có từ trước T-079, không chặn: SL-T080-L-1 |

## Tóm tắt (cho chủ dự án)

Hai lỗi nhỏ về **câu báo** mà T-080 sửa đã được sửa đúng trên Linux. Tôi dựng lại cách tấn công lần trước (một chương trình lạ liên tục tráo thư mục ảnh thành "lối tắt" ra ngoài), cho app đọc và xem ảnh **hơn 3,4 triệu lượt** trong lúc bị tráo hơn 160 triệu lần, bằng cả tài khoản quản trị lẫn tài khoản thường. Kết quả: **không lần nào đọc được nội dung hay số liệu của file bên ngoài**, **không lần nào câu báo nói về file bên ngoài** (kiểu "Ảnh quá lớn (3,0 MB)"), và **không lần nào báo sai thành "không có quyền"**. Cùng cách thử trên bản ngay trước T-080 thì ra 60.046 câu báo tả file ngoài và 148.048 câu "không có quyền", nên tôi chắc cách thử bắt được lỗi khi lỗi còn.

Ba test chỉ chạy được trên Linux/Mac mà Thợ Máy không chạy được trên Windows nay **qua thật**; tôi đã bỏ dấu "lỗi đã biết" của chúng. Mọi test liên quan và toàn bộ bộ test đều qua (0 hỏng).

Tôi tìm thêm **một lỗi nhỏ (Thấp), có từ trước, không chặn**: đôi khi đang bị tráo, app báo "Đường dẫn nằm ngoài thư mục ảnh" hay "Đường dẫn ảnh không hợp lệ (tên ngắn…)" thay vì "vừa bị thay đổi, hãy thử lại". Chỉ sai câu chữ, vẫn an toàn, chỉ xảy ra khi máy đang bị tấn công. Phần riêng của máy Mac vẫn chờ máy Mac.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t079_linux.py` | Chỉ xóa khối `@pytest.mark.xfail(...)` (6 dòng) của `test_sl_t079_l_1_resolve_race_is_reported_as_changed`; không đổi thân test |
| `tests/test_soi_loi_t080_linux.py` | Mới: 6 test đối chứng qua (tráo đúng lúc `resolve`: app từ chối, câu báo không lộ đường dẫn) + 6 test `xfail(strict=True)` ghi **SL-T080-L-1** |
| `docs/team/reports/T-080-soi-loi-linux.md` | Báo cáo này |

Không sửa code ứng dụng (`seo_app/**`, `app/**`), không sửa test khác. Script thử tấn công (`t080_probe.py`, `run_all.sh`, `summarize.py`) và số liệu thô (`race.jsonl`, 70 dòng) nằm trong thư mục tạm của phiên, không commit; cách làm ghi ở bước 3.

## Kết quả từng bước

### Bước 1 · 3 ca SL-T079-L-1 (`tests/test_soi_loi_t079_linux.py`)

Trước khi sửa file (đúng `a88c4e8`):

```
$ uv run pytest tests/test_soi_loi_t079_linux.py -rsxX
tests/test_soi_loi_t079_linux.py .........FFF
[XPASS(strict)] SL-T079-L-1 (soi-loi): ...   (read_image_bytes)
[XPASS(strict)] SL-T079-L-1 (soi-loi): ...   (stat_image)
[XPASS(strict)] SL-T079-L-1 (soi-loi): ...   (list_folder)
========================= 3 failed, 9 passed in 2.24s ==========================
```

Đúng như Thợ Máy đoán: cả 3 ca **XPASS(strict)**. Đã xóa khối `xfail` (diff chỉ 6 dòng xóa), chạy lại **5 lần liên tiếp: `12 passed` cả 5** (1,76–1,79 s). Bằng `nobody` (kèm file mới của tôi): `18 passed, 6 xfailed`.

### Bước 2 · Test liên quan trên Linux

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py \
    tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_soi_loi_t079_linux.py \
    tests/test_la_chan_t079.py tests/test_drafts_images.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py -rsxX
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
...
XFAIL tests/test_images_folders_soi_loi.py::test_r2_exact_budget_with_pending_empty_subfolder_is_not_truncated
  - R2-2 (soi-loi): quét cả cây, vừa đủ max_entries mục mà còn thư mục con RỖNG chờ quét thì vẫn báo 'còn nữa' (phần còn lại của L4)
========== 1216 passed, 160 skipped, 1 xfailed, 82 warnings in 14.49s ==========
```

- **0 hỏng, 0 XPASS.** 1 xfail còn lại là R2-2 (T-048, đã biết, không thuộc phiếu). 6 ca LC-T079-2 (`tests/test_la_chan_t079.py`, chạy mọi hệ điều hành) qua trên Linux.
- **Bằng `nobody`:** `1217 passed, 159 skipped, 1 xfailed` (thêm 1 qua là `test_real_posix_permissions_are_counted_not_fatal`, tự bỏ qua khi chạy bằng root).
- **31 ca T-080 chạy cả trên Mac/Linux** (`-k "same_win_path or lookalike or other_case_opens or problem_of_image or problem_seen_only or resolve_error_after"`): `31 passed, 20 skipped` (20 ca junction chỉ Windows), khớp số Thợ Máy ghi.
- **Python 3.12.13** (11 file trên + file mới): `1222 passed, 160 skipped, 7 xfailed`, giống hệt 3.12.3 (`1222 passed, 160 skipped, 7 xfailed`). Mã `posixpath.realpath` và `Path.resolve` của hai bản giống hệt (so file), nên các lỗi `resolve` khi bị tráo giống nhau.
- 160 bỏ qua (root): 72 junction, 13 junction/handle, 11 cách lấy tên của Windows, 7 cách hỏi từng mục, 3 thuộc tính ẩn/8.3, 2 cách tráo junction (đều chỉ Windows); 51 cần ổ **không** phân biệt hoa thường (Windows NTFS, Mac APFS); 1 thuộc tính ẩn của Windows/Mac; 1 cần người dùng thường (đã chạy bằng `nobody`).

### Bước 3 · Dựng lại phép tấn công của T-079 Linux

Script `t080_probe.py` (thư mục tạm): mỗi lượt dựng cây giả trong thư mục tạm riêng: gốc `anh/` có ảnh mồi `x/bi-mat.jpg` và `a/b/bi-mat.jpg` (8 byte), `y/bi-mat.jpg` (ảnh khác trong gốc); ngoài gốc `ngoai/bi-mat.jpg`, `ngoai/b/bi-mat.jpg` và `ngoai/chi-ngoai.jpg` (tên chỉ có ngoài gốc). Một **tiến trình riêng** (cùng người chạy) tráo liên tục; app gọi liên tục `list_folder`, `read_image_bytes`, `stat_image` (lượt 4 luồng thêm quét cả cây mỗi 10 vòng). Đếm: **lọt nội dung** (bytes khác ảnh mồi), **lọt cỡ** (`stat_image` hay danh sách trả cỡ, giờ sửa, `file_id` không phải của ảnh mồi), **lọt tên** (`chi-ngoai.jpg`), đọc qua liên kết sang ảnh khác trong gốc, **câu báo tả file ngoài** (LC-T079-2: "quá lớn", "rỗng", "Đây không phải là file ảnh." trong khi ảnh mồi là file thường 8 byte), **câu "Không đọc được mục này (không có quyền…)"** (LC-T079-3: không có lỗi quyền nào trong cây thử), câu báo lộ đường dẫn thư mục tạm / `/tmp` / `ngoai` / `SECRET`, lỗi xích lỗi hệ điều hành, lỗi không phải `ImageFolderError`, số fd trước/sau, và sau khi dừng tráo app đọc đúng ảnh mồi.

| Ca | Cách tráo (như T-079 Linux) |
|---|---|
| 8a | Thư mục `x` ↔ symlink ra ngoài, **nguyên tử** (`renameat2(RENAME_EXCHANGE)`) |
| 8b, 8b20, 8b200 | `x` ↔ symlink ra ngoài, **không nguyên tử** (đổi tên đi, tạo symlink, gỡ, trả tên); giữ mỗi trạng thái 0 / 20 µs / 200 µs |
| 8c | Chính file `x/bi-mat.jpg` ↔ symlink tới file ngoài, nguyên tử |
| 8d | Tầng trên `a` (ảnh ở `a/b/bi-mat.jpg`) ↔ symlink ra ngoài, nguyên tử |
| 8e | Tầng giữa `a/b` ↔ symlink ra ngoài, nguyên tử |
| 8f | `x` ↔ symlink tới thư mục **khác trong gốc** (`y/`), nguyên tử |

Biến thể file ngoài: **secret** (37 byte, để đo lọt nội dung/cỡ), **big** (3 MB, giới hạn đặt 1 MB), **empty** (0 byte), **dir** (`bi-mat.jpg` ngoài là thư mục). Ba biến thể sau đo đúng LC-T079-2. Ca 8g (thư mục thật dời vào gốc) không chạy: đã ghi sổ rủi ro (chủ dự án chốt khi gộp T-079).

**Pha A · lọt nội dung, cỡ, tên trên T-080 (mỗi vòng = 1 `list_folder` + 1 `read_image_bytes` + 1 `stat_image`):**

| Ca | Thời gian | root: vòng · lần tráo | `nobody`: vòng · lần tráo | Lọt nội dung · cỡ · tên · qua liên kết | Câu tả file ngoài · "Không đọc được" |
|---|---|---|---|---|---|
| 8a | 20 s | 98.530 · 5.652.530 | 106.783 · 5.941.362 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8b | 20 s | 235.022 · 1.174.283 | 209.704 · 1.565.609 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8b, giữ 20 µs | 20 s | 121.028 · 107.272 | 122.326 · 108.356 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8b, giữ 200 µs | 20 s | 149.916 · 34.139 | 147.396 · 34.625 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8c (chính file) | 20 s | 71.739 · 6.081.008 | 75.209 · 6.435.430 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8d (tầng trên) | 20 s | 81.419 · 5.324.318 | 85.999 · 5.610.090 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8e (tầng giữa) | 20 s | 105.887 · 5.931.706 | 113.142 · 6.095.896 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8f (liên kết trong gốc) | 20 s | 90.597 · 5.664.362 | 95.493 · 5.863.150 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8a, 4 luồng + quét cả cây | 30 s | 36.318 (+9.643 lần quét cả cây, gộp 2 lượt 4 luồng) · 9.383.692 | 35.264 (+9.190) · 9.411.584 | **0 · 0 · 0 · 0** | **0 · 0** |
| 8b, 4 luồng + quét cả cây | 30 s | 60.130 · 2.019.148 | 56.654 · 2.288.732 | **0 · 0 · 0 · 0** | **0 · 0** |

**Pha B · câu báo khi file ngoài có vấn đề (LC-T079-2, -3), T-080 so với `417efea`:**

| Ca × biến thể | root T-080 (15 s): vòng · câu tả file ngoài · "Không đọc được" | root `417efea` (10 s) | `nobody` T-080 (15 s) | `nobody` `417efea` (10 s) |
|---|---|---|---|---|
| 8a big | 82.276 · **0** · **0** | 56.771 · 2.830 · 7.892 | 74.249 · **0** · **0** | 49.704 · 2.031 · 3.561 |
| 8a empty | 76.798 · **0** · **0** | 54.494 · 2.198 · 7.169 | 75.790 · **0** · **0** | 51.279 · 2.145 · 6.133 |
| 8a dir | 84.264 · **0** · **0** | 56.385 · 2.528 · 9.607 | 74.827 · **0** · **0** | 52.048 · 1.706 · 5.860 |
| 8d big | 74.171 · **0** · **0** | 46.802 · 3.709 · 6.422 | 64.434 · **0** · **0** | 45.376 · 2.426 · 5.449 |
| 8d empty | 66.435 · **0** · **0** | 45.373 · 2.548 · 5.015 | 66.348 · **0** · **0** | 46.300 · 3.419 · 8.650 |
| 8d dir | 67.550 · **0** · **0** | 43.543 · 2.739 · 5.245 | 64.099 · **0** · **0** | 43.853 · 2.072 · 3.833 |
| 8e big | 72.993 · **0** · **0** | 55.437 · 4.277 · 15.191 | 74.811 · **0** · **0** | 54.083 · 5.007 · 17.197 |
| 8e empty | 72.141 · **0** · **0** | 51.624 · 4.646 · 9.245 | 73.458 · **0** · **0** | 51.081 · 6.465 · 2.717 |
| 8e dir | 79.607 · **0** · **0** | 58.487 · 3.724 · 22.525 | 80.032 · **0** · **0** | 50.421 · 5.576 · 6.337 |

Câu tả file ngoài trên `417efea` (gộp mọi ca, đọc + `stat`): "Ảnh quá lớn (3,0 MB), tối đa 1,0 MB." 20.280 lần, "File ảnh rỗng (0 byte)." 21.421, "Đây không phải là file ảnh." 18.345. Trên T-080: **0** cả ba.

**Pha C · đối chứng file ngoài thường (secret):**

| Bản | Ca | root: vòng · lọt nội dung · lọt cỡ · "Không đọc được" | `nobody` |
|---|---|---|---|
| `417efea` (T-079) | 8a / 8d / 8e / 8f (10 s mỗi ca) | 201.896 · 0 · 0 · 31.991 | 193.228 · 0 · 0 · 31.854 |
| `417efea` | 8c (10 s, chạy riêng sau) | 36.722 · 0 · 0 · 15.878 | (không chạy) |
| `fa2cc39` (trước T-079) | 8a / 8d / 8e (10 s mỗi ca) | 153.775 · **2.719** · **1.023** · 55.725 | 152.691 · **2.726** · **912** · 56.488 |

**Tổng trên T-080 (mọi ca, mọi biến thể): 3.422.839 vòng** (root 1.726.821, `nobody` 1.696.018), khoảng 10,3 triệu lời gọi, **162,8 triệu lần tráo**:

- **0 lọt nội dung, 0 lọt cỡ/giờ sửa/định danh, 0 lọt tên, 0 lần đọc qua liên kết** (LC-T079-1 phần Linux, SL-T063-2, -3 vẫn đóng).
- **0 câu báo tả file ngoài** (LC-T079-2 đóng trên Linux), **0 câu "Không đọc được mục này (không có quyền…)"** (LC-T079-3 / SL-T079-L-1 đóng trên Linux).
- Câu báo lộ đường dẫn: **0**. Lỗi xích lỗi hệ điều hành: **0**. Lỗi lạ (không phải `ImageFolderError`): **0**. Số fd sau mỗi lượt bằng trước (4 = 4, cả 70 lượt). Sau khi dừng tráo, app đọc đúng ảnh mồi (70/70).

**So với T-079 Linux:** T-079 đo 1.349.659 vòng trên bản T-079, 0 lọt; lượt này 3.422.839 vòng trên T-080, 0 lọt. Đối chứng `fa2cc39` lọt nội dung 960/54.598 vòng ở 8a root (T-079 Linux đo 2.717/68.215: cùng cỡ vài phần trăm), nên cách thử tương đương lần trước. SL-T079-L-1 lần trước đo khoảng 1.100 lần mỗi việc trong 8 giây; trên `417efea` lượt này 8.319 câu "Không đọc được" trong 10 giây ở 8a root; trên T-080: 0.

**Câu báo khi bị tráo trên T-080** (gộp mọi ca, đọc / `stat` / xem thư mục):

| Câu báo | Đọc | `stat` | Xem | Ca |
|---|---|---|---|---|
| Đường dẫn đi qua liên kết tắt (symlink/junction)… | 1.444.410 | 1.592.698 | 1.617.249 | mọi ca |
| Không tìm thấy ảnh hoặc thư mục này… | 496.694 | 520.114 | 524.389 | chỉ 8b, 8b20, 8b200 (lúc `x` đang dời đi) |
| Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại. | 453.063 | 736.573 | 489.257 | mọi ca |
| Ảnh vừa bị thay đổi trong lúc đọc, hãy thử lại. | 23.066 | 7.141 | – | mọi ca |
| Đường dẫn nằm ngoài thư mục ảnh được phép. | 568.595 | 444.572 | 417.243 | 8a, 8b, 8c, 8d, 8e (**SL-T080-L-1**) |
| Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục). | 36.160 | 27.062 | 27.551 | chỉ 8f (**SL-T080-L-1**) |
| Không mở được ảnh (không có quyền hoặc file vừa bị đổi). | 7.252 | – | – | chỉ 8c (ghi nhận, xem dưới) |

Không còn câu "Không đọc được mục này…", "Ảnh quá lớn…", "File ảnh rỗng…", "Đây không phải là file ảnh." nào.

### Bước 4 · Toàn bộ test và ruff (nhánh `team/T-080-linux`, đúng trạng thái commit)

```
$ uv run pytest -q -rfEX
11209 passed, 177 skipped, 96 xfailed, 120 warnings in 342.60s (0:05:42)
(0 FAILED, 0 ERROR, 0 XPASS)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t079_linux.py tests/test_soi_loi_t080_linux.py
(cả hai: already formatted)
```

So với T-079 Linux (`10656 passed, 143 skipped, 90 xfailed`): thêm test của các phiếu gộp `main` sau đó và của T-080, 0 hỏng như lần trước. 96 xfail có 6 ca SL-T080-L-1 mới; trong 11 file liên quan và file mới chỉ có R2-2 (T-048) và 6 ca đó.

## Lỗi phát hiện

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T080-L-1 | Thấp (chỉ sai câu báo, an toàn; có từ trước T-079, code T-048; không chặn gộp T-080, T-056) | Cùng loại với LC-T079-3 nhưng ở nhánh `resolve` **không lỗi**: vòng `lstat` của `_resolve_inside` vừa thấy `x` là thư mục thật, rồi `resolve(strict=True)` đi trọn qua `x` lúc nó đang là symlink. Kết quả ra ngoài gốc thì báo "**Đường dẫn nằm ngoài thư mục ảnh được phép.**", ra thư mục khác trong gốc thì "**Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục).**" Người dùng tưởng ảnh đã chọn sai đường dẫn, trong khi thử lại là được | `seo_app/images/folders.py:655` (`current.resolve(strict=True)`), `:664-665` (`_MSG_OUTSIDE`), `:669-673` (`_MSG_ALIAS`) | (1) Chắc chắn: `tests/test_soi_loi_t080_linux.py::test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed` ×6 (`read_image_bytes`, `stat_image`, `list_folder` × symlink ra ngoài gốc / tới `y` trong gốc; `x` thành symlink đúng trong lúc `os.path.realpath` chạy, trở lại thư mục thật ngay sau). Chạy `--runxfail`: 6 ca hỏng đúng ở `assert 'thay đổi' in 'Đường dẫn nằm ngoài thư mục ảnh được phép.'` (×3) và `… in 'Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục).'` (×3). (2) Thật: bước 3, bảng câu báo (ví dụ 8f: khoảng 90.000 lần / 40 s; `417efea` cũng vậy: 56.364 lần / 20 s) | "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại." (`_ChangedError`), như các ca tráo khác | Câu "nằm ngoài thư mục ảnh" / "không hợp lệ (tên ngắn…)". Không đọc gì, không lộ đường dẫn hay số liệu (6 test đối chứng cùng file qua) |

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Điều kiện an toàn của phiếu (không đọc nội dung, không trả số liệu, không tả file ngoài thư mục ảnh; câu lỗi cố định, không đường dẫn) **đạt** trên Linux.

Cách sửa gợi ý cho SL-T080-L-1 (để Thợ Máy cân nhắc, không bắt buộc): trên Mac/Linux, vòng `lstat` đã thấy mọi tầng là thư mục thật, tên an toàn (không `..`), gốc đã `resolve`; nên `resolve` ra chỗ khác `gốc/parts` chỉ có thể do bị tráo → `_ChangedError`. Trên Windows giữ nguyên (`_MSG_ALIAS` còn có nghĩa thật với tên ngắn 8.3).

## Ghi nhận (không phải lỗi mới)

- **"Không mở được ảnh (không có quyền hoặc file vừa bị đổi)."** chỉ ở ca 8c (chính file vừa thành symlink giữa lúc kiểm và lúc mở: `O_NOFOLLOW` báo ELOOP). Câu có sẵn từ T-079 (`_MSG_CANNOT_OPEN`), nêu cả hai nguyên nhân nên không sai; `417efea` cùng ca cũng ra câu này (1.976 lần / 10 s). Nếu sửa SL-T080-L-1 thì có thể tách luôn ELOOP thành "Ảnh vừa bị thay đổi…".
- Câu "Không tìm thấy…" ở ca 8b (thư mục đang dời đi) và "liên kết tắt" là đúng nghĩa; Lá Chắn T-079 không bắt sửa.
- Kiểm "file ẩn" (`App không đọc file ẩn…`) không thử được trên Linux (Linux không có cờ ẩn; Mac có `UF_HIDDEN`): chờ máy Mac.
- Máy cloud có `fs.protected_symlinks=0` (Ubuntu thường là 1): không ảnh hưởng (app không đi theo symlink nào); ghi lại để lượt sau dựng đúng điều kiện.

## Đối chiếu tiêu chí xong

- [x] (1) 3 ca SL-T079-L-1 XPASS(strict) → đã xóa khối `xfail` (chỉ dấu, 6 dòng), chạy lại 5/5 lần qua (bước 1)
- [x] (2) 11 file test liên quan: **0 hỏng, không XPASS(strict) nào khác** (root, `nobody`, Python 3.12.13) (bước 2)
- [x] (3) Dựng lại tráo thật `renameat2(RENAME_EXCHANGE)` (và không nguyên tử), root và `nobody`, `list_folder` / `read_image_bytes` / `stat_image`: **3.422.839 vòng, 0 lọt nội dung, 0 lọt cỡ**; câu báo khi bị tráo không còn "không có quyền" hay số liệu của file bên ngoài (LC-T079-2, -3); đối chứng `417efea` và `fa2cc39` bắt được lỗi (bước 3)
- [x] (4) Toàn bộ `uv run pytest`: 0 hỏng; `uv run ruff check .`: sạch (bước 4)
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T080-L-1 trong `tests/test_soi_loi_t080_linux.py`; không sửa code ứng dụng
- [x] Báo cáo ghi rõ hệ điều hành, bản Python; push lên `team/T-080-linux`

## Kết luận phần Linux: **ĐẠT**

Cách sửa của T-080 chạy đúng trên Linux thật: lỗi `resolve` khi bị tráo nay báo "vừa bị thay đổi" (SL-T079-L-1 / LC-T079-3 đóng, `xfail` đã gỡ), câu báo khi ảnh có vấn đề chỉ tả mục trong thư mục ảnh (LC-T079-2 đóng: 0 so với 60.046 lần ở bản cũ), và các lớp chặn T-079 (mở thư mục từng tầng) vẫn giữ 0 lọt qua hơn 3,4 triệu vòng tráo thật. SL-T080-L-1 (Thấp, có từ trước) không chặn gộp.

## Rủi ro và điểm cần chú ý

- **Mac chưa kiểm** (điều kiện cũ, giữ): APFS không phân biệt hoa thường và dạng Unicode, cờ ẩn `UF_HIDDEN`, mã lỗi `openat(O_DIRECTORY | O_NOFOLLOW)`, tráo nguyên tử `renamex_np(RENAME_SWAP)`. 31 ca T-080 chạy được trên Mac đã qua trên Linux; 3 ca SL-T079-L-1 và 12 ca file mới cũng chạy được trên Mac.
- Test SL-T080-L-1 và SL-T079-L-1 giả lập kẻ tráo "luôn thắng" bằng cách bọc `os.path.realpath` / `os.readlink`. Nếu sau này `_resolve_inside` không còn dùng `Path.resolve` (hay Python đổi cách `resolve` gọi `realpath`), test có thể không còn tráo đúng chỗ: ca đối chứng của tôi kiểm `x` trở lại thư mục thật sau mỗi lần, nhưng không kiểm việc tráo đã xảy ra. Khi sửa SL-T080-L-1 mà 6 ca thành XPASS thì **phải xóa dấu `xfail`**.
- `team/T-080-linux` sửa `tests/test_soi_loi_t079_linux.py`, file mà phiếu cho phép gỡ `xfail`; `team/T-080` không đụng file này, nên gộp không xung đột (thử `git merge-tree` khi Chỉ Huy gộp nếu `team/T-080` có commit mới).

## Đề xuất

1. **Chỉ Huy:** phần Linux ĐẠT. Gộp `team/T-080-linux` (gỡ `xfail` SL-T079-L-1, file test mới, báo cáo) cùng `team/T-080`, rồi chuyển Lá Chắn rút gọn (F1).
2. **Thợ Máy (phiếu dọn sau, không chặn):** SL-T080-L-1 theo cách gợi ý ở mục Lỗi; có thể tách ELOOP của `_open_image` thành "Ảnh vừa bị thay đổi…" cùng lúc. Hoặc Chỉ Huy cho ghi nhận, không sửa (chỉ sai câu chữ khi đang bị tấn công).
3. **Khi có máy Mac:** chạy 11 file ở bước 2 cùng `tests/test_soi_loi_t080_linux.py -rsxX`, và cách tráo nguyên tử bằng `renamex_np(RENAME_SWAP)`.

## Câu hỏi cho chủ dự án

Không có.

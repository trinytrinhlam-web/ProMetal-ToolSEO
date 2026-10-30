# Báo cáo T-107 · HEIC giải mã một luồng (LC-T093-3) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-107 `docs/team/tickets/T-107-heif-tat-giai-ma-song-song.md` (trên `main` máy, nhánh không chứa) · mức kiểm **rút gọn**, Windows. Không chạy cloud |
| Ngày nộp | 2026-10-30 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15, người dùng thường; pillow-heif 1.8.1 (libheif 1.23.6, libde265 1.1.3), Pillow 13.0.0. Máy đang chạy toàn bộ test của Chỉ Huy song song (RAM trống lúc kiểm: khoảng 0,8 GB / 14 GB) |
| Mã nguồn | Nhánh `team/T-107` tại `9a04a91` (`main` `0122d4b` + T-093 + T-107). Gộp thử với `main` mới nhất trên máy `3164a80` (đã có T-099, T-100, T-106 + T-108) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T107-2), **1 Thấp** (SL-T107-1), cả hai **có từ trước** trên `main` (T-107 không gây ra). Mục tiêu phiếu đạt: mọi đường mở HEIC của app giải mã **một luồng**, LC-T093-3 đóng đúng ý, test cũ không lùi, gộp `main` `3164a80` sạch. Thử đột biến: test cũ chưa phủ ca «HEIF đã đăng ký rồi bị đặt lại số luồng»; Soi Lỗi đã thêm 2 test (qua) để ghim. Đề nghị sửa SL-T107-2 (vài dòng, ngay trong `_check_heif_grid`) trước khi đóng Giai đoạn 3; không chặn gộp T-107 |

## Tóm tắt (cho chủ dự án)

- **Lỗ hổng chính đã được chặn.** App mở ảnh HEIC (ảnh iPhone) bằng **một luồng**, đúng cách tránh lỗ hổng của thư viện libheif 1.23.6. Đã thử mọi chỗ app mở ảnh: ảnh xem trước, ảnh gửi AI viết alt, ảnh gửi lên WordPress. Đã thử thêm ba tình huống: mở lần đầu, mở lại, và nhiều ảnh mở cùng lúc. Chỗ nào cũng một luồng.
- **Ảnh thật vẫn tốt.** Đã thử 258 ảnh HEIC hợp lệ với nhiều cỡ ảnh, cỡ ô và chiều xoay. Kết quả: 0 lỗi, giữ GPS, xoay đúng, điểm ảnh giống hệt cách đọc cũ. Đổi lại, mỗi ảnh HEIC chậm hơn khoảng 1 giây. Ảnh JPEG (ảnh Zalo) không đổi.
- **Ảnh hỏng không làm sập trang.** Đã thử 258 file HEIC hỏng hoặc dựng cố ý. Không lần nào sập, không lần nào treo lâu; chậm nhất 2,6 giây.
- **Tìm thêm 2 lỗi đã có từ trước:**
  - **SL-T107-2 (Trung bình).** Một file HEIC dựng cố ý, chỉ 20 kB, lọt qua giới hạn 80 triệu điểm ảnh của app. Kết quả: app bận 11–14 giây và tốn thêm 250 MB bộ nhớ mỗi lần mở, rồi báo «ảnh hỏng». Dạng file lớn hơn mở được nhưng chưa đo, vì máy thiếu RAM.
    - Muốn gặp lỗi này, ai đó phải cố ý đặt file như vậy vào thư mục ảnh.
    - Sửa chỉ vài dòng.
  - **SL-T107-1 (Thấp).** Một loại lỗi của libheif hiện câu chung «Không xử lý được ảnh này» thay cho câu báo đúng. Trang vẫn chạy bình thường.
- **Việc cần làm:** gộp T-107 được. Nên sửa SL-T107-2 (kèm SL-T107-1) ở một lượt ngắn trước khi đóng Giai đoạn 3.

## Phạm vi và cách kiểm

- Đọc diff T-107 (`seo_app/images/process.py` +50 dòng, `tests/test_la_chan_t093.py` −4, test Thợ Máy `tests/test_t107_heif_mot_luong.py` 29 ca) và mọi chỗ gọi xử lý ảnh trong `app/`, `seo_app/`.
  - Chỉ có **một** lệnh `Image.open` (trong `_pillow_open`).
  - Không chỗ nào gọi `pillow_heif` trực tiếp ngoài `_register_heif`.
  - Mọi đường mở đi qua `_open`: `open_image`, `make_preview`, `PreviewCache.get`, `make_web_image`, `make_ai_image`.
- Script riêng, chạy ngoài repo, chép vào thư mục ghi chú chung `T-107-soi-loi-scripts/`. Mỗi lần mở ảnh, các script này:
  - đo số luồng app **truyền thật** cho libheif, bằng cách gài vào `_pillow_heif.load_file`;
  - đếm luồng hệ điều hành (Toolhelp32);
  - chạy trong tiến trình con có hạn giờ.
- Test chọn lọc (không chạy toàn bộ, máy đang chạy toàn bộ test). Thêm thử đột biến mã T-107 trên bản sao: 11 đột biến, mỗi đột biến một bản sao riêng, không đụng mã nhánh.

## Việc 1 · Mọi đường mở HEIC đều một luồng — **đạt**

`sl107_threads.py`, `sl107_race.py`. Con số là tham số luồng app truyền cho `load_file` lúc mở. Đối chứng là pillow-heif mặc định (4 luồng).

| Tình huống | Luồng truyền libheif | Ghi chú |
|---|---|---|
| Đăng ký lần đầu (HEIF chưa có trong bảng của Pillow, tùy chọn mặc định 4) | **0** | `_register_heif` đặt `DECODE_THREADS` trước, rồi `register_heif_opener(decode_threads=0)` |
| Đăng ký lại: `import pillow_heif.HeifImagePlugin` (gọi `register_heif_opener()` không tham số), hay mã khác gọi `register_heif_opener(decode_threads=4)` / đặt `options.DECODE_THREADS = 4` giữa hai lần mở | **0** | `_register_heif` đặt lại `DECODE_THREADS` **mỗi lần**, ngay trước `Image.open` |
| `open_image`, `make_preview` (cả `PreviewCache`), `make_ai_image` (ảnh gửi AI viết alt), `make_web_image` (ảnh gửi WordPress) | **0** ở cả 4 | Ảnh lưới 12 MP; luồng hệ điều hành tăng **+1** mỗi lần mở. Đối chứng 4 luồng: **+7** |
| `Image.open` trực tiếp, `pillow_heif.open_heif`, `pillow_heif.read_heif` sau khi app đã đăng ký | **0** | App không dùng các đường này; kiểm để biết trạng thái chung của tiến trình |
| 8 luồng app cùng mở (`ThreadPoolExecutor`) | **0** ở 24/24 lời gọi | Kết quả từng byte giống nhau giữa các luồng |
| Mã khác đặt `DECODE_THREADS = 4` **song song** trong lúc app mở (vòng lặp liên tục, 600 lần mở) | 0 ở 599/600, **4 ở 1/600** | Không có thật trong app: không mã nào của app hay thư viện đã cài đặt đặt tùy chọn pillow-heif (tìm trong `.venv`). Ghi nhận GN-1 |

Kết luận: không còn đường nào trong app giải mã HEIC song song. Muốn chặn cả ca song song lý thuyết ở GN-1, app phải giữ khóa quanh `open`. Không cần làm khi chưa có mã nào đặt tùy chọn này.

## Việc 2 · Ảnh hợp lệ vẫn đọc đúng, giữ GPS, xoay đúng; tốc độ — **đạt**

`sl107_correct.py` quét **258 ca (156 ảnh lưới)**:
- 7 cỡ ảnh: 1100 × 800, 1001 × 777 (lẻ), 4032 × 3024, 3024 × 4032, 513 × 513, 64 × 64, 2000 × 130;
- 6 cỡ ô: không lưới, 64, 128, 256, 512, 1024;
- 8 chiều xoay EXIF;
- bỏ các tổ hợp bộ mã hóa không dựng được.

Kết quả: **0 lỗi** (1.095 giây, máy bận). Mỗi ca đều đạt cả bốn điều:
- `make_web_image` qua (phép kiểm lưới không từ chối oan ảnh nào, kể cả ô 64, ô 1024 và ảnh dọc);
- GPS đúng;
- cỡ đúng sau xoay;
- điểm ảnh của `open_image` (một luồng) **giống từng byte** với giải mã 4 luồng; `make_preview`, `make_ai_image` qua.

Tốc độ (`sl107_speed.py`): `make_web_image` đo xen kẽ, 3 lượt, lấy lượt nhanh nhất. Ảnh mẫu 4 mảng màu (dễ giải mã hơn ảnh chụp thật), máy đang chạy toàn bộ test:

| Ảnh | Một luồng (T-107) | 4 luồng (trước T-107) | Chậm thêm |
|---|---|---|---|
| 4032 × 3024 (12 MP), ô 512, EXIF có GPS, xoay 6 | 1,68 s | 0,93 s | ~0,75 s |
| 8064 × 6048 (49 MP), ô 512 | 2,91 s | 2,24 s | ~0,7 s |

Khớp với số đo của Thợ Máy (+1 s với 12 MP, +2 s với 48 MP trên ảnh thật). Chấp nhận được: mỗi bài chọn vài ảnh, ảnh xem trước có cache.

## Việc 3 · HEIC hỏng hoặc dựng cố ý

### Thử hàng loạt (`sl107_fuzz.py`, 258 ca × 2 lời gọi `make_preview` + `make_web_image`)

Mỗi lô ca chạy trong một tiến trình con, mỗi ca có hạn 60 giây. Có 18 ca dựng có chủ đích:
- cắt cụt ở 7 vị trí;
- đầu file đúng nhưng phần sau là rác;
- `ispe` khai 100000 × 100000;
- mô tả lưới đổi số ô hoặc cỡ đầu ra;
- ô 8 / 16 / 32 / 48 do bộ mã hóa tạo.

Có thêm 240 ca đột biến ngẫu nhiên (seed 107) trên 3 file: lưới 12 MP, lưới nhỏ, ảnh đơn. Mỗi file đều có GPS và XMP.

| Kết quả | Số lời gọi |
|---|---|
| Sập tiến trình | **0** |
| Treo quá hạn 60 s | **0** (chậm nhất **2,64 s**) |
| Đọc được (đột biến không chạm phần quan trọng) | 196 |
| Câu báo cố định của app | 316: «không phải ảnh … đọc được» 268, «Ảnh bị hỏng…» 36, «cấu trúc lạ (lưới ô…)» 8 (ô 16/32/48, đầu ra 1 × 1), «quá nhiều điểm ảnh» 2 (`ispe` lớn), «File ảnh rỗng» 2 |
| Lỗi lọt ra ngoài `ImageProcessError` | **4** (2 ca × 2 lời gọi): `RuntimeError` «Security limit exceeded: Image size …» → **SL-T107-1** |

Phép kiểm lưới mới của T-107 bắt đúng mọi ca ô nhỏ hoặc thừa ô, trước khi giải mã.

### Lưới lớn mà mọi ô trỏ cùng một mục (`sl107_gridrepeat.py`, `sl107_gridprobe.py`) → **SL-T107-2**

Cách dựng file thử:
- Bắt đầu từ file hợp lệ của bộ mã hóa pillow-heif (lưới 8 × 6 ô 512, `ispe` 4032 × 3024).
- Sửa mô tả lưới thành C × R ô, đầu ra C·512 × R·512.
- Cho mọi tham chiếu ô (`dimg`) trỏ về **cùng một ô đã mã hóa**, nên file vẫn nhỏ.
- Giữ `ispe` nên Pillow vẫn báo 4032 × 3024 (12 MP) lúc mở: qua phép kiểm 80 MP.
- Số ô vừa đủ phủ đầu ra và ô 512, nên qua cả hai phép kiểm lưới của T-107.

| Lưới | File | Lúc mở | `open_image` | `make_preview` | Bộ nhớ thêm |
|---|---|---|---|---|---|
| 24 × 24 ô 512 (12288², 151 MP) | 19,7 kB | qua mọi phép kiểm | 9,3 s → «Ảnh bị hỏng» | 12,7 s → «Ảnh bị hỏng» | ~108 MB |
| **31 × 31 ô 512 (15872², 252 MP)** | 20,5 kB | qua mọi phép kiểm | **11,1 s** → «Ảnh bị hỏng» | **14,2 s** → «Ảnh bị hỏng» | **~250 MB** |
| 32 × 32 trở lên | — | libheif từ chối ngay (giới hạn 1000 tham chiếu `iref`) → «không phải ảnh … đọc được» | tức thì | tức thì | — |
| 31 × 31 ô **1024** (31744², **1007 MP**) | — | libheif **nhận**, qua mọi phép kiểm của app | chưa đo | chưa đo | chưa đo |

- Không sập, không treo vô hạn, câu báo cuối cùng đúng.
- Nhưng libheif **giải mã hết lưới** rồi mới báo «cỡ ảnh không khớp».
- Hàng 1007 MP không giải mã vì máy chỉ còn khoảng 0,8 GB RAM trống. Ước tính: bộ nhớ vài GB, thời gian vài chục giây, trừ khi libheif tự chặn vì giới hạn khối nhớ.

## Việc 4 · Bỏ `xfail` LC-T093-3 đúng R5; test ảnh cũ không lùi — **đạt**

- Diff `tests/test_la_chan_t093.py`: chỉ bỏ 4 dòng decorator `xfail(strict=True)` của LC-T093-3. Thân test, docstring và phép kiểm **giữ nguyên**: `not heif_on or libheif >= 1.23.7 or DECODE_THREADS == 0`, đặt `DECODE_THREADS = 4` trước khi gọi `_register_heif`. Test giờ qua thật. Đúng R5: không xóa, không nới.
- LC-T093-1, LC-T093-2 vẫn `xfail(strict=True)` (chưa thuộc phiếu này).
- Test chọn lọc trên `team/T-107` (`9a04a91` + test Soi Lỗi), 12 file: `test_soi_loi_t107`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_pillow_heif_setup`, `test_images_process`, `test_soi_loi_t047`, `test_soi_loi_t049`, `test_pillow_version_t058`, `test_soi_loi_t058`, `test_soi_loi_t067`, `test_soi_loi_t080`, `test_app_images`.
  - Kết quả: **607 qua, 13 xfail, 0 hỏng** (541 giây, máy bận). 13 xfail gồm 7 của SL-T107, 2 của LC-T093-1/-2 và 4 xfail cũ đã có từ trước ở T-049, T-067, T-080. Không có XPASS.
  - Hai test bổ sung sau thử đột biến chạy riêng: qua. Cả file `test_soi_loi_t107.py`: 3 qua, 7 xfail.
  - **T-047, T-058, T-080 không lùi.**
- `uv run ruff check .`: qua. `ruff format --check` file test mới: qua.

## Việc 5 · Gộp thử với `main` mới nhất trên máy — **sạch**

- Lần 1 (`main` `0122d4b`): `git merge-tree` **không xung đột**, ra đúng cây của nhánh. Gộp thử thêm T-106 (cũng sửa `tests/test_la_chan_t093.py`) ở worktree tạm: **không xung đột**. Chạy 8 file test HEIF và T-106 ở đó: **184 qua, 11 xfail, 0 hỏng**.
- Lần 2 (`main` mới `3164a80`, đã gộp T-099, T-100, T-106 + T-108):
  - Từ `0122d4b` tới `3164a80`, `main` không sửa `seo_app/images`, `pyproject.toml` hay `uv.lock`. Trong `app/` chỉ sửa `app/views/wordpress.py`, và trang này không còn đường mở ảnh (T-108).
  - `git merge-tree --write-tree main team/T-107`: **không xung đột** (cây `d4c0b0e`).
  - Gộp thật ở worktree tạm tách rời (commit treo `742f061`, không đẩy), rồi chạy 8 file test ở đó. Đã kiểm `seo_app` nạp từ chính worktree tạm. Các file: `test_soi_loi_t107`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_pillow_heif_setup`, `test_images_process`, `test_app_images`, `test_drafts_images` (đổi trên `main`), `test_t106_trang_ket_noi`.
  - Kết quả: **443 qua, 1 bỏ qua, 8 xfail, 0 hỏng, 0 XPASS** (376 giây).
  - 8 xfail gồm 7 của SL-T107 và LC-T093-2. LC-T093-1 đã đóng trên `main` nhờ T-106, LC-T093-3 đóng nhờ T-107: hai lần gỡ `xfail` trên cùng file gộp đúng.
- Cả hai worktree tạm đã gỡ bằng `git worktree remove`.

## Thử đột biến (`sl107_mutate.py`)

Mỗi đột biến là một bản sao `git archive` (`seo_app`, `tests`, `config`, `app`), sửa đúng một chỗ trong `process.py`, rồi chạy 4 file test HEIF (Thợ Máy T-107, Lá Chắn T-093, pillow-heif setup, Soi Lỗi T-107).

| Đột biến | Test hỏng |
|---|---|
| M0 không đổi (đối chứng) | 0 (35 qua, 9 xfail) |
| M1 bỏ dòng đặt lại `DECODE_THREADS` mỗi lần (chỉ còn đặt lúc đăng ký) | **0 lúc đầu: lọt.** Test T-107 cũ không phủ được, vì fixture trả bảng định dạng về trạng thái chưa đăng ký trước mỗi test. Ca bị bỏ sót: app đã đăng ký (hay thư viện khác đăng ký bằng `register_heif_opener()` không tham số) rồi số luồng bị đặt lại. Soi Lỗi thêm `test_already_registered_heif_open_still_single_thread` (2 ca, **qua** trên T-107). Chạy lại M1: **2 hỏng** |
| M2 bỏ `decode_threads=0` lúc đăng ký | 1: `test_first_registration_also_single_thread` |
| M3 bỏ cả hai chỗ đặt luồng | 8: 6 ca một luồng của Thợ Máy, ca lưới xoay, LC-T093-3 |
| M4 `HEIF_DECODE_THREADS = 4` | 8 (như M3) |
| M5 đặt `DECODE_THREADS = 4` sau khi đăng ký | 8 (như M3) |
| M6 bỏ lời gọi `_check_heif_grid` | 1: `test_open_rejects_strange_grid_without_decoding` |
| M7 ô tối thiểu 16 | 1: `[o-63]` |
| M8 cho thừa gấp đôi số ô | 2: `[thua-cot]`, `[thua-hang]` |
| M9 chỉ tính một chiều ô (bỏ chiều xoay) | 0. **Đột biến tương đương** với file thật: libheif báo cả ô lẫn ảnh theo cùng một chiều, sau khi xoay (ảnh dọc, ô chữ nhật của Thợ Máy vẫn qua). Ghi nhận GN-4 |
| M10 thông tin lưới hỏng thì cho qua | 3: `[thieu-khoa]`, `[chu]`, `[none]` |
| M11 bỏ kiểm cột/hàng < 1 | 1: `[0-cot]` |

Kết luận: test của Thợ Máy cộng test bổ sung của Soi Lỗi bắt được mọi đột biến làm đổi hành vi.

## Lỗi mới

| Mã | Mức | Có từ trước? | Mô tả | Test |
|---|---|---|---|---|
| **SL-T107-2** | **Trung bình** | Có (`main` không kiểm lưới; phép kiểm mới của T-107 chưa phủ ca này) | `_check_heif_grid` không so cỡ đầu ra của lưới (`tiling` `image_width × image_height`) với cỡ ảnh lúc mở (`ispe`, `image.size`), cũng không so với `MAX_IMAGE_PIXELS`. File HEIC 20 kB qua giới hạn 80 MP và mọi phép kiểm lưới; libheif giải mã 252 MP (đo: 11–14 s, +250 MB mỗi lần mở) rồi mới báo cỡ không khớp. Dạng ô 1024 cho đầu ra 1007 MP mở được (chưa đo giải mã). Báo cáo Thợ Máy ghi «giới hạn 80 triệu điểm ảnh vẫn áp cho HEIC»: đúng với cỡ `ispe`, **không đúng** với cỡ lưới libheif thật sự dựng | `test_sl_t107_2_grid_larger_than_image_rejected_before_decode` (3 ca: 24 × 24 ô 512, 31 × 31 ô 512, 31 × 31 ô 1024; thông tin lưới đúng như libheif báo với file dựng, đặt qua `_pillow_open`; mong đợi từ chối trước `load`) |
| **SL-T107-1** | Thấp | Có (`main` bắt cùng danh sách lỗi) | `_open` chỉ bắt `OSError`, `ValueError`, `SyntaxError`, `EOFError`, `struct.error` quanh `load()`. `RuntimeError` của libheif (ví dụ «Memory allocation error: Security limit exceeded: Image size 65535x65535 …», mô tả lưới khai đầu ra rất lớn, báo ngay 0,01 s) lọt ra khỏi `process`, trái lời hứa «mọi lỗi thành `ImageProcessError`». Trang **không sập**: mọi chỗ gọi trong `app/views/write.py` có `except Exception`, nhưng người dùng thấy câu chung «Không xử lý được ảnh này» thay vì câu đúng | `test_sl_t107_1_libheif_runtime_error_becomes_fixed_message` (4 ca: `open_image`, `make_preview`, `make_web_image`, `make_ai_image`; file thật, sửa 4 byte cỡ đầu ra trong mô tả lưới) |

Cả hai đánh dấu `xfail(strict=True)` trong `tests/test_soi_loi_t107.py`. Đã chạy `--runxfail` để chắc chúng hỏng đúng lý do:
- SL-T107-1: `RuntimeError` lọt ra;
- SL-T107-2: không có `ImageProcessError`, `load` được gọi.

Đối chứng (qua): lưới thật của bộ mã hóa có đầu ra **bằng** cỡ ảnh, vẫn đọc được.

Gợi ý sửa (để Thợ Máy quyết):
- **SL-T107-2:** trong `_check_heif_grid`, từ chối khi `(width, height)` khác `image.size` (nhận cả hai chiều do xoay), hoặc `width * height > MAX_IMAGE_PIXELS`. Ảnh hợp lệ có cỡ đầu ra lưới đúng bằng cỡ ảnh: 156 ảnh lưới ở Việc 2 đều thỏa. Lưu ý trong `info["tiling"]`, `image_width` / `image_height` là cỡ trước khi bỏ phần thừa của ô, nên phải so với `ispe` chứ không so với số ô × cỡ ô.
- **SL-T107-1:** thêm `RuntimeError` (và `MemoryError`) vào danh sách bắt quanh `load()`, ra `_MSG_BROKEN`.

## Ghi nhận (không phải lỗi)

- **GN-1:** chỉ khi có mã khác đặt `pillow_heif.options.DECODE_THREADS` **song song** với lúc app mở ảnh, thì 1/600 lần mở dùng 4 luồng. Hiện không có mã nào như vậy trong app hay thư viện đã cài. Nếu sau này thêm thư viện dùng pillow-heif, Lá Chắn nên kiểm lại.
- **GN-2:** sau khi app đăng ký HEIF, mọi `Image.open` / `pillow_heif.open_heif` trong cùng tiến trình đều giải mã một luồng. Không ảnh hưởng gì: app không dùng HEIC ở chỗ khác.
- **GN-3:** các treo CPU khác của libheif 1.23.6 (Thợ Máy liệt kê ở «Còn lại») vẫn còn tới khi nâng libheif từ 1.23.7. Soi Lỗi không thử lại từng khuyến cáo đó, vì nằm ngoài phạm vi rút gọn.
- **GN-4:** `needed` lấy số lớn hơn của hai chiều ô (M9), nên lưới ô chữ nhật dựng cố ý được thừa ô tới (cạnh dài ô / cạnh ngắn ô) lần. Ví dụ ảnh 1024 × 100, ô 512 × 64: cần 4 ô, nhưng nhận tới 16 ô. Không có ở ảnh thật. Sửa SL-T107-2 (so cỡ đầu ra với `ispe`) không bịt chỗ này; muốn bịt thì chỉ tính một chiều. Để Thợ Máy quyết khi sửa SL-T107-2.

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t107.py`, 10 ca:
  - 7 `xfail(strict=True)` (SL-T107-1 ×4, SL-T107-2 ×3);
  - 2 ca bổ sung (HEIF đã đăng ký, số luồng bị đặt lại), qua;
  - 1 đối chứng lưới thật, qua.

  Chạy: `uv run pytest tests/test_soi_loi_t107.py -rxX`.
- Script (thư mục ghi chú chung của nhóm phiên, `T-107-soi-loi-scripts/`, chạy từ worktree bằng `.venv/Scripts/python.exe -X utf8 <script>`):
  - `sl107_threads.py`: luồng truyền libheif, luồng hệ điều hành, 8 luồng cùng mở, đăng ký lại;
  - `sl107_race.py`: 600 lần mở với mã khác đặt tùy chọn song song;
  - `sl107_correct.py`: quét 258 ảnh hợp lệ;
  - `sl107_speed.py`: tốc độ;
  - `sl107_fuzz.py`: 258 ca hỏng hoặc dựng;
  - `sl107_gridbomb.py`: mô tả lưới khai đầu ra lớn;
  - `sl107_gridrepeat.py`, `sl107_gridprobe.py`: lưới lặp ô (`SL107_TILE=1024` đổi cỡ ô);
  - `sl107_mutate.py`: thử đột biến.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm để chắc máy quét chạy): file test và báo cáo mới **0** phát hiện; file mồi 2 phát hiện.

---

# Lượt 3 · Tạm không nhận HEIC (LC-T107-2), chặn HEIC có alpha (LC-T107-1) · Soi Lỗi rút gọn

| Mục | Nội dung |
|---|---|
| Ngày nộp | 2026-10-30 (giao 18:40) |
| Mã nguồn | `team/T-107` tại `9b5501f` (Thợ Máy lượt 3, trên Lá Chắn `a9d381e`). Gộp thử với `main` `17b2a31` (đã có T-107 lượt 1–2, T-099 lượt 2) |
| Máy kiểm | Như trên; máy đang chạy toàn bộ test trên `main`, nên chỉ chạy test chọn lọc. Không chạy cloud, không đụng website |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (SL-T107-3: nháp cũ có ảnh `.heic` bị bỏ ảnh như «hỏng», lần tự lưu sau mất cả alt đã duyệt). Công tắc tắt thật ở mọi đường (0 lời gọi libheif ở cả 3 chế độ: tiến trình mới, plugin đăng ký sẵn, nhập muộn). Bật lại thì lượt 1–2 và chặn alpha còn nguyên. R5 khớp danh sách Chỉ Huy duyệt, không có thay đổi ngoài danh sách. Không lùi T-047, T-049, T-058, T-067, T-080, T-056. AVIF đúng như Thợ Máy nêu. Gộp `main` `17b2a31` sạch. Thử đột biến: nhánh bắt `RuntimeError` (SL-T107-1) không còn test nào đi qua; Soi Lỗi đã thêm 8 ca (qua). **SL-T107-3 không chặn Lá Chắn** |

## Tóm tắt (cho chủ dự án)

- **Đã tắt HEIC thật.** Không đường nào trong app đưa file HEIC cho thư viện libheif:
  - ảnh `.heic`, `.heif` không hiện trong khung chọn ảnh;
  - file HEIC đổi đuôi thành `.jpg`, `.png`, `.webp`, `.avif` vẫn hiện, nhưng bị chặn khi xem trước, gửi AI hay gửi WordPress, kèm câu «Tạm chưa nhận ảnh HEIC của iPhone, hãy dùng ảnh JPEG.»;
  - vẫn đúng khi thư viện HEIC đã được nạp sẵn hoặc nạp muộn.
- **Bật lại vẫn an toàn.** Đổi công tắc sang bật thì mọi chốt chặn cũ còn nguyên: giải mã một luồng, chặn lưới ô lạ, chặn ảnh có lớp trong suốt. File dựng cố ý trước đây làm app bận 11–14 giây, nay bị từ chối trong 0,3 giây.
- **Một lỗi nhỏ mới (Thấp), SL-T107-3:** bài nháp cũ đã chọn ảnh HEIC, mở lại thì ảnh đó bị bỏ, kèm câu «ảnh … bị hỏng». Phần chữ của bài vẫn giữ. Lần tự lưu sau xóa hẳn ảnh và alt đã duyệt. Không ảnh hưởng an toàn; nên báo đúng lý do và giữ ảnh lại để dùng tiếp khi bật lại HEIC.
- README đúng sự thật. Riêng AVIF đúng như Thợ Máy nêu: README ghi nhận AVIF nhưng app không mở được (có từ trước).

## Việc 1 · Công tắc tắt thật ở mọi đường — **đạt**, kèm SL-T107-3 (Thấp)

### Không đường nào gọi libheif khi tắt (`sl107l3_off.py`)

Cách kiểm:
- Mỗi chế độ chạy trong một tiến trình riêng. Tiến trình nạp module app (`process`, `folders`, `alt`, `tags`, `storage.drafts`).
- Sau đó gài bộ đếm vào **mọi hàm** của module C `_pillow_heif` (`load_file`, `get_lib_info`, `CtxWrite`, `load_plugin`…).
- Rồi chạy, với 11 file trong một thư mục ảnh thật: liệt kê thư mục, `open_image`, `make_preview`, `PreviewCache.get`, `make_ai_image`, `make_web_image`.
- 11 file gồm:
  - HEIC tên `.heic`, `.HEIC` (lưới), `.heif`, `.Heif`;
  - HEIC đổi đuôi `.jpg`, `.jpg` (lưới), `.png`, `.webp`, `.avif`;
  - HEIC sửa hộp `ftyp` chỉ còn nhãn `mif1`;
  - một JPEG thật.

| Chế độ | Lời gọi libheif | HEIF trong bảng Pillow sau đó | Liệt kê | File HEIC (tên HEIC hay đổi đuôi) | HEIC chỉ nhãn `mif1` | JPEG thật |
|---|---|---|---|---|---|---|
| Như app mới chạy | **0** | không (app không đăng ký) | 7 file: không có `.heic/.HEIC/.heif/.Heif` | mọi đường: «Tạm chưa nhận ảnh HEIC…»; `ImageRef` tên HEIC: «Chỉ nhận ảnh JPEG, PNG, WebP hoặc AVIF (tạm chưa nhận ảnh HEIC của iPhone).» | «không phải ảnh JPEG, PNG hoặc WebP đọc được» | mở được |
| Plugin HEIF **đã đăng ký sẵn** (`import pillow_heif.HeifImagePlugin`, `DECODE_THREADS = 4`, như test khác cùng tiến trình) | **0** | có (của mã khác, app không gỡ) | như trên | như trên | như trên | mở được |
| Nhập plugin **muộn** (chạy một lượt, rồi `import pillow_heif.HeifImagePlugin`, chạy lượt hai) | **0** cả hai lượt | lượt 1 không, lượt 2 có (do lệnh nhập) | như trên | như trên | như trên | mở được |

Lý do: khi tắt, `_open` gọi `Image.open(formats=["JPEG", "PNG", "WEBP"])`, nên Pillow không thử bộ mở HEIF dù bộ mở đã có trong bảng. File có nhãn HEIC bị chặn trước cả `Image.open`. Trong `app/`, `seo_app/` không còn `Image.open` nào khác. Không mã nào nhập `pillow_heif.HeifImagePlugin` hay gọi `register_heif_opener` ngoài `_register_heif`.

Kho thẻ ảnh sửa tay (`data/image_tags.sqlite`) có dòng trỏ tới ảnh `.heic`, lưu từ lúc HEIC còn bật: lúc tắt, dòng đó chỉ bị bỏ qua khi đọc (`_row_to_tag` trả `None`). Kho **không** bị coi là hỏng hay bị đổi tên, bật lại là dùng tiếp.

### Nháp cũ đã chọn ảnh `.heic` → **SL-T107-3 (Thấp)**

`sl107l3_draft.py` dùng kho nháp tạm, không đụng `data/` của app. Các bước:

1. Lưu nháp lúc HEIC bật, như trên `main` trước lượt 3. Nháp có hai ảnh đã duyệt alt: `IMG_0001.HEIC` và `IMG_0002.jpg`.
2. Tắt HEIC rồi mở lại:
   - `dropped_images = 1`, ảnh HEIC bị bỏ khỏi nháp, ảnh JPEG còn.
   - Trang Soạn bài (`restore_images`) báo: «1 ảnh đã chọn trong nháp bị hỏng nên đã bỏ; phần chữ của bài vẫn giữ. Hãy chọn lại ảnh cho các chỗ đó.»
   - Câu này sai lý do: ảnh không hỏng, chỉ là HEIC đang tạm tắt.
3. Bật lại khi chưa lưu lần nào: ảnh HEIC còn trong file nháp.
4. Lưu lại lúc tắt (lần tự lưu sau khi sửa chữ cũng vậy), rồi bật lại: ảnh HEIC và alt đã duyệt **mất hẳn**.

Nguyên nhân: `DraftImage._check_place` dựng `ImageRef`. Tên `.heic` nay bị `ImageRef` từ chối, nên `_drop_broken_image` coi đó là dữ liệu ảnh hỏng.

Mong đợi: giữ ảnh trong nháp như các ảnh không dùng được khác (file mất, thư mục đổi tên). Tức là `check_draft_images` trả `entry None` kèm câu có chữ «HEIC», bật lại là dùng tiếp. Không ảnh hưởng an toàn: ảnh bị bỏ thì không gửi đi đâu.

Test: `test_sl_t107_3_old_draft_heic_image_kept_with_heic_message`, `xfail(strict=True)`. Đã chạy `--runxfail` để chắc test hỏng đúng chỗ: `dropped_images == 1`. Thợ Máy muốn cách khác (vẫn bỏ ảnh nhưng báo đúng lý do) thì xin Chỉ Huy duyệt đổi kỳ vọng.

## Việc 2 · Bật lại (`True`): lượt 1–2 còn nguyên, chặn alpha đúng — **đạt**

Bật công tắc trong script bằng `SL107_HEIC=1`.

`sl107_threads.py`:

| Đường | Luồng truyền libheif | Luồng hệ điều hành |
|---|---|---|
| Đối chứng: `Image.open` với `DECODE_THREADS = 4` | 4 | +8 |
| `open_image`, `make_web_image`, `make_ai_image`, `make_preview` (mỗi đường sau khi mã khác đặt lại 4) | **0** | +1 |
| `Image.open`, `open_heif`, `read_heif` trực tiếp sau khi app đăng ký | 0 | +1 |
| 8 luồng app × 3 lần | 0 ở 24/24 lần, kết quả giống nhau | — |
| Mã khác đặt 4 liên tục trong lúc 8 luồng mở | 0/24 lần nhận 4 | — |

Lưới lặp ô dựng cố ý (`sl107_gridrepeat.py`, SL-T107-2 ở lượt 1), qua mọi đường app:

| Lưới | File | Lượt 1 (trước sửa) | Lượt 3 |
|---|---|---|---|
| 24 × 24 ô 512 (151 MP) | 19,7 kB | 9,3 s, 12,7 s, +108 MB | **0,4 s**, «cấu trúc lạ (lưới ô…)», +0 MB |
| 31 × 31 ô 512 (252 MP) | 20,5 kB | 11,1 s, 14,2 s, +250 MB | **0,3 s**, như trên |
| 21 × 21 ô 1024 (462 MP) | 16,0 kB | chưa đo | **0,3–0,4 s**, như trên |
| 31 × 31 ô 1024 (1008 MP) | 17,1 kB | chưa đo (máy thiếu RAM) | **0,3 s**, như trên |

Thử hàng loạt (`sl107_fuzz.py`, 258 ca × 2 lời gọi, bật HEIC): **0 sập, 0 treo, 0 lỗi lọt ra ngoài `ImageProcessError`**. Ở lượt 1 có 4 lỗi lọt (SL-T107-1). Ca chậm nhất 4,8 s (đột biến ngẫu nhiên lưới 12 MP, máy đang bận). Câu báo: 268 «không phải ảnh…», 36 «Ảnh bị hỏng…», 12 «cấu trúc lạ (lưới ô…)», 2 «quá nhiều điểm ảnh», 2 «File ảnh rỗng». Ca «mô tả lưới khai đầu ra 65535²» trước lọt `RuntimeError`, nay ra «cấu trúc lạ».

Chặn alpha:
- Có 4 ca của Lá Chắn: file 3 kB, ảnh chính 512 × 512, alpha là lưới 31 × 31 ô.
- Có 8 ca HEIC `RGBA`/`LA` của Thợ Máy, kiểm đủ 4 đường.
- Cả hai bộ đều qua: từ chối trước `load`.

Thử đột biến bên dưới cho thấy test bắt được:
- bỏ lời gọi chặn alpha;
- chỉ kiểm chữ `A` hoa (bỏ `RGBa`, `La`);
- dời phép chặn alpha ra sau `load`.

## Việc 3 · R5: bảng cũ → mới của Thợ Máy khớp diff test — **đạt**, không có thay đổi ngoài danh sách

Đối chiếu `git diff a9d381e 9b5501f -- tests/` (13 file, +333 −19). **Mọi dòng bị xóa** đều nằm trong danh sách Chỉ Huy duyệt:

| File | Dòng xóa | Nội dung | Trong danh sách duyệt |
|---|---|---|---|
| `test_app_images.py` | 3 | câu «… JPEG, PNG, WebP hoặc HEIC …» → «… JPEG, PNG hoặc WebP …» | có |
| `test_images_folders.py` | 7 | bỏ `x.heic`, `x.HEIF` khỏi danh sách nhận (chuyển sang test mới `test_image_ref_heic_only_when_enabled`, kiểm cả tắt lẫn bật); `IMAGE_EXTENSIONS` không còn HEIC (thêm kiểm `HEIC_EXTENSIONS`, `HEIC_ENABLED is False`); 2 kỳ vọng liệt kê `IMG_0001.HEIC` → không liệt kê (kỳ vọng cũ chuyển sang `test_list_folder_lists_heic_when_enabled`) | có (4 test) |
| `test_la_chan_t107.py` | 8 | đúng 2 decorator `xfail(strict=True)`: LC-T107-1 (4 ca), LC-T107-2 (1 ca); thân test giữ nguyên, LC-T107-1 thêm `heic_enabled` | có |
| `test_soi_loi_t049.py` | 1 | dòng nhập `naming, process` → `folders, naming, process`. Ca `[heic-trong-suot]` đổi kỳ vọng (bật: `_MSG_HEIF_ALPHA`; tắt: `_MSG_HEIC_OFF`), các ca khác giữ nguyên | có |

Còn lại chỉ là phần **thêm**:
- `conftest.py`: fixture `heic_enabled` (`monkeypatch`, tự trả lại sau test).
- `pytestmark`/`usefixtures("heic_enabled")` ở các file và test trong bảng «giữ nguyên ý» của Thợ Máy: `test_images_process`, `test_soi_loi_t049`, `test_soi_loi_t067`, `test_soi_loi_t107` (file của Soi Lỗi, chỉ thêm `pytestmark`), `test_t107_heif_mot_luong`, 1 test `test_ai_images`, 1 test `test_images_tags`, 1 test `test_soi_loi_t056`.
- Test mới `test_t107_heic_tat.py`, test alpha trong `test_t107_heif_mot_luong.py`.

Kiểm thêm test «qua suông»: tìm mọi file test dùng dữ liệu HEIC mà không bật công tắc. Có 13 file, tất cả hoặc chỉ trả lại trạng thái pillow-heif, hoặc gọi `pillow_heif` trực tiếp chứ không qua mã app (T-047, T-050, T-058, `test_pillow_heif_setup`). Không test nào qua chỉ vì HEIC bị từ chối sớm, trừ hai chốt chặn cố ý: LC-T093-3 và LC-T107-2. Hai chốt này đọc `ALLOWED_FORMATS` lúc nạp module, nên sẽ hỏng lại nếu ai sửa nguồn thành `True` mà libheif vẫn dưới 1.23.7.

## Việc 4 · Không lùi T-047, T-049, T-058, T-067, T-080, T-056; README — **đạt**

- Test chọn lọc trên `team/T-107` (`9b5501f` + test Soi Lỗi), 19 file: `test_soi_loi_t107`, `test_t107_heic_tat`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_la_chan_t107`, `test_pillow_heif_setup`, `test_soi_loi_t047`, `test_images_process`, `test_soi_loi_t049`, `test_pillow_version_t058`, `test_soi_loi_t058`, `test_soi_loi_t067`, `test_soi_loi_t080`, `test_images_folders`, `test_soi_loi_t056`, `test_app_images`, `test_ai_images`, `test_images_tags`, `test_drafts_images`. Kết quả: **2046 qua, 13 bỏ qua, 7 xfail, 0 hỏng, không XPASS** (18 phút, máy bận). 7 xfail gồm SL-T107-3 (mới), LC-T093-2 và 5 xfail cũ có từ trước của phiếu khác. Hai test Soi Lỗi bổ sung sau thử đột biến chạy riêng: qua. **T-047, T-049, T-058, T-067, T-080, T-056 không lùi.**
- README mục 9:
  - Câu «Tạm chưa nhận ảnh HEIC của iPhone (file `.heic`, `.heif`) … ảnh HEIC không hiện trong khung» đúng với file có tên HEIC.
  - File HEIC đổi đuôi `.jpg` vẫn hiện, nhưng bị chặn kèm câu «Tạm chưa nhận…» khi bấm. Không sai, chỉ thiếu ý; không cần sửa.
  - Đường dẫn «Cài đặt → Camera → Định dạng → Tương thích nhất» đúng tên mục trên iPhone tiếng Việt.
  - Ngoài dòng này, README và giao diện không còn chỗ nào nói app nhận HEIC.

## Việc 5 · AVIF — **đúng như Thợ Máy nêu** (ghi nhận, có từ trước)

Pillow 13 trên máy **đọc được** AVIF (`features.check("avif")` là `True`). Đã thử file AVIF thật (323 byte, `ftyp avif` + `mif1 miaf MA1B`):
- `.avif` có trong `IMAGE_EXTENSIONS`, nên khung chọn ảnh **liệt kê** `anh.avif`;
- cả 4 đường `open_image`, `make_preview`, `make_ai_image`, `make_web_image` báo «File này không phải ảnh JPEG, PNG hoặc WebP đọc được (có thể bị đổi đuôi hoặc hỏng).», vì `ALLOWED_FORMATS` không có AVIF (chủ ý từ T-047);
- README dòng 316 «App nhận ảnh JPG, PNG, WebP, AVIF» vì thế **không đúng**.

Không cần sửa trong phiếu này. Đề nghị như Thợ Máy: một phiếu nhỏ bỏ AVIF khỏi danh sách đuôi và README, vì thêm AVIF là thêm bộ giải mã phải lo.

## Việc 6 · Gộp thử với `main` `17b2a31` — **sạch**

- `main` chứa `a9d381e` (lượt 1–2). Từ đó tới `main`, chỉ README đổi một dòng ở mục «tạo thử một bài nháp» (T-108), không đụng mục ảnh.
- `git merge-tree --write-tree main team/T-107`: **không xung đột** (cây `cd45e9b`).
- Gộp thật ở worktree tạm tách rời (commit treo `c73225f`, không đẩy; đã kiểm `seo_app` nạp từ chính worktree tạm) rồi chạy test chọn lọc, 10 file: `test_soi_loi_t107`, `test_t107_heic_tat`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_la_chan_t107`, `test_images_folders`, `test_images_process`, `test_app_images`, `test_drafts_images`, `test_t106_trang_ket_noi`.
  - Kết quả: **792 qua, 12 bỏ qua, 2 xfail (SL-T107-3, LC-T093-2), 0 hỏng, không XPASS** (7,5 phút).
- Worktree tạm đã gỡ.

## Thử đột biến lượt 3 (`sl107l3_mutate.py`)

Mỗi đột biến chạy trên một bản sao riêng, sửa một chỗ trong `process.py` hay `folders.py`. Bộ test chạy gồm:
- `test_t107_heic_tat`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_la_chan_t107`, `test_soi_loi_t107`, `test_pillow_heif_setup`;
- 5 test liệt kê và `ImageRef` của `test_images_folders`;
- ca nguồn AI của `test_soi_loi_t049`.

| Đột biến | Test hỏng (đối chứng không đổi: 125 qua, 3 xfail) |
|---|---|
| L1 `_is_heic_container` luôn `False` | 11: 4 đường từ chối HEIC, HEIC đổi đuôi trong thư mục, 5 ca nhận dạng `ftyp`, `[heic-trong-suot]` |
| L2 chỉ xét nhãn chính (bỏ nhãn tương thích) | 1: `[mif1-heic]` |
| L3 luôn gọi `_register_heif` | 4: «định dạng khác mở được mà không đăng ký HEIF» × 4 đường |
| L4 `_allowed_formats` bỏ qua công tắc | 12, gồm chốt chặn LC-T107-2 |
| L5 bỏ kiểm theo nội dung | 6: 4 đường, HEIC đổi đuôi, `[heic-trong-suot]` |
| L6 liệt kê thư mục bỏ qua công tắc | 6: thư mục không liệt kê HEIC, `ImageRef` × 3, 2 test liệt kê |
| L7 công tắc mặc định bật | 18, gồm LC-T107-2 |
| L8 bỏ lời gọi chặn alpha | 13: 8 ca alpha Thợ Máy, 4 ca LC-T107-1, `[heic-trong-suot]` |
| L9 alpha chỉ xét chữ `A` hoa | 2: `[RGBa]`, `[La]` |
| L10 chặn alpha **sau** `load` | 12: 8 ca alpha («không gọi `load`»), 4 ca LC-T107-1 |
| L11 bỏ so đầu ra lưới với `ispe` (SL-T107-2) | 2: `[thua-dung-mot-o]`, `[nho-hon-anh]` |
| L12 bỏ trần điểm ảnh của lưới | 2: `[mot-o-khong-lo]`, `[sat-80mp-tong-o]` |
| L13 bỏ `RuntimeError` khỏi danh sách bắt quanh `load()` (SL-T107-1) | **0 lúc đầu: lọt.** Từ lượt 2, file của ca SL-T107-1 bị phép kiểm lưới chặn trước `load`, nên không ca nào còn đi qua nhánh này. Soi Lỗi thêm `test_libheif_error_while_decoding_becomes_fixed_message` (8 ca: `RuntimeError`, `MemoryError` × 4 đường, **qua**). Chạy lại L13: **4 hỏng** |
| L14 câu `ImageRef` cũ (không nhắc «tạm chưa nhận HEIC») | 3: `test_image_ref_heic_only_when_enabled` |
| L15 `HEIF_DECODE_THREADS = 4` | 10, gồm 2 ca bổ sung của Soi Lỗi lượt 1 |
| L16 bỏ đặt lại số luồng mỗi lần mở | 2: 2 ca bổ sung của Soi Lỗi lượt 1 |

Kết luận: sau khi thêm test cho L13, mọi đột biến làm đổi hành vi đều bị test bắt.

## Lỗi mới lượt 3

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T107-3** | Thấp | Tắt HEIC rồi mở lại nháp cũ đã chọn ảnh `.heic`: ảnh bị bỏ như «dữ liệu ảnh hỏng» (`dropped_images`), trang báo «ảnh … bị hỏng nên đã bỏ» (sai lý do); lần tự lưu sau xóa hẳn ảnh cùng alt đã duyệt, bật lại HEIC không còn | `test_sl_t107_3_old_draft_heic_image_kept_with_heic_message`, `xfail(strict=True)` |

## Ghi nhận lượt 3 (không phải lỗi)

- **GN-5:** `PreviewCache` trả ảnh xem trước **đã lưu** trước khi kiểm lại file.
  - Hệ quả: file HEIC đổi đuôi `.jpg` đã từng được xem trước lúc HEIC còn bật vẫn hiện ảnh nhỏ cũ trong khung chọn ảnh. Bấm «Chọn» thì `web_info` dựng lại từ file và báo «Tạm chưa nhận…».
  - Không gọi libheif, không gửi gì đi. Cache tự hết khi file đổi.
- **GN-6:** HEIC mà hộp `ftyp` chỉ có nhãn `mif1`/`msf1` (hợp lệ theo chuẩn, hiếm gặp) không bị `_is_heic_container` nhận ra. Khi tắt HEIC, file này nhận câu «không phải ảnh JPEG, PNG hoặc WebP đọc được» thay vì «Tạm chưa nhận ảnh HEIC». Vẫn không gọi libheif. Thợ Máy đã chủ ý để vậy (chú thích `_HEIC_BRANDS`).
- **GN-7:** `_MSG_NOT_IMAGE` và `ALLOWED_FORMATS` tính lúc nạp module. Fixture `heic_enabled` chỉ đổi công tắc, nên trong các test bật HEIC, câu «không phải ảnh…» vẫn là câu không nhắc HEIC. Sửa nguồn thành `True` thì cả hai được tính lại đúng. Đúng thiết kế (chốt chặn LC-T093-3, LC-T107-2 cần giá trị lúc nạp), chỉ cần biết khi viết test.

## Tệp lượt 3

- Test `tests/test_soi_loi_t107.py`, thêm:
  - 1 ca `xfail(strict=True)` (SL-T107-3);
  - 8 ca bổ sung, qua (`test_libheif_error_while_decoding_becomes_fixed_message`).

  Cả file: 18 qua, 1 xfail.
- Script mới (thư mục ghi chú chung, `T-107-soi-loi-scripts/`):
  - `sl107l3_off.py`: công tắc tắt, 3 chế độ;
  - `sl107l3_draft.py`: nháp cũ có ảnh HEIC;
  - `sl107l3_mutate.py`: thử đột biến lượt 3.

  Script cũ nhận `SL107_HEIC=1` để bật HEIC khi chạy.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện. `ruff check`, `ruff format --check` file test: sạch.

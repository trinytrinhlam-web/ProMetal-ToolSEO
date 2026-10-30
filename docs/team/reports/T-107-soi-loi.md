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

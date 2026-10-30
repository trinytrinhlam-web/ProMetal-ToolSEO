# Biên bản bảo mật T-107 · HEIC giải mã một luồng (LC-T093-3), kiểm lưới ô trước khi giải mã · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-107](../tickets/T-107-heif-tat-giai-ma-song-song.md) (file phiếu ở `main`, đọc ở checkout chính) · kiểm **rút gọn** (F1, F2, S1), kiểm chung cả hai lượt: lượt 1 `9a04a91`, lượt 2 `28f4a4d` |
| Phạm vi | Diff `1375e62..28f4a4d` trên `team/T-107`: `seo_app/images/process.py` (+79/−7), test mới của Thợ Máy `tests/test_t107_heif_mot_luong.py`, test của Soi Lỗi `tests/test_soi_loi_t107.py` (lượt 2 gỡ 2 dấu `xfail`), `tests/test_la_chan_t093.py` (gỡ dấu `xfail` LC-T093-3), 2 báo cáo. Không đổi `pyproject.toml`, `uv.lock`, `app/**`. Số dòng theo `28f4a4d` |
| Báo cáo đã đọc | [Thợ Máy](T-107-tho-may.md) (lượt 1, lượt 2), [Soi Lỗi](T-107-soi-loi.md) (SL-T107-1, SL-T107-2, GN-1 → GN-4); [Lá Chắn T-093](T-093-la-chan.md) (LC-T093-3) |
| Ngày | 2026-10-30 (13:11 → 14:13 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, **2 Trung bình** (LC-T107-1 mới; LC-T107-2 là phần còn lại của LC-T093-3, tách mã để theo dõi), 0 Thấp. **LC-T093-3 đóng**: lỗ hổng hỏng bộ nhớ GHSA-35mc-3887-rr37 (và kẹt GHSA-rcqc-842v-m26h) không còn đường tới, mọi đường mở HEIC đều một luồng. **SL-T107-1 đóng. SL-T107-2 đóng ở ảnh chính**; dạng dời lưới sang ảnh phụ alpha vẫn lọt → LC-T107-1. Không lùi T-047, T-058, T-080; không đổi phiên bản thư viện; `pip-audit` sạch. **Gộp `main` được ngay**: gộp thử với `main` `fd28bbc` không xung đột, cây gộp 12 file test 629 qua, 0 hỏng. T-107 làm app an toàn hơn `main` hiện tại; hai lỗi Trung bình đều có từ trước, không do T-107 gây ra. Điều kiện: LC-T107-1 sửa, LC-T107-2 có quyết định của chủ dự án, **trước khi đóng Giai đoạn 3** |

## Tóm tắt (cho chủ dự án)

- **Lỗ hổng nặng nhất đã được chặn.** Thư viện đọc ảnh HEIC (ảnh iPhone) có lỗi có thể làm hỏng bộ nhớ khi giải mã song song. Nay app đọc HEIC một luồng ở mọi chỗ, nên không còn đường tới lỗi đó.
- **Tôi thử thêm 29 file HEIC dựng cố ý.** Phần lớn được xử lý an toàn và nhanh: lưới khai sai cỡ, nhiều ảnh trong một file, ảnh độ sâu, ảnh nhỏ nhúng. Ảnh hợp lệ không bị chặn oan.
- **Còn 2 việc mức Trung bình.** Cả hai chỉ làm app bận hoặc tốn bộ nhớ: không chạy được mã lạ, không lộ dữ liệu. Muốn gặp, phải có người cố ý đặt file dựng sẵn vào thư mục ảnh của bạn.
  1. **Ảnh HEIC có lớp trong suốt khổng lồ (LC-T107-1).** Một file 3 kB bắt app giải mã 252 triệu điểm ảnh (thêm 330 MB bộ nhớ); dạng khác cần tới 1,5 GB. Cách sửa nhỏ: app từ chối ảnh HEIC có lớp trong suốt. Ảnh chụp điện thoại không có lớp này.
  2. **Thư viện libheif còn vài lỗi «làm treo» đã công bố (LC-T107-2).** Bản vá có ở libheif 1.23.7, nhưng pillow-heif (thư viện app dùng) chưa có bản mang 1.23.7. Một file vài kB làm app bận từ vài giây tới vài phút. **Cần bạn chọn một trong ba:**
     - chấp nhận tạm, ghi sổ rủi ro tới khi có bản mới (Lá Chắn khuyên);
     - tạm không nhận ảnh HEIC;
     - chờ bản mới rồi mới đóng Giai đoạn 3.
- **Gộp T-107 được ngay.** Phiếu này làm app an toàn hơn bản đang chạy.

## Lỗi phát hiện

| Mã | Mức | Có từ trước? | Mô tả | Test |
|---|---|---|---|---|
| **LC-T107-1** | **Trung bình** | Có: `main` giải mã ảnh phụ alpha như vậy từ T-047, T-049. T-107 không gây ra, không làm nặng thêm. **Vẫn còn sau khi nâng libheif 1.23.7**, vì đây là giới hạn của app | Giới hạn 80 triệu điểm ảnh (`process.py:66`, so ở `:278-280`) và `_check_heif_grid` (`:165-202`) chỉ xét **ảnh chính** (`image.size`, `info["tiling"]`). Ảnh chính có ảnh phụ alpha (`auxC` = `urn:mpeg:hevc:2015:auxid:1`, tham chiếu `auxl`) thì pillow-heif báo `RGBA` lúc mở, và libheif tự giải mã ảnh phụ trong cùng lời gọi giải mã. App không thấy cỡ hay lưới của ảnh phụ, nên không phép kiểm nào áp lên nó. Đo trên `28f4a4d` (mục «Biến thể đã thử»): file **3.057 byte** gồm ảnh chính 512 × 512 và alpha là lưới 31 × 31 ô 512, mọi ô trỏ cùng một mục. `open_image` **nhận ảnh**, CPU 5,4 s (giờ thực 21 s trên máy bận), bộ nhớ **+330 MB**. Ô 1024 (4,8 kB): cam kết bộ nhớ **~1,47 GB**, tiến trình thử bị dừng ở trần 700 MB. Đúng dạng SL-T107-2, chỉ dời lưới sang ảnh phụ; trái lời hứa ở docstring module («giới hạn số điểm ảnh … kể cả HEIC»). Đường thật: người dùng mở thư mục có file này. `image_grid` dựng ảnh xem trước cho mọi ảnh trong trang (`app/views/write.py:1528-1533`). libheif nhả GIL khi giải mã (đo: luồng chính vẫn chạy đều), nên server và các tab khác không đứng. Nhưng mỗi lần trang chạy lại (bấm nút, tải lại) lại mở thêm một lần giải mã, trong khi lần cũ vẫn chạy: CPU và bộ nhớ cộng dồn | `tests/test_la_chan_t107.py::test_lc_t107_1_big_alpha_rejected_before_decode` × 4 (`open_image`, `make_preview`, `make_web_image`, `make_ai_image`), `xfail(strict=True)`. File nhỏ để test nhanh: alpha 2048² trên ảnh 512². Mong đợi: từ chối trước `load`, câu cố định. Tiền đề `test_big_alpha_fixture_is_valid_heic` (qua): file là HEIC hợp lệ với libheif |
| **LC-T107-2** | **Trung bình** (lý do ở dưới bảng) | Có: phần còn lại của LC-T093-3. Biên bản T-093 đã ghi «sau: nâng pillow-heif … lúc đó các lỗi làm treo CPU mới hết» | libheif 1.23.6 còn **5 khuyến cáo «làm treo CPU» mà app chạm tới** (CVSS 7,5, chỉ ảnh hưởng tính sẵn sàng), vá ở 1.23.7: GHSA-48p4-gj45-w9v6 (giải mã lặp ảnh lớn trong ảnh dẫn xuất: lưới, ảnh chồng), GHSA-2g6j-vhr6-6wrj (nhiều ảnh mã hóa trong một mục), GHSA-7qm8-hj35-269r (lặp phép biến đổi ảnh), GHSA-hhg3-fxg7-3gxw (liên kết hồ sơ màu, **ngay lúc mở file**), GHSA-74mj-m37q-h3q9 (bảng `stsc`, **ngay lúc mở file**). Phép kiểm lưới của T-107 chỉ chặn dạng mẫu của GHSA-48p4 (ô 1 × 1, thừa ô); Thợ Máy ghi «Giảm», trên thực tế giảm rất ít. Đo trên `28f4a4d`: **lưới lồng lưới** (1,2–1,3 kB) qua mọi phép kiểm, libheif giải mã hàng nghìn ô rồi mới báo hỏng (CPU 4,5–10,3 s). **Lưới ô 64 mà mỗi ô là ảnh chồng** dán ảnh 2048² (5 kB): app nhận ảnh, CPU 7,1 s với 64 ô. Khuyến cáo đo được từ 26 s tới 17 phút với ảnh nguồn lớn hơn. Trần duy nhất hiện có là của chính libheif: tối đa 2 × `max_items` lần giải mã mục mỗi ảnh, mỗi ảnh tối đa 32768². Hai khuyến cáo chạy lúc mở file thì chạy trước mọi phép kiểm của app. pillow-heif mới nhất vẫn 1.8.1 (libheif 1.23.6), kiểm 30/10 | `tests/test_la_chan_t107.py::test_lc_t107_2_heic_not_decoded_by_libheif_with_known_cpu_advisories`, `xfail(strict=True)`. Mong đợi: app không nhận HEIF, hoặc libheif mang theo từ 1.23.7. Test tự báo XPASS khi nâng pillow-heif hay tắt HEIF |

**Vì sao LC-T107-2 là Trung bình, không phải Cao.** `security.md` mục 3 xếp «thư viện có lỗ hổng đã biết đang bị dùng tới» vào Cao. LC-T093-3 vì thế là Cao. Phần làm nó thành Cao là GHSA-35mc: dùng vùng nhớ đã giải phóng, có thể sập hay hỏng heap. Phần này đã đóng. Phần còn lại:
- chỉ làm bận CPU, tốn bộ nhớ (chính các khuyến cáo ghi: không ảnh hưởng an toàn bộ nhớ, không lộ dữ liệu);
- phải có người đặt được file vào thư mục ảnh, rồi người dùng mở thư mục đó (CVSS theo môi trường app: AV:L/UI:R, khoảng 5,5);
- khôi phục được: tắt app, bỏ file.

Đây là cùng loại và cùng mức với SL-T107-2 (Soi Lỗi xếp Trung bình), và với «thiếu timeout» trong bảng mức. Theo bảng mức, lỗi Trung bình phải có phiếu sửa, hay quyết định ghi sổ, **trước khi hết giai đoạn**.

**Cách sửa gợi ý.**

LC-T107-1: Thợ Máy quyết, nên làm ở lượt 3 của T-107 hay một phiếu ngắn.
- **(a) Khuyên dùng.** Từ chối HEIC có kênh alpha **trước khi giải mã**: `image.format == "HEIF"` và mode có `A`/`a` (`RGBA`, `RGBa`, `LA`, `La`), báo câu cố định. Gọi ngay sau `_check_heif_grid` trong `_open`. Đã mô phỏng trên máy: cả 4 ca LC-T107-1 qua, `load` không được gọi.
  - Phải đổi kỳ vọng của **một ca test cũ** của Soi Lỗi T-049: `tests/test_soi_loi_t049.py::test_ban_ai_moi_loai_nguon_qua_prepare_images[heic-trong-suot]` (ảnh HEIC trong suốt 64 × 48 hiện được nhận).
  - Đây là đổi hành vi có chủ đích, nên cần Chỉ Huy duyệt theo R5.
- **(b)** Nếu muốn giữ HEIC trong suốt: tự đọc khung HEIF (`iinf`, `iref`, `ipma`, `ispe`, mô tả lưới) trước `Image.open`. Chặn alpha lớn hơn ảnh chính, alpha là lưới hay ảnh chồng. Cách này nhiều mã đọc dữ liệu chưa tin cậy hơn, phải kiểm lại cả Soi Lỗi lẫn Lá Chắn.

LC-T107-2: chủ dự án chọn một trong ba, trước khi đóng Giai đoạn 3.
1. **Ghi sổ rủi ro có thời hạn** tới khi pillow-heif mang libheif ≥ 1.23.7 (Lá Chắn khuyên; câu đề xuất ở mục «Đề xuất ghi sổ»). Có bản mới thì nâng ngay (chủ dự án duyệt, Lá Chắn rút gọn D1).
2. **Tạm không nhận HEIC.** Phải bỏ `"HEIF"` khỏi `ALLOWED_FORMATS`, bỏ `.heic`, `.heif` khỏi `IMAGE_EXTENSIONS` (`folders.py:53`), đổi kỳ vọng nhiều test HEIC. Thay đổi lớn hơn cách 1. Ảnh Zalo là JPEG, và app chưa dùng ảnh HEIC thật nào.
3. Chờ bản mới rồi mới đóng Giai đoạn 3.

## Biến thể đã thử (việc 2)

File dựng bằng script riêng (mục «Tệp, cách chạy lại»): ô HEVC lấy từ bộ mã hóa đi kèm pillow-heif, khung HEIF tự ghi. Mỗi ca chạy `process.open_image` trên `28f4a4d` trong một tiến trình con riêng, có trần bộ nhớ 700 MB và hạn giờ. Máy đang chạy toàn bộ test của Chỉ Huy song song (RAM trống khoảng 0,9 GB), nên đo **thời gian CPU** của tiến trình; giờ thực dài hơn 2–5 lần.

| Nhóm | File | Kết quả | CPU / bộ nhớ |
|---|---|---|---|
| Lưới khai sai `ispe` | SL-T107-2 gốc: lưới 31 × 31 ô 512, `ispe` 4032 × 3024 (2.961 B) | «cấu trúc lạ», **trước khi giải mã** | 0,22 s (giờ thực) |
| | Ô khai `ispe` 512 mà dòng HEVC thật 2048², lưới 8 × 6 (4.949 B) | libheif từ chối sau ô đầu → «Ảnh bị hỏng» | 0,30 s |
| | Ô khai 64 × 64 (đúng ngưỡng) mà thật 1024², lưới 16 × 16 (2.517 B) | như trên | 0,31 s |
| | Ảnh đơn khai 512² mà thật 2048² (4.760 B) | như trên | 0,35 s |
| Ô trỏ lặp | Lưới 8 × 6 ô 512 cùng một mục, cỡ khớp (1.135 B) | nhận; công giải mã bằng ảnh 12 MP thật (đúng thiết kế: không vượt ảnh hợp lệ cùng cỡ) | 2,4 s (giờ thực) |
| | Ảnh chồng (`iovl`) làm ảnh chính, dán 60 / 960 lần (1,4 / 6,8 kB) | libheif không dựng ảnh (thử 8 → 960 tham chiếu; 1–3 tham chiếu thì dựng được, không có `info["tiling"]`, công giải mã ≤ 3 ô); Pillow coi là «không phải ảnh … đọc được» | 0,3 s |
| | **Lưới lồng lưới**: lưới 8 × 6 ô «512», mỗi ô là cùng một lưới con 4 × 4 / 8 × 8 ô 512 (1.228 / 1.324 B) | qua mọi phép kiểm (lưới ngoài trông như ảnh iPhone); libheif giải mã rồi mới báo «Ảnh bị hỏng». Lưới con 30 × 30, 31 × 31 vẫn mở được (2,9–3,1 kB). CPU tăng 2,3 lần khi số ô tăng 4 lần, khớp với trần «2 × `max_items` lần giải mã» của libheif → **LC-T107-2** | **4,5 s / 10,3 s**; bộ nhớ không tăng |
| | **Lưới ô ảnh chồng** (dạng GHSA-48p4, ô 64): lưới 8 × 8 ô 64, mỗi ô là cùng một ảnh chồng 64 × 64 dán ảnh HEVC 2048² (5.074 B) | **nhận** ảnh 512 × 512 → **LC-T107-2** | **7,1 s** |
| Nhiều ảnh trong một file | Ảnh chính 512²; ảnh thứ hai (không ẩn) là lưới 31 × 31 ô trỏ lặp (3.003 B) | chỉ giải mã ảnh chính | 0,30 s |
| | 900 ảnh đơn (38,7 kB) / 40 lưới 31 × 31 đứng trước ảnh chính (80 kB) | mở và giải mã bình thường, chỉ ảnh chính | mở 0,12 / 0,09 s; giải mã 0,31 / 0,30 s |
| Ảnh phụ | Ảnh độ sâu (`auxC` depth) lưới 31 × 31 (3.057 B) | không giải mã (`DEPTH_IMAGES` tắt) | 0,23 s |
| | Ảnh nhỏ (`thmb`) lưới 31 × 31 (3.017 B) | không giải mã (`THUMBNAILS` tắt) | 0,20 s |
| | **Alpha** lưới 8 × 8 / 16 × 16 / 31 × 31 ô 512 (1,3 / 1,6 / 3,1 kB) | **nhận** ảnh 512 × 512 RGBA → **LC-T107-1** | 0,56 / 1,77 / **5,36 s**; +0 / +67 / **+330 MB** |
| | **Alpha** lưới 22 × 22 / 31 × 31 ô 1024 (3,8 / 4,8 kB) | cam kết **~754 MB / ~1.470 MB** thì bị trần thử dừng → **LC-T107-1** | — |
| | Alpha là ảnh chồng dán 3 lần (1.139 B) | nhận | 0,30 s |
| Ảnh hợp lệ | Ảnh đơn (không lưới) 32 × 32, 100 × 40, 2000 × 50 | nhận (ảnh đơn không có `info["tiling"]`, không qua phép kiểm lưới) | ≤ 0,3 s |
| | Lưới ô 512, ảnh 4032 × 40; RGBA 1024 × 768 | nhận | — |

Ảnh hợp lệ khác: Soi Lỗi đã quét 258 ca (156 ảnh lưới, ô 64 → 1024, 8 chiều xoay). Test của Thợ Máy có ảnh 12 MP ngang và dọc, 48 MP, 64 MP, `clap` cắt phần thừa, ảnh đã xoay mà lưới chưa xoay. Tất cả đều được nhận; Lá Chắn không chạy lại.

## Kiểm từng việc

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| **1. LC-T093-3 đóng** | **Đóng** | `_register_heif` (`process.py:144-162`) đặt `heif_options.DECODE_THREADS = 0` **mỗi lần**, trước `Image.open` (`_open` gọi ở `:274`, mở ở `_pillow_open` `:262`). Lần đăng ký đầu truyền thêm `decode_threads=0` (`:157-162`). pillow-heif đọc tùy chọn này lúc mở: `HeifFile.__init__` → `_pillow_heif.load_file(fp_bytes, options.DECODE_THREADS, …)` (`heif.py:319-321`), tức `heif_context_set_max_decoding_threads(ctx, 0)`. Grep `app/`, `seo_app/`, `scripts/`: `Image.open` duy nhất là `process.py:262`, và chỉ `process.py` nhập `pillow_heif`. Văn bản khuyến cáo: GHSA-35mc chỉ xảy ra khi giải mã song song; GHSA-rcqc ghi «single-threaded decoding does not produce this lock-order deadlock». Test LC-T093-3 của Lá Chắn qua; gỡ `xfail` đúng R5 (chỉ xóa 4 dòng decorator) |
| **1b. Ca lý thuyết 1/600 (GN-1 Soi Lỗi): có cần khóa quanh `open`?** | **Không cần; ghi nhận** | Thứ nhất, trong tiến trình chỉ `_register_heif` ghi tùy chọn này, và luôn ghi 0. pillow-heif chỉ ghi khi `register_heif_opener` được gọi kèm `decode_threads=` (`as_plugin.py:269`). Grep `.venv/Lib/site-packages` (trừ chính `pillow_heif`): không gói nào gọi `register_heif_opener` hay đặt `DECODE_THREADS`. Thứ hai, khóa của app không chặn được mã ngoài, vì mã ngoài không giữ khóa đó. Giữa các luồng của app, mọi luồng đều ghi 0, nên khóa không thêm gì; khóa bọc cả `load` còn làm mọi lần mở HEIC phải chờ nhau. Rào thật là kiểm thư viện mới (S1, D1): khi thêm hay nâng thư viện, Lá Chắn grep `register_heif_opener(` và `DECODE_THREADS` (nên thêm vào bước «Khi có bản mới» trong báo cáo Thợ Máy) |
| **2. SL-T107-1 đóng thật** | **Đóng** | `_open` bắt thêm `RuntimeError`, `MemoryError` quanh `open`/`load` (`:296`), ra câu cố định `_MSG_BROKEN`. 4 ca của Soi Lỗi qua; gỡ `xfail` đúng R5 (lượt 2 chỉ xóa 2 decorator, 17 dòng). Trong 29 file tôi dựng và 5 ảnh hợp lệ của bộ mã hóa, không lỗi nào lọt ra ngoài `ImageProcessError` (trừ các ca bị trần bộ nhớ thử dừng trước khi xong). File làm pillow-heif trả danh sách ảnh rỗng (`IndexError` ở `HeifFile.size`) thì Pillow bắt lúc mở, ra «không phải ảnh … đọc được» |
| **2b. SL-T107-2 đóng thật; biến thể gần** | **Đóng ở ảnh chính.** Ảnh phụ alpha → **LC-T107-1**. Lưới lồng lưới, lưới ô ảnh chồng → **LC-T107-2** | So cỡ lưới với `image.size` (cả hai chiều do xoay, dung sai dưới một ô cho `clap`), trần 80 MP cho cả đầu ra lẫn tổng điểm ảnh mọi ô (`:195-202`). File gốc của Soi Lỗi bị từ chối trước giải mã trong 0,22 s; 3 ca của Soi Lỗi qua. Bốn nhóm biến thể Chỉ Huy giao, kết quả từng file ở mục «Biến thể đã thử»: **lưới khai sai `ispe`** an toàn (app hay libheif từ chối trong ≤ 0,35 s); **ô trỏ lặp**: cỡ khớp thì công giải mã không vượt ảnh hợp lệ cùng cỡ, còn lưới lồng lưới, lưới ô ảnh chồng thì lọt; **nhiều ảnh trong một file** an toàn (chỉ ảnh chính được giải mã); **ảnh phụ lớn**: ảnh độ sâu, ảnh nhỏ an toàn, alpha lọt. **Ảnh hợp lệ không bị chặn oan** (bảng trên). Ghi nhận 2 |
| **3. Không lùi T-047, T-058, T-080; không đổi thư viện** | **Đạt** | `git diff 0122d4b 28f4a4d -- pyproject.toml uv.lock`: rỗng. `_register_heif` vẫn tắt ảnh nhỏ, ảnh độ sâu, ảnh phụ, đặt `DISABLE_SECURITY_LIMITS = False`, không gọi `load_libheif_plugin` (T-047 ĐK 3). Pillow 13.0.0 (T-058). Test T-047 (`test_pillow_heif_setup`, `test_soi_loi_t047`), T-058 (`test_pillow_version_t058`, `test_soi_loi_t058`), T-080 (`test_soi_loi_t080`) qua trên cây gộp (việc 4) |
| **3b. `pip-audit`, thư viện C (như T-047)** | **Sạch** (trừ LC-T107-2) | Mục «Công cụ quét» |
| **4. Gộp thử với `main` mới nhất trên máy (`fd28bbc`)** | **Không xung đột** | `git merge-tree --write-tree fd28bbc 28f4a4d` → cây `8ab011a`. Từ `0122d4b` tới `fd28bbc`, `main` không sửa `seo_app/images`, `pyproject.toml`, `uv.lock`; `tests/test_la_chan_t093.py` trên `main` (đã gỡ `xfail` LC-T093-1 ở T-106) và trên nhánh (gỡ LC-T093-3) gộp sạch. Xuất cây gộp bằng `git archive`, chạy bằng `.venv` của `wt-T-107` (đã kiểm `seo_app` nạp từ cây gộp). 12 file test ảnh, HEIF: `test_soi_loi_t107`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_pillow_heif_setup`, `test_soi_loi_t047`, `test_pillow_version_t058`, `test_soi_loi_t058`, `test_soi_loi_t080`, `test_images_process`, `test_soi_loi_t049`, `test_soi_loi_t067`, `test_app_images`. Kết quả **629 qua, 5 xfail có sẵn** (LC-T093-2, SL-T067-1 × 4), **0 hỏng**, không XPASS (1.087 s). Thêm `test_la_chan_t107.py` vào cây gộp: 3 qua, 6 xfail (LC-T107-1 × 4, LC-T107-2, LC-T093-2) |
| F1 (đọc file từ máy) | **Đạt** | Không đổi đường đọc thư mục ảnh (`folders.py`); byte vẫn qua giới hạn dung lượng trước khi tới `_open` |
| F2 (xử lý file chưa tin cậy) | **Đạt có điều kiện** | Một luồng, phép kiểm lưới trước khi giải mã, mọi lỗi giải mã thành câu cố định. Hai chỗ hở là LC-T107-1 và LC-T107-2 |
| S1 (thư viện) | **Đạt có điều kiện** | Không đổi phiên bản; `pip-audit` sạch; thư viện C: LC-T107-2 |

## Đề xuất ghi sổ (nếu chủ dự án chọn cách 1 cho LC-T107-2)

Dòng cho `security.md` mục 6. Chỉ Huy hoặc Thư Ký ghi sau khi chủ dự án đồng ý; Lá Chắn không sửa `security.md` ở phiếu này.

> | 2026-10-30 | Đọc ảnh HEIC (`seo_app/images/process.py`; pillow-heif 1.8.1 mang libheif 1.23.6; LC-T107-2): file HEIC dựng cố ý, vài kB, làm app bận từ vài giây tới vài phút khi dựng ảnh xem trước (GHSA-48p4-gj45-w9v6, GHSA-2g6j-vhr6-6wrj, GHSA-7qm8-hj35-269r, GHSA-hhg3-fxg7-3gxw, GHSA-74mj-m37q-h3q9; vá ở libheif 1.23.7) | Chỉ làm bận, tốn bộ nhớ: không chạy được mã, không lộ dữ liệu. Phải đặt được file vào thư mục ảnh; tắt app, bỏ file là hết. App đã giải mã một luồng (đóng phần hỏng bộ nhớ GHSA-35mc, T-107). **Có thời hạn:** nâng pillow-heif ngay khi có bản mang libheif ≥ 1.23.7; test `test_lc_t107_2_…` tự báo khi nâng. Lá Chắn T-107 xếp Trung bình | Chủ dự án |

## Ghi nhận (không phải lỗi)

1. **Báo cáo Thợ Máy, mục «Còn lại».** Ba điểm cần chỉnh:
   - GHSA-48p4 ghi «Giảm», nhưng trên thực tế phép kiểm lưới chỉ chặn dạng mẫu. Dạng ô 64 và lưới lồng lưới vẫn lọt (LC-T107-2).
   - Danh sách khuyến cáo không dùng tới thiếu GHSA-hpg4-g2gc-pq42 (tràn heap khi đệm khung của chuỗi ảnh) và GHSA-73j7-gvm9-x8q6. Cả hai chỉ xảy ra khi giải mã chuỗi ảnh (track). Module C của pillow-heif 1.8.1 chỉ có `load_file`, `CtxWrite`, `get_lib_info`, `load_plugin(s)`, không giải mã track, nên **không tới**.
   - GHSA-pfcm-ffqg-84hx, GHSA-r9cg-w542-g7hj (công cụ dòng lệnh), GHSA-9rpf-2x22-78m9 (mã hóa), GHSA-gff5-3vgr-p8h2 (gdk-pixbuf) cũng không dùng tới.

   Nhận định của Thợ Máy về GHSA-35mc và GHSA-rcqc đúng với văn bản khuyến cáo.
2. **Dung sai `clap` dưới một ô.** Ảnh HEIC có `clap` cắt hơn một ô mỗi chiều (cắt ảnh kiểu không phá hủy) sẽ bị từ chối «cấu trúc lạ». Ảnh điện thoại không có dạng này. Đây là hướng an toàn, và câu báo dặn xuất sang JPEG. Chấp nhận như Thợ Máy đã ghi.
3. **Ảnh có nhiều khung** (nhiều ảnh trong một file): `is_animated` đúng nên pillow-heif giữ lại cả file trong đối tượng ảnh tới khi đóng. App không `seek`, không dùng khung khác. Không ảnh hưởng.
4. **Bộ nhớ thử.** Tôi không giải mã hết các file vượt 700 MB, vì máy chỉ còn khoảng 0,9 GB RAM trống. Số «~1.470 MB» là bộ nhớ cam kết lúc tiến trình bị dừng, không phải đỉnh cuối cùng.
5. **AVIF.** `folders.py:53` liệt kê đuôi `.avif`, nhưng `ALLOWED_FORMATS` không có AVIF, và wheel pillow-heif chỉ có bộ giải mã HEVC (`libheif_info()`: `libde265`). Các khuyến cáo AV1/libaom (GHSA-jx54, GHSA-fpr5) và OpenH264 (GHSA-xwcv) vì thế không tới.

## Việc 6 · Sau T-107, Giai đoạn 3 còn thiếu gì để đóng

Không kể quyết định của chủ dự án đã có trong `TIEN-DO.md` mục 4, và T-078.

1. **Gộp T-107 vào `main`** (Chỉ Huy), chạy toàn bộ test trên Windows.
2. **Sửa LC-T107-1** (Trung bình).
   - Ai làm: Thợ Máy, ở lượt 3 của T-107 hay một phiếu ngắn. Vài dòng trong `_open`, theo cách (a).
   - Đổi kỳ vọng một ca test T-049; Chỉ Huy duyệt R5.
   - Kiểm: Soi Lỗi và Lá Chắn rút gọn.
3. **Thêm vào danh sách quyết định của chủ dự án:** LC-T107-2. Ba cách: ghi sổ có thời hạn (Lá Chắn khuyên), tạm không nhận HEIC, hay chờ bản mới.
4. **Sổ rủi ro** (Chỉ Huy hoặc Thư Ký, `security.md` mục 6):
   - sửa 2 dòng biên bản T-093 đã nêu: dòng `unfiltered_html`, và số dòng cũ ở dòng LC-T048-6 (`folders.py:163`, `:644` → `_same_file`);
   - ghi các dòng chủ dự án chấp nhận: LC-T107-2 nếu chọn cách 1; LC-T093-2, N1 → N5 nếu chọn ghi sổ.

**Không chặn đóng:**
- SL-T106-1 (`wordpress.py:124` vẫn «hoặc Quản trị viên») và SL-T108-1 (README dòng 7), đều Thấp, vẫn còn trên `main` `fd28bbc`;
- thử ảnh HEIC chụp thật từ iPhone (T-049 ĐK 7). Nên làm ngay sau khi sửa LC-T107-1, để chắc ảnh thật không bị chặn oan;
- kiểm lại bằng Fable sau 01/11.

## Công cụ quét, test

| Công cụ | Kết quả |
|---|---|
| `pip-audit` | `uv export --frozen --no-hashes --no-emit-project`: 69 gói cố định. `uvx pip-audit -r … --no-deps --disable-pip`: nguồn PyPI và nguồn OSV đều «No known vulnerabilities found». OSV, `pillow-heif` 1.8.1: không có mục nào |
| `uv pip check` | 1 chỗ lệch: Streamlit cần `pillow<13`, có 13.0.0 (có chủ đích, T-058). `uv 0.13.4` |
| Thư viện C | **pillow-heif** 1.8.1 vẫn là bản mới nhất: PyPI, và GitHub `bigcat88/pillow_heif` (phát hành 11/10). **libheif**: bản mới nhất 1.23.7 (26/10). Trong 16 khuyến cáo của bản này: GHSA-35mc, GHSA-rcqc không còn đường tới (một luồng); GHSA-48p4, GHSA-2g6j, GHSA-7qm8, GHSA-hhg3, GHSA-74mj → LC-T107-2; còn lại không tới (Ghi nhận 1, 5). OSV-2020-2308, OSV-2023-1129: như T-093 (N2). **libde265**: bản mới nhất 1.1.3 (14/09); khuyến cáo mới nhất GHSA-vm5w-mrw5-q329 đã vá ở 1.1.3 |
| ruff | `ruff check .`: All checks passed! `ruff format --check tests/test_la_chan_t107.py`: đã đúng định dạng |
| bandit (`PYTHONUTF8=1`) | `seo_app/images/process.py`: 0 vấn đề, 810 dòng, không lỗi chạy |
| detect-secrets (`PYTHONUTF8=1`, `--all-files`, kèm file mồi) | File mồi: 3 phát hiện (máy quét có chạy). `tests/test_la_chan_t107.py`, biên bản này: 0 |
| pytest trên nhánh | `tests/test_la_chan_t107.py`: 1 qua, 5 xfail. `--runxfail`: 5 ca hỏng đúng lý do, gồm 4 ca «DID NOT RAISE ImageProcessError» (app nhận ảnh) và 1 ca `assert (not True or (1, 23, 6) >= (1, 23, 7))` |
| pytest trên cây gộp | Việc 4: 629 qua, 5 xfail có sẵn, 0 hỏng; với test mới: 3 qua, 6 xfail |
| Soát R5 | `test_la_chan_t093.py`: chỉ xóa 4 dòng `xfail` LC-T093-3. `test_soi_loi_t107.py` lượt 2: chỉ xóa 2 decorator `xfail` (17 dòng). `test_t107_heif_mot_luong.py` là file của chính Thợ Máy: lượt 2 thêm ca nhận, ca từ chối, không bỏ phép kiểm nào. Lá Chắn chỉ thêm `tests/test_la_chan_t107.py` |

## Tệp, cách chạy lại

- Test: `tests/test_la_chan_t107.py`, gồm 1 tiền đề, LC-T107-1 × 4, LC-T107-2. Chạy: `uv run pytest tests/test_la_chan_t107.py -rxX`; thêm `--runxfail` để xem lý do hỏng. Khi sửa xong, test tự báo XPASS; lúc đó **chỉ xóa** dấu `xfail` (R5).
- Script thử, ngoài repo, nằm trong thư mục ghi chú chung của nhóm phiên `T-107-la-chan-scripts/`:
  - `lc107_heif.py`: bộ dựng file HEIF (ô HEVC từ pillow-heif, khung tự ghi);
  - `lc107_variants.py`: các ca ở mục «Biến thể đã thử».
  - Chạy từ worktree: `.venv/Scripts/python.exe -X utf8 <thư mục>/lc107_variants.py v4a_alpha_grid:31,31 v2b_nested_grid:4 …`. Mỗi ca chạy trong tiến trình con; cha canh bộ nhớ, mặc định trần 700 MB (`LC107_CAP_MB`), hạn 180 s (`LC107_TIMEOUT`).
  - **Đừng chạy** các ca ô 1024 (`v4e_*`) khi máy còn ít RAM.
- Không mở app thật (không cần cho phiếu này), không đụng `launch.json`, không đụng website, không chạy cloud. Cây gộp xuất ra thư mục nháp của phiên; không tạo worktree tạm.

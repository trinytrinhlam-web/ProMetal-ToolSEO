# Báo cáo T-107 · HEIC giải mã một luồng (LC-T093-3)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | T-107 `T-107-heif-tat-giai-ma-song-song.md` (Chỉ Huy commit lên `main`, nhánh này không chứa) |
| Nhánh | `team/T-107` (từ `1375e62`: `main` `0122d4b` + T-093) |
| Ngày nộp | 2026-10-30 09:00 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đã chặn lỗ hổng mức **Cao** của thư viện đọc ảnh HEIC (ảnh iPhone). App nay giải mã ảnh HEIC **một luồng** thay vì 4 luồng song song. Lỗ hổng (dùng vùng nhớ đã giải phóng, có thể làm app sập) chỉ xảy ra khi giải mã song song, nên không còn đường tới.
- Thêm một lớp kiểm trước khi giải mã: ảnh HEIC có lưới ô lạ (ô nhỏ hơn 64 điểm ảnh, hoặc thừa ô) bị từ chối, kèm câu báo tiếng Việt. Ảnh điện thoại thật (ô 512 × 512) không bị ảnh hưởng.
- Ảnh HEIC vẫn đọc đúng, giữ GPS, xoay đúng chiều. Đổi lại, ảnh HEIC chậm hơn khoảng **1–2 giây mỗi ảnh**. Ảnh JPEG (ảnh Zalo) không đổi gì.
- **Chưa** đổi phiên bản thư viện. pillow-heif 1.8.1 vẫn là bản mới nhất (kiểm 30/10). Khi có bản mang libheif 1.23.7 trở lên, nên nâng để vá hẳn các lỗi «làm treo máy» còn lại; việc này cần bạn duyệt (mục «Khi có bản mới»).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/process.py` | `HEIF_DECODE_THREADS = 0`. `_register_heif` đặt `heif_options.DECODE_THREADS = 0` **mỗi lần** trước khi mở ảnh (như các tùy chọn tắt ảnh nhỏ, ảnh độ sâu, ảnh phụ, vẫn giữ nguyên), và truyền `decode_threads=0` khi đăng ký lần đầu. Thêm `_check_heif_grid` (gọi trong `_open` ngay sau phép so số điểm ảnh, trước `load`): ảnh HEIF có `info["tiling"]` mà ô nhỏ hơn `MIN_HEIF_TILE_EDGE = 64`, số ô nhiều hơn số ô cần để phủ kín ảnh, hay thông tin lưới sai kiểu thì `ImageProcessError(_MSG_HEIF_GRID)`, chưa giải mã ô nào. Docstring module cập nhật |
| `tests/test_t107_heif_mot_luong.py` (mới) | 11 hàm test, 29 ca (xem mục Đối chiếu yêu cầu) |
| `tests/test_la_chan_t093.py` | Gỡ dấu `xfail(strict=True)` của `test_lc_t093_3_…` (XPASS). Chỉ xóa dấu, điều kiện kiểm không đổi (R5) |

## Đối chiếu yêu cầu

| Yêu cầu | Cách làm | Bằng chứng |
|---|---|---|
| 1. Giải mã một luồng, đúng chỗ đăng ký, trước mọi lần mở; giữ tùy chọn cũ | `_register_heif` (chỗ duy nhất, gọi trong `_open` trước `Image.open`) đặt `DECODE_THREADS = 0`; pillow-heif chuyển giá trị này vào `_pillow_heif.load_file` (`heif.py:319-321`), tức `heif_context_set_max_decoding_threads(ctx, 0)` theo khuyến cáo. Ai đó đặt lại 4 thì lần mở sau về 0 | `test_every_open_passes_zero_threads_to_libheif` (bắt đúng đối số truyền xuống `load_file` ở cả `open_image`, `make_web_image`, `make_ai_image`, `make_preview`, sau khi cố ý đặt 4); `test_register_heif_sets_single_thread_every_call`; `test_first_registration_also_single_thread`; test Lá Chắn LC-T093-3 qua. Đếm luồng hệ điều hành của tiến trình lúc giải mã ảnh 48 ô (ảnh 12 MP): đặt 4 thì từ 2 lên 10 luồng; đặt 0 thì chỉ thêm 1 luồng (2 lần đo: 1 → 2, 2 → 3), nhiều khả năng là luồng riêng của bộ giải mã HEVC libde265, không phải luồng giải mã song song ô lưới của libheif |
| 2. Giới hạn kích thước, ô lưới | **Làm được một phần.** Thêm `_check_heif_grid` (ô ≥ 64, không thừa ô). Chặn đúng dạng file mẫu của GHSA-48p4-gj45-w9v6 (lưới ô 1 × 1 cắt từ ảnh chồng 8192 × 8192: file 2,6 kB giải mã 26 giây). Giới hạn 80 triệu điểm ảnh (có từ T-049) vẫn áp cho HEIC. **Không làm được** trong phạm vi: giới hạn **thời gian** giải mã (mã C của libheif không ngắt được giữa chừng trong cùng tiến trình; muốn ngắt phải giải mã ở tiến trình con, đổi kiến trúc lớn), và chặn các lỗi treo CPU khác (xem «Còn lại») vì pillow-heif không cho xem cấu trúc bên trong file trước khi libheif xử lý | `test_strange_grids_rejected_before_decode` (10 ca), `test_real_phone_grids_accepted` (7 ca: iPhone 12 MP ngang, dọc, 48 MP, ô chữ nhật…), `test_open_rejects_strange_grid_without_decoding` (đường thật: dừng trước `load`, không giải mã ô nào) |
| 3. Ảnh HEIC đọc đúng, GPS, xoay; số đo tốc độ | Ảnh lưới kiểu iPhone (ô 512, EXIF có GPS, chiều xoay 6) ra WebP giữ đúng GPS, xoay đúng một lần, đúng màu bốn góc; giải mã một luồng ra **đúng từng byte** như 4 luồng | `test_grid_heic_rotated_keeps_gps_and_turns_once`, `test_grid_heic_pixels_same_as_parallel_decode`; số đo ở mục dưới |
| 4. Gỡ `xfail` LC-T093-3; test ảnh, HEIF, T-047, T-058, T-080 qua | Đã gỡ dấu | Mục Kiểm thử |
| 5. Không đổi phiên bản; ghi phiên bản, cách kiểm bản mới | `pyproject.toml`, `uv.lock` không đổi | Mục «Phiên bản» |

## Số đo tốc độ

Máy Windows 8 nhân, cùng lúc có các phiên khác chạy nên số dao động mạnh; ghi **lần nhanh nhất** (trung vị trong ngoặc). Ảnh dựng theo kiểu iPhone (lưới ô 512 × 512, có GPS, xoay 6) bằng bộ mã hóa đi kèm pillow-heif. Script đo nằm ngoài repo.

| Ảnh | Việc | 4 luồng (cũ) | 1 luồng (mới) |
|---|---|---|---|
| 12 MP (4032 × 3024, 48 ô) | Mở + giải mã (`open_image`) | 0,54 s (0,60) | 1,41 s (2,1–2,5) |
| 12 MP | Ảnh gửi web (`make_web_image`: giải mã, thu 1600 px, WebP) | 1,63 s (1,93) | 1,88 s (2,3–2,7) |
| 12 MP | Ảnh xem trước (`make_preview`) | 0,64 s (1,03) | 1,49 s (1,6–2,3) |
| 48 MP (8064 × 6048, 192 ô) | Mở + giải mã | 2,13 s (2,1–4,3) | 3,93 s (6,9–7,3) |
| 48 MP | Ảnh gửi web | 3,20 s (4,0–5,4) | 3,73 s (14,7)* |

\* Một lượt đo 48 MP một luồng ra 36 s (trung vị 43 s), lượt sau 3,7 s: máy đang bận việc khác, không phải do số luồng (phần thu nhỏ và nén WebP không dùng libheif).

Kết luận: chậm thêm khoảng 1 giây (12 MP) đến 2 giây (48 MP) mỗi ảnh HEIC; ảnh xem trước có cache nên chỉ chậm lần đầu. Chấp nhận được với cách dùng hiện tại (chọn vài ảnh cho một bài).

## Phiên bản và cách kiểm khi có bản mới

- Hiện tại (kiểm 30/10 bằng `uv run python` và `uv pip list --outdated`): **pillow-heif 1.8.1** (bản mới nhất trên PyPI), mang sẵn **libheif 1.23.6** và bộ giải mã **libde265 1.1.3**; Pillow 13.0.0. `pyproject.toml`: `pillow-heif>=1.8.1`.
- Khi nghi có bản mới:
  1. `uv pip list --outdated`: dòng `pillow-heif` có cột «Latest» mới hơn 1.8.1.
  2. Đọc ghi chú phát hành pillow-heif (GitHub `bigcat88/pillow_heif`, mục Releases): tìm dòng nâng libheif lên **1.23.7** trở lên.
  3. Trên nhánh riêng: `uv lock --upgrade-package pillow-heif`, `uv sync`, rồi `uv run python -c "import pillow_heif; print(pillow_heif.__version__, pillow_heif.libheif_info())"`: `libheif` phải từ `1.23.7`.
  4. Chạy test ảnh (danh sách ở mục Kiểm thử), nhất là `tests/test_la_chan_t093.py` và `tests/test_t107_heif_mot_luong.py`.
  5. Chủ dự án duyệt nâng thư viện; Lá Chắn kiểm rút gọn (D1). Lúc đó Lá Chắn quyết giữ một luồng (an toàn hơn, chậm hơn ~1 s) hay trả lại mặc định (`HEIF_DECODE_THREADS`). Kiểm lại cả hai mục OSS-Fuzz OSV-2020-2308, OSV-2023-1129 (sổ rủi ro đề xuất N2 của T-093).

## Kiểm thử

- `tests/test_t107_heif_mot_luong.py` + `tests/test_la_chan_t093.py`: 30 qua, 2 xfail (LC-T093-1, LC-T093-2: phiếu khác, giữ nguyên).
- Mọi file test chạm tới xử lý ảnh, HEIF: 38 file. Đó là mọi file có `seo_app.images.process`, `pillow_heif`, `make_web_image`, `make_preview`, `make_ai_image`, `open_image`, `test_images_process`, cộng `test_pillow_version_t058.py`, `test_soi_loi_t080.py`, `test_soi_loi_t080_linux.py`, `test_images_folders.py`, `test_app_pages.py`. Trong đó có test T-047 (`test_pillow_heif_setup.py`, `test_soi_loi_t047.py`), T-058, T-080 và `test_app_images.py`. Kết quả: **5245 qua, 38 bỏ qua, 6 xfail, 0 hỏng** (32 phút).
  - 6 xfail có từ trước, thuộc phiếu khác: LC-T093-1, LC-T093-2, SL-T067-1 (4 ca).
  - 38 bỏ qua: 24 ca là của hai file chỉ chạy trên Linux/Mac (`test_soi_loi_t079_linux.py`, `test_soi_loi_t080_linux.py`). 14 ca còn lại bỏ qua theo điều kiện có sẵn trong test; không ca nào của T-107.
  - Một lượt chạy trước đó bị cắt vì quá giờ chờ, có 1 ca hỏng. Theo vị trí, nhiều khả năng là `test_soi_loi_t058.py::test_anh_pillow_o_cac_cho_khac_cua_streamlit[write]`: trang Streamlit thử có giới hạn 30 giây, trong khi máy đang bận. Ca này không dùng HEIC. Chạy lại riêng và trong lượt đầy đủ ở trên đều qua.
- `uv run ruff check .`: All checks passed. `ruff format --check` sạch với file của phiếu này; riêng `process.py` dòng `expected = (…)` (khoảng dòng 804) bị ruff 0.16.10 đòi gộp dòng, **có từ trước** (bản `HEAD` cũng vậy), không đụng tới vì ngoài phạm vi.
- Không có ảnh HEIC thật nào trên máy (đã tìm ổ D, Pictures, Downloads, Desktop), nên ảnh «kiểu iPhone» là ảnh dựng. Thử ảnh iPhone thật để ở lượt thử thật kế tiếp (đã ghi ở T-093: T-049 ĐK 7 phần ảnh HEIC thật).

## Còn lại (cần nâng thư viện mới hết)

Trong 16 khuyến cáo libheif 1.23.7 vá, phần liên quan tới app (đọc ảnh tĩnh qua pillow-heif):

| Khuyến cáo | Sau T-107 |
|---|---|
| GHSA-35mc-3887-rr37 (dùng vùng nhớ đã giải phóng, giải mã song song) | **Không còn đường tới** (một luồng) |
| GHSA-rcqc-842v-m26h (kẹt khi giải mã song song bỏ qua ô hỏng) | **Không còn đường tới** (một luồng) |
| GHSA-48p4-gj45-w9v6 (lưới ô giải mã lặp ảnh chồng lớn, treo CPU) | **Giảm**: chặn dạng ô 1 × 1 và thừa ô; file dựng với ô ≥ 64 vẫn có thể làm chậm |
| GHSA-2g6j-vhr6-6wrj (nhiều ảnh mã hóa ẩn), GHSA-7qm8-hj35-269r (thuộc tính xoay, cắt lặp), GHSA-hhg3-fxg7-3gxw (nhiều `colr`, ngay lúc mở), GHSA-74mj-m37q-h3q9 (`moov`/`stsc`, ngay lúc mở) | **Còn**: treo CPU (vài chục giây tới vài phút) khi app đọc file HEIC dựng cố ý. Không chạy được mã, không lộ dữ liệu; tắt app mở lại là hết. Hết hẳn khi nâng lên libheif từ 1.23.7 |
| Các khuyến cáo còn lại (AV1, OpenH264, bộ mã hóa, công cụ dòng lệnh, gdk-pixbuf) | Không dùng tới: app chỉ giải mã HEVC bằng libde265, không mã hóa, không dùng công cụ dòng lệnh |

## Lượt 2 · SL-T107-2, SL-T107-1 (Soi Lỗi `f68a206`)

Ngày nộp lượt 2: 2026-10-30 12:50 (+07:00, theo lệnh `date`). Chỉ Huy B giao sau khi Soi Lỗi kết luận ĐẠT CÓ ĐIỀU KIỆN (`docs/team/reports/T-107-soi-loi.md`).

### Tóm tắt (cho chủ dự án)

- Soi Lỗi tìm được một file HEIC dựng cố ý, chỉ khoảng 20 kB, khai cỡ ảnh nhỏ nhưng thực ra là một lưới rất lớn. File này làm app bận 11–14 giây và tốn thêm 250 MB bộ nhớ mỗi lần mở. Nay app so cỡ lưới với cỡ ảnh khai trong file và từ chối ngay, **trước khi giải mã** (tức thì).
- Một loại lỗi của thư viện HEIC trước đây hiện câu chung «Không xử lý được ảnh này». Nay hiện đúng câu «Ảnh bị hỏng…».
- Ảnh điện thoại thật vẫn đọc bình thường; vẫn giải mã một luồng.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/process.py` | `_check_heif_grid` thêm 2 phép kiểm, vẫn trước `load`. (1) Đầu ra của lưới (`tiling` `image_width × image_height`) phải khớp cỡ ảnh lúc mở (`image.size`, từ `ispe`), nhận cả hai chiều do xoay. Chỉ được lớn hơn **dưới một ô mỗi chiều**: đó là phần thừa của ô bị `clap` cắt. (2) Đầu ra của lưới, và tổng điểm ảnh của mọi ô phải giải mã (`số ô × cỡ ô`), không vượt `MAX_IMAGE_PIXELS` (80 triệu). `_open` bắt thêm `RuntimeError`, `MemoryError` quanh `open`/`load`, ra câu cố định `_MSG_BROKEN`. Docstring module cập nhật |
| `tests/test_soi_loi_t107.py` (file của Soi Lỗi) | Gỡ 2 dấu `xfail(strict=True)` (SL-T107-1 ×4 ca, SL-T107-2 ×3 ca, cả 7 XPASS). Chỉ xóa dấu, thân test không đổi (R5) |
| `tests/test_t107_heif_mot_luong.py` (file của Thợ Máy) | Ảnh giả của phép kiểm lưới nay có `size` (`_grid`); thêm ca nhận (64 MP, ảnh đã xoay mà lưới chưa, `clap` cắt phần thừa) và 8 ca từ chối mới (`test_grid_not_matching_image_size_rejected`) |

### Quyết định khi sửa

- **So cỡ có dung sai, không so bằng tuyệt đối.** Soi Lỗi gợi ý từ chối khi cỡ lưới khác `image.size`. Nhưng `clap` (cắt khung) có thật trong file của bộ mã hóa: chính pillow-heif coi `clap` neo góc trên trái, cắt dưới 64 điểm ảnh, là «bỏ phần thừa của bộ mã hóa». Nếu so bằng tuyệt đối thì ảnh thật có `clap` có thể bị từ chối oan. Dung sai dưới một ô mỗi chiều đủ cho phần thừa đó. Kẻ dựng file chỉ còn lợi thêm được chưa tới một hàng, một cột ô, và vẫn bị trần 80 MP ở phép (2).
- **GN-4 (ô chữ nhật dựng cố ý được thừa ô):** giữ phép «thừa ô» nhận cả hai chiều, vì không biết chắc libheif đã xoay cỡ ô hay chưa. Đổi lại, tổng điểm ảnh phải giải mã nay bị chặn ở 80 MP (phép 2). Nên dù thừa ô, công giải mã không vượt mức của một ảnh 80 MP hợp lệ.
- **Đánh đổi:** ảnh HEIC sát 80 MP mà phần thừa của ô đẩy tổng điểm ảnh phải giải mã quá 80 triệu sẽ bị từ chối (ví dụ 10328 × 7744, ô 512: phải giải mã 88 triệu). Không điện thoại nào chụp HEIC cỡ này: iPhone 48 MP giải mã 50,3 triệu, máy 64 MP giải mã 69,7 triệu, máy 108/200 MP đã vượt giới hạn 80 MP từ trước. Người dùng gặp câu «cấu trúc lạ… xuất lại ảnh sang JPEG».
- **Đính chính lượt 1:** câu «giới hạn 80 triệu điểm ảnh vẫn áp cho HEIC» chỉ đúng với cỡ khai trong `ispe`, không đúng với lưới libheif thật sự dựng (Soi Lỗi chỉ ra). Phép (1), (2) ở lượt này bịt chỗ đó.

### Kiểm thử lượt 2

- 12 file test chọn lọc, đúng bộ Soi Lỗi đã chạy: `test_soi_loi_t107`, `test_t107_heif_mot_luong`, `test_la_chan_t093`, `test_pillow_heif_setup`, `test_images_process`, `test_soi_loi_t047`, `test_soi_loi_t049`, `test_pillow_version_t058`, `test_soi_loi_t058`, `test_soi_loi_t067`, `test_soi_loi_t080`, `test_app_images`. Kết quả: **628 qua, 6 xfail, 0 hỏng, không XPASS** (7 phút 48 giây).
  - 7 ca SL-T107 nay qua thật.
  - 6 xfail có từ trước: LC-T093-1, LC-T093-2 và 4 ca cũ của phiếu khác.
  - **T-047, T-058, T-080 không lùi.**
- Chạy lại script của Soi Lỗi (thư mục ghi chú chung `T-107-soi-loi-scripts/`):
  - `sl107_gridrepeat.py 8 6 24 24 31 31` (file dựng 18–20 kB, mọi ô trỏ cùng một mục, Pillow báo 4032 × 3024):
    - lưới 24 × 24 (151 MP) và 31 × 31 (252 MP): «cấu trúc lạ» sau **0,2 giây**, bộ nhớ không tăng. Trước khi sửa: 9–14 giây, thêm 108–250 MB;
    - lưới 8 × 6 (đầu ra 4096 × 3072, lớn hơn cỡ khai dưới một ô) lọt qua phép kiểm theo dung sai `clap`; libheif tự từ chối sau 0,3 giây, ra «Ảnh bị hỏng».
  - `sl107_correct.py`: **258 ca (156 ảnh lưới), 0 lỗi**. Gồm 7 cỡ ảnh, ô 64 → 1024, 8 chiều xoay. Không ảnh nào bị từ chối oan; GPS, cỡ sau xoay đúng; điểm ảnh một luồng giống từng byte bốn luồng.
- `uv run ruff check .`: All checks passed. `ruff format --check` sạch với 2 file test; `process.py` chỉ còn dòng `expected = (…)` có từ trước (đã ghi ở lượt 1).
- Không có ảnh HEIC chụp thật trên máy (như lượt 1); 258 ảnh trên là ảnh dựng bằng bộ mã hóa pillow-heif.

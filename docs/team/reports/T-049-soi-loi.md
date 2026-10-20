# Báo cáo T-049 · Soi Lỗi · Xử lý ảnh: xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch, tên file (G3-3)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-049](../tickets/T-049-xu-ly-anh-webp-giu-gps.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- **Kết luận: ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn được.** Không có lỗi Nghiêm trọng, Cao hay Trung bình. Tìm được 3 lỗi **Thấp** (SL-T049-1, 2, 3), không lỗi nào làm mất GPS của ảnh bình thường hay lọt metadata sang AI; Thợ Máy sửa trong phiếu này hoặc phiếu dọn đều được.
- **Vị trí GPS giữ đúng từng con số** sau khi nén WebP với ảnh JPEG, PNG, WebP và HEIC (iPhone): 4 cặp bán cầu (Bắc/Nam × Đông/Tây), độ cao trên và dưới mặt biển, cả hai cách xếp byte của EXIF (iPhone thường ghi kiểu "MM", nhiều máy Android kiểu "II"), cả 3 cách máy ảnh viết tọa độ. Thông tin máy theo đúng lựa chọn 2A: giữ ngày chụp, hãng, đời máy; bỏ số seri, tên chủ máy, khối dữ liệu riêng của hãng, ảnh nhỏ nhúng.
- **Bản gửi AI sạch hoàn toàn** từ 11 loại ảnh nguồn (kể cả ảnh có hồ sơ màu chở chữ "địa chỉ khách"), qua được bộ kiểm của T-050 và tới đúng máy chủ (giả) của cả Claude, ChatGPT, Gemini mà không kèm GPS, tên máy hay chữ ẩn.
- Ảnh hỏng, ảnh "bom" (file vài KB khai 81 triệu điểm ảnh), file giả đuôi, HEIC tải dở: đều báo câu tiếng Việt cố định, không treo, không lộ tên thư mục khách. **Chưa thử ảnh thật của chủ dự án** (Chỉ Huy sẽ làm riêng): mọi thử nghiệm dùng ảnh giả tạo trong test.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t049.py` | Mới: 28 hàm test, 158 trường hợp (155 qua, 3 `xfail(strict=True)` cho SL-T049-1, 2, 3) |
| `tests/test_pillow_heif_setup.py` | Điều kiện 6 Lá Chắn T-047: bỏ `pytest.skip`, thêm `_go_heif_khoi_bang()` + fixture `heif_chua_dang_ky` (gỡ HEIF khỏi 6 bảng định dạng, trả nguyên sau test) và test kiểm chính fixture đó |
| `docs/team/reports/T-049-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng (`git diff --stat 8e76b54..HEAD`: chỉ 2 file test và báo cáo).

## Bằng chứng

```
$ uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py \
    tests/test_pillow_heif_setup.py tests/test_ai_images.py -q -rsX   (test liên quan, Windows, tại 8a178e7)
516 passed, 3 xfailed in 45.80s
(3 xfail đúng là SL-T049-1, 2, 3; 0 skip: test "chưa đăng ký HEIF" của T-047 chạy thật)

$ uv run ruff check .
All checks passed!

$ uv run pytest -q                                (toàn bộ, Windows, tại 8ffdbb8, 13:23:54–13:40:13)
8278 passed, 17 skipped, 53 xfailed, 1 warning in 971.62s (0:16:11)
(0 hỏng, 0 lỗi, không test nào quá giờ; 53 xfail gồm 3 của phiếu này; cảnh báo Pydantic ở
 tests/test_soi_loi_t028.py có từ trước. 8a178e7 sau đó chỉ thêm báo cáo, không đổi test.)
```

Theo quy tắc mới của chủ dự án (2026-10-20, Chỉ Huy B chuyển): agent chỉ cần chạy test liên quan tới phiếu; **toàn bộ test do Chỉ Huy chạy trên Windows khi gộp vào `main`**. Lượt toàn bộ ở trên đã chạy xong trước khi nhận quy tắc nên vẫn ghi lại.

**Thử ngoài test** (script trong thư mục tạm, ảnh giả, không mạng; kết quả rút gọn đã đưa vào test):

| Thử | Kết quả |
|---|---|
| Ma trận GPS: 4 định dạng × 4 bán cầu × 2 độ cao × 2 endian × 3 cách viết tọa độ, 16 thẻ GPS mỗi ảnh | 192/192 đúng từng giá trị đọc lại độc lập bằng Pillow, dấu tọa độ đúng |
| Đột biến ngẫu nhiên cả file (đổi byte, cắt, chèn, xóa) JPEG/PNG/WebP/HEIC, 400 file mỗi loại × 3 hàm | 4.800 lượt: 0 lỗi thô lọt ra, mọi câu lỗi là câu cố định của module (kể cả câu "quá nhiều điểm ảnh"); mọi bản AI tạo được đều qua `prepare_images`; lâu nhất 0,26 s |
| Xoay 8 hướng × JPEG/PNG/WebP/HEIC × (ảnh web, bản AI, xem trước) | 96/96 đúng chiều |
| Ảnh lạ: CMYK (Adobe), PNG 16 bit RGB/xám+trong suốt, WebP động, APNG, MPO, HEIC trong suốt/xám, ảnh dẹt 1×10000 và 2×16383, GIF giả đuôi | Xử lý đúng (trừ PNG xám 16 bit có màu trong suốt, xem Rủi ro 3) hoặc báo "không phải ảnh JPEG, PNG, WebP hoặc HEIC" |
| Thời gian (máy Windows này) | JPEG 48 MP (8 MB) → WebP 1600 px: 2,45 s (199 KB); bản AI 0,26 s. HEIC 12 MP → WebP 2,43 s (211 KB); bản AI 1,1 s |

## Đối chiếu tiêu chí xong

**7 yêu cầu của phiếu**

- [x] **YC1 mở ảnh an toàn.** Kiểm dung lượng trước khi mở, tự so `rộng × cao` trước `load()`, đổi `DecompressionBombWarning` thành lỗi, bắt `(OSError, ValueError, SyntaxError, EOFError, struct.error)` + `DecompressionBombError` quanh cả `open` lẫn `load` (`process.py:184-219`); WebP đọc cỡ khung trước khi mở (`:160-181`); `formats` đúng 4 định dạng, không `"MPO"`. Test thêm: `test_bien_gioi_han_diem_anh_dung_bang_qua_mot_bi_chan` (đúng bằng giới hạn qua, hơn 1 điểm ảnh bị chặn, 4 định dạng), `test_bom_png_that_khong_doi_gioi_han_bi_chan_truoc_khi_giai_ma` (PNG 9.000 × 9.000 dưới 10 KB, `load()` không được gọi), `test_bom_jpeg_khai_kich_thuoc_lon_bi_chan`, `test_gia_duoi_qua_thu_vien_anh_nhan_theo_noi_dung_cau_loi_khong_lo_duong_dan` (qua `ImageLibrary`: PNG đuôi `.jpg` dùng được; GIF, BMP, chữ, HTML giả đuôi bị từ chối; câu lỗi không có tên thư mục khách, không có `/` hay `\`), `test_heic_cut_o_nhieu_diem_chi_bao_cau_co_dinh` (7 điểm cắt × 3 hàm), `test_dot_bien_ngau_nhien_ca_file_khong_lot_loi_tho` (4 định dạng).
  - Bom HEIC: dùng test của Thợ Máy (hạ giới hạn, HEIC cụt chỉ hỏng lúc `load` mà vẫn ra câu "quá nhiều điểm ảnh", tức chặn trước khi giải mã). Không dựng được HEIC khai kích thước lớn rẻ: sửa hộp `ispe` thành 10.000 × 9.000 thì pillow-heif vẫn báo cỡ thật 64 × 48, ảnh bị báo hỏng (an toàn).
- [x] **YC2 xoay → Orientation = 1 → cạnh dài 1600 → WebP kèm EXIF lọc 2A.** `test_xoay_dung_ca_8_huong_voi_png_webp_heic` (24 trường hợp × 3 loại ảnh ra, bổ sung JPEG của Thợ Máy), `test_2a_giu_bo_dung_the_voi_moi_dinh_dang` (JPEG/PNG/WebP/HEIC: đếm đủ thẻ giữ, thẻ bỏ gồm số seri thân máy và ống kính, `CameraOwnerName`, MakerNote, IFD1, `Artist`, `Software`, `ImageDescription` có địa chỉ, `Copyright`, `HostComputer`, `UserComment`, `ImageUniqueID`, `LensModel`, 2 thẻ GPS chữ tự do).
- [x] **YC3 / F2 GPS đúng giá trị sau nén.** `test_f2_gps_dung_tung_gia_tri_moi_dinh_dang_ban_cau_do_cao` (32 trường hợp: 17 thẻ GPS đọc lại độc lập phải **bằng** ảnh gốc; tọa độ báo cho người dùng đúng dấu), `test_f2_gps_dung_gia_tri_moi_cach_viet_exif` (24 trường hợp: EXIF MM/II, độ-phút-giây, phút thập phân, độ thập phân), `test_mpo_giu_gps_khung_dau_ban_ai_sach`. Lớp kiểm sau nén so giá trị (`process.py:695-721`). Một ngoại lệ hiếm: SL-T049-1.
- [x] **YC4 / A3 bản AI dựng lại từ điểm ảnh, không metadata.** `Image.frombytes` (`:560`), lưu JPEG chỉ với `quality` (`:665`), kiểm danh sách khối (`jpeg_layout`). Test thêm: `test_ban_ai_moi_loai_nguon_qua_prepare_images` (11 loại nguồn: JPEG/PNG/WebP/HEIC có EXIF + GPS + XMP + COM + ICC chở chữ trong `desc`, CMYK, PNG 16 bit, MPO, WebP động, HEIC trong suốt, PNG bảng màu, ảnh chụp màn hình; bản AI và ảnh xem trước không có `Exif`, `ICC_PROFILE`, `acsp`, `GPS`, XMP, chữ trong hồ sơ màu), `test_ban_ai_toi_ca_3_hang_dung_byte_khong_metadata` (12 trường hợp: 4 nguồn × Claude/ChatGPT/Gemini, thư viện thật + mạng giả: byte tới máy chủ đúng bằng byte đã kiểm, phần còn lại của yêu cầu không có tọa độ, tên khách, số seri, hãng/đời máy), đối chứng `test_nguon_con_metadata_thi_bo_kiem_t050_tu_choi` và `test_anh_dang_web_co_gps_khong_bao_gio_qua_bo_kiem_gui_ai` (bộ kiểm T-050 chạy thật, không "cho qua hết").
- [x] **YC5 ảnh xem trước bỏ EXIF, cache trong `.gitignore`.** `.gitignore:22` có `data/`; `_cache_dir_is_ignored` (`process.py:809-827`) và test của Thợ Máy (có `git check-ignore`). Test thêm: ảnh xem trước của 11 loại nguồn đều sạch (trong `test_ban_ai_moi_loai_nguon_qua_prepare_images`). Một khe nhỏ khi Pillow < 13: SL-T049-2.
- [x] **YC6 tên file.** `test_ten_file_tu_ten_nfd_cua_mac_giong_nfc` (tên thư mục trên Mac ở dạng NFD ra cùng tên file), `test_ma_cong_trinh_sai_mau_khong_vao_ten_file` (6 kiểu: `CT 012`, tên khách, `../`, quá 6 số…), `test_ten_file_chi_gom_chu_thuong_so_gach_noi` (HTML, đường dẫn Windows, `../../etc/passwd`, ký tự vô hình, chữ rộng), `test_nhieu_anh_cung_the_khong_trung_ten` (60 ảnh cùng thẻ dài: không trùng, ≤ 60 ký tự). Hàm không nhận tên thư mục (`naming.py:57-65`).
- [x] **YC7 ảnh không EXIF.** `test_anh_khong_exif_xu_ly_binh_thuong_moi_dinh_dang` (JPEG/PNG/WebP/HEIC: không EXIF ra, `gps is None`, không câu báo).

**Lưu ý Soi Lỗi T-047, điều kiện Lá Chắn T-047, T-048, T-050, T-058**

- [x] HEIC cụt chỉ nổ ở `load()` (`ValueError`): bắt được ở mọi điểm cắt (test trên).
- [x] Đăng ký HEIF một chỗ (`_register_heif`, `process.py:122-134`) và **điều kiện 6 Lá Chắn T-047**: `test_chua_dang_ky_thi_pillow_khong_mo_duoc_heic` nay dùng fixture `heif_chua_dang_ky`, không còn `skip` dù HEIF đã đăng ký sẵn; `test_go_heif_khi_da_dang_ky_san_roi_tra_lai` kiểm fixture; `test_go_heif_khoi_bang_roi_module_anh_tu_dang_ky_lai` (gỡ HEIF xong, module ảnh tự đăng ký lại và tắt ảnh phụ).
- [x] Từ chối Pillow < 13: test của Thợ Máy (4 hàm) + `test_pillow_duoi_13_khong_cache_thi_tu_choi` (không ghi cache). Khe khi ảnh đã có trong cache: SL-T049-2.
- [x] Không Arrow, không `PILLOW_ALIGNMENT`, không `ImageCms`: ngoài test dò mã nguồn của Thợ Máy, `test_khong_imagecms_khong_arrow_khong_alignment_khi_chay_that` bẫy các hàm `ImageCms` và Arrow lúc chạy với ảnh có hồ sơ màu (4 định dạng), biến môi trường không đổi.
- [x] Chỉ khung đầu MPO (test của Thợ Máy bẫy `seek`) và GPS khung đầu giữ đúng (`test_mpo_giu_gps_khung_dau_ban_ai_sach`).
- [x] Ảnh 16 bit (SL-T058-1): `test_png_16_bit_mau_va_trong_suot_dung_mau` (PNG màu 16 bit, xám + trong suốt 16 bit viết tay), CMYK: `test_jpeg_cmyk_adobe_dao_mau_ra_dung_mau`.
- [x] Lá Chắn T-050 điều kiện 2: bản AI không hồ sơ màu, qua `prepare_images` (nay có trên nhánh) với 4 định dạng gốc, tới cả 3 hãng; bản web giữ hồ sơ màu và GPS (test của Thợ Máy).

## Lỗi tìm được

| Mã | Mức | Tóm tắt | Test |
|---|---|---|---|
| SL-T049-1 | Thấp | Chữ chỉ hướng GPS sai chuẩn (chữ thường) bị bỏ lặng lẽ, tọa độ đổi bán cầu | `test_gps_ref_sai_khuon_khong_lang_le_doi_ban_cau` |
| SL-T049-2 | Thấp | `PreviewCache.get` trả ảnh trong cache mà không kiểm Pillow ≥ 13 | `test_pillow_duoi_13_co_cache_cung_tu_choi` |
| SL-T049-3 | Thấp | Hai luồng mở ảnh cùng lúc để lại bộ lọc cảnh báo cho cả chương trình | `test_hai_luong_mo_anh_cung_luc_khong_de_lai_bo_loc_canh_bao` |

### SL-T049-1 (Thấp): GPS ref sai khuôn bị bỏ lặng lẽ, tọa độ đổi bán cầu

- **Tái hiện:** ảnh JPEG có `GPSLatitudeRef = "s"`, `GPSLongitudeRef = "w"` (chữ thường, sai chuẩn EXIF) kèm vĩ độ, kinh độ hợp lệ → `make_web_image`.
- **Mong đợi:** giữ đúng bán cầu (chuẩn hóa thành `S`/`W`), hoặc bỏ cả GPS và báo `_NOTICE_GPS_BROKEN` như khi tọa độ hỏng.
- **Thực tế:** `_valid` chỉ nhận chữ hoa (`process.py:366`), `_pick` bỏ 2 thẻ ref (`:385-386`); `_coordinates` coi thiếu ref là Bắc/Đông (`:412-431`); lớp kiểm sau nén so với **phần đã lọc** nên vẫn qua (`:718`). Ảnh ra có vĩ độ, kinh độ mà không có ref: mọi trình đọc hiểu là Bắc/Đông, `web.gps` báo `(10.776, 106.687)` thay vì `(-10.776, -106.687)`, `notice` rỗng.
- **Ảnh hưởng:** chỉ với ảnh do phần mềm ghi sai chuẩn; ảnh ở Việt Nam (Bắc/Đông) không đổi nghĩa. Cùng loại (suy luận, chưa dựng được file thử vì Pillow luôn ghi thẻ này đúng kiểu): `GPSAltitudeRef` sai kiểu bị bỏ thì độ cao dưới mặt biển thành trên mặt biển.
- **Gợi ý:** nếu ảnh gốc có thẻ ref (1, 3, 5) mà giá trị bị loại thì coi như GPS hỏng (bỏ cả khối, báo người dùng), hoặc chuẩn hóa chữ hoa trước khi kiểm.

### SL-T049-2 (Thấp): Pillow < 13 nhưng ảnh xem trước có sẵn trong cache vẫn được trả

- **Tái hiện:** `PreviewCache.get(library, ref)` một lần (tạo cache), đặt `PIL.__version__ = "12.3.0"`, gọi lại.
- **Mong đợi:** `ImageProcessError(_MSG_OLD_PILLOW)` như mọi đường khác của module (LC-T058-3).
- **Thực tế:** trả byte JPEG từ cache (`process.py:899-902` trả trước khi tới `_open`, nơi duy nhất gọi `_require_pillow_13`). Byte này sẽ được `st.image` giải mã bằng Pillow 12.
- **Ảnh hưởng:** nhỏ: byte trong cache do app tạo và được `jpeg_layout` kiểm khuôn trước khi trả; chỉ là khe so với điều kiện "module từ chối khi Pillow < 13".
- **Gợi ý:** gọi `_require_pillow_13()` ở đầu `PreviewCache.get` (hoặc `__init__`).

### SL-T049-3 (Thấp): `warnings.catch_warnings` không an toàn nhiều luồng

- **Tái hiện** (test điều khiển thứ tự 2 luồng bằng `threading.Event`, không phụ thuộc may rủi): luồng A vào khối `catch_warnings` ở `process.py:195`, luồng B vào khối, A ra khối, B ra khối.
- **Mong đợi:** `warnings.filters` sau khi cả hai xong giống hệt trước.
- **Thực tế:** còn thừa `('error', None, DecompressionBombWarning, None, 0)` cho **cả chương trình**: mọi chỗ khác dùng Pillow (ví dụ `st.image`) gặp ảnh 89–179 triệu điểm ảnh sẽ nổ lỗi thay vì cảnh báo. Ngoài ra (suy luận từ cách `catch_warnings` hoạt động): trong lúc B còn trong khối, bộ lọc của B bị A gỡ mất.
- **Ảnh hưởng:** Thợ Máy đã nêu là suy luận (Rủi ro số 3); nay tái hiện được. Không mở lỗ bảo mật: phép so `rộng × cao` với 80 triệu (`:199-201`) và đọc cỡ khung WebP trước (`:190-192`) vẫn chặn trước ngưỡng cảnh báo 89,5 triệu của Pillow. Streamlit chạy mỗi phiên trình duyệt một luồng, nên 2 tab mở ảnh đúng cùng lúc là có thể gặp.
- **Gợi ý:** bọc khối mở ảnh bằng một `threading.Lock` của module (vẫn giữ điều kiện 2 Lá Chắn T-047 "đổi cảnh báo thành lỗi"), hoặc Lá Chắn xét bỏ bộ lọc vì đã có phép so riêng.

## Rủi ro và điểm cần chú ý

1. **Chưa thử ảnh thật của chủ dự án** (iPhone HEIC, ảnh Android, MakerNote thật, ảnh MPO của iPhone, dung lượng WebP thật): Chỉ Huy làm riêng trên máy, không commit ảnh.
2. JPEG có **hai khối EXIF** (khối đầu không GPS, khối sau có GPS): app chỉ đọc khối đầu nên ảnh ra không GPS và không báo. Đây là cách Pillow đọc (đã thử); trình đọc khác (exiftool, WordPress) chưa thử. Ghi lại để Chỉ Huy biết khi thử ảnh đã qua phần mềm sửa ảnh. Tương tự PNG có cả `eXIf` lẫn "Raw profile type exif": `eXIf` thắng (PNG chỉ có "Raw profile type exif" thì GPS vẫn giữ, đã thử).
3. PNG **xám 16 bit có màu trong suốt** (`tRNS`): điểm trong suốt thành màu đen ở cả ảnh web (mất trong suốt) lẫn bản AI (không lót trắng), đã thử. Rất hiếm (ảnh công trình không có dạng này), không lập lỗi.
4. Thẻ GPS chữ tự do còn giữ: `GPSSatellites`, `GPSMapDatum` (≤ 64 ký tự ASCII); Thợ Máy đã bỏ `GPSProcessingMethod`, `GPSAreaInformation`. Máy thật ghi kiểu `WGS-84`, `05`; Lá Chắn xét có cần bỏ luôn không (2A giữ GPS).
5. `_cache_dir_is_ignored` coi mọi thư mục **ngoài** thư mục dự án là an toàn để ghi cache. Hiện thư mục cache cố định trong `data/`; nếu phiếu giao diện/cấu hình (T-056, T-062) cho đặt thư mục cache thì phải chặn đặt vào thư mục ảnh (Drive), vì 3A: app không ghi gì vào Drive.
6. Ghi cho người viết test sau: **Windows Defender chặn mở file** có chuỗi PHP kiểu webshell (`<?php system(...)`), `os.open` báo `Errno 22`; test giả đuôi trên ổ dùng chữ thường.

## Đề xuất

- **Thợ Máy (phiếu này hoặc phiếu dọn):** sửa SL-T049-1, 2, 3 theo gợi ý; sửa xong test `xfail(strict=True)` tự báo XPASS, gỡ dấu `xfail` là xong.
- **Lá Chắn:** soát thêm điểm Rủi ro 4 (thẻ GPS chữ tự do) và 5 (thư mục cache ngoài dự án); SL-T049-3 có liên quan điều kiện 2 của Lá Chắn T-047 (cảnh báo thành lỗi).
- **Chỉ Huy:** thử 3–5 ảnh thật (HEIC iPhone, ảnh Android, ảnh MPO) bằng `make_web_image` ngay trên máy theo cách Thợ Máy đề xuất; xem GPS trong thuộc tính file WebP và dung lượng (mục tiêu 150–400 KB).
- **T-056 (giao diện):** dùng `heif_chua_dang_ky` của `tests/test_pillow_heif_setup.py` khi cần test "chưa đăng ký HEIF"; AppTest mở ảnh sẽ để HEIF đăng ký sẵn.

## Câu hỏi cho chủ dự án

Không có.

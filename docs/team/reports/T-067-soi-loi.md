# Báo cáo T-067 · Soi Lỗi · Dọn lỗi Thấp xử lý ảnh (sau T-049), kiểm rút gọn

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-067](../tickets/T-067-don-loi-thap-xu-ly-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình; 1 lỗi Thấp mới (SL-T067-1). Điều kiện ở mục cuối |

## Tóm tắt (cho chủ dự án)

- **3 lỗi Thấp của T-049 đã sửa thật.** 3 test bắt lỗi cũ của Soi Lỗi nay qua mà thân test giữ nguyên từng chữ.
- **Ảnh có GPS ghi sai chuẩn** (chữ chỉ hướng viết thường, để trống, có dấu cách, ghi sai kiểu dữ liệu…, 26 kiểu, có thử với cả 4 loại ảnh JPEG, PNG, WebP, HEIC): app bỏ vị trí và báo "Thông tin GPS của ảnh gốc bị hỏng…", không còn đăng vị trí sai bán cầu. **Ảnh ghi đúng chuẩn vẫn giữ GPS đúng từng con số**, kể cả ảnh có đủ 10 loại thẻ chỉ hướng, ở cả bán cầu Bắc/Đông lẫn Nam/Tây.
- **Ảnh xem trước:** thư viện ảnh cũ (dưới bản 13) bị từ chối ở mọi trường hợp, kể cả ảnh đã có sẵn trong bộ nhớ đệm, và app không đụng tới thư mục ảnh.
- **8 luồng mở ảnh cùng lúc** (như nhiều tab trình duyệt): ảnh nào giữ đúng vị trí của ảnh đó, "ảnh bom" bị chặn ở mọi luồng, có lỗi giữa chừng cũng không treo. Thử thay khóa của Thợ Máy bằng khóa giả thì test hỏng ngay, tức là test bắt được lỗi cũ.
- **1 lỗi Thấp mới (SL-T067-1):** với ảnh **không có vị trí** (máy tắt định vị) mà có một thẻ GPS phụ ghi sai chuẩn, app vẫn báo "GPS bị hỏng". Trước T-067 app không báo. Lỗi này không làm lộ vị trí, cũng không làm sai vị trí; chỉ là câu báo dễ gây hiểu lầm khi màn hình chọn ảnh (T-056) hiện câu báo. Sửa trước khi gộp T-056.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t067.py` | Mới: 15 hàm test, 109 trường hợp (105 qua, 4 `xfail(strict=True)` cho SL-T067-1) |
| `docs/team/reports/T-067-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của người khác (`git diff --stat da9d6c8..HEAD`: chỉ 2 file trên). Commit: `5ec1eca` (test thử lách), `ba922e6` (SL-T067-1), và commit báo cáo này; đã đẩy lên `team/T-067`.

## Bằng chứng

```
$ git diff origin/main...HEAD -- tests/test_soi_loi_t049.py
3 khối @pytest.mark.xfail(strict=True, reason="SL-T049-n …") thay bằng 1–2 dòng chú thích "sửa ở T-067";
không dòng nào khác đổi. Script so thân 3 hàm test giữa origin/main và HEAD: GIONG × 3;
chữ "xfail(" còn 1 lần trong file (ở docstring), trước là 4.

$ uv run pytest "tests/test_soi_loi_t049.py::test_gps_ref_sai_khuon_khong_lang_le_doi_ban_cau" \
    "…::test_pillow_duoi_13_co_cache_cung_tu_choi" "…::test_hai_luong_mo_anh_cung_luc_khong_de_lai_bo_loc_canh_bao"
3 passed in 26.71s

$ uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_soi_loi_t067.py \
    tests/test_ai_images.py tests/test_pillow_heif_setup.py -q -rsxX        (Windows, tại ba922e6,
                                                                            2026-10-20 16:43:14–16:44:35)
650 passed, 4 xfailed in 76.03s (0:01:16)
(0 hỏng, 0 bỏ qua, 0 xpass; 4 xfail đúng là SL-T067-1)

$ uv run ruff check .
All checks passed!
```

Toàn bộ `uv run pytest` không chạy (quy tắc 2026-10-20: Chỉ Huy chạy khi gộp).

**Thử ngược (test có bắt được lỗi không)**, bằng plugin pytest nháp trong thư mục tạm, không commit:

| Thử | Kết quả |
|---|---|
| Thay `_WARNINGS_LOCK` bằng khóa giả (không khóa gì), chạy 2 test nhiều luồng, 3 lần | Cả 3 lần **cả 2 test hỏng**: còn thừa bộ lọc `('error', …)` trong `warnings.filters`, và luồng mở được "ảnh bom" WebP/HEIF (`DID NOT RAISE ImageProcessError`), tức tái hiện cả 2 hướng (a), (b) của LC-T049-3. Với khóa thật: qua |
| Nạp `process.py` của `origin/main` (trước T-067) thay bản của nhánh | 65 ca Ref sai khuôn hỏng (ảnh ra vẫn còn GPS), 5 ca cache Pillow cũ hỏng, 4 ca N4, 3 ca N1 hỏng; SL-T067-1 thành XPASS (code cũ không báo). Các ca đối chứng (GPS đúng khuôn, Pillow ≥ 13, ASCII 1 ký tự, không tọa độ mà Ref phụ đúng khuôn) đều qua trên code cũ, tức là chúng kiểm hành vi chứ không kiểm tên hàm. 3 test nhiều luồng/khóa hỏng chỉ vì code cũ không có `_WARNINGS_LOCK` (không tính; phép thử khóa giả ở dòng trên mới có ý nghĩa) |

**Thử ngoài test** (script nháp, ảnh giả):

| Thử | Kết quả |
|---|---|
| Thẻ Ref ghi kiểu TIFF lạ (mã kiểu 0, 99) hoặc ASCII độ dài 0 | Pillow bỏ thẻ ngay lúc đọc nên module thấy "thiếu Ref", hiểu là Bắc/Đông, không báo. Xem Ghi nhận 2 |
| `GPSMapDatum` = `"0903 123 456"`, `"Nguyen Van An"`, `"Le Loi Q1"` | Vẫn giữ trong ảnh ra. Xem Ghi nhận 3 |
| `memoryview` đã `release()` | `ValueError` thô lọt ra, giống hệt trước T-067 (`len` và `nbytes` cùng báo lỗi này). Không do T-067; app chỉ truyền `bytes` nên không có đường đi. Không lập lỗi |

## Đối chiếu tiêu chí xong

- [x] **Việc 1: 3 lỗi đã sửa thật.** 3 test `xfail` của Soi Lỗi T-049 qua, thân test không đổi (mục Bằng chứng). SL-T049-1 sửa ở `process.py:496-501`, SL-T049-2 ở `:944`, SL-T049-3 ở `:85` và `:191-200`.
- [x] **Việc 2: thử lách nhanh.**
  - **GPS Ref sai khuôn → bỏ GPS và báo:** `test_ref_sai_khuon_nhieu_kieu_bo_ca_khoi_gps_va_bao` (17 kiểu với JPEG: `s`, `w`, `e` chữ thường; rỗng; `"N "`; `"1"`; `"SS"`; `"X"`; `GPSAltitudeRef` = `\x04`, `\xff`, 2 byte; Ref của hướng đi, hướng ảnh, tốc độ `"km"`, kinh độ đích, góc đích, khoảng cách đích), `test_ref_sai_khuon_moi_dinh_dang_bo_ca_khoi_gps_va_bao` (4 kiểu × PNG, WebP, HEIC), `test_ref_ghi_sai_kieu_tiff_bo_ca_khoi_gps_va_bao` (9 kiểu sửa thẳng byte EXIF × 4 định dạng: Ref vĩ độ kiểu UNDEFINED, BYTE, SHORT, ASCII đệm null; Ref độ cao kiểu UNDEFINED 2 byte, BYTE 2 phần tử, ASCII, SBYTE, LONG). Mỗi ca kiểm: ảnh gốc mang đúng thẻ sai, `web.gps is None`, `notice` đúng câu cố định, ảnh ra không còn khối GPS, hãng máy vẫn giữ.
  - **GPS đúng khuôn giữ đúng giá trị:** `test_du_10_the_ref_dung_khuon_giu_gps_dung_tung_gia_tri` (đủ 10 thẻ Ref × Bắc/Đông và Nam/Tây × 4 định dạng: khối GPS đọc lại **bằng** ảnh gốc, dấu tọa độ đúng), `test_ref_ghi_kieu_ascii_mot_ky_tu_khong_null_van_giu`. Ma trận 32 + 24 ca của Soi Lỗi T-049 vẫn qua.
  - **`PreviewCache.get` với Pillow < 13:** `test_cache_moi_phien_ban_duoi_13_tu_choi_ca_khi_cache_tat` (5 phiên bản `12.3.0`, `12.99.99`, `9.5.0`, `11.0`, `0.1` × cache có sẵn và cache tắt: câu `_MSG_OLD_PILLOW`, không gọi `stat_image`/`read_image_bytes`, cache tắt thì không tạo thư mục; Pillow 13 trở lại thì lấy lại đúng ảnh cũ), `test_cache_pillow_13_tro_len_van_tra_anh` (`13.0.0`, `13.2.1`, `14.0.0`, `20.1.0.dev0`).
  - **Nhiều luồng:** `test_nhieu_luong_anh_that_moi_anh_giu_dung_gps_cua_minh_khong_treo` (24 ảnh 4 định dạng, mỗi ảnh một vị trí riêng, 72 lượt × (ảnh web + bản AI + xem trước) trên 8 luồng: GPS mỗi ảnh ra đúng bằng ảnh gốc của nó, bản AI không có `GPS`/`Exif`, bộ lọc cảnh báo sau bằng trước, khóa đã trả), `test_nhieu_luong_canh_bao_bom_luon_thanh_loi_o_moi_luong` (200 lượt: ảnh 1.200 điểm ảnh khi giới hạn Pillow hạ còn 1.000, 4 định dạng, xen ảnh nhỏ mở bình thường: mọi lượt "bom" đều báo "quá nhiều điểm ảnh"), `test_image_open_nem_base_exception_van_tra_khoa_va_bo_loc` (`Image.open` ném `BaseException` → khóa được trả, bộ lọc không đổi, lần mở sau ở luồng khác không treo). Luồng chạy nền có hạn chờ: khóa bị giữ mãi thì test hỏng chứ không treo. Hai test đầu làm `Image.open` chậm 2 ms để các luồng kịp chen nhau (không làm chậm thì khóa giả vẫn qua, đã thử).
  - **N1, N4 không làm hỏng gì:** `test_n1_bien_the_chu_gps_chi_bo_the_do_vi_tri_van_giu` (11 ca biên: `GPSMapDatum` 16/17 ký tự, `WGS84`, có xuống dòng, có `_`, rỗng; `GPSSatellites` 64/65 chữ số, `1,2,3`, có dấu cách, rỗng: chỉ bỏ đúng thẻ đó, vị trí vẫn giữ, không báo hỏng, các thẻ GPS khác giữ nguyên), `test_n4_memoryview_moi_kieu_phan_tu_mo_dung_va_do_theo_byte` (phần tử 1, 2, 4, 8 byte và 2 chiều: mở đúng ảnh; giới hạn dung lượng tính theo byte, đúng biên), `test_n4_memoryview_khong_lien_mach_bao_cau_co_dinh`.
- [x] **Việc 3: lỗi mới có test `xfail(strict=True)` mã SL-T067-1** trong `tests/test_soi_loi_t067.py` (mục dưới). Không sửa code ứng dụng.
- [x] **Việc 4: test liên quan và `ruff`** (mục Bằng chứng).
- [x] **Việc 5: báo cáo này**, có kết luận.

## Lỗi tìm được

| Mã | Mức | Tóm tắt | Test |
|---|---|---|---|
| SL-T067-1 | Thấp | Ảnh không có tọa độ mà có thẻ Ref phụ sai khuôn bị báo "GPS hỏng" (mới từ T-067) | `test_khong_co_toa_do_ma_ref_phu_sai_khuon_khong_bao_hong` (4 ca) |

### SL-T067-1 (Thấp): báo "GPS hỏng" cho ảnh không có vị trí

- **Tái hiện:** JPEG có khối GPS chỉ gồm `GPSVersionID` và **một** thẻ Ref phụ sai khuôn, không có vĩ độ, kinh độ (ví dụ `GPSSpeedRef = "k"`, `GPSAltitudeRef = b"\x04"`, `GPSImgDirectionRef = "t"` hoặc `GPSDestLatitudeRef = "s"`) → `make_web_image`.
- **Mong đợi:** `web.gps is None`, ảnh ra không có GPS, `notice == ""`. Đây là cách T-049 đã chốt: "Chỉ báo người dùng khi ảnh gốc có ghi tọa độ (máy tắt định vị có thể chỉ ghi phiên bản GPS)" (`process.py:502-507`, test `test_khoi_gps_khong_co_toa_do_thi_bo_khong_bao_hong`). Đối chứng có trong file: cùng ảnh với Ref phụ đúng khuôn thì không báo (`test_khong_co_toa_do_ref_phu_dung_khuon_khong_bao_hong`).
- **Thực tế:** `notice` = "Thông tin GPS của ảnh gốc bị hỏng nên ảnh nén không có vị trí GPS." Lớp kiểm Ref mới (`:496-501`) chạy **trước** lớp kiểm "có tọa độ không" (`:502-507`) và không xét ảnh có tọa độ hay không. Trên `origin/main` 4 ca này không báo (đã chạy: XPASS).
- **Ảnh hưởng:** không lộ, không sai vị trí (ảnh vốn không có vị trí). Chỉ là câu báo sai sự thật một nửa: khi T-056 hiện câu báo, chủ dự án có thể tưởng máy ảnh ghi định vị bị lỗi. Ca này hiếm (máy tắt định vị thường không ghi thẻ Ref phụ).
- **Gợi ý:** chỉ trả `_NOTICE_GPS_BROKEN` vì Ref sai khuôn khi ảnh gốc có thẻ tọa độ (`_GPS_COORDINATE_TAGS`); không có thì đi tiếp nhánh "không có tọa độ" như cũ. Hoặc theo phương án (b) ở Ghi nhận 1. Gỡ `xfail` khi XPASS.

## Ghi nhận cho Lá Chắn (không lập lỗi)

1. **`GPSAltitudeRef` = 2, 3 có thể là giá trị hợp lệ (Exif 3.0).** Bảng thẻ GPS hiện hành của ExifTool ghi `2 = Positive Sea Level (sea-level ref)`, `3 = Negative Sea Level (sea-level ref)` ([exiftool.org/TagNames/GPS.html](https://exiftool.org/TagNames/GPS.html)); một chủ đề trên diễn đàn ExifTool nói 2, 3 hợp lệ từ Exif bản 3 và 0, 1 đổi nghĩa thành "trên/dưới ellipsoid" ([exiftool.org/forum, msg 91824](https://exiftool.org/forum/index.php?msg=91824)). **Chưa đối chiếu với tài liệu chuẩn của CIPA, chưa gặp máy nào ghi 2, 3**, nên đây chỉ là suy luận. Nếu đúng thì máy theo Exif 3.0 ghi `GPSAltitudeRef = 2` sẽ **mất cả vị trí** sau T-067 (trên `main` vẫn giữ vĩ độ, kinh độ; chỉ dấu độ cao có thể sai với giá trị 3). Test của Thợ Máy (`test_the_ref_gps_sai_khuon_thi_bo_ca_khoi_gps_va_bao`, ca `b"\x02"`) đang chốt hành vi này; test của Soi Lỗi cố ý dùng `\x04`, `\xff` (sai ở mọi phiên bản) để không chốt thêm. Hai phương án cho Lá Chắn:
   - (a) Giữ như hiện nay (an toàn: không bao giờ đăng thông tin có thể sai nghĩa).
   - (b) Chỉ Ref vĩ độ, kinh độ sai khuôn mới bỏ cả khối GPS và báo. Ref **phụ** (độ cao, tốc độ, hướng đi, hướng ảnh, điểm đích) sai khuôn thì bỏ riêng cặp thẻ đó (Ref và giá trị đi kèm), giữ vị trí. Cách này vẫn không đăng giá trị sai nghĩa, giữ GPS cho SEO địa phương (2A), và giải luôn SL-T067-1 cùng Rủi ro 3 của Thợ Máy.
2. **Thẻ Ref có trong file nhưng Pillow không đọc được** (mã kiểu TIFF lạ như 0, 99; ASCII độ dài 0): Pillow bỏ thẻ ngay lúc đọc, nên module coi là "thiếu Ref", hiểu là Bắc/Đông và không báo. Đã thử: ảnh có `GPSLatitudeRef` = `"S"` nhưng ghi mã kiểu 99 → `web.gps` = (10.776, −106.687), `notice` rỗng. File ra có vĩ độ mà không có Ref, tức giống cách Pillow đọc file gốc; ExifTool cũng bỏ thẻ có kiểu lạ (suy luận, chưa chạy ExifTool), nên file ra không đổi nghĩa so với gốc. Cùng loại với **Rủi ro 4 của Thợ Máy** (thẻ Ref thiếu hẳn): nếu Lá Chắn chọn "có tọa độ mà thiếu Ref thì coi GPS hỏng" thì ca này cũng được xử lý.
3. **N1: `GPSMapDatum` vẫn chở được ≤ 16 ký tự chữ, số, dấu cách, gạch nối**, ví dụ số điện thoại `"0903 123 456"` hay tên `"Nguyen Van An"` vẫn còn trong ảnh đăng web (test của Thợ Máy chỉ thử số điện thoại ở `GPSSatellites`). Đúng mẫu Lá Chắn gợi ý (`[A-Za-z0-9 -]{1,16}`) và Lá Chắn đã đánh giá rủi ro "không đáng kể"; ghi lại để Lá Chắn biết giới hạn của mẫu này. Máy thật chỉ ghi `WGS-84`, `WGS 84`, `TOKYO`…
4. **Rủi ro 1 của Thợ Máy đúng như mô tả:** Streamlit 1.65 có `warnings.catch_warnings()` ở `streamlit/dataframe_util.py:753` và `streamlit/elements/widgets/data_editor.py:461` (và chú thích "not thread-safe" ở `streamlit/auth_util.py:252`). Soi Lỗi không thử phần tương tác này.

## Rủi ro và điểm cần chú ý

1. **Chưa thử ảnh thật** (iPhone, Android, máy ảnh có GPS, ảnh đã qua phần mềm sửa ảnh): mọi ca dùng ảnh giả tạo trong test. Nên thử khi có T-056, nhất là xem có máy nào ghi `GPSAltitudeRef` = 2, 3 hay Ref đệm null không (hai loại này nay bị bỏ cả vị trí).
2. Test nhiều luồng phát hiện lỗi theo xác suất: với khóa giả hỏng 3/3 lần chạy nhờ làm chậm `Image.open` 2 ms; với khóa thật thì luôn qua (khóa bảo đảm). Thời gian: 2 test này 1–3 giây. Test SL-T049-3 cũ chạy khoảng 10 giây (đúng thiết kế, Thợ Máy đã ghi).
3. `tests/test_soi_loi_t067.py` dùng lại hàm dựng ảnh của `tests/test_soi_loi_t049.py` (`_exif_gps`, `_nguon`, `_gps`, fixture trả nguyên bảng Pillow): đổi các hàm đó thì kiểm lại file này.

## Đề xuất

- **Thợ Máy:** sửa SL-T067-1 (vài dòng ở `process.py:496-507`) ngay trong T-067 nếu còn lượt, hoặc gom vào phiếu dọn; gỡ `xfail` khi XPASS, không đổi điều kiện kiểm. Nếu Lá Chắn chọn phương án (b) ở Ghi nhận 1 thì sửa theo (b), SL-T067-1 hết theo.
- **Lá Chắn (rút gọn):** xét Ghi nhận 1 (Exif 3.0, chọn a hay b), Ghi nhận 2 cùng Rủi ro 4 của Thợ Máy, Ghi nhận 3.
- **Chỉ Huy:** khi thử ảnh thật trên máy (không commit ảnh), xem có ảnh nào bị báo "GPS hỏng" bất ngờ không.

## Câu hỏi cho chủ dự án

Không có.

## Điều kiện của kết luận ĐẠT CÓ ĐIỀU KIỆN

| # | Điều kiện | Ai làm | Hạn |
|---|---|---|---|
| 1 | Sửa SL-T067-1 (hoặc Lá Chắn chốt cách khác thay thế), gỡ 4 `xfail` khi XPASS | Thợ Máy | Trước khi gộp **T-056** (lúc câu báo hiện lên giao diện). Không chặn gộp T-067 hay T-054 |
| 2 | Lá Chắn quyết Ghi nhận 1 (`GPSAltitudeRef` 2, 3) và Ghi nhận 2 (cùng Rủi ro 4) | Lá Chắn | Khi soát T-067 |

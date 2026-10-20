# Báo cáo T-067 · Dọn lỗi Thấp xử lý ảnh (sau T-049)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-067](../tickets/T-067-don-loi-thap-xu-ly-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- **Ảnh có GPS ghi sai chuẩn** (chữ chỉ hướng viết thường `s`, `w`, hoặc độ cao "dưới mặt biển" ghi sai kiểu) không còn lên web với vị trí sai bán cầu: app bỏ hẳn vị trí của ảnh đó và báo "Thông tin GPS của ảnh gốc bị hỏng nên ảnh nén không có vị trí GPS." Ảnh chụp bình thường (iPhone, Android ở Việt Nam) vẫn giữ GPS đúng từng con số như trước (quyết định 2A).
- **Ảnh xem trước** luôn kiểm phiên bản thư viện ảnh trước khi hiện, kể cả ảnh đã có sẵn trong bộ nhớ đệm.
- **Hai tab trình duyệt mở ảnh cùng lúc** không còn làm rối cài đặt cảnh báo của cả app: phần mở ảnh có khóa, mỗi lúc chỉ một tab đi qua đoạn đó (rất ngắn, chỉ đọc phần đầu file); phần giải mã ảnh vẫn chạy song song.
- Làm thêm 2 ghi nhận không bắt buộc của Lá Chắn: N1 (2 thẻ chữ còn giữ trong khối GPS không chở được chữ tự do) và N4 (đo dung lượng ảnh đúng theo byte với mọi kiểu dữ liệu).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/process.py` | LC-T049-1: `_GPS_REF_TAGS` + kiểm trong `_KeptExif.from_source` (`:338-351`, `:496-501`). LC-T049-2: `_require_pillow_13()` ở đầu `PreviewCache.get` (`:944`). LC-T049-3: `_WARNINGS_LOCK` (`:85`) + hàm `_pillow_open` (`:191-200`), `_open` gọi hàm này. N1: `_GPS_MAP_DATUM`, `_GPS_SATELLITES` (`:285-286`), kiểu `datum`/`satellites` trong `_valid` (`:390-393`). N4: `nbytes` (`:157`) |
| `tests/test_images_process.py` | 7 hàm test mới, 26 trường hợp (liệt kê ở mục Đối chiếu) |
| `tests/test_soi_loi_t049.py` | Gỡ 3 dấu `xfail(strict=True)` của SL-T049-1, 2, 3 (thay bằng 1 dòng chú thích "sửa ở T-067"); thân test và điều kiện kiểm giữ nguyên |
| `docs/team/reports/T-067-tho-may.md` | Báo cáo này |

Không sửa `folders.py`, `tags.py`, `alt.py`, `naming.py`, `app/**`, `config/**`, không thêm thư viện (`git diff --stat origin/main...HEAD`: 3 file code/test + báo cáo).

Commit trên `team/T-067` (mỗi phần một commit, đã đẩy lên GitHub): `496d518` (LC-T049-1), `9a8c7e5` (LC-T049-2), `51e2895` (LC-T049-3), `090f15a` (N4), `f564e5d` (N1), và commit báo cáo.

## Bằng chứng

```
$ uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_ai_images.py \
    tests/test_pillow_heif_setup.py tests/test_images_folders.py -q -rsxX     (Windows, tại f564e5d,
                                                                             2026-10-20 15:06–15:07)
688 passed, 6 skipped in 75.79s (0:01:15)
(0 hỏng, 0 xfail, 0 xpass. 6 bỏ qua đều ở test_images_folders.py: symlink cần Developer Mode và
 nhánh Mac/Linux, có từ T-048. So với lượt của Lá Chắn T-049 "659 passed, 6 skipped, 3 xfailed":
 3 xfail nay thành passed, thêm 26 trường hợp mới: 659 + 3 + 26 = 688.)

$ uv run ruff check .
All checks passed!
```

Toàn bộ `uv run pytest` không chạy (quy tắc 2026-10-20: Chỉ Huy chạy khi gộp).

**Thử ngược (test có bắt được lỗi không):** script nháp trong thư mục tạm (không commit) thay `_WARNINGS_LOCK` bằng khóa giả không khóa gì, rồi chạy 2 test nhiều luồng: `test_nhieu_luong_mo_anh_cung_luc_bo_loc_canh_bao_giu_nguyen` **hỏng** (`assert sau == truoc`: còn thừa bộ lọc `('error', …, DecompressionBombWarning…)`), test của Soi Lỗi trở về XFAIL. Với khóa thật: cả hai qua. Test N4 trên code cũ: `len()` = 500 phần tử ≤ 1000 nên lọt qua bước kiểm dung lượng (suy ra từ code cũ, `process.py` tại `main` dòng 150).

## Cách làm chính

| Lỗi | Cách sửa | Vì sao chọn cách này |
|---|---|---|
| LC-T049-1 | Thẻ "Ref" **có trong ảnh gốc** mà bị loại vì sai khuôn → trả `_KeptExif` với GPS rỗng và `notice = _NOTICE_GPS_BROKEN`. Áp cho cả 10 thẻ Ref của chuẩn GPS (`_GPS_REF_TAGS`): vĩ độ, kinh độ, độ cao (bắt buộc theo phiếu) và tốc độ, hướng đi, hướng ảnh, vĩ độ/kinh độ đích, hướng/khoảng cách đích | Đúng đề xuất của Lá Chắn ("an toàn hơn chuẩn hóa chữ hoa: không bao giờ đăng tọa độ có thể sai"). Mở rộng ra mọi thẻ Ref vì cùng một kiểu lỗi: bỏ thẻ Ref thì giá trị đi kèm bị hiểu theo mặc định (vĩ độ đích `s` cũng thành Bắc). Thẻ Ref **không có** trong ảnh gốc thì giữ cách cũ (file ra mơ hồ đúng như file gốc, không đổi nghĩa) |
| LC-T049-2 | `_require_pillow_13()` là dòng đầu của `PreviewCache.get`, trước `stat_image`, trước khi đọc cache | Test kiểm cả "không đụng thư mục ảnh, không đọc cache" khi Pillow < 13 |
| LC-T049-3 | Khóa `threading.Lock` cấp module + `catch_warnings` chỉ bọc **lời gọi `Image.open`** (hàm `_pillow_open`); kiểm số điểm ảnh, `draft`, `load` nằm ngoài khóa nhưng vẫn trong cùng khối `try` bắt lỗi | Đúng cách Lá Chắn đề xuất ("bọc riêng lời gọi `Image.open`, chỗ duy nhất Pillow phát cảnh báo này"). Đã soát Pillow 13.0.0: với JPEG/PNG/WebP/HEIF, `_decompression_bomb_check` chỉ được gọi trong `Image.open` (`PIL/Image.py:3693`, `WebPImagePlugin.py:77`); `MpoImagePlugin.py:165` nằm trong `seek` (module không gọi); pillow-heif không gọi. Có test giữ điều này nếu Pillow đổi (`test_pillow_chi_kiem_bom_trong_khoa_va_bo_loc`). Nhờ vậy phần giải mã ảnh lớn (1–2 giây với ảnh 48 MP) của các tab không phải xếp hàng. Vẫn giữ "cảnh báo thành lỗi" (Lá Chắn T-047 điều kiện 2), không bỏ bộ lọc |
| N1 | `GPSMapDatum` chỉ nhận `[A-Za-z0-9 -]{1,16}`, `GPSSatellites` chỉ nhận số và dấu phẩy (tối đa 64) | Đúng gợi ý của Lá Chắn. Sai dạng thì chỉ bỏ thẻ đó; vị trí vẫn giữ, không báo hỏng (2 thẻ này không đổi nghĩa thẻ khác) |
| N4 | `memoryview` đo bằng `nbytes` | Gợi ý của Lá Chắn |

## Đối chiếu tiêu chí xong

- [x] **LC-T049-1** (`process.py:338-351`, `:496-501`). Test: `test_the_ref_gps_sai_khuon_thi_bo_ca_khoi_gps_va_bao` (`tests/test_images_process.py:947`, 8 trường hợp: `s`, `w`, `n` chữ thường, `EW` hai chữ, `GPSAltitudeRef = b"\x02"`, **`GPSAltitudeRef` kiểu SHORT** (dựng bằng cách sửa byte EXIF, `_altitude_ref_kieu_short` `:916`; Soi Lỗi ghi là chưa dựng được), `GPSSpeedRef = "k"`, `GPSDestLatitudeRef = "s"`; mỗi ca: ảnh gốc mang đúng thẻ sai, ảnh ra không còn khối GPS, `gps is None`, `notice` đúng câu cố định, hãng máy vẫn giữ). Đối chứng `test_the_ref_gps_dung_khuon_giu_nguyen_ban_cau_va_do_cao` (`:924`): cùng ảnh với thẻ Ref đúng khuôn (Nam/Tây, dưới mặt biển, `K`, vĩ độ đích `S`) giữ nguyên GPS đúng từng giá trị, tọa độ âm. Test của Soi Lỗi `test_gps_ref_sai_khuon_khong_lang_le_doi_ban_cau` XPASS → đã gỡ `xfail` (`tests/test_soi_loi_t049.py:375-376`); ma trận GPS 32 + 24 ca của Soi Lỗi và test 2A vẫn qua
- [x] **LC-T049-2** (`process.py:942-944`). Test: `test_cache_co_san_van_tu_choi_khi_pillow_duoi_13` (`tests/test_images_process.py:1322`: cache có sẵn, Pillow "12.3.0" → câu `_MSG_OLD_PILLOW`, `stat_image`/`read_image_bytes` không được gọi, file cache không đổi; Pillow 13 trở lại thì lấy lại đúng ảnh trong cache). Test Soi Lỗi `test_pillow_duoi_13_co_cache_cung_tu_choi` XPASS → đã gỡ `xfail` (`tests/test_soi_loi_t049.py:718-719`)
- [x] **LC-T049-3** (`process.py:82-85`, `:191-200`, `:214`). Test: `test_nhieu_luong_mo_anh_cung_luc_bo_loc_canh_bao_giu_nguyen` (`:583`: 32 lần mở ảnh trên 8 luồng, `Image.open` được làm chậm 10 ms để các luồng chen nhau; bộ lọc cảnh báo sau giống hệt trước, mỗi lúc chỉ 1 luồng trong khối, bộ lọc "thành lỗi" luôn có khi mở), `test_pillow_chi_kiem_bom_trong_khoa_va_bo_loc` (`:619`, 4 định dạng × ảnh web + bản AI + xem trước: mọi lần Pillow kiểm "bom" đều đang giữ khóa và có bộ lọc), `test_khoa_mo_anh_duoc_tra_khi_loi` (`:639`: file rác, PNG hỏng, cảnh báo bom thành lỗi → khóa được trả, bộ lọc không đổi). Test Soi Lỗi `test_hai_luong_mo_anh_cung_luc_khong_de_lai_bo_loc_canh_bao` XPASS → đã gỡ `xfail` (`tests/test_soi_loi_t049.py:727-729`)
- [x] **Gỡ 3 `xfail` khi XPASS, không đổi điều kiện kiểm:** mỗi `xfail` gỡ ngay sau khi thấy `[XPASS(strict)]` ở lần chạy trước đó; `git diff origin/main...HEAD -- tests/test_soi_loi_t049.py` chỉ có 3 khối decorator bị thay bằng dòng chú thích
- [x] **N1** (không bắt buộc): `test_the_gps_chu_chi_nhan_dang_may_that_ghi` (`:980`, 9 ca: `WGS-84`, `WGS 84`, `TOKYO`, `05`, `04,07,12` giữ; địa chỉ, chữ có dấu phẩy, số điện thoại có dấu cách bị bỏ; vị trí vẫn giữ, không báo hỏng)
- [x] **N4** (không bắt buộc): `test_kiem_dung_luong_memoryview_dem_theo_byte` (`:489`: `memoryview` phần tử 4 byte, 500 phần tử = 2000 byte > giới hạn 1000 → "Ảnh quá lớn", không mở ảnh; `memoryview` rỗng → câu "rỗng"; `memoryview` của PNG thật vẫn dùng được)
- [x] Test liên quan qua, `ruff` sạch (mục Bằng chứng). Test không gọi mạng, ảnh tạo trong bộ nhớ, không commit ảnh
- [x] F2: GPS vẫn giữ có chủ đích với ảnh đúng khuôn, so từng giá trị sau nén (không đổi `_verify_web_image`); thêm: không bao giờ đăng tọa độ có thể sai bán cầu. F3: vẫn bắt đủ lỗi quanh cả `open` lẫn `load` trong cùng khối `try` (`process.py:213-236`), `formats` cố định, giữ "cảnh báo bom thành lỗi"

## Rủi ro và điểm cần chú ý

1. **Khóa chỉ giữ trật tự cho code của app.** Streamlit cũng dùng `warnings.catch_warnings()` trong luồng của phiên ở 2 chỗ (`streamlit/dataframe_util.py:753` khi bảng dữ liệu không phải pandas có `__dataframe__`, `streamlit/elements/widgets/data_editor.py:461`). Nếu đúng lúc một tab mở ảnh mà tab khác đang dựng bảng qua 2 chỗ này thì vẫn có thể (a) để lại bộ lọc "cảnh báo bom thành lỗi" cho cả app, hoặc (b) mất bộ lọc trong chốc lát. Cả hai đúng là trường hợp Lá Chắn đã phân tích ở LC-T049-3: (a) chỉ chặt hơn, (b) không mở lỗ vì phép so 80 triệu điểm ảnh của app luôn quyết định trước ngưỡng 89,5 triệu của Pillow. Khe này nhỏ hơn nhiều so với trước (chỉ còn khi trùng với 2 chỗ của Streamlit) và không đóng hẳn được trên Python 3.12 (Python 3.14 mới có cảnh báo theo ngữ cảnh). Cách khác nếu Lá Chắn muốn đóng hẳn: thêm **một lần, vĩnh viễn** bộ lọc "DecompressionBombWarning thành lỗi" cho cả chương trình (cách Streamlit tự làm ở `streamlit/auth_util.py:249-271`) thay vì bật/tắt mỗi lần mở ảnh; đổi lại mọi chỗ dùng Pillow trong app đều coi ảnh 89,5–179 triệu điểm ảnh là lỗi. Không làm trong phiếu này vì phiếu chỉ định khóa.
2. **Test của Soi Lỗi `test_hai_luong_mo_anh_cung_luc_khong_de_lai_bo_loc_canh_bao` nay chạy khoảng 10 giây** (đo: 10,02 s): luồng A chờ luồng B vào khối tới hết thời gian chờ 10 giây, mà có khóa thì B không vào được. Đúng là điều test muốn chứng minh; không đổi điều kiện kiểm nên để nguyên, đã ghi chú trên test (`tests/test_soi_loi_t049.py:727-728`).
3. **LC-T049-1 chặt hơn đề xuất tối thiểu:** thẻ Ref sai khuôn ở cả thẻ phụ (tốc độ, hướng, điểm đích) cũng làm bỏ cả khối GPS. Điện thoại thật (iPhone ghi `K`, `T`; Android ghi vĩ độ, kinh độ, độ cao) luôn ghi đúng chữ hoa nên không bị ảnh hưởng (suy luận theo chuẩn EXIF và dữ liệu thử của Soi Lỗi; chưa thử ảnh thật). Nếu Lá Chắn thấy quá chặt, chỉ cần rút `_GPS_REF_TAGS` về 3 thẻ đầu.
4. Thẻ Ref **thiếu hẳn** trong ảnh gốc (có vĩ độ mà không có `GPSLatitudeRef`) vẫn được hiểu là Bắc/Đông như trước: file ra giống file gốc ở điểm này, mọi trình đọc ảnh cũng hiểu như vậy. Không thuộc LC-T049-1 (lỗi là "bỏ lặng lẽ thẻ có trong ảnh"); ghi lại để Lá Chắn xét.
5. `ruff format --check` báo 2 chỗ định dạng có từ trước ở `process.py` (`expected = (…)` trong `_verify_web_image`) và `tests/test_images_process.py` (1 dòng trống trước mục tên file), không phải dòng của phiếu này; không sửa để diff gọn. Dự án chỉ yêu cầu `ruff check`.

## Đề xuất

- **Soi Lỗi (rút gọn):** chạy lại 3 test đã gỡ `xfail` và 26 trường hợp mới; thử thêm GPS ghi sai chuẩn kiểu khác (Ref có dấu cách `"N "`, `GPSAltitudeRef` kiểu UNDEFINED nhiều byte) và nhiều tab mở ảnh cùng lúc trong app thật khi có T-056.
- **Lá Chắn (rút gọn, soát diff):** xét Rủi ro 1 (giữ khóa như phiếu hay chuyển sang bộ lọc vĩnh viễn), Rủi ro 3 (phạm vi `_GPS_REF_TAGS`), Rủi ro 4 (thẻ Ref thiếu hẳn). Sau phiếu này: điều kiện 1 của biên bản T-049 xong, T-054 (cần LC-T049-1) và T-056 (cần LC-T049-2, -3) hết bị chặn bởi T-049.
- **T-056 (giao diện):** hiện `WebImage.notice` khi có (nay có thêm trường hợp GPS ghi sai chuẩn), như điều kiện 3 của Lá Chắn T-049.

## Câu hỏi cho chủ dự án

Không có.

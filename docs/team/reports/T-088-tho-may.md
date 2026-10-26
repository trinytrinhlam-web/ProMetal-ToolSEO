# Báo cáo T-088 · Dọn lỗi Thấp client WordPress sau T-085 (SL-T085-1, -2, -3, LC-T085-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-088](../tickets/T-088-don-client-wordpress-sau-t085.md) |
| Nhánh | `team/T-088` (từ `main` `dd5ea2d`) |
| Ngày nộp | 2026-10-26 |
| Kết quả | **Hoàn thành**: đủ 5 yêu cầu. Không phải sửa test cũ nào (ngoài việc gỡ dấu `xfail`) |

## Tóm tắt (cho chủ dự án)

- Chốt chặn «không xin website trả nội dung bài» nay bịt nốt mẹo chèn ký tự vô hình NUL sát tên trường (website tự cắt ký tự đó rồi vẫn trả nội dung, tức chạy shortcode). Hôm nay chưa có đường nào đưa chữ lạ vào đó; đây là chốt chặn cho các phiếu sau.
- Website (hay plugin, proxy hỏng) trả dữ liệu lạ, lồng quá sâu thì trang Kết nối WordPress và «Gửi nháp» không còn hiện khung lỗi Python (kèm đường dẫn thư mục trên máy), mà hiện một câu tiếng Việt cố định kèm mã lỗi.
- Trang Kết nối WordPress, tải ảnh đại diện: nếu lệnh tải lỗi mà không phải website từ chối rõ ràng (mất mạng, hết giờ, website lỗi 5xx, trả lời hỏng), câu báo dặn thêm «Ảnh có thể đã lên thư viện Media của website: kiểm Media → Thư viện… trước khi tải lại», để bạn không tải trùng ảnh. Website từ chối rõ ràng (ví dụ không đủ quyền, file quá lớn) thì giữ câu cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `_PHP_TRIM` + `_asks_rendered_fields` cắt hai đầu tên trường như `trim()` (SL-T085-1); `_json`, `_error_from` bắt mọi lỗi giải mã, câu `_json` kèm mã HTTP (SL-T085-2, LC-T085-1); `upload_media` bọc lệnh tải (`_MEDIA_MAYBE_UPLOADED`, `_MEDIA_UPLOAD_UNEXPECTED`, SL-T085-3) và bắt cả lỗi lạ ở lệnh ghi đè (LC-T085-1); 1 dòng chú thích cạnh `ALLOWED_JSON_KEYS` (Ghi nhận 2 của Soi Lỗi T-085) |
| `tests/test_wordpress_t088.py` | Mới: 141 ca (chặn và đối chứng) |
| `tests/test_soi_loi_t085.py` | Gỡ 4 dòng dấu `xfail` (36 ca: SL-T085-1 27, SL-T085-2 3, SL-T085-3 6), chỉ xóa dấu |
| `tests/test_la_chan_t085.py` | Gỡ 2 dòng dấu `xfail` (4 ca LC-T085-1), chỉ xóa dấu |

Không sửa `app/**`, `config/**`, `seo_app/onpage/**`, `seo_app/storage/drafts.py`, `seo_app/site_index.py` (của T-041). Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`.

## Cách sửa từng yêu cầu

1. **SL-T085-1 (NUL trong `_fields`).** WordPress tách `_fields` bằng `wp_parse_list` (chỉ dấu phẩy, khoảng trắng ASCII) rồi `get_fields_for_response` chạy `trim()` của PHP trên từng tên (cắt `" \t\n\r\0\x0b"`, **có NUL**), nên `"\x00content"` vẫn là `content`. `_asks_rendered_fields` (`client.py:249`) nay cắt hai đầu mỗi phần bằng đúng bộ ký tự đó (`_PHP_TRIM`, `client.py:125`), và cắt thêm hai đầu tên trước dấu chấm cho chắc (`"content\x00.rendered"` bị chặn dù WordPress không dựng). Phần chỉ còn rỗng sau khi cắt không tính là tên, nên `_fields` chỉ có NUL bị chặn như `_fields` rỗng. NUL ở **giữa** tên (`"con\x00tent"`) WordPress không cắt, vô hại, vẫn cho đi. Đây là cách «cắt `" \t\n\r\0\x0b"` hai đầu như `trim()`» trong lời giao; không chọn danh sách ký tự tuyệt đối `[A-Za-z0-9_.,]` vì phải sửa 6 ca test cũ của Soi Lỗi T-060.
2. **SL-T085-2 + LC-T085-1 (JSON lạ).** Hai chỗ duy nhất gọi `response.json()`: `_json` (`client.py:1517`) bắt **mọi** lỗi lúc giải mã (không phải JSON, chữ hỏng, `RecursionError` khi lồng quá sâu, lỗi lạ của thư viện) thành câu cố định, nay kèm mã HTTP: «WordPress không trả về dữ liệu JSON đọc được (mã N; có thể là trang HTML hay dữ liệu hỏng)…»; `status_code` của lỗi vẫn để trống như trước, để các nhánh đang xét mã lỗi (`_siteseo_abilities`, `_get_pages_checked`, ghi SEO, gửi nháp kèm ảnh) không đổi cách hiểu. `_error_from` (`client.py:1537`) bắt mọi lỗi giải mã thân lỗi thì coi như thân rỗng, vẫn ra câu cố định theo mã HTTP. Khối `try` chỉ bọc đúng bước giải mã. Trong `upload_media`, phần bọc lệnh ghi đè bắt thêm lỗi lạ (không phải `WordPressError`) thành cùng câu «Ảnh đã lên thư viện Media… mã ảnh N… Media → Thư viện» (`client.py:1178-1179`).
3. **SL-T085-3 (lỗi ở lệnh tải ảnh).** `upload_media` bọc `_post_media` (`client.py:1144-1158`) theo đúng quy tắc của gửi nháp kèm ảnh (`maybe_uploaded`): lỗi có mã 4xx là lời từ chối rõ ràng, ảnh chưa lên, **ném lại nguyên lỗi cũ** (câu không đổi); còn lại (hết giờ, mất kết nối, SSL, 3xx, 5xx, câu trả lời hỏng kể cả `201` thiếu mã hay là trang HTML, mã khác `201`) thì thêm câu `_MEDIA_MAYBE_UPLOADED` (`client.py:386`): «Ảnh có thể đã lên thư viện Media của website: kiểm Media → Thư viện trong trang quản trị WordPress trước khi tải lại (tải lại sẽ thêm một ảnh nữa).»; giữ `status_code`, `code` của lỗi gốc. Lỗi lạ: «Tải ảnh lên WordPress gặp lỗi không mong đợi (TênLớpLỗi).» cộng câu trên. Mã khác `201` (`_MEDIA_NOT_CREATED`) cũng thêm câu này (bản sửa mẫu của Lá Chắn để riêng ca này): website trả 200/202 có thể đã tạo ảnh mới hoặc trả lại ảnh đã có, nên «kiểm Media → Thư viện trước khi tải lại» vẫn đúng, và khớp với nhánh gửi nháp kèm ảnh (ca này ở đó cũng bật `maybe_uploaded`).
4. **Không chặn oan.** Mọi hằng `_fields` của app vẫn đi ra (`test_hang_fields_cua_app_van_gui`, cùng ca đối chứng có sẵn của Soi Lỗi, Lá Chắn T-085); thử ngẫu nhiên 5.000 giá trị `_fields` có NUL và mọi khoảng trắng ASCII so với bản Python riêng của WordPress: không giá trị nào đi ra mà WordPress dựng trường chạy shortcode, và vẫn đủ nhiều giá trị đi ra. Đủ 54 file test có dùng client WordPress hay luồng gửi nháp kèm ảnh qua, kể cả trang Kết nối WordPress và «Gửi nháp» (`tests/test_app_images.py`, `tests/test_la_chan_t056.py`, `tests/test_soi_loi_t056.py`).
5. **Gỡ `xfail` khi XPASS:** 6 dòng dấu (40 ca) đều XPASS thật trước khi gỡ (`--runxfail`: 748/748 qua), chỉ xóa dấu.

## Bằng chứng

Bộ test mới chạy trên **code cũ** (`seo_app` của `dd5ea2d` giải nén vào thư mục nháp, nạp qua `PYTHONPATH`; bản tạm của file test, đã xóa): **117 hỏng, 24 qua** (141 ca). 24 ca qua là 19 ca đối chứng (hằng `_fields` của app, NUL ở giữa tên, lời từ chối 4xx giữ câu cũ, tải và ghi đè thành công) và 5 ca `"\x00\x0bcontent"` mà code cũ đã chặn được vì tách ở `\x0b`.

```
$ uv run ruff check .
All checks passed!

$ uv run pytest --runxfail tests/test_soi_loi_t085.py tests/test_la_chan_t085.py   # trước khi gỡ dấu
748 passed in 27.86s
$ uv run pytest tests/test_soi_loi_t085.py tests/test_la_chan_t085.py              # trước khi gỡ dấu
40 failed, 708 passed in 27.51s      # đúng 40 XPASS(strict): 36 của Soi Lỗi, 4 của Lá Chắn

$ uv run pytest tests/test_wordpress_t088.py tests/test_soi_loi_t085.py tests/test_la_chan_t085.py
889 passed in 26.99s

# 54 file: mọi file trong tests/ có "WordPressClient", "upload_media", "fake_wp",
# "seo_app.wordpress", "wp_client", "_request(", "create_draft_with_images" hay "DraftImage"
# (không kể conftest.py), cộng test_app_pages.py, test_app_images.py, test_la_chan_t056.py,
# test_soi_loi_t056.py
$ uv run pytest tests/test_ai_images.py tests/test_ai_t034.py tests/test_app_images.py
    tests/test_app_pages.py tests/test_app_t044_safe_text.py tests/test_app_wordpress.py
    tests/test_drafts_images.py tests/test_images_folders_t063.py tests/test_la_chan_t039.py
    tests/test_la_chan_t056.py tests/test_la_chan_t060.py tests/test_la_chan_t071.py
    tests/test_la_chan_t076.py tests/test_la_chan_t085.py tests/test_onpage_links.py
    tests/test_phase2_fixes.py tests/test_safety.py tests/test_sanitize.py tests/test_shortcode_t061.py
    tests/test_site_index.py tests/test_site_index_t042.py tests/test_soi_loi_t019_luot2.py
    tests/test_soi_loi_t031.py tests/test_soi_loi_t034.py tests/test_soi_loi_t037.py
    tests/test_soi_loi_t039.py tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py
    tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t044.py tests/test_soi_loi_t054.py
    tests/test_soi_loi_t055.py tests/test_soi_loi_t056.py tests/test_soi_loi_t060.py
    tests/test_soi_loi_t061.py tests/test_soi_loi_t071.py tests/test_soi_loi_t075.py
    tests/test_soi_loi_t076.py tests/test_soi_loi_t081.py tests/test_soi_loi_t085.py
    tests/test_t040_prompts.py tests/test_t081_alt_gach_cheo.py tests/test_wordpress_client.py
    tests/test_wordpress_images.py tests/test_wordpress_paging_t042.py tests/test_wordpress_published.py
    tests/test_wordpress_round2_t042.py tests/test_wordpress_routes_t042.py
    tests/test_wordpress_seo_meta_t042.py tests/test_wordpress_shortcodes.py
    tests/test_wordpress_site_link_t042.py tests/test_wordpress_t060.py tests/test_wordpress_t085.py
    tests/test_wordpress_t088.py
6987 passed, 13 skipped, 15 xfailed in 990.11s (13:32:52–13:49:26)
# 15 xfail có sẵn, không thuộc T-088: LC-T039-2 (3), LC-T056-1 (2), SL-T056-8..11 (5),
# SL-T081-1 (5). 13 bỏ qua: test chỉ chạy trên Mac/Linux hoặc cần symlink (Windows)
```

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: NUL, khoảng trắng kiểu `trim()` sát tên trường bị chặn (`test_fields_co_nul_hay_khoang_trang_kieu_trim_sat_ten_truong_bi_chan` 85 ca, `test_thu_ngau_nhien_co_nul_khong_lot_truong_chay_shortcode`; 27 ca Soi Lỗi đã gỡ `xfail`)
- [x] Yêu cầu 2: không lọt `RecursionError`/lỗi giải mã lạ, câu cố định kèm mã HTTP; câu «thư viện Media» cả khi lỗi lạ (`test_tra_loi_json_long_qua_sau_thanh_cau_co_dinh`, `test_tra_loi_loi_co_than_json_long_qua_sau_thanh_cau_co_dinh` 9 ca, `test_loi_giai_ma_la_thanh_cau_co_dinh` 3 ca, `test_ghi_de_tra_loi_long_qua_sau_van_bao_anh_da_o_thu_vien`, `test_ghi_de_loi_la_van_bao_anh_da_o_thu_vien`; 3 ca Soi Lỗi + 4 ca Lá Chắn đã gỡ `xfail`, gồm trang Kết nối WordPress thật qua `AppTest`)
- [x] Yêu cầu 3: lệnh tải lỗi không phải 4xx rõ ràng thì dặn kiểm Media → Thư viện (`test_tai_anh_loi_khong_ro_rang_thi_dan_kiem_thu_vien` 15 ca, `test_tai_anh_loi_la_van_dan_kiem_thu_vien`); 4xx giữ câu cũ (`test_tai_anh_bi_tu_choi_4xx_giu_cau_cu` 8 ca, cùng ca đối chứng của Soi Lỗi); 6 ca Soi Lỗi đã gỡ `xfail`
- [x] Yêu cầu 4: không chặn oan (54 file qua, gồm «Gửi nháp» T-056 và trang Kết nối WordPress)
- [x] Yêu cầu 5: gỡ `xfail` khi XPASS (6 dòng dấu, 40 ca)
- [x] `uv run ruff check .` sạch; báo cáo này
- [x] Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`; không sửa `app/**`, `config/**` và file của T-041

## Rủi ro và điểm cần chú ý

- **Bắt mọi lỗi lúc giải mã JSON** (kể cả `MemoryError`): khối `try` chỉ có `response.json()`, nên không giấu lỗi của code khác; lỗi gốc vẫn nằm trong `__cause__` (`_json`), app không in ra.
- **Câu báo dài hơn** ở ca tải ảnh lỗi không rõ ràng (câu cũ + câu dặn kiểm Media). Lời từ chối 4xx giữ nguyên câu cũ (có test so đúng bằng).
- **Lỗi ở lệnh tải có thể là website trả lại ảnh đã có** (mã 200/202): câu báo nói «ảnh có thể đã lên», không khẳng định ảnh mới hay cũ; phần mềm không ghi gì vào ảnh đó (LC-T071-1 giữ nguyên).
- Nhận định về `trim()`, `wp_parse_list`, `get_fields_for_response` của WordPress, PHP lấy từ biên bản Lá Chắn và báo cáo Soi Lỗi T-085 (đã đọc mã `wordpress-develop` trunk 2026-10-26); tôi chưa thử trên site (không có staging). Chặn là an toàn dù nhận định sai.
- Ghi nhận 1 của Soi Lỗi T-085 (khóa truy vấn `id`, `name` chưa có lớp chặn phụ khi `ALLOWED_PARAMS` bị nới) không thuộc phiếu này; hôm nay `ALLOWED_PARAMS` không có hai khóa đó.

## Đề xuất

1. (Lá Chắn xét, từ Ghi nhận 1 Soi Lỗi T-085) Lớp chặn phụ cho khóa truy vấn `id`, `name` (so đúng tên, không so chuỗi con vì `hide_empty` chứa «id»).
2. (Còn từ T-085) Bắt buộc có `_fields` trên các đường bài, ảnh; `verify=True` tường minh trong `_request`; `html.escape` tiêu đề, chú thích trong `upload_media`.

## Câu hỏi cho chủ dự án

Không có.

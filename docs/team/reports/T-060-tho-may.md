# Báo cáo T-060 · Dọn lỗi Thấp của client WordPress

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-060](../tickets/T-060-don-loi-thap-client-wordpress.md) |
| Nhánh | `team/T-060` (từ `main` `cf8d824`) |
| Ngày nộp | 2026-10-23 |
| Kết quả | **Hoàn thành**: đủ 8 việc. Riêng 4 test cũ phải sửa theo LC-T061-3 (ngoài phạm vi phiếu cho sửa): đã hỏi, **Chỉ Huy B duyệt 2026-10-23**, commit riêng (bảng trước/sau ở mục «Sửa 4 test cũ theo LC-T061-3») |

## Tóm tắt (cho chủ dự án)

- Phần mềm chỉ gửi lên website đúng những tham số đã duyệt cho từng loại lệnh. Tham số hay dòng đầu lệnh có thể «đổi đường» (gọi sang chỗ nhạy cảm như Code Snippets) hoặc «đổi kiểu lệnh» (biến lệnh sửa thành lệnh xóa) đều bị chặn trước khi gửi. Hôm nay chưa có cách nào đưa được các tham số đó vào, đây là chốt chặn cho các phiếu sau.
- Câu báo lỗi WordPress không còn chép chữ do website trả về, cũng không chép lại địa chỉ website ghi trong `.env`: chỉ còn câu tiếng Việt cố định kèm mã lỗi, ví dụ «Tài khoản WordPress không đủ quyền… (mã 403)». Bạn sẽ thấy câu lỗi ngắn hơn, không còn đoạn «(WordPress: …)».
- Địa chỉ website trong `.env` mà trỏ vào một file chạy được trên máy chủ (`.php`, `.cgi`, `.asp`, `.jsp`…) bị từ chối ngay khi mở app.
- Tiêu đề, mô tả SEO có dấu «<» dính liền chữ (ví dụ «Giá <500k») bị chặn kèm hướng dẫn thêm dấu cách, vì website có thể bỏ cả cụm «<…>» rồi làm lộ ra lệnh shortcode.
- Trang Kết nối WordPress, khi tải ảnh đại diện: chỉ ghi alt nếu website xác nhận vừa tạo ảnh **mới** (không bao giờ ghi đè lên ảnh có sẵn), và luôn ghi đè cả 3 ô alt, tiêu đề, chú thích, để chữ giấu sẵn trong file ảnh (ảnh tải từ mạng) không tự lên website. Ô alt để trống thì ảnh trên website cũng không có alt; tiêu đề ảnh là tên file đã bỏ dấu.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `ALLOWED_PARAMS` + `_is_plain_request`: tham số, header, thân lệnh theo danh sách của từng đường (LC-T042-1); câu lỗi cố định kèm mã HTTP (LC-T042-4); `WORDPRESS_URL` không có dấu «.» trong thư mục (LC-T042-5); `_seo_text` chặn «<» liền ký tự (LC-T061-2); `upload_media` chỉ nhận mã 201 (LC-T071-1) và luôn ghi đè 3 ô (LC-T061-3) |
| `tests/test_wordpress_t060.py` | Mới: 212 ca cho cả 6 lỗi trên (kể cả ca đối chứng) |
| `tests/test_soi_loi_t061.py` | Gỡ 6 `xfail`: 4 SL-T061-1, 2 SL-T061-2 (chỉ xóa dấu) |
| `tests/test_la_chan_t071.py` | Gỡ 2 `xfail` LC-T071-1 (chỉ xóa dấu); ca đối chứng giữ nguyên |
| `tests/test_soi_loi_t042.py` | LC-T061-5: dòng 423-424 cũ so cả phần đường **và** truy vấn; thêm `import` `parse_qs`, `urlsplit` |
| `tests/test_wordpress_client.py` | Chuỗi mong đợi câu lỗi 401, 403: có «(mã 401)», «(mã 403)», **không** còn lời máy chủ. 3 test ảnh sửa theo LC-T061-3 (Chỉ Huy duyệt, bảng dưới) |
| `tests/test_soi_loi_t044.py` | Chuỗi mong đợi câu lỗi 400: đúng bằng «WordPress báo lỗi (mã 400).», không còn chữ máy chủ. 1 test sửa theo LC-T061-3 (Chỉ Huy duyệt, bảng dưới) |
| `tests/test_app_t044_safe_text.py` | Câu lỗi `WORDPRESS_URL` sai: **không** còn chép địa chỉ (trước đòi phải chép) |

Không sửa `app/**`, `config/**`. Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `DraftImage`, `create_draft_with_images`, `DraftImagesError` (T-056 dùng lại); có test chốt mẫu `_SHORTCODE_OPEN` (`test_mau_shortcode_dung_chung_voi_t056_khong_doi`).

## Cách sửa từng mục

1. **LC-T042-1 (tham số, header).** `_request` (`client.py:1348`) gọi `is_allowed_route` như cũ rồi `_is_plain_request` (`client.py:144`), sai là ném câu cố định `_ROUTE_BLOCKED`, **chưa gửi gì**. Chọn cả hai cách của phiếu:
   - **Danh sách cho phép theo từng đường** `ALLOWED_PARAMS` (`client.py:95`), khóa là đúng cặp trong `ALLOWED_ROUTES` (thiếu đường nào là lỗi ngay khi nạp module, có test so hai danh sách). Ví dụ `POST /wp/v2/posts` chỉ nhận `_fields`; `GET /` không nhận tham số nào. Giá trị chỉ là chữ hoặc số nguyên.
   - **Danh sách cấm tối thiểu** `_FORBIDDEN_PARAMS` (`client.py:116`): `rest_route`, `_method`, `_envelope`, `_jsonp`, so trên tên đã gập (chữ thường, ký tự lạ thành «_», vì PHP đổi «.» và dấu cách trong tên tham số thành «_»), phòng khi ai đó nới danh sách cho phép.
   - **Header:** lệnh chỉ được có `Content-Type` (đúng loại ảnh trong `IMAGE_TYPES`) và `Content-Disposition`; không header nào, kể cả header gắn sẵn trong `session`, có chữ «method» (`X-HTTP-Method-Override`, `X-Method-Override`, `X-HTTP-Method`, viết hoa, gạch dưới).
   - **Thêm (cùng mục đích):** chỉ nhận tùy chọn `params`, `json` (`dict`), `data` (`bytes`), `headers`. Lý do: WordPress đọc `rest_route` cả trong thân lệnh dạng form (`$_POST`, qua `WP::parse_request`), nên `files=`, `data=dict`, `Content-Type: application/x-www-form-urlencoded` hay `multipart/form-data` cũng đổi được đường; `verify=`, `auth=`, `cookies=`… cũng bị từ chối. `session.params` khác rỗng, `session` có `Content-Type` riêng: từ chối.
2. **LC-T042-4 (câu lỗi).** `_error_from` (`client.py:1405`) bỏ hẳn phần «(WordPress: …)»; mọi câu theo mã HTTP đều có «(mã N)» (401, 403, 404, 413, 5xx, còn lại). `code` WordPress chỉ giữ trong `WordPressError.code` khi đúng dạng `[A-Za-z0-9_-]{1,100}` (`_ERROR_CODE`, `client.py:57`), để code phân biệt lỗi (`rest_no_route`, `rest_post_invalid_page_number`), không hiện lên màn hình. Không còn câu nào chép `WORDPRESS_URL`: câu khởi tạo sai dạng (`client.py:595`), câu «Không kết nối được» (`client.py:1373`), câu «Không tìm thấy REST API» (404). Câu chuyển hướng thêm «(mã 3xx)». Câu báo file ảnh sai đuôi / rỗng vẫn chép **tên file người dùng tự chọn** (không phải lời máy chủ hay `WORDPRESS_URL`; test T-044 chứng minh hiện ra không thành link) để giữ nguyên hành vi đã được duyệt.
3. **LC-T042-5 (file chạy được).** Theo đúng gợi ý Lá Chắn T-042: `_SITE_PATH` (`client.py:1634`) không nhận dấu «.» trong bất kỳ đoạn thư mục nào, nên mọi đuôi file đều bị chặn (`.php`, `.pht`, `.phtml`, `.cgi`, `.shtml`, `.asp`, `.aspx`, `.jsp`, `.py`, `.pl`, `.php5`…), kể cả đuôi chưa ai nghĩ tới. `index.php` **vẫn bị chặn** như T-042 (Thợ Máy T-042 đã chốt «không chừa `index.php`», có test cũ `tests/test_wordpress_round2_t042.py:462` đòi chặn); tôi hiểu «trừ `index.php` như T-042» trong phiếu là nói theo cách T-042, vì cho qua `index.php` là nới một test cũ.
4. **LC-T061-2 (`_seo_text`).** Thêm `_TAG_LIKE_OPEN = <(?![ \t\n\r\v\f])` (`client.py:227`): «<» mà ký tự ngay sau không phải khoảng trắng ASCII **hoặc «<» ở cuối chữ** là bị chặn (`client.py:1573`), xét cả 3 dạng chữ (gốc, đã chuẩn hóa, NFKC), nên «＜», «﹤» toàn khổ, «<» + U+00A0 / U+3000 / ký tự vô hình đều bị bắt. Kiểm này đặt **sau** các kiểm cũ nên câu báo của các ca cũ không đổi. Gỡ 4 `xfail` SL-T061-1: cả 4 qua.
5. **LC-T061-3 (`upload_media` luôn ghi đè 3 ô).** Sau lệnh tải, `upload_media` (`client.py:1013`) **luôn** gửi `POST /wp/v2/media/<mã>` với đủ `alt_text`, `title`, `caption` (`client.py:1054`, đã `escape_shortcodes`): ô trống (hay `None`) gửi chuỗi rỗng, tiêu đề trống lấy tên file đã làm sạch (giống WordPress tự đặt, ví dụ `anh-cua-sat`). Ba ô được kiểm là chữ **trước** khi tải (`client.py:1041-1046`): sai kiểu thì báo lỗi, chưa gửi gì, để không có cảnh ảnh đã lên mà bước ghi đè lại vỡ giữa chừng (chữ trong file ở lại website). Chọn cách này thay cho «trang Kết nối WordPress đi qua `make_web_image`» vì cách kia phải sửa `app/**` (ngoài phạm vi). Gỡ 2 `xfail` SL-T061-2: cả 2 qua.
6. **LC-T061-5.** `tests/test_soi_loi_t042.py:424-427` (dòng 423-424 cũ): so `urlsplit(url).path == "/wp-json/wp/v2/posts"` **và** `parse_qs(query) == {"_fields": ["id,status,title,link,featured_media"]}` (giá trị viết thẳng, chặt hơn import hằng: ai thêm `content` vào `_POST_FIELDS` là test hỏng).
7. **LC-T071-1.** `upload_media` gọi `self._post_media(data, safe_name, content_type, new_only=True)` (`client.py:1048`): mã khác 201 thì dừng trước khi đọc câu trả lời, không có lệnh ghi alt. Gỡ 2 `xfail` trong `tests/test_la_chan_t071.py`; ca đối chứng (201 vẫn tải và ghi alt) giữ nguyên, vẫn qua.
8. **Gỡ `xfail`:** chỉ xóa dòng dấu, không đổi thân test (8 dấu: 4 SL-T061-1, 2 SL-T061-2, 2 LC-T071-1).

## Sửa 4 test cũ theo LC-T061-3 (Chỉ Huy B duyệt 2026-10-23)

Lý do chung: 4 test này ghi lại đúng cách làm cũ mà phiếu bảo đổi («ô trống thì không gửi lệnh ghi»). Không xóa `assert` nào; mọi `assert` cũ khác giữ nguyên chữ. «Dòng cũ» theo `main` `cf8d824`, «dòng mới» theo nhánh này.

| File · test | Dòng cũ (`main`) | Dòng mới | Lý do |
|---|---|---|---|
| `tests/test_wordpress_client.py` · `test_upload_media_with_alt` | 298: `assert body(update) == {"alt_text": "Cửa sắt sơn đen"}` | 300-301: chú thích + `assert body(update) == {"alt_text": "Cửa sắt sơn đen", "title": "anh-cua-sat", "caption": ""}` | Lệnh ghi nay luôn có đủ 3 ô; vẫn so **đúng bằng** cả thân lệnh (chặt như cũ, thêm 2 ô) |
| `tests/test_wordpress_client.py` · `test_upload_media_without_metadata_is_one_request` → `test_upload_media_without_metadata_still_overwrites_fields` | 303: tên cũ; 306: `assert len(fake_wp.requests) == 1` | 306: tên mới; 308: thêm đường `POST /wp-json/wp/v2/media/5` vào site giả; 310-311: chú thích + `assert len(fake_wp.requests) == 2`; 314: thêm `assert body(fake_wp.requests[1]) == {"alt_text": "", "title": "anh", "caption": ""}` | Không có alt cũng phải ghi đè (ô trống); vẫn đòi **đúng** số lệnh (2), và thêm kiểm thân lệnh 2. `Content-Type`, tên file `anh.webp`, `media.id == 5` giữ nguyên |
| `tests/test_wordpress_client.py` · `test_upload_media_file` | 315 (sau dòng này chưa có đường ghi) | 322: thêm `fake_wp.on("POST", "/wp-json/wp/v2/media/6", {"id": 6, "source_url": "u"})` | Site giả thiếu đường của lệnh ghi đè (trả 404); 2 `assert` cũ (thân lệnh tải, tên file `cong-inox.png`) giữ nguyên |
| `tests/test_soi_loi_t044.py` · `test_null_source_url_does_not_crash_page` | 317 (sau dòng này chưa có đường ghi) | 320: thêm `fake_wp.on("POST", "/wp-json/wp/v2/media/9", media)` (vẫn `source_url: None`) | Như trên; câu trả lời lệnh ghi vẫn có `source_url` `None`, nên test vẫn kiểm đúng điều cũ: trang không vỡ (`not at.exception`) và có đúng 1 thông báo thành công |

## Bằng chứng

Bộ test mới chạy trên **code cũ** (`seo_app` của `cf8d824` giải nén vào thư mục nháp, nạp qua `PYTHONPATH`; bản tạm của file test, đã xóa): **189 hỏng, 23 qua** (212 ca). 23 ca qua là ca đối chứng (tham số đúng danh sách vẫn gửi, thư mục thường vẫn nhận, chữ SEO có «< » vẫn qua, ảnh có đủ 3 ô không còn «[» trần) hoặc việc code cũ đã làm (`.php`, `.phtml`, câu báo `http://`).

Lượt cuối (code cuối của nhánh):

```
$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_wordpress_t060.py tests/test_wordpress_client.py tests/test_wordpress_images.py
    tests/test_soi_loi_t042.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py
    tests/test_la_chan_t071.py tests/test_soi_loi_t071.py tests/test_soi_loi_t054.py
    tests/test_wordpress_round2_t042.py tests/test_wordpress_routes_t042.py
    tests/test_wordpress_seo_meta_t042.py tests/test_soi_loi_t042_round2.py
    tests/test_wordpress_published.py tests/test_soi_loi_t044.py tests/test_app_t044_safe_text.py
    tests/test_app_wordpress.py tests/test_app_pages.py tests/test_t081_alt_gach_cheo.py
    tests/test_soi_loi_t081.py
2350 passed, 5 xfailed in 85.14s (18:09:30–18:10:58)
# 5 xfail có sẵn, không thuộc T-060: SL-T081-1

$ uv run pytest tests/test_la_chan_t039.py tests/test_sanitize.py tests/test_site_index_t042.py
    tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t081.py
    tests/test_wordpress_paging_t042.py tests/test_wordpress_site_link_t042.py
347 passed, 8 xfailed in 35.80s (18:05:33–18:06:11)
# 8 xfail có sẵn, không thuộc T-060: LC-T039-2 (3), SL-T081-1 (5)
```

Lượt chạy phần 1 (commit `9f3b7e2`). Phần 2 chỉ sửa `upload_media`; trong các file dưới đây chỉ `test_app_wordpress.py`, `test_t081_alt_gach_cheo.py` chạm tới tải ảnh (`grep -l "upload_media\|wp/v2/media" tests/`), và cả 2 (cùng `test_app_pages.py`) đã chạy lại ở lượt cuối bên trên:

```
$ uv run pytest tests/test_app_pages.py tests/test_app_wordpress.py tests/test_onpage_links.py
    tests/test_phase2_fixes.py tests/test_safety.py tests/test_site_index.py tests/test_soi_loi_t031.py
    tests/test_soi_loi_t037.py tests/test_soi_loi_t039.py tests/test_soi_loi_t049.py
    tests/test_soi_loi_t050.py tests/test_soi_loi_t075.py tests/test_t081_alt_gach_cheo.py
    tests/test_ai_images.py tests/test_ai_openai_gemini.py tests/test_ai_openai_gemini_soi_loi.py
    tests/test_ai_t026.py tests/test_ai_t028.py tests/test_ai_t034.py tests/test_soi_loi_t019_luot2.py
    tests/test_soi_loi_t026.py tests/test_soi_loi_t034.py
1 failed, 3411 passed, 1 skipped, 2 xfailed in 426.45s (17:49:39–17:57:02)
# 1 hỏng: test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted
# (khóa SQLite ở luồng khác, chờ 10 giây; không dùng phần đã sửa). Chạy riêng lại:
$ uv run pytest "tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted"
1 passed in 11.99s
$ uv run pytest tests/test_soi_loi_t037.py
139 passed in 34.54s
# 2 xfail có sẵn, không thuộc T-060: SL-T026-3; 1 bỏ qua: symlink (Windows chưa bật Developer Mode)
```

Các lượt trên phủ đủ 35 file của `grep -l "WordPressClient\|upload_media\|_request" tests/` (không kể `conftest.py`), mọi file dùng `wp_client`, `fake_wp` hay `seo_app.wordpress`, thêm `tests/test_app_pages.py` và file mới `tests/test_wordpress_t060.py`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `_request` từ chối `rest_route`, `_method`, `_envelope`, `_jsonp`, `X-HTTP-Method-Override`, có test (`test_tham_so_doi_duong_hay_phuong_thuc_bi_chan_truoc_khi_gui`, `test_header_doi_phuong_thuc_bi_chan_ca_trong_lenh_lan_trong_session`, `test_tuy_chon_la_cua_lenh_bi_chan_truoc_khi_gui`, `test_tham_so_cua_duong_khac_bi_chan`)
- [x] Yêu cầu 2: câu lỗi cố định kèm mã HTTP, không chép lời máy chủ, không chép `WORDPRESS_URL` (`test_cau_loi_co_ma_http_khong_chep_loi_may_chu_hay_dia_chi`, `test_ham_cong_khai_khong_chep_loi_may_chu`, `test_loi_mang_va_chuyen_huong_khong_chep_dia_chi`, `test_cau_loi_khoi_tao_khong_chep_wordpress_url`)
- [x] Yêu cầu 3: `WORDPRESS_URL` có đoạn là file bị từ chối (`test_wordpress_url_co_doan_la_file_bi_tu_choi`, 15 ca)
- [x] LC-T061-2: 4 `xfail` SL-T061-1 đã gỡ, qua; thêm 12 ca chặn, 4 ca đối chứng
- [x] LC-T061-3: 2 `xfail` SL-T061-2 đã gỡ, qua; thêm `test_upload_media_luon_ghi_de_ca_ba_o_ke_ca_khi_trong`, `test_upload_media_o_co_chu_giu_nguyen_o_trong_van_ghi_de`, `test_upload_media_o_none_coi_nhu_trong_van_ghi_de`, `test_upload_media_o_khong_phai_chu_bi_chan_truoc_khi_tai`; 4 test cũ sửa theo duyệt của Chỉ Huy
- [x] LC-T061-5: `tests/test_soi_loi_t042.py:424-427` (dòng 423-424 cũ)
- [x] LC-T071-1: 2 `xfail` đã gỡ, qua; ca đối chứng qua; thêm 8 mã 2xx khác 201
- [x] Gỡ `xfail` khi XPASS: chỉ xóa dấu (8 dấu)
- [x] Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, chữ ký `DraftImage`, `create_draft_with_images`, `DraftImagesError`

## Rủi ro và điểm cần chú ý

- **Danh sách tham số chặt:** phiếu sau muốn gửi tham số mới (kể cả trên đường cũ) phải thêm vào `ALLOWED_PARAMS` và qua Lá Chắn; nếu quên, lệnh bị chặn với câu «không có trong danh sách được phép» (an toàn, dễ thấy khi test).
- **Giá trị tham số chưa bị kiểm theo danh sách** (chỉ kiểm kiểu): ví dụ `_fields` vẫn nhận mọi chữ. Hôm nay mọi giá trị là hằng do code viết. Xem Đề xuất 1.
- **`WORDPRESS_URL` có thư mục chứa dấu chấm** (kiểu `https://site.vn/blog.v2`) nay bị từ chối. Website thật cài ở gốc nên không ảnh hưởng; ai cài WordPress trong thư mục có dấu chấm phải đổi tên thư mục.
- **Câu lỗi ít chi tiết hơn:** khi lỗi lạ (400, 409…), người dùng chỉ thấy mã HTTP. Lý do lỗi thật vẫn xem được trong trang quản trị WordPress; `WordPressError.code` còn giữ mã ASCII cho code dùng.
- **Trang Kết nối WordPress, ảnh không có alt:** nay luôn có thêm lệnh ghi thứ 2. Nếu lệnh ghi đó lỗi (mạng, quyền), ảnh đã lên thư viện Media và bài nháp không được tạo, giống hệt trường hợp có alt từ trước tới nay. Tiêu đề ảnh là tên file đã bỏ dấu (`anh-cua-sat`) thay vì chữ WordPress tự đọc trong file.
- Nhận định «WordPress đọc `rest_route` trong thân form» dựa trên mã WordPress lõi (`WP::parse_request` đọc `$_POST` trước `$_GET` cho biến truy vấn công khai); nhận định WordPress lấy tiêu đề, chú thích, alt từ file khi lệnh không có (`insert_attachment`) lấy từ Lá Chắn T-061. Tôi chưa thử trên site (không có staging); hai cách chặn đều an toàn dù nhận định sai.

## Đề xuất

1. (Lá Chắn xét) Kiểm thêm **giá trị** của `_fields` theo danh sách hằng (`_POST_FIELDS`, `_POST_META_FIELDS`, `_MEDIA_FIELDS`, `_PUBLISHED_FIELDS`, trường chuyên mục): chốt luôn điều kiện «không hỏi `content`, `description`» của T-061 bằng code thay vì quy ước.
2. (Ngoài phiếu, W4) `_request` có thể truyền `verify=True` tường minh để `session` được truyền vào (nếu có) không tắt được kiểm chứng chỉ SSL. Hôm nay chỉ test truyền `session`.

## Câu hỏi cho chủ dự án

Không có. (Câu hỏi về 4 test cũ đã được Chỉ Huy B trả lời: đồng ý, 2026-10-23.)

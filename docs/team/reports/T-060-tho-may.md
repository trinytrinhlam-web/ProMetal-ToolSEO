# Báo cáo T-060 · Dọn lỗi Thấp của client WordPress

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-060](../tickets/T-060-don-loi-thap-client-wordpress.md) |
| Nhánh | `team/T-060` (từ `main` `cf8d824`) |
| Ngày nộp | 2026-10-23 |
| Kết quả | **Hoàn thành một phần**: 7/8 việc xong và đã push. Việc 5 (LC-T061-3) đã viết, chạy thử xong, **chờ Chỉ Huy cho sửa 4 test cũ** (ngoài phạm vi phiếu cho sửa), xem mục «Câu hỏi cho Chỉ Huy» |

## Tóm tắt (cho chủ dự án)

- Phần mềm chỉ gửi lên website đúng những tham số đã duyệt cho từng loại lệnh. Tham số hay dòng đầu lệnh có thể «đổi đường» (gọi sang chỗ nhạy cảm như Code Snippets) hoặc «đổi kiểu lệnh» (biến lệnh sửa thành lệnh xóa) đều bị chặn trước khi gửi. Hôm nay chưa có cách nào đưa được các tham số đó vào, đây là chốt chặn cho các phiếu sau.
- Câu báo lỗi WordPress không còn chép chữ do website trả về, cũng không chép lại địa chỉ website ghi trong `.env`: chỉ còn câu tiếng Việt cố định kèm mã lỗi, ví dụ «Tài khoản WordPress không đủ quyền… (mã 403)». Bạn sẽ thấy câu lỗi ngắn hơn, không còn đoạn «(WordPress: …)».
- Địa chỉ website trong `.env` mà trỏ vào một file chạy được trên máy chủ (`.php`, `.cgi`, `.asp`, `.jsp`…) bị từ chối ngay khi mở app.
- Tiêu đề, mô tả SEO có dấu «<» dính liền chữ (ví dụ «Giá <500k») bị chặn kèm hướng dẫn thêm dấu cách, vì website có thể bỏ cả cụm «<…>» rồi làm lộ ra lệnh shortcode.
- Trang Kết nối WordPress: khi tải ảnh, phần mềm chỉ ghi alt nếu website xác nhận vừa tạo ảnh **mới**; không bao giờ ghi đè alt lên ảnh có sẵn.
- Còn chờ: trang Kết nối WordPress luôn ghi đè cả 3 ô alt, tiêu đề, chú thích của ảnh vừa tải (để chữ giấu trong file ảnh không lọt lên website). Code đã viết, cần Chỉ Huy đồng ý sửa 4 test cũ đang ghi lại cách làm cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `ALLOWED_PARAMS` + `_is_plain_request`: tham số, header, thân lệnh theo danh sách của từng đường (LC-T042-1); câu lỗi cố định kèm mã HTTP (LC-T042-4); `WORDPRESS_URL` không có dấu «.» trong thư mục (LC-T042-5); `_seo_text` chặn «<» liền ký tự (LC-T061-2); `upload_media` chỉ nhận mã 201 (LC-T071-1) |
| `tests/test_wordpress_t060.py` | Mới: 195 ca cho cả 5 lỗi trên (kể cả ca đối chứng) |
| `tests/test_soi_loi_t061.py` | Gỡ 4 `xfail` SL-T061-1 (chỉ xóa dấu). 2 `xfail` SL-T061-2 **giữ** tới khi xong việc 5 |
| `tests/test_la_chan_t071.py` | Gỡ 2 `xfail` LC-T071-1 (chỉ xóa dấu); ca đối chứng giữ nguyên |
| `tests/test_soi_loi_t042.py` | LC-T061-5: dòng 423-424 so cả phần đường **và** truy vấn; thêm `import` `parse_qs`, `urlsplit` |
| `tests/test_wordpress_client.py` | Chuỗi mong đợi câu lỗi 401, 403: có «(mã 401)», «(mã 403)», **không** còn lời máy chủ |
| `tests/test_soi_loi_t044.py` | Chuỗi mong đợi câu lỗi 400: đúng bằng «WordPress báo lỗi (mã 400).», không còn chữ máy chủ |
| `tests/test_app_t044_safe_text.py` | Câu lỗi `WORDPRESS_URL` sai: **không** còn chép địa chỉ (trước đòi phải chép) |

Không sửa `app/**`, `config/**`. Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `DraftImage`, `create_draft_with_images`, `DraftImagesError` (T-056 dùng lại); có test chốt mẫu `_SHORTCODE_OPEN` (`test_mau_shortcode_dung_chung_voi_t056_khong_doi`).

## Cách sửa từng mục

1. **LC-T042-1 (tham số, header).** `_request` (`client.py:1345`) gọi `is_allowed_route` như cũ rồi `_is_plain_request` (`client.py:144`), sai là ném câu cố định `_ROUTE_BLOCKED`, **chưa gửi gì**. Chọn cả hai cách của phiếu:
   - **Danh sách cho phép theo từng đường** `ALLOWED_PARAMS` (`client.py:95`), khóa là đúng cặp trong `ALLOWED_ROUTES` (thiếu đường nào là lỗi ngay khi nạp module, có test so hai danh sách). Ví dụ `POST /wp/v2/posts` chỉ nhận `_fields`; `GET /` không nhận tham số nào. Giá trị chỉ là chữ hoặc số nguyên.
   - **Danh sách cấm tối thiểu** `_FORBIDDEN_PARAMS` (`client.py:116`): `rest_route`, `_method`, `_envelope`, `_jsonp`, so trên tên đã gập (chữ thường, ký tự lạ thành «_», vì PHP đổi «.» và dấu cách trong tên tham số thành «_»), phòng khi ai đó nới danh sách cho phép.
   - **Header:** lệnh chỉ được có `Content-Type` (đúng loại ảnh trong `IMAGE_TYPES`) và `Content-Disposition`; không header nào, kể cả header gắn sẵn trong `session`, có chữ «method» (`X-HTTP-Method-Override`, `X-Method-Override`, `X-HTTP-Method`, viết hoa, gạch dưới).
   - **Thêm (cùng mục đích):** chỉ nhận tùy chọn `params`, `json` (`dict`), `data` (`bytes`), `headers`. Lý do: WordPress đọc `rest_route` cả trong thân lệnh dạng form (`$_POST`, qua `WP::parse_request`), nên `files=`, `data=dict`, `Content-Type: application/x-www-form-urlencoded` hay `multipart/form-data` cũng đổi được đường; `verify=`, `auth=`, `cookies=`… cũng bị từ chối. `session.params` khác rỗng, `session` có `Content-Type` riêng: từ chối.
2. **LC-T042-4 (câu lỗi).** `_error_from` (`client.py:1402`) bỏ hẳn phần «(WordPress: …)»; mọi câu theo mã HTTP đều có «(mã N)» (401, 403, 404, 413, 5xx, còn lại). `code` WordPress chỉ giữ trong `WordPressError.code` khi đúng dạng `[A-Za-z0-9_-]{1,100}` (`_ERROR_CODE`, `client.py:57`), để code phân biệt lỗi (`rest_no_route`, `rest_post_invalid_page_number`), không hiện lên màn hình. Không còn câu nào chép `WORDPRESS_URL`: câu khởi tạo sai dạng (`client.py:595`), câu «Không kết nối được» (`client.py:1370`), câu «Không tìm thấy REST API» (404). Câu chuyển hướng thêm «(mã 3xx)». Câu báo file ảnh sai đuôi / rỗng vẫn chép **tên file người dùng tự chọn** (không phải lời máy chủ hay `WORDPRESS_URL`; test T-044 chứng minh hiện ra không thành link) để giữ nguyên hành vi đã được duyệt.
3. **LC-T042-5 (file chạy được).** Theo đúng gợi ý Lá Chắn T-042: `_SITE_PATH` (`client.py:1631`) không nhận dấu «.» trong bất kỳ đoạn thư mục nào, nên mọi đuôi file đều bị chặn (`.php`, `.pht`, `.phtml`, `.cgi`, `.shtml`, `.asp`, `.aspx`, `.jsp`, `.py`, `.pl`, `.php5`…), kể cả đuôi chưa ai nghĩ tới. `index.php` **vẫn bị chặn** như T-042 (Thợ Máy T-042 đã chốt «không chừa `index.php`», có test cũ `tests/test_wordpress_round2_t042.py:462` đòi chặn); tôi hiểu «trừ `index.php` như T-042» trong phiếu là nói theo cách T-042, vì cho qua `index.php` là nới một test cũ.
4. **LC-T061-2 (`_seo_text`).** Thêm `_TAG_LIKE_OPEN = <(?![ \t\n\r\v\f])` (`client.py:227`): «<» mà ký tự ngay sau không phải khoảng trắng ASCII **hoặc «<» ở cuối chữ** là bị chặn (`client.py:1570`), xét cả 3 dạng chữ (gốc, đã chuẩn hóa, NFKC), nên «＜», «﹤» toàn khổ, «<» + U+00A0 / U+3000 / ký tự vô hình đều bị bắt. Kiểm này đặt **sau** các kiểm cũ nên câu báo của các ca cũ không đổi. Gỡ 4 `xfail` SL-T061-1: cả 4 qua.
5. **LC-T061-3 (`upload_media` luôn ghi đè 3 ô).** Đã viết và chạy thử (gỡ được 2 `xfail` SL-T061-2), **chưa commit**: làm 4 test cũ hỏng (xem «Câu hỏi cho Chỉ Huy»).
6. **LC-T061-5.** `tests/test_soi_loi_t042.py:424-427` (dòng 423-424 cũ): so `urlsplit(url).path == "/wp-json/wp/v2/posts"` **và** `parse_qs(query) == {"_fields": ["id,status,title,link,featured_media"]}` (giá trị viết thẳng, chặt hơn import hằng: ai thêm `content` vào `_POST_FIELDS` là test hỏng).
7. **LC-T071-1.** `upload_media` gọi `self._post_media(data, safe_name, content_type, new_only=True)` (`client.py:1039`): mã khác 201 thì dừng trước khi đọc câu trả lời, không có lệnh ghi alt. Gỡ 2 `xfail` trong `tests/test_la_chan_t071.py`; ca đối chứng (201 vẫn tải và ghi alt) giữ nguyên, vẫn qua.
8. **Gỡ `xfail`:** chỉ xóa dòng dấu, không đổi thân test (6 dấu: 4 SL-T061-1, 2 LC-T071-1).

## Bằng chứng

Bộ test mới chạy trên **code cũ** (`seo_app` của `cf8d824` giải nén vào thư mục nháp, nạp qua `PYTHONPATH`; bản tạm của file test, đã xóa): **172 hỏng, 23 qua** (195 ca). 23 ca qua là ca đối chứng (tham số đúng danh sách vẫn gửi, thư mục thường vẫn nhận, chữ SEO có «< » vẫn qua) hoặc việc code cũ đã làm (`.php`, `.phtml`, câu báo `http://`).

```
$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_wordpress_t060.py tests/test_wordpress_client.py tests/test_wordpress_images.py
    tests/test_soi_loi_t042.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py
    tests/test_la_chan_t071.py tests/test_soi_loi_t071.py tests/test_soi_loi_t054.py
    tests/test_wordpress_round2_t042.py tests/test_wordpress_routes_t042.py
    tests/test_wordpress_seo_meta_t042.py tests/test_soi_loi_t042_round2.py
    tests/test_wordpress_published.py tests/test_soi_loi_t044.py tests/test_app_t044_safe_text.py
2140 passed, 2 xfailed in 244.07s (17:44:57–17:49:21)   # 2 xfail: SL-T061-2, chờ việc 5

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
# 2 xfail của lượt này là xfail có sẵn của các file khác, không thuộc T-060; 1 bỏ qua: symlink
```

Hai lượt trên phủ đủ 35 file của `grep -l "WordPressClient\|upload_media\|_request" tests/` (không kể `conftest.py`), thêm `tests/test_app_pages.py`, `tests/test_t081_alt_gach_cheo.py` và file mới `tests/test_wordpress_t060.py`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `_request` từ chối `rest_route`, `_method`, `_envelope`, `_jsonp`, `X-HTTP-Method-Override`, có test (`test_tham_so_doi_duong_hay_phuong_thuc_bi_chan_truoc_khi_gui`, `test_header_doi_phuong_thuc_bi_chan_ca_trong_lenh_lan_trong_session`, `test_tuy_chon_la_cua_lenh_bi_chan_truoc_khi_gui`, `test_tham_so_cua_duong_khac_bi_chan`)
- [x] Yêu cầu 2: câu lỗi cố định kèm mã HTTP, không chép lời máy chủ, không chép `WORDPRESS_URL` (`test_cau_loi_co_ma_http_khong_chep_loi_may_chu_hay_dia_chi`, `test_ham_cong_khai_khong_chep_loi_may_chu`, `test_loi_mang_va_chuyen_huong_khong_chep_dia_chi`, `test_cau_loi_khoi_tao_khong_chep_wordpress_url`)
- [x] Yêu cầu 3: `WORDPRESS_URL` có đoạn là file bị từ chối (`test_wordpress_url_co_doan_la_file_bi_tu_choi`, 15 ca)
- [x] LC-T061-2: 4 `xfail` SL-T061-1 đã gỡ, qua; thêm 12 ca chặn, 4 ca đối chứng
- [ ] LC-T061-3: code xong, chờ Chỉ Huy cho sửa 4 test cũ; 2 `xfail` SL-T061-2 còn giữ
- [x] LC-T061-5: `tests/test_soi_loi_t042.py:424-427` (dòng 423-424 cũ)
- [x] LC-T071-1: 2 `xfail` đã gỡ, qua; ca đối chứng qua; thêm 8 mã 2xx khác 201
- [x] Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, chữ ký `DraftImage`, `create_draft_with_images`, `DraftImagesError`

## Rủi ro và điểm cần chú ý

- **Danh sách tham số chặt:** phiếu sau muốn gửi tham số mới (kể cả trên đường cũ) phải thêm vào `ALLOWED_PARAMS` và qua Lá Chắn; nếu quên, lệnh bị chặn với câu «không có trong danh sách được phép» (an toàn, dễ thấy khi test).
- **Giá trị tham số chưa bị kiểm theo danh sách** (chỉ kiểm kiểu): ví dụ `_fields` vẫn nhận mọi chữ. Hôm nay mọi giá trị là hằng do code viết. Xem Đề xuất 1.
- **`WORDPRESS_URL` có thư mục chứa dấu chấm** (kiểu `https://site.vn/blog.v2`) nay bị từ chối. Website thật cài ở gốc nên không ảnh hưởng; ai cài WordPress trong thư mục có dấu chấm phải đổi tên thư mục.
- **Câu lỗi ít chi tiết hơn:** khi lỗi lạ (400, 409…), người dùng chỉ thấy mã HTTP. Lý do lỗi thật vẫn xem được trong trang quản trị WordPress; `WordPressError.code` còn giữ mã ASCII cho code dùng.
- Nhận định «WordPress đọc `rest_route` trong thân form» dựa trên mã WordPress lõi (`WP::parse_request` đọc `$_POST` trước `$_GET` cho biến truy vấn công khai), tôi chưa thử trên site (không có staging); chặn là an toàn dù nhận định sai.

## Đề xuất

1. (Lá Chắn xét) Kiểm thêm **giá trị** của `_fields` theo danh sách hằng (`_POST_FIELDS`, `_POST_META_FIELDS`, `_MEDIA_FIELDS`, `_PUBLISHED_FIELDS`, trường chuyên mục): chốt luôn điều kiện «không hỏi `content`, `description`» của T-061 bằng code thay vì quy ước.
2. (Ngoài phiếu, W4) `_request` có thể truyền `verify=True` tường minh để `session` được truyền vào (nếu có) không tắt được kiểm chứng chỉ SSL. Hôm nay chỉ test truyền `session`.

## Câu hỏi cho Chỉ Huy

**LC-T061-3:** «`upload_media` luôn ghi đè cả `alt_text`, `title`, `caption`» (ô trống gửi chuỗi rỗng, tiêu đề trống lấy tên file đã làm sạch, như WordPress tự đặt) làm 4 test cũ hỏng, vì chúng ghi lại đúng cách làm cũ mà phiếu bảo đổi (không phải chuỗi câu lỗi, nên ngoài phần phiếu cho sửa):

| Test | Vì sao hỏng | Đề xuất sửa (không nới kiểm tra) |
|---|---|---|
| `tests/test_wordpress_client.py::test_upload_media_with_alt` | so thân lệnh ghi đúng bằng `{"alt_text": …}` | so đúng bằng `{"alt_text": "Cửa sắt sơn đen", "title": "anh-cua-sat", "caption": ""}` |
| `tests/test_wordpress_client.py::test_upload_media_without_metadata_is_one_request` | đòi đúng 1 lệnh | đổi tên `…_still_overwrites_fields`, đòi đúng 2 lệnh, lệnh 2 là `{"alt_text": "", "title": "anh", "caption": ""}` |
| `tests/test_wordpress_client.py::test_upload_media_file` | site giả thiếu đường `/wp/v2/media/6` | thêm đường đó vào site giả |
| `tests/test_soi_loi_t044.py::test_null_source_url_does_not_crash_page` | site giả thiếu đường `/wp/v2/media/9` | thêm đường đó (trả `source_url: None` như cũ) |

Cho sửa 4 test này không? Đề xuất: **có**.

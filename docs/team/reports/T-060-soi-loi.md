# Báo cáo T-060 · Dọn lỗi Thấp của client WordPress · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-060](../tickets/T-060-don-loi-thap-client-wordpress.md) |
| Nhánh | `team/T-060` (gốc `main` `cf8d824`, kiểm trên đầu nhánh `af6edfd`) |
| Ngày nộp | 2026-10-24 |
| Kết quả | Hoàn thành (mức kiểm: có, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được ngay. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T060-1). Soát R5 cho 4 test cũ và các test cũ khác bị đổi: **đạt** |

## Tóm tắt (cho chủ dự án)

- Bản sửa của Thợ Máy làm đúng cả 8 việc. Tôi thử phá bằng site giả của riêng tôi: hơn 250 cách viết lén tham số hay dòng đầu lệnh «đổi đường» (chữ hoa, mã hóa `%5F`, thêm `[]`, dấu cách, gắn sẵn vào phiên kết nối…) đều bị chặn **trước khi gửi**; câu báo lỗi với 20 mã lỗi × 10 kiểu trả lời độc (trang HTML, chuỗi 100.000 ký tự, địa chỉ, mật khẩu…) không bao giờ chép lời website hay địa chỉ, luôn kèm mã lỗi.
- Không chặn oan: mọi việc thật của phần mềm (kiểm kết nối, tải chuyên mục/thẻ, danh sách bài, tạo nháp, tải ảnh, ghi alt, đặt ảnh đại diện, ghi SEO, gửi nháp kèm ảnh) vẫn gửi đúng lệnh. Trang Kết nối WordPress và mọi trang khác vẫn mở được. Tiêu đề SEO thường như «Cửa sắt < 2 triệu», «So sánh cửa sắt & cửa nhôm» vẫn qua.
- Gộp thử với màn hình chọn ảnh T-056 (đang làm song song): không xung đột, test của cả hai cùng qua.
- Tìm thấy **1 lỗi nhỏ (Thấp)**: ở trang Kết nối WordPress, nếu website (hay plugin lỗi) trả lời lệnh ghi mô tả ảnh bằng thông tin của **một ảnh khác**, phần mềm vẫn nhận và hiện địa chỉ ảnh khác đó. Không đụng bài hay ảnh nào trên website; chỉ là dòng báo sai. Có thể sửa ở phiếu dọn lỗi sau, không cần chặn T-060.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t060.py` | Mới: 608 ca (606 qua, 2 `xfail(strict=True)` của SL-T060-1). Dữ liệu, địa chỉ site riêng và bản Python của `sanitize_text_field` riêng (không dùng lại của Thợ Máy hay T-061); dùng site giả chung `FakeWordPress` của repo như mọi file test |
| `docs/team/reports/T-060-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng việc

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| LC-T042-1 · tham số, header đổi đường | **ĐẠT** | `client.py:95` (`ALLOWED_PARAMS`, khóa đúng bằng `ALLOWED_ROUTES`), `:116`, `:119`, `:121`, `:144` (`_is_plain_request`), `:1349-1354`. Danh sách cho phép theo **từng đường** (so đúng từng chữ), cộng danh sách cấm gập chữ làm lớp phụ, chỉ nhận `params`/`json` (`dict`)/`data` (`bytes`)/`headers`; header chỉ `Content-Type` loại ảnh và `Content-Disposition`; header của `session` không được có chữ «method» hay `Content-Type`; `session.params` phải rỗng. Thử: 17 cách viết khóa cấm × 13 đường được phép = 221 ca (`test_khoa_cam_moi_dang_bi_chan_tren_moi_duong`); giá trị có `&rest_route=`, `?_method=`, `#`, `;`, CRLF vẫn chỉ ra đúng **một** khóa `_fields` sau khi mã hóa; 8 header lạ (`X-HTTP-Method-Override ` có dấu cách cuối, viết lẫn hoa thường, `X-Original-URL`, `X-Rewrite-URL`, `Host`, `Authorization`, `Cookie`); 5 `Content-Type` không đúng loại ảnh; 5 đường kèm `?`/`#`/`%3F`; 4 kiểu gắn sẵn vào `session`; 14 tùy chọn lạ của `requests` (thân form `dict`/danh sách, `bytearray`, `memoryview`, `files`, `json` không phải `dict`, `stream`, `proxies`, `cert`, `hooks`, `auth`, `verify=False`, `allow_redirects`). **Lớp chặn phụ**: nới danh sách cho phép của `GET /` để nhận 10 khóa cấm (`REST_ROUTE`, `rest.route`, `rest route`, `rest_route[]`, `_Method`, `_jsonp[x]`…) thì vẫn bị chặn. Mọi ca: **0 lệnh** đi ra, câu cố định không chép đường hay tham số. Script dò thêm: 40 khóa × 4 đường, 14 kiểu `params` lạ (danh sách cặp lặp khóa, `dict` con, `OrderedDict`, chữ, `bytes`, khóa/giá trị là lớp con của `str`, `IntEnum`, `bool`, `float`…), 10 đường, 8 cách viết phương thức (`post`, `PUT`, `DELETE`, ` POST`…), 18 header: 0 lọt |
| LC-T042-4 · câu lỗi cố định kèm mã | **ĐẠT** | `client.py:1405-1446` (`_error_from` tĩnh, bỏ «(WordPress: …)»), `:57` (`_ERROR_CODE`), `:595`, `:1373`, `:1385`. Client dùng địa chỉ riêng `https://suachua-thu.vn` (khác chữ mẫu `https://example.com` trong câu hướng dẫn, để câu nào chép địa chỉ là thấy). Thử 20 mã (400, 401, 402, 403, 404 cả hai nhánh, 405, 409, 410, 413, 415, 418, 422, 429, 451, 500, 501, 502, 503, 504, 520) × 10 thân trả về độc (trang HTML có `<script>` và link, chuỗi 100.000 ký tự, địa chỉ site + số điện thoại, mật khẩu, `code` là HTML, danh sách, chuỗi, `null`, rỗng, `message` là `dict`) = 200 ca: câu luôn có «(mã N)», không có lời máy chủ, mật khẩu, địa chỉ, «<», xuống dòng, dài dưới 400 ký tự; `code` chỉ còn `[A-Za-z0-9_-]`. 6 mã chuyển hướng có `Location` độc: câu có «(mã 3xx)», không đi theo. 9 loại lỗi mạng của `requests` mang địa chỉ + mật khẩu trong thông điệp: không lọt chữ nào. 5 `WORDPRESS_URL` sai dạng (`htps://` hay `ftp://` kèm tên và mật khẩu trước «@», `javascript:`, link Markdown): không chép lại. Lệnh ghi đè ảnh lỗi 400/403/500: câu cố định kèm mã. Script dò riêng: 22 mã × 16 thân qua `check_connection`, 5 mã × 16 thân qua 6 hàm công khai, 6 mã chuyển hướng, 11 lỗi mạng, 11 `WORDPRESS_URL` sai dạng (có tên và mật khẩu, `javascript:`, `<script>`, link Markdown, rỗng): không chép chữ nào của máy chủ hay địa chỉ, chỉ còn chữ mẫu cố định `https://example.com` |
| LC-T042-5 · `WORDPRESS_URL` trỏ file chạy được | **ĐẠT** (xem ghi chú `index.php`) | `client.py:1634` (đoạn thư mục không có dấu «.»). 17 ca bị từ chối, câu không chép địa chỉ: `index.php/`, `index.php/wp`, `INDEX.PHP`, `blog/index.php`, dấu chấm cuối `x.php.`, `x.`, `%2E`, `x.php%20`, `;.php`, `x.php;a`, `::$DATA`, dấu chấm toàn khổ `．`, `.cfm`, `.jspx`, `.htaccess`, `?rest_route=` (có và không có `/`). Không chặn oan: `suachuacuasat.com` (có/không `www`, `/` cuối), cổng `:8443/blog`, thư mục `cgi-bin`, `index`, `php` (không đuôi). Script dò: ~75 địa chỉ xấu đều bị chặn |
| LC-T061-2 · `_seo_text` chặn «<» dính chữ | **ĐẠT** | `client.py:227`, `:1573` (xét cả chữ gốc, chữ đã chuẩn hóa, NFKC). 14 ký tự sau «<» (U+2028, U+2029, U+202F, U+205F, U+1680, U+180E, BOM, dấu kết hợp U+0338, U+3164, `\x1c`, emoji, `'`, `!`, `?`) × 3 mẫu = 42 ca bị chặn. Thử ngẫu nhiên 6.000 chuỗi trong test (200.000 chuỗi trong script dò, 89.125 chuỗi qua bộ kiểm): chữ nào qua thì mọi «<» còn lại đều có khoảng trắng kiểu C ngay sau, và sau bản Python của `sanitize_text_field` (`isspace` của C như PHP, có `wp_pre_kses_less_than`, nháy trong thẻ, «<!», «<?», bỏ `%xx`) **không** có shortcode nào chạy được. 6 tiêu đề thường không bị chặn oan |
| LC-T061-3 · `upload_media` luôn ghi đè 3 ô | **ĐẠT** (còn SL-T060-1, Thấp) | `client.py:1042` (ô trống → `""`, tiêu đề trống → tên file đã làm sạch), `:1043-1046` (kiểm kiểu **trước** khi tải), `:1051-1057`. Test: 4 bộ ô (không truyền, chuỗi rỗng, `None`, ngoặc vuông) → lệnh ghi đè **đúng bằng** 3 ô + `?_fields`; 4 kiểu sai (`1.5`, `True`, tuple, `bytearray`) × 3 ô → báo lỗi, **0 lệnh**. Script dò 14 kiểu ô (trống, `None`, chỉ dấu cách, ngoặc vuông, HTML, `0`, `False`, `[]`, tên file `....jpg`, `[code].jpg`, tên 300 ký tự): lệnh ghi đè luôn có đủ 3 ô, không «[» trần. Lệnh ghi đè lỗi: báo lỗi, đúng 2 lệnh. Câu trả lời lệnh ghi đè nói về ảnh khác thì vẫn nhận: SL-T060-1 |
| LC-T061-5 · siết `test_soi_loi_t042.py:423-424` | **ĐẠT** | `tests/test_soi_loi_t042.py:424-427`: so `urlsplit(...).path` **và** `parse_qs(query) == {"_fields": [...]}` (giá trị viết thẳng, chặt hơn cũ) |
| LC-T071-1 · `upload_media` chỉ nhận 201 | **ĐẠT** | `client.py:1048` (`new_only=True`). 200, 202, 204 rỗng: dừng sau **đúng 1 lệnh**, câu nhắc «201». 201 mà mã ảnh thiếu, `"9"`, `True`, `0`, `-9`, `9.0`, thân là danh sách, trang HTML: dừng sau 1 lệnh, không ghi đè ảnh nào (`test_upload_media_201_ma_anh_sai_khong_ghi_de_gi`) |
| Gỡ `xfail` | **ĐẠT** | `git diff cf8d824..team/T-060`: `test_soi_loi_t061.py` −8 dòng (2 khối dấu: SL-T061-1 4 ca, SL-T061-2 2 ca), `test_la_chan_t071.py` −5 dòng (1 khối, 2 ca). Chỉ xóa dòng dấu, thân test không đổi chữ nào; cả 8 ca qua |

## Không chặn oan

`test_moi_lenh_that_cua_app_van_di_ra` (9 ca) chạy từng việc thật trên site giả trả lời như WordPress, so **đúng** dãy lệnh đi ra (phương thức, đường, tên tham số):

| Việc | Lệnh đi ra |
|---|---|
| Kiểm kết nối | `GET /`, `GET` Abilities SiteSEO, `GET /wp/v2/users/me?context` |
| Chuyên mục, thẻ | `GET /wp/v2/categories`, `/wp/v2/tags` với `per_page, page, orderby, order, hide_empty, _fields` |
| Danh sách bài đã đăng | `GET /wp/v2/posts`, `/wp/v2/pages` với `status, per_page, page, orderby, order, _fields` |
| Tạo nháp (có chuyên mục, thẻ, đoạn trích, slug) | `POST /wp/v2/posts?_fields` |
| Tải ảnh + ghi alt | `POST /wp/v2/media?_fields`, `POST /wp/v2/media/101?_fields` |
| Đặt ảnh đại diện | `GET /wp/v2/posts/42?context&_fields`, `POST /wp/v2/posts/42?_fields` |
| Ghi SEO (Abilities) | `GET` Abilities, `GET /wp/v2/posts/42`, `POST …/seo-data-update/run` |
| Gửi nháp kèm ảnh (ảnh thật qua `make_web_image`) | tải ảnh, ghi alt, tạo nháp, kiểm nháp, đặt ảnh đại diện |

Script dò thêm đường ghi SEO dự phòng (meta qua `wp/v2/posts`): đi ra đúng. Trang Kết nối WordPress và mọi trang: `tests/test_app_pages.py`, `tests/test_app_wordpress.py` qua (trong lượt 25 file bên dưới). Không module nào ngoài `client.py` gọi `_request` hay truyền `session`; `WordPressError.code` chỉ được so ở `client.py:778` (`rest_post_invalid_page_number`) và `:1432` (`rest_no_route`), cả hai qua `_ERROR_CODE`.

## Soát R5

Đối chiếu `git diff cf8d824..team/T-060 -- tests/` với bảng «Sửa 4 test cũ» của báo cáo Thợ Máy; số dòng cũ (`git show cf8d824:…`) và mới khớp từng dòng.

| Test | Kết quả |
|---|---|
| `test_wordpress_client.py::test_upload_media_with_alt` (298 → 300-301) | **Đạt.** Vẫn so **đúng bằng** cả thân lệnh ghi, chỉ thêm 2 ô mới (`title`, `caption`); 5 `assert` khác giữ nguyên |
| `test_wordpress_client.py::test_upload_media_without_metadata_is_one_request` → `…_still_overwrites_fields` (303/306 → 306/308/310-311/314) | **Đạt.** Đổi tên vì điều test cũ khẳng định (ô trống thì 1 lệnh) chính là hành vi phiếu bảo bỏ, Chỉ Huy B duyệt. Vẫn đòi **đúng** số lệnh (1 → 2), thêm `assert` thân lệnh 2; 3 `assert` cũ (`Content-Type`, tên `anh.webp`, `media.id`) giữ nguyên. Không nới |
| `test_wordpress_client.py::test_upload_media_file` (315 → 322) | **Đạt.** Chỉ thêm đường ghi đè vào site giả; 2 `assert` giữ nguyên |
| `test_soi_loi_t044.py::test_null_source_url_does_not_crash_page` (317 → 320) | **Đạt.** Câu trả lời lệnh ghi đè vẫn có `source_url: None`, nên test vẫn kiểm đúng điều cũ (trang không vỡ, đúng 1 thông báo thành công) |
| `test_wordpress_client.py::test_wrong_application_password`, `::test_forbidden` | **Đạt** (phiếu cho sửa chuỗi câu lỗi). Đổi «lời máy chủ **có** trong câu» thành «**không** có» + «(mã 401)», «(mã 403)»; chặt hơn |
| `test_soi_loi_t044.py::test_real_client_multiline_wordpress_error_is_plain` | **Đạt.** `startswith("… (WordPress: Dòng một …")` → `== "WordPress báo lỗi (mã 400)."` cộng 2 `assert` «không có»; các kiểm trang không link, không xuống dòng giữ nguyên |
| `test_app_t044_safe_text.py::test_bad_wordpress_url_message_is_plain` | **Đạt.** Đổi «câu **có** chép địa chỉ» thành «**không** chép» theo yêu cầu 2; «không hợp lệ», không link giữ nguyên |
| `test_soi_loi_t042.py` (LC-T061-5), gỡ 8 `xfail` | **Đạt** (mục trên) |

Lọc mọi dòng thêm/xóa có `assert`, `parametrize`, `raises`, `skip`, `xfail`, `def test_` trong 6 file test cũ (`git diff --numstat`: +23/−23): mỗi dòng `assert` bị xóa đều có dòng thay **chặt hơn hoặc bằng** (so đúng bằng thay cho «bắt đầu bằng», thêm ô, đảo «có chép» thành «không chép» theo yêu cầu 2); không `parametrize`, `raises` nào bị xóa; không test nào bị `skip`; 3 khối `xfail` bị xóa là đúng 3 khối phải gỡ.

## T-056 chạy song song

- `_has_shortcode`, `_SHORTCODE_OPEN`, `escape_shortcodes`, `_drop_invisible`, `create_draft_with_images`, `_describe_draft_media`, `ALLOWED_ROUTES`, `is_allowed_route` **không đổi** (so cây cú pháp `ast` giữa `cf8d824` và nhánh).
- `git merge-tree origin/team/T-056 team/T-060`: không xung đột (T-056 không sửa `client.py`; `seo_app/wordpress/shortcodes.py` của T-056 dùng `_SHORTCODE_OPEN`, `_drop_invisible`).
- Chạy trên cây đã gộp thử (giải nén vào thư mục nháp): `tests/test_wordpress_shortcodes.py`, `tests/test_app_images.py` (T-056), `tests/test_wordpress_t060.py`, `tests/test_soi_loi_t061.py`, `tests/test_wordpress_images.py`, `tests/test_app_wordpress.py`: **463 passed** (07:59–08:01).

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, không đụng worktree), gỡ từng chỗ sửa của T-060 trong `client.py` rồi chạy test. Lượt 1 (08:04–08:10): 7 file (`test_soi_loi_t060.py` bản đầu, `test_wordpress_t060.py`, `test_wordpress_client.py`, `test_soi_loi_t061.py`, `test_la_chan_t071.py`, `test_soi_loi_t042.py`, `test_wordpress_round2_t042.py`). Lượt 2 (08:16–08:20): **chỉ** `test_soi_loi_t060.py` bản cuối. Bản không gỡ: mọi test qua.

| # | Chỗ sửa bị gỡ | Test của Soi Lỗi (lượt 2) | Test của Thợ Máy và test cũ (lượt 1) |
|---|---|---|---|
| M1 | Danh sách khóa theo từng đường | hỏng | 16 `test_wordpress_t060.py` |
| M2 | Danh sách khóa cấm (lớp phụ) | hỏng (`test_lop_chan_phu_…`) | 0 (đúng dự kiến: danh sách cho phép đã che) |
| M3 | Danh sách header | hỏng | 1 |
| M4 | `Content-Type` phải là loại ảnh | hỏng | 2 |
| M5 | `Content-Type` trong `session` | hỏng | 1 |
| M6 | Chữ «method» trong header | hỏng | 5 |
| M7 | Danh sách tùy chọn của lệnh | hỏng | 6 |
| M8 | `session.params` phải rỗng | hỏng | 1 |
| M9 | Kiểu `data`/`json` | hỏng | 4 |
| M10 | Thêm lại «(WordPress: …)» | hỏng | 22 + 2 `test_wordpress_client.py` |
| M11 | Bỏ lọc `code` | hỏng | 7 |
| M12 | `_SITE_PATH` cũ (nhận dấu chấm) | hỏng | 15 + 6 `test_wordpress_round2_t042.py` |
| M13 | Bỏ kiểm «<» liền chữ | hỏng | 13 + 4 `test_soi_loi_t061.py` |
| M14 | Kiểm «<» chỉ trên chữ đã chuẩn hóa | hỏng | 4 |
| M15 | «<» theo `\s` của Python (nhận U+00A0, `\x1c`…) | hỏng | 2 |
| M16 | «<» cuối chữ không chặn | hỏng (thử ngẫu nhiên) | 1 |
| M17 | `upload_media` nhận mọi 2xx | hỏng | 8 + 2 `test_la_chan_t071.py` |
| M18 | Ô trống không gửi | hỏng | 5 + 2 `test_soi_loi_t061.py` + 2 `test_wordpress_client.py` |
| M19 | Tiêu đề trống gửi rỗng | hỏng | 4 + 2 `test_wordpress_client.py` |
| M20 | Kiểm kiểu 3 ô sau khi tải | hỏng | 12 |
| M21 | Câu khởi tạo chép `WORDPRESS_URL` | hỏng | 3 |
| M22 | Lỗi kết nối chép địa chỉ | hỏng | 1 |
| M23 | Câu 404 chép địa chỉ | hỏng | 1 |
| M24 | Câu chuyển hướng không kèm mã | hỏng | 1 |

Ở lượt 1, bản đầu của file test này không bắt được M7, M9, M18–M24 và có một chỗ yếu: địa chỉ site giả `https://example.com` trùng chữ mẫu trong câu hướng dẫn, nên không phân biệt được câu chép địa chỉ. Tôi đã sửa (địa chỉ riêng, đủ 20 mã, thêm chuyển hướng, tùy chọn lạ, lớp chặn phụ, thân lệnh ghi đè); lượt 2 bắt đủ 24.

## Lỗi tìm được

### SL-T060-1 (Thấp) · `upload_media` nhận câu trả lời lệnh ghi đè của ảnh khác

- **Chỗ:** `seo_app/wordpress/client.py:1051-1059`. Nhánh gửi nháp kèm ảnh (`_describe_draft_media`, `:1314-1315`) báo `_MEDIA_ODD_ANSWER` khi câu trả lời lệnh ghi alt không đúng mã ảnh vừa tạo; `upload_media` (trang Kết nối WordPress) thì `media = updated` với bất kỳ `dict` nào.
- **Tái hiện:** tải ảnh trả `201 {"id": 9, "source_url": ".../cong.jpg"}`; lệnh `POST /wp/v2/media/9` trả `{"id": 77, "source_url": ".../anh-khac.jpg", "alt_text": "Ảnh khác"}` (hoặc không có `id`, `source_url` là `https://evil.example/anh.jpg`). Gọi `upload_media(ảnh, "cong.jpg", alt_text="Cổng")`.
- **Mong đợi:** báo lỗi như nhánh gửi nháp kèm ảnh, hoặc ít nhất không lấy địa chỉ, alt của ảnh khác.
- **Thực tế:** trả `Media(id=9, source_url=".../anh-khac.jpg", alt_text="Ảnh khác")`; trang hiện «Ảnh đại diện đã tải lên: <địa chỉ ảnh khác hay địa chỉ ngoài site>» (chữ thường, không thành link). Phần mềm cũng không biết 3 ô của ảnh 9 đã được ghi đè thật chưa, nên LC-T061-3 không được bảo đảm trong ca này. Bài nháp vẫn lấy đúng ảnh 9 làm ảnh đại diện.
- **Mức:** Thấp. Chỉ xảy ra khi website hay plugin trả lời sai; không ghi, không xóa gì trên site. Có từ trước T-060 (khi ô alt có chữ), T-060 làm lệnh ghi đè chạy cả khi ô alt trống. Không chặn T-060.
- **Test:** `test_sl_t060_1_upload_media_khong_nhan_tra_loi_cua_anh_khac` (2 ca, `xfail(strict=True)`). Sửa đúng (báo lỗi, hoặc giữ địa chỉ và alt của ảnh 9) thì XPASS: chỉ cần xóa dòng `@pytest.mark.xfail`.
- **Gợi ý sửa:** sau lệnh ghi đè, kiểm `_positive_id(updated.get("id")) == media_id` như `:1314`; sai thì báo câu cố định.

## Ghi nhận (không phải lỗi của T-060)

1. **`index.php` trong `WORDPRESS_URL`:** lời giao việc cho Soi Lỗi ghi «`index.php` vẫn được», nhưng code vẫn **chặn** `index.php` (cả `INDEX.PHP`, `blog/index.php`). Phiếu ghi «`.php` trừ `index.php` như T-042», mà T-042 chặn `index.php` (`tests/test_wordpress_round2_t042.py:462`, biên bản Lá Chắn T-042 dòng 96). Thợ Máy hiểu theo cách T-042 và không nới test cũ (R5), tôi thấy hợp lý: website dùng đường dẫn tĩnh, `/wp-json/` chạy được (T-033). Đề nghị Chỉ Huy xác nhận cách hiểu; nếu muốn cho qua `index.php` thì phải sửa cả test cũ T-042.
2. **File chạy được không có đuôi:** `https://site/cgi-bin/x` (CGI không đuôi) vẫn được nhận vì không có dấu chấm. Đúng như gợi ý của Lá Chắn T-042 và đúng phạm vi phiếu (danh sách đuôi). Chỉ vào được qua `.env` do chủ máy tự khai. Lá Chắn xét có cần chặn đoạn `cgi-bin` không.
3. **Thân JSON không theo danh sách khóa:** `_request` không kiểm khóa trong `json=` (ví dụ `{"_method": "DELETE", "id": 7}` vẫn gửi). `_method`, `_envelope`, `_jsonp`, `rest_route` WordPress chỉ đọc ở truy vấn hay thân dạng form (đã chặn), nên không đổi đường. Còn `id` trong thân JSON có thể được WordPress ưu tiên hơn `id` trên đường (thứ tự đọc tham số của `WP_REST_Request`: JSON trước URL); **nhận định này tôi chưa đối chiếu mã WordPress**. Hôm nay mọi khóa JSON đều do code viết sẵn (không có `id`), không có đường tới. Lá Chắn xét cùng đề xuất 1 của Thợ Máy.
4. **Mã ảnh quá 19 chữ số:** tải ảnh trả `201 {"id": 10**20}` thì lệnh ghi đè bị chặn đường với câu «Không có gì được gửi lên website», trong khi ảnh đã lên thư viện Media. Chỉ khi website trả mã vô lý (WordPress lõi không thể tới); có từ trước (khi ô alt có chữ). Ghi để Chỉ Huy biết, không xếp lỗi.
5. **Câu lỗi file ảnh sai đuôi / rỗng** vẫn chép tên file người dùng chọn: Thợ Máy giữ có chủ ý (không phải lời máy chủ hay `WORDPRESS_URL`, test T-044 chứng minh không thành link). Đồng ý.
6. `detect-secrets` (`PYTHONUTF8=1`) trên 2 file của tôi: «Secret Keyword» ở `tests/test_soi_loi_t060.py:37` (`PASSWORD = "…"`) và «Basic Auth Credentials» ở `:351`, `:353` (địa chỉ sai dạng có tên, mật khẩu trước «@», dùng để thử câu lỗi không chép lại). Đều là chuỗi giả cho test, cùng kiểu với 18 file test khác có `PASSWORD = "…"` (kể cả `tests/test_wordpress_t060.py`). Báo cáo này: 0.

## Bằng chứng

```
$ uv run pytest tests/test_wordpress_t060.py tests/test_wordpress_client.py tests/test_wordpress_images.py
    tests/test_soi_loi_t042.py tests/test_soi_loi_t044.py tests/test_app_t044_safe_text.py
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_la_chan_t071.py
    tests/test_soi_loi_t071.py tests/test_soi_loi_t054.py tests/test_app_pages.py tests/test_app_wordpress.py
    tests/test_onpage_links.py tests/test_phase2_fixes.py tests/test_site_index.py tests/test_soi_loi_t031.py
    tests/test_soi_loi_t037.py tests/test_soi_loi_t039.py tests/test_soi_loi_t042_round2.py
    tests/test_soi_loi_t075.py tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py -rxX
3559 passed, 1 skipped in 217.59s      # đầu nhánh af6edfd, chưa có file của tôi, 07:52–07:56
# 25 file = danh sách phiếu giao + mọi file có WordPressClient/upload_media (grep -l)

# Lượt cuối (08:20–08:24): 25 file trên + tests/test_soi_loi_t060.py + 8 file WordPress khác
# (test_la_chan_t039, test_sanitize, test_site_index_t042, test_soi_loi_t042_paging_cache,
#  test_soi_loi_t081, test_wordpress_paging_t042, test_wordpress_site_link_t042, test_t081_alt_gach_cheo)
4560 passed, 1 skipped, 10 xfailed in 202.68s
# 10 xfail: 2 SL-T060-1 (mới); 3 LC-T039-2, 5 SL-T081-1 (có sẵn, không thuộc T-060)
# bỏ qua 1: symlink (Windows chưa bật Developer Mode)

$ uv run pytest tests/test_soi_loi_t060.py
606 passed, 2 xfailed in 5.99s

$ uv run ruff check .
All checks passed!

# Test mới trên code cũ (main cf8d824, giải nén vào thư mục nháp):
456 failed, 150 passed, 2 xfailed
# 150 qua: ca đối chứng (lệnh thật, chữ SEO thường, địa chỉ thường), việc T-042 đã làm (đường kèm
# truy vấn, `.php`, mã ảnh sai kiểu, phần lớn lỗi mạng) và mã/thân mà câu cũ vốn không chép gì
```

Script dò riêng (site giả, bản PHP, đột biến): thư mục ghi chú chung `T-060-soi-loi-scripts/` (`fakesite.py`, `probe_params.py`, `probe_errors.py`, `probe_url.py`, `probe_seo_text.py`, `probe_upload.py`, `probe_real_calls.py`, `mutate.py`). Chạy bằng `.venv` của worktree, thư mục làm việc là worktree.

## Đối chiếu tiêu chí xong

- [x] Đọc diff, xác nhận 8 việc (mục «Kiểm từng việc»)
- [x] Thử độc lập bằng site giả riêng: hoa/thường, `%5F`, tham số lặp, header viết khác, `?rest_route=` trong `WORDPRESS_URL`, đuôi file có chấm cuối/khoảng trắng/`%2E`, `index.php/…`, câu lỗi với thân độc, `_seo_text` với «<» + Unicode lạ, `upload_media` 200/202/201 thiếu mã
- [x] Không chặn oan: 9 việc thật + đường SEO dự phòng; `tests/test_app_pages.py` qua
- [x] Soát R5: 4 test cũ đúng bảng trước/sau, các test cũ khác bị đổi không nới `assert` nào
- [x] Lỗi mới có test `xfail(strict=True)`: SL-T060-1
- [x] T-060 không đổi `_has_shortcode`, `_SHORTCODE_OPEN`; gộp thử với T-056 qua
- [x] Không sửa code ứng dụng

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (SL-T060-1). **Chuyển Lá Chắn được ngay.** Điều kiện: SL-T060-1 vào phiếu dọn lỗi sau (hoặc lượt 2 của T-060 nếu Chỉ Huy muốn), theo mốc của T-060 (trước khi hết Giai đoạn 4); Chỉ Huy xác nhận cách hiểu `index.php` (ghi nhận 1).

## Đề xuất

1. (Thợ Máy, phiếu dọn lỗi) SL-T060-1: kiểm mã ảnh trong câu trả lời lệnh ghi đè như `_describe_draft_media`.
2. (Lá Chắn xét) Ghi nhận 2, 3: `cgi-bin` không đuôi; danh sách khóa cho thân JSON, cùng đề xuất 1 của Thợ Máy (kiểm giá trị `_fields`).

## Câu hỏi cho chủ dự án

Không có.

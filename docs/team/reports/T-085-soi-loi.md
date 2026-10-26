# Báo cáo T-085 · Dọn lỗi Thấp client WordPress sau T-060 · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-085](../tickets/T-085-don-client-wordpress-sau-t060.md) |
| Nhánh | `team/T-085` (gốc `main` `8ae67f8`, kiểm trên đầu nhánh `8d0eb56`) |
| Ngày nộp | 2026-10-26 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T085-1, -2, -3). Soát R5 (1 test cũ): **đạt** |

## Tóm tắt (cho chủ dự án)

- Bản sửa của Thợ Máy làm đúng 5 yêu cầu. Phần dữ liệu đi kèm mỗi lệnh gửi lên website nay chỉ nhận đúng các ô của từng loại lệnh: tôi thử 40 tên ô trên cả 13 loại lệnh, «id», «name» viết kiểu nào cũng bị chặn, trạng thái bài chỉ nhận đúng chữ «draft». Khi ảnh đã lên mà bước ghi mô tả ảnh hỏng (29 kiểu hỏng), trang Kết nối WordPress báo rõ «ảnh đã lên thư viện Media, mã ảnh…, vào Media → Thư viện để kiểm».
- Không chặn oan: mọi việc thật của phần mềm vẫn chạy; gộp thử với `main` mới nhất và màn hình chọn ảnh T-056: không xung đột, test của cả hai qua.
- Tìm thấy **3 lỗi nhỏ (Thấp)**, hôm nay chưa khai thác được:
  1. Chốt chặn «không xin website trả nội dung bài» vẫn bị vòng qua nếu chèn một ký tự vô hình đặc biệt (ký tự rỗng, mã 0) sát tên trường: WordPress tự cắt ký tự đó đi. Hôm nay phần mềm không đưa chữ nào từ ngoài vào chỗ này. Sửa 1 dòng.
  2. Nếu website trả về dữ liệu lồng nhau quá sâu, trang Kết nối WordPress hiện lỗi đỏ của Python thay vì câu báo tiếng Việt.
  3. Ở trang Kết nối WordPress, nếu website lỗi ngay lúc nhận ảnh (máy chủ quá tải, hết giờ chờ…) thì ảnh có thể đã lên thư viện Media, nhưng câu báo chỉ nói «thử lại sau»; bấm lại sẽ thành ảnh trùng.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t085.py` | Mới: 741 ca (705 qua, 36 `xfail(strict=True)`: SL-T085-1 27, SL-T085-2 3, SL-T085-3 6). Dữ liệu và bản Python của WordPress riêng (không dùng lại của Thợ Máy, Lá Chắn); site giả chung `FakeWordPress` |
| `docs/team/reports/T-085-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| 1 · LC-T060-1: khóa thân JSON theo đường, không `id`/`name`, `status` chỉ `"draft"` | **ĐẠT** | `client.py:129-152`, `:209-217`. Bảng khóa JSON app **thật** gửi trên từng đường do tôi lập riêng (đọc từ các hàm công khai, không chép `ALLOWED_JSON_KEYS`): 40 tên khóa × 13 đường = 520 ca (`test_khoa_json_theo_dung_duong`): khóa app thật gửi thì đi ra nguyên vẹn, mọi khóa khác bị chặn trước khi gửi (`id`, `ID`, `Id`, ` id`, `id `, `name`, `NAME`, `Name`, `_fields`, `context`, `_method`, `rest_route`, `_embed`, `post`, `parent`, `author`, `password`, `date`, `meta` trên đường ảnh, `input` trên đường bài…). 17 giá trị `status` khác đúng chữ `"draft"` (`publish`, `future`, `pending`, `private`, `trash`, `Draft`, `draft ` có dấu cách, `draft\x00`, `dr` + «а» Kirin, rỗng, `None`, số, `True`, danh sách, `dict`): bị chặn. Khóa không phải chữ (`1`, `None`, tuple, `bytes`), thân là lớp con của `dict`, danh sách, chuỗi: bị chặn. Lớp chặn phụ: nới danh sách khóa của mọi đường thêm `id`/`Id`/`iD`/`name`/`nAme`/`NAME` thì vẫn chặn. Script dò thêm 48 khóa × 13 đường, 18 `status`, 5 kiểu thân: 0 lọt, 0 chặn oan |
| 2 · LC-T060-2: `_fields` không hỏi `content`, `excerpt`, `description`, `caption`, `_embedded`, `_links` | **ĐẠT, còn SL-T085-1 (Thấp)** | `client.py:120-122`, `:227-228`, `:245-254`. So với bản Python của WordPress tôi viết riêng (`wp_parse_list` tách theo khoảng trắng ASCII và dấu phẩy, rồi `array_map('trim')` của `get_fields_for_response`, rỗng thì trả mọi trường, `rest_is_field_included`). 25 biến thể × 6 tên × 9 đường có `_fields` (hoa thường, dấu cách đầu/cuối, tab, xuống dòng, `\x0b`, `\x0c`, `\r`, `.rendered`, `.raw`, `..x`, lặp, dấu phẩy thừa, `%63ontent`, `%2C`, `;`, `+`, U+00A0, `\x1c`, U+200B): giá trị nào đi ra thì WordPress **không** dựng trường chạy shortcode. `_fields` rỗng (6 dạng × 9 đường): bị chặn. Thử ngẫu nhiên 4.000 giá trị (không có NUL): 0 lọt. Không chặn oan: 10 hằng `_fields` của app trên đúng đường vẫn đi ra. **Lọt khi có ký tự NUL sát tên trường**: SL-T085-1 |
| 3 · LC-T060-3 + SL-T060-1: ghi đè hỏng hay trả lời sai mã ảnh → câu cố định | **ĐẠT, còn SL-T085-2 (Thấp)** | `client.py:375-380`, `:1123-1143`. 29 kiểu hỏng ở lệnh ghi đè (`test_ghi_de_hong_moi_kieu_bao_anh_dang_o_thu_vien_media`): 400, 401, 403, 404, 409, 413, 429, 500, 502, 503, chuyển hướng 301/302/307, hết giờ, mất kết nối, SSL, đứt giữa chừng, trang HTML 200, danh sách, chuỗi, `null`, số, mã ảnh khác (77), thiếu mã, mã là chữ `"9"`, `True`, `9.0`, `0`, `-9`. Mọi ca: câu có «thư viện Media», «mã ảnh 9», «Media → Thư viện»; không chép lời máy chủ, địa chỉ, alt của ảnh khác, mã 77; đúng 2 lệnh (tải, ghi đè đúng `/media/9`); lỗi HTTP giữ `status_code` và có «(mã N)». Ghi đè đúng ảnh: `Media` lấy địa chỉ, alt của **chính** câu trả lời đó (không lấy địa chỉ trong câu trả lời lúc tải). **Lọt khi câu trả lời là JSON lồng quá sâu**: SL-T085-2 |
| 4 · Không chặn oan | **ĐẠT** | Mục «Không chặn oan» |
| 5 · Gỡ `xfail` khi XPASS | **ĐẠT** | `git diff 8ae67f8..team/T-085`: `tests/test_la_chan_t060.py` −20 dòng (4 khối dấu, 12 ca), `tests/test_soi_loi_t060.py` −5 dòng (1 khối, SL-T060-1 2 ca). Chỉ xóa dòng dấu, thân test không đổi chữ nào; 14 ca qua |

## Không chặn oan

- Script «lệnh thật của app» (site giả riêng của tôi, dùng lại từ T-060) trên đầu nhánh: kiểm kết nối, chuyên mục, thẻ, danh sách bài đã đăng, tạo nháp, tải ảnh + ghi alt, tải ảnh từ file, đặt ảnh đại diện, ghi SEO qua Abilities, ghi SEO dự phòng (meta), gửi nháp kèm ảnh (ảnh thật qua `make_web_image`): **11/11 đi ra đúng**.
- `test_tao_nhap_du_truong_roi_anh_dai_dien_roi_seo_du_phong_van_di_ra`: tạo nháp đủ mọi trường tùy chọn (8 khóa JSON, `status` `"draft"`), đặt ảnh đại diện, ghi SEO dự phòng: đi ra đủ.
- `test_hang_fields_cua_app_van_di_ra` (10 ca); `tests/test_soi_loi_t060.py::test_moi_lenh_that_cua_app_van_di_ra` (9 việc, so đúng dãy lệnh) và 2 ca đối chứng của Lá Chắn T-060: qua.
- Trang Kết nối WordPress, mọi trang: `tests/test_app_pages.py`, `tests/test_app_wordpress.py`, `tests/test_app_t044_safe_text.py`, `tests/test_soi_loi_t044.py` qua.
- Không đổi: so cây cú pháp `ast` giữa `8ae67f8` và nhánh, chỉ đổi `ALLOWED_JSON_KEYS`, `_FORBIDDEN_JSON_KEYS`, `_RENDERED_FIELDS`, `_ROUTE_JSON_KEYS`, `_MEDIA_NOT_DESCRIBED`, `_asks_rendered_fields`, `_is_plain_request`, `upload_media`. `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`, `create_draft_with_images`, `_describe_draft_media`, `_post_media`, `_request`, `_error_from`, `ALLOWED_ROUTES`, `ALLOWED_PARAMS` **giống hệt**.

## Gộp thử với `main` mới nhất và T-056 (trang Soạn bài)

- `git fetch` (08:30): `origin/main` `ac1f2a4`, `origin/team/T-056` `5ad73eb` (`main` **chưa** có T-056: chưa có `seo_app/wordpress/shortcodes.py`).
- `git merge-tree --write-tree origin/main team/T-085`: không xung đột; gộp tiếp cây đó với `origin/team/T-056`: không xung đột (cây `48aa521`, giải nén vào thư mục nháp; đã kiểm `seo_app.wordpress.client` và `seo_app.wordpress.shortcodes` nạp từ cây gộp; không đụng worktree, không tạo nhánh).
- 18 file trên cây gộp, 08:30–08:39: test của T-056 (`tests/test_app_images.py` trang Soạn bài và màn hình chọn ảnh dùng `create_draft_with_images`, `tests/test_la_chan_t056.py`, `tests/test_soi_loi_t056.py`, `tests/test_wordpress_shortcodes.py`), gửi nháp kèm ảnh (`tests/test_wordpress_images.py`, `tests/test_soi_loi_t054.py`, `tests/test_soi_loi_t071.py`, `tests/test_shortcode_t061.py`), trang (`tests/test_app_pages.py`, `tests/test_app_wordpress.py`, `tests/test_app_t044_safe_text.py`, `tests/test_soi_loi_t044.py`), client (`tests/test_wordpress_round2_t042.py`, `tests/test_wordpress_t085.py`, `tests/test_la_chan_t060.py`, `tests/test_soi_loi_t060.py`, `tests/test_wordpress_t060.py`, `tests/test_wordpress_client.py`): **2055 passed, 7 xfailed, 0 hỏng**. 7 xfail đều là lỗi đã biết của chính T-056 (LC-T056-1 2 ca, SL-T056 5 ca), không liên quan T-085.

## Soát R5

| Test | Kết quả |
|---|---|
| `tests/test_wordpress_round2_t042.py::test_upload_media_odd_fields_are_safe` (89-90 → 89-92) | **Đạt.** Đối chiếu `git show 8ae67f8:…` với nhánh: 2 dòng site giả giữ nguyên; `assert (media.id, media.source_url, media.alt_text) == (5, "", "ảnh")` → `pytest.raises(WordPressError, match="thư viện Media")` + `assert "mã ảnh 5" in …`. Câu trả lời lệnh ghi đè là `["không phải dict"]`, tức không nói đúng ảnh 5: yêu cầu 3 **bắt** phải báo lỗi, nên kết quả cũ (trả `Media` bình thường) không còn đúng. Kiểm mới cụ thể (đúng chữ «thư viện Media», đúng mã ảnh), không nới. Ý cũ «trường sai kiểu không làm vỡ» chuyển sang `tests/test_wordpress_t085.py::test_tra_loi_dung_anh_nhung_truong_sai_kieu_khong_vo` (câu trả lời đúng ảnh 9, `source_url` là số, `alt_text` là danh sách → `Media(9, "", "Cổng")`): tương đương. Chỉ Huy B duyệt 2026-10-24, commit riêng `9d37b97` |

Ngoài test trên và 5 khối `xfail` (yêu cầu 5), không test cũ nào bị đổi (`git diff --stat 8ae67f8..team/T-085 -- tests/`).

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, không đụng worktree), gỡ từng chỗ sửa của T-085 trong `client.py` rồi chạy 5 file: `tests/test_soi_loi_t085.py` (của tôi), `tests/test_wordpress_t085.py` (Thợ Máy), `tests/test_la_chan_t060.py`, `tests/test_soi_loi_t060.py`, `tests/test_wordpress_round2_t042.py` (08:35–08:42). Bản không gỡ: mọi test qua.

| # | Chỗ sửa bị gỡ | Test của tôi hỏng | Test khác hỏng |
|---|---|---|---|
| N1 | Danh sách khóa JSON theo đường | 428 | 15 Thợ Máy |
| N2 | Lớp chặn phụ `id`/`name` | 6 | 5 Thợ Máy |
| N3 | Kiểm `status` | 17 | 15 Thợ Máy, 1 Lá Chắn |
| N4 | `status` không phân biệt hoa thường | 2 | 2 Thợ Máy |
| N5 | Kiểm giá trị `_fields` | 109 | 172 Thợ Máy, 3 Lá Chắn |
| N6 | Cho `_fields` rỗng | 55 | 28 Thợ Máy |
| N7 | Không đổi chữ thường | 0 | 14 Thợ Máy |
| N8 | Không cắt ở dấu chấm (`content.rendered`) | 55 | 42 Thợ Máy |
| N9 | Chỉ tách theo dấu phẩy | 91 | 42 Thợ Máy |
| N10 | Thiếu `description`, `caption`, `_embedded`, `_links` | 37 | 49 Thợ Máy, 1 Lá Chắn |
| N11 | Bỏ bọc lệnh ghi đè ảnh | 18 | 14 Thợ Máy, 3 Lá Chắn |
| N12 | Bỏ kiểm mã ảnh trong câu trả lời | 7 | 7 Thợ Máy, 2 Soi Lỗi T-060 |
| N13 | Câu báo không có mã ảnh | 29 | 25 Thợ Máy, 1 test cũ T-042 |
| N14 | Chỉ kiểm khóa đúng chữ `_fields` (bỏ dạng gập) | 0 | 4 Thợ Máy |
| N15 | Lấy địa chỉ ảnh từ câu trả lời lúc tải | 1 | 2 Thợ Máy |

Mọi chỗ sửa bị gỡ đều làm hỏng ít nhất một test. Hai chỗ test của tôi không bắt: N7 không làm yếu chốt chặn (WordPress so tên trường đúng chữ hoa thường, `Content` không dựng `content`; chặn cả `Content` là chặn thừa an toàn của Thợ Máy); N14 là lớp phụ chỉ có tác dụng khi ai đó nới `ALLOWED_PARAMS`, test của Thợ Máy thử đúng cảnh đó.

## Lỗi tìm được

### SL-T085-1 (Thấp) · `_fields` có ký tự NUL sát tên trường vòng qua chốt chặn LC-T060-2

- **Chỗ:** `seo_app/wordpress/client.py:245-254` (`_asks_rendered_fields`): tách bằng `re.split(r"[\s,]+")`, lấy phần trước dấu chấm, `.lower()`, không bỏ NUL.
- **Phía WordPress:** `get_fields_for_response` (`class-wp-rest-controller.php`, `wordpress-develop` trunk, tôi đọc 2026-10-26): sau `wp_parse_list( $request['_fields'] )` là `array_map( 'trim', $requested_fields )`; `trim()` mặc định của PHP bỏ `" \t\n\r\0\x0B"`, **có NUL**. Byte NUL trong giá trị truy vấn đi qua `$_GET` (PHP giữ nguyên byte), `wp_magic_quotes` (thành `\0`) rồi `wp_unslash` của REST (trả lại NUL), và `wp_parse_list` không tách ở NUL. Phần đường đi của NUL là nhận định từ hiểu biết về PHP, chưa thử trên máy chủ thật (không có staging); nếu tường lửa hay plugin bảo mật của hosting chặn `%00` thì lệnh không tới được WordPress (càng an toàn).
- **Tái hiện:** `wp_client._request("GET", "/wp/v2/posts/42", params={"context": "edit", "_fields": "id,status,\x00content"})` → lệnh **đi ra** (`…&_fields=id%2Cstatus%2C%00content`). WordPress cắt NUL thành `content`, `rest_is_field_included("content.rendered")` đúng, `apply_filters('the_content')` chạy shortcode ngay trong lệnh của app.
- **Mong đợi:** bị chặn trước khi gửi như `"id,status,content"`.
- **Thực tế:** script dò: 240 ca lọt (6 tên trường × 5 cách đặt NUL × 8 đường); test: 27 ca `xfail`. NUL ở giữa tên (`con\x00tent`) thì WordPress không cắt, vô hại.
- **Mức:** Thấp. Hôm nay mọi giá trị `_fields` là hằng của code, không có đường tới; nhưng đây là lối vòng qua đúng chốt chặn yêu cầu 2 (LC-T060-2 phải có trước phiếu nào đưa giá trị tham số lấy từ dữ liệu ngoài vào `_request`).
- **Test:** `test_sl_t085_1_fields_co_nul_sat_ten_truong_bi_chan` (27 ca).
- **Gợi ý sửa:** chỉ nhận giá trị `_fields` gồm `[A-Za-z0-9_.,]` (mọi hằng của app đều khớp), hoặc ít nhất cắt `" \t\n\r\0\x0b"` hai đầu mỗi tên như `trim()` trước khi so.

### SL-T085-2 (Thấp) · Câu trả lời JSON lồng quá sâu làm lọt lỗi Python (`RecursionError`)

- **Chỗ:** `client.py:1479-1486` (`_json` chỉ bắt `ValueError`), nên lỗi lọt qua mọi hàm của client; riêng `upload_media` lọt qua phần bọc mới của T-085 (`:1135`, chỉ bắt `WordPressError`). Nhánh gửi nháp kèm ảnh có bắt `Exception` (`_DRAFT_UNEXPECTED`).
- **Tái hiện:** website (hay plugin hỏng, proxy) trả `200` với thân `[[[…]]]` 50.000 tầng cho `GET /wp-json/`, hoặc cho lệnh ghi đè ảnh sau khi tải ảnh trả 201.
- **Mong đợi:** `WordPressError` câu cố định (như JSON hỏng); riêng ghi đè ảnh: câu «Ảnh đã lên thư viện Media… mã ảnh 9…».
- **Thực tế:** `RecursionError: maximum recursion depth exceeded while decoding a JSON array…` lọt ra. Trang Kết nối WordPress («Kiểm tra kết nối», «Tạo bài nháp») vỡ: Streamlit hiện khung lỗi Python, mặc định kèm chi tiết lỗi có đường dẫn file trên máy; với ảnh thì người dùng không biết ảnh đã ở thư viện Media.
- **Mức:** Thấp: cần máy chủ trả lời độc; có từ trước ở mọi lệnh. (Bảng mức của `security.md` xếp «thông báo lỗi lộ đường dẫn máy» là Trung bình; ở đây chỉ hiện trên màn hình của chính chủ máy và cần website trả lời độc, nên tôi đề nghị Thấp, Lá Chắn quyết.)
- **Test:** `test_sl_t085_2_json_long_qua_sau_thanh_cau_loi_co_dinh` (2 ca), `test_sl_t085_2_trang_ket_noi_khong_vo_vi_json_long_sau` (trang thật qua `AppTest`).
- **Gợi ý sửa:** `_json` bắt thêm `RecursionError` (hay mọi `Exception` lúc giải mã) thành câu cố định; phần bọc lệnh ghi đè của `upload_media` bắt cả lỗi lạ như nhánh gửi nháp kèm ảnh.

### SL-T085-3 (Thấp) · `upload_media` lỗi ở lệnh tải mà ảnh đã hay có thể đã lên: câu báo không dặn kiểm thư viện Media

- **Chỗ:** `client.py:1123` (`_post_media` trong `upload_media`, không bọc). Nhánh gửi nháp kèm ảnh có `maybe_uploaded` và câu `_DRAFT_IMAGE_MAYBE` cho đúng các ca này (`:387-390`, `:1286-1293`).
- **Tái hiện:** `POST /wp/v2/media` trả 500 (ca có thật: WordPress đã tạo ảnh rồi hết bộ nhớ khi dựng các cỡ ảnh; vì thế lõi WordPress có đường `/wp/v2/media/<mã>/post-process` để làm lại), 502, 503, hết giờ chờ, hay **201** mà thân là trang HTML hoặc không có mã ảnh.
- **Mong đợi:** lỗi không phải lời từ chối 4xx rõ ràng thì câu báo dặn ảnh có thể đã lên (201: đã lên) thư viện Media, kiểm Media → Thư viện trước khi tải lại. Lời từ chối 4xx (400, 403, 413) giữ như cũ: ca đối chứng `test_tai_anh_bi_tu_choi_ro_rang_khong_bao_anh_da_len` đang qua.
- **Thực tế:** «Máy chủ WordPress đang gặp lỗi (mã 500). Thử lại sau.», «WordPress phản hồi quá lâu (hơn 30 giây). Thử lại sau.», «WordPress không trả về dữ liệu JSON…», «WordPress trả về dữ liệu ảnh vừa tải lên không đúng dạng. Thử lại sau…». Người dùng thử lại thì thêm ảnh trùng; ảnh đầu giữ alt, tiêu đề, chú thích WordPress lấy từ chữ trong file: đúng nguy cơ của LC-T060-3, chỉ khác bước.
- **Mức:** Thấp. Có từ trước, ngoài yêu cầu 3 của phiếu (phiếu chỉ nói lệnh ghi đè). Không chặn T-085.
- **Test:** `test_sl_t085_3_tai_anh_loi_ma_anh_co_the_da_len_thi_dan_kiem_thu_vien` (6 ca).

## Ghi nhận (không xếp lỗi)

1. **Tham số truy vấn `id`, `name` chưa có lớp chặn phụ.** WordPress đọc truy vấn **trước** tham số trên đường (`get_parameter_order`: JSON → form → truy vấn → đường), nên `?id=7` trên `/wp/v2/media/9` cũng đổi ảnh đích như `id` trong thân JSON. Hôm nay `ALLOWED_PARAMS` không có hai khóa này nên không có đường; thử nới `ALLOWED_PARAMS` thêm `id`/`name` thì lệnh đi ra (thân JSON thì vẫn bị lớp phụ chặn). Lá Chắn xét có thêm lớp phụ cho truy vấn (so **đúng tên**, không so chuỗi con: `hide_empty` chứa «id»).
2. **Khóa `_fields`, `context` trong thân JSON** cũng được WordPress đọc trước truy vấn; hôm nay bị danh sách khóa JSON chặn. Nếu sau này ai thêm `_fields` vào `ALLOWED_JSON_KEYS` thì kiểm giá trị ở `params` bị vòng qua; đáng ghi vào chú thích cạnh `ALLOWED_JSON_KEYS`.
3. Đồng ý đề xuất 1 của Thợ Máy (bắt buộc có `_fields` trên đường bài, ảnh): thiếu `_fields` thì WordPress trả mọi trường, kể cả `content`.
4. Lời giao việc ghi «T-056 vừa gộp», nhưng lúc tôi kiểm (`git fetch` 08:30, 2026-10-26) `origin/main` (`ac1f2a4`) chưa có T-056; tôi gộp thử cả ba (mục trên).
5. `detect-secrets` (`PYTHONUTF8=1`) trên 2 file của tôi: «Secret Keyword» ở `tests/test_soi_loi_t085.py:45`, `:46` (`PASSWORD`, `PAGE_PASSWORD`): mật khẩu giả cho test, cùng kiểu với các file test khác. Báo cáo này: 0.

## Bằng chứng

```
# 41 file WordPress của báo cáo Thợ Máy, đầu nhánh 8d0eb56, chưa có file của tôi (08:22–08:29):
5547 passed, 1 skipped, 8 xfailed in 424.36s

# Lượt cuối (08:42–08:47): 41 file trên + tests/test_soi_loi_t085.py
$ uv run pytest tests/test_soi_loi_t085.py tests/test_ai_images.py tests/test_ai_t034.py
    tests/test_app_pages.py tests/test_app_t044_safe_text.py tests/test_app_wordpress.py
    tests/test_la_chan_t039.py tests/test_la_chan_t060.py tests/test_la_chan_t071.py
    tests/test_onpage_links.py tests/test_phase2_fixes.py tests/test_safety.py tests/test_sanitize.py
    tests/test_shortcode_t061.py tests/test_site_index.py tests/test_site_index_t042.py
    tests/test_soi_loi_t019_luot2.py tests/test_soi_loi_t031.py tests/test_soi_loi_t034.py
    tests/test_soi_loi_t037.py tests/test_soi_loi_t039.py tests/test_soi_loi_t042.py
    tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t044.py
    tests/test_soi_loi_t054.py tests/test_soi_loi_t060.py tests/test_soi_loi_t061.py
    tests/test_soi_loi_t071.py tests/test_soi_loi_t075.py tests/test_soi_loi_t081.py
    tests/test_t081_alt_gach_cheo.py tests/test_wordpress_client.py tests/test_wordpress_images.py
    tests/test_wordpress_paging_t042.py tests/test_wordpress_published.py
    tests/test_wordpress_round2_t042.py tests/test_wordpress_routes_t042.py
    tests/test_wordpress_seo_meta_t042.py tests/test_wordpress_site_link_t042.py
    tests/test_wordpress_t060.py tests/test_wordpress_t085.py -rfxX
6252 passed, 1 skipped, 44 xfailed in 310.21s
# 44 xfail: 36 mới (SL-T085-1 27, SL-T085-2 3, SL-T085-3 6); 8 có sẵn, không thuộc T-085
# (LC-T039-2 3, SL-T081-1 5). Bỏ qua 1: symlink (Windows chưa bật Developer Mode).

$ uv run pytest tests/test_soi_loi_t085.py
705 passed, 36 xfailed

$ uv run ruff check .
All checks passed!

# Cây gộp T-085 + origin/main ac1f2a4 + origin/team/T-056 5ad73eb, 18 file (08:30–08:39):
2055 passed, 7 xfailed      # 7 xfail của chính T-056

# Test mới trên code cũ (main 8ae67f8, giải nén vào thư mục nháp):
671 failed, 34 passed, 36 xfailed
# 34 qua: ca đối chứng (khóa JSON app thật gửi 14, hằng _fields 10, tải ảnh bị từ chối 4xx 3,
# ghi đè đúng ảnh, tạo nháp đủ trường, bản Python của WordPress, mẫu đường) và kiểu thân lạ T-060 đã chặn (3)
```

Script dò riêng (site giả, bản PHP, đột biến): thư mục ghi chú chung `T-085-soi-loi-scripts/` (`fakesite.py`, `probe_fields.py`, `probe_json.py`, `probe_upload.py`, `mutate085.py`; `probe_real_calls.py` của T-060). Chạy bằng `.venv` của worktree, thư mục làm việc là worktree.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–5 (mục «Kiểm từng yêu cầu»); biến thể `_fields`: hoa thường, khoảng trắng, dấu chấm con, mã hóa, lặp
- [x] Không chặn oan: 11 việc thật, trang Kết nối WordPress, mọi trang; gộp thử với `main` mới nhất và T-056
- [x] Soát R5: 1 test cũ đúng bảng trước/sau, không nới
- [x] Lỗi mới có test `xfail(strict=True)`: SL-T085-1, -2, -3
- [x] Không sửa code ứng dụng

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 3 Thấp (SL-T085-1, -2, -3; hôm nay không có đường khai thác hoặc cần website trả lời sai). **Chuyển Lá Chắn rút gọn được ngay.** Điều kiện:

- SL-T085-1 là lối vòng qua chính chốt chặn của yêu cầu 2: đề nghị sửa luôn (1 dòng) trước khi gộp; nếu không, giữ cùng hạn của LC-T060-2 (trước phiếu nào đưa giá trị tham số lấy từ dữ liệu ngoài vào `_request`).
- SL-T085-2, -3: phiếu dọn lỗi sau, trước khi hết Giai đoạn 4.

## Đề xuất

1. (Thợ Máy) SL-T085-1: `_fields` chỉ nhận `[A-Za-z0-9_.,]`.
2. (Thợ Máy, phiếu dọn sau) SL-T085-2: `_json` không để lọt lỗi lạ; SL-T085-3: `upload_media` báo «ảnh có thể đã lên thư viện Media» như nhánh gửi nháp kèm ảnh.
3. (Lá Chắn xét) Ghi nhận 1, 2.

## Câu hỏi cho chủ dự án

Không có.

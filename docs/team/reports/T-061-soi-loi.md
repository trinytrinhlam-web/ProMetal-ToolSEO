# Báo cáo T-061 · Soi Lỗi: shortcode WordPress trong chữ AI, meta SEO, alt và chú thích ảnh

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-061](../tickets/T-061-shortcode-trong-bai-ai.md) (kèm điều kiện 2 của Lá Chắn T-054, LC-T054-1) |
| Nhánh kiểm | `team/T-061`, đầu nhánh lúc nhận `7c5a405` (gốc `43d6c4a`); báo cáo Thợ Máy [T-061-tho-may.md](T-061-tho-may.md) |
| Ngày nộp | 2026-10-20 (giờ máy, +07) |
| Kết quả | Hoàn thành |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 lỗi Nghiêm trọng, Cao, Trung bình; **2 lỗi Thấp** (SL-T061-1, SL-T061-2), không chặn, ghi vào phiếu dọn. 7 file test cũ đã sửa: **không làm yếu điều kiện kiểm** (xem mục R5) |

## Tóm tắt (cho chủ dự án)

- Phần chính của phiếu **đạt**: chữ dạng `[code_snippet …]` trong nội dung bài, tiêu đề, đoạn trích, alt và chú thích ảnh trong bài, ba ô của ảnh trong thư viện Media không còn dấu `[` hay `]` thật nào khi app gửi, nên WordPress không chạy được. Tôi thử thêm khoảng 45.000 chuỗi ngẫu nhiên và 50 dạng lạ: không chuỗi nào lọt.
- Chữ thường vẫn hiện đúng: «[Lưu ý]», «[2026]», địa chỉ có `[`, tiếng Việt có dấu đều hiện y như cũ trên trang web.
- Tìm được **2 lỗi nhỏ (mức Thấp)**, không cần sửa trước khi gộp:
  - **SL-T061-1**: chữ SEO kiểu «[<>code_snippet id=1]» lọt qua bước chặn. Nếu SiteSEO làm sạch chữ bằng hàm chuẩn của WordPress (hàm này bỏ cụm «<>»), chữ còn lại thành shortcode. Chỉ nguy hiểm khi SiteSEO chạy shortcode trong tiêu đề, mô tả SEO (chưa biết, bước 4 của T-059 sẽ thử).
  - **SL-T061-2**: ở trang Kết nối WordPress, ảnh anh tự chọn tải lên nguyên file. Nếu trong file ảnh có sẵn chữ (tiêu đề, chú thích, alt do máy ảnh hay phần mềm ghi vào) dạng shortcode, WordPress lấy chữ đó làm tiêu đề, chú thích, alt của ảnh mà app không vô hiệu. Chữ này do file của chính anh, không phải AI.
- Bảy file test cũ Thợ Máy sửa: vẫn kiểm đúng ý cũ. Tôi thêm một test kiểm nguyên địa chỉ (kể cả phần sau dấu `?`) để bù chỗ các test cũ nay chỉ so phần đường.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t061.py` | Mới: 29 test qua, 6 test `xfail(strict=True)` cho SL-T061-1 (4 dạng) và SL-T061-2 (2 trường hợp) |
| `docs/team/reports/T-061-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test cũ.

## Kiểm từng yêu cầu

Mã nguồn WordPress: kho `WordPress/wordpress-develop`, nhánh `trunk`, tải ngày 2026-10-20 qua `raw.githubusercontent.com` vào thư mục nháp của phiên (không commit, **không gọi website**). PHP: `php/php-src` nhánh `master`, `ext/standard/string.c`. Dòng ghi theo file lúc tải.

| # | Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Nội dung bài không còn `[`/`]` | **Đạt** | `sanitize.py:726` (`_attrs`), `:770` (`handle_data`). Đọc hết `_Sanitizer` (`sanitize.py:703-790`): mọi chữ in ra hoặc là chuỗi cố định (tên thẻ, tên thuộc tính trong danh sách cho phép), hoặc qua `escape_shortcodes`; bình luận, CDATA, `<?…?>`, `<!DOCTYPE>` bị bỏ. Thử 36 dạng lạ (thẻ dở ở cuối chuỗi, `<[code_snippet]>`, `<pre>`, `<textarea>`, `<title>`, `<xmp>`, `<plaintext>`, `<noscript>`, `<svg>`, `<math>`, `<script>`, CDATA, `&#x005B;`, `&#0000091;`, `&#91;;`, `&#xD800;`, NUL, 5.000 dấu `[` liền nhau, `srcset` và `href` có `[`): 0 còn `[`/`]`, 0 chạy lại bị đổi. Ngẫu nhiên 40.000 chuỗi (script nháp) và 3.000 chuỗi (`test_sanitize_html_ngau_nhien_khong_con_ngoac_vuong_va_on_dinh`): 0 |
| 2 | Tiêu đề, đoạn trích bài | **Đạt** | `client.py:706` (`escape_shortcodes(strip_tags(title))`), `:714` (đoạn trích qua `sanitize_html`); `test_moi_lenh_ghi_khong_con_ngoac_vuong_tran` |
| 3 | Alt (thuộc tính có nháy) và `<figcaption>` | **Đạt** | `html.py:107-112`; ký tự vô hình, đảo chiều, U+3164 (ký tự trống Hangul) bị `plain_image_text` gỡ **trước**, `sanitize_html` vô hiệu **sau** (thử: `[code​_snippet id=1]` → `alt="&#91;code_snippet id=1&#93;"`) |
| 4 | Trường Media REST `alt_text`, `title`, `caption` | **Đạt** (đường chữ app gửi); xem SL-T061-2 cho chữ nằm sẵn trong file | `client.py:915-919` (`upload_media`), `:1140-1145` (`_describe_draft_media`) |
| 5 | Chữ SEO (tiêu đề, mô tả, từ khóa chính) | **Đạt phần lớn**; SL-T061-1 | `client.py:1401` kiểm `_has_shortcode` trên chữ gốc, chữ đã chuẩn hóa, NFKC. Thử 26 dạng: chặn đúng `[%41…]`, `[\xa0…]`, `[　…]`, ngoặc toàn khổ, `[́…]` (dấu tổ hợp), `[﻿…]`, `[ᅟ…]`, `[\U000e0020…]`; cho qua đúng `[ 2026 ]`, `[ %41code_snippet]` (sau khi WordPress bỏ `%41` vẫn là `[ code…`, không phải shortcode). Lọt: `[<>…]`, `[<1>…]`, `[<=>…]`, `[<.>…]` |
| 6 | Dạng: gạch nối/gạch dưới, `[[tên]]`, trong thuộc tính có nháy, ký tự vô hình/đảo chiều, `&#91;…&#93;`, `&lsqb;`, `&#x5B;`, toàn khổ, lọc 2 lần | **Đạt** | `NASTY` (14 dạng, `tests/test_soi_loi_t061.py:216`) chạy qua **mọi** lệnh ghi (`create_draft`, `upload_media`, `set_featured_image`, `create_draft_with_images`): duyệt mọi chữ trong JSON, địa chỉ, header của từng lệnh, 0 còn `[`/`]`. Ngoặc toàn khổ `［…］` đi nguyên (WordPress không đọc là `[`). Lọc 2 lần: mọi test đều kiểm `sanitize_html(out) == out` |
| 7 | `_fields` cố định cho 6 lệnh ghi, câu trả lời không có `content.rendered` | **Đạt** | `client.py:43-49`, `:720`, `:842-846`, `:878-883`, `:922-928`, `:955`, `:1147-1149`. `test_moi_lenh_ghi_wp_v2_deu_co_fields_an_toan`: chạy cả 6 đường (8 lệnh POST), mọi lệnh POST tới `wp/v2` có đúng một `_fields`, chỉ gồm trường không dựng bằng `the_content`/`the_excerpt`. WordPress chỉ dựng `content.rendered` khi trường được hỏi: `class-wp-rest-posts-controller.php:1998-2006`; ảnh: `description` `:1461-1466`, `caption` `:1469-1478` (attachments controller) |
| 8 | Không phá chữ người đọc thấy | **Đạt** | `test_chu_thuong_ngau_nhien_nguoi_doc_van_thay_nguyen` (2.000 chuỗi có `[]()\:;!*_#&<>"'`, tiếng Việt, xuống dòng: trình duyệt đọc ra đúng chữ gốc); `test_ngoac_vuong_trong_the_khac_va_dia_chi_van_hien_dung` («[Lưu ý]» trong `<h2>`, `<blockquote><em>`, `<td>`; `href` có `?q=[cua-sat]&p[]=1`; `src` địa chỉ IPv6 `https://[2001:db8::1]/…`). Markdown đã vô hiệu từ trước («[Gọi thợ](…)») hiện nguyên chữ (test của Thợ Máy) |
| 9 | WordPress hiện `&#91;` thành `[` bình thường | **Đạt** (đọc mã nguồn) | Bộ lọc `the_content` chạy trước `do_shortcode` (`default-filters.php:201-208`: block hooks, `do_blocks`, `wptexturize`, `wpautop`, `shortcode_unautop`, `prepend_attachment`, `wp_replace_insecure_home_url`) không giải mã mã ký tự. `do_shortcode` trả nguyên khi không có `[` (`shortcodes.php:250-252`). Khi `do_shortcode` có chạy (plugin khác chèn `[` vào cùng bài), `do_shortcodes_in_html_tags` đổi `&#91;` của app thành `&#091;` trước (`:472-477`), nên `unescape_invalid_shortcodes` (`:580-589`) không biến nó thành `[`. Trình duyệt hiện `&#91;`, `&#091;` đều là `[` |
| 10 | Điều kiện Lá Chắn T-054, thử độc lập 1, 2, 4 | **Đạt** | Thử 1 (6 dạng qua alt/chú thích): nay đều `&#91;…`, kể cả 2 dạng có ký tự vô hình. Thử 2: `sanitize_html('<p>&#91;code_snippet id=1&#93;</p>')` → `<p>&#91;code_snippet id=1&#93;</p>` (không còn giải mã). Thử 4: lệnh tạo nháp, đặt ảnh đại diện có `_fields=id,status,title,link,featured_media`, không có `content` |
| 11 | Gỡ `xfail` SL-T054-2 không đổi điều kiện | **Đạt** | `test_soi_loi_t054.py:488-503`: điều kiện `_shortcode_reached` giữ nguyên; đã thử 2 đầu vào đi đường **không ném lỗi** (không qua oan nhánh `except`): nội dung gửi có `&#91;code_snippet…` |
| 12 | SL-T054-1 vẫn `xfail` đúng lý do | **Đạt** | `--runxfail`: hỏng ở `test_soi_loi_t054.py:475` vì còn `\:` trong alt (lỗi dấu `\`), không phải vì T-061 |

## R5: 7 file test cũ Thợ Máy sửa

Đọc `git diff origin/main...HEAD -- tests/` từng chỗ.

| File:dòng | Thay đổi | Ý kiến |
|---|---|---|
| `test_soi_loi_t042.py:423-424` (`test_base_url_cannot_turn_allowed_route_into_another`) | So `path_url.split("?")[0]` | **Không yếu đi** với 3 dạng `base_url` đang thử: phần tấn công (`#`, `?rest_route=…`, `/purge?`) đều nằm **trước** đường `/wp-json/wp/v2/posts`, nên phần đường vẫn khác và test vẫn bắt. Hôm nay vòng lặp không có lệnh nào (`_is_plain_site_url` từ chối mọi `base_url` có `?`, `#`, `client.py:1460-1482`). Chỗ hở lý thuyết: một lệnh có đúng phần đường nhưng thêm tham số lạ sau `?` sẽ không bị test này bắt. Đã bù bằng `test_lenh_ghi_dung_nguyen_dia_chi_ke_ca_truy_van` (so nguyên `path_url` của 5 lệnh, kể cả truy vấn) |
| `test_soi_loi_t042_round2.py:197-198`, `test_wordpress_round2_t042.py:103-104` | So phần đường danh sách lệnh ghi | **Không yếu đi**: ý test là «chỉ có lệnh tạo nháp, không có lệnh đặt ảnh đại diện»; phần đường đủ để kiểm. Hai file đã dùng cách này ở test khác (`:232`; `:114`, `:162`) |
| `test_soi_loi_t044.py:276-277` | Lọc lệnh tạo nháp theo phần đường | **Không yếu đi**: không sửa thì `posted` rỗng và test hỏng oan; điều kiện thật (`len == 1`, `featured_media: 9`, `status: draft`) giữ nguyên |
| `test_wordpress_seo_meta_t042.py:252-254` | So phần đường | **Không yếu đi** về ý «không ghi vào `wp/v2/posts/42` khi đi đường Abilities». Nhỏ: lệnh `RUN` (Abilities) nay cũng chỉ so phần đường; các test khác cùng file vẫn so nguyên `run.path_url == RUN` (`:243`) |
| `test_soi_loi_t054.py:412`, `:478` | `alt_text == escape_shortcodes(plain)` | **Không yếu đi**: dùng chính hàm của app làm đáp án, nhưng `escape_shortcodes` đã bị ghim bằng đáp án viết tay ở `test_shortcode_t061.py` (`test_escape_shortcodes_chay_lai_khong_doi`, `assert_disarmed` mọi trường Media) và ở `test_moi_lenh_ghi_khong_con_ngoac_vuong_tran`; hàm này hỏng thì các test đó hỏng. Test `:478` vẫn `xfail` đúng lý do (mục 12) |
| `test_soi_loi_t054.py:488-503` | Gỡ 2 `xfail` SL-T054-2 | **Đúng R5**: lỗi đã sửa, điều kiện giữ nguyên (mục 11) |
| `test_soi_loi_t054.py:599-605` | Truy vấn lệnh POST: từ `{}` thành đúng `_fields` cố định | **Chặt hơn**: so bằng đúng giá trị |
| `test_wordpress_images.py:313-314`, `:331-332`, `:340` | Đáp án viết tay đổi sang `&#91;…&#93;` | **Không yếu đi**: vẫn so bằng chuỗi cố định viết tay |

## Lỗi tìm được

### SL-T061-1 (Thấp): chữ SEO «[<>tên …]» lọt qua `_seo_text`, thành shortcode sau khi WordPress bỏ thẻ

- **Tái hiện:** `client_module._seo_text("Tiêu đề SEO", "[<>code_snippet id=1]", 300)` (cũng vậy: `[<1>…]`, `[<=>gallery ids=1]`, `[<.>embed]`). Test: `test_sl_t061_1_chu_seo_co_cum_the_rong_bi_chan` (`tests/test_soi_loi_t061.py:403`, 4 dạng).
- **Mong đợi:** báo lỗi, không gửi (như mọi dạng shortcode khác).
- **Thực tế:** cho qua nguyên văn. `has_html` (`onpage/meta.py:93-95`) chỉ coi `<` + chữ cái, `/`, `!`, `?` là thẻ (`sanitize.py:41`, `:43`); `_SHORTCODE_OPEN` cần ký tự tên ngay sau `[`, mà `<` không phải. Còn `sanitize_text_field` của WordPress (`formatting.php:5776-5812`): có `<` thì `wp_pre_kses_less_than` (`:5317-5340`, giữ cụm `<…>` có `>`) rồi `wp_strip_all_tags` → `strip_tags` của PHP (`:5697`), hàm này bỏ mọi cụm từ `<` (ký tự sau không phải khoảng trắng) tới `>` (`php_strip_tags_ex`, `string.c:5251`, `:5284-5300`), kể cả `<>`. Kết quả còn `[code_snippet id=1]` liền mạch. Bản Python của hai hàm này: `test_ban_python_sanitize_text_field_cua_wordpress` (qua).
- **Mức Thấp vì:** chỉ thành vấn đề khi đủ hai điều chưa biết: SiteSEO (hay Abilities, `register_post_meta`) làm sạch chữ SEO bằng `sanitize_text_field`, **và** SiteSEO chạy shortcode trong tiêu đề, mô tả SEO (bước 4 của T-059). Chữ phải là dạng lạ `[<>…]`.
- **Gợi ý sửa (Thợ Máy):** trong `_seo_text`, xét `_has_shortcode` thêm trên dạng chữ đã bỏ cụm `<…>` theo kiểu PHP, hoặc chặn mọi `<` mà ký tự sau không phải khoảng trắng (chữ SEO không cần `<`).

### SL-T061-2 (Thấp): `upload_media` để WordPress lấy tiêu đề, chú thích, alt từ chữ nằm sẵn trong file ảnh

- **Tái hiện:** ảnh JPEG có EXIF `ImageDescription = "[code_snippet id=2]"` và XMP `Iptc4xmpCore:AltTextAccessibility = "[code_snippet id=1]"`; gọi như trang Kết nối WordPress (`app/views/wordpress.py:133`): `upload_media(file, "cong.jpg", alt_text="")` hoặc có alt. Test: `test_sl_t061_2_chu_trong_file_anh_khong_thanh_chu_media` (`tests/test_soi_loi_t061.py:487`), site giả mô phỏng thư viện Media; bản Python của bộ đọc chữ trong ảnh: `test_ban_python_doc_chu_trong_file_anh_cua_wordpress` (qua).
- **Mong đợi:** tiêu đề, chú thích, alt của ảnh trên site không có `[` trần (app ghi đè cả ba, hoặc bỏ chữ trong file).
- **Thực tế:** app gửi nguyên byte (`client.py:946`, `:953`) và chỉ ghi đè trường người dùng điền (`:915-919`, `if value`); trang Kết nối WordPress không bao giờ gửi tiêu đề, chú thích. WordPress khi tải ảnh (`class-wp-rest-attachments-controller.php:862-875`) thiếu tiêu đề, chú thích thì lấy từ file: `wp_read_image_metadata` (`wp-admin/includes/image.php:825`) đọc IPTC (`:884-907`) và EXIF `ImageDescription` (`:961-980`, ảnh JPEG/TIFF), alt lấy từ XMP qua `wp_get_image_alttext` (`:930`, `:1088`, ghi `@since 7.0.0`, đọc mọi loại ảnh) rồi ghi bằng `sanitize_text_field` (attachments controller `:906-907`, không bỏ `[`). Alt này vào `<img alt>` của trang ảnh (`prepend_attachment`, `post-template.php:1748`) và `do_shortcode` chạy (W7 của Thợ Máy); tiêu đề, chú thích thì lõi WordPress không chạy shortcode (Rủi ro 7 của Thợ Máy, chỉ nói tiêu đề, chú thích; **alt từ XMP là điểm mới**). Kiểm `--runxfail`: hỏng vì `title == "[code_snippet id=2]"`.
- **Mức Thấp vì:** chữ đến từ file người dùng tự chọn (không phải AI); alt từ XMP cần WordPress 7.0 trở lên (chưa biết bản trên site), người dùng để trống ô alt, và trang ảnh còn bật. Đường gửi nháp kèm ảnh (T-054) không bị: WebP do app dựng không có XMP, IPTC (`process.py:592`, `:709`) và luôn gửi alt, tiêu đề.
- **Gợi ý sửa (Thợ Máy):** `upload_media` luôn gửi `alt_text`, `title`, `caption` trong lệnh sửa ảnh (đã `escape_shortcodes`; chữ rỗng cũng ghi đè, `update_item` `:1003-1004`; tiêu đề lấy từ tên file khi người dùng không điền), hoặc dựng lại ảnh như T-049 trước khi tải.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t061.py --runxfail -k sl_t061
E       Failed: DID NOT RAISE WordPressError          (×4, SL-T061-1)
E           AssertionError: ('title', '[code_snippet id=2]')   (×2, SL-T061-2)

$ uv run pytest tests/test_soi_loi_t054.py --runxfail -k sl_t054_1_anh_ai
E         + Minh họa [Trước khi sửa]\: cổng sắt gỉ sét
tests\test_soi_loi_t054.py:475: AssertionError

$ uv run pytest tests/test_soi_loi_t061.py
29 passed, 6 xfailed in 4.76s

$ uv run pytest tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_sanitize.py \
    tests/test_sanitize_autolink.py tests/test_sanitize_bypass.py tests/test_sanitize_hardening.py \
    tests/test_link_escape.py tests/test_wordpress_client.py tests/test_wordpress_images.py \
    tests/test_wordpress_paging_t042.py tests/test_wordpress_published.py \
    tests/test_wordpress_round2_t042.py tests/test_wordpress_routes_t042.py \
    tests/test_wordpress_seo_meta_t042.py tests/test_wordpress_site_link_t042.py \
    tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py \
    tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t044.py tests/test_soi_loi_t054.py \
    tests/test_app_pages.py
2302 passed, 10 xfailed in 169.80s (0:02:49)

$ uv run ruff check .
All checks passed!
```

- 21 file theo phiếu giao (Windows 11, tại `ae0a553`, chỉ khác `7c5a405` ở file test mới): 0 hỏng, 0 XPASS. 10 `xfail`: 6 của tôi (SL-T061-1 ×4, SL-T061-2 ×2) và 4 có từ trước (SL-T054-1 ×1, SL-T054-3 ×3). Lần chạy trước khi thêm file của tôi (20 file, tại `7c5a405`): 2273 passed, 4 xfailed in 373.21s.
- Thử ngoài pytest (script trong thư mục nháp, không commit): `sanitize_html` 36 dạng lạ và 40.000 chuỗi ngẫu nhiên; `create_draft_with_images` 1.500 lần và `create_draft` + `upload_media` + `set_featured_image` 1.500 lần với chữ ngẫu nhiên (ghép `[`, `]`, `&#91;`, `&lsqb;`, ký tự vô hình, đảo chiều, toàn khổ, thẻ, dấu nháy): 0 lệnh có `[`/`]` trần ở địa chỉ, header hay chữ JSON; chữ SEO 26 dạng (mục 5).

## Đối chiếu tiêu chí xong

- [x] Kiểm đủ yêu cầu phiếu và điều kiện Lá Chắn T-054, có `file:dòng` và test (bảng «Kiểm từng yêu cầu»).
- [x] Lỗi tìm được có test `xfail(strict=True)` mã SL-T061-x trong `tests/test_soi_loi_t061.py`; không sửa code ứng dụng.
- [x] Ý kiến về 7 file test cũ đã sửa (mục R5): không làm yếu; một chỗ hở lý thuyết đã bù bằng test mới.
- [x] Test liên quan và `ruff check .` (mục Bằng chứng).
- [x] Báo cáo, kết luận: **ĐẠT CÓ ĐIỀU KIỆN**.

## Rủi ro và điểm cần chú ý

1. Đồng ý với Rủi ro 1–8 của Thợ Máy. Bổ sung (suy luận từ mã nguồn, **chưa thử**): khi người dùng chèn ảnh từ thư viện Media vào một bài khác trong trang quản trị, chú thích, alt dạng `&#91;…&#93;` hoặc hiện nguyên văn mã ký tự (trình soạn khối), hoặc bị trình soạn cổ điển đọc thành `[` rồi lưu lại `[` trần (cùng kiểu Rủi ro 1). Cần người bấm, và người đó thấy rõ chữ `[code_snippet …]`.
2. Tiêu đề bài có ngoặc vuông (AI hay viết «… [Cập nhật 2026]») lưu thành `&#91;Cập nhật 2026&#93;`. Trang web, danh sách bài quản trị hiện đúng `[` (in ra không mã hóa lại). Ô tiêu đề của trình soạn khối có hiện mã ký tự không: chưa biết, nên xem ở T-059.
3. Lệnh ghi SEO qua Abilities (`POST …/seo-data-update/run`) không có `_fields` (không phải đối tượng `wp/v2`); câu trả lời do SiteSEO dựng, tôi không đọc mã SiteSEO. Chữ SEO đã bị chặn trước khi gửi nên không có `[` liền tên đi qua đường này (trừ SL-T061-1).
4. SL-T061-1 phụ thuộc cách SiteSEO làm sạch và có chạy shortcode trong meta hay không: nếu bước 4 của T-059 xác nhận SiteSEO **không** chạy shortcode trong meta thì lỗi này không còn hậu quả.

## Đề xuất

1. **Chỉ Huy:** đưa SL-T061-1, SL-T061-2 vào phiếu dọn (cùng T-071 hoặc phiếu mới), không chặn gộp T-061. Sửa xong thì 6 test `xfail` thành XPASS, chỉ cần xóa 2 dòng `@pytest.mark.xfail`.
2. **Lá Chắn:** xét mức của SL-T061-1, SL-T061-2; xét Rủi ro 1, 2 ở trên cùng Rủi ro 1, 5 của Thợ Máy.
3. **T-059 (thử thật):** ở bước 4, ghi rõ SiteSEO có chạy shortcode trong tiêu đề, mô tả SEO không (dùng shortcode vô hại `[caption]thu[/caption]` như Thợ Máy đề xuất); mở bài nháp có tiêu đề «[Lưu ý]» trong trình soạn khối xem ô tiêu đề hiện gì.

## Câu hỏi cho chủ dự án

Không có.

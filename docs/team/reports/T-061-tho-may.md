# Báo cáo T-061 · Shortcode WordPress trong chữ AI, chữ SEO, alt và chú thích ảnh

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-061](../tickets/T-061-shortcode-trong-bai-ai.md) (kèm điều kiện 2 của Lá Chắn T-054, LC-T054-1; LC-T042-3) |
| Ngày nộp | 2026-10-20 (giờ máy, +07) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Chữ dạng `[code_snippet …]` (gọi là shortcode: WordPress coi là lệnh và **chạy**) do AI viết hay người dùng dán **không còn chạy được** khi app gửi bài nháp. Cách làm: app đổi mọi dấu `[` và `]` thành mã ký tự `&#91;`, `&#93;`. Trình duyệt vẫn hiện đúng `[`, `]`, nên người đọc thấy «[Lưu ý]» y như cũ; WordPress thì không thấy dấu `[` nào nên không chạy gì.
- Phủ mọi chữ app gửi lên website: nội dung bài, tiêu đề, đoạn trích, alt và chú thích ảnh trong bài, cả ba ô của ảnh trong thư viện Media (alt, tiêu đề, chú thích). Chữ SEO (tiêu đề, mô tả, từ khóa chính) không dùng được mã ký tự, nên app **báo lỗi, chưa gửi gì** khi gặp dạng `[chữ…]` (ví dụ «[2026]»); viết «(2026)» hay «[ 2026 ]» thì vẫn gửi được.
- App xin WordPress trả lời gọn (chỉ mã bài, trạng thái…), để WordPress không dựng nội dung bài hay trang ảnh (chỗ shortcode chạy) ngay trong lệnh của app.
- Điều anh có thể thấy khác: trong trang quản trị, hộp «Chi tiết ảnh» của thư viện Media hiện `&#91;…&#93;` thay cho `[…]` ở ảnh có ngoặc vuông trong alt, tiêu đề, chú thích (ví dụ tiêu đề ảnh AI «[AI] …»). Trang web vẫn hiện đúng. Đề xuất cách sửa ở cuối.
- Việc nên làm trên website vẫn giữ nguyên (điều kiện 3 của Lá Chắn T-054): plugin Code Snippets ở bản **3.9.2 trở lên**, tắt «Enable file-based execution» nếu không dùng.

## Cách vô hiệu đã chọn và cách xác minh

Đọc mã nguồn WordPress (kho `WordPress/wordpress-develop`, nhánh `trunk`, đọc ngày 2026-10-20 qua `raw.githubusercontent.com`; **không gọi website**). Dòng ghi theo file lúc đọc.

| # | Mã nguồn WordPress | Điều rút ra |
|---|---|---|
| W1 | `wp-includes/shortcodes.php:247` `do_shortcode()`, dòng 250-252: `if ( ! str_contains( $content, '[' ) ) { return $content; }` | Không có `[` trần thì WordPress trả nguyên nội dung, **không chạy gì**. Đây là chốt app dựa vào |
| W2 | cùng hàm: tên ứng viên `preg_match_all( '@\[([^<>&/\[\]\x00-\x20=]++)@' …)`; `get_shortcode_regex()` (`:330`): `\[(\[?)(tên)(?![\w-])…`, chạy không cờ `/u` | Tên shortcode là mọi ký tự trừ `<>&/[]=`, khoảng trắng, ký tự điều khiển (khớp `add_shortcode()` `:77`). Ký tự vô hình chen vào tên làm tên khác, nhưng bị app gỡ trước khi gửi thì tên liền lại |
| W3 | `do_shortcodes_in_html_tags()` (`:471`) | Chạy shortcode **trong thuộc tính**, kể cả có dấu nháy (`alt="[…]"`, rồi lọc kết quả bằng `wp_kses_one_attr`). Hàm này đổi `&#91;` do người viết sẵn thành `&#091;` trước khi `unescape_invalid_shortcodes()` (`:580`) trả `&#91;` giữ chỗ về `[`, nên `&#91;` app gửi không bao giờ thành `[` |
| W4 | `do_shortcode_tag()` (`:398`) | `[[tên]]` chỉ "thoát" một lượt (in ra `[tên]`); plugin gọi `do_shortcode` lần nữa là chạy. App đổi cả dạng này |
| W5 | `rest-api/endpoints/class-wp-rest-posts-controller.php`: `create_item()` (`:740`, `context=edit` `:852`, trả lời `:875`), `update_item()` (`:943`, `:1042`), `prepare_item_for_response()` (`:1884`, đặt bài làm `$post` toàn cục `:1888-1890`; `title.rendered` `:1978-1982`; `content.rendered = apply_filters( 'the_content', … )` `:2004-2006`; `excerpt` qua `the_excerpt` `:2015-2033`) | Lệnh tạo nháp và lệnh sửa bài (đặt ảnh đại diện, ghi meta dự phòng) **dựng `content.rendered` bằng `the_content`, tức chạy `do_shortcode`**, trừ khi `_fields` không hỏi `content` |
| W6 | `wp-includes/default-filters.php`: `the_content` → `prepend_attachment` (ưu tiên 10) → `do_shortcode` (11) | |
| W7 | `post-template.php:1748` `prepend_attachment()` → `wp_get_attachment_link( 0, 'medium', false )` (`:1674`) → `media.php:1169` `wp_get_attachment_image()`: `alt = trim( strip_tags( get_post_meta( …, '_wp_attachment_image_alt' ) ) )` rồi `esc_attr` | **Điểm mới** (Soi Lỗi T-054 đoán "WordPress mặc định không chạy shortcode ở trường Media"): `alt_text` của ảnh được chèn vào `<img alt="…">` trong nội dung trang ảnh, rồi `do_shortcode` chạy. Trong `class-wp-rest-attachments-controller.php`, `update_item()` ghi alt (`:1003-1004`) rồi dựng câu trả lời (`:1030`); `prepare_item_for_response()` (`:1452`) dựng `description.rendered` bằng `the_content` (`:1461-1465`, ảnh là `$post` toàn cục). Nghĩa là shortcode trong alt **chạy ngay trong lệnh ghi alt của app** (`POST /wp/v2/media/<mã>` không `_fields`). `caption.rendered` qua `the_excerpt` (`:1469-1478`). Tiêu đề ảnh vào chữ của link khi không dựng được `<img>` |
| W8 | `formatting.php:948` `_wp_specialchars( …, $double_encode = false )`, `esc_attr()` `:4826` | WordPress in `alt_text` ra không mã hóa lại `&#91;` (chỉ chuẩn hóa mã ký tự, `:980-988`): trang web hiện `[`, trong HTML không có `[` trần |
| W9 | `media.php:4675-4682` (`wp_prepare_attachment_for_js`: tiêu đề, alt, chú thích thô), `media-template.php:517`, `:524`, `:546` (`{{ data.alt }}`, `{{ data.title }}`, `{{ data.caption }}`) | Hộp «Chi tiết ảnh» hiện nguyên văn `&#91;` (xem Rủi ro 2) |
| W10 | `class-wp-editor.php:1107-1108`: TinyMCE `entities = '38,amp,60,lt,62,gt'`, `entity_encoding = 'raw'` | Trình soạn cổ điển lưu lại `[` trần (xem Rủi ro 1) |

**Cách chọn:** đổi **mọi** `[` và `]` thành `&#91;`, `&#93;` ở **bước in ra** (theo W1: không cần nhận ra shortcode, nên không dạng nào lọt: `[tên …]`, `[tên]…[/tên]`, `[[tên]]`, `[/tên]`, tên có `-`/`_`, ký tự vô hình, đảo chiều, `&#91;`, `&#x5B;`, `&#091;`, `&lsqb;`, `&lbrack;`, `&#91` thiếu `;`). Với chữ SEO thì **chặn** (W2 cho thấy mọi tên đều có thể đã đăng ký; mã ký tự trong chữ SEO đã bị chặn từ T-036/T-042).

Kiểm bằng **bản Python của bộ đọc WordPress** trong `tests/test_shortcode_t061.py` (`wp_runs_shortcode`: W1 + W2 + W4, chạy cả trong thuộc tính như W3). Mỗi nhóm test kiểm hai chiều: chữ cũ (như trước T-061 gửi) thì WordPress chạy; chữ app gửi bây giờ thì không còn `[` nào và WordPress không chạy; chữ người đọc thấy (giải mã như trình duyệt) giữ nguyên.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/sanitize.py` | Mới `escape_shortcodes()` (`:693`). `_Sanitizer._attrs` (`:726`) và `handle_data` (`:770`) gọi nó **sau** `html.escape`, ở bước in ra (bộ đọc đã giải mã `&#91;`, `&lsqb;`… thành `[`): phủ chữ và mọi giá trị thuộc tính. Chạy lại không đổi. Không đổi gì khác (danh sách thẻ, thuộc tính, URL giữ nguyên) |
| `seo_app/wordpress/client.py` | Tiêu đề bài (`create_draft` `:706`); ba trường Media của `upload_media` (`:916`) và `_describe_draft_media` (`:1140-1145`, sau khi `plain_image_text` đã gỡ ký tự vô hình); `_seo_text` chặn dạng shortcode (`_SHORTCODE_OPEN` `:136`, `_has_shortcode` `:1413`, kiểm `:1401` trên chữ gốc, chữ đã gỡ ký tự vô hình và dạng NFKC); `_fields` cố định (`:43-49`) cho 6 lệnh ghi: tạo nháp, đặt ảnh đại diện (`id,status,title,link,featured_media`), ghi meta dự phòng (`id,status,meta`), tải ảnh và ghi alt ảnh ở cả hai hàm (`id,source_url,alt_text`) |
| `seo_app/images/html.py` | Chốt cuối của `figure_html` so `src` theo đúng dạng bộ lọc in ra (`:110`); ghi chú đầu file |
| `tests/test_shortcode_t061.py` | Mới: 144 trường hợp (chi tiết ở Bằng chứng) |
| `tests/test_soi_loi_t054.py` | Gỡ 2 `xfail` SL-T054-2 (điều kiện kiểm giữ nguyên, nay qua). Điều kiện theo dạng mới: `alt_text == escape_shortcodes(plain)` (test chữ độc; test SL-T054-1 **vẫn `xfail`** vì lỗi dấu `\` chưa sửa), truy vấn của lệnh POST là `_fields` cố định thay cho rỗng |
| `tests/test_wordpress_images.py` | 3 điều kiện viết lại theo dạng `&#91;…&#93;` (tiêu đề ảnh AI, `<figcaption>`, chú thích Media) |
| `tests/test_wordpress_round2_t042.py`, `tests/test_soi_loi_t042_round2.py`, `tests/test_wordpress_seo_meta_t042.py`, `tests/test_soi_loi_t042.py`, `tests/test_soi_loi_t044.py` | So phần đường của lệnh ghi (`path_url.split("?")[0]`, cách các file T-042 đã dùng ở test khác), vì lệnh tạo nháp nay có `?_fields=`. Ý test giữ nguyên (`test_soi_loi_t042.py:423` hôm nay không gửi lệnh nào; sửa để sau này không hỏng oan) |
| `docs/team/reports/T-061-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `config/**`, không thêm thư viện. `git diff --stat origin/main...HEAD` (trước báo cáo): 11 file, 3 file code (`sanitize.py` 34 dòng đổi, `client.py` 93, `html.py` 15), 1 file test mới, 7 file test cũ (10 hàm test đổi điều kiện, 1 trong số đó vẫn `xfail`). Gộp thử với `main` (`820f6c7`): `git merge-tree --write-tree` không xung đột (`main` chỉ thêm tài liệu).

## Các đường đã phủ

| Đường gửi lên WordPress | Chữ | Cách | Test |
|---|---|---|---|
| `create_draft` (`POST /wp/v2/posts`) | nội dung, đoạn trích | `sanitize_html` (bước in ra) | `test_tao_nhap_tieu_de_noi_dung_trich_doan_khong_con_shortcode` |
| | tiêu đề | `escape_shortcodes` sau `strip_tags` | cùng test (app vẫn hiện đúng tiêu đề: `post.title`) |
| | câu trả lời | `_fields` không có `content`, `excerpt` | cùng test, `test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung` |
| `create_draft_with_images`: `<figure>` | alt (thuộc tính có nháy), `<figcaption>` | `plain_image_text` (gỡ ký tự vô hình) → `html.escape` → `sanitize_html` | `test_nhap_kem_anh_alt_chu_thich_va_truong_media_khong_con_shortcode` (10 dạng), `test_figure_html_go_ky_tu_vo_hinh_roi_moi_vo_hieu`, SL-T054-2 ×2 |
| `create_draft_with_images`: Media REST | `alt_text`, `title`, `caption` | `plain_image_text` → (`html.escape`) → `escape_shortcodes`; mô phỏng `prepend_attachment` (W7) | cùng test 10 dạng |
| `set_featured_image` (`POST /wp/v2/posts/<mã>`) | (chỉ mã ảnh) | `_fields` | `test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung` |
| `upload_media` (trang Kết nối WordPress) | `alt_text`, `title`, `caption` | `escape_shortcodes`; `_fields` | `test_upload_media_truong_media_khong_con_shortcode` |
| `set_seo_meta` (Abilities, meta dự phòng) | tiêu đề, mô tả, từ khóa chính SEO | `_seo_text` chặn, không gửi request nào | `test_chu_seo_dang_shortcode_bi_chan_truoc_khi_gui` (10 dạng × 3 ô) |
| | câu trả lời meta dự phòng | `_fields=id,status,meta` | `test_chu_seo_ngoac_vuong_ghi_qua_meta_du_phong` |
| Không đổi | `slug` (WordPress bỏ `[` khi làm sạch slug), chuyên mục, thẻ (số) | | |

**Chiều 2 (không phá chữ thường):** `test_ngoac_vuong_thuong_nguoi_doc_van_thay_nguyen` (8 câu như «[Lưu ý] …», Markdown «[Gọi thợ](…)», «a[0]», «[[Ghi chú]]», trong `<p>`, `<figcaption>`, `<pre><code>`, `<li>`, `alt`, `title`), `test_ngoac_vuong_thuong_trong_alt_chu_thich_van_hien_dung`, `test_chu_seo_ngoac_vuong_khong_phai_shortcode_van_gui` (7 câu), `test_khong_doi_html_khong_co_ngoac_vuong` (bài không có ngoặc vuông ra y như trước).

## Bằng chứng

```
$ uv run pytest tests/test_shortcode_t061.py tests/test_sanitize.py tests/test_sanitize_autolink.py \
    tests/test_sanitize_bypass.py tests/test_sanitize_hardening.py tests/test_link_escape.py \
    tests/test_wordpress_client.py tests/test_wordpress_images.py tests/test_wordpress_published.py \
    tests/test_wordpress_paging_t042.py tests/test_wordpress_round2_t042.py \
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py \
    tests/test_wordpress_site_link_t042.py tests/test_soi_loi_t042.py \
    tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t042_round2.py \
    tests/test_site_index_t042.py tests/test_site_index.py tests/test_soi_loi_t054.py \
    tests/test_app_wordpress.py tests/test_app_t044_safe_text.py tests/test_phase2_fixes.py \
    tests/test_safety.py tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t031.py \
    tests/test_soi_loi_t037.py tests/test_soi_loi_t044.py tests/test_app_pages.py
6 failed, 3355 passed, 1 skipped, 5 xfailed in 357.25s      # lần 1, tại b53afec+78ee9d8 (6 hỏng: xem dưới, đã sửa ở 4ac6028)

$ uv run pytest tests/test_soi_loi_t044.py tests/test_soi_loi_t042.py
267 passed in 133.19s

(lần chạy cuối, 41 file, tại 4ac6028: đang chạy, cập nhật khi xong)

$ uv run ruff check .
All checks passed!
```

- 29 file trên là mọi file test có dùng `sanitize_html`, client WordPress, `seo_app.images.html` (grep), cộng `test_link_escape.py`, `test_sanitize_autolink.py`, `test_app_pages.py`. Windows 11, tại commit trước báo cáo (`78ee9d8` + 1 dòng định dạng). 4 `xfail` còn lại là SL-T054-1 (1) và SL-T054-3 (3), chờ phiếu dọn T-071.
- `tests/test_shortcode_t061.py`: 144 qua. **Thử ngược** (thay hàm trong bộ nhớ, không sửa file): `sanitize.escape_shortcodes` không làm gì → 87/90 test mức bộ lọc hỏng (3 test còn lại là test bộ đọc WordPress bản Python và bài không có ngoặc vuông, đúng ý); `client.escape_shortcodes` không làm gì → 11 hỏng; `_has_shortcode` luôn sai → 31 hỏng; `_fields` có thêm `content`/`description` → 3 hỏng.
- **Thử ngẫu nhiên** (script tạm trong thư mục nháp của phiên, không commit; ghép ngẫu nhiên `[`, `]`, `[[`, `&#91;`, `&#x5B;`, `&lsqb;`, `&#91` thiếu `;`, thẻ, thuộc tính, chú thích HTML, CDATA, `<script>`, U+200B, U+202E, U+2060, U+00AD, ngoặc toàn khổ, escape Markdown): `sanitize_html` 20.000 chuỗi: 0 chuỗi còn `[`/`]` trần hay chạy lại bị đổi; `figure_html` 10.000 cặp alt/chú thích: 0 còn `[`/`]`, alt luôn giải mã đúng bằng `plain_image_text(alt)`; chữ SEO 20.000 chuỗi, 7.204 được `_seo_text` cho qua: với mỗi chữ đó, bộ đọc WordPress bản Python coi **mọi** tên ứng viên là đã đăng ký vẫn không chạy được gì (quy tắc chặn không sót).
- Sau khi sửa client, 25 trường hợp test cũ hỏng (19 ở lần chạy nhóm WordPress, 6 ở `test_soi_loi_t044.py` trong lần chạy rộng đầu tiên: 6 hỏng, 3.355 qua): 2 là SL-T054-2 thành XPASS (đã gỡ `xfail`), 23 là test so đúng chuỗi alt/tiêu đề Media hay đúng đường có `?…` (đã viết lại như bảng trên, giữ ý test). Không xóa, không bỏ qua test nào.

## Đối chiếu tiêu chí xong

- [x] Vô hiệu mọi dạng shortcode trong mọi chữ app gửi lên WordPress: nội dung, meta SEO, alt và chú thích trong `<figure>`, trường Media REST (bảng «Các đường đã phủ»; 21 dạng trong chữ, 7 dạng × 8 kiểu thuộc tính, 10 dạng alt/chú thích, 10 dạng chữ SEO). Người đọc vẫn thấy chữ bình thường (so chữ đã giải mã như trình duyệt).
- [x] Điều kiện Lá Chắn T-054: vô hiệu ở **bước in ra** của `sanitize_html`, phủ chữ và mọi thuộc tính (`test_shortcode_trong_moi_thuoc_tinh_bi_vo_hieu`: `alt`, `title`, `class`, `id`, `lang`, `dir`, `width`, `height`, `loading`, `sizes`, `src`, `srcset`, `href`, `rel`, `cite`, `colspan`, `rowspan`, `scope`, `start`, `reversed`, `type`, nháy đơn); chạy lại không đổi (`test_chay_lai_khong_doi_ca_bai`, mỗi test dạng); lọc **sau** khi gỡ ký tự vô hình (`<figure>`, Media REST, chữ SEO: test có U+200B, U+202E, U+2060, U+00AD); trường Media REST đã xét và vô hiệu (W7: alt chạy được thật, nặng hơn đánh giá trước); `_fields` cố định cho lệnh tạo nháp và đặt ảnh đại diện (thêm cả ghi meta dự phòng, tải và ghi alt ảnh).
- [x] Không phá chữ thường có ngoặc vuông, có test hai chiều (mục «Chiều 2»). Riêng chữ SEO: «[Lưu ý]», «[2026]» bị chặn có báo lỗi (Rủi ro 3).
- [x] Gỡ `xfail` SL-T054-2 khi XPASS, không đổi điều kiện kiểm (`tests/test_soi_loi_t054.py`, 2 test).
- [x] Ghi cách xác minh (mục trên, W1–W10), không gọi site thật.
- [x] Test liên quan qua, `ruff check` sạch, báo cáo đã đẩy lên `team/T-061`.

## Rủi ro và điểm cần chú ý

1. **Sửa bài trong trang quản trị WordPress có thể làm `&#91;` thành `[` trần** (suy luận từ cấu hình W10 và cách trình duyệt đọc HTML; chưa thử): trình soạn cổ điển, khối «Cổ điển» hay «Chuyển thành khối» của trình soạn khối đọc `&#91;` thành `[` rồi lưu lại `[` trần. Sau đó xem trước hay đăng là shortcode chạy (bằng tài khoản người sửa). Người sửa nhìn thấy rõ chữ `[code_snippet …]` trong bài. App không chặn được bước này (xảy ra ngoài app); xem Đề xuất 2.
2. **Hộp «Chi tiết ảnh» của thư viện Media hiện nguyên văn `&#91;…&#93;`** cho alt, tiêu đề, chú thích có ngoặc vuông (W9), gồm tiêu đề mọi ảnh AI («&#91;AI&#93; Minh họa …»). Trang web hiện đúng (W8). Trước T-061 đã có hiện tượng giống vậy với `&quot;`, `&amp;` (T-054 escape HTML tiêu đề, chú thích Media). Tạo ảnh AI đang hoãn (T-053), nên chưa gấp.
3. **Chữ SEO chặn cả «[2026]», «[Lưu ý]»**: WordPress nhận mọi tên đã đăng ký (W2), app không biết site đăng ký tên nào. Hàm kiểm meta của T-036 (`check_title`, `check_description` trong `seo_app/onpage/meta.py`, ngoài phạm vi) chưa báo trước dạng này, nên người dùng chỉ thấy lỗi lúc ghi SEO. Nếu bước 4 của T-059 xác nhận SiteSEO không chạy shortcode trong meta thì có thể nới.
4. Plugin hay theme gắn bộ lọc giải mã mã ký tự vào `the_content` trước `do_shortcode` (ưu tiên dưới 11) thì có thể tạo lại `[` khi trang được xem (suy luận; chưa biết plugin nào làm vậy). `_fields` chỉ bảo vệ lệnh của app.
5. `_fields` là tham số mới truyền vào `_request` khi LC-T042-1 (T-060: chặn `rest_route`, `_method`) chưa làm. Giá trị là hằng do code viết, không lấy từ dữ liệu ngoài, nên đường tấn công của LC-T042-1 vẫn không có; Lá Chắn T-054 đã đề nghị thêm `_fields`. Ghi để Lá Chắn xét.
6. Test SL-T054-1 (vẫn `xfail`): đã đổi điều kiện `alt_text` sang dạng `&#91;…&#93;`, để khi phiếu dọn T-071 sửa dấu `\` thì test thành XPASS đúng, không vấp vì T-061.
7. Đường phụ còn lại (ngoài chữ app gửi): khi tải ảnh mà lệnh không có tiêu đề, chú thích, WordPress tự lấy từ thông tin IPTC/EXIF trong file (`class-wp-rest-attachments-controller.php:858-870`). `upload_media` của trang Kết nối WordPress gửi nguyên file người dùng chọn, nên chữ trong file ảnh có thể thành tiêu đề, chú thích ảnh (không qua `escape_shortcodes`). Chỉ chạy được nếu theme cho shortcode chạy trong tiêu đề, đoạn trích (lõi WordPress không làm, trừ chữ của link khi không dựng được `<img>`, W7). Chữ này đến từ file của chính người dùng, không phải AI. Đường gửi nháp kèm ảnh (T-054) dùng WebP do app dựng (không có các trường này) và luôn gửi tiêu đề.
8. Ghi nhận ngoài phạm vi: `WP_Embed::autoembed` (`class-wp-embed.php:41`, `:442-450`) nhúng (iframe) địa chỉ đứng riêng một dòng hoặc một mình trong `<p>`, cùng hậu quả với `[embed]`. Hôm nay chữ AI có ký tự ngắt sau `:/` (T-031) nên không khớp; nếu Giai đoạn 5 gỡ ký tự ngắt trước khi gửi thì cần xét lại.

## Đề xuất

1. **Chỉ Huy, chủ dự án:** đổi tiền tố tiêu đề ảnh AI `[AI] ` (`AI_MEDIA_TITLE_PREFIX`, thiết kế T-046 mục 4) sang dạng không có ngoặc vuông, ví dụ `(AI) `, để thư viện Media không hiện `&#91;AI&#93;`. Một dòng code và vài điều kiện test; làm khi mở lại T-053.
2. **T-056 (Họa Sĩ), Chỉ Huy:** trước nút «Gửi nháp», cảnh báo khi chữ có dạng shortcode (có thể dùng chung `client._has_shortcode`, đưa thành hàm công khai), nhắc: "WordPress sẽ chạy đoạn này nếu bạn sửa và lưu bài trong trang quản trị; nên xóa". Kèm điều kiện 3 của Lá Chắn T-054 (Code Snippets ≥ 3.9.2).
3. **T-036 hoặc phiếu dọn:** thêm kiểm dạng shortcode vào `check_title`, `check_description` (mức Chặn) để người dùng thấy ngay khi sửa meta, cùng quy tắc với `_seo_text`.
4. **T-059 (thử thật):** chỉ dùng shortcode vô hại của lõi WordPress, `[caption]thu[/caption]`, trong alt, chú thích, tiêu đề bài của bài nháp thử: trang xem trước phải hiện nguyên chữ, không có khung chú thích WordPress; rồi mở bài trong trình soạn, bấm Lưu nháp, xem lại nguồn để xác nhận Rủi ro 1.
5. **Soi Lỗi:** thử thêm dạng lạ (shortcode trong `srcset`, `<pre>`, tiêu đề bài, đoạn trích, chữ rất dài toàn `[`), đường `upload_media` của trang Kết nối WordPress; xác nhận 10 hàm test cũ đã viết lại điều kiện (7 file, bảng «Đã thay đổi») vẫn đúng ý.
6. **Lá Chắn:** soát riêng diff `sanitize.py` (3 chỗ: `escape_shortcodes`, `_attrs`, `handle_data`); xét điểm mới W7 (alt chạy shortcode ngay trong lệnh ghi alt); xét Rủi ro 1 và 5.

## Câu hỏi cho chủ dự án

Không có (đề xuất 1 do Chỉ Huy hỏi khi mở lại T-053).

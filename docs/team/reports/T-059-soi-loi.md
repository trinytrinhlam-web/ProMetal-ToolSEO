# Báo cáo T-059 bước 7 · Siết client WordPress theo kết quả thử thật · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-059](../tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md), bước 7 |
| Nhánh | `team/T-059` (gốc `main` `4671104`, kiểm trên đầu nhánh `d0fbbd8`) |
| Ngày nộp | 2026-10-28 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T059-1, có từ trước, không bắt buộc sửa trước Lá Chắn). Soát R5: **đạt** |

## Tóm tắt (cho chủ dự án)

- **Ghi SEO lên website:** app nay chỉ báo «đã ghi» khi website trả lời đúng khuôn thật đã thấy ngày 27/10. Tôi thử 34 kiểu trả lời lạ (thiếu phần đọc lại, sai kiểu, lệch một ký tự, «đã ghi» dạng chữ hay số…): không kiểu nào làm app báo «đã ghi» sai. Khuôn thật vẫn được nhận.
- **Ảnh trong bài:** mỗi ảnh nay ghi sẵn «danh sách cỡ ảnh» chỉ có file đầy đủ 1600 px (còn GPS). Tôi đọc mã WordPress lõi và dựng lại phần đó: WordPress thấy danh sách này thì **không** thêm các bản thu nhỏ mất GPS, kể cả khi website gắn lớp `wp-image-…` như lần thử 27/10. Khung ảnh, alt, chú thích, chặn shortcode giữ nguyên.
- **1 lỗi nhỏ (Thấp), có từ trước:** SiteSEO tự làm sạch chữ khi lưu (dấu «< » thành `&lt;`, «%» kèm 2 chữ/số kiểu «10%BE» bị cắt, dấu «\» bị bỏ). Khi tiêu đề, mô tả có các ký tự đó, website **đã ghi** nhưng app báo «không thành công, hãy chép tay». Không hỏng gì; chỉ báo sai và làm bạn chép tay thừa. Nên sửa ở phiếu sau.
- Vẫn cần **thử lại trên website thật** một bài nháp một ảnh (như Thợ Máy đề xuất): xem nguồn trang chỉ còn file đầy đủ trong `srcset`.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t059.py` | Mới: 76 ca (71 qua, 5 `xfail(strict=True)` của SL-T059-1). Khuôn trả lời, site giả SiteSEO 1.4.2 làm sạch chữ, bản Python của WordPress (`wp_filter_content_tags`, `sanitize_text_field`, `stripslashes`) đều viết riêng, không dùng lại của Thợ Máy |
| `docs/team/reports/T-059-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Việc 1 · `_ability_confirms`

**Đạt** (`seo_app/wordpress/client.py:1865-1893`): chỉ nhận `updated is True`, `post` là dict, mọi trường đã gửi có trong `post` đúng từng chữ; `code` có mặt hay `success` có mặt mà khác `True` thì chưa ghi.

- Khuôn thật theo ghi chú phiếu 27/10 (`{"updated": true, "post": {title, description, canonical_url: null, focus_keyphrase, seo_score: null, robots{5 cờ false}, social{6 null}}}`), điểm SEO là số, có thêm khóa `message`, có `success: true` đi kèm: **nhận** (`test_khuon_that_va_khoa_la_vo_hai_duoc_nhan`, 4 ca).
- 34 khuôn lạ: **chưa ghi** (`test_khuon_la_la_chua_ghi`): thiếu `post`; `post` là `null`, danh sách, chuỗi, `{}`; chỉ `{"success": true}`; `success` là `false`, `0`, `"true"`, `null`; có `code` (kể cả `code: null`); `updated` là `"true"`, `1`, `1.0`, `null`, `false`, `[true]`, thiếu; bọc trong `data`; tiêu đề thêm dấu cách, viết hoa, dạng NFD, chèn ký tự rộng 0, khác một ký tự, là danh sách, là dict; mô tả khác; từ khóa `null`; khóa `focus_keyword` thay cho `focus_keyphrase`; cả câu trả lời là danh sách, chuỗi, `null`, `true`. Script dò riêng (37 khuôn, cả nhận lẫn không): 37/37 đúng mong đợi.
- Chỉ so trường đã gửi (gửi tiêu đề thì mô tả cũ trên site không làm hỏng xác nhận).
- **Không chặn oan khuôn thật:** site giả làm đúng như SiteSEO 1.4.2 (`update_post_seo_data`: `update_post_meta(…, sanitize_text_field($value))`, trả `post` đọc lại từ meta; tôi đọc mã ở kho plugin wordpress.org `siteseo/tags/1.4.2/main/abilitiesregister.php`, 2026-10-28). 6 tiêu đề chữ thường (có `|`, `&`, `100%`, «< … >», `>`, nháy kép): báo đã ghi (`test_chu_siteseo_luu_nguyen_thi_bao_da_ghi`). Chữ mà SiteSEO làm khác đi thì báo nhầm: **SL-T059-1**.

## Việc 2 · `srcset` của ảnh trong bài

**Đạt** (`seo_app/images/html.py:57`, `:59`, `:115-154`: `<img src alt srcset="<src> 1x" width height>`, chốt cuối đòi `srcset` còn sau bộ lọc, địa chỉ có dấu phẩy bị từ chối).

- **Đọc mã WordPress lõi** (`wordpress-develop` trunk, 2026-10-28; không gọi website): `wp_filter_content_tags` lấy mã ảnh bằng `preg_match( '/wp-image-([0-9]+)/i', … )` và chỉ thêm `srcset`/`sizes` khi `$attachment_id > 0 && ! str_contains( $filtered_image, ' srcset=' )`; `wp_image_add_srcset_and_sizes` và `wp_img_tag_add_srcset_and_sizes_attr` tự chúng không kiểm `srcset` có sẵn (nên điều kiện trên là chốt duy nhất); `wp_calculate_image_srcset` trả `false` khi dưới 2 ứng viên. `$allowedposttags['img']` của kses chỉ có `alt, align, border, height, hspace, loading, longdesc, vspace, src, usemap, width`: **không** có `srcset` (đúng rủi ro 2 của Thợ Máy).
- **Giả lập** (bản Python riêng của phần `srcset` trong `wp_filter_content_tags`, ảnh 1600×1200 có các cỡ 150×150, 300, 768, 800 như site thật): thẻ **cũ** + lớp `wp-image-951` bị thêm `-300x225.webp 300w`, `-800x600.webp 800w` và `sizes` (**tái hiện đúng lỗi 27/10**); thẻ **mới** với 7 cách website gắn lớp (đầu thẻ, cuối thẻ, kèm `alignnone size-full`, chữ hoa `WP-IMAGE-951`, thẻ tự đóng `/>`, kèm `loading="lazy" decoding="async"`, `srcset` nháy đơn): **không đổi gì**, `srcset` chỉ có file đầy đủ, không `sizes` (`test_wordpress_khong_them_ban_thu_nho_vao_the_moi`). Gửi nháp 3 ảnh qua site giả, gắn lớp đúng mã từng ảnh: cả 3 ảnh giữ file đầy đủ.
- **Không làm vỡ** (`test_figure_khong_vo_alt_chu_thich_chan_shortcode`, 6 ca: chữ Việt có «», gạch dài; nháy kép; `[caption]thu[/caption]`, `[code_snippet id=1]`, `[[embed]]`; ký tự rộng 0; `</figcaption><script>`, `<img onerror>`; emoji, chú thích rỗng): trình duyệt thấy đúng `figure` > `img` (đúng 5 thuộc tính `src, alt, srcset, width, height`) > `figcaption`; alt, chú thích đúng chữ đã làm sạch; không còn «[» «]» trần; `sanitize_html` giữ nguyên (chạy lại không đổi). Địa chỉ có `[1]`, `?ver=2&size=full`, `%C3%B4`, `%2C`: `src` và `srcset` cùng một địa chỉ. Địa chỉ có dấu phẩy, dấu cách, `2x`, tab, `javascript:` bị từ chối. Bộ lọc mà bỏ `srcset` thì không tạo nháp (chốt cuối).

## Việc 3 · Soát R5 test cũ đã đổi

Đối chiếu `git diff 4671104..team/T-059 -- tests/` với bảng «Test cũ đã đổi» của Thợ Máy (Chỉ Huy B duyệt 27/10). **Đạt**: chỉ đổi khuôn site giả hay danh sách khuôn, không câu kiểm nào bị nới.

| Nhóm | Kết quả |
|---|---|
| 1 · site giả mặc định `{"success": True}` → `siteseo_seo_answer` (`test_soi_loi_t042.py`, `test_wordpress_seo_meta_t042.py`, `test_soi_loi_t060.py`, `test_soi_loi_t088.py`, `test_t041_seo_ui.py`) | Chỉ đổi dòng `fake.on(… RUN …)`; không `assert` nào đổi |
| 2 · danh sách khuôn «được nhận» / «chưa ghi» (`test_soi_loi_t042_round2.py`, `test_wordpress_round2_t042.py`) | `{"updated": True}`, `{"success": True}` chuyển từ «được nhận» sang «chưa ghi»: **chặt hơn**, đúng việc của phiếu; thêm khuôn thật vào «được nhận» |
| 3 · `run={"updated": True}` → `siteseo_seo_answer` ở test không xét khuôn (`test_draft_check_is_the_last_request_before_writing`, chữ `&`, mã ký tự) | Giữ đúng ý test cũ (khuôn `{"updated": True}` nay là «chưa ghi» nên phải đổi site giả); `assert` giữ nguyên |
| Ảnh · `test_wordpress_images.py`, `test_soi_loi_t054.py` | «không có `srcset`» thay bằng «đúng một `srcset` là file đầy đủ, không `sizes`, không `wp-image-`» (vẫn chặn cỡ nhỏ); danh sách thuộc tính `<img>` vẫn so **đúng bằng** (thêm `srcset`); mẫu giả lập «bộ lọc bỏ alt» được sửa để vẫn thật sự bỏ alt (`( srcset)` thay `( width)`), thêm ca «bỏ `srcset`» |

Ghi chú: `siteseo_seo_answer` (site giả dùng chung) lưu **y chữ đã gửi**, còn SiteSEO thật làm sạch chữ; nên test cũ dùng tiêu đề «< 5 triệu» (`tests/test_t059_siet_ghi_seo_va_srcset.py`, `TITLE`) qua với site giả nhưng sẽ báo «không thành công» trên site thật (SL-T059-1).

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, không đụng worktree), gỡ từng chỗ sửa của bước 7 rồi chạy 7 file: `tests/test_soi_loi_t059.py` (của tôi), `tests/test_t059_siet_ghi_seo_va_srcset.py` (Thợ Máy), `tests/test_wordpress_images.py`, `tests/test_soi_loi_t054.py`, `tests/test_soi_loi_t042_round2.py`, `tests/test_wordpress_round2_t042.py`, `tests/test_wordpress_seo_meta_t042.py` (00:51–01:01). Bản không gỡ: mọi test qua.

| # | Chỗ sửa bị gỡ | Test của tôi hỏng | Test khác hỏng |
|---|---|---|---|
| Q1 | Bỏ `srcset` (cả chốt cuối) | 19 | 10 Thợ Máy, 12 Soi Lỗi T-054, 5 `test_wordpress_images.py` |
| Q2 | `srcset` theo bề rộng `1600w` thay `1x` | 18 | 9 Thợ Máy, 2 `test_wordpress_images.py` |
| Q3 | Nhận dấu phẩy trong địa chỉ ảnh | 1 | 1 Thợ Máy |
| Q4 | Chốt cuối không đòi `srcset` | 1 | 1 Thợ Máy, 1 `test_wordpress_images.py` |
| Q5 | Thiếu `post` vẫn nhận | 2 | 3 Thợ Máy, 2 test cũ T-042 |
| Q6 | Nhận lại khuôn `{"success": true}` | 4 | 4 Thợ Máy, 1 test cũ T-042 |
| Q7 | Bỏ so từng chữ | 17 (gồm 5 ca SL-T059-1 thành XPASS) | 7 Thợ Máy, 5 test cũ T-042 |
| Q8 | `success` lạ (`0`, chuỗi, `null`) vẫn nhận | 3 | 2 Thợ Máy |
| Q9 | Bỏ chặn khóa `code` | 2 | 1 Thợ Máy |

Mọi chỗ sửa bị gỡ đều làm hỏng test của tôi.

## Lỗi tìm được

### SL-T059-1 (Thấp) · Website đã ghi SEO (bản SiteSEO làm sạch) mà app báo «không thành công»

- **Chỗ:** `seo_app/wordpress/client.py:1893` (`_ability_confirms` so `post` đúng từng chữ với chữ đã gửi) cùng `_seo_text` (`:1662`), vốn cho đi các chữ mà SiteSEO lưu khác đi.
- **Phía SiteSEO 1.4.2** (đọc mã công khai, 2026-10-28): `update_post_seo_data` lưu `update_post_meta( $post_id, $meta_key, sanitize_text_field( $value ) )` rồi trả `post` đọc lại từ meta. `sanitize_text_field` đổi «< …» không có «>» phía sau thành `&lt; …` (`wp_pre_kses_less_than`), bỏ mọi «%» + 2 ký tự hex (`%[a-f0-9]{2}`); `update_metadata` của WordPress còn `wp_unslash` giá trị nên bỏ «\». Phần `wp_unslash` là hiểu biết về mã WordPress (`update_metadata`), chưa thử trên site thật.
- **Tái hiện** (site giả làm đúng như trên): `set_seo_meta(42, title="Cửa sắt giá < 2 triệu")` → app gửi `seo-data-update/run`, site lưu `Cửa sắt giá &lt; 2 triệu`, trả `{"updated": true, "post": {"title": "Cửa sắt giá &lt; 2 triệu", …}}` → app báo «Ghi SEO lên website không thành công. Bài nháp vẫn còn; hãy chép tay…». Cùng kết quả với mô tả «Cổng xếp < 3 triệu…», tiêu đề «Tăng 10%BE độ bền…» (site lưu «Tăng 10 độ bền…»), «Giảm giá 5\% …» (site lưu «Giảm giá 5% …»). Chính tiêu đề mẫu của test Thợ Máy (`"Cổng inox < 5 triệu, giảm 10% tiền công | Pro-Metal"`, theo bước 2 của phiếu) cũng rơi vào ca này trên site thật.
- **Mong đợi:** website đã ghi thì app báo đã ghi; hoặc app chặn trước khi gửi (kèm câu báo) những chữ mà SiteSEO sẽ đổi.
- **Thực tế:** báo «không thành công», người dùng chép tay thừa (kết quả trên site như nhau). Với «%» + 2 ký tự hex, chữ trên site còn **bị cắt mất** (do SiteSEO) mà người dùng không được báo.
- **Mức:** Thấp: không ghi sai, không lộ gì, chỉ báo sai chiều an toàn. **Có từ trước** (T-042 đã so từng chữ khi có `post`; 5 ca `xfail` cũng XFAIL trên code `4671104`), bước 7 chỉ làm `post` bắt buộc. **Không bắt buộc sửa trước Lá Chắn.**
- **Test:** `test_sl_t059_1_chu_siteseo_lam_sach_van_bao_dung` (5 ca: «<» ở tiêu đề, mô tả; «%BE»; «\»).
- **Gợi ý sửa:** (a) so `post` với cả bản «đã làm sạch kiểu SiteSEO» của chữ gửi (`wp_unslash(sanitize_text_field(…))`), hoặc (b) `_seo_text` chặn trước khi gửi, kèm câu báo, các chữ SiteSEO sẽ đổi: «<» không có «>» phía sau, «%» + 2 ký tự hex, «\». Cách (b) còn tránh được chuyện SiteSEO cắt mất chữ mà người dùng không biết.

## Ghi nhận (không xếp lỗi)

1. **Rủi ro kses** (Thợ Máy, rủi ro 2) xác nhận bằng mã: `img` trong kses không có `srcset`. App đọc được quyền này: `check_connection` đã lấy `capabilities` của tài khoản (`/wp/v2/users/me?context=edit`, `client.py:760-774`, hiện chỉ dùng `edit_posts`, `publish_posts`, `upload_files`); nếu `unfiltered_html` không phải `true` thì có thể cảnh báo ngay ở trang Kết nối WordPress rằng ảnh trong bài sẽ bị WordPress gắn bản thu nhỏ mất GPS. Đề xuất cho phiếu sau, không xếp lỗi.
2. **Chưa thử trên site thật**: lớp `wp-image-951` do thứ gì phía website gắn vẫn chưa rõ; nếu là plugin tự dựng `srcset` riêng (không qua `wp_filter_content_tags`) hay viết lại thẻ `<img>` thì cách này có thể không đủ. Đồng ý đề xuất của Thợ Máy: thử lại một bài nháp một ảnh, xem nguồn trang chỉ còn `srcset="…/<tên-ảnh>.webp 1x"`, tải file về kiểm GPS.
3. Khóa lạ thêm vào câu trả lời (`message`, `data`…) vẫn được nhận khi `post` khớp đủ: chủ ý của Thợ Máy (bản SiteSEO sau thêm khóa không làm app báo sai); `code` hay `success` khác `True` thì không nhận. Đồng ý.
4. `detect-secrets` (`PYTHONUTF8=1`) trên 2 file của tôi: «Secret Keyword» ở `tests/test_soi_loi_t059.py:39` (`PASSWORD`): mật khẩu giả cho test, cùng kiểu các file test khác. Báo cáo này: 0.

## Bằng chứng

```
# 37 file liên quan (client WordPress, gửi nháp kèm ảnh, T-042, T-054, T-061, T-071, các file
# T-059 đã đổi, trang Soạn bài/SEO/Kết nối), đầu nhánh d0fbbd8, chưa có file của tôi (00:42–01:12):
$ uv run pytest tests/test_wordpress_client.py tests/test_wordpress_images.py
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py
    tests/test_wordpress_site_link_t042.py tests/test_wordpress_paging_t042.py
    tests/test_wordpress_t060.py tests/test_wordpress_t085.py tests/test_wordpress_t088.py
    tests/test_wordpress_shortcodes.py tests/test_soi_loi_t042.py tests/test_soi_loi_t042_round2.py
    tests/test_soi_loi_t042_paging_cache.py tests/test_site_index_t042.py tests/test_soi_loi_t054.py
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_soi_loi_t071.py
    tests/test_la_chan_t071.py tests/test_t059_siet_ghi_seo_va_srcset.py tests/test_soi_loi_t060.py
    tests/test_la_chan_t060.py tests/test_soi_loi_t085.py tests/test_la_chan_t085.py
    tests/test_soi_loi_t088.py tests/test_la_chan_t089.py tests/test_soi_loi_t089.py
    tests/test_t041_meta.py tests/test_t041_seo_ui.py tests/test_soi_loi_t081.py
    tests/test_t081_alt_gach_cheo.py tests/test_soi_loi_t056.py tests/test_app_images.py
    tests/test_app_wordpress.py tests/test_app_pages.py -rfxX
5069 passed, 13 xfailed in 1775.83s
# 13 xfail có sẵn, không thuộc T-059: SL-T088-1 (8), SL-T081-1 (5)

# Lượt chốt (01:21–01:22): file của tôi + 11 file gần nhất
$ uv run pytest tests/test_soi_loi_t059.py tests/test_t059_siet_ghi_seo_va_srcset.py
    tests/test_wordpress_images.py tests/test_soi_loi_t054.py tests/test_soi_loi_t042_round2.py
    tests/test_wordpress_round2_t042.py tests/test_wordpress_seo_meta_t042.py
    tests/test_soi_loi_t042.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py
    tests/test_soi_loi_t071.py tests/test_la_chan_t071.py -rfxX
1741 passed, 5 xfailed in 66.48s       # 5 xfail: SL-T059-1

$ uv run pytest tests/test_soi_loi_t059.py
71 passed, 5 xfailed

$ uv run ruff check .
All checks passed!

# Test mới trên code trước bước 7 (4671104, giải nén vào thư mục nháp):
26 failed, 45 passed, 5 xfailed
# 26 hỏng: không có srcset (19), nhận khuôn thiếu post/success cũ (6), không chặn dấu phẩy (1).
# 5 ca SL-T059-1 XFAIL cả trên code cũ: lỗi có từ trước.

# Gộp thử với origin/main d9e6b5c (git merge-tree): không xung đột; main mới chỉ thêm 2 file test
# (Cài đặt ảnh, T-084), không đụng client WordPress, figure_html, sanitize_html, fake_wordpress.
```

Script dò riêng: thư mục ghi chú chung `T-059-soi-loi-scripts/` (`probe_confirm.py`, `mutate059.py`). Chạy bằng `.venv` của worktree, thư mục làm việc là worktree.

## Đối chiếu tiêu chí xong

- [x] Việc 1: khuôn thật được nhận; 34 khuôn lạ (thiếu `post`, `post` sai kiểu, chữ khác một ký tự, `success`, `updated` dạng chuỗi/số…) là chưa ghi; không chặn oan khuôn thật với chữ SiteSEO để nguyên (chữ SiteSEO làm khác: SL-T059-1)
- [x] Việc 2: đọc mã `wp_filter_content_tags`, `wp_image_add_srcset_and_sizes`, `wp_calculate_image_srcset`, kses; giả lập: thẻ có `srcset` thì WordPress không thêm bản thu nhỏ; `<figure>`, alt, chú thích, chặn shortcode, `sanitize_html` giữ thuộc tính
- [x] Việc 3: soát R5 các test cũ đã đổi: chỉ đổi khuôn site giả, không nới câu kiểm
- [x] Lỗi mới có test `xfail(strict=True)`: SL-T059-1
- [x] Không sửa code ứng dụng, không gọi website thật

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (SL-T059-1, có từ trước T-059, báo sai chiều an toàn). **Chuyển Lá Chắn rút gọn được ngay; không lỗi nào phải sửa trước Lá Chắn.** Điều kiện: SL-T059-1 vào phiếu dọn sau (trước khi bật «Ghi SEO lên website» cho người dùng dùng thường xuyên); thử lại `srcset` trên site thật sau khi gộp (ghi nhận 2).

## Đề xuất

1. (Thợ Máy, phiếu sau) SL-T059-1: cách (b) ở trên (chặn trước khi gửi, kèm câu báo) hoặc (a).
2. (Thợ Máy hay Họa Sĩ, phiếu sau) Cảnh báo ở trang Kết nối WordPress khi tài khoản không có quyền `unfiltered_html` (ghi nhận 1).
3. (Chỉ Huy) Thử lại trên site thật một bài nháp một ảnh (ghi nhận 2).

## Câu hỏi cho chủ dự án

Không có.

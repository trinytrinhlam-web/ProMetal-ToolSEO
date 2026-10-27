# Báo cáo T-059 · Bước 7: siết code theo kết quả thử thật (ghi SEO, ảnh trong bài)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-059](../tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md), bước 7 |
| Ngày nộp | 2026-10-28 00:10 (giờ máy, +07); làm từ 2026-10-27 |
| Kết quả | Hoàn thành (chờ Soi Lỗi, Lá Chắn; cần thử lại trên site thật, mục «Đề xuất») |

## Tóm tắt (cho chủ dự án)

- **Ghi SEO lên website:** app chỉ báo «đã ghi» khi website trả lời đúng khuôn thật của SiteSEO 1.4.2 (như lần thử 27/10) **và** chữ website đã lưu giống từng chữ app gửi. Câu trả lời khác khuôn thì app báo «không thành công» để người dùng chép tay vào hộp SiteSEO; không bao giờ báo «đã ghi» khi chưa chắc.
- **Ảnh trong bài:** mỗi ảnh app chèn vào bài nay kèm sẵn danh sách cỡ ảnh (`srcset`) chỉ có **một** file: file đầy đủ 1600 px còn GPS. WordPress thấy ảnh đã có danh sách này thì không tự thêm các bản thu nhỏ (bản thu nhỏ mất GPS), nên điện thoại cũng tải đúng file đầy đủ (quyết định 5A).
- **Đổi lại:** điện thoại tải file 1600 px thay vì bản 300–800 px, nên trang nặng hơn trên điện thoại (mục «Rủi ro»).
- **Phát hiện:** app **không** gắn lớp `wp-image-951` vào ảnh (đã vậy từ T-054); lớp này do một thứ phía website gắn. Cách sửa trên chặn được dù lớp vẫn bị gắn, nhưng cần thử lại trên site thật để chắc.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `_ability_confirms`: bỏ nhánh nhận `{"success": true}`; chỉ nhận `updated is True` + `post` (bắt buộc, là dict) có từng trường đã gửi đúng từng chữ; `success` có mặt mà khác `True`, hay có `code`: chưa ghi; không có trường nào để so: chưa ghi. Viết lại docstring theo khuôn thật 27/10 |
| `seo_app/images/html.py` | `figure_html` ghi `srcset="<src> 1x"` (một ứng viên, chính file đầy đủ) vào `<img>`; chốt cuối đòi `srcset` còn nguyên sau bộ lọc, mất thì báo lỗi, không gửi ảnh; địa chỉ ảnh có dấu phẩy bị từ chối (dấu phẩy tách ứng viên trong `srcset`). Docstring module ghi lý do, giới hạn |
| `tests/test_t059_siet_ghi_seo_va_srcset.py` (mới) | 42 test: khuôn trả lời thật (chữ có `%`, `<`), 24 khuôn khác khuôn thật đều «chưa ghi»; `srcset` một ứng viên; **WordPress giả lập** (mục dưới) tái hiện đúng lỗi 27/10 ở thẻ cũ và không đổi gì ở thẻ mới dù website gắn lớp; giới hạn kses; chặn shortcode trong `srcset`; chốt cuối khi bộ lọc bỏ `srcset`; gửi nháp 3 ảnh qua site giả |
| `tests/fake_wordpress.py` | Thêm `siteseo_seo_answer`: site giả trả lời `seo-data-update/run` đúng khuôn thật 27/10 (lưu y chữ đã gửi), dùng chung cho các test cũ ở bảng dưới |

### Test cũ đã đổi (Chỉ Huy B duyệt 27/10, R5: không xóa, không bỏ qua test nào)

Lý do chung cho nhóm 1–3: khuôn thật đo trên site 27/10 là `{"updated": true, "post": {…}}`, không có `success`; `post` nay bắt buộc. Các test «`success: False` / `0` / `"false"` là chưa ghi» giữ nguyên (vẫn đúng).

| Nhóm | File:dòng (sau khi sửa) | Đổi gì |
|---|---|---|
| 1 | `tests/test_soi_loi_t042.py:56-58` | Site giả mặc định `{"success": True}` → `siteseo_seo_answer` |
| 1 | `tests/test_wordpress_seo_meta_t042.py:54-56` | Như trên |
| 1 | `tests/test_soi_loi_t060.py:682` | Như trên |
| 1 | `tests/test_soi_loi_t088.py:256` | Như trên |
| 1 | `tests/test_t041_seo_ui.py:155` | Như trên (test giao diện bước SEO) |
| 2 | `tests/test_soi_loi_t042_round2.py:262-265`, `:289-292` | Danh sách «được nhận»: bỏ `{"updated": True}`, `{"success": True}`, thêm khuôn thật; hai khuôn đó chuyển sang danh sách «chưa ghi» |
| 2 | `tests/test_wordpress_round2_t042.py:198`, `:222-225` | Như trên |
| 3 | `tests/test_soi_loi_t042_round2.py:43-45` | Site giả mặc định `{"updated": True}` → `siteseo_seo_answer` |
| 3 | `tests/test_wordpress_round2_t042.py:156`, `:394`, `:404` | `run={"updated": True}` → `run=siteseo_seo_answer` |

Lý do cho nhóm ảnh: thẻ `<img>` nay có thêm `srcset` (việc 2 của phiếu); không nới kiểm tra nào.

| File:dòng (sau khi sửa) | Đổi gì |
|---|---|
| `tests/test_wordpress_images.py:9-10` | Docstring: `srcset` chỉ có file đầy đủ |
| `tests/test_wordpress_images.py:256-261` | Trước: «không có `srcset`, `sizes`». Nay: đúng một `srcset` là `<file đầy đủ> 1x`, không `sizes`, không `wp-image-` |
| `tests/test_wordpress_images.py:362-366` | Danh sách thuộc tính `<img>` trình duyệt thấy: thêm `srcset` (5 thuộc tính) |
| `tests/test_wordpress_images.py:388-389` | Chuỗi `<figure>` mong đợi có `srcset="… 1x"` |
| `tests/test_wordpress_images.py:1029-1030` | Giả lập «bộ lọc bỏ alt» tìm `alt` đứng trước `srcset` (trước đó trước `width`, nay không còn khớp nên test không thử được gì); thêm ca «bộ lọc bỏ `srcset`» |
| `tests/test_soi_loi_t054.py:418-423` (của Soi Lỗi) | Danh sách thuộc tính `<img>`: thêm `srcset` |

## Tìm hiểu WordPress trước khi chọn cách (bước 2 của việc)

Đọc mã WordPress lõi (`wp-includes/media.php`, `wp-includes/kses.php`, nhánh trunk trên GitHub `WordPress/wordpress-develop`, ngày 2026-10-27; không gọi website của mình):

- `wp_filter_content_tags` lấy mã ảnh **chỉ** từ lớp `wp-image-N` của thẻ (`preg_match( '/wp-image-([0-9]+)/i', … )`), không dò theo địa chỉ ảnh. Không có lớp thì mã là 0, không thêm gì.
- Nó chỉ gọi `wp_img_tag_add_srcset_and_sizes_attr` khi `$attachment_id > 0 && ! str_contains( $filtered_image, ' srcset=' )`: **thẻ đã có `srcset` thì để nguyên**.
- `wp_calculate_image_srcset` chỉ trả `srcset` khi có từ 2 ứng viên trở lên; ứng viên lấy từ các cỡ WordPress tạo (những bản đã mất EXIF/GPS).
- `$allowedposttags['img']` của kses chỉ có `alt, align, border, height, hspace, loading, longdesc, vspace, src, usemap, width`: **không có `srcset`, `sizes`**. Tài khoản không có quyền `unfiltered_html` thì WordPress bỏ `srcset` khi lưu bài.

Vì app đã không gắn `wp-image-<mã>` (`seo_app/images/html.py`, test `test_anh_dung_trong_bai_la_file_day_du_va_khong_co_wp_image` có từ T-054), cách «không phát lớp» trong phiếu đã có sẵn mà site thật vẫn ra `wp-image-951` + `srcset`. Nên chọn cách chắc hơn:

| Cách | Kết luận |
|---|---|
| A. Không gắn `wp-image-<mã>` | Đã làm từ T-054; **không đủ** (website tự gắn lớp) |
| B. Ghi sẵn `srcset` chỉ có file đầy đủ | **Chọn.** Đúng cơ chế WordPress lõi tôn trọng (`' srcset='` có rồi thì bỏ qua); không đổi cách ảnh hiện; có lớp `wp-image-<mã>` hay không cũng vậy |
| C. Khai `width`/`height` sai tỷ lệ để không cỡ nào khớp | Loại: khung ảnh sai tỷ lệ trước khi tải xong (nhảy bố cục) |
| D. Viết `src` bằng nháy đơn để biểu thức `src="…"` của WordPress không bắt | Loại: bộ lọc của app in lại nháy kép; mẹo mong manh |
| E. Tắt `srcset` phía website (một dòng Code Snippets) | Không làm: sửa website, ảnh hưởng mọi bài cũ, cần chủ dự án duyệt (mục «Đề xuất») |

Chọn `1x` (không `1600w` + `sizes`): một ứng viên thì `sizes` vô nghĩa; không có `sizes` thì `wp_img_tag_add_auto_sizes` (WordPress 6.7+) cũng không đụng tới. App không ghi `loading`: WordPress tự thêm `loading="lazy"`/`fetchpriority` theo vị trí ảnh (bước này không cần mã ảnh), ảnh đầu bài không bị lười tải.

### Thử bằng WordPress giả lập (Chỉ Huy đề nghị)

Không gọi được website thật, nên tôi chép sang Python đường WordPress lõi dựng `srcset` khi in bài: `wp_filter_content_tags` → `wp_image_add_srcset_and_sizes` → `wp_calculate_image_srcset` (so file với `src`, cùng tỷ lệ ±1 px, bỏ cỡ > 2048 px, cần ≥ 2 ứng viên, ảnh của `src` đứng đầu) → `sizes` mặc định `(max-width: Wpx) 100vw, Wpx`. Dữ liệu ảnh giả có các cỡ 150×150 (cắt vuông), 300, 768, 800 như site thật. Kết quả (test trong `tests/test_t059_siet_ghi_seo_va_srcset.py`):

| Ca | Kết quả giả lập |
|---|---|
| Thẻ cũ (trước T-059), không lớp | Không đổi (WordPress không tự gắn lớp, không thêm gì) |
| Thẻ cũ + lớp `wp-image-951` (như trang 27/10) | Thêm `srcset` 1600w, 300w, 768w, 800w và `sizes`: **tái hiện đúng lỗi thật** |
| Thẻ mới + lớp ở đầu thẻ / cuối thẻ kèm lớp khác / chữ hoa / kèm `loading="lazy" decoding="async"` | **Không đổi gì**: `srcset` vẫn chỉ có file đầy đủ, không có `sizes` |
| Gửi nháp 3 ảnh qua site giả, gắn lớp đúng mã từng ảnh | Không đổi gì; cùng nội dung bỏ `srcset` thì cả 3 ảnh bị thêm cỡ 300 px (giả lập nhận đúng mã, đúng file) |
| Thẻ mới bị kses bỏ `srcset` + lớp | Lỗi quay lại (giới hạn, mục «Rủi ro» 2) |

### Lớp `wp-image-951` từ đâu

App **không** gắn lớp này: `figure_html` chỉ có `wp-block-image` trên `<figure>` (từ T-054), `sanitize_html` không thêm lớp, client không sửa nội dung sau bộ lọc (`seo_app/wordpress/client.py`, `create_draft_with_images`). WordPress lõi cũng không gắn (chỉ **đọc** lớp này để lấy mã ảnh). Vậy một thứ phía website gắn: **chưa xác định được** vì phiếu không cho gọi website. Nghi (suy luận, chưa kiểm): (a) trình soạn khối khi mở bài nháp để xem hộp SiteSEO rồi lưu, (b) plugin tối ưu ảnh/cache (SpeedyCache, LiteSpeed), (c) tính năng ảnh của SiteSEO Pro, (d) theme. Cách kiểm ở mục «Đề xuất».

## Vì sao `post` là bắt buộc (bước 1 của việc)

- Site thật trả `post` ở mọi lần ghi thành công (27/10), đúng mã SiteSEO 1.4.2 (`update_post_seo_data`).
- `post` là phần duy nhất cho biết website **lưu đúng chữ đã gửi**. SiteSEO làm sạch chữ (ví dụ `<` thành `&lt;`, `%` thành `&#37;`) thì giá trị khác; thiếu `post` thì app không có cách nào biết.
- Câu trả lời `{"updated": true}` trơn không phải của SiteSEO 1.4.2: có thể là ability khác, lớp đệm, plugin chen giữa. Coi là «chưa ghi» là chiều an toàn (người dùng chép tay; cùng lắm chép trùng chữ đã có).
- Đúng việc 10 của Lá Chắn T-042 («bắt buộc có `post` và khớp từng trường»).
- Khóa lạ khác thêm vào (ví dụ `message`) vẫn nhận, để bản SiteSEO sau thêm khóa không làm app báo sai; riêng `success` mà khác `True` thì không nhận (SL-T042-8: một khóa nói «chưa ghi» thì không tin khóa kia).

## Bằng chứng

Máy Windows của chủ dự án, worktree `wt-T-059`. 37 file test liên quan: mọi file test gọi `figure_html`, `create_draft_with_images`, `set_seo_meta`, `_ability_confirms`, ability `seo-data-update`, «Gửi nháp» (kể cả `app/views/write.py` gọi qua giao diện: `test_t041_seo_ui.py`, `test_app_images.py`, `test_t089_send_draft.py`…), mọi `tests/test_wordpress*.py`, và file mới.

```
$ uv run pytest -q -p no:cacheprovider <37 file test liên quan>   # toàn bộ test do Chỉ Huy chạy khi gộp
5082 passed, 13 xfailed in 3498.66s (0:58:18)

$ uv run pytest -q tests/test_t059_siet_ghi_seo_va_srcset.py
42 passed in 17.49s

$ uv run ruff check .
All checks passed!
```

Lượt chạy trước khi đổi test cũ (code mới, test cũ): `58 failed, 5016 passed, 13 xfailed`. 57 lỗi đúng dự kiến (41 do site giả trả khuôn `success` / thiếu `post`, 16 do thẻ ảnh có thêm `srcset`); 1 lỗi `test_app_images.py::test_spot_is_real_picker_and_nothing_scanned_until_opened` do máy quá tải (chạy riêng: `1 passed in 114.40s`; lượt sau cùng qua). 13 xfail có từ trước, không thuộc phiếu.

Test mới bắt được bản cũ (hàm của `HEAD` `4671104` chạy với khuôn cũ):

```
HEAD nhan {'success': True}: True
HEAD nhan {'updated': True} thieu post: True
HEAD figure_html co srcset: False
Moi nhan {'success': True}: False
Moi nhan {'updated': True} thieu post: False
```

## Đối chiếu tiêu chí xong

- [x] Bỏ nhánh `{"success": true}`; chỉ nhận `updated is True` và `post` là dict có giá trị đúng chữ đã gửi; `post` bắt buộc (lý do ở trên). Bằng chứng: `seo_app/wordpress/client.py` `_ability_confirms`; test `test_khuon_tra_loi_that_cua_siteseo_la_da_ghi`, `test_khuon_khac_khuon_that_la_chua_ghi[khuon-success-cu]`, `[thieu-post]`, `[phan-tram-bi-doi]`…
- [x] Docstring cập nhật theo khuôn thật 27/10.
- [x] Ảnh trong nội dung không còn để WordPress gắn `srcset`/`sizes` cỡ nhỏ: `srcset` có sẵn một ứng viên là file đầy đủ. Bằng chứng: `test_wordpress_khong_doi_srcset_cua_app_du_noi_dung_bi_doi` (5 ca), `test_gia_lap_tai_hien_dung_loi_that_27_10` (giả lập bắt đúng lỗi 27/10 ở thẻ cũ), `test_gui_nhap_kem_anh_moi_anh_co_srcset_file_day_du`.
- [x] Giữ `width`, `height`, alt, chú thích, chặn shortcode như cũ; `loading` để WordPress tự đặt như trước (app chưa bao giờ ghi `loading`). Bằng chứng: test cũ T-054, T-061, T-071, T-081 qua; `test_srcset_vo_hieu_shortcode_nhu_src`.
- [x] Test cũ T-042, T-054, T-061, T-071 qua (sau khi đổi site giả sang khuôn thật, mục «Đã thay đổi»).
- [ ] Thử lại trên site thật (không thuộc Thợ Máy; mục «Đề xuất»).

## Rủi ro và điểm cần chú ý

1. **Chưa rõ thứ gì gắn `wp-image-951`.** WordPress lõi không tự gắn lớp này (mục trên). Nếu đó là plugin vừa gắn lớp vừa tự dựng `srcset` riêng (không qua `wp_filter_content_tags`), hoặc viết lại thẻ `<img>`, thì cách B có thể không đủ. Phải thử lại trên site thật.
2. **kses bỏ `srcset`** khi tài khoản không có quyền `unfiltered_html` (Biên tập viên trên site đơn có quyền này, trừ khi site đặt `DISALLOW_UNFILTERED_HTML`). Khi đó ảnh quay về như 27/10. Thử lại trên site thật sẽ thấy.
3. **Trình soạn khối:** người dùng mở bài nháp rồi bấm «Chuyển thành khối» thì khối Ảnh có thể bỏ `srcset` (khối Ảnh chỉ giữ một số thuộc tính). Đây là **suy luận** từ cách trình soạn khối hoạt động, chưa kiểm.
4. **Tốc độ trên điện thoại:** luôn tải file 1600 px. So với bản 800 px, file 1600 px có **gấp 4 lần số điểm ảnh** (1600×1200 so với 800×600); dung lượng thật tùy ảnh (WebP), chưa đo trên site. Ảnh dưới màn hình đầu vẫn được WordPress lười tải (`loading="lazy"`), nên chỉ tải khi người đọc cuộn tới; ảnh đầu bài tải ngay và có thể làm chậm chỉ số tốc độ của Google trên điện thoại (LCP). Đây là đánh đổi của quyết định 5A (GPS tới người xem và Google), không đổi quyết định.
5. `post` bắt buộc: bản SiteSEO sau đổi khuôn (bỏ `post`, đổi tên trường) thì app báo «không thành công» dù đã ghi; người dùng chép tay, không hỏng gì.

## Đề xuất

- **Chỉ Huy, thử lại trên site thật sau khi gộp** (một bài nháp, một ảnh; điều kiện 6 Lá Chắn T-054): mở nguồn trang xem trước, thẻ ảnh trong nội dung phải có `srcset="…/<tên-ảnh>.webp 1x"` và **không** có `-300x…`, `-768x…`, `-800x…`; tải file trong `srcset` về kiểm còn GPS.
- **Chỉ Huy, tìm thứ gắn `wp-image-951`:** trong bài nháp thử, xem nội dung đã lưu (trình soạn → «Trình soạn mã») có lớp `wp-image-951` không. Có thì nội dung bị sửa lúc lưu (ví dụ trình soạn khối khi mở bài); không thì một plugin thêm lúc in trang. Nghi (suy luận, chưa kiểm): SpeedyCache, tính năng ảnh của SiteSEO Pro, hay theme.
- **Việc phía website, cần chủ dự án duyệt (ngoài phạm vi):** một dòng Code Snippets `add_filter( 'wp_calculate_image_srcset', '__return_false' );` (theo mã WordPress: `wp_calculate_image_srcset` trả rỗng khi bộ lọc trả không phải mảng; chưa thử) tắt `srcset` cho **mọi** ảnh của site (kể cả ảnh đại diện theme in bằng `the_post_thumbnail`, việc Chỉ Huy đang hỏi riêng) và **mọi bài cũ**: trang nặng hơn trên điện thoại ở mọi bài. Chỉ nên làm nếu chủ dự án muốn GPS ở cả ảnh đại diện.

## Câu hỏi cho chủ dự án

Không có.

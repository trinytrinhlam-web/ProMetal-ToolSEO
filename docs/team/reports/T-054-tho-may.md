# Báo cáo T-054 · WordPress: tải ảnh và chèn `<figure>` vào nháp (G3-8)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-054](../tickets/T-054-chen-anh-vao-nhap-wordpress.md) |
| Ngày nộp | 2026-10-20 (15:40, giờ máy) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- App đã có phần "Gửi nháp kèm ảnh": tải ảnh 1600 px (còn GPS) lên thư viện Media của website, ghi alt, tiêu đề, chú thích, chèn từng ảnh vào đúng chỗ trong bài, tạo bài **nháp**, rồi đặt ảnh đại diện. Chưa có nút trên giao diện: phiếu giao diện T-056 sẽ nối vào nút "Gửi nháp".
- File gửi lên đúng là file app đã nén (không sửa một byte), nên GPS tới website đúng từng con số. Trong bài, ảnh luôn trỏ vào file đầy đủ 1600 px (quyết định 5A), không để WordPress tự đổi sang cỡ nhỏ đã mất GPS.
- Nếu lỗi giữa chừng (mạng, website báo lỗi), app **không xóa gì**: báo rõ những ảnh nào đã lên thư viện (ảnh này xem được công khai qua đường dẫn) để anh tự xử lý.
- Kiểm hết trước khi gửi: thiếu alt, ảnh chưa qua bước xử lý, chọn hai ảnh đại diện… thì báo lỗi và **chưa gửi gì** lên website.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/html.py` | Mới: `plain_image_text` (gỡ ký tự ngắt rộng 0, gỡ escape link Markdown, bỏ ký tự vô hình, gộp một dòng), `figure_html` (dựng `<figure class="wp-block-image"><img …><figcaption>…</figcaption></figure>` bằng code, escape, qua `sanitize_html` lần cuối), `ImageHtmlError` |
| `seo_app/wordpress/client.py` | `DraftImage`, `UploadedImage`, `DraftWithImages`, `DraftImagesError`; `WordPressClient.create_draft_with_images`; tách `_post_media` khỏi `upload_media` (hành vi `upload_media` giữ nguyên) |
| `tests/test_wordpress_images.py` | Mới: 37 hàm test, 90 trường hợp (site giả, ảnh giả tạo trong bộ nhớ, không mạng) |
| `docs/team/reports/T-054-tho-may.md` | Báo cáo này |

**Không sửa `seo_app/sanitize.py`** (lý do ở mục "Quyết định": `class` đã được cho phép từ trước, không cần mở). Không sửa `app/**`, `config/**`, `process.py`, `naming.py`, `alt.py`, `folders.py`, `seo_app/wordpress/__init__.py`, không import `seo_app/images/tags.py`, không thêm thư viện. `git diff --stat 5441a68..HEAD` (trước báo cáo): 3 file, 1209 dòng thêm, 17 dòng bỏ.

Commit trên `team/T-054`: `ccb3565` (html.py), `642c921` (client), `e99f6e5` (test), `293dcba` (dọn trường thừa), và commit báo cáo.

## Cách dùng (cho T-056)

```python
from seo_app.images.process import make_web_image
from seo_app.wordpress.client import DraftImage, DraftImagesError, WordPressClient, WordPressError

web = make_web_image(library.read_image_bytes(ref), **load_image_settings())  # WebImage
image = DraftImage(
    web,
    alt=alt_da_duyet,            # chữ trong ô nhập (có thể còn ký tự ngắt rộng 0: client tự gỡ)
    caption=chu_thich_da_duyet,
    category=tags.category, area=tags.area, project_code=tags.project_code,  # ImageTags (T-052)
    ai_generated=(tags.source == "ai"),
    featured=True,               # không ảnh nào đánh dấu thì lấy ảnh đầu tiên
)
try:  # CHỈ gọi khi người dùng bấm «Gửi nháp»
    result = client.create_draft_with_images(title, ["<h2>…</h2>", "<p>…</p>", image, "<p>…</p>"])
except DraftImagesError as exc:  # chưa có bài; exc.uploaded: ảnh đã công khai trên website
    ...
except WordPressError as exc:    # kiểm sai: chưa gửi gì
    ...
# result.post, result.images (mã, tên file, địa chỉ, link sửa), result.featured_media, result.message
```

## Bằng chứng

```
$ uv run pytest -q tests/test_wordpress_images.py
90 passed in 2.59s

$ uv run pytest -q -p no:cacheprovider tests/test_app_wordpress.py tests/test_images_process.py \
    tests/test_safety.py tests/test_sanitize.py tests/test_sanitize_autolink.py \
    tests/test_sanitize_bypass.py tests/test_sanitize_hardening.py tests/test_site_index_t042.py \
    tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t042_round2.py \
    tests/test_wordpress_client.py tests/test_wordpress_images.py tests/test_wordpress_paging_t042.py \
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py \
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py \
    tests/test_wordpress_site_link_t042.py
2013 passed in 129.38s (0:02:09)          (Windows 11, tại 293dcba)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/images/html.py seo_app/wordpress/client.py tests/test_wordpress_images.py
"results": {}
```

Không chạy toàn bộ `uv run pytest` (Chỉ Huy chạy khi gộp). Test chạy được cả khi không đặt `PYTHONUTF8`.

**Thử "đột biến" để chắc test bắt được lỗi thật** (sửa tạm code, chạy test, chép lại bản gốc; `git diff` sau đó chỉ còn thay đổi thật):

| Sửa tạm | Kết quả |
|---|---|
| Thêm `class="wp-image-1"` vào `<img>` | 3 test hỏng |
| `plain_image_text` bỏ bước gỡ ký tự ngắt và escape Markdown | 2 test hỏng |
| Gửi `image.data` bị đổi 2 byte cuối | 2 test hỏng |
| `set_featured_image` bỏ bước hỏi lại bài còn nháp (`_own_draft`) | 2 test hỏng |

## Đối chiếu yêu cầu và điều kiện

**Yêu cầu 1. Chỉ tải ảnh khi bấm Gửi nháp; lỗi giữa chừng liệt kê media đã tải, không xóa (W2, Lá Chắn T-046 số 8).**
- Chỉ `create_draft_with_images` tải ảnh của bài (`client.py:932`); dựng `DraftImage`, `figure_html` không gọi mạng (`test_dung_html_va_draft_image_khong_goi_mang`). Việc chỉ gọi hàm này khi người dùng bấm là của T-056 (ghi trong docstring và mục Đề xuất).
- Kiểm hết **trước** request đầu tiên (`_plan_draft_images`, `client.py:1037`): 16 kiểu ảnh/nội dung sai + 9 kiểu tiêu đề/chuyên mục sai + 5 kiểu `parts` sai đều cho 0 request, kể cả khi ảnh hợp lệ đứng trước ảnh lỗi (`test_kiem_sai_thi_chua_gui_gi`, `test_tieu_de_chuyen_muc_sai_thi_chua_gui_gi`, `test_noi_dung_khong_phai_danh_sach_thi_chua_gui_gi`).
- Lỗi ở bước tải ảnh, ghi alt, tạo nháp: `DraftImagesError` (`client.py:414`) có `uploaded` (mã, tên file, địa chỉ, link sửa từng ảnh) và câu báo "Phần mềm không xóa ảnh: ảnh vẫn xem được công khai…". Ảnh đang tải lúc lỗi mạng/máy chủ 5xx hay website không trả mã: `maybe_uploaded=True` và câu báo nhắc kiểm thư viện. Lỗi lạ (không nên có) cũng được bọc lại để không mất danh sách (`client.py:1020`). Không có lệnh nào ngoài `GET`/`POST`; client không có hàm xóa. Test: `test_anh_thu_hai_loi_may_chu_liet_ke_anh_dau_khong_tao_bai`, `test_anh_bi_tu_choi_4xx_thi_khong_bao_co_the_da_len`, `test_tai_len_khong_tra_ma_anh_thi_bao_co_the_da_len`, `test_ghi_alt_loi_van_liet_ke_anh_da_tai`, `test_tao_nhap_loi_liet_ke_moi_anh_da_tai`, `test_loi_la_van_liet_ke_anh_da_tai`, `test_client_khong_co_ham_xoa`.

**Yêu cầu 2. Byte gửi lên còn GPS; tải đúng `WebImage.data` (Lá Chắn T-049 điều kiện 4).**
- Gửi thẳng `item.source.image.data` (`client.py:987`) qua `_post_media` (`client.py:906`), không đổi, không nén lại. Test tạo JPEG giả có GPS → `make_web_image` thật → gửi: byte website nhận **bằng** `web.data`, đọc lại GPS độc lập bằng Pillow đúng từng giá trị (vĩ độ, kinh độ, N/E) (`test_byte_gui_len_dung_webimage_data_va_con_gps`). Ảnh không GPS cũng gửi nguyên byte.
- Chỉ nhận `WebImage` WebP đúng khuôn, chỉ có chunk ảnh đăng web được phép (`_check_web_image`, `client.py:1422`): byte trần, `WebImage` chứa JPEG, rỗng, `bytearray`, cỡ sai, MIME sai đều bị từ chối trước khi gửi.
- Tên file chỉ từ `naming.image_file_name` (`client.py:1074`) với `category`, `area`, `project_code` (chuỗi đã chuẩn hóa) và alt đã duyệt (đã gỡ ký tự ngắt); tránh trùng trong bài (`-2`). `DraftImage` không có trường nào nhận tên thư mục hay tên file gốc (`test_draft_image_khong_co_cho_cho_ten_file_goc_hay_thu_muc`). Mã công trình sai mẫu không vào tên file. Ảnh AI: `minh-hoa-ai-…`, không mã công trình.
- Trong bài, `src` là địa chỉ file đầy đủ website trả về; không `wp-image-N`, không `srcset`/`sizes` (`test_anh_dung_trong_bai_la_file_day_du_va_khong_co_wp_image`).

**Yêu cầu 3. alt/chú thích và `<figure>` (Lá Chắn T-050 điều kiện 4, T-046 số 7).**
- `plain_image_text` (`html.py:46`): `unbreak_autolinks` → `unescape_link_syntax` (gỡ `]\(`, `]\[`, `]\:`) → `normalize_meta` (bỏ mọi ký tự vô hình còn lại như U+202E, gạch nối mềm; gộp khoảng trắng); ký tự điều khiển thành dấu cách. Rồi `html.escape(…, quote=True)` khi ghép vào HTML (`html.py:93`).
- `alt_text` gửi qua REST là chữ đã gỡ ký tự rộng 0 (chữ thường, WordPress tự escape khi in). Tiêu đề và chú thích media (WordPress hiện như HTML) được `html.escape(…, quote=True)` (`client.py:1099-1101`).
- `<figure>` dựng bằng code, qua `sanitize_html` lần cuối (`html.py:99`); bộ lọc mà bỏ `src` thì dừng. Cả bài vẫn qua `sanitize_html` trong `create_draft`. Test: chữ người dùng gõ `"><img onerror…>`, `</figcaption><script>…` chỉ còn là chữ, trình duyệt chỉ thấy đúng 3 thẻ do code dựng (`test_chu_nguoi_dung_go_the_html_bi_escape_khong_thanh_the`); `src` lạ (`http:`, `javascript:`, `data:`, `//`, dấu nháy, dấu cách, `<`, `\`, xuống dòng, quá dài) bị từ chối.
- `class`: **không mở trong `sanitize.py`** (xem Quyết định 1). Lớp duy nhất app ghi ra là `wp-block-image` trên `<figure>` (`test_anh_dung_trong_bai…`: mọi `class=` trong nội dung gửi đi đúng bằng `["wp-block-image"]`).

**Yêu cầu 4. Chỉ ghi vào nháp do app tạo, qua danh sách đường cố định; không `publish`/`future`.**
- Thứ tự lệnh thật (`test_thu_tu_lenh_va_moi_duong_trong_danh_sach`): `POST /wp/v2/media` → `POST /wp/v2/media/<mã vừa trả>` (cho từng ảnh) → `POST /wp/v2/posts` (tạo nháp) → `GET /wp/v2/posts/42` (hỏi còn nháp, `_own_draft`) → `POST /wp/v2/posts/42` `{"featured_media": …}`. Mọi cặp đều qua `is_allowed_route`; không thêm đường mới, không thêm `params` (LC-T042-1).
- Không sửa bài có sẵn: nội dung có ảnh được gửi ngay lúc **tạo** nháp; ảnh đại diện qua `set_featured_image` có sẵn (`client.py:1030`). Bài không còn nháp thì không ghi, trả `message` (`test_bai_khong_con_nhap_thi_khong_dat_anh_dai_dien`).
- Duyệt mọi giá trị trong JSON của mọi lệnh ghi: không có `publish`/`future`; `status` chỉ ở lệnh tạo nháp và bằng `"draft"`; lệnh ghi media chỉ có `alt_text`, `title`, `caption` (`test_khong_bao_gio_publish_future_va_chi_gui_truong_can_thiet`).
- Ghi alt chỉ cho đúng mã website vừa trả; câu trả lời nói về ảnh khác thì dừng (`test_ghi_alt_tra_loi_anh_khac_thi_dung`). Địa chỉ ảnh phải `https://` trên đúng website (`is_site_link`, `client.py:1109`), không thì dừng trước khi tạo nháp.

**Điều kiện Lá Chắn T-049 điều kiện 7 và T-067:** chưa đáp ứng ở phiếu này (không phải việc của Thợ Máy): trước khi gộp T-054, T-067 (LC-T049-1, GPS sai khuôn) phải gộp và Chỉ Huy thử 3–5 ảnh thật. Phiếu này không phụ thuộc code của T-067 (chỉ dùng `WebImage` đã có).

## Quyết định trong lúc làm

1. **Không mở `class` trong `sanitize.py`.** Thiết kế T-046 ghi "chưa cho `class`", nhưng thực tế `class` đã nằm trong `GLOBAL_ATTRS` (`sanitize.py:648`, từ T-004): mọi thẻ đều giữ `class` với mọi giá trị (đã thử `sanitize_html('<p class="evil x">')` → giữ nguyên). Vì vậy không cần mở gì. Đồng thời **không dùng `wp-image-<mã>`**: theo hiểu biết về mã WordPress (`wp_filter_content_tags` tìm `wp-image-(\d+)` để thêm `srcset`/`sizes`; chưa xác minh trên site), có lớp này thì điện thoại sẽ tải cỡ nhỏ WordPress tạo, đã bị bỏ EXIF, trái quyết định 5A. Siết `class` về đúng mẫu `wp-image-\d+`/`wp-block-image` trên `img`/`figure` là việc nên làm (xem Đề xuất), nhưng sẽ đổi kết quả của test cũ `tests/test_sanitize.py:143-144` (đang đòi giữ `<p class="a">`), file ngoài phạm vi phiếu này.
2. **Thứ tự: tải ảnh → tạo nháp có sẵn ảnh → đặt ảnh đại diện bằng `set_featured_image`** (theo chỉ dẫn của Chỉ Huy). Thiết kế T-046 mục 6 cho phép gửi `featured_media` ngay lúc tạo nháp (ít hơn 2 request); tôi giữ `set_featured_image` để đi qua bước hỏi lại "còn nháp". Lỗi ở bước này không mất bài: trả `DraftWithImages` kèm `message`.
3. Ảnh chưa "gắn" vào bài trong thư viện Media (trường `post` của media): muốn gắn phải thêm tham số khi tải hoặc thêm một lệnh ghi; không cần cho bài, nên không làm.
4. Tiêu đề media của ảnh AI bắt đầu bằng `[AI] ` (thiết kế T-046 mục 4); ảnh thật: tiêu đề là alt.
5. Giới hạn: alt tối đa 500 ký tự, chú thích 1000, mỗi thẻ 200 (alt AI gợi ý mặc định 125, chú thích 200); quá thì báo trước khi gửi.

## Rủi ro và điểm cần chú ý

- **Shortcode trong alt/chú thích (T-061).** Chú thích nằm trong nội dung bài (`<figcaption>`), WordPress chạy shortcode trong nội dung, và site có Code Snippets. Alt/chú thích (AI gợi ý, người dùng duyệt) có `[code_snippet …]` thì sẽ chạy như chữ thân bài hiện nay. Không chặn được ở `html.py` vì `create_draft` lọc lại cả bài và giải mã `&#91;` về `[`. T-061 phải phủ cả `<figcaption>` và thuộc tính `alt` (làm ở `sanitize_html` thì phủ được). Suy luận, chưa thử trên site.
- **Chưa xác minh trên site thật** (không có site thử, không gọi mạng): website nhận WebP; `alt_text` qua REST được WordPress làm sạch bằng `sanitize_text_field`; không `wp-image-N` thì WordPress không thêm `srcset`; plugin nén ảnh/CDN có thể xóa EXIF hay đổi `src`; nếu site phục vụ ảnh từ tên miền khác (CDN) thì `is_site_link` sẽ chặn và báo lỗi sau khi ảnh đã lên thư viện. Cần phiếu thử thật với một bài nháp (như T-059): tải file ảnh từ web về, kiểm GPS.
- Mở bài trong trình soạn khối (Gutenberg): nội dung không có chú thích khối nên hiện là một khối "Cổ điển"; "Chuyển thành khối" cho khối ảnh không gắn mã media (vì không có `wp-image-N`). Ảnh vẫn hiện đúng.
- Chú thích media đã escape nên nếu mở ô "Chú thích" trong trang quản trị Media, dấu `"`, `&` có thể hiện dạng `&quot;`, `&amp;` (trang web hiện đúng). Chỉ là hình thức.
- Câu lỗi của bước tải/tạo nháp nối thêm câu cố định của phiếu này vào câu lỗi cũ của client, nên vẫn có thể kèm "(WordPress: …)" (LC-T042-4, Thấp, có từ trước).
- Khe "kiểm rồi ghi" khi đặt ảnh đại diện giống LC-T042-2 (bài bị đăng đúng khe dưới một giây): ghi ảnh đại diện vào chính bài app vừa tạo, không hại bài cũ.
- Thẻ `category`, `area` chỉ được kiểm kiểu và độ dài: bảo vệ tên khách nằm ở `ImageTags` (T-052) mà T-056 phải dùng (Lá Chắn T-049 N8).

## Đề xuất

**Cho T-056 (giao diện):**
- Gọi `create_draft_with_images` **chỉ khi người dùng bấm «Gửi nháp»**; trước nút ghi rõ ảnh (có GPS) xem được công khai ngay khi tải, kể cả khi bài là nháp (Lá Chắn T-046 số 8).
- Nối với `ImageTags` (T-052): `DraftImage(web, alt=…, caption=…, category=tags.category, area=tags.area, project_code=tags.project_code, ai_generated=(tags.source == SOURCE_AI))`. Chỉ lấy thẻ từ `ImageTags` (đã kiểm theo danh sách cố định), không bao giờ truyền tên thư mục, tên file gốc.
- `alt`/`caption`: truyền chữ trong ô nhập người dùng đã duyệt (không truyền bản đã `escape_markdown`, vì dấu `\` của bản đó sẽ thành chữ).
- `web`: kết quả `make_web_image(..., **load_image_settings())`; không tự sửa `web.data`.
- Hiện `DraftImagesError`: `st.error(str(exc))` và liệt kê `exc.uploaded` (tên file, link sửa) bằng chữ thường/`escape_markdown`; `exc.maybe_uploaded` thì nhắc kiểm thư viện. `result.message` (chưa đặt được ảnh đại diện) bằng `st.warning`. Không `unsafe_allow_html`.
- Có thể nên để Chỉ Huy thêm `DraftImage`, `DraftImagesError`, `DraftWithImages`, `UploadedImage` vào `seo_app/wordpress/__init__.py` (ngoài phạm vi phiếu này); hiện import từ `seo_app.wordpress.client`.

**Cho Soi Lỗi:** thử `parts` là danh sách bị đổi trong lúc chạy, `DraftImage` lớp con, `WebImage` lớp con có `data` đổi theo lần đọc; website trả `source_url` lạ (có `%22`, `#`, tên miền con, cổng khác, chữ hoa); trả 201 kèm `id` của ảnh cũ; lỗi ở ảnh thứ N với N lớn; alt chỉ toàn dấu `\`, toàn ký tự ngắt, có `]\:` đầu dòng; chú thích nhiều dòng; hai `DraftImage` khác nhau cùng một `WebImage`; tiêu đề chỉ có thẻ HTML.

**Cho Lá Chắn:** soát `_check_web_image`, `figure_html` (`_check_src`, kiểm sau `sanitize_html`), `_describe_draft_media` (chỉ 3 trường, đúng mã ảnh, `is_site_link`), cách ghép câu lỗi `_draft_images_error`, nhánh `except Exception`. Cân nhắc một phiếu siết `class` trong `sanitize.py` (chỉ `img`/`figure`, từng lớp khớp toàn bộ `wp-image-\d+` hoặc `wp-block-image`, bỏ lớp lạ; sửa kèm `tests/test_sanitize.py:143-144`). Xếp T-061 (shortcode) trước khi bật tính năng cho người dùng.

**Cho Chỉ Huy:** trước khi gộp: T-067 gộp và thử 3–5 ảnh thật (Lá Chắn T-049 điều kiện 7). Sau khi có giao diện: một phiếu thử thật với **một** bài nháp: tải file ảnh từ web về kiểm GPS, xem nguồn trang không có `srcset` cho ảnh, ảnh hiện đúng trên điện thoại.

## Câu hỏi cho chủ dự án

Không có.

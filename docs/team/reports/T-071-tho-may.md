# Báo cáo T-071 · Dọn lỗi Thấp phần chèn ảnh vào nháp (sau T-054)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-071](../tickets/T-071-don-loi-thap-chen-anh-nhap.md) |
| Ngày nộp | 2026-10-23 (làm 22/10, chủ dự án cho dừng lúc 18:34; làm tiếp sáng 23/10) |
| Kết quả | Hoàn thành (yêu cầu 1–6). Yêu cầu 5 làm theo **cách A** Chỉ Huy chọn (2026-10-22 18:16): bỏ `ai_generated`, sửa cơ học 7 chỗ test ngoài phạm vi (bảng ở mục 4) |

## Tóm tắt (cho chủ dự án)

- Khi gửi bài nháp kèm ảnh mà website trục trặc **đúng lúc tạo bài** (chậm quá giờ, mất mạng, lỗi máy chủ, trả lời sai dạng), phần mềm nay báo «Bài nháp có thể vẫn đã được tạo» và dặn mở trang quản trị kiểm **Bài viết → Nháp** trước khi gửi lại. Trước đây nó chỉ bảo «thử lại sau», nên bấm gửi lại có thể ra bài nháp trùng và thêm một bộ ảnh công khai. Khi website từ chối rõ ràng (lỗi 4xx) thì câu báo nói «Chưa tạo bài nháp».
- Alt và chú thích của **ảnh AI** kiểu «Minh họa [Trước khi sửa]: cổng sắt gỉ sét» lên website không còn dấu «\» thừa. Lớp chặn shortcode của T-061 giữ nguyên.
- Phần mềm chỉ ghi alt cho ảnh mà website xác nhận **vừa tạo mới**. Nếu website trả cùng một mã cho hai ảnh (có thể là ảnh đã có sẵn) thì dừng, không sửa ảnh đã có trên website.
- Tên file ảnh công khai chỉ lấy từ thẻ trong danh sách cố định (mã công trình, hạng mục, khu vực). Phần gửi nháp không còn nhận chữ tự do, nên tên thư mục hay tên khách không thể lọt vào tên file.
- Hôm nay giao diện chưa thấy gì khác: nút «Gửi nháp» nằm ở màn hình chọn ảnh T-056 (chưa làm). Phiếu này dọn đường cho T-056.

## 1. Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `DraftImage` nhận `tags: ImageTags` thay cho `category`, `area`, `project_code`, `ai_generated` (`:388-417`); client kiểm đúng lớp và dựng lại thẻ (`:1157-1165`), ảnh AI theo `tags.is_ai` (`:1181`, `:1185`, `:1203`). Lệnh tải ảnh của phần gửi nháp phải trả `201` (`_post_media(new_only=True)`, `:973-994`, `:1064`); mã ảnh trùng trong một lần gửi thì dừng (`:1066-1069`). `DraftImagesError` có thêm `maybe_draft` và tài liệu đúng (`:447-474`); lỗi ở lệnh tạo nháp không phải 4xx rõ ràng thì bật cờ và câu báo «có thể đã có» (`:1059`, `:1089`, `:1099-1123`, `_draft_images_error` `:1579-1602`). 4 câu báo mới, `_DRAFT_UNEXPECTED` bỏ câu khẳng định «Chưa tạo bài nháp» (`:211-236`). Bỏ hằng `MAX_IMAGE_TAG_CHARS` (không còn nơi dùng) |
| `seo_app/images/html.py` | `plain_image_text` gỡ «\» của `]\:` ở mọi chỗ trong dòng (`:46-52`, `:79`); chốt cuối của `figure_html` chỉ đọc thẻ `<img>` (`:53-55`, `:123-130`); docstring module, `plain_image_text` |
| `tests/test_wordpress_images.py` | 44 ca mới `test_t071_*` (mục 5); test cũ của chính T-054 đổi sang `tags=ImageTags(...)`; ca «kiểm sai thì chưa gửi gì» thay 3 ca thẻ chữ tự do bằng 6 ca thẻ không phải `ImageTags` (mục 3, YC5). File: 90 ca → 137 ca |
| `tests/test_soi_loi_t054.py` | Gỡ 2 `xfail` (SL-T054-1, SL-T054-3; 4 ca), sửa lời docstring đầu file cho đúng; 4 chỗ dựng `DraftImage` sửa cơ học (mục 4) |
| `tests/test_shortcode_t061.py` | 1 chỗ sửa cơ học (mục 4), thêm 1 dòng import |
| `tests/test_soi_loi_t061.py` | 1 chỗ sửa cơ học (mục 4), thêm 1 dòng import |
| `docs/team/reports/T-071-tho-may.md` | Báo cáo này |

Không sửa `seo_app/sanitize.py`, `seo_app/storage/drafts.py`, `app/**`, `config/**` (`git diff --stat a9338f7` chỉ có 6 file trên và báo cáo). `upload_media` (trang Kết nối WordPress) không đổi. Không thêm thư viện.

## 2. Cách sửa từng yêu cầu

### YC1 · LC-T054-2 (= SL-T054-3): lỗi ở lệnh tạo nháp

- Biến `creating` bật ngay trước `self.create_draft(...)` (`client.py:1089`). Khi lỗi, `unsure = status is None or not 400 <= status < 500` (`:1102`): chỉ lời từ chối 4xx là rõ ràng «website không làm»; hết giờ, mất mạng, lỗi SSL, 5xx, chuyển hướng 3xx, câu trả lời 2xx sai dạng (không phải JSON, `id` sai kiểu) đều là «có thể đã chạy xong». `maybe_draft = creating and unsure`.
- Câu báo (`_draft_images_error`, `:1579`): lý do, rồi `_DRAFT_MAYBE_CREATED` («Bài nháp có thể vẫn đã được tạo dù có lỗi: trước khi gửi lại, mở trang quản trị WordPress, kiểm tra Bài viết → Nháp (và Media → Thư viện)…»), rồi danh sách ảnh đã lên như cũ. Lệnh tạo nháp bị từ chối 4xx thì thêm «Chưa tạo bài nháp.» (`:1104-1105`).
- Lỗi lạ (không phải lỗi WordPress): `_DRAFT_UNEXPECTED` không còn khẳng định «Chưa tạo bài nháp»; câu này chỉ thêm khi lỗi xảy ra **trước** lệnh tạo nháp (`:1116-1118`), còn lỗi trong lúc tạo nháp thì `maybe_draft`.
- Tài liệu `DraftImagesError` (`:447-459`): lỗi ở bước tải ảnh, ghi alt (chưa gửi lệnh tạo) **hoặc ở chính lệnh tạo nháp**; mô tả `maybe_draft`; «`maybe_draft` tắt thì chưa có bài nháp nào được tạo». Tài liệu `create_draft_with_images` ghi thêm.
- Cùng một quy tắc «không phải 4xx rõ ràng» cho `maybe_uploaded` (trước đây chỉ «không có mã hoặc ≥ 500»): nay chuyển hướng 3xx lúc tải ảnh cũng nhắc «ảnh có thể vẫn đã lên». Báo thừa, an toàn hơn; test cũ không đổi.

### YC2 · LC-T054-3 (= SL-T054-1): dấu «\» trong alt, chú thích ảnh AI

- Nguyên nhân (Soi Lỗi, Lá Chắn): `escape_link_syntax` chỉ thêm «\» trước «:» khi «[» mở nhãn ở **đầu dòng**, `unescape_link_syntax` cũng chỉ gỡ khi «[» còn ở đầu dòng; `clean_suggestion` ghép tiền tố «Minh họa» **sau** bước escape, nên «[» ra giữa dòng và «\» còn lại.
- Sửa ở `plain_image_text` (`html.py:79`), tức là **sau** khi đã ghép tiền tố và ngay sau `unescape_link_syntax`: gỡ «\» nằm giữa «]» (không bị escape: đứng sau một số chẵn dấu «\») và «:» ở mọi chỗ trong dòng (`_LABEL_COLON_ESCAPE`, `:52`). Phủ cả chữ người dùng tự gõ thêm phía trước nhãn. Chữ gửi WordPress không phải Markdown nên bỏ dấu này không hại gì.
- Không đụng «[», «]»: `sanitize_html` và `escape_shortcodes` vẫn đổi chúng thành `&#91;`, `&#93;` **sau** bước này (T-061 không nới). Test: nội dung gửi đi không còn «[» «]» trần, `alt_text`, `title`, `caption` gửi REST đúng dạng đã vô hiệu (`test_t071_anh_ai_chu_mo_dau_ngoac_vuong_khong_con_dau_gach_cheo`, `test_t071_go_dau_gach_cheo_khong_mo_lai_shortcode`), cùng toàn bộ `tests/test_shortcode_t061.py`, `tests/test_soi_loi_t061.py` vẫn qua.
- `plain_image_text` chạy lại không đổi (test có kiểm).

### YC3 · LC-T054-5: mã `201`, mã ảnh trùng

- `_post_media(..., new_only=True)` (`client.py:973-994`): phần gửi nháp chỉ nhận `201 Created` (WordPress lõi luôn trả 201 khi tạo ảnh). Mã khác (200, 202, 204…) có thể là mục **có sẵn** (plugin trả lại ảnh trùng byte): dừng **trước** khi ghi alt, câu `_MEDIA_NOT_CREATED`, không có tên trong `uploaded`, `maybe_uploaded` bật (ảnh có thể đã lên).
- Mã website trả đã có trong `uploaded` của lần gửi này (`:1066-1069`): dừng với `_MEDIA_SAME_ID`, **không** gửi lệnh ghi alt cho mã đó (alt ảnh trước không bị đè), ảnh trước vẫn được liệt kê, `maybe_uploaded` bật (ảnh vừa gửi có thể đã lên với mã khác). Cùng một đối tượng `DraftImage` đặt hai chỗ vẫn chỉ tải một lần như cũ (G10).
- Chỉ áp dụng cho phần gửi nháp kèm ảnh (phạm vi phiếu). `upload_media` của trang Kết nối WordPress giữ nguyên (`new_only` mặc định tắt): xem Đề xuất.

### YC4 · LC-T054-6: chốt cuối của `figure_html`

`html.py:123-130`: lấy các thẻ `<img …>` trong kết quả của bộ lọc (`_IMG_TAG`; giá trị thuộc tính đã escape nên thẻ kết thúc ở dấu «>» đầu tiên, chữ chú thích có «<» đã thành `&lt;`), phải có **đúng một** thẻ, và ` src="…"`, ` alt=` phải nằm **trong thẻ đó**. Chú thích `chữ src="https://…" alt=y` không còn làm chốt này tưởng ảnh vẫn có `src`. Thử trên bản cũ (mục 6): bộ lọc bỏ `src`, bỏ `alt` hay bỏ hẳn thẻ ảnh thì bản cũ **không** báo lỗi, bản mới báo lỗi.

### YC5 · LC-T054-4 (phần code): `DraftImage` nhận `ImageTags`

- `DraftImage(image, alt, caption="", tags=ImageTags(), featured=False)` (`client.py:396-417`); mặc định là ảnh thật chưa có thẻ (nhập `ImageTags` muộn như các module ảnh khác, `_no_tags` `:388`). Không còn trường chữ tự do nào; trường `ai_generated` bỏ hẳn (cách A): ảnh AI chỉ theo `tags.source == SOURCE_AI` (một nguồn duy nhất).
- `_plan_draft_images` (`:1157-1165`), **trước mọi request**: `type(part.tags) is ImageTags` (không nhận chữ, dict, đối tượng giả dạng, lớp con), rồi `replace(part.tags)` dựng lại thẻ để chạy lại bước kiểm danh sách cố định của `ImageTags.__post_init__`: thẻ bị sửa sau khi tạo (`object.__setattr__`) bị từ chối với câu cố định «Thẻ của ảnh thứ N không hợp lệ. Chưa gửi gì lên website.» (không chép chữ của thẻ). Tên file chỉ từ `image_file_name(category=tags.category, area=tags.area, project_code=tags.project_code, alt=…, ai_generated=tags.is_ai)`; tiêu đề media `[AI] …` theo cùng cờ.
- Điều kiện 4 của Lá Chắn T-049 nay do code bảo đảm: chữ tự do (tên thư mục, tên khách, địa chỉ) không thành `ImageTags` được (`TagError`), nên không tới được bước đặt tên file.

### YC6 · gỡ `xfail`

- SL-T054-3 (3 ca): trước khi gỡ, lần chạy ngày 22/10 trên code đã sửa cho đúng **3 XPASS(strict)**; gỡ khối `@pytest.mark.xfail(...)` (5 dòng), không đổi thân test.
- SL-T054-1 (1 ca): gỡ khối `xfail` (4 dòng); chỉ đổi lời gọi `DraftImage(..., ai_generated=True)` thành `tags=ImageTags(source=SOURCE_AI)` (chỗ số 5 ở mục 4), không đổi `assert` nào. Test qua.
- Docstring đầu file ghi «SL-T054-1 và SL-T054-3 [sửa] ở T-071 (đã gỡ `xfail`)». Trong `tests/test_soi_loi_t054.py` không còn `xfail` nào.

## 3. Ghi chú về test cũ của T-054 trong `tests/test_wordpress_images.py`

File này thuộc phạm vi phiếu (test của chính Thợ Máy T-054). Thay đổi trên test cũ, để Soi Lỗi soát theo R5:

| Test cũ | Đổi thành | Lý do |
|---|---|---|
| 4 test dựng `DraftImage(..., category=…, area=…, project_code=…)` | `tags=ImageTags(...)` cùng giá trị; `assert` giữ nguyên | Trường cũ không còn |
| `test_anh_ai_co_tien_to_ten_file_va_tieu_de_khong_ma_cong_trinh` (`category`, `project_code="CT012"`, `ai_generated=True`) | `tags=ImageTags.for_ai_image("Cổng inox")`, thêm `assert` `ImageTags(source=SOURCE_AI, project_code="CT012")` báo `TagError`; `assert` tên file, tiêu đề giữ nguyên | Ảnh AI không mang được mã công trình (T-052): ý «không mã công trình» nay do lớp thẻ bảo đảm |
| `test_ma_cong_trinh_sai_mau_khong_vao_ten_file` | Thay bằng `test_the_nhap_tay_duoc_chuan_hoa_vao_ten_file` và hai test mới chặt hơn: `test_t071_chu_tu_do_khong_thanh_the_duoc` (3 ca, `TagError`), `test_t071_the_bi_sua_sau_khi_tao_bi_chan_truoc_khi_gui` (3 ca: mã công trình, hạng mục, khu vực bị sửa thành chữ tự do → dừng, 0 request) | Chữ tự do không còn đường vào tên file |
| `test_draft_image_khong_co_cho_cho_ten_file_goc_hay_thu_muc` | Tập trường mong đợi đổi thành `{"image", "alt", "caption", "tags", "featured"}`, thêm `assert` mặc định `ImageTags()` | Đúng ý test: không trường nào nhận đường dẫn, tên thư mục, chữ tự do |
| `_bad_cases`: «thẻ không phải chữ», «thẻ quá dài», «ai_generated lạ» | «thẻ là chữ», «thẻ là dict», «thẻ giả dạng», «thẻ lớp con», «thẻ bị sửa sau khi tạo», «featured lạ» (cùng test `test_kiem_sai_thi_chua_gui_gi`: lỗi, 0 request) | Ba ca cũ không còn dựng được |

## 4. Bảng trước/sau 7 chỗ test ngoài phạm vi (cách A, Chỉ Huy cho phép)

Chỉ đổi lời gọi dựng `DraftImage` (và thêm dòng import `ImageTags`, `SOURCE_AI`, `TagError`). Không đổi `assert`, dữ liệu thử, `parametrize` hay điều kiện kiểm nào khác. Số dòng theo bản mới.

| # | Chỗ | Trước | Sau | Điều kiện kiểm |
|---|---|---|---|---|
| 1 | `tests/test_soi_loi_t054.py:291-294` (`test_byte_va_moi_lenh_gui_di_khong_co_ten_khach_ten_file_goc`) | `DraftImage(web, alt="Cổng inox", category="Cổng inox", area="Tân Phú")` | `DraftImage(web, alt="Cổng inox", tags=ImageTags(category="Cổng inox", area="Tân Phú"))` (xuống dòng cho đủ 100 ký tự) | Không đổi (tên file `cong-inox-tan-phu.webp`, không chữ khách nào trong mọi lệnh, GPS còn) |
| 2 | `tests/test_soi_loi_t054.py:342-346` (`test_ten_file_chi_lay_tu_image_file_name`, ảnh 1) | `DraftImage(web, alt=alt, category="Cổng inox", area="Tân Phú", project_code="CT012")` | `DraftImage(web, alt=alt, tags=ImageTags(category="Cổng inox", area="Tân Phú", project_code="CT012"))` | Không đổi (tham số gửi `image_file_name` vẫn ⊆ {`category`, `area`, `project_code`, `alt`, `ai_generated`, `taken`}) |
| 3 | `tests/test_soi_loi_t054.py:347-349` (cùng test, ảnh 2) | `DraftImage(web, alt="Minh họa cổng", category="Cổng inox", ai_generated=True)` | `DraftImage(web, alt="Minh họa cổng", tags=ImageTags(source=SOURCE_AI, category="Cổng inox"))` | Không đổi |
| 4 | `tests/test_soi_loi_t054.py:371-386` (`test_ten_file_khong_the_chen_header_hay_doi_duoi`, 7 chuỗi độc) | `send(wp_client, [DraftImage(web, alt="Cổng", category=category)])` rồi kiểm header | **Thêm** (chặt hơn): `ImageTags(category=category)` báo `TagError`; `DraftImage(web, alt="Cổng", tags=category)` báo `WordPressError`, `fake_wp.requests == []`. **Giữ** ý kiểm cũ: chuỗi độc đi qua cùng `image_file_name` bằng chữ tự do duy nhất còn vào tên file (alt của ảnh không có thẻ): `send(wp_client, [DraftImage(web, alt=category)])` rồi kiểm header | Giữ đủ 7 chuỗi; 2 `assert` header cũ giữ nguyên (`attachment; filename="[a-z0-9-]+\.webp"`, không `\r`, `\n`) |
| 5 | `tests/test_soi_loi_t054.py:483-490` (`test_sl_t054_1_…`) | `@pytest.mark.xfail(strict=True, reason="SL-T054-1: …")` và `DraftImage(web, alt=…, caption=…, ai_generated=True)` | Gỡ `xfail` (YC6); `DraftImage(web, alt=…, caption=…, tags=ImageTags(source=SOURCE_AI))` | Không đổi (5 `assert` giữ nguyên) |
| 6 | `tests/test_shortcode_t061.py:420` (`test_ngoac_vuong_thuong_trong_alt_chu_thich_van_hien_dung`) | `DraftImage(web, alt=alt, caption=caption, ai_generated=True)` | `DraftImage(web, alt=alt, caption=caption, tags=ImageTags(source=SOURCE_AI))` | Không đổi |
| 7 | `tests/test_soi_loi_t061.py:244` (`test_moi_lenh_ghi_khong_con_ngoac_vuong_tran`, 14 ca) | `DraftImage(web, alt=chu, caption=chu, ai_generated=True)` | `DraftImage(web, alt=chu, caption=chu, tags=ImageTags(source=SOURCE_AI))` | Không đổi |

`git diff --numstat a9338f7`: `tests/test_shortcode_t061.py` +2/−1, `tests/test_soi_loi_t061.py` +2/−1, `tests/test_soi_loi_t054.py` +28/−15 (gồm 2 khối `xfail` gỡ và câu docstring đầu file). Ngoài 7 chỗ này, không còn chỗ nào trong repo gọi `DraftImage` của phần gửi nháp với `ai_generated`, `category`, `area`, `project_code` (grep `seo_app`, `app`, `scripts`, `tests`; `DraftImage` trong `seo_app/storage/drafts.py` là lớp khác, của nháp đã lưu).

## 5. Test mới (`tests/test_wordpress_images.py`, 44 ca `test_t071_*`)

| Test | Kiểm gì |
|---|---|
| `test_t071_loi_khong_ro_o_lenh_tao_nhap_bao_bai_nhap_co_the_da_co` (8 ca) | Lệnh tạo nháp hết giờ, mất mạng, 500, 502 trang HTML, 301, 201 với `id` chữ, 201 `[]`, 200 HTML: `maybe_draft` bật, câu báo có «Bài nháp có thể vẫn đã được tạo», «Bài viết → Nháp», không có «Chưa tạo bài nháp», câu này đứng trước danh sách ảnh; ảnh vẫn được liệt kê; không lộ khóa; không lệnh xóa |
| `test_t071_lenh_tao_nhap_bi_tu_choi_4xx_thi_bao_chua_tao` (7 ca) | 400, 401, 403, 404, 409, 413, 429: `maybe_draft` tắt, câu báo «Chưa tạo bài nháp», giữ `status_code` |
| `test_t071_loi_truoc_lenh_tao_nhap_khong_bao_nhap_co_the_da_co` (4 ca) | Lỗi lúc tải ảnh, lúc ghi alt (5xx, hết giờ, mất mạng): `maybe_draft` tắt, chưa có lệnh tạo nháp |
| `test_t071_loi_la_o_lenh_tao_nhap_khong_khang_dinh_chua_tao`, `test_t071_loi_la_truoc_lenh_tao_nhap_van_bao_chua_tao` | Lỗi lạ trong lúc tạo nháp: «có thể đã có»; lỗi lạ trước đó: «Chưa tạo bài nháp»; `DraftImagesError` mặc định `maybe_draft=False` |
| `test_t071_plain_image_text_go_dau_gach_cheo_cua_nhan_giua_dong` | `]\:` giữa dòng, nhiều nhãn, cùng `](`, `][`; «]» đã escape giữ nguyên; chạy lại không đổi |
| `test_t071_anh_ai_chu_mo_dau_ngoac_vuong_khong_con_dau_gach_cheo` (2 ca) | Gợi ý AI qua `clean_suggestion(ai_generated=True)` → gửi: alt, chú thích trình duyệt đọc được đúng «Minh họa [Trước khi sửa]: …», «Ảnh minh họa (AI): [Lưu ý]: …»; không «\»; không «[» «]» trần trong nội dung; `alt_text`, `title` (`[AI] …`), `caption` gửi REST đúng dạng đã vô hiệu shortcode |
| `test_t071_nguoi_dung_go_them_chu_truoc_nhan_khong_con_dau_gach_cheo` | Người dùng gõ thêm chữ trước nhãn |
| `test_t071_go_dau_gach_cheo_khong_mo_lai_shortcode` | Gợi ý AI «[code_snippet id=1]: …»: sau khi gỡ «\», shortcode vẫn chỉ là `&#91;code_snippet id=1&#93;` |
| `test_t071_tai_anh_khong_phai_201_thi_dung_khong_ghi_alt` (3 ca) | 200, 202, 204: dừng, không ghi alt, không tạo nháp, nhắc «có thể vẫn đã lên» |
| `test_t071_anh_thu_hai_khong_phai_201_liet_ke_anh_dau` | Ảnh 2 trả 200: liệt kê ảnh 1, không ghi gì vào mã ảnh 2 |
| `test_t071_website_tra_cung_ma_anh_thi_dung_khong_ghi_de_alt` | Website trả mã 101 cho cả 2 ảnh: dừng, chỉ một lệnh ghi alt cho ảnh 101 («Ảnh một»), không tạo nháp |
| `test_t071_chu_thich_giong_thuoc_tinh_anh_van_dung_binh_thuong` | Chú thích `chữ src="…" alt=y` vẫn dựng bình thường, đúng một `<img>` |
| `test_t071_bo_loc_lam_hong_the_anh_thi_bao_loi_du_chu_thich_co` (4 ca) | Bộ lọc (giả) bỏ `src`, bỏ `alt`, bỏ thẻ ảnh, thêm thẻ ảnh thứ hai: báo `ImageHtmlError` dù chú thích có chữ giống thuộc tính |
| `test_t071_chu_tu_do_khong_thanh_the_duoc` (3 ca), `test_t071_the_bi_sua_sau_khi_tao_bi_chan_truoc_khi_gui` (3 ca) | Chữ tự do không thành `ImageTags`; thẻ bị sửa sau khi tạo bị chặn trước mọi request, câu báo cố định |
| `test_t071_anh_ai_lay_tu_the_nguon_anh`, `test_t071_anh_that_khong_co_tien_to_ai` | Ảnh AI theo `tags.source`: tên `minh-hoa-ai-…`, tiêu đề `[AI] …`; ảnh thật thì không |

## 6. Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, worktree `wt-T-071`, nhánh `team/T-071` (gốc `a9338f7`). Máy có các agent khác chạy song song.

```
$ uv run pytest -q -p no:cacheprovider tests/test_wordpress_images.py tests/test_soi_loi_t054.py \
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_client.py \
    tests/test_images_tags.py tests/test_app_pages.py tests/test_wordpress_paging_t042.py \
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py \
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py \
    tests/test_wordpress_site_link_t042.py tests/test_app_wordpress.py \
    tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t044.py -rxXf
(2026-10-23 07:32:57 → 07:37:52, mã cuối của nhánh)
2180 passed, 1 skipped, 6 xfailed in 267.21s (0:04:27)

$ uv run ruff check .
All checks passed!
```

- 16 file: đủ 7 file lời giao, thêm mọi `tests/test_wordpress*.py` (tiêu chí của phiếu) và các test cũ của `upload_media` (`_post_media` có thêm tham số). 0 hỏng, 0 XPASS.
- 6 `xfailed` là SL-T061-1 (4 ca), SL-T061-2 (2 ca) trong `tests/test_soi_loi_t061.py`, thuộc T-060, không liên quan phiếu này.
- 1 `skipped`: `tests/test_images_tags.py:1777` («máy không cho tạo symlink (Windows chưa bật Developer Mode)»), do máy, không liên quan.
- Ngày 22/10, trước khi gỡ `xfail` SL-T054-3, `uv run pytest tests/test_soi_loi_t054.py -rxXf` cho đúng 3 ca `[XPASS(strict)] SL-T054-3: …` trên code đã sửa.
- Quét bí mật: chép 7 file của phiếu (6 file đã sửa và báo cáo này) cùng toàn bộ patch `git diff a9338f7` vào thư mục riêng, thêm một file mồi có chữ tiếng Việt (một khóa AWS giả, một dòng gán mật khẩu giả), chạy `PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files .` (detect-secrets 1.5.0): mồi **bắt đủ 2/2**, 7 file và patch: **0**. Đã xóa mồi. Grep `api[_-]?key|password|secret|token` trên dòng thêm của patch: chỉ vòng lặp kiểm khóa giả của fixture không lộ trong câu báo (`tests/test_wordpress_images.py`).

Thử bản cũ và bản mới của `seo_app/images/html.py` (bản cũ lấy bằng `git show HEAD:seo_app/images/html.py` khi HEAD còn là `a9338f7`, nạp thành module riêng; script ở thư mục nháp của phiên, không commit):

```
cũ  | bỏ src của ảnh: KHÔNG báo lỗi -> …<img alt="Cổng" width="10" height="10"><figcaption>chữ src="https://example.com/wp-content/uploads/2026/10/cong-inox.webp" alt=y</figcaption>…
cũ  | bỏ alt của ảnh: KHÔNG báo lỗi -> …
cũ  | bỏ hẳn thẻ ảnh: KHÔNG báo lỗi -> …<span src="…" alt="Cổng" …>…
mới | bỏ src của ảnh: báo lỗi (Địa chỉ ảnh không hợp lệ (phải là https:// trên website, không có ký tự lạ).)
mới | bỏ alt của ảnh: báo lỗi (…)
mới | bỏ hẳn thẻ ảnh: báo lỗi (…)
cũ  | plain_image_text: 'Minh họa [Trước khi sửa]\\: cổng sắt gỉ sét'
mới | plain_image_text: 'Minh họa [Trước khi sửa]: cổng sắt gỉ sét'
```

## 7. Đối chiếu tiêu chí xong

- [x] YC1 LC-T054-2: `client.py:1089-1123`, `:447-474`; test mục 5 (21 ca) và `test_sl_t054_3_…` (3 ca, đã gỡ `xfail`).
- [x] YC2 LC-T054-3: `html.py:52`, `:79`; `test_t071_plain_image_text_…`, `test_t071_anh_ai_…` (2 ca), `test_t071_nguoi_dung_…`, `test_t071_go_dau_gach_cheo_…`, `test_sl_t054_1_…` (đã gỡ `xfail`); T-061 không nới (toàn bộ `test_shortcode_t061.py`, `test_soi_loi_t061.py` qua).
- [x] YC3 LC-T054-5: `client.py:993-994`, `:1064-1069`; 5 ca `test_t071_tai_anh_…`, `test_t071_anh_thu_hai_…`, `test_t071_website_tra_cung_ma_anh_…`.
- [x] YC4 LC-T054-6: `html.py:123-130`; 5 ca `test_t071_chu_thich_…`, `test_t071_bo_loc_…`; thử bản cũ/mới ở mục 6.
- [x] YC5 LC-T054-4 (phần code): `client.py:396-417`, `:1157-1185`; test mục 3, mục 5.
- [x] YC6: 2 khối `xfail` gỡ, không đổi điều kiện kiểm (mục 2, YC6).
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục 6). Toàn bộ test do Chỉ Huy chạy khi gộp.
- [x] Báo cáo này.

## 8. Rủi ro và điểm cần chú ý

- **Báo thừa «có thể đã có»:** lỗi lạ xảy ra trong `create_draft` **trước** khi gửi (ví dụ lúc lọc HTML) cũng bật `maybe_draft`. Chỉ làm người dùng kiểm mục Nháp thêm một lần; không bao giờ báo thiếu.
- **Mã 201:** nếu một plugin, tường lửa hay CDN trên site đổi `201` thành `200`, mọi lần gửi nháp kèm ảnh sẽ dừng ở ảnh đầu tiên (câu báo rõ, không ghi alt, ảnh đó có thể đã lên). WordPress lõi trả 201 (đọc từ mã nguồn, chưa thử trên site): nên kiểm ở phiếu thử thật T-059.
- **Gỡ «\» ở mọi `]\:`:** nếu người dùng cố ý gõ «]\:» trong alt thì dấu «\» mất. Chấp nhận được: alt, chú thích gửi WordPress là chữ thường, không phải Markdown (gợi ý của Soi Lỗi và Lá Chắn T-054).
- **Thẻ mặc định:** `DraftImage` không truyền `tags` thì là ảnh thật chưa có thẻ (như mặc định `ai_generated=False` trước đây). T-056 phải truyền `tags=` từ thẻ đã kiểm (`checked.tags`), nhất là với ảnh AI.
- **Lớp con của `ImageTags` bị từ chối** (kiểm đúng lớp, chặt hơn `isinstance` Lá Chắn gợi ý), vì lớp con có thể bỏ bước kiểm của `__post_init__`.
- Chưa thử trên website thật (test chỉ dùng site giả).

## 9. Đề xuất

- **Cho Chỉ Huy, ghi vào phiếu T-056:** (a) điều kiện «chỉ truyền thẻ từ `ImageTags`» của Lá Chắn T-054 nay do code bảo đảm: T-056 dựng `DraftImage(web, alt=…, caption=…, tags=checked.tags, featured=…)`; (b) ngoài `exc.uploaded`, `exc.maybe_uploaded`, hiện thêm `exc.maybe_draft` (câu báo đã có sẵn trong `str(exc)`) và nhắc kiểm mục Nháp trước khi bấm gửi lại.
- **Phiếu dọn sau (T-060 hoặc phiếu mới):** `upload_media` của trang Kết nối WordPress cùng loại rủi ro LC-T054-5 (ghi alt, tiêu đề, chú thích cho mã website trả mà không kiểm `201`). Có thể dùng `_post_media(..., new_only=True)`; theo grep, mọi site giả trả lời `POST /wp/v2/media` (thành công) trong test hiện có đều đã trả `201` (`tests/test_app_wordpress.py` thì thay hẳn `upload_media`). Ngoài phạm vi T-071 nên chưa làm.
- **Cho Soi Lỗi:** soát 7 chỗ ở mục 4 và các test cũ ở mục 3 theo R5.

## 10. Câu hỏi cho chủ dự án

Không có.

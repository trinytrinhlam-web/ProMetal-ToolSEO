# Báo cáo T-110 · Gắn ảnh «Gửi nháp» vào bài nháp vừa tạo (LC-T093-2, chủ dự án chọn 1A) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-110](../tickets/T-110-gan-anh-vao-bai-nhap.md) (đọc ở checkout chính) |
| Nhánh | `team/T-110` (commit `fc45a15`, tách từ `fd28bbc`); thử gộp với `main` `17b2a31` |
| Ngày nộp | 2026-10-30 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T110-1, việc 8, ngoài phạm vi phiếu). **Không lỗi nào bắt buộc sửa trước Lá Chắn.** Gộp `main` có **1 xung đột vị trí** ở `client.py` (gỡ bằng cách giữ cả hai hàm), xem mục 7 |

## Tóm tắt (cho chủ dự án)

- **Gắn ảnh vào bài nháp chạy đúng.** Gửi nháp xong, website giả của tôi (nhớ ảnh nào thuộc bài nào như WordPress) cho thấy mọi ảnh vừa tải đã thuộc đúng bài nháp vừa tạo. Ảnh có sẵn trên website không bị đụng. Nội dung bài, ảnh đại diện vẫn như cũ.
- **Không đường nào khác gắn hay gỡ ảnh khỏi bài.** Tôi thử 27 cách gọi sai: gắn vào bài khác, gỡ bài cha, gắn ảnh có sẵn, kèm khóa khác, đổi tên khóa, qua đường tạo bài, hẹn giờ, ghi SEO. Tất cả bị chặn trước khi gửi.
- **Gắn lỗi** (23 kiểu: mất mạng, lỗi máy chủ, trả lời lạ…): bài nháp vẫn tạo xong, không tải lại ảnh, không tạo bài thứ hai, không thử lại. Phần mềm báo rõ «chưa gắn được N ảnh» và cách kiểm. Trên trang Soạn bài, nút «Gửi nháp» vẫn khóa như trước.
- **1 lỗi nhỏ (Thấp), ngoài phạm vi phiếu:** gửi hỏng **trước** khi có bài nháp thì ảnh đã tải không có bài cha, nên vẫn hiện trong danh sách Media công khai. Câu báo lúc đó chỉ nói «xem được công khai qua đường dẫn», không nói ảnh còn trong danh sách. Câu nhắc mới trên nút lại hứa «gắn không được thì phần mềm báo». Nên sửa câu báo ở phiếu sau.
- **Việc cho Chỉ Huy khi gộp:** `main` mới có T-099 lượt 2 thêm một hàm vào đúng chỗ T-110 thêm hàm. Git báo xung đột; giữ cả hai hàm là xong. Tôi đã thử bản gộp đó: test client WordPress và «Gửi nháp» đều qua.
- **Việc của bạn:** không có (lượt thử thật với website như Thợ Máy đề xuất do Chỉ Huy sắp xếp).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t110.py` | Mới: 65 ca (62 qua, 3 `xfail(strict=True)` SL-T110-1). Website giả riêng `_ParentSite` (adapter `requests`): nhớ bài, ảnh, **bài cha** của ảnh (nhận `?post=` lúc tải và `post` lúc sửa ảnh), có sẵn ảnh 9 gắn vào bài đã đăng 7. Một ca giao diện mượn khung «Gửi nháp» của `test_app_images`, `test_t086_send_state` (như các file T-086, T-089). Không dùng site giả hay bảng kỳ vọng của Thợ Máy |
| `docs/team/reports/T-110-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu. Không gọi website thật (bộ chặn mạng của `tests/conftest.py` bật suốt).

## Kiểm theo yêu cầu

### 1. Khóa `post` chỉ đi được đúng lệnh gắn ảnh

- **Chạy đúng:** `create_draft_with_images` 2 ảnh (ảnh 2 làm ảnh đại diện): ảnh 101, 102 có bài cha 42; ảnh có sẵn 9 vẫn thuộc bài 7; bài 42 vẫn `draft`, ảnh đại diện 102. Lệnh gắn: thân đúng `{"post": 42}`, tham số đúng `_fields=id,post`; không lệnh nào có tham số `post` trên đường (kể cả lệnh tải ảnh).
- **Gọi thẳng `_request` 27 cách** (sau khi client đã có ảnh 101, 102 và bài 42): khóa `post` ở lệnh tạo bài, sửa bài (có, không kèm `featured_media`), tải ảnh (tham số `post`, thân JSON), sửa ảnh kèm `alt_text`, gắn vào bài 7 (không phải của client), gắn **ảnh có sẵn 9**, gỡ bài cha (`post: 0`), `post` dạng chữ, `True`, số thực, `null`, mảng, âm, 2⁶³, khóa `Post`, `post ` (thừa dấu cách), `post_parent`, `parent`, tham số `post` kèm `_fields`, `_method=PUT`, header `X-HTTP-Method-Override`, `_fields` có `description`, chạy ability kèm `post`, `GET` bài có tham số `post`, `GET` danh sách có `parent`: **27/27 bị chặn, 0 request**; ảnh 9 vẫn thuộc bài 7.
- Dấu hẹn giờ thật (`_RELEASE`) kèm `post`: chặn. Client khác (cùng website) gọi thẳng `_request` hay `_attach_media` cho ảnh, bài của client này: chặn. Đối chứng: đúng dạng, đúng ảnh, đúng bài của client thì gửi được.
- **Hàm công khai:** `create_draft`, `upload_media` (ảnh tải riêng **không** tự gắn vào bài nào), `set_featured_image`, rồi `create_draft_with_images`: khóa `post` chỉ có ở đúng 2 lệnh gắn ảnh của lần gửi kèm ảnh, đúng bài vừa tạo. Đọc mã nguồn: dict có khóa `"post"` chỉ ở `_attach_media`.

### 2. Lỗi khi gắn

- **23 kiểu lỗi ở lệnh gắn ảnh đầu tiên:** mất mạng, hết giờ, 301, 302, 400, 401, 403, 404, 429, 500, 502 HTML, 503, 200 không phải JSON, danh sách, thiếu `post`, `post` `null`, `0`, bài khác, chữ, `True`, mã ảnh khác, mã ảnh dạng chữ, JSON lồng 100.000 tầng. Mọi ca: hàm trả bài nháp 42 (không ném lỗi), `unattached == (101, 102)`; ảnh đại diện vẫn đặt (102); **2** lệnh tải ảnh (không tải lại), **1** lệnh tạo bài (không trùng), **1** lệnh gắn (không thử lại, không gắn tiếp ảnh sau); câu báo «chưa gắn được 2 ảnh… Media → Thư viện», không chép lời máy chủ (`MOI-T110`, `evil`, `<b>`), không chép `WORDPRESS_URL`.
- Lỗi ở ảnh thứ hai: chỉ báo 1 ảnh, ảnh 1 đã gắn. Gắn lỗi **và** ảnh đại diện lỗi: báo cả hai câu.
- **Khóa gửi trùng T-086, T-089** (ca giao diện, trang Soạn bài): gắn ảnh lỗi 500 thì trang báo «Đã tạo bài nháp trên WordPress» kèm cảnh báo «chưa gắn được…» (không chép lời máy chủ); nháp ghi «đã gửi (mã 501)», không còn «đang gửi»; 1 ảnh tải, 1 bài tạo; mở lại nháp ở phiên mới thì nút «Gửi nháp» khóa.

### 3. Nội dung, `srcset`, ảnh đại diện, thứ tự lệnh

Thứ tự đúng như báo cáo Thợ Máy: tải ảnh 1, ghi alt 1, tải ảnh 2, ghi alt 2, tạo nháp, gắn ảnh 1, gắn ảnh 2, kiểm nháp (`GET`), đặt ảnh đại diện. Nội dung bài trên website đúng bằng ghép `figure_html` (có `srcset` file đầy đủ, T-059) của hai ảnh với đoạn chữ; ảnh đại diện 102. Bài không ảnh: 0 lệnh gắn.

### 4. `GPS_PUBLIC_WARNING`

Câu mới nói đúng: ảnh và GPS **xem được công khai qua đường dẫn trực tiếp ngay khi tải lên**; phần mềm gắn ảnh vào bài nháp nên ảnh **không hiện trong danh sách Media công khai cho tới khi bài được đăng**; gắn không được thì phần mềm báo sau khi gửi; không tự xóa ảnh. Đúng với mọi lần gửi tạo được nháp. Riêng lời hứa «gắn không được thì phần mềm báo» chưa giữ ở lần gửi hỏng **trước** khi có nháp: SL-T110-1. Ghi nhận G2: giữa lúc tải ảnh và lúc gắn (vài giây tới vài phút khi nhiều ảnh) ảnh vẫn nằm trong danh sách công khai.

### 5. R5: test cũ đổi theo nhóm A/B/C, `xfail` LC-T093-2

Đối chiếu `git diff fd28bbc..fc45a15` với bảng «Test cũ đã đổi» của Thợ Máy: **đúng 18 hàm, không thay đổi ngoài bảng, không nới kiểm.**

| Nhóm | Hàm | Đối chiếu |
|---|---|---|
| A (11) | `test_app_images.py` ×3, `test_soi_loi_t056.py` ×1 | `(media,) = …` thành `*writes, attach = …`, thêm `attach == {"post": POST_ID}`, kiểm alt giữ nguyên trên `writes` |
| A | `test_soi_loi_t061.py::test_moi_lenh_ghi_khong_con_ngoac_vuong_tran` | Ảnh 102: 1 → 2 lệnh, lệnh cuối thân đúng `{"post": 42}`; ảnh 101 (tải bằng `upload_media`, không gắn) giữ 1 lệnh |
| A | `test_soi_loi_t081.py` ×2, `test_t081_alt_gach_cheo.py` ×2 (qua hàm phụ `_sent`, `_send_ai_image`; grep: mỗi hàm phụ đúng 2 nơi gọi, đúng 2 hàm trong bảng), `test_soi_loi_t083.py` ×1 | `len(writes) == 1` thành `== 2 and writes[1] == {"post": 42}`; lệnh ghi alt vẫn là `writes[0]` |
| A | `test_shortcode_t061.py::test_nhap_kem_anh_alt_chu_thich_…` | `[describe] =` thành `[describe, attach] =`, thêm `body(attach) == {"post": 42}`; vòng kiểm vô hiệu shortcode trên `describe` giữ nguyên |
| B (4) | `test_shortcode_t061.py::test_moi_lenh_ghi_co_fields_co_dinh_…` | Dict thành danh sách `(phương thức, đường, _fields)` so một lần (chặt hơn: so cả thứ tự lẫn `_fields` từng lệnh); vòng «không `content`, `excerpt`, `description`, `caption`» giữ |
| B | `test_soi_loi_t060.py` (`REAL_CALLS`), `test_soi_loi_t061.py::test_lenh_ghi_dung_nguyen_dia_chi_…`, `test_wordpress_images.py::test_thu_tu_lenh_…` | Chỉ chèn lệnh gắn vào đúng chỗ (sau lệnh tạo); `featured_media`, `message == ""` giữ |
| C (3) | `test_soi_loi_t054.py::test_moi_lenh_deu_qua_danh_sach_duong_…` | Nhánh mới chỉ cho lệnh vào `MEDIA/<mã>` có thân **đúng** `{"post": 42}`, đòi `_fields` đúng `id,post`; lệnh khác vẫn qua nhánh cũ |
| C | `test_soi_loi_t061.py::test_moi_lenh_ghi_wp_v2_deu_co_fields_an_toan` | 8 → 9 lệnh; `SAFE_FIELDS` thêm `post` (grep: chỉ hàm này dùng) |
| C | `test_wordpress_images.py::test_khong_bao_gio_publish_future_…` | `continue` chỉ cho lệnh Media thân đúng `{"post": 42}`, đặt **sau** kiểm «không `publish`, `future`, `status`» |

`test_soi_loi_t085.py` không đổi. `tests/test_la_chan_t093.py`: chỉ xóa 4 dòng dấu `xfail` LC-T093-2, thân test giữ nguyên.

### 6. Không lùi T-054, T-059, T-060, T-071, T-085, T-086, T-088, T-089, T-091, T-099

- Nơi gọi (grep `seo_app/`, `app/`, `tests/`): `create_draft_with_images` chỉ `app/views/write.py` («Gửi nháp») gọi; `_post_media` từ `upload_media` và `create_draft_with_images`; `_owns_attach` trong `_request` chỉ xét lệnh có khóa `post` (trước đây bị chặn ở mọi đường); `DraftWithImages.unattached` thêm ở cuối, có mặc định; app chỉ đọc `post`, `images`, `message` và hiện `message` bằng `st.warning(escape_markdown(…))` sẵn có.
- Câu ghim: «xem được công khai» (`test_app_images.py`, `test_la_chan_t056.py`) giữ trong câu nhắc mới; `_DRAFT_IMAGES_LEFT`, `_FEATURED_NOT_SET` không đổi.
- Chạy trên bản gộp (mục 7): 37 file, 0 hỏng.

### 7. Gộp thử với `main` `17b2a31`

- `git merge-tree --write-tree main HEAD`: **xung đột** ở `seo_app/wordpress/client.py`. Một khối duy nhất: `main` (T-099 lượt 2) thêm `_is_image_upload`, nhánh thêm `_is_media_attach`, cả hai ngay sau `_is_plain_request`. Xung đột vị trí, không xung đột logic: hai hàm độc lập; các chỗ khác của `_is_plain_request` (luật `data` của T-099, luật `post` của T-110) tự gộp được. Gỡ: giữ cả hai hàm (`_is_image_upload` trước). `ruff check` sạch. `tests/test_la_chan_t093.py` tự gộp (nhánh gỡ dấu LC-T093-2, `main` gỡ dấu LC-T093-3).
- Trên bản gộp đã gỡ (thêm file test của tôi), 37 file, 2 phần song song (máy đang chạy toàn bộ test): **5.308 passed, 3 xfailed, 0 failed** (5.076 + 232). 3 xfail là SL-T110-1 của tôi.
  - Phần A (client WordPress): T-110 (`test_t110_…`, `test_soi_loi_t110.py`, `test_la_chan_t093.py`), T-099 (`test_wordpress_release.py`, `test_soi_loi_t099.py`, `test_la_chan_t099.py`), canh `status` (`test_soi_loi_t037.py`, `test_safety.py`), `test_wordpress_client.py`, `test_wordpress_images.py`, T-054, T-060, T-061, T-071, T-081, T-083, T-085, T-088, T-091, T-059.
  - Phần B («Gửi nháp» trên trang): `test_app_images.py`, `test_soi_loi_t056.py`, `test_la_chan_t056.py`, T-086 (3 file), T-089 (3 file).

### 8. Ảnh của lần gửi hỏng trước khi có nháp

Xác nhận: lệnh tạo nháp bị từ chối (400), lỗi 500 hay hết giờ: `DraftImagesError` liệt kê ảnh 101, 102 đã tải; **không lệnh gắn nào**; hai ảnh không có bài cha nên vẫn nằm trong danh sách Media công khai. Câu báo không nói điều đó: **SL-T110-1 (Thấp)**.

### Đột biến

15 đột biến (script `mutate110.py`), mỗi lần chạy `test_soi_loi_t110.py`, `test_t110_gan_anh_vao_bai_nhap.py`, `test_la_chan_t093.py`: **13 bị bắt, 2 sống sót tương đương.**

| Đột biến | Ca hỏng: Soi Lỗi / Thợ Máy / Lá Chắn |
|---|---|
| T1 thân gắn ảnh cho kèm khóa khác | 1 / 1 / 0 |
| T2 `_is_media_attach` nhận mọi giá trị `post` | sống sót: `_owns_attach` vẫn đòi số nguyên thuộc bài của client |
| T3 `_is_media_attach` bỏ kiểm đường | sống sót: `post` ở đường khác bị `ALLOWED_JSON_KEYS` chặn, `_owns_attach` cũng chặn |
| T4 bỏ hẳn luật khóa `post` | 1 / 1 / 0 |
| T5 `_owns_attach` luôn đúng | 3 / 5 / 0 |
| T6 `_owns_attach` không kiểm ảnh | 1 / 1 / 0 |
| T7 `_owns_attach` không kiểm bài | 1 / 2 / 0 |
| T8 không so `post` trả về | 6 / 4 / 0 |
| T9 lỗi một ảnh vẫn gắn tiếp ảnh sau | 24 / 13 / 0 |
| T10 lỗi gắn thành lỗi gửi nháp | 25 / 20 / 0 |
| T11 ảnh không cần `201` vẫn là ảnh của client | 0 / 1 / 0 |
| T12 không gắn ảnh | 54 / 23 / 1 |
| T13 gắn lỗi mà không báo | 25 / 19 / 0 |
| T14 gắn cả khi bài vừa tạo không là nháp | 1 / 8 / 0 |
| T15 câu nhắc GPS về câu trước T-110 | 1 / 1 / 0 |

T2, T3: hai lớp chặn trùng nhau là đúng thiết kế (lớp dạng lệnh và lớp «của client»); muốn bắt riêng phải gọi thẳng `_is_plain_request`, không cần.

## Lỗi tìm ra

### SL-T110-1 · Thấp · Gửi hỏng trước khi có nháp: câu báo không nói ảnh còn trong danh sách Media công khai

- **Chỗ:** `seo_app/wordpress/client.py`, `_DRAFT_IMAGES_LEFT` (dùng trong `_draft_images_error`): «Đã có N ảnh lên thư viện Media trước khi lỗi… ảnh vẫn xem được công khai qua đường dẫn; nếu không dùng, hãy tự xóa…». Cùng gốc: `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED` của `app/views/write.py` (lỗi lạ, lần gửi bị ngắt) chỉ dặn «kiểm tra… Media → Thư viện».
- **Thử:** lệnh tạo nháp trả 400, 500 hay hết giờ sau khi đã tải 2 ảnh: không lệnh gắn nào, ảnh không có bài cha (website giả nhớ bài cha); câu báo không có «danh sách Media».
- **Hậu quả:** đúng chỗ LC-T093-2 lo (ảnh còn GPS liệt kê công khai qua `GET /wp-json/wp/v2/media`) vẫn còn ở các lần gửi hỏng, mà người dùng không được nói. Câu nhắc mới trên nút «Gửi nháp» (T-110) hứa «gắn không được thì phần mềm báo sau khi gửi». Có từ trước T-110; Thợ Máy đã nêu ngoài phạm vi («Rủi ro» 2). **Đề xuất mức Thấp**, như LC-T093-2 gốc: chỉ xảy ra khi gửi hỏng, người dùng đã được nói ảnh công khai qua đường dẫn và được dặn tự xóa.
- **Test:** `test_sl_t110_1_gui_hong_truoc_khi_co_nhap_bao_anh_con_trong_danh_sach_media` (3 xfail: 400, 500, hết giờ).
- **Gợi ý (phiếu sau, như Thợ Máy đề xuất):** `_DRAFT_IMAGES_LEFT` nói thêm ảnh chưa gắn vào bài nào nên **hiện trong danh sách Media công khai** của website; sửa cùng ý cho `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED`.

## Ghi nhận (không tính lỗi)

- **G1 · Gắn ảnh tin mã `201` như ghi alt (LC-T071-1).** Ảnh vào `_uploaded_media_ids` khi website trả `201 Created`. Plugin nào trả `201` kèm mã **ảnh có sẵn** (đang thuộc bài đã đăng) thì lệnh gắn chuyển ảnh đó sang bài nháp (bài cũ mất ảnh trong gallery «ảnh đính kèm»), cùng lúc alt, tiêu đề, chú thích của ảnh đó bị ghi đè như từ trước. Rủi ro LC-T071-1 đã chấp nhận, nay thêm một trường bị ghi. Lớp phòng rẻ: xin thêm `post` trong `_fields` của lệnh tải ảnh, chỉ gắn khi `post` trả về rỗng.
- **G2 · Khoảng trước lúc gắn.** Từ lúc tải ảnh tới lúc gắn (tải hết ảnh, ghi alt, tạo nháp) ảnh vẫn nằm trong danh sách công khai; câu nhắc nói «không hiện… cho tới khi bài được đăng» không nhắc khoảng này. Không sửa được nếu không đổi thứ tự (tạo nháp trước, tải ảnh kèm `?post=`); ghi để Lá Chắn cân nhắc.
- **G3 · Chưa thử trên website thật** (Thợ Máy đã nêu): kiểm ở lượt thử thật bằng cửa sổ ẩn danh `https://<site>/wp-json/wp/v2/media`.

## Lệnh đã chạy

- `uv run pytest tests/test_soi_loi_t110.py`: 62 passed, 3 xfailed; `--runxfail` 3 ca SL-T110-1: hỏng đúng ở dòng kiểm «danh sách Media».
- Cùng file trên code trước T-110 (`fd28bbc`): các ca gắn ảnh, lớp chặn hỏng (tức test nhắm đúng thay đổi).
- Bản gộp với `main` `17b2a31` (gỡ xung đột giữ cả hai hàm), 37 file: 5.308 passed, 3 xfailed, 0 failed.
- Đột biến: 13/15 bị bắt, 2 tương đương.
- `uv run ruff check .`: sạch. `detect-secrets` (`PYTHONUTF8=1`) trên file test, báo cáo: sạch.
- Script: thư mục ghi chú chung `T-110-soi-loi-scripts/mutate110.py`.

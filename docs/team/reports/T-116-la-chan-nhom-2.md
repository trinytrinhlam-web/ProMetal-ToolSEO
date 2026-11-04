# Biên bản bảo mật T-116 · nhóm 2: client WordPress, đăng bài (kiểm lại bằng Fable)

> Kiểm lại độc lập các biên bản Lá Chắn chạy tạm bằng Opus 5.5 từ 15/10 cho vùng WordPress và đăng bài: T-054, T-060, T-061, T-071, T-085, T-086, T-088, T-089, T-091, T-096, T-099, T-102, T-106, T-108, T-110, T-115 và các mã LC-T094-* (thiết kế Giai đoạn 5). Làm cùng lượt với kiểm đầy đủ T-112 ([`T-112-la-chan.md`](T-112-la-chan.md)), vì nhánh `team/T-112` đã chứa toàn bộ vùng này. Quy trình và mức độ lỗi: `docs/team/security.md`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **chạy Fable 5.1** (dòng «You are powered by» của lời nhắc hệ thống, kiểm theo luật 08:05) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-116](../tickets/T-116-la-chan-fable-kiem-lai.md) nhóm 2 (phiếu chưa commit; Chỉ Huy giữ) |
| Phạm vi | `team/T-112` `b4f7900` (= `origin/main` `7485b94` + `team/T-115` `a7572f7` + T-112): `seo_app/wordpress/client.py` (2.782 dòng, đọc trọn), `seo_app/wordpress/shortcodes.py`, `seo_app/publish/` (`render.py`, `markdown.py`, `review.py`, `schedule.py`), `seo_app/sanitize.py` (`sanitize_html`, `escape_shortcodes`, `strip_tags`, `is_safe_url`), `seo_app/images/html.py` (`figure_html`), `app/views/write.py` bước Xuất bản (`:2731-4191`), `app/views/wordpress.py`, `app/views/settings.py` (`release_tab`), `seo_app/storage/drafts.py` (`SendState`, `save_send_state`); mã WordPress 6.9.4 của website ở `D:\Suachuacuasat` (chỉ đọc) để dẫn chứng khi cần |
| Ngày | 2026-11-03 (08:05–09:10, nghỉ vì hết hạn mức, 12:33–12:36; giờ máy +07) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Không gọi website thật, không cloud; máy đang chạy toàn bộ test trên `main` nên chỉ test chọn lọc |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**). Điều kiện là của T-112 (sửa SL-T112-1, README, thử thật LC-T094-44, sổ rủi ro) — xem biên bản T-112. Đối chiếu 28 mã LC (1 Cao, 2 Trung bình, 25 Thấp), 27 mã SL và 44 điều kiện LC-T094 của Opus: **giữ** cả, **0 đổi mức, 0 sai**; còn mở chỉ SL-T106-1, SL-T108-1 (README, Thấp), LC-T094-44 (thử thật) và phần Chặn của LC-T094-39 (SL-T112-1) |

## Tóm tắt (cho chủ dự án)

Phần nối với WordPress và gửi bài **an toàn** như các biên bản Opus đã kết luận. Tôi đọc trọn lại mã phần kết nối (hơn 2.700 dòng), bộ lọc HTML, bộ dựng bài và bước Xuất bản, rồi tự thử lại từ đầu bằng một WordPress giả trên máy (không đụng website thật), nhắm vào 5 chuyện đáng lo nhất:

1. **Đăng bài ngoài ý bạn:** không đường nào. Chỉ đúng một lệnh (hẹn giờ/đăng) gửi được trạng thái khác «nháp», chỉ cho bài phần mềm vừa tạo trong chính lần bấm đó, sau khi bạn tick xác nhận đúng bản đã xem, và chỉ khi công tắc ở Cài đặt đang bật (mặc định tắt). Mọi cách giả dấu, gửi lệch khuôn, dùng mã bài cũ đều bị chặn **trước khi** có lệnh nào ra mạng.
2. **Mã độc, shortcode chạy trên website:** 38 mẩu HTML xấu (script, sự kiện chuột, `javascript:`, iframe, form, SVG…) đều bị lọc sạch; mọi dấu «[» «]» ở chữ, tiêu đề, alt, chú thích đều thành mã ký tự nên WordPress không chạy shortcode; chữ SEO có dạng shortcode/thẻ/mã ký tự bị từ chối.
3. **Sửa nhầm bài, ảnh có sẵn trên website:** phần mềm chỉ ghi vào bài và ảnh nó vừa tạo, hỏi lại website «còn là nháp không» ngay trước mỗi lệnh ghi; ảnh website trả lại mà không chắc là ảnh mới thì không ghi gì.
4. **Lộ địa chỉ, mật khẩu ứng dụng:** câu lỗi là câu cố định (không chép lời máy chủ, không chép địa chỉ chuyển hướng, không in mật khẩu); phần mềm không đi theo chuyển hướng nên mật khẩu không bao giờ gửi sang máy khác.
5. **Gửi trùng:** khóa «đang gửi» ghi trong file nháp kiểu «so rồi đặt», hai tab không cùng qua được; lệnh đăng không rõ kết quả thì khóa tới khi bạn xác nhận đã kiểm trang quản trị.

Không tìm thấy lỗi mới. Việc cần làm trước khi **bật** Hẹn giờ / Đăng ngay nằm ở biên bản T-112.

## Lỗi phát hiện (mới)

Không phát hiện lỗi mới của Lá Chắn trong vùng nhóm 2. Lỗi còn mở duy nhất (SL-T112-1, Trung bình, của Soi Lỗi) đánh giá ở biên bản T-112.

## Kiểm theo 5 rủi ro Chỉ Huy nêu

| Rủi ro | Lớp chặn (mã tại `b4f7900`) | Tôi thử (probe `probe_nhom2.py`, WordPress giả) |
|---|---|---|
| **Đăng ngoài ý người dùng** | `client.py`: `_RELEASE` (`:184`, dấu riêng, so bằng `is`), `_is_release_request` (`:341`: `POST /wp/v2/posts/<mã>`, chỉ `json`+`params`, `_fields` cố định, thân **đúng** `{status: future, date_gmt}` hay `{status: publish}`); mọi lệnh khác có `status` phải là `"draft"`, không `date`, `date_gmt` (`_is_plain_request:283-291`); `release_draft` (`:1475`) giành mã một bước, kiểm hình thức/giờ, hỏi lại còn nháp + `modified_gmt` + giờ máy chủ, rồi **một** lệnh; mã bài không trả lại sau lệnh. App: `release_post` (`write.py:3692`) là chỗ duy nhất gọi; công tắc `is True` (`:2855`, `:4073`, `:3364`); mã băm xác nhận (`render.py:378-512`, `write.py:3107`, `:3467`); `render._review` Chặn Đăng ngay khi SEO không ghi | A1–A10: 20 ca đều đúng (thân `status`/`future`/`Draft` không dấu, 4 dấu giả, 7 khuôn sai, bài lạ, gọi lại: **0 request**; hẹn giờ đúng khuôn; quá gần/đã qua/không `Date`: chặn trước lệnh; website đăng ngay thay vì hẹn: câu KHẨN, 1 lệnh; `modified_gmt` khác: chặn) |
| **Shortcode / HTML chạy được** | `sanitize_html` (`sanitize.py:792`): allowlist thẻ (`:634`), thuộc tính theo thẻ (`:651`), `is_safe_url` (`:665`: chỉ http/https/mailto/tel/tương đối, chặn `//`, `/\`, `\`, bỏ ký tự điều khiển/rộng 0 trước khi xét), `srcset` kiểm từng ứng viên, thẻ nguy hiểm bỏ cả ruột, bình luận/khai báo bỏ, `escape_shortcodes` ở cả chữ lẫn thuộc tính; `markdown_to_html` không sinh `<a>/<img>/HTML thô`, `escape_text` (`markdown.py:65`); bộ dựng chạy lọc **hai lần** quanh `place_links` rồi `check_links`; tiêu đề `strip_tags` + `escape_shortcodes`; alt/tiêu đề/chú thích Media `escape_shortcodes` (`client.py:1789`, `:2116-2121`); chữ SEO `_seo_text` (`:2401`); `review._shortcodes` liệt kê đoạn dạng shortcode cho người dùng xóa (sổ rủi ro 30/10: trình soạn có thể đưa «[» trở lại khi tự sửa trên website) | B1–B8: 38 payload sạch; idempotent; `is_safe_url` 13 xấu/8 tốt; Markdown không link/ảnh, `&#91;` giải mã rồi escape lại; `strip_tags` lồng; `_seo_text` 11/11 xấu chặn, 5 tốt qua; `figure_html` escape alt/chú thích, 4 `src` xấu từ chối; thân `create_draft`/`upload_media` không «[» trần, không script |
| **Ghi vào bài/ảnh không phải của app** | `_created_post_ids` (`:1051`, chỉ thêm khi website xác nhận nháp `:1288`), `_uploaded_media_ids` (`:1054`, chỉ khi 201 + chưa có bài cha `:1844-1855`), `_own_draft` (`:1336`) trước ảnh đại diện/SEO, `_owns_attach` (`:2181`) + `_is_media_attach` (`:330`) cho lệnh gắn ảnh, `_is_own_draft_answer` (`:2673`) ở mọi câu trả lời lệnh ghi, `_FORBIDDEN_JSON_KEYS` `id`/`name` (`:170`: thân JSON không đổi được bài/ability trên đường); `upload_media` đòi 201 + `post` null/0; `set_seo_meta` chỉ 3 trường, không `null` | C1–C4: ảnh đại diện/SEO cho bài lạ, gắn ảnh lạ, gắn ảnh vào bài lạ: **0 request**; bài không còn nháp: không POST, mã bị bỏ; thân gắn ảnh kèm khóa khác: chặn; upload trả 200 / ảnh có bài cha / thiếu `post`: không ghi alt |
| **Lộ `WORDPRESS_URL`, mật khẩu ứng dụng** | `__init__` (`:1021-1047`): đòi https, `_is_plain_site_url` (`:2504`: không `@ ? # %`, không `.` trong thư mục, không `wp-json`/`wp-admin`/`code-snippets`/`prometal`), câu lỗi không chép địa chỉ; `__repr__` chỉ `base_url`; `_request` (`:2198`): `allow_redirects=False`, `_REQUEST_OPTIONS` không cho `verify`/`auth`/`cookies`; `_error_from` (`:2268`) câu cố định theo mã HTTP, `code` chỉ giữ ASCII; lỗi mạng chỉ tên lớp (`:2230`); `_json` (`:2249`) câu cố định; không `logging`/`print` trong client; giao diện `app/views/wordpress.py` chỉ hiện `base_url` (địa chỉ công khai, đã chặn dạng có mật khẩu) qua `escape_markdown` | D1–D6: 500 mang chữ bí mật + địa chỉ, 302 → `evil`, HTML thay JSON, 403: 4 câu cố định không chữ máy chủ/Location/mật khẩu; 302 không đi theo (1 request); `repr` sạch; header `Authorization` chỉ tới `example.com`; lỗi mạng mang mật khẩu → chỉ tên lớp; JSON lồng 50.000 tầng → câu cố định. E2: 12/12 địa chỉ cấu hình xấu từ chối, câu lỗi không chép địa chỉ |
| **Gửi trùng** | `save_send_state` (`drafts.py:995`): so rồi đặt trong `BEGIN IMMEDIATE`; `send_and_record` (`write.py:3543`) ghi «đang gửi» trước, không `st.*` giữa chừng, `record_outcome` chỉ ghi khi có `claimed`; `apply_send`/`finish_send` thứ tự đơn điệu; `release_unknown` khóa; nút xét lại điều kiện lúc bấm (`:4170`); «gửi lại» phải tick ô nói rõ việc sẽ làm | Đọc mã; test T-086/T-089/T-102/T-112 chạy chọn lọc (mục công cụ). Không lặp lại thử hai tab (Soi Lỗi T-112 đã thử) |

## Đối chiếu từng phát hiện của biên bản Opus cũ

Kết luận Fable: **giữ** (đúng mức, trạng thái đúng), **đổi mức**, hoặc **sai**. Bằng chứng theo mã tại `b4f7900`.

Nguồn: 15 biên bản Lá Chắn Opus trong vùng (T-108 kiểm chung trong T-106; T-115 Lá Chắn nằm ở `team/T-115`, đối chiếu ở biên bản T-112). Mỗi biên bản đều ghi «chạy tạm Opus 5.5, kiểm lại bằng Fable sau 01/11». Tổng: **28 mã LC** (1 Cao, 2 Trung bình, 25 Thấp), **27 mã SL** Lá Chắn có nhắc (24 có mức), **44 điều kiện LC-T094**, 29 dòng điều kiện đánh số còn «mở» theo chữ biên bản.

### a. 28 mã LC-* (lỗi Lá Chắn Opus tự tìm)

| Biên bản | Mã | Mức Opus | Kết luận Fable | Bằng chứng tại `b4f7900` |
|---|---|---|---|---|
| T-054 | LC-T054-1 (= SL-T054-2) | Trung bình | giữ (đóng T-061) | Alt/tiêu đề/chú thích Media qua `escape_shortcodes` sau `plain_image_text` (`client.py:2116-2121`); `_MEDIA_FIELDS` không `description`; probe B8. Mức đúng: shortcode chỉ chạy snippet **có sẵn** (`[code_snippet id=N]`), không tạo mã mới |
| T-054 | LC-T054-2 (= SL-T054-3) | Thấp | giữ (đóng T-071) | `DraftImagesError.maybe_draft` + `_DRAFT_MAYBE_CREATED` khi lỗi không phải 4xx ở lệnh tạo nháp (`:1956-1971`) |
| T-054 | LC-T054-3 (= SL-T054-1) | Thấp | giữ (đóng T-071) | `plain_image_text` gỡ `]\:` ở mọi chỗ (`html.py:66`, `:93`) |
| T-054 | LC-T054-4 | Thấp | giữ (đóng T-071) | `DraftImage.tags: ImageTags`, client `replace()` dựng lại để kiểm danh sách cố định (`:2072-2077`); tên file chỉ từ `image_file_name` |
| T-054 | LC-T054-5 | Thấp | giữ (đóng T-071) | `_MEDIA_SAME_ID` (`:1924-1927`), `new_only=True` đòi 201 (`:1836`); probe C4 |
| T-054 | LC-T054-6 | Thấp | giữ (đóng T-071) | Chốt `figure_html` chỉ tìm trong thẻ `<img>` (`html.py:69`, `:145-153`) |
| T-060 | LC-T060-1 | Thấp | giữ (đóng T-085) | `ALLOWED_JSON_KEYS`, `_FORBIDDEN_JSON_KEYS` (`:149-173`); probe E4 (`id` trong thân → chặn) |
| T-060 | LC-T060-2 | Thấp | giữ (đóng T-085, T-088) | `_asks_rendered_fields` cắt như `trim()` PHP kể cả NUL (`:385-399`); probe E4 (`content`, `""`, `\x00content` → chặn) |
| T-060 | LC-T060-3 | Thấp | giữ (đóng T-085) | `_MEDIA_NOT_DESCRIBED` (`:543-548`, `:1793-1803`) |
| T-061 | LC-T061-1 | **Cao** | giữ (đóng T-075) | `certifi 2026.10.19` đang cài (kiểm `import certifi`); pip-audit 02/11 sạch. Mức Cao đúng với lúc đó (gốc emSign lộ khóa) |
| T-061 | LC-T061-2 (= SL-T061-1) | Thấp | giữ (đóng T-060) | `_TAG_LIKE_OPEN` (`:438`, `:2437-2443`); probe B6 (`<1> cổng` chặn, `x < y` qua đúng ý) |
| T-061 | LC-T061-3 (= SL-T061-2) | Thấp | giữ (đóng T-060, T-108) | Trang Kết nối không còn tải ảnh (`wordpress.py` docstring, mục 3 chỉ chữ); `upload_media` ghi đè 3 ô (`:1760`, `:1785-1791`); probe B8 |
| T-061 | LC-T061-4 | Thấp | giữ (sổ rủi ro 30/10) | `security.md` §6 dòng 30/10; `review._shortcodes` + `shortcode_findings` liệt kê trước khi gửi; Code Snippets 4.0.0 tắt chạy theo file |
| T-061 | LC-T061-5 | Thấp | giữ (đóng T-060) | Chỉ test (`test_soi_loi_t042.py`); không đọc lại |
| T-071 | LC-T071-1 | Thấp | giữ (đóng T-060) | `_post_media(new_only=True)` đòi 201 + `post` null/0 (`:1836-1855`); probe C4 (200, có cha, thiếu `post`) |
| T-085 | LC-T085-1 | Thấp | giữ (đóng T-088) | `_error_from` bắt `Exception` khi đọc thân lỗi (`:2273-2276`); `_json` cũng vậy (`:2258-2265`); probe D6 |
| T-086 | LC-T086-1 | Thấp | giữ (đóng T-089) | `record_outcome` bắt `ValueError` → `MSG_POST_ID_OUT_OF_RANGE` (`write.py:3826-3827`) |
| T-089 | LC-T089-1 | Thấp | giữ (đóng T-089 lượt 4) | `holder["replaced"]` (`write.py:3599`) trả lại đúng trạng thái khi không tạo được bài (`:3805-3806`) |
| T-091 | LC-T091-1 | Thấp | giữ (đóng: T-091 gộp `470a11a`, T-093 ghi Đóng) | R5 đã duyệt; test chạy qua (lô 2) |
| T-096 | LC-T096-1 | Trung bình | giữ (đóng T-096 lượt 3) | `_strip_closing_hashes` không regex, tuyến tính (`markdown.py:267-278`) |
| T-096 | LC-T096-2 | Thấp | giữ (đóng lượt 3) | Thẻ ảnh trong mã băm (`render.py:482-488`), `_same_image` so `tags` (`:270`) |
| T-096 | LC-T096-3 | Thấp | giữ (đóng lượt 3) | `_DROPPED` gồm U+202A–E, U+2066–9 (`markdown.py:57-59`) |
| T-096 | LC-T096-4 | Thấp | giữ (đóng lượt 3) | `_JS_TRIM` (`review.py:74-80`) |
| T-096 | LC-T096-5 | Thấp | giữ (đóng lượt 4) | `_block_editor_embeds` (`review.py:319-350`); BLOCK ở `render.py:568-577` |
| T-096 | LC-T096-6 | Thấp | giữ (đóng lượt 5) | Tách tên máy kiểu WHATWG (`review.py:341-345`) |
| T-099 | LC-T099-1 | Thấp | giữ (đóng lượt 2) | `_created_post_ids.remove` một bước (`:1512-1517`); probe A5, A7 |
| T-102 | LC-T102-1 | Thấp | giữ, **đóng ở T-112 + T-115** | `featured_missing` → Đăng ngay giữ nháp (`write.py:3633`, `:3708`); client còn chặn thêm (`_taint_modified` khi lệnh ảnh đại diện lỗi, `:1462-1464`); dấu `xfail` đã gỡ, test qua |
| T-110 | LC-T110-1 | Thấp | giữ (đóng lượt 2–3) | `_post_media` kiểm `post` null/0 trước khi nhận là ảnh mới (`:1844-1853`); `_attach_media` chỉ `_uploaded_media_ids` (`:2031`); probe C1, C4 |

### b. 27 mã SL-* Lá Chắn Opus có nhắc (mức do Lá Chắn xếp)

| Mã | Mức Lá Chắn Opus | Kết luận Fable | Bằng chứng |
|---|---|---|---|
| SL-T054-1, -2, -3 | Thấp / TB / Thấp | giữ (= LC-T054-3, -1, -2) | như bảng a |
| SL-T060-1 | Thấp | giữ (đóng T-085) | `upload_media` đòi câu trả lời ghi đè nói đúng `media_id` (`:1802-1803`) |
| SL-T061-1, -2 | Thấp | giữ (= LC-T061-2, -3) | như bảng a |
| SL-T071-1 | Thấp | giữ (đóng T-081, CLAUDE.md 23/10) | `_LABEL_COLON_ESCAPE` (`html.py:66`) |
| SL-T085-1, -2, -3 | Thấp | giữ (đóng T-088) | NUL trong `_fields` (`:396-398`); `_json` bắt mọi lỗi; `_MEDIA_MAYBE_UPLOADED` (`:1772-1776`) |
| SL-T086-1, -2 | Thấp | giữ (đóng T-089) | So rồi đặt `BEGIN IMMEDIATE` (`drafts.py:1013-1024`); băm `altsha-` so lại trước khi tải (`write.py:3408-3412`) |
| SL-T088-1 | Thấp | giữ (đóng T-091) | `_without_lone_surrogates` luôn chạy trong `_json` (`:2259`) |
| SL-T089-1, -2 | Thấp / — | giữ (đóng lượt 2+3) | `record_outcome` chỉ ghi khi có `claimed`, dự phòng `expected=(None, False)` (`write.py:3819-3821`) |
| SL-T091-1, -2, -3 | Thấp | giữ (đóng: T-093 Lá Chắn ghi «LC-T091-1, SL-T091-1 → -3 Đóng») | `_json` lọc trên dữ liệu đã giải mã; `PublishedItem` dùng `_positive_id` có `MAX_ID` (`:857`); `test_soi_loi_t091.py` không còn `xfail` |
| SL-T096-8, -9 | Thấp | giữ (đóng lượt 3) | `ImageRow.featured_auto` (`render.py:608`), `featured_section` theo đúng luật client |
| SL-T099-1 | Thấp | giữ (đóng lượt 2) | `_is_image_upload` (`:300-322`); probe E4 (`data` ở `/posts/7` → chặn) |
| SL-T102-1 | Trung bình | giữ; **đóng ở T-112** (3 `xfail` gỡ, test qua) — phần còn sót thành **SL-T112-1** (TB, biên bản T-112) | `release_missing`, `MSG_PUBLISH_HELD` |
| SL-T106-1, SL-T108-1 | Thấp | giữ, **còn mở** (3 `xfail` XFAIL ở lô 2) | `wordpress.py` câu «Biên tập viên (Editor) hoặc Quản trị viên (Administrator)» vẫn còn; README dòng Trạng thái → phiếu dọn README cùng SL-T112-2, -3 |
| SL-T110-1, -2, -3 | Thấp / — / — | giữ (đóng lượt 2–3) | `_DRAFT_IMAGES_LEFT`, `_DRAFT_IMAGE_RETURNED`, `_IMAGES_NOT_ATTACHED` (`:549-587`) |

### c. 44 điều kiện LC-T094-* (thiết kế Giai đoạn 5)

| Mã | Phiếu | Kết luận Fable | Bằng chứng |
|---|---|---|---|
| LC-T094-1, -2, -3 | chung | giữ, đạt | Test qua `fake_wordpress` + bộ chặn mạng; câu báo hằng (probe D1); `shown_text`/`cell_text` bỏ ký tự hướng chữ, vô hình (`write.py:2858-2872`); hai chỗ `unsafe_allow_html` đều `html.escape` |
| LC-T094-4 → -10 | T-096 | giữ, đạt | probe B4 (bộ chuyển không link/ảnh/HTML thô); `render.py:417-421` đúng thứ tự, mã băm trên chính `sections`; `embedded_urls` + BLOCK mọi hình thức; `link_rows` 8 cờ, `bare_addresses`, `_shortcodes`, GPS; `_section_html:287` unbreak trước escape; `_heading_tag` → `<h3>`+ |
| LC-T094-22 | T-099 | giữ, đạt | probe A2–A4, E4; AST test `test_wordpress_release.py` |
| LC-T094-23 | T-099 | giữ, **đóng đủ** (phần «nên» xong ở T-115) | probe A5, A7, A10; `_modified` (`:1060`, `:2139-2157`), `release_draft:1545-1550` |
| LC-T094-24, -25, -26, -27 | T-099 | giữ, đạt | probe A8, A9; `schedule.release_time_problem`; `_released_from`; `post_statuses` + `_PARAM_VALUES`; `timezone_warning` (`timezone_string` chỉ đọc, chưa hiện: GN 4 cũ, vô hại) |
| LC-T094-36, -37, -40 | T-102 | giữ, đạt | `build_package` cho mọi hình thức, dựng lại `fresh=True`; `review_panel` đủ/rút gọn; `record_plan` qua T-100, lỗi Sheet không gửi lại WordPress, G1 thêm ở T-112 |
| LC-T094-38 | T-102 | giữ, đạt; LC-T102-1 **đóng** (T-112, T-115) | `confirm_box`, `send_draft:3467` `compare_digest`; `release_post` sau ảnh đại diện/SEO trên cùng client |
| LC-T094-39 | T-102 | giữ; phần Chặn: SL-T102-1 đóng, **còn SL-T112-1** (trường SEO bị Chặn bị bỏ) trước khi bật | `release_missing`, `render.py:628` |
| LC-T094-41 | T-102 | giữ, **đóng ở T-112** (phương án A, Lá Chắn duyệt ở biên bản T-112) | `release_tab`, `release_enabled() is True`, G2 |
| LC-T094-44 | thử thật | giữ, **còn mở** | Danh sách kiểm ở biên bản T-112 (B4) |
| LC-T094-11 → -21, -28 → -35, -42, -43 | T-097, T-098, T-100, T-101, T-103, README | giữ (đã đối chiếu ở [biên bản nhóm 4](T-116-la-chan-nhom-4.md)) | — |

### d. 29 dòng điều kiện đánh số còn «mở» theo chữ biên bản Opus — trạng thái thật hôm nay

| Nhóm | Trạng thái thật (tôi kiểm trên `main`/nhánh, CLAUDE.md, T-093) |
|---|---|
| T-054 ĐK 1, 3, 6; T-061 ĐK 1, 2; T-071 ĐK 1, 3, 4; T-086 ĐK 4, 5; T-091 ĐK 0, 1, 2; T-102 câu 2 điều 1, 2, 5–8; T-110 gộp T-115; «kiểm lại bằng Fable» | **Đã xong** ở phiếu sau (T-056, T-059 thử thật 27–28/10, T-067, T-075, T-081, T-089, T-091/T-093, T-112, T-115; biên bản này) |
| T-099 ĐK 3 = T-102 câu 2 điều 3 (thử thật LC-T094-44); T-091 ĐK 4 (tiêu đề «< 5 triệu», `srcset`); T-110 ĐK 3 (Media ẩn danh, `"post": null` thật) | **Còn mở**, gom vào buổi thử thật trước khi bật công tắc (biên bản T-112, B4) |
| T-102 câu 2 điều 4 (Lá Chắn rà Giai đoạn 5) | **Xong về phần bảo mật**: biên bản này + nhóm 4 (Google, kế hoạch) + T-112 |
| T-106 ĐK 2, 3 (SL-T106-1, SL-T108-1) | **Còn mở** (README/câu trang Kết nối, Thấp) → phiếu dọn README |
| T-096 ĐK 7 phần «giới hạn cỡ thân bài khi dựng» (T-102 GN 1) | **Còn mở, Thấp, không bắt buộc**: bài rất dài chỉ làm chậm máy mình; nên thêm trần khi sửa SL-T112-1 |
| T-060 ĐK 4 (sửa chữ phiếu T-060 về `index.php`); T-089 việc theo sau 3 (dọn tùy chọn) | Hành chính, không ảnh hưởng an toàn |

**Tóm lại:** 28 mã LC và 27 mã SL: **giữ** cả, **0 đổi mức, 0 sai**; mọi mã đều đã đóng trừ SL-T106-1, SL-T108-1 (README, Thấp) và LC-T061-4 (sổ rủi ro có chủ đích). 44 điều kiện LC-T094: 23 thuộc vùng này đạt/đóng, còn mở đúng hai chỗ đã biết (LC-T094-44 thử thật; LC-T094-39 phần Chặn chờ SL-T112-1); 21 thuộc nhóm 4 đã đối chiếu trước.

## Thử độc lập (`probe_nhom2.py`, không mạng)

Chạy bằng `uv run python -X utf8` từ worktree (`seo_app` nạp từ `wt-T-112`); WordPress giả là `tests/fake_wordpress.py` (adapter của `requests`, không socket).

| Nhóm | Ca | Kết quả |
|---|---|---|
| A · đăng ngoài ý | 20 | PASS hết (bảng trên) |
| B · HTML, shortcode | 38 payload + 7 ca | PASS; 1 «FAIL» của probe: `x < y` hợp lệ theo LC-T061-2 (chỉ chặn «<» liền ký tự khác); 1 «FAIL» của probe: `[` trong `src` ảnh được escape thành `&#91;` (vô hại, tôi đặt kỳ vọng sai) |
| C · bài/ảnh lạ | 8 | PASS hết |
| D · lộ thông tin | 6 | PASS hết |
| E · kiểm dạng | 5 | PASS; 1 «FAIL» của probe: địa chỉ có tab cuối bị `strip()` rồi nhận (`https://site.vn`), vô hại |

Tổng: **41 PASS / 0 FAIL thật** (3 «FAIL» đều là probe đặt kỳ vọng sai, đã xác minh lại từng ca).

## Đọc mã: điểm đáng chú ý ngoài probe

- `release_draft` bắt 4xx là «vẫn nháp» (lời từ chối rõ), mọi lỗi khác là `unsure` (khóa gửi lại); `_released_from` đòi đúng mã bài, đúng trạng thái, hẹn giờ thì đúng chuỗi `date_gmt` đã gửi; `future` mà website trả `publish` → `went_public` (câu KHẨN, hướng dẫn chuyển về nháp). `release_time_problem` dùng header `Date` của **chính** lệnh kiểm nháp, thiếu thì chặn; lệch đồng hồ > 2 phút chặn; hẹn ≥ 10 phút (WordPress đăng ngay khi < 60 giây) và ≤ 365 ngày.
- Mã băm xác nhận gồm cả ba ô SEO và công tắc «Ghi SEO», chuyên mục, giờ hẹn; so bằng `hmac.compare_digest`; dựng lại với danh sách bài tải lại trước lệnh đầu. Đổi hình thức, giờ, công tắc SEO sau khi tick → bỏ tick.
- `post_statuses` (`:1659`) chỉ đọc, `include`/`status`/`context` kiểm giá trị, không nạp mã nào vào `_created_post_ids`.
- `list_published` lọc lại phía app (`status == publish`, link `https` đúng tên máy, độ dài, ký tự điều khiển/vô hình), chặn vòng lặp (`MAX_PAGES`, trang lặp).
- `_without_lone_surrogates` đi bằng ngăn xếp; `_positive_id` từ chối `True`, chữ, số thực, 0, > 2⁶³−1.
- Client mới cho mỗi lần bấm gửi (`wordpress_client()`), không `st.cache_resource`; `check_connection` dò Abilities chỉ `GET`.

## Ghi nhận (không lập lỗi)

1. `sanitize_html` cho thuộc tính `id`, `class` (mọi thẻ) và `rel` (`<a>`), giá trị tự do. Không đường nào đưa thuộc tính từ AI hay người dùng vào bài: `clean_ai_text` bỏ mọi thẻ lúc nhận chữ AI, `markdown_to_html` không sinh thuộc tính (trừ `start` của `<ol>` là số), `figure_html` và `place_links` do code dựng; trang Kết nối gửi chữ thuần qua `paragraphs_to_html` (`html.escape`). Nếu phiếu sau cho dán HTML thô thì nên thu hẹp.
2. Không giới hạn cỡ thân câu trả lời của website (`response.json()` đọc hết): website là của chính chủ dự án, chỉ làm chậm máy mình; không lập lỗi.
3. `set_featured_image(post_id, media_id)` chỉ kiểm bài là của client, không kiểm `media_id` là ảnh client vừa tải (nơi gọi duy nhất `create_draft_with_images` truyền đúng ảnh vừa tải). Dùng ảnh có sẵn làm ảnh đại diện cho **nháp của chính app** không sửa ảnh đó; vô hại.
4. Nếu ability của SiteSEO đổi `post_modified` thì Đăng ngay/Hẹn giờ kèm «Ghi SEO» luôn bị `_RELEASE_CHANGED` (chức năng, không an toàn): mục kiểm (b) của buổi thử thật (T-112 điều kiện B4).
5. `_seo_text` cho «<» liền dấu cách (`x < y`): đúng LC-T061-2 (`strip_tags` của PHP chỉ mở thẻ khi «<» liền ký tự khác).
6. `WORDPRESS_URL` có khoảng trắng hai đầu được `strip()` trước khi kiểm: tiện cho người gõ `.env`, không mở đường nào.
7. Khe «liên kết đặt vào đúng khoảnh khắc» không thuộc vùng này; ba giới hạn `modified_gmt`: biên bản T-112 mục 2.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| W1 | Đạt | Chỉ `release_draft` → `future`/`publish`; công tắc mặc định tắt; màn hình xác nhận + mã băm; Đăng ngay thêm điều kiện ảnh đại diện/SEO (T-112), bài chưa bị sửa (T-115). Còn SL-T112-1 (sửa trước khi bật) |
| W2 | Đạt | Chỉ bài/ảnh client vừa tạo; hỏi lại còn nháp; ảnh website trả lại không chắc là mới thì không ghi; `post_statuses`, `list_published` chỉ đọc |
| W3 | Đạt | `sanitize_html` hai lần, `escape_shortcodes` mọi chữ gửi, `is_safe_url`, `_seo_text`; oEmbed Chặn ở màn hình xác nhận |
| W4 | Đạt | Khóa gửi trùng so rồi đặt; khóa khi không rõ; «gửi lại» phải tick ô nói rõ |
| U1 | Đạt | Chữ website/AI qua `escape_markdown`/`st.text`/bảng; hai chỗ `unsafe_allow_html` của trang Bài viết, bước SEO đều `html.escape` |
| U2 | Đạt | Câu lỗi cố định; không chép lời máy chủ, Location, `WORDPRESS_URL` dạng có mật khẩu, đường dẫn |
| F3 | Đạt | Không `eval`/`pickle`; không chạy nội dung file |
| D1 | Đạt | pip-audit 69 gói sạch (02/11, lock không đổi); không thư viện mới |
| D2 | Đạt | `.gitignore` giữ `.env`, file khóa, `data/` |
| D3 | Đạt | Test WordPress đều qua `fake_wordpress`; bộ chặn mạng `conftest`; probe không mạng |
| S1–S3, A1–A3, U3, F1, F2 | Không áp dụng (nhóm 1, 3, 4) | — |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Dùng lại sáng 02/11 (lock không đổi): 69 gói, 0 lỗ hổng | ✔ |
| bandit (`PYTHONUTF8=1`) | `seo_app/wordpress`, `seo_app/publish`, `seo_app/sanitize.py`, 3 view: 0 | ✔ |
| detect-secrets (`PYTHONUTF8=1`) | 2 báo nhầm (`client.py:1023`, `write.py:2493`: chú thích/docstring ví dụ `tên:mật-khẩu@`) | ✔ |
| Soát lịch sử git `7485b94..b4f7900` | 0 mẫu mật khẩu ứng dụng/khóa | ✔ |
| ruff | sạch | ✔ |
| pytest chọn lọc lô 1 (11 file) | **785 qua / 4 xfail (= SL-T112-1 ×2, SL-T112-2, SL-T112-3) / 0 hỏng / 0 XPASS**, 16 phút 18 | ✔ |
| pytest chọn lọc lô 2 (48 file vùng nhóm 2) | **6.058 qua / 3 xfail (= SL-T106-1 ×2, SL-T108-1: README, Thấp, đã biết) / 0 hỏng / 0 XPASS**, 25 phút 58 | ✔ |

## Báo nhầm đã loại

- detect-secrets ×2 (chú thích/docstring ví dụ).
- Probe 3 ca (bảng «Thử độc lập»).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. Các điều kiện B1–B6 của biên bản T-112 (sửa SL-T112-1; README SL-T112-2, -3, G1; thử thật LC-T094-44 với danh sách kiểm; sổ rủi ro ba giới hạn `modified_gmt`; nên gộp T-118 trước khi bật).
2. Điều kiện cũ còn mở trong vùng (theo biên bản Opus cuối nhắc tới, tôi xác nhận lại trên mã và test): **SL-T106-1, SL-T108-1** (README/trang Kết nối, Thấp; 3 `xfail` trong `tests/test_soi_loi_t106.py` vẫn XFAIL) → gom vào phiếu dọn README cùng SL-T112-2, -3; **T-059 điều kiện 2 và T-091 điều kiện 4** (thử thật `srcset` ảnh và tiêu đề SEO có «<» trên website) → gom vào buổi thử thật LC-T094-44 (biên bản T-112, B4 mục g). Ngoài vùng: test trên Mac thật.

## Tệp và cách chạy lại

- Probe: `C:\Users\ADMIN\AppData\Local\Temp\claude\D--ProMetal-ToolSEO\42f61352-e440-426b-832a-72b79f8aff54\scratchpad\probe_nhom2.py` (thư mục tạm của phiên; chạy từ worktree: `PYTHONUTF8=1 uv run python -X utf8 <đường dẫn>`).
- Bảng trích phát hiện Opus (dữ liệu để đối chiếu): `…\scratchpad\bang-phat-hien-opus-nhom2.md`.
- Ghi chú bàn giao: thư mục ghi chú chung của phiên, file `T-116-la-chan-nhom-1.md` (mục nhóm 2).

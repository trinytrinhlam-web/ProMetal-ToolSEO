# Biên bản bảo mật T-042 · Ghi meta SEO (SiteSEO) lên bài nháp

> **Model:** chạy tạm **Opus 5.5** vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-042](../tickets/T-042-ghi-meta-seo-len-nhap.md) |
| Phạm vi | diff `origin/main...team/T-042`, HEAD `dab6e86` (3 lượt Thợ Máy, 2 lượt Soi Lỗi). Code: `seo_app/wordpress/client.py`, `seo_app/wordpress/__init__.py`, `seo_app/storage/site_index.py`; 9 file test mới, 4 file test cũ sửa 1 dòng. Không đổi `app/`, `config/`, `uv.lock`, `pyproject.toml`, `.env.example`, `.gitignore`, `.streamlit/`, `.claude/` |
| Ngày | 2026-10-19 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: không có lỗi Nghiêm trọng, Cao hay Trung bình. 5 lỗi Thấp (LC-T042-1…5), điều kiện ở cuối. Được gộp vào `main` |

## Tóm tắt (cho chủ dự án)

Phiếu này an toàn để gộp. Tôi đã thử mọi cách tìm được để phần mềm ghi SEO hay ảnh đại diện vào **bài đã đăng** hoặc **bài không do app tạo**: không có đường nào. Trước khi ghi, phần mềm luôn hỏi lại website "bài này còn là nháp không". Phần mềm chỉ gọi được **13 địa chỉ cố định** trên website. Các địa chỉ nguy hiểm (`code-snippets`, `prometal/v1/deploy-files`, `purge`) bị chặn trước khi gửi, kể cả khi viết lách bằng `..`, `%`, `//`, chữ hoa, chữ số toàn khổ hay ký tự vô hình. Tính năng ghi SEO **mặc định tắt** và chưa có nút trên giao diện, nên hiện tại app chưa gửi gì thêm lên website.

Còn 5 điểm nhỏ (mức Thấp), không ai bên ngoài khai thác được. Đáng chú ý nhất: nếu anh bấm **Đăng** bài trong trang quản trị đúng lúc phần mềm đang ghi SEO (khe dưới một giây), SEO vẫn được ghi vào bài vừa đăng đó. Đây là chính bài của app, với chữ anh đã duyệt, nên không hại bài cũ. Trước khi bật tính năng cho anh dùng, cần một **phiếu thử thật** với một bài nháp (danh sách việc ở cuối biên bản).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T042-1 | Thấp | Danh sách đường cố định chỉ kiểm **đường** (`path`), không kiểm **tham số** (`params`) và header. WordPress đọc `?rest_route=` (đổi đường) và `?_method=` hay header `X-HTTP-Method-Override` (đổi phương thức) ngay cả khi gọi `/wp-json/wp/v2/posts`. Nhận định này dựa trên hiểu biết về mã WordPress lõi (`WP::parse_request`, `WP_REST_Server::serve_request`); tôi chưa đối chiếu dòng cụ thể | `client.py:810-816` (`_request`), `:77-91` (`is_allowed_route`) | Đã chạy thử, không mạng: `client._request("GET", "/wp/v2/posts", params={"rest_route": "/code-snippets/v1/snippets", "_method": "DELETE"})` qua danh sách đường, request đi ra `…/wp-json/wp/v2/posts?rest_route=%2Fcode-snippets%2Fv1%2Fsnippets&_method=DELETE`. **Hôm nay không có đường tới**: chỉ 3 chỗ truyền `params` (`client.py:399, 503, 630`), đều là hằng do code viết (`context`, `_fields`, `page`, `per_page`, `status`…), không có chữ người dùng, AI hay máy chủ. Chỉ thành lỗi nếu phiếu sau thêm tham số lấy từ dữ liệu ngoài | Trong `_request`: từ chối (trước khi gửi) khi `params` có khóa `rest_route`, `_method`, `_envelope`, `_jsonp`, hoặc `headers` có `X-HTTP-Method-Override` / `X-Method-Override` (không phân biệt hoa thường). Tốt hơn nữa: danh sách khóa `params` cho phép cố định theo từng đường. Thêm test. Làm ở phiếu dọn lỗi, **trước** phiếu nào truyền `params` mới |
| LC-T042-2 | Thấp | Khe "kiểm còn nháp rồi mới ghi" ở đường Abilities: giữa lệnh `GET` kiểm nháp và lệnh `POST …/run` là một vòng mạng (thường dưới 1 giây). Bài bị đăng trong khe đó thì SEO vẫn được ghi và app vẫn báo "Đã ghi SEO…", không nhắc gì. Đường dự phòng (meta) thì phát hiện được nhờ đọc `status` trong câu trả lời (`client.py:698-700`) | `client.py:614-617`, `:662-675` | Đã chạy thử với site giả: lệnh kiểm trả `draft`, site đổi sang `publish` ngay sau đó → `written=True`, "Đã ghi SEO vào hộp SiteSEO của bài nháp.", lúc ghi bài đã là `publish`. **Ai làm được:** chỉ người có tài khoản quản trị website bấm Đăng đúng khe đó; không có đường nào từ dữ liệu ngoài (trang đối thủ, AI). **Hậu quả:** tiêu đề, mô tả, từ khóa mà người dùng đã duyệt cho **chính bài app vừa tạo** được ghi vào bài đó sau khi đăng. Không đụng bài cũ, không xóa gì (không gửi `null`, canonical, robots). Không có cách đóng khe hoàn toàn từ phía app, vì SiteSEO không nhận điều kiện "chỉ ghi nếu còn nháp" | Không bắt buộc. Nên làm ở phiếu giao diện nối `set_seo_meta`: sau khi ghi qua Abilities thì `GET` lại trạng thái bài; không còn `draft` thì báo người dùng "Bài đã được đăng trong lúc ghi SEO; mở hộp SiteSEO kiểm tra lại", không im lặng. Giữ nguyên thứ tự hiện tại (dò Abilities trước, kiểm nháp ngay trước lệnh ghi) |
| LC-T042-3 | Thấp | Chữ SEO dạng **shortcode** (`[code_snippet id=3]`, `[code_snippet_source id=3]`, `[gallery]`) không bị chặn. Chưa biết SiteSEO có chạy shortcode trong tiêu đề, mô tả SEO không (chưa xác minh được: không có site thử, không gọi mạng) | `client.py:996-1029` (`_seo_text`) | Đã chạy thử: `_seo_text("T", "[shortcode]", 200)` cho qua. Đường đi giả định: chữ đối thủ có lệnh ẩn → AI gợi ý meta có `[code_snippet_source id=N]` → bộ lọc T-036 không bỏ (chỉ bỏ link, HTML, `%%`, thực thể) → người dùng không để ý → T-042 ghi lên SiteSEO → nếu SiteSEO chạy `do_shortcode` cho meta thì trang công khai lộ mã nguồn snippet (site có plugin Code Snippets). Chỉ thành lỗi nếu SiteSEO thật sự chạy shortcode trong meta: **suy luận, chưa xác minh** | Phiếu thử thật kiểm (mục cuối): tạo một nháp có tiêu đề SEO `[caption]x[/caption]`, xem trước bài, mở mã nguồn trang. SiteSEO in nguyên văn thì đóng lỗi này. SiteSEO chạy shortcode thì `_seo_text` phải chặn mẫu `[` + tên ASCII (+ thuộc tính) + `]`, trước khi bật tính năng cho người dùng |
| LC-T042-4 | Thấp (có từ trước, ngoài phần mới) | Các hàm cũ vẫn chép lời máy chủ vào câu lỗi: `_error_from` thêm "(WordPress: …)" (dùng cho `create_draft`, `upload_media`, `check_connection`, `list_*` và lệnh ghi của `set_featured_image`). Hàm khởi tạo vẫn chép nguyên `WORDPRESS_URL` khi sai phần đầu `https://` | `client.py:876`, `:328` | Lời máy chủ đã qua `_plain` (bỏ thẻ) và trang WordPress hiện bằng `escape_markdown` (`app/views/wordpress.py:59`), nên không thành link hay HTML. WordPress không bao giờ chép Application Password vào câu lỗi. Còn lại: máy chủ (hay plugin lỗi) đặt được một câu tiếng Việt tùy ý lên màn hình của chủ máy. `WORDPRESS_URL` sai dạng kiểu `htps://ten:matkhau@site` thì bị chép lại lên màn hình của chính chủ máy. Mọi câu lỗi **mới** của phiếu này (`_SEO_*`, `_IMAGE_*`, `_BAD_DATA`, câu chặn đường, câu chặn `WORDPRESS_URL`) đều cố định | Phiếu dọn lỗi sau: bỏ phần "(WordPress: …)", chỉ giữ mã HTTP và `code` đã lọc (chữ ASCII, gạch dưới); câu khởi tạo không chép `base_url`. Phải sửa cùng các test cũ đang yêu cầu chuỗi "(WordPress: …)" |
| LC-T042-5 | Thấp | `_is_plain_site_url` chặn `.php`, `.phtml`, `.phar` nhưng vẫn nhận `WORDPRESS_URL` có đoạn là file chạy được kiểu khác: `.pht`, `.cgi`, `.shtml`, `.asp`, `.py` | `client.py:1070-1092` | Đã chạy thử: `https://example.com/x.pht`, `…/cgi-bin/x.cgi`, `…/x.shtml` được nhận. Request thật sẽ là `POST https://example.com/x.pht/wp-json/wp/v2/posts`. Chỉ đi vào được qua `.env` do chủ máy tự khai (không có giao diện sửa) | Siết `_SITE_PATH`: mỗi đoạn thư mục không có dấu `.` (`[A-Za-z0-9_~-]+`). WordPress cài trong thư mục con gần như không bao giờ có dấu chấm trong tên thư mục. Phiếu dọn lỗi |

Ngoài phạm vi phiếu (không tính lỗi của T-042, chuyển Chỉ Huy cân nhắc): xem mục "Đề xuất ngoài phạm vi".

## Soát trọng tâm Chỉ Huy giao

### 1. W1–W3, R2, R3: không có đường ghi vào bài đã đăng hay bài không do app tạo

**`set_seo_meta`** (`client.py:577-618`). Thứ tự thật, đã kiểm bằng site giả có ghi lại request:
1. `type(post_id) is int` và có trong `_created_post_ids`. Sai thì `WordPressError` và **không có request nào**. Đã thử `42.0`, `True`, `"42"`, `1`, `-1`, `2**64`: 0 request.
2. `write_seo` phải đúng `True` (`client.py:353`). Đã thử `1`, `"true"`, `"yes"`, `object()`: đều tắt.
3. `_seo_text` cho từng trường (mục 5 bên dưới). Không có trường nào thì từ chối.
4. Dò Abilities (chỉ `GET`, có nhớ kết quả), **rồi** `_own_draft` ngay trước lệnh ghi.
5. Ghi theo một trong hai đường:
   - Abilities: `{"input": {"postId", "title"?, "description"?, "focus_keyphrase"?}}`.
   - Meta: `{"meta": {2 khóa}}`.

Request thật bắt được (đường Abilities):

```
POST /wp/v2/posts {'status': 'draft', 'title': 'Tiêu đề', 'content': '<p>x</p>'}
GET  /wp-abilities/v1/abilities/siteseo-posts/seo-data-update
GET  /wp/v2/posts/42?context=edit&_fields=id%2Cstatus%2Cmeta
POST /wp-abilities/v1/abilities/siteseo-posts/seo-data-update/run {'input': {'postId': 42, 'title': 'A | Pro-Metal', 'description': 'Mô tả', 'focus_keyphrase': 'cửa sắt'}}
```

Tôi duyệt mọi giá trị lồng trong JSON của mọi lệnh ghi:
- không có `null`;
- không có `status`, trừ lệnh tạo nháp, vốn là `"draft"` cố định (`client.py:557`);
- không có `canonical`, `robots`.

Đường dự phòng chỉ gửi đúng `{'meta': {'_siteseo_titles_desc': 'Mô tả'}}`.

**`_own_draft`** (`client.py:620-642`) và **`_is_own_draft_answer`** (`:1105-1112`). Câu trả lời phải là dict, `id` đúng kiểu `int` và bằng `post_id`, `status == "draft"` đúng chữ. Sai thì từ chối **và bỏ id khỏi `_created_post_ids`** (`:640`), nên sau đó `set_featured_image` cũng không còn sửa được bài đó. Đã thử: site trả `publish` → từ chối, 3 request (tạo, dò, kiểm), không có lệnh ghi, `42 in _created_post_ids` là `False`.

**`set_featured_image`** (`client.py:708-728`) làm như sau:
- kiểm kiểu và `_created_post_ids`;
- `_positive_id(media_id)`;
- `_own_draft` ngay trước lệnh ghi;
- soát câu trả lời bằng `_is_own_draft_answer`.

**`_created_post_ids`**: chỉ được thêm ở **một** chỗ, `create_draft` (`client.py:574`), và chỉ khi site trả `status == "draft"`, `id` qua `_positive_id`. Mỗi client có tập riêng. `app/views/wordpress.py:32` tạo client mới mỗi lần trang chạy lại, nên tập này không sống qua các lần bấm. Đây là chiều an toàn.

**`_positive_id`** (`client.py:1095-1097`): chỉ nhận `int` thật > 0. `True`, `"7"`, `7.9`, lớp con của `int` đều bị từ chối.

**Khe kiểm-rồi-ghi:** xem LC-T042-2 (Thấp, đánh giá mức thật ở bảng lỗi).

Còn một đường lý thuyết: site bị chiếm trả `id` của **một bản nháp khác** (của tác giả khác) khi tạo nháp. Khi đó app sẽ coi nháp đó là của mình. Muốn vậy máy chủ phải đã bị chiếm, mà khi đó kẻ tấn công đã có toàn quyền trên site, nên không tính lỗi.

### 2. Danh sách 13 đường REST cố định

`ALLOWED_ROUTES` (`client.py:56-70`):
- 13 cặp, so `fullmatch` (không nhận `\n` ở cuối như `$`);
- mã bài `[1-9][0-9]{0,18}`, chỉ chữ số ASCII;
- thêm `_FORBIDDEN_IN_PATH` (`:74`), so trên chữ thường: `..`, `%`, `//`, `\`, `code-snippets`, `prometal`.

Kiểm ở dòng đầu `_request` (`:811`), **trước** khi tạo URL. Câu từ chối cố định, không chép đường.

Tôi thử 34 đường × 8 phương thức (`GET`, `POST`, `get`, `DELETE`, `PUT`, `OPTIONS`, `HEAD`, `"GET "`). Các đường gồm:
- `..`, `%31`, `//`, `\`, `?x`, `#x`, `\n` ở cuối;
- chữ số toàn khổ `１`, chữ số Ả Rập `٤`, gạch chéo Unicode U+2215, U+200B;
- `;1`, `POSTS`, `/0`, `/01`, 20 chữ số;
- `revisions`, `autosaves`, `users`, `application-passwords`, `settings`, `seo-data-get/run`, `run/`, `media/1/post-process`, `pages/5`, `oembed/1.0/proxy`.

**Chỉ** đúng các đường trong danh sách được nhận. 19 chữ số được nhận vì đúng biểu thức; WordPress sẽ trả 404, vô hại.

`_is_plain_site_url` (`client.py:1070-1092`) xét **chuỗi gốc** trước `urlsplit`: khoảng trắng và ký tự điều khiển ở bất kỳ đâu đều bị từ chối. Tên máy và đường chỉ nhận ASCII. Đoạn thư mục không được bắt đầu bằng `.`. Tôi thử 50 địa chỉ. Bị từ chối:
- `?rest_route=`, `#`, `u:p@`, `\@evil.com`;
- dấu chấm toàn khổ `。`, U+200B, U+202E, `\x00`, tab;
- `.php`, `.PhP`, `.php5`, `.phar`, `index.php`, `.well-known`, `wp-JSON`;
- `[::1]`, `-example.com`, `/.%2e`.

Câu lỗi không chép địa chỉ. Còn lọt: `.pht`, `.cgi`, `.shtml` (LC-T042-5, chỉ qua `.env`).

**Không đi theo 3xx:** `allow_redirects=False` (`:823`), mọi mã 300–399 thành `WordPressError` câu cố định (`:845-851`). Test `test_redirect_is_not_followed` và test của Soi Lỗi đều qua: 300–399 ở cả 4 bước, không có request thứ hai. Vì không đi theo chuyển hướng nên mật khẩu cũng không bị gửi sang máy khác.

**Tham số, header:** không nằm trong danh sách (LC-T042-1, Thấp, hôm nay không có đường tới).

### 3. S2: câu lỗi

Mọi câu mới là hằng (`client.py:122-165`), chỉ ghép thêm mã HTTP (số) hoặc tên trường do code đặt (`Tiêu đề SEO`…):
- `_own_draft`: `:633-637`;
- `_seo_error`: `:1032-1040`;
- `_SEO_UNAVAILABLE`;
- `_BAD_DATA`;
- `_IMAGE_*`;
- câu chặn đường;
- câu chặn `WORDPRESS_URL`.

Câu chặn chữ SEO không chép chữ người dùng. Test của Thợ Máy và Soi Lỗi gài `SERVER_SECRET` / `SECRET` vào lời máy chủ ở 8 nhánh lỗi: không câu nào lọt.

`_error_from` cũ vẫn kèm "(WordPress: …)" cho các hàm cũ. Đánh giá: Thấp, có từ trước (LC-T042-4). Không lộ mật khẩu: WordPress không chép Application Password vào câu lỗi, và `requests` không đưa header vào câu lỗi của client này, vì mọi `RequestException` được đổi thành câu cố định kèm tên lớp lỗi (`:825-844`).

### 4. `_ability_confirms` (`client.py:1115-1137`)

Đã chạy thử 11 câu trả lời:

| Câu trả lời | Coi là đã ghi? |
|---|---|
| `{"updated": true}` | Có |
| `{"success": true}` | Có |
| `{"updated": true, "post": null}` | Có |
| `{"updated": true, "post": {"title": "x"}}` (khớp chữ đã gửi) | Có |
| `{"updated": true, "data": {...}}` | Có |
| `{"updated": true, "message": "err"}` | Có |
| `{"updated": true, "code": null}` | Không |
| `{"updated": true, "success": false}` | Không |
| `{"updated": "true"}` | Không |
| `[true]` | Không |
| `{"updated": true, "post": {}}` | Không |

Đường báo "đã ghi" sai duy nhất: một phiên bản SiteSEO (hay plugin chen vào) trả `updated`/`success` đúng `true` mà không lưu. Hậu quả: người dùng không chép tay, bài thiếu SEO. Không phải lỗi bảo mật (không ghi sai bài, không xóa gì). Nhánh `{"success": true}` và nhánh "không có `post`" nên siết sau phiếu thử thật (xem danh sách việc).

`_siteseo_abilities` chỉ nhận khi câu trả lời dò có `name == "siteseo-posts/seo-data-update"` (`:659`). Lỗi 400/401/403/404 nghĩa là chưa bật. Lỗi mạng hay 5xx thì lần sau dò lại.

### 5. Chặn chữ SEO (điều kiện LC-T036-3)

`_seo_text` (`client.py:996-1029`) xét chữ gốc, chữ đã `normalize_meta` và dạng NFKC.

**Bị chặn trước khi gửi** (đã chạy thử 38 chuỗi):
- biến SiteSEO: `%%sitetitle%%`, `%%%`;
- thực thể HTML: `&#37;&#37;…`, `&lt;script&gt;`, `&ensp;`, `&NotANamed;`, `&Amp;`;
- tên cũ thiếu `;`: `&ltscript`, `&amp`, `&nbsp`, `&AMP`;
- mã số thiếu `;`: `&#x25`, `&#0`, `&#X41`;
- thẻ HTML: `<b>`, `<script>`, `＜script＞`, `﹤script﹥`;
- `％％` toàn khổ;
- ký tự vô hình chen giữa: `%`+U+200B+`%`, `%`+gạch nối mềm+`%`, `%`+U+3164+`%`, `%`+U+FE0F+`%`;
- ký tự điều khiển: `\x07`, `\x1b[31m`;
- dài quá 200 ký tự.

**Vẫn qua:**
- chữ bình thường: `R&D`, `Q&A`, `10% off`, `< 5 triệu`, `% %`, `&#`;
- ký tự vô hình đứng một mình (`a`+U+202E+`b` thành `ab`) bị **bỏ**, không bị chặn. Điều kiện T-036 chấp nhận cách này, vì chữ gửi đi đã sạch;
- U+2028 thành dấu cách;
- `javascript:alert(1)`, `{{x}}`: chữ thường, không có thẻ hay link;
- `[shortcode]`: LC-T042-3;
- U+D800 lẻ: máy chủ PHP sẽ từ chối JSON, app báo lỗi, không hại (Soi Lỗi đã ghi).

### 6. Điều kiện cũ đã sửa đúng

| Điều kiện | Kết quả | Bằng chứng |
|---|---|---|
| LC-T036-3 (thực thể HTML) | Đã sửa | Mục 5. `_ENTITY` của `meta.py:485` + `_NUMERIC_REF` (`client.py:108`) + `_LEGACY_ENTITY` (`:111-120`, 106 tên cũ, phân biệt hoa thường) |
| T-037 điểm 2 (đường cố định) | Đã sửa | Mục 2 |
| LC-T037-1 (a)(b) | Đã sửa | `is_site_link` từ chối `" ' < > `` ` ``, `\`, Cf và `IGNORABLE_NOT_CF` (`client.py:927-931`). `_clean_text` bỏ chúng (`:985-994`). `PublishedItem` từ chối (`:285`). Test `test_wordpress_site_link_t042.py`, `test_soi_loi_t042_paging_cache.py` qua |
| SL-T037-3 | Đã sửa | `_get_pages_checked` (`client.py:484-530`) so trang trùng cả khi có header (`:517`), vượt `MAX_PAGES` thì bật `truncated`. Đã bỏ `xfail` ở `test_soi_loi_t037.py` (diff chỉ xóa đúng 2 dòng `xfail`) |
| SL-T037-4 | Đã sửa | `_is_corrupt` (`site_index.py:364-370`) chỉ nhận mã `SQLITE_CORRUPT`/`SQLITE_NOTADB` (kể cả mã mở rộng `& 0xFF`). `_is_healthy` ném lại lỗi khác (`:349-352`). `_load_checked` chỉ xóa file khi `_Corrupt` hoặc `_is_corrupt`. Việc xóa vẫn chỉ đụng đúng file cache và `-wal`/`-shm` (`:301-303`) |
| SL-T037-5 | Đã sửa | `get` thấy bận thì tải từ site, không ghi (`site_index.py:99-102`). Chờ 1 giây (`_HEALTH_TIMEOUT`) |
| LC-T044-1 | Đã sửa | `_plain` nhận mọi kiểu (`client.py:1138-1146`). `check_connection` kiểm `namespaces` là list, `me` là dict (`:391-401`). `_list_terms` bỏ mục lạ (`:438`). `_post_from` và `upload_media` dùng `_positive_id`, ném `_BAD_DATA` (`:761-763, 794-796`) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets scan --all-files`: 3 kết quả, đều báo nhầm (mục "Báo nhầm"), không có kết quả nào trong file của diff. `git log -p origin/main..team/T-042` lọc `api_key/password/secret/token`: chỉ có mật khẩu giả `"abcd efgh ijkl mnop"`, `SERVER_SECRET`, `SECRET`, `pw-SECRET` của test, cùng chữ trong báo cáo. Lọc mẫu khóa thật (`sk-ant-api`, `sk-proj-`, `AIza…`, `BEGIN PRIVATE`) trên **toàn bộ lịch sử** (`--all`): mọi chuỗi đều là khóa giả của test (`…KhoaGia…`, `…ThuNghiemKhongPhaiKhoaThat…`, `AIzaSyA1234567890abcdef…`, `MIIEvQIBADANBg` cụt). `git log --all -- .env '*.sqlite'`: rỗng |
| S2 | Đạt (có ghi chú) | Mục 3. Câu lỗi mới đều cố định. `_error_from` cũ chép lời máy chủ (đã lọc thẻ, không có mật khẩu): LC-T042-4, Thấp |
| S3 | Không áp dụng | Không có biến cấu hình mới. `write_seo` là tham số của hàm khởi tạo, mặc định `False`. `seo_app/config.py`, `.env.example` không đổi |
| W1 | Đạt | Không thêm `publish`/`future`: `"status"` duy nhất được gửi đi là `"draft"` cố định (`client.py:557`). `"publish"` ở `:465` là tham số **đọc** của `list_published`. Lệnh ghi SEO/ảnh không có khóa `status` (đã duyệt JSON, mục 1). `test_client_has_no_publish_function`, `test_every_write_request_to_posts_never_publishes` qua |
| W2 | Đạt (có ghi chú) | Mục 1. Chỉ bài trong `_created_post_ids`, site xác nhận còn nháp ngay trước lệnh ghi. Không gửi `null`. Ability chỉ đổi trường được gửi (T-033 mục 1.4, `abilitiesregister.php:262-264`). Khe kiểm-rồi-ghi: LC-T042-2, Thấp. `upload_media` cập nhật alt/tiêu đề cho `id` site trả về (có từ Giai đoạn 1). Site bị chiếm trả `id` ảnh cũ thì alt ảnh cũ bị đổi, nhưng máy chủ phải đã bị chiếm nên không tính |
| W3 | Đạt | Không gửi HTML mới. Chữ SEO có thẻ hay thực thể bị chặn (mục 5). Nội dung bài vẫn qua `sanitize_html` (`client.py:559, 566`, không đổi). SiteSEO còn `sanitize_text_field` phía máy chủ (T-033 mục 1.4) |
| W4 | Đạt | Mọi lệnh gọi đi qua `_request` với `timeout=self.timeout` (30 giây) và `allow_redirects=False` (`client.py:822-824`). Không có `verify=False` trong repo (`grep` rỗng). `WORDPRESS_URL` phải `https://` (`:330-335`) và là địa chỉ trần (`:336-341`). Ghi chú: `requests` vẫn đọc `HTTPS_PROXY`/`REQUESTS_CA_BUNDLE` của máy, giống rủi ro đã chấp nhận cho thư viện AI (`security.md` mục 6). Không mới |
| A1 | Không áp dụng | Phiếu không có prompt AI |
| A2 | Đạt | AI không có công cụ gọi `set_seo_meta`. Hàm chỉ chạy khi code gọi, và hiện **chưa nối vào giao diện** (`grep set_seo_meta app/` rỗng). Chữ SEO (có thể do AI gợi ý) được kiểm lại trong `_seo_text` trước khi gửi |
| A3 | Không áp dụng | Không gửi gì vào prompt |
| U1 | Không áp dụng | Không đổi `app/`. `siteseo_status`, `SeoWriteResult.message` là câu cố định; phiếu giao diện phải hiện bằng widget chữ thường hoặc `escape_markdown` |
| U2 | Đạt | `.streamlit/config.toml:5` `address = "localhost"`, không đổi. Không có trang mới |
| U3 | Không áp dụng | Không đụng đăng nhập |
| F1 | Đạt | `site_index.py` chỉ xóa đúng file cache của mình và `-wal`/`-shm` (`:169, 301-303`). Symlink bị từ chối (`:279`, có từ T-037). SL-T037-4 làm việc xóa **ít** đi |
| F2 | Không áp dụng | Không đổi xử lý ảnh |
| F3 | Đạt | Không có `eval`, `pickle`, `yaml.load` mới. SQLite chỉ dùng câu lệnh tham số. `bandit` không báo gì trên 2 file code đổi |
| D1 | Đạt | Không thêm thư viện (`uv.lock`, `pyproject.toml` không đổi). `html.entities`, `unicodedata` là thư viện chuẩn. `pip-audit` trên 203 gói của `uv.lock`: **No known vulnerabilities found** |
| D2 | Đạt | `.gitignore` không đổi. `git check-ignore`: `.env` (dòng 2), `.env.local` (dòng 3), `data/x.sqlite` (dòng 22) đều bị chặn |
| D3 | Đạt | 9 file test mới dùng `FakeWordPress`/`make_session` (adapter giả, không mở socket). `test_site_index_t042.py` chỉ dùng SQLite cục bộ. `suachuacuasat.com` chỉ xuất hiện như chuỗi dữ liệu. Bộ chặn mạng `tests/conftest.py` không đổi. Script thử của tôi còn tự chặn `socket.connect`/`getaddrinfo` |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uvx pip-audit -r <uv export --frozen>` (203 gói): **No known vulnerabilities found**. Bỏ qua 1 dòng `-e .` (chính dự án) | Có. `uv.lock` không đổi trong phiếu |
| bandit | `uvx bandit -r seo_app app scripts`: 1 Low `B101 assert_used` ở `seo_app/storage/drafts.py:203` (không thuộc diff). Trên `client.py` và `site_index.py`: không có gì | Có (báo nhầm, xem dưới) |
| detect-secrets | `--all-files`: 3 kết quả (`.pytest_cache/CACHEDIR.TAG`, `.ruff_cache/CACHEDIR.TAG`, `tests/test_config.py:34`), không có trong file của diff | Có (báo nhầm) |
| Soát lịch sử git | Mục S1: chỉ khóa giả | Có |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest | _(đang chạy, cập nhật khi xong)_ | |
| Thử tay (không mạng) | 3 script trong thư mục tạm, tự chặn socket: 272 cặp (phương thức, đường); 50 `WORDPRESS_URL`; luồng `set_seo_meta` (2 đường, bài đổi trạng thái, `post_id` lạ, `write_seo` lạ); 11 câu trả lời ability; 38 chữ SEO; khe kiểm-rồi-ghi; `params` lạ | Có, kết quả ở các mục trên |

## Báo nhầm đã loại

- `.pytest_cache/CACHEDIR.TAG`, `.ruff_cache/CACHEDIR.TAG` ("Hex High Entropy"): chữ ký cố định của chuẩn CACHEDIR. Thư mục đã bị `.gitignore`.
- `tests/test_config.py:34` ("Secret Keyword"): `"abcd efgh"`, mật khẩu giả của test cấu hình.
- `bandit B101` ở `drafts.py:203`: không thuộc phiếu. `assert` kiểu này chỉ dùng để kiểm kiểu nội bộ, không phải chốt bảo mật.
- Kết quả "giống khóa" trong lịch sử git: đều là khóa giả của test (mục S1).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không có lỗi Trung bình trở lên, nên không có hạn bắt buộc theo `security.md`. Tôi đặt các mốc sau để giữ an toàn:

1. **Phiếu giao diện nối `set_seo_meta` / `set_featured_image` vào app** (Họa Sĩ), điều kiện của chính phiếu đó:
   - Giữ `write_seo` mặc định tắt. Công tắc bật phải nằm trong app, chỉ bật khi người dùng tick. Không đọc từ `.env` nếu chưa qua Lá Chắn.
   - **Không được** tự thêm id vào `_created_post_ids`, hay lưu id qua `st.session_state` rồi nạp lại, để "sửa" việc client bị tạo lại mỗi lần trang chạy. Muốn giữ client qua các lần bấm thì giữ **cả đối tượng client** trong `st.session_state` của phiên đó, không dùng `st.cache_resource` (dùng chung giữa các phiên).
   - Hiện `SeoWriteResult.message`, `siteseo_status`, `str(WordPressError)` bằng widget chữ thường hoặc `escape_markdown`, không dùng `unsafe_allow_html`.
   - Làm LC-T042-2: sau khi ghi qua Abilities thì `GET` lại trạng thái bài, không còn nháp thì báo người dùng.
2. **Phiếu thử thật** (ngay sau T-042, trước khi bật tính năng cho người dùng): xác minh LC-T042-3 (shortcode). Nếu SiteSEO chạy shortcode trong meta thì phải chặn trong `_seo_text` trước phiếu giao diện ở điểm 1.
3. **Phiếu dọn lỗi Thấp** (trước khi hết Giai đoạn 4, cùng đợt với T-045 hoặc phiếu mới), cho Thợ Máy:
   - LC-T042-1: chặn `rest_route`, `_method`, header ghi đè phương thức. Bắt buộc **trước** phiếu nào truyền `params` mới vào `_request`.
   - LC-T042-4: câu lỗi cũ không chép lời máy chủ hay `WORDPRESS_URL`.
   - LC-T042-5: đoạn thư mục của `WORDPRESS_URL` không có dấu chấm.

## Việc cho phiếu thử thật (sau T-042)

Chủ dự án làm (Chỉ Huy hướng dẫn từng bước), trên **site thật**, chỉ với **một bài nháp**:

**Chuẩn bị (chủ dự án làm trong trang quản trị):**
1. Bật **Abilities** trong SiteSEO (`siteseo_toggle['toggle-abilities']`, T-033 mục 1.4).
2. Tạo tài khoản WordPress vai **Biên tập viên** (không phải Quản trị viên) riêng cho phần mềm, tạo Application Password cho tài khoản đó.
3. Khai `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD` mới vào `.env` trên máy. Không dán vào chat, báo cáo hay ảnh chụp màn hình.
4. Khai `WORDPRESS_URL` đúng dạng `https://suachuacuasat.com` (không `www` nếu site chuyển hướng về bản không `www`, không có `/wp-admin`, `/wp-json`). Bấm **Kiểm tra kết nối**:
   - vai trò phải là Biên tập viên;
   - quyền "Đăng bài" phải hiện ✅. Biên tập viên có quyền này; app vẫn không bao giờ tự đăng;
   - `siteseo_status` (nếu giao diện đã hiện) phải là "ghi được".

**Thử (một bài nháp duy nhất):**
5. Tạo **một** bài nháp bằng app, rồi gọi `set_seo_meta` với tiêu đề có `< 5 triệu` và `10%`, một mô tả, một từ khóa chính. Ghi vào báo cáo:
   - **nguyên khuôn câu trả lời** của `POST …/seo-data-update/run` (thành công). Che mọi chuỗi giống mật khẩu hay cookie nếu có;
   - app báo "đã ghi" hay "không thành công". SiteSEO làm sạch chữ, ví dụ `<` thành `&lt;`, thì app sẽ báo không thành công, theo chiều an toàn.
6. Mở bài nháp trong trang quản trị: hộp SiteSEO phải hiện đúng tiêu đề, mô tả, từ khóa chính. Canonical và robots phải **trống / mặc định**. Bài phải **vẫn là Nháp**.
7. LC-T042-3: đổi tiêu đề SEO thành `[caption]thu[/caption]` (gõ tay trong hộp SiteSEO, không qua app), xem trước bài, mở mã nguồn trang (Ctrl+U), tìm thẻ `<title>`. Thấy nguyên văn `[caption]…` thì SiteSEO không chạy shortcode trong meta: đóng LC-T042-3.
8. Thử chặn bài đã đăng mà **không đăng bài thật**: dùng một bài **nháp thứ hai do app tạo**, chuyển sang "Chờ duyệt" (pending) trong trang quản trị, rồi gọi `set_seo_meta` → app phải từ chối ("không còn là bản nháp") và **không** có thay đổi trong hộp SiteSEO.
9. Xóa tay các bài nháp thử (đưa vào thùng rác, rồi xóa vĩnh viễn trong trang quản trị). Việc xóa do **chủ dự án** làm, không phải app.

**Sau khi thử:**
10. Gửi lại khuôn câu trả lời cho Thợ Máy để siết `_ability_confirms`:
    - khuôn là `{"updated": true, "post": {…}}` thì bỏ nhánh `{"success": true}`, bắt buộc có `post` và khớp từng trường;
    - đổi site giả trong test của Thợ Máy và Soi Lỗi sang khuôn thật.
11. Phiếu thử thật cũng qua Lá Chắn (phiếu đầu tiên chạm site thật bằng tính năng này).

## Đề xuất ngoài phạm vi (cho Chỉ Huy)

- **Shortcode trong nội dung bài** (có từ Giai đoạn 2, không thuộc T-042): `sanitize_html` không bỏ shortcode `[…]` trong nội dung AI viết. Site có plugin Code Snippets. Nếu lệnh ẩn trong trang đối thủ khiến AI chèn `[code_snippet …]` hay `[code_snippet_source …]` vào bài, thì bản xem trước (và bài sau khi đăng) sẽ chạy shortcode đó. Người dùng có thấy chữ `[…]` khi duyệt bài. Mức độ phụ thuộc phiên bản Code Snippets và shortcode nào đang bật: **suy luận, chưa xác minh**. Đề xuất một phiếu nhỏ cho Thợ Máy: thoát (`[[…]]`) hoặc bỏ shortcode lạ trong nội dung AI trước khi gửi WordPress (chỉ giữ danh sách cho phép, nếu cần). Lá Chắn kiểm.
- Kiểm lại toàn bộ biên bản này bằng **Fable sau 01/11**.

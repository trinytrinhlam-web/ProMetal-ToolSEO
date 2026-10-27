# Biên bản bảo mật T-094 · Đọc thiết kế Giai đoạn 5 (kế hoạch, Google Sheets, hẹn giờ, đăng bài) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-094](../tickets/T-094-thiet-ke-giai-doan-5.md) · báo cáo thiết kế [T-094-tho-may.md](T-094-tho-may.md) |
| Phạm vi | Rút gọn, **chỉ đọc**: diff `origin/main...team/T-094` (1 commit `4812b96`, chỉ thêm `docs/team/reports/T-094-tho-may.md`, 556 dòng). Đối chiếu `docs/team/security.md`, `docs/team/board.md` mục «Việc bắt buộc khi làm Giai đoạn 5», và code mà thiết kế dựa vào: `seo_app/wordpress/client.py` (`ALLOWED_ROUTES`, `ALLOWED_JSON_KEYS`, `_is_plain_request`, `_created_post_ids`, `_own_draft`), `seo_app/sanitize.py`, `seo_app/env_file.py`, `seo_app/config.py`, `seo_app/content/prompts.py`, `app/views/write.py` (`wordpress_client`, `send_draft`), `.gitignore`, `.env.example`, `uv.lock`. Đọc lại mã WordPress `class-wp-embed.php` (`autoembed`) |
| Ngày | 2026-10-27 (23:03–23:26 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT** cho phiếu tài liệu (không bí mật, không dữ liệu khách). **Thiết kế đủ để mở phiếu code**, với điều kiện Chỉ Huy chép **44 điều kiện bảo mật LC-T094-1 → -44** vào đúng phiếu (mục «Điều kiện theo phiếu»). Không có chỗ nào phải thiết kế lại; 13 chỗ thiếu đã có cách sửa nằm trong các điều kiện. **Chạy trước được:** T-096, T-098, T-097 (đợt 1); T-099 sau T-091 |

## Tóm tắt (cho chủ dự án)

- **Thiết kế Giai đoạn 5 an toàn và đủ để bắt đầu viết code.** Những điểm quan trọng nhất đều đúng hướng: bài luôn lên WordPress dạng **nháp trước**, chỉ đúng **một chỗ trong code** được chuyển sang hẹn giờ hay đăng, sau **màn hình xác nhận** liệt kê mọi link, ảnh còn GPS và SEO; app **không bao giờ sửa bài đã đăng**; ghi Google Sheets luôn ở dạng chữ thường (không ai cài công thức độc được); chặn hẹn giờ quá gần (WordPress sẽ đăng ngay) và chặn đoạn chỉ có một địa chỉ web (WordPress sẽ tự nhúng trang đó vào bài).
- Tôi bổ sung **44 điều kiện** để các phiếu code làm cho đúng, ví dụ: file khóa Google phải nằm ngoài thư mục dự án và ngoài thư mục ảnh/thư mục đồng bộ, không bao giờ hiện nội dung; app chỉ dùng đúng file khóa đó (không tự lấy tài khoản Google khác trên máy); mã Google Sheet ghi vào `.env` phải được kiểm chặt; chữ từ Sheet hay file tải lên luôn là dữ liệu chưa tin cậy; nếu ghi chú kế hoạch có số điện thoại, email của khách thì app nhắc trước khi gửi cho AI; nút Hẹn giờ, Đăng ngay **mặc định tắt** cho tới khi thử thật trên website xong (như công tắc ghi SEO).
- **Việc của bạn:** khi tạo Google Sheet kế hoạch, **đừng** bật «Bất kỳ ai có đường liên kết đều chỉnh sửa được»; chỉ chia sẻ cho email của tài khoản dịch vụ. File khóa Google giữ như mật khẩu: không gửi qua email, Zalo. README sẽ hướng dẫn từng bước.

## Bằng chứng (phiếu tài liệu)

| Kiểm | Lệnh | Kết quả |
|---|---|---|
| Chỉ đúng 1 file | `git diff --stat origin/main...HEAD`, `git log --oneline origin/main..HEAD` | `docs/team/reports/T-094-tho-may.md` (+556), 1 commit `4812b96`. Không sửa code, cấu hình, test |
| Quét bí mật file | `PYTHONUTF8=1 uvx detect-secrets scan docs/team/reports/T-094-tho-may.md` | 0 phát hiện |
| Quét bí mật cả patch của nhánh | `git log -p origin/main..HEAD` ra file nháp → `PYTHONUTF8=1 uvx detect-secrets scan` | 0 phát hiện |
| Khóa, mật khẩu, đường dẫn máy, dữ liệu khách | grep `api_key=`, `password=`, `sk-ant`, `AIza…`, `BEGIN PRIVATE`, `C:/Users`, `/Users/`, `@gmail`, số điện thoại 10 chữ số | Chỉ khớp dòng mô tả đuôi email `.iam.gserviceaccount.com` (chữ mẫu, không phải địa chỉ thật) |
| Thiết kế không gọi Google, WordPress thật | đọc toàn văn | Chỉ đọc mã nguồn, tài liệu công khai; không đọc `.env` |

## Đối chiếu với code hiện có (điều thiết kế dựa vào)

| Điều thiết kế dựa vào | Đối chiếu | Kết quả |
|---|---|---|
| Client WordPress tạo mới mỗi lần gửi, nên `_created_post_ids` chỉ có bài của lần gửi đó | `app/views/write.py:2566-2570` (`wordpress_client`: «Client mới mỗi lần gọi (không `st.cache_resource`: điều kiện Lá Chắn T-042)») | Đúng. Giữ bất biến này cho `release_draft` (LC-T094-23) |
| Thân JSON tạo bài chỉ nhận `status = "draft"` | `client.py` `_is_plain_request` (T-085) | Đúng. T-099 sửa đúng chỗ này, có dấu riêng (LC-T094-22) |
| `sanitize_html` bỏ chú thích HTML (dấu khối Gutenberg `<!-- wp:… -->` chạy khối động như RSS) | `sanitize.py:772-783` (`handle_comment`, `handle_decl`, `handle_pi`, `unknown_decl` đều bỏ); thử: `<!-- wp:core/rss {"feedURL":…} /-->` → bỏ; CDATA, `<?php ?>` → bỏ; `<h1>` → chỉ còn chữ; bảng giữ nguyên | Đúng |
| Đoạn chỉ có một địa chỉ bị WordPress nhúng | Thử: `sanitize_html('<p>https://www.youtube.com/watch?v=abc</p>')` trả **nguyên văn**, tức bộ lọc không chặn. Mã WordPress (`class-wp-embed.php`, trunk, đọc 2026-10-27): `autoembed` ở `the_content` mức 8, trước `wpautop`; 2 biểu thức: dòng chỉ có địa chỉ `\|^(\s*)(https?://[^\s<>"]+)(\s*)$\|im` (sau khi đổi `\n` trong thẻ thành chỗ giữ), và `<p>` chỉ có địa chỉ | Chốt chặn ở bộ dựng là **bắt buộc**; phải dùng đúng cả hai biểu thức (LC-T094-6) |
| Ghi `GOOGLE_SHEET_ID` vào `.env` từ Cài đặt | `env_file.py`: chỉ ghi 3 khóa AI (`ALLOWED_KEYS`), bộ kiểm `validate_key_value` cho phép `/ : + . ~`, ghi nguyên tử, quyền 600 | Phải thêm bộ kiểm **riêng** cho mã Sheet (LC-T094-15) |
| `google-auth` đã có | `uv.lock:406-412`: 2.62.0, phụ thuộc `cryptography`, `pyasn1-modules` (không có gói `rsa`); `pip-audit` trên 69 gói của `uv export` sạch ở các lượt T-085, T-088 (26/10) | Đúng. Quét lại ở T-097 (LC-T094-16) |
| `.gitignore` chỉ chặn `*service-account*.json` | `.gitignore:5`; `data/` chặn ở `:22` | Đúng: app phải tự từ chối file khóa trong thư mục dự án (LC-T094-11) |
| Từ khóa ngoài khung dữ liệu (SL-7) | `tests/test_soi_loi_t003_t009.py:209-213` (`xfail` strict) | Còn mở, T-098 đóng (LC-T094-19) |

## Điều kiện theo phiếu (Chỉ Huy chép vào phiếu)

Mỗi điều kiện có cách kiểm; Lá Chắn của phiếu đó kiểm đúng các dòng này. «Chặn» là không gửi gì; «Cảnh báo» là báo, người dùng vẫn làm tiếp được.

### Chung cho mọi phiếu Giai đoạn 5

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-1 | Test không gọi Google, WordPress thật: Sheets và máy chủ mã (token) giả bằng adapter như `FakeWordPress`; bộ chặn mạng của `tests/conftest.py` vẫn bật | Lá Chắn đọc test (D3) |
| LC-T094-2 | Mọi câu báo lỗi mới (Sheets, file khóa, kế hoạch, hẹn giờ) là câu cố định: không chép lời máy chủ Google, WordPress; không chép nội dung file khóa, đường dẫn đầy đủ, mã Sheet, chữ ô Sheet; lỗi của `google-auth` (`RefreshError`, `TransportError`, `MalformedError`…) và `json.JSONDecodeError` khi đọc file khóa thành câu cố định (`from None`; không bao giờ in `exc.doc`, `exc.args`) | Test gài chuỗi mồi vào lời máy chủ và file khóa hỏng: câu báo không có mồi (S2) |
| LC-T094-3 | Chữ từ Sheet, file, chữ dán, AI, website hiện trên giao diện là **chữ thuần** (`st.dataframe`, `st.text`, `escape_markdown`); không `unsafe_allow_html`, không `st.markdown` có link; link không bấm được; bỏ ký tự điều khiển hướng chữ (U+202A–U+202E, U+2066–U+2069) và ký tự vô hình trước khi hiện, để bảng duyệt không hiện chữ đánh lừa | AppTest gài chữ có `[x](javascript:…)`, `<b>`, U+202E: hiện thuần (U1) |

### T-096 · Bộ dựng bài cuối (Markdown → HTML, dữ liệu xác nhận)

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-4 | Bộ chuyển Markdown **không bao giờ** sinh `<a>`, `<img>`, `<iframe>`, HTML thô hay chú thích HTML. Mọi chữ qua `html.escape` rồi `escape_shortcodes`. `[x](url)`, `![x](url)`, `<https://…>`, khai báo link tham chiếu `[1]: url`, autolink, `<tag>` thô đều ra chữ thường. Chỉ `apply_links` (bài trong `SiteIndex`) sinh `<a>`; chỉ `figure_html` (ảnh app vừa tải) sinh `<img>` | Test đối kháng gồm mẫu của T-015, T-031, T-061: `javascript:`, `data:`, `&#106;avascript:`, `[x][1]` + `[1]: url`, U+200B trong địa chỉ, `\[`, `\<`, `<!-- wp:… -->`: HTML ra không có thẻ nào ngoài danh sách của bộ chuyển |
| LC-T094-5 | Thứ tự trên **đúng chuỗi sẽ gửi**: `sanitize_html` → `apply_links` → `sanitize_html` → `check_links(…, required_ids)` (LC-T039 đk 3a); không bước nào sửa HTML sau `check_links`; mã băm (LC-T094-8) tính trên chính chuỗi đó | Test bộ dựng với client, index giả |
| LC-T094-6 | Chặn nhúng: áp **đúng hai biểu thức** của `WP_Embed::autoembed` lên HTML cuối (dòng chỉ có địa chỉ, tính sau khi đổi `\n` nằm trong thẻ như `wp_replace_in_html_tags`; `<p>` chỉ có địa chỉ). Khớp thì **Chặn** ở **mọi** hình thức gửi, kể cả Nháp (bài nháp đăng sau trong trang quản trị vẫn bị nhúng) | Test: `<p>https://youtube…</p>`, `<p> https://x </p>`, địa chỉ đứng một dòng trong `<li>`, `\r\n`: Chặn; địa chỉ giữa câu: không chặn |
| LC-T094-7 | `ArticleReview` (dữ liệu màn hình xác nhận) liệt kê **mọi** `href` của HTML cuối: tên máy dạng ASCII (punycode), cờ cho tên máy ngoài ASCII, có `@`, `\`, `//` đầu, cổng lạ, khác tên máy site; mọi địa chỉ trần, email còn trong chữ (sau `unbreak_autolinks`); đoạn dạng shortcode; từng ảnh còn GPS hay không. Trả chữ thô kèm cờ «phải escape» (bất biến board: kết quả `unescape_link_syntax`/`unbreak_autolinks` không vào `st.markdown`) | Test với `suachuacuasаt.com` (а Kirin), `https://a@b`, `//evil`, `http://x:8080` |
| LC-T094-8 | Mã băm xác nhận: SHA-256 trên **bản chuẩn hóa xác định** (JSON khóa sắp xếp, UTF-8, `separators=(",", ":")`) của mọi thứ sẽ gửi: tiêu đề, HTML cuối, đoạn trích, slug, mã chuyên mục, mã thẻ, băm từng ảnh cùng alt, chú thích, ảnh đại diện, 3 ô SEO và công tắc ghi SEO, hình thức, giờ hẹn UTC đúng chuỗi `date_gmt` sẽ gửi | Test: đổi một ký tự ở bất kỳ phần nào → mã băm khác |
| LC-T094-9 | `unbreak_autolinks` chỉ chạy trong bộ dựng, trên chữ thô **trước** khi escape; chữ sau khi gỡ vẫn coi là chưa an toàn (vẫn escape, lọc, kiểm địa chỉ trần) | Test theo gợi ý của T-031: HTML gửi đi không còn U+200B, không có `<a>` ngoài link nội bộ |
| LC-T094-10 | Sửa LC-T039-2 trong `links.py` (gỡ 3 `xfail` của `tests/test_la_chan_t039.py`) **trước** khi bộ dựng dùng `apply_links`; thân bài không có `<h1>`, `<h2>` (tiêu đề trong thân hạ xuống `h3`+, LC-T039 đk 3b) | 3 test XPASS rồi gỡ dấu; test cấp tiêu đề |

### T-097 · Google Sheets và tài khoản dịch vụ

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-11 | Kiểm file khóa trước **mỗi** lần dùng, như thiết kế mục 2.1, thêm: so **đường dẫn thật** (`resolve(strict=True)`, theo symlink, junction): từ chối nếu nằm trong thư mục dự án hoặc trong bất kỳ gốc `IMAGE_FOLDERS` nào (thư mục ảnh thường là thư mục Drive đồng bộ); chỉ file thường, ≤ 64 KB; mở một lần rồi đọc từ chính handle đó (không kiểm rồi mở lại); đường dẫn có đoạn `Google Drive`, `My Drive`, `OneDrive`, `Dropbox`, `iCloud` → Cảnh báo; Mac/Linux: nhóm hay người khác đọc được (`st_mode & 0o077`) → Cảnh báo kèm cách `chmod 600` | Test: file trong dự án, qua symlink trỏ vào dự án, trong thư mục ảnh, file 65 KB, thư mục, `type` khác, `token_uri` lạ, `universe_domain` lạ: từ chối, câu cố định |
| LC-T094-12 | Không bao giờ in, ghi log, gửi AI, ghi Sheet, cache, báo cáo: nội dung file khóa (cả trường khóa riêng và mã của khóa riêng), mã truy cập. `repr`/`str` của đối tượng xác thực và của client Sheets không có khóa. Mã truy cập chỉ trong bộ nhớ, không ghi đĩa. Giao diện chỉ hiện «đã khai báo / chưa khai báo», **tên file** (không đường dẫn đầy đủ, như T-084) và email dịch vụ (cần để chia sẻ Sheet; chỉ ở trang Cài đặt) | Test `repr`; grep code: không `print`, `logging`, `st.write` với đối tượng xác thực |
| LC-T094-13 | Client Sheets có danh sách đường cố định (thiết kế mục 2.3), kiểm **trước khi gửi** như `ALLOWED_ROUTES`/`_is_plain_request`: chỉ `https://sheets.googleapis.com` (và `https://oauth2.googleapis.com/token` cho mã); `spreadsheetId` khớp `[A-Za-z0-9_-]{25,100}`; vùng ô dựng từ hằng tên tab và **chỉ số** cột (không từ chữ tiêu đề cột của Sheet); tham số theo danh sách từng đường; **`valueInputOption` chỉ nhận `RAW`** (chặn ở lớp kiểm, không chỉ ở nơi gọi); `:batchUpdate` chỉ nhận 4 loại yêu cầu của thiết kế, đúng `sheetId` của tab «KeHoach» vừa đọc (không bao giờ `deleteSheet`, `deleteDimension`, `deleteRange`, `updateSpreadsheetProperties`, `duplicateSheet`, `addProtectedRange`); không theo chuyển hướng ở cả lệnh Sheets lẫn lệnh xin mã (`allow_redirects=False`, phiên xin mã `max_redirects = 0`); timeout ≤ 30 giây cho cả lệnh xin mã; câu trả lời đọc theo luồng, quá 2 MB thì bỏ; thử lại đúng như thiết kế (lệnh thêm dòng không bao giờ tự thử lại) | Test mọi đường lạ, `USER_ENTERED`, loại `batchUpdate` lạ, `sheetId` khác, chuyển hướng, câu trả lời 3 MB: không có request hay báo lỗi cố định |
| LC-T094-14 | Xác thực chỉ bằng `service_account.Credentials.from_service_account_info(<dict đã kiểm>)` với đúng một phạm vi hằng `https://www.googleapis.com/auth/spreadsheets`. **Không** dùng `google.auth.default()` (không đọc `GOOGLE_APPLICATION_CREDENTIALS`, cấu hình `gcloud`, máy chủ metadata), không `with_subject` (ủy quyền toàn miền), không thêm phạm vi Drive | Test: đặt `GOOGLE_APPLICATION_CREDENTIALS` trỏ file khác → không được dùng; grep `google.auth.default`, `with_subject`: 0 |
| LC-T094-15 | Mã Sheet chỉ tách từ link đúng dạng `https://docs.google.com/spreadsheets/d/<mã>/…` (tên máy đúng chữ, không `@`, không cổng, không `\`); **không bao giờ** mở link người dùng dán. Ghi `GOOGLE_SHEET_ID` qua `env_file.py` với bộ kiểm **riêng** `[A-Za-z0-9_-]{25,100}` (không dùng `validate_key_value` của khóa AI), giữ ghi nguyên tử, quyền 600, giữ nguyên dòng khác; `load_settings` kiểm lại dạng mã khi đọc. `GOOGLE_SERVICE_ACCOUNT_FILE` **không** ghi được từ giao diện. Mã Sheet coi như nửa bí mật (Sheet lỡ bật «bất kỳ ai có link» thì mã là chìa khóa): không hiện đầy đủ trong câu báo, log, báo cáo; giao diện hiện **tên** Sheet đọc từ API (đã escape) | Test link `docs.google.com.evil.example`, `https://x@docs.google.com/…`, mã có `\n`, `=`, `"`: từ chối, `.env` không đổi |
| LC-T094-16 | Khai báo `google-auth` đúng bản đã khóa (`>=2.62.0`, không nới); `uv.lock` không thêm gói nào (`git diff uv.lock` chỉ đổi phần khai báo của dự án); `pip-audit` sạch trên `uv export` lúc làm phiếu. Không thêm `gspread`, `google-api-python-client`, `openpyxl` (câu 2 chọn A) | Lá Chắn quét (D1) |
| LC-T094-17 | Test không có khóa thật, không có khóa PEM cố định trong repo: sinh khóa RSA lúc chạy test bằng `cryptography` (đã có); `detect-secrets` (`PYTHONUTF8=1`) trên diff không có «Private Key» | Lá Chắn quét (S1) |

### T-098 · Kế hoạch: khuôn dữ liệu, đọc, đề xuất (có AI)

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-18 | Mọi dữ liệu kế hoạch (file, chữ dán, Sheet, cache, AI) qua đúng một bộ làm sạch `PlanRow` (`extra="forbid"`): NFC; bỏ ký tự Cc (trừ khoảng trắng thường), Cf (gồm điều khiển hướng chữ), Cs, Co, Cn như `normalize_meta` của T-041; giới hạn kiểm **theo byte trước khi giải mã** (file ≤ 1 MB), ≤ 1.000 dòng, ≤ 26 cột, ô ≤ 2.000 ký tự, chữ dán ≤ 20.000; chỉ `utf-8`, `utf-8-sig` (không đoán bảng mã); CSV bằng `csv` chuẩn (không `eval`, không `pandas`); ngày không nhận `mm/dd`; số ngày kiểu Sheets nằm trong khoảng hợp lý (ví dụ năm 2020–2035) | Test file 2 MB, 1.001 dòng, ô 5.000 ký tự, cp1258, U+202E, U+0000 |
| LC-T094-19 | SL-7: `_neutralize` (và đổi «» như `rewrite_prompt`) cho từ khóa ở **mọi** lời dặn, cả từ khóa gõ tay; gỡ `xfail` `test_keyword_cannot_fake_a_frame` khi XPASS. Lời dặn `plan`: kế hoạch hiện tại và kế hoạch mới mỗi thứ một khung (thêm vào `DATA_TAGS`), kèm `DATA_RULES`. Việc `plan` **không bao giờ** có tìm web: chặn trong code dù `config/ai.toml` bật (như T-062: phần bảo vệ nằm trong code) | Test từ khóa có `</du_lieu_tham_khao>`, `</ke_hoach_moi>`; test cấu hình `web_search = true` cho `plan` vẫn không tìm web (A1) |
| LC-T094-20 | Kết quả AI (`PlanSuggestions`) là dữ liệu chưa tin cậy: khuôn chặt, ≤ 100 mục, sai thì bỏ (chỉ đếm, không chép chữ AI vào câu báo); `key` phải có thật với «Cập nhật», «Bỏ»; nhãn thuộc danh sách cố định; ngày trong khoảng; `reason` chữ thường ≤ 300 ký tự. **AI không đưa được địa chỉ web nào vào kế hoạch hay bài**: cột trang đích chỉ nhận mã bài có trong `SiteIndex`, chuỗi dạng URL ở `reason`, `notes`, `title_hint` chỉ là chữ. «Bỏ» không tick sẵn; không đường nào xóa dòng | Test AI giả trả mục sai kiểu, `key` không có, trang đích ngoài site, 150 mục (A2) |
| LC-T094-21 | A3: trước khi gửi chữ kế hoạch cho AI (`plan`) và khi điền «Ghi chú của thợ» vào Soạn bài, dò số điện thoại Việt Nam, email → **Cảnh báo** kèm nút che (`[đã ẩn]`) hoặc để người dùng sửa; không gửi mà người dùng chưa thấy cảnh báo | Test chữ có `0909 123 456`, `+84 909…`, `a@b.vn` (A3) |

### T-099 · Client WordPress: hẹn giờ, đăng ngay, đọc trạng thái (soát kỹ nhất)

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-22 | **Đúng một đường:** `release_draft` là hàm duy nhất gửi được `status` khác `"draft"` và khóa `date_gmt`. `_is_plain_request` chỉ cho hai khóa đó khi lệnh mang dấu riêng `_RELEASE` (so bằng `is`), đúng `POST /wp/v2/posts/<mã>`, thân **đúng** `{"status": "future", "date_gmt": …}` hoặc `{"status": "publish"}` (`str`, đúng chữ); dấu riêng bị gỡ khỏi tùy chọn trước khi tới `requests`; `date` không bao giờ được nhận; lệnh tạo bài vẫn chỉ `"draft"`. Test đọc mã nguồn: `_RELEASE` chỉ ở định nghĩa, `release_draft`, `_is_plain_request`; `release_draft` chỉ được gọi từ đúng một hàm của bước Xuất bản (T-102) | Test thiết kế mục 3.3 (mọi hàm khác gửi `status` lạ, `date_gmt` → 0 request) (W1) |
| LC-T094-23 | Chỉ bài tạo trong **chính lần gửi này** bằng **chính đối tượng client** (client tạo mới mỗi lần bấm như `wordpress_client()` hiện nay; không `st.cache_resource`, không giữ client trong `session_state`): mã bài thuộc `_created_post_ids`; hỏi lại site còn `draft` ngay trước lệnh (`_own_draft`). **Nên** so `modified_gmt` với giá trị app nhận ở lệnh ghi cuối của mình (ai đó vừa sửa nháp trong trang quản trị giữa lúc tạo và lúc đăng → dừng, báo). Sau khi chuyển: bỏ mã bài khỏi `_created_post_ids`. Câu 5 chọn A: không hẹn giờ, đăng bài nháp có từ trước | Test: bài không do client tạo, bài `publish`/`future`/`pending`/`private`, client của lượt chạy khác → 0 request (W2, R3) |
| LC-T094-24 | **Giờ:** `when_utc` phải có múi giờ; giờ máy chủ lấy từ header `Date` của câu trả lời `_own_draft` **ngay trước** lệnh, đọc bằng `email.utils.parsedate_to_datetime`; thiếu hay sai dạng → **Chặn** (không lấy đồng hồ máy thay); lệch đồng hồ máy > 2 phút → Chặn; hẹn giờ ≥ giờ máy chủ + 10 phút, ≤ 365 ngày; `date_gmt` đúng dạng `YYYY-MM-DDTHH:MM:SS` (UTC, không đuôi múi giờ); Đăng ngay không gửi ngày | Test: không `Date`, `Date` hỏng, lệch 3 phút, giờ đã qua, 9 phút, 400 ngày, `when_utc` không múi giờ → 0 request |
| LC-T094-25 | **Kiểm câu trả lời:** `id` khớp, `status` đúng chế độ, `future` thì `date_gmt` trả về đúng chuỗi đã gửi. Hẹn giờ mà nhận `publish` → câu báo khẩn cố định (bài đã công khai, cách chuyển về nháp theo `security.md` 7.2), **không** tự gửi lệnh nào vào bài đó. Lỗi không rõ (hết giờ, mất mạng, 5xx) → trạng thái «có thể đã hẹn giờ/đăng», khóa gửi lại, không tự thử lại | Test từng ca (W1) |
| LC-T094-26 | `post_statuses` chỉ đọc. Thêm `include` vào `ALLOWED_PARAMS` của **đúng** `GET /wp/v2/posts`, và **kiểm giá trị** (T-085 chỉ kiểm kiểu): `include` ≤ 100 số nguyên dương nối bằng dấu phẩy; `status` đúng hằng `draft,future,publish,pending,private`; `_fields` hằng, không `content`, `excerpt`. Mã bài lấy từ Sheet là dữ liệu chưa tin cậy: kết quả chỉ dùng để ghi ô trạng thái Sheet, không bao giờ dẫn tới lệnh ghi WordPress | Test `include` có chữ, số âm, 101 mã, `1,2;3` → 0 request (W3) |
| LC-T094-27 | `ConnectionInfo` thêm `timezone_string`, `gmt_offset` (dữ liệu website): kiểm kiểu, giới hạn độ dài, chỉ dùng để Cảnh báo, hiện chữ thuần. `schedule.py`: `ZoneInfo(settings.timezone_name)` (đã kiểm ở `load_settings`); nhãn «Thứ Ba, 03/11/2026 lúc 08:00» tính từ giờ người dùng chọn, không từ đồng hồ máy | Test múi giờ site lạ, `gmt_offset` sai kiểu |

### T-100 · Đồng bộ kế hoạch, cache, kho nháp

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-28 | **Ghi Sheet:** chỉ các cột app được ghi (thiết kế 2.4) của dòng tìm theo Mã bài; so từng ô với bản gốc ngay trước lệnh ghi (thiết kế 2.5); Mã bài trùng → không ghi; không xóa dòng, cột, không ghi cột lạ; mọi ô `RAW`; chữ bắt đầu bằng `=`, `+`, `-`, `@`, tab hay CR được thêm một dấu cách đầu (hoặc bỏ ký tự đó), để bản tải về CSV mở bằng Excel không thành công thức; giờ ghi vào Sheet là giờ Việt Nam ghi rõ (`+07:00` trong chữ hoặc tiêu đề cột), tính bằng `datetime.now(ZoneInfo(…))`, không dùng giờ không múi giờ | Test với Sheets giả: ô vừa bị sửa, Mã bài trùng, cột lạ, chữ `=IMPORTXML(…)` |
| LC-T094-29 | **Cache** `data/plan_cache.sqlite`: SQL chỉ tham số `?`; kiểm cấu trúc trước khi đọc (như T-074 kho thẻ); mỗi dòng đọc lại qua `PlanRow`, sai một dòng hay khác mã băm Sheet → bỏ cả cache; không lưu bí mật, không lưu mã Sheet gốc (chỉ mã băm); luôn đọc lại Sheet trước lệnh ghi và trước khi mở Soạn bài từ một dòng | Test cache sửa tay (F3) |
| LC-T094-30 | **Kho nháp:** `DraftSnapshot.plan`, `SendState` mở rộng (hình thức, giờ hẹn, đã chuyển / không rõ) tăng phiên bản cấu trúc, nháp cũ vẫn mở; giữ so-rồi-đặt của T-089. Việc ghi Sheet còn nợ lưu trong `drafts.sqlite`; thử lại **chỉ** ghi Sheet (không bao giờ gửi lại WordPress), vẫn kiểm xung đột | Test nháp cũ, việc còn nợ |
| LC-T094-31 | «Chuẩn bị trang tính» chỉ khi người dùng bấm; chỉ 4 loại yêu cầu trên đúng tab «KeHoach»; tiêu đề cột thiếu ghi vào **cuối** dòng 1 (không dời cột có sẵn); danh sách chọn là hằng của code | Test với Sheets giả có tab khác cùng tên gần giống |

### T-101 · Trang Kế hoạch, Cài đặt → Google, trang Bài viết

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-32 | LC-T094-3 cho mọi bảng (đề xuất trước/bây giờ/đề xuất, lý do, cảnh báo, danh sách bài); trang đích, link Sheet hiện chữ, không bấm được | AppTest (U1) |
| LC-T094-33 | Tải file: kiểm kích thước bằng code **trước khi** đọc (≤ 1 MB; không dựa vào `server.maxUploadSize`); chỉ `.csv`, `.tsv`, `.txt`, `.md` (câu 2 chọn A); không lưu file xuống đĩa | AppTest file 2 MB, `.xlsx`, `.exe` đổi đuôi |
| LC-T094-34 | Cài đặt → Google: chỉ hiện như LC-T094-12, LC-T094-15 (đã khai báo, tên file, email dịch vụ, tên Sheet); «Kiểm tra kết nối», «Chuẩn bị trang tính», «Áp dụng thay đổi» chỉ chạy khi bấm; «Bỏ» và dòng có cảnh báo không tick sẵn; trang mới có trong `PAGES`, qua cổng đăng nhập (U2) | AppTest |
| LC-T094-35 | Không có nút hẹn giờ hay đăng **hàng loạt** từ danh sách kế hoạch: «Viết bài» chỉ mở Soạn bài với chữ điền sẵn (đã qua `PlanRow`), không gửi gì lên WordPress | AppTest: bấm «Viết bài» → 0 request WordPress |

### T-102 · Bước Xuất bản thật

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-36 | Mọi hình thức (Nháp, Hẹn giờ, Đăng ngay) gửi đúng gói do bộ dựng T-096 trả; không đường nào khác ghép HTML hay gửi chữ chưa qua bộ dựng, kể cả chữ người dùng sửa tay; tải lại danh sách bài ngay trước `check_links`; còn dòng Chặn → nút khóa | AppTest: HTML tới client giả đúng bằng đầu ra bộ dựng (W3) |
| LC-T094-37 | Màn hình xác nhận bắt buộc với Hẹn giờ, Đăng ngay, đủ các phần thiết kế 3.5 (giờ Việt Nam kèm thứ, «Hiện công khai ngay khi bấm», mọi link, địa chỉ trần, ảnh + GPS, shortcode, SEO, kiểm tra); với Nháp ở dạng rút gọn nhưng **vẫn có bảng mọi link và địa chỉ trần** (nháp có thể được đăng sau trong trang quản trị mà không qua app). Ô tick và nút ghi rõ hành động; mọi chữ hiện thuần, link không bấm được | AppTest đủ dòng; grep `st.markdown` quanh dữ liệu xác nhận (U1) |
| LC-T094-38 | Ràng buộc xác nhận: mã băm LC-T094-8 tính lúc hiện màn hình, lưu cùng ô tick; lúc bấm dựng lại và so **ngay trước lệnh mạng đầu tiên**; khác → không gửi, bỏ tick, hiện lại. `release_draft` chỉ gọi sau khi tải ảnh, tạo nháp, ảnh đại diện, ghi SEO đã xong trong **cùng** lần bấm | AppTest: chưa tick; đổi chữ, ảnh, giờ, công tắc SEO sau khi xem → 0 request; thứ tự gọi đúng |
| LC-T094-39 | Khóa gửi trùng (T-086, T-089) phủ cả bước chuyển trạng thái: «đang gửi» giữ tới khi biết kết quả `release_draft`; kết quả không rõ → khóa, hướng dẫn kiểm trang quản trị, không tự gửi lại. Đăng ngay khi SEO chưa ghi lên website → Chặn; Hẹn giờ khi SEO chưa ghi → Cảnh báo | AppTest hai tab, lỗi hết giờ ở bước chuyển |
| LC-T094-40 | Cập nhật dòng kế hoạch sau khi gửi chỉ qua T-100 (4 ô, kiểm xung đột); lỗi ghi Sheet không làm gửi lại WordPress | AppTest |
| LC-T094-41 | Hẹn giờ và Đăng ngay có công tắc riêng trong Cài đặt, **mặc định tắt**, như công tắc ghi SEO của T-041; chỉ bật sau lượt thử thật (LC-T094-44) và Lá Chắn rà Giai đoạn 5. Công tắc tắt thì hai nút ẩn hoặc khóa, có câu nói rõ lý do | AppTest công tắc tắt → không có đường gọi `release_draft` |

### T-103 · Lời dặn đọc kế hoạch (Ngòi Bút)

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-42 | Giữ nguyên khung dữ liệu và `DATA_RULES`; lời dặn không xin AI trả URL, HTML hay link Markdown; `[tasks.plan]` không có `web_search` (code vẫn chặn, LC-T094-19); giá trị `[plan]` trong `config/content.toml` (giờ mặc định, nhãn) chỉ bổ sung, code kiểm (giờ `HH:MM`, nhãn thuộc danh sách của code) | Lá Chắn rút gọn (A1) |

### README (Thư Ký) và thử thật

| Mã | Điều kiện | Kiểm |
|---|---|---|
| LC-T094-43 | README: project Google riêng, chỉ bật Sheets API, service account **không có vai trò** nào; khóa lưu ngoài thư mục dự án và ngoài thư mục đồng bộ (Drive, OneDrive, USB ảnh), không gửi qua email, Zalo; chỉ chia sẻ **đúng một** Sheet cho email dịch vụ, Sheet **không** bật «Bất kỳ ai có đường liên kết»; lộ khóa: xóa khóa trong Google Cloud, tạo khóa mới, sửa `.env` hai máy (`security.md` 7.1); Mac/Linux `chmod 600`; WordPress múi giờ «Hồ Chí Minh», cron; tải Sheet về CSV mở bằng Excel cẩn thận công thức. `.env.example`: chú thích hai biến Google, ví dụ dùng tên bịa, không giá trị thật | Lá Chắn rút gọn (S1, S3) |
| LC-T094-44 | Thử thật: trên Sheet bản sao; không ghi Application Password, file khóa, mã Sheet đầy đủ, email dịch vụ vào báo cáo; hẹn giờ, đăng chỉ với bài chủ dự án duyệt; kiểm site trả header `Date` (không có thì app Chặn hẹn giờ, phải xử lý trước khi bật công tắc LC-T094-41); kiểm tài khoản Biên tập viên hẹn giờ được qua REST; xem bài hiển thị thật (không nhúng lạ, không link lạ do theme, plugin) | Chỉ Huy, chủ dự án; Lá Chắn đọc báo cáo thử |

**Số điều kiện theo phiếu:** chung 3 · T-096: 7 · T-097: 7 · T-098: 4 · T-099: 6 · T-100: 4 · T-101: 4 · T-102: 6 · T-103: 1 · README 1 · thử thật 1 = **44**.

## Chỗ thiếu hay rủi ro trong thiết kế (kèm cách sửa)

Không chỗ nào buộc thiết kế lại; mỗi chỗ đã có điều kiện sửa ở trên.

| # | Chỗ thiếu | Vì sao quan trọng | Sửa ở |
|---|---|---|---|
| 1 | Chưa nói cấm `google.auth.default()` | Hàm đó tự lấy tài khoản Google khác trên máy (`GOOGLE_APPLICATION_CREDENTIALS`, `gcloud`), app có thể chạy bằng quyền khác với file đã kiểm | LC-T094-14 |
| 2 | Ghi `GOOGLE_SHEET_ID` vào `.env` chưa có bộ kiểm riêng; chưa nói đường dẫn file khóa có ghi từ giao diện không | Bộ kiểm khóa AI hiện có cho `/ : + . ~`; một giá trị có xuống dòng sẽ chèn được biến khác vào `.env` (ví dụ `WORDPRESS_URL`) | LC-T094-15 |
| 3 | Kiểm vị trí file khóa chưa so đường dẫn thật, chưa xét thư mục ảnh, chưa nói quyền file | File trong thư mục Drive đồng bộ là khóa lên mây; symlink vòng qua phép so thư mục dự án | LC-T094-11 |
| 4 | Mã Sheet chưa được coi là thông tin cần giữ | Sheet lỡ bật «bất kỳ ai có link» thì ai có mã là sửa được kế hoạch, và qua đó đưa chữ vào lời dặn AI | LC-T094-15, -43 |
| 5 | Chưa xét công thức khi chủ dự án tải Sheet về CSV, mở bằng Excel | `RAW` giữ an toàn trong Google Sheets, nhưng Excel vẫn chạy chữ bắt đầu bằng `=`, `+`, `-`, `@` | LC-T094-28 |
| 6 | Chưa xét dữ liệu cá nhân khách trong ghi chú kế hoạch gửi AI (A3) | Ghi chú của thợ dễ có tên, số điện thoại khách | LC-T094-21 |
| 7 | Ký tự điều khiển hướng chữ chỉ được bỏ ở từ khóa | Chữ trong bảng duyệt có thể hiện đảo, đánh lừa người tick | LC-T094-3, -18 |
| 8 | Lệnh xin mã của `google-auth` chưa có timeout, chưa chặn chuyển hướng | Bản 2.62.0 mặc định đợi tới 120 giây (`google/auth/transport/requests.py:49`); theo chuyển hướng với lệnh có chữ ký | LC-T094-13 |
| 9 | Chưa kiểm nháp bị sửa giữa lúc tạo và lúc chuyển trạng thái | Nội dung lên công khai có thể khác nội dung đã xác nhận | LC-T094-23 (nên) |
| 10 | Mã băm xác nhận chưa nói cách chuẩn hóa và lúc so | Chuẩn hóa không xác định thì so sai; so muộn thì đã gửi một phần | LC-T094-8, -38 |
| 11 | Tham số `include` mới chưa kiểm giá trị | T-085 chỉ kiểm kiểu giá trị tham số; mã bài lấy từ Sheet do người sửa | LC-T094-26 |
| 12 | Chặn nhúng mới nói «đoạn chỉ có một địa chỉ» | WordPress còn nhúng địa chỉ đứng một mình trên một dòng (biểu thức thứ nhất), kể cả trong `<li>` | LC-T094-6 |
| 13 | Chưa có công tắc bật Hẹn giờ, Đăng ngay | Không có website thử; công tắc mặc định tắt cho tới khi thử thật, như ghi SEO ở T-041 | LC-T094-41, -44 |

## Câu hỏi cho chủ dự án: nhận xét bảo mật về lựa chọn A của Chỉ Huy

| Câu | Lá Chắn |
|---|---|
| 1A (`google-auth`) | Không phản đối: gói đã có trong môi trường, `pip-audit` sạch, không thêm gói; làm theo LC-T094-14, -16. Theo R6 đây vẫn là thêm thư viện: nếu sáng 28/10 chủ dự án đổi sang B thì T-097 đổi hướng, nên gộp T-097 sau khi chủ dự án đã xem câu 1 |
| 2A (chỉ CSV, chữ) | Đồng ý: bớt một thư viện đọc file nhị phân |
| 3A (tab «KeHoach») | Không ảnh hưởng bảo mật |
| 4A (app tự ghi 4 ô trạng thái) | Đồng ý với LC-T094-28 (chỉ 4 ô, kiểm xung đột) |
| 5A (không hẹn giờ, đăng nháp có từ trước) | **Đồng ý mạnh**: không có đường ghi vào bài đã nằm trên website (R3) |
| 6A (chưa cập nhật bài cũ) | **Đồng ý mạnh**: sửa bài đã đăng cần thiết kế, duyệt riêng |

## Phiếu nào chạy trước được

| Đợt | Phiếu | Ghi chú bảo mật |
|---|---|---|
| 1 (ngay) | **T-096**, **T-098** | Không bí mật mới, không đường gọi mạng mới. Lá Chắn đầy đủ cho cả hai |
| 1 (ngay) | **T-097** | Bí mật mới (file khóa): Lá Chắn đầy đủ; gộp sau khi chủ dự án xem câu 1 |
| 1 (khi T-091 gộp) | **T-099** | Cùng `client.py`; soát kỹ nhất (đường tới `future`/`publish`) |
| 2 | T-100 (sau T-097, T-098), T-103 (sau T-098) | |
| 3 | T-101, T-102 | T-102 bật được Hẹn giờ, Đăng ngay chỉ qua công tắc mặc định tắt (LC-T094-41) |
| 4 | README, thử thật, Lá Chắn rà Giai đoạn 5 | Công tắc LC-T094-41 chỉ bật sau mục này |

## Ghi nhận (không xếp lỗi)

1. **Biến môi trường proxy, chứng chỉ** (`HTTPS_PROXY`, `REQUESTS_CA_BUNDLE`) cũng có tác dụng với lệnh gọi Google qua `requests` (như WordPress: «không mới» ở T-042, T-075). Dòng sổ rủi ro 2026-10-15 hiện chỉ ghi thư viện AI; đề nghị Chỉ Huy hỏi chủ dự án ghi rõ dòng đó áp cả cho `requests` (WordPress, Google). Muốn khai thác phải chiếm máy trước; Thấp.
2. **Khe «hai máy ghi cùng một ô trong 1–2 giây»** (thiết kế 2.5): không phải rủi ro bảo mật (không lộ gì, không đụng website; tệ nhất một ô Sheet mang giá trị cũ), không cần ghi sổ rủi ro; ghi trong báo cáo T-100 là đủ.
3. Hiện email dịch vụ ở trang Cài đặt: đồng ý (không phải bí mật, cần để chia sẻ Sheet); không đưa vào câu báo, log, báo cáo.
4. Đề xuất của Thợ Máy thêm mẫu `"type": "service_account"` vào bước quét bí mật: đồng ý làm thêm ở mỗi lượt Lá Chắn có file JSON mới (detect-secrets đã bắt «Private Key» trong nội dung).

## Điều kiện

Chép LC-T094-1 → -44 vào các phiếu T-096 → T-103, phiếu README và lượt thử thật theo bảng trên (Chỉ Huy). Lá Chắn của từng phiếu kiểm đúng các dòng đó.

**Kết luận:** phiếu T-094 (tài liệu) **ĐẠT**. Thiết kế Giai đoạn 5 **đủ để mở phiếu code** khi kèm 44 điều kiện; chạy trước được T-096, T-098, T-097, rồi T-099 sau T-091.

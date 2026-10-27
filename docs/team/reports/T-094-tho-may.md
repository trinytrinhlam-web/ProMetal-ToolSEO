# Báo cáo T-094 · Thiết kế Giai đoạn 5: kế hoạch, lịch, hẹn giờ và đăng bài

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-094](../tickets/T-094-thiet-ke-giai-doan-5.md) |
| Ngày nộp | 2026-10-27 20:21 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành (phiếu thiết kế, không sửa code) |

## Tóm tắt (cho chủ dự án)

- **Kế hoạch nằm trên Google Sheets**, trong một trang tính tên «KeHoach» có cột cố định (mã bài, từ khóa, ý định, loại trang, ngày dự kiến, trạng thái…). Hai máy cùng đọc, cùng ghi vào đó; máy chỉ giữ bản tạm. Chủ dự án vẫn sửa tay được trên Google Sheets như bình thường.
- **Đưa kế hoạch vào app bằng 3 cách** như giao diện demo đã duyệt: tải file, dán chữ (kể cả chép một vùng ô từ Excel), dán link Google Sheets. App so với kế hoạch đang có, đưa ra **danh sách thay đổi kèm lý do** (thêm bài, đổi ngày, bỏ bài…); chủ dự án tick dòng nào thì app mới ghi dòng đó. Chữ tự do (ghi chú định hướng) do AI đọc; bảng có cột rõ ràng thì code tự đọc, không cần AI.
- **Từ một dòng kế hoạch bấm «Viết bài»**: trang Soạn bài mở sẵn từ khóa, ghi chú của thợ, slug, trang dịch vụ phải link tới và ngày giờ dự kiến. Gửi lên WordPress xong, dòng đó tự đổi trạng thái («Đã gửi nháp», «Đã hẹn giờ», «Đã đăng») và ghi mã bài.
- **Hẹn giờ và Đăng ngay**: app luôn tạo **nháp trước** (ảnh, SEO đầy đủ), rồi mới chuyển sang hẹn giờ hoặc đăng, qua **đúng một chỗ trong code**, sau **màn hình xác nhận** liệt kê mọi link, ảnh còn vị trí GPS, tiêu đề và mô tả SEO, giờ đăng theo giờ Việt Nam kèm thứ trong tuần. Có lỗi giữa chừng thì bài vẫn chỉ là nháp. App không bao giờ sửa bài đã đăng.
- Đã tìm ra hai điều WordPress làm mà phải chặn trước: (1) hẹn giờ vào một thời điểm **đã qua** (hoặc chưa tới 1 phút) thì WordPress **đăng ngay**; (2) một đoạn văn chỉ có một địa chỉ web thì WordPress **tự nhúng** trang đó vào bài. App chặn cả hai.
- **Không cần cài thư viện mới**: thư viện xác thực Google (`google-auth`) **đã có sẵn trong máy** vì thư viện Gemini dùng nó; chỉ cần chủ dự án đồng ý khai báo nó là thư viện của app (câu hỏi 1). Đọc file Excel trực tiếp thì cần thêm thư viện, có cách không cần (câu hỏi 2).
- Đề xuất **8 phiếu** (T-096 → T-103) cộng README và một lượt thử thật; 3–4 phiếu đầu chạy song song được. **6 câu hỏi** ở cuối báo cáo, mỗi câu có khuyến nghị.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-094-tho-may.md` | Báo cáo này (file duy nhất). Không sửa code, cấu hình, test |

## Nguồn đã dùng

**Code trong repo** (nhánh `team/T-094` = `main` lúc `10c7933`), dẫn `file:dòng`:

| Chỗ | Điều rút ra |
|---|---|
| `seo_app/wordpress/client.py:69-83` (`ALLOWED_ROUTES`), `:141-143`, `:155`, `:219-221` | Đường gọi cố định; thân JSON `POST /wp/v2/posts` chỉ nhận `status = "draft"`; phiếu mở đường đăng phải sửa đúng chỗ này |
| `client.py:710` (`_created_post_ids`), `:896-937` (`create_draft`), `:939-980` (`set_seo_meta`), `:1226-1355` (`create_draft_with_images`) | Chỉ bài **chính client này** vừa tạo mới được ghi tiếp (ảnh đại diện, SEO), site phải xác nhận còn nháp (`_own_draft`) |
| `app/views/write.py:2490-2492` (`sent_text`), `:2511-2527` (`article_parts`), `:2748` | Thân bài hiện gửi dạng đoạn văn thường (`paragraphs_to_html`), **chưa** chuyển Markdown, **chưa** chèn link nội bộ, **chưa** gửi slug, chuyên mục |
| `app/views/write.py:3086-3134` (`step_publish`) | «Hẹn giờ», «Đăng ngay» còn demo (`:3122`) |
| `app/views/plan.py`, `seo_app/demo.py` (`PLAN_ROWS`, `PLAN_CHANGES`, `PLAN_PASTE_EXAMPLE`), `app/views/home.py` | Bố cục trang Kế hoạch và trang Bài viết đã duyệt (giữ nguyên khi làm thật) |
| `seo_app/onpage/links.py:502` (`markdown_blocks`), `:940` (`apply_links`), `:1157` (`check_links`) | Đã có chèn link do code và kiểm mọi `href`; chờ bộ chuyển Markdown → HTML |
| `seo_app/storage/drafts.py:536-560`, `:647-666` (`SendState`) | Nháp lưu trên máy; trạng thái gửi có so-rồi-đặt (T-089) |
| `seo_app/config.py:23-36`, `.env.example` | Đã có sẵn biến `GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_SHEET_ID`; không cần biến mới |
| `seo_app/content/prompts.py:133`, `:153` | Từ khóa đặt **ngoài** khung dữ liệu, chưa vô hiệu thẻ khung: SL-7, test `xfail` ở `tests/test_soi_loi_t003_t009.py:209-213` |
| `uv.lock:406-412`, `:424-438` | `google-auth` 2.62.0 (kéo `cryptography` 50.0.2, `pyasn1-modules`) **đã cài** vì `google-genai` cần `google-auth[requests]` |
| `.gitignore:5` | Chỉ chặn file khóa tên có chữ `service-account` |

**Mã nguồn WordPress 6.9** (`github.com/WordPress/wordpress-develop`, nhánh `6.9`), chỉ đọc:

| File | Điều rút ra |
|---|---|
| `wp-includes/post.php`, hàm `wp_insert_post` | So `post_date_gmt` với giờ UTC của máy chủ, ngưỡng `MINUTE_IN_SECONDS`: `publish` có ngày ≥ 60 giây sau → thành `future`; **`future` có ngày < 60 giây sau (kể cả ngày đã qua) → thành `publish` ngay**. Nháp, chờ duyệt có "ngày trôi" (`0000-00-00 00:00:00`) |
| cùng file, `check_and_publish_future_post` | Cron của WordPress tới giờ thì đăng; cron chạy trễ (site ít khách) thì bài lên trễ, đăng ở lần cron sau |
| `rest-api/endpoints/class-wp-rest-posts-controller.php` | `date_gmt` đọc bằng `rest_get_date_with_gmt(…, true)`, đặt cả `post_date` lẫn `post_date_gmt`; `handle_status_param`: `publish`, `future` cần quyền `publish_posts` (Biên tập viên có, thử thật T-059) |
| `rest-api/class-wp-rest-server.php`, `get_index` | `GET /wp-json/` trả `timezone_string`, `gmt_offset` của site |
| `class-wp-embed.php`, `autoembed` (gắn vào `the_content` mức 8) | Địa chỉ `https://…` **đứng một mình trên một dòng hoặc một mình trong `<p>`** bị nhúng (oEmbed) khi hiển thị; địa chỉ giữa câu thì không |

**Tài liệu Google** (chỉ đọc web công khai): phạm vi quyền Sheets API (`developers.google.com/workspace/sheets/api/scopes`), giới hạn dùng (`…/sheets/api/limits`: 60 lệnh đọc và 60 lệnh ghi mỗi phút cho mỗi người dùng; quá thì lỗi 429; nên lùi thời gian theo cấp số nhân; mỗi lệnh ghi áp dụng trọn hoặc không gì cả). Mã nguồn `google-auth` (`google/oauth2/service_account.py`): `token_uri` lấy **nguyên văn từ file JSON, không kiểm**; không kiểm `type == "service_account"`.

**Không** gọi website thật, không gọi Google thật, không đọc `.env`.

---

## 1. Luồng người dùng: từ kế hoạch tới bài đăng (yêu cầu 1)

### 1.1 Toàn cảnh

```
 [Tải file] [Dán chữ] [Link Google Sheets]          (trang Kế hoạch, bố cục demo đã duyệt)
        │
        ▼
 Chuẩn hóa thành danh sách bài (PlanRow)  ── bảng có cột: code đọc · chữ tự do: AI đọc
        │
        ▼
 So với kế hoạch hiện tại trên Sheets  ──►  Đề xuất: Thêm / Cập nhật / Bỏ, mỗi dòng có lý do,
        │                                    cảnh báo (trùng bài đã đăng, ngày đã qua…)
        ▼
 Chủ dự án tick → «Áp dụng»  ──►  ghi Google Sheets (kiểm xung đột từng ô, mục 2.5)
        │
        ▼
 Danh sách bài theo kế hoạch  ──  nút «Viết bài» trên từng dòng
        │
        ▼
 Soạn bài (bước 1–4 như hiện nay, điền sẵn từ dòng kế hoạch)
        │
        ▼
 Bước 5 «Xuất bản»: Nháp / Hẹn giờ / Đăng ngay ──► màn hình xác nhận ──► WordPress
        │
        ▼
 Dòng kế hoạch tự cập nhật: trạng thái, mã bài WordPress, ngày đăng (mục 1.7)
```

### 1.2 Nhận kế hoạch (3 cách)

| Cách | Đọc thế nào | Giới hạn |
|---|---|---|
| **Tải file** | `.csv`, `.tsv`, `.txt`, `.md`: thư viện chuẩn (`csv`, đọc chữ). Mã chữ: `utf-8`, `utf-8-sig` (CSV của Excel «CSV UTF-8»); không đọc được thì báo, gợi ý lưu lại bằng «CSV UTF-8», **không đoán** bảng mã khác. `.xlsx`: xem câu hỏi 2. `.docx`, `.pdf`: không đọc trực tiếp; mở file, chép chữ, dán vào ô «Dán nội dung» | ≤ 1 MB, ≤ 1.000 dòng, mỗi ô ≤ 2.000 ký tự |
| **Dán chữ** | Có dấu tab trên đa số dòng (chép một vùng ô từ Excel hay Google Sheets) → đọc như bảng. Không thì là chữ tự do (ghi chú định hướng như mẫu demo) → AI đọc | ≤ 20.000 ký tự |
| **Link Google Sheets** | Chỉ nhận dạng `https://docs.google.com/spreadsheets/d/<mã>/…`; app lấy `<mã>`, **không bao giờ mở địa chỉ khác**. Trùng Sheet kế hoạch chính → chỉ tải lại. Sheet khác (phải chia sẻ cho tài khoản dịch vụ) → đọc **một lần** như file nguồn, đề xuất ghi vào Sheet chính | Như tải file |

Bảng có dòng tiêu đề thì code ghép cột theo **tên cột** (danh sách tên đồng nghĩa: «Từ khóa», «Từ khóa chính», «keyword»; «Ngày», «Ngày đăng», «Ngày dự kiến», «Phát hành»…). Không nhận ra cột từ khóa → coi như chữ tự do, đưa AI.

### 1.3 Chuẩn hóa thành danh sách bài

Một kiểu dữ liệu chung `PlanRow` (pydantic, `extra="forbid"`), dùng cho mọi nguồn và cho cache:

| Trường | Nội dung | Kiểm |
|---|---|---|
| `key` (Mã bài) | `B-001`… (yêu cầu phần mềm 3.1). Dòng mới chưa có mã thì app cấp số kế tiếp | `[A-Z]{1,3}-[0-9]{1,5}`; trùng mã trong Sheet → báo, không ghi dòng đó |
| `keyword` (Từ khóa chính) | **bắt buộc** | NFC, một dòng, 2–120 ký tự, bỏ ký tự điều khiển, ký tự vô hình; «» đổi thành ‹› (như tiêu đề mục ở `rewrite_prompt`) |
| `secondary` (Từ khóa phụ, ý cần có) | | ≤ 500 ký tự |
| `intent` (Ý định) | Tìm hiểu / So sánh trước khi mua / Mua hàng (đúng 3 nhãn của demo) hoặc trống | danh sách cố định; Ngòi Bút có thể chỉnh nhãn ở T-103 |
| `kind` (Loại trang) | Hướng dẫn / Dịch vụ / Khu vực / Công trình thực tế / Cập nhật bài cũ | ánh xạ sang `ArticleKind` của `links.py` (quy tắc link YC-602); «Cập nhật bài cũ» chưa viết được (mục 8, câu hỏi 6) |
| `priority` (Ưu tiên) | Cao / Trung bình / Thấp | |
| `planned_date`, `planned_time` | Ngày dự kiến; giờ đăng (trống = giờ mặc định trong cấu hình, đề xuất 08:00) | ngày: số ngày kiểu Sheets, `dd/mm/yyyy`, `yyyy-mm-dd`; **không** nhận `mm/dd` |
| `status` (Trạng thái) | Chưa viết / Đang viết / Đã gửi nháp / Đã hẹn giờ / Đã đăng / Bỏ | danh sách cố định |
| `title_hint`, `slug`, `target_url`, `notes` | Tiêu đề dự kiến; slug; trang dịch vụ đích; ghi chú của thợ | slug chỉ `a-z0-9-`; `target_url` phải là link của chính site **và** có trong danh sách bài đã đăng (`is_site_link` + `SiteIndex`), app chỉ giữ **mã bài**, không giữ địa chỉ |
| `wp_post_id`, `published_at`, `updated_at` | Mã bài WordPress, ngày đăng thực tế (hoặc giờ hẹn), lúc app cập nhật | app ghi |

Chỉ «Từ khóa chính» là bắt buộc để bấm «Viết bài». Thiếu loại trang, trang đích, ngày… thì Cảnh báo, không chặn (chặt hơn yêu cầu YC-101 sẽ làm khó dùng; đổi được sau).

### 1.4 Đề xuất thay đổi kèm lý do

Hai nguồn đề xuất, cùng một khuôn `Proposal(action, key, before, after, reason, warnings)`:

1. **Code so bảng** (file/bảng/Sheet khác): khớp theo Mã bài, không có mã thì theo từ khóa đã chuẩn hóa (chữ thường, bỏ dấu, gộp khoảng trắng). Mới → «Thêm»; khác trường → «Cập nhật» (lý do do code viết: «Ngày dự kiến 15/11 → 20/11 theo file»). Bảng **không bao giờ** sinh «Bỏ», trừ khi dòng ghi Trạng thái «Bỏ».
2. **AI đọc chữ tự do**: việc mới `plan` (`[tasks.plan]` trong `config/ai.toml`, **không** `web_search`). Lời dặn chứa kế hoạch hiện tại (mã bài + từ khóa + ngày + trạng thái) và chữ người dùng dán, **mỗi thứ một khung dữ liệu** (`<ke_hoach_hien_tai>`, `<ke_hoach_moi>`, thêm vào `DATA_TAGS`), kèm `DATA_RULES`. AI trả `PlanSuggestions` (≤ 100 mục): `{action, key?, keyword?, fields…, reason}`. Code kiểm từng mục, sai là **bỏ** (đếm số bị bỏ, không chép chữ AI vào câu báo): `key` phải có thật; nhãn thuộc danh sách; ngày đọc được; từ khóa qua bộ làm sạch 1.3; `reason` là chữ thường ≤ 300 ký tự; «Bỏ» phải có lý do.

Code kiểm thêm cho **mọi** đề xuất (chỉ thêm cảnh báo, không tự sửa):

| Kiểm | Mức |
|---|---|
| Từ khóa trùng một dòng khác trong kế hoạch | Cảnh báo |
| Trùng bài **đã đăng** trên site (tiêu đề, slug trong `SiteIndex`, như kiểm trùng T-036): hai trang nhắm một từ khóa (N5) | Cảnh báo, gợi ý «Cập nhật bài cũ» |
| Ngày dự kiến đã qua | Cảnh báo |
| Dòng đã «Đã hẹn giờ» / «Đã đăng» mà đề xuất đổi ngày hay «Bỏ» | Cảnh báo: đổi ở đây **không** đổi lịch trên website |
| ≥ 3 từ khóa chỉ khác nhau tên quận, phường (khuôn chung thay địa danh) | Cảnh báo «nguy cơ trang cửa ngõ» (`review_ke_hoach_v1.md` L5; quy tắc 1: không sản xuất bài hàng loạt) |

Tick mặc định: «Thêm», «Cập nhật» không có cảnh báo thì tick sẵn (như demo); «Bỏ» và dòng có cảnh báo thì **không** tick sẵn.

### 1.5 Duyệt và ghi Google Sheets

Bấm «Áp dụng thay đổi» (nút demo đã có): app đọc lại Sheet, kiểm xung đột (mục 2.5), ghi **một** lệnh cho mọi ô sửa (Sheets áp dụng trọn hoặc không gì cả), dòng mới bằng lệnh thêm dòng. Kết quả: «Đã ghi 5 thay đổi. 1 dòng vừa bị sửa ở nơi khác nên chưa ghi: B-012 (Ngày dự kiến)», kèm nút «Đề xuất lại trên bản mới». App **không bao giờ xóa dòng**: «Bỏ» chỉ đổi Trạng thái thành «Bỏ».

### 1.6 Từ một dòng kế hoạch mở Soạn bài

Nút «Viết bài» trên dòng (trang Kế hoạch, mục «Tiếp theo trong kế hoạch» ở trang Bài viết, ô «Từ kế hoạch» của «Viết bài mới»):

1. Đọc lại đúng dòng đó từ Sheets (lấy bản mới nhất).
2. Đã có nháp trên máy gắn với mã bài này → mở nháp đó, không tạo nháp thứ hai.
3. Không thì tạo nháp mới, ghi `DraftSnapshot.plan = DraftPlanRef(key, sheet_hash, …)` và điền sẵn:

| Từ dòng | Vào Soạn bài |
|---|---|
| Từ khóa chính | ô từ khóa bước 1 |
| Ghi chú của thợ | «Kinh nghiệm của xưởng» (chất liệu thật) |
| Tiêu đề dự kiến | gợi ý tiêu đề dàn ý |
| Slug | slug bước SEO (slug của phiếu thắng slug tự sinh, T-033 mục 5.2) |
| Trang dịch vụ đích | link **bắt buộc** (`required` của `select_candidates`, `required_ids` của `check_links`) |
| Loại trang | `ArticleKind` cho quy tắc chọn link |
| Ngày, giờ dự kiến | ô Ngày, Giờ của «Hẹn giờ» |

4. Trạng thái dòng → «Đang viết» (tự ghi hay hỏi: câu hỏi 4).

### 1.7 Sau khi gửi WordPress

- Gửi xong (nháp, hẹn giờ hay đăng): ghi vào dòng **chỉ 4 ô** Trạng thái, Mã bài WordPress, Ngày đăng thực tế (giờ hẹn hoặc giờ đăng), Cập nhật lúc; kiểm xung đột như 2.5.
- Ghi Sheets lỗi (mất mạng): WordPress đã xong nên **không** gửi lại bài. Việc ghi Sheets còn nợ lưu trong kho nháp trên máy, thử lại khi mở trang Kế hoạch/Bài viết, có nút «Thử ghi lại».
- **Đồng bộ từ WordPress** (nút «Cập nhật trạng thái từ website», tự chạy khi mở trang Kế hoạch nếu lần trước đã quá 30 phút): với các dòng có Mã bài WordPress, hỏi website trạng thái (chỉ đọc, mục 3.3) rồi đổi «Đã hẹn giờ» → «Đã đăng» khi bài đã lên. Bài `future` đã quá giờ hẹn 15 phút → nhãn «**Lỡ lịch**» kèm hướng dẫn (cron của WordPress chạy trễ; mục 3.1). Bài bị xóa, về nháp trên website → Cảnh báo, không tự sửa Sheet.
- Bài chủ dự án tự hẹn giờ trong trang quản trị WordPress (câu hỏi 5, lựa chọn A) cũng được nhận ra ở bước đồng bộ này.

### 1.8 Trang Bài viết (giữ bố cục demo)

«Tiếp theo trong kế hoạch»: 3 dòng «Chưa viết» gần nhất từ cache kế hoạch. «Đã gửi WordPress»: các bài app đã gửi (mã bài lấy từ kho nháp và cột Mã bài WordPress), trạng thái hỏi website. Xóa dữ liệu mẫu `SENT_TO_WORDPRESS`, `plan_rows` khỏi `seo_app/demo.py`.

---

## 2. Google Sheets (yêu cầu 2)

### 2.1 Tài khoản dịch vụ (service account), quyền tối thiểu

Việc chủ dự án làm một lần (README hướng dẫn từng bước, phiếu Thư Ký):

1. Google Cloud: tạo một project riêng cho app, bật **Google Sheets API** (chỉ API này; Search Console bật ở Giai đoạn 6).
2. Tạo service account, **không cấp vai trò (role) nào** trong project: đọc/ghi Sheet chỉ cần Sheet được chia sẻ cho nó.
3. Tạo khóa JSON, lưu **ngoài thư mục dự án và ngoài thư mục đồng bộ** (không để trong Google Drive for Desktop, USB ảnh), ghi đường dẫn vào `GOOGLE_SERVICE_ACCOUNT_FILE`. Máy thứ hai: chép file bằng USB, không gửi qua email, Zalo.
4. Mở Sheet kế hoạch → «Chia sẻ» → dán địa chỉ email của service account, quyền **Người chỉnh sửa**. Chỉ chia sẻ đúng Sheet này.
5. Dán link Sheet vào Cài đặt (app lấy mã, ghi `GOOGLE_SHEET_ID`; mục 6, T-097).

Ghi chú (theo tài liệu Google, **chưa xác minh** với tài khoản của chủ dự án): tổ chức Google Workspace tạo từ 05/2024 có thể bị **chặn tạo khóa service account** theo mặc định (chính sách `iam.disableServiceAccountKeyCreation`); khi đó phải tắt chính sách cho project này, hoặc dùng tài khoản Gmail cá nhân để tạo project.

**Phạm vi quyền (scope):** `https://www.googleapis.com/auth/spreadsheets`. Phạm vi `drive.file` hẹp hơn nhưng chỉ áp cho file app tự tạo/mở qua bộ chọn file, không dùng được với Sheet chia sẻ cho service account (suy luận từ mô tả của Google, không thử). Bảo vệ thật là **chỉ chia sẻ một Sheet**: service account không thấy file nào khác.

**Kiểm file khóa trước khi dùng** (`seo_app/google/service_account.py`), sai thì câu báo cố định, không chép nội dung file:

| Kiểm | Vì sao |
|---|---|
| File thường, ≤ 64 KB, không phải liên kết tắt | File lạ, file lớn bất thường |
| **Không nằm trong thư mục dự án** | `.gitignore` chỉ chặn tên có `service-account`; file Google tải về tên kiểu `ten-project-1a2b3c.json` sẽ lọt vào git |
| JSON là object, `type == "service_account"`, có `client_email` (đuôi `.iam.gserviceaccount.com`), `private_key` dạng PEM | `google-auth` không kiểm `type` |
| `token_uri` **đúng** `https://oauth2.googleapis.com/token`; `universe_domain` trống hoặc `googleapis.com` | `google-auth` gửi lệnh xin mã tới `token_uri` lấy nguyên văn từ file |

Mã truy cập (access token) chỉ nằm trong bộ nhớ, không ghi đĩa. `repr` của đối tượng không có khóa. Giao diện chỉ hiện «đã khai báo / chưa khai báo» và **địa chỉ email** của service account (cần để chia sẻ Sheet; không phải bí mật, Lá Chắn xét lại).

### 2.2 Có cần thư viện mới không

Ký JWT của service account cần thuật toán RSA, thư viện chuẩn của Python không có. Các cách:

| Cách | Thư viện | Đánh giá |
|---|---|---|
| **A. `google-auth`** (chính hãng Google, Apache-2.0) + gọi REST Sheets v4 bằng `requests` (đã có), qua `google.auth.transport.requests.AuthorizedSession` | `google-auth` **đã cài sẵn** (2.62.0, `uv.lock:406`) vì `google-genai` cần. Chỉ thêm một dòng `pyproject.toml`, `uv.lock` không thêm gói nào | **Khuyến nghị**. Không tăng bề mặt tấn công: gói đã nằm trong môi trường mà `pip-audit` của Lá Chắn quét (suy luận: lệnh quét đọc cả môi trường); T-097 vẫn quét lại |
| B. `gspread` hoặc `google-api-python-client` | Gói mới (và phụ thuộc của chúng) | Không cần: app chỉ gọi 5 đường REST (2.3) |
| C. Tự ký JWT bằng `cryptography` (cũng đã có sẵn) | Không thêm dòng nào | Tự viết phần xác thực là việc dễ sai; vẫn phụ thuộc gói có sẵn y như A |
| D. Không dùng API: xuất CSV cho chủ dự án tự dán vào Sheet, nhập lại bằng file | Không | Hai máy không tự đồng bộ, trái quyết định đã chốt «kế hoạch trên Google Sheets» |

Thêm khai báo vẫn là «thêm thư viện» theo R6 (như tiền lệ `pydantic`, `pillow`): **câu hỏi 1**.

### 2.3 Đường gọi cố định của client Sheets

Giống client WordPress (`ALLOWED_ROUTES`): danh sách cố định, so khớp toàn chuỗi trước khi gửi, mọi đường khác bị từ chối.

| Lệnh | Dùng khi | Ràng buộc |
|---|---|---|
| `GET /v4/spreadsheets/{id}?fields=properties(title,locale,timeZone),sheets.properties(sheetId,title)` | Kiểm kết nối, có tab «KeHoach» chưa | `fields` cố định |
| `GET /v4/spreadsheets/{id}/values/'KeHoach'!A1:Z1001` | Đọc cả kế hoạch (1 lệnh) | `valueRenderOption=UNFORMATTED_VALUE`, `dateTimeRenderOption=SERIAL_NUMBER` (ngày ra số, không phụ thuộc định dạng vùng của Sheet) |
| `POST /v4/spreadsheets/{id}/values:batchUpdate` | Ghi các ô đã duyệt, các ô trạng thái | **`valueInputOption=RAW` luôn luôn**: chữ bắt đầu bằng `=` không thành công thức (chặn chèn công thức kiểu `=IMPORTXML("https://…"&A1)` gửi dữ liệu ra ngoài) |
| `POST /v4/spreadsheets/{id}/values/'KeHoach'!A1:P1:append` | Thêm dòng mới | `RAW`, `insertDataOption=INSERT_ROWS` (hai máy cùng thêm không đè nhau) |
| `POST /v4/spreadsheets/{id}:batchUpdate` | **Chỉ** nút «Chuẩn bị trang tính» trong Cài đặt | Loại yêu cầu cho phép: `addSheet`, `updateSheetProperties` (cố định dòng tiêu đề), `repeatCell` (định dạng ngày), `setDataValidation` (danh sách chọn). Không bao giờ `deleteSheet`, `deleteDimension`… |

Ràng buộc chung: chỉ `https://sheets.googleapis.com`; `id` khớp `[A-Za-z0-9_-]{25,100}`; tên tab và vùng ô do code dựng; mọi lệnh có timeout (30 giây); không đi theo chuyển hướng; câu trả lời > 2 MB thì bỏ; lỗi thành câu cố định theo mã HTTP (403: «Sheet chưa chia sẻ cho tài khoản dịch vụ», 404, 429, 5xx), không chép lời máy chủ. Lỗi 429: lệnh **đọc** thử lại tối đa 3 lần (1, 2, 4 giây + ngẫu nhiên); lệnh ghi ô (`values:batchUpdate`, ghi cùng giá trị vào cùng ô nên lặp lại không sao) thử lại 1 lần; lệnh **thêm dòng không bao giờ tự thử lại** (lặp lại là thêm trùng): hết giờ thì đọc lại, xem mã bài đã có chưa.

Biến môi trường proxy (`HTTPS_PROXY`…) vẫn có tác dụng như với WordPress và AI (đã ghi sổ rủi ro 2026-10-15).

### 2.4 Cấu trúc trang tính đề xuất

Một tab tên **«KeHoach»** (câu hỏi 3) trong Sheet chủ dự án chỉ định. Dòng 1 là tiêu đề cột, app tìm cột **theo tên** (đổi thứ tự cột, thêm cột riêng đều được; cột lạ app bỏ qua và không bao giờ ghi).

| Cột | Tiêu đề | Ai ghi | Ghi chú |
|---|---|---|---|
| A | Mã bài | người / app (dòng mới) | khóa của dòng |
| B | Từ khóa chính | người / đề xuất đã duyệt | bắt buộc |
| C | Từ khóa phụ, ý cần có | như trên | |
| D | Ý định | như trên | danh sách chọn |
| E | Loại trang | như trên | danh sách chọn |
| F | Ưu tiên | như trên | danh sách chọn |
| G | Ngày dự kiến | như trên | ô ngày (định dạng `dd/mm/yyyy`) |
| H | Giờ đăng | như trên | chữ `HH:MM`, giờ Việt Nam |
| I | Trạng thái | người / đề xuất / **app sau khi gửi** | danh sách chọn |
| J | Tiêu đề dự kiến | người / đề xuất | |
| K | Slug | như trên | |
| L | Trang dịch vụ đích | như trên | link một trang trên website |
| M | Ghi chú của thợ | như trên | |
| N | Mã bài WordPress | **app** | |
| O | Ngày đăng thực tế | **app** | giờ hẹn hoặc giờ đăng, giờ Việt Nam |
| P | Cập nhật lúc | **app** | kèm `+07:00` |

Nút «Chuẩn bị trang tính» (Cài đặt → Google): tạo tab nếu chưa có, ghi dòng tiêu đề, cố định dòng 1, định dạng cột ngày, danh sách chọn cho D, E, F, I. Tab đã có mà thiếu cột → báo thiếu cột nào, nút «Thêm cột còn thiếu» ghi tiêu đề vào **cuối** dòng 1 (không dời cột có sẵn). Ngày ghi dạng số ngày của Sheets (`RAW`), nên vẫn là ô ngày thật, sắp xếp đúng.

Dữ liệu đọc từ Sheet là **chưa tin cậy** (mục 5): ≤ 1.000 dòng, ≤ 26 cột, mỗi ô ≤ 2.000 ký tự (dài hơn thì cắt và Cảnh báo), mọi dòng qua `PlanRow`.

### 2.5 Hai máy cùng sửa: xử lý xung đột

Sheets API **không có** lệnh ghi có điều kiện (kiểu «chỉ ghi nếu chưa ai sửa»). Cách làm (so rồi ghi theo từng ô):

1. Khi bắt đầu duyệt đề xuất, app giữ **bản gốc** của từng dòng liên quan (giá trị lúc đọc).
2. Bấm «Áp dụng»: đọc lại cả tab (1 lệnh), tìm dòng theo **Mã bài** (không theo số dòng: người dùng có thể sắp xếp, chèn dòng).
3. Với mỗi thay đổi: so **các ô sắp ghi** và ô Mã bài, Từ khóa với bản gốc. Khác (máy kia vừa ghi, hay chủ dự án vừa sửa tay trên Google Sheets) → **không ghi** dòng đó, hiện «trước / bây giờ / đề xuất» để chủ dự án quyết. Mã bài xuất hiện hai lần → không ghi.
4. Ghi các thay đổi còn lại trong **một** lệnh `values:batchUpdate` (trọn hoặc không). Chỉ ghi đúng các ô đổi, không ghi cả dòng: hai máy sửa hai cột khác nhau của cùng dòng không đè nhau.

Khe hở còn lại: hai máy ghi **cùng một ô** trong khoảng 1–2 giây giữa bước 2 và 4 thì bản ghi sau thắng. Chủ dự án dùng hai máy luân phiên (máy công ty, máy nhà) nên rất hiếm; xếp Thấp, ghi vào báo cáo của phiếu (không cần khóa phân tán).

Ô trạng thái app tự ghi sau khi gửi (1.7) dùng cùng cách: chỉ ghi khi Trạng thái, Mã bài WordPress vẫn như lúc mở bài (hoặc đang ở trạng thái «trước» hợp lệ, ví dụ «Đang viết» → «Đã gửi nháp»).

### 2.6 Cache SQLite

File `data/plan_cache.sqlite` (đã bị `.gitignore` chặn qua `data/`, `*.sqlite`), làm như `seo_app/storage/site_index.py`:

- Bảng `info` (mã băm của Sheet ID, giờ tải có múi giờ, dòng tiêu đề, phiên bản cấu trúc) và `rows` (số dòng, Mã bài, dữ liệu JSON đã qua `PlanRow`). SQL chỉ dùng tham số `?`.
- Dùng để vẽ trang ngay khi mở và khi mất mạng (nhãn «bản lưu lúc 14:05»). Tự tải lại khi cũ hơn 5 phút; **luôn** đọc lại từ Sheets trước mọi lệnh ghi và trước khi mở Soạn bài từ một dòng.
- Đọc từ file là dữ liệu chưa tin cậy: kiểm lại từng dòng; một dòng sai hay đổi Sheet (mã băm khác) → bỏ cả cache, tải lại. Xóa file vẫn tạo lại được. Không lưu bí mật, không lưu Sheet ID gốc.
- Việc ghi Sheets còn nợ sau khi gửi bài (1.7) **không** để trong cache (cache xóa được): để trong kho nháp `drafts.sqlite`, gắn với nháp.

---

## 3. Hẹn giờ và đăng ngay (yêu cầu 3)

### 3.1 WordPress làm gì (mục Nguồn), và hệ quả cho thiết kế

| Hành vi của WordPress | App phải làm |
|---|---|
| `future` với giờ < 60 giây sau **giờ máy chủ** (kể cả giờ đã qua) → **đăng ngay** | Giờ hẹn phải ≥ giờ máy chủ + **10 phút**, kiểm ngay trước lệnh hẹn giờ (không chỉ lúc người dùng chọn: tải ảnh có thể mất vài phút). Giờ máy chủ lấy từ header `Date` của lệnh đọc ngay trước đó; đồng hồ máy tính lệch website > 2 phút → Chặn, nhắc chỉnh đồng hồ |
| `publish` mà bài có ngày trong tương lai → thành `future` | Đăng ngay không gửi ngày; kiểm trạng thái trong câu trả lời |
| `date_gmt` là giờ tuyệt đối (UTC); múi giờ của site chỉ đổi cách hiện trong trang quản trị | Chỉ gửi `date_gmt`, **không** gửi `date` (giờ địa phương của site). `check_connection` đọc `timezone_string`, `gmt_offset`: khác giờ Việt Nam → Cảnh báo «trang quản trị sẽ hiện giờ khác; bài vẫn lên đúng giờ Việt Nam» |
| Cron WordPress chạy khi có người vào site; site ít khách thì bài hẹn giờ lên trễ | Nhãn «Lỡ lịch» ở bước đồng bộ (1.7); README khuyên nhờ người làm web bật cron thật trên hosting |
| `publish`/`future` cần quyền `publish_posts` | Tài khoản thiếu quyền → khóa hai nút, nói rõ lý do (`ConnectionInfo.can_publish_posts` đã có) |
| Đoạn chỉ có một địa chỉ `https://…` bị **nhúng** (oEmbed) khi hiển thị | Bộ dựng bài phát hiện, **Chặn** (mục 3.5) |
| Nội dung không có khối Gutenberg được chạy `wpautop` khi hiển thị: xuống dòng đơn trong đoạn thành `<br>` | Bộ chuyển Markdown nối dòng mềm bằng dấu cách, không để `\n` trong `<p>` |

### 3.2 Thứ tự gửi: luôn nháp trước

Cả ba hình thức dùng chung đường gửi nháp đã chạy thật (T-054, T-086, T-089), «Hẹn giờ» và «Đăng ngay» chỉ thêm **một bước cuối**:

1. Dựng bài cuối (mục 3.5, phiếu T-096) và màn hình xác nhận; người dùng tick, bấm.
2. Kiểm lại ảnh, băm ảnh đã duyệt (như hiện nay).
3. Tải ảnh → tạo **nháp** (kèm slug, chuyên mục, thẻ: hiện chưa gửi, `write.py:2748`) → ảnh đại diện.
4. Ghi SEO lên SiteSEO (công tắc «Ghi SEO lên website»): Abilities chỉ cho ghi khi bài **còn là nháp** (`set_seo_meta`), nên phải trước bước 5.
5. **Chỉ khi** chế độ là Hẹn giờ / Đăng ngay: `release_draft` (3.3).
6. Ghi kết quả vào kho nháp (`SendState` thêm: hình thức, giờ hẹn, đã chuyển hay chưa, không rõ kết quả), cập nhật dòng kế hoạch (1.7).

Lỗi ở bước 3–4 → dừng, bài (nếu đã có) **vẫn là nháp**, câu báo nói rõ «chưa hẹn giờ/chưa đăng». Lỗi ở bước 5 kiểu từ chối rõ ràng (4xx) → bài vẫn là nháp. Lỗi không rõ (hết giờ, mất mạng, 5xx) → khóa nút như `maybe_draft` hiện nay: «Bài **có thể đã** được hẹn giờ/đăng. Mở trang quản trị kiểm tra trước khi làm gì tiếp», kèm link sửa bài. Không bao giờ tự gửi lại.

**Đăng ngay khi SEO chưa ghi lên website** (công tắc tắt, hoặc site chưa cho ghi): Chặn, vì bài lên công khai với tiêu đề SEO mặc định mà không còn bước nào để sửa trước. **Hẹn giờ** khi SEO chưa ghi: Cảnh báo (còn thời gian chép tay vào SiteSEO trước giờ đăng).

### 3.3 Đúng một đường tới `future` / `publish` trong client

Trong `seo_app/wordpress/client.py`:

```python
_RELEASE = object()  # dấu riêng: chỉ release_draft truyền vào _request

def release_draft(self, post_id: int, *, mode: Literal["future", "publish"],
                  when_utc: datetime | None = None) -> Released: ...
```

| Ràng buộc | Chi tiết |
|---|---|
| Chỉ bài app vừa tạo | `post_id` trong `_created_post_ids` của **chính đối tượng client** (client mới mỗi lần gửi, nên chỉ bài vừa tạo trong lần bấm này) |
| Bài còn là nháp ngay trước lệnh | `_own_draft` (đã có): site xác nhận `status == "draft"`. Thêm: đọc header `Date` của chính câu trả lời này làm giờ máy chủ |
| Giờ hẹn | `mode="future"`: `when_utc` có múi giờ, ≥ giờ máy chủ + 10 phút, ≤ 1 năm (chặn gõ nhầm năm). `mode="publish"`: `when_utc` phải là `None` |
| Lệnh gửi | `POST /wp/v2/posts/<id>`, thân JSON **chỉ** `{"status": "future", "date_gmt": "YYYY-MM-DDTHH:MM:SS"}` hoặc `{"status": "publish"}`; không nội dung, không tiêu đề; `_fields=id,status,date_gmt,link` |
| `_is_plain_request` | Khóa `status` khác `"draft"`, khóa `date_gmt` chỉ được nhận khi lệnh mang dấu `_RELEASE`, đúng đường `POST /wp/v2/posts/<id>`, đúng bộ khóa trên. Không có dấu → từ chối trước khi gửi như hiện nay. `date` không bao giờ được nhận |
| Kiểm câu trả lời | `id` khớp; `status` đúng chế độ; `future` thì `date_gmt` trả về đúng giờ đã gửi. Hẹn giờ mà nhận `publish` → câu báo khẩn: «Bài đã hiện công khai ngay» + cách chuyển về nháp (`security.md` mục 7.2) |
| Sau khi chuyển | Bỏ `post_id` khỏi `_created_post_ids`: không lệnh nào của client sửa tiếp bài đó |

Đọc trạng thái bài cho bước đồng bộ (1.7, 1.8): hàm chỉ đọc `post_statuses(ids)` = `GET /wp/v2/posts` với `include=<≤100 mã>`, `status=draft,future,publish,pending,private`, `context=edit`, `_fields=id,status,date_gmt,modified_gmt,link` (thêm `include` vào `ALLOWED_PARAMS` của đúng đường này). Giữ `list_published` như cũ.

**Test bắt buộc** (Soi Lỗi bổ sung): mọi đường khác (kể cả `create_draft`, `set_featured_image`, ghi meta) gửi `status` khác nháp hay `date_gmt` → từ chối, không có request; `release_draft` với bài không do client tạo, bài đã `publish`/`future`/`pending`, giờ đã qua, giờ < 10 phút, đồng hồ lệch → từ chối, không có request; câu trả lời sai trạng thái → lỗi đúng câu; một test đọc mã nguồn khẳng định `_RELEASE` chỉ xuất hiện ở định nghĩa, `release_draft` và `_is_plain_request`, và `release_draft` chỉ được gọi từ đúng một hàm của bước Xuất bản.

### 3.4 Múi giờ: `Asia/Ho_Chi_Minh` → `date_gmt`

`seo_app/publish/schedule.py` (logic thuần):

- Người dùng chọn ngày + giờ (điền sẵn từ dòng kế hoạch; không có giờ thì giờ mặc định trong cấu hình). Dựng `datetime(…, tzinfo=ZoneInfo(settings.timezone_name))`, đổi sang UTC, gửi dạng `YYYY-MM-DDTHH:MM:SS` không đuôi múi giờ. Việt Nam không đổi giờ mùa hè nên không có giờ «không tồn tại».
- Nhãn hiển thị do máy tính (YC-803): «**Thứ Ba, 03/11/2026 lúc 08:00** (giờ Việt Nam)».
- Kiểm: ngày đã qua → Chặn; < 10 phút nữa → Chặn; > 365 ngày → Chặn; trùng giờ với bài khác đã hẹn (từ đồng bộ) → Cảnh báo.

### 3.5 Màn hình xác nhận

Hiện khi chọn Hẹn giờ hoặc Đăng ngay (và cả với Nháp, ở dạng rút gọn), **trước** khi gửi bất cứ thứ gì. Dữ liệu do bộ dựng bài (T-096) trả, giao diện (T-102) chỉ hiển thị:

| Phần | Nội dung |
|---|---|
| Hình thức | Hẹn giờ «Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)» hoặc «**Hiện công khai ngay khi bấm**»; cảnh báo múi giờ site (3.1) |
| Bài | Tiêu đề, đường dẫn sẽ có (`tên miền/slug/`), chuyên mục, thẻ, ảnh đại diện |
| SEO | Tiêu đề, mô tả, từ khóa chính; «sẽ ghi lên website» hay «chưa ghi: chép tay» |
| **Mọi link** | Bảng mọi `href` trong HTML cuối (kết quả `check_links`): chữ neo, địa chỉ, loại (nội bộ / ra ngoài / neo / khác), mức, lý do. Tên máy hiện **dạng ASCII** (`xn--…`), tên máy có chữ ngoài ASCII, có `@`, `//…`, `\` được đánh dấu riêng (LC-T039-1). Địa chỉ hiện bằng chữ thường, **không bấm được** |
| Địa chỉ trần | Mọi chuỗi dạng `https://`, `www.`, email còn trong chữ (sau khi gỡ ký tự rộng 0); đoạn **chỉ có một địa chỉ** → Chặn «WordPress sẽ nhúng trang này vào bài» |
| Ảnh | Từng ảnh: mục, alt, **còn vị trí GPS hay không**; câu nhắc «ảnh và vị trí GPS sẽ công khai cùng bài» (hiện có cho nháp) |
| Shortcode | Danh sách đoạn dạng shortcode (`shortcode_findings`, đã có) |
| Kiểm tra trước khi đăng | Các dòng Chặn / Cảnh báo (bài trống, câu cần xem lại, ảnh chưa duyệt, SEO, link Chặn, lỗi giờ). Còn dòng Chặn → nút khóa |
| Xác nhận | Ô tick «Tôi đã đọc lại toàn bài và danh sách trên» (M7 #13). Nút ghi rõ: «Gửi và hẹn giờ Thứ Ba 03/11 08:00» / «Gửi và **đăng công khai ngay**» |

**Ràng buộc xác nhận với đúng nội dung đã xem:** bộ dựng bài tính mã băm SHA-256 của toàn bộ thứ sẽ gửi (tiêu đề, HTML cuối, slug, chuyên mục, thẻ, băm từng ảnh, chữ SEO, hình thức, giờ hẹn UTC). Lúc bấm, dựng lại và so: khác (tab khác vừa sửa bài, ảnh đổi, giờ đổi) → không gửi, bỏ tick, hiện lại màn hình. Cùng ý với băm ảnh đã duyệt của T-086.

### 3.6 Không bao giờ sửa bài đã đăng ngoài ý người dùng

- App chỉ gửi lệnh ghi tới bài **chính lần gửi này** tạo ra, khi site xác nhận bài còn là nháp (3.3). Không có hàm nào ghi vào bài `publish`, `future`, `pending`, `private`.
- Đồng bộ trạng thái (1.7) **chỉ đọc** WordPress; chỉ ghi Google Sheets.
- Không có «hủy hẹn giờ», «sửa bài đã đăng», «cập nhật bài cũ» trong Giai đoạn 5: làm trong trang quản trị WordPress (câu hỏi 5, 6).
- Bài đã gửi nháp ở lần trước: theo câu hỏi 5 (khuyến nghị: hẹn giờ trong trang quản trị, app tự nhận ra).

---

## 4. Đối chiếu điều kiện Lá Chắn (yêu cầu 4)

Gồm 8 dòng của `board.md` mục «Việc bắt buộc khi làm Giai đoạn 5» và các điều kiện Giai đoạn 5 rải trong biên bản (T-003…009, T-004/T-005, T-008r3, T-031, T-039, T-041).

| # | Điều kiện | Nguồn | Phiếu làm | Cách chứng minh |
|---|---|---|---|---|
| 1 | Markdown → HTML bằng code có escape, hiểu `\`, chuẩn hóa xuống dòng (`\r\n`, `\r`), **không** xử lý link tham chiếu (`[x]: url`) | board; T-008r3 #2 | **T-096** | Test bộ chuyển: mọi ký tự HTML bị escape, `\*` thành `*`, khai báo link tham chiếu ra chữ thường, `\r` như `\n` |
| 2 | `sanitize_html` cho **toàn bộ** HTML cuối, kể cả phần người dùng tự gõ | board; T-008r3 #2 | **T-096** (bộ dựng luôn lọc), **T-102** (mọi hình thức gửi đi qua bộ dựng; chữ sửa tay cũng đi qua) | Test bộ dựng; test giao diện: HTML tới client giả đúng là đầu ra bộ dựng |
| 3 | Màn hình xác nhận liệt kê **mọi** `href`, đánh dấu địa chỉ lạ, `@` ở phần tên máy, `//…` | board; T-015; T-004 #2 | **T-096** (dữ liệu: `check_links` + đánh dấu), **T-102** (hiển thị, bắt buộc) | Test: HTML có link `@`, `//`, `\` → có dòng đánh dấu; AppTest màn hình có đủ dòng |
| 4 | Đúng một đường tới `publish`/`future`, có xác nhận, có test không xác nhận thì không đăng | board; T-001; W1 | **T-099** (client, mục 3.3), **T-102** (giao diện, băm xác nhận) | Test client (3.3); AppTest: chưa tick / nội dung đổi sau khi xem → `release_draft` không được gọi |
| 5 | Từ khóa từ Google Sheets vô hiệu thẻ khung (SL-7) | board; T-010 | **T-098** (`_neutralize` + đổi «» cho từ khóa ở **mọi** lời dặn, kể cả từ khóa gõ tay), **T-100** (mọi dòng từ Sheets/cache qua `PlanRow`) | Gỡ `xfail` của `test_keyword_cannot_fake_a_frame` (`tests/test_soi_loi_t003_t009.py:209`) khi XPASS |
| 6 | URL trần không thành link (GFM autolink) | board; T-015 | **T-096** (bộ chuyển không có autolink; liệt kê địa chỉ trần) | Test: bài có `https://`, `www.`, email → HTML không có `<a>` nào ngoài link nội bộ |
| 7 | Gỡ U+200B (`unbreak_autolinks`) trước khi gửi: thân bài, tiêu đề bài, tiêu đề mục, meta; sau khi gỡ không autolink; chữ đã gỡ không coi là an toàn | board; T-031 | **T-096** (thân, tiêu đề: gỡ rồi mới escape trong bộ chuyển); meta: **đã có** (`normalize_meta` bỏ ký tự loại Cf, T-041), **T-102** giữ test | Test: HTML gửi đi và chữ SEO không còn U+200B (theo gợi ý test của T-031) |
| 8 | Kết quả `unescape_link_syntax`/`unbreak_autolinks` không bao giờ vào `st.markdown` | board | **T-096** (dữ liệu xác nhận trả chữ thô có ghi chú «phải escape»), **T-102** | Test giao diện: chữ link, địa chỉ hiện qua `st.text`/ô bảng hoặc `escape_markdown`; Lá Chắn grep `st.markdown` quanh `sent_text` |
| 9 | Thứ tự: `sanitize_html` → `apply_links` → `sanitize_html` → `check_links(…, required_ids)` trên đúng HTML sẽ gửi; tải lại danh sách bài ngay trước `check_links`; mức Chặn khóa nút gửi | LC-T039 đk 3a | **T-096** (thứ tự), **T-102** (tải lại, khóa nút) | Test bộ dựng gọi đúng thứ tự (client, index giả) |
| 10 | Mỗi phần đúng một `<h2>`; tiêu đề con trong thân là `<h3>` trở xuống (`#`, `##` trong thân hạ cấp) | LC-T039 đk 3b | **T-096** | Test: thân có `#`, `##`, `###` → không có `<h1>`, `<h2>` trong thân |
| 11 | LC-T039-1: tên máy hiện dạng ASCII `xn--…`, đánh dấu tên máy ngoài ASCII, link không bấm được; test 2 địa chỉ Kirin | LC-T039 đk 3c | **T-096** (dữ liệu), **T-102** (hiển thị) | Test với `suachuacuasаt.com` (а Kirin), `suachuacuasat.cоm` |
| 12 | LC-T039-2: `place_links` giữ `[` `]` đã vô hiệu; gỡ 3 `xfail` của `tests/test_la_chan_t039.py` | LC-T039 đk 3d | **T-096** (sửa `links.py` trước khi dùng `apply_links`) | 3 test XPASS, gỡ `xfail` |
| 13 | U1 cho `LinkPlacement.skipped`, `LinkCheck.message`, `LinkCheck.href` | LC-T039 đk 2c, LC-T041 đk 3 | **T-102** | AppTest như T-041 |
| 14 | Link nội bộ gắn **sau** `clean_ai_text`; `href` chỉ từ danh sách bài, không từ AI | T-004/T-005; T-033 4.3 | **T-096** (giữ `apply_links`, không đường nào khác ghép `<a>`) | Test: bộ chuyển không bao giờ sinh `<a>` |
| 15 | `set_featured_image` (và mọi lệnh ghi tiếp) chỉ trong cùng đối tượng client | T-003…009 | **T-099** (`release_draft` cũng vậy; bỏ mã bài sau khi chuyển) | Test client |
| 16 | JSON-LD lên site (FAQPage) | LC-T041 đk 3 | **Không làm ở Giai đoạn 5** (T-033 mục 3.3 cách d, phiếu riêng khi chủ dự án muốn) | — |

---

## 5. Bảo mật từng phần (yêu cầu bảo mật riêng)

| Phần | Rủi ro | Biện pháp trong thiết kế | Mục `security.md` |
|---|---|---|---|
| **Khóa service account** | Lộ file JSON: ai có nó đọc/sửa được mọi Sheet đã chia sẻ cho tài khoản này | Chỉ chia sẻ một Sheet; service account không có vai trò nào trong project; file ngoài thư mục dự án (app từ chối file trong thư mục dự án) và ngoài thư mục đồng bộ; không in, không ghi log, câu lỗi cố định (lỗi của `google-auth` có thể chứa trả lời của máy chủ mã); mã truy cập chỉ trong bộ nhớ; `token_uri` cố định; khi lộ: xóa khóa trong Google Cloud, tạo khóa mới, sửa `.env` hai máy (mục 7.1 đã có) | 2.1, 2.7, 7 |
| | File khóa bị sửa để gửi chữ ký sang máy chủ lạ | Kiểm `token_uri`, `universe_domain` (2.1) | 2.7 |
| **Dữ liệu từ Google Sheets, file, chữ dán** (chưa tin cậy) | Lệnh giấu trong từ khóa, ghi chú điều khiển AI (prompt injection) | Từ khóa, ghi chú, kế hoạch đều vào khung dữ liệu, vô hiệu thẻ khung (SL-7); việc `plan` không có tìm web; AI không có công cụ, chỉ trả đề xuất; code kiểm từng đề xuất; người dùng tick mới ghi | 2.4, A1, A2 |
| | Chèn công thức khi app ghi Sheet (`=IMPORTXML(…)` gửi dữ liệu Sheet ra ngoài) | Ghi **luôn** `RAW` | 2.3 |
| | Chữ lạ hiện trên giao diện thành link, HTML | Hiện bằng ô bảng, `st.text` hoặc `escape_markdown`; không `unsafe_allow_html` | U1 |
| | File/Sheet rất lớn làm treo app | Giới hạn 1 MB, 1.000 dòng, 26 cột, 2.000 ký tự/ô, câu trả lời ≤ 2 MB | 2.6 (tinh thần chống bom) |
| | Link trong Sheet đưa vào bài | Cột «Trang dịch vụ đích» chỉ đổi thành **mã bài** có trong danh sách bài đã đăng; app không bao giờ chèn địa chỉ lấy từ Sheet, không mở link do người dùng dán ngoài dạng link Google Sheets | 2.3 |
| | Cache bị sửa tay | Đọc lại như dữ liệu ngoài, sai thì bỏ (như `site_index.py`) | F3 |
| **Đường gọi WordPress mới** (`release_draft`, `post_statuses`) | Lỡ đăng bài (Nghiêm trọng nếu sai) | Một đường duy nhất có dấu riêng, chỉ bài vừa tạo, site xác nhận còn nháp, màn hình xác nhận có băm, test (3.3) | 2.2, W1 |
| | Hẹn giờ thành đăng ngay (giờ đã qua, đồng hồ lệch) | ≥ 10 phút theo giờ máy chủ, kiểm lệch đồng hồ, kiểm trạng thái trả về | 2.2 |
| | Sửa bài đã đăng | Không hàm nào ghi vào bài không phải nháp (3.6) | W2, R3 |
| | Link ẩn, trang bị nhúng | Bộ chuyển không tạo link; bảng mọi `href`; đoạn chỉ có địa chỉ → Chặn | 2.3, W3 |
| | Tham số đọc mới (`include`, `status` nhiều giá trị) | Thêm vào `ALLOWED_PARAMS` của đúng `GET /wp/v2/posts`; `_fields` cố định không có `content` | 2.7 |
| **AI đề xuất kế hoạch** | AI bị dụ đề xuất «Bỏ» hàng loạt hay thêm từ khóa rác | «Bỏ» không tick sẵn; tối đa 100 đề xuất; app không bao giờ xóa dòng | A2 |
| **Đường mới tới Google** | Đổi đường gọi, gọi API khác | Danh sách đường cố định (2.3), chỉ `sheets.googleapis.com` (và máy chủ mã `oauth2.googleapis.com`), không theo chuyển hướng, timeout | 2.7 |

Không đề xuất chấp nhận rủi ro mới nào ngoài khe hở «ghi cùng một ô trong 1–2 giây» (2.5, Thấp; Lá Chắn quyết có cần ghi sổ không).

---

## 6. Chia phiếu (yêu cầu 5)

Số phiếu tạm từ **T-096** (theo `board.md`); Chỉ Huy đánh lại nếu đã dùng. Trước khi giao, Chỉ Huy tạo sẵn trên `main` ba gói rỗng `seo_app/publish/__init__.py`, `seo_app/plan/__init__.py`, `seo_app/google/__init__.py` để các phiếu song song chỉ **thêm file riêng**.

Độ lớn: **S** ≈ dưới 150 dòng code; **M** ≈ 150–400 dòng code + test; **L** ≈ 400–900 dòng code + test nhiều, thường 2 lượt Soi Lỗi/Lá Chắn.

### Nhóm 1: logic, chạy bằng dữ liệu giả (không cần website, không cần Google)

| Phiếu | Mục tiêu | Agent | File được sửa | Phụ thuộc | Độ lớn | Bảo mật / Lá Chắn |
|---|---|---|---|---|---|---|
| **T-096** Bộ dựng bài cuối | `seo_app/publish/render.py`: Markdown → HTML (phần nhỏ của Markdown AI dùng: đoạn, `###`, danh sách 2 cấp, bảng GFM, đậm, nghiêng, `mã`, trích dẫn, kẻ ngang; mọi thứ khác là chữ đã escape; **không** link, không link tham chiếu, không autolink, không HTML thô); dùng chung quy tắc khối với `markdown_blocks` để link chèn đúng chỗ. `build_article(...)`: `sent_text` → chuyển → `sanitize_html` → `place_links` → `sanitize_html` → `check_links` → `ArticleReview` (mọi `href`, tên máy ASCII, địa chỉ trần, đoạn chỉ có địa chỉ, mã băm xác nhận). Sửa LC-T039-2 trong `links.py` | Thợ Máy | mới: `seo_app/publish/render.py`, `seo_app/publish/review.py`, `tests/test_publish_render.py`, `tests/test_publish_review.py`; sửa: `seo_app/onpage/links.py` (LC-T039-2, tách hàm nhận dạng khối dùng chung), gỡ `xfail` `tests/test_la_chan_t039.py` | Không | **L** | Mục 4 dòng 1–3, 6–12, 14; đầy đủ |
| **T-097** Google Sheets | `seo_app/google/service_account.py` (kiểm file khóa, 2.1), `seo_app/google/sheets.py` (`SheetsClient`, đường cố định 2.3, `RAW`, lỗi cố định, thử lại 429), tách mã từ link Sheet; ghi `GOOGLE_SHEET_ID` vào `.env` từ Cài đặt (mở rộng `env_file.py` với bộ kiểm riêng); khai báo `google-auth` | Thợ Máy | mới: 2 file trên, `tests/test_google_sheets.py`; sửa: `seo_app/env_file.py`, `pyproject.toml`, `uv.lock` (không thêm gói) | **Câu hỏi 1** | **M–L** | Bí mật mới (S1–S3), 2.7; đầy đủ; Lá Chắn quét `google-auth` |
| **T-098** Kế hoạch: khuôn, đọc, đề xuất | `seo_app/plan/model.py` (`PlanRow`, nhãn, bộ làm sạch), `parse.py` (CSV/TSV/chữ dán, tên cột đồng nghĩa, ngày), `propose.py` (so bảng → đề xuất, kiểm 1.4); AI: `ContentWriter.plan_changes`, `prompts.plan_prompt` (khung `ke_hoach_hien_tai`, `ke_hoach_moi`), `PlanSuggestions` + kiểm; **SL-7** cho mọi lời dặn | Thợ Máy | mới: 3 file `seo_app/plan/`, `tests/test_plan_*.py`; sửa: `seo_app/content/prompts.py`, `seo_app/content/workflow.py`, `seo_app/content/models.py`; gỡ `xfail` SL-7 | Không (dùng `SiteIndex` có sẵn) | **L** | A1, A2, SL-7; đầy đủ |
| **T-099** Client: hẹn giờ, đăng ngay, đọc trạng thái | `release_draft` + dấu `_RELEASE` + `_is_plain_request` (3.3); `post_statuses`; `ConnectionInfo` thêm múi giờ site; `seo_app/publish/schedule.py` (giờ Việt Nam → UTC, nhãn thứ, kiểm giờ, 3.4) | Thợ Máy | sửa: `seo_app/wordpress/client.py`; mới: `seo_app/publish/schedule.py`, `tests/test_wordpress_release.py`, `tests/test_publish_schedule.py` | **Sau T-091** (cùng `client.py`; T-091 chờ T-059 bước 7) | **M** | W1, W2, R2, R3; đầy đủ, **soát kỹ nhất** |
| **T-100** Đồng bộ kế hoạch | `seo_app/storage/plan_cache.py` (2.6); `seo_app/plan/sync.py`: đọc Sheet → `PlanRow`, áp dụng đề xuất có kiểm xung đột (2.5), ghi 4 ô trạng thái, «Chuẩn bị trang tính»; kho nháp: `DraftSnapshot.plan`, `SendState` thêm hình thức/giờ hẹn/đã chuyển, bảng việc ghi Sheets còn nợ | Thợ Máy | mới: 2 file trên, test; sửa: `seo_app/storage/drafts.py` (tăng phiên bản cấu trúc, nháp cũ vẫn mở được) | T-097, T-098 | **M–L** | F3, SQL tham số, dữ liệu file chưa tin cậy; đầy đủ |

### Nhóm 2: nội dung

| Phiếu | Mục tiêu | Agent | File | Phụ thuộc | Độ lớn | Lá Chắn |
|---|---|---|---|---|---|---|
| **T-103** Lời dặn đọc kế hoạch | Viết lại phần chữ `plan_prompt` cho tự nhiên, đúng 3 nhãn ý định, lý do ngắn dễ hiểu, câu cảnh báo trang cửa ngõ; `[tasks.plan]` trong `config/ai.toml` (không `web_search`, cùng hãng/mô hình với `outline` cho tới khi chủ dự án đổi); `[plan]` trong `config/content.toml` (giờ đăng mặc định 08:00, nhãn) | Ngòi Bút | `config/ai.toml`, `config/content.toml`, phần chữ trong `seo_app/content/prompts.py` | Sau T-098 | **S** | Rút gọn (A1, không bỏ `DATA_RULES`) |

### Nhóm 3: giao diện (thay demo, giữ bố cục đã duyệt)

| Phiếu | Mục tiêu | Agent | File được sửa | Phụ thuộc | Độ lớn | Lá Chắn |
|---|---|---|---|---|---|---|
| **T-101** Trang Kế hoạch, Cài đặt Google, trang Bài viết | Kế hoạch: 3 tab nhận kế hoạch, bảng đề xuất có tick + lý do + cảnh báo, «Áp dụng» ghi Sheets, kết quả xung đột, danh sách bài từ cache + «Tải lại», «Cập nhật trạng thái từ website», nút «Viết bài». Cài đặt → Google: đã khai báo khóa chưa, email để chia sẻ, dán link Sheet, «Kiểm tra kết nối», «Chuẩn bị trang tính». Bài viết: «Tiếp theo trong kế hoạch», «Đã gửi WordPress». Khung «Thông tin nền cho mọi bài» hiện tóm tắt `config/business_profile.md` (chỉ đọc). Xóa phần mẫu kế hoạch trong `demo.py` | Họa Sĩ | `app/views/plan.py`, `app/views/settings.py`, `app/views/home.py`, `seo_app/demo.py` (phần kế hoạch, `SENT_TO_WORDPRESS`) | T-100, T-103 (và T-099 cho `post_statuses`) | **L** | U1, U2; đầy đủ |
| **T-102** Bước Xuất bản thật | Cả ba hình thức gửi bằng bộ dựng T-096 (nháp cũng có định dạng, link nội bộ, slug, chuyên mục thật từ `list_categories`); màn hình xác nhận (3.5) + băm; Hẹn giờ (ngày/giờ điền sẵn từ kế hoạch) và Đăng ngay qua `release_draft`; kết quả, khóa khi không rõ; ghi dòng kế hoạch (1.7). Mở Soạn bài từ dòng kế hoạch (1.6). Xóa `CATEGORIES` khỏi `demo.py` | Họa Sĩ | `app/views/write.py` (bước Xuất bản, khởi tạo từ kế hoạch), `seo_app/demo.py` (`CATEGORIES`) | T-096, T-099, T-100 | **L** | W1, W3, U1; đầy đủ |

### Đi kèm

| Việc | Agent | Phụ thuộc | Ghi chú |
|---|---|---|---|
| README «Kế hoạch và Google Sheets» (tạo service account từng bước, chia sẻ Sheet, chuẩn bị trang tính), «Hẹn giờ và Đăng ngay» (giờ Việt Nam, lỡ lịch, cron), chú thích `.env.example` cho 2 biến Google | Thư Ký | T-101, T-102 | S; Lá Chắn rút gọn |
| **Thử thật**: (1) Sheet bản sao «KeHoach-thu»: đọc, áp dụng đề xuất, sửa tay cùng lúc trên trình duyệt để thấy báo xung đột; (2) hẹn giờ **một bài thật chủ dự án muốn đăng**, giờ ≥ 1 ngày sau, kiểm trong trang quản trị hiện «Đã lên lịch» đúng giờ Việt Nam, sau giờ hẹn 15 phút kiểm bài đã lên; (3) Đăng ngay chỉ với bài chủ dự án duyệt đăng. Không có site thử nên không đăng bài thử | Chỉ Huy + chủ dự án | Tất cả | Ghi kết quả vào báo cáo; Application Password, file khóa không ghi vào báo cáo |

### Thứ tự và song song

```
Đợt 1 (song song, ≤ 3 phiên):  T-096 · T-098 · T-097 (khi có câu trả lời 1)
                                T-099 khi T-091 đã gộp (cùng client.py)
Đợt 2:                          T-100 (sau T-097, T-098) · T-103 (sau T-098)
Đợt 3 (song song):              T-101 (plan/settings/home) · T-102 (write.py)
Đợt 4:                          README · Thử thật · Lá Chắn rà cả Giai đoạn 5
```

File không chồng nhau giữa các phiếu cùng đợt. Chỗ dễ đụng: `seo_app/storage/drafts.py` (T-100) với T-092 (Họa Sĩ, nháp bị xóa ở tab khác) nếu T-092 sửa file này → làm T-092 trước hoặc sau T-100, không song song. `seo_app/demo.py` bị T-101 và T-102 sửa ở hai chỗ khác nhau (gộp thường không xung đột).

---

## 7. Thư viện

| Việc | Dùng | Không dùng (và vì sao) |
|---|---|---|
| Xác thực Google | `google-auth` (**đã cài sẵn**, chỉ khai báo: câu hỏi 1) | `gspread`, `google-api-python-client`: gói mới, không cần |
| Gọi Sheets REST | `requests` (đã có) qua `AuthorizedSession` | |
| Markdown → HTML | **Tự viết** phần nhỏ (mục 6, T-096) | `markdown-it-py` (+`mdurl`): gói mới; phải tắt nhiều thứ (link, HTML, autolink) và vẫn phải khớp cách chia khối với `markdown_blocks` để chèn link đúng chỗ. Tự viết phần nhỏ dễ kiểm hơn, khớp chắc chắn với `apply_links` |
| CSV, TSV, chữ | `csv`, thư viện chuẩn | |
| Excel `.xlsx` | Không (câu hỏi 2, A) | `openpyxl` nếu chủ dự án chọn B: MIT, phổ biến; mở `read_only`, `data_only`, từ chối `.xlsm`, giới hạn kích thước giải nén |
| Word, PDF | Không: chép chữ rồi dán | `python-docx`, `pypdf`: gói mới, file nhị phân phức tạp |
| Múi giờ | `zoneinfo` + `tzdata` (đã có) | |
| Cache | `sqlite3` (chuẩn) | |

---

## 8. Ngoài phạm vi Giai đoạn 5 (ghi lại để không quên)

- **Cập nhật bài cũ** (YC-804), gộp bài, chuyển hướng 301 (YC-503, YC-806): sửa bài đã có trên website, cần chủ dự án duyệt riêng theo R3 (câu hỏi 6).
- Hủy hẹn giờ, đổi giờ hẹn từ app: làm trong trang quản trị.
- Các dòng M7 chưa có dữ liệu để kiểm: số liệu khớp file thông tin (M7 #2), địa danh theo danh sách hành chính (#3), độ giống giữa các trang khu vực (#5), lỗi chính tả cấm (#1). Cần file thông tin doanh nghiệp và danh sách 168 phường, xã; đề xuất phiếu sau.
- FAQPage lên site (T-033 mục 3.3 cách d).
- Theo dõi thứ hạng: Giai đoạn 6 (dùng lại service account, thêm phạm vi chỉ đọc Search Console).

---

## 9. Câu hỏi cho chủ dự án (yêu cầu 6)

Xếp theo mức cần thiết. Mỗi câu trả lời bằng một chữ cái. Phần nào chưa có câu trả lời, app vẫn chạy với lựa chọn khuyến nghị an toàn nhất.

**Câu 1. Cho app dùng thư viện xác thực của Google để đọc, ghi Google Sheets?**
Để đọc/ghi Sheet bằng tài khoản dịch vụ, app cần thư viện `google-auth` của chính Google. Thư viện này **đã có sẵn trong máy** (thư viện Gemini đang dùng nó), chỉ cần ghi tên nó vào danh sách thư viện của app, không tải thêm gì.
- **A (khuyến nghị).** Đồng ý. Hệ quả: kế hoạch nằm trên Google Sheets, hai máy luôn thấy giống nhau, app tự ghi trạng thái bài.
- **B.** Không dùng. Hệ quả: app chỉ nhận kế hoạch qua file và chữ dán, xuất file CSV để tự dán lại vào Sheet; hai máy không tự đồng bộ.

**Câu 2. File kế hoạch tải lên nhận loại nào?**
Giao diện demo ghi nhận cả Excel, Word, PDF. Đọc thẳng các loại này phải thêm thư viện mới.
- **A (khuyến nghị).** Nhận CSV và chữ thường (TXT); với Excel, Word, PDF thì mở file, **chép vùng ô hoặc đoạn chữ rồi dán** vào ô «Dán nội dung» (app nhận ra bảng chép từ Excel), hoặc dán link Google Sheets. Hệ quả: không thêm thư viện; giao diện bỏ chữ «Excel, Word, PDF» ở ô tải file.
- **B.** Thêm thư viện `openpyxl` để đọc thẳng file `.xlsx` (Word, PDF vẫn chép dán). Hệ quả: thêm một thư viện, Lá Chắn quét trước khi dùng.

**Câu 3. Kế hoạch trên Google Sheets đặt thế nào?**
- **A (khuyến nghị).** Dùng một Google Sheet (mới hoặc đang có), app tạo một trang tính tên **«KeHoach»** với các cột cố định ở mục 2.4 (có danh sách chọn cho ý định, loại trang, ưu tiên, trạng thái). Hệ quả: vẫn sửa tay thoải mái trên Google Sheets; thêm cột riêng được; app chỉ ghi vào các cột của mình.
- **B.** App đọc theo bảng kế hoạch đang có, cột do chủ dự án chỉ ra. Hệ quả: tốn thêm công khai báo cột, dễ hỏng khi đổi tên cột.

**Câu 4. App có tự cập nhật trạng thái trên Sheet không?**
Khi bấm «Viết bài» từ một dòng, hay gửi bài lên WordPress xong.
- **A (khuyến nghị).** Tự ghi, **chỉ 4 ô** của đúng dòng đó: Trạng thái, Mã bài WordPress, Ngày đăng thực tế, Cập nhật lúc. Các thay đổi khác (thêm bài, đổi ngày, bỏ bài) vẫn phải tick duyệt. Hệ quả: Sheet luôn đúng mà không thêm thao tác.
- **B.** Mọi thay đổi trên Sheet, kể cả trạng thái, đều phải tick duyệt. Hệ quả: thêm một bước sau mỗi lần gửi bài.

**Câu 5. Bài đã gửi lên làm nháp từ trước, muốn hẹn giờ hay đăng thì làm ở đâu?**
App hẹn giờ/đăng được ngay **trong lần gửi** (bài lên WordPress là hẹn giờ hoặc đăng luôn).
- **A (khuyến nghị).** Bài đã là nháp trên website thì hẹn giờ hoặc đăng trong **trang quản trị WordPress** (nút «Lên lịch» / «Đăng»); app tự nhận ra và cập nhật Sheet. Hệ quả: app không có lệnh nào sửa bài đã nằm trên website; xem bài thật trước khi đăng.
- **B.** App được hẹn giờ/đăng cả bài nháp app tạo từ trước (chỉ khi chưa ai sửa bài đó trong trang quản trị). Hệ quả: thêm một đường sửa bài đã có trên website (cần chủ dự án đồng ý theo quy tắc R3), thêm việc kiểm.

**Câu 6. Giai đoạn 5 có làm «Cập nhật bài cũ» (sửa bài đã đăng, giữ nguyên đường dẫn) không?**
- **A (khuyến nghị).** Chưa. Giai đoạn 5 chỉ viết bài mới, hẹn giờ, đăng. Cập nhật bài cũ để một giai đoạn sau, phiếu riêng, vì đó là sửa bài đang có trên website thật. Dòng kế hoạch loại «Cập nhật bài cũ» hiện nhắc «chưa hỗ trợ».
- **B.** Làm luôn trong Giai đoạn 5. Hệ quả: thêm 2–3 phiếu (đọc bài cũ, so khác biệt, sửa có xác nhận), Giai đoạn 5 dài hơn.

**Việc chủ dự án làm phía Google, WordPress** (không phải câu hỏi; README hướng dẫn): tạo project Google Cloud + service account + khóa JSON (mục 2.1); chia sẻ Sheet kế hoạch cho email của service account; kiểm WordPress → Cài đặt → Tổng quan → Múi giờ là «Hồ Chí Minh»; (nên) nhờ người làm web bật cron thật trên hosting để bài hẹn giờ lên đúng giờ.

---

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: luồng người dùng (mục 1)
- [x] Yêu cầu 2: Google Sheets, service account, thư viện, cấu trúc trang tính, xung đột, cache (mục 2, 7)
- [x] Yêu cầu 3: một đường tới `future`/`publish`, múi giờ, màn hình xác nhận, không sửa bài đã đăng (mục 3)
- [x] Yêu cầu 4: đối chiếu 16 điều kiện Lá Chắn (mục 4)
- [x] Yêu cầu 5: 8 phiếu + README + thử thật, thứ tự, song song, độ lớn (mục 6)
- [x] Yêu cầu 6: 6 câu hỏi có A/B và khuyến nghị (mục 9)
- [x] Yêu cầu bảo mật riêng: rủi ro từng phần (mục 5)
- [x] Báo cáo tại `docs/team/reports/T-094-tho-may.md`, có «Tóm tắt (cho chủ dự án)»
- [x] Không sửa code, cấu hình, test; không gọi website thật hay Google thật; không đọc `.env`

## Rủi ro và điểm cần chú ý

- **Chưa xác minh trên site thật**: tài khoản Biên tập viên đặt `future` bằng `date_gmt` qua REST (theo mã WordPress là được, quyền `publish_posts` đã thấy ở T-059); plugin bảo mật hay bộ nhớ đệm của hosting có giữ header `Date` đúng không (không đúng thì app báo lệch đồng hồ và Chặn, không đăng nhầm); cron của site có chạy đúng giờ không. Kiểm ở lượt thử thật.
- **Chưa xác minh với Google**: khóa service account có bị chính sách tổ chức chặn không (2.1); `drive.file` không dùng được (suy luận).
- Ngưỡng 60 giây của WordPress tính theo **giờ máy chủ**; biên 10 phút + kiểm lệch đồng hồ là để không bao giờ chạm ngưỡng.
- `wpautop` và `autoembed` là bộ lọc hiển thị của WordPress; theme hay plugin có thể thêm bộ lọc khác (ví dụ tự tạo link). Màn hình xác nhận chỉ đảm bảo HTML **gửi đi**; lượt thử thật nên xem bài hiển thị.
- Khe hở ghi cùng một ô trên Sheet trong 1–2 giây (2.5): Thấp.
- Bộ chuyển Markdown tự viết chỉ hiểu phần nhỏ; chỗ AI viết lạ (danh sách lồng 3 cấp, bảng lệch cột) hiện thành chữ thường, không hỏng bài. T-096 cần nhiều mẫu thật từ các bài đã viết.

## Đề xuất

- Chỉ Huy: tạo ba gói rỗng (`seo_app/publish/`, `seo_app/plan/`, `seo_app/google/`) trên `main` trước khi giao đợt 1; xếp T-099 sau T-091.
- Thư Ký: chú thích `.env.example` cho `GOOGLE_SERVICE_ACCOUNT_FILE` nên thêm «để file ngoài thư mục dự án và ngoài thư mục Google Drive đồng bộ; Google đặt tên file kiểu `ten-project-1a2b3c.json`, `.gitignore` không chặn tên này» (đi cùng phiếu README).
- Lá Chắn: xét thêm mẫu tên `*.json` có `"type": "service_account"` vào bước quét bí mật (detect-secrets có bộ nhận khóa riêng tư PEM, nên đã bắt được nội dung; chỉ là thêm lớp).
- Soi Lỗi: khi T-096 xong, lấy vài bài nháp thật đã viết (chỉ chữ, không bí mật) làm mẫu cho test bộ chuyển Markdown.

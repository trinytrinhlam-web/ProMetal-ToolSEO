# Báo cáo T-041 · Bước SEO thật · Soi Lỗi (rút gọn): phần logic, phần giao diện và lượt 3

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-041](../tickets/T-041-buoc-seo-that.md). Lượt 1: **phần logic** của Thợ Máy (đầu nhánh `c059b41`, gốc `main` `2e04066`). Lượt 2: **cả phiếu** (giao diện Họa Sĩ lượt 1–2, Thợ Máy lượt 2–3, đầu nhánh `433c533`) |
| Ngày nộp | 2026-10-26 (lượt 1), 2026-10-27 (lượt 2) |
| Kết quả lượt 1 | Phần logic: ĐẠT CÓ ĐIỀU KIỆN, 7 Thấp (SL-T041-1 → -7), 6 góp ý. Đã sửa hết ở Thợ Máy lượt 2 |
| **Kết luận cả phiếu (lượt 2)** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình; SL-T041-1 → -7 đóng; **4 Thấp mới** (SL-T041-8 → -11, test `xfail(strict=True)`), 3 góp ý. **Không lỗi nào phải sửa trước Lá Chắn**: chuyển Lá Chắn rút gọn được ngay. Nên sửa trước khi gộp: SL-T041-9, -10, -11; SL-T041-8 chờ Lá Chắn quyết. Chi tiết: mục [«Phần giao diện và lượt 3»](#phần-giao-diện-và-lượt-3-soi-lỗi-lượt-2-2026-10-27) |

## Tóm tắt (cho chủ dự án)

- Phần "máy" của bước SEO làm đúng các điều kiện bảo mật và các lỗi nhỏ mà các lần kiểm trước để lại. Tôi thử lại từng điều kiện bằng dữ liệu của riêng tôi, rồi thử **gỡ từng chỗ sửa trên một bản sao** của phần mềm: cả 28 lần gỡ đều bị bộ test phát hiện, tức là mỗi chỗ sửa đều có test canh thật.
- Nháp cũ (lưu trước phiếu này, kể cả nháp có ảnh) vẫn mở được. Phần SEO trong nháp bị sửa hỏng thì chỉ mất phần SEO, chữ và ảnh của bài còn nguyên. Nháp không lưu địa chỉ link.
- Chưa kết nối WordPress, hoặc WordPress lỗi (sai mật khẩu, máy chủ lỗi, mất mạng, hết giờ…): phần mềm chỉ báo một câu tiếng Việt nhẹ nhàng, không sập, không chép lời máy chủ hay mật khẩu.
- Tôi thấy 7 lỗi nhỏ, chủ yếu là chỗ "vênh" giữa các phần:
  1. Gợi ý meta của AI và nút «chép sang SiteSEO» vẫn cho qua chữ dạng lệnh WordPress (shortcode, ví dụ `[gallery]`), trong khi phần ghi lên website đã chặn đúng loại chữ này.
  2. Ô sửa tiêu đề (hiện chưa gắn đuôi « | Pro-Metal»): tiêu đề 38–48 ký tự bị chê «hơi ngắn» dù gắn đuôi vào là vừa đẹp; 49 ký tự lại được khen «vừa».
  3. Gõ từ khóa không dấu (ví dụ «sua cua uy tin hcm», giống cột từ khóa trong file kế hoạch) thì mọi tiêu đề AI viết có dấu đều bị loại.
  4. Nháp chỉ giữ 20 bản meta gần nhất: nếu bản anh/chị đang chọn cũ hơn thế thì bị bỏ, nháp lặng lẽ đổi sang bản khác.
  5. Mục Hỏi đáp: tiêu đề con không phải câu hỏi (như «Lưu ý trước khi đọc») vẫn bị coi là câu hỏi.
  6. Một dạng chữ hiếm (link nằm trong đoạn mã) làm dữ liệu Hỏi đáp gửi Google còn mang địa chỉ link.
  7. Nếu anh/chị đổi đuôi thương hiệu trong `config/content.toml`, lời dặn AI vẫn nói về đuôi « | Pro-Metal» cũ.
- Lỗi 1, 2, 4 nên sửa trước khi Họa Sĩ làm giao diện (đều sửa nhỏ). Các lỗi còn lại không chặn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t041.py` | Mới: 111 ca (94 qua, 17 `xfail(strict=True)` cho SL-T041-1 → -7). Thử độc lập các điều kiện, nháp khuôn 1/2 có ảnh, hàm cho Họa Sĩ với site giả lỗi đủ kiểu và AI giả trả gợi ý độc |
| `tests/test_soi_loi_t038.py` | `test_lone_surrogate_output_is_at_least_valid_json`: nay kết quả bị Chặn nên nhánh `if` cũ không bao giờ chạy (test rỗng); đổi thành khẳng định `json_ld is None` (chặt hơn), sửa docstring |
| `tests/test_soi_loi_t040.py` | Chỉ sửa 2 docstring cũ còn nói «phần mềm chưa đọc mục [meta]» |
| `docs/team/reports/T-041-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `config/`, test của Thợ Máy hay Lá Chắn. Commit test: `e3192b8`.

## Kiểm từng mục

### 1. Điều kiện phiếu giao: thử độc lập và gỡ chỗ sửa trên bản sao

Bản sao: `git worktree` tạm ở `c059b41` (không đụng `wt-T-041`), mỗi lần thay đúng một đoạn code về như trước khi sửa (đoạn phải có đúng một lần), chạy các file test của phần đó với `-x`, rồi trả file về. Script: `T-041-soi-loi-scripts/mutate.py` (thư mục ghi chú chung).

| Điều kiện | Kết quả | Thử độc lập (test của tôi) | Gỡ chỗ sửa → test bắt |
|---|---|---|---|
| LC-T038 đk 1, SL-T038-1: chặn Cs, Co, Cn | **ĐẠT** | 11 ký tự lạ (NUL, ESC, DEL, C1, 2 surrogate, 2 ký tự riêng, 3 chưa gán / không phải ký tự) ở câu hỏi hoặc trả lời: đều Chặn, không có JSON-LD, câu báo không chép ký tự (`test_lc_t038_1_…`, 22 ca) | `_ODD_CATEGORIES = {"Cc"}` → `test_odd_chars_blocked` hỏng |
| LC-T038 đk 2, SL-T038-2: bỏ Markdown ở cả hai phía, link chỉ giữ chữ, không đổi sang HTML | **ĐẠT** (còn SL-T041-6) | 8 dạng link CommonMark lạ trong bài đã escape như trang Soạn bài: đích trong `<…>`, có tiêu đề, ngoặc lồng, đích xuống dòng, link tham chiếu + dòng khai báo, ảnh, `javascript&#58;`. JSON-LD không còn `javascript`, địa chỉ, `](`, `**`, dấu huyền ngược. Còn lọt: link nằm trong đoạn mã (SL-T041-6) | 3 lần gỡ (bài không bỏ Markdown; hỏi/đáp không bỏ; link giữ địa chỉ) đều hỏng test |
| LC-T036-1: bỏ Cc, Cs, Co, Cn ở chữ AI, chữ người dùng | **ĐẠT** | 11 ký tự lạ qua `normalize_meta`, `check_title`, `siteseo_copy` (title, description): không còn ký tự loại Cc/Cf/Cs/Co/Cn, luôn ghi được UTF-8 | chỉ bỏ Cf → hỏng |
| SL-T036-10: chỉ loại trừ «xu hướng» | **ĐẠT** | «xu hướng» viết hoa, hai dấu cách, xuống dòng: không phải giá; «500 xu», «vài xu», «200.000đ», «1tr5», «giá rẻ» vẫn là giá. «2 đô vật» vẫn `xfail` đúng điều kiện | bỏ `(?!\s+hướng)` → hỏng |
| SL-T036-12: cắt độ dài trong `has_link`, `mentions_price` | **ĐẠT** | chữ 1.000 ký tự dò 0,04 giây; từ 1.001 ký tự trả «có» ngay, 50.000 ký tự 0,01 giây | không cắt / không đo lại sau NFKC → hỏng |
| LC-T040-1: dò giá mọi vị trí, bỏ qua chỗ nằm trọn trong từ khóa | **ĐẠT** (còn SL-T041-3) | 7 ca: giá vắt qua mép sau và mép trước từ khóa, giá ngoài từ khóa, «quận 1» + «1 triệu», giá nằm trọn trong từ khóa (giữ) | quay về «xóa từ khóa rồi dò» → hỏng |
| SL-T040-1: title 49 ký tự | **ĐẠT** (còn SL-T041-2 về cách gọi) | title AI 49 ký tự được nhận, «dài vừa (không còn chỗ gắn đuôi thương hiệu)» | bỏ ngoại lệ / bỏ điều kiện «chưa có đuôi» → hỏng |
| Nối `[meta]`, `find_avoided` bỏ từ khóa ra | **ĐẠT** (còn SL-T041-3, -7) | qua `ContentWriter.meta` với AI giả: «uy tín» ngoài từ khóa bị bỏ, nằm trong từ khóa «sửa cửa sắt uy tín» thì giữ; đuôi lấy từ file | 5 lần gỡ (không nối avoid, không nối đuôi, không ngoại lệ từ khóa, `_ai_text` không dò, bỏ ranh giới từ) → đều hỏng |
| SL-T037-5: file cache bận ghi dở không làm treo | **ĐẠT** | đo lại bằng script của Thợ Máy trên máy này: `get` khi kết nối khác giữ `BEGIN IMMEDIATE` + ghi: **1,19 giây**; bản sao gỡ sửa (`_WRITE_TIMEOUT = 5`): **5,53 giây**; `BEGIN EXCLUSIVE` 1,6 giây cả hai | `_WRITE_TIMEOUT = 5` → `test_pending_write_elsewhere_does_not_hang` hỏng |
| LC-T039 đk 2a: chỉ `_run("links", …)` rồi `check_suggestions`, không `web_search` | **ĐẠT** | AI giả trả trường thừa `href`, `url`, ID ngoài danh sách, cụm `[bản lề](javascript:…)`, `<b>…</b>`: chỉ gợi ý đúng được nhận, 3 câu báo cố định không chép chữ AI; lời dặn chỉ có «- ID 11: tiêu đề», không địa chỉ, slug, `http`; `[tasks.links]` bật `web_search` thì từ chối trước khi gọi AI. `config/ai.toml` `[tasks.links]` không có `web_search` | bỏ từ chối `web_search` → hỏng |
| LC-T039 đk 2b: nháp lưu `asdict(InternalLink)`, đọc lại qua `InternalLink(**d)` | **ĐẠT** | JSON nháp có đúng 4 khóa `section, anchor, post_id, use`; mở lại dựng `InternalLink`, chèn qua `apply_links` với địa chỉ lấy từ danh sách bài | không dựng `InternalLink` / `post_id` không strict → hỏng |

Thêm: `site_listing` không báo «chưa kết nối», không bắt `WordPressError`, `siteseo_copy` không chặn, `find_faq` tính cả mở bài, khối SEO hỏng làm hỏng cả nháp, liên kết hỏng làm hỏng cả khối SEO, không cắt 20 bản, không cắt 500 ký tự: **mọi lần gỡ đều bị bắt (28/28)**.

### 2. Trường SEO trong nháp

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Nháp khuôn 2 đúng như `main` lưu, có ảnh | **ĐẠT** | Nháp lưu bằng code hiện tại rồi bỏ khóa `seo` (khác biệt duy nhất của `DraftSnapshot` ở T-041, đã đối chiếu diff): mở được, ảnh đã chọn giữ nguyên, `dropped_images == 0`, SEO trống (`test_v2_draft_as_saved_by_main_opens_with_image_and_empty_seo`) |
| Nháp khuôn 1 | **ĐẠT** | JSON khuôn 1 như T-016/T-021 lưu: mở được, SEO trống (`test_v1_draft_opens_with_empty_seo`) |
| Khối SEO hỏng / sửa tay | **ĐẠT** | SEO hỏng (`current = -1`) và ảnh hỏng (`../`) trong cùng nháp: SEO về trống, ảnh bị bỏ và đếm 1, chữ giữ nguyên. SEO hỏng bỏ **lặng lẽ** (không đếm), đúng như Thợ Máy ghi ở Rủi ro |
| Không lưu địa chỉ link | **ĐẠT** | Khối SEO đã lưu không có `http`, `href`, khóa `link` |
| Giới hạn 20 bản, 500 ký tự, 30 liên kết | **ĐẠT** (lỗi SL-T041-4) | Test của Thợ Máy + gỡ sửa bị bắt. Cắt 20 bản thì có thể cắt mất bản đang dùng (SL-T041-4) |

### 3. Hàm cho Họa Sĩ, gọi như giao diện sẽ gọi

| Hàm | Kết quả | Bằng chứng |
|---|---|---|
| `site_listing` | **ĐẠT** | `WordPressClient` thật nối site giả (`fake_wordpress`) trả 401, 403 (HTML), 500, 200 nhưng là HTML, JSON không phải danh sách, mất kết nối, hết giờ, lỗi SSL; cả `get` và `refresh` (16 ca): không ném lỗi, `index` là `None`, câu báo mở đầu «Chưa tải được danh sách bài đã đăng.» kèm câu cố định của client, không chép mật khẩu giả, lời máy chủ (`<script>`, `javascript:`, địa chỉ), hay `WORDPRESS_URL`. Chưa kết nối: `MSG_NOT_CONNECTED`, không tạo file cache, slug/kiểm trùng/chép SiteSEO vẫn chạy |
| `ContentWriter.meta` | **ĐẠT** | AI giả trả title có `<img onerror>`, `%%sitename%%`: bị bỏ, báo «Các meta title AI gợi ý đều không đạt…»; từ khóa rỗng: «Chưa có từ khóa chính…». Riêng shortcode lọt: SL-T041-1 |
| `ContentWriter.internal_links` | **ĐẠT** | Như LC-T039 đk 2a ở trên; 0,02 giây |
| `check_title_duplicates`, `check_slug_duplicates`, `check_description_duplicates` | **ĐẠT** (lưu ý U1) | Câu báo chứa nguyên văn tiêu đề bài trên site (kể cả `<img onerror>`, `[…](javascript:…)`): đúng như mô tả, Họa Sĩ phải hiện bằng chữ thuần (điều kiện LC-T036 số 5) |
| `build_article_faq` | **ĐẠT** (lỗi SL-T041-5, -6) | Bài đã escape như trang Soạn bài dựng được JSON-LD chữ thuần; bài không có mục Hỏi đáp: `MSG_NO_FAQ`. 1.000 / 10.000 câu hỏi: dừng ở 21 cặp, 0,1 / 1,1 giây |
| `siteseo_copy`, `make_slug`, `check_slug` | **ĐẠT** (lỗi SL-T041-1) | Title gắn đuôi đúng, trường bị Chặn là `None` |

### 4. Soát R5 các test cũ bị đổi

| Test | Đánh giá |
|---|---|
| Gỡ dấu `xfail` (5 test, 13 ca): `test_r2_public_detectors_linear`, `test_lone_surrogate_blocked`, `test_plain_answer_matches_markdown_formatted_article`, `test_lc1_price_across_keyword_edge_is_dropped`, `test_sl_t040_1_title_of_49_chars_is_not_short` | **Đúng R5**: diff chỉ xóa dòng `@pytest.mark.xfail(…)`, thân test giữ nguyên |
| `test_r2_xu_huong_not_price`: tách ca «2 đô vật» thành `test_r2_do_vat_not_price` (`xfail(strict=True)`) | **Đúng R5**: không bỏ ca nào, «đô vật» vẫn được canh; khớp điều kiện LC-T036 số 2 (chỉ loại trừ «xu hướng») |
| `test_bold_answer_raw_markdown_passes_without_asterisks` | **Đúng R5**: test cũ ghi lại hành vi lỗi SL-T038-2 (JSON-LD còn `**`); nay khẳng định JSON-LD bằng đúng câu chữ thường, **chặt hơn** |
| `test_read_note_is_above_meta_and_true` (file của tôi ở T-040) | **Đúng R5**: thêm khẳng định cụm `avoid` bị bỏ khi dùng `[meta]` thật, giữ khẳng định cũ cho trường hợp không truyền `avoid` |
| `test_lone_surrogate_output_is_at_least_valid_json` | Không do Thợ Máy đổi, nhưng nay thành test rỗng; tôi sửa thành khẳng định `json_ld is None` (mục Đã thay đổi) |

## Lỗi và góp ý

| Mã | Mức | Mô tả | Ai sửa | Trước khi Họa Sĩ nối? |
|---|---|---|---|---|
| SL-T041-1 | Thấp | Chữ SEO mà client WordPress **từ chối ghi** (`client.py:1537` `_seo_text`: shortcode `[gallery]`, `[code_snippet_source id=3]`, `[<>code_snippet id=1]`, `<1>`, mã ký tự thiếu `;` như `&#37`) vẫn được `siteseo_copy` (`meta.py:731`) trả ra để **chép tay** sang SiteSEO, và bộ kiểm gợi ý AI (`_ai_text`, `meta.py:620`) nhận, cả title lẫn description. Đường «chép tay» chính là đường dự phòng khi chưa bật ghi SEO, cùng ô SiteSEO với `set_seo_meta`. Hậu quả chỉ có nếu SiteSEO chạy shortcode trong meta (chưa xác minh, T-059 bước 4) và người dùng không để ý chữ lạ, nên Thấp; nhưng T-061 đã chọn chặn hẳn ở đường ghi, hai đường nên giống nhau | Thợ Máy (`meta.py`): một hàm kiểm chữ SEO dùng chung (tách từ `client._seo_text`) cho `_ai_text` (bỏ gợi ý) và `siteseo_copy` (trả `None` + câu báo) | **Có**: Họa Sĩ hiện gợi ý AI và nút chép bằng hai hàm này |
| SL-T041-2 | Thấp | `check_title(title, suffix)` (`meta.py:160`) chấm đúng chữ được truyền vào. «Hàm cho Họa Sĩ» dặn hiện ô sửa không đuôi (`strip_brand`) và kiểm ô bằng `check_title(title, suffix)`: theo đúng hướng dẫn thì title 38–48 ký tự ra «hơi ngắn» dù title gửi đi (gắn đuôi) là 50–60 «dài vừa», còn 49 lại «dài vừa». Người dùng gõ thêm một chữ thì cảnh báo đổi ngược | Thợ Máy: trong `check_title`, title chưa có đuôi mà gắn được thì chấm `with_brand(title, suffix)` (hàm này chạy lại không đổi gì nên `accept_ai_title`, `siteseo_copy` không ảnh hưởng; test `(48, None, True)` của Thợ Máy đổi theo). Hoặc ghi rõ «truyền `with_brand(…)`» trong hướng dẫn và Chỉ Huy bỏ test xfail này | **Có** |
| SL-T041-3 | Thấp | Từ khóa gõ không dấu («sua cua uy tin hcm», «cua cuon gia re», «sua cua cuon chuyen nghiep»): `has_keyword` (`meta.py:505`) so không dấu nên nhận title có dấu, nhưng ngoại lệ «cụm nằm trong từ khóa» (`_KeywordSpans`, `meta.py:547`) so có dấu, nên «uy tín», «giá rẻ», «chuyên nghiệp» trong chính từ khóa bị tính là cụm nên tránh / nói giá: mọi gợi ý bị bỏ, `meta()` báo «đều không đạt». Cột từ khóa trong `docs/plan/ke_hoach_6_thang_chi_tiet.md` viết không dấu («gia sua cua»). Có dấu thì đúng (test đối chứng qua) | Thợ Máy: tìm chỗ xuất hiện của từ khóa trên chữ đã bỏ dấu (bỏ dấu từng ký tự giữ nguyên vị trí) | Không (nên sửa cùng đợt) |
| SL-T041-4 | Thấp | `DraftMetaVersions._keep_recent` (`drafts.py:413`) giữ 20 bản mới nhất mà không giữ bản đang dùng: người dùng chọn bản cũ (ví dụ bản tự viết), giao diện thêm gợi ý AI cho tới quá 20 bản, thì bản đang dùng bị bỏ và `current` nhảy sang bản khác («Bản tôi tự viết» thành «Gợi ý AI 0»), nháp lặng lẽ đổi meta. Chỉ xảy ra nếu giao diện thêm bản mà không chuyển `current` sang bản mới | Thợ Máy: khi cắt, luôn giữ bản đang dùng (bỏ bản cũ nhất khác) | **Có**: Họa Sĩ thiết kế «thêm bản / quay lại» dựa vào đây |
| SL-T041-5 | Thấp | `_question_of` (`schema.py:510`) nhận **mọi** tiêu đề con trong mục Hỏi đáp là câu hỏi, kể cả «### Lưu ý trước khi đọc» (docstring `find_faq` nói «`### …?`»). JSON-LD có `Question` không phải câu hỏi (Google yêu cầu là câu hỏi) | Thợ Máy: tiêu đề con chỉ là câu hỏi khi chữ thuần kết thúc «?»/«？» như đoạn một dòng | Không (JSON-LD chỉ xem trước ở Giai đoạn 4; sửa trước khi đưa lên site) |
| SL-T041-6 | Thấp | Link nằm trong đoạn mã: `` `[x](javascript:alert(1))` `` hay ``` ``…`` ```. `plain_text` (`schema.py:211`) bỏ dấu `\` của app (`](` hiện lại), `strip_markdown_links` cố ý bỏ qua đoạn mã, rồi `_strip_inline` bỏ dấu huyền ngược, nên JSON-LD mang nguyên «[x](javascript:alert(1))». Chỉ là chữ (không thành link, trùng chữ hiện trong thẻ `<code>` của trang), nhưng trái nguyên văn điều kiện LC-T038 đk 2 | Thợ Máy: còn cú pháp link sau `plain_text` thì Chặn (hoặc bỏ cả đoạn mã khỏi FAQ); Lá Chắn cân nhắc mức | Không (xem trước); trước khi đưa schema lên site |
| SL-T041-7 | Thấp | `[meta].brand_suffix` nay có tác dụng (`workflow.py:295`) nhưng lời dặn ghi cứng «đuôi « \| Pro-Metal» (12 ký tự)… title 40-48 ký tự sẽ có đuôi… Ít nhất một cái dài 40-48 ký tự» (`prompts.py:316-320`). Đặt `brand_suffix = ""` (chú thích trong file cho phép) thì AI vẫn được bảo phần mềm sẽ gắn đuôi; đuôi dài 23 ký tự thì title 40–48 không gắn được nữa. Ngòi Bút đã báo trước ở đề xuất 1 T-040 | Thợ Máy (truyền đuôi vào `meta_prompt`) + Ngòi Bút (câu chữ theo độ dài đuôi; đuôi rỗng thì bỏ câu) | Không (chỉ khi đổi đuôi) |
| G1 | Góp ý | Lời dặn `prompts.py:319-320` còn ghi «title 49 ký tự không gắn được đuôi mà lại hơi ngắn»; từ T-041 code coi 49 là «dài vừa». Vô hại (AI vẫn tránh 49), sửa cùng SL-T041-7 | Ngòi Bút | Không |
| G2 | Góp ý | `build_article_faq` chạy `find_faq` trên cả bài **trước** khi kiểm độ dài (500.000 ký tự): đo bài 3 triệu ký tự (dán nhầm) mất khoảng 15 giây mỗi lần trang chạy lại. Kiểm độ dài trước | Thợ Máy | Không |
| G3 | Góp ý | Câu trả lời FAQ còn «[cần bổ sung: …]» vẫn vào JSON-LD, không cảnh báo. Nên Cảnh báo (hoặc Chặn) | Thợ Máy | Không |
| G4 | Góp ý | `select_candidates` **luôn** báo «Bài hướng dẫn chưa có trang dịch vụ đích (ghi trong phiếu giao bài)» vì app chưa có phiếu giao bài (`required=()`). Hiện ra mỗi lần thì khó hiểu với chủ dự án: Họa Sĩ không hiện câu này hoặc viết lại | Họa Sĩ | Khi nối |
| G5 | Góp ý | `TASK_EXAMPLES` (`seo_app/ai/registry.py:36`) chưa có `links` (và `meta`): máy nào `config/ai.toml` thiếu `[tasks.links]` chỉ được báo «thiếu mục», không có mẫu để chép như việc `alt` | Thợ Máy | Không |
| G6 | Góp ý | `tests/test_la_chan_t040.py` dòng 1 còn ghi «`xfail(strict=True)` tới khi sửa» (file của Lá Chắn, tôi không sửa) | Lá Chắn | Không |

### Cách tái hiện

```bash
uv run pytest tests/test_soi_loi_t041.py --runxfail -k sl_t041
```

Mong đợi: 0 hỏng. Thực tế: 17 hỏng, đúng chỗ khẳng định của từng lỗi:

- SL-T041-1 (5 ca): `siteseo_copy(...).title` là chữ có `[code_snippet_source id=3]`, `[gallery]`, `[<>code_snippet id=1]`, `<1>`, `&#37` thay vì `None`; ca đối chứng `test_client_refuses_these_seo_titles` cho thấy client từ chối cả 5.
- SL-T041-2 (3 ca): `check_title` của title 38, 43, 48 ký tự chưa gắn đuôi ra «Meta title hơi ngắn: 38 ký tự, nên 50–60 ký tự.» dù title gắn đuôi là 50, 55, 60 ký tự «dài vừa».
- SL-T041-3 (3 ca): `accept_ai_title("Sửa cửa uy tín HCM: …", "sua cua uy tin hcm", avoid=[meta].avoid)` là `None`; cùng câu với từ khóa có dấu thì được nhận.
- SL-T041-4: `DraftMetaVersions(versions=["Bản tôi tự viết", "Gợi ý AI 0", …, "Gợi ý AI 19"], current=0).text == "Gợi ý AI 0"`.
- SL-T041-5: `find_faq` trả `["Lưu ý trước khi đọc", "Cửa cuốn kêu to có sao không?"]`.
- SL-T041-6 (2 ca): JSON-LD có `"text": "Gõ [x](javascript:alert(1)) vào ô."`.
- SL-T041-7 (2 ca): lời dặn gửi AI vẫn có «40-48» khi `MetaRules(brand_suffix="")` hoặc đuôi 23 ký tự.

## Bằng chứng

Windows 11, Git Bash, worktree `wt-T-041`, code tại `c059b41`.

```
$ git pull                       # đầu phiên
Already up to date.              # HEAD c059b41, gốc main 2e04066

$ uv run pytest <37 file test liên quan, đúng danh sách trong báo cáo Thợ Máy>   # trước khi thêm test
2969 passed, 8 skipped, 8 xfailed in 962.82s (0:16:02)                       # = số Thợ Máy báo

$ uv run pytest tests/test_soi_loi_t038.py tests/test_soi_loi_t040.py tests/test_soi_loi_t041.py
388 passed, 17 xfailed in 14.45s

$ uv run pytest tests/test_soi_loi_t041.py
94 passed, 17 xfailed

$ uv run pytest tests/test_soi_loi_t041.py --runxfail -k sl_t041
17 failed, 94 deselected        # đúng 7 lỗi SL-T041-1 → -7

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # thư mục tạm: test mới + file mồi
# chỉ file mồi (tên có dấu, khóa AWS mẫu, mật khẩu giả) bị bắt, 4 mục; tests/test_soi_loi_t041.py: 0
```

Gỡ chỗ sửa trên bản sao (`mutate.py`, mỗi lần chạy các file test của phần đó với `-x`):

```
BẮT | LC-T038-1 Cs/Co/Cn                       BẮT | SL-T040-1 bỏ ngoại lệ 49 ký tự
BẮT | SL-T038-2 bài không bỏ Markdown          BẮT | SL-T040-1 bỏ điều kiện chưa có đuôi
BẮT | SL-T038-2 hỏi/đáp không bỏ Markdown      BẮT | avoid: không ngoại lệ từ khóa
BẮT | LC-T038-2 link giữ địa chỉ               BẮT | avoid: _ai_text không dò
BẮT | find_faq tính cả mở bài                  BẮT | avoid: bỏ ranh giới từ
BẮT | LC-T036-1 chỉ bỏ Cf                      BẮT | siteseo_copy không chặn
BẮT | SL-T036-10 xu hướng                      BẮT | [meta].avoid không nối vào meta()
BẮT | SL-T036-12 không cắt độ dài              BẮT | [meta].brand_suffix không nối
BẮT | SL-T036-12 không đo sau NFKC             BẮT | LC-T039-2a không từ chối web_search
BẮT | LC-T040-1 xóa từ khóa rồi dò             BẮT | LC-T039-2b DraftLink không dựng InternalLink
BẮT | SL-T037-5 ghi chờ 5 giây                 BẮT | LC-T039-2b post_id không strict
BẮT | site_listing không báo chưa kết nối      BẮT | SEO hỏng làm hỏng cả nháp
BẮT | site_listing không bắt WordPressError    BẮT | liên kết hỏng làm hỏng cả khối SEO
BẮT | không cắt 20 bản                         BẮT | không cắt 500 ký tự
# 28/28 bị bắt; bản sao trả về nguyên trạng sau mỗi lần (git status sạch)
```

Đo SL-T037-5 (`T-041-tho-may-scripts/busy_reserved.py` của Thợ Máy): `IMMEDIATE stale 1.19s`; trên bản sao gỡ sửa: `IMMEDIATE stale 5.53s`.

Ghi chú quy trình: trên **bản sao tạm của riêng tôi** (`wt-T041-sl-dotbien`, không ai khác dùng, đã gỡ sau khi xong) có một lần tôi trả file về bằng `git checkout --`; không đụng `wt-T-041` hay thư mục của phiên khác.

## Đối chiếu việc được giao

- [x] 1. Từng điều kiện làm thật, thử độc lập, gỡ chỗ sửa trên bản sao: 28/28 bị bắt (mục 1)
- [x] 2. Trường SEO trong nháp: khuôn 1, 2 (có ảnh) mở được, khối SEO hỏng bỏ riêng, không lưu địa chỉ, giới hạn 20 bản / 500 ký tự (mục 2; SL-T041-4)
- [x] 3. Hàm cho Họa Sĩ gọi như giao diện: AI giả, site giả, câu lỗi tiếng Việt, không treo, không lộ chữ thô ngoài tiêu đề site đã mô tả (mục 3)
- [x] 4. Soát R5 test cũ bị đổi và `xfail` gỡ (mục 4)
- [x] 5. Lỗi mới: `tests/test_soi_loi_t041.py`, `xfail(strict=True)`, SL-T041-1 → -7
- [x] Test liên quan và `uv run ruff check .` sạch; không gọi AI, WordPress hay mạng thật

## Rủi ro và điểm cần chú ý

- **Chưa kiểm giao diện**: U1 (hiện tiêu đề site, câu báo bằng chữ thuần), LC-T038 đk 3 (`st.code`), công tắc ghi SEO là phần Họa Sĩ, kiểm ở lượt sau.
- Mọi câu báo kiểm trùng có nguyên văn tiêu đề bài trên website (dữ liệu chưa tin cậy, thử với `<img onerror>`, `[…](javascript:…)`): Họa Sĩ **phải** hiện bằng chữ thuần.
- SL-T041-1 phụ thuộc câu hỏi chưa trả lời «SiteSEO có chạy shortcode trong meta không» (T-059 bước 4). Nếu T-059 xác nhận không chạy thì hậu quả còn nhỏ hơn, nhưng vẫn nên để hai đường giống nhau.
- Test SL-T041-2 giả định cách sửa trong code. Nếu Chỉ Huy chọn chỉ sửa hướng dẫn cho Họa Sĩ thì bỏ test này (nó sẽ không bao giờ XPASS).
- `tests/test_soi_loi_t041.py` không thay cho test giao diện `AppTest` của Họa Sĩ.

## Đề xuất

1. **Thợ Máy (cùng phiếu, trước khi Họa Sĩ nối):** SL-T041-1, -2, -4. Sửa xong thì gỡ `xfail` tương ứng (test tự báo XPASS).
2. **Thợ Máy (cùng phiếu hoặc trước khi gộp):** SL-T041-3, -5, -6, G2, G3, G5.
3. **Ngòi Bút + Thợ Máy (phiếu sau, khi cần đổi đuôi):** SL-T041-7 và G1.
4. **Họa Sĩ:** dùng «Hàm cho Họa Sĩ» kèm G4; kiểm ô tiêu đề theo cách sửa của SL-T041-2.
5. Script kiểm (gỡ sửa, thử meta, thử schema, thử `site_listing`, thử hàm cho Họa Sĩ) để ở thư mục ghi chú chung `T-041-soi-loi-scripts/`, chạy trong worktree bằng `PYTHONUTF8=1 uv run python <script>`.

## Phần giao diện và lượt 3 (Soi Lỗi lượt 2, 2026-10-27)

Kiểm trên đầu nhánh `433c533`: Thợ Máy lượt 2 (sửa SL-T041-1 → -7), gộp `main` (T-056, T-085, T-086, T-087), giao diện Họa Sĩ lượt 1–2 (`app/views/write.py`, `app/views/wordpress.py`), Thợ Máy lượt 3 (sửa lỗi lùi ký tự điều khiển: `client._seo_text`, `check_title`/`check_description`, `DraftMetaVersions`, gợi ý AI, đuôi thương hiệu). Không sửa code ứng dụng.

**Kết luận cả phiếu: ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình. SL-T041-1 → -7 **đóng**. **4 lỗi Thấp mới** (SL-T041-8 → -11, test `xfail(strict=True)`), 3 góp ý. **Không lỗi nào phải sửa trước Lá Chắn**: chuyển Lá Chắn được ngay. Nên sửa trước khi gộp `main` (đều nhỏ): SL-T041-9, -10, -11; SL-T041-8 cần Lá Chắn quyết (liên quan điều kiện LC-T036-1 về ký tự «chưa gán»).

### Tóm tắt (cho chủ dự án)

- Bước **4 · SEO** chạy thật đúng yêu cầu: AI gợi ý và viết lại riêng từng ô, quay lại bản trước / tới bản sau, đếm ký tự (tiêu đề tính cả đuôi « | Pro-Metal»), nhãn màu Nên / Cảnh báo / Chặn, đường dẫn, kiểm trùng với bài đã đăng, liên kết nội bộ, dữ liệu Hỏi đáp cho Google, tự lưu vào nháp, khung chép sang SiteSEO, công tắc «Ghi SEO lên website» mặc định tắt. Chưa kết nối WordPress hay chưa có khóa AI thì vẫn dùng được phần còn lại.
- Tôi mở **app thật** trên máy (không kết nối website thật) với một bài nháp bị sửa tay rất "vô lý" (chữ có thẻ HTML, lệnh WordPress, ký tự vô hình, đường dẫn «/..»): trang vẫn chạy, không lỗi, mọi ô sai đều đỏ «Chặn» và không chép được.
- 7 lỗi nhỏ lần trước đã sửa xong. Lỗi lùi Họa Sĩ tìm ra (chữ có ký tự điều khiển bị lặng lẽ sửa rồi ghi) đã sửa: nay bị chặn kèm lời nhắc ở ô gõ, khung chép, gợi ý AI, nháp sửa tay và khi ghi lên website. Tiếng Việt, tab, xuống dòng, emoji quen thuộc không bị chặn.
- 4 lỗi nhỏ mới, không cái nào nguy hiểm:
  1. Emoji rất mới (có từ năm 2024) trong tiêu đề, mô tả bị chặn nhầm là «ký tự lạ (không nhìn thấy)».
  2. Từ khóa chính có ký tự lạ (thường do dán): phần mềm bỏ luôn cả tiêu đề, mô tả khi ghi lên website, hoặc lặng lẽ bỏ ký tự rồi ghi; không báo trước.
  3. Bước Xuất bản: mở lại bài ở bước này rồi bật «Ghi SEO lên website», màn hình có lúc vừa báo «SEO đã sẵn sàng» vừa báo «sẽ không ghi tiêu đề».
  4. Tiêu đề có chữ dạng lệnh WordPress (ví dụ `[gallery]`): nhãn dưới ô vẫn xanh «Nên», chỉ khung chép báo không chép được (phần mềm vẫn không chép, không ghi chữ này lên website).

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t041.py` | Thêm 32 ca (24 qua, 8 `xfail(strict=True)` cho SL-T041-8 → -11), mục «5. giao diện và lượt 3»: nháp khuôn 1/2 và khối SEO sửa tay vô lý ở trang thật, chưa có khóa AI, mở nháp khác không lẫn SEO, khoảng trắng / ký tự vô hình / emoji qua mọi đường, khung chép từ chối đúng chữ client từ chối. Dùng chung AI giả, WordPress giả của `tests/test_t041_seo_ui.py`. Commit `92d656d` |
| `docs/team/reports/T-041-soi-loi.md` | Mục này |

Không sửa code ứng dụng, `config/`, test của agent khác.

### Kiểm từng mục

| # | Việc (tin nhắn Chỉ Huy B) | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | SL-T041-1 → -7 đã đóng, gỡ `xfail` đúng R5 | **ĐẠT** | `git diff 85b06b6..HEAD -- tests/test_soi_loi_t041.py`: chỉ 35 dòng xóa (7 khối `@pytest.mark.xfail(...)`), 0 dòng thêm; 17 ca SL-T041-1 → -7 qua. Test cũ lượt 2 đổi: 4 chỗ thêm `suffix=""` (`test_onpage_meta.py` 2, `test_soi_loi_t036.py` 2) để giữ đúng ý «chấm chữ trần», không đổi khẳng định: đúng R5. Lượt 3 chỉ đổi test của chính Thợ Máy theo hành vi mới (đổi tên `…_drops_…` → `…_is_blocked`/`…_falls_back…`), không đổi test của người khác |
| 2 | Giao diện bước SEO, yêu cầu 1–6 + ghi chú | **ĐẠT** (lỗi SL-T041-10, -11) | 32 test `AppTest` của Họa Sĩ (`tests/test_t041_seo_ui.py`) qua, đọc lại từng test: AI gợi ý / 🔄 từng ô / ↶ ↷ / bản mới khi tự sửa / đếm NFC kèm đuôi / Chặn không chép / slug / xem trước escape / kiểm trùng chữ thuần / liên kết + cột «Dùng» / tải lại danh sách / schema chỉ `st.code` / lưu, mở lại / đổi trang / công tắc mặc định tắt / ghi sau khi tạo nháp, hỏi lại trạng thái / không ghi theo mã bài trong nháp / lỗi lạ không vỡ trang / dòng SiteSEO trang WordPress. Tôi thêm: chưa có khóa AI thì ba nút AI mờ, vẫn gõ, đếm, chép được; mở nháp khác cùng phiên không lẫn bản meta, slug, công tắc của nháp trước. Lỗi: nhãn dưới ô xanh khi khung chép từ chối (SL-T041-11); dòng kiểm bước 5 trái công tắc ở lần bật đầu (SL-T041-10) |
| 3 | Lỗi lùi lượt 3: chặn có câu báo ở mọi đường, không chặn oan | **ĐẠT phần lớn** (lỗi SL-T041-8, -9) | Bảng «Từng đường» bên dưới |
| 4 | Nháp cũ mở được; khối SEO sửa tay vô lý không làm trang lỗi | **ĐẠT** | `AppTest` trang thật: khuôn 1 (như T-016/T-021) và khuôn 2 (như `main` lưu, có ảnh) mở, bước SEO trống, slug gợi ý từ từ khóa, AI gợi ý được. Khối SEO vô lý (5 bản tiêu đề: `<script>`, 500 ký tự, `[gallery ids=1]`, ESC, `%%sitename%%`, bản đang dùng có ESC; mô tả 520 ký tự có `<b>`; slug `Cửa Sắt/../../etc`; liên kết tới bài 424242 không có; một liên kết sai khuôn; «Dùng schema» khi bài không có Hỏi đáp): không lỗi, 3 nhãn đỏ, 3 dòng «chưa chép được», không khung chép nào, không HTML thô, bảng «bài #424242», liên kết sai khuôn bị bỏ riêng, không có ô schema; bật ghi SEO rồi gửi nháp: lệnh ghi chỉ có từ khóa chính. Trình duyệt thật: như trên, console không lỗi |
| 5 | App thật | **ĐẠT** | Mục «Thử trên trình duyệt thật» bên dưới |

**Từng đường của chữ có ký tự lạ** (thử bằng `check_title`, `check_description`, `siteseo_copy`, `accept_ai_title`, `DraftMetaVersions`, `client._seo_text`, và ở trang thật):

| Đường | Ký tự điều khiển (ESC, NUL…) | Ký tự riêng / chưa gán (Co, Cn) | Ký tự vô hình định dạng (Cf: U+200B, BOM, gạch mềm) | Khoảng trắng (tab, xuống dòng, CRLF, VT, FF, FS, NEL, NBSP, U+2028, U+3000) |
|---|---|---|---|---|
| Gõ tay / dán vào ô title, description | Chặn + câu «… Xóa ô rồi gõ lại chữ thường» | Chặn + cùng câu | Bỏ, không báo (thiết kế T-036) | Gộp thành dấu cách |
| Khung «Chép sang SiteSEO» | Không chép, câu lý do | Không chép | Chép chữ đã bỏ ký tự vô hình | Gộp |
| Gợi ý AI | Bỏ gợi ý | Bỏ gợi ý | Bỏ ký tự, nhận | Gộp |
| Nháp sửa tay | Giữ ký tự để bộ kiểm Chặn (đã thử trên trang thật) | Giữ, Chặn | Giữ, bộ kiểm bỏ | Gộp |
| Ghi lên website (client), title/description | Không gửi (đã Chặn ở bước trước); client cũng tự chặn | Không gửi | Bỏ (thiết kế T-042: `_drop_invisible`) | Gộp |
| **Từ khóa chính** (gõ ở bước Chuẩn bị, đi thẳng vào client) | **Client từ chối cả lệnh ghi SEO**, mất cả tiêu đề, mô tả hợp lệ (SL-T041-9) | **Lặng lẽ bỏ ký tự rồi ghi** (SL-T041-9) | Bỏ (thiết kế) | Gộp |
| Đuôi thương hiệu trong `config/content.toml` | Dùng « \| Pro-Metal» mặc định, không báo (như đuôi có thẻ HTML, `%%`) | như trái | Bỏ ký tự | Gộp |

Không chặn oan: chữ Việt dạng tổ hợp (NFD), emoji ⭐ ✅ 🫨, ❤️ có bộ chọn biến thể: Nên. **Chặn oan:** emoji Unicode 16 (SL-T041-8).

«Một ca chưa xử lý» của Họa Sĩ (từ khóa chính có ký tự điều khiển làm client từ chối cả lệnh ghi SEO): tôi xếp **Thấp** và gộp vào **SL-T041-9**, cùng nhánh «ký tự riêng / chưa gán trong từ khóa bị lặng lẽ bỏ rồi ghi» mà tôi tìm thêm. Thấp vì: bài nháp vẫn tạo, câu báo nói đúng lý do, người dùng còn khung chép tay; từ khóa có ký tự lạ hiếm (gõ ở bước đầu). Nhưng trái nguyên tắc lượt 3 «không lặng lẽ sửa rồi ghi» và người dùng không được báo trước.

### Lỗi và góp ý (lượt 2)

| Mã | Mức | Mô tả | Ai sửa | Trước Lá Chắn? |
|---|---|---|---|---|
| SL-T041-8 | Thấp | Emoji mới hơn bảng Unicode của Python 3.12 (15.0) là ký tự «chưa gán» (Cn) với Python: tiêu đề, mô tả có emoji Unicode 16 (ví dụ U+1FAE9, U+1FAC6, có từ 2024, đã có trên điện thoại) bị **Chặn** với câu «có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ nơi khác)» (`meta.py` `has_odd_chars`); gợi ý AI có emoji đó bị bỏ; câu hỏi/trả lời FAQ có nó bị Chặn (`schema.py` `_ODD_CATEGORIES`). Client WordPress ghi được chữ này (`seo_write_problem` rỗng). Câu báo sai («không nhìn thấy» với emoji nhìn thấy rõ) | Thợ Máy, **sau khi Lá Chắn quyết**: điều kiện LC-T036-1 đòi bỏ/Chặn cả Cn. Cách gợi ý: chỉ coi «không phải ký tự» (U+FDD0–FDEF, U+xxFFFE/FFFF) là lạ, Cn khác cho qua (có thể là ký tự mới); hoặc giữ Chặn nhưng câu báo nói «biểu tượng mới phần mềm chưa nhận ra» | Không (Lá Chắn quyết hướng sửa) |
| SL-T041-9 | Thấp | Từ khóa chính đi thẳng vào `set_seo_meta` (`write.py` `seo_request`: `"focus_keyword": keyword()`), không qua bộ kiểm meta: (a) có ký tự điều khiển thì client ném lỗi cho **cả** lệnh ghi, tiêu đề và mô tả hợp lệ cũng không được ghi (= «Một ca chưa xử lý» của Họa Sĩ); (b) có ký tự riêng / chưa gán thì client lặng lẽ bỏ ký tự rồi ghi (client chỉ chặn Cc; `normalize_meta` bỏ Co, Cn); (c) bước Xuất bản không báo trước | Họa Sĩ (`seo_request`, `seo_toggle`): kiểm từ khóa bằng `seo_write_problem` + `has_odd_chars`, hỏng thì bỏ riêng từ khóa (vào `skipped`, câu kết quả nói «Không ghi Từ khóa chính…»), báo trước ở công tắc | Không; nên sửa trước khi gộp |
| SL-T041-10 | Thấp | `step_publish` vẽ dòng kiểm SEO (`seo_check`, không tải danh sách bài) **trước** công tắc; công tắc bật thì `seo_request` mới tải danh sách. Phiên mới mở nháp ở bước Xuất bản, tiêu đề trùng hệt bài đã đăng: lần bật công tắc đó màn hình có cùng lúc «✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng» và «Sẽ không ghi Tiêu đề SEO: ở bước SEO đang báo «Chặn»»; lần chạy sau mới đúng. Ghi lên website vẫn đúng (không ghi tiêu đề trùng) | Họa Sĩ: công tắc bật thì tải danh sách (`published_listing()`) trước khi vẽ dòng kiểm | Không; nên sửa trước khi gộp |
| SL-T041-11 | Thấp | Nhãn dưới ô meta (`meta_field`: `check_title`/`check_description` + kiểm trùng) không tính việc client từ chối ghi (`seo_write_problem`): tiêu đề có `[gallery]`, «<2m», «&#37» hiện **xanh «Nên · 51 ký tự»** và xem trước Google hiện cả tiêu đề kèm đuôi, trong khi khung chép bên cạnh báo «Tiêu đề SEO: chưa chép được…» (đã thấy trên trình duyệt thật). Docstring `test_blocked_title_is_red_and_not_copyable` nói dạng shortcode «hiện mức Chặn», nhưng test chỉ kiểm không chép được. Không sai về an toàn (không chép, không ghi) | Họa Sĩ (`meta_field` dùng kết quả kiểm đã nâng mức như `siteseo_copy`, ví dụ dùng `copy.checks` của `final_seo`) hoặc Thợ Máy mở hàm công khai thay cho `_writable` | Không; nên sửa trước khi gộp |
| G7 | Góp ý | Ký tự vô hình định dạng (Cf) bị bỏ lặng lẽ là đúng thiết kế T-036/T-042, nhưng hai ca có thấy khác: dấu nối emoji (U+200D) bị bỏ làm emoji gia đình tách thành 3 hình riêng (đã thử: chữ chép không còn U+200D); dấu đảo chiều (U+202E…) có thể làm ô sửa hiện chữ ngược trong khi chữ chép/ghi là chữ xuôi (suy luận, chưa thử trên trình duyệt) | Ghi nhận; Lá Chắn xem có cần Chặn riêng dấu đảo chiều | Không |
| G8 | Góp ý | Chú thích `brand_suffix` trong `config/content.toml` liệt kê «dài quá 25 ký tự, có thẻ HTML hay «%%»» là bị bỏ qua; lượt 3 thêm «có ký tự điều khiển, ký tự lạ» mà chú thích chưa ghi | Thư Ký / Thợ Máy, một dòng | Không |
| G9 | Góp ý | Ghi SEO chạy trong cùng lượt gửi nháp (sau `record_outcome`), thêm tối đa 4 lệnh, mỗi lệnh chờ tối đa 30 giây; lần chạy mới của T-086 chỉ đợi lượt gửi tối đa 60 giây. Website chậm thì có thể quá giờ đợi: nháp đã ghi «đã gửi» nên an toàn, chỉ câu kết quả SEO có thể không hiện. Suy luận, chưa thử | Họa Sĩ xem khi làm T-089 | Không |

### Cách tái hiện (lượt 2)

```bash
uv run pytest tests/test_soi_loi_t041.py --runxfail -k "sl_t041_8 or sl_t041_9 or sl_t041_10 or sl_t041_11"
```

Mong đợi: 0 hỏng. Thực tế: 8 hỏng, đúng chỗ khẳng định:

- SL-T041-8: `check_title("Cửa sắt bị xệ 🫩 tự kiểm tra hay nên gọi thợ?")` (U+1FAE9) ra `Level.BLOCK`. Test bỏ qua trên Python đã biết Unicode 16 (3.14 trở lên).
- SL-T041-9: từ khóa `sửa cổng<ESC> inox`, bật ghi SEO, gửi nháp: **không có lệnh ghi SEO nào** (`expected 1, got 0`); từ khóa `sửa cổng<U+E000> inox`: lệnh ghi có `focus_keyphrase` đã bị bỏ ký tự; bật công tắc không có câu báo trước về từ khóa.
- SL-T041-10: sau khi bật công tắc, trang có «✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng» cùng câu «Sẽ không ghi Tiêu đề SEO…».
- SL-T041-11 (3 ca): huy hiệu đầu tiên là `:green-badge[Nên · 51 ký tự]` cho `[gallery]`, «<2m», «&#37».

### Thử trên trình duyệt thật

Worktree `wt-T-041`, cổng 8503; **không** khai báo WordPress (không gọi website nào), không có khóa AI. Mật khẩu thử ngẫu nhiên tạo trong phiên (file tạm, đã xóa). Cấu hình tạm `seo-app-t041-soiloi` thêm vào `D:\ProMetal-ToolSEO\.claude\launch.json` rồi **trả đúng bản cũ ngay sau khi app chạy** (SHA-256 trước/sau `a5607e8c…f169`); không chạy `seo-app-main`. Một nháp có khối SEO vô lý (như test mục 4) ghi vào `data/` của worktree (trước đó không có `data/`), xong đã xóa `data/`, dừng app, cổng 8503 đóng. Script: `T-041-soi-loi-scripts/setup_soi_loi.py`.

- Mở nháp, bước SEO: dòng «Chưa kết nối WordPress…»; ô tiêu đề (bản 4/5, có ESC) «Chặn · 29 ký tự» kèm câu nhắc xóa ô gõ lại; mô tả có `<b>` hiện thành chữ thường, «Chặn · 499 ký tự»; slug `Cửa Sắt/../../etc` «Chặn»; xem trước Google hiện `<b>` là chữ (đã escape); khung chép: 3 dòng «chưa chép được» kèm lý do; bảng liên kết «không có trong bài → bài #424242»; console trình duyệt: không lỗi.
- Gõ «Sửa cổng inox [gallery] tại nhà Tân Phú» vào ô tiêu đề: nhãn xanh «Nên · 51 ký tự», xem trước Google «Sửa cổng inox [gallery] tại nhà Tân Phú | Pro-Metal», khung chép «Tiêu đề SEO: chưa chép được. Meta title có chữ dạng shortcode WordPress…» (SL-T041-11).

### Bằng chứng (lượt 2)

```
$ git pull                       # wt-T-041, đầu phiên
Already up to date.              # HEAD 433c533

$ uv run pytest tests/test_soi_loi_t041.py
135 passed, 8 xfailed in 64.83s   # 8 = SL-T041-8 → -11

$ uv run pytest tests/test_soi_loi_t041.py --runxfail -k "sl_t041_8 or sl_t041_9 or sl_t041_10 or sl_t041_11"
8 failed, 135 deselected

$ uv run pytest <62 file liên quan: mọi file test gọi hàm lượt 2–3 đổi (normalize_meta, check_title,
    check_description, siteseo_copy, resolve_brand_suffix, DraftMetaVersions, meta_prompt, plain_text,
    find_faq, build_article_faq, _seo_text, set_seo_meta, WordPressClient), test_t041_*, client
    WordPress T-042/T-060/T-085, T-061, trang Soạn bài (test_app_*, T-056, T-086), trang WordPress>
    # code ứng dụng tại 433c533
4 failed, 7715 passed, 2 skipped, 54 xfailed in 2046.33s (0:34:06)
    # 4 ca hỏng đều là test MỚI của tôi ở bản trung gian: bộ chạy nạp tests/test_soi_loi_t041.py đúng
    # lúc tôi đang sửa (gọi ui.read_row chưa có; so câu chưa thoát Markdown). Đã sửa test, chạy lại:
$ uv run pytest tests/test_t041_seo_ui.py tests/test_soi_loi_t041.py
167 passed, 8 xfailed in 95.32s (0:01:35)

$ uv run pytest <19 file trên bản gộp tạm T-041 + T-088 (commit fb76bcc, không thuộc nhánh nào):
    test_soi_loi_t088, test_wordpress_t088, client SEO T-042/T-060/T-085, T-061, test_t041_meta,
    test_t041_seo_ui, test_soi_loi_t041, test_app_wordpress>
4025 passed, 16 xfailed in 301.14s (0:05:01)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # thư mục tạm: test mới + file mồi
# chỉ file mồi (tên có dấu, khóa AWS mẫu, mật khẩu giả) bị bắt, 4 mục; test mới và báo cáo: 0
```

Thử gộp chỉ đọc `git merge-tree --write-tree origin/team/T-041 origin/team/T-088`: **không xung đột** (T-088 sửa `client.py` ở chỗ khác `_seo_text`).

### Đối chiếu việc được giao (lượt 2)

- [x] 1. SL-T041-1 → -7 đóng, gỡ `xfail` đúng R5
- [x] 2. Giao diện bước SEO theo yêu cầu 1–6 và ghi chú phiếu (2 lỗi Thấp: SL-T041-10, -11)
- [x] 3. Lỗi lùi lượt 3 ở mọi đường; xếp mức «Một ca chưa xử lý» (Thấp, SL-T041-9); chặn oan emoji mới (SL-T041-8)
- [x] 4. Nháp cũ và nháp có khối SEO vô lý (test trang thật + trình duyệt)
- [x] 5. App thật: không chạy `seo-app-main`, `launch.json` trả đúng bản cũ, không ghi gì lên website
- [x] 6. Không sửa code ứng dụng; lỗi mới SL-T041-8 → -11 có `xfail(strict=True)`

### Rủi ro (lượt 2)

- Chưa thử với WordPress thật (đúng phiếu: không có trang thử). Câu hỏi «SiteSEO có chạy shortcode trong meta không» vẫn chờ T-059 bước 4.
- `test_sl_t041_8` giả định cách sửa «không Chặn emoji mới»; nếu Lá Chắn chọn giữ Chặn và chỉ đổi câu báo thì Chỉ Huy đổi test này.
- `tests/test_soi_loi_t041.py` dùng chung AI giả, WordPress giả và fixture của `tests/test_t041_seo_ui.py`, `tests/test_app_images.py`: đổi tên các thứ đó thì file này báo lỗi nhập ngay (không lặng lẽ qua).

### Đề xuất (lượt 2)

1. **Chỉ Huy:** giao Lá Chắn rút gọn ngay (không lỗi nào chặn). Kèm câu hỏi SL-T041-8 (Cn) và G7 (dấu đảo chiều).
2. **Họa Sĩ (cùng phiếu, trước khi gộp):** SL-T041-9 (từ khóa chính), -10 (thứ tự dòng kiểm), -11 (nhãn ô); gỡ `xfail` khi XPASS. Xem G9 khi làm T-089.
3. **Thợ Máy:** SL-T041-8 theo quyết định Lá Chắn; G8 một dòng chú thích.

## Câu hỏi cho chủ dự án

Không có.

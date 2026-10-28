# Báo cáo T-096 · Soi Lỗi (rút gọn) · Bộ dựng bài cuối (Markdown → HTML, kiểm link, dữ liệu xác nhận)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-096](../tickets/T-096-bo-dung-bai-cuoi.md) · báo cáo Thợ Máy: [T-096-tho-may](T-096-tho-may.md) · thiết kế: [T-094](T-094-tho-may.md) mục 3.5, 4, 6 · điều kiện: [T-094-la-chan](T-094-la-chan.md) mục «Chung», «T-096» |
| Ngày nộp | 2026-10-28 (giờ máy, +07) |
| Nhánh kiểm | `team/T-096`, đầu nhánh lúc nhận `3031336` |
| Mức kiểm | Rút gọn |
| Kết quả | Hoàn thành |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T096-1), **6 Thấp** (SL-T096-2 → 7). **Phải sửa trước Lá Chắn: SL-T096-1.** Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t096.py` |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN** (đầu nhánh `c961000`): 7 lỗi lượt 1 đóng thật. 2 lỗi mới **Thấp** (SL-T096-8, -9), không lỗi nào phải sửa trước Lá Chắn. **Chuyển Lá Chắn được.** Xem mục «Lượt 2» cuối báo cáo |

## Tóm tắt (cho chủ dự án)

- **Phần an toàn làm đúng.** Tôi cho bộ dựng chạy với 20 bài thật của anh (đọc chữ từ các file Word trong `Content-20-bai`, không sửa gì) và với hàng chục mẫu chữ độc (link giả, ảnh giả, thẻ HTML, `<script>`, chú thích kiểu khối WordPress, shortcode, ký tự vô hình, ký tự đảo chiều chữ). Bài ra luôn sạch: **không có link nào ngoài link nội bộ app tự chèn**, link chỉ trỏ tới bài đã đăng, shortcode không chạy được. Đoạn hay dòng **chỉ có một địa chỉ web** (WordPress sẽ nhúng cả trang đó vào bài) bị Chặn ở cả Nháp, Hẹn giờ, Đăng ngay.
- **Link nội bộ chèn đúng chỗ:** trên 20 bài thật, 6.822 link giả lập AI chọn đều được chèn đúng cụm từ (chỉ trừ trường hợp cụm từ dính dấu gạch đầu dòng, xem SL-T096-2).
- **Mã xác nhận ổn định:** cùng bài thì cùng mã (kể cả chạy ở tiến trình khác); sửa một ký tự mà làm đổi thứ gửi đi thì mã đổi.
- **1 lỗi Trung bình (SL-T096-1):** bài có một «chữ» rất dài không dấu cách (hoặc khối mã nhiều dòng trống) làm màn hình xác nhận chậm theo bình phương: 20.000 ký tự mất khoảng 2–3 giây, 80.000 ký tự mất gần một phút. AI bị trang đối thủ dụ có thể sinh ra chữ như vậy. Sửa nhanh, nên sửa trước khi qua Lá Chắn.
- **6 lỗi Thấp**, đều không làm lộ link hay chạy mã: vài kiểu cụm từ AI chọn được duyệt ở bước SEO nhưng khi dựng bài thì bị bỏ; một địa chỉ YouTube có `&` bị đếm 2 lần; địa chỉ web nằm trong tiêu đề, đoạn trích, chú thích ảnh chưa được liệt kê; ảnh đưa vào lúc gửi chưa bị so với ảnh đã xác nhận; một chỗ sót nhỏ của lỗi shortcode cũ; một dòng bắt đầu bằng ba dấu «`» làm cả phần sau thành khối mã.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t096.py` | **Mới.** 21 hàm test, 188 trường hợp; 25 trường hợp `xfail(strict=True)` cho 7 lỗi SL-T096-1 → 7. Không gọi mạng |
| `docs/team/reports/T-096-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của Thợ Máy. Chữ 20 bài thật chỉ dùng để thử ngoài repo (script trong thư mục ghi chú chung, mục Bằng chứng 4); hai bài mẫu trong test là chữ tôi viết lại theo đúng các dạng gặp trong bài thật, không chép nguyên văn.

## Kiểm từng việc Chỉ Huy giao

| Việc | Kết quả | Test (`tests/test_soi_loi_t096.py`) |
|---|---|---|
| Bộ chuyển Markdown với chữ AI thật và độc: không lọt link, HTML | **Đạt** | `test_real_like_article_renders_safely` (2 bài dạng thật: danh sách mở bằng chữ đậm, ngoặc kép thẳng, dòng chú thích in nghiêng, «[Alt ảnh: …]», «### 1. …», danh sách số, trích dẫn, bảng, đường dẫn trong chữ) · `test_hostile_text_through_whole_builder` (34 mẫu × 2 dạng: thô như người gõ, qua `clean_ai_text` như chữ AI; ở thân, tiêu đề phần, tiêu đề bài: link Markdown lồng, ảnh trong link, chú thích cuối `[^1]`, link tham chiếu `[x]: <url>`, autolink, `&lt;a&gt;`, `javascript&#58;`, `vbscript:`, `<div onclick>`, `<details ontoggle>`, `<svg><script>`, `<!-- wp:html -->`, `<!-- wp:embed … /-->`, `<?xml?>`, CDATA, `</p><script>`, «＜script＞» toàn khổ, `\<`, `\[`, `&#x3C;script&#x3E;`, `&#0;`, `&#xD800;`, shortcode, U+202E, U+2066, BOM, địa chỉ trần, `<h1>`/`<h2>` trong thân, khối mã có `</code></pre><script>`): HTML cuối chỉ có thẻ của bộ chuyển + `<h2>` + `<a>` của app, không thuộc tính lạ, không chú thích, link chỉ trỏ bài đã đăng, không `[` `]` trần, `sanitize_html` chạy lại không đổi |
| Ký tự rộng 0 của T-031 | **Đạt** | `test_t031_breaks_removed_and_addresses_listed_whole`: thân, tiêu đề phần, tiêu đề bài qua `clean_ai_text` → HTML và tiêu đề không còn ký tự ngắt; 3 địa chỉ hiện liền mạch trong danh sách địa chỉ trần, không thành link |
| URL một mình trên một dòng/khối (WordPress nhúng) | **Đạt**, trừ SL-T096-3 (đếm trùng) | `test_url_alone_is_blocked_in_every_mode` (21 dạng × 3 hình thức gửi = 63 ca: đoạn, sau `clean_ai_text`, chữ hoa, dấu cách/tab/dấu cách không ngắt hai đầu, mục danh sách, danh sách thưa, danh sách số, ô bảng, tiêu đề con, trích dẫn, khối mã, dòng giữa khối mã, `&#10;`, `&#13;&#10;`, `\:`, `&#58;`, `&#47;`, có `&`, dấu chấm cuối) · `test_url_with_other_text_is_not_an_embed` (7 dạng không bị chặn oan: giữa câu, hai địa chỉ, `<…>`, link Markdown, ảnh Markdown, ký tự rộng 0 đứng đầu, xuống dòng mềm) |
| Khớp chia khối với `markdown_blocks` để `place_links` chèn đúng chỗ | **Đạt** cho chữ thường; **SL-T096-2** (Thấp) cho cụm từ dính ký hiệu Markdown | `test_every_link_accepted_at_seo_step_is_placed_when_building` (2 bài × 120 lượt gợi ý giả lập, mọi link `check_suggestions` nhận đều được chèn, đúng chữ). Trên 20 bài thật (ngoài repo): 6.822/6.822 link chèn được khi bỏ cụm từ bắt đầu bằng dấu mục danh sách; tính cả dạng đó thì 111 link bị bỏ, **tất cả** đều vì dấu «- » |
| Mã băm xác nhận ổn định | **Đạt** | `test_digest_same_in_every_process` (2 tiến trình, hạt băm `PYTHONHASHSEED` 0 và 12345: cùng mã) · `test_digest_changes_exactly_when_sent_content_changes` (150 lần sửa một ký tự ở tiêu đề, tiêu đề phần, thân, đoạn trích, slug, alt, chú thích, tiêu đề SEO: mã đổi **đúng khi** thứ gửi đi đổi; không hai gói khác nhau cùng mã). Ngoài repo: 20 bài thật × 3 tiến trình hạt băm khác nhau: cùng mã |
| Dữ liệu xác nhận liệt kê đủ link và cờ lạ | **Đạt** cho link trong thân; **SL-T096-4** (Thấp) cho chữ ngoài thân | `test_review_lists_every_internal_link_with_its_text` (4 link ở 4 phần, cả trong mục danh sách và ô bảng: đủ dòng, đúng chữ, đúng mã bài, không cờ) · `test_bare_addresses_in_body_listed_with_flags` (8 địa chỉ × 2 dạng: «а» Kirin → `xn--suachuacuast-79j.com`, «о» Kirin ở đuôi, `@`, cổng 8080, `xn--`, email tên miền Kirin, tên miền con giả, chữ hoa) |
| `links.py` sau khi sửa không lùi các ca T-039 | **Đạt**, trừ SL-T096-6 (Thấp, chỗ sót ngoài luồng bộ dựng) | `test_place_links_on_sanitized_html_never_reopens_shortcodes_fuzz` (800 mẫu HTML đã lọc có `&#91;…&#93;`: chữ in lại vẫn vô hiệu `[` `]`, chữ người đọc thấy không đổi). Toàn bộ test T-039, T-040, T-041 qua (mục Bằng chứng 2) |

## Lỗi tìm thấy

| Mã | Mức | Tóm tắt | Test |
|---|---|---|---|
| SL-T096-1 | **Trung bình** | `bare_addresses` và `embedded_urls` chạy **bậc hai**: một «từ» dài không dấu cách, hay nhiều dòng trống trong khối mã, làm dựng bài (mỗi lần hiện màn hình xác nhận) chậm theo bình phương | `test_sl1_*` (4) |
| SL-T096-2 | Thấp | Bước SEO (`check_suggestions` đọc `markdown_blocks`) nhận cụm từ mà HTML cuối không có hay ở đoạn khác: link bị bỏ khi dựng; link bắt buộc thành Chặn «Thiếu link bắt buộc» | `test_sl2_*` (9) |
| SL-T096-3 | Thấp | Địa chỉ có `&` đứng một mình bị liệt kê 2 lần ở chỗ nhúng (dạng `&amp;` và dạng thật): câu báo «Có 2 đoạn…» dù chỉ có một | `test_sl3_*` (1) |
| SL-T096-4 | Thấp | Địa chỉ web, email trong tiêu đề bài, đoạn trích, alt, chú thích ảnh không có trong danh sách địa chỉ trần | `test_sl4_*` (4) |
| SL-T096-5 | Thấp | `content_parts` chỉ so số phần, không so ảnh đưa vào với ảnh đã băm (byte, alt, ảnh đại diện) | `test_sl5_*` (3) |
| SL-T096-6 | Thấp | `place_links` in lại «[» từ `&#91;` thành «[» trần khi cùng nút chữ có «]» trần: tạo shortcode chạy được (phần sót của LC-T039-2, không gặp trong bộ dựng) | `test_sl6_*` (1) |
| SL-T096-7 | Thấp | Dòng bắt đầu bằng ``` mà phía sau còn dấu «`» (CommonMark: không phải rào mã) vẫn mở khối mã tới hết phần: bài trên website khác bản xem trước | `test_sl7_*` (3) |

### SL-T096-1 (Trung bình) · Dữ liệu màn hình xác nhận chạy bậc hai

- **Nguyên nhân:**
  - `review._BARE_EMAIL = [\w.%+-]+@…` (`review.py:66`): với một dãy dài ký tự chữ/số/dấu chấm không có «@», biểu thức thử lại từ **mọi** vị trí trong dãy, mỗi lần đọc tới cuối dãy.
  - `review._EMBED_LINE = ^([ \t\n\r\f\v]*)(https?://…)` (`review.py:53-55`, cờ `MULTILINE`): ở mỗi đầu dòng, `[ \t\n…]*` ăn qua **mọi** dòng trống phía sau rồi lùi lại.
- **Tái hiện** (máy Windows, thời gian CPU, mỗi lần một lời gọi):
  - `bare_addresses("<p>" + "a" * n + "</p>", SITE)`: n = 5.000 → 0,14 s; n = 20.000 → 2,7 s (gấp 19 lần khi dài gấp 4). Dạng `"a." * n`: 0,45 s → 7,6 s.
  - `embedded_urls("<pre><code>x" + "\n" * n + "y</code></pre>")`: n = 5.000 → 0,28 s; n = 20.000 → 4,3 s.
  - `build_article` với thân `"a" * 16000`: 1,8 s; khối mã có 16.000 dòng trống: 3,1 s (gấp 13–16 lần so với 4.000).
- **Mong đợi:** tuyến tính như mọi bộ lọc khác của dự án (T-004 #1, T-015; bộ chuyển `markdown.py` đã có test tuyến tính, phần dữ liệu xác nhận thì chưa).
- **Thực tế:** bậc hai. Nháp cho phép tới 5 MB (`storage/drafts.py:97`), nên một chuỗi base64 hay một «từ» 80.000 ký tự AI bị dụ trả về làm màn hình xác nhận treo gần một phút **mỗi lần dựng** (T-102 dựng khi hiện màn hình và dựng lại trước khi gửi).
- **Sửa gợi ý:** email: thêm `(?<![\w.%+-])` trước nhóm đầu (chỉ thử ở đầu dãy). Dòng nhúng: xét từng dòng (`splitlines`), dòng bỏ khoảng trắng ASCII hai đầu mà khớp trọn `https?://[^\s<>"]+` là nhúng (cùng kết quả với biểu thức của WordPress, không quay lui). Thêm test tuyến tính cho `bare_addresses`, `embedded_urls`, `build_article`.

### SL-T096-2 (Thấp) · Bước SEO nhận cụm từ mà bộ dựng không chèn được

- **Nguyên nhân:** `markdown_blocks` giữ nguyên ký hiệu Markdown trong chữ của khối, và chia khối, che `mã` khác bộ chuyển. `check_suggestions` tìm cụm từ trên chữ đó nên nhận cụm từ mà HTML cuối không có.
- **Tái hiện** (mỗi ca: `check_suggestions` nhận, `build_article(links=…)` báo bỏ qua; nếu là trang bắt buộc thì Chặn «Thiếu link bắt buộc»):

  | Thân bài | Cụm từ AI chọn | Vì sao HTML không có |
  |---|---|---|
  | `- Kéo cửa ở giữa rồi lau ray.` | `- Kéo cửa ở giữa` | dấu mục thành `<li>` (cũng `+ `, `1. `, `1) `) |
  | `Gọi dịch vụ sửa␠␠⏎cửa kéo` | `dịch vụ sửa cửa kéo` | hai dấu cách cuối dòng thành `<br>` |
  | `sửa cửa k&eacute;o` | `sửa cửa k&eacute;o` | mã ký tự đã giải mã thành «é» |
  | `> Kéo cửa thật chậm⏎để nghe` | `Kéo cửa thật chậm để nghe` | dòng nối sau trích dẫn thành đoạn riêng |
  | bảng có ô thừa cột | chữ trong ô thừa | ô thừa bị bỏ (đúng GFM) |
  | ``Dùng `a` hoặc dịch vụ sửa cửa kéo hoặc `b` khi kẹt ray.⏎⏎Gọi dịch vụ sửa cửa kéo`` + link «kẹt ray» | `dịch vụ sửa cửa kéo` | `_mask_code` che cả quãng giữa hai `mã` nên bước SEO kiểm link ở đoạn 2; bộ dựng chèn vào đoạn 1 (lần xuất hiện đầu), chiếm đoạn của link «kẹt ray», link đó bị bỏ |

- **Mong đợi:** cụm từ bước SEO đã nhận thì bộ dựng chèn được, đúng đoạn đã kiểm; không chèn được thì bước SEO bỏ ngay (câu báo ở bước SEO, người dùng bấm gợi ý lại).
- **Thực tế:** nhận rồi bỏ khi dựng. Hướng an toàn (không chèn sai chỗ cấm, không link lạ). Dạng dễ gặp nhất là dấu mục danh sách: trên 20 bài thật, mọi link bị bỏ đều vì dạng này.
- **Sửa gợi ý:** bỏ dấu mục danh sách, dấu `>` khỏi chữ khối trong `markdown_blocks` và che `mã` theo đúng cặp dấu huyền như bộ chuyển; hoặc `check_suggestions` kiểm thêm trên chữ của HTML bộ chuyển dựng. Việc này sửa `markdown_blocks` (`links.py`), ngoài phần Chỉ Huy đã duyệt cho T-096 (chỉ `place_links`): cần Chỉ Huy cho phép.

### SL-T096-3 (Thấp) · Địa chỉ có «&» bị đếm hai lần ở chỗ nhúng

- **Tái hiện:** thân bài chỉ có `https://www.youtube.com/watch?v=abc&t=10` → `review.embeds == ('https://www.youtube.com/watch?v=abc&amp;t=10', 'https://www.youtube.com/watch?v=abc&t=10')`, câu báo «Có 2 đoạn chỉ có một địa chỉ web…».
- **Nguyên nhân:** `embedded_urls` gộp kết quả của biểu thức chạy trên HTML (`&amp;`) với lớp chặt hơn chạy trên chữ đã giải mã (`review.py:283-289`), rồi bỏ trùng theo chữ.
- **Mong đợi:** một mục, dạng địa chỉ thật (chữ thô người dùng đọc), câu báo «Có 1 đoạn». Vẫn Chặn đúng (không phải lỗ).

### SL-T096-4 (Thấp) · Địa chỉ ngoài thân bài không được liệt kê

- **Tái hiện:** tiêu đề bài «Xem https://evil.example/khuyen-mai nhé» (tương tự đoạn trích, alt, chú thích ảnh) → `review.bare == ()`.
- **Nguyên nhân:** `bare_addresses` chỉ chạy trên HTML thân bài (`render.py:455`). Đoạn trích cũng không được tìm đoạn dạng shortcode (`render._shortcodes` chỉ xét tiêu đề, thân, alt, chú thích).
- **Mong đợi:** LC-T094-7, thiết kế 3.5: «mọi chuỗi dạng `https://`, `www.`, email còn trong chữ». Tiêu đề, đoạn trích, chú thích hiện công khai; alt đọc được bằng máy. Hậu quả nhỏ: tiêu đề và SEO vẫn hiện ở màn hình xác nhận; địa chỉ không thành link.

### SL-T096-5 (Thấp) · `content_parts` không ràng ảnh với mã băm

- **Tái hiện:** `build_article(images=[ArticleImage(section=0, sha256=băm(b"anh-da-duyet"), alt="Ray dưới")])`, rồi `content_parts({0: DraftImage(image=WebImage(data=b"anh-khac", …), alt="Ray dưới")})` (hoặc alt khác, hoặc `featured=True`) → ghép bình thường, không báo lỗi.
- **Nguyên nhân:** `BuiltArticle.content_parts` (`render.py:170-181`) chỉ so tập số phần.
- **Mong đợi:** mã băm (LC-T094-8) gồm băm byte, alt, chú thích, ảnh đại diện của từng ảnh; gói gửi đi phải đúng ảnh đã xác nhận. Khi `T` là `DraftImage`, `content_parts` nên so `sha256(image.data)`, `plain_image_text(alt)`, `plain_image_text(caption)`, `featured` với ảnh đã dựng, khác thì `BuildError`. Hiện an toàn chỉ khi T-102 dựng cả hai từ cùng một trạng thái (LC-T094-38); kiểm ở đây là lớp chặn thêm, rẻ.

### SL-T096-6 (Thấp) · `place_links` mở lại «[» đã vô hiệu

- **Tái hiện:** `place_links("<p>&#91;gallery id=1] dịch vụ sửa cửa kéo</p>", [InternalLink(0, "dịch vụ sửa cửa kéo", 10)], INDEX).html` → `<p>[gallery id=1] <a href=…>dịch vụ sửa cửa kéo</a></p>`: đầu vào không có shortcode chạy được, đầu ra có.
- **Nguyên nhân:** cách sửa LC-T039-2 (`links.py:929-935`) quyết theo **cả nút chữ**: nút có «[» hoặc «]» trần thì in lại bằng `html.escape` thường, nên «[» từ `&#91;` thành trần.
- **Mong đợi:** chữ vốn đã vô hiệu thì giữ vô hiệu (LC-T094-10 a, LC-T039 đk 3d: «`place_links` giữ `[` `]` đã vô hiệu»). Không gặp trong bộ dựng (luôn `sanitize_html` trước và sau `place_links`, test đã có), nhưng `apply_links` là hàm dùng chung. Sửa gợi ý: luôn `escape_shortcodes` chữ in lại (chữ người đọc thấy không đổi), hoặc chỉ giữ «[» «]» trần ở đúng vị trí vốn trần.

### SL-T096-7 (Thấp) · Dòng «```chữ```…» mở khối mã tới hết phần

- **Tái hiện:** thân `"```lệnh``` là lệnh mở cửa.\n\nĐoạn sau là chữ thường."` → `<pre><code>\nĐoạn sau là chữ thường.</code></pre>`. Tương tự ví dụ của CommonMark «``` aa ```», và «```` `x`» do `clean_ai_text` sinh ra khi bỏ thẻ giữa hai cặp dấu huyền («``<b>`` `x`»).
- **Nguyên nhân:** `markdown._blocks` (`markdown.py:470-480`) và `markdown_blocks` coi mọi dòng bắt đầu bằng ``` là rào mở; rào chưa đóng thì chạy tới hết phần.
- **Mong đợi:** CommonMark 4.5 (Streamlit dùng để hiện bản xem trước): sau rào bằng dấu huyền, phần chữ không được có «`»; có thì dòng đó là đoạn văn có `mã`. Thiết kế T-094: chỗ AI viết lạ «hiện thành chữ thường, không hỏng bài».
- **Thực tế:** cả phần còn lại thành khối mã trên website (bản xem trước vẫn là chữ thường); link nội bộ trong phần đó bị bỏ (khớp với bước SEO nên không chèn sai). Sửa cả hai nơi để giữ khớp chia khối (cũng chạm `markdown_blocks`).

## Bằng chứng

Chạy trên Windows 11 (máy chủ dự án), worktree `wt-T-096`, Python 3.12.15.

### 1. Test của Soi Lỗi

```
$ uv run pytest tests/test_soi_loi_t096.py
163 passed, 25 xfailed in 25.18s
```

Chạy riêng các ca `xfail` với `--runxfail`: cả 25 đỏ đúng lý do ghi ở mục «Lỗi tìm thấy» (tỉ lệ thời gian 18–19 lần; link bị bỏ; trùng dạng `&amp;`; địa chỉ không có trong danh sách; `DID NOT RAISE BuildError`; `[gallery` trần; `<pre><code>` nuốt đoạn sau).

### 2. Test liên quan (T-096 + mọi file dùng `links.py`, `markdown_blocks`, bộ dựng + trang app)

```
$ uv run pytest tests/test_la_chan_t039.py tests/test_onpage_links.py tests/test_publish_markdown.py \
    tests/test_publish_render.py tests/test_soi_loi_t039.py tests/test_soi_loi_t041.py \
    tests/test_soi_loi_t096.py tests/test_t040_prompts.py tests/test_t041_drafts_seo.py \
    tests/test_t041_links_ai.py tests/test_t041_seo_ui.py tests/test_la_chan_t041.py tests/test_app_pages.py
1095 passed, 28 xfailed in 290.68s (0:04:50)

$ uv run ruff check .
All checks passed!
```

28 `xfail` = 25 của `test_soi_loi_t096.py` + 3 có từ trước, cùng một lỗi SL-T041-8 (emoji mới, phiếu T-090): 1 ở `test_soi_loi_t041.py`, 2 ở `test_la_chan_t041.py`. 3 ca LC-T039-2 vừa gỡ `xfail` ở `test_la_chan_t039.py` qua.

Nơi gọi `links.py` (grep `seo_app app`): `app/views/write.py`, `seo_app/content/prompts.py`, `seo_app/content/workflow.py`, `seo_app/storage/drafts.py`, `seo_app/publish/*.py`. `place_links` (hàm duy nhất đổi) chỉ có `seo_app/publish/render.py` gọi. Mốc trước khi viết test: 645 ca của 5 file (T-096 + T-039) qua.

### 3. Test tốc độ

```
$ for i in 1..5; uv run pytest tests/test_publish_markdown.py tests/test_soi_loi_t096.py -k linear
11 passed, 4 xfailed   (5/5 lượt)
```

11 test tốc độ của bộ chuyển (Thợ Máy) không đỏ lượt nào trong lúc máy chạy song song agent khác; 4 ca tốc độ của SL-T096-1 đỏ ở cả 5 lượt (không lượt nào XPASS), nên `strict=True` không chập chờn.

### 4. Thử ngoài repo (script trong thư mục ghi chú chung `T-096-soi-loi-scripts/`)

- **20 bài thật** (đọc `.docx` bằng `zipfile` + `xml.etree`, chỉ đọc; chuyển gần đúng sang Markdown: tiêu đề cấp 2 chia phần, cấp 3 thành `###`, danh sách, đậm, nghiêng):
  - an toàn: mọi phần chỉ có thẻ cho phép, không chú thích, không `[` `]` trần, lọc lại không đổi; dựng hai lần cùng mã băm;
  - chèn link: 150 lượt × 20 bài gợi ý giả lập → 6.849 link được `check_suggestions` nhận, 111 bị bỏ khi dựng, cả 111 có cụm từ bắt đầu bằng «- » (SL-T096-2); bỏ dạng đó: 6.822 nhận, 0 bị bỏ;
  - mã băm: 20 bài × 3 tiến trình (`PYTHONHASHSEED` 1, 2, 999): cùng một dãy mã.
- **4.000 bài ngẫu nhiên** (chữ bài thật trộn ký hiệu Markdown, thẻ, mã ký tự, ký tự vô hình, nửa cặp UTF-16 lẻ; một nửa qua `clean_ai_text`; có ảnh, đoạn trích, link): không ném lỗi, dựng hai lần cùng mã, HTML cuối luôn sạch.
- **200.000 tiêu đề ngẫu nhiên:** tiêu đề `create_draft` gửi (`strip_tags(…).strip()` lần nữa) luôn đúng bằng `built.title` đã băm.
- **Đo tốc độ** 17 dạng đầu vào xấu cho `build_article` (từ dài, dấu chấm, `@`, `www.`, `http://`, dòng trống trong khối mã, `&#10;`, `[`, `*`, `|`, bảng nhiều cột, danh sách sâu, trích dẫn sâu, `<`, `&`, dấu cách, `\`): chỉ 3 dạng của SL-T096-1 tăng theo bình phương.

## Đối chiếu điều kiện Lá Chắn (phần Soi Lỗi kiểm được)

| Mã | Soi Lỗi thấy |
|---|---|
| LC-T094-1 | Test mới không gọi mạng, không tạo client; `test_digest_same_in_every_process` chạy Python con nhưng không mở mạng |
| LC-T094-4 | Đạt (mục «Kiểm từng việc» dòng 1) |
| LC-T094-5 | Đạt: HTML gửi đi đúng chuỗi `check_links` đã kiểm (test của Thợ Máy; Soi Lỗi kiểm thêm `sanitize_html(section) == section` ở mọi bài) |
| LC-T094-6 | Đạt (63 ca Chặn, 7 ca không chặn oan); SL-T096-1 (tốc độ), SL-T096-3 (đếm trùng) |
| LC-T094-7 | Đạt cho thân bài; SL-T096-4 cho chữ ngoài thân |
| LC-T094-8 | Đạt cho mã băm; SL-T096-5 cho ràng ảnh gửi đi với mã |
| LC-T094-9 | Đạt |
| LC-T094-10 | Đạt (3 ca LC-T039-2 qua, thân không có `<h1>`, `<h2>`); SL-T096-6 là chỗ sót ngoài luồng bộ dựng |

## Rủi ro và điểm cần chú ý (quan sát, không tính là lỗi)

- **Ô bảng thừa cột bị bỏ chữ** (đúng GFM, Streamlit cũng bỏ nên bản xem trước khớp): chữ trong ô thừa không lên website. Nên có câu nhắc ở bước SEO hay bước viết nếu bảng lệch cột.
- **Chỗ «[cần bổ sung: …]»** không nằm trong `ArticleReview.problems`; bộ dựng liệt kê nó như đoạn dạng shortcode (câu báo nói về shortcode). Trang Soạn bài đã có dòng «Chỗ thiếu số liệu thật còn» (`write.py:3088`); T-102 phải giữ dòng này ở màn hình xác nhận.
- **`<br>` không tách chữ khi tìm địa chỉ trần:** «a@evil.example» + ngắt dòng cứng + «hotline» liệt kê thành «a@evil.examplehotline» (cờ vẫn đúng «Khác website»).
- **Lớp chặn nhúng chặt hơn WordPress** (đúng thiết kế): `<p><code>https://…</code></p>`, ô bảng, tiêu đề chỉ có một địa chỉ cũng Chặn dù WordPress không nhúng. Người dùng thêm chữ quanh địa chỉ là qua.
- **Ký hiệu `&#10;` trong chữ** (người gõ) thành xuống dòng thật trong `<p>`: `wpautop` đổi thành `<br>` khi hiện; vẫn được kiểm nhúng đúng (test «mã xuống dòng»).

## Đề xuất

- **Thợ Máy, lượt 2 ngắn trước Lá Chắn:** sửa SL-T096-1 (bắt buộc). Cùng file, sửa nhỏ, nên làm luôn: SL-T096-3 (`html.unescape` rồi bỏ trùng), SL-T096-5 (so ảnh trong `content_parts`), SL-T096-6 (luôn vô hiệu `[` `]` chữ in lại), SL-T096-4 (chạy `bare_addresses` trên tiêu đề, đoạn trích, alt, chú thích; `_shortcodes` thêm đoạn trích). Bỏ `xfail` của test tương ứng khi XPASS.
- **SL-T096-2, SL-T096-7:** phải sửa `markdown_blocks` trong `links.py` cho khớp bộ chuyển. Chỉ Huy quyết cho làm ở lượt 2 T-096 hay để phiếu riêng trước T-102 (T-102 là lúc người dùng thật gặp link bắt buộc bị Chặn).
- **T-102:** dựng `ArticleImage` và `DraftImage` từ cùng một trạng thái; giữ dòng «Chỗ thiếu số liệu thật còn»; đếm chỗ nhúng theo số dòng hiển thị chứ không theo `len(embeds)` nếu SL-T096-3 chưa sửa.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (xem lại nhanh, 2026-10-28, đầu nhánh `c961000`)

### Tóm tắt lượt 2 (cho chủ dự án)

- **Cả 7 lỗi lượt 1 đã sửa thật.** 25 ca test của tôi trước đây đỏ (đánh dấu «lỗi chờ sửa») nay qua; Thợ Máy chỉ gỡ dấu, không đổi điều kiện kiểm.
- **Không còn chậm theo bình phương.** Chữ 20.000 ký tự hay 20.000 dòng dựng xong trong vài phần mười giây tới vài giây; gấp 4 độ dài thì chậm khoảng 4 lần.
- **Link nội bộ trên 20 bài thật:** 6.930 link bước SEO nhận, **cả 6.930 đều chèn được** (lượt 1 bị bỏ 111 link vì dấu gạch đầu dòng).
- **Không lọt link hay HTML mới**, kể cả với cách in lại chữ mới của phần chèn link.
- **2 lỗi Thấp mới**, đều an toàn, không cần sửa trước khi qua Lá Chắn:
  - tiêu đề nằm **trong** khung trích dẫn hay gạch đầu dòng vẫn được bước SEO nhận làm chỗ đặt link rồi bị bỏ khi gửi (dạng hiếm);
  - bài có ảnh mà chưa chọn ảnh đại diện thì website tự lấy ảnh đầu, nhưng màn hình xác nhận lại báo «không có ảnh đại diện».

### 7 lỗi lượt 1: đóng thật

| Mã | Soi Lỗi kiểm | Kết quả |
|---|---|---|
| SL-T096-1 | 4 test tốc độ (nay qua); đo lại 25 dạng đầu vào xấu ở 20.000 và 80.000 ký tự cho cả `build_article` lẫn `check_suggestions`; đo 5 MB | **Đóng** (số đo ở dưới) |
| SL-T096-2 | 9 ca (nay qua); thử nghiệm 20 bài thật **tính cả** cụm từ dính dấu `- ` | **Đóng**: 6.930/6.930 link chèn được |
| SL-T096-3 | 1 ca (nay qua): một mục, dạng chữ thật | **Đóng** |
| SL-T096-4 | 4 ca (nay qua): tiêu đề, đoạn trích, alt, chú thích | **Đóng** |
| SL-T096-5 | 3 ca (nay qua): khác byte, alt, ảnh đại diện → `BuildError` | **Đóng** |
| SL-T096-6 | 1 ca (nay qua); thêm thử ngẫu nhiên 40.000 lần `place_links` (HTML thô và đã lọc, đủ kiểu `&#91;`, `&lsqb;`, `&amp` không «;», `&ampx`, `&NotEqualTilde;`…): chữ người đọc thấy không đổi, không lần nào sinh thêm `[` `]` trần, 22.784 link được chèn | **Đóng** |
| SL-T096-7 | 3 ca (nay qua) | **Đóng** |

Gỡ `xfail` đúng R5: diff `5d88877..c961000` của `tests/test_soi_loi_t096.py` chỉ bỏ 10 dòng `@pytest.mark.xfail(…)`, không đổi `assert` nào. Ở lượt này tôi dọn 2 hằng chữ `_SL1`, `_SL2` không còn dùng và ghi chú đầu nhóm test (file của tôi).

### Tốc độ (thời gian CPU, máy Windows đang chạy song song agent khác)

| Đầu vào | `check_suggestions` (bước SEO) | `build_article` (bộ dựng) |
|---|---|---|
| Từ dài 20.000 ký tự / 80.000 ký tự | 0,03 s / 0,06 s | 0,02 s / 0,06 s |
| 20.000 dòng gạch đầu dòng (80.000 ký tự) | 0,33 s | 4,0 s |
| 20.000 dòng trích dẫn `>` | 0,11 s | 0,19 s |
| 20.000 dòng có hai dấu cách cuối dòng | 0,11 s | 1,8 s |
| 80.000 dòng trống trong khối mã | 0,03 s | 0,16 s |
| 25 dạng xấu, 20.000 → 80.000 ký tự | tỉ lệ 1–6 (tuyến tính) | tỉ lệ 2–5 (tuyến tính) |
| **5 MB** bài chữ thường | 3,2 s | 20,6 s |
| 5 MB một «từ» liền | 4,1 s | 4,4 s |
| 5 MB dòng trống trong khối mã | 3,1 s | 11,9 s |
| 5 MB dòng gạch đầu dòng (1,3 triệu mục) | 20,5 s | 236 s |
| 5 MB `` `a` `` lặp / bảng / danh sách lồng | 4,8 / 7,2 / 10,4 s | 180 / 142 / 177 s |

Tất cả tuyến tính (vài dạng chạy dưới 16 ms ở 20.000 ký tự thì đồng hồ CPU của Windows làm tròn về 0, tỉ lệ đo ra vô nghĩa; các dạng đó vẫn dưới 0,1 s ở 80.000 ký tự). Dạng độc cực đoan 5 MB mất 2–4 phút: xem «Ghi nhận lượt 2».

### Không lùi T-039, T-041 (mọi file test dùng `links.py`)

Nơi gọi các hàm đổi: `markdown_blocks`, `_anchor_words` chỉ có `check_suggestions`, `place_links` gọi (cùng file); `check_suggestions` chạy ở bước SEO qua `ContentWriter.internal_links` (`seo_app/content/workflow.py:349`); `place_links` chỉ có `seo_app/publish/render.py` gọi; `seo_app/storage/drafts.py` chỉ dùng `InternalLink` (không đổi). Link cũ đã lưu trong nháp có dạng «- Kéo cửa…» nay vẫn chèn được vì `place_links` đọc cụm từ qua `_anchor_words`.

```
$ uv run pytest tests/test_la_chan_t039.py tests/test_onpage_links.py tests/test_publish_markdown.py \
    tests/test_publish_render.py tests/test_soi_loi_t039.py tests/test_soi_loi_t041.py \
    tests/test_soi_loi_t096.py tests/test_t040_prompts.py tests/test_t041_drafts_seo.py \
    tests/test_t041_links_ai.py tests/test_t041_seo_ui.py tests/test_la_chan_t041.py tests/test_app_pages.py
1132 passed, 7 xfailed in 218.48s (0:03:38)

$ uv run ruff check .
All checks passed!
```

7 `xfail` = 4 ca mới của lượt này (SL-T096-8 × 3, SL-T096-9) + 3 ca có từ trước của SL-T041-8 (emoji mới, phiếu T-090). Gồm 3 ca LC-T039-2 (`test_la_chan_t039.py`), 1.000 mẫu ngẫu nhiên của `test_soi_loi_t039.py`, giao diện bước SEO T-041 và mọi trang app.

### Không lọt link, HTML mới (chạy lại các bộ thử lượt 1 trên code lượt 2)

- `tests/test_soi_loi_t096.py`: 188 qua (gồm 34 mẫu độc × 2 dạng qua cả bộ dựng, 63 ca địa chỉ đứng một mình bị Chặn ở 3 hình thức, mã băm giữa 2 tiến trình), 4 `xfail` mới.
- Ngoài repo: 86/86 lần dựng với chữ độc sạch; 4.000 bài ngẫu nhiên không ném lỗi, mã băm ổn định, HTML luôn sạch; 32 dạng địa chỉ đứng một mình cho đúng kết quả như lượt 1 (một mục cho địa chỉ có `&`).
- 30 dạng chỗ dễ lệch giữa bước SEO và bộ dựng (trích dẫn, danh sách, bảng lồng nhau; rào mã; `\`, `&nbsp;`, `&amp;` trong `mã`; thẻ HTML dạng chữ; dấu mục 10 chữ số…): chỉ 3 dạng lệch còn lại, là SL-T096-8.

### Lỗi mới (lượt 2)

| Mã | Mức | Tóm tắt | Test |
|---|---|---|---|
| SL-T096-8 | Thấp | Tiêu đề **trong** trích dẫn hay mục danh sách («> ### …», «- ### …», dòng gạch dưới trong trích dẫn): bước SEO nhận cụm từ ở đó, bộ dựng dựng `<h3>` nên bỏ link; link bắt buộc thành Chặn | `test_sl8_*` (3) |
| SL-T096-9 | Thấp | Không ảnh nào `featured`: client lấy ảnh đầu tiên làm ảnh đại diện (`wordpress/client.py:1410`), dữ liệu xác nhận và mã băm lại ghi «không có ảnh đại diện» | `test_sl9_*` (1) |

#### SL-T096-8 (Thấp) · Tiêu đề trong trích dẫn, mục danh sách

- **Tái hiện:** thân `"> ### Mẹo bảo dưỡng cửa\n> Lau ray mỗi tháng."`, AI chọn «Mẹo bảo dưỡng cửa» → `check_suggestions` nhận; `build_article` ra `<blockquote><h3>Mẹo bảo dưỡng cửa</h3>…` và báo «không thấy cụm từ ở chỗ chèn được»; là trang bắt buộc thì Chặn «Thiếu link bắt buộc». Tương tự `"- ### Mẹo bảo dưỡng cửa\n- Lau ray mỗi tháng."` và `"> Mẹo bảo dưỡng cửa\n> ---\n> Lau ray mỗi tháng."`.
- **Nguyên nhân:** `markdown_blocks` chỉ nhận tiêu đề ở đầu dòng (dòng bắt đầu bằng «>» hay dấu mục danh sách là chữ đoạn văn), còn bộ chuyển đọc phần trong trích dẫn, mục danh sách như một thân riêng (`_blocks(quoted)`, `_blocks(content)`) nên thấy tiêu đề.
- **Mong đợi:** như SL-T096-2: cụm từ bước SEO nhận thì bộ dựng chèn được, hoặc bước SEO bỏ ngay. Hướng an toàn (không chèn vào tiêu đề), dạng viết hiếm (trên 20 bài thật không gặp).

#### SL-T096-9 (Thấp) · Ảnh đại diện mặc định không hiện ở màn hình xác nhận

- **Tái hiện:** `build_article(…, images=[ArticleImage(section=0, …), ArticleImage(section=1, …)])` không ảnh nào `featured=True` → `review.images` cả hai `featured=False`, không câu báo nào; `content_parts` nhận `DraftImage` cũng `featured=False` (khớp nhau), rồi `create_draft_with_images` đặt **ảnh phần 0** làm ảnh đại diện (`_plan_draft_images`: `chosen[0] if chosen else planned[0].source`).
- **Mong đợi:** thiết kế 3.5 (hàng «Bài»: «ảnh đại diện»), LC-T094-7, -8: dữ liệu xác nhận và mã băm nói đúng ảnh website sẽ dùng. Sửa gợi ý: bộ dựng đánh dấu ảnh đầu (theo thứ tự phần) là ảnh đại diện khi không ảnh nào được chọn, như client; hoặc báo «chưa chọn ảnh đại diện».
- **Thực tế:** chủ dự án tick xác nhận mà không thấy ảnh nào sẽ thành ảnh đại diện công khai. Ảnh vẫn là ảnh đã duyệt (byte, alt đúng), không phải lỗ bảo mật.

### Ghi nhận lượt 2 (không xếp lỗi)

- **5 MB chữ độc dựng 2–4 phút** (tuyến tính, hằng số lớn ở danh sách, bảng, `mã`: khoảng 0,2 ms mỗi mục danh sách). Chữ AI bị giới hạn số token nên thực tế dưới vài trăm KB (200 KB dạng nặng nhất khoảng 10 giây); chỉ người dùng tự dán chữ cực lớn mới gặp. Nên có giới hạn cỡ thân bài khi dựng (ví dụ 500 KB một phần, báo câu cố định) ở T-102 hoặc lượt sau.
- **Rào mã đóng khác CommonMark** (có từ lượt 1, cả hai nơi cùng cách nên link vẫn khớp): dòng «```python» bên trong khối mã đóng khối (CommonMark: rào đóng không có chữ phía sau), rào 4 dấu «````» bị đóng bởi «```» (CommonMark: phải đủ 4). Bài trên website khác bản xem trước ở dạng hiếm này.
- `_anchor_words` bỏ một dấu mục ở đầu cụm từ cả khi dấu đó là gạch ngang trong câu («Nhiệt độ - Kéo cửa»): link bọc phần chữ sau dấu, vẫn đúng bài, vô hại.

### Bằng chứng lượt 2

```
$ uv run pytest tests/test_soi_loi_t096.py tests/test_publish_markdown.py tests/test_publish_render.py   # trước khi thêm test mới
347 passed in 35.23s

$ uv run pytest tests/test_soi_loi_t096.py
188 passed, 4 xfailed in 18.28s

$ uv run pytest tests/test_soi_loi_t096.py --runxfail -k "sl8 or sl9"
4 failed   # đỏ đúng lý do: 3 ca «Link 1 … không thấy cụm từ…» (SL-T096-8), «assert [] == [0]» (SL-T096-9)
```

Script ngoài repo (thư mục ghi chú chung `T-096-soi-loi-scripts/`): `corpus3.py` (20 bài thật), `perf3.py`, `perf5mb.py` (tốc độ), `probe5.py` (30 dạng lệch, ảnh đại diện), `reprint1.py` (in lại theo ký tự), `hostile1.py`, `fuzz1.py`, `embed1.py`.

### Đề xuất lượt 2

- **Chuyển Lá Chắn ngay.** SL-T096-8, -9 là Thấp, sửa ở T-102 hoặc lượt dọn sau:
  - SL-T096-9 nên sửa trước khi T-102 nối màn hình xác nhận: bộ dựng đánh dấu ảnh đại diện mặc định như client;
  - SL-T096-8: `markdown_blocks` đọc phần sau «>» và sau dấu mục danh sách như bộ chuyển (hoặc bỏ dòng tiêu đề ở đó).
- T-102: giới hạn cỡ bài khi dựng (Ghi nhận lượt 2).

# Biên bản bảo mật T-096 · Bộ dựng bài cuối (Markdown → HTML, kiểm link, dữ liệu xác nhận) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-096](../tickets/T-096-bo-dung-bai-cuoi.md), điều kiện LC-T094-1 → -10 ([T-094-la-chan](T-094-la-chan.md) mục «Chung», «T-096») và LC-T039-2 ([T-039-la-chan](T-039-la-chan.md)) |
| Phạm vi | Rút gọn, soát kỹ phần chuyển Markdown và link. Diff `516fd36...team/T-096`, đầu nhánh lúc kiểm `088ebbe` (code lượt 2 `c961000`, sau đó chỉ có test, báo cáo Soi Lỗi): mới `seo_app/publish/markdown.py` (524 dòng), `render.py` (597), `review.py` (319); `seo_app/onpage/links.py` (`place_links` in lại theo từng ký tự, `markdown_blocks` đọc như bộ chuyển, hàm chia khối dùng chung, `_anchor_words` bỏ một dấu mục danh sách); test `tests/test_publish_markdown.py`, `tests/test_publish_render.py`, `tests/test_soi_loi_t096.py` (mới), `tests/test_la_chan_t039.py` (chỉ gỡ `xfail`). Đọc thêm code dùng chung: `seo_app/sanitize.py` (`_Sanitizer`, `escape_shortcodes`, `_ENTITY`, `_entity_value`, `_ESCAPABLE`), `seo_app/wordpress/client.py` (`create_draft`, `create_draft_with_images`, `_plan_draft_images`, `_describe_draft_media`, `DraftImage`), `seo_app/images/html.py` (`figure_html`, `plain_image_text`), `seo_app/images/tags.py` (`ImageTags`), `seo_app/wordpress/shortcodes.py`. Mã WordPress `class-wp-embed.php` (`autoembed`, theo biên bản T-094) và mã Gutenberg `packages/block-library/src/embed/transforms.js` (đọc 2026-10-28 qua `raw.githubusercontent.com`, không gọi website). Thử gộp với `origin/main` `0390a94` (đã có T-082, T-083, T-059 bước 7); `main` mới nhất lúc nộp `b513d67` chỉ đổi thêm `docs/team/board.md` |
| Ngày | 2026-10-28 (02:20–03:00 và 07:32–07:50 +07, giờ máy đo bằng `date`; phiên bị ngắt giữa chừng vì hết lượt dùng) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (LC-T096-1), **3 Thấp mới** (LC-T096-2, -3, -4); giữ mức **Thấp** cho 2 lỗi mới của Soi Lỗi (SL-T096-8, -9). Mỗi lỗi của tôi có test `xfail(strict=True)` trong `tests/test_la_chan_t096.py`. **LC-T094-1 → -10 và LC-T039-2: đóng** (LC-T094-8 trừ phần thẻ ảnh = LC-T096-2; LC-T094-6 đúng hai biểu thức của WordPress, lớp chặt hơn còn LC-T096-4). Không lọt link, HTML, ảnh, chú thích `<!-- wp:… -->`, shortcode. **Gộp `main` được ngay** (bộ dựng chưa được app gọi tới, không có đường đi hôm nay); khuyên một lượt Thợ Máy ngắn sửa LC-T096-1, -3, -4 trước khi gộp (khoảng 10 dòng, đã thử cách sửa); **bắt buộc** xong trước khi T-102 nối bộ dựng vào màn hình xác nhận |
| **Kết luận xem lại lượt 3** (2026-10-28, `7ea52e8`) | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**: 6/6 lỗi đóng (LC-T096-1 → -4, SL-T096-8, -9), không lùi điều kiện đã đóng; còn **1 Thấp mới LC-T096-5** (trước khi T-102 nối bộ dựng). Xem mục [Xem lại lượt 3](#xem-lại-lượt-3-2026-10-28-đầu-nhánh-7ea52e8) |
| **Kết luận xem lại lượt 4** (2026-10-28, `7da465f`) | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được**: **LC-T096-5 đóng** (1.993 đoạn Gutenberg nhúng, sót 0; lượt 3 sót 1.023), không chặn oan, R5 đúng, không lùi điều kiện đã đóng, không biểu thức chạy lâu; còn **1 Thấp mới LC-T096-6** (các dạng địa chỉ lạ mà `new URL` vẫn nhận; trước khi T-102 nối bộ dựng). Xem mục [Xem lại lượt 4](#xem-lại-lượt-4-2026-10-28-đầu-nhánh-7da465f) |

## Tóm tắt (cho chủ dự án)

Bộ dựng bài cuối **an toàn**: tôi cho nó chạy với hàng nghìn bài chứa chữ độc (link giả, ảnh giả, thẻ HTML, `<script>`, chú thích kiểu khối WordPress, shortcode, ký tự vô hình, ký tự đảo chiều chữ…). Bài ra luôn sạch: chỉ có định dạng thường (đậm, nghiêng, danh sách, bảng…), **link duy nhất là link nội bộ** app tự chèn tới bài đã đăng, không shortcode nào chạy được. Tôi cũng chạy đúng hai biểu thức mà WordPress dùng để **tự nhúng** địa chỉ web vào bài: 10.000 bài thử, WordPress sẽ nhúng ở 7.272 bài, bộ dựng **chặn đủ cả 7.272**. Mã xác nhận ổn định: dựng lại cùng bài thì cùng mã.

Còn 4 điểm, hôm nay chưa gây hại được vì bộ dựng chưa nối vào giao diện (phiếu T-102 mới nối):

1. **(Trung bình)** Bài có một tiêu đề con chứa dãy dấu cách rất dài làm bước dựng bài chậm theo bình phương: 16.000 dấu cách mất 2 giây, 64.000 ước khoảng nửa phút, mỗi lần mở màn hình xác nhận. Sửa một dòng.
2. **(Thấp)** Mã xác nhận chưa gồm **thẻ ảnh** (ảnh thật hay ảnh AI, mã công trình, khu vực). Thẻ quyết định tên file ảnh công khai và chữ «[AI]» trên ảnh. Nếu thẻ đổi sau khi bạn bấm xác nhận thì app vẫn gửi.
3. **(Thấp)** Một dòng code viết trần ký tự đảo chiều chữ. Hiện vô hại, nhưng kiểu viết này có thể làm người đọc code thấy khác điều máy chạy. Sửa một dòng.
4. **(Thấp)** Đoạn văn chỉ có một địa chỉ web mà đứng sau ký tự cách đặc biệt (`&nbsp;`): WordPress không tự nhúng, nhưng nếu bạn mở bài nháp rồi bấm «Chuyển thành khối» trong trình soạn của WordPress thì đoạn đó thành khối nhúng trang ngoài. Bộ dựng nên chặn cả dạng này.

## Lỗi phát hiện

Số dòng theo `088ebbe`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T096-1 | **Trung bình** (cùng loại, cùng chỗ với SL-T096-1 Soi Lỗi xếp Trung bình) | **Tiêu đề con có dãy khoảng trắng dài: bộ chuyển chạy bậc hai.** `_CLOSING_HASHES = re.compile(r"(?:^\|[ \t]+)#+[ \t]*$")` dùng với `sub` ở mỗi tiêu đề `#`: tại **mọi** vị trí trong một dãy dấu cách/tab, `[ \t]+` đọc tới hết dãy rồi mới thua (sau dãy không phải `#`). Đo (thời gian CPU, máy Windows): `markdown_to_html("# a" + " " * n + "b")` n = 4.000 → 0,11 s, n = 16.000 → **1,98 s** (gấp 18 lần khi dài gấp 4); dạng xen dấu cách, tab 32.000 ký tự → 8,3 s; `build_article` cùng thân: 0,13 → 1,97 s. `assert_scales_linearly` của dự án: tỉ lệ 19,0 và 16,4 (ngưỡng 9). Không ảnh hưởng bước SEO (`markdown_blocks` không dùng biểu thức này) | `seo_app/publish/markdown.py:60`, dùng ở `:443` | Lệnh giấu trong trang đối thủ (bước nghiên cứu) dụ AI viết một dòng tiêu đề `### …` kèm dãy hàng chục nghìn dấu cách, hoặc người dùng dán chữ như vậy → T-102 dựng bài mỗi lần hiện màn hình xác nhận và dựng lại ngay trước khi gửi (LC-T094-38) → app treo: 64.000 dấu cách khoảng 30 giây, 128.000 khoảng 2 phút mỗi lần dựng (suy từ tỉ lệ đo được). Không lộ gì, không đổi nội dung gửi. **Hôm nay không có đường:** `seo_app.publish` chỉ được test gọi (`grep` `seo_app app scripts`) | Chỉ bắt đầu ở đầu dãy khoảng trắng: `re.compile(r"(?:^\|(?<![ \t])[ \t]+)#+[ \t]*$")` (cùng kết quả: dãy đầu đã thua thì mọi vị trí sau trong dãy cũng thua), hoặc bỏ biểu thức (cắt `#` cuối bằng `rstrip`). Đã thử cách nhìn lùi trên bản giả lập ngoài repo: 2 ca `xfail` thành XPASS, 7 ca canh cách bỏ `#` đóng (`test_lc1_closing_hashes_still_removed_like_commonmark`) và mọi test T-096 qua. Thêm một ca vào `test_converter_scales_linearly` (`"# a" + " " * …`) |
| LC-T096-2 | Thấp | **Thẻ ảnh không được ràng vào ảnh đã xác nhận.** Client dùng `DraftImage.tags` (`ImageTags`: `source` thật/AI, `project_code`, `category`, `area`) để đặt **tên file công khai** (`image_file_name(…, ai_generated=tags.is_ai)`: tiền tố `minh-hoa-ai-`, mã công trình, khu vực) và **tiêu đề Media** («[AI] …» khi là ảnh AI). Nhưng `ArticleImage` không có thẻ, mã băm không có thẻ, `_same_image` không so thẻ, `ImageRow` không ghi ảnh thật/AI. Test: ảnh đã xác nhận không thẻ, `content_parts` nhận cả `DraftImage` mang `ImageTags(source="ai")` lẫn `ImageTags(project_code="CT012", area="Tân Phú")` | `seo_app/publish/render.py:86-96` (`ArticleImage`), `:188-202` (`_same_image`), `:384-393` (ảnh trong mã băm); client `seo_app/wordpress/client.py:1397-1404`, `:1424` | Bạn xem màn hình xác nhận (alt «Minh họa…» của ảnh AI) → trước khi gửi, thẻ ảnh đổi (đổi tên thư mục Drive, sửa thẻ tay ở tab khác) → T-102 dựng lại: mã băm vẫn khớp vì không có thẻ → gửi: ảnh AI lên website với tên file mang mã công trình, khu vực của công trình thật, tiêu đề Media mất «[AI]» (hoặc ngược lại). Alt vẫn đúng chữ đã duyệt (có trong mã băm), không chạy mã, không lộ gì: là chữ công khai sai so với điều bạn đã duyệt. Điều kiện LC-T094-8 («mọi thứ sẽ gửi») chưa nêu thẻ | Thêm `tags: ImageTags` vào `ArticleImage` (mặc định `ImageTags()`), vào mã băm (đủ các trường), so `draft.tags == image.tags` trong `_same_image`, hiện «Ảnh thật / Ảnh AI», mã công trình, khu vực ở `ImageRow`. Đã thử bản giả lập: 2 ca `xfail` XPASS, các test khác qua. **Trước khi T-102 nối màn hình xác nhận** |
| LC-T096-3 | Thấp (bandit B613 Medium: hạ mức vì nội dung đã kiểm, vô hại) | **Mã ứng dụng viết trần ký tự điều khiển hướng chữ («Trojan Source», CVE-2021-42574).** Biểu thức `_DROPPED` có trần U+202A, U+202E, U+2066, U+2069 (đúng là khoảng ký tự cần bỏ, đã đọc từng ký tự bằng `unicode_escape`). Các file khác của dự án viết dạng mã (`\u200b`… ở `sanitize.py:664`) | `seo_app/publish/markdown.py:57` | Hôm nay vô hại. Rủi ro là cách viết: trình soạn thảo, trang so sánh code áp quy tắc đảo chiều lên dòng đó nên hiện khác điều Python chạy; lần sửa sau có thể giấu chữ khác trong dòng mà người soát (người hay AI xem bản hiển thị) không thấy. GitHub hiện cảnh báo «bidirectional Unicode text» cho file này | Viết `\u202a-\u202e\u2066-\u2069` trong chuỗi `r"…"` (mô-đun `re` hiểu `\uXXXX`, như `\ud800-\udfff` ngay cạnh). Test `test_lc3_escaped_pattern_drops_the_same_characters` (đang qua) chứng minh bản viết mã bỏ đúng cùng các ký tự trên toàn bộ 1.114.112 mã Unicode; `test_lc3_no_raw_bidi_control_characters_in_app_source` (`xfail`) quét `seo_app/`, `app/`, `scripts/` |
| LC-T096-4 | Thấp | **Lớp chặn nhúng «chặt hơn» chỉ bỏ khoảng trắng ASCII, trình soạn khối bỏ cả khoảng trắng Unicode.** `embedded_urls` lớp thứ ba (khối mà chữ chỉ là một địa chỉ, «phòng trình soạn khối hay giao diện khác của WordPress nhúng tiếp») dùng `text.strip(_PCRE_SPACE)`. Gutenberg, khối Embed, biến đổi `raw` (dùng khi «Chuyển thành khối» và khi dán): `<p>` có `node.textContent.trim()` là đúng một địa chỉ `https://` (qua `isURL`, không đuôi file trừ `html`, `php`) thì thành khối Embed. `trim()` của JavaScript bỏ cả U+00A0, U+FEFF, U+2000–U+200A, U+3000… Đã chạy: thân `&nbsp;https://www.youtube.com/watch?v=x` (cũng `&#160;`, U+FEFF trần, `&emsp;`, `&#x3000;`) → `<p>\xa0https://…</p>`, `review.blocked = False`, `embeds = ()` (địa chỉ chỉ nằm ở danh sách địa chỉ trần, mức Cảnh báo). Dấu cách không ngắt **trần** thì đã Chặn (bộ chuyển `strip()` bỏ trước khi dựng) | `seo_app/publish/review.py:295-298` | AI bị dụ viết đoạn `&nbsp;https://trang-ngoài/…` → bộ dựng chỉ Cảnh báo «địa chỉ dạng chữ» → bạn gửi nháp. WordPress `autoembed` **không** nhúng (PCRE `\s` không gồm U+00A0: đúng LC-T094-6). Sau đó bạn mở nháp trong trang quản trị, bấm «Chuyển thành khối» → đoạn thành khối Embed → khi đăng, trang ngoài được nhúng vào bài (khung iframe của trang lạ trên site thật). Cần bạn tự bấm chuyển và trình soạn hiện ô nhúng trước khi lưu, nên xếp Thấp | Lớp chặt hơn bỏ khoảng trắng như `trim()` của JavaScript (Python `str.strip()` cộng U+FEFF, hoặc liệt kê đúng tập của JavaScript). Đã thử bản giả lập: 5 ca `xfail` XPASS; ca canh (dạng đang Chặn vẫn Chặn; địa chỉ có chữ khác cùng đoạn không bị Chặn oan) và mọi test T-096 qua, kể cả 7 dạng «không chặn oan» của Soi Lỗi (ký tự rộng 0 đứng đầu vẫn không Chặn: `trim()` không bỏ U+200B) |

## Ý kiến về 2 lỗi mới của Soi Lỗi (lượt 2)

| Mã | Mức Lá Chắn | Lý do | Khi nào sửa |
|---|---|---|---|
| SL-T096-8 (tiêu đề trong trích dẫn, mục danh sách: bước SEO nhận, bộ dựng bỏ link) | **Thấp, đồng ý** | Hướng an toàn: link bị bỏ kèm câu báo, không bao giờ chèn vào tiêu đề hay chỗ cấm, `href` vẫn chỉ từ danh sách bài; link bắt buộc thì `check_links` Chặn «Thiếu link bắt buộc» (hiện rõ). Tự tái hiện: `--runxfail` 3 ca đỏ đúng lý do | Phiếu dọn sau, hoặc T-102 |
| SL-T096-9 (không ảnh nào `featured`: client lấy ảnh đầu, màn hình xác nhận và mã băm ghi «không có ảnh đại diện») | **Thấp, đồng ý** | Ảnh vẫn là ảnh đã duyệt (byte, alt, chú thích trong mã băm), GPS đã Cảnh báo từng ảnh; chỉ thiếu thông tin ảnh nào thành ảnh đại diện công khai (ảnh chia sẻ mạng xã hội, trang danh mục). Quy tắc của client: `featured = chosen[0] if chosen else planned[0]` (`client.py:1410`), `planned` theo thứ tự phần | **Trước khi T-102 nối màn hình xác nhận**: bộ dựng đánh dấu ảnh đầu theo thứ tự phần làm ảnh đại diện khi không ảnh nào được chọn (đúng quy tắc client), vào mã băm và `ImageRow` |

## Đối chiếu điều kiện

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T094-1 (test không gọi mạng) | **Đóng** | Test mới dựng `SiteIndex` bằng tay, không tạo client WordPress. `test_soi_loi_t096.py` chạy một tiến trình Python con chỉ để tính mã băm (`subprocess`, không mạng). Bộ chặn mạng `autouse` (`tests/conftest.py`) không đổi |
| LC-T094-2 (câu lỗi cố định) | **Đóng** | `BuildError` chỉ có `_MSG_BAD_INPUT` (chèn tên phần sai là hằng: «các phần», «ảnh»…) và `_MSG_SPLIT` (`render.py:69-70`); không chép dữ liệu bài, không gọi mạng |
| LC-T094-3 (chữ hiện thuần, bỏ ký tự hướng chữ) | **Đóng phần T-096** | Dữ liệu: thân bỏ ký tự điều khiển, hướng chữ (`markdown._DROPPED`), tiêu đề bài, tiêu đề phần, đoạn trích qua `plain_line` (cùng `_DROPPED`), alt, chú thích qua `plain_image_text` (`normalize_meta` bỏ loại Cf); `ArticleReview.needs_escape = True`. Hiển thị: T-102. (Ký tự trần trong **mã nguồn**: LC-T096-3) |
| LC-T094-4 (không sinh `<a>`, `<img>`, HTML thô, chú thích) | **Đóng** | Theo cấu tạo: mọi chữ qua `escape_text` = `escape_shortcodes(html.escape(…))` (`markdown.py:64-66`); thẻ là hằng (`p`, `h3`–`h6`, `strong`, `em`, `code`, `pre`, `br`, `hr`, `ul`, `ol`, `li`, `table`…`td`, `blockquote`), thuộc tính duy nhất `start` của `<ol>` là số `[0-9]{1,9}`. **Thử E2** (6.000 bài chữ độc, mục Thử độc lập): 0 thẻ lạ, 0 thuộc tính lạ, 0 chú thích, `href` chỉ từ danh sách bài, 0 `[` `]` trần, lọc lại không đổi. Kèm test Thợ Máy (28 mẫu × 3 dạng + 5.000 bài) và Soi Lỗi (34 mẫu × 2 dạng, 4.000 bài, 20 bài thật) |
| LC-T094-5 (thứ tự trên đúng chuỗi gửi) | **Đóng** | `render.py:338-342`: `sanitize_html` → `place_links` → `sanitize_html` → `check_links(final, index, required)` trên một chuỗi; sau đó chỉ cắt ở `<h2>` có kiểm `"\n".join(phần) == final` (`:224-240`); mã băm tính trên các phần đó. Client chèn `<figure>` giữa các phần (`client.py:1313`, nối `"\n"`), mỗi `<figure>` một dòng, chú thích đã gộp khoảng trắng; **thử E1**: `sanitize_html(chuỗi gửi kèm ảnh) == chuỗi gửi` ở 7.000 bài |
| LC-T094-6 (chặn nhúng, đúng hai biểu thức WordPress, mọi hình thức) | **Đóng** (lớp chặt hơn: LC-T096-4) | `review.py:54-61`: biểu thức «dòng chỉ có địa chỉ» xét từng dòng (cùng kết quả với `'\|^(\s*)(https?://[^\s<>"]+)(\s*)$\|im'`), biểu thức `<p>` dùng lượng từ chiếm hữu (cùng kết quả), khoảng trắng chỉ ASCII như PCRE không cờ `/u`, `\n` trong thẻ đổi thành chỗ giữ như `wp_replace_in_html_tags`. Chặn ở `draft`, `future`, `publish` (`render.py:470-478`; test 63 ca của Soi Lỗi). **Thử E1**: chạy **đúng** hai biểu thức PHP bằng biểu thức byte của Python (cùng ngữ nghĩa PCRE: `\s` chỉ ASCII gồm VT, `[^\s<>"]` theo byte UTF-8, `^`/`$` theo LF) trên đúng chuỗi client gửi (kèm `<figure>`): 10.000 bài (8.000 trên nhánh, 2.000 trên cây gộp với `figure_html` mới), WordPress nhúng ở 7.272 bài, bộ dựng **sót 0**, chặn thêm 1.891 bài (lớp chặt hơn) |
| LC-T094-7 (dữ liệu xác nhận: mọi `href`, cờ tên máy, địa chỉ trần, shortcode, GPS, cờ phải escape) | **Đóng** (ảnh: SL-T096-9, LC-T096-2) | `link_rows` (`review.py:179-208`): `ascii_host` qua `_browser_host`, cờ ngoài ASCII, `xn--`, `@`, `\`, `//`, cổng lạ, khác website; `bare_addresses` gồm cả tiêu đề, đoạn trích, alt, chú thích (SL-T096-4 đã sửa); `_shortcodes` mọi chữ gửi; `ImageRow` alt, chú thích, ảnh đại diện, GPS; `needs_escape`. Ghi chú: trong bộ dựng, `<a>` chỉ do `place_links` (bài đã đăng), nên bảng link thực tế chỉ có link nội bộ; cờ là lớp phòng |
| LC-T094-8 (mã băm chuẩn hóa xác định, mọi thứ sẽ gửi) | **Đóng phần đã liệt kê**; thiếu thẻ ảnh → LC-T096-2 | `digest_of` (`render.py:299-303`): JSON khóa sắp xếp, `(",", ":")`, `ensure_ascii=False`, UTF-8 `surrogatepass`, có `DIGEST_VERSION`; nội dung (`:374-401`): hình thức, `date_gmt`, tiêu đề cuối, đoạn trích, slug, chuyên mục, thẻ (giữ thứ tự), mọi phần HTML, mỗi ảnh (phần, băm byte, alt, chú thích, ảnh đại diện, GPS), 3 ô SEO, công tắc ghi SEO. Chữ client gửi là hàm xác định của chữ đã băm: tiêu đề `escape_shortcodes(strip_tags(built.title).strip())` (`client.py:913-918`), đoạn trích `sanitize_html(built.excerpt)` = `built.excerpt` (E2 kiểm 6.000 bài). **E2**: dựng hai lần cùng mã ở 6.000 bài; Soi Lỗi: cùng mã giữa 3 tiến trình hạt băm khác. `content_parts` so ảnh với ảnh đã băm (SL-T096-5 đã sửa), trừ thẻ (LC-T096-2) |
| LC-T094-9 (`unbreak_autolinks` chỉ trong bộ dựng, chữ sau gỡ vẫn chưa an toàn) | **Đóng** | Gỡ ở `render.py:218` (thân, trước `markdown_to_html`) và `plain_line` (`:211`, `unescape_link_syntax` gỡ cả hai); chỗ khác có từ trước (`images/html.py:78`, `onpage/schema.py:227`). Chữ sau gỡ vẫn qua `escape_text`, lọc, kiểm địa chỉ trần (E1, E2) |
| LC-T094-10 (sửa LC-T039-2 trước khi dùng `apply_links`; thân không `<h1>`, `<h2>`) | **Đóng** | (a) `place_links` in lại từng ký tự (`links.py:1078`, `_literal_chars`, `_reprint` `:1091-1116`): `[` `]` vốn là `&#91;` `&#93;` thì vô hiệu lại, vốn trần thì giữ (so nguyên văn), không rõ thì vô hiệu. Đã đọc: `_CHARREF` trùng biểu thức của `html.unescape`, mỗi mã giải mã độc lập nên độ dài khớp; lệch thì `None` (vô hiệu hết). `tests/test_la_chan_t039.py`: chỉ gỡ 3 dấu `xfail`, không đổi `assert` (`git diff`). E2: 0 `[` `]` trần; Soi Lỗi: 40.000 lần thử. (b) `_heading_tag` = `h{max(3, level)}` (`markdown.py:266-268`), gạch dưới → `h3`; `_split` báo lỗi nếu số `<h2>` khác số phần − 1, nên mọi bài E2 dựng được là không có `<h2>` lạ |
| LC-T039-2 | **Đóng** | Như LC-T094-10 (a) |

## Các việc Chỉ Huy giao

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| Không lọt link, HTML, autolink, ảnh, `<!-- wp:… -->`, shortcode | **Đạt** | LC-T094-4 ở trên. Autolink: bộ chuyển không tự thành link; địa chỉ trần ở lại dạng chữ, được liệt kê; WordPress không chạy `make_clickable` trên nội dung bài; chỗ duy nhất WordPress tự thành link/nhúng là `autoembed` (dòng/đoạn chỉ có địa chỉ: Chặn). Ảnh: `![x](url)` thành chữ; `<img>` chỉ do `figure_html`. Chú thích, `<!…>`, `<?…?>`, CDATA: không bao giờ sinh, `sanitize_html` bỏ. Shortcode: mọi `[` `]` thành `&#91;` `&#93;` |
| Chặn nhúng đúng hai biểu thức WordPress | **Đạt** (LC-T096-4 cho lớp chặt hơn) | LC-T094-6 |
| `sanitize_html` → `place_links` → `sanitize_html` → `check_links` | **Đạt** | LC-T094-5 |
| Mã băm chuẩn hóa ổn định | **Đạt** (LC-T096-2) | LC-T094-8. Ghi chú: `matches()` với chuỗi có ký tự ngoài ASCII ném `TypeError` thay vì trả `False` (Quan sát 2) |
| Tốc độ tuyến tính | **1 lỗi Trung bình** (LC-T096-1) | **Thử E3**: 16 dạng độc riêng; chỉ tiêu đề có dãy khoảng trắng dài là bậc hai; 13 dạng khác tỉ lệ 3,6–4,3 hoặc dưới độ phân giải đồng hồ (`_` mở rồi `*` đóng 48.000 ký tự, dấu huyền 50 độ dài 220.000 ký tự, bảng 40 cột, danh sách lồng sâu, trích dẫn tới 7 tầng, mã ký tự, 24.000 địa chỉ trần, khối mã nhiều dòng chỉ có địa chỉ, rào mã giả, gạch dưới lặp). SL-T096-1 đã sửa đúng (đo lại không còn bậc hai) |
| `markdown_blocks` không lùi T-039, T-041 | **Đạt** | 63 file test nhập (trực tiếp hay gián tiếp, kể cả nhập muộn) `links.py`, `seo_app/publish`, `workflow.py`, `drafts.py`, `write.py`: **5.624 passed, 18 skipped, 24 xfailed, 0 hỏng** (30 phút). Soi Lỗi: 20 bài thật 6.930/6.930 link bước SEO nhận đều chèn được |
| Xếp mức 2 lỗi Thấp mới của Soi Lỗi | Xong | Mục «Ý kiến về 2 lỗi mới của Soi Lỗi» |
| Thử gộp với `origin/main` mới nhất | **Không xung đột, test qua** | Mục Kết quả công cụ quét, dòng «Thử gộp» |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (`PYTHONUTF8=1`) trên 11 file (10 file của diff + `tests/test_la_chan_t096.py`) và bản vá nhánh `git log -p 516fd36..team/T-096` (4 commit): 0 mục; mồi tiếng Việt bắt 2/2. Lệnh soát `security.md` mục 5 trên lịch sử nhánh: chỉ khớp chữ «token» trong câu báo cáo Soi Lỗi («giới hạn số token») và tên biến `tokens` của bộ chuyển; dạng khóa (`sk-ant`, `AIza…`, `ghp_`, `PRIVATE KEY`, `xox`): 0 |
| S2 | Đạt | Không ghi log. Câu lỗi cố định (LC-T094-2); câu trong `review.problems` chèn chữ bài, địa chỉ, tiêu đề bài trên site (chữ thô, `needs_escape`), không bí mật |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không gọi WordPress; `mode` chỉ là dữ liệu, chưa có đường gửi `future`/`publish` (T-099, T-102). Bộ dựng Chặn «Đăng ngay mà SEO chưa ghi» (`render.py:524-531`) |
| W2 | Không áp dụng | Không ghi gì lên site |
| W3 | Đạt (còn LC-T096-4 Thấp: lớp chặn nhúng chặt hơn) | Không lọt HTML, link, shortcode: LC-T094-4, -5, -6, -10. Bộ lọc `sanitize.py` không đổi; `create_draft` vẫn `sanitize_html(content)` (`client.py:919`) |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Không đổi lời dặn AI |
| A2 | Đạt | Chữ AI coi là chưa tin cậy ở mọi bước (escape, lọc, kiểm nhúng, địa chỉ trần, shortcode); `place_links` chỉ chèn `href` từ `SiteIndex` |
| A3 | Không áp dụng | Không gửi gì vào AI |
| U1 | Đạt (phần T-096) | Không đổi `app/`. Dữ liệu xác nhận là chữ thô có `needs_escape`; docstring `review.py:16-19` ghi cách hiện. T-102 kiểm hiển thị (LC-T094-3, -37) |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng đăng nhập |
| F1 | Không áp dụng | Không đọc, ghi file (test LC-T096-3 chỉ đọc mã nguồn trong repo) |
| F2 | Đạt | Không đổi byte ảnh; GPS từng ảnh có trong mã băm và dữ liệu xác nhận (Cảnh báo) |
| F3 | Đạt | Không `eval`, `exec`, `pickle`, `yaml.load`; chỉ thư viện chuẩn và `pydantic` có sẵn. LC-T096-3 (ký tự trần trong mã nguồn) |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi ở nhánh và ở `main` từ gốc (`git diff --quiet`). `pip-audit` 69 gói ghim, nguồn PyPI và OSV: không có lỗ hổng đã biết |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, worktree `wt-T-096` tại `088ebbe`; có agent khác chạy song song.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` (69 gói), `--no-deps --disable-pip`: PyPI `No known vulnerabilities found`; OSV `No known vulnerabilities found` | Có. Khóa thư viện không đổi |
| bandit 1.9.4 | 4 file code của phiếu: **B613 (trojansource) Medium** ở `seo_app/publish/markdown.py:57`. Toàn bộ `seo_app app scripts` (18.282 dòng): thêm B101 `seo_app/storage/drafts.py:709`, B608 `seo_app/storage/image_tags.py:128` | Có. B613 là thật → LC-T096-3 (xếp Thấp). B101, B608 có từ trước, ngoài diff (mục Báo nhầm) |
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trong thư mục nháp: bản sao 11 file, bản vá nhánh, **file mồi có chữ tiếng Việt** (khóa AWS giả, `password = …` giả). Mồi: **bắt 2/2**. File của phiếu và bản vá: 0 | Có. Đã xóa file mồi |
| Soát lịch sử git | `git log -p 516fd36..team/T-096` (4 commit): không bí mật | Có (S1) |
| pytest, nhánh | 63 file liên quan (mục «Các việc», dòng `markdown_blocks`): **5.624 passed, 18 skipped, 24 xfailed in 1801.34s**, 0 hỏng. `tests/test_la_chan_t096.py`: **16 passed, 10 xfailed**; `--runxfail`: 10 ca đỏ đúng lý do (tỉ lệ 19,0 và 16,4; `DID NOT RAISE BuildError` × 2; đúng `markdown.py:57` với 4 ký tự; `blocked` sai × 5) | Có. 24 xfail có từ trước (SL-T096-8 × 3, -9, SL-T041-8 × 3 và các file cũ) |
| Bản sửa giả lập (ngoài repo) | Plugin pytest thay biểu thức LC-T096-1, thêm so thẻ ảnh LC-T096-2, lớp chặt hơn bỏ khoảng trắng như JavaScript LC-T096-4: 5 file test T-096 với `--runxfail`: **378 passed**, 5 đỏ = LC-T096-3 (sửa ở mã nguồn, plugin không giả lập được) + SL-T096-8 × 3, -9 (của Soi Lỗi, chưa sửa) | Có: test của tôi qua được khi sửa, không vướng test khác |
| ruff | `uv run ruff check .`: `All checks passed!` (cả sau khi thêm `tests/test_la_chan_t096.py`); `ruff format --check` file mới: `already formatted` | Có |
| Thử gộp với `main` | `git merge-tree --write-tree origin/main HEAD` (`main` `0390a94`, đã có T-082, T-083, T-059 bước 7): cây `fd78238`, **không xung đột**; với `main` mới nhất `b513d67` (thêm đúng 1 file `docs/team/board.md`): cây `4fbea1f`, không xung đột. Từ gốc `516fd36`, `main` đổi 39 file; giao với code bộ dựng dùng: `seo_app/images/html.py` (`figure_html` thêm `srcset="<src> 1x"`, `_SRC_UNSAFE` chặn dấu phẩy; `plain_image_text` không đổi), `seo_app/wordpress/client.py` (chỉ phần xác nhận ghi SEO, không đụng `create_draft*`, `_plan_draft_images`), `tests/fake_wordpress.py`. Cây gộp dựng thành commit tạm `828ade8` (không nhánh, không push), mở bằng `git worktree add --detach` trong thư mục nháp, chạy 22 file (T-096, T-039, T-041, trang app, và test ảnh/client của `main`: `test_wordpress_images`, `test_t059_*`, `test_soi_loi_t059`, `test_t083_*`, `test_soi_loi_t083`, `-t054`, `-t068`, `-t081`) cùng `tests/test_la_chan_t096.py`: **3.870 passed, 22 xfailed in 484.06s**, 0 hỏng (22 xfail = 10 của tôi, SL-T096-8 × 3, -9, SL-T041-8 × 3 và xfail có sẵn trong test T-059/T-083 của `main`). `ruff check .` trên cây gộp: `All checks passed!`. Thử E1 hạt giống 4 với `figure_html` mới (có `srcset`): 2.000 bài, WordPress nhúng ở 1.463, **bộ dựng sót 0**, lọc lại chuỗi gửi không đổi. Đã gỡ worktree tạm | Có |

## Thử độc lập (thư mục nháp của phiên, không commit, không gọi website)

Chạy trong worktree: `PYTHONUTF8=1 uv run python <thư mục nháp>/<script> …`. Bản sao ở thư mục ghi chú chung, `T-096-la-chan-scripts/`.

- **E1 · Chặn nhúng so với WordPress** (`p_embed_oracle.py <hạt giống> <số bài>`, hạt giống 1, 2, 3 trên nhánh, 4 trên cây gộp): oracle là đúng mã `autoembed` (`wp_html_split` viết lại không điều kiện, đổi `\n` trong thẻ thành `<!-- wp-line-break -->`, câu kiểm `#(^|\s|>)https?://#i`, rồi hai `preg_replace_callback`) chạy trên byte UTF-8. Bài ghép từ 6 địa chỉ × 15 kiểu đệm (dấu cách, tab, U+00A0 trần và `&nbsp;`, `&#32;`, `&#9;`, U+3000, U+FEFF, `&#x20;`, U+2003, `&emsp;`, `\ `, U+200B) × 34 khuôn (đoạn, mục danh sách, danh sách số, trích dẫn lồng, tiêu đề, ô bảng, khối mã, thụt 4 dấu cách, xuống dòng cứng hai kiểu, `&#10;`, `&#13;&#10;`, `**…**`, `` `…` ``, `<…>`, link Markdown, `htt&#112;s://`, `https&#58;//`, `https\://`, `- [ ]`…), nửa số bài qua `clean_ai_text`, nửa số bài có ảnh với chú thích là địa chỉ. Chuỗi thử = các phần + `<figure>` của `figure_html`, nối `"\n"` như client. 10.000 bài: WordPress nhúng ở 7.272, **bộ dựng sót 0**, chặn thêm 1.891; lọc lại chuỗi gửi không đổi (7.000 bài có kiểm này).
- **E2 · Chữ độc qua cả bộ dựng** (`p_markup_fuzz.py`, hạt giống 7, 8, 9 × 2.000 bài, 1–3 phần, link nội bộ ngẫu nhiên, ảnh, đoạn trích): 69 mảnh độc (link, ảnh, link tham chiếu, chú thích cuối, `<script>`, `<img onerror>`, `<!-- wp:html -->`, `<!-- wp:embed … /-->`, CDATA, `<?php`, `&lt;a&gt;`, `&#60;script&#62;`, shortcode, `\[x\]\(…\)`, đậm/nghiêng lồng, bảng có thẻ, `<svg>`, `<math>`, `<base>`, `<noscript>`, `<template>`, `<iframe>`, `<form>`, ký tự đảo chiều, BOM, U+200B, NUL, nửa cặp UTF-16, `</p><a href=…>`…). **0 vi phạm**: chỉ thẻ của bộ chuyển + `<h2>` + `<a>`; thuộc tính chỉ `start` (số) và `href` (454 link, đều thuộc danh sách bài); không chú thích, `<!…>`, `<?…?>`; không `[` `]` trần; `sanitize_html(phần) == phần`; dựng hai lần cùng mã băm; tiêu đề, đoạn trích (đúng chữ client gửi) không có chỗ mở thẻ, không `[` `]` trần, đoạn trích gửi đúng bằng đoạn trích đã băm.
- **E3 · Tốc độ** (`p_speed96.py [dạng …]`): 16 dạng, kết quả ở mục «Các việc», dòng tốc độ, và LC-T096-1.
- **E4 · LC-T096-4**: 7 thân thử ở mục Lỗi; mã Gutenberg đọc ở `packages/block-library/src/embed/transforms.js` (nhánh `trunk`).
- **Bản sửa giả lập** (`fixsim/lc96_fix_plugin.py`, chạy `PYTHONPATH=<thư mục fixsim> uv run pytest -p lc96_fix_plugin …`): mục Kết quả công cụ quét.

## Quan sát (không tính là lỗi)

1. **Cỡ bài cực lớn**: 5 MB chữ độc (1,3 triệu mục danh sách, bảng, `mã` lặp) dựng mất 2–4 phút dù tuyến tính (Soi Lỗi đã đo, lượt 2). Nháp cho phép tới 5 MB. Đồng ý đề xuất của Soi Lỗi: T-102 giới hạn cỡ thân bài khi dựng (ví dụ 500 KB một phần), câu báo cố định.
2. **`BuiltArticle.matches`** với chuỗi có ký tự ngoài ASCII ném `TypeError` (`hmac.compare_digest` không so chuỗi như vậy) thay vì trả `False` (đã chạy). Vẫn là «không gửi» (đóng khi nghi ngờ). T-102 nên bắt lỗi này hoặc bộ dựng kiểm `isascii()` trước khi so, để không hiện lỗi lạ.
3. **Test có ký tự vô hình viết trần**: `tests/test_publish_markdown.py:107` (U+200B), `:164-165` (U+202E, U+2066, U+200D). Không phải mã ứng dụng (trên `main` đã có tiền lệ ở `tests/test_images_folders_soi_loi.py:1069-1073`), nên không tính vào LC-T096-3; khuyên viết dạng `\u…` khi sửa tới.
4. **Đoạn có `<br>`**: «a@evil.example» + ngắt dòng cứng + «hotline» được liệt kê thành một địa chỉ dính chữ sau (Soi Lỗi đã ghi); cờ «Khác website» vẫn đúng, không phải lỗ.
5. **Gỡ `&nbsp;` thì sao**: chính bộ chuyển giữ `&nbsp;` dạng U+00A0 trong `<p>`; WordPress `wpautop` và trình duyệt hiện như dấu cách. Không liên quan an toàn ngoài LC-T096-4.

## Báo nhầm đã loại

- bandit B101 (`seo_app/storage/drafts.py:709`): `assert` kiểm tra nội bộ có từ trước (T-055), ngoài diff.
- bandit B608 (`seo_app/storage/image_tags.py:128`): chỉ ghép tên bảng, tên cột hằng; có từ T-052/T-070/T-074, các biên bản Lá Chắn đó đã xác minh; ngoài diff.
- bandit B613 **không phải báo nhầm**: LC-T096-3.
- Lệnh soát lịch sử git khớp chữ «token» trong câu «giới hạn số token» của báo cáo Soi Lỗi và tên biến `tokens` trong `markdown.py`: không phải bí mật.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T096-1 (Trung bình):** sửa `_CLOSING_HASHES` (nhìn lùi hoặc bỏ biểu thức), gỡ 2 dấu `xfail` khi XPASS (không đổi `assert`), thêm một dạng tiêu đề có dãy khoảng trắng dài vào test tốc độ của bộ chuyển | Thợ Máy: **T-096 lượt 3** (khuyên, trước khi gộp) hoặc phiếu riêng | **Bắt buộc trước khi T-102 nối bộ dựng**; chậm nhất trước khi hết Giai đoạn 5 |
| 2 | **LC-T096-3 (Thấp):** viết `\u202a-\u202e\u2066-\u2069` thay ký tự trần ở `markdown.py:57`, gỡ dấu `xfail` của test quét mã nguồn | Cùng lượt với điều kiện 1 | Như điều kiện 1 |
| 3 | **LC-T096-4 (Thấp):** lớp chặn nhúng chặt hơn bỏ khoảng trắng như `trim()` của JavaScript (cả U+00A0, U+FEFF, U+2000–U+200A, U+3000…), gỡ 5 dấu `xfail` | Cùng lượt với điều kiện 1 | Trước khi T-102 nối bộ dựng |
| 4 | **LC-T096-2 (Thấp):** `ArticleImage` mang `ImageTags`, vào mã băm, `_same_image` so thẻ, `ImageRow` hiện ảnh thật/AI, mã công trình, khu vực; gỡ 2 dấu `xfail` | Thợ Máy (T-096 lượt 3 nếu tiện, không thì phần logic của T-102) | **Trước khi T-102 nối màn hình xác nhận** |
| 5 | **SL-T096-9 (Thấp):** bộ dựng đánh dấu ảnh đại diện mặc định đúng quy tắc client (ảnh đầu theo thứ tự phần), vào mã băm và `ImageRow` | Như điều kiện 4 | Như điều kiện 4 |
| 6 | **SL-T096-8 (Thấp):** `markdown_blocks` đọc tiêu đề trong trích dẫn, mục danh sách như bộ chuyển (hoặc bước SEO bỏ cụm từ ở đó) | Phiếu dọn sau hoặc T-102 | Trước khi hết Giai đoạn 5 |
| 7 | **T-102** (thêm vào điều kiện đã có LC-T094-36 → -39): giới hạn cỡ thân bài khi dựng (Quan sát 1); bắt `TypeError` của `matches` hoặc so chỉ khi `isascii()` (Quan sát 2); hiện `ascii_host` cạnh mọi link, địa chỉ, chữ thô theo `needs_escape` (LC-T094-3, LC-T039-1) | Họa Sĩ, Thợ Máy (T-102) | Khi làm T-102 |
| 8 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

Không có rủi ro nào cần chủ dự án quyết định chấp nhận; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

---

## Xem lại lượt 3 (2026-10-28, đầu nhánh `7ea52e8`)

| Mục | Nội dung |
|---|---|
| Phạm vi | Xem lại nhanh: diff `12b905e..7ea52e8` (Thợ Máy lượt 3): `seo_app/onpage/links.py` (+35), `seo_app/publish/markdown.py` (+18/−3), `render.py` (+110/−7), `review.py` (+14/−2); test `tests/test_la_chan_t096.py` (−16, chỉ gỡ dấu `xfail`), `tests/test_soi_loi_t096.py` (−9, chỉ gỡ dấu), `tests/test_publish_markdown.py` (5 dòng: ký tự trần sang dạng mã), `tests/test_publish_render.py` (+79, test mới) |
| Ngày | 2026-10-28 (10:28–11:00 và 13:12–13:25 +07, giờ máy đo bằng `date`; phiên bị ngắt giữa chừng vì hết lượt dùng) |
| **Kết luận lượt 3** | **ĐẠT CÓ ĐIỀU KIỆN**: **6/6 lỗi đóng** (LC-T096-1 Trung bình; LC-T096-2, -3, -4; SL-T096-8, -9), Quan sát 2 (`matches`) cũng đã sửa; gỡ `xfail` đúng R5; không lùi LC-T094-1 → -10, LC-T039-2. **1 lỗi Thấp mới: LC-T096-5** (đoạn «địa chỉ `https://` + chữ» vẫn thành khối nhúng khi «Chuyển thành khối»), 4 ca `xfail(strict=True)`. Không còn lỗi Trung bình. **Gộp `main` được ngay** (thử gộp với `main` mới nhất `5e1d831`: không xung đột, test qua); LC-T096-5 sửa trước khi T-102 nối bộ dựng |

### Tóm tắt lượt 3 (cho chủ dự án)

- Cả 6 điểm lần trước đã sửa đúng. Tiêu đề có dãy dấu cách dài nay dựng gần như tức thì (256.000 dấu cách dưới 0,02 giây; trước đây 16.000 dấu cách đã mất 2 giây). Thẻ ảnh (ảnh thật hay AI, mã công trình, khu vực) và ảnh đại diện nay nằm trong mã xác nhận: thẻ đổi sau khi bạn xác nhận thì app dừng, không gửi. Code không còn ký tự đảo chiều viết trần. Đoạn `&nbsp;` + một địa chỉ bị chặn.
- Còn **1 điểm nhỏ mới (Thấp)**, cùng loại với điểm 4 lần trước: trình soạn khối của WordPress coi cả đoạn «địa chỉ web + chữ phía sau» (ví dụ `https://trang-la/… xem thêm`) là một địa chỉ, nên biến nó thành khối nhúng khi bạn bấm «Chuyển thành khối». Lần trước tôi tả điều kiện của trình soạn chưa đủ. Bộ dựng nên chặn cả dạng này. Hôm nay chưa có hại vì bộ dựng chưa nối vào giao diện.
- Tôi cũng sửa chính file test của mình: công cụ ghi file đã đổi 3 chỗ mã ký tự thành ký tự thật (đúng lỗi kiểu LC-T096-3).

### Kiểm từng lỗi

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T096-1 (Trung bình) | **Đóng** | Bỏ biểu thức; `_strip_closing_hashes` cắt dấu «#» đóng bằng `rstrip` (`markdown.py:267`). 2 ca của tôi qua. Đo lại: `markdown_to_html("# a" + " " * n + "b")` n = 16.000: dưới 16 ms (trước 1,98 s); n = 256.000: 15,6 ms; `assert_scales_linearly` qua ở cỡ 64.000/256.000 (dấu cách, và dấu cách xen tab). 7 ca canh cách bỏ «#» đóng (CommonMark 4.2) của tôi qua. Thợ Máy thêm `test_heading_with_long_whitespace_is_linear` (qua cả `build_article`) |
| LC-T096-2 (Thấp) | **Đóng** | `ArticleImage` có 5 trường thẻ, dựng bằng `ArticleImage.of(…, tags=ImageTags)`, đọc lại `.tags` (kiểm theo danh sách cố định, sai là `BuildError`: `render.py:369`); `_same_image` so `draft.tags == image.tags` (`:270`); mã băm có `tags` (5 trường) và `featured_effective` (`:482`), `DIGEST_VERSION` lên `t096-2`; `ImageRow` có ảnh AI, mã công trình, hạng mục, khu vực. 2 ca của tôi qua. Ghi chú: thẻ lưu thành 5 trường chữ thay vì một trường `ImageTags` (đồng ý, để gói dựng ra ghi JSON được); T-102 phải dựng `ArticleImage.of(…, tags=draft.tags)` từ cùng trạng thái với `DraftImage` |
| LC-T096-3 (Thấp) | **Đóng** | `_DROPPED` viết dạng mã (`markdown.py:57-59`). Ca quét mã nguồn của tôi qua (nay quét thêm 4 file test của phiếu); bandit trên 4 file code của phiếu: 0 cảnh báo (B613 hết). `tests/test_publish_markdown.py` đổi 5 dòng ký tự trần sang dạng mã: cây cú pháp (AST) bản cũ và mới **giống hệt**, điều kiện kiểm không đổi |
| LC-T096-4 (Thấp) | **Đóng** | `_JS_TRIM` (`review.py:69`, dùng ở `:308`) trùng **đúng** tập ký tự `String.prototype.trim` bỏ: so với Node 24 trên mọi mã Unicode, 25/25 ký tự, không khác. 5 ca của tôi qua, 7 ca canh qua |
| SL-T096-8 (Thấp) | **Đóng** | `markdown_blocks` bỏ dòng mà phần sau «>» hay sau dấu mục danh sách là tiêu đề, dòng gạch dưới, kẻ ngang (`links.py:689`, `_quote_or_item_text` `:712`): hướng chặt hơn, bước SEO bỏ ngay chỗ bộ dựng không chèn được. 3 ca Soi Lỗi qua. Hàm mới tuyến tính (chỗ bậc hai do chính lượt 3 gây ra đã bị test tốc độ T-039 bắt và được sửa trước khi nộp) |
| SL-T096-9 (Thấp) | **Đóng** | Ảnh đại diện thật sự tính đúng quy tắc client (`render.py:445`, `client.py:1410`): `ImageRow.featured` là ảnh website dùng, `featured_auto` khi tự chọn; mã băm có `featured_effective`. Ca Soi Lỗi qua |
| Quan sát 2 (`matches`) | **Đã sửa** | `digest.isascii()` trước `compare_digest` (`render.py:230`); test `test_matches_never_raises_on_odd_text` |

**R5:** `git diff 12b905e..7ea52e8 -- tests/`: `test_la_chan_t096.py` chỉ xóa 4 dấu `xfail` (10 ca), `test_soi_loi_t096.py` chỉ xóa 2 dấu (4 ca), không `assert` nào đổi; `test_publish_render.py` chỉ thêm (+79/−0); `test_publish_markdown.py` cùng AST.

**Không lùi điều kiện đã đóng:** LC-T094-4, -5, -6, -10, LC-T039-2: thử E1 (đúng hai biểu thức `autoembed`, có `<figure>`) 1.500 bài trên nhánh (WordPress nhúng 1.072, sót 0) và 1.500 bài trên cây gộp (nhúng 1.087, sót 0), lọc lại chuỗi gửi không đổi; thử E2 (chữ độc qua cả bộ dựng) 1.500 bài, 0 vi phạm. LC-T094-8: cách chuẩn hóa giữ nguyên, nội dung băm thêm thẻ ảnh và ảnh đại diện thật sự, đổi phiên bản. LC-T094-1, -2: test mới không gọi mạng; câu lỗi mới cố định («thẻ ảnh»).

### Lỗi mới (lượt 3)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T096-5 | Thấp (cùng loại, cùng điều kiện với LC-T096-4) | **Lớp chặn nhúng «chặt hơn» vẫn chỉ Chặn đoạn mà cả chữ là một địa chỉ; trình soạn khối nhúng cả đoạn «địa chỉ `https://` + chữ».** Mã Gutenberg (`trunk`, đọc 2026-10-28): khối Embed, biến đổi `raw` (`packages/block-library/src/embed/transforms.js`): `<p>` có `textContent.trim()` qua `isURL` (`packages/url/src/is-url.ts`: chỉ là `new URL(chữ)` không ném lỗi), bắt đầu bằng `https://`, chỉ một `https://`, và tên file cuối (`getFilename`) không phải đuôi tệp (trừ `html`, `php`) thì thành khối Embed. `new URL` (WHATWG) nhận dấu cách trong đường dẫn, tham số (tự mã thành `%20`), nên cả đoạn `https://evil.example/trang nội dung bất kỳ` là «một địa chỉ». Mô tả điều kiện Gutenberg ở LC-T096-4 của tôi chưa đủ (chỉ nói khoảng trắng hai đầu). Thử (`p_gutenberg_compare.py`: chạy đúng `isMatch` bằng `URL` của Node 24 trên từng `<p>` của HTML cuối, code lượt 3): 12 mẫu cố định, Gutenberg nhúng 8, bộ dựng không Chặn 6 (`https://www.youtube.com/watch?v=abc xem thêm`, `https://evil.example/trang nội dung bất kỳ`, `https://evil.example/a.mp4 xem`, `https://evil.example/x, xem thêm.`, `**https://evil.example/x** xem`, `https://evil.example/x?y=1 z`); 3.000 mẫu ngẫu nhiên: Gutenberg nhúng 1.993, bộ dựng không Chặn 1.023. WordPress `autoembed` không nhúng các đoạn này (đúng LC-T094-6) | `seo_app/publish/review.py:306-310` (lớp chặt hơn: `_ONLY_URL.fullmatch`) | AI bị dụ (lệnh giấu trong trang đối thủ) viết đoạn `https://trang-ngoài/đường-dẫn vài chữ` (hoặc người dùng dán) → bộ dựng chỉ Cảnh báo «địa chỉ dạng chữ» → gửi nháp → mở nháp trong trang quản trị, bấm «Chuyển thành khối» → đoạn thành khối Embed (chữ phía sau thành một phần địa chỉ) → khi đăng, trang ngoài được nhúng vào bài (trang có oEmbed thì nhúng được với mọi đường dẫn). Cần tự bấm chuyển và trình soạn hiện ô nhúng trước khi lưu: Thấp | Lớp chặt hơn làm đúng điều kiện `isMatch`: sau `strip(_JS_TRIM)`, chữ bắt đầu bằng `https://` (không phân biệt hoa thường), đúng một `https://`, phần tên máy (trước `/`, `?`, `#` đầu tiên) không rỗng, không khoảng trắng, tên file cuối (dấu cách tính như `%20`) không khớp `\.(?!(html?\|php)$)[a-z0-9]+$` → Chặn. Đã thử bản giả lập ngoài repo (`fixsim5/lc965_fix_plugin.py`): 4 ca `xfail` XPASS; so lại Gutenberg: 1.993/1.993 đoạn bị Chặn; 5 file test T-096 với `--runxfail`: 394 qua, **1 ca phải đổi theo**: `test_embed_patterns_not_found` của Thợ Máy, mẫu `<p><a href="https://suachuacuasat.com/x/">https://suachuacuasat.com/x/</a> rồi</p>` (Gutenberg cũng nhúng đoạn này khi chuyển; bộ dựng không sinh được HTML này vì chữ link không được giống địa chỉ: `_anchor_words` → `has_link`), cần Chỉ Huy duyệt đổi điều kiện ca này cùng lượt sửa. 3 ca canh của tôi (`Xem https://…`, hai `https://`, chỉ `http://`) và 7 ca «không chặn oan» của Soi Lỗi giữ nguyên |

### Tự sửa file test của tôi (`tests/test_la_chan_t096.py`)

Công cụ ghi file đã đổi chuỗi mã thành ký tự thật ở 3 dòng của chính file test Lá Chắn: biểu thức «bản viết mã» trong ca canh LC-T096-3 có trần U+202A, U+202E, U+2066, U+2069; tham số LC-T096-4 có trần U+FEFF và U+00A0. Hệ quả: ca canh LC-T096-3 so hai biểu thức cùng dạng trần nên không chứng minh điều nó nói (kết quả vẫn đúng). Đã sửa: ca canh so `_DROPPED` với **tập mã số** (không chép ký tự); tham số dùng `\N{…}`; ca quét mã nguồn quét thêm 4 file test của phiếu. Quét lại: file không còn ký tự loại Cf, Zs (trừ dấu cách), Cc viết trần. Không đổi điều kiện ca nào khác; thêm 4 ca `xfail` LC-T096-5 và 3 ca canh.

### Kết quả công cụ quét (lượt 3)

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest, nhánh | 15 file (14 file Thợ Máy đã chạy + `tests/test_la_chan_t096.py`): **1.170 passed, 7 xfailed in 249.74s**, 0 hỏng (7 xfail = LC-T096-5 × 4 mới, SL-T041-8 × 3 có từ trước). `tests/test_la_chan_t096.py`: 29 passed, 4 xfailed; `--runxfail`: 4 ca LC-T096-5 đỏ đúng lý do (`blocked` sai) | Có |
| Thử gộp với `main` | `origin/main` `5e1d831` (từ `0390a94`, lần thử gộp trước, chỉ đổi tài liệu: `TIEN-DO.md`, `docs/team/board.md`, `docs/team/security.md`, 3 phiếu): `git merge-tree` cây `e15c343`, **không xung đột**. Commit tạm `4048ffa` (không nhánh, không push) trong worktree tạm, kèm test của tôi: 12 file (T-096, T-039, T-041 AI, test ảnh/client của `main`: `test_wordpress_images`, `test_t059_*`, `test_soi_loi_t059`, `test_t083_*`, `test_soi_loi_t083`): **2.997 passed, 9 xfailed in 113.44s**, 0 hỏng (9 xfail = LC-T096-5 × 4 và xfail có sẵn trong test T-059, T-083). `ruff check .` sạch; E1 hạt giống 6: 1.500 bài, sót 0. Đã gỡ worktree tạm | Có |
| ruff | `uv run ruff check .`: `All checks passed!`; `ruff format` đã chạy cho file test của tôi | Có |
| bandit 1.9.4 | 4 file code của phiếu: 0 cảnh báo (B613 lượt trước đã hết) | Có |
| detect-secrets | **Đặt `PYTHONUTF8=1`**: 9 file đổi ở lượt 3, file test của tôi, bản vá `git log -p 12b905e..7ea52e8`, **file mồi có chữ tiếng Việt**: mồi bắt 2/2; còn lại 0. Soát lịch sử lượt 3 theo dạng khóa: 0 | Có. Đã xóa file mồi |

### Điều kiện (lượt 3)

Thay các điều kiện 1 → 6 của mục «Điều kiện» ở trên (đã xong). Còn:

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T096-5 (Thấp):** lớp chặn nhúng chặt hơn làm đúng điều kiện `isMatch` của Gutenberg (cách sửa ở bảng trên), gỡ 4 dấu `xfail`; đổi điều kiện ca `<p><a …>https://…</a> rồi</p>` của `test_embed_patterns_not_found` (Chỉ Huy duyệt) | Thợ Máy (T-096 lượt 4 ngắn, hoặc phần logic của T-102) | Trước khi T-102 nối bộ dựng |
| 2 | Điều kiện 7 (T-102: giới hạn cỡ bài khi dựng; hiện `ascii_host`, thẻ ảnh, ảnh đại diện, chữ thô theo `needs_escape`; dựng `ArticleImage.of(…, tags=draft.tags)` cùng trạng thái với `DraftImage`) và điều kiện 8 (kiểm lại bằng Claude Fable sau 01/11) giữ nguyên | Như trên | Như trên |

---

## Xem lại lượt 4 (2026-10-28, đầu nhánh `7da465f`)

| Mục | Nội dung |
|---|---|
| Phạm vi | Xem lại rút gọn: diff `1b45f5d..7da465f` (Thợ Máy lượt 4, sửa LC-T096-5; nhánh đã tua tới commit gộp `1b45f5d`): `seo_app/publish/review.py` (+36/−5: `_block_editor_embeds`, `_FILE_EXTENSION`, `_HTTPS`), `render.py` (câu báo Chặn), `tests/test_la_chan_t096.py` (−5, gỡ dấu `xfail`), `tests/test_publish_render.py` (+34/−1). Đọc lại mã Gutenberg `trunk` qua `raw.githubusercontent.com` (không gọi website): `packages/block-library/src/embed/transforms.js` (ba biểu thức `/^https:\/\//i`, `/https:\/\//gi`, `/\.(?!(html?\|php)$)[a-z0-9]+$/i`), `packages/url/src/is-url.ts` (chỉ `new URL(url)` trong `try`), `get-filename.ts` (`new URL(url, 'http://example.com').pathname`, lấy phần sau «/» cuối): bộ so `p_gutenberg_ismatch.js` của tôi khớp |
| Ngày | 2026-10-28 (16:00–16:30 và 17:30–17:46 +07, giờ máy đo bằng `date`; phiên bị ngắt giữa chừng vì hết lượt dùng) |
| **Kết luận lượt 4** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được**: **LC-T096-5 đóng**; 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới: LC-T096-6** (phần còn lại của LC-T096-5: tab trong tên máy, «\», thừa «/», tên đăng nhập có dấu cách), 5 ca `xfail(strict=True)` trong `tests/test_la_chan_t096.py`; sửa vài dòng trước khi T-102 nối bộ dựng (đã giả lập: sót 0, không ca nào khác đổi) |

### Tóm tắt lượt 4 (cho chủ dự án)

- Điểm nhỏ lần trước (đoạn «địa chỉ web + chữ phía sau» bị trình soạn của WordPress biến thành khối nhúng) **đã sửa đúng**: tôi cho bộ dựng chạy với 3.000 đoạn mẫu; cả 1.993 đoạn mà trình soạn sẽ nhúng đều bị chặn (trước khi sửa lọt 1.023). Đoạn có chữ đứng trước địa chỉ, có hai địa chỉ, hay chỉ `http://` vẫn qua bình thường.
- Còn **1 điểm nhỏ mới (Thấp)**: vài cách viết địa chỉ rất lạ (dấu tab chen trong tên trang, dấu «\», ba dấu «/», tên đăng nhập có dấu cách) trình soạn của WordPress vẫn hiểu là địa chỉ, bộ dựng chưa nhận ra. Người viết hay AI bình thường gần như không viết kiểu này, và theo mã WordPress thì máy chủ từ chối tải phần lớn các dạng đó. Sửa vài dòng (tôi đã thử: hết lọt), làm trước khi nối bộ dựng vào màn hình xác nhận (T-102). Hôm nay chưa có hại vì bộ dựng chưa nối vào giao diện.

### Kiểm từng việc

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| 1. LC-T096-5 đóng thật | **Đóng** | `p_gutenberg_compare.py 2 3000` (12 mẫu cố định + 3.000 mẫu ngẫu nhiên, như lượt 3): 2.959 đoạn, Gutenberg nhúng 1.993, **bộ dựng không Chặn 0** (lượt 3: 1.023). 4 ca của tôi qua sau khi gỡ dấu `xfail` |
| 2. Không chặn oan | **Đạt** | 3 ca canh của tôi (`test_lc5_url_not_at_start_or_not_https_is_not_blocked`) và 7 ca của Soi Lỗi (`test_url_with_other_text_is_not_an_embed`: giữa câu, hai địa chỉ, `<…>`, link và ảnh Markdown, ký tự rộng 0 đứng đầu, xuống dòng mềm) qua; trong bộ so biên, mọi đoạn Gutenberg không nhúng mà bộ dựng Chặn chỉ có dạng đuôi tệp viết hoa (Quan sát lượt 4) |
| 3. R5 | **Đúng** | `git diff 1b45f5d..7da465f -- tests/`: `test_la_chan_t096.py` chỉ xóa 1 dấu `xfail` (4 ca), không `assert` nào đổi; `test_publish_render.py`: đúng một ca được duyệt (`<p><a …>https://…</a> rồi</p>`) chuyển khỏi `test_embed_patterns_not_found` sang test mới mong được bắt, đúng chữ `"https://suachuacuasat.com/x/ rồi"`; hai ca còn lại của test cũ giữ nguyên; thêm `test_block_editor_embed_conditions` (13 ca) |
| 4. Không lùi, không chạy lâu | **Đạt** | 7 file test T-096 (đúng bộ Thợ Máy chạy, gồm ca LC-T096-1 → -4, LC-T039-2, SL-T096): **900 passed**. E1 (`p_embed_oracle.py 41 3000`, đúng hai biểu thức `autoembed`, chuỗi gửi kèm `<figure>`): WordPress nhúng 2.193 bài, **sót 0** (chặn thêm 700 do lớp chặt hơn). E2 (`p_markup_fuzz.py 41 1500`, chữ độc qua cả bộ dựng): **0 vi phạm**. Tốc độ (`p_speed96_l4.py`): `_block_editor_embeds`, `embedded_urls`, `build_article` với 10 dạng chữ độc dài (nhiều dấu chấm, chấm và chữ xen kẽ, một đuôi dài, nhiều «/», nhiều «@», tên máy dài, dãy dấu cách, «?#» lặp, «\» lặp, «https:/» lặp), cỡ 200.000 → 800.000 ký tự: tỉ lệ 2,6–6,4 (tuyến tính khoảng 4, ngưỡng dự án 9), lâu nhất 0,19 giây; `_FILE_EXTENSION` dùng lượng từ chiếm hữu `++` nên không quay lui. Ca quét ký tự trần (LC-T096-3) qua |
| 5. Gộp thử `main` `d1506cb` (T-090, T-097) | **Đạt** | Gốc chung `1b45f5d`; hai bên không chung file nào; `git merge-tree` cây `997ef9b`, **không xung đột**. Commit tạm `dd957c0` (không nhánh, không push), worktree nháp: 21 file (7 file T-096; 8 file T-090: `test_t090_env_bang_ma.py`, `test_t090_meta_emoji_moi.py`, `test_soi_loi_t090.py`, `test_la_chan_t090.py`, `test_onpage_meta.py`, `test_onpage_schema.py`, `test_t041_meta.py`, `test_t041_schema.py`; 4 file T-097: `test_google_service_account.py`, `test_google_sheets.py`, `test_la_chan_t097.py`, `test_soi_loi_t097.py`; `test_config.py`, `test_env_file.py`), 17:36:26 → 17:42:38: **2.378 passed, 7 skipped, 44 xfailed, 0 hỏng**. 44 `xfail` đều là lỗi đã biết có sẵn trên `main` (chạy lại riêng 6 file có dấu `xfail`: 768 passed, 44 xfailed): `test_la_chan_t090.py` 17 (LC-T090-1, -2), `test_la_chan_t097.py` 11, `test_soi_loi_t097.py` 16; không ca nào của T-096. 7 bỏ qua là điều kiện bỏ qua có sẵn |

### Lỗi mới (lượt 4)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T096-6 | Thấp (phần còn lại của LC-T096-5, cùng điều kiện) | **`_block_editor_embeds` tách tên máy đơn giản hơn bộ phân tích URL của trình duyệt (WHATWG, `new URL`).** Các dạng `new URL` vẫn nhận nên khối Embed vẫn nhúng, mà bộ dựng không Chặn: (a) tab (U+0009) trong hay ngay sau tên máy (WHATWG bỏ tab, xuống dòng ở mọi chỗ); (b) «\» sau tên máy (với `https`, WHATWG coi «\» như «/»); (c) thừa «/» sau `https://` (`https:///evil.example/…`: WHATWG bỏ qua); (d) tên đăng nhập, mật khẩu có dấu cách (`https://a b@evil.example/x`: WHATWG mã hóa thành `%20`, tên máy là phần sau «@») | `seo_app/publish/review.py:334-341` (cắt tên máy chỉ ở «/», «?», «#»; không bỏ tab, không bỏ «/» thừa, không bỏ phần trước «@») | Bộ so biên mới (`p_gutenberg_edge.py`): 36 ca dựng tay, **7 sót** (2 tab, 1 «\», 2 thừa «/», 2 tên đăng nhập); 3.027 đoạn ghép ngẫu nhiên từ các mảnh biên: Gutenberg nhúng 1.272, bộ dựng **sót 752** (tên đăng nhập 272, tab 224, «\» 158, thừa «/» 98). Đường đi: chữ AI hay chữ dán có đoạn mở đầu bằng dạng trên rồi tới chữ → bộ dựng không Chặn → nháp lên WordPress → mở nháp, bấm «Chuyển thành khối» → khối Embed. Hậu quả có lẽ nhỏ hơn LC-T096-5 (đọc mã WordPress, chưa thử trên site): proxy oEmbed làm sạch URL bằng `sanitize_url` (bỏ tab, «\») và `wp_http_validate_url` từ chối URL có tên đăng nhập hay hỏng («///»), nên chỉ dạng tab thành URL hợp lệ, có thể tải trang ngoài vào khung xem trước của trình soạn. Xuống dòng mềm không lọt: bộ chuyển đổi nó thành dấu cách | Trong `_block_editor_embeds`, trước khi tách tên máy làm như WHATWG: bỏ U+0009, U+000A, U+000D; bỏ «/», «\» thừa ngay sau `https://`; «\» cũng là dấu chia (cả khi lấy tên file); tên máy là phần sau «@» cuối cùng. Giả lập (`fixsim6/lc966_fix.py`, khoảng 6 dòng): bộ so cũ 1.993 nhúng, sót 0; bộ so biên 36 ca và 3.027 đoạn, sót 0; 7 file test T-096 cộng test mới: 903 qua, chỉ 5 ca `xfail` LC-T096-6 thành XPASS, không ca nào khác đổi (cả 13 ca của Thợ Máy, 3 ca canh mới của tôi) |

### Quan sát lượt 4 (không tính là lỗi)

- **Đuôi tệp viết hoa:** chú thích của `_FILE_EXTENSION` (`review.py:66-68`) và ca `("https://x.vn/xem video.MP4", True)` của `test_block_editor_embed_conditions` cho rằng biểu thức của Gutenberg phân biệt hoa thường. Mã Gutenberg có cờ `i` (`/\.(?!(html?|php)$)[a-z0-9]+$/i`), nên Gutenberg **không** nhúng `https://x.vn/xem video.MP4`; bộ dựng Chặn: chặt hơn, chỉ chặn oan đoạn mở đầu bằng địa chỉ tệp viết hoa (rất hiếm). Không bắt buộc sửa; nếu muốn khớp thì thêm `re.IGNORECASE` và đổi ca «.MP4» (R5, Chỉ Huy duyệt), hoặc chỉ sửa chú thích.
- **T-102:** `review.embeds` nay có thể là cả một đoạn chữ của người viết hay AI (ví dụ `"https://suachuacuasat.com/x/ rồi"`), không chỉ một địa chỉ. Màn hình xác nhận phải hiện mục này như chữ thường đã escape (U1) và cắt ngắn khi dài; gộp vào điều kiện 7.
- Lớp mới xét mọi khối chữ (mục danh sách, ô bảng, tiêu đề), Gutenberg chỉ xét `<p>`: chặt hơn, cùng hướng với LC-T096-4 đã duyệt (Thợ Máy đã ghi).

### Tự sửa file test của tôi (`tests/test_la_chan_t096.py`, lượt 4)

Thêm mục LC-T096-6 ở lời mô tả và cuối file: `test_lc6_url_forms_new_url_accepts_are_blocked` (5 ca `xfail(strict=True)`: tab trong tên máy, tab sau tên máy, «\», thừa «/», tên đăng nhập có dấu cách) và `test_lc6_invalid_url_with_text_is_not_blocked` (3 ca canh: dấu cách ngay sau tên máy, cổng có dấu cách, dấu cách không ngắt trong tên máy: `new URL` từ chối nên không được Chặn). Ký tự lạ viết bằng `chr(…)`; quét lại: không ký tự trần. Không đổi ca cũ nào.

### Kết quả công cụ quét (lượt 4)

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest, nhánh | 7 file test T-096 (bộ Thợ Máy chạy): **900 passed in 116.37s**. `tests/test_la_chan_t096.py` sau khi thêm LC-T096-6: **36 passed, 5 xfailed** | Có |
| pytest, giả lập sửa LC-T096-6 | `PYTHONPATH=<fixsim6> uv run pytest -p lc966_fix` 7 file + test mới: 903 passed, 5 failed (đúng 5 ca `XPASS(strict)` LC-T096-6) | Có |
| Thử gộp với `main` | Xem việc 5 | Có |
| ruff | `uv run ruff check .`: `All checks passed!`; `ruff format --check tests/test_la_chan_t096.py`: đã định dạng | Có |
| bandit | `review.py`, `render.py` (916 dòng): **No issues identified** | Có |
| detect-secrets | **Đặt `PYTHONUTF8=1`**, `--all-files` trong thư mục nháp: 5 file đổi ở lượt 4 (kèm file test của tôi), bản vá `git log -p 1b45f5d..7da465f`, **file mồi có chữ tiếng Việt**: mồi bắt 2/2; còn lại 0. Soát bản vá theo dạng khóa: 0 | Có. Đã xóa file mồi |

### Điều kiện (lượt 4)

Thay điều kiện 1 của mục «Điều kiện (lượt 3)» (LC-T096-5: đã xong). Còn:

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T096-6 (Thấp):** `_block_editor_embeds` tách tên máy như WHATWG (cách sửa ở bảng trên), gỡ 5 dấu `xfail` (R5) | Thợ Máy (T-096 lượt 5 ngắn, hoặc phần logic của T-102) | Trước khi T-102 nối bộ dựng |
| 2 | Điều kiện 7 (T-102), thêm: hiện `review.embeds` như chữ thường đã escape, cắt ngắn (Quan sát lượt 4); điều kiện 8 (kiểm lại bằng Claude Fable sau 01/11) giữ nguyên | Như trên | Như trên |

Script thử của lượt này (thư mục ghi chú chung `T-096-la-chan-scripts/`, chạy trong worktree `PYTHONUTF8=1 uv run python <script>`): `p_gutenberg_edge.py [hạt giống] [số mẫu]` (ca biên WHATWG), `p_run_fixed.py <tên script> …` (chạy bộ so với bản vá giả lập `fixsim6/lc966_fix.py`), `p_speed96_l4.py` (tốc độ lớp mới).

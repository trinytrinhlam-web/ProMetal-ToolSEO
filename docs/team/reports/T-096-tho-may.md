# Báo cáo T-096 · Bộ dựng bài cuối: Markdown → HTML, kiểm link, dữ liệu xác nhận

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-096](../tickets/T-096-bo-dung-bai-cuoi.md) |
| Ngày nộp | 2026-10-28 00:18 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đã làm **bộ dựng bài cuối**: phần chuyển bài viết (dạng Markdown trong app) thành HTML gửi WordPress. Nay bài lên website giữ được **in đậm, nghiêng, gạch đầu dòng, danh sách đánh số, bảng, tiêu đề con, trích dẫn**. Trước đây mỗi đoạn chỉ là chữ thường.
- Link trong chữ (do AI hay người gõ) **không bao giờ** thành link bấm được. Link duy nhất trong bài là link nội bộ app tự chèn, trỏ tới bài đã đăng trên website. Đoạn dạng shortcode `[...]` vẫn bị vô hiệu.
- Bộ dựng trả sẵn dữ liệu cho **màn hình xác nhận** (phiếu T-102 sẽ hiện ra):
  - mọi link, kèm tên miền dạng mã `xn--` để lộ tên miền giả chữ;
  - địa chỉ web, email còn dạng chữ trong bài;
  - đoạn dạng shortcode;
  - ảnh còn GPS;
  - các lỗi **Chặn** / **Cảnh báo**.
- Chặn được trường hợp **đoạn chỉ có một địa chỉ web** (WordPress sẽ tự nhúng cả trang đó vào bài), ở **mọi** hình thức gửi, kể cả Nháp.
- Có **mã xác nhận**: đổi một ký tự bất kỳ trong bài, ảnh, SEO, giờ hẹn thì mã khác. Nhờ vậy T-102 biết chắc thứ gửi đi đúng là thứ chủ dự án đã xem.
- Chưa nối vào giao diện: nút «Gửi nháp» vẫn chạy như cũ cho tới phiếu T-102.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/publish/markdown.py` (mới) | Bộ chuyển Markdown → HTML: khối (đoạn, tiêu đề con, danh sách lồng, bảng GFM, trích dẫn, kẻ ngang, khối mã) và trong dòng (đậm, nghiêng, `mã`, `\` escape, mã ký tự `&…;`, xuống dòng cứng). Không sinh `<a>`, `<img>`, HTML thô; mọi chữ `html.escape` rồi `escape_shortcodes` |
| `seo_app/publish/review.py` (mới) | Dữ liệu màn hình xác nhận: `link_rows`, `address_flags`, `bare_addresses`, `embedded_urls` (đúng hai biểu thức `WP_Embed::autoembed` + một lớp chặt hơn), `block_texts` |
| `seo_app/publish/render.py` (mới) | `build_article` → `BuiltArticle` (các phần HTML cuối, tiêu đề, slug, chuyên mục, thẻ, ảnh, SEO, hình thức, giờ hẹn, `ArticleReview`, mã băm); `content_parts` ghép ảnh cho `create_draft_with_images`; `digest_of`, `plain_line` |
| `seo_app/onpage/links.py` | **Chỉ** `place_links`: sửa LC-T039-2 đúng cách Lá Chắn T-039 chỉ ra. Nút chữ gốc không có `[` `]` trần thì in lại bằng `escape_shortcodes(html.escape(…))`; nút có `[` `]` trần giữ như cũ. Điều kiện LC-T094-10 bắt sửa ở phiếu này. `markdown_blocks` **không đổi** |
| `tests/test_la_chan_t039.py` | Gỡ `xfail(strict=True)` của 3 ca LC-T039-2 (đã XPASS), **không đổi `assert`** |
| `tests/test_publish_markdown.py` (mới) | 76 ca: mẫu đối kháng, khối, trong dòng, thử ngẫu nhiên 5.000 bài, khớp `markdown_blocks`, đo tốc độ tuyến tính |
| `tests/test_publish_render.py` (mới) | 71 ca: thứ tự lọc/chèn/kiểm, ký tự ngắt, tiêu đề, nhúng, cờ link, địa chỉ trần, shortcode, ảnh, mã băm, đầu vào sai |

Không sửa `seo_app/wordpress/**`, `app/**`, `config/**`, `seo_app/storage/**`.

## Cách T-102 dùng (hợp đồng)

```python
from seo_app.publish.render import ArticleImage, ArticlePart, SeoFields, build_article

built = build_article(
    title=S.article_title,                       # chữ thô như trong nháp
    parts=[ArticlePart(S[f"heading-{pid}"], current_text(pid)) for pid in S.part_ids],
    index=site_index_vua_tai_lai,                # SiteIndexStore.refresh ngay trước (LC-T094-36)
    links=[link.to_link() for link in draft_seo.links if link.use],
    required_ids=candidates.required_ids,
    images=[ArticleImage(section=k, sha256=băm_byte, alt=alt, caption=cap, featured=…, has_gps=…)],
    slug=…, categories=…, tags=…,
    seo=SeoFields(title, description, focus_keyword, write=S.seo_write),
    mode="draft" | "future" | "publish", date_gmt="" | "YYYY-MM-DDTHH:MM:SS",  # T-099 schedule
)
built.review          # bảng link, địa chỉ trần, chỗ nhúng, shortcode, ảnh, problems (Chặn/Cảnh báo)
built.review.blocked  # True: khóa nút gửi
built.digest          # lưu cùng ô tick lúc hiện màn hình; ngay trước lệnh mạng đầu tiên: built2.matches(digest)
client.create_draft_with_images(built.title, built.content_parts({k: DraftImage(...)}),
                                slug=built.slug, categories=built.categories, tags=built.tags,
                                excerpt=built.excerpt)
```

- Phần 0 không có `<h2>` (mở bài), từ phần 1 có `<h2>` tiêu đề phần, như `article_parts` cũ. Số phần trùng `InternalLink.section`.
- `content_parts` chỉ nhận ảnh **đúng** các phần đã khai trong `build_article` (thiếu hay thừa: `BuildError`).
- `create_draft` vẫn chạy `sanitize_html` lần cuối. Kết quả không đổi vì đầu ra bộ dựng đã sạch (test `assert sanitize_html(out) == out`).
- `ArticleReview.needs_escape = True`: mọi chữ trong review là chữ thô (chữ AI, chữ người gõ, tiêu đề bài trên site). Phải hiện bằng ô bảng, `st.text` hoặc `escape_markdown`, link không bấm được (U1, LC-T094-3, LC-T094-37).

## Đối chiếu điều kiện Lá Chắn (LC-T094-n)

### Chung cho mọi phiếu Giai đoạn 5

| Mã | Đáp ứng ở đâu |
|---|---|
| LC-T094-1 | Test không gọi mạng: danh sách bài dựng tay (`SiteIndex(...)` trong test), không client nào được tạo. Bộ chặn mạng `tests/conftest.py` vẫn bật (không đụng) |
| LC-T094-2 | Câu lỗi mới đều cố định: `render._MSG_BAD_INPUT`, `_MSG_SPLIT` (`BuildError`), chỉ có tên phần sai (không chép dữ liệu). Bộ dựng không đọc lời máy chủ nào. Test `test_bad_input_raises_fixed_message` (18 ca) |
| LC-T094-3 | Phần giao diện thuộc T-102. Ở đây: dữ liệu trả chữ thô kèm cờ `needs_escape`. Bộ chuyển bỏ ký tự điều khiển hướng chữ U+202A–U+202E, U+2066–U+2069 và ký tự điều khiển khỏi bài (`markdown._DROPPED`; test `test_dropped_characters`) |

### T-096

| Mã | Đáp ứng ở đâu | Test |
|---|---|---|
| LC-T094-4 | `markdown.py`: chỉ sinh `p`, `h3`–`h6`, `strong`, `em`, `code`, `pre`, `br`, `hr`, `ul`, `ol`, `li`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `blockquote`; thuộc tính duy nhất là `start` của `<ol>`. Mọi chữ qua `escape_text` = `escape_shortcodes(html.escape(…))`. `<a>` chỉ do `place_links` (`href` từ `SiteIndex`); `<img>` chỉ do `figure_html` của client | `test_hostile_markdown_never_makes_links_or_raw_html`: 28 mẫu (T-015, T-031, T-061: `javascript:`, `data:`, `&#106;avascript:`, `[x][1]` + `[1]: url`, tiêu đề có `\"`, U+200B trong địa chỉ, `\[`, `\<`, `<!-- wp:core/rss … /-->`, CDATA, `<?php`, `<img onerror>`, `<iframe>`, shortcode, bảng, danh sách, trích dẫn, khối mã), mỗi mẫu chạy 3 dạng (thô, `clean_ai_text`, đã gỡ ký tự ngắt): chỉ thẻ trong danh sách, lồng đúng, không chú thích, không `[` `]` trần, `sanitize_html(out) == out`. Thêm thử ngẫu nhiên 3.000 + 2.000 bài |
| LC-T094-5 | `render.build_article`: `sanitize_html` → `place_links` → `sanitize_html` → `check_links(…, required_ids)` trên **một** chuỗi. Sau `check_links` chỉ cắt theo `<h2>`, có kiểm `"\n".join(sections) == final` (`_split`). Mã băm tính trên `sections` | `test_order_filter_link_filter_check_on_the_same_string`: bọc 3 hàm, đúng thứ tự, mỗi bước nhận đúng đầu ra bước trước, `built.html` đúng chuỗi `check_links` đã kiểm |
| LC-T094-6 | `review.embedded_urls`: đúng hai biểu thức của `WP_Embed::autoembed` (khoảng trắng kiểu PCRE chỉ ASCII; `\n` trong thẻ đổi thành chỗ giữ như `wp_replace_in_html_tags`), cộng một lớp chặt hơn: khối (`li`, `td`, `pre`…) mà chữ chỉ là một địa chỉ. Có chỗ nhúng → **Chặn** ở mọi `mode` | `test_embed_patterns_are_found` (7 ca: `<p>https://youtube…</p>`, `<p> https://x </p>`, `<p class>` có tab và `\n`, địa chỉ đứng một dòng trong `<li>`, `<li>` chỉ có địa chỉ, `\r\n`, dòng trong `<pre>`), `test_embed_patterns_not_found` (giữa câu, chữ của `<a>` có chữ khác, `ftp:`), `test_url_alone_blocks_every_mode` (draft, future, publish) |
| LC-T094-7 | `ArticleReview`: `links` (mọi `href` theo thứ tự `check_links`, chữ neo, `host`, `ascii_host` punycode, cờ: chữ ngoài ASCII, dạng `xn--`, `@`, `\`, `//` đầu, cổng lạ, khác website), `bare` (địa chỉ web, `www.`, email còn trong chữ, kèm tên máy ASCII và cờ), `embeds`, `shortcodes` (tiêu đề, từng phần, alt, chú thích, vắt qua nhiều phần), `images` (mục, alt, chú thích, ảnh đại diện, GPS), `skipped_links`, `problems`; `needs_escape = True` | `test_link_rows_list_every_href_with_flags` (`suachuacuasаt.com` với «а» Kirin → `xn--suachuacuast-79j.com` + cờ; `.cоm` Kirin; `a@b`; `//evil`; `/\evil`; `:8080`; `xn--`; `mailto:`; link của site không cờ), `test_bare_addresses_in_text`, `test_review_lists_shortcodes_images_and_needs_escape` |
| LC-T094-8 | `render.digest_of`: SHA-256 của `json.dumps(…, ensure_ascii=False, sort_keys=True, separators=(",", ":"))` mã UTF-8, nửa cặp UTF-16 lẻ không làm lỗi (`surrogatepass`). Nội dung băm: phiên bản cách chuẩn hóa, hình thức, `date_gmt`, tiêu đề cuối, đoạn trích, slug, mã chuyên mục, mã thẻ, mọi phần HTML cuối, mỗi ảnh (phần, băm byte, alt, chú thích, ảnh đại diện, GPS), 3 ô SEO, công tắc ghi SEO. `BuiltArticle.matches` so bằng `hmac.compare_digest` | `test_digest_changes_with_any_part` (20 ca: tiêu đề, thân, tiêu đề phần, link, đoạn trích, slug, chuyên mục, thứ tự thẻ, băm ảnh, alt, chú thích, ảnh đại diện, phần của ảnh, bỏ ảnh, 3 ô SEO, công tắc SEO, hình thức), `test_digest_changes_with_schedule_time` (lệch 1 giây), `test_digest_is_deterministic_and_canonical`, `test_digest_survives_lone_surrogate` |
| LC-T094-9 | `unbreak_autolinks` chỉ chạy trong bộ dựng: thân (`_section_html`, trước `markdown_to_html`), tiêu đề bài, tiêu đề phần, đoạn trích (`plain_line` → `unescape_link_syntax`, hàm này gỡ trước). Chữ đã gỡ vẫn escape, lọc, kiểm địa chỉ trần | `test_autolink_breaks_removed_and_addresses_never_become_links`: chữ qua `clean_ai_text` (có U+200B) → HTML, tiêu đề không còn U+200B; chỉ 1 `<a>` (link nội bộ); 3 địa chỉ trần được liệt kê |
| LC-T094-10 | (a) LC-T039-2 sửa trong `place_links` **trước** khi bộ dựng dùng nó; gỡ 3 `xfail`. (b) `#`, `##`, `###` trong thân → `<h3>`, dòng gạch dưới → `<h3>`; `<h2>` chỉ là tiêu đề phần (`markdown._heading_tag`) | `tests/test_la_chan_t039.py` 6 ca qua (3 ca vừa gỡ `xfail`); `test_headings_never_h1_or_h2`, `test_body_never_has_h1_or_h2_and_one_h2_per_section`, `test_heading_text_is_escaped` |

### Board «Việc bắt buộc khi làm Giai đoạn 5» (phần thuộc bộ dựng)

| Dòng board | Ở đây |
|---|---|
| Markdown → HTML có escape, hiểu `\`, chuẩn hóa xuống dòng, không link tham chiếu | LC-T094-4; `test_backslash_escapes_follow_commonmark`, `test_all_newline_styles_are_the_same` (`\n`, `\r\n`, `\r`), `test_reference_definition_is_plain_text` |
| `sanitize_html` cho toàn bộ HTML cuối | LC-T094-5 (phần giao diện, chữ sửa tay: T-102, LC-T094-36) |
| Màn hình xác nhận liệt kê mọi `href`, đánh dấu `@` | Dữ liệu: LC-T094-7. Hiển thị: T-102 |
| URL trần không thành link | Bộ chuyển không có autolink; địa chỉ trần nằm trong `review.bare` |
| Gỡ U+200B trước khi gửi (thân, tiêu đề, meta) | LC-T094-9. Meta: `normalize_meta` của T-041 đã bỏ ký tự loại Cf (không đổi) |
| Kết quả `unescape_link_syntax`/`unbreak_autolinks` không vào `st.markdown` | `needs_escape`; T-102 kiểm |

## Bằng chứng

```
$ uv run pytest tests/test_publish_markdown.py tests/test_publish_render.py tests/test_la_chan_t039.py tests/test_onpage_links.py
435 passed in 33.80s

$ uv run pytest tests/test_soi_loi_t039.py tests/test_soi_loi_t041.py tests/test_t040_prompts.py \
    tests/test_t041_drafts_seo.py tests/test_t041_links_ai.py tests/test_t041_seo_ui.py
471 passed, 1 xfailed in 316.84s     # mọi file test khác có dùng seo_app/onpage/links.py
                                     # xfail có từ trước: SL-T041-8 (emoji mới, phiếu T-090)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/publish tests/test_publish_render.py tests/test_publish_markdown.py
6 files already formatted
```

Trước khi gỡ `xfail`, chạy `tests/test_la_chan_t039.py` trên bản đã sửa `place_links`: 3 ca LC-T039-2 báo `XPASS(strict)`, nghĩa là bản sửa đúng. Cùng lượt chạy, 285 ca khác của `test_la_chan_t039.py` + `test_onpage_links.py` qua.

Nơi gọi `place_links`/`apply_links` (grep `seo_app app tests`): chỉ có `tests/test_onpage_links.py`, `tests/test_la_chan_t039.py` và nay `seo_app/publish/render.py`. App chưa gọi.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: làm đúng dòng T-096 của thiết kế (`seo_app/publish/`), không đụng file của T-097 → T-103
- [x] Yêu cầu 2: LC-T094-1 → -10 (bảng trên)
- [x] Yêu cầu 3: 147 ca test mới; test cũ liên quan qua
- [x] Test liên quan + `ruff check .` sạch
- [x] Báo cáo này

## Rủi ro và điểm cần chú ý

- **Sửa ngoài `seo_app/publish/`**: `seo_app/onpage/links.py` (chỉ `place_links`) và `tests/test_la_chan_t039.py` (gỡ `xfail`). Hai chỗ này do LC-T094-10 bắt làm ở phiếu này. Đã grep nơi gọi và chạy test của chúng (mục Bằng chứng). `markdown_blocks` không đổi.
- **Dùng hàm riêng (tên có `_`) của `links.py`**: `_is_atx_heading`, `_is_list_item`, `_is_rule` (để chia khối đúng như `markdown_blocks`), `_browser_host`, `_hosts` (để tên máy ASCII khớp đúng cách `check_links` đọc). Cùng kiểu với `seo_app/wordpress/shortcodes.py` dùng `_SHORTCODE_OPEN` của client. Sửa các hàm đó thì phải chạy lại test của `seo_app/publish/`.
- **Bộ chuyển không phải CommonMark đầy đủ**: đậm/nghiêng lồng phức tạp (`*a **b* c**`) có thể ra khác trình hiển thị của Streamlit, nhưng thẻ luôn lồng đúng và an toàn. Thụt 4 dấu cách không thành khối mã (giống `markdown_blocks`). Chỗ bộ chuyển và `markdown_blocks` chia khối khác nhau (dòng `>` ngay sau đoạn văn) thì link nội bộ ở đó bị bỏ qua kèm câu báo, không bao giờ chèn sai chỗ.
- **Khác với «Gửi nháp» hiện nay khi T-102 nối vào**:
  - bài có định dạng thật (danh sách, đậm, bảng);
  - mục có tiêu đề rỗng bị Chặn;
  - ký tự điều khiển hướng chữ bị bỏ khỏi bài;
  - đoạn chỉ có một địa chỉ bị Chặn cả với Nháp.
- Lớp chặn nhúng «khối chỉ có một địa chỉ» chặt hơn WordPress: một mục danh sách chỉ ghi một địa chỉ cũng bị Chặn. Người dùng thêm chữ quanh địa chỉ là qua.
- Ký tự rộng 0 do **người** cài sẵn dạng mã `&#8203;` không phải ký tự ngắt của T-031: bộ dựng giải mã rồi giữ như chữ (vô hại, không tạo link).
- Bộ dựng có kiểm lỗi «Đăng ngay khi SEO chưa ghi» (Chặn) và «Hẹn giờ khi SEO chưa ghi» (Cảnh báo) theo thiết kế 3.2. T-102 vẫn phải tự kiểm theo LC-T094-39.

## Đề xuất

- T-102 (Họa Sĩ): dùng đúng hợp đồng ở mục «Cách T-102 dùng». Tính `digest` lúc hiện màn hình xác nhận, dựng lại và so ngay trước lệnh mạng đầu tiên (LC-T094-38). Hiện `ascii_host` cạnh mọi link ra ngoài (LC-T039-1).
- Soi Lỗi: thêm mẫu thật từ các bài đã viết (chỉ chữ) vào test bộ chuyển. Thử thêm tổ hợp danh sách lồng trong trích dẫn và bảng có `mã` chứa `|`.

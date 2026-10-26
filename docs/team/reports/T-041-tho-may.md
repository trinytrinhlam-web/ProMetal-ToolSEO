# Báo cáo T-041 · Bước 4 «SEO» chạy thật: phần logic (Thợ Máy)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Opus 5.5 |
| Phiếu | [T-041](../tickets/T-041-buoc-seo-that.md) |
| Ngày nộp | 2026-10-26 |
| Kết quả | Hoàn thành phần logic. Giao diện (`app/views/write.py`) là việc của Họa Sĩ, làm sau khi T-086 gộp |
| Nhánh | `team/T-041` (worktree `wt-T-041`), gốc `main` `2e04066` |

## Tóm tắt (cho chủ dự án)

- Phần "máy" của bước SEO đã sẵn sàng để Họa Sĩ gắn giao diện: gợi ý meta bằng AI (viết lại riêng tiêu đề hay mô tả), gợi ý đường dẫn (slug) và kiểm trùng với bài đã đăng, gợi ý liên kết nội bộ bằng AI, dựng dữ liệu Hỏi đáp (FAQ) cho Google từ mục Hỏi đáp của bài, và chữ sẵn để anh chép dán vào hộp SiteSEO.
- Mọi lựa chọn ở bước SEO (tiêu đề, mô tả kèm các bản trước để quay lại, slug, liên kết đã tick, có dùng FAQ không) **được lưu cùng bài nháp** như bước 1–3. Nháp cũ vẫn mở được.
- Đã làm đủ các điều kiện bảo mật và lỗi nhỏ mà các lần kiểm trước để lại cho phiếu này: bỏ ký tự rác vô hình trong meta, không bỏ oan gợi ý có chữ «xu hướng», bắt được chỗ nói giá dính sát từ khóa, tiêu đề 49 ký tự không còn bị chê «hơi ngắn», dữ liệu FAQ không còn dấu `**` hay địa chỉ link, danh sách «cụm nên tránh» trong `config/content.toml` mục `[meta]` nay **có tác dụng thật** (trừ khi cụm đó nằm trong từ khóa chính).
- Chưa có kết nối WordPress thì phần danh sách bài chỉ báo nhẹ «chưa kết nối», các phần khác vẫn dùng được. Khi file lưu tạm danh sách bài đang bị chương trình khác ghi dở, app chỉ chờ khoảng 1 giây thay vì 5,5 giây (đã đo trên máy Windows này).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/onpage/meta.py` | `normalize_meta` bỏ ký tự Cc (trừ khoảng trắng), Cs, Co, Cn (LC-T036-1). Đơn vị «xu» không tính khi là «xu hướng» (SL-T036-10). `has_link`, `mentions_price` coi chữ quá `MAX_SCAN_CHARS` (1.000) ký tự là «có» (SL-T036-12). `mentions_price` dò mọi vị trí, chỉ bỏ chỗ nằm trọn trong từ khóa (LC-T040-1). `find_avoided` (cụm nên tránh, cùng cách). `check_title(title, suffix)`: title không gắn được đuôi là «dài vừa» (SL-T040-1). `accept_ai_*`/`filter_ai_*` nhận `avoid`. Mới cho giao diện: `site_posts`, `SiteSeoCopy`, `siteseo_copy` |
| `seo_app/onpage/schema.py` | Chặn Cs, Co, Cn như ký tự điều khiển (LC-T038 đk 1). `plain_text`: bỏ Markdown ở cả bài lẫn câu hỏi/trả lời, link chỉ giữ chữ, ảnh chỉ giữ alt, không đổi sang HTML (LC-T038 đk 2). Mới: `find_faq`, `article_markdown`, `build_article_faq`, `MSG_NO_FAQ` |
| `seo_app/content/rules.py` | Mới: `MetaRules`, `load_meta_rules` (đọc mục `[meta]`) |
| `seo_app/content/workflow.py` | `ContentWriter(ai, rules, meta_rules=None)`; `meta()` đọc `[meta]` (đuôi thương hiệu, cụm nên tránh). Mới: `internal_links()` (điều kiện LC-T039 2a) |
| `seo_app/storage/drafts.py` | Mới: `DraftSeo`, `DraftMetaVersions`, `DraftLink`; trường `DraftSnapshot.seo` (mặc định trống). Khối SEO tách riêng để gộp với T-086 ít xung đột |
| `seo_app/storage/site_index.py` | Ghi cache chờ tối đa 1 giây (`_WRITE_TIMEOUT`, SL-T037-5 phần còn lại). Mới: `SiteListing`, `site_listing`, `MSG_NOT_CONNECTED`, `MSG_TRUNCATED` |
| `config/content.toml` | Chỉ chú thích: dòng «phần mềm CHƯA đọc mục [meta]» thành «phần mềm đọc mục [meta]…» (chính chú thích cũ hẹn bỏ dòng này khi nối xong; giữ đầu dòng `# LƯU Ý (T-040` vì test Soi Lỗi T-040 cắt file ở đó); thêm một câu: cụm nằm trong từ khóa chính thì không tính. Không đổi giá trị nào |
| `config/ai.toml` | Thêm `[tasks.links]` (như `[tasks.meta]`: Claude Opus 5.5, effort low, max_tokens 2000, **không** `web_search`) |
| `seo_app/content/blind_test.py` | Nhãn «Gợi ý liên kết nội bộ» cho việc `links` ở bảng mô hình (Cài đặt) |
| `tests/test_t041_meta.py` (mới, 82) | LC-T036-1 (chữ người dùng, JSON AI `\u0000`/`\u001b`, hậu tố), SL-T036-12, LC-T040-1, cụm nên tránh, SL-T040-1, `load_meta_rules`, `ContentWriter.meta` đọc `[meta]`, `site_posts`, `siteseo_copy` |
| `tests/test_t041_schema.py` (mới, 74) | Cs/Co/Cn, `plain_text`, Markdown hai phía, `javascript:`/tên miền lạ không vào JSON-LD, `<script>` giấu giữa dấu Markdown bị Chặn, `find_faq`, `build_article_faq` |
| `tests/test_t041_drafts_seo.py` (mới, 36) | Lưu/mở lại, nháp cũ, liên kết hỏng bỏ riêng, khối SEO hỏng bỏ riêng, chữ lạ được làm sạch, giới hạn |
| `tests/test_t041_site_index.py` (mới, 8) | Khóa ghi thật (`BEGIN IMMEDIATE`) cho `get`/`refresh`, `site_listing` |
| `tests/test_t041_links_ai.py` (mới, 7) | `[tasks.links]` không `web_search`, lời dặn không có địa chỉ, gợi ý được kiểm, từ chối `web_search`, AI → nháp → `apply_links` |
| `tests/test_soi_loi_t036.py`, `test_soi_loi_t038.py`, `test_soi_loi_t040.py`, `test_la_chan_t040.py` | Gỡ dấu `xfail` đã XPASS; 3 chỗ sửa nhiều hơn «chỉ xóa dấu», xin Chỉ Huy duyệt (mục «Test cũ đã đổi») |

Không sửa `app/**`, `seo_app/wordpress/**`, `seo_app/images/**`, `seo_app/onpage/links.py` (nên LC-T039-2 vẫn để cho phiếu bộ dựng HTML Giai đoạn 5, đúng điều kiện 3d). Không thêm thư viện. Không nâng số khuôn nháp (`SCHEMA_VERSION` vẫn 2): trường mới có mặc định nên nháp khuôn 1, 2 mở được; app cũ hơn mở nháp mới thì báo «bị hỏng» như khi nâng khuôn.

## Từng điều kiện → cách làm → test

| Điều kiện | Cách làm | Test |
|---|---|---|
| **LC-T038 đk 1, SL-T038-1**: chặn Cs, Co, Cn | `_ODD_CATEGORIES = {Cc, Cs, Co, Cn}` trong `_has_control` (`schema.py:146-151`); câu báo «có ký tự điều khiển hoặc ký tự lạ», không chép ký tự | `test_odd_chars_blocked` (6 ký tự × câu hỏi/trả lời), `test_validate_blocks_odd_chars_in_data`; gỡ xfail `test_lone_surrogate_blocked` |
| **LC-T038 đk 2, SL-T038-2 + lỗi 3**: bỏ Markdown nội dòng ở cả bài lẫn trả lời; link chỉ giữ chữ; ảnh bỏ/giữ alt; không đổi sang HTML; vẫn qua `_has_html` và `to_json_ld` | `plain_text` (`schema.py:211`): `unescape_link_syntax` (bỏ `\` app thêm) → `strip_markdown_links` (link → chữ, ảnh → alt, dòng khai báo link bỏ) → bỏ dấu tiêu đề/trích dẫn/gạch đầu dòng → bỏ dấu nhấn **có cặp** (`_strip_inline`, dấu lẻ như «2*3m» giữ nguyên) → `normalize_text`. Áp cho bài (`_prepare_article`) và cho câu hỏi/trả lời trong `build_faq_page`; JSON-LD chỉ mang chữ đã bỏ dấu. `validate_faq_page` so chữ trong dict với chữ người đọc thấy, nên dict còn `**` thì không khớp, bị Chặn | `test_markdown_both_sides_matches_and_json_is_plain` (12 ca, có `[x](javascript:alert(1))`, `![](https://tên-miền-lạ…)`), `test_html_hidden_between_markdown_marks_is_blocked` (6 ca: `<**script**>`, `` <`/script`> ``…), `test_markdown_never_becomes_html`, `test_plain_text` (17 ca), `test_plain_text_is_linear`; gỡ xfail `test_plain_answer_matches_markdown_formatted_article` (4 ca) |
| LC-T038 đk 3: giao diện hiện `json_ld` bằng `st.code` | Phần Họa Sĩ; ghi trong docstring `schema.py` và `build_article_faq` | Họa Sĩ |
| **LC-T036 đk 1 (LC-T036-1)**: bỏ Cc, Cs, Co, Cn ở chữ AI, chữ người dùng, hậu tố | `normalize_meta` (`meta.py:88`) giữ khoảng trắng (kể cả tab, xuống dòng, U+001C–001F, U+0085 để gộp), bỏ các loại còn lại; mọi kiểm meta và `resolve_brand_suffix` đều đi qua hàm này | `test_user_text_drops_odd_chars` (9 ký tự), `test_ai_json_with_control_chars_is_cleaned` (JSON thật `\u0000`, `\u001b` qua khuôn `MetaSuggestions`), `test_brand_suffix_drops_odd_chars`, `test_whitespace_control_chars_still_become_spaces` |
| **LC-T036 đk 2 (SL-T036-10)**: chỉ loại trừ đúng «xu hướng» | `xu(?!\s+hướng)` trong `_MONEY_UNIT` (`meta.py:483`); không đổi đơn vị nào khác | `test_r2_xu_huong_not_price` (2 ca, gỡ xfail). Ca «2 đô vật» (cùng mã lỗi) **không sửa** theo đúng điều kiện này, tách thành xfail riêng (mục «Test cũ đã đổi») |
| **LC-T036 đk 3 (SL-T036-12)** | Cắt ngay trong hai hàm: `_scan_text` (`meta.py:530`) chuẩn hóa (tuyến tính), quá 1.000 ký tự (đo cả sau NFKC) thì coi như **có** link/giá (hướng an toàn). Giao diện gọi với chữ dán dài bao nhiêu cũng không treo | `test_detectors_linear_on_long_text` (6 ca), `test_long_text_counts_as_found`; gỡ xfail `test_r2_public_detectors_linear` (3 ca) |
| **LC-T040-1** | `mentions_price` (`meta.py:565`) không xóa từ khóa; thử `_PRICE.match` ở mọi vị trí, bỏ qua chỗ khớp nằm trọn trong một lần xuất hiện của từ khóa (`_KeywordSpans`, tìm nhị phân); giữ cắt độ dài trước | `test_price_touching_keyword_is_found`, `test_price_words_inside_keyword_only_are_kept`; gỡ xfail `test_lc1_price_across_keyword_edge_is_dropped` (4 ca); 7 ca canh của Lá Chắn vẫn qua |
| **SL-T040-1** (title 49 ký tự) | `check_title(title, suffix)` (`meta.py:160`): title **chưa có đuôi**, ở khoảng «hơi ngắn», mà cộng đuôi thì quá 60 (không gắn được) thì ghi «dài vừa … (không còn chỗ gắn đuôi thương hiệu)». Ngưỡng Cảnh báo, ngưỡng 50–60 với title có đuôi giữ nguyên; không dùng đuôi (`""`) thì như cũ | `test_title_too_long_for_suffix_is_not_short`, `test_title_suffix_band_depends_on_suffix` (5 ca), `test_title_with_suffix_or_too_short_keeps_old_rules`; gỡ xfail `test_sl_t040_1_title_of_49_chars_is_not_short` (lý do cũ vẫn đúng) |
| **Nối `[meta]`**; `avoid` phải bỏ từ khóa ra trước khi dò, cùng cách LC-T040-1 | `load_meta_rules` (`rules.py:511`): thiếu mục/khóa thì mặc định; `avoid` sai dạng → `ContentRulesError` nêu file, mục (không khóa trang Soạn bài, `load_rules` không đổi); `brand_suffix` sai dạng → đuôi mặc định (đúng chú thích). `ContentWriter.meta` đọc `[meta]` mỗi lần gọi (sửa file là có hiệu lực), `brand_suffix` truyền thẳng vẫn thắng. `find_avoided` (`meta.py:598`): như `find_banned` (trọn từ, không phân biệt hoa thường) trên chữ NFKC, chỗ khớp nằm trọn trong từ khóa thì bỏ qua, vắt qua mép vẫn tính | `test_find_avoided` (10 ca), `test_accept_ai_uses_avoid_with_keyword_exception`, `test_load_meta_rules_*` (11 ca), `test_writer_meta_*` (3); test có sẵn `test_keyword_with_price_or_avoid_word_is_kept_and_accepted` (từ khóa «sửa cửa uy tín hcm») vẫn qua |
| **SL-T037-5** | Đường «khóa hẳn» (`BEGIN EXCLUSIVE`) T-042 đã sửa. Còn đường «chương trình khác đang ghi dở» (khóa ghi, vẫn cho đọc): kiểm file qua được, bước ghi chờ đủ 5 giây. Đo trước khi sửa: `get` khi cache cũ mất **5,53 giây**. Sửa: `save` mở kết nối với `_WRITE_TIMEOUT = 1` (`site_index.py:51`, `:147`); ghi không được thì vẫn trả danh sách vừa tải kèm «đang bận». Đo sau khi sửa: **1,19 giây** | `test_pending_write_elsewhere_does_not_hang` (`get` và `refresh`, khóa thật bằng `BEGIN IMMEDIATE`, cache cũ còn nguyên sau đó) |
| **LC-T039 đk 2b**: nháp lưu `InternalLink` (`asdict` khi ghi, `InternalLink(**d)` trong `try` khi đọc, sai khuôn thì bỏ) | `DraftLink.from_link` = `cls(**asdict(link), use=…)`; mỗi lần tạo `DraftLink` dựng lại `InternalLink` (`to_link`, sai → `ValueError`); đọc từ file: liên kết sai khuôn bị bỏ riêng (`DraftSeo._drop_broken_links`). Không lưu địa chỉ; chèn link vẫn chỉ qua `apply_links`/`place_links` (kiểm lại từ đầu với danh sách bài lúc đó) | `test_broken_link_is_dropped_alone` (13 dạng hỏng: âm, 0, rỗng, quá dài, chữ thay số, `true`, trường lạ `href`…), `test_links_saved_as_asdict_without_address`, `test_suggestion_saved_in_draft_then_applied` |
| **LC-T039 đk 2a** (không có trong danh sách việc của tôi nhưng cần cho hàm «gợi ý liên kết nội bộ») | `ContentWriter.internal_links` (`workflow.py:325`): chỉ `_run("links", prompts.internal_links_prompt(title, parts, candidates.for_prompt()), LinkSuggestions)` rồi `check_suggestions`; `[tasks.links]` bật `web_search` thì từ chối trước khi gọi; không có bài đích thì không gọi AI. Commit riêng `39f2178`, Chỉ Huy bỏ được nếu muốn giao phiếu khác | `test_t041_links_ai.py` (7) |
| Trường SEO trong nháp, tự lưu, nháp cũ mở được | `DraftSnapshot.seo: DraftSeo` (mặc định trống). `DraftMetaVersions` (bản + bản đang dùng, như `DraftPart`; tối đa 20 bản; chỉ số lệch thì về bản cuối để lần tự lưu không hỏng). Chữ chuẩn hóa như meta, tối đa 500 ký tự. Khối SEO hỏng khi đọc từ file: bỏ cả khối SEO, chữ và ảnh của bài giữ nguyên; tạo trong code mà sai: lỗi ngay (lần tự lưu báo «Chưa lưu được nháp») | `test_t041_drafts_seo.py` (36) |
| Không có WordPress thì báo nhẹ «chưa kết nối», phần còn lại dùng được | `site_listing(store, None)` → `index=None`, `MSG_NOT_CONNECTED`. Các hàm còn lại không cần danh sách: `site_posts(None) == []` nên kiểm trùng ra Nên; meta, slug, FAQ chạy bình thường | `test_not_connected_is_a_gentle_notice`, `test_site_posts_from_index_feeds_duplicate_checks` |

## Hàm cho Họa Sĩ (giao diện bước SEO)

Mọi câu báo dưới đây là chữ thuần, có thể chứa **tiêu đề bài lấy từ website** (dữ liệu chưa tin cậy): hiện bằng `st.text`, `st.code`, ô bảng, hoặc `escape_markdown`/`html.escape` khi phải vào `st.markdown`, `st.caption`, HTML (U1; điều kiện LC-T036 số 5, LC-T037, LC-T039 2c).

**Danh sách bài đã đăng** (`seo_app.storage.site_index`)
- `site_listing(store: SiteIndexStore, source: WordPressClient | None, *, refresh=False) -> SiteListing(index: SiteIndex | None, notice: str)`. `source=None` khi `WordPressClient.from_settings` lỗi (giao diện đã có `wordpress_client()`): `notice = MSG_NOT_CONNECTED`. Nút «Tải lại danh sách bài» → `refresh=True`. Lỗi WordPress: `index=None`, `notice` = «Chưa tải được danh sách bài đã đăng. » + câu tiếng Việt của `WordPressError` (câu cố định kèm mã HTTP, T-060). `notice` còn có thể là `MSG_TRUNCATED` hay câu «đang bận» của file cache. Không ném lỗi WordPress ra giao diện. Danh sách: `listing.index.items` (`PublishedItem`: `id`, `type`, `slug`, `link`, `title`…).
- Kho cache: `SiteIndexStore()` (file `data/site_index.sqlite`); giữ một đối tượng cho cả trang như `draft_store()`.

**Meta** (`seo_app.onpage.meta`, `seo_app.content`)
- Gợi ý: `build_writer().meta(keyword, title, parts, which="both"|"title"|"description", current_title="", current_description="") -> MetaSuggestions(titles: list[str] ≤ 3, descriptions: list[str] ≤ 2)`. Viết lại riêng một ô: `which="title"` (truyền `current_description`) hoặc `which="description"` (truyền `current_title`); danh sách của ô kia rỗng. Title đã gắn đuôi « | Pro-Metal» khi còn chỗ. Lỗi: `AIError` (gọi qua `ai_call`), câu: «Chưa có từ khóa chính nên chưa gợi ý meta được…», «Các meta title AI gợi ý đều không đạt (…). Bấm viết lại.», «Các meta description AI gợi ý đều không đạt (…)», hoặc `ContentRulesError` «File config/content.toml, mục [meta]: «avoid» phải là danh sách chữ…».
- Kiểm ô người dùng sửa: `check_title(title, suffix) -> FieldCheck`, `check_description(text) -> FieldCheck`. `FieldCheck(field, value, length, level: Level.GOOD|WARN|BLOCK, messages: tuple[str, ...])`: `length` đã đếm NFC (thay `len()` thô ở bản demo), màu theo `level` (Nên / Cảnh báo / Chặn), `messages` là chữ thuần. Gộp nhiều mức: `worst(levels)`.
- Kiểm trùng: `posts = site_posts(listing.index)` (rỗng khi chưa kết nối); `check_title_duplicates(title, posts)`, `check_description_duplicates(desc, posts)`, `check_slug_duplicates(slug, posts)` → `FieldCheck` (câu báo có tên bài trên site: chữ thuần).
- Đuôi thương hiệu: `suffix = load_meta_rules().brand_suffix` (bọc `try … except AIError` như `alt_limits()`, lỗi thì `None` = đuôi mặc định); `with_brand(title, suffix) -> str`; `strip_brand(title, suffix)` để hiện ô sửa không đuôi.
- Xem trước Google: `ui.serp_preview(with_brand(title, suffix), url, description)` (đã escape).
- Chép sang SiteSEO: `siteseo_copy(title, description, slug, suffix=suffix) -> SiteSeoCopy(title|None, description|None, slug|None, checks)`: chữ cuối cùng (title đã gắn đuôi); trường bị Chặn là `None`, không cho chép, hiện `checks[i].messages`. Hiện bằng `st.code(...)` (có nút chép sẵn). Cùng chữ này dùng cho `set_seo_meta` của T-042 khi bật công tắc.

**Slug**
- Gợi ý: `make_slug(keyword_or_title, given=None) -> str` (không dấu, tối đa 60, bỏ từ nối cuối; `given` = slug người dùng gõ, chỉ đổi về dạng không dấu). Kiểm: `check_slug(slug) -> FieldCheck`, trùng: `check_slug_duplicates(slug, posts)`.

**Liên kết nội bộ** (`seo_app.onpage.links`, `seo_app.content`)
- Chọn bài đích: `candidates = select_candidates(listing.index, kind="huong_dan", title=article_title, keyword=keyword)` → `Candidates(items, notices)`; `notices[i].message` chữ thuần. App chưa nhập phiếu giao bài nên `required=()`, `kind` mặc định «hướng dẫn» (đổi được: `ArticleKind`).
- Gợi ý: `build_writer().internal_links(article_title, parts, candidates) -> LinkReview(links: tuple[InternalLink, ...], rejected: tuple[str, ...], missing_required)`. Không có bài đích: trả rỗng, không gọi AI. Lỗi: `AIError` (thiếu khóa, mạng…, hay «Việc gợi ý liên kết nội bộ không được bật web_search…»).
- Bảng «Dùng / Cụm từ trong bài / Trỏ tới bài»: mỗi `InternalLink` một dòng; «Trỏ tới bài» = tiêu đề của `post_id` trong `listing.index.items` (chữ thuần; không có thì «bài #id»). `rejected` là câu cố định, không chép chữ AI.
- Không gắn `<a>` ở đâu trong giao diện: link chỉ chèn qua `apply_links`/`place_links` khi dựng HTML (Giai đoạn 5).

**Schema FAQ** (`seo_app.onpage.schema`)
- `build_article_faq(parts) -> SchemaResult(page, json_ld: str | None, issues: tuple[Issue, ...])`; `result.blocked`. Bài chưa có mục Hỏi đáp: `issues == (Issue(BLOCK, MSG_NO_FAQ),)`. Hiện `json_ld` **chỉ** bằng `st.code(json_ld, language="json")` (LC-T038 đk 3); `issues[i].message` chữ thuần (không chép chữ của bài). `parts` là `current_parts()` (dạng chữ như trong session). Mục Hỏi đáp nhận ra: phần (không phải mở bài) có tiêu đề chứa «Hỏi đáp», «Câu hỏi», «Thắc mắc», «FAQ»; câu hỏi là `### …`, dòng `**…?**`, hoặc đoạn một dòng kết thúc «?».

**Nháp** (`seo_app.storage.drafts`)
- Ghi trong `snapshot()`: `seo=DraftSeo(title=DraftMetaVersions(versions=[…], current=i), description=…, slug=…, links=[DraftLink.from_link(link, use=bool) …], use_faq=bool)`.
- Đọc trong `open_draft()`: `snap.seo.title.versions/current/text`, `snap.seo.slug`, `[(d.to_link(), d.use) for d in snap.seo.links]`, `snap.seo.use_faq`. Phần SEO hỏng (sửa tay) thì đã thành trống, phần còn lại của bài vẫn mở.

## Test cũ đã đổi (xin Chỉ Huy duyệt)

| File · test | Đổi gì | Vì sao |
|---|---|---|
| `test_soi_loi_t036.py::test_r2_xu_huong_not_price` | Bỏ `xfail`, bỏ ca «2 đô vật» khỏi danh sách; ca đó thành test mới `test_r2_do_vat_not_price`, vẫn `xfail(strict=True)`, lý do «chưa sửa, điều kiện Lá Chắn T-036 số 2 chỉ cho loại trừ đúng «xu hướng»» | Cùng mã SL-T036-10 nhưng điều kiện LC-T036 số 2 chỉ cho loại trừ «xu hướng». Chỉ xóa dấu thì ca «đô vật» làm test đỏ (strict) |
| `test_soi_loi_t038.py::test_bold_answer_raw_markdown_passes_and_leaks_asterisks` | Đổi tên `…_passes_without_asterisks`, khẳng định JSON-LD **không** còn `**` (bằng đúng câu trả lời chữ thường) | Test cũ ghi lại hành vi lỗi SL-T038-2 (JSON-LD mang `**`), không phải `xfail` |
| `test_soi_loi_t040.py::test_not_read_yet_note_is_above_meta_and_true` | Đổi tên `test_read_note_is_above_meta_and_true`: ghi chú là «phần mềm đọc mục [meta]», không còn «CHƯA đọc»; cụm chỉ có trong `avoid` bị bỏ khi dùng `load_meta_rules().avoid` | Test cũ ghi lại trạng thái «chưa nối [meta]», nay đã nối |
| Gỡ dấu `xfail` (chỉ xóa dấu, lý do cũ đúng) | `test_r2_public_detectors_linear` (SL-T036-12), `test_lone_surrogate_blocked` (SL-T038-1), `test_plain_answer_matches_markdown_formatted_article` (SL-T038-2), `test_lc1_price_across_keyword_edge_is_dropped` (LC-T040-1), `test_sl_t040_1_title_of_49_chars_is_not_short` (SL-T040-1) | XPASS |

Còn vài docstring cũ nói «xfail tới khi sửa» / «chưa đọc mục [meta]» (`test_la_chan_t040.py` dòng 1, `test_soi_loi_t040.py` dòng 11 và docstring `test_broken_meta_section_does_not_lock_any_reader`, `test_soi_loi_t038.py::test_lone_surrogate_output_is_at_least_valid_json` nay luôn qua vì kết quả bị Chặn): tôi không sửa (chỉ được xóa dấu); Soi Lỗi dọn khi tiện.

## Bằng chứng

Windows 11, Git Bash, worktree `wt-T-041`, code tại `5cf42bc` (commit sau đó chỉ thêm báo cáo này).

```
$ uv run pytest tests/test_onpage_meta.py tests/test_onpage_schema.py tests/test_onpage_links.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_site_index.py \
    tests/test_site_index_t042.py tests/test_soi_loi_t037.py tests/test_soi_loi_t042_paging_cache.py \
    tests/test_app_drafts.py tests/test_soi_loi_t036.py tests/test_soi_loi_t038.py \
    tests/test_soi_loi_t039.py tests/test_la_chan_t039.py tests/test_la_chan_t040.py \
    tests/test_soi_loi_t040.py tests/test_t040_prompts.py tests/test_content_rules.py \
    tests/test_content_workflow.py tests/test_t062_content_config.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t016_t020.py tests/test_blind_test.py tests/test_settings_blind.py \
    tests/test_t062_image_config.py tests/test_soi_loi_t062.py tests/test_config_tolerance.py \
    tests/test_ai.py tests/test_ai_t034.py tests/test_soi_loi_t034.py tests/test_t041_meta.py \
    tests/test_t041_schema.py tests/test_t041_drafts_seo.py tests/test_t041_site_index.py \
    tests/test_t041_links_ai.py tests/test_app_pages.py tests/test_app_images.py
2969 passed, 8 skipped, 8 xfailed in 556.39s (0:09:16)

$ uv run ruff check .
All checks passed!
```

0 hỏng, không ca nào hết giờ. 8 `xfail` còn lại đều có chủ đích: SL-T036-11 (4 cách nói giá còn lọt, không bắt buộc), SL-T036-10 phần «2 đô vật» (1, giữ theo điều kiện Lá Chắn T-036 số 2), LC-T039-2 (3, để phiếu bộ dựng HTML Giai đoạn 5 theo điều kiện 3d vì phiếu này không sửa `links.py`). 8 `skipped` có từ trước, bằng đúng số lúc chưa sửa (test cần tạo symlink hay quyền kiểu POSIX, không chạy trên Windows).

Trước khi sửa (29 file có sẵn của danh sách trên, tức trừ `test_ai.py`, `test_ai_t034.py`, `test_soi_loi_t034.py` và 5 file `test_t041_*`; `main` `2e04066`): `2480 passed, 8 skipped, 23 xfailed in 595.59s`. Số `xfail` giảm 23 → 8: gỡ 16 ca đã sửa, thêm lại 1 ca «đô vật».

Đo SL-T037-5 (script trong thư mục nháp của phiên, kết nối khác giữ `BEGIN IMMEDIATE` + một lệnh ghi): `get` khi cache cũ **5,53 giây → 1,19 giây**; ca `BEGIN EXCLUSIVE` (T-042 đã sửa) 1,7–1,9 giây cả trước lẫn sau.

Thử gộp (chỉ đọc, `git merge-tree --write-tree`): với `origin/main` `9a1308d` và với `origin/team/T-086` `801fbdf`: **không xung đột**.

`PYTHONUTF8=1 uvx detect-secrets scan` trên 15 file của phiếu: 1 báo «Secret Keyword» ở `tests/test_t041_schema.py:209`, là chuỗi mồi cố ý `MA-BI-MAT-T041` để kiểm câu báo không chép chữ của bài (cùng cách `tests/test_soi_loi_t038.py` dùng `MA-BI-MAT-123`). Không có bí mật thật.

## Đối chiếu tiêu chí xong (phần Thợ Máy)

- [x] Điều kiện LC-T038 đk 1–2, SL-T038-1, -2 (bảng trên; `test_t041_schema.py`, xfail đã gỡ)
- [x] Điều kiện LC-T036 đk 1–3 (LC-T036-1, SL-T036-10, SL-T036-12)
- [x] LC-T040-1, SL-T040-1, nối `[meta]` (avoid bỏ từ khóa ra trước khi dò)
- [x] SL-T037-5 (phần còn lại, có test khóa thật)
- [x] LC-T039 đk 2b (và 2a, commit riêng)
- [x] Trường SEO trong nháp, `extra="forbid"`, nháp cũ mở được
- [x] Danh sách hàm cho Họa Sĩ (mục trên)
- [x] Test không gọi AI, WordPress hay mạng thật (provider giả, nguồn giả; bộ chặn mạng `autouse` của `tests/conftest.py` vẫn bật)
- [ ] Giao diện bước SEO, test `AppTest`, báo cáo Họa Sĩ: việc của Họa Sĩ, sau khi T-086 gộp

## Rủi ro và điểm cần chú ý

- **Tìm mục Hỏi đáp là đoán theo cách viết.** Lời dặn viết bài chưa quy định dạng mục Hỏi đáp; `find_faq` nhận các dạng hay gặp (`### câu hỏi?`, `**câu hỏi?**`, đoạn một dòng có dấu hỏi). Dạng khác (ví dụ «Hỏi: … / Đáp: …») thì báo «chưa có mục Hỏi đáp» hoặc thiếu câu. Không có hại về an toàn: cặp nào cũng phải có nguyên văn trong bài và qua mọi bộ kiểm.
- `plain_text` là bản gần đúng của cách Markdown hiển thị (không phải bộ đọc CommonMark đầy đủ): bài và câu trả lời luôn qua cùng một cách nên khớp nguyên văn không sai; chữ trong JSON-LD có thể khác chữ hiển thị ở ca hiếm (dấu huyền ngược lẻ bị bỏ, nhấn lồng lạ).
- Ký tự «chưa gán» (Cn) tính theo bảng Unicode 15.0 của Python 3.12: biểu tượng cảm xúc mới hơn bị bỏ khỏi meta và làm câu FAQ bị Chặn.
- `has_link`/`mentions_price` với chữ quá 1.000 ký tự trả «có» (cố ý, hướng an toàn): giao diện mà dùng hai hàm này để cảnh báo ô người dùng dán chữ rất dài sẽ thấy «có link/giá».
- Đuôi thương hiệu tự đặt dài (tối đa 25 ký tự) thì khoảng «dài vừa không gắn được đuôi» rộng hơn (ví dụ đuôi 23 ký tự: title 38–49 ký tự).
- Phần SEO hỏng trong file nháp bị bỏ **lặng lẽ** (không đếm như ảnh hỏng). Chỉ xảy ra khi file bị sửa tay hay hỏng.
- `[tasks.links]` dùng cùng hãng/mô hình với `[tasks.meta]`; chủ dự án đổi được trong `config/ai.toml` (không được thêm `web_search`).

## Đề xuất

- **Họa Sĩ (T-041):** nối theo mục «Hàm cho Họa Sĩ»; giữ `SiteIndexStore`, `ContentWriter` qua các lần chạy như `draft_store()`; hiện mọi chữ từ site/AI bằng chữ thuần (U1).
- **Ngòi Bút (phiếu sau, tùy chọn):** dặn AI viết mục Hỏi đáp theo một dạng cố định (`### Câu hỏi?` rồi đoạn trả lời) để `find_faq` luôn nhận ra.
- **Soi Lỗi:** dọn các docstring cũ ở mục «Test cũ đã đổi»; SL-T036-11, LC-T036-2, lỗi 4 của LC-T038 (`_host` bỏ mọi dấu chấm cuối) vẫn để ngỏ (không bắt buộc).

## Câu hỏi cho chủ dự án

Không có.

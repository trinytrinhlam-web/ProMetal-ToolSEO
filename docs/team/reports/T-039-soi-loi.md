# Báo cáo T-039 · Soi Lỗi · Liên kết nội bộ (chọn bài đích, AI gợi ý anchor, chèn link, kiểm link)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-039](../tickets/T-039-lien-ket-noi-bo.md) · báo cáo Thợ Máy: [T-039-tho-may](T-039-tho-may.md) · thiết kế: [T-033](T-033-tho-may.md) mục 4.2 → 4.5 |
| Ngày nộp | 2026-10-21 (giờ máy, +07) |
| Nhánh kiểm | `team/T-039`, đầu nhánh lúc nhận `bf1f889`, gốc `main` `d9e279f` |
| Mức kiểm | Đầy đủ |
| Kết quả | Hoàn thành |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T039-6), **5 Thấp** (SL-T039-1 → 5). Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t039.py` |

## Tóm tắt (cho chủ dự án)

- **Phần quan trọng nhất làm đúng.** Tôi thử mọi cách để AI chèn được link ra trang ngoài (địa chỉ web trong cụm từ, link kiểu Markdown, thẻ HTML, ký tự vô hình, chữ toàn khổ, chữ Nga giả chữ Latinh…): không cách nào lọt. Địa chỉ của link luôn do phần mềm lấy từ danh sách bài **đã đăng** trên website; bài nháp, hẹn giờ, riêng tư, chờ duyệt, đã xóa không bao giờ thành đích. Link không bao giờ bị chèn vào tiêu đề, vào link có sẵn hay vào đoạn mã.
- **Tìm được 1 lỗi mức Trung bình (SL-T039-6):** với một số bài có dòng chữ thừa ở cuối (không nằm trong đoạn văn nào), phần chèn link **bị lỗi dừng hẳn** thay vì chèn. Nguyên nhân là phần mềm đặt một biến trùng tên với biến mà Python vừa thêm vào bản vá mới nhất. Lỗi chỉ xảy ra trên máy có Python mới (máy Windows hiện tại), nên hai máy có thể chạy khác nhau. Sửa rất nhanh (đổi tên một biến). Phần chèn link chưa được nối vào app nên hiện chưa ảnh hưởng gì tới anh.
- **5 lỗi Thấp**, đều theo hướng "an toàn mà thiếu", không có lỗi nào làm link sai địa chỉ: chữ tiếng Việt dạng "tổ hợp" (hay gặp khi dán từ máy Mac) làm gợi ý bị bỏ oan; link có thể nằm trong chỗ "[cần bổ sung: …]" khi trong đó có chữ in đậm; vài kiểu link bài nháp gõ tay rất lạ chưa bị chặn; AI trả `true` thay cho số thì phần mềm tự hiểu thành số 1.
- **Đề xuất:** sửa SL-T039-6 trước khi gộp (một lượt ngắn của Thợ Máy); 5 lỗi Thấp để Thợ Máy dọn cùng T-041 hoặc trước Giai đoạn 5.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t039.py` | **Mới.** 44 hàm test, 198 trường hợp (kể cả tham số hóa), không gọi mạng; 29 trường hợp `xfail(strict=True)` cho 6 lỗi SL-T039-1 → 6 |
| `docs/team/reports/T-039-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của Thợ Máy.

## Kiểm từng yêu cầu của phiếu

| # | Yêu cầu | Kết quả | Test của Soi Lỗi (`tests/test_soi_loi_t039.py`) |
|---|---|---|---|
| 1 | Chọn ứng viên chỉ từ bài **đã đăng**; link bắt buộc luôn có; bài nháp/hẹn giờ/riêng tư không thành đích | **Đạt** | `test_only_published_items_ever_become_targets` (tải qua `WordPressClient` thật + `FakeWordPress`, 8 mục chưa đăng: `draft`, `future`, `private`, `pending`, `trash`, `"Publish"` viết hoa, thiếu `status`, trang nháp; ghi bắt buộc bằng ID, đường dẫn, địa chỉ đầy đủ, slug, `?p=`; cả 3 loại bài) · `test_unpublished_targets_never_linked_or_accepted` · `test_required_link_always_first_even_with_many_related` · `test_required_link_resolution_variants` · `test_draft_required_link_blocks_even_when_list_truncated` · `test_related_uses_accentless_words_and_ignores_case_and_nfd` |
| 2 | AI chỉ nhận ID + tiêu đề trong khung dữ liệu, không URL | **Đạt** | `test_prompt_never_contains_any_address` (không link, không slug, không `href`; bài là khối cuối) · `test_site_title_cannot_break_any_frame` (6 dạng thẻ giả, cả `</bai_viet>`) |
| 3 | Gợi ý sai thì bỏ, không sửa giùm | **Đạt**, trừ SL-T039-5 (Thấp) | `test_each_bad_suggestion_dropped_not_fixed` (14 kiểu: ID lạ, ID có trên site mà không được chọn, không có trong bài, đổi hoa thường, bỏ dấu, thêm dấu câu, sai phần, 1 từ, 9 từ, chỉ có ở tiêu đề phần / tiêu đề con, vắt qua 2 đoạn; câu báo không chép chữ AI) · `test_duplicates_limits_and_same_paragraph` (trùng đích, trùng cụm từ, cùng đoạn, quá 5) · `test_required_target_processed_first_even_if_listed_last` · `test_heading_text_also_in_body_is_accepted_and_placed_in_body` · `test_raw_dicts_with_wrong_types_dropped` · `test_good_json_suggestions_kept_verbatim` (đi đường `model_validate_json` như app thật) |
| 4 | Link lưu riêng `InternalLink(section, anchor, post_id)` | **Đạt** | Đọc code: `links.py:88-107` không có trường địa chỉ, tự kiểm kiểu; `place_links` kiểm lại từ đầu (`links.py:775-806`) |
| 5 | `apply_links`: chỉ nút chữ; không chèn trong `<a>`, `<h2>`, `<h3>`, `<code>`, thẻ bộ lọc bỏ cả nội dung; `href` từ danh sách, escape đúng; ký tự đặc biệt, NFC/NFD, thực thể HTML, chữ bị thẻ cắt ngang; `sanitize_html(apply_links(...))` giữ link và vẫn vô hiệu `[` `]` | **Đạt**, trừ SL-T039-6 (Trung bình), SL-T039-1, SL-T039-2 (Thấp) | `test_never_inserts_inside_tags_the_filter_drops` (22 thẻ của `DANGEROUS_TAGS` × 3 cách lồng) · `test_never_inserts_inside_link_heading_or_code` (15 dạng, cả `<a>`/`<code>` bị đóng ngầm, chữ hoa, thẻ lồng, × 2 phần) · `test_special_characters_and_entities` (7: `"` `'` `&` `( ) + ? $ % ^ { }`, `m²`, thực thể số, `&nbsp;`, xuống dòng) · `test_anchor_split_by_inline_tag_not_wrapped_partially` (`<b>`, `<em>`, `<br>`, chú thích, `<wbr>`) · `test_nfd_html_with_nfd_anchor_works_and_never_wraps_wrong_text` · `test_placeholder_in_single_text_node_never_linked` · `test_href_only_from_index_and_escaped` · `test_sanitize_after_apply_keeps_links_and_neutralizes_brackets` (shortcode `[gallery]`, `[[caption]]`, chạy `sanitize_html` lần 2 không đổi) · `test_random_html_only_index_hrefs_added_and_text_unchanged` (1.000 mẫu HTML ngẫu nhiên) |
| 6 | Kiểm link nháp/hỏng: cùng tên miền mà chưa đăng → Chặn; `?p=`, `?page_id=`, `preview=true` → Chặn; `truncated` không kết luận hỏng; link ngoài chỉ liệt kê, không gọi mạng | **Đạt**, trừ SL-T039-3, SL-T039-4 (Thấp) | `test_same_site_unpublished_blocks` (13 biến thể: hoa thường, `%`, `www.`, `http`/`https`, `/` cuối, `//`, `..`, dấu chấm cuối tên máy) · `test_draft_query_forms_block` (21 biến thể `?p=`, `?P=`, `?%70=`, `?page%5Fid=`, `preview` không giá trị, `/index.php?p=`…) · `test_draft_query_forms_block_even_when_truncated` · `test_truncated_list_never_concludes_broken` · `test_published_variants_ok` · `test_external_links_listed_never_fetched` (khóa `requests`, `urlopen`, `getaddrinfo`, `create_connection`: 0 lần gọi) · `test_required_link_must_survive_in_final_html` |
| 7 | Test bắt buộc + AI không chèn được link ngoài + tốc độ tuyến tính | **Đạt** | `test_ai_cannot_smuggle_link_through_anchor` (24 dạng: URL, toàn khổ, chữ Kirin, `javascript:`, `mailto:`, email, Markdown, HTML, `` ` ``, 11 loại ký tự vô hình/điều khiển) · `test_end_to_end_ai_never_adds_foreign_href` (JSON AI có trường `href`/`url`/`link` lạ → HTML cuối đã lọc chỉ có link trong danh sách, `check_links` không thấy link ngoài) · 13 test tốc độ mới (mục Bằng chứng 3) |

Điều kiện Lá Chắn T-037 (phiếu, mục Ghi chú): (1) `href` qua `html.escape(quote=True)` và qua `sanitize_html`: có (`links.py:820`, test `test_href_only_from_index_and_escaped`); (2) tiêu đề từ site vào lời dặn nằm trong khung: có; (3) `truncated` không kết luận "link hỏng": có, ở cả chọn bài lẫn kiểm link; (4) chuẩn hóa link trước khi so: có (`path_key`), trừ các dạng tên máy ở SL-T039-4; (5) SL-T037-5: không áp dụng (`grep` không thấy `apply_links`, `check_links`, `select_candidates`… trong `app/` hay module nào khác).

## Lỗi tìm thấy

| Mã | Mức | Tóm tắt | Test |
|---|---|---|---|
| SL-T039-6 | **Trung bình** | `place_links`/`apply_links` ném `IndexError` hoặc bỏ oan đoạn chữ cuối bài: biến `_TextRuns._pending` trùng tên bộ đệm mới của `HTMLParser` (Python 3.12.15) | `test_sl6_*` (8 trường hợp) |
| SL-T039-1 | Thấp | Thân bài dạng NFD (dán từ máy Mac): mọi gợi ý AI bị bỏ oan, link bắt buộc thành "thiếu" | `test_sl1_*` (2) |
| SL-T039-2 | Thấp | Link lọt vào chỗ `[cần bổ sung: …]` khi trong ngoặc có thẻ (`<strong>`, `<em>`) | `test_sl2_*` (2) |
| SL-T039-3 | Thấp | `check_links` coi là "trang chủ" (Nên) các link nháp dạng tham số PHP tự đổi tên (`?%20p=`, `?page.id=`…) và `?name=`, `?pagename=` | `test_sl3_*` (8) |
| SL-T039-4 | Thấp | Tên máy của chính site viết dạng trình duyệt tự đổi (`%2E`, toàn khổ, `。`) bị xếp "ra ngoài" (Cảnh báo) thay vì Chặn; `https://…:80` được Nên | `test_sl4_*` (4) |
| SL-T039-5 | Thấp | Khuôn `LinkSuggestion` tự đổi kiểu: `"post_id": true` thành 1, `"1"` thành 1, `"section": false` thành 0 (sửa giùm) | `test_sl5_*` (5) |

### SL-T039-6 (Trung bình) · `apply_links` ném lỗi hoặc bỏ oan đoạn cuối bài

- **Nguyên nhân** (đã chứng minh): `_TextRuns.__init__` đặt `self._pending: list[str] = []` (`links.py:674`) và `handle_data` nối chữ đã giải mã vào đó (`links.py:734-737`). Python 3.12.15 (bản đang chạy trên máy Windows, `uv run python -c "import sys; print(sys.version)"` → `3.12.15 (main, Oct 3 2026…)`) thêm bộ đệm riêng **cùng tên** `HTMLParser._pending` (`Lib/html/parser.py:141`, dùng trong `feed()` và `close()` dòng 176-182). Khi đọc xong mà `_pending` còn chữ, `close()` nối chữ **đã giải mã** vào cuối dữ liệu và đọc lại như HTML: `&lt;b&gt;` trong chữ thành thẻ `<b>` thật, số dòng vượt số dòng thật của bài nên `self._line_starts[line - 1]` (`links.py:678`) ném `IndexError`; hoặc nút chữ cuối bị coi là "không khớp" nên không chèn.
- **Cách tái hiện** (`uv run python`, `INDEX` như test):
  - `apply_links("<p>Gọi dịch vụ sửa cửa kéo tận nơi.</p>\n&lt;b&gt;\n", [InternalLink(section=0, anchor="dịch vụ sửa cửa kéo", post_id=10)], INDEX)` → `IndexError: list index out of range`, dù cụm từ nằm trong một `<p>` hợp lệ.
  - Chuỗi 5 ký tự `"\n>;<!"` cũng ném lỗi (tìm ra khi thử ngẫu nhiên: mẫu thứ 160 trên 400, hạt giống 39).
  - `"<p>Mở bài.</p>Gọi dịch vụ sửa cửa kéo &lt;b&gt; ngay"`, `"…\nngay <!"`, `"Gọi dịch vụ sửa cửa kéo\n<?"`: không lỗi nhưng **không chèn** (bỏ oan).
- **Mong đợi:** không bao giờ ném lỗi (báo cáo Thợ Máy mục Bằng chứng ghi 16.000 mẫu thử "không ném lỗi"); chèn được link vào đúng cụm từ.
- **Thực tế:** `IndexError` làm hỏng cả bước dựng HTML; hoặc link bị bỏ qua.
- **Chứng minh nguyên nhân:** một bản sao `links.py` (để ngoài repo) chỉ đổi `self._pending` thành `self._txt_parts`: cả 6 mẫu của `test_sl6_trailing_text_never_crashes_nor_dropped` chèn đúng, 3.000 mẫu ngẫu nhiên không lỗi, chữ người đọc thấy không đổi; mọi test `test_sl6_*` qua với bản sao đó.
- **Không phải lỗ bảo mật** (suy luận, có thử): chưa thấy trường hợp nào link bị chèn **sai chỗ**: phần đọc lại nằm ở vị trí sau cuối bài, và chốt chặn `html.unescape(source[start:end]) == text` (`links.py:693`) loại các nút chữ lệch. Hậu quả chỉ là dừng hẳn hoặc bỏ sót.
- **Phụ thuộc phiên bản Python:** `.python-version` ghi `3.12` nên mỗi máy dùng bản vá 3.12.x đang cài; máy có Python cũ hơn 3.12.15 không gặp lỗi. Hai máy của chủ dự án có thể cho kết quả khác nhau. Các test `test_sl6_*` vì vậy đánh `xfail` **có điều kiện** `"_pending" in vars(HTMLParser())`: trên Python cũ chúng chạy như test thường và qua.
- **Sửa gợi ý (Thợ Máy):** đổi tên `_pending`, `_pending_start` thành tên không trùng (ví dụ `_text_parts`, `_text_start`). Test `test_sl6_parsers_do_not_shadow_htmlparser_attributes` canh luôn về sau: không lớp đọc HTML nào của `links.py` được đặt biến trùng tên biến của `HTMLParser`. Ngoài phạm vi phiếu: `_Sanitizer` (`sanitize.py`) và `_Anchors` không trùng tên (đã kiểm `vars`).
- **Mức Trung bình** vì: lỗi dừng hẳn trong hàm hứa "không bao giờ ném lỗi", phụ thuộc bản Python, và bộ thử ngẫu nhiên của Thợ Máy (`T-039-tho-may-scripts/fuzz_links*.py` trong thư mục ghi chú chung) chưa gặp tổ hợp gây lỗi: cần chữ trần ở **cuối** bài (không có thẻ nào sau nó) mà khi đọc lại sinh ra một thẻ hoàn chỉnh hoặc một chú thích, cộng một dấu xuống dòng. Chưa ảnh hưởng người dùng vì `apply_links` chưa được nối vào app.

### SL-T039-1 (Thấp) · Chữ tổ hợp NFD bị bỏ oan

- **Tái hiện:** thân phần là `unicodedata.normalize("NFD", "Nếu không tự làm được, hãy gọi dịch vụ sửa cửa kéo tận nơi.")`. Lời dặn gửi AI chạy qua `_neutralize` (NFKC) nên AI thấy chữ NFC (test có kiểm) và chép cụm từ NFC `"dịch vụ sửa cửa kéo"`. `check_suggestions` bỏ: "cụm từ không có nguyên văn trong thân phần đó"; `place_links` trên HTML NFD với cụm từ NFC: bỏ qua.
- **Mong đợi:** hai chuỗi tương đương chuẩn Unicode (nhìn giống hệt) được coi là nguyên văn; link bao đúng chữ trong bài.
- **Thực tế:** bị bỏ; nếu là trang dịch vụ bắt buộc thì `missing_required`, rồi `check_links` Chặn "Thiếu link bắt buộc".
- Hướng an toàn (không chèn sai chỗ: `test_nfd_html_with_nfd_anchor_works_and_never_wraps_wrong_text`). Dự án đã ghi nhận chữ NFD dán từ Mac (`seo_app/content/rules.py:521`).

### SL-T039-2 (Thấp) · Link lọt vào chỗ `[cần bổ sung: …]`

- **Tái hiện:** `apply_links("<p>Giá [cần bổ sung: <strong>giá</strong> thay ray mới] tùy.</p><p>Thợ thay ray mới rất nhanh.</p>", [InternalLink(section=0, anchor="thay ray mới", post_id=11)], INDEX)` → `<a>` nằm **trong** ngoặc ở đoạn đầu. Tương tự `"<p>[xem <em>thêm</em> dịch vụ thay ray mới]</p>…"`.
- **Nguyên nhân:** `_mask_brackets` chạy trên từng nút chữ (`links.py:795`); nút chữ sau `</strong>` không còn thấy dấu `[`. `check_suggestions` che ngoặc trên cả khối Markdown nên vẫn cho qua khi cụm từ còn có ở đoạn khác cùng phần; `apply_links` lại chọn lần xuất hiện đầu tiên, tức chỗ trong ngoặc.
- **Mong đợi:** không chèn trong ngoặc (docstring `apply_links` hứa "không chèn vào chỗ […]"); chèn ở đoạn sau.
- Hậu quả: chữ chờ bổ sung thành link. Sau `sanitize_html` dấu ngoặc thành `&#91;` nên không chạy shortcode (không phải lỗ bảo mật).

### SL-T039-3 (Thấp) · Kiểm link nháp bỏ sót dạng tham số lạ

- **Tái hiện:** `check_links('<p><a href="https://suachuacuasat.com/?%20p=12">x</a></p>', INDEX)` → `Level.GOOD`, "Link về trang chủ." Tương tự `?+p=12`, `?page.id=10`, `?page%20id=10`, `?page+id=10`, `/sua-cua-keo-tphcm/?preview.id=12`, `?name=bai-nhap`, `?pagename=trang-nhap`.
- **Vì sao là link nháp:** PHP bỏ dấu cách ở đầu tên tham số và đổi `.`, dấu cách trong tên thành `_`, nên WordPress nhận đúng `p=12`, `page_id=10`, `preview_id=12`. `?name=`, `?pagename=` là cách WordPress mở bài/trang theo slug (bài nháp thì người đọc gặp trang 404). `parse_qsl` của Python không đổi tên như PHP nên `_is_draft_query` (`links.py:179-180`) không nhận ra.
- **Mong đợi:** Chặn (phiếu yêu cầu 6: link cùng tên miền không có trong danh sách đã đăng → Chặn).
- **Thực tế:** Nên. Các dạng này chỉ có khi người dùng tự gõ (AI không viết được link). Cùng họ, chưa đưa vào test: `?attachment_id=5`, `?cat=3` cũng thành "trang chủ" (trong khi `/category/…` bị Chặn).

### SL-T039-4 (Thấp) · Tên máy, cổng dạng lạ của chính site

- **Tái hiện:** `https://suachuacuasat%2Ecom/bai-nhap/`, `https://ｓｕａｃｈｕａｃｕａｓａｔ.com/bai-nhap/` (toàn khổ), `https://suachuacuasat。com/bai-nhap/` (dấu chấm kiểu chữ Hán) → `LinkKind.EXTERNAL`, `Level.WARN`. Trình duyệt giải mã `%2E` và chuẩn hóa tên miền quốc tế nên cả ba đều là **chính site**, tới một bài chưa đăng. `https://suachuacuasat.com:80/sua-cua-keo-tphcm/` → `Level.GOOD` dù https qua cổng 80 không mở được (`links.py:951` cho qua cổng 80 với cả `https`).
- **Mong đợi:** Chặn (như dạng dấu cách không ngắt mà Thợ Máy đã Chặn: "trình duyệt hiểu khác điều ta thấy").
- **Thực tế:** Cảnh báo "ra ngoài" / Nên. Chỉ có khi người dùng tự gõ.

### SL-T039-5 (Thấp) · Khuôn AI tự đổi kiểu dữ liệu

- **Tái hiện:** `LinkSuggestions.model_validate_json('{"links": [{"post_id": true, "section": 0, "anchor": "dịch vụ sửa cửa kéo"}]}')` → `post_id=1`; nếu bài ID 1 là ứng viên thì `check_suggestions` nhận gợi ý. Tương tự `"1"`→1, `1.0`→1, `"section": false`→0, `"0"`→0.
- **Nguyên nhân:** `LinkSuggestion` (`links.py:110-113`) dùng `int` thường nên pydantic tự đổi kiểu **trước** khi tới `check_suggestions`. Kiểm `type(...) is int` (`links.py:571, 577`) chỉ có tác dụng với dữ liệu thô. Báo cáo Thợ Máy mục 3 ghi "không nhận `True`, `"10"`, `10.0`": đúng với `dict` thô (test `test_bad_post_id_type_rejected` truyền `dict`), không đúng với đường thật (`gemini_provider.py:341`, `openai_provider.py:236` gọi `model_validate_json`).
- **Mong đợi:** bỏ, đúng quy tắc "sai thì bỏ, không sửa giùm" (ví dụ `Field(strict=True)` cho `post_id`, `section`).
- Hậu quả nhỏ: `post_id` vẫn phải nằm trong ứng viên và cụm từ vẫn phải có nguyên văn.

## Bằng chứng

Chạy trên Windows 11 (máy chủ dự án), worktree `wt-T-039`, Python 3.12.15, trong lúc 2 agent khác và một lượt pytest toàn bộ chạy song song.

### 1. Test của Soi Lỗi và test của phiếu

```
$ uv run pytest tests/test_soi_loi_t039.py tests/test_onpage_links.py
361 passed, 29 xfailed in 28.64s
```

192 ca của Thợ Máy (`test_onpage_links.py`) qua hết; 169 ca của Soi Lỗi qua, 29 ca `xfail` đúng 6 lỗi ở trên.

### 2. Test liên quan (phiếu, `sanitize`, `site_index`, `app_pages`, mọi file test có `prompts`/`onpage`)

```
$ uv run pytest tests/test_ai_images.py tests/test_app_pages.py tests/test_blind_test.py \
    tests/test_business_profile.py tests/test_config_tolerance.py tests/test_content_edge_cases.py \
    tests/test_content_workflow.py tests/test_link_escape.py tests/test_onpage_links.py \
    tests/test_onpage_meta.py tests/test_onpage_schema.py tests/test_prompt_data_frames.py \
    tests/test_safety.py tests/test_sanitize.py tests/test_sanitize_autolink.py \
    tests/test_sanitize_bypass.py tests/test_sanitize_hardening.py tests/test_site_index.py \
    tests/test_site_index_t042.py tests/test_soi_loi_round3.py tests/test_soi_loi_t003_t009.py \
    tests/test_soi_loi_t026.py tests/test_soi_loi_t036.py tests/test_soi_loi_t038.py \
    tests/test_soi_loi_t039.py
2489 passed, 1 skipped, 47 xfailed in 557.80s (0:09:17)

$ uv run ruff check .
All checks passed!
```

25 file = danh sách của phiếu + mọi file có chữ `prompts` hoặc `onpage` (`grep -l`), như Thợ Máy đã chạy, thêm file mới của Soi Lỗi. 1 bỏ qua và 18 trong 47 `xfail` là của các file có sẵn (Thợ Máy cũng ghi 1 bỏ qua, 18 `xfail`); 29 `xfail` còn lại là của `test_soi_loi_t039.py`. Lượt chạy lâu (9 phút) vì máy đang chạy song song 2 agent khác và một lượt pytest toàn bộ.

### 3. Test tốc độ không chập chờn

```
$ for i in 1..5;  uv run pytest tests/test_onpage_links.py -k linear      → 13 passed (5/5 lượt)
$ for i in 1..11; uv run pytest <2 file> -k linear (cỡ ban đầu)           → 26 passed ở 9/11 lượt; 2 lượt đỏ 1 test
$ for i in 1..15; uv run pytest <2 file> -k linear (sau khi tăng cỡ)      → 26 passed (15/15 lượt)
```

- **13 test tốc độ của Thợ Máy:** không đỏ lượt nào trong mọi lượt có ghi tên test đỏ (5 lượt riêng, 6 + 15 lượt chung). Lượt đỏ đầu tiên của nhóm 11 lượt không ghi lại tên test; lượt đỏ thứ hai là test **của Soi Lỗi** `test_place_and_check_links_linear_on_more_hostile_html[unclosed-tags]` (tỉ lệ 9,3, ngưỡng 9), nên lượt đầu nhiều khả năng cũng vậy (suy luận).
- **Nguyên nhân và cách sửa (test của Soi Lỗi, không phải code ứng dụng):** đo riêng 8 lần mỗi cỡ: chuỗi `"<a b"` lặp 2.000 → 8.000 lần cho tỉ lệ dao động 4,9–13,9; lặp 8.000 → 32.000 lần cho 3,4–5,1. Thẻ mở rất dài làm biểu thức của `html.parser` giữ trạng thái theo độ dài thẻ, nên ở cỡ nhỏ bộ nhớ đệm CPU làm tỉ lệ nhảy; ở cỡ lớn tỉ lệ ổn định quanh 4 (tuyến tính). Đã tăng cỡ của 2 dạng nhạy (`unclosed-tags`, `long-attr`) lên 8.000 (ghi chú ngay trên test); sau đó 15/15 lượt qua.
- **13 test tốc độ mới của Soi Lỗi:** HTML thù địch cho cả `place_links` lẫn `check_links` (thẻ không đóng, thuộc tính dài, `<p>` lồng, `<li>` không đóng, nhiều link, `&amp` liên tục, dấu cách không ngắt), thân bài thù địch cho `check_suggestions` (dãy dấu cách dài giữa các từ để ép biểu thức quay lui, cụm gần khớp, `[` không đóng, dấu `` ` ``, `>` liên tục; 30 bài đích khác nhau để gợi ý nào cũng phải tìm hết cả phần), và `select_candidates` theo cỡ site (150 → 600 bài, 30 link bắt buộc). Đo trước khi chốt cỡ (đúng cỡ trong test hoặc cỡ sát đó, 5–8 lần mỗi dạng): tỉ lệ lớn nhất từ 1,1 tới 6,4, dưới ngưỡng 9.

### 4. Thử ngẫu nhiên

- `test_random_html_only_index_hrefs_added_and_text_unchanged`: 1.000 mẫu HTML ghép từ thẻ đúng, thẻ hỏng, `<script>`, chú thích, `[`, `]`, `<` trần, `&amp;`, `&#91;`, dấu cách không ngắt, ký tự rộng 0, link ngoài có sẵn: link **mới** chỉ là link trong danh sách bài, số link mới bằng số báo đã chèn (≤ 5), chữ người đọc thấy không đổi, link mới còn sau `sanitize_html`. Mỗi mẫu được thêm `-->`, `</script>`, `</p>` ở cuối để không vấp SL-T039-6.
- Cùng bộ mẫu **không** thêm phần cuối: mẫu thứ 160 ném `IndexError` (SL-T039-6, `test_sl6_random_html_never_raises`).

## Rủi ro và điểm cần chú ý (quan sát, không tính là lỗi)

- **`check_links` phải chạy trên HTML đã lọc.** Đọc HTML trước `sanitize_html` thì link nằm trong `<noscript>` hoặc `<template>` vẫn được tính là "đã có link bắt buộc", dù bộ lọc bỏ hẳn hai thẻ này (đã thử). Thiết kế ghi "HTML cuối" nhưng docstring chưa nói rõ thứ tự. Giai đoạn 5 nên gọi `check_links(sanitize_html(...))`.
- **Link bắt buộc trong phiếu giao bài** dạng `#gia`, `?utm=1`, `/` hay chỉ tên miền được hiểu là trang chủ (nếu trang chủ là trang đã đăng), không báo gì. Cổng (`:8443`) và tên đăng nhập (`u:p@`) trong link bắt buộc bị bỏ qua, trong khi `check_links` coi `:8443` là ra ngoài và `@` là Chặn. Không nguy hiểm vì `href` luôn lấy từ danh sách bài.
- **Site dùng đường dẫn dạng `?p=`** (không phải site hiện tại): `apply_links` vẫn chèn link `https://…/?p=50` của bài đã đăng nhưng `check_links` Chặn chính link đó (đã thử).
- **"Mỗi đích 1 link, tổng 5"** chỉ đếm link do phần này chèn; link có sẵn trong HTML (nếu Giai đoạn 5 cho người dùng tự gõ link) không được tính.
- **Chọn đoạn theo kiểu "ai trước được trước":** gợi ý không bắt buộc chiếm đoạn đầu có thể làm gợi ý sau bị bỏ dù đổi sang đoạn khác được. Đúng quy tắc "lần xuất hiện đầu tiên" của thiết kế; chỉ là bỏ oan.
- Test tốc độ dùng thời gian CPU (`tests/timing.py`), nên máy bận ít ảnh hưởng; vẫn có thể đỏ oan nếu máy cực bận, khi đó chạy riêng lại.

## Đề xuất

- **Thợ Máy, lượt 2 ngắn của T-039 (nên làm trước khi gộp):** sửa SL-T039-6 (đổi tên `_pending`, `_pending_start` trong `_TextRuns`), bỏ dấu `xfail` của `test_sl6_*`. Có thể gộp luôn SL-T039-5 (`Field(strict=True)`) và SL-T039-2 (che ngoặc theo đoạn văn thay vì theo nút chữ) vì cùng file, sửa nhỏ.
- **SL-T039-1, -3, -4:** làm cùng T-041 hoặc trước Giai đoạn 5 (khi người dùng bắt đầu tự gõ link và nối `check_links` vào màn hình xác nhận).
- **Giai đoạn 5:** gọi `check_links` trên `sanitize_html(apply_links(...))`; ghi rõ thứ tự này trong docstring.
- **Chỉ Huy:** cân nhắc ghim bản vá Python trong `.python-version` (ví dụ `3.12.15`) để hai máy chạy cùng một thư viện chuẩn; SL-T039-6 cho thấy bản vá nhỏ của Python cũng có thể đổi hành vi.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-22) · kiểm lại sau khi Thợ Máy sửa SL-T039-1 → 6

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Nhánh kiểm | `team/T-039`, đầu nhánh lúc nhận `c0e5806` (Thợ Máy lượt 2: `706fc0a` SL-T039-6, `61c98ce` SL-T039-1 → 5, `c0e5806` báo cáo) |
| Mức kiểm | Đầy đủ: kiểm lại 6 lỗi cũ, soát test đã đổi, tìm lỗi mới do lượt 2 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn được. **6/6 lỗi cũ đã sửa thật.** Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T039-7 → 9), mỗi lỗi có test `xfail(strict=True)`. Điều kiện: nên sửa SL-T039-7 trước khi gộp (lỗi do lượt 2 gây ra, trái yêu cầu "chạy tuyến tính" của phiếu; việc nhỏ) |

### Tóm tắt (cho chủ dự án)

- **Cả 6 lỗi lần trước đã được sửa thật.** Phần chèn link không còn dừng hẳn trên máy có Python mới. Chữ tiếng Việt dán từ máy Mac được nhận đúng. Không còn chèn link vào chỗ "[cần bổ sung: …]" có chữ in đậm. Phần mềm chặn thêm các kiểu link bài nháp gõ lạ và tên website viết lạ. AI trả sai kiểu số thì bị coi là trả sai, không tự đoán.
- **Chữ dán từ máy Mac được thử rất kỹ:** 15.000 bài thử ngẫu nhiên, có cả thẻ chen vào giữa chữ cái và dấu. Link luôn bao đúng cụm từ, chưa lần nào cắt đôi một chữ có dấu, chữ người đọc thấy không đổi.
- **Tìm thêm 3 lỗi nhỏ (Thấp).** Không lỗi nào làm link trỏ sai địa chỉ hay lộ thông tin:
  1. Phần kiểm tên website mới thêm có thể **chạy rất chậm** (link dài 8.000 ký tự mất 50 giây) nếu bài có một link gõ cố ý với tên website cực dài bằng chữ lạ (ví dụ chữ Hán). Link thật không bao giờ như vậy, nhưng phiếu yêu cầu mọi phần chạy nhanh đều theo độ dài bài. Sửa nhỏ.
  2. Bài có đoạn "mã" (chữ trong dấu `) chứa dấu ngoặc vuông: phần chèn link có thể bỏ oan link bắt buộc, hoặc đặt link vào chỗ "[cần bổ sung: …]". Bài sửa cửa hầu như không có đoạn mã.
  3. Vài kiểu link bài nháp gõ tay rất hiếm (`?p[]=12`) vẫn bị coi là "link về trang chủ".
- **Đề xuất:** Thợ Máy sửa lỗi 1 trước khi gộp (một lượt ngắn); lỗi 2 và 3 làm cùng lượt đó hoặc cùng T-041, trước Giai đoạn 5. Phiếu chuyển sang Lá Chắn được.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t039.py` | Thêm 4 hàm test, 12 trường hợp: 10 ca `xfail(strict=True)` cho SL-T039-7 (1), SL-T039-8 (2), SL-T039-9 (7); 2 ca thường (đang qua) canh hướng sửa SL-T039-7. Không sửa test có sẵn |
| `docs/team/reports/T-039-soi-loi.md` | Mục này |

Không sửa code ứng dụng, không sửa test của Thợ Máy.

### Kiểm từng lỗi cũ

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| SL-T039-6 (Trung bình) | **Đã sửa** | Đọc code: mọi biến, hàm riêng của `_TextRuns` (`links.py:667-777`) đặt dạng `__x`, Python đổi thành `_TextRuns__x` nên không thể trùng tên của `HTMLParser`. Soát tên: so `vars(HTMLParser())`, `dir(HTMLParser)` với mọi tên của `_TextRuns` (sau khi đọc một bài) và `_Anchors`. **3.12.15**: `vars` có 13 tên, gồm `_pending`, `_pending_len`, `_parse_threshold`, `_escapable`, `_support_cdata`, `scripting`. **3.14.6**: 10 tên, không có `_pending`. Cả hai bản: giao nhau rỗng; tên công khai `runs`, `linked`, `read`, `hrefs`, `ids` không có trong `HTMLParser`. **3.12.3: máy không có** (chỉ 3.12.15 và 3.14.6; tôi không tải thêm). Suy luận cho 3.12.3: tên dạng `_TextRuns__x` không thể trùng ở bản nào; 3.12.3 chỉ có ít tên hơn 3.12.15 (theo mã nguồn CPython, chưa chạy). Test `test_html_readers_never_shadow_htmlparser_names` của Thợ Máy so cả các tên mới của 3.12.15 nên đúng ý trên 3.12.3. 8 ca `test_sl6_*` nay là test thường và qua; mẫu tái hiện gốc chèn đúng |
| SL-T039-1 (Thấp) | **Đã sửa** | `check_suggestions` so ở dạng NFC. `place_links` tìm trên chữ NFC kèm bảng vị trí (`_nfc_offsets`, `links.py:800`), bọc **chữ gốc**, rồi kiểm lại chữ gốc ra đúng các từ (`_find_in_run`, `links.py:819`). Bảng vị trí chỉ có ở đầu mỗi cụm "chữ cái + dấu", nên không thể bọc nửa chữ. Thử ngẫu nhiên riêng (mục Bằng chứng 4): 15.000 bài, chữ NFD/NFC lẫn lộn; thẻ, chú thích, `<wbr>`, `<br>` và thực thể (`&#769;`) chen vào **mọi chỗ, kể cả giữa chữ cái và dấu**; chạy trên HTML gốc lẫn HTML đã qua `sanitize_html`. Kết quả: không ném lỗi, chữ người đọc thấy không đổi, chữ trong link (NFC) đúng cụm từ, **0 lần** ký tự đầu link hoặc ký tự ngay sau link là dấu tổ hợp. Một trường hợp biên có từ lượt 1: mục Quan sát |
| SL-T039-2 (Thấp) | **Đã sửa** | `_masked_runs` (`links.py:780`) che "[…]" theo đoạn văn. 2 ca `test_sl2_*` qua. Còn một biến thể qua đoạn `mã`: SL-T039-8 |
| SL-T039-3 (Thấp) | **Đã sửa** cả 8 dạng đã báo | `_php_name` (`links.py:187`); thêm `?name=`, `?pagename=` vào nhóm Chặn. Link thật của site không bị chặn oan: 15 dạng (`www.`, chữ hoa, `:443`, dấu chấm cuối, `?utm_source=`, `#gia`, `?s=`, `?names=`, `?pname=`, `?page=2`, `?a[name]=1`…) vẫn cho kết quả như lượt 1. Còn dạng tên mảng của PHP: SL-T039-9 |
| SL-T039-4 (Thấp) | **Đã sửa** | `_browser_host` (`links.py:1009`), `_WRONG_PORT`. Link ngoài viết lạ vẫn "ra ngoài" (10 dạng: `例え.jp`, `xn--…`, `ｅｘａｍｐｌｅ.com`, `suachuacuasat.com.evil.com`, `suachuacuasat%2Ecom.evil.com`, `suachuacuasat.com%2F.evil.com`…). Nhưng cách đổi tên máy mới gây SL-T039-7 (tốc độ) |
| SL-T039-5 (Thấp) | **Đã sửa** | `Field(strict=True)` (`links.py:114-115`). Không bỏ oan gợi ý đúng: khuôn JSON gửi AI vẫn là `integer` ở đường OpenAI (`openai.pydantic_function_tool`) lẫn Anthropic (`transform_schema`), tôi đã in ra kiểm. Cả 3 hãng đọc câu trả lời từ chữ JSON: `gemini_provider.py:341` và `openai_provider.py:236` dùng `model_validate_json`; với Anthropic, `parsed_output` của thư viện gọi `validate_json` (`anthropic/lib/_parse/_response.py:19`). Số nguyên thật vì vậy luôn qua |

### Soát test lượt 2 (`git diff 5b4ec03..c0e5806 -- tests/`)

- `tests/test_soi_loi_t039.py`: chỉ gỡ đúng 29 dấu `xfail` (SL-1: 2, SL-2: 2, SL-6: 8, SL-3: 8, SL-4: 4, SL-5: 5 ca), bỏ 2 hằng không còn dùng (`_STDLIB_PENDING`, `_SL6`) và sửa lời chú thích. **Không thân test nào đổi**, không điều kiện kiểm nào bị nới.
- `tests/test_onpage_links.py`: thêm 17 hàm, 69 ca. Đọc từng test: kiểm đúng ý (tên riêng của lớp đọc HTML, giả lập bộ đệm `_pending` trên mọi bản Python, NFD hai chiều, che "[…]" qua thẻ, thẻ đóng lạc, gọi trên HTML đã lọc, tham số PHP, tên máy lạ, khuôn chặt, tốc độ). Thiếu một ca: test tốc độ tên máy dài (`long-fullwidth-host`) dùng chữ toàn khổ. Nameprep đổi chữ toàn khổ về ASCII nên ca này không đi qua bước punycode, vì vậy không bắt được SL-T039-7.

### Lỗi mới

| Mã | Mức | Tóm tắt | Test (`tests/test_soi_loi_t039.py`) |
|---|---|---|---|
| SL-T039-7 | Thấp | `check_links` chạy **bậc hai** với tên máy dài không phải ASCII (do `_browser_host` của lượt 2) | `test_sl7_check_links_linear_on_long_non_ascii_host` (xfail) · canh hướng sửa: `test_own_site_with_ignored_marks_in_host_still_blocks` (2 ca, đang qua) |
| SL-T039-8 | Thấp | Dấu ngoặc trong đoạn `mã`: `check_suggestions` và `apply_links` thấy chỗ "[…]" khác nhau. Hậu quả: bỏ oan link bắt buộc (hồi quy từ bản sửa SL-T039-2) hoặc link lọt vào "[…]" | `test_sl8_code_brackets_seen_same_by_check_and_apply` (2 ca, xfail) |
| SL-T039-9 | Thấp | Tên tham số dạng mảng PHP (`?p[]=12`, `?page_id[]=10`, `?name[]=…`) vẫn là "Link về trang chủ" (bản sửa SL-T039-3 chưa hết) | `test_sl9_php_array_query_forms_block` (7 ca, xfail) |

#### SL-T039-7 (Thấp) · `check_links` chạy bậc hai với tên máy dài không phải ASCII

- **Tái hiện:** `check_links('<p><a href="https://' + "".join(chr(0x4E00 + i) for i in range(n)) + '.vn/">x</a></p>', INDEX)`. Đo trên máy Windows, Python 3.12.15 (đồng hồ thường): n = 2.000 mất 2,9 giây; n = 4.000 mất 12,6 giây; n = 8.000 mất **50 giây**. Code lượt 1 (`5b4ec03`, đo thời gian CPU, n = 500 → 2.000): dưới 0,02 giây. Test đo 3 lần: dài gấp 4 thì chậm gấp 14–21 lần (hàm tuyến tính chỉ khoảng 4 lần).
- **Nguyên nhân:** `_browser_host` (`links.py:1009-1017`) chạy `unquote(host).encode("idna")` cho mọi tên máy không phải ASCII (hoặc có `%`) mà không phải tên site (`links.py:1061`). Bộ mã IDNA của Python (`encodings/idna.py`, `ToASCII`) mã **punycode** nhãn không phải ASCII, rồi mới kiểm độ dài 63. Punycode của Python chạy bậc hai theo độ dài nhãn khi nhãn có nhiều chữ khác nhau.
- **Mong đợi:** tuyến tính (phiếu, Yêu cầu 7: "Có test tốc độ tuyến tính"; docstring `links.py:24-25`: "Mọi hàm chạy tuyến tính theo độ dài bài").
- **Hậu quả:** app treo khi kiểm link nếu HTML có một link như vậy. Hiện chưa có đường đi tới đây: `check_links` chưa nối vào app. AI cũng không đưa link vào bài được (`clean_ai_text` bỏ link Markdown, `apply_links` chỉ chèn link từ danh sách bài). Từ Giai đoạn 5, người dùng tự gõ hoặc dán link mới có thể gặp. Không lộ gì.
- **Sửa gợi ý (Thợ Máy):** bỏ hẳn bước mã punycode. Chạy `encodings.idna.nameprep` cho từng nhãn (tách ở `.`, `。`, `．`, `｡`); bước này tuyến tính. Nhãn nào vẫn còn chữ không phải ASCII thì không thể là tên site (tên site là ASCII): trả nguyên tên máy. **Không** chặn theo độ dài chữ gốc. Nhãn dài hơn 63 ký tự vẫn có thể ra đúng tên site sau khi nameprep bỏ ký tự vô nghĩa: `suachuacuasat` + 100 ký tự U+FE0F + `.com` hiện bị Chặn đúng, nhưng chặn độ dài thô sẽ xếp nó thành "ra ngoài". Test `test_own_site_with_ignored_marks_in_host_still_blocks` canh việc này (đã thử: đỏ với cách chặn độ dài thô). Bản sao `links.py` sửa theo cách nameprep (ngoài repo) qua cả 3 test này và toàn bộ 2 file test của phiếu.

#### SL-T039-8 (Thấp) · Dấu ngoặc trong đoạn `mã`: hai hàm thấy chỗ "[…]" khác nhau

- **Tái hiện 1 (hồi quy):** thân phần Markdown ``"Gõ `a[0` rồi gọi dịch vụ sửa cửa kéo."``, HTML `"<p>Gõ <code>a[0</code> rồi gọi dịch vụ sửa cửa kéo.</p>"`, gợi ý cho trang dịch vụ bắt buộc #10. `check_suggestions` **nhận** gợi ý. `place_links` lại **bỏ qua** ("không thấy cụm từ ở chỗ chèn được"), nên `check_links(..., required_ids)` **Chặn** "Thiếu link bắt buộc tới «Sửa cửa kéo tại TP.HCM»". Code lượt 1: chèn đúng, Nên.
- **Tái hiện 2:** Markdown ``"Giá [cần bổ sung: `x]` thay ray mới] tùy.\n\nThợ thay ray mới rất nhanh."``, HTML tương ứng có `<code>x]</code>`. `check_suggestions` coi "thay ray mới" ở đoạn đầu nằm trong "[…]" và chỉ nhận nhờ đoạn sau. `apply_links` lại chèn vào **đoạn đầu**, giữa "[cần bổ sung: …]". Code lượt 1 cũng vậy (biến thể của SL-T039-2 chưa hết).
- **Nguyên nhân:** `markdown_blocks` che đoạn `mã` (`_mask_code`, `links.py:463`, gọi ở `:533`) **trước** khi che "[…]" (`:510`), nên dấu ngoặc trong mã không được tính. `_masked_runs` (`links.py:780-797`) lại tính dấu ngoặc ở mọi nút chữ, kể cả trong `<code>` (docstring ghi đây là chủ ý). Ở lượt 1 mỗi nút chữ che riêng, nên "[" trong `<code>` không lan sang chữ phía sau.
- **Mong đợi:** với HTML dựng từ Markdown, hai hàm thấy cùng một chỗ "[…]". Gợi ý đã nhận thì chèn được, và không chèn vào chỗ `check_suggestions` coi là "[…]".
- **Hậu quả nhỏ:** bài về sửa cửa hầu như không có đoạn mã. Không phải lỗ bảo mật: `href` vẫn từ danh sách bài, `sanitize_html` vẫn vô hiệu `[` `]`.
- **Sửa gợi ý:** `_TextRuns` ghi thêm nút chữ nào nằm trong `<code>` (đã có bộ đếm thẻ mở); `_masked_runs` bỏ qua dấu ngoặc của các nút đó, như `_mask_code`. Bản sao thử (ngoài repo): qua cả 2 ca và toàn bộ test của phiếu.

#### SL-T039-9 (Thấp) · Tên tham số dạng mảng PHP lọt kiểm link nháp

- **Tái hiện:** `check_links('<p><a href="https://suachuacuasat.com/?p[]=12">x</a></p>', INDEX)` cho Nên, "Link về trang chủ." Tương tự với `?p[0]=12`, `?p%5B%5D=12`, `?page_id[]=10`, `?name[]=bai-nhap`, `?pagename[x]=trang-nhap`. `/sua-cua-keo-tphcm/?preview_id[]=12` cho Nên, "Link tới bài đã đăng."
- **Vì sao không phải trang chủ:** PHP đọc tên `p[]`, `p[0]` là biến `p` dạng mảng. WordPress vì vậy vẫn nhận tham số `p`, `page_id`, `name`…, không mở trang chủ. Đây là suy luận theo cách PHP đọc tên tham số; tôi không thử trên site thật vì site không có bản thử. Các dạng này cùng họ với `?p=` mà phiếu yêu cầu Chặn.
- **Nguyên nhân:** `_php_name` (`links.py:187-190`) đổi mọi "[" thành "_". PHP chỉ làm vậy khi "[" không có "]" phía sau; có "]" thì tên biến dừng ở "[".
- **Mong đợi:** Chặn như `?p=12`.
- **Sửa gợi ý:** trong `_php_name`, nếu sau dấu "[" đầu tiên có "]" thì cắt tên tại "[", rồi mới đổi " ", "." thành "_". Hàm này dùng chung cho link bắt buộc (`_resolve_required`). Bản sao thử: qua cả 7 ca. Chỉ gặp khi người dùng tự gõ link.

### Quan sát (không tính là lỗi)

- **Dấu tổ hợp bị thẻ tách khỏi chữ cái.** Ví dụ HTML bất thường `"Gọi thợ sửa cửa<b>́</b> kéo"`: dấu sắc nằm trong thẻ sau, người đọc thấy "cửá". Với cụm từ "thợ sửa cửa", link bao "thợ sửa cửa" và dấu nằm ngoài link. Cơ chế này có từ lượt 1 với chữ không dấu: `"ke<b>́o</b>"` với cụm từ kết thúc ở "…ke" thì lượt 1 và lượt 2 đều chèn. Lượt 2 chỉ làm dạng NFD cũng gặp được. Nguyên nhân: kiểm "đứng trọn từ" chỉ xét trong một nút chữ. HTML dựng từ Markdown không tách chữ cái khỏi dấu, và `check_suggestions` chỉ nhận cụm từ có nguyên văn trong thân bài. Thực tế gần như không gặp: 15.000 bài thử ngẫu nhiên không gặp lần nào.
- **Chưa chạy trên Python 3.12.3** (máy không có). Các test SL-T039-6 không phụ thuộc bản Python; lượt chạy trên cloud sẽ xác nhận.
- **Dạng `?attachment_id=`, `?cat=`** vẫn là "Link về trang chủ", như Thợ Máy đã ghi (để Giai đoạn 5 quyết). Tôi không tính vào SL-T039-9.

### Bằng chứng (lượt 2)

Chạy trên Windows 11 (máy chủ dự án), worktree `wt-T-039`, Python 3.12.15, có agent khác chạy song song.

#### 1. Test của phiếu (bản cuối, sau khi thêm test mới)

```
$ uv run pytest tests/test_onpage_links.py tests/test_soi_loi_t039.py
461 passed, 10 xfailed in 29.04s
# trước lượt kiểm này (Thợ Máy): 459 passed; nay thêm 12 ca của Soi Lỗi: 2 qua, 10 xfail (SL-T039-7 → 9)
```

#### 2. Test liên quan (25 file, đúng danh sách lượt 1, mục Bằng chứng 2)

```
$ uv run pytest tests/test_ai_images.py tests/test_app_pages.py … tests/test_soi_loi_t039.py
2589 passed, 1 skipped, 28 xfailed in 232.31s (0:03:52)
# 1 bỏ qua và 18 trong 28 xfail là của các file khác, có từ trước (Thợ Máy lượt 2: 2587 passed,
# 1 skipped, 18 xfailed); 10 xfail còn lại là SL-T039-7 → 9; 2587 + 2 ca canh mới = 2589

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t039.py
1 file already formatted
$ PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files tests/test_soi_loi_t039.py docs/team/reports/T-039-soi-loi.md
"results": {}
```

Kiểm công cụ trước: file mồi có chữ tiếng Việt và khóa giả (thư mục tạm ngoài repo, quét xong đã xóa) bị bắt đúng "AWS Access Key", dòng 2.

#### 3. Test mới đỏ đúng lỗi, và qua khi lỗi được sửa

- Chạy với `--runxfail`: SL-T039-7 đỏ vì tỉ lệ thời gian ("gấp 4 độ dài thì chậm gấp 14.3 / 20.6 / 14.2 lần", ngưỡng 9). SL-T039-8 đỏ vì `placed.applied == ()` (ca 1) và vì link nằm ở đoạn đầu (ca 2). SL-T039-9 đỏ vì `Level.GOOD`. Chạy riêng SL-T039-7 6 lần: 6/6 `xfailed`, không lần nào qua oan.
- Bản sao `links.py` giả lập 3 bản sửa theo gợi ý ở trên (để ngoài repo, nạp bằng plugin pytest như Thợ Máy đã làm; không sửa repo): `uv run pytest tests/test_soi_loi_t039.py tests/test_onpage_links.py --runxfail` cho **471 passed**. Nghĩa là test mới qua được khi lỗi được sửa và không vướng test cũ.

#### 4. Thử ngẫu nhiên (script để ngoài repo)

- Script riêng của Soi Lỗi (chữ NFD bị thẻ/thực thể cắt ở mọi chỗ, chạy trên HTML gốc và HTML đã qua `sanitize_html`): 5 hạt giống × 3.000 bài = 15.000 bài (30.000 lượt chèn), 15.803 link được chèn. Đạt hết như ghi ở SL-T039-1.
- Script của Thợ Máy với hạt giống mới: `fuzz_round2.py` và `fuzz_round2c.py`, hạt giống 7101 và 7102, mỗi lượt 5.000 mẫu. Đạt cả 4 lượt.

#### 5. Tốc độ

```
$ for i in 1..5; uv run pytest tests/test_onpage_links.py tests/test_soi_loi_t039.py -k linear
32 passed, 438 deselected, 1 xfailed   (5/5 lượt; xfail là test_sl7_*)
```

32 test tốc độ (của Thợ Máy và Soi Lỗi, gồm 6 test tốc độ mới của Thợ Máy lượt 2) qua cả 5 lượt, không lượt nào đỏ oan. Hàm mới `_nfc_offsets`, `_masked_runs` chạy tuyến tính (test `test_apply_links_linear_round_2` của Thợ Máy); `unicodedata.normalize` của Python 3.12.15 cũng không chạy bậc hai với dãy dấu tổ hợp dài xen thứ tự (đo 20.000 → 320.000 dấu: dưới 0,3 giây). Chỗ duy nhất không tuyến tính tìm được là SL-T039-7.

### Đề xuất (lượt 2)

- **Thợ Máy, lượt ngắn trước khi gộp:** sửa SL-T039-7 theo hướng nameprep ở trên, gỡ `xfail` của `test_sl7_*`. Có thể làm luôn SL-T039-8 và SL-T039-9: cùng file, sửa nhỏ, đã có hướng sửa và test.
- Nếu Chỉ Huy muốn gộp ngay: SL-T039-8, SL-T039-9 để cùng T-041 hoặc trước Giai đoạn 5 (khi người dùng được tự gõ link). SL-T039-7 phải sửa trước khi `check_links` được nối vào app.
- Thêm vào test tốc độ của Thợ Máy một tên máy dài gồm nhiều chữ không phải ASCII khác nhau (ngoài chữ toàn khổ), như `test_sl7_*`.

### Câu hỏi cho chủ dự án (lượt 2)

Không có.

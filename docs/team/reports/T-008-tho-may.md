# Báo cáo T-008 · Gia cố bộ lọc HTML/link

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-008](../tickets/T-008-gia-co-bo-loc.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Bộ lọc chữ AI giờ bắt được mọi cách viết link Markdown mà Soi Lỗi tìm ra (ngoặc lồng nhiều tầng, nhãn hai dòng, địa chỉ ở dòng sau…), nên AI không giấu được link lạ vào bài nữa. Bài có thẻ `<embed>`, `<meta>`, `<input>` không còn bị mất nửa sau. Bộ lọc cũng không còn bị làm chậm: một bài 200 KB toàn mã xấu giờ lọc xong trong khoảng 0,05 giây (trước đây 40 KB đã mất gần 1 giây, 200 KB ước tính vài chục giây đến vài phút). Kết quả nghiên cứu và dàn ý do AI trả về giờ cũng được lọc ngay khi nhận, giống thân bài.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/sanitize.py` | `strip_tags`: bỏ khối thẻ nguy hiểm bằng một lượt quét (không còn regex `.*?` chạy bậc hai), giới hạn 8 lượt bóc thẻ lồng. `strip_markdown_links`: viết lại thành bộ đọc một lượt (ghép ngoặc, có escape, không vượt dòng trống) thay cho regex đoán link; khai báo `[nhãn]:` nhận cả nhãn nhiều dòng, địa chỉ ở dòng sau, trong trích dẫn/danh sách. `is_safe_url`: chặn `//…`, `/\…`, `\…`. Thêm `DANGEROUS_VOID_TAGS` (`input`, `base`, `link`, `meta`, `embed`, `frame`): chỉ bỏ thẻ, không nuốt phần sau. |
| `seo_app/content/workflow.py` | Thêm `clean_research`, `clean_outline` (lọc mọi trường chữ), gọi ở `research()` và `outline()`; tiêu đề lấy từ dàn ý (khi AI bỏ trống tiêu đề bài) cũng qua `strip_tags`. |
| `tests/test_sanitize_bypass.py` | Gỡ 2 dấu `xfail` (14 trường hợp), sửa chú thích. Không xóa test nào. |
| `tests/test_sanitize_hardening.py` (mới) | 49 trường hợp: tốc độ với 13 loại đầu vào 200 KB, biến thể link, chữ thường có ngoặc không bị đụng, `is_safe_url`, thẻ rỗng, lọc nghiên cứu/dàn ý ở ranh giới AI. |

## Bằng chứng

```
$ uv run pytest            # trước khi sửa
344 passed, 23 xfailed in 18.25s

$ uv run pytest            # sau khi sửa
407 passed, 9 xfailed in 18.75s

$ uv run ruff check .
All checks passed!
```

9 `xfailed` còn lại là lỗi của T-002, thuộc phiếu T-006 (làm tiếp ngay sau phiếu này).

Đo tốc độ (máy cloud, `clean_ai_text`):

| Đầu vào | Bộ lọc cũ (HEAD `e1c5f33`) | Bộ lọc mới |
|---|---|---|
| `<script>` × 5 000 (40 KB) | 0,84 s | — |
| `[` × 20 000 (20 KB) | 2,57 s | — |
| `<script>` × 25 000 (200 KB) | (bậc hai, ước tính ~20 s) | 0,04 s |
| `[` × 200 000 (200 KB) | (bậc hai, ước tính ~250 s) | 0,05 s |
| `<<<…a>a>a>` 200 KB (thẻ lồng sâu) | — | 0,22 s |

Test `test_filters_run_fast_on_huge_malicious_input` kiểm cả `clean_ai_text` lẫn `sanitize_html` trên 13 loại đầu vào 200 KB, mỗi loại phải xong dưới 1 giây.

## Đối chiếu tiêu chí xong

- [x] 14 test `xfail` của `test_sanitize_bypass.py` chuyển thành `passed` (`test_dangerous_void_tag_does_not_swallow_rest_of_article` ×5, `test_clean_ai_text_drops_commonmark_link_variants` ×9).
- [x] Test mới: đầu vào 200 KB toàn `<script>` hoặc `[` lọc xong dưới 1 giây (`tests/test_sanitize_hardening.py::test_filters_run_fast_on_huge_malicious_input[script]`, `[ngoac-vuong]` và 11 loại khác).
- [x] Lá Chắn #2: `test_protocol_relative_urls_are_blocked`. Lá Chắn #3: `test_clean_research_and_outline_clean_every_field`, `test_research_and_outline_are_cleaned_at_ai_boundary`, `test_title_falls_back_to_cleaned_outline_title`. Lá Chắn #4 / Soi Lỗi #3: `test_dangerous_void_tags_are_dropped_without_eating_the_rest`.
- [x] Báo cáo này.

## Rủi ro và điểm cần chú ý

- Bộ đọc link **bắt rộng hơn chuẩn CommonMark**: hễ thấy `](` có ngoặc `)` khớp trong cùng đoạn văn là bỏ phần trong ngoặc. Hệ quả có thể có: một địa chỉ vốn chỉ hiện thành chữ (không phải link) cũng bị bỏ, ví dụ `[a [b](x) c](y)` mất cả `(y)`. Chọn hướng này vì mất chữ thừa an toàn hơn sót link. Câu chữ thường có ngoặc (`[cần bổ sung: …] (ghi chú)`, `(đã gồm VAT)`, ngoặc chưa đóng) không bị đụng — có test.
- Dòng bắt đầu bằng `[chữ]:` rồi một từ (ví dụ `[Lưu ý]: cần đo trước`) bị coi là khai báo link và bị bỏ cả dòng (giống bộ lọc cũ, nay rộng hơn: cả trong trích dẫn, danh sách). AI hiếm khi viết vậy.
- Thẻ lồng sâu hơn 8 tầng (`<<<…script>…`) không được bóc sạch hết: phần sót chỉ còn là chữ (`< script`), không thành thẻ được. Có test `test_deeply_nested_tags_leave_no_real_tag`.
- Các lỗi Thấp còn lại trong báo cáo Soi Lỗi (`ui.highlight` cắt ngang mã thực thể, địa chỉ viết trần vẫn thành link) không thuộc phiếu này.

## Đề xuất

- Soi Lỗi và Lá Chắn kiểm lại theo phiếu (bộ đọc link mới là phần đáng thử lách nhất).
- Lá Chắn #5 (Python 3.12.3 chưa có vá CVE-2025-6069): ghi `3.12.11` hoặc mới hơn vào `.python-version` khi tiện; không thuộc phạm vi phiếu này.

## Câu hỏi cho chủ dự án

Không có.

## Làm lại (2026-10-14, sau [Soi Lỗi T-003-006-008-009](T-003-006-008-009-soi-loi.md))

Soi Lỗi tìm thêm hai cách lách mức Cao (SL-1, SL-2) và bốn lỗi khác. Tất cả đã sửa trong `seo_app/sanitize.py`.

| Lỗi | Sửa |
|---|---|
| SL-1 (Cao): tiêu đề link có "(" lẻ làm lệch ghép ngoặc, link lọt | Gặp `](` mà "(" không có ")" khớp thì bắt rộng: bỏ tới ")" cuối cùng của đoạn văn. Đoạn không có ")" nào thì đó không phải link (CommonMark), nên giữ nguyên. Vị trí ")" cuối mỗi đoạn được tính sẵn trong `_matching_parens`, tra bằng `bisect`, nên vẫn chạy tuyến tính. |
| SL-1b: địa chỉ `<…(>` | Cùng cách sửa SL-1. |
| SL-2 (Cao): bỏ một link ghép phần còn lại thành link mới | `clean_ai_text` lặp "bỏ thẻ → bỏ link" tới khi chữ không đổi, tối đa 4 lượt. Chữ cố tình lồng sâu hơn 4 tầng thì dùng bước dự phòng: xóa mọi dấu `]` đứng ngay trước `(`, nên không còn link nào. Địa chỉ khi đó **hiện ra thành chữ** (người dùng nhìn thấy, đúng security.md 2.3). |
| SL-3: bỏ link làm hiện ra thẻ HTML | Cùng vòng lặp với SL-2. Bước dự phòng tách `<` khỏi chữ cái. Hai bước dự phòng chỉ xóa `]` hoặc thêm dấu cách nên không tạo ra link hay thẻ mới. |
| SL-4: dòng `[nhãn]: chữ` bị xóa cả dòng | `_MD_LINK_DEF` chỉ nhận đúng dạng CommonMark: sau địa chỉ chỉ được có tiêu đề (`"…"`, `'…'`, `(…)`) rồi hết dòng. Dòng tiếp theo trong trích dẫn (`> `) vẫn được nhận. |
| SL-5: `button/form/select/option/svg/math` không đóng nuốt phần sau | Thêm `DANGEROUS_CONTAINER_TAGS`: chỉ bỏ thẻ, giữ chữ bên trong và phía sau, giống trình duyệt. Thẻ con nguy hiểm (`script`…) vẫn bị bỏ cả ruột. Thuộc tính vẫn bị bỏ vì thẻ không nằm trong danh sách cho phép. |

**Test:**
- Gỡ 6 dấu `xfail` (18 trường hợp) trong `tests/test_soi_loi_t003_t009.py` của Soi Lỗi.
- Thêm vào `tests/test_sanitize_hardening.py` 20 trường hợp:
  - Lồng sâu hơn số lượt, chuỗi 160–200 KB: không còn link hay thẻ, xong dưới 1 giây.
  - Link có tiêu đề chứa ngoặc lẻ vẫn giữ nhãn.
  - Dòng `[nhãn]:` thường được giữ nguyên dòng.
  - Khai báo link có tiêu đề hoặc nằm trong trích dẫn vẫn bị bỏ.
  - Thẻ "bọc" giữ chữ.

Đo tay (máy cloud): lồng 20 000 tầng (100 KB) mất 0,13 s; `[a][](x)` × 20 000 (160 KB) mất 0,11 s; `[a](u "(")` × 20 000 mất 0,02 s.

```
$ uv run pytest
575 passed, 18 xfailed in 22.83s      # 18 xfail còn lại thuộc T-010 (SL-6…SL-14) và SL-7

$ uv run ruff check .
All checks passed!
```

**Rủi ro:**
- Bắt rộng ở SL-1 có thể xóa thừa chữ tới dấu ")" cuối đoạn, nhưng chỉ khi có `](` mà ngoặc lệch (bất thường trong bài thật).
- Ở bước dự phòng, địa chỉ còn lại hiện thành chữ trần. Streamlit tự biến địa chỉ trần thành link bấm được: đây là rủi ro Lá Chắn #2 đã chấp nhận (người dùng nhìn thấy địa chỉ). Giai đoạn 5 phải liệt kê mọi URL trước khi gửi.
- Nội dung trong `<form>`/`<svg>`… giờ được giữ thành chữ (trước đây bị bỏ cả ruột).

## Làm lại lần 2 (2026-10-14, sau [Soi Lỗi R3](T-008r-010-011-soi-loi.md) và [Lá Chắn](T-008r-010-011-la-chan.md))

**Đổi cách làm.** Ba vòng trước đều cố *nhận ra* link để xóa, và lần nào cũng còn một dạng CommonMark ít gặp lọt qua. Lần này an toàn không còn phụ thuộc việc nhận ra link nữa.

Mọi link Markdown đều cần một dấu `]` (không escape) đứng **sát ngay trước** một trong ba ký tự:
- `(`: link hoặc ảnh nội dòng;
- `[`: link tham chiếu `[chữ][nhãn]` hoặc `[chữ][]`;
- `:`: dòng khai báo `[nhãn]: địa chỉ`. Link kiểu `[nhãn]` trơn chỉ thành link khi có dòng khai báo.

Hàm mới `escape_link_syntax` (`seo_app/sanitize.py`) thêm dấu `\` trước ký tự đó. Markdown vẫn hiện `](`, `][`, `]:` y như cũ, nhưng không còn là link.

### Cách làm

1. Đầu `clean_ai_text`, đổi `\r\n` và `\r` thành `\n` (Lá Chắn #2).
2. Vòng "bỏ thẻ → bỏ link" cũ vẫn giữ, nhưng **chỉ để chữ gọn** (bỏ địa chỉ thừa). Đã bỏ `_LINK_JOIN`; bước dự phòng chỉ còn tách `<`.
3. Cuối `clean_ai_text`, gọi `escape_link_syntax`. Đây là bước quyết định an toàn.
   - Chạy một lượt, tuyến tính. Chạy lại không đổi gì.
   - Chỉ **thêm** dấu `\`, không xóa hay đổi ký tự nào. Vì vậy không thể tạo ra thẻ hay link mới.
   - Dấu `:` chỉ được escape khi `[` mở nhãn đứng đầu dòng, sau thụt lề, `>`, `-`, `*`, `+` hoặc `1.`. Khai báo link chỉ có thể nằm ở đó. Nhờ vậy câu thường kiểu `Mục [1] và [2]: …` giữ nguyên.
4. **Vì sao escape khi lọc (lúc nhận kết quả AI), không escape lúc hiển thị:**
   - Kết quả AI được lọc ở **một** chỗ (`workflow.py`). Còn chỗ hiển thị thì nhiều (`write.py` có hơn 10 chỗ), và Giai đoạn 4–5 sẽ thêm chỗ xuất lên WordPress. Escape lúc hiển thị thì mỗi chỗ mới đều phải nhớ gọi, dễ sót.
   - Dấu `[` và `]` giữ nguyên, nên `find_missing` vẫn nhận ra `[cần bổ sung: …]` mà không cần sửa chỗ dò.
5. R3-4: nhãn `[cần bổ sung: …]` không bao giờ bị coi là link, nên phần `(…)` phía sau được giữ. Dấu `(` ngay sau `]` vẫn được escape.

### Từng lỗi

| Lỗi | Sửa |
|---|---|
| R3-1 (Cao), lồng 4 tầng | Đạt nhờ bước escape: link còn sót sau 4 lượt lọc bị vô hiệu. |
| R3-2 (Cao) / Lá Chắn #1, #2: khai báo có tiêu đề escape, `\r\n`, `\r`, NBSP | Chuẩn hóa xuống dòng, rồi escape `]:` đầu dòng. `[Gọi thợ][foo]` cũng thành `[Gọi thợ]\[foo]`, nên không còn là link dù khai báo có lọt. |
| R3-3 (Trung bình): tiêu đề bài, tiêu đề mục, reason, summary chỉ qua `strip_tags` | `workflow.py` dùng `clean_ai_text` cho reason và summary. Tiêu đề bài/mục (bài viết và dàn ý) và tiêu đề dự phòng lấy từ dàn ý dùng hàm mới `clean_ai_line`, tức `clean_ai_text` rồi gộp thành một dòng. Tên bài đối thủ vẫn chỉ `strip_tags`, vì `write.py` hiển thị nó qua `markdown_link`, hàm này đã escape mọi ký tự Markdown. Escape thêm ở đây thì dấu `\` sẽ hiện ra. Địa chỉ đối thủ vẫn qua `_clean_url`. **Không sửa `app/`.** |
| (thêm) Áp gợi ý sửa câu ghép ra link | Khi thay hoặc xóa một câu, chỗ nối có thể ghép `[thợ]` với `(https://…)` thành link mới. `apply_flag` nay escape lại kết quả. |
| R3-4 (Thấp) | Như mục 5 ở trên. |
| R3-5 (Thấp) | `_phrase_pattern` (`rules.py`) chỉ đòi ranh giới từ ở đầu hoặc cuối cụm khi đầu hoặc cuối cụm là chữ hay số. |
| R3-6 / Lá Chắn #3 | `redact_secrets` (`ai/base.py`) nhận thêm `apiKey`/`api-key`, `secret` (gồm `client_secret`), `private_key`, `passwd`, `user:pass@` trong địa chỉ, `Bearer:xyz` và `Basic` + xuống dòng. |
| R3-7 / Lá Chắn #4 | `_neutralize` (`prompts.py`) chạy NFKC trước (vì NFKC biến U+FFA0 thành U+1160), rồi bỏ ký tự loại Cf và các ký tự "mặc định bỏ qua" khác: U+034F, U+115F, U+1160, U+17B4–5, U+180B–D, U+180F, U+2065, U+3164, U+FE00–FE0F, U+FFA0, U+FFF0–8 và U+E0100–E01EF. |
| Lá Chắn #5 | Trong `rewrite_prompt`, dấu `«` và `»` trong tiêu đề mục đổi thành `‹` và `›`. |

### Test

- Gỡ 8 dấu `xfail` (20 trường hợp) trong `tests/test_soi_loi_round3.py`. Chỉ còn SL-7 (để Giai đoạn 5).
- Thêm `tests/test_link_escape.py` (82 trường hợp):
  - 21 kiểu tấn công, gồm các dạng của Lá Chắn #1 và #2 và lồng 10 tầng: không còn `](`, `][` hay `[nhãn]:` đầu dòng chưa escape, không còn `\r`.
  - Lọc và escape chạy lại không đổi gì; escape chỉ thêm `\`.
  - Chữ thường giữ nguyên; `[cần bổ sung]` vẫn được nhận ra.
  - Chuỗi 300 KB xong dưới 1 giây.
  - Mọi trường của nghiên cứu và dàn ý; tiêu đề thành một dòng.
  - Áp gợi ý không ghép được link.
  - Các lỗi Thấp.
- **Đã sửa test của chính Thợ Máy** cho hợp với cách mới. Ý đồ an toàn không đổi, chỉ đổi đầu ra mong đợi từ `][` thành `]\[`, `](` thành `]\(`, `]:` thành `]\:`:
  - `tests/test_sanitize.py::test_clean_ai_text_strips_markdown_links` (1 trường hợp);
  - `tests/test_sanitize_hardening.py::test_markdown_link_variants_lose_their_target` (2 trường hợp);
  - `tests/test_sanitize_hardening.py::test_label_colon_sentences_are_kept_whole` (4 trường hợp);
  - trường hợp `Cửa [loại A](chưa chốt\n\nđoạn sau)` tách khỏi `test_normal_brackets_are_kept` thành test riêng `test_paren_after_bracket_across_blank_line_is_kept_but_escaped`.

### Test của Soi Lỗi KHÔNG sửa, đang đỏ (để Chỉ Huy và Soi Lỗi quyết)

`tests/test_soi_loi_round3.py::test_normal_vietnamese_with_brackets_is_untouched` đòi `clean_ai_text(text) == text`. 5 trường hợp đỏ vì dòng bắt đầu bằng `[nhãn]:` nay có thêm một dấu `\`:

| Đầu vào | Đầu ra |
|---|---|
| `[Lưu ý]: cần đo khe ray trước khi đặt cửa.` | `[Lưu ý]\: …` |
| `1. [Bước 1]: Tắt cầu dao (CB) …` | `1. [Bước 1]\: …` |
| `**[Mẹo]:** tra dầu vào ray …` | `**[Mẹo]\:** …` |
| `> [Lưu ý]: lò xo xoắn …` | `> [Lưu ý]\: …` |
| `[cần bổ sung: giá thay lò xo]: hỏi lại xưởng` | `[cần bổ sung: giá thay lò xo]\: …` |

Khi hiển thị bằng Markdown, chữ trên màn hình y hệt bản gốc, không mất chữ nào, và `[cần bổ sung]` vẫn được nhận ra. Nếu muốn các dòng này giữ nguyên từng ký tự thì phải đoán dòng nào là khai báo link thật, tức là quay lại cách "nhận ra link" mà phiếu yêu cầu bỏ. Đề xuất: Soi Lỗi đổi kỳ vọng thành "hiện ra giống bản gốc", tức là `out.replace("\\", "") == text`, kèm "không còn link".

### Bằng chứng

```
$ uv run pytest
5 failed, 822 passed, 1 xfailed in 26.59s
# 5 failed = test_normal_vietnamese_with_brackets_is_untouched (5 trường hợp ở bảng trên)
# 1 xfailed = SL-7 (Giai đoạn 5)

$ uv run ruff check .
All checks passed!
```

### Rủi ro

- **Dấu `\` hiện ra ở chỗ không dùng Markdown:**
  - Ô "Sửa trực tiếp" (`st.text_area`) và ô sửa tiêu đề dàn ý hiện `[Lưu ý]\:` hoặc `]\(` khi AI viết kiểu đó.
  - Lời dặn gửi lại AI (viết lại, rà soát) cũng mang dấu `\`.
  - Không mất chữ và không hại gì, chỉ hơi lạ mắt.
  - Khi làm phần xuất lên WordPress (Giai đoạn 4–5), phải chuyển Markdown sang HTML bằng bộ chuyển chuẩn: dấu `\` sẽ biến mất đúng như khi hiển thị.
- Chữ trong đoạn code (`` `…` ``) có `](` sẽ hiện thêm dấu `\`, vì Markdown không xử lý escape trong code. Bài sửa cửa hiếm khi có đoạn code.
- Nếu người dùng tự gõ link trong ô "Sửa trực tiếp" rồi bấm "Áp dụng" một gợi ý ở cùng phần, link đó cũng bị escape (`apply_flag` escape lại cả phần). Đây là đánh đổi để chỗ nối không ghép ra link.
- Địa chỉ viết trần (`https://…`, không ngoặc) vẫn được Streamlit/GFM tự biến thành link. Đây là rủi ro đã ghi ở lần trước, ngoài phạm vi phiếu này.

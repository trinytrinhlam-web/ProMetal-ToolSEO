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

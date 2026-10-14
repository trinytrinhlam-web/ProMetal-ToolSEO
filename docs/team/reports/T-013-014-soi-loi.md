# Báo cáo T-013, T-014 · Kiểm thử (Soi Lỗi)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-013](../tickets/T-013-escape-cau-can-xem-lai.md), [T-014](../tickets/T-014-loi-thap-escape.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. T-013 **đạt**, T-014 **đạt**. Còn 1 lỗi Thấp chỉ làm mất chữ (R5-1), không ảnh hưởng an toàn |

## Tóm tắt (cho chủ dự án)

Khung «Cần xem lại» nay không còn tạo được link, kể cả dòng «Gợi ý». Tôi thử khoảng 7 nghìn câu cắt từ bài có bẫy và 20 nghìn chuỗi ngẫu nhiên, rồi cho qua hai bộ hiển thị Markdown thật. Không chỗ nào còn link. Chữ có kiểu xuống dòng `\r` được chặn link giống như xuống dòng thường. Sửa tay rồi lưu lại cũng không làm sai chữ.

Còn một lỗi nhỏ chỉ ảnh hưởng chữ hiển thị. Câu như «Cửa [A](dày "mỏng" 1mm)» vẫn bị cắt mất phần trong ngoặc.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_round5.py` (mới) | 55 trường hợp: 52 qua, 3 `xfail(strict=True)` (R5-1) |

Tôi không sửa code ứng dụng, `config/` hay test cũ, và không chạy `git stash`, `checkout` hay `reset` (R11).

Để kiểm thử `quote_ai_text`, tôi đọc riêng hàm này từ `write.py` bằng `ast`. Lý do: nhập cả file sẽ chạy luôn trang Streamlit. Tôi đã thử thay hàm bằng hai bản lỗi, `> {câu}` và «trích dẫn từng dòng nhưng không escape». Test bắt được cả hai, mỗi bản 66 câu lỗi.

## Bằng chứng

```
$ uv run pytest
1444 passed, 6 xfailed in 37.96s
# 6 xfail: R4-3 ×2 (Chỉ Huy chấp nhận, giữ nguyên), SL-7 (Giai đoạn 5), R5-1 ×3 (mới)

$ uv run ruff check .
All checks passed!
```

**Đối chiếu bằng bộ hiển thị thật.** Tôi chạy tạm trong thư mục nháp, không thêm thư viện vào dự án. Hai bộ hiển thị là `markdown-it-py` (qua `uv run --with markdown-it-py`) và `micromark` + GFM trên Node 22. Họ micromark là loại Streamlit dùng. Tôi đếm các link mà chữ hiện ra khác với địa chỉ thật.

| Bộ thử | Số mẫu × 2 bộ hiển thị | Còn link |
|---|---|---|
| `quote_ai_text` trên mọi đoạn con dài tối đa 80 ký tự, lấy từ 8 bài có bẫy (`[x]:` giữa dòng, `](`, `\]`, `\\]`, nhãn nhiều dòng, `\r`). Mỗi bài thử cả bản đã lọc và bản chỉ escape | 7 241 | 0 |
| `quote_ai_text` trên chuỗi ngẫu nhiên có `\r`, `\r\n`, `` ` ``, `>`, thụt lề | 20 000 | 0 (*) |
| `**Gợi ý:** {clean_ai_text(x)}`: 12 kiểu tấn công và 10 000 chuỗi ngẫu nhiên, thêm khung `> {…}` để đối chứng | 19 826 | 0 |
| `escape_link_syntax` gọi trực tiếp (như ở `save_manual` và `apply_flag`) trên chữ có `\r` | 20 009 | 0 |
| `escape(unescape(escape(t)))` trên chữ có `\r` | 20 009 | 0 |

(*) Có 1 mẫu bị bộ đếm báo nhầm. Đó là chuỗi ngẫu nhiên chưa lọc có `<bhttps://evil.example]>`, tức một link tự động hiện chính địa chỉ (rủi ro đã chấp nhận từ T-004). Câu thật trong app luôn là đoạn con của bài đã lọc, nên `<b…>` đã bị bỏ trước khi tới đây.

**Round-trip với `\r`.** Thử 100 000 chuỗi ngẫu nhiên, đều đúng ba điều sau:
- Chạy `escape` hai lần cho kết quả như chạy một lần.
- `escape(unescape(e)) == e`.
- `unescape(escape(s)) == s` với mọi `s` không có `\`.

Thêm một tính chất: đổi mọi `\n` thành `\r` (hoặc `\r\n`) thì kết quả của `escape` và `unescape` đổi đúng theo (`test_carriage_return_behaves_like_newline`). Thử ngẫu nhiên 200 000 chuỗi có `\f`, `\v`, NBSP, `` ` ``: không lỗi chương trình, `clean_ai_text` luôn trả chữ không còn link.

## Kết luận từng phiếu

| Phiếu | Kết luận | Lý do |
|---|---|---|
| T-013 | **Đạt** | `quote_ai_text` (`app/views/write.py:477-486`): mọi dòng đều bắt đầu bằng `>`, `\r` và `\r\n` được tách đúng, và bước escape chạy sau khi đã thêm `> `. Đã chạy qua bộ hiển thị thật như bảng trên. Ngoài ra có test AppTest bấm «Kiểm tra lại toàn bài» với câu thay độc: dòng «Gợi ý» hiện `[thợ]\:` và không có link. |
| T-013, dòng `**Gợi ý:** {replacement}` (`write.py:520`) | **Đạt**, nay có bằng chứng | Suy luận của Họa Sĩ đúng. `replacement` đã qua `clean_ai_text`. Tiền tố `**Gợi ý:** ` chỉ khiến dòng đầu *không còn* là đầu dòng, nên bước escape lúc trước chỉ thừa chứ không thiếu. Các dòng sau giữ nguyên vị trí đầu dòng. Bằng chứng: `test_suggestion_line_has_no_link` (11 mẫu), `test_suggestion_line_on_page_has_no_link`, và kết quả trên 19 826 mẫu ở bảng. |
| T-014 · R4-2 + Lá Chắn #1 (`\r`) | **Đạt** | `sanitize.py:356, 400`. Không còn đường lách nào với `\r` đứng riêng: khai báo nằm sau `\r`, trong `>`, trong danh sách, nhãn có `\r`, địa chỉ ở dòng sau `\r`. Round-trip đúng như mục Bằng chứng. |
| T-014 · R4-4 | **Đạt**, còn lỗi chữ nhỏ R5-1 | `[rè rè](sau mưa)`, `[a](x\ y)` và trường hợp bị dòng trống cắt đôi đều giữ đủ chữ. Mười dạng link thật vẫn bị bỏ địa chỉ, khớp với markdown-it: có tiêu đề `"` `'` `(`, có `<…>`, có dấu cách quanh địa chỉ, có tab hay xuống dòng trước tiêu đề, có `\r`. Phần này chỉ làm chữ gọn hơn; an toàn vẫn do bước escape lo, và bước escape không đổi gì ngoài `\r`. |
| T-014 · R4-3 | Giữ `xfail` theo quyết định của Chỉ Huy | Không kiểm thử thêm. Phần `_code_spans` mới chỉ dùng trong `strip_markdown_links`, nên không ảnh hưởng an toàn. Đã thử ngẫu nhiên với `` ` `` / ` `` `: không lỗi chương trình, không lọt link. |

## Lỗi tìm thấy

### R5-1 · Thấp (chỉ mất chữ) · Ngoặc có tiêu đề rồi thêm chữ vẫn bị cắt
- **Vị trí:** `seo_app/sanitize.py:205`. `looks_like_destination` chỉ xét ký tự **đầu tiên** sau địa chỉ (`"`, `'` hoặc `(`), không kiểm tra tiêu đề có đóng rồi hết ngoặc hay không.
- **Tái hiện:** `clean_ai_text('Cửa [A](dày "mỏng" 1mm) nhé.')` ra `'Cửa A nhé.'`. Tương tự với `Xem [Bảng 1](cột 'giá' bên phải).` và `Cửa [A](dày (mỏng) 1mm) nhé.`.
- **Mong đợi:** giữ nguyên chữ, chỉ thêm `\` sau `]`. Theo CommonMark đây không phải link: markdown-it-py không tạo thẻ `<a>`.
- **Thực tế:** mất cả phần trong ngoặc. **Không ảnh hưởng an toàn.**
- **Test:** `test_r5_1_parenthesis_with_quote_then_more_words_keeps_text` (3 mẫu, `xfail strict`).
- **Gợi ý sửa (Thợ Máy):** sau ký tự mở tiêu đề, tìm ký tự đóng tương ứng, rồi kiểm tra từ đó tới `)` chỉ còn khoảng trắng. Cần giữ thời gian chạy tuyến tính. Cũng có thể chấp nhận lỗi này vì rất hiếm gặp.

Ghi chú nhỏ, chưa tính là lỗi: `[a](u\f't')` và `[a](u\v't')` cũng bị cắt dù không phải link. AI hầu như không bao giờ viết ra ký tự `\f`, `\v`.

## Tốc độ: test «dưới 1 giây» có dễ chập chờn không

Tôi đo trên máy cloud 4 nhân:
- Test thời gian chậm nhất trong bộ test hiện tại mất 0,38 s (`test_filters_run_fast_on_huge_malicious_input[the-long-nhau]`). Các test T-014 mất 0,11–0,27 s.
- Mẫu 0,8 s Thợ Máy đo tay (`[a]( ` × 50 000 + `)` × 50 000) **không có** trong bộ test. Tôi đo lại được 0,72 s. Với 450 KB thì 1,17 s, với 1,2 MB thì 2,97 s: tăng tuyến tính, chỉ là hệ số lớn.
- `[](\n` × 60 000 + `)` × 60 000 (300 KB) mất **1,01 s**, vượt mốc 1 s ngay trên máy cloud. Mẫu này cũng không có trong bộ test.
- Trên thực tế, AI trả về tối đa 32 000 token (`config/ai.toml`), tức khoảng 130 KB, nên mất khoảng 0,3 s hoặc ít hơn. Người dùng không bị treo app.

Mốc «< 1 s» hiện có dư khoảng 2,5 lần. Tôi chạy thử khi 6 tiến trình chiếm CPU: các phép đo chậm gấp khoảng 2 lần. Trên máy Windows yếu có phần mềm diệt virus quét, test có thể đỏ thỉnh thoảng.

**Đề xuất (Chỉ Huy quyết):** chuyển test tốc độ sang đo **tỉ lệ**. Tôi đã làm mẫu trong `test_clean_grows_linearly_on_nested_parentheses`: cùng một hàm, độ dài gấp 4 thì thời gian phải tăng dưới 9 lần. Tăng tuyến tính thì khoảng 4 lần, tăng bình phương thì khoảng 16 lần. Máy chậm làm chậm cả hai lần đo nên tỉ lệ gần như không đổi. Tôi đo 40 lần, cả khi máy bận: tỉ lệ từ 1,65 đến 6,37. Một cách khác là giữ test cũ nhưng nới mốc lên 3 s; như vậy vẫn bắt được lỗi bình phương, vì lỗi đó tốn hàng chục giây. Tôi không sửa test cũ vì nằm ngoài phạm vi.

## Đối chiếu tiêu chí xong

- [x] Câu AI chỉ ra hiển thị không có link (`test_quote_of_any_substring_of_safe_body_has_no_link`, `test_quote_random_text_has_no_link`, `test_r4_1_…` của lượt 4 nay đã qua). Đã đối chiếu với bộ hiển thị thật.
- [x] Dòng «Gợi ý» không có link (`test_suggestion_line_has_no_link`, `test_suggestion_line_on_page_has_no_link`)
- [x] `\r`: escape đúng, round-trip đúng (`test_escape_blocks_definitions_after_lone_carriage_return`, `test_round_trip_with_carriage_returns`, `test_carriage_return_behaves_like_newline`)
- [x] R4-4: không phải link thì giữ chữ, link thật thì bỏ địa chỉ (`test_not_links_keep_their_text_and_stay_safe`, `test_real_links_with_title_or_spaces_lose_their_address`)
- [ ] R5-1, lỗi chữ hiếm gặp: vẫn còn
- [x] Tốc độ vẫn tuyến tính (`test_clean_grows_linearly_on_nested_parentheses`)

## Rủi ro và điểm cần chú ý

- `quote_ai_text` chỉ để hiển thị. Hai nút Áp dụng và Bỏ qua dùng câu gốc; test AppTest của Họa Sĩ đã kiểm điều này (`write.py:521-536`).
- Thợ Máy có ghi rằng đã chạy `git stash` khoảng 2 giây trong lúc Họa Sĩ đang làm. Tôi kiểm lại: bản sửa của Họa Sĩ trong `write.py` và 2 test mới trong `tests/test_edit_unescape.py` vẫn còn đủ và đều qua. Không thấy mất gì.
- Chữ đã lọc giờ có thể còn `[a]\(x y)`, chỗ trước đây chỉ còn `a`. Khi hiển thị, chữ này ra `[a](x y)`, không phải link.

## Đề xuất

- R5-1: giao Thợ Máy nếu muốn sửa, hoặc chấp nhận vì không ảnh hưởng an toàn.
- Test tốc độ: đổi sang đo tỉ lệ, hoặc nới mốc lên 3 s (xem mục Tốc độ). Việc này thuộc về người viết test tương ứng (Thợ Máy và Soi Lỗi).

## Câu hỏi cho chủ dự án

Không có.

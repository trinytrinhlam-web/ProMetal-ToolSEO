# Báo cáo T-008 (lần 3), T-012 · Kiểm thử (Soi Lỗi)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-008](../tickets/T-008-gia-co-bo-loc.md) (làm lại lần 3), [T-012](../tickets/T-012-an-dau-escape-o-o-sua.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. T-008 lần 3 **đạt** cho mọi trường chữ AI qua `clean_ai_text` / `clean_ai_line` / `apply_flag`; còn **1 lỗi Trung bình ở chỗ hiển thị** (R4-1) và 3 lỗi Thấp. T-012 **đạt** |

## Tóm tắt (cho chủ dự án)

Cách mới (thêm một dấu `\` vô hình ngay sau `]`) chặn được link rất chắc: tôi thử khoảng 190 nghìn đoạn chữ ngẫu nhiên và hơn 50 kiểu tấn công viết tay, rồi đưa kết quả qua **hai bộ hiển thị Markdown thật**. Không đoạn nào còn tạo được link. Ô sửa tay (T-012) hiện chữ sạch, không có dấu `\`, và bấm Lưu thì chữ được bảo vệ lại y như cũ.

Còn một lỗ ở **khung "Cần xem lại"**: câu AI chỉ ra được hiện bằng dạng trích dẫn `> câu`. Nếu AI chọn đúng một đoạn bắt đầu bằng `[nhãn]:`, khung này lại thành link bấm được (R4-1, Trung bình). Bài viết thì vẫn an toàn. Ngoài ra có 3 lỗi Thấp: chữ trong đoạn `code` hiện thêm dấu `\`, `[chữ](chữ có dấu cách)` vẫn bị cắt mất phần trong ngoặc, và hàm escape chưa tự hiểu ký tự xuống dòng `\r`.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_round4.py` (mới) | 527 trường hợp: 520 qua, 7 `xfail(strict=True)` ứng với R4-1 … R4-4 |
| `tests/test_soi_loi_round3.py` | Sửa `test_normal_vietnamese_with_brackets_is_untouched` theo quyết định của Chỉ Huy (xem dưới) |

Không sửa code ứng dụng, `config/`, hay test của agent khác.

**Sửa test theo quyết định của Chỉ Huy.** Ý đồ của test là "chữ tiếng Việt thường không bị hỏng khi hiển thị". Kỳ vọng cũ `clean_ai_text(text) == text` đổi thành: (1) `unescape_link_syntax(out) == text`, (2) `out.replace("\\", "") == text` (bỏ các `\` do escape thì bằng đầu vào), (3) `out` không còn `](` chưa escape. 11 mẫu đều qua. Ghi chú: Thợ Máy đã gỡ dấu `xfail` khỏi 9 test R3-1…R3-7 của tôi trong file này vì chúng nay đã qua (đúng quy ước XPASS → gỡ `xfail`).

## Bằng chứng

```
$ uv run pytest          # trước khi sửa test (theo Chỉ Huy)
5 failed (test_normal_vietnamese_with_brackets_is_untouched)

$ uv run pytest          # sau khi sửa test + thêm test_soi_loi_round4.py
1367 passed, 8 xfailed in 28.22s

$ uv run ruff check .
All checks passed!
```

`xfail` còn lại: 7 của file mới + 1 cũ (SL-7, từ khóa ngoài khung, để Giai đoạn 5).

**Đối chiếu bằng bộ hiển thị Markdown thật** (chạy tạm trong thư mục nháp, không thêm vào dự án; có mạng):
- `markdown-it-py` 4.2.0 (chuẩn CommonMark), qua `uv run --with markdown-it-py`.
- `micromark` 4 + `micromark-extension-gfm` 3 (Node 22) — cùng họ bộ đọc mà Streamlit dùng (react-markdown + remark-gfm).
- Đếm thẻ `<a>`/`<img>` mà chữ hiện ra khác địa chỉ (bỏ qua địa chỉ viết trần — đã chấp nhận từ T-004).

| Bộ thử | Số mẫu | Còn link |
|---|---|---|
| 52 kiểu tấn công viết tay → `clean_ai_text`, `clean_ai_line`, và lồng vào 6 khung hiển thị của `write.py` (`> {}`, `- {}`, `## {}`, `**Gợi ý:** {}`, `:gray[{}]`, `**{}**`) | 416 | 0 |
| Chuỗi ngẫu nhiên 1–22 mảnh (`[ ] ( ) \ : \n \r ! \` < > ^ \|`, NBSP, tab, `&#93;`, `1.`, `-`, `*`, `#`…) → `clean_ai_text` / `clean_ai_line` / `apply_flag` / `escape(unescape(…))` | 175 000 | 0 |
| Đoạn con ngẫu nhiên của chữ đã lọc, hiển thị dạng `> {đoạn}` | 15 000 | 0 (ngẫu nhiên không trúng; mẫu viết tay R4-1 thì có link ở **cả hai** bộ đọc) |
| Kiểm tra bộ dò: chữ chưa lọc `[a](https://evil.example)` | 1 | 1 (bộ dò hoạt động) |

Tốc độ: `escape_link_syntax` + `unescape_link_syntax` trên chuỗi 200–300 KB (toàn `](`, `[\n`, `\\](`, `[` lồng) ≤ 0,17 giây; `clean_ai_text` ≤ 0,16 giây.

## Kết luận từng phiếu

| Phiếu | Kết luận | Lý do |
|---|---|---|
| T-008 lần 3 | **Đạt** cho phần lọc; R4-1 (Trung bình) là chỗ hiển thị trong `write.py` | Mọi kiểu đã thử qua `clean_ai_text` / `clean_ai_line` / `apply_flag` đều không còn link: nội dòng, ảnh, tham chiếu đầy đủ/rút gọn/trơn, khai báo trong `>`/danh sách/thụt lề/lồng nhiều tầng, nhãn nhiều dòng, chú thích `[^1]:`, `\r\n` và `\r`, `\\]` escape sẵn, ngoặc lồng, code span, NBSP/ZWSP/BOM/U+0085/U+2028 sau `]`, ngoặc Unicode `］（`, thực thể `&#93;`, chuỗi 5 000 tầng. R3-1 … R3-7 đều đã qua. |
| T-012 | **Đạt** | `escape(unescape(t)) == t` với mọi chữ đã lọc (52 mẫu tấn công + 4 000 chuỗi ngẫu nhiên); ô sửa không hiện `\`; người dùng gõ link vào ô thì lưu xong không còn là link; chữ AI viết sẵn `[a]\(…)` hiện trong ô thành `[a](…)` nhưng lưu lại vẫn escape. Không mở đường tạo link. |

## Lỗi tìm thấy

### R4-1 · Trung bình · Câu AI chỉ ra hiện bằng `> {câu}` vẫn tạo được link
- **Vị trí:** `app/views/write.py:506` (`st.markdown(f"> {sentence}")`); gốc ở `seo_app/content/workflow.py:135-151` (`clean_flags` nhận mọi **đoạn con** của bài làm "câu").
- **Tái hiện:** AI viết bài có dòng `Gọi ngay [thợ]: https://evil.example` rồi dòng sau `[thợ] nhé.`. Trong bài, `[thợ]:` nằm giữa dòng nên không phải khai báo link, không bị escape (đúng). Lượt rà soát, AI "chỉ ra" câu `[thợ]: https://evil.example\n[thợ] nhé.` (là đoạn con của bài nên được nhận). Trang hiện `> [thợ]: https://evil.example\n[thợ] nhé.`: `[thợ]:` nay đứng đầu dòng → khai báo link, `[thợ]` thành link tới evil.example.
- **Mong đợi:** khung "Cần xem lại" không có link. **Thực tế:** có link ở cả markdown-it-py và micromark+GFM.
- **Test:** `test_r4_1_flag_sentence_shown_in_review_has_no_link` (AppTest, xfail strict); `test_r4_1_flag_sentence_is_a_substring_of_safe_body` (qua, khẳng định đường đi).
- **Gợi ý sửa:** ở `write.py:506` hiển thị `escape_link_syntax(sentence)` (vì `> ` đưa câu về đầu dòng), giữ nguyên `sentence` gốc khi gọi `apply_fix`/`ignore_fix` để còn khớp với bài. Hoặc dùng chung một hàm "hiện chữ AI ở đầu dòng".

### R4-2 · Thấp · `escape_link_syntax` không tự hiểu `\r`
- **Vị trí:** `seo_app/sanitize.py:210-257` (chỉ `\n` là xuống dòng); được gọi trực tiếp ở `app/views/write.py:208` (`save_manual`) và `seo_app/content/workflow.py:157-159` (`apply_flag`).
- **Tái hiện:** `escape_link_syntax("a\r\r[a]: https://evil.example\r\r[a]")` trả nguyên văn → hai bộ đọc đều ra link. Docstring của hàm lại nói "xuống dòng `\r` cũng không lọt".
- **Mức Thấp vì:** mọi chữ AI đã qua `clean_ai_text` (đổi `\r` trước); ô sửa trên trình duyệt gửi `\n`. Chỉ là phòng thủ nhiều lớp.
- **Gợi ý:** chuyển bước đổi `\r\n`/`\r` → `\n` vào chính `escape_link_syntax`.
- **Test:** `test_r4_2_escape_handles_lone_carriage_return` (2 mẫu, xfail strict).

### R4-3 · Thấp · Dấu `\` hiện ra trong đoạn `code`
- **Vị trí:** `seo_app/sanitize.py:210-257`. Trong `` `…` `` Markdown không hiểu escape, nên `` `x][y` `` hiện thành `` `x]\[y` ``. (Có từ trước: `strip_markdown_links` cũng cắt link trong code: `` `arr]](x)` `` → `` `arr]` ``.)
- **Gợi ý:** bỏ qua đoạn code khi escape/bỏ link (trong code không thể có link). Ít gặp với bài tiếng Việt.
- **Test:** `test_r4_3_code_span_is_not_escaped` (2 mẫu, xfail strict).

### R4-4 · Thấp · `[chữ](chữ có dấu cách)` không phải link vẫn bị cắt phần ngoặc
- **Vị trí:** `seo_app/sanitize.py:158-207` (`strip_markdown_links`). R3-4 chỉ sửa riêng cho `[cần bổ sung: …]`.
- **Tái hiện:** `Khách hỏi: «Cửa kêu [rè rè](sau mưa) là sao?»` → `Khách hỏi: «Cửa kêu rè rè là sao?»`. Theo CommonMark đây không phải link (địa chỉ có dấu cách).
- **Gợi ý:** nay bước escape đã là chốt an toàn, `strip_markdown_links` chỉ nên bỏ những gì CommonMark thật sự coi là link (địa chỉ không có dấu cách, hoặc nằm trong `<…>`).
- **Test:** `test_r4_4_bracket_then_parenthesis_with_spaces_keeps_text` (2 mẫu, xfail strict).

## Đối chiếu tiêu chí xong

- [x] Không cách nào qua `clean_ai_text` / `clean_ai_line` / `apply_flag` còn tạo được link (`test_clean_ai_text_leaves_no_link`, `test_clean_ai_line_leaves_no_link`, `test_apply_flag_cannot_join_a_link`, `test_unescape_then_escape_is_identity_on_random_attack_text`; đối chiếu bộ đọc thật ở trên)
- [x] Chữ đã lọc ghép vào các khung hiển thị của `write.py` không ra link (`test_cleaned_text_inside_display_templates_leaves_no_link`)
- [ ] Câu AI chỉ ra (`flag.sentence`) hiển thị không ra link (R4-1)
- [x] Ô sửa → lưu: round-trip đúng, không mở đường tạo link (`test_edit_box_round_trip_keeps_text_and_stays_safe`, `test_whatever_user_types_is_saved_without_link`)
- [x] Chữ thường không hỏng: chỉ thêm `\` vô hình sau `]` (`test_normal_text_only_gains_invisible_backslashes`, test round 3 đã sửa); trừ R4-3, R4-4

## Rủi ro và điểm cần chú ý

- **Giai đoạn 5 (gửi WordPress):** thân bài nay chứa `]\(`, `]\[`, `]\:`. Bộ chuyển Markdown → HTML phải hiểu escape của CommonMark, nếu không dấu `\` sẽ hiện trên website.
- **Rà soát của AI:** bài gửi lại cho AI có các dấu `\`. Khi AI chép câu để chỉ lỗi mà bỏ `\`, `clean_flags` sẽ loại câu đó (không khớp bài) — chỉ làm giảm số gợi ý ở câu có `](`, `][`, `[x]:`, không ảnh hưởng an toàn.
- Địa chỉ viết trần (`https://…`, `www.…`) vẫn thành link thấy được (đã chấp nhận từ T-004, không đổi).
- Bộ đọc thật chỉ chạy tạm trong máy kiểm thử; test trong repo dùng thước đo `escape_link_syntax(out) == out` (không cần thư viện mới).

## Đề xuất

- Giao R4-1 cho Họa Sĩ (sửa `write.py:506`), làm cùng một hàm hiển thị chung cho mọi chữ AI ghép vào Markdown.
- Giao R4-2, R4-4 (và R4-3 nếu muốn) cho Thợ Máy; đều nhỏ.

## Câu hỏi cho chủ dự án

Không có.

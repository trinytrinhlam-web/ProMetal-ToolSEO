# Báo cáo T-031 · Địa chỉ trần và email trong chữ AI không thành link bấm được

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-031](../tickets/T-031-dia-chi-tran-thanh-link.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trước đây, nếu AI viết `https://…`, `www.…` hay một email vào bài, trang Soạn bài và trang Thử mù hiện nó thành link bấm được. Nay app chèn một ký tự **vô hình** vào giữa địa chỉ (giữa hai dấu `/`, trước dấu `.` của `www.`, trước `@`). Người đọc vẫn thấy nguyên địa chỉ, nhưng không bấm được. Ô «Sửa trực tiếp» không hiện ký tự này, nên chép từ ô sửa ra là địa chỉ sạch. Khi làm việc này tôi tìm ra thêm một lỗi có từ trước: tên bài đối thủ có chứa địa chỉ cũng thành link. Lỗi đó đã sửa luôn, Chỉ Huy B đã đồng ý.

## Cách làm

- **Bộ hiển thị thật của Streamlit 1.65** là remark-gfm. Tôi đã đọc file `streamlit/static/static/js/StreamlitMarkdown.*.js`: link tự động được nhận ở hai nơi. (1) micromark (`www.`, `http(s)://`, email, `mailto:`, `xmpp:`). (2) Một bước tìm bằng biểu thức chính quy trên chữ **đã giải mã**: `/(https?:\/\/|www(?=\.))…/gi` và `/([-.\w+]+)@…/gu`. Vì vậy `www\.evil.com`, `https\://evil.com`, `a&#64;evil.com` vẫn thành link. Escape bằng `\` **không** đủ (đã chạy thật).
- `seo_app/sanitize.py`:
  - `break_autolinks(text)`: dựng "chữ đã giải mã" (`\x` và `&…;` hợp lệ theo CommonMark, kèm vị trí gốc), tìm 3 chỗ cần ngắt rồi chèn `AUTOLINK_BREAK` (U+200B, ký tự rộng 0) vào **vị trí gốc**, giữa hai phần (không cắt ngang `\.` hay `&#46;`):
    - `://` thành `:/` + ngắt + `/`. Áp cho mọi giao thức, không riêng http(s).
    - `www.` thành `www` + ngắt + `.`. Chỉ không phân biệt hoa thường ASCII, không dùng `re.IGNORECASE`, vì dùng thì `K` (Kelvin) và `ſ` cũng khớp.
    - Ngắt trước `@` khi ký tự đứng trước có thể thuộc tên email (`[-A-Za-z0-9_.+;:&=$,"]`, đủ cả tập của GFM lẫn linkify).
  - `unbreak_autolinks(text)`: chỉ bỏ ký tự ngắt nằm **đúng** ba chỗ trên. Ký tự rộng 0 ở chỗ khác, hoặc viết bằng mã `&#8203;`, được giữ nguyên.
  - `escape_link_syntax` gọi `break_autolinks` ở cuối. Đây đã là "bước quyết định an toàn" trên mọi đường hiện chữ: `clean_ai_text`, `clean_ai_line`, `apply_flag` (cả chỗ nối), ô sửa khi lưu, bản nháp nạp lại, `quote_ai_text`. `unescape_link_syntax` gọi `unbreak_autolinks` ở đầu, nên ô sửa không hiện ký tự lạ. Vẫn bảo đảm `escape(unescape(t)) == t`.
  - Ký tự ngắt chỉ đứng trước `/`, `.` hoặc `@`, không bao giờ đứng sau `]`. Vì vậy phần escape link Markdown (T-004 → T-015) không đổi và không phụ thuộc vào nó.
  - Tuyến tính: một lượt dựng chữ giải mã, một lượt biểu thức chính quy (lookbehind độ dài cố định). Có test tốc độ bằng `tests/timing.py`.
- **Mở rộng phạm vi (Chỉ Huy B duyệt 2026-10-16):**
  - `seo_app/content/workflow.py::clean_flags`: so câu AI chỉ ra bằng `break_autolinks(câu)`. Bài đã có ký tự ngắt mà AI chép câu thường thiếu nó; không sửa thì gợi ý văn phong cho câu có địa chỉ bị bỏ mất.
  - `seo_app/text.py::escape_markdown` (dùng trong `markdown_link`): thêm `break_autolinks`. Đây là **lỗi bảo mật có từ trước**, xem mục Rủi ro.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/sanitize.py` | `AUTOLINK_BREAK`, `break_autolinks`, `unbreak_autolinks`; gọi trong `escape_link_syntax`/`unescape_link_syntax`; docstring |
| `seo_app/content/workflow.py` | `clean_flags` so câu sau khi ngắt địa chỉ (1 dòng + chú thích) |
| `seo_app/text.py` | `escape_markdown` ngắt địa chỉ trần (sửa lỗi có sẵn của `markdown_link`) |
| `tests/test_sanitize_autolink.py` | Test mới: 90 ca (xem dưới) |
| `tests/test_edit_unescape.py`, `tests/test_link_escape.py`, `tests/test_soi_loi_round4.py` | Sửa chuỗi mong đợi (xem mục "Test cũ đã sửa") |

## Test cũ đã sửa (Chỉ Huy B cho phép, không nới kiểm tra bảo mật)

| Test | Vì sao đổi | Kiểm bảo mật |
|---|---|---|
| `test_edit_unescape.py::test_unescape_is_inverse_of_escape` (2 cặp có `https://`) | Chuỗi escape nay có `https:/\u200b/` | Giữ nguyên 3 khẳng định; `unescape` vẫn ra đúng chữ gốc |
| `test_edit_unescape.py::test_manual_edit_box_hides_backslash_and_save_escapes_again` | Chuỗi lưu nay có ký tự ngắt | Giữ cũ, **thêm** `gfm_autolinks(saved) == []` |
| `test_edit_unescape.py::test_flagged_sentence_is_quoted_line_by_line_without_link` | Câu trích hiện địa chỉ có ký tự ngắt (`EVIL_SHOWN`) | Giữ cũ, **thêm** `gfm_autolinks(value) == []` cho mọi dòng trích |
| `test_edit_unescape.py::test_apply_and_ignore_still_use_original_sentence` | Câu trích và câu lưu vào `ignored_flags` là câu đã ngắt | Giữ nguyên các kiểm Áp dụng / Bỏ qua |
| `test_link_escape.py::test_escape_only_adds_backslashes` | Hàm nay thêm `\` **và** ký tự ngắt | So sau khi bỏ cả hai; chuỗi mong đợi đầy đủ |
| `test_link_escape.py::test_code_spans_keep_text_but_stay_escaped` (ca `<b>`) | Chuỗi mong đợi có ký tự ngắt | Như cũ |
| `test_soi_loi_round4.py::test_r4_1_flag_sentence_is_a_substring_of_safe_body` | Câu được nhận là `break_autolinks(câu)` | Giữ `no_link_left(body)` |

`test_soi_loi_t021_t017.py::test_poison_is_disabled_in_every_ai_field` **không sửa**. Test này đỏ là vì bắt được lỗi có sẵn ở `markdown_link`; sửa code xong thì xanh lại.

## Bằng chứng

```
$ uv run pytest
3434 passed, 4 skipped, 13 xfailed, 1 warning in 157.95s (0:02:37)

$ uv run ruff check .
All checks passed!
```

**Kiểm bằng remark-gfm thật** (`unified` + `remark-parse` + `remark-gfm`, micromark-extension-gfm-autolink-literal 2.1.0, cùng cách Streamlit dùng). Cài tạm bằng npm trong scratchpad, **không** thêm vào dự án.
- 61 mẫu viết tay (đủ các dạng ở yêu cầu 3, dạng `\`, dạng mã `&…;`, danh sách, trích dẫn, bảng, tiêu đề, đậm/nghiêng, Unicode, punycode, `mailto:`, `xmpp:`). Thêm 20 000 chuỗi ngẫu nhiên, mỗi chuỗi chạy qua 4 đường: `clean_ai_text`, `clean_ai_line`, `escape_link_syntax` thô, và round-trip ô sửa. Thêm 20 000 lần `apply_flag` có chỗ nối. Tổng 120 150 ca.
  - **0 link** trên mọi đường thật (`clean_ai_text`, `clean_ai_line`, round-trip, `apply_flag`).
  - Còn 12 ca, đều là `escape_link_syntax` gọi trên chuỗi **thô chưa bỏ thẻ** có dạng `<https:…>`. Đây là autolink CommonMark có dấu `< >`, `strip_tags` trong `clean_ai_text` đã bỏ từ trước (T-015), không phải dạng địa chỉ trần. Kể cả khi đó, đích link cũng hỏng (`https:/%E2%80%8B/…`).
- `markdown_link` / `escape_markdown`: 15 mẫu, 0 link. Trên `main` cũ (7d8f6f3), `markdown_link("[bấm](https://evil.example/x)", "")` ra link `https://evil.example/x`; `www.evil.example` và `a@evil.example` cũng thành link.

**Kiểm bằng markdown-it-py + linkify-it-py** (`uv run --with`, không thêm vào dự án), chế độ `gfm-like`:
- `fuzzy_link`/`fuzzy_email` **tắt**: chỉ còn link `//evil.com` (giao thức tương đối, riêng linkify mới có, GFM không có) và 12 ca `<…>` thô nói trên.
- `fuzzy` **bật**: còn nhiều link. linkify-it tự nhận **tên miền trần** (`evil.com`) và coi U+200B là "chữ cái". Streamlit **không** dùng linkify-it, cũng không nhận tên miền trần (đã chạy remark-gfm: `evil.com` không thành link). Vì vậy đây không phải lỗi trên app. Nếu muốn chặn cả dạng này thì phải chèn dấu câu nhìn thấy được vào mọi tên miền; tôi không làm.

**Test mới** `tests/test_sanitize_autolink.py` (90 ca). `gfm_autolinks` chép hai biểu thức của remark-gfm, bỏ bớt điều kiện nên bắt rộng hơn bản thật, chạy trên chữ đã giải mã theo CommonMark. Gồm:
- 32 dạng ở yêu cầu 3 × 3 đường (`clean_ai_text`, `clean_ai_line`, `escape_link_syntax`): không link, chữ người đọc thấy giữ nguyên.
- Chữ thường có dấu chấm, `@`, `:`, `/` không bị đổi (`TP.HCM`, `1.500.000`, `v.v.`, `@suachuacuasat`, `8:30/17:30`, `C:\…`).
- Vị trí chèn chính xác. Không cắt ngang `\.`, `&#46;`. Không dùng gập hoa thường Unicode.
- Idempotent, round-trip ô sửa (không còn ký tự ngắt trong ô), `unbreak` chỉ bỏ ký tự ngắt do mình chèn.
- Fuzz 4 000 chuỗi. Không mã HTML nào sinh nhiều ký tự mà giấu được chỗ ngắt.
- Tốc độ tuyến tính, 6 mẫu × 2 hàm.
- Gợi ý văn phong cho câu có địa chỉ vẫn được nhận và Áp dụng / bỏ câu được. Chỗ nối `apply_flag` (`www` + `.evil…`, `a` + `@…`, `https:` + `//…`). Tên bài đối thủ qua `markdown_link`.

## Đối chiếu tiêu chí xong

- [x] Không còn link bấm được với mọi dạng ở yêu cầu 3, có test (`test_bare_addresses_are_not_links_but_still_readable`; remark-gfm thật: 0 link trên đường thật)
- [x] Không làm hỏng chữ thường và round-trip ô sửa (`test_ordinary_text_is_unchanged`, `test_idempotent_and_edit_box_round_trip`, `test_edit_unescape.py`)
- [x] `uv run pytest` và `uv run ruff check .` sạch trên Linux (Windows: chưa chạy được trên cloud)
- [x] Báo cáo nộp

## Rủi ro và điểm cần chú ý

- **Lỗi bảo mật có từ trước, đã sửa:** `seo_app/text.py::markdown_link`. Khi địa chỉ bài đối thủ không hợp lệ (`_clean_url` trả `""`), hàm trả về tên bài chỉ escape Markdown. GFM giải mã `\:` rồi mới tìm địa chỉ, nên `https\://evil.example/x` vẫn thành link. Tên bài đối thủ lấy từ trang web lạ (nguồn prompt injection). Đã chạy thật bằng remark-gfm trên `main` cũ (xem Bằng chứng). Nay sửa ở `escape_markdown`, nên mọi chỗ dùng hàm này đều được che, kể cả nhãn nằm trong link hợp lệ (ở đó ký tự ngắt vô hại).
- **Người dùng chép chữ từ màn hình (vùng xem bài) thì có dính ký tự rộng 0.** Trình duyệt chép cả U+200B, nên dán địa chỉ đó vào thanh địa chỉ có thể hỏng. Chép từ ô «Sửa trực tiếp» thì sạch, vì `unescape_link_syntax` đã gỡ.
- Câu AI chỉ ra (`flag.sentence`) nay được lưu ở dạng đã ngắt, kể cả trong `ignored_flags`. Bản nháp lưu **trước** T-031 có câu đã «Bỏ qua» chứa địa chỉ: gợi ý đó có thể hiện lại một lần. Việc này vô hại.
- Chữ AI gửi lại cho AI (rà soát, viết lại từng phần) nay có U+200B trong địa chỉ. AI có thể chép hoặc bỏ nó, và `clean_flags` đã chịu được cả hai.
- Còn lại, ngoài GFM: `//evil.com` và tên miền trần chỉ thành link với linkify-it (không phải Streamlit).

## Việc cho Giai đoạn 5

- **Trước khi chuyển bài Markdown sang HTML gửi WordPress, phải gỡ ký tự ngắt** (`unbreak_autolinks`, hoặc gọi `unescape_link_syntax` nếu bỏ luôn dấu `\` thêm vào). Không gỡ thì bài trên web chứa U+200B trong địa chỉ: chép ra hỏng, và tìm kiếm cũng không khớp đúng chữ. Sau khi gỡ, bộ chuyển Markdown → HTML phải **tắt autolink** (hoặc màn hình xác nhận liệt kê mọi `href`, như `board.md` đã ghi), vì lúc đó địa chỉ trần lại liền mạch.
- Tiêu đề bài, tiêu đề mục, meta lấy từ chữ đã lọc cũng có thể chứa U+200B, nên gỡ trước khi gửi. Slug thì `slugify` đã bỏ ký tự lạ.

## Đề xuất

- Soi Lỗi và Lá Chắn nên chú ý:
  1. Các dạng giải mã lạ (`&…;` không dấu `;`, mã số quá lớn, `\` trước ký tự không phải dấu câu).
  2. Hai bước lồng nhau `strip_tags` → `escape`.
  3. Chỗ nối `apply_flag`.
  4. Phần chữ hiện bằng `st.markdown` mà **không** đi qua `escape_link_syntax` hay `escape_markdown`. Tôi chưa rà hết `app/**` vì ngoài phạm vi. Ví dụ: chữ báo lỗi, tên mô hình người dùng gõ.
- Script kiểm bằng remark-gfm (node) có thể đưa vào `scripts/` cho các phiếu sau (không phải thư viện Python). Chỉ Huy quyết.

## Câu hỏi cho chủ dự án

Không có.

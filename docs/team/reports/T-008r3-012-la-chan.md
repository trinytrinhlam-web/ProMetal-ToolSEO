# Biên bản bảo mật T-008 (làm lại lần 2) + T-012 · Escape cú pháp link thay vì nhận diện link; ô sửa không hiện dấu `\`

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Fable 5.1 |
| Phiếu được kiểm | [T-008](../tickets/T-008-gia-co-bo-loc.md) mục "Làm lại lần 2" (Thợ Máy) · [T-012](../tickets/T-012-an-dau-escape-o-o-sua.md) (Họa Sĩ) |
| Phạm vi | Thay đổi **chưa commit** so với `HEAD` = `2f53463` (nhánh `main`): `seo_app/sanitize.py` (+128/−?), `seo_app/ai/base.py`, `seo_app/content/{prompts,rules,workflow}.py`, `app/views/write.py` (T-012); test của Thợ Máy `tests/test_link_escape.py` (mới), `tests/test_sanitize.py`, `tests/test_sanitize_hardening.py`, gỡ `xfail` trong `tests/test_soi_loi_round3.py`; test của Họa Sĩ `tests/test_edit_unescape.py` (mới). Kiểm lại Lá Chắn #1–#5 ([biên bản trước](T-008r-010-011-la-chan.md)) và Soi Lỗi R3-1…R3-7 ([báo cáo Soi Lỗi](T-008r-010-011-soi-loi.md)). |
| Ngày | 2026-10-14 |
| **Kết luận** | **T-008 làm lại lần 2: ĐẠT** (3 lỗi Thấp ghi sổ) · **T-012: ĐẠT**. **Giai đoạn 2 phần 1 đã đủ điều kiện bảo mật để đóng.** |

> Ghi chú môi trường: Soi Lỗi đang thêm/sửa test song song; phần họ đổi trong `tests/test_soi_loi_round3.py` (đổi kỳ vọng của `test_normal_vietnamese_with_brackets_is_untouched` theo quyết định của Chỉ Huy) **không** thuộc biên bản này, chỉ ghi nhận là lúc tôi chạy thì toàn bộ test xanh. Lịch sử git không đổi (HEAD vẫn `2f53463`). `uv.lock`, `pyproject.toml`, `.env.example`, `.gitignore`, `.streamlit/config.toml`, `app/main.py`, `seo_app/auth.py`, `seo_app/wordpress/` không đổi (`git diff HEAD --stat` trống).

## Tóm tắt (cho chủ dự án)

Ba vòng trước, bộ lọc cố *nhận ra* link để xóa, và lần nào tôi hoặc Soi Lỗi cũng tìm được một kiểu viết link lạ mà nó không nhận ra. Lần này Thợ Máy đổi hẳn cách làm: không cần nhận ra link nữa, mà chèn một dấu `\` vào đúng chỗ nối bắt buộc của **mọi** kiểu link Markdown (`](`, `][`, `]:` đầu dòng). Dấu `\` này không hiện ra màn hình, chữ vẫn y nguyên, nhưng Markdown không còn coi đó là link. Tôi đã kiểm chứng bằng một bộ dựng Markdown chuẩn (CommonMark và GFM, chạy tạm, không thêm vào dự án): 59 mẫu tấn công có chủ đích (gồm mọi mẫu từng lọt ở ba vòng trước) và 30 000 chuỗi ngẫu nhiên đều **không còn link ẩn nào**; chạy lại không đổi gì; chữ 475 KB lọc trong 0,13 giây. Cả hai lỗi tôi nêu lần trước và bảy lỗi của Soi Lỗi đều đã đóng đúng.

Phần T-012 (Họa Sĩ) chỉ làm cho các ô sửa chữ không hiện dấu `\` lạ, và khi bấm Lưu hoặc Duyệt dàn ý thì dấu `\` được chèn lại; tôi thử 30 000 chuỗi ngẫu nhiên, vòng "bỏ `\` rồi chèn lại" luôn ra đúng bản đã bảo vệ.

Còn ba điểm nhỏ (mức Thấp, không khai thác được hôm nay) ghi vào sổ rủi ro để làm ở Giai đoạn 5 khi xuất bài lên WordPress. **Giai đoạn 2 phần 1 đủ điều kiện bảo mật để đóng.**

## Kết luận riêng từng phiếu

| Phiếu | Kết luận | Lý do |
|---|---|---|
| **T-008 làm lại lần 2** (Thợ Máy) | **ĐẠT** | Cách mới (`escape_link_syntax`, `sanitize.py:210-257`) thật sự không phụ thuộc việc nhận diện link (phân tích ở mục dưới). Đóng đúng Lá Chắn #1, #2, #3, #4, #5 và Soi Lỗi R3-1…R3-7 (bảng xác minh). Kiểm chứng bằng CommonMark thật: 0 link ẩn. 3 lỗi Thấp (#1–#3) ghi sổ. |
| **T-012** (Họa Sĩ) | **ĐẠT** | `unescape_link_syntax` (`sanitize.py:260-305`) chỉ **bỏ** đúng dấu `\` do hàm escape thêm, không tạo thẻ/link; mọi chỗ đưa chữ vào ô sửa đều escape lại khi lưu (`write.py:104`, `:111`, `:208`); ô sửa là `st.text_input`/`st.text_area` (không dựng Markdown), và không có chỗ nào hiển thị `S.outline_title`/`S["h-…"]` (bản chưa escape) bằng `st.markdown` (grep `write.py`: chỉ `:349`, `:356` là ô nhập). Bất biến `escape(unescape(t)) == t` giữ đúng trên 30 000 chuỗi ngẫu nhiên. |

## Đánh giá cách làm mới: có thật sự không còn phụ thuộc nhận diện link?

**Có.** Lập luận và kiểm chứng:

1. **Theo đặc tả CommonMark/GFM**, mọi cấu trúc link/ảnh đều cần một dấu `]` không escape đứng **sát ngay** trước `(` (link/ảnh nội dòng), `[` (tham chiếu đầy đủ/rút gọn) hoặc `:` (dòng khai báo, và dòng khai báo chỉ có ở đầu khối: sau thụt lề, `>`, `-`/`*`/`+`, `1.`/`1)`). Link kiểu `[nhãn]` trơn chỉ có tác dụng khi có dòng khai báo. Thực thể HTML (`&#40;`) không tạo được cấu trúc. Hàm chỉ **thêm** `\` sau `]` ở ba chỗ đó (`sanitize.py:241-246`), không xóa hay đổi ký tự nào, nên không thể ghép ra thẻ hay link mới; sau khi thêm, `\(`, `\[`, `\:` là ký tự thường. Vì không cần đoán đâu là link, các dạng từng lọt (tiêu đề có escape, `\r`, NBSP, lồng 4 tầng, bước dự phòng ghép link) không còn ý nghĩa.
2. **Bước 1 chuẩn hóa `\r\n`/`\r` → `\n`** (`:317`) nên "đầu dòng" được hiểu đúng với mọi kiểu xuống dòng CommonMark công nhận.
3. **Vòng "bỏ thẻ → bỏ link" cũ chỉ còn để chữ gọn** (`:318-324`); `_LINK_JOIN` (nguồn R3-1) đã bỏ. Bước escape chạy **sau cùng** (`:325`) trên mọi đầu ra, kể cả khi vòng lặp hết lượt.
4. **Còn lại đúng hai cách cho địa chỉ lạ hiện ra, cả hai đều hiện trần, người dùng nhìn thấy địa chỉ:** autolink `<https://…>` bị `strip_tags` bỏ như thẻ (`_TAG` `:39`), và địa chỉ viết trần (`https://…`) được GFM tự biến thành link, chữ hiện ra chính là địa chỉ (rủi ro đã chấp nhận từ T-003…009, xem thêm lỗi #3).
5. **Kiểm chứng bằng bộ dựng thật** (`markdown-it-py` chế độ `commonmark` và `gfm-like` + `linkify-it-py`, chạy qua `uv run --with …`, script trong scratchpad, không sửa repo):
   - 59 mẫu tấn công × 2 hàm (`clean_ai_text`, `clean_ai_line`) × 2 bộ dựng: **0 link ẩn, 0 ảnh**. Gồm: mọi mẫu Lá Chắn #1/#2 (tiêu đề `"a\"b"`, `'it\'s'`, `(a\)b)`, `\r\n`, `\r`), R3-1 (lồng đúng 4 tầng, `\\]`), R3-2 (6 dạng), lồng 10 và 50 tầng, khai báo trong trích dẫn lồng/danh sách `-`/`*`/`1.`/`1)`/thụt 3 dấu cách/tab, nhãn nhiều dòng, địa chỉ và tiêu đề ở dòng sau, nhãn có `\[`, nhiều khai báo liền, khai báo sau tiêu đề/trích dẫn, tham chiếu rút gọn và trơn (so nhãn không phân biệt hoa thường), `![…]`, ảnh lồng link, nhãn có code/HTML, `<https://…>`, `<a href>`/`<A HREF>`, `<[](x)a href=…>`, `&#40;`, `\\(`, link trong tiêu đề `##`/bảng/danh sách/in đậm/qua nhiều dòng/setext, `[cần bổ sung: …](…)` (cả lồng).
   - 6 mẫu `apply_flag` ghép câu thành link: 0 lọt.
   - 30 000 chuỗi ngẫu nhiên (bảng chữ gồm `[ ] ( ) : \ \n \r \t > * 1 . ! < # " ' / = NBSP ZWSP &#40; &#93;`, địa chỉ `evil.example`, cụm `cần bổ sung:`): đường AI (`clean_ai_text`, và `escape(unescape(clean_ai_text))` mô phỏng mở ô sửa rồi lưu) **0 link ẩn**; `escape_link_syntax` idempotent 30 000/30 000; vòng `escape(unescape(escape(s))) == escape(s)` 30 000/30 000.
   - Tốc độ: 200 KB toàn `[`, 340 KB khai báo link, 475 KB trộn, 300 KB toàn `\`, 370 KB `\r\n`: `clean_ai_text` ≤ 0,14 s, `unescape_link_syntax` ≤ 0,03 s (tuyến tính).

## Xác minh các lỗi còn mở từ vòng trước

| Lỗi cũ | Mức | Đã làm | Bằng chứng |
|---|---|---|---|
| LC #1 / R3-2 (3 dạng tiêu đề escape) | Cao | **Đóng đúng** | `[Gọi thợ][r]` → `[Gọi thợ]\[r]` (`:243`), dòng khai báo → `[r]\: …` (`:243`, `label_at_line_start`). CommonMark: không còn `<a>`. `_MD_LINK_DEF` (`:102-106`) vẫn giữ nguyên regex cũ nhưng nay chỉ để dọn chữ, không còn là lớp quyết định. |
| LC #2 / R3-2 (`\r\n`, `\r`) | TB | **Đóng đúng** | `:317`. Mẫu `[Gọi thợ][r]\r\n\r\n[r]: …\r\n` và dạng `\r` đơn → CommonMark không còn `<a>`. |
| R3-2 (NBSP trong địa chỉ) | Cao | **Đóng đúng** | Không cần nhận địa chỉ nữa; mẫu `[r]: https://evil.example/a b` → `]\:`. |
| R3-1 (lồng 4 tầng, `\\]`) | Cao | **Đóng đúng** | `_LINK_JOIN` đã bỏ; `[Gọi thợ]][][][][](x)(y)(y)(y)(url)` và dạng `\\]` → mọi `](`/`][` đều thành `]\(`/`]\[`; CommonMark không `<a>`. Lồng 10, 50 tầng cũng vậy. |
| R3-3 (tiêu đề bài/mục, reason, summary) | TB | **Đóng đúng** | `workflow.py:31-37` `clean_ai_line` = `clean_ai_text` + gộp một dòng; dùng ở `:43`, `:46` (`clean_draft`), `:91`, `:94` (`clean_outline`), `:210` (tiêu đề dự phòng); `clean_review` `:108-109`, `:114` dùng `clean_ai_text`. Gộp dòng chạy **sau** escape và chỉ thay khoảng trắng bằng một dấu cách, nên không ghép được `](`/`][`/`]:` (kiểm bằng CommonMark với `clean_ai_line` trên 59 mẫu). Tên bài đối thủ vẫn `strip_tags` + `markdown_link` (escape mọi ký tự Markdown, đã kiểm T-010). |
| R3-4 (`[cần bổ sung: …](…)` mất dấu) | Thấp | **Đóng đúng** | `:109`, `:186-188`: nhãn `cần bổ sung:` không bao giờ bị coi là link; `(` sau đó vẫn escape (`:243`). `find_missing(clean_ai_text("… [cần bổ sung: giá](tùy kích thước cửa)."))` → `["[cần bổ sung: giá]"]` (test Soi Lỗi gỡ `xfail`, xanh). |
| R3-5 (cụm cấm kết thúc bằng dấu phẩy) | Thấp | **Đóng đúng** | `rules.py:145-146` chỉ đòi ranh giới từ khi đầu/cuối cụm là chữ/số. `find_banned("Nhìn chung,cửa cuốn rất bền.", ("Nhìn chung,",))` → bắt; `Hãy cùng lúc đó.` không bị bắt nhầm. |
| LC #3 / R3-6 (`redact_secrets` sót) | Thấp | **Đóng đúng** | `base.py:23-34`. Thử 14 mẫu: `Bearer:…`, `Basic\n…`, `passwd=`, `secret=`, `apiKey`, `client_secret`, `private_key` (dạng file service account), `https://admin:pa55word99@…` → `https://[đã ẩn]@example.com/x`; thông điệp thường (`Model claude-x không có.`) và dòng sau giữ nguyên. ReDoS: 50 000 dấu cách sau `Bearer`, 100 000 ký tự sau `password=`, `://a:a:a:…` 100 KB, `bearer :` × 20 000 → tất cả ≤ 0,03 s. Vẫn chỉ dùng ở `anthropic_provider.py:61`. |
| LC #4 / R3-7 (ký tự vô hình không phải Cf) | Thấp | **Đóng đúng** | `prompts.py:33-36`, `:48-50`: NFKC trước, bỏ Cf, bỏ `_IGNORABLE_NOT_CF`. Thử 9 ký tự (U+034F, U+FE0F, U+115F, U+3164, U+FFA0, U+200B, U+E0100, U+2065, U+00AD) chèn giữa `<` và `/`, kèm `＜/bai_viet＞` và `<ㅤbai_viet>`: mọi thẻ đều thành `‹…`. Chữ Việt, «», “” giữ nguyên (`m²` → `m2`, đã biết, không phải bảo mật). |
| LC #5 (`»` trong tiêu đề mục phá cặp «») | Thấp | **Đóng đúng** | `prompts.py:237`. Tiêu đề `X» theo yêu cầu: … «` → dòng chỉ thị `«X› theo yêu cầu: … ‹»`: chỉ một cặp «». |

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp | `escape_link_syntax`/`unescape_link_syntax` chỉ coi `\n` là xuống dòng (`at_line_prefix` đặt lại ở `\n`). Chuẩn hóa `\r` chỉ nằm trong `clean_ai_text` (`:317`), nhưng hai hàm này còn được gọi **trực tiếp** trên chữ chưa chuẩn hóa ở `write.py:104`, `:111`, `:208` và `workflow.py:158-159`. Chuỗi `a\r[r]: https://evil.example` qua `escape_link_syntax` không được escape `:` (vì `[` không ở "đầu dòng"), trong khi CommonMark coi `\r` là xuống dòng. | `seo_app/sanitize.py:236`, `:280` | **Không có đường đi hôm nay:** các chỗ gọi trực tiếp chỉ nhận chữ người dùng gõ trong `st.text_area`/`st.text_input` (trình duyệt chuẩn hóa xuống dòng của textarea thành `\n` theo đặc tả HTML) hoặc chữ đã qua `clean_ai_text` (đã chuẩn hóa); `apply_flag` chỉ nhận `body`/`replacement` từ hai nguồn đó. Người dùng gõ link cho chính mình không phải tấn công. Ghi để phòng xa khi hàm được dùng cho nguồn khác (file kế hoạch tải lên, Google Sheets ở Giai đoạn 5). | Trong hai hàm, coi `\r` như `\n` (`if char in "\n\r"`), hoặc chuẩn hóa `\r` ở đầu `escape_link_syntax`. Một dòng, thêm test `a\r[r]: url` → `]\:`. Gộp phiếu sửa nhỏ. |
| 2 | Thấp | Đường "người dùng sửa rồi lưu" (`save_manual`, `current_outline`) chỉ escape cú pháp link, **không** `strip_tags`: người dùng gõ `<a href=…>`, `<https://…>` hay `<script>` thì chuỗi đó nằm nguyên trong `texts-`/dàn ý. (Họa Sĩ đã tự ghi nhận.) | `app/views/write.py:104`, `:111`, `:208` | **Không có đường đi hôm nay:** hiển thị qua `ui.highlight` (`write.py:471`) escape `& < >` trước khi `unsafe_allow_html` (`ui.py:64-81`); tiêu đề dàn ý chỉ vào prompt AI (dữ liệu trong khung) và kết quả AI lại qua `clean_*`. Nguồn là chính người dùng. Thành vấn đề thật chỉ khi Giai đoạn 5 chuyển Markdown → HTML gửi WordPress mà quên `sanitize_html` cho phần người dùng gõ. | Ghi vào danh sách "phải làm" Giai đoạn 5: `sanitize_html` áp cho **toàn bộ** HTML cuối (AI + người dùng), không chỉ phần AI. Tùy chọn: `save_manual`/`current_outline` gọi `strip_tags` trước `escape_link_syntax` cho đồng nhất (có thể làm người dùng mất `<` cố ý gõ, nên để Chỉ Huy quyết). |
| 3 | Thấp | Biến thể của rủi ro "địa chỉ hiện trần" đã chấp nhận: GFM tự link địa chỉ trần có phần `user@`, ví dụ `https://suachuacuasat.com@evil.example/`, hiện ra bắt đầu bằng tên miền của mình nhưng bấm vào thì tới `evil.example`. Bộ lọc không đụng tới địa chỉ trần (đúng chủ ý). | `seo_app/sanitize.py:325` (không escape địa chỉ trần); `is_safe_url` `:363-372` cho qua `https://…@…` | Trang đối thủ dụ AI viết địa chỉ trần dạng trên → `st.markdown` (GFM) hiện link, chữ nhìn như tên miền của mình → người dùng bấm nhầm. Hôm nay dừng ở bấm nhầm trong app; Giai đoạn 5 `sanitize_html` cho `https` qua. Toàn bộ địa chỉ (kể cả `@evil.example`) vẫn nhìn thấy, nên chỉ Thấp. | Giai đoạn 5: màn hình xác nhận liệt kê mọi `href` trong HTML cuối (đã ghi ở biên bản trước); thêm vào `is_safe_url` (hoặc bước liệt kê) quy tắc từ chối/đánh dấu địa chỉ có `@` ở phần máy chủ. Ghi sổ rủi ro cùng dòng "địa chỉ hiện trần". |

Ghi nhận thêm (không tính lỗi): `unescape_link_syntax` không phải nghịch đảo đơn ánh (chữ gốc tự có `]\(` sẽ hiện `](` trong ô sửa, lưu lại vẫn ra `]\(`) — Họa Sĩ đã nêu, không ảnh hưởng an toàn vì lưu luôn escape lại. `_MD_LINK_DEF` (`:102-106`) vẫn giữ regex có điểm yếu của vòng trước; nay vô hại vì chỉ để dọn chữ, nhưng nếu sau này ai đó bỏ bước escape thì lỗi cũ quay lại — docstring `clean_ai_text` (`:314-315`) đã ghi rõ bước escape là "bước quyết định an toàn", đủ cảnh báo. Dấu `\` lộ trong prompt gửi AI (viết lại/rà soát) và trong code span: không phải bảo mật.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | **Đạt** | `git diff HEAD` (10 file) + 4 file chưa theo dõi: grep `sk-ant`, `AIza`, `AKIA`, `PRIVATE KEY`, `password="…"` chỉ ra chú thích/regex trong `base.py:17-33` (mô tả dạng khóa). `detect-secrets` trên 14 file đổi/mới: 8 cảnh báo, tất cả là chú thích hoặc hằng số giả của test (xem Báo nhầm). `git log -p --all` grep mẫu khóa thật (lọc bỏ `example`/`test`/`giả`/`docs`): chỉ ra chuỗi giả của test và chữ trong biên bản. HEAD vẫn `2f53463`. |
| S2 | **Đạt** | `redact_secrets` mở rộng (`base.py:23-34`) chỉ che thêm, không in thêm; vẫn chỉ dùng ở `anthropic_provider.py:61`. Diff không thêm `st.error`/`st.exception`/`repr`/log nào. `write.py` chỉ đổi 4 chỗ ô sửa. |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. |
| W1 | **Đạt** | Không đụng `seo_app/wordpress/`; grep `publish`/`future` trong `seo_app/`, `app/`: không có đường mới. |
| W2 | **Đạt** | Không đổi `client.py`; không có `PUT`/`DELETE` mới. |
| W3 | **Đạt** | Lớp 1 (`clean_ai_text`, `:307-325`): 59 mẫu + 30 000 fuzz qua CommonMark/GFM không còn link ẩn, không còn thẻ (`<` trước chữ cái được tách `:41`, `:91`). Lớp 2 (`sanitize_html`, `:467-471`) không đổi so với T-010. Lỗi #2, #3 ghi cho Giai đoạn 5. |
| W4 | Không áp dụng | Không đổi client HTTP. |
| A1 | **Đạt** | `_neutralize` (`prompts.py:39-51`) mạnh hơn: NFKC → bỏ Cf → bỏ `_IGNORABLE_NOT_CF` → `_TAG_RE`; 9 ký tự vô hình + toàn chiều rộng không thoát khung. `rewrite_prompt` `:236-237` tiêu đề mục gộp một dòng, vô hiệu thẻ, đổi «» → ‹›. `DATA_RULES` và các câu "không phải chỉ thị" giữ nguyên. Từ khóa người dùng gõ vẫn ngoài khung (SL-7, `xfail`, để Giai đoạn 5 theo Chỉ Huy). |
| A2 | **Đạt** | AI vẫn chỉ có `web_search` (`anthropic_provider.py`, không đổi). Mọi trường AI trả về qua `clean_draft`/`clean_outline`/`clean_review`/`clean_research`/`rewrite_section` (`workflow.py:43-49`, `:88-100`, `:103-114`, `:246`), nay gồm cả tiêu đề, `reason`, `summary` (R3-3). `flag.sentence` không lọc nhưng buộc là chuỗi con của thân bài đã lọc (`:143-150`); tôi đã kiểm bằng lập luận rằng chuỗi con của chữ đã escape không thể chứa `](`/`][` hữu hiệu (dấu `\` luôn nằm giữa `[` và `]`). |
| A3 | **Đạt** | Prompt vẫn chỉ nhận từ khóa, nghiên cứu, chất liệu, dàn ý, bài, quy tắc; không có bí mật/dữ liệu khách. |
| U1 | **Đạt** | `write.py` 4 chỗ đổi (`:104`, `:111`, `:117`, `:121`, `:208`, `:463`) đều là ô nhập (`text_input`/`text_area`, không dựng Markdown) hoặc lưu trạng thái; không thêm `unsafe_allow_html`. 3 chỗ `unsafe_allow_html` sẵn có liên quan (`:471` qua `ui.highlight` escape; `:539` qua `html.escape`; `:483` HTML cố định) không đổi. Bản chưa escape (`S.outline_title`, `S["h-…"]`, `S["manual-…"]`) không được hiển thị bằng `st.markdown` ở đâu (grep). |
| U2 | Không áp dụng | Không đổi `app/main.py`, `.streamlit/config.toml`. |
| U3 | Không áp dụng | Không đổi `seo_app/auth.py`. |
| F1 | **Đạt** | Diff không có `open(`/`Path(` mới; `tests/test_edit_unescape.py` dùng `tmp_path` + `monkeypatch` như các AppTest sẵn có. |
| F2 | Không áp dụng | Không đụng ảnh/EXIF; GPS giữ nguyên theo sổ rủi ro mục 6. |
| F3 | **Đạt** | Không có `eval`/`exec`/`pickle`/`yaml.load`/`subprocess` trong diff (grep); bandit 0 cảnh báo; `unicodedata.normalize`/regex chỉ đổi dạng chữ. |
| D1 | **Đạt** | `pyproject.toml`, `uv.lock` không đổi. `markdown-it-py`/`linkify-it-py` chỉ chạy qua `uv run --with` tạm, **không** thêm vào dự án. `pip-audit` trên 156 dòng xuất từ `uv.lock`: No known vulnerabilities found. |
| D2 | **Đạt** | `.gitignore` không đổi: vẫn chặn `.env`, `.env.*`, `*service-account*.json`, `secrets/`, `.streamlit/secrets.toml`, `.venv/`, `*.sqlite*` (dòng 2-24). |
| D3 | **Đạt** | `tests/test_link_escape.py`, `tests/test_edit_unescape.py`: không `socket`/`requests`/`httpx`/`urlopen`/`anthropic.Anthropic(`/`openai`/`genai`, không đọc `.env` hay `config/` thật (grep); AppTest dùng `fake_ai.FakeProvider`. Fixture chặn socket + không đọc `.env` thật (`tests/conftest.py:1-40`) không đổi. `uv run pytest`: 847 passed, 1 xfailed. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt --no-hashes` (156 dòng) → `uvx pip-audit -r … --no-deps`: **No known vulnerabilities found** (`seo-app` bỏ qua vì không có trên PyPI, bình thường). `uv.lock` không đổi. | Có |
| bandit | `uvx bandit -q -r` trên 6 file code đổi (`sanitize.py`, `ai/base.py`, `content/{prompts,rules,workflow}.py`, `app/views/write.py`): **0 cảnh báo** ở mọi mức. | Có |
| detect-secrets | `uvx detect-secrets scan` trên 14 file đổi/mới (code, test, báo cáo, phiếu): 8 cảnh báo, đều là chú thích hoặc hằng số giả của test (bên dưới). | Có |
| Soát lịch sử git | HEAD vẫn `2f53463`, không commit mới; `git log -p --all` grep mẫu khóa thật chỉ ra chuỗi giả của test (`sk-ant-api03-KHOA-GIA-…`, `AIzaSyA1234…`) và chữ trong biên bản. Diff chưa commit: sạch. | Có |
| pytest / ruff | `uv run pytest`: **847 passed, 1 xfailed** (27 s; `xfail` còn lại là SL-7). `uv run ruff check .`: **All checks passed**. | Có |
| Kiểm chứng CommonMark thật | `uv run --with markdown-it-py --with linkify-it-py python <script scratchpad>` (không mạng, không sửa repo): 59 mẫu tấn công × 2 hàm × 2 bộ dựng, 6 mẫu `apply_flag`, 30 000 chuỗi ngẫu nhiên × 3 ứng viên × 2 bộ dựng, 5 chuỗi 200–475 KB đo thời gian. Đường AI: **0 link ẩn, 0 ảnh**; idempotent và vòng escape/unescape đúng 100 %. | Có |
| Thử tay `redact_secrets`, `_neutralize`, `rewrite_prompt`, `find_banned` | 14 mẫu che khóa + 4 mẫu ReDoS, 9 ký tự vô hình, 1 tiêu đề mục phá «», 2 câu cụm cấm (kết quả ở bảng xác minh). | Có |

## Báo nhầm đã loại

| Công cụ | Cảnh báo | Lý do loại |
|---|---|---|
| detect-secrets | `seo_app/ai/base.py:22` "Basic Auth Credentials" | Là **chú thích** mô tả dạng `https://admin:matkhau@site…` mà regex che, không phải khóa. |
| detect-secrets | `tests/test_edit_unescape.py:18` `PASSWORD = "mat-khau-thu-123"` | Mật khẩu giả của AppTest, trùng hằng số đã có ở `tests/test_app.py:8`, `tests/test_app_wordpress.py:9` (băm bằng `hash_password` trong test, không có ở `.env`). |
| detect-secrets | `tests/test_link_escape.py:205` `http://wp:abcd%20efgh@site.vn` | Dữ liệu vào của test `redact_secrets`, mẫu đếm được. |
| detect-secrets | `tests/test_soi_loi_round3.py:343-344`, `:361-363` | Hằng số giả của test R3-6 (`AIzaSyA-abcdefghijklmnopqrstu`, `sk-ant-xyz12345678`, `GOCSPX-abcdefghijkl`, `MIIEvQIBADANBg`, `pa55word99`); diff của Thợ Máy chỉ gỡ `xfail`. Không phải khóa thật. |
| Kiểm chứng CommonMark (gfm-like) | 2 880 → 12 → 4 "link" trong fuzz | Toàn bộ là `linkify-it-py` tự link **địa chỉ trần** (`https://evil.example…`, khác nhau chỉ ở punycode/`%5C`) hoặc link "mờ" `//1.cần`, `​.ax` mà GFM thật **không** tự link (GFM chỉ tự link `www.` hoặc có giao thức). Địa chỉ trần là rủi ro đã chấp nhận (xem lỗi #3). 8 trường hợp còn lại nằm ở ứng viên "chữ người dùng gõ, chỉ escape" (autolink `<bxhttps://…>`, `<bb:…>` do người dùng tự gõ, hiển thị đã escape HTML) — ghi ở lỗi #2. |

## Điều kiện

Không có điều kiện chặn. **T-008 làm lại lần 2: ĐẠT. T-012: ĐẠT.**

Ba lỗi Thấp (#1, #2, #3) ghi sổ rủi ro, đề nghị Chỉ Huy:
- #1: gộp vào một phiếu sửa nhỏ **không chặn** (một dòng trong `escape_link_syntax`/`unescape_link_syntax` + 1 test).
- #2, #3: đưa vào danh sách "phải làm" của Giai đoạn 5 (cùng các mục đã ghi ở [biên bản T-003…009](T-003-006-008-009-la-chan.md) và [biên bản trước](T-008r-010-011-la-chan.md)): `sanitize_html` áp cho toàn bộ HTML cuối kể cả phần người dùng gõ; bộ chuyển Markdown → HTML phải là bộ chuẩn (để dấu `\` biến mất đúng) và **không** xử lý khai báo link tham chiếu; màn hình xác nhận liệt kê mọi `href`, đánh dấu địa chỉ có `@` ở phần máy chủ.

**Giai đoạn 2 phần 1: đã đủ điều kiện bảo mật để đóng.** Không còn lỗi Nghiêm trọng/Cao/Trung bình mở trong phạm vi phần 1; mọi lỗi của ba vòng trước (SL-1…SL-14 trừ SL-7 để Giai đoạn 5, R3-1…R3-7, Lá Chắn #1–#5) đã đóng và có test giữ. Khi Soi Lỗi nộp test sửa kỳ vọng, chỉ cần Chỉ Huy xác nhận `uv run pytest` xanh; không cần Lá Chắn kiểm lại trừ khi có sửa code.

# Biên bản bảo mật T-013 + T-014 · Hiện an toàn câu «Cần xem lại»; các lỗi Thấp của bộ escape link

> **Ghi chú model:** lần kiểm định này chạy **tạm bằng Claude Opus 5.5** vì Claude Fable 5.1 (model quy định cho Lá Chắn) đã hết hạn mức. Sẽ có một lần kiểm lại bằng Fable sau; kết luận dưới đây có hiệu lực tới lúc đó.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable 5.1, xem ghi chú) |
| Phiếu được kiểm | [T-013](../tickets/T-013-escape-cau-can-xem-lai.md) (Họa Sĩ) · [T-014](../tickets/T-014-loi-thap-escape.md) (Thợ Máy) |
| Phạm vi | Thay đổi **chưa commit** so với `HEAD` = `17aadbe`: `app/views/write.py` (+14/−1, T-013), `seo_app/sanitize.py` (+130/−?, T-014); báo cáo `T-012-hoa-si.md` mục T-013, `T-014-tho-may.md` (mới); `docs/team/rules.md` (thêm R11). Kiểm lại Soi Lỗi R4-1, R4-2, R4-4 ([báo cáo](T-008r3-012-soi-loi.md)) và Lá Chắn #1 ([biên bản trước](T-008r3-012-la-chan.md)). Test mới của Soi Lỗi (làm song song) **không** thuộc biên bản này. |
| Ngày | 2026-10-14 |
| **Kết luận** | **T-013: ĐẠT** · **T-014: ĐẠT** (1 lỗi Thấp mới, có từ trước, ghi sổ kèm đề nghị phiếu sửa nhỏ) |

> Ghi chú môi trường: tôi không dùng `git stash`/`checkout`/`reset`; chỉ đọc `git diff`, `git show HEAD:…`. `uv.lock`, `pyproject.toml`, `.env.example`, `.gitignore`, `.streamlit/config.toml`, `app/main.py`, `seo_app/auth.py`, `seo_app/wordpress/`, `seo_app/content/` không đổi (`git diff HEAD --stat`).

## Tóm tắt (cho chủ dự án)

Hai bản sửa đều an toàn. Khung «Cần xem lại» không còn biến câu AI chỉ ra thành link nữa: tôi thử lại đúng mẫu của Soi Lỗi bằng bộ dựng Markdown chuẩn, trước khi sửa ra link tới evil.example, sau khi sửa chỉ còn chữ. Bộ escape nay hiểu kiểu xuống dòng `\r`, và chữ thường trong ngoặc như «[rè rè](sau mưa)» được giữ mà không mở đường cho link nào lọt. 30 000 chuỗi ngẫu nhiên cùng 45 mẫu viết tay đều không còn link ẩn.

Khi thử, tôi tìm ra một lỗ nhỏ **có từ trước**, không do hai phiếu này gây ra. Lúc AI tự sửa câu, phần nối có thể ghép lại thành thẻ HTML như `<a href="…">`. Hôm nay lỗ này chưa gây hại vì app luôn hiện thẻ đó thành chữ thường. Nhưng phải sửa trước khi làm phần gửi bài AI lên WordPress (Giai đoạn 5). Tôi đề nghị một phiếu nhỏ, sửa một dòng.

## Kết luận riêng từng phiếu

| Phiếu | Kết luận | Lý do |
|---|---|---|
| **T-013** (Họa Sĩ) | **ĐẠT** | `quote_ai_text` (`app/views/write.py:477-486`) đặt **mọi** dòng của câu vào trích dẫn rồi mới chạy `escape_link_syntax` **trên cả khối đã có `> `**. Vì vậy `[nhãn]:` bị đưa lên đầu dòng cũng được escape thành `]\:`. `apply_fix`/`ignore_fix` vẫn nhận câu gốc (`:518-534`). R4-1 đóng đúng. |
| **T-014** (Thợ Máy) | **ĐẠT** | `\r` được coi là xuống dòng ở cả hai hàm (`seo_app/sanitize.py:356`, `:400`), nên vẫn là nghịch đảo của nhau. R4-2 và LC #1 đóng. Điều kiện R4-4 (`_Whitespace.looks_like_destination`, `:189-205`) và việc bỏ qua đoạn code (`_code_spans`, `:270-325`) chỉ nằm ở `strip_markdown_links`, tức bước làm gọn chữ. Bước quyết định an toàn `escape_link_syntax` không dùng hai cơ chế này và vẫn chạy sau cùng (`:445`). Nhận diện sai vì thế chỉ làm chữ dư, không làm lọt link. R4-3 cố ý không sửa; Chỉ Huy đã chấp nhận đây là lỗi hiển thị. Tôi đồng ý: không sửa là cách an toàn hơn. |

## Xác minh các lỗi được giao

| Lỗi | Mức | Kết quả | Bằng chứng |
|---|---|---|---|
| R4-1 (câu AI trong `> {câu}` thành link) | TB | **Đóng đúng** | Mẫu Soi Lỗi `[thợ]: https://evil.example\n[thợ] nhé.`: cách cũ `> …` thì CommonMark ra `<a href="https://evil.example">thợ</a>`. `quote_ai_text` ra `> [thợ]\: https://evil.example\n> [thợ] nhé.`, CommonMark chỉ còn chữ. Thử thêm 19 mẫu viết tay: khai báo nhiều dòng, nhãn nhiều dòng, thụt lề, `-`, `1)`, `>`, tab, NBSP, `\r`, `\r\n`, `[^1]:`, `[a][b]`, ảnh. Với mỗi mẫu, **mọi đoạn con** (tối đa 80 ký tự) của thân bài đã lọc đều đưa qua `quote_ai_text`: 0 link. 29 413 đoạn con ngẫu nhiên từ fuzz: 0 link. Test `test_r4_1_flag_sentence_shown_in_review_has_no_link` xanh. |
| R4-2 / LC #1 (`\r` đứng riêng) | Thấp | **Đóng đúng** | `escape_link_syntax("a\r\r[a]: https://evil.example\r\r[a]")` ra `…[a]\: …`, CommonMark không còn `<a>`. Fuzz 30 000 chuỗi có `\r`, `\r\n`, đưa thẳng vào `escape_link_syntax` (không qua `clean_ai_text`): 0 link. Idempotent và `escape(unescape(escape(s))) == escape(s)`: 30 000/30 000. |
| R4-4 (`[chữ](chữ có dấu cách)` bị cắt) | Thấp | **Đóng đúng, không mở đường lọt** | `Khách hỏi: «Cửa kêu [rè rè](sau mưa) là sao?»` ra `…[rè rè]\(sau mưa)…`: chữ giữ đủ, `(` đã escape. 26 mẫu nhắm vào điều kiện mới, mỗi mẫu qua cả `clean_ai_text` và `clean_ai_line`: `[a](x y)`, `[a](x "t")`, `[a]( x )`, `[a](<x y>)`, tiêu đề ở dòng sau, NBSP/`\f`/`\v` trong địa chỉ, ngoặc lồng, `[[a](x y)](url)`, `[a](x y)(url)`, ảnh, link trong/ngoài/sát đoạn code, code nhiều dòng, khối ``` ```, code lẫn thẻ HTML. Kết quả: 0 link ở CommonMark, 0 link ẩn ở GFM+linkify. Link thật vẫn bị bỏ địa chỉ: `[a](https://evil.example)`, `[a]( url "t")`, `[a](<url có cách>)`, `[a](url\n'y')` đều ra `a`. Kể cả khi bộ đoán đánh giá sai thì `]\(` vẫn được thêm. |

**Dòng `**Gợi ý:** {replacement}` (`write.py:520`).** An toàn. `replacement` đã qua `clean_ai_text` (`workflow.py:108`), nên dòng đầu đã được escape như thể đứng đầu dòng. Tiền tố `**Gợi ý:** ` chỉ **đẩy** dòng đầu ra khỏi đầu dòng, không đưa dòng nào vào đầu dòng. Tiền tố cũng kết thúc bằng dấu cách, không chứa `]`, nên không ghép được `](`, `][`, `]:`. Mỗi `st.markdown` dựng riêng, nên khai báo link ở khối này không có tác dụng ở khối khác. Kiểm chứng: 30 000 `**Gợi ý:** {clean_ai_text(s)}` và 30 000 `st.caption`-tương đương (`reason`) qua CommonMark: 0 link. Họa Sĩ ghi điều này là suy luận, chưa có test; nay đã có kiểm chứng bằng bộ dựng thật.

**Thời gian chạy** (chống treo app): `[a]( `×50 000 + `)`×50 000 (300 KB): 0,79 s; `` `a ``×150 000: 0,26 s; `[a](b c)`×40 000: 0,21 s; `\r[a]: …\r`×20 000: 0,17 s; `quote_ai_text` 360 KB: 0,07 s. Đều tuyến tính và dưới 1 s. Trường hợp 0,79 s chậm hơn trước (0,04 s), Thợ Máy đã nêu; chưa thành rủi ro treo.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp (**có từ trước**, không do T-013/T-014) | `apply_flag` thay câu bằng `body.replace(sentence, replacement)` rồi chỉ chạy `escape_link_syntax`, **không** `strip_tags`. `clean_ai_text` cho phép chữ kết thúc bằng `<` (chỉ tách `<` đứng trước chữ cái), nên phần nối có thể ghép `<` với chữ phía sau thành thẻ HTML hoặc autolink. | `seo_app/content/workflow.py:154-159`; chạy tự động trong `apply_replacements` `:162-174` ← `write_and_review` `:232`; và khi bấm Áp dụng `app/views/write.py:217` | Trang đối thủ dụ AI viết thân bài `Gọi ngay fooa href="https://evil.example">thợ giỏi nhất` (qua lọc vì không có `<`), rồi ở lượt rà soát chỉ ra câu `foo` với gợi ý `bên mình <`. AI **tự sửa** trước khi người dùng xem, thân bài thành `Gọi ngay bên mình <a href="https://evil.example">thợ giỏi nhất`. Đã chạy thật: `apply_replacements` ra đúng chuỗi này. `sanitize_html(markdown→html)` vẫn giữ `<a href="https://evil.example">thợ giỏi nhất</a>`, tức link ẩn. Biến thể `<https://evil.example>` thành autolink (địa chỉ hiện ra). **Hôm nay chưa có đường gây hại:** thân bài hiện qua `ui.highlight` (escape `& < >`, `ui.py:64-81`); `st.markdown` không bật `unsafe_allow_html` thì Streamlit không dựng HTML thô; trang WordPress hiện chỉ gửi chữ người dùng gõ (`app/views/wordpress.py:109-111`), chưa gửi bài AI. Thành **Cao** ngay khi Giai đoạn 5 gửi thân bài AI lên WordPress mà chưa sửa. | Trong `apply_flag`, gọi `strip_tags` trước `escape_link_syntax`: `escape_link_syntax(strip_tags(…))`. `strip_tags` đã bỏ thẻ và tách `<` khỏi chữ cái, nên không ghép được nữa; chạy lại trên chữ đã lọc thì không đổi gì. Thêm test: `apply_flag("Gọi fooa href=\"https://x\">y", "foo", "z <")` không còn `<a`, và `<https://…>` không còn đi liền. Mở **phiếu sửa nhỏ, phải xong trước khi bắt đầu phần xuất bài của Giai đoạn 5**. Ghi sổ rủi ro tới lúc đó. |

Ghi nhận thêm (không tính lỗi):
- `quote_ai_text` nhận chuỗi tùy ý có autolink `<https://…>` thì vẫn hiện link, nhưng địa chỉ **hiện ra** (chữ = địa chỉ). Đây là rủi ro "địa chỉ hiện trần" đã chấp nhận. Câu thật luôn là đoạn con của thân bài đã lọc, nên chỉ gặp qua lỗi #1.
- Fuzz cũng thấy `apply_flag` tạo autolink có scheme lạ (`<ng:…>`, `<le:-[]>`); cùng gốc với lỗi #1, sửa #1 là hết.
- `seo_app/sanitize.py:425-427` chỉ có một dòng trống trước `def clean_ai_text` (PEP 8 cần hai). Đây là chuyện cách viết; ruff cấu hình hiện tại không bắt.
- Báo cáo T-014 tự khai đã dùng `git stash`/`stash pop` khoảng 2 giây khi agent khác đang sửa song song. Điều này nay bị cấm theo R11 (`docs/team/rules.md`, thêm trong cùng đợt này, có vẻ sau sự việc). Tôi không thấy hậu quả: diff của Họa Sĩ (`quote_ai_text`, 2 test mới) còn nguyên và toàn bộ test xanh. Đề nghị Chỉ Huy nhắc R11; tôi không chặn phiếu vì việc này.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | **Đạt** | Grep `sk-ant`, `AIza`, `AKIA`, `GOCSPX`, `PRIVATE KEY`, `password=` trên `git diff HEAD` + file chưa theo dõi: chỉ ra hằng số giả `PASSWORD = "mat-khau-thu-123"` (test, dòng ngữ cảnh). `git log -p 2f53463..HEAD` tìm mẫu khóa thật: chỉ ra chữ trong biên bản trước. HEAD vẫn `17aadbe`. detect-secrets: 3 cảnh báo, đều là báo nhầm (bên dưới). |
| S2 | **Đạt** | Diff không thêm `st.error`, `st.exception`, log hay `repr`. `quote_ai_text` chỉ hiện câu AI (không phải bí mật). |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. |
| W1 | **Đạt** | Không đụng `seo_app/wordpress/`; không có đường `publish`/`future` mới. |
| W2 | **Đạt** | Không có `PUT`/`DELETE` mới, `client.py` không đổi. |
| W3 | **Đạt** (lỗi #1 Thấp ghi sổ) | `clean_ai_text` vẫn: chuẩn hóa `\r` (`sanitize.py:437`), vòng làm gọn, `escape_link_syntax` cuối cùng (`:445`). Fuzz 30 000 + 45 mẫu viết tay: 0 link ẩn. `sanitize_html` không đổi. Lỗi #1 (có từ trước) phải sửa trước khi xuất bài AI lên WordPress. |
| W4 | Không áp dụng | Không đổi client HTTP. |
| A1 | Không áp dụng | Không đổi prompt (`seo_app/content/prompts.py` không đổi). |
| A2 | **Đạt** | Kết quả AI hiển thị ở khung «Cần xem lại» nay đều qua lớp chặn link: câu qua `quote_ai_text` (`write.py:518`), lý do và gợi ý qua `clean_ai_text` (`workflow.py:108-109`). AI vẫn không có công cụ hành động. Lỗi #1 là chỗ kết quả AI ghép lại chưa được `strip_tags`. |
| A3 | Không áp dụng | Không đổi dữ liệu gửi vào prompt. |
| U1 | **Đạt** | Diff không thêm `unsafe_allow_html`. `write.py:518` và `:520` dùng `st.markdown` không có `unsafe_allow_html`, nên HTML thô bị Streamlit escape. Các chỗ `unsafe_allow_html` sẵn có (`:409`, `:471`, `:495`, `:551`, `:588`) không đổi. |
| U2 | Không áp dụng | Không đổi `app/main.py`, `.streamlit/config.toml`. |
| U3 | Không áp dụng | Không đổi `seo_app/auth.py`. |
| F1 | **Đạt** | Diff không có `open(`/`Path(` mới. |
| F2 | Không áp dụng | Không đụng ảnh/EXIF; GPS giữ nguyên theo sổ rủi ro mục 6. |
| F3 | **Đạt** | Không có `eval`/`exec`/`pickle`/`yaml.load`/`subprocess` trong diff; regex mới (`_ASCII_SPACE`, `_BACKTICK_RUN`, `_LINE_BREAK`) đơn giản, không lồng lượng từ (không ReDoS); bandit 0 cảnh báo. |
| D1 | **Đạt** | `pyproject.toml`, `uv.lock` không đổi; `bisect` là thư viện chuẩn. `markdown-it-py`, `linkify-it-py` chỉ chạy tạm qua `uv run --with`, **không** thêm vào dự án. pip-audit sạch. |
| D2 | **Đạt** | `.gitignore` không đổi: `.env` (`:2`), `.env.*` (`:3`), `*service-account*.json` (`:5`), `secrets/` (`:6`), `.venv/` (`:10`), `*.sqlite*` (`:23-24`). |
| D3 | **Đạt** | Test Họa Sĩ/Thợ Máy thêm (`tests/test_edit_unescape.py`, `tests/test_link_escape.py`) không dùng `socket`/`requests`/`httpx`/`urlopen` (grep); AppTest dùng provider giả như trước; `tests/conftest.py` không đổi. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt --no-hashes` (156 dòng) → `uvx pip-audit -r … --no-deps`: **No known vulnerabilities found** (`seo-app` bỏ qua vì không có trên PyPI, bình thường). `uv.lock` không đổi. | Có |
| bandit | `uvx bandit seo_app/sanitize.py app/views/write.py` (1 046 dòng): **No issues identified**. | Có |
| detect-secrets | `uvx detect-secrets scan` trên 8 file đổi/mới: 3 cảnh báo, đều báo nhầm (bên dưới). | Có |
| Soát lịch sử git | HEAD `17aadbe`, không commit mới; `git log -p 2f53463..HEAD` không có mẫu khóa thật; diff chưa commit sạch. | Có |
| pytest / ruff | `uv run pytest`: **1444 passed, 6 xfailed** (37 s). Riêng 3 file liên quan: 647 passed, 2 xfailed (đều là R4-3, cố ý). 4 xfail còn lại thuộc test Soi Lỗi đang thêm song song và SL-7, ngoài phạm vi. `uv run ruff check .`: **All checks passed**. | Có |
| Kiểm chứng CommonMark thật | `uv run --with markdown-it-py --with linkify-it-py python <script trong scratchpad>`. Script lấy **đúng mã nguồn** `quote_ai_text` từ `write.py` (qua `ast`, không import trang Streamlit). Đã chạy: 19 mẫu R4-1 cùng mọi đoạn con; 26 mẫu R4-4/code; fuzz 30 000 chuỗi × 8 kiểu kiểm (đoạn con → `quote_ai_text`, chuỗi thô → `quote_ai_text`, `**Gợi ý:**`, `reason`, `escape_link_syntax` thô có `\r`, `apply_flag`, `clean_ai_line`, idempotent/round-trip); 5 phép đo thời gian. Kết quả: 0 link ẩn ở mọi đường của T-013/T-014. Có 11 trường hợp ra `<a>`, đều đã phân loại: 1 autolink tự gõ (địa chỉ hiện ra, không tới được trên đường thật) và 10 từ `apply_flag` (lỗi #1). | Có |

## Báo nhầm đã loại

| Công cụ | Cảnh báo | Lý do loại |
|---|---|---|
| detect-secrets | `tests/test_edit_unescape.py:18` `PASSWORD = "mat-khau-thu-123"` | Mật khẩu giả của AppTest, đã có từ biên bản trước, trùng `tests/test_app.py:8`. |
| detect-secrets | `tests/test_link_escape.py:205` `http://wp:abcd%20efgh@site.vn` | Dữ liệu vào của test `redact_secrets` (có từ trước). |
| detect-secrets | `tests/test_soi_loi_round4.py:209` `PASSWORD = "mat-khau-thu-123"` | Cùng hằng số giả. File này thuộc Soi Lỗi; diff T-013/T-014 chỉ gỡ `xfail`. |
| Kiểm chứng CommonMark | `r41-quote`: `> [a]\: <https://evil.example>` ra `<a>` | Autolink `<…>` có chữ hiện ra đúng là địa chỉ. Chuỗi này chỉ có khi đưa chuỗi thô (chưa lọc) vào hàm; trên đường thật câu là đoạn con của thân bài đã `strip_tags`. |

## Điều kiện

Không có điều kiện chặn. **T-013: ĐẠT. T-014: ĐẠT.**

Đề nghị Chỉ Huy:
- **Lỗi #1 (Thấp, có từ trước):** mở phiếu sửa nhỏ cho Thợ Máy (`apply_flag` thêm `strip_tags` + 1–2 test), **phải xong trước khi bắt đầu phần xuất bài AI lên WordPress ở Giai đoạn 5**. Tới lúc đó, ghi vào sổ rủi ro. Phiếu này cần Lá Chắn kiểm lại (sửa code).
- R4-3: giữ `xfail` như Chỉ Huy đã quyết; nếu muốn sửa thì làm ở bước hiển thị, không làm ở `escape_link_syntax` (đồng ý với đề xuất của Thợ Máy).
- Nhắc R11 cho cả đội.
- Lần kiểm lại bằng Claude Fable 5.1 khi có hạn mức: chỉ cần chạy lại mục "Kiểm chứng CommonMark" và xem lại lỗi #1.

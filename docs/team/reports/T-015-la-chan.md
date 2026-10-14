# Biên bản bảo mật T-015 · Lỗi Thấp còn lại sau T-013/T-014, test tốc độ ổn định

> **Ghi chú model:** lần kiểm định này chạy **tạm bằng Claude Opus 5.5**. Model quy định cho Lá Chắn là Claude Fable 5.1, nhưng Fable đang bị giới hạn tới 01/11. Sau ngày đó sẽ kiểm lại bằng Fable; tới lúc ấy kết luận dưới đây vẫn có hiệu lực.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable 5.1, xem ghi chú) |
| Phiếu được kiểm | [T-015](../tickets/T-015-loi-thap-con-lai.md) (Thợ Máy, [báo cáo](T-015-tho-may.md)) |
| Phạm vi | Thay đổi **chưa commit** so với `HEAD` = `8b1b125`: `seo_app/content/workflow.py` (+3/−2), `seo_app/sanitize.py` (+42/−7), `tests/timing.py` (mới), 5 file test (phần đo tốc độ, gỡ `xfail` R5-1). Kiểm lại lỗi #1 của [biên bản T-013/T-014](T-013-014-la-chan.md). Không thuộc biên bản này: `tests/test_soi_loi_round6.py` và `T-015-soi-loi.md` (Soi Lỗi làm song song); tôi chỉ đối chiếu. |
| Ngày | 2026-10-14 |
| **Kết luận** | **Lần 2: ĐẠT** (xem mục [Lần 2](#lần-2-2026-10-14) ở cuối). Lần 1: KHÔNG ĐẠT, chỉ vì **mục 1** (`apply_flag`): lỗi #1 chưa đóng. Mục 2 (R5-1), mục 3 (test tốc độ), mục 4 (PEP 8): **ĐẠT**. |

> Ghi chú môi trường: tôi không dùng `git stash`/`checkout`/`reset`/`clean`, không commit; chỉ đọc `git diff HEAD`. `uv.lock`, `pyproject.toml`, `.env.example`, `.gitignore`, `.streamlit/`, `app/`, `scripts/` không đổi (`git diff HEAD --stat` không liệt kê).

## Tóm tắt (cho chủ dự án)

Phần sửa chữ bị mất (R5-1) an toàn. Tôi thử 147 mẫu viết tay và 30 000 chuỗi ngẫu nhiên bằng bộ dựng Markdown chuẩn: không còn link nào lọt. Kể cả khi ép bộ đoán trả lời sai hoàn toàn thì cũng không có link nào lọt, vì bước chặn link cuối cùng không phụ thuộc vào bộ đoán. Test tốc độ mới vẫn bắt được code chậm kiểu bình phương.

Lỗ ở chỗ «AI tự sửa câu» thì **chưa được vá**. Mẫu tấn công tôi nêu ở biên bản trước vẫn ra nguyên một link ẩn `<a href="https://evil.example">`. Bản sửa mới chỉ lọc câu AI gợi ý. Nhưng thẻ độc được ghép ở **chỗ nối** giữa câu đó với phần bài xung quanh, nên lọc riêng câu gợi ý không đủ. Hôm nay lỗ này chưa gây hại, vì app luôn hiện thẻ thành chữ thường. Tuy vậy, bộ lọc HTML khi gửi WordPress **giữ lại** link `https`. Vì vậy lý do "đã có `sanitize_html`" không đủ để hạ mức. Cần sửa thêm một dòng, chạy bộ lọc thẻ trên **cả kết quả sau khi ghép**, rồi phiếu mới đóng được.

## Kết luận riêng từng mục của phiếu

| Mục | Kết luận | Lý do ngắn |
|---|---|---|
| 1. `apply_flag` bỏ thẻ | **KHÔNG ĐẠT** | Lỗi #1 vẫn tái hiện được bằng đúng mẫu cũ, cả hai chỗ nối, cả nhánh bỏ câu. Chi tiết ở lỗi #1 bên dưới. |
| 2. R5-1 `looks_like_destination` | **ĐẠT** | Không mở lại đường cho link thật. Bằng chứng ở mục "Kiểm R5-1". |
| 3. Test tốc độ theo tỉ lệ | **ĐẠT** (1 lỗi Thấp) | Vẫn bắt thuật toán bình phương. Nhưng mất mốc tuyệt đối, nên không còn bắt được code tuyến tính mà rất chậm (lỗi #2). |
| 4. PEP 8 | **ĐẠT** | `sanitize.py` nay có 2 dòng trống trước `def clean_ai_text`; ruff sạch. |

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | **Thấp hôm nay, thành Cao khi Giai đoạn 5 gửi thân bài AI lên WordPress.** Không phải lỗi mới: đây là lỗi #1 của biên bản T-013/T-014, **chưa đóng**. | `apply_flag` chỉ chạy `strip_tags` trên **câu thay thế**, không chạy trên **kết quả sau khi ghép**. Thẻ được ghép từ `<` ở một bên chỗ nối và chữ ở bên kia, nên lọc từng mảnh riêng không chặn được. Phiếu và biên bản trước yêu cầu `escape_link_syntax(strip_tags(…))` trên kết quả. | `seo_app/content/workflow.py:154-160` (`:159` nhánh thay, `:160` nhánh bỏ câu). Chạy tự động qua `apply_replacements` `:163-175` ← `write_and_review` `:233`, và khi bấm Áp dụng ở `app/views/write.py:217`. | Đã chạy thật, thân bài đều qua `clean_ai_text` trước: **(a) chỗ nối phải**, mẫu của biên bản trước: thân `Gọi ngay fooa href="https://evil.example">thợ giỏi nhất`, câu `foo`, gợi ý `bên mình <`. `strip_tags("bên mình <")` không đổi, vì `<` đứng cuối, sau nó không có chữ. Kết quả là `Gọi ngay bên mình <a href="https://evil.example">thợ giỏi nhất`. **(b) chỗ nối trái** (câu hỏi của Thợ Máy): thân `Gọi ngay <"foo" nhé` (`clean_ai_text` giữ, vì sau `<` là dấu nháy), câu `"foo"`, gợi ý `a href="https://evil.example">thợ giỏi`, ra `<a href=…>`. Chữ bình thường cũng dính, ví dụ «Nhiệt độ <5 độ là tốt.» (R6-2 của Soi Lỗi). **(c) nhánh bỏ câu:** thân `Gọi ngay <"x" a href="https://evil.example">thợ giỏi`, bỏ câu `"x"`, ra `<a href=…>`. **(d)** dạng `<https://evil.example>` thành autolink. Trong cả bốn trường hợp, đem Markdown dựng thành HTML rồi chạy `sanitize_html` thì **vẫn còn** `<a href="https://evil.example">…</a>`, vì `a[href]` với `https` được phép (`sanitize.py:502`, `:512`). Kết quả là một link ẩn tới trang lạ, trái mục 2.3 «không tự chèn link lạ». Kẻ tấn công cần dụ AI qua trang đối thủ (prompt injection) để AI viết cả thân bài lẫn gợi ý sửa. Bước sửa này chạy **tự động trước khi người dùng xem**. **Hôm nay chưa gây hại:** thân bài hiện qua `ui.highlight` (escape `& < >`, `seo_app/ui.py:64`), `st.markdown` không bật `unsafe_allow_html`, và chưa có đường gửi thân bài AI lên WordPress. | Một dòng, đúng như biên bản trước: chạy `strip_tags` trên **kết quả sau khi ghép**, ở **cả hai nhánh**: `escape_link_syntax(strip_tags(body.replace(sentence, strip_tags(replacement))))` và `escape_link_syntax(strip_tags(body.replace(…).strip()))`. Tôi đã thử cách này: (a) ra `Gọi ngay bên mình thợ`, (b) ra `Gọi ngay thợ nhé`, (c) ra `Gọi ngay thợ giỏi`, đều không còn thẻ. Cái giá là HTML người dùng tự gõ trong phần đó cũng bị bỏ khi áp gợi ý. Tôi chấp nhận được, vì thân bài là Markdown. Nếu Chỉ Huy muốn giữ HTML tự gõ thì tối thiểu phải chạy `_TAG_OPEN.sub("< ", …)` trên kết quả. **Không** được chỉ xử lý câu thay thế. Test cần có: (a), (b), (c), (d); gỡ `xfail` R6-2 của Soi Lỗi. Board.md mục «Việc bắt buộc Giai đoạn 5» nên ghi rõ: `sanitize_html` **không** bỏ link `https`, nên lớp chặn link ẩn ở bước gửi là màn hình xác nhận liệt kê `href`. |
| 2 | Thấp | Test tốc độ theo tỉ lệ bỏ mất **mốc tuyệt đối**. Code vẫn tuyến tính nhưng chậm đi nhiều lần sẽ không còn bị bắt. Mốc cũ có từ Lá Chắn #1 của T-004: «không thể làm treo app». Code chạy cỡ $n^{1{,}5}$ cũng nằm sát ngưỡng ($4^{1{,}5} = 8 < 9$). | `tests/timing.py:16-55` | Một thay đổi sau này làm `clean_ai_text` chậm đi 20 lần nhưng vẫn tuyến tính, ví dụ 200 KB mất 5 giây: test vẫn xanh. Mỗi lần AI trả bài dài, app treo vài giây. Đã kiểm: một hàm tuyến tính chậm, 1,4 s cho 200 KB, **lọt**. Mốc cũ `< 1.0` sẽ bắt được. Không phải lỗ khai thác: đầu vào là bài AI tối đa khoảng 100 KB, chạy trên máy người dùng. | Thêm vào `assert_scales_linearly` một mốc tuyệt đối **rộng** cho lần đo lớn, ví dụ `t_large < 5 s`. Mốc này không đỏ oan trên máy Windows chậm (hiện chỉ khoảng 0,2 s) nhưng vẫn chặn được việc treo app. Nếu Thợ Máy đổi sang `time.process_time` như Soi Lỗi gợi ý ở R6-3, về bảo mật không có vấn đề gì. |

Ghi nhận thêm (không tính lỗi):
- Trong `test_title_lookup_stays_linear` (`tests/test_link_escape.py`), đầu vào `"[a](x (" * N + ")" * 2N` chỉ gọi `_title_end` **một lần**: link ngoài cùng nuốt hết phần còn lại. Vì vậy ca này không thật sự thử "tra tiêu đề nhiều lần". Tôi đã thử một bản lỗi cố ý, quét thẳng để tìm ngoặc đóng: test **không bắt**. Code thật thì không chậm, vì tra qua `pairs`. Đề nghị Soi Lỗi thêm một đầu vào gọi `_title_end` nhiều lần với tiêu đề dài, ví dụ `('[a](x (' + 't' * m + ') y)') * N`. Đây không phải lỗi bảo mật.
- Bộ đoán R5-1 so với CommonMark: trong 21 436 ca `[a](…)` ngẫu nhiên, có 166 ca CommonMark coi là link mà bộ đoán nói "không phải". Đa số là ca có `\` escape. Ở các ca này chữ được giữ và `]\(` vẫn được thêm, nên không thành link (kiểm bằng `assert` trong cùng script). Chỉ là chữ dư, đúng như docstring nói «chỉ để chữ gọn».
- R6-1 của Soi Lỗi (`(<0,5 mm)` mất chữ) cũng chỉ là chuyện hiển thị, không ảnh hưởng an toàn. Nếu sửa thì đi theo cùng hướng R5-1 (kiểm tra có `>` đóng).

## Kiểm R5-1: có mở lại đường cho link thật không

**Lập luận:** `strip_markdown_links` chỉ được gọi trong `clean_ai_text` (`sanitize.py:475`). Sau nó luôn có `escape_link_syntax` (`:480`), và hàm này escape **mọi** `](`, `][`, cùng `]:` ở đầu dòng mà không cần nhận ra link. Vì vậy `looks_like_destination` trả lời sai chỉ dẫn tới **giữ chữ**, không dẫn tới link. Chữ được giữ cũng không ghép được thẻ mới: giữ nhiều hơn tức là ghép ít hơn. `\r` đã được đổi thành `\n` từ trước (`:472`), nên bộ đoán không bao giờ gặp `\r` đứng riêng.

**Kiểm chứng bằng bộ dựng thật** (`markdown-it-py` CommonMark và GFM có linkify, chạy tạm qua `uv run --with`, **không** thêm vào dự án):

| Thử | Kết quả |
|---|---|
| 49 mẫu viết tay × 3 biến thể (địa chỉ `x`, địa chỉ `https://evil.example`, có chữ bao quanh) = 147 ca. Gồm: tiêu đề `"…"`, `'…'`, `(…)`; địa chỉ `<…>` có dấu cách; `<>` rỗng; tiêu đề xuống dòng; tiêu đề ở dòng sau; `\r`, `\r\n`, tab, `\f`, `\v`, NBSP; ngoặc lồng `((t))`, `(a(b)c)`, `(a\)b)`; nháy escape `"a\"b"`; hai tiêu đề; tiêu đề dính địa chỉ `x"t"`; `"t ) u"`; `'(' `; ảnh; link lồng; link trong code. | **0 link, 0 HTML thô** ở cả CommonMark và GFM. URL trần do linkify nhận ra, địa chỉ hiện đúng như chữ, nằm trong rủi ro "địa chỉ hiện trần" đã ghi nhận. |
| Fuzz 30 000 chuỗi từ bảng ký tự `[ ] ( ) " ' < > \ \n \r \t` … qua `clean_ai_text` | **0** link hoặc HTML thô |
| Cùng fuzz, **ép** `looks_like_destination` luôn `False` | **0**. An toàn không phụ thuộc bộ đoán. |
| Cùng fuzz, ép luôn `True` | **0** |
| Thời gian | `test_title_lookup_stays_linear` xanh. Bản lỗi cố ý "lập lại bảng mỗi lần tra" bị bắt với tỉ lệ 16,5. |

## Kiểm test tốc độ: có làm yếu khả năng bắt thuật toán chậm không

`assert_scales_linearly` (`tests/timing.py`) đo cỡ 1/4 và cỡ đầy đủ, rồi đòi tỉ lệ thời gian không quá 9. Tôi kiểm bằng các hàm cố ý chậm ở cỡ 200 000 ký tự:

| Hàm thử | Kết quả |
|---|---|
| Bình phương thuần | **Bắt**, tỉ lệ 17,1 |
| Tuyến tính + bình phương, phần bình phương nhỏ | **Bắt**, tỉ lệ 14,3 và 15,1 |
| Bản lỗi thật của `_Whitespace`: lập lại bảng mỗi lần tra | **Bắt**, tỉ lệ 16,5 |
| $n^{1{,}5}$ | Bắt sát ngưỡng (9,7). Về lý thuyết là 8, tức có thể lọt. |
| Tuyến tính nhưng chậm (1,4 s / 200 KB) | **Lọt** (lỗi #2) |

Đầu vào không bị thu nhỏ: `make(4)` cho đúng chuỗi cũ. Đã so từng dòng diff ở 5 file. Ví dụ `test_filters_stay_fast_on_more_adversarial_inputs` vẫn đòi `len(make(4)) >= 190_000`. Các kiểm tra "không còn thẻ, không còn link" vẫn chạy trên cỡ đầy đủ. Mức sàn `MIN_SECONDS = 1e-4` chỉ ảnh hưởng các ca chạy dưới 0,1 ms. Ở các ca đó, mốc cũ `< 1 s` cũng không bắt được gì, nên không yếu đi. Kết luận: **không làm yếu khả năng bắt thuật toán bình phương**, chỉ mất mốc tuyệt đối (lỗi #2).

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | **Đạt** | Grep `sk-ant`, `AIza`, `AKIA`, `GOCSPX`, `PRIVATE KEY`, `password=` trên `git diff HEAD` và file chưa theo dõi: chỉ trúng chữ trong biên bản trước (dòng mô tả cách grep). `git log -p 17aadbe..HEAD`: không có mẫu khóa thật. detect-secrets: chỉ ra khóa giả có từ trước, không nằm trong diff (bên dưới). |
| S2 | **Đạt** | Diff không thêm `st.error`, `st.exception`, log hay `repr`. Thông báo `assert` trong `tests/timing.py:55` chỉ in tỉ lệ thời gian. |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. |
| W1 | **Đạt** | Không đụng `seo_app/wordpress/`; không có đường `publish`/`future` mới. |
| W2 | **Đạt** | Không có `PUT`/`DELETE` mới. |
| W3 | **Không đạt** (lỗi #1, Thấp hôm nay) | `clean_ai_text` vẫn chặn link: 147 mẫu, fuzz 30 000 lần ×3, 0 link. Nhưng `apply_flag` (`workflow.py:159-160`) vẫn ghép được thẻ `<a href="https://…">`, và `sanitize_html` giữ thẻ đó lại. Phải sửa trước khi đóng mục 1. |
| W4 | Không áp dụng | Không đổi client HTTP. |
| A1 | Không áp dụng | Không đổi prompt. |
| A2 | **Không đạt** (lỗi #1) | Kết quả AI (thân bài, câu, câu thay thế) được ghép lại mà phần ghép xong không được lọc thẻ. AI vẫn không có công cụ hành động. |
| A3 | Không áp dụng | Không đổi dữ liệu gửi vào prompt. |
| U1 | **Đạt** | Diff không thêm `unsafe_allow_html`. Thẻ sinh ra từ lỗi #1 hiện qua `ui.highlight` (escape `& < >`, `seo_app/ui.py:64`), nên hôm nay chỉ hiện thành chữ. |
| U2 | Không áp dụng | Không đổi `app/main.py`, `.streamlit/config.toml`. |
| U3 | Không áp dụng | Không đổi `seo_app/auth.py`. |
| F1 | **Đạt** | Diff không có `open(`/`Path(` mới. |
| F2 | Không áp dụng | Không đụng ảnh/EXIF; GPS giữ theo sổ rủi ro mục 6. |
| F3 | **Đạt** | Không có `eval`/`exec`/`pickle`/`yaml.load`/`subprocess` trong diff. Regex mới `_UNESCAPED_QUOTE = r"\\[\s\S]\|([\"'])"` (`sanitize.py:164`) không có lượng từ lồng nhau, nên không có ReDoS. `bisect` tra theo log. `tests/timing.py` chỉ import `gc`, `time`, `collections.abc`. |
| D1 | **Đạt** | `pyproject.toml`, `uv.lock` không đổi. `markdown-it-py`, `linkify-it-py` chỉ chạy tạm qua `uv run --with`, không thêm vào dự án. pip-audit sạch. |
| D2 | **Đạt** | `.gitignore` không đổi. |
| D3 | **Đạt** | `tests/timing.py` và các test sửa không dùng `socket`/`requests`/`httpx`/`urlopen` (grep). Không đổi `tests/conftest.py`. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt --no-hashes` (156 dòng) → `uvx pip-audit -r … --no-deps`: **No known vulnerabilities found**. `seo-app` bị bỏ qua vì không có trên PyPI, bình thường. `uv.lock` không đổi. | Có |
| bandit | `uvx bandit -r seo_app app scripts` (3 053 dòng): **0 cảnh báo**. Chạy thêm trên `tests/timing.py`: 2 cảnh báo B101 (`assert`), báo nhầm. | Có |
| detect-secrets | `uvx detect-secrets scan` trên 9 file đổi/mới: 11 cảnh báo. Tất cả nằm ở dòng **không thuộc diff** và là khóa giả dùng cho test che bí mật (bên dưới). | Có |
| Soát lịch sử git | HEAD `8b1b125`. `git log -p 17aadbe..HEAD` không có mẫu khóa thật; diff chưa commit sạch. | Có |
| pytest / ruff | `uv run pytest`: **1512 passed, 9 xfailed** (59 s). Con số này gồm cả `tests/test_soi_loi_round6.py` của Soi Lỗi đang làm song song. 9 xfail gồm: R4-3 ×2 (đã chấp nhận), SL-7 (Giai đoạn 5), R6-1 ×3, R6-2 ×2 (chính là lỗi #1), R6-3. `uv run ruff check .`: **All checks passed!** | Có |
| Kiểm chứng bằng bộ dựng thật | Các script trong scratchpad, chạy bằng `uv run --with markdown-it-py --with linkify-it-py`: PoC lỗi #1 (4 dạng) và bản sửa đề xuất; 147 mẫu R5-1; fuzz 30 000 × 3 chế độ; so sánh bộ đoán với CommonMark (21 436 ca); thử các hàm cố ý chậm. Kết quả đã ghi ở trên. | Có |

## Báo nhầm đã loại

| Công cụ | Cảnh báo | Lý do loại |
|---|---|---|
| bandit | B101 `assert` ở `tests/timing.py:40`, `:55` | File test; `assert` là cách pytest kiểm tra. |
| detect-secrets | `tests/test_soi_loi_round3.py:347-348, 365-367`; `tests/test_soi_loi_t003_t009.py:234-237, 261` | Chuỗi giả kiểu `sk-ant-api03-AAAA…`, `AIzaSyA-abcdef…`, dùng để thử `redact_secrets`. Có từ trước và nằm ngoài các khối diff (`git diff -U0` chỉ đụng dòng 9–115 và 124–147). |
| detect-secrets | `tests/test_link_escape.py:207` `http://wp:abcd%20efgh@site.vn`; `tests/test_soi_loi_round5.py:33` | Dữ liệu giả có từ trước (đã loại ở biên bản T-013/T-014). |

## Điều kiện để chuyển thành ĐẠT

1. **Thợ Máy sửa lỗi #1 ngay trong T-015**, bằng cách chạy `strip_tags` trên kết quả sau khi ghép, ở cả hai nhánh của `apply_flag`. Thêm test cho 4 dạng (a)–(d) ở trên và gỡ `xfail` R6-2. Lá Chắn kiểm lại; chỉ cần xem `apply_flag` và chạy lại PoC.
2. **Lỗi #2 (Thấp):** không chặn phiếu. Đề nghị Thợ Máy thêm mốc tuyệt đối rộng (ví dụ 5 s) vào `assert_scales_linearly` khi sửa R6-3 của Soi Lỗi. Tới lúc đó, ghi vào sổ rủi ro.
3. **Chỉ Huy cập nhật board.md** mục «Việc bắt buộc khi làm Giai đoạn 5»: `sanitize_html` giữ link `https`, nên **không** chặn được link ẩn. Lớp chặn ở bước gửi là màn hình xác nhận liệt kê mọi `href`, và mục này là bắt buộc.

Mục 2, 3, 4 của phiếu đã đạt, không cần làm lại. Khi Fable 5.1 dùng được lại (sau 01/11), lần kiểm lại chỉ cần chạy lại phần "Kiểm R5-1" và PoC lỗi #1.

---

## Lần 2 (2026-10-14)

> Vẫn chạy **tạm bằng Claude Opus 5.5**, vì Fable 5.1 bị giới hạn tới 01/11.

| Mục | Nội dung |
|---|---|
| Phạm vi | Thay đổi chưa commit so với `HEAD` = `8b1b125`, sau lần sửa thứ 2 của Thợ Máy ([báo cáo, mục "Lần 2"](T-015-tho-may.md)): `apply_flag` (`seo_app/content/workflow.py:154-167`); R6-1 trong `looks_like_destination` (`seo_app/sanitize.py:165`, `:221-268`); `tests/timing.py` (đo bằng `process_time`, thêm `MAX_SECONDS`); test mới `test_apply_flag_seam_cannot_make_tag_or_autolink` (`tests/test_link_escape.py:354`); gỡ `xfail` R6-1/R6-2/R6-3; `board.md` mục Giai đoạn 5. |
| **Kết luận** | **ĐẠT**. Lỗi #1 và lỗi #2 đã đóng; R6-1 không mở đường cho link nào. Không còn lỗi Nghiêm trọng, Cao hay Trung bình. |

### Tóm tắt (cho chủ dự án)

Lỗ ở chỗ «AI tự sửa câu» đã được vá. Cả 4 mẫu tấn công lần trước giờ chỉ còn chữ thường, không còn link ẩn. Tôi thử thêm 30 000 lần ghép ngẫu nhiên: không lần nào tạo ra thẻ hay link. Phần sửa chữ bị mất khi trong ngoặc có «<» (R6-1) cũng an toàn. Test tốc độ giờ bắt được cả code chậm bất thường, không chỉ code chậm kiểu bình phương.

### Kiểm lại 4 dạng tấn công (lỗi #1)

Chạy đúng các script của lần 1, thân bài đều qua `clean_ai_text` trước:

| Dạng | Lần 1 | Lần 2 |
|---|---|---|
| (a) chỗ nối phải: câu gợi ý `bên mình <` ghép với `a href="https://evil.example">…` | `<a href="https://evil.example">` | `Gọi ngay bên mình thợ giỏi nhất`: không thẻ, không link |
| (b) chỗ nối trái: `<"foo"` hoặc `<1 foo`, câu thay thế `a href=…>` | `<a href=…>` | `Gọi ngay thợ giỏi nhé` / `Gọi ngay thợ giỏi` |
| (c) nhánh bỏ câu: `<"x" a href=…>`, bỏ `"x"` | `<a href=…>` | `Gọi ngay thợ giỏi` |
| (d) autolink `<https://evil.example>` | link | `Gọi ngay bên mình  nhé`: địa chỉ bị bỏ |

Cũng qua `MarkdownIt("commonmark").render` rồi `sanitize_html`: không còn `<a`. Fuzz `apply_flag` với 29 529 bộ (thân bài sạch, câu là đoạn con, câu thay thế ngẫu nhiên gồm `<`, `<"`, `a href="…">`, `https://…>`, `img … onerror=…>`; có cả nhánh bỏ câu): **0** thẻ, **0** link. Code đúng như đề xuất: `escape_link_syntax(strip_tags(joined))` cho cả hai nhánh (`workflow.py:163-167`). Test của Thợ Máy có 6 trường hợp; Thợ Máy đã đối chứng là cả 6 đỏ với bản cũ. `xfail` R6-2 đã gỡ và xanh.

Cái giá là HTML người dùng tự gõ trong một phần sẽ bị bỏ khi bấm Áp dụng gợi ý ở phần đó. Tôi chấp nhận được, vì thân bài là Markdown; Thợ Máy cũng đã ghi điều này trong docstring.

### R6-1 không mở đường cho link thật

Như lần 1, `strip_markdown_links` chỉ chạy trong `clean_ai_text`, và `escape_link_syntax` luôn chạy sau cùng (`sanitize.py:509`). Thay đổi R6-1 chỉ làm bộ đoán nói "không phải link" nhiều hơn, tức **giữ chữ** nhiều hơn. Regex mới `_UNESCAPED_MARK` (`:165`) không có lượng từ lồng nhau, nên không có ReDoS. Vị trí các ký tự được tra bằng `bisect`, nên vẫn tuyến tính.

| Thử | Kết quả |
|---|---|
| 31 mẫu `<…>` viết tay × 3 biến thể = 93 ca. Gồm: `<x>`, `<x> "t"`, `<x>"t"`, `<x>\n"t"`, `<x y>`, `<x\>y>`, `<x\<y>`, `<x<y>`, `<x\ny>`, `<x` không đóng, `<x> y`, `< x>`, `<>`, `<x>)y`, `<x> (t)`, `<x>\t`, `<x>\r`, `<(x)>`, `<x>>`, `<x"> "t"`, `<x\\>`, `<x\r\ny>`, ảnh, link lồng, 3 mẫu R6-1 của Soi Lỗi. | **0** link và **0** HTML thô ở CommonMark và GFM (trừ URL trần hiện đúng địa chỉ, rủi ro đã ghi nhận) |
| Fuzz 30 000 chuỗi có thêm các mảnh `<x>`, `](<`, `[a](<`, `> ` | **0** |
| Cùng fuzz, ép bộ đoán luôn `False` / luôn `True` | **0** / **0** |
| Chạy lại toàn bộ kiểm R5-1 của lần 1 (147 mẫu, fuzz 20 000 ×3) | **0** |
| So bộ đoán với CommonMark: 14 307 ca `[a](…)` | 125 ca CommonMark coi là link mà bộ đoán nói "không". Sau `clean_ai_text` đều còn 0 link (có `assert`). Chỉ là chữ dư. |

### Test tốc độ (lỗi #2, R6-3)

`tests/timing.py` nay đo **thời gian CPU** (`time.process_time`). Mỗi lần đo kéo dài ít nhất 0,1 giây rồi chia cho số lần chạy. Có thêm mốc tuyệt đối `MAX_SECONDS = 5`. Thử lại bằng các hàm cố ý chậm:

| Hàm thử | Lần 1 | Lần 2 |
|---|---|---|
| Bình phương thuần | Bắt (17,1) | **Bắt** (15,5) |
| Tuyến tính + bình phương nhỏ | Bắt (14,3 / 15,1) | **Bắt** (18,5 / 15,4) |
| $n^{1{,}5}$ | Bắt sát ngưỡng (9,7) | **Bắt** (17,9) |
| Tuyến tính, khoảng 1,6 s / 200 KB | Lọt | Lọt. Chấp nhận được: dưới mốc 5 s, không treo app. |
| Tuyến tính, khoảng 6 s / 200 KB | (không thử) | **Bắt**: «cỡ đầy đủ mất 5,4 giây CPU» |

Không đầu vào nào bị thu nhỏ hay bỏ. Bỏ mức sàn 0,1 ms làm phép đo chặt hơn: các ca rất nhanh nay cũng đo được tỉ lệ thật. Lỗi #2 **đóng**.

Ghi nhận (không tính lỗi):
- `process_time` không tính lúc chờ (I/O, `sleep`). Các hàm được đo đều là xử lý chữ thuần, nên không ảnh hưởng.
- Ghi nhận ở lần 1 về `test_title_lookup_stays_linear` vẫn còn: ca `(` chỉ tra tiêu đề một lần. Việc này thuộc Soi Lỗi, không phải lỗi bảo mật.

### Board.md

Mục «Việc bắt buộc khi làm Giai đoạn 5» (`docs/team/board.md:52`) nay ghi rõ: `sanitize_html` cho qua `<a href="https://…">`, nên màn hình liệt kê mọi `href` là **bắt buộc**. Điều kiện 3 của lần 1 đã đạt.

### Danh sách kiểm tra (lần 2)

Chỉ ghi các dòng đổi so với lần 1; các dòng khác giữ nguyên kết quả, vì phạm vi file không đổi.

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| S1 | **Đạt** | `git diff HEAD` không có mẫu khóa. detect-secrets trên `sanitize.py`, `workflow.py`, `timing.py`: 0 cảnh báo. HEAD vẫn `8b1b125`. |
| W3 | **Đạt** | 4 dạng tấn công và fuzz 29 529 lần trên `apply_flag`: 0 thẻ, 0 link. Fuzz `clean_ai_text` 30 000 + 20 000 lần, mỗi bộ ×3 chế độ: 0. |
| A2 | **Đạt** | Kết quả AI ghép lại nay được `strip_tags` và `escape_link_syntax` sau khi ghép (`workflow.py:163-167`). |
| F3 | **Đạt** | Không có `eval`/`exec`/`pickle`/`subprocess`; regex mới đơn giản. |
| D1 | **Đạt** | `uv.lock`, `pyproject.toml` không đổi; pip-audit chạy lại: **No known vulnerabilities found**. |
| D3 | **Đạt** | `tests/timing.py` chỉ import `gc`, `time`, `collections.abc`; grep không có `socket`/`requests`/`urlopen`. |

### Công cụ quét (lần 2)

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found (156 gói, `uv.lock` không đổi) | Có |
| bandit | `-r seo_app app scripts`: 0 cảnh báo | Có |
| detect-secrets | 3 file code đổi: 0 cảnh báo | Có |
| Soát lịch sử git | Không có commit mới (`8b1b125`); diff sạch | Có |
| pytest / ruff | **1525 passed, 3 xfailed** (72 s): R4-3 ×2 (đã chấp nhận), SL-7 (Giai đoạn 5). `ruff check .`: **All checks passed!** | Có |

### Kết luận lần 2

**T-015: ĐẠT.** Không còn điều kiện. Khi Fable 5.1 dùng được lại (sau 01/11), lần kiểm lại chỉ cần chạy lại 4 dạng tấn công, fuzz `apply_flag` và phần kiểm R5-1/R6-1.

# Biên bản bảo mật T-004 + T-005 · Lọc HTML kết quả AI và hiển thị bài an toàn

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Fable 5.1 |
| Phiếu được kiểm | [T-004](../tickets/T-004-loc-html-ket-qua-ai.md) (Thợ Máy) và [T-005](../tickets/T-005-escape-hien-thi-bai.md) (Họa Sĩ) |
| Phạm vi | Thay đổi **chưa commit** so với `HEAD` = `ce73f97` (nhánh `main`): `seo_app/sanitize.py` (mới), `seo_app/content/workflow.py`, `seo_app/wordpress/client.py`, `seo_app/ui.py`, `tests/test_sanitize.py` (mới), `tests/test_ui_escape.py` (mới), gỡ `xfail` trong `tests/test_safety.py` và `tests/test_content_edge_cases.py`; rà mọi `unsafe_allow_html=True` trong `app/`. Kiểm lại lỗi #1 của [T-001](T-001-la-chan.md). |
| Ngày | 2026-10-14 |
| **Kết luận** | **T-004: ĐẠT** (4 lỗi Thấp, ghi sổ rủi ro) · **T-005: ĐẠT** (không phát hiện lỗi). **Lỗi #1 của T-001 đã được sửa đúng**; mốc gốc T-001 chuyển thành **ĐẠT CÓ ĐIỀU KIỆN** với các điều kiện còn lại ở cuối biên bản. |

> Ghi chú môi trường: lúc kiểm định, thư mục làm việc có thêm hai file **chưa commit** của Soi Lỗi (chạy song song): `tests/test_sanitize_bypass.py` và `docs/team/reports/T-004-T-005-soi-loi.md`. Hai file này **không** thuộc phạm vi biên bản và không được đánh giá; pytest trong biên bản chạy với `--ignore=tests/test_sanitize_bypass.py`.

## Tóm tắt (cho chủ dự án)

Lỗi lớn nhất của đợt kiểm định nền (bài AI viết có thể chứa mã HTML/JavaScript chạy ngay trong app và về sau lên website) **đã được sửa đúng, bằng hai lớp độc lập**: (1) ngay khi AI trả bài về, app bỏ hết thẻ HTML và địa chỉ link AI tự chèn; (2) khi hiển thị, mọi chữ được "khóa" thành chữ thường, chỉ còn thẻ tô màu do app tự thêm; và (3) trước khi gửi WordPress, nội dung đi qua bộ lọc chỉ giữ thẻ an toàn. Tôi đã thử hơn 130 cách lách (thẻ lồng nhau, chữ hoa, mã hóa ký tự, `javascript:` viết lắt léo, SVG, form, comment, thẻ không đóng, tô màu cắt ngang ký tự đặc biệt…) và **không cách nào tạo được thẻ HTML thật** ở cả ba chỗ. Bộ lọc không dùng thư viện mới, không đụng tới khóa, không đụng tới đường đăng bài.

Còn bốn điểm nhỏ, không khai thác được để chạy mã, ghi vào sổ rủi ro và gộp vào phiếu T-006 khi tiện: bộ lọc có thể bị làm chậm vài chục giây nếu AI trả về một bài toàn thẻ `<script>` rất dài; link dạng `//trang-la.com` và `/\trang-la.com` được coi là link nội bộ dù thực ra trỏ ra ngoài; vài chỗ (tiêu đề dàn ý, kết quả nghiên cứu) chưa qua lớp lọc 1 nhưng đã được lớp 2 che; thẻ nguy hiểm không đóng làm mất phần bài phía sau (hướng an toàn, nhưng bài rỗng thì người dùng phải để ý).

## Xác minh lỗi #1 của T-001

| Yêu cầu sửa trong T-001 | Đã làm | Bằng chứng |
|---|---|---|
| (a) Lọc tại ranh giới nhận kết quả AI: `Draft.intro`, `Section.body`, `SectionText.body`, `Flag.replacement`; bỏ/đánh dấu link Markdown | **Đã làm** | `workflow.py:28-37` (`clean_draft`: title, intro, heading, body), `:40-51` (`clean_review`: replacement, reason, summary), `:138` (`write`), `:145` (`review`), `:177` (`rewrite_section`). Link Markdown `[chữ](url)`, ảnh `![..](..)`, khai báo `[ref]: url` đều bị bỏ địa chỉ, giữ chữ (`sanitize.py:61-72`). Test `tests/test_sanitize.py` (19 hàm test, 58 trường hợp). |
| (b) `ui.highlight()` escape văn bản và câu tô trước khi chèn `<mark>` | **Đã làm** | `ui.py:56-81`: `html.escape(text, quote=False)` cho cả bài lẫn từng câu; thay thế trong **một lượt** regex nên không tô nhầm vào thẻ vừa chèn; chuỗi rỗng bị bỏ qua. Test `tests/test_ui_escape.py` (20 test) và `tests/test_safety.py::test_highlight_escapes_ai_text` (4 mẫu). |
| (c) Test: AI giả trả `<script>`, `<img onerror>` → trang không dựng thẻ, bài trong session không còn thẻ | **Đã làm** | `tests/test_content_edge_cases.py::test_html_in_ai_article_is_not_rendered_as_html` (đã gỡ `xfail`), `tests/test_ui_escape.py:113-138` (hai test `AppTest` **đi vòng qua lớp 1**: dán HTML vào ô Sửa, đặt thẳng chữ độc vào session). |
| (d) Bộ lọc HTML theo 2.3 trước khi gửi WordPress | **Đã làm sớm** (phiếu yêu cầu, không chờ Giai đoạn 5) | `client.py:214-227`: `create_draft` luôn gọi `sanitize_html` cho `content`/`excerpt`, `strip_tags` cho `title`; không có tham số tắt. `sanitize.py:82-215`: danh sách cho phép, dùng `html.parser` chuẩn. Test `tests/test_safety.py::test_html_sent_to_wordpress_is_sanitized`, `tests/test_sanitize.py:240-264`. |

Cách tôi thử lách (script tạm trong scratchpad, không mạng; không sửa code/test):

- **`strip_tags` / `clean_ai_text`** (31 mẫu): thẻ không đóng `<img … onerror=…` → `< img …` (trình duyệt coi là chữ); `>` trong thuộc tính `<img src="a>b" onerror=…>` → còn lại chữ `b" onerror=…>` không có `<`; `<scr<script>ipt>` → `< scr`; `<svg/onload>`, `<math>`, `<style>`, `<?php ?>`, CDATA, comment lồng `<!--<script>-->` → sạch; `&lt;script&gt;` giữ nguyên (chỉ là chữ, sẽ hiện nguyên văn); link `[x](javascript:…)`, `[x](<javascript:…>)`, `[x](url "title")`, URL có ngoặc, autolink `<https://…>`, link tham chiếu → chỉ còn chữ. **Không mẫu nào để lại `<` đứng trước chữ cái.**
- **`sanitize_html`** (83 mẫu): `onerror`/`ONERROR`/`onmouseover`/`style` bị bỏ; `javascript:` dưới mọi dạng (hoa-thường, `&#106;`, `&amp;#106;`, tab, `&#9;`, khoảng trắng đầu, `&colon;`, `\x01`, ` `, `\x00` giữa chữ, `data:`, `vbscript:`) đều bị bỏ `href`; `srcset` có `javascript:` ở bất kỳ vị trí → bỏ; hai `href` (một tốt một xấu) → chỉ giữ cái đầu; `<a/href=…>`, `<p/onclick=…>` → thuộc tính bị bỏ; `<svg>`, `<math>`, `<form>`, `<textarea>`, `<noscript>`, `<title>`, `<xmp>`, `<plaintext>`, `<base>`, `<meta refresh>`, `<object>`, `<embed>` → bỏ cả ruột; `<script>` lồng/thiếu đóng/`</script foo>`/`\n-->` → không còn script; chữ `a < b > c`, `1 <3` → `&lt;`/`&gt;`; `alt="&quot; onerror=&quot;…"` → được escape lại đúng; thẻ không cân `<p><b>x<i>y</p>z` → tự đóng đủ. **Không mẫu nào để lại thẻ hoặc thuộc tính ngoài danh sách cho phép.** Vì bộ lọc **tạo lại HTML từ đầu** (chữ luôn `html.escape`, tên thẻ chỉ lấy từ danh sách, giá trị thuộc tính `escape(quote=True)`), khác biệt cách đọc giữa `html.parser` và trình duyệt chỉ có thể làm **mất** nội dung, không tạo được thẻ thật.
- **`highlight`** (19 mẫu): câu tô chứa HTML, câu tô là `<mark>`, câu tô cắt ngang thực thể (`a&lt;b` với câu `lt;b` → `a&amp;<mark>lt;b</mark>`, chỉ là chữ), câu chồng lấn/lồng nhau, câu rỗng, câu nhiều dòng, câu có dấu nháy. Sau khi bỏ các thẻ `<mark class="tone|missing">`/`</mark>` do hàm tự thêm, **không còn ký tự `<` hay `>` nào** trong kết quả.
- **Hiệu năng** (xem lỗi #1 bên dưới).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp | Hai regex trong lớp lọc 1 chạy bậc hai với đầu vào xấu: `_DANGEROUS_BLOCK` (thẻ mở nguy hiểm lặp nhiều lần mà không đóng) và `_MD_LINK` (nhiều `[` liên tiếp). Đo được: `<script>`×20 000 (160 KB) mất 15,6 s, ×60 000 mất 138 s; `[`×100 000 mất 63 s. `sanitize_html` (`html.parser`) không bị: 8 mẫu dị dạng 100–200 KB đều < 0,5 s. | `seo_app/sanitize.py:30-33`, `:41`, vòng lặp `:52-57`, `:67-71` | Trang đối thủ cài lệnh → AI trả về bài dài tối đa (bước viết cho phép tới 32 000 token, `config/ai.toml:27`, ≈ 100 KB) toàn thẻ `<script>` không đóng → `clean_draft` chạy vài chục giây → **app treo trên máy chủ dự án** (chỉ máy mình, không lộ gì, bấm tải lại là hết). Chưa có đường đi nào để người lạ đưa chuỗi dài vào hàm này ngoài qua AI. | Trong `strip_tags`, bỏ regex `_DANGEROUS_BLOCK` + vòng `while`, dùng cùng `html.parser` như `sanitize_html` nhưng ở chế độ "chỉ giữ chữ" (mọi thẻ đều bỏ, thẻ nguy hiểm bỏ cả ruột) rồi `_TAG_OPEN.sub` một lần; hoặc đơn giản hơn: chặn độ dài đầu vào (ví dụ > 200 000 ký tự thì cắt và báo). Với `_MD_LINK`, đổi `[^\]\n]*` thành không cho phép `[` lồng (`[^\[\]\n]*`). Thêm test đo thời gian < 1 s với `<script>`×20 000. Gộp vào T-006. |
| 2 | Thấp | `is_safe_url` coi `//evil.example` và `/\evil.example` là đường dẫn tương đối nên cho qua; trình duyệt hiểu cả hai là link ra ngoài tới `evil.example` (cùng giao thức). Không nguy hiểm hơn link `https://` vốn được phép, nhưng `/\evil.example` nhìn như link nội bộ, dễ qua mắt người duyệt ở Giai đoạn 5 (2.3: link ra ngoài phải được người dùng nhìn thấy). | `seo_app/sanitize.py:109-116` (chỉ chặn `\\` ở đầu) | Chỉ xảy ra khi HTML gửi WordPress có sẵn `<a href="/\evil">` — hiện bài AI đã bị bỏ hết link ở lớp 1, nên đường đi thật chỉ còn qua chữ người dùng tự dán ở Giai đoạn 5. | Trong `is_safe_url`, với URL không có scheme: trả `False` nếu `compact` bắt đầu bằng `//`, `/\`, `\/` hoặc `\\` (chỉ cho `/đường-dẫn`, `#muc`, `?q=`, `tên-file`). Thêm 3 trường hợp vào test `test_is_safe_url_blocks`. Gộp vào T-006. |
| 3 | Thấp | Lớp lọc 1 còn sót: khi AI trả `Draft.title` rỗng, tiêu đề lấy từ `outline.title` chưa qua `strip_tags`; `Research` (tên/URL/nhận xét đối thủ) và `Outline` (tiêu đề mục, ý chính) chưa lọc ở ranh giới AI (Thợ Máy đã tự nêu). **Đã được lớp 2 che kín**: tiêu đề hiển thị qua `html.escape` (`write.py:530`), nghiên cứu/dàn ý hiển thị bằng `st.markdown` không `unsafe_allow_html` (`write.py:293-306`), tiêu đề gửi WordPress qua `strip_tags` (`client.py:214`). | `seo_app/content/workflow.py:141`, `:128`, `:132` | Không có đường đi tới hậu quả hôm nay. Rủi ro là người sau dùng `S.research`/`S.outline` ở chỗ mới có `unsafe_allow_html`. | `title = strip_tags(draft.title or outline.title).strip()` trong `write`; thêm `clean_outline`/`clean_research` (strip_tags từng trường chuỗi) gọi ở `outline()`/`research()`. Gộp vào T-006 cùng đề xuất của Thợ Máy. |
| 4 | Thấp | Thẻ nguy hiểm **không đóng** làm mất toàn bộ phần sau nó; riêng `input`, `button`, `select`, `option`, `base`, `link`, `meta`, `embed` trong `DANGEROUS_TAGS` không nằm trong `VOID_TAGS`, trong đó `input`/`base`/`link`/`meta`/`embed` là thẻ **không bao giờ có đóng** trong HTML, nên `<input><p>x</p>` → kết quả rỗng. Hướng an toàn (mất chữ, không chạy mã), nhưng kẻ cài lệnh có thể làm bài gửi lên WordPress thành rỗng; người dùng thấy được vì bài trống. | `seo_app/sanitize.py:18-26`, `:148-156` | Chữ chứa `<input>` hoặc `<iframe …>` thiếu đóng → `create_draft` gửi nội dung cụt. Hiện bài AI qua lớp 1 đã bỏ sẵn các thẻ này nên chỉ còn đường qua chữ người dùng dán (Giai đoạn 5). | Trong `_start`: nếu `tag in {"input","base","link","meta","embed","frame"}` thì chỉ bỏ thẻ (không đặt `skip_tag`). Giữ nguyên cách xử lý cho `iframe`/`script`/… vì chúng có ruột. Thêm test `<input><p>x</p>` → `<p>x</p>`. Gộp vào T-006. |
| 5 | Thấp (ghi nhận) | Python trong môi trường cloud là 3.12.3, chưa có vá CVE-2025-6069 (`html.parser` chạy bậc hai với một số đầu vào dị dạng; vá ở 3.12.11). Tôi không tái hiện được bằng 8 mẫu dị dạng; và như phân tích ở trên, bộ lọc tạo lại HTML từ đầu nên khác biệt cách đọc không tạo được thẻ. `.python-version` ghi `3.12` nên uv trên máy người dùng sẽ cài bản vá mới nhất. | `.python-version`, `pyproject.toml:6` | Không có đường đi thật. | Khi tiện, ghi `3.12.11` (hoặc mới hơn) vào `.python-version` để cả cloud lẫn máy người dùng cùng bản có vá. |

Không phát hiện lỗi nào trong phần của **T-005** (`seo_app/ui.py`, các `unsafe_allow_html` trong `app/`).

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | **Đạt** | Diff và 6 file mới (code, test, hai báo cáo) không có chuỗi giống khóa (grep `sk-ant-`, `AIza`, `AKIA`, `PRIVATE KEY`, `pbkdf2_sha256:`, `api_key=`). `detect-secrets` chỉ báo `tests/test_ui_escape.py:15` là mật khẩu giả của test (xem "Báo nhầm"). Thay đổi chưa commit nên không ảnh hưởng lịch sử git. |
| S2 | **Đạt** | Diff không thêm chỗ in lỗi/log nào. `WordPressError` mới duy nhất là "Tiêu đề bài viết không được để trống" (`client.py:216`), không chứa dữ liệu. `score_panel` chỉ chèn số nguyên (`ui.py:31-40`). |
| S3 | Không áp dụng | Không có biến cấu hình mới (`.env.example` không đổi). |
| W1 | **Đạt** | `create_draft` vẫn ghi cứng `"status": "draft"` (`client.py:218`); diff không có chữ `publish`/`future` (grep). Test `tests/test_safety.py` và `tests/test_wordpress_client.py` không đổi về điểm này. |
| W2 | **Đạt** | Không thêm request `PUT`/`DELETE`; `create_draft` vẫn chỉ `POST /wp/v2/posts` (`client.py:232`). |
| W3 | **Đạt** | `create_draft` luôn lọc `content`/`excerpt` bằng `sanitize_html`, `title` bằng `strip_tags`, không có tham số tắt (`client.py:214-227`). Bộ lọc đúng danh sách 2.3: bỏ `script/iframe/object/embed/form/style` và cả ruột (`sanitize.py:19-26, 153-156`), bỏ mọi thuộc tính ngoài danh sách (`on*`, `style`, `target`… `:131-146`), bỏ `javascript:`/`data:` và mọi scheme ngoài `http/https/mailto/tel` (`:103-116`), kể cả viết lắt léo (`:106, 111`). 83 mẫu lách thử đều sạch. Ghi chú: 2 điểm Thấp (#2, #4). |
| W4 | Không áp dụng | Diff không đụng tới `requests`, `timeout`, `verify`, URL (grep). Lỗi #4 của T-001 (bắt buộc `https://`) thuộc T-006, chưa làm. |
| A1 | Không áp dụng | Không sửa prompt (`seo_app/content/prompts.py` không đổi). Lỗi #2 của T-001 thuộc T-003. |
| A2 | **Đạt** | AI vẫn không có công cụ hành động (không đổi `seo_app/ai/`). Kết quả AI giờ được kiểm tra **nội dung** chứ không chỉ kiểu: bài, phần viết lại, câu thay thế, lý do, nhận xét đều qua `clean_ai_text`/`strip_tags` trước khi vào session (`workflow.py:28-51, 138, 145, 177`); `Flag.sentence` không lọc nhưng chỉ được giữ khi có thật trong bài đã lọc (`workflow.py:80-87`). Sót nhỏ: `outline.title` fallback, `Research`/`Outline` (lỗi #3, đã được lớp hiển thị che). |
| A3 | Không áp dụng | Không đổi dữ liệu đưa vào prompt. |
| U1 | **Đạt** | Rà đủ 9 chỗ (8 `unsafe_allow_html=True` + 1 `st.html`), khớp bảng của Họa Sĩ: `ui.py:15` escape; `home.py:41-46` escape + `progress_dots` chỉ chèn số (`ui.py:23-25`); `home.py:52-55` escape `note`, `updated` là hằng demo (phải escape khi dùng dữ liệu thật — Họa Sĩ đã ghi); `write.py:397-401` nhãn cố định + `int` + escape tiêu đề mục; **`write.py:462`** → `highlight` escape toàn bộ, chỉ thêm `<mark class="tone|missing">` cố định (`ui.py:56-81`); `write.py:474` → `score_panel` chỉ chèn `int` đã kẹp 0–100 và escape tên tiêu chí (`ui.py:28-45`); `write.py:530` escape; `write.py:565-568` → `serp_preview` escape cả ba (`ui.py:48-53`); `main.py:64` CSS cố định trong repo. Các chỗ hiển thị khác của chữ AI (`write.py:293-306, 496-499, 519-520`) dùng `st.markdown`/`st.caption` không `unsafe_allow_html` nên Streamlit tự escape. Đã xác minh trực tiếp bằng 19 mẫu trên `highlight` (không còn `<`/`>` ngoài `<mark>`) và hai test `AppTest` đi vòng qua lớp 1 (`tests/test_ui_escape.py:113-138`). Ghi chú (không phải lỗi, Họa Sĩ đã nêu): escape không chặn **cú pháp Markdown**, nên chữ người dùng dán có `[x](https://lạ)` vẫn thành link thường; `javascript:`/`data:` bị Streamlit tự bỏ (test `test_competitor_javascript_link_is_not_rendered`). |
| U2 | Không áp dụng | Không đổi `app/main.py`, `.streamlit/config.toml`. |
| U3 | Không áp dụng | Không đổi `seo_app/auth.py`. |
| F1 | Không áp dụng | Diff không có `open(`/`Path(` nhận đường dẫn ngoài (grep). |
| F2 | Không áp dụng | Không đụng ảnh/EXIF. (GPS giữ nguyên theo sổ rủi ro mục 6 — không coi là lỗi.) |
| F3 | **Đạt** | Không có `eval`/`exec`/`pickle`/`subprocess` trong file mới (bandit 0 cảnh báo); `sanitize.py` chỉ dùng `html`, `re`, `html.parser`. Không đọc/ghi file. |
| D1 | **Đạt** | Không thêm thư viện: `pyproject.toml`, `uv.lock` không đổi (`git diff HEAD --stat` trống); bộ lọc dùng thư viện chuẩn đúng yêu cầu phiếu. `pip-audit` trên 153 gói xuất từ `uv.lock`: 0 lỗ hổng đã biết. |
| D2 | **Đạt** | `.gitignore` không đổi. |
| D3 | **Đạt** | `tests/test_sanitize.py`, `tests/test_ui_escape.py`: không `import requests/socket/urllib`; AI giả bằng `FakeProvider`, WordPress giả bằng `fake_wp` fixture (`test_sanitize.py:240-264`, `test_ui_escape.py:95`); các URL `https://evil.example` chỉ là chuỗi trong dữ liệu test, không được gọi. Fixture chặn mạng của T-002 trong `tests/conftest.py` vẫn còn hiệu lực. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt` (153 dòng, đúng `uv.lock`) → `uvx pip-audit -r … --no-deps`: **No known vulnerabilities found**. `uv.lock` không đổi so với T-001. | Có |
| bandit | `uvx bandit -r seo_app/sanitize.py seo_app/ui.py seo_app/content/workflow.py seo_app/wordpress/client.py`: 705 dòng, **0 cảnh báo** (mọi mức). | Có |
| detect-secrets | `uvx detect-secrets scan` trên 4 file code đổi + 2 test mới + 2 báo cáo: 1 cảnh báo "Secret Keyword" ở `tests/test_ui_escape.py:15` — báo nhầm (bên dưới). | Có |
| Soát lịch sử git | Thay đổi chưa commit, lịch sử git không đổi so với T-001 (HEAD `ce73f97`, các commit sau `90728a7` chỉ là tài liệu/phiếu/test). Grep mẫu khóa trên diff + file mới: sạch. | Có |
| pytest / ruff | `uv run pytest --ignore=tests/test_sanitize_bypass.py`: **252 passed, 9 xfailed** (17,6 s; 9 `xfail` là lỗi khác của T-002 chưa sửa). `uv run ruff check .`: **All checks passed**. Ba test mục tiêu của phiếu (`test_highlight_escapes_ai_text`, `test_html_in_ai_article_is_not_rendered_as_html`, `test_html_sent_to_wordpress_is_sanitized`) đã bỏ `xfail` và đang xanh. | Có |
| Thử lách thủ công | Script tạm (không mạng, chạy `python -I`): 31 mẫu `clean_ai_text`, 83 mẫu `sanitize_html`, 25 mẫu `is_safe_url`, 19 mẫu `highlight`, 11 mẫu đo thời gian. Không tạo được thẻ/thuộc tính thật; phát hiện lỗi #1, #2. | Có |

## Báo nhầm đã loại

| Công cụ | Cảnh báo | Lý do loại |
|---|---|---|
| detect-secrets | `tests/test_ui_escape.py:15` — `PASSWORD = "mat-khau-thu-123"` | Mật khẩu giả để tạo mã băm tạm trong test `AppTest`, giống các file test đã có (T-001 đã loại cùng lý do). |
| Thử lách | `<a href="https://ok?a=1&b=2">` → `&amp;b=2`; `<ol start="javascript:alert(1)">` được giữ | Đúng chuẩn HTML (`&` trong thuộc tính phải là `&amp;`); `start` là thuộc tính số, trình duyệt bỏ qua giá trị không phải số, không thực thi. |
| Thử lách | `is_safe_url("javascript\xa0:x")`, `("javascript　:x")`, `("İavascript:x")` trả `True` | Trình duyệt không bỏ NBSP/khoảng trắng Unicode/chữ Thổ khi đọc scheme → các chuỗi này là đường dẫn tương đối, không chạy mã. Bộ lọc bỏ `\x00-\x20` ở mọi vị trí còn chặt hơn trình duyệt. |
| Thử lách | `strip_tags("a <b")` → `a < b`; `<img src="a>b" …>` → còn chữ `b" onerror=alert(1)>` | Chỉ là chữ (không có `<` trước chữ cái); khi hiển thị được escape, khi gửi WordPress đi qua `sanitize_html`. Thợ Máy đã ghi nhận điểm `a< b` là đổi chữ nhỏ. |

## Điều kiện

**T-004 và T-005: ĐẠT, không có điều kiện.** Bốn lỗi Thấp (#1–#4) ghi vào sổ rủi ro và đề nghị Chỉ Huy gộp vào **T-006** (Thợ Máy, sửa lỗi nhỏ Giai đoạn 2); #5 ghi nhận.

**T-001 (mốc gốc) chuyển thành ĐẠT CÓ ĐIỀU KIỆN** vì lỗi #1 (Cao) đã sửa; các điều kiện còn lại không đổi so với biên bản T-001:

| Lỗi T-001 | Phiếu | Trước mốc |
|---|---|---|
| #2 (TB) tách dữ liệu ngoài khỏi chỉ thị trong prompt | T-003 (Ngòi Bút) | Hết Giai đoạn 2 |
| #3 (TB) EXIF/GPS | **Đã đóng**: chủ dự án quyết định giữ GPS (sổ rủi ro mục 6, T-007 hủy). Phần còn lại của #3 (giới hạn kích thước ảnh, kiểm tra định dạng thật) chuyển sang Giai đoạn 3. | Giai đoạn 3 |
| #4 (TB) bắt buộc `https://` | T-006 | Hết Giai đoạn 2 |
| #5 (TB) test không đọc `.env` thật | T-006 (mục 5 đã được duyệt) | Hết Giai đoạn 2 |
| #6, #7, #8 (Thấp) | T-006 / sổ rủi ro | Không bắt buộc |

Nhắc cho Giai đoạn 5 (đã ghi ở T-001, nay cụ thể hơn sau T-004): khi nối nút "Gửi sang WordPress", Markdown của bài phải được chuyển sang HTML bằng code có escape **rồi mới** vào `create_draft` (tự lọc); link nội bộ do app gắn **sau** `clean_ai_text` (vì lớp 1 bỏ mọi link Markdown); và màn hình xác nhận phải liệt kê mọi link ra ngoài còn lại trong HTML cuối (kể cả dạng `//…`, lỗi #2).

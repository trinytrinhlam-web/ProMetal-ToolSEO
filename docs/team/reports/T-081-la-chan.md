# Biên bản bảo mật T-081 · Bỏ dấu «\» sót ở alt, chú thích ảnh AI (SL-T071-1) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-081](../tickets/T-081-dau-gach-cheo-alt-anh-ai.md), kèm điều kiện 1 của [Lá Chắn T-071](T-071-la-chan.md) (SL-T071-1) |
| Phạm vi | Rút gọn: W3 (mục 2.3), A3 theo mặc định. Diff `1d1e53e..team/T-081` (gốc `1d1e53e`, đầu nhánh lúc kiểm `d78725e`). Code ứng dụng chỉ có `seo_app/images/alt.py` (+9/−0: hằng `_LINK_ESCAPES` `:363`, 2 dòng `:391-392`, còn lại là chú thích); test: `tests/test_t081_alt_gach_cheo.py` (mới, 48 ca), `tests/test_soi_loi_t081.py` (mới, 126 ca), `tests/test_soi_loi_t071.py` (−5 dòng dấu `xfail`); 2 báo cáo. Kèm cả đường đi của chữ: `clean_suggestion` → `_one_line` (`normalize_meta`, `clean_ai_text`) → `_strip_ai_prefix` → `clean_alt_text` → `_with_prefix` → chữ lưu trong nháp (cả đường mở lại nháp `drafts._ai_prefixed`) → `plain_image_text` → `figure_html` / `_plan_draft_images` → `_describe_draft_media` → REST (`<img alt>`, `<figcaption>`, `alt_text`, `title`, `caption`). `origin/main` lúc bắt đầu: `367c3bf`; lúc kết thúc: `bbb55dc` (đã gộp T-080) |
| Ngày | 2026-10-23 (14:30–15:15 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 lỗi mới của Lá Chắn**. SL-T081-1 của Soi Lỗi (có từ T-062): đồng ý **Thấp**, không có hệ quả bảo mật, sửa ở **T-083** (đã lập, sau T-056) như chủ dự án đã duyệt. **SL-T071-1 đóng** (điều kiện 1 của Lá Chắn T-071). **Gộp `main` được ngay** |

## Tóm tắt (cho chủ dự án)

- **An toàn.** Bản sửa chỉ bỏ đúng một dấu «\» thừa ngay sau tiền tố «[Minh họa]» mà AI tự viết. Mọi dấu «[» «]» vẫn được đổi thành mã ký tự trước khi gửi website, nên không đoạn lệnh WordPress (shortcode) nào chạy được; link, thẻ HTML vẫn bị bỏ. Tôi tự thử gần 150.000 chuỗi độc đặt ngay sau tiền tố (đoạn lệnh, link, `<script>`, ký tự vô hình, ngoặc lồng 4 lớp): không chuỗi nào lọt, nhãn «Minh họa» của ảnh AI luôn còn.
- Câu kỳ lạ kiểu «[Minh họa]: [Lưu ý]: Cửa» nay báo «AI không viết được alt…, bấm thử lại»: an toàn (không gửi gì lên website, câu báo cố định, không chép chữ AI).
- Lỗi nhỏ có từ trước «(AI): (AI)» lặp chữ trong chú thích không ảnh hưởng an toàn; để phiếu dọn T-083 sau màn hình chọn ảnh như chủ dự án đã duyệt. Gộp vào `main` được ngay.

## Lỗi phát hiện

Không phát hiện lỗi mới (không có mã LC-T081, không thêm file test).

Đánh giá lỗi của Soi Lỗi:

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| SL-T081-1 | **Thấp** (đồng ý), có từ T-062, ngoài phạm vi | AI viết «(AI)» tách khỏi tiền tố («[Minh họa] (AI): …», «**Ảnh minh họa** (AI): …», «Minh họa: (AI) …») thì chú thích ra «Ảnh minh họa (AI): (AI): …», alt «Minh họa (AI): …»; chạy lại `clean_suggestion` đổi chữ | `seo_app/images/alt.py:347-350` (`_AI_PREFIX` chỉ nhận «(AI)» liền sau), `:379-395` | AI viết «[Minh họa] (AI): Cổng inox 2 cánh» → người dùng duyệt → chú thích công khai lặp «(AI): (AI)». **Không có hệ quả bảo mật:** phần «(AI)» thừa đi qua cùng lớp lọc như mọi chữ khác (bộ thử E2–E4: 0 «[» «]» trần, 0 thẻ lạ); nhãn ảnh AI không mất mà còn lặp (C7: alt luôn mở đầu «Minh họa», chú thích luôn mở đầu «Ảnh minh họa (AI)», quy tắc C6 của Lá Chắn T-051) | Theo gợi ý của Soi Lỗi, ở **T-083** (đã lập, gồm cả SL-T068-1 → -3, LC-T068-1): sau khi bỏ tiền tố, ngoặc, dấu câu, nếu phần còn lại mở đầu «(AI)» thì bỏ luôn rồi lại bỏ dấu câu; giữ C1–C7 ở mục Thử độc lập (Điều kiện 1) |

## Kiểm lại lỗi cũ

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| SL-T071-1 (điều kiện 1 của Lá Chắn T-071) · alt, chú thích ảnh AI còn «\» khi AI viết «[Minh họa]: …» | **Đóng** | Đúng cách 1 của phiếu: `_strip_ai_prefix` bỏ ngoặc đóng tận cùng «]» mà ngay sau là `\:`, `\[`, `\(` thì bỏ luôn «\» (`alt.py:391-392`); đây đúng là 3 chỗ `escape_link_syntax` thêm «\» (`sanitize.py:542-546`). Tái hiện lại E7 của biên bản T-071 trên nhánh: «[Minh họa]: Cổng inox 2 cánh» → `alt="Minh họa cổng inox 2 cánh"`, `<figcaption>Ảnh minh họa (AI): cổng inox 2 cánh</figcaption>` (bản `main`: `Minh họa \: Cổng…`); dạng «[» có shortcode «[Minh họa][code_snippet id=1] sơn» → `alt="Minh họa &#91;code_snippet id=1&#93; sơn"` (bản `main`: `Minh họa \&#91;code_snippet…`), shortcode vẫn vô hiệu. Gỡ `xfail`: `git diff 1d1e53e..team/T-081 -- tests/test_soi_loi_t071.py` chỉ xóa 5 dòng `@pytest.mark.xfail(strict=True, reason=…)`, thân và tham số giữ nguyên (R5); 2 ca qua. Lớp vô hiệu «[» «]» của T-061 không bị nới (W3) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có khóa, mật khẩu (detect-secrets, soát lịch sử: mục Công cụ). Test mới chỉ dùng mật khẩu giả của site giả (`tests/conftest.py:235`) |
| S2 | Đạt | Câu lỗi duy nhất trên đường mới là `EMPTY_ALT_MESSAGE` cố định (`alt.py:65`, `:451`): `str(exc)` đúng câu đó, `exc.args` chỉ có câu đó, `__cause__`/`__context__` rỗng; chuỗi mồi trong chữ AI (một chuỗi giả trông như khóa API, một địa chỉ lạ) không có trong `repr(exc)` (E5) |
| S3 | Không áp dụng | Không thêm biến cấu hình; `.env.example` không đổi |
| W1 | Đạt | Không sửa `seo_app/wordpress/**`. 1.566 lần gửi nháp kèm ảnh AI qua client (site giả, E3): trường `status` duy nhất trong mọi JSON là `draft` |
| W2 | Đạt | Không sửa client; không lệnh xóa, ghi đè. Ảnh alt rỗng (đường AIError mới, hay alt bị xóa khi mở lại nháp) bị chặn trước mọi lệnh: `WordPressError` «Ảnh thứ 1 chưa có alt…», **0 lệnh** (E5) |
| W3 | Đạt | Mục «W3 / 2.3» bên dưới |
| W4 | Đạt | `client.py` không đổi (`git diff --stat`: chỉ `alt.py` trong `seo_app/`); SSL, timeout, `https://` giữ nguyên |
| A1 | Không áp dụng | Không đổi prompt: `alt_prompt`, `alt_instructions`, `ALT_SYSTEM` không nằm trong diff |
| A2 | Đạt | Chữ AI vẫn là dữ liệu chưa tin cậy: bỏ «\» xong, phần thân được lọc lại toàn bộ (`clean_alt_text` → `clean_ai_text`: bỏ thẻ, bỏ link, `escape_link_syntax`, `alt.py:448-449`), ghép tiền tố rồi lọc lần nữa (`_with_prefix`, `:419`). AI không có công cụ (`suggest_alt` tắt `web_search`, `:485-487`, không đổi) |
| A3 | Đạt (không đổi) | Phiếu ghi A3 theo mặc định. Không đổi dữ liệu gửi AI (ảnh qua `prepare_images`, thẻ, từ khóa: `suggest_alt` `alt.py:481-500` không nằm trong diff); phần sửa chỉ chạy **sau** khi AI trả lời |
| U1 | Không áp dụng | Không sửa `app/`; không `unsafe_allow_html`. Chữ lưu (hiện trên Streamlit ở T-056) không có link, thẻ: E2 (markdown-it) |
| U2 | Không áp dụng | Không trang mới; `.streamlit/` không đổi |
| U3 | Không áp dụng | Không đụng mật khẩu đăng nhập app |
| F1 | Không áp dụng | Phần sửa không mở file, không nhận đường dẫn |
| F2 | Không áp dụng | Không đụng byte ảnh, EXIF, giới hạn ảnh |
| F3 | Đạt | Phần thêm không `eval`, `exec`, `pickle`, `yaml`, `subprocess`, `open(` (grep phần thêm của diff `seo_app`: 0) |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` giống gốc (`git diff --quiet`). pip-audit: 0 lỗ hổng |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới dùng `FakeWordPress` (fixture `fake_wp`, `wp_client`); bộ chặn mạng tự bật (`tests/conftest.py:18-19`); `tests/test_t081_alt_gach_cheo.py`, `tests/test_soi_loi_t081.py` không có `requests.get/post/Session`, `urlopen`, `socket`, `http.client`, client AI thật (grep: 0). Thử độc lập của Lá Chắn chỉ dùng site giả và phiên `requests` gắn bộ chuyển giả |

### W3 / mục 2.3: bỏ «\» không mở lại link, thẻ, shortcode

- **Cấu trúc:** phần sửa chỉ xóa đúng một ký tự «\» trong chữ đã lọc một lượt, ở đúng chỗ ngay sau ngoặc đóng «]» của tiền tố vừa bỏ (`alt.py:391-392`). Sau đó phần thân **luôn** được lọc lại (`clean_alt_text`, `alt.py:448-449`) rồi ghép tiền tố và lọc lần nữa (`_with_prefix`, `:419`), nên chữ lưu không thể còn link, thẻ hay cú pháp link sống, dù việc bỏ «\» làm «[», «(» của phần thân đứng trần. Lớp vô hiệu ở bước in ra **không đổi** (diff chỉ `alt.py`): `plain_image_text` (`html.py:66-80`) → `html.escape` → `sanitize_html` → `escape_shortcodes` cho `<img alt>`, `<figcaption>` (`sanitize.py:726`, `:770`); `escape_shortcodes` cho `alt_text`, `escape_shortcodes(html.escape(…))` cho `title`, `caption` (`client.py:1205-1209`). Vòng lặp vẫn luôn dừng: mỗi vòng bỏ ít nhất 8 ký tự («minh họa»), dòng mới chỉ bỏ thêm 1 ký tự.
- **Chuỗi độc ngay sau tiền tố** (E2, E3): 19 dạng tiền tố (5 dạng của phiếu, ngoặc lồng 2–4 lớp, `[*…*]`, `[«…»]`, `*[…]*`, `«[…]»`, `([…])`, ký tự rộng 0 trong ngoặc, tiền tố lặp) × 27 cách nối (`:`, `\:`, `\\:`, `[`, `(`, `\[`, `\(`, `]:`, ký tự rộng 0, U+202E, BOM, gạch nối mềm, NBSP, U+3000, xuống dòng, U+2028, U+0085, tab) × 58 chuỗi độc (`[code_snippet id=1]`, `[[code_snippet id=1]]`, `[/code_snippet]`, `[embed]https://…[/embed]`, `[caption]<img onerror>[/caption]`, `[gallery]`, `[contact-form-7]`, tên chen ký tự rộng 0 hay thẻ `<b>`, `[<>code_snippet]`, `&#91;…&#93;`, `&#x5b;`, `&lsqb;`, ngoặc toàn khổ, link Markdown thường, `javascript:`, ảnh Markdown, link tham chiếu và dòng khai báo, `<https://…>`, địa chỉ trần, email, `<script>`, `<img onerror>`, `<a href=javascript:>`, `<iframe>`, `<svg onload>`, thẻ lồng, `<` + ký tự rộng 0, dấu nháy phá thuộc tính, `\`, `\\`, `%%sitename%%`…) × 3 phần thân = **89.262 chuỗi**: mọi kiểm C1–C4, C7 (mục Thử độc lập) **0 vi phạm**; gửi thật qua client 1.566 lần (tiền tố «[Minh họa]» × mọi cách nối × mọi chuỗi độc): mọi chuỗi JSON không có «[» «]» trần, ký tự Cf, «\» lạ; trang chỉ có `figure`, `img`, `figcaption`.
- **Thử ngẫu nhiên** (E4, hạt giống 81811, 60.000 chuỗi; 1–3 tiền tố, 80% ngoặc cân, rồi 0–7 mảnh độc): **0 vi phạm**. Đối chứng: bản `main` để «\» lọt ra chữ gửi đi ở 3.357 chuỗi không có «\» đầu vào; bản mới 0.
- **Giả lập LC-T061-4** (trình soạn thảo WordPress giải mã `&#91;` thành `[` khi người sửa bài lưu lại; rủi ro Thấp đã ghi ở T-061, T-056 cảnh báo): chạy biểu thức shortcode của WordPress (`get_shortcode_regex`, có xét `[[…]]` đã thoát) trên chữ đã giải mã từng trường (alt, chú thích, tiêu đề Media), so bản mới với bản `main`. Với danh sách shortcode thật (`caption`, `code_snippet`, `embed`, `gallery`, `audio`, `video`, `playlist`, `contact-form-7`…): **0 trường** bản mới chạy được nhiều hơn bản `main`, 0 ca từ `[[…]]` (đã thoát) thành chạy được; tổng số lần chạy được bản mới 26.934, bản `main` 26.946 (60.000 chuỗi ngẫu nhiên). Bộ chuỗi độc (79.031 cặp không lỗi ở cả hai bản): cũng **0 trường**. Dấu «\» chưa bao giờ là lớp chặn: bộ đọc shortcode của WordPress không hiểu «\» (thoát bằng `[[…]]`), như biên bản T-071 đã ghi.

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, `uv` 0.13.4, worktree `wt-T-081`, nhánh `team/T-081` tại `d78725e`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` (69 gói, có `certifi==2026.10.19`, `pillow==13.0.0`, `requests==2.34.2`, `urllib3==2.8.0`, `anthropic==1.13.0`) → `uvx --offline pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có. `uv.lock` không đổi so với gốc |
| bandit 1.9.4 | `seo_app/images/alt.py` (396 dòng code): **No issues identified** | Có |
| detect-secrets 1.5.0 | **`PYTHONUTF8=1`**, `--all-files` trong thư mục nháp riêng: 6 file của diff, patch cả nhánh, 1 file mồi có chữ tiếng Việt (khóa AWS giả, dòng gán mật khẩu giả): bắt **đủ 2/2 mồi, 0 mục khác**. Quét lại biên bản này và các script thử trước khi commit (cùng cách, cùng mồi): mồi 2/2, biên bản **0 mục**, script `lc81_aierror.py` 1 mục (xem Báo nhầm). Đã xóa mồi cả hai lần | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p 1d1e53e..team/T-081 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 2 dòng, đều là câu báo cáo tả cách quét mồi | Có, đọc từng dòng. Không có khóa thật |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest (nhánh) | 11 file lời giao (`tests/test_soi_loi_t071.py tests/test_t081_alt_gach_cheo.py tests/test_soi_loi_t081.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t054.py tests/test_soi_loi_t068.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py tests/test_ai_images.py`), 14:33:39–14:34:40: **1479 passed, 34 xfailed, 0 hỏng** (khớp số Soi Lỗi) | Có. 34 xfail: SL-T081-1 (5, T-083); SL-T068-1 (8), SL-T068-2 (11), SL-T068-3 (4) (T-083); SL-T061-1 (4), SL-T061-2 (2) (T-060). 0 XPASS |
| Gộp với `main` | `git merge-tree --write-tree`: `origin/main` lúc bắt đầu `367c3bf` + `team/T-081` → cây `3599481`, **không xung đột**; cộng `team/T-080` (khi đó sắp gộp, đầu `8869baf`) → cây `02a59e7`, không xung đột. Trong lúc kiểm, Chỉ Huy gộp T-080: `origin/main` = `bbb55dc` + `team/T-081` → cây `217bd0a`, **không xung đột** (khác cây `02a59e7` chỉ ở 8 file tài liệu `docs/team/`). `main` đổi từ gốc `1d1e53e` chỉ ở `seo_app/images/folders.py` và test của T-080, không trùng file nào của T-081. Cây `217bd0a` chép ra thư mục nháp (`git archive`), chạy bằng Python của worktree: 11 file lời giao + `tests/test_drafts_images.py tests/test_storage_drafts.py` (đường mở lại nháp dùng `clean_suggestion`) + `tests/test_soi_loi_t080.py tests/test_images_folders.py` (T-080), 14:58:50–15:00:29: **1971 passed, 12 skipped, 44 xfailed, 0 hỏng** | Có: `seo_app` nạp từ thư mục cây gộp, có `_LINK_ESCAPES` (T-081) và `folders.py` bản T-080 (in ra cuối lượt chạy). 44 xfail: 34 như trên + SL-T080-L-1 (6), SL-T080-1 (3), SL-T080-2 (1) (T-082). 12 bỏ qua đều do máy: symlink (Windows chưa bật Developer Mode), ca chỉ tạo được trên Mac/Linux. 0 XPASS |

## Báo nhầm đã loại

- **detect-secrets:** ở các file của nhánh và biên bản, mục duy nhất là chuỗi mồi tôi tự đặt (đã xóa). Ở script thử `lc81_aierror.py` (ngoài repo), 1 mục «Secret Keyword» là chuỗi giả cố ý đặt vào chữ AI để xem câu lỗi có chép lại không (tên biến `SECRET_LIKE`).
- **Soát lịch sử nhánh:** 2 dòng là câu báo cáo của Thợ Máy, Soi Lỗi tả cách quét mồi.
- **Giả lập LC-T061-4, bản đầu** (lỗi của script, không phải của nhánh): coi **mọi** chữ sau «[» là tên shortcode đã đăng ký (cả «Minh», «“Minh») thì 94/60.000 chuỗi cho kết quả khác bản `main`. Xét từng ca (282 lần khớp ở 3 trường): đều là «khớp khác»: ở bản `main`, cụm «[Minh họa …» (tiền tố AI viết, bản mới bỏ được nhờ hết «\») đứng trước và nuốt cụm phía sau trong cùng một lần khớp; cụm «[tên» chạy được ở bản mới đều có sẵn, chưa thoát, ở bản `main`; 0 ca từ `[[…]]` thành chạy được, 0 tên mới. Với danh sách tên shortcode thật: 0 khác (mục W3).
- **Lỗi script của tôi, đã sửa** (không phải lỗi của nhánh): (a) bản đầu của bộ ngẫu nhiên hiếm khi dựng được ngoặc cân quanh tiền tố (500/500 chuỗi giống `main`), đã sửa cho 80% chuỗi có ngoặc cân rồi chạy lại; (b) vài script tạo bằng heredoc trong Bash bị rút `\\` thành `\`: các chuỗi thử vẫn đúng nghĩa (Python giữ «\» trước ký tự không phải mã thoát), riêng biểu thức xếp loại «lỗi mới» bị sai nên bản đầu xếp nhầm mọi ca «[nhãn]: một-chữ» vào «khác». Đã viết lại các script đó bằng công cụ ghi file, chạy lại; số trong biên bản là của lượt chạy lại.

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục nháp của phiên; bản sao ở thư mục ghi chú chung, `T-081-la-chan-scripts/`), không sửa code ứng dụng; chạy trong worktree bằng `PYTHONUTF8=1 uv run --offline --with markdown-it-py python <script>` (markdown-it-py 4.2.0 lấy từ bộ nhớ đệm của `uv`, không tải mạng, không thêm vào thư viện dự án); `seo_app` nạp từ worktree (script kiểm `__file__`). Bản `main` của `alt.py` lấy bằng `git show 1d1e53e:seo_app/images/alt.py`, nạp thành module riêng. Không dùng lại dữ liệu của Thợ Máy, Soi Lỗi.

Các kiểm trên **mọi** kết quả không lỗi của bản mới:
- **C1** chữ lưu (sẽ hiện trên Streamlit): bất động với `escape_link_syntax` (không cú pháp link sống, địa chỉ trần đã chèn ký tự ngắt), `strip_tags` không đổi gì, markdown-it (CommonMark, bật HTML thô) không dựng ra thẻ nào ngoài `p`, `em`, `strong`, `code`;
- **C2** `figure_html`: chỉ `figure`, `img`, `figcaption`; `<img>` đúng 4 thuộc tính `src`, `alt`, `width`, `height`, `src` đúng; không «[» «]» trần, không ký tự Cf (đảo chiều, rộng 0); chữ trình duyệt đọc ra đúng bằng `plain_image_text`;
- **C3** ô Media dựng như client (`alt_text`, `title` có `[AI] `, `caption`): không «[» «]» trần, không ký tự Cf;
- **C4** chuỗi vào không có «\» thì chữ gửi đi không có «\»;
- **C7** nhãn ảnh AI: alt (cả chữ lưu lẫn chữ gửi đi) mở đầu «Minh họa», chú thích mở đầu «Ảnh minh họa (AI)».

| # | Thử gì | Kết quả |
|---|---|---|
| E1 | Đọc diff, đường đi của chữ (mục Phạm vi); `_strip_ai_prefix` chỉ chạy cho ảnh AI (`alt.py:444-445`) | Phần sửa xóa 1 ký tự rồi lọc lại; lớp in ra không đổi; ảnh thật không đi qua dòng sửa |
| E2 | Bộ chuỗi độc 89.262 chuỗi (mục W3), so bản `main` | C1–C4, C7: **0 vi phạm**. So chữ **gửi đi** với bản `main` (`lc81_khac.py`): giống 61.390; chỉ khác dấu «\» (bản `main` thừa) 9.035; khác thêm dấu «:», khoảng trắng, hoa/thường đầu câu 13.714; bỏ thêm tiền tố AI lặp, ngoặc (bản `main` dừng ở «\» đầu tiên) 4.263; lỗi mới 860 (324 ca alt bản `main` không có chữ mô tả nào, 536 ca thân «[nhãn]: một-chữ hay địa chỉ»: Ghi nhận, E5); hết lỗi 0; **khác loại nào khác: 0**. Có ca dấu «\» chỉ dời chỗ trong chữ lưu (`\[1]:` thành `[1]\:` vì phần thân được escape lại khi đứng đầu dòng), chữ gửi đi vẫn hết «\» |
| E3 | Gửi thật qua `WordPressClient.create_draft_with_images` với site giả: 1.566 lần | Mọi chuỗi JSON: 0 «[» «]» trần, 0 ký tự Cf, 0 «\» lạ; trang chỉ 3 thẻ; `status` chỉ `draft` |
| E4 | Thử ngẫu nhiên 60.000 chuỗi (hạt giống 81811); giả lập LC-T061-4 | C1–C4, C7: **0 vi phạm** (`main`: 3.357 chuỗi lọt «\»). So chữ gửi đi: giống 51.909; chỉ khác «\» 2.423; khác thêm «:», khoảng trắng, hoa/thường 1.621; bỏ thêm tiền tố lặp, ngoặc 2.996; lỗi mới 1.051 (thân chỉ còn tiền tố, ngoặc, dấu, hay «[nhãn]: …» một chữ); khác loại khác 0. Giả lập: 0 trường chạy được nhiều shortcode hơn `main` |
| E5 | Việc 3: «[Minh họa]: [Lưu ý]: Cửa», có chữ mồi giống khóa, địa chỉ, `<script>`; đường mở lại nháp; gửi ảnh alt rỗng | `AIError` đúng câu cố định `EMPTY_ALT_MESSAGE`, không mang chữ AI, không gắn lỗi gốc; `drafts._ai_prefixed` trả rỗng cho cả alt lẫn chú thích; gửi ảnh alt rỗng: `WordPressError` câu cố định, **0 lệnh** |
| E6 | Tốc độ với chuỗi dài (tiền tố lặp có ngoặc, `]\:` lặp, «[» lặp, «\» lặp), bản cũ và mới | 8.000 ký tự (cỡ trả lời tối đa với `max_tokens = 2000` của `[tasks.alt]`): 0,02–0,04 giây ở cả hai bản. 200.000 ký tự (gấp 25 lần): tiền tố ngoặc lặp 1,5–2,0 giây (bản `main` 1,0–1,1 giây, vì bản `main` dừng ở «\» đầu tiên); dạng «Minh họa: » lặp (có từ trước) 1,0–1,2 giây ở cả hai. Không treo, không đáng kể |
| E7 | Giả định xa: chữ **gửi WordPress** bị một bộ đọc Markdown xử lý (cần đồng thời: site có plugin Markdown **và** trình soạn thảo giải mã `&#91;` thành `[` như LC-T061-4). Đếm link, ảnh Markdown (markdown-it) trong alt, chú thích gửi đi, bản mới so với `main` | Bộ ngẫu nhiên (46.304 cặp không lỗi): 24 = 24, bản mới không nhiều hơn ca nào. Bộ chuỗi độc (79.031 cặp): bản mới 1.357, `main` 1.279; bản mới nhiều hơn ở **78** cặp, ít hơn 0. Cả 78 đều là AI tự gõ `[x]\(địa chỉ)` ngay sau tiền tố: bản `main` tình cờ còn «\» trước «[x]» (dấu của tiền tố); bản mới ra `[x](địa chỉ)`, đúng như bản `main` vẫn ra với `Minh họa: [x]\(địa chỉ)`. Xem Ghi nhận |

## Ghi nhận (không thành lỗi)

- **Hành vi mới «[Minh họa]: [nhãn]: một-chữ» → `AIError` (việc 3): an toàn.** Sau khi bỏ tiền tố và «\», phần thân «[Lưu ý]: Cửa» đứng đầu dòng nên `clean_ai_text` coi là dòng khai báo link và xóa (`_MD_LINK_DEF`, `sanitize.py:104-108`), alt rỗng → `AIError(EMPTY_ALT_MESSAGE)` (`alt.py:450-451`). Câu cố định, không chép chữ AI (E5); không gửi gì lên website; giống cách bản `main` đã xử lý «Minh họa: [Lưu ý]: Cửa», ««Minh họa»: [Lưu ý]: Cửa». Dạng «[nhãn]: địa chỉ» (AI chèn khai báo link ngay sau tiền tố) cũng thành `AIError` thay vì ra alt có địa chỉ: hướng an toàn hơn. Thân nhiều chữ vẫn ra alt (Soi Lỗi: 38/38 câu hợp lý). Xếp từng ca «lỗi mới» của tôi (`lc81_newerr.py`): bộ chuỗi độc 860 = 324 ca alt bản `main` không có chữ mô tả nào (chỉ tiền tố, ngoặc, dấu: đúng thiết kế SL-T062-1 là từ chối) + 536 ca thân «[nhãn]: một-chữ hay địa chỉ»; bộ ngẫu nhiên 1.051 = 1.035 + 14, cộng 2 ca xem tay cũng là «[nhãn]: một-chữ» sau 2–3 tiền tố lặp. Không ca nào alt bản `main` có câu mô tả thật.
- **Mở lại nháp:** `_ai_prefixed` (`drafts.py:177-191`) gặp `AIError` trả chuỗi rỗng cho **cả** alt lẫn chú thích (vì gọi `clean_suggestion` với cùng một chữ cho hai ô), `_ai_wording` đặt `alt_approved=False` (`:319`): người dùng phải gõ lại; ảnh alt rỗng không gửi được (E5). Chỉ gặp khi alt, chú thích đã lưu của ảnh AI chưa mở đầu bằng tiền tố chuẩn mà lại có dạng trên (chữ do app ghép luôn có tiền tố chuẩn). Có từ trước với các dạng không ngoặc vuông; hướng an toàn, không cần sửa.
- **«\» AI tự gõ sát sau «]» của tiền tố** (`[Minh họa]\: …`) cũng bị bỏ (Thợ Máy, Soi Lỗi Ghi nhận 3 đã nêu): trong Markdown `\:`, `\[`, `\(` chỉ là «:», «[», «(»; mọi bước sau (HTML, JSON, bộ đọc shortcode WordPress) không hiểu «\», nên về an toàn không đổi gì.
- **Chữ lưu nay có «[…]» trần ở phần thân** (ví dụ `Minh họa [code_snippet id=1] sơn`, trước là `Minh họa \[code_snippet id=1] sơn`): không phải link (C1, markdown-it), và ngay cả bản cũ thì «[code_snippet» vẫn nằm nguyên trong chữ. Hàm cảnh báo đoạn dạng shortcode của T-056 (LC-T061-4) vẫn thấy được như trước.
- **Dấu «\» bị bỏ không phải lớp chặn nào ở chữ gửi đi (E7).** Thiết kế T-054, T-071 gỡ escape Markdown cho chữ gửi WordPress (`plain_image_text`) vì WordPress không đọc Markdown. Chỉ khi **đồng thời** site bật plugin Markdown và trình soạn thảo giải mã `&#91;` thì `[x](địa chỉ)` trong chú thích mới có thể thành link; lớp chuỗi này đã có sẵn ở bản `main` (1.279/79.031 cặp trong bộ chuỗi độc), T-081 chỉ thêm 78 cặp cùng loại (AI tự gõ `[x]\(…)` sát sau tiền tố). Còn phải qua thêm: alt nằm trong thuộc tính HTML (bộ đọc Markdown không đụng), chú thích nằm trong khối `<figure>`. Không phải lỗi của T-081, không cần sửa. Đề xuất nhỏ cho Chỉ Huy (không phải điều kiện): ở phiếu thử thật T-059, ghi lại site **không** bật plugin Markdown (ví dụ mô-đun Markdown của Jetpack); `TIEN-DO.md` hiện chỉ ghi SiteSEO, Code Snippets. Nếu sau này bật thì cần xét lại cả lớp này, không riêng T-081.

## Điều kiện

| # | Việc | Ai làm | Trước mốc nào |
|---|---|---|---|
| 1 | **SL-T081-1** (Thấp): «(AI)» viết tách khỏi tiền tố không bị lặp; gỡ 5 `xfail` trong `tests/test_soi_loi_t081.py`. Khi sửa `_strip_ai_prefix` phải giữ: bước bỏ «\» của T-081 (`alt.py:391-392`); thân luôn lọc lại sau khi bỏ tiền tố; C6 (nhãn ảnh AI). Lá Chắn rút gọn W3 dùng lại `T-081-la-chan-scripts/` (C1–C4, C7, giả lập LC-T061-4) | Thợ Máy (**T-083**, đã lập, cùng SL-T068-1 → -3, LC-T068-1) | Sau T-056 (không chặn gộp T-081, không chặn T-056), như chủ dự án đã duyệt |

Không có điều kiện nào buộc sửa code của T-081 trước khi gộp. Toàn bộ `uv run pytest` trên Windows do Chỉ Huy chạy khi gộp.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 lỗi mới của Lá Chắn; SL-T081-1 đồng ý Thấp, không có hệ quả bảo mật (T-083, sau T-056). SL-T071-1 đóng. W3 / mục 2.3 đạt: bỏ «\» không mở lại được link Markdown, thẻ HTML hay shortcode ở bất kỳ chuỗi nào gửi WordPress (`<img alt>`, `<figcaption>`, `alt_text`, `title`, `caption`); mọi «[» «]» trần vẫn thành `&#91;` `&#93;`; nhãn ảnh AI luôn còn; câu lỗi mới cố định. **Gộp `main` được ngay**: không xung đột với `origin/main` `bbb55dc` (đã có T-066, T-071, T-080); test liên quan qua trên cây gộp (1971 passed, 0 hỏng).

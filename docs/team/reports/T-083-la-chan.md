# Biên bản bảo mật T-083 · Dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-083](../tickets/T-083-don-loi-chu-mo-ta-anh.md) (SL-T068-1, -2, -3, LC-T068-1, SL-T081-1; lượt 2: SL-T083-1), kèm điều kiện 1 của [Lá Chắn T-068](T-068-la-chan.md) và điều kiện 1 của [Lá Chắn T-081](T-081-la-chan.md) |
| Phạm vi | Rút gọn: W3 (mục 2.3), A3 theo mặc định; C6, chặn link và shortcode (T-061, T-062, T-081), bất động, ảnh thật không đổi, ngưỡng giới hạn, gỡ `xfail` (R5). Diff `b60054f..team/T-083` (gốc `main` `b60054f`, đầu nhánh lúc kiểm `de6b78a`). Code ứng dụng chỉ có `seo_app/images/alt.py` (+139/−35); test: `tests/test_soi_loi_t068.py` (−5 dòng dấu `xfail`), `tests/test_soi_loi_t081.py` (−5), `tests/test_soi_loi_t083.py` (mới, của Soi Lỗi; lượt 2 −5), `tests/test_t083_alt_tien_to.py` (mới); 2 báo cáo. Kèm cả đường đi của chữ và mọi nơi gọi: `app/views/write.py` `ai_write_alt` → `suggest_alt` (giới hạn từ `load_alt_rules()`); `seo_app/storage/drafts.py` `_ai_prefixed` (mở lại nháp, lưu ảnh AI) và `_one_line` (`clean_alt_text`); `plain_image_text` → `figure_html` / `_plan_draft_images` → `_describe_draft_media` → REST. `origin/main` lúc kiểm: `d9e6b5c` |
| Ngày | 2026-10-28 (01:27–02:05 +07, giờ máy) |
| **Kết luận** | **ĐẠT**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp; không lỗi mới, không điều kiện. **LC-T068-1 đóng** (ngưỡng 10 / 17 thay cho 20: xác nhận); SL-T068-1, -2, -3, **SL-T081-1** (điều kiện 1 của Lá Chắn T-081), SL-T083-1 đóng. **Gộp `main` được ngay** |

## Tóm tắt (cho chủ dự án)

- **An toàn.** Bản sửa chỉ dọn chữ «Minh họa» bị lặp hay cụt trong alt, chú thích ảnh AI. Nhãn ảnh AI («Minh họa», «Ảnh minh họa (AI)») **luôn còn**; mọi dấu «[» «]» vẫn được đổi thành mã ký tự trước khi gửi website nên không đoạn lệnh WordPress (shortcode) nào chạy được; link, thẻ HTML vẫn bị bỏ; ảnh thật không đổi gì. Tôi tự thử hơn 500.000 lần với chữ độc (đoạn lệnh, link, `<script>`, ký tự vô hình) đặt ngay sau các kiểu «Minh họa» mới, ở nhiều mức giới hạn ký tự: không lần nào lọt, và phần mềm không bao giờ tự tạo ra đoạn dạng lệnh.
- Giới hạn ký tự quá nhỏ để chứa chữ «Minh họa» thì phần mềm báo lỗi bằng câu cố định thay vì cắt cụt nhãn; app không có đường nào đặt được mức nhỏ như vậy (cấu hình không cho dưới 20).
- Không còn lỗi nào phải theo dõi từ phiếu này. Gộp vào `main` được ngay.

## Lỗi phát hiện

Không phát hiện lỗi (không có mã LC-T083, không thêm file test).

Các lỗi của Soi Lỗi trong phiếu đều đã sửa (mục «Kiểm lại lỗi cũ»); các ghi nhận 1–7 của Soi Lỗi T-083 không phải lỗi bảo mật (mục «Ghi nhận»).

## Kiểm lại lỗi cũ

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| **LC-T068-1** (Lá Chắn T-068, Thấp) · chú thích ảnh AI với `caption_max_chars` < 17 là tiền tố bị cắt cụt; bảo đảm C6 nằm ở file khác | **Đóng** | `_with_prefix` không còn nhánh `prefix[:limit]` (`alt.py:469-477`); `_check_ai_limits` (`:499-508`) báo `ValueError` khi alt < 10 (`AI_ALT_MIN_CHARS` = «Minh họa» + dấu cách + 1, `:405`) hay chú thích < 17 (`AI_CAPTION_MIN_CHARS` = độ dài «Ảnh minh họa (AI)», `:406`), chạy **trước** mọi bước lọc (`:538-539`). Bảo đảm nay nằm ngay trong `alt.py`. Quét mọi cặp giới hạn (E4): mục «Ngưỡng 10 / 17» bên dưới |
| **Ngưỡng 10 / 17 thay cho 20** (điều kiện 1 của Lá Chắn T-068 ghi «dưới 20») | **Xác nhận chấp nhận** | Mục «Ngưỡng 10 / 17» bên dưới |
| **SL-T068-1, -2, -3** (Soi Lỗi T-068, Thấp, đã đồng ý không phải lỗi bảo mật) | **Đóng** | 23 ca `xfail` cũ qua; gỡ dấu đúng R5 (mục R5 bên dưới). Không lỗi nào trong ba lỗi này từng làm mất tiền tố; bản sửa giữ đúng như vậy (C7, E2, E4, E6) |
| **SL-T081-1** (điều kiện 1 của Lá Chắn T-081) · «(AI)» viết tách khỏi tiền tố bị lặp | **Đóng** | `_AI_TAG` (`alt.py:372`) bỏ «(AI)», «AI» ở đầu phần còn lại mỗi vòng của `_strip_ai_prefix` (`:430-433`). Đúng các ràng buộc tôi ghi ở T-081: bước bỏ «\» của T-081 còn nguyên (`:447-448`); phần thân luôn lọc lại sau khi bỏ tiền tố (`_ai_body` gọi `clean_alt_text`, `:493`, rồi `_with_prefix` lọc lần nữa, `:477`); C6 giữ. 5 ca `xfail` của Soi Lỗi T-081 qua; dùng lại bộ kiểm C1–C4, C7 và giả lập LC-T061-4 của T-081 (E2, E3, E5) |
| **SL-T083-1** (Soi Lỗi T-083, Thấp) · «+ », «> » trước tiền tố vẫn lặp | **Đóng (lượt 2)** | `_LIST_MARK` (`alt.py:377`): số thứ tự, «+», «>», «●», «◦», «▪», chỉ bỏ khi ngay sau là tiền tố (`:434-435`). 4 ca `xfail` qua, gỡ dấu đúng R5 |
| Điều kiện 2 của Lá Chắn T-068 cho T-056 (không chạy lại `clean_suggestion` trên alt đã làm sạch cho tới khi phiếu dọn gộp) | **Hết cần sau khi T-083 gộp** | Kết quả nay bất động (C8, E2, E4, E6: 0 lần đổi chữ). T-056 hiện cũng không chạy lại `clean_suggestion` trên alt đã duyệt (`app/views/write.py` chỉ gọi `suggest_alt` khi bấm, `:1018-1052`) |

### Ngưỡng 10 / 17 (xác nhận)

Ý của LC-T068-1 là: tiền tố ảnh AI **không bao giờ** bị cắt, và bảo đảm phải nằm trong `alt.py`. Con số 20 tôi ghi ở T-068 lấy theo mức sàn của cấu hình (`ALT_MIN_CHARS = 20`, `seo_app/content/rules.py:89`), không phải yêu cầu riêng. Ngưỡng 10 / 17 đạt đúng ý đó:

- Từ ngưỡng trở lên, tiền tố luôn trọn: alt 10–19 là «Minh họa» + ít nhất một ký tự, hoặc `AIError` khi không còn chữ vừa chỗ; chú thích 17–19 đúng bằng «Ảnh minh họa (AI)» (chú thích chỉ có tiền tố là thiết kế có từ T-062). Không cặp giới hạn nào cho alt chỉ có tiền tố (C7).
- Dưới ngưỡng thì `ValueError` với câu dựng từ hằng `AI_LIMIT_TOO_SMALL` (`alt.py:407-410`), chỉ chứa tên trường, hai con số và tiền tố cố định: không chép chữ AI, không lộ gì.
- Không đường nào trong app tới được dưới ngưỡng: `suggest_alt` lấy giới hạn từ `load_alt_rules()` (cả `max_chars` lẫn `caption_max_chars` ≥ 20, `rules.py:485-490`); `drafts._ai_prefixed` dùng 500 / 1000 (`drafts.py:112-113`, `:199-204`); nếu có thì `write.py:1046-1047` bắt mọi lỗi lạ bằng câu cố định `MSG_ALT_FAILED`.
- Ngưỡng 20 sẽ làm hỏng `tests/test_soi_loi_t081.py::test_cat_do_dai_sau_khi_bo_gach_cheo` (ảnh AI, `max_chars=18`), test không được sửa (R5).

### Gỡ `xfail` (R5)

`git diff --numstat b60054f..team/T-083 -- tests/`: `tests/test_soi_loi_t068.py` 0 thêm / 5 xóa, `tests/test_soi_loi_t081.py` 0 / 5; lượt 2 (`git diff 36e9721..de6b78a -- tests/test_soi_loi_t083.py`) 0 / 5. Cả 15 dòng xóa là dòng `@pytest.mark.xfail(strict=True, reason=…)`; tham số, thân test giữ nguyên. Không test nào bị tắt, bỏ qua hay nới.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có khóa, mật khẩu (detect-secrets, soát lịch sử: mục Công cụ). Test mới chỉ dùng mật khẩu giả của site giả (`tests/conftest.py`) |
| S2 | Đạt | Câu lỗi trên đường mới: `EMPTY_ALT_MESSAGE` cố định (`alt.py:65`, `:552-553`) và `ValueError` dựng từ `AI_LIMIT_TOO_SMALL` (chỉ có giới hạn, tiền tố cố định); không câu nào chép chữ AI (E4, E6) |
| S3 | Không áp dụng | Không thêm biến cấu hình; `.env.example` không đổi |
| W1 | Đạt | Không sửa `seo_app/wordpress/**`, `app/**`. Gửi nháp kèm ảnh AI qua client với site giả (E3): trường `status` duy nhất là `draft` |
| W2 | Đạt | Không sửa client; không lệnh xóa, ghi đè. Alt rỗng (đường `AIError` mới, hay `_ai_prefixed` trả rỗng khi mở lại nháp) không gửi được: client báo lỗi trước mọi lệnh (`_IMAGE_NO_ALT`, như T-081 E5) |
| W3 | Đạt | Mục «W3 / 2.3» bên dưới |
| W4 | Đạt | `client.py`, `html.py`, `sanitize.py` không đổi (`git diff --quiet`); SSL, timeout, `https://` giữ nguyên |
| A1 | Không áp dụng | Không đổi prompt: mọi chỗ sửa của `alt.py` từ dòng 309 trở đi (`git diff -U0`), `alt_instructions`, `alt_prompt`, `reference_lines` (trước dòng 304) không đổi |
| A2 | Đạt | Chữ AI vẫn là dữ liệu chưa tin cậy: bước bỏ tiền tố chỉ **bỏ bớt** ký tự (cắt, `lstrip`, khớp neo đầu chuỗi), rồi phần thân lọc lại toàn bộ (`_ai_body` → `clean_alt_text` → `clean_ai_text`, `alt.py:493`), ghép tiền tố rồi lọc lần nữa (`_with_prefix`, `:477`). `suggest_alt` vẫn tắt `web_search` (không đổi) |
| A3 | Đạt (không đổi) | Phiếu ghi A3 theo mặc định. Không đổi dữ liệu gửi AI (ảnh qua `prepare_images`, thẻ, từ khóa: `suggest_alt` và hàm dựng prompt không nằm trong diff); phần sửa chỉ chạy **sau** khi AI trả lời |
| U1 | Không áp dụng | Không sửa `app/`; không `unsafe_allow_html`. Chữ lưu (hiện trên Streamlit) không có link, thẻ: C1 (markdown-it) |
| U2 | Không áp dụng | Không trang mới; `.streamlit/` không đổi |
| U3 | Không áp dụng | Không đụng mật khẩu đăng nhập app |
| F1 | Không áp dụng | Phần sửa không mở file, không nhận đường dẫn |
| F2 | Không áp dụng | Không đụng byte ảnh, EXIF, giới hạn ảnh |
| F3 | Đạt | Phần thêm không `eval`, `exec`, `pickle`, `yaml`, `subprocess`, `open(`, gọi mạng (grep phần thêm của diff `seo_app`: 0) |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` giống gốc (`git diff --quiet`). pip-audit: mục Công cụ |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới dùng `FakeWordPress` (fixture `fake_wp`, `wp_client`); bộ chặn mạng tự bật (`tests/conftest.py`); `tests/test_soi_loi_t083.py`, `tests/test_t083_alt_tien_to.py` không có `requests.get/post/Session`, `urlopen`, `socket`, `http.client`, `httpx` (grep: 0). Thử độc lập của Lá Chắn chỉ dùng site giả |

### W3 / mục 2.3: bỏ tiền tố kiểu mới không mở lại link, thẻ, shortcode

- **Cấu trúc:** bước bỏ tiền tố (`_strip_ai_prefix`, `alt.py:413-451`) chỉ **bỏ bớt** ký tự ở đầu chữ (`lstrip`, khớp neo đầu chuỗi `_AI_TAG`, `_LIST_MARK`, ngoặc, `_AI_PREFIX`) và một ngoặc đóng ở cuối chữ; không thêm ký tự nào, không đụng giữa chữ. Phần thân sau đó **luôn** được lọc lại (`_ai_body` → `clean_alt_text` → `clean_ai_text`: bỏ thẻ, bỏ link, `escape_link_syntax`, `alt.py:493`), rồi ghép tiền tố và lọc lần nữa (`_with_prefix`, `:477`). Nhánh trả rỗng (`_ai_body` `:491-492`, `_with_prefix` `:475-476`) chỉ trả chuỗi rỗng hay đúng hằng tiền tố. Cắt thô `_RAW_FACTOR` (`:544-546`) cắt trên chữ đã lọc lần đầu; mẩu bị cắt đi qua bước lọc lại như trên. Lớp vô hiệu «[» «]» khi in ra (`plain_image_text` → `figure_html` → `sanitize_html`/`escape_shortcodes`; ô Media `client.py`) **không đổi** (`git diff --quiet`). Code chỉ thêm tiền tố cố định (không có «[»), dấu cách hay «: », và các ký tự của chính bước lọc (dấu «\» escape, ký tự ngắt rộng 0), nên không thể tự tạo ra cụm «[tên» (E5 kiểm bằng số).
- **Chuỗi độc ngay sau tiền tố kiểu mới** (E2, E3): 30 kiểu tiền tố (không dấu «Minh hoa», «MINH HOA», gạch nối, dính liền, «Ảnh minh họa AI», «Tranh minh họa», «Hình vẽ minh họa», `` `Minh họa` ``, `_…_`, `__…__`, `**…**`, «- », «1. », «2) », «+ », «> », «>> », «● », «[Minh họa] (AI)», «(AI) Minh họa», «AI: Minh họa», ngoặc lồng, dấu trộn «1. + `Minh hoa`», «> **[Minh họa]**») × 18 cách nối (`:`, `\:`, `[`, `(`, « (AI) », « AI », ký tự rộng 0, U+202E, xuống dòng, « - », « > », « + », `` ` ``, `_`, `]:`…) × 70 chuỗi độc (58 chuỗi của T-081: shortcode, `[[…]]`, `[embed]…[/embed]`, tên chen ký tự rộng 0 hay thẻ, `&#91;`, link Markdown, `javascript:`, link tham chiếu, `<script>`, `<img onerror>`, `<svg onload>`, thẻ lồng, dấu nháy phá thuộc tính…; thêm 12 chuỗi hợp kiểu mới: `` `[code_snippet id=1]` ``, `_[code_snippet]_`, `(AI)[code_snippet id=1]`, `AI[embed]x[/embed]`, `> [x](https://…)`, `+ <script>`, `1. [x](javascript:…)`, `[Minh hoa](https://…)`…) × 2 phần thân = **75.600 chuỗi**, chạy ở 4 cặp giới hạn (125/200 mặc định, 20/20 sàn cấu hình, 10/17 ngưỡng mới, 500/1000 đường mở lại nháp): C1–C4, C7, C8, C10 **0 vi phạm** ở cả 4; lỗi chỉ có `AIError` câu cố định; ảnh thật khác bản `main` **0**. Gửi thật qua client với site giả 2.100 lần (30 tiền tố × 70 chuỗi độc): mọi chuỗi JSON không có «[» «]» trần, ký tự Cf, «\» lạ; trang chỉ có `figure`, `img`, `figcaption`; alt trên trang mở đầu «Minh họa »; `status` chỉ `draft`.
- **Thử ngẫu nhiên** (E6, hạt giống 83164, 60.000 cặp; 0–3 tiền tố từ 26 kiểu chữ × 22 kiểu dấu đầu dòng × 18 kiểu ngoặc (có `` ` ``, `_`, `__`, `[[`, `**[`) × 8 kiểu «(AI)»/«AI» × 24 cách nối, rồi 0–8 mảnh độc; giới hạn ngẫu nhiên, 8% dưới ngưỡng): C1–C4, C7, C8, C10 **0 vi phạm** trên 40.708 kết quả; lỗi chỉ có `ValueError` đúng khi dưới ngưỡng (4.805) và `AIError` câu cố định (14.487); ảnh thật khác bản `main` **0**.
- **Giả lập LC-T061-4** (trình soạn thảo WordPress giải mã `&#91;` thành `[` khi người sửa bài lưu lại; Thấp, đã có cảnh báo liệt kê đoạn dạng shortcode ở T-056): code **không tự tạo** cụm «[tên» nào: mọi tên shortcode chạy được trong chữ gửi đi đều có sẵn trong chữ AI sau bước lọc đầu, ở 214.988 kết quả của bản mới (E5). T-083 làm phần chữ thật vừa giới hạn nhiều hơn (bỏ được tiền tố rác), nên khi AI tự viết chữ dạng shortcode thì chữ đó có thể lọt vào alt ở chỗ bản `main` đã cắt mất; đó là cùng lớp đã có ở bản `main` với chữ AI không có tiền tố lạ, được vô hiệu khi gửi và được liệt kê trong cảnh báo của T-056 (xem Báo nhầm).

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, `uv` 0.13.4, worktree `wt-T-083`, nhánh `team/T-083` tại `de6b78a`. Máy chạy song song nhiều phiên khác (CPU 100% suốt lượt kiểm) nên test chạy lâu.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` (69 gói) → `uvx --offline pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có. `uv.lock`, `pyproject.toml` không đổi so với gốc |
| bandit 1.9.4 | `seo_app/images/alt.py` (470 dòng code): **No issues identified** | Có |
| detect-secrets 1.5.0 | **`PYTHONUTF8=1`**, `--all-files` trong thư mục nháp riêng: 7 file của diff, patch cả nhánh, 1 file mồi có chữ tiếng Việt (khóa AWS giả, dòng gán mật khẩu giả): bắt **đủ 2/2 mồi, 0 mục khác**. Quét lại biên bản này và 8 script thử trước khi commit (cùng cách, cùng mồi): mồi 2/2, biên bản và script **0 mục**. Đã xóa mồi cả hai lần | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p b60054f..team/T-083 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 2 dòng, đều là câu báo cáo (tả cách quét mồi; chữ `max_tokens`) | Có, đọc từng dòng. Không có khóa thật |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest (nhánh) | 9 file trong tiêu chí xong của phiếu (`tests/test_soi_loi_t068.py tests/test_soi_loi_t081.py tests/test_t081_alt_gach_cheo.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t071.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py`) + 2 file test mới (`tests/test_soi_loi_t083.py tests/test_t083_alt_tien_to.py`, 2.066 ca) + test của mọi nơi gọi hàm bị sửa (`tests/test_ai_images.py tests/test_soi_loi_t054.py tests/test_drafts_images.py tests/test_storage_drafts.py tests/test_app_drafts.py tests/test_app_images.py tests/test_la_chan_t056.py tests/test_soi_loi_t056.py`: mở lại nháp `_ai_prefixed`, `_one_line`; trang Soạn bài gọi `suggest_alt`), 19 file, 01:31:51–01:50:19: **3926 passed, 1 skipped, 0 hỏng** | Có. 0 `xfailed`, 0 XPASS: 19 file không còn dấu `xfail` nào (grep chỉ thấy chữ trong docstring; lỗi cũ đã sửa ở T-060, T-071, T-081, T-083). 1 bỏ qua: `posix_only` «symlink thử trên Mac/Linux» (`tests/test_drafts_images.py:51`), do máy Windows |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-083`: `origin/main` `d9e6b5c` + `de6b78a` → cây `6b40fc1`, **không xung đột**. `main` đổi từ gốc `b60054f` chỉ ở `app/views/settings.py` (T-084, tab Ảnh), 3 gói rỗng Giai đoạn 5, test của T-084 và tài liệu; không trùng file nào của T-083; `alt.py`, `sanitize.py`, `html.py`, `meta.py` của `main` giống gốc. Cây `6b40fc1` chép ra thư mục nháp (`git archive`), chạy bằng Python của worktree: 9 file tiêu chí xong + 2 file test mới + `tests/test_drafts_images.py tests/test_storage_drafts.py tests/test_app_images.py` (nơi gọi) + `tests/test_settings_images.py tests/test_soi_loi_t084.py tests/test_app_pages.py` (phần đổi của `main`, mở mọi trang), 17 file, 01:44:49–01:56:26: **3496 passed, 1 skipped, 2 xfailed, 0 hỏng** | Có: `seo_app` nạp từ thư mục cây gộp, có `_check_ai_limits` (T-083) và `image_folders_list` (T-084) (plugin nhỏ in ra cuối lượt chạy). 2 `xfailed`: SL-T084-1 (`.env` không phải UTF-8, 2 ca, có sẵn trên `main`, đã giao T-090). 1 bỏ qua: `posix_only` như trên. 0 XPASS |

## Báo nhầm đã loại

- **detect-secrets:** 2 mục duy nhất là chuỗi mồi tôi tự đặt (đã xóa).
- **Soát lịch sử nhánh:** 2 dòng là câu báo cáo của Soi Lỗi (cách quét mồi) và Thợ Máy (chữ `max_tokens`).
- **Giả lập LC-T061-4 kiểu T-081 (C6′, «bản mới không chạy được nhiều shortcode hơn bản `main`»)** báo 334/60.000 cặp ngẫu nhiên và 4.186/75.600 chuỗi độc ở mức 20/20 (0 ở 3 mức còn lại). Đọc mẫu: ở bản `main`, tiền tố AI viết lạ không được nhận nên chiếm chỗ, alt bị cắt **trước** đoạn shortcode có sẵn trong chữ AI (ví dụ alt `main` `Minh họa (AI) [x]\[1` cụt, bản mới `Minh họa [x]\[1]`; alt `main` `Minh họa + > (minh-hoạ`, bản mới `Minh họa ［]]\[embed]…`). Tiêu chí này đúng cho T-081 (chỉ bỏ một dấu «\») nhưng không đúng cho T-083 (bỏ được tiền tố thì phần chữ thật vừa giới hạn nhiều hơn). Tôi thay bằng tiêu chí đúng: code không tự tạo cụm «[tên» nào không có sẵn trong chữ AI sau bước lọc đầu (E5). Lớp này (AI tự viết chữ dạng shortcode) có sẵn ở bản `main` với chữ AI không có tiền tố lạ, đã có cảnh báo liệt kê đoạn dạng shortcode trước nút «Gửi nháp» (T-056, LC-T061-4).

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục nháp của phiên; bản sao ở thư mục ghi chú chung, `T-083-la-chan-scripts/`), không sửa code ứng dụng; chạy trong worktree bằng `PYTHONUTF8=1 uv run --offline --with markdown-it-py python <script>` (markdown-it-py lấy từ bộ nhớ đệm của `uv`, không tải mạng, không thêm vào thư viện dự án); `seo_app` nạp từ worktree (script kiểm `__file__`). Bản `main` của `alt.py` lấy bằng `git show b60054f:seo_app/images/alt.py` (giống `alt.py` của `origin/main` `d9e6b5c`), nạp thành module riêng. Không dùng lại dữ liệu của Thợ Máy, Soi Lỗi; bộ kiểm C1–C4, C7 dùng lại từ biên bản T-081.

Các kiểm trên **mọi** kết quả không lỗi của ảnh AI (bản mới):
- **C1** chữ lưu (hiện trên Streamlit): bất động với `escape_link_syntax`, `strip_tags` không đổi gì, markdown-it (CommonMark, bật HTML thô) không dựng ra thẻ nào ngoài `p`, `em`, `strong`, `code`;
- **C2** `figure_html`: chỉ `figure`, `img`, `figcaption`; `<img>` đúng 4 thuộc tính, `src` đúng; không «[» «]» trần, không ký tự Cf; chữ trình duyệt đọc ra đúng bằng `plain_image_text`;
- **C3** ô Media dựng như client (`alt_text`, `title` có `[AI] `, `caption`): không «[» «]» trần, không ký tự Cf;
- **C4** chuỗi vào không có «\» thì chữ gửi đi không có «\»;
- **C7** nhãn ảnh AI: alt (lưu và gửi) mở đầu «Minh họa », còn chữ cái hay chữ số sau tiền tố; chú thích mở đầu «Ảnh minh họa (AI)»;
- **C8** bất động: chạy lại `clean_suggestion` (cùng giới hạn) trên kết quả ra đúng kết quả đó;
- **C10** không quá giới hạn, một dòng, NFC.

| # | Thử gì | Kết quả |
|---|---|---|
| E1 | Đọc diff, mọi nơi gọi (`write.py:1018-1052`, `drafts.py:163-168`, `:193-207`), cấu trúc `_strip_ai_prefix` / `_ai_body` / `_with_prefix` | Chỉ bỏ bớt ký tự rồi lọc lại; lớp in ra không đổi; ảnh thật đi đúng hai dòng cũ (`alt.py:548-550`) |
| E2 | Bộ chuỗi độc 75.600 chuỗi × 4 cặp giới hạn (mục W3), so bản `main` | C1–C4, C7, C8, C10: **0 vi phạm**; ảnh thật khác `main`: **0**; lỗi chỉ `AIError` câu cố định. So với `main` ở 125/200: giống 9.715, khác 57.500, lỗi mới 8.385 (alt chỉ còn tiền tố hay chữ đầu không vừa chỗ: hướng an toàn) |
| E3 | Gửi thật qua `WordPressClient.create_draft_with_images` với site giả: 2.100 lần | Mọi chuỗi JSON: 0 «[» «]» trần, 0 ký tự Cf, 0 «\» lạ; trang chỉ 3 thẻ, alt mở đầu «Minh họa »; `status` chỉ `draft` |
| E4 | Quét giới hạn (`lc83_limits.py`): mọi cặp `max_chars` 0–60 (thêm 9 mức tới 400) × `caption_max_chars` 0–60 (thêm 9 mức tới 1000) × 30 chuỗi = 147.000 lần | Dưới ngưỡng (alt < 10 hay chú thích < 17): **51.600/51.600** ra đúng `ValueError` với câu dựng từ `AI_LIMIT_TOO_SMALL` (trường alt báo trước); từ ngưỡng: 70.649 kết quả qua C1–C4, C7, C8, C10, chú thích 17–19 đúng bằng «Ảnh minh họa (AI)»; 24.751 `AIError` câu cố định; 0 lỗi lạ. Ảnh thật: giống hệt `main` ở mọi cặp, không bao giờ `ValueError` |
| E5 | Code có tự tạo cụm «[tên» không (giả lập LC-T061-4 đúng cách, `lc83_c6src.py`): với mọi kết quả, mọi tên shortcode **chạy được** (biểu thức `get_shortcode_regex` của WordPress, coi mọi tên là đã đăng ký, «[[tên]]» là đã thoát) trong alt, chú thích gửi đi đã giải mã phải có sẵn cụm «[tên» tương ứng (đủ số lần) trong chữ AI sau bước lọc đầu `_one_line` (bước này không đổi giữa hai bản). Bộ ngẫu nhiên của E6 + bộ chuỗi độc của E2 ở cả 4 cặp giới hạn | Bản mới: **0**/40.708 (ngẫu nhiên) và **0**/174.280 (chuỗi độc) kết quả có tên chạy được do code tự tạo; bản `main`: 0/52.816 và 0/260.250. Mọi đoạn dạng shortcode trong chữ gửi đi đều do AI viết sẵn, và vẫn bị vô hiệu khi gửi (`&#91;`, C2, C3, E3) |
| E6 | Thử ngẫu nhiên 60.000 cặp (`lc83_fuzz.py`, hạt giống 83164; mục W3) | C1–C4, C7, C8, C10: **0 vi phạm** (40.708 kết quả); `ValueError` chỉ khi dưới ngưỡng (4.805), `AIError` chỉ câu cố định (14.487), không lỗi lạ; ảnh thật khác `main` **0** |
| E7 | Tốc độ với chữ dựng cố ý cho các biểu thức mới có lượng từ lặp (`_AI_PREFIX` với `[\s_\-‐‑]+`, `_LIST_MARK`, `_AI_TAG`) và vòng `_strip_ai_prefix`, `_ai_body`: 19 mẫu (dãy «_», «-», «‐» dài sau «hình», «minh», «bức tranh»; «1.», «1», «123)», «+ », «> », «(AI) », «AI », «( », «Minh hoa », `` `Minh họa` ``, «1. + `Minh hoa` (AI): », «[Minh họa]», «Minhhọa», «Tranh vẽ minh hoạ AI », «: » lặp) × 8.000 và 50.000 ký tự × 3 cặp giới hạn (125/200, 500/1000, 5000/5000), bản `main` và bản mới chạy liền nhau | Bản mới **nhanh hơn** bản `main` ở mọi mẫu (cắt thô `_RAW_FACTOR` chặn độ dài trước vòng bỏ tiền tố). 8.000 ký tự (trả lời dài nhất với `max_tokens = 2000`) ở 125/200: mới 0,018–0,062 giây (cũ 0,039–0,095). Chậm nhất toàn bộ: mới 0,25 giây (50.000 ký tự, giới hạn 5000), cũ 0,53 giây. Biểu thức neo đầu chuỗi (`.match`), các đoạn lặp cách nhau bởi chữ cố định: không có dấu hiệu ReDoS |

## Ghi nhận (không thành lỗi)

- **Báo «AI không viết được alt» nhiều hơn ở ca lạ: hướng an toàn.** Alt ảnh AI chỉ có tiền tố viết kiểu lạ («Minh hoa», «+ Minh họa»), hay chữ đầu của phần thân dài hơn chỗ còn lại (địa chỉ web, `[code_snippet`, chữ dính liền; chỉ đáng kể ở mức sàn 20), nay báo `AIError` câu cố định thay vì ra alt rác hay mẩu chữ cụt («Minh họa [code_snipp»). Không gửi gì lên website; người dùng bấm thử lại hay tự gõ. Soi Lỗi đã thử 760 câu hợp lý × 4 mức giới hạn: 0 lần báo lỗi mới.
- **`ValueError` mới khi gọi sai giới hạn:** hiện không đường nào tới được (mục «Ngưỡng 10 / 17»). Phiếu sau mà gọi `clean_suggestion` cho ảnh AI với giới hạn tự đặt thì phải lấy từ `load_alt_rules()` hoặc bắt `ValueError` bằng câu cố định như `write.py:1046-1047`; `drafts._ai_prefixed` chỉ bắt `AIError`, an toàn vì dùng hằng 500 / 1000.
- **Mở lại nháp:** `_ai_prefixed` (`drafts.py:193-207`) trả rỗng khi `AIError`, nên alt ảnh AI đã lưu mà không mở đầu bằng tiền tố chuẩn và chỉ có tiền tố kiểu lạ («+ Minh họa») nay thành rỗng, `alt_approved=False` (`:352`): người dùng phải gõ lại; ảnh alt rỗng không gửi được. Hướng an toàn, như T-081 đã ghi.
- **Nhận tiền tố rộng hơn chỉ đụng chữ ảnh AI:** «AI», «(AI)», dấu câu, số thứ tự, «+», «>» ở đầu phần thân bị bỏ (Rủi ro 1, 2 của Thợ Máy; Ghi nhận 1 của Soi Lỗi). Chỉ là câu chữ; tiền tố chuẩn luôn được ghi lại nên nhãn ảnh AI không bao giờ mất (C7); ảnh thật không đổi (C9).
- **Cắt thô (G4)** có thể để lại mẩu tiền tố dở khi chữ AI toàn tiền tố lặp dài hơn 4 × giới hạn («Minh họa minh», Rủi ro 3 của Thợ Máy). Tiền tố chuẩn vẫn trọn; AI thật không viết vậy (`max_tokens = 2000`).
- **Ghi nhận E7 của T-081 (giả định site có plugin Markdown) không đổi:** T-083 không bỏ thêm dấu «\» nào (`_AFTER_PREFIX`, `_AI_TAG`, `_LIST_MARK` không chứa «\»; `_LINK_ESCAPES` giữ nguyên), nên không thêm chuỗi nào vào lớp đó.
- **G2 (ngoặc lệch, Thợ Máy Rủi ro 6) chưa sửa:** chỉ là thẩm mỹ, không có hệ quả bảo mật, kết quả vẫn bất động.

## Điều kiện

Không có. Toàn bộ `uv run pytest` trên Windows do Chỉ Huy chạy khi gộp.

Ghi cho Chỉ Huy (không phải điều kiện): sau khi T-083 gộp, điều kiện 2 của Lá Chắn T-068 cho T-056 («không chạy lại `clean_suggestion` trên alt đã làm sạch») không còn cần; phiếu sau gọi `clean_suggestion` cho ảnh AI phải lấy giới hạn từ `load_alt_rules()` hoặc bắt `ValueError` bằng câu cố định (mục «Ghi nhận»).

## Kết luận

**ĐẠT.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. LC-T068-1 đóng (ngưỡng 10 / 17 xác nhận: tiền tố không bao giờ bị cắt, bảo đảm nằm ngay trong `alt.py`, câu lỗi cố định, không đường nào trong app tới được dưới ngưỡng); SL-T068-1, -2, -3, SL-T081-1, SL-T083-1 đóng. W3 / mục 2.3 đạt: bỏ tiền tố kiểu mới chỉ bớt ký tự rồi lọc lại, không mở lại được link Markdown, thẻ HTML hay shortcode ở bất kỳ chuỗi nào gửi WordPress (`<img alt>`, `<figcaption>`, `alt_text`, `title`, `caption`), code không tự tạo cụm «[tên»; C6 giữ (nhãn ảnh AI luôn còn, alt chỉ có tiền tố bị từ chối); kết quả bất động; ảnh thật không đổi; A3 không đổi; gỡ `xfail` đúng R5. **Gộp `main` được ngay**: không xung đột với `origin/main` `d9e6b5c`; test liên quan qua trên nhánh (3926 passed) và trên cây gộp (3496 passed), 0 hỏng.

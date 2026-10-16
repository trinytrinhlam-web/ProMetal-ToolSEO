# Biên bản bảo mật T-031 · Địa chỉ trần, `www.` và email trong chữ AI không thành link

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (**Opus tạm**: hồ sơ ghi Fable, Fable bị giới hạn tới 01/11, chủ dự án duyệt chạy tạm; nên kiểm lại bằng Fable sau 01/11) |
| Phiếu được kiểm | [T-031](../tickets/T-031-dia-chi-tran-thanh-link.md), kèm ghi chú mở rộng phạm vi 2026-10-16 (`clean_flags`, `markdown_link`) |
| Phạm vi | `git diff origin/main...team/T-031` tại `c6505ee`: `seo_app/sanitize.py`, `seo_app/content/workflow.py`, `seo_app/text.py`, 5 file test |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Trước phiếu này, nếu AI (hoặc một trang đối thủ) viết `https://…`, `www.…` hay một email, trang Soạn bài và trang Thử mù hiện nó thành link bấm được. Nay app chèn một ký tự vô hình vào giữa địa chỉ: người đọc vẫn thấy nguyên địa chỉ nhưng không bấm được. Tôi tự dựng lại bộ hiển thị Markdown giống Streamlit và thử gần **49 000 mẫu** cố tình lách (escape, mã HTML, chữ toàn khổ, ký tự vô hình cài sẵn, chỗ nối khi Áp dụng gợi ý): **không mẫu nào thành link**. Các lớp chặn link cũ (T-004 → T-015) không bị yếu đi. Lỗi có từ trước ở tên bài đối thủ (`markdown_link`) đã được chặn. Còn hai việc nhỏ ngoài phiếu, không chặn: trang Kết nối WordPress (SL-T031-1) và một test chạy song song thỉnh thoảng đỏ (của T-028).

## Lỗi phát hiện

Không phát hiện lỗi trong phạm vi T-031.

Ghi nhận ngoài phạm vi (không chặn phiếu này):

| # | Mức | Mô tả | Vị trí | Đường đi thật | Đề xuất |
|---|---|---|---|---|---|
| N1 | Thấp | SL-T031-1: tên website, tên tài khoản lấy từ WordPress hiện bằng Markdown không escape | `app/views/wordpress.py:41-42` | WordPress trả `site_name = "www.evil.example"` → `st.success`/`st.markdown` → link bấm được. Nguồn là site của chính chủ dự án, chỉ người có quyền quản trị site mới đổi được tên site/tài khoản; trang chỉ để thử kết nối | **Đồng ý** với Chỉ Huy: phiếu nhỏ cho Họa Sĩ, không chặn T-031. Bọc bằng `escape_markdown` (nay đã có `break_autolinks`) hoặc `st.text`. Gỡ `xfail` của `test_wordpress_site_name_is_not_a_link` khi sửa. Làm trước khi hết Giai đoạn 2, hoặc gộp vào lúc làm lại trang WordPress ở Giai đoạn 5 |
| N2 | Thấp | Test `tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail` đỏ 1 lần khi chạy cả bộ, chạy riêng 11 lần đều xanh | test của T-028 (đọc `os.environ` song song khi `ignoring_custom_headers` gỡ biến) | Không liên quan diff T-031 (không đụng `seo_app/ai/`). Có thể chỉ là test đua luồng nhạy với máy bận; cũng có thể là chỗ đua thật trong `ignoring_custom_headers` | Chỉ Huy giao Soi Lỗi bắt lại lỗi (in `errors`) để biết là test hay code. Không chặn T-031 |

## Phép thử độc lập của Lá Chắn

Bộ hiển thị: `react-markdown` 9.1.0 + `remark-gfm` 4.0.1 (+ `rehype-raw` 7.0.0 cho chỗ app dùng `unsafe_allow_html`), đếm thẻ `<a href>` thật sau khi hiện. Cài tạm bằng npm trong scratchpad, **không** thêm vào dự án. Script riêng, không chép của Thợ Máy hay Soi Lỗi.

- **Đối chứng:** tắt `break_autolinks` thì `www.evil.com`, `a@evil.com`, `https\://evil.com`, `a&#64;evil.com`, `www\.evil.com` đều ra link. Vậy bộ thử bắt được lỗi thật.
- **48 977 ca, 0 link.** 63 mẫu viết tay + 4 000 chuỗi ngẫu nhiên, mỗi mẫu qua 10 đường:
  - `clean_ai_text` (thường và qua `ui.highlight` + HTML);
  - `clean_ai_line`;
  - `:gray[…]`;
  - trích câu (`> …` rồi `escape_link_syntax`);
  - round-trip ô sửa: `escape(unescape(clean(t)))` qua `ui.highlight`;
  - người dùng **tự gõ** chữ độc vào ô sửa rồi Lưu, kể cả khi đã gỡ U+200B trước;
  - `markdown_link(t, "")` và `markdown_link(t, "javascript:x")`.
  
  Thêm ~3 000 lần `apply_flag` (thay câu và xóa câu) và 64 chỗ nối cố ý: `https:` | `//…`, `https:/` | `/…`, `ww` | `w.…`, `a` | `@…`, `&#6` | `4;…`, `\` | `@…`.
- **Mẫu lách đã thử:**
  - escape: `https\://`, `https:\/\/`, `www\.`, `a\@`, `\\www.`, `\www.`;
  - mã HTML: `&#64;`, `&commat;`, `&period;`, `&colon;&sol;&sol;`, `&#119;&#119;&#119;&#46;`, `&#x77;ww.`, `&amp;@`, `&lt;@`, `&amp;www.`, mã thiếu `;`;
  - chữ toàn khổ: `ｗｗｗ．`, `：／／`, `＠`;
  - ký tự vô hình có sẵn: U+2060, soft hyphen;
  - **U+200B do kẻ tấn công cài sẵn** đúng chỗ app sẽ chèn (`https:/​/`, `www​.`, `a​@`, `​www.`) và dạng mã `&#8203;`, `&#x200B;`;
  - thẻ/chú thích HTML chen giữa địa chỉ (`w<b>ww</b>.`, `https:<!-- -->//`), link `[x](…)`, `<https://…>`, `<a href>`, đậm, nghiêng, danh sách, trích dẫn, bảng, tiêu đề, Unicode, punycode.
- **U+200B cài sẵn + `unbreak_autolinks`:** `unbreak` gỡ đúng ký tự đó (vì không phân biệt được với ký tự app chèn), nhưng kết quả chỉ đi vào ô nhập chữ thường (`st.text_area` ở `app/views/write.py:664`, `st.text_input` ở `:552`, `:559` qua `set_outline` và `drafts.py:342`). Khi Lưu, `escape_link_syntax` chèn lại. Đã thử: mọi đường quay về giao diện đều 0 link. Đã xác nhận bằng grep: không chỗ nào đưa kết quả `unescape_link_syntax` vào `st.markdown`. Đây là bất biến cần giữ, xem mục Lưu ý.
- **`ui.highlight` đổi `&` thành `&amp;`:** bộ hiển thị lúc đó không giải mã mã HTML nữa, nên "chữ đã giải mã" của nó khác của `break_autolinks`. Tôi đã xét: `www.`, `://` viết liền không thể nằm trong một mã `&…;`. Ký tự trước `@` mà bộ hiển thị thấy là `;` thì GFM không nhận làm email. Phép thử thực tế: 0 link.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có bí mật. `detect-secrets` báo `tests/test_soi_loi_t031.py:47` `PASSWORD = "mat-khau-thu-123"`: mật khẩu giả của test, dùng chung mẫu với các test cũ |
| S2 | Không áp dụng | Diff không in log, không hiện lỗi |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng đường đăng bài |
| W2 | Không áp dụng | |
| W3 | Đạt (cho phần hiển thị) | Chữ AI và chữ ngoài (tên bài đối thủ, nghiên cứu) không còn tạo link qua autolink GFM: `sanitize.py:506-557` (`escape_link_syntax` kết thúc bằng `break_autolinks`), `text.py:44-50` (`escape_markdown`). Phần gửi WordPress là việc Giai đoạn 5, xem dưới |
| W4 | Không áp dụng | |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | Đạt | Kết quả AI vẫn qua `clean_ai_text`/`clean_ai_line`. `clean_flags` (`workflow.py:141`) chỉ đổi cách so câu: câu vẫn phải là chuỗi con của thân bài đã lọc, nên không thêm đường cho chữ AI chưa lọc lên giao diện |
| U1 | Đạt | `ui.highlight` vẫn `html.escape` toàn bộ trước khi chèn `<mark>`, phép thử có `rehype-raw` cho 0 link. U+200B không phải ký tự HTML. Không có `unsafe_allow_html` mới |
| U2 | Không áp dụng | |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | |
| F2 | Không áp dụng | |
| F3 | Không áp dụng | Không đọc/ghi file. Test đọc file JS của Streamlit chỉ để đối chiếu, không chạy nó |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi. `import html.entities` là thư viện chuẩn. Bộ hiển thị node chỉ cài tạm ngoài repo |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Test mới không mở mạng. Bộ chặn mạng trong `tests/conftest.py` vẫn áp. `test_soi_loi_t031.py` chỉ đọc file JS đã cài trong `.venv` |

### Các lớp T-004 → T-015 không bị yếu đi

- **Ký tự ngắt không đụng phần escape link:** chỉ chèn ngay trước `/`, `.` hoặc `@` (`_AUTOLINK_CUT`, `sanitize.py:415`), không bao giờ sau `]`. Vì vậy `]\(`, `]\[`, `[nhãn]\:` không đổi, và phần escape link Markdown không phụ thuộc vào nó.
- **`unescape_link_syntax` chỉ gỡ đúng ký tự do app chèn:**
  - `unbreak_autolinks` (`sanitize.py:488-503`) chỉ bỏ U+200B nằm đúng 3 chỗ, trên chữ đã giải mã. Ký tự đó phải là U+200B thật trong chữ gốc, không phải dạng mã `&#8203;`.
  - Phần gỡ `\` giữ nguyên như trước.
  - Trường hợp duy nhất gỡ "nhầm" là U+200B kẻ tấn công cài đúng chỗ. Đã xét ở trên: vô hại vì Lưu lại thì chèn lại.
- **`escape(unescape(t)) == t`:** 0 lỗi trên 4 063 chuỗi của tôi. Soi Lỗi đã thử 30 000 chuỗi, cũng 0 lỗi. `break_autolinks` chạy lại không đổi gì (idempotent): 0 lỗi.
- **7 test cũ bị sửa:** đã đọc từng dòng diff. Không khẳng định nào bị bỏ. Chỉ chuỗi mong đợi đổi sang dạng có U+200B, và vẫn so cả chuỗi. Hai chỗ có thêm `gfm_autolinks(...) == []`. `test_escape_only_adds_backslashes` nay bỏ thêm U+200B trước khi so, đúng với tính chất mới, rồi vẫn so nguyên chuỗi. Kết luận: **không nới**.
- **`markdown_link` (lỗi có từ trước):**
  - Đã chặn. `markdown_link("https\\://evil…", "")` và các dạng `www.`, email, `[x](…)`: 0 link.
  - Khi URL hợp lệ, link đối thủ vẫn bấm được như thiết kế cũ (`_clean_url` chỉ nhận http/https). Ký tự ngắt trong nhãn vô hại.
  - URL `javascript:` vẫn bị loại.

### ReDoS và tốc độ

- Ba biểu thức mới chỉ dùng lookbehind độ dài cố định. `_ENTITY` có giới hạn độ dài (6/7 chữ số, tên tối đa 32).
- `_decoded_view` và `unbreak` chạy một lượt (`drop` là `set`).
- Đo trên 11 mẫu xấu (`www`, `a@`, `&#64;`, `&#`, `&a`, `\.`, `:/`, U+200B, `w​.`, `&aaa…`, `&#1111111`): 20 000 → 200 000 ký tự, thời gian tăng khoảng ×10, tối đa 0,22 giây. **Tuyến tính.**

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found | Có |
| bandit (`seo_app app scripts`) | 1 Thấp: B101 `assert` ở `seo_app/storage/drafts.py:203` | Có: có từ trước, không thuộc diff T-031 |
| detect-secrets | Trong repo (ngoài `.venv`): chỉ các mật khẩu/khóa giả trong test và biên bản cũ; mới ở diff: `tests/test_soi_loi_t031.py:47` (mật khẩu giả) | Có: báo nhầm |
| Soát lịch sử git (`origin/main..HEAD`) | Chỉ có `hash_password`, `PASSWORD` giả, `delenv("ANTHROPIC_API_KEY")` trong test | Có: không có bí mật |
| pytest | `1 failed, 4086 passed, 4 skipped, 14 xfailed`. Ca đỏ: `test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail`; chạy riêng 11 lần đều xanh (N2) | Có: không thuộc diff |
| ruff | All checks passed! | Có |
| Bộ hiển thị thật (node, ngoài repo) | 48 977 ca, 0 link; đối chứng không ngắt thì 5/6 ra link | Có |

## Báo nhầm đã loại

- `detect-secrets`: `PASSWORD = "mat-khau-thu-123"` là mật khẩu giả dùng cho đăng nhập trong AppTest. Các test cũ dùng cùng giá trị này.
- `bandit` B101: `assert` trong `drafts.py` có từ trước, ngoài diff.

## Lưu ý cho các phiếu sau

1. **Bất biến mới (cần giữ):**
   - Kết quả của `unescape_link_syntax` / `unbreak_autolinks` chỉ được đưa vào ô nhập chữ thường (`text_area`, `text_input`), không bao giờ đưa vào `st.markdown`, `st.caption`, `st.success`… Hai hàm này gỡ cả U+200B do kẻ tấn công cài sẵn (cũng như gỡ `\` trước `(`), nên đưa vào Markdown là ra link.
   - Hiện code đã đúng.
   - Đề nghị Thư Ký ghi một dòng vào docstring hoặc `rules.md`, hoặc đưa vào việc của phiếu sau.
2. **Dạng `<https://…>` để nguyên:**
   - Dạng này chỉ an toàn nhờ `strip_tags` (trong `clean_ai_text`, `apply_flag`) hoặc `ui.highlight` chạy trước.
   - Đường hiện chữ mới phải đi qua một trong hai.
   - Tôi đồng ý với nhận xét của Soi Lỗi.
3. **Nâng Streamlit:** `test_streamlit_autolink_rules_unchanged` đỏ thì phải kiểm lại T-031. Không được sửa chuỗi mong đợi cho xanh.

## Việc cho Giai đoạn 5 (đề nghị Chỉ Huy bổ sung vào `docs/team/board.md`, mục «Việc bắt buộc khi làm Giai đoạn 5»)

Dòng URL trần hiện có (dòng 89) chưa đủ sau T-031. Đề nghị thêm:

- **Gỡ ký tự ngắt U+200B do app chèn (`unbreak_autolinks`, hoặc `unescape_link_syntax` nếu gỡ cả `\`) trước khi chuyển Markdown sang HTML gửi WordPress.** Áp cho thân bài, tiêu đề bài, tiêu đề mục, meta. Không gỡ thì bài trên site thật có U+200B trong địa chỉ và email: chép ra hỏng, tìm kiếm không khớp.
- **Sau khi gỡ, địa chỉ trần lại liền mạch.** Vì vậy bộ chuyển Markdown → HTML **phải tắt autolink**. Nếu không tắt được thì màn hình xác nhận phải liệt kê cả các địa chỉ trần này như link, và đánh dấu địa chỉ lạ.
- Hàm gỡ cũng gỡ U+200B do kẻ tấn công cài sẵn, nên không được coi chữ đã gỡ là "an toàn để hiện Markdown". Sau bước gỡ, mọi link chỉ được tin sau `sanitize_html` và màn hình xác nhận `href`.
- Nên có test: bài có `https://`, `www.`, email → HTML gửi đi không chứa U+200B và không có `<a>` nào ngoài các link người dùng đã thấy ở màn hình xác nhận.

## Điều kiện

Không có (kết luận ĐẠT). N1 và N2 là việc ngoài phạm vi, đề nghị lập phiếu riêng:
- N1 (SL-T031-1) cho Họa Sĩ;
- N2 cho Soi Lỗi bắt lại lỗi.

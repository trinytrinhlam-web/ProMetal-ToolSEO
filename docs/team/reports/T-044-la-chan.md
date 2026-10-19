# Biên bản bảo mật T-044 · Chữ lấy từ WordPress hiện an toàn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable) |
| Phiếu được kiểm | [T-044](../tickets/T-044-ten-site-tu-wordpress-hien-an-toan.md) |
| Phạm vi | Kiểm định rút gọn (U1): diff `origin/main...team/T-044` tại `9af9e43` (main `6306343`): `app/views/wordpress.py`, `app/views/settings.py`, `tests/test_app_t044_safe_text.py`, `tests/test_soi_loi_t044.py`, `tests/test_app_wordpress.py`, `tests/test_soi_loi_t031.py` |
| Ngày | 2026-10-17 (pytest chạy lại xong 2026-10-19) |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Trên trang **Kết nối WordPress**, mọi chữ lấy từ website (tên site, địa chỉ, tên tài khoản, vai trò, tiêu đề bài nháp, địa chỉ ảnh, câu lỗi) giờ chỉ hiện là chữ thường; không còn chỗ nào biến thành link hay HTML. Ở thử mù, tên mô hình kiểu `https://…`, `www.…`, email không còn thành link trong câu lỗi; chỉ có thể ra kiểu chữ nghiêng hay biểu tượng vô hại nếu chính bạn gõ như vậy, tôi chấp nhận không cần sửa. Còn 2 điểm nhỏ nằm ngoài phiếu này (ghi ở dưới), không chặn gộp.

## Lỗi phát hiện

Không phát hiện lỗi trong diff T-044.

Ghi nhận ngoài phạm vi (không chặn T-044, chuyển phiếu khác):

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T044-1 | Thấp | Client WordPress không chịu dữ liệu sai kiểu: `_plain` chỉ nhận chuỗi, `int(...)` không bắt lỗi | `seo_app/wordpress/client.py:156,158` (`name` của site/tài khoản), cùng loại ở `:181-185` (`_list_terms`: `name`, `id`, `count`), `:292`, `:319-324` (`_post_from`: `id`, `title`), `:154` (`me` không phải dict) | Site của chính chủ dự án (hoặc plugin lỗi) trả `"name": 123` / `null` / danh sách → `TypeError` (không phải `WordPressError`) → trang Kết nối WordPress hiện khung lỗi Streamlit kèm traceback (`client.showErrorDetails` mặc định `full` ở Streamlit 1.65: lộ đường dẫn thư mục trên máy, chỉ người đang mở app ở localhost thấy). Không lộ khóa, không đăng bài, không link/HTML | Thợ Máy: ép kiểu an toàn trong client (`_plain(str(x))` khi không phải chuỗi, `None` → `""`; lỗi `int()`/`KeyError`/sai kiểu gói thành `WordPressError` tiếng Việt), có test bằng `tests/fake_wordpress.py`. Gộp vào **T-042** (đang sửa đúng file `client.py`, tránh xung đột) nếu T-042 còn lượt; nếu không thì phiếu dọn lỗi Thấp mới, trước khi hết Giai đoạn 4 |
| LC-T044-2 | Thấp | `escape_link_syntax` không chặn autolink kiểu `<scheme:…>` (ký tự rộng 0 vẫn hợp lệ bên trong `<…>`) | `seo_app/sanitize.py:506` | Ở T-044 **không với tới**: tên mô hình không có `<` (`blind_test._MODEL_CHARS`), câu lỗi AI là câu cố định. Các chỗ dùng khác: chữ AI và chữ lưu nháp đều qua `clean_ai_text`/`strip_tags` trước (bỏ `<…>`); chỉ còn chữ chính chủ dự án tự gõ ở Soạn bài (`app/views/write.py:131,138,410`), tự gõ link thì tự thấy link, không phải tấn công | Không cần phiếu riêng. Ghi vào docstring/ghi chú khi phiếu nào sau này đụng `sanitize.py`: escape `<` khi theo sau là `scheme:` hoặc có `@`. Bắt buộc xét lại nếu có phiếu đưa chữ ngoài (không qua `strip_tags`/`clean_ai_text`) vào `escape_link_syntax` |

## Quyết định: định dạng vô hại còn sót trong câu lỗi thử mù

**Chấp nhận, không đặt điều kiện cho Thợ Máy.** Lý do:

- 3 chỗ trong `app/views/settings.py` (`:296-302` câu lỗi sau khi hiện tên, `:391` "Chưa chạy được", `:405` lỗi khi bấm chạy) dùng `escape_link_syntax`. Chữ đi vào chỉ gồm câu cố định của lớp AI / `validate_request` cộng tên mô hình đã qua `_MODEL_CHARS = [A-Za-z0-9._:/@-]+` (`seo_app/content/blind_test.py:65,252`); không chép chữ máy chủ AI (`_call` trả câu lỗi cố định, `blind_test.py:292-311`; đã soát `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`).
- Bảng chữ đó không có `< > [ ] ( ) & \ $ ~ *`, nên không dựng được link nội dòng/tham chiếu, HTML, autolink `<…>`, thực thể, LaTeX, chỉ thị màu `:red[…]`. Địa chỉ trần, `www.`, email do `break_autolinks` trong `escape_link_syntax` chặn (Soi Lỗi fuzz 3.000 tên, `test_blind_error_escape_fuzz_restricted_alphabet`).
- Phần còn sót (`_abc1_` nghiêng, `__abc1__` đậm, `:smile:`, `:material/home:`) chỉ là kiểu chữ, do chính người dùng gõ vào ô của mình trên máy mình. Không có đường nào cho người ngoài đưa chữ vào đây.
- Có khóa chặn hồi quy: `tests/test_soi_loi_t044.py::test_model_name_alphabet_matches_blind_test` đỏ ngay nếu ai nới bảng chữ. Khi đó phải xét lại quyết định này.

## Danh sách kiểm tra (rút gọn: U1 và các dòng liên quan)

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| U1 | Đạt | `grep unsafe_allow_html app/views/wordpress.py app/views/settings.py`: không có (chỉ có ở `home.py`, `write.py`, không đổi trong diff). Soát từng dòng `app/views/wordpress.py` (148 dòng): mọi chữ từ WordPress vào Markdown đều qua `plain()` = ép `str` + `escape_markdown` (`:35`, `:58`, `:62-68`, `:87`, `:142-147`); `escape_markdown` escape `` \`*_{}[]()<>#+-.!|~:$ `` và gộp dòng, rồi `break_autolinks` (`seo_app/text.py:40,44-50`). Caption `:40-43` lấy từ `.env` (chuỗi) vẫn qua `escape_markdown`. Chuyên mục/thẻ: `st.dataframe` (chữ thường); nhãn lựa chọn `st.multiselect` qua `format_func` không đọc Markdown (docstring Streamlit 1.65: chỉ `label`, `help` đọc Markdown). `post.id` là `int` (`client.py:319`), `len(terms)` là số, `st.link_button` dùng `edit_link` dựng từ `WORDPRESS_URL` + id số (`client.py:313-314`). Thử mù: xem mục quyết định ở trên |
| U2 | Đạt (không đổi) | Diff không đụng `app/main.py`, `.streamlit/config.toml`. `app/main.py:72-73` chặn mọi trang khi chưa đăng nhập; `server.address = "localhost"` |
| S1 | Đạt | `uvx detect-secrets scan` trên 8 file đổi: `"results": {}`. `git log -p origin/main..team/T-044 \| grep -inE "api[_-]?key\|password\|secret\|token"`: chỉ giá trị giả trong test (`mat-khau-thu-123`, `abcd efgh`, `khoa-gia-anthropic`, `khoa-gia-openai`, `hash_password(..., iterations=1_000)`) |
| S2 | Đạt | Câu lỗi hiện ra là câu `WordPressError` đã có sẵn (không chứa mật khẩu ứng dụng) và câu lỗi AI cố định; diff chỉ thêm escape |
| D1 | Đạt | Diff không đổi `pyproject.toml`, `uv.lock`; không thêm thư viện. Không chạy `pip-audit` vì không có thư viện mới (rút gọn) |
| D3 | Đạt | Test mới đi qua `tests/fake_wordpress.py` (`requests.Session` gắn `BaseAdapter` giả, không mở socket) và hãng AI giả; `tests/conftest.py:19` (`_block_real_network`, tự bật) chặn socket mạng thật cho mọi test. Bộ test chạy xanh với bộ chặn đó |
| Các dòng còn lại (S3, W1-W4, A1-A3, U3, F1-F3, D2) | Không áp dụng | Kiểm định rút gọn U1; diff không đụng cấu hình, client WordPress, lớp AI, đăng nhập, file/ảnh, `.gitignore`. Test Soi Lỗi xác nhận bài tạo thử vẫn `draft` (`test_uploaded_image_url_line_is_plain`) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy (rút gọn, không có thư viện mới) | — |
| bandit | Không chạy (rút gọn; diff chỉ thêm escape ở giao diện) | — |
| detect-secrets (8 file đổi) | 0 phát hiện | Có |
| Soát lịch sử git (`origin/main..team/T-044`) | Chỉ giá trị giả trong test | Có |
| `uv run pytest` (Windows 11, `9af9e43`) | 5378 passed, 10 skipped, 30 xfailed, 1 warning in 693.83s; 0 hỏng (khớp số Họa Sĩ báo) | Có |
| `uv run ruff check .` | All checks passed! | Có |

## Báo nhầm đã loại

Không có.

## Việc chuyển phiếu khác

- **LC-T044-1** (Thấp): client WordPress ép kiểu an toàn. Đề xuất đưa vào T-042 lượt sau (cùng file `seo_app/wordpress/client.py`), hoặc phiếu dọn lỗi Thấp mới cho Thợ Máy; xong trước khi hết Giai đoạn 4. Có thể kèm đề xuất nhỏ cho Chỉ Huy cân nhắc: đặt `client.showErrorDetails` gọn hơn trong `.streamlit/config.toml` để lỗi bất ngờ không hiện traceback (cần chủ dự án đồng ý vì ảnh hưởng việc gỡ lỗi).
- **LC-T044-2** (Thấp): không cần phiếu riêng; ghi chú cho phiếu sau đụng `seo_app/sanitize.py`.
- Ghi chú test của Họa Sĩ/Soi Lỗi (bộ dò `decode` hai lượt trong `tests/test_app_t044_safe_text.py` có thể báo nhầm với `&#…;`): không phải lỗi bảo mật, sửa khi tiện.

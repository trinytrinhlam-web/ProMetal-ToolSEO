# Báo cáo T-044 · Tên site và tên người dùng lấy từ WordPress hiện an toàn

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-044](../tickets/T-044-ten-site-tu-wordpress-hien-an-toan.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trên trang **Kết nối WordPress**, mọi chữ lấy từ website (tên site, địa chỉ site, tên tài khoản, vai trò, tiêu đề bài nháp, địa chỉ ảnh, câu lỗi có chữ của máy chủ) giờ chỉ hiện là chữ thường: không thành link bấm được, không in đậm hay thành thẻ HTML. Ở **Cài đặt → thử mù**, tên mô hình bạn gõ dạng `https://…`, `www.…` hay email không còn tự thành link trong câu lỗi. Bố cục và nội dung chữ người đọc thấy không đổi.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/wordpress.py` | Chữ từ WordPress và câu lỗi `WordPressError` qua `escape_markdown` trước khi vào Markdown (dòng 23, 29-30, 46, 50-56, 75, 130-134). `st.write` địa chỉ ảnh đổi sang `st.markdown` (cùng cách hiện). Không dùng `unsafe_allow_html` |
| `app/views/settings.py` | 3 chỗ hiện câu lỗi thử mù qua `escape_link_syntax` (dòng 297-303 câu lỗi sau khi hiện tên, 391 "Chưa chạy được", 405 lỗi khi bấm chạy) |
| `tests/test_app_t044_safe_text.py` | Mới, 33 ca `AppTest` (client WordPress và `run_blind_test` giả) |
| `tests/test_app_wordpress.py` | `test_check_connection_error_is_shown` so với `escape_markdown(...)` vì câu lỗi nay được escape (chữ hiện ra y hệt) |
| `tests/test_soi_loi_t031.py` | Bỏ `xfail(strict)` của `test_wordpress_site_name_is_not_a_link` (SL-T031-1 đã sửa; để nguyên thì XPASS strict làm đỏ bộ test). Thân test giữ nguyên |

Không sửa `seo_app/**`, `tests/conftest.py`, không thêm thư viện.

## Bằng chứng

```
$ uv run pytest            (Windows 11, worktree wt-T-044, commit a0ae171)
5325 passed, 10 skipped, 30 xfailed, 1 warning in 453.67s (0:07:33)

$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_app_t044_safe_text.py tests/test_settings_blind.py tests/test_soi_loi_t034.py -q
263 passed in 46.30s

# Test mới bắt được lỗi cũ: chép tạm app/views/{wordpress,settings}.py của main b5ff3b3 rồi chạy
$ uv run pytest tests/test_app_t044_safe_text.py -q
23 failed, 10 passed      (10 ca qua là ca tự kiểm bộ dò; cả 23 ca trên trang đều đỏ)
```

`tests/test_app_pages.py` nằm trong lượt chạy toàn bộ ở trên, qua hết.

**Test mới (`tests/test_app_t044_safe_text.py`):**
- Bộ dò link viết riêng: giải mã Markdown (bỏ `\x`, giải mã `&…;`, rộng hơn CommonMark), tìm địa chỉ trần, `www.`, email theo hai biểu thức của remark-gfm, cộng `](`/`][` và `<` chưa escape. `test_detector_catches_raw_hostile_text` bảo đảm bộ dò bắt được chữ độc khi chưa escape.
- `test_wordpress_texts_never_become_links` × 10 mẫu độc (link Markdown, ảnh Markdown, địa chỉ trần, `www.`, email, `<a>`, `<img onerror>`, `<https://…>`, link tham chiếu, `**`/`_`/`` ` ``/`#`) đặt vào tên site, tên tài khoản, vai trò, chuyên mục, thẻ, tiêu đề bài nháp. Đi hết 3 mục của trang. Mọi phần tử Markdown (markdown, caption, success, error, warning, info, title, header) không có link, không bật `allow_html`. Người đọc vẫn thấy nguyên chữ. Bảng chuyên mục/thẻ giữ nguyên tên.
- `test_wordpress_error_with_site_text_is_plain` × 3 nút: câu lỗi chứa cả 10 mẫu độc, không ra link, chữ hiện ra đúng câu gốc.
- `test_bad_wordpress_url_message_is_plain` (`WORDPRESS_URL=www.evil.example`), `test_account_email_in_caption_is_plain` (tên đăng nhập là email).
- `test_blind_reveal_error_with_url_model_is_plain` và `test_blind_run_error_with_url_model_is_plain` × 4 tên (`https://x.y`, `www.evil.example`, `ban@evil.example`, `http://evil.example/m`): tên vẫn qua bộ lọc tên (nút chạy bật), câu lỗi không ra link, chữ hiện ra y như cũ.

**Tự kiểm tra trên giao diện:** `uv run streamlit run app/main.py` → Kết nối WordPress → Kiểm tra kết nối, Tải chuyên mục và thẻ, Tạo bài nháp: chữ và bố cục như trước. Muốn thấy rõ: đổi tên website trong WordPress (Cài đặt → Tổng quan) thành `Ghé www.vidu.com` rồi bấm Kiểm tra kết nối, tên hiện là chữ thường, không bấm được.

## Đối chiếu tiêu chí xong

- [x] Không chữ nào từ WordPress thành link hay HTML trên trang, có test (`tests/test_app_t044_safe_text.py`, `tests/test_soi_loi_t031.py::test_wordpress_site_name_is_not_a_link` nay qua thật)
- [x] Câu lỗi thử mù có tên mô hình kiểu địa chỉ không thành link (LC-T034-1; 8 ca `test_blind_*_with_url_model_is_plain`)
- [x] Giữ bố cục đã duyệt (không đổi phần tử, nhãn hay thứ tự; chỉ đổi chuỗi đưa vào)
- [x] `tests/test_app_pages.py` vẫn qua; `uv run pytest` 0 hỏng, 0 lỗi trên Windows; `uv run ruff check .` sạch
- [x] Báo cáo này

## Rủi ro và điểm cần chú ý

- **Thử mù dùng `escape_link_syntax`, không dùng `escape_markdown`** (phiếu cho chọn một trong hai). Lý do: `escape_markdown` thêm `\` trước `.`, `-`, `:`… nên 4 test của Soi Lỗi/Họa Sĩ cũ so chuỗi con trong câu lỗi bị đỏ (`test_settings_blind.py::test_failed_candidate_shows_fixed_message_then_real_error`, `test_soi_loi_t019.py::test_ui_all_candidates_fail_no_traceback_no_key`, `::test_ui_broken_content_rules_shows_vietnamese_error`, `test_soi_loi_t019_luot2.py::test_ui_full_flow_three_vendors_names_hidden_until_scored`). `escape_link_syntax` chặn mọi dạng link (Markdown, địa chỉ trần, `www.`, email) mà chữ không đổi. Phần còn lại: tên mô hình chỉ gồm `[A-Za-z0-9._:/@-]` (`blind_test._MODEL_CHARS`), nên chỉ có thể ra **định dạng vô hại** như `_abc1_` thành nghiêng, `:smile:` thành biểu tượng. Không có HTML, không có link. Câu lỗi AI là câu cố định của lớp AI (T-026), không chép chữ máy chủ.
- `escape_markdown` gộp khoảng trắng liên tiếp thành một (tên site có 2 dấu cách sẽ hiện 1). Câu lỗi WordPress hiện là một dòng nên không mất gì.
- Chữ có ký tự rộng 0 (`AUTOLINK_BREAK`) chèn giữa địa chỉ: người đọc không thấy, nhưng nếu bôi đen sao chép địa chỉ site/ảnh sẽ kèm ký tự này (giống chữ AI từ T-031).
- Địa chỉ ảnh đại diện sau khi tải lên không còn bấm được (trước đây là link). Bài nháp vẫn mở được bằng nút «Mở bài trong trang quản trị WordPress» (địa chỉ dựng từ `WORDPRESS_URL`, không từ WordPress).
- `AppTest` không giả lập được tải file, nên dòng địa chỉ ảnh (`wordpress.py:134`) chỉ kiểm bằng đọc code, chưa có test chạy qua.
- `st.dataframe` (chuyên mục/thẻ) và nhãn lựa chọn của `multiselect` hiện chữ thường, không đọc Markdown, nên giữ nguyên tên gốc.

## Đề xuất

- **Soi Lỗi nên thử:** tên site / tên tài khoản dạng có thực thể HTML (`&#119;ww.x.com`, `&commat;`), chữ toàn khổ, U+200B có sẵn; câu lỗi 4xx có `message` WordPress dài nhiều dòng; xem trên trình duyệt thật (không chỉ `AppTest`) với site giả trả tên độc.
- **Lá Chắn nên thử (U1):** soát lại `app/views/wordpress.py` không còn chỗ nào đưa chữ WordPress vào Markdown chưa escape; định dạng vô hại còn lại ở câu lỗi thử mù (`_x1_`, `:material/…:`) có chấp nhận được không, hay muốn chặn thêm `_` đầu/cuối và `:` trong `validate_request` (thuộc Thợ Máy, `seo_app/content/blind_test.py`).

## Câu hỏi cho chủ dự án

Không có.

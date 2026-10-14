# Báo cáo T-006 · Sửa các lỗi Trung bình và Thấp của Giai đoạn 2

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-006](../tickets/T-006-sua-loi-nho-giai-doan-2.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Đã sửa cả 7 mục của phiếu. Những gì bạn thấy khác: app từ chối địa chỉ website bắt đầu bằng `http://` (phải là `https://`, để mật khẩu WordPress không đi trên mạng dạng không mã hóa); viết sai `config/ai.toml` thì hiện lời nhắc tiếng Việt thay vì trang lỗi; AI trả bài rỗng hoặc bản viết lại rỗng thì báo "bấm thử lại". Khi chạy kiểm thử trên máy công ty/máy nhà, test **không bao giờ đọc file `.env` thật** và khóa thật nữa. Không thêm thư viện mới (chỉ ghi tên `pydantic` vốn đã cài sẵn, theo đúng phần bạn đã duyệt).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | (1) Chỉ nhận `https://` (không phân biệt hoa thường). (7) `set_featured_image` chỉ cho bài nháp chính client này vừa tạo; ID lạ bị từ chối, không gửi request. (4) Bắt mọi `RequestException` còn sót, báo tên lỗi, không chép thông điệp thô. |
| `seo_app/ai/registry.py` | (2) `[tasks]` sai dạng, việc không phải bảng, `max_tokens` không phải số nguyên dương, `web_search` không phải `true/false` thật → `AIError` tiếng Việt. |
| `seo_app/ai/base.py` | (4) Thêm `redact_secrets`: che chuỗi giống khóa (`sk-…`, `AIza…`, `Bearer …`, `x-api-key: …`, `api_key=…`, `password=…`). |
| `seo_app/ai/anthropic_provider.py` | (4) Lỗi 400 qua `redact_secrets`; bắt thêm `anthropic.APIError` còn lại → `AIError` chỉ nêu tên lỗi. |
| `seo_app/content/workflow.py` | (3) Bài sau khi lọc không còn chữ (không mở bài, không nội dung mục) hoặc bản viết lại rỗng → `AIError`. |
| `seo_app/content/rules.py` | (4) `find_banned` so khớp sau khi chuẩn hóa Unicode NFC; câu trả về giữ nguyên như trong bài. |
| `seo_app/config.py` | (5) `load_settings()` tra `DEFAULT_ENV_FILE` **lúc gọi** (trước đây cố định lúc nạp module), nên test trỏ được sang file khác. Gọi có tham số vẫn như cũ. |
| `tests/conftest.py` | (5) Fixture tự động `_never_read_real_env`: trỏ `DEFAULT_ENV_FILE` sang file không tồn tại và xóa 12 biến của app khỏi môi trường cho mọi test. |
| `pyproject.toml`, `uv.lock` | (6) Thêm `"pydantic>=2"`. `uv lock`: chỉ thêm 2 dòng khai báo, **không gói nào đổi phiên bản** (pydantic vẫn 2.14.1, vẫn 57 gói). |
| `tests/test_content_edge_cases.py`, `tests/test_safety.py` | Gỡ 7 dấu `xfail` (8 trường hợp) đã sửa xong; sửa một chú thích. Không xóa test. |
| `tests/test_wordpress_client.py` | `test_set_featured_image`: tạo bài nháp trước rồi mới đặt ảnh (đúng luật mới). |
| `tests/test_phase2_fixes.py` (mới) | 37 trường hợp cho mọi mục của phiếu. |

Không sửa `app/`: các chỗ bắt lỗi trong `app/views/write.py` (`except AIError`) đã đủ vì mọi lỗi mới đều là `AIError`; trang WordPress đã bắt `WordPressError` khi tạo client.

## Bằng chứng

```
$ uv run pytest            # sau T-008, trước T-006
407 passed, 9 xfailed in 18.75s

$ uv run pytest            # sau T-006
452 passed, 1 xfailed in 18.93s

$ uv run ruff check .
All checks passed!

$ git diff uv.lock         # chỉ hai dòng
+    { name = "pydantic" },
+    { name = "pydantic", specifier = ">=2" },
```

## Đối chiếu tiêu chí xong

| Mục phiếu | Nguồn | Bằng chứng |
|---|---|---|
| 1. Bắt buộc `https://` | LC #4 | `client.py:94-105`; `test_wordpress_requires_https` (3), `test_wordpress_https_any_case_is_accepted` |
| 2. `ai.toml` sai kiểu, `web_search = "false"` | SL #4, #5 | `registry.py:31-71`; gỡ xfail `test_bad_value_types_in_ai_config_give_ai_error` (2), `test_web_search_string_false_is_not_true`, `test_non_numeric_max_tokens_shows_warning` (trang Soạn bài không sập); mới `test_bad_ai_config_values_give_clear_ai_error` (6), `test_project_ai_config_still_loads` |
| 3. AI trả rỗng | SL #6 | `workflow.py` (`write`, `rewrite_section`); gỡ xfail `test_empty_draft_is_reported`, `test_empty_rewrite_is_reported`; mới `test_draft_that_is_only_markup_is_reported_as_empty`, `test_draft_with_only_intro_is_accepted` |
| 4a. Unicode NFC | SL #7 | gỡ xfail `test_find_banned_handles_decomposed_vietnamese` |
| 4b. Lọc chuỗi giống khóa lỗi 400 | SL #2 | gỡ xfail `test_ai_400_error_message_is_filtered`; mới `test_redact_secrets_hides_key_like_strings` (6), `test_redact_secrets_keeps_normal_error_text` (3) |
| 4c. Lỗi mạng còn sót | LC #8 | `test_other_network_errors_become_wordpress_error` (4: InvalidURL, TooManyRedirects, ChunkedEncodingError, InvalidHeader), `test_other_anthropic_errors_become_ai_error_without_raw_message` |
| 5. Test không đọc `.env` thật | LC #5 | `test_tests_never_point_at_the_real_env_file`; `test_real_env_file_with_keys_is_not_seen_by_tests` (đối chứng: trỏ vào file có khóa thì thấy khóa; mặc định thì "chưa có khóa"); `test_app_pages_see_no_key_even_if_real_env_has_one` (trang Soạn bài thật qua `AppTest`, cùng cách đối chứng) |
| 6. Khai báo `pydantic` | LC #7 | `test_pydantic_is_declared_dependency`; diff `uv.lock` ở trên |
| 7. `set_featured_image` | LC #6 | `test_featured_image_refused_for_post_not_created_by_app` (không request nào được gửi), `test_featured_image_allowed_only_for_own_draft` |

- [x] Các test `xfail` tương ứng chuyển thành `passed` (8 trường hợp).
- [x] Báo cáo này.

**`xfail` còn lại (1):** `tests/test_safety.py::test_outside_data_in_prompts_is_marked_as_data_not_instructions` — Soi Lỗi #8 / Lá Chắn T-001 #2 (bọc dữ liệu ngoài trong prompt). Thuộc phiếu T-003 của Ngòi Bút (`seo_app/content/prompts.py`), không thuộc T-006.

## Rủi ro và điểm cần chú ý

- **Máy nào đang để `WORDPRESS_URL=http://…` trong `.env` sẽ không kết nối được nữa** (trang WordPress hiện lời nhắc đổi sang `https://`). Đây là chủ ý; README đã ghi `https://`.
- `set_featured_image` chỉ nhớ bài trong **một** đối tượng client. Streamlit tạo lại client mỗi lần trang chạy lại, nên muốn đặt ảnh cho bài vừa tạo thì phải làm trong cùng một lượt (hoặc truyền `featured_media` ngay trong `create_draft` như trang WordPress đang làm). Giai đoạn 5 cần lưu ý.
- `redact_secrets` là bộ lọc theo mẫu: che được các dạng khóa phổ biến, không phải mọi chuỗi bí mật có thể có. Lỗi ngoài 400 vẫn không chép thông điệp thô.
- `max_tokens` giờ phải là số nguyên trong TOML (`16000`), không nhận `"16000"` trong ngoặc kép. `config/ai.toml` hiện tại đúng dạng (có test).
- Fixture `_never_read_real_env` xóa các biến app khỏi môi trường của test; test nào cần giá trị phải tự `monkeypatch.setenv` (các test hiện có đều đã làm vậy).

## Đề xuất

- Họa Sĩ (khi tiện): đoạn cảnh báo `if not client.uses_https` ở `app/views/wordpress.py:23-27` giờ không bao giờ hiện (client đã từ chối http), có thể xóa. Tôi không sửa vì `app/` ngoài phạm vi.
- Lá Chắn: kiểm lại LC #4–#8 của T-001 để chuyển mốc gốc lên ĐẠT.
- Lá Chắn T-004 #5: cân nhắc ghi `3.12.11` (hoặc mới hơn) vào `.python-version`.

## Câu hỏi cho chủ dự án

Không có.

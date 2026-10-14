# Báo cáo T-020 · Nhập khóa API AI ngay trong app (phần Thợ Máy)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-020](../tickets/T-020-nhap-khoa-api-trong-app.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành (phần Thợ Máy; phần giao diện chờ Họa Sĩ) |

## Tóm tắt (cho chủ dự án)

Đã viết phần "máy" để app tự ghi khóa Claude, ChatGPT, Gemini vào file `.env` thay cho việc mở file bằng tay. App chỉ ghi được đúng 3 khóa này, giữ nguyên mọi dòng khác trong `.env`, và từ chối khóa có ký tự lạ (để không ai chèn thêm thứ khác vào file). Có thêm nút kiểm tra khóa Claude (hỏi Anthropic danh sách mô hình, không tốn tiền). Chưa có giao diện: Họa Sĩ sẽ làm tab "Kết nối" dựa trên phần này.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/env_file.py` | Mới: ghi/xóa khóa trong `.env`, kiểm tra giá trị, ghi an toàn, kiểm tra biến môi trường hệ điều hành, kiểm tra khóa Claude |
| `tests/test_env_file.py` | Mới: 82 test, chỉ dùng file tạm và client giả |

Không đụng `seo_app/storage/` (T-016 đang làm song song), không thêm thư viện.

## Bằng chứng

```
$ uv run pytest tests/test_env_file.py -q
82 passed in 1.73s

$ uv run pytest -q
1682 passed, 3 xfailed in 72.20s

$ uv run ruff check .
All checks passed!
```

Tên API Anthropic đã xác minh trong mã nguồn thư viện (`anthropic` 1.13.0 trong `.venv`): `Models.list(*, limit, timeout, …)` ở `anthropic/resources/models.py:107`; hàm gọi ngay (không lười) qua `get_api_list` (`_base_client.py:1611`); các lớp lỗi `AuthenticationError`, `PermissionDeniedError`, `RateLimitError`, `APITimeoutError`, `APIConnectionError`, `APIStatusError`, `AnthropicError` ở `anthropic/_exceptions.py`.

## Đối chiếu tiêu chí xong

1. Chỉ nhận 3 biến, mặc định `config.DEFAULT_ENV_FILE` tra lúc gọi: `seo_app/env_file.py:29`, `:43`, `:48`. Test: `test_default_file_is_looked_up_at_call_time`, `test_other_names_rejected` (kể cả `APP_PASSWORD_HASH`, `WORDPRESS_APP_PASSWORD`, tên viết thường).
2. Giữ nguyên dòng khác, chú thích, thứ tự; tạo file nếu chưa có; thay đúng dòng; xóa thì để trống: `_write_value` (`:118`). Test: `test_replace_existing_line_keeps_everything_else`, `test_append_when_missing`, `test_create_file_when_missing`, `test_commented_line_not_touched`, `test_similar_names_not_touched`, `test_export_and_spaces_variants_replaced`, `test_old_multiline_quoted_value_removed`, `test_crlf_line_endings_kept`, `test_bom_kept`, `test_clear_sets_empty_value_in_place`.
3. Chặn giá trị nguy hiểm, bỏ khoảng trắng hai đầu, tối đa 512 ký tự: `validate_key_value` (`:54`). Ngoài danh sách phiếu, chặn thêm theo kiểu "chỉ cho phép": chỉ nhận chữ/số ASCII và `- _ . : + / ~` (nên `$`, `\`, `=`, chữ có dấu, dấu cách không ngắt ` `, ` ` cũng bị chặn). Test: `test_dangerous_values_rejected` (22 trường hợp, file không đổi), `test_injection_cannot_add_other_variable`, `test_error_messages_never_contain_value`, `test_realistic_keys_accepted`.
4. Ghi file tạm cùng thư mục rồi `os.replace`, UTF-8, quyền `600` trên Mac/Linux, Windows bỏ qua: `_atomic_write` (`:187`). Test: `test_uses_os_replace_and_leaves_no_temp_file`, `test_failed_replace_keeps_old_file_and_cleans_temp`, `test_permissions_600`, `test_windows_skips_chmod`.
5. Kiểm tra khóa Claude: `client.models.list(limit=1, timeout=…)`, client tạo với `timeout` và `max_retries=0` (`:302`, `:304`), mọi thông báo qua `redact_secrets`; OpenAI/Gemini trả "Chưa hỗ trợ kiểm tra". Test: `test_check_ok_calls_models_list_with_timeout`, `test_check_errors_mapped`, `test_check_message_never_contains_key`, `test_check_reads_key_from_settings_when_not_given`, `test_check_other_providers_unsupported`, `test_check_with_real_client_class_hits_network_guard`.
6. Test không đọc/ghi `.env` thật, không gọi mạng: mọi test dùng `tmp_path` (fixture `env_path` trỏ `DEFAULT_ENV_FILE` sang file tạm), client giả; `conftest.py` vẫn chặn mạng (test cuối chứng minh client thật bị chặn và trả "unknown").

## Cách giao diện dùng (cho Họa Sĩ)

```python
from seo_app.env_file import (
    ALLOWED_KEYS,             # ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")
    EnvFileError,             # lỗi; str(exc) là câu tiếng Việt hiện thẳng được, không chứa khóa
    set_api_key,              # set_api_key(name, value) -> None
    clear_api_key,            # clear_api_key(name) -> None
    overridden_by_os_environ, # overridden_by_os_environ(name) -> bool
    check_api_key,            # check_api_key(name) -> KeyCheckResult(status, message, .ok)
)
```

- **Lưu**: `set_api_key("ANTHROPIC_API_KEY", gia_tri_o_nhap)` trong `try/except EnvFileError as exc: st.error(str(exc))`. Không cần tự `strip()`. Lưu xong (thành công hay lỗi) xóa giá trị khỏi ô nhập/`session_state`, rồi tải lại cấu hình (`load_settings()` hoặc cách app đang cache settings) để `Settings.status()` đổi ngay.
- **Xóa**: `clear_api_key(name)` sau bước hỏi lại. Chưa có khóa thì không làm gì, không lỗi.
- **Trạng thái "đã khai báo / chưa khai báo"**: dùng `Settings.status()` hoặc `bool(settings.anthropic_api_key)`; **không** hiển thị giá trị.
- **Cảnh báo biến môi trường**: nếu `overridden_by_os_environ(name)` là `True` thì báo "Khóa này đang được đặt trong biến môi trường của máy, khóa nhập ở đây sẽ không có hiệu lực". Hàm chỉ trả đúng/sai.
- **Kiểm tra**: `r = check_api_key("ANTHROPIC_API_KEY")` (không truyền khóa; hàm tự đọc khóa đang có hiệu lực từ `.env` + biến môi trường). `r.status` là một trong:
  - `"ok"` → `st.success(r.message)`
  - `"invalid"` → `st.error(r.message)` (khóa sai/bị thu hồi/không có quyền)
  - `"unknown"` → `st.warning(r.message)` (mạng, hết thời gian chờ, máy chủ lỗi, giới hạn lượt gọi)
  - `"missing"` → chưa khai báo khóa
  - `"unsupported"` → OpenAI/Gemini, chưa kiểm tra được
  Cuộc gọi chờ tối đa 15 giây (`CHECK_TIMEOUT_SECONDS`), nên bọc trong `st.spinner`.
- Test giao diện: đặt `monkeypatch.setattr(seo_app.config, "DEFAULT_ENV_FILE", tmp_path / ".env")` để không ghi `.env` thật (conftest đã trỏ sang file không tồn tại, nhưng `set_api_key` sẽ **tạo** file đó trong thư mục tạm chung của pytest; nên dùng `tmp_path` riêng của từng test). Giả `check_api_key` bằng `monkeypatch` để không gọi mạng.

## Rủi ro và điểm cần chú ý

- **Ghi nhiều tab cùng lúc**: không khóa file; hai lần lưu đồng thời thì lần sau thắng (mỗi lần ghi vẫn trọn vẹn nhờ `os.replace`). App một người dùng nên chấp nhận được.
- **`.env` là liên kết tắt (symlink)**: `os.replace` thay chính liên kết bằng file thường, không ghi ra file đích ngoài thư mục app. Suy luận từ hành vi `os.replace`, chưa có test riêng.
- **Biến trùng tên nhiều dòng**: mọi dòng đều được thay (để `.env` không còn giá trị cũ). Giá trị cũ nhiều dòng trong dấu nháy cũng được bỏ trọn.
- **Khóa hợp lệ có ký tự ngoài danh sách cho phép** (`A-Z a-z 0-9 - _ . : + / ~`): sẽ bị từ chối. Khóa Anthropic, OpenAI, Gemini hiện tại đều nằm trong tập này; nếu hãng đổi định dạng thì nới `_ALLOWED_VALUE` (`seo_app/env_file.py:34`).
- Trên Windows tệp không được đặt quyền riêng (theo phiếu).
- `RateLimitError` trả `"unknown"` dù về lý thuyết khóa có thể đúng: để người dùng thử lại thay vì báo nhầm "dùng được".

## Đề xuất

- Họa Sĩ làm tab "Kết nối" theo mục trên.
- Soi Lỗi: có thể thêm trường hợp `.env` là symlink và `.env` chỉ đọc (read-only).
- Khi T-018 duyệt thư viện OpenAI/Gemini: thêm nhánh kiểm tra trong `check_api_key` (hiện trả `"unsupported"`).

## Câu hỏi cho chủ dự án

Không có.

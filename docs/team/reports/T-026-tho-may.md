# Báo cáo T-026 · Sửa 4 lỗi mức Thấp của lớp AI

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-026](../tickets/T-026-loi-thap-lop-ai.md) |
| Nhánh | `team/T-026` (tạo từ `main` `ed0324e`), worktree `D:\ProMetal-ToolSEO\wt-T-026` |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Lớp AI giờ chịu được việc thư viện của hãng bị cài lệch phiên bản: thay vì trang Soạn bài hiện
lỗi kỹ thuật, app báo một câu tiếng Việt nhắc chạy lại `run.bat` / `run.command` (lệnh `uv sync`).
Khi máy chủ AI từ chối yêu cầu (lỗi 400), app chỉ hiện câu tiếng Việt cố định kèm mã lỗi và tên
mô hình, không bao giờ chép câu của máy chủ. Cả 3 hãng (kể cả nút **Kiểm tra** khóa trong Cài
đặt) luôn gọi đúng địa chỉ máy chủ chính thức, phần mềm khác trên máy không đổi được địa chỉ này
qua biến môi trường.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | Thêm địa chỉ chính thức `ANTHROPIC_URL`, `OPENAI_URL`, `GEMINI_URL` (`:55-57`); nhóm lỗi thư viện `LIBRARY_ERRORS` (ImportError, AttributeError, TypeError, KeyError) và `SETUP_ERRORS` (thêm `pydantic.ValidationError`) (`:61-64`); câu "uv sync" dùng chung `library_message`/`library_error` (`:67-76`); `safe_code` lọc mã lỗi ngắn (`:85`); `bad_request_error` dựng câu 400 cố định (`:92`). |
| `seo_app/ai/registry.py` | `make_provider` bắt `SETUP_ERRORS` cả lúc nhập module hãng **và** lúc tạo client (`:96-107`). |
| `seo_app/ai/anthropic_provider.py` | `base_url=ANTHROPIC_URL` (`:33`); `generate` bọc `_generate`, lỗi thư viện → "uv sync" (`:36-41`); lỗi 400 → câu cố định + loại lỗi đã lọc (`:81`). |
| `seo_app/ai/openai_provider.py` | `base_url=OPENAI_URL` (`:54`); `generate` bọc `_generate` nên `text_format()` (SL-3) và mọi bước khác đều được bắt (`:57-63`); lỗi 400 → câu cố định + `code`/`param` đã lọc (`:105-110`). |
| `seo_app/ai/gemini_provider.py` | `HttpOptions(base_url=GEMINI_URL, …)` (`:118`); `generate` bọc `_generate` (`:122-127`); cấu hình gọi dựng ở một chỗ `_content_config`, `ValidationError` của google-genai → "uv sync" (`:197-204`); JSON sai kiểu từ máy chủ (`ValidationError` lúc đọc trả lời) → "dữ liệu lạ" (`:154-164`); lỗi 400 → câu cố định + trạng thái, lỗi đã biết "User location is not supported" có câu gợi ý viết sẵn `KNOWN_400_HINTS` (`:83`, `:230-234`). |
| `seo_app/env_file.py` | `check_api_key` của 3 hãng: nhập thư viện + tạo client trong `try`, lỗi → câu "uv sync" (`:328-341`, `:368-381`, `:408-429`); `base_url` cố định (`:338`, `:378`, `:423`); lúc gọi, AttributeError/TypeError/ImportError → câu "uv sync" (`:325`); Claude thêm nhánh `except Exception` như 2 hãng kia (trước đây lỗi lạ làm sập nút). |
| `tests/test_ai_t026.py` | **Mới**, 87 trường hợp cho LC-1 → LC-4 (xem dưới). |
| `tests/test_ai_openai_gemini_soi_loi.py` | **Chỉ bỏ dấu `xfail`** của 2 test: `test_openai_public_helper_change_gives_vietnamese_error` (SL-3) và `test_gemini_library_missing_constant_gives_vietnamese_error` (SL-4). Không sửa gì khác. |
| `tests/test_ai_openai_gemini.py`, `tests/test_env_file.py` | Test của Thợ Máy kiểm tham số tạo client: thêm `base_url` vào giá trị mong đợi (chặt hơn, không nới): `test_check_openai_builds_client_without_retry`, `test_check_gemini_builds_client_without_retry`, `test_check_reads_key_from_settings_when_not_given`. |

### Test mới (`tests/test_ai_t026.py`)

- **LC-1 (lúc gọi):** `test_library_error_at_call_time_is_vietnamese` (3 hãng × 5 loại lỗi),
  `test_openai_helper_returning_other_shape_is_vietnamese`, `test_openai_helper_with_new_signature_is_vietnamese`,
  `test_gemini_config_rejected_by_library_is_vietnamese`, `test_gemini_missing_finish_reason_constant_at_call_time`,
  `test_gemini_wrongly_typed_json_is_strange_response_not_crash`, `test_library_errors_do_not_hide_normal_ai_errors`.
- **LC-2 (lúc nhập / tạo client):** `test_library_missing_name_at_import_or_build` (6 trường hợp, gồm `types.ThinkingLevel`,
  `HttpRetryOptions`, `FinishReason`, `anthropic.Anthropic`, `openai.OpenAI`), `test_client_rejecting_arguments_through_router`
  (3 hãng × TypeError/ValidationError, đi qua `AIRouter`), `test_provider_labels_match_registry`.
- **Nút Kiểm tra khóa:** `test_check_library_not_importable`, `test_check_client_rejecting_arguments`,
  `test_check_library_error_at_call_time`, `test_check_anthropic_other_exception_only_names_it`.
- **LC-3:** thư viện thật + mạng giả trả 400 có khóa không tiền tố ` key=…`, link Markdown, thẻ HTML:
  `test_anthropic_400_shows_only_fixed_sentence`, `test_openai_400_shows_only_fixed_sentence_with_code_and_param`,
  `test_openai_400_reasoning_retry_still_works_and_final_error_is_fixed`, `test_gemini_400_shows_only_fixed_sentence`,
  `test_gemini_known_400_gets_written_hint_not_server_text`, `test_openai_bad_code_from_server_is_dropped`,
  `test_unsafe_codes_are_dropped` (12 dạng), `test_safe_codes_are_kept`, `test_anthropic_400_credit_message_still_recognised`.
- **LC-4:** fixture `evil_base_urls` đặt `OPENAI_BASE_URL`, `ANTHROPIC_BASE_URL`, `GOOGLE_GEMINI_BASE_URL`,
  `GOOGLE_VERTEX_BASE_URL` = `https://evil.example/`. `test_libraries_would_follow_env_without_fixed_base_url` (chứng
  minh biến có tác dụng thật nếu không truyền `base_url`), `test_providers_point_to_official_urls_despite_env`,
  `test_generate_calls_official_host_despite_env` và `test_check_api_key_calls_official_host_despite_env` (bọc hàm tạo
  client của 3 thư viện để ghi lại địa chỉ **thật** mà thư viện gọi tới qua `MockTransport`: luôn là máy chủ chính thức,
  `https`), `test_official_urls_are_https_official_hosts`.

Kiểm chứng test có tác dụng: chạy `tests/test_ai_t026.py` với code cũ (`ed0324e`, chỉ thay `base.py` mới
để nhập được tên mới): **65 failed, 22 passed**. 22 test qua là test đơn vị của `safe_code`/hằng địa chỉ
và test giữ hành vi cũ (không đổi gì sai), đúng như mong đợi.

## Bằng chứng

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_ai_t026.py
87 passed in 9.26s

$ uv run pytest -q tests/test_ai_openai_gemini_soi_loi.py tests/test_ai_openai_gemini.py tests/test_ai.py tests/test_safety.py tests/test_env_file.py
398 passed, 4 skipped in 16.98s
```

Toàn bộ test trên Windows (máy dự án, cùng lúc Soi Lỗi chạy T-027):

```
# Trước khi sửa (team/T-026 = main ed0324e)
$ uv run pytest -q -rfE
145 failed, 2161 passed, 10 skipped, 5 xfailed, 63 warnings, 7 errors in 224.35s

# Sau khi sửa
$ uv run pytest -q -rfE
145 failed, 2250 passed, 10 skipped, 3 xfailed, 54 warnings, 7 errors in 228.24s
```

Đối chiếu bằng script so tên test hỏng với danh sách đỏ sẵn trên Windows (khớp theo tiền tố vì một số tên dài bị cắt):

```
$ uv run python compare_failures.py t026_before.txt windows_baseline_failures.txt
Số test hỏng: 152
Nằm ngoài danh sách đỏ sẵn: 0

$ uv run python compare_failures.py t026_after.txt windows_baseline_failures.txt
Số test hỏng: 152
Nằm ngoài danh sách đỏ sẵn: 0
```

Chênh lệch trước/sau: **+89 passed** = 87 test mới + 2 test SL-3, SL-4 được bỏ `xfail` (5 → 3 xfailed;
3 xfail còn lại là test cũ ngoài phạm vi). 152 test hỏng còn lại đều nằm trong danh sách đỏ sẵn trên
Windows (phiếu T-027), không có test nào mới hỏng. Lần chạy này không gặp test đo tốc độ chập chờn.

```
```

## Đối chiếu tiêu chí xong

- [x] **LC-1 (= SL-3):** lỗi thư viện lúc gọi của cả 3 hãng → `AIError` "uv sync" (`anthropic_provider.py:36-41`,
  `openai_provider.py:57-63`, `gemini_provider.py:122-127`, `:197-204`). Test SL-3 đã bỏ `xfail` và qua.
- [x] **LC-2 (= SL-4):** lúc nhập module và lúc tạo client (`registry.py:96-107`; `env_file.py` cho nút Kiểm tra).
  Test SL-4 đã bỏ `xfail` và qua.
- [x] **LC-3:** lỗi 400 của 3 hãng chỉ hiện câu cố định + "lỗi 400" + mã lỗi đã lọc + tên mô hình (`base.py:92`).
  Mã/tham số chỉ giữ khi là chữ cái không dấu nối bằng `_`/`.`, tối đa 40 ký tự (không số, không dấu cách,
  không ký tự Markdown/HTML).
- [x] **LC-4:** `base_url` cố định ở 6 chỗ tạo client (3 provider + 3 hàm kiểm tra khóa); test chứng minh biến
  môi trường giả không có tác dụng, địa chỉ thật được gọi là máy chủ chính thức.
- [x] Test cho mọi nhánh mới, không gọi mạng (mạng giả `MockTransport`, conftest vẫn chặn socket).
- [x] `uv run ruff check .` sạch.
- [x] pytest: không có test hỏng nào ngoài danh sách đỏ sẵn trên Windows; mọi test mới và 2 test được bỏ `xfail` đều qua.

## Rủi ro và điểm cần chú ý

1. **Bắt rộng lỗi kiểu Python.** `generate` của 3 hãng đổi mọi `ImportError`/`AttributeError`/`TypeError`/`KeyError`
   thành câu "uv sync". Nếu sau này code của chính app có lỗi loại đó trong `generate`, người dùng cũng thấy câu
   "uv sync" (lỗi gốc vẫn giữ trong `__cause__`, traceback đầy đủ khi gỡ lỗi). Chính tôi đã gặp một lần khi viết test
   (gói provider hai lần → `AttributeError` → câu "uv sync"), nên test phải kiểm nội dung kết quả, không chỉ kiểu lỗi.
2. **google-genai ném `AttributeError` khi máy chủ/proxy trả JSON lạ** (ví dụ `{"candidates": "x"}`, tôi đã thử bằng
   thư viện thật). Trường hợp này giờ ra câu "uv sync" thay vì "dữ liệu lạ". Không lộ gì, chỉ là câu gợi ý chưa trúng;
   JSON sai kiểu (`ValidationError`) thì vẫn ra "dữ liệu lạ".
3. **Test Soi Lỗi mong có chữ "User location".** `test_gemini_other_400_is_not_reported_as_bad_key[...FAILED_PRECONDITION...]`
   (file của Soi Lỗi, tôi không sửa) kiểm câu báo có "User location", tức là đang mong chép câu máy chủ. Tôi giải quyết
   bằng bảng lỗi đã biết `KNOWN_400_HINTS`: câu máy chủ chỉ dùng để **nhận ra** lỗi, câu hiện lên là câu viết sẵn trong
   code (có cụm "User location is not supported" trong ngoặc và gợi ý tắt VPN). Đúng yêu cầu LC-3 nhưng Soi Lỗi nên
   xem lại test đó.
4. **Nút Kiểm tra khóa:** lúc gọi, `KeyError` vẫn chỉ nêu tên lỗi (không đổi sang "uv sync"), vì test của Soi Lỗi
   `test_check_generic_exception_only_names_the_error` yêu cầu đúng câu đó và `KeyError` lúc này có thể do dữ liệu trả về.
5. **Ngoài phạm vi, ghi nhận cho Lá Chắn:** thư viện vẫn đọc một số biến môi trường khác không đổi địa chỉ nhưng ảnh
   hưởng đường đi: `HTTPS_PROXY`/`HTTP_PROXY`, `SSL_CERT_FILE` (httpx/httpx2 `trust_env`), `OPENAI_CUSTOM_HEADERS`,
   `ANTHROPIC_CUSTOM_HEADERS` (thêm header). Kiểm tra chứng chỉ SSL vẫn bật nên proxy không đọc được nội dung nếu không
   cài chứng chỉ riêng vào máy. Nếu muốn khóa chặt hơn cần phiếu riêng (ví dụ `trust_env=False`), có thể ảnh hưởng người
   dùng mạng công ty cần proxy.
6. Gemini: đổi `ThinkingConfig(...)`/`Tool(...)` sang dạng dict để mọi lỗi kiểm tham số nằm ở `_content_config`. Nội
   dung gửi đi không đổi (test `test_gemini_config_contents_still_correct`, `test_gemini_real_library_research_sends_only_google_search` của Soi Lỗi vẫn qua).

## Đề xuất

- **Soi Lỗi:** thử thêm các dạng thư viện lệch (đổi chữ ký `beta.messages.stream`, `responses.create`, bỏ thuộc tính
  `parsed_output`), và xem lại test "User location" ở mục rủi ro 3.
- **Lá Chắn:** kiểm S2 (câu 400 không còn chữ nào từ máy chủ trừ mã đã lọc qua `safe_code`), W4 (6 chỗ tạo client có
  `base_url` cố định), và mục rủi ro 5 (proxy/header qua biến môi trường).

## Câu hỏi cho chủ dự án

Không có.

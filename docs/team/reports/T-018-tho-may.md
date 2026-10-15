# Báo cáo T-018 · Thêm AI ChatGPT (OpenAI) và Gemini (Google)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-018](../tickets/T-018-them-openai-gemini.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành (nhánh `team/T-018`) |

## Tóm tắt (cho chủ dự án)

App giờ viết bài được bằng **Gemini** và **ChatGPT**, không chỉ Claude. Muốn đổi hãng cho một việc
(nghiên cứu, dàn ý, viết, viết lại, rà soát), chỉ cần sửa `provider` và `model` trong
`config/ai.toml`. Bước nghiên cứu vẫn tìm web thật (Gemini dùng Google Search, ChatGPT dùng công cụ
tìm web của OpenAI). Phần logic cho nút **Kiểm tra** khóa ChatGPT và Gemini đã có; nút trên giao
diện do Họa Sĩ làm ở T-023. Chưa đổi mô hình mặc định: `config/ai.toml` vẫn dùng Claude.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/openai_provider.py` (mới) | `OpenAIProvider`: Responses API, kết quả có khuôn `json_schema` (strict), `reasoning.effort`, công cụ `web_search` (vị trí VN), `store=False`, timeout 900 giây, thử lại 3 lần, đổi mọi lỗi sang `AIError` tiếng Việt. |
| `seo_app/ai/gemini_provider.py` (mới) | `GeminiProvider`: `models.generate_content` có `response_schema`, `thinking_level`, Google Search grounding; mô hình 1.x/2.x tìm web hai lượt; timeout 900 giây, thử lại 3 lần; đổi lỗi sang `AIError`. |
| `seo_app/ai/registry.py` | `SUPPORTED` gồm `openai`, `gemini`; `make_provider` tạo đúng provider; thiếu khóa thì chỉ tới **Cài đặt → 🔌 Kết nối**. |
| `seo_app/ai/base.py` | `redact_secrets` che thêm tham số `key=` trong địa chỉ (`…?key=…`, `&key=…`). |
| `seo_app/ai/__init__.py` | Sửa docstring (bỏ "OpenAI, Gemini sẽ thêm sau"). |
| `seo_app/env_file.py` | `check_api_key` kiểm được cả 3 khóa qua bảng `_CHECKERS`; thêm `_check_openai`, `_check_gemini`; gom hàm che khóa thành `_result`. |
| `pyproject.toml`, `uv.lock` | Thêm `openai`, `google-genai` (`uv add`). |
| `tests/test_ai_openai_gemini.py` (mới) | 41 hàm test (116 trường hợp), dùng client giả. |
| `tests/test_ai.py`, `tests/test_env_file.py` | Sửa 2 test cũ (xem mục riêng bên dưới). |

## Thư viện đã thêm (chủ dự án duyệt 2026-10-14)

| Thư viện | Phiên bản | Giấy phép | Nguồn |
|---|---|---|---|
| `openai` | 3.31.0 | Apache-2.0 | OpenAI (chính hãng) |
| `google-genai` | 2.30.1 | Apache-2.0 | Google (chính hãng) |

Thư viện phụ mới vào `uv.lock` (do hai thư viện trên kéo theo):

| Thư viện | Phiên bản | Giấy phép | Ai kéo theo |
|---|---|---|---|
| `httpx` | 0.28.1 | BSD-3-Clause | openai, google-genai |
| `httpcore` | 1.0.9 | BSD-3-Clause | httpx |
| `distro` | 1.9.0 | Apache-2.0 | openai |
| `google-auth` | 2.62.0 | Apache-2.0 | google-genai |
| `cryptography` | 50.0.2 | Apache-2.0 OR BSD-3-Clause | google-auth |
| `cffi` | 2.1.1 | MIT-0 | cryptography |
| `pycparser` | 3.11 | BSD-3-Clause | cffi |
| `pyasn1` | 0.6.4 | BSD-2-Clause | google-auth |
| `pyasn1-modules` | 0.4.2 | BSD | google-auth |
| `tenacity` | 9.1.4 | Apache-2.0 | google-genai (thử lại) |

Thay đổi khác trong `uv.lock`: `websockets` **hạ** từ 17.2 xuống 16.1.1 (google-genai đòi bản 16).
Streamlit cũng dùng `websockets`; toàn bộ test giao diện (`tests/test_app*.py`) vẫn qua.

Quét lỗ hổng (toàn bộ thư viện trong `uv.lock`, xuất bằng `uv export`):

```
$ uv export --no-hashes --no-emit-project -o req.txt
$ uvx pip-audit -r req.txt --no-deps --disable-pip
No known vulnerabilities found
```

## Bảng quy đổi `effort`

| `effort` trong app | ChatGPT (`reasoning.effort`) | Gemini (`thinking_level`) |
|---|---|---|
| low | low | LOW |
| medium | medium | MEDIUM |
| high | high | HIGH |
| xhigh | xhigh | HIGH |
| max | max | HIGH |

- OpenAI có đủ 5 mức cùng tên (`openai/types/shared/reasoning_effort.py` trong thư viện).
- Gemini chỉ có `minimal/low/medium/high` (`types.ThinkingLevel`); `minimal` không dùng vì quá nông.
- **Mô hình không suy nghĩ** (hoặc không nhận mức đã chọn): máy chủ báo lỗi 400 nhắc tới
  `reasoning` / `thinking`. Provider gọi lại **đúng một lần** không kèm tham số đó, không báo lỗi
  (`openai_provider.py:62-68`, `gemini_provider.py:143-150`; test
  `test_openai_model_without_reasoning_is_retried_without_it`,
  `test_gemini_model_without_thinking_is_retried_without_it`). Lỗi 400 khác thì không gọi lại.
- Bảng này cũng ghi trong docstring đầu mỗi file provider.

## Tìm web cùng kết quả có khuôn

| Hãng | Cách làm | Bằng chứng |
|---|---|---|
| ChatGPT | Một lượt gọi: công cụ `{"type": "web_search", "user_location": VN}` + `text.format = json_schema`. OpenAI cho dùng cùng lúc. | `test_openai_web_search_uses_only_the_search_tool` |
| Gemini 3 trở lên (`gemini-3.x`, `gemini-4-argon`) | Một lượt gọi: `tools=[google_search]` + `response_schema`. Google cho dùng cùng lúc từ Gemini 3 (tài liệu ghi là bản preview). | `test_gemini_new_model_searches_and_formats_in_one_call` |
| Gemini 1.x / 2.x | Hai lượt. Lượt 1: tìm Google, ghi chép bằng chữ (không khuôn). Lượt 2: không công cụ, định dạng ghi chép theo khuôn `Research`. Ghi chép bọc trong khung `<du_lieu_tham_khao>` bằng đúng hàm `_block` của phần nội dung, nên ghi chép không tự đóng khung được. Ghi chép rỗng thì báo lỗi, không âm thầm bỏ tìm web. | `test_gemini_legacy_model_searches_then_formats`, `test_gemini_legacy_model_empty_notes_is_an_error`, `test_content_writer_runs_on_gemini[gemini-2.5-pro]` |

AI chỉ có đúng một công cụ (tìm web), và chỉ ở việc bật `web_search = true` (security A2).

## Đề xuất mô hình cho từng việc (chưa sửa `config/ai.toml`)

Tên mô hình tra ngày 2026-10-14 trên trang chính thức:
[Gemini models](https://ai.google.dev/gemini-api/docs/models),
[Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/latest-model),
[Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking),
[OpenAI models](https://developers.openai.com/api/docs/models).

**Gemini** (chủ dự án định dùng chính):

| Việc | model | effort | Ghi chú |
|---|---|---|---|
| research | `gemini-4-argon` | medium | Tìm Google + khuôn trong một lượt |
| outline | `gemini-4-argon` | medium | |
| write | `gemini-4-argon` | high | |
| rewrite | `gemini-3.8-flash` | medium | Nhanh, rẻ hơn cho viết lại một phần |
| review | `gemini-4-argon` | medium | Cần soi kỹ văn phong |

Phương án tiết kiệm: dùng `gemini-3.8-flash` cho mọi việc. `effort = "xhigh"`/`"max"` với Gemini
bằng `high`.

**ChatGPT:**

| Việc | model | effort | Ghi chú |
|---|---|---|---|
| research | `gpt-6.1-sol` | medium | Có `web_search` |
| outline | `gpt-6.1-sol` | medium | |
| write | `gpt-6-astra` | high | Mô hình mạnh nhất |
| rewrite | `gpt-6.1-sol` | medium | |
| review | `gpt-6.1-sol` | medium | |

Phương án tiết kiệm: `gpt-6-luna` cho rewrite và review.

Giá theo trang Gemini 4 Argon: 2 USD / 1 triệu token vào, 10 USD / 1 triệu token ra (giá giới
thiệu tới 30/11/2026, từ 1/12/2026 tăng gấp đôi); **không dùng được ở gói miễn phí**. Giá ChatGPT
tôi chưa xác minh được từ trang chính thức, cần xem lại trước khi chốt.

## Các test cũ đã sửa

| Test cũ | Sửa thành | Lý do |
|---|---|---|
| `tests/test_ai.py::test_other_providers_are_not_supported_yet` (mong lỗi "OpenAI chưa được hỗ trợ") | `test_openai_and_gemini_are_supported`: `make_provider` trả `OpenAIProvider` / `GeminiProvider` | Phiếu yêu cầu hỗ trợ hai hãng |
| `tests/test_env_file.py::test_check_other_providers_unsupported` (mong `status == "unsupported"`) | `test_check_other_providers_now_supported`: kiểm qua client giả, ra `ok`, gọi đúng 1 lần | `check_api_key` nay kiểm được hai khóa |

Không xóa hay `skip` test nào. Trạng thái `"unsupported"` vẫn còn trong `CheckStatus` vì giao diện
có thể đang dùng, nhưng `check_api_key` không trả trạng thái này nữa.

## Bằng chứng

```
$ uv run pytest
1987 passed, 3 xfailed in 87.91s (0:01:27)

$ uv run ruff check .
All checks passed!
```

Test chính trong `tests/test_ai_openai_gemini.py`:
- Trả đúng khuôn: `test_openai_returns_validated_schema_and_sends_settings`, `test_gemini_returns_validated_schema_and_sends_settings`.
- Sai khuôn, rỗng, bị cắt, bị chặn: `test_openai_bad_results`, `test_gemini_bad_results`.
- Từng loại lỗi (sai khóa, không có quyền, không có mô hình, giới hạn gọi, hết tiền, lỗi máy chủ, quá lâu, mất mạng): `test_openai_errors_become_vietnamese`, `test_gemini_errors_become_vietnamese`.
- Thông báo lỗi không chứa khóa giả: `test_openai_error_never_contains_key`, `test_gemini_error_never_contains_key` (cả khóa trong `?key=` và header `x-goog-api-key`), `test_check_message_never_contains_key`, `test_redact_hides_google_key_in_url_and_header`.
- `repr` của provider không chứa khóa: `test_provider_repr_has_no_key`.
- Quy trình viết bài trọn vẹn qua `ContentWriter` (nghiên cứu → dàn ý → viết + tự rà soát → viết lại): `test_content_writer_runs_on_gemini[gemini-4-argon]`, `[gemini-2.5-pro]`, `test_content_writer_runs_on_openai`.
- Kiểm tra khóa: `test_check_openai_*`, `test_check_gemini_*` (gọi danh sách mô hình, timeout, không thử lại, client thật bị conftest chặn mạng thì ra `unknown`).

## Đối chiếu tiêu chí xong

- [x] Đổi `provider = "gemini"`/`"openai"` là chạy được quy trình viết bài (`test_content_writer_runs_on_gemini`, `test_content_writer_runs_on_openai`; cấu hình đọc từ file `ai.toml` tạm).
- [x] `check_api_key` kiểm được khóa ChatGPT và Gemini (`seo_app/env_file.py:343`, `:373`).
- [x] `uv run pytest`, `uv run ruff check .` sạch.
- [x] Có test cho mọi nhánh logic mới.
- [x] Báo cáo có bảng đề xuất mô hình.

## Rủi ro và điểm cần chú ý (mời Soi Lỗi, Lá Chắn soi kỹ)

1. **Hàm nội bộ của thư viện openai:** `openai_provider.py` dùng `type_to_text_format_param` từ
   `openai.lib._parsing._responses` để tạo khuôn `json_schema`. Lý do: tự kiểm tra trạng thái
   (`incomplete`, `refusal`) **trước** khi đối chiếu khuôn, để báo đúng lỗi "dài quá max_tokens"
   thay vì "sai khuôn". Phiên bản đã khóa trong `uv.lock`; nếu nâng thư viện mà hàm này đổi, test
   `test_openai_returns_validated_schema_and_sends_settings` sẽ báo ngay.
2. **Gọi lại khi lỗi 400 nhắc tới `reasoning`/`thinking`:** dựa vào chữ trong thông điệp lỗi của
   máy chủ. Nếu hãng đổi câu chữ, sẽ hiện lỗi "không nhận yêu cầu" thay vì tự bỏ qua (không nguy
   hiểm, chỉ kém tiện).
3. **Khóa Gemini sai trả 400, không phải 401:** nhận ra qua `API_KEY_INVALID` / "API key not valid"
   (`gemini_provider.py:182`). Đã có test.
4. **`check_api_key` của ChatGPT và Gemini có `except Exception`** ở cuối: chỉ nêu tên lỗi, không
   chép thông điệp, để nút Kiểm tra không làm sập trang (google-genai không gom lỗi về một lớp
   chung; client OpenAI không thử lại thì lỗi lạ từ tầng mạng lọt ra nguyên dạng). Phần
   `generate` không bắt chung như vậy.
5. **Khóa trong bộ nhớ:** `repr(GeminiProvider)` không chứa khóa, nhưng đối tượng nội bộ của
   google-genai (`client._api_client._http_options`) có header `x-goog-api-key`. App không in đối
   tượng này ra đâu; ghi lại để Lá Chắn biết.
6. **Gemini 1.x/2.x tìm web hai lượt:** tốn gấp đôi lượt gọi ở bước nghiên cứu. Gemini 3 trở lên
   không bị.
7. `store=False` với OpenAI: bài không được lưu trên máy chủ OpenAI.
8. `uv run ruff format --check .` báo `seo_app/sanitize.py` chưa định dạng từ trước (không thuộc
   phiếu này, không sửa). Các file của phiếu đã định dạng.

## Đề xuất

- **Họa Sĩ (T-023):** bật nút **Kiểm tra** cho ChatGPT và Gemini trong Cài đặt → 🔌 Kết nối;
  `check_api_key("OPENAI_API_KEY")` / `check_api_key("GEMINI_API_KEY")` trả `ok`/`invalid`/
  `unknown`/`missing` như Claude (không còn `unsupported`). Test
  `tests/test_settings_keys.py::test_check_only_for_claude` mang tên cũ, nên đổi theo khi làm.
- **Ngòi Bút:** cập nhật chú thích đầu `config/ai.toml` (dòng "openai và gemini sẽ thêm sau"),
  và nếu chủ dự án đồng ý thì đổi mô hình theo bảng đề xuất ở trên.
- **Thư Ký:** README mục AI: nói rõ đã dùng được Gemini, ChatGPT; cách đổi hãng trong
  `config/ai.toml`; Trạng thái trong `CLAUDE.md` (Giai đoạn 2: xong provider OpenAI/Gemini).

## Câu hỏi cho chủ dự án

1. Chuyển các việc sang Gemini theo bảng đề xuất (Argon cho nghiên cứu/dàn ý/viết/rà soát, 3.8
   Flash cho viết lại) không? **Đề xuất: có**, sau khi thử vài bài.
2. Tài khoản Gemini đã bật thanh toán chưa? Gemini 4 Argon **không dùng được ở gói miễn phí**.
   Nếu chưa: dùng `gemini-3.8-flash` cho mọi việc.

## Lượt 2 (2026-10-15) · sửa theo báo cáo Soi Lỗi `T-018-soi-loi.md`

### Đã sửa

| Lỗi | Cách sửa | File |
|---|---|---|
| **SL-1** (Trung bình): Gemini nhận dữ liệu không phải JSON (trang HTML của Wi-Fi/proxy) hoặc dữ liệu nén hỏng thì lỗi thô lọt ra | Bắt `json.JSONDecodeError`, `errors.UnknownApiResponseError`, `httpx.DecodingError` → `AIError` "Máy chủ Gemini trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy). Kiểm tra mạng rồi thử lại." Không chép thông điệp thô. Đổi `httpx.TransportError` thành `httpx.RequestError` (thêm cả `TooManyRedirects`) → "Không kết nối được tới Gemini". Không bắt chung `ValueError`, để lỗi lập trình không bị gọi nhầm là "lỗi mạng". | `seo_app/ai/gemini_provider.py` (`generate`) |
| SL-1, phía OpenAI | Đã kiểm: không có lỗ tương tự. Thư viện openai tự bọc dữ liệu lạ thành `APIResponseValidationError` / `APIConnectionError` (đều là `OpenAIError`), provider đã đổi sang `AIError`; Soi Lỗi cũng đã thử. Không sửa. | — |
| **SL-2** (Thấp): phụ thuộc hàm nội bộ `type_to_text_format_param` | **Bỏ hẳn phụ thuộc**: dựng khuôn `json_schema` bằng hàm công khai `openai.pydantic_function_tool` (xuất ở `openai/__init__.py`), cho ra JSON Schema strict giống hệt cách `responses.parse` làm (test so sánh với hàm nội bộ cho cả 6 khuôn). Thêm lớp an toàn: `make_provider` bắt `ImportError` khi nhập module của bất kỳ hãng nào → `AIError` "Thư viện của … chưa cài hoặc sai phiên bản. Đóng app, chạy lại run.bat / run.command (hoặc lệnh uv sync)…". | `seo_app/ai/openai_provider.py` (`text_format`), `seo_app/ai/registry.py` (`make_provider`) |
| Ghi chú cho Lá Chắn: `redact_secrets` không che `"key": "…"` | Đã thêm: che giá trị của trường tên **đúng** `key` trong JSON/dict (`"key": "…"`, `'key': '…'`). Không che `"monkey"`, `"keyword"`, câu thường có chữ "key". `key%3D…` và `key=` đầu dòng vẫn không che (không có đường thật để khóa đi vào dạng này; khóa thật có tiền tố `AIza`/`sk-` vẫn bị che). | `seo_app/ai/base.py` |

Mục 1 trong "Rủi ro và điểm cần chú ý" ở lượt 1 (hàm nội bộ openai) **không còn đúng**: code không
còn nhập gì từ `openai.lib` (có test `test_openai_text_format_uses_public_api_and_matches_library`).

### Test

Bỏ dấu `xfail(strict=True)` ở đúng 3 test của Soi Lỗi (`tests/test_ai_openai_gemini_soi_loi.py`):

| Test | Thay đổi |
|---|---|
| `test_gemini_html_response_becomes_vietnamese_error` | Chỉ bỏ dấu `xfail`. |
| `test_gemini_decoding_error_becomes_vietnamese_error` | Chỉ bỏ dấu `xfail`. |
| `test_openai_internal_helper_missing_gives_vietnamese_error` | Bỏ dấu `xfail` **và sửa nội dung**: vì đã bỏ phụ thuộc hàm nội bộ, xóa hàm đó thì ChatGPT **vẫn chạy** (không còn lỗi để báo). Test giờ khẳng định (1) mất hàm nội bộ → `make_provider("openai")` vẫn tạo được provider; (2) module provider không nhập được (`ImportError`) → `AIError` nhắc `uv sync`. Mời Soi Lỗi xem lại test này. |

Không đụng test nào khác của Soi Lỗi. Test mới của tôi (trong `tests/test_ai_openai_gemini.py`):
`test_gemini_strange_response_becomes_vietnamese_error` (3 loại lỗi, có khóa giả trong thông
điệp), `test_gemini_other_request_errors_are_network_errors`,
`test_openai_text_format_uses_public_api_and_matches_library`,
`test_broken_vendor_library_gives_vietnamese_error` (3 hãng), `test_redact_json_key_field`,
`test_redact_json_key_field_keeps_ordinary_text`. Test cũ `test_content_writer_runs_on_openai` đổi
tên hàm gọi (`type_to_text_format_param` → `text_format`).

### Bằng chứng

```
$ uv run pytest
2099 passed, 3 xfailed in 90.59s (0:01:30)
# 3 xfailed còn lại là test cũ không thuộc T-018 (R4-3, SL-7).

$ uv run ruff check .
All checks passed!
```

### Chưa làm (để Chỉ Huy quyết)

- Gợi ý của Soi Lỗi: lỗi 400 của OpenAI hiện nguyên chuỗi `Error code: 400 - {...}` (đã che khóa),
  khó đọc. Có thể chỉ lấy `error.message` trong body. Không thuộc 2 lỗi được giao nên chưa sửa.

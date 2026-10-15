# Báo cáo T-018 · Kiểm thử ChatGPT (OpenAI) và Gemini (Google)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-018](../tickets/T-018-them-openai-gemini.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành. Kết luận: **ĐẠT có điều kiện** (2 lỗi mức Thấp–Trung bình, không lộ khóa, không chặn cổng bảo mật) |

## Tóm tắt (cho chủ dự án)

ChatGPT và Gemini viết được trọn một bài (nghiên cứu → dàn ý → viết → rà soát → viết lại) khi đổi
`provider` trong `config/ai.toml`. Không tìm thấy chỗ nào làm lộ khóa API. Có 2 lỗi nhỏ: nếu mạng
trả về trang web lạ (ví dụ Wi-Fi quán cà phê bắt đăng nhập) thì Gemini làm trang Soạn bài hiện lỗi
tiếng Anh thay vì câu báo tiếng Việt; và nếu sau này nâng thư viện `openai` lên bản mới hơn thì có
thể hỏng tương tự. Cả hai không mất dữ liệu, chỉ khó hiểu.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_ai_openai_gemini_soi_loi.py` (mới) | 30 hàm test (98 trường hợp: 95 qua, 3 `xfail(strict=True)` cho lỗi SL-1, SL-2). |

Không sửa code ứng dụng, không sửa hay bỏ qua test có sẵn.

Điểm khác với test của Thợ Máy: phần lớn test mới chạy **thư viện thật** (`openai`, `google-genai`)
với mạng giả `httpx.MockTransport` / `httpx2.MockTransport` (không mở socket, conftest vẫn chặn
mạng). Nhờ vậy kiểm được cách thư viện thật dựng yêu cầu (khóa nằm ở đâu, có công cụ nào) và đọc
trả lời thật của máy chủ, chứ không chỉ đối tượng giả.

Thư viện mới trong `uv.lock` (đối chiếu với báo cáo Thợ Máy, khớp): `openai`, `google-genai`, và
kéo theo `httpx`, `httpcore`, `distro`, `google-auth`, `cryptography`, `cffi`, `pycparser`,
`pyasn1`, `pyasn1-modules`, `tenacity`. `websockets` hạ 17.2 → 16.1.1.

## Bằng chứng

```
$ uv run pytest            (trước khi thêm test, nhánh 86ffa4e)
1987 passed, 3 xfailed in 118.47s

$ uv run pytest            (sau khi thêm test)
2082 passed, 6 xfailed in 96.95s

$ uv run ruff check .
All checks passed!
```

## Nhánh logic mới và test tương ứng

| Nhánh | Test (file của Thợ Máy = TM, của Soi Lỗi = SL) |
|---|---|
| `base.redact_secrets`: `?key=`, `&key=` | TM `test_redact_hides_google_key_in_url_and_header`; SL `test_redact_every_key_shape` (8 dạng × 3 khóa) |
| `registry.make_provider`: openai / gemini / thiếu khóa | TM `test_router_mixes_vendors`, `test_missing_key_points_to_settings`; SL `test_ai_toml_vendor_without_key_points_to_settings` (đi từ file `ai.toml`) |
| OpenAI: trả đúng khuôn, `store=False`, Bearer | TM + SL `test_openai_real_library_parses_response_and_sends_bearer` |
| OpenAI: 400 reasoning → gọi lại 1 lần | TM; SL `…_reasoning_retry_is_bounded` (2 lần lỗi → đúng 2 lượt gọi), `…_retry_then_success` |
| OpenAI: 400 khác → không gọi lại, che khóa | TM; SL `…_other_400_is_not_retried`, `test_openai_400_message_with_key_is_hidden_end_to_end` |
| OpenAI: 401/403/404/429/quota/5xx/timeout/mạng/lỗi khác | TM `test_openai_errors_become_vietnamese`; SL `test_openai_real_library_bad_results`, `…_network_errors` |
| OpenAI `_parse`: incomplete (max tokens, content_filter), failed, refusal, rỗng, sai khuôn, phase | TM `test_openai_bad_results`, `…_non_final_phase…`; SL `test_openai_real_library_bad_results` (gồm trả HTML) |
| Gemini: khóa trong header, không trong URL; chỉ `googleSearch` | SL `test_gemini_real_library_key_in_header_never_in_url`, `…_research_sends_only_google_search` |
| Gemini: 400 thinking → gọi lại 1 lần | TM; SL `test_gemini_real_library_thinking_retry_is_bounded`, `test_gemini_thinking_retry_in_legacy_search_is_bounded` |
| Gemini `_bad_key` | TM; SL `test_gemini_bad_key_detection` (8 trường hợp), `test_gemini_other_400_is_not_reported_as_bad_key` |
| Gemini `_api_error`: 401/403/404/429/billing/400/5xx | TM `test_gemini_errors_become_vietnamese`; SL `test_gemini_real_library_bad_key_400`, `…_bad_results` (502 HTML) |
| Gemini tìm web 2 lượt (đời 1.x/2.x), ghi chép rỗng / bị cắt / bị chặn | TM; SL `test_gemini_real_library_legacy_search_two_calls_with_frame`, `test_legacy_notes_max_tokens_and_blocked_are_errors` |
| Gemini `_frame` (prompt injection) | TM; SL `test_legacy_notes_cannot_break_out_of_frame` (6 dạng thẻ giả) |
| Gemini `_text`: prompt_feedback, không candidate, MAX_TOKENS, SAFETY…, bỏ phần thought | TM `test_gemini_bad_results`; SL `test_gemini_real_library_bad_results` |
| Gemini httpx Timeout / Transport | TM; SL `test_gemini_real_library_network_errors` |
| `env_file._check_openai`, `_check_gemini`, `except Exception` | TM; SL `test_check_generic_exception_only_names_the_error` (4 loại lỗi × 2 hãng), `test_check_gemini_real_library_html_and_bad_key` |
| `repr`/`str` provider và client | TM; SL `test_repr_of_provider_and_client_has_no_key` (cả `_client`, `_api_client`, `models`) |
| `ContentWriter` trọn quy trình | TM (client giả); SL `test_content_writer_end_to_end_on_real_library_with_mock_network[gemini/openai]` |

## Kết quả các điểm cần thử

- **(a) Hàm nội bộ `type_to_text_format_param`:** đã thử cho mọi khuôn trong
  `seo_app/content/models.py` (10 lớp): khuôn strict hợp lệ (mọi trường đều `required`,
  `additionalProperties: false`, không có từ khóa lạ). Nếu thư viện bỏ hàm này → **lỗi SL-2**.
  Không ảnh hưởng Claude/Gemini (thư viện được nhập khi cần; test
  `test_openai_internal_helper_missing_does_not_break_other_vendors`).
- **(b) Gọi lại khi lỗi reasoning/thinking:** đúng 1 lần gọi lại, không lặp; lỗi 400 khác không gọi
  lại (OpenAI và Gemini, cả với thư viện thật). Ghi nhận: OpenAI gọi lại khi thông điệp 400 có chữ
  "reasoning" ở bất kỳ đâu, nên lỗi 400 khác có nhắc chữ này cũng bị gọi lại một lần không kèm
  `reasoning` (không nguy hiểm, có thể ra bài nghĩ nông hơn mà không báo). Không xếp là lỗi.
- **(c) `_bad_key`:** nhận đúng `API_KEY_INVALID` và "API key not valid" (cả "API key expired" kèm
  `API_KEY_INVALID`); không nhầm "invalid argument", "User location is not supported", "Unknown
  name apiKey", lỗi thinking, 403 `API_KEY_SERVICE_BLOCKED`.
- **(d) Ghi chép tìm web:** bọc đúng một khung `<du_lieu_tham_khao>`; thẻ đóng/mở giả, chữ hoa,
  có dấu cách, xuống dòng, chữ toàn khổ đều bị vô hiệu.
- **(e) `check_api_key` `except Exception`:** thông báo đúng dạng "Lỗi khi kiểm tra khóa
  (TênLỗi)." và không chứa khóa, kể cả khi lỗi mang khóa trong URL/header/Bearer. Gemini nhận trang
  HTML ra `unknown`, không sập.
- **(f) `repr`/`str`:** provider, client OpenAI, client Gemini, `_api_client`, `models` đều không
  chứa khóa.
- **Khóa trong thông báo lỗi:** `?key=`, `&key=`, `x-goog-api-key`, `Authorization: Bearer`,
  `Bearer:` đều được che, cả khi đi qua thư viện thật. Thư viện thật của Gemini gửi khóa ở header
  `x-goog-api-key`, URL không có `key=`.
- **Thiếu khóa khi `ai.toml` chọn gemini/openai:** báo "Chưa có khóa … (GEMINI_API_KEY/OPENAI_API_KEY).
  Vào Cài đặt → 🔌 Kết nối để nhập khóa." ngay khi dựng `AIRouter` (trang Soạn bài bắt được).

## Lỗi tìm thấy

### SL-1 · Gemini trả dữ liệu không phải JSON làm lọt lỗi thô — mức **Trung bình**

- **Tái hiện:** `test_gemini_html_response_becomes_vietnamese_error`,
  `test_gemini_decoding_error_becomes_vietnamese_error` (đang `xfail(strict=True)`). Trong đời thật:
  máy dùng Wi-Fi bắt đăng nhập hoặc proxy công ty trả trang HTML mã 200, rồi bấm một bước AI dùng
  Gemini.
- **Mong đợi:** `AIError` tiếng Việt (ví dụ "Không kết nối được tới Gemini. Kiểm tra mạng
  Internet."), trang hiện ô báo lỗi như các lỗi khác.
- **Thực tế:** `json.JSONDecodeError` (hoặc `httpx.DecodingError` khi dữ liệu nén hỏng) lọt ra khỏi
  `GeminiProvider.generate`; `ai_call` ở `app/views/write.py:374` chỉ bắt `AIError` nên Streamlit
  hiện khung lỗi tiếng Anh kèm traceback. Không lộ khóa (thông điệp chỉ có nội dung trang HTML).
- **Chỗ sửa gợi ý (Thợ Máy):** `seo_app/ai/gemini_provider.py:116-121`, bắt thêm `ValueError`
  (gồm `JSONDecodeError`, `errors.UnknownApiResponseError`) và `httpx.RequestError` (thay cho
  `TransportError`), đổi sang `AIError`, không chép thông điệp thô. OpenAI không bị (đã thử: ra
  "không đúng khuôn").

### SL-2 · Thư viện `openai` đổi hàm nội bộ thì báo lỗi thô — mức **Thấp**

- **Tái hiện:** `test_openai_internal_helper_missing_gives_vietnamese_error` (`xfail(strict=True)`):
  bỏ `openai.lib._parsing._responses.type_to_text_format_param` rồi gọi `make_provider("openai", …)`.
- **Mong đợi:** `AIError` tiếng Việt, ví dụ "Thư viện openai không tương thích, cần cài lại đúng
  phiên bản (uv sync)."
- **Thực tế:** `ImportError` thô; `build_writer` ở `app/views/write.py:875` chỉ bắt `AIError` nên
  trang Soạn bài sập (cả khi chỉ một việc dùng OpenAI). Chỉ xảy ra khi thư viện bị nâng ngoài
  `uv.lock`, nên mức Thấp; test có sẵn của Thợ Máy cũng sẽ báo đỏ khi đó.
- **Chỗ sửa gợi ý:** bọc lần nhập ở `seo_app/ai/registry.py:100` (hoặc ở đầu
  `openai_provider.py`) để đổi `ImportError` sang `AIError`.

## Rủi ro và điểm cần chú ý

- `redact_secrets` **không** che khóa không có tiền tố khi viết dạng `"key": "…"` (JSON),
  `key%3D…` hay `key=…` đầu dòng (không có `?`/`&`). Không thấy đường nào thật để khóa đi vào các
  dạng này (Gemini gửi khóa ở header; khóa thật có tiền tố `AIza`/`sk-` nên vẫn bị che). Ghi lại để
  Lá Chắn xét, không xếp là lỗi.
- Thông báo lỗi 400 của OpenAI hiện nguyên chuỗi `Error code: 400 - {'error': {...}}` (đã che khóa),
  khó đọc với người dùng. Gợi ý: chỉ lấy `error.message` trong body.
- `google-genai` khi thử lại ghi log mức INFO kèm `str(lỗi)` (gồm cả body trả về); app không bật log
  INFO nên không hiện ra.
- Test với thư viện thật gắn với cấu trúc nội bộ của `google-genai` (`client_args.transport`); nếu
  nâng thư viện có thể phải chỉnh test.

## Đề xuất

- Chỉ Huy giao Thợ Máy sửa SL-1 (nên sửa trước khi chủ dự án dùng Gemini làm chính) và SL-2; khi
  sửa xong, bỏ dấu `xfail` ở 3 test tương ứng (strict nên sẽ tự báo khi đã qua).
- Họa Sĩ (T-023): test `tests/test_settings_keys.py::test_check_only_for_claude` mang tên cũ (Thợ
  Máy đã nêu).

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-15) · kiểm lại bản sửa d028c13

**Kết luận: ĐẠT.** SL-1 và SL-2 đã sửa đúng. Có thêm 2 lỗi mức **Thấp** cùng loại với SL-2
(chỉ xảy ra khi thư viện bị nâng ngoài `uv.lock`). Hai lỗi này không lộ khóa, không chặn cổng bảo
mật, nên sửa trong phiếu sau cũng được.

### Bằng chứng

```
$ uv run pytest
2116 passed, 5 xfailed in 86.51s

$ uv run ruff check .
All checks passed!
```

`tests/test_ai_openai_gemini_soi_loi.py` có thêm 6 hàm test (21 trường hợp: 19 qua, 2 `xfail(strict=True)` cho SL-3, SL-4).

### Kết quả kiểm từng mục

1. **SL-1 đã sửa.** `gemini_provider.py` bắt `JSONDecodeError`, `UnknownApiResponseError`, `httpx.DecodingError`
   và trả câu "Máy chủ Gemini trả về dữ liệu lạ…". Lỗi mạng khác (`httpx.RequestError`) ra "Kiểm tra
   mạng". Hai test xfail của tôi nay qua thật với thư viện thật. Không chép thông điệp thô.
2. **SL-2 đã sửa, test được Thợ Máy sửa nội dung, không bị nới lỏng nhưng yếu hơn bản gốc.** Code mới
   dùng `openai.pydantic_function_tool` công khai. Thợ Máy đã kiểm khuôn tạo ra **trùng** với hàm cũ
   cho mọi khuôn bài viết. Test sửa lại kiểm hai việc: hàm nội bộ mất thì vẫn dựng được provider, và
   module hỏng hẳn (`ImportError`) thì ra `AIError` "uv sync". Cả hai đúng rủi ro ban đầu. Chỗ yếu: test
   chỉ dựng provider, chưa gọi `generate`. Tôi thêm `test_openai_still_generates_when_internal_helper_is_gone`:
   hàm nội bộ mất thì vẫn viết được bài (qua). Rủi ro "thư viện đổi thì sập" vẫn còn một nhánh,
   xem SL-3.
3. **`redact_secrets` che trường `"key"`.** Đã che được nháy kép, nháy đơn, có dấu cách quanh `:`, tab, chữ hoa,
   nháy lẫn (`'key': "…"`), dạng `Error code: 400 - {'error': {…, 'key': '…'}}` và trường lồng sâu.
   Không che nhầm `keyword`, `key_points`, `monkey`, `"key": ""`.
   - Che dư: giá trị thường của trường tên đúng `key` cũng bị ẩn (`{"key": "cổng sắt"}` →
     `[đã ẩn]`). Hàm này chỉ dùng cho thông báo lỗi (`openai_provider.py:88`,
     `anthropic_provider.py:61`, `gemini_provider.py:186`, `env_file.py:313`) nên vô hại.
   - Chưa che được (ghi nhận, không xếp là lỗi vì chưa thấy đường thật nào đưa khóa vào): xuống
     dòng giữa `:` và giá trị; JSON đã escape (`{\"key\": \"…\"}`); giá trị không có nháy
     (`"key": abc`); tuple `("key", "…")`. Khóa Google thật có tiền tố `AIza` nên vẫn bị che ở mọi dạng.
4. **`make_provider` bắt `ImportError` của cả 3 hãng.** Đúng. Test của Thợ Máy
   (`test_broken_vendor_library_gives_vietnamese_error`) và test của tôi
   (`test_broken_vendor_library_error_is_vietnamese_and_through_router`, đi qua `AIRouter`
   như `build_writer`) đều qua. Câu báo có tên hãng, không có chữ `ImportError`. Chưa bắt
   `AttributeError`, xem SL-4.

### Lỗi mới

**SL-3 · Đổi `openai.pydantic_function_tool` thì lỗi thô ngay lúc viết bài, mức Thấp**
- Tái hiện: `test_openai_public_helper_change_gives_vietnamese_error` (`xfail(strict=True)`): bỏ
  `openai.pydantic_function_tool`, gọi `OpenAIProvider.generate`.
- Mong đợi: `AIError` tiếng Việt (giống câu "uv sync").
- Thực tế: `AttributeError` thô. `text_format(schema)` chạy khi dựng `params`, nằm ngoài khối `try`
  (`openai_provider.py:52`). `ai_call` chỉ bắt `AIError` nên trang sập. Hàm công khai ít đổi hơn hàm
  nội bộ, nên rủi ro thấp hơn SL-2 nhưng chưa hết: lỗi chỉ dời từ lúc nhập sang lúc gọi.
- Gợi ý sửa: bọc `text_format(schema)` (hoặc cả phần dựng `params`) để đổi `AttributeError`/`TypeError`/`KeyError` sang `AIError`.

**SL-4 · `make_provider` chỉ bắt `ImportError`, không bắt `AttributeError` lúc nhập, mức Thấp**
- Tái hiện: `test_gemini_library_missing_constant_gives_vietnamese_error` (`xfail(strict=True)`):
  bỏ `google.genai.types.ThinkingLevel`, gọi `make_provider("gemini", …)`.
- Mong đợi: `AIError` "Thư viện của Google Gemini … uv sync".
- Thực tế: `AttributeError` thô. `gemini_provider.py` dùng hằng của thư viện ngay khi nhập
  (`THINKING_LEVELS`, `_BLOCKED`, `RETRY`). Bản google-genai đổi tên một hằng là trang Soạn bài sập.
- Gợi ý sửa: `registry.py:96-103` bắt `(ImportError, AttributeError)`.

### Ghi chú

Thợ Máy đã sửa file test của Soi Lỗi: bỏ 3 dấu `xfail` và viết lại nội dung một test. Việc này
đúng hướng và nội dung không nới lỏng, nhưng theo phân công thì file `tests/*_soi_loi.py` do Soi
Lỗi giữ. Lần sau nên để Soi Lỗi bỏ `xfail`.

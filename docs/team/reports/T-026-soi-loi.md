# Báo cáo T-026 · Kiểm thử: sửa 4 lỗi mức Thấp của lớp AI

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-026](../tickets/T-026-loi-thap-lop-ai.md) |
| Nhánh | `team/T-026` (kiểm trên commit Thợ Máy `f042764`), worktree `D:\ProMetal-ToolSEO\wt-T-026` |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |
| Kết luận | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Thợ Máy đã sửa đủ 4 lỗi LC-1 → LC-4. Tôi thử thêm 159 trường hợp xấu: không trường hợp nào
làm lộ khóa hay khiến app gọi sang máy chủ khác. Tìm được 4 lỗi, đều mức **Thấp**. Hai lỗi nằm
trong phạm vi phiếu, sửa mất vài dòng, nên sửa trước khi gộp:

- **SL-T026-1:** mã lỗi của máy chủ dạng `www.xxx.com` vẫn hiện ra và Streamlit biến nó thành link bấm được.
- **SL-T026-2:** nút **Kiểm tra** khóa chưa hiện câu "chạy lại run.bat (uv sync)" khi thư viện đổi tên lớp lỗi.

Hai lỗi còn lại chỉ làm câu báo lỗi chưa đúng hoặc hiện lỗi kỹ thuật khi máy chủ trả dữ liệu
hỏng. Không lỗi nào làm lộ khóa. Một trong hai lỗi này đã có sẵn trên `main` trước phiếu này.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t026.py` | **Mới**, 159 trường hợp: 144 qua, 15 `xfail(strict=True)` cho 4 lỗi tìm được (SL-T026-1 → 4). |
| `tests/test_ai_openai_gemini_soi_loi.py` | `test_gemini_other_400_is_not_reported_as_bad_key`: thêm `assert message not in str(info.value)` (câu máy chủ không được chép ra màn hình, theo LC-3). Chặt hơn, không nới. |

Không sửa code ứng dụng.

## Lỗi tìm được

| Mã | Mức | Ở đâu | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|
| **SL-T026-1** | Thấp | `seo_app/ai/base.py:82-89` (`_SAFE_CODE`, `safe_code`) | Máy chủ (hoặc proxy giả máy chủ) trả 400 với `code`/`param` (OpenAI), `error.type` (Anthropic) hoặc `status` (Gemini) = `www.evil.com`. Test: `test_safe_code_drops_www_autolink`, `test_400_code_from_server_cannot_become_link` (3 hãng). | Mã lạ bị bỏ. Câu báo không có link. | Câu báo là `…(lỗi 400; mã www.evil.com, tham số www.phishing.example)…`. `write.py:380` hiện câu này bằng `st.error`, mà `st.error` đọc Markdown có GFM: `StreamlitMarkdown` (Streamlit 1.65) có `literalAutolinkWww`, nên `www.evil.com` đứng sau dấu cách thành link bấm được. Báo cáo Thợ Máy ghi "không ký tự Markdown/HTML" nhưng dấu `.` đủ để tạo link `www.`. Chỉ xảy ra khi máy chủ trả mã lạ; địa chỉ máy chủ đã cố định (LC-4) nên khó xảy ra. |
| **SL-T026-2** | Thấp | `seo_app/env_file.py:328-365`, `:368-405`, `:408-455` | Thư viện đổi tên một lớp lỗi (ví dụ bỏ `anthropic.AuthenticationError`, `openai.AuthenticationError`, `google.genai.errors.APIError`), rồi lúc kiểm tra có lỗi bất kỳ. Test: `test_check_api_key_renamed_exception_class` (3 hãng). | `check_api_key` trả `unknown` kèm câu "uv sync" (phiếu, yêu cầu 1: "cả 3 hãng, lúc nhập thư viện lẫn lúc gọi"). | Python tính biểu thức của câu `except anthropic.AuthenticationError:` và ném `AttributeError`. Lỗi này nằm ngoài các nhánh `except` của cùng khối `try` nên lọt thẳng ra khỏi `check_api_key`. Trang không sập vì `settings.py:115-121` bắt mọi lỗi, nhưng người dùng thấy "Không kiểm tra được khóa (AttributeError)" thay vì câu nhắc chạy `uv sync`. Ở `generate` của 3 hãng thì đúng (lớp bọc ngoài bắt được), có test `test_renamed_exception_class_in_provider_is_library_error`. |
| **SL-T026-3** | Thấp | `seo_app/ai/gemini_provider.py:122-127` | Máy chủ/proxy trả mã 200 với `{"candidates": [1]}` hoặc `{"candidates": [{"finishReason": 5}]}`. Test: `test_gemini_strange_json_is_not_reported_as_library_problem`. | Câu "Máy chủ Gemini trả về dữ liệu lạ…" (`BAD_RESPONSE`). | google-genai ném `TypeError` / `AttributeError` khi đọc trả lời, lớp bọc đổi thành câu "uv sync". Đúng như Thợ Máy nêu ở rủi ro 2. Riêng ví dụ của Thợ Máy `{"candidates": "x"}` thì ở bản thư viện hiện tại ra "không đúng khuôn". Không lộ gì, trang không sập (`test_gemini_strange_json_never_crashes`, 9 dạng JSON lạ), chỉ là câu gợi ý sai hướng. |
| **SL-T026-4** | Thấp (**có sẵn trên `main`**, ngoài phạm vi T-026) | `seo_app/ai/anthropic_provider.py:46-86`, `seo_app/ai/openai_provider.py:79-114` | Mã 200 nhưng nội dung hỏng: Anthropic nhận trang HTML, JSON thường (không phải luồng SSE) hoặc SSE có JSON hỏng; OpenAI nhận JSON hỏng. Test: `test_garbage_200_gives_vietnamese_error` (4 dạng). | `AIError` tiếng Việt (Gemini đã xử lý trường hợp này bằng `BAD_RESPONSE`). | Lỗi thô lọt ra ngoài `generate`: `AssertionError` (từ `anthropic/lib/streaming/_beta_messages.py:102`) và `json.JSONDecodeError`. `ai_call` (`write.py:379`) chỉ bắt `AIError`, nên Streamlit hiện traceback. Thông điệp không chứa khóa. Tôi đã chạy lại trên mã nguồn `main` (`git archive origin/main`), kết quả y hệt, nên lỗi này không do T-026 gây ra. |

### Ghi nhận thêm (không tính là lỗi)

- **Bắt rộng lỗi kiểu Python (điểm 2 Thợ Máy nhờ thử):** lỗi `TypeError`/`AttributeError`/`KeyError`/`ImportError`
  trong chính code của app nằm trong `generate` cũng ra câu "uv sync". Ví dụ: `_frame` → `seo_app.content.prompts._block`
  ở đường Gemini 2 lượt, `_parse`, `text_format`, `THINKING_LEVELS[task.effort]`. Lỗi gốc vẫn ở `__cause__`
  (`test_app_bug_inside_generate_keeps_root_cause`), nhưng app không ghi `__cause__` ra đâu cả (`ai_call` chỉ hiện
  `str(exc)`), nên người gỡ lỗi chỉ thấy "uv sync", chạy lại `uv sync` vẫn hỏng. Không phải lỗ hổng bảo mật. Đề xuất:
  ghi `__cause__` vào log ở mức DEBUG/WARNING (chỉ tên lớp và vị trí, không ghi nội dung), hoặc chỉ bọc quanh các lời
  gọi thư viện.
- **Ngoài phạm vi:** `config/ai.toml` có tên mô hình Gemini chứa `?`, `../` hoặc ký tự xuống dòng ở giữa thì
  google-genai ném `ValueError`/`httpx.InvalidURL` thô (đã có từ trước, do người dùng gõ nhầm, rất khó xảy ra).

## Trả lời các điểm Thợ Máy nhờ thử

1. **Test "User location" (`test_gemini_other_400_is_not_reported_as_bad_key[…FAILED_PRECONDITION…]`):** vẫn đúng ý,
   vì "User location" giờ lấy từ câu viết sẵn trong `KNOWN_400_HINTS`, không lấy từ máy chủ. Tôi siết thêm: câu máy chủ
   nguyên văn không được có trong câu báo. Thêm `test_gemini_known_400_shows_written_hint_only`: chữ hoa/thường khác
   nhau, câu máy chủ chèn link/khóa/HTML vẫn ra đúng câu viết sẵn. `test_gemini_known_phrase_on_other_codes_gives_no_hint`:
   lỗi 403/429/500 không kèm gợi ý. `test_known_400_hints_are_plain_text`: gợi ý không có ký tự Markdown hay link.
2. **Bắt rộng `ImportError/AttributeError/TypeError/KeyError`:** xem mục "Ghi nhận thêm". Không che lỗi bảo mật,
   chỉ làm khó gỡ lỗi. Lớp bọc này còn có lợi: bắt được trường hợp đổi tên lớp lỗi, việc mà các nhánh `except`
   bên trong không tự bắt được (xem SL-T026-2).
3. **google-genai ném `AttributeError` với JSON lạ:** đã xác nhận, ghi thành SL-T026-3. Có thêm dạng `TypeError`.
4. **Cấu hình Gemini dạng dict:** nội dung gửi đi **giống hệt** bản cũ (`types.ThinkingConfig`, `types.Tool`).
   Tôi so nguyên địa chỉ và JSON gửi đi qua thư viện thật trong 20 tổ hợp (5 mức effort × có/không khuôn × có/không
   tìm web): `test_gemini_request_body_same_as_before`. So cả lượt gọi lại khi lỗi "thinking"
   (`test_gemini_thinking_retry_body_same_as_before`) và đường Gemini 2.x hai lượt
   (`test_gemini_legacy_two_turn_bodies_same_as_before`). Ghi chú: thư viện gửi `thinkingConfig: {"thinking_level": …}`
   (tên trường kiểu gạch dưới), bản cũ cũng vậy.
5. **Đổi chữ ký hàm:** `beta.messages.stream` bỏ `fallbacks`, `responses.create` bỏ `store`/`reasoning`,
   `generate_content` đổi tên `config` (thư viện thật, thay hàm của lớp). Thêm các trường hợp: thiếu `parsed_output`,
   thiếu `stop_reason`, `stream()` không còn là context manager, đổi tên `get_final_message`, client không có
   `responses.create`, đổi tên lớp lỗi (5 trường hợp). Tất cả ra câu "uv sync" và giữ lỗi gốc.
6. **LC-3:** câu 400 của cả 3 hãng **đúng từng chữ** câu cố định, với 14 dạng câu máy chủ độc: khóa không tiền tố
   ` key=…`, `apikey: …`, link và ảnh Markdown, tiêu đề Markdown sau xuống dòng, `<script>`, `onerror=`, `javascript:`,
   ký tự vô hình (ZWSP, ZWJ, WJ, BOM), chữ đảo chiều RLO, `:red[…]`/`:material/…:` của Streamlit, câu 20 000 ký tự,
   chuỗi rỗng. Hai câu máy chủ khác nhau cho ra cùng một câu báo (`test_400_message_does_not_depend_on_server_text`).
   `safe_code` bỏ được 24 dạng mã độc: chữ vô hình, BOM, RLO, chữ toàn khổ, chữ Kirin giống Latinh, ký hiệu Kelvin,
   xuống dòng/tab/dấu cách cuối, 41 ký tự, dấu nối ở đầu/cuối/liền nhau, dấu nháy ngược, `|`, `:red[x]`, khóa, kiểu
   không phải chuỗi. Có kiểm cả qua máy chủ giả. Lọt duy nhất dạng `www.…` (SL-T026-1).
   **LC-4:** ngoài các biến Thợ Máy đã thử, tôi đặt thêm `*_BASE_URL` = `http://127.0.0.1:8080/`,
   `GOOGLE_GENAI_USE_VERTEXAI=true` + `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION`, và khóa khác trong
   `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`. Kết quả: cả
   `generate` lẫn `env_file.check_api_key` của 3 hãng vẫn gọi đúng máy chủ chính thức qua `https`, header mang đúng
   khóa của app, không header hay địa chỉ nào chứa khóa từ biến môi trường, Gemini không chuyển sang Vertex AI
   (`test_generate_ignores_hostile_env`, `test_check_api_key_ignores_hostile_env`,
   `test_gemini_client_stays_off_vertex_despite_env`).

## Bằng chứng

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_soi_loi_t026.py tests/test_ai_t026.py tests/test_ai_openai_gemini_soi_loi.py
348 passed, 15 xfailed in 18.36s
```

Toàn bộ test trên Windows (máy dự án):

```
# Trước khi thêm test (team/T-026 = f042764)
$ uv run pytest -q -rfE
145 failed, 2250 passed, 10 skipped, 3 xfailed, 57 warnings, 7 errors in 237.31s (0:03:57)
$ uv run python compare_failures.py t026_soiloi_run1.txt windows_baseline_failures.txt
Số test hỏng: 152
Nằm ngoài danh sách đỏ sẵn: 0

# Sau khi thêm test
$ uv run pytest -q -rfE
145 failed, 2394 passed, 10 skipped, 18 xfailed, 57 warnings, 7 errors in 186.38s (0:03:06)
$ uv run python compare_failures.py t026_soiloi_run2.txt windows_baseline_failures.txt
Số test hỏng: 152
Nằm ngoài danh sách đỏ sẵn: 0
```

Chênh lệch: **+144 passed, +15 xfailed**, khớp đúng 159 trường hợp mới (144 qua, 15 `xfail(strict=True)`).
152 test hỏng còn lại (145 failed + 7 errors) đều nằm trong danh sách đỏ sẵn trên Windows (phiếu T-027), giống
hệt trước khi thêm test. Không gặp test đo tốc độ chập chờn trong hai lần chạy.


15 xfail mới đều thất bại đúng lý do: tôi chạy với `--runxfail` và đối chiếu từng lỗi. `safe_code('www.evil.com')`
trả `'www.evil.com'`. `check_api_key` ném `AttributeError: module 'anthropic' has no attribute 'AuthenticationError'`.
Gemini báo câu "uv sync". Anthropic ném `AssertionError`, OpenAI ném `JSONDecodeError`.

## Đối chiếu tiêu chí xong

- [x] LC-1: lỗi thư viện lúc gọi → "uv sync" ở `generate` cả 3 hãng (đổi chữ ký, bỏ thuộc tính, đổi tên lớp lỗi).
- [ ] LC-1 ở nút Kiểm tra khóa: còn trường hợp đổi tên lớp lỗi (SL-T026-2).
- [x] LC-2: lúc nhập / tạo client (Thợ Máy đã có test, tôi không tìm thêm được lỗi).
- [ ] LC-3: câu 400 cố định, không chép câu máy chủ. Còn mã dạng `www.…` thành link (SL-T026-1).
- [x] LC-4: địa chỉ cố định ở 6 chỗ tạo client, biến môi trường đổi địa chỉ / Vertex / khóa không có tác dụng.
- [x] Cấu hình Gemini dạng dict gửi đi giống hệt bản cũ.
- [x] Không có test hỏng ngoài danh sách đỏ sẵn trên Windows. Test mới đều qua hoặc `xfail(strict=True)` có ghi mã lỗi.

## Điều kiện để ĐẠT

1. Thợ Máy sửa **SL-T026-1**. Cách rẻ nhất: bọc mã trong dấu nháy ngược (`` mã `invalid_value` ``), vì Markdown
   không tạo link bên trong đoạn mã, hoặc cho `safe_code` từ chối mã có dấu `.` mà bắt đầu bằng `www`. Sau đó bỏ
   `xfail` của `test_safe_code_drops_www_autolink` (nếu chọn cách nháy ngược thì sửa test này theo cách đó) và
   `test_400_code_from_server_cannot_become_link`.
2. Thợ Máy sửa **SL-T026-2**: ở `check_api_key` (hoặc mỗi `_check_*`), bọc thêm một lớp ngoài bắt
   `_CALL_LIBRARY_ERRORS` → `_library_result(label)`, giống lớp bọc `generate` của provider. Sau đó bỏ `xfail` của
   `test_check_api_key_renamed_exception_class`.

## Đề xuất

- **SL-T026-3:** Chỉ Huy quyết sửa luôn hay chấp nhận. Cách sửa gợi ý: chỉ đổi `TypeError`/`AttributeError` sang câu
  "uv sync" khi lỗi xảy ra **trước** lúc nhận được trả lời. Lỗi khi thư viện đọc trả lời thì đổi sang `BAD_RESPONSE`.
- **SL-T026-4** (có sẵn trên `main`): lập phiếu riêng cho Thợ Máy: Anthropic bắt `AssertionError`/`json.JSONDecodeError`
  quanh luồng stream, OpenAI bắt `json.JSONDecodeError`, đều đổi sang câu "Máy chủ … trả về dữ liệu lạ" như Gemini.
- **Lá Chắn:** xem SL-T026-1 (S2, U1: chữ từ máy chủ hiện bằng Markdown). Ghi `__cause__` vào log (mục "Ghi nhận
  thêm") nếu làm thì phải bảo đảm không ghi nội dung lỗi (có thể chứa khóa).

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (kiểm lại sau khi Thợ Máy sửa, nhánh `d8fd392`)

**Kết luận lượt 2: ĐẠT.** Hai điều kiện ở lượt 1 (SL-T026-1, SL-T026-2) đã được sửa đúng. Tôi không tìm
thêm được lỗi mới. SL-T026-3 vẫn để `xfail` theo quyết định của Chỉ Huy. SL-T026-4 đã chuyển sang phiếu T-028.

### Đã kiểm

- **Thợ Máy chỉ bỏ đúng 3 `xfail` của tôi.** `git diff c906285 d8fd392 -- tests/test_soi_loi_t026.py`
  chỉ có 9 dòng bị xóa (3 dấu `xfail` của `test_safe_code_drops_www_autolink`,
  `test_400_code_from_server_cannot_become_link`, `test_check_api_key_renamed_exception_class`), không sửa gì
  khác. `tests/test_ai_openai_gemini_soi_loi.py` và báo cáo của tôi không bị đụng.
- **SL-T026-1** (`seo_app/ai/base.py:83-115`). GFM chỉ tự tạo link cho 3 dạng: `www.`, `http(s)://` và email.
  Bộ ký tự của `safe_code` không có `:`, `/`, `@`, nên chỉ còn dạng `www.` có thể thành link. Thợ Máy bỏ mọi mã chứa
  `www.` ở bất kỳ vị trí nào, so sánh sau khi đổi sang chữ thường. Cách này phủ đủ mọi dạng GFM nhận, vì GFM nhận
  `www.` không phân biệt hoa thường, ở đầu dòng, sau dấu cách hoặc sau `*`, `_`, `~`, `(`.
  - Tôi thử thêm 10 dạng lách: `WwW.evil.com`, `a_www.evil`, `x.www.y`, `www.evil` (không có đuôi), `A_WWW.B_C`…
    Tất cả đều bị bỏ.
  - Mã có dạng tên miền với đuôi trong danh sách (`evil.COM`, `login.bank.io`, `phish.localhost`…) bị bỏ.
  - Punycode `xn--…`, dấu chấm ở đầu/cuối/liền nhau, dấu cách, chữ số đều bị chặn ngay từ bộ ký tự.
  - Thử ngẫu nhiên 30 000 mã ghép từ `wW._aE` (hạt giống cố định): không mã nào được nhận mà còn chứa `www.`. Với
    `safe_code` lượt 1, cùng phép thử này lọt 208 mã.
  - 58 mã thật của 3 hãng vẫn giữ được: mã lỗi và tham số của OpenAI (`reasoning.effort`, `text.format.schema`…),
    loại lỗi của Anthropic, trạng thái của Gemini.
  - Ghi chú, không phải lỗi: danh sách đuôi tên miền không đủ, ví dụ `evil.ru` vẫn được giữ. Markdown của
    Streamlit không tự tạo link cho tên miền trần (không có `www.`), nên đây chỉ là lớp phòng thêm, như Thợ Máy đã
    ghi ở mục rủi ro.
- **SL-T026-2** (`seo_app/env_file.py:307-314`).
  - Đổi tên **từng** lớp lỗi mà 3 hàm `_check_*` dùng tới, 16 trường hợp: 7 của Claude, 6 của ChatGPT, 3 của
    Gemini (`errors.APIError`, `httpx.TimeoutException`, `httpx.TransportError`). Cả 16 đều ra câu "uv sync" của
    đúng hãng, không lộ khóa.
  - `ImportError`/`AttributeError`/`TypeError` ném lúc gọi ra câu "uv sync", cả 3 hãng.
  - `KeyError` vẫn chỉ nêu tên lỗi, cả 3 hãng.
  - Đổi tên lớp lỗi cùng lúc với máy trả `KeyError` thì vẫn ra câu "uv sync".

### Test thêm ở lượt 2 (`tests/test_soi_loi_t026.py`)

105 trường hợp, đều qua:

- `test_real_vendor_codes_are_still_kept` (58)
- `test_www_anywhere_any_case_is_dropped` (10)
- `test_domain_like_codes_with_listed_tld_are_dropped` (6)
- `test_other_domain_shapes_fail_charset` (6)
- `test_no_accepted_code_can_contain_www_property` (1)
- `test_check_every_renamed_exception_class` (16)
- `test_check_library_error_types_from_call` (9)
- `test_check_key_error_still_only_names_it` (3)
- `test_check_renamed_class_with_key_error_is_library_message` (3)

### Bằng chứng (Windows, máy dự án, nhánh `team/T-026` sau khi thêm test lượt 2)

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q -rfE
2718 passed, 10 skipped, 9 xfailed in 206.76s (0:03:26)
```

0 hỏng, 0 lỗi. Có 2718 test qua, tức là 2613 của Thợ Máy cộng 105 trường hợp mới của tôi. Có 9 `xfail`: 2 của
SL-T026-3, 4 của SL-T026-4 (phiếu T-028) và 3 test cũ ngoài phạm vi.

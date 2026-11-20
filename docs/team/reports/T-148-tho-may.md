# Báo cáo T-148 · Loại lỗi AI, một lớp thử lại, đọc mục `[auto]` (phiếu G)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-148](../tickets/T-148-loai-loi-ai-mot-lop-thu-lai.md) · thiết kế T-141 (2.4, 6.3, 6.5, 7.2 dòng G) · biên bản Lá Chắn T-141 (`03568dc`) |
| Nhánh | `team/T-148`, từ `main` `ddcd23c`; mã và test `1926247`; báo cáo ở commit ngay sau |
| Ngày nộp | 2026-11-20 (giờ máy, +07); mã và test xong 19/11, các lượt test chạy lại 20/11 vì máy khởi động lại |
| Kết quả | Hoàn thành yêu cầu 1–8. Thêm phần nối `AIRouter(..., single_attempt=True)` trong `registry.py` theo lời giao của Chỉ Huy B ngày 19/11 (phiếu ghi để T-149 làm) |

## Tóm tắt (cho chủ dự án)

- Đây là **phần nền** cho chế độ tự động. App chưa có nút mới. Các trang đang dùng chạy như cũ, câu báo lỗi giữ nguyên từng chữ.
- Khi AI báo lỗi, phần mềm nay biết **loại lỗi**: máy chủ bận, gọi dày quá, hết lượt trong ngày, rớt mạng, chờ quá lâu, khóa sai, tên mô hình sai, AI từ chối, bài dài quá giới hạn… Lượt chạy tự động sau này dựa vào đó để **chờ rồi thử lại**, hay **dừng và báo**.
- Lượt chạy tự động chỉ còn **một lớp thử lại**. Trước đây, khi Gemini bận, thư viện của Google tự gọi lại tới 3 lần mà phần mềm không biết, nên không đếm được số lần đã dùng. Nay lượt chạy tự động yêu cầu thư viện gọi đúng một lần; việc thử lại do phần mềm làm và đếm đủ.
- Phần mềm tính **ngày theo giờ Mỹ (Thái Bình Dương)**, đúng mốc Google đặt lại lượt miễn phí:
  - **15:00 giờ Việt Nam** từ tháng 11 tới tháng 3;
  - **14:00** từ tháng 3 tới tháng 11.
- Đọc được mục `[auto]` trong `config/ai.toml`: khoảng cách tối thiểu giữa hai lần gọi Gemini, số lần gọi tối đa mỗi ngày. Chưa có mục này thì dùng mặc định: 6 giây, không giới hạn số lần.
- Câu báo lỗi che thêm mã truy cập Cloudflare (dạng `cfut_…`) nếu lỡ có trong đó.
- Một phần **đang tắt, chờ buổi thử**: nhận ra «hết lượt trong ngày» từ chi tiết lỗi của Google. Tài liệu của Google không nói rõ khuôn này, nên phải xem lỗi thật trước. Tới lúc đó, mọi lỗi «gọi dày quá» được coi là giới hạn theo phút.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | <ul><li>`AI_ERROR_KINDS`: 12 tên đúng bảng T-141 2.4 (`busy`, `rate`, `quota_day`, `network`, `timeout`, `auth`, `model`, `bad_request`, `shape`, `refusal`, `token_limit`, `other`).</li><li>`AIError(…, kind=None, retry_after=None)`: `kind` mặc định `"other"`, tên lạ thì `ValueError`; `retry_after` qua `clamp_retry_after` (0–120 giây, không phải số thì `None`). Gọi kiểu cũ `AIError("câu")` không đổi.</li><li>`TokenLimitError.kind = "token_limit"`.</li><li>`status_kind(code)`: chỉ đọc số. 500, 502, 503, 504, 529 → `busy`; 429 → `rate`; 408 → `timeout`; 401 → `auth`; 403, 404 → `model`; 400 → `bad_request`; mã khác → `other`.</li><li>`bad_request_error` → `bad_request`; `bad_response_error` (mã 200 mà dữ liệu lạ) → `shape`; `unreadable_error`: quá giờ → `timeout`, đứt mạng → `network`.</li><li>`redact_secrets`: thêm mẫu `cfut_[A-Za-z0-9_\-]{20,}` (LC-T140-2), che ở bất kỳ đâu trong câu.</li></ul> |
| `seo_app/ai/gemini_provider.py` | <ul><li>`GeminiProvider(api_key, client=None, *, single_attempt=False)`: `True` thì `HttpRetryOptions(attempts=1)` (`SINGLE_ATTEMPT`), mặc định giữ `RETRY` (3 lần).</li><li>`_api_error` đặt `kind` ở từng nhánh có sẵn (cùng câu): 401/`UNAUTHENTICATED`/khóa sai trả 400 → `auth`; 403, 404 → `model`; 429 có `billing`, `credit`, `prepayment` → `quota_day`; 429 khác → `rate`; 400 → `bad_request`; còn lại theo `status_kind`, thêm trạng thái `INTERNAL`, `UNAVAILABLE`, `DEADLINE_EXCEEDED` → `busy` khi mã số không dùng được.</li><li>`quota_details(details)`, `duration_seconds(value)`: đọc QuotaFailure (`quotaId` chứa «PerDay») và RetryInfo (`retryDelay`, trần 120). Chỉ dùng khi `READ_QUOTA_DETAILS` bật; hằng này **đang `False`** (LC-T141-13).</li><li>Quá giờ → `timeout`; mất mạng → `network`; dữ liệu lạ, trả rỗng, sai khuôn, ghi chép tìm web rỗng → `shape`; bị chặn → `refusal`.</li></ul> |
| `seo_app/ai/openai_provider.py` | <ul><li>`OpenAIProvider(…, *, single_attempt=False)`: `max_retries=0` khi `True`, mặc định giữ 3.</li><li>`kind` ở từng nhánh có sẵn: 401 → `auth`; 403, 404 → `model`; 429 `insufficient_quota` → `quota_day`; 429 khác → `rate`; quá giờ → `timeout`; mất mạng → `network`; 400 → `bad_request`; mã khác theo `status_kind`.</li><li>`_parse`: từ chối, bộ lọc nội dung → `refusal`; `max_output_tokens` → `token_limit`; `failed`, `cancelled`, `incomplete` khác → `shape`; không có chữ, JSON hỏng → `shape`.</li></ul> |
| `seo_app/ai/anthropic_provider.py` | <ul><li>`AnthropicProvider(…, *, single_attempt=False)`: `max_retries=0` khi `True`, mặc định giữ 3.</li><li>`kind` ở từng nhánh có sẵn: 401 → `auth`; 403, 404 → `model`; 429 → `rate`; mất mạng → `network`, riêng `APITimeoutError` → `timeout` (câu giữ như cũ); hết tiền (`credit`, có từ trước) → `quota_day`; 400 → `bad_request`; mã khác theo `status_kind` (529 «quá tải» → `busy`).</li><li>`refusal` → `refusal`; `max_tokens` → `token_limit`; `pause_turn` hết lượt đọc tiếp → `timeout`; không ra khuôn → `shape`; `_schema_error` giữ câu, loại theo lớp lỗi.</li></ul> |
| `seo_app/ai/registry.py` (theo lời giao của Chỉ Huy B) | <ul><li>`make_provider(provider, settings, *, single_attempt=False)`: chỉ đổi **dòng chữ ký** và **dòng `return`** (`cls(api_key, single_attempt=True)` khi bật, ngược lại `cls(api_key)` như cũ). Không đụng docstring và hai dòng đầu thân hàm (chỗ T-142 thêm).</li><li>`AIRouter(…, prepare=…, *, single_attempt=False)`, thuộc tính `single_attempt`; `_provider` gọi `make_provider(hãng, settings)` y như cũ khi tắt, thêm `single_attempt=True` khi bật.</li></ul> |
| `seo_app/ai/limits.py` (mới) | `AutoLimits`, `load_auto_limits()` (mục `[auto]`: `min_seconds_between_calls` 1–120 giây, mặc định 6; `gemini_requests_per_day` 0–100.000, mặc định 0; loại `bool`, chữ, `nan`; thiếu mục, thiếu khóa thì mặc định; câu lỗi chỉ nêu `config/ai.toml` và `[auto]`); `pacific_day(now)`, `reset_at_vn(now)` (theo `ZoneInfo`, đúng giờ mùa hè); `seconds_to_wait(last_call, now, min_seconds)` (hàm thuần, giờ `time.monotonic()`); `daily_limit_reached(used, limits)` (trần 0 không chặn). Không nhập `streamlit` |
| `tests/test_t148_loai_loi.py` (mới) | Loại lỗi từng nhánh của 3 hãng qua thư viện thật + đường truyền giả, so cả câu với câu cũ; chữ máy chủ không lọt; `TokenLimitError`; `retry_after` trần; `quota_details` (đang tắt, và khi bật); `duration_seconds`; `cfut_` |
| `tests/test_t148_mot_lop_thu_lai.py` (mới) | Đếm request qua đường truyền giả: `single_attempt` gửi đúng 1 request với 503, 429, rớt mạng; mặc định gửi như cũ (Gemini 3, OpenAI 4, Anthropic 4); tham số truyền tới từng thư viện; router; quét `import streamlit`; chạy trong `threading.Thread` thường |
| `tests/test_t148_gioi_han.py` (mới) | `[auto]` thiếu, sai dạng, `bool`, ngoài khoảng, file hỏng; `pacific_day` qua hai mốc đổi giờ của Mỹ năm 2026; `reset_at_vn`; `seconds_to_wait`; `daily_limit_reached` |

## Chỗ để ngỏ, tôi đã chọn

1. **Nối router ngay ở phiếu này.** Phiếu ghi để T-149 làm, nhưng Chỉ Huy B giao thêm ngày 19/11 («nối router single_attempt vào registry.py cho T-149», chỉ phần router). Theo ghi chú của Chỉ Huy về các chỗ T-142 sửa:
   - `registry.py` chỉ đổi **dòng chữ ký** `make_provider` và **dòng `return cls(...)`**, cùng lớp `AIRouter`;
   - không đụng khối hằng đầu file, `load_ai_config`, docstring và hai dòng đầu thân `make_provider`;
   - router tắt `single_attempt` gọi `make_provider(hãng, settings)` y như cũ, nên các test thay `make_provider` bằng hàm hai tham số vẫn chạy.

   **Chỗ chồng với T-142 (`035c598`; lượt 2 `ab6b524` không đổi `registry.py`), cần gộp tay một chỗ.** T-142 thêm hai hàm `image_steps`, `provider_label` **ngay trên** dòng `def make_provider(...)`, mà dòng này T-148 thêm tham số `single_attempt`. Git coi hai thay đổi sát nhau là xung đột: đúng **1 chỗ**, ở `seo_app/ai/registry.py`. Cách gỡ:
   - giữ nguyên hai hàm T-142 thêm;
   - dòng chữ ký dùng bản T-148: `def make_provider(provider: str, settings: Settings, *, single_attempt: bool = False) -> AIProvider:`.

   Mọi chỗ khác tự gộp: khối hằng đầu file và `load_ai_config` của T-142; hai dòng đầu thân `make_provider` của T-142 nằm cùng dòng `return cls(...)` của T-148; lớp `AIRouter` của T-148. Không đổi chữ ký thì không truyền được tùy chọn vào lớp provider mà khỏi chép lại phần tìm khóa của `make_provider`, nên tôi giữ cách này và ghi rõ như Chỉ Huy dặn. Bản gộp đã gỡ chạy thử test của cả hai phiếu (mục Bằng chứng); file gỡ sẵn để ở thư mục ghi chú chung (`T-148-registry-gop-T-142.py`).
2. **Vài mã ngoài bảng 2.4**, vẫn chỉ đọc số và chuỗi cố định:
   - 408 (máy chủ báo quá giờ) → `timeout`: trước đây thư viện tự thử lại mã này, nay lượt chạy thử lại theo dòng `timeout`;
   - 529 (Anthropic «quá tải») → `busy`;
   - Gemini có trạng thái `INTERNAL`, `UNAVAILABLE`, `DEADLINE_EXCEEDED` mà mã số lạ → `busy`;
   - mã khác (409, 413, 422, 501…) → `other`.
3. **Loại cho các ca bảng không ghi:**
   - mã 200 mà dữ liệu lạ (trang HTML, nén hỏng) → `shape`;
   - OpenAI `failed`, `cancelled`, `incomplete` (không vì `max_output_tokens`, bộ lọc) → `shape`, vì chưa có câu trả lời dùng được;
   - Anthropic `pause_turn` hết lượt đọc tiếp («AI tìm kiếm quá lâu») → `timeout`;
   - Anthropic hết tiền (lỗi 400 có chữ `credit`, đã kiểm từ trước) → `quota_day`, như 429 thanh toán;
   - `APITimeoutError` của Anthropic → `timeout`, câu báo giữ như cũ («Không kết nối được…»).
4. **Tên loại lạ thì `ValueError`** ngay lúc dựng lỗi, để T-142 hay phiếu sau gõ sai tên bị test bắt.
5. **`retry_after`:** số thực, chặn trong 0–120. Âm, `nan`, chữ thì `None` (lượt chạy dùng mặc định 60 giây).
6. **Khi bật `READ_QUOTA_DETAILS`:** 429 «PerDay» dùng câu có sẵn «Tài khoản Gemini đã hết tiền hoặc hết hạn mức (quota) trong ngày.», vì câu «Đợi một phút» sai với hết lượt ngày. Lúc hằng tắt (hiện nay), không câu nào đổi.
7. **`[auto]`:**
   - số giây nhận cả số lẻ (6.5);
   - số lần mỗi ngày chỉ nhận số nguyên;
   - khóa lạ trong `[auto]` bỏ qua, để phiếu sau thêm khóa không làm hỏng bản cũ;
   - lỗi là `AIError` (loại `other`).
8. **Giờ:**
   - `seconds_to_wait` nhận giờ `time.monotonic()`, không đổi theo giờ máy. Giờ chạy ngược thì chờ đúng một nhịp, không hơn;
   - `pacific_day`, `reset_at_vn` đòi giờ có múi giờ (thiếu thì `ValueError`).
9. **Thêm `daily_limit_reached`:** hàm nhỏ cho dòng `quota_day` «sổ đếm đã chạm trần bạn ghi» (bảng 2.4), để T-149, T-151 dùng chung.

## Ghi nhận cho phiếu sau (không sửa, ngoài phạm vi)

- **Một lần `generate` có thể gửi 2 request.** Đây là phần mềm tự gọi lại với thông số khác, không phải thư viện thử lại, nên `single_attempt` không tắt:
  - Gemini bỏ `thinking_config` khi máy chủ báo 400 về thinking;
  - OpenAI bỏ `reasoning` khi 400 về reasoning;
  - Gemini đời 1.x, 2.x tìm web hai lượt;
  - Anthropic `pause_turn` đọc tiếp tới 5 lượt.

  Sổ đếm ghi theo lần gọi `generate` (T-149) sẽ đếm thiếu ở các ca này. Với cấu hình hiện tại (`gemini-3.8-flash`, tắt tìm web), chỉ còn ca thinking, khi mô hình không nhận mức suy nghĩ đã ghi. Muốn đếm đúng từng request thì provider cần một móc «trước mỗi request» cho lượt chạy (phiếu sau; Lá Chắn xem, LC-T141-12).
- **Lỗi tầng nội dung đang là `other`:**
  - `workflow.py`: bài rỗng, bản viết lại rỗng, chưa có từ khóa;
  - `images/alt.py`: alt rỗng, sai khuôn;
  - câu kiểm đầu vào của thử mù, kế hoạch.

  Các file này ngoài phạm vi phiếu. T-149 đặt `kind="shape"` cho «AI trả bài rỗng» nếu muốn lượt chạy thử lại. Lỗi của provider đi qua các lớp này nguyên vẹn: không chỗ nào bắt rồi dựng lại `AIError` từ lỗi provider.
- **Lô dừng khi 2 bài liền dừng vì `rate` hay `busy`** (LC-T141-13): phần lượt chạy, T-149, T-151.

## Đổi kỳ vọng ca test cũ (R5)

Không đổi ca test cũ nào. Câu báo lỗi giữ nguyên từng chữ (ca mới so cả câu); test câu lỗi có sẵn (T-026, T-028, T-034, `test_ai.py`…) chạy lại qua hết (mục Bằng chứng).

## Điều kiện Lá Chắn (từng mục)

| Điều kiện | Đáp ứng | Test |
|---|---|---|
| **LC-T141-9** (không `streamlit`, dùng được trong luồng thường) | Các file của phiếu (`base.py`, 3 provider, `limits.py`, `registry.py`) không nhập `streamlit`; nạp cả lớp AI không kéo theo `streamlit`. Provider tạo và gọi được trong `threading.Thread` thường; lỗi về tới luồng gọi đúng loại. Không giữ client hay khóa trong đối tượng dùng chung (router do lượt chạy tạo trong luồng, T-149) | `test_ticket_files_do_not_import_streamlit` (6 file), `test_importing_ai_layer_does_not_load_streamlit` (tiến trình riêng), `test_provider_runs_in_a_plain_thread` |
| **LC-T141-12** (một lớp thử lại) | Gemini `HttpRetryOptions(attempts=1)`, OpenAI và Anthropic `max_retries=0` khi `single_attempt=True`. `AIRouter(…, single_attempt=True)` tạo provider ở chế độ đó. Mặc định giữ như cũ cho các trang đang có. Đếm request qua đường truyền giả: đúng 1 request với 503, 429, rớt mạng; mặc định Gemini 3, OpenAI 4, Anthropic 4 | `test_single_attempt_sends_exactly_one_request` (9 ca), `test_default_still_retries_like_before` (3), `test_client_options_passed_to_each_library` (2), `test_single_attempt_success_is_one_request`, `test_router_single_attempt_builds_providers_in_that_mode`, `test_router_single_attempt_reaches_the_library`, `test_default_router_calls_make_provider_like_before` |
| **LC-T141-13** (`kind` từ `code`, `status`; `quota_day`; `retryDelay`; S2; câu và test cũ không đổi) | <ul><li>`kind` đặt từ mã số, trạng thái chuỗi cố định.</li><li>Chữ máy chủ chỉ dùng ở các chỗ đã có: `billing`, `credit`, `prepayment`, khóa sai trả 400, gợi ý 400 đã biết, `credit` của Anthropic.</li><li>`quota_day` từ cấu trúc (QuotaFailure «PerDay», RetryInfo) có hàm và test, nhưng **tắt** (`READ_QUOTA_DETAILS = False`, có test ghim). Tới khi chép được khuôn thật ở buổi thử, mọi 429 khác là `rate`.</li><li>`retryDelay` thành số giây, trần 120.</li><li>Câu báo không chép chữ máy chủ.</li><li>Câu tiếng Việt giữ nguyên; không đổi test cũ nào.</li></ul> Phần «lô dừng khi 2 bài liền `rate`/`busy`» thuộc lượt chạy (T-149) | `test_gemini_status_codes_give_kind_and_same_message` (11), `test_gemini_429_with_billing_words_is_quota_day` (3), `test_reading_429_details_is_off_until_the_real_shape_is_seen`, `test_when_turned_on_429_details_set_kind_and_retry_after` (4), `test_quota_details_ignores_unknown_shapes` (9), `test_retry_after_is_capped_at_120_seconds` (11), ca OpenAI (12), Anthropic (13); mọi ca qua `caught()` kiểm dấu chữ máy chủ không lọt |
| **LC-T140-2** (phần `redact_secrets`) | Mẫu `cfut_[A-Za-z0-9_\-]{20,}`, che ở bất kỳ đâu trong câu (cả dính chữ, chữ hoa, trong địa chỉ). Chuỗi `cfut_` ngắn dưới 20 ký tự không bị che | `test_redact_hides_cloudflare_tokens` (6), `test_redact_keeps_short_cfut_words_and_plain_text` |
| **S2** (không chép chữ máy chủ, không lộ khóa) | Như LC-T141-13; chi tiết lỗi 429 chỉ đọc số giây và tên hạn mức để xếp loại, không đưa chữ nào ra câu báo | như trên |
| **A2** | AI không có thêm công cụ nào; phiếu không đổi lời dặn hay công cụ gửi AI | — (không đổi phần này) |

## Bằng chứng

```text
# Windows 11, Python 3.12.15, ruff 0.16.10, google-genai 2.30.1. Worktree wt-T-148, uv sync --frozen.
# Không gọi AI, Cloudflare, Google, WordPress thật: thư viện thật của từng hãng chạy với đường
# truyền giả (MockTransport); time.sleep được thay ở các ca đếm lần thử lại mặc định.

uv run pytest -q -p no:randomly tests/test_t148_loai_loi.py tests/test_t148_mot_lop_thu_lai.py \
    tests/test_t148_gioi_han.py
  232 passed

# Đột biến (script ở thư mục nháp; mỗi đột biến sửa một chỗ, chạy test T-148 liên quan, trả file
# đúng byte, kiểm bằng SHA-256; chỉ tính «bắt» khi có ca failed, không có error):
#   lượt đầu 24/25 bắt. Sống: M6 (mạng đứt khi đang đọc trả lời mất loại «network»).
#   Thêm ca test_anthropic_failure_while_reading_the_answer (4 ca), chạy lại M6 → bắt.
#   Sau khi trả docstring make_provider về như cũ, chạy lại M16, M17 → bắt. Tổng 25/25:
#   M1 TokenLimitError mất loại · M2 bỏ mẫu cfut_ · M3 503 không còn busy · M4 trần 1000 giây
#   M5 dữ liệu lạ mất shape · M6 mạng đứt khi đọc mất network · M7 Gemini bỏ qua single_attempt
#   M8 bật đọc chi tiết 429 · M9 chữ thanh toán thành rate · M10 PerDay thành PerMinute
#   M11 khóa sai thành model · M12 OpenAI bỏ qua single_attempt · M13 OpenAI hết tiền thành rate
#   M14 Anthropic mặc định không thử lại · M15 Anthropic quá giờ thành mạng · M16 router bỏ qua
#   single_attempt · M17 make_provider bỏ qua single_attempt · M18 ngày theo giờ Việt Nam
#   M19 nửa đêm theo giờ Việt Nam · M20 nhận true làm số giây · M21 trần giãn nhịp 1200
#   M22 giờ ngược chờ quá nhịp · M23 trần 0 chặn hết · M24 OpenAI chưa xong mất shape
#   M25 Gemini 5xx thành other

# Mọi nơi gọi lớp AI, trên đúng commit 1926247 (git status chỉ còn file báo cáo này), 102 file:
#   - test có nhập seo_app.ai, AIError, redact_secrets, make_provider, AIRouter, AI giả;
#   - trang Soạn bài, Kế hoạch, Cài đặt, Bài viết (test_app_pages, test_app_images, test_t101_*…);
#   - thử mù (test_blind_test, test_settings_blind, test_soi_loi_t019…);
#   - test câu lỗi T-026, T-028, T-034 (test_ai_t026/t028/t034, test_soi_loi_t026/t028/t034),
#     test_ai.py, test_ai_openai_gemini*.py; 3 file T-148.
uv run pytest -q -p no:randomly -rfEsxX <102 file>   (chạy 4 phần, mỗi phần một file kết quả)
  phần 1 (26 file): 1666 passed in 1143.89s (0:19:03)
  phần 2 (26 file): 3529 passed, 7 skipped, 7 xfailed, 1 warning in 1210.76s (0:20:10)
  phần 3 (26 file): 2563 passed in 1825.08s (0:30:25)
  phần 4 (24 file): 2514 passed, 1 skipped in 1384.48s (0:23:04)
  cộng: 10272 passed, 8 skipped, 7 xfailed, 0 failed
#   8 skipped: symlink, quyền kiểu POSIX, os.environb (Windows chưa bật Developer Mode).
#   7 xfailed: lỗi Soi Lỗi ghi từ trước (R4-3, SL-T026-3, SL-T028-1, SL-T036-10).
#   1 warning: Pydantic, ở ca T-028 cố ý đưa luồng trả lời hỏng (có từ trước).
#   Hai lượt trước của cùng 102 file bị dừng khi máy khởi động lại (tới 88%, 89%; không có ca
#   hỏng tới đó); lượt này chạy đủ theo từng phần.
# Thư mục data/ của worktree có data/site_index.sqlite (19/11 13:45), do test cũ ghi trong lượt
#   chạy đầu: nhánh tách từ main ddcd23c, chưa có fixture chuyển kho sang thư mục tạm của T-138
#   (yêu cầu 6). Lượt 102 file này không đổi file đó (giờ sửa vẫn 19/11 13:45). Chỉ trong
#   worktree, không đụng thư mục app.

uv run ruff check .                       → All checks passed!
uv run ruff format --check seo_app/ai/    → đã đúng khuôn
# Quét bí mật: 9 file đổi lấy từ 1926247 và báo cáo này, có khóa giả đối chứng (bắt được).
#   Một chỗ báo, có từ trước: chú thích «người-dùng:mật-khẩu@» ở base.py:31 (703a21b, 14/10).
#   Khóa giả trong test mới viết dạng «khoa-gia-t148» (không giống khóa thật).
# Ký tự ẩn, CR, NFC: 0.
# Gộp thử (git merge-tree, 20/11):
#   - main ddcd23c, team/T-143 (chưa có commit mới) → không xung đột;
#   - team/T-142 035c598 (và 28bb809, ab6b524 sau đó) → 1 xung đột ở seo_app/ai/registry.py:
#     T-142 thêm image_steps,
#     provider_label ngay trên dòng chữ ký make_provider mà T-148 thêm single_attempt. Gỡ: giữ
#     hai hàm T-142, dòng chữ ký bản T-148 (mục «Chỗ để ngỏ» 1).
# Bản gộp đã gỡ (worktree tạm tách ở 1926247, git merge --no-commit team/T-142, gỡ bằng script,
#   không commit; xóa worktree tạm sau khi chạy):
uv run ruff check .                       → All checks passed!
uv run pytest -q -p no:randomly -rfEsxX <3 file T-148, 3 file T-142, test_ai, test_ai_openai_gemini,
    test_t062_image_config, test_soi_loi_t062, test_soi_loi_t051, test_blind_test,
    test_settings_blind, test_soi_loi_t019, test_soi_loi_t026>
  1098 passed, 2 xfailed in 343.79s (0:05:43)
#   2 xfailed: SL-T026-3, lỗi Soi Lỗi ghi từ trước. File registry.py đã gỡ: thư mục ghi chú
#   chung, T-148-registry-gop-T-142.py.

# Cây gộp đủ (theo bài học «gộp thử với nhánh chờ gộp»): worktree tạm tách ở 1926247, gộp
#   f6ec79b (main + T-137 + T-138, cây Chỉ Huy đang gộp; commit gộp tạm trong worktree tạm,
#   không push), rồi team/T-142 28bb809 (--no-commit, gỡ registry.py bằng cùng script: ra đúng
#   file gỡ sẵn). T-138 không xung đột chữ với T-148.
uv run ruff check .                       → All checks passed!
uv run pytest -q -p no:randomly -rfEsxX <111 file: 102 file trên (lấy lại trong cây gộp) và 9 file
    test của T-137, T-138, T-142 (test_t137_*, test_soi_loi_t137, test_t138_*, test_soi_loi_t138,
    test_t142_*, test_soi_loi_t142)>   (chạy 4 phần)
  phần 1 (28 file): 1761 passed in 1344.08s (0:22:24)
  phần 2 (28 file): 3725 passed, 7 skipped, 7 xfailed, 1 warning in 1371.54s (0:22:51)
  phần 3 (28 file): 3743 passed, 6 xfailed in 2480.25s (0:41:20)
  phần 4 (27 file): 2 failed, 1443 passed, 1 skipped in 1327.85s (0:22:07)
#   6 xfailed của phần 3: SL-T142-1, SL-T142-2 (Soi Lỗi T-142 ghi, ở test_soi_loi_t142).
#   2 failed, đều là test của T-142: test_t142_config_registry.py
#   ::test_router_never_asks_for_cloudflare_when_writing, ::test_write_page_does_not_ask_for_cloudflare_key
#   («Chưa có khóa Google Gemini»). Đây là SL-T142-1: bản test của T-142 ở 28bb809 chưa theo
#   cấu hình Gemini của T-138. T-142 sửa ở lượt 2 (ab6b524), sau khi tôi dựng cây gộp. Kiểm:
#   - 2 ca đó trên f6ec79b + ab6b524, không có T-148 → 2 passed;
#   - chạy riêng 2 ca đó trên cây có T-148 + 28bb809 → 2 failed như trong lượt.
#   Không do T-148.
# Cập nhật cây gộp lên T-142 mới nhất ab6b524 (đã chứa f6ec79b; registry.py của T-142 không đổi
#   so với 28bb809, gỡ ra đúng file gỡ sẵn), ruff sạch, chạy lại 49 file: cả phần 4 cũ (có 2 ca
#   hỏng), mọi test T-142 và T-148, test T-142 lượt 2 sửa, test lõi lớp AI:
  phần 1 (25 file): 1803 passed, 1 skipped, 4 xfailed, 1 warning in 1182.09s (0:19:42)
  phần 2 (24 file): 1388 passed, 1 skipped in 1126.77s (0:18:46)
  cộng: 3191 passed, 2 skipped, 4 xfailed, 0 failed
#   2 ca SL-T142-1 nay qua. 4 xfailed: SL-T026-3, SL-T028-1 (ghi từ trước). Cây gộp không tạo
#   thư mục data/ (có fixture của T-138). Xóa worktree tạm sau khi chạy.
```

## Đối chiếu tiêu chí xong

| Tiêu chí | Đáp ứng |
|---|---|
| Yêu cầu 1: `AIError.kind`, `TokenLimitError` | `base.py`; `test_aierror_default_kind_is_other_and_retry_after_unknown`, `test_kind_must_be_one_of_the_fixed_names`, `test_token_limit_error_has_its_kind_and_old_message` |
| Yêu cầu 2: phân loại ở 3 provider | Từng nhánh có ca riêng: Gemini 25 ca, OpenAI 22, Anthropic 25 (kể cả mạng đứt khi đang đọc trả lời) |
| Yêu cầu 3: `quota_day`, chi tiết 429 tắt, `retry_after` | Ca chữ thanh toán, ca hằng tắt, ca bật, ca khuôn lạ, trần 120 |
| Yêu cầu 4: một lớp thử lại | Tùy chọn ở 3 provider, mặc định như cũ; đếm request; router (theo lời giao thêm) |
| Yêu cầu 5: `limits.py` | `test_t148_gioi_han.py` |
| Yêu cầu 6: `cfut_` | 7 ca |
| Yêu cầu 7: không `streamlit`, luồng thường | 8 ca |
| Yêu cầu 8: test, chạy lại test câu lỗi có sẵn | 3 file mới; 102 file gọi lớp AI (mục Bằng chứng) |
| `uv run ruff check .` sạch | Có |
| Báo cáo | File này |

## Rủi ro và điểm cần chú ý

- **Chưa thấy khuôn lỗi 429 theo ngày tận mắt.** Tới khi bật `READ_QUOTA_DETAILS` sau buổi thử (T-141 7.4.2), hết lượt ngày sẽ hiện như «gọi dày quá»: lượt chạy thử lại tới trần rồi dừng (đã ghi trong biên bản Lá Chắn, mục 10).
- **Gộp với T-142 cần sửa tay 1 chỗ** ở `registry.py`: dòng chữ ký `make_provider` (mục «Chỗ để ngỏ» 1). Bản gộp đã gỡ chạy qua test của cả hai phiếu (mục Bằng chứng); file gỡ sẵn ở thư mục ghi chú chung.
- **Đếm thiếu ở vài ca app tự gọi lại đổi thông số** (mục «Ghi nhận»): không ảnh hưởng cấu hình hiện tại trừ ca mô hình không nhận mức suy nghĩ.
- `AIError(…, kind="tên lạ")` ném `ValueError`: an toàn cho mã mới (test bắt), nhưng phiếu sau phải dùng đúng 12 tên.

## Câu hỏi cho chủ dự án

Không có.

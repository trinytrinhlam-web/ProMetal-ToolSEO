# Báo cáo T-142 · Client Cloudflare Workers AI, ảnh AI sạch, kho ảnh AI (phiếu A)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-142](../tickets/T-142-client-cloudflare-anh-ai-sach.md) · đợt 1 (song song T-143, T-148, T-144 → T-153) |
| Nhánh | `team/T-142`, từ `main` `ddcd23c` |
| Ngày nộp | 2026-11-19 (+07:00, giờ theo lệnh `date`, ghi ở commit) |
| Kết quả | Hoàn thành yêu cầu 1–13. Chưa nối vào lượt chạy, giao diện; chưa bật cho bài thật (cần lần gọi thử cùng chủ dự án) |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã có **bộ phận gọi Cloudflare để tạo ảnh minh họa**: gửi đi một câu mô tả ảnh bằng tiếng Anh, nhận về một ảnh.
- **Ảnh nhận về được làm sạch trước khi dùng:** app dựng lại ảnh từ từng điểm ảnh, nén WebP, kiểm lại. Ảnh lên website không mang theo dữ liệu lạ nào (không vị trí, không ghi chú ẩn).
- **Ảnh AI luôn được đánh dấu do chính phần mềm làm:** tên file `minh-hoa-ai-…`, thẻ «ảnh AI», không mã công trình, không khu vực.
- **Ảnh tạo xong nằm trên máy** trong thư mục `data/ai_images` cho tới lúc gửi bài; ảnh cũ không còn dùng thì app tự dọn (sau 14 ngày).
- **Hai biến mới trong file `.env`:** mã tài khoản và mã truy cập Cloudflare, có chú thích cách tạo mã truy cập chỉ có quyền tối thiểu. Mã truy cập không bao giờ hiện ra màn hình hay câu báo lỗi.
- **Bạn chưa phải làm gì lúc này.** Bộ phận này chưa nối vào trang Soạn bài (phiếu sau). Trước khi dùng thật có một buổi thử: tạo tài khoản Cloudflare, tạo mã truy cập, gọi thử một lần cùng Chỉ Huy.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/cloudflare_images.py` (mới) | Client Cloudflare: `generate(prompt, model, steps)` tạo một ảnh, `verify_token()` kiểm mã truy cập; `load_image_task()` đọc `[tasks.image]`; lỗi `CloudflareImageError` có `kind` cho lượt chạy tự động |
| `seo_app/images/generated.py` (mới) | `make_generated_web_image` (ảnh về → WebP sạch), `wrap_generated` (kèm thẻ ảnh AI, băm), `generated_file_name`, kho `AIImageStore` (`data/ai_images/`) |
| `seo_app/ai/registry.py` | Hãng chỉ tạo ảnh `IMAGE_ONLY_PROVIDERS = {"cloudflare": …}`; `IMAGE_PROVIDERS` thêm `"cloudflare"`; `load_ai_config` kiểm Cloudflare chỉ cho `[tasks.image]` và kiểm `steps`; `image_steps()`, `provider_label()`; 2 dòng đầu `make_provider` chặn Cloudflare |
| `seo_app/config.py` | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` vào `ENV_VARS`; `Settings` thêm hai trường, cả hai `repr=False` |
| `.env.example` | Khối «Ảnh minh họa AI: Cloudflare Workers AI», chú thích tiếng Việt cho từng biến, không giá trị |
| `seo_app/content/blind_test.py` | Một dòng: bảng việc–mô hình dùng `provider_label()` (không `KeyError` khi `[tasks.image]` dùng Cloudflare) |
| `tests/fake_cloudflare.py` (mới) | Cloudflare giả: adapter `requests` gắn vào phiên, như `FakeGoogle` |
| `tests/test_t142_cloudflare_client.py`, `tests/test_t142_generated_images.py`, `tests/test_t142_config_registry.py` (mới) | Test của phiếu (mục Bằng chứng) |

Không thư viện mới (`requests`, Pillow đã có). Không gọi Cloudflare thật.

## Chỗ lệch thiết kế, đã chọn

1. **Không đưa `cloudflare` vào `PROVIDERS`** (thiết kế T-140 2.9 ghi `PROVIDERS["cloudflare"] = …`). `PROVIDERS` được thử mù (`provider_status`, ô chọn hãng) và tab «Kết nối» duyệt qua: thêm vào thì Cloudflare hiện thành một hãng viết bài, trạng thái khóa lại sai (bảng khóa ở `blind_test.provider_status` chỉ có 3 hãng). Thay bằng `IMAGE_ONLY_PROVIDERS` riêng; `load_ai_config` nhận `cloudflare` chỉ ở `[tasks.image]`, việc khác báo «Cloudflare Workers AI chỉ dùng để tạo ảnh (mục [tasks.image])».
2. **`IMAGE_PROVIDERS` giữ Gemini, OpenAI và thêm Cloudflare** (thiết kế ghi chỉ còn Cloudflare). Bỏ Gemini thì hỏng các điều bảo vệ T-062 đang được test (bật `[tasks.image]` bằng Gemini không bắt nhập khóa Gemini khi chỉ viết bài) mà không được gì: app chưa có mã tạo ảnh bằng Gemini, OpenAI.
3. **`make_provider("cloudflare")` báo `AIError`**, không `KeyError`. Ảnh Cloudflare tạo bằng `CloudflareImageClient`, không qua lớp AI viết chữ. Đã báo trước Chỉ Huy B: đây là chỗ duy nhất có thể chồng với T-148 trong `registry.py` (T-148 nối router).
4. **`steps` không nằm trong `TaskConfig`** (file `base.py` thuộc T-148 cùng đợt): `load_ai_config` kiểm `steps` ngay lúc đọc (câu lỗi sớm ở trang Cài đặt), `load_image_task()` đọc lại giá trị đã kiểm.
5. **Mẫu `cfut_` của `redact_secrets` làm ở T-148** (cùng file `base.py`, Chỉ Huy B đã chuyển). Ở đây token không bao giờ vào câu lỗi: mọi câu lỗi là câu cố định, có test.
6. **Lớp vận chuyển** (`_Bearer`, `_refuse_redirect`, `_read_limited`, `_Redirected`, `_TooLarge`, `_close_and_status`) nhập từ `seo_app/google/sheets.py` như client Search Console, không chuyển sang module chung (sẽ đụng `sheets.py`, `search_console.py` ngoài phạm vi). Đề xuất dời sau.
7. **`Settings.status()` chưa thêm dòng Cloudflare:** trang Cài đặt (T-146) làm phần hiện «đã nhập / chưa nhập»; thêm ở đây sẽ đổi số huy hiệu mà test cũ của trang Cài đặt đang đếm.
8. **Mã tài khoản kiểm lúc tạo client, không lúc đọc `.env`:** sai dạng thì chỉ việc tạo ảnh báo lỗi (câu không chép giá trị), các trang khác vẫn chạy.

## Điều kiện Lá Chắn đã làm

| Mã | Làm thế nào | Test |
|---|---|---|
| **LC-T140-1** đường gọi cố định | Hằng `API_BASE`; hai đường `accounts/<mã>/ai/run/<mô hình>`, `user/tokens/verify`; mã tài khoản `^[0-9a-f]{32}$`; mô hình trong `ALLOWED_MODELS`; không query, không header riêng (chỉ `Authorization` qua `_Bearer`, `Content-Type` của `json=`); `allow_redirects=False`, `max_redirects = 0`, móc `_refuse_redirect`; giờ chờ ≤ 60 s; đọc theo luồng ≤ 16 MB; kiểm lại tên máy trước khi gửi (`MSG_BLOCKED`); không AI Gateway | `test_generate_sends_exactly_two_fields_to_the_fixed_route` (ghim từng lớp: `allow_redirects`, `stream`, `timeout`, móc, `_Bearer`, không `params`/`headers`), `test_session_never_follows_redirects_and_never_retries_by_itself`, `test_route_is_built_only_from_constants_and_checked_values` (đổi sang `gateway.ai.cloudflare.com` → không gửi), `test_redirect_is_refused_and_never_followed`, `test_account_id_must_be_32_lowercase_hex`, `test_model_must_be_in_the_allow_list` |
| **LC-T140-2** token, mã tài khoản | Chỉ trong `.env`; `Settings` `repr=False` cả hai; mọi ngoại lệ `requests` thành câu cố định (`raise … from None`, không chép `str(exc)`); không `logging`; mẫu `cfut_` ở T-148 | `test_repr_never_shows_account_or_token`, `test_requests_errors_become_fixed_messages_without_url`, `test_server_message_never_reaches_the_user`, `test_settings_read_cloudflare_values_and_hide_them`, `test_new_modules_never_import_streamlit_or_logging` |
| **LC-T140-3** thân lệnh | Đúng `{"prompt", "steps"}`; `steps` 1–8, loại `bool`; prompt 1–2048 ký tự, dài hơn báo lỗi, không cắt | `test_steps_must_be_a_real_integer_from_one_to_eight`, `test_bad_prompt_is_refused_before_any_request`, `test_prompt_of_exactly_2048_characters_is_sent_whole`, `test_odd_steps_are_refused_when_loading` |
| **LC-T140-4** câu trả lời | HTTP 200 + `Content-Type` JSON + bộ đọc chặt (`NaN`/`Infinity`, khóa trùng, `RecursionError`); `success is True`; `result.image` chuỗi ≤ 12.000.000 ký tự, `b64decode(validate=True)`, ≤ 9 MB; có `url` hay không phải base64 thì từ chối; mã lỗi chỉ đọc khi là `int` trong danh sách đã biết (5007 là HTTP 400); `message` không lên trang | `test_errors_become_fixed_vietnamese_messages_with_kind` (19 ca), `test_error_code_is_read_only_when_it_is_a_real_integer`, `test_odd_json_is_refused`, `test_only_base64_image_is_accepted_never_a_link` (không có lệnh GET nào), `test_base64_string_length_is_checked_before_decoding`, `test_decoded_image_size_is_limited`, `test_response_body_is_read_with_a_limit` |
| **LC-T140-5** ảnh về → WebP sạch | `_open` với `formats=("JPEG", "PNG", "WEBP")`, một khung, cạnh 256–2048, từ chối ảnh gần một màu; ảnh mới `Image.frombytes` (bỏ `info`); `make_web_image`; byte ra qua `_check_webp`, `gps is None` | `test_dirty_image_comes_out_without_any_metadata` (JPEG, PNG, WebP có EXIF + GPS + XMP + ICC + COM / `tEXt`, `iTXt`), `test_png_private_chunk_never_reaches_the_webp`, `test_animated_image_is_refused`, `test_odd_size_is_refused` (4096, 2049, 255, 200 px), `test_blank_image_is_refused`, `test_not_an_allowed_image_is_refused` (GIF, BMP, rỗng, chữ) |
| **LC-T140-6** kho `data/ai_images/` | Tên = SHA-256 byte WebP, mẫu `^[0-9a-f]{64}\.webp$`; ghi nguyên tử; `dir_has_link` trước mỗi lần đọc, ghi, xóa; thư mục phải nằm trong `data/` đã chặn ở `.gitignore` (`_cache_dir_is_ignored`); ≤ 2 MB; đọc lại khớp băm rồi `_check_webp`; dọn chỉ tên đúng mẫu, file thường, giữ băm còn được nhắc; 14 ngày / 500 file / 500 MB | `test_save_and_load_by_hash`, `test_load_refuses_odd_names`, `test_load_detects_a_changed_file`, `test_load_detects_dirty_webp_with_matching_name`, `test_save_refuses_anything_but_clean_webp`, `test_save_refuses_folder_that_git_would_commit`, `test_data_folder_link_is_never_read_or_written` (junction thật trên Windows), `test_cleanup_*` (4 ca) |
| **LC-T140-7** không tự thử lại | `HTTPAdapter` mặc định `max_retries=0`; client không vòng thử lại; lỗi mang `kind` để lượt chạy (T-149) quyết. Đếm neuron là kho của T-143 | `test_session_never_follows_redirects_and_never_retries_by_itself`, `test_failed_call_is_never_retried_by_the_client` |
| **LC-T140-8** kiểm token | `verify_token()` `GET user/tokens/verify`, chỉ đọc `result.status` (`active`, `disabled`, `expired`); `TOKEN_MESSAGES["active"]` nói rõ quyền Workers AI biết ở lần tạo ảnh đầu; nút bấm ở T-146; README (token người dùng) ở T-147 | `test_verify_token_reads_only_the_status`, `test_verify_token_odd_status_is_refused`, `test_verify_token_errors_use_the_same_fixed_messages`, `test_active_token_message_says_workers_ai_right_is_not_proven` |
| **LC-T140-13** ảnh AI do mã gắn nhãn | `wrap_generated` gắn `ImageTags.for_ai_image(category)` ngay lúc bọc (hạng mục lạ: bỏ, không giữ chữ); `generated_file_name` luôn `minh-hoa-ai-…` | `test_wrap_generated_tags_are_set_by_code`, `test_unknown_category_is_dropped_not_kept`, `test_file_name_always_marks_ai` |
| **LC-T140-17** gọi thử thật | Không gọi trong phiếu. Buổi thử cùng chủ dự án xác nhận vị trí `result.image`, định dạng, cỡ ảnh, neuron mỗi ảnh, quyền Read, kiểm token | — |
| **LC-T140-18** test với Cloudflare giả | `tests/fake_cloudflare.py`, dưới bộ chặn mạng; đủ ca ở các dòng trên; tham số lớn có `ids` ngắn. Không chuyển lớp vận chuyển sang module chung (mục «Chỗ lệch» 6) | Cả 3 file test |
| **LC-T141-9** gọi được từ luồng nền | Hai module mới không nhập `streamlit`, `logging`; client không giữ trạng thái phiên | `test_new_modules_never_import_streamlit_or_logging`, `test_generate_works_from_a_plain_thread` |
| **LC-T141-12** lỗi trả `kind`, không tự thử lại | `CloudflareImageError.kind` theo bảng 2.4 của thiết kế T-141 (`quota_day` 3036; `busy` 3040, 5xx; `rate` 429 khác; `auth` 401, 403, 3023; `timeout` 408, hết giờ; `network`; `bad_request`; `shape`) | `test_errors_become_fixed_vietnamese_messages_with_kind`, `test_requests_errors_become_fixed_messages_without_url` |

Thêm (T-062, C7): thiếu khóa Cloudflare không làm trang Soạn bài đòi khóa: `test_write_page_does_not_ask_for_cloudflare_key`, `test_router_never_asks_for_cloudflare_when_writing`; trang Cài đặt hiện đúng dòng việc ảnh: `test_settings_page_lists_the_cloudflare_image_task`.

## Bằng chứng

```text
# Windows 11, Python 3.12.15, Pillow 13.0.0, requests 2.34.2, ruff 0.16.10. Chạy trong
# worktree wt-T-142. Không gọi Cloudflare, AI, Google, WordPress thật (bộ chặn mạng của conftest).

# 3 file test mới:
uv run pytest -q -p no:randomly tests/test_t142_cloudflare_client.py \
    tests/test_t142_generated_images.py tests/test_t142_config_registry.py
  200 passed in 69.22s

# 3 file mới + 32 file của mọi nơi gọi registry.py, config.py, blind_test.py, .env.example và
# các test quét cả gói seo_app/ (lớp AI 3 hãng, T-026, T-028, T-034, T-051, T-062, thử mù,
# cấu hình, .env, set_password, trang Cài đặt T-084, T-101, test_images_process,
# test_la_chan_t096, test_t103_plan_prompt, test_wordpress_release, test_app_images,
# test_app_pages):
uv run pytest -q -p no:randomly -rfEx <35 file>
  2580 passed, 4 xfailed, 1 warning in 894.37s (0:14:54)
#   4 xfailed: lỗi Soi Lỗi ghi từ trước (SL-T026-3 ×2, SL-T028-1 ×2).
#   1 warning: Pydantic, ở ca T-028 cố ý đưa luồng trả lời hỏng (có từ trước).
# Sau lượt chạy: worktree không có thư mục data/ (test không ghi kho thật).

uv run ruff check .                                       → All checks passed!
# detect-secrets (PYTHONUTF8=1, bản sao 11 file của phiếu ngoài git + file mồi tiếng Việt,
# scan --all-files .): 0 kết quả ở file của phiếu; file mồi bị bắt (3 mục).
# Ký tự ẩn, CR, NFC: 0 ở mọi file mới, file đã sửa.
```

## Đối chiếu yêu cầu của phiếu

| Yêu cầu | Đáp ứng |
|---|---|
| 1. Client, đường gọi cố định | `cloudflare_images.py`, LC-T140-1 |
| 2. Thân lệnh | LC-T140-3 |
| 3. Câu trả lời | LC-T140-4 |
| 4. Loại lỗi `kind` | `CloudflareImageError(kind=…)`, cùng tên thuộc tính `kind` với T-148 |
| 5. Không tự thử lại, câu lỗi cố định, không `logging` | LC-T140-7, LC-T140-2 |
| 6. Kiểm tra kết nối | `verify_token()`, `TOKEN_MESSAGES` |
| 7. Ảnh về → WebP sạch | `make_generated_web_image` |
| 8. Kho `data/ai_images/` | `AIImageStore` |
| 9. Ảnh AI do mã gắn nhãn | `wrap_generated`, `ai_image_tags`, `generated_file_name` |
| 10. `registry.py` | Hãng chỉ tạo ảnh, `steps`, provider lười (mục «Chỗ lệch» 1–4) |
| 11. `config.py`, `.env.example` | Hai biến, `repr=False`, chú thích |
| 12. Gọi được từ luồng nền | LC-T141-9 |
| 13. Test với Cloudflare giả | 3 file test, `tests/fake_cloudflare.py` |

## Rủi ro và điểm cần chú ý

- **Năm điều chỉ biết ở lần gọi thử thật** (LC-T140-17): vị trí `result.image`, định dạng ảnh, cỡ ảnh, neuron thật mỗi ảnh, quyền Read có đủ không. Mã đã chọn cách an toàn cho cả 5 (nhận JPEG, PNG, WebP; cạnh 256–2048; không tự thử lại).
- **`registry.py` cùng sửa với T-148:** chỗ có thể chồng là 2 dòng đầu thân `make_provider` (đã báo Chỉ Huy B).
- **Lớp vận chuyển nhập tên riêng (`_…`) từ `sheets.py`:** đổi lớp đó thì chạy cả test của Cloudflare. Nên dời sang module chung ở phiếu sau.
- **`requests` vẫn đọc biến môi trường proxy, chứng chỉ** (như client Sheets, Search Console, WordPress): nằm trong nhóm rủi ro «phần mềm khác trên máy đổi môi trường» đã có.

## Đề xuất

- T-149 (lõi chạy): tạo `CloudflareImageClient` trong luồng, đọc `load_image_task()`, ghi neuron vào kho T-143 **trước** khi gọi, gọi `wrap_generated` với `max_edge_px`, `webp_quality` từ `load_image_settings()`, lưu bằng `AIImageStore.save`, dọn bằng `cleanup(keep=<băm trong các nháp>)`.
- T-146 (Cài đặt): nút «Kiểm tra kết nối» gọi `verify_token()`, hiện `TOKEN_MESSAGES[...]`.
- Phiếu sau: chuyển lớp vận chuyển chung ra `seo_app/http_guard.py`, chạy test cả ba client.

## Câu hỏi cho chủ dự án

Không có.

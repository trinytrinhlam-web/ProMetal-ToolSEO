# Báo cáo T-034 · Lỗi Thấp còn lại của lớp AI và thử mù (sau T-019)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`), bên Chỉ Huy B, cloud Linux · model: Claude Opus 5.5 |
| Phiếu | [T-034](../tickets/T-034-loi-thap-lop-ai-sau-t019.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành (7/7 lỗi đã sửa) |

## Tóm tắt (cho chủ dự án)

- Thử mù che kỹ hơn: AI tự xưng "Claude Opus 5.5", "Gemini 3 Pro" thì số phiên bản cũng bị che. Số liệu trong bài ("dày 5.5 mm") giữ nguyên.
- Claude viết bài thử quá dài: câu lỗi giờ bảo hạ effort, như ChatGPT và Gemini. Trước đây câu này bảo sửa một mục người dùng không có.
- Mạng hay proxy làm hỏng dữ liệu nén: app báo "dữ liệu lạ", không còn báo nhầm "không kết nối được". Áp dụng cả ở nút Kiểm tra khóa.
- Ô tên mô hình ở trang thử mù từ chối ký tự lạ (ngoặc vuông, dấu sao…). Câu báo thiếu file cấu hình không còn lộ đường dẫn thư mục trên máy.
- Sửa lỗi hiếm khi nhiều phần của app cùng tạo kết nối AI một lúc (thử mù chạy song song). Trang Soạn bài không đổi gì.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | `ignoring_custom_headers` không gỡ biến khỏi `os.environ` nữa (SL-T019-5); khóa `_ENV_LOCK` gọi lồng được (LC-T028-1); hàm mới `caused_by_decoding` (LC-T028-3). |
| `seo_app/ai/anthropic_provider.py` | Bài sai khuôn mà luồng báo `stop_reason = max_tokens` thì ném `TokenLimitError`, câu chữ giữ nguyên (SL-T019-4). Nhánh `APIConnectionError` do giải nén hỏng ra `bad_response_error` (LC-T028-3). |
| `seo_app/ai/openai_provider.py` | Nhánh `APIConnectionError` do giải nén hỏng ra `bad_response_error` (LC-T028-3). |
| `seo_app/env_file.py` | Nút Kiểm tra khóa (Anthropic, OpenAI): như trên (LC-T028-3). |
| `seo_app/content/blind_test.py` | Che số phiên bản / biến thể đứng liền sau tên đã che (SL-T019-3). `validate_request` chỉ nhận tên mô hình gồm `[A-Za-z0-9._:/@-]` (LC-T019-1). |
| `seo_app/ai/registry.py` | Thiếu file: "Không thấy file cấu hình AI: config/ai.toml." (LC-T019-2). |
| `tests/test_ai_t034.py` | **Mới**, 33 trường hợp cho mọi nhánh mới. |
| `tests/test_soi_loi_t019_luot2.py`, `tests/test_soi_loi_t028.py` | Bỏ `xfail` của 3 test đã sửa xong (xem dưới). |
| `tests/test_soi_loi_t028.py`, `tests/test_ai_t028.py` | Đổi phần kiểm **bên trong khối** của 4 test vì cơ chế đổi (xem "Sửa test"). |

### Cách sửa từng lỗi

| Mã | Cách sửa |
|---|---|
| SL-T019-3 | Thêm `_VERSION` sau tên đã che, cả ở `_VENDOR_WORDS` lẫn tên mô hình của ứng viên. Phần này chỉ ăn các chữ đứng **liền sau** tên, cách bằng dấu cách, không qua dòng mới: số (`5.5`, `6.1`, `3`, `v2`, `4o`) hoặc biến thể (`Pro`, `Flash`, `Ultra`, `mini`, `nano`, `lite`, `turbo`, `max`, `plus`, `preview`, `thinking`, `exp`, `latest`). Số dính chữ như `5.5mm` không bị ăn. Số đứng riêng trong bài không bị đụng. |
| SL-T019-4 | Thư viện kiểm khuôn lúc khối chữ kết thúc, **trước** sự kiện mang lý do dừng. Khi gặp `ValidationError` bên trong `stream`, `_cut_by_token_limit` đọc tiếp các sự kiện thô còn lại của luồng (tối đa 50, dữ liệu đã có sẵn, không gọi thêm lần nào) để tìm `message_delta.stop_reason`. Đúng `max_tokens` thì ném `TokenLimitError`. Câu chữ giống từng chữ câu T-028, nên Soạn bài không đổi (`test_token_limit_anthropic_real_library_message_unchanged` vẫn qua). Mọi trục trặc lúc đọc tiếp (thư viện đổi tên thuộc tính, mạng đứt, dữ liệu lạ) đều trả `False`, tức là giữ cách báo cũ. |
| SL-T019-5 | Không gỡ biến khỏi `os.environ`. Thư viện chỉ đọc 4 biến bằng `os.environ.get` trong `anthropic/_client.py` và `openai/_client.py`. Trong khối, tên `os` của **đúng hai module đó** được trỏ tạm sang `_OsWithoutIgnored`: mọi thứ như `os` thật, riêng `environ` là một khung nhìn chỉ đọc không thấy `IGNORED_ENV`. Ra khỏi khối thì trả `os` thật. Luồng khác và phần còn lại của máy luôn thấy `os.environ` nguyên vẹn, nên không còn `KeyError`. **Lưới an toàn:** nếu bản thư viện khác không có tên `os` trỏ tới module `os` thật thì quay về cách cũ (gỡ biến tạm thời), để header lạ không bao giờ tới client. Có test cho nhánh này. |
| LC-T028-1 | `_ENV_LOCK` là `_ReentrantLock`: bọc `threading.RLock`, có thêm `locked()`, vì `RLock` của Python 3.12 chưa có hàm này mà test cũ dùng. Gọi lồng trong cùng luồng không treo. Vẫn cần khóa: hai luồng cùng trỏ/trả `os` của module phải theo thứ tự, nếu không một luồng có thể trả `os` thật giữa lúc luồng kia đang tạo client. |
| LC-T028-3 | `caused_by_decoding` lần theo `__cause__` / `__context__` (tối đa 20 bước, chống vòng) tìm `DecodingError` của httpx/httpx2. Dùng ở nhánh `APIConnectionError` của 2 provider và 2 hàm kiểm tra khóa. Lỗi kết nối thật vẫn ra câu "Không kết nối được tới …" (có test đối chứng). |
| LC-T019-1 | Thêm `_MODEL_CHARS = [A-Za-z0-9._:/@-]+`, kiểm trước `_maskable`. Câu lỗi cố định, **không chép lại tên người dùng gõ**. 42 tên thật trong `test_real_model_names_are_accepted` vẫn qua. |
| LC-T019-2 | Câu lỗi chỉ ghi `config/{tên file}`, như các nhánh khác của hàm. |

### Test đã bỏ `xfail`

1. `tests/test_soi_loi_t019_luot2.py::test_version_number_after_vendor_word_is_masked` (3 trường hợp, SL-T019-3)
2. `tests/test_soi_loi_t019_luot2.py::test_blind_token_limit_anthropic_real_library_points_to_effort` (SL-T019-4)
3. `tests/test_soi_loi_t028.py::test_gzip_garbage_is_strange_data` (2 trường hợp, LC-T028-3 / SL-T028-3)

Không bỏ `xfail` nào khác. `test_deep_library_mismatch_is_reported_as_library` (SL-T028-1) vẫn `xfail`: lỗi đó không thuộc phiếu.

### Sửa test (cần Soi Lỗi và Lá Chắn xem kỹ)

Phiếu yêu cầu không gỡ biến khỏi `os.environ`. Có 4 test khẳng định đúng điều ngược lại **bên trong** khối `ignoring_custom_headers` (`assert name not in os.environ`), tức là kiểm cơ chế cũ chứ không kiểm mục tiêu:

- `test_soi_loi_t028.py`: `test_unicode_value_restored_exactly`, `test_only_one_of_two_variables_set`, `test_empty_value_is_restored`
- `test_ai_t028.py`: `test_ignoring_custom_headers_keeps_proxy_and_certificates`

Tôi chỉ thay dòng kiểm bên trong khối bằng bất biến mới, **chặt hơn**:
1. Thư viện (`anthropic._client`, `openai._client`) không thấy biến, kể cả biến rỗng (hàm phụ `library_sees` trong `test_ai_t028.py`).
2. `os.environ` vẫn giữ đúng giá trị.

Mọi dòng kiểm khác giữ nguyên: trả lại đúng giá trị, không tự thêm biến, proxy và chứng chỉ vẫn thấy. Các test chứng minh header lạ không tới client **không đổi gì** và vẫn qua: `test_generate_ignores_custom_headers_env`, `test_check_ignores_custom_headers_env`, `test_many_threads_creating_clients_at_once`, `test_generate_ignores_openai_org_and_project_env`, `test_proxy_env_still_used_by_provider_clients`… `test_other_threads_reading_environment_never_fail` cũng không đổi.

## Bằng chứng

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q
3383 passed, 4 skipped, 7 xfailed, 1 warning in 159.07s
# (trước phiếu: 13 xfailed; bỏ đúng 6 trường hợp xfail đã sửa)

$ uv run pytest -q tests/test_ai_t034.py
33 passed

# SL-T019-5: chạy riêng tests/test_soi_loi_t028.py 30 lần
pass=30 fail=0
```

## Đối chiếu tiêu chí xong

- [x] 7 lỗi đã sửa (bảng "Cách sửa từng lỗi"; test `tests/test_ai_t034.py`)
- [x] Test `xfail` tương ứng đã bỏ dấu và qua (3 test, 6 trường hợp)
- [x] `tests/test_soi_loi_t028.py` chạy riêng 30 lần, 0 hỏng
- [x] Báo cáo này
- [x] Câu lỗi mới đều cố định tiếng Việt, không chép chữ máy chủ hay tên người dùng gõ, không có khóa
- [x] Không sửa `app/**`, `config/**`, `seo_app/sanitize.py`; không thêm thư viện

## Rủi ro và điểm cần chú ý

1. **SL-T019-5 dựa vào cách thư viện viết**: hai module `_client` đọc biến bằng `os.environ.get` qua tên `os` của module. Đổi tên `os` thì có lưới an toàn (quay về gỡ biến). Đổi sang đọc biến ở module khác thì lưới **không** tự bắt. Khi đó các test "header lạ không tới client" (`test_libraries_would_add_custom_headers_without_fix` và các test kèm) sẽ đỏ khi nâng thư viện. Vì vậy nâng thư viện phải chạy đủ test.
2. Trong khối, luồng khác đang chạy code của `anthropic._client` / `openai._client` cũng thấy khung nhìn đã lọc. Hai module này chỉ đọc `os.environ` lúc tạo client, nên không ảnh hưởng.
3. **SL-T019-3**: sau tên hãng, số đi liền cũng bị che. Ví dụ "Claude 3 năm" thành "«đã ẩn tên mô hình» năm". Bài về cửa sắt hầu như không có tên hãng AI, và việc che chỉ ảnh hưởng phần hiện trước khi chấm, nên chấp nhận được.
4. **SL-T019-4**: muốn nhận ra bị cắt thì phải đọc tiếp vài sự kiện còn lại của luồng, qua thuộc tính nội bộ `_raw_stream`. Thiếu thuộc tính thì giữ câu cũ, không sập.

## Đề xuất

- Chuyển Soi Lỗi rồi Lá Chắn (S2, W4 mục 2.7). Phần đáng soi nhất là cơ chế mới của `ignoring_custom_headers` và 4 test đã đổi dòng kiểm.
- Ngoài phạm vi, không sửa: `uv run ruff format --check .` báo 7 file chưa định dạng, có sẵn từ trước (ví dụ `app/views/settings.py`). Dự án không bắt buộc chạy `ruff format`.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-16)

Theo báo cáo Soi Lỗi `docs/team/reports/T-034-soi-loi.md` (đạt có điều kiện).

| Mã | Cách sửa | Commit |
|---|---|---|
| SL-T034-2 (bảo mật) | `ignoring_custom_headers`: không nhập được `anthropic._client` / `openai._client` thì thử nhập gói gốc (`anthropic`, `openai`). Gói nhập được (thư viện còn cài nhưng đổi cấu trúc) thì bật đường dự phòng, tức là gỡ biến tạm thời như cách cũ. Chỉ bỏ qua khi chính gói chưa cài, vì khi đó không có client nào của gói được tạo. | `seo_app/ai/base.py` |
| SL-T034-1 | Trong `_VERSION`, mỗi phần (số hoặc biến thể) được kèm đuôi nối bằng gạch `(?:-[^\W_]+(?:\.\d+)*)*` trước phần nhìn trước. "Gemini 2.5 Flash-Lite", "Opus 5.5-preview", "Pro-002" đều bị che. Số đứng riêng vẫn giữ: "dày 5.5-6 mm", "cửa pro-max" không có tên hãng đứng trước nên không bị đụng. | `seo_app/content/blind_test.py` |

Test đã bỏ `xfail` (trong `tests/test_soi_loi_t034.py`):
- `test_library_without_client_module_falls_back` (2 trường hợp, SL-T034-2)
- `test_hyphenated_variant_after_version_is_masked` (3 trường hợp, SL-T034-1)

### Câu lỗi người dùng thấy (để Thư Ký đối chiếu README mục 7.6)

T-034 **không đổi chữ** câu lỗi khi Claude bị cắt ở trang Soạn bài. Câu vẫn là:

> AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt vì quá giới hạn … token). Bấm thử lại; nếu vẫn lỗi, tăng max_tokens của việc «…» trong config/ai.toml.

Dòng này ở README 7.6 **vẫn đúng** cho Soạn bài. Chỗ đổi là **lớp lỗi**: khi luồng báo chắc chắn bị cắt (`stop_reason = max_tokens`), lỗi là `TokenLimitError`. Nhờ vậy ở **thử mù**, ứng viên Claude bị cắt giờ hiện câu sau (giống ChatGPT, Gemini), thay cho câu trên:

> Bài thử dài quá giới hạn 2000 token của phần thử mù (mô hình suy nghĩ càng kỹ càng dùng nhiều phần giới hạn này). Chọn effort thấp hơn (low hoặc medium) cho ứng viên này rồi chạy lại.

README đã có dòng "Ở thử mù: «Bài thử dài quá giới hạn 2000 token…»". Đề xuất Thư Ký: ở dòng "(Claude)" thêm ghi chú "ở trang Soạn bài". Không cần dòng mới.

Câu khác T-034 làm người dùng gặp, kiểm với README 7.6:

| Tình huống | Câu | README |
|---|---|---|
| Nội dung nén gzip/br hỏng (Anthropic, OpenAI, cả nút Kiểm tra) | "Máy chủ … trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy). Kiểm tra mạng rồi thử lại." Trước đây là "Không kết nối được tới …". | Đã có dòng (189). Không cần sửa. |
| Tên mô hình ở thử mù có ký tự lạ | "Ứng viên …: tên mô hình chỉ gồm chữ không dấu, số và các dấu . _ : / @ -, ví dụ claude-opus-5-5, gpt-6.1, gemini-3-pro." | Chưa có. Câu tự giải thích, có thể không cần thêm. |
| Thiếu `config/ai.toml` | "Không thấy file cấu hình AI: config/ai.toml." (trước ghi đường dẫn đầy đủ) | Chưa có. Có thể thêm: "Tải lại phần mềm từ GitHub hoặc chép lại file `config/ai.toml`." |

### Bằng chứng lượt 2

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q
KET_QUA_PYTEST_L2

# Chạy riêng tests/test_soi_loi_t028.py 30 lần
KET_QUA_30_LAN_L2
```

# Báo cáo T-028 · Máy chủ AI trả mã 200 nhưng nội dung hỏng: báo lỗi tiếng Việt, không hiện traceback

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-028](../tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Khi Wi-Fi công cộng, proxy công ty hay máy chủ AI trục trặc trả về một trang lạ thay cho câu trả lời, trang
Soạn bài và nút Kiểm tra khóa giờ hiện câu "Máy chủ … trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy).
Kiểm tra mạng rồi thử lại." thay vì một khối lỗi tiếng Anh khó hiểu. Mạng đứt giữa lúc Claude đang viết thì
báo "Mất kết nối … giữa chừng". Bài Claude bị cắt vì quá giới hạn độ dài cũng có câu hướng dẫn riêng (trước
đây cũng ra lỗi thô). App cũng không còn nhận các biến môi trường lạ có thể chèn thêm thông tin vào mọi lời
gọi AI, nhưng vẫn đi qua proxy của mạng công ty như cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | Thêm `is_bad_response` (lỗi nảy ra khi thư viện **đang đọc** trả lời), `network_error_kind` (lỗi mạng httpx/httpx2), `unreadable_error`, câu cố định `bad_response_message` / `connection_lost_message`; `ignoring_custom_headers` tạm ẩn `ANTHROPIC_CUSTOM_HEADERS`, `OPENAI_CUSTOM_HEADERS` khi tạo client (`base.py:96-209`). |
| `seo_app/ai/anthropic_provider.py` | Tạo client trong `ignoring_custom_headers`; `generate` đổi lỗi đọc trả lời hỏng / mạng đứt giữa luồng sang `AIError`; `ValidationError` lúc ghép luồng (bài bị cắt vì `max_tokens`) có câu riêng; lỗi lúc gọi thư viện vẫn ra câu "uv sync". |
| `seo_app/ai/openai_provider.py` | Như trên cho `generate`; `_parse` chịu được JSON sai kiểu (`"output": 5`) thay vì ném `TypeError` thành câu "uv sync". |
| `seo_app/ai/gemini_provider.py` | `BAD_RESPONSE` dùng chung mẫu câu (chữ không đổi); `no_debug_config()` tắt chế độ ghi/phát lại qua biến `GOOGLE_GENAI_CLIENT_MODE`… |
| `seo_app/env_file.py` | Nút Kiểm tra: `_other_result` (dữ liệu lạ / "uv sync" / tên lỗi), `_listing_ok` (danh sách mô hình sai dạng là dữ liệu lạ), bỏ qua `*_CUSTOM_HEADERS`, Gemini tắt ghi/phát lại. |
| `tests/test_ai_t028.py` | Mới, 226 trường hợp (xem dưới). |
| `tests/test_soi_loi_t026.py` | Chỉ bỏ dấu `xfail` của `test_garbage_200_gives_vietnamese_error` (SL-T026-4, 4 trường hợp). Không sửa gì khác. |

### Cách phân biệt "dữ liệu hỏng" với "thư viện lệch phiên bản"

Cả hai đều ra `TypeError`/`AttributeError`/`KeyError`, nên không thể phân biệt theo loại lỗi. Tôi xét **chỗ
lỗi nảy ra** (traceback):

- Lỗi nảy ra bên trong hàm đọc trả lời của thư viện hãng, chỉ chạy sau khi đã nhận mã 2xx:
  `_process_response` (anthropic, openai: đọc JSON), `__stream__` / `accumulate_event` (đọc luồng SSE),
  `_from_response`, `…_from_mldev`, `…_from_vertex` (google-genai), hoặc trong `anthropic.types` /
  `openai.types` (thuộc tính tính từ dữ liệu máy chủ) → **dữ liệu lạ**.
- `JSONDecodeError`, `UnicodeDecodeError`, `AssertionError` nảy ra ở bất kỳ đâu trong code thư viện hãng →
  **dữ liệu lạ** (thư viện chỉ ném chúng khi đọc dữ liệu).
- Lỗi nảy ra lúc **gọi** thư viện (đổi tên tham số, mất hàm, mất thuộc tính) không đi qua các hàm trên → vẫn
  câu **"uv sync"** như T-026.
- Lỗi từ client giả (file test) hay code của app → giữ cách báo cũ.

Tên hàm lấy từ mã nguồn thư viện trong `.venv` (anthropic 1.13.0, openai 3.31.0, google-genai 2.30.1).

### Mục 3: biến môi trường

Đọc mã nguồn thư viện:

- `anthropic/_client.py:244` và `openai/_client.py:317`: đọc `*_CUSTOM_HEADERS` **chỉ trong `__init__`**,
  tách theo dòng `Tên: giá trị`, gộp vào header mặc định của mọi lời gọi. OpenAI còn nhận cả dòng
  `Authorization:` (`openai/_client.py:325-331`). Không có tham số nào để tắt, và tham số `default_headers`
  chỉ ghi đè được header trùng tên. Cách tắt đúng: ẩn biến trong lúc tạo client. `ignoring_custom_headers`
  làm việc này dưới một khóa (2 trang tạo client cùng lúc không trả biến về sai), rồi trả lại như cũ (phần
  còn lại của máy không bị đụng). Tham số truyền vào `anthropic.Anthropic`/`openai.OpenAI` **không đổi**.
- google-genai **không** có biến chèn header. Biến "tương tự" (đổi cách gọi mạng) là
  `GOOGLE_GENAI_CLIENT_MODE` / `GOOGLE_GENAI_REPLAYS_DIRECTORY` / `GOOGLE_GENAI_REPLAY_ID`
  (`google/genai/client.py:274-287`, `:460-473`): chế độ `record` ghi lời gọi (kèm bài viết) ra thư mục,
  `replay` lấy câu trả lời từ file thay vì máy chủ. Tắt bằng `debug_config=DebugConfig(None, None, None)`
  (tham số công khai của `genai.Client`). `GOOGLE_GENAI_USE_VERTEXAI`/`…_ENTERPRISE` vốn đã không có tác dụng
  vì app truyền `vertexai=False` (`google/genai/_api_client.py:672-698`).
- **Giữ nguyên** `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY`, `NO_PROXY`, `SSL_CERT_FILE`, `SSL_CERT_DIR`: không
  đụng tới. Test `test_proxy_env_still_used_by_provider_clients` xác nhận client vẫn đi qua proxy khai báo,
  `test_ignoring_custom_headers_keeps_proxy_and_certificates` xác nhận các biến này còn nguyên trong lúc ẩn.

## Bằng chứng

Dựng lại lỗi trước khi sửa (thư viện thật, mạng giả, trên `396656b`):

```
anthropic  generate  html/json-thuong/json-hong/rỗng  → AssertionError thô
anthropic  generate  sse-hong                          → JSONDecodeError thô
anthropic  generate  bài bị cắt vì max_tokens          → pydantic ValidationError thô
anthropic  generate  luồng thiếu message_start         → RuntimeError thô
anthropic  generate  mạng đứt giữa luồng               → httpx2.ReadError thô
openai     generate  json-hong / utf-8 hỏng            → JSONDecodeError / UnicodeDecodeError thô
anthropic/openai  Kiểm tra  html, rỗng, json-null…    → câu "uv sync" (sai)
3 hãng     Kiểm tra  json-hong                         → "Lỗi khi kiểm tra khóa (JSONDecodeError)."
3 hãng     Kiểm tra  {"x": 1}, Gemini rỗng/null         → "Khóa … dùng được." (sai)
```

Sau khi sửa: mọi dạng trên ra câu cố định (test `test_generate_garbage_200_gives_fixed_vietnamese_error`,
`test_check_garbage_200_gives_fixed_vietnamese_message`, `test_anthropic_cut_at_max_tokens_is_explained`,
`test_anthropic_broken_stream_is_strange_data`, `test_anthropic_network_failure_mid_stream`).

```
$ uv run pytest -q
FAILED tests/test_soi_loi_t027.py::test_fallback_socketpair_ipv4_works_in_tests
FAILED tests/test_soi_loi_t027.py::test_ipv6_connect_still_blocked[::1] - OSE...
FAILED tests/test_soi_loi_t027.py::test_ipv6_connect_still_blocked[2606:2800:21f:cb07:6820:80da:af6b:8b2c]
FAILED tests/test_soi_loi_t027.py::test_other_thread_inside_socketpair_does_not_open_this_thread
FAILED tests/test_soi_loi_t027.py::test_inside_socketpair_only_its_own_listener_is_allowed[address0]
FAILED tests/test_soi_loi_t027.py::test_inside_socketpair_only_its_own_listener_is_allowed[address1]
FAILED tests/test_soi_loi_t027.py::test_inside_socketpair_only_its_own_listener_is_allowed[127.0.0.1]
FAILED tests/test_soi_loi_t027.py::test_inside_socketpair_only_its_own_listener_is_allowed[address3]
FAILED tests/test_soi_loi_t027.py::test_inside_socketpair_other_loopback_listener_is_blocked
9 failed, 2947 passed, 2 skipped, 5 xfailed in 133.05s (0:02:13)

$ uv run pytest -q tests/test_ai_t028.py
226 passed in 3.85s

$ uv run ruff check .
All checks passed!
```

9 test hỏng đều trong `tests/test_soi_loi_t027.py` (Linux thiếu `socket._fallback_socketpair`, máy không có
IPv6), có sẵn trên `main`, do T-030 đang sửa; T-028 không đụng tới. 5 xfail: 2 của SL-T026-3 (ngoài phạm vi)
và 3 test cũ ngoài phạm vi. Chưa chạy được trên Windows (máy cloud là Linux); code mới không dùng gì riêng
của hệ điều hành (traceback, `os.environ`, `threading.Lock`).

## Đối chiếu tiêu chí xong

- [x] Các test SL-T026-4 bỏ `xfail` và qua: `tests/test_soi_loi_t026.py::test_garbage_200_gives_vietnamese_error`
  (4 trường hợp: `anthropic-html`, `anthropic-json-thuong`, `anthropic-sse-hong`, `openai-json-hong`). Chỉ bỏ
  đúng 4 dòng của dấu `xfail` đó (`git diff 396656b -- tests/test_soi_loi_t026.py`).
- [x] Có test mới cho cả 3 hãng: `tests/test_ai_t028.py`, 3 hãng × 11 dạng trả lời hỏng, cả `generate` lẫn
  nút Kiểm tra; câu báo không chứa chữ máy chủ, khóa, `<`, `{`, "Error", "uv sync".
- [x] Không bắt nhầm sang câu "uv sync": `test_*_library_error_before_response_is_still_library`,
  `test_anthropic_real_client_rejecting_argument_is_library`, `test_errors_while_calling_library_are_not_bad_response`;
  toàn bộ test "uv sync" của T-026 vẫn qua.
- [x] Mục 3: `test_generate_ignores_custom_headers_env`, `test_check_ignores_custom_headers_env` (header lạ và
  `Authorization` lạ không lọt, khóa thật vẫn được gửi), `test_libraries_would_add_custom_headers_without_fix`
  (chứng minh biến có tác dụng nếu không chặn), `test_gemini_ignores_replay_env`,
  `test_check_gemini_ignores_replay_env`, proxy/chứng chỉ giữ nguyên.
- [x] Test dùng mạng giả (`MockTransport`), không gọi mạng thật.
- [x] `uv run pytest`: không hỏng gì ngoài 9 test của T-030; `uv run ruff check .` sạch.
- [x] Báo cáo nộp tại đây.

## Rủi ro và điểm cần chú ý

1. **Nhận diện theo tên hàm trong thư viện.** Bản thư viện sau đổi tên `_process_response`, `__stream__`…
   thì lỗi kiểu `TypeError` khi đọc dữ liệu hỏng lại rơi về câu "uv sync" (như trước T-028); `JSONDecodeError`,
   `AssertionError`, `UnicodeDecodeError` vẫn nhận đúng. Hậu quả chỉ là câu gợi ý sai hướng, không lộ gì,
   không sập trang. Có test khóa danh sách tên với thư viện thật (`test_check_garbage_*`, `test_generate_garbage_*`):
   nâng thư viện mà tên đổi thì test đỏ ngay.
2. **Ngược lại**, lỗi lệch phiên bản nảy ra *bên trong* hàm đọc trả lời (thư viện tự mâu thuẫn với chính nó)
   sẽ ra "dữ liệu lạ" thay vì "uv sync". Khó xảy ra vì các hàm này chỉ dùng code của cùng thư viện.
3. **Anthropic, message thiếu trường sau khi đọc xong luồng:** lỗi nảy ra khi app đọc `message.stop_reason`
   trên kiểu `SimpleNamespace`/kiểu lạ vẫn là "uv sync" (giữ test LC-2 của T-026: `mat-parsed_output`,
   `mat-stop_reason`). Trên kiểu thật của thư viện thì nảy ra trong `anthropic.types` → "dữ liệu lạ"
   (`test_anthropic_broken_stream_is_strange_data[message-rong]`).
4. **Kiểm tra khóa Gemini:** danh sách mô hình rỗng giờ là "dữ liệu lạ" (google-genai đổi trường `models` bị
   thiếu thành danh sách rỗng, nên không phân biệt được). Khóa đúng luôn thấy ít nhất 1 mô hình, nhưng nếu
   Google có lúc trả trang đầu rỗng thì người dùng thấy "dữ liệu lạ" thay vì "Khóa dùng được" (viết bài vẫn
   chạy bình thường). Anthropic/OpenAI: danh sách rỗng đúng dạng vẫn là "dùng được".
5. **`ignoring_custom_headers` đụng `os.environ` trong chốc lát** (dưới khóa, rồi trả lại). Trong khoảnh khắc
   đó, một luồng khác của app đọc đúng 2 biến này sẽ không thấy chúng; app không đọc chúng ở đâu khác.
   Không đụng biến nào khác. Lá Chắn xem có muốn đổi sang "xóa hẳn khỏi tiến trình" hay không.
6. **Bài Claude bị cắt vì max_tokens**: thư viện ném lỗi trước khi biết lý do dừng, nên câu báo nói "có thể bị
   cắt" kèm hướng dẫn tăng `max_tokens`, không khẳng định chắc.
7. Lỗi bị đổi câu vẫn giữ ở `__cause__` (để gỡ lỗi), app không ghi ra đâu (như T-026).

## Đề xuất

- **Soi Lỗi:** thử thêm luồng SSE hỏng ở các vị trí khác (`content_block_delta` sai kiểu, `index` lệch,
  `message_delta` thiếu `usage`), nội dung nén `gzip`/`br` hỏng, `content-type` lạ, và lỗi lệch phiên bản
  nảy ra sâu trong thư viện (monkeypatch một hàm nội bộ ném `TypeError`) để xem có bị nhận nhầm là "dữ liệu lạ".
- **Lá Chắn:** soát S2 cho các câu mới (đều cố định, chỉ ghép tên hãng viết sẵn và `task.max_tokens`/`task.name`
  từ `config/ai.toml`); cách ẩn biến trong `ignoring_custom_headers` (khóa, trả lại, không đụng proxy/SSL);
  `no_debug_config` (tắt record/replay).
- **Ghi nhận, ngoài phạm vi:** luồng Anthropic có sự kiện `error` trong mã 200 (ví dụ `overloaded_error` giữa
  chừng) đang ra câu "Anthropic báo lỗi 200. Thử lại sau ít phút." (có sẵn trên `main`, câu cố định, không lộ
  gì, chỉ hơi khó hiểu). Có thể sửa thành "Anthropic đang quá tải giữa chừng" ở phiếu sau nếu Chỉ Huy muốn.
- **SL-T026-3** (Gemini JSON sai kiểu ra "uv sync"): cùng cơ chế `is_bad_response` có thể sửa được (lỗi nảy ra
  trong `…_from_mldev`), nhưng tôi **không** áp vào `generate` của Gemini vì Chỉ Huy đã chấp nhận và để
  `xfail(strict=True)`. Nếu Chỉ Huy muốn sửa luôn thì là thay đổi nhỏ trong `gemini_provider.py`.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (sửa SL-T028-2 theo Soi Lỗi, 2026-10-15)

Gộp `origin/team/T-028` (`d0f82ce`, báo cáo và test của Soi Lỗi) trước khi sửa: fast-forward, không xung đột.

### Đã sửa

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | `IGNORED_ENV` thêm `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`. Dùng chung cho mọi chỗ tạo client (viết bài và nút Kiểm tra khóa), nên không phải sửa chỗ khác. |
| `tests/test_ai_t028.py` | 4 test mới: `test_ignored_env_covers_org_and_project` (danh sách có 2 biến mới, không có biến proxy/chứng chỉ), `test_openai_would_send_org_and_project_without_fix` (chứng minh thư viện gửi 2 header này nếu không bỏ qua), `test_generate_ignores_openai_org_and_project_env`, `test_check_ignores_openai_org_and_project_env` (không có header `OpenAI-Organization`/`OpenAI-Project`, khóa của app vẫn được gửi, biến được trả lại). |
| `tests/test_soi_loi_t028.py` | Chỉ bỏ dấu `xfail` của `test_openai_org_and_project_env_ignored` (SL-T028-2). Không đụng SL-T028-1, SL-T028-3. |

### Đã tra mã nguồn thư viện (`.venv`)

- **openai 3.31.0**: `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID` (`_client.py:281-286`) thành header
  `OpenAI-Organization`/`OpenAI-Project` (`:659-660`) ở mọi lời gọi → đã bỏ qua. `OPENAI_ADMIN_KEY`
  (`:264-266`) chỉ gửi ở lời gọi quản trị (`admin_api_key_auth`, `resources/admin/…`), và khóa của app được ưu
  tiên (`setdefault`, `:619-625`) → không cần. `OPENAI_WEBHOOK_SECRET` không gửi đi.
- **anthropic 1.13.0**: `ANTHROPIC_AUTH_TOKEN` và tự dò thông tin đăng nhập (profile, federation) chỉ chạy khi
  không truyền `api_key` (`_client.py:218-226`, `:100-109`); app luôn truyền → không cần. Không có biến
  tổ chức/dự án.
- **google-genai 2.30.1**: không có biến header; `GOOGLE_CLOUD_PROJECT`/`LOCATION` chỉ dùng khi Vertex, app
  truyền `vertexai=False`; chế độ ghi/phát lại đã tắt ở lượt 1.
- **Giữ nguyên** `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY`, `SSL_CERT_FILE`, `SSL_CERT_DIR`.

### Bằng chứng lượt 2

```
$ uv run pytest -q tests/test_ai_t028.py tests/test_soi_loi_t028.py tests/test_ai_t026.py tests/test_soi_loi_t026.py
710 passed, 6 xfailed, 1 warning
  (6 xfail: 2 SL-T026-3, 2 SL-T028-1, 2 SL-T028-3; cảnh báo pydantic đến từ test cũ, không từ test_ai_t028.py)

$ uv run ruff check .
All checks passed!

$ uv run pytest -q
9 failed, 3069 passed, 2 skipped, 9 xfailed, 1 warning in 157.93s
  (9 hỏng đều trong tests/test_soi_loi_t027.py, có sẵn trên main, của T-030; 9 xfail = 6 nêu trên + 3 test cũ
  ngoài phạm vi)
```

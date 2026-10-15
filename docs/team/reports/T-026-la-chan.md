# Biên bản bảo mật T-026 · Sửa 4 lỗi mức Thấp của lớp AI

> **Model:** lượt này chạy **tạm bằng Opus 5.5** (Fable 5.1 bị giới hạn tới 01/11), chủ dự án đã duyệt
> cách này. Sau 01/11 cần kiểm lại bằng Fable.
> Kiểm **từ đầu**: Lá Chắn trước (do Chỉ Huy A giao) dừng khi mới đọc, chưa có biên bản.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, thay Fable 5.1) |
| Phiếu được kiểm | [T-026](../tickets/T-026-loi-thap-lop-ai.md) |
| Phạm vi | Diff riêng T-026: `git diff ed0324e c906285` (trước merge `main`) và `git diff e4107f2 ac9fbda` (sau merge `3366566`). Kiểm trên nhánh `team/T-026` tại `2c63a14` (= `ac9fbda` + merge tài liệu điều phối từ `main`; `git diff ac9fbda HEAD -- seo_app app` rỗng). File code: `seo_app/ai/base.py`, `registry.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`. |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Phiếu này an toàn để gộp vào `main`. Khi máy chủ AI từ chối yêu cầu, app giờ chỉ hiện một câu tiếng
Việt viết sẵn, không còn chép chữ nào của máy chủ (nên không thể lộ khóa hay hiện link lạ). Cả 3 hãng,
kể cả nút **Kiểm tra** khóa, luôn gọi đúng máy chủ chính thức; phần mềm khác trên máy không đổi được
địa chỉ này. Tôi không tìm thấy lỗi Nghiêm trọng, Cao hay Trung bình. Có 2 ghi nhận mức Thấp, không cần
sửa trong phiếu này (xem bảng dưới).

## Lỗi phát hiện

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình. Hai ghi nhận mức Thấp:

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T026-1 | Thấp (ghi nhận) | Bắt rộng `ImportError/AttributeError/TypeError/KeyError` quanh toàn bộ `_generate` làm lỗi code của chính app cũng hiện câu "uv sync". | `seo_app/ai/base.py:61`, `anthropic_provider.py:39`, `openai_provider.py:60`, `gemini_provider.py:125` | Lỗi lập trình trong `_generate` → `AIError` câu "uv sync" (lỗi gốc chỉ nằm ở `__cause__`, app không ghi log). **Không phải lỗ hổng:** luôn kết thúc bằng lỗi (không biến lỗi thành thành công), câu báo cố định, không gọi lại mạng. Chỉ làm khó gỡ lỗi. | Không bắt buộc. Nếu sau này thêm log `__cause__` thì chỉ ghi tên lớp và vị trí, **không ghi nội dung lỗi** (có thể chứa khóa/URL). |
| LC-T026-2 | Thấp (ghi nhận) | Thư viện AI vẫn đọc `HTTPS_PROXY`/`HTTP_PROXY`, `SSL_CERT_FILE`/`SSL_CERT_DIR`, `OPENAI_CUSTOM_HEADERS`, `ANTHROPIC_CUSTOM_HEADERS` từ biến môi trường. | thư viện: `anthropic/_client.py:244`, `openai/_client.py:317`, `google/genai/_api_client.py:1135`, `:1188` | Muốn lợi dụng phải đặt được biến môi trường của tài khoản người dùng, tức là đã vào được máy (khi đó đọc thẳng `.env` còn dễ hơn). Proxy chỉ thấy tên máy chủ, không đọc được nội dung vì SSL vẫn kiểm (trừ khi cài thêm chứng chỉ gốc, cũng cần quyền trên máy). `*_CUSTOM_HEADERS` chỉ thêm header vào lời gọi tới **máy chủ chính thức**, không đổi được địa chỉ. Xem đánh giá chi tiết ở mục "Đánh giá thêm". | Không lập phiếu riêng. **Không chặn proxy/SSL** (mạng công ty cần). Tùy chọn: khi làm T-028, bỏ qua `*_CUSTOM_HEADERS` (app không dùng tới). |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff chỉ có khóa giả trong test (`tests/test_ai_t026.py:41-44`, `tests/test_soi_loi_t026.py:35-38`, `:653-657`, đều có chữ `KhoaGia`). Soát lịch sử git toàn bộ nhánh: chuỗi dạng `sk-ant-`/`sk-proj-`/`AIza` đều là khóa giả (`…BIMAT_KHONG_DUOC_IN`, `…ThuNghiemKhongPhaiKhoaThat`…). Không có `.env`, file service account hay `.sqlite` từng được commit. |
| S2 | Đạt | **Lỗi 400:** `bad_request_error` (`base.py:118-141`) chỉ ghép tên hãng (cố định trong code), `task.model`/`task.name` (từ `config/ai.toml`, không từ máy chủ), gợi ý viết sẵn, và mã/tham số qua `safe_code`. Gọi ở `anthropic_provider.py:81` (`error.type`), `openai_provider.py:110` (`code`, `param`), `gemini_provider.py:234` (`status`). Câu máy chủ ở Gemini chỉ dùng để **nhận ra** lỗi đã biết (`KNOWN_400_HINTS`, `gemini_provider.py:83`), câu hiện lên viết sẵn. **`safe_code`** (`base.py:82-115`): chỉ `[A-Za-z]` nối `_`/`.`, ≤ 40 ký tự → không có số (khóa thật luôn có số/dấu `-`), không `:`/`/`/`@` (nên không thành `http(s)://`, email, `:red[…]` hay `:material/…:` của Streamlit), không `[]()<>`. Dạng `www.` (cách duy nhất GFM tự tạo link với bộ ký tự này) bị loại sau khi đổi chữ thường (`base.py:96-100`). Tôi tự chạy lại: `www.evil.com`, `WWW.X`, `a_www.b`, `evil.com`, `sk-ant-x`, `key=abc`, chuỗi 41 ký tự, `[a](b)`, ZWSP → đều `None`; `invalid_value`, `INVALID_ARGUMENT`, `reasoning.effort` giữ. `evil.ru` được giữ nhưng là chữ trơn (GFM không tự tạo link cho tên miền không có `www.`). **Các câu lỗi khác** của 3 provider đều cố định hoặc chỉ nêu mã HTTP/tên lớp lỗi (đã soát hết `raise AIError` trong 3 file). **Nút Kiểm tra:** mọi nhánh mới trả `_library_result` (câu cố định) hoặc tên lớp lỗi, qua `_result` → `redact_secrets` (`env_file.py:309`, `:316-319`, `:366-371`, `:405-410`, `:455-460`). Hiển thị: `app/views/write.py:380` (`st.error`, không `unsafe_allow_html`). |
| S3 | Không áp dụng | Không có biến cấu hình mới; `git diff ed0324e ac9fbda -- .env.example` rỗng. |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` hay đường đăng bài. |
| W2 | Không áp dụng | Như trên. |
| W3 | Không áp dụng | Như trên. |
| W4 | Đạt | **Đủ 6 chỗ tạo client** có `base_url` chính thức `https` cố định (`base.py:55-57`): `anthropic_provider.py:33`, `openai_provider.py:54`, `gemini_provider.py:118`, `env_file.py:344`, `:384`, `:429`. Đã grep cả `seo_app app scripts`: không còn chỗ tạo client AI nào khác. **Đã đọc mã thư viện** để chắc biến môi trường không còn tác dụng khi truyền `base_url`: `anthropic/_client.py:234-242` (kwarg > `ANTHROPIC_BASE_URL` > profile; profile chỉ điền khi `base_url` không rõ; truyền `api_key` thì không đọc `ANTHROPIC_AUTH_TOKEN`/profile, `:216-226`), `openai/_client.py:307-309` (chỉ đọc `OPENAI_BASE_URL` khi `base_url is None`), `google/genai/_base_url.py:44-50` (`HttpOptions.base_url` thắng `GOOGLE_GEMINI_BASE_URL`), `vertexai=False` rõ ràng nên `GOOGLE_GENAI_USE_VERTEXAI` không có tác dụng. Tôi tự chạy với 4 biến `*_BASE_URL=https://evil.example/` + `GOOGLE_GENAI_USE_VERTEXAI=true`: 3 client vẫn là `https://api.anthropic.com`, `https://api.openai.com/v1/`, `https://generativelanguage.googleapis.com/`, Gemini `vertexai=False`. Test của Soi Lỗi/Thợ Máy ghi lại địa chỉ **thật** qua `MockTransport` cho cả `generate` và `check_api_key`. SSL: không chỗ nào tắt `verify`. Timeout: giữ như cũ (`TIMEOUT_SECONDS`, `TIMEOUT_MS`, `timeout` của nút Kiểm tra). |
| A1 | Đạt | Đường Gemini 2 lượt vẫn bọc ghi chép tìm web bằng `_frame` → khung `du_lieu_tham_khao` (`gemini_provider.py:142`, `:207-211`). Không đổi prompt nào khác. |
| A2 | Đạt | Công cụ duy nhất vẫn là tìm web: Gemini đổi sang dạng dict `[{"google_search": {}}]` (`gemini_provider.py:182`); tôi chạy thử thư viện: dựng ra đúng `Tool(google_search=GoogleSearch())`, không hàm Python nào nên không bật gọi hàm tự động. Soi Lỗi so nguyên JSON gửi đi giống hệt bản cũ (20 tổ hợp, `test_gemini_request_body_same_as_before`). Mọi nhánh lỗi mới kết thúc bằng `AIError`, không có đường nào biến lỗi thành kết quả hợp lệ. |
| A3 | Đạt | Không đổi nội dung gửi đi. OpenAI vẫn `store: False` (`openai_provider.py:74`). |
| U1 | Đạt | Không có `unsafe_allow_html` mới. Câu lỗi hiện bằng `st.error` (Markdown), nội dung cố định + mã đã lọc (xem S2). |
| U2 | Không áp dụng | Không đụng giao diện. `.streamlit/config.toml:5` vẫn `address = "localhost"`. |
| U3 | Không áp dụng | Không đụng đăng nhập. |
| F1 | Không áp dụng | Không đọc/ghi file mới. |
| F2 | Không áp dụng | Không xử lý ảnh. |
| F3 | Đạt | Không có `eval`, `pickle`, `yaml.load` mới; không đọc file mới. |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi (`git diff ed0324e ac9fbda -- uv.lock pyproject.toml` rỗng). pip-audit trên đúng danh sách thư viện của dự án: sạch. |
| D2 | Đạt | `.gitignore` không đổi; vẫn chặn `.env` (`:2-3`), `*service-account*.json` (`:5`), `*.sqlite` (`:23-24`). |
| D3 | Đạt | `tests/conftest.py:18` chặn socket mạng cho mọi test (autouse). Test mới dùng `httpx.MockTransport`/client giả. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uvx pip-audit -r <uv export>` (203 dòng, đúng thư viện của dự án): **No known vulnerabilities found**. (Chạy `uvx pip-audit` không tham số chỉ quét môi trường của chính công cụ, nên tôi quét lại bằng danh sách xuất từ `uv.lock`.) | Có |
| bandit | `uvx bandit -r seo_app app scripts`: 1 cảnh báo Low (B101 `assert`) ở `seo_app/storage/drafts.py:203`. Không có cảnh báo nào trong file của T-026. | Có, báo nhầm (xem dưới) |
| detect-secrets | `--all-files`: 99 kết quả trong file được git theo dõi, toàn ở `tests/` và `docs/team/reports/` (khóa giả, mẫu `user:pass@` trong test), và `seo_app/ai/base.py:22` (chú thích ví dụ `https://admin:matkhau@site…`). Phần trong `.venv/`, `.ruff_cache/` không thuộc repo. | Có, đều là dữ liệu giả |
| Soát lịch sử git | `git log -p` lọc `api_key|password|secret|token`; lọc riêng chuỗi dạng khóa thật `sk-ant-…`, `sk-proj-…`, `AIza…` trên `--all`: chỉ có khóa giả. Không file `.env`/service account/`.sqlite` nào trong lịch sử. | Có |
| pytest | `uv run pytest -q -rfE` (Linux): **9 failed, 2717 passed, 2 skipped, 9 xfailed**. 9 test hỏng **đều** ở `tests/test_soi_loi_t027.py` (thiếu `socket._fallback_socketpair` trên Python 3.12.3, máy không có IPv6). Chúng hỏng y vậy trên `main`, do phiếu T-030 đang sửa, **không do T-026**. Chạy riêng 5 file test liên quan T-026: **705 passed, 6 xfailed**. 9 xfail = 2 SL-T026-3, 4 SL-T026-4 (T-028), 3 test cũ ngoài phạm vi. | Có |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |

## Báo nhầm đã loại

- **bandit B101** `seo_app/storage/drafts.py:203`: không thuộc diff T-026; `assert` chỉ kiểm điều kiện nội bộ (`saved_at` vừa được gán), không phải kiểm tra bảo mật.
- **detect-secrets** "Secret Keyword", "Base64 High Entropy", "Basic Auth" trong test/báo cáo: khóa giả có chữ `KhoaGia`, `BIMAT_KHONG_DUOC_IN`…, hoặc ví dụ minh họa. `seo_app/ai/base.py:22` là chú thích ví dụ `admin:matkhau` cho bộ lọc `redact_secrets`.

## Trọng tâm được giao

### Bắt lỗi rộng có che lỗi bảo mật không

Không. Tôi xét từng nơi:

- `generate` 3 hãng (`anthropic_provider.py:36-41`, `openai_provider.py:57-63`, `gemini_provider.py:122-127`): bắt `LIBRARY_ERRORS` **bên ngoài** mọi nhánh `except` cũ, nên các lỗi đã có câu riêng (khóa sai, hết tiền, 400…) vẫn ra câu riêng (`AIError` không thuộc 4 loại bị bắt). Kết quả luôn là ném `AIError`, không trả dữ liệu, không gọi lại. Bộ lọc prompt (`_frame`) nếu hỏng thì lời gọi dừng, prompt không đi.
- `registry.make_provider` (`registry.py:96-107`): bắt thêm lúc tạo client; khóa không bị in (câu cố định `library_error(label)`).
- `env_file.check_api_key` (`env_file.py:307-314`) và 3 hàm `_check_*`: mọi nhánh mới trả trạng thái `unknown`, **không bao giờ** `ok`. Nhánh `except Exception` mới của Claude (`:368`) chỉ nêu tên lớp lỗi. Không còn đường nào trả "Khóa dùng được" khi có lỗi.
- Không có lỗi bảo mật nào của thư viện là 4 loại trên (lỗi SSL, kết nối, xác thực đều là lớp riêng của `httpx`/thư viện), nên không bị đổi thành câu "uv sync" sai lệch. Riêng lỗi SSL (`httpx.ConnectError`) vẫn ra "Không kết nối được…", kiểm tra chứng chỉ không bị tắt.

### SL-T026-3 (Chỉ Huy A chấp nhận): Gemini nhận JSON sai kiểu → câu "uv sync"

**Đồng ý chấp nhận, không ảnh hưởng bảo mật.** Đường đi: máy chủ/proxy trả mã 200 với JSON sai kiểu → google-genai ném `TypeError`/`AttributeError` khi đọc → câu "uv sync". Câu cố định, không chép dữ liệu, kết thúc bằng lỗi; địa chỉ máy chủ đã cố định (W4) nên nguồn duy nhất là máy chủ Google hoặc proxy/Wi-Fi chặn giữa đường. Hậu quả chỉ là gợi ý sai hướng (chạy `uv sync` vô hại vì chỉ cài theo `uv.lock`). Test `xfail(strict=True)` giữ dấu vết.

### SL-T026-4 → T-028

**Đồng ý.** Có sẵn trên `main` từ trước T-026 (Soi Lỗi đã chạy lại trên `git archive origin/main`). Thông điệp thô là `AssertionError` của thư viện Anthropic hoặc `json.JSONDecodeError` (vị trí ký tự trong dữ liệu máy chủ), không chứa khóa vì khóa đi trong header. Mức Thấp. T-028 khi sửa phải dùng câu cố định như `BAD_RESPONSE` của Gemini, **không chép** `str(exc)` (JSONDecodeError có thể kèm một đoạn dữ liệu máy chủ).

## Đánh giá thêm: proxy, chứng chỉ, header qua biến môi trường (LC-T026-2)

| Biến | Thư viện làm gì | Rủi ro thật | Đề xuất |
|---|---|---|---|
| `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY`, `NO_PROXY` | httpx `trust_env=True`: đi qua proxy bằng đường hầm `CONNECT` | Proxy chỉ thấy tên máy chủ (`api.openai.com`…), không đọc được khóa hay bài vì SSL vẫn kiểm đầu-cuối | **Giữ.** Mạng công ty có thể bắt buộc proxy; chặn sẽ làm app không gọi được AI. |
| `SSL_CERT_FILE`, `SSL_CERT_DIR` | Đổi kho chứng chỉ gốc (google-genai đọc rõ ở `_api_client.py:1188`) | Kết hợp với proxy, ai đặt được biến này + cài chứng chỉ gốc thì đọc được nội dung. Nhưng phải có quyền trên tài khoản máy, khi đó đọc thẳng `.env` dễ hơn. Mạng công ty có kiểm tra SSL cũng cần đúng cơ chế này. | **Giữ.** Không phải đường tấn công thực tế. |
| `OPENAI_CUSTOM_HEADERS`, `ANTHROPIC_CUSTOM_HEADERS` | Thêm header vào mọi lời gọi | Chỉ tới máy chủ chính thức (địa chỉ đã cố định), cần quyền trên máy để đặt. OpenAI đã `store: False` nên không có nội dung lưu trên tài khoản khác. App không cần tính năng này. | Không cần phiếu riêng. Nếu tiện, gom vào T-028: bỏ qua 2 biến này khi tạo client. |

Kết luận: **không lập phiếu riêng**. Đề nghị Chỉ Huy hỏi chủ dự án có muốn ghi vào sổ rủi ro (`security.md` mục 6) dòng "App dùng proxy và chứng chỉ của hệ thống (biến môi trường) để chạy được trên mạng công ty" hay không; chỉ chủ dự án được ghi sổ.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có. Kết luận **ĐẠT**: được gộp `team/T-026` vào `main`. Nhắc lại việc theo sau (không phải điều kiện):

- T-028: sửa SL-T026-4 bằng câu cố định; tùy chọn bỏ qua `*_CUSTOM_HEADERS`.
- Sau 01/11: kiểm lại biên bản này bằng Fable 5.1.

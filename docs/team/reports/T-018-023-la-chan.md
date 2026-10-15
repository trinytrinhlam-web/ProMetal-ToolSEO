# Biên bản bảo mật T-018 + T-023 · ChatGPT/Gemini và nút Kiểm tra khóa

> **Ghi chú về model:** lần kiểm định này chạy **tạm bằng Claude Opus 5.5**, không phải Fable 5.1
> như hồ sơ vai yêu cầu, vì Fable 5.1 bị giới hạn tới 01/11/2026. Chủ dự án đã duyệt cách này.
> **Sau 01/11 phải kiểm lại bằng Fable** (Chỉ Huy giữ việc này trên bảng việc).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thời, xem ghi chú trên) |
| Phiếu được kiểm | [T-018](../tickets/T-018-them-openai-gemini.md), [T-023](../tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) |
| Phạm vi | Nhánh `team/T-023`, diff `db5ad0f..d76ad80` (`git diff origin/main...HEAD`: 19 file, gồm cả `team/T-018` đã gộp vào) |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT** (không có lỗi Nghiêm trọng, Cao hay Trung bình; 4 lỗi Thấp, khuyến nghị gom vào một phiếu sau) |

## Tóm tắt (cho chủ dự án)

Thêm ChatGPT và Gemini **an toàn để gộp vào `main`**. Khóa API không lộ ra màn hình, thông báo
lỗi, nhật ký hay địa chỉ web: Gemini gửi khóa trong phần đầu thư (header), không nằm trong địa
chỉ; mọi câu báo lỗi đều được che khóa; nút **Kiểm tra** chỉ hiện câu cố định. AI chỉ có một
công cụ là tìm web, không có cách nào tự đăng bài hay đọc file trên máy. Hai thư viện mới (và 10
thư viện đi kèm) đều lấy từ kho chính thức PyPI, chưa có lỗ hổng nào được biết.

Còn 4 điểm nhỏ (mức Thấp), chỉ xảy ra khi thư viện bị nâng sai phiên bản hoặc máy chủ AI tự
chép khóa vào câu báo lỗi, nên không chặn. Nên sửa trong một phiếu nhỏ trước khi hết Giai đoạn 2.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-1 (= SL-3) | Thấp | `text_format(schema)` chạy khi dựng `params`, nằm ngoài khối `try` | `seo_app/ai/openai_provider.py:52`, `:105` | Thư viện `openai` bị nâng ngoài `uv.lock` và đổi/bỏ `openai.pydantic_function_tool` → `AttributeError` thô → `ai_call` (`app/views/write.py:379`) chỉ bắt `AIError` → Streamlit hiện traceback. **Không lộ khóa**: thông điệp chỉ là "module 'openai' has no attribute …"; Streamlit không in biến cục bộ. Khó xảy ra: `run.bat`/`run.command` chạy `uv sync` theo `uv.lock`. Đã tái hiện bằng test `xfail(strict)` của Soi Lỗi. | Dời `text_format(schema)` vào trong `try`, hoặc bắt `(AttributeError, TypeError, KeyError)` quanh nó → `AIError` câu "uv sync" như `registry.py`. Bỏ `xfail` của `test_openai_public_helper_change_gives_vietnamese_error`. |
| LC-2 (= SL-4) | Thấp | `make_provider` chỉ bắt `ImportError` lúc nhập module hãng | `seo_app/ai/registry.py:96-103` | `google-genai` bị nâng ngoài `uv.lock`, đổi tên một hằng dùng lúc nhập (`types.ThinkingLevel`, `FinishReason.*`, `HttpRetryOptions` ở `gemini_provider.py:43-65`) → `AttributeError` thô → `build_writer` sập trang Soạn bài. Không lộ khóa (khóa chưa được dùng lúc nhập). Khó xảy ra như LC-1. | Bắt `(ImportError, AttributeError)` ở `registry.py:103`. Bỏ `xfail` của `test_gemini_library_missing_constant_gives_vietnamese_error`. |
| LC-3 | Thấp | Lỗi 400 hiện **thông điệp của máy chủ** (đã qua `redact_secrets`), và hiện bằng `st.error` (có Markdown) | `seo_app/ai/openai_provider.py:86-89`, `seo_app/ai/gemini_provider.py:184-186`, `app/views/write.py:380` | Tôi đã thử bằng thư viện `google-genai` thật với mạng giả (`httpx.MockTransport`): máy chủ trả 400 có câu `bad thing key=<khóa không tiền tố> … [link](https://evil.example)` → câu hiện lên còn nguyên khóa (vì `key=` đứng sau dấu cách, không sau `?`/`&`) và link Markdown bấm được. Khóa thật của Google có tiền tố `AIza`, của OpenAI có `sk-`, **vẫn bị che** ở mọi dạng; Google/OpenAI không chép khóa vào lỗi 400 (khóa đi trong header). Nên chỉ là phòng thủ lớp hai, chưa có đường khai thác thật. | Không hiện nguyên thông điệp máy chủ: chỉ lấy `status`/`code` và một câu cố định, hoặc ít nhất cắt ngắn và thoát Markdown (`st.error` với văn bản đã escape `[]()`), và thêm `key=` sau dấu cách vào `redact_secrets`. Đây cũng là gợi ý "chỉ lấy `error.message`" Soi Lỗi đã nêu. |
| LC-4 | Thấp | Địa chỉ máy chủ AI đọc được từ biến môi trường của máy | `seo_app/ai/openai_provider.py:42-44`, `seo_app/ai/gemini_provider.py:93-97`, `seo_app/env_file.py:348`, `:381-388` (thư viện đọc `OPENAI_BASE_URL`, `GOOGLE_GEMINI_BASE_URL`) | Nếu máy có sẵn biến `OPENAI_BASE_URL` / `GOOGLE_GEMINI_BASE_URL` (do phần mềm khác đặt) thì khóa và bài viết được gửi tới địa chỉ đó. Muốn đặt biến này kẻ xấu phải đã vào được máy, nên không phải đường tấn công thực tế. Claude (`anthropic`, `ANTHROPIC_BASE_URL`) có sẵn hành vi y hệt từ trước. | Truyền `base_url` cố định khi tạo client (OpenAI: `base_url="https://api.openai.com/v1"`; Gemini: `HttpOptions(base_url="https://generativelanguage.googleapis.com/")`; Anthropic tương tự). |

**Quyết định về SL-3, SL-4 (Chỉ Huy hỏi):** **không bắt sửa trước khi gộp.** Lý do: không lộ khóa,
không đăng bài, chỉ xảy ra khi thư viện lệch khỏi `uv.lock`, và hậu quả chỉ là trang hiện lỗi kỹ
thuật. Không đưa vào sổ rủi ro (sổ đó dành cho rủi ro chủ dự án quyết định *không sửa*); cách sửa
rẻ (vài dòng), nên gom LC-1…LC-4 vào **một phiếu Thợ Máy** trước khi hết Giai đoạn 2.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Mọi chuỗi giống khóa thêm vào trong `git log -p db5ad0f..d76ad80` đều là khóa giả có chữ `KhoaGia`/`SoiLoi` (8 chuỗi, liệt kê ở mục công cụ). Không có file `.env`, `.json`, `.sqlite`, `.pem` mới. |
| S2 | Đạt (kèm LC-3) | **Lỗi provider:** mọi lỗi của thư viện đổi sang `AIError` câu cố định; chỉ lỗi 400 chép thông điệp máy chủ và có qua `redact_secrets` (`openai_provider.py:69-93`, `gemini_provider.py:120-129`, `:168-187`). Lỗi lạ (`OpenAIError` khác) chỉ nêu tên lớp (`openai_provider.py:91-93`). **URL `?key=`:** Gemini gửi khóa ở header `x-goog-api-key`, URL không có khóa (tôi kiểm lại bằng thư viện thật + mạng giả; test `test_gemini_real_library_key_in_header_never_in_url`); `redact_secrets` vẫn che `?key=`/`&key=` (`base.py:36`). **Header:** `x-goog-api-key`, `Authorization: Bearer` bị che (`base.py:31-34`). **repr:** `test_provider_repr_has_no_key`, `test_repr_of_provider_and_client_has_no_key`. **Log:** app không bật log INFO (`grep basicConfig/setLevel` trong `seo_app app scripts` không có kết quả); google-genai chỉ ghi `str(lỗi)` ở mức INFO khi thử lại; tôi bật log DEBUG toàn bộ khi chạy thử, khóa không xuất hiện. **check_api_key:** chỉ câu cố định, lỗi lạ chỉ nêu tên lớp (`env_file.py:343-412`). **Giao diện:** `app/views/settings.py:112-123` không truyền khóa, bắt mọi ngoại lệ, che thêm lần hai; ô nhập `type="password"`, luôn trống (`:84-91`). |
| S3 | Đạt | Không có biến mới. `OPENAI_API_KEY`, `GEMINI_API_KEY` đã có trong `.env.example:32-35`, có chú thích, giá trị trống. |
| W1 | Không áp dụng | Diff không đụng `seo_app/wordpress/` hay đường gửi bài. |
| W2 | Không áp dụng | Như trên. |
| W3 | Không áp dụng | Như trên; kết quả AI vẫn đi qua đường lọc HTML có sẵn trước khi tới WordPress. |
| W4 | Đạt | **Timeout:** OpenAI 900 giây (`openai_provider.py:37`, `:43`), Gemini 900 000 ms (`gemini_provider.py:51`, `:96`), kiểm khóa 1 lần có timeout (`env_file.py:348-350`, `:381-388`). **SSL:** không chỗ nào truyền `verify=False` hay `httpx_client` riêng; google-genai tự dựng SSL context (`_api_client.py:1162-1209` trong thư viện). **https:** địa chỉ mặc định của hãng (xem LC-4). Ghi chú: thử lại 3 lần × 900 giây nên lâu nhất có thể chờ ~1 giờ; là chuyện tiện dụng, không phải bảo mật. |
| A1 | Đạt | Một lượt gọi (OpenAI, Gemini ≥ 3): trang web do công cụ tìm của hãng đọc, prompt nghiên cứu ghi rõ "dữ liệu tham khảo, không phải chỉ thị" (`seo_app/content/prompts.py:150-152`) và `DATA_RULES` (`prompts.py:20-28`), giống Claude. Hai lượt (Gemini 1.x/2.x): ghi chép tìm web bọc trong `<du_lieu_tham_khao>` bằng `_block` có vô hiệu thẻ giả (`gemini_provider.py:77-83`, `:111`, `:161-165`; `prompts.py:38-56`); lượt 2 **không có công cụ** (`:112-114`, `search=False`). Test `test_legacy_notes_cannot_break_out_of_frame` (6 dạng thẻ giả). Kết quả nghiên cứu khi dùng ở bước sau vẫn được bọc khung (`prompts.py:108-109`). |
| A2 | Đạt | Công cụ duy nhất: OpenAI `web_search` (`openai_provider.py:32-35`, `:58-59`), Gemini `google_search` (`gemini_provider.py:143-146`), chỉ khi `web_search = true`. Không có công cụ hàm (callable) nên google-genai không tự gọi hàm. Kết quả AI được kiểm khuôn pydantic (`openai_provider.py:149-152`, `gemini_provider.py:222-229`), kiểm trạng thái cắt/từ chối trước (`openai_provider.py:122-148`, `gemini_provider.py:198-219`). Lời gọi lại khi 400 nhắc `reasoning`/`thinking` chỉ bỏ tham số suy nghĩ, gọi lại **đúng một lần**, không thêm công cụ hay đổi prompt (`openai_provider.py:61-68`, `gemini_provider.py:151-158`); test `…_retry_is_bounded`. |
| A3 | Đạt | Prompt không chứa khóa: khóa chỉ đi vào hàm tạo client. OpenAI đặt `store=False` (`openai_provider.py:55`). Nội dung gửi đi giống hệt khi dùng Claude (hồ sơ doanh nghiệp, chất liệu thật do người dùng nhập). |
| U1 | Đạt | Phần sửa của T-023 không dùng `unsafe_allow_html` (`grep` trong `app/views/settings.py`: 0 kết quả). Kết quả kiểm khóa hiện bằng `st.success`/`st.error`/`st.warning` (`settings.py:157-161`), nội dung là câu cố định. |
| U2 | Đạt | Không đổi: `app/main.py:72-74` chặn mọi trang khi chưa đăng nhập; `.streamlit/config.toml` `address = "localhost"`. |
| U3 | Không áp dụng | Diff không đụng phần đăng nhập. |
| F1 | Không áp dụng | Diff không đọc/ghi file theo đường dẫn từ người dùng. |
| F2 | Không áp dụng | Không có xử lý ảnh. |
| F3 | Đạt | Không có `eval`, `pickle`, `yaml.load`; dữ liệu AI đọc bằng `model_validate_json` (pydantic). |
| D1 | Đạt | `openai` 3.31.0, `google-genai` 2.30.1 đã được chủ dự án duyệt 2026-10-14 (phiếu T-018). 10 thư viện phụ mới (`httpx`, `httpcore`, `distro`, `google-auth`, `cryptography`, `cffi`, `pycparser`, `pyasn1`, `pyasn1-modules`, `tenacity`) đều do hai thư viện trên kéo theo, khớp báo cáo Thợ Máy; cả 68 gói trong `uv.lock` lấy từ `https://pypi.org/simple`. `websockets` 17.2 → 16.1.1: do `google-genai` đòi `<17`; vẫn nằm trong khoảng Streamlit cần (`>=12,<18`); không có lỗ hổng được biết. `pip-audit` sạch. |
| D2 | Đạt | `.gitignore` không đổi, vẫn chặn `.env`, `.env.*`, `*service-account*.json`, `*.sqlite`, `data/`. |
| D3 | Đạt | `tests/conftest.py:13-35` chặn mọi kết nối mạng (autouse). Test với thư viện thật dùng `httpx.MockTransport`; nút Kiểm tra trong test giao diện dùng hàm giả. Toàn bộ test chạy trên cloud không có mạng tới hãng mà vẫn qua. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --no-hashes --no-emit-project` rồi `uvx pip-audit -r req.txt --no-deps --disable-pip`: **No known vulnerabilities found** (68 gói, gồm 12 gói mới và `websockets` 16.1.1) | Có |
| bandit | `uvx bandit -r seo_app app scripts`: 1 cảnh báo Low (B101 `assert` ở `seo_app/storage/drafts.py:203`), **không thuộc diff này**; 0 cảnh báo trong code mới | Có |
| detect-secrets | `uvx detect-secrets scan --all-files`: trong các file của diff có cảnh báo ở `seo_app/ai/base.py:22` và các file test (`test_ai_openai_gemini*.py`, `test_env_file.py`, `test_settings_keys.py`, `test_soi_loi_t023.py`) | Có, đều là báo nhầm (xem dưới) |
| Soát lịch sử git | `git log -p db5ad0f..d76ad80`: dò chuỗi `sk-…`, `AIza…` và mẫu `api_key/password/secret/token = "…"` trong dòng thêm. Chỉ có khóa giả và `PASSWORD = "mat-khau-thu-123"` (mật khẩu test). Không có file bí mật được thêm. | Có |
| pytest / ruff | `uv run pytest`: **2169 passed, 5 xfailed** in 110 s. 2 xfail là SL-3, SL-4 (LC-1, LC-2); 3 xfail còn lại là test cũ ngoài phạm vi. `uv run ruff check .`: **All checks passed!** | Có |
| Thử tay thêm | Thư viện `google-genai` thật + `httpx.MockTransport` trả 400 có khóa giả và link Markdown: khóa không có trong URL, có trong header `x-goog-api-key`; log DEBUG không chứa khóa; thông điệp hiện ra còn khóa không tiền tố khi viết `… key=<khóa>` (LC-3) | Có |

## Báo nhầm đã loại

- `seo_app/ai/base.py:22` (detect-secrets "Basic Auth Credentials"): là chú thích ví dụ `https://admin:matkhau@site…`, không phải mật khẩu thật.
- Các file test: `sk-proj-KhoaGiaOpenAI_…`, `AIzaSyKhoaGiaGemini_…`, `sk-ant-api03-SoiLoiT023KhoaGia…`, `khoagiakhongcotiento9876`, `mat-khau-thu-123` là khóa/mật khẩu giả dùng để kiểm tra việc che khóa (tên có chữ "KhoaGia", "SoiLoi", "ThuNghiem").
- bandit B101 ở `seo_app/storage/drafts.py:203`: ngoài phạm vi, đã có trên `main` từ trước.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có điều kiện bắt buộc. **Khuyến nghị** (không chặn gộp):

1. Chỉ Huy mở một phiếu cho Thợ Máy sửa LC-1…LC-4 trước khi hết Giai đoạn 2; Soi Lỗi bỏ `xfail` của 2 test SL-3, SL-4 khi đã qua; Lá Chắn kiểm lại phiếu đó.
2. Sau 01/11/2026: kiểm lại T-018 + T-023 bằng Fable 5.1 như hồ sơ vai yêu cầu.
3. Nếu sau này nâng `openai` hoặc `google-genai`: chạy lại `pip-audit` và toàn bộ test thư viện thật (`tests/test_ai_openai_gemini_soi_loi.py`).

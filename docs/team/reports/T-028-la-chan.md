# Biên bản bảo mật T-028 · Máy chủ AI trả mã 200 nhưng nội dung hỏng

> **Lưu ý về model:** lần kiểm định này chạy **tạm bằng Opus 5.5** (`claude-opus-5-5`), vì tài khoản hiện không dùng được Fable 5.1 (cần mua thêm lượt dùng). Chủ dự án đã duyệt cho Lá Chắn chạy tạm Opus 5.5 tới 01/11. **Sau 01/11 phải kiểm lại bằng Fable** (Chỉ Huy giữ việc này trên bảng việc).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm thay Fable 5.1, xem lưu ý trên) |
| Phiếu được kiểm | [T-028](../tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) |
| Phạm vi | `git diff origin/main...team/T-028`, HEAD code `1c300f5` (gốc `396656b` trên `main`). File code: `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`. Test: `tests/test_ai_t028.py` (mới), `tests/test_soi_loi_t028.py` (mới), `tests/test_soi_loi_t026.py` (bỏ 4 dòng `xfail`). Không đụng `app/`, `config/`, `scripts/`, `tests/conftest.py`, `uv.lock`, `pyproject.toml`, `.gitignore`, `.env.example` |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT** (không có lỗi Nghiêm trọng/Cao/Trung bình; 3 lỗi Thấp ghi sổ, không cần phiếu riêng). Được gộp vào `main`. |

## Tóm tắt (cho chủ dự án)

Phiếu này an toàn để gộp. Khi Wi-Fi công cộng, proxy hay máy chủ AI trả về một trang lạ, app giờ chỉ hiện một câu tiếng Việt viết sẵn. App không còn hiện khối lỗi tiếng Anh, không chép chữ nào của máy chủ, không lộ khóa. Nút **Kiểm tra** khóa cũng chặt hơn: trước đây gặp trang lạ nó có thể báo nhầm "Khóa dùng được", nay báo "dữ liệu lạ".

App cũng không còn nhận các biến môi trường lạ có thể chèn thêm thông tin vào mọi lời gọi AI (`*_CUSTOM_HEADERS`, mã tổ chức/dự án OpenAI) hay bắt thư viện Gemini ghi bài ra file. Proxy và chứng chỉ của mạng công ty vẫn dùng như cũ, đúng quyết định của anh.

Tôi có 3 ghi chú mức Thấp, đều chỉ là câu báo hơi sai hướng hoặc cách viết có thể gọn hơn. Không lỗi nào làm lộ khóa hay gọi sai máy chủ, nên không cần sửa trước khi gộp.

## Lỗi phát hiện

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T028-1 | Thấp (ghi nhận) | `ignoring_custom_headers` sửa `os.environ` (chung cho cả tiến trình) trong lúc tạo client, dưới `threading.Lock`, rồi trả lại | `seo_app/ai/base.py:200-221` | Đã thử (biến giả, không gọi mạng): (1) trong lúc một luồng đang tạo client, luồng khác **không thấy** 4 biến này (`OPENAI_ORG_ID` vắng mặt), đúng như Thợ Máy nêu; app không đọc 4 biến này ở chỗ nào khác nên không ảnh hưởng. (2) Luồng thứ hai tạo client phải **chờ khóa**, client của nó cũng không có header lạ. (3) Ngoại lệ giữa chừng: biến trả lại đủ, khóa được nhả. (4) Máy **không có** biến nào trong 4 biến (trường hợp thường gặp): `os.putenv`/`os.unsetenv` được gọi **0 lần**, tức là không đụng môi trường. Các khe còn lại: gọi lồng trong cùng luồng sẽ treo (`Lock` không vào lại được, hiện không có chỗ lồng); Ctrl+C rơi đúng giữa các lệnh `pop` thì biến mất khỏi **tiến trình app** (không phải khỏi máy), mà đó lại đúng là điều app muốn; trên Mac, đổi biến môi trường trong lúc mã C ở luồng khác đọc biến môi trường về lý thuyết không an toàn, nhưng việc này chỉ xảy ra khi máy có đặt các biến đó, và hậu quả xấu nhất là app dừng chứ không lộ gì. **Không có đường làm header lạ lọt vào client**: cả 4 chỗ tạo client Anthropic/OpenAI đều nằm trong khóa (`anthropic_provider.py:39`, `openai_provider.py:58`, `env_file.py:383`, `:425`) | Không bắt buộc. **Cách "sạch hơn" bằng tham số không có:** thư viện không có tham số tắt `*_CUSTOM_HEADERS`. `default_headers` chỉ đè được header trùng tên, nên phải tự đọc và tự tách biến để biết tên mà đè. Truyền `organization=""` thì thư viện vẫn gửi header rỗng (`openai/_client.py:281-286`). Xóa hẳn biến lúc nạp module thì mất tác dụng khi biến được đặt sau đó. Vì vậy cách hiện tại là hợp lý. Khi tiện: đổi `Lock` thành `RLock` để gọi lồng không treo |
| LC-T028-2 | Thấp (= SL-T028-1, **chấp nhận**) | Thư viện tự lệch phiên bản **bên trong** hàm đọc trả lời → câu "dữ liệu lạ" thay vì "uv sync" | `seo_app/ai/base.py:123-152` (`is_bad_response`) | Chỉ xảy ra khi thư viện hãng mâu thuẫn với chính nó (Soi Lỗi giả lập bằng cách vá `construct_type`). Câu báo cố định, không lộ gì, không biến lỗi thành kết quả, không sập trang. Đổi lại, chiều ngược quan trọng hơn: dữ liệu hỏng từ máy chủ **không bao giờ** bị báo thành "uv sync" (Soi Lỗi thử 13 dạng × 2 hãng × 2 chỗ) | Chấp nhận như Soi Lỗi đề xuất. Không lập phiếu. Giữ test `xfail(strict=True)` |
| LC-T028-3 | Thấp (= SL-T028-3, có từ trước T-028) | Nội dung nén `gzip`/`br` hỏng ở Anthropic/OpenAI ra câu "Không kết nối được tới …" thay vì "dữ liệu lạ" | `seo_app/ai/anthropic_provider.py`, `openai_provider.py` (nhánh `APIConnectionError`), `seo_app/env_file.py` | Thư viện bọc `DecodingError` thành `APIConnectionError` trước khi app thấy. Câu vẫn cố định, vẫn hướng người dùng kiểm tra mạng (đúng hướng xử lý với proxy/Wi-Fi chen trang). Không chép chữ máy chủ, không lộ khóa | Không lập phiếu riêng. Khi có phiếu khác sửa lớp AI thì gộp vào: nhánh `APIConnectionError` xét `__cause__` là `DecodingError` → `bad_response_error`. Giữ test `xfail(strict=True)` |

**Hai quyết định Chỉ Huy hỏi:** SL-T028-1 **chấp nhận** (lý do ở dòng LC-T028-2). SL-T028-3 **chấp nhận tạm**, không chặn và không cần phiếu riêng; sửa kèm khi có phiếu lớp AI tiếp theo. Cả hai đều là câu gợi ý chưa trúng, không phải lỗ hổng.

## Đánh giá các điểm trọng tâm

**S2, câu báo cố định.** Mọi câu mới chỉ ghép: tên hãng viết sẵn trong code (`VENDOR`/`LABEL`), `task.max_tokens` và `task.name` (đọc từ `config/ai.toml`, không từ máy chủ):
- `bad_response_message` (`base.py:88`), `connection_lost_message` (`:100`), câu quá giờ (`:182`), câu bài bị cắt (`anthropic_provider.py:55-59`), `_other_result` (`env_file.py:329-344`).
- `_other_result` nhánh lạ chỉ nêu `type(exc).__name__`.
- Không chỗ nào ghép `str(exc)`, `exc.message`, `exc.body` hay nội dung trả lời. `_result` vẫn che thêm bằng `redact_secrets`.
- Test của Thợ Máy và Soi Lỗi chèn chuỗi máy chủ và khóa giả (3 hãng) vào trang HTML, JSON, luồng SSE, và vào cả thông điệp lỗi mạng giữa luồng: câu hiện ra không chứa cả hai.
- Hiển thị vẫn qua `st.error(str(exc))` (`app/views/write.py:380`), chỉ với `AIError`.

**Bắt rộng `except Exception` trong `generate`** (`anthropic_provider.py:48`, `openai_provider.py:69`). Chỉ đổi lỗi thành `AIError` khi nhận ra (dữ liệu hỏng / mạng / thư viện lệch). Lỗi khác vẫn `raise` nguyên như trước T-028. Không nhánh nào biến lỗi thành kết quả hợp lệ. Lỗi SSL/chứng chỉ vẫn đi qua `APIConnectionError` (câu "không kết nối được"), không bị nuốt.

**Nút Kiểm tra chặt hơn** (`env_file.py:352-363`, `_listing_ok`): trước T-028, proxy trả `{}` hay trang lạ mã 200 thì nút báo "Khóa … dùng được". Nay báo "dữ liệu lạ". Đây là thay đổi theo hướng an toàn.

**Biến môi trường (yêu cầu 3, sổ rủi ro `security.md` mục 6 trên `main`):**
- `IGNORED_ENV` gồm `ANTHROPIC_CUSTOM_HEADERS`, `OPENAI_CUSTOM_HEADERS`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID` (`base.py:200-205`).
- Tôi tự đặt `OPENAI_CUSTOM_HEADERS="Authorization: Bearer …\nX-Evil: 1"`, `ANTHROPIC_CUSTOM_HEADERS="X-Evil: 1\nx-api-key: …"`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`, rồi tạo provider và gọi `check_api_key`. Kết quả: không có `X-Evil`, không có `OpenAI-Organization`/`OpenAI-Project`; `x-api-key`/`Authorization` là khóa của app; biến được trả lại đúng giá trị.
- Gemini: `GOOGLE_GENAI_CLIENT_MODE=replay` + thư mục/mã phát lại → client vẫn là `BaseApiClient` (không phải `ReplayApiClient`), ở cả provider (`gemini_provider.py:120`) lẫn nút Kiểm tra (`env_file.py:479`). Trước T-028, tôi đã tái hiện được: biến này chuyển `GeminiProvider` sang `ReplayApiClient` (ghi bài ra file hoặc lấy câu trả lời từ file). T-028 đã bịt.
- `HTTPS_PROXY` còn nguyên trong và sau khi tạo client. `SSL_CERT_FILE`/`SSL_CERT_DIR` không bị đụng. Khớp quyết định của chủ dự án ghi trong sổ rủi ro.
- Biến còn lại thư viện đọc: `ANTHROPIC_AUTH_TOKEN` (bỏ qua khi app truyền `api_key`), `OPENAI_ADMIN_KEY` (chỉ gửi ở lời gọi quản trị app không dùng), `*_WEBHOOK_*` (không gửi đi), `GOOGLE_GENAI_USE_VERTEXAI`/`_ENTERPRISE` (vô hiệu vì `vertexai=False`). Đồng ý với tra cứu của Thợ Máy.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Chuỗi giống khóa trong diff chỉ có 3 khóa giả `…T028KhoaGia…` (`tests/test_ai_t028.py:43-45`). `detect-secrets` trên 9 file của diff: không báo. `git log -p origin/main..team/T-028` lọc `api_key/password/secret/token/sk-ant/AIza/BEGIN PRIVATE`: chỉ là chữ mô tả trong báo cáo và tên trường (`max_tokens`, `nextPageToken`) |
| S2 | Đạt | Xem mục "Đánh giá các điểm trọng tâm". Mọi câu mới cố định (`base.py:88-104,176-187`, `anthropic_provider.py:43-66`, `openai_provider.py:64-79`, `env_file.py:329-344`), không ghép nội dung máy chủ, qua `redact_secrets` ở nút Kiểm tra |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi |
| W1 | Không áp dụng | Không đụng WordPress hay đường đăng bài |
| W2 | Không áp dụng | Như trên |
| W3 | Không áp dụng | Như trên |
| W4 | Đạt | 6 chỗ tạo client vẫn có `base_url` chính thức `https` cố định (`anthropic_provider.py:40`, `openai_provider.py:59-61`, `gemini_provider.py:113-120`, `env_file.py:384-386`, `:426-428`, `:470-479`). Timeout giữ như cũ. Không chỗ nào tắt SSL. Proxy/chứng chỉ giữ theo sổ rủi ro. Chế độ phát lại của Gemini tắt (không lấy câu trả lời từ file thay vì máy chủ) |
| A1 | Không áp dụng | Không đổi prompt hay khung dữ liệu |
| A2 | Đạt | Không thêm công cụ cho AI. Kết quả AI vẫn qua kiểm khuôn. `_parse` của OpenAI chịu được JSON sai kiểu (`_as_list`, `openai_provider.py:193-197`) và chỉ nhận `text` là chuỗi. Mọi nhánh lỗi mới kết thúc bằng `AIError` |
| A3 | Không áp dụng | Không đổi nội dung gửi đi. Header lạ từ biến môi trường bị bỏ, nên lời gọi gửi **ít** thông tin hơn |
| U1 | Đạt | Không có `unsafe_allow_html` mới. Câu lỗi hiện bằng `st.error`, nội dung cố định |
| U2 | Không áp dụng | Không đụng giao diện |
| U3 | Không áp dụng | Không đụng đăng nhập |
| F1 | Không áp dụng | Không đọc/ghi file mới. Bịt chế độ ghi bài ra file của google-genai (`no_debug_config`) |
| F2 | Không áp dụng | Không xử lý ảnh |
| F3 | Đạt | Không `eval`/`pickle`/`yaml.load`. `is_bad_response` chỉ đọc tên module/hàm trong traceback, không chạy gì |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi. Chỉ dùng thư viện chuẩn (`json`, `os`, `threading`, `traceback`, `contextlib`) và thư viện đã có. `pip-audit` trên danh sách khóa (`uv export --frozen`, 202 dòng): `No known vulnerabilities found` |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | `tests/conftest.py` không đổi (bộ chặn mạng autouse). Test mới dùng `httpx.MockTransport`/`httpx2.MockTransport`. Phép thử của tôi chỉ tạo client, không gọi mạng; `HTTPS_PROXY` giả trỏ `127.0.0.1:9` không được dùng tới |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uvx pip-audit -r <uv export --frozen>` (202 dòng, đúng thư viện của dự án): `No known vulnerabilities found` | Có |
| bandit | `-r seo_app app scripts`: 1 Thấp, B101 `assert` ở `seo_app/storage/drafts.py:203` (ngoài diff, đã biết) | Có, báo nhầm |
| detect-secrets | 9 file của diff (5 file code, 2 file test, 2 báo cáo): không báo | Có |
| Soát lịch sử git | `git log -p origin/main..team/T-028`: không có bí mật; chuỗi giống khóa đều là khóa giả `KhoaGia` | Có |
| pytest | Windows 11, worktree `wt-T-028` (cùng lúc máy đang chạy test ở worktree khác): `3070 passed, 10 skipped, 9 xfailed, 1 warning in 335.00s`, **0 hỏng, 0 lỗi**. Chạy lần 2 các file test lớp AI, khóa và bộ chặn mạng (8 file): `1090 passed, 4 skipped, 6 xfailed`. Cảnh báo duy nhất là `PydanticSerializationUnexpectedValue` từ test của Soi Lỗi (`test_soi_loi_t028.py::test_anthropic_other_broken_streams_give_fixed_message[message-content-la-so]`), cố ý đưa dữ liệu sai kiểu | Có |
| ruff | `uv run ruff check .`: `All checks passed!` | Có |
| Phép thử tay | 5 test tạm ngoài repo (biến môi trường độc, nhiều luồng, ngoại lệ giữa chừng, đếm `putenv`, nút Kiểm tra), nạp `tests/conftest.py` của nhánh: đều qua, kết quả ghi ở LC-T028-1 và mục biến môi trường | Có |

## Báo nhầm đã loại

- **bandit B101** `seo_app/storage/drafts.py:203`: ngoài diff, đã xét ở các biên bản trước.
- Các dòng soát lịch sử git có chữ `token`/`secret`: là chữ trong báo cáo (`OPENAI_WEBHOOK_SECRET`, `max_tokens`) và trường dữ liệu giả (`nextPageToken`), không phải bí mật.

## Điều kiện

Không có điều kiện bắt buộc (kết luận ĐẠT). Đề nghị Chỉ Huy:

1. Ghi LC-T028-1, LC-T028-2 (SL-T028-1, chấp nhận) và LC-T028-3 (SL-T028-3) vào bảng việc. Không cần phiếu riêng; LC-T028-3 và việc đổi `Lock` → `RLock` gộp vào phiếu lớp AI tiếp theo nếu có.
2. Sau 01/11: kiểm lại biên bản này bằng Fable.

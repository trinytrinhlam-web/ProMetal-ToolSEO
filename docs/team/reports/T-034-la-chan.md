# Biên bản bảo mật T-034 · Lỗi Thấp còn lại của lớp AI và thử mù (sau T-019)

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Opus 5.5 (Opus tạm**, Fable bị giới hạn tới 01/11; chủ dự án duyệt chạy tạm. Nên kiểm lại bằng Fable sau 01/11) |
| Phiếu được kiểm | [T-034](../tickets/T-034-loi-thap-lop-ai-sau-t019.md) |
| Phạm vi | diff `699d7ba..931e976` (nhánh `team/T-034`, gồm 2 lượt Thợ Máy + test Soi Lỗi). Code: `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `registry.py`, `seo_app/content/blind_test.py`, `seo_app/env_file.py`, test |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Thay đổi an toàn. Cách mới để bỏ qua biến "header lạ" (`*_CUSTOM_HEADERS`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`) không còn gỡ biến khỏi máy nữa, nên hết lỗi khi chạy nhiều luồng. Header lạ vẫn **không bao giờ** tới máy chủ AI: tôi đã thử tạo 240 client song song của thư viện thật, không client nào nhận header lạ, và client vẫn chỉ gọi đúng địa chỉ chính thức. Mọi câu lỗi mới là câu cố định, không chép chữ máy chủ, không lộ khóa. Còn 3 điểm nhỏ mức Thấp, ghi sổ, không cần chặn.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T034-1 | Thấp | Tên mô hình kiểu địa chỉ web vẫn qua bộ lọc ký tự (`:` `/` `.` được phép), và vẫn thành link bấm được trong câu lỗi. LC-T019-1 mới sửa được dạng `[chữ](link)` | `seo_app/content/blind_test.py:65`, `:252`; hiện ở `app/views/settings.py:295` (`st.error`, Markdown) | Người dùng gõ tên mô hình `https://x.y` hoặc `www.x.y` ở trang thử mù → qua `validate_request` (đã thử: `_MODEL_CHARS` và `_maskable` đều nhận) → máy chủ báo không có mô hình → `st.error("Bài A (… · https://x.y): Không có mô hình «https://x.y»…")` → Markdown của Streamlit tự biến địa chỉ trần thành link. Chỉ là chữ do chính người dùng gõ, không ai khác chèn được, máy chủ vẫn là địa chỉ chính thức (`base_url` cố định), nên không khai thác được | Khi tiện (ví dụ cùng T-031 về link trần): trong `validate_request` từ chối thêm tên có `://` hoặc bắt đầu bằng `www.`; tên thật của 3 hãng không có các dạng này |
| LC-T034-2 | Thấp | Khung nhìn `os` đã lọc chỉ che `os.environ`/`os.getenv`; `os.environb` và `os.getenvb` vẫn đi thẳng tới `os` thật nên còn thấy biến lạ | `seo_app/ai/base.py:301` (`__getattr__`) | Đã thử: `_OS_WITHOUT_IGNORED.getenvb(b"OPENAI_ORG_ID")` trả giá trị thật. **Hiện không có đường đi**: `anthropic` 1.13.0 và `openai` 3.31.0 chỉ đọc biến qua `os.environ.get` trong `_client.py` (đã grep toàn bộ hai gói: không có `environb`/`getenvb`, không có `from os import environ`). Trên Windows không có `environb`. Chỉ thành lỗi nếu bản thư viện sau này đổi cách đọc; khi đó test thư viện thật (`tests/test_soi_loi_t034.py:223-224`, `tests/test_ai_t034.py:119`) sẽ đỏ lúc đổi `uv.lock` | Thêm `environb`/`getenvb` vào lớp lọc (hoặc cho chúng ném lỗi để rơi về đường dự phòng). Không gấp |
| LC-T034-3 | Thấp | Nếu việc nạp `openai._client` ném lỗi khác `ImportError` (gói hỏng), `anthropic._client.os` đã bị trỏ sang khung nhìn lọc mà không được trả lại, vì vòng trỏ nằm **trước** `try/finally` | `seo_app/ai/base.py:327-352` (trước `try` ở `:358`) | Đã thử: giả `import_module("openai._client")` ném `RuntimeError` → sau đó `anthropic._client.os` vẫn là khung lọc. Hậu quả nghiêng về **an toàn** (thư viện tiếp tục không thấy biến lạ), khóa vẫn được nhả (`locked() == False`). Chỉ là sai lệch nhỏ về chức năng, không lộ gì | Đưa vòng trỏ vào trong `try` (hoặc bắt `Exception` thay vì chỉ `ImportError` khi nạp module, coi như cần dự phòng) |

Không có lỗi Nghiêm trọng, Cao hay Trung bình.

## Kiểm từng trọng tâm của Chỉ Huy

### 1. W4 / mục 2.7, S2: `_OsWithoutIgnored` và đường dự phòng

Cách làm: trong `ignoring_custom_headers()` (`seo_app/ai/base.py:312`), tên `os` bên trong `anthropic._client` và `openai._client` được trỏ tạm sang `_OS_WITHOUT_IGNORED`. Khung này đọc thẳng `os.environ` thật mỗi lần, nhưng không thấy 4 biến trong `IGNORED_ENV`. Xong thì trả lại.

- **Thư viện đọc biến ở đâu.** Đã grep hai gói đang cài: `ANTHROPIC_CUSTOM_HEADERS` chỉ đọc ở `anthropic/_client.py:244` (và `:686`, client async, app không dùng); `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`, `OPENAI_CUSTOM_HEADERS` chỉ ở `openai/_client.py:281, :285, :317` (và bản async `:1047-1083`). Đều là `os.environ.get(...)` qua tên `os` của module đó. Bản trong `anthropic/lib/google_cloud` và `openai/lib/azure.py` app không dùng. Google-genai không có biến tương tự (đã ghi ở T-028).
- **Đủ 4 chỗ tạo client** đều nằm trong `with ignoring_custom_headers()`: `anthropic_provider.py:43`, `openai_provider.py:61`, `env_file.py:388`, `env_file.py:438`. Không có chỗ tạo client Anthropic/OpenAI nào khác (`grep "Anthropic(\|OpenAI("` toàn `seo_app`, `app`, `scripts`).
- **Tạo song song.** Tôi tự viết thử (ngoài bộ test): đặt cả 4 biến chứa header độc (có cả `Authorization: Bearer …`), 8 luồng mỗi luồng tạo 30 client thật xen kẽ Anthropic/OpenAI, cùng lúc 4 luồng khác chạy `dict(os.environ)` 3.000 lần. Kết quả: 0 client nhận header lạ, 0 `KeyError` ở luồng đọc, `base_url` của mọi client đúng `ANTHROPIC_URL`/`OPENAI_URL`, xong thì `os` của hai module trả về `os` thật và biến vẫn còn nguyên trong máy.
- **Khung nhìn chỉ đọc có lọt không.** Đã thử trực tiếp: `get`, `getenv`, `in`, `copy()`, `items()`, `dict(...)` đều không thấy biến lạ. `environb`/`getenvb` thì lọt (LC-T034-2), nhưng thư viện không dùng. Thư viện đọc qua module khác ngoài `_client`: hiện không có (grep ở trên). Nếu bản sau dời sang module khác mà `_client` vẫn còn `os`, đường dự phòng sẽ không tự bật; khi đó test dùng thư viện thật với header độc (`tests/test_ai_t034.py:119`, `tests/test_soi_loi_t034.py:223-224`, `:335`) sẽ đỏ ngay lúc nâng phiên bản. Mức bảo vệ này chấp nhận được.
- **Đường dự phòng.** Có hai nhánh: module `_client` mất mà gói vẫn còn (`base.py:345`), hoặc `os` của module không phải `os` thật (`:352`). Cả hai đều quay về cách cũ: gỡ biến khỏi `os.environ` rồi trả lại (`:361`). Đã thử thay `openai._client.os` bằng đối tượng khác: biến bị gỡ đúng trong lúc tạo, trả lại đúng sau. Đây là hướng an toàn: không biết thư viện đọc ở đâu thì vẫn chặn.
- **Ngoại lệ và khóa.** Lồng hai tầng rồi ném lỗi giữa chừng: `os` trả về đúng, khóa nhả. `_ReentrantLock` (`base.py:241`) bọc `threading.RLock`, gọi lồng cùng luồng không treo (đã thử, và có `test_nested_call_same_thread_does_not_hang`). Một kẽ nhỏ khi nạp module hỏng: LC-T034-3, nghiêng về an toàn.
- **`base_url` của T-026** vẫn truyền rõ ở cả 4 chỗ và đã xác minh trên client thật ở trên.
- **Windows:** `os.environ` không phân biệt hoa thường, còn lớp lọc so đúng chữ hoa. Thư viện luôn gọi tên chữ hoa, nên không có đường lọt. Ghi lại để biết.

### 2. S2: câu lỗi mới hoặc đổi

| Câu | Vị trí | Nhận xét |
|---|---|---|
| `TokenLimitError` ở nhánh `ValidationError` | `anthropic_provider.py:88-90`, `_schema_error` `:142` | Câu cố định, chỉ ghép `task.max_tokens` (số) và `task.name` (tên việc trong code). `_cut_by_token_limit` (`:155`) chỉ so `stop_reason == "max_tokens"`, trả `True/False`, không đưa chữ nào của máy chủ ra; mọi lỗi khi đọc tiếp đều nuốt thành `False`; đọc tối đa 50 sự kiện của chính luồng đang mở (có timeout của client), không gọi thêm lần nào. Thử mù thay câu này bằng câu riêng của thử mù |
| Câu gzip / "dữ liệu lạ" | `anthropic_provider.py:109`, `openai_provider.py:124`, `env_file.py:406`, `:458` | Dùng `bad_response_error(VENDOR)` / `_bad_response(...)` có sẵn, câu cố định. `caused_by_decoding` (`base.py:191`) chỉ xét tên lớp lỗi, có giới hạn 20 bước và chặn vòng |
| Câu tên mô hình lạ | `blind_test.py:252-258` | Câu cố định, **không** nhắc lại tên người dùng gõ. Câu cũ có `«{model}»` (`_maskable`) chỉ chạy sau khi tên đã qua bộ lọc ký tự |
| Câu thiếu `config/ai.toml` | `registry.py:29` | Chỉ còn `config/{path.name}`, không còn đường dẫn đầy đủ (LC-T019-2 đã sửa) |

Không câu nào in khóa, header, URL hay chữ thô của máy chủ.

### 3. U1: ký tự tên mô hình

`_MODEL_CHARS = [A-Za-z0-9._:/@-]+` dùng `fullmatch` (`blind_test.py:65`, `:252`). Đã thử: `[a1](https://x.y)`, `<b>x</b>`, dấu `` ` ``, `*`, chữ toàn khổ (`ｇpt-5`), gạch Unicode đều bị từ chối. Dạng Markdown link đã hết. Còn dạng địa chỉ trần (`https://…`, `www.…`) vẫn thành link: LC-T034-1, mức Thấp như phiếu gốc vì chỉ là chữ của chính người dùng.

Phụ: tên mô hình đi vào đường dẫn URL của Gemini (`models/<tên>:…`). Có `/` và `.` thì gõ được `../`, nhưng máy chủ vẫn là địa chỉ chính thức cố định và khóa nằm trong header gửi đúng máy chủ đó; trước T-034 còn rộng hơn. Không phải lỗi.

### 4. ReDoS ở biểu thức che tên

Tôi đo lại, cả với chuỗi xấu của Soi Lỗi và chuỗi tự dựng:

| Chuỗi | ~4.000 ký tự | ~10.000 ký tự | ~20.000 ký tự |
|---|---|---|---|
| `Claude 1` + `-1.1`×n + `x` | 0,018 s | 0,095 s | 0,37 s |
| `Claude pro` + `-a.1`×n + `_x` | 0,015 s | 0,089 s | 0,35 s |
| tên mô hình `gpt-6.1 1` + `-1.1`×n | 0,016 s | 0,093 s | 0,41 s |
| 10 dạng khác (khoảng trắng dài, `gpt ` lặp, `1,` lặp…) | | ≤ 0,01 s | ≤ 0,03 s |

Tăng theo bình phương, không có dạng tăng theo hàm mũ (các nhóm lặp đều bắt đầu bằng ký tự riêng `-` hoặc khoảng trắng, nên không có nhiều cách tách). Đầu vào là chữ AI bị máy chủ cắt ở `BLIND_MAX_TOKENS = 2000` (`blind_test.py:35`). Với dạng xấu này mỗi token chỉ được vài ký tự, nên thực tế dưới 10.000 ký tự, dưới 0,1 giây. Muốn làm chậm đáng kể thì phải gửi trả lời hàng trăm nghìn ký tự, tức là đã chiếm được máy chủ hoặc proxy (rủi ro proxy đã ghi sổ ở mục 6), và hậu quả chỉ là app trên máy mình chạy chậm. **Chấp nhận được, không cần giới hạn độ dài ngay.** Đồng ý với đề xuất của Soi Lỗi: nếu sau này tăng giới hạn token của thử mù, giới hạn số đuôi nối gạch (ví dụ `{0,4}`) thay vì cắt độ dài (cắt độ dài có thể bỏ sót tên chưa che). Test `test_l2_hyphen_suffix_adversarial_text_is_fast` giữ ngưỡng.

### 5. D1, D3

`uv.lock`, `pyproject.toml` không đổi; không thêm thư viện. Test mới dùng `MockTransport`/đối tượng giả; bộ chặn mạng của test (T-029/T-030) vẫn bật, cả bộ chạy xanh.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không có bí mật trong diff. detect-secrets báo 4 chỗ, đều là báo nhầm (xem dưới). Soát `git log -p 699d7ba..HEAD` tìm `sk-ant…`/`sk-proj…`/`AIza…`: chỉ khóa giả có chữ "KhoaGia" |
| S2 | Đạt | Mục 2 ở trên: mọi câu mới/đổi là câu cố định; `_cut_by_token_limit` chỉ trả bool; `registry.py:29` bỏ đường dẫn đầy đủ |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Không áp dụng | Không đụng WordPress |
| W3 | Không áp dụng | Không đụng HTML gửi lên |
| W4 | Đạt | `base_url` cố định ở cả 4 chỗ tạo client (đã xác minh trên client thật); header lạ không tới client khi tạo song song (240 client, 0 lọt); đường dự phòng gỡ biến khi thư viện đổi cấu trúc (`base.py:345`, `:352`). Ghi sổ LC-T034-2, LC-T034-3 |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | Đạt | AI vẫn không có công cụ hành động; chữ AI vẫn qua che tên (`blind_test.py:283-289`) trước khi hiện. Biểu thức che chạy đủ nhanh với đầu vào thật (mục 4) |
| A3 | Không áp dụng | Không đổi dữ liệu gửi vào prompt |
| U1 | Đạt | `validate_request` chặn ký tự Markdown/HTML (`blind_test.py:252`). Còn địa chỉ trần tự thành link: LC-T034-1 (Thấp, chữ của chính người dùng) |
| U2 | Không áp dụng | Không đổi trang hay đăng nhập |
| U3 | Không áp dụng | Không đổi mật khẩu |
| F1 | Không áp dụng | Không đọc/ghi file mới |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Không có `eval`/`pickle`/`yaml.load`; `registry.py` vẫn đọc `utf-8-sig` |
| D1 | Đạt | Không thêm thư viện; pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới không gọi mạng; bộ chặn mạng của test vẫn hoạt động |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found | Có |
| bandit (`seo_app/ai`, `blind_test.py`, `env_file.py`) | 0 lỗi (1.597 dòng) | Có |
| detect-secrets (các file trong diff) | 4 cảnh báo | Có, đều báo nhầm |
| Soát lịch sử git | Không có khóa thật trong `699d7ba..931e976` | Có |
| pytest | 3.599 qua, 4 bỏ qua, 7 xfail (các xfail còn lại thuộc phiếu khác), 0 hỏng | Có |
| `tests/test_soi_loi_t028.py` chạy riêng 30 lần | 30/30 lần qua, 0 hỏng (Linux) | Có |
| ruff | All checks passed! | Có |

## Báo nhầm đã loại

- `seo_app/ai/base.py:28` "Basic Auth Credentials": dòng chú thích ví dụ `https://admin:matkhau@site…` mô tả bộ che bí mật, không phải mật khẩu thật.
- `tests/test_ai_t028.py:44-46` "Base64 High Entropy String": khóa giả của test (`sk-ant-api03-T028KhoaGia_…`, `sk-proj-T028KhoaGia_…`, `AIzaSyT028KhoaGia_…`), có từ T-028.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có. Ba lỗi Thấp LC-T034-1, -2, -3 ghi vào sổ; đề xuất gộp vào phiếu dọn lớp AI tiếp theo (LC-T034-1 có thể đi cùng T-031 vì cùng chủ đề link trần). Nên kiểm lại phiếu này bằng Fable sau 01/11 như các phiếu chạy Opus tạm khác.

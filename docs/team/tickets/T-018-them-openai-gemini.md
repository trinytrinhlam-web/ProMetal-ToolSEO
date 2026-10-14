# T-018 · Thêm AI ChatGPT (OpenAI) và Gemini (Google)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không |
| Trạng thái | Đã giao |

## Mục tiêu

Ngoài Claude, app viết bài được bằng ChatGPT (OpenAI) và Gemini (Google). Muốn đổi hãng cho một việc, chủ dự án chỉ cần sửa `provider` và `model` trong `config/ai.toml`, không phải sửa code. Nút **Kiểm tra** khóa ChatGPT và Gemini có hàm logic để gọi (giao diện làm ở T-023).

## Bối cảnh

- Chủ dự án **đã duyệt** (2026-10-14, trả lời trong chat) dùng thư viện chính hãng: `openai` và `google-genai`. Không thêm thư viện nào khác.
- Chủ dự án nói sẽ dùng **Gemini** là chính, có thể dùng cả ChatGPT và Claude.
- Đọc trước: `seo_app/ai/base.py` (giao diện `AIProvider`, `TaskConfig`, `redact_secrets`), `seo_app/ai/anthropic_provider.py` (làm mẫu: stream, xử lý lỗi, `pause_turn`), `seo_app/ai/registry.py`, `seo_app/env_file.py` (`check_api_key`), `seo_app/content/models.py` (các khuôn kết quả), `tests/test_ai.py`, `tests/fake_ai.py`.
- Bước nghiên cứu (`research`) dùng `web_search = true`. Các bước còn lại không tìm web.

## Phạm vi

- **Được sửa:** `seo_app/ai/**` (thêm `openai_provider.py`, `gemini_provider.py`), `seo_app/env_file.py` (phần kiểm tra khóa), `pyproject.toml`, `uv.lock`, test mới trong `tests/` cho phần mình làm.
- **Không được sửa:** `app/**` (giao diện thuộc Họa Sĩ, phiếu T-023), `config/**` (thuộc Ngòi Bút), `seo_app/config.py`, `.env.example` (đã có đủ biến `OPENAI_API_KEY`, `GEMINI_API_KEY`).
- **Ngoài phạm vi:** thử mù mô hình (T-019), tạo ảnh bằng AI (Giai đoạn 3), đổi mô hình mặc định trong `config/ai.toml`.

## Yêu cầu

1. Thêm thư viện bằng `uv add openai google-genai`. Ghi vào báo cáo: phiên bản, giấy phép, các thư viện phụ kéo theo mới vào `uv.lock`.
2. `OpenAIProvider` và `GeminiProvider` làm đúng giao diện `AIProvider.generate(task, *, system, prompt, schema)`: trả về đối tượng pydantic đúng khuôn `schema` (đã kiểm tra), dùng tính năng kết quả có khuôn (structured output) của từng hãng. Kết quả sai khuôn thì báo `AIError` tiếng Việt, như Anthropic.
3. `effort` (`low` … `max`) được đổi sang mức suy nghĩ tương ứng của từng hãng; ghi bảng quy đổi vào docstring. Mô hình không hỗ trợ suy nghĩ thì bỏ qua, không lỗi.
4. `web_search = true`: dùng công cụ tìm web chính hãng (OpenAI: web search; Gemini: Google Search grounding). Nếu hãng không cho dùng tìm web cùng lúc với kết quả có khuôn, phải có cách làm vẫn ra đúng khuôn `Research` (ví dụ tìm trước rồi định dạng ở lượt sau) và ghi rõ trong báo cáo. Không được âm thầm bỏ tìm web.
5. Lỗi: xử lý như `anthropic_provider.py`. Gồm: sai khóa, không có quyền, không có mô hình, giới hạn số lần gọi, mất mạng, hết tiền, bị từ chối vì an toàn, bài dài quá `max_tokens`. Mỗi lỗi ra một `AIError` tiếng Việt. **Không bao giờ** đưa khóa hay thông điệp thô chưa qua `redact_secrets` vào thông báo. Mọi lệnh gọi có timeout và giữ kiểm tra SSL.
6. `registry.py`: `SUPPORTED` gồm cả `openai`, `gemini`; `make_provider` tạo đúng provider. Thông báo thiếu khóa chỉ người dùng tới **Cài đặt → 🔌 Kết nối**.
7. `env_file.check_api_key` kiểm tra được `OPENAI_API_KEY` và `GEMINI_API_KEY`. Dùng lệnh rẻ nhất (danh sách mô hình), có timeout, không thử lại (`max_retries=0` hoặc tương đương). Kết quả `ok` / `invalid` / `unknown` như Claude, thông báo qua `redact_secrets`.
8. Tên mô hình: tra tài liệu chính thức của OpenAI và Google (tìm web) để biết tên mô hình hiện hành. Ghi vào báo cáo **đề xuất** `model` và `effort` cho từng việc (research, outline, write, rewrite, review) nếu chuyển sang Gemini hoặc ChatGPT. Không sửa `config/ai.toml`.
9. Test bằng client giả (không gọi mạng; `tests/conftest.py` đã chặn mạng) cho mỗi provider. Phải có: trả đúng khuôn, sai khuôn, từng loại lỗi ở mục 5, thông báo lỗi không chứa khóa giả, có `web_search` và không có, quy đổi `effort`, `check_api_key` của hai hãng.
10. Test cũ đang khẳng định "OpenAI/Gemini chưa hỗ trợ" thì sửa cho đúng hành vi mới. Liệt kê từng test đã sửa và lý do trong báo cáo. Không xóa, không `skip` test.

## Yêu cầu bảo mật riêng

S1, S2 (khóa không lọt vào lỗi, log, `repr` của provider), A1, A2 (AI không có công cụ nào ngoài tìm web), W4 (timeout, SSL), D1 (2 thư viện mới đã được duyệt; chạy `uvx pip-audit` sau khi thêm), D3.

## Tiêu chí xong

- [ ] Đổi `provider = "gemini"` (hoặc `"openai"`) với `model` hợp lệ trong `config/ai.toml` là app chạy được quy trình viết bài (chứng minh bằng test với client giả qua `ContentWriter`)
- [ ] `check_api_key` kiểm được khóa ChatGPT và Gemini
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Có test cho mọi nhánh logic mới
- [ ] Báo cáo nộp tại `docs/team/reports/T-018-tho-may.md`, có bảng đề xuất mô hình (mục 8)

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Thử kỹ: lỗi của thư viện chứa khóa hoặc URL có khóa (Gemini hay để khóa trong URL `?key=`), dữ liệu trả về rỗng/sai khuôn, tìm web cùng kết quả có khuôn.
- Lá Chắn: Có (thư viện mới, đụng tới bí mật).

## Ghi chú của Chỉ Huy

- Không commit, không chạy lệnh git làm đổi thư mục làm việc (R11): Ngòi Bút đang làm T-022 song song. Chỉ Huy commit sau khi qua Soi Lỗi và Lá Chắn.

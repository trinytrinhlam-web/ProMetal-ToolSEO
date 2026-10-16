# Báo cáo T-035 · README và chú thích `config/ai.toml`: 3 hãng AI, thử mù

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Sonnet 5.5 |
| Phiếu | [T-035](../tickets/T-035-readme-ai-3-hang-thu-mu.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

README mục 7 được viết lại cho đủ 3 hãng (Claude, ChatGPT, Gemini): lấy khóa ở đâu và có cần nạp tiền không, nhập và kiểm tra khóa trong app, đổi hãng/mô hình trong `config/ai.toml`, cách dùng thử mù, và bảng lỗi dùng đúng câu app hiện ra. Phần chú thích đầu `config/ai.toml` cũng sửa lại cho đúng (không còn câu "openai và gemini sẽ thêm sau"). Không đụng tới code, test hay giá trị cấu hình.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md` | Mục 7 chia 7.1–7.6 (khóa; đổi hãng/mô hình; thử mù; soạn bài; tùy chỉnh gồm nhãn `[CẦN XÁC NHẬN]`; bảng lỗi). Dòng "Trạng thái" đầu file và mục 5 (nhắc bấm Kiểm tra) cập nhật cho khớp |
| `config/ai.toml` | Chỉ dòng chú thích `#` (3 dòng cũ bị thay, thêm các dòng mới). `git diff`: không có dòng giá trị nào đổi; `tomllib` vẫn đọc được 5 việc |

## Bằng chứng

```
$ uv run pytest tests/test_app_pages.py tests/test_config_tolerance.py tests/test_ai_openai_gemini_soi_loi.py tests/test_ai_t028.py tests/test_content_edge_cases.py tests/test_settings_blind.py
455 passed in 26.11s

$ uv run ruff check .
All checks passed!
```

Các test này gồm mọi test có đọc `ai.toml` (`grep -rl "ai.toml" tests/`) cùng test trang và thử mù. Chưa chạy toàn bộ bộ test (phiếu chỉ sửa tài liệu và chú thích).

## Bảng đối chiếu câu lỗi trong README → code

| Câu trong README (rút gọn) | Nơi trong code |
|---|---|
| "Chưa có khóa {hãng} ({TÊN_BIẾN}). Vào Cài đặt → 🔌 Kết nối để nhập khóa." | `seo_app/ai/registry.py:93`; tên hãng `registry.py:14-18` |
| "Các bước dùng AI tạm khóa cho tới khi sửa xong." | `app/views/write.py:877` |
| "Khóa ANTHROPIC_API_KEY trong file .env không đúng." | `seo_app/ai/anthropic_provider.py:91` |
| "Khóa OPENAI_API_KEY … không đúng." | `seo_app/ai/openai_provider.py:106` |
| "Khóa GEMINI_API_KEY … không đúng." | `seo_app/ai/gemini_provider.py:235` |
| Nút Kiểm tra: "Khóa Claude/ChatGPT/Gemini không đúng hoặc đã bị thu hồi." | `seo_app/env_file.py:393`, `:435`, `:490` |
| Nút Kiểm tra: "Khóa … không có quyền truy cập …" | `env_file.py:395`, `:438`, `:493` |
| "Khóa … dùng được." | `env_file.py:412`, `:454`, `:510` |
| "Tài khoản Anthropic đã hết tiền (credit)." | `anthropic_provider.py:104` |
| "Tài khoản OpenAI đã hết tiền (credit) hoặc hết hạn mức." | `openai_provider.py:115` |
| "Tài khoản Gemini đã hết tiền hoặc hết hạn mức (quota) trong ngày." | `gemini_provider.py:242` |
| "Bài dài quá giới hạn (… token). Tăng max_tokens của việc «…» …" | `seo_app/ai/base.py:67` |
| "AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt …)" (Claude) | `anthropic_provider.py:57` |
| Thử mù: "Bài thử dài quá giới hạn 2000 token của phần thử mù …" | `seo_app/content/blind_test.py:51-55` (2000 = `BLIND_MAX_TOKENS`, `:35`) |
| "{Hãng} đang giới hạn số lần gọi. Đợi một phút rồi thử lại." | `anthropic_provider.py:99`, `openai_provider.py:116`, `gemini_provider.py:243` |
| "{Hãng} báo lỗi {mã}. Thử lại sau ít phút." | `anthropic_provider.py:108`, `openai_provider.py:128`, `gemini_provider.py:249` |
| "… trả lời quá lâu. Bấm thử lại." | `base.py:197`, `openai_provider.py:118`, `gemini_provider.py:155` |
| "Không có mô hình «…». Kiểm tra lại tên trong config/ai.toml." | `anthropic_provider.py:96`, `openai_provider.py:111`, `gemini_provider.py:239` |
| "Tài khoản … không được dùng mô hình «…»." | `anthropic_provider.py:93`, `openai_provider.py:108`, `gemini_provider.py:237` |
| "… không nhận yêu cầu (lỗi 400…) với mô hình «…». Kiểm tra tên mô hình và các thông số …" | `base.py:300` (lời khuyên `:295-298`) |
| "Gemini chưa phục vụ khu vực mạng bạn đang dùng (User location is not supported) …" | `gemini_provider.py:87-89` |
| "Không kết nối được tới … Kiểm tra mạng Internet." | `anthropic_provider.py:101`, `openai_provider.py:120`, `gemini_provider.py:167` |
| "Mất kết nối tới … giữa chừng …" | `base.py:116` |
| "Máy chủ … trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy) …" | `base.py:106` |
| "AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú." | `anthropic_provider.py:115`, `openai_provider.py:165`, `gemini_provider.py:80` |
| "Thư viện của … chưa cài hoặc sai phiên bản. Đóng app, chạy lại run.bat / run.command …" | `base.py:91-92` |

## Đối chiếu tính năng mô tả với code

| Điều README/ai.toml nói | Nơi trong code |
|---|---|
| Có 3 hãng `anthropic`, `openai`, `gemini` | `registry.py:14-18` |
| Gemini: `xhigh`, `max` tính là `high` | `gemini_provider.py:57-63` |
| Claude, ChatGPT dùng đúng mức effort | `anthropic_provider.py:81`, `openai_provider.py:89` |
| Mô hình không suy nghĩ thì bỏ qua effort | `openai_provider.py:98-104`, `gemini_provider.py:189-196` |
| Thử mù chọn 2–3 ứng viên | `blind_test.py:31-32`, `:225` |
| Báo trước số lần gọi, có tốn tiền | `app/views/settings.py:380` (`estimate_calls`, `blind_test.py:201`) |
| Bài hiện A/B/C ngẫu nhiên, chấm 1–10, bấm "Chấm xong — hiện tên mô hình" | `blind_test.py:311`; `settings.py:273`, `:411` |
| Thử mù không đọc/ghi `ai.toml`, không có `blind_test` trong file | `blind_test.py:48-50`, `:270` (`TaskConfig` dựng tại chỗ); `ai.toml` chỉ 5 việc |
| Nút Lưu / Kiểm tra / Xóa; Kiểm tra không tốn tiền | `settings.py:97`, `:105`, `:109` (`help=`: "không tốn tiền") |
| Link lấy khóa 3 hãng | `settings.py:15` (`API_KEY_FIELDS`) |
| Tên tab "🔌 Kết nối", "🤖 Mô hình AI" | `settings.py:437` |
| Nhãn `[CẦN XÁC NHẬN]` | Lấy nguyên văn từ ghi chú đầu `config/business_profile.md` (T-032) |

Tên mô hình ví dụ (`claude-opus-5-5`, `claude-sonnet-5-5`, `gpt-5.1`, `gemini-3-pro`) lấy từ `config/ai.toml`, `blind_test.py:239` và các test hiện có; không thêm tên mới.

## Đối chiếu tiêu chí xong

- [x] README mục 7 đúng với app hiện tại, đủ 3 hãng và thử mù (bảng trên)
- [x] Chú thích `config/ai.toml` đúng, giá trị không đổi (`git diff`: dòng bị xóa chỉ là 3 dòng `#`; `tomllib` đọc đủ 5 việc)
- [x] Báo cáo này
- [x] Không khóa thật hay khóa mẫu trông giống thật; không nêu giá tiền; không hướng dẫn tắt SSL hay đổi địa chỉ máy chủ

## Rủi ro và điểm cần chú ý

- Cột "Có cần nạp tiền không" của OpenAI và Gemini là hiểu biết chung về chính sách hãng (code chỉ biết Anthropic báo "credit"). Chính sách có thể đổi nên README hướng người dùng xem trang giá của hãng và không nêu con số. Chỉ Huy xem lại nếu muốn nói chắc hơn.
- Số dòng đã đối chiếu lại bằng `grep -n` sau khi viết xong.
- Nhãn "Cài đặt" trong app vẫn gắn `demo=True` ở đầu trang (`settings.py`), nên chủ dự án có thể thấy nhãn "Bản demo" dù các tab Kết nối và Mô hình AI chạy thật. README không đụng chuyện này.

## Đề xuất

- Sơ đồ thư mục ở cuối README (mục "Dành cho người phát triển") chưa liệt kê `seo_app/ai/`, `seo_app/content/`, `seo_app/storage`… Nên cập nhật khi đóng Giai đoạn 2 (ngoài phạm vi phiếu này).
- Gỡ `demo=True` ở trang Cài đặt nếu Họa Sĩ thấy hợp lý.

## Câu hỏi cho chủ dự án

Không có.

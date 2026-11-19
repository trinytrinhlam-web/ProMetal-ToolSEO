# T-148 · Loại lỗi AI, một lớp thử lại, đọc mục `[auto]` (phiếu G)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không. **Đợt 1**, song song T-142, T-143 và T-144 → T-153 (khác file). Làm từ `main` mới nhất (đã gộp T-138) |
| Trạng thái | Mới |

## Mục tiêu

Lượt chạy tự động cần biết một lỗi AI nên **chờ rồi thử lại** hay **dừng**, và cần là lớp thử lại **duy nhất**, để sổ đếm thấy đủ mọi request. Phiếu này:

- thêm loại lỗi `AIError.kind`;
- cho provider tạo được ở chế độ không tự thử lại;
- đọc mục `[auto]` (giãn nhịp, trần ngày);
- tính ngày theo giờ Thái Bình Dương (ngày Google đặt lại hạn mức).

## Bối cảnh

- Thiết kế T-141: 2.4 (bảng loại lỗi, giãn nhịp, sổ đếm), 6.3, 6.5, 7.2 dòng G.
- Biên bản Lá Chắn T-141 (`03568dc`): mục 4 (4) (hai lớp thử lại chồng nhau: `google-genai` 2.30.1 với `HttpRetryOptions(attempts=3)` tự gọi lại với 408, 429, 500, 502, 503, 504, lùi tới 60 s; sổ đếm không thấy), mục 8 dòng G.
- Tài liệu Google đọc 19/11: hạn mức theo project; số lần/ngày đặt lại lúc nửa đêm giờ Thái Bình Dương; **không** ghi trường nào phân biệt hạn mức theo phút và theo ngày.
- Mẫu `cfut_` của `redact_secrets` (LC-T140-2) chuyển từ phiếu A sang phiếu này vì cùng file `base.py`.

## Yêu cầu

1. **`AIError.kind`** (`seo_app/ai/base.py`): mặc định `"other"`; tập cố định `busy`, `rate`, `quota_day`, `network`, `timeout`, `auth`, `model`, `bad_request`, `shape`, `refusal`, `token_limit`, `other` (đúng tên bảng T-141 2.4; T-142 dùng cùng tên trên lớp lỗi Cloudflare). `TokenLimitError` có `kind = "token_limit"`. **Câu tiếng Việt và test cũ không đổi.**
2. **Phân loại ở 3 provider** (Gemini, OpenAI, Anthropic), chỉ từ `exc.code`, `exc.status` (số, chuỗi cố định), không từ chữ máy chủ (S2):
   - 500, 502, 503, 504 → `busy`; 429 → `rate`;
   - 401 → `auth`; 403 → như câu hiện có (không được dùng mô hình → `model`); 404 → `model`;
   - 400 → `bad_request` (khóa sai trả 400 → `auth`, như `_bad_key`);
   - lỗi mạng, quá giờ theo các hàm có sẵn của `base.py` → `network`, `timeout`;
   - khuôn hỏng → `shape`; bị chặn, từ chối → `refusal`.
3. **`quota_day`** (LC-T141-13):
   - 429 có các từ đã dùng trong mã hiện nay (`billing`, `credit`, `prepayment`) → `quota_day`;
   - đọc cấu trúc trong `exc.details` (`error.details[]` có `@type` QuotaFailure với `quotaId` chứa «PerDay», hay RetryInfo): viết hàm và test, nhưng **tắt bằng một hằng** cho tới khi Chỉ Huy chép được khuôn thật ở buổi thử (T-141 7.4.2). Tới đó mọi 429 khác là `rate`;
   - `retryDelay` của RetryInfo (khi đọc được) thành số giây, trần 120: `AIError.retry_after`;
   - không chép chữ máy chủ lên trang hay sổ việc.
4. **Một lớp thử lại** (LC-T141-12): mỗi provider nhận tùy chọn khi tạo để **không tự thử lại**: Gemini `HttpRetryOptions(attempts=1)`, OpenAI và Anthropic `max_retries=0`. Mặc định giữ như cũ cho các trang đang có. Việc nối tùy chọn vào `AIRouter` (`registry.py`) làm ở T-149, vì `registry.py` thuộc T-142 trong đợt 1.
5. **`seo_app/ai/limits.py` (mới):**
   - đọc mục `[auto]` của `config/ai.toml` chịu lỗi: thiếu mục, thiếu khóa → mặc định `min_seconds_between_calls = 6`, `gemini_requests_per_day = 0` (0 = chưa biết, không chặn). Đúng tên khóa T-144 ghi;
   - loại `bool`; giãn nhịp 1–120 giây; trần ngày 0–100.000;
   - câu lỗi tiếng Việt chỉ nêu `config/ai.toml` và `[auto]`, không đường dẫn đầy đủ;
   - `pacific_day(now)`: ngày theo `ZoneInfo("America/Los_Angeles")`, đúng giờ mùa hè; `reset_at_vn(now)`: giờ đặt lại để hiện cho người dùng;
   - hàm thuần tính số giây phải chờ trước lần gọi sau (không tự `sleep`).
6. **`redact_secrets`** thêm mẫu `cfut_[A-Za-z0-9_\-]{20,}` (LC-T140-2).
7. **Không phụ thuộc Streamlit** (LC-T141-9): các file của phiếu không import `streamlit`; provider dùng được trong `threading.Thread` thường.
8. **Test:**
   - từng nhánh phân loại của từng provider (lỗi giả có `code`, `status`); `TokenLimitError` có `kind`; 429 + `billing` → `quota_day`; 429 khác → `rate`; hàm đọc `details` có test nhưng đang tắt; `retry_after` có trần;
   - tùy chọn không thử lại cho đúng một request (đếm qua đường truyền giả); mặc định vẫn như cũ;
   - `[auto]` thiếu, sai dạng, `bool`, ngoài khoảng;
   - `pacific_day` qua hai mốc đổi giờ của Mỹ năm 2026; `redact_secrets` che `cfut_…`;
   - chạy lại test các câu lỗi AI có sẵn (T-026, T-028, `test_ai.py`…).

## Phạm vi

- **Được sửa:** `seo_app/ai/base.py`, `seo_app/ai/gemini_provider.py`, `seo_app/ai/openai_provider.py`, `seo_app/ai/anthropic_provider.py`, `seo_app/ai/limits.py` (mới), test mới `tests/test_t148_*.py`.
- **Không được sửa:** `seo_app/ai/registry.py` (T-142 trong đợt 1; nối router ở T-149), `seo_app/ai/__init__.py`, `config/ai.toml` (T-144 thêm `[auto]`), `seo_app/storage/**` (kho đếm của T-143), `app/**`.
- **Ngoài phạm vi:** ghi sổ đếm mỗi request (lượt chạy T-149 ghi vào kho của T-143), quyết thử lại (T-149).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

S2 (không chép chữ máy chủ, không lộ khóa), A2.

- **LC-T141-9** (không `streamlit`, dùng được trong luồng thường), **LC-T141-12** (một lớp thử lại: provider không tự thử lại khi lượt chạy yêu cầu; giữ hai lớp thì không chấp nhận), **LC-T141-13** (`kind` từ `code`, `status`; `quota_day` từ cấu trúc đã biết chỉ sau khi thấy khuôn thật; tới đó 429 là `rate`; không phân loại bằng chữ ngoài các từ đã có; `retryDelay` trần 120; câu tiếng Việt, test cũ không đổi).
- **LC-T140-2** (phần `redact_secrets`: mẫu `cfut_`).

## Tiêu chí xong

- [ ] Yêu cầu 1–8, có test.
- [ ] Test liên quan + test **mọi nơi gọi** lớp AI (các trang Soạn bài, Kế hoạch, Cài đặt, thử mù; test câu lỗi T-026, T-028, T-034) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-148-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (phân loại từng hãng, không thử lại, mốc ngày).
- Lá Chắn: **đầy đủ** (lớp AI).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-148`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật (lỗi máy chủ dựng giả).
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu G, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-148`, nhánh `team/T-148`.

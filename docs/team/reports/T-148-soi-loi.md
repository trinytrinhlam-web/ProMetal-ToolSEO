# Báo cáo T-148 · Loại lỗi AI, một lớp thử lại, đọc mục `[auto]` · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-148](../tickets/T-148-loai-loi-ai-mot-lop-thu-lai.md) · báo cáo Thợ Máy [`T-148-tho-may.md`](T-148-tho-may.md) · điều kiện Lá Chắn T-141 (LC-T141-9, -12, -13), T-140 (LC-T140-2), T-144 (LC-T144-4) |
| Nhánh | `team/T-148` đầu `1e29c45` (mã và test `1926247`, gốc `main` `ddcd23c`). Mọi lần chạy trên đúng mã này (worktree `wt-T-148`, hay bản sao `git archive` trong thư mục nháp của phiên) |
| Ngày nộp | 2026-11-20 (bắt đầu 13:57, xong 15:40, +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn (đầy đủ) được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T148-5: 429 thật của Gemini có chữ «billing» cả khi chỉ vượt hạn mức theo phút; lỗi ở đặc tả, mã làm đúng phiếu; **Chỉ Huy, Lá Chắn quyết trước T-149**), **4 Thấp** (SL-T148-1 → -4; SL-T148-3 lệch LC-T144-4, cần chốt). Trọng tâm (1) đúng: chế độ một lần gửi đúng 1 lệnh ở mọi lỗi thư viện vốn tự thử lại, cả 3 hãng, không ngủ; mặc định như cũ. (2) đúng trừ SL-T148-1, -5. (3) đúng: 109 cặp tình huống–hãng, câu cũ/mới giống từng byte, 0 chép lời máy chủ hay khóa; thiếu `cfat_`, `cfk_` (SL-T148-2). (4) ngày đặt lại đúng ở mọi thời điểm năm 2026; lệnh phụ của app (2 tới 5 lệnh) ghim cho T-149. (5) đúng. Đột biến: 35/35 bắt. Lô 119 file mọi nơi gọi: 11.791 qua, 0 hỏng. Gộp thử: 1 xung đột `registry.py` với T-142 (cách gỡ trùng bản Thợ Máy), cây gộp 1.719 qua |

## Tóm tắt (cho chủ dự án)

- **Chỉ còn một lớp thử lại, đúng như thiết kế.** Tôi dựng máy chủ AI giả trả đủ loại lỗi (máy chủ bận, gọi dày quá, quá giờ, rớt mạng…) và đếm từng lệnh gửi đi ở tầng thấp nhất:
  - chế độ dành cho lượt chạy tự động: **mỗi lần gọi đúng 1 lệnh**, ở cả 3 hãng, kể cả khi máy chủ bảo «thử lại đi»; không chờ giây nào;
  - các trang đang dùng: vẫn tự thử lại như cũ (Gemini 3 lệnh, OpenAI và Anthropic 4 lệnh).
- **Câu báo lỗi giữ nguyên từng chữ.** Tôi chạy song song mã cũ (trước phiếu) và mã mới với cùng 109 tình huống lỗi: câu báo giống hệt. Không câu nào chép lời máy chủ hay khóa.
- **Loại lỗi đúng** ở gần hết các tình huống; ngày Google đặt lại lượt miễn phí tính đúng (14:00 hay 15:00 giờ Việt Nam) ở mọi thời điểm năm 2026, kể cả hai ngày Mỹ đổi giờ.
- **1 lỗi mức Trung bình nằm ở chính yêu cầu của phiếu, cần Chỉ Huy quyết trước khi làm lượt chạy tự động (T-149):** khi Gemini miễn phí báo «gọi dày quá trong một phút», câu báo của Google có chữ «billing» (thanh toán). Phiếu dặn coi mọi lỗi có chữ đó là «hết lượt trong ngày», nên lượt chạy tự động sau này sẽ **dừng cả lô và hẹn 14:00/15:00**, trong khi Google chỉ bảo chờ vài giây. Hôm nay, ở trang Soạn bài, lỗi này cũng đang hiện câu «hết tiền hoặc hết hạn mức trong ngày» (sai nghĩa, có từ trước).
- **4 lỗi nhỏ (Thấp)**, không ảnh hưởng cách app đang chạy hôm nay (đang dùng Gemini):
  1. Với Claude, lỗi «máy chủ quá tải» đến giữa lúc đang nhận bài bị xếp nhầm loại, nên lượt chạy tự động sau này sẽ dừng bài thay vì chờ rồi thử lại.
  2. Bộ che mã bí mật chỉ nhận một trong ba dạng mã của Cloudflare (dạng tạo ở «My Profile»); hai dạng kia (mã của tài khoản, khóa tổng) không được che nếu lỡ lọt vào câu báo.
  3. Mục `[auto]` ghi sai giá trị thì app báo lỗi dừng, trong khi điều kiện mới của Lá Chắn (ra sau khi phiếu viết xong) muốn app dùng giá trị mặc định và chỉ cảnh báo. **Cần Chỉ Huy chốt theo bên nào.**
  4. Một con số dài bất thường (hàng trăm chữ số) trong `[auto]` làm app ra lỗi lạ thay vì câu báo tiếng Việt.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t148.py` | Mới: 122 ca. 104 qua; 16 `xfail(strict=True)` ghim SL-T148-1 → -5 (mục 8); 2 ca chỉ chạy khi đã gộp T-142 (trên nhánh này bỏ qua, trên cây gộp qua) |
| `docs/team/reports/T-148-soi-loi.md` | Báo cáo này |

Không sửa mã ứng dụng, không sửa test cũ.

## 1. Trọng tâm 1 — thật sự chỉ một lớp thử lại: đếm lệnh HTTP thật

**Cách đếm (khác cách của Thợ Máy):** Thợ Máy gắn đường truyền giả vào client (`http_client=`, `client_args=`). Tôi để thư viện của từng hãng tự dựng client mặc định với đúng tham số app truyền, chỉ thay **tầng cuối** `HTTPTransport.handle_request` của `httpx` (Gemini) và `httpx2` (OpenAI, Anthropic). Mọi lần gọi lại ở bất kỳ tầng nào phía trên (tenacity của google-genai, vòng thử lại của SDK, `x-should-retry`, `retry-after`) đều bị đếm. Socket bị chặn phòng có lệnh lọt ra mạng thật. `time.sleep` được thay, ghi lại số giây thư viện định chờ.

Kết quả (script `probe148.py`, 218 ca trên mã mới, 109 ca trên mã cũ `ddcd23c`; số lệnh mỗi lần `generate`, «thường / một lần»):

| Máy chủ giả trả | Gemini | OpenAI | Anthropic |
|---|---|---|---|
| 500, 502, 503, 504 | 3 / **1** | 4 / **1** | 4 / **1** |
| 408 | 3 / **1** | 4 / **1** | 4 / **1** |
| 429 | 3 / **1** | 4 / **1** | 4 / **1** |
| 529 | 1 / 1 | 4 / **1** | 4 / **1** |
| Quá giờ: đọc, nối, ghi, chờ chỗ (4 loại) | 3 / **1** | 4 / **1** | 4 / **1** |
| Không nối được mạng | 3 / **1** | 4 / **1** | 4 / **1** |
| Đứt giữa chừng (`RemoteProtocolError`, `ReadError`) | 1 / 1 | 4 / **1** | 4 / **1** |
| 409, 501, 520 | 1 / 1 | 4 / **1** | 4 / **1** |
| 400, 401 kèm `x-should-retry: true` | 1 / 1 | 4 / **1** | 4 / **1** |
| 429 kèm `retry-after: 30` | 3 / **1** | 4 / **1** | 4 / **1** |
| 400, 401, 403, 404, 413, 422; trả lời đúng; trang HTML | 1 / 1 | 1 / 1 | 1 / 1 |

- Chế độ một lần: **đúng 1 lệnh ở mọi ca lỗi mà thư viện vốn tự thử lại**; thư viện không ngủ giây nào ở cả 109 ca.
- google-genai 2.30.1 (`_api_client.retry_args`): mặc định tự thử lại mã 408, 429, 500, 502, 503, 504 **và** lỗi quá giờ, không nối được (`_HTTPX_TRANSIENT_EXC`); `attempts=1` là `stop_after_attempt(1)`. Không còn vòng thử lại nào khác cho `generate_content` (vòng `MAX_RETRY_COUNT` chỉ ở tải file lên, app không dùng).
- Chế độ thường: số lệnh, số lần ngủ của mã mới giống hệt mã cũ ở cả 109 ca.

**Lệnh phụ do chính app gửi** (không phải thư viện thử lại; chế độ một lần vẫn gửi): Gemini bỏ `thinking_config` khi 400 về thinking **2 lệnh**; Gemini đời 1.x, 2.x tìm web **2 lệnh**; OpenAI bỏ `reasoning` khi 400 về reasoning **2 lệnh**; Anthropic `pause_turn` **5 lệnh** (1 + `MAX_CONTINUATIONS` 4). Lệnh thứ hai cũng chỉ đi một lần (400 thinking rồi 503: 2 lệnh ở chế độ một lần, 4 ở chế độ thường). Đúng như mục «Ghi nhận» của Thợ Máy; tôi ghim các con số này bằng test để T-149 dựa vào (mục 9).

## 2. Trọng tâm 2 — loại lỗi, `retry_after`

| Tình huống | Loại | Đúng bảng T-141 2.4 / phiếu |
|---|---|---|
| 500, 502, 503, 504, 529; Gemini trạng thái `UNAVAILABLE`… | `busy` | Có |
| 429 thường; Gemini 429 «PerDay» khi `READ_QUOTA_DETAILS` tắt | `rate` | Có (tắt tới buổi thử, LC-T141-13) |
| Gemini 429 có `billing`/`credit`/`prepayment`; OpenAI `insufficient_quota`; Anthropic 400 «credit» | `quota_day` | Có |
| Gemini 429 **theo khuôn thật**: câu chung có «billing details», chi tiết ghi hạn mức **theo phút**, `retryDelay` 7 giây | `quota_day` | Đúng phiếu, **sai thực tế**: SL-T148-5 |
| 401; Gemini 400 `API_KEY_INVALID` | `auth` | Có |
| 403, 404 | `model` | Có |
| 400 | `bad_request` | Có |
| 408; quá giờ (mọi loại) | `timeout` | Có |
| Không nối được, đứt giữa chừng | `network` | Có |
| Mã 200 mà trang HTML, JSON hỏng | `shape` | Có |
| 409, 413, 422, 501, 520 | `other` | Có (ngoài bảng) |
| Anthropic: lỗi đến **giữa luồng SSE** (`overloaded_error`, `api_error`, `rate_limit_error`) | `other` | **Không**: SL-T148-1 |

- `retry_after`: chỉ có ở Gemini (RetryInfo, đang tắt). `clamp_retry_after` chặn 0–120; âm, `nan`, `inf`, `bool`, chữ ra `None`. Số nguyên rất lớn (`10**400`) ném `OverflowError` (SL-T148-4, chưa có đường nào đưa số như vậy vào: `duration_seconds` chỉ nhận tối đa 9 chữ số).
- **Không ngủ quá lâu:** ở chế độ một lần, thư viện không ngủ giây nào (mục 1). Ở chế độ thường (các trang đang có) thư viện Anthropic chờ đúng `retry-after` máy chủ gửi, không trần: 429 kèm `retry-after: 3600` → chờ 3 × 3600 = **10.800 giây**. Có từ trước, ngoài phạm vi phiếu (ghi nhận G-1, mục 9).

## 3. Trọng tâm 3 — câu tiếng Việt giữ nguyên, không chép lời máy chủ, che khóa

- **So từng byte với mã cũ:** cùng máy chủ giả, cùng 109 tình huống, chạy mã `git archive ddcd23c` và mã mới: câu báo, lớp lỗi, lớp lỗi gốc (`__cause__`), số lệnh, kết quả **giống hệt** (0 khác). Ở chế độ một lần, câu và loại giống chế độ thường (0 khác).
- **Không chép lời máy chủ, không lộ khóa:** mọi thân trả lời giả mang chuỗi đánh dấu và khóa giả: 0 câu báo trong 218 ca có hai chuỗi đó.
- **Mẫu `cfut_`:** che được ở câu thường, trong JSON, trong đường dẫn, dính chữ phía trước, sau `=`. Thiếu hai tiền tố còn lại của Cloudflare (SL-T148-2).

## 4. Trọng tâm 4 — sổ đếm, ngày đặt lại hạn mức

- **Sổ đếm** chưa có ở phiếu này (T-149 ghi vào kho của T-143). Phần T-148 phải lo, «sổ đếm thấy đủ request», đúng ở tầng thư viện: chế độ một lần không còn lệnh ẩn. Còn lệnh phụ của chính app (mục 1): sổ đếm theo lần gọi `generate` sẽ đếm thiếu 1 (thinking, reasoning, tìm web 2 lượt) tới 4 (`pause_turn`). Với cấu hình hiện tại (`gemini-3.8-flash`, tắt tìm web) chỉ còn ca thinking. Ghi nhận G-2 cho T-149.
- **Ngày đặt lại:** kiểm mọi thời điểm năm 2026, bước 15 phút (35.040 thời điểm, gồm 08/03 và 01/11): lần đặt lại kế tiếp luôn là nửa đêm Los Angeles ngay sau đó, đúng 14:00 hoặc 15:00 giờ Việt Nam, sau thời điểm đang xét và cách không quá 25 giờ; `pacific_day` của lúc đặt lại là ngày hôm sau, một micro giây trước đó vẫn là hôm nay. Thêm 8 ca tay quanh hai ngày đổi giờ (ví dụ 08/03 15:00 → lần sau 09/03 14:00; 01/11 14:00 → lần sau 02/11 15:00).
- `seconds_to_wait`: 5.000 bộ số ngẫu nhiên (kể cả giờ chạy ngược): luôn trong `[0, min_seconds]`, đúng bằng phần còn thiếu khi giờ không ngược. `daily_limit_reached`: trần 0 không chặn.
- **`[auto]`:** đọc đúng tên khóa T-144 ghi; cây gộp có `[auto]` thật của T-144 đọc ra (6, 0). Lệch điều kiện **LC-T144-4** (Lá Chắn T-144, 20/11 13:31, sau khi mã T-148 viết xong 19/11): SL-T148-3.

## 5. Trọng tâm 5 — không nới lớp bảo vệ cũ

- Đặt `ANTHROPIC_BASE_URL`, `OPENAI_BASE_URL`, `GOOGLE_GEMINI_BASE_URL`, `GOOGLE_VERTEX_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS`, `OPENAI_CUSTOM_HEADERS`, `GOOGLE_GENAI_CLIENT_MODE=replay` (kèm thư mục, mã phát lại), `GOOGLE_GENAI_USE_VERTEXAI=true`, rồi gọi cả 3 hãng ở **cả hai chế độ**: lệnh chỉ tới 3 địa chỉ chính thức, không header lạ, thư mục phát lại không có file nào; tên header ở chế độ một lần giống hệt chế độ thường.
- `make_provider(..., single_attempt=True)` vẫn trong khối bắt lỗi thư viện lệch phiên bản (T-026); `ignoring_custom_headers()` (T-028, T-034) và `no_debug_config()` vẫn bọc cả hai nhánh.
- Test câu lỗi, lớp bảo vệ có sẵn (T-026, T-028, T-034, `test_ai.py`, `test_ai_openai_gemini*`, Soi Lỗi T-019, T-026, T-028, T-034) chạy trong lô 119 file mọi nơi gọi lớp AI: **11.791 qua, 0 hỏng** (mục 11).

## 6. Gộp thử với nhánh chờ gộp

| Gộp `team/T-148` (`1e29c45`) với | Kết quả `git merge-tree` |
|---|---|
| `team/T-142` (`a9ee007`: lượt 2 `ab6b524` + biên bản Lá Chắn; đã chứa `int/T-137-138`) | **1 xung đột: `seo_app/ai/registry.py`**, đúng một khúc: T-142 thêm `image_steps`, `provider_label` ngay trên dòng `def make_provider(...)` mà T-148 thêm `single_attempt` |
| `int/T-137-138` (`f6ec79b`) | Không xung đột |
| `team/T-144` (`4b8fe56`, có `[auto]` trong `config/ai.toml`) | Không xung đột |
| `team/T-143` | Đã nằm trong `main` |

- **Cách gỡ:** giữ hai hàm của T-142, dòng chữ ký bản T-148. Tôi tự gỡ bằng script (không nhìn file của Thợ Máy): ra **đúng từng byte** file `T-148-registry-gop-T-142.py` Thợ Máy để ở thư mục ghi chú chung. Thân `make_provider` sau gộp: chặn `cloudflare` của T-142 đứng trước dòng `return cls(..., single_attempt=True)` của T-148, nên `make_provider("cloudflare", …, single_attempt=True)` vẫn bị chặn (ca của Soi Lỗi).
- **Cây gộp đủ** (`git commit-tree` trên cây đã gỡ, không đụng worktree hay nhánh nào, không push): T-148 + T-142 `a9ee007` + T-144 `4b8fe56`, bản sao `git archive` trong thư mục nháp:
  - `ruff check .` sạch;
  - 17 file (3 file T-148, file Soi Lỗi T-148, 3 file T-142 và Soi Lỗi T-142, 2 file T-144, `test_ai.py`, `test_ai_images.py`, `test_ai_openai_gemini*.py`, `test_ai_t026/t028/t034.py`): **1.719 qua, 15 xfail, 0 hỏng, 0 bỏ qua**. 15 xfail là ca ghim SL-T148-1 → -4 (file Soi Lỗi bản trước khi thêm ca SL-T148-5; chạy lại bản cuối trên cây gộp: 106 qua, 16 xfail); 2 ca chờ gộp T-142 của Soi Lỗi (lớp lỗi Cloudflare dùng đúng bảng tên loại, `cloudflare` vẫn bị chặn ở chế độ một lần) chạy và qua.
- Lớp lỗi Cloudflare của T-142 (`CloudflareImageError`) đặt `self.kind` thẳng, không qua kiểm tên của `AIError.__init__`; mọi hằng `KIND_*` đều nằm trong `AI_ERROR_KINDS` (ca Soi Lỗi). Ghi nhận G-4.

## 7. Đột biến các chốt chính

`mutate148.py`, bản sao `git archive 1e29c45` kèm file Soi Lỗi (bản 121 ca, trước khi thêm ca SL-T148-5); mỗi đột biến sửa một chỗ, chạy 4 file (3 file T-148 và file Soi Lỗi), trả file; chỉ tính «bắt» khi có ca `failed`, không ca nào lỗi dựng; cuối lượt mọi file `.py` của bản sao khớp SHA-256 ban đầu.

- Bản gốc: 336 qua, 2 bỏ qua, 15 xfail.
- **35 đột biến, 35 bị bắt**, 0 sống:
  - `base.py` (9): mẫu `cfut_` chỉ che khi ≥ 40 ký tự; `retry_after` nhận số âm; bỏ trần 120; 502 không còn `busy`; 408 thành `busy`; đứt mạng khi đọc thành `timeout`; bỏ kiểm tên loại; loại mặc định `shape`; `TokenLimitError` loại `shape`;
  - Gemini (7): bỏ qua `single_attempt`; một lần thành 2 lần; bỏ dò trạng thái chuỗi bận; quá giờ thành `network`; bật đọc chi tiết 429; khóa sai trả 400 thành `bad_request`; bị chặn ở prompt thành `shape`;
  - OpenAI (3), Anthropic (4): bỏ qua `single_attempt` / một lần thành 2 lần; quá giờ thành `network`; mã lạ đều `busy`; `pause_turn` thành `shape`; `pause_turn` đọc tiếp thêm một lượt (6 lệnh);
  - `registry.py` (3): `make_provider` bỏ qua `single_attempt`; router bỏ qua; router luôn tắt;
  - `limits.py` (9): ngày theo giờ Việt Nam; nửa đêm theo giờ Việt Nam; giờ ngược chờ quá một nhịp; trần ngày cho thêm một lần; nhận giãn nhịp 0 giây; đọc sai tên mục; giờ đặt lại là nửa đêm đã qua; nhận giờ không múi giờ; **giờ Thái Bình Dương cố định UTC-8, bỏ giờ mùa hè**.
- **Chỉ ca Soi Lỗi bắt:** `pause_turn` đọc tiếp thêm một lượt (ca ghim lệnh phụ). Ca Soi Lỗi bắt thêm (cùng ca Thợ Máy) ở 20 đột biến khác, nhiều nhất ở các chốt một lần (`make_provider` 53 ca, OpenAI 22, Anthropic 21, Gemini 12).

## 8. Lỗi mới

| Mã | Mức | Lỗi | Cách thấy | Gợi ý sửa |
|---|---|---|---|---|
| **SL-T148-5** | **Trung bình** · lỗi ở đặc tả, **cần Chỉ Huy, Lá Chắn quyết trước T-149** | Lỗi 429 thật của Gemini có chữ «billing» **cả khi chỉ vượt hạn mức theo phút**. Bài người dùng dán trên diễn đàn Google AI (04/12/2025, thread 111105): câu «You exceeded your current quota, please check your plan and billing details», cùng lỗi đó có `quotaId` `GenerateRequestsPerMinutePerProjectPerModel-FreeTier` và `retryDelay` `"7s"` (bài 06/08/2025, thread 96899: cùng câu với hạn mức theo ngày). Phiếu (yêu cầu 3) và LC-T141-13 bảo «429 có `billing` → `quota_day`», Thợ Máy làm đúng như vậy. Hệ quả ở T-149: vượt giới hạn theo phút (số lần hay **số token mỗi phút**, dễ chạm khi viết bài dài) → `quota_day` → **dừng cả lô**, báo giờ đặt lại 14:00/15:00, trong khi chỉ cần chờ vài giây. Câu báo hiện nay cho lỗi này («hết tiền hoặc hết hạn mức trong ngày») cũng sai nghĩa (có từ trước, ở mọi trang). Nhánh «billing» trả lỗi trước khi xét chi tiết, nên dù bật `READ_QUOTA_DETAILS` vẫn ra `quota_day`, không có `retry_after` | Máy chủ giả trả đúng khuôn trên | Chỉ Huy, Lá Chắn chọn: (a) bỏ dò chữ `billing` ở Gemini (mọi 429 là `rate` tới khi đọc chi tiết); (b) có `QuotaFailure` trong chi tiết thì không dò chữ; (c) bật đọc chi tiết ngay (khuôn ở diễn đàn khớp đúng khuôn `quota_details` của T-148 đang chờ: `quotaId` có «PerMinute»/«PerDay», `retryDelay` dạng «7s»), xét chi tiết **trước** chữ. Buổi thử thật vẫn nên chép lại khuôn (T-141 7.4.2) |
| **SL-T148-1** | Thấp | Anthropic: lỗi đến **giữa luồng SSE** sau mã 200 (`event: error`, `overloaded_error`, `api_error`, `rate_limit_error`) ra loại `other` thay vì `busy`/`rate`. SDK `anthropic` 1.13.0 dựng `APIStatusError` với `status_code` 200 (`_make_status_error` chỉ xét mã HTTP), nên `status_kind(200)` = `other`. App luôn gọi Claude bằng luồng, và «quá tải» giữa luồng là cách Anthropic hay báo khi bận: lượt chạy tự động sẽ dừng bài thay vì chờ 30 giây rồi thử lại. Câu báo («Anthropic báo lỗi 200…») có từ trước, không đổi. Hôm nay app dùng Gemini nên chưa gặp | Máy chủ giả trả luồng SSE có `event: error` | Ở nhánh `APIStatusError`, khi `status_code` không phải mã lỗi (200), đọc loại cố định `error.type` (đã có `_error_type`): `overloaded_error`, `api_error` → `busy`; `rate_limit_error` → `rate`; giữ câu cũ. Đây là chuỗi cố định như trạng thái `UNAVAILABLE` của Gemini mà phiếu cho dùng |
| **SL-T148-2** | Thấp | Mẫu che chỉ có `cfut_`. Trang chính thức của Cloudflare (token formats, đọc 20/11) có ba tiền tố: `cfk_` (Global API Key), `cfut_` (token của người dùng), `cfat_` (token của tài khoản, «dùng cho tích hợp lâu dài», có Workers AI trong bảng tương thích), mỗi tiền tố theo sau 40 ký tự và mã kiểm. `.env.example` của T-142 dặn tạo ở My Profile (ra `cfut_`), nhưng nếu chủ dự án tạo token của tài khoản, app vẫn nhận (T-142 chỉ kiểm 20–256 ký tự) mà `redact_secrets` không che khi mã lọt vào câu báo không kèm chữ «token»/«Bearer». Phiếu, LC-T140-2 chỉ ghi `cfut_` (thiếu ở đặc tả, không phải Thợ Máy làm sai) | `redact_secrets("… cfat_<40 ký tự><mã kiểm>")` | `cf(?:ut\|at\|k)_[A-Za-z0-9_\-]{20,}`; Lá Chắn xác nhận cập nhật LC-T140-2 |
| **SL-T148-3** | Thấp · **cần Chỉ Huy chốt** | Lệch **LC-T144-4** (Lá Chắn T-144, `4b8fe56`, 20/11 13:31, ra sau khi mã T-148 viết xong 19/11; báo cáo Thợ Máy không nhắc): (a) LC-T144-4 đòi giá trị `[auto]` sai (chữ, âm, quá lớn) thì **dùng 6 và 0**, câu báo cố định, app không sập; mã hiện **ném `AIError` dừng** (theo phiếu, yêu cầu 5); (b) khoảng giây: LC-T144-4 «0–600», phiếu và mã «1–120» (0 và 121–600 hiện bị từ chối); (c) câu lỗi cú pháp TOML kèm lời của `tomllib`, có thể chép tên khóa hay một ký tự trong file («Cannot declare … twice», «Found invalid character …»), trong khi LC-T144-4 ghi «không chép chữ file» (giống `load_ai_config` có từ trước). Mã hiện không làm sập trang nào (chưa ai gọi), nhưng T-149, T-146 sẽ phải tự bắt lỗi | Đọc biên bản T-144 trên `team/T-144`; 8 ca giá trị sai (sai ở cả hai đặc tả) | Chỉ Huy chốt theo LC-T144-4 hay theo phiếu. Theo LC-T144-4 thì `load_auto_limits` trả mặc định kèm một câu cảnh báo cố định (ví dụ thêm trường cảnh báo), và test cũ `test_bad_*_give_clear_error` đổi kỳ vọng theo R5 |
| **SL-T148-4** | Thấp | Số nguyên rất lớn làm lỗi lạ thay vì câu tiếng Việt: `math.isfinite(10**400)` ném `OverflowError`. (a) `[auto]` `min_seconds_between_calls = 1000…0` (401 chữ số; `tomllib` nhận số nguyên dài) → `load_auto_limits` ném `OverflowError`, không phải `AIError`; (b) `clamp_retry_after(10**400)` và `AIError(…, retry_after=10**400)` ném `OverflowError` (dựng lỗi để báo lỗi cũng hỏng). Hôm nay chưa đường nào đưa số như vậy vào `retry_after` | Ca tay | So sánh khoảng trước rồi mới `isfinite`, hoặc bắt `OverflowError` (chặn trần 120 / câu báo `[auto]`) |

Nguồn (đọc 20/11/2026):
- SL-T148-5: https://discuss.ai.google.dev/t/gemini-flash-image-gemini-2-5-flash-image-no-longer-working-rpm-limit-errors/111105 (câu có «billing» cùng `quotaId` theo phút, theo ngày, `retryDelay` "7s"); https://discuss.ai.google.dev/t/429-errors-despite-waiting-after-retrydelay/96899 (cùng câu, hạn mức theo ngày, `retryDelay` "1s"). Đây là lỗi người dùng dán lại, chưa phải khuôn Chỉ Huy chép ở buổi thử.
- SL-T148-2: https://developers.cloudflare.com/fundamentals/api/get-started/token-formats/ (bảng `cfk_`, `cfut_`, `cfat_`; «40 characters and a checksum»); https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/ (token tài khoản cho tích hợp lâu dài; Workers AI dùng được).

## 9. Ghi nhận (không chặn)

- **G-1 (có từ trước, chế độ thường, ngoài phạm vi):** thư viện `anthropic` 1.13.0 chờ đúng `retry-after` máy chủ gửi, chỉ chặn ở 4.294.967 giây: 429 kèm `retry-after: 3600` → trang chờ 3 × 3600 = 10.800 giây trước khi báo lỗi. `openai` 3.31.0 chỉ nghe tới 120 giây (quá thì thôi thử lại); google-genai không đọc header này. Chế độ một lần của T-148 không bị (0 giây). Hôm nay app dùng Gemini cho mọi việc. Nếu quay lại Claude, nên có phiếu chặn trần (Lá Chắn xem).
- **G-2 (cho T-149, LC-T141-12):** lệnh phụ của chính app (mục 1): sổ đếm theo lần gọi `generate` đếm thiếu 1 (thinking, reasoning, tìm web 2 lượt) tới 4 (`pause_turn`). Hạn mức ngày của Google tính theo lệnh, nên trần trong `[auto]` có thể bị vượt đúng chừng đó; lỗi 429 của máy chủ vẫn là chốt cuối. Muốn đếm đúng từng lệnh thì cần móc «trước mỗi request» ở provider (như Thợ Máy đề xuất). Test `test_request_phu_cua_app_dung_so_da_ghi` ghim các con số để T-149 dựa vào.
- **G-3 (cho T-149):** `retry_after` chỉ có ở Gemini (đang tắt): lỗi `rate` của OpenAI, Anthropic luôn chờ 60 giây mặc định dù máy chủ có gửi `retry-after` (phiếu không đòi đọc). `pause_turn` hết lượt là `timeout`: bảng 2.4 cho thử lại 1 lần sau 30 giây, tức tới 10 lệnh Claude (có tìm web, tốn tiền) cho một bước.
- **G-4 (lúc gộp T-142):** `CloudflareImageError.__init__` gọi `super().__init__(message)` rồi đặt `self.kind = kind`, nên tên loại không qua kiểm của `AIError`. Hôm nay mọi `KIND_*` đúng bảng (ca Soi Lỗi bắt nếu sai). Sau khi gộp, nếu đổi thành `super().__init__(message, kind=kind)` thì gõ sai tên bị chặn ngay lúc dựng lỗi.
- **G-5:** `registry.py` nằm trong danh sách «không được sửa» của phiếu; Thợ Máy sửa theo lời giao thêm của Chỉ Huy B ngày 19/11 (ghi ở báo cáo Thợ Máy). Chính phần này gây xung đột với T-142 (mục 6).

## 10. Test của Soi Lỗi (`tests/test_soi_loi_t148.py`, 122 ca)

| Nhóm | Ca | Kết quả |
|---|---|---|
| Một lần: đúng 1 lệnh ở tầng `HTTPTransport` (12 lỗi × 3 hãng), không ngủ, đúng loại | 36 | Qua |
| Một lần: không nghe `x-should-retry`, `retry-after`, `retry-after-ms` (4 mã × 3 header × OpenAI, Anthropic) | 24 | Qua |
| Chế độ thường: số lệnh, số lần ngủ như cũ (5 lỗi × 3 hãng) | 15 | Qua |
| Thành công 1 lệnh; router cả 3 hãng ở hai chế độ | 3 | Qua |
| Lệnh phụ của app (thinking, tìm web 2 lượt, reasoning, `pause_turn`) | 4 | Qua |
| Biến môi trường đổi đường gọi, chèn header, chế độ phát lại (3 hãng × 2 chế độ) | 6 | Qua |
| SL-T148-1: lỗi giữa luồng SSE đúng loại | 3 | xfail strict |
| Lỗi giữa luồng SSE: câu cũ, 1 lệnh, không chép lời máy chủ | 1 | Qua |
| SL-T148-5: Gemini 429 khuôn thật, hạn mức theo phút → `rate` | 1 | xfail strict |
| `cfut_` ở 5 vị trí; SL-T148-2 (`cfat_`, `cfk_`) | 5 + 2 | Qua; xfail strict |
| Ngày đặt lại cả năm 2026 bước 15 phút; 8 ca hai ngày đổi giờ; `seconds_to_wait` 5.000 bộ số | 1 + 8 + 1 | Qua |
| SL-T148-3: 8 giá trị `[auto]` sai → mặc định (LC-T144-4) | 8 | xfail strict |
| SL-T148-4: số nguyên rất lớn ở `[auto]`, `retry_after` | 2 | xfail strict |
| Chờ gộp T-142: `KIND_*` của Cloudflare trong bảng tên; `cloudflare` bị chặn ở chế độ một lần | 2 | Bỏ qua trên nhánh; qua trên cây gộp |

Sửa xong lỗi nào thì ca xfail của lỗi đó báo XPASS (strict), phải bỏ dấu xfail. Nếu Chỉ Huy chốt SL-T148-3 theo phiếu (giữ báo lỗi), xóa 8 ca của SL-T148-3.

## 11. Lệnh đã chạy

```text
# Windows 11, Python 3.12.15, venv của wt-T-148 (anthropic 1.13.0, openai 3.31.0, google-genai
# 2.30.1, httpx 0.28.1, httpx2 2.13.1). Không gọi AI, Cloudflare, Google, WordPress thật: tầng
# HTTPTransport bị thay, socket bị chặn (script), bộ chặn mạng của conftest bật (pytest).

# Đếm lệnh, loại, câu (probe148.py; bản sao git archive HEAD và git archive ddcd23c)
python probe148.py <HEAD> new new.json new   → 218 ca (109 cặp tình huống–hãng × 2 chế độ)
python probe148.py <ddcd23c> old old.json old → 109 ca (chế độ thường)
python report148.py                           → 0 khác câu, lớp lỗi, số lệnh, số lần ngủ giữa cũ
                                                 và mới; 0 khác câu, loại giữa hai chế độ; 0 câu
                                                 có chữ máy chủ hay khóa; 0 lệnh ngoài 3 địa chỉ
# Biến môi trường (probe_env148.py, 3 hãng × 2 chế độ): 3 địa chỉ chính thức, 0 header lạ,
#   thư mục phát lại rỗng, tên header hai chế độ giống hệt

# File của Soi Lỗi (worktree)
uv run pytest -q -p no:randomly tests/test_soi_loi_t148.py
  104 passed, 2 skipped, 16 xfailed
uv run ruff check tests/test_soi_loi_t148.py; ruff format --check → sạch

# Gộp thử (git merge-tree; cây đã gỡ dựng bằng git commit-tree, không push, không đụng worktree)
T-148 + team/T-142 a9ee007  → 1 xung đột seo_app/ai/registry.py (gỡ: trùng từng byte file Thợ Máy)
T-148 + int/T-137-138 f6ec79b, + team/T-144 4b8fe56 → không xung đột
Cây T-148 + T-142 + T-144 (git archive vào thư mục nháp):
  ruff check .                                   → All checks passed!
  pytest 17 file (mục 6)                         → 1719 passed, 15 xfailed in 263.06s
  pytest tests/test_soi_loi_t148.py (bản cuối)   → 106 passed, 16 xfailed

# Đột biến (mutate148.py, bản sao git archive 1e29c45 + file Soi Lỗi 121 ca)
  gốc: 336 passed, 2 skipped, 15 xfailed; 35 đột biến: 35 bắt (failed), 0 sống, 0 lỗi dựng
  sha256sum mọi file .py của bản sao trước/sau: khớp

# Lô mọi nơi gọi (worktree, 4 lô, mỗi lô một file log, móc kiểm data/ audit_data): 119 file test
#   nhắc seo_app.ai, AIRouter, make_provider, AIError, redact_secrets, TokenLimitError, AI giả hay
#   mở trang bằng AppTest: 3 file T-148, file Soi Lỗi, test_ai.py, test_ai_openai_gemini*,
#   test_ai_t026/t028/t034, test_soi_loi_t019/t026/t028/t034, test_app_pages, test_blind_test,
#   test_settings_blind, test_t101_*…
uv run pytest -q -p no:randomly -p audit_data <lô>
  lô 1 (30 file): 3455 passed, 1 skipped, 2 xfailed, 1 warning in 1228.36s (0:20:28)
  lô 2 (30 file): 2078 passed, 9 skipped, 16 xfailed in 1249.45s (0:20:49)
  lô 3 (30 file): 4231 passed, 1 skipped, 4 xfailed in 841.91s (0:14:01)
  lô 4 (29 file): 2027 passed, 1 xfailed in 1391.29s (0:23:11)
  cộng: 11791 passed, 11 skipped, 23 xfailed, 0 failed, 0 error
#   23 xfailed: 16 ca ghim của Soi Lỗi T-148, 7 có từ trước (như báo cáo Thợ Máy).
#   11 skipped: 2 ca chờ gộp T-142 của Soi Lỗi, 9 có từ trước.
#   1 warning: Pydantic, ca test_soi_loi_t028 cố ý đưa luồng trả lời hỏng (có từ trước).
#   Móc kiểm data/: 15 lần, đều tests/test_la_chan_t102.py mở data/site_index.sqlite của worktree
#   (nhánh tách từ ddcd23c, trước fixture của T-138); giờ sửa file vẫn 19/11 13:45 trước và sau
#   lượt; không đụng thư mục app. git status sau lượt: chỉ 2 file mới của Soi Lỗi.

# Ký tự ẩn (Cf), CR, NFC trong 2 file của Soi Lỗi: 0, 0, NFC
# detect-secrets (uvx, PYTHONUTF8=1, bản sao ngoài git kèm file mồi tiếng Việt): chỉ file mồi
#   bị báo (AWS Access Key giả), 2 file của Soi Lỗi sạch
```

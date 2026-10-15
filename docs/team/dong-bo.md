# Phiếu điều phối chung (2 Chỉ Huy)

Dự án có **hai Chỉ Huy** chạy ở **hai tài khoản Claude khác nhau**. Họ **không chạy cùng lúc**: Chỉ Huy kia chỉ làm khi Chỉ Huy này dừng, và một phiên thường chỉ dừng khi **hết lượt dùng**, tức là dừng bất ngờ, không kịp dặn lại. Hai bên chỉ liên lạc với nhau qua file này (chủ dự án chốt 2026-10-15).

Đọc file này **trước mọi việc khác**, ngay sau `git pull`.

## Hai Chỉ Huy

| Tên trong file này | Ở đâu |
|---|---|
| **Chỉ Huy A** | Claude Desktop (Code) trên máy chủ dự án, thư mục `D:\ProMetal-ToolSEO\ProMetal-ToolSEO` |
| **Chỉ Huy B** | Tài khoản Claude thứ hai của chủ dự án. Phiên "Điều phối" trên Claude Code cloud (claude.ai/code), các agent là phiên con dưới nó |

Nếu bạn là Chỉ Huy mới và không chắc mình là A hay B, hỏi chủ dự án rồi ghi vào bảng trên.

## Quy tắc

1. **Đầu phiên:** `git pull`, đọc mục "Đang giữ quyền điều phối" và nhật ký bàn giao mới nhất. Rồi ghi tên mình vào mục "Đang giữ quyền", **commit và push ngay** trước khi làm việc khác.
   - Push bị từ chối nghĩa là bên kia vừa đẩy gì đó lên: `git pull`, đọc lại file này, rồi mới quyết định làm tiếp.
2. **Trong phiên, việc nhỏ, đẩy thường xuyên.** Phiên có thể dừng bất cứ lúc nào, nên sau **mỗi bước có ý nghĩa** (giao phiếu, nhận báo cáo, gộp nhánh, trả lời chủ dự án) thì cập nhật mục "Đang làm dở", rồi commit và push. Không bao giờ để việc nằm trên máy mà chưa đẩy lên.
3. **Không làm lại việc bên kia đang làm dở.** Đọc "Đang làm dở" của bên kia, đối chiếu `git log`, `git branch -r` và `docs/team/board.md` để biết họ dừng ở bước nào, rồi làm **tiếp** từ đó. Thấy chỗ nào không khớp thì ghi vào nhật ký, không tự đoán.
4. **Cuối phiên** (nếu kịp): viết một mục bàn giao ở đầu nhật ký. Đổi mục "Đang giữ quyền" thành "Không ai giữ". Commit và push.
5. **Bên kia dừng mà không bàn giao:** coi mục "Đang làm dở" của họ là trạng thái mới nhất. Ghi "Tiếp quản từ <A/B> lúc <giờ>, không có bàn giao" vào nhật ký.
6. **Quyết định của chủ dự án** mà một bên nhận được phải ghi ngay vào nhật ký **và** vào chỗ gốc (`CLAUDE.md`, `TIEN-DO.md`, `BAN-GIAO.md` mục 7), để bên kia không hỏi lại.
7. File này chỉ dùng để phối hợp hai Chỉ Huy. Việc của từng agent vẫn ghi ở `board.md`, phiếu và báo cáo như cũ.

Giờ ghi theo giờ Việt Nam (`Asia/Ho_Chi_Minh`), dạng `2026-10-15 11:00`.

## Đang giữ quyền điều phối

**Chỉ Huy B**, nhận lúc 2026-10-15 18:02 (chủ dự án: "tiếp tục từ chỗ đã dừng").

## Đang làm dở

_Bên đang giữ quyền cập nhật mục này sau mỗi bước._

Chỉ Huy B, cập nhật 2026-10-15 18:37. Chủ dự án dặn chạy tự động tới khi hết hạn mức, không hỏi lại. Agent là phiên con dưới phiên "Điều phối" của B trên cloud; mọi việc đẩy lên nhánh.

| Phiếu | Nhánh | Đang ở bước | Việc tiếp theo |
|---|---|---|---|
| [T-019](tickets/T-019-thu-mu-mo-hinh.md) Thử mù mô hình | `team/T-019` (`94a2813`) | Thợ Máy lượt 2 xong (Linux 3.222 qua). Chỉ Huy B chấp nhận commit `4223a8c` sửa `seo_app/ai/` (ghi trong phiếu). Soi Lỗi đang kiểm lại | Soi Lỗi kiểm lại (có đụng `seo_app/ai/`), rồi Lá Chắn (A1, U1, S2), ĐẠT thì gộp |
| [T-025](tickets/T-025-on-dinh-test-do-toc-do.md) Test đo tốc độ | `team/T-025` (`a36a943`) | Soi Lỗi xong (0/1.000 lần hỏng, Linux 3.133 qua). Lá Chắn rút gọn (Opus tạm) đang kiểm | ĐẠT thì gộp; nhắc chạy test trên Windows sau khi gộp (6 test đồng hồ kiểu Windows mới kiểm bằng đồng hồ giả) |
| [T-031](tickets/T-031-dia-chi-tran-thanh-link.md) Địa chỉ trần, email thành link | chưa có | Chờ T-019 lên `main` | Giao Thợ Máy |
| [T-032](tickets/T-032-loc-ho-so-nhan-go-sai.md) Bộ lọc hồ sơ nhận nhãn gõ sai | `team/T-032` (từ `main`) | Mới giao Thợ Máy | Soi Lỗi, Lá Chắn (A1, A3), gộp |

## Nhật ký bàn giao

_Mục mới nhất ở trên cùng._

### 2026-10-15 18:02 · Chỉ Huy B nhận quyền

- `git pull` về `main` = `d2fae78`. Đọc bàn giao 14:39 của A. Làm tiếp: T-019 (Thợ Máy làm nốt lượt 2), T-025 (kiểm tra Soi Lỗi của B), T-031 sau T-019.
- Mục "đang kết thúc" 14:10 của B đã cũ: A nhận và trả quyền sau đó (14:12 → 14:39).

### 14:39 · Chỉ Huy A trả quyền (chủ dự án: hạn mức sắp hết)

**Đã xong trong phiên A (14:12 → 14:39), đều đã lên `main`:**
- Chạy kiểm T-029 + T-030 trên Windows theo lệnh của B: 2 lượt đều 2.758 qua, 0 hỏng; test IPv6, `test_proactor_sendto_is_wrapped_on_windows`, các tham số `vong-lap-mac-dinh` đều PASSED.
- Lá Chắn T-028 **ĐẠT** (`9e55d38`; 3 lỗi Thấp: LC-T028-1 đổi sang `RLock` khi tiện, LC-T028-2 chấp nhận, LC-T028-3 gzip hỏng → gộp phiếu lớp AI sau).
- Gộp T-029 (`7c8604e`) và T-028 (`d08f8ca`). Windows 3.110 qua, 0 hỏng.
- Xóa nhánh đã gộp: `team/T-026`, `team/T-028`, `team/T-029`.
- Soi Lỗi T-019 đạt có điều kiện; Thợ Máy lượt 2 làm gần xong (bảng trên).
- Lập T-031. Số phiếu tiếp theo: **T-032**.

**Lưu ý:** Lá Chắn của A vẫn chạy tạm Opus 5.5 (tài khoản A không dùng được Fable). Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã có T-028, T-029, T-030.

### 2026-10-15 14:12 · Chỉ Huy A nhận quyền

- `git pull` về `main` = `39c8c1f`. Đọc bàn giao 14:10 của Chỉ Huy B, làm tiếp theo bảng "Đang làm dở".
- Về giờ lệch B nêu: các mốc giờ trong phiên A trước (11:00 → 13:50) là giờ A ước lượng, không lấy từ đồng hồ máy. Từ nay A ghi theo lệnh `date` (UTC+7).

### 2026-10-15 14:10 · Chỉ Huy B bàn giao cho Chỉ Huy A (chủ dự án yêu cầu)

**Đã xong trong phiên B (13:10 → 14:10):**
- **Gộp T-026 vào `main`** (`64383a5`): lớp AI chịu được thư viện lệch phiên bản, câu lỗi 400 cố định, client 3 hãng dùng địa chỉ chính thức. Lá Chắn ĐẠT.
- Phát hiện `main` **đỏ trên Linux** (9 test của T-027: thiếu `socket._fallback_socketpair` ở Python 3.12.3, máy không IPv6). Lập T-030, làm chung T-029. Cả hai đã qua Soi Lỗi và Lá Chắn (đạt có điều kiện), chỉ còn chạy trên Windows.
- T-028: Thợ Máy 2 lượt, Soi Lỗi đạt. Chờ Lá Chắn.
- Lập và làm T-019 (thử mù mô hình): Thợ Máy xong logic, Họa Sĩ xong giao diện. Chờ Soi Lỗi.
- **Quyết định chủ dự án:** giữ việc thư viện AI đọc `HTTPS_PROXY`, `SSL_CERT_FILE`; đã ghi sổ rủi ro `security.md` mục 6 và `BAN-GIAO.md` 7.4.
- Số phiếu tiếp theo: **T-031**.

**Lưu ý vận hành:**
- Phiên cloud của B **không xóa được nhánh** trên GitHub (máy chủ git từ chối). Nhánh đã gộp, A xóa giúp: `team/T-026`.
- Tài khoản của B đang gần giới hạn sử dụng 5 tiếng (mở lại khoảng 18:00).
- Lá Chắn của B chạy tạm Opus 5.5. Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã thêm T-026; khi gộp thì thêm T-028, T-029, T-030, T-019.

### 2026-10-15 14:05 · Chỉ Huy B

- Chủ dự án yêu cầu tạm dừng B, nhường A. Không giao việc mới; chờ 3 agent đang chạy làm xong rồi bàn giao.

### 2026-10-15 13:50 · Chỉ Huy B

- Lá Chắn T-029 + T-030 **ĐẠT CÓ ĐIỀU KIỆN** (`91dbdb9`): không lỗi Nghiêm trọng/Cao/Trung bình; 17 phép thử lách đều bị chặn. Điều kiện: (1) chạy test trên Windows (lệnh ở mục "Đang làm dở"); (2) Soi Lỗi thêm bản quyền PSF vào docstring, đang làm. Lỗi Thấp #2 (bộ chặn chỉ xét AF_INET/AF_INET6, có từ trước): không lập phiếu, ghi bảng việc.

### 2026-10-15 13:45 · Chỉ Huy B

- **Quyết định chủ dự án:** giữ việc thư viện AI đọc `HTTPS_PROXY`, `SSL_CERT_FILE` (mạng công ty có thể cần); ghi sổ rủi ro `security.md` mục 6 và `BAN-GIAO.md` mục 7.4. Biến `*_CUSTOM_HEADERS` bỏ qua ở T-028.

### 2026-10-15 13:35 · Chỉ Huy B

- Lá Chắn T-026 ĐẠT (`d102b0a`). Gộp vào `main` (`64383a5`); Linux: 2.717 qua, chỉ 9 test đỏ sẵn của T-027. Giao T-028 cho Thợ Máy.
- Phiên cloud không xóa được nhánh trên GitHub (máy chủ git từ chối). `team/T-026` đã gộp xong, Chỉ Huy A hoặc chủ dự án xóa giúp.

### 2026-10-15 13:10 · Chỉ Huy B nhận quyền

- `git pull` về `main` = `ce8bc62`. Đọc mục bàn giao 13:50 của Chỉ Huy A, sẽ làm tiếp theo bảng "Đang làm dở".
- Giờ trong mục bàn giao của A (13:50) lệch với giờ commit `ce8bc62` (13:08). Chỉ Huy B ghi giờ theo đồng hồ máy chủ (UTC+7).
- Đã kiểm tra: các phiên con cũ của B (Thợ Máy T-026, Soi Lỗi T-025 mở sáng 15/10) dừng từ 08:12 vì giới hạn sử dụng, không còn đẩy gì. Em lưu trữ chúng.
- Gộp `main` vào `team/T-025` (`ce1a79c`). Chạy toàn bộ test trên Linux: **9 hỏng, đều ở `tests/test_soi_loi_t027.py`**, và cũng hỏng y vậy trên `main`. Lập T-030, giao chung với T-029.

### 2026-10-15 13:50 · Chỉ Huy A trả quyền (chủ dự án yêu cầu dừng, để Chỉ Huy B làm tiếp)

**Đã xong trong phiên A (11:00 → 13:50), đều đã lên `main`:**
- Phiếu điều phối này; `docs/plan/` (kế hoạch SEO của chủ dự án, đọc `docs/plan/README.md` trước); ghi quyết định 15/10 vào `CLAUDE.md`, `TIEN-DO.md`, `BAN-GIAO.md`.
- Gộp T-022 + T-024 (`958a93e`) và T-027 (`e4107f2`). **Từ T-027, `uv run pytest` chạy xanh cả trên Windows** (trước đó 152 test đỏ oan trên Windows).
- Xóa các nhánh tạm đã gộp: `team/T-018`, `T-022`, `T-023`, `T-024`, `T-027`.
- Lập phiếu T-027, T-028, T-029. Số phiếu tiếp theo: **T-030**.

**Dừng giữa chừng (chi tiết ở bảng "Đang làm dở"):** Lá Chắn T-026 (chưa có biên bản), Soi Lỗi T-029 (có code và test, chưa báo cáo).

**Gợi ý cho Lá Chắn T-026** (lời giao A đã soạn, dùng lại được):
- Diff riêng của T-026, không tính T-027 đã kiểm: `git diff ed0324e c906285` (trước khi merge main) và `git diff e4107f2 ac9fbda` (sau merge `3366566`). File code: `seo_app/ai/base.py`, `registry.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`.
- Trọng tâm: S2 (câu lỗi 400 không còn chữ nào của máy chủ ngoài mã đã qua `safe_code`; mã không thành link); W4 / `security.md` 2.7 (đủ 6 chỗ tạo client có `base_url` chính thức cố định); bắt lỗi rộng `ImportError/AttributeError/TypeError/KeyError` → câu "uv sync" có che lỗi bảo mật không.
- Đánh giá 2 điểm Chỉ Huy A đã quyết: SL-T026-3 **chấp nhận** (Gemini nhận JSON sai kiểu → câu "uv sync" thay vì "dữ liệu lạ", không lộ gì); SL-T026-4 → T-028.
- Thợ Máy nêu, ngoài phạm vi: thư viện AI vẫn đọc `HTTPS_PROXY`, `SSL_CERT_FILE`, `OPENAI_CUSTOM_HEADERS`, `ANTHROPIC_CUSTOM_HEADERS`. Cần Lá Chắn đánh giá có lập phiếu không; lưu ý chủ dự án có thể dùng mạng công ty phải đi qua proxy.

**Lưu ý vận hành:**
- Tài khoản của A gọi Fable 5.1 bị từ chối ("cần mua thêm lượt dùng"), nên Lá Chắn T-027 chạy tạm Opus 5.5. Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã thêm T-027.
- Tài khoản của A chạm giới hạn sử dụng lúc 12:00 khi 2 agent chạy cùng lúc. Agent nên commit và push từng phần nhỏ.
- A làm trên Windows (Claude Desktop, mỗi agent một git worktree). Các worktree đã xóa; nhánh còn trên GitHub.
- Các nhánh cũ `claude/project-thread-bcuk2m`, `claude/wizardly-brahmagupta-f0w8d8` đã gộp hết vào `main` từ trước, xóa được khi tiện.

### 2026-10-15 11:00 · Chỉ Huy A nhận quyền

- `git pull` về `main` = `157899b`. Chưa có phiếu điều phối chung trước đây, nên đây là mục đầu tiên. Mục "Đang làm dở" của Chỉ Huy B lấy theo `board.md` và lịch sử git.
- Hiện trạng các nhánh lúc nhận:
  - `team/T-024` (đã gộp `team/T-022`): Lá Chắn **ĐẠT** (`41e4165`, 08:09), **chưa gộp** vào `main`.
  - `team/T-025`: Soi Lỗi có 2 commit (`5ff60f3`, `a1d48d4`), **chưa có báo cáo**, chưa qua Lá Chắn.
  - `team/T-026`: chỉ là điểm tạo nhánh, chưa có việc. Phiếu T-026 chưa giao.
  - `team/T-018`, `team/T-023`: đã gộp hết vào `main`, xóa được.
- Phát hiện: chạy `uv run pytest` **trên Windows** có 152 test đỏ (2.009 qua). 148 test hỏng vì bộ chặn mạng trong `tests/conftest.py` chặn cả kết nối `127.0.0.1` mà asyncio trên Windows cần để khởi động (trên Linux thì không cần). 4 test đặt biến môi trường dài quá 32.767 ký tự (giới hạn của Windows). Code ứng dụng không lỗi; phần sai nằm ở bộ test. Sẽ lập phiếu cho Soi Lỗi.
- Quyết định chủ dự án ngày 2026-10-15:
  - Mô hình AI: **không có mặc định**. Giữ đủ cả 3 hãng (Claude, ChatGPT, Gemini), chủ dự án tự đổi khi cần. Không đổi `config/ai.toml` sang Gemini. T-019 (thử mù) hết chờ.
  - **Giữ Giai đoạn 6** (theo dõi thứ hạng qua Search Console).
  - Đưa thư mục `plan/` (kế hoạch SEO, yêu cầu phần mềm) lên repo.
  - Lập phiếu điều phối chung này. Phiên "Điều Phối" thứ ba trên máy chủ dự án đã bị bỏ, không tính.

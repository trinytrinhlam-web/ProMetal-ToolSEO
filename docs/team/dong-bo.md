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

**Chỉ Huy B**, nhận lúc 2026-10-15 13:10 (theo yêu cầu của chủ dự án: "đọc việc agent khác đã làm, tiếp tục từ chỗ đang làm dở").

## Đang làm dở

_Bên đang giữ quyền cập nhật mục này sau mỗi bước._

Chỉ Huy B, cập nhật 2026-10-15 13:20. Agent là phiên con dưới phiên "Điều phối" của B trên cloud; nhánh nào cũng đẩy lên GitHub.

| Phiếu | Nhánh | Đang ở bước | Việc tiếp theo |
|---|---|---|---|
| [T-026](tickets/T-026-loi-thap-lop-ai.md) Lỗi Thấp lớp AI | `team/T-026` (`ac9fbda`) | Lá Chắn (Opus tạm) kiểm từ đầu | ĐẠT thì gộp vào `main`, rồi giao T-028 |
| [T-029](tickets/T-029-bo-chan-mang-udp-va-dns.md) + [T-030](tickets/T-030-test-t027-chay-tren-linux-mac.md) Bộ chặn mạng, test chạy trên Linux/Mac | `team/T-029` (`3628608`) | Soi Lỗi làm nốt T-029 và làm T-030 | Lá Chắn kiểm; **chạy lại `uv run pytest` trên Windows** (A hoặc chủ dự án) rồi mới gộp |
| [T-025](tickets/T-025-on-dinh-test-do-toc-do.md) Test đo tốc độ | `team/T-025` (`ce1a79c`, đã gộp `main`) | Soi Lỗi làm tiếp, nộp báo cáo | Lá Chắn rút gọn, gộp |
| [T-028](tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) | chưa có | Chờ T-026 lên `main` | Giao Thợ Máy |

**Lưu ý cho Chỉ Huy A:** `main` hiện **đỏ trên Linux** (9 test trong `tests/test_soi_loi_t027.py`: thiếu `socket._fallback_socketpair` trên Python 3.12.3, máy không có IPv6). Trên Windows vẫn xanh. Đang sửa ở T-030.

## Nhật ký bàn giao

_Mục mới nhất ở trên cùng._

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

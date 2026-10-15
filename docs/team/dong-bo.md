# Phiếu điều phối chung (2 Chỉ Huy)

Dự án có **hai Chỉ Huy** chạy ở **hai tài khoản Claude khác nhau**. Họ **không chạy cùng lúc**: Chỉ Huy kia chỉ làm khi Chỉ Huy này dừng, và một phiên thường chỉ dừng khi **hết lượt dùng**, tức là dừng bất ngờ, không kịp dặn lại. Hai bên chỉ liên lạc với nhau qua file này (chủ dự án chốt 2026-10-15).

Đọc file này **trước mọi việc khác**, ngay sau `git pull`.

## Hai Chỉ Huy

| Tên trong file này | Ở đâu |
|---|---|
| **Chỉ Huy A** | Claude Desktop (Code) trên máy chủ dự án, thư mục `D:\ProMetal-ToolSEO\ProMetal-ToolSEO` |
| **Chỉ Huy B** | Tài khoản Claude thứ hai của chủ dự án |

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

**Chỉ Huy A**, từ 2026-10-15 11:00.

## Đang làm dở

_Bên đang giữ quyền cập nhật mục này sau mỗi bước._

- ✅ Lập phiếu điều phối chung; đưa `docs/plan/` lên repo (`5d62087`).
- ✅ Gộp `team/T-024` (T-022 + T-024) vào `main` (`958a93e`); xóa nhánh `team/T-018`, `team/T-022`, `team/T-023`, `team/T-024`.
- ✅ Lập phiếu T-027 (Soi Lỗi: bộ test chạy xanh trên Windows).
- ⏳ Đang làm: giao T-027 cho Soi Lỗi và T-026 cho Thợ Máy. Hai agent chạy dưới phiên Chỉ Huy A, mỗi agent một worktree riêng (`D:\ProMetal-ToolSEO\wt-T-027`, `wt-T-026`), đẩy lên nhánh `team/T-027`, `team/T-026`. **Chỉ Huy B: nếu tiếp quản, xem hai nhánh này trên GitHub để biết agent đã làm tới đâu; đừng giao lại hai phiếu này.**
- Còn treo: T-025 (Soi Lỗi có 2 commit trên `team/T-025`, chưa nộp báo cáo). Chưa giao lại vì đang chạy 2 agent.

## Nhật ký bàn giao

_Mục mới nhất ở trên cùng._

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

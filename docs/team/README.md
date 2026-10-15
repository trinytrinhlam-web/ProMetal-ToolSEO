# Đội agent của dự án

Tài liệu này mô tả cách nhiều agent AI cùng làm dự án SEO App dưới sự điều phối của một agent chính. Mọi thứ đều nằm trong thư mục dự án và được lưu trên GitHub, nên có thể giao cho bất kỳ AI nào làm tiếp.

## Sơ đồ đội

```
                     Chủ dự án (An Manu)
                            │  duyệt, quyết định
                            ▼
                     ┌────────────┐
                     │  CHỈ HUY   │  điều phối: lập phiếu, giao việc, duyệt báo cáo
                     └─────┬──────┘
     ┌──────────┬──────────┼──────────┬──────────┬──────────┐
     ▼          ▼          ▼          ▼          ▼          ▼
  THỢ MÁY    HỌA SĨ    NGÒI BÚT    SOI LỖI    LÁ CHẮN    THƯ KÝ
  logic      giao diện  nội dung   kiểm thử   bảo mật    tài liệu
  seo_app/   app/       prompt,    test,      (quyền     README,
                        checklist  tìm lỗi    chặn)      .env.example
```

Danh sách đầy đủ, phạm vi file và model khuyên dùng: [roster.md](roster.md).

## Thư mục

| Đường dẫn | Nội dung |
|---|---|
| `AGENTS.md` (gốc repo) | Điểm bắt đầu cho mọi AI |
| `docs/team/roster.md` | Danh sách agent, phạm vi, model |
| `docs/team/rules.md` | Quy tắc, nguyên tắc, ràng buộc chung |
| `docs/team/security.md` | Chính sách bảo mật và danh sách kiểm định |
| `docs/team/board.md` | Bảng việc: ai đang làm gì |
| `docs/team/dong-bo.md` | Phiếu điều phối chung giữa 2 Chỉ Huy (2 tài khoản, chạy luân phiên) |
| `docs/team/templates/` | Mẫu phiếu giao việc, báo cáo, biên bản bảo mật |
| `docs/team/tickets/` | Các phiếu giao việc (`T-001-ten-ngan.md`) |
| `docs/team/reports/` | Báo cáo của agent (`T-001-ten-agent.md`) |
| `.claude/agents/` | Hồ sơ từng agent. Claude Code tự nhận các file này làm agent phụ; AI khác đọc như văn bản thường |

## Vòng đời một việc

```
Mới ──► Đã giao ──► Đang làm ──► Chờ kiểm thử ──► Chờ bảo mật ──► Chờ duyệt ──► Xong
                       │               │                │               │
                       └───────────────┴──── Trả lại ◄──┴───────────────┘
                                 (kèm lý do, quay về Đang làm)
```

1. **Chỉ Huy lập phiếu** từ lộ trình trong `CLAUDE.md` hoặc yêu cầu của chủ dự án, theo mẫu `templates/ticket.md`. Mỗi phiếu chỉ một việc, giao cho một agent chính, ghi rõ file được phép sửa và tiêu chí xong.
2. **Ghi vào `board.md`** để chủ dự án theo dõi.
3. **Agent làm việc** đúng phạm vi phiếu, rồi nộp báo cáo theo `templates/report.md` vào `reports/`.
4. **Soi Lỗi kiểm thử** mọi phiếu có sửa code: chạy toàn bộ test, viết thêm test cho phần mới, thử các trường hợp xấu.
5. **Lá Chắn kiểm định bảo mật** mọi phiếu có sửa code, cấu hình, thư viện hoặc prompt AI, theo `security.md`. Kết quả ghi vào biên bản theo `templates/security-review.md`. Lá Chắn **có quyền chặn**: còn lỗi mức Nghiêm trọng hoặc Cao thì phiếu không được đóng.
6. **Chỉ Huy duyệt**: đối chiếu với tiêu chí xong, cập nhật `board.md` và mục Trạng thái trong `CLAUDE.md`.
7. **Chủ dự án quyết định** những việc trong danh sách "phải hỏi" ở `rules.md` (đăng bài thật, thêm thư viện, đổi quyết định đã chốt, commit/push…).

Phiếu chỉ sửa tài liệu thì bỏ qua bước 4; bước 5 vẫn chạy nhanh để soát bí mật bị lộ.

## Cách Chỉ Huy giao việc

- **Trên Claude Code cloud** (cách mặc định từ 2026-10-14, chủ dự án chọn để theo dõi được): Chỉ Huy chạy ở phiên **"Điều phối"** và mở mỗi agent thành **một phiên con** (hiện lồng dưới "Điều phối" ở thanh bên của app Claude). Tên phiên: `<Tên agent> · T-xxx <việc ngắn>`, ví dụ `Thợ Máy · T-018 ChatGPT/Gemini`. Phiên con dùng đúng model của vai trong `roster.md`.
  - Mỗi phiếu có **một nhánh tạm** `team/T-xxx`, tạo từ `main`. Agent làm phiếu commit và đẩy lên nhánh đó (không đẩy `main`, không `rebase`, không `push --force`).
  - Soi Lỗi rồi Lá Chắn mở phiên con riêng, làm trên **cùng nhánh** đó. Soi Lỗi được thêm test; Lá Chắn chỉ thêm biên bản.
  - Lá Chắn ĐẠT: Chỉ Huy gộp nhánh vào `main` (merge, không rebase), chạy lại `uv run pytest` và `uv run ruff check .`, đẩy `main`, rồi **xóa nhánh tạm** để repo gọn.
  - Xong việc, phiên con gửi Chỉ Huy một tin ngắn (công cụ `send_message`); Chỉ Huy cũng tự kiểm tra định kỳ.
  - **Tối đa 3 phiên con chạy cùng lúc.** Tài khoản Claude có giới hạn sử dụng theo 5 tiếng, dùng chung cho mọi phiên, kể cả "Điều phối". Ngày 2026-10-14 chạy 7 phiên cùng lúc thì chạm giới hạn, 4 phiên dừng giữa chừng. Phiên con phải commit và đẩy lên nhánh sau từng phần lớn, để không mất việc nếu bị dừng.
- **Trong Claude Code trên máy** (một thư mục làm việc): Chỉ Huy gọi agent phụ bằng tên trong `.claude/agents/`, kèm đường dẫn phiếu. Agent phụ không nói chuyện trực tiếp với chủ dự án; Chỉ Huy tổng hợp kết quả và báo lại.
- **Với AI khác**: mở một phiên mới, đưa cho AI đó nội dung `AGENTS.md`, hồ sơ vai trò và phiếu. Yêu cầu AI nộp báo cáo đúng mẫu.

Chủ dự án luôn theo dõi được qua `board.md`: mỗi dòng ghi tên agent, phiếu và trạng thái.

## Bàn giao cho AI khác

Thư mục này đã đủ để AI khác làm tiếp mà không cần hỏi lại:

1. Gửi link GitHub của dự án (hoặc cả thư mục, **trừ file `.env` và thư mục `.venv`**).
2. Bảo AI đó: "Đọc `AGENTS.md` và làm theo. Bạn là Chỉ Huy" (hoặc vai khác).
3. AI đó đọc `board.md` để biết việc nào đang dở, việc nào tiếp theo.

Không cần gửi khóa API. Trên máy không có `.env`, AI chỉ chạy được test bằng dữ liệu giả, và như vậy là đúng ý đồ.

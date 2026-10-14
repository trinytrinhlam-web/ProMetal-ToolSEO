# Bàn giao: chuyển dự án sang máy mới và project Claude mới

_Viết ngày 2026-10-14 bởi Chỉ Huy (Claude). Đọc kèm [`TIEN-DO.md`](TIEN-DO.md) (tiến độ) và [`AGENTS.md`](AGENTS.md) (luật cho mọi AI)._

Toàn bộ code, tài liệu, phiếu việc, báo cáo và hồ sơ agent đều nằm trong repo GitHub `trinytrinhlam-web/ProMetal-ToolSEO`, nhánh `main`. Máy mới chỉ cần lấy repo về là có đủ. Những thứ **không** nằm trong repo (vì là bí mật hoặc dữ liệu riêng của máy) được liệt kê ở mục 2.

## 1. Trạng thái lúc bàn giao

- Nhánh `main` đã có mọi việc đã xong. Không còn thay đổi nào chưa đẩy lên.
- Không có agent nào đang làm dở. Bảng việc: [`docs/team/board.md`](docs/team/board.md).
- 1.871 bài kiểm tra tự động đều qua; `ruff` sạch.
- Việc tiếp theo và quyết định đang chờ: mục 6 bên dưới.

## 2. Những thứ phải tự mang sang (không có trên GitHub)

| Thứ | Ở đâu trên máy cũ | Cách mang sang |
|---|---|---|
| File `.env` (khóa API, mật khẩu WordPress, mã băm mật khẩu đăng nhập app) | Thư mục dự án, ví dụ `C:\Projects\ProMetal-ToolSEO\.env` | Chép bằng USB. Hoặc bỏ qua, rồi trên máy mới đặt mật khẩu và nhập lại khóa (mục 3). **Không** gửi qua email/chat. |
| File JSON service account Google (nếu đã có) | Ngoài thư mục dự án | Chép bằng USB, sửa đường dẫn trong `.env` |
| Bài đang soạn dở (tự lưu) | `data/drafts.sqlite` trong thư mục dự án | Chép thư mục `data/` nếu muốn giữ bài dở. Không chép thì chỉ mất bài đang viết dở, không mất gì khác. |
| Thư mục ảnh thật | USB / Google Drive for Desktop | Khai báo lại đường dẫn trong `.env` (`IMAGE_FOLDERS`) khi tới Giai đoạn 3 |

Bài đã gửi lên WordPress, kế hoạch trên Google Sheets thì nằm trên mạng, máy nào cũng thấy.

## 3. Dựng lại trên máy mới (Windows)

1. **Cài GitHub Desktop** (https://desktop.github.com), đăng nhập tài khoản GitHub `trinytrinhlam-web`.
2. **File → Clone repository** → chọn `ProMetal-ToolSEO` → thư mục lưu nên là `C:\Projects\ProMetal-ToolSEO` → **Clone**.
3. Nếu đã chép `.env` (và `data/`) bằng USB: dán vào thư mục vừa clone.
4. **Bấm đúp `run.bat`**. Lần đầu nó tự cài `uv`, Python và thư viện (vài phút, cần mạng). Trình duyệt mở app.
5. Nếu **chưa** chép `.env`: tắt app, bấm đúp `set_password.bat`, gõ mật khẩu hai lần, rồi chạy lại `run.bat`.
6. Đăng nhập → **Cài đặt → 🔌 Kết nối** → dán khóa Claude (và ChatGPT/Gemini nếu có) → **Lưu** → **Kiểm tra** (hiện chỉ kiểm được khóa Claude).
7. Trang **Kết nối WordPress**: điền địa chỉ site, tên đăng nhập, Application Password (hướng dẫn trong `README.md` mục 6).

Mac làm tương tự với `run.command` và `set_password.command` (xem `README.md` mục 3).

## 4. Mở project Claude mới để tiếp tục

1. Tạo project mới trên Claude, gắn repo GitHub `trinytrinhlam-web/ProMetal-ToolSEO`.
2. Nếu dùng Claude Code trên máy: cho phép thư mục `C:\Projects\ProMetal-ToolSEO`.
3. Dán tin nhắn đầu tiên sau vào project:

   > Đọc `AGENTS.md`, `BAN-GIAO.md`, `TIEN-DO.md` và `docs/team/board.md`. Bạn là Chỉ Huy, điều phối đội agent trong `.claude/agents/`. Mỗi agent bạn gọi phải có tên rõ ràng để tôi theo dõi. Tiếp tục việc tiếp theo trên bảng việc. Trả lời tôi bằng tiếng Việt.

4. Claude Code tự nhận 7 agent từ thư mục `.claude/agents/` (tên, vai trò, mô hình đã ghi sẵn), và tự chạy `uv sync` khi mở phiên trên cloud (`.claude/hooks/session-start.sh`).

## 5. Cách theo dõi agent

- **Bảng việc** [`docs/team/board.md`](docs/team/board.md): agent nào đang làm phiếu nào, chờ gì, đã xong gì.
- **Phiếu** `docs/team/tickets/T-xxx-*.md`: giao việc gì, tiêu chí xong.
- **Báo cáo** `docs/team/reports/`: agent đã làm gì, bằng chứng chạy test; biên bản bảo mật của Lá Chắn.
- Quy trình mỗi phiếu: agent làm → **Soi Lỗi** kiểm thử → **Lá Chắn** kiểm bảo mật (có quyền chặn) → Chỉ Huy đẩy lên `main`.

| Agent | Mã | Việc | Mô hình | Đang làm lúc bàn giao |
|---|---|---|---|---|
| Chỉ Huy | `chi-huy` | Điều phối, lập phiếu, báo cáo anh | Opus 5.5 | Không |
| Thợ Máy | `tho-may` | Logic Python `seo_app/` | Opus 5.5 | Không (việc kế: T-018) |
| Họa Sĩ | `hoa-si` | Giao diện `app/` | Opus 5.5 | Không (việc kế: T-019) |
| Ngòi Bút | `ngoi-but` | Prompt, văn phong `config/` | Opus 5.5 | Không |
| Soi Lỗi | `soi-loi` | Kiểm thử | Opus 5.5 | Không |
| Lá Chắn | `la-chan` | Bảo mật, quyền chặn | Fable 5.1 (tạm chạy Opus 5.5 tới 01/11 vì Fable bị giới hạn) | Không |
| Thư Ký | `thu-ky` | Tài liệu | Sonnet 5.5 | Không |

## 6. Việc tiếp theo và quyết định đang chờ

**Chờ anh quyết:**

1. **Cách thêm ChatGPT và Gemini (T-018).** Dùng thư viện chính hãng `openai` và `google-genai` (Chỉ Huy đề xuất, giống cách đang dùng cho Claude) hay tự viết. Quy tắc dự án: thêm thư viện phải được anh duyệt. Trả lời là AI ở project mới làm ngay.
2. **PR #3 Hồ sơ doanh nghiệp** (`config/business_profile.md`, nhánh `claude/project-thread-bcuk2m`): chờ gộp. Ngòi Bút ghi nhận dòng 112 cần chỉnh: hàm `confirmed_profile` bỏ luôn một quy tắc có nhắc tới nhãn `[CẦN XÁC NHẬN]`. Khi chưa gộp, AI viết bài chưa có thông tin riêng của Pro-Metal.
3. **Giai đoạn 6** (theo dõi thứ hạng Search Console): có giữ không.

**Việc tiếp theo theo thứ tự:**

1. T-018: thêm ChatGPT/Gemini (sau khi anh chọn ở điểm 1).
2. T-019: thử mù mô hình trong Cài đặt.
3. Giai đoạn 3: ảnh (giữ nguyên GPS trong ảnh, khi nén WebP phải chép lại EXIF).
4. Giai đoạn 4: meta, schema, liên kết nội bộ (plugin SiteSEO).
5. Giai đoạn 5: kế hoạch, lịch, gửi bài lên WordPress. Có danh sách bảo mật bắt buộc ở cuối `docs/team/board.md`.

**Việc nhỏ còn treo:**

- Lá Chắn kiểm lại T-013 → T-021 bằng Fable 5.1 sau ngày 01/11 (các lượt vừa rồi chạy tạm bằng Opus).
- Thư Ký cập nhật `README.md`: nhập khóa API trong Cài đặt → Kết nối; bài đang soạn được tự lưu.
- Meta title/description chưa được lưu vào nháp (làm ở Giai đoạn 4).

## 7. Quyết định anh đã chốt (AI mới phải giữ)

- Push thẳng lên `main`, không tạo nhánh mới, không mở PR mới; giữ repo gọn. (Điều này thay cho dòng "mỗi giai đoạn một nhánh" trong `CLAUDE.md`.)
- Không cần tiết kiệm chi phí mô hình AI; ưu tiên chất lượng.
- Chỉ Huy tự gọi agent phụ, nhưng mỗi agent phải có tên cụ thể để anh theo dõi.
- Giữ nguyên vị trí GPS trong ảnh (cố ý, cho SEO địa phương). Đã ghi vào sổ rủi ro `docs/team/security.md` mục 6.
- Website suachuacuasat.com dùng plugin SEO **SiteSEO**, **không có** site thử nghiệm: chỉ tạo bản nháp, đăng thật phải có anh bấm xác nhận.
- Không dùng năm thành lập, tên tác giả, bảng giá trong bài. Chi nhánh có ở mọi quận TP.HCM.
- Khóa API nhập trong app nhưng chỉ lưu trong `.env` trên máy, không bao giờ lên GitHub.
- Anh dùng GitHub Desktop; mọi giải thích bằng tiếng Việt, đơn giản, giải thích thuật ngữ trước khi hỏi quyết định.

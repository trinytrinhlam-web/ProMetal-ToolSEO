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

## 7. Mọi trao đổi và quyết định của chủ dự án (không được bỏ sót)

Gom từ toàn bộ project cũ (chat chung và các luồng: Khám phá repo, Duyệt và merge WordPress, Soạn thông tin nền doanh nghiệp, Xây Giai đoạn 2, Hệ thống agent và phiếu giao việc). Quyết định có từ trước nữa (06/10) nằm trong `CLAUDE.md` mục "Quyết định đã chốt".

### 7.1 Cách làm việc với anh

- Trả lời và viết tài liệu **bằng tiếng Việt**, ngắn, dễ hiểu. Anh hiểu khái niệm lập trình nhưng ít dùng Git và dòng lệnh: **giải thích thuật ngữ trước khi hỏi quyết định** (ví dụ anh đã hỏi lại "GPS trong ảnh là gì, T-007 là gì").
- Câu hỏi cần anh quyết: mỗi câu trả lời được bằng một từ, có đề xuất của Claude.
- **Làm liên tục, hết việc này sang việc khác, không chờ ngày** (anh nói 14/10: "Hết việc tới việc, không chờ ngày"). Việc gì đổi được, sửa lại được thì cứ làm; chỉ hỏi khi cần anh quyết.
- Trước khi trả lời phải nắm rõ từng agent làm gì (anh yêu cầu 14/10).
- Anh muốn **kiểm soát và theo dõi được mọi agent**: agent nào cũng có tên cụ thể, việc ghi trên `docs/team/board.md`.

### 7.2 Repo, Git, máy tính

- Repo: `https://github.com/trinytrinhlam-web/ProMetal-ToolSEO` (tài khoản GitHub `trinytrinhlam-web`, chủ dự án An Manu).
- **Push thẳng lên `main`, không tạo nhánh mới, không mở PR mới.** Ngoại lệ chủ dự án chốt 2026-10-14: agent chạy ở phiên con dùng nhánh tạm `team/T-xxx`, Chỉ Huy gộp vào `main` sau khi Lá Chắn ĐẠT rồi xóa nhánh (`docs/team/README.md`, mục "Cách Chỉ Huy giao việc"). Thay cho dòng "mỗi giai đoạn một nhánh / PR" trong `CLAUDE.md`. Luôn `git pull` trước khi sửa vì có thể có phiên khác cùng đẩy lên.
- **Repo phải gọn, sạch, tự đủ**: xóa file phần mềm không cần; đưa lên đủ mọi file để AI khác (Claude, ChatGPT, Gemini…) mở ra là làm tiếp được.
- Máy anh là Windows, thư mục dự án `C:\Projects\ProMetal-ToolSEO`. Anh dùng **GitHub Desktop** (Fetch → Pull để lấy bản mới). Máy cũ ban đầu chưa có Git; cài bằng `winget install --id Git.Git -e` hoặc tải ở git-scm.com.
- Phần mềm **cài và chạy trên máy** (không phải web): bấm đúp `run.bat`, mở trong trình duyệt ở localhost, có mật khẩu. Cần Internet để gọi AI và gửi bài nháp sang WordPress.
- Anh từng từ chối cho Claude điều khiển máy từ xa ở các luồng khác; chỉ duyệt riêng thư mục `C:\Projects\ProMetal-ToolSEO` cho luồng hệ thống agent. Muốn chạy lệnh trên máy mới phải xin anh duyệt lại thư mục.

### 7.3 Đội agent và chi phí

- Chỉ Huy **tự gọi agent phụ**, nhưng **mỗi agent phải có tên cụ thể** để anh theo dõi.
- Bắt buộc có phiếu giao việc và báo cáo; có quy tắc, nguyên tắc, ràng buộc; **agent kiểm thử và bảo mật phải đảm bảo mức an toàn cao nhất**; ghi rõ model từng agent.
- **Không cần tiết kiệm chi phí model**, ưu tiên chất lượng: Lá Chắn Fable 5.1 (không bao giờ hạ cấp; tạm Opus 5.5 tới 01/11 vì Fable bị giới hạn), Thư Ký Sonnet 5.5, còn lại Opus 5.5.
- Đã duyệt: sửa code ngay cho các lỗi bảo mật; sửa `seo_app/config.py` để test không bao giờ đọc `.env` thật; khai báo `pydantic` trong `pyproject.toml`.

### 7.4 Website và doanh nghiệp

- Website **suachuacuasat.com** (Cơ khí Pro-Metal, sửa và làm cửa sắt). Plugin SEO là **SiteSEO** (không phải Rank Math/Yoast). Trang chủ có Site Kit by Google.
- **Không có site thử nghiệm (staging)**: làm thẳng trên site thật, nên mọi bài chỉ tạo **nháp**; đăng thật phải có anh bấm xác nhận.
- Chi nhánh có ở **mọi quận huyện TP.HCM**, website chưa cập nhật đủ. Bài viết nói "có thợ ở mọi khu vực TP.HCM"; địa chỉ cụ thể chỉ dùng 9 địa chỉ trên trang Liên hệ cho tới khi anh bổ sung.
- **Không dùng** năm thành lập, tên người phụ trách/tác giả, bảng giá trong bài. Hướng khách gửi ảnh qua Zalo để báo giá.
- **Ca sửa thật đáng nhớ, câu khách hay hỏi qua Zalo: để sau.** Khi viết từng bài, app hỏi anh "chất liệu thật" (bước 3 quy trình).
- Thông tin doanh nghiệp đã soạn (từ website) nằm trong `config/business_profile.md` của **PR #3** (chưa gộp vào `main`): hotline 03.4444.07.17, trụ sở 728/1 Lê Trọng Tấn, Bình Tân, bảo hành 2 năm, gần 30 thợ, dịch vụ và kiến thức nghề. Dòng nào đánh dấu `[CẦN XÁC NHẬN]` thì AI không dùng.
- PR #3 đang xung đột nhỏ với `main` ở `CLAUDE.md` (hai bên cùng thêm dòng Trạng thái, cách sửa là giữ cả hai). Có thẻ hỏi "gộp bản mới nhất vào PR #3" chưa được trả lời.

### 7.5 Tính năng và nội dung

- **Giữ nguyên vị trí GPS trong ảnh** ("nhiều khi đó là mục đích cố ý"). Phiếu T-007 xóa GPS đã hủy; ghi trong sổ rủi ro `docs/team/security.md` mục 6. Khi nén WebP phải chép lại EXIF.
- Anh muốn **tự nhập khóa API trong phần mềm** (Gemini, ChatGPT, Claude): đã làm ở Cài đặt → 🔌 Kết nối; khóa lưu trong `.env`, không bao giờ hiện lại.
- Anh sẽ dùng **Gemini** (và có thể ChatGPT, Claude). Cách nối ChatGPT/Gemini vào phần viết bài (T-018) đang chờ anh chọn (mục 6).
- AI viết bài có bật **mô hình dự phòng**: nếu Claude từ chối một yêu cầu thì tự chạy lại bằng mô hình khác.
- Giai đoạn 6 (theo dõi thứ hạng) đã bỏ khỏi giao diện demo; chờ anh xác nhận có giữ không.

### 7.6 Lịch sử ngắn

- 06/10: khởi tạo; xong Giai đoạn 0, Giai đoạn 1 và giao diện demo (PR #2). Anh duyệt bố cục demo lần 2, chốt phần mềm tập trung vào viết bài.
- 14/10 sáng: PR #2 gộp vào `main`; soạn hồ sơ doanh nghiệp (PR #3); Giai đoạn 2 phần 1 (Claude viết bài) đẩy lên `main`.
- 14/10 chiều tối: lập đội agent; T-001 → T-021 xong (kiểm định bảo mật, gia cố lọc nội dung AI, tự lưu bài, nhập khóa API).
- 14/10 tối: anh chuyển sang máy mới và project mới; viết file này.

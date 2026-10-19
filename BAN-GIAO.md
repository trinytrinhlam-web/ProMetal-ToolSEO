# Bàn giao: chuyển dự án sang máy mới và project Claude mới

_Viết ngày 2026-10-14 bởi Chỉ Huy (Claude). Đọc kèm [`TIEN-DO.md`](TIEN-DO.md) (tiến độ) và [`AGENTS.md`](AGENTS.md) (luật cho mọi AI)._

Toàn bộ code, tài liệu, phiếu việc, báo cáo và hồ sơ agent đều nằm trong repo GitHub `trinytrinhlam-web/ProMetal-ToolSEO`, nhánh `main`. Máy mới chỉ cần lấy repo về là có đủ. Những thứ **không** nằm trong repo (vì là bí mật hoặc dữ liệu riêng của máy) được liệt kê ở mục 2.

## 1. Trạng thái lúc bàn giao

_Cập nhật 2026-10-16, 13:00 giờ Việt Nam (Chỉ Huy B). Trạng thái mới hơn: xem [`docs/team/dong-bo.md`](docs/team/dong-bo.md) và [`TIEN-DO.md`](TIEN-DO.md)._

- `main` chỉ chứa việc đã qua kiểm định bảo mật. Việc làm xong nhưng chưa qua Lá Chắn nằm ở các **nhánh tạm** `team/T-xxx` trên GitHub, không mất.
- **Giai đoạn 2 xong** (2026-10-16). Còn 2 phiếu dọn lỗi mức Thấp, không chặn: T-044, T-045.
- Đang dở (chi tiết ở [`docs/team/board.md`](docs/team/board.md)):

  | Nhánh | Phiếu | Còn lại |
  |---|---|---|
  | `team/T-036` | T-036 meta title/description/slug (Giai đoạn 4) | Thợ Máy xong. Còn Soi Lỗi, rồi Lá Chắn, rồi gộp |

- Các agent chạy ở **phiên con dưới phiên "Điều phối"** của Chỉ Huy đang giữ quyền. Hai Chỉ Huy phối hợp qua `docs/team/dong-bo.md`.
- `main`: 4.658 bài kiểm tra qua trên Linux, `ruff` sạch. Lần chạy Windows gần nhất là 3.110 bài; cần chạy lại.
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

> Trạng thái mới nhất giữa hai Chỉ Huy luôn nằm ở [`docs/team/dong-bo.md`](docs/team/dong-bo.md); mục này có thể cũ hơn.

**Chờ anh quyết:** không còn câu nào. Ngày 16/10 anh trả lời 1A 2A 3A 4A 5A (mục 7.4). Việc anh làm trên website (bật Abilities, tạo tài khoản Biên tập viên, dọn 3 chỗ, nhờ kiểm 3 đường REST): `TIEN-DO.md` mục 4.

**Việc tiếp theo theo thứ tự:**

1. T-036: Soi Lỗi, rồi Lá Chắn, rồi gộp.
2. T-037 (danh sách bài đã đăng + cache) và T-038 (schema FAQPage): chạy song song được.
3. T-039 (liên kết nội bộ), rồi T-040 (lời dặn meta/anchor), rồi T-041 (bước SEO thật trên giao diện).
4. T-042 (ghi SEO lên nháp WordPress qua Abilities): làm sau T-037. Thử thật cần anh bật Abilities và có tài khoản Biên tập viên.
5. Dọn lỗi Thấp khi có chỗ: T-044 (Họa Sĩ), T-045 (Thợ Máy).
6. Giai đoạn 3 (ảnh; Pillow đã duyệt 16/10) và Giai đoạn 5 (kế hoạch, lịch, gửi bài). Giai đoạn 5 có danh sách bảo mật bắt buộc ở cuối `docs/team/board.md`.

**Việc nhỏ còn treo:**

- Sau ngày 01/11, Lá Chắn kiểm lại bằng Fable 5.1 các phiếu đã chạy tạm bằng Opus. Danh sách ở đầu `board.md`.
- Chạy `uv run pytest` trên Windows (Chỉ Huy A). Các phiếu gần đây mới chạy trên Linux.
- Xóa các nhánh tạm đã gộp: `team/T-019`, `T-025`, `T-031`, `T-032`, `T-033`, `T-034`, `T-035`, `T-043`. Phiên cloud của B không xóa được nhánh.
- README 7.6, dòng "(Claude)": Thư Ký thêm chữ "ở trang Soạn bài" (đề xuất của Thợ Máy T-034).

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
- Chốt 2026-10-15 (Lá Chắn T-026): **giữ** việc thư viện AI đọc cài đặt proxy và chứng chỉ của máy (`HTTPS_PROXY`, `SSL_CERT_FILE`) để chạy được trong mạng công ty; đã ghi sổ rủi ro `docs/team/security.md` mục 6.
- Chốt thêm 2026-10-14 (phiếu T-022): bài **không nêu thời gian trả báo giá** qua Zalo; **không nói giá dưới bất kỳ dạng nào** (kể cả so sánh rẻ/đắt giữa vật liệu); khu vực phục vụ **gồm cả Bình Dương và Bà Rịa–Vũng Tàu cũ** (sáp nhập vào TP.HCM từ 1/7/2025), địa chỉ cụ thể vẫn chỉ 9 địa chỉ trên trang Liên hệ.
- **Ca sửa thật đáng nhớ, câu khách hay hỏi qua Zalo: để sau.** Khi viết từng bài, app hỏi anh "chất liệu thật" (bước 3 quy trình).
- Thông tin doanh nghiệp đã soạn (từ website) nằm trong `config/business_profile.md` của **PR #3** (chưa gộp vào `main`): hotline 03.4444.07.17, trụ sở 728/1 Lê Trọng Tấn, Bình Tân, bảo hành 2 năm, gần 30 thợ, dịch vụ và kiến thức nghề. Dòng nào đánh dấu `[CẦN XÁC NHẬN]` thì AI không dùng.
- PR #3 đang xung đột nhỏ với `main` ở `CLAUDE.md` (hai bên cùng thêm dòng Trạng thái, cách sửa là giữ cả hai). Có thẻ hỏi "gộp bản mới nhất vào PR #3" chưa được trả lời.
- 2026-10-16: Chủ dự án 2026-10-16: chưa trả lời 4 câu hỏi Giai đoạn 4; yêu cầu phần mềm **vẫn chạy ổn định khi chưa có câu trả lời** và làm tiếp các việc khác. Phần nào cần câu trả lời thì để tùy chọn (mặc định an toàn, đổi trong cấu hình); ghi SEO lên website chờ câu 1, 2, trong lúc đó chép tay.
- Chủ dự án trả lời 2026-10-16: **1A** (bật Abilities của SiteSEO để phần mềm ghi tiêu đề, mô tả, từ khóa chính vào bài nháp), **2A** (tạo tài khoản WordPress vai Biên tập viên riêng cho phần mềm), **3A** (đuôi " | Pro-Metal" khi tiêu đề còn chỗ, dưới 60 ký tự), **4A** (dọn khối Organization rỗng của SiteSEO, mô tả thừa "3 chi nhánh…" ở trang chủ, mức giá "$$"; chủ dự án hoặc người làm web làm), **5A** (đồng ý thêm thư viện Pillow cho Giai đoạn 3).

- Chủ dự án trả lời 5 câu Giai đoạn 3 ngày 2026-10-19 (báo cáo `docs/team/reports/T-046-tho-may.md` mục 8): **1A** thêm thư viện `pillow-heif` để đọc ảnh HEIC của iPhone (Lá Chắn quét lỗ hổng trước khi dùng); **2A** EXIF giữ GPS, ngày chụp, hãng và đời máy, bỏ số seri máy, tên chủ máy, khối dữ liệu riêng của hãng; **3A** thẻ ảnh đặt theo tên thư mục trong Drive (ví dụ `CT012 - Cổng inox - Hải Châu/truoc`), app không ghi gì vào Drive, thẻ sửa tay chỉ nhớ trên máy đang dùng; **4A** viết alt bằng Claude Sonnet, tạo ảnh bằng Gemini (mô hình ghi trong `config/ai.toml`, đổi được); **5A** ảnh trong bài dùng file đầy đủ 1600 px để GPS tới người xem và Google (không để WordPress tự chọn cỡ nhỏ).

### 7.5 Tính năng và nội dung

- **Giữ nguyên vị trí GPS trong ảnh** ("nhiều khi đó là mục đích cố ý"). Phiếu T-007 xóa GPS đã hủy; ghi trong sổ rủi ro `docs/team/security.md` mục 6. Khi nén WebP phải chép lại EXIF.
- Anh muốn **tự nhập khóa API trong phần mềm** (Gemini, ChatGPT, Claude): đã làm ở Cài đặt → 🔌 Kết nối; khóa lưu trong `.env`, không bao giờ hiện lại.
- Anh sẽ dùng **Gemini** (và có thể ChatGPT, Claude). Cách nối ChatGPT/Gemini vào phần viết bài (T-018) đang chờ anh chọn (mục 6).
- AI viết bài có bật **mô hình dự phòng**: nếu Claude từ chối một yêu cầu thì tự chạy lại bằng mô hình khác.
- Giai đoạn 6 (theo dõi thứ hạng) đã bỏ khỏi giao diện demo. Anh chốt 2026-10-15: **giữ**.
- Chốt 2026-10-15: **không có hãng AI mặc định**, giữ đủ Claude, ChatGPT, Gemini; anh tự đổi khi cần.
- Chốt 2026-10-15: kế hoạch SEO và yêu cầu phần mềm anh soạn ngày 07/10 đưa vào repo ở `docs/plan/` (đọc `docs/plan/README.md` trước: có những chỗ đã lệch với quyết định mới hơn).

### 7.6 Lịch sử ngắn

- 06/10: khởi tạo; xong Giai đoạn 0, Giai đoạn 1 và giao diện demo (PR #2). Anh duyệt bố cục demo lần 2, chốt phần mềm tập trung vào viết bài.
- 14/10 sáng: PR #2 gộp vào `main`; soạn hồ sơ doanh nghiệp (PR #3); Giai đoạn 2 phần 1 (Claude viết bài) đẩy lên `main`.
- 14/10 chiều tối: lập đội agent; T-001 → T-021 xong (kiểm định bảo mật, gia cố lọc nội dung AI, tự lưu bài, nhập khóa API).
- 14/10 tối: anh chuyển sang máy mới và project mới; viết file này.
- 15/10 sáng: T-018, T-023 lên `main`. Có thêm Chỉ Huy thứ hai (Claude Desktop trên máy anh); lập phiếu điều phối chung; đưa `docs/plan/` lên repo.

### 7.7 Hai Chỉ Huy (chốt 2026-10-15)

- Có **hai Chỉ Huy** ở hai tài khoản Claude khác nhau, chạy luân phiên: một bên chỉ làm khi bên kia dừng, mà thường dừng vì hết lượt dùng nên không kịp dặn lại.
- Hai bên liên lạc **chỉ qua phiếu điều phối chung** `docs/team/dong-bo.md`. Quy tắc nằm trong file đó: đầu phiên ghi nhận quyền và push ngay, sau mỗi bước cập nhật "Đang làm dở" và push.
- Phiên "Điều Phối" thứ ba từng mở trên máy anh đã bị bỏ (làm việc chưa đúng quy trình), không tính.

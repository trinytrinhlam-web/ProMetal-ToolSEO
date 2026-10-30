# SEO App — hướng dẫn cho Claude

## Dự án là gì

Phần mềm Python cài trên máy (Windows và Mac) giúp triển khai kế hoạch SEO cho một website WordPress: nghiên cứu, viết bài bằng AI, xử lý ảnh, tối ưu meta/schema, gắn liên kết nội bộ, đăng nháp / hẹn giờ / đăng ngay, theo dõi thứ hạng qua Google Search Console.

Người dùng là chủ dự án: hiểu khái niệm lập trình nhưng ít dùng Git và dòng lệnh. Luôn giải thích bằng tiếng Việt, ngắn gọn, không giả định kiến thức chuyên sâu.

Ưu tiên số 1: nội dung có ích thật cho người đọc và tối ưu SEO. Không tạo bài sáo rỗng, không sản xuất nội dung hàng loạt.

## Quyết định đã chốt (không tự ý đổi, muốn đổi phải hỏi người dùng)

- Chạy cục bộ: web app Streamlit mở ở localhost. Người dùng khởi động bằng cách bấm đúp `run.bat` (Windows) hoặc `run.command` (Mac).
- Quản lý Python và thư viện bằng uv (`pyproject.toml` + `uv.lock`).
- Dữ liệu dùng chung không lưu trong máy, để 2 máy luôn thấy cùng trạng thái:
  - Bài viết, lịch đăng: WordPress (REST API + Application Password)
  - Kế hoạch từ khóa, lịch nội dung: Google Sheets
  - Thứ hạng: Google Search Console API
  - Ảnh thật: các thư mục cục bộ do người dùng khai báo (USB, thư mục Google Drive for Desktop)
  - Trong máy chỉ có cache SQLite; xóa đi vẫn tạo lại được.
- Hẹn giờ đăng: gửi bài sang WordPress với trạng thái `future` kèm ngày giờ. App không cần chạy nền.
- Mặc định mọi bài là bản nháp (`draft`). Đăng ngay (`publish`) phải được người dùng bấm xác nhận.
- AI: một lớp provider chung, hỗ trợ Anthropic, OpenAI, Google Gemini. Mô hình cho từng việc (nghiên cứu, viết, rà soát, meta, alt ảnh, tạo ảnh) khai báo trong file cấu hình, đổi được mà không sửa code. **Không có hãng mặc định** (chốt 2026-10-15): giữ đủ cả 3, chủ dự án tự đổi hãng khi cần.
- Google: dùng service account (file JSON nằm ngoài repo, đường dẫn khai báo trong `.env`).
- Có màn hình đăng nhập bằng mật khẩu; `.env` chỉ lưu mã băm của mật khẩu, kèm script để người dùng tạo mã băm.
- Phần mềm tập trung vào **viết bài** (người dùng chốt 2026-10-06). Menu trên cùng: Bài viết · Soạn bài · Kế hoạch · Cài đặt · Kết nối WordPress.
  - Mọi phần nội dung do AI tạo (ý định, dàn ý từng mục, từng phần của bài, meta, prompt ảnh) đều có nút viết lại; viết lại một phần không đụng tới phần khác, và quay lại được bản trước.
  - Có AI kiểm tra văn phong: thân thiện, tự nhiên (không máy móc), dễ đọc, cụ thể, chuẩn SEO; tô câu có vấn đề ngay trong bài, kèm gợi ý và nút Áp dụng / Bỏ qua.
  - Bài đánh dấu chỗ cần ảnh ngay trong từng phần; mỗi chỗ chọn ảnh thật (từ thư mục) hoặc ảnh AI — ảnh AI luôn kèm prompt xem/sửa/sao chép được.
  - Trang Kế hoạch nhận kế hoạch người dùng cung cấp (tải file, dán chữ, link Google Sheets); AI đề xuất thay đổi, người dùng tick duyệt rồi mới cập nhật. Có "thông tin nền doanh nghiệp" dùng cho mọi bài.
- SEO trên website (chốt 2026-10-16): phần mềm ghi tiêu đề, mô tả, từ khóa chính vào SiteSEO qua **Abilities** (chủ dự án bật trong SiteSEO), chỉ cho bài nháp do app tạo; dùng tài khoản WordPress vai **Biên tập viên** riêng; tiêu đề SEO thêm đuôi " | Pro-Metal" khi còn chỗ (dưới 60 ký tự).
- Thư viện ảnh **Pillow** được duyệt cho Giai đoạn 3 (chốt 2026-10-16).
- Chủ dự án chốt 2026-10-20 (phiếu T-058): **nâng lên Pillow 13** (lựa chọn A), dù Streamlit khóa `pillow<13`, để vá 53 khuyến cáo của Pillow 12.3.0 mà Lá Chắn T-047 tìm ra. Thợ Máy nâng bằng `override-dependencies`, chạy đủ test, Chỉ Huy mở app thử mọi trang; hỏng thì quay về bản cũ.
- Chủ dự án chốt 2026-10-20: **rút gọn phần ảnh** vì ảnh thợ gửi qua Zalo đã bị nén, mất GPS (thử 99 ảnh trên website: không ảnh nào còn GPS). Làm màn hình chọn ảnh T-056 và các phiếu bắt buộc trước nó (ưu tiên T-061 chặn shortcode); **hoãn** tạo ảnh AI (T-053), phiếu GPS (T-072) và các lỗi nhỏ không chặn (T-064, T-057); **chuyển sớm** sang Giai đoạn 4 (SEO) và 5 (đăng bài).
- Chủ dự án trả lời 5 câu Giai đoạn 3 ngày 2026-10-19 (báo cáo `docs/team/reports/T-046-tho-may.md` mục 8): **1A** thêm thư viện `pillow-heif` để đọc ảnh HEIC của iPhone (Lá Chắn quét lỗ hổng trước khi dùng); **2A** EXIF giữ GPS, ngày chụp, hãng và đời máy, bỏ số seri máy, tên chủ máy, khối dữ liệu riêng của hãng; **3A** thẻ ảnh đặt theo tên thư mục trong Drive (ví dụ `CT012 - Cổng inox - Tân Phú/truoc`), app không ghi gì vào Drive, thẻ sửa tay chỉ nhớ trên máy đang dùng; **4A** viết alt bằng Claude Sonnet, tạo ảnh bằng Gemini (mô hình ghi trong `config/ai.toml`, đổi được); **5A** ảnh trong bài dùng file đầy đủ 1600 px để GPS tới người xem và Google (không để WordPress tự chọn cỡ nhỏ).
- Chủ dự án trả lời 5 câu rà soát Giai đoạn 3 ngày 2026-10-30 (T-093): **1A** phần mềm gắn ảnh «Gửi nháp» vào bài nháp (ảnh không hiện trong danh sách Media công khai trước khi bài đăng, T-110); **2** ghi sổ rủi ro 4 lỗi nhỏ (shortcode khi tự sửa bài trên website, 2 lỗi libheif chưa có bản sửa, giấy phép GPLv2 của x265, khe nhỏ kho thẻ ảnh); **3** sửa câu sổ rủi ro về quyền `unfiltered_html`; **4** cho nâng pillow-heif ngay khi có bản mang libheif ≥ 1.23.7, sau khi Lá Chắn quét, không cần hỏi lại; **5** mang sang sau Giai đoạn 3: tạo ảnh AI (T-053), GPS thẻ phụ (T-072), lỗi nhỏ đọc thư mục ảnh (T-064), chạy test trên Mac, lượt test Linux. Cùng ngày, cho LC-T107-2 (libheif 1.23.6 còn lỗi làm treo, chưa có pillow-heif mới): **tạm không nhận ảnh HEIC** (một công tắc, T-107 lượt 3) cho tới khi nâng được; điều này tạm thay quyết định 1A ngày 2026-10-19.

## Bí mật và bảo mật

- Khóa API, mật khẩu, file JSON service account chỉ nằm trong `.env` hoặc ngoài repo. Không bao giờ commit.
- Luôn giữ `.env.example` cập nhật: đủ tên biến, không có giá trị thật, có chú thích tiếng Việt cho từng biến.
- Không in khóa hay mật khẩu ra log hoặc giao diện.

## Môi trường làm việc

- Code được viết trên cloud (Ubuntu) nhưng chạy trên Windows và Mac. Bắt buộc:
  - Dùng `pathlib`, không viết cứng đường dẫn, không dùng lệnh chỉ có trên một hệ điều hành.
  - Đọc/ghi file với `encoding="utf-8"` (nội dung tiếng Việt).
  - Múi giờ mặc định `Asia/Ho_Chi_Minh`; lưu thời gian kèm múi giờ.
- Trên cloud (`CLAUDE_CODE_REMOTE=true`) không có `.env` và không gọi được API thật. Kiểm thử bằng dữ liệu giả (mock); test không bao giờ gọi WordPress, AI hay Google thật.
- Lệnh chuẩn:
  - `uv sync` — cài thư viện
  - `uv run pytest` — kiểm thử
  - `uv run ruff check .` — kiểm tra code
  - `uv run streamlit run app/main.py` — chạy app

## Cấu trúc thư mục (đề xuất, được điều chỉnh ở Giai đoạn 0)

```
seo-app/
├── CLAUDE.md
├── README.md            # hướng dẫn cài & chạy cho người dùng, tiếng Việt
├── pyproject.toml
├── .env.example
├── run.bat / run.command
├── config/              # cấu hình không bí mật: mô hình AI theo việc, quy tắc nội dung
├── app/                 # giao diện Streamlit
├── seo_app/
│   ├── ai/              # provider Anthropic / OpenAI / Gemini, prompt
│   ├── content/         # quy trình viết bài, checklist chất lượng
│   ├── images/          # đọc thư mục ảnh, nén WebP, đổi tên, alt
│   ├── wordpress/       # client REST API
│   ├── google/          # Sheets, Search Console
│   └── storage/         # cache SQLite
├── tests/
└── scripts/
```

## Quy trình nội dung (bắt buộc)

1. Xác định ý định tìm kiếm của từ khóa.
2. Nghiên cứu các kết quả đứng đầu: họ đã nói gì, còn thiếu gì → bài mình phải bổ sung điều mới.
3. Người dùng thêm "chất liệu thật": kinh nghiệm, số liệu, câu hỏi khách hay hỏi, ảnh thật.
4. Tạo dàn ý → người dùng duyệt → mới viết toàn bài.
5. AI tự rà soát bài theo checklist chất lượng (trong `config/`) và sửa trước khi đưa người dùng xem.
6. Tạo meta title, meta description, schema, gợi ý liên kết nội bộ, alt ảnh.
7. Gửi sang WordPress dạng nháp (hoặc hẹn giờ / đăng ngay nếu người dùng chọn).

Cấm: mở bài kiểu "Trong thời đại…", "Hãy cùng tìm hiểu…"; câu chung chung không có ví dụ; nhồi từ khóa; bịa số liệu hoặc nguồn.

## Lộ trình

- [x] Giai đoạn 0 — Bộ khung: `pyproject.toml` (uv), app Streamlit có màn hình đăng nhập, đọc cấu hình từ `.env`, `.env.example`, `run.bat` + `run.command`, SessionStart hook trong `.claude/settings.json` chạy `uv sync` khi `CLAUDE_CODE_REMOTE=true`, pytest + ruff, README tiếng Việt hướng dẫn cài trên Windows và Mac.
- [x] Giai đoạn 1 — WordPress: kiểm tra kết nối, lấy chuyên mục/thẻ, tạo bài nháp, tải ảnh lên thư viện, đặt ảnh đại diện.
- [x] Giai đoạn 2 — AI viết bài: lớp provider (Anthropic, OpenAI, Gemini), quy trình nội dung ở trên, nút viết lại từng phần, AI kiểm tra văn phong, thử mù mô hình (trong Cài đặt), kiểm tra khóa 3 hãng. Xong 2026-10-16. Còn 2 phiếu dọn lỗi Thấp không chặn: T-044, T-045.
- [ ] Giai đoạn 3 — Ảnh: chỗ cần ảnh trong bài; chọn ảnh từ thư mục đã khai báo (USB / Drive), nén WebP, đổi tên chuẩn SEO, **giữ nguyên vị trí GPS trong ảnh** (người dùng chốt 2026-10-14: có chủ đích; khi nén WebP phải chép lại EXIF), viết alt bằng AI; ảnh AI kèm prompt, tạo ảnh bằng AI.
- [ ] Giai đoạn 4 — Tối ưu on-page: meta, schema JSON-LD, liên kết nội bộ dựa trên danh sách bài trên WordPress. Thiết kế xong (T-033), phiếu T-036 → T-042. Đã lên `main`: schema FAQPage (T-038). Đang kiểm: meta (T-036), danh sách bài đã đăng + cache (T-037).
- [ ] Giai đoạn 5 — Kế hoạch & lịch: nhận kế hoạch người dùng cung cấp (file / dán / Google Sheets), AI đề xuất cập nhật để duyệt, đồng bộ Google Sheets, hẹn giờ đăng.
- [ ] Giai đoạn 6 — Theo dõi: Search Console (từ khóa, vị trí, lượt click) theo từng bài. *(Chủ dự án chốt 2026-10-15: **giữ**. Giao diện demo hiện chưa có trang này; khi làm thì hỏi chủ dự án đặt ở đâu trong menu.)*

## Câu hỏi còn mở (hỏi người dùng khi tới giai đoạn liên quan)

- Đã trả lời 2026-10-16: 4 câu Giai đoạn 4 và Pillow (1A 2A 3A 4A 5A, xem "Quyết định đã chốt"). Việc chủ dự án làm trên website: `TIEN-DO.md` mục 4.
- Đã chốt 2026-10-14: plugin SEO là **SiteSEO** (ghi meta/schema theo SiteSEO). Tên miền suachuacuasat.com. **Không có staging**: làm việc trực tiếp trên site chính thức, nên mọi bài thử phải là nháp.

## Cách làm việc

- Mỗi phiên làm một giai đoạn hoặc một phần nhỏ của giai đoạn, kết thúc bằng một PR riêng.
- Trước khi sửa code: trình bày kế hoạch ngắn bằng tiếng Việt.
- Viết test cho phần logic; chạy test liên quan tới phiếu và `uv run ruff check .` trước khi báo xong. Toàn bộ `uv run pytest` do Chỉ Huy chạy trên Windows một lần khi gộp vào `main` (chủ dự án chốt 2026-10-20).
- Không thêm thư viện khi chưa cần; khi thêm, giải thích ngắn lý do.
- Xong một giai đoạn: đánh dấu [x] trong Lộ trình, ghi một dòng vào mục Trạng thái, cập nhật README nếu cách dùng thay đổi.

### Đội agent (từ 2026-10-14)

- Dự án làm theo đội agent do **Chỉ Huy** (Claude) điều phối: Thợ Máy (logic), Họa Sĩ (giao diện), Ngòi Bút (nội dung, prompt), Soi Lỗi (kiểm thử), **Lá Chắn** (bảo mật, có quyền chặn), Thư Ký (tài liệu).
- Điểm bắt đầu cho mọi AI: `AGENTS.md`. Quy tắc, chính sách bảo mật, mẫu phiếu và báo cáo, bảng việc: `docs/team/`. Hồ sơ và model từng agent: `.claude/agents/`.
- Mọi việc đi qua phiếu (`docs/team/tickets/`) và báo cáo (`docs/team/reports/`). Phiếu có sửa code phải qua Soi Lỗi và Lá Chắn trước khi đóng.
- Chủ dự án chốt: agent điều phối tự gọi agent phụ; ưu tiên chất lượng, không cần tiết kiệm chi phí model; push thẳng lên `main`, không tạo nhánh mới, không mở PR.
- Từ 2026-10-14 (chủ dự án chốt): mỗi agent chạy ở **một phiên con riêng** dưới phiên "Điều phối", tên phiên ghi rõ vai và phiếu (ví dụ "Thợ Máy · T-018 …"). Mỗi phiếu dùng **một nhánh tạm** `team/T-xxx`; Soi Lỗi và Lá Chắn kiểm trên nhánh đó; Lá Chắn ĐẠT thì Chỉ Huy gộp vào `main` và xóa nhánh. `main` chỉ chứa code đã qua kiểm định.
- Từ 2026-10-15 (chủ dự án chốt): có **hai Chỉ Huy** ở hai tài khoản Claude, chạy luân phiên (một bên chỉ làm khi bên kia dừng, thường vì hết lượt dùng). Hai bên liên lạc qua **phiếu điều phối chung** `docs/team/dong-bo.md`: đọc đầu phiên, ghi nhận quyền, cập nhật và push sau mỗi bước.

### Giao diện và trang demo

- Giao diện: theme trong `.streamlit/config.toml` (font Be Vietnam Pro, màu chủ đạo xanh ngọc `#0F7B6C`, có chế độ tối), CSS chung trong `app/assets/style.css`, mảnh HTML dùng chung trong `seo_app/ui.py`. Menu đặt trên cùng (`st.navigation(position="top")`).
- App có giao diện demo cho mọi chức năng chưa làm (nhãn "Bản demo", dữ liệu mẫu trong `seo_app/demo.py`; nút chạy thử trên dữ liệu mẫu, không gọi AI hay mạng). Người dùng đã duyệt bố cục này (lần 2, 2026-10-06).
- Khi làm thật một giai đoạn: thay phần demo tương ứng bằng chức năng thật, giữ bố cục đã duyệt (muốn đổi nhiều thì hỏi người dùng), xóa phần mẫu không còn dùng trong `seo_app/demo.py`.
- Trang mới phải được thêm vào `PAGES` trong `app/main.py`; `tests/test_app_pages.py` tự mở mọi trang và mọi bước soạn bài để bắt lỗi.
- Lưu ý Streamlit: nhãn của `segmented_control`/`pills` phải cố định giữa các lần chạy (đừng để `format_func` phụ thuộc trạng thái), nếu không widget bị coi là mới và mất lựa chọn.

### Làm việc trên 2 máy (máy công ty và máy nhà), đồng bộ qua GitHub

Người dùng chạy Claude Code ngay trên máy của mình để vừa làm vừa xem app chạy thật. Claude tự chạy các lệnh git, người dùng không cần gõ lệnh.

- Đầu buổi: chạy `git status` và `git pull` để lấy code mới nhất từ máy kia trước khi sửa. Nếu còn thay đổi chưa commit thì hỏi người dùng trước.
- Trong buổi: sau mỗi thay đổi xem được trên giao diện, nhắc người dùng mở app (`run.bat` / `run.command`, hoặc Claude chạy `uv run streamlit run app/main.py`) để tự kiểm tra.
- Cuối buổi (hoặc khi người dùng nói sắp nghỉ): tóm tắt việc đã làm, chạy `uv run pytest` và `uv run ruff check .`, rồi **đề nghị** commit và push lên GitHub. Chỉ commit/push khi người dùng đồng ý.
- Mỗi giai đoạn làm trên một nhánh riêng, xong thì mở PR. Ghi tên nhánh đang làm vào mục Trạng thái để máy kia biết chuyển sang đúng nhánh.

## Trạng thái

- 2026-10-06: Khởi tạo dự án. Chưa có code.
- 2026-10-06: Xong Giai đoạn 0 — bộ khung uv + Streamlit, đăng nhập bằng mã băm PBKDF2 (`seo_app/auth.py`), cấu hình từ `.env` (`seo_app/config.py`), `run`/`set_password` (.bat/.command), SessionStart hook, pytest + ruff, README.
- 2026-10-06: Xong Giai đoạn 1 (nhánh `claude/wizardly-brahmagupta-f0w8d8`) — `seo_app/wordpress/` (kiểm tra kết nối, chuyên mục/thẻ, tạo bài nháp, tải ảnh, ảnh đại diện; chỉ tạo `draft`), app nhiều trang (`app/views/`), trang WordPress, README mục Kết nối WordPress.
- 2026-10-06: Thêm giao diện demo toàn bộ phần mềm (cùng nhánh, PR #2): menu nhóm Tổng quan / Nội dung / Theo dõi / Hệ thống; trang Kế hoạch từ khóa, Viết bài (7 bước), Thử mù, Ảnh, Lịch đăng, Thứ hạng, Cài đặt dùng dữ liệu mẫu.
- 2026-10-06: Làm lại giao diện demo theo yêu cầu người dùng (cùng nhánh, PR #2): tập trung viết bài; menu trên cùng; Soạn bài 5 bước với nút viết lại từng phần, AI kiểm tra văn phong, chỗ cần ảnh (ảnh thật / ảnh AI + prompt); trang Kế hoạch nhận kế hoạch và đề xuất thay đổi; bỏ các trang Ảnh, Lịch đăng, Thứ hạng riêng (thử mù chuyển vào Cài đặt).
- 2026-10-14: Giai đoạn 2, phần 1 (đã push thẳng lên `main`): `seo_app/ai/` (lớp provider chung, Anthropic qua thư viện `anthropic`, mô hình theo việc trong `config/ai.toml`), `seo_app/content/` (nghiên cứu có tìm web → dàn ý → viết → tự rà soát và sửa một lượt → viết lại từng phần; quy tắc trong `config/content.toml`, hồ sơ doanh nghiệp `config/business_profile.md` bỏ dòng `[CẦN XÁC NHẬN]`). Trang Soạn bài bước 1–3 chạy AI thật; SEO và Xuất bản vẫn demo. Bài đang soạn chỉ nằm trong session (F5 là mất).
- 2026-10-14: Lập đội agent (`AGENTS.md`, `docs/team/`, `.claude/agents/`): 7 agent, quy tắc, chính sách bảo mật, mẫu phiếu/báo cáo/biên bản bảo mật, bảng việc. Giao T-001 (Lá Chắn: kiểm định bảo mật toàn repo) và T-002 (Soi Lỗi: kiểm thử Giai đoạn 2 phần 1).
- 2026-10-14: Thêm `config/business_profile.md` (hồ sơ doanh nghiệp để AI dùng khi viết bài), soạn từ website; người dùng đã trả lời các câu hỏi chính; mục 7 (chất liệu thật) điền sau. Nhánh `claude/project-thread-bcuk2m` (PR #3), gộp vào `main` ngày 2026-10-14 kèm phiếu T-022.
- 2026-10-15: Gộp T-018 (ChatGPT qua `openai`, Gemini qua `google-genai`; chủ dự án duyệt thư viện 2026-10-14) và T-023 (nút Kiểm tra khóa cả 3 hãng) vào `main`. Soi Lỗi đạt, Lá Chắn ĐẠT (chạy tạm Opus 5.5, kiểm lại bằng Fable sau 01/11). Đổi hãng cho từng việc: sửa `provider`/`model` trong `config/ai.toml`.
- 2026-10-15: Chủ dự án chốt: không có hãng AI mặc định (đủ 3 hãng, tự đổi khi cần); giữ Giai đoạn 6. Lập phiếu điều phối chung cho 2 Chỉ Huy (`docs/team/dong-bo.md`). Đưa kế hoạch SEO và yêu cầu phần mềm của chủ dự án vào `docs/plan/`.
- 2026-10-15: Gộp T-022 (hồ sơ doanh nghiệp theo trả lời chủ dự án) và T-024 (bộ lọc hồ sơ bỏ cả ý có nhãn `[CẦN XÁC NHẬN]`) vào `main`. Soi Lỗi đạt, Lá Chắn ĐẠT (Opus tạm).
- 2026-10-15: Gộp T-027 vào `main`: bộ test chạy xanh trên Windows (bộ chặn mạng cho qua đúng cặp socket nội bộ của asyncio, chặn ConnectEx; tên ngắn cho test dữ liệu lớn). Trên Windows 2.358 test qua, 0 hỏng.
- 2026-10-15: Chỉ Huy B gộp T-026 (lớp AI chịu được thư viện lệch phiên bản, câu lỗi 400 cố định, địa chỉ máy chủ chính thức cố định). Chỉ Huy A gộp T-029 + T-030 (bộ chặn mạng của test chặn thêm UDP, tra tên; test chạy được trên Linux/Mac) và T-028 (nội dung hỏng từ máy chủ AI ra câu lỗi tiếng Việt; bỏ qua `*_CUSTOM_HEADERS`). Windows 3.110 test qua.
- 2026-10-15: Gộp T-026 vào `main`: lớp AI chịu được thư viện lệch phiên bản, câu lỗi 400 cố định (không chép câu máy chủ), client 3 hãng dùng địa chỉ chính thức cố định. Lá Chắn ĐẠT (Opus tạm).
- 2026-10-15: Gộp T-025 vào `main`: test đo tốc độ không còn đỏ oan (đo xen kẽ nhỏ/lớn, lấy lần nhanh nhất; ngưỡng giữ nguyên). Lá Chắn ĐẠT (Opus tạm).
- 2026-10-15: Gộp T-019 vào `main`: thử mù mô hình ở Cài đặt → 🤖 Mô hình AI (2–3 ứng viên, chấm xong mới hiện tên; bảng việc–mô hình đọc thật từ `config/ai.toml`). Lá Chắn ĐẠT (Opus tạm).
- 2026-10-16: Gộp T-032 vào `main`: bộ lọc hồ sơ nhận cả nhãn `[CẦN XÁC NHẬN]` gõ sai (dính chữ, không dấu, ngoặc tròn, vắt dòng); nhãn trên tiêu đề giấu cả mục. Lá Chắn ĐẠT (Opus tạm).
- 2026-10-16: Gộp T-031 vào `main`: địa chỉ trần, `www.`, email trong chữ AI và chữ ngoài không còn thành link (chèn ký tự rộng 0; Giai đoạn 5 phải gỡ trước khi gửi WordPress). Lá Chắn ĐẠT (Opus tạm).
- 2026-10-16: Gộp T-043 vào `main`: bộ lọc hồ sơ nhận nhãn có ký tự lạ chen vào (`[**CẦN XÁC NHẬN**]`, `[⚠ …]`), nửa nhãn qua dòng trống, tiêu đề thụt lề. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), 3 lỗi Thấp theo dõi ở T-045.
- 2026-10-16: Gộp T-034 vào `main` (7 lỗi Thấp lớp AI và thử mù; chặn `*_CUSTOM_HEADERS` bằng khung nhìn `os` đã lọc thay vì gỡ biến môi trường). Lá Chắn ĐẠT (Opus tạm). **Xong Giai đoạn 2.** Linux 4.658 test qua.
- 2026-10-16: Chủ dự án trả lời 2026-10-16: **1A** (bật Abilities của SiteSEO để phần mềm ghi tiêu đề, mô tả, từ khóa chính vào bài nháp), **2A** (tạo tài khoản WordPress vai Biên tập viên riêng cho phần mềm), **3A** (đuôi " | Pro-Metal" khi tiêu đề còn chỗ, dưới 60 ký tự), **4A** (dọn khối Organization rỗng của SiteSEO, mô tả thừa "3 chi nhánh…" ở trang chủ, mức giá "$$"; chủ dự án hoặc người làm web làm), **5A** (đồng ý thêm thư viện Pillow cho Giai đoạn 3).
- 2026-10-16: Gộp T-038 vào `main`: dựng và kiểm schema FAQPage không cần mạng (`seo_app/onpage/schema.py`; không xuất Article/Breadcrumb/LocalBusiness vì site đã tự có). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), 3 điều kiện làm ở T-041.
- 2026-10-19: Chủ dự án trả lời 5 câu Giai đoạn 3 (1A 2A 3A 4A 5A, xem "Quyết định đã chốt"). Chỉ Huy A gộp T-036, T-037 (Giai đoạn 4, logic), T-044, T-046 (thiết kế Giai đoạn 3); lập phiếu code Giai đoạn 3.
- 2026-10-20: Chỉ Huy B gộp T-048 vào `main` (Giai đoạn 3, phần đầu: đọc thư mục ảnh an toàn, `seo_app/images/folders.py`; chặn `..`, symlink, junction, chỉ đọc). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm): phải chạy test trên Mac/Linux trước khi gộp giao diện chọn ảnh (T-063). Trước đó Chỉ Huy A đã gộp T-045, T-047 (Pillow, pillow-heif) và T-042 (ghi meta SEO SiteSEO lên bài nháp).
- 2026-10-20: Chỉ Huy B gộp T-058 vào `main`: **Pillow 13.0.0** (ép bằng `override-dependencies` vì Streamlit 1.65 khai báo `pillow<13`), vá 53 khuyến cáo của 12.3.0. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm); chủ dự án cùng Chỉ Huy mở app thật xem mọi trang: không lỗi. Windows 7.483 test qua. Chủ dự án đặt lại mật khẩu đăng nhập app trên máy Windows bằng `set_password.bat`.
- 2026-10-20: Chỉ Huy B gộp T-051 vào `main`: quy tắc viết alt (`[alt]`, 6 ví dụ) và `[images]` trong `config/content.toml`; `[tasks.alt]` (Claude Sonnet) và `[tasks.image]` (Gemini, ghi sẵn nhưng tắt, chờ T-062) trong `config/ai.toml`. Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm). Windows 7.519 test qua.
- 2026-10-20: Chỉ Huy B gộp T-050 vào `main`: lớp AI đọc ảnh cho cả 3 hãng và gợi ý alt (`seo_app/images/alt.py`); ảnh gửi AI phải qua bộ kiểm "danh sách cho phép" (không còn EXIF/GPS/XMP/chú thích), thẻ và từ khóa gửi AI qua lớp lọc ký tự (không lộ đường dẫn máy). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), lỗi Thấp dọn ở T-066. Windows 8.009 test qua.
- 2026-10-20: Chỉ Huy B gộp T-049 vào `main`: xử lý ảnh thật (`seo_app/images/process.py`, `naming.py`): xoay đúng chiều, cạnh dài 1600 px, WebP **giữ GPS** cùng ngày chụp, hãng, đời máy (bỏ số seri, tên chủ máy, MakerNote); bản gửi AI dựng lại từ điểm ảnh, không còn metadata hay hồ sơ màu; tên file không dấu theo nội dung. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), lỗi Thấp dọn ở T-067. Windows 8.278 test qua. Chưa thử ảnh thật.
- 2026-10-20: Chỉ Huy B gộp T-062 vào `main`: cấu hình việc ảnh đọc an toàn; bật được `[tasks.image]` mà trang Soạn bài không đòi khóa Gemini; quy tắc alt từ `config/` chỉ bổ sung, phần bảo vệ nằm trong code; ảnh AI luôn có tiền tố «Minh họa». Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm). Windows 8.487 test qua. Báo cáo tiến độ cho chủ dự án: Google Docs trong thư mục Drive "SEO-Tool".
- 2026-10-20: Chỉ Huy B gộp T-052 vào `main`: thẻ ảnh lấy từ tên thư mục Drive theo danh sách cố định (mã công trình, hạng mục, khu vực, trước/sau, ảnh thật/AI), thẻ sửa tay lưu trong `data/image_tags.sqlite`. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), lỗi còn lại dọn ở T-070.
- 2026-10-20: Chỉ Huy B gộp T-067 vào `main`: dọn 3 lỗi Thấp xử lý ảnh (GPS ghi sai chuẩn bị bỏ và báo, ảnh xem trước luôn kiểm Pillow 13, khóa luồng khi mở ảnh). Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN.
- 2026-10-20: Chỉ Huy B gộp T-054 và T-068 vào `main`: gửi nháp kèm ảnh (tải ảnh lên WordPress, chèn `<figure>`, alt và chú thích đã làm sạch) và sửa bước tự chỉnh alt ảnh AI. Thử 8 ảnh thật trên website: xử lý tốt, không ảnh nào còn GPS (ảnh Zalo). Windows 9.477 test qua.
- 2026-10-21: Chỉ Huy B gộp T-070 vào `main`: nhận ảnh AI theo tên thư mục/tên file ("minh họa", "trí tuệ nhân tạo", tên công cụ tạo ảnh), kho thẻ sửa tay kiểm cấu trúc trước khi đọc. Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm), 2 lỗi Thấp dọn ở T-074 trước T-056. Windows 9.740 test qua.
- 2026-10-21: Chỉ Huy B gộp T-061 vào `main`: mọi dấu `[` `]` app gửi lên WordPress (nội dung, tiêu đề, đoạn trích, alt, chú thích, ô Media) thành `&#91;` `&#93;` nên shortcode không chạy; chữ SEO dạng shortcode bị chặn. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm); LC-T061-1 (Cao, `certifi` có chứng chỉ bị lộ khóa) sửa gấp ở T-075, chủ dự án đã duyệt. Windows 9.915 test qua.
- 2026-10-21: Chỉ Huy B gộp T-074 vào `main`: file thẻ ảnh sửa tay kiểm cấu trúc theo danh sách và trong cùng giao dịch với thao tác (đóng LC-T070-1, -2), giới hạn độ dài giá trị, nhận thêm tên ảnh AI (chữ dính số, "AIgen", "mô phỏng"). Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (Opus tạm); tên công cụ AI gõ khác dạng chuẩn dọn ở T-077 trước T-056. Windows 10.135 test qua.
- 2026-10-21: Chỉ Huy B gộp T-075 (`certifi` 2026.10.19, vá GHSA-6q48-6c7w-9gw2; Lá Chắn ĐẠT) và T-055 (nháp nhớ ảnh đã chọn: thư mục số + đường dẫn tương đối, mở lại nháp thì kiểm lại ảnh trên máy, ảnh AI giữ «Minh họa»; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, điều kiện vào T-056, T-076) vào `main`. Nâng công cụ `uv` máy Windows lên 0.13.4 (T-078, GHSA-hq85-5cpj-mr62). Windows 10.441 test qua.
- 2026-10-21: Chỉ Huy B gộp T-077 vào `main`: tên công cụ AI gõ khác dạng chuẩn ("MidJourney", "Mid Journey", "Co-Pilot") là ảnh AI; kho thẻ sửa tay đọc xong mới xử lý. Lá Chắn rút gọn ĐẠT (Opus tạm). Windows 10.585 test qua.
- 2026-10-22: Chỉ Huy B gộp T-065 vào `main`: quy tắc alt cấm chép chữ đọc được trong ảnh (biển hiệu, tên cửa hàng, số điện thoại…) vào cả alt lẫn chú thích; ví dụ trong `config/content.toml` chỉ dùng thông tin bịa. Lá Chắn rút gọn ĐẠT (Opus tạm). Windows 10.602 test qua.
- 2026-10-22: Chỉ Huy B gộp T-076 (thư mục ảnh trả tên theo tên trên ổ, kể cả Google Drive for Desktop; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN) và T-063 (lần đầu chạy test đọc thư mục ảnh trên Linux bằng phiên cloud; tìm ra SL-T063-2: Cao trên Mac/Linux, Thấp trên Windows, sửa ở T-079 trước T-056 theo cách A chủ dự án chọn) vào `main`. Windows 10.739 test qua.
- 2026-10-23: Chỉ Huy B gộp T-039 (liên kết nội bộ: chọn bài đích từ bài đã đăng, AI chỉ gợi ý cụm từ có sẵn, link do code chèn, kiểm link nháp/hỏng; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, điều kiện vào T-040, T-041, GĐ5) và T-069 (README phần ảnh) vào `main`. Windows 11.234 test qua.
- 2026-10-23: Chỉ Huy B gộp T-079 vào `main`: đọc ảnh an toàn khi bị tráo thư mục (Mac/Linux mở từng tầng bằng fd; Windows hỏi lại vị trí thật của file đã mở); vá SL-T063-2 (Cao trên Mac/Linux). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 3 lỗi Thấp sửa ở T-080; sổ rủi ro thêm ca "thư mục dời vào gốc". Điều kiện "vá trước khi chạy Mac/Linux" đã xong; Mac vẫn phải chạy test trên máy Mac thật trước khi dùng. Windows 11.265 test qua (3 hỏng oan vì máy bận).
- 2026-10-23: Chỉ Huy B gộp T-066 (lớp kiểm ảnh gửi AI từ chối mọi hồ sơ màu, chặn khối lặp/dài quá khuôn; Lá Chắn ĐẠT; sổ rủi ro thêm giới hạn "ảnh dựng cố ý") và T-071 (gửi nháp kèm ảnh: báo «bài nháp có thể đã có» khi lỗi đúng lúc tạo nháp, chỉ nhận ảnh website xác nhận vừa tạo, `DraftImage` nhận `ImageTags`; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, LC-T071-1 → T-060, SL-T071-1 → T-081 trước T-056) vào `main`. Windows 11.578 test qua.
- 2026-10-23: Chỉ Huy B gộp T-080 vào `main`: đọc ảnh so đường dẫn thật từng chữ (vá lỗi thư mục "anh em" tên trông y hệt, Soi Lỗi khai thác được thật trên bản cũ; Lá Chắn nâng lên Cao), câu báo khi bị tráo không tả file ngoài thư mục ảnh. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 3 lỗi câu báo Thấp làm ở T-082 sau T-056. Đã thử ổ mạng, Google Drive, USB FAT32 và Linux thật (cloud). Windows 11.668 test qua.
- 2026-10-23: Chỉ Huy B gộp T-081 vào `main`: bỏ dấu «\» sót ở alt, chú thích ảnh AI khi AI viết «[Minh họa]: …»; chặn shortcode giữ nguyên. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; lỗi chữ nhỏ còn lại gom ở T-083 sau T-056. **Mọi phiếu bắt buộc trước màn hình chọn ảnh T-056 đã gộp.** Windows 11.839 test qua.
- 2026-10-24: Chỉ Huy B gộp T-060 vào `main`: client WordPress chặn tham số và header có thể đổi đường gọi (`rest_route`, `_method`, `X-HTTP-Method-Override`…), câu lỗi cố định kèm mã HTTP (không chép lời máy chủ, không chép `WORDPRESS_URL`), `WORDPRESS_URL` không trỏ file thực thi, `upload_media` chỉ ghi vào ảnh vừa tạo và ghi đè đủ alt, tiêu đề, chú thích. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 3 lỗi Thấp chốt chặn cho phiếu sau. Windows 12.667 test qua.
- 2026-10-24: Chỉ Huy B gộp T-040 vào `main`: lời dặn AI cho meta title, description và anchor liên kết nội bộ viết lại có ví dụ (title vừa với đuôi « | Pro-Metal», description có lợi ích và lời mời nhẹ, không giá, không số); mục `[meta]` trong `config/content.toml` (code chưa đọc, nối ở T-041). Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN; LC-T040-1 → T-041. Windows 12.859 test qua.
- 2026-10-26: Chỉ Huy B gộp T-056 vào `main`: trang Soạn bài có **chỗ cần ảnh thật** (chọn ảnh từ thư mục USB/Google Drive, Ảnh thật/AI kèm lý do, GPS, AI viết alt khi bấm, duyệt alt, prompt ảnh AI) và nút **«Gửi nháp»** gửi thật bài nháp kèm ảnh lên WordPress (cảnh báo GPS công khai, liệt kê đoạn dạng shortcode). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 5 lỗi Thấp gửi trùng sửa ở T-086. Chủ dự án đã cập nhật Code Snippets 4.0.0. Windows 12.974 test qua.
- 2026-10-26: Chỉ Huy B gộp T-085 (client WordPress chỉ nhận khóa thân JSON đã duyệt theo từng đường, chặn `_fields` lấy nội dung bài, câu báo «ảnh đã lên thư viện Media»; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, 4 Thấp cho phiếu dọn sau) và T-087 (README «Chọn ảnh cho bài»; Lá Chắn ĐẠT) vào `main`. Windows 13.961 test qua.
- 2026-10-26: Chỉ Huy B gộp T-086 vào `main`: «Gửi nháp» nhớ trạng thái «đang gửi / đã gửi (mã bài)» trong chính file nháp (tải lại trang, đóng tab, mở bài khác vẫn khóa gửi trùng tới khi người dùng xác nhận), khóa đơn điệu, băm ảnh đã duyệt chặn ảnh bị thay. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 3 Thấp ở T-089. Windows 14.032 test qua.
- 2026-10-27: Chỉ Huy B gộp T-088 vào `main`: client WordPress bịt lối NUL trong `_fields`, mọi chỗ đọc JSON trả lời không để lọt `RecursionError` hay lỗi giải mã lạ (câu cố định kèm mã HTTP), lệnh tải ảnh lỗi giữa chừng dặn kiểm Media → Thư viện trước khi tải lại. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 1 Thấp có từ trước SL-T088-1. Windows 14.722 test qua, 0 hỏng.
- 2026-10-27: Chỉ Huy B gộp T-089 (lượt 1–3) vào `main`: «Gửi nháp» ghi «đang gửi» kiểu so rồi đặt trong một giao dịch (hai tab cùng gửi một bài chỉ ra một bài nháp), chỉ lần gửi đã giành được «đang gửi» mới ghi kết quả, mã bài lạ từ website không làm trang lỗi, ảnh xem trước dựng từ đúng byte đã băm, băm ảnh đã duyệt lưu trong nháp (mở lại mà ảnh khác thì bắt duyệt lại; nháp cũ phải tick duyệt lại một lần). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; lượt 4 (LC-T089-1) đang làm. Windows 14.804 test qua, 0 hỏng.
- 2026-10-27: Chỉ Huy B gộp T-041 vào `main`: bước 4 «SEO» của Soạn bài chạy thật (meta title/description AI gợi ý, viết lại từng ô, quay lại bản trước; đếm ký tự, nhãn Nên/Cảnh báo/Chặn; slug; kiểm trùng bài đã đăng; liên kết nội bộ; schema FAQ; lưu SEO vào nháp; chép sang SiteSEO; công tắc ghi SEO lên website mặc định tắt); chữ SEO có ký tự điều khiển hay ký tự lạ bị chặn có câu báo ở mọi đường. Gộp cùng T-089 lượt 4 (lần gửi chưa tạo bài trả nháp về đúng trạng thái cũ) và README sau T-089. Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (T-041), ĐẠT (T-089). Windows 15.263 test qua, 0 hỏng.
- 2026-10-27: Chỉ Huy B gộp T-084 vào `main`: tab Ảnh của trang Cài đặt chỉ hiện tên ngắn thư mục ảnh, báo lối tắt, không in đường dẫn đầy đủ (U2). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN. Thử thật T-059 trên website: ghi SEO qua Abilities bằng tài khoản Biên tập viên, ảnh còn GPS, từ chối bài đã chuyển trạng thái; còn `srcset` làm bản thu nhỏ mất GPS (sửa ở T-059 bước 7). Windows 15.304 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-082 vào `main`: câu báo đọc ảnh khi thư mục bị dời/tráo đúng nghĩa, không nới lớp chặn (ép thắng, tráo thật 0 lọt). Lá Chắn ĐẠT. Gộp tài liệu T-094 (thiết kế Giai đoạn 5, 8 phiếu T-096 → T-103), T-095 (README bước SEO, tài khoản Biên tập viên). Windows 15.352 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-083 (alt, chú thích ảnh AI không lặp hay cụt tiền tố «Minh họa»; Lá Chắn ĐẠT) và T-059 bước 7 (xác nhận ghi SEO theo khuôn thật SiteSEO 1.4.2; ảnh trong bài ghi sẵn `srcset` file đầy đủ để điện thoại nhận ảnh còn GPS; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN) vào `main`. Windows 17.562 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-096 vào `main`: bộ dựng bài cuối Giai đoạn 5 (`seo_app/publish/`: Markdown → HTML an toàn, kiểm link, chặn nhúng, dữ liệu màn hình xác nhận; chưa nối vào app). Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; LC-T096-5 (Thấp) sửa ở lượt 4 ngắn trước T-102. Windows 17.950 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-090 (câu báo emoji mới trong chữ SEO, `.env` sai bảng mã, `set_password` báo câu tiếng Việt; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, 2 Thấp có từ trước → T-104) và T-097 (client Google Sheets `seo_app/google/`, kiểm file khóa tài khoản dịch vụ, khai báo `google-auth`; Lá Chắn đầy đủ ĐẠT CÓ ĐIỀU KIỆN, 5 Thấp → lượt 2) vào `main`. Windows 18.870 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-098 (kế hoạch Giai đoạn 5 `seo_app/plan/`: khuôn, đọc CSV/TSV/Markdown/chữ dán, đề xuất có AI; Soi Lỗi 3 lượt, Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 3 Thấp → lượt 4) và T-096 lượt 4 (LC-T096-5 đóng; LC-T096-6 → lượt 5 trước T-102) vào `main`. Windows 19.496 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-097 lượt 2 (client Google Sheets không đọc thân câu trả lời chuyển hướng, lỗi lạ, đường dẫn `\\?\`; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; SL-T097-5 → T-100) và T-098 lượt 4 (Soi Lỗi ĐẠT, cả 20 lỗi đã đóng) vào `main`. Windows 19.645 test qua, 0 hỏng.
- 2026-10-28: Chỉ Huy B gộp T-091 (client WordPress: lọc surrogate lẻ sau giải mã ở `_json`, trần mã 2⁶³−1 coi như sai khuôn, so xác nhận SiteSEO theo `sanitize_text_field`, `ConnectionInfo.can_unfiltered_html`; Soi Lỗi 2 lượt, Lá Chắn ĐẠT CÓ ĐIỀU KIỆN) và T-096 lượt 5 (LC-T096-6 đóng, bộ dựng bài cuối xong hẳn) vào `main`. Windows 19.888 test qua, 0 hỏng.
- 2026-10-30: Chỉ Huy B gộp T-103 (lời dặn AI đọc kế hoạch, `[tasks.plan]`, `[plan]`; Soi Lỗi 2 lượt ĐẠT, Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, LC-T103-1 → T-100) và T-104 (`set_password` ghi `.env` an toàn qua `seo_app/env_file.py`: thay đúng mọi dòng mã băm như python-dotenv, ghi nguyên tử; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN, 2 Thấp → T-105) vào `main`. Windows 20.051 test qua, 0 hỏng.
- 2026-10-30: Chỉ Huy B gộp T-099 (client WordPress hẹn giờ, đăng ngay: `release_draft` là đường duy nhất tới `future`/`publish`, chỉ nháp client vừa tạo; Lá Chắn đầy đủ ĐẠT CÓ ĐIỀU KIỆN, lượt 2 trước T-102), T-100 lượt 2 (đồng bộ kế hoạch với Google Sheets, cache, nối nháp, khuôn nháp 3; Lá Chắn ĐẠT CÓ ĐIỀU KIỆN), T-106 + T-108 (trang Kết nối WordPress bỏ ô tải nguyên ảnh ở mục tạo thử, cảnh báo thiếu quyền `unfiltered_html`) và biên bản T-093 (Lá Chắn rà soát Giai đoạn 3: chưa đóng, còn T-107 và quyết định của chủ dự án) vào `main`. Windows 20.877 test qua, 0 hỏng.
- 2026-10-30: Chỉ Huy B gộp T-100 lượt 3–4 (so đúng Sheet khi ghi trạng thái, Sheet đầy không cấp mã mới, dò giá trong chữ AI so theo chữ có dấu; Soi Lỗi ĐẠT, Lá Chắn ĐẠT; T-100 xong hẳn) vào `main`. Windows 21.063 test qua, 0 hỏng.

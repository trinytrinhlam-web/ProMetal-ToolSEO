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
- AI: một lớp provider chung, hỗ trợ Anthropic, OpenAI, Google Gemini. Mô hình cho từng việc (nghiên cứu, viết, rà soát, meta, alt ảnh, tạo ảnh) khai báo trong file cấu hình, đổi được mà không sửa code.
- Google: dùng service account (file JSON nằm ngoài repo, đường dẫn khai báo trong `.env`).
- Có màn hình đăng nhập bằng mật khẩu; `.env` chỉ lưu mã băm của mật khẩu, kèm script để người dùng tạo mã băm.

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
- [ ] Giai đoạn 1 — WordPress: kiểm tra kết nối, lấy chuyên mục/thẻ, tạo bài nháp, tải ảnh lên thư viện, đặt ảnh đại diện.
- [ ] Giai đoạn 2 — AI viết bài: lớp provider, quy trình nội dung ở trên, màn hình thử mù (cùng một đề, nhiều mô hình, ẩn tên mô hình).
- [ ] Giai đoạn 3 — Ảnh: chọn ảnh từ thư mục đã khai báo (USB / Drive), nén WebP, đổi tên chuẩn SEO, xóa vị trí GPS trong EXIF, viết alt bằng AI; tạo ảnh bằng AI.
- [ ] Giai đoạn 4 — Tối ưu on-page: meta, schema JSON-LD, liên kết nội bộ dựa trên danh sách bài trên WordPress.
- [ ] Giai đoạn 5 — Kế hoạch & lịch: đồng bộ Google Sheets, hẹn giờ đăng.
- [ ] Giai đoạn 6 — Theo dõi: Search Console (từ khóa, vị trí, lượt click) theo từng bài.

## Câu hỏi còn mở (hỏi người dùng khi tới giai đoạn liên quan)

- Website dùng plugin SEO nào (Rank Math, Yoast, khác)? Quyết định cách ghi meta/schema.
- Tên miền website; có site thử nghiệm (staging) hay không.

## Cách làm việc

- Mỗi phiên làm một giai đoạn hoặc một phần nhỏ của giai đoạn, kết thúc bằng một PR riêng.
- Trước khi sửa code: trình bày kế hoạch ngắn bằng tiếng Việt.
- Viết test cho phần logic; chạy `uv run pytest` và `uv run ruff check .` trước khi báo xong.
- Không thêm thư viện khi chưa cần; khi thêm, giải thích ngắn lý do.
- Xong một giai đoạn: đánh dấu [x] trong Lộ trình, ghi một dòng vào mục Trạng thái, cập nhật README nếu cách dùng thay đổi.

### Làm việc trên 2 máy (máy công ty và máy nhà), đồng bộ qua GitHub

Người dùng chạy Claude Code ngay trên máy của mình để vừa làm vừa xem app chạy thật. Claude tự chạy các lệnh git, người dùng không cần gõ lệnh.

- Đầu buổi: chạy `git status` và `git pull` để lấy code mới nhất từ máy kia trước khi sửa. Nếu còn thay đổi chưa commit thì hỏi người dùng trước.
- Trong buổi: sau mỗi thay đổi xem được trên giao diện, nhắc người dùng mở app (`run.bat` / `run.command`, hoặc Claude chạy `uv run streamlit run app/main.py`) để tự kiểm tra.
- Cuối buổi (hoặc khi người dùng nói sắp nghỉ): tóm tắt việc đã làm, chạy `uv run pytest` và `uv run ruff check .`, rồi **đề nghị** commit và push lên GitHub. Chỉ commit/push khi người dùng đồng ý.
- Mỗi giai đoạn làm trên một nhánh riêng, xong thì mở PR. Ghi tên nhánh đang làm vào mục Trạng thái để máy kia biết chuyển sang đúng nhánh.

## Trạng thái

- 2026-10-06: Khởi tạo dự án. Chưa có code.
- 2026-10-06: Xong Giai đoạn 0 — bộ khung uv + Streamlit, đăng nhập bằng mã băm PBKDF2 (`seo_app/auth.py`), cấu hình từ `.env` (`seo_app/config.py`), `run`/`set_password` (.bat/.command), SessionStart hook, pytest + ruff, README.

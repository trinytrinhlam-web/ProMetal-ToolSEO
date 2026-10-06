# SEO App

Phần mềm chạy ngay trên máy tính (Windows và Mac) để triển khai kế hoạch SEO cho website WordPress: nghiên cứu, viết bài bằng AI, xử lý ảnh, tối ưu meta/schema, gắn liên kết nội bộ, đăng bài và theo dõi thứ hạng.

App mở trong trình duyệt tại địa chỉ `http://localhost:8501`. Địa chỉ này chỉ dùng được trên chính máy bạn, người khác không truy cập được.

> **Trạng thái:** đã có bộ khung (đăng nhập, đọc cấu hình). Các chức năng sẽ được thêm dần theo lộ trình trong `CLAUDE.md`.

---

## 1. Tải phần mềm về máy

Nên dùng **GitHub Desktop** (https://desktop.github.com) để sau này cập nhật chỉ cần bấm một nút:

1. Cài GitHub Desktop và đăng nhập tài khoản GitHub.
2. Chọn **File → Clone repository**, chọn `ProMetal-ToolSEO`, chọn thư mục lưu → **Clone**.

Cách khác: trên trang GitHub của dự án, bấm **Code → Download ZIP**, rồi giải nén.

## 2. Chạy lần đầu trên Windows

1. Mở thư mục dự án, **bấm đúp `run.bat`**.
   - Nếu Windows hiện "Windows protected your PC", bấm **More info → Run anyway**.
2. Lần đầu, cửa sổ đen sẽ tự cài `uv` (công cụ quản lý Python), Python và các thư viện. Có thể mất vài phút, cần có mạng.
3. Trình duyệt tự mở app. Lúc này app sẽ báo **"Chưa đặt mật khẩu"**, đây là bình thường.
4. Đóng cửa sổ đen (app sẽ tắt), rồi **bấm đúp `set_password.bat`** và nhập mật khẩu hai lần. Khi gõ mật khẩu, chữ sẽ không hiện ra.
5. Bấm đúp `run.bat` lần nữa và đăng nhập.

## 3. Chạy lần đầu trên Mac

1. Mở thư mục dự án, **bấm đúp `run.command`**.
   - Nếu Mac báo "không thể mở vì không xác định được nhà phát triển": **chuột phải (hoặc Control + bấm) vào file → Open → Open**. Chỉ cần làm một lần.
   - Nếu Mac báo không có quyền chạy file: mở ứng dụng **Terminal**, gõ `chmod +x ` (có dấu cách ở cuối), kéo file `run.command` vào cửa sổ Terminal, nhấn Enter. Làm tương tự với `set_password.command`.
2. Lần đầu, cửa sổ Terminal sẽ tự cài `uv`, Python và thư viện. Có thể mất vài phút.
3. Trình duyệt mở app và báo **"Chưa đặt mật khẩu"**.
4. Tắt app (nhấn `Control + C` trong Terminal hoặc đóng cửa sổ), rồi **bấm đúp `set_password.command`** và nhập mật khẩu.
5. Bấm đúp `run.command` lần nữa và đăng nhập.

## 4. Dùng hằng ngày

- **Mở app:** bấm đúp `run.bat` (Windows) hoặc `run.command` (Mac).
- **Tắt app:** đóng cửa sổ đen / Terminal. Đóng tab trình duyệt thì app chưa tắt.
- **Đổi mật khẩu hoặc quên mật khẩu:** chạy lại `set_password.bat` / `set_password.command`.
- Tải lại trang (F5) thì phải đăng nhập lại. Đây là chủ ý để bảo mật.

## 5. File cấu hình `.env`

Khóa API, mật khẩu WordPress, đường dẫn thư mục ảnh… đều nằm trong file **`.env`** ở thư mục dự án. File này được tạo tự động khi bạn đặt mật khẩu, dựa trên file mẫu `.env.example`. Mỗi dòng trong file mẫu đều có chú thích tiếng Việt.

- **Mở file:** dùng Notepad (Windows) hoặc TextEdit (Mac). Trên Mac, file bắt đầu bằng dấu chấm bị ẩn; trong Finder nhấn `Command + Shift + .` để hiện.
- **Chỉ điền mục cần dùng.** Trang chủ của app cho biết mục nào đã khai báo, mục nào chưa (không hiện giá trị).
- Sửa `.env` xong thì tắt app rồi mở lại.
- **Bảo mật:**
  - Không gửi `.env` qua email hay chat, không đưa lên GitHub (dự án đã chặn sẵn).
  - File JSON service account của Google nên để ngoài thư mục dự án.
- **Dùng trên hai máy:**
  - Mỗi máy cần một file `.env` riêng. Có thể chép bằng USB.
  - Bài viết, kế hoạch và thứ hạng nằm trên WordPress / Google, nên hai máy luôn thấy cùng dữ liệu.

## 6. Cập nhật phiên bản mới

- Với GitHub Desktop: mở dự án, bấm **Fetch origin**, rồi bấm **Pull origin** nếu có.
- Sau đó chạy `run.bat` / `run.command` như bình thường. Thư viện mới (nếu có) sẽ được cài tự động.
- File `.env` của bạn không bị ghi đè.

## 7. Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| "Không cài được uv" | Kiểm tra mạng rồi chạy lại. Nếu vẫn lỗi, cài uv thủ công theo hướng dẫn ở https://docs.astral.sh/uv/getting-started/installation/ |
| "Cài thư viện bị lỗi" | Chụp màn hình cửa sổ và gửi người hỗ trợ. |
| Trình duyệt không tự mở | Tự mở trình duyệt và vào địa chỉ in trong cửa sổ đen (thường là `http://localhost:8501`). |
| Lỡ mở app hai lần | Lần thứ hai sẽ dùng cổng khác (8502…). Nên đóng bớt một cửa sổ. |
| App báo "Múi giờ APP_TIMEZONE không hợp lệ" | Sửa dòng `APP_TIMEZONE` trong `.env` thành `Asia/Ho_Chi_Minh`. |

---

## Dành cho người phát triển

Cần có [uv](https://docs.astral.sh/uv/).

```bash
uv sync                            # cài thư viện
uv run pytest                      # kiểm thử (không gọi API thật)
uv run ruff check .                # kiểm tra code
uv run ruff format .               # định dạng code
uv run streamlit run app/main.py   # chạy app
uv run python scripts/hash_password.py --print   # tạo mã băm mật khẩu, chỉ in ra
```

Cấu trúc thư mục:

```
app/          giao diện Streamlit (main.py)
seo_app/      phần logic: config.py (đọc .env), auth.py (mật khẩu)
scripts/      script tiện ích (hash_password.py)
tests/        kiểm thử pytest
.streamlit/   cấu hình Streamlit (chỉ mở ở localhost, không thu thập số liệu)
.claude/      hook cài thư viện cho phiên Claude Code trên cloud
```

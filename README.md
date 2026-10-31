# SEO App

Phần mềm chạy ngay trên máy tính (Windows và Mac) để triển khai kế hoạch SEO cho website WordPress: nghiên cứu, viết bài bằng AI, xử lý ảnh, tối ưu meta/schema, gắn liên kết nội bộ, đăng bài và theo dõi thứ hạng.

App mở trong trình duyệt tại địa chỉ `http://localhost:8501`. Địa chỉ này chỉ dùng được trên chính máy bạn, người khác không truy cập được.

> **Trạng thái:** đã có đăng nhập, kết nối WordPress (kiểm tra kết nối, xem chuyên mục/thẻ, tạo bài nháp có ảnh đại diện), viết bài bằng AI (Claude, ChatGPT, Gemini; có thử mù để chọn mô hình, xem mục 7), chọn ảnh thật từ thư mục cho bài (mục 9), bước SEO: tiêu đề, mô tả cho Google, đường dẫn, liên kết nội bộ, schema hỏi đáp (mục 10) và gửi bài nháp kèm ảnh lên website, có thể ghi luôn tiêu đề, mô tả SEO vào SiteSEO (mục 11). Các chức năng khác sẽ được thêm dần theo lộ trình trong `CLAUDE.md`.

---

## 1. Tải phần mềm về máy

Nên dùng **GitHub Desktop** (https://desktop.github.com) để sau này cập nhật chỉ cần bấm một nút:

1. Cài GitHub Desktop và đăng nhập tài khoản GitHub.
2. Chọn **File → Clone repository**, chọn `ProMetal-ToolSEO`, chọn thư mục lưu (không nằm trong Google Drive hay OneDrive, xem mục 8) → **Clone**.

Cách khác: trên trang GitHub của dự án, bấm **Code → Download ZIP**, rồi giải nén.

## 2. Chạy lần đầu trên Windows

1. Mở thư mục dự án, **bấm đúp `run.bat`**.
   - Nếu Windows hiện "Windows protected your PC", bấm **More info → Run anyway**.
2. Lần đầu, cửa sổ đen sẽ tự cài `uv` (công cụ quản lý Python), Python và các thư viện. Có thể mất vài phút, cần có mạng.
3. Trình duyệt tự mở app. Lúc này app sẽ báo **"Chưa đặt mật khẩu"**, đây là bình thường.
4. Đóng cửa sổ đen (app sẽ tắt), rồi **bấm đúp `set_password.bat`** và nhập mật khẩu hai lần. Khi gõ mật khẩu, chữ sẽ không hiện ra.
5. Bấm đúp `run.bat` lần nữa và đăng nhập.

**Công cụ `uv` phải từ bản 0.13.4 trở lên.** Bản cũ hơn còn tin một chứng chỉ bảo mật đã bị lộ (lỗi GHSA-hq85-5cpj-mr62), nên kẻ xấu có thể giả kho thư viện Python để cài mã độc vào máy. Với `uv` cũ, app không mở: cửa sổ đen báo `Required uv version …` (xem mục 13). `run.bat` chỉ cài `uv` khi máy chưa có, **không tự nâng** bản đã có. Máy đã cài `uv` từ trước thì kiểm và nâng như sau:

1. Bấm phím Windows, gõ `cmd`, nhấn Enter: cửa sổ **Command Prompt** (nền đen) mở ra. Không cần mở thư mục dự án.
2. Gõ `uv --version` rồi nhấn Enter. So từng số: `uv 0.13.4`, `0.13.5`, `0.14.0`… là đủ mới, không cần làm gì thêm; `uv 0.12.23` hay `0.13.3` là cũ.
3. Bản cũ: gõ `uv self update` rồi nhấn Enter, đợi xong (cần mạng). **Làm bước này ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng**: `uv` cũ tải bản mới qua đúng kênh chứng chỉ bị lộ. Gõ lại `uv --version` để chắc đã từ 0.13.4 trở lên.
4. Đóng cửa sổ, bấm đúp `run.bat` như thường.

- Cửa sổ báo không tìm thấy lệnh `uv` (`'uv' is not recognized…` hay câu tương tự): ở bước 2, 3 gõ `%USERPROFILE%\.local\bin\uv.exe` thay cho `uv` (đó là chỗ `run.bat` cài `uv`).
- `uv self update` báo không tự nâng được (thường do `uv` được cài bằng `pip`, không phải bằng `run.bat`): gõ `pip install --upgrade uv`, hoặc cài lại `uv` theo hướng dẫn ở https://docs.astral.sh/uv/getting-started/installation/. Cũng làm ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng.

## 3. Chạy lần đầu trên Mac

1. Mở thư mục dự án, **bấm đúp `run.command`**.
   - Nếu Mac báo "không thể mở vì không xác định được nhà phát triển": **chuột phải (hoặc Control + bấm) vào file → Open → Open**. Chỉ cần làm một lần.
   - Nếu Mac báo không có quyền chạy file: mở ứng dụng **Terminal**, gõ `chmod +x ` (có dấu cách ở cuối), kéo file `run.command` vào cửa sổ Terminal, nhấn Enter. Làm tương tự với `set_password.command`.
2. Lần đầu, cửa sổ Terminal sẽ tự cài `uv`, Python và thư viện. Có thể mất vài phút.
3. Trình duyệt mở app và báo **"Chưa đặt mật khẩu"**.
4. Tắt app (nhấn `Control + C` trong Terminal hoặc đóng cửa sổ), rồi **bấm đúp `set_password.command`** và nhập mật khẩu.
5. Bấm đúp `run.command` lần nữa và đăng nhập.

**Công cụ `uv` phải từ bản 0.13.4 trở lên** (lý do ở cuối mục 2). Với `uv` cũ, app không mở: cửa sổ Terminal báo `Required uv version …` (xem mục 13). `run.command` chỉ cài `uv` khi máy chưa có, **không tự nâng** bản đã có. Máy đã cài `uv` từ trước thì kiểm và nâng như sau:

1. Nhấn `Command + Space`, gõ `Terminal`, nhấn Enter. Không cần mở thư mục dự án.
2. Gõ `uv --version` rồi nhấn Enter. So từng số: `uv 0.13.4`, `0.13.5`, `0.14.0`… là đủ mới; `uv 0.12.23` hay `0.13.3` là cũ.
3. Bản cũ: gõ `uv self update` rồi nhấn Enter, đợi xong (cần mạng). **Làm bước này ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng**: `uv` cũ tải bản mới qua đúng kênh chứng chỉ bị lộ. Gõ lại `uv --version` để chắc đã từ 0.13.4 trở lên.
4. Đóng Terminal, bấm đúp `run.command` như thường.

- Terminal báo không tìm thấy lệnh `uv` (`command not found: uv`): ở bước 2, 3 gõ `~/.local/bin/uv` thay cho `uv` (đó là chỗ `run.command` cài `uv`).
- `uv self update` báo không tự nâng được (thường do `uv` được cài bằng `pip`): gõ `pip3 install --upgrade uv`, hoặc cài lại `uv` theo hướng dẫn ở https://docs.astral.sh/uv/getting-started/installation/. Cũng làm ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng.

## 4. Dùng hằng ngày

- **Mở app:** bấm đúp `run.bat` (Windows) hoặc `run.command` (Mac).
- **Tắt app:** đóng cửa sổ đen / Terminal. Đóng tab trình duyệt thì app chưa tắt.
- **Đổi mật khẩu hoặc quên mật khẩu:** chạy lại `set_password.bat` / `set_password.command`.
- Tải lại trang (F5) thì phải đăng nhập lại. Đây là chủ ý để bảo mật. Nút **Đăng xuất** nằm ở trang Cài đặt.
- **Menu trên cùng**: **Bài viết** (các bài đang viết), **Soạn bài** (viết một bài qua 5 bước), **Kế hoạch** (đưa kế hoạch của bạn vào), **Cài đặt**, **Kết nối WordPress**.
- Chỗ nào có nhãn cam **"Bản demo"** là đang dùng dữ liệu mẫu để bạn xem trước: bấm thử thoải mái, không gửi gì đi đâu. Chức năng sẽ chạy thật khi tới giai đoạn tương ứng. Ba bước đầu của **Soạn bài** đã dùng AI thật (xem mục 7); chọn ảnh, bước SEO và gửi bài nháp cũng đã chạy thật (mục 9, 10, 11).

## 5. File cấu hình `.env`

Khóa API, mật khẩu WordPress, đường dẫn thư mục ảnh… đều nằm trong file **`.env`** ở thư mục dự án. File này được tạo tự động khi bạn đặt mật khẩu, dựa trên file mẫu `.env.example`. Mỗi dòng trong file mẫu đều có chú thích tiếng Việt.

- **Mở file:** dùng Notepad (Windows) hoặc TextEdit (Mac). Trên Mac, file bắt đầu bằng dấu chấm bị ẩn; trong Finder nhấn `Command + Shift + .` để hiện.
- **Khóa API AI (Claude, ChatGPT, Gemini)** nhập ngay trong app: **Cài đặt → 🔌 Kết nối**, dán khóa, bấm **Lưu** rồi **Kiểm tra**. App ghi vào `.env` và không bao giờ hiện lại khóa (xem mục 7.1).
- **Chỉ điền mục cần dùng.** Trang chủ của app cho biết mục nào đã khai báo, mục nào chưa (không hiện giá trị).
- Sửa `.env` xong thì tắt app rồi mở lại.
- **Bảo mật:**
  - Không gửi `.env` qua email hay chat, không đưa lên GitHub (dự án đã chặn sẵn).
  - File JSON service account của Google nên để ngoài thư mục dự án.
- **Dùng trên hai máy:**
  - Mỗi máy cần một file `.env` riêng. Có thể chép bằng USB.
  - Bài viết, kế hoạch và thứ hạng nằm trên WordPress / Google, nên hai máy luôn thấy cùng dữ liệu.

## 6. Kết nối WordPress

App gửi bài sang WordPress bằng **Application Password** (mật khẩu ứng dụng): một mật khẩu riêng cho app, khác mật khẩu đăng nhập thường. Bạn có thể thu hồi nó bất cứ lúc nào mà không ảnh hưởng tài khoản.

**Tạo tài khoản riêng cho app, vai Biên tập viên**

Đừng dùng tài khoản quản trị cho app. Tài khoản **Biên tập viên** (Editor) viết được bài, tải được ảnh, nhưng không cài được plugin, không đổi được cài đặt website: lỡ lộ mật khẩu ứng dụng thì thiệt hại nhỏ hơn nhiều.

1. Đăng nhập trang quản trị WordPress (`https://ten-mien-cua-ban/wp-admin`) bằng tài khoản quản trị.
2. Vào **Người dùng → Thêm mới** (Users → Add New User):
   - **Tên người dùng**: đây chính là **tên đăng nhập** của tài khoản, ví dụ `bien-tap-seo`. Ghi lại tên này.
   - Email: phải là email chưa dùng cho tài khoản nào khác trên website.
   - Mật khẩu: đặt mật khẩu mạnh (app không dùng mật khẩu này).
   - **Vai trò**: chọn **Biên tập viên** (Editor).

   Bấm nút thêm người dùng ở cuối trang.

**Tạo mật khẩu ứng dụng trên chính tài khoản đó**

3. Đăng xuất, rồi đăng nhập lại bằng tài khoản Biên tập viên vừa tạo. Mật khẩu ứng dụng phải tạo **trên tài khoản Biên tập viên**, không phải trên tài khoản quản trị.
4. Vào **Hồ sơ** (Profile) ở menu bên trái, kéo xuống mục **Application Passwords** (Mật khẩu ứng dụng).
5. Gõ một **tên cho mật khẩu**, ví dụ `SEO App - may cong ty`, rồi bấm **Thêm Application Password mới**. Tên này chỉ để sau này bạn nhận ra mật khẩu dùng ở đâu, **không phải** tên đăng nhập.
6. WordPress hiện một dãy dạng `abcd efgh ijkl mnop qrst uvwx`. **Chép ngay**: dãy này chỉ hiện một lần.

**Khai vào app**

7. Mở file `.env`, điền:
   ```
   WORDPRESS_URL=https://ten-mien-cua-ban
   WORDPRESS_USERNAME=ten-dang-nhap-cua-tai-khoan-bien-tap-vien
   WORDPRESS_APP_PASSWORD=abcd efgh ijkl mnop qrst uvwx
   ```
   - `WORDPRESS_USERNAME` là **tên đăng nhập** của tài khoản Biên tập viên (ở bước 2, ví dụ `bien-tap-seo`), **không phải** tên bạn đặt cho mật khẩu ứng dụng ở bước 5 (ví dụ `SEO App - may cong ty`). Nhầm hai tên này thì app báo «WordPress từ chối đăng nhập (mã 401)…».
   - Quên tên đăng nhập: đăng nhập bằng tài khoản quản trị, vào **Người dùng → Tất cả người dùng** (Users → All Users), xem cột **Tên người dùng** (Username).

**Bật cho app ghi SEO vào SiteSEO**

Phần này cần cho công tắc **Ghi SEO lên website** (mục 10). Không làm thì app vẫn tạo bài nháp bình thường, bạn chép tay tiêu đề, mô tả vào hộp SiteSEO.

8. Đăng nhập bằng tài khoản quản trị, vào **Plugin → Plugin đã cài** (Plugins → Installed Plugins), xem phiên bản của **SiteSEO**: phải từ **1.4.0** trở lên. Cũ hơn thì cập nhật SiteSEO trước (bản cũ không có mục ở bước 9).
9. Trong menu **SiteSEO** bên trái, mở mục **AI Abilities** và bật công tắc ở đó.

**Kiểm tra**

10. Tắt app rồi mở lại. Vào menu **Kết nối WordPress** và bấm **Kiểm tra kết nối**. Đúng thì thấy:
    - «Kết nối thành công tới …»;
    - «Tài khoản: … — vai trò: editor». `editor` là Biên tập viên. Thấy `administrator` là app đang dùng nhầm tài khoản quản trị: làm lại bước 3–7;
    - «Viết bài: ✅», «Tải ảnh lên: ✅»;
    - «SiteSEO: ghi được». Thấy «SiteSEO: chưa bật (…)» thì làm lại bước 8–9 rồi bấm kiểm tra lần nữa; thấy «SiteSEO: chưa dò được (…)» thì đợi một lúc rồi bấm lại.

Ở trang này bạn còn có thể:
- bấm **Tải chuyên mục và thẻ** để xem danh sách đang có trên website;
- **tạo thử một bài nháp** chỉ có chữ, không có ảnh, để kiểm kết nối. Muốn thử gửi ảnh thì dùng «Gửi nháp» ở trang **Soạn bài**: ảnh ở đó đã qua bước làm sạch (bỏ số seri máy, tên chủ máy…) trước khi lên website.

App **chỉ tạo bài nháp**: khách không thấy bài cho tới khi bạn tự bấm Đăng trong WordPress. Bài thử có thể xóa trong WordPress sau khi kiểm tra.

**Lưu ý trên website**

- **Không dùng trình sửa `.htaccess` của SiteSEO Pro.** Khi lưu, trình sửa này xóa mất các dòng có dạng `<…>` (ví dụ `<IfModule …>`) trong file `.htaccess`, làm lệch cấu hình website (đã gặp khi thử thật). Cần sửa `.htaccess` thì nhờ người làm web sửa qua cPanel của hosting, và sao lưu file trước khi sửa.
- **Gỡ mật khẩu ứng dụng không còn dùng**, nhất là trên tài khoản quản trị. Mật khẩu ứng dụng có đủ quyền của tài khoản chứa nó: mật khẩu trên tài khoản quản trị mà lộ thì người khác làm được mọi việc trên website. Đăng nhập tài khoản đó, vào **Người dùng → Hồ sơ**, mục **Application Passwords**, bấm **Thu hồi** (Revoke) ở dòng không dùng nữa. Thu hồi nhầm mật khẩu app đang dùng thì app báo «từ chối đăng nhập»: tạo mật khẩu mới (bước 3–7).

**Lỗi thường gặp**

| App báo | Cách xử lý |
|---|---|
| "WordPress từ chối đăng nhập (mã 401)…" | **Kiểm tên đăng nhập trước.** `WORDPRESS_USERNAME` trong `.env` phải là tên đăng nhập của tài khoản Biên tập viên, không phải tên đặt cho mật khẩu ứng dụng (bước 7). Sai tên đăng nhập, sai mật khẩu hay website chặn, app đều báo cùng câu này, nên lỗi trông giống lỗi hosting mà thường chỉ do nhầm tên (đã gặp khi thử thật). Rồi kiểm `WORDPRESS_APP_PASSWORD` là mật khẩu ứng dụng tạo **trên chính tài khoản đó** (không phải mật khẩu đăng nhập thường, không phải mật khẩu ứng dụng của tài khoản khác). Sửa `.env` xong thì tắt app rồi mở lại. Đã đúng cả hai mà vẫn lỗi: có thể plugin bảo mật (Wordfence, iThemes…) đang tắt Application Passwords, hoặc hosting chặn header `Authorization`; nhờ người quản lý website kiểm tra. |
| "Không tìm thấy REST API" | Kiểm tra `WORDPRESS_URL`. Trong WordPress vào **Cài đặt → Đường dẫn tĩnh** (Settings → Permalinks), bấm **Lưu thay đổi** một lần. |
| "không đủ quyền" | Tài khoản của app cần vai trò Biên tập viên (bước 2). Bấm **Kiểm tra kết nối** để xem dòng «vai trò: …». |
| "Lỗi chứng chỉ bảo mật (SSL)" | Website chưa có https hợp lệ. Kiểm tra bằng cách mở website trên trình duyệt. |

## 7. Viết bài bằng AI

Trang **Soạn bài** dùng AI thật cho 3 bước đầu: **Chuẩn bị** (nghiên cứu từ khóa và các bài đứng đầu Google), **Dàn ý**, **Viết & kiểm tra**. Ở bước **Viết & kiểm tra** bạn chọn ảnh cho bài (mục 9); bước **SEO** có AI gợi ý tiêu đề, mô tả cho Google và liên kết nội bộ (mục 10); bước **Xuất bản** gửi được bài nháp kèm ảnh lên website (mục 11). Hai cách **Hẹn giờ**, **Đăng ngay** vẫn là bản demo.

App dùng được 3 hãng AI: **Claude** (Anthropic), **ChatGPT** (OpenAI) và **Gemini** (Google). **Không có hãng mặc định**: bạn có khóa của hãng nào thì dùng hãng đó, và đổi hãng cho từng việc khi cần (xem "Đổi hãng hoặc mô hình" bên dưới). Việc nào trong `config/ai.toml` đang ghi hãng nào thì hãng đó phải có khóa.

### 7.1. Lấy khóa API và nhập vào app

Khóa API là một dãy chữ-số riêng của bạn, để app gọi AI thay bạn. Chỉ cần khóa của hãng bạn định dùng.

| Hãng | Lấy khóa ở | Có cần nạp tiền không |
|---|---|---|
| Claude (Anthropic) | https://console.anthropic.com → mục **API Keys** | Cần: nạp tiền (credit) vào tài khoản API. Khác với gói Claude chat. |
| ChatGPT (OpenAI) | https://platform.openai.com/api-keys | Cần: thêm thẻ hoặc nạp tiền trả trước ở trang quản lý thanh toán (Billing). Khác với gói ChatGPT Plus. |
| Gemini (Google) | https://aistudio.google.com/apikey | Thường có bậc miễn phí với hạn mức thấp; muốn dùng nhiều thì bật thanh toán. Hết hạn mức thì app báo (xem bảng lỗi). |

App tính tiền theo lượng chữ AI đọc và viết, giá do từng hãng quy định và có thể đổi. Xem giá mới nhất trên trang giá của hãng, đừng dựa vào con số cũ.

Nhập khóa ngay trong app, không cần mở file:

1. Vào **Cài đặt → 🔌 Kết nối**, ở mục **🔑 Khóa API cho AI** chọn thẻ của hãng.
2. Dán khóa vào ô, bấm **Lưu**. App ghi vào file `.env` trên máy này và không bao giờ hiện lại khóa.
3. Bấm **Kiểm tra**: app hỏi thử máy chủ của hãng xem khóa dùng được không (không tốn tiền). Báo xanh "Khóa … dùng được." là xong. Muốn gỡ khóa thì bấm **Xóa**.

Khóa nằm trong `.env` của từng máy, nên máy thứ hai cần nhập lại một lần.

### 7.2. Đổi hãng hoặc mô hình cho từng việc

Mỗi việc (nghiên cứu, dàn ý, viết bài, viết lại một phần, kiểm tra văn phong, gợi ý tiêu đề và mô tả SEO, gợi ý liên kết nội bộ) dùng một mô hình riêng, khai báo trong `config/ai.toml`. Mở bằng Notepad / TextEdit, sửa hai dòng `provider` và `model` của việc cần đổi, lưu file rồi tải lại trang (F5, sẽ phải đăng nhập lại). Không cần sửa code.

Ví dụ đổi việc viết bài sang ChatGPT:

```toml
[tasks.write]
provider = "openai"        # "anthropic" (Claude), "openai" (ChatGPT) hoặc "gemini"
model = "gpt-5.1"          # tên mô hình đúng theo tài liệu của hãng đó
effort = "high"
max_tokens = 32000
```

- Tên mô hình do hãng đặt và đổi theo thời gian. Xem danh sách mới nhất trong tài liệu của hãng, gõ sai thì app báo "Không có mô hình …".
- `effort` là mức "suy nghĩ" của AI (`low`, `medium`, `high`, `xhigh`, `max`): càng cao càng kỹ nhưng chậm và tốn tiền hơn. Claude và ChatGPT dùng đúng mức bạn ghi. Gemini chỉ có 3 mức (`low`, `medium`, `high`): `xhigh` và `max` được tính là `high`. Mô hình không có chế độ suy nghĩ thì app tự bỏ qua `effort`.
- Việc đang dùng hãng nào thì hãng đó phải có khóa. Thiếu khóa thì ngay khi mở **Soạn bài**, app báo màu vàng và khóa tạm các bước dùng AI.

**Việc viết alt cho ảnh (`[tasks.alt]`) gửi ảnh công trình cho hãng AI.** Alt là dòng chữ mô tả ảnh cho Google và người khiếm thị. Để viết alt, app gửi ảnh công trình cho hãng ghi ở `[tasks.alt]` (đang ghi Claude Sonnet). Ảnh gửi đi là bản sao đã bỏ GPS, EXIF, không kèm tên file hay đường dẫn; chữ gửi kèm chỉ gồm quy tắc viết alt (mục `[alt]` trong `config/content.toml`), từ khóa của bài và hạng mục, khu vực, trước/sau đọc từ tên thư mục (mục 8). Nhưng hãng AI vẫn thấy mọi thứ **trong** ảnh: nhà khách, số nhà, người trong ảnh. App chỉ gửi ảnh cho hãng AI khi bạn bấm **✨ AI viết alt** (hay **🔄 AI viết lại alt**) ở một ảnh đã chọn (mục 9), mỗi lần một ảnh. Vì vậy:

- Nên dùng Claude (đang ghi sẵn) hoặc khóa **trả phí** của OpenAI / Gemini.
- Khóa Gemini **miễn phí**: Google được dùng ảnh gửi lên để cải tiến sản phẩm, và người duyệt của Google có thể xem ảnh. Muốn dùng khóa miễn phí cho việc viết alt thì báo Chỉ Huy để ghi vào sổ rủi ro trước.

### 7.3. Thử mù: chọn mô hình viết hay nhất

Không biết nên dùng hãng nào? Cho 2–3 mô hình viết cùng một đề, chấm điểm không biết tên, rồi mới xem bài nào của ai.

1. Vào **Cài đặt → 🤖 Mô hình AI**. Bảng phía trên cho biết mỗi việc đang dùng mô hình nào (đọc thật từ `config/ai.toml`). Các hãng chưa có khóa hiện nhãn xám "chưa có khóa" và không chọn được.
2. Ở mục **🎭 Thử mù**, nhập **Từ khóa thử** (và ghi chú nếu muốn), chọn **2 mô hình** hoặc **3 mô hình**. Với mỗi ứng viên, chọn hãng, tên mô hình và mức nghĩ (effort). Có thể thử giữa các mô hình của cùng một hãng.
3. App báo trước: *"Bấm chạy sẽ gọi AI N lần (mỗi mô hình một lần) và có tốn tiền"*. Mỗi bài thử ngắn (một mở bài và một mục), không tìm web nên tốn rất ít. Bấm **▶️ Chạy thử mù**.
4. Các bài hiện dưới tên **A / B / C** theo thứ tự ngẫu nhiên, tên mô hình bị che. Kéo thanh **Điểm** (1–10) cho từng bài.
5. Bấm **Chấm xong — hiện tên mô hình**. Bảng xếp hạng hiện ra kèm hãng và mô hình của từng bài, cùng hướng dẫn sửa `config/ai.toml` để dùng mô hình điểm cao nhất. Điểm đã chốt thì không chấm lại được; muốn thử lại, bấm **🔄 Xóa kết quả**.

Thử mù **không đọc và không ghi** `config/ai.toml` (không có mục `blind_test` trong đó): giới hạn độ dài bài thử cố định trong app. Muốn dùng kết quả, bạn tự sửa `config/ai.toml` như mục 7.2.

### 7.4. Soạn một bài

1. Vào **Soạn bài**, nhập từ khóa, bấm **Phân tích từ khóa**. Điền phần **Chất liệu thật** (kinh nghiệm, số liệu, câu hỏi khách hay hỏi): AI không tự bịa phần này.
2. Bấm **Tiếp: tạo dàn ý**, sửa / xóa / sắp xếp lại các mục, rồi bấm **Duyệt dàn ý**. AI viết toàn bài, tự rà soát theo checklist và sửa một lượt trước khi đưa bạn xem.
3. Ở bước **Viết & kiểm tra**: viết lại từng phần theo yêu cầu, sửa tay, áp dụng hoặc bỏ qua các gợi ý. Chỗ tô đỏ `[cần bổ sung: ...]` là nơi cần bạn điền số liệu thật.
4. Cũng ở bước này, mục nào có khung **📷 Chỗ cần ảnh** thì chọn ảnh, viết alt rồi duyệt (mục 9).
5. Ở bước **SEO**: chọn tiêu đề, mô tả hiện trên Google, đường dẫn của bài, liên kết nội bộ, schema hỏi đáp (mục 10).
6. Ở bước **Xuất bản**, hình thức **Nháp**, bấm **📤 Gửi nháp** để gửi bài nháp kèm ảnh lên website (mục 11).

Mỗi bước AI mất khoảng 1–4 phút. Bài đang soạn được **tự lưu** sau mỗi thay đổi (vào `data/drafts.sqlite` trên máy, không lên GitHub). Tải lại trang hay tắt app vẫn không mất bài: vào **Soạn bài**, khung **Bài đang soạn dở** ở bước 1 có nút Mở và Xóa.

### 7.5. Tùy chỉnh khác (không cần sửa code)

Mở bằng Notepad / TextEdit:
- `config/ai.toml`: hãng, mô hình, mức "suy nghĩ" (effort) và độ dài tối đa (`max_tokens`) cho từng việc.
- `config/content.toml`: cách xưng hô, giọng văn, cụm từ cấm, checklist rà soát; mục `[meta]`: đuôi thương hiệu « | Pro-Metal» gắn sau tiêu đề SEO, các cụm nên tránh trong tiêu đề, mô tả SEO.
- `config/business_profile.md`: hồ sơ doanh nghiệp AI được phép dùng. Ý nào chưa chắc, đánh dấu bằng nhãn `[CẦN XÁC NHẬN]` thì AI bỏ qua ý đó (viết hoa hay thường, có dấu hay không dấu, ngoặc vuông `[ ]` hay ngoặc tròn `( )` đều được; nhớ gõ dấu mở ngoặc). Nhãn đặt trên tiêu đề (ví dụ `## 7. … [CẦN XÁC NHẬN]`) thì AI bỏ cả mục, tới tiêu đề cùng cấp kế tiếp. Khi đã xác nhận, xóa nhãn đi. Chi tiết nằm ngay đầu file đó.

### 7.6. Lỗi thường gặp

Dấu `…` là chỗ app điền tên cụ thể (tên hãng, tên mô hình, con số).

| App báo | Cách xử lý |
|---|---|
| "Chưa có khóa Anthropic (Claude) (ANTHROPIC_API_KEY). Vào Cài đặt → 🔌 Kết nối để nhập khóa. Các bước dùng AI tạm khóa cho tới khi sửa xong.", hoặc "…OpenAI (OPENAI_API_KEY)…", "…Google Gemini (GEMINI_API_KEY)…" | Việc đó trong `config/ai.toml` đang dùng hãng chưa có khóa. Vào **Cài đặt → 🔌 Kết nối** nhập khóa, hoặc đổi hãng của việc đó (mục 7.2). |
| "Khóa ANTHROPIC_API_KEY trong file .env không đúng." (cũng có bản cho `OPENAI_API_KEY`, `GEMINI_API_KEY`) | Tạo khóa mới ở trang của hãng, nhập lại ở **Cài đặt → 🔌 Kết nối**, bấm **Kiểm tra**. |
| Ở nút Kiểm tra: "Khóa Claude (hoặc ChatGPT, Gemini) không đúng hoặc đã bị thu hồi." | Như trên: khóa sai hoặc đã bị xóa ở trang của hãng. |
| Ở nút Kiểm tra: "Khóa … không có quyền truy cập…" | Khóa đúng nhưng tài khoản chưa được cấp quyền dùng API. Mở trang của hãng (Console, OpenAI, Google AI Studio) để kiểm tra. |
| "Tài khoản Anthropic đã hết tiền (credit)." | Nạp thêm credit ở console.anthropic.com → Billing. |
| "Tài khoản OpenAI đã hết tiền (credit) hoặc hết hạn mức." | Nạp thêm tiền hoặc kiểm tra hạn mức ở trang quản lý thanh toán của OpenAI. |
| "Tài khoản Gemini đã hết tiền hoặc hết hạn mức (quota) trong ngày." | Đợi sang ngày mới, hoặc bật thanh toán ở Google AI Studio. |
| "Bài dài quá giới hạn (… token). Tăng max_tokens của việc «…» trong config/ai.toml." | Mở `config/ai.toml`, tăng `max_tokens` của việc được nêu tên (ví dụ từ 32000 lên 48000). |
| "AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt vì quá giới hạn … token)…" (Claude) | Bấm thử lại; nếu vẫn lỗi, tăng `max_tokens` như trên. |
| Ở thử mù: "Bài thử dài quá giới hạn 2000 token của phần thử mù…" | Giới hạn này cố định, không sửa trong `config/ai.toml`. Chọn effort thấp hơn (`low` hoặc `medium`) cho ứng viên đó rồi chạy lại. |
| "Anthropic đang giới hạn số lần gọi. Đợi một phút rồi thử lại." (cũng có bản cho OpenAI, Gemini) | Đợi một phút rồi bấm lại. |
| "Anthropic báo lỗi … Thử lại sau ít phút." (cũng có bản cho OpenAI, Gemini), "… trả lời quá lâu. Bấm thử lại." | Máy chủ của hãng đang bận hoặc quá tải. Đợi vài phút rồi thử lại. |
| "Không có mô hình «…». Kiểm tra lại tên trong config/ai.toml." | Tên mô hình gõ sai hoặc hãng đã bỏ mô hình đó. Xem tên đúng trong tài liệu của hãng và sửa `model`. |
| "Tài khoản … không được dùng mô hình «…»." | Tài khoản chưa được cấp mô hình đó. Đổi sang mô hình khác hoặc hỏi hãng. |
| "… không nhận yêu cầu (lỗi 400…) với mô hình «…». Kiểm tra tên mô hình và các thông số…" | Kiểm tra `model`, `max_tokens`, `effort`, `web_search` của việc được nêu tên trong `config/ai.toml`. |
| "Gemini chưa phục vụ khu vực mạng bạn đang dùng (User location is not supported)…" | Tắt VPN hoặc proxy rồi thử lại, hoặc đổi việc đó sang hãng khác trong `config/ai.toml`. |
| "Không kết nối được tới … Kiểm tra mạng Internet." hoặc "Mất kết nối tới … giữa chừng…" | Kiểm tra mạng rồi bấm thử lại. |
| "Máy chủ … trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy)…" | Thường do Wi-Fi bắt đăng nhập hoặc proxy công ty chen vào. Đăng nhập Wi-Fi hoặc đổi mạng rồi thử lại. |
| "AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú." | Bộ lọc an toàn của hãng chặn. Đổi cách viết từ khóa hoặc ghi chú. |
| "Thư viện của … chưa cài hoặc sai phiên bản. Đóng app, chạy lại run.bat / run.command…" | Đóng app, bấm đúp `run.bat` / `run.command` để app cài đúng thư viện. |

## 8. Đặt thư mục ảnh

App lấy ảnh công trình từ các thư mục bạn khai báo (USB, thư mục Google Drive for Desktop…) và đọc **thẻ** của mỗi ảnh từ **tên thư mục**: mã công trình, hạng mục, khu vực, trước/sau, ảnh thật hay ảnh AI. Đặt thư mục theo cách dưới đây để app đọc đúng thẻ; cách chọn ảnh cho bài ở mục 9.

**Khai báo thư mục**

1. Mở `.env`, điền dòng `IMAGE_FOLDERS`. Nhiều thư mục thì ngăn cách bằng dấu `;`, ví dụ:
   ```
   IMAGE_FOLDERS=E:/anh-cong-trinh;G:/My Drive/Anh SEO
   ```
   Trên Mac, ví dụ: `/Volumes/USB/anh-cong-trinh`.
2. Tắt app rồi mở lại. Vào **Cài đặt → 🖼️ Ảnh**: mỗi thư mục hiện tên ngắn (chỉ tên thư mục cuối, không hiện đường dẫn đầy đủ) kèm "✅ tìm thấy" hoặc "⚠️ Chưa thấy thư mục ảnh số … trên máy này (USB chưa cắm hoặc Google Drive chưa chạy?)".

- Khai báo thư mục **chứa** các thư mục công trình, đừng khai báo từng công trình: app không lấy mã công trình, hạng mục, khu vực, trước/sau từ tên của chính thư mục đã khai báo, chỉ từ tên các thư mục bên dưới nó.
- Thêm thư mục mới thì ghi vào **cuối** dòng, đừng đổi thứ tự các thư mục đã có: app nhớ ảnh theo số thứ tự thư mục trong dòng này (ảnh đã chọn trong bài đang soạn dở, dấu «ảnh AI» gắn tay ở mục 9), đổi thứ tự thì những thứ này không còn khớp đúng ảnh.
- Đừng để thư mục phần mềm (thư mục có `run.bat`) nằm trong Google Drive, OneDrive (hay thư mục nào tự đồng bộ lên mạng) hoặc trong thư mục ảnh. Trong đó có file `.env` (khóa AI, mật khẩu WordPress) và thư mục `data/` (bài đang soạn, dấu «ảnh AI» gắn tay): để vậy thì các file này lên mạng hoặc lẫn vào thư mục ảnh.

**Đặt tên thư mục công trình**

Mỗi công trình một thư mục; ảnh trước và sau khi làm để trong hai thư mục con:

```
Anh SEO/                            ← thư mục đã khai báo
├── CT012 - Cổng inox - Tân Phú/
│   ├── truoc/                      ảnh trước khi làm
│   ├── sau/                        ảnh sau khi làm
│   └── Ảnh AI/                     ảnh tạo bằng AI cho công trình này (nếu có)
└── Ảnh AI/                         ảnh tạo bằng AI dùng chung
```

- Tên thư mục công trình gồm các phần cách nhau bằng ` - ` (gạch ngang, hai bên có dấu cách), thứ tự nào cũng được:
  - mã công trình: `CT` và số, ví dụ `CT012`;
  - hạng mục: ghép từ danh sách có sẵn, ví dụ `Cổng inox`, `Cửa kéo`, `Lan can sắt`, `Mái tôn`;
  - khu vực: một quận/huyện của TP.HCM, Bình Dương hoặc Bà Rịa – Vũng Tàu, ví dụ `Tân Phú`, `Quận 7`, `Dĩ An`.
- Phần nào không có trong danh sách của app (tên khách, số điện thoại, địa chỉ, năm) thì app bỏ qua cả phần đó và không gửi đi đâu. Vì vậy hãy tách bằng ` - `: viết `CT012 - Cổng inox - Nhà anh Tuấn - Tân Phú`, đừng viết `CT012 Cổng inox nhà anh Tuấn - Tân Phú` (phần đầu có tên khách nên mất luôn mã và hạng mục).
- Thư mục trước/sau: `truoc` / `sau`, hoặc `Trước`, `Trước khi làm`, `Hiện trạng`, `Sau`, `Sau khi làm`, `Hoàn thành`… Ảnh để thẳng trong thư mục công trình thì không có thẻ trước/sau.
- Một thư mục ghi hai khu vực khác nhau (`Quận 7 - Tân Phú`) thì app để trống khu vực, không đoán.
- App hiểu cả tên không dấu (`Tan Phu`, `q7`), nhưng **nên gõ có dấu** (xem phần dưới).

**Ảnh AI**

- Để ảnh tạo bằng AI trong một thư mục con có chữ **AI**, ví dụ `Ảnh AI`, nằm **bên dưới** thư mục đã khai báo (trong thư mục công trình, hoặc ngay dưới thư mục đã khai báo như hình trên). Ảnh AI không bao giờ mang mã công trình, khu vực, trước/sau (chỉ giữ hạng mục), để bài viết không giới thiệu ảnh AI như công trình thật.
- Cũng có thể khai báo riêng thư mục ảnh AI làm một mục của `IMAGE_FOLDERS` (ví dụ `G:/My Drive/Ảnh AI`): tên thư mục đó có chữ AI hay tên công cụ tạo ảnh thì **mọi** ảnh trong đó là ảnh AI, khung chọn ảnh ghi «🤖 Mọi ảnh trong thư mục gốc này là ảnh AI».
- Các chữ làm ảnh thành ảnh AI. App tìm ở tên thư mục đã khai báo, tên **mọi** thư mục bên dưới nó và ở **tên file ảnh**, không phân biệt hoa thường:
  - chữ `AI` đứng riêng (`Ảnh AI`, `Hình AI`, `ai`, `IMG_AI_01.jpg`), và `GenAI`, `AI images`;
  - `minh họa`, `trí tuệ nhân tạo`, `phối cảnh`, `mô phỏng`, `render`, `do máy tạo`, `tạo tự động`;
  - tên công cụ tạo ảnh: Gemini, Imagen, Nano Banana, ChatGPT, GPT, DALL-E, Midjourney, Stable Diffusion, SDXL, Firefly, Copilot, Designer, Bing, Image Creator, Leonardo, Ideogram, Flux, Grok, Kling, Dreamina, Jimeng, Seedream, ComfyUI, Runway, Krea, Canva, Recraft, NightCafe, SeaArt, Hailuo, Sora. Tên file mặc định khi tải ảnh từ các công cụ này (ví dụ `Gemini_Generated_Image_….png`, `Designer (3).png`) cũng được nhận ra.
- Gõ tên công cụ theo cách viết chuẩn, liền một chữ: `Midjourney`, `Firefly`, `Copilot`, `Seedream`. App nhận được vài kiểu gõ tách (`Mid Journey`, `Co-Pilot`) nhưng không phải mọi kiểu: `Hai Luo`, `Leo nardo` thì không.

**Thư mục ảnh thật: tránh các chữ trên**

- Tên thư mục ảnh thật (kể cả thư mục khai báo trong `IMAGE_FOLDERS`) đừng có chữ `AI` đứng riêng hay tên công cụ đứng riêng (`Sora`, `Flux`, `Designer`, `Canva`, `Bing`…), ví dụ `Thuốc hàn Flux`, `Công ty Designer Home`: cả thư mục bị coi là ảnh AI và **mất thẻ** công trình.
- Gõ tên thư mục ảnh thật **có dấu**: `Nhà chị Ái`, `Nhà anh Minh Hòa` là ảnh thật; gõ không dấu `Nha chi Ai`, `Nha anh Minh Hoa` thì app đọc ra chữ `AI`, `minh họa` và coi là ảnh AI.
- Không để ảnh lấy từ mạng, ảnh tham khảo, ảnh của nơi khác trong thư mục ảnh: app không phân biệt được và coi chúng là ảnh công trình thật.

**App không ghi gì vào thư mục ảnh**

- App chỉ đọc ảnh: không đổi tên, không di chuyển, không ghi file nào vào thư mục ảnh hay Drive.
- Dấu «ảnh AI» bạn gắn bằng nút **🤖 Đây là ảnh AI** (mục 9) chỉ nhớ trên **máy đang dùng**, trong file `data/image_tags.sqlite`; máy kia không thấy. Muốn hai máy cùng thấy thì để ảnh AI vào thư mục có chữ AI trên Drive.
- Ảnh trong thư mục ảnh AI (hoặc tên file có dấu hiệu AI) luôn là ảnh AI, trong app không đổi được thành ảnh thật. Muốn đổi thì đổi tên hoặc chuyển ảnh sang thư mục khác.

**Lỗi thường gặp**

| App báo | Cách xử lý |
|---|---|
| "Không mở được file lưu thẻ ảnh (có thể chương trình khác đang giữ file, hoặc không có quyền ghi). Ảnh vẫn dùng thẻ đọc từ tên thư mục." (báo mãi, thử lại vẫn vậy) | Đóng chương trình khác đang mở file `data/image_tags.sqlite` (phần mềm xem file SQLite, phần mềm sao lưu…) rồi thử lại. Vẫn báo thì tắt app, xóa file `data/image_tags.sqlite`, mở lại app: chỉ mất các dấu «ảnh AI» gắn tay. Ảnh đã gắn dấu mà không nằm trong thư mục có chữ AI thì chọn lại sẽ là **Ảnh thật**: kiểm lại các ảnh đó. |
| "File lưu thẻ ảnh sửa tay bị hỏng nên đã được cất sang một bên (tên «…», cùng thư mục). Các dấu «ảnh AI» đã gắn tay trước đó không còn…" | App đã tự tạo file mới. Xem lại các ảnh AI không nằm trong thư mục có chữ AI, bấm lại **🤖 Đây là ảnh AI** nếu cần. |
| "Chưa lưu được dấu «ảnh AI» trên máy này: … Trong lần làm việc này app vẫn coi ảnh là ảnh AI." | Dấu chưa được lưu: lần sau chọn lại ảnh này, app coi là ảnh thật. Xử lý như dòng "Không mở được file lưu thẻ ảnh…" rồi bấm lại, hoặc chuyển ảnh vào thư mục có chữ AI. |

## 9. Chọn ảnh cho bài

Ở bước **Viết & kiểm tra** của **Soạn bài**, mục nào AI đề xuất cần ảnh (ở bước **Dàn ý** có nhãn **📷 cần ảnh**) thì có khung **📷 Chỗ cần ảnh**, kèm mô tả ảnh nên dùng. Cần khai báo thư mục ảnh trước (mục 8).

**Chọn ảnh thật**

1. Bấm **📁 Chọn ảnh từ thư mục**. Khung chọn ảnh mở ngay dưới chỗ đó: ô **Thư mục ảnh** (thư mục đã khai báo, chỉ hiện tên), ô **Thư mục con** để mở thư mục bên trong, nút **⬆ Lên một cấp**, **🔄 Quét lại**. Mỗi trang 12 ảnh nhỏ.
   - App chỉ xem thư mục khi bạn mở nó. Ổ Google Drive chậm thì app báo đang quét ở nền: đợi vài giây rồi bấm **🔄 Xem kết quả**.
   - App nhận ảnh JPG, PNG, WebP, mỗi ảnh tối đa 40 MB. Lối tắt, mục ẩn, file khác (kể cả ảnh AVIF `.avif`) bị bỏ qua (khung ghi số mục bỏ qua).
   - **Tạm chưa nhận ảnh HEIC của iPhone** (file `.heic`, `.heif`): thư viện đọc HEIC đang chờ bản vá lỗi bảo mật, nên ảnh HEIC không hiện trong khung. Hãy dùng ảnh JPEG: ảnh gửi qua Zalo đã là JPEG; muốn iPhone chụp thẳng JPEG thì vào **Cài đặt → Camera → Định dạng → Tương thích nhất**.
2. Bấm **Chọn** dưới ảnh muốn dùng. Khung hiện ảnh xem trước, tên file, thư mục, và:
   - **📷 Ảnh thật** hoặc **🤖 Ảnh AI**. Ảnh AI có dòng «Vì sao là ảnh AI: …» (tên thư mục, tên file có chữ AI hay tên công cụ tạo ảnh, hoặc ảnh đã được đánh dấu).
   - **Thẻ** đọc từ tên thư mục, ví dụ «Mã CT012 · Cổng inox · Tân Phú · Trước khi làm». Tên thư mục chưa theo quy ước (mục 8) thì ghi «Chưa có thẻ (tên thư mục chưa theo quy ước).»
   - **Vị trí GPS**: «📍 Ảnh có vị trí GPS: vị trí này lên website cùng ảnh.» hoặc «Ảnh không có vị trí GPS.» (ảnh gửi qua Zalo thường đã mất GPS).
3. Viết alt (dòng chữ mô tả ảnh cho Google và người khiếm thị): tự gõ vào ô **Alt**, hoặc bấm **✨ AI viết alt**. AI chỉ xem đúng ảnh này, và là bản sao đã bỏ GPS, thông tin máy chụp (hãng AI nào, xem mục 7.2). Chưa ưng thì bấm **🔄 AI viết lại alt** hoặc sửa tay. Ô **Chú thích dưới ảnh** không bắt buộc. Alt dài tối đa 125 ký tự (dưới ô có đếm), chú thích tối đa 200; dài hơn thì app nhắc.
4. Đọc lại alt và chú thích: đúng với ảnh, không có tên, số điện thoại, địa chỉ khách. Rồi tick **✅ Đã duyệt**. Sửa chữ thì phải tick lại. Alt có dãy số giống số điện thoại thì app nhắc.

Còn ảnh nào chưa có alt hay chưa tick **Đã duyệt** thì chưa gửi bài được (mục 11). Nút khác: **📂 Mở thư mục chứa ảnh**, **🔁 Chọn ảnh khác**, **✖ Bỏ ảnh**. Ảnh đã chọn, alt, chú thích được lưu cùng bài đang soạn dở trên máy này; mở lại bài, app kiểm lại ảnh trên máy và báo nếu ảnh đã bị xóa hay đổi tên.

Lúc bạn tick **Đã duyệt**, app nhớ «dấu vân tay» của đúng bản ảnh đang hiện (lưu trong nháp trên máy, không gửi đi đâu). Mở lại bài mà file ảnh đã bị thay bằng ảnh khác cùng tên thì ở khung ảnh app bỏ **Đã duyệt** («Ảnh này khác bản bạn đã duyệt trước đó…»), bắt xem lại ảnh, alt, chú thích rồi duyệt lại; bấm gửi thẳng ở bước Xuất bản thì app dừng, chưa gửi gì. Bài soạn dở lưu bằng bản app cũ (trước khi app có dấu vân tay này) thì các ảnh đã duyệt phải tick **Đã duyệt** lại một lần; app báo «… nháp không có «dấu vân tay» của ảnh lúc duyệt …».

**Ảnh AI**

Tạo ảnh ngay trong app đang tạm hoãn (hai nút **🎨 Tạo ảnh**, **🔄 Prompt khác** bị khóa). Cách làm:

1. Ở đầu khung chỗ cần ảnh, chọn **Ảnh AI**: app hiện **prompt** (lời mô tả để tạo ảnh). Bấm biểu tượng ở góc khung để sao chép, hoặc **✏️ Sửa prompt**.
2. Dán prompt vào Gemini (hoặc công cụ tạo ảnh khác), tải ảnh về máy.
3. Lưu ảnh vào thư mục có chữ **AI** hay **minh họa** trong tên (ví dụ `Ảnh AI`, `Ảnh minh họa`), bên dưới thư mục đã khai báo (mục 8).
4. Bấm **📁 Chọn ảnh từ thư mục**, mở thư mục đó, chọn ảnh: khung hiện **🤖 Ảnh AI**. Ảnh AI lên website với alt mở đầu «Minh họa», chú thích (nếu có) mở đầu «Ảnh minh họa (AI)», tên file `minh-hoa-ai-…`, không mang mã công trình, khu vực, trước/sau.

Chọn **Ảnh AI** ở đầu khung chỉ để hiện prompt. Ảnh có phải ảnh AI hay không là do tên thư mục, tên file, hoặc nút dưới đây.

**Nút 🤖 Đây là ảnh AI**: ảnh hiện **📷 Ảnh thật** mà thật ra do AI tạo (ví dụ lỡ để lẫn trong thư mục công trình) thì bấm nút này. Alt được thêm «Minh họa» ở đầu, chú thích (nếu có) thêm «Ảnh minh họa (AI)», và phải duyệt lại; mọi chỗ trong bài dùng cùng ảnh cũng đổi theo.

- **Trong app không đổi lại thành ảnh thật được.** Lỡ bấm nhầm thì đổi tên file ảnh (hoặc chuyển sang thư mục khác), bấm **🔄 Quét lại** rồi chọn lại.
- Dấu này chỉ nhớ trên **máy đang dùng**, trong file `data/image_tags.sqlite`. Xóa file đó, đổi thứ tự thư mục trong `IMAGE_FOLDERS`, hay dùng máy kia thì khi chọn lại, ảnh đó là **Ảnh thật**. Vì vậy cách chắc nhất vẫn là để ảnh AI trong thư mục có chữ AI.

## 10. Bước SEO: tiêu đề, mô tả, đường dẫn

Bước **4 · SEO** của **Soạn bài** chuẩn bị những gì Google thấy: dòng tiêu đề và đoạn mô tả trên trang kết quả tìm kiếm, đường dẫn của bài; kèm liên kết tới các bài đã có trên website và schema hỏi đáp. Làm sau khi bài đã viết xong ở bước **Viết & kiểm tra**. Mọi lựa chọn ở bước này được **tự lưu vào nháp** như các bước trước.

- Các nút AI (✨, 🔄 của ô tiêu đề, mô tả) cần khóa của hãng ghi ở `[tasks.meta]`, `[tasks.links]` trong `config/ai.toml` (mục 7.2). Thiếu khóa thì nút mờ, bạn vẫn tự gõ được.
- Chưa kết nối WordPress (mục 6) thì đầu bước có một dòng báo nhẹ «Chưa kết nối WordPress nên chưa có danh sách bài đã đăng…». Tiêu đề, mô tả, đường dẫn, khung chép, schema vẫn dùng được; chỉ thiếu kiểm trùng và liên kết nội bộ.

**Tiêu đề và mô tả (meta title, meta description)**

1. Bấm **✨ AI gợi ý tiêu đề và mô tả SEO** (nút này chỉ hiện khi hai ô còn trống). AI đưa vài phương án; ô **Meta title** và **Meta description** hiện phương án đầu, dưới ô ghi «Bản 1/…».
2. Cạnh mỗi ô có ba nút: **🔄** để AI viết lại **riêng ô đó** (ô kia giữ nguyên), **↶** về bản trước, **↷** tới bản sau. Tự sửa chữ trong ô cũng thành một bản mới, nên luôn quay lại được bản AI.
3. Ô Meta title **không cần gõ tên thương hiệu**: app tự gắn đuôi « | Pro-Metal» khi tiêu đề cộng đuôi không quá 60 ký tự (đổi đuôi ở mục `[meta]` của `config/content.toml`, mục 7.5).

**Nhãn Nên / Cảnh báo / Chặn**

Dưới mỗi ô có nhãn màu, số ký tự (đếm như Google thấy; tiêu đề tính cả đuôi « | Pro-Metal») và lý do:

| Nhãn | Nghĩa | Khi nào |
|---|---|---|
| **Nên** (xanh) | Dùng được. | Tiêu đề 50–60 ký tự, mô tả 120–155 ký tự. Hơi ngắn hay hơi dài một chút vẫn là Nên, kèm lời nhắc. |
| **Cảnh báo** (cam) | Vẫn dùng được, nên sửa. | Tiêu đề dưới 30 hay trên 65 ký tự, mô tả dưới 70 hay trên 160 ký tự (Google cắt bớt); giống nhiều một bài đã đăng. |
| **Chặn** (đỏ) | Không chép được, không ghi lên website. | Ô trống; có ký tự lạ không nhìn thấy (thường lẫn vào khi dán từ nơi khác: xóa ô rồi gõ lại); có thẻ HTML hay dấu `<` viết liền chữ, số (ví dụ `<2m`: viết «dưới 2m»); có `%%`, mã ký tự kiểu `&#37;`, đoạn dạng shortcode `[...]`; trùng hệt tiêu đề, mô tả hay đường dẫn của một bài đã đăng. |

**Đường dẫn (slug)**

- Ô **Đường dẫn (slug)** tự gợi ý từ từ khóa: không dấu, nối bằng gạch ngang, ví dụ `cua-cong-inox-tan-phu`. Sửa tay được, app tự bỏ dấu và nối gạch ngang. Nút **🔄** bên cạnh gợi ý lại từ từ khóa.
- Nên 3–7 từ, không quá 60 ký tự; trống hay trùng hệt đường dẫn của bài đã đăng thì **Chặn**.
- Từ khóa chính có vấn đề (trống, có ký tự lạ, có chữ website không nhận như `<2m`, dài quá 200 ký tự) thì dưới ô đường dẫn có thêm dòng **Từ khóa chính** nhãn **Chặn**, kèm câu «… Sửa từ khóa ở bước 1 · Chuẩn bị.»

**Kiểm trùng với bài đã đăng**

App lấy danh sách bài đã đăng trên website và so với tiêu đề, mô tả, đường dẫn của bài này: trùng hệt một bài thì **Chặn**, giống nhiều thì **Cảnh báo**, kèm tên bài bị trùng. Danh sách được lưu tạm trên máy (file `data/site_index.sqlite`, dùng lại tới 6 giờ). Vừa đăng bài mới trên website thì bấm **🔄 Tải lại danh sách bài** (ở phần Liên kết nội bộ). Website có quá nhiều bài thì app báo «… danh sách chưa đủ, kiểm trùng có thể sót.»

**Xem trước và «Chép sang SiteSEO»** (cột bên phải)

- **Xem trước trên Google**: tiêu đề (đã gắn đuôi), tên website › đường dẫn, mô tả, gần giống cách Google hiện.
- **Chép sang SiteSEO**: ba khung **Tiêu đề SEO** (đã gắn đuôi), **Mô tả SEO**, **Đường dẫn (slug)**. Bấm biểu tượng ở góc khung để chép. Trong trang sửa bài nháp của WordPress: tiêu đề, mô tả dán vào hộp SiteSEO; đường dẫn dán vào ô đường dẫn (slug) của bài. Ô đang **Chặn** thì khung ghi «…: chưa chép được.» kèm lý do.
- Muốn app tự ghi tiêu đề, mô tả thay vì chép tay: xem «Ghi SEO lên website» bên dưới.

**Liên kết nội bộ**

Cần kết nối WordPress và có bài đã đăng cùng chủ đề.

1. Bấm **✨ AI gợi ý liên kết**. App chọn bài đích trong các bài đã đăng; AI chỉ chọn **cụm từ có sẵn trong bài** để đặt link, không viết thêm chữ.
2. Bảng **Dùng / Cụm từ trong bài / Trỏ tới bài**: bỏ tick **Dùng** ở dòng không muốn.
3. Nút mờ thì dòng chữ bên dưới nói lý do: AI chưa dùng được (thiếu khóa), hay chưa có danh sách bài đã đăng. Dòng «Chưa có bài đã đăng nào cùng chủ đề để đặt liên kết.» nghĩa là website chưa có bài phù hợp.

**App chưa chèn các liên kết này vào bài nháp khi gửi** (làm ở Giai đoạn 5). Muốn có link ngay thì tự thêm trong trang sửa bài WordPress, theo bảng này.

**Schema Hỏi đáp (FAQ)**

Schema là đoạn mã giúp Google hiểu phần hỏi đáp của bài. Mở khung **Schema (dữ liệu có cấu trúc cho Google)**:

- Bài cần có một mục tên «Câu hỏi thường gặp» (hay «Hỏi đáp»). Mỗi câu hỏi là tiêu đề con hay dòng in đậm, kết thúc bằng dấu «?», câu trả lời nằm ngay bên dưới. Chưa đúng dạng thì app nói cách viết lại.
- Đúng dạng thì app hiện đoạn mã (chép bằng biểu tượng ở góc) và ô **Dùng schema Hỏi đáp (FAQ) này cho bài**. Ô này chỉ ghi nhớ lựa chọn trong nháp: **app chưa gửi schema lên website**.

**Ghi SEO lên website** (ở bước Xuất bản)

Ở bước **5 · Xuất bản**, hình thức **Nháp**, phía trên nút **📤 Gửi nháp** có công tắc **Ghi SEO lên website**, **mặc định tắt**.

- **Tắt:** app chỉ tạo bài nháp; bạn chép tay từ khung «Chép sang SiteSEO».
- **Bật:** ngay sau khi tạo bài nháp, app ghi **tiêu đề SEO** (đã gắn đuôi), **mô tả SEO** và **từ khóa chính** vào hộp SiteSEO của **chính bài nháp app vừa tạo trong lần gửi đó**, rồi hỏi lại website để chắc bài vẫn là nháp. App không ghi SEO vào bài nào khác: bài đã có sẵn trên website, bài nháp tạo ở lần gửi trước, bài đã chuyển sang «Chờ duyệt» hay đã đăng đều không bị đụng tới. Đường dẫn, liên kết nội bộ, schema không ghi.
- Cần làm trước trên website: SiteSEO từ bản 1.4.0, bật **AI Abilities** (mục 6, bước 8–10: **Kiểm tra kết nối** thấy «SiteSEO: ghi được»).
- Ô nào đang **Chặn** ở bước SEO thì không ghi ô đó, các ô còn lại vẫn ghi. Bật công tắc là thấy trước: «Sẽ không ghi …: ở bước SEO đang báo «Chặn» (xem lý do ở đó).»
- Khung **Kiểm tra trước khi gửi** có dòng «✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng» hoặc «⚠️ SEO: … chưa dùng được (xem bước SEO)».

Gửi xong, dưới dòng «Đã tạo bài nháp trên WordPress (mã …)» có một dòng kết quả SEO:

| App báo | Cách xử lý |
|---|---|
| «Đã ghi SEO vào hộp SiteSEO của bài nháp.» | Xong. Bấm **Mở bài nháp trong WordPress** xem hộp SiteSEO. |
| «Website chưa cho phần mềm ghi SEO (SiteSEO chưa bật Abilities)…» | Lần này chép tay từ khung «Chép sang SiteSEO». Lần sau: bật AI Abilities (mục 6, bước 8–9). |
| «Đã ghi tiêu đề, mô tả SEO vào bài nháp. Từ khóa chính chưa ghi được…» | Chép tay từ khóa chính vào hộp SiteSEO. |
| «Bài này không còn là bản nháp trên website…» | Bài vừa bị đăng hay bị xóa trước khi app ghi; app không sửa bài đã đăng. Sửa tay trong WordPress nếu cần. |
| «Ghi SEO lên website không thành công…», «Không kiểm được bài nháp trên WordPress trước khi ghi SEO…», «Ghi SEO lên website gặp lỗi không mong đợi…» | Bài nháp vẫn còn. Mở bài nháp trong WordPress xem hộp SiteSEO; thiếu chữ thì chép tay từ khung «Chép sang SiteSEO» (đừng gửi lại: gửi lại sẽ tạo thêm một bài nháp nữa). |
| «… Kiểm lại ngay sau khi ghi SEO: …» | Đã ghi, nhưng lúc hỏi lại website có trục trặc. Mở bài trong WordPress xem bài còn là nháp và hộp SiteSEO đã đúng chữ. |
| «… Không ghi …: ở bước SEO đang báo «Chặn»…» | Các ô bị Chặn không được ghi. Sửa ở bước SEO rồi chép tay vào hộp SiteSEO. |

## 11. Gửi bài nháp lên WordPress

Cần kết nối WordPress trước (mục 6). Ở bước **Xuất bản** của **Soạn bài**, hình thức **Nháp**:

1. Xem khung **Kiểm tra trước khi gửi**, trong đó có dòng «Chỗ cần ảnh đã có ảnh, alt đã duyệt: …». Ảnh nào chưa có alt hay chưa duyệt thì app báo tên mục và khóa nút gửi. Chỗ cần ảnh để trống thì bài gửi đi không có ảnh ở chỗ đó.
2. Bài có từ 2 ảnh: chọn ảnh ở ô **Ảnh đại diện** (mặc định là ảnh đầu tiên). Bài một ảnh thì ảnh đó là ảnh đại diện.
3. Nếu có khung vàng **«Có đoạn dạng shortcode»**: app liệt kê các đoạn dạng `[...]` trong tiêu đề, nội dung, alt, chú thích. Lúc gửi, app làm cho chúng không chạy; nhưng nếu sau đó bạn sửa và lưu bài trong trang quản trị WordPress thì WordPress sẽ chạy chúng. **Nên xóa** các đoạn đó rồi mới gửi (ở bước **Viết & kiểm tra**: nội dung bấm **✏️ Sửa** ở từng mục, alt và chú thích sửa ở khung ảnh). Đoạn nằm ở **tiêu đề bài** hay **tiêu đề mục** thì chưa sửa được ở bước này: gửi nháp xong, mở bài trong WordPress và xóa đoạn đó **trước khi** bấm Lưu hay Đăng. (Cách khác: sửa tiêu đề ở bước **Dàn ý** rồi duyệt lại để AI viết lại toàn bài; cách này mất phần đã sửa tay và phải chọn lại ảnh.)
4. Muốn app ghi luôn tiêu đề, mô tả SEO, từ khóa chính vào hộp SiteSEO của bài nháp: bật công tắc **Ghi SEO lên website** (mặc định tắt, xem mục 10).
5. Ngay trên nút, app nhắc ảnh xem được công khai (xem «Cần biết khi gửi» bên dưới). Bấm **📤 Gửi nháp**, rồi **đợi app báo kết quả** (xem «App nhớ việc đã gửi» bên dưới).

Gửi xong, app báo «Đã tạo bài nháp trên WordPress (mã …)», có nút **Mở bài nháp trong WordPress** và danh sách ảnh đã lên thư viện Media (tên file, địa chỉ ảnh). Bật **Ghi SEO lên website** thì có thêm một dòng kết quả SEO (bảng ở mục 10). Nút gửi khóa lại; muốn tạo thêm một bài nháp nữa từ bài này thì tick **Tạo thêm một bài nháp mới** (ảnh sẽ tải lên lần nữa).

**Cần biết khi gửi**

- **Chỉ tạo bài nháp.** Khách chưa thấy bài cho tới khi bạn tự bấm Đăng trong WordPress. App không sửa bài có sẵn.
- **Ảnh xem được công khai ngay khi tải lên, kể cả khi bài còn là nháp**: ảnh vào thư viện Media của website, mà WordPress cho **bất kỳ ai, không cần đăng nhập**, xem danh sách Media (kèm địa chỉ ảnh, alt, chú thích). Người lạ tìm được ảnh mà không cần ai gửi đường dẫn, mở ảnh là đọc được vị trí GPS còn trong ảnh. App **không tự xóa** ảnh đã tải lên, kể cả khi bạn xóa bài nháp; muốn gỡ ảnh thì xóa trong **Media → Thư viện** của trang quản trị. Xóa chỉ gỡ ảnh khỏi website: ai đã tải ảnh về vẫn còn bản sao.
- Ảnh được nén WebP, cạnh dài tối đa 1600 px (cỡ và chất lượng đổi được ở mục `[images]` trong `config/content.toml`), giữ vị trí GPS. Tên file do app đặt từ thẻ (thiếu thẻ thì từ alt), không dấu, ví dụ `cong-inox-tan-phu-ct012.webp`; không lấy tên file, tên thư mục trên máy (có thể có tên khách).
- Bài nháp gồm tiêu đề, các mục (tiêu đề mục, đoạn văn), ảnh kèm alt, chú thích, ảnh đại diện. Chữ đậm, gạch đầu dòng viết bằng dấu `**`, `-` còn hiện nguyên dấu; chuyên mục, đường dẫn (slug), liên kết nội bộ, schema chưa gửi. Tiêu đề, mô tả SEO và từ khóa chính chỉ lên website khi bạn bật **Ghi SEO lên website** (mục 10); không bật thì chép tay vào hộp SiteSEO. Sửa trong WordPress trước khi đăng.

**Khi có lỗi**

- Lỗi trước khi gửi (ảnh vừa đổi hay bị thay bằng ảnh khác cùng tên, ổ đĩa chậm, ảnh hỏng, chưa ghi được trạng thái gửi vào nháp…): app ghi «Chưa gửi gì lên website» kèm lý do. Sửa rồi bấm lại.
- Lỗi giữa chừng: bài nháp và ảnh có thể **đã lên website**. App liệt kê ảnh đã lên thư viện Media và **không tự gửi lại**. Trước khi gửi lại, mở trang quản trị WordPress, kiểm tra **Bài viết → Nháp** và **Media → Thư viện**, xóa bài nháp, ảnh thừa nếu có. Khi app không chắc bài nháp đã có hay chưa, nút gửi khóa tới khi bạn tick **Tôi đã kiểm tra trang quản trị, vẫn muốn gửi**.

**App nhớ việc đã gửi**

App ghi «đang gửi» vào bài nháp trên máy ngay trước khi gửi, và ghi «đã gửi» kèm mã bài nháp khi website trả lời. Vì vậy tải lại trang (F5), đóng tab, mở bài khác rồi mở lại, hay hôm sau mở lại bài, app vẫn nhớ và không cho gửi trùng khi bạn chưa xác nhận:

- **Bài đã gửi:** app ghi «Bài này đã gửi lên WordPress (bài nháp mã …, lúc …). Gửi lại sẽ tạo thêm một bài nháp mới và tải ảnh lên lần nữa.», có nút **Mở bài nháp trong WordPress**. Nút gửi khóa tới khi bạn tick **Tạo thêm một bài nháp mới**.
- **Lần gửi trước chưa có kết quả** (tải lại trang, đóng tab hay mất mạng đúng lúc đang gửi, hoặc đang gửi ở cửa sổ khác): app nhắc «… **bài nháp có thể đã có trên website**», khóa nút tới khi bạn tick **Tôi đã kiểm tra trang quản trị, vẫn muốn gửi**. Kiểm **Bài viết → Nháp** và **Media → Thư viện** trước khi tick; đang gửi ở tab khác thì đợi tab đó xong rồi hãy xem.
- **Lỡ bấm nút khác, bấm đúp, hay sang trang khác rồi quay lại lúc đang gửi:** app không gửi thêm. Lần gửi chưa xong thì trang hiện ô «⏳ Lần gửi nháp vừa bấm vẫn đang chạy, đợi gửi xong rồi mới hiện kết quả…»; xong thì hiện kết quả (có thể kèm dòng «Lần gửi này bị ngắt giữa chừng…»). Nút gửi vẫn khóa, phải tick xác nhận mới gửi tiếp được. Website chậm quá 60 giây thì app báo «Lần gửi nháp trước vẫn đang chạy (website chậm?)…»: đợi thêm rồi bấm lại hoặc tải lại trang.
- **Cùng một bài mở ở hai tab (hay hai cửa sổ), bấm 📤 Gửi nháp ở cả hai:** chỉ ra **một** bài nháp. Tab bấm sau không gửi gì, báo «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi (thường do bài vừa được gửi, hoặc đang gửi, ở một tab khác của app)…», và nút gửi khóa theo lời nhắc phía trên nút.
- **Đã tick xác nhận rồi gửi, mà lần gửi đó hỏng trước khi tạo được bài** (ví dụ mất mạng lúc tải ảnh): bài giữ nguyên khóa như trước lúc gửi (vẫn «chưa có kết quả», hay vẫn «đã gửi» bài cũ). Muốn gửi tiếp thì kiểm trang quản trị rồi tick lại.

**Lần gửi thật đầu tiên**

Thử **một bài, một ảnh, một tab**, chọn ảnh app báo «📍 Ảnh có vị trí GPS» **chụp ở nơi đã công khai** (xưởng, cửa hàng); đừng dùng ảnh nhà khách cho lần thử. Gửi xong, tải ảnh đó từ website về máy để kiểm GPS:

1. Trong danh sách ảnh đã lên thư viện Media, chép địa chỉ ảnh (dòng bắt đầu bằng `https://`), dán vào trình duyệt, chuột phải vào ảnh → **Save image as** để lưu về máy.
2. Trên Windows: chuột phải file vừa lưu → **Properties** → thẻ **Details**, kéo xuống phần **GPS**. Có **Latitude**, **Longitude** là ảnh còn GPS; không có phần đó thì báo Chỉ Huy. Trên Mac chưa thử cách kiểm này.
3. Kiểm xong thì xóa ngay bài nháp và ảnh thử trong trang quản trị (**Bài viết → Nháp**, **Media → Thư viện**).

## 12. Cập nhật phiên bản mới

- Với GitHub Desktop: mở dự án, bấm **Fetch origin**, rồi bấm **Pull origin** nếu có.
- Sau đó chạy `run.bat` / `run.command` như bình thường. Thư viện mới (nếu có) sẽ được cài tự động.
- Riêng công cụ `uv` **không** tự nâng. Bản mới của phần mềm đòi `uv` mới hơn thì cửa sổ báo `Required uv version …`: nâng `uv` như cuối mục 2 (Windows) hoặc cuối mục 3 (Mac).
- File `.env` của bạn không bị ghi đè.

## 13. Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| "Không cài được uv" | Kiểm tra mạng rồi chạy lại. Nếu vẫn lỗi, cài uv thủ công theo hướng dẫn ở https://docs.astral.sh/uv/getting-started/installation/ |
| Cửa sổ đen / Terminal báo `error: Required uv version … does not match the running version …`, rồi "Cài thư viện bị lỗi", app không mở | Công cụ `uv` trên máy cũ hơn bản phần mềm cần (từ 0.13.4, vì lỗi bảo mật chứng chỉ). Nâng `uv` theo cuối mục 2 (Windows) hoặc cuối mục 3 (Mac), rồi bấm đúp `run.bat` / `run.command` lại. Phần cuối câu báo (gợi ý cách sửa, bằng tiếng Anh) có thể khác nhau tùy bản `uv`; chỉ cần câu bắt đầu bằng `Required uv version`. `set_password.bat` / `set_password.command` cũng báo câu này khi `uv` cũ: nâng `uv` như trên. |
| "Cài thư viện bị lỗi" (không có dòng `Required uv version` phía trên) | Chụp màn hình cửa sổ và gửi người hỗ trợ. |
| Trình duyệt không tự mở | Tự mở trình duyệt và vào địa chỉ in trong cửa sổ đen (thường là `http://localhost:8501`). |
| Lỡ mở app hai lần | Lần thứ hai sẽ dùng cổng khác (8502…). Nên đóng bớt một cửa sổ. |
| App báo "Múi giờ APP_TIMEZONE không hợp lệ" | Sửa dòng `APP_TIMEZONE` trong `.env` thành `Asia/Ho_Chi_Minh`. |

---

## Dành cho người phát triển

Cần có [uv](https://docs.astral.sh/uv/) từ bản 0.13.4 (`required-version` trong `pyproject.toml`; bản cũ hơn bị từ chối ở lệnh dự án như `uv sync`, `uv run`, nâng bằng `uv self update`). `required-version` không áp dụng cho `uvx`: kiểm `uv --version` trước khi dùng `uvx` (quy tắc ở `docs/team/security.md` mục 5).

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
app/          giao diện Streamlit: main.py (đăng nhập, menu), views/ (từng trang),
              assets/ (logo, style.css); dữ liệu mẫu demo nằm ở seo_app/demo.py
seo_app/      phần logic: config.py (đọc .env), auth.py (mật khẩu), text.py (xử lý chữ),
              wordpress/ (client REST API)
scripts/      script tiện ích (hash_password.py)
tests/        kiểm thử pytest
.streamlit/   cấu hình Streamlit (chỉ mở ở localhost, không thu thập số liệu)
.claude/      hook cài thư viện cho phiên Claude Code trên cloud; agents/ (hồ sơ đội agent)
docs/team/    quy tắc, chính sách bảo mật, phiếu giao việc, báo cáo của đội agent
AGENTS.md     điểm bắt đầu cho mọi AI làm tiếp dự án
```

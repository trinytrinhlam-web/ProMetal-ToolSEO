# SEO App

Phần mềm chạy ngay trên máy tính (Windows và Mac) để triển khai kế hoạch SEO cho website WordPress: nghiên cứu, viết bài bằng AI, xử lý ảnh, tối ưu meta/schema, gắn liên kết nội bộ, đăng bài và theo dõi thứ hạng.

App mở trong trình duyệt tại địa chỉ `http://localhost:8501`. Địa chỉ này chỉ dùng được trên chính máy bạn, người khác không truy cập được.

> **Trạng thái:** đã có đăng nhập, kết nối WordPress (kiểm tra kết nối, xem chuyên mục/thẻ, tạo bài nháp có ảnh đại diện) và viết bài bằng AI (Claude, ChatGPT, Gemini; có thử mù để chọn mô hình, xem mục 7). Các chức năng khác sẽ được thêm dần theo lộ trình trong `CLAUDE.md`.

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
- Tải lại trang (F5) thì phải đăng nhập lại. Đây là chủ ý để bảo mật. Nút **Đăng xuất** nằm ở trang Cài đặt.
- **Menu trên cùng**: **Bài viết** (các bài đang viết), **Soạn bài** (viết một bài qua 5 bước), **Kế hoạch** (đưa kế hoạch của bạn vào), **Cài đặt**, **Kết nối WordPress**.
- Chỗ nào có nhãn cam **"Bản demo"** là đang dùng dữ liệu mẫu để bạn xem trước: bấm thử thoải mái, không gửi gì đi đâu. Chức năng sẽ chạy thật khi tới giai đoạn tương ứng. Ba bước đầu của **Soạn bài** đã dùng AI thật (xem mục 7).

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

App gửi bài sang WordPress bằng **Application Password**: một mật khẩu riêng cho app, khác mật khẩu đăng nhập thường. Bạn có thể thu hồi nó bất cứ lúc nào mà không ảnh hưởng tài khoản.

1. Đăng nhập trang quản trị WordPress (`https://ten-mien-cua-ban/wp-admin`).
   - Nên tạo một tài khoản riêng cho app, vai trò **Biên tập viên (Editor)**.
2. Vào **Người dùng → Hồ sơ** (Users → Profile), kéo xuống mục **Application Passwords**.
3. Gõ tên, ví dụ `SEO App - may cong ty`, rồi bấm **Thêm Application Password mới**.
4. WordPress hiện một dãy dạng `abcd efgh ijkl mnop qrst uvwx`. **Chép ngay**: dãy này chỉ hiện một lần.
5. Mở file `.env`, điền:
   ```
   WORDPRESS_URL=https://ten-mien-cua-ban
   WORDPRESS_USERNAME=ten-dang-nhap-wordpress
   WORDPRESS_APP_PASSWORD=abcd efgh ijkl mnop qrst uvwx
   ```
6. Tắt app rồi mở lại. Vào menu **Kết nối WordPress** và bấm **Kiểm tra kết nối**.

Ở trang này bạn còn có thể:
- bấm **Tải chuyên mục và thẻ** để xem danh sách đang có trên website;
- **tạo thử một bài nháp** có ảnh đại diện.

App **chỉ tạo bài nháp**: khách không thấy bài cho tới khi bạn tự bấm Đăng trong WordPress. Bài thử có thể xóa trong WordPress sau khi kiểm tra.

**Lỗi thường gặp**

| App báo | Cách xử lý |
|---|---|
| "WordPress từ chối đăng nhập" | Kiểm tra lại tên đăng nhập và Application Password trong `.env`. Nếu đã đúng, có thể plugin bảo mật (Wordfence, iThemes…) đang tắt Application Passwords, hoặc hosting chặn header `Authorization`. Nhờ người quản lý website kiểm tra. |
| "Không tìm thấy REST API" | Kiểm tra `WORDPRESS_URL`. Trong WordPress vào **Cài đặt → Đường dẫn tĩnh** (Settings → Permalinks), bấm **Lưu thay đổi** một lần. |
| "không đủ quyền" | Tài khoản cần vai trò Biên tập viên hoặc Quản trị viên. |
| "Lỗi chứng chỉ bảo mật (SSL)" | Website chưa có https hợp lệ. Kiểm tra bằng cách mở website trên trình duyệt. |

## 7. Viết bài bằng AI

Trang **Soạn bài** dùng AI thật cho 3 bước đầu: **Chuẩn bị** (nghiên cứu từ khóa và các bài đứng đầu Google), **Dàn ý**, **Viết & kiểm tra**. Bước **SEO** và **Xuất bản** vẫn là bản demo.

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

Mỗi việc (nghiên cứu, dàn ý, viết bài, viết lại một phần, kiểm tra văn phong) dùng một mô hình riêng, khai báo trong `config/ai.toml`. Mở bằng Notepad / TextEdit, sửa hai dòng `provider` và `model` của việc cần đổi, lưu file rồi tải lại trang (F5, sẽ phải đăng nhập lại). Không cần sửa code.

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

Mỗi bước AI mất khoảng 1–4 phút. Bài đang soạn được **tự lưu** sau mỗi thay đổi (vào `data/drafts.sqlite` trên máy, không lên GitHub). Tải lại trang hay tắt app vẫn không mất bài: vào **Soạn bài**, khung **Bài đang soạn dở** ở bước 1 có nút Mở và Xóa.

### 7.5. Tùy chỉnh khác (không cần sửa code)

Mở bằng Notepad / TextEdit:
- `config/ai.toml`: hãng, mô hình, mức "suy nghĩ" (effort) và độ dài tối đa (`max_tokens`) cho từng việc.
- `config/content.toml`: cách xưng hô, giọng văn, cụm từ cấm, checklist rà soát.
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

## 8. Cập nhật phiên bản mới

- Với GitHub Desktop: mở dự án, bấm **Fetch origin**, rồi bấm **Pull origin** nếu có.
- Sau đó chạy `run.bat` / `run.command` như bình thường. Thư viện mới (nếu có) sẽ được cài tự động.
- File `.env` của bạn không bị ghi đè.

## 9. Xử lý sự cố

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

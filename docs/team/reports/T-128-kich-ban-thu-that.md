# Kịch bản buổi thử thật Hẹn giờ / Đăng ngay trên website (LC-T094-44)

| Mục | Nội dung |
|---|---|
| Phiếu | T-128 (`docs/team/tickets/T-128-so-rui-ro-va-kich-ban-thu-that.md`) |
| Soạn | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 · 2026-11-05; lượt 2 cùng ngày theo Lá Chắn T-128 (LC-T128-1, -2, -3; ghi nhận N1–N5) |
| Dùng cho | **Chỉ Huy** làm từng bước; **chủ dự án ngồi cùng**, duyệt bài thử và tự làm các việc trên trang quản trị cần mật khẩu hay xóa hẳn. **Lá Chắn** đọc bảng kết quả (mục 7) trước khi cho dùng Hẹn giờ / Đăng ngay |
| Khi nào | Khi chủ dự án báo rảnh (chủ dự án quyết 04/11). Cần khoảng 1 giờ 30 tới 2 giờ, trong đó có 15–20 phút chờ bài hẹn giờ tự đăng (lúc chờ không đụng tới website, ca 4) |
| Nguồn | Lá Chắn T-112 (mục «Điều kiện», phần B mục 4; bảng «Còn phải làm trước khi bật công tắc» lượt 3), Lá Chắn T-094 (LC-T094-44), Lá Chắn T-115 (điều kiện 4), Lá Chắn T-110 (điều kiện 3), Lá Chắn T-091 (điều kiện 4), Lá Chắn T-059 (ghi nhận 2), Lá Chắn T-097 (điều kiện 5), Fable T-116 nhóm 2 (các việc gom vào buổi thử), Lá Chắn T-128 (lượt 2), Lá Chắn T-136 (B.3; ca R do Soi Lỗi soạn, Lá Chắn sửa). README mục 11, mục 14 |

## 0. Tóm tắt (cho chủ dự án)

- Phần mềm đã làm xong Hẹn giờ và Đăng ngay nhưng đang **tắt**. Trước khi anh/chị dùng thật, cần một buổi thử trên chính website, có anh/chị ngồi cùng.
- Buổi thử gửi vài **bài thử** do anh/chị đọc và đồng ý trước:
  - phần lớn là bài nháp hay bài hẹn giờ xa, khách không thấy;
  - **hai bài sẽ hiện công khai vài phút** (một bài hẹn giờ 15 phút, một bài Đăng ngay) rồi gỡ ngay.
- Việc của anh/chị trong buổi:
  - tự đăng nhập trang quản trị WordPress (anh/chị gõ mật khẩu);
  - đọc bài thử trước khi đăng;
  - quyết vài việc phía website ở mục 3.1;
  - khi bài thử hiện công khai, xem tên tác giả có lộ tên đăng nhập của tài khoản phần mềm không (mục 4.1);
  - tự bấm xóa hẳn ảnh thử rồi bài thử khi dọn (ảnh trước).
- Xong buổi, Lá Chắn đọc kết quả rồi mới cho dùng Hẹn giờ / Đăng ngay.

## 1. Quy tắc trong buổi thử

1. **Không ghi bí mật** vào báo cáo, ảnh chụp, tin nhắn:
   - không mật khẩu ứng dụng (Application Password), không mật khẩu đăng nhập;
   - không tên hay nội dung file khóa Google, không email tài khoản dịch vụ;
   - mã hay link Sheet chỉ ghi **4 ký tự cuối** (như app hiện);
   - không chép **tên đăng nhập** WordPress của tài khoản phần mềm (ca 0, mục 4.1 chỉ ghi trùng/không trùng, có/không);
   - không chụp file `.env`, trang Hồ sơ có mật khẩu ứng dụng, khung «🔑 Tài khoản dịch vụ Google» ở Cài đặt → 📗 Google.
2. **Chỉ gửi bài thử chủ dự án đã đọc và đồng ý.** Bài sẽ hiện công khai (ca 4, ca 5) phải được chủ dự án duyệt nội dung ngay trước khi bấm.
3. **Chủ dự án tự đăng nhập** trang quản trị (tự gõ mật khẩu) và **tự bấm xóa hẳn** (Media → xóa vĩnh viễn ảnh thử **trước**, rồi thùng rác → xóa vĩnh viễn bài; xóa nháp trên máy).
4. **Một tab app duy nhất.** Công tắc Hẹn giờ/Đăng ngay chỉ giữ trong tab đã bật (README mục 11).
5. **Trong lúc app đang gửi, không mở bài thử trong trình soạn của trang quản trị.** Trình soạn tự lưu nháp có thể đổi «giờ sửa bài» làm sai kết quả ca 3. Xem danh sách bài thì được.
6. Mạng nhà hay công ty, không Wi-Fi công cộng.
7. Ghi giờ theo đồng hồ máy (lệnh `date` hay góc màn hình), mã bài, câu báo nguyên văn (không có bí mật) vào bảng mục 7 ngay sau mỗi ca.
8. **Dừng buổi thử ngay** (rồi theo mục 5) khi app hiện một trong các câu:
   - «KHẨN: website báo bài … đã ĐĂNG CÔNG KHAI NGAY…»;
   - «Không biết chắc lệnh … đã chạy trên website chưa…»;
   - «… không đúng như mong đợi…», «… không đúng dạng…», «… không trả về dữ liệu JSON đọc được…»;
   - hoặc khi có bài hiện công khai ngoài ca 4, ca 5.

## 2. Việc cần kiểm → ca nào kiểm

| Mã | Việc cần kiểm (nguồn) | Kiểm ở |
|---|---|---|
| (a) | Tài khoản Biên tập viên của app có quyền đăng bài `publish_posts`: trang Kết nối báo «Đăng bài: ✅» (Lá Chắn T-112 B4) | Ca 0 |
| (b) | Ghi SEO qua AI Abilities của SiteSEO có làm đổi `modified_gmt` («giờ sửa bài») không. Có đổi thì Hẹn giờ/Đăng ngay kèm «Ghi SEO» gần như luôn bị chặn (trừ khi hai lệnh rơi vào cùng một giây), cần phiếu client đọc lại giờ sửa sau lệnh SEO (Lá Chắn T-112 B4, T-115 điều kiện 4). Kết luận theo «Luật đọc (b)» ở mục 4 (Lá Chắn T-128, LC-T128-1) | Ca 2 (đối chứng) + ca 3, ca 4, ca 5 (ít nhất 3 lần gửi bật «Ghi SEO») |
| (c) | Múi giờ website «Hồ Chí Minh»; giờ hẹn hiện đúng trong trang quản trị (Lá Chắn T-112 B4) | Ca 0 + ca 2 |
| (d) | Website dùng trình soạn nào (khối hay cổ điển): khe 3 của phép so `modified_gmt` (Lá Chắn T-112 B4, T-115) | Ca 0 |
| (e) | Lịch chạy của WordPress (WP-Cron) đăng bài hẹn giờ đúng giờ: hẹn một bài 15 phút sau, xem nó tự đăng **trước** hay chỉ **sau** khi có người mở trang (Lá Chắn T-112 B4; T-128 ghi nhận N4: website có SpeedyCache) | Ca 4 |
| (f) | Câu báo trên màn hình không lộ gì lạ (không đường dẫn máy, không lời máy chủ, không địa chỉ có mật khẩu); website trả lời đúng khuôn app chờ (không hiện câu «trả lời lạ») (Lá Chắn T-112 B4) | Mọi ca |
| (g) | Hai việc còn nợ: ảnh trong bài có `srcset="…webp 1x"`, điện thoại tải đúng file đầy đủ còn GPS (Lá Chắn T-059 ghi nhận 2); tiêu đề SEO có «< 5 triệu» ghi lên hộp SiteSEO hiện đúng dấu «<» (Lá Chắn T-091 điều kiện 4) | Ca 1 |
| LC-T094-44 | Website trả header `Date` (thiếu thì app chặn hẹn giờ); tài khoản Biên tập viên hẹn giờ được qua REST; xem bài hiển thị thật (không nhúng lạ, không link lạ do theme, plugin); thử trên **Sheet bản sao** | Ca 0, ca 2, ca 4/5, ca S |
| LC-T128-2 | Bài công khai có làm lộ **tên đăng nhập** của tài khoản phần mềm không: tên tác giả trên bài, trang tác giả, `/wp-json/wp/v2/users` (Lá Chắn T-128) | Ca 0, ca 4/5 (mục 4.1) |
| T-110 đk 3 | Gửi nháp kèm ảnh: danh sách Media xem bằng cửa sổ ẩn danh không có ảnh vừa gửi; tài khoản Biên tập viên gắn được ảnh vào bài (không lỗi 403) | Ca 1 |
| T-097 đk 5 | Lệnh Google thật đầu tiên chỉ tới 2 máy chủ (`sheets.googleapis.com`, `oauth2.googleapis.com`), khuôn câu trả lời đúng như client đọc (tùy chọn) | Mục 3.4 |
| Lá Chắn T-136 B.3 | File nháp bị cất sang một bên (chương trình khác làm hỏng file): câu báo, khóa gửi trùng có đủ để người dùng không gửi trùng không (Soi Lỗi T-136 G2, SL-T136-1) | Ca R |

## 3. Chuẩn bị

### 3.1 Chủ dự án quyết trước buổi (việc phía website)

- [ ] **Sao lưu website** trước buổi thử bằng plugin sao lưu đang có (khuyến nghị; chủ dự án hay người làm web làm).
- [ ] **Plugin tự báo bài mới.** Website có plugin nào tự gửi email cho người đăng ký, tự đăng lên mạng xã hội, hay tự báo Google/Bing khi có bài mới không? Ví dụ chức năng «Instant Indexing» của SiteSEO nếu đang bật. WordPress cũng tự báo các dịch vụ cập nhật ghi ở **Cài đặt → Viết** (Update Services, mặc định Ping-O-Matic). Có thì chủ dự án quyết một trong hai:
  - tắt tạm trong buổi thử (bật lại khi dọn);
  - chấp nhận bài thử bị báo đi rồi gỡ (đường dẫn trả 404 sau khi xóa).
- [ ] **Pingback** (Lá Chắn T-128, LC-T128-3). WordPress mặc định bật ô **Cố gắng thông báo cho các blog được liên kết tới từ bài viết** (Attempt to notify any blogs linked to from the post). Khi bài thử lên công khai (ca 4, ca 5), WordPress gửi pingback tới mọi link trong bài, kể cả link nội bộ tới bài thật của website: bài thật có thể nhận bình luận «Pingback: Bài thử…» trỏ tới trang đã xóa. Chủ dự án quyết một trong hai:
  - tắt tạm ô đó ở **Cài đặt → Thảo luận** (Settings → Discussion), bật lại khi dọn;
  - chấp nhận, rồi xóa pingback khi dọn (mục 6, bước 5).
- [ ] **Nội dung bài thử** (mục 3.3): chủ dự án đồng ý cho bài đó hiện công khai vài phút ở ca 4 và ca 5.

### 3.2 Máy

- [ ] App bản mới nhất: GitHub Desktop → **Fetch origin** → **Pull origin**, rồi bấm đúp `run.bat`. Bản này phải có T-112, T-115, T-118, T-128 (ca R cần thêm T-136; nên có cả phiếu sửa SL-T136-1, T-137).
- [ ] Đồng hồ Windows bật **đặt giờ tự động**. App so giờ máy với giờ website, lệch quá 2 phút thì không hẹn giờ («Đồng hồ máy tính lệch giờ website hơn 2 phút…»).
- [ ] Chủ dự án đăng nhập trang quản trị WordPress trong trình duyệt riêng (tự gõ mật khẩu).
- [ ] Mở sẵn một cửa sổ **ẩn danh** (chưa đăng nhập) để xem như khách.

### 3.3 Bài thử

- [ ] Một bài ngắn, chữ trung tính, **không giá, không số điện thoại, không tên khách**. Tiêu đề rõ là bài thử, ví dụ «Bài thử phần mềm – sẽ gỡ sau ít phút». **Không** dùng dấu `[` `]` trong tiêu đề: màn hình xem lại sẽ có thêm dòng **Cảnh báo** (khung vàng) «Có … đoạn dạng shortcode…», không chặn nhưng làm rối kết quả.
- [ ] Bài thử **không chèn link ra website khác** (pingback, mục 3.1). Link nội bộ do bước SEO gắn thì được.
- [ ] **Một ảnh** chụp ở nơi đã công khai (xưởng, cửa hàng), là file gốc từ điện thoại **còn GPS**: ảnh qua Zalo đã mất GPS. App phải báo «📍 Ảnh có vị trí GPS». Không có ảnh còn GPS thì vẫn làm ca 1, ghi «không kiểm được GPS».
- [ ] Soạn bài qua app tới bước 5 (có tốn một ít tiền AI; chủ dự án đồng ý). Nếu đã nối Google, **mở bài thử từ một dòng của Sheet bản sao** (mục 3.4) để mỗi lần gửi kiểm luôn việc ghi trạng thái dòng.
- [ ] Bước SEO: tiêu đề SEO, mô tả SEO hợp lệ (nhãn **Nên** hay **Cảnh báo**, không **Chặn**). Ca 1 tạm đổi tiêu đề SEO có «< 5 triệu» (mục 4, ca 1), xong ca 1 đổi lại.
- [ ] Một bài thử trên máy dùng được cho mọi ca. Mỗi lần gửi lại, app tạo **thêm một bài mới** trên website (tick ô gửi lại).

### 3.4 Sheet bản sao (làm nếu đã nối Google Sheets theo README mục 14; chưa nối thì bỏ, ghi «chưa làm» ở mục 7)

- [ ] Chủ dự án mở Sheet kế hoạch thật → **Tệp → Tạo bản sao** (File → Make a copy). Đặt tên rõ, ví dụ «KeHoach – BAN SAO THU». Chia sẻ bản sao cho email tài khoản dịch vụ, quyền **Người chỉnh sửa** (không ghi email này vào báo cáo).
- [ ] App: **Cài đặt → 📗 Google** → dán link bản sao vào ô **Link Google Sheet kế hoạch** → **Lưu** → **Kiểm tra kết nối**. Phải thấy «Kết nối được Google Sheet «…». Trang tính «KeHoach»: đã có». Ghi 4 ký tự cuối mã Sheet app hiện.
- [ ] (Tùy chọn, T-097 đk 5) Ngay sau khi bấm **Kiểm tra kết nối**, mở PowerShell, chạy `Get-DnsClientCache | Where-Object Entry -like "*googleapis.com"`. Thấy `sheets.googleapis.com`, `oauth2.googleapis.com`. Tên khác có thể do trình duyệt tra, chỉ để tham khảo.
- [ ] Trang **Kế hoạch** → khung **📥 Cung cấp kế hoạch** → thẻ **Dán nội dung** → dán một bảng nhỏ có cột «Từ khóa chính» với một dòng bài thử → **🧠 Đọc kế hoạch và đề xuất cập nhật** → tick dòng đề xuất → **✅ Áp dụng thay đổi (1)**. Mở Sheet bản sao xem dòng mới có Mã bài.
- [ ] Chọn dòng đó ở ô **Chọn bài để viết** → **✍️ Viết bài** → soạn bài thử như mục 3.3.

### 3.5 Ca 0 · Kiểm nhanh trước khi gửi gì

1. App: menu **Kết nối WordPress** → **Kiểm tra kết nối**. Ghi lại:
   - «Kết nối thành công tới …»;
   - «Tài khoản: … — vai trò: editor»: chỉ ghi vai trò. Tên sau «Tài khoản:» là tên hiển thị của tài khoản phần mềm; chủ dự án xem tên này có trùng tên đăng nhập không, ghi «trùng / không trùng» vào dòng «Tác giả công khai» ở mục 7, **không chép tên** (LC-T128-2);
   - «Viết bài: ✅ · **Đăng bài: ✅** · Tải ảnh lên: ✅» → **(a)**;
   - «SiteSEO: ghi được»;
   - có câu cảnh báo quyền `unfiltered_html` không (không có là đúng; có thì `srcset` ở ca 1 có thể bị website bỏ).
2. Trang quản trị: **Cài đặt → Tổng quan → Múi giờ**: «Hồ Chí Minh» (hay UTC+7) → **(c)** phần 1.
3. Trang quản trị: mở một bài **cũ** bất kỳ (không phải bài thử) để xem trình soạn → **(d)**. Đóng bài, không lưu.
   - **Trình soạn khối:** có nút «+» thêm khối.
   - **Trình soạn cổ điển:** thanh công cụ kiểu Word, hai thẻ «Trực quan / Văn bản».

   Xem thêm **Plugin → Plugin đã cài** có «Classic Editor» không.
4. (Tùy chọn) Header `Date`: trong cửa sổ **Command Prompt** chạy `curl.exe -sI https://<tên-miền>/wp-json/` rồi tìm dòng bắt đầu bằng `date:` (gõ đủ `curl.exe`: trong PowerShell, `curl` là lệnh khác). Lệnh này chỉ đọc trang công khai, không cần đăng nhập. Không có dòng `date:` thì ca 2 sẽ bị chặn với câu «Không đọc được giờ của website (header Date thiếu hoặc sai dạng)…» → dừng, ghi kết quả, nhờ người làm web.

## 4. Các ca thử

Mỗi ca ghi vào bảng mục 7: giờ bắt đầu, mã bài app báo, câu báo nguyên văn, kết quả.

### Ca 1 · Nháp có ảnh, ghi SEO có «< 5 triệu» → (g), T-110 đk 3, (f)

Công tắc Hẹn giờ/Đăng ngay **chưa cần bật**.

1. Bước SEO: tạm đổi tiêu đề SEO thành câu có «< 5 triệu» (có dấu cách sau «<»), ví dụ «Sửa cửa cổng giá < 5 triệu có nên không». Nhãn không được **Chặn**.
2. Bước 5 · Xuất bản, hình thức **Nháp**, bật **Ghi SEO lên website**. Đọc khung «Xem lại link, địa chỉ trong bài» → **📤 Gửi nháp** → đợi kết quả.
3. Phải thấy:
   - «Đã tạo bài nháp trên WordPress (mã …)»;
   - «Đã ghi SEO vào hộp SiteSEO của bài nháp.»;
   - danh sách «Ảnh đã lên thư viện Media»;
   - không câu báo gắn ảnh lỗi (T-110 đk 3: gắn được ảnh, không 403).
4. **(g) «< 5 triệu»:** trang quản trị mở bài nháp vừa tạo (giờ được mở trình soạn, vì ca 1 đã gửi xong). Hộp SiteSEO hiện đúng «< 5 triệu». Bấm **Xem trước** (Preview): tiêu đề tab trình duyệt có «< 5 triệu». Nguồn trang (Ctrl+U) có `&lt; 5 triệu` trong thẻ `<title>`, chữ không bị cắt sau dấu «<».
5. **(g) `srcset`, GPS:**
   - Trong trình soạn, xem mã của bài (khối: menu ⋮ → trình soạn mã, Code editor; cổ điển: thẻ «Văn bản», Text). Thẻ ảnh có `srcset="…/<tên-ảnh>.webp 1x"`.
   - Nguồn trang xem trước: ảnh **trong bài** không có bản thu nhỏ `-300x…`, `-768x…`, `-800x…`. Ảnh đại diện do theme in có thể có, đã chấp nhận 27/10, chỉ ghi lại.
   - Kiểm GPS theo README mục 11 «Lần gửi thật đầu tiên»: chép địa chỉ ảnh (trong `srcset`, hay trong danh sách «Ảnh đã lên thư viện Media») → lưu về máy → chuột phải → **Properties → Details** → phần **GPS** có Latitude, Longitude.
   - Điện thoại: kiểm ở ca 4 hay ca 5, lúc bài đang công khai (mục 4.1). Xem trước bài nháp trên điện thoại thì phải đăng nhập trang quản trị trên điện thoại.
6. **T-110 đk 3, Media ẩn danh:** trong cửa sổ ẩn danh mở `https://<tên-miền>/wp-json/wp/v2/media`. Tìm (Ctrl+F) tên file ảnh vừa gửi. **Không** được có (ảnh đang gắn vào bài nháp).
7. Đổi tiêu đề SEO ở bước SEO về câu bình thường (không giá) cho các ca sau.

### Bật công tắc

8. **Cài đặt → 📅 Hẹn giờ, đăng** → tick **Tôi hiểu: bài sẽ được hẹn giờ/đăng công khai thật trên website** → bật **Bật Hẹn giờ và Đăng ngay**. Quay lại Soạn bài, cùng tab.

### Ca 2 · Hẹn giờ xa, **tắt** «Ghi SEO» → LC-T094-44 (hẹn giờ qua REST, header `Date`), (c), đối chứng cho (b)

1. Bước 5 · Xuất bản: hình thức **Hẹn giờ**.
   - Tick ô gửi lại **Tạo thêm một bài mới và hẹn giờ đăng bài mới đó**.
   - **Ngày đăng**: khoảng **30 ngày sau**; **Giờ đăng**: 08:00.
   - Tắt **Ghi SEO lên website**.
2. Xem:
   - dòng «Hẹn đăng: …» ghi đúng thứ, ngày, giờ Việt Nam;
   - có câu «Múi giờ của website là … khác giờ Việt Nam…» không. Có là (c) cần sửa phía website.
   - có câu «Không đọc được múi giờ của website…» không (website không trả múi giờ). Có thì ghi vào (c).
   - Bấm **🔄 Kiểm tra lại quyền đăng bài, múi giờ website** nếu cần.
3. Đọc màn hình «Xem lại trước khi gửi» → tick **Tôi đã đọc lại toàn bài và danh sách trên** → **📅 Gửi và hẹn giờ …**.
4. Phải thấy «Đã hẹn giờ đăng bài: …». Màn hình xem lại có dòng nhắc chép tiêu đề, mô tả vào SiteSEO trước giờ đăng: đúng, vì «Ghi SEO» đang tắt.
   - Câu «Không đọc được giờ của website (header Date …)» → header `Date` thiếu: dừng, ghi lại.
   - Câu «Bài nháp trên website đã bị sửa sau lần phần mềm ghi cuối…» khi **không** có «Ghi SEO» → có thứ khác (plugin) sửa bài: dừng, ghi lại, báo Lá Chắn.
5. Trang quản trị: **Bài viết**, lọc bài **đã lên lịch** (Scheduled) → bài vừa hẹn hiện đúng ngày, giờ đã chọn → **(c)** phần 2.
6. **Chuyển bài về nháp ngay** (chủ dự án): **Sửa nhanh** (Quick Edit) → Trạng thái **Bản nháp** (Draft) → **Cập nhật** (Update). Kiểm: bộ lọc **đã lên lịch** không còn bài thử. Có làm ca S thì làm **ca S bước 2** ngay lúc này, trước ca 3.

### Luật đọc (b) (Lá Chắn T-128, LC-T128-1)

App so «giờ sửa bài» tính tới **giây**. Một lần hẹn giờ qua có thể chỉ là may: lệnh ghi SEO và lệnh ghi trước đó của app rơi vào cùng một giây (giới hạn 1 của sổ rủi ro). Vì vậy:

- **(b) = CÓ ĐỔI** khi một lần gửi bật «Ghi SEO» (ca 3, ca 4 hay ca 5) có **cả hai** câu «Đã ghi SEO vào hộp SiteSEO của bài nháp.» và «Bài nháp trên website đã bị sửa sau lần phần mềm ghi cuối…», trong khi ca 2 đã qua và không ai mở bài.
- **(b) = KHÔNG ĐỔI** chỉ khi **ít nhất 3 lần** gửi bật «Ghi SEO» đều hẹn giờ hay đăng được: ca 3, ca 4, ca 5. Thiếu lần nào (ví dụ không làm ca 5) thì lặp ca 3, mỗi lần chuyển bài về nháp như ca 2 bước 6.
- Lần gửi bật «Ghi SEO» mà **không có** câu «Đã ghi SEO…» (lệnh ghi SEO lỗi, có câu lỗi SEO): **chưa kết luận**, không tính vào 3 lần; ghi lại câu báo. Lỗi ghi SEO lặp lại thì ghi (b) «chưa kết luận», báo Lá Chắn.
- Mục 7, dòng (b): ghi từng lần gửi bật «Ghi SEO»: ca, mã bài, hẹn giờ/đăng được hay bị chặn, có câu «Đã ghi SEO…» không.

### Ca 3 · Hẹn giờ xa, **bật** «Ghi SEO» → **(b)**, lần thứ nhất

1. Như ca 2, nhưng bật **Ghi SEO lên website**. Tick ô gửi lại; ô xác nhận bị bỏ tick vì bài đổi: tick lại.
2. **📅 Gửi và hẹn giờ …**. Đọc kết quả theo luật đọc (b):
   - **«Đã ghi SEO…» và «Đã hẹn giờ đăng bài: …»** → lần qua thứ nhất. **Chưa kết luận** (b): còn cần ca 4, ca 5 (hay ca 3 lặp) cùng qua.
   - **«Đã ghi SEO…» và «Bài nháp trên website đã bị sửa sau lần phần mềm ghi cuối…»**, mà ca 2 (không ghi SEO) đã qua và không ai mở bài → ghi SEO qua Abilities **có** đổi giờ sửa bài → **(b) = CÓ ĐỔI**.
     - Ghi lại nguyên câu. Bài vẫn là nháp.
     - **Bỏ ca 5** (Đăng ngay bắt buộc ghi SEO, nên gần như luôn bị chặn).
     - Ca 4 làm với «Ghi SEO» tắt.
     - Cần phiếu client trước khi bật công tắc.
   - Không có câu «Đã ghi SEO…»: chưa kết luận (luật đọc (b)).
3. Hẹn giờ được thì: trang quản trị kiểm hộp SiteSEO của bài có đúng tiêu đề, mô tả; rồi **chuyển về nháp** như ca 2 bước 6.

### Ca 4 · Hẹn giờ 15 phút sau → **(e)**, xem bài hiển thị thật, (b) lần thứ hai

Bài này **sẽ hiện công khai**: chủ dự án đọc lại nội dung trước khi bấm.

1. Hình thức **Hẹn giờ**, tick ô gửi lại.
   - **Ngày đăng**: hôm nay; **Giờ đăng**: khoảng 15 phút sau, làm tròn 5 phút (app đòi ít nhất 10 phút).
   - «Ghi SEO» **bật** nếu chưa có lần nào ra (b) = CÓ ĐỔI (lần gửi này tính vào luật đọc (b)); **tắt** nếu (b) = CÓ ĐỔI.
2. Tick xác nhận → **📅 Gửi và hẹn giờ …** → «Đã hẹn giờ đăng bài: …». Ghi mã bài, giờ hẹn.
   - Bị chặn vì (b) (có «Đã ghi SEO…» và «Bài nháp trên website đã bị sửa…») → **(b) = CÓ ĐỔI**: làm lại ca 4 với «Ghi SEO» tắt để vẫn kiểm được (e), bỏ ca 5.
3. Chờ tới giờ hẹn. Để biết lịch chạy có **tự** chạy không, trong lúc chờ **không đụng tới website** (Lá Chắn T-128, ghi nhận N4):
   - đóng các tab trang quản trị, nhưng không đóng cả trình duyệt để vẫn giữ đăng nhập (trang quản trị đang mở tự gửi yêu cầu lên website khoảng mỗi phút);
   - không mở trang nào của website, không thao tác trong app. Ca 5, ca S làm **sau** bước 4.

   WordPress kích lịch chạy ở cuối mỗi lần tải một trang không lấy từ cache: trang quản trị, lệnh của app, trang chưa có trong cache. Lần tải đó làm thay việc của khách thật.
4. Quá giờ hẹn 2–3 phút: chủ dự án mở trang quản trị **Bài viết**. Lần mở này còn hiện trạng thái **trước** khi chính nó kích lịch chạy. Ghi giờ xem và trạng thái bài.
   - Đã **xuất bản** (Published): bài **tự đăng** trước khi có người mở trang → **(e) = ĐẠT**.
   - Chưa (lỡ lịch, Missed schedule, hay vẫn đang lên lịch, Scheduled): đợi 1 phút, tải lại trang (F5). Lúc này mới xuất bản thì bài **chỉ đăng sau khi có người mở trang**: ghi rõ như vậy, kèm giờ; Lá Chắn xét (có thể cần lịch chạy thật của hosting). Đừng mở trang chủ để kích: website có SpeedyCache, trang lấy từ cache không chạy lịch.
   - Tải lại vài lần trong 5 phút mà vẫn chưa: **(e) = KHÔNG ĐẠT**. Lịch chạy của WordPress không chạy; người làm web phải bật lịch chạy thật của hosting trước khi dùng Hẹn giờ. Chuyển bài về nháp.
5. Nếu bài đã đăng: **xem bài hiển thị thật** (mục 4.1); có làm ca S thì làm **ca S bước 3** ngay lúc này; rồi **gỡ ngay** (mục 6, bước 1).

### Ca 5 · Đăng ngay → xem bài hiển thị thật, (b) lần thứ ba

Chỉ làm khi chưa có lần nào ra (b) = CÓ ĐỔI. Làm **sau** ca 4 (có làm ca S thì sau ca S bước 3), không làm trong lúc chờ ca 4. Bài **hiện công khai ngay** khi gửi được: chủ dự án đọc lại nội dung trước khi bấm. Bị chặn vì (b) thì bài vẫn là nháp: ghi (b) = CÓ ĐỔI.

1. Hình thức **Đăng ngay**, tick **Tạo thêm một bài mới và đăng công khai ngay bài mới đó**, bật **Ghi SEO lên website**.
   - Nếu bước SEO báo trùng bài đã đăng (vì bài ca 4 còn trên website): gỡ bài ca 4, bấm **🔄 Tải lại danh sách bài** ở bước SEO, rồi quay lại.
2. Màn hình ghi «Hiện công khai ngay khi bấm», không còn dòng **Chặn**. Tick xác nhận → **🚀 Gửi và đăng công khai ngay**.
3. Phải thấy «Đã ghi SEO vào hộp SiteSEO của bài nháp.», «Đã đăng bài công khai trên website.», «Địa chỉ bài: …». Đủ 3 lần gửi bật «Ghi SEO» đều qua (ca 3, ca 4, ca 5; thiếu thì lặp ca 3) → **(b) = KHÔNG ĐỔI**.
4. **Xem bài hiển thị thật** (mục 4.1), rồi **gỡ ngay** (mục 6, bước 1).

### 4.1 Xem bài hiển thị thật (LC-T094-44, LC-T128-2)

Mở «Địa chỉ bài» trong **cửa sổ ẩn danh**:

- [ ] Tiêu đề, các mục, đoạn văn, chữ đậm, danh sách, ảnh, chú thích hiện đúng.
- [ ] Nguồn trang (Ctrl+U), **phần thân bài**: không có `<iframe`, `<script` hay nhúng lạ. Link trong bài chỉ là các link có trong bảng «Mọi link trong bài» của màn hình xem lại.
- [ ] Ảnh trong bài có `srcset="…webp 1x"`.
- [ ] Thẻ `<title>` và `<meta name="description">` đúng chữ SEO đã ghi (khi bật «Ghi SEO»).
- [ ] Phần do theme, plugin thêm (nút chia sẻ, bài liên quan, quảng cáo…): **ghi lại** để Lá Chắn biết. Không phải lỗi của app.
- [ ] **Tác giả** (LC-T128-2), vẫn trong cửa sổ ẩn danh:
  - tên tác giả hiện trên bài;
  - bấm vào tên đó: trang tác giả, địa chỉ dạng `https://<tên-miền>/author/…/`;
  - mở `https://<tên-miền>/wp-json/wp/v2/users`.

  Chủ dự án xem có chỗ nào hiện **tên đăng nhập** của tài khoản phần mềm không. Ghi có/không vào dòng «Tác giả công khai» ở mục 7, **không chép tên**.
- [ ] **Điện thoại** ((g)-1, ghi nhận N5): mở «Địa chỉ bài» trên điện thoại (không cần đăng nhập), tải ảnh trong bài về điện thoại, xem thông tin ảnh có vị trí (GPS) không. Ghi vào (g)-1.

### Ca S · Dòng kế hoạch trên Sheet bản sao (làm nếu đã làm mục 3.4)

Luật của app: trạng thái dòng **chỉ đi tới** (Chưa viết → Đang viết → Đã gửi nháp → Đã hẹn giờ → Đã đăng), **không bao giờ lùi**. Dòng đã ở bước sau thì app báo «Dòng … trên Google Sheet đã ở bước sau nên không đổi trạng thái.» và không ghi.

1. **Sau mỗi lần gửi** ở ca 1–5, mở Sheet bản sao. Ghi vào mục 7 ô **Trạng thái**, **Mã bài WordPress** của dòng bài thử, và câu báo về dòng kế hoạch nếu app hiện.
   - Chờ đúng: ca 1 «Đã gửi nháp»; ca 2, ca 3, ca 4 «Đã hẹn giờ»; ca 5 «Đã đăng». Mã bài WordPress là mã của lần gửi đó.
   - Ca 3 bị chặn ((b) = CÓ ĐỔI): dòng giữ «Đã hẹn giờ» của ca 2 (không lùi về «Đã gửi nháp»), app báo «… đã ở bước sau nên không đổi trạng thái.».
2. **Bài hẹn giờ đã chuyển về nháp** (ca 2 bước 6, trước ca 3): trang **Kế hoạch** → **🌐 Cập nhật trạng thái từ website**. Phải có cảnh báo «Bài #… (dòng …) đang là … trên website trong khi Google Sheet ghi «Đã hẹn giờ». Phần mềm không tự sửa Google Sheet.». Không có dòng nào để ghi (đúng luật không lùi).
3. **Đường ghi đi tới** (ca 4, sau khi bài tự đăng, **trước** ca 5): **🌐 Cập nhật trạng thái từ website** → khung **🌐 Thay đổi trạng thái từ website** nêu «Bài #… đã đăng trên website …» → tick dòng đó → **✍️ Ghi 1 thay đổi vào Google Sheet** → Sheet bản sao đổi ô Trạng thái thành «Đã đăng», có Ngày đăng thực tế, Cập nhật lúc.
4. **Lỡ lịch** (ca 4 quá giờ hẹn 15 phút mà chưa lên): **🌐 Cập nhật trạng thái từ website** ra cảnh báo «Lỡ lịch: bài #… (dòng …) hẹn giờ lúc … đã quá giờ mà chưa lên…». Ghi thêm vào (e).
5. **Sau khi dọn** (mục 6, bước 1–4), trước khi đổi về Sheet thật: **🌐 Cập nhật trạng thái từ website** ra «Không thấy bài #… (dòng …) trên website: bài đã bị xóa, đang trong thùng rác…» cho các bài thử. Đây là cách kiểm nhanh đã dọn đủ.

### Ca R · File nháp bị cất rồi thử gửi lại → Lá Chắn T-136 B.3, Soi Lỗi SL-T136-1

Chỉ làm khi app đã có T-136. Kiểm: Chỉ Huy chạy `Test-Path seo_app\storage\sqlite_file.py` trong PowerShell ở thư mục dự án (thư mục có `run.bat` chủ dự án bấm), phải ra `True`. Chưa có thì bỏ ca, ghi «chưa làm» ở mục 7. **Nên làm sau khi phiếu sửa SL-T136-1 đã gộp** (để kiểm lời nhắc mới); làm trước thì kỳ vọng như dưới (hành vi hiện tại, đã biết).

Làm **sau ca 5** (bỏ ca 5 thì sau ca 4; có làm ca S thì sau ca S bước 3), trước mục 6. Cần bài thử trên máy đã gửi ít nhất một lần. **Ca này không bật công tắc Hẹn giờ/Đăng ngay và không gửi gì lên website** (phần gửi trùng Soi Lỗi đã thử bằng WordPress giả). Khoảng 20 phút, tắt mở app hai lần.

Tình huống: một chương trình khác (đồng bộ đám mây, diệt virus, ổ đĩa lỗi) làm hỏng file nháp trong lúc app chạy. App cất file hỏng sang một bên (đổi tên thành `drafts.hong-<ngày>-<giờ>.sqlite`, cùng thư mục) rồi bắt đầu file nháp mới. Dấu «đã gửi» của các bài nằm trong file cũ. Ca này xem app nhắc gì để người dùng không gửi trùng.

File nháp thật của chủ dự án (`drafts.sqlite` trong thư mục `data` của dự án) được chép dự phòng ở bước 1 và trả lại ở bước 8. Các lệnh do Chỉ Huy chạy trong **PowerShell**, ở thư mục dự án. Câu lỗi của lệnh có thể in đường dẫn trong máy: **không chép** câu đó vào báo cáo.

- **Từ bước 3 tới hết bước 8, không soạn hay sửa bài thật**: nháp tạo trong lúc này nằm ở file sẽ đổi tên ở bước 8 và bị xóa ở bước dọn.
- **Ảnh chụp màn hình chỉ giữ trong máy**, không đưa vào repo, không gửi đi (có tên bài, từ khóa).

1. **Chép dự phòng.** Tắt app: đóng cửa sổ dòng lệnh (màu đen) mà `run.bat` mở. Chỉ Huy chạy:

   ```powershell
   $ErrorActionPreference = 'Stop'; if (Test-Path data\drafts.ban-sao-ca-R.sqlite) { 'DUNG: da co ban sao tu lan truoc (khong chep de len)' } elseif (Test-Path data\drafts.sau-ca-R.sqlite) { 'DUNG: con file drafts.sau-ca-R.sqlite tu lan truoc' } elseif (Get-ChildItem data -Filter 'drafts.sqlite-*') { 'DUNG: con file nhat ky drafts.sqlite-...' } else { Copy-Item data\drafts.sqlite data\drafts.ban-sao-ca-R.sqlite; 'ban sao giong file goc: ' + ((Get-FileHash data\drafts.sqlite).Hash -eq (Get-FileHash data\drafts.ban-sao-ca-R.sqlite).Hash) }
   ```

   Phải thấy `ban sao giong file goc: True`. Ra `DUNG…` hay câu lỗi: bỏ ca, ghi «chưa làm», báo Soi Lỗi. `DUNG: da co ban sao…` hay `DUNG: con file drafts.sau-ca-R…` nghĩa là lần làm trước chưa dọn: **không xóa hay đổi tên file nào để chạy lại** (bản sao cũ có thể là bản tốt duy nhất), hỏi Soi Lỗi trước.

2. **Khóa gửi lúc bình thường.** Bấm đúp `run.bat`, chủ dự án đăng nhập app. **Không bật công tắc Hẹn giờ/Đăng ngay.**
   - Trang **Bài viết**, cột **Đã gửi WordPress**: có bài thử.
   - **Soạn bài**: ghi số trong **📂 Bài đang soạn dở (…)** vào mục 7. **Mở** bài thử → **5 · Xuất bản**, hình thức **Nháp**.

   Phải thấy: «Bài này đã gửi … (bài … mã …)», ô **Tạo thêm một bài nháp mới** chưa tick, nút **📤 Gửi nháp** mờ. Ghi mã bài.

3. **Làm hỏng file nháp** (giả chương trình khác). Để yên tab app, không bấm gì. Chỉ Huy chạy:

   ```powershell
   $ErrorActionPreference = 'Stop'; $f = (Resolve-Path data\drafts.sqlite).Path; $s = [IO.File]::Open($f, 'Open', 'ReadWrite', 'ReadWrite'); try { $h = New-Object byte[] 20; [void]$s.Read($h, 0, 20); if ([Text.Encoding]::ASCII.GetString($h, 0, 15) -ne 'SQLite format 3' -or $h[18] -gt 2) { 'DUNG: khong sua gi (dau file khong nhu cho)' } else { $s.Position = 18; $s.WriteByte(3); "da sua byte 18: $($h[18]) -> 3" } } finally { $s.Close() }
   ```

   Phải thấy `da sua byte 18: 1 -> 3` (hay `2 -> 3`). Lệnh chỉ đổi 1 byte ở đầu file (số «phiên bản ghi» của SQLite); đầu file khác dự đoán thì không sửa gì. Bản gốc nằm ở bản dự phòng.

4. **App cất file.** Trong tab app, bấm menu **Bài viết**.

   Phải thấy ở cột **Đã gửi WordPress**:
   - khung vàng «File nháp cũ bị hỏng nên đã được cất sang một bên (tên «drafts.hong-…sqlite», cùng thư mục)… trước khi gửi lại một bài, hãy xem trên WordPress bài đó đã có chưa để khỏi gửi trùng.» Ghi tên file vào mục 7, chụp màn hình (giữ trong máy);
   - dòng «Chưa có bài nào phần mềm đã gửi lên WordPress.» (đã nối Sheet bản sao thì cột này có thể vẫn hiện bài thử, lấy từ cột Mã bài WordPress của Sheet: ghi lại). **Đã có phiếu sửa SL-T136-1:** dòng này phải là lời nhắc «file nháp đã cất», không phải «Chưa có bài nào…» trơn.

   Bấm menu **Bài viết** lần nữa. Phải thấy (hành vi hiện tại): khung vàng **mất** (câu chỉ hiện một lần), dòng «Chưa có bài nào…» vẫn còn. **Đã có phiếu sửa:** lời nhắc vẫn còn.

5. **Tab đang mở bài thử.** Bấm menu **Soạn bài** (trang đang ở bước khác thì bấm **5 · Xuất bản**, hình thức **Nháp**).

   Phải thấy:
   - nội dung bài thử còn nguyên;
   - khung vàng «**Nháp của bài này không còn trong kho nháp**… Tab này biết bài đã gửi (hoặc gửi dở) lên website: lưu lại thì nháp vẫn nhớ việc đó, nút gửi vẫn khóa như trước.», nút **💾 Lưu lại thành nháp**, **🗑️ Bỏ bài này**;
   - vẫn «Bài này đã gửi … (bài … mã …)», ô **Tạo thêm một bài nháp mới** chưa tick, nút **📤 Gửi nháp** mờ;
   - trang Soạn bài **không** có câu «File nháp cũ bị hỏng…» (câu đó chỉ hiện ở trang đã cất file). Có thì ghi lại.

   **Không** chọn hình thức Hẹn giờ hay Đăng ngay, **không** tick «Tạo thêm…», không bấm gửi.

6. **Tab mới chưa biết bài đã gửi** (chỉ xem). Mở thêm một tab trình duyệt tới địa chỉ app, chủ dự án đăng nhập.

   Phải thấy (hành vi hiện tại):
   - **Bài viết**: không có khung vàng; cột **Đã gửi WordPress** ghi «Chưa có bài nào…» (hay chỉ bài theo Sheet);
   - **Soạn bài**: không có câu nhắc nào; khung **📂 Bài đang soạn dở** không hiện (mọi nháp, kể cả bài thử, nằm trong file đã cất).

   Đây là chỗ người dùng có thể nghĩ bài bị mất, viết lại rồi gửi trùng mà app không còn nhắc gì (Soi Lỗi SL-T136-1). **Đã có phiếu sửa:** cả hai trang phải có lời nhắc, nút gửi của bài chưa có dấu «đã gửi» phải đòi tick «đã kiểm trên WordPress». Không viết lại, không gửi. Đóng tab này.

7. **Lưu lại nháp rồi mở lại.** Về tab đầu, **Soạn bài** → **💾 Lưu lại thành nháp**.

   Phải thấy «Đã lưu lại nháp», khung vàng mất, nút gửi vẫn mờ.

   Tải lại trang (F5), chủ dự án đăng nhập. Phải thấy:
   - **Bài viết**, cột **Đã gửi WordPress**: có lại bài thử;
   - **Soạn bài** → **📂 Bài đang soạn dở** có bài thử → **Mở** → **5 · Xuất bản**: vẫn «Bài này đã gửi … (bài … mã …)», ô **Tạo thêm…** chưa tick, nút mờ.

8. **Trả file nháp thật.** Tắt app (đóng cửa sổ dòng lệnh của `run.bat`). Chỉ Huy chạy:

   ```powershell
   $ErrorActionPreference = 'Stop'; if (Get-ChildItem data -Filter 'drafts.sqlite-*') { 'DUNG: con file nhat ky drafts.sqlite-...' } else { Rename-Item data\drafts.sqlite drafts.sau-ca-R.sqlite; Copy-Item data\drafts.ban-sao-ca-R.sqlite data\drafts.sqlite; 'da tra file cu, giong ban sao: ' + ((Get-FileHash data\drafts.sqlite).Hash -eq (Get-FileHash data\drafts.ban-sao-ca-R.sqlite).Hash) }
   ```

   Phải thấy `da tra file cu, giong ban sao: True`. Bấm đúp `run.bat`, chủ dự án đăng nhập: **📂 Bài đang soạn dở** đúng số bài ghi ở bước 2; bài thử mở ra vẫn khóa như bước 2. Ra `DUNG…` hay câu lỗi: không chạy lại lệnh, không xóa file nào, báo Soi Lỗi (bản dự phòng `drafts.ban-sao-ca-R.sqlite` vẫn còn).

### Suốt buổi · (f)

- [ ] Mọi câu báo là câu tiếng Việt cố định, kèm mã bài. Không có đường dẫn máy, tên file khóa, địa chỉ có mật khẩu, chữ tiếng Anh của máy chủ.
- [ ] Không câu nào thuộc nhóm «trả lời lạ» ở mục 1, quy tắc 8.

## 5. Khi gặp sự cố trong buổi

1. **Dừng**, không bấm gửi lại.
2. Làm theo README mục 11, «**Kiểm bài trên trang quản trị WordPress**»: mở bài theo dòng «Sửa bài trong trang quản trị: …», xem trạng thái thật.
3. Bài lỡ hiện công khai ngoài ý muốn: chủ dự án **chuyển về Bản nháp** (hay bỏ vào thùng rác) ngay, rồi xóa cache (mục 6, bước 1).
4. Ghi vào bảng mục 7: giờ, câu báo nguyên văn (không bí mật), mã bài, việc đã làm. Báo Chỉ Huy, Lá Chắn. Chưa dùng Hẹn giờ/Đăng ngay cho tới khi Lá Chắn xem.

## 6. Dọn sau buổi thử (đánh dấu từng dòng)

1. [ ] **Bài đã hiện công khai** (ca 4, ca 5): chủ dự án bỏ vào **thùng rác** ngay sau khi xem; rồi **xóa cache** của website (plugin cache đang dùng, ví dụ SpeedyCache → xóa cache) để trang bài không còn được phục vụ từ cache. Mở lại địa chỉ bài bằng cửa sổ ẩn danh: phải ra trang không tìm thấy.
2. [ ] **Bài viết, bộ lọc đã lên lịch (Scheduled): không còn bài thử nào** (bài hẹn giờ 30 ngày sau mà quên thì sẽ tự đăng).
3. [ ] **Media → Thư viện: xóa ảnh thử trước khi xóa hẳn bài** (LC-T128-3). Chọn dạng danh sách (List view). Ảnh thử là ảnh có cột **Đã tải lên** (Uploaded to) là tên bài thử, khớp tên file ghi ở dòng «Ảnh thử» của mục 7 → chủ dự án **xóa vĩnh viễn** (Delete Permanently). App không tự xóa ảnh.
   - Vì sao trước: xóa hẳn bài thì ảnh của bài thành ảnh «không gắn», hiện trong danh sách ảnh công khai (`/wp-json/wp/v2/media`). Cột «Đã tải lên» cũng mất tên bài, nên dễ xóa nhầm ảnh thật hay sót ảnh thử.
4. [ ] **Bài viết**: mọi bài thử (ghi mã ở mục 7: các bản nháp, và bài ca 4, ca 5 đã bỏ vào thùng rác ở bước 1) → thùng rác (Trash) → chủ dự án **xóa vĩnh viễn** (Delete Permanently).
5. [ ] **Bình luận** (Comments), nếu bài ca 4, ca 5 đã lên công khai mà ô pingback không tắt (mục 3.1): ô lọc loại bình luận chọn **Pings** → pingback có tên bài thử (nằm ở bài thật được link tới) → chủ dự án bỏ vào thùng rác rồi xóa vĩnh viễn. Không có thì ghi «không có».
6. [ ] Bật lại những gì đã tắt tạm ở mục 3.1 (plugin, ô thông báo pingback), nếu có.
7. [ ] App: tải lại trang (F5) hay tắt app để **tắt công tắc**. Mở lại **Cài đặt → 📅 Hẹn giờ, đăng**: «đang **tắt**».
8. [ ] Nếu đã dùng Sheet bản sao:
   - **Cài đặt → 📗 Google** → dán lại link Sheet **thật** → **Lưu** → **Kiểm tra kết nối** (thấy đúng tên Sheet thật);
   - chủ dự án xóa bản sao, hoặc bỏ chia sẻ bản sao với email tài khoản dịch vụ.
9. [ ] App, Soạn bài, khung **Bài đang soạn dở**: bài thử trên máy → **🗑️ Xóa** → **Xóa hẳn** (chủ dự án bấm). Làm **sau** bước 8, để không còn nháp gắn với Sheet bản sao.
10. [ ] Bước SEO của một bài bất kỳ: **🔄 Tải lại danh sách bài**, để danh sách bài đã đăng trên máy không còn bài thử.
11. [ ] Ảnh chụp màn hình của buổi thử: soát lại không có bí mật (mục 1); lưu ngoài thư mục dự án, không đưa lên GitHub.
12. [ ] **Ca R** (nếu đã làm), chỉ khi ca R bước 8 đã ra `True` và kiểm đủ nháp: chủ dự án xóa ba file thử trong thư mục `data` của dự án: `drafts.ban-sao-ca-R.sqlite`, `drafts.sau-ca-R.sqlite` và file `drafts.hong-<ngày>-<giờ>.sqlite` đúng tên ghi ở mục 7. **Không xóa `drafts.sqlite`.** Ba file này chứa nháp của chủ dự án: không gửi đi. Chưa chắc thì để lại, app không đọc các file này.

## 7. Bảng ghi kết quả (cho Lá Chắn)

Chỉ Huy điền ngay trong buổi. Sau buổi, chép bảng vào báo cáo buổi thử (`docs/team/reports/`, phiếu do Chỉ Huy lập) cùng các ca đã bỏ và lý do.

| Mã | Kiểm gì | Kết quả (Đạt / Không đạt / Chưa làm) | Ghi chú: giờ, mã bài, câu báo nguyên văn (không bí mật) |
|---|---|---|---|
| (a) | «Đăng bài: ✅» ở Kết nối WordPress | | |
| (b) | Ca 2 (không ghi SEO) hẹn giờ được. Từng lần gửi bật «Ghi SEO» (ca 3, ca 4, ca 5, ca 3 lặp): mã bài, hẹn giờ/đăng được hay bị chặn, có «Đã ghi SEO…» không. Kết luận theo luật đọc (b): KHÔNG ĐỔI (≥ 3 lần qua) / CÓ ĐỔI / chưa kết luận | | |
| (c) | Múi giờ «Hồ Chí Minh»; giờ hẹn trong trang quản trị đúng giờ đã chọn; có/không câu cảnh báo múi giờ | | |
| (d) | Trình soạn: khối / cổ điển; có plugin Classic Editor không | | |
| (e) | Bài hẹn 15 phút: giờ hẹn; giờ xem lần đầu và trạng thái lúc đó; tự đăng **trước** khi có người mở trang, hay chỉ **sau** (giờ thấy đã đăng); có «Lỡ lịch» không | | |
| (f) | Câu báo sạch; không câu «trả lời lạ» | | |
| (g)-1 | `srcset="…webp 1x"` trong nội dung đã lưu; không bản thu nhỏ trong bài; ảnh tải về còn GPS (máy tính ở ca 1; điện thoại ở ca 4/5, lúc bài công khai) | | |
| (g)-2 | «< 5 triệu» trong hộp SiteSEO, tiêu đề tab, `&lt;` trong `<title>` | | |
| Header `Date` | Có (ca 0 hay ca 2 không bị chặn vì `Date`) | | |
| REST hẹn giờ | Tài khoản Biên tập viên hẹn giờ được (ca 2) | | |
| Bài hiển thị thật | Mục 4.1: không nhúng lạ, không link lạ; phần theme/plugin thêm (ghi rõ) | | |
| Tác giả công khai | Ca 0: tên sau «Tài khoản:» trùng / không trùng tên đăng nhập. Mục 4.1: tên tác giả trên bài, trang tác giả, `/wp-json/wp/v2/users` có / không hiện tên đăng nhập. Không chép tên (LC-T128-2) | | |
| Ảnh thử | Tên file ảnh của từng ca (để dọn ở mục 6 bước 3) | | |
| T-110 đk 3 | Ảnh của bài nháp không có trong `/wp-json/wp/v2/media` khi xem ẩn danh; gắn ảnh không lỗi | | |
| Sheet bản sao | Mục 3.4, ca S: kết nối bản sao, dòng ghi đúng trạng thái, cập nhật từ website ghi đúng ô | | |
| T-097 đk 5 | (tùy chọn) Tên máy chủ Google thấy được | | |
| Ca R | File nháp bị cất rồi thử gửi lại (Lá Chắn T-136 B.3, Soi Lỗi SL-T136-1). Bước 1: `True`. Bước 4: câu «File nháp cũ bị hỏng…» hiện ở đâu, mất sau mấy lần bấm, tên file `drafts.hong-…`; dòng «Chưa có bài nào…» hay lời nhắc. Bước 5: còn nội dung; khung «Tab này biết bài đã gửi…»; nút gửi mờ; có/không câu «File nháp cũ…» trên Soạn bài. Bước 6: tab mới thấy/không thấy bài thử, có/không câu nhắc. Bước 7: lưu lại, F5 vẫn khóa. Bước 8: `True`, số bài như bước 2. Không bật công tắc, không gửi gì | | |
| Dọn | Mục 6, đủ 12 dòng (ảnh xóa trước bài; pingback có / không, đã xóa) | | |
| `unfiltered_html` | Có/không câu cảnh báo ở Kết nối WordPress | | |

## 8. Sau buổi thử

- **Lá Chắn** đọc bảng mục 7, kết luận có cho dùng Hẹn giờ / Đăng ngay không. Các ô «Không đạt» hay «Chưa làm» do Lá Chắn xét.
  - Theo biên bản T-112: (b) = CÓ ĐỔI thì cần phiếu client (Thợ Máy) đọc lại giờ sửa sau lệnh ghi SEO trước khi dùng. Lần đọc lại đó nhận luôn mọi lần sửa của người khác trong lúc lệnh SEO đang chạy, tức khe 2 của sổ rủi ro rộng thêm đúng bằng thời gian lệnh SEO. Phiếu đó phải sửa lại dòng khe 2 (`docs/team/security.md` mục 6) hay chọn cách khác; Lá Chắn xét lại (Lá Chắn T-128 mục 1).
  - (e) «chỉ đăng sau khi có người mở trang»: Lá Chắn xét có cần lịch chạy thật của hosting không (ghi nhận N4).
- **Chủ dự án quyết trước khi dùng thật** (LC-T128-2), nhất là khi dòng «Tác giả công khai» ghi «trùng» hay «có»:
  - đặt **Biệt danh** (Nickname) và **Tên hiển thị công khai** (Display name publicly as) của tài khoản phần mềm, ví dụ «Pro-Metal»: trang quản trị **Người dùng → Tất cả người dùng** (Users → All Users) → tài khoản phần mềm;
  - đặt mật khẩu **đăng nhập** của tài khoản này dài, ngẫu nhiên (app chỉ dùng mật khẩu ứng dụng, không dùng mật khẩu này);
  - địa chỉ trang tác giả (`/author/…/`) vẫn là tên đăng nhập. Muốn giấu luôn thì dùng chức năng chặn liệt kê người dùng của plugin bảo mật (bản sao website trong máy có Loginizer; website hiện nay có thể khác), hoặc đổi tác giả của bài.

  Lá Chắn xét theo kết quả buổi thử.
- **Thư Ký** đọc lại README mục 11 theo kết quả thật: chữ trên màn hình xác nhận, câu kết quả, luật Hẹn giờ khi SEO lỗi, đường Abilities.
- **Chỉ Huy** cập nhật bảng việc, `docs/team/dong-bo.md`, bảng tiến độ cho chủ dự án.
- **Công tắc chỉ bật để dùng thật** khi có **cả hai**: Lá Chắn đồng ý kết quả buổi thử này, **và** Lá Chắn đã rà soát Giai đoạn 5 (LC-T094-41, ghi nhận N3). Sau đó, mỗi lần muốn Hẹn giờ / Đăng ngay, chủ dự án tự bật công tắc ở **Cài đặt → 📅 Hẹn giờ, đăng**. Công tắc chỉ giữ trong tab đó, trong lần mở app đó.

# Kịch bản buổi thử thật Google Search Console (Giai đoạn 6)

| Mục | Nội dung |
|---|---|
| Phiếu | T-133 (`docs/team/tickets/T-133-kich-ban-thu-that-google.md`) |
| Soạn | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 · 2026-11-07; lượt 2 ngày 2026-11-10 (trong T-126 lượt cuối): thêm ca 6b theo Lá Chắn T-127 B.1, sửa đoạn lệnh ca 7 theo Lá Chắn T-133 G1 |
| Dùng cho | **Chỉ Huy** làm từng bước; **chủ dự án ngồi cùng**, tự đăng nhập Google (Search Console, Google Cloud) và tự làm việc cần quyền chủ sở hữu. **Lá Chắn** đọc kịch bản (nhất là đoạn lệnh ở ca 7) trước buổi, đọc bảng kết quả (mục 7) sau buổi |
| Khi nào | Khi T-125 (trang «📈 Theo dõi», khung Search Console trong Cài đặt) và T-127 (nút «Đưa vào kế hoạch») đã gộp `main`, và chủ dự án báo rảnh. Khoảng 45–60 phút. Buổi thử **chỉ đọc** với Search Console và website: không đăng bài, không sửa gì trên Search Console hay website. Chỉ ca 6b ghi một dòng kế hoạch lên Google Sheet, khi chủ dự án bấm «Áp dụng» |
| Tên nút | Theo `main` `7153f0a` (đã gộp T-125): `app/views/tracking.py`, `app/views/settings.py`. Ca 6b theo nhánh `team/T-127` (`08b24df`, chưa gộp `main` khi soạn): `app/views/tracking.py`, `app/views/plan.py`. Gộp xong mà khác thì theo giao diện. Nhãn của Search Console theo trang trợ giúp tiếng Việt của Google; chỗ chưa chắc ghi «(tên theo giao diện khi gộp)» hay «(tên theo giao diện Search Console)» |
| Nguồn | Thiết kế T-120 (`T-120-tho-may.md` mục 1.2, 2.7; mục 6 «Đi kèm» dòng «Thử thật»; mục «Rủi ro và điểm cần chú ý»), Lá Chắn T-121 (điều kiện B4), Lá Chắn T-124 (điều kiện B.3), Lá Chắn T-127 (điều kiện B.1), Lá Chắn T-133 (ghi nhận G1), README mục 14, mục 15, kịch bản mẫu T-128 |

## 0. Tóm tắt (cho chủ dự án)

- Trang **📈 Theo dõi** cho xem mỗi bài được Google hiển thị bao nhiêu lần, được bấm bao nhiêu lần, đứng vị trí trung bình nào, khách tìm bằng từ khóa gì. Số liệu lấy từ Google Search Console, **chỉ đọc**.
- Trước khi dùng thật, cần một buổi thử với Search Console thật của website, anh/chị ngồi cùng. Buổi thử không đăng bài, không sửa gì trên Search Console hay website. Chỉ có một việc ghi: thêm một dòng kế hoạch vào Google Sheet từ từ khóa anh/chị chọn (ca 6b), và chỉ khi anh/chị bấm «Áp dụng».
- Việc của anh/chị:
  - trước buổi: làm README mục 15 bước 1–3 (bật «Google Search Console API», thêm email tài khoản dịch vụ với quyền «Hạn chế»), nếu chưa làm;
  - trong buổi: tự đăng nhập Search Console; mở bảng «Trang» để so số với phần mềm; cuối buổi xem lại «Người dùng và quyền».
- Xong buổi, Lá Chắn đọc kết quả rồi mới cho dùng trang 📈 Theo dõi.

## 1. Quy tắc trong buổi thử

1. **Không ghi bí mật** vào báo cáo, ảnh chụp, tin nhắn:
   - không tên, đường dẫn, nội dung file khóa Google;
   - không email tài khoản dịch vụ: Cài đặt hiện email này ở khung «🔑 Tài khoản dịch vụ Google (file khóa)» và trong kết quả «🔎 Tìm thuộc tính»;
   - không mã project Google Cloud;
   - mã hay link Google Sheet kế hoạch (ca 6b) chỉ ghi **4 ký tự cuối** (như app hiện);
   - thuộc tính Search Console chỉ ghi **loại** (tiền tố hay tên miền), không ghi đầy đủ. Tên máy ngoài website (bảng của «Kiểm tra») chỉ ghi dạng: `www.`, bản thử (staging), «địa chỉ http:// hoặc lạ»;
   - không chụp: file `.env`, khung 🔑, bảng kết quả «Tìm thuộc tính», trang tài khoản dịch vụ và khóa trong Google Cloud;
   - tên bài, từ khóa là chữ công khai nhưng không cần chép: bảng kết quả ghi số và khớp / không khớp.
2. **Chỉ đọc.** Không bấm gì làm thay đổi Search Console: không gửi sơ đồ trang web, không yêu cầu lập chỉ mục, không xóa URL. Không đổi cài đặt Google Cloud. Hai ngoại lệ: chủ dự án làm README mục 15 nếu chưa làm; ca 6b ghi một dòng kế hoạch lên Google Sheet khi chủ dự án bấm «Áp dụng».
3. **Gặp lỗi 403: không nâng quyền.** Không đổi sang «Toàn quyền», không thêm làm chủ sở hữu, không cấp vai trò (role) nào trong Google Cloud. Dừng, ghi câu báo nguyên văn, hỏi chủ dự án và Lá Chắn (mục 5).
4. **Chủ dự án tự đăng nhập** Search Console và Google Cloud (tự gõ mật khẩu).
5. **Một tab app** (trừ bước tùy chọn ở ca 3).
6. Mạng nhà hay công ty, không Wi-Fi công cộng.
7. Ghi giờ theo đồng hồ máy. Ngày trong phần mềm và trong Search Console là **ngày theo giờ Google** (giờ Thái Bình Dương của Mỹ, chậm hơn giờ Việt Nam 14–15 tiếng).
8. **Dừng buổi thử ngay** (rồi theo mục 5) khi:
   - app hiện một trong các câu: «Lệnh gọi Search Console này không nằm trong danh sách được phép…», «Tài khoản dịch vụ chưa được mở đúng quyền chỉ đọc Search Console…», «Search Console trả lời bằng một lệnh chuyển hướng…», «Lỗi chứng chỉ bảo mật (SSL)…», «Search Console trả về dữ liệu không đúng dạng…», «Search Console trả về nhiều dòng không đúng dạng hoặc lặp lại…»;
   - hay thấy Search Console có thay đổi: người dùng mới, quyền bị đổi, sơ đồ trang web mới.

## 2. Việc cần kiểm → ca nào kiểm

| Mã | Việc cần kiểm (nguồn) | Kiểm ở |
|---|---|---|
| (1) | Chủ dự án làm hai việc phía Google: bật API, thêm email tài khoản dịch vụ quyền «Hạn chế» (T-120 «Thử thật» bước 1; README mục 15) | Mục 3.1, ca 0 |
| (2) | «Tìm thuộc tính» thấy đúng thuộc tính, quyền «Hạn chế»; «Kiểm tra» báo ngày có số liệu, phần ngoài website (staging) không tính (T-120 bước 2). Tài khoản dịch vụ quyền «Hạn chế» đọc được danh sách thuộc tính (`sites`) và số liệu (`query`) (Lá Chắn T-121 B4 (a)) | Ca 1, ca 2 |
| (3) | Lấy số liệu; so 2 bài với Search Console (Hiệu suất → bảng «Trang», 28 ngày): click, hiển thị phải khớp, vị trí lệch ≤ 0,1 (T-120 bước 3; rủi ro «vị trí trung bình theo lượt hiển thị») | Ca 3, ca 5 |
| (4) | `metadata` (ngày số tạm) thật của đoạn mới nhất và một đoạn cũ; tên trường (T-120 bước 4; Lá Chắn T-121 B4 (b); Lá Chắn T-124 B.3) | Ca 7 |
| (5) | Bấm lại ngay thì bị chặn (T-120 bước 5) | Ca 4 |
| (6) | Search Console → Người dùng và quyền: không có gì thay đổi (T-120 bước 6) | Ca 0, ca 8 |
| (7) | Dòng bị bỏ (`dropped`) của Q1 (ngày × trang) và Q2 (từ khóa) với website thật; cỡ câu trả lời (Lá Chắn T-121 B4 (d); Lá Chắn T-124 B.3) | Ca 3, ca 7 |
| (8) | Số lệnh của lần bấm đầu ≤ 20 (Lá Chắn T-124 B.3) | Ca 3 |
| (9) | Mã lý do 403 khi chưa bật API, khi hết hạn mức (Lá Chắn T-121 B4 (c)) | Mục 3.1 (nếu API chưa bật); mọi ca (nếu gặp) |
| (10) | Từ khóa của một bài khớp Search Console (phiếu T-133) | Ca 6 |
| (11) | «➕ Đưa vào kế hoạch» với từ khóa thật: ô chọn chỉ có từ khóa sạch, câu đếm từ khóa bị để ngoài; đề xuất «Thêm» nguồn «Search Console» ở trang Kế hoạch, cảnh báo trùng; **chỉ** sau «Áp dụng» mới có dòng mới trên Sheet, kiểm trực tiếp trên Sheet (Lá Chắn T-127 B.1) | Ca 6b |

## 3. Chuẩn bị

### 3.1 Chủ dự án làm trước buổi (phía Google)

- [ ] Đã có tài khoản dịch vụ và file khóa, đã khai báo trong `.env`: README mục 14, các phần «Tạo tài khoản dịch vụ», «Cất file khóa» và bước 1–2 của «Khai báo trong app». Ca 6b cần thêm Google Sheet kế hoạch đã nối (README mục 14, phần «Khai báo trong app»); chưa nối thì bỏ ca 6b.
- [ ] README mục 15 bước 1–3:
  - bật **Google Search Console API** trong đúng project của tài khoản dịch vụ;
  - thêm email tài khoản dịch vụ vào thuộc tính của **website chính**, quyền **Hạn chế**. Không thêm vào thuộc tính bản thử (staging).
- [ ] (Tùy chọn, Lá Chắn T-121 B4 (c)) Tới buổi thử mà **chưa bật API** thì:
  1. làm ca 1 bước 1 **trước khi bật**. Đúng thiết kế thì ra câu «Chưa bật Google Search Console API trong Google Cloud (mã 403)…». Ra câu 403 khác thì ghi nguyên văn: Google dùng mã lý do khác với code chờ;
  2. chủ dự án bật API, đợi vài phút, làm lại ca 1.

  API đã bật thì bỏ bước này, **không tắt API để thử**.

### 3.2 Máy

- [ ] App bản mới nhất: GitHub Desktop → **Fetch origin** → **Pull origin**, rồi bấm đúp `run.bat`. Bản này phải có T-124, T-125: menu có **📈 Theo dõi**, giữa Kế hoạch và Cài đặt.
- [ ] Đồng hồ Windows bật **đặt giờ tự động**: «ngày theo giờ Google» tính từ giờ máy.
- [ ] Kết nối WordPress chạy được (menu **Kết nối WordPress** → **Kiểm tra kết nối** thấy «Kết nối thành công tới …»). Phần mềm cần danh sách bài đã đăng để gắn số liệu vào từng bài.
- [ ] Chủ dự án đăng nhập Search Console (https://search.google.com/search-console) bằng tài khoản chủ sở hữu thuộc tính.

### 3.3 Ca 0 · Kiểm nhanh trước khi bấm gì

1. Search Console → **Cài đặt** (Settings) → **Người dùng và quyền** (Users and permissions): chủ dự án đếm người dùng theo quyền, ví dụ «1 chủ sở hữu, 1 Hạn chế». Ghi số vào dòng (1) mục 7, không chép email. Ca 8 so lại.
2. App: **Cài đặt → 📗 Google**, khung **🔑 Tài khoản dịch vụ Google (file khóa)** ghi «✅ Đã khai báo». Không chụp khung này (có email).
3. Kéo xuống khung **📈 Search Console**:
   - **không** có câu «Thuộc tính Search Console đang được đặt trong biến môi trường GSC_SITE_URL của máy…». Có thì dừng: biến môi trường của máy đè file `.env`, phải gỡ trước (LC-T120-23);
   - dòng «⚪ Chưa chọn thuộc tính» (lần đầu), hay «✅ Đã chọn thuộc tính (lưu trong file .env)» (đã chọn từ trước: ghi loại ở dòng chú thích bên dưới);
   - chưa chọn thuộc tính thì nút **✅ Kiểm tra** bị khóa: đúng.

## 4. Các ca thử

Mỗi ca ghi vào bảng mục 7: giờ, câu báo nguyên văn (không bí mật), kết quả.

### Ca 1 · Tìm và lưu thuộc tính → (2)

1. Khung **📈 Search Console** → **🔎 Tìm thuộc tính**. Chờ dòng «Đang hỏi Search Console… (có thể mất vài giây)».
2. Xem bảng **Thuộc tính · Quyền · Dùng cho website**. Không chụp bảng và dòng email phía trên nó.
   - Phải có thuộc tính của website chính: cột **Quyền** là **Hạn chế**, cột **Dùng cho website** là «✔ dùng được» (thuộc tính tên miền: «✔ dùng được (tự lọc phần ngoài website)»).
   - Ghi số dòng; với mỗi dòng ghi loại (tiền tố hay tên miền), quyền, trạng thái.
   - Có dòng «✘ không phải website trong WORDPRESS_URL» (ví dụ thuộc tính staging): ghi lại. Khi dọn, chủ dự án gỡ email khỏi thuộc tính đó (mục 6, bước 3).
   - Có câu «Phần mềm chỉ cần quyền «Hạn chế»: nên hạ quyền…»: chủ dự án hạ quyền theo README mục 15 bước 3 ý 4, rồi bấm **🔎 Tìm thuộc tính** lại.
   - Câu «Tài khoản dịch vụ chưa thấy thuộc tính nào…»: kiểm lại README mục 15 bước 3 (đúng thuộc tính, đúng email), đợi vài phút, bấm lại. Vẫn vậy thì dừng, hỏi Lá Chắn.
   - Câu «… mục Google trả không đúng dạng bị bỏ.»: ghi số.
3. Ô **Thuộc tính dùng cho trang Theo dõi**: chọn thuộc tính của website chính. Có cả hai loại thì chọn loại **tiền tố** (README mục 15). Bấm **Lưu thuộc tính đã chọn**.
4. Phải thấy:
   - «Đã lưu thuộc tính Search Console vào file .env.»;
   - dòng «✅ Đã chọn thuộc tính (lưu trong file .env)»;
   - chú thích «Loại thuộc tính: …». Ghi loại.

### Ca 2 · Kiểm tra kết nối → (2)

1. Bấm **✅ Kiểm tra**. Chờ dòng «Đang kiểm kết nối Search Console… (có thể mất vài giây)».
2. Khung xanh phải có:
   - «Tài khoản dịch vụ thấy thuộc tính này, quyền «Hạn chế».»: đọc được danh sách thuộc tính với quyền «Hạn chế»;
   - «Có số liệu đã chốt tới hết ngày … (ngày theo giờ Google).»: đọc được số liệu. Ghi ngày, thường là 2–3 ngày trước.
3. Thuộc tính **tên miền** có thêm một trong hai câu:
   - «Mọi lượt hiển thị 28 ngày qua đều thuộc website.»;
   - «… lượt hiển thị 28 ngày qua nằm ngoài website (danh sách tên máy bên dưới): không tính.», kèm bảng **Tên máy · Lượt hiển thị · Ghi chú**. Ghi tỉ lệ và dạng tên máy, không chép tên.

   Thuộc tính **tiền tố** không có phần này: đúng thiết kế.
4. Dừng, hỏi Lá Chắn khi thấy:
   - «Gần hết lượt hiển thị nằm ngoài địa chỉ trong WORDPRESS_URL…» (`WORDPRESS_URL` có thể thiếu hay thừa `www.`);
   - «Thuộc tính chưa xác minh nên chưa đọc được số liệu.»;
   - câu 403 (mục 5).

### Ca 3 · Lấy số liệu lần đầu → (3), (7), (8)

1. Bấm **Mở trang Theo dõi** ở cuối khung Search Console (hay menu **📈 Theo dõi**). Trang ghi «Chưa có số liệu. Bấm «Lấy số liệu mới» (lần đầu lấy 16 tháng, khoảng một phút).».
2. Ghi giờ, bấm **🔄 Lấy số liệu mới**. Chờ dòng «Đang lấy số liệu từ Search Console…» chạy xong (khoảng một phút), không bấm gì thêm.
   - (Tùy chọn, LC-T120-22) Trong lúc chờ: mở tab thứ hai, đăng nhập app, vào **📈 Theo dõi**, bấm **🔄 Lấy số liệu mới**. Phải ra «Đang lấy số liệu Search Console ở tab khác…». Đóng tab đó.
3. Ghi giờ xong (tức thời gian lấy) và khung kết quả:
   - khung xanh «Đã lấy số liệu tới hết ngày … (ngày theo giờ Google). … ngày gần nhất còn là số tạm, chưa tính.»: ghi ngày và số ngày tạm;
   - các câu phụ bên dưới, ghi nguyên văn nếu có:
     - «… dòng số liệu không đúng dạng bị bỏ.» → (7);
     - «Có đoạn ngày nhiều dòng tới mức Google chỉ trả phần đầu…»;
     - «Từ khóa của một kỳ chạm trần số dòng Google trả…»;
     - «Chưa có danh sách bài đã đăng…».
   - **Không** có câu «Đã gửi đủ 20 lệnh tới Search Console cho lần bấm này…» → lần bấm đầu dùng ≤ 20 lệnh (8).
     - Màn hình không hiện số lệnh. Theo code, lần đầu cần **18 lệnh**: 16 đoạn ngày × trang (16 tháng, mỗi đoạn ≤ 31 ngày) và 2 kỳ từ khóa.
     - Có thể thêm 1 lệnh nếu Google báo 429 rồi phần mềm thử lại, và thêm vài lệnh nếu một đoạn quá 25.000 dòng.
   - Khung vàng «Đã lưu số liệu tới hết ngày …; phần còn lại chưa lấy được, bấm lại để lấy tiếp.» (kèm câu «Đã gửi đủ 20 lệnh…» hay «… (mã 429). Đợi 15 phút rồi bấm lại.»): ghi lại, đợi theo câu báo rồi bấm lại. Ghi tổng số lần bấm tới khi đủ.
4. Dưới nút có dòng «Số liệu tới hết ngày … (ngày theo giờ Google) · lấy lúc …». Ngày này phải khớp ngày ở bước 3 và ở ca 2.
5. Kéo xuống xem:
   - bốn ô **Lượt click · Lượt hiển thị · CTR · Vị trí trung bình**, bảng **Bài / trang**;
   - các câu «… dòng số liệu nằm ngoài địa chỉ website nên không tính.» hay «… bài, trang có địa chỉ không khớp địa chỉ website…», nếu có: ghi số.

### Ca 4 · Bấm lại ngay thì bị chặn → (5)

1. Ngay sau ca 3 (trong 10 phút), bấm **🔄 Lấy số liệu mới** lần nữa.
2. Phải thấy khung xanh dương «Vừa lấy số liệu lúc …; Google cập nhật khoảng một lần mỗi ngày nên chưa có gì mới. Để sau rồi bấm lại.». Trang trả lời ngay, không chờ: không có lệnh nào tới Google.
   - Ca 3 chưa lấy đủ (khung vàng) thì lần bấm này lấy tiếp, không bị chặn: đúng luật. Lấy đủ rồi làm lại ca 4.

### Ca 5 · So 2 bài với Search Console (bảng «Trang», 28 ngày) → (3)

1. Phần mềm, trang **📈 Theo dõi**: ô **Khoảng** chọn **28 ngày**, ô **So với** để **Kỳ trước**.
   - Kỳ 28 ngày kết thúc ở ngày «Số liệu tới hết ngày …» (gọi là E) và bắt đầu từ E trừ 27 ngày.
   - Dòng «Từ khóa trên Google (… – …)» ở phần **Chi tiết một bài, trang** ghi đúng hai ngày này. Ghi lại.
2. Chọn **2 bài** trong bảng **Bài / trang**:
   - bài A: nhiều click (đầu bảng);
   - bài B: ít click nhưng có lượt hiển thị (từ 100 trở lên, nếu có).

   Ghi cho mỗi bài: **Click**, **Hiển thị**, **Vị trí**.
3. Lấy địa chỉ hai bài: mở bài trên website (hay trang quản trị → Bài viết → Xem), chép địa chỉ.
4. Search Console, đúng thuộc tính đã lưu ở ca 1: **Hiệu suất** (Performance) → **Kết quả tìm kiếm** (Search results).
   - Bộ lọc ngày ở đầu báo cáo → **Tùy chỉnh** (Custom), đặt đúng hai ngày ở bước 1 → áp dụng. Không dùng «28 ngày qua»: ngày cuối của nó có thể là dữ liệu sơ bộ, khác ngày đã chốt của phần mềm.
   - Loại tìm kiếm để **Web** (mặc định), như phần mềm.
   - Bấm ô **Vị trí trung bình** trên biểu đồ để bật chỉ số này.
   - Thẻ **Trang** dưới biểu đồ: dùng ô lọc của bảng tìm theo một phần đường dẫn bài (tên theo giao diện Search Console).
5. So từng bài:
   - **Click**, **Hiển thị**: phải **bằng nhau**;
   - **Vị trí**: lệch **≤ 0,1**. Phần mềm viết «4,3»; Search Console viết «4,3» hay «4.3» tùy ngôn ngữ.
   - Có lệch: xem bảng «Trang» có nhiều dòng cùng một bài không (đường dẫn có `#…`, khác chữ hoa, có hay không có `/` cuối). Phần mềm gộp các dòng này, nên cộng lại rồi so. Vẫn lệch thì ghi cả hai số, báo Lá Chắn.
6. (Tùy chọn) So **tổng**: bốn ô đầu trang của phần mềm với các ô số trên biểu đồ của Search Console, cùng kỳ. Phần mềm có thể cao hơn chút, vì cộng theo từng trang («Tổng cộng theo từng trang nên có thể cao hơn chút so với biểu đồ của Search Console…»). Chỉ ghi lại.

### Ca 6 · Xem từ khóa của một bài → (10)

1. Phần mềm: phần **Chi tiết một bài, trang** → ô **Bài, trang** chọn bài A. Xem bảng «Từ khóa trên Google (…)» với các cột **Từ khóa · Click · Hiển thị · CTR · Vị trí · ± vị trí · Ghi chú**.
2. Search Console, cùng khoảng ngày:
   - thêm bộ lọc **Trang** bằng địa chỉ bài A (nút thêm bộ lọc ở hàng bộ lọc trên cùng; tên theo giao diện Search Console);
   - rồi thẻ **Cụm từ tìm kiếm** (Queries).
3. So 3 từ khóa đầu bảng của phần mềm: **Click**, **Hiển thị** phải bằng nhau.
   - Dòng có ghi chú «gộp … cách gõ»: bật **Xem từng cách gõ của từ khóa đã gộp**, so từng cách gõ.
   - Ghi khớp / không khớp và các số, không chép từ khóa.
4. Cộng click của mọi từ khóa luôn **ít hơn** click của bài, vì Google ẩn từ khóa hiếm («Google ẩn từ khóa hiếm và từ khóa có thông tin cá nhân…» dưới bảng). Đúng, không phải lỗi.
5. Dưới bảng có ô chọn từ khóa và nút **➕ Đưa vào kế hoạch**: làm ở ca 6b.

### Ca 6b · Đưa từ khóa vào kế hoạch → (11)

Cần Google Sheet kế hoạch đã nối (README mục 14) và trang **Kế hoạch** đọc được kế hoạch. Chưa nối thì bỏ ca này, ghi «Chưa làm».

Dòng thêm vào là **dòng kế hoạch thật** trên Sheet đang khai báo. Vì vậy:
- chủ dự án chọn từ khóa mình thật sự muốn viết bài;
- không muốn đụng Sheet thật thì làm trên Sheet bản sao như kịch bản T-128 mục 3.4, rồi đổi lại Sheet thật khi dọn.

1. Mở Google Sheet kế hoạch trong trình duyệt. Ghi số dòng và Mã bài cuối cùng (ví dụ «B-0…»).
2. Phần mềm: **📈 Theo dõi** → **Chi tiết một bài, trang** → bài A, khoảng **28 ngày**. Dưới bảng từ khóa có ô **Chọn từ khóa đưa vào kế hoạch (tối đa 10)**.
   - Ô chọn chỉ có từ khóa «sạch»: chữ tiếng Việt hoặc a–z, số, khoảng trắng, dấu «-», tối đa 80 ký tự, không có số điện thoại, email, địa chỉ web.
   - Có dòng «… từ khóa không có trong ô chọn…» thì dòng đó chỉ ghi số, không chép lại từ khóa bị để ngoài.
   - Không từ khóa nào qua lọc thì có dòng «Không có từ khóa nào đưa vào kế hoạch được…». Khi đó chọn bài khác.
   - Ghi số từ khóa trong ô chọn và số từ khóa bị để ngoài.
3. Chủ dự án chọn **1–2 từ khóa**, bấm **➕ Đưa vào kế hoạch**.
4. App mở trang **Kế hoạch**. Khung **Đề xuất thay đổi** phải có:
   - ghi chú «Từ khóa chọn ở trang «📈 Theo dõi» (Search Console): duyệt rồi mới ghi vào Sheet.»;
   - mỗi từ khóa một dòng: cột **Loại** là «Thêm», **Mã bài** mới (chưa có trên Sheet), **Nguồn** là «Search Console»;
   - dòng trùng kế hoạch hay trùng bài đã đăng có dấu ⚠️ và **không** tick sẵn.
5. **Trước khi áp dụng:** tải lại Sheet trong trình duyệt (F5). Phải **chưa** có dòng mới: số dòng như bước 1.
6. Tick đúng một dòng (chủ dự án quyết), bấm **✅ Áp dụng thay đổi (1)**. Khung **Kết quả áp dụng** phải màu xanh.
7. Tải lại Sheet. Phải có **đúng một** dòng mới, với:
   - Mã bài như ở bước 4;
   - Trạng thái «Chưa viết»;
   - từ khóa đúng như đã chọn.

   Các dòng cũ không đổi.
8. (Tùy chọn) Làm lại bước 2–4 rồi bấm **Hủy** ở trang Kế hoạch. Tải lại Sheet: không có gì đổi.

### Ca 7 · Số đo cho Lá Chắn: `metadata`, dòng bị bỏ → (4), (7)

Màn hình không hiện `metadata` và số dòng bị bỏ của từng lần gọi. Chỉ Huy chạy một đoạn lệnh **chỉ đọc**:

- dùng đúng client Search Console của phần mềm: chỉ xin quyền đọc, chỉ hai loại lệnh cố định;
- gửi khoảng 3 lệnh;
- chỉ in loại thuộc tính, ngày, số dòng, trạng thái. Không in email, thuộc tính đầy đủ, địa chỉ trang hay từ khóa.

Lá Chắn đọc đoạn lệnh này trước buổi thử.

1. Làm sau ca 6, app vẫn mở cũng được.
2. Mở **PowerShell** trong thư mục phần mềm (thư mục có `run.bat`): mở thư mục đó trong File Explorer, gõ `powershell` vào thanh địa chỉ, Enter.
3. Dán cả khối dưới đây, Enter. Khối chỉ có chữ không dấu, vì PowerShell gửi chữ qua ống bằng bảng mã ASCII.

```powershell
@'
from datetime import timedelta
from seo_app import config
from seo_app.google.search_console import SearchConsoleClient, today_pacific
try:
    c = SearchConsoleClient.from_settings(config.load_settings())
    t = today_pacific()
    print("loai thuoc tinh:", c.site.kind)
    for name, a, b in (("Q1 moi nhat", t - timedelta(days=30), t),
                       ("Q1 cu", t - timedelta(days=120), t - timedelta(days=90))):
        r = c.fetch_day_page(a, b)
        print(name, a, b, "| metadata:", r.metadata, "| ngay tam dau:", r.first_incomplete_date,
              "| dong:", len(r.rows), "| bo:", r.dropped, "| cham tran:", r.truncated)
    q = c.fetch_page_query(t - timedelta(days=30), t - timedelta(days=3))
    print("Q2 28 ngay | dong:", len(q.rows), "| bo:", q.dropped, "| cham tran:", q.truncated)
    print("so lenh da gui:", c.request_count)
except Exception as exc:
    ok = type(exc).__name__ in {"SearchConsoleError", "ServiceAccountError", "ConfigError"}
    print("DUNG:", type(exc).__name__, exc if ok else "")
'@ | uv run python -
```

4. Kết quả có 5 dòng. Ghi vào mục 7:
   - `metadata:` của «Q1 moi nhat» (31 ngày tới hôm nay theo giờ Google) và «Q1 cu» (31 ngày, cách đây 3–4 tháng): `ok`, `missing` hay `bad`; kèm `ngay tam dau`.
     - `ok`: Google có trả ngày số tạm, dưới một trong hai tên trường phần mềm nhận (`first_incomplete_date`, `firstIncompleteDate`). Đoạn lệnh không đọc tên thô.
     - «Q1 moi nhat» ra `missing` hay `bad`: Google thiếu `metadata` ở đoạn mới nhất. Chỉ Huy mở phiếu nhỏ (mục 8).
     - «Q1 cu» ra `missing`: bình thường, cả đoạn đã chốt.
   - `bo:` (dòng bị bỏ), `dong:` (số dòng), `cham tran:` (`True`: Google chỉ trả phần đầu) của ba lần gọi.
   - `so lenh da gui:` (thường là 3).
   - Dòng `DUNG: …` thay cho kết quả: ghi nguyên dòng. Lỗi của phần mềm (ba loại `SearchConsoleError`, `ServiceAccountError`, `ConfigError`) thì có kèm câu cố định, không bí mật; lỗi khác chỉ in tên loại lỗi. Câu 403 thì theo mục 5.
5. Đóng cửa sổ PowerShell.

### Ca 8 · Search Console: Người dùng và quyền không đổi → (6)

1. Chủ dự án mở Search Console, đúng thuộc tính đã dùng → **Cài đặt** → **Người dùng và quyền**.
2. Phải giống ca 0 bước 1: email tài khoản dịch vụ vẫn quyền **Hạn chế**; không có người dùng hay chủ sở hữu mới; không ai bị đổi quyền. Ghi «không đổi», hay điều khác thấy (không chép email).
3. (Tùy chọn) **Sơ đồ trang web** (Sitemaps): không có mục mới. Phần mềm không có lệnh ghi nào nên không thể thêm.

## 5. Khi gặp sự cố trong buổi

1. **Dừng**, không bấm lại nhiều lần.
2. Ghi giờ, câu báo nguyên văn (không bí mật), đang ở ca nào.
3. Theo câu báo:

| App báo | Làm gì |
|---|---|
| «Chưa bật Google Search Console API trong Google Cloud (mã 403)…» | Chủ dự án bật API (README mục 15 bước 1), đúng project của tài khoản dịch vụ; đợi vài phút, làm lại. Ghi vào (9) |
| «Tài khoản dịch vụ chưa có quyền xem thuộc tính này (mã 403)…» | **Không nâng quyền.** Kiểm README mục 15 bước 1 và 3 (đúng thuộc tính, đúng email, quyền «Hạn chế»). Vẫn báo thì dừng buổi thử, hỏi chủ dự án và Lá Chắn |
| «Search Console đang giới hạn số lần lấy số liệu (mã 429)…» | Đợi 15 phút rồi bấm lại. Ghi vào (9). Google có thể báo hết hạn mức bằng mã 403; khi đó phần mềm vẫn hiện câu này |
| «Google không nhận mã truy cập (mã 401)…» | Dừng; kiểm file khóa theo README mục 14. Không tạo khóa mới trong buổi |
| «Không tìm thấy thuộc tính trong Search Console (mã 404)…» | Làm lại ca 1 |
| «Thuộc tính Search Console đã chọn không phải của website trong WORDPRESS_URL…» | Làm lại ca 1, chọn thuộc tính của website chính |
| «Không kết nối được tới Search Console…», «Search Console không trả lời sau … giây…» | Kiểm mạng, đợi rồi làm lại |
| Câu ở quy tắc 8 | Dừng buổi thử, báo Lá Chắn |

4. Báo Chỉ Huy và Lá Chắn. Chưa dùng trang 📈 Theo dõi cho tới khi Lá Chắn xem.

## 6. Dọn sau buổi thử (đánh dấu từng dòng)

1. [ ] **Giữ** thuộc tính đã lưu trong `.env` và bản lưu tạm số liệu: anh/chị dùng tiếp trang 📈 Theo dõi.
2. [ ] Chỉ **xóa bản lưu tạm** khi phần mềm báo file lưu tạm bị lỗi, khi Lá Chắn yêu cầu lấy lại (ví dụ sau phiếu `metadata`), hay khi đã lưu nhầm thuộc tính.
   - Cách xóa: trang **📈 Theo dõi** → khung **🧹 Bản lưu tạm số liệu trên máy** → **Xóa bản lưu tạm** → **Xóa**.
   - Phải thấy «Đã xóa bản lưu tạm số liệu Search Console…». Lần bấm **🔄 Lấy số liệu mới** sau đó lấy lại 16 tháng.
3. [ ] Ca 1 có dòng «✘ …» (thuộc tính staging hay thuộc tính thừa đang có email tài khoản dịch vụ): chủ dự án gỡ email khỏi thuộc tính đó. Search Console → **Cài đặt → Người dùng và quyền** → biểu tượng trình đơn cạnh email → **Xoá quyền truy cập**.
4. [ ] Ca 1 có phải hạ quyền: kiểm lại quyền đã là «Hạn chế» (ca 8).
5. [ ] Đóng cửa sổ PowerShell của ca 7; không lưu đầu ra vào thư mục phần mềm.
6. [ ] Tab thứ hai (bước tùy chọn ở ca 3): đã đóng.
7. [ ] Dòng kế hoạch thêm ở ca 6b:
   - chủ dự án muốn viết bài đó thì giữ;
   - không thì chủ dự án tự xóa dòng trên Google Sheet (phần mềm không bao giờ xóa dòng);
   - đã làm trên Sheet bản sao thì dán lại link Sheet thật ở **Cài đặt → 📗 Google** (kịch bản T-128 mục 6 bước 8).
8. [ ] Ảnh chụp màn hình: soát không có email, thuộc tính đầy đủ, tên máy, đường dẫn file khóa, mã Sheet đầy đủ (mục 1); lưu ngoài thư mục dự án, không đưa lên GitHub.

## 7. Bảng ghi kết quả (cho Lá Chắn)

Chỉ Huy điền ngay trong buổi. Sau buổi, chép bảng vào báo cáo buổi thử (`docs/team/reports/`, phiếu do Chỉ Huy lập), kèm các ca đã bỏ và lý do.

| Mã | Kiểm gì | Kết quả (Đạt / Không đạt / Chưa làm) | Ghi chú: giờ, câu báo nguyên văn (không bí mật), số |
|---|---|---|---|
| (1) | API đã bật, email quyền «Hạn chế» trước buổi; người dùng Search Console trước buổi (đếm theo quyền, ca 0) | | |
| (2) Tìm thuộc tính | Số dòng; loại, quyền, «Dùng cho website» từng dòng; cảnh báo quyền cao; mục bị bỏ | | |
| (2) Lưu | «Đã lưu thuộc tính…»; loại thuộc tính đã lưu; có / không cảnh báo biến môi trường | | |
| (2) Kiểm tra | Quyền «Hạn chế»; ngày chốt cuối; thuộc tính tên miền: tỉ lệ ngoài website, dạng tên máy | | |
| (3) Lấy lần đầu | Khung xanh / vàng / đỏ; thời gian lấy; ngày chốt cuối; số ngày tạm; các câu phụ | | |
| (8) Số lệnh | Không có «Đã gửi đủ 20 lệnh…» (≤ 20); số lần bấm tới khi đủ | | |
| (5) Bấm lại | «Vừa lấy số liệu lúc …», trả lời ngay | | |
| Tab khác (tùy chọn) | «Đang lấy số liệu Search Console ở tab khác…» | | |
| (3) Bài A | Phần mềm / Search Console: click, hiển thị, vị trí; khoảng ngày | | |
| (3) Bài B | Như bài A | | |
| (3) Tổng (tùy chọn) | Bốn ô đầu trang so với Search Console | | |
| (10) Từ khóa | 3 từ khóa đầu: click, hiển thị khớp; cộng từ khóa ít hơn tổng của bài | | |
| (11) Đưa vào kế hoạch | Số từ khóa trong ô chọn, số bị để ngoài; đề xuất «Thêm», nguồn «Search Console», Mã bài mới, cảnh báo ⚠️; trước «Áp dụng» Sheet không đổi; sau «Áp dụng» đúng một dòng mới, trạng thái «Chưa viết»; «Hủy» không ghi gì (tùy chọn) | | |
| (4) `metadata` mới nhất | `ok` / `missing` / `bad`; ngày tạm đầu | | |
| (4) `metadata` cũ | `ok` / `missing` / `bad` | | |
| (7) Dòng bị bỏ | Câu «… dòng số liệu không đúng dạng bị bỏ.» ở lần lấy đầu (số); ca 7: `bo`, `dong`, `cham tran` của Q1 mới nhất, Q1 cũ, Q2 | | |
| (9) 403, 429 | Câu báo nếu gặp: chưa bật API, thiếu quyền, hết hạn mức | | |
| (6) Người dùng và quyền | Không đổi so với ca 0 | | |
| Câu báo | Mọi câu là câu tiếng Việt cố định; không lộ email, đường dẫn máy, lời máy chủ | | |
| Dọn | Mục 6, đủ 8 dòng | | |

## 8. Sau buổi thử

- **Lá Chắn** đọc bảng mục 7, kết luận có cho dùng trang 📈 Theo dõi không (Lá Chắn T-121 B4: đọc báo cáo thử trước khi dùng), rồi rà cả Giai đoạn 6 (T-120 mục 6 «Đi kèm»).
  - `metadata` của đoạn mới nhất ra `missing` hay `bad`: Chỉ Huy mở phiếu nhỏ theo Lá Chắn T-124 B.3. Phiếu đó làm hai việc, sửa ở client T-121 và Lá Chắn kiểm lại:
    - mỗi lần bấm lấy lại 7 ngày cuối (vẫn 1 lệnh);
    - xét nới luật 10% dòng lạ, chỉ áp khi lần gọi có từ 20 dòng trở lên.
  - Có dòng bị bỏ, hay câu «… nhiều dòng không đúng dạng hoặc lặp lại…»: Lá Chắn xét lại luật 10% (Soi Lỗi T-124 GN-2).
  - Click, hiển thị không bằng nhau, hay vị trí lệch quá 0,1: phiếu cho Thợ Máy (cách cộng số theo trang, vị trí trung bình theo lượt hiển thị, T-120 «Rủi ro»).
- **Thư Ký**: README mục 15 (T-126 đã viết theo thiết kế) sửa theo kết quả thật nếu khác: thời gian lần lấy đầu, số ngày tạm, số từng bài có khớp thẻ «Trang» không, quyền «Hạn chế» có đủ không.
- **Chỉ Huy** cập nhật bảng việc, `docs/team/dong-bo.md`, bảng tiến độ cho chủ dự án.

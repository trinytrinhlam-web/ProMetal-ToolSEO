# Báo cáo T-126 · README «Theo dõi trên Google» (Search Console)

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-126](../tickets/T-126-readme-theo-doi-google.md) (Chỉ Huy B giao phần 1 ngày 05/11) |
| Nhánh | `team/T-126` (từ `main` cục bộ `8caab2f`) |
| Ngày nộp phần 1 | 2026-11-05 10:56 (+07:00, theo đồng hồ máy) |
| Kết quả | **Phần 1 xong** (yêu cầu 1, 2 của phiếu). Phần 2 (yêu cầu 3: cách đọc số, nút «Đưa vào kế hoạch») làm sau T-125. Chỉ sửa `README.md` và chú thích trong `.env.example`, không sửa code |

## Phần 1

### Tóm tắt (cho chủ dự án)

- README có **mục 15 «Theo dõi trên Google (Search Console)»**. Anh/chị làm trước 3 bước phía Google, mỗi bước làm một lần, dùng cho cả hai máy:
  1. bật «Google Search Console API» trong đúng project Google Cloud đang dùng cho Sheets;
  2. chép email tài khoản dịch vụ ở **Cài đặt → 📗 Google**;
  3. thêm email đó vào Search Console với quyền **«Hạn chế»**.
- Mục 15 cũng dặn:
  - chọn thuộc tính nào (nên dùng loại «Tiền tố URL»);
  - không dùng thuộc tính của bản thử website (staging);
  - gặp lỗi 403 thì **không nâng quyền** mà báo Chỉ Huy;
  - cách gỡ quyền khi không dùng nữa.
- Trang 📈 Theo dõi và phần chọn thuộc tính trong app **chưa có**. README ghi rõ điều này, và dặn chưa cần sửa `GSC_SITE_URL` trong `.env`.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md:604-659` (mục 15 mới, sau mục 14, trước «Dành cho người phát triển») | Đoạn mở đầu (chỉ đọc, dùng lại file khóa mục 14); khung «Hiện tại» (app chưa có phần này); «Trước khi bắt đầu» (có tài khoản dịch vụ, đăng nhập bằng chủ sở hữu, «thuộc tính» / «tài sản» / *property*); bước 1 bật API (đúng project, không cấp vai trò); bước 2 chép email (chú thích «quyền Người chỉnh sửa» trong app là nói về Sheet); bước 3 thêm email quyền «Hạn chế», không «Toàn quyền», không chủ sở hữu, Search Console không nhận thì dừng, báo Chỉ Huy; bảng «Chọn thuộc tính nào» (hai loại, dạng app lưu, staging, `http://`); bảng «Khi app báo lỗi» (4 câu: hai câu 403, thuộc tính không phải của website, sai dạng); «Giữ an toàn» (xem lại quyền, đổi khóa không đổi email, «Xoá quyền truy cập») |
| `README.md:556`, `:561` (mục 14) | Câu mở đầu thêm «(và thuộc tính Search Console bạn thêm nó vào, mục 15)». Bước 2 đổi «Chỉ cần bật API này.» thành «Phần kế hoạch chỉ cần API này; phần theo dõi Google (mục 15) bật thêm Google Search Console API trong cùng project.» Câu cũ sẽ sai khi chủ dự án làm bước 1 của mục 15 |
| `.env.example:53-59` | Chú thích `GSC_SITE_URL`: thuộc tính của website (README mục 15); nên chọn trong app ở Cài đặt → Google, mục Search Console (đang làm), app tự ghi dòng này; chỉ 2 dạng, chữ thường không dấu: `https://example.com/` («Tiền tố URL», nên dùng: `https://`, có `/` cuối, không đường con, tên miền giống hệt `WORDPRESS_URL` kể cả `www.`) và `sc-domain:example.com` («Tên miền», app chỉ lấy số liệu của `WORDPRESS_URL`); không dùng thuộc tính staging hay `http://`. Dòng `GSC_SITE_URL=` giữ nguyên, rỗng |

### Đối chiếu

**Yêu cầu 1** (phiếu; thiết kế `T-120-tho-may.md` mục 1.2, 2.1, 2.7, 2.8):

| Ý | README mục 15 |
|---|---|
| Bật «Google Search Console API» trong project đang dùng cho Sheets, không cấp thêm vai trò (1.2 bước 1) | Bước 1 |
| Chép email tài khoản dịch vụ ở Cài đặt → Google (1.2 bước 2) | Bước 2. App hiện email ở khung «🔑 Tài khoản dịch vụ Google (file khóa)» (`app/views/settings.py:573-598`, `st.code`) |
| «Cài đặt» → «Người dùng và quyền» → «Thêm người dùng» → quyền «Hạn chế»; không «Toàn quyền», không chủ sở hữu; chỉ chủ sở hữu làm được (1.2 bước 3) | Bước 3, «Trước khi bắt đầu» |
| Có cả hai loại thì chọn tiền tố; chỉ có tên miền thì dùng, app tự lọc (1.2) | Bảng «Chọn thuộc tính nào» |
| Không chọn thuộc tính staging (1.2, 2.7) | Bảng và gạch đầu dòng dưới bảng; bước 3 ý 1 «website chính»; câu báo «… (ví dụ thuộc tính staging)» |
| 403 không nâng quyền, hỏi Chỉ Huy (phiếu) | Bảng «Khi app báo lỗi» dòng 2; bước 3 (Search Console không nhận email thì báo Chỉ Huy) |
| Cùng file khóa, không khóa thứ hai; hai lớp chỉ đọc (2.1) | Đoạn mở đầu; bước 3 ý 3 |
| Câu báo cố định (2.8) | 4 câu trích khớp nguyên văn đầu câu trong `seo_app/google/search_console.py` |
| 1.2 bước 4 (trong app: «Tìm thuộc tính», lưu, «Kiểm tra») | **Không viết**: app chưa có (grep `app/` không thấy «Search Console», `GSC_SITE_URL`). Khung «Hiện tại» nói phần này viết thêm khi làm xong |

**Yêu cầu 2** (`.env.example`): đủ ba ý của phiếu, gồm hai dạng hợp lệ, nên chọn ở Cài đặt và không dùng staging. Chỉ đổi dòng chú thích.

**Đối chiếu code** (script Python đọc UTF-8, chạy trên nhánh, gọi thẳng hàm của `seo_app/google/search_console.py`): «thiếu/sai: 0» trên 38 điểm.
- 4 câu báo trong bảng là đầu câu thật: `_MSG_API_OFF`, `_MSG_BY_STATUS[403]`, `_MSG_NOT_SITE`, `_MSG_BAD_PROPERTY`.
- 3 nhãn giao diện có thật: «📗 Google», «🔑 Tài khoản dịch vụ Google (file khóa)», câu chú thích email «… (quyền Người chỉnh sửa):».
- `parse_property` nhận `https://example.com/`, `sc-domain:example.com`. Từ chối bằng câu sai dạng: `http://`, thiếu `/` cuối, chữ hoa, đường con, cổng, rỗng.
- `covers_site`:
  - tiền tố phải cùng tên máy (`www.` phải giống);
  - tên miền phủ cả `www.`;
  - `evilexample.com` không phủ;
  - thuộc tính staging (tiền tố `https://www.staging-m.example.com/` hay `sc-domain:staging-m.example.com`) không phủ `https://example.com`.
- Phạm vi `webmasters.readonly`; `from_settings` dùng `GOOGLE_SERVICE_ACCOUNT_FILE` với phạm vi đó; chỉ hai lệnh (`GET sites`, `POST query`).
- Mọi «mục N» trong README trỏ tới mục có thật.

**Trang trợ giúp Google** «Quản lý chủ sở hữu, người dùng và quyền» (`support.google.com/webmasters/answer/7687615?hl=vi`, đọc ngày 05/11):
- Đường đi: «Cài đặt > Người dùng và quyền» → «Thêm người dùng».
- Chỉ chủ sở hữu thêm, xóa người dùng được.
- Trình đơn cạnh người dùng có «Thay đổi quyền», «Xoá quyền truy cập».
- Bảng quyền: «Người dùng bị hạn chế» xem được «Hiệu suất». «Cài đặt tài sản» chỉ xem. Không «Gửi sơ đồ trang web», không «Thêm người dùng».
- Câu README «cài đặt của Search Console thì chỉ xem, không sửa được» viết theo bảng này.

### Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ uv run pytest tests/test_config.py tests/test_hash_password_script.py tests/test_la_chan_t090.py tests/test_t090_env_bang_ma.py -q
62 passed
$ uv run pytest tests/test_soi_loi_t112.py tests/test_soi_loi_t106.py -k readme -q
5 passed, 69 deselected
$ (script đối chiếu README mục 15, .env.example với code)   thiếu/sai: 0
$ PYTHONUTF8=1 uvx detect-secrets scan README.md .env.example docs/team/reports/T-126-thu-ky.md
  "results": {}
```

- Các test đã chạy:
  - `test_config.py` có hai ca đọc `.env.example`: đủ tên biến, không có giá trị thật.
  - Ba file còn lại chép `.env.example` thật hay dựng `.env` từ nó.
  - Năm ca `readme` đọc README mục 11 và dòng «Trạng thái».
- Không chạy toàn bộ pytest, không chạy ruff (không đổi file `.py`).
- `detect-secrets` có mồi đối chứng: chép 3 file vào thư mục nháp, thêm vào bản chép dòng mở đầu một khóa riêng (như trong file khóa Google) và một khóa AWS mẫu, quét từ chính thư mục đó: bắt được cả hai («Private Key», «AWS Access Key»).
- README và `.env.example` không chứa:
  - email tài khoản dịch vụ (chỉ có đuôi `.iam.gserviceaccount.com`, như mục 14);
  - mã project, đường dẫn file khóa thật, tên miền thật.

  Ví dụ dùng `ten-mien-cua-ban` (như mục 6) và `example.com` (như `.env.example`).

### Rủi ro và điểm cần chú ý

- **Nhãn trên giao diện Search Console chưa đối chiếu trên trang thật.**
  - Các nhãn đã lấy từ trang trợ giúp tiếng Việt, mà Google ghi trang đó có thể do AI dịch: «Cài đặt», «Người dùng và quyền», «Thêm người dùng», «Thay đổi quyền», «Xoá quyền truy cập».
  - «Hạn chế» / «Toàn quyền» trong ô chọn quyền và nút «Thêm» lấy theo thiết kế T-120 mục 1.2.
  - Cột «Nhận ra trong Search Console» (thuộc tính tên miền chỉ ghi tên miền, thuộc tính tiền tố ghi `https://…`) viết theo hiểu biết của tôi, chưa xem trên tài khoản thật.
- **Thêm tài khoản dịch vụ làm người dùng Search Console chưa xác minh với tài khoản thật** (T-120 mục 1.2; Lá Chắn T-121 điều kiện B4 (a)). README có lối dừng: Search Console không nhận email, hay chỉ cho thêm làm chủ sở hữu, thì báo Chỉ Huy. Nên đưa ý này vào buổi thử thật với Google.
- **Hai chỗ chỉ đúng tới khi T-124, T-125 xong**: khung «Hiện tại» của README mục 15 và chữ «(đang làm)» trong `.env.example`. Phần 2 phải sửa lại.
- Hai câu ở mục 14 đổi để không mâu thuẫn với mục 15. Không có test nào ghim hai câu này: đã grep `tests/` theo «README», «.env.example».

### Để lại cho phần 2 (sau T-125)

- Cách dùng trong app: «Tìm thuộc tính», chọn, lưu, «Kiểm tra». Bỏ khung «Hiện tại» và chữ «(đang làm)».
- Cách đọc số (yêu cầu 3), nút «Đưa vào kế hoạch».
- Câu báo mới của T-124, T-125 (đang lấy ở tab khác, 429, giới hạn 20 lệnh…).
- Cảnh báo biến môi trường `GSC_SITE_URL` đè `.env` (LC-T120-23).
- Mục 4 (menu có «📈 Theo dõi») và dòng «Trạng thái» đầu README.

### Câu hỏi cho chủ dự án

Không có.

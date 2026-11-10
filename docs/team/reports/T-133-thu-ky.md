# Báo cáo T-133 · Kịch bản buổi thử thật Google Search Console

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-133](../tickets/T-133-kich-ban-thu-that-google.md) (Chỉ Huy B giao 07/11) |
| Nhánh | `team/T-133` (từ `main` cục bộ `e25afa1`, đã có T-124) |
| Ngày nộp | 2026-11-07 08:29 (+07:00, theo đồng hồ máy) |
| Kết quả | Xong yêu cầu 1–4. Thêm `docs/team/reports/T-133-kich-ban-thu-that-google.md` (300 dòng) và báo cáo này. Không sửa code, README |

## Tóm tắt (cho chủ dự án)

- **Kịch bản buổi thử thật trang 📈 Theo dõi** đã soạn sẵn từng bước, theo mẫu kịch bản Hẹn giờ/Đăng ngay (T-128). Anh/chị báo rảnh là làm được, sau khi phiếu giao diện T-125 gộp xong.
- Buổi thử **chỉ đọc**: không đăng bài, không sửa gì trên Search Console hay website. Khoảng 45–60 phút.
- Việc của anh/chị:
  - trước buổi: làm README mục 15 bước 1–3 (bật API, thêm email tài khoản dịch vụ với quyền «Hạn chế»), nếu chưa làm;
  - trong buổi: tự đăng nhập Search Console, mở bảng «Trang» để so số với phần mềm, cuối buổi xem lại «Người dùng và quyền».
- Gặp lỗi 403 thì **không nâng quyền**: dừng, hỏi anh/chị và Lá Chắn.

## Đã thay đổi

| File | Nội dung |
|---|---|
| `docs/team/reports/T-133-kich-ban-thu-that-google.md` (mới) | Bảng đầu (dùng cho ai, khi nào, tên nút theo `team/T-125` `216ff2f`, nguồn). Mục 0 tóm tắt cho chủ dự án. Mục 1: 8 quy tắc (không bí mật, chỉ đọc, 403 không nâng quyền, điểm dừng). Mục 2: bảng 10 việc → ca. Mục 3: chuẩn bị phía Google, máy, ca 0. Mục 4: ca 1–8. Mục 5: xử lý sự cố (bảng 8 câu báo). Mục 6: dọn (7 bước). Mục 7: bảng kết quả cho Lá Chắn (19 dòng). Mục 8: sau buổi thử |

## Đối chiếu

### Yêu cầu 1: chuẩn bị, các ca, bảng kết quả, dọn

| Phiếu đòi | Kịch bản |
|---|---|
| Chuẩn bị: chủ dự án đã bật API, đã thêm email quyền «Hạn chế» | Mục 3.1 (kèm điều kiện có tài khoản dịch vụ, file khóa theo README mục 14), ca 0 (Cài đặt, biến môi trường đè `.env`) |
| Tìm thuộc tính | Ca 1 (bảng Thuộc tính · Quyền · Dùng cho website, chọn, **Lưu thuộc tính đã chọn**) |
| Kiểm tra | Ca 2 (quyền «Hạn chế», ngày chốt cuối, phần ngoài website của thuộc tính tên miền) |
| Lấy số liệu lần đầu | Ca 3 (thời gian, câu kết quả, câu phụ, ≤ 20 lệnh) |
| Bấm lại ngay bị chặn | Ca 4 |
| So 2 bài với Search Console bảng «Trang» 28 ngày | Ca 5 (khoảng ngày tùy chỉnh đúng kỳ của phần mềm; click, hiển thị bằng nhau, vị trí lệch ≤ 0,1) |
| Xem từ khóa | Ca 6 |
| Search Console → Người dùng và quyền không đổi | Ca 0 bước 1 (đếm trước buổi), ca 8 (so lại) |
| Bảng ghi kết quả cho Lá Chắn | Mục 7 |
| Cách dọn (Xóa bản lưu tạm nếu cần) | Mục 6 bước 2 (chỉ xóa khi file lỗi, Lá Chắn yêu cầu, hay lưu nhầm thuộc tính) |

**Nguồn:**

| Nguồn | Kịch bản |
|---|---|
| T-120 mục 6 «Thử thật», 6 bước | Việc (1)–(6) ở mục 2 |
| T-120 «Rủi ro»: tài khoản dịch vụ làm người dùng; vị trí trung bình theo lượt hiển thị; tổng theo trang cao hơn biểu đồ; từ khóa bị ẩn; staging; `WORDPRESS_URL` thiếu, thừa `www.`; lần đầu 18 lệnh | Ca 1 (Search Console không nhận email thì dừng), ca 5, ca 5 bước 6, ca 6 bước 4, ca 1–2, ca 2 bước 4, ca 3 |
| Lá Chắn T-121 B4 (a) quyền «Hạn chế» đọc `sites`, `query` | Ca 1, ca 2 |
| Lá Chắn T-121 B4 (b) tên trường `metadata` | Ca 7 |
| Lá Chắn T-121 B4 (c) mã lý do 403 chưa bật API, hết hạn mức | Mục 3.1 (tùy chọn, chỉ khi API chưa bật), mục 5 |
| Lá Chắn T-121 B4 (d) `dropped` của Q1, cỡ câu trả lời | Ca 3, ca 7 (`dong`, `bo`, `cham tran`) |
| Lá Chắn T-124 B.3: `metadata` đoạn mới nhất và một đoạn cũ; `dropped` Q1, Q2; quyền «Hạn chế»; số lệnh lần đầu ≤ 20; thiếu `metadata` thì mở phiếu nhỏ | Ca 7; ca 3, ca 7; ca 1, ca 2; ca 3; mục 8 |
| README mục 15 | Mục 3.1, ca 1, mục 5, mục 6 bước 3 |

### Yêu cầu 2: 403 không nâng quyền

- Quy tắc 3 (`:31`): không «Toàn quyền», không chủ sở hữu, không cấp vai trò Google Cloud; dừng, hỏi chủ dự án và Lá Chắn.
- Mục 5, dòng câu «Tài khoản dịch vụ chưa có quyền xem thuộc tính này (mã 403)…»: kiểm README mục 15 bước 1, 3, vẫn báo thì dừng.
- Ca 1, ca 2 trỏ về mục 5.

### Yêu cầu 3: không ghi bí mật

- Quy tắc 1 (`:23`):
  - không ghi file khóa, email tài khoản dịch vụ, mã project;
  - thuộc tính chỉ ghi **loại**, tên máy chỉ ghi dạng;
  - không chụp `.env`, khung 🔑, bảng «Tìm thuộc tính» (bảng này hiện cả email lẫn thuộc tính đầy đủ: `gsc_found_panel` của T-125).
- Bảng kết quả không có cột nào đòi giá trị bí mật.
- Đoạn lệnh ca 7 không in email, thuộc tính đầy đủ, địa chỉ trang, từ khóa.
- Dọn bước 7: soát ảnh chụp.
- Bản thân kịch bản:
  - không có email, `.json`, tên miền thật;
  - địa chỉ duy nhất là trang công khai `https://search.google.com/search-console`.

### Yêu cầu 4: tên nút theo T-125

- Đọc `app/views/tracking.py`, `app/views/settings.py`, `app/main.py` trên `team/T-125` (`216ff2f`). Nhánh này chỉ đổi `app/` so với `main`, nên câu của lõi đối chiếu theo `main`.
- Bảng đầu (`:9`) ghi rõ: tên theo `216ff2f`, chưa gộp; gộp xong mà khác thì theo giao diện.
- Nhãn của Search Console chưa chắc thì ghi «(tên theo giao diện Search Console)»: ô lọc bảng «Trang», nút thêm bộ lọc. Các nhãn «Cụm từ tìm kiếm», «Trang», «Vị trí trung bình», báo cáo mặc định 3 tháng, «dữ liệu sơ bộ» đã đối chiếu với trang trợ giúp tiếng Việt của Google (`support.google.com/webmasters/answer/7576553?hl=vi`, đọc 07/11).

### Thêm ngoài danh sách ca của phiếu (đề nghị Lá Chắn xét)

1. **Ca 7: đoạn lệnh đo kỹ thuật** (`:182-227`).
   - Màn hình T-125 không hiện `metadata`, cũng không hiện dòng bị bỏ của từng lần gọi, mà Lá Chắn T-121 B4 (b), T-124 B.3 cần hai số này.
   - Đoạn lệnh dùng đúng `SearchConsoleClient.from_settings` của phần mềm: phạm vi chỉ đọc, hai loại lệnh cố định, khoảng 3 lệnh.
   - Chỉ in loại thuộc tính, ngày, trạng thái `metadata`, số dòng, số dòng bị bỏ, `truncated`, số lệnh. Viết toàn chữ không dấu, vì PowerShell 5.1 gửi chữ qua ống bằng ASCII.
   - Lá Chắn đọc trước buổi.
2. **Ca 0 bước 1**: đếm người dùng Search Console theo quyền trước buổi, để ca 8 có cái so.
3. **Hai bước tùy chọn:**
   - tab thứ hai trong lúc lấy số liệu → «đang lấy ở tab khác» (LC-T120-22);
   - thử «Tìm thuộc tính» khi API chưa bật (T-121 B4 (c)). Kịch bản dặn rõ: không tắt API để thử.
4. **Ca 5 dùng khoảng ngày tùy chỉnh** đúng kỳ 28 ngày của phần mềm, không dùng «28 ngày qua» của Search Console. Lý do: ngày mới nhất có thể là dữ liệu sơ bộ, trong khi phần mềm chỉ tính số đã chốt.

## Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ (script đối chiếu kịch bản với code: lõi theo main, giao diện theo team/T-125)   tổng: 217 thiếu/sai: 0
$ (script kiểm đoạn lệnh ca 7, không gọi mạng)                                     thiếu/sai: 0 (24 điểm)
$ (chạy thử đoạn lệnh: không .env, gỡ biến Google, proxy chết)
DUNG: SearchConsoleError WORDPRESS_URL chưa khai báo hoặc không dùng được để lấy số liệu Search Console (…)
$ PYTHONUTF8=1 uvx detect-secrets scan docs/team/reports/T-133-kich-ban-thu-that-google.md docs/team/reports/T-133-thu-ky.md
  "results": {}
```

- **Script đối chiếu (217 điểm):**
  - 97 câu, nhãn trích có cả trong code lẫn trong kịch bản;
  - 3 câu có số, dựng lại từ hằng của code: `MSG_ALL_INSIDE`, `_MSG_BUDGET`, `MSG_LISTED`;
  - menu «📈 Theo dõi», nhãn quyền;
  - các số trong kịch bản: trần 20 lệnh, chặn bấm lại 10 phút, đoạn ≤ 31 ngày, 25.000 dòng;
  - «16 đoạn + 2 kỳ từ khóa = 18 lệnh» tính bằng chính `_fetch_start`, `_chunk_end`, `_default_periods` của `refresh.py`, ở 4 ngày khác nhau (có ngày 29/02);
  - không email, không `.json`, không tên miền thật.
- **Đoạn lệnh ca 7:**
  - bản trong kịch bản giống hệt bản đã kiểm, toàn ASCII, cú pháp đúng;
  - tên hàm, thuộc tính có thật;
  - khoảng ngày hợp khuôn: Q1 31 ngày ≤ 31, Q2 28 ngày ≤ 93, trong 16 tháng;
  - chạy thử thì dừng gọn bằng câu báo cố định, không traceback, không gọi mạng.
- `detect-secrets` có mồi đối chứng: bản chép có thêm khóa giả, quét từ chính thư mục nháp, thì bị bắt.
- Không chạy pytest, ruff (chỉ thêm tài liệu).

## Rủi ro và điểm cần chú ý

- **Số lệnh chính xác của lần bấm đầu không đo được trên màn hình.** Kịch bản dùng dấu hiệu thay thế: không có câu «Đã gửi đủ 20 lệnh…» nghĩa là ≤ 20 lệnh. Con số dự kiến 18 tính từ code. Muốn số chính xác thì cần màn hình hiện `RefreshReport.requests` (việc của giao diện, ngoài phạm vi phiếu này).
- **Tên thô của trường `metadata` không đọc được.** Client nhận cả `first_incomplete_date` lẫn `firstIncompleteDate`, nên `ok` chỉ cho biết Google trả một trong hai. Lá Chắn cần đúng tên thì phải có đoạn lệnh đọc JSON thô; tôi không đưa vào, để đoạn lệnh chỉ dùng hàm công khai của client.
- **Đoạn lệnh ca 7 gọi Google thật ngoài giao diện** (cùng client, chỉ đọc). Lá Chắn nên duyệt trước buổi; không duyệt thì bỏ ca 7, các ô (4), (7) ghi «chưa làm».
- **T-125 chưa gộp `main`.** Soi Lỗi, Lá Chắn có thể đổi tên nút. Trước buổi thử nên chạy lại script đối chiếu trên `main` đã gộp; tôi giữ script trong thư mục nháp, chạy lại được khi Chỉ Huy giao.
- **Nhãn Search Console chưa thấy trên giao diện thật:** «Tùy chỉnh» trong bộ lọc ngày, ô lọc bảng, nút thêm bộ lọc. Đã ghi kèm tên tiếng Anh và «(tên theo giao diện Search Console)».
- **Tài khoản dịch vụ có thể chưa có.** Theo `TIEN-DO.md`, chủ dự án tạo tài khoản dịch vụ «khi tới bước thử thật». Mục 3.1 đặt việc này làm điều kiện trước buổi.

## Câu hỏi cho chủ dự án

Không có. Việc phía Google (bật API, thêm email quyền «Hạn chế») đã có trong README mục 15; kịch bản mục 3.1 nhắc lại.

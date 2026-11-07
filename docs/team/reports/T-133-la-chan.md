# Biên bản bảo mật T-133 · Kịch bản buổi thử thật Google Search Console · rút gọn

> **Model:** Claude **Opus 5.5** (dòng «You are powered by»: Opus 5.5). Chỉ Huy B giao chạy Opus 5.5; chủ dự án 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus 5.5, ghi rõ model.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-133](../tickets/T-133-kich-ban-thu-that-google.md) · [kịch bản](T-133-kich-ban-thu-that-google.md) · [báo cáo Thư Ký](T-133-thu-ky.md) |
| Phạm vi | Rút gọn, chỉ đọc: `team/T-133` tại `d8410c6` (từ `main` cục bộ `e25afa1`), 2 file tài liệu: kịch bản (300 dòng), báo cáo Thư Ký. Đối chiếu: điều kiện thử thật của Lá Chắn T-121 (phần B mục 4), T-124 (phần B mục 3), T-126 (ghi nhận N1, N2, N4); `seo_app/google/search_console.py` trên `main`; câu báo, tên nút trên `team/T-125` (`216ff2f` và đầu nhánh `1c55e9e`) |
| Máy | Windows 11 Pro, uv 0.13.4 (đạt ngưỡng `uvx`, T-078). Không gọi Google, không gọi website, không chạy pytest (theo giao việc) |
| Ngày | 2026-11-07 (08:33–08:38, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Đủ mọi điều kiện thử thật đã đặt. Không lộ bí mật; có bước dọn; có bảng kết quả 19 dòng. **Đoạn lệnh ca 7: Lá Chắn duyệt, chạy được** (mục 2). 4 ghi nhận không bắt buộc (mục 4). **Gộp `main` được ngay** |

## Tóm tắt (cho chủ dự án)

- **Kịch bản đủ và an toàn.** Buổi thử chỉ đọc: không đăng bài, không sửa gì trên Search Console, Google Cloud hay website. Gặp lỗi 403 thì dừng và hỏi, **không nâng quyền**.
- Kịch bản kiểm đủ những gì Lá Chắn cần trước khi cho dùng trang 📈 Theo dõi:
  - tài khoản phần mềm chỉ có quyền «Hạn chế» mà vẫn đọc được số liệu;
  - số liệu khớp Search Console;
  - lần lấy đầu không vượt 20 lệnh, bấm lại ngay thì bị chặn;
  - «Người dùng và quyền» trên Search Console không đổi sau buổi thử.
- **Không ghi bí mật:** không email tài khoản dịch vụ, không file khóa, không mã project, không thuộc tính đầy đủ.
- **Đoạn lệnh ở ca 7** (Chỉ Huy dán vào PowerShell để đo vài số cho Lá Chắn): tôi đã đọc từng dòng. Đoạn lệnh dùng đúng phần chỉ đọc của phần mềm, gửi khoảng 3 lệnh, chỉ in số đếm và ngày, không in gì riêng tư. **Được chạy.**
- **Việc của anh/chị:** trước buổi, làm README mục 15 bước 1–3 nếu chưa làm.

## 1. Đủ các điều kiện thử thật đã đặt chưa: **đủ**

| Điều kiện | Nguồn | Kịch bản |
|---|---|---|
| Quyền «Hạn chế» đọc được `sites` và `query` | T-121 B4 (a); T-124 B.3; T-126 N1 (chưa xác minh) | Ca 1 (cột **Quyền** = Hạn chế, «✔ dùng được») + ca 2 («Tài khoản dịch vụ thấy thuộc tính này, quyền «Hạn chế».», «Có số liệu đã chốt tới hết ngày…»). Bảng (2) |
| Gặp 403 không nâng quyền | T-120 `:124`; T-121; README mục 15 | Quy tắc 3; mục 5 dòng 403: «Không nâng quyền… dừng buổi thử, hỏi chủ dự án và Lá Chắn». Lỗi 401: «Không tạo khóa mới trong buổi» |
| `metadata` thật của đoạn mới nhất và một đoạn cũ; tên trường | T-121 B4 (b); T-124 B.3 | Ca 7: «Q1 moi nhat» (31 ngày tới hôm nay, `dataState=all`) và «Q1 cu» (cách 3–4 tháng), ghi `ok` / `missing` / `bad` kèm ngày tạm đầu. Bảng (4) ×2. Mục 8: đoạn mới nhất `missing` hay `bad` thì mở phiếu nhỏ, đúng như T-124 B.3 |
| `dropped` của Q1, Q2 với website thật; cỡ câu trả lời | T-121 B4 (d); T-124 B.3 | Ca 3 (câu «… dòng số liệu không đúng dạng bị bỏ.») + ca 7 (`bo`, `dong`, `cham tran` của 3 lần gọi). Bảng (7). Mục 8: Lá Chắn xét lại luật 10% |
| Số lệnh của lần bấm đầu ≤ 20 | T-124 B.3 | Ca 3: không có câu `_MSG_BUDGET` thì ≤ 20; code dự kiến 18 (16 đoạn + 2 kỳ). Bảng (8). Xem ghi nhận G4 |
| Bấm lại ngay bị chặn | T-120 bước 5 | Ca 4: «Vừa lấy số liệu lúc …», trả lời ngay, 0 lệnh. Thêm phần tùy chọn: tab thứ hai bị chặn bằng khóa (LC-T120-22) |
| «Người dùng và quyền» không đổi | T-120 bước 6 | Ca 0 (đếm theo quyền, không chép email) + ca 8 (so lại; tùy chọn: sơ đồ trang web không có mục mới) |
| Mã lý do 403 khi chưa bật API, khi hết hạn mức | T-121 B4 (c) | Mục 3.1: chỉ khi tới buổi mà API chưa bật thì chạy ca 1 trước khi bật. «**Không tắt API để thử**» (đúng quy tắc chỉ đọc). Hết hạn mức: ghi nếu gặp. Bảng (9). Xem ghi nhận G3 |
| Chỉ thêm email vào đúng thuộc tính của website | T-126 N2 | Mục 3.1 («không thêm vào thuộc tính bản thử»); ca 1 ghi dòng «✘ …»; dọn bước 3: gỡ email khỏi thuộc tính thừa |
| Biến môi trường `GSC_SITE_URL` đè `.env` | LC-T120-23 | Ca 0 bước 3: có câu cảnh báo thì dừng |

## 2. Đoạn lệnh ca 7 (gọi Google thật ngoài giao diện): **duyệt, được chạy**

Tôi đọc từng dòng (`T-133-kich-ban-thu-that-google.md:196-216`) và đối chiếu với `seo_app/google/search_console.py` trên `main`:

- **Chỉ đọc, đúng client của phần mềm.** `SearchConsoleClient.from_settings` (`:423-452`) kiểm `WORDPRESS_URL`, thuộc tính phủ website, rồi nạp file khóa với **một** phạm vi `webmasters.readonly`. Lệnh gửi qua `_send` và bộ kiểm `_check_call` (`:637`), chỉ hai khuôn lệnh cố định của client; lệnh ghi không có đường nào để gửi.
- **Tên hàm, thuộc tính có thật:** `site.kind`, `fetch_day_page` (`:491`), `fetch_page_query` (`:495`), `request_count` (`:420`), các trường `SearchResult` `rows`, `dropped`, `truncated`, `first_incomplete_date`, `metadata` (`:267-272`).
- **Khoảng ngày hợp lệ** theo `_body` (`:595-604`): ngày cuối không sau hôm nay; Q1 = 31 ngày (trần 31); Q2 = 28 ngày (trần 93); ngày đầu trong 486 ngày. Tổng 3 lệnh (cộng lật trang nếu một đoạn quá 25.000 dòng), dưới trần 20 của client.
- **Chỉ in:** loại thuộc tính, ngày, trạng thái `metadata`, số dòng, số dòng bị bỏ, cờ chạm trần, số lệnh. Không in dòng số liệu, địa chỉ trang, từ khóa, email hay thuộc tính đầy đủ.
- **Khi lỗi:** in `type(exc).__name__` và câu lỗi. Lỗi của chính phần mềm (`SearchConsoleError`, `ServiceAccountError`, `ConfigError`) đều là câu cố định. Câu của `ServiceAccountError` không có đường dẫn hay tên file. Câu của `ConfigError` chỉ có tên loại lỗi hay giá trị `APP_TIMEZONE`. Lỗi mạng và lỗi xin mã đã được client gói thành câu cố định.
- **Không ghi gì:** không đụng bản lưu tạm (`search_cache`), không ghi `.env`.
- **Chạy được bởi Chỉ Huy (AI):** đoạn lệnh đọc `.env` trong tiến trình Python nhưng không in giá trị nào, nên đúng luật «không đọc `.env`, không in khóa».

Thư Ký đã chạy thử khi không có `.env`: dừng gọn bằng câu cố định, không gọi mạng.

## 3. Bí mật, dọn, bảng kết quả: **đạt**

- **Không lộ bí mật:**
  - Quy tắc 1: không ghi file khóa, email tài khoản dịch vụ, mã project. Thuộc tính chỉ ghi **loại**; tên máy ngoài website chỉ ghi **dạng**.
  - Cấm chụp `.env`, khung 🔑, bảng «Tìm thuộc tính», trang tài khoản dịch vụ trong Google Cloud.
  - Bản thân kịch bản và báo cáo Thư Ký: detect-secrets sạch. Grep diff: địa chỉ duy nhất là trang công khai `https://search.google.com/search-console`; không email, không tên miền thật, không `.json`, không đường dẫn máy.
- **Chỉ đọc** (quy tắc 2): không gửi sơ đồ trang web, không yêu cầu lập chỉ mục, không xóa URL, không đổi cài đặt Google Cloud.
- **Điểm dừng** (quy tắc 8): đủ 6 câu lạ của client (lệnh ngoài danh sách, phạm vi sai, chuyển hướng, SSL, dữ liệu sai dạng, quá 10% dòng lạ), kèm trường hợp thấy Search Console có thay đổi. Cả 6 câu có nguyên văn trong `search_console.py`.
- **Dọn** (mục 6, 7 bước):
  - giữ thuộc tính đã lưu và bản lưu tạm, vì đây là dữ liệu dùng thật, không phải dữ liệu thử;
  - chỉ xóa bản lưu tạm khi cần;
  - gỡ email tài khoản dịch vụ khỏi thuộc tính thừa hay staging;
  - kiểm lại quyền «Hạn chế»;
  - đóng PowerShell, không lưu đầu ra vào thư mục phần mềm;
  - đóng tab thứ hai;
  - soát ảnh chụp.
- **Bảng kết quả** (mục 7, 19 dòng): đủ ô cho mọi điều kiện ở mục 1, kèm dòng «Câu báo» và «Dọn». Mục 8 nêu Lá Chắn làm gì với từng kết quả xấu.
- **Tên nút:** kịch bản theo `team/T-125` `216ff2f`, có dặn «gộp xong mà khác thì theo giao diện». Tôi đối chiếu 11 câu, nút quan trọng (cảnh báo hạ quyền, biến môi trường đè, «Vừa lấy số liệu lúc», khóa tab khác, «Xóa bản lưu tạm», «Đã lưu thuộc tính…», «Tài khoản dịch vụ thấy thuộc tính này, quyền», «Sắp có (T-127)», «Tìm thuộc tính», «Lấy số liệu mới», «Lưu thuộc tính đã chọn»): có cả ở `216ff2f` lẫn đầu nhánh hiện tại `1c55e9e`.

## 4. Ghi nhận (không tính lỗi, không bắt buộc)

- **G1 · đoạn lệnh ca 7, phòng xa:** chỉ in câu lỗi khi lỗi thuộc ba loại của phần mềm. Lỗi khác thì chỉ in tên loại, ví dụ:

  ```python
  except Exception as exc:
      ok = type(exc).__name__ in {"SearchConsoleError", "ServiceAccountError", "ConfigError"}
      print("DUNG:", type(exc).__name__, exc if ok else "")
  ```

  Hôm nay tôi không thấy đường nào để lỗi lạ mang bí mật ra. Sửa này chỉ để chặn trước, khi code đổi về sau.
- **G2 · T-125 chưa gộp:** trước buổi thử, chạy lại script đối chiếu tên nút của Thư Ký trên `main` đã gộp T-125, như Thư Ký đã ghi.
- **G3 · mã lý do 403 (T-121 B4 (c)):** API đã bật sẵn thì phần «chưa bật API» không kiểm được, và **không** nên tắt API để thử. Phần «hết hạn mức» cũng không nên cố tạo ra. Hai ô này để «Chưa làm» là chấp nhận được. Client nhận mã lý do lạ thì rơi về câu 403 chung «… chưa có quyền xem thuộc tính này… kiểm tra đã bật Google Search Console API», tức hướng an toàn: không khuyên nâng quyền.
- **G4 · số lệnh lần đầu:** màn hình không hiện số lệnh, nên kịch bản dùng dấu hiệu thay thế: không có câu «Đã gửi đủ 20 lệnh…» nghĩa là ≤ 20. Đủ cho mục đích bảo mật vì trần 20 nằm trong code, đã có test. Muốn số chính xác thì T-125 hay phiếu sau hiện `RefreshReport.requests`; không bắt buộc.

## 5. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| `uv --version` trước `uvx` | 0.13.4 | ✔ |
| detect-secrets (`PYTHONUTF8=1`; chép 2 file ra thư mục ngoài git cùng file mồi tiếng Việt, `scan --all-files .`) | 2 file: 0 kết quả; file mồi: bị bắt | ✔ |
| Grep diff `d8410c6` (email, link Sheet, `sc-domain:…`, địa chỉ thật, `.json`, đường dẫn máy, khóa) | 0. Chỉ có trang công khai của Search Console | ✔ |
| Đối chiếu đoạn lệnh ca 7 với `search_console.py` (tên hàm, trường, khoảng ngày, lỗi) | Khớp (mục 2) | ✔ |
| Câu, nút trên `team/T-125` (`216ff2f`, `1c55e9e`) | 11/11 có | ✔ |
| Gộp thử với `main` cục bộ `e25afa1` | Nhánh nằm ngay trên `main`, `merge-tree` sạch | ✔ |
| pytest | Không chạy (phiếu chỉ tài liệu, theo giao việc) | — |

## 6. Kết luận

**ĐẠT.** Gộp `main` được ngay. Ca 7 được chạy như kịch bản viết; G1 nên sửa nếu Thư Ký còn sửa kịch bản. Buổi thử làm sau khi T-125 gộp `main`. Sau buổi thử, Lá Chắn đọc bảng mục 7 rồi mới cho dùng trang 📈 Theo dõi (T-121 B4).

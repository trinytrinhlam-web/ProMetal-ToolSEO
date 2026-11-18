# T-139 · Kết quả buổi thử thật Google (kịch bản T-133), 2026-11-18

| Mục | Nội dung |
|---|---|
| Phiếu | [T-139](../tickets/T-139-la-chan-doc-thu-that-google.md) |
| Kịch bản | [T-133-kich-ban-thu-that-google.md](T-133-kich-ban-thu-that-google.md) |
| Làm | Chỉ Huy B (Claude Opus 5.5) cùng chủ dự án, 11:09–13:25 (+07). Chủ dự án thao tác Search Console, Google Cloud, Google Sheet và app; Chỉ Huy hướng dẫn, chạy ca 7 |
| Cho | **Lá Chắn** đọc bảng mục 7 (dưới), kết luận có cho dùng trang 📈 Theo dõi không |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã **nối Google** (tài khoản dịch vụ, Sheet kế hoạch, Search Console) trên máy này.
- Số liệu trang **📈 Theo dõi** **khớp Search Console từng con số**: cả 17 bài, trang so được (click, hiển thị, vị trí), tổng 11 click / 259 hiển thị (28 ngày), và 5 từ khóa của một bài.
- Nút **«Đưa vào kế hoạch»** ghi đúng một dòng vào Google Sheet, chỉ sau khi bấm «Áp dụng».
- Không lỗi, không cảnh báo lạ, quyền trên Search Console không đổi. Có 3 ghi nhận nhỏ (cách làm tròn CTR, tỉ lệ phần ngoài website, chữ trong kịch bản) và một lưu ý SEO (từ khóa mới gần trùng bài cũ).
- Còn chờ Lá Chắn đọc kết quả rồi mới dùng số liệu để quyết định việc gì.

## Chi tiết

- Bắt đầu: 11:09 +07 (chủ dự án chọn «1»). App: main 3202035 (có T-124, T-125, T-136), `config/ai.toml` tạm Gemini Flash (không ảnh hưởng Search Console).
- Mục 3.1 làm ngay trước buổi (10:50–11:05): tạo project, bật Google Sheets API + Google Search Console API, tài khoản dịch vụ không vai trò, khóa JSON để ngoài thư mục phần mềm; `.env` có GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID; Sheet «KeHoach» đã chuẩn bị; email tài khoản dịch vụ thêm vào Search Console quyền «Hạn chế»; chủ dự án đã «Tìm thuộc tính», lưu, «Kiểm tra» (phần 3) → `.env` GSC_SITE_URL loại **tên miền** (`sc-domain:`).
- API bật trước khi thử → bỏ bước tùy chọn 403 «chưa bật API».

## Nhật ký

| Giờ | Ca/bước | Ghi |
|---|---|---|
| ~11:15 | Ca 1, ca 2 | Chủ dự án bấm lại «Tìm thuộc tính» (ảnh, không có email): 1 dòng, loại tên miền, quyền «Hạn chế», «✔ dùng được (tự lọc phần ngoài website)»; ô chọn đã là thuộc tính đó. «Kiểm tra» (ảnh): «Tài khoản dịch vụ thấy thuộc tính này, quyền «Hạn chế».», «Có số liệu đã chốt tới hết ngày 15/11/2026 (ngày theo giờ Google).», «0,8% lượt hiển thị 28 ngày qua nằm ngoài website (danh sách tên máy bên dưới): không tính.» Ca 0 (đếm người dùng) chưa trả lời. |
| 11:16 | Ca 3 | Lấy lần đầu xong lúc 11:16 (ảnh). Khung xanh: «Đã lấy số liệu tới hết ngày 15/11/2026 (ngày theo giờ Google). 2 ngày gần nhất còn là số tạm, chưa tính.» Không câu phụ nào (không dòng bị bỏ, không chạm trần, không «Đã gửi đủ 20 lệnh…», không «Chưa có danh sách bài…»). Dưới nút: «Số liệu tới hết ngày 15/11/2026 (ngày theo giờ Google) · lấy lúc 11:16 18/11/2026» (khớp ca 2). 28 ngày, so kỳ trước: click 11 (↑ +8, +267%), hiển thị 259 (↑ +196, +311%), CTR 4,2% (↓ −0,6 điểm), vị trí 16,2 (↑ lên 5,6 bậc). «Cần chú ý: 17 bài chưa có lượt hiển thị». Thời gian lấy: chủ dự án chưa báo. |
| 11:18 | Ghi nhận nhỏ | CTR kỳ trước suy từ số trên ô: 3/63 = 4,76%; nay 11/259 = 4,25% → chênh −0,51 điểm, app ghi «−0,6 điểm» (có thể lấy hiệu của hai số đã làm tròn 4,8% và 4,2%). Không phải lỗi bảo mật; Lá Chắn/Thợ Máy xét cách làm tròn. |
| 11:20 | Ca 7 | Chỉ Huy chạy đúng đoạn lệnh mục 4 ca 7 trong thư mục phần mềm (`uv run python -`, chỉ đọc). Kết quả: «loai thuoc tinh: domain»; «Q1 moi nhat 2026-10-18 2026-11-17 | metadata: ok | ngay tam dau: 2026-11-16 | dong: 169 | bo: 0 | cham tran: False»; «Q1 cu 2026-07-20 2026-08-19 | metadata: missing | ngay tam dau: None | dong: 6 | bo: 0 | cham tran: False»; «Q2 28 ngay | dong: 23 | bo: 0 | cham tran: False»; «so lenh da gui: 3». |
| ~11:35 | Ca 5 | Chủ dự án gửi 2 ảnh: bảng «Bài / trang» của app (28 ngày, 17 dòng đầu) và Search Console → Hiệu suất → Tùy chỉnh (khoảng 19/10–15/11/2026 theo hướng dẫn), Web, thẻ Trang (25 dòng). So **cả 17 dòng** của app với dòng cùng đường dẫn: click, hiển thị, vị trí **khớp hết** (ví dụ A «Giới Thiệu» 4 / 14 / 2,1 = 4 / 14 / 2,1; B «Cửa sắt bị kẹt…» 1 / 38 / 7,6 = 1 / 38 / 7,6; trang chủ 2 / 18 / 7,1; «Cửa nhôm kính…» 0 / 6 / 67,7). Tổng: cộng các dòng Search Console không có `www.` = 11 click, 259 hiển thị = đúng bốn ô của app (11, 259). Search Console có 2 dòng `www.` (một trang lưu trữ ngày, một trang thẻ; 2 + 2 hiển thị) mà app không tính, và trang lưu trữ tháng, trang thẻ không có `www.` (có tính vào tổng). |
| ~11:45 | Ca 6 (chọn bài) | Bài B không có từ khóa nào (app và Search Console đều trống). Chỉ Huy chạy thêm 1 lệnh chỉ đọc `fetch_page_query` (19/10–15/11) để đếm số từ khóa theo trang (chỉ in đường dẫn trang và số đếm, không in từ khóa): chọn bài «Sửa Cửa Kéo Sắt TPHCM…» (5 từ khóa). |
| ~11:35 | Ghi nhận nhỏ | Ca 2 báo «0,8% lượt hiển thị 28 ngày qua nằm ngoài website»; bảng Trang của Search Console (khoảng tùy chỉnh) có 4 hiển thị ở 2 dòng `www.` trên 263 ≈ 1,5%. Có thể khác khoảng ngày (ca 2 bấm trước khi có số chốt mới?) hay cách đếm; chỉ ghi lại cho Lá Chắn. |

## Bảng mục 7

| Mã | Kết quả | Ghi chú |
|---|---|---|
| (1) | Đạt | API bật, email tài khoản dịch vụ quyền «Hạn chế» trước khi bấm ca 1 (làm ngay trước buổi). Người dùng Search Console (ca 0, chủ dự án đếm): 1 chủ sở hữu, 1 Hạn chế, 1 Toàn quyền («đầy đủ»; chủ dự án: email khác của chính chủ dự án) |
| (2) Tìm thuộc tính | Đạt | 1 dòng: tên miền · Hạn chế · ✔ dùng được (tự lọc phần ngoài website); không cảnh báo quyền cao; không mục bị bỏ |
| (2) Lưu | Đạt | Lưu ở phần 3 (trước buổi); loại tên miền; không cảnh báo biến môi trường (chủ dự án không báo) |
| (2) Kiểm tra | Đạt | Quyền «Hạn chế»; ngày chốt cuối 15/11/2026 (giờ Google); 0,8% lượt hiển thị 28 ngày ngoài website, không tính (dạng tên máy: chưa hỏi) |
| (3) Lấy lần đầu | Đạt | Khung xanh; ngày chốt cuối 15/11/2026 (khớp ca 2); 2 ngày tạm; không câu phụ; lấy lúc 11:16; thời gian lấy chưa ghi |
| (8) Số lệnh | Đạt | Không có «Đã gửi đủ 20 lệnh…»; 1 lần bấm là đủ |
| (5) Bấm lại | Đạt | ~11:20 (trong 10 phút sau ca 3), ảnh: khung xanh dương «Vừa lấy số liệu lúc 11:16 18/11/2026; Google cập nhật khoảng một lần mỗi ngày nên chưa có gì mới. Để sau rồi bấm lại.»; dòng dưới nút giữ «lấy lúc 11:16» |
| Tab khác (tùy chọn) | Chưa làm | Bỏ bước tùy chọn (một tab) |
| (3) Bài A | Đạt | «Giới Thiệu» (trang): app 4 click / 14 hiển thị / vị trí 2,1; Search Console 4 / 14 / 2,1. Khoảng 19/10–15/11/2026 |
| (3) Bài B | Đạt | «Cửa sắt bị kẹt, khó đóng mở, cong vênh…» (bài): app 1 / 38 / 7,6; Search Console 1 / 38 / 7,6. Không trang nào ≥ 100 hiển thị; chọn trang nhiều hiển thị nhất |
| (3) Tổng (tùy chọn) | Đạt | Cả 17 dòng đầu của app khớp từng dòng; tổng 11 click / 259 hiển thị khớp tổng các dòng Search Console không `www.` |
| (10) Từ khóa | Đạt | Lần 2, bài «Sửa Cửa Kéo Sắt TPHCM…» (5 từ khóa, chọn theo lệnh đếm chỉ đọc 1 lệnh của Chỉ Huy): cả 5 từ khóa app = Search Console (click / hiển thị / vị trí: 0/6/68,0 · 0/3/66,0 · 0/3/77,7 · 0/2/68,0 · 0/1/52,0); 2 dòng «từ khóa mới». Tổng bài 1 / 27 / 41,8 khớp; cộng từ khóa 0 click, 15 hiển thị < tổng bài (Google ẩn từ khóa hiếm), đúng. Lần 1, bài B «Cửa sắt bị kẹt…»: app «Chưa có từ khóa nào của bài này trong khoảng đang xem.», «Không có từ khóa nào đưa vào kế hoạch được…»; Search Console lọc Trang = đường dẫn bài, thẻ Cụm từ: «Không có dữ liệu» (tổng 1 / 38 / 2,6% / 7,6 khớp app). Biểu đồ tuần của app: 1 click tuần tới 15/11; vị trí 5,0 (tuần tới 08/11), ~8,7 (tuần tới 15/11) |
| (11) Đưa vào kế hoạch | Đạt (2 ghi nhận) | 13:20, bài «Sửa Cửa Kéo Sắt TPHCM…», 28 ngày. Ô chọn: 5 từ khóa, đủ cả 5 (0 bị để ngoài; không có dòng «… không có trong ô chọn…»); ô có mục «Select all» của Streamlit. Chủ dự án chọn 1 → «➕ Đưa vào kế hoạch» → trang Kế hoạch, khung «Đề xuất thay đổi»: ghi chú «Từ khóa chọn ở trang «📈 Theo dõi» (Search Console): duyệt rồi mới ghi vào Sheet.»; 1 dòng: Loại «Thêm», Mã bài B-001 (Sheet trống), Thay đổi «Bài mới», Lý do «Từ khóa người tìm trên Google đã đưa tới website (Search Console).», không ⚠️, ô «Dòng 1: Thêm B-001» tick sẵn. Trước «Áp dụng»: Sheet chưa có dòng nào (chủ dự án F5). «✅ Áp dụng thay đổi (1)» → «Đã ghi 1 thay đổi.» Sheet: đúng 1 dòng B-001, từ khóa đúng, «Chưa viết», «Cập nhật lúc» 2026-11-18 13:20+07:00, các cột khác trống. «Hủy» (tùy chọn): chưa làm. **Ghi nhận 1:** bảng đề xuất không có cột «Nguồn» như kịch bản ghi; nguồn nằm trong ô «Lý do» (Thư Ký sửa kịch bản/README nếu cần). **Ghi nhận 2:** từ khóa đã chọn gần trùng chủ đề bài đã đăng «Cửa sắt bị kẹt, khó đóng mở, cong vênh…» nhưng không có ⚠️ (app so trùng theo từ khóa/slug, không theo ý); báo chủ dự án nguy cơ hai bài giành nhau |
| (4) `metadata` mới nhất | Đạt (`ok`) | Ngày tạm đầu 16/11/2026 (khớp «2 ngày gần nhất còn là số tạm» và ngày chốt 15/11) |
| (4) `metadata` cũ | `missing` (bình thường) | Đoạn 20/07–19/08/2026 đã chốt cả |
| (7) Dòng bị bỏ | Đạt (0 dòng bị bỏ) | Lần lấy đầu không có câu dòng bị bỏ. Ca 7: Q1 mới nhất 169 dòng, bỏ 0, không chạm trần; Q1 cũ 6 dòng, bỏ 0; Q2 23 dòng, bỏ 0; 3 lệnh |
| (9) 403, 429 | Không gặp | API bật trước buổi nên không thử câu «chưa bật API»; không 403, 429 nào trong buổi |
| (6) Người dùng và quyền | Đạt | ~13:25, chủ dự án: «không có gì thay đổi» (vẫn 1 chủ sở hữu, 1 Hạn chế, 1 Toàn quyền) |
| Câu báo | Đạt | Mọi câu thấy trong buổi là câu tiếng Việt cố định; không lộ email, đường dẫn máy, lời máy chủ (ảnh chủ dự án gửi không có email) |
| Dọn | Đạt (1 dòng chờ chủ dự án) | 1 giữ thuộc tính, bản lưu tạm; 2 không xóa bản lưu tạm; 3 không có dòng «✘»; 4 không phải hạ quyền; 5 Chỉ Huy chạy ca 7 bằng Bash trong thư mục phần mềm, không lưu đầu ra vào đó; 6 không mở tab thứ hai; 7 dòng B-001: chủ dự án quyết giữ hay tự xóa (gợi ý bổ sung bài cũ thay vì bài mới); 8 ảnh chụp chỉ nằm trong cuộc trò chuyện, không trong thư mục dự án |

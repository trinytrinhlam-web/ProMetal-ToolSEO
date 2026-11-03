# T-120 · Thiết kế Giai đoạn 6: theo dõi bài qua Google Search Console

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-03 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình (mở đường cho cả giai đoạn) |
| Phụ thuộc | Không (chỉ tài liệu) |
| Trạng thái | Xong (gộp `main` 2026-11-03) |

## Mục tiêu

Một báo cáo thiết kế đủ để chia Giai đoạn 6 thành các phiếu code nhỏ, giống T-094 (Giai đoạn 5): theo dõi từng bài đã đăng qua Google Search Console (từ khóa, vị trí trung bình, lượt hiển thị, lượt click, CTR) và đưa số liệu về chỗ người dùng xem được.

## Bối cảnh

- `CLAUDE.md`: Lộ trình Giai đoạn 6 (chủ dự án chốt 2026-10-15 **giữ**; giao diện demo chưa có trang này; **vị trí trong menu phải hỏi chủ dự án**), quyết định đã chốt (dữ liệu dùng chung trên WordPress và Google Sheets, service account Google trong `.env`).
- `docs/plan/bang_dieu_khien_theo_doi_vi.md` (bảng điều khiển theo dõi), `docs/plan/review_ke_hoach_v1.md` (thuộc tính staging trong Search Console, chưa có nguồn số liệu từ khóa), `docs/plan/README.md`.
- Giai đoạn 5 đã có: lớp Google (`seo_app/google/**`, service account, `google-auth`, chia sẻ Sheet), trang Kế hoạch, lõi ghi trạng thái website về Sheet (T-109, T-113), cột link bài trên Sheet.
- `docs/team/security.md` và biên bản Lá Chắn T-116 nhóm 4 (Google Sheets, kế hoạch).

## Phạm vi

- **Được sửa:** chỉ báo cáo `docs/team/reports/T-120-tho-may.md`. Không sửa code, cấu hình, test.
- Được đọc mã nguồn và tài liệu công khai của Search Console API (`searchanalytics.query`, `sites.list`, URL Inspection nếu cần). **Không** gọi Google thật hay website thật.

## Yêu cầu

1. Luồng người dùng: kết nối thuộc tính Search Console (tên miền hay tiền tố URL, cách thêm tài khoản dịch vụ làm người dùng của thuộc tính, quyền tối thiểu chỉ đọc), lấy số liệu theo từng bài (khớp URL bài với dòng kế hoạch / bài WordPress), xem theo khoảng ngày, so hai kỳ, đánh dấu bài tụt hạng hay chưa có lượt hiển thị.
2. API: phạm vi OAuth chỉ đọc (`webmasters.readonly`), có cần thư viện mới không (nêu tên, lý do, phương án dùng `google-auth` + HTTP như lớp Sheets hiện có; **thêm thư viện cần chủ dự án duyệt**), giới hạn số dòng/hạn mức API, độ trễ số liệu 2–3 ngày, múi giờ, lọc đúng thuộc tính chính (không lẫn staging).
3. Lưu số liệu: cache SQLite hay ghi Google Sheets (trang tính riêng?), giữ bao lâu, làm mới khi nào (nút bấm, không chạy ngầm), dung lượng.
4. Giao diện: đề xuất **2–3 phương án vị trí trong menu** (trang mới, tab trong trang Kế hoạch, cột trong trang Bài viết…) kèm phác thảo chữ; không tự chọn, để câu hỏi cho chủ dự án.
5. Chia phiếu (khoảng 3–6 phiếu nhỏ, có thứ tự và phụ thuộc, phiếu nào chạy song song được), ước lượng độ lớn.
6. Câu hỏi cho chủ dự án (đánh số, mỗi câu có lựa chọn A/B và khuyến nghị), gom ở cuối báo cáo; câu đầu tiên là vị trí trong menu.

## Yêu cầu bảo mật riêng

Đọc `docs/team/security.md`; nêu rủi ro từng phần: bí mật service account (dùng lại file khóa hiện có, không thêm khóa thứ hai nếu tránh được), chữ từ Search Console (truy vấn tìm kiếm của người lạ) là dữ liệu chưa tin cậy khi hiện lên giao diện, ghi Sheet, hay đưa vào lời dặn AI; không lộ số liệu ra ngoài máy.

## Tiêu chí xong

- [ ] Yêu cầu 1–6
- [ ] Báo cáo nộp tại `docs/team/reports/T-120-tho-may.md`, có phần «Tóm tắt (cho chủ dự án)» lời thường

## Kiểm thử và kiểm định

- Soi Lỗi: Không (chỉ tài liệu). Lá Chắn: Rút gọn (đọc thiết kế, góp điều kiện bảo mật cho các phiếu code).

## Ghi chú của Chỉ Huy

- Lập 2026-11-03 theo chỉ đạo của chủ dự án «tạm thời mở mức tối đa cho các Agent để dùng hết hạn mức 5h» và Lộ trình Giai đoạn 6. Làm trong worktree `wt-T-120` (nhánh `team/T-120` từ `main` `29499dd`).
- 2026-11-03 23:10 (Chỉ Huy B): Thợ Máy `3a2e9f7`; Lá Chắn rút gọn (Opus tạm, Fable hết hạn mức tuần) **ĐẠT** (`334edf1`), 24 điều kiện LC-T120-1 → -24 đã chép vào T-121, T-122, T-123 (T-124 → T-127 chép khi lập). Gộp `main`. Lập đợt 1: T-121, T-123 giao ngay, T-122 khi máy rảnh. 7 câu hỏi gửi chủ dự án; trong lúc chờ làm theo khuyến nghị. Ghi nhận FAQ (kết quả FAQ không còn hiện trên Google từ 05/2026) hỏi chủ dự án.

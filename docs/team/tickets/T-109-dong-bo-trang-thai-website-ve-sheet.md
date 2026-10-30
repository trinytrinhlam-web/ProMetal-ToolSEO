# T-109 · Lõi: đưa trạng thái bài trên website về Google Sheets (nút «Cập nhật trạng thái từ website»)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-30 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-099, T-100 đã gộp (`post_statuses`, đồng bộ kế hoạch) |
| Trạng thái | Đang làm |

## Mục tiêu

Một hàm lõi nhận kết quả `post_statuses` (trạng thái các bài trên website) và kế hoạch đang đọc, trả về danh sách thay đổi cần ghi vào Sheet (trạng thái, lỡ lịch) để giao diện cho người dùng xem rồi bấm ghi; ghi qua đúng đường đồng bộ của T-100.

## Bối cảnh

- Thiết kế T-094 mục 1.7 «Cập nhật trạng thái từ website» (`docs/team/reports/T-094-tho-may.md`).
- Họa Sĩ T-101 (30/10) báo lõi chưa có hàm đổi kết quả `post_statuses` thành lệnh ghi Sheet; Chỉ Huy đồng ý T-101 chỉ làm phần đọc (cột «Trên website», nhãn «Lỡ lịch», không ghi Sheet), phần ghi để phiếu này.

## Phạm vi

- **Được sửa:** `seo_app/plan/sync.py` (hoặc mô-đun mới trong `seo_app/plan/`), test.
- **Không được sửa:** `seo_app/wordpress/**`, `seo_app/google/**`, `app/**`.

## Yêu cầu

1. Hàm thuần (không mạng) so trạng thái website với dòng kế hoạch theo Mã bài / mã bài WordPress đã nối (T-100), trả danh sách thay đổi có kiểu rõ ràng (ô nào, giá trị cũ → mới, lý do); không đề xuất gì cho dòng không nối được.
2. Ghi qua đường ghi của T-100 (luôn `RAW`, so mã băm Sheet, `unsure` không ghi lại, không thêm dòng); không đổi cột ngoài cột trạng thái đã thiết kế.
3. Dữ liệu từ website và từ Sheet là dữ liệu chưa tin cậy (LC-T094 «Chung»).
4. Test: bài đã đăng, đã hẹn giờ, lỡ lịch, bị xóa / vào thùng rác, không còn quyền đọc, mã lạ; Sheet đổi giữa chừng.

## Yêu cầu bảo mật riêng

Theo `docs/team/reports/T-094-la-chan.md` mục «Chung» và mục T-100 (đồng bộ).

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-109-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-30 theo đề xuất Họa Sĩ T-101 (ranh giới giao diện / lõi). Nối nút ghi vào trang Kế hoạch ở lượt sau của T-101 hoặc ở T-102.
- 2026-10-30 22:24 (Chỉ Huy B): giao 20:25 cho phiên Thợ Máy T-094 (người viết thiết kế 1.7). Nhánh `team/T-109`, worktree `wt-T-109`, từ `main` `eef13b5` (có T-101). Lưu ý điều kiện LC-T101-1 (ô mở đầu `=`, `+`, `-`, `@`) khi ghi Sheet hay hiện bảng.

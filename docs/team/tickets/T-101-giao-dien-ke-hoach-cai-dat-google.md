# T-101 · Giao diện: trang Kế hoạch, Cài đặt → Google, trang Bài viết (thay demo, giữ bố cục đã duyệt)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (đợt 3) |
| Phụ thuộc | T-100, T-103 đã gộp |
| Trạng thái | Xong (gộp `main` 2026-10-30) |

## Mục tiêu

Làm phần **T-101** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-101) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-101 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `app/views/` (trang Kế hoạch, Cài đặt, Bài viết), `seo_app/demo.py` (phần mẫu không còn dùng), test.
- **Không được sửa:** `seo_app/**` trừ `demo.py`, `config/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-101 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-101-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 23:14 (Chỉ Huy B): góp ý G4 của Soi Lỗi T-103: dữ liệu mẫu trang Kế hoạch demo (`seo_app/demo.py`) dùng trạng thái «Sẵn sàng», không thuộc danh sách nhãn của `PlanRow`; khi thay demo bằng dữ liệu thật đừng dùng lại nhãn đó.
- 2026-10-30 11:00 (Chỉ Huy B): điều kiện Lá Chắn T-100 (mục 5): hiện chữ Sheet, `Conflict.now` bằng chữ thuần (LC-T094-3); giữ `listing.plan` (bản người dùng đã xem) trong `session_state` tới lúc «Áp dụng»; không tự dựng `Proposal` ngoài `compare_rows` / `from_ai`. LC-T100-1 (vùng đọc đầy), LC-T100-2 (cảnh báo giá) phải xong ở T-100 lượt 2 trước khi nối «Áp dụng» và hiện đề xuất AI tick sẵn.
- 2026-10-30 17:23 (Chỉ Huy B): T-100, T-103 đã gộp. Nhánh `team/T-101` từ `main` `fd28bbc`, worktree `wt-T-101`; giao Họa Sĩ (phiên Họa Sĩ T-084). Ranh giới (Họa Sĩ hỏi, Chỉ Huy chọn A): nút «Viết bài» trên dòng kế hoạch dùng khóa `write.py` có sẵn (`_open_draft`, `_start_keyword`) và khóa mới `_start_plan_key`, `open_row` chỉ đọc Sheet, không gửi WordPress (LC-T094-35); T-102 đọc `_start_plan_key` để gắn `DraftPlanRef`. «Cập nhật trạng thái từ website»: T-101 chỉ làm phần đọc; phần ghi Sheet → T-109.
- 2026-10-30 19:59 (Chỉ Huy B): Họa Sĩ `6b0c785`; Soi Lỗi ĐẠT (`164c58a`, 0 lỗi; G1 `_start_plan_key` → T-102); Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (`18756ae`, LC-T101-1 Thấp: nút tải CSV không trung hòa ô `=…` → sửa ở T-102). Khi T-102 gộp nhánh này, lộ 21 ca `tests/test_soi_loi_t103.py` (đã ở `main`) dùng `demo.plan_rows`, `demo.PLAN_PASTE_EXAMPLE` mà T-101 đã xóa (Soi Lỗi, Lá Chắn chỉ chạy test chọn lọc nên không thấy). R5 Chỉ Huy duyệt 30/10 19:50: chép mẫu thành hằng trong file test, ý test giữ nguyên; Họa Sĩ sửa trên `team/T-101`, rồi Chỉ Huy gộp sau toàn bộ test.
- 2026-10-30 22:24 (Chỉ Huy B): sửa test `test_soi_loi_t103.py` trên nhánh (`944160c`, R5). Gộp `main` (`4594f06`, cùng T-107 lượt 3, T-110 lượt 1; `eef13b5` bỏ import thừa sau gộp). Windows 21.539 test qua, 0 hỏng. LC-T101-1 đã sửa ở nhánh T-102 (chờ Lá Chắn đầy đủ T-102 đóng).

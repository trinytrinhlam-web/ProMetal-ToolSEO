# T-102 · Bước Xuất bản thật: màn hình xác nhận, hẹn giờ, đăng ngay (công tắc mặc định tắt tới khi thử thật)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (đợt 3) |
| Phụ thuộc | T-096, T-099, T-100 đã gộp |
| Trạng thái | Đang làm (gộp T-101 vào nhánh) |

## Mục tiêu

Làm phần **T-102** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-102) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-102 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `app/views/write.py` (bước Xuất bản), `seo_app/demo.py`, test.
- **Không được sửa:** `seo_app/**` trừ `demo.py`, `config/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-102 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-102-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Đầy đủ.

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-30 11:00 (Chỉ Huy B): điều kiện Lá Chắn T-100 (mục 5): gọi `find_plan_draft` với mã băm Sheet đang dùng; chỉ gọi `record_status` sau khi T-100 lượt 2 sửa LC-T100-3 (so mã băm Sheet của nháp trước khi ghi trạng thái).
- 2026-10-30 17:23 (Chỉ Huy B): T-101 đặt `_start_plan_key` (Mã bài) khi bấm «Viết bài» trên dòng kế hoạch chưa có nháp; T-102 đọc khóa này trong `write.py` để gắn `DraftPlanRef`, điền các ô còn lại (hợp đồng chi tiết trong báo cáo `T-101-hoa-si.md`).
- 2026-10-30 17:23 (Chỉ Huy B): T-099 lượt 2 qua Lá Chắn (`38613fe`, T-102 nối màn hình xác nhận được). Nhánh `team/T-102` từ `main` `fd28bbc` + T-099 lượt 2 (`c8986da`), worktree `wt-T-102`; giao Họa Sĩ (phiên Họa Sĩ T-056). Giữ điều kiện Lá Chắn T-099 (Điều kiện 2 lượt 1, L2-1 → L2-3); công tắc Hẹn giờ/Đăng ngay mặc định tắt (LC-T094-41) tới khi thử thật (LC-T094-44).
- 2026-10-30 19:59 (Chỉ Huy B): Họa Sĩ xong lượt 1 (`32a217a`); R5 duyệt 4 test cũ (18:45, kèm điều kiện giữ ý «đăng ngay cần xác nhận», client giả kiểm khóa gửi). Lượt gộp: gộp `team/T-101` vào nhánh (`b34145a`), R5 đổi 2 test T-101 (trang Kế hoạch không ghi Sheet; Soạn bài ghi «Đang viết» một lần, bỏ khóa sau khi dùng), G1 (bài gõ tay không nhận `DraftPlanRef` cũ; cho sửa đúng chỗ đó ở trang Bài viết), LC-T101-1 (`safe_text` cho bảng có nút tải CSV; cho sửa `app/views/plan.py`). Chú thích `[plan]` trong `config/content.toml` («chưa dùng») giao người được sửa `config/**` sau.
- 2026-10-30 22:24 (Chỉ Huy B): Họa Sĩ lượt gộp `5c37be0` (T-101 `944160c`, G1, LC-T101-1). Giao Soi Lỗi rút gọn (20:25; gộp thử với `main` `eef13b5`), rồi Lá Chắn đầy đủ (đóng cả LC-T101-1).

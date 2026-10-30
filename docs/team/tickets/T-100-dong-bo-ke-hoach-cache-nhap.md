# T-100 · Đồng bộ kế hoạch: cache SQLite, kiểm xung đột khi ghi Sheets, nối nháp với dòng kế hoạch

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (đợt 2) |
| Phụ thuộc | T-097, T-098 đã gộp; không song song với T-092 (cùng `drafts.py`) |
| Trạng thái | Xong (gộp `main` 2026-10-30, đủ 4 lượt) |

## Mục tiêu

Làm phần **T-100** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-100) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-100 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `seo_app/storage/plan_cache.py`, `seo_app/plan/sync.py` (mới), `seo_app/storage/drafts.py` (phần `plan`, `SendState`), test.
- **Không được sửa:** `seo_app/wordpress/**`, `app/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-100 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-100-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 23:14 (Chỉ Huy B): T-097, T-098 đã gộp đủ các lượt. Nhánh `team/T-100` từ `main` `b241e79`, worktree `wt-T-100`; giao Thợ Máy (phiên Thợ Máy T-083).
- 2026-10-28 23:14 (Chỉ Huy B): thêm vào phạm vi **SL-T097-5** (Soi Lỗi T-097 lượt 2, Thấp): so danh tính file khóa trên đường thật (`realpath`) thay vì chữ gõ, chỉ tin danh tính khi cùng gốc ổ; gỡ 3 `xfail` (chỉ xóa dấu). Phải xong trước khi T-101 hiện câu báo file khóa trên trang Cài đặt. Thêm **G2** (Soi Lỗi T-103): cảnh báo kiểu `WARN_PERSONAL` khi chữ AI đề xuất có dạng giá (số + «k», «đ», «triệu», «VNĐ»), vì hồ sơ doanh nghiệp không công bố giá; Chỉ Huy duyệt cho sửa `seo_app/plan/propose.py` phần cảnh báo này. Lá Chắn T-103 nâng G2 thành **LC-T103-1** (Thấp); `xfail` của nó vào `main` khi T-103 gộp, T-100 gộp `main` vào nhánh rồi gỡ dấu. **Chỉ Huy duyệt A (R5):** khuôn nháp lên 3 (LC-T094-30), đổi 8 dòng test cũ ghim khuôn 2 / «3 là khuôn lạ» (`test_drafts_images.py`, `test_soi_loi_t016_t020.py`, `test_soi_loi_t041.py`, `test_soi_loi_t055.py`); khuôn 1, 2 vẫn mở, có ca chứng minh.
- 2026-10-30 12:52 (Chỉ Huy B): Lá Chắn xem lại lượt 2 ĐẠT CÓ ĐIỀU KIỆN (`a214c0b`). Gộp `main`, Windows 20.877 test qua, 0 hỏng. Lượt 3 (`777d124`) Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`0b1da79`, 4 Thấp SL-T100-12 → -15 ở hàm dò giá) → lượt 4. Sau lượt 4, ca dò giá lặt vặt còn sót coi là giới hạn đã biết của cảnh báo mềm (lời dặn AI đã cấm giá, người dùng còn duyệt), không mở thêm lượt chỉ vì chúng.
- 2026-10-30 17:23 (Chỉ Huy B): lượt 4 Soi Lỗi ĐẠT (`da0e510`, 0 lỗi mới), Lá Chắn xem lại lượt 3–4 ĐẠT (`a39ed14`). Gộp `main` (`fd28bbc`), Windows 21.063 test qua, 0 hỏng. Không còn lỗi nào mở trong phạm vi T-100; ca dò giá lặt vặt sau này coi là giới hạn đã biết của cảnh báo mềm.

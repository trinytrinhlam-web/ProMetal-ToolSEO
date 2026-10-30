# T-099 · Client WordPress: hẹn giờ, đăng ngay, đọc trạng thái bài (`release_draft`)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (đợt 1, sau T-091) |
| Phụ thuộc | T-091 đã gộp (cùng `client.py`) |
| Trạng thái | Xong (gộp `main` 2026-10-30, đủ 2 lượt) |

## Mục tiêu

Làm phần **T-099** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-099) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-099 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py` (chỉ phần mới), `seo_app/publish/schedule.py` (mới), test.
- **Không được sửa:** `app/**`, `config/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-099 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-099-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Đầy đủ, soát kỹ nhất (đường tới `future`/`publish`).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 23:14 (Chỉ Huy B): T-091 đã qua Soi Lỗi lượt 2 (ĐẠT). Nhánh `team/T-099` từ `main` `b241e79` + đưa T-091 vào trước (`9e0115e`), worktree `wt-T-099`; giao Thợ Máy (phiên Thợ Máy T-059).
- 2026-10-30 12:52 (Chỉ Huy B): Lá Chắn đầy đủ ĐẠT CÓ ĐIỀU KIỆN (`ce451fe`). Gộp `main`, Windows 20.877 test qua, 0 hỏng. Lượt 2: LC-T099-1, SL-T099-1 (Thợ Máy).
- 2026-10-30 19:59 (Chỉ Huy B): lượt 2 (Soi Lỗi ĐẠT `7c2a827`, Lá Chắn ĐẠT `38613fe`) gộp `main` (`9283592`, cùng T-107 lượt 1–2 ở `17b2a31`). Windows 21.295 test qua, 0 hỏng. T-099 xong hẳn; T-102 nối màn hình xác nhận, giữ công tắc mặc định tắt tới khi thử thật (LC-T094-41, -44).

# T-098 · Kế hoạch: khuôn dữ liệu, đọc CSV/TSV/chữ dán, đề xuất thay đổi có AI, sửa SL-7

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (đợt 1) |
| Phụ thuộc | Không |
| Trạng thái | Xong (gộp `main` 2026-10-28); lượt 4 (3 Thấp) đang làm, trước T-100 |

## Mục tiêu

Làm phần **T-098** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-098) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-098 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `seo_app/plan/model.py`, `parse.py`, `propose.py` (mới); `ContentWriter.plan_changes`, `prompts.plan_prompt` trong `seo_app/content/` (chỉ phần mới), test.
- **Không được sửa:** `seo_app/wordpress/**`, `app/**`, `seo_app/storage/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-098 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-098-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (dữ liệu chưa tin cậy, prompt).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 21:09 (Chỉ Huy B): Soi Lỗi lượt 3 ĐẠT CÓ ĐIỀU KIỆN (`2e0d29b`: SL-T098-12 → -17 đóng; 3 Thấp mới SL-T098-18 → -20, không chặn gộp); Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (`b520623`, 0 lỗi mới). Gộp `main`, Windows 19.496 test qua, 0 hỏng. Lượt 4 (Thợ Máy) sửa 3 Thấp trước T-100, T-101.

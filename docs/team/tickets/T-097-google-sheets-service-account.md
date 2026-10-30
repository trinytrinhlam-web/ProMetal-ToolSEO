# T-097 · Client Google Sheets và kiểm file khóa tài khoản dịch vụ

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (đợt 1) |
| Phụ thuộc | Câu hỏi 1: **chủ dự án chốt A sáng 28/10** (khai báo `google-auth`) |
| Trạng thái | Xong (gộp `main` 2026-10-28, cả lượt 2); SL-T097-5 chuyển T-100 |

## Mục tiêu

Làm phần **T-097** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-097) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-097 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `seo_app/google/service_account.py`, `seo_app/google/sheets.py` (mới), `seo_app/env_file.py` (bộ kiểm riêng cho `GOOGLE_SHEET_ID`), `pyproject.toml` + `uv.lock` (khai báo `google-auth`, khóa phiên bản), `.env.example`, test.
- **Không được sửa:** `seo_app/wordpress/**`, `app/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-097 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-097-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Đầy đủ (bí mật, thư viện).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 28/10 08:27 (Chỉ Huy B): chủ dự án chốt A cả 6 câu thiết kế (câu 1: khai báo `google-auth`). Nhánh `team/T-097` từ `main` `b513d67`, worktree `wt-T-097`; giao Thợ Máy (phiên Thợ Máy T-059).
- 2026-10-28 17:31 (Chỉ Huy B): Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`82bf0c0`, 4 Thấp), Lá Chắn đầy đủ ĐẠT CÓ ĐIỀU KIỆN (`4f6a970`, 1 Thấp mới LC-T097-1). Gộp `main`, Windows 18.870 test qua, 0 hỏng. Lượt 2 (Thợ Máy) sửa SL-T097-1, -2, LC-T097-1 trước khi T-100 dùng client; SL-T097-3, -4 trước T-101.
- 2026-10-28 21:09 (Chỉ Huy B): lượt 2 giao Thợ Máy (phiên Thợ Máy T-059), nhánh `team/T-097` tua tới `main` `24013b3`.
- 2026-10-28 23:14 (Chỉ Huy B): lượt 2 Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`16b9f64`, 1 Thấp mới SL-T097-5), Lá Chắn xem lại ĐẠT CÓ ĐIỀU KIỆN (`931bfed`, LC-T097-1 đóng). Gộp `main`, Windows 19.645 test qua, 0 hỏng. SL-T097-5 (so danh tính file khóa theo đường thật) gom vào T-100 theo đề xuất Soi Lỗi.

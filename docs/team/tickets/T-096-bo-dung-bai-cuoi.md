# T-096 · Bộ dựng bài cuối: Markdown → HTML, kiểm link, dữ liệu xác nhận

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (đợt 1) |
| Phụ thuộc | Không |
| Trạng thái | Xong (gộp `main` 2026-10-28); lượt 5 ngắn LC-T096-6 đang làm (trước T-102) |

## Mục tiêu

Làm phần **T-096** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-096) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-096 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** `seo_app/publish/render.py` (mới) và file mới trong `seo_app/publish/`, test mới.
- **Không được sửa:** `seo_app/wordpress/**`, `app/**`, `config/**`, `seo_app/storage/**`.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-096 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-096-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (soát kỹ phần chuyển Markdown, link).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 15:47 (Chỉ Huy B): Lá Chắn xem lại lượt 3 ĐẠT CÓ ĐIỀU KIỆN (`d864943`, 6/6 lỗi đóng). Gộp `main` (`1b45f5d`), Windows 17.950 test qua, 0 hỏng. LC-T096-5 (Thấp) làm theo đề xuất của Lá Chắn: lượt 4 ngắn của Thợ Máy (phiên Thợ Máy T-094), nhánh `team/T-096` tua tới `main`; Chỉ Huy duyệt đổi điều kiện ca `<p><a …>https://…</a> rồi</p>` của `test_embed_patterns_not_found` cùng lượt sửa.
- 2026-10-28 21:09 (Chỉ Huy B): Lá Chắn xem lại lượt 4 ĐẠT CÓ ĐIỀU KIỆN (`5aa1ecf`: LC-T096-5 đóng, 1.993/1.993 đoạn Gutenberg nhúng bị Chặn). Gộp `main`, Windows 19.496 test qua, 0 hỏng. LC-T096-6 (Thấp: tab, «\», thừa «/», tên đăng nhập có dấu cách) → lượt 5 ngắn khi máy rảnh, bắt buộc trước T-102.
- 2026-10-28 23:14 (Chỉ Huy B): lượt 5 (LC-T096-6) giao Thợ Máy (phiên Thợ Máy T-094), nhánh `team/T-096` tua tới `main` `b241e79`.

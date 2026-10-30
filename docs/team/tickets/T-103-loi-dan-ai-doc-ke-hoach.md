# T-103 · Lời dặn AI đọc kế hoạch, `[tasks.plan]`, `[plan]`

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (đợt 2) |
| Phụ thuộc | T-098 đã gộp |
| Trạng thái | Đang làm |

## Mục tiêu

Làm phần **T-103** đúng như thiết kế Giai đoạn 5: `docs/team/reports/T-094-tho-may.md` mục 6 «Chia phiếu» (dòng T-103) và các mục thiết kế nó trỏ tới.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-094-tho-may.md` (mục 1–8). Câu hỏi cho chủ dự án (mục 9): Chỉ Huy chọn khuyến nghị **A cả 6 câu** theo dặn 27/10 («có đề xuất thì làm theo đề xuất»); chủ dự án có thể đổi sáng 28/10.
- **Điều kiện bảo mật bắt buộc:** `docs/team/reports/T-094-la-chan.md` mục «Chung cho mọi phiếu Giai đoạn 5» và mục «T-103 · …»; cùng «Chỗ thiếu hay rủi ro trong thiết kế» phần liên quan. Phải làm đủ, ghi từng mã LC-T094-n đã đáp ứng ở đâu trong báo cáo.
- Board mục «Việc bắt buộc khi làm Giai đoạn 5».

## Phạm vi

- **Được sửa:** phần chữ của `plan_prompt`, `config/ai.toml` (`[tasks.plan]`), `config/content.toml` (`[plan]`), test lời dặn.
- **Không được sửa:** code logic ngoài phần chữ.
- Không gọi WordPress, Google hay AI thật trong test.

## Yêu cầu

1. Làm đúng dòng T-103 của thiết kế, giữ ranh giới file với các phiếu cùng đợt.
2. Đáp ứng mọi điều kiện LC-T094-n của phiếu này và phần «Chung».
3. Test cho phần logic mới; test cũ vẫn qua.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-103-<vai>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 23:46 theo thiết kế T-094 (Lá Chắn: thiết kế đủ để mở phiếu code, 44 điều kiện) và chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 21:09 (Chỉ Huy B): T-098 đã gộp. Nhánh `team/T-103` từ `main` `24013b3`, worktree `wt-T-103`; giao Ngòi Bút (phiên Ngòi Bút T-040).
- 2026-10-28 23:14 (Chỉ Huy B): Ngòi Bút xong (`f61012a`). Chấp nhận dòng thêm ngoài danh sách file: nhãn `'plan'` trong `TASK_LABELS` (`seo_app/content/blind_test.py`) để thử mù chạy được với tác vụ mới. Soi Lỗi rút gọn ĐẠT (`fdb47c2`, 0 lỗi, 4 góp ý), giao Lá Chắn rút gọn. Góp ý làm theo đề xuất: **G1** (một câu cho dòng «(chưa có mã)») Ngòi Bút làm ở lượt sửa sau Lá Chắn; **G2** (cảnh báo chữ AI có dạng giá) → T-100; **G3** (AI lẫn ví dụ trong lời dặn với bài thật) → thử ở lượt thử thật Giai đoạn 5 với AI thật; **G4** (nhãn «Sẵn sàng» của demo) → T-101.

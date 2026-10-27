# T-101 · Giao diện: trang Kế hoạch, Cài đặt → Google, trang Bài viết (thay demo, giữ bố cục đã duyệt)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (đợt 3) |
| Phụ thuộc | T-100, T-103 đã gộp |
| Trạng thái | Chờ |

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

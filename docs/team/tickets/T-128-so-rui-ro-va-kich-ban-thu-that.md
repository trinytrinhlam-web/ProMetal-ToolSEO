# T-128 · Sổ rủi ro 3 giới hạn `modified_gmt` và kịch bản buổi thử thật Hẹn giờ/Đăng ngay

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-04 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (2 việc cuối trước khi bật công tắc) |
| Phụ thuộc | T-112, T-115 đã gộp `main`; chủ dự án đồng ý ghi sổ 04/11 |
| Trạng thái | Xong (gộp `main` 2026-11-07) |

## Mục tiêu

Xong hai việc giấy tờ còn lại trước khi bật công tắc Hẹn giờ/Đăng ngay: ghi sổ rủi ro, và soạn sẵn kịch bản buổi thử thật để chủ dự án báo rảnh là làm được ngay.

## Yêu cầu

1. `docs/team/security.md` §6: ghi **3 dòng** (chủ dự án đồng ý 04/11) cho 3 giới hạn phép so `modified_gmt` mà Lá Chắn T-115 nêu (`docs/team/reports/T-115-la-chan.md`, mục «Tự tái hiện cả ba»): cùng giây; khe giữa lệnh đọc kiểm và lệnh ghi của app; sửa chỉ meta. Mỗi dòng: rủi ro, vì sao chấp nhận (WordPress không có khóa lạc quan; cần người đang sửa đúng nháp vừa tạo trong vài giây; nội dung đã xác nhận bằng mã băm T-102), người chấp nhận «Chủ dự án (04/11)».
2. Kịch bản buổi thử thật **LC-T094-44**, mục (a)–(g) như Lá Chắn T-112 liệt kê (`docs/team/reports/T-112-la-chan.md`, mục «Điều kiện», phần B mục 4, và bảng «Còn phải làm trước khi bật công tắc» lượt 3): viết thành `docs/team/reports/T-128-kich-ban-thu-that.md`, từng bước cho Chỉ Huy làm khi chủ dự án ngồi cùng: chuẩn bị (Sheet bản sao, bài thử nháp do chủ dự án duyệt), bật công tắc trong phiên, từng ca (hẹn giờ xa rồi chuyển về nháp; Đăng ngay một bài thử rồi gỡ; ghi SEO qua Abilities có đổi `modified_gmt` không — mục (b); header `Date`; quyền `publish_posts`; xem bài hiển thị thật; trả lời lạ), cách dọn sau buổi thử, bảng ghi kết quả để Lá Chắn đọc.
3. Kịch bản **không** chứa Application Password, file khóa, mã Sheet đầy đủ, email dịch vụ (LC-T094-44).

## Phạm vi

- **Được sửa:** `docs/team/security.md` §6, báo cáo mới `docs/team/reports/T-128-kich-ban-thu-that.md`, `docs/team/reports/T-128-thu-ky.md`. Không sửa code, README.

## Tiêu chí xong

- [ ] Yêu cầu 1–3; `detect-secrets` (`PYTHONUTF8=1`) sạch

## Kiểm thử và kiểm định

- Soi Lỗi: không. Lá Chắn: rút gọn (đọc kịch bản: đủ (a)–(g), không lộ bí mật, có bước dọn).

## Ghi chú của Chỉ Huy

- Lập 2026-11-04. Chủ dự án 04/11: **đồng ý ghi sổ** 3 giới hạn; buổi thử thật **làm khi chủ dự án báo rảnh** (Chỉ Huy soạn sẵn kịch bản). Worktree `wt-T-128`, nhánh `team/T-128`.
- 2026-11-05 12:37 (Chỉ Huy B): Thư Ký `fb1dece` (3 dòng sổ rủi ro, kịch bản); Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (`952aaca`): sổ rủi ro đúng, 3 Thấp trong kịch bản sửa trước buổi thử → lượt 2.
- 2026-11-07 07:52 (Chỉ Huy B): lượt 2 (`0ad9c7b`), Lá Chắn ĐẠT (`90adf36`). Gộp `main`, đã đẩy. Buổi thử thật làm khi chủ dự án báo rảnh.

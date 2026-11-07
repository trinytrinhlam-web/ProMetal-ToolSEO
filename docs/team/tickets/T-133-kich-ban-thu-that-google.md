# T-133 · Kịch bản buổi thử thật Google Search Console (Giai đoạn 6)

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-07 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình (trước bản 1.0) |
| Phụ thuộc | T-121, T-124 (lõi); T-125 (giao diện) để chốt tên nút |
| Trạng thái | Đang làm |

## Mục tiêu

Soạn sẵn kịch bản từng bước cho buổi thử thật phần theo dõi Google (Chỉ Huy làm, chủ dự án ngồi cùng), giống kịch bản T-128 cho Hẹn giờ/Đăng ngay, để chủ dự án báo rảnh là làm được ngay.

## Nguồn

- Thiết kế T-120 (`docs/team/reports/T-120-tho-may.md`) mục 6 «Đi kèm» dòng «Thử thật» (6 bước) và mục «Rủi ro và điểm cần chú ý».
- Lá Chắn T-121 (`docs/team/reports/T-121-la-chan.md`): điều kiện cho lượt thử thật Google (quyền «Hạn chế», tên trường `metadata`, mã lý do 403, `dropped`, cỡ câu trả lời).
- Lá Chắn T-124 (`docs/team/reports/T-124-la-chan.md`) điều kiện 3: ghi `metadata` thật của đoạn mới nhất và một đoạn cũ; `dropped` với website thật; số lệnh lần đầu; nếu Google có lúc thiếu `metadata` thì mở phiếu nhỏ.
- README mục 15 «Theo dõi trên Google» (việc chủ dự án làm trước phía Google).
- Kịch bản mẫu: `docs/team/reports/T-128-kich-ban-thu-that.md`.

## Yêu cầu

1. Viết `docs/team/reports/T-133-kich-ban-thu-that-google.md`: chuẩn bị (chủ dự án đã bật API, đã thêm email tài khoản dịch vụ quyền «Hạn chế»), từng ca (Tìm thuộc tính, Kiểm tra, Lấy số liệu lần đầu, bấm lại ngay bị chặn, so 2 bài với Search Console bảng «Trang» 28 ngày, xem từ khóa, Search Console → Người dùng và quyền không đổi), bảng ghi kết quả cho Lá Chắn đọc, cách dọn (Xóa bản lưu tạm nếu cần).
2. **Không nâng quyền** khi gặp 403: dừng, hỏi chủ dự án và Lá Chắn.
3. Không ghi vào kịch bản hay bảng kết quả: file khóa, email tài khoản dịch vụ đầy đủ, mã project, `GSC_SITE_URL` đầy đủ nếu không cần.
4. Tên nút, tên mục theo giao diện T-125 (`app/views/tracking.py`, `app/views/settings.py` trên nhánh `team/T-125`); chỗ nào chưa chắc thì ghi «(tên theo giao diện khi gộp)».

## Phạm vi

- **Được sửa:** chỉ báo cáo mới `docs/team/reports/T-133-kich-ban-thu-that-google.md`, `docs/team/reports/T-133-thu-ky.md`.

## Tiêu chí xong

- [ ] Yêu cầu 1–4; `detect-secrets` (`PYTHONUTF8=1`) sạch

## Kiểm thử và kiểm định

- Soi Lỗi: không. Lá Chắn: rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-11-07 theo điều kiện 3 Lá Chắn T-124. Worktree `wt-T-133`, nhánh `team/T-133`.

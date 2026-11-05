# T-126 · README «Theo dõi trên Google» (Giai đoạn 6)

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-04 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Phần 1: T-121 đã gộp; phần 2: sau T-125 |
| Trạng thái | Đang làm (phần 1 xong; phần 3 sau T-125) |

## Mục tiêu

Hướng dẫn chủ dự án dùng phần theo dõi Google bằng lời thường.

## Yêu cầu

1. **Phần 1 (làm ngay khi giao):** việc chủ dự án làm phía Google (thiết kế T-120 mục 1.2): bật «Google Search Console API» trong project Google Cloud đang dùng cho Sheets; thêm email tài khoản dịch vụ vào Search Console với quyền **«Hạn chế»**; không chọn thuộc tính staging; không nâng quyền khi gặp lỗi 403 (hỏi Chỉ Huy).
2. Chú thích `GSC_SITE_URL` trong `.env.example`: hai dạng hợp lệ (`sc-domain:…`, tiền tố `https://…/`), nên chọn ở Cài đặt, không dùng thuộc tính staging (chỉ chú thích).
3. **Phần 2 (sau T-125):** cách đọc số (trễ 2–3 ngày, ngày theo giờ Google, tổng theo trang khác biểu đồ Search Console, từ khóa bị ẩn, nhãn tụt hạng…), nút «Đưa vào kế hoạch».

## Phạm vi

- **Được sửa:** `README.md`, chú thích trong `.env.example`. **Không** sửa code.

## Yêu cầu bảo mật riêng

Không ghi email tài khoản dịch vụ đầy đủ, mã project, đường dẫn file khóa thật vào README. LC-T120-15 (test README nếu có).

## Tiêu chí xong

- [ ] Phần 1, 2 rồi phần 3; báo cáo `docs/team/reports/T-126-thu-ky.md`; `detect-secrets` (`PYTHONUTF8=1`) sạch

## Kiểm thử và kiểm định

- Soi Lỗi: không. Lá Chắn: rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-11-04 theo thiết kế T-120. Phần 1 giúp chủ dự án làm sớm hai việc phía Google cho buổi thử thật.
- 2026-11-05 12:37 (Chỉ Huy B): phần 1 (`cbe3114`): README mục 15, chú thích `GSC_SITE_URL`; Lá Chắn rút gọn ĐẠT (`9ead565`). Gộp `main`, chạy lại test README/`.env.example`: 134 qua, 2 xfail.

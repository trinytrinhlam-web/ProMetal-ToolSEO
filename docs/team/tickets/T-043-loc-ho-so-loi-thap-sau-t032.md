# T-043 · Bộ lọc hồ sơ: 3 lỗi Thấp còn lại sau T-032

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-16 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp (nên xong trước khi chủ dự án tự điền mục 7 của hồ sơ) |
| Phụ thuộc | T-032 đã gộp (`cbfe37a`) |
| Trạng thái | Chờ chỗ trống |

## Mục tiêu

Chủ dự án gõ nhãn `[CẦN XÁC NHẬN]` theo kiểu lạ hơn nữa thì ý chưa xác nhận vẫn không tới AI.

## Bối cảnh và danh sách lỗi

| Mã | Nguồn | Lỗi | Gợi ý |
|---|---|---|---|
| SL-T032-4 | `docs/team/reports/T-032-soi-loi.md` (Lượt 2) | Tiêu đề có nửa nhãn, rồi tới **dòng trống**, rồi mới tới nửa sau. Mục bị lọt | Theo báo cáo Soi Lỗi |
| SL-T032-5 | như trên | Tiêu đề **thụt lề** có nửa nhãn. Mục bị lọt | Theo báo cáo Soi Lỗi |
| LC-T032-1 | `docs/team/reports/T-032-la-chan.md` | Ký tự khác khoảng trắng chen trong nhãn làm nhãn không được nhận: `[**CẦN XÁC NHẬN**]`, `["CẦN XÁC NHẬN"]`, `[⚠ CẦN XÁC NHẬN]`, `[CẦN-XÁC-NHẬN]`. Lỗi có từ trước | Cho phép tối đa vài ký tự không phải chữ/số ở giữa và đầu nhãn, ví dụ `[\W_]{0,4}`. **Phải có giới hạn**: dùng `*` thì chuỗi `[[[[…` chạy bậc hai |

Cả 3 đều là lỗi để **lọt**, nhưng rất hiếm gặp. Hồ sơ hiện tại không dính lỗi nào.

## Phạm vi

- **Được sửa:** `seo_app/content/rules.py`, test. Nếu cú pháp nhãn được nới, sửa thêm các dòng `>` đầu `config/business_profile.md`.
- **Không được sửa:** mọi file khác.

## Yêu cầu

1. Sửa 3 lỗi. Bỏ `xfail` của đúng các test tương ứng (SL-T032-4, -5 có sẵn). Thêm test cho LC-T032-1.
2. Giữ nguyên mọi hành vi đã có. Toàn bộ test của T-024 và T-032 vẫn qua.
3. Câu thường như "cần xác nhận lịch" (không có ngoặc) vẫn **không** bị giấu.
4. Tuyến tính. Thêm test tốc độ cho chuỗi xấu, ví dụ `[[[[…`, `[****…`.
5. Phần hồ sơ thật mà AI thấy không đổi so với `main`: so chuỗi.

## Yêu cầu bảo mật riêng

A1, A3, D3.

## Tiêu chí xong

- [ ] 3 lỗi đã sửa, có test
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-043-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1, A3).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-043 Bộ lọc hồ sơ, lỗi Thấp sau T-032"**, nhánh `team/T-043` (từ `main`).

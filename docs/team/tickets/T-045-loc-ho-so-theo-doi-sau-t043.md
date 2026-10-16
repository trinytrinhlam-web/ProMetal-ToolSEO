# T-045 · Bộ lọc hồ sơ: phiếu theo dõi 3 lỗi Thấp sau T-043

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-16 |
| Giai đoạn | Giai đoạn 2 (dọn lỗi) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-043 đã gộp |
| Trạng thái | Chờ (phiếu theo dõi, điều kiện của Lá Chắn T-043) |

## Mục tiêu

Lá Chắn T-043 kết luận **ĐẠT CÓ ĐIỀU KIỆN**, với điều kiện mở phiếu theo dõi 3 lỗi Thấp còn lại của bộ lọc hồ sơ (`docs/team/reports/T-043-la-chan.md`). Phiếu này sửa cả 3 lỗi. Nếu chủ dự án không muốn sửa thì ghi cả 3 vào sổ rủi ro (`docs/team/security.md` mục 6) rồi đóng phiếu.

## Danh sách lỗi

| Mã | Nguồn | Lỗi | Gợi ý |
|---|---|---|---|
| LC-T043-1 | `T-043-la-chan.md` | **Lùi so với trước T-043.** Một ý đã có nhãn, kèm một dòng nối thụt lề `  ## … [CẦN` mà nhãn không gõ hết. Khi đó các dòng thụt lề phía sau tới AI. Trước T-043, bộ lọc giấu được ca này | Do phần sửa SL-T032-5 (`rules.py` khoảng dòng 142). Thêm điều kiện: khối đã có nhãn thì không tách. Lá Chắn đã fuzz 300.000 ca: ngoài lớp này không có ca lùi nào |
| SL-T043-1 | `T-043-soi-loi.md` | Nhãn có từ 5 ký tự lạ trở lên không được nhận, ví dụ `[❗❗❗ **CẦN XÁC NHẬN**]` hoặc emoji ghép nhiều điểm mã | Cách của Soi Lỗi: `(?:\s\|[^\w\s\[\]()]\|_)*+`. Lá Chắn đo: tuyến tính, an toàn về ReDoS. Phải sửa đồng bộ `_PARTIAL_TAG_REST` và giữ cửa sổ 64 ký tự |
| SL-T043-2 | như trên | Tiêu đề `## 7 [CẦN XÁC`, rồi dòng kế `## NHẬN]`: mục bị lọt. Có từ trước T-043 | Theo báo cáo Soi Lỗi |

## Phạm vi

- **Được sửa:** `seo_app/content/rules.py`, test.
- **Không được sửa:** các file khác.

## Yêu cầu

1. Sửa 3 lỗi. Bỏ `xfail` của đúng các test tương ứng. Thêm test cho LC-T043-1.
2. Giữ nguyên mọi hành vi đã có. Toàn bộ test của T-024, T-032, T-043 vẫn qua.
3. Bộ lọc vẫn tuyến tính.
4. Phần hồ sơ thật mà AI thấy không đổi.

## Yêu cầu bảo mật riêng

A1, A3, D3.

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1, A3).

## Ghi chú của Chỉ Huy

- Chỉ Huy B lập phiếu lúc bàn giao, chưa giao. Chỉ Huy kế tiếp giao khi còn chỗ: phiên **"Thợ Máy · T-045 Bộ lọc hồ sơ, theo dõi sau T-043"**, nhánh `team/T-045` tạo từ `main`.

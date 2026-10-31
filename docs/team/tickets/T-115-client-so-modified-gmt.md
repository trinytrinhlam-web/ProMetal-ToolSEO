# T-115 · Client WordPress: so `modified_gmt` ngay trước lệnh chuyển (LC-T094-23)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-31 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (trước khi bật công tắc Hẹn giờ/Đăng ngay) |
| Phụ thuộc | T-099, T-102 đã gộp |
| Trạng thái | Đang làm |

## Mục tiêu

Nếu bài nháp trên website bị sửa (trong trang quản trị, plugin, người khác) sau khi app ghi lần cuối, `release_draft` không chuyển bài sang `future`/`publish`; bài giữ là nháp, câu báo cố định.

## Bối cảnh

- Lá Chắn T-094 LC-T094-23, nhắc lại ở biên bản Lá Chắn đầy đủ T-102 (`docs/team/reports/T-102-la-chan.md`, «Nên làm cùng lúc»); tách từ T-112 vì phải sửa client.
- Đề xuất của Họa Sĩ (T-112): client nhớ `modified_gmt` trả về từ các lệnh ghi của chính nó (tạo nháp, đặt ảnh đại diện, ghi meta SEO, gắn ảnh T-110), rồi trong lệnh GET kiểm nháp ngay trước lệnh chuyển thì so lại; khác thì `ReleaseError`, bài vẫn là nháp. Phía app không đổi (đường `ReleaseError` «bài vẫn là nháp» đã có).

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py` (chỉ phần nhớ/so `modified_gmt`, danh sách `_fields` cần thiết), test.
- **Không được sửa:** `app/**`, phần khác của client.

## Yêu cầu

1. Nhớ `modified_gmt` của bài nháp sau mỗi lệnh ghi của chính client vào bài đó (xin thêm `modified_gmt` trong `_fields` khi cần; giá trị lạ/thiếu → coi như không biết → không chuyển, câu báo cố định).
2. Lệnh GET kiểm ngay trước lệnh chuyển so `modified_gmt` với giá trị đã nhớ; khác → `ReleaseError` (bài vẫn là nháp), không gửi lệnh chuyển.
3. Lệnh ghi xen giữa (ảnh đại diện, SEO) cập nhật giá trị nhớ đúng thứ tự; hai client / hai tab không dùng chung giá trị.
4. Ghi rõ trong báo cáo cần kiểm khi thử thật: ghi SEO qua Abilities (SiteSEO) có làm đổi `modified_gmt` không và có trả giá trị đó về không; nếu không trả thì đề xuất cách (đọc lại bằng GET sau lệnh ghi SEO).
5. Không lùi T-060, T-085, T-088, T-091, T-099, T-110 (grep mọi nơi gọi, test ghim `_fields`); đổi test cũ thì hỏi Chỉ Huy (R5).

## Yêu cầu bảo mật riêng

W2, W3; LC-T094-23.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-115-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-31, tách từ T-112 yêu cầu 3 theo đề xuất Họa Sĩ.
- 2026-10-31 13:32 (Chỉ Huy B): giao Thợ Máy (phiên T-094) 09:55, nhánh từ `d6df633`. R5 duyệt 10:55 (thêm `,modified_gmt` vào chuỗi `_fields` mong đợi; thêm `modified_gmt` vào câu trả lời giả tạo/kiểm nháp), 13:20 (gỡ `xfail` LC-T102-1: T-115 chặn ở lớp client).

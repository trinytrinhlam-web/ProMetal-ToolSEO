# T-007 · Xóa thông tin GPS trong ảnh trước khi tải lên WordPress

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 1 (lỗi tồn tại từ trước), liên quan Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Quyết định của chủ dự án |
| Trạng thái | Chờ chủ dự án chọn cách |

## Mục tiêu

Ảnh chụp ở nhà khách hàng không bao giờ lên website kèm tọa độ GPS.

## Bối cảnh

Lỗi #3 trong [T-001-la-chan.md](../reports/T-001-la-chan.md): ô tải ảnh đại diện ở trang Kết nối WordPress gửi ảnh nguyên bản.

## Cách làm (chủ dự án chọn)

- (a) Khai báo thư viện ảnh Pillow (đã có sẵn trên máy nhờ Streamlit) và dùng nó xóa EXIF, giới hạn kích thước ảnh. Giai đoạn 3 cũng cần thư viện này. **Chỉ Huy đề xuất.**
- (b) Tạm gỡ ô tải ảnh ở trang Kết nối WordPress cho tới Giai đoạn 3.

## Tiêu chí xong

- [ ] Test: ảnh có GPS → dữ liệu gửi đi không còn GPS (cách a), hoặc trang không còn ô tải ảnh (cách b)
- [ ] Báo cáo `docs/team/reports/T-007-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có
- Lá Chắn: Có

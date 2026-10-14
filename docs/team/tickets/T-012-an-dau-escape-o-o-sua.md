# T-012 · Không hiện dấu `\` trong các ô người dùng sửa chữ

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-008 lần 3 |
| Trạng thái | Xong |

## Mục tiêu

T-008 lần 3 chèn `\` vào chữ AI (`]\(`, `]\[`, `]\:`) để không tạo được link. Trên phần hiển thị Markdown không thấy gì, nhưng trong các ô sửa chữ (ô «Sửa trực tiếp», tiêu đề dàn ý, tiêu đề bài…) người dùng sẽ thấy dấu `\` lạ. Bỏ dấu đó khi đưa chữ vào ô sửa, và chạy lại `escape_link_syntax` khi lưu.

## Phạm vi

- **Được sửa:** `app/views/write.py`, `seo_app/ui.py`; có thể thêm hàm ngược `unescape_link_syntax` trong `seo_app/sanitize.py` (chỉ thêm, không sửa hàm có sẵn).

## Tiêu chí xong

- [ ] Ô sửa không hiện `\` do escape; lưu xong chữ lại được escape (không tạo được link)
- [ ] Test AppTest cho ô «Sửa trực tiếp» và tiêu đề dàn ý
- [ ] Báo cáo `docs/team/reports/T-012-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

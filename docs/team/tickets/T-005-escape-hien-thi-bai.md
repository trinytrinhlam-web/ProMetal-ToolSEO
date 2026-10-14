# T-005 · Hiển thị bài AI an toàn trên trang Soạn bài

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | **Cao** |
| Phụ thuộc | Không (làm song song T-004, khác file) |
| Trạng thái | Mới (chờ chủ dự án cho phép sửa code) |

## Mục tiêu

Lớp bảo vệ thứ hai: dù bộ lọc ở T-004 có sót, trang Soạn bài vẫn không bao giờ dựng nội dung AI thành HTML.

## Bối cảnh

Lỗi #1 trong [T-001-la-chan.md](../reports/T-001-la-chan.md): `app/views/write.py:462` gọi `st.markdown(..., unsafe_allow_html=True)` với nội dung từ `seo_app/ui.py:49-55` (`highlight`) chưa escape.

## Phạm vi

- **Được sửa:** `seo_app/ui.py`, `app/views/write.py` (chỉ phần hiển thị).
- **Không được sửa:** logic trong `seo_app/content/`.

## Yêu cầu

1. `ui.highlight()` gọi `html.escape` cho văn bản và cho câu được tô trước khi chèn `<mark>`.
2. Rà mọi `unsafe_allow_html=True` trong `app/`: chỉ được dùng với HTML cố định hoặc nội dung đã escape.
3. Giữ nguyên bố cục đã duyệt.

## Tiêu chí xong

- [ ] `test_highlight_escapes_ai_text` chuyển thành `passed`
- [ ] Bảng liệt kê mọi `unsafe_allow_html=True` và lý do an toàn, trong báo cáo
- [ ] Báo cáo `docs/team/reports/T-005-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có
- Lá Chắn: Có

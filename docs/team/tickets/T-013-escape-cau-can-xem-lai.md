# T-013 · Hiển thị an toàn câu trong khung «Cần xem lại»

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không |
| Trạng thái | Xong (2026-10-14) |

## Mục tiêu

R4-1 trong [T-008r3-012-soi-loi.md](../reports/T-008r3-012-soi-loi.md): `app/views/write.py:506` hiện câu AI chỉ ra bằng `st.markdown(f"> {sentence}")`, có thể tạo link. Hiển thị `escape_link_syntax(sentence)` (xử lý cả câu nhiều dòng), vẫn giữ câu gốc khi gọi `apply_fix`/`ignore_fix`.

## Tiêu chí xong

- [ ] Test `test_r4_1_…` chuyển thành `passed`
- [ ] Bổ sung mục "T-013" cuối `docs/team/reports/T-012-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

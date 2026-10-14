# T-017 · Tự lưu nháp và mở lại bài đang soạn (giao diện)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao |
| Phụ thuộc | T-016 |
| Trạng thái | Xong (2026-10-14) |

## Yêu cầu

1. Trang Soạn bài tự lưu nháp sau mỗi lần AI chạy xong và sau mỗi thay đổi của người dùng (sửa dàn ý, viết lại, áp dụng/bỏ qua gợi ý, sửa tay). Người dùng không phải bấm nút lưu.
2. Bước 1 có khung "Bài đang soạn dở": liệt kê nháp mới nhất (tiêu đề hoặc từ khóa, thời điểm lưu), nút Mở và nút Xóa (xóa phải hỏi lại một lần).
3. Mở nháp dựng lại đúng bước, đúng các phiên bản của từng phần.
4. Hiện dòng nhỏ "Đã lưu lúc HH:MM" để người dùng yên tâm.
5. Giữ bố cục đã duyệt. Mọi chữ lấy từ nháp hiển thị qua đường escape sẵn có (không `unsafe_allow_html` với dữ liệu nháp).
6. `tests/test_app_pages.py` vẫn mở được mọi trang và mọi bước; thêm test mở một nháp mẫu.

## Tiêu chí xong

- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-017-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

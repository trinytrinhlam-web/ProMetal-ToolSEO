# T-084 · Trang Cài đặt → Ảnh không in đường dẫn đầy đủ của thư mục ảnh

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-24 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (sau T-056) |
| Phụ thuộc | T-056 đã gộp vào `main` |
| Trạng thái | Mới (chờ T-056 gộp) |

## Mục tiêu

Tab Ảnh của trang Cài đặt hiện thư mục ảnh giống trang Soạn bài: tên ngắn của từng thư mục gốc, có báo "đi qua lối tắt", không in đường dẫn đầy đủ trên máy.

## Bối cảnh

- `app/views/settings.py` (khoảng dòng 472–477) in `folder` (đường dẫn tuyệt đối trong `IMAGE_FOLDERS`) bằng `st.markdown`. Có từ trước T-056; ghi chú U2 của Lá Chắn T-048 (`docs/team/reports/T-048-la-chan.md`): không hiện đường dẫn tuyệt đối, dùng `ImageLibrary.roots()`.
- Báo cáo Họa Sĩ T-056 (`docs/team/reports/T-056-hoa-si.md`, mục Đề xuất) nêu việc này; trang Soạn bài đã làm đúng cách (tên từ `RootInfo`, báo lối tắt, chữ đã escape và cô lập hướng chữ).
- Chủ dự án duyệt 2026-10-24.

## Phạm vi

- **Được sửa:** `app/views/settings.py` (tab Ảnh), test giao diện.
- **Không được sửa:** `seo_app/**`, `config/**`, `app/views/write.py`.

## Yêu cầu

1. Liệt kê thư mục gốc qua `ImageLibrary.roots()` (hoặc hàm dùng chung T-056 đã dùng), hiện tên ngắn đã escape và cô lập hướng chữ, trạng thái tìm thấy/không thấy, báo khi gốc đi qua lối tắt.
2. Không in đường dẫn tuyệt đối hay nội dung `.env` ở bất kỳ chỗ nào của tab.
3. Giữ phần còn lại của tab như bố cục đã duyệt; `tests/test_app_pages.py` vẫn qua.

## Yêu cầu bảo mật riêng

U1, U2.

## Tiêu chí xong

- [ ] Yêu cầu 1–3, có test (tên thư mục độc hại: RLO, ký tự rộng 0, Markdown)
- [ ] Test liên quan (`uv run pytest tests/test_app_pages.py` và test mới) qua, `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-084-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (U1, U2).

## Ghi chú của Chỉ Huy

- Lập theo đề xuất của Họa Sĩ T-056; chủ dự án duyệt 2026-10-24.

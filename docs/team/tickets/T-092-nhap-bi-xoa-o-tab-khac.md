# T-092 · Nháp bị xóa ở một tab trong khi tab khác còn mở: tự lưu tạo lại mất khóa gửi trùng

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`); được sửa phần lưu nháp trong `seo_app/storage/drafts.py` (việc Thợ Máy, Chỉ Huy duyệt cho Họa Sĩ làm để khỏi chia hai nhánh) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-089 đã gộp |
| Trạng thái | Chờ (giao khi máy rảnh) |

## Mục tiêu

Một bài đã gửi WordPress (nháp mang «đã gửi»/«đang gửi») không bị mất khóa gửi trùng chỉ vì người dùng xóa nháp ở tab này trong lúc tab khác vẫn mở bài đó và tự lưu.

## Bối cảnh

- Lá Chắn T-089, mục «Xem lại lượt 4» (`docs/team/reports/T-089-la-chan.md`): xóa nháp ở một tab khi tab khác còn mở thì lần tự lưu của tab kia tạo lại nháp **không có trạng thái gửi**; nháp đã gửi mất khóa, bấm gửi tiếp ra bài nháp thứ hai trên website. Có từ trước T-089. Mức Thấp.

## Phạm vi

- **Được sửa:** `app/views/write.py` (tự lưu, mở nháp), phần lưu/xóa nháp trong `seo_app/storage/drafts.py`, `.streamlit/config.toml` (chỉ yêu cầu 4), test.
- **Không được sửa:** `seo_app/wordpress/**`, khối SEO trong `drafts.py`, `config/**`.

## Yêu cầu

1. Tự lưu của tab còn mở không tạo lại nháp đã bị xóa một cách lặng lẽ (ví dụ: lưu kiểu «so rồi đặt» theo dấu phiên bản; nháp đã bị xóa thì báo rõ và hỏi tạo lại; nếu tạo lại thì giữ trạng thái gửi tab đó đang biết).
2. Không lùi các ca T-086, T-089 (hai tab, ngắt giữa chừng, gửi dở, băm ảnh).
3. Nháp cũ vẫn mở được; test cho các ca mới.
4. Đề xuất của Lá Chắn T-084 (chủ dự án dặn 27/10 «vấn đề có đề xuất thì làm theo đề xuất»): đặt `client.showErrorDetails = "type"` trong `.streamlit/config.toml` để trang lỗi không in traceback có đường dẫn cài đặt; kiểm `tests/test_app_pages.py` và các test đọc cấu hình Streamlit vẫn qua.

## Yêu cầu bảo mật riêng

W1, W2, U1.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Mọi test luồng gửi nháp và kho nháp + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-092-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W1, W2, U1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo «cứ làm liên tục, không cần hỏi».

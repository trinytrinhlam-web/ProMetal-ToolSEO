# T-023 · Bật nút Kiểm tra khóa ChatGPT và Gemini trong Cài đặt

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-018 (nhánh `team/T-023` tạo từ `team/T-018`) |
| Trạng thái | Đã giao |

## Mục tiêu

Ở **Cài đặt → 🔌 Kết nối**, chủ dự án bấm **Kiểm tra** được cả khóa ChatGPT và Gemini, như khóa Claude. Biết ngay khóa dùng được hay không trước khi viết bài.

## Bối cảnh

- T-018 (Thợ Máy) đã làm `env_file.check_api_key` cho cả 3 khóa: trả `ok` / `invalid` / `unknown` / `missing`, không còn `unsupported` (`docs/team/reports/T-018-tho-may.md`).
- Giao diện hiện chỉ bật nút cho Claude: `app/views/settings.py`, biến `CHECKABLE_KEYS`; chú thích nút còn ghi "chờ cài thư viện của hãng".
- Test `tests/test_settings_keys.py::test_check_only_for_claude` mang tên và nội dung theo hành vi cũ.

## Phạm vi

- **Được sửa:** `app/views/settings.py` (chỉ phần tab "🔌 Kết nối"), test giao diện liên quan trong `tests/test_settings_keys.py` (đổi theo hành vi mới, không nới lỏng kiểm tra bảo mật).
- **Không được sửa:** `seo_app/**` (logic thuộc Thợ Máy), `config/**`, các tab khác của Cài đặt (thử mù làm ở T-019).
- **Ngoài phạm vi:** tab "🤖 Mô hình AI" (T-019).

## Yêu cầu

1. Nút **Kiểm tra** bật cho cả 3 khóa khi khóa đã khai báo. Bỏ câu "chờ cài thư viện của hãng".
2. Kết quả kiểm tra hiện đúng màu: `ok` xanh, `invalid` đỏ, còn lại vàng. Câu thông báo lấy nguyên từ `check_api_key` (đã che khóa).
3. Vẫn **không bao giờ** hiện giá trị khóa, kể cả vài ký tự.
4. Đổi tên và nội dung test cũ theo hành vi mới. Thêm test: bấm Kiểm tra cho ChatGPT và Gemini gọi đúng `check_api_key` với tên biến tương ứng (dùng hàm giả, không gọi mạng). Thông báo trên trang không chứa khóa giả.
5. Trang vẫn qua `tests/test_app_pages.py`. Giữ bố cục đã duyệt.

## Yêu cầu bảo mật riêng

S2, U1 (không hiện khóa; thông báo hiện bằng `st.success` / `st.error` / `st.warning`, không qua HTML), D3.

## Tiêu chí xong

- [ ] Ba nút Kiểm tra hoạt động, có test
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-023-hoa-si.md`, kèm hướng dẫn chủ dự án tự mở app kiểm tra

## Kiểm thử và kiểm định

- Soi Lỗi: Có (gộp chung lượt kiểm thử với T-018 nếu kịp).
- Lá Chắn: Có (S2, U1).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Họa Sĩ · T-023 Nút Kiểm tra khóa"**, trên nhánh tạm `team/T-023` (tạo từ `team/T-018`). Commit và đẩy lên `team/T-023`; không đẩy `main`. Chỉ Huy gộp vào `main` sau khi T-018 và T-023 cùng qua Lá Chắn.

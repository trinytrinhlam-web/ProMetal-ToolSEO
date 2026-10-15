# T-031 · Địa chỉ trần và email trong chữ AI không được thành link bấm được

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình (chữ AI hiện trên mọi trang có bài; Giai đoạn 5 bắt buộc phải xử lý trước khi gửi WordPress) |
| Phụ thuộc | T-019 đã gộp vào `main` (T-019 cũng sửa phần che tên trong chữ AI; tránh hai phiếu cùng sửa một chỗ) |
| Trạng thái | Mới |

## Mục tiêu

Chữ do AI viết hiện trên trang Soạn bài và trang Thử mù không bao giờ chứa link bấm được, kể cả địa chỉ trần hay email.

## Bối cảnh

- Soi Lỗi phát hiện khi kiểm T-019 (`docs/team/reports/T-019-soi-loi.md`): địa chỉ trần `https://…`, `www.…` và email trong chữ AI vẫn thành link bấm được. Lý do: Streamlit hiện chữ bằng Markdown kiểu GFM, tự biến các dạng này thành link (autolink), mà `seo_app/sanitize.py::clean_ai_text` chỉ vô hiệu link dạng `[chữ](địa chỉ)` và thẻ HTML.
- Lỗi có ở mọi chỗ dùng `clean_ai_text`, gồm trang Soạn bài.
- Lá Chắn và Soi Lỗi đã nêu từ T-015 cho Giai đoạn 5 (`docs/team/board.md`, mục "Việc bắt buộc khi làm Giai đoạn 5"): URL trần có thể bị GFM tự biến thành link.
- T-026 đã gặp đúng dạng này với mã lỗi `www.evil.com` và xử lý riêng ở `safe_code`.

## Phạm vi

- **Được sửa:** `seo_app/sanitize.py`, test mới cho phần mình làm.
- **Không được sửa:** `app/**`, `config/**`, `tests/conftest.py`.
- **Ngoài phạm vi:** chuyển Markdown sang HTML cho WordPress (Giai đoạn 5).

## Yêu cầu

1. Sau `clean_ai_text`, chữ hiện qua `st.markdown` của Streamlit (GFM, có autolink `www.`, `http(s)://`, email) không còn link nào. Cách làm do Thợ Máy chọn, ví dụ chèn ký tự ngắt vô hại vào đúng chỗ autolink nhận diện, nhưng người đọc vẫn đọc được địa chỉ.
2. Không làm hỏng chữ tiếng Việt bình thường, số, dấu câu; không làm hỏng round-trip ở ô sửa chữ (T-012: ô sửa không hiện dấu `\`).
3. Test cho các dạng: `https://`, `http://`, `www.`, chữ hoa (`WWW.`), email, địa chỉ có dấu câu ở cuối, địa chỉ trong ngoặc, địa chỉ có ký tự Unicode/punycode, và chữ thường có dấu chấm (không bị đổi thừa).
4. Kiểm bằng bộ đọc Markdown giống Streamlit (Lá Chắn và Soi Lỗi từng dùng `markdown-it-py` + `linkify-it-py` qua `uv run --with`, không thêm vào dự án).

## Yêu cầu bảo mật riêng

A2 (kết quả AI là dữ liệu chưa tin cậy), U1.

## Tiêu chí xong

- [ ] Không còn link bấm được với mọi dạng ở yêu cầu 3, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-031-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có.
- Lá Chắn: Có (A2, U1).

## Ghi chú của Chỉ Huy

- Làm trên nhánh tạm `team/T-031`, tạo từ `main` sau khi T-019 đã gộp.

# T-044 · Tên site và tên người dùng lấy từ WordPress hiện an toàn

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-16 |
| Giai đoạn | Giai đoạn 2 (dọn lỗi giao diện) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-031 đã gộp (dùng `escape_markdown` hoặc `escape_link_syntax` phiên bản mới) |
| Trạng thái | Chờ T-031 |

## Mục tiêu

Chữ lấy từ WordPress (tên site, tên người dùng, tên chuyên mục, thẻ…) hiện trên trang **Kết nối WordPress** chỉ là chữ thường, không thành link, không thành định dạng Markdown.

## Bối cảnh

Soi Lỗi phát hiện khi kiểm T-031 (`docs/team/reports/T-031-soi-loi.md`, SL-T031-1). `app/views/wordpress.py:41-42` hiện `site_name`, `user_name` bằng Markdown mà không escape, nên một tên có `[chữ](https://…)` hoặc địa chỉ trần sẽ thành link bấm được. Nguồn là site của chính chủ dự án, nên rủi ro thấp, nhưng nên sửa cho nhất quán.

## Phạm vi

- **Được sửa:** `app/views/wordpress.py`, test giao diện.
- **Không được sửa:** `seo_app/**`.

## Yêu cầu

1. Rà toàn bộ `app/views/wordpress.py`. Mọi chữ lấy từ WordPress phải hiện bằng `st.text`, `st.code`, hoặc Markdown sau `escape_markdown`, không bao giờ qua `unsafe_allow_html`. Áp dụng cho tên site, tên người dùng, chuyên mục, thẻ, tiêu đề bài nháp, thông báo lỗi.
2. Giữ bố cục đã duyệt.
3. Test bằng `AppTest` với client giả trả tên có link Markdown, địa chỉ trần, thẻ HTML. Trên trang không có link nào.
4. `tests/test_app_pages.py` vẫn qua.

## Yêu cầu bảo mật riêng

U1, D3.

## Tiêu chí xong

- [ ] Không chữ nào từ WordPress thành link hay HTML trên trang, có test
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-044-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (U1).

## Ghi chú của Chỉ Huy

- Phiên **"Họa Sĩ · T-044 Tên site từ WordPress hiện an toàn"**, nhánh `team/T-044` (từ `main` sau khi T-031 gộp).

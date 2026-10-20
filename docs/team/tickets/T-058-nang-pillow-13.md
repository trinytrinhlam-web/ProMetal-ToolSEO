# T-058 · Pillow 12.3.0 có lỗ hổng mới: nâng lên Pillow 13 hoặc chấp nhận rủi ro

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) nếu chủ dự án chọn nâng; Chỉ Huy ghi sổ rủi ro nếu chủ dự án chấp nhận |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Cao (chặn T-049: Lá Chắn T-047 ghi T-049 sẽ KHÔNG ĐẠT nếu chưa có phiếu này) |
| Phụ thuộc | T-047 đã gộp (`d350aec`). Chủ dự án chọn **A** ngày 2026-10-20 |
| Trạng thái | Chờ chỗ trống (chủ dự án đã chọn A) |

## Mục tiêu

Trước khi phần mềm bắt đầu giải mã ảnh thật bằng Pillow (T-049), xử lý xong các lỗ hổng của Pillow 12.3.0.

## Bối cảnh

Lá Chắn T-047 (`docs/team/reports/T-047-la-chan.md`, tra ngày 2026-10-19):

- Kho `python-pillow/Pillow` công bố 53 khuyến cáo (GHSA) ngày 17/10 (1 nghiêm trọng, 14 cao), bản vá chỉ có ở **Pillow 13.0.0**. pip-audit, OSV và kho khuyến cáo chung của GitHub chưa có các mục này.
- Đáng lo nhất: GHSA-8g5g-8vmr-9782 (tràn bộ nhớ khi thu nhỏ JPEG qua `thumbnail()`/`draft()`; giới hạn `formats=["JPEG"]` không chặn được).
- Streamlit 1.65 và 1.66 khóa `pillow<13`, nên `uv` không tự nâng được.
- Hiện chưa có code nào đưa ảnh vào Pillow; Pillow 12.3.0 đã có trên `main` từ trước (Streamlit kéo theo).

## Hai lựa chọn (chủ dự án quyết)

- **A. Nâng Pillow 13.0.0** bằng `[tool.uv] override-dependencies` (vượt ràng buộc `pillow<13` của Streamlit). Phải chạy đủ test, mở app thử thật mọi trang (Streamlit dùng Pillow cho `st.image`), ghi lại cách quay về nếu hỏng.
- **B. Chấp nhận rủi ro**: giữ Pillow 12.3.0 tới khi Streamlit cho phép bản 13; ghi vào `docs/team/security.md` mục 6, chủ dự án ký. T-049 khi đó phải tránh `thumbnail()`/`draft()`, `seek()`, không ghi JPEG (điều kiện Lá Chắn T-047).

## Phạm vi (nếu chọn A)

- **Được sửa:** `pyproject.toml`, `uv.lock`, test nhỏ xác nhận phiên bản Pillow.
- **Không được sửa:** code ứng dụng.

## Yêu cầu (nếu chọn A)

1. `override-dependencies = ["pillow>=13.0.0,<14"]` (hoặc tương đương), `uv lock`, ghi phiên bản, thư viện đổi theo.
2. `uvx pip-audit` toàn bộ `uv.lock`; tra lại khuyến cáo của kho `python-pillow/Pillow` cho bản 13.
3. `uv run pytest` 0 hỏng trên Windows; Chỉ Huy mở app (`uv run streamlit run app/main.py`) xem mọi trang không lỗi.

## Yêu cầu bảo mật riêng

D1, D3.

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Có (D1).

## Ghi chú của Chỉ Huy

- Lá Chắn T-047 khuyên nâng (A). Đã hỏi chủ dự án 2026-10-19.
- 2026-10-20 07:31 (Chỉ Huy A): chủ dự án chọn **A: nâng lên Pillow 13**. Giao Thợ Máy ngay khi có chỗ trống (đang đủ 3 agent). Ưu tiên trước mọi phiếu khác vì chặn T-049.

# T-074 · Dọn thẻ ảnh lượt 2 (sau T-070)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (Lá Chắn T-070 ghi: phải gộp trước T-056) |
| Phụ thuộc | T-070 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Kho thẻ sửa tay (`data/image_tags.sqlite`) không bị lách lớp kiểm cấu trúc, không treo vì dữ liệu quá lớn; nhận ảnh AI theo tên chính xác hơn.

## Bối cảnh

Biên bản Lá Chắn T-070 (`docs/team/reports/T-070-la-chan.md`, điều kiện 1) và báo cáo Soi Lỗi T-070 (`docs/team/reports/T-070-soi-loi.md`); test `xfail` trong `tests/test_soi_loi_t070.py`.

## Phạm vi

- **Được sửa:** `seo_app/storage/image_tags.py`, `seo_app/images/tags.py`, `tests/test_images_tags.py`, gỡ `xfail` trong `tests/test_soi_loi_t070.py`.
- **Không được sửa:** `seo_app/storage/drafts.py` (T-055), `app/**`, `config/**`.

## Yêu cầu

1. **LC-T070-1 (= SL-T070-1):** `_app_tables` đọc vào danh sách; hơn số dòng mong đợi hoặc có dòng trùng thì trả `None` (coi như file lạ).
2. **LC-T070-2:** kiểm cấu trúc trong **cùng giao dịch** với thao tác (`BEGIN IMMEDIATE` cho ghi, `BEGIN` cho đọc, trước `_app_tables`); `_prepare` kiểm trong giao dịch trước `CREATE`/`INSERT`. Test giả lập như T2 của biên bản.
3. **SL-T070-2:** `setlimit(SQLITE_LIMIT_LENGTH, …)` trong `_guard`; coi `SQLITE_TOOBIG` là hỏng ở `_is_healthy` (và đặt lại `_ready`); sửa lời "không làm treo app" ở docstring `image_tags.py` cho đúng.
4. **SL-T070-3:** tên file tách thêm ở chỗ chữ ↔ số (giữ "xAI3kQ" là ảnh thật); xét thêm "AIgen".
5. **SL-T070-5:** thêm `mô phỏng` vào `_AI_PHRASES`.
6. Gỡ `xfail` khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

A3, F1, F3.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py tests/test_images_folders.py tests/test_ai_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-074-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (A3, F1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-070. Làm trên nhánh tạm `team/T-074`, tạo từ `main` sau khi T-070 gộp.
- **Hoãn** (theo quyết định chủ dự án 20/10 "hoãn lỗi nhỏ không chặn"; Lá Chắn T-070 cũng khuyên hoãn): SL-T070-4 (tên riêng thật trùng tên công cụ AI thành ảnh AI, không đổi lại được trong app: hướng an toàn, chỉ nói ít hơn sự thật) và LC-T052-5 (khe khi SQLite tạo file journal). Không làm trong phiếu này.

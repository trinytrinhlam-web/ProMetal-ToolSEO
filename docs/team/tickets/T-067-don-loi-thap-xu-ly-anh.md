# T-067 · Dọn lỗi Thấp xử lý ảnh (sau T-049)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (LC-T049-1 chặn gộp T-054; LC-T049-2, -3 chặn gộp T-056) |
| Phụ thuộc | T-049 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Sửa 3 lỗi Thấp Soi Lỗi và Lá Chắn ghi ở T-049, để GPS sai khuôn không bị hiểu sai bán cầu, ảnh xem trước luôn kiểm phiên bản Pillow, và mở ảnh từ nhiều phiên Streamlit cùng lúc không để lại bộ lọc cảnh báo sai.

## Bối cảnh

Biên bản Lá Chắn T-049 (`docs/team/reports/T-049-la-chan.md`, điều kiện 1) và báo cáo Soi Lỗi T-049 (`docs/team/reports/T-049-soi-loi.md`): LC-T049-1 (= SL-T049-1), LC-T049-2 (= SL-T049-2), LC-T049-3 (= SL-T049-3); 3 test `xfail` trong `tests/test_soi_loi_t049.py`.

## Phạm vi

- **Được sửa:** `seo_app/images/process.py`, `tests/test_images_process.py`, gỡ `xfail` trong `tests/test_soi_loi_t049.py`.
- **Không được sửa:** `seo_app/images/folders.py`, `tags.py`, `alt.py`, `app/**`, `config/**`.

## Yêu cầu

1. **LC-T049-1:** thẻ chỉ hướng GPS sai khuôn (`"s"`, `"w"` chữ thường; `GPSAltitudeRef` sai kiểu) → coi GPS hỏng: bỏ cả khối GPS và báo qua `WebImage.notice`, không lặng lẽ hiểu là Bắc/Đông.
2. **LC-T049-2:** gọi `_require_pillow_13()` ở đầu `PreviewCache.get` (trước khi trả ảnh có sẵn trong cache).
3. **LC-T049-3:** khóa `threading.Lock` quanh đoạn mở ảnh có `warnings.catch_warnings()`, giữ đúng bộ lọc cảnh báo khi nhiều phiên mở ảnh cùng lúc.
4. Gỡ 3 dấu `xfail` khi XPASS, không đổi điều kiện kiểm. Có thể làm thêm N1, N4 trong biên bản Lá Chắn (không bắt buộc).

## Yêu cầu bảo mật riêng

F2, F3.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_ai_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-067-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn (gỡ `xfail`, thử lại 3 ca). Lá Chắn: Rút gọn (soát diff).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-049. Làm trên nhánh tạm `team/T-067`, tạo từ `main` sau khi T-049 gộp.

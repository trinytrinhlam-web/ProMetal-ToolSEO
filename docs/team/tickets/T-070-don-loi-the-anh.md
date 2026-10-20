# T-070 · Dọn lỗi thẻ ảnh (sau T-052)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (có LC-T052-1 mức Trung bình; phải gộp trước T-056) |
| Phụ thuộc | T-052 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Ảnh AI không bị coi là ảnh thật vì tên thư mục hay tên file dùng cách gọi chưa có trong danh sách; file thẻ độc trong `data/` không làm treo hay hỏng phần thẻ sửa tay.

## Bối cảnh

Biên bản Lá Chắn T-052 (`docs/team/reports/T-052-la-chan.md`, điều kiện 1): LC-T052-1 (Trung bình), LC-T052-2, LC-T052-3, LC-T052-5 (Thấp); báo cáo Soi Lỗi T-052 lượt 2: SL-T052-9 → -11 (`xfail` trong `tests/test_soi_loi_t052.py`).

## Phạm vi

- **Được sửa:** `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, `tests/test_images_tags.py`, gỡ `xfail` trong `tests/test_soi_loi_t052.py`.
- **Không được sửa:** `seo_app/images/folders.py`, `process.py`, `alt.py`, `app/**`, `config/**`.

## Yêu cầu

1. **LC-T052-1 (a)–(d), SL-T052-11:** thêm dấu hiệu ảnh AI: `minh họa` (cả không dấu), `trí tuệ nhân tạo`, `GenAI` (dạng liền), Copilot, Designer, Bing Image Creator, Leonardo, Ideogram, Flux, Grok, Kling, Dreamina, ComfyUI, Runway, Krea, Seedream (Canva: cân nhắc, ghi lý do). Test cả tên thư mục lẫn tên file mặc định của các công cụ. Thêm hàm công khai `is_ai_name(name) -> bool` để T-056 dùng. Không chặn nhầm ảnh thật (có test đối chứng).
2. **LC-T052-2, SL-T052-9, SL-T052-10:** `_is_healthy` kiểm `sqlite_master` khớp đúng trước mọi truy vấn khác (chỉ 2 bảng, đúng câu `CREATE TABLE`, không VIEW/TRIGGER/bảng ảo/`WITHOUT ROWID`); đặt lại `_ready` khi lỗi "no such table/column"; cân nhắc `set_progress_handler`. Test ca `info` là khung nhìn, có trigger, `WITHOUT ROWID`.
3. **LC-T052-3:** `get_many` áp `_keep_ai` theo từng `ref` được hỏi; test ca đổi tên chỉ khác hoa thường.
4. **LC-T052-5:** chờ chủ dự án chọn: ghi sổ rủi ro (mở rộng dòng LC-T048-6 cho file trong `data/`) hay đặt `PRAGMA journal_mode = MEMORY`. Chưa có quyết định thì để nguyên và ghi trong báo cáo.
5. Gỡ `xfail` khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

A3, F1, F3.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_images_folders.py tests/test_ai_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-070-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (A3, F1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-052. Làm trên nhánh tạm `team/T-070`, tạo từ `main` sau khi T-052 gộp.

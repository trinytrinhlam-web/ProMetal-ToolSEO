# T-077 · Dọn thẻ ảnh nhỏ (sau T-074): tên công cụ AI gõ khác dạng chuẩn

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-21 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (Lá Chắn T-074: **phải gộp trước T-056**) |
| Phụ thuộc | T-074 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Thư mục hay file ảnh AI đặt tên công cụ theo kiểu "MidJourney", "Mid Journey", "Co-Pilot" không còn bị coi là ảnh thật; lần lưu thẻ ở tab khác không phải chờ khi một tab đang đọc rất nhiều thẻ.

## Bối cảnh

Biên bản Lá Chắn T-074 (`docs/team/reports/T-074-la-chan.md`, điều kiện 1) và báo cáo Soi Lỗi T-074 (`docs/team/reports/T-074-soi-loi.md`); test `xfail` trong `tests/test_soi_loi_t074.py` và `tests/test_la_chan_t074.py`.

## Phạm vi

- **Được sửa:** `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, `tests/test_images_tags.py`, gỡ `xfail` ở `tests/test_soi_loi_t074.py` và `tests/test_la_chan_t074.py`.
- **Không được sửa:** `seo_app/storage/drafts.py`, `seo_app/images/folders.py`, `app/**`, `config/**`.

## Yêu cầu

1. **LC-T074-1 (gồm SL-T074-2), bắt buộc:** `_parse_dir_name` đọc thêm kiểu không tách chữ hoa (`… or _has_ai_marker(cleaned, split_case=False)`); thêm `"Mid Journey"`, `"Fire Fly"`, `"Co Pilot"`, `"See Dream"` vào `_AI_TOOLS`. Không ghép bừa mọi cặp chữ liền nhau; giữ ca đối chứng của `tests/test_la_chan_t074.py` (tên ảnh thật vẫn là ảnh thật).
2. **SL-T074-1, nên làm cùng:** `get_many` đọc hết các dòng trong giao dịch, xử lý sau (như cách thử E3b của Soi Lỗi); mọi câu SQL vẫn nằm trong giao dịch đã kiểm (giữ LC-T070-2).
3. Sửa lời docstring `image_tags.py:19-21` cho đúng với chế độ WAL.
4. Gỡ `xfail` khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

A3, F1, F3.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py tests/test_soi_loi_t074.py tests/test_la_chan_t074.py tests/test_images_folders.py tests/test_ai_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-077-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (A3).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-074. Làm trên nhánh tạm `team/T-077`, tạo từ `main` sau khi T-074 gộp. Phải gộp trước T-056. Trong lúc chờ: đặt tên thư mục ảnh AI theo cách viết liền chuẩn (Midjourney, Firefly, Copilot).

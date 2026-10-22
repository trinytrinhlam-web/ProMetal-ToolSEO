# T-071 · Dọn lỗi Thấp phần chèn ảnh vào nháp (sau T-054)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi gộp T-056) |
| Phụ thuộc | T-054 đã gộp; nên sau T-070 (cần `ImageTags` ổn định) |
| Trạng thái | Đang làm |

## Mục tiêu

Phần gửi nháp kèm ảnh báo đúng khi bài nháp có thể đã được tạo, không còn dấu `\` thừa trong alt ảnh AI, kiểm mã ảnh trả về, và chỉ nhận thẻ đã chuẩn hóa.

## Bối cảnh

Biên bản Lá Chắn T-054 (`docs/team/reports/T-054-la-chan.md`, điều kiện 5) và báo cáo Soi Lỗi T-054 (`docs/team/reports/T-054-soi-loi.md`).

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py` (phần gửi nháp kèm ảnh), `seo_app/images/html.py`, `tests/test_wordpress_images.py`, gỡ `xfail` trong `tests/test_soi_loi_t054.py`.
- **Không được sửa:** `seo_app/sanitize.py` (phần shortcode thuộc T-061), `app/**`, `config/**`.

## Yêu cầu

1. **LC-T054-2 (= SL-T054-3):** lỗi ở lệnh tạo nháp mà không phải 4xx rõ ràng (hết giờ, mất mạng, 5xx, 201 sai dạng) thì báo bài nháp **có thể đã có** (người dùng kiểm trên WordPress trước khi gửi lại); sửa tài liệu `DraftImagesError` cho đúng.
2. **LC-T054-3 (= SL-T054-1):** alt, chú thích ảnh AI mở đầu `[…]:` không còn dấu `\` khi lên website (gỡ escape đúng chỗ, sau khi ghép tiền tố).
3. **LC-T054-5:** lệnh tải ảnh kiểm mã `201 Created`; website trả cùng một mã ảnh cho hai lần tải trong một lần gửi thì báo lỗi, không ghi đè alt.
4. **LC-T054-6:** chốt cuối của `figure_html` chỉ tìm ` src="…"`, ` alt=` trong thẻ `<img>`, không trong chữ chú thích.
5. **LC-T054-4 (phần code):** `DraftImage` nhận `ImageTags` (T-052) thay cho chữ tự do `category`, `area`, `project_code`, để code tự bảo đảm điều kiện 4 của Lá Chắn T-049 (tên file không mang chữ ngoài danh sách cố định).
6. Gỡ `xfail` SL-T054-1, -3 khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

W1–W4, 2.3, F2.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_wordpress_images.py tests/test_soi_loi_t054.py tests/test_wordpress*.py tests/test_images_tags.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-071-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W1–W4).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 5 của Lá Chắn T-054. Làm trên nhánh tạm `team/T-071`, tạo từ `main` sau khi T-054 gộp.
- 2026-10-22 18:07 (Chỉ Huy B): giao (chủ dự án "tiếp tục"). Nhánh `team/T-071` tạo từ `main` sau khi gộp T-039, T-069. Phiếu trước T-056.

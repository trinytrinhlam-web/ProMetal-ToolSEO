# T-088 · Dọn lỗi Thấp client WordPress sau T-085 (SL-T085-1, -2, -3, LC-T085-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-26 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 4; SL-T085-1 bắt buộc trước phiếu nào đưa giá trị tham số lấy từ dữ liệu ngoài vào `_request`) |
| Phụ thuộc | T-085 đã gộp |
| Trạng thái | Đang làm |

## Mục tiêu

Đóng nốt các lỗi Thấp ở client WordPress mà vòng kiểm T-085 để lại: lối vòng NUL của `_fields`, trả lời lồng quá sâu làm lỗi đỏ Python, câu báo khi lệnh tải ảnh lỗi giữa chừng.

## Bối cảnh

Biên bản Lá Chắn T-085 (`docs/team/reports/T-085-la-chan.md`, mục Điều kiện 1–3) và báo cáo Soi Lỗi T-085 (`docs/team/reports/T-085-soi-loi.md`):

- **SL-T085-1:** `_fields` có ký tự NUL sát tên trường vòng qua bộ chặn `content`/`excerpt`/`description`/`caption` (WordPress tự cắt NUL).
- **SL-T085-2 + LC-T085-1:** `response.json()` (`_json`, `_error_from`) để lọt `RecursionError` hay lỗi giải mã lạ (trả lời lồng quá sâu) → trang Kết nối WordPress hiện lỗi đỏ Python; câu «thư viện Media» của `upload_media` phải hiện cả khi lỗi lạ.
- **SL-T085-3:** lỗi không phải lời từ chối 4xx rõ ràng ở lệnh tải ảnh của `upload_media` (5xx, hết giờ, mất kết nối, `201` hỏng thân) thì câu báo chỉ «thử lại sau»; phải dặn ảnh có thể đã lên thư viện Media.

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py`, test mới; gỡ `xfail` trong `tests/test_soi_loi_t085.py` (27 + 3 + 6 ca) và `tests/test_la_chan_t085.py` (4 ca) khi XPASS (chỉ xóa dấu).
- **Không được sửa:** `app/**`, `config/**`; tên, chữ ký, hành vi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`.

## Yêu cầu

1. **SL-T085-1:** `_fields` có NUL (và khoảng trắng kiểu `trim()`: `" \t\n\r\0\x0b"`) sát tên trường bị chặn như tên trường thường.
2. **SL-T085-2 + LC-T085-1:** mọi chỗ đọc JSON trả lời không để lọt `RecursionError` hay lỗi giải mã lạ; ra câu cố định tiếng Việt kèm mã HTTP; câu «thư viện Media» của `upload_media` hiện cả khi lỗi lạ.
3. **SL-T085-3:** lệnh tải ảnh của `upload_media` lỗi không phải lời từ chối 4xx rõ ràng thì dặn «ảnh có thể đã lên thư viện Media, kiểm Media → Thư viện trước khi tải lại».
4. Không chặn oan lệnh thật (gồm luồng «Gửi nháp» của T-056/T-086 và trang Kết nối WordPress).
5. Gỡ `xfail` khi XPASS.

## Yêu cầu bảo mật riêng

W2, W3, S2.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan (các file test WordPress, `tests/test_soi_loi_t085.py`, `tests/test_la_chan_t085.py`, `tests/test_wordpress_t085.py`, `tests/test_wordpress_t060.py`, `tests/test_app_pages.py`, `tests/test_app_images.py`) qua, `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-088-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W2, W3, S2).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1–3 của Lá Chắn T-085; chủ dự án duyệt 2026-10-26. Làm song song với T-041 (không chung file).

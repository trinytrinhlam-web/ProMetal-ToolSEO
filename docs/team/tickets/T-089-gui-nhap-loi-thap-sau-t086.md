# T-089 · Dọn lỗi Thấp gửi nháp sau T-086 (LC-T086-1, SL-T086-1, -2; băm ảnh đã duyệt trong nháp)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`); được sửa phần trạng thái gửi và `DraftImage` trong `seo_app/storage/drafts.py` (việc Thợ Máy, Chỉ Huy duyệt cho Họa Sĩ làm để khỏi chia hai nhánh) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-26 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-086 đã gộp |
| Trạng thái | Soi Lỗi đạt có điều kiện, Lá Chắn đang kiểm |

## Mục tiêu

Đóng nốt các khe nhỏ của luồng «Gửi nháp» mà vòng kiểm T-086 để lại: hai tab cùng gửi một bài, mã bài lạ từ website làm trang lỗi, ảnh xem trước không khớp ảnh đã băm, và nháp mở lại không nhớ «dấu vân tay» ảnh đã duyệt.

## Bối cảnh

Biên bản Lá Chắn T-086 (`docs/team/reports/T-086-la-chan.md`, điều kiện 2, 3) và báo cáo Soi Lỗi T-086 (`docs/team/reports/T-086-soi-loi.md`):

- **LC-T086-1:** website trả mã bài từ 2⁶³ trở lên thì `record_outcome` ném lỗi ngoài khối bắt (dựng `SendState.now(...)` trước `try`), trang lỗi lặp lại (vẫn không gửi trùng).
- **SL-T086-1:** cùng một bài mở ở hai tab, bấm gửi cách nhau vài giây: ra hai bài nháp. Sửa: ghi «đang gửi» kiểu «so rồi đặt» trong một giao dịch SQLite.
- **SL-T086-2:** file bị thay tại chỗ (cùng cỡ, cùng giờ sửa) trước khi chọn: khung xem trước hiện ảnh cũ từ cache trong khi băm và dòng GPS là của ảnh mới. Sửa: ảnh xem trước dựng từ đúng byte đã băm.
- **Điều kiện 3 (Thợ Máy):** lưu băm ảnh đã duyệt trong `DraftImage` (Ghi nhận 1 Lá Chắn T-086; phần còn lại của SL-T056-2), để mở lại nháp vẫn so được ảnh với lúc duyệt.

## Phạm vi

- **Được sửa:** `app/views/write.py` (luồng gửi nháp, xem trước ảnh), `seo_app/storage/drafts.py` (trạng thái gửi, `DraftImage`; nháp cũ vẫn mở được, giữ `extra="forbid"`), test; gỡ `xfail` trong `tests/test_la_chan_t086.py`, `tests/test_soi_loi_t086.py` khi XPASS (chỉ xóa dấu).
- **Không được sửa:** `seo_app/wordpress/**` (T-088 đang sửa `client.py`), `seo_app/onpage/**`, `config/**`; khối SEO trong `drafts.py` (T-041 đang thêm).

## Yêu cầu

1. LC-T086-1: dựng `SendState` trong `try` của `record_outcome`; mã bài ngoài khoảng thì báo câu cố định, không lặp lỗi.
2. SL-T086-1: ghi «đang gửi» theo kiểu «so rồi đặt» trong một giao dịch; tab thứ hai bị khóa với câu nhắc rõ.
3. SL-T086-2: ảnh xem trước dựng từ đúng byte đã băm.
4. Lưu băm ảnh đã duyệt trong `DraftImage`; mở lại nháp mà ảnh khác băm thì bắt duyệt lại.
5. Giữ mọi test mới của T-086 (ngắt ở từng lần ghi, ngắt hai lần, trạng thái sửa tay, mã bài trong nháp không dùng để ghi lên website).

## Yêu cầu bảo mật riêng

W1, W2, U1, F2.

## Tiêu chí xong

- [ ] Yêu cầu 1–5, có test
- [ ] Test liên quan (`tests/test_app_images.py`, `tests/test_soi_loi_t056.py`, `tests/test_la_chan_t056.py`, `tests/test_soi_loi_t086.py`, `tests/test_la_chan_t086.py`, `tests/test_storage_drafts.py`, `tests/test_drafts_images.py`, `tests/test_app_pages.py`) qua, `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-089-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W1, W2, U1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 2, 3 của Lá Chắn T-086; chủ dự án duyệt 2026-10-26. Chạy song song với T-041 phần giao diện (cùng `write.py`, `drafts.py` nhưng khác chỗ: bước 5 gửi nháp và `DraftImage` so với bước 4 SEO và khối SEO); Chỉ Huy gộp lần lượt và xử lý xung đột nếu có.
- Phần không bắt buộc của Lá Chắn T-086 (giới hạn trên cho `_positive_id` trong client) để sau T-088 (cùng `client.py`).
- 2026-10-26 15:19 (Chỉ Huy B): **Họa Sĩ xong** (`87ad51c`, 5/5; gỡ 3 `xfail`; 39 file test liên quan 3.908 qua). Giao **Soi Lỗi rút gọn** (phiên Soi Lỗi T-056).
- 2026-10-26 19:22 (Chỉ Huy B): **Soi Lỗi rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`66131e5`): 1 Thấp SL-T089-1 (2 `xfail`). Giao **Lá Chắn rút gọn** (phiên Lá Chắn T-056).

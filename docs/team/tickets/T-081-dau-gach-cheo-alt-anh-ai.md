# T-081 · Bỏ dấu «\» sót ở alt, chú thích ảnh AI (SL-T071-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-23 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (phải xong trước khi gộp T-056) |
| Phụ thuộc | T-071 đã gộp vào `main` (test `xfail` của SL-T071-1 nằm trong `tests/test_soi_loi_t071.py`) |
| Trạng thái | Đang làm |

## Mục tiêu

AI viết mô tả ảnh kiểu «[Minh họa]: cổng inox…» thì alt và chú thích ảnh AI lên website không còn dấu «\» (ví dụ `Minh họa \: Cổng inox…`).

## Bối cảnh

Báo cáo Soi Lỗi T-071 (`docs/team/reports/T-071-soi-loi.md`, mục SL-T071-1):
- `escape_link_syntax` thêm «\» sau «]» của nhãn đầu dòng (`[Minh họa]\:`); `_strip_ai_prefix` (`seo_app/images/alt.py`) bỏ tiền tố AI tự viết **kèm dấu «]» đóng** nhưng để lại dấu «\» (không có trong `_AFTER_PREFIX`). Bước gỡ `]\:` của T-071 (`seo_app/images/html.py`) không còn thấy «]» nên không gỡ.
- Gặp với `[Minh họa]:`, `[Ảnh minh họa]:`, `[Hình minh họa]:`, `[Minh hoạ]:`, `[MINH HỌA]:`, `[Minh họa]:chữ`, `[Minh họa][cổng sắt] sơn đen` (dạng «[»: `Minh họa \[cổng sắt] sơn đen mờ`). Ảnh thật không bị.
- Có từ T-062. Chỉ là chữ xấu, không mở được link, thẻ hay shortcode (mọi «[» vẫn thành `&#91;`).

## Phạm vi

- **Được sửa:** `seo_app/images/alt.py`; test của phần này (`tests/test_t062_alt_prompt.py`, `tests/test_soi_loi_t062.py` chỉ thêm ca, hoặc file test mới); gỡ `xfail` SL-T071-1 trong `tests/test_soi_loi_t071.py` (2 ca, chỉ xóa dấu).
- **Không được sửa:** `seo_app/images/html.py`, `seo_app/wordpress/**`, `app/**`, `config/**`.

## Yêu cầu

1. Khi `_strip_ai_prefix` bỏ ngoặc đóng mà ngay sau còn dấu «\» do `escape_link_syntax` thêm (trước «:», «[», «(»), bỏ luôn dấu «\» đó; hoặc bỏ tiền tố trên chữ **chưa** escape. Chọn cách nào thì ghi lý do.
2. Đủ các biến thể ở mục Bối cảnh ra alt «Minh họa cổng inox…», chú thích «Ảnh minh họa (AI): cổng…», không «\».
3. Không nới chặn link, shortcode của T-061, T-062: mọi «[» «]» trần vẫn bị vô hiệu trước khi gửi WordPress; dấu «\» do người dùng hay AI gõ ở chỗ khác giữ nguyên ý nghĩa như trước.
4. Gỡ `xfail` 2 ca SL-T071-1 khi XPASS.

## Yêu cầu bảo mật riêng

W3 (mục 2.3), A3 theo mặc định.

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Test liên quan (`uv run pytest tests/test_soi_loi_t071.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t054.py tests/test_soi_loi_t068.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Có test cho phần logic mới
- [ ] Báo cáo nộp tại `docs/team/reports/T-081-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W3).

## Ghi chú của Chỉ Huy

- Lập từ điều kiện của Soi Lỗi T-071 (SL-T071-1). Chủ dự án chọn phiếu riêng (2026-10-23) để không phải kiểm lại T-071. Nhánh `team/T-081` tạo từ `main` sau khi gộp T-071.
- 2026-10-23 11:10 (Chỉ Huy B): T-071 đã gộp; nhánh `team/T-081` tạo từ `main` `c124b1a`, worktree `wt-T-081`. Giao Thợ Máy (chủ dự án duyệt "làm khi có agent rảnh").

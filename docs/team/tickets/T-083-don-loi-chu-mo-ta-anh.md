# T-083 · Dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI (SL-T068-1, -2, -3, LC-T068-1, SL-T081-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-23 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (làm sau T-056; không chặn T-056) |
| Phụ thuộc | T-081 đã gộp vào `main`; T-056 xong |
| Trạng thái | Đang làm |

## Mục tiêu

Alt và chú thích ảnh AI không còn lặp hay cụt chữ khi AI tự viết tiền tố theo kiểu lạ («Minh hoa», «- Minh họa», «`Minh họa`», «[Minh họa] (AI): …»), và chú thích ảnh AI ở giới hạn ký tự nhỏ không cụt tiền tố. Chỉ sửa câu chữ; tiền tố «Minh họa» / «Ảnh minh họa (AI)» luôn còn (C6), chặn link và shortcode giữ nguyên.

## Bối cảnh

- Báo cáo Soi Lỗi T-068 (`docs/team/reports/T-068-soi-loi.md`) và biên bản Lá Chắn T-068 (`docs/team/reports/T-068-la-chan.md`, mục "Đánh giá 3 lỗi Thấp", khuyến nghị gom vào một phiếu dọn nhỏ):
  - **SL-T068-1:** tiền tố AI tự viết không dấu, nối bằng gạch, thiếu ngoặc quanh «AI» hay gọi khác không được nhận ra, code ghép thêm tiền tố chuẩn nên lặp; alt chỉ «Minh hoa» vẫn nhận.
  - **SL-T068-2:** tiền tố trong dấu Markdown khác `*` (`` ` ``, `_`, `__`) hay sau dấu đầu dòng («- », «1. », «• ») không được nhận ra: lặp; chạy lại thì báo lỗi.
  - **SL-T068-3:** chú thích ảnh AI với `caption_max_chars` 20–21: thân còn 1–2 ký tự, cụt giữa chữ.
  - **LC-T068-1:** `caption_max_chars` nhỏ hơn 17 thì chú thích ảnh AI là tiền tố bị cắt cụt, không đủ «(AI)».
- Báo cáo Soi Lỗi T-081 (`docs/team/reports/T-081-soi-loi.md`): **SL-T081-1**: «(AI)» viết tách khỏi tiền tố («[Minh họa] (AI): Cổng inox») thì chú thích ra «Ảnh minh họa (AI): (AI): Cổng inox».
- Test `xfail(strict=True)` sẵn có: `tests/test_soi_loi_t068.py` (23 ca), `tests/test_soi_loi_t081.py` (5 ca).
- Chủ dự án duyệt 2026-10-23: gom thành một phiếu dọn, làm sau màn hình chọn ảnh T-056.

## Phạm vi

- **Được sửa:** `seo_app/images/alt.py`; nếu cần giới hạn dưới của `caption_max_chars` thì phần đọc cấu hình ảnh (Chỉ Huy xác nhận file trước khi sửa); test của phần này; gỡ `xfail` trong `tests/test_soi_loi_t068.py`, `tests/test_soi_loi_t081.py` (chỉ xóa dấu).
- **Không được sửa:** `seo_app/images/html.py`, `seo_app/wordpress/**`, `app/**`.

## Yêu cầu

1. Sửa SL-T068-1, -2, -3, LC-T068-1, SL-T081-1 theo gợi ý trong các báo cáo trên.
2. Giữ C6 (tiền tố AI luôn còn, alt chỉ có tiền tố thì từ chối) và lớp chặn link, shortcode của T-061, T-062, T-081.
3. Kết quả bất động: chạy lại `clean_suggestion` trên chính kết quả không đổi chữ.
4. Gỡ `xfail` khi XPASS.

## Yêu cầu bảo mật riêng

W3 (mục 2.3), A3 theo mặc định.

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Test liên quan (`uv run pytest tests/test_soi_loi_t068.py tests/test_soi_loi_t081.py tests/test_t081_alt_gach_cheo.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t071.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Có test cho phần logic mới
- [ ] Báo cáo nộp tại `docs/team/reports/T-083-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W3).

## Ghi chú của Chỉ Huy

- Lập theo khuyến nghị gom của Lá Chắn T-068 và Soi Lỗi T-081; chủ dự án duyệt 2026-10-23.
- 2026-10-27 17:35 (Chỉ Huy B): chủ dự án duyệt làm ngay. Nhánh `team/T-083` từ `main` `b60054f`, worktree `wt-T-083`; giao Thợ Máy (phiên mới). Chạy song song T-082, T-083, T-084 (khác file).

# T-025 · Ổn định các test đo tốc độ chập chờn

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình (test đỏ oan làm chậm mọi lượt kiểm và lúc gộp) |
| Phụ thuộc | Không |
| Trạng thái | Đã giao |

## Mục tiêu

`uv run pytest` không còn đỏ oan vì test đo tốc độ, kể cả khi máy đang bận hay chạy nhiều phiên cùng lúc. Các test này vẫn phải bắt được code chạy chậm theo kiểu bình phương như hiện nay.

## Bối cảnh

- `tests/timing.py` (T-015) so thời gian CPU giữa đầu vào cỡ nhỏ và cỡ gấp 4: tỉ lệ không quá 9 lần thì coi là "tuyến tính".
- Có hai test kiểm chính công cụ này: bản code bình phương (tỉ lệ khoảng 16) **phải** bị bắt. Hai test này chập chờn:
  - `tests/test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan`: hỏng 4/80 lần, **cả 4 đều ở lượt chạy đầu**, hay gặp khi có tiến trình khác chạy chồng. Xem `docs/team/reports/T-024-soi-loi.md` trên nhánh `team/T-024`.
  - `tests/test_soi_loi_round6.py::test_helper_catches_quadratic_function`: Ngòi Bút thấy hỏng 1/3 lần; Soi Lỗi chạy 50 lần không tái hiện được.
- Khi các test này hỏng, nghĩa là bản bình phương đo ra tỉ lệ dưới 9: cỡ nhỏ bị đo chậm bất thường (lượt đầu, bộ nhớ đệm nguội, CPU đổi xung nhịp) hoặc cỡ lớn bị đo nhanh bất thường.

## Phạm vi

- **Được sửa:** `tests/timing.py`, các test đo tốc độ trong `tests/` (`test_soi_loi_round6.py`, `test_soi_loi_round7.py` và test khác dùng `assert_scales_linearly`).
- **Không được sửa:** code ứng dụng (`seo_app/**`, `app/**`).
- **Ngoài phạm vi:** đổi thuật toán của `seo_app/sanitize.py`.

## Yêu cầu

1. Tìm nguyên nhân bằng số đo: in tỉ lệ đo được qua nhiều lần chạy, ở máy rảnh và máy bận (chạy song song 2–3 bản pytest). Ghi vào báo cáo.
2. Sửa cho ổn định **mà không nới lỏng**:
   - Bản bình phương vẫn phải luôn bị bắt.
   - Bản tuyến tính vẫn phải luôn được nhận.
   - Không tăng `MAX_RATIO`, không bỏ test, không `skip`, không thêm "chạy lại khi hỏng" để che lỗi thật.

   Gợi ý (tự đánh giá): chạy nháp cả cỡ lớn trước khi đo; đo xen kẽ nhỏ/lớn nhiều vòng rồi lấy trung vị tỉ lệ; với test "phải bắt bản bình phương" thì dùng cỡ đủ lớn để tỉ lệ thật xa ngưỡng.
3. Chứng minh: chạy mỗi test đã sửa ít nhất 100 lần (gồm cả lúc máy bận), 0 lần hỏng. Thời gian chạy toàn bộ test không tăng quá 20 giây.
4. Test phải chạy được trên Windows (đồng hồ CPU chỉ chính xác khoảng 15,6 ms) và Mac.

## Yêu cầu bảo mật riêng

D3 (test không gọi mạng). Theo mặc định.

## Tiêu chí xong

- [ ] 0 lần hỏng trong ít nhất 100 lần chạy mỗi test đã sửa, có số liệu trong báo cáo
- [ ] Bản bình phương vẫn bị bắt, bản tuyến tính vẫn qua
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-025-soi-loi.md`

## Kiểm thử và kiểm định

- Soi Lỗi: chính là người làm. Chỉ Huy soát lại số liệu.
- Lá Chắn: Rút gọn (chỉ soát bí mật; phiếu chỉ sửa test).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Soi Lỗi · T-025 Test đo tốc độ"**, trên nhánh tạm `team/T-025`. Commit và đẩy lên `team/T-025`; không đẩy `main`.

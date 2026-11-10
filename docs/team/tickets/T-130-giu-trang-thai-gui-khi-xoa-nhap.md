# T-130 · Giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa (khép khoảng hở cuối của T-092)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`); được sửa phần xóa nháp trong `seo_app/storage/drafts.py` như T-092 |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-05 |
| Giai đoạn | Giai đoạn 5 (trước khi bật công tắc Hẹn giờ/Đăng ngay) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-092 đã gộp `main` |
| Trạng thái | Xong (gộp `main` 2026-11-10) |

## Mục tiêu

Bịt nốt khoảng hở mà T-092 còn để lại: bài đã gửi lên website rồi bị xóa nháp ở một tab trong lúc tab khác chưa từng thấy lần gửi; tab đó lưu lại thì nháp mới **không có khóa gửi trùng**, bấm gửi là ra bài thứ hai trên website.

## Bối cảnh

- Báo cáo Họa Sĩ T-092 (`docs/team/reports/T-092-hoa-si.md`), mục «Rủi ro» 1 và «Đề xuất» 1, 2.
- Biên bản Lá Chắn T-092 (`docs/team/reports/T-092-la-chan.md`), mục điều kiện 1 và 3: khuyến nghị làm trước khi bật công tắc Hẹn giờ/Đăng ngay.
- Chỉ Huy quyết 2026-11-05: **làm** Đề xuất 1 và 2 (tăng chặn, không đổi quyết định nào của chủ dự án).

## Yêu cầu

1. **Đề xuất 1:** xóa một nháp **đã gửi** (hay đang gửi, gửi dở) thì giữ lại trạng thái gửi của nó (dòng «mồ côi» như SL-T089-2), để nháp tạo lại ở **bất kỳ** tab nào (kể cả tab chưa từng biết) vẫn mang khóa gửi trùng. Nháp chưa gửi thì xóa như cũ.
2. Cách dọn dòng mồ côi cũ, an toàn (không bao giờ xóa trạng thái của nháp còn tồn tại; có giới hạn số dòng hay tuổi; ghi rõ trong báo cáo).
3. **Đề xuất 2:** popover «🗑️ Xóa» của nháp đã gửi nhắc rõ: bài đã gửi lên website (mã …), xóa nháp **không** xóa bài trên website.
4. Không lùi T-086, T-089, T-092 (hai tab, ngắt giữa chừng, gửi dở, băm ảnh, tự lưu không tạo lại lặng lẽ).
5. Đổi test T-086 `test_send_state_removed_with_its_draft` (và test nào khác ghim hành vi «xóa nháp là xóa trạng thái gửi»): Chỉ Huy duyệt R5, ghi bảng cũ → mới.

## Phạm vi

- **Được sửa:** phần xóa nháp và dọn dòng mồ côi trong `seo_app/storage/drafts.py`, `app/views/write.py` / `app/views/home.py` (nơi có nút Xóa), test.
- **Không được sửa:** `seo_app/wordpress/**`, khối SEO trong `drafts.py`.

## Yêu cầu bảo mật riêng

W1 (không mở thêm đường gửi), W2 (không xóa gì trên website), U1.

## Tiêu chí xong

- [ ] Yêu cầu 1–5; test liên quan (kho nháp, gửi nháp, hai tab, T-086, T-089, T-092, `test_app_pages.py`) + `uv run ruff check .`
- [ ] Báo cáo `docs/team/reports/T-130-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: rút gọn (W1, W2, U1).

## Ghi chú của Chỉ Huy

- Lập 2026-11-05 theo điều kiện 1, 3 của Lá Chắn T-092. Worktree `wt-T-130`, nhánh `team/T-130` từ `main` có T-092.
- 2026-11-10 13:03 (Chỉ Huy B): Soi Lỗi `9e3971b` ĐẠT, Lá Chắn `b0a36ea` ĐẠT. Gộp `main` (`f084f5c`), Windows 24.109 test qua, 0 hỏng. Đã đẩy.

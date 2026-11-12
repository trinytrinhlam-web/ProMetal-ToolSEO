# T-137 · Nhắc chống gửi trùng sau khi file nháp bị cất sang một bên (SL-T136-1, G4)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-12 |
| Giai đoạn | Giai đoạn 5 (trước khi bật Hẹn giờ/Đăng ngay cho bài thật) |
| Mức ưu tiên | Trung bình (lỗi Thấp, nhưng nằm trên đường bật công tắc) |
| Phụ thuộc | T-136 (câu `MSG_RECOVERED`, `sqlite_file.newer_file_format`). Làm từ đầu nhánh `team/T-136` (`6a005c1`); T-136 gộp `main` rồi thì gộp `main` vào nhánh |
| Trạng thái | Đang làm |

## Mục tiêu

Khi file nháp bị chương trình khác làm hỏng và app cất nó sang một bên (`drafts.hong-*.sqlite`), dấu «đã gửi» của các bài nằm trong file cũ. Hiện người dùng có thể gửi trùng mà app không còn nhắc gì (Soi Lỗi SL-T136-1, Lá Chắn T-136 lượt 2: **Thấp**; khung «Xem lại trước khi gửi» **không** phải chốt chống gửi trùng). Phiếu này thêm một lời nhắc thường trực và một cổng tick, không nới khóa nào đã có.

## Bối cảnh

- Biên bản Lá Chắn `docs/team/reports/T-136-la-chan.md` mục «Lượt 2» (SL-T136-1, G4, hướng sửa).
- Soi Lỗi thử cục bộ G2 (WordPress giả, 52 bước): hai đường gửi trùng.
  - **Đường 1:** tab đã mở bài **trước** lần gửi ở tab khác. Khung vàng T-092 nói tab không biết, nhưng nút gửi không khóa. «Lưu lại thành nháp» làm mất khung. Hẹn giờ: tick «Tôi đã đọc lại…» là gửi được.
  - **Đường 2:** F5, tab mới hay mở lại app. «Bài đang soạn dở» rỗng, cột «Đã gửi WordPress» (trang Bài viết) ghi «Chưa có bài nào phần mềm đã gửi lên WordPress.», sai sự thật. Viết lại bài rồi gửi: không nhắc gì.
  - `MSG_RECOVERED` chỉ hiện **một lần**, ở trang đã cất file (`app/views/home.py` khoảng dòng 62–63; dòng «Chưa có bài nào…» khoảng dòng 299).
  - Byte 18 = 3: kho nháp dùng chung không kiểm lại khi chỉ đọc; file chỉ bị cất khi một trang mở kho mới, hay Soạn bài ghi lần hai (lần một báo «chỉ đọc»).

## Yêu cầu

1. **Dấu hiệu «đã có file nháp bị cất»** theo **tên file** `drafts.hong-*.sqlite` trong `data/`:
   - sống qua lần mở lại app;
   - kiểm sau `data_dir.dir_has_link` (như mọi kho);
   - khuôn tên chặt (đúng mẫu tên app đặt khi cất);
   - **không mở, không đọc** file đã cất (giữ hướng B.2 của T-136).
2. **Lời nhắc thường trực** ở cột «Đã gửi WordPress» của trang Bài viết thay cho «Chưa có bài nào…» khi có dấu hiệu ở mục 1: nói rõ dấu «đã gửi» của các bài trước nằm trong file đã cất, hãy xem trên WordPress trước khi gửi lại. Không in đường dẫn đầy đủ (tên file ngắn thì được, như `MSG_RECOVERED`).
3. **Cổng tick trước khi gửi:** khi có dấu hiệu ở mục 1, **mọi hình thức** (Nháp, Hẹn giờ, Đăng ngay) của bài **chưa có** dấu «đã gửi» trong kho hiện tại phải tick một ô kiểu «Tôi đã xem trên WordPress: bài này chưa có trên website» thì nút gửi mới mở. Ô **không tick sẵn**, đổi bài hay đổi nội dung thì bỏ tick (như ô xác nhận hiện có).
   - Chỉ **thêm** cổng: không nới T-089 (giành «đang gửi»), T-092 (tab khác xóa nháp), T-130 (xóa nháp giữ khóa), W1.
   - Nếu bài có «Mã bài WordPress» từ dòng kế hoạch (Google Sheet), nên nêu mã đó trong lời nhắc.
   - Người dùng bỏ file đã cất đi (xóa tay) thì lời nhắc, cổng tự hết. Ghi rõ trong README hay câu nhắc: muốn tắt nhắc thì làm gì (không tự xóa file).
4. **G4 (câu chữ):** SQLite báo mã 8 (READONLY) mà `sqlite_file.newer_file_format` đúng → coi là file lạ (cất, báo `MSG_RECOVERED`), không báo `_MSG_READONLY`.
5. **Test:** cả hai đường của Soi Lỗi (tab mở trước; F5/tab mới/mở lại app), ca không có file cất (không đổi gì), ca tên file gần giống mà sai khuôn, ca `data/` là liên kết; ca cổng tick bỏ tick khi đổi bài. AppTest không bấm được nút khóa: dùng cách vá `st.button` theo key kèm ca đối chứng. Tham số lớn kèm `ids=` ngắn.
6. README mục «Gửi nháp» (hay mục File nháp bị hỏng): một đoạn ngắn lời thường.

## Phạm vi

- **Được sửa:** `app/views/home.py`, `app/views/write.py` (hay mảnh bước Xuất bản), `seo_app/storage/drafts.py` (chỉ phần dò dấu hiệu và G4), `README.md` (đoạn ngắn), test.
- **Không được sửa:** logic giành/ghi trạng thái gửi, bộ dựng bài, client WordPress.

## Tiêu chí xong

- [ ] Yêu cầu 1–6; test liên quan + test mọi nơi gọi hàm sửa + `uv run ruff check .`; báo cáo `docs/team/reports/T-137-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ (chạy lại 52 bước G2 trên mã mới). Lá Chắn: **đầy đủ** (đụng cổng gửi; Opus 5.5 khi Fable hết hạn mức, ghi rõ model).

## Ghi chú của Chỉ Huy

- Lập 2026-11-12 theo Lá Chắn T-136 lượt 2 (`6a005c1`): sửa ở phiếu riêng **trước khi bật Hẹn giờ/Đăng ngay cho bài thật**, không chặn gộp T-136 và không chặn buổi thử thật. Worktree `wt-T-137`, nhánh `team/T-137` từ `team/T-136`.

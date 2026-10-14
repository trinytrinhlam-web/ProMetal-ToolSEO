# T-016 · Lưu nháp bài đang soạn (phần logic)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (hiện bấm F5 là mất bài) |
| Phụ thuộc | Không. T-017 (giao diện) làm sau phiếu này |
| Trạng thái | Đang làm |

## Mục tiêu

Bài đang soạn hiện chỉ nằm trong `st.session_state` (`app/views/write.py`), tải lại trang là mất. Cần một kho nháp cục bộ để giao diện tự lưu sau mỗi thay đổi và mở lại được.

## Yêu cầu

1. Module mới `seo_app/storage/` (đúng cấu trúc trong `CLAUDE.md`), chỉ dùng `sqlite3` có sẵn của Python, **không thêm thư viện**.
2. File dữ liệu mặc định `data/drafts.sqlite` trong thư mục app (đã nằm trong `.gitignore`), đường dẫn tính bằng `pathlib`; test dùng thư mục tạm, không bao giờ đụng file thật.
3. Khuôn dữ liệu `DraftSnapshot` (pydantic) chứa đủ để dựng lại trang Soạn bài: từ khóa, bước đang ở, chất liệu thật, kết quả nghiên cứu, dàn ý, tiêu đề bài, các phần (tiêu đề + mọi phiên bản + phiên bản đang chọn, để nút quay lại bản trước vẫn dùng được), lần rà soát, các gợi ý đã bỏ qua, thời điểm lưu (kèm múi giờ `Asia/Ho_Chi_Minh`). Đọc kỹ `init_state`, `set_outline`, `set_article` trong `app/views/write.py`.
4. Hàm: lưu (tạo mới hoặc ghi đè cùng mã nháp), đọc một nháp, liệt kê nháp mới nhất (tiêu đề, từ khóa, thời điểm lưu), xóa một nháp. Giữ tối đa 30 nháp, tự bỏ nháp cũ nhất.
5. Bảo mật:
   - Dữ liệu đọc từ file coi là chưa tin cậy: kiểm khuôn bằng pydantic, giới hạn kích thước (một nháp không quá vài MB), file hỏng hoặc sai khuôn thì bỏ qua nháp đó và báo lỗi dễ hiểu, không làm sập app.
   - Câu lệnh SQL luôn dùng tham số (`?`), không ghép chuỗi.
   - Không lưu khóa API, mật khẩu hay bất kỳ giá trị nào từ `.env`.
   - Không dùng `pickle`.

## Tiêu chí xong

- [ ] Test cho lưu, đọc lại đúng nguyên vẹn (kể cả chữ tiếng Việt và các phiên bản), liệt kê, xóa, giới hạn 30, file hỏng, nháp sai khuôn, nháp quá lớn
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-016-tho-may.md`, có mục "Cách giao diện dùng" để Họa Sĩ làm T-017

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

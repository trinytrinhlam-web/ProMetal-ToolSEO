# T-059 · Thử thật: tạo một bài nháp và ghi SEO lên site (có chủ dự án)

| Mục | Nội dung |
|---|---|
| Giao cho | Chỉ Huy (hướng dẫn chủ dự án), Thợ Máy (siết code theo kết quả) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-042 đã gộp; chủ dự án đã bật Abilities trong SiteSEO và tạo tài khoản Biên tập viên riêng (`TIEN-DO.md` mục 4) |
| Trạng thái | Chờ chủ dự án |

## Mục tiêu

Xác nhận trên site thật rằng phần mềm tạo được **một** bài nháp và ghi đúng tiêu đề, mô tả, từ khóa chính vào SiteSEO, không đụng gì khác.

## Bối cảnh

Lá Chắn T-042 (`docs/team/reports/T-042-la-chan.md`, cuối biên bản) liệt kê đầy đủ các bước. Website **không có site thử nghiệm**: chỉ làm trên bài nháp, chủ dự án tự xóa sau khi xong.

## Các bước

1. Chủ dự án bật Abilities trong SiteSEO, tạo tài khoản vai Biên tập viên riêng kèm Application Password, khai vào `.env` (qua Cài đặt → Kết nối), bấm Kiểm tra kết nối: thấy "SiteSEO: ghi được".
2. Thử **một** bài nháp có tiêu đề kèm `< 5 triệu` và `10%` (Soi Lỗi T-042 đề nghị). Ghi lại nguyên khuôn câu trả lời của `seo-data-update/run` (không có khóa, mật khẩu).
3. Mở trang quản trị: hộp SiteSEO hiện đúng chữ; canonical và robots để trống; bài vẫn là Nháp.
4. Kiểm LC-T042-3: gõ tay `[caption]` vào hộp SiteSEO của bài nháp, xem trang xem trước có chạy shortcode không.
5. Kiểm việc chặn: một nháp thứ hai do app tạo, chủ dự án chuyển sang "Chờ duyệt", rồi cho app ghi SEO: app phải từ chối. **Không đăng bài thật.**
6. Chủ dự án tự xóa các nháp thử.
7. Thợ Máy siết `_ability_confirms` theo khuôn câu trả lời thật (bỏ nhánh `{"success": true}`), có test; qua Soi Lỗi, Lá Chắn.

## Yêu cầu bảo mật riêng

R2, R3, W1–W4, S1 (không ghi khóa, mật khẩu vào báo cáo).

## Ghi chú của Chỉ Huy

- Giao diện công tắc "Ghi SEO lên website" thuộc T-041; phiếu này có thể thử bằng lệnh Python nhỏ do Chỉ Huy hướng dẫn nếu T-041 chưa xong.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-054** (điều kiện 6), khi thử thật một bài nháp có ảnh (sau T-056, T-061): tải file ảnh từ web về kiểm còn GPS; nguồn trang không có `srcset` cho ảnh; plugin nén ảnh/CDN không đổi file hay tên miền của `src`; chú thích `[caption]thu[/caption]` hiện nguyên văn trong nguồn trang.
- 2026-10-21 (Chỉ Huy B): **Điều kiện Lá Chắn T-061**: bước 4 xác nhận SiteSEO có chạy shortcode trong tiêu đề, mô tả SEO không (đóng LC-T061-2 nếu không); thử vòng sửa trong trang quản trị bằng shortcode vô hại `[caption]thu[/caption]` (LC-T061-4). Trước phiếu này: T-075 (`certifi`) phải gộp.
- 2026-10-23 11:10 (Chỉ Huy B): điều kiện 4 của **Lá Chắn T-071**: xác nhận `POST /wp/v2/media` trên site thật trả **201** (plugin, CDN, tường lửa không đổi mã); tải **cùng một ảnh** ở hai lần gửi khác nhau ra **hai mã khác nhau** (không plugin nào trả lại ảnh cũ). Sau T-056, trước khi dùng thật.
- 2026-10-27 17:35 (Chỉ Huy B): **chủ dự án duyệt tiến hành.** T-041 (công tắc «Ghi SEO lên website» trên bước SEO), T-056, T-086, T-088, T-089 đã gộp, nên thử qua giao diện app (không cần lệnh Python). Đã gửi chủ dự án danh sách việc trên website: bật Abilities trong SiteSEO, tạo tài khoản Biên tập viên riêng + Application Password, khai qua Cài đặt → Kết nối, Kiểm tra kết nối thấy «SiteSEO: ghi được»; xác nhận tắt «Enable file-based execution» của Code Snippets. Gộp các điều kiện T-054, T-061, T-071 vào lần thử: **một** bài nháp **một** ảnh, một tab.
- 2026-10-27 17:50 (Chỉ Huy B): chủ dự án không thấy mục Abilities: website chạy **SiteSEO 1.1.6** (readme công khai), Abilities có từ 1.4.0 (T-033 đọc mã 1.4.2, chưa xác minh bản trên site). Chủ dự án đã **cập nhật SiteSEO lên 1.4.2** (readme công khai xác nhận) và **bật Abilities**. Lưu ý: changelog wordpress.org ghi «AI Abilities Pro feature»; nếu Kiểm tra kết nối không ra «SiteSEO: ghi được» thì xét đường A (meta qua `wp/v2/posts`, không có từ khóa chính).

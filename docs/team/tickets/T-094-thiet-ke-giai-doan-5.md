# T-094 · Thiết kế Giai đoạn 5: kế hoạch, lịch, hẹn giờ và đăng bài

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Cao (mở đường cho cả giai đoạn) |
| Phụ thuộc | Không (chỉ tài liệu) |
| Trạng thái | Đang làm |

## Mục tiêu

Một báo cáo thiết kế đủ để chia Giai đoạn 5 thành các phiếu code nhỏ, giống T-033 (Giai đoạn 4) và T-046 (Giai đoạn 3): người dùng đưa kế hoạch vào app (tải file, dán chữ, link Google Sheets), AI đề xuất thay đổi để duyệt, đồng bộ Google Sheets, gửi bài lên WordPress dạng nháp, hẹn giờ (`future`) hoặc đăng ngay (`publish`, có xác nhận).

## Bối cảnh

- `CLAUDE.md`: quyết định đã chốt (dữ liệu dùng chung trên WordPress và Google Sheets, service account Google trong `.env`, mặc định nháp, đăng ngay phải bấm xác nhận, hẹn giờ bằng `future`), Lộ trình Giai đoạn 5.
- `docs/plan/`: kế hoạch SEO và yêu cầu phần mềm của chủ dự án.
- `docs/team/board.md` mục «Việc bắt buộc khi làm Giai đoạn 5»: các điều kiện Lá Chắn đã đặt (Markdown → HTML có escape, `sanitize_html` cho HTML cuối, màn hình xác nhận liệt kê mọi link, đúng một đường tới `publish`/`future`, gỡ ký tự rộng 0 của T-031…).
- Giao diện demo trang Kế hoạch đã duyệt (`app/views/`, `seo_app/demo.py`); trang Soạn bài bước 5 «Xuất bản» và nút «Gửi nháp» đã chạy thật (T-056, T-086, T-089), bước 4 SEO chạy thật (T-041).
- Thử thật T-059 (27/10): client gửi nháp, ghi SEO qua Abilities, ảnh còn GPS đã chạy trên site thật; tài khoản Biên tập viên có quyền `publish_posts`.

## Phạm vi

- **Được sửa:** chỉ báo cáo `docs/team/reports/T-094-tho-may.md`. Không sửa code, cấu hình, test.
- Được đọc mã nguồn và tài liệu công khai của thư viện Google (Sheets API, service account) và WordPress REST (`status` `future`, `date_gmt`). **Không** gọi website thật hay Google thật.

## Yêu cầu

1. Luồng người dùng từ kế hoạch tới bài đăng: nhận kế hoạch (3 cách), chuẩn hóa thành danh sách bài (từ khóa, ý định, ngày dự kiến, trạng thái), AI đề xuất thay đổi kèm lý do, người dùng tick duyệt, ghi lại Sheets; từ một dòng kế hoạch mở Soạn bài; sau khi gửi WordPress thì cập nhật trạng thái dòng đó.
2. Google Sheets: cách đọc/ghi bằng service account (quyền tối thiểu, chỉ file được chia sẻ), có cần thư viện mới không (nêu tên, lý do, phương án không thêm thư viện; **thêm thư viện cần chủ dự án duyệt**), cấu trúc trang tính đề xuất, xử lý xung đột khi hai máy cùng sửa, cache SQLite.
3. Hẹn giờ và đăng ngay: đúng một đường tới `future`/`publish` trong client (danh sách đường gọi cố định, xác nhận, múi giờ `Asia/Ho_Chi_Minh` → `date_gmt`), màn hình xác nhận (liệt kê link, ảnh GPS công khai, SEO), không bao giờ sửa bài đã đăng ngoài ý người dùng.
4. Đối chiếu từng điều kiện Lá Chắn trong board mục «Việc bắt buộc khi làm Giai đoạn 5»: làm ở phiếu nào.
5. Chia phiếu (khoảng 5–8 phiếu, mỗi phiếu nhỏ, có thứ tự và phụ thuộc, phiếu nào chạy song song được), ước lượng độ lớn.
6. Câu hỏi cho chủ dự án (đánh số, mỗi câu có lựa chọn A/B và khuyến nghị), gom ở cuối báo cáo.

## Yêu cầu bảo mật riêng

Đọc `docs/team/security.md`; nêu rủi ro từng phần (bí mật service account, chữ từ Google Sheets là dữ liệu chưa tin cậy, đường gọi WordPress mới).

## Tiêu chí xong

- [ ] Yêu cầu 1–6
- [ ] Báo cáo nộp tại `docs/team/reports/T-094-tho-may.md`, có phần «Tóm tắt (cho chủ dự án)» lời thường

## Kiểm thử và kiểm định

- Soi Lỗi: Không (chỉ tài liệu). Lá Chắn: Rút gọn (đọc thiết kế, góp điều kiện bảo mật cho các phiếu code).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo của chủ dự án «cứ làm liên tục, không cần hỏi» và Lộ trình Giai đoạn 5. Câu hỏi thiết kế gom lại hỏi chủ dự án một lần, không chặn phần việc khác.

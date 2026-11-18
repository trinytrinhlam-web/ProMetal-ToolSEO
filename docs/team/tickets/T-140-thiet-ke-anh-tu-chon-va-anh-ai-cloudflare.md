# T-140 · Thiết kế: ảnh tự chọn từ thư mục và ảnh minh họa AI miễn phí (Cloudflare Workers AI)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) — thiết kế, chưa viết mã |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-18 |
| Giai đoạn | Giai đoạn 3 (ảnh) mở lại: thay T-053 (tạo ảnh AI, đang hoãn) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | `main` (sau T-137, T-138 khi gộp); thiết kế cũ T-046, T-053, T-056, T-062 |
| Trạng thái | Đang làm (thiết kế) |

## Quyết định của chủ dự án (2026-11-18)

1. **Hạn chế ảnh thật, ưu tiên ảnh minh họa AI.** «Trong folder ảnh mà có thì tự lấy, không có thì dùng ảnh minh họa do AI tạo.»
2. **Tự chọn ảnh trong thư mục, không hỏi** (chủ dự án chọn «Tự chọn luôn, không hỏi» thay cho «gợi ý, bấm nhận»). Ảnh tự chọn vẫn hiện ở màn hình xem lại trước khi gửi.
3. **Ảnh AI miễn phí, app tự làm**: chủ dự án muốn dùng Flow của Google miễn phí và «phải là bạn tự làm, không phải tôi». Flow không có API; dịch vụ bên thứ ba điều khiển Flow phải vượt reCAPTCHA (trái điều khoản Google, không làm). Chủ dự án chọn **Cloudflare Workers AI** (mô hình FLUX, ví dụ `@cf/black-forest-labs/flux-1-schnell`): hạn mức miễn phí 10.000 neuron/ngày (khoảng 4,8 neuron/ô 512×512 + 9,6 neuron/bước; ước khoảng 150 ảnh 1024 px/ngày), gọi qua REST bằng API token. Chưa có ngân sách bật thanh toán Gemini (khóa Gemini miễn phí không tạo được ảnh: 429, Chỉ Huy thử 18/11).
4. Chủ dự án đã chấp nhận dùng Gemini miễn phí cho alt (sổ rủi ro 18/11).

## Việc (thiết kế, báo cáo `docs/team/reports/T-140-tho-may.md`)

1. **Tự chọn ảnh thư mục:** thuật toán so chỗ cần ảnh (mô tả ảnh trong dàn ý, từ khóa, khu vực, hạng mục) với thẻ ảnh (tên thư mục theo 3A: mã công trình, hạng mục, khu vực, trước/sau, ảnh thật/AI; thẻ sửa tay). Ngưỡng «đủ hợp» thì tự gắn; không đủ thì sang ảnh AI. Không dùng một ảnh hai lần trong bài; không lấy ảnh đã dùng ở bài khác nếu được (cần dữ liệu gì?). Có gửi ảnh cho AI để so không (ảnh gửi Gemini miễn phí: sổ rủi ro) — đề xuất cách chỉ dùng thẻ, tên file.
2. **Ảnh AI qua Cloudflare Workers AI:** lớp provider ảnh mới (`seo_app/ai/` hay `seo_app/images/`), không thư viện mới (dùng `requests`/`httpx` đang có): đường gọi REST cố định (`api.cloudflare.com/client/v4/accounts/<id>/ai/run/<model>`), chỉ nhận ảnh trong thân trả lời (base64/bytes), không tải theo URL; giới hạn cỡ; mở bằng Pillow có kiểm (như T-053 yêu cầu 1); xuất WebP 1600 px; không EXIF; tên file chuẩn SEO; alt, chú thích luôn có tiền tố «Minh họa» (luật hiện có). Biến `.env` mới (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`), `.env.example` có chú thích; token **chỉ quyền Workers AI** (hướng dẫn tạo token tối thiểu). Báo lỗi tiếng Việt cố định (hết hạn mức ngày, token sai, mạng). Đếm số ảnh trong ngày, chặn trước khi chạm hạn mức.
3. **Prompt ảnh:** dùng prompt app đã có cho mỗi chỗ cần ảnh (T-056); luật: không chữ, không logo, không mặt người rõ, không giả «công trình đã làm» (minh họa khái niệm); tiếng Anh hay tiếng Việt cho FLUX; người dùng sửa được prompt và tạo lại.
4. **Giao diện** (Họa Sĩ làm sau): nơi hiện ảnh tự chọn / ảnh AI, nút tạo lại, đổi ảnh, bỏ ảnh; câu báo khi hết hạn mức; Cài đặt có mục Cloudflare (trạng thái khóa, kiểm tra kết nối, không in token).
5. **Bảo mật** (cho Lá Chắn): dữ liệu gửi Cloudflare (chỉ prompt chữ, không ảnh của khách); chính sách dữ liệu của Cloudflare Workers AI (có dùng để huấn luyện không — ghi nguồn); token trong `.env`, không log; đường gọi cố định, chặn chuyển hướng; ảnh trả về có thể chở dữ liệu lạ (kiểm như `prepare_images`).
6. **Chia phiếu code** (Thợ Máy, Họa Sĩ, Ngòi Bút cho luật prompt), test, thứ tự gộp; câu hỏi còn mở cho chủ dự án (nếu có), mỗi câu có khuyến nghị.

## Phạm vi

- Chỉ viết báo cáo thiết kế; đọc mã, tài liệu; có thể đọc tài liệu Cloudflare trên web. **Không** gọi Cloudflare thật, không tạo token. Không sửa mã.

## Kiểm định

- Lá Chắn đọc thiết kế trước khi lập phiếu code (như T-094, T-120).

## Ghi chú của Chỉ Huy

- Lập 2026-11-18 theo quyết định của chủ dự án trong buổi thử thật Hẹn giờ/Đăng ngay. T-053 coi như được thay bằng phiếu này (ghi chú T-053 khi thiết kế xong).

# T-042 · Ghi meta SEO (SiteSEO) lên bài nháp trên WordPress

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-037 đã gộp (cùng sửa `seo_app/wordpress/client.py`). **Chủ dự án trả lời câu hỏi 1 và 2** của T-033 (cách ghi SEO: bật Abilities hay không; tài khoản Biên tập viên riêng) |
| Trạng thái | Chờ chủ dự án |

## Mục tiêu

Sau khi app tạo bài nháp, app ghi luôn meta title, meta description, từ khóa chính vào SiteSEO của bài nháp đó.

## Bối cảnh

Thiết kế: `docs/team/reports/T-033-tho-may.md`:
- mục 1.4, 1.5: đường B "Abilities" là đường chính, đường A "meta qua `wp/v2/posts`" dự phòng;
- mục "Rủi ro".

## Yêu cầu (tóm tắt, chi tiết khi chủ dự án trả lời)

1. Thêm `WordPressClient.set_seo_meta(post_id, ...)`:
   - dò đường B hay A;
   - **chỉ** cho bài trong `_created_post_ids`, tức bài do app tạo trong phiên;
   - không bao giờ gửi `null` (gửi `null` là xóa);
   - không đổi `status`.
2. **Danh sách đường REST được gọi là cố định** trong code, từ chối mọi đường khác. Site có đường nhạy cảm `/code-snippets/v1`, `/prometal/v1/deploy-files`, `/prometal/v1/purge`.
3. `check_connection` báo thêm "SiteSEO: ghi được / chưa bật".
4. Lỗi không chép thông điệp máy chủ.
5. Test bằng site giả, gồm: bài không do app tạo → từ chối; đường lạ → từ chối.

## Yêu cầu bảo mật riêng

W1, W2, W3, W4, S2, D3. Lá Chắn soát kỹ nhất phần chặn ghi bài đã đăng.

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-042 Ghi meta SEO lên nháp"**, nhánh `team/T-042`. Chỉ giao sau khi chủ dự án trả lời.
- Sau phiếu này là một phiếu thử thật (số phiếu kế tiếp lúc đó): chủ dự án (có Chỉ Huy hướng dẫn) tạo thử **một bài nháp** bằng app, mở trang quản trị xem hộp SiteSEO hiện đúng, rồi tự xóa nháp. Ghi kết quả vào báo cáo của phiếu đó. Lập phiếu khi tới bước đó.
- 2026-10-16: khi làm, ghi SEO lên site là **tùy chọn**, mặc định tắt. Dò không thấy đường ghi thì app im lặng quay về chép tay, không chặn việc tạo nháp.

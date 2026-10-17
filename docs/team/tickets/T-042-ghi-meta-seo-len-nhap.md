# T-042 · Ghi meta SEO (SiteSEO) lên bài nháp trên WordPress

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-037 đã gộp (cùng sửa `seo_app/wordpress/client.py`). Chủ dự án đã trả lời 2026-10-16: **1A** (Abilities là đường chính), **2A** (tài khoản Biên tập viên riêng) |
| Trạng thái | Chờ T-037 |

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

- Phiên **"Thợ Máy · T-042 Ghi meta SEO lên nháp"**, nhánh `team/T-042`. Giao sau khi T-037 gộp (chủ dự án đã trả lời 16/10).
- Sau phiếu này là một phiếu thử thật (số phiếu kế tiếp lúc đó): chủ dự án (có Chỉ Huy hướng dẫn) tạo thử **một bài nháp** bằng app, mở trang quản trị xem hộp SiteSEO hiện đúng, rồi tự xóa nháp. Ghi kết quả vào báo cáo của phiếu đó. Lập phiếu khi tới bước đó.
- 2026-10-16: khi làm, ghi SEO lên site là **tùy chọn**, mặc định tắt. Dò không thấy đường ghi thì app im lặng quay về chép tay, không chặn việc tạo nháp.
- 2026-10-16: chủ dự án chọn 1A, 2A. Abilities là đường chính; đường A (meta qua `wp/v2/posts`) chỉ dự phòng. Test bằng site giả; thử thật chỉ sau khi chủ dự án bật Abilities và tạo tài khoản Biên tập viên.
- 2026-10-17 (Chỉ Huy A): **Điều kiện của Lá Chắn T-036** (LC-T036-3): trước khi gửi meta lên site, **Chặn** chữ có thực thể HTML (`&#37;`, `&lt;script&gt;`…), dùng `_ENTITY` có sẵn ở `seo_app/onpage/meta.py` (khoảng dòng 485). Lá Chắn khuyên Chặn, thay vì chờ phiếu thử thật chứng minh SiteSEO lưu và in nguyên văn.
- 2026-10-17 (Chỉ Huy A): **Điều kiện của Lá Chắn T-037** (`docs/team/reports/T-037-la-chan.md`, ĐẠT CÓ ĐIỀU KIỆN). Phiếu này được sửa `seo_app/wordpress/client.py` và `seo_app/storage/site_index.py` cho các điểm sau:
  1. SL-T037-3 (**bắt buộc xong trước Giai đoạn 5**): thiếu hoặc sai header `X-WP-TotalPages` mà trang trả đủ 100 mục thì đọc tiếp trang sau, hoặc ít nhất bật `truncated`. Sửa luôn `_get_all_pages`. Bỏ `xfail` tương ứng trong `tests/test_soi_loi_t037.py`.
  2. Danh sách đường gọi cố định trong `_request`: so khớp toàn chuỗi cặp (method, path), từ chối trước khi gửi request, chặn `..`, `%2e`, `//`, `/code-snippets/v1`, `/prometal/v1`. Lá Chắn đồng ý danh sách Thợ Máy T-037 đề xuất. Có test.
  3. LC-T037-1 (a)(b): `is_site_link` từ chối `" ' < >` và ký tự vô hình (U+202E, U+200B…); `_clean_text` bỏ ký tự vô hình.
  4. SL-T037-4: chỉ xóa file cache khi chắc chắn hỏng (`SQLITE_NOTADB` / `SQLITE_CORRUPT`, `quick_check` lỗi, sai cột); sửa cả `site_index.py` khoảng dòng 138 (`load`) lẫn khoảng dòng 324.
  5. SL-T037-5: khi `load` đã thấy file bận thì `refresh` bỏ bước ghi, hoặc giảm thời gian chờ (hiện treo khoảng 14 giây). Nếu T-039 hoặc T-041 nối `get()` vào giao diện trước phiếu này thì phiếu đó sửa.

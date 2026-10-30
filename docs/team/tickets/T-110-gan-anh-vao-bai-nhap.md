# T-110 · Gắn ảnh «Gửi nháp» vào bài nháp để ảnh không lộ trong danh sách Media công khai (LC-T093-2, chủ dự án chọn 1A)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-30 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (trước khi đóng Giai đoạn 3) |
| Phụ thuộc | Không |
| Trạng thái | Đang làm |

## Mục tiêu

Ảnh app tải lên khi «Gửi nháp» được gắn vào chính bài nháp vừa tạo (mục Media có bài cha), nên danh sách Media công khai (`GET /wp-json/wp/v2/media` không đăng nhập) không liệt kê ảnh của bài chưa đăng; ảnh chỉ công khai qua danh sách khi bài được đăng.

## Bối cảnh

- Lá Chắn T-093 (`docs/team/reports/T-093-la-chan.md`, mục 3), **LC-T093-2 (Thấp)**, đã nêu ở LC-T087-2: ảnh «Gửi nháp» không gắn vào bài nháp (không lệnh nào gửi `post`; `_describe_draft_media` chỉ gửi alt, tiêu đề, chú thích). WordPress lõi (`class-wp-rest-posts-controller.php`, `check_read_permission`): mục `inherit` không có bài cha thì ai cũng đọc được, nên danh sách Media liệt kê mọi ảnh app đã tải (`source_url` còn GPS), kể cả của bài chưa đăng, bài bỏ dở, lần gửi hỏng.
- **Chủ dự án chọn 1A (30/10):** phần mềm gắn ảnh vào bài nháp.
- Test `xfail(strict=True)`: `tests/test_la_chan_t093.py::test_lc_t093_2_uploaded_images_attached_to_new_draft` (đã ở `main`).
- Lưu ý: địa chỉ trực tiếp của file ảnh vẫn mở được nếu ai biết đường dẫn (WordPress không chặn file tĩnh); phiếu này chỉ bỏ ảnh khỏi danh sách công khai.

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py` (đường gửi nháp kèm ảnh, `_describe_draft_media`, danh sách khóa thân lệnh được phép cho đường Media), `app/views/write.py` (**chỉ** câu `GPS_PUBLIC_WARNING` cho đúng sự thật mới), test; gỡ `xfail` LC-T093-2 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** `config/**`, phần khác của `app/**`.

## Yêu cầu

1. Sau khi tạo bài nháp, gắn từng ảnh vừa tải vào bài đó (`post` = mã bài nháp) trong cùng lệnh ghi alt, tiêu đề, chú thích, hoặc lệnh riêng; chỉ cho gắn vào bài nháp **chính client vừa tạo** (`_created_post_ids`), mã ảnh **chính client vừa tải**; khóa `post` chỉ được phép ở đúng đường này.
2. Lỗi khi gắn (mạng, 4xx/5xx, trả lời lạ): không tải lại ảnh, không tạo bài trùng; câu báo cố định nói rõ ảnh có thể còn hiện trong danh sách Media và cách kiểm (Media → Thư viện); giữ đúng khóa gửi trùng T-086, T-089.
3. Ảnh đại diện (`featured_media`) vẫn đặt được; nội dung bài, `srcset` (T-059) không đổi.
4. `GPS_PUBLIC_WARNING`: nói đúng: ảnh và GPS xem được qua đường dẫn trực tiếp ngay khi tải lên; không hiện trong danh sách Media công khai cho tới khi bài đăng (nếu gắn thành công).
5. Không lùi T-054, T-059, T-060, T-071, T-085, T-086, T-088, T-089, T-091, T-099 (grep mọi nơi gọi và test ghim câu báo cũ; đổi test cũ cần Chỉ Huy duyệt R5).

## Yêu cầu bảo mật riêng

W2, W3, F1.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-110-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W2, W3, F1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-30 theo quyết định 1A của chủ dự án (rà soát Giai đoạn 3, T-093).

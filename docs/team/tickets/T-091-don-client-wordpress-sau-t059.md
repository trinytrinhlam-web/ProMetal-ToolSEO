# T-091 · Dọn client WordPress sau T-059: chữ website có surrogate lẻ (SL-T088-1), giới hạn trên cho mã bài

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-059 bước 7 đã gộp (cùng sửa `seo_app/wordpress/client.py`) |
| Trạng thái | Đang làm |

## Mục tiêu

Chữ website trả về có ký tự surrogate lẻ (U+D800–U+DFFF) không đi xuyên client làm vỡ chỗ khác (Streamlit, SQLite); mã bài/ảnh website trả về có giới hạn trên hợp lý ngay trong client.

## Bối cảnh

- **SL-T088-1** (`docs/team/reports/T-088-soi-loi.md`, mức Thấp, Lá Chắn đồng ý trong `T-088-la-chan.md`): `check_connection()` trả `site_name` còn surrogate lẻ; 8 `xfail(strict=True)` trong `tests/test_soi_loi_t088.py`.
- Phần không bắt buộc của Lá Chắn T-086 (`docs/team/reports/T-086-la-chan.md`): giới hạn trên cho `_positive_id` trong client (LC-T086-1 đã đóng ở `write.py`, đây là lớp phòng thêm).

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py`, test; gỡ `xfail` SL-T088-1 khi XPASS (chỉ xóa dấu).
- **Không được sửa:** `app/**`, `config/**`; tên, chữ ký, hành vi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`.

## Yêu cầu

1. Mọi chữ client lấy từ website (tên site, tên người dùng, tiêu đề bài, tên chuyên mục, thẻ…) bỏ hoặc thay surrogate lẻ ở một chỗ dùng chung.
2. `_positive_id` có giới hạn trên (ví dụ 2⁶³−1), quá thì như mã sai khuôn.
3. **SL-T059-1** (Soi Lỗi T-059, Thấp, có từ trước): SiteSEO lưu chữ qua `sanitize_text_field` (đổi «< » thành `&lt;`, cắt «%» kèm 2 ký tự hex, WordPress bỏ «\») nên `_ability_confirms` báo «chưa ghi» dù đã ghi: so theo bản đã chuẩn hóa như SiteSEO, hoặc chặn trước khi gửi các ký tự đó kèm câu báo; gỡ 5 `xfail` khi XPASS.
4. Rủi ro kses (Soi Lỗi T-059): tài khoản thiếu quyền `unfiltered_html` thì WordPress bỏ `srcset` khi lưu bài, ảnh trong bài lại mất GPS trên điện thoại: `check_connection` báo được tài khoản có `unfiltered_html` không (phần giao diện cảnh báo ở trang Kết nối WordPress: báo Chỉ Huy giao Họa Sĩ).
5. Test; mọi test client WordPress cũ vẫn qua (grep mọi nơi gọi).

## Yêu cầu bảo mật riêng

W2, W3.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-091-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W2, W3).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo «cứ làm liên tục, không cần hỏi».
- 2026-10-28 15:47 (Chỉ Huy B): T-059 bước 7 đã gộp. Nhánh `team/T-091` từ `main` `1b45f5d`, worktree `wt-T-091`; giao Thợ Máy (phiên Thợ Máy T-059).
- 2026-10-28 21:09 (Chỉ Huy B): Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`2ff1425`), Lá Chắn ĐẠT CÓ ĐIỀU KIỆN nhưng chưa gộp được (`ed5d86b`: LC-T091-1). Chỉ Huy duyệt (R5) đổi kỳ vọng 2 ca `tests/test_t089_send_draft.py` theo mẫu phương án A; lượt 2 Thợ Máy sửa thêm SL-T091-1 → -3 (theo đề xuất).

# T-106 · Trang Kết nối WordPress: cảnh báo khi tài khoản thiếu quyền `unfiltered_html`

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-29 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-091 đã gộp (`ConnectionInfo.can_unfiltered_html`) |
| Trạng thái | Đang làm |

## Mục tiêu

Khi tài khoản WordPress của app thiếu quyền `unfiltered_html`, trang Kết nối WordPress báo rõ cho chủ dự án: ảnh trong bài sẽ mất GPS trên điện thoại (WordPress bỏ `srcset` app ghi sẵn), kèm cách xử lý.

## Bối cảnh

- Soi Lỗi T-059 (rủi ro kses), T-091 yêu cầu 4: client đã báo được quyền qua `ConnectionInfo.can_unfiltered_html` (gộp `main` 28/10); phần giao diện để Họa Sĩ làm.
- Sổ rủi ro `docs/team/security.md` mục 6, dòng 2026-10-28: tài khoản Biên tập viên `phan-mem-seo` có `unfiltered_html`; cách giữ GPS ảnh trong bài dựa vào quyền này; không cấp thêm quyền cho tài khoản.

## Phạm vi

- **Được sửa:** `app/views/wordpress.py` (trang Kết nối), test giao diện.
- **Không được sửa:** `seo_app/**`, `config/**`.

## Yêu cầu

1. Khi `can_unfiltered_html` là sai: cảnh báo (không phải lỗi chặn) bằng tiếng Việt dễ hiểu: ảnh trong bài sẽ mất vị trí GPS khi xem trên điện thoại; muốn giữ GPS thì tài khoản cần vai trò Biên tập viên (Editor) trên website một trang. Không khuyên cấp quyền Quản trị.
2. Khi không biết (website không trả thông tin quyền): câu trung tính, không báo động.
3. Khi có quyền: không hiện gì thêm (hoặc một dòng xác nhận nhỏ).
4. Không in tên đăng nhập, mật khẩu, đường dẫn; chữ từ website đi qua lớp làm sạch sẵn có.
5. Test `AppTest` cho cả 3 trường hợp; test trang Kết nối cũ vẫn qua.

## Yêu cầu bảo mật riêng

W2, U1.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-106-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W2, U1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-29: phần giao diện còn lại của T-091 yêu cầu 4 (đề xuất Soi Lỗi T-059), theo chỉ đạo «vấn đề nào có đề xuất thì làm theo đề xuất».
- 2026-10-30 11:00 (Chỉ Huy B): làm cùng T-108 trên nhánh `team/T-106` (từ `main` `0122d4b` + T-093), worktree `wt-T-106`; giao Họa Sĩ (phiên Họa Sĩ T-084).

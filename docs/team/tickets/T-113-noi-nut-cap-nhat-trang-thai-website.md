# T-113 · Nối nút «Cập nhật trạng thái từ website» (T-109) vào trang Kế hoạch; trung hòa ô công thức ở trang Kết nối

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-31 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-109 (lõi `seo_app/plan/website.py`) đã gộp `main` |
| Trạng thái | Đang kiểm (Soi Lỗi) |

## Mục tiêu

Người dùng bấm «Cập nhật trạng thái từ website» ở trang Kế hoạch, xem danh sách thay đổi đề xuất và cảnh báo, rồi bấm ghi vào Google Sheets (thiết kế T-094 mục 1.7).

## Bối cảnh

- T-109 làm lõi: `check_website` (thuần) và `apply_website_changes` (ghi theo bước T-100). Biên bản Lá Chắn T-109 (`docs/team/reports/T-109-la-chan.md`) ghi **điều kiện cho lượt nối nút**: một nút đọc và một nút ghi riêng, chỉ chạy khi bấm; truyền đúng kết quả `post_statuses`, `sheet_id` và `now=settings.now()` (không truyền `S.plan_web` dạng tuple, G2 Soi Lỗi); kiểm lại website ngay trước khi ghi hoặc từ chối lần kiểm đã cũ (lõi từ chối lần kiểm cũ quá 5 phút); bảng chữ thuần và qua `safe_text` (LC-T101-1); mọi lỗi thành câu cố định.
- Soi Lỗi T-109 G1: trang Kế hoạch và trang Bài viết đang tính «Lỡ lịch» bằng hằng 15 phút riêng → dùng chung `website.LATE_AFTER`.
- Lá Chắn T-102: bảng chuyên mục, thẻ ở trang Kết nối WordPress (có từ Giai đoạn 1) chưa trung hòa ô dạng công thức (cùng loại LC-T101-1) → sửa ở phiếu này.

## Phạm vi

- **Được sửa:** `app/views/plan.py`, `app/views/home.py` (hằng «Lỡ lịch»), `app/views/wordpress.py` (bảng chuyên mục, thẻ), test.
- **Không được sửa:** `seo_app/**` (cần đổi lõi thì hỏi Chỉ Huy).

## Yêu cầu

1. Nút đọc (gọi `post_statuses` rồi `check_website`) và nút ghi (`apply_website_changes`) riêng, chỉ khi bấm; không tự chạy khi mở trang hay rerun.
2. Hiện thay đổi đề xuất (dòng, ô, cũ → mới, lý do) và cảnh báo bằng chữ thuần qua `safe_text`; người dùng chọn/bỏ từng thay đổi trước khi ghi (nếu thiết kế 1.7 yêu cầu).
3. Lần kiểm cũ thì báo «kiểm lại» thay vì ghi; lỗi mạng / Sheet đổi giữa chừng ra câu cố định.
4. Dùng chung `website.LATE_AFTER` ở `plan.py`, `home.py`.
5. Bảng chuyên mục, thẻ ở trang Kết nối WordPress trung hòa ô mở đầu `=`, `+`, `-`, `@` (như LC-T101-1).
6. Không lùi T-101, T-102, T-109; `tests/test_app_pages.py` mở mọi trang không lỗi.

## Yêu cầu bảo mật riêng

Theo `docs/team/reports/T-094-la-chan.md` mục «Chung», điều kiện trong `T-109-la-chan.md`, LC-T101-1.

## Tiêu chí xong

- [ ] Yêu cầu 1–6
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-113-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-10-31 theo điều kiện Lá Chắn T-109 và ghi nhận Lá Chắn T-102.
- 2026-10-31 13:32 (Chỉ Huy B): giao Họa Sĩ (phiên T-084) 10:40, nhánh từ `main` `bb25dde`. Họa Sĩ xong (`7b93af1`). Giao Soi Lỗi rút gọn.

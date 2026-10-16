# T-041 · Bước 4 "SEO" của Soạn bài chạy thật

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`), Thợ Máy hỗ trợ phần lưu nháp |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-036, T-037, T-038, T-039 đã gộp (T-040 nên gộp trước) |
| Trạng thái | Chờ |

## Mục tiêu

Thay phần demo bước 4 trong trang Soạn bài bằng chức năng thật. **Giữ bố cục chủ dự án đã duyệt.**

## Phạm vi

- **Được sửa:**
  - `app/views/write.py`: chỉ bước SEO và trạng thái liên quan;
  - `seo_app/demo.py`: xóa `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` khi không còn dùng;
  - `seo_app/storage/drafts.py`: thêm trường meta/link/schema vào nháp, giữ `extra="forbid"`. Phần này Thợ Máy làm trước, cùng nhánh;
  - test giao diện.
- **Không được sửa:** logic `seo_app/onpage/**` (báo Thợ Máy nếu cần đổi).

## Yêu cầu (tóm tắt)

1. **Meta:**
   - ô title/description có nút 🔄 viết lại riêng từng ô, quay lại bản trước được;
   - đếm ký tự NFC; màu Nên / Cảnh báo / Chặn;
   - xem trước kiểu Google (`ui.serp_preview` đã có, kiểm lại escape).
2. **Slug:** gợi ý, sửa được, kiểm trùng.
3. **Liên kết nội bộ:** bảng tick "Dùng", "Cụm từ trong bài", "Trỏ tới bài"; nút "Tải lại danh sách bài".
4. **Schema:** xem FAQPage đã dựng (nếu bài có mục Hỏi đáp), hiện chữ thuần, không HTML.
5. Lưu mọi lựa chọn vào nháp cục bộ (tự lưu như bước 1–3).
6. Bỏ nhãn "Bản demo" của bước này. `tests/test_app_pages.py` vẫn qua.

## Yêu cầu bảo mật riêng

U1 (chữ từ site và AI phải escape; không `unsafe_allow_html` với chữ chưa escape), U2, D3.

## Tiêu chí xong

- [ ] Bước SEO chạy thật, giữ bố cục
- [ ] Test giao diện bằng `AppTest`, hàm giả
- [ ] Báo cáo `docs/team/reports/T-041-hoa-si.md` (và `T-041-tho-may.md` cho phần nháp), kèm hướng dẫn chủ dự án tự mở app xem

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (U1).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-041 Lưu SEO vào nháp"** rồi **"Họa Sĩ · T-041 Bước SEO thật"**, nhánh `team/T-041`.
- 2026-10-16: chủ dự án chưa trả lời câu 1, 2 (cách ghi SEO lên SiteSEO). Bước SEO phải chạy trọn vẹn **không cần** ghi lên site:
  - có nút chép (copy) title, description, slug để chủ dự án dán tay vào hộp SiteSEO;
  - không hiện lỗi hay nút hỏng khi chưa cấu hình ghi SEO;
  - không có kết nối WordPress thì danh sách bài (liên kết nội bộ, kiểm trùng) báo nhẹ "chưa kết nối", các phần còn lại vẫn dùng được.

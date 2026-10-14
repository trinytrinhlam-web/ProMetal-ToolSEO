# T-006 · Sửa các lỗi Trung bình và Thấp của Giai đoạn 2

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 (phải xong trước khi đóng giai đoạn) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-004 (cùng file) |
| Trạng thái | Mới (chủ dự án đã duyệt cả mục 5 và 6 ngày 2026-10-14) |

## Mục tiêu

Đóng các lỗi còn lại mà Lá Chắn và Soi Lỗi đã tìm ra, mỗi lỗi có test.

## Yêu cầu

Chi tiết và cách sửa đề xuất nằm trong [T-001-la-chan.md](../reports/T-001-la-chan.md) (LC) và [T-002-soi-loi.md](../reports/T-002-soi-loi.md) (SL).

1. Bắt buộc `WORDPRESS_URL` là `https://` (LC #4).
2. `ai.toml` viết sai kiểu báo `AIError` dễ hiểu, `web_search = "false"` không bị hiểu là bật (SL #4, #5).
3. AI trả bài rỗng hoặc bản viết lại rỗng thì báo cho người dùng (SL #6).
4. Chuẩn hóa Unicode khi tìm cụm từ cấm (SL #7); lọc chuỗi giống khóa trong thông báo lỗi 400 (SL #2); bắt lỗi mạng còn sót để không hiện traceback (LC #8).
5. **Cần chủ dự án duyệt** (`seo_app/config.py` thuộc danh sách file nhạy cảm): cho phép test trỏ sang file `.env` rỗng để không bao giờ đọc `.env` thật trên máy (LC #5). Phần fixture trong `tests/conftest.py` giao Soi Lỗi.
6. **Cần chủ dự án duyệt** (R6): khai báo `pydantic` trong `pyproject.toml`; thư viện này đã được cài sẵn nhờ thư viện `anthropic`, chỉ là ghi tên cho đúng (LC #7).
7. `set_featured_image`: xóa hàm (chưa dùng) hoặc chỉ cho phép với bài app vừa tạo (LC #6).

## Tiêu chí xong

- [ ] Các test `xfail` tương ứng chuyển thành `passed`
- [ ] Báo cáo `docs/team/reports/T-006-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có
- Lá Chắn: Có

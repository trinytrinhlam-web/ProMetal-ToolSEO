# T-008 · Gia cố bộ lọc HTML/link (các lỗ hở Soi Lỗi và Lá Chắn tìm ra sau T-004)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 (bắt buộc trước Giai đoạn 5) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-004 (đã xong) |
| Trạng thái | Xong |

## Mục tiêu

Không còn đường nào để AI chèn link lạ vào bài, bộ lọc không làm mất nửa bài, và không thể làm app treo bằng bài cực dài.

## Bối cảnh

- [T-004-T-005-soi-loi.md](../reports/T-004-T-005-soi-loi.md): lỗi #1, #2 (link Markdown dạng ít gặp lọt qua), #3 (thẻ `embed/input/link/meta/base` nuốt phần sau). Có sẵn 14 test `xfail` trong `tests/test_sanitize_bypass.py`.
- [T-004-T-005-la-chan.md](../reports/T-004-T-005-la-chan.md): lỗi #1 (biểu thức chính quy chạy rất chậm với đầu vào dài), #2 (`is_safe_url` cho qua `//…`, `/\…`), #3 (lọc thêm `outline.title`, `Research`, `Outline` ở lớp 1), #4 (trùng Soi Lỗi #3).

## Phạm vi

- **Được sửa:** `seo_app/sanitize.py`, `seo_app/content/workflow.py`; thêm test và gỡ `xfail` tương ứng trong `tests/`.

## Tiêu chí xong

- [ ] 14 test `xfail` của `test_sanitize_bypass.py` chuyển thành `passed`
- [ ] Test mới: đầu vào 200 KB toàn `<script>` hoặc `[` lọc xong dưới 1 giây
- [ ] Báo cáo `docs/team/reports/T-008-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

## Ghi chú của Chỉ Huy

- 2026-10-14, trả lại lần 1: Soi Lỗi tìm SL-1..SL-5 ([báo cáo](../reports/T-003-006-008-009-soi-loi.md)).
- 2026-10-14, trả lại lần 2: Soi Lỗi R3-1..R3-4 ([báo cáo](../reports/T-008r-010-011-soi-loi.md)), Lá Chắn #1, #2 ([biên bản](../reports/T-008r-010-011-la-chan.md)). Ba vòng vá từng kiểu link đều còn lọt, nên **đổi cách làm**: không cố nhận diện link nữa mà làm cho văn bản AI không thể tạo link Markdown (escape mọi `[`, `]` khi hiển thị/xuất; chuẩn hóa xuống dòng), áp dụng cho mọi trường chữ AI tạo ra (kể cả R3-3: tiêu đề, `reason`, `summary`).

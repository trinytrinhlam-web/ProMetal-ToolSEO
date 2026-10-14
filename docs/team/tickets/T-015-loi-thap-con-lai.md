# T-015 · Lỗi Thấp còn lại sau T-013/T-014, test tốc độ ổn định

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp (mục 1 phải xong trước Giai đoạn 5, nếu không thành Cao) |
| Phụ thuộc | Không |
| Trạng thái | Xong (2026-10-14) |

## Yêu cầu

Nguồn: [T-013-014-la-chan.md](../reports/T-013-014-la-chan.md) (#1, ghi chú PEP 8) và [T-013-014-soi-loi.md](../reports/T-013-014-soi-loi.md) (R5-1, test tốc độ).

1. `apply_flag` (`seo_app/content/workflow.py`): câu thay thế phải qua `strip_tags` trước khi ghép, tức `escape_link_syntax(strip_tags(…))`, để thẻ HTML trong gợi ý AI không lọt vào bài. Thêm test.
2. R5-1: `looks_like_destination` (`seo_app/sanitize.py`) làm mất chữ ở trường hợp Soi Lỗi nêu. Sửa và chuyển test `xfail` R5-1 thành `passed`.
3. Test tốc độ đang so với mốc cố định `< 1.0` giây, dễ hỏng trên máy Windows chậm. Đổi sang so tỉ lệ: đầu vào dài gấp 4 thì thời gian không quá 9 lần. Không được nới hay bỏ test.
4. Sửa dòng trống thừa theo PEP 8 ở `seo_app/sanitize.py` (khoảng dòng 425–427).

## Tiêu chí xong

- [ ] `uv run pytest` qua hết (test R5-1 không còn `xfail`), `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-015-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

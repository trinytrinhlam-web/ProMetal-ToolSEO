# T-021 · Sửa lỗi kho nháp (T-016) và ghi `.env` (T-020)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`): phần A và phần B làm song song bởi hai lượt Thợ Máy |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (chặn đóng T-016, T-017, T-020) |
| Phụ thuộc | Không |
| Trạng thái | Đang làm |

Nguồn: [T-016-020-la-chan.md](../reports/T-016-020-la-chan.md) và [T-016-020-soi-loi.md](../reports/T-016-020-soi-loi.md). Test `xfail` R8-x nằm trong `tests/test_soi_loi_t016_t020.py`.

## Phần A · Kho nháp `seo_app/storage/`

1. **Lá Chắn #1 / R8-2 (Trung bình):** khi đọc nháp, chạy lại đúng các hàm `clean_*` của `seo_app/content/workflow.py` (nghiên cứu, rà soát, dàn ý, tiêu đề, thân bài, ghi chú ảnh), không chỉ kiểm khuôn. Bản đúng phải giữ nguyên sau nhiều lần lưu/mở.
2. **R8-1 (Trung bình):** xóa file hoặc thư mục `data/` khi app đang chạy thì lần lưu sau phải tự tạo lại.
3. R8-3: thông báo lỗi kiểm khuôn không chép tên trường hay dữ liệu từ file.
4. R8-4: đường dẫn mặc định tra lúc gọi (như `DEFAULT_ENV_FILE`), sửa cả gợi ý trong báo cáo T-016.
5. R8-5: lỗi mã hóa khi lưu trả về `DraftError`.
6. R8-6: không xóa nháp vừa lưu khi đồng hồ máy bị chỉnh lùi.

## Phần B · Ghi `.env` `seo_app/env_file.py`

1. **Lá Chắn #2 (Trung bình):** dòng khóa cũ mở nháy không đóng thì không được bỏ các dòng sau; báo lỗi dễ hiểu và không ghi gì.
2. R8-7, R8-8, R8-9: sau khi ghi, đọc lại bằng python-dotenv để so; sai thì khôi phục bản cũ và báo lỗi, không báo "Đã lưu".
3. Lá Chắn #3 (Thấp): `.env` là symlink thì từ chối ghi, báo dễ hiểu (không lộ đường dẫn).

## Tiêu chí xong

- [ ] Mọi `xfail` R8-x chuyển thành `passed`; thêm test cho Lá Chắn #1, #2, #3
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-021-tho-may.md` (mỗi lượt một mục A / B)

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có

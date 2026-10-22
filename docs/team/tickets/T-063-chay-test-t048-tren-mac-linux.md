# T-063 · Chạy test đọc thư mục ảnh (T-048) trên Mac hoặc Linux

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Cao (điều kiện Lá Chắn T-048, **chặn gộp T-056**) |
| Phụ thuộc | T-048 đã gộp (`main`) |
| Trạng thái | Mới |

## Mục tiêu

Có bằng chứng chạy thật cho nhánh chặn liên kết của `seo_app/images/folders.py` trên Mac/Linux. Cả đội tới nay chỉ chạy trên Windows, nên 6 test chỉ chạy trên Mac/Linux luôn bị bỏ qua.

## Bối cảnh

- Biên bản Lá Chắn T-048 (`docs/team/reports/T-048-la-chan.md`), lỗi **LC-T048-1 (Trung bình)**: trên Mac/Linux, mọi lần xem thư mục đi nhánh `_scan_by_fd` (`openat(…, O_NOFOLLOW)` + `os.scandir(fd)`), `O_NOFOLLOW` khi đọc, cờ ẩn `UF_HIDDEN` (chỉ có trên Mac), tên sai UTF-8. Lá Chắn đọc từng dòng, không thấy lỗi, nhưng chưa có lần chạy nào.
- Chỗ code: `folders.py:158`, `:182`, `:297-311`, `:630-634`, `:739-751`. Test bị bỏ qua trên Windows: `tests/test_images_folders.py:62` (4 test symlink), `:368`, `:381`.

## Phạm vi

- **Được sửa:** test trong `tests/test_images_folders*.py` (chỉ thêm), báo cáo.
- **Không được sửa:** `seo_app/**`, `app/**`. Có lỗi thì ghi vào báo cáo, Chỉ Huy lập phiếu cho Thợ Máy.

## Yêu cầu

1. Chạy `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py -rs` trên **Linux** (phiên Claude Code cloud chạy Ubuntu là đủ) và, nếu có máy, trên **Mac** (chỉ Mac kiểm được `UF_HIDDEN`).
2. Kết quả phải cho thấy 6 test Mac/Linux **chạy**, không bị bỏ qua. Dán nguyên phần tóm tắt `-rs`.
3. Thử thêm trên Linux: symlink đặt sẵn trong thư mục gốc, symlink trỏ ra ngoài, thư mục gốc là symlink, tên file sai UTF-8, thư mục không có quyền đọc. Kết quả phải như trên Windows: không đọc được nội dung ngoài gốc, câu lỗi không lộ đường dẫn.
4. Chạy toàn bộ `uv run pytest` và `uv run ruff check .` trên máy đó.

## Yêu cầu bảo mật riêng

F1 (đọc file ngoài thư mục đã khai báo).

## Tiêu chí xong

- [ ] 6 test Mac/Linux chạy thật và qua (hoặc lỗi đã ghi rõ, có cách tái hiện)
- [ ] `uv run pytest` 0 hỏng trên máy kiểm, `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-063-soi-loi.md`, ghi rõ hệ điều hành, bản Python

## Kiểm thử và kiểm định

- Soi Lỗi: chính phiếu này. Lá Chắn: chỉ kiểm lại nếu có lỗi phải sửa.

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-048. Hạn: trước khi gộp T-056 và trước khi hết Giai đoạn 3.
- Máy chủ dự án là Windows; Chỉ Huy B cũng chạy trên Windows. Cách nhanh: mở một phiên Claude Code cloud trên nhánh `main` (đã có T-048), làm trên nhánh tạm `team/T-063`.
- 2026-10-20 (Chỉ Huy B): **Thêm theo Lá Chắn T-052** (điều kiện 5): chạy cả `uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py -rs` để 2 ca symlink chạy thật; nếu có Mac thì thử tên NFD thật. Ghi vào báo cáo T-063.
- 2026-10-21 (Chỉ Huy B): **Điều kiện Lá Chắn T-055** (điều kiện 4): chạy thêm `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py` trên Mac (symlink, APFS không phân biệt hoa thường, tên NFD).
- 2026-10-22 (Chỉ Huy B): **Điều kiện Lá Chắn T-076** (điều kiện 3): chạy thêm `tests/test_images_folders.py`, `tests/test_soi_loi_t076.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py` trên Mac (phần `fd` của `_listed_names`, symlink thật, NFD thật); đo `stat_image` và kiểm nháp nhiều ảnh trên Google Drive for Desktop của Mac.

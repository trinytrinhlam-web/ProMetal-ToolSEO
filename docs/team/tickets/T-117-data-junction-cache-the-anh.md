# T-117 · Thư mục `data/` là liên kết (junction/symlink): cache ảnh xem trước và kho thẻ ảnh không ghi ra ngoài dự án (LC-T116-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-02 |
| Giai đoạn | Giai đoạn 3 (dọn sau rà soát Fable) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | Không |
| Trạng thái | Xong (gộp `main` 2026-11-03) |

## Mục tiêu

Khi thư mục `data/` (hay tầng nào dưới thư mục dự án) là junction/symlink, `PreviewCache` và `ImageTagStore` không ghi file ra nơi liên kết trỏ tới; báo câu cố định, không lộ đường dẫn.

## Bối cảnh

- Lá Chắn T-116 nhóm 1 (chạy Fable 5.1, `docs/team/reports/T-116-la-chan-nhom-1.md` trên nhánh `team/T-116`), **LC-T116-1 (Thấp)**: hai module chỉ kiểm liên kết ở tên file, không ở tầng thư mục; `data/` là junction thì ảnh xem trước và SQLite thẻ ảnh được ghi vào nơi liên kết trỏ tới. Cần quyền ghi vào thư mục cài app từ trước (cùng lớp sổ rủi ro). Đổi mức từ T-049 N2 của Opus.
- Có 2 test `xfail(strict=True)` trong `tests/test_la_chan_t116_nhom1.py` (nhánh `team/T-116`).
- Đề xuất của Lá Chắn: một hàm kiểm liên kết từng tầng dưới `PROJECT_ROOT`, dùng chung cho cả hai.

## Phạm vi

- **Được sửa:** nơi dựng đường dẫn `data/` của `PreviewCache` và `ImageTagStore` (`seo_app/images/**`, `seo_app/storage/**` nếu có), một hàm dùng chung, test; gỡ `xfail` LC-T116-1 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** `app/**`, lớp đọc ảnh từ thư mục người dùng (`folders.py` phần đọc), cách băm/thẻ.

## Yêu cầu

1. Kiểm từng tầng từ `PROJECT_ROOT` tới file (junction, symlink, reparse point trên Windows; `O_NOFOLLOW`/`lstat` trên Mac/Linux); có liên kết → không ghi, câu cố định («Thư mục dữ liệu của phần mềm là lối tắt…»), không lộ đường dẫn; cache xem trước hỏng thì app vẫn chạy (chỉ không lưu cache).
2. Dùng chung cho cả hai nơi; grep mọi chỗ khác ghi vào `data/` (`plan_cache.sqlite`, `site_index.sqlite`, kho nháp) và ghi trong báo cáo có cần áp dụng không (chỉ sửa nếu cùng hàm dựng đường dẫn; còn lại đề xuất).
3. Test Windows (junction thật) và giả lập Mac/Linux; không lùi T-048, T-052, T-074, T-079, T-080.

## Yêu cầu bảo mật riêng

F1, F2.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-117-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-11-02 theo LC-T116-1; Chỉ Huy chọn phiếu dọn nhỏ thay vì ghi sổ rủi ro (đề xuất của Lá Chắn, sửa rẻ).
- 2026-11-02 12:44 (Chỉ Huy B): giao Thợ Máy (phiên T-075) 08:35, nhánh `team/T-117` từ `origin/main` + T-116 nhóm 1 (`3669046`).
- 2026-11-03 12:33 (Chỉ Huy B): Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`8c0190d`), Lá Chắn (Fable) ĐẠT CÓ ĐIỀU KIỆN (`bb5b463`, LC-T116-1 đóng). Gộp `main` (cùng biên bản T-116 nhóm 1, 3, 4), Windows 22.300 test qua, 0 hỏng, đã đẩy.

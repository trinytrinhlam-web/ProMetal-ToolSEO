# T-122 · Cache số liệu Search Console trong máy (Giai đoạn 6, đợt 1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-03 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-120 (thiết kế, đã gộp `main`) |
| Trạng thái | Xong (gộp `main` 2026-11-05) |

## Mục tiêu

Kho SQLite `data/search_cache.sqlite` giữ số liệu đã lấy từ Search Console (theo trang, theo ngày; từ khóa theo kỳ), xóa đi lấy lại được, kiểm cấu trúc khi đọc như `plan_cache`.

## Bối cảnh

- Thiết kế T-120 mục 3.1–3.4 (bảng, kiểu, ghi theo đoạn, giữ 16 tháng, ≤ 6 khoảng từ khóa, trần dung lượng, mã băm phạm vi), mục 6 dòng T-122.
- `CLAUDE.md` Lộ trình Giai đoạn 6; `docs/team/security.md`.

## Phạm vi

- **Được sửa:** mới: `seo_app/storage/search_cache.py`, `tests/test_search_cache.py`.
- **Không được sửa:** `seo_app/google/**`, `seo_app/tracking/**`, `app/**`, các kho SQLite khác.

## Yêu cầu

1. `SearchCacheStore`: bảng và kiểu đúng mục 3.1; ghi theo đoạn trong một giao dịch; giữ tối đa 16 tháng; ≤ 6 khoảng từ khóa; trần dung lượng (3.2).
2. Kiểm khi đọc: một dòng sai → bỏ cả cache; mã băm phạm vi (thuộc tính, tiền tố) đổi → bỏ cache.
3. Không mở khi `data/` là liên kết: dùng `seo_app/images/data_dir.dir_has_link` ngay từ đầu (không lặp SL-T117-1).
4. Mốc ngày giờ đọc từ cache kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError`, `ValueError` (như T-118, LC-T113-2).

## Quy tắc chung

- Không gọi Google thật hay website thật; test chỉ dùng dữ liệu giả (`tests/fake_google.py`, bộ chặn mạng của `tests/conftest.py`).
- Không thêm thư viện (thiết kế: không cần thư viện mới).
- Chủ dự án chưa trả lời 7 câu hỏi của T-120: phần nào phụ thuộc câu trả lời thì làm theo **lựa chọn khuyến nghị** và để hằng số/tên rõ ràng để đổi sau.
- Máy đang chạy nhiều agent: chỉ chạy test liên quan (kể cả test mọi nơi gọi hàm dùng chung mình sửa), `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120 (`docs/team/reports/T-120-la-chan.md` mục «Điều kiện theo phiếu»); thiết kế chi tiết ở `docs/team/reports/T-120-tho-may.md`.

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-9 | = Đ9: cache kiểm như `plan_cache`; một dòng sai → bỏ cả cache; mã băm phạm vi đổi → bỏ cache; không mở khi `data/` là liên kết | Dùng `data_dir.dir_has_link` ngay từ đầu (không lặp SL-T117-1); SQL chỉ tham số `?` | T-122 |
| LC-T120-10 | = Đ10: mốc ngày giờ từ cache, Google, WordPress kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError` | Thêm `ValueError` như T-118 (LC-T113-2) | T-122, T-123, T-124 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |

## Tiêu chí xong

- [ ] Yêu cầu 1–4 và mọi điều kiện LC-T120 ở trên có test
- [ ] Test liên quan + `uv run ruff check .` qua
- [ ] Báo cáo `docs/team/reports/T-122-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ. Lá Chắn: **đầy đủ**. Ước lượng: **M**.

## Ghi chú của Chỉ Huy

- Lập 2026-11-03 theo thiết kế T-120 (Lá Chắn rút gọn ĐẠT, Opus tạm) và chỉ đạo «làm liên tục, không cần hỏi». Đợt 1 gồm T-121, T-122, T-123, chạy song song được (thư mục riêng). Worktree `wt-T-122`, nhánh `team/T-122`.
- 2026-11-05 12:37 (Chỉ Huy B): gộp `main` cùng đợt 1 Giai đoạn 6 (T-121, T-122, T-123); Windows 23.548 test qua, 0 hỏng. Đã đẩy. Điều kiện Lá Chắn cho phiếu sau đã chép vào T-124.

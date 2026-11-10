# T-124 · Lấy số liệu Search Console, lưu thuộc tính (Giai đoạn 6, đợt 2)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-04 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Cao |
| Phụ thuộc | T-121, T-122, T-123 đã gộp `main` |
| Trạng thái | Xong (gộp `main` 2026-11-10) |

## Mục tiêu

`seo_app/tracking/refresh.py` nối client T-121, cache T-122 và lõi T-123: một cú bấm lấy số liệu còn thiếu, ghi vào cache theo đoạn; kiểm kết nối cho nút «Kiểm tra»; lưu thuộc tính Search Console vào `.env` qua `env_file` (câu hỏi 2 = A).

## Bối cảnh

- Thiết kế T-120 mục 1.2, 1.3, 2.5, 2.6, 3.3, mục 6 dòng T-124.
- Chủ dự án 04/11: câu 1 A (trang «📈 Theo dõi»), câu 7 B; câu 2–6 theo khuyến nghị A (thuộc tính chọn ở Cài đặt rồi ghi `.env`; chỉ hiện số đã chốt; không ghi Sheets; ngưỡng mặc định; không kiểm lập chỉ mục).
- Điều kiện Lá Chắn từ biên bản T-121, T-122, T-123 dành cho T-124 (xem mục «Yêu cầu bảo mật riêng»).

## Phạm vi

- **Được sửa:** mới `seo_app/tracking/refresh.py`, `tests/test_tracking_refresh.py`; sửa `seo_app/env_file.py` (`validate_gsc_site_url`, `set_gsc_site_url`, `clear_gsc_site_url`); **gom 3 hàm chuẩn hóa `WORDPRESS_URL`** (`site_prefix` ở `seo_app/google/search_console.py`, `site_base` ở `seo_app/tracking/`, `site_base` ở `seo_app/storage/search_cache.py`) về **một hàm dùng chung** với một luật đường con (Lá Chắn T-121, T-122, T-123).
- **Không được sửa:** `app/**` (T-125), README (T-126).

## Yêu cầu

1. Khoảng cần lấy, chia đoạn ≤ 31 ngày, đánh dấu tạm/chốt, từ khóa 2 kỳ, làm mới `SiteIndex` khi cũ, ngày đăng qua `post_statuses`, ghi từng đoạn, dừng ở lỗi đầu, chặn bấm lại (thiết kế 1.3, 3.3).
2. `check_connection` cho nút «Kiểm tra» (1.2).
3. `env_file`: `validate_gsc_site_url`, `set_gsc_site_url`, `clear_gsc_site_url`; chỉ lưu thuộc tính vừa nhận từ `sites` trong cùng phiên và qua bộ kiểm (LC-T120-12); báo khi biến môi trường `GSC_SITE_URL` có mặt (kể cả rỗng) đè `.env` (LC-T120-23).
4. Một client mỗi lần bấm; khóa cấp module để chỉ một lần lấy chạy cùng lúc (LC-T120-22); bắt lỗi đủ 20 lệnh (LC-T120-8).
5. Gom 3 hàm chuẩn hóa `WORDPRESS_URL` về một hàm, một luật đường con (Lá Chắn T-121 ghi nhận: `site_prefix` nhận đường con có `/..`, client WordPress không nhận); test bảng ca chung cho cả 3 nơi gọi cũ.
6. Phép thử chung với dataclass thật của T-122 qua `Protocol` của T-123 (`final` là `bool`, `day` là `date`; Thợ Máy T-123 đề nghị).
7. LC-T123-1 (Thấp, biên bản `docs/team/reports/T-123-la-chan.md`): sửa phần thuộc T-124, ghi phần còn lại cho T-125.
8. Sửa `env_file.py` và hàm chuẩn hóa dùng chung: chạy mọi test `.env` (`test_env_file*`, T-104, T-105, `test_t101_settings_google`) và mọi test của T-121, T-122, T-123; grep test theo hành vi bị ghim.

## Quy tắc chung

- Không gọi Google thật hay website thật; tham số test lớn luôn kèm `ids=` ngắn.
- Không thêm thư viện. Chỉ chạy test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120 (`docs/team/reports/T-120-la-chan.md` mục «Điều kiện theo phiếu»); thiết kế chi tiết ở `docs/team/reports/T-120-tho-may.md`.

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-8 | = Đ8: ≤ 20 lệnh mỗi lần bấm, không song song, thử lại 429 tối đa 1 lần, trần `startRow` | Xem LC-T120-22 (chỉ một lần lấy chạy cùng lúc) | T-121, T-124 |
| LC-T120-10 | = Đ10: mốc ngày giờ từ cache, Google, WordPress kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError` | Thêm `ValueError` như T-118 (LC-T113-2) | T-122, T-123, T-124 |
| LC-T120-12 | = Đ12: ghi `GSC_SITE_URL` qua `env_file` với bộ kiểm chặt, ghi nguyên tử, báo khi biến môi trường đè | Giá trị lưu phải là một mục vừa nhận từ `sites` trong cùng phiên **và** qua bộ kiểm, không nhận chữ gõ tay ở đường này | T-124 |
| LC-T120-13 | = Đ13: từ khóa không vào lời dặn AI, không ghi Sheet (trừ câu 7 = B theo LC-T120-24) | | T-124, T-125, T-127 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-21** | **Không gọi mạng khi mở trang**, áp cho cả trang theo dõi **và** mục Search Console trong Cài đặt («Tìm thuộc tính», «Kiểm tra» chỉ chạy khi bấm). Không `st.cache_data`/`st.cache_resource` có hạn quanh lệnh gọi mạng, không `st.fragment(run_every=…)`, không tự làm mới | Test AppTest: mở trang và Cài đặt dưới bộ chặn mạng, giả client đếm lệnh = 0 | T-124, T-125 |
| **LC-T120-22** | **Chỉ một lần lấy số liệu chạy cùng lúc** trong một tiến trình app: khóa cấp module. Tab thứ hai bấm thì báo «đang lấy ở tab khác», không gửi lệnh. Mốc «vừa lấy lúc …» để chặn bấm lại lưu trong cache (dùng chung các tab), không trong `session_state` | Tránh tốn gấp đôi hạn mức và hai lượt ghi xen nhau | T-124 |
| **LC-T120-23** | **Cảnh báo biến môi trường `GSC_SITE_URL` đè `.env`** theo đúng điều kiện của `load_settings`: biến **có mặt** là đè, kể cả rỗng (`name in os.environ`, như `password_hash_overridden` T-105). Không chép cách `.strip()` của thẻ Sheet (`settings.py:609`, lệch đã biết) | | T-124, T-125 |

Thêm từ Lá Chắn T-121 (`docs/team/reports/T-121-la-chan.md`, mục điều kiện cho phiếu sau), T-122, T-123: đọc và làm đủ phần ghi cho T-124.

## Tiêu chí xong

- [ ] Yêu cầu 1–8 và các LC ở trên có test
- [ ] Báo cáo `docs/team/reports/T-124-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ. Lá Chắn: **đầy đủ** (Fable khi có hạn mức). Ước lượng: **M**.

## Ghi chú của Chỉ Huy

- Lập 2026-11-04 theo thiết kế T-120 và các biên bản đợt 1. Worktree `wt-T-124`, nhánh `team/T-124` từ `main` có T-121, T-122, T-123.
- 2026-11-05 12:37 (Chỉ Huy B): giao 05/11 10:15 (Thợ Máy, `wt-T-124` từ `8caab2f`); mã `ac6a53a`, đang viết báo cáo.
- 2026-11-07 07:52 (Chỉ Huy B): Soi Lỗi ĐẠT (`37eb8a7`), Lá Chắn đầy đủ Fable ĐẠT CÓ ĐIỀU KIỆN (`682f62c`). ĐK1 → T-125, ĐK2 → T-126 phần 3, ĐK3 → buổi thử thật Google, ĐK4 → T-131. Gộp `main` sau toàn bộ test.
- 2026-11-10 13:03 (Chỉ Huy B): Gộp `main` (`06a1b0e`); toàn bộ test chạy hết 100% không ca hỏng (dòng tổng kết mất vì phiên khởi động lại), rồi chạy lại cùng T-125, T-130, T-132: Windows 24.109 test qua, 0 hỏng. Đã đẩy.

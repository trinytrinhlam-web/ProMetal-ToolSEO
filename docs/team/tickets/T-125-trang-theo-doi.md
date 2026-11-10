# T-125 · Trang «📈 Theo dõi» và mục Search Console trong Cài đặt (Giai đoạn 6, đợt 3)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-05 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Cao |
| Phụ thuộc | T-124 (Lá Chắn Fable ĐẠT CÓ ĐIỀU KIỆN; nhánh `team/T-124`) |
| Trạng thái | Đang làm |

## Mục tiêu

Giao diện cho phần theo dõi Google: trang mới **«📈 Theo dõi»** trên menu (giữa Kế hoạch và Cài đặt) và mục **Search Console** trong Cài đặt → Google, dùng `seo_app/tracking/refresh.py` của T-124.

## Bối cảnh

- Thiết kế T-120 (`docs/team/reports/T-120-tho-may.md`) mục 1 (luồng người dùng), 4.1 (phương án A, phác thảo), 4.4 (phần chung, hiển thị an toàn).
- Chủ dự án 04/11: **câu 1 A** (trang mới «📈 Theo dõi»); câu 2 A (chọn thuộc tính ở Cài đặt từ «Tìm thuộc tính»); câu 3 A (chỉ hiện số đã chốt, ghi «số liệu tới hết ngày …»); câu 4 A (không ghi Sheets); câu 5 A (ngưỡng mặc định); câu 6 A (không kiểm lập chỉ mục trong app: bài «chưa có lượt hiển thị» kèm hướng dẫn kiểm bằng tay ô «Kiểm tra URL»). Câu 7 B làm ở T-127 (để chỗ cho nút «Đưa vào kế hoạch»).
- Điều kiện Lá Chắn dành cho T-125 trong các biên bản T-121, T-123 (LC-T123-1), T-124 (`docs/team/reports/T-124-la-chan.md`, điều kiện 1).

## Yêu cầu

1. Trang `app/views/tracking.py`, thêm vào `PAGES` trong `app/main.py` giữa Kế hoạch và Cài đặt; kiểm đăng nhập như mọi trang.
2. Chọn khoảng 7/28/91 ngày hoặc tự chọn, so kỳ trước; bảng từng bài (hiển thị, click, CTR, vị trí), nhãn (tụt hạng, mất click, chưa có lượt hiển thị, nhiều hiển thị ít click), «Trang khác»; bảng từ khóa của một bài; biểu đồ `st.vega_lite_chart` dựng từ khuôn cố định (LC-T120-20).
3. Nút «Lấy số liệu» gọi `refresh`; hiện «đang lấy ở tab khác» khi bận; mốc «vừa lấy lúc …»; câu cố định khi có mục bị bỏ (`skipped_items > 0`); nút «Xóa bản lưu tạm».
4. Cài đặt → Google: mục Search Console: «Tìm thuộc tính» (giữ kết quả trong `session_state`, truyền **đúng đối tượng đó** vào `save_property`), «Kiểm tra», cảnh báo khi biến môi trường `GSC_SITE_URL` đè `.env`, cảnh báo khi quyền cao hơn «Hạn chế» (T-121).
5. **Mở trang và Cài đặt không gọi mạng** (chỉ khi bấm nút); AppTest dưới bộ chặn mạng chứng minh (LC-T120-21).
6. Mọi chữ từ Google (từ khóa, đường dẫn, tên máy) hiện **chữ thuần**: qua `escape_markdown`, không `unsafe_allow_html`, không thành link; bảng có chữ Google dùng `safe_rows` (LC-T120-11, -19).
7. Để chỗ (chưa làm) cho nút «Đưa vào kế hoạch» của T-127.
8. Không lùi trang khác; `tests/test_app_pages.py` mở được trang mới.

## Phạm vi

- **Được sửa:** mới `app/views/tracking.py`; `app/main.py` (`PAGES`); `app/views/settings.py` (mục Search Console); `app/assets/style.css` nếu cần; test AppTest.
- **Không được sửa:** `seo_app/tracking/**`, `seo_app/google/**`, `seo_app/storage/**` (nhờ Thợ Máy nếu cần đổi), README (T-126).

## Quy tắc chung

- Không gọi Google, website thật; tham số test lớn kèm `ids=` ngắn; chỉ chạy test liên quan + `uv run ruff check .`.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120 (`docs/team/reports/T-120-la-chan.md` mục «Điều kiện theo phiếu»):

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-11 | = Đ11: chữ từ Google chỉ hiện dạng chữ thuần; không `unsafe_allow_html`; chú thích nổi của biểu đồ chỉ có số và ngày | **Mọi** bảng có chữ từ Google (từ khóa, đường dẫn, «Trang khác», tên thuộc tính) đi qua `safe_rows` trước `st.dataframe`; không cột `LinkColumn` nào cho chữ từ Google | T-123, T-125 |
| LC-T120-13 | = Đ13: từ khóa không vào lời dặn AI, không ghi Sheet (trừ câu 7 = B theo LC-T120-24) | | T-124, T-125, T-127 |
| LC-T120-14 | = Đ14: trang theo dõi kiểm đăng nhập như mọi trang; không gọi mạng khi mở trang; client tạo mới mỗi lần bấm | Xem LC-T120-21 (áp cả cho Cài đặt) | T-125 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-19** | **Đường dẫn đã giải mã và tên máy từ Google** (mục «Trang khác», 3 tên máy ngoài website ở «Kiểm tra»): qua `clean_text` sau khi giải mã `%`, cắt độ dài, hiện như chữ, không bao giờ thành link. Tên máy kiểm đúng dạng tên miền trước khi hiện | Giải mã `%` ra ký tự đảo hướng, ký tự vô hình thì bị `clean_text` bỏ | T-123, T-125 |
| **LC-T120-20** | **Biểu đồ dựng từ khuôn cố định trong code**: dữ liệu nhúng chỉ có số và ngày; không chữ nào từ Google hay WordPress nằm trong đặc tả Vega-Lite (tên bài đặt **ngoài** biểu đồ, bằng `st.markdown(escape_markdown(…))`). Không `expr` dựng từ chữ ngoài, không kênh `href`, không nguồn dữ liệu `url` | Vega có lịch sử lỗi chạy mã qua biểu thức; giữ đặc tả cố định là cách chắc nhất | T-125 |
| **LC-T120-21** | **Không gọi mạng khi mở trang**, áp cho cả trang theo dõi **và** mục Search Console trong Cài đặt («Tìm thuộc tính», «Kiểm tra» chỉ chạy khi bấm). Không `st.cache_data`/`st.cache_resource` có hạn quanh lệnh gọi mạng, không `st.fragment(run_every=…)`, không tự làm mới | Test AppTest: mở trang và Cài đặt dưới bộ chặn mạng, giả client đếm lệnh = 0 | T-124, T-125 |
| **LC-T120-23** | **Cảnh báo biến môi trường `GSC_SITE_URL` đè `.env`** theo đúng điều kiện của `load_settings`: biến **có mặt** là đè, kể cả rỗng (`name in os.environ`, như `password_hash_overridden` T-105). Không chép cách `.strip()` của thẻ Sheet (`settings.py:609`, lệch đã biết) | | T-124, T-125 |

Thêm: điều kiện 1 của Lá Chắn T-124 (mục 4 ở trên là tóm tắt), phần T-125 của Lá Chắn T-121 và LC-T123-1.

## Tiêu chí xong

- [ ] Yêu cầu 1–8; test AppTest; báo cáo `docs/team/reports/T-125-hoa-si.md` (kèm ảnh chụp chữ mô tả bố cục)

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ. Lá Chắn: **đầy đủ**. Ước lượng: **L** (có thể 2 lượt).

## Ghi chú của Chỉ Huy

- Lập 2026-11-05 theo thiết kế T-120 và quyết định chủ dự án 04/11. Worktree `wt-T-125`, nhánh `team/T-125` từ `team/T-124` (`682f62c`); gộp `main` vào nhánh trước khi nộp.

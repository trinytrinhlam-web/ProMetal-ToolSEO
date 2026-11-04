# T-123 · Lõi tính toán theo dõi bài (Giai đoạn 6, đợt 1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-03 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-120 (thiết kế, đã gộp `main`) |
| Trạng thái | Đang làm |

## Mục tiêu

Gói mới `seo_app/tracking/` gồm các hàm thuần (không mạng, không file): khớp địa chỉ trang với bài WordPress và dòng kế hoạch, kỳ ngày, cộng dồn và so hai kỳ, nhãn đánh dấu bài, gộp từ khóa.

## Bối cảnh

- Thiết kế T-120 mục 1.4–1.7 (khớp địa chỉ, khoảng ngày và so kỳ, đánh dấu bài, từ khóa), 2.6 (ngày giờ PT), 3.1 (hai kiểu dữ liệu), mục 6 dòng T-123.
- `CLAUDE.md` Lộ trình Giai đoạn 6; `docs/team/security.md`.

## Phạm vi

- **Được sửa:** mới: `seo_app/tracking/__init__.py`, `model.py`, `periods.py`, `match.py`, `stats.py`, `flags.py`, `keywords.py`, `tests/test_tracking_*.py`.
- **Không được sửa:** `seo_app/google/**`, `seo_app/storage/**`, `app/**`, `seo_app/plan/**` (chỉ nhập `PlanRow`, `PublishedItem` có sẵn).

## Yêu cầu

1. `model.py`: `Protocol` của hai kiểu ở 3.1 (để T-122 và T-123 không phụ thuộc nhau), `PageStats`, `Comparison`, `Flag`, `TrackedPage`.
2. `periods.py`: ngày theo giờ Google (PT), kỳ 7/28/91/tùy chọn, kỳ trước, cùng kỳ năm trước, tuần; ca đổi giờ PT (08/03, 01/11).
3. `match.py`: `page_key`, khớp `SiteIndex`, dòng kế hoạch, «Trang khác» (1.4); bài đổi slug; dòng kế hoạch slug trùng hai bài.
4. `stats.py`: cộng dồn, vị trí trung bình theo lượt hiển thị, so hai kỳ (1.5).
5. `flags.py`: nhãn tụt hạng, mất click, chưa có lượt hiển thị, nhiều hiển thị ít click; **ngưỡng là hằng có tên** theo mặc định ở câu hỏi 5 (khuyến nghị A) (1.6).
6. `keywords.py`: gộp có dấu/không dấu bằng `fold_key`, từ khóa chính, từ khóa mới (1.7).

## Quy tắc chung

- Không gọi Google thật hay website thật; test chỉ dùng dữ liệu giả (`tests/fake_google.py`, bộ chặn mạng của `tests/conftest.py`).
- Không thêm thư viện (thiết kế: không cần thư viện mới).
- Chủ dự án chưa trả lời 7 câu hỏi của T-120: phần nào phụ thuộc câu trả lời thì làm theo **lựa chọn khuyến nghị** và để hằng số/tên rõ ràng để đổi sau.
- Máy đang chạy nhiều agent: chỉ chạy test liên quan (kể cả test mọi nơi gọi hàm dùng chung mình sửa), `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120 (`docs/team/reports/T-120-la-chan.md` mục «Điều kiện theo phiếu»); thiết kế chi tiết ở `docs/team/reports/T-120-tho-may.md`.

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-6 | = Đ6: thuộc tính phải phủ website; từ chối `http://` và thuộc tính staging; dòng ngoài tiền tố bị bỏ cả khi Google trả | Xem LC-T120-17 (kiểm theo từng phần tên miền) | T-121, T-123 |
| LC-T120-10 | = Đ10: mốc ngày giờ từ cache, Google, WordPress kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError` | Thêm `ValueError` như T-118 (LC-T113-2) | T-122, T-123, T-124 |
| LC-T120-11 | = Đ11: chữ từ Google chỉ hiện dạng chữ thuần; không `unsafe_allow_html`; chú thích nổi của biểu đồ chỉ có số và ngày | **Mọi** bảng có chữ từ Google (từ khóa, đường dẫn, «Trang khác», tên thuộc tính) đi qua `safe_rows` trước `st.dataframe`; không cột `LinkColumn` nào cho chữ từ Google | T-123, T-125 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-19** | **Đường dẫn đã giải mã và tên máy từ Google** (mục «Trang khác», 3 tên máy ngoài website ở «Kiểm tra»): qua `clean_text` sau khi giải mã `%`, cắt độ dài, hiện như chữ, không bao giờ thành link. Tên máy kiểm đúng dạng tên miền trước khi hiện | Giải mã `%` ra ký tự đảo hướng, ký tự vô hình thì bị `clean_text` bỏ | T-123, T-125 |

## Tiêu chí xong

- [ ] Yêu cầu 1–6 và mọi điều kiện LC-T120 ở trên có test
- [ ] Test liên quan + `uv run ruff check .` qua
- [ ] Báo cáo `docs/team/reports/T-123-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ. Lá Chắn: **rút gọn** (hàm thuần). Ước lượng: **M–L**.

## Ghi chú của Chỉ Huy

- Lập 2026-11-03 theo thiết kế T-120 (Lá Chắn rút gọn ĐẠT, Opus tạm) và chỉ đạo «làm liên tục, không cần hỏi». Đợt 1 gồm T-121, T-122, T-123, chạy song song được (thư mục riêng). Worktree `wt-T-123`, nhánh `team/T-123`.

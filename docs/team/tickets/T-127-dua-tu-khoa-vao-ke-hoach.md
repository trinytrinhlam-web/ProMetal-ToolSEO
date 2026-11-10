# T-127 · Nút «Đưa vào kế hoạch»: từ khóa Google thành đề xuất «Thêm bài» ở trang Kế hoạch (Giai đoạn 6)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`); Chỉ Huy duyệt cho Thợ Máy thêm nút trên `app/views/tracking.py` để khỏi chia hai nhánh |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-07 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Trung bình (chủ dự án chọn câu 7 = B, 04/11) |
| Phụ thuộc | T-125 (Lá Chắn Fable ĐẠT CÓ ĐIỀU KIỆN; nhánh `team/T-125`) |
| Trạng thái | Đã qua Lá Chắn; chờ gộp |

## Mục tiêu

Ở bảng từ khóa của trang «📈 Theo dõi», người dùng tick tối đa 10 từ khóa rồi bấm «Đưa vào kế hoạch»: các từ khóa thành đề xuất «Thêm bài» ở trang Kế hoạch, duyệt như mọi đề xuất (không qua AI).

## Bối cảnh

- Thiết kế T-120 (`docs/team/reports/T-120-tho-may.md`) câu hỏi 7 và mục 6 dòng T-127; chủ dự án chọn **B** ngày 04/11.
- Bộ đề xuất bảng có sẵn ở `seo_app/plan/propose.py` (T-098): kiểm trùng, trùng bài đã đăng, trang cửa ngõ.
- Lá Chắn T-125 (`docs/team/reports/T-125-la-chan.md`) điều kiện B.1: T-127 làm đúng LC-T120-24, Lá Chắn kiểm đầy đủ.

## Yêu cầu

1. Hàm trong `seo_app/plan/propose.py` nhận danh sách từ khóa (≤ 10) và trả đề xuất «Thêm» theo khuôn đề xuất bảng có sẵn; không gọi AI; kiểm trùng kế hoạch, trùng bài đã đăng, trang cửa ngõ như T-098.
2. Bộ lọc từ khóa **chặt hơn** ô từ khóa thường (LC-T120-24): chỉ chữ (kể cả tiếng Việt), số, khoảng trắng, `-`; ≤ 80 ký tự; bỏ từ khóa có số điện thoại, email, địa chỉ web; câu báo cố định cho từ khóa bị bỏ.
3. Nút trên bảng từ khóa (`app/views/tracking.py`): tick ≤ 10; bấm thì đưa sang trang Kế hoạch dạng đề xuất chờ duyệt (không ghi thẳng Sheet); chữ hiện chữ thuần.
4. Từ khóa không vào lời dặn AI khi tạo đề xuất (LC-T120-13).
5. Không lùi trang Kế hoạch, T-098, T-125; `test_app_pages.py`.

## Phạm vi

- **Được sửa:** `seo_app/plan/propose.py` (thêm hàm), `app/views/tracking.py` (nút), `app/views/plan.py` (nhận đề xuất nếu cần), test.
- **Không được sửa:** `seo_app/google/**`, `seo_app/storage/**`, client Sheets.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120:

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-13 | = Đ13: từ khóa không vào lời dặn AI, không ghi Sheet (trừ câu 7 = B theo LC-T120-24) | | T-124, T-125, T-127 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-24** | (Chỉ khi câu 7 = B) **Từ khóa sang Kế hoạch**: chỉ nhận từ khóa qua bộ lọc chặt hơn ô từ khóa thường. Chỉ chữ (kể cả tiếng Việt), số, khoảng trắng, `-`; ≤ 80 ký tự; bỏ từ khóa có số điện thoại/email (`personal_info`). Hiện nguyên văn cho người dùng tick; ≤ 10 mỗi lần; không AI ở bước này; đề xuất ghi nguồn «Search Console». Vẫn qua mọi bộ kiểm của dòng kế hoạch; khi bài được viết, từ khóa vào lời dặn AI trong khung dữ liệu như hiện nay (T-098) | Kẻ xấu muốn «cài» lệnh vào từ khóa phải có nhiều người gõ cùng một câu trong 2–3 tháng (Google ẩn từ khóa hiếm). Bộ lọc ký tự làm câu lệnh dài, có dấu câu không lọt | T-127 |

## Tiêu chí xong

- [ ] Yêu cầu 1–5; test liên quan + `uv run ruff check .`; báo cáo `docs/team/reports/T-127-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: **đầy đủ** (LC-T120-24). Ước lượng: **S–M**.

## Ghi chú của Chỉ Huy

- Lập 2026-11-07. Worktree `wt-T-127`, nhánh `team/T-127` từ `team/T-125` (`09fdad2`).
- 2026-11-10 13:03 (Chỉ Huy B): Thợ Máy 2 lượt, Soi Lỗi `8e2cd5a`, Lá Chắn Fable `08b24df` ĐẠT CÓ ĐIỀU KIỆN (B.1 → T-133, B.2 → README, B.3 → sổ rủi ro: T-126 lượt cuối). Chủ dự án đồng ý ghi sổ rủi ro LC-T120-24 (10/11). Gộp cùng T-126 sau toàn bộ test.

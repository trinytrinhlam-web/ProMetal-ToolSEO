# T-057 · Bộ lọc hồ sơ: nhãn tiêu đề vắt nhiều dòng (theo dõi sau T-045)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 2 (dọn lỗi) |
| Mức ưu tiên | Thấp (phải có trên bảng việc trước khi hết giai đoạn; nếu chủ dự án không muốn sửa thì ghi sổ rủi ro) |
| Phụ thuộc | T-045 đã gộp (`cc3099f`) |
| Trạng thái | Mới |

## Mục tiêu

Nhãn `[CẦN XÁC NHẬN]` gắn trên tiêu đề nhưng bị tách qua nhiều dòng vẫn giấu đúng cả mục khỏi prompt AI.

## Bối cảnh

Lá Chắn T-045 kết luận ĐẠT CÓ ĐIỀU KIỆN, điều kiện là mở phiếu này (`docs/team/reports/T-045-la-chan.md`). Hai lỗi có từ trước trên `main`, T-045 không làm tệ hơn (`docs/team/reports/T-045-soi-loi.md`):

- **SL-T045-1:** nhãn trên tiêu đề vắt qua 3 dòng, ví dụ `## 7 [CẦN` / `XÁC` / `NHẬN]` / `- BIMAT` / `## 8`: cả mục tới AI, vì tiêu đề chờ chỉ ghép với đúng 1 dòng kế. Lá Chắn tìm thêm biến thể tiêu đề thụt lề: `- a` / `  ## 7 [CẦN` / `  XÁC` / `  NHẬN] BIMAT`: dòng `NHẬN] BIMAT` lọt.
- **SL-T045-2:** nhãn tiêu đề bị tách hai lần liền nhau, ví dụ `## 7 [CẦN XÁC` / `## NHẬN] [CẦN XÁC` / `## NHẬN]` / `- BIMAT`: dòng `## NHẬN]` cuối và `- BIMAT` tới AI.

## Phạm vi

- **Được sửa:** `seo_app/content/rules.py`, test mới cho phần mình làm. Bỏ đúng 5 `xfail` ở `tests/test_soi_loi_t045.py` (khoảng dòng 266–296), ghi tên vào báo cáo.
- **Không được sửa:** `app/**`, `config/**`, `tests/conftest.py`, test khác.

## Yêu cầu

1. Sửa SL-T045-1 (cả biến thể tiêu đề thụt lề) và SL-T045-2.
2. Giữ tuyến tính: giới hạn số dòng chờ ghép nhãn; có test tốc độ với đầu vào xấu cỡ 1 MB (`tests/timing.py`).
3. Hồ sơ thật `config/business_profile.md`: phần AI thấy giống hệt `main` (so sha256).
4. Không lùi: chạy lại fuzz so với `main` như Soi Lỗi và Lá Chắn T-045 (0 dòng có nhãn, 0 dòng của ý hoặc mục có nhãn tới AI).

## Yêu cầu bảo mật riêng

A1, A3, F3.

## Tiêu chí xong

- [ ] 2 lỗi đã sửa, 5 `xfail` bỏ và qua, có test biến thể thụt lề
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-057-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A3, F3).

## Ghi chú của Chỉ Huy

- Làm trên nhánh tạm `team/T-057`, tạo từ `main`. Ưu tiên thấp hơn các phiếu Giai đoạn 3; giao khi còn chỗ.

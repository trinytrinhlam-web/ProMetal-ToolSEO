# T-068 · Dọn lỗi Thấp bước code tự sửa alt (sau T-062)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi gộp T-056) |
| Phụ thuộc | T-062 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Bước code tự sửa alt (`clean_suggestion`, tiền tố ảnh AI) không nhận alt vô nghĩa, không lặp tiền tố, không cắt mất chữ.

## Bối cảnh

Báo cáo Soi Lỗi T-062 (`docs/team/reports/T-062-soi-loi.md`) và biên bản Lá Chắn T-062 (`docs/team/reports/T-062-la-chan.md`, điều kiện 2): SL-T062-1 → -3, mỗi lỗi có test `xfail` trong `tests/test_soi_loi_t062.py`.

## Phạm vi

- **Được sửa:** `seo_app/images/alt.py`, `tests/test_t062_alt_prompt.py`, gỡ `xfail` trong `tests/test_soi_loi_t062.py`.
- **Không được sửa:** `seo_app/ai/**`, `seo_app/content/**`, `app/**`, `config/**`.

## Yêu cầu

1. **SL-T062-1:** alt không có chữ hay số nào («???», «!!!», chỉ biểu tượng) bị coi như AI không viết được alt, cả ảnh AI («Minh họa ???») lẫn ảnh thật.
2. **SL-T062-2:** nhận ra tiền tố AI tự viết trong ngoặc góc, ngoặc kép, hay dính dấu câu lạ («Minh họa «Minh họa» cửa cuốn», «Ảnh minh họa (AI): «Ảnh minh họa (AI)» ray dưới», «Minh họa ! Cửa cuốn», «Minh họa … cửa cuốn»), bỏ đi rồi ghi đúng một tiền tố chuẩn.
3. **SL-T062-3:** bỏ tiền tố AI tự viết **trước**, ghép tiền tố chuẩn, rồi mới cắt theo giới hạn; với `max_chars = 20` vẫn ra alt có nghĩa.
4. Giữ nguyên bảo đảm C6 của Lá Chắn T-051 (mọi test C6 hiện có phải qua). Gỡ 3 dấu `xfail` khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

A1 (C6: ảnh AI luôn có tiền tố do code bảo đảm).

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_ai_images.py tests/test_soi_loi_t050.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-068-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (C6).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 2 của Lá Chắn T-062. Làm trên nhánh tạm `team/T-068`, tạo từ `main` sau khi T-062 gộp. Có thể giao cùng lúc với T-065 (Ngòi Bút, `config/`) vì khác file.

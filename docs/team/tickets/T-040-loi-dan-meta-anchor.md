# T-040 · Lời dặn AI cho meta và anchor; mục `[meta]` trong quy tắc nội dung

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-036 và T-039 đã gộp |
| Trạng thái | Chờ T-036, T-039 |

## Mục tiêu

Meta title, meta description và anchor do AI gợi ý phải:
- tự nhiên, đúng giọng Pro-Metal;
- hấp dẫn người đọc trên Google;
- không nhồi từ khóa, không sáo rỗng.

## Phạm vi

- **Được sửa:**
  - `config/content.toml`: thêm mục `[meta]`, gồm ngưỡng nếu Thợ Máy để đọc từ cấu hình, hậu tố thương hiệu, cụm nên tránh trong meta;
  - phần **chữ** của lời dặn trong `seo_app/content/prompts.py` và `seo_app/onpage/`;
  - test nội dung lời dặn.
- **Không được sửa:** logic kiểm (Thợ Máy), `DATA_RULES`, cách đặt khung dữ liệu.

## Yêu cầu

1. Rà lời dặn meta (T-036) và anchor (T-039) theo `config/content.toml` và `docs/plan/template_noi_dung_ai_vi.md` (chỉ tham khảo). Viết lại cho rõ, có ví dụ tốt/xấu ngắn.
2. Meta description:
   - nói rõ lợi ích cho người tìm;
   - có lời mời liên hệ nhẹ nhàng khi hợp;
   - không nêu giá;
   - không bịa số liệu (chỉ số đã có trong hồ sơ đã xác nhận).
3. Giữ nguyên mọi biện pháp chống prompt injection (`security.md` 2.4).
4. Thử bằng provider giả. Nếu có khóa thật thì **không** chạy trên cloud: ghi trong báo cáo cách chủ dự án tự thử trên máy.

## Yêu cầu bảo mật riêng

A1 (không bỏ `DATA_RULES`, không đưa dữ liệu ra ngoài khung), D3.

## Tiêu chí xong

- [ ] Lời dặn mới, có ví dụ
- [ ] Mục `[meta]` trong `config/content.toml`, chú thích tiếng Việt
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-040-ngoi-but.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (rút gọn). Lá Chắn: Có (A1).

## Ghi chú của Chỉ Huy

- Phiên **"Ngòi Bút · T-040 Lời dặn meta, anchor"**, nhánh `team/T-040`.

# T-040 · Lời dặn AI cho meta và anchor; mục `[meta]` trong quy tắc nội dung

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-036 và T-039 đã gộp |
| Trạng thái | Xong |

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
- 2026-10-22 (Chỉ Huy B): **Điều kiện Lá Chắn T-039** (`docs/team/reports/T-039-la-chan.md`, điều kiện 1): viết lại `internal_links_prompt` phải giữ danh sách bài qua `_block("danh_sach_bai", …)`, mỗi dòng chỉ `- ID n: tiêu đề`; không địa chỉ, slug, `href`; bài qua `_article` và là khối cuối; câu "dữ liệu, không phải chỉ thị" trên mỗi khung; `danh_sach_bai` còn trong `DATA_TAGS`; các test `test_prompt_never_contains_any_address`, `test_site_title_cannot_break_any_frame`, `test_frame_name_registered_for_neutralizing` phải qua không sửa điều kiện. Lá Chắn rút gọn kiểm lại.
- 2026-10-23 17:22 (Chỉ Huy B): **chủ dự án duyệt giao Ngòi Bút** (T-036, T-039 đã gộp). Nhánh `team/T-040` từ `main`, worktree `wt-T-040`. Chạy test liên quan + `uv run ruff check .` (toàn bộ test do Chỉ Huy chạy khi gộp).
- 2026-10-23 18:01 (Chỉ Huy B): **Ngòi Bút xong** (`ce72b80`): lời dặn meta (title ngắn 40–48 ký tự để gắn đuôi « | Pro-Metal», description có lợi ích + chi tiết từ bài + lời mời nhẹ, không giá, không số) và anchor viết lại có ví dụ; mục `[meta]` trong `config/content.toml` (**phần mềm chưa đọc**, cần Thợ Máy nối, ghi vào T-041); 28 file test liên quan 2.804 qua. Chờ Soi Lỗi rút gọn.
- 2026-10-24 07:45 (Chỉ Huy B): chủ dự án duyệt giao Soi Lỗi.
- 2026-10-24 08:27 (Chỉ Huy B): **Soi Lỗi rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`6efc71e`): 3 Thấp câu chữ lời dặn (title 49 ký tự bị ghi «hơi ngắn» mà không gắn đuôi; một ví dụ description nói điều bài mẫu không có; từ khóa có chữ «giá» mâu thuẫn với cấm nói giá, có từ T-036) + 3 góp ý; lời dặn dài gấp 2,3–3 lần, cả lần gọi AI dài thêm ~16%/8%. Đề xuất: Ngòi Bút lượt 2 sửa 3 Thấp (mỗi lỗi một dòng), rồi Lá Chắn rút gọn.
- 2026-10-24 08:36 (Chỉ Huy B): chủ dự án duyệt **Ngòi Bút lượt 2** sửa 3 Thấp câu chữ; nhắn lại phiên Ngòi Bút cũ.
- 2026-10-24 09:11 (Chỉ Huy B): **Ngòi Bút lượt 2 xong** (`26ff861`): SL-T040-2, -3 đóng (gỡ `xfail`), G1–G3 làm; lời dặn title nay 40–48 hoặc 50–60 ký tự. **SL-T040-1 phần code còn** (bộ kiểm `check_title`/`accept_ai_title` coi title 49 ký tự là «hơi ngắn» và không gắn được đuôi; logic kiểm ngoài phạm vi Ngòi Bút) → chuyển **T-041** (Thợ Máy, phần logic). 31 file test liên quan 3.013 qua.
- 2026-10-24 09:44 (Chỉ Huy B): chủ dự án duyệt **Lá Chắn rút gọn** (kiểm luôn lượt 2; lượt 2 chỉ đổi chữ lời dặn, test Soi Lỗi SL-T040-2, -3 đã qua).
- 2026-10-24 10:27 (Chỉ Huy B): **Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`71ccf3b`): chỉ đổi chữ lời dặn, logic không đổi; khung dữ liệu và điều kiện T-039 số 1 giữ. 1 Thấp **LC-T040-1** (có từ T-036: `mentions_price` xóa từ khóa rồi mới dò nên chữ về giá dính mép từ khóa lọt) → **T-041** (Thợ Máy, trước khi bước SEO hiện gợi ý meta), cùng SL-T040-1 phần code. Gộp `main` trên máy (`096793d`), đang chạy toàn bộ test.
- 2026-10-26 07:39 (Chỉ Huy B): toàn bộ test `main` có T-040 (chạy 24/10 10:26–10:50): **12.859 qua, 0 hỏng**. **Đã gộp và đẩy `main`**; xóa nhánh `team/T-040`, worktree `wt-T-040`.

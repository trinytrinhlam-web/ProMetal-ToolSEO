# T-036 · Meta title, meta description, slug: kiểm độ dài, kiểm trùng, AI gợi ý

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 (nhóm 1: logic thuần, test giả) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không. Chạy song song được với T-037, T-038 (mỗi phiếu thêm file riêng trong `seo_app/onpage/`) |
| Trạng thái | Chờ chỗ trống |

## Mục tiêu

Phần logic cho bước 4 "SEO" của trang Soạn bài:
- kiểm meta title, meta description, slug đúng chuẩn và không trùng bài khác trên site;
- AI gợi ý vài phương án meta, code kiểm từng phương án trước khi đưa người dùng chọn.

Phiếu này chưa làm giao diện (T-041) và chưa ghi lên WordPress (T-042).

## Bối cảnh

Thiết kế đã duyệt: `docs/team/reports/T-033-tho-may.md`. Đọc kỹ:
- mục 5 (5.1 → 5.4): ngưỡng độ dài, NFC, `%%`, slug, kiểm trùng;
- mục 6: phiếu "T-034 Meta" trong báo cáo, nay đánh số lại thành **T-036**.

Yêu cầu gốc của chủ dự án: `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md`, YC-401, YC-402, M7 mục 6 và 9.

## Phạm vi

- **Được sửa:**
  - mới: `seo_app/onpage/__init__.py`. Nội dung **đúng một dòng** `"""Tối ưu on-page: meta, liên kết nội bộ, schema (Giai đoạn 4)."""`. T-037, T-038 cũng tạo file này y hệt, nên gộp không xung đột;
  - mới: `seo_app/onpage/meta.py`, `tests/test_onpage_meta.py`;
  - sửa: `seo_app/content/workflow.py` (chỉ **thêm** hàm tạo meta), `seo_app/content/prompts.py` (chỉ **thêm** hàm lời dặn meta và khuôn trả về);
  - sửa: `config/ai.toml` (chỉ **thêm** mục `[tasks.meta]`, cùng hãng/mô hình với `[tasks.review]`, `effort = "low"`, `max_tokens` nhỏ).
- **Không được sửa:** `app/**`, `seo_app/ai/**`, `seo_app/sanitize.py`, `seo_app/wordpress/**`, `seo_app/storage/**`.

## Yêu cầu

1. **Đếm và kiểm (không AI).** Hàm thuần:
   - chuẩn hóa NFC, bỏ ký tự vô hình, gộp khoảng trắng, bỏ xuống dòng;
   - trả kết quả kiểm từng trường (title, description, slug) theo bảng ngưỡng mục 5.1: **Nên / Cảnh báo / Chặn**, kèm câu giải thích tiếng Việt;
   - chặn: rỗng, có thẻ HTML, có `%%`; slug có ký tự ngoài `a-z0-9-`.
2. **Slug.** Dùng `seo_app/text.py::slugify`, cắt mặc định 60, bỏ từ nối vô nghĩa ở cuối (danh sách ngắn, có test). Slug do người dùng hoặc phiếu giao bài đưa vào thắng slug tự sinh.
3. **Kiểm trùng (mục 5.4).**
   - Đầu vào: danh sách bài của site. Dùng kiểu dữ liệu đơn giản tự định nghĩa trong `meta.py` (id, tiêu đề, meta title, meta description, slug). T-037 sẽ đưa dữ liệu thật vào; không phụ thuộc code T-037.
   - Chuẩn hóa: NFC, chữ thường, bỏ dấu câu, bỏ hậu tố thương hiệu.
   - Trùng hệt → Chặn. Giống nhiều (thư viện chuẩn, ngưỡng nêu trong code) → Cảnh báo, kèm tên bài bị giống.
   - Slug trùng → Chặn.
   - Bỏ qua chính bài đang sửa (theo id).
4. **AI gợi ý meta (mục 5.3).**
   - Hàm trong `workflow.py` gọi lớp provider đã có với việc `meta`.
   - Lời dặn: bài viết, từ khóa, hồ sơ doanh nghiệp nằm trong khung dữ liệu, có `DATA_RULES`, vô hiệu thẻ khung (`security.md` 2.4).
   - Khuôn trả về (pydantic): 3 title, 2 description.
   - **Kiểm từng gợi ý (A2):** `strip_tags`, NFC, không URL/link, không `%%`, không cụm cấm (`config/content.toml`), không nêu giá (`BAN-GIAO.md` 7.4), có từ khóa chính (so cả bản không dấu), trong ngưỡng Chặn. Gợi ý hỏng thì bỏ; hỏng hết thì `AIError` tiếng Việt.
   - Chữ AI qua `clean_ai_text` trước khi trả ra.
   - Viết lại riêng title hoặc riêng description được, không đụng phần kia.
5. **Hậu tố thương hiệu** (câu hỏi 3 cho chủ dự án, chưa trả lời): làm thành tham số. Mặc định thêm `" | Pro-Metal"` khi title còn chỗ (≤ 60 ký tự sau khi thêm), theo phương án đề xuất. Đổi được bằng một hằng số hoặc tham số, không phải sửa nhiều chỗ. Ghi rõ trong báo cáo.
6. **Test**, provider giả, không gọi mạng:
   - chữ NFD dài gấp đôi khi đếm thô mà đếm NFC vẫn đúng;
   - `%%`, thẻ HTML, URL trong gợi ý AI bị bỏ;
   - từ khóa thiếu dấu vẫn được nhận;
   - trùng hệt, giống nhiều, slug trùng;
   - AI trả khung dữ liệu giả hoặc lệnh lạ trong bài viết;
   - tốc độ tuyến tính với danh sách bài lớn (`tests/timing.py`).

## Yêu cầu bảo mật riêng

A1, A2, U1 (chữ AI qua `clean_ai_text`), D1 (không thư viện mới), D3.

## Tiêu chí xong

- [ ] Kiểm độ dài, slug, trùng: có test
- [ ] AI gợi ý meta, kiểm từng gợi ý: có test với provider giả
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-036-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1, A2).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-036 Meta title, description, slug"**, nhánh `team/T-036` (từ `main`).

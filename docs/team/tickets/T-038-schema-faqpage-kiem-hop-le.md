# T-038 · Schema: dựng và kiểm FAQPage không cần mạng

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 (nhóm 1: logic thuần, test giả) |
| Mức ưu tiên | Thấp–Trung bình |
| Phụ thuộc | Không. Chạy song song được với T-036, T-037 |
| Trạng thái | Chờ chỗ trống |

## Mục tiêu

Phần mềm dựng được dữ liệu cấu trúc (schema JSON-LD) loại **FAQPage** từ mục Hỏi đáp của bài, và kiểm nó hợp lệ mà không gọi công cụ trực tuyến. Kết quả dùng để xem trước ở bước SEO (T-041) và cho kiểm tra trước khi đăng (M7 mục 10).

**Chưa** đưa schema lên site: chờ chủ dự án quyết, theo cách "d" ở mục 3.3 của thiết kế.

## Bối cảnh

Thiết kế: `docs/team/reports/T-033-tho-may.md`.
- Mục 3 (3.1 → 3.4): site đã tự xuất Article, BreadcrumbList, LocalBusiness. Phần mềm **không** xuất các loại này.
- Mục 6: phiếu "T-037" trong báo cáo, nay là **T-038**.

## Phạm vi

- **Được sửa:**
  - mới: `seo_app/onpage/schema.py`, `tests/test_onpage_schema.py`;
  - mới: `seo_app/onpage/__init__.py`, nội dung y hệt dòng nêu ở T-036.
- **Không được sửa:** mọi file khác.

## Yêu cầu

1. Khuôn pydantic (`extra="forbid"`): `FAQPage`, `Question`, `Answer`. **AI không viết JSON.** Code dựng từ dữ liệu đã có: danh sách cặp câu hỏi/trả lời.
2. Kiểm (mục 3.4):
   - `@context` đúng `https://schema.org`;
   - `@type` trong danh sách cho phép; chặn `HowTo`;
   - loại site đã lo (Article, BreadcrumbList, LocalBusiness, Organization) thì từ chối dựng (danh sách là hằng số trong code);
   - `mainEntity` có ít nhất 1 câu; mỗi câu có `name` và `acceptedAnswer.text` không rỗng;
   - không thẻ HTML;
   - độ dài có giới hạn;
   - URL (nếu có) là `https://` và cùng tên miền với `WORDPRESS_URL` (truyền vào dạng tham số, không đọc `.env` trong hàm thuần).
3. **Khớp nội dung:** câu hỏi và trả lời phải có **nguyên văn** trong bài (sau chuẩn hóa NFC, khoảng trắng). Không khớp thì báo, không dựng.
4. Xuất chuỗi JSON: `json.dumps(..., ensure_ascii=False)`, rồi đổi `<`, `>`, `&` thành `<`, `>`, `&`. Như vậy chuỗi không bao giờ đóng được thẻ `</script>`.
5. Kết quả kiểm trả dạng **Chặn / Cảnh báo** kèm câu tiếng Việt, cùng kiểu với T-036 nếu tiện. Không phụ thuộc code T-036.
6. **Test:**
   - dữ liệu có `</script>`, `<img onerror>`, ký tự điều khiển;
   - câu hỏi không có trong bài;
   - loại bị cấm;
   - URL khác tên miền;
   - JSON xuất ra đọc lại được (`json.loads`) và vẫn đúng nội dung.

## Yêu cầu bảo mật riêng

W3 (không có đường đưa `<script>` vào nội dung bài), U1, D1 (không thư viện mới: chỉ `json` + `pydantic`), D3.

## Tiêu chí xong

- [ ] Dựng và kiểm FAQPage, có test
- [ ] Không thể đóng thẻ `</script>` bằng dữ liệu, có test
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-038-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (W3, U1).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-038 Schema FAQPage"**, nhánh `team/T-038` (từ `main`).

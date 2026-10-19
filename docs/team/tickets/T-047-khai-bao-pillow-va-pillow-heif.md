# T-047 · Khai báo Pillow và pillow-heif (G3-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Cao (mở đường cho Giai đoạn 3) |
| Phụ thuộc | Không |
| Trạng thái | Mới |

## Mục tiêu

Dự án khai báo trực tiếp `pillow` và `pillow-heif` (đọc ảnh HEIC của iPhone), đã quét lỗ hổng.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `pyproject.toml`, `uv.lock`, một test nhỏ xác nhận import được `pillow_heif` và mở được ảnh HEIC giả (nếu tạo được trong test).
- **Không được sửa:** `seo_app/**` (chưa dùng thư viện ở phiếu này), `app/**`.

## Yêu cầu

1. `uv add "pillow>=12.3" pillow-heif` (bản mới nhất ổn định). Ghi vào báo cáo: phiên bản, giấy phép, thư viện phụ kéo theo, bản libheif/libde265 đi kèm wheel Windows và Mac.
2. Chạy `uv export` + `uvx pip-audit` trên toàn bộ `uv.lock`, dán kết quả. Nếu Pillow có bản vá mới hơn 12.3 thì nâng.
3. `uv run pytest`, `uv run ruff check .` sạch trên Windows.

## Yêu cầu bảo mật riêng

D1 (thư viện mới: chủ dự án đã duyệt `pillow-heif` ngày 2026-10-19), góp ý Lá Chắn T-046 số 4.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-047-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Có (D1, `pip-audit`, bản libheif).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-047`, tạo từ `main`.

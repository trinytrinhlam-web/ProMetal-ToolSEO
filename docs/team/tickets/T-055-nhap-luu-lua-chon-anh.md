# T-055 · Nháp lưu lựa chọn ảnh (G3-9)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-052 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Bài đang soạn nhớ ảnh đã chọn cho từng chỗ cần ảnh (thật hoặc AI), alt đã duyệt, prompt ảnh AI; nháp cũ vẫn mở được.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/storage/drafts.py`, `tests/test_drafts_images.py`.
- **Không được sửa:** `app/**`, `seo_app/images/**`.

## Yêu cầu

1. Chỉ lưu (chỉ số gốc, đường dẫn tương đối), không lưu đường dẫn tuyệt đối (F1).
2. Đọc nháp: kiểm lại đường dẫn qua đúng hàm chặn của T-048; không tin chỉ số gốc vượt phạm vi (nháp có thể bị sửa tay) (góp ý Lá Chắn số 11).
3. Nháp cũ (chưa có phần ảnh) vẫn mở được; tăng `schema_version` đúng cách.

## Yêu cầu bảo mật riêng

F1, F3; góp ý Lá Chắn T-046 số 11.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-055-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (F1).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-055`, tạo từ `main`.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-048**: `ImageRef` đọc từ nháp phải tạo lại bằng `ImageRef(...)` rồi đi qua `ImageLibrary.stat_image`/`read_image_bytes`, không tin số thứ tự gốc lưu trong nháp (góp ý Lá Chắn T-046 số 11); khóa lựa chọn theo `ImageRef` của kết quả quét.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-052** (điều kiện 3): thẻ hay nguồn ảnh lưu trong nháp là dữ liệu chưa tin cậy; khi mở nháp dựng lại qua `ImageTags(...)`; nguồn ảnh theo hướng an toàn: là ảnh AI nếu nháp ghi AI **hoặc** `resolve` hiện tại nói AI; nháp không bao giờ kéo ảnh AI về "ảnh thật".

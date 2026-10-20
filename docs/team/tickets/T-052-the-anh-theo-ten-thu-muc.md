# T-052 · Thẻ ảnh đọc từ tên thư mục (G3-6)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-048 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

App đọc thẻ ảnh (mã công trình, hạng mục, khu vực, trước/sau, nguồn thật/AI) từ tên thư mục Drive theo quyết định 3A; thẻ sửa tay lưu cache trên máy.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, `tests/test_images_tags.py`.
- **Không được sửa:** `seo_app/images/__init__.py`, `seo_app/images/folders.py`, `app/**`.

## Yêu cầu

1. Theo 3A: app **không ghi** gì vào thư mục ảnh/Drive.
2. Khu vực chỉ nhận khi khớp **danh sách quận/huyện cố định**; mã công trình chỉ nhận mẫu cố định (ví dụ `CT\d+`); không khớp thì để trống (góp ý Lá Chắn số 3). Tên thư mục có thể chứa tên/địa chỉ khách: không đưa phần không khớp vào prompt AI, tên file, tiêu đề, caption.
3. Cache SQLite cục bộ trong `data/` (đã `.gitignore`), xóa đi vẫn tạo lại được; đọc an toàn (không `pickle`/`eval`).
4. Ảnh AI luôn mang `nguon = AI`, không gắn thẻ công trình thật.

## Yêu cầu bảo mật riêng

F1, F3, A3; góp ý Lá Chắn T-046 số 3 (số 10 không áp dụng vì chọn 3A).

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-052-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (F1, A3).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-052`, tạo từ `main`.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-048** (`docs/team/reports/T-048-la-chan.md`, LC-T048-4 mục a): tên thư mục và tên file từ `seo_app/images/folders.py` là dữ liệu chưa tin cậy; `_is_safe_name` còn cho qua ký tự vô hình/ngắt dòng (U+2028, U+2029, U+200B, U+200F, U+061C, U+FEFF, U+FFF9, khối ký tự thẻ U+E0000–E007F). Thẻ chỉ nhận khi khớp danh sách cố định (góp ý Lá Chắn T-046 số 3); bỏ ký tự Cf, Zl, Zp trước khi so.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-050** (điều kiện 5): chỉ đưa vào thẻ phần tên thư mục **bên dưới** thư mục ảnh đã khai báo (không `Users/…`, `My Drive/…`); khu vực đối chiếu danh sách quận/huyện cố định. Lớp lọc của T-050 cho qua thẻ có một dấu `/` (SL-T050-4), nên không thay được việc này.

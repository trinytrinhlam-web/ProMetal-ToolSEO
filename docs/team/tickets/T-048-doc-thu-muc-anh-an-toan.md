# T-048 · Đọc thư mục ảnh an toàn (G3-2)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không (không cần Pillow) |
| Trạng thái | Mới |

## Mục tiêu

App liệt kê ảnh trong các thư mục khai báo ở `IMAGE_FOLDERS`, không bao giờ đọc ra ngoài các thư mục đó, không treo khi thư mục lớn hay ổ Drive chậm.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/images/__init__.py` (chỉ phiếu này tạo), `seo_app/images/folders.py`, `tests/test_images_folders.py`.
- **Không được sửa:** `app/**`, `config/**`, `tests/conftest.py`.

## Yêu cầu

1. Mỗi ảnh được nhận diện bằng (chỉ số thư mục gốc, đường dẫn tương đối); không lưu, không hiện đường dẫn tuyệt đối.
2. Chặn `..`, đường dẫn tuyệt đối lạ, ổ đĩa, UNC, symlink và **junction Windows** trỏ ra ngoài (`resolve()` rồi `is_relative_to(gốc)`; `os.scandir` coi junction là thư mục thường, phải kiểm thêm `is_junction()`).
3. Danh sách đuôi được nhận (JPEG, PNG, WebP, HEIC/HEIF, AVIF theo báo cáo T-046); giới hạn dung lượng file.
4. Quét có ngân sách (số mục, thời gian), phân trang; báo "còn nữa" thay vì treo.
5. Tên thư mục là dữ liệu chưa tin cậy (góp ý Lá Chắn số 3): phiếu này chỉ trả tên, không diễn giải thẻ (để T-052).
6. Test junction chạy trên Windows, symlink trên Mac/Linux (`skipif` đúng hệ điều hành, không bỏ qua kiểm tra bảo mật).

## Yêu cầu bảo mật riêng

F1, F3, U2; góp ý Lá Chắn T-046 số 3, 9.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-048-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (đường dẫn Windows/Mac, junction, thư mục rất lớn). Lá Chắn: Có (F1).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-048`, tạo từ `main`.

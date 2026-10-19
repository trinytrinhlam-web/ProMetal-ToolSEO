# T-049 · Xử lý ảnh: xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch (G3-3)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Cao |
| Phụ thuộc | T-047 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Ảnh thật được xoay đúng chiều, thu cạnh dài 1600 px, nén WebP, **còn nguyên GPS**; bản gửi AI không còn chút metadata nào; tên file chuẩn SEO.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/images/process.py`, `seo_app/images/naming.py`, `tests/test_images_process.py`.
- **Không được sửa:** `seo_app/images/__init__.py`, `seo_app/images/folders.py`, `app/**`, `config/**`.

## Yêu cầu

1. Mở ảnh an toàn: giới hạn số điểm ảnh (chống bom giải nén) áp dụng cả cho HEIC; chỉ nhận định dạng cho phép (Pillow nhận theo nội dung, không theo đuôi); không ghi `"MPO"` vào `formats=` (gây `KeyError`).
2. `exif_transpose` → đặt Orientation = 1 → thu cạnh dài 1600 → lưu WebP kèm `exif=` đã lọc theo quyết định 2A (giữ GPS, ngày chụp, hãng, đời máy; bỏ số seri, `CameraOwnerName`, MakerNote, ảnh nhỏ IFD1).
3. Kiểm GPS **sau nén**: so giá trị GPS với ảnh gốc, không chỉ xem có thẻ GPS (góp ý Lá Chắn số 2).
4. Bản gửi AI (khoảng 1024 px): dựng lại từ điểm ảnh, không còn APP1/COM/XMP, chunk `tEXt/iTXt` (góp ý Lá Chắn số 1). Test bằng ảnh gốc có đủ EXIF + GPS + XMP + COM, và PNG có chunk chữ.
5. Ảnh xem trước dùng trong máy: bỏ EXIF; thư mục cache nằm trong `.gitignore` (kiểm trong code).
6. Đặt tên file không dấu theo nội dung (dùng `slugify` có sẵn), tránh trùng tên; không lấy tên khách từ tên thư mục làm tên file (góp ý số 3).
7. Ảnh chụp màn hình không có EXIF vẫn xử lý bình thường.

## Yêu cầu bảo mật riêng

F2 (test bắt buộc: còn GPS sau nén, bản AI không còn metadata), F3, A3; góp ý Lá Chắn T-046 số 1, 2, 3, 9.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-049-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (F2, F3, A3).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-049`, tạo từ `main`.
- 2026-10-19 (Chỉ Huy A): **Lưu ý của Soi Lỗi T-047** (`docs/team/reports/T-047-soi-loi.md`):
  1. HEIC cắt cụt vẫn mở được bằng `Image.open`; lỗi chỉ nổ ở `load()` và là `ValueError`, không phải `OSError`. Đặt cả `open` lẫn `load` trong khối bắt lỗi, bắt `(OSError, ValueError)`.
  2. HEIC hỏng ở giữa dữ liệu vẫn giải mã ra ảnh rác mà không báo lỗi: chỉ ghi nhận, giao diện cho người dùng xem trước.
  3. Đăng ký HEIF (`register_heif_opener`) một lần ở một chỗ cố định. Test "chưa đăng ký" trong `tests/test_pillow_heif_setup.py` đang `pytest.skip` khi HEIF đã đăng ký sẵn: nếu phiếu này đăng ký lúc import thì báo Soi Lỗi đổi test đó thành fixture tự gỡ HEIF khỏi bảng (phiếu này không sửa test của T-047).

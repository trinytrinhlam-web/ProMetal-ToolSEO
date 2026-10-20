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
- 2026-10-19 (Chỉ Huy A): **Điều kiện bắt buộc của Lá Chắn T-047** (`docs/team/reports/T-047-la-chan.md`). Phiếu này **phụ thuộc thêm T-058** (nâng Pillow 13 hoặc chủ dự án chấp nhận rủi ro); thiếu T-058 thì Lá Chắn kết luận KHÔNG ĐẠT (Cao).
  1. Bắt lỗi quanh cả `open` lẫn `load`, gồm `(OSError, ValueError, Image.DecompressionBombError)` (`DecompressionBombError` **không** phải con của `OSError`).
  2. Kiểm dung lượng file trước khi mở; đặt `MAX_IMAGE_PIXELS` rõ ràng và biến `DecompressionBombWarning` thành lỗi (Pillow chỉ báo lỗi khi vượt gấp đôi giới hạn; giới hạn có áp cho HEIC).
  3. `register_heif_opener()` một lần ở chỗ cố định (tắt thumbnails, depth, aux); không gọi `load_libheif_plugin`, không bật `DISABLE_SECURITY_LIMITS`, không ghi file HEIC.
  4. Luôn mở với `formats=["JPEG","PNG","WEBP","HEIF"]` (thêm AVIF nếu cần, ghi lý do).
  5. Nếu vẫn dùng Pillow 12.x (T-058 chọn B): không `thumbnail()`/`draft()`, không `seek()`, không ghi JPEG.
  6. Báo Soi Lỗi thay `pytest.skip` trong test "chưa đăng ký" của T-047 bằng fixture tự gỡ HEIF.
- 2026-10-20 (Chỉ Huy A): theo Thợ Máy T-058, Pillow 13.0.0 còn 1 khuyến cáo chưa vá (GHSA-654x-cwwv-5j9c, lộ vùng nhớ khi xuất ảnh sang Arrow, chỉ xảy ra khi đặt `PILLOW_ALIGNMENT` > 1). Phiếu này: **không** xuất ảnh sang Arrow, **không** đặt `PILLOW_ALIGNMENT`. Nếu T-058 đã gộp thì điều kiện 5 (tránh `thumbnail()`/`draft()`…) không còn bắt buộc.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-048**: kiểm nội dung bằng Pillow `formats=…`, không tin đuôi file; thư mục cache ảnh xem trước phải nằm trong `.gitignore` (góp ý Lá Chắn T-046 số 9). Đọc ảnh qua `ImageLibrary.read_image_bytes` (`seo_app/images/folders.py`).
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-058** (`docs/team/reports/T-058-la-chan.md`, mục "Điều kiện" 2), áp khi T-058 đã gộp (Pillow 13.0.0):
  - Điều kiện 5 của T-047 (tránh `thumbnail()`/`draft()`, `seek()`, ghi JPEG) **không còn bắt buộc**; vẫn chỉ xử lý khung đầu của ảnh MPO.
  - Điều kiện 1–4, 6, 7 của T-047 **giữ nguyên**: bắt `(OSError, ValueError, Image.DecompressionBombError)` quanh cả `open` lẫn `load`; kiểm dung lượng trước khi mở, đặt `MAX_IMAGE_PIXELS`, đổi `DecompressionBombWarning` thành lỗi; đăng ký HEIF một chỗ; luôn mở với `formats=["JPEG","PNG","WEBP","HEIF"]`.
  - LC-T058-1: không xuất ảnh sang Arrow (`__arrow_c_array__`, `__arrow_c_schema__`, `Image.fromarrow`, `pyarrow`), không đặt/đọc `PILLOW_ALIGNMENT`.
  - LC-T058-2: chỉ đưa vào `st.image` ảnh Pillow đã mở qua hàm mở an toàn của module ảnh, hoặc byte WebP/JPEG do app tạo; **không bao giờ** đưa đường dẫn hay byte gốc của file trong `IMAGE_FOLDERS`. Có test. Áp cả cho phiếu giao diện xem trước ảnh (T-056).
  - LC-T058-3: module ảnh từ chối xử lý khi Pillow < 13 (một dòng kiểm phiên bản, câu lỗi tiếng Việt cố định, có test).
  - SL-T058-1: ảnh 16 bit đưa vào `st.image` phải đổi về 8 bit hoặc `output_format="PNG"`.

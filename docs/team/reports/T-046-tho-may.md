# Báo cáo T-046 · Thiết kế Giai đoạn 3 (ảnh): tìm hiểu kỹ thuật, chia phiếu

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-046](../tickets/T-046-thiet-ke-giai-doan-3.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | **Bản dở, đang viết** (đẩy sớm để không mất việc) |

Đang làm: đọc code, thử Pillow (EXIF/GPS → WebP, HEIC) trong thư mục tạm ngoài repo. Các mục 1–8 sẽ được bổ sung dần.

## Kết quả thử Pillow (đã chạy, 2026-10-17)

Môi trường: Windows 11, Python 3.12.15, **Pillow 13.0.0**, thư mục tạm ngoài repo. Ảnh và GPS đều giả (tạo bằng Pillow). Lệnh:
`PYTHONIOENCODING=utf-8 uv run --no-project --with pillow python exif_gps_test.py` và `... bomb_heic_test.py`.

| # | Thử | Kết quả |
|---|---|---|
| 1 | JPEG giả 4000×3000, Orientation=6, GPS N 16.0544 / E 108.2022, Make/Model/số seri giả | Đọc lại đủ |
| 2 | Nén WebP **không** truyền `exif=` | **Mất hết EXIF, mất GPS** |
| 3 | `exif_transpose` → đặt Orientation=1 → thu cạnh dài 1600 → WebP q80 kèm `exif=` | **GPS giữ nguyên** (N 16.0544, E 108.2022), Orientation=1, ảnh 1200×1600 xoay đúng |
| 4 | Như 3 nhưng bỏ Make/Model/Software/số seri | GPS và ngày chụp còn, thông tin máy hết |
| 5 | Bản gửi AI: cạnh dài 1024, JPEG, bỏ `exif`/`xmp` | Không còn chuỗi `Exif` trong file, không GPS |
| 6 | Ảnh chụp màn hình PNG không EXIF → WebP | Không lỗi, file không có EXIF |
| 7 | Bom giải nén (hạ ngưỡng thử) | > 1 lần ngưỡng: cảnh báo; > 2 lần: `DecompressionBombError` ngay lúc mở, chưa giải nén. Biến cảnh báo thành lỗi được |
| 8 | File BMP / file chữ đổi đuôi `.jpg`, mở với `formats=["JPEG","PNG","WEBP"]` | `UnidentifiedImageError` (Pillow nhận dạng theo nội dung) |
| 9 | File `.heic` (đầu file `ftypheic`) | Pillow **không đọc được** (`UnidentifiedImageError`); `.heic` không có trong danh sách đuôi của Pillow 13 |
| 10 | AVIF | Pillow 13 đọc/ghi được (có sẵn) |
| 11 | JPEG nhiều khung (MPO, iPhone hay tạo) | Mở được qua bộ mở JPEG, `im.format = "MPO"`. Lưu ý: ghi `"MPO"` vào `formats=` là lỗi `KeyError` |
| 12 | JPEG bị cụt | `load()` báo `OSError` |

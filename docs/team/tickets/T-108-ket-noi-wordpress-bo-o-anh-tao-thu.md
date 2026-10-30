# T-108 · Trang Kết nối WordPress: bỏ ô chọn ảnh ở mục «Tạo thử một bài nháp» (LC-T093-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`), cùng nhánh với T-106 (cùng `app/views/wordpress.py`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-30 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (chặn đóng Giai đoạn 3) |
| Phụ thuộc | Không |
| Trạng thái | Xong (gộp `main` 2026-10-30) |

## Mục tiêu

Trang Kết nối WordPress không còn đường tải nguyên file ảnh người dùng chọn lên thư viện Media công khai (bỏ qua bước làm sạch ảnh, quyết định 2A).

## Bối cảnh

- Lá Chắn T-093 (`docs/team/reports/T-093-la-chan.md`, mục 3), **LC-T093-1 (Trung bình)**, phần còn lại của T-001 #3: mục «Tạo thử một bài nháp» (`app/views/wordpress.py:124-135`) gửi `upload_media(image.getvalue(), image.name)`: nguyên byte file, không qua `make_web_image`. Số seri máy, tên chủ máy, MakerNote, XMP, IPTC, ảnh nhỏ IFD1 (có thể là ảnh **trước khi** cắt, che) lên Media công khai ngay; tên file gốc thành tên trên website; chỉ xét đuôi file; README (`:115-117`) dặn «tạo thử một bài nháp có ảnh đại diện».
- Gợi ý của Lá Chắn: **bỏ ô chọn ảnh ở mục tạo thử**, sửa README `:115`; gỡ `xfail` LC-T093-1.
- Test `xfail(strict=True)` trong `tests/test_la_chan_t093.py` (nhánh `team/T-093`, sẽ vào `main` khi T-093 gộp).

## Phạm vi

- **Được sửa:** `app/views/wordpress.py`, `README.md` (đúng đoạn tạo thử), test giao diện; gỡ `xfail` LC-T093-1 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** `seo_app/**`, `config/**`.

## Yêu cầu

1. Bỏ ô chọn ảnh và lệnh tải ảnh ở mục «Tạo thử một bài nháp»; nút tạo thử vẫn tạo được một bài nháp chữ thuần để kiểm kết nối.
2. README đoạn tạo thử nói đúng: tạo thử bài nháp không ảnh; muốn thử ảnh thì dùng «Soạn bài» (ảnh đã qua bước làm sạch).
3. Không lùi các test trang Kết nối, `T-001`, `T-087` cũ (grep test ghim câu, nút cũ; đổi test cũ cần Chỉ Huy duyệt R5).
4. Làm cùng T-106 trên một nhánh (`team/T-106`), một báo cáo `docs/team/reports/T-106-hoa-si.md` có hai mục.

## Yêu cầu bảo mật riêng

W2, F1, U1.

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W2, F1, U1), chung một lượt với T-106.

## Ghi chú của Chỉ Huy

- Lập 2026-10-30 theo đề xuất Lá Chắn T-093 (việc 2 để đóng Giai đoạn 3) và chỉ đạo «vấn đề nào có đề xuất thì làm theo đề xuất».
- 2026-10-30 12:52 (Chỉ Huy B): LC-T093-1 đóng (Soi Lỗi, Lá Chắn xác nhận). Gộp `main` cùng T-106, Windows 20.877 test qua, 0 hỏng.

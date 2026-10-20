# T-069 · README: ảnh gửi hãng AI khi viết alt, cách đặt thư mục ảnh

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (trước khi gộp T-056) |
| Phụ thuộc | T-062 đã gộp; nên sau T-052 |
| Trạng thái | Mới |

## Mục tiêu

Chủ dự án đọc README biết: việc viết alt gửi ảnh công trình cho hãng AI, nên dùng khóa nào; và cách đặt thư mục ảnh (công trình thật, ảnh AI) để app đọc đúng thẻ.

## Bối cảnh

- Lá Chắn T-050 (`docs/team/reports/T-050-la-chan.md`, LC-T050-4) và Lá Chắn T-062 (điều kiện 3): khóa Gemini **miễn phí** cho Google dùng nội dung gửi lên để cải tiến sản phẩm và người duyệt có thể xem.
- Câu đề xuất của Thợ Máy T-062 (`docs/team/reports/T-062-tho-may.md`, mục Đề xuất).
- Soi Lỗi T-052 (`docs/team/reports/T-052-soi-loi.md`, Đề xuất): ghi cách đặt thư mục ảnh AI và thư mục giai đoạn (trước/sau). Quyết định 3A trong `CLAUDE.md`.

## Phạm vi

- **Được sửa:** `README.md`.
- **Không được sửa:** code, `config/**`, test.

## Yêu cầu

1. Mục cấu hình AI của README thêm một đoạn ngắn: việc viết alt gửi ảnh công trình (đã bỏ GPS, EXIF) cho hãng AI ghi ở `[tasks.alt]`; nên dùng Claude (mặc định) hoặc khóa **trả phí** của OpenAI / Gemini; khóa Gemini miễn phí cho Google dùng ảnh để cải tiến sản phẩm và người duyệt có thể xem; muốn dùng khóa miễn phí cho alt thì báo Chỉ Huy để ghi sổ rủi ro.
2. Một mục ngắn "Đặt thư mục ảnh": ví dụ `CT012 - Cổng inox - Tân Phú/truoc`, chỗ đặt ảnh AI, app không ghi gì vào thư mục ảnh, thẻ sửa tay chỉ nhớ trên máy đang dùng. Lấy đúng theo code T-052 (nếu T-052 chưa gộp thì làm phần 1 trước, phần 2 sau khi gộp).
3. Viết tiếng Việt, ngắn, cho người ít dùng dòng lệnh.

## Yêu cầu bảo mật riêng

Không có (soát bí mật như mọi phiếu tài liệu).

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên
- [ ] `uv run pytest tests/test_readme*.py` (nếu có) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-069-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Không (chỉ tài liệu). Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 3 của Lá Chắn T-062 (LC-T050-4) và đề xuất của Soi Lỗi T-052.

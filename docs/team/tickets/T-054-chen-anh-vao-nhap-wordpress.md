# T-054 · WordPress: tải ảnh và chèn `<figure>` vào nháp (G3-8)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-049 và **T-042** đã gộp (cùng sửa `seo_app/wordpress/client.py`) |
| Trạng thái | Mới |

## Mục tiêu

Khi người dùng bấm Gửi nháp, app tải ảnh 1600 px (còn GPS) lên thư viện, đặt alt/caption, ảnh đại diện, chèn `<figure>` vào nội dung nháp.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py`, `seo_app/sanitize.py` (chỉ phần mở `class`), `seo_app/images/html.py`, `tests/test_wordpress_images.py`.
- **Không được sửa:** `app/**`, `config/**`.

## Yêu cầu

1. Chỉ tải ảnh khi người dùng bấm Gửi nháp (ảnh xem được công khai ngay khi tải lên). Lỗi giữa chừng: liệt kê media đã tải, **không xóa** (W2) (góp ý Lá Chắn số 8).
2. Test bytes gửi lên còn GPS (theo 5A dùng file đầy đủ 1600 px làm ảnh chính).
3. Nếu mở `class`: chỉ trên `img`/`figure`, mỗi lớp khớp **toàn bộ** `wp-image-\d+` hoặc `wp-block-image`, bỏ lớp lạ; `<figure>` dựng bằng code, alt/caption đã escape, vẫn qua `sanitize_html` lần cuối (góp ý Lá Chắn số 7).
4. Chỉ ghi vào bài nháp do app tạo (`_own_draft` của T-042), đi qua danh sách đường REST cố định của T-042.

## Yêu cầu bảo mật riêng

W1–W4, `security.md` 2.3 (Lá Chắn soát riêng thay đổi ở `sanitize.py`), F2.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-054-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (W1–W4, 2.3).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-054`, tạo từ `main`.

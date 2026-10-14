# T-001 · Kiểm định bảo mật toàn bộ code hiện có

| Mục | Nội dung |
|---|---|
| Giao cho | Lá Chắn (`la-chan`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 0, 1 và Giai đoạn 2 phần 1 |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không |
| Trạng thái | Đã giao |

## Mục tiêu

Có một biên bản bảo mật làm "mốc gốc" cho toàn bộ code đang có trên `main`, để các phiếu sau chỉ cần soát phần thay đổi.

## Bối cảnh

- Code hiện có: đăng nhập (`seo_app/auth.py`), cấu hình (`seo_app/config.py`), client WordPress (`seo_app/wordpress/`), lớp AI và quy trình viết bài vừa đưa lên (`seo_app/ai/`, `seo_app/content/`, `config/ai.toml`, `config/content.toml`), giao diện (`app/`), script (`scripts/`, `run.*`, `set_password.*`), hook (`.claude/`).
- Giai đoạn 2 phần 1 có bước nghiên cứu **tìm web**: nội dung trang ngoài đi vào prompt. Soi kỹ prompt injection.
- Website không có bản thử nghiệm; mọi thứ gửi lên WordPress là thật.

## Phạm vi

- **Được sửa:** chỉ tạo `docs/team/reports/T-001-la-chan.md`.
- **Không được sửa:** mọi file khác.

## Yêu cầu

1. Kiểm định toàn repo tại commit mới nhất của `main` theo `docs/team/security.md` mục 3, đủ 19 dòng danh sách kiểm tra.
2. Soát lịch sử git tìm bí mật.
3. Chạy các công cụ ở mục 5 (nếu môi trường cho phép).
4. Lập danh sách lỗi theo mức độ, mỗi lỗi có `file:dòng`, đường đi thật, cách sửa đề xuất.

## Yêu cầu bảo mật riêng

Toàn bộ danh sách kiểm tra. Ưu tiên: S1, S2, W1, W3, A1, A2, U1.

## Tiêu chí xong

- [ ] Biên bản tại `docs/team/reports/T-001-la-chan.md` theo mẫu `templates/security-review.md`
- [ ] Có kết luận ĐẠT / ĐẠT CÓ ĐIỀU KIỆN / KHÔNG ĐẠT
- [ ] Mỗi lỗi có đề xuất sửa để Chỉ Huy lập phiếu

## Kiểm thử và kiểm định

- Soi Lỗi: Không (chạy song song ở T-002)
- Lá Chắn: đây chính là phiếu kiểm định

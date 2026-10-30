# T-105 · `set_password`: câu báo đúng nguyên nhân khi đọc lại lỗi, cảnh báo khi biến môi trường đè `.env` (SL-T104-1, SL-T104-2)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-29 |
| Giai đoạn | Giai đoạn 0 (đăng nhập app) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-104 đã gộp (cùng `scripts/hash_password.py`, `seo_app/env_file.py`) |
| Trạng thái | Chờ (giao khi máy rảnh) |

## Mục tiêu

Người đặt mật khẩu app luôn nhận câu báo đúng sự thật: không báo «dòng sai định dạng» khi thật ra file đang bị chương trình khác giữ, và không báo «Đã lưu» khi mật khẩu mới sẽ không có hiệu lực vì biến môi trường đè `.env`.

## Bối cảnh

- Soi Lỗi T-104 (`docs/team/reports/T-104-soi-loi.md`), Lá Chắn T-104 (`docs/team/reports/T-104-la-chan.md`) giữ mức Thấp, đề xuất «sửa ở một phiếu nhỏ sau, không chặn»:
  - **SL-T104-1:** đọc lại `.env` ngay sau khi thay mà lỗi (chương trình khác giữ file đúng lúc đó) thì câu báo nói «dòng sai định dạng». File vẫn an toàn (bộ ghi trả bản cũ rồi mới báo); chỉ sai nguyên nhân.
  - **SL-T104-2 (có từ trước, U3):** biến môi trường `APP_PASSWORD_HASH` đè giá trị trong `.env`; `set_password` vẫn báo «Đã lưu» nhưng mật khẩu mới không có hiệu lực, mật khẩu cũ vẫn vào được.
- Mỗi lỗi có `xfail(strict=True)` trong `tests/test_soi_loi_t104.py`.

## Phạm vi

- **Được sửa:** `scripts/hash_password.py`, `seo_app/env_file.py` (phần câu báo, kiểm biến môi trường), test; gỡ `xfail` SL-T104-1, -2 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** cách băm, so mật khẩu, `seo_app/config.py`, `app/**`.

## Yêu cầu

1. SL-T104-1: phân biệt «không đọc lại được file» với «dòng sai định dạng»; câu tiếng Việt cố định, đúng nguyên nhân, không đường dẫn, không traceback.
2. SL-T104-2: khi biến môi trường `APP_PASSWORD_HASH` đang đặt, vẫn lưu vào `.env` nhưng báo rõ mật khẩu mới chưa có hiệu lực cho tới khi bỏ biến đó (câu dễ hiểu cho người không rành kỹ thuật), hoặc từ chối kèm lý do; không in giá trị biến.
3. Test cho cả hai; test T-090, T-104 cũ vẫn qua.

## Yêu cầu bảo mật riêng

U3, F3.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-105-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (U3, F3).

## Ghi chú của Chỉ Huy

- Lập 2026-10-29 theo đề xuất Soi Lỗi, Lá Chắn T-104 và chỉ đạo «vấn đề nào có đề xuất thì làm theo đề xuất».

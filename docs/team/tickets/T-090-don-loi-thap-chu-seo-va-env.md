# T-090 · Dọn lỗi Thấp: câu báo emoji mới trong chữ SEO (SL-T041-8), `.env` không phải UTF-8 (SL-T084-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-041, T-084 đã gộp |
| Trạng thái | Chờ (giao khi máy rảnh) |

## Mục tiêu

Hai lỗi nhỏ còn để lại: emoji rất mới trong tiêu đề, mô tả SEO bị chặn với câu báo sai nghĩa («ký tự lạ không nhìn thấy»); `.env` lưu bằng bảng mã khác UTF-8 (Notepad «ANSI») làm app không mở được trang nào và hiện traceback tiếng Anh có đường dẫn cài đặt.

## Bối cảnh

- **SL-T041-8** (`docs/team/reports/T-041-soi-loi.md`, quyết định của Lá Chắn trong `docs/team/reports/T-041-la-chan.md`): **giữ Chặn** (cho qua thì emoji bị lặng lẽ xóa khi ghi website); chỉ sửa câu báo kiểu «phần mềm chưa nhận ra ký tự này (có thể là biểu tượng mới), xóa hoặc thay bằng chữ thường». Test `xfail` SL-T041-8 của Soi Lỗi đang đòi hướng ngược lại (không chặn): **Chỉ Huy duyệt** đổi test đó theo quyết định giữ Chặn (ghi rõ trong báo cáo, R5).
- **SL-T084-1** (`docs/team/reports/T-084-soi-loi.md`, `T-084-la-chan.md`): `.env` không phải UTF-8 thì app không mở trang, traceback tiếng Anh có đường dẫn cài đặt (có thể có tên tài khoản Windows). Cần câu báo tiếng Việt cố định (gợi ý lưu lại `.env` dạng UTF-8), không lộ đường dẫn, không lộ nội dung `.env`. `client.showErrorDetails` là cấu hình Streamlit, **không** làm ở phiếu này (cần chủ dự án duyệt).

## Phạm vi

- **Được sửa:** `seo_app/onpage/meta.py` (câu báo), `seo_app/config.py` (đọc `.env`), test; đổi test `xfail` SL-T041-8 theo ghi chú trên; gỡ `xfail` SL-T084-1 khi XPASS.
- **Không được sửa:** `seo_app/wordpress/**` (T-059 đang sửa), `app/**` trừ khi câu báo cần hiện ở trang (báo Chỉ Huy trước), `.streamlit/config.toml`.

## Yêu cầu

1. SL-T041-8: giữ Chặn, câu báo đúng nghĩa, phân biệt với ký tự điều khiển/vô hình.
2. SL-T084-1: `.env` sai bảng mã ra câu tiếng Việt cố định, app vẫn mở trang đăng nhập hay trang báo lỗi rõ ràng; không traceback, không đường dẫn.
3. Test cho cả hai; test cũ liên quan (T-036, T-040, T-041 meta; cấu hình) vẫn qua.

## Yêu cầu bảo mật riêng

U1, U2, S1.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan + `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-090-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (U1, U2, S1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo «cứ làm liên tục, không cần hỏi».

# T-020 · Nhập khóa API AI ngay trong app

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`): phần ghi `.env`. Họa Sĩ (`hoa-si`): giao diện |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (chủ dự án yêu cầu 2026-10-14) |
| Phụ thuộc | Không |
| Trạng thái | Xong (2026-10-14) |

## Mục tiêu

Chủ dự án muốn tự nhập khóa API của Gemini, ChatGPT (OpenAI) và Claude (Anthropic) trong app, không phải mở file `.env` bằng tay. Khóa vẫn chỉ nằm trong `.env` (quyết định đã chốt), app chỉ là chỗ ghi vào đó.

## Yêu cầu

### Thợ Máy: `seo_app/env_file.py` (mới)

1. Hàm ghi/xóa một biến trong `.env`, mặc định `seo_app.config.DEFAULT_ENV_FILE` (tra lúc gọi, như `load_settings`). Chỉ nhận đúng danh sách cho phép: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`.
2. Giữ nguyên mọi dòng khác, chú thích và thứ tự trong `.env`. Chưa có file thì tạo mới. Có biến rồi thì thay đúng dòng đó; xóa thì để trống giá trị.
3. Chặn giá trị nguy hiểm: xuống dòng (`\n`, `\r`), ký tự điều khiển, dấu nháy, `#`, khoảng trắng ở giữa, dài bất thường (quá 512 ký tự). Bỏ khoảng trắng hai đầu. Mục đích: không ai chèn được biến khác (ví dụ `APP_PASSWORD_HASH`) qua ô nhập.
4. Ghi an toàn: ghi file tạm cùng thư mục rồi thay thế (`os.replace`), `encoding="utf-8"`. Trên Mac/Linux đặt quyền `600`; trên Windows bỏ qua bước đó, không lỗi.
5. Kiểm tra khóa Claude: hàm gọi thử Anthropic (danh sách mô hình, rẻ nhất) có timeout, trả về đúng/sai và thông báo dễ hiểu đã qua `redact_secrets`. OpenAI và Gemini chưa kiểm tra được (chờ chủ dự án duyệt thư viện ở T-018): trả về "chưa hỗ trợ kiểm tra".
6. Test dùng file tạm, không bao giờ đọc hay ghi `.env` thật, không gọi mạng thật.

### Họa Sĩ: tab "🔌 Kết nối" trong `app/views/settings.py` (làm sau phần của Thợ Máy)

1. Ba ô nhập khóa (Claude, ChatGPT, Gemini), `type="password"`, kèm link lấy khóa như trong `.env.example`.
2. **Không bao giờ hiện lại khóa** đã lưu, kể cả vài ký tự cuối. Chỉ hiện "đã khai báo / chưa khai báo".
3. Nút Lưu, nút Xóa khóa (hỏi lại một lần), nút Kiểm tra (chỉ Claude lúc này).
4. Lưu xong thì xóa giá trị khỏi ô nhập và `session_state`, tải lại cấu hình để trạng thái đổi ngay.
5. Nếu biến cũng được đặt trong biến môi trường hệ điều hành (được ưu tiên hơn `.env`), báo cho người dùng biết khóa vừa nhập sẽ không có hiệu lực.
6. Giữ bố cục đã duyệt; trang vẫn qua `tests/test_app_pages.py`.

## Tiêu chí xong

- [ ] Test đủ các trường hợp ở mục 1–6 của Thợ Máy và test giao diện không hiện lại khóa
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-020-tho-may.md` và `docs/team/reports/T-020-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có (đụng tới bí mật: kiểm S1, S2, F1, F3)

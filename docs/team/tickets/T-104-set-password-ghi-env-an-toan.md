# T-104 · `set_password` ghi `.env` an toàn: thay đúng dòng app đọc, ghi nguyên tử (LC-T090-1, LC-T090-2)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-28 |
| Giai đoạn | Giai đoạn 0 (đăng nhập app) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-090 đã gộp (cùng `scripts/hash_password.py`) |
| Trạng thái | Xong (gộp `main` 2026-10-30) |

## Mục tiêu

Đặt mật khẩu app bằng `set_password` luôn có hiệu lực đúng như app đọc `.env`, và không bao giờ làm `.env` rỗng hay mất dòng khác khi ghi lỗi giữa chừng.

## Bối cảnh

- Lá Chắn T-090 (`docs/team/reports/T-090-la-chan.md`), 2 lỗi Thấp **có từ trước** (T-090 không gây ra), đề xuất gộp một phiếu:
  - **LC-T090-1:** `set_env_value` trong `scripts/hash_password.py` thay dòng **đầu** `APP_PASSWORD_HASH=` rồi dừng, còn python-dotenv lấy dòng **cuối** khi biến lặp lại. `str.splitlines()` còn cắt ở FF, VT, FS/GS/RS, NEL, U+2028, U+2029, trong khi python-dotenv chỉ coi CR, LF là xuống dòng. Hệ quả: mật khẩu mới có thể không có hiệu lực.
  - **LC-T090-2:** `Path.write_text` mở kiểu `"w"`, nên file bị cắt về 0 byte **trước** khi ghi. Lỗi ghi giữa chừng làm `.env` rỗng, mà câu báo mới (T-090 lượt 2) lại dặn «chạy lại set_password».
- Lá Chắn gợi ý: `set_password` ghi bằng bộ ghi của `seo_app/env_file.py`, bỏ BOM trước khi tách dòng, thay đúng dòng có hiệu lực.
- Mục 6 sổ rủi ro chỉ ghi rủi ro chủ dự án đã chấp nhận, nên hai lỗi này được theo dõi bằng phiếu này cho tới khi sửa.

## Phạm vi

- **Được sửa:** `scripts/hash_password.py`, `seo_app/env_file.py` (nếu cần thêm hàm ghi), test; gỡ `xfail` LC-T090-1, -2 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** cách băm, so mật khẩu (PBKDF2, so sánh an toàn), `seo_app/config.py`, `app/**`, `.env.example`.

## Yêu cầu

1. Tách dòng đúng như python-dotenv (chỉ CR, LF); bỏ BOM đầu file trước khi tách; thay **mọi** dòng `APP_PASSWORD_HASH=` / `export APP_PASSWORD_HASH=`, hoặc chỉ giữ một dòng (dòng app sẽ đọc) và bỏ dòng thừa; giữ nguyên mọi dòng khác (kể cả ký tự lạ trong giá trị).
2. Ghi nguyên tử: ghi file tạm cùng thư mục, `flush` + `fsync`, rồi `os.replace`; lỗi ở bất kỳ bước nào thì `.env` cũ còn nguyên, file tạm bị dọn, câu báo không lộ đường dẫn hay nội dung.
3. Câu báo khi không ghi được vẫn là câu tiếng Việt cố định (như T-090 lượt 2), và đúng sự thật (file cũ còn nguyên).
4. Test cho các ca:
   - hai dòng mã băm;
   - ký tự FF, VT, NEL, U+2028 trong giá trị dòng khác;
   - BOM;
   - CRLF;
   - lỗi ghi giữa chừng (giả lỗi ở mức file tạm hoặc `os.replace`).
5. Đổi cách giả lỗi của `test_set_password_cannot_write_env`: Chỉ Huy duyệt (R5), ghi rõ trong báo cáo.

## Yêu cầu bảo mật riêng

U3, F3.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-104-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (U3, F3).

## Ghi chú của Chỉ Huy

- Lập 2026-10-28 theo đề xuất của Lá Chắn T-090 và chỉ đạo «vấn đề nào có đề xuất thì làm theo đề xuất».
- 2026-10-29 00:41 (Chỉ Huy B): T-090 đã gộp. Nhánh `team/T-104` từ `main` `b8ac183`, worktree `wt-T-104`; giao Thợ Máy (phiên Thợ Máy T-094). Chỉ Huy duyệt (R5) đổi cách giả lỗi của `test_set_password_cannot_write_env` (giả ở file tạm hoặc `os.replace`), giữ ý ca.
- 2026-10-30 11:00 (Chỉ Huy B): Soi Lỗi ĐẠT (`8eef5cb`), Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN (`b9e51fc`: LC-T090-1, -2 đóng). Gộp `main` (`0122d4b`), Windows 20.051 test qua, 0 hỏng. SL-T104-1, -2 (Thấp) → T-105 theo đề xuất.

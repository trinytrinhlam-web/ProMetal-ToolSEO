# Báo cáo T-104 · `set_password` ghi `.env` an toàn (LC-T090-1, LC-T090-2)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-104](../tickets/T-104-set-password-ghi-env-an-toan.md) |
| Nhánh | `team/T-104` (từ `main` `b8ac183`) |
| Ngày nộp | 2026-10-29 00:06 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đặt mật khẩu bằng `set_password` nay **luôn có hiệu lực**. Trước đây, nếu `.env` có hai dòng `APP_PASSWORD_HASH` (ví dụ dòng mẫu và dòng dán thêm), script sửa dòng đầu còn app đọc dòng cuối, nên mật khẩu mới không dùng được. Nay script thay **mọi** dòng mật khẩu.
- Ghi `.env` không còn có thể làm **mất file**. Script ghi ra một file tạm cạnh `.env`, ghi xong mới thay vào. Ghi lỗi (đĩa đầy, file đang bị chương trình khác giữ, không có quyền) thì `.env` cũ còn nguyên từng byte, file tạm được dọn, câu báo tiếng Việt nói đúng «File .env cũ vẫn còn nguyên».
- Mọi dòng khác trong `.env` (khóa API, đường dẫn ảnh, Google Sheet…) giữ nguyên, kể cả file lưu kiểu «UTF-8 with BOM», xuống dòng kiểu Windows, hay có ký tự lạ trong giá trị.
- Không đổi cách băm hay cách so mật khẩu. Mật khẩu đang dùng không bị ảnh hưởng; chỉ khi chạy lại `set_password` mới dùng cách ghi mới.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/env_file.py` | Thêm `set_password_hash` (chỉ nhận chuỗi dạng mã băm `[A-Za-z0-9_:]`, tối đa 512 ký tự; sai thì báo câu cố định, không chép giá trị). Ghi qua bộ ghi chung có sẵn (`_write_value` → `_build_content` → `_atomic_write`). Thêm 3 lớp lỗi con của `EnvFileError` để nơi gọi báo đúng sự thật: `EnvFileReadError` (không đọc được, kèm `not_utf8` / `error_name`), `EnvFileWriteError` (lỗi trước hoặc ngay ở `os.replace`, file cũ chưa bị thay), `EnvFileFormatError` (nội dung mới không khớp cách dotenv đọc: không ghi, hoặc đã trả bản cũ). Thêm câu `_RESTORE_FAILED` cho ca hiếm «đã thay mà đọc lại thấy sai và trả bản cũ cũng lỗi»: không báo «còn nguyên». `_BOM` viết bằng `chr(0xFEFF)` thay cho ký tự trần |
| `scripts/hash_password.py` | `set_env_value` bỏ cách tự sửa từng dòng + `Path.write_text`, gọi `set_password_hash`; chỉ nhận khóa `APP_PASSWORD_HASH`. Chép `.env.example` khi chưa có `.env` giữ như cũ. Lỗi đổi sang câu cố định: `MSG_ENV_KEPT` (ghi lỗi, «File .env cũ vẫn còn nguyên»), `MSG_ENV_FORMAT` (dòng sai định dạng, chưa ghi), `MSG_ENV_NOT_UTF8` / `MSG_ENV_UNREADABLE` (như T-090). `MSG_ENV_UNWRITABLE` chỉ còn dùng khi chép mẫu lỗi (lúc đó chưa có file cũ để nói «còn nguyên»). `read_env_lines` (kiểm `.env` đọc được trước khi hỏi mật khẩu) tách dòng như dotenv: chỉ CR, LF |
| `tests/test_t104_set_password.py` (mới) | 12 hàm test, 38 ca (xem mục Kiểm thử) |
| `tests/test_t090_env_bang_ma.py` | `test_set_password_cannot_write_env`: đổi cách giả lỗi (R5, xem dưới) |
| `tests/test_la_chan_t090.py` | Gỡ 3 dấu `xfail` (LC-T090-1 dòng lặp, LC-T090-1 ký tự tách dòng, LC-T090-2); 17 ca XPASS. Chỉ xóa dấu, không sửa điều kiện kiểm |

## Đối chiếu yêu cầu

| Yêu cầu | Cách làm | Test |
|---|---|---|
| 1. Tách dòng như dotenv, bỏ BOM, thay mọi dòng mã băm, giữ dòng khác | Bộ ghi chung tách file bằng chính `dotenv.parser.parse_stream` (đúng ranh giới dòng, giá trị nhiều dòng trong nháy), bỏ BOM trước khi tách rồi gắn lại; mọi đoạn có khóa `APP_PASSWORD_HASH` (kể cả `export`, dấu cách quanh «=») đều thay bằng dòng mới, đoạn khác chép nguyên văn. Trước khi ghi còn so: dotenv đọc nội dung mới phải ra đúng các biến cũ + mã băm mới, không khớp thì không ghi | `test_every_hash_line_replaced_new_password_works` (4 ca), `test_hash_line_inside_other_multiline_value_is_not_touched`, `test_other_values_with_unicode_separators_kept_byte_for_byte` (FF, VT, NEL, U+2028, U+2029, RS; có/không nháy: 12 ca), `test_bom_with_hash_on_first_line_replaced_in_place`, `test_crlf_line_endings_kept`, `test_missing_line_is_appended`, `test_read_env_lines_splits_like_dotenv` |
| 2. Ghi nguyên tử | `_atomic_write` (có sẵn từ trước): `mkstemp` cùng thư mục → ghi → `flush` → `fsync` → (Mac/Linux `chmod 600`) → `os.replace`; lỗi thì xóa file tạm trong `finally` | `test_write_failure_keeps_env_and_cleans_temp` (lỗi ở tạo file tạm, `fsync`, `os.replace`: `.env` giống từng byte, không sót `.tmp`, mật khẩu cũ vẫn đăng nhập được) |
| 3. Câu báo cố định, đúng sự thật | `EnvFileWriteError` → `MSG_ENV_KEPT`; không có đường dẫn, câu lỗi gốc, traceback. Ca trả bản cũ cũng lỗi → câu riêng, không nói «còn nguyên» | cùng test trên (kiểm câu, không «Permission denied», không đường dẫn); `test_restore_failure_is_not_reported_as_unchanged` |
| 4. Test các ca | Đủ: hai dòng mã băm; FF, VT, NEL, U+2028; BOM; CRLF; lỗi giữa chừng. Ký tự lạ viết bằng `chr(…)` | như trên; thêm `test_set_password_hash_rejects_unsafe_values_without_echo` (11 ca), `test_set_password_hash_accepts_real_hash`, `test_script_only_writes_password_hash` |
| 5. Đổi cách giả lỗi của test cũ | Xem mục dưới | |

## Đổi cách giả lỗi `test_set_password_cannot_write_env` (Chỉ Huy B duyệt, R5)

- Cũ: tạo lớp con `Path` có `write_text` ném `PermissionError`. Script nay không gọi `Path.write_text` nữa (ghi qua file tạm + `os.replace`), nên cách giả này không còn chạm tới đường ghi; test đỏ đúng như dự kiến.
- Mới: giả `PermissionError` ở `seo_app.env_file.os.replace`, đúng chỗ Windows từ chối khi `.env` đang bị chương trình khác giữ.
- Ý test giữ nguyên, các `assert` không đổi: mã thoát 1, câu cố định kèm tên loại lỗi, không traceback, không đường dẫn, file giữ nguyên. Docstring của test ghi lý do và việc Chỉ Huy duyệt.

## Kiểm thử

- 12 file test (T-104, T-090 cả 3 file, script `hash_password`, `env_file`, đăng nhập `test_auth`, `test_config`, khóa API `test_settings_keys`, `test_soi_loi_t016_t020`, Google Sheet `test_google_sheets`, `test_soi_loi_t097`): **958 qua, 10 bỏ qua, 3 xfail**.
  - 3 xfail là SL-T097-5 trong `test_soi_loi_t097.py`, có từ trước, thuộc T-100; không liên quan phiếu này.
  - 10 bỏ qua là ca chỉ chạy trên Mac/Linux (symlink, quyền POSIX).
  - Ca chỉ chạy trên Windows `test_lc2_env_never_emptied_when_write_fails` (khóa thật bằng `LockFileEx`, `.env` không bao giờ rỗng) đã chạy và qua.
- 17 ca Lá Chắn T-090 trước là `xfail` nay qua thật (đã gỡ dấu).
- `uv run ruff check .`: All checks passed; `ruff format --check` sạch.
- Quét ký tự vô hình trần trong file đã sửa: sạch.
- `detect-secrets` (`PYTHONUTF8=1`) trên 6 file: 2 kết quả «Secret Keyword», đều báo nhầm. `seo_app/env_file.py:54` là tên biến `PASSWORD_HASH_VAR = "APP_PASSWORD_HASH"`, không phải giá trị. `tests/test_t090_env_bang_ma.py:30` đã có y hệt trên `main`.
- Không đọc `.env` thật; mọi test dùng `.env` giả trong thư mục tạm, mật khẩu giả ghép lúc chạy.

## Rủi ro, ghi chú

- `os.chmod(…, 0o600)` trên file tạm chỉ chạy trên Mac/Linux (có từ trước trong bộ ghi chung). Chưa thử trên máy Mac thật (theo T-063, chủ dự án chưa có Mac).
- Chép `.env.example` thành `.env` lúc chưa có `.env` không nguyên tử (`shutil.copyfile`, như cũ). Lúc đó chưa có dữ liệu người dùng nên lỗi giữa chừng không làm mất gì; câu báo là `MSG_ENV_UNWRITABLE` (không nói «còn nguyên»).
- Bộ ghi chung dùng cho cả khóa API và Google Sheet ID. Thay đổi ở đó chỉ là thêm lớp lỗi con (vẫn là `EnvFileError`, câu báo giữ nguyên) và một nhánh mới khi trả bản cũ lỗi; test `env_file`, khóa API, Google Sheet đều chạy lại và qua.

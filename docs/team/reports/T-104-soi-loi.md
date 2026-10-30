# Báo cáo T-104 · `set_password` ghi `.env` an toàn (LC-T090-1, LC-T090-2) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-104](../tickets/T-104-set-password-ghi-env-an-toan.md) |
| Ngày nộp | 2026-10-29 |
| Nhánh | `team/T-104` (kiểm code `8acf9c7`, gốc `main` `b8ac183`) |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT, chuyển Lá Chắn rút gọn được ngay.** LC-T090-1, LC-T090-2 **đã sửa thật**. Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T104-1: câu báo sai nguyên nhân ở một đường hiếm, file vẫn an toàn; SL-T104-2: **có từ trước**, ngoài phạm vi phiếu). **Không lỗi nào phải sửa trước Lá Chắn.** Soát R5: đạt. Thử gộp với `main` mới nhất trên máy: không xung đột |

## Tóm tắt (cho chủ dự án)

- Đặt mật khẩu bằng `set_password` nay có hiệu lực đúng như app đọc trong mọi kiểu `.env` tôi thử: nhiều dòng mật khẩu, dòng có `export`, dấu cách, dấu nháy, file «UTF-8 with BOM», xuống dòng kiểu Windows hay kiểu Mac cũ, ký tự lạ trong giá trị khác, và 300 file `.env` ngẫu nhiên (thêm 3.000 file khi thử tay). Các dòng khác (khóa AI, mật khẩu WordPress, thư mục ảnh…) giữ nguyên.
- Ghi lỗi ở bất kỳ bước nào (ổ đầy giữa chừng, `.env` đang mở ở chương trình khác, `.env` chỉ đọc, không tạo được file tạm…): `.env` cũ **còn nguyên từng byte**, không sót file tạm, câu báo tiếng Việt nói đúng «File .env cũ vẫn còn nguyên», không lỗi tiếng Anh, không đường dẫn.
- Còn 2 lỗi nhỏ:
  1. Một đường rất hiếm: ghi xong mà lần đọc lại để kiểm bị lỗi (file vừa bị chương trình khác giữ đúng lúc đó) thì app trả bản cũ (đúng), nhưng câu báo bảo «có dòng sai định dạng… thiếu dấu nháy đóng», trong khi không có dòng nào sai.
  2. Có từ trước, ngoài phiếu: nếu máy có **biến môi trường** `APP_PASSWORD_HASH` (đặt tay trong Windows), app dùng biến đó thay cho `.env`; `set_password` vẫn báo «Đã lưu mật khẩu mới» nhưng mật khẩu mới không dùng được, mật khẩu cũ vẫn vào được.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t104.py` | Mới: 25 ca (23 qua, 2 `xfail(strict=True)` SL-T104-1, -2). Dùng lại hàm nạp script của `tests/test_hash_password_script.py` |
| `docs/team/reports/T-104-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng việc được giao

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| 1. Mật khẩu mới luôn có hiệu lực đúng như app đọc (python-dotenv): hai dòng mã băm trở lên, `export`, dấu nháy, BOM, CRLF, FF, VT, NEL, U+2028, U+2029 trong giá trị dòng khác | **Đạt** | 17 ca `xfail` cũ của Lá Chắn T-090 (dòng lặp, ký tự tách dòng, khóa chia sẻ) nay qua thật; test Thợ Máy qua. Thêm `test_new_password_active_and_other_values_kept` × 16: ba dòng mã băm có `export`, dấu cách quanh «=», nháy đơn; mã băm trong nháy kép kèm chú thích; dòng chỉ có tên biến; dòng chú thích giống mã băm (không bị đụng); BOM có và chưa có dòng mã băm; CR kiểu Mac cũ; CRLF trộn LF; không xuống dòng cuối; file rỗng; chỉ chú thích; nháy mở không đóng ở biến khác; dòng mã băm giả nằm trong giá trị nhiều dòng; FF, VT, NEL, U+2028, U+2029, RS, NUL, tab trong giá trị. `test_other_value_referencing_hash_follows_new_hash`: biến tham chiếu `${APP_PASSWORD_HASH}` đọc ra mã băm mới. `test_random_env_files`: 300 `.env` ngẫu nhiên (hạt giống cố định), 0 sai. Thử tay 3.000 `.env` ngẫu nhiên cùng kiểu: 0 sai |
| 2. Các dòng khác giữ nguyên từng byte có nghĩa | **Đạt** | Mọi ca trên: python-dotenv đọc ra đúng các biến khác như trước, BOM giữ nguyên; test byte của Thợ Máy (6 ký tự tách dòng × có, không nháy: từng byte), BOM, CRLF qua |
| 3. Lỗi ghi ở mọi bước: `.env` cũ còn nguyên, file tạm được dọn, câu báo đúng sự thật, không traceback, không đường dẫn | **Đạt**, trừ SL-T104-1 (bước đọc lại sau khi thay) | `test_write_fault_keeps_env_and_tells_truth` × 3: ổ đầy giữa lúc ghi file tạm (ghi được một nửa rồi `ENOSPC`), `flush` lỗi, không tạo được file tạm. `test_real_windows_refusal_keeps_env` × 2 (lỗi thật của Windows, không giả): `.env` đang được chương trình khác mở, `.env` có thuộc tính chỉ đọc. Cả 5: mã thoát 1, `.env` giống từng byte, không sót `.env.*.tmp`, câu «Không ghi được file .env (…). File .env cũ vẫn còn nguyên…». Test Thợ Máy (tạo file tạm, `fsync`, `os.replace`) và Lá Chắn (`test_lc2_env_never_emptied_when_write_fails`: khóa chia sẻ thật bằng `LockFileEx`) qua. File tạm sót lại khi mất điện đúng lúc ghi (`.env.*.tmp`, có cả khóa) đã nằm trong `.gitignore` (`.env.*`) |
| 4. Không lùi T-090 | **Đạt** | `tests/test_t090_env_bang_ma.py`, `tests/test_soi_loi_t090.py` (gồm `.env` bị khóa thật, «ANSI», UTF-16, byte lạ, đăng nhập sau khi sửa), `tests/test_la_chan_t090.py`, `tests/test_soi_loi_t084.py`, `tests/test_app_pages.py` qua (mục «Bằng chứng») |
| 5. Đổi test đúng điều kiện duyệt; gỡ `xfail` LC-T090-1, -2 đúng R5 | **Đạt** | Mục «Soát R5» |
| 6. Thử gộp với `main` mới nhất trên máy | **Không xung đột** | `git merge-tree`: `team/T-104` với `main` trên máy `209615a` (đã có T-103, chưa đẩy) và `origin/main` `03d39d7`. Từ `b8ac183`, `main` chỉ đổi phần kế hoạch T-103, không đụng `scripts/`, `seo_app/env_file.py`, `seo_app/config.py` hay test của phiếu |

## Lỗi tìm thấy

Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t104.py` (`--runxfail`: hỏng đúng câu kiểm).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T104-1 | Thấp (đường rất hiếm, file vẫn an toàn) | Đọc lại `.env` ngay sau khi thay mà lỗi thì câu báo nói sai nguyên nhân | `test_readback_failure_message_tells_the_real_cause`: lần đọc thứ hai của bộ ghi (đọc lại ngay sau `os.replace` để kiểm) ném `EnvFileReadError` (như khi chương trình quét virus, đồng bộ đang giữ file đúng lúc đó) | Câu nói đúng: chưa lưu được vì không đọc lại được file để kiểm; file cũ còn nguyên | Bộ ghi trả bản cũ (đúng, file còn nguyên từng byte), nhưng `_write_value` ném `EnvFileFormatError` cho cả hai ca «đọc lại lỗi» và «đọc lại ra khác», nên `set_password` in `MSG_ENV_FORMAT`: «File .env có dòng sai định dạng nên chưa ghi được mật khẩu mới… Mở .env, sửa dòng đó (thường là thiếu dấu nháy đóng)…»: người dùng đi tìm dòng hỏng không có. Cùng đường: chương trình khác (ví dụ trang Cài đặt lưu khóa đúng lúc) đổi `.env` giữa lúc thay và lúc đọc lại thì bộ ghi trả bản cũ, đè mất thay đổi kia (đọc mã, chưa thử) | Ở `_write_value`: lần đọc lại lỗi (`EnvFileError` khi đọc) thì sau khi trả bản cũ ném lỗi riêng (ví dụ `EnvFileWriteError` kèm tên loại lỗi) để `set_password` báo `MSG_ENV_KEPT`; chỉ ném `EnvFileFormatError` khi đọc lại được mà nội dung khác |
| SL-T104-2 | Thấp, **có từ trước** (ngoài phạm vi phiếu: `load_settings` ưu tiên biến môi trường từ Giai đoạn 0) | Máy có biến môi trường `APP_PASSWORD_HASH` thì `set_password` báo «Đã lưu mật khẩu mới» mà mật khẩu mới không có hiệu lực | `test_os_environment_hash_is_reported`: biến môi trường `APP_PASSWORD_HASH` = mã băm cũ, chạy `set_password` | Báo rõ: mật khẩu mới chỉ có hiệu lực khi gỡ biến đó khỏi máy (như trang Cài đặt đã nhắc cho khóa API) | Mã thoát 0, «Đã lưu mật khẩu mới vào …»; `load_settings()` vẫn ra mã băm cũ: mật khẩu mới bị từ chối, mật khẩu cũ vẫn đăng nhập được (thử tay: đúng như vậy). Cùng hệ quả LC-T090-1, khác đường; ít gặp (phải tự đặt biến môi trường) | `main` của `scripts/hash_password.py` kiểm `env_file.overridden_by_os_environ("APP_PASSWORD_HASH")` trước khi hỏi mật khẩu: in câu nhắc gỡ biến, thoát mã 1 (hoặc ghi rồi nhắc, không báo đã xong như thường) |

## Ghi nhận (không phải lỗi)

1. Ổ đầy: câu báo «Không ghi được file .env (OSError). File .env cũ vẫn còn nguyên. Đóng chương trình đang mở file (nếu có), kiểm tra quyền ghi file…» đúng sự thật nhưng lời khuyên không nhắc «ổ đĩa đầy». Có thể thêm vào câu (ví dụ «…, ổ đĩa còn chỗ trống…»).
2. `.env` là liên kết tắt (symlink): bộ ghi không ghi xuyên qua (quy tắc Lá Chắn T-016-020), đúng; nhưng bước kiểm đầu của `set_password` đọc xuyên liên kết nên người dùng gõ mật khẩu hai lần rồi mới bị báo. Đọc mã, chưa thử (Windows cần quyền tạo symlink).
3. Ghi bằng `os.replace` thay file mới: trên Windows file mới mang quyền thừa kế của thư mục (thuộc tính chỉ đọc, quyền riêng đặt tay trên `.env` cũ không còn); Mac/Linux đặt 600. Đọc mã; để Lá Chắn xem ở F3.
4. Mã băm thật của `seo_app.auth` (`pbkdf2_sha256:lặp:muối hex:băm hex`) khớp bộ lọc `[A-Za-z0-9_:]{1,512}` của `set_password_hash`.

## Soát R5

- `tests/test_la_chan_t090.py`: `git diff b8ac183..8acf9c7` chỉ xóa 3 dấu `@pytest.mark.xfail(...)` (15 dòng): LC-T090-1 dòng lặp, LC-T090-1 ký tự tách dòng, LC-T090-2; thân test, `parametrize`, `skipif` giữ nguyên.
- `tests/test_t090_env_bang_ma.py::test_set_password_cannot_write_env`: đổi cách giả lỗi đúng điều kiện **Chỉ Huy B duyệt** (giả ở `os.replace` của bộ ghi thay cho `Path.write_text` mà script không còn gọi); các `assert` giữ nguyên (mã thoát 1, câu cố định kèm tên loại lỗi, không đường dẫn, file giữ nguyên); docstring ghi lý do. Không nới.
- Không `skip`, không xóa test.

## U3, F3 (soát nhanh)

- U3: không đổi cách băm, cách so mật khẩu; mã băm ghi đúng dòng có hiệu lực (trừ SL-T104-2, có từ trước).
- F3: đọc, ghi `encoding="utf-8"`, ghi nguyên tử (file tạm cùng thư mục, `flush`, `fsync`, `os.replace`), file tạm được dọn ở mọi lỗi đã thử; Ghi nhận 3.

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest -rxXfs tests/test_t104_set_password.py tests/test_soi_loi_t104.py \
    tests/test_t090_env_bang_ma.py tests/test_la_chan_t090.py tests/test_soi_loi_t090.py \
    tests/test_hash_password_script.py tests/test_env_file.py tests/test_settings_keys.py \
    tests/test_soi_loi_t016_t020.py tests/test_google_sheets.py tests/test_soi_loi_t097.py \
    tests/test_soi_loi_t023.py tests/test_auth.py tests/test_config.py tests/test_app.py \
    tests/test_soi_loi_t084.py tests/test_app_pages.py
1080 passed, 10 skipped, 4 xfailed in 212.71s (0:03:32)   # code 8acf9c7 + test Soi Lỗi 8581769
# 0 hỏng, 0 XPASS. 4 xfail: SL-T104-1 (1) và SL-T097-5 có sẵn trên main (3, thuộc T-100).
# 10 bỏ qua có sẵn (symlink cần quyền đặc biệt, quyền kiểu POSIX: chỉ chạy trên Mac/Linux).

$ uv run pytest tests/test_soi_loi_t104.py -rxX      # bản cuối 9229085 (thêm SL-T104-2)
23 passed, 2 xfailed in 17.23s

$ uv run pytest tests/test_soi_loi_t104.py --runxfail -k "readback or os_environment"
2 failed   # hỏng đúng câu kiểm: câu có «sai định dạng»; mã thoát 0, không nhắc biến môi trường

# Thử tay (script trong scratchpad của phiên): 18 kiểu .env lạ và 3.000 .env ngẫu nhiên: 0 sai;
# 5 kiểu lỗi ghi (ổ đầy giữa chừng, flush, file đang mở, chỉ đọc, không tạo được file tạm):
# .env giữ nguyên từng byte, không sót .env.*.tmp, câu «File .env cũ vẫn còn nguyên».

$ git merge-tree --write-tree HEAD main          # main trên máy 209615a: không xung đột
$ git merge-tree --write-tree HEAD origin/main   # 03d39d7: không xung đột

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t104.py docs/team/reports/T-104-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Không đọc `.env` thật; mọi test dùng `.env` giả trong thư mục tạm.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Mật khẩu mới có hiệu lực đúng như python-dotenv đọc ở mọi ca được giao và thêm; dòng khác giữ nguyên.
- [x] Lỗi ghi ở mọi bước: `.env` cũ còn nguyên, file tạm dọn, câu báo cố định (trừ SL-T104-1 ở bước đọc lại).
- [x] Không lùi T-090; đổi test và gỡ `xfail` đúng R5; thử gộp với `main` mới nhất: không xung đột.
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T104-n; không sửa code ứng dụng.

## Đề xuất

- **Thợ Máy (phiếu nhỏ, không chặn):** SL-T104-1, SL-T104-2 theo cột «Gợi ý sửa»; Ghi nhận 1, 2 nếu tiện.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-105 · `set_password`: câu báo đúng nguyên nhân, biến môi trường đè `.env` · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-105 `docs/team/tickets/T-105-set-password-cau-bao-bien-moi-truong.md` (đọc ở bản trên `main`) · mức kiểm **rút gọn**, Windows · yêu cầu bảo mật U3, F3. Không chạy cloud, không đụng website, không đổi mật khẩu thật của máy |
| Ngày nộp | 2026-10-31 |
| Máy kiểm | Windows 11 Pro 10.0.26300, `uv 0.13.4`, Python 3.12.15. Máy đang chạy toàn bộ test trên `main` |
| Mã nguồn | `team/T-105` tại `4f8c31a` (mã + test `1ca123a`, gốc `origin/main` `731a46e`). Gộp thử với `main` cục bộ `4ee27d8` |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới, có từ trước** (SL-T105-1, từ T-104; không chặn Lá Chắn). SL-T104-1 và SL-T104-2 đóng đúng ý, kể cả khi chạy thật `set_password.bat` và khi khóa file kiểu chia sẻ của Windows. Câu báo cố định, không đường dẫn, không traceback, không lộ giá trị biến. `.env` vẫn ghi nguyên tử, không mất dòng. Không lùi T-090, T-104, đăng nhập app. R5 chỉ gỡ đúng 2 dấu `xfail`. Gộp `main` sạch |

## Tóm tắt (cho chủ dự án)

- **Hai lỗi của phiếu đã sửa đúng.**
  - Khi phần mềm khác (diệt virus, đồng bộ) giữ file `.env` đúng lúc lưu, công cụ đặt mật khẩu nay nói đúng nguyên nhân. Câu báo khớp trạng thái thật của file: «file cũ còn nguyên» hoặc «chưa chắc đã lưu».
  - Khi máy có biến môi trường `APP_PASSWORD_HASH`, công cụ dừng trước khi hỏi mật khẩu, giải thích và chỉ cách gỡ biến. Không in giá trị của biến.
- Đã chạy thật `set_password.bat` với biến ở 5 dạng: có giá trị, rỗng, toàn khoảng trắng, tên viết thường, tên lẫn hoa thường. Cả 5 đều báo đúng.
- **Một lỗi nhỏ mới (Thấp, có từ trước), SL-T105-1:** nếu chương trình khác **sửa** `.env` đúng phần nghìn giây vừa lưu, công cụ vẫn báo nhầm «dòng sai định dạng». File vẫn được trả về bản cũ, không mất gì. Rất hiếm, không chặn.

## Việc 1 · SL-T104-1: đọc lại `.env` lỗi → câu đúng nguyên nhân — **đạt**

Test của Thợ Máy khóa file bằng khóa vùng byte (`msvcrt.locking`). Tôi thử thêm kiểu khóa mà phần mềm diệt virus, đồng bộ thư mục, trình soạn thảo hay dùng: mở file bằng `CreateFileW` với chế độ chia sẻ hẹp (`sl105_sharelock.py`). Cách chạy:
- Gọi `set_password` thật (`main`), mật khẩu gõ giả.
- `.env` tạm có chú thích tiếng Việt và 3 dòng khác.

| Ca | Mã thoát | Câu báo | `.env` sau đó |
|---|---|---|---|
| A. Khóa không chia sẻ, từ ngay sau khi thay file tới hết | 1 | «Chưa chắc đã lưu được mật khẩu mới. Không đọc lại được file .env để kiểm sau khi ghi (PermissionError), cũng không bỏ được bản vừa ghi…» | Đúng là đang mang mật khẩu mới, đủ các dòng khác. Câu **không** nói «còn nguyên» |
| B. Khóa chỉ cho xóa/đổi tên, từ sau khi thay tới hết | 1 | Như A. Windows cũng từ chối trả bản cũ | Như A, khớp câu báo |
| C. Khóa không chia sẻ từ trước khi chạy | 1 | «Chưa đặt được mật khẩu. Không đọc được file .env (PermissionError)…» (T-104) | Giữ nguyên từng byte |
| D. Khóa chỉ cho đọc từ trước khi chạy | 1 | «Chưa lưu mật khẩu mới. Không ghi được file .env (PermissionError). File .env cũ vẫn còn nguyên…» (T-104) | Giữ nguyên từng byte |

Cả 4 ca: không lộ đường dẫn thư mục tạm, không traceback, không sót file tạm `.env.*.tmp`. Hai ca khóa vùng byte của Thợ Máy (trả bản cũ được / không được) chạy qua trên máy.

Dòng sai định dạng thật vẫn được báo đúng:
- Mã băm nằm trong dấu nháy chưa đóng: «Dòng APP_PASSWORD_HASH trong file .env đang sai định dạng (thường là thiếu dấu nháy đóng)…», `.env` giữ nguyên.
- Một dòng **khác** thiếu nháy, nuốt cả dòng mã băm cũ: `set_password` thêm dòng mã băm mới ở cuối và báo «Đã lưu». Đã kiểm bằng `load_settings`: app đúng là dùng mật khẩu mới, nên câu «Đã lưu» đúng.

## Việc 2 · SL-T104-2: biến môi trường đè `.env` — **đạt**

Điều kiện mới `password_hash_overridden` (biến **có mặt**, kể cả rỗng) khớp đúng cách `load_settings` đọc: `values.update({name: env[name] for name in ENV_VARS if name in env})`, rồi `strip`. Vì vậy:
- biến rỗng hay toàn khoảng trắng: app dùng mã băm rỗng, bỏ qua `.env`, nên báo «bị đè» là đúng;
- chữ hoa/thường: trên Windows `os.environ` không phân biệt, nên app và công cụ cùng thấy biến; trên Mac/Linux cả hai cùng phân biệt.

Chạy thật `set_password.bat` (`sl105_bat.py`: `cmd /c set_password.bat` → `uv run python scripts/hash_password.py`, Enter cho lệnh `pause`). Worktree không có `.env`.

| Biến | Kết quả |
|---|---|
| `APP_PASSWORD_HASH=<giá trị dấu riêng>` | Dừng trước khi hỏi mật khẩu: «Chưa đặt được mật khẩu. Máy này đang có biến môi trường APP_PASSWORD_HASH…», kèm 3 bước gỡ biến (Windows, Mac) |
| `APP_PASSWORD_HASH=` (rỗng) | Như trên |
| `APP_PASSWORD_HASH="   "` | Như trên |
| `app_password_hash=…` (chữ thường) | Như trên |
| `App_Password_Hash=…` | Như trên |

Cả 5 ca: **không** in giá trị biến, không traceback, không đường dẫn, không tạo `.env`.

Không báo động nhầm:
- Trong thư mục có `.env` chứa mã băm, máy không có biến: `uv run` **không** tự nạp `.env` vào biến môi trường. `'APP_PASSWORD_HASH' in os.environ` là `False`, `password_hash_overridden()` là `False`.
- Không chỗ nào trong `seo_app/`, `app/`, `scripts/` gọi `load_dotenv`. Máy không đặt `UV_ENV_FILE`.

Chế độ `--print` (in mã băm kèm lời lưu ý khi có biến): test của Thợ Máy qua. File `.bat` không truyền `--print` nên không chạy được qua `.bat`.

## Việc 3 · R5, U3, F3 — **đạt**

- `tests/test_soi_loi_t104.py`: diff chỉ xóa đúng 2 khối `@pytest.mark.xfail(strict=True, …)` của SL-T104-1, SL-T104-2 (10 dòng). Thân test, điều kiện kiểm giữ nguyên, nay qua thật. Không test cũ nào khác bị đổi.
- U3: không đổi cách băm hay cách so mật khẩu (`seo_app/auth.py` không đổi). Mật khẩu không bị in; giá trị biến môi trường không bao giờ được đọc ra, hàm chỉ trả đúng/sai.
- F3: đọc/ghi `.env` vẫn qua `_read_env_text` / `_atomic_write` (UTF-8, nguyên tử) của T-104. Không có `eval`/`pickle`.
- `.env` ghi nguyên tử, không mất dòng: mọi ca trên giữ đủ chú thích và các dòng khác; không sót file tạm.

## Việc 4 · Không lùi; gộp thử

- Test chọn lọc trên nhánh, 15 file: `test_t105_set_password`, `test_soi_loi_t104`, `test_t104_set_password`, `test_hash_password_script`, `test_env_file`, `test_auth`, `test_config`, `test_config_tolerance`, `test_la_chan_t090`, `test_soi_loi_t090`, `test_t090_env_bang_ma`, `test_settings_keys`, `test_la_chan_t097`, `test_soi_loi_t097`, `test_app`.
  - Kết quả: **789 qua, 4 bỏ qua, 0 hỏng, 0 xfail, không XPASS** (3 phút).
  - **T-090, T-104, đăng nhập app (`test_auth`, `test_app`) không lùi.** Trang Cài đặt lưu khóa AI và mã Google Sheet (`test_settings_keys`, T-097) không lùi.
- Thêm test Soi Lỗi `tests/test_soi_loi_t105.py`: 2 ca `xfail(strict=True)`.
- `ruff check`, `ruff format --check` file mới: sạch.
- Gộp thử với `main` cục bộ `4ee27d8` (đã có T-110 lượt 2–3): `git merge-tree --write-tree main team/T-105` **không xung đột** (cây `5667e36`). Từ `731a46e`, `main` chỉ sửa `app/views/write.py`, `seo_app/wordpress/client.py` và test ảnh, WordPress. Không file nào T-105 sửa hay dùng tới, nên không chạy riêng test trên bản gộp.

## Thử đột biến (`sl105_mutate.py`)

Bản sao `git archive` riêng cho mỗi đột biến, chạy 5 file (`test_t105_set_password`, `test_soi_loi_t104`, `test_t104_set_password`, `test_hash_password_script`, `test_env_file`). Đối chứng không đổi: 191 qua, 4 bỏ qua.

| Đột biến | Test hỏng |
|---|---|
| N1 `password_hash_overridden` luôn `False` | 11 |
| N2 bỏ qua biến rỗng/khoảng trắng (khác `load_settings`) | 5: `[rong]`, `[dau-cach]` ở 3 test |
| N3 không dừng khi biến đè | 3, gồm `test_os_environment_hash_is_reported` (T-104) |
| N4 `--print` không kèm lời lưu ý | 1 |
| N5 file vừa ghi biến mất coi như lỗi định dạng | 1: `[bien-mat]` |
| N6 đảo cờ «đã bỏ bản vừa ghi» | 11 |
| N7 lỗi đọc lại báo như lỗi định dạng (bỏ phần sửa SL-T104-1) | 11 |
| N8 tên lỗi trong câu báo thành câu lỗi gốc (có thể lộ đường dẫn) | 1: `[lien-ket-tat]` |
| N9 bỏ bắt `OSError` khi bỏ bản vừa ghi | 2 |
| N10 «chưa chắc đã lưu» báo như «đã bỏ, còn nguyên» | 2, gồm ca khóa thật `test_real_lock_after_replace_until_end` |
| N11 kiểm biến **sau** khi hỏi mật khẩu | 2 |

Kết luận: mọi đột biến làm đổi hành vi đều bị test bắt.

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T105-1** | Thấp (có từ trước, từ T-104) | Bộ ghi thay `.env` xong, đọc lại **được** nhưng nội dung đã khác chữ vừa ghi, vì chương trình khác (đồng bộ thư mục trả bản cũ, trang Cài đặt lưu khóa cùng lúc…) ghi đè đúng lúc đó. Bộ ghi trả bản cũ đúng, `.env` giữ nguyên từng byte. Nhưng câu báo nói sai nguyên nhân: «File .env có dòng sai định dạng … sửa dòng đó (thường là thiếu dấu nháy đóng)» (`set_password`), hay «File .env có định dạng lạ … sửa tay» (trang Cài đặt). Người dùng đi tìm một dòng sai không có, cùng loại với SL-T104-1. Từ T-104, dòng sai định dạng phần lớn đã bị bắt **trước** khi ghi, nên khi đọc lại mà khác thì nhiều khả năng là file vừa bị sửa | `tests/test_soi_loi_t105.py`: `test_sl_t105_1_set_password_other_program_changed_env`, `test_sl_t105_1_settings_writer_other_program_changed_env`, cả hai `xfail(strict=True)`. Đã chạy `--runxfail`: hỏng đúng chỗ câu báo |

Gợi ý sửa (để Thợ Máy quyết): trong `_write_value`, khi đọc lại được mà khác, so chữ đọc lại với `content` vừa ghi.
- **Khác chữ:** file vừa bị chương trình khác sửa. Báo câu riêng, ví dụ «File .env vừa bị chương trình khác thay đổi đúng lúc lưu; đã giữ bản cũ. Đóng chương trình đồng bộ hay app đang mở rồi thử lại».
- **Giống chữ mà đọc ra khác:** mới là định dạng, giữ câu cũ.

Không chặn Lá Chắn: rất hiếm (phải trúng khe vài phần nghìn giây), file không mất gì.

## Ghi nhận (không phải lỗi)

- **GN-1:** khi `.env` có dòng không đọc được, python-dotenv in cảnh báo tiếng Anh «python-dotenv could not parse statement starting at line N» ra cửa sổ, cạnh câu tiếng Việt. Có từ trước (T-104), không do phiếu này.
- **GN-2:** câu thành công «Đã lưu mật khẩu mới vào <đường dẫn .env>.» in đường dẫn đầy đủ. Đây là file của chính người dùng, câu có từ trước. Yêu cầu «không đường dẫn» áp cho câu lỗi; câu lỗi đều đạt.
- **GN-3:** hướng dẫn gỡ biến trên Mac chỉ nói `~/.zshrc`. Biến cũng có thể nằm ở `~/.zprofile`, `~/.bash_profile` hay `launchctl setenv`. Chưa có máy Mac; Thư Ký có thể thêm nửa câu khi sửa README lần sau.
- **GN-4:** sau khi gỡ biến bằng hộp «biến môi trường» của Windows, cửa sổ cmd **đang mở sẵn** vẫn giữ biến cũ. Chạy lại `set_password` từ cửa sổ đó sẽ vẫn bị báo. Bấm đúp `set_password.bat` từ thư mục (cách README hướng dẫn) thì được biến mới. Câu báo đã dặn tắt app; có thể thêm «mở cửa sổ mới».
- **GN-5:** dòng mã băm nằm trong nháy chưa đóng chỉ bị báo **sau** khi đã hỏi mật khẩu hai lần (phép kiểm trước khi hỏi không bắt ca này). Có từ trước (T-104), câu báo đúng.

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t105.py` (2 `xfail(strict=True)`). Chạy: `uv run pytest tests/test_soi_loi_t105.py -rxX`.
- Script (thư mục ghi chú chung, `T-105-soi-loi-scripts/`, chạy từ worktree bằng `.venv/Scripts/python.exe -X utf8 <script>`):
  - `sl105_sharelock.py`: 4 kiểu khóa chia sẻ của Windows;
  - `sl105_bat.py`: chạy thật `set_password.bat` với 5 dạng biến, và `uv run` không nạp `.env`;
  - `sl105_mutate.py`: thử đột biến.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện.

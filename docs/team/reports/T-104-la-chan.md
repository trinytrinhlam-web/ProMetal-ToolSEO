# Biên bản bảo mật T-104 · `set_password` ghi `.env` an toàn (LC-T090-1, LC-T090-2) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-104](../tickets/T-104-set-password-ghi-env-an-toan.md), sửa [LC-T090-1, LC-T090-2](T-090-la-chan.md) |
| Phạm vi | Rút gọn: U3, F3 (cộng S1, S2) và 8 việc Chỉ Huy giao. Diff `b8ac183...team/T-104`, đầu nhánh lúc kiểm `8eef5cb` (code `8acf9c7`; sau đó chỉ có test và báo cáo Soi Lỗi): `seo_app/env_file.py` (+64/−10: `set_password_hash`, `PASSWORD_HASH_VAR`, ba lớp lỗi con `EnvFileReadError`, `EnvFileWriteError`, `EnvFileFormatError`, câu `_RESTORE_FAILED`), `scripts/hash_password.py` (+45/−19: `set_env_value` ghi qua `set_password_hash`, câu `MSG_ENV_KEPT`, `MSG_ENV_FORMAT`, `read_env_lines` tách dòng như python-dotenv); test mới `tests/test_t104_set_password.py`, `tests/test_soi_loi_t104.py`; test đổi `tests/test_la_chan_t090.py` (−15), `tests/test_t090_env_bang_ma.py` (+11/−5) |
| Ngày | 2026-10-29 (01:32–01:47 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được**: **LC-T090-1, LC-T090-2 đóng**; 0 Nghiêm trọng, 0 Cao, 0 Trung bình; **không có lỗi mới của Lá Chắn**. Giữ mức **Thấp** cho 2 lỗi Soi Lỗi đã ghi (SL-T104-1; SL-T104-2 có từ trước), đã có `xfail(strict=True)`; sửa ở một phiếu nhỏ sau, không chặn |

## Tóm tắt (cho chủ dự án)

- Đổi mật khẩu bằng `set_password` nay **an toàn**: mật khẩu mới luôn có hiệu lực, và `.env` không còn có thể bị xóa trắng hay mất dòng khi ghi lỗi. Tôi thử lại đúng những cách đã làm hỏng bản cũ: 26 kiểu `.env` dựng tay và 6.000 `.env` ngẫu nhiên, 0 lỗi (bản cũ: 338 lần mật khẩu mới không có hiệu lực trên 3.000 file). Cho chương trình khác giữ file `.env` thật trên Windows theo 4 kiểu: `.env` còn nguyên từng byte, không sót file tạm, câu báo nói đúng «File .env cũ vẫn còn nguyên».
- Cách băm và cách kiểm mật khẩu không đổi; đăng nhập app vẫn đúng.
- Còn 2 điểm nhỏ Soi Lỗi đã ghi, tôi đồng ý mức Thấp và không chặn: (1) một đường rất hiếm làm câu báo nói sai nguyên nhân, file vẫn an toàn; (2) có từ trước: nếu máy có đặt **biến môi trường** `APP_PASSWORD_HASH` (phải tự đặt tay trong Windows) thì `set_password` báo đã lưu mà mật khẩu mới không dùng được. Nên sửa ở một phiếu nhỏ sau.

## Lỗi phát hiện

Không phát hiện lỗi mới.

Ý kiến về 2 lỗi Soi Lỗi đã ghi (`tests/test_soi_loi_t104.py`; chạy `--runxfail`: cả hai hỏng đúng câu kiểm):

| Mã | Mức Lá Chắn | Lý do | Khi nào sửa |
|---|---|---|---|
| SL-T104-1 (đọc lại `.env` ngay sau khi thay mà lỗi thì câu báo nói «dòng sai định dạng») | **Thấp, đồng ý** | File luôn an toàn: bộ ghi trả bản cũ rồi mới báo. Chỉ câu báo sai nguyên nhân, ở đúng khoảnh khắc chương trình khác giữ file sau `os.replace`. Cùng đường này: nếu một bộ ghi khác (trang Cài đặt lưu khóa) đổi `.env` đúng lúc đó, bước trả bản cũ đè mất thay đổi kia; hai bộ ghi vốn không khóa lẫn nhau nên lần thay sau luôn thắng (Quan sát 2), rất hiếm vì cần cùng một người làm hai việc trong cùng một lúc | Phiếu nhỏ sau (cách sửa trong báo cáo Soi Lỗi) |
| SL-T104-2 (biến môi trường `APP_PASSWORD_HASH` đè `.env`, `set_password` vẫn báo «Đã lưu») | **Thấp, đồng ý, có từ trước** (U3) | Cùng hệ quả LC-T090-1 (đổi mật khẩu không có hiệu lực, mật khẩu cũ vẫn vào được), nhưng phải tự đặt biến môi trường; tài liệu dự án không hướng dẫn cách này. Khi sửa: `env_file.overridden_by_os_environ` hiện chỉ nhận 3 tên khóa AI (`_check_name`), nên `set_password` cần xét thẳng `os.environ` (hoặc nới hàm đó cho `APP_PASSWORD_HASH`) và báo trước khi hỏi mật khẩu | Phiếu nhỏ sau |

## Kết quả theo việc Chỉ Huy giao

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| 1. LC-T090-1, -2 đóng thật | **Đóng** | 17 ca `xfail` cũ của tôi nay qua thật: `tests/test_la_chan_t090.py` **28 passed** (dòng mã băm lặp, `export`, dấu cách quanh «=», dòng trong giá trị nhiều dòng; FF, VT, RS, NEL, U+2028, U+2029 trong giá trị dòng khác; khóa chia sẻ thật bằng `LockFileEx`). Chạy lại script T-090 của tôi trên bản mới (`p_env_roundtrip.py`, chỉ đổi giá trị mã băm thử sang dạng thật vì `set_password_hash` chỉ nhận `[A-Za-z0-9_:]`): 26 ca dựng tay **0 vấn đề** (T-090: 20 ca có vấn đề); 3.000 `.env` ngẫu nhiên hạt giống 7 **0 vấn đề** (T-090: 338 lần mật khẩu mới không có hiệu lực); hạt giống 19: 0. `p_env_lock_write.py` (4 kiểu giữ file thật trên Windows, đặt đúng lúc người dùng đang gõ mật khẩu): mở cấm ghi, khóa độc quyền, **khóa chia sẻ** (T-090: `.env` thành 0 byte), ánh xạ bộ nhớ: **cả 4 giữ nguyên từng byte**, mã thoát 1 |
| 2. Ghi nguyên tử trên Windows | **Đạt** | `_atomic_write` (có từ T-020, đã kiểm ở T-016-020): `tempfile.mkstemp(prefix=".env.", suffix=".tmp", dir=thư mục của .env)` tạo file mới kiểu độc quyền (`O_EXCL`), tên ngẫu nhiên 8 ký tự (thử 5 lần: `.env.ma_v_kzl.tmp`, `.env.scyfa0l7.tmp`, …), **cùng thư mục** với `.env` (nên `os.replace` là đổi tên trong một ổ); ghi, `flush`, `fsync`, rồi `os.replace`. Quyền: Windows không dùng bit quyền kiểu POSIX (đọc ra `0o666`), file tạm nhận quyền thừa kế của thư mục như mọi file mới ở đó (Quan sát 1); Mac/Linux đặt `600` trước khi thay. `os.replace` khi `.env` đang bị giữ: mở cấm ghi, khóa chia sẻ, ánh xạ bộ nhớ: Windows từ chối thay, `.env` còn nguyên; khóa độc quyền: bước đọc bị từ chối trước khi ghi, không ghi gì; thuộc tính chỉ đọc: từ chối (Soi Lỗi thử thật). **File tạm bị dọn**: 4 ca khóa của tôi không sót file nào cạnh `.env`; 3 ca giả lỗi của Thợ Máy (tạo file tạm, `fsync`, `os.replace`) và 5 ca của Soi Lỗi (ổ đầy giữa chừng, `flush`, không tạo được file tạm, file đang mở thật, chỉ đọc thật) cũng không sót. File tạm sót khi mất điện đúng lúc ghi (`.env.*.tmp`, có cả khóa) bị `.gitignore` (`.env.*`) chặn khỏi git |
| 3. `.env` không bao giờ rỗng hay mất dòng; câu báo không lộ gì | **Đạt** | Không còn bước nào cắt file: đọc bản cũ → dựng nội dung mới bằng chính bộ tách của python-dotenv (`parse_stream`), chép nguyên văn mọi đoạn khác, thay mọi đoạn `APP_PASSWORD_HASH` → so trước khi ghi (`_parse(mới) == biến cũ + mã băm mới`, không khớp thì không ghi) → thay nguyên tử → đọc lại, sai thì trả bản cũ (cũng nguyên tử). Câu báo của mọi đường lỗi là hằng, chỉ ghép tên loại lỗi: `MSG_ENV_KEPT`, `MSG_ENV_FORMAT`, `MSG_ENV_NOT_UTF8`, `MSG_ENV_UNREADABLE`, `MSG_ENV_UNWRITABLE`, câu của bộ ghi (liên kết tắt, không phải file, dòng mã băm thiếu nháy, «Mã băm mật khẩu không đúng định dạng.», `_RESTORE_FAILED`): không mã băm, không đường dẫn, không nội dung `.env`, không câu lỗi gốc (các ca khóa thật của tôi: không đường dẫn). «File .env cũ vẫn còn nguyên» chỉ in khi lỗi xảy ra trước hoặc ngay ở `os.replace` (đúng sự thật); ca đã thay mà không trả lại được có câu riêng, không nói «còn nguyên» |
| 4. Cách băm, cách so mật khẩu không đổi; đăng nhập đúng | **Đạt** | `git diff b8ac183 8eef5cb -- seo_app/auth.py seo_app/config.py app/ .env.example`: rỗng. `set_password_hash` chỉ nhận `[A-Za-z0-9_:]{1,512}`: khớp đúng dạng `pbkdf2_sha256:lặp:muối hex:băm hex` của `hash_password`, chặn xuống dòng, dấu cách, nháy, `#`, `$`, `=` (không chèn được biến khác, không thế biến `${…}`). Test đăng nhập sau `set_password` (`load_settings` + `verify_password`) của Thợ Máy, Soi Lỗi, `test_auth.py`, `test_app.py` qua trên cây gộp |
| 5. Đổi test đúng điều kiện duyệt; gỡ `xfail` đúng R5 | **Đúng** | `tests/test_la_chan_t090.py`: chỉ xóa 3 dấu `xfail` (15 dòng), thân test, `parametrize`, `skipif` giữ nguyên. `tests/test_t090_env_bang_ma.py::test_set_password_cannot_write_env`: chỉ đổi cách giả lỗi (từ đè `Path.write_text`, ném lỗi trước khi mở file và không còn được gọi, sang ném `PermissionError` ở `os.replace` của bộ ghi, đúng chỗ Windows từ chối thật) như **Chỉ Huy B duyệt**; mọi `assert` giữ nguyên (mã thoát 1, câu cố định kèm tên loại lỗi, không đường dẫn, file giữ nguyên); lời mô tả ghi lý do |
| 6. Mức 2 `xfail` của Soi Lỗi | **Thấp cả hai** | Bảng ở mục «Lỗi phát hiện» |
| 7. Gộp thử `main` mới nhất trên máy | **Đạt** | `main` cục bộ `209615a` (Gộp T-103; `origin/main` `03d39d7` là bản cũ hơn). Gốc chung `b8ac183`; hai bên không chung file nào (`main` đổi `config/ai.toml`, `config/content.toml`, `seo_app/content/`, test T-103); `git merge-tree` cây `f03cce6`, **không xung đột**. Commit tạm `4cbe246` (không nhánh, không push), worktree nháp, 18 file (test T-104, T-090, `hash_password`, `env_file`, khóa API, Google Sheet, `test_auth.py`, `test_config.py`, `test_app.py`, `test_soi_loi_t084.py`, 3 file test T-103), 01:38:34 → 01:43:12: **1.103 passed, 10 skipped, 10 xfailed, 0 hỏng**. 10 `xfail` đều đã biết: `test_la_chan_t103.py` 5, `test_soi_loi_t097.py` 3 (SL-T097-5), `test_soi_loi_t104.py` 2 (SL-T104-1, -2) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` 1.5.0 (`PYTHONUTF8=1`, `--all-files` trong thư mục nháp): bản sao 8 file đổi (code, test, 2 báo cáo), bản vá `git log -p b8ac183..8eef5cb`, **file mồi có chữ tiếng Việt**: mồi bắt 2/2; còn lại đều là báo nhầm (mục «Báo nhầm»). Soát bản vá theo dạng khóa (`sk-ant-`, `AIza…`, `ghp_`, `PRIVATE KEY`, `xox`, `AKIA…`): 0 |
| S2 | Đạt | Không in, không log mã băm hay nội dung `.env`; câu báo là hằng (việc 3) |
| S3 | Không áp dụng | Không có biến cấu hình mới (`.env.example` không đổi) |
| W1–W4, A1–A3 | Không áp dụng | Không đụng WordPress, AI |
| U1, U2 | Không áp dụng | Không đổi giao diện |
| U3 | Đạt, kèm SL-T104-2 (có từ trước) | PBKDF2, so sánh an toàn không đổi; mã băm mới ghi vào **mọi** dòng app có thể đọc (việc 1, 4) |
| F1 | Đạt | Chỉ ghi `.env` (đường dẫn cố định) và file tạm trong cùng thư mục; không ghi xuyên liên kết tắt (`_read_env_text` từ chối, quy tắc T-016-020) |
| F2 | Không áp dụng | |
| F3 | Đạt | Đọc, ghi `encoding="utf-8"`, `newline=""` (giữ nguyên kiểu xuống dòng, BOM); ghi nguyên tử, `fsync`; python-dotenv chỉ đọc, không chạy nội dung; Quan sát 1 (quyền file trên Windows) |
| D1 | Đạt | Không thư viện mới (`pyproject.toml`, `uv.lock` không đổi) nên không chạy lại pip-audit |
| D2 | Đạt | `.gitignore` không đổi, có `.env`, `.env.*` (chặn cả file tạm sót) |
| D3 | Đạt | Test chỉ dùng `.env` giả trong thư mục tạm, `getpass` giả; bộ chặn mạng của `tests/conftest.py` vẫn bật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy: không đổi thư viện | Có |
| bandit | `PYTHONUTF8=1 uvx --offline bandit` `seo_app/env_file.py`, `scripts/hash_password.py` (593 dòng): 1 cảnh báo B105 Low (`"APP_PASSWORD_HASH"`): báo nhầm | Có |
| detect-secrets | Mồi 2/2; còn lại báo nhầm | Có. Đã xóa file mồi |
| Soát lịch sử git | Bản vá 4 commit của nhánh: 0 dạng khóa | Có |
| pytest / ruff | Nhánh: `tests/test_la_chan_t090.py` 28 passed. Cây gộp: xem việc 7. `uv run ruff check .`: All checks passed! Quét ký tự trần trong 6 file code, test đổi: 0 | Có |

## Báo nhầm đã loại

| Công cụ | Vị trí | Lý do |
|---|---|---|
| bandit B105, detect-secrets | `seo_app/env_file.py:54` (và dòng tương ứng của bản vá) | `PASSWORD_HASH_VAR = "APP_PASSWORD_HASH"` là tên biến, không phải mật khẩu |
| detect-secrets | `tests/test_t090_env_bang_ma.py:30` | Chuỗi mồi `FAKE_KEY` có từ T-090 |
| detect-secrets | `docs/team/reports/T-104-tho-may.md:53` | Chữ «detect-secrets», «Secret Keyword» trong báo cáo |

## Quan sát (không phải lỗi, không cần sửa ở phiếu này)

1. **Quyền file trên Windows (Soi Lỗi Ghi nhận 3):** `os.replace` thay bằng file tạm, nên `.env` mới mang quyền thừa kế của thư mục; quyền riêng ai đó đặt tay trên `.env` cũ (nếu có) không còn. Bộ ghi khóa API ở trang Cài đặt đã làm như vậy từ T-020. Máy của chủ dự án một người dùng, chưa thấy ai đặt quyền riêng; nếu cần thì đặt quyền cho cả thư mục app. `.env` có thuộc tính chỉ đọc thì `set_password` từ chối, câu báo đúng, file còn nguyên. Mac/Linux: `.env` mới luôn `600`, chặt hơn trước.
2. **Hai bộ ghi cùng lúc:** trang Cài đặt (lưu khóa API, mã Sheet) và `set_password` không khóa lẫn nhau; nếu cùng ghi trong cùng một lúc, lần thay sau thắng và thay đổi của bên kia mất (không hỏng file). Rất hiếm (cùng một người); README dặn tắt app trước khi đặt mật khẩu lần đầu.
3. `set_password` thành công vẫn in «Đã lưu mật khẩu mới vào {đường dẫn}» (có từ trước, ra cửa sổ của chính người dùng; đã ghi ở T-090).

## Điều kiện

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | SL-T104-1, SL-T104-2 (Thấp, Soi Lỗi): theo gợi ý trong báo cáo Soi Lỗi và bảng trên; gỡ `xfail` khi sửa (R5) | Chỉ Huy lập phiếu nhỏ (Thợ Máy) | Phiếu dọn lỗi Thấp kế tiếp; không chặn gộp |
| 2 | Kiểm lại bằng Claude Fable sau 01/11 | Lá Chắn | Khi có Fable |

Script thử (thư mục nháp của phiên; bản T-090 ở thư mục ghi chú chung `T-090-la-chan-scripts/`, chạy trong worktree `PYTHONUTF8=1 uv run python <script>`): `p_env_roundtrip.py [hạt giống] [số mẫu]` (đổi giá trị mã băm thử sang dạng `pbkdf2_sha256:600000:6d6f69:6d6f69`), `p_env_lock_write.py` (4 kiểu giữ file thật, nay in cả file sót lại cạnh `.env`).

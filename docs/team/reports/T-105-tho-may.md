# Báo cáo T-105 · `set_password`: câu báo đúng nguyên nhân khi đọc lại lỗi, cảnh báo khi biến môi trường đè `.env` (SL-T104-1, SL-T104-2)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-105](../tickets/T-105-set-password-cau-bao-bien-moi-truong.md) |
| Nhánh | `team/T-105`, từ `origin/main` `731a46e`; commit thay đổi chính `1ca123a` |
| Ngày nộp | 2026-10-31 (giờ máy, +07) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Công cụ đặt mật khẩu app (`set_password`) nay báo đúng sự thật trong hai tình huống hiếm:
  1. **Ngay sau khi ghi, phần mềm khác (diệt virus, đồng bộ thư mục) giữ file `.env`** nên không đọc lại được để kiểm. Trước đây công cụ báo nhầm «dòng sai định dạng… thiếu dấu nháy», người dùng đi tìm một lỗi không có. Nay báo đúng: không đọc lại được file để kiểm, file cũ vẫn còn nguyên, đóng chương trình đang mở file rồi chạy lại. Nếu đến bản cũ cũng không trả lại được, công cụ báo «chưa chắc đã lưu được», không nói sai là «chưa lưu».
  2. **Máy có đặt biến môi trường `APP_PASSWORD_HASH`.** App luôn ưu tiên biến này hơn file `.env`. Trước đây công cụ vẫn báo «Đã lưu mật khẩu mới» nhưng mật khẩu mới không có tác dụng, mật khẩu cũ vẫn vào được. Nay công cụ dừng ngay, trước khi hỏi mật khẩu, giải thích lý do và chỉ từng bước gỡ biến. Không in giá trị của biến.
- Trang Cài đặt (lưu khóa AI, mã Google Sheet) dùng chung bộ ghi `.env`, nên ở tình huống 1 cũng hết báo nhầm «định dạng lạ».
- Không đổi cách băm hay cách so mật khẩu. Bình thường người dùng không thấy gì khác.

## Chọn cách xử lý SL-T104-2: dừng và giải thích, không «lưu rồi nhắc»

Phiếu cho chọn một trong hai cách. Tôi chọn **từ chối kèm lý do** (dừng trước khi hỏi mật khẩu, mã thoát 1, không ghi `.env`), vì:

1. Đúng hướng Soi Lỗi và Lá Chắn T-104 đề xuất: kiểm biến môi trường và báo **trước khi hỏi mật khẩu** (`T-104-soi-loi.md` dòng SL-T104-2, `T-104-la-chan.md` bảng lỗi Soi Lỗi).
2. Người dùng không bao giờ thấy chữ «Đã lưu» khi mật khẩu chưa có hiệu lực, và không mất công gõ mật khẩu hai lần vô ích.
3. Không để lại trạng thái ngầm. Nếu «lưu rồi nhắc», `.env` sẽ mang một mật khẩu chưa dùng tới; nhiều tháng sau ai đó gỡ biến môi trường thì mật khẩu đó bỗng có hiệu lực mà không ai nhớ.
4. Sau khi gỡ biến vẫn phải tắt hẳn app đang chạy (app giữ biến đó tới khi mở lại), nên chạy lại `set_password` lúc đó không thêm bước đáng kể.

Chế độ `--print` (chỉ in mã băm để tự dán, không ghi file) vẫn chạy như cũ, kèm một lời lưu ý khi máy có biến đó.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/env_file.py` | (1) Lớp lỗi mới `EnvFileReadBackError` (con của `EnvFileError`), kèm `error_name` (tên loại lỗi) và `restored` (đã bỏ được bản vừa ghi hay chưa). (2) `_write_value`: sau `os.replace`, đọc lại **không được** (bị giữ, đổi bảng mã, file vừa ghi biến mất, bị thay bằng liên kết tắt) thì bỏ bản vừa ghi rồi ném `EnvFileReadBackError`. Chỉ khi đọc lại **được** mà nội dung khác mới ném `EnvFileFormatError` như cũ. Hai hàm phụ `_read_error_name`, `_discard_written` (trả bản cũ, hoặc xóa file vừa tạo khi trước đó chưa có `.env`). Hai câu chung `_READBACK_RESTORED` / `_READBACK_UNSURE` (trang Cài đặt hiện `str(exc)`). (3) Hàm `password_hash_overridden(environ=None)`: biến `APP_PASSWORD_HASH` **có mặt** trong biến môi trường (kể cả rỗng), đúng điều kiện `load_settings` dùng (`config.py`: `values.update({name: env[name] for name in ENV_VARS if name in env})`). Chỉ trả đúng/sai. Viết hàm riêng vì `overridden_by_os_environ` bị test cũ ghim là chỉ nhận tên khóa AI (`test_env_file.py`, `test_other_names_rejected`). (4) Docstring đầu module: sửa câu đã sai từ T-104 («không biến nào khác sửa được qua đây», trong khi module có `set_password_hash`), thêm một đoạn về mã băm mật khẩu |
| `scripts/hash_password.py` | Câu cố định mới: `MSG_ENV_READBACK` (đã bỏ bản vừa ghi, «File .env cũ vẫn còn nguyên»), `MSG_ENV_READBACK_UNSURE` (không bỏ được bản vừa ghi), `MSG_ENV_OVERRIDDEN` (3 bước gỡ biến), `MSG_PRINT_OVERRIDDEN`. Lớp `UnsureSaveError` (con của `ConfigError`) để `main` in «Chưa chắc đã lưu được mật khẩu mới.» thay cho «Chưa lưu mật khẩu mới.». `main`: có biến môi trường thì dừng **trước** bước kiểm `.env` và trước khi hỏi mật khẩu; `--print` vẫn in mã băm rồi thêm lời lưu ý |
| `tests/test_t105_set_password.py` | Mới, 16 hàm test, 28 ca (2 ca chỉ chạy trên Windows, dùng khóa file thật) |
| `tests/test_soi_loi_t104.py` | Gỡ 2 dấu `xfail(strict=True)` (SL-T104-1, SL-T104-2) sau khi cả hai XPASS. Chỉ xóa 2 khối trang trí, không đổi thân test hay điều kiện kiểm (R5) |
| `docs/team/reports/T-105-tho-may.md` | Báo cáo này |

Không đụng cách băm, so mật khẩu (`seo_app/auth.py`), `seo_app/config.py`, `app/**`.

```
$ git diff --stat 731a46e..1ca123a
 scripts/hash_password.py        |  62 +++++-
 seo_app/env_file.py             |  93 +++++++--
 tests/test_soi_loi_t104.py      |  10 -
 tests/test_t105_set_password.py | 445 ++++++++++++++++++++++++++++++++++++++++
 4 files changed, 586 insertions(+), 24 deletions(-)
```

Cộng thêm báo cáo này (commit sau). Gộp thử: `origin/main` vẫn ở `731a46e` (gốc nhánh), `git merge-tree --write-tree origin/main HEAD` không xung đột.

## Câu báo người dùng thấy (mới)

| Tình huống | Câu (in ra màn hình `set_password`) |
|---|---|
| Đọc lại lỗi, đã trả bản cũ | «Chưa lưu mật khẩu mới. Không đọc lại được file .env để kiểm sau khi ghi (PermissionError) nên đã bỏ bản vừa ghi. File .env cũ vẫn còn nguyên. Đóng chương trình đang mở file (ví dụ phần mềm diệt virus hay đồng bộ thư mục) rồi chạy lại set_password.» |
| Đọc lại lỗi, trả bản cũ cũng lỗi | «Chưa chắc đã lưu được mật khẩu mới. Không đọc lại được file .env để kiểm sau khi ghi (PermissionError), cũng không bỏ được bản vừa ghi: file .env có thể đã mang mật khẩu mới nhưng chưa được kiểm. Đóng chương trình đang mở file (…) rồi chạy lại set_password để ghi lại cho chắc.» |
| Máy có biến môi trường `APP_PASSWORD_HASH` | «Chưa đặt được mật khẩu. Máy này đang có biến môi trường APP_PASSWORD_HASH (một cài đặt của Windows hay Mac, nằm ngoài file .env). App luôn dùng giá trị trong biến đó trước file .env, nên mật khẩu mới ghi vào .env sẽ không có hiệu lực.» rồi «Cách sửa:» 3 bước: gỡ biến (đường đi trong Windows, Mac), tắt hẳn app nếu đang chạy, chạy lại set_password |
| `--print` khi máy có biến đó | Vẫn in mã băm, thêm «Lưu ý: máy này đang có biến môi trường APP_PASSWORD_HASH…» |
| Trang Cài đặt (khóa AI, mã Sheet), đọc lại lỗi | «Không đọc lại được file .env để kiểm sau khi ghi (…) nên đã bỏ bản vừa ghi, file .env vẫn như trước khi lưu. Đóng chương trình đang mở file .env (…) rồi thử lại.» (trước: «File .env có định dạng lạ…») |

Mọi câu đều cố định: chỉ chèn tên loại lỗi, không đường dẫn, không nội dung `.env`, không giá trị biến, không traceback (có test kiểm).

## Bằng chứng

```
# 1. Gốc 731a46e, trước khi sửa: 2 ca của Soi Lỗi còn xfail
$ uv run pytest tests/test_soi_loi_t104.py -q -rxX -k "readback_failure or os_environment"
XFAIL tests/test_soi_loi_t104.py::test_readback_failure_message_tells_the_real_cause - SL-T104-1: …
XFAIL tests/test_soi_loi_t104.py::test_os_environment_hash_is_reported - SL-T104-2 (có từ trước): …
23 deselected, 2 xfailed in 7.15s

# 2. Đã sửa mã, dấu xfail còn nguyên: cả hai XPASS (strict nên báo hỏng, đúng mong đợi)
$ uv run pytest tests/test_t105_set_password.py tests/test_soi_loi_t104.py -q -rfEsxX
[XPASS(strict)] SL-T104-1: …
[XPASS(strict)] SL-T104-2 (có từ trước): …
2 failed, 51 passed in 25.87s          (51 = 28 ca mới + 23 ca cũ của Soi Lỗi)

# 3. Gỡ 2 dấu (chỉ xóa dấu), chạy 21 file test liên quan (danh sách dưới)
$ uv run pytest <21 file> -q -rfEsxX
1259 passed, 10 skipped in 520.97s     (lượt 1, trước 3 sửa nhỏ tự soát)
1259 passed, 10 skipped in 357.80s     (lượt cuối, đúng bản commit 1ca123a: mã băm 4 file
                                        trùng nhau lúc đầu, lúc cuối lượt chạy và lúc commit)

$ uv run ruff check .                   # ruff 0.16.10
All checks passed!

# 4. Chạy thật script, máy có biến APP_PASSWORD_HASH (giá trị giả), worktree không có .env
$ APP_PASSWORD_HASH=gia-tri-gia-T105 uv run python scripts/hash_password.py
Chưa đặt được mật khẩu. Máy này đang có biến môi trường APP_PASSWORD_HASH (một cài đặt của
Windows hay Mac, nằm ngoài file .env). App luôn dùng giá trị trong biến đó trước file .env, nên
mật khẩu mới ghi vào .env sẽ không có hiệu lực.
Cách sửa:
1. Gỡ biến APP_PASSWORD_HASH khỏi máy. Windows: bấm Start, gõ «environment variables» (Windows
   tiếng Việt: «biến môi trường»), mở «Edit environment variables for your account» (…), chọn dòng
   APP_PASSWORD_HASH, bấm Delete rồi OK; không thấy dòng đó thì có thể nó nằm ở phần biến của hệ
   thống (cần quyền quản trị). Mac: xóa dòng có APP_PASSWORD_HASH trong file ~/.zshrc.
2. Nếu app đang chạy: tắt hẳn app (đóng cửa sổ đen hay Terminal của app).
3. Chạy lại set_password.
mã thoát = 1                            (không hỏi mật khẩu, không in giá trị biến, không tạo .env)

# 5. Quét bí mật (S1), PYTHONUTF8=1
$ PYTHONUTF8=1 uvx detect-secrets scan scripts/hash_password.py seo_app/env_file.py \
    tests/test_t105_set_password.py tests/test_soi_loi_t104.py docs/team/reports/T-105-tho-may.md
seo_app/env_file.py:58  Secret Keyword  (báo nhầm, có từ trước: tên biến PASSWORD_HASH_VAR;
                                         bản main cũng bị báo ở dòng 54)
```

- File mồi có chữ tiếng Việt, một khóa AWS giả và một dòng `…password = "…"` giả, đặt trong thư mục nháp của phiên: `detect-secrets` bắt đủ **2/2**, đã xóa file mồi ngay.
- Lần quét đầu, test mới bị báo nhầm một dòng so mã băm app đọc được với chữ giả «khac». Đã viết lại phép so qua một biến trung gian; quét lại không còn. Bản đầu của báo cáo này cũng bị báo nhầm 4 dòng (tên hàm, tên file có chữ «password» đứng cạnh chữ khác trong dấu `` ` ``); đã viết lại câu, quét lại sạch.

**21 file test liên quan:**

| Nhóm | File |
|---|---|
| Phiếu này | `test_t105_set_password.py` (mới), `test_soi_loi_t104.py` (đã gỡ 2 dấu) |
| `set_password` cũ (T-104, T-090, Giai đoạn 0) | `test_t104_set_password.py`, `test_t090_env_bang_ma.py`, `test_soi_loi_t090.py`, `test_la_chan_t090.py`, `test_hash_password_script.py`, `test_soi_loi_t003_t009.py` (nạp script) |
| Bộ ghi `.env` dùng chung và trang Cài đặt | `test_env_file.py`, `test_soi_loi_t016_t020.py`, `test_soi_loi_t021_t017.py`, `test_settings_keys.py`, `test_soi_loi_t023.py`, `test_t101_settings_google.py`, `test_google_sheets.py`, `test_soi_loi_t097.py`, `test_la_chan_t097.py` |
| Cấu hình, đăng nhập, app | `test_auth.py`, `test_config.py`, `test_app.py`, `test_soi_loi_t084.py` |

10 mục bỏ qua đều có từ trước, do Windows: quyền `600` kiểu Mac/Linux (`test_env_file.py:291`, `test_soi_loi_t016_t020.py:333`), tạo symlink cần quyền đặc biệt (`test_env_file.py:592` ×2, `:613`; `test_soi_loi_t016_t020.py:232` ×2, `:260`, `:273` ×2). 2 ca khóa file thật của `test_t105_set_password.py` **có chạy** trên máy này (Windows).

**Các ca test mới chính:**

| Ca | Kiểm gì |
|---|---|
| `test_readback_failure_tells_real_cause_and_old_file_kept` | Đúng câu cố định; không «sai định dạng», «định dạng lạ», «dấu nháy»; file giữ nguyên từng byte; không sót file tạm; mật khẩu cũ vẫn có hiệu lực |
| `test_readback_failure_is_its_own_error_not_format` ×4 | Bị giữ, đổi bảng mã, file vừa ghi biến mất, bị thay bằng liên kết tắt: đều ra `EnvFileReadBackError` (không phải `EnvFileFormatError`), đúng tên loại lỗi, `restored=True`, file giữ nguyên |
| `test_readback_and_restore_both_fail_never_claims_old_file_kept` | Trả bản cũ cũng lỗi: «Chưa chắc đã lưu được…», không «còn nguyên», không «Chưa lưu…»; thật vậy mật khẩu mới đang có hiệu lực |
| `test_real_lock_during_readback_only`, `test_real_lock_after_replace_until_end` | Khóa file **thật** của Windows (`msvcrt`, không giả lỗi): khóa đúng lúc đọc lại rồi nhả (ra câu «còn nguyên»); khóa từ sau `os.replace` tới cuối (ra câu «chưa chắc», nhả khóa ra thì đúng bản mới đang trên đĩa) |
| `test_readback_mismatch_still_reported_as_format` | Canh: đọc lại được mà khác vẫn là `MSG_ENV_FORMAT` như cũ |
| `test_settings_page_writer_gets_true_message_without_old_file`, `test_new_file_that_cannot_be_removed_is_not_reported_as_kept` | Bộ ghi dùng chung (trang Cài đặt), chưa có `.env`: xóa được thì «vẫn như trước khi lưu», xóa không được thì không nói vậy; câu không chứa khóa |
| `test_overridden_matches_how_app_reads` ×5 | `password_hash_overridden` khớp đúng `load_settings`: không có biến, có giá trị, rỗng, chỉ dấu cách, biến khác |
| `test_set_password_stops_before_asking_when_env_var_set` ×2 | Biến là mã băm cũ hoặc rỗng: dừng trước khi hỏi mật khẩu, mã thoát 1, đúng câu cố định, không in giá trị, `.env` giữ nguyên; gỡ biến rồi chạy lại thì đặt được và có hiệu lực |
| `test_print_mode_with_env_var_prints_hash_and_note`, `…_without_env_var_has_no_note` | `--print` vẫn in mã băm; chỉ khi có biến mới thêm lời lưu ý |

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1 (SL-T104-1): phân biệt «không đọc lại được file» với «dòng sai định dạng»; câu tiếng Việt cố định, đúng nguyên nhân, không đường dẫn, không traceback (`seo_app/env_file.py` hàm `_write_value`, lớp `EnvFileReadBackError`; trong `scripts/hash_password.py` có hai câu `MSG_ENV_READBACK` và `MSG_ENV_READBACK_UNSURE`; test ở mục Bằng chứng)
- [x] Yêu cầu 2 (SL-T104-2): chọn **từ chối kèm lý do**, lý do ở mục riêng; câu dễ hiểu, có các bước; không in giá trị biến (hàm `password_hash_overridden` và câu `MSG_ENV_OVERRIDDEN`; test `test_set_password_stops_before_asking_when_env_var_set`)
- [x] Yêu cầu 3: test cho cả hai (28 ca mới); 2 ca `xfail` XPASS rồi gỡ dấu (chỉ xóa dấu, R5); test T-090, T-104 cũ qua hết, không đổi test cũ nào khác
- [x] Test liên quan (21 file): 1259 passed, 10 skipped, 0 hỏng; `uv run ruff check .` sạch; `detect-secrets` (`PYTHONUTF8=1`): không có bí mật mới
- [x] U3: không đổi cách băm, cách so mật khẩu (`seo_app/auth.py` không đụng); mật khẩu chỉ được báo «đã lưu» khi đã ghi và kiểm được. F3: đọc/ghi `.env` vẫn `encoding="utf-8"` qua bộ ghi cũ; không `eval`, `pickle`
- [x] Báo cáo nộp tại `docs/team/reports/T-105-tho-may.md`
- [ ] Toàn bộ `uv run pytest` trên Windows: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Đổi hành vi nhỏ ở một ca lỗi kép, cùng hàm `_write_value`.** Ca này là: trước đó chưa có `.env`, đọc lại thấy khác, mà xóa file vừa tạo cũng lỗi. Trước đây lỗi xóa bị bỏ qua lặng lẽ rồi báo «định dạng lạ… (đã giữ nguyên file cũ)», sai vì file hỏng vẫn còn. Nay báo `_RESTORE_FAILED` («không trả lại được bản cũ…, hãy mở .env kiểm tra») như ca có file cũ. Có test `test_mismatch_new_file_that_cannot_be_removed_is_not_reported_as_kept`. Ca đọc lại thấy khác mà trả bản cũ lỗi (`test_restore_failure_is_not_reported_as_unchanged` của T-104) giữ nguyên câu. Lỗi đó nay không còn nối chuỗi `from exc` (chỉ ảnh hưởng thông tin gỡ lỗi nội bộ, không hiện cho người dùng).
- **Tên mục cài đặt Windows trong câu dặn gỡ biến.** «Edit environment variables for your account» là tên chuẩn trên Windows tiếng Anh. Tên tiếng Việt «Chỉnh sửa biến môi trường cho tài khoản của bạn» và từ khóa «biến môi trường» là suy luận, chưa thử trên máy Windows tiếng Việt.
- **Đọc lại lỗi vẫn bắt người dùng chạy lại.** Bộ ghi không tự thử đọc lại lần nữa. Nếu phần mềm diệt virus hay giữ file trong khoảnh khắc ngắn, người dùng sẽ gặp câu báo (nay đã đúng) nhiều hơn mức cần thiết (xem Đề xuất).
- **Máy dùng `uv` với `UV_ENV_FILE` trỏ vào `.env`** (uv tự nạp `.env` vào biến môi trường) thì `APP_PASSWORD_HASH` luôn có mặt, nên `set_password` sẽ luôn dừng. Dự án không dùng cách này: `set_password.bat`, `set_password.command`, `run.bat`, `run.command` gọi `uv run` không kèm `--env-file`.
- Quan sát 2 của Lá Chắn T-104 (hai bộ ghi cùng lúc, lần thay sau thắng) giữ nguyên, ngoài phạm vi phiếu.
- `detect-secrets` báo `seo_app/env_file.py:58` (dòng khai báo hằng chứa tên biến mật khẩu, không có giá trị bí mật). Mục này có từ trước: bản trên `main` bị báo ở dòng 54, dời 4 dòng vì đoạn docstring thêm vào.

## Đề xuất

- **Họa Sĩ hoặc Chỉ Huy (Thấp, ngoài phạm vi `app/**`):** thẻ Google Sheet ở trang Cài đặt cảnh báo biến môi trường bằng `os.environ.get(GOOGLE_SHEET_VAR, "").strip()` (`app/views/settings.py:609`). Trong khi đó `load_settings` coi biến **có mặt**, kể cả rỗng, là đè `.env` (`seo_app/config.py`, dòng `values.update(...)`). Biến rỗng thì app bỏ mã Sheet trong `.env` mà trang không cảnh báo. Nên kiểm theo điều kiện «có mặt» như `password_hash_overridden`.
- **Thư Ký (tùy chọn):** thêm một dòng vào bảng xử lý sự cố của README cho câu «Máy này đang có biến môi trường APP_PASSWORD_HASH…».
- **Phiếu nhỏ sau, nếu gặp thật:** cho bộ ghi thử đọc lại vài lần (ví dụ 3 lần, cách 0,2 giây) trước khi bỏ bản vừa ghi, để giảm số lần phải chạy lại vì phần mềm diệt virus giữ file chốc lát.

## Câu hỏi cho chủ dự án

Không có.

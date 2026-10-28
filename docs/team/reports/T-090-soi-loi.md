# Báo cáo T-090 · Dọn lỗi Thấp: câu báo emoji mới trong chữ SEO (SL-T041-8), `.env` không phải UTF-8 (SL-T084-1) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-090](../tickets/T-090-don-loi-thap-chu-seo-va-env.md) |
| Ngày nộp | 2026-10-28 |
| Nhánh | `team/T-090` (kiểm đầu nhánh `97fc800`, code lượt 2 `52ce068`, gốc `main` `1e49185`) |
| Kết quả | Hoàn thành (kiểm rút gọn cả 2 lượt). **Kết luận: ĐẠT, chuyển Lá Chắn rút gọn được ngay.** SL-T041-8, SL-T084-1 **đã sửa thật**; câu báo FAQ và `set_password` (lượt 2) đúng. Lỗi mới: **0** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp); **không lỗi nào phải sửa trước Lá Chắn**. Soát R5: đạt. Ca hỏng `test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` ở lượt 2 của Thợ Máy là **hỏng oan** (chạy riêng 3/3 qua) |

## Tóm tắt (cho chủ dự án)

- Tiêu đề, mô tả SEO có **biểu tượng cảm xúc rất mới** vẫn bị chặn như đã chốt, nay câu báo nói đúng «phần mềm chưa nhận ra ký tự này (có thể là biểu tượng cảm xúc rất mới)», kể cả khi biểu tượng đó nằm trong biểu tượng ghép, lặp lại, ở đầu hay cuối câu. Biểu tượng quen (kể cả loại mới nhất phần mềm đã biết, cờ, màu da, biểu tượng ghép) và tiếng Việt (gõ kiểu nào cũng vậy) không bị chặn oan. Mục Hỏi đáp báo đúng câu nào, loại ký tự nào.
- File `.env` lưu sai bảng mã (Notepad «ANSI», UTF-16, hay có byte hỏng ở bất cứ dòng nào) hoặc **đang bị chương trình khác khóa**: app mở ra trang báo lỗi tiếng Việt chỉ cách sửa, không còn lỗi tiếng Anh kèm đường dẫn máy; sửa xong tải lại trang là vào được. Bấm `set_password` lúc đó cũng báo ngay bằng tiếng Việt, chưa bắt gõ mật khẩu, không đụng vào file.
- Không tìm thấy lỗi mới.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t090.py` | Mới: 28 ca (đều qua). Dùng lại hàm giúp của `tests/test_hash_password_script.py`, `tests/test_settings_images.py` |
| `docs/team/reports/T-090-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng việc được giao

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| Emoji mới, ký tự chưa gán vẫn Chặn với câu đúng | **Đạt** | Test Thợ Máy (103 ca lượt 1), test Lá Chắn `test_sl8_new_emoji_stays_blocked_with_accurate_message` (gỡ `xfail`), test Soi Lỗi T-041 đã đổi theo quyết định giữ Chặn: qua. Thêm (`test_new_emoji_in_sequences_blocked_with_one_new_message` × 7): emoji Unicode 16 kèm VS16, trong chuỗi ghép ZWJ (trước, sau emoji quen), lặp 3 lần, hai emoji mới khác nhau, ở đầu, ở cuối (sát đuôi « \| Pro-Metal»): title (có và không đuôi), description đều Chặn, **đúng một** câu «chưa nhận ra», không kèm «không nhìn thấy», không chép lại ký tự. Quét cả bảng mã (1.114.112 mã, script tạm): `has_odd_chars` và `odd_char_kinds` thấy đúng cùng các ký tự, 0 khác biệt |
| Ký tự điều khiển, vô hình vẫn câu cũ | **Đạt** | Test Thợ Máy (84 ca meta, 162 ca FAQ: Cc, Cs, Co, đủ 66 «không phải ký tự», mã để dành cho ký tự vô hình) qua; FAQ nhiều câu (`test_faq_messages_name_the_right_question_and_kind`): ký tự ESC ở «Câu hỏi 2» ra câu cũ có «không nhìn thấy», emoji mới ở «Trả lời 3» ra câu mới; đúng số thứ tự, câu khác không bị báo |
| Không chặn oan emoji cũ và tiếng Việt | **Đạt** | `test_known_emoji_not_blocked_as_odd` × 11: emoji Unicode 15.0 (mới nhất Python 3.12 biết: mặt rung, tim hồng, ngỗng, nai), chuỗi ghép (phượng hoàng, gia đình, tim lửa), màu da, cờ Việt Nam, phím số, ⭐ ✅: không câu báo ký tự lạ, không Chặn. `test_vietnamese_all_tones_not_blocked` (NFC, NFD: «Ống đồng ửng đỏ, ầm ĩ, ẵm ỹ, ợ ụ ữ, Đà Nẵng…»): không câu báo |
| Câu FAQ đồng bộ, tập ký tự bị Chặn không đổi | **Đạt** | Dùng chung `odd_char_kinds` với ô meta. Quét **cả** bảng mã trên chữ đã chuẩn hóa (`normalize_text("a{ký tự}b")`), so cách cũ (Cc/Cs/Co/Cn) với cách mới: 0 khác biệt (12 giây; test canh của Thợ Máy quét mỗi 11 mã một) |
| `.env` ANSI, UTF-16, BOM, rỗng, không đọc được: câu tiếng Việt cố định, không traceback, không đường dẫn, không nội dung `.env`, app vẫn mở trang báo lỗi rõ | **Đạt** | Test Thợ Máy (cp1252, cp1258, UTF-16 LE/BE có BOM, UTF-8 có BOM, lỗi quyền giả) và test Soi Lỗi T-084 `test_env_file_not_utf8_fixed_message_no_traceback` (gỡ `xfail`) qua. Thêm (`test_app_error_page_for_other_bad_bytes` × 4): surrogate mã hóa kiểu CESU-8, mã hóa dài thừa, một byte hỏng nằm trong dòng chú thích sau 80 dòng đúng, chữ cp1258 tiếng Việt: đúng một khung lỗi là câu cố định, không ô mật khẩu, không «Traceback», «codec», «byte», «position», «Errno», tên biến, đường dẫn thư mục app, thư mục tạm, thư mục nhà. `.env` **bị khóa thật** (khóa vùng byte của Windows, như chương trình khác đang giữ file; `test_app_with_env_locked_by_other_program_then_unlocked`): trang báo «Không đọc được file .env (PermissionError)…»; mở khóa, tải lại: màn đăng nhập, đăng nhập được. Thử tay: `.env` rỗng (0 byte) đọc như không có biến, app ra màn đăng nhập bình thường |
| `set_password` cũng vậy | **Đạt** | Test Thợ Máy (4 bảng mã, lỗi đọc, ghi, chép mẫu giả, `--print`) qua. Thêm: `.env` bị khóa thật (`test_set_password_with_env_locked_stops_before_asking`): báo ngay câu cố định kèm tên loại lỗi, **không** gọi ô gõ mật khẩu, file giữ nguyên từng byte, không đường dẫn, không traceback; mở khóa chạy lại thì lưu được, app đọc được mã băm mới. `.env` «UTF-8 with BOM» mà dòng `APP_PASSWORD_HASH` nằm ngay dòng đầu (`test_set_password_bom_hash_on_first_line`): đặt xong đăng nhập được bằng mật khẩu mới (xem Ghi nhận 1) |
| Gỡ `xfail` đúng R5 | **Đạt** | Mục «Soát R5» |
| Ca hỏng ở lượt 2 của Thợ Máy | **Hỏng oan** | `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` chạy riêng 3 lần: 3 qua, bước gọi 9,16 / 9,18 / 9,32 giây trong khi khóa chỉ giữ 10 giây (còn dư dưới 1 giây, máy bận là vượt). Không liên quan phần sửa (T-090 không đụng `seo_app/storage/site_index.py`) |

## Lỗi tìm thấy

Không có lỗi mới.

## Ghi nhận (không phải lỗi của T-090)

1. **Có từ trước:** `set_password` tìm dòng `APP_PASSWORD_HASH=` sau `strip()`, mà BOM (U+FEFF) không phải khoảng trắng, nên với `.env` «UTF-8 with BOM» có dòng đó ngay đầu file, dòng cũ (có BOM phía trước) không được thay, dòng mới thêm vào cuối. App vẫn đúng (python-dotenv bỏ BOM, dòng sau cùng thắng: đăng nhập được bằng mật khẩu mới), chỉ để lại một dòng mã băm cũ thừa. Phiếu dọn sau có thể bỏ BOM khi so tên biến.
2. `.env` là **thư mục** (gần như không gặp): app coi như chưa có `.env` (`is_file()` sai), còn `set_password` báo «Không đọc được file .env (PermissionError)…», hơi lệch nghĩa. Không cần sửa.
3. **Đã biết (Góp ý G7 của Soi Lỗi T-041, đúng thiết kế T-036/T-042):** `normalize_meta` bỏ dấu nối ZWJ (U+200D) và VS16 (U+FE0F, qua `IGNORABLE_NOT_CF`) nên emoji ghép bị tách khi chép, ghi (gia đình thành ba người riêng, tim lửa thành tim và lửa, 1️⃣ mất VS16) mà không Chặn, không báo. Khác với lý do giữ Chặn emoji mới («cho qua là lặng lẽ mất khi ghi»); Chỉ Huy, Lá Chắn có thể muốn một câu Cảnh báo ở phiếu sau.
4. `.env` UTF-16 **không** BOM chỉ có chữ không dấu: đọc như UTF-8 (có ký tự NUL), biến bị đọc sai tên. Đồng ý với mục «Rủi ro» của Thợ Máy (Notepad luôn ghi BOM cho UTF-16).
5. Câu `MSG_ENV_UNREADABLE` có tên loại lỗi tiếng Anh (ví dụ «PermissionError»), như câu của `seo_app/env_file.py`; chấp nhận được.
6. Đề nghị (Soi Lỗi, phiếu nhỏ): `test_r2_long_lock_in_other_thread_is_busy_not_deleted` giữ khóa 30 giây thay cho 10 giây để không hỏng oan khi máy bận (chỉ đổi thời gian giữ khóa, không đổi câu kiểm).

## Soát R5

- `tests/test_la_chan_t041.py`, `tests/test_soi_loi_t084.py`: `git diff 1e49185..97fc800` chỉ xóa 4 dòng `@pytest.mark.xfail(...)` mỗi file, thân test không đổi.
- `tests/test_soi_loi_t041.py`: `test_sl_t041_8_new_emoji_is_not_blocked` thành `test_sl_t041_8_new_emoji_is_blocked_with_accurate_message`, theo quyết định giữ Chặn của Lá Chắn T-041, **Chỉ Huy B duyệt** (tin giao T-090): vẫn kiểm client WordPress ghi được chữ đó, thêm kiểm chữ ghi đi mất emoji, title và description phải Chặn, câu có «chưa nhận ra», không có «không nhìn thấy». Không nới.
- `tests/test_t041_meta.py`, `tests/test_t041_schema.py` (của Thợ Máy): chỉ ca U+0378 (chưa gán, cùng nhóm emoji mới) đổi câu mong đợi sang «chưa nhận ra»; vẫn đủ ca, vẫn Chặn, vẫn kiểm không chép lại ký tự, không JSON-LD, chép SiteSEO bị từ chối. Không nới.
- Không `skip` mới (các `skipif` emoji Unicode 16 chỉ bỏ qua trên Python đã biết Unicode 16), không xóa test.

## U1, U2, S1 (soát nhanh)

- U1: câu mới là câu cố định; `app/main.py` hiện `st.error(str(exc))` với câu cố định (không chữ lấy từ `.env`); không thêm `unsafe_allow_html`.
- U2: không đổi trang, đăng nhập, `.streamlit/config.toml`.
- S1: câu báo `.env` không có khóa, mật khẩu, nội dung file hay câu lỗi gốc (test kiểm cả trang); `set_password` không in đường dẫn khi lỗi, không ghi đè `.env` khi đọc lỗi.
- Test không gọi mạng thật; `.env` chỉ là file giả trong thư mục tạm.

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest -rxXfs tests/test_onpage_meta.py tests/test_t041_meta.py \
    tests/test_soi_loi_t036.py tests/test_t090_meta_emoji_moi.py tests/test_t090_env_bang_ma.py \
    tests/test_config.py tests/test_config_tolerance.py tests/test_env_file.py \
    tests/test_onpage_schema.py tests/test_t041_schema.py tests/test_soi_loi_t038.py \
    tests/test_hash_password_script.py tests/test_app_pages.py tests/test_la_chan_t041.py \
    tests/test_soi_loi_t041.py tests/test_soi_loi_t084.py tests/test_t041_seo_ui.py \
    tests/test_soi_loi_t090.py
1565 passed, 4 skipped, 5 xfailed in 440.72s (0:07:20)   # code 52ce068 (đầu nhánh 97fc800)
# 0 hỏng, 0 XPASS. 5 xfail có sẵn trên main: test_soi_loi_t036.py SL-T036-10 (1), SL-T036-11 (4).
# 4 bỏ qua có sẵn trong test_env_file.py (quyền 600 chỉ Mac/Linux, symlink cần quyền đặc biệt).

$ uv run pytest tests/test_soi_loi_t090.py      # bản commit da3fb12
28 passed in 29.06s

$ uv run pytest "tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted" \
    --durations=1                                  # 3 lần liên tiếp
1 passed (call 9.16s) · 1 passed (call 9.18s) · 1 passed (call 9.32s)

# Script tạm quét cả bảng mã (1.114.112 mã), trong scratchpad của phiên:
FAQ full scan: 0 khác biệt (12s)   # Cc/Cs/Co/Cn trên normalize_text("a{ký tự}b") so với odd_char_kinds
meta full scan: 0 khác biệt        # has_odd_chars so với odd_char_kinds
load_settings / set_password khi .env bị khóa thật (msvcrt): câu cố định, set_password thoát 1

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t090.py docs/team/reports/T-090-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Không đọc `.env` thật.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Emoji mới, ký tự chưa gán vẫn Chặn với câu đúng; ký tự điều khiển, vô hình vẫn câu cũ; không chặn oan emoji cũ và tiếng Việt; câu FAQ đồng bộ.
- [x] `.env` ANSI, UTF-16, BOM, rỗng, không đọc được (cả khóa thật): câu tiếng Việt cố định, không traceback, không đường dẫn, không nội dung `.env`, app mở trang báo lỗi rõ; `set_password` cũng vậy.
- [x] Gỡ `xfail` đúng R5; ca hỏng `test_soi_loi_t037` là hỏng oan.
- [x] Không lỗi mới (không cần test `xfail`); không sửa code ứng dụng.
- [x] Test liên quan và `ruff` (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.

## Đề xuất

- **Soi Lỗi (phiếu nhỏ):** Ghi nhận 6.
- **Phiếu dọn sau (nếu Chỉ Huy muốn):** Ghi nhận 1 (`set_password` bỏ BOM khi so tên biến), Ghi nhận 3 (câu Cảnh báo cho emoji ghép bị tách).

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-090 · Dọn lỗi Thấp: câu báo emoji mới trong chữ SEO (SL-T041-8), `.env` không phải UTF-8 (SL-T084-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-090](../tickets/T-090-don-loi-thap-chu-seo-va-env.md) |
| Nhánh | `team/T-090` (worktree `D:\ProMetal-ToolSEO\wt-T-090`), gốc `main` `1e49185` |
| Ngày nộp | 2026-10-28 08:30 (+0700); lượt 2: 2026-10-28 10:26 (+0700) |
| Kết quả | Hoàn thành (yêu cầu 1–3). Không cần sửa `app/**`: `app/main.py` đã hiện câu của `ConfigError` thành trang báo lỗi. Lượt 2: làm đề xuất 2 (câu báo FAQ) và 3 (`set_password`), mục [«Lượt 2»](#lượt-2--đề-xuất-2-và-3-2026-10-28) |

## Tóm tắt (cho chủ dự án)

- Tiêu đề hay mô tả SEO có **biểu tượng cảm xúc rất mới** (ra năm 2024, ví dụ 🫩, phần mềm chưa nhận ra) vẫn bị «Chặn» như trước, vì cho qua thì biểu tượng đó sẽ **mất** khi ghi lên website. Nhưng câu báo nay nói đúng: «Meta title có ký tự phần mềm chưa nhận ra nên không ghi được (có thể là biểu tượng cảm xúc rất mới). Xóa ký tự đó hoặc thay bằng chữ thường, biểu tượng quen thuộc.», thay cho câu cũ nói ký tự «không nhìn thấy». Biểu tượng quen (⭐ ✅ ❤️) vẫn dùng được như cũ.
- File `.env` lỡ lưu **sai bảng mã** (Notepad lưu kiểu «ANSI», hay UTF-16): app không còn hiện lỗi tiếng Anh dài kèm đường dẫn thư mục trên máy, mà hiện trang báo lỗi tiếng Việt chỉ cách sửa: mở `.env`, chọn Lưu thành (Save As), ở ô Mã hóa (Encoding) chọn UTF-8, lưu đè rồi mở lại app. Lưu lại xong, tải lại trang là ra màn đăng nhập. `.env` có mà không mở được (đang bị khóa, không có quyền đọc) cũng có câu báo tiếng Việt riêng.
- Không đổi gì khác: ký tự điều khiển, ký tự vô hình vẫn bị chặn với câu cũ; `.env` lưu UTF-8 (kể cả «UTF-8 with BOM») đọc như cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/onpage/meta.py` | `odd_char_messages(name, text)` mới (`:134`): câu báo Chặn theo loại ký tự lạ, mỗi loại một câu; `_may_be_new_symbol` mới (`:123`); `_check_text` dùng nó (`:189`) thay cho một câu chung. Không đổi `has_odd_chars`, `normalize_meta`, mức Chặn |
| `seo_app/config.py` | Câu cố định `MSG_ENV_NOT_UTF8`, `MSG_ENV_UNREADABLE` (`:44`, `:48`); `_read_env_file` mới (`:154`): bắt `UnicodeDecodeError`, `OSError` khi đọc `.env`, ném `ConfigError`; `load_settings` gọi nó (`:121`) |
| `tests/test_t090_meta_emoji_moi.py` | Mới: 8 hàm, 103 ca (mục «Test mới») |
| `tests/test_t090_env_bang_ma.py` | Mới: 6 hàm, 12 ca |
| `tests/test_la_chan_t041.py` | Gỡ 4 dòng `@pytest.mark.xfail(...)` của `test_sl8_new_emoji_stays_blocked_with_accurate_message` (2 ca). Thân test không đổi |
| `tests/test_soi_loi_t084.py` | Gỡ 4 dòng `@pytest.mark.xfail(...)` của `test_env_file_not_utf8_fixed_message_no_traceback` (2 ca). Thân test không đổi |
| `tests/test_soi_loi_t041.py` | Đổi test SL-T041-8 của Soi Lỗi theo quyết định giữ Chặn (Chỉ Huy duyệt; mục «R5») |
| `tests/test_t041_meta.py` | Test của tôi ở T-041: ca U+0378 (ký tự chưa gán) nay mong câu mới (mục «R5») |
| `docs/team/reports/T-090-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `seo_app/wordpress/**`, `seo_app/onpage/schema.py`, `seo_app/env_file.py`, `scripts/**`, `.streamlit/config.toml`.

## Cách sửa

### SL-T041-8: giữ Chặn, câu báo theo loại ký tự

Bộ kiểm vẫn xét **chữ gốc** và vẫn Chặn đúng các ký tự như trước (`odd_char_messages` thấy đúng các ký tự `has_odd_chars` thấy; test quét đều cả bảng mã). Chỉ câu báo đổi:

| Ký tự trong chữ gốc (trừ khoảng trắng) | Câu báo |
|---|---|
| Chưa gán (loại Cn) mà có thể là biểu tượng mới: emoji Unicode 16 với Python 3.12 (U+1FAE9, U+1FAC6, U+1FADF, U+1FABE…), mã chưa gán khác (U+0378, U+2FFFD…) | **Mới:** «{tên ô} có ký tự phần mềm chưa nhận ra nên không ghi được (có thể là biểu tượng cảm xúc rất mới). Xóa ký tự đó hoặc thay bằng chữ thường, biểu tượng quen thuộc.» |
| Điều khiển (Cc), surrogate lẻ (Cs), ký tự riêng (Co); «không phải ký tự» (U+FDD0–U+FDEF, hai mã cuối mỗi mặt phẳng như U+FFFE, U+FFFF); mã Unicode để dành cho ký tự vô hình (U+2065, U+FFF0–U+FFF8, U+E0000–U+E0FFF) | **Cũ, giữ nguyên:** «{tên ô} có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ nơi khác). Xóa ô rồi gõ lại chữ thường.» |
| Có cả hai loại | Hai câu (mỗi câu một vấn đề, như quy ước của `FieldCheck.messages`) |

Vì sao tách «không phải ký tự» và mã để dành cho ký tự vô hình khỏi câu mới (Lá Chắn gợi ý «Cn → câu mới»): Python cũng xếp hai nhóm này vào Cn, nhưng chúng **không bao giờ** thành biểu tượng nhìn thấy được («không phải ký tự» không bao giờ được gán; mã để dành chỉ dành cho ký tự định dạng vô hình, Unicode quy định hiện ra không thấy gì). Với chúng, câu cũ «không nhìn thấy, thường do dán từ nơi khác» mới đúng. Cách nhận: so khoảng mã cố định (`_may_be_new_symbol`), không cần thư viện.

Những chỗ khác dùng `has_odd_chars` không đổi: gợi ý AI có ký tự lạ (kể cả emoji mới) vẫn bị bỏ, đuôi thương hiệu có ký tự lạ vẫn dùng đuôi mặc định, từ khóa chính (`app/views/write.py`) vẫn Chặn với câu riêng của trang (mục «Đề xuất» 1).

### SL-T084-1: `.env` sai bảng mã hay không đọc được

`load_settings` đọc `.env` qua `_read_env_file` (`config.py:154-169`):

- `UnicodeDecodeError` (Notepad «ANSI» cp1252 hay cp1258 của Windows tiếng Việt, UTF-16 có BOM): `ConfigError(MSG_ENV_NOT_UTF8)`: «File .env không đọc được dạng UTF-8 (thường do Notepad lưu kiểu «ANSI»). Mở file .env, chọn Lưu thành (Save As), ở ô Mã hóa (Encoding) chọn UTF-8, lưu đè rồi mở lại app.»
- `OSError` khi hỏi «có file không» (`is_file`) hay khi mở file: «Không đọc được file .env (PermissionError). Đóng chương trình đang mở file (nếu có), kiểm tra quyền đọc file rồi mở lại app.» Chỉ có tên loại lỗi, như câu của `seo_app/env_file.py` khi lưu khóa.
- Câu báo không có đường dẫn, không có nội dung `.env`, không chép câu lỗi gốc (câu gốc có số byte, vị trí, đường dẫn đầy đủ). Lỗi gốc vẫn nối sau `ConfigError` (`from exc`) để xem được ở cửa sổ dòng lệnh khi cần; trang không hiện nó.
- `app/main.py:66-70` đã bắt `ConfigError`, hiện `st.error(câu)` rồi dừng: đó là trang báo lỗi (không có ô mật khẩu, không traceback). Mọi trang khác chỉ chạy sau khi lần đọc này của `main.py` thành công trong cùng lượt chạy, nên không trang nào tới được chỗ đọc `.env` khi file hỏng. Không cần sửa `app/**`.
- UTF-8 có BOM: python-dotenv 1.2.4 đã tự bỏ BOM (`dotenv/parser.py`, `removeprefix("\ufeff")`) nên không đổi cách đọc; có test canh.

## Test mới

`tests/test_t090_meta_emoji_moi.py` (103 ca):

| Test | Kiểm |
|---|---|
| `test_unknown_char_stays_blocked_with_accurate_message` (7) | 4 emoji Unicode 16, 3 mã chưa gán: title (có, không đuôi thương hiệu), description đều Chặn; câu có «chưa nhận ra», «biểu tượng cảm xúc», không có «không nhìn thấy», «điều khiển»; không chép lại ký tự; khung chép SiteSEO không cho chép |
| `test_new_emoji_is_still_dropped_where_text_is_written` (4) | Lý do giữ Chặn: `normalize_meta` bỏ emoji; gợi ý AI có emoji bị bỏ, bản không có thì nhận |
| `test_control_invisible_and_noncharacters_keep_old_message` (84) | Cc, Cs, Co, đủ 66 «không phải ký tự», 10 mã để dành cho ký tự vô hình: Chặn, câu cũ, không có câu mới |
| `test_both_kinds_give_both_messages` | Cả hai loại: hai câu, đúng thứ tự |
| `test_no_message_without_odd_chars` (4) | Chữ thường, khoảng trắng loại điều khiển, emoji quen (⭐ ✅ 🫨 ❤️), dấu cách rộng 0 (bị bỏ, không Chặn): không câu báo |
| `test_messages_cover_exactly_what_has_odd_chars_sees` | Câu báo và `has_odd_chars` thấy cùng các ký tự (quét mỗi 11 mã một trên cả bảng mã, cộng mọi mã của các nhóm trên) |
| `test_noncharacter_list_is_complete_and_cn` | Danh sách «không phải ký tự» đủ 66 mã, mọi mã của hai nhóm tách riêng đều là Cn với Python này |
| `test_seo_step_shows_accurate_message_for_new_emoji` | Trang Soạn bài, bước SEO (chưa có khóa AI, tự gõ): nhãn «Chặn», câu dưới ô là câu mới, không có «không nhìn thấy», khung chép báo «chưa chép được» |

Các test về emoji mới bỏ qua (`skipif`) trên Python đã biết Unicode 16 (3.14 trở lên), như test của Soi Lỗi và Lá Chắn.

`tests/test_t090_env_bang_ma.py` (12 ca, `.env` giả trong thư mục tạm):

| Test | Kiểm |
|---|---|
| `test_cp1258_sample_is_vietnamese_ansi` | Mẫu cp1258 đúng là «Ảnh công trình Tân Phú» khi đọc bằng bảng mã đó |
| `test_env_in_other_encoding_gives_fixed_message` (4) | cp1252, cp1258, UTF-16 LE/BE có BOM: `ConfigError` đúng câu cố định, cả qua `DEFAULT_ENV_FILE`; câu không có đường dẫn (thư mục tạm, thư mục nhà), nội dung `.env` (thư mục ảnh, khóa giả, tên biến), câu lỗi gốc («codec», «byte», «position», «0x»…) |
| `test_env_saved_again_as_utf8_is_read` (2) | Lưu lại UTF-8, có và không BOM: đọc đủ, biến dòng đầu không mất |
| `test_unreadable_env_gives_fixed_message` (2) | `PermissionError`, `OSError` (có đường dẫn trong lỗi gốc): câu cố định kèm tên loại lỗi, không đường dẫn |
| `test_env_that_cannot_even_be_checked_gives_fixed_message` | `is_file` ném `PermissionError`: vẫn câu cố định |
| `test_app_shows_clear_error_page_then_login_after_fix` (2) | Mở app (`AppTest`) với `.env` cp1252 / UTF-16: không lỗi lạ, đúng một khung lỗi là câu cố định, không ô mật khẩu, mọi chữ trên trang không có đường dẫn thư mục app, thư mục tạm, thư mục nhà, nội dung `.env`, «Traceback»; lưu lại UTF-8, chạy lại: màn đăng nhập hiện, đăng nhập được |

## R5: test cũ đã đổi

| File, dòng | Trước | Sau | Lý do, người duyệt |
|---|---|---|---|
| `tests/test_soi_loi_t041.py:733-746` (Soi Lỗi; bản cũ `:733-744`) | `test_sl_t041_8_new_emoji_is_not_blocked`, `xfail(strict=True)`: khẳng định title, description có emoji mới **không** bị Chặn | `test_sl_t041_8_new_emoji_is_blocked_with_accurate_message`, không còn `xfail`: vẫn Chặn, câu có «chưa nhận ra», không có «không nhìn thấy». Giữ nguyên dòng «client WordPress ghi được chữ này», thêm dòng «chữ ghi đi mất emoji» (lý do giữ Chặn) | Lá Chắn T-041 quyết giữ Chặn; test cũ đòi hướng ngược lại nên không bao giờ XPASS. **Chỉ Huy B duyệt** đổi test này trong tin nhắn giao T-090 (2026-10-28 02:45) |
| `tests/test_t041_meta.py:78-82` (của tôi, T-041 lượt 3) | `test_user_text_with_odd_chars_is_blocked`: cả 9 ký tự (kể cả U+0378, chưa gán) mong câu «ký tự điều khiển hoặc ký tự lạ» | U+0378 mong câu mới «chưa nhận ra»; 8 ký tự còn lại giữ câu cũ. Vẫn đủ 9 ca, vẫn Chặn, vẫn kiểm không chép lại ký tự, chép SiteSEO bị từ chối | Hệ quả trực tiếp của quyết định trên (U+0378 cùng nhóm Cn với emoji mới). Không bớt ca, không nới điều kiện Chặn |
| `tests/test_la_chan_t041.py:98-101` (bản cũ) | 4 dòng `@pytest.mark.xfail(strict=True, …)` | Gỡ, chỉ xóa dấu | Trước khi gỡ: 2 ca `XPASS(strict)` |
| `tests/test_soi_loi_t084.py:320-323` (bản cũ) | 4 dòng `@pytest.mark.xfail(strict=True, …)` | Gỡ, chỉ xóa dấu | Trước khi gỡ: 2 ca `XPASS(strict)` |

`git diff 1e49185 -- tests/test_la_chan_t041.py tests/test_soi_loi_t084.py`: 8 dòng `-`, 0 dòng `+`.

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15 (uv; bảng Unicode của Python 15.0.0), worktree `wt-T-090`. Máy chạy song song các phiên khác.

**Test mới bắt được lỗi trên code cũ.** Chép cây `1e49185` (`git archive`) ra thư mục nháp, thêm đúng các tên mà test mới nhập nhưng giữ hành vi cũ (`odd_char_messages` trả câu cũ cho mọi ký tự lạ; `MSG_ENV_NOT_UTF8` chỉ là hằng, `load_settings` không bắt lỗi), chạy 2 file test mới bằng venv của worktree (`seo_app` nạp từ cây cũ): **`18 failed, 97 passed`**. 18 ca hỏng đúng là ca của hai lỗi: 7 ca câu mới, 1 ca hai câu, 1 ca trang SEO; 4 ca bảng mã, 2 ca không đọc được, 1 ca `is_file` lỗi, 2 ca trang báo lỗi. 97 ca còn lại là ca canh (câu cũ giữ nguyên, câu báo và `has_odd_chars` thấy cùng ký tự, gợi ý AI vẫn bị bỏ, UTF-8 có BOM đọc đúng), qua trên cả hai bản.

**Dấu `xfail` cũ báo XPASS trước khi gỡ.** `test_la_chan_t041.py::test_sl8_new_emoji_stays_blocked_with_accurate_message` (2 ca) và `test_soi_loi_t084.py::test_env_file_not_utf8_fixed_message_no_traceback` (2 ca): cả 4 ca `XPASS(strict)`. `test_soi_loi_t041.py::test_sl_t041_8_new_emoji_is_not_blocked` vẫn `XFAIL` (test đòi không Chặn), nên đổi theo mục «R5».

**Test liên quan, 81 file:** file của phiếu, test mới, và test của mọi nơi gọi phần đã sửa: `grep` mọi file test có `onpage.meta`, `onpage_meta`, `check_title`, `check_description`, `siteseo_copy`, `seo_write_problem`, `has_odd_chars`, `load_settings`, `ConfigError`, `DEFAULT_ENV_FILE`, `seo_app.config`; cộng mọi file có `WordPressClient`, `set_seo_meta`, `_seo_text` (bài học lỗi lùi T-041: client chuẩn hóa bằng `normalize_meta`); cộng `test_t041_*`, `test_la_chan_t04*`, `test_soi_loi_t04*`, `test_config_tolerance.py`, `test_app_pages.py` (mở mọi trang), `test_t059_*`, `test_shortcode_t061.py`.

```
$ uv run pytest -q -p no:cacheprovider --no-header -rfE \
    tests/test_ai.py tests/test_ai_openai_gemini.py tests/test_ai_openai_gemini_soi_loi.py \
    tests/test_ai_t026.py tests/test_app_images.py tests/test_app_pages.py \
    tests/test_app_t044_safe_text.py tests/test_app_wordpress.py tests/test_blind_test.py \
    tests/test_config.py tests/test_config_tolerance.py tests/test_content_edge_cases.py \
    tests/test_content_workflow.py tests/test_env_file.py tests/test_hash_password_script.py \
    tests/test_images_process.py tests/test_images_tags.py tests/test_la_chan_t040.py \
    tests/test_la_chan_t041.py tests/test_la_chan_t060.py tests/test_la_chan_t089.py \
    tests/test_onpage_links.py tests/test_onpage_meta.py tests/test_phase2_fixes.py \
    tests/test_sanitize.py tests/test_sanitize_hardening.py tests/test_settings_blind.py \
    tests/test_settings_images.py tests/test_settings_keys.py tests/test_shortcode_t061.py \
    tests/test_site_index.py tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t016_t020.py \
    tests/test_soi_loi_t019.py tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t023.py \
    tests/test_soi_loi_t031.py tests/test_soi_loi_t036.py tests/test_soi_loi_t037.py \
    tests/test_soi_loi_t039.py tests/test_soi_loi_t040.py tests/test_soi_loi_t041.py \
    tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py \
    tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t043.py tests/test_soi_loi_t044.py \
    tests/test_soi_loi_t045.py tests/test_soi_loi_t047.py tests/test_soi_loi_t049.py \
    tests/test_soi_loi_t051.py tests/test_soi_loi_t054.py tests/test_soi_loi_t056.py \
    tests/test_soi_loi_t059.py tests/test_soi_loi_t060.py tests/test_soi_loi_t061.py \
    tests/test_soi_loi_t062.py tests/test_soi_loi_t075.py tests/test_soi_loi_t084.py \
    tests/test_soi_loi_t085.py tests/test_soi_loi_t088.py tests/test_soi_loi_t089.py \
    tests/test_t040_prompts.py tests/test_t041_drafts_seo.py tests/test_t041_links_ai.py \
    tests/test_t041_meta.py tests/test_t041_schema.py tests/test_t041_seo_ui.py \
    tests/test_t041_site_index.py tests/test_t059_siet_ghi_seo_va_srcset.py \
    tests/test_t062_image_config.py tests/test_t090_env_bang_ma.py \
    tests/test_t090_meta_emoji_moi.py tests/test_wordpress_client.py \
    tests/test_wordpress_images.py tests/test_wordpress_published.py \
    tests/test_wordpress_round2_t042.py tests/test_wordpress_seo_meta_t042.py \
    tests/test_wordpress_t060.py tests/test_wordpress_t085.py tests/test_wordpress_t088.py
(2026-10-28 07:52:22 → 08:24:43 +0700)
9315 passed, 12 skipped, 24 xfailed in 1930.01s (0:32:10)
```

- **0 hỏng, 0 XPASS.** 24 `xfailed` đều là lỗi đã biết của phiếu khác, có sẵn trên `main` (chạy lại với `-rxX` riêng 10 file có dấu `xfail`: `2495 passed, 24 xfailed`, 0 XPASS): `test_soi_loi_t003_t009.py::test_keyword_cannot_fake_a_frame` (1), `test_soi_loi_t036.py::test_r2_do_vat_not_price` (1) và `test_r2_price_forms_still_missed` (4), `test_soi_loi_t045.py` SL-T045-1, -2 (5), `test_soi_loi_t059.py::test_sl_t059_1_…` (5), `test_soi_loi_t088.py` SL-T088-1 (8). Không còn ca nào của SL-T041-8, SL-T084-1. 12 bỏ qua do máy (symlink, quyền kiểu POSIX chỉ thử trên Mac/Linux…), có từ trước.
- Sau lượt trên chỉ đổi cách viết ký tự trong test (mã thoát `\N{…}`, `chr(0x0378)` thay cho ký tự vô hình viết thẳng), thêm một chú thích, xuống dòng một docstring. Chạy lại trên đúng bản commit (08:24:55 → 08:25:22): `tests/test_t090_meta_emoji_moi.py tests/test_t090_env_bang_ma.py tests/test_t041_meta.py` → **`215 passed in 21.99s`**.

```
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check <8 file đã sửa: 2 file code, 6 file test>
8 files already formatted
$ PYTHONUTF8=1 uvx --offline detect-secrets scan <8 file đã sửa>
```

- `detect-secrets`: `tests/test_t090_env_bang_ma.py:25` («Secret Keyword»: `FAKE_KEY = "sk-ant-gia-T090-khong-phai-khoa-that"`, chuỗi mồi có chú thích, không phải khóa thật, dùng để chứng minh khóa trong `.env` không hiện ra); `tests/test_la_chan_t041.py:5`, `:34` có từ trước (chuỗi mồi của Lá Chắn), tôi không đụng các dòng đó.
- Gộp thử với `origin/main` `1dfc062` (`git merge-tree`): không xung đột; từ gốc nhánh `1e49185`, `main` chỉ đổi tài liệu (7 file, không file code hay test nào).
- Không đọc `.env` thật: mọi test dùng `.env` giả trong thư mục tạm; `tests/conftest.py` vẫn trỏ `DEFAULT_ENV_FILE` sang file không tồn tại cho mọi test khác. Không thử bằng app thật trên trình duyệt: phải làm hỏng `.env` thật mới thấy trang báo lỗi; `AppTest` chạy đúng `app/main.py` thay cho bước đó.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1, SL-T041-8: giữ Chặn, câu báo đúng nghĩa, phân biệt với ký tự điều khiển/vô hình (`meta.py:123-162`, `:189`; `test_unknown_char_stays_blocked_with_accurate_message`, `test_control_invisible_and_noncharacters_keep_old_message`, `test_seo_step_shows_accurate_message_for_new_emoji`; test Lá Chắn `test_sl8_…` và test Soi Lỗi đã đổi qua)
- [x] Yêu cầu 2, SL-T084-1: `.env` sai bảng mã ra câu tiếng Việt cố định, app mở trang báo lỗi rõ ràng, sửa xong ra trang đăng nhập; không traceback, không đường dẫn (`config.py:44-51`, `:154-169`; `test_app_shows_clear_error_page_then_login_after_fix`; test Soi Lỗi `test_env_file_not_utf8_fixed_message_no_traceback` gỡ `xfail` qua)
- [x] Yêu cầu 3: test cho cả hai (115 ca mới); test cũ liên quan (T-036, T-040, T-041 meta; client ghi SEO T-042, T-059, T-061; cấu hình; mọi trang) qua (mục «Bằng chứng»)
- [x] `uv run ruff check .` sạch; báo cáo này

## Rủi ro và điểm cần chú ý

- Lên Python có bảng Unicode mới hơn (3.14: Unicode 16), emoji năm 2024 thành ký tự thường và tự qua (không bị Chặn), các test emoji mới bỏ qua; emoji ra sau bảng Unicode của Python lúc đó lại nhận câu mới. Không cần sửa code.
- Câu mới cũng hiện với mã chưa gán không phải emoji (U+0378): chữ «có thể là» giữ câu đúng nghĩa.
- `.env` UTF-16 **không** BOM mà chỉ có chữ không dấu vẫn là UTF-8 hợp lệ (có ký tự NUL), nên không ra câu báo bảng mã, các biến bị đọc sai tên (app báo chưa đặt mật khẩu). Notepad luôn ghi BOM cho UTF-16 nên rất hiếm; không xử lý ở phiếu này.
- `.env` lưu «ANSI» mà chỉ có chữ không dấu vẫn đọc bình thường (ASCII cũng là UTF-8), đúng như mong muốn.

## Đề xuất

Việc ngoài phạm vi phiếu, Chỉ Huy quyết:

1. **Từ khóa chính có emoji mới** (`app/views/write.py`, `MSG_KEYWORD_ODD` `:1957-1959`, `keyword_problem()`): vẫn hiện câu cũ «không nhìn thấy». Sửa một dòng: dùng `" ".join(onpage_meta.odd_char_messages(KEYWORD_LABEL, text))`; `tests/test_t041_seo_ui.py:711` đang khẳng định đúng câu cũ nên cần đổi theo (R5). Từ khóa có emoji gần như không gặp, mức rất thấp. Họa Sĩ hoặc phiếu giao diện kế tiếp đụng `write.py`.
2. **FAQ** (`seo_app/onpage/schema.py:341`): câu «có ký tự điều khiển hoặc ký tự lạ.» không nói «không nhìn thấy» nên ít sai hơn; Lá Chắn ghi «nếu tiện». Muốn đồng bộ thì dùng cùng cách phân loại (ngoài phạm vi phiếu này).
3. **`scripts/hash_password.py`** (`set_password.bat`) đọc `.env` bằng UTF-8 mà không bắt lỗi: `.env` «ANSI» thì cửa sổ đặt mật khẩu hiện traceback tiếng Anh (máy của chính chủ, không lên trình duyệt). Nên bắt `UnicodeDecodeError`, in `MSG_ENV_NOT_UTF8`, không ghi đè file. Cũng có thể cho `seo_app/env_file.py` dùng chung câu này (câu hiện tại ngắn hơn nhưng đúng).
4. `client.showErrorDetails` (cấu hình Streamlit, mọi lỗi lạ chỉ hiện tên loại lỗi): không làm ở phiếu này theo ghi chú của phiếu, cần chủ dự án duyệt.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 · Đề xuất 2 và 3 (2026-10-28)

Chỉ Huy B giao (chủ dự án dặn «có đề xuất thì làm theo đề xuất»), mở phạm vi `seo_app/onpage/schema.py` (đúng chỗ câu báo ký tự lạ) và `scripts/hash_password.py`. Đề xuất 1 (từ khóa chính, `app/views/write.py`) giao Họa Sĩ ở T-092, tôi không làm. Đề xuất 4 vẫn chờ chủ dự án.

### Tóm tắt (cho chủ dự án)

- Mục Hỏi đáp của bài có biểu tượng cảm xúc rất mới: schema Hỏi đáp vẫn không dựng (như trước), nhưng câu báo nay nói đúng: «Trả lời 1: có ký tự phần mềm chưa nhận ra (có thể là biểu tượng cảm xúc rất mới). Sửa trong bài: xóa ký tự đó hoặc thay bằng biểu tượng quen thuộc.» Ký tự vô hình thì câu báo nói rõ là không nhìn thấy, thường do dán từ nơi khác, và cách sửa (gõ lại câu đó).
- Bấm đúp `set_password` khi file `.env` lưu sai bảng mã: cửa sổ báo ngay bằng tiếng Việt cách lưu lại file bằng UTF-8 rồi chạy lại, **chưa bắt gõ mật khẩu**; không còn lỗi tiếng Anh dài kèm đường dẫn. File `.env` không đọc hay ghi được (đang mở ở chương trình khác, không có quyền) cũng có câu báo riêng. File `.env` không bị đụng tới khi báo lỗi.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/onpage/meta.py` | Tách phần phân loại khỏi `odd_char_messages` thành `odd_char_kinds(text)` (`:134-150`), dùng chung cho meta và FAQ. Câu báo meta, mức Chặn không đổi |
| `seo_app/onpage/schema.py` | `_check_text` (`:330-350`) dùng `odd_char_kinds`: hai câu báo theo loại, có cách sửa trong bài. Bỏ `_ODD_CATEGORIES`, `_has_control` (chỉ chỗ này dùng). Không đổi `normalize_text` hay tập ký tự bị Chặn |
| `seo_app/config.py` | Tách phần đầu câu báo bảng mã thành `ENV_RESAVE_UTF8` (`:45`) để `set_password` dùng chung; `MSG_ENV_NOT_UTF8` (`:49`) giữ nguyên từng chữ |
| `scripts/hash_password.py` | Câu cố định `MSG_ENV_NOT_UTF8`, `MSG_ENV_UNREADABLE`, `MSG_ENV_UNWRITABLE` (`:24-34`); `read_env_lines` mới (`:37-47`); `set_env_value` báo `ConfigError` câu cố định khi chép mẫu, đọc, ghi lỗi; `main` kiểm `.env` **trước** khi hỏi mật khẩu (`:97-102`), lỗi lúc ghi thì báo «Chưa lưu mật khẩu mới.» (`:115-119`), thoát mã 1, không traceback |
| `tests/test_t090_meta_emoji_moi.py` | Thêm 6 hàm, 182 ca (mục «Test mới» dưới) |
| `tests/test_t090_env_bang_ma.py` | Thêm 6 hàm, 10 ca |
| `tests/test_t041_schema.py` | Test của tôi ở T-041: ca U+0378 mong câu mới (mục «R5» dưới) |

### Cách sửa

**Câu báo FAQ.** Như ô meta (mục «Cách sửa» lượt 1), nhưng xét chữ đã chuẩn hóa của câu hỏi, trả lời (`normalize_text`, như trước):

| Ký tự còn lại sau chuẩn hóa | Câu báo |
|---|---|
| Chưa gán, có thể là biểu tượng mới (emoji Unicode 16, U+0378…) | «{Câu hỏi n / Trả lời n}: có ký tự phần mềm chưa nhận ra (có thể là biểu tượng cảm xúc rất mới). Sửa trong bài: xóa ký tự đó hoặc thay bằng biểu tượng quen thuộc.» |
| Điều khiển, surrogate lẻ, ký tự riêng, «không phải ký tự», mã để dành cho ký tự vô hình | «{…}: có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ nơi khác). Sửa trong bài: gõ lại câu đó bằng chữ thường.» (câu cũ chỉ có «có ký tự điều khiển hoặc ký tự lạ.») |

Tập ký tự bị Chặn ở FAQ **không đổi** (điều kiện 1 của Lá Chắn T-038): đã so cách cũ (`_has_control` trên chữ đã chuẩn hóa) với cách mới trên **từng** mã của cả bảng mã (1.114.112 mã): 0 khác biệt (`str.isspace` và `\s` của `re` trùng nhau, nên bỏ qua khoảng trắng như `odd_char_kinds` không đổi gì sau `normalize_text`). Test canh `test_faq_blocks_exactly_the_same_chars_as_before` giữ điều này. Ba mã «mặc định bỏ qua» U+2065, U+FFF0–U+FFF8 vẫn bị `normalize_text` bỏ như trước (không Chặn), có test canh.

`schema.py` nhập `odd_char_kinds` từ `meta.py`: không tạo vòng nhập (`meta.py` không nhập `schema.py`; `schema.py` vốn đã kéo `meta.py` vào qua `seo_app.content`). Đã thử nhập riêng từng module trước tiên trong một trình Python mới: `seo_app.onpage.schema`, `seo_app.onpage.meta`, `seo_app.content`, `seo_app.onpage.links`, `seo_app.wordpress.client`, `seo_app.storage`, `seo_app.images.alt`, `seo_app.images.html`, `seo_app.content.prompts`: đều được.

**`set_password`.** Câu báo bảng mã dùng chung phần đầu với app, chỉ khác bước cuối: «File .env không đọc được dạng UTF-8 (thường do Notepad lưu kiểu «ANSI»). Mở file .env, chọn Lưu thành (Save As), ở ô Mã hóa (Encoding) chọn UTF-8, lưu đè rồi chạy lại set_password.»

| Lúc | Trước | Nay |
|---|---|---|
| `.env` sai bảng mã (cp1252, cp1258, UTF-16) | Bắt gõ mật khẩu hai lần, rồi traceback tiếng Anh (`UnicodeDecodeError`, đường dẫn thư mục app) | Báo ngay «Chưa đặt được mật khẩu. File .env không đọc được dạng UTF-8…», chưa hỏi mật khẩu, thoát mã 1 |
| `.env` không đọc được | Traceback (`PermissionError` kèm đường dẫn đầy đủ) | «Chưa đặt được mật khẩu. Không đọc được file .env (PermissionError). Đóng chương trình đang mở file (nếu có), kiểm tra quyền đọc file rồi chạy lại set_password.» |
| Đọc được mà không ghi được `.env`, hay không chép được `.env.example` sang | Traceback | «Chưa lưu mật khẩu mới. Không ghi được file .env (PermissionError). … kiểm tra quyền ghi file rồi chạy lại set_password.» |
| `--print` (chỉ in mã băm) | Không đọc `.env` | Như cũ: không đọc, không cần `.env` đúng |

Câu báo chỉ có tên loại lỗi, không đường dẫn, không nội dung `.env`, không câu lỗi gốc; lỗi gốc nối sau `ConfigError` (`from exc`) nhưng không in ra. Dòng «Đã lưu mật khẩu mới vào {đường dẫn}.» khi thành công giữ như cũ (không thuộc lỗi này).

### Test mới

`tests/test_t090_meta_emoji_moi.py`, mục «lượt 2» (182 ca):

| Test | Kiểm |
|---|---|
| `test_faq_unknown_char_stays_blocked_with_accurate_message` (14) | 4 emoji Unicode 16 và 3 mã chưa gán, ở câu hỏi và câu trả lời: Chặn, không JSON-LD, đúng một câu báo mở đầu «Câu hỏi 1: / Trả lời 1: có ký tự phần mềm chưa nhận ra», có cách sửa, không có «không nhìn thấy», «điều khiển», không chép lại ký tự |
| `test_faq_control_invisible_and_noncharacters_keep_old_message` (162) | 81 ký tự (Cc, Cs, Co, đủ 66 «không phải ký tự», mã để dành còn lại sau chuẩn hóa) × câu hỏi, trả lời: Chặn, câu «ký tự điều khiển hoặc ký tự lạ (không nhìn thấy…)», không có câu mới |
| `test_faq_drops_reserved_ignorable_chars_as_before` (3) | Canh: U+2065, U+FFF0, U+FFF8 vẫn bị bỏ, không Chặn |
| `test_faq_blocks_exactly_the_same_chars_as_before` | Canh: Chặn đúng khi chữ đã chuẩn hóa còn Cc, Cs, Co, Cn (quét mỗi 11 mã một trên cả bảng mã) |
| `test_faq_both_kinds_give_two_issues` | Có cả hai loại: hai câu báo |
| `test_seo_step_faq_shows_accurate_message_for_new_emoji` | Trang Soạn bài, bước SEO, bài có mục Hỏi đáp với emoji mới: không có JSON-LD, câu dưới phần Schema là câu mới |

`tests/test_t090_env_bang_ma.py`, mục «lượt 2» (10 ca, `.env` giả, thay `getpass` bằng hàm giả):

| Test | Kiểm |
|---|---|
| `test_set_password_with_env_in_other_encoding_stops_before_asking` (4) | cp1252, cp1258, UTF-16 LE/BE: thoát mã 1, **không gọi** `getpass`, in đúng một dòng câu cố định; không đường dẫn (thư mục app, thư mục tạm, thư mục nhà), không nội dung `.env`, không «Traceback», «decode»…; file giữ nguyên từng byte |
| `test_set_password_after_resave_as_utf8_works` (2) | UTF-8 có và không BOM: mật khẩu mới lưu được, app đọc được (`load_settings` + `verify_password`), các dòng khác giữ nguyên |
| `test_set_password_cannot_write_env` | Ghi lỗi (`PermissionError`): «Chưa lưu mật khẩu mới. Không ghi được file .env (PermissionError).», không đường dẫn, file giữ nguyên |
| `test_set_password_env_unreadable_gives_fixed_message` | Đọc lỗi: câu cố định kèm tên loại lỗi, không đường dẫn |
| `test_set_password_cannot_create_env_from_template` | Chép `.env.example` lỗi: câu cố định, không tạo file |
| `test_print_mode_does_not_need_env` | Canh: `--print` vẫn chạy khi `.env` hỏng, không đụng file |

Lỗi giả (`PermissionError`) tạo bằng lớp con của `Path` hay thay `shutil.copyfile`, không đổi quyền file thật, nên chạy như nhau trên Windows, Mac, Linux (kể cả máy chạy bằng tài khoản quản trị).

### R5: test cũ đã đổi

| File, dòng | Trước | Sau | Lý do |
|---|---|---|---|
| `tests/test_t041_schema.py:65-67` (của tôi, T-041) | `test_odd_chars_blocked`: cả 6 ký tự (kể cả U+0378, chưa gán) mong câu có «ký tự lạ» | U+0378 mong câu mới «chưa nhận ra»; 5 ký tự còn lại giữ «ký tự lạ». Vẫn đủ 12 ca, vẫn Chặn, vẫn kiểm không JSON-LD, không chép lại ký tự | Hệ quả trực tiếp của đề xuất 2 Chỉ Huy giao (U+0378 cùng nhóm với emoji mới). Không bớt ca, không nới điều kiện Chặn |

Không đổi test nào của Soi Lỗi hay Lá Chắn ở lượt này. `tests/test_hash_password_script.py` (4 test cũ của script) không đổi và vẫn qua.

### Bằng chứng

Cùng máy Windows, Python 3.12.15. Máy rất bận lúc chạy (CPU khoảng 92% do các phiên khác), nên lượt dài gấp đôi lượt 1.

**Test mới bắt được lỗi trên bản lượt 1.** Chép cây `17a8eda` (lượt 1, `git archive`) ra thư mục nháp, thêm 2 file test T-090 bản lượt 2, chạy các ca lượt 2 (`-k "faq or set_password or print_mode"`) bằng venv của worktree: **`185 failed, 6 passed`**. 6 ca qua trên cả hai bản đúng là ca canh: `test_faq_drops_reserved_ignorable_chars_as_before` (3), `test_set_password_after_resave_as_utf8_works` (2), `test_print_mode_does_not_need_env` (1). Lần thử đầu, test trang SEO FAQ qua cả trên bản cũ (nó so câu trên trang với câu do chính code đang chạy dựng), nên tôi thêm điều kiện «có chữ *chưa nhận ra*» rồi chạy lại: hỏng đúng trên bản cũ. Test canh `test_faq_blocks_exactly_the_same_chars_as_before` thêm sau lượt này, nên không nằm trong 191 ca trên (qua trên bản mới, xem dưới).

**Test liên quan, 90 file:** 81 file của lượt 1 (cùng cách lấy danh sách) cộng mọi file test nhập `seo_app.onpage.schema`, `build_article_faq`, `build_faq_page`, `validate_faq_page` (thêm `test_onpage_schema.py`, `test_soi_loi_t038.py` của T-038) và mọi file có chữ `hash_password` (thêm `test_app.py`, `test_auth.py`, `test_edit_unescape.py`, `test_soi_loi_round4.py`, `test_soi_loi_round5.py`, `test_soi_loi_t019_luot2.py`, `test_ui_escape.py`: các file này dùng hàm băm mật khẩu để đăng nhập app).

```
$ uv run pytest -q -p no:cacheprovider --no-header -rfEX \
    tests/test_ai.py tests/test_ai_openai_gemini.py tests/test_ai_openai_gemini_soi_loi.py \
    tests/test_ai_t026.py tests/test_app.py tests/test_app_images.py tests/test_app_pages.py \
    tests/test_app_t044_safe_text.py tests/test_app_wordpress.py tests/test_auth.py \
    tests/test_blind_test.py tests/test_config.py tests/test_config_tolerance.py \
    tests/test_content_edge_cases.py tests/test_content_workflow.py tests/test_edit_unescape.py \
    tests/test_env_file.py tests/test_hash_password_script.py tests/test_images_process.py \
    tests/test_images_tags.py tests/test_la_chan_t040.py tests/test_la_chan_t041.py \
    tests/test_la_chan_t060.py tests/test_la_chan_t089.py tests/test_onpage_links.py \
    tests/test_onpage_meta.py tests/test_onpage_schema.py tests/test_phase2_fixes.py \
    tests/test_sanitize.py tests/test_sanitize_hardening.py tests/test_settings_blind.py \
    tests/test_settings_images.py tests/test_settings_keys.py tests/test_shortcode_t061.py \
    tests/test_site_index.py tests/test_soi_loi_round4.py tests/test_soi_loi_round5.py \
    tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t019_luot2.py tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t023.py \
    tests/test_soi_loi_t031.py tests/test_soi_loi_t036.py tests/test_soi_loi_t037.py \
    tests/test_soi_loi_t038.py tests/test_soi_loi_t039.py tests/test_soi_loi_t040.py \
    tests/test_soi_loi_t041.py tests/test_soi_loi_t042.py \
    tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t042_round2.py \
    tests/test_soi_loi_t043.py tests/test_soi_loi_t044.py tests/test_soi_loi_t045.py \
    tests/test_soi_loi_t047.py tests/test_soi_loi_t049.py tests/test_soi_loi_t051.py \
    tests/test_soi_loi_t054.py tests/test_soi_loi_t056.py tests/test_soi_loi_t059.py \
    tests/test_soi_loi_t060.py tests/test_soi_loi_t061.py tests/test_soi_loi_t062.py \
    tests/test_soi_loi_t075.py tests/test_soi_loi_t084.py tests/test_soi_loi_t085.py \
    tests/test_soi_loi_t088.py tests/test_soi_loi_t089.py tests/test_t040_prompts.py \
    tests/test_t041_drafts_seo.py tests/test_t041_links_ai.py tests/test_t041_meta.py \
    tests/test_t041_schema.py tests/test_t041_seo_ui.py tests/test_t041_site_index.py \
    tests/test_t059_siet_ghi_seo_va_srcset.py tests/test_t062_image_config.py \
    tests/test_t090_env_bang_ma.py tests/test_t090_meta_emoji_moi.py tests/test_ui_escape.py \
    tests/test_wordpress_client.py tests/test_wordpress_images.py \
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py \
    tests/test_wordpress_seo_meta_t042.py tests/test_wordpress_t060.py \
    tests/test_wordpress_t085.py tests/test_wordpress_t088.py
(2026-10-28 08:57:30 → 10:19:39 +0700)
1 failed, 10457 passed, 12 skipped, 26 xfailed in 4919.00s (1:21:59)
FAILED tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted
```

- **Ca hỏng không do lượt này, là test đo thời gian:** test giữ khóa SQLite ở luồng khác **10 giây** rồi tự nhả; các bước kiểm bên trong mất khoảng 9 giây trên máy này, máy bận thì vượt 10 giây, khóa nhả trước bước cuối nên «DID NOT RAISE». Lượt này không đụng `seo_app/storage/site_index.py` hay chỗ nào test đó gọi. Ca này đã hỏng y như vậy khi máy bận ở nhiều phiếu trước (báo cáo T-041 Thợ Máy lượt 2, T-041 Họa Sĩ, T-050 Lá Chắn, T-060, T-085 Thợ Máy), lần nào chạy riêng cũng qua. Chạy lại riêng ngay sau (10:20:13): `1 passed` (bước gọi mất 9,19 giây); cả file `tests/test_soi_loi_t037.py`: `139 passed`. Đề nghị Soi Lỗi nới thời gian giữ khóa của test này (ví dụ 30 giây) để khỏi hỏng oan khi máy bận.
- 0 XPASS (log không có dòng `XPASS`). 26 `xfailed` là lỗi đã biết, có sẵn trên `main`: 24 ca như lượt 1 và 2 ca `test_soi_loi_round4.py::test_r4_3_code_span_is_not_escaped` (file mới thêm vào danh sách; chạy riêng: `525 passed, 2 xfailed`). 12 bỏ qua do máy, như lượt 1.
- Bản cuối (thêm test canh FAQ, đổi bước quét 7 → 11 sau khi lượt dài đã bắt đầu), chạy lại trên đúng bản commit (10:23:38 → 10:24:29): `tests/test_t090_meta_emoji_moi.py tests/test_t090_env_bang_ma.py tests/test_t041_schema.py tests/test_hash_password_script.py` → **`394 passed in 46.63s`**.

```
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check scripts/hash_password.py seo_app/config.py seo_app/onpage/meta.py \
    tests/test_t090_meta_emoji_moi.py tests/test_t090_env_bang_ma.py tests/test_t041_schema.py
6 files already formatted
$ PYTHONUTF8=1 uvx --offline detect-secrets scan <7 file đã sửa ở lượt này>
```

- `ruff format --check seo_app/onpage/schema.py`: một dòng trống thiếu có từ trước (mục «Rủi ro» dưới).
- `detect-secrets`: `tests/test_t090_env_bang_ma.py:30` (chuỗi mồi `FAKE_KEY` của lượt 1, dời xuống 5 dòng); `tests/test_t041_schema.py:212` có từ trước (`secret = "MA-BI-MAT-T041"`, chuỗi mồi ở T-041, cùng dòng trên `1e49185` là `:210`).
- Gộp thử `team/T-090` (bản commit lượt 2, `52ce068`) với `origin/main` `3f228bc` (`git merge-tree`): không xung đột. Từ gốc nhánh `1e49185`, `main` chỉ đổi tài liệu (không file code, test, script nào).

### Đối chiếu

- [x] Đề xuất 2: câu báo FAQ tách «chưa nhận ra» / «không nhìn thấy», vẫn Chặn đúng tập ký tự cũ (`schema.py:330-350`; 182 ca mới; `test_t041_schema.py`, `test_soi_loi_t041.py::test_lc_t038_1_…`, `test_onpage_schema.py`, `test_soi_loi_t038.py` qua)
- [x] Đề xuất 3: `set_password` báo câu tiếng Việt cố định khi `.env` lưu «ANSI»/UTF-16 (và khi không đọc, ghi được), không traceback, không đường dẫn (`scripts/hash_password.py`; 10 ca mới; `test_hash_password_script.py` qua)
- [x] Test liên quan + `uv run ruff check .` sạch; báo cáo mục này

### Rủi ro

- `ruff format --check seo_app/onpage/schema.py` báo một dòng trống thiếu trước `check_schema_type` (`:240`): có sẵn từ trước trên `main` `1e49185` (cùng chỗ đó), không do lượt này; tôi không sửa để diff chỉ gồm phần được mở phạm vi. `ruff check .` sạch.
- Ghi `.env` của `set_password` vẫn là ghi đè trực tiếp như trước (không qua file tạm như `seo_app/env_file.py`): nếu máy tắt đúng lúc ghi thì `.env` có thể hỏng. Có từ trước, ngoài phạm vi; nếu muốn thì phiếu sau cho dùng cách ghi an toàn của `env_file.py`.

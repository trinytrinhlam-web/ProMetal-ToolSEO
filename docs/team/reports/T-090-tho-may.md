# Báo cáo T-090 · Dọn lỗi Thấp: câu báo emoji mới trong chữ SEO (SL-T041-8), `.env` không phải UTF-8 (SL-T084-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-090](../tickets/T-090-don-loi-thap-chu-seo-va-env.md) |
| Nhánh | `team/T-090` (worktree `D:\ProMetal-ToolSEO\wt-T-090`), gốc `main` `1e49185` |
| Ngày nộp | 2026-10-28 08:30 (+0700) |
| Kết quả | Hoàn thành (yêu cầu 1–3). Không cần sửa `app/**`: `app/main.py` đã hiện câu của `ConfigError` thành trang báo lỗi |

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

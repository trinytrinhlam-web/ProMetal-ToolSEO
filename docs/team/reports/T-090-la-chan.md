# Biên bản bảo mật T-090 · Dọn lỗi Thấp: câu báo emoji mới trong chữ SEO (SL-T041-8), `.env` không phải UTF-8 (SL-T084-1) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-090](../tickets/T-090-don-loi-thap-chu-seo-va-env.md) (lượt 1 và lượt 2 của Thợ Máy, test của Soi Lỗi) |
| Phạm vi | Rút gọn: U1, U2, S1 và 4 việc Chỉ Huy giao (không lộ thông tin ở câu báo, trang lỗi; không nới tập ký tự bị Chặn; `set_password` không ghi hỏng `.env`; gộp thử với `main`). Diff `1e49185...team/T-090`, đầu nhánh lúc kiểm `0207c88` (code lượt 2 `52ce068`, sau đó chỉ có test và báo cáo Soi Lỗi): `seo_app/config.py` (`_read_env_file`, câu cố định), `seo_app/onpage/meta.py` (`odd_char_kinds`, `odd_char_messages`), `seo_app/onpage/schema.py` (câu báo FAQ), `scripts/hash_password.py` (`read_env_lines`, bắt lỗi đọc, ghi); 3 file test mới, 5 file test đổi |
| Ngày | 2026-10-28 (Chỉ Huy giao 13:50; xong 14:17 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới** (LC-T090-1, LC-T090-2), cả hai **có từ trước** ở phần ghi `.env` của `set_password` (T-090 không đổi phần này; riêng LC-T090-2, câu báo mới dặn «chạy lại set_password» làm việc mất dữ liệu thành hẳn). Phần T-090 sửa đạt cả 4 việc: câu báo không lộ gì, tập ký tự bị Chặn không đổi (quét đủ 1.114.112 mã), gộp với `main` không xung đột. Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_la_chan_t090.py` |

## Tóm tắt (cho chủ dự án)

Phần sửa của T-090 **an toàn**. Khi file `.env` lưu sai kiểu chữ (Notepad «ANSI», UTF-16), bị chương trình khác khóa, hay là thư mục chứ không phải file, cả trang app lẫn cửa sổ `set_password` chỉ hiện câu tiếng Việt cố định: không đường dẫn trên máy, không chữ nào trong `.env`, không lỗi tiếng Anh. Tiêu đề, mô tả SEO và mục Hỏi đáp vẫn chặn đúng những ký tự như trước (tôi thử đủ mọi ký tự Unicode: không ký tự nào được nới); chỉ câu báo nói đúng hơn.

Tôi tìm thêm 2 điểm nhỏ ở `set_password` (bấm đúp để đổi mật khẩu đăng nhập app). Cả hai có từ khi làm phần mềm, không do T-090, không làm lộ mật khẩu hay khóa:

1. Nếu file `.env` có **hai dòng** `APP_PASSWORD_HASH` (ví dụ dòng trống của file mẫu và dòng bạn từng dán thêm ở cuối), `set_password` sửa dòng đầu, còn app đọc dòng cuối: cửa sổ báo «Đã lưu mật khẩu mới» nhưng mật khẩu mới không vào được, **mật khẩu cũ vẫn vào được**. Nếu gặp: mở `.env`, xóa hết các dòng `APP_PASSWORD_HASH` thừa, chỉ để một dòng, rồi chạy lại `set_password`.
2. Nếu đúng lúc lưu có một chương trình khác giữ file `.env` theo một kiểu khóa ít gặp (vẫn cho đọc, không cho ghi), file `.env` bị **xóa trắng** (mất khóa AI, mật khẩu ứng dụng WordPress, thư mục ảnh), mà câu báo lại bảo chạy lại `set_password`. Chạy lại thì `.env` chỉ còn mật khẩu app.

Cách sửa cả hai: cho `set_password` dùng cách ghi `.env` an toàn **đã có sẵn** ở trang Cài đặt (ghi ra file tạm rồi mới thay, đọc lại để kiểm). Tôi đã thử cách này: hết cả hai lỗi. Không gấp, không chặn gộp T-090; Chỉ Huy lập phiếu sửa sau.

## Lỗi phát hiện

Số dòng theo `0207c88`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T090-1 | Thấp (có từ Giai đoạn 0) | **`set_password` sửa `.env` theo dòng tự chế, khác cách app (python-dotenv) đọc.** (a) Thay dòng **đầu tiên** bắt đầu bằng `APP_PASSWORD_HASH=` hay `export APP_PASSWORD_HASH=` rồi `break`; python-dotenv lấy dòng **cuối** khi biến lặp lại. (b) Tách dòng bằng `str.splitlines()`, cắt cả ở FF (U+000C), VT (U+000B), FS, GS, RS (U+001C–U+001E), NEL (U+0085), U+2028, U+2029, mà python-dotenv chỉ coi CR, LF là xuống dòng; nối lại bằng LF | `scripts/hash_password.py:43` (`splitlines`), `:62-71` (vòng thay dòng đầu, `break`); lời dặn `:112` («Dán dòng sau vào file .env») | (a) `.env` chép từ `.env.example` (dòng 15 là `APP_PASSWORD_HASH=`), người dùng từng dùng `--print` (README dòng 492) và dán dòng mã băm xuống cuối như lời dặn → app dùng dòng cuối. Bấm đúp `set_password`, gõ mật khẩu mới → script thay dòng 15, in «Đã lưu mật khẩu mới vào …» → app vẫn dùng mã băm cũ: **mật khẩu mới bị từ chối, mật khẩu cũ vẫn đăng nhập được** (nếu đổi vì lộ mật khẩu thì việc đổi không có tác dụng). Cũng xảy ra khi dòng sau viết `APP_PASSWORD_HASH = …` (có dấu cách), `export …`, hay khi dòng giống hệt nằm trong giá trị nhiều dòng (có nháy) của biến khác (khi đó còn sửa hỏng biến kia). Thử: 26 `.env` dựng tay, 4 ca dòng trùng đều hỏng; 3.000 `.env` ngẫu nhiên (dòng trùng, `export`, dấu cách, BOM, CRLF, chú thích): **338** lần mật khẩu mới không có hiệu lực, không lần nào hỏng vì lý do khác. (b) Biến khác có một trong 8 ký tự trên trong giá trị (rất hiếm, ví dụ chữ dán từ PDF): không nháy thì giá trị bị **cắt cụt** và phần sau thành dòng rác, có nháy thì ký tự đổi thành xuống dòng: 16/16 ca | `set_password` ghi bằng bộ ghi của `seo_app/env_file.py` (`_write_value`: tách bằng `parse_stream` của python-dotenv, thay **mọi** dòng của biến, chép nguyên văn mọi đoạn khác, kiểm `_parse(nội dung mới)` đúng như mong đợi, ghi file tạm rồi `os.replace`, đọc lại, sai thì trả bản cũ); cần một hàm công khai không qua `validate_key_value` (mã băm có dấu `:`). Giả lập: 26/26 ca dựng tay và 3.000 mẫu ngẫu nhiên: **0 vấn đề**; 17/17 ca `xfail` của tôi chuyển sang qua |
| LC-T090-2 | Thấp (ghi đè trực tiếp có từ trước; câu báo mới ở lượt 2) | **Ghi `.env` không nguyên tử: lỗi ghi sau khi file đã bị cắt làm `.env` rỗng, câu báo mới dặn chạy lại.** `Path.write_text` mở kiểu `"w"` (Windows: `CREATE_ALWAYS`, cắt file về 0 byte) **rồi** mới ghi. Báo cáo Thợ Máy lượt 2 ghi «File `.env` không bị đụng tới khi báo lỗi»: đúng khi không mở được file, sai khi mở được mà ghi lỗi. Test `test_set_password_cannot_write_env` giả lỗi bằng cách đè `Path.write_text` (ném lỗi trước khi mở file) nên không thấy chỗ này | `scripts/hash_password.py:73-76` (`write_text`), câu `MSG_ENV_UNWRITABLE` `:31-34` | Thử thật trên máy Windows 11 của chủ dự án, `.env` giả trong thư mục tạm, chạy `main()` của script với `getpass` giả: một chương trình khác giữ `.env` bằng **khóa vùng byte kiểu chia sẻ** (`LockFileEx` không cờ độc quyền: mọi tiến trình đọc được, không ai ghi được) → bước kiểm đầu đọc được, người dùng gõ mật khẩu → `write_text`: Windows vẫn cho mở và **cắt `.env` về 0 byte**, ghi thì `PermissionError` → in «Chưa lưu mật khẩu mới. Không ghi được file .env (PermissionError). Đóng chương trình đang mở file (nếu có), kiểm tra quyền ghi file rồi chạy lại set_password.» → `.env` **0 byte**. Làm theo câu báo (chạy lại) → `.env` chỉ còn `APP_PASSWORD_HASH`: mất `WORDPRESS_*`, khóa AI, `IMAGE_FOLDERS` (khóa API và mật khẩu ứng dụng WordPress chỉ hiện một lần lúc tạo, nên phải tạo lại). Ba kiểu giữ file khác (khóa độc quyền, mở cấm ghi, ánh xạ bộ nhớ): file **giữ nguyên**, câu báo đúng. Mất điện đúng lúc ghi cũng cho file rỗng (Thợ Máy đã ghi ở «Rủi ro» lượt 2). Câu báo không lộ đường dẫn ở cả 4 kiểu | Như LC-T090-1 (ghi file tạm rồi `os.replace`): dưới khóa chia sẻ `os.replace` bị Windows từ chối, `.env` **giữ nguyên** (đã thử). Khi sửa: giữ chỗ bắt lỗi khi chép `.env.example`; `test_set_password_cannot_write_env` phải đổi cách giả lỗi (ví dụ đè `os.replace`), giữ điều kiện kiểm (câu cố định, file còn nguyên): R5, Chỉ Huy duyệt |

## Kết quả theo việc Chỉ Huy giao

**1. Câu báo và trang lỗi không lộ đường dẫn, traceback, nội dung `.env`, mật khẩu: đạt.**

- Câu báo là hằng (`seo_app/config.py:45-53`, `scripts/hash_password.py:24-34`), chỉ ghép **tên loại lỗi** (`type(exc).__name__`, ví dụ `PermissionError`); lỗi gốc (có đường dẫn trong `exc.filename`) chỉ nối bằng `from exc`, không in. `app/main.py:66-70` bắt `ConfigError`, hiện `st.error(câu)` rồi dừng (không ô mật khẩu, không trang nào khác chạy trong lượt đó); `set_password` in câu rồi thoát mã 1.
- Đã có test của Thợ Máy, Soi Lỗi (mở app thật bằng `AppTest`, quét chữ trên trang): cp1252, cp1258, UTF-16 LE/BE có BOM, surrogate kiểu CESU-8, mã hóa dài thừa, byte hỏng sau 80 dòng đúng, khóa độc quyền thật. Tôi thử thêm `set_password` dưới **4 kiểu giữ file thật** (khóa độc quyền đặt lúc đang gõ mật khẩu, khóa chia sẻ, mở cấm ghi, ánh xạ bộ nhớ) và `.env` là **thư mục**: mọi câu in ra không có đường dẫn thư mục tạm, không «Traceback»; app với `.env` là thư mục: không lỗi, coi như chưa đặt mật khẩu.
- BOM: python-dotenv 1.2.4 bỏ BOM khi đọc (`dotenv/parser.py`, `removeprefix`), nên `.env` «UTF-8 with BOM» đọc đúng; BOM kèm byte hỏng thì ra câu cố định.

**2. Không nới tập ký tự bị Chặn: đạt** (script `p_odd_equiv.py`, 90 s + 100 s + 7 s).

- Meta: Chặn mới là `any(odd_char_kinds(chữ gốc))`, cũ là `has_odd_chars(chữ gốc)`. FAQ: mới là `any(odd_char_kinds(normalize_text(x)))`, cũ là `_has_control` (loại Cc, Cs, Co, Cn) trên chữ đã chuẩn hóa. Mỗi mã trong **1.114.112** mã thử ở 5 ngữ cảnh (đứng riêng, giữa chữ, giữa dấu cách, sau nguyên âm có dấu, cạnh xuống dòng): **0 khác biệt** ở cả hai bên (5.570.560 chữ mỗi bên).
- Vì sao FAQ bỏ qua khoảng trắng mà không nới: `normalize_text` thay mọi dãy `\s` của `re` (trùng `str.isspace`) bằng một dấu cách rồi cắt hai đầu, NFC cuối không tạo ra khoảng trắng mới; dấu cách thường là loại Zs, không thuộc tập bị Chặn.
- Nối dây: `check_title` với **mọi** mã: 0 ca có ký tự lạ mà không Chặn; `check_description` 1/7 số mã: 0; `build_faq_page` 5.767 mã (mọi Cc, Cs, Cn ở BMP, 200 mã Co, 2.000 mã ngẫu nhiên): sót Chặn 0, báo ký tự lạ thừa 0. Câu báo chỉ có tên ô hay «Câu hỏi n / Trả lời n», không chép lại ký tự.

**3. `set_password` không ghi hỏng hay làm mất dòng khác: chưa đạt hẳn, 2 lỗi Thấp có từ trước** (LC-T090-1, -2 ở trên). Các dạng thường gặp vẫn đúng: một dòng, CRLF (ghi lại thành LF, giá trị không đổi), «UTF-8 with BOM» có dòng mã băm ngay đầu (dòng mới thêm cuối, app dùng dòng mới; dòng cũ còn nhưng không hiệu lực, như Soi Lỗi ghi), `export`, thiếu xuống dòng cuối, chưa có dòng nào (test canh `test_lc1_guard_single_line_cases_keep_working`). `.env` sai bảng mã: báo trước khi hỏi mật khẩu, file giữ nguyên từng byte (test Thợ Máy).

**4. Gộp thử với `main` mới nhất: đạt.** `main` cục bộ `1b45f5d` (Gộp T-096; lúc kiểm `origin/main` vẫn là `5e1d831`, chưa có bản gộp này). `git merge-tree --write-tree main team/T-090` → cây `3965c31`, **không xung đột**; hai bên không chung file nào (`main` đổi `seo_app/publish/*`, `seo_app/onpage/links.py`, test T-096; T-090 đổi `config.py`, `meta.py`, `schema.py`, `hash_password.py`). Mã T-096 chỉ nhập `Level`, `worst` từ `meta.py`; không chỗ nào trên cây gộp còn dùng `_has_control` hay `schema._ODD_CATEGORIES` đã bỏ. Test trên cây gộp (commit tạm `6807e90`, worktree nháp, không giữ), 24 file: 3 file test T-090, 5 file test T-090 đổi, `test_hash_password_script.py`, `test_config.py`, `test_config_tolerance.py`, `test_env_file.py`, `test_onpage_meta.py`, `test_onpage_schema.py`, `test_soi_loi_t036.py`, `test_soi_loi_t038.py`, 4 file test T-096 (`test_publish_markdown.py`, `test_publish_render.py`, `test_soi_loi_t096.py`, `test_la_chan_t096.py`), `test_la_chan_t039.py`, `test_onpage_links.py`, `test_t041_seo_ui.py` (bước SEO trên trang thật), `test_app.py` (14:02:15 → 14:12:53): **2.225 passed, 4 skipped, 9 xfailed, 0 hỏng**. 9 `xfail` đều là lỗi đã biết có sẵn trên `main` (chạy lại riêng 7 file có dấu `xfail`: 773 passed, 9 xfailed): SL-T036-11 (4 ca), SL-T036-10 phần «đô vật» (1), LC-T096-5 (4); không ca nào của T-090. 4 bỏ qua là điều kiện bỏ qua có sẵn (ví dụ `tests/test_env_file.py` chỉ chạy trên Mac/Linux).

**5. R5 (test cũ đã đổi): đúng quy tắc.**

| File | Thay đổi | Kết luận |
|---|---|---|
| `tests/test_la_chan_t041.py` (của tôi ở T-041) | Gỡ 4 dòng `xfail` của `test_sl8_new_emoji_stays_blocked_with_accurate_message`; thân test không đổi | Đúng: đây là hướng sửa tôi đặt ở T-041 (giữ Chặn, câu báo không nói «không nhìn thấy») |
| `tests/test_soi_loi_t084.py` | Gỡ 4 dòng `xfail` SL-T084-1; thân test không đổi | Đúng |
| `tests/test_soi_loi_t041.py` | Test SL-T041-8 đổi hướng: từ «không Chặn» sang «Chặn, câu có "chưa nhận ra", không có "không nhìn thấy"», thêm dòng «chữ ghi đi mất emoji» | Phiếu ghi **Chỉ Huy duyệt** đổi test này (dòng 19); hướng mới khớp quyết định Lá Chắn T-041 |
| `tests/test_t041_meta.py`, `tests/test_t041_schema.py` (của Thợ Máy) | Ca U+0378 (chưa gán) mong câu mới «chưa nhận ra»; các ca khác giữ câu cũ | Không bớt ca, vẫn kiểm Chặn và không chép lại ký tự: không nới |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` 1.5.0 (`PYTHONUTF8=1`, `--all-files` trong thư mục nháp): bản sao 15 file (code, test, báo cáo của nhánh và `tests/test_la_chan_t090.py`), bản vá `git log -p 1e49185..0207c88`, **file mồi có chữ tiếng Việt** (khóa AWS giả, `password = …` giả): mồi **bắt 2/2**; các mục còn lại là chuỗi mồi đã biết hay chữ trong báo cáo (mục «Báo nhầm»). Soát bản vá theo dạng khóa (`sk-ant-`, `AIza…`, `ghp_`, `PRIVATE KEY`, `xox`, `AKIA…`): 0 |
| S2 | Đạt | Câu báo chỉ có tên loại lỗi; không in nội dung `.env`, giá trị biến hay mã băm |
| S3 | Không áp dụng | Không có biến cấu hình mới (`.env.example` không đổi) |
| W1–W4 | Không áp dụng | Không đụng client WordPress |
| A1–A3 | Không áp dụng | Không đụng AI |
| U1 | Đạt | `st.error(str(exc))`, không `unsafe_allow_html`; câu là hằng |
| U2 | Đạt | Trang báo lỗi hiện trước đăng nhập nhưng chỉ câu cố định; `main()` dừng ngay, không trang nào chạy; `server.address = "localhost"` không đổi (`.streamlit/config.toml` không đổi) |
| U3 | Đạt, kèm LC-T090-1 | PBKDF2, so sánh an toàn không đổi; LC-T090-1: `set_password` có thể ghi mã băm mới vào dòng không có hiệu lực |
| F1 | Không áp dụng | Đường dẫn `.env` cố định (`DEFAULT_ENV_FILE`) |
| F2 | Không áp dụng | |
| F3 | Đạt, kèm LC-T090-2 | Đọc, ghi `encoding="utf-8"`; python-dotenv chỉ đọc, không chạy nội dung; ghi không nguyên tử là LC-T090-2 |
| D1 | Đạt | Không thư viện mới (`pyproject.toml`, `uv.lock` không đổi) nên không chạy lại pip-audit |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới chỉ dùng `.env` giả trong thư mục tạm, `getpass` giả; bộ chặn mạng của `tests/conftest.py` vẫn bật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy: không đổi thư viện | Có (`git diff 1e49185 0207c88 -- pyproject.toml uv.lock` rỗng) |
| bandit | `PYTHONUTF8=1 uvx --offline bandit` 4 file code của diff (1.400 dòng): **No issues identified** | Có |
| detect-secrets | Mồi 2/2; còn lại là báo nhầm (dưới) | Có. Đã xóa file mồi |
| Soát lịch sử git | Bản vá 8 commit của nhánh (`1e49185..0207c88`): 0 dạng khóa | Có |
| pytest / ruff | Nhánh: `tests/test_la_chan_t090.py` **11 passed, 17 xfailed**; giả lập cách sửa (plugin `lc090_fix_plugin.py`): 17/17 ca `xfail` thành XPASS (sửa đúng thì qua). Cây gộp: xem việc 4. `uv run ruff check .` (nhánh, có file test mới): All checks passed!; `ruff format --check tests/test_la_chan_t090.py`: đã định dạng | Có |

## Báo nhầm đã loại

| Công cụ | Vị trí | Lý do |
|---|---|---|
| detect-secrets | `tests/test_t090_env_bang_ma.py:30` (`FAKE_KEY`) | Chuỗi mồi giả của Thợ Máy (lượt 1), đã ghi trong báo cáo Thợ Máy |
| detect-secrets | `tests/test_t041_schema.py:212`, `tests/test_la_chan_t041.py:5`, `:34` | Có từ T-041: chuỗi mồi (`MA-BI-MAT-T041`, `MAT-KHAU-GIA-T041`) và ví dụ `https://tên:mật-khẩu@site` trong lời mô tả test |
| detect-secrets | `docs/team/reports/T-090-tho-may.md:325`, bản vá dòng 609, 778 | Chữ «detect-secrets», «secret» trong báo cáo; dòng ngữ cảnh `PASSWORD = "mat-khau-thu-t090"` (mật khẩu giả của test Soi Lỗi) |

`tests/test_la_chan_t090.py` ghép mật khẩu giả lúc chạy (`"-".join([...])`, cách Soi Lỗi gợi ý) nên máy quét không báo.

## Quan sát (không phải lỗi, không cần sửa ở phiếu này)

- `set_password` thành công vẫn in «Đã lưu mật khẩu mới vào {đường dẫn}» (`:120`, có từ trước): in ra cửa sổ của chính người dùng, không lên trình duyệt. Thợ Máy đã nêu.
- `ConfigError` múi giờ chép lại giá trị `APP_TIMEZONE` lên trang lỗi (`config.py:134-136`, có từ trước): không phải bí mật.
- Các trang gọi lại `load_settings()` ở đầu trang (`app/views/home.py:10`, `plan.py:8`, `settings.py:507`, `wordpress.py:27`, vài chỗ trong `write.py`) mà không bắt `ConfigError`. `.env` chỉ có thể hỏng giữa lần đọc của `main.py` và lần đọc của trang trong **cùng một lượt chạy** (vài mili giây) thì Streamlit mới hiện traceback; không có `st.fragment` nào. Đề xuất 4 của Thợ Máy (`client.showErrorDetails`) đủ che, chờ chủ dự án.

## Ý kiến về quan sát của Soi Lỗi

- «`set_password` với BOM và dòng mã băm ngay đầu: dòng cũ không được thay, dòng mới thêm cuối, app vẫn đúng»: **đồng ý, không phải lỗi bảo mật** (dòng cũ không có hiệu lực). Cách sửa LC-T090-1 (bộ ghi `env_file.py` bỏ BOM trước khi tách, thay đúng dòng) xử lý luôn.
- `test_soi_loi_t037` hỏng oan khi máy bận: không liên quan bảo mật.

## Điều kiện

1. Chỉ Huy lập phiếu sửa **LC-T090-1** và **LC-T090-2** (gợi ý gộp một phiếu: `set_password` ghi bằng bộ ghi của `seo_app/env_file.py`), ghi vào sổ rủi ro tới khi sửa. Không chặn gộp T-090. Khi sửa: gỡ `xfail` theo R5 (không đổi điều kiện kiểm); đổi cách giả lỗi của `test_set_password_cannot_write_env` cần Chỉ Huy duyệt (R5).
2. Kiểm lại bằng Claude Fable sau 01/11.

## Test mới của Lá Chắn

`tests/test_la_chan_t090.py` (28 ca, chạy khoảng 3–8 giây; gọi `main()` của script như bấm đúp `set_password`, `getpass` giả, `.env` giả trong thư mục tạm):

| Test | Loại | Kiểm |
|---|---|---|
| `test_lc1_duplicate_lines_old_password_is_the_active_one_before` (4) | Canh tiền đề | Trước khi đặt lại, app dùng mã băm của dòng cuối (mật khẩu cũ) |
| `test_lc1_new_password_takes_effect_with_duplicate_lines` (4) | `xfail(strict=True)` | Dòng mẫu rỗng + dòng dán cuối; dòng sau có dấu cách; dòng sau có `export`; dòng giống hệt trong giá trị nhiều dòng: mật khẩu mới có hiệu lực, mật khẩu cũ hết, biến khác giữ nguyên |
| `test_lc1_other_values_kept_when_they_hold_unicode_line_separators` (12) | `xfail(strict=True)` | FF, VT, RS, NEL, U+2028, U+2029 trong giá trị biến khác (có và không nháy): giá trị giữ nguyên |
| `test_lc1_guard_single_line_cases_keep_working` (6) | Canh hướng sửa | Một dòng, CRLF, BOM dòng đầu, `export`, chưa có dòng, thiếu xuống dòng cuối: vẫn đúng |
| `test_lc2_shared_lock_lets_others_read_but_not_write` (Windows) | Canh tiền đề | Dưới khóa chia sẻ: đọc được, ghi lỗi |
| `test_lc2_env_never_emptied_when_write_fails` (Windows) | `xfail(strict=True)` | Ghi lỗi dưới khóa chia sẻ: không mất biến nào; báo «Chưa lưu» thì file còn nguyên từng byte; câu báo không đường dẫn, không traceback |

Script thử (thư mục nháp của phiên, chép vào thư mục ghi chú chung `T-090-la-chan-scripts/`, chạy trong worktree `PYTHONUTF8=1 uv run python <script>`): `p_env_roundtrip.py [hạt giống] [số mẫu]` (so biến trước, sau `set_env_value` bằng python-dotenv), `p_env_lock_write.py` (4 kiểu giữ file thật, có bước «chạy lại như câu báo dặn»), `p_fixsim.py <thư mục script>` (giả lập sửa bằng `env_file._write_value`), `p_odd_equiv.py` (quét cả bảng mã), `fixsim/lc090_fix_plugin.py` (`PYTHONPATH=<fixsim> uv run pytest -p lc090_fix_plugin tests/test_la_chan_t090.py`).

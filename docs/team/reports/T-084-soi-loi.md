# Báo cáo T-084 · Trang Cài đặt → Ảnh không in đường dẫn đầy đủ của thư mục ảnh · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-084](../tickets/T-084-cai-dat-anh-khong-in-duong-dan.md) |
| Ngày nộp | 2026-10-27 |
| Nhánh | `team/T-084` (kiểm code `98feec1`, gốc `main` `b60054f`) |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT, chuyển Lá Chắn rút gọn được ngay.** Phần sửa của T-084 không có lỗi; hai hàm chép sang `settings.py` khớp bản gốc trong `write.py`. Lỗi: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp có từ trước** (SL-T084-1, không do T-084, nằm ngoài phạm vi phiếu), **không lỗi nào phải sửa trước Lá Chắn**. Soát R5: đạt |

## Tóm tắt (cho chủ dự án)

- Tab **Cài đặt → 🖼️ Ảnh** làm đúng: mỗi thư mục ảnh chỉ hiện số thứ tự và tên thư mục cuối, kèm «tìm thấy», lý do không dùng được, hay «đi qua lối tắt». Tôi đã thử nhiều cách khai báo lạ trong `IMAGE_FOLDERS` (thiếu ổ đĩa, `.`, `..`, `~`, tên thiết bị như `NUL`, `CON`, có dấu nháy, ký tự hỏng, chỉ có dấu `;`, ổ đĩa gốc, lối tắt nối tiếp lối tắt, ổ mạng không có) và nhiều tên thư mục lạ (ký tự ẩn, ký tự đảo chiều chữ, dấu Markdown, công thức `$…$`, tên rất dài): trang không lỗi, không lộ đường dẫn đầy đủ.
- Tôi quét **cả trang Cài đặt** (mọi tab, mọi chữ, gợi ý, ô nhập) khi mọi dòng trong `.env` đều có giá trị (khóa AI giả, mật khẩu WordPress giả, đường dẫn file Google, thư mục ảnh), kể cả sau khi bấm «Kiểm tra» khóa và «Lưu» khóa sai: không hiện giá trị nào, không hiện đường dẫn nào.
- Có **1 lỗi nhỏ có từ trước** (không do phiếu này, sửa ở phiếu khác): nếu file `.env` bị lưu sai bảng mã (ví dụ Notepad cũ lưu kiểu «ANSI»), app không mở được trang nào và hiện một khung lỗi tiếng Anh kèm đường dẫn thư mục cài app, thay vì câu tiếng Việt dặn lưu lại file bằng UTF-8.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t084.py` | Mới: 32 ca (30 qua, 2 `xfail(strict=True)` SL-T084-1). Dùng lại hàm giúp của `tests/test_settings_images.py` (Họa Sĩ) |
| `docs/team/reports/T-084-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| 1. Liệt kê qua `ImageLibrary.roots()`; tên ngắn đã escape, cô lập hướng chữ; tìm thấy / không thấy; báo lối tắt | **Đạt** | Test của Họa Sĩ (11) qua. Thêm: khai báo lạ (`test_odd_declaration_shown_without_path` × 13: `.`, `..`, `…\Anh tot\..`, dấu `/` cuối, `..\Anh tot\.`, dấu nháy, `  ;  …  ;;  `, và trên Windows `C:Anh`, `\\?\…`, `\\.\C:\`, `NUL`, `C:\NUL`, `C:\Windows\CON`): dòng đúng câu, không lỗi trang. `~` chỉ hiện tên thư mục nhà (`test_home_folder_shows_only_its_name`). Chỉ có dấu `;` hay khoảng trắng: «Chưa khai báo» (× 3). Ký tự NUL trong `.env`: mục đó «�» và «Chưa thấy», mục khác vẫn hiện (`test_nul_in_env_file_entry`). Tên lạ thật trên ổ (`test_odd_folder_name_matches_write_page_rule` × 7: `$x^2$ ---`, 120 ký tự, RLO và các dấu hướng chữ, BOM, gạch nối mềm, chữ Hangul trống, dấu kết hợp chồng nhau, `[a](…) ~~…~~ ==…== ^…^ {b} @x #1`): dòng đúng luật hiện tên của trang Soạn bài, không HTML. Lối tắt nối tiếp lối tắt và thư mục bên trong (`test_link_to_link_is_reported`) |
| 2. Không in đường dẫn tuyệt đối hay nội dung `.env` ở bất kỳ chỗ nào | **Đạt** cho tab Ảnh và cả trang Cài đặt (trừ SL-T084-1, có từ trước, toàn app) | `test_whole_settings_page_never_shows_env_values_or_paths`: `.env` có đủ 10 biến (địa chỉ WordPress có tên và mật khẩu, mật khẩu ứng dụng, 3 khóa AI giả, đường dẫn file Google, mã Sheet, GSC, hai thư mục ảnh); quét mọi chuỗi trong mọi phần tử của trang (chữ, nhãn, `help`, giá trị ô nhập) sau khi mở trang, sau khi bấm «Kiểm tra» từng khóa (mạng bị chặn: câu cố định kèm tên loại lỗi), sau khi «Lưu» khóa có dấu cách: không giá trị nào, không thư mục tạm, thư mục nhà, file `.env`, không `st.exception`. Câu báo lỗi của tab Mô hình AI (`config/ai.toml`, `config/content.toml`) chỉ có tên file (đọc mã `seo_app/ai/registry.py`, `seo_app/content/rules.py`) |
| 3. Giữ phần còn lại của tab; `tests/test_app_pages.py` vẫn qua | **Đạt** | Test của Họa Sĩ `test_rest_of_the_tab_unchanged`; `tests/test_app_pages.py` qua (mục «Bằng chứng») |
| So hai bản hàm chép với bản gốc trong `write.py` | **Khớp, không lệch** | `test_copied_name_rule_matches_write_page`: `_HIDDEN_IN_NAME` bằng nhau; `folder_name_md` (Cài đặt) cho đúng kết quả `name_md` (Soạn bài) trên 15 tên, kể cả tên không tạo được trên Windows (`:red[…]`, `:material/delete:`, `<img …>`, `&lt;b&gt;`, xuống dòng, NUL, nửa cặp surrogate, ký tự riêng, ký tự thẻ, chuỗi rỗng). `test_copied_link_check_is_same_code`: thân `through_link` và `_through_link` giống hệt (so cây cú pháp). `test_copied_link_check_same_answers`: cùng kết quả trên 11 đường dẫn (thư mục thật, lối tắt, lối tắt nối tiếp, bên trong lối tắt, không có, tương đối, `~`, ổ gốc, có NUL). Hai hàm lấy từ mã nguồn (không nhập file trang): ai sửa một bên mà quên bên kia thì các test này hỏng. Khác biệt duy nhất: `root_notes` của Soạn bài có kiểm `root.index < len(folders)`; ở Cài đặt không cần (danh sách gốc và danh sách khai báo lấy từ cùng một `settings`) |
| `st.exception`, câu báo lỗi, gợi ý (`help`) | **Đạt** trên trang Cài đặt | Không ca nào ở trên sinh `st.exception`; `help` của trang chỉ là câu cố định (đọc mã). Lỗi hệ điều hành quanh `roots()` ra câu cố định (test Họa Sĩ). Ổ mạng không có (`\\khong-ton-tai-t084-soiloi\share\a\b\c\d`): `roots()` và kiểm lối tắt từng tầng xong ngay (đo tay: dưới 0,1 giây mỗi bước), không treo trang |

## Lỗi tìm thấy

Test `xfail(strict=True)` trong `tests/test_soi_loi_t084.py` (`--runxfail`: hỏng đúng câu kiểm «không có `st.exception`»).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T084-1 | Thấp, **có từ trước** (không do T-084; ngoài phạm vi phiếu: `app/main.py`, `seo_app/config.py`) | File `.env` không đọc được dạng UTF-8 làm app sập ngay từ đầu, mọi trang (kể cả Cài đặt, cả trước màn đăng nhập) hiện traceback tiếng Anh có đường dẫn tuyệt đối | `test_env_file_not_utf8_fixed_message_no_traceback[ansi, utf16]`: `.env` lưu kiểu «ANSI» (`IMAGE_FOLDERS=C:/Ánh công trình`, cp1252) hay UTF-16 có BOM; mở app | Câu tiếng Việt cố định, ví dụ như `env_file` đã có khi lưu khóa («File .env không đọc được dạng UTF-8. Mở và lưu lại bằng UTF-8.»), không traceback, không đường dẫn | `load_settings` (`seo_app/config.py:112`, `dotenv_values(..., encoding="utf-8")`) ném `UnicodeDecodeError`; `app/main.py:67-70` chỉ bắt `ConfigError` nên Streamlit hiện «'utf-8' codec can't decode byte 0xc1…» kèm traceback: `D:\ProMetal-ToolSEO\…\app\main.py`, `…\seo_app\config.py`, `…\.venv\Lib\site-packages\dotenv\main.py`… (thư mục cài app, có thể có tên tài khoản máy). Không lộ nội dung `.env`. Cùng đường: `.env` không có quyền đọc (`PermissionError`) | Phiếu riêng (Thợ Máy): `load_settings` bắt `UnicodeDecodeError`, `OSError` khi đọc `.env` và ném `ConfigError` câu tiếng Việt cố định (không đường dẫn); test như trên. Có thể cân nhắc thêm `client.showErrorDetails` trong `.streamlit/config.toml` để mọi lỗi lạ chỉ hiện tên loại lỗi (đổi cấu hình, cần chủ dự án duyệt) |

## Ghi nhận (không phải lỗi)

1. Khai báo `~` (thư mục nhà) thì tab hiện tên thư mục nhà, tức tên tài khoản máy (ví dụ «ADMIN»). Chỉ là tên thư mục cuối như mọi gốc khác, không phải đường dẫn; chấp nhận.
2. Ký tự trông như khoảng trống nhưng là chữ (chữ Hangul trống U+3164, U+115F, U+1160, U+FFA0; ô chữ nổi trống U+2800) không bị đổi thành «�» nên một thư mục có thể trông như không có tên. Luật hiện tên dùng chung với trang Soạn bài; khi đưa hai hàm ra module dùng chung (Đề xuất của Họa Sĩ) có thể thêm các ký tự này.
3. Gốc khai báo kết thúc bằng `..` hiện tên «..» (đúng là tên tầng cuối của đường dẫn khai báo, không lộ gì, chỉ không rõ nghĩa).
4. Chưa thử trên trình duyệt (ngoài phạm vi phiếu): Markdown của Streamlit có thể giải mã tham chiếu ký tự có tên như `&rlm;`, `&ZeroWidthSpace;` thành ký tự ẩn. Tên thư mục gốc không chứa được `;` (dấu tách của `IMAGE_FOLDERS`) nên tab Ảnh không bị; tên file, thư mục con ở trang Soạn bài thì có thể. Nên kiểm khi làm module dùng chung.
5. Không mở app thật: các ca trên chạy bằng `AppTest` với thư mục, lối tắt (junction) thật trên Windows; Họa Sĩ đã mở app thật kiểm HTML cả trang.

## Soát R5

- `git diff b60054f..98feec1 -- tests/`: chỉ thêm `tests/test_settings_images.py` (mới). Không sửa, không `skip`, không xóa test cũ.

## U1, U2 (soát nhanh)

- U1: tab Ảnh chỉ dùng `st.markdown`, `st.warning`, `st.caption` thường, không `unsafe_allow_html` (test kiểm `allow_html` của mọi ô Markdown, chú thích trong tab là `False`); chữ lấy từ máy qua `folder_name_md` (escape gồm cả `:` và `$`, nên `:red[…]`, `:material/…:`, `$…$` hiện nguyên văn).
- U2: trang vẫn sau màn đăng nhập (`app/main.py`), `.streamlit/config.toml` không đổi (`address = "localhost"`); tab hết in đường dẫn tuyệt đối.
- Test không gọi mạng thật (bộ chặn mạng của `tests/conftest.py`).

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest -rxXfs tests/test_app_pages.py tests/test_settings_images.py \
    tests/test_app.py tests/test_app_t044_safe_text.py tests/test_settings_blind.py \
    tests/test_settings_keys.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t023.py tests/test_soi_loi_t044.py \
    tests/test_soi_loi_t062.py tests/test_soi_loi_t084.py
471 passed, 6 skipped, 2 xfailed in 226.11s (0:03:46)   # code 98feec1; 2 xfail = SL-T084-1
# 6 bỏ qua có sẵn trong test_soi_loi_t016_t020.py (symlink cần quyền đặc biệt, quyền kiểu POSIX).
# Trước khi thêm file của Soi Lỗi (Họa Sĩ, cùng 12 file): 441 passed, 6 skipped.

$ uv run pytest tests/test_soi_loi_t084.py --runxfail -k not_utf8
2 failed   # hỏng đúng câu kiểm: assert not at.exception
           # ("'utf-8' codec can't decode byte 0xc1 in position 17", "… 0xff in position 0")

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t084.py docs/team/reports/T-084-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Không đọc `.env` thật (test dùng `.env` tạm); khóa, mật khẩu trong test là chuỗi giả để dò.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Thử tên thư mục độc hại (RLO, ký tự rộng 0, Markdown, HTML, tên rất dài), gốc không tìm thấy, gốc là file, đường dẫn tương đối, lối tắt/junction, ổ đĩa gốc, `IMAGE_FOLDERS` trống/hỏng.
- [x] Tìm mọi chỗ trên trang Cài đặt còn lộ đường dẫn tuyệt đối hay nội dung `.env` (câu báo lỗi, `st.exception`, `help`): chỉ còn SL-T084-1 (có từ trước, toàn app).
- [x] So hai bản hàm chép với bản gốc: khớp; có test chặn lệch.
- [x] Lỗi có test `xfail(strict=True)` mã SL-T084-n; không sửa code ứng dụng.
- [x] Test liên quan và `ruff` (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.

## Đề xuất

- **Thợ Máy (phiếu nhỏ):** SL-T084-1 theo cột «Gợi ý sửa».
- **Họa Sĩ (khi làm module dùng chung theo Đề xuất của báo cáo T-084):** chuyển `test_copied_*` của file này sang so một bản duy nhất; xem Ghi nhận 2, 4.

## Câu hỏi cho chủ dự án

Không có.

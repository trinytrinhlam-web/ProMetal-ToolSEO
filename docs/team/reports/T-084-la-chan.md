# Biên bản bảo mật T-084 · Tab Ảnh của trang Cài đặt không in đường dẫn đầy đủ · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-084](../tickets/T-084-cai-dat-anh-khong-in-duong-dan.md) · kiểm **rút gọn** (U1, U2) |
| Phạm vi | Diff `b60054f..0b07ff4`: `app/views/settings.py` (tab Ảnh: `folder_name_md`, `through_link`, `image_folders_list`), test mới `tests/test_settings_images.py` (Họa Sĩ), `tests/test_soi_loi_t084.py` (Soi Lỗi), 2 báo cáo. Không đổi `seo_app/**`, `config/**`, `app/views/write.py`, `.streamlit/`, `uv.lock`. Soát U2 cả trang Cài đặt (mọi tab). Số dòng theo `0b07ff4` |
| Báo cáo đã đọc | [Họa Sĩ](T-084-hoa-si.md), [Soi Lỗi](T-084-soi-loi.md) (SL-T084-1) |
| Ngày | 2026-10-27 (18:17 → 18:24 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp có từ trước** (SL-T084-1 của Soi Lỗi, giữ Thấp; không do T-084, ngoài phạm vi phiếu); Lá Chắn không có lỗi mới. U1, U2 đạt cho tab Ảnh và cả trang Cài đặt; hai bản hàm chép khớp bản gốc. **Gộp `main` được ngay**: thử gộp với `origin/main` `4671104` không xung đột (từ gốc nhánh `main` chỉ đổi tài liệu). Điều kiện: phiếu riêng cho SL-T084-1 |

## Tóm tắt (cho chủ dự án)

- Tab **Cài đặt → 🖼️ Ảnh** nay chỉ hiện số thứ tự và tên thư mục cuối của từng thư mục ảnh (như trang Soạn bài), kèm «tìm thấy», lý do không dùng được, hay «đi qua lối tắt». Không còn in đường dẫn đầy đủ trên máy. Tên thư mục lạ (ký tự ẩn, ký tự đảo chiều chữ, dấu định dạng, địa chỉ web) hiện nguyên văn, không thành link hay chữ đậm, chữ màu. Cả trang Cài đặt không hiện khóa, mật khẩu, nội dung file `.env` hay câu lỗi của Windows. Bản sửa an toàn để gộp.
- Còn **1 lỗi nhỏ có từ trước** (Soi Lỗi tìm ra, không do phiếu này): file `.env` lưu sai bảng mã (ví dụ Notepad lưu kiểu «ANSI» khi có chữ có dấu) thì app không mở được trang nào và hiện khung lỗi tiếng Anh có đường dẫn thư mục cài app trên máy. Không lộ khóa hay mật khẩu; chỉ người ngồi ở máy này thấy (app chỉ mở trên máy). Nên sửa ở một phiếu riêng. Trong lúc chờ: luôn lưu `.env` bằng UTF-8.

## Lỗi phát hiện

Không phát hiện lỗi mới (Lá Chắn). Lỗi của Soi Lỗi: mục «Mức SL-T084-1».

## U1, U2 và hai bản hàm chép

| Điểm kiểm | Kết quả | Bằng chứng |
|---|---|---|
| **U1**: tên thư mục độc hại không thành Markdown, HTML, link; không đảo chiều chữ | **Đạt** | `image_folders_list` (`settings.py:468-505`) hiện mỗi gốc một dòng `số. tên — trạng thái`. Tên qua `folder_name_md` (`:451-456`): ký tự loại Cc, Cf, Cs, Co, Cn, Zl, Zp thành «�» (RLO, LRI và mọi dấu hướng chữ, ký tự rộng 0, BOM, xuống dòng, U+2028, U+2029: tên không mở dòng mới trong danh sách), cả tên nằm trong cặp cô lập hướng chữ U+2068 … U+2069, rồi `escape_markdown` (`seo_app/text.py`): escape ``\ ` * _ { } [ ] ( ) < > # + - . ! | ~ : $`` (link, ảnh, thẻ HTML, `:red[…]`, `:material/…:`, emoji `:…:`, công thức `$…$`) và `break_autolinks` cho `www.`, `https://`, email (T-031). Trạng thái là câu cố định (`root.message` của `ImageLibrary`, cũng qua `escape_markdown`). `settings.py` không có `unsafe_allow_html=True` nào (chữ `unsafe_allow_html` duy nhất là chú thích `:443`). Tham chiếu ký tự HTML (`&rlm;`, `&#8238;`) cần dấu `;`, mà `;` là dấu tách của `IMAGE_FOLDERS` nên tên gốc không chứa được. Test qua: Họa Sĩ (RLO, rộng 0, Markdown), Soi Lỗi `test_odd_folder_name_matches_write_page_rule` × 7, ô Markdown và chú thích trong tab đều `allow_html` tắt |
| **U2**, tab Ảnh: không đường dẫn tuyệt đối, không câu lỗi hệ điều hành | **Đạt** | Tên chỉ từ `RootInfo.label` = tên tầng cuối của đường dẫn khai báo (`folder.name`; ổ gốc, gốc UNC thì «Thư mục ảnh N», `seo_app/images/folders.py:603`). `message` là câu cố định của `ImageFolderError`, chỉ có số thứ tự thư mục (`folders.py:88-99`, `_root` `:612-631`). `_root` bắt `OSError`, `RuntimeError` của `resolve` (lỗi vòng lối tắt của `pathlib` có đường dẫn trong câu) thành câu cố định (`:625`); lỗi còn lại có thể ra khỏi `roots()` (`OSError` khi xem thư mục, `ValueError`) bị tab bắt thành câu cố định (`settings.py:475-483`), câu gốc của Windows không lên trang. `through_link` nuốt `OSError`, `RuntimeError`, `ValueError`, chỉ trả đúng/sai (`:459-465`). Câu cảnh báo lối tắt, chú thích dưới danh sách đều cố định |
| **U2**, cả trang Cài đặt: không đường dẫn, không nội dung `.env`, không câu lỗi hệ điều hành | **Đạt** (trừ SL-T084-1, có từ trước, cả app) | Tab Kết nối chỉ báo «đã khai báo / chưa khai báo», không hiện khóa (`settings.py:552-580`). Lưu, xóa khóa: câu của `EnvFileError` chỉ có tên loại lỗi, không đường dẫn, không nội dung `.env` (`seo_app/env_file.py:96-117`, `:218-227`). Kiểm khóa: câu cố định kèm tên loại lỗi (`settings.py:123-128`). Câu lỗi `config/ai.toml`, `config/content.toml` chỉ có tên file và vị trí lỗi cú pháp (`seo_app/ai/registry.py:73-91`, `seo_app/content/rules.py:349-365`). Thử mù: câu lỗi lớp AI cố định, qua `escape_link_syntax`. Soi Lỗi quét mọi chuỗi của cả trang với `.env` đủ 10 biến, cả sau khi bấm «Kiểm tra» và «Lưu» khóa sai (`test_whole_settings_page_never_shows_env_values_or_paths`): không giá trị nào, không đường dẫn nào, không `st.exception` |
| Hai bản hàm chép có lệch bản gốc không | **Khớp** | `folder_name_md` cho đúng kết quả `name_md` của `write.py` (`escape_markdown(shown_name(…))`, cùng `_HIDDEN_IN_NAME`); `through_link` giống từng dòng `_through_link`. Trong cây gộp với `origin/main` `4671104`, bản gốc ở `write.py` không đổi (so từng dòng). Rủi ro sửa một bên mà quên bên kia: chú thích ở `settings.py:439-445` (phiếu cấm sửa `write.py` nên không có chú thích ngược lại); có test giữ cả hai chiều, đọc hàm từ mã nguồn, không nhập trang: Soi Lỗi `test_copied_name_rule_matches_write_page` (so `_HIDDEN_IN_NAME`, so kết quả trên 15 tên kể cả `:red[…]`, `<img …>`, xuống dòng, NUL, nửa cặp surrogate), `test_copied_link_check_is_same_code` (so cây cú pháp), `test_copied_link_check_same_answers` (11 đường dẫn). Ghi nhận 1 |

## Mức SL-T084-1

| Mã | Mức Lá Chắn | Lý do |
|---|---|---|
| SL-T084-1 (`.env` không phải UTF-8, hay không đọc được, làm app sập ngay từ đầu, mọi trang hiện traceback tiếng Anh có đường dẫn tuyệt đối) | **Thấp** (giữ; có từ trước, không do T-084, ngoài phạm vi phiếu) | Đúng như Soi Lỗi tả, tôi đọc lại mã: `load_settings` đọc `.env` bằng `dotenv_values(…, encoding="utf-8")` (`seo_app/config.py:112`) nên ném `UnicodeDecodeError`; `app/main.py:68` chỉ bắt `ConfigError`; Streamlit 1.65 mặc định `client.showErrorDetails = "full"` (`.streamlit/config.toml` không đặt) nên hiện câu lỗi và traceback. Lộ: đường dẫn thư mục cài app, thư viện (có thể có tên tài khoản máy). Không lộ nội dung `.env` hay khóa (traceback chỉ có tên file, số dòng, dòng mã, và câu `UnicodeDecodeError` với byte, vị trí). Chỉ người ở máy thấy: máy chủ chỉ nghe `localhost` (`.streamlit/config.toml:5`). Dễ gặp hơn mức hiếm (Notepad lưu «ANSI» khi `.env` có chữ có dấu, ví dụ tên thư mục ảnh), nhưng hậu quả chính là app không mở (người dùng sẽ báo). Phiếu riêng (Thợ Máy) như Soi Lỗi gợi ý; gỡ 2 `xfail` khi XPASS. Phòng thêm (tùy chọn, đổi cấu hình nên cần chủ dự án duyệt): `client.showErrorDetails = "type"` trong `.streamlit/config.toml`, mọi lỗi lạ chỉ hiện tên loại lỗi và câu chung trên trình duyệt (câu đầy đủ, traceback chỉ ra cửa sổ dòng lệnh) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `PYTHONUTF8=1 uvx detect-secrets scan` 5 file đổi: `{}`; biên bản này: `{}`. `.env` giả trong test của Soi Lỗi viết tách tên và giá trị (commit `58401ff`), không còn báo nhầm |
| S2 | Đạt | Không in khóa, không ghi log mới |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1–W4, A1–A3 | Không áp dụng | Không đổi WordPress, AI |
| U1 | Đạt | Mục trên |
| U2 | Đạt | Mục trên (SL-T084-1 có từ trước, ngoài phạm vi) |
| U3 | Không áp dụng | — |
| F1 | Đạt | Tab chỉ hỏi thư mục gốc qua `ImageLibrary.roots()` và kiểm lối tắt từng tầng; không đọc file ảnh, không quét |
| F2, F3 | Không áp dụng | — |
| D1 | Đạt | Không thư viện mới; `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test dùng thư mục tạm, `.env` tạm, không gọi mạng (bộ chặn mạng của `tests/conftest.py`) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets | `{}` (5 file đổi, biên bản này), `PYTHONUTF8=1` | — |
| bandit | `uvx bandit -r app/views/settings.py`: 0 vấn đề | — |
| pip-audit | Không chạy lại: `uv.lock` không đổi | — |
| ruff | `uv run ruff check .`: All checks passed! | — |
| pytest (nhánh `0b07ff4`) | `tests/test_settings_images.py`, `tests/test_soi_loi_t084.py`, `tests/test_app_pages.py`, `PYTHONUTF8=1`: **59 passed, 2 xfailed, 0 failed** (77,8 s); 2 xfail = SL-T084-1 (`.env` «ANSI», UTF-16) | — |
| Soát R5 | `git diff b60054f..0b07ff4 -- tests/`: chỉ thêm 2 file test mới; không sửa, không `skip`, không xóa test cũ | Đạt (khớp soát R5 của Soi Lỗi) |

## Thử gộp

| Việc | Kết quả |
|---|---|
| `git merge-tree --write-tree` của `team/T-084` với `origin/main` `4671104` | Không xung đột |
| Từ gốc nhánh `b60054f`, `main` có 5 commit, chỉ đổi tài liệu (`TIEN-DO.md`, `docs/team/board.md`, phiếu T-059, T-082, T-083, T-084); `settings.py`, `write.py`, `seo_app/images/folders.py`, `seo_app/text.py`, `tests/conftest.py` không đổi | Mã cây gộp trùng mã nhánh: lượt pytest trên nhánh dùng được cho cây gộp; hàm gốc ở `write.py` trong cây gộp giống từng dòng |

## Báo nhầm đã loại

- Chữ `unsafe_allow_html` trong diff `settings.py`: chỉ là chú thích (`:443`), không có lệnh nào bật HTML.

## Ghi nhận (không phải lỗi)

1. Hai bản hàm chép (`folder_name_md`, `through_link` ở Cài đặt; `name_md`, `_through_link` ở Soạn bài): hiện khớp và có test giữ. Nên làm Đề xuất của Họa Sĩ (đưa ra một module dùng chung, phiếu nhỏ khi được sửa `write.py`) để bỏ hẳn rủi ro lệch.
2. Ghi nhận 2 của Soi Lỗi (chữ Hangul trống U+3164, U+115F, U+1160, U+FFA0; ô chữ nổi trống U+2800 không thành «�» nên tên có thể trông như trống): không lộ gì, cùng luật với trang Soạn bài; thêm khi làm module dùng chung.
3. Khai báo `~` thì tab hiện tên thư mục nhà (thường là tên tài khoản máy): là tên tầng cuối như mọi gốc khác, không phải đường dẫn; chấp nhận.
4. Mỗi lần mở trang Cài đặt, app kiểm từng thư mục gốc và từng tầng cha (lối tắt), như trang Soạn bài; ổ mạng không có thì xong ngay (Soi Lỗi đo dưới 0,1 giây). Không phải vấn đề bảo mật.

## Điều kiện

1. **Gộp `main`:** được ngay, không lỗi nào của phiếu phải sửa trước. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ.
2. **SL-T084-1 (Thấp, có từ trước) → phiếu riêng (Thợ Máy):** `load_settings` bắt `UnicodeDecodeError`, `OSError` khi đọc `.env`, ném `ConfigError` câu tiếng Việt cố định (không đường dẫn); gỡ 2 `xfail` của `tests/test_soi_loi_t084.py` khi XPASS. Tùy chọn (chủ dự án duyệt): `client.showErrorDetails = "type"`.
3. Ghi nhận 1, 2: phiếu nhỏ sau (không bắt buộc).
4. **Lá Chắn:** kiểm lại biên bản này bằng Claude Fable sau 01/11.

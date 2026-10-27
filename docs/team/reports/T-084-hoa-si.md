# Báo cáo T-084 · Trang Cài đặt → Ảnh không in đường dẫn đầy đủ của thư mục ảnh

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-084](../tickets/T-084-cai-dat-anh-khong-in-duong-dan.md) |
| Ngày nộp | 2026-10-27 17:49 |
| Nhánh | `team/T-084` (từ `main` `b60054f`) |
| Kết quả | Hoàn thành: yêu cầu 1–3, có test mới (tên độc hại RLO, ký tự rộng 0, Markdown; gốc không thấy; gốc đi qua lối tắt). Đã mở app thật kiểm tra |

## Tóm tắt (cho chủ dự án)

- Trang **Cài đặt → 🖼️ Ảnh** không còn in đường dẫn đầy đủ của thư mục ảnh (ví dụ `C:\Users\…\Ảnh công trình`). Nay mỗi thư mục chỉ hiện **số thứ tự và tên thư mục cuối**, giống trang Soạn bài: «1. Ảnh công trình — ✅ tìm thấy».
- Thư mục không dùng được thì app nói rõ lý do: chưa thấy trên máy (USB chưa cắm, Google Drive chưa chạy), khai báo thiếu ổ đĩa, hay đó là file chứ không phải thư mục. Số thứ tự giúp bạn biết đó là dòng nào trong `IMAGE_FOLDERS`.
- Thư mục là lối tắt (shortcut kiểu symlink/junction) thì có chữ «↪️ đi qua lối tắt» và một lời nhắc kiểm tra đúng thư mục.
- Tên thư mục lạ (có ký tự ẩn, ký tự đảo chiều chữ, dấu Markdown) hiện nguyên văn, không thành link, ký tự ẩn hiện thành «�». Phần còn lại của tab (phong cách ảnh AI, chất lượng nén WebP) giữ nguyên.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/settings.py` | Tab Ảnh: danh sách thư mục ảnh qua `ImageLibrary.roots()` (`image_folders_list`, `:468`); tên qua `folder_name_md` (`:451`); báo lối tắt qua `through_link` (`:459`); thay khối cũ in `folder` (`:545`) |
| `tests/test_settings_images.py` | Mới: 11 test (tên độc hại, không lộ đường dẫn/.env, gốc không thấy, lỗi hệ điều hành, ổ đĩa, lối tắt, phần còn lại của tab) |

## Cách làm theo yêu cầu

| # | Yêu cầu | Cách làm | Test |
|---|---|---|---|
| 1 | Liệt kê gốc qua `ImageLibrary.roots()` | `ImageLibrary.from_settings(settings).roots()` (`settings.py:476`), không dùng `ImageLibrary._folders`; mỗi gốc một dòng «số. tên — trạng thái» trong một ô Markdown | mọi test dùng `folder_lines`; `test_no_absolute_path_or_env_content_anywhere` kiểm mã nguồn không có `._folders` |
| 1 | Tên ngắn đã escape, cô lập hướng chữ | `folder_name_md` (`:451`): ký tự loại Cc/Cf/Cs/Co/Cn/Zl/Zp (rộng 0, RLO, ngắt dòng…) → «�», bọc U+2068…U+2069, rồi `escape_markdown` (`seo_app/text.py`); chỉ `st.markdown` thường, không `unsafe_allow_html` | `test_folder_names_escaped_isolated_never_html` (thư mục ``[bấm](evil.example) _đậm_ `mã` <U+200B>ẩn <U+202E>gpj.exe אב``: so đúng cả dòng, không link, không U+200B/U+202E ở bất kỳ đâu trên trang, ô Markdown không cho HTML), `test_folder_names_isolated_one_by_one` (mỗi tên một cặp cô lập riêng) |
| 1 | Trạng thái tìm thấy / không thấy | Tìm thấy: «✅ tìm thấy». Không thấy: «⚠️» + `RootInfo.message` (câu cố định của `ImageLibrary`, có số thứ tự, không đường dẫn), đã `escape_markdown` (`:487`) | `test_roots_not_found_explained_without_path` (gốc không có trên máy, gốc ghi đường dẫn tương đối, gốc là file, gốc tìm thấy) |
| 1 | Báo khi gốc đi qua lối tắt | `through_link` (`:459`): tầng nào của đường dẫn khai báo là symlink/junction thì dòng có «↪️ đi qua lối tắt» và tab có một `st.warning` giải thích (câu của trang Soạn bài) | `test_root_through_link_is_reported_without_path` (junction thật trên Windows: gốc là lối tắt, gốc **nằm trong** lối tắt, lối tắt hỏng trỏ tới chỗ đã xóa → «Chưa thấy» + «đi qua lối tắt»), `test_link_warning_only_when_some_root_is_a_link` (không có lối tắt thì không cảnh báo) |
| 2 | Không in đường dẫn tuyệt đối hay nội dung `.env` | Không còn chỗ nào hiện `folder`; `roots()` lỗi hệ điều hành (ví dụ `PermissionError` có đường dẫn trong câu lỗi) thì chỉ hiện câu cố định (`:477`), không để Streamlit in traceback | `test_no_absolute_path_or_env_content_anywhere` (`.env` tạm có `IMAGE_FOLDERS` và khóa giả; quét **mọi chuỗi trong mọi phần tử của cả trang**, mọi tab: không có đường dẫn khai báo, thư mục cha, thư mục nhà, đường dẫn file `.env`, giá trị `IMAGE_FOLDERS`, khóa), `test_os_error_while_reading_roots_shows_fixed_message`, `test_drive_root_shows_number_not_drive_letter` (khai báo thẳng ổ đĩa: hiện «Thư mục ảnh 1», không hiện `C:\`) |
| 3 | Giữ phần còn lại của tab | Giữ tiêu đề «**Thư mục ảnh thật**» (test Soi Lỗi T-019 dựa vào chữ này), câu «Chưa khai báo…», ô phong cách ảnh AI, thanh WebP; chỉ thêm một dòng chú thích nhỏ dưới danh sách | `test_rest_of_the_tab_unchanged`, `test_no_folders_declared`, `tests/test_app_pages.py` |

**Hàm dùng chung:** `escape_markdown` (`seo_app/text.py`) và `ImageLibrary.roots()` dùng lại nguyên. `shown_name`/`name_md` và `_through_link` mà trang Soạn bài dùng nằm trong `app/views/write.py`, là file trang (nhập vào là chạy cả trang Soạn bài) và phiếu cấm sửa, nên không nhập được: tôi chép hai hàm nhỏ này vào `settings.py` (cùng bộ loại ký tự, cùng cách kiểm lối tắt), có chú thích «sửa bên nào thì sửa cả bên kia» (`settings.py:439-445`). Xem mục Đề xuất.

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest tests/test_settings_images.py -q
11 passed in 9.78s

$ PYTHONUTF8=1 uv run pytest tests/test_app_pages.py tests/test_settings_images.py tests/test_app.py \
    tests/test_app_t044_safe_text.py tests/test_settings_blind.py tests/test_settings_keys.py \
    tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t019.py tests/test_soi_loi_t021_t017.py \
    tests/test_soi_loi_t023.py tests/test_soi_loi_t044.py tests/test_soi_loi_t062.py -q
441 passed, 6 skipped in 247.39s (0:04:07)
# Mọi file test mở trang Cài đặt (grep -l 'views/settings.py\|"settings.py"' tests/: 12 file).
# 6 bỏ qua đều có sẵn trong tests/test_soi_loi_t016_t020.py, chỉ chạy trên Mac/Linux
# (`-rs`: 5 «tạo symlink trên Windows cần quyền đặc biệt», 1 «quyền kiểu POSIX»).

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/settings.py tests/test_settings_images.py \
    docs/team/reports/T-084-hoa-si.md
"results": {}
```

Chạy lúc 17:35 → 17:49 (giờ máy, `date`), trên code của commit nộp.

`uv run ruff format --check app/views/settings.py` báo một chỗ có từ trước (bảng `API_KEY_FIELDS`, `main` `b60054f` cũng báo y hệt); phần tôi viết không bị báo. Không sửa chỗ đó (ngoài phạm vi).

**Thử làm hỏng code để xem test có bắt được không** (bản sao worktree, mỗi lần một chỗ hỏng, chạy `tests/test_settings_images.py`):

| Chỗ làm hỏng trong `settings.py` | Kết quả |
|---|---|
| Không cô lập hướng chữ | bắt được |
| Không thay ký tự ẩn bằng «�» | bắt được |
| Không `escape_markdown` | bắt được |
| `through_link` luôn trả «không» | bắt được |
| `through_link` chỉ xét chính thư mục, bỏ các tầng cha | bắt được |
| In lại đường dẫn khai báo như cũ | bắt được |
| Bỏ chặn lỗi hệ điều hành quanh `roots()` | bắt được |
| Gốc không dùng được chỉ ghi «không thấy» chung chung | bắt được |
| Không hiện cảnh báo lối tắt | bắt được |
| Không làm hỏng gì | 11 qua |

Script thử hỏng (`mutate_t084.py`) và script tạo dữ liệu mở app (`setup_app_t084.py`) để ở thư mục ghi chú chung của đội, mục `T-084-hoa-si-scripts` (ngoài repo).

**Mở app thật** (cấu hình tạm `wt-T-084-hoa-si`, cổng 8508, chạy từ worktree với file môi trường tạm ngoài repo; không chạy `seo-app-main`): 4 thư mục khai báo: «Anh cong trinh» (thường), thư mục tên độc hại ở trên, «Anh USB» (không có trên máy), «Anh qua loi tat» (junction). Tab Ảnh hiện:

```
Thư mục ảnh thật
1. Anh cong trinh — ✅ tìm thấy
2. [bấm](evil.example) _đậm_ `mã` �ẩn �gpj.exe אב — ✅ tìm thấy
3. Anh USB — ⚠️ Chưa thấy thư mục ảnh số 3 trên máy này (USB chưa cắm hoặc Google Drive chưa chạy?).
4. Anh qua loi tat — ✅ tìm thấy · ↪️ đi qua lối tắt
[cảnh báo vàng] Thư mục ghi «đi qua lối tắt» là lối tắt (symlink/junction) …
Đọc từ IMAGE_FOLDERS trong file .env, theo thứ tự khai báo. App chỉ hiện tên thư mục cuối, …
Phong cách chung cho ảnh AI … / Chất lượng nén WebP 80
```

Kiểm HTML cả trang bằng JavaScript: không có thư mục tạm, `C:\Users`, tên tài khoản máy, `app.env`, không có link `evil`, không có U+200B, U+202E. Xong đã dừng app, trả `D:\ProMetal-ToolSEO\.claude\launch.json` về đúng bản cũ (SHA-256 `a5607e8c…f169`, `cmp` giống hệt), worktree không có `data/`, cổng 8508 đã đóng.

**Chủ dự án tự kiểm tra:** mở app → Cài đặt → tab 🖼️ Ảnh: thấy số thứ tự và tên thư mục cuối, không thấy đường dẫn đầy đủ. Rút USB (nếu có thư mục ảnh trên USB) rồi tải lại trang: dòng đó báo «Chưa thấy thư mục ảnh số …».

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–3, có test tên thư mục độc hại: RLO, ký tự rộng 0, Markdown (`test_folder_names_escaped_isolated_never_html`, bảng trên)
- [x] Test liên quan qua (`tests/test_app_pages.py`, test mới, mọi test trang Cài đặt có sẵn), `uv run ruff check .` sạch (mục Bằng chứng)
- [x] Báo cáo nộp tại `docs/team/reports/T-084-hoa-si.md`

**Bảo mật:** U1: chỉ `st.markdown`/`st.warning`/`st.caption` thường, không `unsafe_allow_html`; chữ từ máy qua `folder_name_md`, câu của `ImageLibrary` qua `escape_markdown`. U2: không thêm trang (trang Cài đặt vẫn sau màn đăng nhập của `app/main.py`), `.streamlit/config.toml` không đổi (`address = "localhost"`); hết in đường dẫn tuyệt đối (ghi chú U2 Lá Chắn T-048). Không thêm thư viện; không đụng `seo_app/**`, `config/**`, `app/views/write.py`; không sửa test cũ.

## Rủi ro và điểm cần chú ý

- `folder_name_md`/`through_link` là bản chép của hàm trong `write.py`: sửa luật hiện tên ở một trang mà quên trang kia thì hai trang lệch nhau (đã ghi chú ở cả đầu khối code; xem Đề xuất).
- Trên Mac, thư mục Google Drive khai báo qua `~/Google Drive/…` (là symlink tới `~/Library/CloudStorage/…`) sẽ hiện «đi qua lối tắt». Đây là đúng (trang Soạn bài cũng báo vậy), chỉ là nhắc, không chặn.
- Mỗi lần mở trang Cài đặt, app kiểm từng thư mục gốc (như trước, chỉ thêm kiểm lối tắt từng tầng thư mục cha); không quét ảnh bên trong.

## Đề xuất

- **Họa Sĩ (phiếu nhỏ, khi được sửa `write.py`):** đưa `shown_name`/`name_md`, `_through_link` (và `_HIDDEN_IN_NAME`) ra một module dùng chung (ví dụ `app/image_names.py` hoặc `seo_app/ui.py`) để trang Soạn bài và Cài đặt dùng một bản, bỏ bản chép trong `settings.py`.
- Có thể thêm dòng «🤖 mọi ảnh là ảnh AI» cho gốc có tên AI ở tab này như trang Soạn bài (`root_notes`); phiếu không yêu cầu nên chưa làm.

## Câu hỏi cho chủ dự án

Không có.

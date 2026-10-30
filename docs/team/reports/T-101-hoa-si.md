# Báo cáo T-101 · Giao diện Giai đoạn 5: trang Kế hoạch, Cài đặt → Google, trang Bài viết

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-101](../tickets/T-101-giao-dien-ke-hoach-cai-dat-google.md) |
| Ngày nộp | 2026-10-30 17:50 |
| Nhánh | `team/T-101` (từ `main` `fd28bbc`) |
| Kết quả | Hoàn thành: dòng T-101 của thiết kế, mọi LC-T094 của phiếu và phần «Chung», điều kiện mang theo của T-097, T-098, T-100, T-103. «Trạng thái trên website» chỉ đọc (Chỉ Huy đồng ý; ghi Sheet ở T-109). Đổi kỳ vọng 1 ca test cũ, **Chỉ Huy duyệt A 30/10** (R5) |

## Tóm tắt (cho chủ dự án)

- **Trang Kế hoạch chạy thật.** Bạn đưa kế hoạch vào bằng một trong ba cách: tải file (CSV, TSV, TXT, MD; tối đa 1 MB), dán chữ (bảng chép từ Excel/Google Sheets, hoặc ghi chú tự do), hoặc dán link Google Sheets.
  - Bảng có cột «Từ khóa chính»: phần mềm tự so với kế hoạch trên Google Sheets.
  - Ghi chú tự do: phần mềm báo «AI sẽ đọc, có tốn tiền», bạn bấm «Gửi AI đọc» mới gọi AI. Chữ có số điện thoại, email thì phần mềm nhắc trước và có nút «Che rồi gửi».
  - Kết quả là bảng **Đề xuất thay đổi**: Thêm / Cập nhật / Bỏ, mỗi dòng có lý do và cảnh báo. Dòng «Bỏ» và dòng có cảnh báo **không tick sẵn**. Có ô «Xem đủ một đề xuất» để đọc trọn chữ trước khi tick.
  - Bấm **«Áp dụng thay đổi»** mới ghi lên Google Sheet. Dòng vừa bị sửa ở nơi khác (máy kia, hay bạn sửa tay trên Google Sheets) thì **không ghi**, trang hiện bảng «trước / bây giờ / đề xuất» để bạn quyết. Phần mềm không bao giờ xóa dòng.
  - **Danh sách bài** đọc từ Google Sheets (lưu tạm trên máy 5 phút), nút «Tải lại», nút «Trạng thái trên website» (chỉ xem, có nhãn «Lỡ lịch»), và **«Viết bài»** để mở Soạn bài với từ khóa của dòng đó (không gửi gì lên website).
  - Khung **«Thông tin nền cho mọi bài»** hiện hồ sơ doanh nghiệp AI đang dùng (chỉ đọc; sửa file `config/business_profile.md`).
- **Cài đặt → 📗 Google** (tab mới, ở cuối): báo file khóa đã khai báo chưa, **tên** file (không đường dẫn), **email** của tài khoản dịch vụ để bạn chia sẻ Sheet; ô dán link Sheet kế hoạch (lưu vào `.env`); nút «Kiểm tra kết nối» (hiện tên Sheet), «Chuẩn bị trang tính» (tạo trang tính «KeHoach», cột, danh sách chọn), «Thêm cột còn thiếu».
- **Trang Bài viết:** «Tiếp theo trong kế hoạch» lấy 3 bài «Chưa viết» gần nhất từ kế hoạch thật; ô «Từ kế hoạch» của «Viết bài mới» cũng vậy; «Đã gửi WordPress» liệt kê bài phần mềm đã gửi, nút «Hỏi trạng thái trên website» (chỉ xem). Khung «Đang viết» vẫn là bản demo.
- Đã xóa dữ liệu mẫu kế hoạch khỏi `seo_app/demo.py`.

**Chưa làm ở phiếu này** (theo trả lời của Chỉ Huy ngày 30/10):
- Nút «Trạng thái trên website» **chỉ xem** (cột «Trên website», nhãn «Lỡ lịch»), chưa tự đổi cột Trạng thái trên Google Sheet. Phần đó cần hàm lõi mới, đã giao phiếu T-109 (Thợ Máy), sau đó nối vào giao diện.
- Mở Soạn bài từ dòng kế hoạch: phần này chỉ mở Soạn bài với từ khóa của dòng. Gắn dòng kế hoạch vào nháp, điền sẵn các ô khác (ghi chú, tiêu đề, slug, ngày giờ…) là việc của T-102.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/plan.py` | Viết lại thay bản demo: nhận kế hoạch 3 cách, AI đọc chữ tự do (có xác nhận, che thông tin cá nhân), bảng đề xuất + ô tick + xem đủ chữ, «Áp dụng» (ghi Sheet, kết quả, bảng xung đột), danh sách bài, «Tải lại», trạng thái website (chỉ đọc), «Viết bài», việc ghi trạng thái còn nợ («Thử ghi lại»), khung thông tin nền |
| `app/views/settings.py` | Tab «📗 Google» (cuối danh sách tab): `account_card`, `sheet_card`, `check_card`, `prepare_plan_sheet`, `google_tab` (`:523-727`) |
| `app/views/home.py` | «Tiếp theo trong kế hoạch», «Từ kế hoạch» (cache kế hoạch thật), «Bắt đầu» theo dòng kế hoạch, «Đã gửi WordPress» (kho nháp + cột Mã bài WordPress, hỏi website khi bấm) |
| `seo_app/demo.py` | Xóa `SENT_TO_WORDPRESS`, `PLAN_ROWS`, `plan_rows`, `PLAN_PASTE_EXAMPLE`, `PLAN_CHANGES`, `BUSINESS_BRIEF` (G4: nhãn «Sẵn sàng» không còn) |
| `tests/test_t101_plan_page.py` | Mới: 30 ca |
| `tests/test_t101_settings_google.py` | Mới: 14 ca |
| `tests/test_t101_home_page.py` | Mới: 15 ca |
| `tests/test_app_pages.py` | Đổi kỳ vọng 1 ca ghim bản demo (`test_plan_reading_shows_proposed_changes`), **Chỉ Huy duyệt A 30/10** (mục «Đổi test cũ») |

## Cách làm theo thiết kế (dòng T-101 của `T-094-tho-may.md` mục 6)

| Phần thiết kế | Cách làm | Test |
|---|---|---|
| 1.2 Nhận kế hoạch 3 cách | Ba tab giữ như bố cục demo (`st.tabs` có `key="plan_source"` để biết tab đang mở); một nút «🧠 Đọc kế hoạch và đề xuất cập nhật» đọc đúng tab đó (`read_source`, `plan.py:240`). File: `parse.read_file`; chữ dán: `parse.read_paste`; link: `sheet_id_from_link` (không mở link). Link Sheet chính: tải lại. Sheet khác: đọc **một lần** tab «KeHoach» của Sheet đó như file nguồn (`read_sheet_link`, `:286`) | `test_pasted_table_proposals_and_default_ticks`, `test_csv_file_gives_proposals`, `test_main_sheet_link_only_reloads`, `test_other_sheet_is_read_once_as_source`, `test_bad_sheet_link_is_refused_without_request` (3 ca) |
| 1.4 Đề xuất kèm lý do, tick | Bảng đọc (`st.dataframe`: Dòng, Loại, Mã bài, Từ khóa chính, Thay đổi, Lý do, Cảnh báo, Nguồn) và **một ô tick mỗi đề xuất** (nhãn chỉ có số dòng, loại, Mã bài), mặc định `Proposal.preselected`. «Xem đủ một đề xuất» hiện mọi trường «Hiện tại / Đề xuất», chữ dài bằng `st.text` (`proposals_box`, `:448`; `proposal_detail`, `:425`) | `test_pasted_table_proposals_and_default_ticks`, `test_hostile_text_in_proposals_is_plain` |
| 1.4 AI đọc chữ tự do | Chữ không phải bảng → khung «Gửi AI đọc» báo tốn tiền; chỉ gọi `ContentWriter.plan_changes` khi bấm (`ai_box`, `:334`; `run_ai`, `:376`) | `test_free_text_waits_for_click_then_ai_proposes`, `test_ai_error_is_fixed_text` |
| 1.5 «Áp dụng thay đổi» | Chỉ khi bấm; client mới; `sync.apply_proposals(client, plan_base, các dòng đã tick)`. Kết quả: `ApplyResult.message` (có `notes`), bảng xung đột «Trước (lúc duyệt) / Bây giờ trên Sheet / Đề xuất / Vì sao chưa ghi»; xong thì tải lại danh sách (`apply_chosen`, `:502`; `result_box`, `:550`) | `test_apply_writes_only_ticked_and_shows_result`, `test_conflict_shows_before_now_proposed` |
| 1.6 «Viết bài» | Chọn dòng → «✍️ Viết bài» (`write_picker`, `:697`; `start_writing`, `:648`). Đã có nháp của Mã bài này (Sheet đang dùng, `find_plan_draft`): mở nháp đó (`_open_draft`). Chưa có: **đọc lại** đúng dòng (`sync.open_row`), mở Soạn bài với `_start_keyword` = từ khóa, `_start_plan_key` = Mã bài (T-102 dùng để gắn `DraftPlanRef`, điền các ô khác). «Cập nhật bài cũ», dòng «Bỏ»: nút khóa | `test_write_button_opens_compose_without_wordpress`, `test_write_button_reopens_existing_draft`, `test_update_old_kind_cannot_be_written` |
| 1.7 Ghi trạng thái còn nợ | Có việc ghi Sheet còn nợ của Sheet đang dùng: câu báo + «Thử ghi lại» (chỉ khi bấm), `sync.retry_pending`, chỉ ghi Sheet (`pending_box`, `:723`) | `test_pending_status_write_retries_only_sheet` |
| 1.7 «Cập nhật trạng thái từ website» | **Chỉ đọc** (`post_statuses`): cột «Trên website» (Nháp, Đã hẹn giờ, Đã đăng, Chờ duyệt, Riêng tư, Không thấy, **Lỡ lịch** khi hẹn giờ quá 15 phút), không ghi Sheet (`ask_website`, `:627`; `web_label`, `:594`). Phần đổi cột Trạng thái trên Sheet cần hàm lõi (xem «Chưa làm») | `test_website_status_is_read_only` |
| 1.8, 2.6 Danh sách bài | `sync.get_plan` (cache 5 phút, «🔄 Tải lại»); `st.dataframe` các cột thiết kế 2.4 trừ «Cập nhật lúc»; câu báo bản lưu, `MSG_FULL`, cảnh báo đọc Sheet (`plan_list`, `:754`) | `test_list_reads_sheet_and_shows_plain_text`, `test_list_uses_cache_then_reload`, `test_sheet_error_message_is_fixed_text` |
| Thông tin nền cho mọi bài | Hồ sơ doanh nghiệp AI đang dùng (`load_rules().business_profile`, đã bỏ ý «[CẦN XÁC NHẬN]»): danh sách mục + «Xem đủ nội dung» (`st.text`), chỉ đọc (`business_box`, `:798`) | `test_business_profile_is_read_only_plain` |
| 2.1, 2.4 Cài đặt → Google | Tab «📗 Google» **đặt cuối** (test T-023 cũ tìm tab «Kết nối» ở vị trí 3). Tài khoản dịch vụ: đã khai báo, tên file, email để chia sẻ, cảnh báo thư mục đồng bộ hay quyền file. Sheet: đã khai báo, mã chỉ 4 ký tự cuối, ô dán link + «Lưu», «Bỏ Sheet». «Kiểm tra kết nối» (tên Sheet, có tab «KeHoach» chưa), «Chuẩn bị trang tính», «Thêm cột còn thiếu» (`settings.py:510-715`) | `tests/test_t101_settings_google.py` |
| 1.8 Trang Bài viết | «Tiếp theo trong kế hoạch»: 3 bài «Chưa viết» gần nhất từ cache (mở trang không gọi Google), «Bắt đầu» như «Viết bài». Ô «Từ kế hoạch» của «Viết bài mới» cũng từ cache. «Đã gửi WordPress»: mã bài từ kho nháp (trạng thái gửi) và cột Mã bài WordPress, «🌐 Hỏi trạng thái trên website» (chỉ đọc) (`home.py`) | `tests/test_t101_home_page.py` |
| Xóa demo | `SENT_TO_WORDPRESS`, `PLAN_ROWS`, `plan_rows`, `PLAN_PASTE_EXAMPLE`, `PLAN_CHANGES`, `BUSINESS_BRIEF` khỏi `seo_app/demo.py`; G4 (nhãn «Sẵn sàng») không còn | `test_demo_data_is_gone` |

**Vì sao dùng ô tick riêng thay cho bảng tick (`st.data_editor`) của demo:** AppTest không đặt được giá trị `st.data_editor` (Streamlit không cho đặt qua `session_state`), nên không có test chứng minh «Bỏ không tick sẵn», «chỉ ghi dòng đã tick». Ô tick riêng test được. Nhãn ô tick chỉ có chữ cố định (số dòng, loại, Mã bài), không có chữ Sheet hay AI (nhãn widget đọc Markdown). Bảng đọc vẫn hiện đủ cột như demo. Đây là đổi bố cục nhỏ trong khung «Đề xuất thay đổi».

**Ghi xuống đĩa khi chỉ mở trang (tự tìm ra, đã sửa):** lượt test lớn để lại file `data/plan_cache.sqlite` thật trong worktree. Bộ dò (plugin pytest kiểm file sau mỗi test) cho thấy 3 file test mới không ghi. Nguồn là `tests/test_soi_loi_t084.py`: test này khai báo `GOOGLE_SHEET_ID` trong `.env` tạm, mà sau đăng nhập trang mở đầu là trang Bài viết. Trang đọc cache kế hoạch, và mở kho cache là tạo file. Sửa: chưa có file cache thì trang Bài viết, Kế hoạch không mở kho (`home.py` `cached_plan`; `plan.py` `plan_listing` khi không đọc được Google). Test: `test_opening_page_does_not_create_plan_cache` (2 trang); lượt test cuối có bộ dò, không còn file nào trong `data/`.

**Một lỗi lùi tự tìm ra và đã sửa:** sau đăng nhập, trang mở đầu là trang Bài viết. Trang này (và trang Kế hoạch) đọc kho nháp, nên file nháp hỏng bị kho cất sang một bên ngay ở đó; trang Soạn bài không còn báo «file nháp bị hỏng» (`tests/test_app_drafts.py::test_corrupt_drafts_file_is_reported` hỏng). Sửa: hai trang chỉ mở kho khi file có đúng đầu file SQLite, chưa có file thì không tạo (`draft_store`, `plan.py:128`, `home.py:50`); kho vẫn phải cất file thì chính trang đó báo (`note_recovered`). Test: `test_corrupt_drafts_file_is_left_for_compose_page` (2 trang), `test_missing_drafts_file_is_not_created`.

## Hợp đồng `_start_plan_key` (cho T-102; Chỉ Huy chọn A ngày 30/10)

Nút «✍️ Viết bài» (trang Kế hoạch, `plan.py` `start_writing`) và «Bắt đầu» theo dòng kế hoạch (trang Bài viết, `home.py` `start_writing`, cả ô «Từ kế hoạch» của «Viết bài mới») chỉ dùng khóa phiên của `write.py`; **không sửa `write.py`**, không ghi Sheet, không gửi gì lên WordPress.

| Khóa | Kiểu | Lúc đặt | Ai xóa |
|---|---|---|---|
| `_open_draft` (có sẵn, `write.py:235`) | `str`: mã nháp do `DraftStore.find_plan_draft(Mã bài, sheet_hash của Sheet đang dùng)` trả (kho nháp tự kiểm khuôn) | Đã có nháp gắn Mã bài này: đặt ngay trước `st.switch_page("views/write.py")`; cùng lúc **bỏ** `_start_plan_key` còn sót | `write.py` (`init_state` đã `pop`) |
| `_start_keyword` (có sẵn, `write.py:230`) | `str`: Từ khóa chính của dòng, dựng lại qua `PlanRow` (lõi: NFC, bỏ ký tự điều khiển/đảo hướng/vô hình, 2–120 ký tự, «» → ‹›) | Chưa có nháp: sau khi `sync.open_row` **đọc lại** đúng dòng trên Sheet (chỉ `GET`), ngay trước `st.switch_page` | `write.py` (`init_state` đã `pop`) |
| `_start_plan_key` (**mới**) | `str`: Mã bài dạng `B-001` (`[A-Z]{1,3}-[0-9]{3,5}`), đã qua `model.parse_key` (lõi) **hai lần**: mã người dùng chọn, và mã của dòng `open_row` trả (phải trùng nhau, khác thì dừng, báo câu cố định) | Cùng lúc với `_start_keyword`, chỉ khi chưa có nháp của Mã bài này | **T-102** (`write.py`): đọc và `pop` cùng lúc với `_start_keyword` trong `init_state`, rồi tự gọi lại `find_plan_draft` / `open_row` + `sync.plan_ref` để gắn `DraftPlanRef` và điền các ô khác (T-102 không được tin chữ trong phiên, chỉ tin Mã bài). Trước khi T-102 xong: khóa này nằm yên trong phiên, không ai đọc; lần bấm sau ghi đè; mở nháp có sẵn thì bị bỏ |

Test: `test_write_button_opens_compose_without_wordpress`, `test_start_from_plan_row_opens_compose_without_wordpress` (0 request WordPress; Sheet chỉ có lệnh `GET`, không ghi ô, không thêm dòng, không sửa cấu trúc), `test_write_button_reopens_existing_draft` (mở nháp có sẵn, `_start_plan_key` cũ bị bỏ, không đọc lại Sheet).

## Đổi test cũ (R5): Chỉ Huy duyệt A 30/10

`tests/test_app_pages.py::test_plan_reading_shows_proposed_changes` ghim hành vi bản demo. Tôi hỏi Chỉ Huy, đề xuất A (giữ tên ca, đổi kỳ vọng) hay B (xóa). **Chỉ Huy duyệt A 30/10.** Không xóa ca nào, không `skip`, không `xfail`.

| Ca | Cũ | Mới |
|---|---|---|
| `test_plan_reading_shows_proposed_changes` | Bấm «🧠 Đọc kế hoạch và đề xuất cập nhật» thì phiên có `plan_changes` dài bằng `demo.PLAN_CHANGES` (dữ liệu mẫu) | Chưa khai báo Google; mở tab «Dán nội dung», dán chữ, bấm «🧠 Đọc kế hoạch…» thì trang không lỗi, báo «Chưa đọc được kế hoạch hiện tại…», không có đề xuất (`plan_proposals`), không chờ AI (`plan_ai`), không gọi AI (AI giả `fake_ai` không có lần gọi nào) |
| `tests/test_soi_loi_t103.py` (21 ca dùng mẫu kế hoạch của trang demo) | Đọc `demo.plan_rows(TODAY)` và `demo.PLAN_PASTE_EXAMPLE` từ `seo_app/demo.py`: T-101 đã xóa hai tên này nên 21 ca hỏng (`AttributeError`) | Chép đúng 6 dòng mẫu (từ khóa, ý định, ưu tiên, ngày lệch) và đoạn chữ dán mẫu thành hằng `SAMPLE_PLAN`, `SAMPLE_PASTE` ngay trong file test; ý test giữ nguyên (mẫu chỉ đi vào khung dữ liệu); không khôi phục dữ liệu demo. **R5: Chỉ Huy B duyệt 30/10 19:50** (Họa Sĩ sửa khi gộp T-101 vào T-102) |

## Đối chiếu điều kiện Lá Chắn

| Mã | Điều kiện | Đáp ứng ở đâu | Test |
|---|---|---|---|
| LC-T094-1 | Test không gọi Google, WordPress thật | `FakeGoogle` + `FakePlanSheet` (đi qua `SheetsClient` thật), `FakeWordPress`, AI giả; bộ chặn mạng của `conftest.py` vẫn bật; cache kế hoạch, cache bài, kho nháp ở thư mục tạm | Cả 3 file test mới |
| LC-T094-2 | Câu báo lỗi cố định | Chỉ hiện `str(err)` của lớp lỗi app (`SheetsError`, `ServiceAccountError`, `ConfigError`, `SheetPlanError`, `PlanSourceError`, `PlanKeyError`, `PersonalInfoError`, `AIError`, `WordPressError`, `DraftError`); `ValueError` lạ → câu cố định `MSG_ODD_DATA`; không `st.exception`, không giữ đối tượng lỗi | `test_sheet_error_message_is_fixed_text` (mồi trong lời máy chủ), `test_key_file_problem_is_fixed_text` (mồi trong file khóa), `test_check_connection_error_is_fixed_text`, `test_ai_error_is_fixed_text` |
| LC-T094-3 | Chữ ngoài hiện thuần, bỏ ký tự đảo hướng, vô hình | Chữ Sheet, file, AI: `st.dataframe`, `st.text`, hoặc `escape_markdown` (`plain`/`show`, `plan.py:179-188`); `PlanRow` đã qua `clean_text`; tên file khóa qua `folder_name_md`, email và câu cảnh báo qua `visible` (`settings.py:523`); tiêu đề nháp ở trang Bài viết qua `clean_text`. Không `st.table` (đọc Markdown), không thêm `unsafe_allow_html` | `test_list_reads_sheet_and_shows_plain_text`, `test_hostile_text_in_proposals_is_plain`, `test_file_name_with_odd_characters_is_cleaned`, `test_upcoming_text_is_plain`, `test_sent_list_from_drafts_and_plan_then_website_read_only` (U+202E, U+200B, `[x](javascript:…)`, `<b>`) |
| LC-T094-32 | LC-T094-3 cho mọi bảng; trang đích, link Sheet không bấm được | Bảng đề xuất, chi tiết, xung đột, danh sách bài đều `st.dataframe`; trang đích hiện «bài #mã» (không địa chỉ); link Sheet chỉ nằm trong ô nhập | như trên |
| LC-T094-33 | Tải file: kiểm cỡ trước khi đọc, 4 đuôi, không ghi đĩa | `upload.size > MAX_FILE_BYTES` trước `getvalue()` (`plan.py:262`); `parse.read_file` kiểm lại cỡ, đuôi, bảng mã; không ghi file nào | `test_file_too_big_is_refused_before_reading` (2 MB, không đọc byte), `test_wrong_files_are_refused` (`.xlsx`, `.exe` đổi đuôi `.csv`) |
| LC-T094-34 | Cài đặt chỉ hiện đã khai báo, tên file, email, tên Sheet; nút chỉ chạy khi bấm; «Bỏ», dòng có cảnh báo không tick sẵn; qua cổng đăng nhập | Như bảng trên; không thêm trang mới (U2: mọi trang sau `app/main.py`, `server.address` không đổi) | `test_declared_shows_file_name_email_never_path_or_key`, `test_check_connection_shows_sheet_title` (mở trang: 0 request), `test_prepare_sheet_only_on_click_and_add_missing`, `test_pasted_table_proposals_and_default_ticks` |
| LC-T094-35 | «Viết bài» không gửi gì lên WordPress | Chỉ đọc Sheet và mở Soạn bài | `test_write_button_opens_compose_without_wordpress`, `test_start_from_plan_row_opens_compose_without_wordpress` (0 request WordPress) |
| LC-T094-12 | Không in khóa; chỉ tên file, email | `account_card` | `test_declared_shows_file_name_email_never_path_or_key` (không đường dẫn, không mảnh khóa riêng, không mã khóa) |
| LC-T094-15 | Mã Sheet chỉ tách từ link đúng dạng, ghi qua bộ kiểm riêng, không hiện đầy đủ | `_save_sheet` → `sheet_id_from_link` → `env_file.set_google_sheet_id`; hiện `mask_sheet_id` | `test_save_sheet_link_writes_env_and_masks_id`, `test_bad_link_does_not_touch_env` (4 ca: tên máy giả, `@`, xuống dòng chèn biến, dấu nháy) |
| LC-T094-31 | «Chuẩn bị trang tính» chỉ khi bấm | `check_card` | `test_prepare_sheet_only_on_click_and_add_missing`, `test_prepare_creates_tab_when_missing` |
| T-097 đk 3 | Client mới mỗi lần, không cache, không giữ trong phiên; bắt `ConfigError`; không hiện `google_sheet_id` | `sheets_client()` (`plan.py:110`), `google_client()` (`settings.py:563`), `start_writing` (`home.py:96`) tạo mới mỗi lần, không `st.cache_*`; phiên chỉ giữ dữ liệu (đề xuất, `SheetPlan`, chữ báo) | `test_key_file_inside_project_is_refused_without_path`; grep `st.cache` trong 3 trang: 0 |
| T-098 đk 1 | Bắt mọi lỗi của `parse`, `propose`, `plan_changes` (cả `ValueError`) | `read_source`, `read_sheet_link`, `run_ai`, `apply_chosen` | `test_wrong_files_are_refused`, `test_ai_error_is_fixed_text` |
| T-098 đk 3 | «Che» che cả từ khóa kế hoạch, hoặc báo rõ chỗ còn số | «Che rồi gửi» che chữ dán (`mask_personal_info`). Số ở từ khóa kế hoạch: báo rõ Mã bài, nút «Che» khóa, chỉ còn «Vẫn gửi» | `test_phone_in_pasted_text_must_be_masked_or_confirmed`, `test_phone_in_plan_keyword_is_named_and_mask_disabled` |
| T-100 đk 5 | Chữ Sheet, `Conflict.now` thuần; giữ `listing.plan` tới «Áp dụng»; không tự dựng `Proposal` | `S.plan_base` là bản đã xem, chỉ bỏ sau khi áp dụng hay «Hủy»; đề xuất chỉ từ `compare_rows`, `plan_changes` (`from_ai`) | `test_conflict_shows_before_now_proposed`, `test_pasted_table_proposals_and_default_ticks` |
| T-100 lượt 3–4 (a) | Bảng duyệt hiện đủ chữ AI, không cắt | «Xem đủ một đề xuất»: mọi trường, `st.text` cho từ khóa phụ, tiêu đề dự kiến, ghi chú, lý do | `test_hostile_text_in_proposals_is_plain` |
| T-103 | `TokenLimitError` → câu dễ hiểu; G4 | `MSG_AI_TOO_LONG`; xóa dữ liệu demo «Sẵn sàng» | `test_demo_data_is_gone` |

## Bằng chứng

```
# Mọi file test mở trang Kế hoạch, Cài đặt, Bài viết (grep -lE 'views/(home|plan|settings)\.py'),
# thêm test_app_drafts.py (kho nháp), 3 file test mới: 20 file. Kèm plugin dò ghi cache thật
# (in tên test nếu data/plan_cache.sqlite của worktree xuất hiện sau test đó).
$ PYTHONUTF8=1 uv run pytest tests/test_app.py tests/test_app_images.py tests/test_app_pages.py \
    tests/test_app_t044_safe_text.py tests/test_settings_blind.py tests/test_settings_images.py \
    tests/test_settings_keys.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t023.py tests/test_soi_loi_t044.py \
    tests/test_soi_loi_t056.py tests/test_soi_loi_t062.py tests/test_soi_loi_t084.py \
    tests/test_t041_seo_ui.py tests/test_t101_home_page.py tests/test_t101_plan_page.py \
    tests/test_t101_settings_google.py tests/test_app_drafts.py -q -rxXfs -p find_cache_writer
SKIPPED [2] tests\test_soi_loi_t016_t020.py:232: tạo symlink trên Windows cần quyền đặc biệt
SKIPPED [1] tests\test_soi_loi_t016_t020.py:260: tạo symlink trên Windows cần quyền đặc biệt
SKIPPED [2] tests\test_soi_loi_t016_t020.py:273: tạo symlink trên Windows cần quyền đặc biệt
SKIPPED [1] tests\test_soi_loi_t016_t020.py:333: quyền kiểu POSIX
691 passed, 6 skipped in 1244.08s (0:20:44)
# Code của commit nộp, chạy 17:26 → 17:47 (giờ máy, `date`; máy đang chạy cả toàn bộ test của
# Chỉ Huy nên chậm). 6 ca bỏ qua có sẵn, chỉ chạy trên Mac/Linux. Bộ dò: 0 test ghi cache thật,
# không có thư mục data/ sau lượt chạy.
# Trước khi đổi ca R5, cùng bộ file: 1 failed (đúng ca test_plan_reading_shows_proposed_changes).

$ PYTHONUTF8=1 uv run pytest tests/test_t101_plan_page.py   # 30 passed
$ PYTHONUTF8=1 uv run pytest tests/test_t101_settings_google.py   # 14 passed
$ PYTHONUTF8=1 uv run pytest tests/test_t101_home_page.py   # 15 passed
# (nằm trong lượt trên)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/plan.py app/views/home.py app/views/settings.py \
    seo_app/demo.py tests/test_t101_plan_page.py tests/test_t101_settings_google.py \
    tests/test_t101_home_page.py docs/team/reports/T-101-hoa-si.md
"results": {}
# Lần quét đầu bắt 3 mục trong test (chữ đầu khối khóa PEM dùng để so, tên trường private_key của
# file khóa mồi, mã Sheet giả nhiều ký tự ngẫu nhiên): đều là chữ giả, đã đổi cách viết để bản vá
# không có mục «Private Key» (LC-T094-17). tests/test_app_pages.py:13 (mật khẩu thử có từ trước) là
# dòng cũ, không đổi.
```

`uv run ruff format --check` báo hai chỗ có từ trước trong `app/views/settings.py` (bảng `API_KEY_FIELDS`) và `app/views/wordpress.py`; phần tôi viết không bị báo.

**Thử làm hỏng code để xem test mới có bắt được không** (bản sao worktree, mỗi lần một chỗ, chạy file test của trang đó; script `mutate_t101.py`, `mutate_one.py` ở thư mục ghi chú chung, mục `T-101-hoa-si-scripts`):

| Chỗ làm hỏng | Kết quả |
|---|---|
| Kế hoạch: mọi đề xuất tick sẵn (kể cả «Bỏ», dòng có cảnh báo) | bắt được |
| Kế hoạch: bỏ kiểm cỡ file trước khi đọc | bắt được |
| Kế hoạch: «Áp dụng» so với bản đọc lại lúc bấm thay vì bản người dùng đã xem | bắt được |
| Kế hoạch: «Viết bài» không đọc lại Sheet (dùng bản lưu) | bắt được |
| Kế hoạch: chữ tự do gửi AI ngay, không chờ bấm | bắt được |
| Kế hoạch: «Che rồi gửi» không che | bắt được |
| Kế hoạch: bỏ `escape_markdown` trong `plain()` | lần đầu **lọt** (chưa test nào đưa chữ không tin cậy qua `plain()`); thêm `test_business_profile_headings_are_plain` (tên mục hồ sơ doanh nghiệp có link, `**`, `<b>`, U+202E) → bắt được |
| Cài đặt: hiện mã Sheet đầy đủ | bắt được |
| Cài đặt: hiện đường dẫn file khóa | bắt được |
| Bài viết: không làm sạch tiêu đề nháp | bắt được |
| Bài viết: mở kho nháp khi file hỏng | bắt được |
| Không làm hỏng gì | 3 file test mới đều qua |

**Mở app thật** (cấu hình tạm `wt-T-101-hoa-si`, cổng 8509, chạy từ worktree với file môi trường tạm ngoài repo, chưa khai báo Google, WordPress; không chạy `seo-app-main`): trang Bài viết («Tiếp theo trong kế hoạch»: «Chưa có kế hoạch trên máy…», «Đã gửi WordPress»: chưa có bài), trang Kế hoạch (3 tab, nút đọc, khung «Thông tin nền» liệt kê 8 mục hồ sơ, «Danh sách bài» báo chưa kết nối), Cài đặt → 📗 Google (hai thẻ «Chưa khai báo», ô link, nút khóa) hiện đúng bố cục. Thấy và đã sửa 2 lỗi nhỏ: câu báo chưa kết nối hiện nguyên `**` (bỏ định dạng trong câu được escape), nút «Bỏ Sheet» bị cắt chữ (nới cột). Xong đã dừng app, trả `D:\ProMetal-ToolSEO\.claude\launch.json` về đúng bản cũ (SHA-256 `a5607e8c…f169`, `cmp` giống hệt), cổng 8509 đã đóng. Chưa thử với Google, WordPress thật (phiếu cấm; lượt thử thật của Chỉ Huy và chủ dự án theo thiết kế mục 6 «Đi kèm»).

**Chủ dự án tự kiểm tra** (sau khi Thư Ký có README phần Google): mở Cài đặt → 📗 Google, dán link Sheet kế hoạch, «Lưu», «Kiểm tra kết nối», «Chuẩn bị trang tính»; sang trang Kế hoạch, dán vài dòng chép từ Excel (có cột «Từ khóa chính»), bấm «🧠 Đọc kế hoạch…», tick, «Áp dụng», mở Google Sheet xem dòng mới.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: làm đúng dòng T-101 của thiết kế (bảng «Cách làm theo thiết kế»), giữ ranh giới file (không sửa `write.py`, `seo_app/**` trừ `demo.py`, `config/**`)
- [x] Yêu cầu 2: mọi LC-T094 của phiếu và phần «Chung», điều kiện T-097, T-098, T-100, T-103 mang theo (bảng «Đối chiếu điều kiện Lá Chắn»)
- [x] Yêu cầu 3: mọi đề xuất AI phải tick mới ghi; dòng có cảnh báo (giá, số điện thoại, email) không tick sẵn (`Proposal.preselected` của lõi)
- [x] Yêu cầu 4: không in đường dẫn, nội dung file khóa; cảnh báo «thư mục đồng bộ» (SL-T097-4) hiện ở thẻ tài khoản dịch vụ
- [x] Yêu cầu 5: test `AppTest` cho cả 3 trang; `tests/test_app_pages.py` mở được mọi trang; nhãn `st.tabs` cố định
- [x] Test liên quan + `uv run ruff check .` sạch (mục Bằng chứng)
- [x] Báo cáo `docs/team/reports/T-101-hoa-si.md`

## Rủi ro và điểm cần chú ý

- **Giao diện chưa thử với Google Sheets thật.** Mọi đường đi qua `SheetsClient` thật với Google giả (cùng bộ giả T-097, T-100). Lượt thử thật (thiết kế mục 6 «Đi kèm») vẫn cần.
- Đổi bố cục nhỏ ở khung «Đề xuất thay đổi»: bảng đọc + ô tick riêng thay cho bảng tick (lý do ở trên). Nếu chủ dự án muốn tick ngay trong bảng như demo, phải bỏ test tự động cho phần tick.
- Tab «📗 Google» đặt cuối danh sách tab (sau «Kết nối») để không làm hỏng test cũ tìm tab theo vị trí.
- Trang Kế hoạch tạo client Google mới mỗi lần vẽ trang (đọc lại file khóa, chưa gọi mạng); cache kế hoạch cũ hơn 5 phút thì mở trang là đọc lại Sheet (một lệnh), như thiết kế 2.6.
- Thanh tải file của Streamlit vẫn ghi «200MB per file» (giới hạn chung của Streamlit); nhãn ô và code giới hạn 1 MB.
- `write.py:3156` hiện tên file nháp hỏng không qua `escape_markdown` (có từ trước, ngoài phạm vi); trang Kế hoạch, Bài viết thì có escape.

## Đề xuất

- **T-102 (Họa Sĩ):** đọc `_start_plan_key` theo hợp đồng ở trên (pop cùng `_start_keyword`, tự đọc lại dòng, gắn `DraftPlanRef`, điền các ô còn lại).
- **T-109 (Thợ Máy, Chỉ Huy đã lập):** hàm lõi đổi kết quả `post_statuses` thành lệnh ghi ô Trạng thái trên Sheet; sau đó Họa Sĩ nối vào nút «Trạng thái trên website».
- **Thư Ký:** README «Kế hoạch và Google Sheets» (tạo tài khoản dịch vụ, chia sẻ Sheet, Cài đặt → 📗 Google, cách đưa kế hoạch vào, ý nghĩa «Lỡ lịch»).
- **Họa Sĩ (phiếu nhỏ):** khung «Đang viết» của trang Bài viết vẫn là bản demo; có thể thay bằng danh sách nháp thật (`DraftStore.list_drafts`).
- **Soi Lỗi hoặc Thợ Máy (phiếu nhỏ, `tests/conftest.py`):** thêm fixture tự động trỏ `plan_cache.DEFAULT_PLAN_CACHE_FILE` (và `site_index.DEFAULT_SITE_INDEX_FILE`) sang thư mục tạm cho mọi test, như kho nháp và kho thẻ ảnh. Hôm nay mỗi file test tự trỏ; test nào quên thì ghi vào `data/` thật.

## Câu hỏi cho chủ dự án

Không có.

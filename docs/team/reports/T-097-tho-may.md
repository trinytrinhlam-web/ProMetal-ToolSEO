# Báo cáo T-097 · Client Google Sheets và kiểm file khóa tài khoản dịch vụ

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-097](../tickets/T-097-google-sheets-service-account.md) (Giai đoạn 5, đợt 1) |
| Ngày nộp | 2026-10-28 09:05 (giờ máy, +07) |
| Kết quả | Hoàn thành (chờ Soi Lỗi rút gọn, Lá Chắn đầy đủ) |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã có «bộ phận» đọc, ghi Google Sheet kế hoạch bằng **tài khoản dịch vụ** Google. Chưa có nút nào trên giao diện dùng tới (trang Kế hoạch, Cài đặt → Google làm ở T-100, T-101).
- **File khóa Google được kiểm mỗi lần dùng:** phải nằm ngoài thư mục phần mềm và ngoài thư mục ảnh (app từ chối), nếu nằm trong thư mục đồng bộ (Google Drive, OneDrive…) thì app nhắc chuyển ra; file lạ, file bị sửa để gửi chữ ký sang máy chủ khác đều bị từ chối. Nội dung file không bao giờ hiện ra.
- **Ghi Sheet luôn ở dạng chữ thường** (không ai cài được công thức qua app), và app chỉ được làm đúng 5 việc với Sheet: đọc thông tin, đọc kế hoạch, ghi ô, thêm dòng, chuẩn bị trang tính. Không bao giờ xóa tab, dòng hay vùng.
- Mã Google Sheet ghi vào `.env` qua bộ kiểm riêng, chặt hơn khóa AI; app tự lấy mã từ link Sheet bạn dán, không mở link đó.
- Thư viện `google-auth` (đã có sẵn trong máy) được ghi tên vào danh sách thư viện của app theo câu 1A bạn chốt sáng 28/10; không tải thêm gói nào, quét lỗ hổng: sạch.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/google/service_account.py` (mới) | `load_service_account`: kiểm vị trí (đường dẫn thật, thư mục dự án, thư mục ảnh, thư mục đồng bộ), mở một lần đọc từ handle, ≤ 64 KB, kiểm từng trường JSON, `token_uri`, `universe_domain`; tạo `Credentials` chỉ từ dict đã kiểm, một phạm vi Sheets. `ServiceAccount` (email, tên file, cảnh báo; `repr` không có khóa, email, đường dẫn) |
| `seo_app/google/sheets.py` (mới) | `SheetsClient`: 5 lệnh cố định kiểm trước khi gửi (`_check_call`), `RAW`, `:batchUpdate` 4 loại trên đúng tab «KeHoach», lớp chuyển xin mã riêng (`_TokenRequest`), giờ chờ 30 giây, không chuyển hướng, ≤ 2 MB, thử lại 429 theo thiết kế, `SheetsError` câu cố định + `unsure`. `sheet_id_from_link`, `mask_sheet_id`, `column_letter` |
| `seo_app/env_file.py` | `SHEET_ID_PATTERN`, `validate_sheet_id` (bộ kiểm riêng), `set_google_sheet_id`, `clear_google_sheet_id`. Ba khóa AI giữ nguyên, `ALLOWED_KEYS` không đổi |
| `pyproject.toml`, `uv.lock` | Khai báo `google-auth>=2.62.0`; `uv.lock` chỉ thêm 2 dòng khai báo của dự án (70 gói như cũ) |
| `.env.example` | Chú thích hai biến Google: file khóa ngoài thư mục phần mềm, thư mục ảnh, thư mục đồng bộ; tên file Google không bị `.gitignore` chặn; `chmod 600`; biến này chỉ sửa tay; mã Sheet giữ kín, không bật «Bất kỳ ai có đường liên kết». Ví dụ dùng tên bịa |
| `tests/fake_google.py` (mới) | Google giả (máy chủ mã + Sheets), tìm đường theo địa chỉ đầy đủ, trả thân theo luồng; khóa RSA sinh lúc chạy test. Dùng lại được cho T-100 |
| `tests/test_google_service_account.py` (mới) | 56 test (53 chạy trên Windows, 3 bỏ qua: 2 symlink cần Developer Mode, 1 `chmod` chỉ Mac/Linux; ca symlink có bản thay bằng junction chạy được trên Windows) |
| `tests/test_google_sheets.py` (mới) | 194 test: link, `.env`, xin mã, 5 lệnh, lớp kiểm, chuyển hướng, 2 MB, thử lại, bộ chặn mạng |

## Điều đọc được trong mã `google-auth` 2.62.0 (ảnh hưởng thiết kế)

Đọc trong môi trường đã cài (`google/auth/transport/requests.py`, `google/auth/credentials.py`, `google/oauth2/service_account.py`, `google/oauth2/_client.py`); không gọi Google thật.

1. Lớp chuyển mặc định `google.auth.transport.requests.Request` đợi tới **120 giây** (`_DEFAULT_TIMEOUT`) và đi theo chuyển hướng. `Credentials.refresh(request)` gọi đúng một lệnh `POST token_uri` qua đối tượng `request` mình đưa vào (`_client.jwt_grant`, tối đa 3 lần khi máy chủ báo lỗi tạm). Vì vậy app tự viết lớp chuyển `_TokenRequest`: chỉ nhận `POST https://oauth2.googleapis.com/token`, giờ chờ 30 giây (bỏ qua giá trị thư viện đưa), không chuyển hướng, câu trả lời ≤ 64 KB.
2. **Phát hiện mới:** `before_request` (và `AuthorizedSession`, vốn dùng nó) của bản 2.62.0 gọi `_after_refresh` → mở **luồng nền** tra «regional access boundary» tại `https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/<email>/allowedLocations`. Đó là một máy chủ ngoài thiết kế, gửi kèm mã truy cập. App **không** dùng `before_request`, `AuthorizedSession`: chỉ `refresh()` khi mã hết hạn rồi tự gắn header `Bearer`. Test `test_chi_goi_dung_hai_may_chu_google` xác nhận chỉ có `oauth2.googleapis.com` và `sheets.googleapis.com`.
3. Khi phiên `requests` đặt `max_redirects = 0`, câu trả lời 3xx (kể cả với `allow_redirects=False`) làm `requests` ném `TooManyRedirects` sau khi đọc thân câu trả lời đó (không giới hạn cỡ; giống client WordPress hiện có). Không lệnh nào được gửi tới địa chỉ mới; app bắt riêng lỗi này để ra câu «chuyển hướng».

## Đối chiếu điều kiện Lá Chắn T-094

| Mã | Đáp ứng ở đâu | Test |
|---|---|---|
| LC-T094-1 (không gọi Google thật) | `tests/fake_google.py` (máy chủ mã + Sheets giả); bộ chặn mạng `tests/conftest.py` vẫn bật, không sửa | `test_bo_chan_mang_chan_ca_client_sheets_khong_co_site_gia` (client dùng phiên thật → `RealNetworkBlocked`), `test_bo_chan_mang_chan_ca_lop_chuyen_mac_dinh_cua_google_auth` (lớp chuyển 120 giây của thư viện cũng bị chặn) |
| LC-T094-2 (câu báo cố định) | `service_account.py` `_MSG_*` + `raise … from None` ở mọi chỗ bắt lỗi (`_parse_key`, `_read_key_file`, `_credentials`); `sheets.py` `_MSG_*`, `_answer`, `_call`, `_access_token`, `_refresh_message` (chỉ đọc mã OAuth ASCII `invalid_grant`, không chép mô tả) | `test_json_hong_khong_chep_noi_dung`, `test_noi_dung_sai_bi_tu_choi_cau_co_dinh` (18 ca), `test_loi_xin_ma_thanh_cau_co_dinh` (9 ca), `test_ghi_o_loi_co_cau_co_dinh_va_co_unsure` (8 ca): chuỗi mồi trong file khóa và lời máy chủ không có trong câu báo; `__cause__` là `None` |
| LC-T094-3 (chữ hiện trên giao diện) | Thuộc giao diện (T-101). Client đã bỏ ký tự điều khiển, vô hình, đổi hướng chữ ở tên Sheet, tên tab (`_clean_text`); chữ trong ô trả nguyên (nơi dùng qua `PlanRow`, T-100) | `test_ten_sheet_bo_ky_tu_dieu_khien_va_doi_huong` |
| LC-T094-11 (kiểm file khóa mỗi lần dùng) | `load_service_account` (`service_account.py:140`): đường tuyệt đối; `resolve(strict=True)`; so **cả** đường gõ và đường thật với thư mục dự án và từng gốc `IMAGE_FOLDERS` (`_is_within`, so bằng `normcase`, Windows không phân biệt hoa thường; so cả gốc gõ và gốc thật); đoạn `Google Drive`, `My Drive`, `Drive của tôi`, `OneDrive`, `Dropbox`, `iCloud` → Cảnh báo (`_SYNC_MARKERS`); `_read_key_file` (`:210`): `os.open` một lần (`O_NOFOLLOW` trên Mac/Linux), `fstat` trên handle (file thường, ≤ 64 KB), so (thiết bị, số file) của handle với đường đã kiểm (`:229`), đọc từ handle; Mac/Linux `st_mode & 0o077` → Cảnh báo kèm `chmod 600` (`:175`, chỉ tên file). «Mỗi lần dùng»: `SheetsClient.from_settings` gọi lại `load_service_account` mỗi lần; client tạo mới cho mỗi thao tác | `test_file_trong_thu_muc_du_an_bi_tu_choi`, `…dau_cham_cham…`, `test_junction_*` (3 ca, chạy trên Windows), `test_symlink_*` (Mac/Linux), `test_file_trong_thu_muc_anh_bi_tu_choi`, `test_thu_muc_dong_bo_chi_canh_bao` (6 ca), `test_file_qua_64_kb_bi_tu_choi`, `test_thu_muc_khong_phai_file`, `test_file_bi_thay_giua_luc_kiem_va_mo_bi_tu_choi`, `test_noi_dung_sai…` (`type`, `token_uri`, `universe_domain` lạ), `test_from_settings_kiem_lai_file_khoa_moi_lan`, `test_from_settings_tu_choi_file_khoa_trong_thu_muc_anh` |
| LC-T094-12 (không lộ khóa, mã truy cập) | Không `print`, `logging` trong `seo_app/google/`; `ServiceAccount.__repr__` chỉ tên file; `SheetsClient.__repr__` chỉ 4 ký tự cuối mã Sheet; `_Bearer.__repr__` che mã; mã truy cập chỉ trong đối tượng `credentials` (bộ nhớ), không ghi đĩa. Giao diện chỉ cần `account_email`, `ServiceAccount.file_name`, `account_warnings` | `test_repr_khong_co_khoa_email_duong_dan`, `test_repr_khong_lo_ma_truy_cap_ma_sheet_email`, `test_code_khong_dung_tai_khoan_ngam_dinh_hay_uy_quyen` (đọc cây cú pháp: không `print`, `logging`) |
| LC-T094-13 (đường cố định, kiểm trước khi gửi) | `_ROUTES` (`sheets.py:89`) + `_check_call` (`:723`) chạy trong `_send` **trước** cả lệnh xin mã: đúng phương thức, đường khớp toàn chuỗi, mã Sheet đúng của client, tham số **bằng đúng** bộ giá trị cố định, thân JSON đúng khuôn từng lệnh (`_valid_update_body`: `valueInputOption == "RAW"`, vùng `'KeHoach'!<cột><dòng>` dựng từ chỉ số; `_valid_append_body`; `_valid_structure_request`: chỉ `addSheet` «KeHoach» khi lần đọc gần nhất chưa có tab, `updateSheetProperties` chỉ `gridProperties.frozenRowCount`, `repeatCell` chỉ `userEnteredFormat.numberFormat`, `setDataValidation` chỉ `ONE_OF_LIST` chữ không bắt đầu bằng `= + - @`; mọi `sheetId` phải là tab «KeHoach» của `get_info` ngay trước; ≤ 50 yêu cầu). Chỉ `sheets.googleapis.com` (hằng `SPREADSHEETS_URL`) và `oauth2.googleapis.com/token` (`_TokenRequest`). `allow_redirects=False` ở cả hai, `max_redirects = 0` (`:577`). Giờ chờ ≤ 30 giây cả lệnh xin mã (`:352`). Đọc theo luồng (`stream=True`, `_read_limited`), quá 2 MB (lệnh xin mã: 64 KB) thì bỏ, kể cả khi máy chủ không khai `Content-Length`. 429: đọc thử lại 3 lần (1, 2, 4 giây + 0–0,5 giây ngẫu nhiên), ghi ô 1 lần, thêm dòng và `:batchUpdate` 0 lần | `test_lop_kiem_chan_truoc_khi_gui` (18 ca gọi thẳng `_send`, có `USER_ENTERED`, vùng tab khác, `FORMULA`, mã Sheet khác, `..`), `test_yeu_cau_cau_truc_ngoai_danh_sach_khong_gui` (26 ca: `deleteSheet`, `deleteDimension`, `deleteRange`, `updateSpreadsheetProperties`, `duplicateSheet`, `addProtectedRange`, `updateCells`, `repeatCell` ghi công thức, `ONE_OF_RANGE`, `CUSTOM_FORMULA`, `sheetId` khác…), `test_moi_lenh_co_gio_cho_va_khong_theo_chuyen_huong`, `test_chuyen_huong_cua_sheets_khong_di_theo`, `test_loi_xin_ma…[302]`, `test_cau_tra_loi_qua_2_mb_bi_bo` (có và không có `Content-Length`), `test_doc_429_thu_lai_3_lan_roi_bao_loi`, `test_ghi_o_429_thu_lai_dung_1_lan`, `test_them_dong_khong_bao_gio_tu_thu_lai`, `test_sua_cau_truc_khong_tu_thu_lai`, `test_ghi_o_du_lieu_sai_khong_gui` (0 request, kể cả lệnh xin mã) |
| LC-T094-14 (chỉ file khóa đã kiểm) | `_credentials` (`service_account.py:299`): `Credentials.from_service_account_info` với dict **chỉ** gồm `type`, `client_email`, `private_key`, `private_key_id`, `token_uri` (hằng), `universe_domain` (hằng), `scopes=[SHEETS_SCOPE]`. Không `google.auth.default`, `with_subject`, phạm vi Drive | `test_file_khoa_dung_doc_duoc` (đúng 1 phạm vi, `_subject` rỗng, không JWT tự ký), `test_chi_lay_truong_can_thiet_tu_file`, `test_khong_doc_google_application_credentials`, `test_lenh_xin_ma_dung_chuan_va_ky_bang_khoa_trong_file` (kiểm chữ ký JWT bằng khóa công khai, `iss`, `aud`, `scope`, không `sub`), `test_code_khong_dung_tai_khoan_ngam_dinh_hay_uy_quyen` |
| LC-T094-15 (link, mã Sheet, `.env`) | `sheet_id_from_link` (`sheets.py:230`): chỉ `https`, tên máy đúng chữ `docs.google.com`, không `@`, cổng, `\`, ký tự ngoài ASCII, khoảng trắng; đường `/spreadsheets[/u/N]/d/<mã>`; dán thẳng mã đúng dạng cũng được; không mở link. `env_file.validate_sheet_id` (`env_file.py:263`) bộ kiểm riêng `[A-Za-z0-9_-]{25,100}`; `set_google_sheet_id` dùng chung đường ghi nguyên tử, quyền 600, giữ nguyên dòng khác, đọc lại. `GOOGLE_SERVICE_ACCOUNT_FILE` không có hàm ghi (`ALLOWED_KEYS` không đổi). Câu báo không chép mã; `mask_sheet_id` cho chỗ cần nhắc tới mã. **Lệch:** `load_settings` chưa kiểm dạng mã khi đọc, vì `seo_app/config.py` thuộc danh sách file chỉ sửa khi chủ dự án đồng ý (`roster.md`); kiểm ở `SheetsClient.from_settings` (trước mọi lệnh gọi) và ở `SheetsClient.__init__` (mục «Rủi ro» 1) | `test_link_sai_dang_bi_tu_choi` (25 ca: `docs.google.com.evil.example`, `x@docs…`, cổng, `\`, chữ Kirin, `%0a`, `\n`, `=`, `"`…), `test_ma_sheet_sai_khong_ghi_gi` (17 ca, `.env` không đổi một byte), `test_bo_kiem_ma_sheet_chat_hon_khoa_ai`, `test_khong_ghi_duoc_bien_google_bang_ham_khoa_ai`, `test_from_settings_kiem_ma_sheet_truoc_moi_lenh` |
| LC-T094-16 (thư viện) | `pyproject.toml`: `google-auth>=2.62.0` (đúng bản đã khóa, không nới). `git diff uv.lock`: chỉ 2 dòng khai báo của dự án, `Resolved 70 packages` như cũ. `pip-audit` trên `uv export` lúc làm phiếu: sạch (mục «Bằng chứng»). Không thêm `gspread`, `google-api-python-client`, `openpyxl` | Lá Chắn quét lại |
| LC-T094-17 (không khóa thật, không PEM cố định) | Khóa RSA 2048 sinh lúc chạy (`fake_google.new_private_key`, `cryptography` có sẵn); dấu đầu/cuối PEM trong code và test ghép từ hai nửa. `detect-secrets` (`PYTHONUTF8=1`) trên 8 file của phiếu: 0 kết quả (đã thử mồi «Private Key» trên bản sao file tiếng Việt: bắt được) | Mục «Bằng chứng» |

## Bằng chứng

Máy Windows của chủ dự án, worktree `wt-T-097` (nhánh `team/T-097` từ `main` `b513d67`).

```
$ uv run pytest -q -p no:cacheprovider tests/test_google_service_account.py tests/test_google_sheets.py
247 passed, 3 skipped in 43.60s

$ uv run pytest -q -p no:cacheprovider <24 file test liên quan>   # toàn bộ test do Chỉ Huy chạy khi gộp
2277 passed, 13 skipped, 6 xfailed, 1 warning in 589.15s (0:09:49)

$ uv run ruff check .
All checks passed!

$ uv lock
Resolved 70 packages in 2.46s          # git diff uv.lock: +2 dòng (khai báo google-auth của dự án)

$ uv export --frozen --no-hashes --no-emit-project   # 69 gói; google-auth==2.62.0, cryptography==50.0.2
$ uvx pip-audit -r <danh sách> --no-deps --disable-pip      # 08:48 +07
No known vulnerabilities found

$ PYTHONUTF8=1 uvx detect-secrets scan <8 file của phiếu>
(0 kết quả)
```

24 file test liên quan: hai file mới, và mọi file chạm `env_file` (hàm dùng chung vừa sửa; nơi gọi: `app/views/settings.py`), `.env.example`, `pyproject.toml`, cấu hình, trang Cài đặt, bộ chặn mạng: `test_env_file.py`, `test_config.py`, `test_config_tolerance.py`, `test_settings_keys.py`, `test_hash_password_script.py`, `test_safety.py`, `test_soi_loi_t016_t020.py`, `test_soi_loi_t021_t017.py`, `test_soi_loi_t023.py`, `test_soi_loi_t026.py`, `test_soi_loi_t027.py`, `test_soi_loi_t084.py`, `test_phase2_fixes.py`, `test_pillow_version_t058.py`, `test_ai_t026.py`, `test_ai_t028.py`, `test_ai_t034.py`, `test_soi_loi_t028.py`, `test_soi_loi_t034.py`, `test_ai_openai_gemini.py`, `test_ai_openai_gemini_soi_loi.py`, `test_ai_images.py`. 13 bỏ qua, 6 xfail, 1 cảnh báo pydantic có từ trước (không thuộc phiếu), trừ 3 bỏ qua của file mới (mục «Đã thay đổi»).

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: đúng dòng T-097 của thiết kế (mục 2.1, 2.3; tách mã từ link; ghi `GOOGLE_SHEET_ID`; khai báo `google-auth`), chỉ sửa file trong phạm vi phiếu; không đụng `seo_app/wordpress/**`, `app/**`, `config/**`.
- [x] Yêu cầu 2: LC-T094-1, -2, -11 → -17 (bảng trên). LC-T094-3 là việc giao diện (T-101), client làm phần dữ liệu. LC-T094-15: một chỗ lệch (`load_settings`), xin Chỉ Huy quyết (mục «Rủi ro» 1).
- [x] Yêu cầu 3: 250 test mới (247 chạy trên Windows); test cũ liên quan qua hết.
- [x] Test liên quan + `uv run ruff check .` sạch.
- [x] Báo cáo này.

## Rủi ro và điểm cần chú ý

1. **`load_settings` chưa kiểm dạng `GOOGLE_SHEET_ID`** (LC-T094-15 ghi «`load_settings` kiểm lại dạng mã khi đọc»): `seo_app/config.py` nằm trong danh sách file chỉ sửa khi phiếu ghi rõ và chủ dự án đồng ý, phiếu này không ghi. Thay vào đó mã được kiểm ở `SheetsClient.from_settings` và `SheetsClient.__init__`, trước mọi lệnh gọi; mã sai không bao giờ đi vào địa chỉ gọi. Mã sai trong `.env` vẫn nằm trong `Settings.google_sheet_id` (chuỗi), nên giao diện (T-101) không được hiện thẳng giá trị này. Nếu Lá Chắn muốn chốt ở `load_settings`, cần một dòng trong `config.py` (phiếu riêng, chủ dự án duyệt).
2. **Lệnh xin mã có thể đi tối đa 3 lần** (thư viện tự thử lại khi máy chủ mã báo lỗi tạm 5xx), mỗi lần ≤ 30 giây: trường hợp xấu nhất khoảng 90 giây cộng thời gian chờ giữa các lần. Không gửi đi đâu khác ngoài `oauth2.googleapis.com/token`.
3. **Thân câu trả lời 3xx**: `requests` đọc hết thân của câu trả lời chuyển hướng trước khi app kịp kiểm cỡ (giống client WordPress). Chỉ xảy ra với `sheets.googleapis.com`, `oauth2.googleapis.com` qua https; Thấp.
4. **Chưa thử với Google thật**: khuôn câu trả lời (`updatedRange` của lệnh thêm dòng, `totalUpdatedCells`, `replies`) theo tài liệu Google; câu trả lời khác khuôn thì app trả `None` hay báo «không đúng dạng», không đoán. Khóa service account có thể bị chính sách tổ chức chặn tạo (thiết kế 2.1). Kiểm ở lượt thử thật (LC-T094-44).
5. Đường dẫn thật so bằng `normcase`: trên Mac, ổ đĩa mặc định không phân biệt hoa thường nhưng `normcase` của Mac giữ nguyên chữ, nên thư mục ảnh khai báo khác hoa thường với tên thật trên ổ có thể lọt phép so «trong thư mục ảnh» (đường thật vẫn được so). Suy luận, chưa thử trên Mac (chủ dự án chưa có Mac).
6. Tên biến dùng chung: `SHEET_ID_PATTERN` đặt ở `env_file.py` (theo phiếu: «bộ kiểm riêng ở env_file»), `sheets.py` nhập từ đó, để chỉ có một biểu thức mã Sheet.

## Đề xuất

- **T-101 (Họa Sĩ):** tạo `SheetsClient.from_settings()` mới cho **mỗi** lần bấm (không `st.cache_resource`, không giữ trong `st.session_state` qua các lần bấm), để file khóa được kiểm lại mỗi lần (LC-T094-11). Bắt cả `SheetsError` lẫn `ServiceAccountError`, hiện `str(err)` bằng widget chữ thường. Hiện `account_warnings`. Không hiện `Settings.google_sheet_id`; hiện tên Sheet (`get_info().title`) hoặc `mask_sheet_id`.
- **T-100 (Thợ Máy):** khi `SheetsError.unsure` là `True` ở lệnh ghi, đọc lại tab trước khi làm lại; `batch_update` xong phải `get_info` lại; dùng `tests/fake_google.py`.
- **Lá Chắn:** xét cho ghi sổ rủi ro dòng «biến môi trường proxy, chứng chỉ» áp cả `requests` gọi Google (Ghi nhận 1 của T-094); xét điểm «Rủi ro» 1.
- **Thư Ký (README):** nhắc `.env.example` mới đã có chú thích hai biến Google; README hướng dẫn tạo khóa theo LC-T094-43.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-28): sửa 5 lỗi Thấp của Soi Lỗi, Lá Chắn

Chỉ Huy B giao 28/10 18:50, trên `team/T-097` vừa tua tới `main` `24013b3`. Sửa theo cách hai biên bản gợi ý (`T-097-soi-loi.md`, `T-097-la-chan.md` mục «Sửa mẫu»); không đổi thư viện, không thêm phụ thuộc, không gọi Google thật.

### Tóm tắt (cho chủ dự án)

- Google trả lời lạ (lệnh chuyển hướng, mã truy cập hỏng) không còn làm phần mềm đọc quá giới hạn bộ nhớ hay hiện lỗi kỹ thuật: mọi trường hợp ra câu báo tiếng Việt cố định.
- Khi lệnh ghi lên Sheet gặp câu trả lời chuyển hướng, phần mềm coi là «có thể đã ghi» để bước sau đọc lại Sheet trước, không thêm dòng trùng.
- File khóa Google nằm trong thư mục phần mềm hay thư mục ảnh bị từ chối kể cả khi đường dẫn viết theo kiểu đặc biệt của Windows; file trong «Shared drives», «Other computers» của Google Drive cũng có cảnh báo «thư mục đồng bộ».

### Đã thay đổi

| Lỗi | Sửa ở đâu | Cách sửa |
|---|---|---|
| **LC-T097-1** (thân 3xx bị đọc hết) | `seo_app/google/sheets.py`: `_Redirected`, `_refuse_redirect`; `_TokenRequest.__call__` và `SheetsClient._call` thêm `hooks={"response": [_refuse_redirect]}` | Móc `response` của `requests` chạy ngay khi có mã trả lời, **trước** `Session.resolve_redirects` (hàm đọc, giải nén hết thân 3xx cả khi `allow_redirects=False`). Gặp 3xx: `response.close()` (không đọc thân), ném `_Redirected`. `_call` đổi thành `SheetsError` câu «chuyển hướng», `unsure` theo loại lệnh; `_TokenRequest` trả `_TokenResponse(mã, {}, b"")` (google-auth báo lỗi xin mã → câu cố định). Giữ `allow_redirects=False`, `max_redirects = 0`, nhánh `TooManyRedirects` cũ để phòng thêm |
| **SL-T097-1** (`OverflowError`, `RecursionError` lọt) | `SheetsClient._access_token` | Nhánh bắt cuối thêm **đúng** `OverflowError`, `RecursionError` (ra `_MSG_AUTH`). Không bắt `Exception` (theo Lá Chắn: lỗi `RealNetworkBlocked` của bộ chặn mạng trong test phải lọt ra) |
| **SL-T097-2** (3xx không `Location` báo `unsure=False`) | `SheetsClient._call` | Đi chung nhánh `_Redirected` ở trên (móc chặn mọi 3xx, có hay không `Location`) với `unsure=writes`; nhánh kiểm `300 <= status < 400` sau đó (phòng thêm) cũng thêm `unsure=writes` |
| **SL-T097-3** (đường `\\?\…`, `\\?\Volume{…}\…`, `\\?\GLOBALROOT\??\…`, `\\localhost\D$\…` lọt) | `seo_app/google/service_account.py`: `_identity`, `_inside_by_identity`; `_is_within` | So **danh tính thư mục** trước: đi ngược từng thư mục cha của đường gõ và đường thật, so `(st_dev, st_ino)` với thư mục dự án và từng gốc thư mục ảnh (bỏ qua khi `st_ino == 0`, như `seo_app/images/folders.py`); không khớp thì so chuỗi như cũ (ổ không cho số file, thư mục chưa có). Không chỉ bỏ tiền tố `\\?\` (dạng Volume, GLOBALROOT vẫn lọt). Cách này cũng bắt symlink, junction và (suy luận, chưa thử trên Mac) chữ hoa thường trên ổ Mac (Rủi ro 5 lượt 1) |
| **SL-T097-4** (thiếu thư mục Google Drive) | `_SYNC_MARKERS`, `_in_sync_folder`, `ServiceAccount.in_sync_folder` | Thêm `shared drives`, `other computers` và tên tiếng Việt `bộ nhớ dùng chung`, `drive dùng chung`, `máy tính khác` (tên tiếng Việt chưa xác minh trên máy chủ dự án; chỉ là Cảnh báo); so tên thư mục sau NFC (tên dạng tổ hợp NFD cũng nhận, Ghi nhận 8 của Soi Lỗi). **Dấu hiệu cho giao diện:** trường mới `ServiceAccount.in_sync_folder` (bool, mặc định `False`); câu Cảnh báo vẫn trong `warnings`. Hiện cảnh báo: Họa Sĩ, T-101 |
| Test | `tests/test_la_chan_t097.py`, `tests/test_soi_loi_t097.py` | Gỡ **27 dấu `xfail`** (đều `XPASS(strict)` trước khi gỡ: 7 LC-T097-1, 4 SL-T097-3 của Lá Chắn; 6 SL-T097-1, 4 SL-T097-2, 4 SL-T097-3, 2 SL-T097-4 của Soi Lỗi), **chỉ xóa dòng dấu** (gồm dòng định nghĩa biến dấu `_LC1`, `_SL3_MORE`, `_SL1`, `_SL3` và các dòng `@…`); không đổi điều kiện ca nào |
| Test của tôi | `tests/test_google_service_account.py` | Thêm 6 ca: `in_sync_folder` đúng cho «Shared drives», «Other computers», «Bộ nhớ dùng chung», «Máy tính khác», «Drive của tôi» dạng NFD; thư mục thường thì `False`, không cảnh báo; ca cũ «thư mục đồng bộ» kiểm thêm `in_sync_folder is True` |

### Bằng chứng (lượt 2)

Máy Windows của chủ dự án, worktree `wt-T-097` (nhánh `team/T-097` từ `main` `24013b3`), 2026-10-28 19:37 (+07).

```
$ uv run pytest -q tests/test_google_sheets.py tests/test_google_service_account.py tests/test_soi_loi_t097.py tests/test_la_chan_t097.py   # trước khi gỡ dấu
27 failed, 569 passed, 3 skipped        # 27 «failed» đều là XPASS(strict): đúng 27 ca xfail của 5 lỗi, không hỏng nào khác

$ uv run pytest -q -p no:cacheprovider <81 file test liên quan>   # sau khi gỡ dấu; toàn bộ test do Chỉ Huy chạy khi gộp
6952 passed, 65 skipped, 45 xfailed, 1 warning in 2386.93s (0:39:46)

$ uv run pytest -q -p no:cacheprovider tests/test_google_service_account.py   # có 6 ca mới của lượt 2
59 passed, 3 skipped in 13.00s

$ uv run ruff check .
All checks passed!
```

81 file: mọi file test T-097 (`test_google_*.py`, `test_soi_loi_t097.py`, `test_la_chan_t097.py`), và mọi file nhắc tới `seo_app.google`, `fake_google`, `seo_app.config`/`load_settings`, `env_file`, thư mục ảnh (`images.folders`, `ImageLibrary`). 45 `xfail`, 65 bỏ qua, 1 cảnh báo pydantic có từ trước, thuộc phiếu khác (không còn dấu `xfail` nào trong hai file test T-097). Ca chia sẻ quản trị `\\localhost\D$` chạy thật trên máy này (không bỏ qua).

### Còn lại, ngoài phạm vi lượt 2

- Ghi nhận 1 của Lá Chắn (lỗi gốc vẫn ở `__context__`), Ghi nhận 2 (`_check_call` có thể ném `TypeError`, `ValueError` với thân hỏng do code gọi), Ghi nhận 3 của Soi Lỗi (`MAX_UPDATES` và câu báo), Ghi nhận 4, 5, 6 (liên kết cứng; khóa EC; `load_settings`) giữ nguyên như hai biên bản đã xếp «không xếp lỗi» hay chờ `config.py` mở lại.
- Điều kiện 3 của Lá Chắn (T-101: không giữ client, `ServiceAccount`, đối tượng lỗi trong `st.session_state`; hiện chữ thường; dùng `in_sync_folder`/`warnings` cho cảnh báo) chép sang phiếu T-101.

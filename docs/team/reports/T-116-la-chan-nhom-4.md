# Biên bản bảo mật T-116 · nhóm 4: Google Sheets, kế hoạch (kiểm lại bằng Fable)

> Kiểm lại độc lập các biên bản Lá Chắn chạy tạm bằng Opus 5.5 về nhóm này (T-097 ×2, T-098, T-100 ×4, T-101, T-103 phần kế hoạch, T-109 ×2, T-113) và điều kiện thiết kế `T-094-la-chan.md` (phần Sheets/kế hoạch). Quy trình và mức độ lỗi: `docs/team/security.md`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **chạy Fable 5.1** (lời nhắc hệ thống của lượt này báo Fable 5.1; lượt bắt đầu 13:00 ngày 02/11) |
| Phiếu được kiểm | [T-116](../tickets/T-116-la-chan-fable-kiem-lai.md) (phiếu chưa commit; Chỉ Huy giữ) |
| Phạm vi | `main` cục bộ `935d381` (đã gộp vào `team/T-116` ở `d4d19d0`; có T-105, T-113): `seo_app/google/service_account.py`, `seo_app/google/sheets.py`, `seo_app/storage/plan_cache.py`, `seo_app/plan/{model,parse,propose,sync,website}.py`, `app/views/plan.py`, `app/views/home.py`, tab Google của `app/views/settings.py` (`:510-790`), biến `GOOGLE_SERVICE_ACCOUNT_FILE`/`GOOGLE_SHEET_ID` |
| Ngày | 2026-11-02 |
| Máy | Windows 11, Python 3.12.15, uv 0.13.4, thư viện theo `uv.lock` (google-auth, requests bản ghim) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**). Điều kiện chỉ hành chính: lỗi Thấp **cũ** LC-T113-2 còn mở với 9 `xfail(strict=True)` mà chưa có phiếu dọn, và hai điều kiện thiết kế chưa làm (LC-T094-43 README, LC-T094-44 thử thật trên Sheet bản sao) — xem mục Điều kiện |

## Tóm tắt (cho chủ dự án)

Phần Google Sheets và kế hoạch **an toàn** như các biên bản Opus kết luận, và tôi đã tự thử lại từ đầu thay vì chỉ đọc lại biên bản. File khóa tài khoản dịch vụ chỉ được nhận khi nằm ngoài thư mục phần mềm và ngoài thư mục ảnh, đúng định dạng của Google (địa chỉ lấy mã truy cập bắt buộc là của Google), mở một lần và kiểm ngay trên file vừa mở; câu báo không bao giờ chép nội dung hay đường dẫn. Phần mềm chỉ gửi Google Sheets đúng 5 loại lệnh cố định trên đúng Sheet và đúng tab «KeHoach» (tôi thử gửi lệnh xóa, lệnh sang Sheet khác, ghi công thức, ghi tab khác, ghi ngoài 1.000 dòng — đều bị chặn trước khi gửi); chữ ghi lên Sheet luôn là chữ thường (không thành công thức, kể cả khi tải về mở bằng Excel). Trước mỗi lần ghi, phần mềm đọc lại Sheet, tìm đúng **một** dòng theo Mã bài, dòng đã bị sửa ở nơi khác thì không ghi; lệnh ghi lỗi giữa chừng thì không tự ghi lại (thêm dòng còn đọc lại để không thêm trùng). Dữ liệu từ website chỉ dùng để so trạng thái, không ghi chữ của website vào Sheet. File lưu tạm kế hoạch chỉ giữ mã băm của mã Sheet, cấu trúc lạ thì bỏ file.

Không tìm thấy lỗi mới nào. Đối chiếu 13 biên bản/lượt Opus (37 phát hiện Thấp, 0 mức cao hơn; 25 điều kiện thiết kế T-094 trong phạm vi): không phát hiện nào bị xếp **sai**, không phát hiện nào cần **đổi mức**; chỉ còn **một** lỗi Thấp cũ mở (LC-T113-2: file lưu tạm bị sửa tay ghi giờ sát năm 9999 làm trang Kế hoạch lỗi cho tới khi xóa file; cần quyền ghi vào máy) chưa có phiếu dọn — đó là điều kiện chính.

## Lỗi phát hiện (mới)

Không phát hiện lỗi mới. Một ghi nhận thuộc lỗi đã báo ở nhóm 1 (LC-T116-1): `plan_cache.py` cùng khe «liên kết ở tầng thư mục `data/`» và chỉ xét symlink ở tên file (`:238`), không xét hard link như `image_tags._is_link` — đưa vào cùng phiếu dọn LC-T116-1, không lập mã mới.

## Đối chiếu từng phát hiện của biên bản Opus cũ

Nguồn: 13 biên bản/lượt (T-094 thiết kế; T-097 ×2; T-098; T-100 ×3 lượt biên bản; T-101; T-103; T-109 ×2; T-113 ×2), tất cả Opus 5.5 tạm. 37 phát hiện có mức, **toàn bộ Thấp** (8 Lá Chắn tìm, 29 Soi Lỗi tìm được Lá Chắn giữ mức). Kết luận Fable: **giữ** / **đổi mức** / **sai**; trạng thái xác minh trên mã tại `935d381`.

| Biên bản | Mã | Mức Opus | Kết luận Fable | Bằng chứng / ghi chú |
|---|---|---|---|---|
| T-094 | LC-T094-1, -2, -3, -11 → -21, -28 → -35, -42 (điều kiện thiết kế) | điều kiện | giữ (Đạt ở các phiếu code) | Các điều kiện cốt lõi tôi tự kiểm lại ở mục «Đọc mã»: -2 (câu cố định), -3 (chữ thuần), -11 → -15 (file khóa, danh sách lệnh, phạm vi, mã Sheet che), -18 → -21 (`PlanRow`, khung dữ liệu, mã bài thay địa chỉ, lời dặn gọn), -28 → -30 (công thức, cache, ghi có kiểm); probe lệnh/link/file khóa/công thức/cache |
| T-094 | LC-T094-43, -44 | điều kiện | giữ (**chưa làm**) | -43 README mục Google chưa được biên bản nào trong nhóm đối chiếu; -44 thử thật trên Sheet bản sao chưa thực hiện (cần chủ dự án) → điều kiện 2, 3 |
| T-097 l1 | LC-T097-1 | Thấp | giữ (đã đóng l2) | `_refuse_redirect` `sheets.py:291-299` gắn ở lệnh xin mã `:375` và mọi lệnh `:855`: đóng 3xx không đọc thân |
| T-097 l1 | SL-T097-1, -2, -3, -4 | Thấp | giữ (đã đóng l2) | `_access_token` bắt `OverflowError`, `RecursionError` `:798-809`; 3xx không `Location` → `unsure=writes` `:857-862`; `_is_within` so danh tính `(st_dev, st_ino)` `service_account.py:204-266`; `_SYNC_MARKERS` 13 mục kể cả tiếng Việt `:62-76`, cờ `in_sync_folder` |
| T-097 l2 | SL-T097-5 | Thấp | giữ (đã đóng T-100 l1) | `_inside_by_identity` đi ngược theo **đường thật** `:253` (docstring nêu SL-T097-5) |
| T-097 | Ghi nhận 4, 5 (`Settings.__repr__` chưa `repr=False` cho `google_sheet_id`, đường dẫn file khóa; `load_settings` chưa kiểm dạng mã Sheet) | ghi nhận | giữ (**còn mở**, không lập lỗi) | `config.py:69-70` chưa `repr=False`; dạng mã Sheet được kiểm ở `SheetsClient.from_settings` `sheets.py:623` trước mọi lệnh; `repr(Settings)` không được in/log ở đâu (nhóm 3 đã kiểm) → không có đường lộ; dọn khi phiếu nào mở `config.py` |
| T-097 | Ghi nhận 6 (cảnh báo `st_nlink > 1` cho file khóa) | ghi nhận | giữ (không bắt buộc) | — |
| T-098 | SL-T098-12 → -17 | Thấp | giữ (đã đóng Soi Lỗi l3; -17 xác nhận ở T-101) | `model.py:339-340` `MAX_KEY_NUMBER`/`KEYS_EXHAUSTED`; giao diện bắt lớp lỗi riêng; 29 file test qua |
| T-100 l1 | LC-T100-1 | Thấp | giữ (đã đóng l2 + l3–4) | `parse_sheet` đặt `full` `sync.py:256` + `MSG_FULL`; `write_status` `:735-736`, `open_row` `:841-842` chặn khi đầy; `apply_proposals` báo dòng ngoài vùng `:503-505`; `_update` không cấp mã mới khi đầy (SL-T100-11 đóng) |
| T-100 l1 | LC-T100-2, SL-T100-1 → -3, -5 → -10, -12 → -15 (dò giá) | Thấp | giữ (đã đóng l2 + l3–4) | `propose.py:384+` bộ dò giá viết lại (so chữ có dấu, số ≥ 10.000, tuyến tính); `from_ai` gắn `WARN_PRICE` `:356`; không phải bảo mật thuần (lưới mềm, người dùng duyệt) |
| T-100 l1 | LC-T100-3, SL-T100-4 | Thấp | giữ (đã đóng l2 + l3–4) | `_connected_hash` `sync.py:865-875` lấy Sheet lệnh ghi thật sự tới, lệch → `None` → `BLOCKED` `:722-723`; `apply_website_changes` cùng kiểm `website.py:435` |
| T-101 | LC-T101-1 | Thấp | giữ (đã đóng T-102, xác nhận T-113 l1) | `safe_rows` `plan.py:221` cho mọi `st.dataframe` (tải CSV mở Excel không thành công thức) |
| T-103 | LC-T103-1 | Thấp | giữ (đã đóng T-100) | `_has_price` trong `from_ai` `propose.py:356`; 5 ca `xfail` cũ đã gỡ, test `test_la_chan_t103.py` qua |
| T-109 l1 | SL-T109-1, -2, -3 | Thấp | giữ (đã đóng l2) | `_status_of`/`_post_id_of` đọc qua `_reader_text` như bộ đọc bảng `sync.py:882-902`; `_cells_for` đòi đúng dòng bộ đọc nhận `website.py:492-496`; ô lạ → `ODD_CELL`, không đề xuất |
| T-113 l1 | LC-T113-1 | Thấp | giữ (đã đóng l2 `c1852c0`) | `_due_of` xét năm theo giờ UTC trước khi đổi múi giờ (theo biên bản l2); `_moment_text` `sync.py:1072-1075` bắt `OverflowError` cùng kiểu; `test_la_chan_t113.py` 11 qua |
| T-113 l2 | LC-T113-2 | Thấp | giữ (**còn mở**) | `plan_cache._parse_time` `:319-326` chỉ bắt `ValueError` của `fromisoformat`; `astimezone` với mốc sát năm 9999 ném `OverflowError`; `load()` `:104-117` không bắt → trang Kế hoạch lỗi tới khi xóa `data/plan_cache.sqlite` (cần quyền ghi file trên máy, không lộ gì). 9 ca `xfail(strict=True)` `tests/test_la_chan_t113.py` (= 9 xfail trong lượt test của tôi). Cùng kiểu ở `site_index.py:391` (ngoài nhóm, nhóm 2) |
| T-094, T-097 → T-113 | Ghi nhận/quan sát không xếp lỗi (54 dòng) | ghi nhận | giữ | Không có dòng nào thành lỗi khi đọc lại mã; T-101 Quan sát 2 (`showErrorDetails`) trùng điều kiện 3 của nhóm 3 |

**Sai:** không có. **Đổi mức:** không có. **Còn mở sau đối chiếu:** LC-T113-2 (Thấp, chưa có phiếu dọn); điều kiện thiết kế LC-T094-43, -44; ghi nhận T-097 GN4/5 (không lập lỗi).

## Kiểm lại độc lập (lượt Fable): probe trong thư mục tạm, không gọi mạng, không ghi vào repo

| Probe | Nội dung thử | Kết quả |
|---|---|---|
| File khóa (`load_service_account`) | Đường tương đối; file trong thư mục dự án; file trong thư mục ảnh; `token_uri` lạ; JSON trùng khóa; `type` khác; PEM giả | Cả 7 bị từ chối bằng câu cố định; câu báo **không** chứa đường dẫn tạm, nội dung file, `token_uri` lạ, loại file; `repr` không có email |
| Link Sheet (`sheet_id_from_link`) | 3 dạng hợp lệ (link, `/u/1/d/`, mã trần) và 7 giả dạng (`http`, `docs.google.com@evil`, `docs.google.com.evil`, tên máy khác, `\`, chữ có dấu, `javascript:`) | 3 nhận đúng mã, 7 từ chối |
| Danh sách lệnh (`SheetsClient._check_call`) | GET Sheet khác; DELETE; `values:clear`; ghi `USER_ENTERED`; ghi tab khác; ô dòng 2000; `deleteSheet` (trước và sau `get_info`); `repeatCell` ghi công thức; đối chứng: ghi `RAW` ô hợp lệ chứa `=HYPERLINK(1)` | 9/9 bị chặn trước khi gửi (`_MSG_BLOCKED`/`_MSG_NO_INFO`); đối chứng được nhận (chữ bắt đầu `=` vẫn là chữ nhờ `RAW`) |
| Trung hòa công thức (`sync.to_cell`/`safe_text`) | Chữ bắt đầu `=`, `+`, `-`, `@`, TAB, CR | Cả 6 được chèn dấu cách đầu |
| Cache kế hoạch (`PlanCacheStore`) | File có trigger lạ (kết nối tạo trigger đã đóng); file bị chương trình khác giữ mở + trigger lạ | Trigger lạ → không dùng cache, bỏ file (`reset_count = 1`), file tạo lại không còn trigger; bị giữ mở → `load` trả `None`, không nổ, không dùng cache (thất bại an toàn). *Lần chạy đầu tôi để kết nối tạo trigger còn mở nên app không xóa được file — lỗi probe, đã ghi để người sau không lặp lại* |
| Bộ đọc chữ dán (`parse.read_paste`) | 4 dòng 19.600–19.900 ký tự dựng để biểu thức tách bảng Markdown `_MD_SEPARATOR` (có lượng từ lồng) thất bại muộn | ≤ 0,01 s mỗi dòng: không ReDoS trong giới hạn 20.000 ký tự |

Test chọn lọc hiện có (29 file: `test_google_*`, `test_plan_*`, `test_la_chan_t097/t100/t101/t103/t113`, `test_soi_loi_t097/t098/t100/t101/t103/t109/t113`, `test_t100_*`, `test_t101_*`, `test_t102_formula_cells`, `test_t103_plan_prompt`, `test_t109_website_status`, `test_t113_website_status`): kết quả ở bảng công cụ.

## Đọc mã: các điểm then chốt đã xác nhận (bằng chứng `file:dòng` tại `935d381`)

- **File khóa (S1, S2, F1, F3; LC-T094-11/-12/-14):** `service_account.py:161-196` đường dẫn tuyệt đối, `resolve(strict=True)`, từ chối trong dự án/thư mục ảnh bằng cả đường gõ lẫn đường thật (`_is_within` `:204-226`, so danh tính `(st_dev, st_ino)` `:239-266`); mở **một lần** `O_NOFOLLOW`, `fstat` file thường ≤ 64 KB, so danh tính sau khi mở `:283-319`; JSON không trùng khóa `:322-337`, `type` `:338`, email đúng mẫu `:53`, `:341`, PEM `:365-369`, `token_uri` phải đúng của Google `:346`, `universe_domain` `:348`; chỉ truyền dict tối thiểu và đúng một phạm vi Sheets `:372-386`; không `google.auth.default()`; `repr` không email/đường dẫn `:145-147`; mọi câu báo cố định `:78-125`.
- **Client Sheets (W4, A2, S2; LC-T094-2/-13/-15):** 5 lệnh cố định `sheets.py:91-111`, kiểm **trước khi gửi** `_check_call` `:755-786` (đúng mã Sheet, đúng tham số, đúng khuôn thân); ghi chỉ `RAW` `:85`, `:417-440`; vùng ô dựng từ hằng tab + chỉ số cột `:113`, `:715`; `:batchUpdate` chỉ `addSheet`/`updateSheetProperties`/`repeatCell`/`setDataValidation` trên đúng `sheetId` vừa `get_info` `:480-565` (không giá trị ô, không công thức, không xóa); thêm dòng **không bao giờ** thử lại `:107`, `:722-737`; lệnh xin mã qua `_TokenRequest` `:346-391` (chỉ `POST TOKEN_URI`, 30 s, không chuyển hướng, ≤ 64 KB); mọi lệnh `allow_redirects=False` + móc `_refuse_redirect` `:291-299` (đóng 3xx không đọc thân); trả lời ≤ 2 MB `:302-314`; timeout ≤ 30 s `:602`; `_NoAuth` chặn `.netrc` `:260-264`; `_Bearer.__repr__` che `:271-272`; mã Sheet chỉ 4 ký tự cuối `:222-224`; lỗi theo mã HTTP, câu cố định, `unsure` cho lệnh ghi `:892-909`, `:857-890`; `from_settings` kiểm lại file khóa mỗi lần `:608-628`.
- **Cache kế hoạch (F1, F3; LC-T094-29, LC-T113-2):** `plan_cache.py` chỉ băm mã Sheet `:80-82`; `_guard` `:348-361` (`trusted_schema = OFF`, giới hạn độ dài, 50 triệu bước); kiểm `sqlite_master` trong giao dịch `:207-232`, `:378-386`; `_is_healthy` + `quick_check` `:389-406`; kiểm từng ô, mã băm toàn bộ, dòng sai → bỏ cả cache `:165-205`; symlink ở tên file → xóa chính liên kết `:238-240`.
- **Ghi Sheet có kiểm (W2-tương-đương cho Sheet; LC-T094-28/-30, LC-T100-1/-3):** `sync.apply_proposals` `:428-508` đọc lại trước khi ghi `:443`, dòng khác bản đã xem → `Conflict`, ghi theo lô, lỗi `unsure` thì **không** ghi lại, thêm dòng lỗi `unsure` → `_key_present` đọc lại Mã bài `:493-501`, dòng > 1.000 → báo `:503-505`; `write_status` `:699-769` so mã băm Sheet `:722` (`_connected_hash` `:865-875`), đúng một dòng `:734-741`, trạng thái không lùi `:750-751`, Mã bài WordPress phải quen `:747-753`, ≤ 4 ô; `open_row` `:829-850` đọc lại, đúng một dòng và đúng dòng bộ đọc nhận; `parse_sheet` `:245-301` Mã bài trùng → bỏ dòng và cảnh báo, Sheet đầy `full`; `prepare_sheet` `:933-974` chỉ ghi tiêu đề vào **cuối** dòng 1, không ghi đè; `safe_text` `:1033-1041`, `to_cell` `:1044-1060` chèn dấu cách trước `= + - @ TAB CR` (LC-T094-28) — lớp hai ngoài `RAW`.
- **Trạng thái từ website (T-109, T-113):** `website.apply_website_changes` `:418-476` chỉ nhận thay đổi của chính lần kiểm, so mã băm Sheet `:435`, lần kiểm ≤ 5 phút `:440-442`, đọc lại, `_cells_for` `:479-530` kiểm dòng (đúng một dòng, đúng dòng bộ đọc, chưa bị sửa) và **chỉ ghi** trạng thái/giờ do app dựng (`to_cell("status", …)`, `_moment_text`) — không chữ nào của website vào ô; `_moment_text` `sync.py:1067-1076` bắt `OverflowError` (LC-T113-1 cùng kiểu).
- **Dữ liệu chưa tin cậy (A1, A2, U1; LC-T094-18/-19/-20):** `PlanRow` `model.py:427-529` `extra="forbid"`, `frozen`, mọi ô qua `_clean_limited`/`clean_text` `:159-180` (bỏ Cc/Cf/Cs/Co/Cn, NFC), nhãn khớp danh sách cố định, `target_id` là **mã bài** (không địa chỉ), từ khóa «» → ‹›; `from_ai` `propose.py:320-363` bỏ mục có HTML (kiểm sau làm sạch **và** NFKC `:369-373`), cảnh báo SĐT/email `:376-381`, giá `:384+` (LC-T103-1 đóng); bộ đọc file kiểm cỡ **trước** khi giải mã `parse.py:143-160`, chữ dán ≤ 20.000 `:171-176`, `csv.Error` bắt `:201-206`, `:257-260`; lời dặn kế hoạch trong khung `_block` và `web_search` luôn tắt (nhóm 3 đã kiểm, `ai.toml:80-88`).
- **Giao diện (U1, U2):** `plan.py:8-12` (docstring) không `unsafe_allow_html` (grep: 0 chỗ), chữ hiện qua `st.dataframe(safe_rows(…))` `:221`, `:464`, `:489`, `:587`, `:760`, `:839`, `:980` hay `escape_markdown` `:196`; tải file kiểm cỡ `:291`; đọc lại Sheet chỉ khi cache quá 5 phút hay bấm «Tải lại» (`sync.get_plan` `:321-360`), không có vòng chạy nền; `home.py` tiêu đề/lỗi qua `escape_markdown` `:114`, `:132`, `:184`, `:190`, hỏi website chỉ khi bấm và chỉ đọc `:178-192`; tab Google `settings.py:563-571` chỉ bắt lớp lỗi câu cố định (`SheetsError`, `ServiceAccountError`, `ConfigError`, `SheetPlanError`), file khóa chỉ **tên** (`folder_name_md`), email dịch vụ (cần để chia sẻ Sheet, LC-T094-12/-31), mã Sheet 4 ký tự cuối.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Soát lịch sử git: 0 khóa riêng/`client_email` thật, chưa từng commit file khóa/`.sqlite`; detect-secrets 0 |
| S2 | Đạt | Xem «File khóa», «Client Sheets», «Giao diện»; probe câu báo không chép đường dẫn/nội dung |
| S3 | Đạt | `GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_SHEET_ID` có trong `.env.example` kèm chú thích; không biến mới |
| W1–W3 | Không áp dụng | Nhóm 2 (WordPress); lớp «không xóa/ghi đè» cho Sheet xem mục ghi Sheet có kiểm |
| W4 | Đạt | Chỉ `https://sheets.googleapis.com` và `https://oauth2.googleapis.com/token`; timeout ≤ 30 s; không theo chuyển hướng; SSL mặc định (`grep verify=`: 0); proxy/chứng chỉ của máy theo sổ rủi ro 28/10 |
| A1 | Đạt | Chữ kế hoạch/Sheet/chữ dán vào lời dặn qua `_block`, `_keyword`; T-103 đã kiểm, test `test_t103_plan_prompt` qua |
| A2 | Đạt | Việc `plan` không công cụ; kết quả AI qua `from_ai` (HTML, nhãn, ngày, Mã bài kiểm), người dùng tick duyệt; cảnh báo SĐT/email/giá |
| A3 | Đạt | Lời dặn kế hoạch chỉ Mã bài, từ khóa, ngày, trạng thái, ưu tiên (LC-T094-21); ghi chú thợ không gửi AI; không bí mật |
| U1 | Đạt | `st.dataframe`/`escape_markdown`/`st.text`; không `unsafe_allow_html` trong `plan.py`, `home.py`, tab Google |
| U2 | Đạt | Đăng nhập chặn mọi trang (`main.py`); câu báo cố định không đường dẫn; file khóa chỉ tên |
| U3 | Không áp dụng | Nhóm 3 |
| F1 | Đạt (ghi nhận LC-T116-1) | File khóa: từ chối trong dự án/thư mục ảnh, mở `O_NOFOLLOW` một lần; cache: symlink ở tên file bị xóa; **khe tầng `data/`** như nhóm 1 |
| F2 | Không áp dụng | Nhóm 1 |
| F3 | Đạt | `json.loads` có `object_pairs_hook` chặn trùng khóa; `utf-8-sig`; SQLite tham số `?`, `trusted_schema = OFF`; không `eval`/`pickle`; file tải lên kiểm byte trước khi giải mã |
| D1 | Đạt | `uv.lock` không đổi khi gộp `935d381` (bảng công cụ); pip-audit sáng 02/11 69 gói sạch |
| D2 | Đạt | `.gitignore`: `*service-account*.json`, `data/`, `*.sqlite`, `.env*` |
| D3 | Đạt | Test dùng `fake_google.py`, `fake_plan_sheet.py`; bộ chặn mạng; probe không gọi mạng |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| `uv --version` | 0.13.4 | ✔ |
| pip-audit | `git diff 731a46e 935d381 -- uv.lock pyproject.toml` rỗng → dùng lại lần chạy sáng 02/11 (nhóm 1, cùng lock): 69 gói ghim, **No known vulnerabilities found** (`uv export` → `uvx pip-audit -r … --no-deps --disable-pip`) | ✔ |
| bandit 1.9.4 (`PYTHONUTF8=1`; `seo_app/google`, `seo_app/plan`, `plan_cache.py`, `plan.py`, `home.py`; 5.965 dòng) | 3 Low, đều báo nhầm: B105 `service_account.py:45` (`TOKEN_URI` là địa chỉ), B105 `:110` (một câu báo có chữ «token_uri»), B311 `sheets.py:830` (`random.uniform` chỉ làm độ trễ ngẫu nhiên khi thử lại 429, không phải mật mã) | ✔ |
| detect-secrets 1.5.0 (`PYTHONUTF8=1`; phạm vi + `settings.py` + `tests/fake_google.py`, `fake_plan_sheet.py`) | `"results": {}` (0 mục) | ✔ |
| Soát lịch sử git (`git log -p --all`, mẫu `BEGIN PRIVATE KEY`, `private_key_id`, `client_email` thật) | Chỉ fixture giả trong test (`"ab" * 20`, mồi) và dòng mã; `git log --diff-filter=A`: chưa từng thêm `*service*account*.json`, `*.sqlite`, `.env` | ✔ |
| pytest chọn lọc (29 file) | **2205 passed, 3 skipped, 9 xfailed, 0 failed** (10′23″; máy đang chạy toàn bộ test trên `main` song song; 3 bỏ qua là ca Mac/Linux, 9 xfail là lỗi treo đã biết có dấu `strict`) | ✔ |
| ruff (`seo_app/google`, `seo_app/plan`, `plan_cache.py`, `plan.py`, `home.py`) | All checks passed | ✔ |

## Báo nhầm đã loại

- bandit B105 ×2 (`service_account.py:45`, `:110`): hằng địa chỉ và câu báo, không phải mật khẩu; B311 `sheets.py:830`: độ trễ thử lại, không dùng cho mật mã.
- Probe cache lần đầu: «không bỏ được file» do chính probe giữ kết nối SQLite mở (Windows khóa file); chạy lại với kết nối đã đóng thì app bỏ file đúng. Khi file bị chương trình khác giữ thật, app vẫn không dùng cache (thất bại an toàn).

## Ghi nhận (không lập lỗi mới)

1. `plan_cache.py` thuộc cùng khe LC-T116-1 (liên kết ở tầng `data/`) và chỉ xét symlink ở tên file, không xét hard link như `image_tags._is_link` → gom vào phiếu dọn LC-T116-1 (cả ba module: `PreviewCache`, `ImageTagStore`, `PlanCacheStore`). Cache chỉ chứa dữ liệu kế hoạch (không bí mật, không mã Sheet gốc).
2. `sheets._is_read_value` `:912-917` không chặn độ dài chuỗi ô Google trả (chỉ giới hạn bởi 2 MB cả trả lời); `PlanRow`/`_clean_limited` cắt theo từng trường trước khi dùng, giao diện hiện qua `st.dataframe` — không có đường khai thác.
3. Email tài khoản dịch vụ hiện ở tab Google (`st.code`) và tên file khóa trong cảnh báo `chmod` — có chủ đích (LC-T094-12/-31), cần để chủ dự án chia sẻ Sheet.
4. `requests.Session()` của client Sheets tôn trọng biến proxy/chứng chỉ của máy (`trust_env`) — đúng dòng sổ rủi ro 28/10; `.netrc` không bị đọc nhờ `_NoAuth`/`_Bearer`.

## Chưa làm được trong lượt này

- Không gọi Google thật (đúng dặn dò): lớp mạng kiểm bằng `fake_google.py`/`fake_plan_sheet.py` có sẵn và đọc mã; không thử lại ổ Google Drive thật cho `_SYNC_MARKERS`.
- Không chạy Mac/Linux (quyền `0o077` của file khóa, `O_NOFOLLOW`).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN — hành chính, không có lỗi mới)

1. **LC-T113-2 (Thấp, cũ):** Chỉ Huy lập phiếu dọn nhỏ (Thợ Máy) trước khi đóng Giai đoạn 5, như biên bản T-113 lượt 2 đề nghị: `plan_cache._parse_time` và `site_index._parse_time` xét năm theo giờ UTC trước khi đổi múi giờ, ngoài khoảng/tràn → `_Corrupt` (bỏ cache); rà kho nháp cùng kiểu; gỡ 9 `xfail` khi XPASS. **Nên gộp cùng phiếu dọn LC-T116-1** (cả ba module `data/`: `PreviewCache`, `ImageTagStore`, `PlanCacheStore` — kiểm liên kết tầng thư mục và hard link) thành một phiếu «dọn kho dữ liệu phụ».
2. **LC-T094-44 / T-097 điều kiện 5:** thử thật một lượt trên Sheet **bản sao** (không phải Sheet kế hoạch thật) với tài khoản dịch vụ thật trước khi dùng Giai đoạn 5 — chủ dự án cùng Chỉ Huy; Lá Chắn không chạy Google thật.
3. **LC-T094-43:** Thư Ký đối chiếu README mục Google (file khóa để ngoài dự án/thư mục ảnh, chia sẻ Sheet cho email dịch vụ với quyền Người chỉnh sửa, không bật «bất kỳ ai có link») với mã hiện tại.
4. Không điều kiện mới nào từ lượt Fable này.

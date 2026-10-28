# Báo cáo T-097 · Client Google Sheets và kiểm file khóa tài khoản dịch vụ · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-097](../tickets/T-097-google-sheets-service-account.md) (Giai đoạn 5, đợt 1) |
| Nhánh | `team/T-097` (gốc `main` `b513d67`, kiểm trên đầu nhánh `c260116`) |
| Ngày nộp | 2026-10-28 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn đầy đủ được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **4 Thấp** (SL-T097-1 → -4). **Không lỗi nào bắt buộc sửa trước Lá Chắn**; nên sửa SL-T097-1, -2 (mỗi lỗi một dòng) trước khi T-100 dùng client |

## Tóm tắt (cho chủ dự án)

- Phần đọc, ghi Google Sheet (chưa có nút nào trên giao diện dùng tới) làm đúng những điều quan trọng nhất: chỉ gọi đúng 2 máy chủ của Google và đúng 5 việc đã định; **ghi lên Sheet luôn là chữ thường** (tôi cho ghi chữ kiểu công thức `=IMPORTXML(…)`: lên Sheet vẫn là chữ, không thành công thức); 40 kiểu lệnh lạ (xóa tab, thay chữ hàng loạt, ghi công thức qua đường khác…) đều bị chặn **trước khi gửi**; mã Sheet độc (có xuống dòng, dấu `=`, `${…}`, chữ Kirin giống chữ Latinh…) không ghi được vào `.env`, file `.env` giữ nguyên từng byte.
- **File khóa Google:** tôi thử khoảng 30 kiểu file hỏng hay độc (JSON sai, thiếu trường, sai loại, quá lớn, khóa không phải RSA, địa chỉ lấy mã giả…): app đều từ chối bằng câu cố định, **không bao giờ chép nội dung file hay đường dẫn** ra câu báo. File nằm trong thư mục phần mềm hay thư mục ảnh (kể cả qua junction, viết hoa thường khác, thêm dấu chấm cuối tên) bị từ chối.
- **Thư viện `google-auth`:** chỉ thêm đúng 2 dòng khai báo, không tải gói nào mới; quét lỗ hổng 69 gói lúc 13:18 hôm nay: sạch.
- **4 lỗi nhỏ (Thấp), không cần sửa trước khi Lá Chắn kiểm:**
  1. Máy chủ cấp mã của Google trả lời lạ (thời hạn mã lớn vô lý, dữ liệu lồng quá sâu) thì app ném lỗi kỹ thuật thay vì câu tiếng Việt cố định. Chỉ xảy ra khi chính máy chủ Google trả lời sai; không lộ gì.
  2. Khi ghi lên Sheet mà Google trả lời kiểu «chuyển hướng» thiếu địa chỉ, app báo như thể **chắc chắn chưa ghi**; phần đồng bộ làm sau (T-100) có thể thêm dòng lần nữa thành dòng trùng. Rất hiếm.
  3. Gõ đường dẫn file khóa theo kiểu đặc biệt của Windows (`\\?\…` hay `\\localhost\D$\…`) thì file nằm trong thư mục phần mềm hay thư mục ảnh vẫn được nhận. Không ai gõ vậy vô tình; nên chặn cho chắc.
  4. File khóa nằm trong «Shared drives» hay «Other computers» của Google Drive (cùng ổ với «My Drive») **không** có lời nhắc «đang ở thư mục đồng bộ». Trên máy Windows này, thư mục «Other computers» có sẵn trong ổ Google Drive.
- **Việc của bạn:** không có. Lời khuyên giữ nguyên: để file khóa trong một thư mục riêng trên ổ C (không để ở Desktop hay Documents nếu bạn bật Google Drive sao lưu các thư mục đó).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t097.py` | Mới: 330 ca (314 qua, 16 `xfail(strict=True)`: SL-T097-1 6 ca, -2 4 ca, -3 4 ca chỉ chạy trên Windows, -4 2 ca). Google giả viết riêng (`_Google`, thân trả lời là `urllib3.HTTPResponse` thật, đọc theo luồng như khi chạy thật), không dùng `tests/fake_google.py`; khóa RSA sinh lúc chạy; file khóa, thư mục dự án, thư mục ảnh, `.env` đều trong thư mục tạm |
| `docs/team/reports/T-097-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác. Không gọi Google thật (bộ chặn mạng của `tests/conftest.py` bật suốt; script dò ngoài pytest tự chặn socket ở dòng đầu).

## Lỗi tìm ra

### SL-T097-1 · Thấp · Lệnh xin mã trả lời lạ làm lỗi lọt khỏi `SheetsClient`

- **Chỗ:** `seo_app/google/sheets.py:756-771` (`_access_token`) chỉ bắt `RefreshError`, `TransportError`, `GoogleAuthError`, `ValueError`, `TypeError`, `KeyError`. Mã `google-auth` 2.62.0 đã cài (`google/oauth2/_client.py`): `_parse_expiry` làm `_helpers.utcnow() + datetime.timedelta(seconds=expires_in)` nên ném **`OverflowError`** khi `expires_in` là vô cực (`1e400`), `1e20`, hay từ khoảng 2,5·10¹¹ giây (dạng số lẫn dạng chữ số); `_token_endpoint_request_no_throw` chỉ bắt `ValueError` quanh `json.loads` nên thân lồng sâu (60 KB, dưới giới hạn 64 KB của `_TokenRequest`) ném **`RecursionError`**, ở cả mã 200 lẫn 400.
- **Hậu quả:** `get_info()` (và mọi lệnh) ném `OverflowError: date value out of range` / `RecursionError: maximum recursion depth exceeded while decoding a JSON array…` thay vì `SheetsError` câu cố định (LC-T094-2). Giao diện T-101 theo đề xuất của Thợ Máy chỉ bắt `SheetsError`, `ServiceAccountError` nên sẽ hiện lỗi kỹ thuật. Không lộ khóa hay mã (thông điệp lỗi không có dữ liệu). Chỉ máy chủ `oauth2.googleapis.com` (https) trả lời được như vậy.
- **Đối chứng đã đúng** (14 ca qua): `expires_in` NaN hay lồng, thân không phải UTF-8, JSON là mảng hay chữ, mã rỗng, mã có xuống dòng, mã là số, thiếu `access_token`, `invalid_grant` có mồi (ra câu «Google từ chối khóa…»), lỗi khác có mồi, 302 có `Location` (không đi theo), thân quá 64 KB, đứt giữa thân. 503 liên tục: thư viện tự thử 3 lần, chỉ tới máy chủ mã, rồi câu cố định.
- **Test:** `test_sl_t097_1_lenh_xin_ma_tra_loi_la_thanh_cau_co_dinh` (6 xfail).
- **Gợi ý:** thêm `OverflowError`, `RecursionError` vào nhánh bắt cuối của `_access_token` (ra `_MSG_AUTH`), hoặc bắt `Exception` như `_credentials` của `service_account.py` đang làm.

### SL-T097-2 · Thấp · Lệnh ghi gặp mã 3xx không có `Location` báo `unsure=False`

- **Chỗ:** `seo_app/google/sheets.py:831-832`: `if 300 <= status < 400: raise SheetsError(_MSG_REDIRECT…, status_code=status)` không có `unsure=writes`. Nhánh `TooManyRedirects` (`:814-820`) thì có, nhưng `requests` chỉ ném `TooManyRedirects` khi câu trả lời có `Location` (`Session.resolve_redirects` → `get_redirect_target`).
- **Hậu quả:** cùng một tình huống (máy chủ trả 3xx cho lệnh ghi) mà `unsure` khác nhau tùy có header `Location`. Docstring `SheetsError` và đề xuất cho T-100: `unsure` là `True` thì đọc lại trước khi làm lại; `False` nghĩa là chắc chưa ghi, nên T-100 có thể làm lại **lệnh thêm dòng** → dòng trùng (thiết kế 2.3: «lặp lại là thêm trùng»). Chỉ khi Google trả 3xx không `Location` cho lệnh POST: rất hiếm.
- **Đối chứng đã đúng:** 3xx có `Location` ở cả 5 lệnh: không đi theo, không gọi địa chỉ mới, `unsure` đúng theo loại lệnh (5 ca); lệnh đọc gặp 3xx không `Location`: `unsure=False` (2 ca).
- **Test:** `test_sl_t097_2_ghi_gap_3xx_khong_location_van_la_khong_chac` (4 xfail: ghi ô 302, thêm dòng 302 và 307, sửa cấu trúc 302).
- **Gợi ý:** thêm `unsure=writes` ở `:832`.

### SL-T097-3 · Thấp (Windows) · Đường dẫn dạng thiết bị hay UNC về chính máy lọt phép so vị trí file khóa

- **Chỗ:** `seo_app/google/service_account.py:163-168`, `_is_within` (`:192-202`), `_norm` (`:187-189`): so **chuỗi** sau `normcase(normpath(abspath(…)))`. `ntpath.realpath` của Python 3.12 **giữ** tiền tố `\\?\` khi đường gõ có tiền tố đó; đường UNC `\\localhost\D$\…` là chuỗi khác `D:\…` dù cùng một file.
- **Thử** (máy Windows của chủ dự án, thư mục tạm, script `probe_paths.py`): `\\?\<đường đầy đủ>` của file trong thư mục dự án → **nhận**; của file trong thư mục ảnh → nhận; khai thư mục ảnh bằng `\\?\…` → file trong đó nhận; `\\localhost\D$\…` và `\\127.0.0.1\D$\…` vào thư mục dự án → nhận (máy này mở được chia sẻ quản trị). **Đối chứng đã bắt:** `\\.\…`, dấu chấm hay dấu cách cuối tên, `::$DATA`, hoa thường, dấu `/`, `..`, junction.
- **Hậu quả:** LC-T094-11 («so **đường dẫn thật**») chưa trọn. Phải cố ý gõ dạng đặc biệt mới gặp; nội dung file vẫn được kiểm, câu báo vẫn cố định.
- **Test:** 4 xfail `test_sl_t097_3_…`, chỉ chạy trên Windows; ca `\\localhost` tự bỏ qua nếu máy không mở được chia sẻ quản trị.
- **Gợi ý:** so theo **danh tính file** thay cho chuỗi: đi ngược từng thư mục cha của `real`, so `(st_dev, st_ino)` với thư mục dự án và từng thư mục ảnh (`os.path.samefile`); cách này cũng bịt Rủi ro 5 của Thợ Máy (Mac không phân biệt hoa thường, NFC/NFD). Tối thiểu: bỏ tiền tố `\\?\`, `\\?\UNC\` trước khi so, từ chối UNC trỏ về chính máy (`localhost`, `127.0.0.1`, tên máy).

### SL-T097-4 · Thấp · Cảnh báo «thư mục đồng bộ» thiếu «Shared drives», «Other computers» của Google Drive

- **Chỗ:** `seo_app/google/service_account.py:59-68` (`_SYNC_MARKERS`).
- Google Drive for Desktop trên Windows gắn ổ ảo (G:, H:…) với các thư mục gốc `My Drive`, `Shared drives`, `Other computers`; danh sách chỉ có `My Drive` (và «Drive của tôi»). Trên máy này, ổ Google Drive có sẵn `Other computers` (chỉ xem tên thư mục gốc, không đọc hay ghi gì trong Drive). File khóa đặt ở `G:\Shared drives\…` (người khác trong nhóm thấy) hay `G:\Other computers\…` không có Cảnh báo.
- **Test:** 2 xfail `test_sl_t097_4_…`; đối chứng 8 dạng đã có Cảnh báo (`My Drive`, `Google Drive`, «Drive của tôi», `GoogleDrive-…` của Mac, `OneDrive - Công ty`, `Dropbox (Personal)`, `iCloudDrive`, `com~apple~CloudDocs`).
- **Gợi ý:** thêm `shared drives`, `other computers` cùng tên tiếng Việt tương ứng (chưa xác minh trên máy chủ dự án: «Bộ nhớ dùng chung», «Máy tính khác»); hoặc trên Windows coi cả ổ là Google Drive khi gốc ổ có `My Drive`/«Drive của tôi»/`Other computers`. Ngoài tầm phát hiện theo đường dẫn: thư mục trên máy được Google Drive **sao lưu** (Desktop, Documents…), nên README dặn thêm.

## Kiểm theo việc được giao

| Việc | Kết quả | Test |
|---|---|---|
| File khóa hỏng, độc: JSON sai (hỏng có mồi, rỗng, trùng khóa `private_key`, lồng sâu, số 5000 chữ số, UTF-16), thiếu khóa, sai loại (`authorized_user`, `external_account`, `type` là mảng, cả file là mảng), trường sai (email lạ, viết hoa, thiếu; PEM rác có mồi; khóa 9000 ký tự; `private_key_id` lạ; `token_uri` lạ, thêm `/`, viết hoa, thiếu; `universe_domain` lạ) | **Đạt**: câu cố định, không mồi, không đường dẫn, không tên file, `__cause__` là `None`; ngữ cảnh lỗi gốc bị ẩn (`from None`) | `test_file_khoa_noi_dung_la_cau_co_dinh` (9), `test_file_khoa_truong_sai_cau_co_dinh` (13) |
| Khóa không phải RSA (EC P-256, Ed25519) có dấu PEM đúng | Nạp được (chưa ký), gọi thì câu cố định «Không lấy được mã truy cập…», không request nào | `test_khoa_khong_phai_rsa_khong_lam_lot_loi` (2) |
| Quá lớn | Đúng 65 536 byte: nhận; 65 537: từ chối | `test_file_khoa_dung_64_kb_nhan_64_kb_cong_1_tu_choi` |
| BOM, đường dẫn rỗng, tương đối, `C:khoa.json`, `~`, có NUL | BOM nhận; còn lại câu cố định | `test_file_khoa_utf16_va_bom`, `test_duong_dan_file_khoa_la_cau_co_dinh` (6) |
| Symlink | Máy này **không tạo được** symlink (WinError 1314; Thợ Máy cũng bỏ qua 2 ca này trên Windows). Thay bằng junction (bắt) và liên kết cứng (nhận: Ghi nhận 4) | `probe_paths.py`; test junction của Thợ Máy |
| Trong thư mục ảnh / Drive | Thư mục ảnh: từ chối (cả dạng hoa thường, `..`, junction); dạng `\\?\` lọt: **SL-T097-3**. Drive: 8 dạng có Cảnh báo; thiếu 2: **SL-T097-4** | `test_cac_dang_duong_dan_khac_van_bi_bat` (2: dự án, thư mục ảnh), `test_thu_muc_dong_bo_co_canh_bao` (8) |
| Quyền lỏng | Chỉ Mac/Linux, không thử được trên Windows; đọc code: `st_mode & 0o077` lấy từ `fstat` của chính handle, câu chỉ có tên file | Test `chmod` của Thợ Máy (bỏ qua trên Windows) |
| `GOOGLE_SHEET_ID` độc khi ghi `.env`: xuống dòng kèm `WORDPRESS_URL=…`, `\r`, `=`, `${WORDPRESS_APP_PASSWORD}`, `$…`, `"` `'` `#` `\` `` ` ``, dấu cách, NUL, U+2028, U+0085, chữ toàn khổ, chữ Kirin, 24 và 101 ký tự, cả link, `None` | **Đạt**: `EnvFileError`, `.env` (có BOM, xuống dòng CRLF) giữ nguyên **từng byte**, câu báo không chép mã | `test_ma_sheet_doc_khong_ghi_gi_vao_env` (20) |
| `.env` lạ khi ghi mã đúng: chưa có dòng, `export`, hai dòng, giá trị nháy nhiều dòng chứa `WORDPRESS_URL=…evil`, `${WORDPRESS_URL}`, không xuống dòng cuối | **Đạt**: chỉ dòng của biến đổi, `load_settings` đọc lại đúng mã và đúng `WORDPRESS_URL`. Dòng thiếu nháy đóng: từ chối, không ghi | `test_ghi_ma_dung_vao_env_la_chi_doi_dong_cua_no` (6) |
| Link Sheet đủ dạng | 15 dạng đúng (`/edit#gid`, `?usp=sharing`, `/u/0/`, `/htmlview`, `?gid=…#gid=…`, `?usp=drive_link`, tham số dài, `%40`, `HTTPS` hoa, xuống dòng, dán thẳng mã…): đúng mã. 19 dạng độc (tên máy giả, `@`, cổng, `\`, `http`, `https:/`, dấu chấm cuối tên máy, `javascript:`, link «xuất bản» `/d/e/2PACX…`, chèn `\n`, `%0a`, Kirin, U+200B, tab, 24/101 ký tự, `None`, bytes): từ chối, câu không chép mã | `test_link_sheet_dung_dang_lay_dung_ma` (15), `test_link_sheet_doc_bi_tu_choi_cau_khong_chep_ma` (19) |
| Mã Sheet sai sửa tay trong `.env` | `from_settings` chặn trước khi đọc file khóa và trước mọi lệnh; câu không chép mã | `test_sheets_client_tu_choi_ma_sheet_doc_trong_env` |
| Câu trả lời Sheets lạ: lồng sâu 2 MB (mảng, object), số 5000 chữ số, thân rỗng, không phải JSON có mồi, JSON là mảng, mã 201, 204, 500 có mồi, 503, 400/401/403/404 có mồi, 3 MB không khai cỡ, khai `Content-Length` 3 MB, hết giờ đọc, hết giờ nối, mất kết nối, lỗi SSL, đứt giữa thân, hết giờ giữa thân | **Đạt** cho cả 5 lệnh (110 ca): `SheetsError` câu cố định, không mồi, `unsure` đúng (lệnh ghi: `True` trừ mã 4xx; lệnh đọc: luôn `False`), mỗi lệnh gọi đúng 1 lần | `test_cau_tra_loi_sheets_la_thanh_cau_co_dinh` (110) |
| JSON đúng cú pháp nhưng sai khuôn (tab: `properties` là mảng, `sheets` là dict, `sheetId` chữ/bool/âm, tên tab là mảng, hai tab «KeHoach», 201 tab; ô: `values` dict, dòng là chữ, ô là object, 27 cột, 1 002 dòng, số 2⁶⁰, `null`, `COLUMNS`; `replies` sai) | **Đạt**: «không đúng dạng», `unsure` đúng | `test_json_dung_cu_phap_nhung_sai_khuon_bi_tu_choi` (20), `test_o_doc_ve_la_vo_cuc_bi_tu_choi` |
| 429 | **Đạt**: đọc gọi 4 lần, chờ 1/2/4 giây cộng ≤ 0,5; ghi ô 2 lần; thêm dòng, sửa cấu trúc 1 lần; 429 rồi 200: đọc, ghi ô thành công, thêm dòng và sửa cấu trúc không thử lại | `test_429_thu_lai_dung_so_lan_va_gio_cho` (5), `test_429_roi_thanh_cong` (5) |
| Chuyển hướng | Không đi theo ở cả Sheets lẫn lệnh xin mã; lệnh ghi thiếu `Location`: **SL-T097-2** | Mục SL-T097-1, -2 |
| Hết giờ, đứt mạng | **Đạt** (bảng trên). Ghi chú: Google giả kiểu `io.RawIOBase` không có `.stream` cho kết quả sai «lọt `ProtocolError`»; đã kiểm lại bằng `urllib3.HTTPResponse` thật (như `requests` dùng): không lọt. Test dùng bản thật | `probe_body_break.py` |
| Ghi luôn `RAW`, đường cố định, «không chặn oan» | **Đạt**: luồng hợp lệ trọn vẹn (chuẩn bị trang tính 2 bước: tạo tab rồi cố định dòng, định dạng ngày `dd/mm/yyyy`, danh sách chọn tiếng Việt; ghi 200 ô chữ dạng công thức `=`, `+`, `-`, `@`; thêm dòng 26 cột; đọc lại) đi qua hết; mọi lệnh thuộc 6 địa chỉ cố định, `allow_redirects=False`, `stream=True`, giờ chờ ≤ 30 giây, luôn gắn auth riêng (không lấy `.netrc`), không đâu có `USER_ENTERED`, mã truy cập chỉ gửi tới Sheets, lệnh xin mã không có header `Authorization`, xin mã 1 lần cho cả client. 40 lệnh lạ gọi thẳng `_send` (ghi ô `USER_ENTERED`/`raw`/qua tham số, vùng 2 ô, tab khác, dòng 1 002, cột AA, ô là object hay có NUL, `PUT`; thêm dòng `USER_ENTERED`/`OVERWRITE`/2 dòng; đọc `FORMULA`; `fields=*`, `includeGridData`; mã Sheet khác, `?alt=media`, `..`; `developerMetadata:search`, `values:batchClear`; `findReplace`, `appendCells` công thức, `pasteData` HTML, `sortRange`, `autoFill`, `cutPaste`, `repeatCell` ghi giá trị hay `fields=*`, danh sách chọn có công thức hay ở tab khác, `sheetId` là bool, đổi tên tab, thêm khóa ngoài `requests`): chặn, **0 request**, kể cả lệnh xin mã | `test_luong_hop_le_day_du_khong_chan_oan_va_chi_ghi_raw`, `test_lenh_ngoai_danh_sach_khong_gui_gi` (40) |
| Không lộ khóa, mã trong câu báo và log | **Đạt**: bật log DEBUG cho mọi logger, chạy lệnh đúng và lệnh lỗi (403, hết giờ, 500, `invalid_grant` có mồi): không bản ghi log, câu báo, `repr` nào có mã Sheet, mã truy cập, email dịch vụ, mồi, dòng khóa PEM hay đường dẫn file khóa | `test_khong_lo_khoa_ma_email_trong_log_va_cau_bao` |
| Cấm `google.auth.default()` | **Đạt**: đọc cây cú pháp 2 module (không `*.auth.default`, `with_subject`, `AuthorizedSession`, `before_request`, `compute_engine`, `apply`, lớp chuyển `requests` của thư viện, không đọc `GOOGLE_APPLICATION_CREDENTIALS`). Đặt `GOOGLE_APPLICATION_CREDENTIALS` trỏ một file khóa khác: JWT gửi đi vẫn `iss` là email của file đã kiểm, chữ ký kiểm được bằng khóa công khai của file đó, `aud` đúng máy chủ mã, `scope` đúng một phạm vi Sheets, không `sub` | `test_code_google_khong_dung_tai_khoan_ngam_dinh_hay_lop_chuyen_cua_thu_vien`, `test_khong_dung_google_application_credentials_ma_dung_file_da_kiem` |
| Bộ chặn mạng của test chặn được `google-auth` | **Đạt**: lớp chuyển `requests` (120 giây) và `urllib3` của thư viện bị chặn; `AuthorizedSession` (app không dùng) bị chặn cả lệnh chính lẫn **luồng nền** tra «regional access boundary» tới `iamcredentials.googleapis.com` (xác nhận phát hiện 2 của Thợ Máy: luồng nền có thật; bộ chặn bắt được ở bước tra tên) | `test_bo_chan_mang_chan_…` (3) |
| `uv.lock` chỉ thêm `google-auth`, khóa phiên bản | **Đạt**: `git diff b513d67..c260116 -- uv.lock` +2 dòng (khai báo của dự án); 70 gói trước và sau; `google-auth` 2.62.0 (phụ thuộc `cryptography`, `pyasn1-modules`); `uv lock --locked --offline`: khớp. `pyproject.toml`: `google-auth>=2.62.0` (cận dưới đúng bản khóa) | Lệnh tay |
| `pip-audit` | **Sạch**: `uv export --frozen --no-hashes --no-emit-project` (69 gói, có `google-auth==2.62.0`, `cryptography==50.0.2`, `urllib3==2.8.0`, `requests==2.34.2`), `uvx pip-audit -r … --no-deps --disable-pip` lúc 13:18 +07: «No known vulnerabilities found» | Lệnh tay |
| Quét bí mật file test mới | `PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t097.py`: 0 (đã đổi một chuỗi giả bị nhận nhầm «Base64 High Entropy») | Lệnh tay |

## Soát R5

Nhánh **không sửa test cũ nào**: `git diff --name-status b513d67..c260116 -- tests/` chỉ có 3 file mới (`A`): `tests/fake_google.py`, `tests/test_google_service_account.py`, `tests/test_google_sheets.py`. Không có gì để soát.

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, chép thêm file test của tôi; không đụng worktree), gỡ từng chốt chặn rồi chạy 3 file: `tests/test_soi_loi_t097.py` (của tôi), `tests/test_google_sheets.py`, `tests/test_google_service_account.py` (Thợ Máy). Bản không gỡ: 560 qua, 3 bỏ qua, 16 xfail. Script `mutate097.py` (thư mục ghi chú chung).

| Đột biến | Số test hỏng: Soi Lỗi / Thợ Máy |
|---|---|
| M1 ghi ô nhận mọi `valueInputOption` | 2 / 1 |
| M2 thêm dòng `USER_ENTERED` (cả danh sách đường lẫn lệnh) | 2 / 2 |
| M3 lệnh Sheets theo chuyển hướng (bỏ `max_redirects = 0`, `allow_redirects=True`) | 6 / 2 |
| M4 lớp chuyển xin mã nhận mọi địa chỉ | 0 / 1 (không quan sát được qua `google-auth` vì `token_uri` đã cố định; test Thợ Máy gọi thẳng lớp chuyển) |
| M5 bỏ giới hạn 2 MB | 4 / 2 |
| M6 thêm dòng tự thử lại 1 lần | 2 / 1 |
| M7 không kiểm tham số | 8 / 5 |
| M8 `:batchUpdate` nhận mọi loại yêu cầu | 12 / 26 |
| M9 không kiểm `token_uri` | 4 / 6 |
| M10 bỏ chặn thư mục dự án | 1 / 5 |
| M11 bỏ chặn thư mục ảnh | 1 / 4 (lượt đầu Soi Lỗi 0: đã thêm ca thư mục ảnh vào test đối chứng, chạy lại bắt được) |
| M12 chỉ so đường gõ, bỏ so đường thật | 2 / 2 |
| M13 bỏ Cảnh báo thư mục đồng bộ | 8 / 6 |
| M14 mã Sheet dùng bộ kiểm của khóa AI | 3 / 4 |
| M15 link Sheet không kiểm tên máy | 4 / 4 |
| M16 câu trả lời Sheets không bắt `RecursionError` | 10 / 1 |
| M17 hết giờ ở lệnh ghi không `unsure` | 6 / 2 |
| M18 dùng `token_uri` lấy từ file | 4 / 6 |
| M19 không kiểm dạng mã truy cập | 2 / 1 |
| M20 `repr` lộ mã Sheet | 1 / 1 |
| M21 câu báo 4xx chép lời máy chủ | 26 / 4 |
| M22 câu báo JSON hỏng chép nội dung file | 5 / 1 |
| M23 giờ chờ 120 giây | 1 / 2 |
| M24 lệnh đọc gặp 429 không thử lại | 4 / 2 |

**24/24 đột biến bị bắt**; 23/24 bị test của tôi bắt (trừ M4, test Thợ Máy bắt).

## Ghi nhận (không xếp lỗi)

1. **`load_settings` chưa kiểm `GOOGLE_SHEET_ID`** (Rủi ro 1 của Thợ Máy, lệch LC-T094-15 đã khai): xác nhận `from_settings` chặn trước khi đọc file khóa và trước mọi lệnh (5 mã sai sửa tay); `Settings.google_sheet_id` vẫn là chuỗi thô, T-101 không được hiện. Lá Chắn quyết.
2. **Thế biến của `.env`:** `load_settings` đọc `.env` có thế biến (python-dotenv mặc định). Nếu chủ dự án tự gõ `GOOGLE_SHEET_ID=${ANTHROPIC_API_KEY}`, khóa AI dạng `sk-ant-…` lại **đúng dạng** mã Sheet (`[A-Za-z0-9_-]{25,100}`) nên sẽ nằm trong địa chỉ gọi Google. App không bao giờ ghi `$` vào `.env` (bộ kiểm riêng chặn), chỉ xảy ra khi sửa tay. Có thể khép khi làm điều «`load_settings` kiểm lại dạng mã» (đọc biến này không thế biến).
3. **`MAX_UPDATES = 200`** (không có trong thiết kế): 201 ô thì câu báo «ô phải là chữ ≤ 2000 ký tự, số hoặc đúng/sai», sai nghĩa. T-100 phải chia lệnh (mất tính trọn gói) hay có câu báo riêng.
4. **Liên kết cứng:** file trong thư mục dự án có thêm một tên ngoài dự án (`mklink /H`) được nhận. Phải cố ý mới có; gợi ý `st_nlink > 1` thì Cảnh báo.
5. Khóa EC, Ed25519 có dấu PEM đúng: nạp được, chỉ báo khi gọi, câu «Không lấy được mã truy cập… Kiểm tra file khóa còn hiệu lực» chưa đúng nguyên nhân. Kiểm loại khóa lúc nạp sẽ báo đúng chỗ hơn.
6. `token_uri` của khóa rất cũ (`https://accounts.google.com/o/oauth2/token`) bị từ chối theo đúng LC-T094-11; khóa tạo mới không ảnh hưởng. Link Sheet dạng `/a/<tên miền>/spreadsheets/…` (Google Workspace cũ), tên máy viết hoa, thiếu `https://`, `drive.google.com/open?id=`, có `<…>` bao quanh bị từ chối theo đúng LC-T094-15; câu báo dặn chép lại từ thanh địa chỉ.
7. Giờ chờ 30 giây là của **từng lần đọc mạng** (`requests`), không phải tổng thời gian: máy chủ trả nhỏ giọt có thể giữ lâu hơn (giống client WordPress). Thân câu trả lời 3xx được `requests` đọc hết trước khi app kiểm cỡ (Rủi ro 3 của Thợ Máy; xác nhận theo mã `Session.resolve_redirects`). Cả hai chỉ khi máy chủ Google trả lời bất thường.
8. Tên thư mục dạng tổ hợp (NFD) «Drive của tôi» không có Cảnh báo; Box, pCloud, MEGA, Nextcloud không có trong danh sách (ngoài LC-T094-11).
9. Mac/Linux: `os.open` không có `O_NONBLOCK`, file bị đổi thành FIFO đúng lúc giữa kiểm và mở thì treo; Windows không hỏi lại đường thật của handle như bộ đọc ảnh T-079. Cần người chiếm máy, không xếp lỗi.

## Test liên quan

Máy Windows của chủ dự án, worktree `wt-T-097` (đầu nhánh `c260116` + file test của tôi):

```
$ uv run pytest -q -p no:cacheprovider tests/test_soi_loi_t097.py
314 passed, 16 xfailed in 39.23s

$ uv run pytest -q -p no:cacheprovider <26 file>        # 14:01–14:09 +07
2609 passed, 13 skipped, 22 xfailed, 1 warning in 486.32s (0:08:06)

$ uv run ruff check .
All checks passed!
```

Gộp thử với `origin/main` `5e1d831` (`git merge-tree`): không xung đột; từ `b513d67`, `main` chỉ đổi tài liệu (không đụng `seo_app/`, `tests/conftest.py`, `pyproject.toml`, `uv.lock`, `.env.example`).

26 file: 24 file Thợ Máy liệt kê (hai file test mới của phiếu, mọi file chạm `env_file`, `.env.example`, `pyproject.toml`, cấu hình, trang Cài đặt, bộ chặn mạng, lớp AI dùng `google-genai`), file của tôi, và `tests/test_app_pages.py` (trang Cài đặt nhập `env_file`, hàm dùng chung vừa thêm). 22 xfail = 16 của tôi + 6 có từ trước; 13 bỏ qua có từ trước hoặc chỉ chạy trên Mac/Linux (3 của file mới: 2 symlink, 1 `chmod`); 1 cảnh báo pydantic có từ trước.

## Đối chiếu yêu cầu

- [x] Đọc phiếu, thiết kế T-094 (mục 2.1–2.6, mục 6 dòng T-097, mục 7), điều kiện T-094 Lá Chắn («Chung», «T-097», «Chỗ thiếu»), báo cáo Thợ Máy.
- [x] Thử file khóa hỏng/độc, `GOOGLE_SHEET_ID` độc, câu trả lời Sheets lạ, `RAW`, đường cố định, không lộ, bộ chặn mạng, `uv.lock`, `pip-audit`.
- [x] Không gọi Google thật; không sửa code ứng dụng; lỗi ghi thành `xfail(strict=True)` mã SL-T097-n trong `tests/test_soi_loi_t097.py`.
- [x] Test liên quan + `uv run ruff check .` sạch.

## Đề xuất

- **Thợ Máy (lượt 2 T-097 hoặc đầu T-100):** sửa SL-T097-1 (thêm 2 loại lỗi vào nhánh bắt), SL-T097-2 (thêm `unsure=writes`), gỡ 10 dấu `xfail`. T-100 dựa vào `unsure` nên nên sửa trước T-100.
- **Phiếu dọn sau (trước T-101 hiện cảnh báo file khóa):** SL-T097-3 (so theo danh tính file), SL-T097-4 (thêm thư mục Google Drive), cân nhắc Ghi nhận 3, 4, 5.
- **Lá Chắn:** xét Ghi nhận 1, 2 (`load_settings`), 7.
- **Thư Ký (README):** dặn không để file khóa trong thư mục được Google Drive sao lưu (Desktop, Documents…), ngoài «My Drive».

# Biên bản bảo mật T-097 · Client Google Sheets và kiểm file khóa tài khoản dịch vụ · đầy đủ

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-097](../tickets/T-097-google-sheets-service-account.md) (code Thợ Máy `c260116`, test Soi Lỗi `82bf0c0`) |
| Phạm vi | **Đầy đủ** (bí mật, thư viện): toàn bộ diff `b513d67..82bf0c0` (`seo_app/google/service_account.py`, `seo_app/google/sheets.py`, `seo_app/env_file.py`, `pyproject.toml`, `uv.lock`, `.env.example`, `tests/fake_google.py`, 3 file test, 2 báo cáo) và code quanh chỗ sửa (`seo_app/config.py`, `tests/conftest.py`); mã thư viện đã cài mà phiếu dựa vào: `google-auth` 2.62.0 (`google/oauth2/service_account.py`, `google/oauth2/_client.py`, `google/auth/credentials.py`), `requests` 2.34.2 (`sessions.py`), Streamlit 1.65.0 (`elements/exception.py`). Điều kiện LC-T094-1, -2, -3, -11 → -17 |
| Ngày | 2026-10-28 (Chỉ Huy giao 14:20; làm 14:43 → 15:33 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **5 Thấp**: 1 mới của Lá Chắn (**LC-T097-1**, thân câu trả lời chuyển hướng bị đọc hết) và 4 của Soi Lỗi giữ mức Thấp (SL-T097-1 → -4; SL-T097-3 rộng hơn Soi Lỗi ghi: thêm 2 dạng đường dẫn). **Không lỗi nào phải sửa trước khi gộp**; SL-T097-1, -2, LC-T097-1 sửa trước khi T-100 dùng client, SL-T097-3, -4 trước khi T-101 làm trang Cài đặt → Google. Lỗi mới có test `xfail(strict=True)` trong `tests/test_la_chan_t097.py`. Không sửa code ứng dụng |

## Tóm tắt (cho chủ dự án)

Phần đọc, ghi Google Sheet (chưa có nút nào dùng tới) **an toàn để gộp**. Tôi kiểm lại từ đầu, không dựa vào kết quả của Thợ Máy, Soi Lỗi:

- **File khóa Google không bao giờ hiện ra.** Tôi gài chữ mồi vào 12 kiểu file khóa hỏng và 13 kiểu lỗi từ Google, rồi hiện lỗi theo mọi cách thường gặp (câu báo, trang lỗi kiểu Streamlit, log): không chỗ nào có chữ mồi, đường dẫn file khóa, mã Sheet hay mã truy cập.
- **Quyền hẹp đúng thiết kế.** Phần mềm chỉ nói chuyện với 2 máy chủ của Google, chỉ xin quyền Google Sheets (không Google Drive), chỉ dùng đúng file khóa đã kiểm (kể cả khi máy có cài sẵn tài khoản Google khác). Ghi lên Sheet luôn là chữ thường: chữ kiểu công thức `=IMPORTXML(…)` lên Sheet vẫn là chữ. Tôi sửa ngẫu nhiên 60.000 lệnh ghi: không lệnh sai nào lọt qua lớp kiểm.
- **Thư viện `google-auth`** và các gói nó kéo theo (đều đã có sẵn trong máy): không lỗ hổng đã biết (quét 2 nguồn dữ liệu lúc 14:58), giấy phép tự do (Apache, BSD, MIT, MPL).
- **1 điểm nhỏ mới:** nếu máy chủ Google (hay kẻ đã chiếm được máy hoặc mạng, có chứng chỉ được máy tin) trả lời kiểu «chuyển hướng» kèm dữ liệu nén cực lớn, phần mềm giải nén hết vào bộ nhớ rồi mới báo lỗi (thử: 100 KB nén thành 200 MB bộ nhớ). Không lộ gì, không ghi gì, chỉ có thể làm phần mềm treo. Sửa dễ, tôi đã thử cách sửa.
- **4 điểm nhỏ của Soi Lỗi:** giữ mức Thấp. Một điểm (gõ đường dẫn file khóa theo kiểu đặc biệt của Windows thì phép chặn «file khóa nằm trong thư mục phần mềm/thư mục ảnh» bị qua mặt) rộng hơn Soi Lỗi ghi: có thêm 2 kiểu gõ; cách sửa phải so «cùng một thư mục thật».
- **Việc của bạn:** không có. Giữ lời dặn: để file khóa trong một thư mục riêng trên máy, không trong thư mục phần mềm, thư mục ảnh hay thư mục Google Drive, OneDrive.

## Lỗi phát hiện

Số dòng theo `82bf0c0`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T097-1 | Thấp | **Câu trả lời chuyển hướng (3xx có `Location`) bị `requests` đọc và giải nén hết vào bộ nhớ trước khi client kiểm cỡ**: giới hạn 2 MB (Sheets) và 64 KB (lệnh xin mã) không áp dụng cho nhánh này, nên LC-T094-13 («câu trả lời đọc theo luồng, quá 2 MB thì bỏ») chưa trọn. Thợ Máy đã nêu (Rủi ro 3), Soi Lỗi ghi nhận (Ghi nhận 7); Lá Chắn đo phần giải nén, thấy cả lệnh xin mã cũng bị, và thử cách sửa | `seo_app/google/sheets.py:803-820` (lệnh Sheets), `:347-359` (lệnh xin mã), `:577` (`max_redirects = 0`); `requests/sessions.py:818-824` (`allow_redirects=False` vẫn gọi `resolve_redirects`), `:212` (`resp.content`), `:216` (`TooManyRedirects` sau khi đã đọc) | `sheets.googleapis.com` hay `oauth2.googleapis.com` (https, chứng chỉ được kiểm, nên chỉ Google hoặc kẻ nghe lén có chứng chỉ được máy tin, xem sổ rủi ro 2026-10-28) trả 302 + `Location` + thân gzip → `Session.send` gọi `resolve_redirects(yield_requests=True)` dù `allow_redirects=False` → `resp.content` đọc và giải nén **hết** thân → mới ném `TooManyRedirects` → app ra câu «chuyển hướng» (đúng). Đo bằng `probe_t097.py bom`: thân nén 100 KB (100 MB khi giải nén) → bộ nhớ đỉnh **201 MB**, 1,1–1,5 s, ở cả lệnh đọc kế hoạch lẫn lệnh xin mã. Cùng thân với mã 200: đỉnh 2,3 MB (Sheets), 0,4 MB (xin mã), bị bỏ đúng. Thân nén 1 MB ≈ 1 GB khi giải nén: app có thể hết bộ nhớ, treo. Không lệnh nào đi tới địa chỉ chuyển hướng (0/3 ca), không lộ, không ghi gì. Test: 7 ca `xfail` (thân 8 MB với 301, 302, 303, 307, 308; lệnh thêm dòng 307; lệnh xin mã 302): đọc 8.388.608 byte, giới hạn 2.097.152 | Thêm móc `hooks={"response": [_refuse_redirect]}` cho **cả hai** lệnh (`_call`, `_TokenRequest`): móc chạy **trước** `resolve_redirects` (`sessions.py:791` so với `:818`); gặp 3xx thì `response.close()` (không đọc thân) rồi ném một lỗi riêng; `_call` đổi lỗi đó thành `SheetsError` câu «chuyển hướng» với `unsure=writes`; `_TokenRequest` trả `_TokenResponse(mã, {}, b"")` như nhánh hiện có. Giữ `max_redirects = 0`. Đã thử trên bản sao (mục «Sửa mẫu»): 7/7 `xfail` thành XPASS, không test nào hỏng; sửa cách này thì SL-T097-2 cũng đi chung một nhánh |

## Xếp mức 4 lỗi của Soi Lỗi (việc 7)

| Mã | Soi Lỗi | Lá Chắn | Vì sao (đường đi thật) | Sửa trước |
|---|---|---|---|---|
| SL-T097-1 | Thấp | **Thấp, giữ** | `OverflowError`, `RecursionError` lọt khi máy chủ mã trả lời lạ. Tôi thử lại 4 ca có gài mồi vào mã truy cập: lỗi lọt **không** có mồi (thông điệp chỉ là `date value out of range`, `maximum recursion depth…`; traceback chỉ có dòng code), không lệnh Sheets nào được gửi (lỗi xảy ra trước). Hậu quả là trang hiện lỗi kỹ thuật (tiền lệ LC-T044-1, LC-T085-1: Thấp) | Trước T-100, T-101 (phiếu dọn T-097). Bắt **đúng hai loại này** ở nhánh cuối của `_access_token`; **không** đổi thành `except Exception`: bản sửa thử bằng `Exception` làm hỏng `test_bo_chan_mang_chan_ca_client_sheets_khong_co_site_gia` (test cần `RealNetworkBlocked` của bộ chặn mạng lọt ra) |
| SL-T097-2 | Thấp | **Thấp, giữ** | Lệnh ghi gặp 3xx **không** `Location` báo `unsure=False`; T-100 có thể thêm dòng lần nữa (dòng trùng). Không lộ, không đụng website; Google không trả kiểu này cho lệnh đúng | Trước T-100; sửa cùng LC-T097-1 |
| SL-T097-3 | Thấp | **Thấp, giữ; rộng hơn Soi Lỗi ghi** | Thêm 2 dạng lọt: `\\?\Volume{…}\…` và `\\?\GLOBALROOT\??\<ổ>:\…`, vào cả thư mục dự án lẫn thư mục ảnh (4 `xfail` mới trong file của tôi). Bị bắt đúng: `\\.\…`, `\\.\Volume{…}\…`, tên ngắn 8.3, đường thường (đường thật được chuẩn hóa). Phải tự gõ dạng đặc biệt vào `.env`; nội dung file vẫn kiểm đủ, câu báo cố định. Chốt này để tránh **lỡ** đưa khóa lên git hay lên mây, không có kẻ tấn công nào được lợi | Trước T-101. Sửa bằng **danh tính thư mục**: đi ngược các thư mục cha của đường gõ và đường thật, so `(st_dev, st_ino)` với thư mục dự án và từng gốc thư mục ảnh (bỏ qua khi `st_ino == 0`, như `seo_app/images/folders.py`). Đã thử: 8/8 `xfail` SL-T097-3 (4 Soi Lỗi + 4 Lá Chắn) thành XPASS; đối chứng «file ngoài hai thư mục, gõ dạng nào cũng nhận» vẫn qua. Chỉ bỏ tiền tố `\\?\` thì dạng Volume, GLOBALROOT vẫn lọt. Cách này cũng bịt Rủi ro 5 của Thợ Máy (Mac không phân biệt hoa thường; suy luận, chưa thử trên Mac) |
| SL-T097-4 | Thấp | **Thấp, giữ** | Chỉ là Cảnh báo «thư mục đồng bộ»; file vẫn dùng được | Trước T-101 hiện cảnh báo |

## Kết quả theo việc Chỉ Huy giao

**1. Cổng bảo mật mục 3 `security.md`: đủ 5 bước.** Đọc toàn bộ diff và code quanh chỗ sửa (bước 1); danh sách kiểm tra mục 4 (bên dưới, bước 2); công cụ mục 5, mỗi cảnh báo đã xác minh (bước 3); mỗi lỗi có đường đi thật (bước 4); biên bản theo mẫu (bước 5).

**2. Bí mật: đạt.**

- **Không lọt file khóa, khóa riêng.** `seo_app/google/` không có `print`, `logging`, `lru_cache`, `st.cache_*`, `verify=` (grep). Câu báo là hằng `_MSG_*`; mọi chỗ bắt lỗi dùng `from None`. Script `probe_t097.py loi`: 12 file khóa hỏng có mồi trong nội dung (JSON hỏng, UTF-8 hỏng, UTF-16, trùng khóa, sai loại, PEM rác có mồi, địa chỉ lấy mã, email, mã khóa riêng, `universe_domain` lạ, lồng sâu, số 5.000 chữ số) và mồi trong **đường dẫn** thư mục chứa file: `str`, `repr`, `traceback.format_exception`, `marshall` của Streamlit 1.65 (cách `st.exception` hiện lỗi) và `logging` với `exc_info`: **0 mồi, 0 đường dẫn**. Mã truy cập chỉ nằm trong `credentials.token` (bộ nhớ), không ghi đĩa; `ServiceAccount`, `SheetsClient`, `_Bearer` có `repr` che (đã thử). `st.session_state`: phiếu chưa có giao diện, đặt điều kiện cho T-101 (mục «Điều kiện»). Git: mục «Kết quả công cụ quét».
- **Lỗi của thư viện, máy chủ mã, Sheets thành câu cố định**: 6 kiểu lỗi xin mã có mồi (`invalid_grant`, `invalid_client`, 500, mã có xuống dòng, thiếu mã, JSON là mảng) và 7 kiểu lỗi Sheets (403, 500 có mồi, JSON hỏng, lỗi kết nối, hết giờ, SSL, hết giờ khi ghi; lời lỗi gài mã Sheet và mã truy cập): câu đúng, 0 mồi, 0 mã Sheet, 0 mã truy cập, 0 email ở mọi cách hiện.
- **Quyền file, đường dẫn lạ:** Mac/Linux `st_mode & 0o077` → Cảnh báo kèm `chmod 600` (lấy từ `fstat` của chính handle, `service_account.py:175`); mở **một lần** (`os.open`, `O_NOFOLLOW` trên Mac/Linux), `fstat` file thường, ≤ 64 KB, so `(st_dev, st_ino)` handle với đường đã kiểm (`:210-246`). Junction vào dự án: từ chối (test Thợ Máy); máy này không tạo được symlink (WinError 1314, như Soi Lỗi ghi), ca symlink có test chạy trên Mac/Linux. Dạng đường dẫn thiết bị: SL-T097-3 (rộng hơn). Liên kết cứng: Ghi nhận 6.

**3. Phạm vi quyền: đạt.** Bắt lệnh xin mã (`probe_t097.py mang`) và đọc JWT: header `alg` `RS256`, `kid` đúng mã khóa; claims **đúng** 5 trường `iss` (email file đã kiểm), `scope` (**đúng một** phạm vi `https://www.googleapis.com/auth/spreadsheets`), `aud` (`https://oauth2.googleapis.com/token`), `iat`, `exp` (1 giờ); **không** `sub` (không ủy quyền toàn miền); chữ ký kiểm được bằng khóa của file đã kiểm, trong khi `GOOGLE_APPLICATION_CREDENTIALS` trỏ một file khóa khác. Không gọi Drive: chỉ 5 đường Sheets cố định (`_ROUTES`, `sheets.py:89-109`). Đọc mã thư viện: `refresh()` chỉ gọi `_perform_refresh_token` → `jwt_grant` tới `token_uri` (hằng của app); luồng nền «regional access boundary» (`iamcredentials.googleapis.com`) chỉ chạy từ `before_request`, app không gọi (số luồng trước, sau bằng nhau); biến môi trường duy nhất thư viện đọc trên đường này là `GOOGLE_CLOUD_QUOTA_PROJECT`, chỉ trong `with_quota_project_from_environment` (app không gọi; thử đặt biến: không có header `x-goog-user-project`).

**4. Ghi Sheets luôn `RAW`: đạt.** Lớp kiểm `_check_call` (`sheets.py:723-754`) chặn trước cả lệnh xin mã: ghi ô đòi `valueInputOption == "RAW"` trong thân (`:392-417`), thêm dòng đòi tham số **đúng bằng** `_APPEND_PARAMS` (`RAW`, `INSERT_ROWS`), `:batchUpdate` chỉ 4 loại, `repeatCell` chỉ định dạng số, danh sách chọn không bắt đầu bằng `= + - @`. Thử đột biến (`probe_t097.py kiem`): 4 loại lệnh × 15.000 thân sửa ngẫu nhiên (đổi giá trị, xóa, thêm khóa, lồng): 2.505 thân được nhận, **cả 2.505** đúng bộ kiểm độc lập của tôi (`RAW`, vùng một ô `'KeHoach'!<A–Z><1–1001>`, giá trị đơn, đúng 4 loại cấu trúc, đúng mã tab); 17 đường, phương thức, tham số lạ (`:clear`, `values:batchClear`, `batchUpdateByDataFilter`, `fields=*`, `includeGridData`, `valueRenderOption=FORMULA`, `..`, `%2F..%2F`, `DELETE`, `PUT`, `copyTo`, `developerMetadata`, mã Sheet khác, có `\n`, `?`, `#`): chặn hết. Lệnh gửi đi thật (bắt ở phiên): ghi ô và thêm dòng đều `RAW`, không chữ `USER_ENTERED` ở đâu. Công thức khi chủ dự án tải Sheet về mở bằng Excel: điều kiện LC-T094-28 của T-100.

**5. Mạng: đạt, trừ LC-T097-1.** Bắt mọi lệnh (`probe_t097.py mang`, luồng đủ 5 lệnh): chỉ `oauth2.googleapis.com` và `sheets.googleapis.com`; mọi lệnh `allow_redirects=False`, `stream=True`, giờ chờ ≤ 30 giây (lệnh xin mã bỏ qua 120 giây của thư viện, `sheets.py:352`); xin mã đúng 1 lần, không header `Authorization`; mã `Bearer` chỉ gửi tới Sheets; đặt `NETRC` có mật khẩu cho cả hai máy chủ: không header `Basic` (app luôn đưa `auth` riêng). Kiểm chứng chỉ: mặc định của `requests`, không chỗ nào tắt. Chuyển hướng: không bao giờ đi theo (0 lệnh tới `Location` ở mọi ca), nhưng thân bị đọc hết: LC-T097-1. Giới hạn cỡ với thân gzip 300 MB khi giải nén (nén 299 KB): lệnh đọc kế hoạch dừng ở 2 MB (đỉnh 2,3 MB, 0,03 s), lệnh xin mã dừng ở 64 KB (đỉnh 0,4 MB). Biến proxy, chứng chỉ của máy (`HTTPS_PROXY`, `REQUESTS_CA_BUNDLE`…): đã ghi sổ rủi ro 2026-10-28. Link Sheet (`probe_t097.py link`): 40.000 chuỗi trộn tên máy giả (`docs.google.com.`, `:443`, `@`, `\`, `%2E`, chấm `。`, chữ Kirin, `xn--`, `[::1]`), lược đồ lạ, đường lạ, chèn ký tự: nhận 127, cả 127 đúng `https://docs.google.com/spreadsheets/…` và mã đúng dạng; câu báo không chép mã.

**6. Thư viện: đạt.**

| Gói | Bản (khóa trong `uv.lock`) | Giấy phép | Vì sao có |
|---|---|---|---|
| `google-auth` | 2.62.0 | Apache-2.0 | Khai báo mới (câu 1A, chủ dự án chốt 28/10); đã có từ trước nhờ `google-genai` |
| `cryptography` | 50.0.2 | Apache-2.0 OR BSD-3-Clause | Phụ thuộc của `google-auth` (đã có) |
| `cffi`, `pycparser` | 2.1.1, 3.11 | MIT-0, BSD-3-Clause | Phụ thuộc của `cryptography` (đã có) |
| `pyasn1-modules`, `pyasn1` | 0.4.2, 0.6.4 | BSD, BSD-2-Clause | Phụ thuộc của `google-auth` (đã có) |
| `requests`, `urllib3`, `certifi`, `charset-normalizer`, `idna` | 2.34.2, 2.8.0, 2026.10.19, 3.5.2, 3.20 | Apache-2.0, MIT, MPL-2.0, MIT, BSD-3-Clause | `requests` đã khai báo (client WordPress) |

- `pyproject.toml`: `google-auth>=2.62.0` (cận dưới đúng bản đã khóa, không nới). `git diff b513d67..82bf0c0 -- uv.lock`: +2 dòng, đều là khai báo của dự án; `uv lock --locked --offline`: «Resolved 70 packages», khớp (như trước phiếu).
- `pip-audit` 2.10.1: nguồn PyPI trên `uv export --frozen --no-hashes --no-emit-project` (69 gói, 14:58–14:59): «No known vulnerabilities found»; nguồn OSV trên 11 gói của chuỗi `google-auth`, `requests` (14:59): «No known vulnerabilities found».
- Không kéo thêm thư viện ngoài khai báo: code mới chỉ nhập `google.auth.exceptions`, `google.auth.transport`, `google.oauth2.service_account`, `requests` và thư viện chuẩn. Test nhập thêm `cryptography`, `urllib3` (có sẵn, chỉ để sinh khóa và giả thân trả lời). Không `gspread`, `google-api-python-client`, `openpyxl`.

**7. 4 lỗi Thấp của Soi Lỗi: không lỗi nào phải nâng mức** (bảng «Xếp mức» ở trên).

**8. Gộp thử với `main` trên máy: đạt.**

- `main` cục bộ `1b45f5d` (đã gộp T-096, chưa đẩy lên `origin`): `git merge-tree --write-tree main team/T-097` → cây `650c7b5`, **không xung đột**; hai bên không chung file nào (`main` đổi `seo_app/publish/*`, `seo_app/onpage/links.py`, tài liệu). Giải nén cây gộp vào thư mục nháp, `seo_app` nạp từ cây gộp; 32 file (26 file liên quan của T-097, 5 file test T-096: `test_publish_markdown.py`, `test_publish_render.py`, `test_soi_loi_t096.py`, `test_la_chan_t096.py`, `test_la_chan_t039.py`, và `test_wordpress_published.py`), 15:10–15:21: **3.058 passed, 13 skipped, 26 xfailed, 0 hỏng** (26 xfail = 22 của T-097 + 4 LC-T096-5 có sẵn).
- `main` + T-090 (`team/T-090` `4af2d4b`, sắp gộp; commit tạm `1f0271c`, không đẩy) + T-097: không xung đột, cây `54d4b21`. T-090 đổi `config.load_settings` (`.env` không phải UTF-8 thì ném `ConfigError`), mà `SheetsClient.from_settings()` gọi `load_settings()` khi không truyền `settings`: T-101 phải bắt cả `ConfigError` (mục «Điều kiện»). Cây gộp ba bên giải nén vào thư mục nháp, 23 file (3 file test T-097, file của tôi, `test_env_file.py`, `test_config.py`, `test_config_tolerance.py`, `test_settings_keys.py`, `test_hash_password_script.py`, `test_soi_loi_t084.py`, `test_app_pages.py`, 4 file test T-090, `test_t041_meta.py`, `test_t041_schema.py`, `test_soi_loi_t041.py`, `test_la_chan_t041.py`, `test_safety.py`, `test_soi_loi_t016_t020.py`, `test_soi_loi_t021_t017.py`, `test_phase2_fixes.py`), 15:26–15:32: **1.679 passed, 13 skipped, 44 xfailed, 0 hỏng** (44 xfail = 16 Soi Lỗi T-097 + 11 Lá Chắn T-097 + 17 LC-T090-1, -2 có sẵn).

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` 0 trên 12 file của phiếu (mồi «Private Key» trong file tiếng Việt: bắt được); `git log -p b513d67..HEAD`: không khối PEM, không mã `ya29.`, `AIza`, `sk-ant-`, chỉ email, mã khóa bịa; khóa RSA sinh lúc chạy test, dấu PEM trong code ghép từ hai nửa (LC-T094-17) |
| S2 | Đạt | Việc 2 ở trên: 25 kiểu lỗi có mồi, 5 cách hiện lỗi, 0 lọt. SL-T097-1 làm lỗi kỹ thuật lọt nhưng không có bí mật. Lỗi gốc vẫn gắn trong bộ nhớ (Ghi nhận 1) |
| S3 | Đạt | `.env.example`: chú thích tiếng Việt cho `GOOGLE_SERVICE_ACCOUNT_FILE` (ngoài thư mục phần mềm, thư mục ảnh, thư mục đồng bộ; tên file Google không bị `.gitignore` chặn; `chmod 600`; chỉ sửa tay) và `GOOGLE_SHEET_ID` (dạng mã, giữ kín, không bật «Bất kỳ ai có đường liên kết»); giá trị để trống, ví dụ dùng tên bịa |
| W1 | Không áp dụng | Phiếu không đụng WordPress |
| W2 | Không áp dụng | Như trên. Với Sheet: không lệnh xóa tab, dòng, vùng (`_valid_structure_request` chỉ 4 loại) |
| W3 | Không áp dụng | Không gửi HTML |
| W4 | Đạt (áp cho Google) | `https://` cố định, kiểm chứng chỉ mặc định, giờ chờ ≤ 30 giây mọi lệnh (kể cả xin mã), không theo chuyển hướng. Thân 3xx: LC-T097-1 |
| A1 | Không áp dụng | Không gọi AI. Dữ liệu Sheet vào lời dặn AI: T-098, T-103 |
| A2 | Không áp dụng | Như trên |
| A3 | Không áp dụng | Như trên |
| U1 | Không áp dụng | Chưa có giao diện; điều kiện cho T-101 (LC-T094-3, mục «Điều kiện») |
| U2 | Không áp dụng | Như trên |
| U3 | Không áp dụng | Như trên |
| F1 | Đạt (Thấp SL-T097-3) | File khóa do người dùng khai báo; app **từ chối** file trong thư mục dự án, thư mục ảnh (so cả đường gõ và đường thật), đọc một lần qua handle, ≤ 64 KB, file thường. Dạng `\\?\…`, `\\?\Volume{…}`, `\\?\GLOBALROOT` lọt: SL-T097-3 |
| F2 | Không áp dụng | Không xử lý ảnh |
| F3 | Đạt | File khóa đọc dạng byte, giải mã `utf-8-sig`; `json.loads` có chặn khóa trùng; không `eval`, `pickle`, `yaml` |
| D1 | Đạt | `google-auth` được chủ dự án duyệt (câu 1A, 28/10); `pip-audit` sạch ở 2 nguồn; không gói mới trong `uv.lock` |
| D2 | Đạt | `.gitignore` không đổi: vẫn chặn `.env`, `*service-account*.json`, `secrets/`, `data/`, `*.sqlite`. Tên file Google tự đặt (`ten-project-1a2b3c….json`) không bị chặn: bù bằng việc app từ chối file khóa trong thư mục dự án và lời dặn ở `.env.example` (Ghi nhận 8) |
| D3 | Đạt | `tests/conftest.py` không đổi (bộ chặn mạng bật); Google giả gắn vào phiên (`tests/fake_google.py`, Google giả riêng của Soi Lỗi, của tôi); test của Thợ Máy, Soi Lỗi chứng minh bộ chặn bắt cả phiên thật của client và lớp chuyển của `google-auth` |

## Đối chiếu điều kiện LC-T094 của phiếu

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T094-1 | Đạt | D3 |
| LC-T094-2 | Đạt, trừ SL-T097-1 (Thấp) | Việc 2; 2 loại lỗi lọt không chứa bí mật |
| LC-T094-3 | Phần client đạt; phần giao diện thuộc T-101 | `_clean_text` bỏ ký tự loại Cc, Cf (có U+202A–U+202E, U+2066–U+2069, U+200B), Cs, Co, Cn ở tên Sheet, tên tab; chữ ô trả nguyên, T-100 qua `PlanRow` |
| LC-T094-11 | Đạt, trừ SL-T097-3, -4 (Thấp) | Việc 2; «mỗi lần dùng»: `from_settings` gọi lại `load_service_account` mỗi lần, T-101 không được giữ client (điều kiện) |
| LC-T094-12 | Đạt | Việc 2; giao diện: điều kiện T-101 |
| LC-T094-13 | Đạt, trừ LC-T097-1, SL-T097-2 (Thấp) | Việc 4, 5 |
| LC-T094-14 | Đạt | Việc 3 |
| LC-T094-15 | Đạt, có một chỗ lệch đã khai (chấp nhận, Ghi nhận 4) | `sheet_id_from_link` (40.000 mẫu), `validate_sheet_id` + `set_google_sheet_id` (test Thợ Máy 17 ca, Soi Lỗi 20 ca: `.env` không đổi một byte); `GOOGLE_SERVICE_ACCOUNT_FILE` không có hàm ghi; `repr` che mã Sheet; câu báo không chép mã |
| LC-T094-16 | Đạt | Việc 6 |
| LC-T094-17 | Đạt | S1 |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | 0 lỗ hổng: nguồn PyPI 69 gói (14:58–14:59), nguồn OSV 11 gói chuỗi `google-auth` (14:59) | Đọc từ `uv export --frozen` (đúng bản khóa) |
| bandit 1.9.4 | 3 Low trên `seo_app/google/`, `seo_app/env_file.py` (1.460 dòng) | Cả 3 báo nhầm (mục dưới). Trên Windows phải đặt `PYTHONUTF8=1` (không thì bandit hỏng khi in chữ Việt) |
| detect-secrets 1.5.0 (`PYTHONUTF8=1`) | 0 trên 12 file của phiếu và trên `tests/test_la_chan_t097.py` | Mồi «Private Key» trong bản sao `service_account.py` (có chữ Việt): bắt được; đã xóa mồi |
| Soát lịch sử git | `git log -p b513d67..HEAD`: không khối PEM, mã truy cập, khóa API; 209 dòng có chữ `token`, `secret`, `password`, `api_key` đều là tên biến, câu báo, chữ trong báo cáo | Đọc lướt kết quả grep |
| pytest | Nhánh: 26 file liên quan (14:57–15:08) **2.609 passed, 13 skipped, 22 xfailed, 0 hỏng**; `tests/test_la_chan_t097.py`: 8 passed, 11 xfailed. Cây gộp: việc 8 | `xfail` đều có mã lỗi; 13 bỏ qua có sẵn hoặc chỉ chạy trên Mac/Linux |
| ruff | `uv run ruff check .`: sạch | |
| Script dò độc lập | `probe_t097.py` (thư mục nháp, không commit): **40.145 ca, 0 hỏng** (lượt đủ 15:31) (phần `loi`, `mang`, `kiem`, `link`, `bom`, `duong`) | Script tự chặn socket ở dòng đầu; ghi chú bàn giao có đường dẫn |

## Báo nhầm đã loại

- bandit B105 `service_account.py:44` (`TOKEN_URI = "https://oauth2.googleapis.com/token"`) và `:101-104` (`_MSG_BAD_TOKEN_URI`, câu báo): tên biến có chữ «TOKEN», giá trị là địa chỉ công khai của Google và câu tiếng Việt, không phải mật khẩu.
- bandit B311 `sheets.py:788` (`random.uniform(0, 0.5)`): độ lệch ngẫu nhiên của thời gian chờ thử lại khi gặp 429, không dùng cho bảo mật.

## Sửa mẫu (chỉ trên bản sao, không commit)

Bản sao nhánh (`git archive HEAD` + file test của tôi) trong thư mục nháp, script `patch_sua_mau_097.py`: LC-T097-1 (móc `response` chặn 3xx cho cả `_call` và `_TokenRequest`), SL-T097-1 (thêm `OverflowError`, `RecursionError`), SL-T097-2 (`unsure=writes`), SL-T097-3 (`_is_within` so `(st_dev, st_ino)` các thư mục cha trước, rồi mới so chuỗi như cũ), SL-T097-4 (thêm 4 tên thư mục). Chạy 4 file (`test_google_sheets.py`, `test_google_service_account.py`, `test_soi_loi_t097.py`, `test_la_chan_t097.py`, 15:21–15:25): **27 XPASS(strict)** (đúng 27 ca `xfail` của 5 lỗi), **569 passed**, 3 skipped, **0 hỏng khác**. Lượt thử đầu bắt `Exception` ở SL-T097-1 thì hỏng 1 test Thợ Máy (bảng «Xếp mức», SL-T097-1).

## Ghi nhận (không xếp lỗi)

1. **Lỗi gốc vẫn gắn kèm trong bộ nhớ.** `raise … from None` ẩn lỗi gốc khi hiện nhưng vẫn giữ nó ở `__context__`: với file khóa JSON hỏng, `JSONDecodeError.doc` và `UnicodeDecodeError.object` là **toàn bộ nội dung file** (có `private_key`). Mọi cách hiện đã thử đều tôn trọng `__suppress_context__` (traceback chuẩn, Streamlit 1.65 `elements/exception.py:490`, `logging`), nên không lộ. T-101 chỉ hiện `str(err)` bằng chữ thường, không `st.exception(err)`, không giữ đối tượng lỗi trong `st.session_state`. Muốn chắc hơn: ném lỗi cố định sau khối `except` (không có ngữ cảnh), như đã làm ở vài chỗ khác.
2. **`_check_call` có thể ném `TypeError`, `ValueError`** (không phải `SheetsError`) khi nơi gọi đưa thân hay tham số hỏng kiểu lạ (ví dụ `numberFormat.type` là danh sách, tham số không phải dict): 3.564/60.000 đột biến của tôi rơi vào đây, không lệnh nào được gửi; chỉ code của app (T-100) gọi, dựng từ hằng. Không xếp lỗi.
3. **Client WordPress** (`seo_app/wordpress/client.py:1481-1483`) có cùng cách đọc thân 3xx và không giới hạn cỡ câu trả lời nói chung (có từ Giai đoạn 1, máy chủ là website của chủ dự án): ngoài phạm vi T-097; Chỉ Huy cân nhắc gom vào phiếu dọn client WordPress sau.
4. **`load_settings` chưa kiểm dạng `GOOGLE_SHEET_ID`** (Rủi ro 1 của Thợ Máy, Ghi nhận 1 của Soi Lỗi; LC-T094-15 lệch): **chấp nhận**. Mọi đường gọi mạng kiểm mã trước (`from_settings`, `SheetsClient.__init__`); không code nào khác đọc `google_sheet_id` (grep `app/`, `seo_app/`, `scripts/`). Còn lại: `Settings.__repr__` in đủ mã Sheet và đường dẫn file khóa (hai trường chưa `repr=False`; hiện không chỗ nào in `Settings`). Khi `seo_app/config.py` được mở lại (có duyệt của chủ dự án): kiểm dạng mã khi đọc và thêm `repr=False` cho hai trường.
5. **Thế biến trong `.env`** (Ghi nhận 2 của Soi Lỗi): đúng, nhưng chỉ khóa **Gemini** (39 ký tự) lọt dạng mã Sheet; khóa Anthropic (khoảng 108 ký tự) và khóa dự án OpenAI (dài hơn 100) không. Chỉ xảy ra khi tự gõ `GOOGLE_SHEET_ID=${GEMINI_API_KEY}` vào `.env` (bộ ghi của app chặn `$`), và khóa chỉ đi tới máy chủ Google. Không xếp lỗi; làm cùng mục 4 (đọc biến này không thế biến, hay từ chối khi dòng gốc có `$`).
6. **Liên kết cứng** (Ghi nhận 4 của Soi Lỗi): cùng loại rủi ro đã ghi sổ cho thư mục ảnh (LC-T048-6, 2026-10-20); phải cố ý tạo. Nên (không bắt buộc): `st_nlink > 1` thì Cảnh báo.
7. **Giờ chờ 30 giây là của từng lần đọc mạng** (Ghi nhận 7 của Soi Lỗi), lệnh xin mã có thể đi 3 lần (Rủi ro 2 của Thợ Máy, xấu nhất khoảng 90 giây cộng thời gian chờ): giống client WordPress, chỉ khi máy chủ Google trả lời bất thường; chấp nhận. T-101 hiện vòng chờ khi gọi Google.
8. **Tên file khóa Google tự đặt không bị `.gitignore` chặn** (`.env.example` đã ghi): chốt thật là app từ chối file khóa trong thư mục dự án. README (Thư Ký) nhắc lại khi hướng dẫn tạo khóa (LC-T094-43).

## Điều kiện

1. **Phiếu dọn T-097 (Thợ Máy), trước khi T-100 dùng client:** sửa LC-T097-1 (móc `response` chặn 3xx trước khi đọc thân, cả `_call` và `_TokenRequest`), SL-T097-1 (bắt thêm đúng `OverflowError`, `RecursionError`), SL-T097-2 (`unsure=writes`); gỡ 17 dấu `xfail` (7 trong `tests/test_la_chan_t097.py`, 10 trong `tests/test_soi_loi_t097.py`). Lá Chắn rút gọn xem lại.
2. **Trước khi T-101 làm trang Cài đặt → Google:** sửa SL-T097-3 bằng danh tính thư mục (không chỉ bỏ tiền tố), SL-T097-4; gỡ 10 dấu `xfail` (4 của tôi, 6 của Soi Lỗi). Có thể gộp vào phiếu dọn ở điều kiện 1.
3. **T-101 (Họa Sĩ), thêm vào điều kiện LC-T094-3, -11, -12, -15 đã có:**
   - Tạo `SheetsClient.from_settings()` mới cho mỗi lần bấm; không `st.cache_resource`, `st.cache_data`, không giữ client, `ServiceAccount`, `credentials` hay đối tượng lỗi trong `st.session_state`.
   - Bắt `SheetsError`, `ServiceAccountError` và `ConfigError` (sau T-090 `load_settings` ném lỗi này khi `.env` sai bảng mã); hiện `str(err)` bằng chữ thường. Không `st.exception(err)`, không `st.write`/`st.help` đối tượng client hay `credentials` (`st.help` liệt kê thuộc tính công khai, trong đó có `token`).
   - Tên file khóa, email dịch vụ, câu Cảnh báo hiện bằng chữ thường, bỏ ký tự điều khiển, đổi hướng chữ (tên file trên Mac/Linux có thể chứa các ký tự đó).
   - Không hiện `settings.google_sheet_id`: dùng tên Sheet (`get_info().title`) hoặc `mask_sheet_id`.
4. **Khi `seo_app/config.py` được mở lại** (chủ dự án duyệt): Ghi nhận 4, 5 (nên, Thấp).
5. **Lượt thử thật (LC-T094-44):** lệnh Google thật đầu tiên chỉ tới 2 máy chủ, khuôn câu trả lời đúng như client đọc.

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 5 Thấp (LC-T097-1 mới; SL-T097-1 → -4 giữ Thấp). **Gộp `main` được ngay** (chủ dự án đã chốt câu 1A sáng 28/10; không lỗi nào phải sửa trước khi gộp). Điều kiện 1–2 vào phiếu dọn trước T-100, T-101; điều kiện 3 chép vào phiếu T-101.

## Xem lại lượt 2 (rút gọn) · 2026-10-28

| Mục | Nội dung |
|---|---|
| Phạm vi | Diff `24013b3..16b9f64`: Thợ Máy lượt 2 `8b98996` (`seo_app/google/sheets.py`: `_Redirected`, `_refuse_redirect`, móc `response` ở `_TokenRequest` và `_call`, bắt thêm `OverflowError`, `RecursionError`; `seo_app/google/service_account.py`: `_identity`, `_inside_by_identity`, `_SYNC_MARKERS`, `in_sync_folder`; gỡ 27 dấu `xfail`; 6 ca mới) và Soi Lỗi lượt 2 `16b9f64` (86 ca mới, SL-T097-5). Chỉ Huy giao 20:45; làm 20:44 → 21:04 +07 |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**. **LC-T097-1 đóng thật**; SL-T097-1 → -4 đóng, không mở lỗ mới. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp còn mở: SL-T097-5** (Soi Lỗi, lùi do lượt 2: chặn oan đường có `..`, hướng an toàn; giữ Thấp). Lá Chắn không có lỗi mới. Không lỗi nào phải sửa trước khi gộp |

### Tóm tắt (cho chủ dự án)

- Điểm nhỏ tôi báo ở lượt 1 (Google trả lời «chuyển hướng» kèm dữ liệu nén rất lớn làm phần mềm tốn bộ nhớ) **đã sửa thật**: phần mềm đóng câu trả lời đó ngay, không đọc byte nào. Thử lại đúng ca cũ: bộ nhớ từ 200 MB xuống gần 0.
- 4 điểm nhỏ của Soi Lỗi cũng đã sửa, không mở lỗ mới: lỗi lạ từ Google vẫn không làm lộ khóa hay mã truy cập; file khóa trong thư mục phần mềm, thư mục ảnh bị bắt với mọi cách viết đường dẫn đặc biệt của Windows.
- Còn 1 điểm nhỏ mới (Soi Lỗi tìm ra): đường dẫn file khóa gõ kiểu có «..» đi ngang thư mục phần mềm bị từ chối nhầm. Không lộ gì; gõ đường dẫn bình thường thì không gặp. **Việc của bạn:** không có.

### Việc 1: LC-T097-1 đóng thật

- **Móc `_refuse_redirect`** (`sheets.py:292-300`) gắn vào **cả hai** lệnh (`hooks={"response": …}` ở `:376` và `:847`). `requests` chạy móc ngay sau khi có mã trả lời (`requests/sessions.py:791`), **trước** `resolve_redirects` (`:818`, chỗ đọc hết thân). Móc chặn mọi mã 300–399, có hay không `Location`: `response.close()` (thân chưa đọc thì đóng luồng urllib3, đóng luôn kết nối, không trả về hàng chờ), rồi ném `_Redirected`. `_call` đổi thành `SheetsError` câu «chuyển hướng», `unsure` theo loại lệnh (`:849-854`); `_TokenRequest` trả `_TokenResponse(mã, {}, b"")` (`:378-380`), google-auth báo lỗi xin mã thành câu cố định. Vẫn giữ `allow_redirects=False`, `max_redirects = 0`, nhánh `TooManyRedirects` và nhánh kiểm `300 <= status < 400` để phòng thêm.
- **Script `probe_t097_l2.py`** (thư mục nháp, không commit), **715 ca, 0 hỏng**:
  - `chuyen`: 10 mã (300, 301, 302, 303, 304, 305, 306, 307, 308, 399) × có/không `Location` (kèm `Content-Encoding: gzip`) × 6 lệnh (đọc thông tin, đọc kế hoạch, ghi ô, thêm dòng, sửa cấu trúc, xin mã). Thân là «bẫy» đếm byte: **0 byte bị đọc**, thân đã đóng, không lệnh nào tới địa chỉ chuyển hướng. `status_code` đúng; `unsure` là `True` ở lệnh ghi, `False` ở lệnh đọc; câu báo không chép `Location`.
  - `tran`: mã 200, 201, 204, 400, 401, 403, 404, 429, 500, 503 × thân gzip, deflate (zlib), deflate trần (mỗi loại 200 MB khi giải nén), thân thường 5 MB × lệnh đọc kế hoạch (trần 2 MB), lệnh xin mã (trần 64 KB): mọi ca ra `SheetsError`, bộ nhớ đỉnh < 16 MB.
  - `chunked`: thân `Transfer-Encoding: chunked` đi qua `http.client` thật (cặp socket nội bộ, không mạng). 200 gzip 200 MB: đỉnh 2,3 MB; 200 thường 5 MB: dừng ở 2 MB (đỉnh 5,1 MB gồm cả dữ liệu thử đã nạp sẵn); 500 gzip: 2,3 MB; xin mã 200 gzip: 0,4 MB; 302 chunked gzip kèm `Location`, xin mã 307 chunked: 0,2 MB, không đi theo.
- Script lượt 1 `probe_t097.py` chạy lại trên code lượt 2: **40.137 ca, 0 hỏng**. Ca đo LC-T097-1 (302 + `Location` + gzip 100 MB, ở lệnh đọc và lệnh xin mã): bộ nhớ đỉnh **0,0 MB** (lượt 1: 201 MB); 302 không `Location`: 0,0 MB.

### Việc 2: phần sửa SL-T097-1 → -4 không mở lỗ mới

- **SL-T097-1:** `_access_token` bắt thêm đúng `OverflowError`, `RecursionError` (`sheets.py:790-801`), không bắt `Exception`. Script lượt 1: 4 ca từng lọt nay ra câu cố định («SL-T097-1 còn lọt: []»).
- **Lỗi lạ không lộ khóa riêng, mã truy cập** (`probe_t097_l2.py loi`): 6 loại lỗi `requests` (`ConnectionError`, `ChunkedEncodingError`, `ContentDecodingError`, `InvalidHeader`, `ReadTimeout`, `SSLError`), lời lỗi gài thân lệnh xin mã (có JWT ký bằng khóa riêng), mã `Bearer` và một dòng của khối khóa PEM, ném ở lệnh xin mã và ở lệnh Sheets. `str`, `repr`, traceback, `marshall` của Streamlit: 0 lần có JWT, mã truy cập, dòng khóa (12/12). Phần `loi` của script lượt 1 (25 kiểu lỗi có mồi): vẫn 0 lọt.
- **SL-T097-3, đường `\\?\…`:** `_is_within` (`service_account.py:204-226`) so **danh tính thư mục** trước (`_inside_by_identity`, `:239-252`: đi ngược thư mục cha, so `(st_dev, st_ino)`, bỏ qua `st_ino == 0`), không khớp thì vẫn so chuỗi như lượt 1. Phép so mới **chỉ thêm** lý do từ chối, không làm đường nào trước bị từ chối nay được nhận: không mở đường lọt mới. Thử lại (script lượt 1 phần `duong`, `probe_t097_l2.py duong`): trong dự án, thư mục ảnh với đường thường, `\\?\`, `\\.\`, `\\?\Volume{…}`, `\\.\Volume{…}`, `\\?\GLOBALROOT\??\`, `\\localhost\C$`, tên 8.3: **đều từ chối**, câu không chép đường dẫn. File ngoài hai thư mục gõ ở mọi dạng đó: **đều nhận** (không chặn oan), trừ dạng có `..` đi ngang hai thư mục: SL-T097-5.
- **SL-T097-4:** thêm 5 tên thư mục đồng bộ, so sau NFC; `in_sync_folder` là cờ đúng/sai. Chỉ là Cảnh báo; `ServiceAccount.__repr__` vẫn không có đường dẫn, email.

### Việc 3: SL-T097-5 giữ Thấp

`_inside_by_identity` đi ngược thư mục cha theo **chữ** của đường gõ: `<dự án>\..\ngoai\k.json` có «cha» `<dự án>` nên bị từ chối «thư mục phần mềm». Tôi thử lại: `dự án\..\ngoai` và `anh\..\ngoai` bị từ chối nhầm; `ngoai\..\ngoai` nhận; `dự án\..\du-an\k` (thật trong dự án) bị từ chối đúng. Chỉ là chặn oan kèm câu sai lý do, hướng an toàn; phải tự gõ `..` đi ngang đúng thư mục dự án hay thư mục ảnh. **Thấp.** Sửa thử trên bản sao: đi ngược cha của `os.path.realpath(candidate)` thay vì của chữ gõ: 3/3 `xfail` SL-T097-5 thành XPASS, 685 ca khác của 4 file T-097 qua, mọi dạng đường thiết bị vẫn bị từ chối. Ghi nhận 1 lượt 2 của Soi Lỗi (ổ Google Drive G:, H:, I: trùng `st_dev`, `st_ino` nhỏ lặp lại) cũng chỉ làm **chặn oan** file khóa đặt trên Drive (vốn không nên); sửa cùng lúc bằng cách chỉ tin danh tính khi hai đường cùng gốc ổ (`anchor`) sau `realpath`.

### Việc 4: dấu `xfail` gỡ đúng R5

`git diff 24013b3..8b98996`: `tests/test_la_chan_t097.py` **chỉ xóa 16 dòng**, đều là dấu: 2 khối định nghĩa `_LC1`, `_SL3_MORE` (mỗi khối 6 dòng) và 4 dòng `@_LC1` (3), `@_SL3_MORE` (1); thân test không đổi. 11 ca của tôi (7 LC-T097-1, 4 SL-T097-3) nay chạy như ca thường và qua. `tests/test_soi_loi_t097.py`: chỉ xóa 25 dòng dấu (không dòng thêm ở `8b98996`); `16b9f64` chỉ thêm ca mới và xóa đúng 1 dòng docstring. `tests/test_google_service_account.py`: chỉ thêm ca. **Đạt.**

### Việc 5: thử gộp với `main` trên máy

`main` trên máy lúc 20:53 vẫn là `24013b3`, chính là gốc của lượt 2: gộp là tua thẳng, không xung đột; test trên nhánh chính là trạng thái sau gộp. 4 file T-097 (`test_google_sheets.py`, `test_google_service_account.py`, `test_soi_loi_t097.py`, `test_la_chan_t097.py`), 20:53–20:56: **685 passed, 3 skipped, 3 xfailed** (SL-T097-5), 0 hỏng. Lượt 2 chỉ sửa `seo_app/google/` (chưa nơi nào ngoài gói gọi tới); 81 file của Thợ Máy (6.952 passed) đã chạy rộng hơn. `ruff`: sạch. `detect-secrets` (`PYTHONUTF8=1`) trên 7 file lượt 2: 0. `bandit` `seo_app/google/`: đúng 3 báo nhầm như lượt 1 (B105 ở `service_account.py:45`, `:110`; B311 ở `sheets.py:822`).

### Điều kiện lượt 2

1. **SL-T097-5** (Thấp): phiếu dọn sau hay gom vào T-100 (Thợ Máy): so danh tính trên đường thật (`realpath`) thay vì chữ gõ; chỉ tin danh tính khi cùng gốc ổ (Ghi nhận 1 lượt 2 của Soi Lỗi); gỡ 3 dấu `xfail`. Nên xong trước khi T-101 hiện câu báo file khóa trên trang Cài đặt.
2. Điều kiện 3 → 5 của lượt 1 giữ nguyên (T-101, `config.py`, lượt thử thật). Điều kiện 1, 2 của lượt 1: **đã xong**.

**Kết luận lượt 2:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp còn mở (SL-T097-5). LC-T097-1, SL-T097-1 → -4 đóng. **Gộp `main` được ngay.**

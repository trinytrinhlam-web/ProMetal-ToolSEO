# Biên bản bảo mật T-121 · Client Google Search Console (chỉ đọc) · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 04/11 sau khi hạn mức Fable tuần mở lại, làm sau việc đọc lại T-112 lượt 3. Soi Lỗi chưa kiểm lại lượt 2 của Thợ Máy: biên bản này xác nhận thay việc SL-T121-1 đã đóng.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-121](../tickets/T-121-client-search-console.md): Thợ Máy lượt 1 `eb05747`, Soi Lỗi đầy đủ `482cdea` (ĐẠT CÓ ĐIỀU KIỆN, SL-T121-1 Thấp), Thợ Máy lượt 2 `b873a5d` |
| Phạm vi | **Đầy đủ** (đường gọi mới tới Google, phạm vi quyền): toàn bộ diff `a499a13..b873a5d`, 8 file đúng phạm vi phiếu (`seo_app/google/search_console.py` mới 1.034 dòng; `service_account.py`; `sheets.py` chỉ docstring; `tests/fake_google.py` chỉ thêm; `tests/test_google_search_console.py`, `tests/test_soi_loi_t121.py`; 2 báo cáo). Đọc cùng code phiếu dựa vào: lớp vận chuyển trong `sheets.py` (`_NoAuth` `:267`, `_Bearer` `:274`, `_refuse_redirect` `:298`, `_read_limited` `:309`, `_TokenRequest` `:353-391`, `_refresh_message` `:927`), `is_site_link` (`wordpress/client.py:2322-2348`), `_SITE_PATH` (`:2500`), `clean_text` (`plan/model.py:159-180`), `config.py` (`google_service_account_file`, `gsc_site_url`); thiết kế T-120 mục 1.2, 2.1–2.8, 5; biên bản Lá Chắn T-120 (LC-T120-1 → -8, -15 → -18). Không gọi Google thật, không đụng website, không chạy cloud |
| Ngày | 2026-11-04 13:18 → 13:32 (+07, giờ máy đo bằng `date`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4, `requests` 2.34.2, `google-auth` 2.62.0. Máy đang chạy nhiều agent: chỉ chạy test liên quan, không chạy toàn bộ |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. **SL-T121-1 (Thấp) đã đóng** ở lượt 2 (đọc diff, chạy test; xác nhận thay Soi Lỗi). 12 điều kiện LC-T120 của phiếu: **đủ cả**, mỗi điều kiện có test chứng minh (bảng «Danh sách kiểm tra»). Điều kiện của biên bản này đều dành cho phiếu sau (T-124, T-125, lượt thử thật), không chặn gộp |

## Tóm tắt (cho chủ dự án)

Phần đọc số liệu Google Search Console **an toàn để gộp**. Tôi đọc lại từ đầu, thử riêng, không dựa vào kết quả của Thợ Máy, Soi Lỗi:

- **Chỉ đọc, hai lớp.** Phần mềm chỉ xin Google quyền «đọc Search Console»; mã truy cập của phần Sheet và của phần Search Console tách riêng. Trong code không có chỗ nào mượn danh người khác hay xin quyền rộng hơn, và có test đọc thẳng mã nguồn để chặn ai thêm vào sau này. Phía Google, anh/chị chỉ cấp quyền «Hạn chế» cho tài khoản dịch vụ.
- **Chỉ hai lệnh đọc, kiểm trước khi gửi.** Lệnh nào không đúng y nguyên hai mẫu (địa chỉ, cách gọi, nội dung) thì không gửi. Tôi thử 11 nội dung sửa lệch và 5 địa chỉ sửa lệch: đều bị chặn.
- **Chỉ nhận đúng website.** Thuộc tính Search Console phải là của website trong `WORDPRESS_URL`; thuộc tính staging, tên miền na ná (`evilsuachuacuasat.com`), `http://`, viết hoa… đều bị từ chối, và dòng số liệu của website khác bị lọc hai lần (ở Google và trong máy).
- **Số liệu Google trả về được coi là dữ liệu lạ**: kiểm từng dòng, bỏ dòng sai, quá 10% dòng sai thì bỏ cả lần lấy. Lỗi Thấp Soi Lỗi tìm ra (dòng lặp bị cộng đôi) đã sửa đúng.
- **Câu báo lỗi là câu tiếng Việt cố định**, không chép lời Google, không chép từ khóa hay địa chỉ trang. Không thêm thư viện.
- **Việc của anh/chị lúc này:** không có. Khi tới lượt thử thật với Google (phiếu sau), Chỉ Huy sẽ xác nhận vài điểm chưa kiểm được bằng dữ liệu giả (mục «Điều kiện»).

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Phạm vi `webmasters.readonly` duy nhất; không `with_subject`, không `google.auth.default()` — **đạt** (LC-T120-1, -16)

- `service_account.py:49-51`: `SEARCH_CONSOLE_SCOPE`, `ALLOWED_SCOPES = (SHEETS_SCOPE, SEARCH_CONSOLE_SCOPE)`; `load_service_account` kiểm `type(scope) is str and scope in ALLOWED_SCOPES` **trước** mọi việc khác, kể cả trước khi đọc file (`:170-171`); `_credentials(info, scope)` kiểm lại rồi tạo đối tượng với `scopes=[scope]` (`:386-396`). Phạm vi chỉ là hằng trong module, không đường nào từ `.env`, `config/`, giao diện.
- `search_console.py:830-839` `_search_console_only`: đối tượng xác thực phải có **đúng** `[webmasters.readonly]` (danh sách bằng nhau, không phải «có chứa») và `_subject is None`; `__init__` (`:391-392`) từ chối tài khoản khác bằng câu cố định, trước khi tạo phiên.
- Tôi grep lại hai module: không `with_subject`, `with_scopes`, `.default(`, `print`, `logging`, `os.environ`, `subprocess`; `os.open` ở `service_account.py:303` là mở file khóa có từ T-097. Test cây cú pháp của Thợ Máy (`test_code_search_console_khong_mao_danh_khong_lenh_ghi`, `:251-282`) chặn thêm `AuthorizedSession`, `before_request`, `compute_engine`, chuỗi `/auth/webmasters` (đọc-ghi), địa chỉ `https://` nào khác gốc Search Console. Test của `test_google_service_account.py` quét mọi file `seo_app/google/*.py` nên quét cả module mới.
- Lệnh xin mã ký đúng phạm vi, không `sub` (Thợ Máy `test_lenh_xin_ma_ky_dung_pham_vi_search_console`); hai tài khoản từ cùng file khóa có hai mã riêng (Soi Lỗi `test_hai_tai_khoan_hai_ma_rieng`); có phạm vi chỉ đọc **kèm** phạm vi khác vẫn bị từ chối (Soi Lỗi `test_client_tu_choi_tai_khoan_co_them_pham_vi`, bắt đột biến M40).

### 2. `load_service_account` (hàm dùng chung với Sheets) — **đạt**

- 4 nơi gọi: `app/views/plan.py:336`, `app/views/settings.py:585`, `seo_app/google/sheets.py:632` không truyền `scope` (mặc định Sheets, không đổi gì); `search_console.py:446` truyền `SEARCH_CONSOLE_SCOPE`. `scope` là tham số chỉ-tên nên không lệch vị trí.
- Test ghim hành vi cũ (`test_google_service_account.py:79` `scopes == (SHEETS_SCOPE,)`, `test_google_sheets.py:324` JWT `scope == SHEETS_SCOPE`) vẫn qua trong lô test dưới. Thợ Máy đã chạy 19 file, Soi Lỗi 21 file mọi nơi gọi (mục Kiểm thử của hai báo cáo); tôi chạy lại 7 file Google chính trên `b873a5d`.

### 3. Đường gọi cố định, thân theo khuôn — **đạt** (LC-T120-2, -7)

- `_ROUTES` (`:124`) đúng hai lệnh `("sites", "GET")`, `("query", "POST")`. `_check_call` (`:636-646`) so **đúng phương thức, đúng địa chỉ nguyên văn, đúng thân**: `sites` phải không có thân; `query` phải trúng `self._query_url` và `_known_body`. `_send` (`:668-679`) gọi `_check_call` **trước** khi xin mã và trước khi gửi; Soi Lỗi khóa thứ tự này bằng cây cú pháp (`test_soi_loi_t121.py:843-867`: chỉ `_call` gọi `session.request`).
- `_known_body` (`:648-666`): JSON sắp khóa, `allow_nan=False`, so **bằng chuỗi** với thân dựng lại từ chính khuôn (`_body`, `:592-634`) cho 4 khuôn; vì so cả giá trị nên `true` ≠ `1`, `25000.0` ≠ `25000`, khóa thừa (`searchType`) hay thiếu (`dataState`) đều lệch. `startRow` phải là `int` đúng bội số và dưới trần (`:604-610`).
- `{siteUrl}` = `quote(site.site_url, safe="")` của thuộc tính đã `parse_property` **lại** từ chuỗi (`:399`, không tin đối tượng truyền vào); tên máy chỉ `[a-z0-9.-]` nên không có `/`, `..`, `@` nào lọt vào đường dẫn lệnh.
- Thử riêng (mục «Thử độc lập», phần E): 11 thân biến thể, 9 bị chặn; 2 gửi được là thân đúng và thân có `dimensions` dạng tuple (cùng nội dung, gửi đi y hệt, như Soi Lỗi đã ghi). 5 địa chỉ biến thể (thêm `/`, `post` chữ thường, `?x=1`, bỏ `www.`, `DELETE`): chặn cả.

### 4. Lọc thuộc tính theo từng phần tên miền, không lẫn staging — **đạt** (LC-T120-6, -17)

- `_DOMAIN` (`:128-130`): chữ thường ASCII, nhãn hợp lệ, ≥ 2 nhãn, nhãn cuối bắt đầu bằng chữ cái (không IP), ≤ 253 ký tự, không dấu chấm cuối, không cổng. `parse_property` (`:291-313`) chỉ nhận `sc-domain:<tên miền>` và `https://<tên máy>/`; `site_prefix` (`:316-347`) chỉ `https`, không tên/mật khẩu, cổng 443, không `?`/`#`, không khoảng trắng, ký tự lạ.
- `covers_site` (`:355-366`): tên miền thì `host == prop.host or host.endswith("." + prop.host)`; tiền tố thì `host == prop.host`. Không `endswith` trần.
- Hai lớp lọc dòng: bộ lọc gửi Google `^` + tiền tố đã thoát RE2 (`page_filter_expression`, `:350-352`); ở máy `_page` (`:787-798`) đòi `startswith(prefix)` **và** `is_site_link` (cùng tên máy, cùng cổng, `https`, không ký tự lạ) **và** mã hóa được UTF-8. Thuộc tính tên miền trả dòng staging thì dòng bị bỏ (Thợ Máy `test_thuoc_tinh_ten_mien_bo_dong_staging_ca_khi_google_tra`).
- Thử riêng phần C, D: 10 ca phủ website và 12 ca dạng thuộc tính đúng hướng cả (bảng mục «Thử độc lập»). Thợ Máy 33 + 17 ca; Soi Lỗi 7 ca phiếu nêu + 16 biến thể (chữ Kirin, `。`, `．`, `%2E`, `127.0.0.1`, `[::1]`, `a:b@`, tab, NUL): từ chối trước khi đọc file khóa.

### 5. Lớp vận chuyển nhập từ `sheets.py` được nối đúng — **đạt** (LC-T120-3, -18)

- Nhập 11 tên (`:62-74`), không chép; `search_console._TokenRequest is sheets._TokenRequest` (Thợ Máy). `_call` (`:708-751`) truyền đủ: `timeout=self.timeout` (ép ≤ 30 giây ở `:412`), `allow_redirects=False`, `stream=True`, `auth=_Bearer(token)` (có `auth` nên `requests` không đọc `.netrc`; `repr` che mã), `hooks={"response": [_refuse_redirect]}` (3xx đóng ngay, **không đọc thân**, `sheets.py:303-305`); phiên `max_redirects = 0` (`:411`); thân đọc qua `_read_limited` với `limit` do `_check_call` trả (256 KB cho `sites`, 8 MB cho `query`), `Content-Length` khai quá cỡ thì bỏ trước khi đọc. Lệnh xin mã qua `_TokenRequest(self._session, self.timeout)` (`:415`): chỉ `POST TOKEN_URI`, `_NoAuth`, ≤ 64 KB.
- Test từng lớp (không chỉ «có nhập»): Thợ Máy `test_moi_lenh_co_gio_cho_khong_theo_chuyen_huong_khong_doc_netrc`, `test_netrc_khong_duoc_doc`, `test_chuyen_huong_khong_di_theo_khong_doc_than`, `test_cau_tra_loi_query_qua_8_mb_bi_bo`, `test_gioi_han_co_theo_tung_lenh`, `test_repr_khong_lo_ma_truy_cap_email`; Soi Lỗi thêm 3xx ở lệnh `POST query` (5 mã, không gửi lại thân), `.netrc` thật có mật khẩu cho cả hai máy chủ, giờ chờ truyền đúng cả lệnh xin mã, biên 256 KB, `Content-Length` 1 TB. Docstring hai module ghi chéo (`sheets.py:34-39`).

### 6. Kiểm câu trả lời — **đạt** (LC-T120-5)

- `_parse_json` (`:982-992`): `parse_constant` chặn `NaN`/`Infinity`, `object_pairs_hook` chặn trùng khóa, bắt `RecursionError`, `UnicodeDecodeError`. `_answer` (`:1017-1034`): chỉ 200 và JSON object mới đi tiếp. `_raw_rows` (`:753-761`): `responseAggregationType` có thì phải `byPage`, `rows` ≤ `rowLimit`.
- Từng dòng: `_number` loại `bool` (`:844`), số nguyên ngoài ±2⁵³ coi như sai (Soi Lỗi: số 401 chữ số, `1e400` không làm sập); `_numbers` (`:860-875`): 0 ≤ click ≤ hiển thị ≤ 10⁹, hiển thị ≥ 1, 1 ≤ vị trí ≤ 10.000, `ctr` 0…1; ngày trong khoảng đã hỏi (`_iso_day`); trang qua `_page` (kể cả surrogate lẻ `"\ud800"`, `_utf8_ok`); từ khóa qua `clean_text` (bỏ Cc/Cf/Cs/Co/Cn, NFC) cắt 200 ký tự. Dòng lặp **nguyên văn** bị bỏ và đếm (`_fetch` `:556-567`, `check_hosts` `:510-524`); quá 10% dòng sai hay lặp thì bỏ cả lần lấy với câu riêng (`_check_share`, `:878-882`).
- Soi Lỗi: `NaN` một dòng giữa 20 dòng đúng ở 5 chỗ, `NaN` trong `metadata`, trùng khóa trong `metadata`, ngày lạ, địa chỉ dài nhờ `#…`: đúng hướng cả.

### 7. Câu lỗi cố định; không lệnh ghi — **đạt** (LC-T120-4, -7)

- 21 câu `_MSG_*` (`:141-207`) chỉ chèn `{code}` (số HTTP), `{count}`, `{timeout:g}`, `{kind}` (tên lớp lỗi của `requests`). Mã lý do của Google (`_reasons`, `:998-1014`) chỉ đọc khi là `[A-Za-z_]{1,64}`, tối đa 20 mục, chỉ để chọn câu, không bao giờ hiện. Không chỗ nào chép `siteUrl`, trang, từ khóa, lời Google; mọi `raise … from None`.
- Không lệnh ghi: `_ROUTES` chỉ `GET sites`, `POST query`; không `sites.add/delete`, `sitemaps.*`, URL Inspection; test cây cú pháp chặn chuỗi `PUT`/`DELETE`/`PATCH` và mọi địa chỉ ngoài gốc `webmasters/v3/`.

## Lỗi phát hiện

Không có lỗi mới. Các điểm còn lại của tôi đều là ghi nhận cho phiếu sau (mục «Ghi nhận»).

## Đánh giá lỗi và ghi nhận của Soi Lỗi

| Mục | Soi Lỗi | Lá Chắn |
|---|---|---|
| **SL-T121-1** · Thấp · dòng lặp nguyên văn bị cộng dồn | Trang sau lặp trang trước, hay số liệu `all` dịch giữa hai lệnh lật trang → click, lượt hiển thị gấp bội mà không báo | **Đồng ý mức Thấp** (số liệu sai, không phải lỗ hổng). **Đã đóng ở lượt 2 `b873a5d`**, tôi xác nhận thay Soi Lỗi: `_fetch` nhớ khóa thô (`keys` nguyên văn) qua mọi trang của một lần lấy (`:556-567`), `check_hosts` nhớ địa chỉ thô (`:510-524`); dòng lặp bị bỏ và đếm vào `dropped`; cả trang lặp là 100% dòng sai nên quy tắc 10% bỏ cả lần lấy, câu riêng `_MSG_ODD_ROWS`; `_merge` (`:927-951`) chỉ còn gộp dòng khác nhau ở `#…`. Hai ca Soi Lỗi gỡ `xfail` (`test_sl_t121_1_*`) qua trong lô test; 5 ca mới của Thợ Máy qua. Đổi test R5 (`test_tran_so_dong_thi_dung_va_bao_co_the_thieu`, `test_toi_da_so_lenh_moi_client`): chỉ đổi dữ liệu mỗi trang thành dòng riêng, giữ kỳ vọng chính; đúng cách Soi Lỗi đề nghị, không nới |
| GN-1 · lệnh xin mã tự thử lại 3 lần (google-auth) | Để lại, ghi T-124 | Đồng ý: hành vi của thư viện ở lớp dùng chung với Sheets (T-097), lệnh xin mã không phải lệnh Search Console; LC-T120-8 không trái. T-124 biết tổng chờ có thể thêm ~3 giây |
| GN-2 · 403 vì hạn mức | Thợ Máy sửa: `_QUOTA_REASONS` → câu «đợi 15 phút», không tự thử lại | Đồng ý; 403 không thử lại là đúng (chỉ 429 thử lại một lần) |
| GN-3 · cỡ câu trả lời Q1 khi website lớn; GN-4 · tỉ lệ 10% với lần gọi ít dòng | Lượt thử thật | Đồng ý; hỏng theo hướng an toàn. Ghi vào điều kiện lượt thử thật |
| GN-5 · «Tìm thuộc tính» giữ mục không đúng dạng (`usable=False`) | Để lại có chủ đích | Đồng ý, với điều kiện T-125 hiện `site_url` bằng chữ thuần (LC-T120-11, -19; docstring `SiteEntry` đã ghi) |
| GN-6 · «Kiểm tra» hiện tên máy trùng website | T-124/T-125 | Đồng ý |
| GN-7 · `_known_body` không bắt `RecursionError` | Thợ Máy sửa | Đồng ý; chỉ code app dựng thân, không có đường nhập ngoài |
| Đột biến sống M70, S6 | Chấp nhận | Đồng ý: M70 (mã lý do không lọc ASCII) tương đương vì chỉ so với tập cố định; S6 là phép kiểm phòng xa sau phép kiểm đầu hàm (S4 bị bắt) |

## Thử độc lập (Fable)

Script `probe_t121.py` (thư mục nháp của phiên, không commit): hàm thuần, không mạng; client giả với phiên **ném lỗi nếu bị gọi** (chỉ kiểm `_check_call`, không gửi gì).

| Phần | Ca | Kết quả |
|---|---|---|
| A `site_prefix` | 11 địa chỉ `WORDPRESS_URL` | Từ chối `%2e%2e`, `;x`, `%20`, dấu chấm cuối, `。`; nhận `:443`, `xn--…`, chữ hoa (thành chữ thường, giữ chữ hoa đường con). **Nhận `/..`, `/./`, `/blog/../`** → ghi nhận 1 |
| B `page_filter_expression` | 2 tiền tố | `^https://suachuacuasat\.com/`, `blog\.x~y-z/`: thoát đúng ký tự RE2 |
| C `covers_site` | 10 cặp (thuộc tính, website) | Phủ: tên miền ⊇ chính nó, ⊇ `blog.`; tiền tố ⊇ đường con. Không phủ: `cuasat.com`, `evilsuachuacuasat.com`, `….com.evil.com`, cổng 8443, `a:b@`, `www.` ≠ không `www.` (cả hai chiều) |
| D `parse_property` | 12 chuỗi | Từ chối NUL, xuống dòng, nhãn bắt đầu `-`, nhãn cuối toàn số, nhãn 64 ký tự, `/?`, `/#`, `//`; nhận nhãn 60 ký tự, `.c0m` (nhãn cuối bắt đầu bằng chữ), `xn--…` cả hai dạng |
| E `_check_call` thân | 11 thân | Chặn: `aggregationType` khác, thêm `searchType`, `rowLimit`/`startRow` số thực, `groupType` `or`, hai bộ lọc, biểu thức không thoát, ngày đảo, thiếu `dataState`. Gửi được: thân đúng; `dimensions` tuple cùng nội dung (gửi y hệt) |
| E `_check_call` đường | 5 địa chỉ/phương thức | Chặn cả: thêm `/` cuối, `post` chữ thường, `?x=1`, bỏ `www.`, `DELETE` |

Ngoài ra: grep hai module theo danh sách chuỗi nhạy cảm (mục 1); đọc diff lượt 2 (`482cdea..b873a5d`, 68 dòng code): chỉ thêm `seen`, `_utf8_ok`, `_QUOTA_REASONS`, `_MSG_ODD_ROWS`, bắt `RecursionError`; không nới phép kiểm nào.

## Danh sách kiểm tra (điều kiện LC-T120 của phiếu)

| Mã | Đạt | Bằng chứng (code `b873a5d`; test) |
|---|---|---|
| LC-T120-1 | ✔ | `ALLOWED_SCOPES`, kiểm trước khi đọc file (`service_account.py:170-171`, `:386-389`); Thợ Máy `test_pham_vi_la_bi_tu_choi_truoc_khi_doc_file` (13 ca), `test_mac_dinh_van_la_pham_vi_sheets`; Soi Lỗi `test_pham_vi_bien_the_bi_tu_choi_truoc_khi_doc_file` |
| LC-T120-2 | ✔ | `_check_call`, `_known_body` so đủ khóa, đủ giá trị (`:636-666`); Thợ Máy `test_than_sai_khuon_khong_gui` (40 ca), `test_lenh_ngoai_danh_sach_khong_gui` (18 ca), `test_than_gui_dung_nguyen_van_khuon`; Soi Lỗi 21 thân + 15 đường; probe E |
| LC-T120-3 | ✔ | Mục 5; `timeout` ≤ 30 (`:412`), `max_redirects = 0` (`:411`), `_call` (`:712-722`), giới hạn theo lệnh (`:642-645`) |
| LC-T120-4 | ✔ | Mục 7; Thợ Máy `test_loi_http_thanh_cau_co_dinh` (9 mã, lời Google mang từ khóa/địa chỉ/thuộc tính không lọt), `test_ma_ly_do_la_khong_doi_cau`; Soi Lỗi kiểm mọi câu không có lời Google, mã, email, tên miền, `__cause__` rỗng |
| LC-T120-5 | ✔ | Mục 6; `_parse_json` của chính module (không dựa `_answer` của Sheets); Thợ Máy `test_json_la_bi_bo_ca_cau_tra_loi` (12 ca), `test_dong_sai_bi_bo_va_dem` (36 ca); Soi Lỗi `NaN` giữa dòng đúng (bắt đột biến M44), số khổng lồ (M22) |
| LC-T120-6 | ✔ | `covers_site` lúc tạo client và trong `from_settings` **trước** khi đọc file khóa (`:400-401`, `:443-445`); dòng ngoài tiền tố bị bỏ cả khi Google trả (`_page`); Thợ Máy `test_from_settings_tu_choi_thuoc_tinh_truoc_khi_doc_file_khoa`, `test_thuoc_tinh_ten_mien_bo_dong_staging_ca_khi_google_tra` |
| LC-T120-7 | ✔ | `_ROUTES` (`:124`); test cây cú pháp (không `PUT`/`DELETE`/`PATCH`, không địa chỉ khác); Soi Lỗi `test_lenh_query_phuong_thuc_khac_khong_gui`, `test_lenh_sites_bien_the_khong_gui` |
| LC-T120-8 | ✔ | `MAX_REQUESTS = 20` không nâng được quá 20 (`:416-418`), đếm cả lần thử lại (`:672-674`); 429 thử lại đúng 1 lần (`QUERY_RETRIES = 1`), 5xx không thử lại (Soi Lỗi `test_5xx_khong_thu_lai`); trần `startRow` theo khuôn (`:604-610`, `:576-578`); không song song (một client, lệnh nối tiếp). Phần «chỉ một lần lấy chạy cùng lúc» (LC-T120-22) là của T-124 |
| LC-T120-15 | ✔ | Google giả `tests/fake_google.py` (chỉ thêm 2 hằng, 1 hàm); bộ chặn mạng vẫn bật (Thợ Máy `test_bo_chan_mang_chan_ca_client_khong_co_google_gia`); mọi ca biên 2.4 có test (mục 6); chưa có trang mới (T-125) |
| LC-T120-16 | ✔ | Mục 1: `_search_console_only` đúng một phạm vi, `_subject is None`; test cây cú pháp; JWT không `sub` |
| LC-T120-17 | ✔ | Mục 4: `_DOMAIN`, `parse_property`, `covers_site` theo từng phần tên miền; 7 ca phiếu nêu có trong `test_thuoc_tinh_sai_dang_bi_tu_choi` (33 ca) và `test_phu_website_theo_tung_phan_ten_mien` (17 ca); Soi Lỗi 23 ca; probe C, D |
| LC-T120-18 | ✔ | Mục 5: từng lớp có test riêng ở cả Thợ Máy lẫn Soi Lỗi; docstring chéo hai module |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 7 file trên `b873a5d`: `test_google_search_console`, `test_soi_loi_t121`, `test_google_service_account`, `test_google_sheets`, `test_soi_loi_t097`, `test_la_chan_t097`, `test_t100_google_identity` | **1.178 qua, 3 bỏ qua, 0 hỏng, 0 XPASS**, 5 phút 07 (13:23–13:28). 3 bỏ qua có từ trước (`test_google_service_account.py`: 2 ca symlink vì máy chưa bật Developer Mode, 1 ca quyền kiểu chmod) | ✔ |
| Probe (mục «Thử độc lập») | 51 ca, đúng hướng cả; 1 ghi nhận | ✔ |
| `ruff check` 6 file của phiếu; `ruff format --check` 3 file mới | sạch; đã đúng định dạng | ✔ |
| bandit `search_console.py`, `service_account.py` (`PYTHONUTF8=1`) | 3 Low, đều báo nhầm (mục dưới) | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 8 file của phiếu + biên bản này | 0 phát hiện | ✔ |
| D1 | `uv.lock`, `pyproject.toml` không đổi (`git diff a499a13..b873a5d`); không thêm thư viện; `.env.example`, `config/`, `app/**`, `seo_app/storage/**`, `seo_app/tracking/**` không đổi; diff đúng 8 file phiếu cho phép | ✔ |

## Báo nhầm đã loại

- bandit B311 `random.uniform` (`search_console.py:677`): chỉ cộng ngẫu nhiên 0–0,5 giây vào thời gian chờ thử lại 429, không dùng cho mật mã.
- bandit B105 ×2 (`service_account.py:52` địa chỉ `TOKEN_URI`, `:117` câu báo): chuỗi địa chỉ và câu tiếng Việt, không phải mật khẩu; có từ T-097.

## Ghi nhận (không xếp lỗi)

1. **`site_prefix` nhận đường con có dấu chấm** (`/..`, `/./`, `/blog/../`, probe A) qua `_PATH` (`:131`), trong khi client WordPress kiểm `WORDPRESS_URL` bằng `_SITE_PATH` không nhận dấu `.` (`client.py:2500`, SL-T042-10). Hậu quả chỉ là tiền tố lọc `^https://host/\.\./` không khớp trang nào (0 dòng, hướng an toàn); `.env` do chủ dự án ghi. Khi T-124 gom ba hàm chuẩn hóa `WORDPRESS_URL` (đề xuất của Thợ Máy), dùng **một** luật đường con cho cả WordPress lẫn Search Console.
2. `today_pacific(now)` với `now` không múi giờ sẽ coi là giờ máy, không báo; chỉ test truyền `now`. Không cần sửa.
3. Lệnh xin mã không tính vào trần 20 lệnh (GN-1): đúng với LC-T120-8 (trần cho lệnh Search Console).
4. `_merge` không kiểm lại trần 10⁹ sau khi cộng các dòng chỉ khác `#…`: số nguyên Python không tràn; cache SQLite (T-122) dùng INTEGER 64 bit vẫn đủ.
5. `SiteEntry.site_url`, `HostCheck.hosts`, `SearchRow.page`, `SearchRow.query` là chữ từ Google: T-124, T-125 hiện bằng chữ thuần (docstring đã ghi, LC-T120-11, -19).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp.

**B. Cho các phiếu sau** (không chặn T-121):

1. **T-124 (lấy số liệu, cache):** một client mỗi lần bấm (`from_settings`); khóa cấp module để chỉ một lần lấy chạy cùng lúc (LC-T120-22); bắt `SearchConsoleError` «Đã gửi đủ 20 lệnh» và giữ phần đã ghi; ngày theo `today_pacific()`; câu lỗi của client hiện qua `escape_markdown`; biết lệnh xin mã có thể chờ thêm ~3 giây (GN-1); «Kiểm tra» ghi «(địa chỉ http:// hoặc lạ)» khi tên máy trùng website (GN-6).
2. **T-124, gom ba hàm chuẩn hóa `WORDPRESS_URL`** (đề xuất Thợ Máy): giữ phép kiểm chặt ở cửa vào (`SearchConsoleClient.from_settings`), thống nhất luật đường con với `_SITE_PATH` (ghi nhận 1). Hàm dùng chung: chạy test mọi nơi gọi; Lá Chắn kiểm lại.
3. **T-125 (giao diện):** hiện `site_url`, tên máy, từ khóa, địa chỉ trang bằng chữ thuần, không `unsafe_allow_html` (LC-T120-11, -19); «Tìm thuộc tính» cảnh báo khi quyền cao hơn «Hạn chế»; thuộc tính không phủ website hay «Chưa xác minh» không chọn được (`SiteEntry.usable`).
4. **Lượt thử thật với Google** (T-126 hay buổi thử của Chỉ Huy, chủ dự án có mặt; không ghi gì lên Search Console): xác nhận (a) tài khoản dịch vụ quyền «Hạn chế» đọc được `sites` và `query`; (b) tên trường `metadata` (`first_incomplete_date` hay `firstIncompleteDate`); (c) mã lý do 403 khi chưa bật API và khi hết hạn mức (GN-2); (d) `dropped` của Q1 với địa chỉ thật của website (GN-4) và cỡ câu trả lời (GN-3). Lá Chắn đọc báo cáo thử trước khi bật trang Theo dõi.
5. **Sửa lớp vận chuyển** ở `sheets.py` hay `search_console.py`: chạy test của **cả hai** client (docstring đã ghi, LC-T120-18).

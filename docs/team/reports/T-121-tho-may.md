# Báo cáo T-121 · Client Google Search Console (chỉ đọc)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-121](../tickets/T-121-client-search-console.md) |
| Nhánh | `team/T-121` (từ `main` `a499a13`) |
| Ngày nộp | 2026-11-03 23:42 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã **đọc được Search Console**: liệt kê các website (thuộc tính) mà tài khoản dịch vụ được xem, và lấy số liệu Hiệu suất (lượt hiển thị, click, vị trí, từ khóa) bằng 4 kiểu lệnh cố định. Chưa có nút trên giao diện; các phiếu sau mới nối.
- **Chỉ đọc, hai lớp**: mã truy cập chỉ xin quyền «đọc Search Console», và quyền «Hạn chế» anh cấp trên Search Console. Phần mềm không có lệnh nào sửa gì trên Search Console.
- Dùng lại **file khóa Google** đang dùng cho Sheets, không thêm khóa. Phần Sheets và phần Search Console mỗi phần một mã truy cập riêng: mã của phần này không dùng được cho phần kia.
- Chỉ nhận thuộc tính **đúng website** trong `WORDPRESS_URL`. Thuộc tính staging, địa chỉ `http://`, tên miền na ná (ví dụ `evilsuachuacuasat.com`) đều bị từ chối. Số liệu ngoài website (staging, `www.`) bị lọc ngay ở Google và kiểm lại lần nữa trong máy.
- Số liệu Google trả về được **kiểm từng dòng**. Dòng lạ bị bỏ; quá 10% dòng lạ thì bỏ cả lần lấy. Từ khóa người lạ gõ được làm sạch (bỏ ký tự vô hình, ký tự đảo chiều chữ).
- Mỗi lần bấm gửi tối đa 20 lệnh. Google báo đang giới hạn thì thử lại đúng một lần, rồi báo «đợi 15 phút».
- Không thêm thư viện. Test không gọi Google thật.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/google/search_console.py` (mới) | Client chỉ đọc: `SearchConsoleClient` (`from_settings`, `list_sites`, `fetch_day_page`, `fetch_page_query`, `fetch_days`, `check_hosts`), 4 khuôn thân `SHAPES`, kiểm trước khi gửi (`_check_call`), kiểm câu trả lời từng dòng, câu lỗi cố định; hàm `parse_property`, `covers_site`, `site_prefix`, `page_filter_expression`, `today_pacific` |
| `seo_app/google/service_account.py` | Thêm `SEARCH_CONSOLE_SCOPE` (`webmasters.readonly`), `ALLOWED_SCOPES`, tham số `scope` của `load_service_account` (mặc định `SHEETS_SCOPE`, kiểm **trước** khi đọc file), `_credentials(info, scope)`; docstring |
| `seo_app/google/sheets.py` | **Chỉ docstring**: ghi chéo các phần lớp vận chuyển client Search Console dùng chung, sửa thì chạy test cả hai client (LC-T120-18) |
| `tests/fake_google.py` | Chỉ thêm: `SEARCH_CONSOLE`, `SC_SITES`, `search_console_requests()`; phần cũ không đổi |
| `tests/test_google_search_console.py` (mới) | 66 hàm test, 309 ca (mục Kiểm thử) |
| `docs/team/reports/T-121-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `seo_app/storage/**`, `seo_app/tracking/**`, `.env.example`, `config/**`, logic `sheets.py`, `pyproject.toml`, `uv.lock`.

## Cách dùng (cho T-124, T-125)

```python
client = SearchConsoleClient.from_settings(settings)            # mỗi lần bấm một client mới
client.list_sites()        # SitesResult(entries=(SiteEntry(site_url, permission, kind, covers, usable), …), skipped)
client.fetch_day_page(start, end)   # Q1: SearchResult(rows=(SearchRow(day, page, clicks, impressions, position), …),
                                    #     dropped, truncated, first_incomplete_date, metadata)
client.fetch_page_query(start, end) # Q2: SearchRow(page, query, …)
client.fetch_days(start, end)       # Q3 theo ngày: SearchRow(day, …)
client.check_hosts(start, end)      # Q3 theo trang: HostCheck(inside_impressions, outside_impressions, hosts, dropped, truncated)
SearchConsoleClient.from_settings(settings, with_property=False).list_sites()   # «Tìm thuộc tính» khi chưa chọn
```

| Điểm | Chi tiết |
|---|---|
| Ngày | `date` theo giờ Thái Bình Dương: `today_pacific()`. Khoảng ngày kiểm trước khi gửi: không ở tương lai, không cũ hơn 486 ngày (16 tháng), Q1 ≤ 31 ngày, Q2 ≤ 93 ngày, Q3 ≤ 28 ngày |
| Lỗi | `SearchConsoleError` (câu tiếng Việt cố định, hiện được ngay; có `status_code`), `ServiceAccountError` (file khóa) |
| Số lệnh | `client.request_count`; quá `MAX_REQUESTS = 20` lệnh Search Console (kể cả lần thử lại 429) thì `SearchConsoleError` «Đã gửi đủ 20 lệnh…»: T-124 giữ phần đã ghi, lần bấm sau lấy tiếp |
| `SearchRow` | `clicks`, `impressions` là số nguyên; `position` là số thực; `position_sum` = vị trí × lượt hiển thị (cộng dồn được). `page` là địa chỉ đã kiểm trên đúng website, đã bỏ `#…`, **chưa** chuẩn hóa (giải mã `%`, `/` cuối là việc của T-123). `query` đã qua `clean_text`, ≤ 200 ký tự |
| Số tạm | Chỉ Q1 (`dataState = all`): `first_incomplete_date` và `metadata` = `"ok"` / `"missing"` / `"bad"`. Đoạn cũ không có trường này là bình thường; đoạn mới nhất (kết thúc hôm nay theo giờ PT) mà `"missing"`/`"bad"` thì T-124 coi 3 ngày cuối là số tạm (thiết kế 2.4) |
| `truncated` | Đã lật tới trần số dòng của khuôn (Q1 200.000, Q2 50.000, Q3 200): có thể còn dòng chưa lấy, giao diện ghi «có thể thiếu dòng» |
| Hiện chữ | `SiteEntry.site_url`, `HostCheck.hosts`, `SearchRow.page`, `SearchRow.query` là chữ từ Google: nơi hiện phải hiện chữ thuần (LC-T120-11, -19) |

## Theo yêu cầu phiếu

| # | Yêu cầu | Làm ở |
|---|---|---|
| 1 | `SEARCH_CONSOLE_SCOPE`; `load_service_account` chỉ nhận 2 phạm vi cố định | `service_account.py`: `ALLOWED_SCOPES`, kiểm `type(scope) is str` và thuộc danh sách trước mọi việc khác; `_credentials` kiểm lại |
| 2 | `from_settings` kiểm mỗi lần; `list_sites`, `query` theo 3 khuôn; `_check_call` một chỗ; lật trang; 429 thử lại 1 lần; câu lỗi cố định | `SearchConsoleClient`. Thiết kế 2.3 có Q1, Q2, Q3; Q3 tách 2 khuôn (theo ngày có lọc, theo trang không lọc), nên `SHAPES` có 4 khuôn. Mỗi khuôn một hàm công khai, không có hàm `query(...)` nhận khuôn tự do |
| 3 | Kiểm từng dòng: `bool`, `NaN`/`Infinity`, trùng khóa, `RecursionError`, tỉ lệ dòng hỏng | `_parse_json` (`parse_constant`, `object_pairs_hook`), `_numbers`, `_row`, `_check_share` |
| 4 | Bộ đọc thuộc tính, kiểm phủ website theo từng phần tên miền, tiền tố lọc từ `WORDPRESS_URL`; từ chối `http://`, staging | `parse_property`, `covers_site`, `site_prefix`, `page_filter_expression` |
| 5 | Nhập lớp vận chuyển từ `sheets.py`, test chứng minh từng lớp được nối đúng | Nhập `_TokenRequest`, `_refuse_redirect`, `_read_limited`, `_Bearer`, `_Redirected`, `_TooLarge`, `_close_and_status`, `_refresh_message`, `_TOKEN`, `_MSG_AUTH`, `_MSG_AUTH_NETWORK`; mục LC-T120-18 bên dưới |
| 6 | Sửa hàm dùng chung: chạy mọi test Google, grep test theo hành vi | Mục Kiểm thử |
| 7 | Ca biên Soi Lỗi gợi ý (T-120) | `test_lat_trang_khi_du_25000_dong`, `test_ngay_dau_tien_con_so_tam`, `test_thuoc_tinh_ten_mien_bo_dong_staging_ca_khi_google_tra`, `test_ma_phan_tram_hoa_thuong_giu_nguyen_cho_loi_chuan_hoa`, `test_bo_phan_thang_va_cong_don`, `test_dong_sai_bi_bo_va_dem` (`bool`, `position` 0, click > hiển thị…), `test_kieu_cong_don_la_bo_ca_cau_tra_loi`, `test_json_la_bi_bo_ca_cau_tra_loi`, `test_hom_nay_theo_gio_thai_binh_duong` (ngày đổi giờ 08/03, 01/11) |

## Đối chiếu điều kiện Lá Chắn

| Mã | Cách làm | Test |
|---|---|---|
| LC-T120-1 | Phạm vi chỉ từ hằng `ALLOWED_SCOPES`; phạm vi khác, danh sách, chuỗi rỗng, `bytes`, `None` bị từ chối **trước khi đọc file**; client Sheets mặc định vẫn đúng `[spreadsheets]` | `test_pham_vi_la_bi_tu_choi_truoc_khi_doc_file` (13 ca), `test_mac_dinh_van_la_pham_vi_sheets`, `test_moi_client_mot_doi_tuong_xac_thuc_rieng` |
| LC-T120-2 | `_check_call`: đúng phương thức + địa chỉ + thân. Thân so **JSON đã sắp khóa** với thân dựng lại từ chính khuôn (đủ khóa, đủ giá trị, đúng kiểu; `true` ≠ `1`, `1.0` ≠ `1`); `{siteUrl}` đúng thuộc tính đã kiểm (mã hóa `%` chữ hoa); bộ lọc so nguyên văn | `test_than_sai_khuon_khong_gui` (40 ca: `searchType`, `type` khác `web`, `dataState` lạ, `byProperty`, `rowLimit`/`startRow` sai kiểu, bộ lọc khác…), `test_lenh_ngoai_danh_sach_khong_gui` (18 ca), `test_than_gui_dung_nguyen_van_khuon`, `test_than_dung_khuon_duoc_gui` (đối chứng) |
| LC-T120-3 | Chỉ `www.googleapis.com/webmasters/v3/` và máy chủ mã; giờ chờ ≤ 30 giây; `allow_redirects=False`, `max_redirects = 0`; ≤ 256 KB (`sites`), ≤ 8 MB (`query`) | `test_chi_goi_dung_hai_may_chu_google`, `test_gio_cho_toi_da_30_giay`, `test_gioi_han_co_theo_tung_lenh`, `test_cau_tra_loi_query_qua_8_mb_bi_bo` |
| LC-T120-4 | Câu cố định theo mã HTTP; mã lý do chỉ đọc khi là chữ `[A-Za-z_]` ≤ 64 ký tự, chỉ để chọn câu «chưa bật API» | `test_loi_http_thanh_cau_co_dinh` (9 mã; lời Google có từ khóa, địa chỉ trang, thuộc tính: không lọt), `test_403_api_chua_bat_co_cau_rieng`, `test_ma_ly_do_la_khong_doi_cau`, hàm `assert_fixed` dùng ở mọi ca lỗi |
| LC-T120-5 | `_parse_json` của module mới: `parse_constant` chặn `NaN`/`Infinity`, `object_pairs_hook` chặn trùng khóa, bắt `RecursionError`; số nguyên quá lớn coi như sai | `test_json_la_bi_bo_ca_cau_tra_loi` (12 ca), `test_dong_sai_bi_bo_va_dem` (36 ca), `test_qua_10_phan_tram_dong_sai_bo_ca_cau_tra_loi`, `test_dung_10_phan_tram_dong_sai_van_nhan` |
| LC-T120-6 | Thuộc tính phải phủ website (khi tạo client và trong `from_settings`, **trước** khi đọc file khóa); dòng ngoài tiền tố bị bỏ cả khi Google trả | `test_from_settings_tu_choi_thuoc_tinh_truoc_khi_doc_file_khoa`, `test_thuoc_tinh_ten_mien_bo_dong_staging_ca_khi_google_tra`, `test_client_kiem_lai_thuoc_tinh_truyen_vao` |
| LC-T120-7 | `_ROUTES` chỉ `("sites", "GET")`, `("query", "POST")`; không `sites.add/delete`, `sitemaps.*`, URL Inspection | `test_code_search_console_khong_mao_danh_khong_lenh_ghi` (đọc cây cú pháp: không chuỗi `PUT`/`DELETE`/`PATCH`, không địa chỉ nào khác gốc Search Console), `test_lenh_ngoai_danh_sach_khong_gui` |
| LC-T120-8 | ≤ 20 lệnh mỗi client (`MAX_REQUESTS`, không nâng được quá 20); 429 thử lại 1 lần; trần `startRow` theo khuôn. Một lần lấy chạy cùng lúc (LC-T120-22) là việc của T-124 | `test_toi_da_so_lenh_moi_client`, `test_429_thu_lai_dung_mot_lan_roi_thanh_cong`, `test_429_hai_lan_thi_bao_loi`, `test_tran_so_dong_thi_dung_va_bao_co_the_thieu` |
| LC-T120-15 | Test chỉ dùng Google giả; bộ chặn mạng chặn cả client không gắn Google giả; mọi ca biên 2.4 có test | `test_bo_chan_mang_chan_ca_client_khong_co_google_gia` và cả file |
| LC-T120-16 | Không `with_subject`, `with_scopes`, `google.auth.default`, `AuthorizedSession`; client từ chối tài khoản có phạm vi khác hoặc có `subject` | `test_tai_khoan_search_console_dung_mot_pham_vi_chi_doc` (`[webmasters.readonly]`, `_subject is None`), `test_client_tu_choi_tai_khoan_pham_vi_sheets`, `test_client_tu_choi_tai_khoan_uy_quyen_toan_mien`, `test_lenh_xin_ma_ky_dung_pham_vi_search_console` (JWT: `scope` đúng, không `sub`), `test_code_search_console_khong_mao_danh_khong_lenh_ghi` |
| LC-T120-17 | `sc-domain:` chỉ chữ thường ASCII/`xn--`, nhãn hợp lệ, ≥ 2 nhãn, nhãn cuối bắt đầu bằng chữ cái (không IP), không cổng, `@`, đường dẫn, dấu chấm cuối; tiền tố chỉ `https://<tên máy>/`. Phủ: tên máy **bằng** tên miền hoặc **kết thúc bằng «.» + tên miền** | `test_thuoc_tinh_sai_dang_bi_tu_choi` (33 ca, đủ 7 ca Lá Chắn nêu), `test_phu_website_theo_tung_phan_ten_mien` (17 ca, kể cả `https://evilsuachuacuasat.com` với `sc-domain:suachuacuasat.com` và `sc-domain:cuasat.com`: hai ca `endswith` trần sẽ cho qua) |
| LC-T120-18 | Từng lớp được nối và có test: 3xx bị từ chối, không đọc thân; thân quá cỡ bị bỏ; giờ chờ truyền đúng; `.netrc` không đọc; mã xin qua `_TokenRequest`; `repr` không lộ mã. Docstring hai module ghi chéo | `test_moi_lenh_co_gio_cho_khong_theo_chuyen_huong_khong_doc_netrc` (mọi lệnh kể cả lệnh xin mã: `timeout`, `allow_redirects`, `stream`, `auth`, móc `_refuse_redirect`; `_TokenRequest` là đúng lớp của `sheets.py`), `test_netrc_khong_duoc_doc` (vá `get_netrc_auth` ném lỗi nếu bị gọi), `test_chuyen_huong_khong_di_theo_khong_doc_than` (thân 3xx bẫy đếm lần đọc = 0), `test_cau_tra_loi_query_qua_8_mb_bi_bo`, `test_het_gio_thanh_cau_co_dinh`, `test_loi_xin_ma_thanh_cau_co_dinh`, `test_repr_khong_lo_ma_truy_cap_email` |

## Kiểm thử

Không chạy toàn bộ pytest (theo dặn dò; máy chạy 4 agent).

```
$ uv run pytest tests/test_google_search_console.py -q
309 passed in 24.36s

# Mọi file test chạm lớp Google: gọi load_service_account (kể cả qua SheetsClient.from_settings,
# app/views/plan.py, app/views/settings.py), dùng fake_google, hay đọc cây cú pháp seo_app/google
$ uv run pytest <19 file> -q -rfEsxX
1659 passed, 3 skipped in 400.66s (0:06:40)
   3 bỏ qua có từ trước: test_google_service_account.py:180 ×2 (máy chưa bật Developer Mode nên
   không tạo được symlink), :299 (Windows không dùng quyền kiểu chmod)

# Chạy lại 5 file Google chính trên bản cuối (sau khi sửa docstring), mã băm 5 file sửa không đổi
# trong lượt chạy
$ uv run pytest tests/test_google_search_console.py tests/test_google_service_account.py \
      tests/test_google_sheets.py tests/test_soi_loi_t097.py tests/test_la_chan_t097.py -q
997 passed, 3 skipped in 77.19s (0:01:17)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check <4 file mới/sửa phần lớn>
4 files already formatted

$ PYTHONUTF8=1 uvx detect-secrets scan <6 file của phiếu>      # uv 0.13.4
"results": {}
```

**19 file:** `test_google_search_console.py`, `test_google_service_account.py`, `test_google_sheets.py`, `test_la_chan_t097.py`, `test_la_chan_t100.py`, `test_la_chan_t113.py`, `test_plan_sync.py`, `test_soi_loi_t097.py`, `test_soi_loi_t100.py`, `test_soi_loi_t101.py`, `test_soi_loi_t109.py`, `test_soi_loi_t113.py`, `test_t100_google_identity.py`, `test_t101_home_page.py`, `test_t101_plan_page.py`, `test_t101_settings_google.py`, `test_t102_publish.py`, `test_t109_website_status.py`, `test_t113_website_status.py`.

**Grep test theo hành vi bị ghim** (sửa hàm dùng chung `load_service_account`):
- Phạm vi mặc định được ghim ở `test_google_service_account.py:79` (`scopes == (SHEETS_SCOPE,)`) và `test_google_sheets.py:324` (JWT `scope == SHEETS_SCOPE`). Cả hai vẫn qua, vì tham số `scope` mặc định là Sheets.
- Hai test đọc cây cú pháp: `test_google_service_account.py::test_code_khong_dung_tai_khoan_ngam_dinh_hay_uy_quyen` quét **mọi** file `seo_app/google/*.py`, nên quét cả module mới (không `default`, `print`, `logging`, không chuỗi «auth/drive», «cloud-platform»). `test_soi_loi_t097.py::test_code_google_khong_dung_tai_khoan_ngam_dinh_hay_lop_chuyen_cua_thu_vien` quét `service_account.py`, `sheets.py`. Cả hai đều qua; docstring mới cố ý không viết chữ «cloud-platform».
- Không test nào gọi `load_service_account` với đối số theo vị trí ngoài `path`, gọi `_credentials` trực tiếp, hay đọc chữ ký hàm.

**`ruff format`**: `seo_app/google/service_account.py:290-292` (`_in_sync_folder`) còn một chỗ `ruff format` muốn gộp dòng. Chỗ này có từ trước (bản `HEAD` cũng vậy), không thuộc phiếu nên để nguyên. Dòng mình sửa trong file đã đúng định dạng.

## Rủi ro và điểm cần chú ý

1. **Sự cố khi chạy test (đã xử lý trong lượt):** một tham số test ban đầu là chuỗi 200 KB, nên tên ca dài quá 32.767 ký tự. Trên Windows pytest không đặt được biến `PYTEST_CURRENT_TEST`, và câu báo lỗi của pytest **in cả `os.environ`**. Trong đó có giá trị biến `GEMINI_API_KEY` mà máy đang đặt sẵn trong biến môi trường (biến môi trường đè `.env`). Giá trị đó chỉ nằm trong kết quả lệnh của phiên này và file kết quả trên máy (thư mục `tool-results` của Claude Code trong `C:\Users\ADMIN\.claude\projects\…`). Nó **không** vào repo, báo cáo hay commit; tôi không chép lại ở đâu. Đã đặt `ids` ngắn cho tham số đó (`BAD_JSON`), các lần chạy sau sạch. Vì giá trị đã đi qua ngữ cảnh của mô hình, đề nghị Chỉ Huy báo chủ dự án quyết có đổi khóa Gemini không (`security.md` mục 7.1) và xóa file kết quả đó nếu muốn.
2. **Tên trường `metadata`** (tài liệu ghi `first_incomplete_date`): client nhận cả `first_incomplete_date` lẫn `firstIncompleteDate`. Lượt thử thật xác nhận tên thật. Sai thì T-124 coi 3 ngày cuối là tạm (hỏng theo hướng an toàn).
3. **Lớp vận chuyển dùng chung qua tên `_…` của `sheets.py`**: đây là ràng buộc ngầm, đã ghi chéo trong docstring hai module. Test `search_console._TokenRequest is sheets._TokenRequest` sẽ bắt nếu ai chép lớp ra.
4. `clean_text` nhập muộn từ `seo_app.plan.model` (kéo theo lớp AI, khoảng 2 giây lần đầu trong một tiến trình), chỉ khi lấy từ khóa. Nếu sau này `seo_app.plan` nhập `seo_app.google.search_console` ở đầu module thì vẫn không vòng, vì phần nhập nằm trong hàm.
5. `SiteEntry.covers` của «Tìm thuộc tính» tính theo `WORDPRESS_URL` hiện tại. Đổi `WORDPRESS_URL` thì thuộc tính cũ có thể thành «không phủ»: `from_settings` từ chối bằng câu cố định.
6. Một `ServiceAccount` dùng cho nhiều client thì các client dùng chung một đối tượng xác thực (và mã). `from_settings` luôn nạp file khóa mới, nên mỗi lần bấm có đối tượng riêng; chỉ test tạo nhiều client trên cùng một tài khoản.
7. Chưa xác minh với Google thật (đúng dặn dò): tài khoản dịch vụ làm người dùng quyền «Hạn chế», tên trường `metadata`, mã lý do `accessNotConfigured`/`SERVICE_DISABLED` khi chưa bật API. Cả ba đều hỏng theo hướng an toàn (không lấy được số, câu báo chung).

## Đề xuất

- **T-124:** dùng `today_pacific()`; một client mỗi lần bấm (`from_settings`); khóa cấp module để chỉ một lần lấy chạy cùng lúc (LC-T120-22); xử lý `SearchConsoleError` «đã gửi đủ 20 lệnh» (giữ phần đã ghi); quy tắc 3 ngày tạm khi `metadata` thiếu/sai ở đoạn mới nhất; `truncated` → «có thể thiếu dòng». Câu lỗi của client là câu cố định, hiện qua `escape_markdown`.
- **T-123:** `page_key` chuẩn hóa từ `SearchRow.page` (đã bỏ `#…`, chưa giải mã `%`).
- **Soi Lỗi:** thử thêm ca thân lệnh dựng tay với kiểu dữ liệu lạ. `Decimal` bị chặn (`json.dumps` khi so thân báo lỗi), lớp con của `int` ở `startRow` bị chặn (`type(...) is int` ở `_body`). Lớp con của `str` cùng nội dung thì được nhận, vì gửi đi y hệt thân đúng.

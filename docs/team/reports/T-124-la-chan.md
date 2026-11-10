# Biên bản bảo mật T-124 · Lấy số liệu Search Console, lưu thuộc tính, gom chuẩn hóa `WORDPRESS_URL` · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 05/11 13:20 sau khi Soi Lỗi đầy đủ nộp `37eb8a7`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-124](../tickets/T-124-lay-so-lieu-luu-thuoc-tinh.md): Thợ Máy mã `ac6a53a`, R5 `c8cbb5b`, báo cáo `03333cc`; Soi Lỗi đầy đủ `37eb8a7` (ĐẠT, 0 lỗi mới, 6 ghi nhận). Đầu nhánh **`37eb8a7`**, đã push |
| Phạm vi | **Đầy đủ** (ghi `.env`, đường gọi Google và WordPress, hàm dùng chung): toàn bộ diff `8caab2f..37eb8a7`, 14 file: `seo_app/tracking/refresh.py` (mới 768 dòng), `seo_app/env_file.py` (+69), `seo_app/wordpress/client.py` (+68: `site_path_ok`, `_canonical_origin`, `site_base`, `site_link`), `seo_app/google/search_console.py` (`site_prefix`), `seo_app/storage/search_cache.py` (LC-T122-1, -2, G1), `seo_app/tracking/match.py` (LC-T123-1), 4 file test mới (Thợ Máy 3, Soi Lỗi 1), 2 test cũ đổi theo R5, 2 báo cáo. Đọc cùng code không đổi mà phiếu dựa vào: `config.load_settings` (cách đọc biến môi trường), `env_file._write_value`, `SearchConsoleClient.from_settings`, `_site_entry`, `is_site_link`, `_is_plain_site_url`, `SearchCacheStore` (`load`, `save_days`, `clear`, `_is_healthy`), `SiteIndexStore.get`, `post_statuses`. Không gọi Google, website thật; không chạy cloud |
| Ngày | 2026-11-05 13:22 → 13:29 (+07, giờ máy đo bằng `date`); đã đọc trước mã từ 12:40 (nhánh tại `c8cbb5b`, mã không đổi tới `37eb8a7`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `f6a6e64`: `git merge-tree` không xung đột; từ gốc gộp `8caab2f` `main` không đụng file nào của phiếu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. 8 điều kiện LC-T120 của phiếu (-8, -10, -12, -13, -15, -21, -22, -23) **đạt phần T-124**; điều kiện của Lá Chắn T-121 (B.1, B.2), T-122 (LC-T122-1, -2, G1, G2, mục 8.3) và T-123 (LC-T123-1) **đã làm đúng**. Hàm chuẩn hóa dùng chung **không nới lọc**. Điều kiện của biên bản này đều dành cho T-125, T-126 và lượt thử thật (T-128), không chặn gộp |

## Tóm tắt (cho chủ dự án)

Phần lấy số liệu Google Search Console **an toàn để gộp**. Tôi đọc lại từ đầu và thử riêng, không dựa vào kết quả của Thợ Máy, Soi Lỗi:

- **Chỉ đọc, có trần.** Một cú bấm tạo một client mới, gửi tối đa 20 lệnh tới Google rồi dừng và giữ phần đã lấy; hai tab bấm cùng lúc thì tab sau được báo «đang lấy ở tab khác», không gửi gì. Không có lệnh ghi nào tới Google hay website; với WordPress chỉ hỏi danh sách bài và ngày đăng.
- **Lưu thuộc tính vào `.env` rất chặt.** Chỉ lưu được một thuộc tính vừa tìm thấy bằng nút «Tìm thuộc tính» trong cùng phiên, qua hai lớp kiểm, ghi thay đúng một dòng. Tôi thử 26 cách gõ lạ (xuống dòng, `=`, `#`, dấu nháy, dấu cách, chữ hoa, ký tự ẩn…): không cách nào chèn thêm được dòng vào `.env`. Máy có biến môi trường đè `.env` thì phần mềm báo đúng, kể cả khi biến rỗng.
- **Ba chỗ đọc địa chỉ website nay chung một luật**, và luật mới chỉ **chặt hơn** luật cũ (thư mục con có dấu chấm như `/..` nay bị từ chối ở cả phần WordPress lẫn Search Console). Soi Lỗi đã so hơn 600.000 cặp địa chỉ, tôi thử thêm 22 cách viết: không địa chỉ nào ngoài website lọt.
- **Không gọi mạng ngầm:** mở trang chỉ đọc bản lưu tạm; mọi lệnh gọi Google chỉ chạy khi bấm nút. Từ khóa người lạ gõ không đi vào lời dặn AI hay Google Sheets.
- **Ba lỗi nhỏ đợt trước đã sửa đúng**: bản lưu tạm bị sửa tay thì tự bỏ và tạo lại; lỗi quyền khi xóa bản lưu tạm ra câu tiếng Việt; link bài viết hoa tên miền vẫn nhận số liệu.
- **Việc của anh/chị lúc này:** không có. Vài điểm phải xác nhận với Google thật ở buổi thử (cách Google báo «số tạm»), tôi ghi ở mục «Điều kiện».

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Hàm chuẩn hóa `WORDPRESS_URL` dùng chung không nới lọc — **đạt**

- Một hàm ở `seo_app/wordpress/client.py`: `site_path_ok` (`:2357-2367`, luật đường con = `_SITE_PATH` không nhận «.» + từ cấm, đúng luật cửa vào WordPress SL-T042-10, LC-T042-5), `_canonical_origin` (`:2370-2385`: scheme, tên máy viết thường, bỏ cổng 443; đòi chuỗi gốc đúng `scheme://netloc`), `site_base` (`:2388-2398`), `site_link` (`:2401-2409`). Ba nơi gọi cũ nhập từ đây: `search_console.site_prefix` (`:316-348`: giữ phép kiểm chặt rồi trả `site_base(…) + "/"`), `search_cache.CacheScope.base` (`:186-188`), `match.page_key` (`:75-92`). Không còn bản riêng (Thợ Máy `test_khong_con_ban_chuan_hoa_rieng`; Soi Lỗi `test_three_filters_take_the_same_pages_and_only_on_site_pages`).
- **Không nới:** `site_path_ok` chặt hơn `_PATH` cũ của T-121 (bỏ «.», thêm từ cấm): ghi nhận 1 của Lá Chắn T-121 **đóng**. `site_base` giữ nguyên luật của T-122/T-123 (viết thường scheme, tên máy; bỏ `:443`; bỏ `/` cuối; đường dẫn giữ hoa thường), chỉ chặt hơn ở chuỗi có khoảng trắng (không chuẩn hóa nữa). Soi Lỗi so chéo 15.015 địa chỉ × 41 cách viết giữa cây `8caab2f` và cây T-124: 0 địa chỉ «mới nhận, cũ bỏ» ở cả cache, client, lõi; tôi đọc lại ba hàm và thử 22 cách viết (mục «Thử độc lập», A): `/..`, `/./`, `/blog/../x`, `/%2e%2e/`, `/b.log`, `//x`, `/wp-json`, `/WP-Admin/`, cổng 8443, tên/mật khẩu, `?`, `#`, dấu cách đầu, tab, `[::1]`, dấu chấm cuối, `http://` đều bị `site_prefix` từ chối; chữ hoa, `:443`, `/Blog/` chuẩn hóa đúng.
- **`site_link` (LC-T123-1)** chỉ chạy sau `is_site_link` (`match.py:167-170`): link có tên/mật khẩu hay tên máy khác không bao giờ tới `site_link` (probe A2; Soi Lỗi K3 thêm 2 ca sau khi thấy test Thợ Máy không bắt).

### 2. `GSC_SITE_URL`: chỉ mục vừa nhận từ `sites`, ghi nguyên tử, báo biến môi trường đè — **đạt** (LC-T120-12, -23)

- **Hai lớp** trước khi ghi: `save_property` (`refresh.py:747-768`) đòi `site_url` là **chuỗi** nằm trong `found.usable_site_urls` (`PropertyList` của «Tìm thuộc tính» cùng phiên; mục `usable` = đúng dạng, phủ website, quyền đã xác minh, do client T-121 xét), rồi `parse_property` (đúng dạng tên miền), rồi `set_gsc_site_url(value, offered=…)` (`env_file.py:453-468`): `validate_gsc_site_url` (`:440-450`, toàn chuỗi `sc-domain:[a-z0-9.-]{1,253}` hay `https://[a-z0-9.-]{1,253}/`, ≤ 300, không bỏ khoảng trắng) **và** phải nằm trong `offered` (chuỗi hay `bytes` làm `offered` bị từ chối). Không nhận chữ gõ tay.
- **Ghi:** `_write_value` dùng chung với mã Sheet, khóa AI (thay đúng dòng, giữ mọi dòng khác và CRLF, ghi nguyên tử, đọc lại). Probe C: file `A=1\r\nGSC_SITE_URL=old\r\n# chu thich\r\nB=2\r\n` sau ghi chỉ đổi dòng `GSC_SITE_URL`; 26 cách gõ lạ (xuống dòng, `\r`, `#`, `=`, nháy đơn, nháy kép, dấu cách đầu, `sc-domain:` rỗng, thiếu `/`, chữ hoa, `:443`, `@`, đường con, ký tự rộng 0, NUL, `bytes`, `None`, số) đều bị từ chối, câu báo không chép giá trị.
- **Biến môi trường đè:** `gsc_site_url_overridden` (`:476-484`) = `"GSC_SITE_URL" in environ`, đúng điều kiện của `load_settings` (`config.py:125`: biến **có mặt** là đè, kể cả rỗng; không `.strip()`). Probe D, F: rỗng → `overridden=True`; tên khác hoa thường trong `Mapping` thường → không đè (cả hai phía dùng `os.environ`, trên Windows cùng không phân biệt hoa thường).

### 3. Khóa cấp module, một client mỗi lần bấm, trần 20 lệnh — **đạt** (LC-T120-8, -22)

- `_FETCH_LOCK = threading.Lock()` (`refresh.py:122`); `refresh` (`:269-287`) `acquire(blocking=False)` → `BUSY` câu cố định, không dựng client; nhả trong `finally` cả khi lỗi lạ (Thợ Máy `test_khoa_nha_ca_khi_loi_bat_ngo`; probe E: sau lần hỏng vì lỗi client, lần sau không bị BUSY; giữ khóa ở luồng khác → BUSY). `refresh` không gọi `st.*` nên Streamlit không dừng được giữa chừng; hai luồng thật: một lần lấy (Thợ Máy `test_hai_tab_cung_bam_chi_mot_lan_lay`).
- Mỗi lần bấm `self.factory(self.settings)` = `SearchConsoleClient.from_settings` (`:262-263`, `:325`): kiểm lại thuộc tính, `WORDPRESS_URL`, file khóa (T-121). Trần 20 lệnh nằm ở client (`MAX_REQUESTS`, không nâng quá 20); hết trần → `SearchConsoleError` → `_Stop` → `PARTIAL`, giữ phần đã lưu (`test_het_tran_lenh_…`, `test_tran_20_lenh_cua_client_that`). Lần đầu 18 lệnh (16 đoạn + 2 kỳ từ khóa). Mốc «vừa lấy lúc …» lấy từ `cache.fetched_at` (dùng chung các tab), không từ `session_state` (`_is_recent`, `:601-611`).
- Vòng chia đoạn không lặp vô hạn ngay cả khi Google trả dữ liệu lạ: chốt `MSG_STUCK` khi đoạn không tiến (`:363-364`), ngoài trần lệnh của client. Soi Lỗi mô phỏng 4.800 lần bấm: ≤ 20 lệnh mọi lần.

### 4. Không gọi mạng ngầm — **đạt** (LC-T120-21 phần T-124)

- Nạp module chỉ tạo hằng và khóa (`test_nap_module_khong_goi_ham_nao_ngoai_hang_so`); không `st.cache_data`, `st.cache_resource`, `st.fragment` (module không nhập Streamlit). `refresh_hint` (`:614-631`) chỉ đọc cache. Mọi hàm gọi mạng (`refresh`, `check_connection`, `find_properties`) là hàm thường, T-125 chỉ gọi khi bấm (điều kiện B.1). Phần AppTest «mở trang và Cài đặt dưới bộ chặn mạng, giả client đếm lệnh = 0» là của T-125.

### 5. Chữ từ Google không vào lời dặn AI hay Sheet — **đạt** (LC-T120-13)

- `refresh.py` không nhập `seo_app.ai`, `seo_app.google.sheets`, `seo_app.plan`, `anthropic`, `openai`, `google.genai`, `streamlit`, `requests` (`test_module_khong_nhap_giao_dien_ai_sheets`); tôi grep lại: không `print`, `logging`, `open(`, `subprocess`, `os.environ`, `eval`, `exec`. Từ khóa chỉ đi Google → client (làm sạch, cắt 200) → cache. Câu trả về chỉ chèn số, ngày giờ do code định dạng; chữ Google (`SiteEntry.site_url`, `HostShare.host`) nằm ở trường riêng cho T-125 hiện chữ thuần.

## Lỗi phát hiện

Không có lỗi mới. Các điểm còn lại là ghi nhận (mục «Ghi nhận») và điều kiện cho phiếu sau.

## Đánh giá ghi nhận của Soi Lỗi và rủi ro Thợ Máy nêu

| Mục | Nội dung | Lá Chắn |
|---|---|---|
| Soi Lỗi GN-1 | Thiếu `metadata` mà độ trễ chốt số thật > 3 ngày thì số tạm bị ghi «đã chốt» mãi | Không phải lỗi bảo mật; đúng thiết kế 2.4. Rủi ro dữ liệu thật, phụ thuộc Google: **điều kiện B.3** (lượt thử thật ghi `metadata` thật; nếu có lúc thiếu thì lấy lại 7 ngày cuối mỗi lần bấm, vẫn 1 lệnh) |
| Soi Lỗi GN-2 | Đoạn ngắn + luật 10% dòng lạ của client T-121 → `FAILED` lặp lại | Luật của T-121 (dữ liệu chưa tin cậy), hỏng theo hướng an toàn, số đã lưu không hỏng; Google thật hầu như không trả dòng lạ. Giữ; xét lại sau thử thật (B.3) |
| Soi Lỗi GN-3 | «Kiểm tra», «Tìm thuộc tính» không giữ khóa của `refresh` | Đúng chữ LC-T120-22 (một lần **lấy số liệu**); hai nút này tối đa 3 lệnh, mỗi nút một client. Chấp nhận |
| Soi Lỗi GN-4 | Lỗi WordPress khi hỏi ngày đăng chỉ ghi chú, 10 phút sau mới hỏi lại | Chấp nhận (không mất số liệu Google) |
| Soi Lỗi GN-5 | LC-T120-12 dựa vào T-125 truyền đúng kết quả «Tìm thuộc tính» | Đồng ý: **điều kiện B.1** cho T-125; hai lớp kiểm vẫn chặn mọi chuỗi sai dạng kể cả khi `PropertyList` dựng tay (probe D) |
| Soi Lỗi GN-6 | Bài WordPress không trả ngày đăng bị hỏi lại mỗi lần, lô 1.000 | Chấp nhận (chỉ đọc, trong trần lô) |
| Thợ Máy: khóa chỉ trong một tiến trình | Hai cửa sổ app hai tiến trình vẫn lấy cùng lúc | Chấp nhận: cache tự chặn ghi xen (giao dịch, luật nối liền), nhiều nhất tốn gấp đôi lệnh; chạy app bằng `run.bat` là một tiến trình |
| Thợ Máy: nửa đêm giờ PT | `refresh` và client lệch «hôm nay» một ngày | Khoảng vẫn hợp lệ với client; lần sau lấy nốt. Chấp nhận |
| Thợ Máy: đổi luật đường con | `WORDPRESS_URL` có «.» hay từ cấm nay bị client Search Console từ chối | Đúng ý điều kiện B.2 của Lá Chắn T-121; client WordPress đã từ chối từ trước nên không đổi gì với người dùng |

## Thử độc lập (Fable)

Script `probe_t124.py` (thư mục nháp của phiên, không nằm trong repo): hàm thuần và file `.env` tạm; không mạng.

| Phần | Ca | Kết quả |
|---|---|---|
| A `site_path_ok`, `site_base`, `site_prefix`, `_is_plain_site_url` | 22 cách viết `WORDPRESS_URL` | Đúng hướng cả: `site_prefix` từ chối mọi đường con có «.», `//`, từ cấm, cổng khác 443, tên/mật khẩu, `?`, `#`, khoảng trắng, IPv6, dấu chấm cuối, `http://`; chuẩn hóa đúng chữ hoa, `:443`, giữ hoa thường đường con |
| A2 `site_link` | 4 link bài | Viết thường scheme, tên máy, bỏ `:443`, giữ đường dẫn; link có tên người dùng hay tên máy khác bị `is_site_link` chặn trước |
| B `validate_gsc_site_url` | 26 giá trị | 3 đúng dạng được nhận; 23 từ chối, câu báo không chép giá trị. Hai chuỗi chỉ đúng biểu thức (`sc-domain:a..b`, `sc-domain:-a.com`) bị `parse_property` chặn ở lớp trên (ghi nhận 1) |
| C `set_gsc_site_url` | 5 ca | Thay đúng một dòng, giữ CRLF và dòng khác; mục ngoài danh sách, danh sách là chuỗi, chèn dòng: từ chối; mục không phải chữ trong danh sách bị bỏ qua |
| D `save_property`, `gsc_site_url_overridden` | 9 ca | Mục không phủ website, chưa xác minh, giả mạo `usable` mà sai dạng, không có trong danh sách, kiểu sai, `found` sai kiểu: đều từ chối; mục dùng được: ghi đúng; biến môi trường rỗng: `overridden=True` |
| E `refresh` | 5 ca | Client hỏng ngay: `FAILED` câu cố định, 0 lệnh, cache trống; lần sau không `BUSY` (khóa đã nhả); khóa bị giữ: `BUSY`; giờ máy năm 1: `FAILED` + câu giờ máy |

## Danh sách kiểm tra (điều kiện của phiếu)

| Mã | Đạt | Bằng chứng (code `37eb8a7`; test) |
|---|---|---|
| LC-T120-8 | ✔ (phần T-124) | Mục 3; `test_tran_20_lenh_cua_client_that`, `test_het_tran_lenh_dung_giu_phan_da_luu_lan_sau_lay_tiep`, mô phỏng Soi Lỗi |
| LC-T120-10 | ✔ | `google_today` kiểm năm trước khi đổi múi giờ (`test_gio_may_khong_hop_le`, probe E); `_time_text` bắt `OverflowError`, `ValueError` (`:550-556`); cache kiểm năm cả sau đổi múi giờ (G1, `search_cache.py:1020-1025`); `refresh_hint` bắt `PeriodError`, `TypeError` |
| LC-T120-12 | ✔ | Mục 2; `test_chi_ghi_thuoc_tinh_trong_danh_sach_vua_tim`, `test_gia_tri_sai_bi_chan_truoc_khi_xet_danh_sach`, `test_luu_thuoc_tinh_*` (4), Soi Lỗi `test_forged_usable_entry_must_still_pass_parse_property`; probe B, C, D |
| LC-T120-13 | ✔ | Mục 5 |
| LC-T120-15 | ✔ | Test chạy dưới bộ chặn mạng, Google giả, WordPress giả; ca biên 2.4 phần T-124: `metadata` thiếu/sai/ngoài khoảng, trần dòng, dòng sai bị bỏ và đếm, surrogate lẻ (Soi Lỗi ghép client thật → cache) |
| LC-T120-21 | ✔ (phần T-124) | Mục 4; phần AppTest là của T-125 (B.1) |
| LC-T120-22 | ✔ | Mục 3; `test_khoa_dang_giu_tab_khac_bao_ban`, `test_hai_tab_cung_bam_chi_mot_lan_lay`, `test_khoa_nha_ca_khi_loi_bat_ngo`; mốc trong cache |
| LC-T120-23 | ✔ | Mục 2; `test_bao_bien_moi_truong_de_env`, `test_bien_moi_truong_rong_de_gia_tri_trong_env`, `test_luu_thuoc_tinh_bao_bien_moi_truong_de_env`; probe D |
| Lá Chắn T-121 B.1 | ✔ | Một client mỗi lần bấm; khóa; bắt «đã gửi đủ 20 lệnh» giữ phần đã ghi; `google_today` (cùng ngày PT với `today_pacific`); GN-6 (`HOST_SAME_SITE`). Phần `escape_markdown`, chờ ~3 giây lệnh xin mã: T-125 (B.1) |
| Lá Chắn T-121 B.2 | ✔ | Gom chuẩn hóa về `wordpress/client.py`, một luật đường con (`site_path_ok`), phép kiểm chặt vẫn ở cửa vào `from_settings`; bảng ca chung `test_mot_ham_cho_ca_ba_noi_goi_cu`, `test_mot_luat_duong_con_cho_wordpress_va_search_console`; ghi nhận 1 của T-121 đóng |
| Lá Chắn T-122 mục 8.1 (LC-T122-1, -2, G2) | ✔ | `_is_healthy`, `_prepare` đọc `sqlite_master` bằng `_decode_text`; chỉ bận, khóa, quyền, vào ra mới ném lại (`_KEEP_FILE_CODES`), còn lại coi là file lạ; `clear()` đưa `dir_has_link` vào `try` → `MSG_IO` câu cố định (`test_file_sua_tay_bi_bo_va_ghi_lai_duoc`, `test_file_dang_ban_van_bao_ban_khong_xoa`, `test_clear_loi_quyen_khi_kiem_lien_ket`, `test_clear_loi_xoa_file_cung_cau_co_dinh`); 4 ca ghim G2 (`test_ghim_*`) |
| Lá Chắn T-122 mục 8.3 | ✔ | `fetched_at` ở tương lai coi như cũ (`_is_recent`, `CLOCK_SKEW`; `test_moc_lay_o_tuong_lai_coi_nhu_cu`); gom `site_base`; đồng hồ lùi → `clear()` (`:327-330`; `test_dong_ho_chinh_lui_bo_cache_lay_lai`) |
| Lá Chắn T-123 LC-T123-1 | ✔ (phần T-124) | `site_link` sau `is_site_link` (`match.py:167-170`; `test_link_bai_viet_hoa_ten_may_van_nhan_so_lieu`, `test_link_hoa_cua_may_khac_van_bi_bo`, Soi Lỗi 2 ca LC-T123-1). Phần câu báo `skipped_items`: T-125 (B.1) |
| R5 | ✔ | `test_google_search_console.py`: ca nhận `b.log` chuyển sang danh sách từ chối (đúng luật chung), phép thoát «.» của RE2 kiểm riêng, thêm 7 địa chỉ bị từ chối; `test_tracking_model.py`: phép kiểm hàm thuần áp cho 7 file lõi, `refresh.py` là lớp nối nhưng vẫn cấm `open`, `eval`, `exec`, `compile`, `__import__`, thêm hai ràng buộc chặt hơn (gói không có file chưa xếp loại; lõi không nhập `refresh`). Không ca nào yếu đi; `git diff 8caab2f..37eb8a7 -- tests/` chỉ hai file cũ đổi |
| W2 | ✔ | Không lệnh ghi tới Google, WordPress; `.env` chỉ ghi `GSC_SITE_URL`; cache chỉ xóa file của chính app khi đồng hồ lùi (có `dir_has_link`) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 23 file liên quan trên `37eb8a7` (T-124 4 file; T-121, T-122, T-123; `.env`, script đặt mật khẩu, `config`; luật `WORDPRESS_URL` của client WordPress) | **1.843 qua, 5 bỏ qua, 0 hỏng, 0 XPASS**, 5 phút 02 (13:23–13:28). 5 bỏ qua có từ trước, theo hệ điều hành (symlink, chmod, `os.environb`) | ✔ |
| Probe (mục «Thử độc lập») | 71 ca, đúng hướng cả | ✔ |
| `ruff check` 10 file của phiếu; `ruff format --check` 5 file mới | sạch; đã đúng định dạng | ✔ |
| bandit 5 module đổi (`PYTHONUTF8=1`) | 6 Low, đều báo nhầm (mục dưới); khối hàm mới trong `client.py:2351-2410` không có `assert`, `eval`, `exec` | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 13 file của phiếu + biên bản này | 3 báo nhầm đã biết: `env_file.py:70` (tên biến `APP_PASSWORD_HASH`), `client.py:1023` (docstring ví dụ `tên:mật-khẩu@`), `T-124-tho-may.md:123` (nhắc ví dụ đó); biên bản này: 0 phát hiện (một dòng bảng này đổi chữ «set_password» thành «script đặt mật khẩu» để tránh báo nhầm) | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `.env.example`, `config/`, `app/` không đổi; không thêm thư viện | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `f6a6e64`) không xung đột; `git diff 8caab2f..main` không đụng file nào của phiếu | ✔ |

## Báo nhầm đã loại

- bandit B101 ×4 (`refresh.py:334`, `:355`, `:406`, `:488`): `assert` chỉ thu hẹp kiểu cho bộ kiểm tĩnh (`cache`, `client`, `site_index` đã được gán ở nhánh trên); chạy `python -O` bỏ chúng thì hành vi không đổi.
- bandit B105 (`env_file.py:70`, chuỗi `"APP_PASSWORD_HASH"` là tên biến) và B311 (`search_console.py:678`, chờ ngẫu nhiên 429): có từ T-104, T-121.
- detect-secrets 3 chỗ: tên biến và ví dụ trong docstring, báo cáo.

## Ghi nhận (không xếp lỗi)

1. `validate_gsc_site_url` chỉ kiểm bộ ký tự (`sc-domain:a..b`, `sc-domain:-a.com` qua biểu thức), nghĩa tên miền do `parse_property` kiểm ở `save_property`. Đường duy nhất tới `set_gsc_site_url` là `save_property` (và `offered` chỉ gồm mục client T-121 đã kiểm), nên đủ; ai gọi thẳng `set_gsc_site_url` sau này phải gọi `parse_property` trước (docstring nên ghi; việc nhỏ cho phiếu dọn).
2. Cửa vào client WordPress (`_is_plain_site_url`) chặt hơn `site_prefix` ở **tên máy** (không nhận chữ hoa, `:443`, `/` cuối), không phải ở đường con; `load_settings` bỏ `/` cuối. Cả hai cùng từ chối mọi địa chỉ ngoài website; khác biệt chỉ ở cách viết của chủ dự án, như SL-T122-1 đã xét.
3. `site_base` không bỏ khoảng trắng đầu/giữa (chặt hơn bản cũ); `load_settings` đã bỏ khoảng trắng hai đầu, hai cửa vào đều từ chối khoảng trắng.
4. «Kiểm tra», «Tìm thuộc tính» không giữ khóa `_FETCH_LOCK` (Soi Lỗi GN-3): đúng chữ LC-T120-22, tối đa 3 lệnh.
5. Khóa chỉ trong một tiến trình app; cache tự chặn ghi xen nhau.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp.

**B. Cho các phiếu sau** (không chặn T-124):

1. **T-125 (giao diện), Lá Chắn kiểm khi nộp:** (a) `find_properties(...)` giữ trong `session_state`, chỉ cho chọn `found.usable_site_urls` và truyền **đúng đối tượng đó** vào `save_property`; không dựng `PropertyList` từ chữ người dùng (LC-T120-12, Soi Lỗi GN-5); (b) `SaveResult.overridden` → cảnh báo biến môi trường đè (LC-T120-23); (c) mở trang và Cài đặt **không gọi mạng** (AppTest dưới bộ chặn mạng, giả client đếm lệnh = 0; LC-T120-21), nút «Lấy số liệu mới», «Kiểm tra», «Tìm thuộc tính» chỉ gọi khi bấm, không `st.cache_data`/`st.cache_resource` quanh lệnh mạng, không `st.fragment(run_every=…)`; (d) mọi câu `report.message`, `report.notes`, `check.messages`, `PropertyList.message`, `SaveResult.message` qua `escape_markdown`; `SiteEntry.site_url`, `HostShare.host`, từ khóa, địa chỉ trang hiện chữ thuần, không link (LC-T120-11, -19); (e) nút «Xóa bản lưu tạm» gọi `store.clear()` khi `MSG_OPEN`/`MSG_BROKEN` lặp (Lá Chắn T-122 mục 8.2); (f) LC-T123-1 phần còn lại: câu cố định khi `skipped_items > 0`; (g) biết lệnh xin mã có thể chờ thêm ~3 giây (GN-1 T-121) khi hiện trạng thái chờ.
2. **T-126 (README):** lần đầu lấy khoảng một phút, 18 lệnh; bấm lại trong 10 phút không có gì mới; nghĩa «số tạm»; thuộc tính chỉ chọn từ «Tìm thuộc tính»; biến môi trường `GSC_SITE_URL` đè `.env`.
3. **Lượt thử thật với Google (T-128):** ghi lại `metadata` thật của đoạn mới nhất và một đoạn cũ (Soi Lỗi GN-1, Thợ Máy rủi ro 1); `dropped` của Q1 và Q2 với website thật (GN-2, luật 10%); quyền «Hạn chế» của tài khoản dịch vụ; số lệnh của lần bấm đầu (≤ 20). Nếu Google có lúc thiếu `metadata` ở đoạn mới nhất thì mở phiếu nhỏ: mỗi lần bấm lấy lại 7 ngày cuối (vẫn 1 lệnh), và xét nới luật 10% chỉ khi lần gọi có từ 20 dòng trở lên (sửa ở client T-121, Lá Chắn kiểm lại).
4. **Phiếu dọn (Thấp, ngoài phạm vi):** `plan_cache._is_healthy` cùng mẫu LC-T122-1 (Lá Chắn T-122 mục 8.4); docstring `set_gsc_site_url` ghi «gọi sau `parse_property`» (ghi nhận 1).

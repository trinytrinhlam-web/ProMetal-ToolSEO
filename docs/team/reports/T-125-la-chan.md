# Biên bản bảo mật T-125 · Trang «📈 Theo dõi» và mục Search Console trong Cài đặt · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 07/11 09:17 sau lượt 2 của Thợ Máy. Soi Lỗi chưa kiểm lại lượt 2: biên bản này xác nhận thay việc SL-T125-1, SL-T125-2 đã đóng. Hạn mức Fable tuần đã dùng 79%: tập trung vào trọng tâm Chỉ Huy giao, không lan rộng.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-125](../tickets/T-125-trang-theo-doi.md): Họa Sĩ `2cc720b` (gộp `main` `8a09fcb`, báo cáo `216ff2f`), Soi Lỗi đầy đủ `1c55e9e` (ĐẠT CÓ ĐIỀU KIỆN, SL-T125-1, -2 Thấp), Thợ Máy lượt 2 `93d9f78` (báo cáo `df46f70`). Đầu nhánh **`df46f70`**, đã push |
| Phạm vi | **Đầy đủ**: diff `682f62c..df46f70` phần của phiếu: `app/views/tracking.py` (mới 960 dòng), `app/views/settings.py` (+189, mục Search Console), `app/main.py` (`PAGES`), `seo_app/storage/search_cache.py` (+36: `stamp()`), `seo_app/tracking/refresh.py` (+29: `clear_cache`, `ClearResult`), 4 file test mới (Họa Sĩ 2, Soi Lỗi 1, Thợ Máy 1). Phần còn lại của diff là `main` gộp vào nhánh (T-092, T-128, T-129, T-130…), đã qua Lá Chắn riêng. Đọc cùng code không đổi mà trang dựa vào: `refresh`, `find_properties`, `check_connection`, `save_property` (T-124), `safe_text`, `visible` (Cài đặt), `page_label`, `page_key` (T-123), `escape_markdown`. Không gọi Google, website thật; không chạy cloud |
| Ngày | 2026-11-07 09:19 → 09:30 (+07, giờ máy đo bằng `date`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; không vòng chờ dài |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `31d8cec`: `git merge-tree` không xung đột; ba file dùng chung với `main` chỉ khác đúng phần lượt 2): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. 8 điều kiện LC-T120 của phiếu (-11, -13, -14, -15, -19, -20, -21, -23) **đạt**; điều kiện 1 của Lá Chắn T-124, phần T-125 của T-121 và LC-T123-1 **đã làm đúng**. **SL-T125-1, SL-T125-2 đã đóng** ở lượt 2 (đọc mã, thử riêng, test); bản giữ theo dấu file **không làm hổng** LC-T120-9 và không vi phạm LC-T120-21. Điều kiện chỉ dành cho T-127, lượt thử thật và máy Mac, không chặn gộp |

## Tóm tắt (cho chủ dự án)

Trang «📈 Theo dõi» và mục Search Console trong Cài đặt **an toàn để gộp**. Tôi đọc lại từ đầu và thử riêng, không dựa vào kết quả của Họa Sĩ, Soi Lỗi, Thợ Máy:

- **Mở trang, mở Cài đặt không hỏi Google.** Mọi lệnh tới Google chỉ chạy khi bấm ba nút «Lấy số liệu mới», «Tìm thuộc tính», «Kiểm tra»; mỗi lần bấm một client mới, chung khóa «một lần lấy mỗi lúc» của T-124.
- **Chữ từ Google và từ website chỉ hiện như chữ thường**: từ khóa, đường dẫn, tên bài không bao giờ thành link hay HTML; tải bảng ra CSV mở bằng Excel cũng không thành công thức. Tôi thử đường dẫn giấu ký tự đảo hướng chữ, giấu link dạng `%`: đều bị làm sạch hay bị bỏ.
- **Biểu đồ dựng từ khuôn cố định trong code**, chỉ có số và ngày; tên bài đặt ngoài biểu đồ.
- **Lưu thuộc tính** chỉ nhận đúng thuộc tính vừa tìm thấy trong phiên; máy có biến môi trường đè `.env` thì báo; tài khoản dịch vụ được cấp quyền cao hơn «Hạn chế» thì nhắc hạ.
- **Hai lỗi nhỏ Soi Lỗi tìm ra đã sửa đúng:** trang không đọc lại toàn bộ bản lưu tạm ở mỗi cú bấm (chỉ đọc lại khi file đổi, và khi đọc thì kiểm đủ như trước), «Xóa bản lưu tạm» không xóa khi tab khác đang lấy số liệu.
- **Việc của anh/chị lúc này:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Mở trang và Cài đặt không gọi mạng — **đạt** (LC-T120-14, -21)

- `render()` (`tracking.py:899-957`): `load_settings`, `setup_problem`, nút «Lấy số liệu mới» (gọi `fetch_now` chỉ trong `if action.button(...)`, `:905-913`), `load_cache` (chỉ `exists`, `stamp`, `store.load`: đọc file), `cached_items`, `cached_plan_rows` (đọc file, không mở kho khi chưa có file), `refresh_hint` (không mạng), bảng, biểu đồ. Client WordPress chỉ dựng trong `fetch_now` (`:446`). Không `st.cache_data`, `st.cache_resource`, `st.fragment`, `run_every` (grep trang chỉ thấy hai dòng docstring; Họa Sĩ có ca đọc cây mã).
- Cài đặt (`settings.py:851-884`): `gsc_current_text` kiểm dạng và phủ website **trên máy** (`parse_property`, `covers_site`); `gsc_site_url_overridden()` đọc biến môi trường; «Tìm thuộc tính», «Kiểm tra» chỉ trong `if find.button(...)` / `if check.button(...)`.
- Test: Họa Sĩ `test_mo_trang_va_doi_moi_o_khong_goi_mang`, `test_mo_cai_dat_khong_goi_mang`, `test_chua_co_file_thi_mo_trang_khong_tao_file` dưới bộ chặn mạng với client giả đếm lệnh, kèm 2 ca đối chứng bấm nút thì bộ đếm lên; Soi Lỗi thêm đổi ô, chạy lại nhiều lần: mỗi hàm mạng đúng 1 lần. Đăng nhập: trang chạy qua `main.py` (`test_chua_dang_nhap_thi_khong_mo_duoc_trang`).

### 2. Chữ Google, WordPress hiện chữ thuần — **đạt** (LC-T120-11, -19; Lá Chắn T-123 mục 7, T-124 B.1 d)

- **Ba lớp, đúng thứ tự:** (1) chữ đã được làm sạch ở nguồn: từ khóa qua `clean_text` của client T-121, đường dẫn «Trang khác» qua `page_label` (giải mã `%` rồi `clean_text`, cắt 120 ký tự, T-123), tiêu đề bài qua `_clean_text` của client WordPress, thuộc tính và tên máy ASCII in được (T-121); (2) bảng chỉ qua `st.dataframe(safe_rows(…))` (`tracking.py:265-276`, `:791`, `:803`, `:892`, `:956`; Cài đặt dùng `plan_sync.safe_text(visible(…))`, `settings.py:793`, `:840`): ô bảng là chữ thuần, dấu `=`, `+`, `-`, `@`, tab, CR đầu ô được thêm dấu cách (CSV tải về không thành công thức, LC-T101-1); (3) chữ đưa vào Markdown đi qua `plain` = `escape_markdown` (`:254-256`): tên bài `:830`, nhãn và lý do `:832-834`, câu «Cần chú ý» `:880`, câu của lõi `:456-458`, `:493`, `:917`, `:922`. Ô chọn (`selectbox`) hiện chữ thuần. Không `unsafe_allow_html`, không `LinkColumn`, không `markdown_link`, không `st.link_button` với chữ ngoài (grep).
- **Thử riêng** (probe A, B): `/?s=[x](https://evil.example)` và dạng `%5Bx%5D%28…%29` giải mã thành chữ `[x](…)`, chỉ nằm trong ô bảng; `%E2%80%AE` (ký tự đảo hướng) bị `clean_text` bỏ; `<b>x</b>` bị `page_key` từ chối từ đầu (`is_site_link`); `=HYPERLINK("x")` giữ nguyên chữ, `safe_text` thêm dấu cách đầu; đường dẫn 500 ký tự cắt còn 120. `escape_markdown` thoát `[`, `(`, `*`, `<` và chèn ký tự rộng 0 vào `://` nên không thành link. Ghi nhận 1: `escape_markdown` **không** bỏ ký tự đảo hướng (`‮` đi qua nguyên), nên lớp (1) ở nguồn là bắt buộc; trang không có chỗ nào đưa chữ Google chưa qua lớp (1) vào `plain`.
- Soi Lỗi đã quét **mọi** chữ Markdown trên trang với từ khóa `**đậm** [x](…)`, tiêu đề bài có `<b>` và link: không còn link hay chữ đậm chưa thoát.

### 3. Biểu đồ dựng từ khuôn cố định, chỉ số và ngày — **đạt** (LC-T120-20)

`CLICK_CHART`, `POSITION_CHART` là hằng (`:217-237`), chỉ chữ của code (`field`, `type`, `title`, `scale`, `tooltip`), không `expr`, không kênh `href`, không nguồn `url`; dữ liệu `chart_data` (`:720-729`) chỉ `tuan` (`dd/mm/yyyy` do code viết), `click` (số nguyên), `vi_tri` (số hay rỗng). Tên bài nằm ngoài biểu đồ qua `plain` (`:830`). Họa Sĩ `test_bieu_do_khuon_co_dinh_chi_ngay_va_so`.

### 4. «Tìm thuộc tính» truyền đúng đối tượng trong `session_state` vào `save_property` — **đạt** (LC-T120-12; Lá Chắn T-124 B.1 a; Soi Lỗi T-124 GN-5)

`S["gsc-found"]` chỉ được gán bằng kết quả `find_properties(settings)` lúc bấm (`settings.py:871`); `_save_property` (`:764-776`) lấy đúng đối tượng đó, kiểm `isinstance(found, PropertyList)`, truyền nguyên vào `save_property(S.get("gsc-choice"), found)`; ô chọn chỉ có `found.usable_site_urls` (`:804-818`). Không dựng `PropertyList` từ chữ trên trang. Họa Sĩ `test_luu_truyen_dung_doi_tuong_tim_thay_vao_save_property` (so `is`), Soi Lỗi so `is` sau khi đổi ô và chạy lại; `test_chua_tim_ma_bam_luu_thi_khong_ghi`.

### 5. Bản giữ theo dấu file (lượt 2, SL-T125-1) không làm hổng LC-T120-9, không vi phạm LC-T120-21 — **đạt**

- `SearchCacheStore.stamp()` (`search_cache.py:466-496`): `lstat` (không theo liên kết; không phải file thường thì `None`), đọc **100 byte đầu** (số đếm thay đổi SQLite ở byte 24–27), cỡ, giờ sửa nano giây, mã file, ổ đĩa, cỡ và giờ sửa file `-wal`. Không mở SQLite, không ghi.
- `load_cache` (`tracking.py:334-362`): khóa giữ = (dấu **lấy trước khi đọc**, phạm vi, múi giờ); dấu khác hay `None` thì `store.load(scope)` **kiểm đủ như T-122** (LC-T120-9); lỗi đọc thì không giữ; file mất thì bỏ bản giữ. Bản giữ nằm trong `st.session_state` của tab (không `st.cache_*`, không có hạn giờ, không dùng chung tab): LC-T120-21 giữ nguyên. `tracking_for` (`:364-381`) chỉ dùng lại `build_tracking` khi cùng bản giữ **và** cùng địa chỉ website, danh sách bài, dòng kế hoạch.
- **Đọc theo góc bảo mật:** mọi dữ liệu lên trang đều đã qua `load` (kiểm cấu trúc, từng dòng, mã băm phạm vi). File bị thay mà dấu đổi → đọc và kiểm lại; file bị thay mà **dấu không đổi** (phải cùng mã file, cỡ, giờ sửa, số đếm thay đổi, `-wal`) → trang hiện bản **cũ đã kiểm**, không hiện gì từ file mới: hướng an toàn (chỉ «cũ», không «chưa kiểm»). Probe C: ghi đè cùng cỡ, giả giờ sửa trùng, số đếm thay đổi vẫn khác → dấu khác. Thợ Máy 7 ca `test_stamp_*`, `test_page_shows_new_data_after_the_cache_file_changes`, `test_file_written_during_reading_is_read_again`, `test_changed_property_reads_the_file_again`; đột biến M01–M06, M08, M09 bị bắt.
- Ghi nhận 2: giữa `lstat` và `open` 100 byte có khe rất nhỏ; đổi đường dẫn thành liên kết đúng lúc đó thì `open` đọc 100 byte đầu của file đích vào dấu (không hiện, không lưu), lần đọc thật vẫn qua `load` có `dir_has_link`. Vô hại. Ca liên kết (`test_stamp_of_a_folder_or_link_is_none`) bỏ qua trên máy này (Windows chưa bật Developer Mode; probe C cũng không tạo được symlink): điều kiện B.3 cho máy Mac.

### 6. Xóa trong khóa (SL-T125-2) — **đạt**

`refresh.clear_cache` (`refresh.py:301-315`): `_FETCH_LOCK.acquire(blocking=False)` → khóa đang giữ thì `ClearResult(False, MSG_BUSY, busy=True)`, không xóa gì; xóa trong `try`, lỗi cache ra câu cố định, khóa nhả ở `finally`. Trang `_clear_cache` (`tracking.py:473-494`) chỉ gọi hàm này sau khi hỏi lại («Xóa» / «Thôi»), bị từ chối thì ô vàng, giữ số liệu; xóa xong thì lần chạy sau bỏ bản giữ (file mất). Soi Lỗi `test_sl_t125_2_clearing_is_refused_while_another_tab_fetches` (gỡ `xfail`), Thợ Máy 5 ca `test_clear_cache_*`, M07 bị bắt.

### 7. Cảnh báo biến môi trường đè, quyền cao hơn «Hạn chế» — **đạt** (LC-T120-23; Lá Chắn T-121 mục 3, T-124 B.1 b)

`search_console_card` (`settings.py:851-884`): `env_file.gsc_site_url_overridden()` (biến **có mặt**, kể cả rỗng, cùng điều kiện `load_settings`) → cảnh báo mỗi lần mở; sau khi lưu, `SaveResult.overridden` → ô vàng (`:773-775`). Quyền «Chủ sở hữu», «Toàn quyền»: cảnh báo ở «Tìm thuộc tính» (`:803`) và tách riêng ở «Kiểm tra» (`:834-835`). Thuộc tính không phủ website, chưa xác minh, sai dạng: không chọn được (`SiteEntry.usable`, `gsc_entry_status`). Họa Sĩ 2 ca biến môi trường (rỗng, có giá trị), `test_kiem_tra_hien_cau_co_dinh_canh_bao_quyen_ten_may_chu_thuan`, `test_khong_co_muc_dung_duoc_thi_khong_cho_chon`.

## Lỗi phát hiện

Không có lỗi mới.

## Đánh giá lỗi, ghi nhận của Soi Lỗi; R5

| Mục | Lá Chắn |
|---|---|
| **SL-T125-1** · Thấp · đọc lại cả bản lưu tạm mỗi lần bấm | Đồng ý Thấp (tốc độ). **Đã đóng** ở `93d9f78` theo cách Soi Lỗi gợi ý, cộng dấu file chặt hơn (mục 5). Ca Soi Lỗi gỡ `xfail` qua (lô test) |
| **SL-T125-2** · Thấp · «Xóa bản lưu tạm» khi tab khác đang lấy | Đồng ý Thấp. **Đã đóng** qua hàm công khai `clear_cache` trong cùng khóa (mục 6). Ca Soi Lỗi gỡ `xfail` qua |
| GN-1 kết quả «Tìm thuộc tính» không tự bỏ khi `WORDPRESS_URL` đổi | Chấp nhận: client T-121 kiểm lại phủ website ở lần lấy, câu cố định |
| GN-2 mở trang với bản lưu tạm của thuộc tính khác | Hành vi kho T-122 (thiết kế 2.7), đúng ý |
| GN-3 số trong bảng là chữ; chưa có nút lấy từ khóa cho khoảng tự chọn | Không phải bảo mật; phiếu sau |
| R5 (`tests/test_soi_loi_t125.py`) | `git diff 1c55e9e..df46f70`: chỉ xóa 2 khối `@pytest.mark.xfail(...)` và dòng `import pytest`; thân test không đổi. Đúng |
| Họa Sĩ mục 5.2 (hai test cũ hỏng ở bản đầu, sửa phía giao diện) | Đúng luật U2 (không in giá trị `.env`, kể cả `GSC_SITE_URL`): trang chỉ nói **loại** thuộc tính; `test_soi_loi_t084` giữ nguyên và qua |

## Thử độc lập (Fable)

Script `probe_t125.py` (thư mục nháp của phiên, không nằm trong repo): hàm thuần, file SQLite tạm; không mạng, không Streamlit.

| Phần | Ca | Kết quả |
|---|---|---|
| A `page_label` (đường dẫn «Trang khác») | 6 địa chỉ: link Markdown trần và dạng `%`, `%E2%80%AE`, `<b>`, `=HYPERLINK`, 500 ký tự | Giải mã rồi làm sạch: ký tự đảo hướng bị bỏ, `<b>` bị từ chối, chữ `[x](…)` và `=HYPERLINK` giữ làm **chữ** (chỉ vào ô bảng), cắt 120 ký tự |
| B `safe_text`, `escape_markdown` | 8 chuỗi | `safe_text` thêm dấu cách trước `=`, `+`, `-`, `@`, tab; `escape_markdown` thoát `[ ] ( ) * <` và chèn ký tự rộng 0 vào `://`; **không** bỏ ký tự đảo hướng (ghi nhận 1) |
| C `stamp()` | ghi đè cùng cỡ + giả giờ sửa trùng; thư mục; file không có; liên kết | Số đếm thay đổi khác → dấu khác; thư mục và file không có → `None`; symlink không tạo được trên máy này (điều kiện B.3) |

Ngoài ra: grep trang và phần mới của Cài đặt theo danh sách mẫu cấm (`unsafe_allow_html`, `LinkColumn`, `st.cache_*`, `fragment`, `run_every`, `"expr"`, `"href"`, `"url"`, `markdown_link`, `st.html`, `components`, `os.environ`, `print`, `logging`): không có (chỉ docstring nhắc tên).

## Danh sách kiểm tra (điều kiện của phiếu)

| Mã | Đạt | Bằng chứng |
|---|---|---|
| LC-T120-11 | ✔ | Mục 2 |
| LC-T120-13 | ✔ | Trang, Cài đặt không nhập `seo_app.ai`, `seo_app.google.sheets`; từ khóa chỉ hiện trong bảng (`test_trang_khong_nhap_ai_sheets_khong_html_khong_cache_tu_lam_moi`); kế hoạch đọc từ bản lưu tạm, không gọi Sheets |
| LC-T120-14 | ✔ | Mục 1; client mới mỗi lần bấm là của `refresh`, `find_properties`, `check_connection` (T-124) |
| LC-T120-15 | ✔ | Test dưới bộ chặn mạng, Google giả, client giả đếm lệnh; trang mới trong `PAGES` (`main.py:29`), `test_app_pages` tự mở |
| LC-T120-19 | ✔ | Mục 2; probe A |
| LC-T120-20 | ✔ | Mục 3 |
| LC-T120-21 | ✔ | Mục 1, 5 |
| LC-T120-23 | ✔ | Mục 7 |
| Lá Chắn T-124 ĐK 1 (a–g) | ✔ | (a) mục 4; (b) mục 7; (c) mục 1; (d) mục 2, câu của lõi qua `plain`, `SiteEntry.site_url`, `HostShare.host` trong ô bảng hay `st.code`; (e) nút «Xóa bản lưu tạm» trong ô mở rộng, mở sẵn khi file lỗi (`test_loi_mo_ban_luu_tam_bao_cau_co_dinh_va_mo_san_nut_xoa`); (f) `MSG_SKIPPED_ITEMS` (`:163-166`, `:854`); (g) câu chờ `MSG_FETCHING` nhắc lệnh xin quyền có thể chờ thêm |
| Lá Chắn T-121 phần T-125 | ✔ | Mục 7; `SiteEntry.site_url`, tên máy chữ thuần |
| LC-T123-1 phần còn lại | ✔ | `MSG_SKIPPED_ITEMS` khi `skipped_items > 0` (`test_bai_dia_chi_la_va_dong_ke_hoach_chua_noi_co_cau_bao`) |
| U2 (T-084) | ✔ | Trang Cài đặt không in giá trị `.env` (`gsc_current_text` chỉ loại thuộc tính); `test_soi_loi_t084` trong lô |
| W2 | ✔ | Không lệnh ghi tới Google, WordPress; `.env` chỉ ghi qua `save_property`; xóa chỉ file cache của app, trong khóa |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 14 file liên quan trên `df46f70` (T-125 4 file; `test_app_pages`; trang Cài đặt `test_soi_loi_t084`, `test_t101_settings_google`, `test_settings_keys`, `test_t112_settings_switch`; T-122 `test_search_cache`, `test_soi_loi_t122`; T-124 `test_tracking_refresh`, `test_t124_chuan_hoa_va_cache`, `test_soi_loi_t124`) | **569 qua, 2 bỏ qua** (2 ca symlink `test_t125_tho_may.py:163`, `test_search_cache.py:755`: Windows chưa bật Developer Mode), 0 hỏng, 6 phút 19 giây | ✔ |
| Probe (mục «Thử độc lập») | đúng hướng cả | ✔ |
| `ruff check` 9 file; `ruff format --check` 5 file mới | sạch; đã đúng định dạng | ✔ |
| bandit `tracking.py`, `settings.py` (`PYTHONUTF8=1`) | 1 Low B101 (`tracking.py:538`, `assert` thu hẹp kiểu sau khi `render` đã loại `final_end is None`): báo nhầm | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 8 file của phiếu + 3 báo cáo | 0; biên bản này: 0 | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `config/` không đổi | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `31d8cec`) không xung đột; `git diff main..HEAD` ở `refresh.py`, `search_cache.py`, `match.py`, `env_file.py`, `client.py` chỉ là phần lượt 2 (+36, +29): T-124 trên `main` và trên nhánh cùng nội dung | ✔ |

## Ghi nhận (không xếp lỗi)

1. `escape_markdown` không bỏ ký tự đảo hướng, ký tự vô hình; trang an toàn nhờ lớp làm sạch ở nguồn (`clean_text` của client T-121, `page_label`, `_clean_text` của client WordPress, `visible` ở Cài đặt). Phiếu sau nào đưa chữ ngoài **mới** vào `plain` phải qua một trong các lớp đó trước (ghi vào `security.md` U1 khi tiện).
2. Khe `lstat` → `open` 100 byte trong `stamp()` (mục 5): vô hại; ca liên kết của Thợ Máy chạy trên Mac/Linux.
3. Bản giữ trong `session_state`: mỗi tab một bản (vài chục MB ở cỡ trần); đóng tab là mất. Không chép ra đâu.
4. «Kiểm tra», «Tìm thuộc tính» không giữ khóa `_FETCH_LOCK` (Soi Lỗi T-124 GN-3): đúng chữ LC-T120-22.
5. `assert` ở `choose_periods` (bandit B101): chỉ thu hẹp kiểu, `render` đã loại ca `final_end is None` trước khi gọi.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp.

**B. Cho việc sau** (không chặn T-125):

1. **T-127 («Đưa vào kế hoạch», câu 7 = B):** làm đúng LC-T120-24 (bộ lọc chặt hơn ô từ khóa thường: chỉ chữ, số, khoảng trắng, `-`; ≤ 80 ký tự; bỏ từ khóa có số điện thoại, email; ≤ 10 mỗi lần; không AI; qua mọi bộ kiểm của dòng kế hoạch; ghi nguồn «Search Console»). Lá Chắn kiểm đầy đủ.
2. **Lượt thử thật với Google:** mở trang Theo dõi và Cài đặt với dữ liệu thật; xác nhận từ khóa, đường dẫn thật hiện chữ thuần, số lệnh mỗi nút (≤ 20; «Kiểm tra» ≤ 3), cảnh báo quyền khi tài khoản dịch vụ có quyền cao hơn «Hạn chế».
3. **Khi có máy Mac** (chủ dự án chưa có): chạy `test_t125_tho_may.py::test_stamp_of_a_folder_or_link_is_none` (phần symlink) cùng các ca Mac đang treo (T-063 ĐK 3).
4. **Phiếu dọn (Thấp):** ghi vào `security.md` mục U1 câu «chữ ngoài mới phải qua lớp làm sạch trước `escape_markdown`» (ghi nhận 1).

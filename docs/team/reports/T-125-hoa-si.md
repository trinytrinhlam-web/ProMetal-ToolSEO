# Báo cáo T-125 · Trang «📈 Theo dõi» và mục Search Console trong Cài đặt (phần Họa Sĩ)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | T-125 (Chỉ Huy B giao 05/11) |
| Ngày nộp | 2026-11-05 |
| Nhánh | `team/T-125` (từ `team/T-124` `682f62c`; gộp `main` trước khi nộp, mục 7) |
| Kết quả | Xong yêu cầu 1–8. Trang mới `app/views/tracking.py` (menu «📈 Theo dõi», giữa Kế hoạch và Cài đặt) và mục «📈 Search Console» trong Cài đặt → 📗 Google. Mở trang, mở Cài đặt **không gọi mạng**; chỉ ba nút «🔄 Lấy số liệu mới», «🔎 Tìm thuộc tính», «✅ Kiểm tra» gọi Google. Không sửa `seo_app/**`, README. 41 ca test mới; chọn lọc trên cây đã gộp `main`: **684 qua, 6 bỏ qua, 0 hỏng**; `ruff check .` sạch |

## 1. Tóm tắt (cho chủ dự án)

- Menu có thêm trang **📈 Theo dõi**, nằm giữa Kế hoạch và Cài đặt (anh chọn ngày 04/11). Trang cho biết từng bài, trang trên website được bao nhiêu lượt click, lượt hiển thị trên Google, tỉ lệ click (CTR), vị trí trung bình, và so với kỳ trước.
- Trang **chỉ hiện số đã chốt** (Google còn đang cập nhật 2–3 ngày gần nhất nên chưa tính), ghi rõ «Số liệu tới hết ngày …».
- Bài đáng chú ý có nhãn: 🔻 tụt hạng, 📉 mất click, 👻 chưa có lượt hiển thị, 👀 nhiều hiển thị ít click, 🎯 từ khóa chính chưa có, 🌱 mới đăng, 🔺 lên hạng. Ngưỡng là mặc định (anh chọn ngày 04/11). Bài «chưa có lượt hiển thị» kèm cách kiểm bằng tay trong Search Console (ô «Kiểm tra URL»), app không tự kiểm.
- Chọn một bài để xem biểu đồ click, vị trí theo tuần và các từ khóa người ta gõ để tìm thấy bài. Nút «Đưa vào kế hoạch» đã có chỗ nhưng chưa bấm được (làm ở phiếu T-127).
- Lấy số liệu: bấm **«🔄 Lấy số liệu mới»**. Lần đầu lấy 16 tháng, khoảng một phút; các lần sau chỉ vài ngày mới. Mở trang không hỏi Google: số liệu đọc từ bản lưu tạm trong máy.
- Lần đầu dùng: vào **Cài đặt → 📗 Google → 📈 Search Console**, bấm «Tìm thuộc tính», chọn thuộc tính của website, bấm «Lưu thuộc tính đã chọn», rồi «Kiểm tra». Việc anh làm phía Google (bật API, thêm email tài khoản dịch vụ với quyền «Hạn chế») đã có trong README mục 15.

## 2. Bố cục (ảnh chụp chữ)

Trang «📈 Theo dõi» khi đã có số liệu (khung rộng):

```
Theo dõi trên Google                                                    [🔄 Lấy số liệu mới]
Lượt click, lượt hiển thị, vị trí của từng bài, trang trên Google (Search Console, chỉ đọc).
(kết quả lần bấm vừa rồi, hiện một lần: ✅ «Đã lấy số liệu tới hết ngày …» + các câu phụ)
Số liệu tới hết ngày 02/11/2026 (ngày theo giờ Google) · lấy lúc 13:59 05/11/2026
(ℹ️ «Có thể đã có số liệu mới.» khi lần lấy cuối đã quá 24 giờ)
Khoảng: (7 ngày)(28 ngày)(3 tháng)(Tùy chọn)   So với: [Kỳ trước ▾]   ☐ Chỉ bài trong kế hoạch
  (Tùy chọn: [Từ ngày] [Tới ngày], chỉ trong phần số liệu đã có)
┌ Lượt click ──────┬ Lượt hiển thị ───┬ CTR ─────────────┬ Vị trí trung bình ─┐
│ 252  ▼ -28 (-10%)│ 4.065 ▼ -135 (-3%)│ 6,2% ▼ -0,5 điểm │ 4,8  ▼ xuống 0,9 bậc│
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
Tổng cộng theo từng trang nên có thể cao hơn chút so với biểu đồ của Search Console …
1 bài, trang có địa chỉ không khớp địa chỉ website trong cài đặt (WORDPRESS_URL) …
1 dòng kế hoạch «Đã đăng» chưa nối được với bài trên website …
**Cần chú ý: 1 bài tụt hạng · 1 bài mất click · 1 bài chưa có lượt hiển thị · …**
Lọc theo nhãn: [Mọi bài, trang ▾]
 Bài / trang             Loại  Mã KH  Click ± click  Hiển thị ± hiển thị  CTR  ± CTR  Vị trí ± vị trí  Nhãn
 Sửa cửa kéo bị kẹt ray  Bài   B-012     56 0          1.120  0         5,0% 0 điểm  6,0  giữ nguyên
 Cổng sắt bị xệ cánh     Bài   B-007      0 -28 (-100%)  420  -140 (-25%) 0,0% …   14,0  xuống 9,0 bậc  🔻 Tụt hạng · 📉 Mất click · 🎯 …
 Lan can cầu thang bị gỉ Bài              0 0              0  0           —    …     —    …              👻 Chưa có lượt hiển thị
Bảng xếp theo click nhiều nhất, rồi lượt hiển thị.
Bài «chưa có lượt hiển thị» có thể chưa được Google lập chỉ mục. Kiểm bằng tay: … «Kiểm tra URL» …
#### Chi tiết một bài, trang
Bài, trang: [Sửa cửa kéo bị kẹt ray ▾]
**Sửa cửa kéo bị kẹt ray** · Bài
🔻 Tụt hạng: <lý do do code viết, chỉ có số>          (gợi ý cố định)
 (biểu đồ cột: click mỗi tuần)        (biểu đồ đường: vị trí mỗi tuần, lên cao là tốt)
**Từ khóa trên Google (06/10/2026 – 02/11/2026)**
 Từ khóa             Click  Hiển thị  CTR   Vị trí  ± vị trí     Ghi chú
 sửa cửa kéo bị kẹt     23       600  3,8%   6,5    lên 1,0 bậc  từ khóa chính, gộp 2 cách gõ
 …(50 dòng đầu)   [Xem thêm 8 từ khóa]   ⬜ Xem từng cách gõ của từ khóa đã gộp
Google ẩn từ khóa hiếm và từ khóa có thông tin cá nhân, nên cộng các dòng ở đây ít hơn tổng của bài.
[➕ Đưa vào kế hoạch] (khóa, «Sắp có (T-127)»)
▸ Trang khác trên website (trang chủ, chuyên mục, địa chỉ cũ…): 3 trang
▸ 🧹 Bản lưu tạm số liệu trên máy  → [Xóa bản lưu tạm] → hỏi lại → [Xóa] [Thôi]
```

Chưa khai báo thuộc tính: chỉ có tiêu đề, nút «Lấy số liệu mới» bị khóa, ô «Chưa chọn thuộc tính Search Console. Vào Cài đặt → …» và link «Mở Cài đặt». Chưa có số liệu: «Chưa có số liệu. Bấm «Lấy số liệu mới» (lần đầu lấy 16 tháng, khoảng một phút).»

Cài đặt → 📗 Google, khung mới dưới phần Google Sheet:

```
#### 📈 Search Console
Trang 📈 Theo dõi đọc số liệu … Cách thêm: Search Console → Cài đặt → Người dùng và quyền → … «Hạn chế».
(⚠️ khi có biến môi trường GSC_SITE_URL: «… đè file .env, kể cả khi để trống …»)
✅ Đã chọn thuộc tính (lưu trong file .env)
Loại thuộc tính: tên miền (sc-domain:…); phần mềm tự lọc phần ngoài website.
[🔎 Tìm thuộc tính] [✅ Kiểm tra]
Email tài khoản dịch vụ (thêm vào Search Console, quyền «Hạn chế»): [seo-app@…]
 Thuộc tính                                  Quyền          Dùng cho website
 sc-domain:suachuacuasat.com                 Hạn chế        ✔ dùng được (tự lọc phần ngoài website)
 https://suachuacuasat.com/                  Chủ sở hữu     ✔ dùng được
 https://www.staging-m.suachuacuasat.com/    Hạn chế        ✘ không phải website trong WORDPRESS_URL
⚠️ Phần mềm chỉ cần quyền «Hạn chế»: nên hạ quyền …
Thuộc tính dùng cho trang Theo dõi: [sc-domain:suachuacuasat.com ▾]   [Lưu thuộc tính đã chọn]
(✅ Kiểm tra: danh sách câu cố định; ⚠️ quyền cao; bảng «Tên máy · Lượt hiển thị · Ghi chú»)
→ Mở trang Theo dõi
```

## 3. Việc đã làm (yêu cầu 1–8)

| Yêu cầu | Chỗ làm |
|---|---|
| 1. Trang, menu, đăng nhập | `app/views/tracking.py` (mới). `app/main.py` `PAGES`: «📈 Theo dõi» giữa Kế hoạch và Cài đặt. Trang chỉ chạy sau khi `main.py` kiểm đăng nhập, như mọi trang |
| 2. Khoảng, so kỳ, bảng, nhãn, «Trang khác», từ khóa, biểu đồ | <ul><li>`choose_periods`: 7/28/91 ngày (`PRESET_DAYS`); «Tùy chọn» là hai ô ngày trong phần số liệu đã có (`custom_period`); so «Kỳ trước» hay «Cùng kỳ năm trước». Kỳ so sánh chưa đủ số liệu thì nói rõ, không so.</li><li>`metrics_row`: tổng toàn website (`site_totals`). Màu chênh lệch theo dấu; với vị trí, lên hạng là xanh.</li><li>`pages_section`: dòng «Cần chú ý» (`attention_text`), lọc theo nhãn, «Chỉ bài trong kế hoạch», bảng từng bài. Cột «Mã KH» lấy từ kế hoạch lưu trên máy.</li><li>`detail_panel`: nhãn kèm lý do và gợi ý; biểu đồ tuần `st.vega_lite_chart` (`CLICK_CHART`, `POSITION_CHART`).</li><li>`keyword_panel`: 50 dòng đầu, «Xem thêm», từng cách gõ, ghi chú Google ẩn từ khóa hiếm.</li><li>«Trang khác trên website» nằm trong một ô mở rộng.</li></ul> |
| 3. «Lấy số liệu mới» | <ul><li>`fetch_now` gọi `refresh` (client mới mỗi lần bấm); client WordPress chỉ tạo cho đúng lần bấm.</li><li>Kết quả hiện một lần (`show_report`): câu chính và câu phụ, đều qua `escape_markdown`.</li><li>Tab khác đang lấy: câu `MSG_BUSY`.</li><li>Mốc «lấy lúc …» ở dòng trạng thái; bấm lại trong 10 phút: «Vừa lấy số liệu lúc …».</li><li>`skipped_items > 0`: câu cố định.</li><li>Ô «🧹 Bản lưu tạm số liệu trên máy» có nút «Xóa bản lưu tạm»: hỏi lại rồi mới gọi `store.clear()`.</li></ul> |
| 4. Cài đặt → Google → Search Console | `search_console_card`, `gsc_found_panel`, `gsc_check_panel`, `_save_property` trong `app/views/settings.py` |
| 5. Không gọi mạng khi mở | <ul><li>Mọi lệnh mạng nằm sau `if st.button(...)`.</li><li>Trang chỉ đọc bản lưu tạm khi file đã có, nên mở trang không tạo file.</li><li>Có test dưới bộ chặn mạng, giả client đếm lệnh, kèm 2 ca đối chứng (mục 5).</li></ul> |
| 6. Chữ thuần | Mọi bảng qua `safe_rows` (như trang Kế hoạch). Chữ ngoài còn hiện ở ô chọn (chữ thuần) và qua `plain` = `escape_markdown`. Không `unsafe_allow_html`, không cột link |
| 7. Chỗ cho «Đưa vào kế hoạch» | Nút khóa «➕ Đưa vào kế hoạch» dưới bảng từ khóa, chú thích «Sắp có (T-127)» |
| 8. Không lùi | `test_app_pages.py` tự mở trang mới (lấy từ thư mục `views`); các test cũ của trang Cài đặt vẫn qua (mục 5) |

## 4. Điều kiện bảo mật

| Điều kiện | Làm thế nào | Test |
|---|---|---|
| LC-T120-11 | Mọi bảng có chữ Google hay WordPress qua `safe_rows`; không `LinkColumn`. Chỉ hiện `TrackedPage.label`, `KeywordGroup.text`, `KeywordVariant.text`; không hiện `PageKey`, `KeywordGroup.key` (Lá Chắn T-123 mục 7.2) | `test_tieu_de_wordpress_va_tu_khoa_google_hien_chu_thuan`: `=HYPERLINK(…)` thành « =HYPERLINK(…)»; chữ Markdown, link chỉ nằm trong ô bảng, không vào Markdown. Kèm `test_trang_khong_nhap_ai_sheets_…` |
| LC-T120-13 | Trang không nhập lớp AI, client Google Sheets; từ khóa chỉ hiện trên trang | `test_trang_khong_nhap_ai_sheets_khong_html_khong_cache_tu_lam_moi` |
| LC-T120-14 | Trang chạy qua `main.py` (đăng nhập); không gọi mạng khi mở; `refresh`, `find_properties`, `check_connection` tự tạo client mới mỗi lần bấm | `test_chua_dang_nhap_thi_khong_mo_duoc_trang`; `test_bam_lay_so_lieu_moi_…`: một client mỗi lần bấm |
| LC-T120-19 | Đường dẫn «Trang khác» là `page_label` (đã giải mã `%`, qua `clean_text`, cắt 120 ký tự), nằm trong ô bảng. Tên máy ở «Kiểm tra» cũng trong ô bảng. Không dựng link | `test_trang_khac_hien_duong_dan_da_lam_sach_chu_thuan`: `/?s=[x](https://evil.example)` và ký tự đảo hướng. `test_kiem_tra_…_ten_may_chu_thuan` |
| LC-T120-20 | `CLICK_CHART`, `POSITION_CHART` là hằng trong code. Dữ liệu chỉ có ngày (`dd/mm/yyyy` do code viết) và số. Tên bài nằm trên biểu đồ, qua `st.markdown(escape_markdown(…))` | `test_bieu_do_khuon_co_dinh_chi_ngay_va_so`: đặc tả không có chữ của bài, `expr`, `href`, `url` |
| LC-T120-21 | Mở trang, mở Cài đặt: 0 client, 0 lệnh. Không `st.cache_*`, `st.fragment`, `run_every`. Chưa có file thì mở trang không tạo file | `test_mo_trang_va_doi_moi_o_khong_goi_mang`, `test_mo_cai_dat_khong_goi_mang`, `test_chua_co_file_thi_mo_trang_khong_tao_file`, `test_trang_khong_nhap_…`; đối chứng `test_doi_chung_bam_nut_thi_bo_dem_bat_duoc` và `test_doi_chung_bam_nut_thi_moi_tao_client` |
| LC-T120-23, Lá Chắn T-124 B.1 b | `env_file.gsc_site_url_overridden()`: biến có mặt là đè, kể cả rỗng; không `.strip()`. Mở Cài đặt thì cảnh báo; lưu xong mà `SaveResult.overridden` thì cảnh báo | `test_bien_moi_truong_de_env_thi_canh_bao[bien-rong]`, `[bien-co-gia-tri]` |
| LC-T120-12, Lá Chắn T-124 B.1 a, Soi Lỗi GN-5 | Kết quả `find_properties(...)` giữ trong `S["gsc-found"]`. Ô chọn chỉ có `found.usable_site_urls`. `_save_property` truyền đúng đối tượng đó vào `save_property`; không dựng `PropertyList` từ chữ trên trang | `test_luu_truyen_dung_doi_tuong_tim_thay_vao_save_property` (so `is`); `test_chua_tim_ma_bam_luu_thi_khong_ghi`; `test_luu_that_vao_env_qua_google_gia` (ghi `.env` tạm qua Google giả) |
| Lá Chắn T-124 B.1 c | Như LC-T120-21 | Như trên |
| Lá Chắn T-124 B.1 d | `report.message`, `report.notes`, `check.messages`, `PropertyList.message`, `SaveResult.message` qua `escape_markdown`. `SiteEntry.site_url`, `HostShare.host` trong ô bảng hay `st.code` | `test_loi_lay_so_lieu_ra_cau_co_dinh_da_escape`, `test_tim_thuoc_tinh_loi_hien_cau_co_dinh_da_escape`, `test_kiem_tra_loi_hien_loi_da_escape` |
| Lá Chắn T-124 B.1 e (T-122 mục 8.2) | Nút «Xóa bản lưu tạm» luôn có trong ô «🧹 …». Mở file lỗi (`MSG_OPEN`…) thì ô này mở sẵn | `test_xoa_ban_luu_tam_hoi_lai_roi_moi_xoa`, `test_loi_mo_ban_luu_tam_bao_cau_co_dinh_va_mo_san_nut_xoa` |
| Lá Chắn T-124 B.1 f, LC-T123-1 | `skipped_items > 0`: «N bài, trang có địa chỉ không khớp địa chỉ website trong cài đặt (WORDPRESS_URL) nên không gắn được số liệu.» | `test_bai_dia_chi_la_va_dong_ke_hoach_chua_noi_co_cau_bao` |
| Lá Chắn T-124 B.1 g, GN-1 T-121 | Câu chờ khi lấy số liệu: «… lệnh xin quyền đọc có thể chờ thêm vài giây». Hai nút ở Cài đặt: «(có thể mất vài giây)» | (chữ, không có test riêng) |
| Lá Chắn T-121 mục 3 phần T-125 | «Tìm thuộc tính» cảnh báo `MSG_PERMISSION_HIGH` khi có thuộc tính quyền «Chủ sở hữu», «Toàn quyền». «Kiểm tra» tách câu đó thành cảnh báo riêng. Thuộc tính không phủ website, «Chưa xác minh», sai dạng thì không chọn được (`SiteEntry.usable`) | `test_tim_thuoc_tinh_chi_khi_bam_giu_ket_qua_bang_chu_thuan`, `test_kiem_tra_hien_cau_co_dinh_canh_bao_quyen_ten_may_chu_thuan`, `test_khong_co_muc_dung_duoc_thi_khong_cho_chon` |
| Lá Chắn T-123 mục 7.3 | Nhãn «Trang khác» (có thể là chữ khách gõ ở `/?s=…`) chỉ hiện trong ô bảng, không đi đâu khác | Như LC-T120-19 |

## 5. Test

### 5.1 Test mới: 41 ca, 2 file

`tests/test_t125_tracking_page.py` (25 ca), `tests/test_t125_settings_search_console.py` (16 ca). Bản lưu tạm (cache số liệu 120 ngày, 2 ngày cuối là số tạm; danh sách bài; kế hoạch) dựng sẵn trong thư mục tạm. Google giả lấy của `test_tracking_refresh` (`Search`, `Factory`). Không gọi Google, WordPress thật; bộ chặn mạng của `conftest.py` vẫn bật.

| Nhóm | Ca |
|---|---|
| Không gọi mạng, đăng nhập | <ul><li>`test_mo_trang_va_doi_moi_o_khong_goi_mang`: mở trang, đổi khoảng, kỳ so sánh, lọc, chọn bài, xem cách gõ, xem thêm từ khóa. Kết quả: 0 client, 0 lệnh.</li><li>`test_mo_cai_dat_khong_goi_mang`.</li><li>`test_chua_co_file_thi_mo_trang_khong_tao_file`.</li><li>`test_chua_dang_nhap_thi_khong_mo_duoc_trang`.</li><li>Đối chứng: `test_doi_chung_bam_nut_thi_bo_dem_bat_duoc`, `test_doi_chung_bam_nut_thi_moi_tao_client`. Cùng cách giả, bấm nút thì bộ đếm lên 1, chứng minh bộ đếm canh đúng đường gọi mạng.</li><li>`test_trang_khong_nhap_ai_sheets_khong_html_khong_cache_tu_lam_moi`: đọc cây mã.</li></ul> |
| Số liệu, bảng, nhãn | `test_moc_so_lieu_tong_website_va_so_ky_truoc`, `test_bang_tung_bai_nhan_ma_ke_hoach_va_so_kieu_viet_nam`, `test_bai_dia_chi_la_va_dong_ke_hoach_chua_noi_co_cau_bao`, `test_loc_theo_nhan_va_chi_bai_trong_ke_hoach`, `test_chua_co_ke_hoach_thi_o_loc_ke_hoach_bi_khoa`, `test_trang_khac_hien_duong_dan_da_lam_sach_chu_thuan`, `test_chua_co_danh_sach_bai_thi_moi_dia_chi_vao_trang_khac` |
| Chữ thuần, biểu đồ, từ khóa | `test_tieu_de_wordpress_va_tu_khoa_google_hien_chu_thuan`, `test_bieu_do_khuon_co_dinh_chi_ngay_va_so`, `test_bang_tu_khoa_gop_cach_go_tu_khoa_chinh_xem_them`, `test_chua_co_tu_khoa_cua_khoang_thi_noi_ro` |
| Khoảng ngày | `test_khoang_tu_chon_sai_thu_tu_bao_loi`, `test_khoang_dai_hon_so_lieu_da_luu_va_cung_ky_nam_truoc` |
| «Lấy số liệu mới», bản lưu tạm | `test_bam_lay_so_lieu_moi_hien_ket_qua_roi_hien_so_lieu` (một client mỗi lần bấm; bấm lại trong 10 phút: không lệnh nào), `test_tab_khac_dang_lay_thi_bao_ban`, `test_loi_lay_so_lieu_ra_cau_co_dinh_da_escape`, `test_xoa_ban_luu_tam_hoi_lai_roi_moi_xoa`, `test_loi_mo_ban_luu_tam_bao_cau_co_dinh_va_mo_san_nut_xoa` |
| Cài đặt → Search Console | `test_thuoc_tinh_dang_dung_noi_theo_loai_khong_in_gia_tri` (4 ca), `test_chua_co_file_khoa_thi_khoa_nut`, `test_tim_thuoc_tinh_chi_khi_bam_giu_ket_qua_bang_chu_thuan`, `test_luu_truyen_dung_doi_tuong_tim_thay_vao_save_property`, `test_chua_tim_ma_bam_luu_thi_khong_ghi`, `test_khong_co_muc_dung_duoc_thi_khong_cho_chon`, `test_tim_thuoc_tinh_loi_hien_cau_co_dinh_da_escape`, `test_luu_that_vao_env_qua_google_gia`, `test_bien_moi_truong_de_env_thi_canh_bao` (2 ca), `test_kiem_tra_hien_cau_co_dinh_canh_bao_quyen_ten_may_chu_thuan`, `test_kiem_tra_loi_hien_loi_da_escape` |

### 5.2 Hai test cũ hỏng ở bản đầu: sửa phía giao diện, không đổi test

| Test cũ | Vì sao hỏng | Sửa |
|---|---|---|
| `test_soi_loi_t084.py::test_whole_settings_page_never_shows_env_values_or_paths` | Bản đầu in thuộc tính đang dùng (`GSC_SITE_URL`) ra trang Cài đặt. Luật U2 (T-084): trang Cài đặt không bao giờ in giá trị trong `.env`, kể cả biến này | Chỉ nói **loại** thuộc tính và có phủ website không (`gsc_current_text`: `parse_property`, `covers_site`, ngay trên máy, không gọi mạng); thuộc tính sai dạng thì hiện câu lỗi cố định của client. Lệch phác thảo T-120 mục 4.4 («Thuộc tính đang dùng: https://…/»): theo luật đã có. Mục tìm được từ Google vẫn hiện đủ (chữ Google, không phải giá trị `.env`) |
| `test_t101_settings_google.py::test_not_declared_shows_status_only` | Ca này đếm đúng 2 nhãn «badge» trong tab Google (file khóa, Sheet); bản đầu thêm nhãn thứ ba | Dòng trạng thái Search Console viết bằng chữ (✅/⚪ in đậm), không dùng nhãn «badge» |

### 5.3 Kết quả

Chạy chọn lọc trên cây đã gộp `main` (`8a09fcb`), 19 file:

- T-125: `test_t125_tracking_page`, `test_t125_settings_search_console`;
- mở mọi trang: `test_app_pages`, `test_app`;
- trang Cài đặt: `test_app_t044_safe_text`, `test_settings_blind`, `test_settings_images`, `test_settings_keys`, `test_soi_loi_t016_t020`, `test_soi_loi_t019`, `test_soi_loi_t021_t017`, `test_soi_loi_t023`, `test_soi_loi_t044`, `test_soi_loi_t062`, `test_soi_loi_t084`, `test_soi_loi_t112`, `test_t101_settings_google`, `test_t112_settings_switch`;
- lõi lấy số liệu (Google giả dùng chung): `test_tracking_refresh`.

Kết quả: **684 qua, 6 bỏ qua, 0 hỏng** (12 phút 33). 6 ca bỏ qua là ca có sẵn, cùng số với lượt chạy trước khi gộp. Trước khi gộp, cùng bộ này trừ `test_tracking_refresh`: 576 qua, 6 bỏ qua, 2 hỏng (hai ca ở mục 5.2, đã sửa).

- `uv run ruff check .`: sạch. `ruff format --check` các file mới: sạch. `settings.py` còn khối `API_KEY_FIELDS` chưa đúng khuôn **từ trước**, không phải dòng tôi thêm.
- `detect-secrets` (`PYTHONUTF8=1`): file mồi tiếng Việt bị bắt (công cụ đọc được file tiếng Việt), đã xóa; các file của phiếu không có gì.

## 6. Giới hạn, việc để phiếu sau

- **«Lấy từ khóa cho khoảng này»** (thiết kế 1.3 bước 5) chưa có. Lõi `refresh` (T-124) chỉ lấy từ khóa của 28 ngày tới E và kỳ trước liền kề, chưa có hàm lấy từ khóa cho khoảng tự chọn. Trang nói rõ «Chưa có từ khóa cho khoảng này…». Muốn có nút thì cần thêm hàm ở `seo_app/tracking` (Thợ Máy), Họa Sĩ nối sau.
- **Số trong bảng là chữ** viết kiểu Việt Nam (`1.120`, `5,0%`), bảng xếp sẵn theo click. Bấm tiêu đề cột thì bảng xếp theo chữ, không theo số. Đổi sang cột số thì mất dấu «,» thập phân kiểu Việt Nam; tôi giữ cách viết như thiết kế 4.1.
- **`queries_by_page`** chia từ khóa theo trang ngay trong trang, cùng quy tắc với `keywords.page_queries` (dùng `match.page_key`). Mỗi địa chỉ chỉ dựng khóa một lần, để lần chạy lại không phải duyệt toàn bộ dòng cho từng bài.
- **Đổi thuộc tính hay `WORDPRESS_URL`**: lần mở trang sau, cache T-122 tự bỏ file của phạm vi cũ khi đọc (thiết kế 2.7 bước 5). Đây là hành vi của kho, không phải của trang.
- **Kết quả lần bấm «Lấy số liệu mới» hiện một lần**: đổi ô khác là mất. Mốc «lấy lúc …» vẫn luôn ở dòng trạng thái.
- **Kế hoạch đọc từ bản lưu tạm** của trang Kế hoạch (không gọi Google). Chưa mở trang Kế hoạch lần nào thì cột «Mã KH» trống và ô «Chỉ bài trong kế hoạch» bị khóa.
- **Chưa mở app thật trong trình duyệt**: cần Google thật. AppTest phủ các đường chính; lượt thử thật là việc của T-128.
- Không sửa `seo_app/tracking`, `seo_app/google`, `seo_app/storage`, README; không đụng `write.py`, `home.py`, `wordpress.py`.

## 7. Gộp `main`, commit

- `2cc720b`: trang «📈 Theo dõi», mục Search Console ở Cài đặt, 41 ca test.
- `8a09fcb`: gộp `main` cục bộ `c1aa6bf` (T-092, T-128, T-129, phiếu T-125…), không xung đột. Lúc nộp `main` **chưa có T-124**: nhánh này vẫn mang T-124 từ gốc `team/T-124` `682f62c`. `uv.lock`, `pyproject.toml` không đổi.
- Commit cuối: báo cáo này.

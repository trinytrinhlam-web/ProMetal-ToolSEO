# Báo cáo T-091 · Dọn client WordPress sau T-059 · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-091](../tickets/T-091-don-client-wordpress-sau-t059.md) |
| Nhánh | `team/T-091` (gốc `main` `1b45f5d`, kiểm trên đầu nhánh `7965f2b`); thử gộp với `main` `d1506cb` |
| Ngày nộp | 2026-10-28 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T091-1, -2, -3). **Không lỗi nào bắt buộc sửa trước Lá Chắn** |

## Tóm tắt (cho chủ dự án)

- **Bốn việc của phiếu đều chạy đúng** trên phép thử riêng của tôi:
  - chữ hỏng (surrogate lẻ) website trả về, ở tên site, tên tài khoản, vai trò, chuyên mục, thẻ, bài đã đăng, bài nháp, ảnh, nay thành dấu «�», trang không còn vỡ;
  - mã bài, mã ảnh lớn vô lý bị coi là dữ liệu hỏng;
  - khi tiêu đề, mô tả SEO có «<», «%BE» hay «\», app báo đúng «Đã ghi», hoặc «Đã ghi nhưng SiteSEO tự bỏ vài ký tự». Tôi thử 300 chữ ngẫu nhiên: 0 ca báo sai;
  - kiểm tra kết nối biết tài khoản có quyền «đăng HTML không lọc» hay không.
- **3 lỗi nhỏ (Thấp), không cần sửa trước khi Lá Chắn kiểm:**
  1. Nếu website khai bảng mã khác UTF-8 (WordPress thật không làm vậy), chữ hỏng vẫn lọt qua như trước.
  2. Nếu website trả **mã bài đã đăng** lớn vô lý, bước SEO của trang Soạn bài báo lỗi trang thay vì câu báo nhẹ. Phiếu mới chặn mã bài, mã ảnh ở lúc gửi nháp, chưa chặn ở danh sách bài đã đăng.
  3. Một test cũ được đổi theo phương án A đã bỏ mất phần kiểm «câu báo không chép lời máy chủ, địa chỉ website». Phần mềm vẫn đúng (tôi kiểm lại ở test mới), chỉ là test cũ yếu đi; nên trả lại phần kiểm đó.
- **Việc của bạn:** không có.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t091.py` | Mới: 98 ca (90 qua, 8 `xfail(strict=True)`: SL-T091-1 5 ca, SL-T091-2 3 ca). Website giả theo từng byte và bảng mã (`_RawSite`, thân trả lời là `urllib3.HTTPResponse` thật), bản Python riêng của `sanitize_text_field` + `wp_unslash` dựng lại từ mã WordPress lõi (`esc_html` ra `&#039;`, `strip_tags` để nguyên «<» có khoảng trắng sau). Không dùng hàm hay bảng kỳ vọng của Thợ Máy |
| `docs/team/reports/T-091-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác. Không gọi website thật (bộ chặn mạng của `tests/conftest.py` bật suốt; script dò ngoài pytest tự chặn socket ở dòng đầu).

## Lỗi tìm ra

### SL-T091-1 · Thấp · Surrogate lẻ lọt `_json` khi website khai bảng mã khác UTF-8

- **Chỗ:** `seo_app/wordpress/client.py:1549-1551`. `_json` chỉ đi qua dữ liệu khi `_SURROGATE_ESCAPE` thấy mã thoát `\uD8..`–`\uDF..` trong **byte** câu trả lời (`response.content`), còn `response.json()` của `requests` giải mã theo `charset` website khai (`response.encoding` lấy từ header).
- **Thử** (website giả riêng, câu trả lời `/wp-json/` có tên site `"Site \ud800"`):
  - `charset=utf-16`, `utf-16-le`, `utf-32`, `utf-7`, `cp500` (EBCDIC): byte không có chuỗi ASCII `\ud8`, nên bộ lọc bỏ qua. `check_connection().site_name` còn U+D800, `encode("utf-8")` hỏng: đúng lỗi SL-T088-1.
  - Đối chứng: `utf-8` sạch; cùng câu trả lời `utf-16` mà không có surrogate thì đọc đúng.
- **Hậu quả:** yêu cầu 1 («mọi chữ… ở một chỗ dùng chung») chưa trọn. WordPress thật luôn trả `charset=UTF-8`; chỉ website bị chiếm, plugin hỏng hay kẻ chen giữa có chứng chỉ hợp lệ mới gây ra. Cùng mức với SL-T088-1.
- **Test:** `test_sl_t091_1_bang_ma_khac_utf8_van_khong_lot_surrogate` (5 xfail).
- **Gợi ý:** dò trên chữ đã giải mã (`response.text`), hoặc luôn đi qua dữ liệu khi `response.encoding` không phải UTF-8. Đơn giản nhất: luôn gọi `_without_lone_surrogates`; cách này đi bằng ngăn xếp, chỉ tốn một lượt duyệt.

### SL-T091-2 · Thấp · Mã bài đã đăng lớn hơn `MAX_ID` làm danh sách bài lỗi SQLite

- **Chỗ:** `_published_from` (`client.py:1644-1667`) không dùng `_positive_id`. `PublishedItem.__post_init__` (`client.py:546`) chỉ chặn `id <= 0`, nên mã 2⁶³, 2⁶⁴, 10³⁰ đi qua `list_published()`.
- **Hậu quả:**
  - `SiteIndexStore.save` ném `OverflowError: Python int too large to convert to SQLite INTEGER`. Đây không phải `sqlite3.DatabaseError` nên không thành `SiteIndexError`.
  - `site_listing` (`seo_app/storage/site_index.py:357-360`) chỉ bắt `WordPressError`, `SiteIndexError`. Lỗi lọt tới `published_listing()` của `app/views/write.py:1984-1994`, và **bước SEO của trang Soạn bài lỗi trang**. Có từ trước T-091.
  - Mục tiêu của phiếu là «mã bài/ảnh website trả về có giới hạn trên hợp lý ngay trong client». Danh sách bài đã đăng chính là mã bài website trả về.
- **Đối chứng:** mã đúng `MAX_ID` vẫn lưu tạm được (`test_bai_da_dang_ma_bang_bien_luu_tam_duoc`).
- **Test:** `test_sl_t091_2_bai_da_dang_ma_qua_bien_bi_bo_khong_vo_luu_tam` (3 xfail; mong đợi: mục mã quá lớn bị bỏ, mục khác vẫn lưu).
- **Gợi ý:** `PublishedItem` kiểm thêm `self.id <= MAX_ID` (hay `_published_from` dùng `_positive_id`). Thêm lớp phòng: `SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError`.

### SL-T091-3 · Thấp (soát R5) · Ca test cũ đổi theo phương án A bỏ mất phần kiểm «không chép»

- **Chỗ:** `tests/test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien`.
  - Trước: `assert_says_in_media_library(msg, media_id=10**20)`. Hàm này kiểm 3 điều: có «thư viện Media», có mã ảnh, có «Media → Thư viện». Nó còn kiểm câu báo **không có** `0909`, `evil`, `quản trị</b>`, `example.com`, `anh-khac` (không chép lời máy chủ, không chép địa chỉ website).
  - Sau: chỉ còn «có thể đã lên thư viện Media», «Media → Thư viện» và không có mã. Năm phần kiểm «không chép» bị bỏ cùng phần kiểm mã ảnh.
- **Vì sao là lỗi:** điều kiện duyệt phương án A chỉ cho đổi phần ghim **câu báo, mã cụ thể**. Phần kiểm «không chép lời máy chủ / địa chỉ site» không thuộc phần đó. Trong ca này, câu trả lời của website có `source_url` là `https://example.com/…`. Câu báo sau này mà lỡ chép địa chỉ đó thì ca cũ bắt được, ca mới không bắt.
- **Phần mềm hiện vẫn đúng:** `test_anh_ma_qua_bien_chi_mot_lenh_va_cau_bao_khong_chep_gi` (2 ca) kiểm lại đủ 6 mẩu với câu trả lời có chữ máy chủ và địa chỉ ảnh khác: câu báo không chép mẩu nào.
- **Gợi ý:** trả 5 dòng kiểm «không chép» vào ca đó; có thể tách phần đó khỏi `assert_says_in_media_library` thành một hàm dùng chung.

## Kiểm theo việc được giao

| Việc | Kết quả | Test |
|---|---|---|
| **Yêu cầu 1.** Surrogate ở mọi chữ website | **Đạt** với UTF-8: tên site (đầu, giữa, cuối chữ, `\uDFFF` hoa, cặp ngược `\uDE00\uD83D`), địa chỉ site, tên tài khoản, vai trò, tên khóa JSON (khóa quyền hỏng thì quyền là `False`), tên chuyên mục, thẻ, `slug`, tiêu đề, meta bài đã đăng (lưu tạm SQLite được), tiêu đề, link bài nháp vừa tạo, địa chỉ, alt ảnh vừa tải (thành «a�.webp», **không** thành «a.webp» của ảnh khác), lỗi WordPress có surrogate trong `code`, `message` (câu cố định, câu và `code` không còn surrogate). Cặp đúng (emoji) và chữ «\ud800» gõ thật (6 ký tự) giữ nguyên. Byte CESU-8 của U+D800 thành «�». **Bảng mã khác UTF-8: SL-T091-1** | `test_kiem_tra_ket_noi_khong_lot_surrogate` (7), `test_surrogate_trong_ten_khoa_json_…`, `test_json_doc_ve_khong_con_surrogate_o_ten_khoa_moi_tang`, `test_surrogate_thay_bang_ky_tu_thay_the_khong_bi_bo`, `test_cap_dung_va_chu_go_that_giu_nguyen`, `test_byte_utf8_hong_…`, `test_chuyen_muc_the_…` (2), `test_bai_da_dang_…`, `test_bai_nhap_vua_tao_…`, `test_anh_vua_tai_…`, `test_loi_wordpress_…` |
| **Yêu cầu 2.** `_positive_id` có giới hạn | **Đạt** ở mọi chỗ dùng `_positive_id`: bảng biên (1, `MAX_ID`, `MAX_ID+1`, 2⁶⁴, 10³⁰, 0, −1, `True`, `1.0`, `"5"`, `None`). Mã bài `MAX_ID` tạo nháp và đặt ảnh đại diện được (đường `/posts/9223372036854775807` qua danh sách đường); `MAX_ID+1`, 2⁶⁴, 10²⁵: câu cố định không chép mã, không lệnh nào gọi tiếp, không ghi SEO được cho mã đó. Ảnh đại diện mã quá biên: chặn trước khi gửi. Chuyên mục `[MAX_ID]` gửi được, `[MAX_ID+1]`, `[5, 2⁶⁴]`, `[0]` chặn trước khi gửi (đường «Gửi nháp»). Ảnh mã quá biên: 1 lệnh tải, câu «có thể đã lên thư viện Media»; ảnh `MAX_ID`: ghi đè đúng ảnh. **Danh sách bài đã đăng chưa có giới hạn: SL-T091-2** | `test_positive_id_bien` (11), `test_ma_bai_bang_bien_…`, `test_ma_bai_qua_bien_…` (3), `test_anh_dai_dien_ma_qua_bien_…` (2), `test_chuyen_muc_gui_di_theo_bien` (4), `test_anh_ma_qua_bien_…` (2), `test_anh_ma_bang_bien_…`, `test_bai_da_dang_ma_bang_bien_…` |
| **Yêu cầu 3.** SL-T059-1 | **Đạt.** Đọc lại mã WordPress lõi: `_sanitize_text_fields`, `wp_pre_kses_less_than`, `esc_html` (`_wp_specialchars` ENT_QUOTES, không mã hóa hai lần), `wp_strip_all_tags`, `update_metadata` (`wp_unslash`). Bản Python của client khớp bản của tôi với mọi chữ `_seo_text` cho qua. 300 chữ ngẫu nhiên từ bảng ký tự dễ bị đổi (`<`, `%`, chữ hex, `\`, nháy, `&`, `>`): 86 bị app chặn trước khi gửi, 214 gửi; 144 SiteSEO lưu y nguyên, 3 đổi mà hiện như cũ (`&lt;`), 67 mất ký tự (báo «tự bỏ vài ký tự»); **0 ca báo sai**. 16 chữ chọn sẵn đều đúng. 13 câu trả lời khác cách SiteSEO lưu (`&amp;lt;`, `&#60;`, bỏ «<», thừa dấu cách, thêm chữ, `R&amp;D`, `&#x27;`, `%` còn sót, cắt bớt, «/» thay «\», rỗng, «>» thành `&gt;`): đều «chưa ghi». Mô tả, từ khóa cũng theo bản lưu. Đường meta dự phòng vẫn so từng chữ (có ca đối chứng ghi được) | `test_siteseo_luu_kieu_nao_app_cung_bao_dung` (16), `test_siteseo_luu_nhieu_chu_ngau_nhien`, `test_tra_loi_khac_cach_siteseo_luu_van_la_chua_ghi` (13), `test_mo_ta_tu_khoa_cung_theo_ban_luu` (2), `test_duong_du_phong_meta_van_so_tung_chu` (2) |
| **Yêu cầu 4.** `unfiltered_html` | **Đạt**: chỉ `true` (kiểu bool) là có quyền; `false`, thiếu, `1`, `"true"`, `[true]`, `null`, `capabilities` là danh sách, `null`, chữ: không có quyền, có câu cảnh báo cố định (không chép tên site, tên tài khoản có mồi). Các quyền khác không đổi theo. Kiểm tra kết nối vẫn chỉ `GET`. `ConnectionInfo` tạo kiểu cũ 7 đối số vẫn chạy (mặc định chưa có quyền, có câu nhắc) | `test_quyen_unfiltered_html` (10), `test_quyen_unfiltered_html_khong_doi_…`, `test_connection_info_tao_kieu_cu_van_duoc` |
| **Yêu cầu 5.** Nơi gọi | Grep `app/`, `seo_app/`, `scripts/` (cả nhập muộn): `check_connection` chỉ `app/views/wordpress.py:55` (giữ `ConnectionInfo` trong `st.session_state`, trường mới có mặc định); `_json`, `_positive_id`, `_ability_confirms`, `_siteseo_saved_form`, `_siteseo_lost_text`, `_without_lone_surrogates` chỉ trong `client.py`. `_seo_text` vẫn nhập muộn `seo_app.onpage.meta` (`normalize_meta`, `_ENTITY`): `main` mới sửa `meta.py` (T-090), nên chạy thêm mọi file test của `normalize_meta`/`_seo_text` trên bản gộp | Mục «Test liên quan» |
| Không đụng `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible` | **Đạt**: `git diff 1b45f5d..7965f2b` không có dòng nào chứa ba tên này | Lệnh tay |

## Soát R5 (test cũ đã đổi theo phương án A)

Đối chiếu `git diff 1b45f5d..7965f2b -- tests/` với điều kiện duyệt: chỉ đổi phần ghim câu báo, mã cụ thể; giữ trang không lỗi, nút khóa, «đang gửi», 1 bài, 1 lệnh tải ảnh, không gọi tiếp với mã quá lớn, câu báo «có thể đã có trên website / thư viện».

| # | Ca | Kết quả |
|---|---|---|
| 1 | `test_soi_loi_t054.py::test_ma_anh_qua_lon_bi_danh_sach_duong_chan` | **Đạt.** Giữ đúng 1 lệnh `POST /media` (không gọi tiếp); đổi `uploaded == [10¹⁹]` thành `uploaded == ()`, `maybe_uploaded is True`; thêm câu có «thư viện Media», không có mã; thêm tham số 2⁶³; thêm ca biên `MAX_ID` |
| 2 | `test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` | **Bị nới: SL-T091-3.** Giữ 1 lệnh tải; câu «có thể đã lên thư viện Media», «Media → Thư viện» có kiểm; nhưng mất 5 phần kiểm «không chép» của `assert_says_in_media_library` |
| 3–4 | `test_soi_loi_t089.py::test_post_id_far_out_of_range_fixed_note[2^64]`, `[10^30]` (+ `[2^63]` mới) | **Đạt.** Giữ: trang không lỗi (`ui.send` → `run_ok`), 2 lần chạy lại nút vẫn khóa, `pending` («đang gửi»), 1 bài. Đổi `NOTE`/«mã {id}» thành `UNSURE` («bài nháp có thể đã có trên website»), không thông báo thành công nào có mã; **thêm** không request nào chứa mã đó |
| 5–7 | `test_soi_loi_t089.py::test_post_id_out_of_range_interrupted_at_each_write[1..3]` | **Đạt.** Giữ `fired`, nút khóa 2 lần, `pending`, không còn `_wp_sending`, 1 bài; `NOTE` thành `UNSURE`; **thêm** không request nào chứa 2⁶³ |
| 8 | `test_t059_siet_ghi_seo_va_srcset.py::test_khuon_khac_khuon_that_la_chua_ghi[dau-nho-hon-bi-doi]` | **Đạt** (Chỉ Huy duyệt riêng): ca cũ ghim đúng lỗi SL-T059-1; ca mới `&amp;lt;` (khác cách SiteSEO) vẫn là «chưa ghi», còn ý nghĩa vì bản lưu SiteSEO của tiêu đề đó là `&lt;` |
| — | Gỡ dấu `xfail`: `test_soi_loi_t088.py` (3 dấu, 8 ca SL-T088-1), `test_soi_loi_t059.py` (1 dấu, 5 ca SL-T059-1) | **Đạt**: chỉ xóa dòng dấu, thân test không đổi; 13 ca qua |

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, chép thêm file test của tôi; không đụng worktree), gỡ từng chỗ sửa của T-091 trong `client.py` rồi chạy 7 file: `tests/test_soi_loi_t091.py` (của tôi), `tests/test_t091_don_client_wordpress.py` (Thợ Máy), `tests/test_soi_loi_t088.py`, `tests/test_soi_loi_t059.py`, `tests/test_t059_siet_ghi_seo_va_srcset.py`, `tests/test_wordpress_t085.py`, `tests/test_soi_loi_t054.py` (18:58–19:15). Bản không gỡ: 1160 qua, 8 xfail. Script `mutate091.py` (thư mục ghi chú chung).

| Đột biến | Số test hỏng: Soi Lỗi / các file khác |
|---|---|
| N1 bỏ thay surrogate | 13 / 9 (SL-T088 8, Thợ Máy 1) |
| N2 chỉ thay ở chữ, bỏ qua tên khóa | 0 → **1** / 1 (lượt đầu tôi không bắt; thêm `test_json_doc_ve_khong_con_surrogate_o_ten_khoa_moi_tang`, chạy lại bắt được) |
| N3 bỏ surrogate thay vì thay «�» | 13 / 4 |
| N4 dò mã thoát chỉ `\ud[89ab]` chữ thường | 2 / 1 |
| N5 bỏ giới hạn `MAX_ID` | 12 / 6 |
| N6 `MAX_ID = 2**64 − 1` | 3 / 6 |
| N7 lệch biên (`< MAX_ID`) | 4 / 4 |
| N8 không so bản lưu SiteSEO (như trước T-091) | 15 / 10 |
| N9 nhận mọi chữ `html.unescape` về đúng chữ gửi (máy chủ chọn được chữ) | 14 / 7 |
| N10 `'` thành `&#x27;` thay vì `&#039;` | 3 / 2 |
| N11 bỏ vòng xóa `%xx` | 6 / 6 |
| N12 bỏ `stripslashes` | 5 / 5 |
| N13 không bao giờ báo «tự bỏ ký tự» | 10 / 2 |
| N14 luôn báo «tự bỏ ký tự» | 9 / 5 |
| N15 đoán cả đoạn «< … >» | 0 → **1** / 1 (thêm câu trả lời `&gt;` không phải của SiteSEO, chạy lại bắt được) |
| N16 `unfiltered_html` nhận giá trị «truthy» (`1`, `"true"`) | 3 / 2 |
| N17 `can_unfiltered_html` mặc định `True` | 1 / 1 |
| N18 không đọc `unfiltered_html` | 1 / 1 |

**18/18 đột biến bị bắt**; sau khi thêm 2 ca, test của tôi bắt đủ 18.

## Ghi nhận (không xếp lỗi)

1. **Còn một ca nhỏ của SL-T059-1:** chữ có cả đoạn «< …» không có «>» lẫn đoạn «< … >» (ví dụ «Giá < 5 triệu, cổng < 3m > 2m»). SiteSEO lưu `Giá &lt; 5 triệu, cổng < 3m > 2m`, còn app không đoán (`_siteseo_saved_form` trả `None`) nên báo «không thành công» dù đã ghi. Đây là hướng an toàn, rất hiếm; có ca trong `CURATED` ghi lại hành vi này. Thợ Máy đã nêu ở Rủi ro 2.
2. **Mã chuyên mục, thẻ đọc từ website:**
   - `_list_terms` nhận mã `0` và mã lớn hơn `MAX_ID` (chỉ chặn `< 0`).
   - Trang Kết nối WordPress gọi thẳng `create_draft(categories=…)`. Hàm này không kiểm mã chuyên mục, nên mã đó được gửi đi nguyên; chỉ `create_draft_with_images` («Gửi nháp») kiểm bằng `_is_term_ids`. Có từ trước, website tự từ chối mã lạ.
   - Câu báo khi chuyên mục sai là `_DRAFT_BAD_PART` («Nội dung bài chỉ được gồm các đoạn HTML…»), sai nghĩa.
   - Nên xét khi T-102 nối chuyên mục thật.
3. `unfiltered_html` từ REST là quyền của **vai trò**: site bật `DISALLOW_UNFILTERED_HTML` hay multisite thì REST vẫn báo `true` mà WordPress vẫn lọc (Thợ Máy đã nêu, Rủi ro 4). Lượt thử thật vẫn phải xem nguồn trang có `srcset`.
4. `ConnectionInfo` tạo không có `can_unfiltered_html` (mặc định `False`) thì `unfiltered_html_status` có câu cảnh báo. Họa Sĩ nối giao diện cần nhớ: chỉ hiện câu này với kết quả `check_connection` thật.

## Test liên quan

Máy Windows của chủ dự án.

```
# nhánh team/T-091 (7965f2b) + file của tôi (bản cuối, 98 ca)
$ uv run pytest -q -p no:cacheprovider tests/test_soi_loi_t091.py
90 passed, 8 xfailed in 4.30s

# 7 file đột biến (của tôi, Thợ Máy T-091, SL-T088, T-059 x2, T-085, T-054), bản sao nhánh
1160 passed, 8 xfailed in 69.41s

# bản gộp tạm T-091 + main d1506cb (git merge-tree: không xung đột; commit tạm, không đẩy)
# 67 file (10.351 ca): mọi file nhắc client WordPress, site giả, SiteIndexStore, seo_write_problem,
# siteseo_copy, _seo_text, normalize_meta (main mới sửa meta.py ở T-090), cùng test T-090
lượt 1 (17:39–18:37, dừng ở 88% vì giới hạn giờ của lệnh): 9153 passed, 16 xfailed, 2 skipped, 0 failed
lượt 2 (10 file còn lại, chạy lại cả file đang dở): 1190 passed, 17 xfailed in 113.22s

$ uv run ruff check .
All checks passed!
```

Xfail đều là dấu có sẵn (8 của tôi; còn lại có từ trước trên `main`, như Lá Chắn T-090). Không XPASS, không hỏng: gộp T-091 với `main` mới không làm vỡ gì (T-090 sửa `normalize_meta` mà `_seo_text` dùng). Bản gộp chạy với file của tôi lúc còn 96 ca; 2 ca thêm sau lượt đột biến (tên khóa JSON, `&gt;`) chỉ dùng code nhánh, đã qua ở lượt cuối trên nhánh.

## Đề xuất

- **Thợ Máy (lượt 2 hay phiếu dọn sau):**
  - SL-T091-1: dò surrogate trên chữ đã giải mã, hoặc luôn đi qua dữ liệu.
  - SL-T091-2: `PublishedItem` có `MAX_ID`; `SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError`.
  - SL-T091-3: trả 5 dòng kiểm «không chép» vào ca của `test_wordpress_t085.py`.
  - Gỡ 8 dấu `xfail` khi sửa.
- **T-102 (Họa Sĩ):** khi nối chuyên mục thật, xét Ghi nhận 2.
- **Lá Chắn (rút gọn W2, W3):** xét SL-T091-1 cùng mức SL-T088-1.

# Báo cáo T-091 · Dọn client WordPress sau T-059

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-091](../tickets/T-091-don-client-wordpress-sau-t059.md) |
| Ngày nộp | 2026-10-28 16:20 (giờ máy, +07) |
| Kết quả | Hoàn thành (chờ Soi Lỗi rút gọn, Lá Chắn rút gọn W2, W3) |

## Tóm tắt (cho chủ dự án)

- **Chữ lạ từ website không còn làm vỡ trang:** nếu website trả về tên site, tiêu đề bài… có một loại ký tự hỏng (surrogate lẻ), phần mềm thay nó bằng dấu «�» ngay khi nhận, nên trang Kết nối WordPress và bộ nhớ tạm danh sách bài không còn lỗi.
- **Ghi SEO báo đúng hơn:** khi tiêu đề, mô tả SEO có «< » (ví dụ «Giá < 5 triệu»), SiteSEO lưu thành `&lt;` (trên trang vẫn hiện «<»). Trước đây app báo «không thành công» dù đã ghi; nay báo «Đã ghi». Nếu SiteSEO tự **bỏ mất** ký tự (ví dụ «10%BE» thành «10», hay dấu «\»), app báo «Đã ghi, nhưng SiteSEO tự bỏ vài ký tự, mở hộp SiteSEO xem lại».
- **Kiểm tra kết nối biết thêm một quyền của tài khoản WordPress** (đăng HTML không lọc). Thiếu quyền này thì WordPress bỏ phần giữ ảnh 1600 px khi lưu bài (điện thoại có thể tải ảnh thu nhỏ đã mất GPS). Phần mềm đã có câu cảnh báo sẵn; hiện câu đó trên trang Kết nối WordPress là việc của Họa Sĩ.
- Mã bài, mã ảnh website trả về có giới hạn trên; số lớn bất thường bị coi là dữ liệu hỏng.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | (1) `_json` thay mọi surrogate lẻ trong JSON website trả (chữ và tên khóa, mọi tầng) bằng «�» (`_without_lone_surrogates`, đi bằng ngăn xếp, chỉ chạy khi thân câu trả lời có mã thoát `\uD800`…`\uDFFF`). (2) `MAX_ID = 2**63 - 1`, `_positive_id` nhận tối đa `MAX_ID`. (3) `_ability_confirms` nhận thêm đúng bản SiteSEO 1.4.2 lưu (`_siteseo_saved_form`: `wp_unslash(sanitize_text_field(chữ))`, không đoán chắc thì `None`); `_seo_via_abilities` báo `_SEO_WRITTEN_CHANGED` khi SiteSEO bỏ mất ký tự (`_siteseo_lost_text`). (4) `ConnectionInfo.can_unfiltered_html` (mặc định `False`) + `unfiltered_html_status` (câu cảnh báo cố định); `check_connection` đọc `capabilities.unfiltered_html is True`. Không đụng `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible` (diff: 0 dòng chạm ba tên này) |
| `tests/test_t091_don_client_wordpress.py` (mới) | 52 test: surrogate (tên site, tài khoản, địa chỉ ảnh thay chứ không bỏ, tên khóa, lồng 5.000 tầng, emoji hợp lệ giữ nguyên, chữ «\ud800» thật giữ nguyên, không có mã thoát thì không đi qua dữ liệu); `MAX_ID`; bản lưu SiteSEO (14 ca), không đoán (3 ca), `stripslashes`; ghi SEO đầu cuối với chữ lưu **cố định** (không dùng lại hàm của client); `unfiltered_html` (6 ca) |
| `tests/test_soi_loi_t088.py` | Gỡ 3 dấu `xfail` SL-T088-1 (8 ca XPASS), chỉ xóa dòng dấu |
| `tests/test_soi_loi_t059.py` | Gỡ 1 dấu `xfail` SL-T059-1 (5 ca XPASS), chỉ xóa dòng dấu |
| `tests/test_t059_siet_ghi_seo_va_srcset.py`, `tests/test_soi_loi_t054.py`, `tests/test_wordpress_t085.py`, `tests/test_soi_loi_t089.py` | 8 ca cũ đổi kỳ vọng và thêm ca biên, Chỉ Huy B duyệt phương án A ngày 28/10 (bảng «Test cũ đã đổi» bên dưới) |

### Test cũ đã đổi (Chỉ Huy B duyệt phương án A ngày 2026-10-28, R5)

Lý do chung của 7 ca đầu: yêu cầu 2 («mã quá lớn như mã sai khuôn», lớp phòng thêm của LC-T086-1) làm client không còn đưa mã bài, mã ảnh lớn hơn 2⁶³−1 ra ngoài; các ca này ghim **câu chữ và mã cụ thể** của hành vi cũ (mã quá lớn đi qua client). Chỉ đổi phần ghim đó. Không nới ý nào: trang không lỗi; nút khóa, giữ «đang gửi»; chỉ 1 bài trên website; chỉ 1 lệnh tải ảnh, không tải lại; không lệnh nào gọi tiếp với mã quá lớn (nay có kiểm thêm); câu báo nói rõ «có thể đã có trên website / đã lên thư viện».

| # | Ca | Điều kiện cũ | Điều kiện mới | Biên 2⁶³−1 / 2⁶³ |
|---|---|---|---|---|
| 1 | `test_soi_loi_t054.py::test_ma_anh_qua_lon_bi_danh_sach_duong_chan` (mã ảnh 10¹⁹) | `uploaded == [10**19]` (client nhận mã, lệnh ghi alt bị danh sách đường chặn); chỉ 1 lệnh `POST /media` | `uploaded == ()`, `maybe_uploaded is True`, câu báo có «thư viện Media», không có mã; vẫn chỉ 1 lệnh `POST /media` (như ca «mã sai kiểu» `test_tai_anh_tra_du_lieu_sai_kieu_thi_dung`) | Thêm tham số `2^63` (như sai khuôn); thêm `test_ma_anh_bang_gioi_han_van_nhan` (2⁶³−1: ghi alt `POST /media/9223372036854775807`, tạo nháp, ảnh đúng mã) |
| 2 | `test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` (mã ảnh 10²⁰) | `assert_says_in_media_library(…, media_id=10**20)`: câu có «mã ảnh 100000000000000000000» | Câu có «có thể đã lên thư viện Media» và «Media → Thư viện», không có mã; vẫn chỉ 1 lệnh `POST /media` (lệnh ghi đè không bao giờ gửi) | Thêm tham số `2^63`; thêm `test_ma_anh_bang_gioi_han_van_ghi_de_binh_thuong` (2⁶³−1: ghi đè đúng ảnh đó) |
| 3–4 | `test_soi_loi_t089.py::test_post_id_far_out_of_range_fixed_note[2^64]`, `[10^30]` | Cảnh báo `NOTE` («mã bài nháp lớn bất thường…») và thông báo thành công có «mã {post_id}» | Lỗi có `UNSURE` («bài nháp có thể đã có trên website»); không thông báo thành công nào có mã đó; **thêm**: không request nào chứa mã đó. Giữ nguyên: 2 lần chạy lại nút vẫn khóa, `pending`, 1 bài | Thêm tham số `[2^63]`; biên 2⁶³−1 có sẵn: `test_largest_post_id_still_recorded` (không đổi, vẫn qua) |
| 5–7 | `test_soi_loi_t089.py::test_post_id_out_of_range_interrupted_at_each_write[1]`, `[2]`, `[3]` (mã 2⁶³) | Cảnh báo `NOTE` | Lỗi có `UNSURE`; **thêm**: không request nào chứa mã 2⁶³. Giữ nguyên: ngắt đúng lúc ghi khóa thứ n vẫn xảy ra (`fired`), nút khóa, `pending`, không còn `_wp_sending`, 1 bài | Đã có cả hai biên trong file |
| 8 | `test_t059_siet_ghi_seo_va_srcset.py::test_khuon_khac_khuon_that_la_chua_ghi[dau-nho-hon-bi-doi]` (test T-059 của tôi) | Chữ lưu `&lt;` (đúng cách SiteSEO lưu «<») là «chưa ghi»: đây **chính là lỗi SL-T059-1** phiếu này sửa | Chữ lưu `&amp;lt;` (mã hóa hai lần, khác cách SiteSEO) vẫn «chưa ghi», giữ ý «biến đổi khác SiteSEO thì chưa ghi»; dạng `&lt;` đúng có test «đã ghi» ở `tests/test_t091_don_client_wordpress.py` | — |

## Cách làm từng yêu cầu

**Yêu cầu 1 (SL-T088-1).** Mọi chữ client lấy từ website đi qua đúng một hàm `WordPressClient._json` (đọc JSON); `_error_from` cũng đọc JSON nhưng chỉ lấy `code` dạng ASCII (`_ERROR_CODE`), surrogate không lọt qua được. JSON chỉ tạo được surrogate lẻ từ mã thoát `\uD800`…`\uDFFF` (UTF-8 hợp lệ không chứa chúng; cặp đúng như emoji được bộ đọc JSON ghép thành một ký tự), nên chỉ đi qua dữ liệu khi thân câu trả lời có mã thoát dạng đó. **Thay** bằng «�» thay vì bỏ: bỏ thì «a\ud800.webp» thành «a.webp», có thể là địa chỉ của một ảnh khác. Mã thực thể HTML `&#xD800;` (qua `_plain`) thì `html.unescape` của Python đã đổi thành «�» từ trước.

**Yêu cầu 2.** `MAX_ID = 2⁶³−1` (SQLite, PHP 64 bit). `_positive_id` dùng cho mã bài (`_post_from`), mã ảnh (`_post_media`, `upload_media`, `_describe_draft_media`, `set_featured_image`), danh sách chuyên mục/thẻ (`_is_term_ids`): lớn hơn thì như mã sai khuôn (câu báo «không đúng dạng»; tải ảnh, tạo nháp thì kèm «có thể đã lên thư viện / bài nháp có thể đã có»). Vì vậy mã lớn không bao giờ vào `_created_post_ids` hay một lệnh gọi tiếp (trước đây mã 19 chữ số từ 2⁶³ tới 10¹⁹−1 vẫn khớp mẫu đường `_ID` của `ALLOWED_ROUTES`).

**Yêu cầu 3 (SL-T059-1).** Chọn «so theo bản đã chuẩn hóa như SiteSEO» (cách 1 của phiếu), vì 5 test của Soi Lỗi đòi `set_seo_meta` không ném lỗi; chặn trước khi gửi sẽ chặn cả «Giá < 5 triệu» (rất hay gặp trong tiêu đề) mà chữ đó hiện y như cũ trên trang. `_siteseo_saved_form` chép `sanitize_text_field` (`wp_pre_kses_less_than`: đoạn «<…» không có «>» thì `esc_html` với `&#039;` như PHP; gộp khoảng trắng; vòng bỏ «%» + 2 ký tự hex; gộp dấu cách nếu có bỏ) rồi `stripslashes` (`update_metadata` gọi `wp_unslash`). **Không đoán** (trả `None`, chỉ nhận khớp từng chữ như cũ) khi có đoạn «< … >» (`strip_tags` của PHP; hai bản giả lập của Soi Lỗi ở T-059 và T-060 cho kết quả khác nhau ở ca này, nên không dựa vào), hay «<» không có khoảng trắng ngay sau. Bản lưu tính trên máy từ chữ đã gửi, nên máy chủ không làm app tin một chữ tùy ý. Phạm vi: chỉ đường Abilities; đường dự phòng `_seo_via_meta` giữ so khớp từng chữ (cách site lọc khóa meta không biết trước).

**Yêu cầu 4.** REST `users/me?context=edit` trả `capabilities` là `allcaps` của vai trò. Thiếu `unfiltered_html` thì chắc chắn WordPress lọc bài (kses bỏ `srcset`, T-059). Có quyền thì vẫn có thể bị tắt bởi `DISALLOW_UNFILTERED_HTML` hay multisite (`map_meta_cap`), REST không cho biết: ghi trong chú thích của `ConnectionInfo`; lượt thử thật vẫn phải xem nguồn trang.

**Yêu cầu 5.** Nơi gọi (kể cả nhập muộn): `check_connection` chỉ có `app/views/wordpress.py` (trường mới có mặc định, `ConnectionInfo(...)` 7 đối số cũ vẫn chạy); `_json`, `_positive_id`, `_ability_confirms` chỉ dùng trong `client.py`; `seo_app/onpage/meta.py` dùng `_seo_text` (không đổi). Chạy mọi file test nhắc tới client WordPress, site giả, `SiteIndexStore`, `seo_write_problem`, `siteseo_copy` (mục «Bằng chứng»).

## Bằng chứng

Máy Windows của chủ dự án, worktree `wt-T-091` (nhánh `team/T-091` từ `main` `1b45f5d`).

```
$ uv run pytest -q -p no:cacheprovider <61 file test liên quan>   # toàn bộ test do Chỉ Huy chạy khi gộp
9311 passed, 1 skipped, 7 xfailed in 1684.25s (0:28:04)

$ uv run pytest -q -p no:cacheprovider tests/test_t091_don_client_wordpress.py tests/test_soi_loi_t088.py tests/test_soi_loi_t059.py tests/test_t059_siet_ghi_seo_va_srcset.py
687 passed in 94.98s (0:01:34)          # trước khi đổi 7 ca của phương án A; 13 ca đổi/thêm: 13 passed

$ uv run ruff check .
All checks passed!
```

61 file: mọi file trong `tests/` nhắc tới `seo_app.wordpress`, `fake_wordpress`, `WordPressClient`, `ConnectionInfo`, `site_index`/`SiteIndexStore`, `seo_write_problem`, `siteseo_copy`, cùng file mới. Trước khi gỡ dấu: 13 ca `xfail` (8 SL-T088-1, 5 SL-T059-1) báo `XPASS(strict)`. Lượt đầu (trước phương án A): 8 hỏng = 7 ca ở bảng «Test cũ đã đổi» và `test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (đo khóa luồng, máy bận; chạy riêng: `1 passed`; lượt sau cùng qua). 7 `xfail` và 1 bỏ qua còn lại có từ trước, không thuộc phiếu.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `client.py` `_json` + `_without_lone_surrogates`; 8 ca SL-T088-1 XPASS, đã gỡ dấu.
- [x] Yêu cầu 2: `MAX_ID`, `_positive_id`; `test_positive_id_gioi_han_tren`, `test_ma_bai_qua_lon_bi_tu_choi_nhu_ma_sai`.
- [x] Yêu cầu 3: `_siteseo_saved_form`, `_ability_confirms`, `_SEO_WRITTEN_CHANGED`; 5 ca SL-T059-1 XPASS, đã gỡ dấu.
- [x] Yêu cầu 4: `ConnectionInfo.can_unfiltered_html`, `unfiltered_html_status` (giao diện: Họa Sĩ).
- [x] Yêu cầu 5: test cũ qua; 8 ca đổi kỳ vọng theo đúng việc sửa, Chỉ Huy B duyệt (bảng «Test cũ đã đổi»).
- [x] Không sửa `app/**`, `config/**`; giữ `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`.
- [x] Ruff sạch.

## Rủi ro và điểm cần chú ý

1. **8 ca test cũ đổi kỳ vọng** (bảng «Test cũ đã đổi», Chỉ Huy B duyệt A ngày 28/10): yêu cầu 2 và SL-T059-1 đổi đúng hành vi mà các ca đó ghim. Không xóa, không bỏ qua test nào (R5); mọi ý an toàn giữ nguyên, có ca kiểm thêm «không request nào chứa mã quá lớn». Đổi lại, giao diện không còn hiện con số mã bài/ảnh lạ website trả: người dùng chỉ biết «bài nháp có thể đã có / ảnh có thể đã lên thư viện» và tự kiểm trong trang quản trị. Đường xử lý mã lớn trong `app/views/write.py` (LC-T086-1, câu `MSG_POST_ID_OUT_OF_RANGE`) vẫn còn, nay là lớp thứ hai.
2. **Bản Python của `sanitize_text_field` chỉ đúng cho chữ app gửi** (`_seo_text` đã chặn thẻ, mã ký tự HTML, «<» liền chữ, ký tự điều khiển). Chỗ không chắc trả `None`, quay về so khớp từng chữ: lệch thì app báo «không thành công» (chiều an toàn như trước), không bao giờ báo «đã ghi» sai. Bản SiteSEO sau đổi cách lưu thì cũng chỉ rơi về «không thành công».
3. **Nhận «đã ghi» khi SiteSEO bỏ mất ký tự** («10%BE» thành «10»): chữ trên site khác chữ người dùng gõ. App báo rõ để người dùng xem lại; không tự ghi lại.
4. `unfiltered_html` từ REST là quyền của vai trò, chưa phải quyền thật cuối cùng (yêu cầu 4). Câu cảnh báo chỉ hiện khi **thiếu** quyền; có quyền mà site tắt bằng `DISALLOW_UNFILTERED_HTML` thì app không biết.

## Đề xuất

- **Họa Sĩ (phiếu riêng):** trang Kết nối WordPress hiện `info.unfiltered_html_status` (khi khác rỗng) bằng widget chữ thường, cạnh dòng `siteseo_status`; bước SEO hiện `SeoWriteResult.message` như hiện có (câu mới `_SEO_WRITTEN_CHANGED` là chữ cố định, không chép chữ người dùng).
- **Lượt thử thật kế tiếp (Chỉ Huy):** ghi một tiêu đề có «< 5 triệu» lên bài nháp, app phải báo «Đã ghi»; xem nguồn trang thẻ `<title>` hiện «<» đúng.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-28): sửa theo Soi Lỗi `2ff1425`, Lá Chắn `ed5d86b`

Chỉ Huy B giao 28/10 20:45. Sửa 4 việc theo cột «Cách sửa» của `T-091-la-chan.md` và `T-091-soi-loi.md`; không đổi thư viện, không gọi website thật.

### Tóm tắt (cho chủ dự án)

- Chữ hỏng từ website nay bị thay bằng «�» trong mọi trường hợp, kể cả khi website gửi chữ theo bảng mã khác thường (UTF-16, UTF-32…), nên trang không vỡ.
- Danh sách bài đã đăng bỏ qua mục có mã bài lớn bất thường thay vì làm lỗi bước SEO.
- Hai test cũ ghim câu báo «mã bài nháp lớn bất thường» được đổi sang câu báo mới «bài nháp có thể đã có trên website», vẫn kiểm đủ: 1 bài, nút khóa, «đang gửi».

### Đã thay đổi

| Việc | File | Thay đổi |
|---|---|---|
| **SL-T091-1** (surrogate lọt khi bảng mã khác UTF-8) | `seo_app/wordpress/client.py` `_json` (`:1551`) | Lọc **luôn** trên dữ liệu đã giải mã: `return _without_lone_surrogates(response.json())`. Bỏ phép tắt «byte không có mã thoát `\uD8..` thì không đi qua dữ liệu» (`_SURROGATE_ESCAPE` đã xóa): với `charset=utf-16/utf-32/utf-7/cp500`, hay website không khai bảng mã mà `requests` tự đoán UTF-16/32, surrogate không hiện thành mã thoát trong byte. Bộ lọc đi bằng ngăn xếp, một lượt, rẻ |
| **SL-T091-2** (mã bài đã đăng > 2⁶³−1) | `PublishedItem.__post_init__` (`:546`), `_published_from` (`:1658`) | `PublishedItem` chỉ nhận mã `_positive_id` (1 … `MAX_ID`); `_published_from` đưa `_positive_id(raw["id"])` vào, mã quá biên thành `None` → `PublishedItem` từ chối → mục bị bỏ, đúng đường «mã sai khuôn». `SiteIndexStore.save` không còn gặp số quá biên. Lớp phòng thêm Lá Chắn nêu (`SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError`) ở `seo_app/storage/site_index.py`, ngoài phạm vi phiếu: chưa làm, ghi «Đề xuất» |
| **LC-T091-1** (2 test cũ hỏng) | `tests/test_t089_send_draft.py` `assert_huge_id_reported_and_locked` | Bảng «Test cũ đã đổi (lượt 2)» bên dưới |
| **SL-T091-3** (ca T-085 mất 5 kiểm) | `tests/test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` | Trả lại đủ 5 kiểm «câu báo không chép»: `0909`, `evil`, `quản trị</b>`, `example.com`, `anh-khac` (như `assert_says_in_media_library`) |
| Gỡ dấu `xfail` | `tests/test_soi_loi_t091.py` (dấu `_SL1` 5 ca SL-T091-1, dấu 3 ca SL-T091-2), `tests/test_la_chan_t091.py` (dấu 18 ca SL-T091-1) | 26 ca đều `XPASS(strict)` trước khi gỡ; **chỉ xóa dòng dấu** (gồm dòng định nghĩa `_SL1` và `@_SL1`), không đổi điều kiện ca nào |

### Test cũ đã đổi (lượt 2, Chỉ Huy duyệt 28/10)

| # | Ca | Điều kiện cũ | Điều kiện mới | Lý do |
|---|---|---|---|---|
| 9–10 | `tests/test_t089_send_draft.py::test_huge_post_id_fixed_note_and_lock`, `::test_huge_post_id_when_run_interrupted` (mã 2⁶³, cảnh mở bài `ui.open_article`; chung hàm `assert_huge_id_reported_and_locked`) | Cảnh báo `NOTE` («website trả mã bài nháp lớn bất thường…») và thông báo thành công có «mã {HUGE_ID}» | Lỗi có `UNSURE` («bài nháp có thể đã có trên website»); không thông báo thành công nào có mã 2⁶³; **thêm**: không request nào chứa mã đó. **Giữ nguyên:** 1 bài trước và sau, nháp giữ «đang gửi», nút khóa ngay và qua 2 lần chạy lại; ca bị ngắt vẫn kiểm `_wp_sending` đã bỏ và `UNSURE` | LC-T091-1, **Chỉ Huy duyệt 28/10** theo đúng mẫu phương án A (cùng kiểu ca 3–7 lượt 1). Hằng `NOTE` để nguyên trong file (không còn dùng ở đây) |
| 11 | `tests/test_t091_don_client_wordpress.py::test_khong_co_ma_thoat_surrogate_thi_khong_di_qua_du_lieu` (ca của tôi, lượt 1) → `test_luon_loc_sau_khi_giai_ma_du_byte_khong_co_ma_thoat` | Không có mã thoát trong byte thì `_without_lone_surrogates` không được gọi (ghim phép tắt tối ưu) | Mọi câu trả lời JSON đều qua bộ lọc sau khi giải mã (≥ 2 lần trong `check_connection`); chữ sạch giữ nguyên | SL-T091-1: cách sửa trong biên bản Lá Chắn (Chỉ Huy giao theo cách đó 28/10) bỏ phép tắt; biên bản ghi rõ ca này phải đổi. Ca ghim một phép tối ưu, không phải tính chất an toàn |
| (2) | `tests/test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` | Lượt 1 bỏ mất 5 kiểm «không chép» | Trả lại 5 kiểm (chặt lại như trước phương án A) | SL-T091-3 |

### Bằng chứng (lượt 2)

Máy Windows của chủ dự án, worktree `wt-T-091` (nhánh `team/T-091`, đầu `ed5d86b` trước lượt 2), 2026-10-28 21:49 (+07).

```
$ uv run pytest -q tests/test_soi_loi_t091.py tests/test_la_chan_t091.py <ca đã đổi>   # trước khi gỡ dấu
26 failed, 152 passed      # 26 «failed» đều là XPASS(strict): 5 + 3 Soi Lỗi, 18 Lá Chắn; ca đã đổi đều qua

$ uv run pytest -q -p no:cacheprovider <72 file test liên quan>   # sau khi gỡ dấu; toàn bộ do Chỉ Huy chạy khi gộp
1 failed, 10544 passed, 4 skipped, 10 xfailed in 3538.55s (0:58:58)
FAILED tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted   # đo khóa luồng, máy bận

$ uv run pytest -q tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted
1 passed in 39.81s

$ uv run ruff check .
All checks passed!
```

72 file = 61 file client WordPress của lượt 1, mọi file có số lớn hay câu «lớn bất thường» (`2**63`, `2**64`, `10**19`, `10**20`, `10**30`, `HUGE_ID`, `MAX_ID`, `MSG_POST_ID_OUT_OF_RANGE`, `PublishedItem`, `_published_from`: 34 file), `tests/test_t089_send_draft.py`, `tests/test_t086_send_state.py`, `tests/test_soi_loi_t091.py`, `tests/test_la_chan_t091.py`. Ca T-037 hỏng oan khi máy bận (lượt 1 và Lá Chắn cũng gặp), chạy riêng qua. 10 `xfail`, 4 bỏ qua có từ trước, thuộc phiếu khác (không còn dấu `xfail` nào của T-091). Không còn chỗ nào dùng `_SURROGATE_ESCAPE` (grep `seo_app`, `app`, `tests`).

### Đề xuất (lượt 2)

- **Phiếu dọn sau (Thợ Máy, cần mở phạm vi `seo_app/storage/site_index.py`):** `SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError` (lớp phòng thêm của SL-T091-2, Lá Chắn nêu).
- Ghi nhận 1, 3 của Lá Chắn (nếu Chỉ Huy muốn) gom cùng phiếu dọn client WordPress sau.

# Biên bản bảo mật T-091 · Dọn client WordPress sau T-059 · rút gọn (W2, W3)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-091](../tickets/T-091-don-client-wordpress-sau-t059.md) (code Thợ Máy `7965f2b`, test Soi Lỗi `2ff1425`) |
| Phạm vi | **Rút gọn: W2, W3** và 8 việc Chỉ Huy giao. Diff `1b45f5d..2ff1425`: `seo_app/wordpress/client.py` (`_json` + `_without_lone_surrogates`, `MAX_ID`/`_positive_id`, `_ability_confirms` + `_siteseo_saved_form`, `_siteseo_lost_text`, `ConnectionInfo.can_unfiltered_html`), 4 file test cũ đổi (8 ca, phương án A), 2 file gỡ dấu `xfail`, 2 file test mới |
| Ngày | 2026-10-28 (Chỉ Huy giao 19:20; làm 19:38 → 20:38 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **chưa gộp `main` được ngay**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **4 Thấp**: 1 của Lá Chắn (**LC-T091-1**, soát R5: 2 test cũ trong `tests/test_t089_send_draft.py` ghim hành vi mã bài 2⁶³ nay **hỏng** trên nhánh; không nằm trong 8 ca Chỉ Huy duyệt; Thợ Máy và Soi Lỗi không chạy tới file này) và 3 của Soi Lỗi giữ mức Thấp (SL-T091-1, -2, -3; SL-T091-1 rộng hơn Soi Lỗi ghi: lọt cả khi website **không khai** bảng mã). **Phải sửa trước khi gộp: LC-T091-1** (đổi kỳ vọng 2 ca theo đúng mẫu phương án A, Chỉ Huy duyệt theo R5; đã thử trên bản sao: phần mềm vẫn giữ 1 bài, nút khóa, «đang gửi»); nên làm luôn SL-T091-3. Thêm 18 ca `xfail(strict=True)` cho dạng lọt mới của SL-T091-1 (`tests/test_la_chan_t091.py`). Không sửa code ứng dụng |

## Tóm tắt (cho chủ dự án)

Phần dọn client WordPress **an toàn**, nhưng **chưa gộp được ngay**: 2 bài kiểm tra cũ (của phần «Gửi nháp») vẫn chờ app báo câu cũ khi website trả mã bài lớn vô lý, nên nay báo hỏng. Phần mềm làm đúng (tôi đã thử: vẫn chỉ 1 bài nháp, nút gửi vẫn khóa); chỉ cần sửa lại 2 bài kiểm tra đó, có Chỉ Huy duyệt. Tôi kiểm 4 việc bằng phép thử riêng:

- **Chữ hỏng từ website** (surrogate lẻ) nay thành dấu «�», trang không vỡ. Website WordPress thật luôn gửi chữ UTF-8 nên luôn được lọc. Chỉ website bị chiếm hay plugin hỏng gửi chữ kiểu bảng mã khác mới còn lọt; hậu quả là trang báo lỗi, không lộ gì, không ghi gì lên website.
- **Mã bài, mã ảnh lớn vô lý** không bao giờ đi vào lệnh gọi tiếp theo, không làm tạo bài trùng (vẫn đúng 1 bài, nút gửi vẫn khóa).
- **Báo «Đã ghi SEO» khi chữ có «< »:** app chỉ chấp nhận đúng 2 dạng chữ do chính app tính từ chữ đã gửi, nên website không thể dụ app báo «đã ghi» cho một chữ khác. Tôi thử 20.000 chữ: 0 ca báo sai.
- **Quyền `unfiltered_html`:** app chỉ đọc quyền có sẵn, không xin thêm quyền, câu cảnh báo cố định (không chép tên website, tên tài khoản), khớp dòng sổ rủi ro bạn duyệt sáng 28/10.
- 3 lỗi nhỏ Soi Lỗi tìm ra giữ mức Thấp. **Việc của bạn:** không có.

## Lỗi phát hiện

Số dòng theo `2ff1425`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T091-1 | Thấp (không phải lỗ hổng); **chặn gộp** vì làm đỏ bộ test | **Soát R5: 2 test cũ hỏng, chưa được duyệt đổi.** `test_huge_post_id_fixed_note_and_lock` và `test_huge_post_id_when_run_interrupted` (LC-T086-1, T-089) dùng `HUGE_ID = 2**63` và đòi câu `NOTE` («website trả mã bài nháp lớn bất thường…») cùng thông báo thành công «mã {HUGE_ID}». Yêu cầu 2 của phiếu làm client coi 2⁶³ là mã sai khuôn, nên hai ca hỏng ngay ở dòng kiểm `NOTE`; các kiểm an toàn phía sau (1 bài, «đang gửi», nút khóa qua 2 lần chạy lại) **không còn được chạy** trong cảnh của chúng. File có từ gốc `1b45f5d`, `main` không đổi nó; không có trong 61 file Thợ Máy chạy, 67 file Soi Lỗi chạy, không có trong 8 ca phương án A | `tests/test_t089_send_draft.py:73-107` (`assert_huge_id_reported_and_locked` `:73-82`) | Chạy riêng trên nhánh (20:28): **2 failed**; trên cây gộp: cùng 2 ca hỏng. Hai ca cùng kiểu với ca 3–7 Chỉ Huy đã duyệt (`test_soi_loi_t089.py`, cảnh `ui.ready_image`), khác cảnh mở bài (`ui.open_article`) | Đổi kỳ vọng **đúng mẫu phương án A**, Chỉ Huy duyệt (R5): `NOTE` → `UNSURE` trong `at.error`; bỏ đòi «mã {HUGE_ID}» trong thông báo thành công, thay bằng không thông báo thành công nào có mã đó và không lệnh nào chứa mã đó; **giữ nguyên** 1 bài, «đang gửi», nút khóa 2 lần chạy lại. Đã thử trên bản sao (20:35): **2 passed** |

Xếp mức 3 lỗi của Soi Lỗi (việc 6):

| Mã | Soi Lỗi | Lá Chắn | Đường đi thật (đầu vào → hậu quả) | Sửa trước |
|---|---|---|---|---|
| SL-T091-1 | Thấp | **Thấp, giữ; rộng hơn** | `_json` (`client.py:1541-1558`) chỉ lọc khi **byte** trả về có mã thoát ASCII `\uD8..`–`\uDF..` (`_SURROGATE_ESCAPE`, `:1890`), còn `response.json()` giải mã theo bảng mã `requests` chọn. Soi Lỗi: `charset=utf-16`, `utf-32`, `utf-7`, `cp500` lọt. Lá Chắn thêm: website **không khai** bảng mã (không `Content-Type`, hay `application/octet-stream`, `application/problem+json`) mà trả JSON UTF-16, UTF-32 (có hay không BOM) thì `requests` tự đoán (`guess_json_utf`) và giải mã đúng: lọt (18 ca `xfail`, 6 ca đối chứng: UTF-8 khai hay không khai đều sạch; khai `application/json` không `charset` thì `requests` dùng UTF-8, JSON hỏng, câu cố định). WordPress thật luôn trả `application/json; charset=UTF-8`, nên chỉ website bị chiếm, plugin hỏng hay kẻ nghe lén có chứng chỉ được máy tin (sổ rủi ro 2026-10-28) gây ra; hậu quả là trang lỗi (`UnicodeEncodeError`), lưu SQLite lỗi; không lộ, không ghi | Phiếu dọn sau. Cách sửa gọn nhất: **luôn** gọi `_without_lone_surrogates` (một lượt duyệt, rẻ). Đã thử trên bản sao: 23/23 `xfail` (5 Soi Lỗi + 18 Lá Chắn) thành XPASS; chỉ `test_khong_co_ma_thoat_surrogate_thi_khong_di_qua_du_lieu` của Thợ Máy (ghim phép tắt «không có mã thoát thì không duyệt») phải đổi: R5, Chỉ Huy duyệt. Dò trên `response.text` thì chưa chắc (`text` đoán bảng mã theo cách khác `json()`) |
| SL-T091-2 | Thấp | **Thấp, giữ** | `PublishedItem.__post_init__` (`client.py:546`) không có trần `MAX_ID`, `_published_from` (`:1644`) không dùng `_positive_id` → mã bài đã đăng > 2⁶³−1 làm `SiteIndexStore.save` ném `OverflowError` (không phải `SiteIndexError`) → bước SEO lỗi trang. Chỉ website bị chiếm trả được (PHP không biểu diễn được số nguyên đó). Chỉ là lỗi trang: mã này không đi vào đường gọi nào (danh sách bài dùng `link`, không dựng đường từ mã) | Phiếu dọn sau. Đã thử: thêm `<= MAX_ID` vào `PublishedItem`: 3/3 `xfail` thành XPASS, không test nào hỏng. Thêm lớp phòng: `SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError` |
| SL-T091-3 | Thấp | **Thấp, giữ** | Soát R5: ca `test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` bỏ mất 5 kiểm «câu báo không chép lời máy chủ, địa chỉ website» (`0909`, `evil`, `quản trị</b>`, `example.com`, `anh-khac`) của `assert_says_in_media_library`. Phương án A chỉ cho đổi phần ghim câu báo, mã cụ thể. Phần mềm vẫn đúng: test mới của Soi Lỗi `test_anh_ma_qua_bien_chi_mot_lenh_va_cau_bao_khong_chep_gi` canh cùng tính chất (S2), nên lúc gộp không hở | Nên trả 5 dòng ngay ở lượt sửa kế tiếp của nhánh (chỉ sửa test). Gộp trước thì Chỉ Huy ghi lại vào phiếu dọn |

## Kết quả theo việc Chỉ Huy giao

**1. Chữ website không đi xuyên client làm vỡ chỗ khác: đạt với UTF-8, trừ SL-T091-1 (Thấp).**

- Mọi chữ client lấy từ website đi qua `_json`; `_error_from` (`:1561`) chỉ lấy `code` dạng ASCII (`_ERROR_CODE`), surrogate không lọt được. Không chỗ nào đọc `response.text` (grep).
- Script `probe_t091.py surrogate` (thư mục nháp, không commit): tên site, tên khóa có surrogate, UTF-8 có khai hay không khai: sạch. 900 tầng lồng: 0,02 s; 200.000 surrogate trong một chữ: 0,11 s; hai tên khóa trùng nhau sau khi thay: không lỗi; khóa không phải chữ giữ nguyên; chữ «\ud800» gõ thật (6 ký tự) giữ nguyên.
- Đồng ý cách **thay** bằng «�» (không bỏ): bỏ thì `a\ud800.webp` thành `a.webp`, có thể là ảnh khác trên website. W3: địa chỉ ảnh có «�» vẫn qua `is_site_link`, `figure_html` (`_SRC_UNSAFE`, `html.escape` không đổi) nên chỉ là ảnh hỏng trong bài nháp, không chèn được gì.

**2. Mã quá lớn không lọt vào lệnh gọi tiếp, không tạo bài trùng: đạt.**

- Mọi mã website trả mà sau đó thành đường gọi hay vào `_created_post_ids` đều qua `_positive_id` (`:1876`, `0 < mã ≤ MAX_ID`): `_post_from` (`:1475-1491`) → `create_draft` chỉ ghi nhận bài site xác nhận là nháp (`:959`); `_post_media` (`:1243`) → lệnh ghi đè `/wp/v2/media/{mã}` (`:1190`) và `_describe_draft_media` (`:1457`); `set_featured_image` đòi bài trong `_created_post_ids` và mã ảnh qua `_positive_id` (`:1105-1110`); `set_seo_meta` đòi bài trong `_created_post_ids` (`:986`).
- `probe_t091.py ma`: tạo nháp trả mã 2⁶³, 2⁶⁴, 10³⁰ → câu cố định không chép mã, `_created_post_ids` rỗng; gọi tiếp `set_seo_meta`, `set_featured_image` với mã đó: bị từ chối trước khi gửi; cả lượt chỉ **1** lệnh (lệnh tạo bài), không lệnh nào mang mã. Biên `MAX_ID`: nhận.
- Không tạo bài trùng: 5 ca test đã đổi (`test_soi_loi_t089.py`, chạy trang thật bằng `AppTest`) vẫn kiểm 1 bài trên website, nút «Gửi nháp» khóa qua 2 lần chạy lại, nháp giữ «đang gửi»; thêm kiểm không lệnh nào chứa mã đó. Cảnh mở bài của `test_t089_send_draft.py` (LC-T091-1): hai ca đang hỏng ở dòng kiểm câu cũ; đổi kỳ vọng theo mẫu A trên bản sao thì cũng giữ đủ 1 bài, nút khóa, «đang gửi».
- Mẫu đường `_ID` (`:64`) vẫn nhận số 19 chữ số tới 10¹⁹−1 (lớn hơn `MAX_ID`): không đường nào đưa mã như vậy vào (Ghi nhận 1).

**3. SL-T059-1: cách so mới không làm «đã ghi» thành đúng khi chưa ghi: đạt.**

- `_ability_confirms` (`:1934-1969`) nhận một trường chỉ khi `post.<trường>` **đúng từng chữ** với chữ đã gửi, hoặc với `_siteseo_saved_form(chữ đã gửi)` (`:1990`). Cả hai tính **trên máy** từ chữ app gửi (`fields` của `_seo_via_abilities`, `:1047-1060`, đúng chữ trong thân lệnh); câu trả lời của máy chủ không đi vào phép tính. Muốn app báo «đã ghi», máy chủ phải trả lại đúng một trong hai chữ đó kèm `updated: true`, không `code`, `success` không khác `true`. Trước T-091 máy chủ vốn đã trả lại được đúng chữ đã gửi, nên không có đường mới để giả xác nhận.
- Bản giả lập sai với chữ nào đó thì chữ SiteSEO thật lưu khác chữ giả lập: app báo «chưa ghi» (chiều an toàn). Chỗ không đoán chắc (đoạn «< … >») trả `None`, chỉ nhận khớp từng chữ.
- `probe_t091.py xacnhan`: 20.023 chữ (23 chọn sẵn + 20.000 ngẫu nhiên từ bảng ký tự dễ bị đổi: `<`, `>`, `%`, chữ hex, `\`, nháy, `&`, `;`, `#`, tab, chữ Việt). 5.979 bị `_seo_text` chặn trước khi gửi, 13.955 gửi. Với mỗi chữ gửi: đúng chữ và bản SiteSEO lưu được nhận; 30 dạng khác (`&#60;`, `&#x3c;`, `&LT;`, mã hóa hai lần, bỏ «<», «%», «\», «/» thay «\», NFD, NBSP, U+200B, đổi hoa thường, thừa, thiếu dấu cách, cắt bớt…) bị từ chối; kiểu lạ (danh sách, dict, bytes, `None`, `0`, `True`) bị từ chối, không lỗi lạ; khóa trạng thái sai bị từ chối. **0 hỏng**. «SiteSEO tự bỏ vài ký tự» báo đúng khi và chỉ khi `html.unescape(chữ lưu) != chữ gửi` (4.374 ca). Chạy lại trên cây gộp với `main`: cùng kết quả.
- Shortcode: SiteSEO bỏ «%xx», «\» khi lưu không ghép được shortcode từ chữ app cho qua, vì `_SHORTCODE_OPEN` (`:299`) coi «[» liền «%» hay «\» là đầu shortcode và chặn trước khi gửi (T-061). Đường dự phòng `_seo_via_meta` vẫn so từng chữ.

**4. `unfiltered_html`: đạt, khớp sổ rủi ro.**

- `check_connection` vẫn chỉ 3 lệnh `GET` như trước (`/`, `/wp/v2/users/me?context=edit`, ability SiteSEO); chỉ thêm đọc `capabilities.unfiltered_html is True` (`:799`). Không xin quyền, không ghi gì. `probe_t091.py quyen`: `true` mới là có quyền; `false`, thiếu, `1`, `"true"`, `[true]`, tên khóa có surrogate: không. Mọi lệnh là `GET` tới đúng 3 đường đó. Câu cảnh báo là hằng (`:465-474`), không chép tên site, tên tài khoản (đã gài mồi).
- Sổ rủi ro mục 6, dòng 2026-10-28: tài khoản Biên tập viên mặc định có `unfiltered_html`, cách giữ GPS dựa vào quyền này, «không cấp thêm quyền cho tài khoản». Câu cảnh báo chỉ hiện khi **thiếu** quyền và khuyên dùng vai trò Biên tập viên (vai trò ghi trong `security.md` 2.2), không khuyên Quản trị viên hay cấp quyền lẻ: khớp. REST trả quyền theo vai trò, nên `DISALLOW_UNFILTERED_HTML` hay multisite vẫn có thể lọc bài mà app không biết (Ghi nhận 2).

**5. 8 ca test đã đổi: 7 ca đúng điều kiện duyệt, 1 ca bị nới (SL-T091-3); thêm 2 ca cũ hỏng chưa đổi (LC-T091-1).** Tôi tìm mọi file test có số lớn (`2**63`, `2**64`, `10**19`…, «lớn bất thường», `MSG_POST_ID_OUT_OF_RANGE`, `HUGE_ID`): 16 file; 6 file ngoài lượt chạy cây gộp được chạy thêm trên nhánh cùng `test_t089_send_draft.py`, `test_t086_send_state.py` (8 file, 20:29–20:35): 1.108 passed, 3 skipped, 3 xfailed, **2 failed** (đúng 2 ca LC-T091-1).

| # | Ca | Giữ đủ điều kiện duyệt? |
|---|---|---|
| 1 | `test_soi_loi_t054.py::test_ma_anh_qua_lon_bi_danh_sach_duong_chan` (10¹⁹, thêm 2⁶³) | **Có.** Vẫn đúng 1 lệnh `POST /media`; đổi `uploaded == [mã]` thành `uploaded == ()`, `maybe_uploaded is True`; thêm câu có «thư viện Media», không chép mã; thêm ca biên `MAX_ID` |
| 2 | `test_wordpress_t085.py::test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien` (10²⁰, thêm 2⁶³) | **Không trọn: SL-T091-3.** Giữ 1 lệnh tải, câu «có thể đã lên thư viện Media», «Media → Thư viện», không chép mã; mất 5 kiểm «không chép» |
| 3–4 | `test_soi_loi_t089.py::test_post_id_far_out_of_range_fixed_note[2^64]`, `[10^30]` (thêm `[2^63]`) | **Có.** Giữ trang không lỗi, nút khóa 2 lần chạy lại, «đang gửi», 1 bài; `NOTE` thành `UNSURE`; thêm: không thông báo thành công có mã, không lệnh nào chứa mã |
| 5–7 | `test_soi_loi_t089.py::test_post_id_out_of_range_interrupted_at_each_write[1..3]` | **Có.** Giữ `fired`, nút khóa, «đang gửi», không còn `_wp_sending`, 1 bài; thêm không lệnh nào chứa 2⁶³ |
| 8 | `test_t059_siet_ghi_seo_va_srcset.py::test_khuon_khac_khuon_that_la_chua_ghi[dau-nho-hon-bi-doi]` | **Có** (ca T-059, Chỉ Huy duyệt cùng phương án A): ca cũ ghim đúng lỗi SL-T059-1; ca mới `&amp;lt;` (khác cách SiteSEO lưu) vẫn là «chưa ghi» |
| — | Gỡ dấu `xfail`: `test_soi_loi_t088.py` (3 dấu, 8 ca), `test_soi_loi_t059.py` (1 dấu, 5 ca) | **Đúng R5:** chỉ xóa dòng dấu, thân test không đổi |

**6. 3 lỗi Thấp của Soi Lỗi: không lỗi nào cần nâng mức** (bảng «Lỗi phát hiện»).

**7. Thử gộp với `main` mới nhất trên máy: không xung đột; 2 ca hỏng là LC-T091-1 (có sẵn trên nhánh), không do gộp.** `git merge-tree --write-tree main team/T-091` với `main` `24013b3` (T-096 lượt 4, T-097, T-098, T-090) → cây `45c0894`, **không xung đột**, hai bên không chung file. Chỗ dính nhau: `main` đổi `normalize_meta` (T-090) mà `_seo_text` dùng; chạy lại `probe_t091.py` trên cây gộp: cùng 167.401 ca, 0 hỏng. Test trên cây gộp (giải nén vào thư mục nháp, `seo_app` nạp từ cây gộp), 35 file: mọi file client WordPress, ghi SEO, «Gửi nháp», ảnh trong bài, bài đã đăng, trang Kết nối, `_seo_text`/`normalize_meta` (T-041, T-090), 19:45–20:27: **4.982 passed, 25 xfailed, 3 failed**. 25 xfail = 17 LC-T090-1, -2 có sẵn trên `main` + 8 SL-T091. 3 hỏng: 2 ca LC-T091-1 (hỏng y như trên nhánh) và `test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (đo khóa luồng; chạy riêng trên cây gộp: qua; Thợ Máy cũng gặp khi máy bận): hỏng oan.

**8. Biên bản, test, commit:** biên bản này; `tests/test_la_chan_t091.py` (18 `xfail(strict=True)` + 6 đối chứng); commit lên `team/T-091`, không gộp `main`.

## Danh sách kiểm tra (rút gọn)

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| W2 | Đạt | Không thêm đường ghi nào; ghi đè ảnh vẫn chỉ cho ảnh website vừa xác nhận tạo (`201`); mã bị chặn trên (`MAX_ID`) nên không ghi được vào mã lạ; `_seo_via_meta` không đổi; không xóa gì |
| W3 | Đạt | Không đụng đường dựng HTML (`sanitize_html`, `figure_html`, `escape_shortcodes`); `git diff 1b45f5d..7965f2b` không có dòng nào chạm `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`; chữ mới (`_SEO_WRITTEN_CHANGED`, `unfiltered_html_status`) là hằng |
| S2 (liên quan) | Đạt | Câu báo mới không chép lời máy chủ, tên site, tên tài khoản, mã (probe có mồi); SL-T091-3 là test yếu đi, phần mềm vẫn đúng |
| D3 (liên quan) | Đạt | Test mới dùng site giả hay dựng thẳng `requests.Response`; bộ chặn mạng của `tests/conftest.py` không đổi |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 (`PYTHONUTF8=1`) | 6 kết quả trên các file của phiếu: `client.py:704` (chú thích về địa chỉ có tên, mật khẩu), mật khẩu giả trong 4 file test | Cả 6 dòng có sẵn ở gốc `1b45f5d` (T-091 không thêm); file mới (`test_t091_don_client_wordpress.py`, `test_soi_loi_t091.py`, `test_la_chan_t091.py`): 0 |
| bandit 1.9.4 | `seo_app/wordpress/client.py`: 0 | |
| ruff | `uv run ruff check .`: sạch | |
| pytest | `tests/test_la_chan_t091.py`: 6 passed, 18 xfailed (`--runxfail`: 18 ca hỏng đúng lý do surrogate lọt). Nhánh, 9 file của phiếu (2 file test mới, file của tôi, 4 file test đổi, 2 file gỡ dấu: `test_soi_loi_t091.py`, `test_t091_don_client_wordpress.py`, `test_la_chan_t091.py`, `test_soi_loi_t054.py`, `test_wordpress_t085.py`, `test_soi_loi_t089.py`, `test_t059_siet_ghi_seo_va_srcset.py`, `test_soi_loi_t088.py`, `test_soi_loi_t059.py`), 20:05–20:21: **1.211 passed, 26 xfailed, 0 hỏng** (26 xfail = 18 Lá Chắn + 8 Soi Lỗi). Thêm 8 file có số lớn: 2 failed (LC-T091-1). Cây gộp 35 file: 4.982 passed, 25 xfailed, 3 failed (việc 7) | Máy bận (test toàn bộ của Chỉ Huy chạy song song) nên chậm; ca T-037 hỏng oan đã chạy lại riêng |
| Script dò độc lập | `probe_t091.py`: **167.401 ca, 0 hỏng** trên nhánh (19:46) và trên cây gộp (19:48) | Tự chặn socket ở dòng đầu |

## Sửa mẫu (chỉ trên bản sao, không commit)

Bản sao nhánh (`git archive HEAD` + file test của tôi): `_json` luôn gọi `_without_lone_surrogates`; `PublishedItem` nhận `0 < mã ≤ MAX_ID`. Chạy 7 file (`test_la_chan_t091.py`, `test_soi_loi_t091.py`, `test_t091_don_client_wordpress.py`, `test_soi_loi_t088.py`, `test_wordpress_t088.py`, `test_wordpress_client.py`, `test_wordpress_published.py`), 19:51–19:52: **26 XPASS(strict)** (18 + 5 SL-T091-1, 3 SL-T091-2), 896 passed, 1 hỏng: `test_khong_co_ma_thoat_surrogate_thi_khong_di_qua_du_lieu` (ghim phép tắt, xem SL-T091-1).

## Ghi nhận (không xếp lỗi)

1. **Mẫu đường `_ID`** (`client.py:64`, 1–19 chữ số) nhận cả số từ 2⁶³ tới 10¹⁹−1. Không đường nào đưa mã như vậy vào (việc 2). Nên (lớp phòng thêm): `is_allowed_route` so thêm giá trị số `≤ MAX_ID`.
2. **REST trả quyền theo vai trò** (`allcaps`): `DISALLOW_UNFILTERED_HTML` hay multisite làm WordPress vẫn lọc bài dù `unfiltered_html` là `true` (Rủi ro 4 Thợ Máy, Ghi nhận 3 Soi Lỗi). Lượt thử thật vẫn phải xem nguồn trang bài nháp có `srcset`.
3. **Chữ SEO có «\0»** (dấu «\» rồi số 0) qua được `_seo_text`; SiteSEO lưu thành ký tự NUL (`wp_unslash`). App báo đúng «SiteSEO tự bỏ vài ký tự»; trình duyệt hiện NUL thành «�». Không phải lỗi bảo mật; nếu muốn gọn thì `_seo_text` chặn cặp «\0».
4. `create_draft` (trang Kết nối) không kiểm mã chuyên mục, thẻ; `_list_terms` nhận mã 0 và mã > `MAX_ID` (Ghi nhận 2 Soi Lỗi): mã chỉ nằm trong thân lệnh, không dựng đường; website tự từ chối mã lạ. Xét khi T-102 nối chuyên mục thật.
5. Họa Sĩ nối giao diện: hiện `info.unfiltered_html_status` bằng chữ thường, chỉ với kết quả `check_connection` thật (`ConnectionInfo` dựng kiểu cũ mặc định là chưa có quyền, Ghi nhận 4 Soi Lỗi).
6. Nút tạo bài nháp thử ở trang Kết nối WordPress gọi thẳng `create_draft`: website trả mã bài sai khuôn (nay gồm cả mã > `MAX_ID`) thì câu `_BAD_DATA` («… không đúng dạng. Thử lại sau…», `client.py:323`) không nói bài nháp có thể đã được tạo, nên bấm lại có thể ra thêm một bài nháp thử. Có từ trước với mọi mã sai khuôn; chỉ website hỏng hay bị chiếm mới trả như vậy; chỉ là bài nháp. «Gửi nháp» ở Soạn bài đã có câu «bài nháp có thể đã có trên website» và khóa nút. Nên (phiếu dọn): dùng câu kiểu đó cho lệnh tạo bài.

## Điều kiện

0. **Trước khi gộp (bắt buộc), LC-T091-1:** Chỉ Huy duyệt (R5) đổi kỳ vọng 2 ca `tests/test_t089_send_draft.py` (`assert_huge_id_reported_and_locked`) theo đúng mẫu phương án A (cột «Cách sửa» ở trên), Thợ Máy hay Họa Sĩ (chủ file T-089) sửa; chạy lại cả file. Chỉ sửa test, không đụng code. Lá Chắn xem lại diff test (rút gọn).
1. **SL-T091-3:** trả 5 dòng kiểm «không chép» vào ca của `tests/test_wordpress_t085.py`, nên làm cùng lượt với điều kiện 0 (chỉ sửa test).
2. **Phiếu dọn client WordPress sau (Thợ Máy):** SL-T091-1 (luôn đi qua dữ liệu; đổi test ghim phép tắt theo R5, Chỉ Huy duyệt; gỡ 23 dấu `xfail`: 5 Soi Lỗi, 18 Lá Chắn), SL-T091-2 (`PublishedItem` có `MAX_ID`, `SiteIndexStore.save` đổi `OverflowError` thành `SiteIndexError`; gỡ 3 dấu `xfail`); cân nhắc Ghi nhận 1, 3.
3. **Họa Sĩ:** Ghi nhận 5 khi nối câu cảnh báo `unfiltered_html` vào trang Kết nối WordPress.
4. **Lượt thử thật kế tiếp:** ghi tiêu đề có «< 5 triệu» lên bài nháp: app báo «Đã ghi», nguồn trang hiện «<» đúng; nguồn trang ảnh có `srcset` (Ghi nhận 2).

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 4 Thấp (LC-T091-1 mới; SL-T091-1 → -3 giữ Thấp). Phần mềm an toàn về W2, W3. **Chưa gộp `main` được ngay:** phải đổi kỳ vọng 2 ca test cũ của LC-T091-1 (có duyệt R5) trước khi gộp; sau đó gộp được, không cần Lá Chắn kiểm lại code.

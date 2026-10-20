# Báo cáo T-054 · Soi Lỗi: gửi nháp kèm ảnh (tải ảnh, chèn `<figure>`)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-054](../tickets/T-054-chen-anh-vao-nhap-wordpress.md) |
| Ngày nộp | 2026-10-20 (giờ máy, +07) |
| Kết quả | Hoàn thành |
| Kết luận | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn được. Không có lỗi Cao hay Nghiêm trọng. 3 lỗi: SL-T054-2 Trung bình (trùng phiếu T-061), SL-T054-1 và SL-T054-3 Thấp |

## Tóm tắt (cho chủ dự án)

- Phần "Gửi nháp kèm ảnh" làm đúng 4 yêu cầu của phiếu: file gửi lên website **giống hệt từng byte** file app đã nén (GPS tới web đúng từng con số, kể cả ảnh điện thoại 4032 px thu về 1600 px); tên file chỉ lấy từ thẻ và alt, không có tên thư mục, tên file gốc, tên khách; chữ độc trong alt/chú thích chỉ còn là chữ; bài luôn là **nháp**, ảnh đại diện chỉ đặt vào đúng bài nháp app vừa tạo; lỗi giữa chừng thì báo đủ ảnh đã lên thư viện và **không xóa gì**.
- Tìm được 3 lỗi, không lỗi nào làm lộ khóa, đăng bài hay xóa dữ liệu:
  - **SL-T054-1 (Thấp):** alt/chú thích của **ảnh AI** mà AI viết mở đầu bằng `[…]:` còn dấu `\` thừa khi lên website.
  - **SL-T054-2 (Trung bình, trùng T-061):** chữ dạng shortcode (`[code_snippet id=1]`) trong alt/chú thích đi thẳng vào bài nháp. Đây là rủi ro đã biết, phiếu T-061 đang lo; phải xong trước khi bật nút Gửi nháp.
  - **SL-T054-3 (Thấp):** website trục trặc đúng lúc tạo bài (hết giờ, lỗi máy chủ, trả lời sai) thì bài nháp **có thể đã được tạo**, nhưng thông báo không nói, lại bảo "Thử lại sau": thử lại sẽ ra nháp trùng và tải lại toàn bộ ảnh.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t054.py` | Mới: 30 hàm test, 116 trường hợp (110 qua, 6 `xfail(strict=True)` cho SL-T054-1…3). Site giả, ảnh giả tạo trong bộ nhớ, không mạng |
| `docs/team/reports/T-054-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test cũ. Commit trên `team/T-054`: `a9167b6` (test), và commit báo cáo.

## Bằng chứng

```
$ uv run pytest -q -p no:cacheprovider tests/test_soi_loi_t054.py
110 passed, 6 xfailed in 6.30s          (Windows 11, tại a9167b6)

$ uv run pytest -q -p no:cacheprovider tests/test_soi_loi_t054.py tests/test_wordpress_images.py \
    tests/test_app_wordpress.py tests/test_images_process.py tests/test_safety.py \
    tests/test_sanitize.py tests/test_sanitize_autolink.py tests/test_sanitize_bypass.py \
    tests/test_sanitize_hardening.py tests/test_site_index_t042.py tests/test_soi_loi_t042.py \
    tests/test_soi_loi_t042_paging_cache.py tests/test_soi_loi_t042_round2.py \
    tests/test_wordpress_client.py tests/test_wordpress_paging_t042.py \
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py \
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py \
    tests/test_wordpress_site_link_t042.py
KET_QUA_CHAY_LIEN_QUAN

$ uv run ruff check .
All checks passed!
```

Không chạy toàn bộ `uv run pytest` (Chỉ Huy chạy khi gộp). Mỗi `xfail` đã chạy lại với `--runxfail` để chắc nó hỏng **đúng vì lỗi** (không phải vì test viết sai): 6/6 hỏng ở đúng dòng kiểm lỗi (`\` còn trong alt; `[code_snippet` còn trong bài; câu báo không nhắc bài nháp có thể đã có).

## Đối chiếu yêu cầu và điều kiện

**Yêu cầu 1. Chỉ tải ảnh khi gọi gửi nháp; lỗi giữa chừng liệt kê media đã tải, không xóa (W2).** Đạt.
- Chỉ `create_draft_with_images` tải ảnh (`client.py:932-1035`), không đi qua `upload_media` (cài `upload_media` ném lỗi mà luồng vẫn chạy). Dựng `DraftImage`, `figure_html`, kiểm trước (`_plan_draft_images`) không gửi request nào: `test_chuan_bi_anh_khong_goi_mang_va_khong_qua_upload_media`. Việc chỉ gọi hàm khi người dùng bấm là của T-056.
- Danh sách `parts` bị sửa trong lúc đang gửi không ảnh hưởng (chốt `tuple(parts)`, `client.py:973`): `test_danh_sach_parts_bi_doi_trong_luc_gui_khong_anh_huong`.
- Lỗi ở từng bước × 401/403/404/500 (20 trường hợp, `test_loi_http_o_tung_buoc`): tải ảnh, ghi alt, tạo nháp → `DraftImagesError` có đúng danh sách ảnh đã lên, đúng `status_code`, `maybe_uploaded` chỉ bật khi đang tải mà máy chủ lỗi 5xx; chưa tạo nháp khi lỗi trước bước tạo. Kiểm nháp, đặt ảnh đại diện → không ném lỗi, trả bài kèm câu "chưa đặt được ảnh đại diện"; kiểm nháp lỗi thì không có lệnh ghi. Mật khẩu giả (cả có/không dấu cách) và chuỗi `Authorization` base64 không xuất hiện trong câu báo nào.
- Mất mạng ở ảnh thứ 10/12: liệt kê đủ 9 ảnh (mã, địa chỉ), nhắc ảnh thứ 10 có thể đã lên, không tạo nháp (`test_mat_mang_o_anh_thu_muoi_liet_ke_du_chin_anh_khong_xoa`).
- Không bao giờ có lệnh ngoài `GET`/`POST` trong mọi test (không có `DELETE`, không có hàm xóa).

**Yêu cầu 2. Byte gửi lên đúng `WebImage.data`, còn GPS (Lá Chắn T-049 điều kiện 4).** Đạt.
- Ảnh kiểu điện thoại 4032×3024, GPS **Nam/Tây** có độ cao → `make_web_image` thật → 1600×1200 → byte website nhận **bằng** `web.data`; đọc lại độc lập: `S`, `W`, vĩ độ, kinh độ, độ cao đúng từng phân số; `<img width="1600" height="1200">` khớp file (`test_anh_lon_kieu_dien_thoai_gps_nam_tay_den_web_dung_tung_gia_tri`; code gửi `item.source.image.data`, `client.py:986-988`).
- Ảnh gốc có tên khách, đường dẫn thư mục, tên file gốc, số seri máy, tên chủ máy trong EXIF (ImageDescription, Artist, Copyright, XPComment UTF-16, BodySerialNumber, CameraOwnerName): không chữ nào (UTF-8 lẫn UTF-16) có mặt trong byte ảnh, header, đường gọi hay JSON của **mọi** lệnh gửi đi; GPS vẫn còn (`test_byte_va_moi_lenh_gui_di_khong_co_ten_khach_ten_file_goc`).
- Hai `DraftImage` dùng chung một `WebImage`: gửi 2 lần, cả hai đúng byte, tên và alt đúng từng ảnh.
- Tên file **chỉ** từ `naming.image_file_name` (`client.py:1074`): bọc hàm này để ghi lại, tên trong `Content-Disposition` đúng bằng giá trị hàm trả; hàm chỉ nhận `category`, `area`, `project_code`, `alt` (đã gỡ ký tự ngắt), `ai_generated`, `taken` (`test_ten_file_chi_lay_tu_image_file_name`). Thẻ có `"`, xuống dòng, `../`, `%2e`, `<script>`, đường dẫn Windows, ký tự đảo chiều: header luôn đúng khuôn `attachment; filename="[a-z0-9-]+.webp"` (7 trường hợp).

**Yêu cầu 3. `<figure>` dựng bằng code, alt/chú thích đã gỡ ký tự ngắt và escape Markdown rồi mới escape HTML, qua `sanitize_html` lần cuối (Lá Chắn T-050 điều kiện 4, T-046 số 7).** Đạt, trừ SL-T054-1 và SL-T054-2.
- 12 kiểu chữ độc làm cả alt lẫn chú thích (`test_alt_chu_thich_doc_chi_con_la_chu`): thẻ HTML, dấu nháy đơn/kép, `javascript:`, mã ký tự (`&lt;`, `&#34;`, `&#0;`), chữ AI có link/`www.`/email (đã qua `clean_ai_text`, có ký tự rộng 0), escape Markdown `]\(`, `]\[`, ký tự rộng 0 các loại, 13 ký tự hướng chữ (U+202A–202E, U+2066–2069, U+200E/F, U+061C), ký tự điều khiển, `<!--`/CDATA/`<?php`, chữ tổ hợp NFD, chữ gần 500 ký tự. Mọi trường hợp: trình duyệt chỉ thấy `p`, `figure[class]`, `img[src, alt, width, height]`, `figcaption`; alt và chú thích giải mã ra **đúng bằng** `plain_image_text(chữ)`; không còn ký tự loại Cf; `sanitize_html(nội dung) == nội dung`; `alt_text` gửi REST là chữ thường đã gỡ ký tự rộng 0; `title`, `caption` gửi REST đã escape (không còn `<`, `>`, `"` trần).
- Giới hạn độ dài tính trên chữ đã làm sạch: alt 500 ký tự kèm 5000 ký tự rộng 0 vẫn nhận, gửi đi đúng 500 ký tự; 501 ký tự, chú thích 1001 ký tự, alt toàn ký tự vô hình bị từ chối trước khi gửi gì.
- `class`: phiếu này không mở thêm (xem G6).

**Yêu cầu 4. Chỉ ghi vào nháp do app tạo, qua danh sách đường REST cố định; không `publish`/`future`.** Đạt.
- Không có cách truyền `status`, `featured_media`, `date` vào hàm (ném `TypeError`, 0 request): `test_khong_co_cach_truyen_trang_thai_hay_ngay_dang`. Lệnh tạo luôn `"status": "draft"` (`client.py:691`).
- Bọc `is_allowed_route` để ghi lại: **mọi** request gửi đi đều đã được hỏi và được cho phép, đúng thứ tự; không tham số lạ (lệnh `GET` duy nhất là kiểm nháp với `context`, `_fields`), không header ghi đè phương thức (`test_moi_lenh_deu_qua_danh_sach_duong_khong_tham_so_la`). Gỡ đường `POST /wp/v2/media/<mã>` khỏi danh sách thì lệnh đó không đi ra, ảnh đã tải vẫn được liệt kê (`test_duong_bi_go_khoi_danh_sach_thi_khong_gui`). Mã ảnh 20 chữ số bị danh sách đường chặn (`test_ma_anh_qua_lon_bi_danh_sach_duong_chan`).
- Ảnh đại diện chỉ ghi vào đúng bài vừa tạo (site trả bài 43 → `GET`, `POST` chỉ `/posts/43`, đúng mã ảnh được chọn). Site trả bài vừa tạo là `publish`, `future`, `pending`, `private` hay trạng thái rỗng → không còn lệnh nào sau lệnh tạo (`test_site_tao_bai_khong_phai_nhap_thi_khong_ghi_them`).

**WordPress giả trả dữ liệu sai kiểu, `id` lạ, `source_url` ngoài site.** Đạt (trừ SL-T054-3 về câu báo).
- Tải ảnh trả `[]`, chữ, `null`, `id` là chữ/số thực/`true`/0/âm, thiếu `id`, trang HTML: dừng, nhắc ảnh có thể đã lên, không gửi lệnh nào nữa (10 trường hợp). Ghi alt trả sai dạng hay nói về ảnh khác: dừng, liệt kê ảnh (7 trường hợp). Tạo nháp trả sai dạng: liệt kê ảnh kèm địa chỉ (4 trường hợp).
- `source_url` ngoài site (20 trường hợp: cổng khác, có tên người dùng, tên miền con giả, chữ Kirin, dấu chấm cuối tên miền, `https:` thiếu `//`, `//…`, đường tương đối, dấu nháy, ký tự rộng 0, xuống dòng, `\`, `ftp:`, `data:`, quá 2000 ký tự, số, `null`, dict, list): dừng trước khi tạo nháp, liệt kê ảnh. Dạng lạ nhưng hợp lệ (`EXAMPLE.com`, `:443`, `%22`/`?`/`&`/`#`) được nhận và vào `src` nguyên văn.

**Điều kiện Lá Chắn T-049 số 7 và T-067:** ngoài phạm vi Soi Lỗi; Chỉ Huy làm trước khi gộp (thử 3–5 ảnh thật, T-067 gộp trước).

## Lỗi tìm được

| Mã | Mức | Lỗi | Test |
|---|---|---|---|
| SL-T054-1 | Thấp | Alt/chú thích **ảnh AI** mở đầu bằng `[…]:` còn `\` khi lên website | `test_sl_t054_1_anh_ai_chu_mo_dau_ngoac_vuong_con_dau_gach_cheo` |
| SL-T054-2 | Trung bình (trùng T-061) | Shortcode trong alt/chú thích đi thẳng vào nội dung nháp | `test_sl_t054_2_shortcode_trong_chu_thich`, `test_sl_t054_2_shortcode_trong_alt` |
| SL-T054-3 | Thấp | Lỗi sau lệnh tạo nháp không báo bài nháp có thể đã được tạo | `test_sl_t054_3_loi_sau_lenh_tao_nhap_phai_bao_bai_nhap_co_the_da_co` (3 trường hợp) |

**SL-T054-1.** Vi phạm một phần điều kiện 4 của Lá Chắn T-050 (gỡ escape Markdown mà `clean_ai_text` thêm).
- Tái hiện: AI gợi ý cho ảnh AI `alt="[Trước khi sửa]: cổng sắt gỉ sét"`, `caption="[Lưu ý]: sơn lại cổng"` → `clean_suggestion(…, ai_generated=True)` → `DraftImage(…, ai_generated=True)` → gửi nháp.
- Mong đợi: alt trong bài và `alt_text` là `Minh họa [Trước khi sửa]: cổng sắt gỉ sét`; chú thích `Ảnh minh họa (AI): [Lưu ý]: sơn lại cổng`.
- Thực tế: còn `\` trước `:` ở cả `alt`, `<figcaption>`, `alt_text`, `title`, `caption` gửi REST.
- Nguyên nhân: `escape_link_syntax` chỉ thêm `\` trước `:` khi `[` ở **đầu dòng** (`sanitize.py:543`), và `unescape_link_syntax` cũng chỉ gỡ khi `[` ở đầu dòng (`sanitize.py:589`). `clean_suggestion` ghép tiền tố «Minh họa» / «Ảnh minh họa (AI):» **sau** khi đã escape (`alt.py:357-363`, `:390-392`), nên `[` không còn ở đầu dòng và `plain_image_text` (`html.py:56`) không gỡ được. Ảnh thật (không tiền tố) thì không lỗi (`test_anh_that_chu_ai_mo_dau_ngoac_vuong_khong_con_dau_gach_cheo`). Người dùng sửa alt, gõ thêm chữ trước `[…]\:` cũng ra lỗi này.
- Gợi ý (Thợ Máy chọn): `plain_image_text` gỡ `\` trong `]\:` ở mọi vị trí (chữ gửi WordPress không phải Markdown, nên bỏ dấu này không hại gì). Sửa ở `plain_image_text` thì phủ cả đường người dùng sửa tay.

**SL-T054-2.** Rủi ro đã biết (Thợ Máy T-054 mục Rủi ro, Lá Chắn T-042 LC-T042-3, phiếu T-061).
- Tái hiện: `DraftImage(web, alt="Cổng", caption="[code_snippet id=1] sơn lại")` hoặc `alt="[code_snippet id=1] cổng"` → gửi nháp.
- Mong đợi: shortcode không còn chạy được (bị thoát hay bị chặn trước khi gửi).
- Thực tế: nội dung gửi đi có nguyên `<figcaption>[code_snippet id=1] sơn lại</figcaption>` và `alt="[code_snippet id=1] cổng"`.
- Lưu ý cho T-061 (suy luận, đọc từ hiểu biết về mã WordPress, chưa thử trên site): WordPress chạy shortcode **cả trong thuộc tính HTML có dấu nháy** (`do_shortcodes_in_html_tags`), nên T-061 phải phủ cả thuộc tính `alt`, không chỉ phần chữ. Hai test tách riêng (chú thích, alt) để biết T-061 phủ được phần nào. Trường `alt_text`, `title`, `caption` của Media gửi qua REST không đi qua `sanitize_html`; WordPress mặc định không chạy shortcode ở các trường này (suy luận), T-061 nên ghi rõ đã xét.
- Không chặn chuyển Lá Chắn (không phải lỗi phiếu này sinh ra), nhưng phải xong trước khi T-056 bật nút Gửi nháp.

**SL-T054-3.**
- Tái hiện: ảnh tải xong, lệnh tạo nháp (a) trả `201` nhưng `id` là chữ `"42"`, (b) hết giờ, (c) trả `502`.
- Mong đợi: câu báo nói bài nháp **có thể đã được tạo**, dặn kiểm Bài viết → Nháp trước khi gửi lại.
- Thực tế: câu báo chỉ có lý do lỗi ("Thử lại sau…") và danh sách ảnh; tài liệu của `DraftImagesError` (`client.py:414-419`) còn ghi lỗi xảy ra "trước khi có bài nháp". Ở trường hợp (a) website đã trả `201 Created`, nghĩa là bài chắc chắn đã có. Người dùng bấm gửi lại sẽ được nháp thứ hai và một bộ ảnh công khai nữa (ảnh có GPS).
- Gợi ý: khi lỗi xảy ra ở lệnh tạo nháp mà không phải 4xx rõ ràng (hết giờ, mất mạng, 5xx, 2xx sai dạng), thêm câu kiểu "Bài nháp có thể đã được tạo: kiểm Bài viết → Nháp trước khi gửi lại", tương tự `maybe_uploaded` của ảnh.

## Ghi nhận (không xếp lỗi, không có xfail)

- **G1.** `_check_web_image` (`client.py:1422-1444`) không so cỡ khai trong `WebImage` với cỡ thật của file: `WebImage(web.data, 10, 10, None)` (file 320×240) được nhận, bài có `<img width="10" height="10">`. Chỉ xảy ra khi tự dựng `WebImage` bằng tay (`make_web_image` luôn đúng, lớp đóng băng). Có thể so với khung VP8X.
- **G2.** Alt chỉ gồm ký tự trông như trống mà không thuộc loại vô hình (U+2800 "ô chữ nổi trống") vẫn được coi là có chữ. Rất hiếm.
- **G3.** Website trả **cùng một mã** cho hai lần tải ảnh khác nhau vẫn được nhận: lệnh ghi alt thứ hai đè alt/tiêu đề/chú thích của ảnh thứ nhất (ảnh app vừa tạo), hai `<figure>` trỏ cùng một file. Rộng hơn: website trả mã của ảnh cũ thì alt ảnh cũ bị đổi (Lá Chắn T-042 mục W2 đã xét: máy chủ phải bị chiếm, không tính). Có thể chặn mã trùng trong một lần gửi, rẻ.
- **G4.** `source_url` dạng `HTTPS://` (chữ hoa) qua được `is_site_link` (`client.py:1265`) nhưng `figure_html` từ chối (`html.py:63`): vẫn dừng an toàn, chưa tạo nháp, chỉ là dừng sau khi đã tải **hết** ảnh thay vì ngay ảnh đó (`test_source_url_https_chu_hoa_dung_lai_khong_tao_nhap`).
- **G5.** Chốt cuối của `figure_html` (`html.py:102`) tìm ` src="…"` và ` alt=` trong **cả** khối `<figure>`, gồm chữ chú thích (sau bộ lọc, dấu `"` trong chữ để trần). Nếu sau này `_check_src` bị nới và bộ lọc bỏ `src`, chữ chú thích có thể làm chốt này tưởng vẫn còn `src` (kết quả chỉ là ảnh không có `src`, không thành mã độc). Nên tìm trong riêng thẻ `<img …>`.
- **G6.** `class` cho phép trên mọi thẻ với mọi giá trị từ T-004 (`sanitize.py:648`); phiếu này không mở thêm, nên yêu cầu 3 ("nếu mở `class`") không áp dụng. Chữ thân bài (không phải luồng ảnh) vẫn có thể mang `class="wp-image-N"`. Đề xuất siết `class` của Thợ Máy để Lá Chắn quyết.
- **G7.** Câu báo của `DraftImagesError` vẫn kèm lời máy chủ "(WordPress: …)" do dùng chung `_error_from` (LC-T042-4, phiếu T-060). Không có mật khẩu (đã thử 20 trường hợp).
- **G8.** `DraftImage` nhận `category`, `area` là chữ tự do (chỉ kiểm kiểu, độ dài). Truyền nhầm tên thư mục thì chữ trong đó vào tên file công khai: `category="C:\Users\An\Ảnh\CT012 - Nhà anh Tuấn\cong.php"` → `c-users-an-anh-ct012-nha-anh-tuan-cong-php.webp`; `area="Nhà anh Tuấn 12 Lê Lợi"` → `cong-inox-nha-anh-tuan-12-le-loi.webp`. Bảo vệ hoàn toàn dựa vào T-056 dùng `ImageTags` (T-052, chưa có trên nhánh này). Khi T-052 đã gộp, có thể cho `DraftImage` nhận thẳng `ImageTags` để code tự bảo đảm.
- **G9.** Site trả bài vừa tạo là `publish`/`future` (app không xin): kết quả trả về bình thường, câu báo "Chỉ được đặt ảnh đại diện cho bài nháp app vừa tạo, không sửa bài đã có trên website" dễ hiểu sai. T-056 nên hiện `result.post.status` khi khác `draft`.
- **G10.** Hai `DraftImage` khác đối tượng nhưng cùng giá trị thì tải hai lần (đúng như tài liệu: chỉ gộp khi **cùng một đối tượng**). T-056 nên dùng lại cùng một đối tượng khi đặt một ảnh ở hai chỗ.

## Rủi ro và điểm cần chú ý

- Chưa thử trên website thật (không có site thử, test không gọi mạng): WordPress có giữ nguyên file WebP 1600 px, không thêm `srcset` khi không có `wp-image-N`, plugin nén ảnh/CDN có đổi `src` hay xóa EXIF không. Đồng ý với đề xuất của Thợ Máy: một phiếu thử thật với **một** bài nháp, tải file ảnh từ web về kiểm GPS.
- Test SL-T054-2 sẽ thành XPASS khi T-061 gộp (nếu T-061 phủ đúng): lúc đó chỉ cần xóa dòng `@pytest.mark.xfail`.

## Đề xuất

- **Cho Chỉ Huy:** chuyển T-054 sang Lá Chắn. Giao SL-T054-1 và SL-T054-3 cho Thợ Máy (sửa trong T-054 hoặc phiếu dọn lỗi, trước T-056). Ghi vào T-061: phủ cả `<figcaption>` và thuộc tính `alt` (test SL-T054-2), nêu cách xét trường Media REST. Trước khi gộp: T-067 và thử 3–5 ảnh thật (Lá Chắn T-049 điều kiện 7).
- **Cho T-056 (giao diện):** chỉ truyền thẻ từ `ImageTags`, không bao giờ tên thư mục (G8); dùng lại cùng đối tượng `DraftImage` (G10); hiện `post.status` khi khác nháp (G9); hiện `exc.uploaded` và `maybe_uploaded` như Thợ Máy đề xuất.
- **Cho Lá Chắn:** xem G3, G5, G6, G8.

## Câu hỏi cho chủ dự án

Không có.

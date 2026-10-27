# Biên bản bảo mật T-059 bước 7 · Siết client WordPress theo thử thật 27/10 · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-059](../tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md), bước 7 (ghi chú thử thật 27/10 trên `main`) |
| Phạm vi | Rút gọn: **W1–W4, S1** (yêu cầu bảo mật riêng của phiếu, cùng R2, R3), kèm đủ 19 dòng danh sách kiểm tra. Diff `4671104..team/T-059` (đầu nhánh `ed01cc4`, 3 commit). Code ứng dụng: `seo_app/wordpress/client.py` (+21/−13, chỉ `_ability_confirms`), `seo_app/images/html.py` (+33/−10, `figure_html`, `_SRC_UNSAFE`); test: `tests/test_t059_siet_ghi_seo_va_srcset.py` (mới, Thợ Máy), `tests/test_soi_loi_t059.py` (mới, Soi Lỗi), `tests/fake_wordpress.py` (+20: site giả trả khuôn thật), 9 file test cũ (bảng R5, Chỉ Huy B duyệt 27/10); 2 báo cáo. Kèm code xung quanh: `set_seo_meta`, `_seo_via_abilities`, `create_draft_with_images`, `_describe_draft_media`, `sanitize_html` (`_attrs`, `_is_safe_srcset`), `check_connection`. `origin/main` lúc kiểm: `d9e6b5c` |
| Ngày | 2026-10-28 (01:27–02:04 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T059-1 của Soi Lỗi, đồng ý Thấp, có từ trước). Rủi ro kses bỏ `srcset`: **Thấp, rủi ro chức năng** (làm hỏng quyết định 5A, không làm lộ gì). Lá Chắn không có lỗi mới. `_ability_confirms` chặt hơn mà **không mở đường ghi nào**; `srcset` không lộ gì, không làm vỡ bộ lọc, vẫn chặn shortcode. Test cũ đổi đúng R5 (chặt hơn). **Gộp `main` được ngay**: không xung đột với `origin/main` `d9e6b5c` (main chỉ đổi trang Cài đặt T-084, thêm gói rỗng, không đụng file của T-059); test liên quan qua trên cây gộp |

## Tóm tắt (cho chủ dự án)

- **Phần sửa an toàn.** App nay chỉ báo «đã ghi SEO» khi website trả lời đúng như lần thử 27/10 và chữ đã lưu giống từng chữ app gửi; trả lời lạ thì app báo «chưa ghi, hãy chép tay». Việc này không thêm lệnh nào gửi lên website. Ảnh trong bài nay ghi sẵn «danh sách cỡ ảnh» chỉ có đúng file 1600 px (còn GPS) của chính website bạn, nên WordPress không tự chèn các bản thu nhỏ mất GPS; không thêm thông tin gì ra ngoài, lệnh chặn shortcode vẫn giữ.
- **Hai điểm nhỏ cho phiếu sau:** (1) khi tiêu đề, mô tả SEO có «< », «%» kèm 2 chữ số hay chữ A–F, hoặc «\», SiteSEO tự sửa chữ khi lưu nên app báo nhầm «chưa ghi» (không hỏng gì, chỉ làm bạn chép tay thừa); (2) nếu sau này tài khoản của phần mềm bị bớt quyền «đăng HTML tự do», WordPress sẽ xóa danh sách cỡ ảnh và ảnh trên điện thoại lại mất GPS. App nên báo trước điều này ở trang Kết nối WordPress.
- **Lưu ý bảo mật:** tài khoản Biên tập viên của phần mềm có sẵn quyền «đăng HTML tự do» (mặc định của WordPress); cách giữ GPS lần này dựa vào quyền đó. Nếu mật khẩu ứng dụng bị lộ, người có nó chèn được mã chạy trên trang. Giữ mật khẩu ứng dụng chỉ trên hai máy, thu hồi ngay khi nghi lộ; đừng cấp thêm quyền cho tài khoản chỉ để giữ GPS.

## Lỗi phát hiện

Không phát hiện lỗi mới (SL-T059-1 và rủi ro kses đánh giá ở mục dưới).

## Kiểm từng việc

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| `_ability_confirms` chặt mà không mở đường ghi mới (W2, R3) | **Đạt** | `client.py:1865-1893`: chỉ nhận `dict` không có `code`, `updated is True`, `success` không có hay đúng `True`, `fields` không rỗng, `post` là `dict`, mọi trường đã gửi đúng từng chữ. Hàm chỉ **đọc** câu trả lời. Câu trả lời không được nhận → `_seo_via_abilities` trả `_seo_error("abilities", None)` (`client.py:1035-1036`), **không** chuyển sang đường meta dự phòng, không gửi thêm lệnh nào (`set_seo_meta`: `if abilities: return self._seo_via_abilities(...)`, `:978-979`). Thử độc lập 24 ca: nhận khuôn thật (kèm `message`, kèm `success: true`); không nhận 20 khuôn lạ (`{"success": true}`, `{"updated": true}` thiếu `post`, `updated` là `"true"`/`1`/`false`, `success` là `false`/`null`/`"true"`, có `code` kể cả `code: null`, `post` là `null`/danh sách/chuỗi, thiếu trường, thừa một dấu cách, thêm `&#8203;`, dạng NFD, cả câu trả lời là danh sách, chuỗi, `true`) và `fields` rỗng |
| `srcset="<file đầy đủ> 1x"` không làm lộ gì (S1, W3) | **Đạt** | `html.py:131-135`: `srcset` dùng **đúng** chuỗi `src` đã escape; `src` lấy từ câu trả lời tải ảnh và phải là link `https` của đúng website (`is_site_link`, `client.py:1441-1443`) rồi qua `_check_src` (`html.py:97-106`). Không thêm địa chỉ, tên file, đường dẫn máy hay dữ liệu nào ngoài địa chỉ ảnh công khai đã có trong `src` |
| Không vỡ `sanitize_html`, vẫn chặn shortcode (W3, mục 2.3) | **Đạt** | `sanitize_html` cho `srcset` trên `img` (`sanitize.py:652`) và kiểm từng ứng viên như `src` (`_is_safe_srcset`, `:679-680`, `:722`). Chốt cuối của `figure_html` đòi đúng ` srcset="<src đã qua bộ lọc> 1x"` sau bộ lọc, mất thì không gửi ảnh (`html.py:147-153`). Dấu phẩy bị cấm trong địa chỉ ảnh (`_SRC_UNSAFE`, `html.py:57`) nên không chèn được ứng viên thứ hai. Thử độc lập: 5 địa chỉ đúng (có `[1]`, `?ver=2&size=full`, `%2C`) ra đúng một `img` có `srcset` = `src 1x`, không `sizes`, không «[» «]» trần (alt `[code_snippet id=1]`, chú thích `[caption]thu[/caption]` đều thành `&#91;…&#93;`); 10 địa chỉ xấu bị chặn: `a,b.webp`, `a.webp 2x`, `a.webp,https://evil.example/x.webp 2x`, tab, dấu nháy, `http://`, `javascript:`, xuống dòng, `<`, `\` |
| Cơ chế WordPress mà cách sửa dựa vào | **Đúng** (đọc mã độc lập) | `wordpress-develop` trunk, 2026-10-28, chỉ đọc mã công khai: `wp_filter_content_tags` lấy mã ảnh bằng `preg_match( '/wp-image-([0-9]+)/i', … )` và chỉ thêm `srcset`/`sizes` khi `$attachment_id > 0 && ! str_contains( $filtered_image, ' srcset=' )`; có bộ lọc `wp_img_tag_add_srcset_and_sizes_attr` để tắt theo từng ảnh. kses: `$allowedposttags['img']` chỉ có `alt, align, border, height, hspace, loading, longdesc, vspace, src, usemap, width` (+ thuộc tính chung: `class`, `id`, `style`, `title`, `data-*`, `aria-*`…), **không** có `srcset`; kses gắn vào nội dung khi `! current_user_can( 'unfiltered_html' )` (`kses_init`) |
| W1 (nháp, `publish`/`future`) | **Đạt** | Diff không đụng đường tạo bài, `status`, `_is_plain_request`, `ALLOWED_ROUTES` |
| W4 (SSL, timeout, `https://`) | **Đạt** | `_request` không đổi |
| Test cũ đổi đúng R5 | **Đạt** | Mục «Soát R5» |

## Đánh giá lỗi của Soi Lỗi và rủi ro kses

| Lỗi | Đánh giá của Lá Chắn | Chặn gộp? Phiếu nhận |
|---|---|---|
| SL-T059-1 · SiteSEO làm sạch chữ khi lưu («< » không có «>» phía sau thành `&lt;`, `%` + 2 ký tự hex bị cắt, `\` bị bỏ), app so `post` đúng từng chữ nên báo «không thành công» dù đã ghi | **Đồng ý Thấp.** Báo sai theo chiều an toàn: không ghi sai, không lộ gì, không thêm lệnh; người dùng chép tay thừa (kết quả trên site như nhau). Có từ trước (T-042 đã so từng chữ khi có `post`); bước 7 chỉ làm `post` bắt buộc. Riêng ca `%xx`: SiteSEO **cắt mất chữ** mà người dùng không được báo | **Không.** Phiếu dọn sau (Chỉ Huy lập), **trước khi bật công tắc «Ghi SEO lên website» cho dùng thường xuyên**. Cách sửa khuyên: chặn trước khi gửi, kèm câu báo, `%` + 2 ký tự hex và `\` (hiếm trong chữ SEO, và tránh được chuyện SiteSEO cắt chữ); với «< » thì nhận cả bản đã làm sạch kiểu `sanitize_text_field` khi so (chữ «Giá < 2 triệu» là hợp lệ, T-041 cho phép). Việc so lỏng thêm chỉ đổi cách báo, không mở đường ghi nào |
| Rủi ro kses: tài khoản không có quyền `unfiltered_html` thì WordPress bỏ `srcset` khi lưu, ảnh lại bị gắn bản thu nhỏ mất GPS | **Thấp, rủi ro chức năng** (làm hỏng quyết định 5A). Về bảo mật thì ngược lại: mất GPS là bớt lộ, không phải lộ thêm. Hôm nay tài khoản là Biên tập viên trên site đơn, có `unfiltered_html` theo mặc định của WordPress, nên chưa xảy ra; sẽ xảy ra nếu website đặt `DISALLOW_UNFILTERED_HTML`, chuyển sang nhiều site, hay đổi vai tài khoản | **Không.** Cùng phiếu dọn sau: `check_connection` đọc `capabilities.unfiltered_html` (đã có trong câu trả lời `GET /wp/v2/users/me?context=edit`, `client.py:760-775`), **khác `true`** thì trang Kết nối WordPress và bước gửi nháp **Cảnh báo** «WordPress sẽ bỏ danh sách cỡ ảnh: ảnh trên điện thoại sẽ không còn GPS». Ghi rõ đây là dấu hiệu, không chắc chắn: REST trả quyền theo vai, không thấy `DISALLOW_UNFILTERED_HTML`; nên lượt thử lại trên site thật (dưới) vẫn phải xem nội dung đã lưu. **Không** khuyên cấp thêm quyền `unfiltered_html` cho tài khoản chỉ để giữ GPS (Ghi nhận 1); nếu cần, dùng bộ lọc phía website `wp_img_tag_add_srcset_and_sizes_attr` (chủ dự án duyệt) |

## Soát R5

Đối chiếu `git diff 4671104..team/T-059 -- tests/` với bảng «Test cũ đã đổi» của Thợ Máy (Chỉ Huy B duyệt 27/10) và kết quả soát của Soi Lỗi: **Đạt**.

- Nhóm 1, 3 (site giả mặc định `{"success": True}` hay `{"updated": True}` → `siteseo_seo_answer`, khuôn thật lưu y chữ đã gửi): chỉ đổi dòng `fake.on(… RUN …)`/`run=…`, không câu kiểm nào đổi; cần đổi vì hai khuôn cũ nay đúng là «chưa ghi».
- Nhóm 2 (`tests/test_soi_loi_t042_round2.py`, `tests/test_wordpress_round2_t042.py`): `{"updated": True}`, `{"success": True}` chuyển từ danh sách «được nhận» sang «chưa ghi»: **chặt hơn**, đúng việc của phiếu; thêm khuôn thật vào «được nhận».
- Ảnh (`tests/test_wordpress_images.py`, `tests/test_soi_loi_t054.py`): «không có `srcset`, `sizes`» thay bằng «đúng một `srcset` là `<file đầy đủ> 1x`, không `sizes`» (vẫn chặn cỡ nhỏ mất GPS, ý cũ giữ nguyên); danh sách thuộc tính `<img>` vẫn so **đúng bằng** (thêm `srcset`); mẫu giả lập «bộ lọc bỏ alt» sửa để vẫn thật sự bỏ alt, thêm ca «bộ lọc bỏ `srcset`».

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không bí mật trong diff, file mới, lịch sử 3 commit (mục Công cụ); báo cáo không có tên, mật khẩu ứng dụng thật. Mật khẩu trong test là chuỗi giả |
| S2 | Đạt | Không câu báo mới; `_seo_error`, `_MSG_BAD_SRC` cố định như cũ |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Đạt | Mục «Kiểm từng việc» |
| W2 | Đạt | Không lệnh ghi mới; câu trả lời không được nhận chỉ đổi câu báo |
| W3 | Đạt | `figure_html` vẫn qua `sanitize_html`, chặn shortcode, chốt cuối; `srcset` chỉ là `src` của chính website |
| W4 | Đạt | `_request` không đổi |
| A1–A3 | Không áp dụng | Không đổi lớp AI, prompt |
| U1–U3 | Không áp dụng | Không sửa `app/**`, không trang mới |
| F1, F2 | Không áp dụng | Không đổi đọc ảnh, xử lý ảnh; byte ảnh gửi đi không đổi (GPS giữ theo sổ rủi ro 2026-10-14) |
| F3 | Đạt | Không `eval`, `pickle`; chỉ so chuỗi |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` giống gốc |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới dùng `FakeWordPress` và WordPress giả lập bằng Python; không gọi website thật (thử thật 27/10 do Chỉ Huy, chủ dự án làm, ngoài test) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy lại: `uv.lock`, `pyproject.toml` giống gốc (`git diff --quiet`); lượt gần nhất (T-088, 26/10, 69 gói): 0 lỗ hổng | Có |
| bandit | `seo_app/wordpress/client.py`, `seo_app/images/html.py`: **No issues identified** (1.714 dòng) | Có |
| detect-secrets (`PYTHONUTF8=1`) | 11 file (2 file code, 7 file test, 2 báo cáo): 4 phát hiện, đều không phải bí mật: `client.py:682` dòng chú thích ví dụ dạng «tên:mật-khẩu@site» (có từ T-060); `tests/test_soi_loi_t042_round2.py:100` địa chỉ giả `user:pass@example.com` có từ trước (dòng này không đổi); «Secret Keyword» ở `tests/test_soi_loi_t059.py:39`, `tests/test_t059_siet_ghi_seo_va_srcset.py:37` là chuỗi giả của test | Có, từng dòng |
| Soát lịch sử git | `git log -p 4671104..HEAD` (3 commit): không `sk-ant-`, `AIza…`, `ghp_…`, `-----BEGIN`; không tên, mật khẩu ứng dụng thật; không file `.env`, `.sqlite`, `.json`, `.pem` | Có |
| pytest (nhánh) | 28 file: `tests/test_t059_siet_ghi_seo_va_srcset.py`, `tests/test_soi_loi_t059.py`, ảnh trong bài và chặn shortcode (`test_wordpress_images`, `test_soi_loi_t054`, `test_shortcode_t061`, `test_soi_loi_t061`, `test_soi_loi_t071`, `test_la_chan_t071`), ghi SEO và các test cũ đã đổi (`test_wordpress_seo_meta_t042`, `test_soi_loi_t042`, `test_soi_loi_t042_round2`, `test_wordpress_round2_t042`, `test_soi_loi_t060`, `test_soi_loi_t088`, `test_t041_seo_ui`, `test_t041_meta`), client (`test_wordpress_client`, `test_la_chan_t060`, `test_wordpress_t085`, `test_soi_loi_t085`, `test_la_chan_t085`, `test_wordpress_t088`), «Gửi nháp» và trang (`test_t089_send_draft`, `test_la_chan_t089`, `test_soi_loi_t089`, `test_app_images`, `test_app_wordpress`, `test_app_pages`), 01:30–01:55: **4372 passed, 13 xfailed, 0 hỏng**. Thử độc lập (script ở thư mục nháp, không commit): 40 ca `_ability_confirms`, `figure_html`, 0 hỏng | | Có. 13 xfail có sẵn: SL-T059-1 (5), SL-T088-1 (8); 0 XPASS |
| pytest (cây gộp) | Cây gộp `team/T-059` + `origin/main` `d9e6b5c` (`git merge-tree`, không xung đột; giải nén vào thư mục nháp, `seo_app` nạp từ cây gộp), 11 file (2 file T-084 của trang Cài đặt, 2 file T-059, ảnh trong bài, ghi SEO, `test_app_wordpress`, `test_app_pages`): lượt 1 (01:56–01:59) **1 hỏng**: `tests/test_soi_loi_t084.py::test_whole_settings_page_never_shows_env_values_or_paths` (test của T-084, trang Cài đặt, file chạy **đầu** lượt nên không do thứ tự test); chạy riêng: qua; chạy lại 2 file T-084 trên cây gộp và trên `main` riêng: cùng 41 passed, 2 xfailed; chạy lại nguyên lượt 11 file (02:02–02:04): **1262 passed, 7 xfailed, 0 hỏng**. Kết luận: hỏng oan khi máy bận (như lời dặn của phiếu), không do T-059 | Có. 7 xfail: SL-T059-1 (5), 2 có sẵn của T-084; 0 XPASS |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |

## Ghi nhận (không xếp lỗi)

1. **Quyền `unfiltered_html` của tài khoản phần mềm.** Biên tập viên trên site đơn có quyền này theo mặc định; app tự lọc mọi HTML gửi đi nên **không cần** quyền này, trừ việc giữ `srcset` (bước 7 dựa vào nó để giữ GPS, quyết định 5A). Hệ quả: nếu mật khẩu ứng dụng lộ, người có nó chèn được mã chạy trong trình duyệt người xem và quản trị viên (với quyền Biên tập viên thiếu `unfiltered_html` thì không). Đề nghị Chỉ Huy nói rõ với chủ dự án và hỏi có ghi sổ rủi ro không («tài khoản phần mềm giữ `unfiltered_html` để ảnh trong bài giữ GPS; biện pháp: mật khẩu ứng dụng chỉ trên hai máy, thu hồi ngay khi nghi lộ»). Nếu chủ dự án muốn bỏ quyền này (an toàn hơn) mà vẫn giữ GPS: bộ lọc phía website `wp_img_tag_add_srcset_and_sizes_attr` trả `false` cho ảnh của bài do phần mềm tạo (việc website, chủ dự án duyệt).
2. **Thử lại trên site thật sau khi gộp** (Thợ Máy, Soi Lỗi đề xuất; đồng ý): một bài nháp một ảnh; trong nội dung **đã lưu** (trình soạn mã) thẻ ảnh còn `srcset="…/<tên-ảnh>.webp 1x"`, trong nguồn trang xem trước không có `-300x…`, `-768x…`, `-800x…`; tải file trong `srcset` về kiểm GPS. Đây cũng là cách duy nhất biết chắc kses có bỏ `srcset` không (REST không cho thấy `DISALLOW_UNFILTERED_HTML`). Tìm thứ gắn lớp `wp-image-951` như đề xuất của Thợ Máy.
3. Thuộc tính lạ thêm vào câu trả lời ghi SEO (`message`…) vẫn được nhận khi `post` khớp: đồng ý (không đổi đường ghi nào).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

| # | Việc | Ai làm | Hạn |
|---|---|---|---|
| 1 | **SL-T059-1:** chặn trước khi gửi `%` + 2 ký tự hex và `\` trong chữ SEO (kèm câu báo), nhận bản đã làm sạch kiểu `sanitize_text_field` của «< » khi so `post`; gỡ 5 `xfail` của Soi Lỗi | Thợ Máy, phiếu dọn sau (Chỉ Huy lập) | Trước khi bật «Ghi SEO lên website» cho dùng thường xuyên |
| 2 | **Rủi ro kses:** `check_connection` đọc `capabilities.unfiltered_html`, khác `true` thì Cảnh báo ở trang Kết nối WordPress và bước gửi nháp (ảnh trên điện thoại sẽ mất GPS); câu báo nói đây là dấu hiệu | Thợ Máy (client) + Họa Sĩ (trang), cùng phiếu dọn | Trước khi hết Giai đoạn 4 |
| 3 | Thử lại trên site thật một bài nháp một ảnh (Ghi nhận 2) | Chỉ Huy + chủ dự án | Sau khi gộp, trước khi dùng thật thường xuyên |

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (SL-T059-1, đồng ý Thấp, có từ trước, báo sai theo chiều an toàn); rủi ro kses bỏ `srcset` là Thấp, rủi ro chức năng; Lá Chắn không có lỗi mới. `_ability_confirms` chặt hơn, không mở đường ghi nào (câu trả lời không được nhận chỉ đổi câu báo, không chuyển sang đường meta); `srcset` chỉ là `src` của chính website, qua `sanitize_html`, chặn shortcode, có chốt cuối; W1, W4 không đổi; S1 sạch. Test cũ đổi đúng R5 (chặt hơn). **Gộp `main` được ngay.** Điều kiện 1–2 vào phiếu dọn sau, điều kiện 3 là thử lại trên site thật sau khi gộp.

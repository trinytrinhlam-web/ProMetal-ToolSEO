# Báo cáo T-088 · Dọn lỗi Thấp client WordPress sau T-085 · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-088](../tickets/T-088-don-client-wordpress-sau-t085.md) |
| Nhánh | `team/T-088` (gốc `main` `dd5ea2d`, kiểm trên đầu nhánh `1e87ce8`) |
| Ngày nộp | 2026-10-26 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. **4 lỗi cũ đóng** (SL-T085-1, -2, -3, LC-T085-1). Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T088-1). Gỡ `xfail` đúng; không test cũ nào bị sửa |

## Tóm tắt (cho chủ dự án)

- Cả 4 lỗi nhỏ còn lại của lần trước đã được sửa đúng. Tôi thử lại bằng chính cách đã tìm ra lỗi, cộng nhiều biến thể:
  - mẹo chèn ký tự vô hình để xin website trả nội dung bài: thử gần 2.000 kiểu đặt ký tự và 60.000 giá trị ngẫu nhiên, không kiểu nào lọt;
  - website trả dữ liệu lạ (lồng quá sâu, hỏng, sai bảng mã) ở **mọi** lệnh của phần mềm: 1.520 ca, không lần nào hiện lỗi đỏ của Python, luôn ra câu tiếng Việt;
  - tải ảnh ở trang Kết nối WordPress mà website lỗi giữa chừng: câu báo nay dặn «ảnh có thể đã lên thư viện Media, kiểm Media → Thư viện trước khi tải lại»; website từ chối rõ ràng thì giữ câu cũ.
- Không chặn oan: mọi việc thật của phần mềm vẫn chạy (trang Kết nối WordPress, «Gửi nháp», ghi SEO); gộp thử với `main` mới nhất, với nhánh T-041 và T-086 đang làm song song: không xung đột.
- Tìm thấy **1 lỗi nhỏ mới (Thấp)**: nếu website trả chữ có một loại ký tự hỏng đặc biệt (nửa ký tự Unicode, gọi là «surrogate» lẻ), trang Kết nối WordPress vẫn vỡ (lỗi đỏ Python), và phần lưu tạm danh sách bài cũng hỏng. WordPress bình thường không bao giờ trả loại ký tự này; chỉ xảy ra khi website hay plugin, proxy bị lỗi hoặc cố ý.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t088.py` | Mới: 517 ca (509 qua, 8 `xfail(strict=True)` của SL-T088-1). Dữ liệu, bản Python của WordPress và câu trả lời thô (byte, bảng mã tùy ý) riêng; site giả chung `FakeWordPress` |
| `docs/team/reports/T-088-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm 4 lỗi cũ (cách tái hiện cũ + biến thể)

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| SL-T085-1 · NUL sát tên trường `_fields` | **ĐÓNG** | `client.py:125` (`_PHP_TRIM`), `:249-263`. Cách tái hiện cũ (`"id,status,\x00content"` trên `GET /wp/v2/posts/42`): bị chặn trước khi gửi. Biến thể: NUL và 5 khoảng trắng của `trim()` (`" "`, `\t`, `\n`, `\r`, `\x0b`) ở trước, sau, hai đầu, nhiều lớp, sát dấu phẩy, quanh `.rendered`, trộn với tên khác; 5 tên trường × 3 đường × 210 dạng (`test_nul_va_khoang_trang_trim_quanh_ten_truong_khong_lot`); ngẫu nhiên 6.000 giá trị có NUL (`test_nul_ngau_nhien_khong_lot`). So với bản Python của WordPress tôi viết riêng (`wp_parse_list`, `trim()` từng tên, giữ tên có phần đầu là trường, `rest_is_field_included("X.rendered")`): giá trị nào đi ra thì WordPress **không** dựng trường chạy shortcode. Script dò: 1.806 biến thể và 60.000 giá trị ngẫu nhiên (41.425 đi ra): **0 lọt**. NUL ở giữa tên (`con\x00tent`) vẫn đi ra (WordPress không cắt, vô hại); hằng `_fields` của app vẫn đi ra |
| SL-T085-2 · JSON lồng quá sâu → `RecursionError` | **ĐÓNG** | `client.py:1517-1527` (`_json` bắt mọi lỗi giải mã, câu kèm «(mã N)»). Cách tái hiện cũ (`GET /wp-json/` trả 50.000–200.000 tầng): `WordPressError` câu cố định. `test_moi_lenh_doc_tra_loi_chi_ra_ket_qua_hay_wordpresserror`: 12 kiểu thân (mảng lồng sâu, đối tượng lồng sâu, lồng sâu không khai bảng mã, UTF-8 hỏng có và không khai bảng mã, bảng mã bịa, khai sai UTF-32, BOM, số 5.000 chữ số, JSON cụt, rỗng, HTML) × **19 lệnh** của 8 hàm công khai (kiểm kết nối 3, chuyên mục, bài đã đăng 2, tạo nháp, tải ảnh 2, ảnh đại diện 2, ghi SEO 3, gửi nháp kèm ảnh 5) × mã 200 và 500 = 456 ca: chỉ ra kết quả bình thường hoặc `WordPressError`, câu không chép lời máy chủ. Script dò: 16 kiểu (thêm UTF-16 có BOM, `NaN`/`Infinity`, surrogate, lỗi giải nén) × mã 200, 201, 400, 404, 500 = 1.520 ca: **0 lỗi Python lọt** |
| LC-T085-1 · thân **lỗi** (4xx/5xx) lồng quá sâu | **ĐÓNG** | `client.py:1535-1540` (`_error_from` bắt mọi lỗi giải mã, coi như thân rỗng). Trong 456 ca trên, mọi ca mã 500 đi qua `_error_from`; trang Kết nối WordPress thật (`AppTest`) với mã 200, 404, 500 thân lồng sâu: không vỡ, đúng 1 câu báo lỗi (`test_trang_ket_noi_tra_loi_long_sau_ra_mot_cau_loi`). Lệnh ghi đè ảnh trả lỗi lồng sâu: câu «thư viện Media», mã ảnh (test của Lá Chắn T-085 đã gỡ dấu) |
| SL-T085-3 · lệnh tải ảnh lỗi giữa chừng | **ĐÓNG** | `client.py:386-390`, `:1144-1158`. Cách tái hiện cũ (500, 502, 503, hết giờ, 201 HTML, 201 thiếu mã): câu có «có thể đã lên thư viện Media», «Media → Thư viện». Biến thể (`test_tai_anh_loi_khong_ro_rang_dan_kiem_thu_vien_media`, 17 ca + 201 lồng sâu): 504, 520, 301, mất kết nối, SSL, đứt giữa chừng, lỗi giải nén, 201 mã là chữ, 201 danh sách, 200, 202; đúng 1 lệnh (không ghi đè), câu không chép lời máy chủ hay địa chỉ. Lời từ chối 4xx (11 mã: 400, 401, 403, 404, 405, 408, 409, 413, 415, 422, 429): **không** dọa «ảnh đã lên», giữ câu cũ kèm «(mã N)», giữ `status_code`. Tải thành công: không đổi |
| Gỡ `xfail` | **ĐẠT** | `git diff dd5ea2d..team/T-088`: `tests/test_soi_loi_t085.py` −20 dòng (4 khối dấu: SL-T085-1 27 ca, SL-T085-2 2 + 1 ca, SL-T085-3 6 ca), `tests/test_la_chan_t085.py` −10 dòng (2 khối, LC-T085-1 4 ca). Chỉ xóa dòng dấu, thân test không đổi chữ nào; 40 ca qua |

## Không chặn oan

- Script «lệnh thật của app» (site giả riêng của tôi) trên đầu nhánh: kiểm kết nối, chuyên mục, thẻ, bài đã đăng, tạo nháp, tải ảnh + ghi alt, tải ảnh từ file, ảnh đại diện, ghi SEO qua Abilities, ghi SEO dự phòng (meta), gửi nháp kèm ảnh: **11/11 đi ra đúng**.
- `test_tai_anh_thanh_cong_khong_doi`: tải ảnh thành công vẫn đúng 2 lệnh, `Media` lấy địa chỉ, alt của câu trả lời ghi đè.
- Trang Kết nối WordPress, «Gửi nháp» của T-056 và mọi trang: các file `tests/test_app_pages.py`, `tests/test_app_wordpress.py`, `tests/test_app_images.py`, `tests/test_la_chan_t056.py`, `tests/test_soi_loi_t056.py` trong lượt 54 file (mục Bằng chứng).
- Không đổi: so cây cú pháp `ast` giữa `dd5ea2d` và nhánh, chỉ đổi `_PHP_TRIM`, `_asks_rendered_fields`, `_MEDIA_MAYBE_UPLOADED`, `_MEDIA_UPLOAD_UNEXPECTED`, `upload_media`, `_json`, `_error_from` (cùng 1 dòng chú thích cạnh `ALLOWED_JSON_KEYS`). `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`, `create_draft_with_images`, `_describe_draft_media`, `_post_media`, `_request`, `_is_plain_request`, `is_site_link`, `_plain` **giống hệt**.

## Gộp thử

- `git fetch` (14:00): `origin/main` = `dd5ea2d` = gốc nhánh, nên gộp với `main` mới nhất không đổi gì.
- **T-041** (`origin/team/T-041` `85ce8d7`, đang làm song song; sửa `seo_app/storage/site_index.py`, `drafts.py`, `onpage/`): `git merge-tree` với `team/T-088` không xung đột (cây `1c52d00`, giải nén vào thư mục nháp). 11 file (`tests/test_soi_loi_t088.py`, `tests/test_wordpress_t088.py`, `tests/test_soi_loi_t085.py`, `tests/test_la_chan_t085.py`, 6 file test T-041, `tests/test_app_pages.py`), 14:10–14:14: **1736 passed, 16 xfailed, 0 hỏng** (8 xfail SL-T088-1 vẫn XFAIL, 8 của T-041).
- **T-086** (`origin/team/T-086` `0782e9b`, trạng thái «Gửi nháp», chưa vào `main`): không xung đột (cây `4d85005`; đã kiểm `seo_app.wordpress.client` nạp từ cây gộp, có phần sửa của T-088). 11 file: `tests/test_soi_loi_t088.py`, `tests/test_wordpress_t088.py`, 4 file T-086 (`tests/test_t086_send_state.py`, `tests/test_soi_loi_t086.py`, `tests/test_la_chan_t086.py`, `tests/test_storage_send_state.py`), «Gửi nháp» và trang (`tests/test_app_images.py`, `tests/test_la_chan_t056.py`, `tests/test_soi_loi_t056.py`, `tests/test_wordpress_images.py`, `tests/test_app_wordpress.py`), 14:14–14:41: **951 passed, 11 xfailed, 0 hỏng** (8 SL-T088-1; 3 của chính T-086: SL-T086-1, -2, LC-T086-1).
- Trên cây gộp T-041, thử thêm `site_listing()` (bước SEO của Soạn bài, mới ở T-041) với tiêu đề bài có surrogate lẻ: lọt `UnicodeEncodeError` (SL-T088-1, mục dưới).

## Soát R5

T-088 không sửa test cũ nào. Ngoài file mới `tests/test_wordpress_t088.py`, chỉ có 6 khối dấu `xfail` bị xóa (mục «Gỡ `xfail`»): `git diff --stat dd5ea2d..team/T-088 -- tests/`, lọc dòng thêm/xóa có `assert`, `parametrize`, `raises`, `skip`, `def test_`: không dòng nào.

## Thử đột biến

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, không đụng worktree), gỡ từng chỗ sửa của T-088 trong `client.py` rồi chạy 4 file: `tests/test_soi_loi_t088.py` (của tôi), `tests/test_wordpress_t088.py` (Thợ Máy), `tests/test_soi_loi_t085.py`, `tests/test_la_chan_t085.py` (14:09–14:40). Bản không gỡ: mọi test qua.

| # | Chỗ sửa bị gỡ | Test của tôi hỏng | Test khác hỏng |
|---|---|---|---|
| P1 | Bỏ lần cắt `trim()` từng phần | 0 | 15 Thợ Máy |
| P2 | Bộ ký tự `trim()` thiếu NUL | 16 | 81 Thợ Máy, 27 Soi Lỗi T-085 |
| P3 | Bỏ lần cắt tên trước dấu chấm | 0 | 5 Thợ Máy |
| P4 | `_json` chỉ bắt `ValueError` | 43 | 5 Thợ Máy, 2 Soi Lỗi T-085 |
| P5 | `_error_from` chỉ bắt `ValueError` | 44 | 12 Thợ Máy, 3 Lá Chắn T-085 |
| P6 | Câu `_json` không kèm mã HTTP | 3 | 5 Thợ Máy |
| P7 | Lệnh tải lỗi nào cũng giữ câu cũ | 18 | 15 Thợ Máy, 6 Soi Lỗi T-085 |
| P8 | Lời từ chối 4xx cũng dọa «ảnh đã lên» | 11 | 8 Thợ Máy, 3 Soi Lỗi T-085 |
| P9 | Bỏ bắt lỗi lạ ở lệnh tải | 0 | 1 Thợ Máy |
| P10 | Bỏ bắt lỗi lạ ở lệnh ghi đè | 0 | 3 Thợ Máy |
| P11 | Câu dặn thiếu «Media → Thư viện» | 18 | 15 Thợ Máy, 6 Soi Lỗi T-085 |
| P4+P9+P10 | Bỏ mọi chỗ bắt lỗi lạ | 47 | 11 Thợ Máy, 3 Soi Lỗi T-085 |

Mọi chỗ sửa bị gỡ đều làm hỏng ít nhất một test. Test của tôi không bắt P1, P3, P9, P10, vì bốn chỗ này không làm yếu kết quả: P1, P3 là hai lần cắt `trim()` chồng nhau, gỡ một lần thì lần kia vẫn bắt mọi ca WordPress dựng trường (ca khác biệt là `"\x00"` đứng một mình hay `"content\x00.rendered"`, WordPress cũng không dựng); P9, P10 là lớp bắt lỗi lạ dự phòng, chỉ có tác dụng khi `_json`/`_error_from` để lọt (gỡ cùng P4 thì test của tôi bắt 47 ca). Test hành vi của Thợ Máy bắt cả bốn.

## Lỗi tìm được

### SL-T088-1 (Thấp) · Chữ website trả có ký tự surrogate lẻ đi qua client nguyên vẹn, làm vỡ trang và lưu tạm danh sách bài

- **Chỗ:** `seo_app/wordpress/client.py`: chữ của website qua `_plain` (`:1886`), `_clean_text` (`:1651`), vai trò và `site_url` chỉ lọc kiểu (`:763-772`), địa chỉ ảnh qua `is_site_link` (`:1584`), nhưng không chỗ nào bỏ ký tự surrogate lẻ (U+D800–U+DFFF). JSON cho phép viết chúng (`"\ud800"`), `json.loads` của Python nhận, nên chúng nằm trong chuỗi Python mà không mã hóa UTF-8 được.
- **Tái hiện** (site giả trả JSON hợp lệ):
  1. `GET /wp-json/` có `"name": "Cửa \ud800 sắt"` (hay tên tài khoản, vai trò ở `/wp/v2/users/me`): `check_connection()` trả `ConnectionInfo` chứa chuỗi đó; trang Kết nối WordPress bấm «Kiểm tra kết nối» thì **vỡ** (`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'… surrogates not allowed` khi Streamlit gửi chữ ra trình duyệt).
  2. Chuyên mục có tên như vậy: «Tải chuyên mục và thẻ» vỡ (`StreamlitDataframeConversionError`, lỗi kèm cả dữ liệu).
  3. Bài đã đăng có tiêu đề như vậy: `list_published()` trả nguyên; `SiteIndexStore.refresh()` ném `UnicodeEncodeError` khi ghi SQLite (không phải `SiteIndexError`, nên nơi gọi không bắt). Trên cây gộp với T-041, `site_listing()` của bước SEO ở Soạn bài (chỉ bắt `WordPressError`, `SiteIndexError`) để lọt lỗi đó ở cả «tải lại» lẫn «dùng cache».
  4. Gửi nháp kèm ảnh: câu trả lời lúc tải có `source_url` `https://<đúng site>/…/a\ud800.webp`: `is_site_link` nhận, địa chỉ vào `<img src>` của bài và `UploadedImage.source_url`.
- **Mong đợi:** chữ client trả cho trang, cho SQLite luôn mã hóa UTF-8 được (thay ký tự hỏng bằng «�» hay bỏ đi), hoặc coi dữ liệu đó là hỏng và báo `WordPressError` câu cố định.
- **Thực tế:** như trên; trang hiện khung lỗi Python (mặc định kèm chi tiết có đường dẫn thư mục trên máy, cùng loại LC-T044-1, SL-T085-2).
- **Mức:** Thấp. WordPress lõi không tự sinh surrogate lẻ (`wp_json_encode` sửa chữ UTF-8 hỏng trước khi xuất), nên cần website, plugin hay proxy lỗi hoặc cố ý; không lộ khóa, không ghi gì lên website. Có từ trước T-088 (không do phiếu này gây ra), cùng họ «dữ liệu lạ từ website làm vỡ trang» mà phiếu dọn. Nên sửa trước khi T-041 gộp, vì T-041 đưa danh sách bài đã đăng vào bước SEO của Soạn bài.
- **Test:** `test_sl_t088_1_chu_website_co_surrogate_le_khong_lot_ra` (6 ca: tên site, tên tài khoản, vai trò, chuyên mục, bài đã đăng, địa chỉ ảnh gửi nháp), `test_sl_t088_1_trang_ket_noi_khong_vo_vi_surrogate` (trang thật qua `AppTest`), `test_sl_t088_1_luu_tam_danh_sach_bai_khong_vo_vi_surrogate`.
- **Gợi ý sửa:** một hàm làm sạch chung cho mọi chữ từ website (`_plain`, `_clean_text`, vai trò, `is_site_link` từ chối), ví dụ `re.sub("[\ud800-\udfff]", "�", text)`; hoặc ngay ở `_json`: dữ liệu giải mã ra có surrogate lẻ thì báo câu cố định như JSON hỏng.

## Ghi nhận (không xếp lỗi)

1. Câu báo khi tải ảnh trả mã 200/202 (`_MEDIA_NOT_CREATED`) nay cũng dặn «ảnh có thể đã lên» (Thợ Máy tự quyết, khớp `maybe_uploaded` của gửi nháp kèm ảnh): đồng ý. Mã 3xx ở lệnh tải cũng được coi là «có thể đã lên»; chuyển hướng thường xảy ra trước khi máy chủ xử lý, nên câu này có thể dọa thừa, nhưng an toàn.
2. Đột biến P1, P3 (bỏ một trong hai lần cắt `trim()`) không làm yếu chốt chặn: lần cắt còn lại vẫn bắt mọi ca WordPress dựng trường; chỉ test hành vi của Thợ Máy bắt. Không cần sửa.
3. Đề xuất còn mở từ T-085 (Thợ Máy nhắc lại): lớp chặn phụ `id`/`name` cho tham số truy vấn; bắt buộc `_fields`; `verify=True` tường minh; `html.escape` tiêu đề, chú thích trong `upload_media`.
4. `detect-secrets` (`PYTHONUTF8=1`) trên 2 file của tôi: «Secret Keyword» ở `tests/test_soi_loi_t088.py:41`, `:42` (`PASSWORD`, `PAGE_PASSWORD`): mật khẩu giả cho test, cùng kiểu các file test khác. Báo cáo này: 0.

## Bằng chứng

```
# 54 file của báo cáo Thợ Máy (tiêu chí xong của phiếu), đầu nhánh 1e87ce8, chưa có file của tôi
# (13:55–14:27, máy chạy song song lượt đột biến và hai cây gộp):
6987 passed, 13 skipped, 15 xfailed in 1851.37s
# 15 xfail có sẵn, không thuộc T-088: LC-T039-2 (3), LC-T056-1 (2), SL-T056 (5), SL-T081-1 (5).
# 13 bỏ qua: test chỉ chạy trên Mac/Linux hoặc cần symlink (Windows).

# Lượt chốt (14:50–14:53): file của tôi + 13 file client và trang liên quan nhất
$ uv run pytest tests/test_soi_loi_t088.py tests/test_wordpress_t088.py tests/test_soi_loi_t085.py
    tests/test_la_chan_t085.py tests/test_wordpress_t085.py tests/test_wordpress_t060.py
    tests/test_soi_loi_t060.py tests/test_la_chan_t060.py tests/test_wordpress_client.py
    tests/test_wordpress_round2_t042.py tests/test_app_wordpress.py tests/test_app_t044_safe_text.py
    tests/test_soi_loi_t044.py tests/test_app_pages.py -rfxX
2796 passed, 8 xfailed in 180.02s      # 8 xfail: SL-T088-1

$ uv run pytest tests/test_soi_loi_t088.py
509 passed, 8 xfailed

$ uv run ruff check .
All checks passed!

# Test mới trên code cũ (main dd5ea2d, giải nén vào thư mục nháp):
133 failed, 376 passed, 8 xfailed
# 133 hỏng: NUL quanh tên trường (16), JSON lồng sâu ở mọi lệnh (93), câu _json không có mã (3),
# trang Kết nối vỡ (3), lệnh tải ảnh lỗi không dặn kiểm thư viện (18). 376 qua: ca đối chứng
# (lời từ chối 4xx, tải thành công, bản Python của WordPress) và kiểu thân hỏng mà code cũ đã đỡ.

# Cây gộp T-088 + T-041 85ce8d7 (11 file):  1736 passed, 16 xfailed
# Cây gộp T-088 + T-086 0782e9b (11 file):  951 passed, 11 xfailed
```

Script dò riêng: thư mục ghi chú chung `T-088-soi-loi-scripts/` (`fakesite2.py`, `probe_fields088.py`, `probe_json088.py`, `probe_page_surrogate.py`, `mutate088.py`; `probe_real_calls.py`, `fakesite.py` của T-060). Chạy bằng `.venv` của worktree, thư mục làm việc là worktree (`probe_page_surrogate.py` chạy bằng pytest trong một bản sao có `tests/`).

## Đối chiếu tiêu chí xong

- [x] 4 lỗi cũ đóng, thử bằng cách tái hiện cũ và biến thể: NUL, khoảng trắng `trim()` ở mọi vị trí, nhiều lớp; JSON lồng sâu, hỏng, mã hóa lạ ở mọi lệnh đọc câu trả lời; lệnh tải ảnh 5xx, hết giờ, mất kết nối, 201 hỏng thân
- [x] Không chặn oan: trang Kết nối WordPress, «Gửi nháp» (T-056, gộp thử T-086), ghi SEO
- [x] `xfail` gỡ chỉ xóa dấu; không test cũ nào bị sửa
- [x] Gộp thử với `origin/main` mới nhất, T-041, T-086
- [x] Lỗi mới có test `xfail(strict=True)`: SL-T088-1
- [x] Không sửa code ứng dụng

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** SL-T085-1, SL-T085-2, SL-T085-3, LC-T085-1 **đóng**. Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (SL-T088-1, có từ trước, cần website trả dữ liệu lỗi). **Chuyển Lá Chắn rút gọn được ngay.** Điều kiện: SL-T088-1 vào phiếu dọn sau, nên trước khi gộp T-041 (bước SEO dùng danh sách bài đã đăng), chậm nhất trước khi hết Giai đoạn 4.

## Đề xuất

1. (Thợ Máy, phiếu dọn sau) SL-T088-1: một hàm làm sạch chung cho mọi chữ website trả (bỏ hay thay surrogate lẻ), `is_site_link` từ chối địa chỉ có surrogate.
2. (Chỉ Huy) Báo Soi Lỗi, Lá Chắn T-041: `site_listing()` chỉ bắt `WordPressError`, `SiteIndexError`; lỗi lạ khi ghi cache (như `UnicodeEncodeError` của SL-T088-1) lọt ra bước SEO.

## Câu hỏi cho chủ dự án

Không có.

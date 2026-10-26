# Báo cáo T-085 · Dọn lỗi Thấp client WordPress sau T-060 (LC-T060-1, -2, -3, SL-T060-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-085](../tickets/T-085-don-client-wordpress-sau-t060.md) |
| Nhánh | `team/T-085` (từ `main` `8ae67f8`) |
| Ngày nộp | 2026-10-24 |
| Kết quả | **Hoàn thành**: đủ 5 yêu cầu. 1 test cũ phải sửa theo yêu cầu 3 (ngoài phạm vi phiếu cho sửa): đã hỏi, **Chỉ Huy B duyệt 2026-10-24**, commit riêng `9d37b97` (bảng trước/sau ở mục «Sửa 1 test cũ theo yêu cầu 3») |

## Tóm tắt (cho chủ dự án)

- Phần dữ liệu đi kèm mỗi lệnh phần mềm gửi lên website nay cũng có danh sách cố định cho từng loại lệnh. Một ô như «id» (đổi bài hay ảnh mà lệnh sửa) hay «name» (đổi việc mà lệnh chạy) không bao giờ đi ra được, và trạng thái bài chỉ được là «nháp».
- Phần mềm không bao giờ xin website trả về nội dung bài, đoạn trích, mô tả hay chú thích ảnh: website dựng các phần đó bằng cách chạy shortcode, nên nếu sau này có chữ lạ lọt vào lệnh thì shortcode cũng không chạy ngay trong lệnh của phần mềm.
- Trang Kết nối WordPress: nếu ảnh đã lên thư viện Media mà bước ghi alt, tiêu đề, chú thích hỏng (mất mạng, website lỗi), hoặc website trả lời về một ảnh khác, phần mềm báo rõ «Ảnh đã lên thư viện Media của website (mã ảnh N)… Vào Media → Thư viện… để kiểm, sửa hoặc xóa trước khi tải lại», thay vì chỉ «thử lại sau».
- Hôm nay chưa có đường nào khai thác được ba lỗi này; đây là chốt chặn cho các phiếu sau. Mọi việc thật của phần mềm (kiểm kết nối, chuyên mục, thẻ, bài đã đăng, tạo nháp, tải ảnh, ảnh đại diện, ghi SEO, gửi nháp kèm ảnh) vẫn chạy như cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `ALLOWED_JSON_KEYS` + kiểm khóa thân JSON, `status` (LC-T060-1); `_RENDERED_FIELDS` + `_asks_rendered_fields` (LC-T060-2); `upload_media` bọc lệnh ghi đè, câu cố định `_MEDIA_NOT_DESCRIBED` (LC-T060-3, SL-T060-1) |
| `tests/test_wordpress_t085.py` | Mới: 265 ca (chặn và đối chứng) |
| `tests/test_la_chan_t060.py` | Gỡ 4 dòng dấu `xfail` (12 ca: LC-T060-1 6, LC-T060-2 3, LC-T060-3 3), chỉ xóa dấu |
| `tests/test_soi_loi_t060.py` | Gỡ 1 dòng dấu `xfail` (2 ca SL-T060-1), chỉ xóa dấu |
| `tests/test_wordpress_round2_t042.py` | `test_upload_media_odd_fields_are_safe`: sửa theo yêu cầu 3, Chỉ Huy duyệt (bảng dưới) |

Không sửa `app/**`, `config/**`. Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible` (T-056 dùng lại); `ALLOWED_ROUTES`, `ALLOWED_PARAMS`, `_ROUTE_PARAMS` giữ nguyên dạng (test của Soi Lỗi T-060 sửa tạm `_ROUTE_PARAMS`).

## Cách sửa từng yêu cầu

1. **LC-T060-1 (khóa thân JSON).** `ALLOWED_JSON_KEYS` (`client.py:129`) cùng kiểu `ALLOWED_PARAMS`: khóa là đúng cặp trong `ALLOWED_ROUTES`, dựng `_ROUTE_JSON_KEYS` khi nạp module (`client.py:146`), thiếu đường nào là `KeyError` ngay lúc nạp. Danh sách theo đúng các thân JSON app đang gửi: `POST /wp/v2/posts` (`create_draft`): `status`, `title`, `content`, `excerpt`, `slug`, `categories`, `tags`, `featured_media`; `POST /wp/v2/posts/<mã>`: `featured_media` (ảnh đại diện), `meta` (SEO dự phòng); `POST /wp/v2/media/<mã>`: `alt_text`, `title`, `caption`; Abilities `/run`: `input`; mọi lệnh `GET` và `POST /wp/v2/media` (thân là byte ảnh): không khóa nào. Trong `_is_plain_request` (`client.py:209-217`): khóa phải là chữ, thuộc danh sách của đúng đường; lớp phụ `_FORBIDDEN_JSON_KEYS` (`client.py:152`) chặn `id`, `name` so trên chữ thường, phòng khi ai đó nới danh sách; `status` có mặt thì phải đúng chữ `"draft"` (kiểu `str`). Lệnh `GET` cũng không nhận khóa JSON nào vì WordPress đọc thân JSON ở mọi phương thức khi loại thân là JSON (`get_parameter_order`).
2. **LC-T060-2 (giá trị `_fields`).** `_asks_rendered_fields` (`client.py:245`) tách giá trị như `wp_parse_list` của WordPress (dấu phẩy, khoảng trắng), lấy tên trường là phần trước dấu chấm, so trên chữ thường với `_RENDERED_FIELDS` (`client.py:120`: `content`, `excerpt`, `description`, `caption`, `_embedded`, `_links`). Thêm một điều phiếu không ghi nhưng cần cho đúng mục đích: **`_fields` rỗng** (`""`, `","`, chỉ khoảng trắng) cũng bị chặn, vì khi đó WordPress trả **mọi** trường, kể cả `content` (`get_fields_for_response`: `wp_parse_list` rỗng thì lấy hết). Kiểm áp cho mọi khóa có chữ «fields» sau khi gập (`client.py:227`), nên kể cả khi ai đó nới `ALLOWED_PARAMS` với `" _fields"` (PHP bỏ dấu cách đầu tên) hay `_fields[]` vẫn bị kiểm. Chọn danh sách cấm như phiếu cho phép, nên **không phải sửa 9 ca test cũ** đang gửi `_fields` khác hằng (chúng vẫn qua).
3. **LC-T060-3 + SL-T060-1 (`upload_media`).** Lệnh ghi đè ba ô được bọc (`client.py:1125-1143`): mọi `WordPressError` (mã HTTP 4xx/5xx, chuyển hướng, mất mạng, hết giờ, SSL, câu trả lời không phải JSON, lệnh bị chặn vì mã ảnh quá dài) và câu trả lời không phải `dict` hay `_positive_id(updated.get("id")) != media_id` (như `_describe_draft_media`) đều thành câu cố định `_MEDIA_NOT_DESCRIBED` (`client.py:375`): «Ảnh đã lên thư viện Media của website (mã ảnh N) nhưng phần mềm không xác nhận được đã ghi alt, tiêu đề, chú thích cho ảnh đó (mã HTTP nếu có), nên ảnh có thể đang mang chữ WordPress tự lấy từ file. Vào Media → Thư viện trong trang quản trị WordPress, mở ảnh mã N để kiểm, sửa hoặc xóa trước khi tải lại (tải lại sẽ thêm một ảnh nữa). Chưa tạo bài nháp.» Mã ảnh là số đã kiểm (`_positive_id` ở `_post_media`); câu không chép lời máy chủ, địa chỉ hay alt của ảnh khác; `status_code`, `code` của lỗi gốc được giữ trong `WordPressError`. Khi câu trả lời đúng ảnh, `Media` lấy địa chỉ, alt từ chính câu trả lời đó như cũ. Cách này cũng xử lý Ghi nhận 4 của Soi Lỗi T-060 (mã ảnh quá 19 chữ số: trước đây câu báo «Không có gì được gửi lên website» trong khi ảnh đã lên).
4. **Không chặn oan.** Hai ca đối chứng của Lá Chắn T-060 (`test_lc_t060_doi_chung_than_json_va_fields_that_cua_app_van_gui`: 8 lệnh thật, so đúng khóa thân JSON và `_fields`; `test_lc_t060_3_doi_chung_ghi_de_thanh_cong_khong_bao_loi`) qua; ca đối chứng mới: tạo nháp đủ mọi trường tùy chọn rồi ghi SEO qua meta dự phòng (`test_than_json_that_cua_app_van_gui_du`), mọi hằng `_fields` của app trên đúng đường (`test_fields_hang_cua_app_van_gui`, 12 ca). Đủ 41 file test có dùng client WordPress qua (mục Bằng chứng), kể cả trên cây gộp với nhánh T-056.
5. **Gỡ `xfail` khi XPASS:** 5 dòng dấu (14 ca) đều XPASS thật trước khi gỡ, chỉ xóa dấu, không đổi thân test.

## Sửa 1 test cũ theo yêu cầu 3 (Chỉ Huy B duyệt 2026-10-24)

Commit riêng `9d37b97`. «Dòng cũ» theo `main` `8ae67f8`, «dòng mới» theo nhánh này. Không xóa `assert` nào khác; 2 dòng site giả giữ nguyên.

| File · test | Dòng cũ | Dòng mới | Lý do |
|---|---|---|---|
| `tests/test_wordpress_round2_t042.py` · `test_upload_media_odd_fields_are_safe` | 89: `media = client.upload_media(b"x", "a.png", alt_text="ảnh")`; 90: `assert (media.id, media.source_url, media.alt_text) == (5, "", "ảnh")` | 89: chú thích; 90-91: `with pytest.raises(WordPressError, match="thư viện Media") as err:` + `client.upload_media(b"x", "a.png", alt_text="ảnh")`; 92: `assert "mã ảnh 5" in str(err.value)` | Lệnh ghi đè trả `["không phải dict"]`, tức không nói đúng ảnh 5: yêu cầu 3 bảo phải báo câu cố định có «thư viện Media», mã ảnh, thay vì trả kết quả bình thường. Ý cũ «dữ liệu sai kiểu không làm vỡ» giữ: vẫn không vỡ, chỉ thành lỗi có câu cố định. Phần «trường sai kiểu» (`source_url` là số) chuyển sang ca mới `tests/test_wordpress_t085.py::test_tra_loi_dung_anh_nhung_truong_sai_kieu_khong_vo` (câu trả lời đúng ảnh 9, `source_url` 123, `alt_text` danh sách → `Media(9, "", "Cổng")`) |

## Bằng chứng

Bộ test mới chạy trên **code cũ** (`seo_app` của `8ae67f8` giải nén vào thư mục nháp, nạp qua `PYTHONPATH`; bản tạm của file test, đã xóa): **249 hỏng, 16 qua** (265 ca). Cả 16 ca qua là ca đối chứng: hằng `_fields` của app (12), `status` `"draft"`, thân JSON thật của app, ghi đè thành công, câu trả lời đúng ảnh có trường sai kiểu.

```
$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_wordpress_t085.py
265 passed in 3.75s

# Lượt cuối, 41 file: mọi file trong tests/ có "WordPressClient", "upload_media", "fake_wp",
# "seo_app.wordpress", "wp_client" hay "_request(" (không kể conftest.py), cộng test_app_pages.py
$ uv run pytest tests/test_ai_images.py tests/test_ai_t034.py tests/test_app_pages.py
    tests/test_app_t044_safe_text.py tests/test_app_wordpress.py tests/test_la_chan_t039.py
    tests/test_la_chan_t060.py tests/test_la_chan_t071.py tests/test_onpage_links.py
    tests/test_phase2_fixes.py tests/test_safety.py tests/test_sanitize.py tests/test_shortcode_t061.py
    tests/test_site_index.py tests/test_site_index_t042.py tests/test_soi_loi_t019_luot2.py
    tests/test_soi_loi_t031.py tests/test_soi_loi_t034.py tests/test_soi_loi_t037.py
    tests/test_soi_loi_t039.py tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py
    tests/test_soi_loi_t042_round2.py tests/test_soi_loi_t044.py tests/test_soi_loi_t054.py
    tests/test_soi_loi_t060.py tests/test_soi_loi_t061.py tests/test_soi_loi_t071.py
    tests/test_soi_loi_t075.py tests/test_soi_loi_t081.py tests/test_t081_alt_gach_cheo.py
    tests/test_wordpress_client.py tests/test_wordpress_images.py tests/test_wordpress_paging_t042.py
    tests/test_wordpress_published.py tests/test_wordpress_round2_t042.py
    tests/test_wordpress_routes_t042.py tests/test_wordpress_seo_meta_t042.py
    tests/test_wordpress_site_link_t042.py tests/test_wordpress_t060.py tests/test_wordpress_t085.py
5547 passed, 1 skipped, 8 xfailed in 286.18s (10:14:35–10:19:26)
# 8 xfail có sẵn, không thuộc T-085: LC-T039-2 (3), SL-T081-1 (5). 1 bỏ qua: symlink (Windows)

# Lượt phần 1 (commit 8226ed7), cùng 41 file:
1 failed, 5514 passed, 1 skipped, 13 xfailed in 428.33s (09:56:30–10:03:44)
# 13 xfail = 5 của phần 2 lúc đó (LC-T060-3 3, SL-T060-1 2) + 8 có sẵn. 1 hỏng oan khi máy bận:
# test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted (khóa SQLite, chờ 10 s).
$ uv run pytest "tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted"
1 passed in 15.89s
$ uv run pytest tests/test_soi_loi_t037.py
139 passed in 37.95s
```

**Cây gộp với T-056** (`git merge-tree --write-tree` `team/T-085` `9d37b97` + `origin/team/T-056` `6d0c2a7`: không xung đột; giải nén vào thư mục nháp, đã kiểm `seo_app.wordpress.client` và `seo_app.wordpress.shortcodes` nạp từ cây gộp). 13 file: 3 file T-056 (`tests/test_app_images.py`, `tests/test_soi_loi_t056.py`, `tests/test_wordpress_shortcodes.py`), gửi nháp kèm ảnh (`tests/test_wordpress_images.py`, `tests/test_soi_loi_t054.py`, `tests/test_soi_loi_t071.py`, `tests/test_shortcode_t061.py`), `tests/test_app_pages.py`, `tests/test_app_wordpress.py`, `tests/test_wordpress_round2_t042.py`, `tests/test_wordpress_t085.py`, `tests/test_la_chan_t060.py`, `tests/test_soi_loi_t060.py`, 10:21–10:28: **1722 passed, 5 xfailed, 0 hỏng**. 5 xfail là lỗi của chính T-056 (SL-T056-8 tới -11). `team/T-085` cũng không xung đột với `origin/main` `680ff74` (chỉ thêm 1 dòng vào phiếu).

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: khóa thân JSON theo đường, thiếu đường thì lỗi khi nạp module, không `id`/`name`, `status` chỉ `"draft"` (`test_moi_duong_co_danh_sach_khoa_json_khong_co_id_name`, `test_khoa_json_ngoai_danh_sach_cua_duong_bi_chan_truoc_khi_gui` 24 ca, `test_lenh_doc_khong_nhan_khoa_json_nao`, `test_status_khac_draft_bi_chan` 15 ca, `test_id_name_van_bi_chan_khi_danh_sach_khoa_bi_noi`; 6 ca Lá Chắn đã gỡ `xfail`)
- [x] Yêu cầu 2: `_fields` tách theo dấu phẩy, khoảng trắng, chặn 6 tên trường (và `_fields` rỗng) (`test_fields_hoi_truong_chay_shortcode_hay_rong_bi_chan` 168 ca, `test_gia_tri_fields_van_bi_kiem_khi_danh_sach_tham_so_bi_noi`; 3 ca Lá Chắn đã gỡ `xfail`)
- [x] Yêu cầu 3: câu cố định có «thư viện Media», mã ảnh, «Media → Thư viện» (`test_ghi_de_hong_thi_bao_anh_da_o_thu_vien_media` 13 ca, `test_tra_loi_ghi_de_khong_dung_anh_vua_tao_thi_bao_loi` 11 ca, `test_ma_anh_qua_dai_lenh_ghi_de_bi_chan_van_bao_anh_da_o_thu_vien`; 3 ca Lá Chắn + 2 ca Soi Lỗi đã gỡ `xfail`)
- [x] Yêu cầu 4: không chặn oan (ca đối chứng Lá Chắn T-060 qua; 41 file qua; cây gộp với T-056 qua)
- [x] Yêu cầu 5: gỡ `xfail` khi XPASS (5 dòng dấu, 14 ca)
- [x] `uv run ruff check .` sạch; báo cáo này
- [x] Không đổi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`; không sửa `app/**`, `config/**`

## Rủi ro và điểm cần chú ý

- **Lệnh không có `_fields`:** WordPress trả mọi trường (kể cả `content`) khi lệnh bài, ảnh không gửi `_fields`. Hôm nay mọi lệnh bài, ảnh của app đều gửi hằng `_fields` (ca đối chứng của Lá Chắn so đúng từng lệnh), nên đây là thiếu sót code, không phải chữ từ ngoài lọt vào. Bắt buộc có `_fields` thì phải sửa test cũ đang gọi `_request` không có `_fields` (ví dụ `tests/test_wordpress_routes_t042.py:167`): Đề xuất 1.
- **Danh sách khóa JSON chỉ ở cấp trên cùng** (như phiếu): khóa lồng bên trong `input` của Abilities (`postId`) và `meta` không bị kiểm. `postId` lấy từ mã bài đã qua `_created_post_ids` và `_own_draft` của `set_seo_meta`; `meta` chỉ có 2 khóa SiteSEO do code viết.
- **`_fields` theo danh sách cấm, không phải danh sách hằng tuyệt đối** (đúng lựa chọn phiếu cho phép): tên trường lạ vẫn đi ra; WordPress không trả gì cho tên không có trong khuôn, nên không chạy `the_content`.
- **Câu báo của `upload_media` ghi «Chưa tạo bài nháp.»** theo đúng luồng của nơi gọi duy nhất (trang Kết nối WordPress tải ảnh trước khi tạo nháp), giống `_MEDIA_NOT_CREATED`. Ảnh đã lên thì vẫn ở thư viện Media (phần mềm không có hàm xóa, W2); câu báo dặn người dùng tự kiểm, xóa.
- Nhận định về thứ tự đọc tham số và `wp_parse_list`, `get_fields_for_response` của WordPress lấy từ biên bản Lá Chắn T-060 (mục «Đối chiếu mã nguồn WordPress») và hiểu biết về mã lõi; tôi chưa thử trên site (không có staging). Chặn là an toàn dù nhận định sai.

## Đề xuất

1. (Lá Chắn xét, cần Chỉ Huy duyệt sửa test cũ) Bắt buộc có `_fields` trên các đường bài, ảnh (`/wp/v2/posts*`, `/wp/v2/pages`, `/wp/v2/media*`), để thiếu sót code cũng không làm WordPress dựng `content`.
2. (Còn từ T-060, Ghi nhận 3 của Lá Chắn) `_request` truyền `verify=True` tường minh, để `session` truyền từ ngoài (chỉ test dùng) không tắt được kiểm chứng chỉ SSL.
3. (Ghi nhận 4 của Lá Chắn T-060, tùy chọn) `upload_media` chưa `html.escape` tiêu đề, chú thích như `_describe_draft_media`. Không có đường tới (trang Kết nối WordPress chỉ truyền alt; tiêu đề là tên file đã làm sạch); làm thì phải sửa ca test cũ so đúng thân lệnh, nên không làm trong phiếu này.

## Câu hỏi cho chủ dự án

Không có. (Câu hỏi về 1 test cũ đã được Chỉ Huy B trả lời: đồng ý, 2026-10-24.)

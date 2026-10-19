# Báo cáo T-042 · Ghi meta SEO (SiteSEO) lên bài nháp trên WordPress

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Opus 5.5 |
| Phiếu | [T-042](../tickets/T-042-ghi-meta-seo-len-nhap.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | Hoàn thành (phần logic; giao diện chưa nối, xem "Đề xuất") |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã **biết ghi** tiêu đề SEO, mô tả SEO và từ khóa chính vào hộp SiteSEO của **bài nháp do chính nó vừa tạo**. Đường chính là Abilities của SiteSEO (anh bật trong SiteSEO); nếu chưa bật, phần mềm thử đường dự phòng (chỉ tiêu đề và mô tả); không được thì báo "chép tay", **không chặn** việc tạo nháp.
- Tính năng này **mặc định tắt**. Chưa có nút bật trên giao diện (việc của Họa Sĩ ở phiếu sau), nên hiện tại app vẫn chạy như cũ, không gửi gì thêm lên website.
- Không có đường nào ghi vào bài đã đăng: trước khi ghi, phần mềm hỏi lại website bài đó **còn là nháp không**; đã đăng (hay bị xóa) thì từ chối.
- Phần mềm chỉ được gọi **13 địa chỉ cố định** trên website; mọi địa chỉ khác (kể cả các địa chỉ nhạy cảm `code-snippets`, `prometal/v1/deploy-files`, `purge`) bị chặn **trước khi gửi**.
- Kèm theo: sửa 4 lỗi nhỏ còn lại từ T-037 (danh sách bài không bị thiếu lặng lẽ khi máy chủ giấu số trang; link có dấu lạ bị loại; file lưu tạm không bị xóa oan trên Windows; app không còn đứng ~14 giây khi file lưu tạm bị khóa).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | Danh sách đường cố định `ALLOWED_ROUTES` + `is_allowed_route`, kiểm trong `_request` trước khi gửi, `allow_redirects=False`, phản hồi 3xx báo lỗi câu cố định. `set_seo_meta` (+ `_own_draft`, `_siteseo_abilities`, `_seo_via_abilities`, `_seo_via_meta`, `_seo_text`, `_seo_error`), `SeoWriteResult`, tùy chọn `write_seo=False`. `ConnectionInfo.siteseo_writable` + `siteseo_status`; `check_connection` dò Abilities (chỉ `GET`). `create_draft` chỉ ghi nhận bài site trả `status == "draft"`. Phân trang `_get_pages_checked` mới (SL-T037-3), `_get_all_pages` dùng chung. `is_site_link` từ chối `" ' < > `` ` `` và ký tự Cf; `_clean_text` bỏ Cf; `PublishedItem` từ chối Cf (LC-T037-1 a, b) |
| `seo_app/wordpress/__init__.py` | Xuất thêm `SeoWriteResult`, `is_allowed_route` |
| `seo_app/storage/site_index.py` | Chỉ coi là hỏng khi chắc chắn (`_is_corrupt`: mã `SQLITE_CORRUPT`/`SQLITE_NOTADB`, kể cả mã mở rộng; `quick_check`; sai cột) ở cả `_is_healthy` và `load` (SL-T037-4). `get`: `load` thấy bận thì tải từ site, bỏ bước ghi; bước kiểm file chờ 1 giây (`_HEALTH_TIMEOUT`) (SL-T037-5). Câu báo riêng cho "không mở được" |
| `tests/test_wordpress_routes_t042.py` | Mới: danh sách đường, 49 đường xấu × 2 phương thức, phương thức sai, từ chối không request, chuyển hướng |
| `tests/test_wordpress_paging_t042.py` | Mới: SL-T037-3 (header thiếu/sai, 400 quá số trang, `MAX_PAGES`, máy chủ bỏ qua `page`, chuyên mục/thẻ) |
| `tests/test_wordpress_site_link_t042.py` | Mới: LC-T037-1 (a)(b) |
| `tests/test_site_index_t042.py` | Mới: SL-T037-4, SL-T037-5 (gồm khóa thật, đo thời gian) |
| `tests/test_wordpress_seo_meta_t042.py` | Mới: `set_seo_meta`, `check_connection` (174 test) |
| `tests/test_soi_loi_t037.py` | **Chỉ bỏ 2 dấu `xfail`** của lỗi đã sửa: `test_r2_missing_total_pages_header_is_not_silently_complete` (SL-T037-3, 4 trường hợp) và `test_r2_file_opened_by_other_program_share_delete_is_not_deleted` (SL-T037-4, chỉ chạy trên Windows) |

Không sửa `app/**`, `config/**`, `tests/conftest.py`, `seo_app/onpage/**` (chỉ **đọc** `_ENTITY`, `has_html`, `normalize_meta` của `seo_app/onpage/meta.py`, nhập muộn trong `_seo_text`). Không thêm thư viện.

## Thiết kế `set_seo_meta` (để Soi Lỗi, Lá Chắn soát)

```python
client = WordPressClient(..., write_seo=True)   # mặc định False
post = client.create_draft(...)
result = client.set_seo_meta(post.id, title=..., description=..., focus_keyword=...)
# result.written / route ("abilities"|"meta") / fields / reason ("", "disabled", "unavailable", "error") / message
```

Thứ tự kiểm (`client.py`, hàm `set_seo_meta` khoảng dòng 521):
1. `post_id` phải đúng kiểu `int` và nằm trong `_created_post_ids`; sai thì `WordPressError`, **không có request nào**.
2. `write_seo` tắt: trả `reason="disabled"`, không gửi gì.
3. Kiểm chữ (`_seo_text`): chuẩn hóa như `normalize_meta` (NFC, bỏ ký tự vô hình, gộp khoảng trắng); chặn thẻ HTML, mã ký tự HTML (`_ENTITY` của `meta.py` + `&#37` thiếu `;`), `%%`, ký tự điều khiển, quá dài; xét chữ gốc, chữ đã chuẩn hóa và dạng NFKC (`＜`, `％％`, `＆` toàn khổ). Câu lỗi chỉ có tên trường, không chép chữ người dùng. Trường rỗng/`None` bị bỏ (không gửi); tất cả rỗng thì từ chối.
4. `_own_draft`: `GET /wp/v2/posts/<id>?context=edit&_fields=id,status,meta`. Phải là dict, `id` đúng kiểu `int` và đúng số, `status == "draft"` đúng chữ. Sai thì từ chối **và bỏ id khỏi `_created_post_ids`** (nên `set_featured_image` cũng không còn sửa được bài đó). Lỗi khi hỏi thì câu cố định kèm mã HTTP.
5. Dò Abilities (`GET /wp-abilities/v1/abilities/siteseo-posts/seo-data-update`, nhớ kết quả True/False; 400/401/403/404 = chưa bật; lỗi mạng/5xx = chưa rõ, lần sau dò lại).
6. Có Abilities: `POST …/seo-data-update/run` với đúng `{"input": {"postId", "title"?, "description"?, "focus_keyphrase"?}}`. Không bao giờ có `null`, `status`, `canonical_url`, `robots`.
7. Không có: đường dự phòng `POST /wp/v2/posts/<id>` với **chỉ** `{"meta": {...}}` (2 khóa `_siteseo_titles_title`, `_siteseo_titles_desc`), chỉ khi `GET` ở bước 4 thấy cả 2 khóa. 400/401/403 hoặc máy chủ trả 200 mà không lưu đúng giá trị → `unavailable` (chép tay). Đường này không ghi được từ khóa chính (báo trong `message`).
8. Lỗi khi ghi → `reason="error"`, câu cố định kèm mã HTTP, không chép `message` của máy chủ.

## Bằng chứng

Chạy trên Windows 11, Git Bash, worktree `wt-T-042`.

```
$ uv run pytest
5952 passed, 11 skipped, 31 xfailed, 1 warning in 507.74s (0:08:27)
(0 hỏng, 0 lỗi. 31 xfail đều có từ trước trên main, không cái nào của T-042; 2 dấu xfail của SL-T037-3 và SL-T037-4 đã bỏ và các test đó qua. 1 warning là cảnh báo pydantic có từ trước)

$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_wordpress_seo_meta_t042.py tests/test_wordpress_routes_t042.py tests/test_wordpress_client.py tests/test_phase2_fixes.py tests/test_safety.py tests/test_app_wordpress.py tests/test_soi_loi_t031.py -q
1083 passed, 1 xfailed in 95.19s (0:01:35)

$ uv run pytest tests/test_site_index_t042.py -q
31 passed in 4.52s

$ uv run pytest tests/test_site_index.py tests/test_soi_loi_t037.py -q   (sau khi bỏ cả 2 xfail)
193 passed, 1 skipped in 41.07s
```

`1 skipped` là test liên kết tắt (symlink) có từ T-037 (Windows chưa bật Developer Mode). Commit: `a839e1f` (đường cố định), `3a6968f` (SL-T037-3), `ad91d31` (LC-T037-1), `07c8626` (SL-T037-4/5), `1525135` (`set_seo_meta`), cộng commit báo cáo này.

## Đối chiếu yêu cầu của phiếu

- [x] **YC1** `set_seo_meta(post_id, ...)`: dò đường B (Abilities) rồi A (meta); chỉ bài trong `_created_post_ids`; không gửi `null`; không đổi `status`. Test: `test_writes_through_abilities`, `test_falls_back_to_meta_when_abilities_off`, `test_post_not_created_by_app_is_refused_without_any_request`, `test_post_id_must_be_a_real_int`, `test_new_client_knows_no_post`, `test_never_sends_null_or_status` (5 tổ hợp × 2 đường, duyệt mọi giá trị lồng trong JSON), `test_only_fields_with_text_are_sent`
- [x] **Không có đường ghi bài đã đăng**: kiểm lại trên site ngay trước khi ghi; `test_post_no_longer_draft_on_site_is_refused` (9 trạng thái gồm `publish`, `future`, `" draft"`, `"Draft"`, `None`), `test_site_answer_for_other_post_is_refused`, `test_create_draft_answer_not_draft_is_not_recorded`
- [x] **YC2** danh sách đường REST cố định, từ chối đường khác: `ALLOWED_ROUTES` (`client.py:55`), `is_allowed_route` (`:76`), kiểm ở đầu `_request` (`:731`). Test: `test_allowed_route_list_is_exactly_the_reviewed_one`, `test_other_paths_are_refused`, `test_wrong_method_or_type_is_refused`, `test_client_refuses_before_any_request`, `test_public_methods_only_use_allowed_routes`, `test_every_request_is_on_the_allowed_list`
- [x] **YC3** `check_connection` báo "SiteSEO: ghi được / chưa bật": `ConnectionInfo.siteseo_writable`, `siteseo_status`; test `test_check_connection_reports_siteseo` (8 trường hợp). Dò lỗi không làm hỏng kiểm tra kết nối. *Giao diện chưa hiện dòng này* (không được sửa `app/**`)
- [x] **YC4** lỗi không chép thông điệp máy chủ: mọi câu của `set_seo_meta` là hằng `_SEO_*` (+ mã HTTP); test với `SERVER_SECRET` ở `test_draft_check_failure_raises_fixed_message`, `test_ability_error_gives_fixed_message`, `test_meta_route_*`, `test_ability_network_error_gives_fixed_message`. Câu từ chối đường không chép đường (`test_client_refuses_before_any_request`)
- [x] **YC5** test bằng site giả: bài không do app tạo → từ chối; đường lạ → từ chối (như trên). Không test nào gọi mạng thật (`FakeWordPress`, bộ chặn mạng của `conftest.py` không đổi)
- [x] **Ghi chú 16/10**: tùy chọn, mặc định tắt (`test_seo_write_is_off_by_default`, `test_only_real_true_turns_seo_write_on`, `test_from_settings_passes_write_seo`); dò không thấy đường ghi thì trả `unavailable`, không ném lỗi (`test_no_ability_means_no_ability_call`, `test_meta_route_*`)

## Đối chiếu điều kiện Lá Chắn

- [x] **LC-T036-3** chặn thực thể HTML trước khi gửi, dùng `_ENTITY`: `_seo_text`; thêm `&#37` thiếu `;` và `＆` toàn khổ. Test `test_bad_text_is_blocked_before_any_request` (16 chuỗi × 3 trường, không request nào đi ra); chữ thường như `< 5 triệu`, `&`, `10%`, `Q&A` vẫn qua (`test_ordinary_text_passes`)
- [x] **T-037 điểm 1, SL-T037-3** (bắt buộc trước Giai đoạn 5): `_get_pages_checked`, `_get_all_pages`, `_total_pages`. Đã bỏ `xfail` `test_r2_missing_total_pages_header_is_not_silently_complete`; thêm `tests/test_wordpress_paging_t042.py` (header `None`, `""`, `"abc"`, `"60.0"`, `"-5"`, `"0"`, `"1e2"`, `" "`, chữ số Ả Rập; 300 mục đúng 3 trang; 400 `rest_post_invalid_page_number`; vượt `MAX_PAGES` → `truncated`; máy chủ bỏ qua `page` → dừng, `truncated`; header đúng vẫn được tin)
- [x] **T-037 điểm 2**, đường cố định trong `_request`: so toàn chuỗi `(method, path)`, từ chối trước khi gửi, chặn `..`, `%` (gồm `%2e`), `//`, `\`, `code-snippets`, `prometal` (không phân biệt hoa thường). Danh sách = đề xuất T-037, **bớt** `GET …/seo-data-get/run` (không dùng) và **thêm** `GET /wp/v2/posts/<id>` (kiểm còn nháp) và `GET` thông tin ability (dò). Thêm: không đi theo chuyển hướng (`test_redirect_is_not_followed`, 301/302/303/307/308)
- [x] **T-037 điểm 3, LC-T037-1 (a)(b)**: `is_site_link`, `_clean_text`, `PublishedItem`; `tests/test_wordpress_site_link_t042.py`
- [x] **T-037 điểm 4, SL-T037-4**: cả `_is_healthy` và `load` (`_load_checked`); đã bỏ `xfail` `test_r2_file_opened_by_other_program_share_delete_is_not_deleted` (Windows, mở thật bằng `CreateFileW`, qua); `tests/test_site_index_t042.py` (14 mã lỗi, file SQLite thật bị ghi đè giữa chừng vẫn bị bỏ, sai cột vẫn bị bỏ)
- [x] **T-037 điểm 5, SL-T037-5**: `get` không ghi khi `load` đã thấy bận; chờ 1 giây thay vì 2 × 5 giây. `test_get_skips_second_write_when_file_is_busy`, `test_get_on_locked_file_returns_quickly` (khóa thật bằng `BEGIN EXCLUSIVE`, giới hạn rộng `< 5 giây` để không chập chờn)
- [x] Không vi phạm R1–R11: không bí mật, không `publish`/`future` (không thêm khóa `status` nào; `test_client_has_no_publish_function` và test cây cú pháp của T-037 vẫn qua), không xóa/ghi đè bài đã có, không `verify=False`, không thư viện mới

## Rủi ro và điểm cần chú ý

- **Chưa thử trên site thật** (đúng phiếu). Khuôn `input`/kết quả của ability lấy từ mã nguồn SiteSEO 1.4.2 (T-033 mục 1.4); kết quả trả về chỉ được kiểm `success is False` (không biết chắc khuôn). Phiếu thử thật phải mở hộp SiteSEO xem đúng chữ.
- Đường Abilities: phần mềm **không đọc lại** giá trị sau khi ghi (không gọi `seo-data-get` để giữ danh sách đường ngắn). Đường dự phòng thì có so lại.
- Kiểm "còn là nháp" rồi mới ghi: vẫn có khe thời gian rất ngắn giữa 2 lệnh (người dùng bấm Đăng đúng lúc đó). Muốn khai thác phải là chính người dùng trong trang quản trị; không có đường nào từ dữ liệu ngoài.
- `create_draft` giờ chỉ ghi nhận bài khi site trả `status == "draft"`; site trả khác (do plugin lạ) thì ảnh đại diện và SEO của bài đó bị từ chối (theo chiều an toàn).
- Không đi theo chuyển hướng nữa: nếu `WORDPRESS_URL` khai thiếu/thừa `www` mà site chuyển hướng, app sẽ báo lỗi rõ ràng thay vì tự đi theo. Trước đây `requests` cũng đã bỏ mật khẩu khi đổi tên máy nên trường hợp này vốn không chạy được.
- `_error_from` chung (dùng cho các hàm cũ) **vẫn** kèm `(WordPress: …)` vì test cũ yêu cầu; chỉ các câu của `set_seo_meta` là cố định hoàn toàn.
- Chặn `_ENTITY` có thể chặn oan chữ hiếm kiểu `R&D;`. Người dùng sửa chữ là gửi được.

## Đề xuất

- **Họa Sĩ (phiếu giao diện):** thêm công tắc "Ghi SEO lên website" (mặc định tắt) → `WordPressClient(..., write_seo=True)`; sau `create_draft` gọi `set_seo_meta`, hiện `result.message` bằng widget chữ thường; bắt `WordPressError` và hiện `str(exc)`, không chặn bài nháp đã tạo. Trang Kết nối WordPress hiện thêm `info.siteseo_status`. Tiêu đề truyền vào đã gắn đuôi " | Pro-Metal" bằng `with_brand` (không làm trong client).
- **Soi Lỗi nên thử kỹ:** đổi `status` bài giả giữa các bước; câu trả lời của site dạng lạ (list, chuỗi, `id` kiểu chữ/bool); chữ SEO có thực thể/thẻ dạng biến thể Unicode; header `X-WP-TotalPages` lạ; chuyển hướng; file cache bị khóa/mở chế độ lạ trên Windows.
- **Lá Chắn nên soát kỹ:** `set_seo_meta` + `_own_draft` (đường duy nhất ghi meta), `ALLOWED_ROUTES`/`is_allowed_route`, chỗ `_request` thêm `allow_redirects=False`.
- **Phiếu thử thật (sau phiếu này):** trước khi thử, chủ dự án cần (1) bật **Abilities** trong SiteSEO, (2) tạo tài khoản vai **Biên tập viên** riêng + Application Password, khai vào `.env`. Thử 1 bài nháp, mở trang quản trị xem hộp SiteSEO đúng tiêu đề, mô tả, từ khóa chính, rồi xóa nháp bằng tay.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-19) · sửa theo Soi Lỗi (`T-042-soi-loi.md`) và LC-T044-1

### Tóm tắt (cho chủ dự án)

Sửa đủ 7 lỗi Soi Lỗi tìm thấy và 1 lỗi Lá Chắn chuyển sang từ T-044:
- Danh sách bài đã đăng không còn bị thiếu lặng lẽ khi website có bộ đệm trang.
- Ảnh đại diện cũng phải hỏi lại website "bài còn là nháp không" trước khi ghi.
- Phần mềm chỉ báo "Đã ghi SEO" khi SiteSEO xác nhận rõ. Tôi đã đọc mã nguồn SiteSEO 1.4.2 để biết đúng khuôn câu trả lời.
- Website trả dữ liệu lạ thì app báo câu tiếng Việt, không còn hiện màn hình lỗi kỹ thuật.

### Bước 0

`git pull` (đã mới nhất, `5df3266`), `git merge origin/main` (merge, không rebase) → `6eac892`, `uv sync`, push.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | Toàn bộ sửa mục 1–8 và phần "nên làm" (chi tiết ở bảng đối chiếu) |
| `tests/test_wordpress_round2_t042.py` | Mới, 138 test: SL-T042-2…7, LC-T044-1, khe kiểm-rồi-ghi |
| `tests/test_wordpress_paging_t042.py` | Thêm 3 test SL-T042-1 |
| `tests/test_soi_loi_t042.py`, `tests/test_soi_loi_t042_paging_cache.py` | **Chỉ bỏ dấu `xfail`** (danh sách dưới) |
| `tests/test_wordpress_client.py` (`test_set_featured_image`), `tests/test_phase2_fixes.py` (`test_featured_image_allowed_only_for_own_draft`), `tests/test_safety.py` (`test_every_write_request_to_posts_never_publishes`) | Mỗi test **thêm đúng 1 dòng** `fake_wp.on("GET", "/wp-json/wp/v2/posts/<id>", {"id": …, "status": "draft"})`. Lý do: mục 3 bắt `set_featured_image` hỏi lại site trước khi ghi, mà site giả của các test cũ không có đường đó (trả 404). Không đổi điều gì các test này kiểm |
| `tests/test_wordpress_seo_meta_t042.py`, `tests/test_wordpress_routes_t042.py` (test của tôi) | Theo thứ tự mới (dò Abilities trước): đổi 1 dòng kiểm "không gọi ability" thành "không gọi lệnh ghi `run`". Thêm route `GET` bài nháp. Bỏ trường hợp `[]` ở test meta: trường hợp này giờ báo `error` thay vì `unavailable`, đã có test riêng ở file lượt 2 |

**Các `xfail` đã bỏ** (36 trường hợp, 8 dấu):
- `tests/test_soi_loi_t042_paging_cache.py`:
  - `test_valid_header_but_server_ignores_page_is_not_silently_complete` (SL-T042-1, 3 trường hợp)
  - `test_site_link_refuses_ignorable_not_cf` (SL-T042-7, 7 trường hợp)
  - `test_clean_text_drops_ignorable_not_cf` (SL-T042-7, 7 trường hợp)
- `tests/test_soi_loi_t042.py`:
  - `test_create_draft_odd_id_answer_is_not_recorded` (SL-T042-4, 5 trường hợp)
  - `test_featured_image_is_not_set_on_post_published_after_creation` (SL-T042-5, 1 trường hợp)
  - `test_base_url_cannot_turn_allowed_route_into_another` (SL-T042-3, 3 trường hợp)
  - `test_legacy_entities_without_semicolon_are_blocked` (SL-T042-2, 4 trường hợp)
  - `test_ability_answer_without_confirmation_is_not_written` (SL-T042-6, 6 trường hợp)

Hai file test của Soi Lỗi giờ không còn `xfail` nào.

### Đối chiếu mục 1–8

1. **SL-T042-1** (Trung bình): `_get_pages_checked` so `data == previous` **bất kể có header hay không**. Trùng thì dừng và bật `truncated`. Thêm: lỗi `rest_post_invalid_page_number` chỉ được coi là "đã hết" khi trang trước **thiếu** header; header nói còn trang mà máy chủ báo quá số trang thì báo lỗi. `_get_all_pages` dùng chung hàm này. Test: `test_valid_header_but_page_ignored_flags_truncated` (header 2, 3, 50, 999), `test_categories_with_header_and_page_ignored_do_not_repeat`, `test_out_of_range_with_known_header_still_raises`.
2. **SL-T042-4**: hàm mới `_positive_id` (đúng kiểu `int`, không phải `bool`, > 0).
   - `_post_from` (dùng cho `create_draft`, `set_featured_image`): id sai thì `WordPressError` câu cố định, không ghi nhận gì.
   - `upload_media`: id sai thì báo lỗi **trước** lệnh `POST /wp/v2/media/<id>`.
   - Test: `test_create_draft_with_odd_id_raises_and_records_nothing` (10 kiểu id), `test_upload_media_with_odd_id_raises_without_second_request`.
3. **SL-T042-5**: `set_featured_image` làm theo thứ tự:
   - kiểm `type(post_id) is int` và có trong `_created_post_ids`;
   - mã ảnh phải là số nguyên dương;
   - gọi `_own_draft` ngay trước lệnh ghi. Bài không còn nháp thì từ chối và bỏ id; không hỏi được site thì báo câu cố định riêng cho ảnh.
   - Test: `test_featured_image_refused_when_post_no_longer_draft` (5 trạng thái), `test_featured_image_still_works_on_own_draft` (thứ tự `GET` rồi `POST`), `test_featured_image_post_id_must_be_int`, `test_featured_image_media_id_must_be_positive_int`, `test_featured_image_check_failure_has_fixed_message`.
4. **SL-T042-6**: đọc mã nguồn SiteSEO 1.4.2 (`plugins.svn.wordpress.org/siteseo/tags/1.4.2/main/abilitiesregister.php`, hàm `update_post_seo_data`):
   - Thành công: trả `{"updated": true, "post": post_snapshot}`; `post_snapshot` có `title`, `description`, `focus_keyphrase`…, không có `id` hay `status`.
   - Lỗi: trả `WP_Error` `invalid_post` / `forbidden`.
   - `_ability_confirms` chỉ coi là đã ghi khi câu trả lời là dict, không có `code`, có `updated is True` (hoặc `success is True`, giữ để tương thích). Có `post` thì mọi trường đã gửi phải bằng đúng giá trị đã lưu. Còn lại là `reason="error"`, câu cố định.
   - Test: `test_ability_confirmed_answer_is_written`, `test_ability_answer_not_confirming_is_not_written` (12 trường hợp: `"true"`, `1`, `false`, `code`, giá trị lưu khác, thiếu trường, `post` không phải dict…), `test_ability_snapshot_must_match_every_sent_field`.
5. **SL-T042-2**: `_LEGACY_ENTITY` dựng từ các tên trong `html.entities.html5` **không có** `;` (106 tên, phân biệt hoa thường). Kiểm trên chữ gốc, chữ đã chuẩn hóa và dạng NFKC. Test: `test_legacy_entities_without_semicolon_blocked` (9 chuỗi). `R&D`, `AT&T`, `Q&A`, `P&G`, `&Lt` vẫn qua (`test_plain_ampersand_still_passes`).
6. **SL-T042-3**: `_is_plain_site_url` kiểm trong `__init__`. Chỉ nhận `https://tên-máy[:cổng][/thư-mục]`; từ chối:
   - tên/mật khẩu trong địa chỉ;
   - `?`, `#`, `%`, `\`, khoảng trắng;
   - đoạn `.` / `..`, `//`;
   - `wp-json`, `code-snippets`, `prometal`, `wp-admin`.
   - Câu lỗi không chép địa chỉ. Test: `test_odd_wordpress_url_is_refused` (19 địa chỉ), `test_normal_wordpress_url_is_accepted` (8 địa chỉ, gồm thư mục con, cổng, punycode).
7. **SL-T042-7**: `_has_invisible` / `_drop_invisible` xét cả loại Cf lẫn `IGNORABLE_NOT_CF` của `seo_app/content/rules.py` (nhập muộn, cùng quy ước với `normalize_meta`). Dùng ở `is_site_link`, `_clean_text`, `PublishedItem`. Test: `test_ignorable_not_cf_is_dropped_and_refused` (9 ký tự).
8. **LC-T044-1**: dữ liệu sai kiểu không làm vỡ trang nữa:
   - `_plain` nhận mọi kiểu: chữ giữ nguyên; số nguyên/thực đổi thành chữ; `bool`, `None`, list, dict thành `""`.
   - `check_connection`: `namespaces` phải là list; `me` không phải dict thì `WordPressError` câu cố định; `capabilities` không phải dict thì coi như rỗng, quyền chỉ tính khi đúng `True`; `roles` chỉ giữ phần tử là chữ; `site_url` chỉ lấy khi là chữ.
   - `_list_terms`: bỏ mục không phải dict hoặc id sai; `count`/`parent` sai kiểu thành 0.
   - `_post_from`, `upload_media`: như mục 2; `status`, `link`, `source_url`, `alt_text` sai kiểu thành giá trị mặc định.
   - Test: `test_check_connection_odd_names_do_not_crash` (6 kiểu), `test_check_connection_me_not_dict_raises_fixed_error`, `test_check_connection_namespaces_must_be_a_list`, `test_check_connection_odd_fields_are_safe`, `test_check_connection_roles_not_list`, `test_terms_with_odd_items_are_skipped_or_coerced`, `test_post_answer_odd_fields_are_safe`, `test_upload_media_odd_fields_are_safe`, `test_create_draft_with_odd_answer_raises`.

**Phần "nên làm" (đã làm):**
- `set_seo_meta` giờ dò Abilities trước, rồi gọi `_own_draft` ngay trước lệnh ghi (`test_draft_check_is_the_last_request_before_writing`, cả 2 đường).
- Đường dự phòng: câu trả lời của lệnh ghi phải đúng `id` và `status == "draft"`, không thì `reason="error"` (`test_meta_route_write_answer_must_be_same_draft`, 5 trường hợp).

### Bằng chứng (lượt 2)

Windows 11, Git Bash, worktree `wt-T-042`.

```
$ uv run pytest
6465 passed, 11 skipped, 30 xfailed, 1 warning in 661.80s (0:11:01)
(0 hỏng, 0 lỗi. Không còn xfail nào của T-042: 2 file test Soi Lỗi T-042 không còn dấu xfail. 30 xfail còn lại có từ trước trên main, ở file của phiếu khác. 1 warning pydantic có từ trước)

$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_wordpress_round2_t042.py -q
138 passed in 13.41s

$ uv run pytest tests/ -q -k "wordpress or soi_loi_t042 or phase2 or safety or t031 or t044 or site_index or t037 or app or config"
2154 passed, 1 skipped, 4299 deselected in 204.73s (0:03:24)
```

Commit lượt 2:
- `6eac892`: gộp main
- `e382fb7`: SL-T042-1
- `5e66aeb`: SL-T042-4, -5, -6, khe kiểm-rồi-ghi, LC-T044-1
- `5684fa8`: SL-T042-2, -3, -7
- cộng commit báo cáo này

### Rủi ro còn lại (lượt 2)

- Vẫn còn khe rất ngắn giữa lệnh kiểm nháp và lệnh ghi (2 request liền nhau). Đường dự phòng phát hiện được sau khi ghi (câu trả lời có `status`). Đường Abilities thì không, vì câu trả lời của SiteSEO không có `status`.
- `{"success": true}` vẫn được nhận như "đã ghi" để tương thích với site giả của bộ test. Khuôn thật của SiteSEO là `updated`. Phiếu thử thật nên ghi lại câu trả lời thật để bỏ nhánh `success` nếu không cần.
- `_LEGACY_ENTITY` chặn cả chữ ghép hiếm như `&notice` (bắt đầu bằng tên cũ `not`). Người dùng chỉ cần thêm dấu cách sau `&` là gửi được.
- `WORDPRESS_URL` có `/wp-admin` hay `/wp-json` giờ bị từ chối ngay khi mở app: báo câu tiếng Việt, không chạy tiếp.

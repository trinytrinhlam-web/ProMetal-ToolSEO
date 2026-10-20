# Báo cáo T-042 · Kiểm thử ghi meta SEO (SiteSEO) lên bài nháp

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Opus 5.5 |
| Phiếu | [T-042](../tickets/T-042-ghi-meta-seo-len-nhap.md) |
| Ngày nộp | 2026-10-19 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

- Tôi đã thử nhiều cách để phần mềm ghi SEO vào **bài đã đăng** (đổi trạng thái bài giữa các bước, site trả lời sai kiểu, số bài giả mạo…). `set_seo_meta` **chặn được hết**: luôn hỏi lại website bài còn là nháp không rồi mới ghi.
- Danh sách 13 địa chỉ được gọi giữ vững trước 90+ địa chỉ xấu (`..`, `%2e`, `//`, chữ hoa, `code-snippets`, `prometal`, chữ số toàn khổ, gạch chéo Unicode…) và không đi theo chuyển hướng ở bước nào. Cách duy nhất làm lệch là **khai `WORDPRESS_URL` có dấu `?` hoặc `#`** trong `.env` (lỗi Thấp, chỉ chủ máy sửa được file này).
- Tìm thấy **7 lỗi: 1 Trung bình, 6 Thấp**. Lỗi Trung bình: nếu website có bộ đệm bỏ qua số trang, danh sách bài đã đăng bị **thiếu mà không báo** (cùng loại SL-T037-3, bắt buộc xong trước Giai đoạn 5).
- Toàn bộ test chạy xanh trên Windows; 36 test mới đánh dấu "lỗi đã biết" chờ Thợ Máy sửa.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t042.py` | Mới: `set_seo_meta`/`_own_draft` (trạng thái đổi giữa các bước, câu trả lời lạ, `post_id` lạ, lớp con của `int`), đường dự phòng meta, câu lỗi cố định (8 nhánh lỗi, không lộ lời máy chủ/mật khẩu), 45 đường xấu, chuyển hướng 300–399 ở cả 4 bước, chặn chữ SEO (18 chuỗi × 3 trường), `xfail` SL-T042-2…6 |
| `tests/test_soi_loi_t042_paging_cache.py` | Mới: phân trang (header lạ, header lặp bị gộp, máy chủ trả trang xoay vòng, trang 2 hỏng), `_total_pages`, ký tự vô hình loại Cf và ngoài Cf, cache bị chương trình khác giữ trên Windows (7 chế độ chia sẻ + khóa vùng byte, mở thật bằng `CreateFileW`/`LockFileEx`), `xfail` SL-T042-1, SL-T042-7 |
| `docs/team/reports/T-042-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `conftest.py`, `timing.py`, test của agent khác.

## Bằng chứng

Windows 11, Git Bash, worktree `wt-T-042`.

```
$ uv run ruff check .
All checks passed!

$ uv run pytest            (trước khi thêm test, HEAD 6a02005)
5952 passed, 11 skipped, 31 xfailed, 1 warning in 740.08s (0:12:20)

$ uv run pytest            (sau khi thêm test)
6199 passed, 11 skipped, 67 xfailed, 1 warning in 613.08s (0:10:13)
(0 hỏng. +247 qua, +36 xfail đều của Soi Lỗi T-042; 31 xfail cũ và 1 warning pydantic có từ trước)

$ uv run pytest tests/test_soi_loi_t042.py -q
196 passed, 19 xfailed in 4.68s

$ uv run pytest tests/test_soi_loi_t042_paging_cache.py -q
51 passed, 17 xfailed in 32.77s
```

36 `xfail` mới = 7 lỗi dưới đây (SL-T042-1: 3, -2: 4, -3: 3, -4: 5, -5: 1, -6: 6, -7: 14). Mọi `xfail` đều `strict=True`: Thợ Máy sửa xong thì test báo XPASS, phải bỏ dấu.

## Lỗi tìm thấy

### SL-T042-1 · Trung bình · Header số trang đúng nhưng máy chủ bỏ qua `page`: thiếu bài lặng lẽ

- **Tái hiện:** site giả trả mọi trang `GET /wp/v2/posts?page=N` y hệt trang 1, kèm `X-WP-TotalPages: 3` (đúng là hành vi của plugin cache/CDN bỏ qua chuỗi truy vấn: trả lại nguyên phản hồi trang 1, cả header). `list_published()`.
- **Mong đợi:** đủ 300 bài, hoặc `truncated=True`.
- **Thực tế:** 100 bài (300 bài lặp, bỏ trùng còn 100), `truncated=False`. `_get_pages_checked` chỉ so trang trùng khi **thiếu** header (`client.py` khoảng dòng 463: `if total_pages is None and data and data == previous`). Chuyên mục/thẻ (`_get_all_pages`) cũng vậy.
- **Test:** `test_valid_header_but_server_ignores_page_is_not_silently_complete` (header 2, 3, 5).
- **Gợi ý sửa:** so `data == previous` bất kể có header hay không; trùng thì dừng và `truncated=True`.

### SL-T042-2 · Thấp · Thực thể HTML tên cũ thiếu `;` lọt bộ chặn (LC-T036-3)

- **Tái hiện:** `set_seo_meta(42, title="Cửa &ltscript&gt")` (cả `&lt b &gt`, `&amp`, `&copy 2026`).
- **Mong đợi:** chặn như `&#37` thiếu `;` mà Thợ Máy đã chặn: trình duyệt vẫn giải mã các tên cũ (`lt`, `gt`, `amp`, `quot`, `nbsp`, `copy`, `reg`…) khi thiếu `;`.
- **Thực tế:** gửi nguyên văn lên SiteSEO. `_ENTITY` của `meta.py` bắt buộc `;`; `_NUMERIC_REF` chỉ bắt dạng số. Nếu SiteSEO in nguyên văn, khách thấy `<script>` trên tab trình duyệt (chỉ hiện chữ, không chạy mã).
- **Test:** `test_legacy_entities_without_semicolon_are_blocked`. Đối chứng `R&D`, `AT&T`, `A & B`, `a&#` vẫn qua (`test_ampersand_without_entity_still_passes`).
- **Gợi ý sửa:** chặn thêm `&` + tên trong `html.entities.html5` không có `;` (danh sách tên cũ, phân biệt hoa thường).

### SL-T042-3 · Thấp · `WORDPRESS_URL` có `?` hoặc `#` làm request thật đi ra ngoài danh sách đường

- **Tái hiện:** `WordPressClient("https://example.com/wp-json/code-snippets/v1/snippets#", …).create_draft(…)` → request thật `POST https://example.com/wp-json/code-snippets/v1/snippets` (phần `/wp-json/wp/v2/posts` thành fragment). Với `https://example.com/?rest_route=/code-snippets/v1/snippets&x=` WordPress hiểu đường là `rest_route`. Tương tự `…/prometal/v1/purge?`.
- **Mong đợi:** danh sách đường là đường **thật** được gọi; client từ chối `base_url` có query, fragment, `..`, `%`, `wp-json`, `code-snippets`, `prometal`.
- **Thực tế:** `is_allowed_route` chỉ kiểm phần ghép sau `base_url`; hàm khởi tạo chỉ kiểm `^https?://[^/\s]+` (cho qua `?`, `#`, `@`).
- **Mức Thấp** vì `WORDPRESS_URL` chỉ đến từ `.env` của chủ máy (không có giao diện sửa). Vẫn nên chặn vì đây là chốt chặn cuối của danh sách đường (Lá Chắn T-037 điểm 2).
- **Test:** `test_base_url_cannot_turn_allowed_route_into_another` (3 địa chỉ).

### SL-T042-4 · Thấp · `create_draft` nhận `id` sai kiểu nên ghi nhận nhầm bài khác là "bài app tạo"

- **Tái hiện:** site trả lời tạo nháp `{"id": true, "status": "draft"}` (hay `"7"`, `" 8 "`, `7.9`, `"0042"`). `_post_from` dùng `int(data["id"])`: `True` thành bài **1**, `7.9` thành bài 7, rồi `create_draft` thêm vào `_created_post_ids`.
- **Mong đợi:** chỉ ghi nhận khi `type(id) is int` và `id > 0` (như `_own_draft` đã làm).
- **Thực tế:** bài 1 / bài 7 (có thể là bài đã đăng) được coi là bài app tạo. `set_seo_meta` vẫn an toàn nhờ hỏi lại trạng thái, nhưng `set_featured_image` thì không (xem SL-T042-5). Cần site trả lời sai/bị xâm nhập mới xảy ra.
- **Test:** `test_create_draft_odd_id_answer_is_not_recorded` (5 trường hợp).

### SL-T042-5 · Thấp · `set_featured_image` vẫn ghi được vào bài đã đăng

- **Tái hiện:** `create_draft` (bài 42 nháp) → người dùng bấm Đăng trong trang quản trị → `set_featured_image(42, 7)` → `POST /wp/v2/posts/42 {"featured_media": 7}` được gửi.
- **Mong đợi:** báo cáo Thợ Máy ghi "không có đường nào ghi vào bài đã đăng"; hàm này cũng phải hỏi lại `_own_draft` trước khi ghi.
- **Thực tế:** chỉ kiểm `post_id in _created_post_ids` (cũng không kiểm `type(post_id) is int`; `True`/`42.0` bị danh sách đường chặn lại nên chưa hại). Có từ Giai đoạn 1, không phải code mới của T-042; giao diện hiện **chưa gọi** hàm này (`app/` chỉ gọi `create_draft`), nên rủi ro còn ngủ. Phải sửa trước phiếu nối ảnh đại diện vào giao diện.
- **Test:** `test_featured_image_is_not_set_on_post_published_after_creation`.

### SL-T042-6 · Thấp · Kết quả Abilities không xác nhận vẫn báo "Đã ghi SEO"

- **Tái hiện:** `POST …/seo-data-update/run` trả 200 với `{"success": "false"}`, `{"success": 0}`, thân lỗi WordPress `{"code": "rest_forbidden", …}`, `[]`, `"ok"`, `null`.
- **Mong đợi:** không coi là đã ghi (hoặc ít nhất báo "chưa chắc, kiểm lại hộp SiteSEO"), vì người dùng dựa vào câu này để quyết định có chép tay không.
- **Thực tế:** `written=True`, "Đã ghi SEO vào hộp SiteSEO của bài nháp." (`_seo_via_abilities` chỉ bắt `success is False`; đường này cũng không đọc lại). Thợ Máy đã ghi rủi ro này; phiếu thử thật cần ghi lại đúng khuôn trả lời để siết.
- **Test:** `test_ability_answer_without_confirmation_is_not_written` (6 trường hợp).

### SL-T042-7 · Thấp · Ký tự vô hình không thuộc loại Cf lọt `is_site_link` và `_clean_text` (LC-T037-1 b)

- **Tái hiện:** `is_site_link("https://example.com/cuaㅤsat/", …)` là `True`; `_clean_text("Cửaㅤ sắt", 50)` giữ nguyên ký tự. Tương tự U+115F, U+1160, U+FFA0, U+034F, U+FE0F, U+180B.
- **Mong đợi:** cùng quy ước với `normalize_meta` của `meta.py` (bỏ cả `IGNORABLE_NOT_CF` của `seo_app/content/rules.py`).
- **Thực tế:** client chỉ xét loại Cf. Hại thấp (chữ hiển thị lạ, link giả dạng); không thoát được `href`.
- **Test:** `test_site_link_refuses_ignorable_not_cf`, `test_clean_text_drops_ignorable_not_cf` (7 ký tự mỗi test).

## Đã thử, không thấy lỗi

- **Ghi bài đã đăng qua `set_seo_meta`:** nháp lúc tạo, đã đăng lúc ghi (5 trạng thái × 2 đường); đăng sau lần ghi đầu (lần 2 bị chặn, bỏ id, ảnh đại diện cũng bị chặn); site trả `id` `42.0`, `False`, `None`, list, dict, `status` list/dict/`DRAFT`/`draft`+U+200B, thân rỗng/list/số/HTML: đều từ chối, không request ghi nào. `post_id` `42.5`, số phức, `"0x2a"`, bytes, tuple, set, `2**63+42`, lớp con của `int` có `__str__` giả đường `code-snippets`: từ chối trước khi gửi. Client khác không ghi được bài client này tạo. `create_draft` trả `status` `"draft "`, `auto-draft`, rỗng, list, số: không ghi nhận.
- **Đường dự phòng:** chỉ gửi `{"meta": {2 khóa}}`, không có từ khóa chính, báo "chép tay"; so lại chính xác (thừa dấu cách, hoa/thường, list, `None` đều thành `unavailable`); lỗi mạng/HTML/timeout không ném lỗi; dò Abilities lỗi 5xx thì dùng đường dự phòng, không gọi ability.
- **Câu lỗi:** 8 nhánh lỗi (kiểm nháp 500/403, ability 500/403/`success:false`, meta 500/403, chuyển hướng 302): không chứa lời máy chủ, `wp-config`, `<b>`, mật khẩu, `code-snippets`, tên khóa meta.
- **Danh sách đường:** 45 đường xấu thêm (gạch cuối, số 0 đầu, chữ số toàn khổ/Ả Rập, `;`, `\n`, `\x00`, `?`, `#`, revisions/autosaves, application-passwords, settings, plugins, DELETE/PUT/PATCH/OPTIONS/HEAD, phương thức chữ thường, đường rỗng, gạch chéo Unicode, `seo-data-get`, GET lên `run`, `%2F`, `..`, `Code-Snippets`, `PROMETAL`, `\`, `//host`, khoảng trắng, U+200B, U+202E): đều bị chặn. Chuyển hướng 300, 301, 302, 303, 304, 307, 308, 399 ở 4 bước (kiểm nháp, dò, ghi ability, ghi meta): không request thứ hai, không ghi.
- **Chặn chữ SEO:** `&#037;`, `&#x0025;`, `&#x25`, `&percnt;`, `&LT;`, `＆#37;`, `&＃37;`, `&#３７;`, `%`+U+200B+`%`, `%`+gạch nối mềm+`%`, `﹪﹪`, `%`+U+3164+`%`, `<`+U+3164/U+00AD+`script>`, `﹤script﹥`, `\x07`, `\x1b`, `\x9b`: đều chặn trước khi gửi, câu lỗi không chép chữ. `\x1c`–`\x1f`, U+2028 thành dấu cách (vô hại).
- **SL-T037-3:** header `"3, 3"` (proxy gộp header lặp), `+3`, `Infinity`, `３`: đọc tiếp tới trang thiếu, đủ bài. Header cực lớn: dừng ở `MAX_PAGES`, bật `truncated`. Trang xoay vòng 1, 2, 1, 2 không header: dừng, bật `truncated`. Trang 2 lỗi 404/500/HTML/không phải list: báo lỗi, không trả thiếu như đủ.
- **SL-T037-4/5 (Windows, mở file thật):** chương trình khác giữ file độc quyền, chỉ cho đọc, đọc+xóa, chỉ xóa, chỉ ghi, đọc+ghi (không cho xóa), khóa vùng byte khóa đọc của SQLite: **không lần nào xóa file**, cache cũ còn nguyên sau khi đóng. Khóa vùng byte: `get` báo "đang bận" sau ~1,7 giây (trước đây ~14 giây).
- **LC-T037-1:** 11 ký tự Cf (U+200B/C/D, U+2060, U+2066, U+202E, BOM, gạch nối mềm, U+E0001, U+061C, U+180E) bị bỏ khỏi chữ và làm link bị từ chối; link đã mã hóa `%3C`, `%E1%BB%AD`, `?p=42&preview=true` vẫn qua.

## Đối chiếu tiêu chí xong

- [x] Kết luận đạt / đạt có điều kiện / không đạt: **ĐẠT CÓ ĐIỀU KIỆN** (mục dưới)
- [x] Lỗi có mức, tái hiện, mong đợi, thực tế: 7 lỗi ở trên
- [x] Test đã thêm: 2 file, 283 test (247 qua, 36 `xfail` strict)
- [x] Kết quả lệnh thật: mục Bằng chứng
- [x] Đã push nhánh `team/T-042`

## Kết luận: ĐẠT CÓ ĐIỀU KIỆN

Yêu cầu chính của phiếu (chỉ bài app tạo, còn nháp; không `null`/`status`; danh sách đường cố định; câu lỗi cố định; mặc định tắt) đạt. Không tìm được đường nào để `set_seo_meta` ghi vào bài đã đăng hay để code gọi đường ngoài danh sách. Điều kiện:

1. **SL-T042-1** (Trung bình) sửa trước Giai đoạn 5, cùng hạn SL-T037-3. Khuyên sửa luôn trong T-042 (vài dòng).
2. **SL-T042-4, SL-T042-5, SL-T042-6** sửa trước phiếu giao diện nối `set_seo_meta` / `set_featured_image` vào app.
3. SL-T042-2, -3, -7 (Thấp): sửa khi tiện, hoặc theo dõi ở phiếu dọn lỗi.

## Rủi ro và điểm cần chú ý

- **Khe thời gian kiểm rồi ghi:** `set_seo_meta` gọi `_own_draft`, **rồi mới dò Abilities** (một request mạng nữa), rồi mới ghi; người dùng bấm Đăng trong khe đó thì vẫn ghi (đã thử). Đổi thứ tự (dò trước, kiểm nháp ngay trước khi ghi) làm khe ngắn hơn. Thợ Máy đã nêu rủi ro này.
- Đường dự phòng không kiểm `id`/`status` trong câu trả lời của `POST /wp/v2/posts/<id>`: site trả `{"id": 43, "status": "publish", meta đúng}` vẫn báo "đã ghi". Nên kiểm thêm để phát hiện bất thường.
- Ký tự thay thế lẻ (U+D800) lọt `_seo_text`; máy chủ PHP sẽ từ chối JSON (400), app báo lỗi, không hại.
- File cache bị giữ độc quyền (không phải "bận"): `get` mất ~2,9 giây (SQLite tự thử mở lại ~1,4 giây × 2 lần), không xóa file. Chấp nhận được.
- `upload_media` (có từ Giai đoạn 1) cũng dùng `int(media["id"])` từ câu trả lời của site rồi `POST /wp/v2/media/<id>`: cùng loại SL-T042-4 với ảnh; ngoài phạm vi T-042.

## Đề xuất

- **Thợ Máy:** sửa SL-T042-1 (so trang trùng cả khi có header), SL-T042-4 (kiểm kiểu `id` khi tạo nháp, và cả `upload_media`), SL-T042-5 (`set_featured_image` gọi `_own_draft` và kiểm `type(post_id) is int`), SL-T042-6 (chỉ coi là đã ghi khi câu trả lời xác nhận rõ), SL-T042-2/3/7. Bỏ dấu `xfail` tương ứng trong 2 file test của Soi Lỗi.
- **Lá Chắn:** soát kỹ SL-T042-3 (chốt chặn danh sách đường phụ thuộc `base_url`) và thứ tự kiểm-rồi-ghi.
- **Phiếu thử thật:** ghi lại nguyên khuôn trả lời của `seo-data-update/run` (thành công và lỗi) để siết SL-T042-6.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-19) · kiểm lại sau khi Thợ Máy sửa (nhánh `0dc2464`)

### Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** (điều kiện nhẹ, không chặn gộp)

Cả 7 lỗi lượt 1 và LC-T044-1 đã được sửa đúng. Hai việc "nên làm" cũng đã làm. Tôi thử phá từng chỗ sửa và tìm thêm **4 lỗi, đều Thấp**:
- Không lỗi nào mở đường ghi vào bài đã đăng, hay để code gọi đường REST ngoài danh sách.
- Hai lỗi chỉ xảy ra khi chủ máy tự khai sai `WORDPRESS_URL` trong `.env`.

Điều kiện:
- Sửa SL-T042-8 và SL-T042-11 trước phiếu giao diện nối `set_seo_meta` / `set_featured_image` vào app.
- SL-T042-9, -10 sửa khi tiện.

### Tóm tắt (cho chủ dự án)

- Đã sửa xong:
  - Danh sách bài đã đăng không còn bị thiếu khi website có bộ đệm.
  - Đặt ảnh đại diện cũng hỏi lại website "bài còn là nháp không" trước khi ghi.
  - Phần mềm chỉ báo "Đã ghi SEO" khi SiteSEO xác nhận.
  - Website trả dữ liệu lạ cũng không làm vỡ trang (tôi thử 374 trường hợp dữ liệu sai).
- Còn 4 lỗi nhỏ:
  - Câu trả lời mâu thuẫn của website vẫn được báo là thành công.
  - Kiểm `WORDPRESS_URL` chưa thật chặt.

### Soát thay đổi của Thợ Máy trong test

- `tests/test_soi_loi_t042.py`, `tests/test_soi_loi_t042_paging_cache.py`: Thợ Máy **chỉ bỏ đúng 8 dấu `xfail`**, không sửa thân test nào (`git diff 6eac892 0dc2464`). 8 dấu đó ứng với 36 trường hợp: SL-T042-1: 3, -2: 4, -3: 3, -4: 5, -5: 1, -6: 6, -7: 14.
- 3 test cũ về ảnh đại diện (`test_set_featured_image`, `test_featured_image_allowed_only_for_own_draft`, `test_every_write_request_to_posts_never_publishes`) **không bị làm yếu**:
  - Mỗi test chỉ thêm đúng 1 dòng: site giả trả lời `GET` bài nháp với `status: draft`.
  - Không assert nào bị xóa hay nới.
  - Các test vẫn kiểm đủ điều cũ: ảnh chỉ đặt cho bài app tạo, không có `publish`/`future` trong lệnh ghi.
  - `test_public_methods_only_use_allowed_routes` cũng thêm 1 dòng như vậy.
- Test của chính Thợ Máy có 2 chỗ đổi, đều chấp nhận được:
  - `test_post_no_longer_draft_on_site_is_refused`: điều kiện "không gọi ability" đổi thành "không gọi lệnh ghi `run`". Hợp lý vì giờ app dò Abilities trước. Test vẫn kiểm không có lệnh ghi.
  - `test_meta_route_not_saved_is_not_reported_as_written`: bỏ trường hợp `[]`. Trường hợp này giờ ra `error` và đã được kiểm ở `test_meta_route_write_answer_must_be_same_draft` (file lượt 2).

### Lỗi lượt 2

#### SL-T042-8 · Thấp · Câu trả lời ability tự mâu thuẫn vẫn báo "đã ghi"

- **Tái hiện:** `run` trả `{"updated": false, "success": true}` hoặc `{"updated": true, "success": false}`.
- **Mong đợi:** có khóa nói rõ `false` thì không coi là đã ghi.
- **Thực tế:** `written=True`. Lý do: `_ability_confirms` dùng `updated is True or success is True`.
- **Test:** `test_ability_explicit_false_wins` (2 trường hợp).

#### SL-T042-9 · Thấp · Tab/xuống dòng **giữa** `WORDPRESS_URL` vẫn qua

- **Tái hiện:** `WordPressClient("https://example.com/blo\tg", …)` được nhận. Request thật đi tới `https://example.com/blo%09g/wp-json/wp/v2/posts`. Cũng nhận `https://exa\tmple.com`, `https://exam\nple.com`.
- **Mong đợi:** từ chối, như báo cáo Thợ Máy mô tả ("từ chối khoảng trắng").
- **Thực tế:** `urlsplit` âm thầm bỏ `\t`, `\n`, `\r`, nên `_is_plain_site_url` xét một chuỗi khác với chuỗi được dùng để gọi.
- **Mức Thấp** vì hiện vô hại: tên máy lạ thì requests báo lỗi, thư mục lạ thì website trả 404.
- **Test:** `test_wordpress_url_with_inner_tab_or_newline_is_refused` (3 trường hợp).
- **Gợi ý sửa:** từ chối khi `any(ch.isspace() or ord(ch) < 32 for ch in base_url)`.

#### SL-T042-10 · Thấp · `WORDPRESS_URL` trỏ thẳng vào một file `.php`

- **Tái hiện:** `https://example.com/wp-content/plugins/x/run.php` được nhận (cả `/xmlrpc.php`, `/wp-login.php`). Request thật là `POST …/run.php/wp-json/wp/v2/posts`: nó chạy file PHP đó, không phải REST API của WordPress.
- **Mong đợi:** thư mục con chỉ gồm tên thư mục, không có đoạn `*.php`. Có thể chừa `index.php` nếu muốn hỗ trợ đường dẫn tĩnh kiểu PATH_INFO.
- Chỉ xảy ra qua `.env`.
- **Test:** `test_wordpress_url_pointing_at_php_file_is_refused` (3 trường hợp).

#### SL-T042-11 · Thấp · `set_featured_image` không soát câu trả lời của lệnh ghi

- **Tái hiện:** `POST /wp/v2/posts/42` trả `{"id": 43, …}` hoặc `{"id": 42, "status": "publish", …}`.
- **Mong đợi:** báo bất thường (`WordPressError`). Đường meta dự phòng đã làm việc này ở lượt 2, bằng `_is_own_draft_answer`.
- **Thực tế:** hàm trả `Post` của bài 43, hay của bài đã đăng, như thành công.
- **Test:** `test_featured_image_answer_for_other_or_published_post_is_reported` (2 trường hợp).

### Đã thử, không thấy lỗi (lượt 2)

**`_get_pages_checked`**
- Trang trùng: dừng và bật `truncated`, dù có header (`2`, `50`, `999`) hay không. Chỉ tốn 2 request.
- Lỗi `rest_post_invalid_page_number`: header nói còn trang thì báo lỗi; không có header thì coi là hết trang.
- Ghi nhận, không tính lỗi: máy chủ trả xoay vòng trang 1, 2, 1 kèm header `3` thì thiếu trang 3 mà không báo. Tình huống này quá giả tạo.

**`_positive_id`**
- Từ chối `True`, `False`, `0`, số âm, lớp con của `int`, chuỗi, số thực, `None`, list, dict.
- Không có giới hạn trên, nhưng vô hại:
  - `2**70` qua được `_positive_id`, nhưng đường có hơn 19 chữ số bị danh sách đường chặn.
  - `set_featured_image(42, 2**70)` vẫn gửi `GET` kiểm nháp rồi `POST`; WordPress sẽ từ chối. Ghi nhận.

**`set_featured_image`**
- Bài đổi sang `publish`, `future`, `private`, `pending`, `trash` hoặc `None` giữa lúc tạo và lúc đặt ảnh: từ chối, không `POST`, bỏ id.
- `media_id` hay `post_id` lạ: từ chối trước mọi request.
- Request ngay trước lệnh ghi là `GET` kiểm nháp. Thân lệnh ghi chỉ có `{"featured_media": 7}`.

**`_ability_confirms`**
- Khuôn SiteSEO `{"updated": true, "post": {...}}`, kể cả có trường thừa: tính là đã ghi.
- Tính là chưa ghi: trường không khớp (thừa dấu cách, sai tên trường), `post` không phải dict, có `code` (kể cả `null`), `"true"`, `1`, `null`, `{}`.
- Từ khóa được so đúng tên trường `focus_keyphrase`.

**`_LEGACY_ENTITY`**
- Đúng 106 tên, và cả 106 đều bị chặn.
- Vẫn qua: `R&D`, `AT&T`, `Q&A`, `P&G`, `H&M`, `M&E`, `Sale&off`, `Cửa&cổng`, `Sắt&Inox`, `Mua&bán`, `&Lt`, `&Notice`.
- Biến thể bị chặn: `&` + U+200B + `lt`, `＆lt`, `&ETH`, `&ltd`.
- **Đánh giá việc chặn `&notice`:** về mặt kỹ thuật không phải chặn oan. Trong nội dung HTML (kể cả `<title>`), trình duyệt giải mã `&not` + chữ thành `¬ice`, nên nếu SiteSEO in nguyên văn thì khách thấy chữ sai. Chữ kiểu này hiếm trong tiêu đề tiếng Việt, và câu báo đã chỉ cách sửa. **Chấp nhận.**

**`_is_plain_site_url`**
- Từ chối 26 địa chỉ xấu: `wp-admin`/`wp-json` ở mọi kiểu hoa thường, `;`, `.`/`..`, `.well-known`, `//`, tên/mật khẩu, `\@`, `%2F@`, tên miền Unicode chưa đổi sang punycode, `[::1]`, dấu chấm cuối, cổng rỗng hoặc là chữ, khoảng trắng, `?`, `#`, `Code-Snippets`, `ProMetal`, `http`, `ftp`.
- Câu lỗi không chép lại địa chỉ.
- Vẫn nhận 8 địa chỉ bình thường: thư mục con, `~user`, có cổng, IP, punycode.

**`_has_invisible` / `_drop_invisible`**
- Test lượt 1 qua hết (7 ký tự ngoài Cf, 11 ký tự Cf).

**LC-T044-1**
- Thử 17 kiểu dữ liệu sai: `None`, bool, số âm, `nan`, `10**30`, chuỗi, HTML, list, dict…
- Ở 22 vị trí:
  - `check_connection`: 10 vị trí, gồm câu trả lời dò Abilities.
  - Chuyên mục: 6 vị trí.
  - Câu trả lời tạo nháp / ảnh đại diện / tải ảnh: 6 vị trí.
- Kết quả 374 test: chỉ có `WordPressError` câu cố định, không lọt lỗi Python nào. Quyền chỉ được tính khi đúng `True`.

**Nhánh `{"success": true}`: khuyên giữ đến phiếu thử thật**
- Rủi ro báo nhầm thấp: muốn được nhận phải là đúng `true` kiểu bool, không có `code`, và nếu có `post` thì phải khớp từng chữ.
- Phiếu thử thật ghi lại câu trả lời thật của `seo-data-update/run`. Nếu đúng khuôn `updated` thì bỏ nhánh `success`, và đổi site giả trong test (của Thợ Máy và Soi Lỗi) sang `{"updated": true}`.
- Sửa SL-T042-8 trước việc này.

### Rủi ro còn lại (lượt 2)

- App so giá trị `post` trong câu trả lời của SiteSEO với chữ đã gửi.
  - Nếu SiteSEO làm sạch chữ khi lưu (ví dụ `sanitize_text_field` đổi `<` lẻ thành `&lt;`, bỏ `%ab`), app sẽ báo "không thành công" dù đã ghi.
  - Lỗi này theo chiều an toàn: người dùng sẽ chép tay.
  - Phiếu thử thật nên thử một tiêu đề có `< 5 triệu` và `10%`.
- Khe "kiểm rồi ghi" vẫn còn (2 request liền nhau); Thợ Máy đã ghi rõ.

### Test lượt 2

`tests/test_soi_loi_t042_round2.py` (mới): 499 test, 489 qua, 10 `xfail` strict cho SL-T042-8…11.

### Bằng chứng (lượt 2)

Windows 11, Git Bash, worktree `wt-T-042`.

```
$ uv run ruff check .
All checks passed!

$ uv run pytest            (HEAD 0dc2464, trước khi thêm test lượt 2)
6465 passed, 11 skipped, 30 xfailed, 1 warning in 612.40s (0:10:12)

$ uv run pytest            (sau khi thêm tests/test_soi_loi_t042_round2.py)
6954 passed, 11 skipped, 40 xfailed, 1 warning in 993.13s (0:16:33)
(0 hỏng. +489 qua, +10 xfail đều của Soi Lỗi lượt 2; 30 xfail cũ và 1 warning pydantic có từ trước)

$ uv run pytest tests/test_soi_loi_t042_round2.py -q
489 passed, 10 xfailed in 16.77s
```

### Việc cần Thợ Máy sửa (lượt 3, nhỏ)

- SL-T042-8: `_ability_confirms` trả `False` khi `updated is False` hoặc `success is False`.
- SL-T042-11: `set_featured_image` soát câu trả lời bằng `_is_own_draft_answer`; sai thì ném `WordPressError` câu cố định.
- SL-T042-9: từ chối `WORDPRESS_URL` có khoảng trắng hoặc ký tự điều khiển ở bất kỳ đâu.
- SL-T042-10: đoạn thư mục không được là file `.php` (cân nhắc chừa `index.php`).
- Sửa xong thì bỏ các dấu `xfail` tương ứng trong `tests/test_soi_loi_t042_round2.py`.

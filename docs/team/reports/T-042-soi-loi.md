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
| `tests/test_soi_loi_t042.py` | Mới: `set_seo_meta`/`_own_draft` (trạng thái đổi giữa các bước, câu trả lời lạ, `post_id` lạ, lớp con của `int`), đường dự phòng meta, câu lỗi cố định (8 nhánh lỗi, không lộ lời máy chủ/mật khẩu), 47 đường xấu, chuyển hướng 300–399 ở cả 4 bước, chặn chữ SEO (18 chuỗi × 3 trường), `xfail` SL-T042-2…6 |
| `tests/test_soi_loi_t042_paging_cache.py` | Mới: phân trang (header lạ, header lặp bị gộp, máy chủ trả trang xoay vòng, trang 2 hỏng), `_total_pages`, ký tự vô hình loại Cf và ngoài Cf, cache bị chương trình khác giữ trên Windows (7 chế độ chia sẻ + khóa vùng byte, mở thật bằng `CreateFileW`/`LockFileEx`), `xfail` SL-T042-1, SL-T042-7 |
| `docs/team/reports/T-042-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `conftest.py`, `timing.py`, test của agent khác.

## Bằng chứng

Windows 11, Git Bash, worktree `wt-T-042`.

```
$ uv run ruff check .
All checks passed!

$ uv run pytest            (trước khi thêm test, HEAD 6a02005)
BASELINE_RESULT

$ uv run pytest            (sau khi thêm test)
FINAL_RESULT

$ uv run pytest tests/test_soi_loi_t042.py tests/test_soi_loi_t042_paging_cache.py -q
247 passed, 36 xfailed
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
- **Danh sách đường:** 47 đường xấu thêm (gạch cuối, số 0 đầu, chữ số toàn khổ/Ả Rập, `;`, `\n`, `\x00`, `?`, `#`, revisions/autosaves, application-passwords, settings, plugins, DELETE/PUT/PATCH/OPTIONS/HEAD, phương thức chữ thường, đường rỗng, gạch chéo Unicode, `seo-data-get`, GET lên `run`, `%2F`, `..`, `Code-Snippets`, `PROMETAL`, `\`, `//host`, khoảng trắng, U+200B, U+202E): đều bị chặn. Chuyển hướng 300, 301, 302, 303, 304, 307, 308, 399 ở 4 bước (kiểm nháp, dò, ghi ability, ghi meta): không request thứ hai, không ghi.
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

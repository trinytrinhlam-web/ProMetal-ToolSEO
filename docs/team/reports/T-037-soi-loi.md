# Báo cáo T-037 · Soi Lỗi · Danh sách bài đã đăng + cache SQLite

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-037](../tickets/T-037-danh-sach-bai-da-dang-cache.md) |
| Ngày nộp | 2026-10-16 (lượt 1) · 2026-10-17 (lượt 2) |
| Kết quả | Lượt 1: **ĐẠT CÓ ĐIỀU KIỆN** · Lượt 2: **ĐẠT** (3 lỗi Thấp mới, không chặn) |

## Tóm tắt (cho chủ dự án)

Phần đọc danh sách bài đã đăng làm đúng: chỉ lấy bài đã đăng, chỉ đọc (không sửa gì trên site), bỏ mọi đường dẫn lạ hoặc giả mạo tên miền. Cache chịu được file hỏng, bị xóa, bị sửa tay. Tìm được **1 lỗi mức Trung bình**: khi file cache đang bị chương trình khác giữ lâu (hơn 5 giây), phần mềm tưởng file hỏng và xóa nó. Chỉ ảnh hưởng file tạm (tải lại được), không đụng tới website. Không chặn việc gộp, nhưng nên sửa trước khi T-036/T-039 dùng.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t037.py` | Mới: 87 test (86 qua, 1 `xfail` SL-T037-1) |
| `docs/team/reports/T-037-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest            (toàn repo, Linux)
4848 passed, 4 skipped, 17 xfailed, 1 warning in 251.13s

$ uv run pytest tests/test_soi_loi_t037.py
86 passed, 1 xfailed in 2.13s

$ uv run ruff check .
All checks passed!
```

(Trước Soi Lỗi: 4.762 qua, 16 xfail. `xfail` thêm 1 là SL-T037-1.)

## Đối chiếu việc được giao

1. **Tiêu chí phiếu: đạt.**
   - Chỉ giữ `publish`: thử `future`, `draft`, `private`, `pending`, `trash`, `Publish` (chữ hoa) ở cả bài và trang (`test_only_publish_survives_each_status`).
   - Chỉ `GET`, `status=publish` gửi lên cả hai đường, không xin `context=edit`, không có body.
   - Tiêu đề có thẻ, thực thể (`&amp;`, `&nbsp;`, `&#8211;`), `<img onerror>`, xuống dòng, mã thoát `&#x1b;`: ra chữ thuần một dòng, không còn ký tự điều khiển.
   - Meta thiếu / rỗng / sai kiểu (`[]`, chuỗi, `None`): rỗng, không lỗi.
   - Nhiều trang kết quả cho cả bài và trang: đọc đủ.
2. **`is_site_link`: không phá được.** 38 dạng xấu đều bị từ chối: `suachuacuasat.com.evil.tld`, `@` trước/sau tên máy, có tên/mật khẩu, punycode lạ, chữ `ⅽ` La Mã (trình duyệt chuẩn hóa thành `c`; ở đây bị từ chối, an toàn), dấu chấm cuối `suachuacuasat.com.` (từ chối, an toàn hơn nhận), cổng 8443/80/99999/`abc`, `\` thay `/`, `javascript:`, `//evil.tld`, `//suachuacuasat.com`, đường tương đối, `http`, `ftp`, `https:` thiếu `//`, tên miền con, `%2e`, ký tự rộng 0, dấu cách, xuống dòng, NUL, IP, kiểu không phải chuỗi, quá 2.000 ký tự. Nhận đúng link thật: chữ hoa, `HTTPS://`, `:443`, `?p=123`, đường có dấu tiếng Việt mã hóa `%`.
3. **Cache:**
   | Tình huống | Kết quả |
   |---|---|
   | File rác, sai cột, một dòng sai (link giả, `id` = 1.5, `type` lạ) | Đạt: bỏ cache, tải lại |
   | Symlink | Đạt (test của Thợ Máy): xóa liên kết, file đích nguyên vẹn |
   | Cache của site khác | Đạt: không trả, ghi đè |
   | Cũ hơn 6 giờ | Đạt: 5 giờ 59 dùng cache, 6 giờ 1 giây tải lại |
   | Không ghi được (giả `sqlite3.connect` lỗi, vì chạy bằng root nên `chmod` vô hiệu) | Đạt: vẫn trả danh sách, `cache_error` tiếng Việt, không lộ câu lỗi gốc |
   | 2 lần làm mới cùng lúc (2 luồng × 15 lần, 300 và 200 mục) | Đạt: không lỗi, không reset, cache cuối trọn vẹn một bộ |
   | **File bị giữ khóa lâu hơn timeout** | **Lỗi SL-T037-1** (dưới) |
   | Xóa file khi đang mở (Windows) | Đạt: kiểm bằng cách theo dõi mọi kết nối; lúc xóa (file rác, dòng sai, `clear()`) không còn kết nối nào mở |
   | File `-journal` rác cạnh cache | Đạt: không chết |
   | Múi giờ `fetched_at` | Đạt: lưu `+07:00`; giá trị ghi theo giờ UTC vẫn so đúng |
4. **`MAX_PAGES`:** xem SL-T037-2.
5. **Test "không có hàm publish" bị sửa:** vẫn chặn mọi tên khác chứa `publish` (`publish_post`, `_publish`, `republish`, `schedule_publish`…). Hai chỗ hở **có từ trước**, không do T-037: so chữ phân biệt hoa thường (`Publish_now` lọt), và chỉ xét hàm của đối tượng, không xét hàm cấp module. Đã thêm 3 test mạnh hơn (không phân biệt hoa thường; tên cấp module chỉ được là `PublishedItem`, `PUBLISHED_TYPES`, `_PUBLISHED_FIELDS`, `_published_from`) và **1 test theo hành vi**: đọc cây cú pháp `client.py`, mọi chỗ gán khóa `status` khác `"draft"` chỉ được nằm trong `list_published` (đúng 1 chỗ: `"publish"` trong tham số GET). Test này bắt cả hàm đăng bài đặt tên vô hại như `make_live`.
   **Đổi tên hàm?** Không cần. Tên `list_published` do phiếu chỉ định; test hành vi ở trên chặn chắc hơn việc giữ nguyên test tên cũ. Nếu Lá Chắn muốn giữ test cũ nguyên văn thì `list_live_items` dùng được, nhưng `PublishedItem` vẫn có chữ đó ở cấp module.
6. **Tốc độ:** `list_published` 5.000 mục qua site giả và lưu+đọc cache 5.000 mục đều tuyến tính (`assert_scales_linearly`). Cả file test chạy 2 giây.

## Lỗi tìm thấy

### SL-T037-1 · Trung bình · File cache đang bận bị coi là hỏng và bị xóa

- **Tái hiện:** `tests/test_soi_loi_t037.py::test_locked_file_is_busy_not_corrupt` (`xfail strict`). Một kết nối khác giữ `BEGIN EXCLUSIVE` trên file; gọi `store.load(...)` khi timeout đã hết.
- **Mong đợi:** file đang bận thì để yên, báo "đang bận, thử lại" (câu này đã có trong `_db_message`).
- **Thực tế:** `_prepare` → `_is_healthy` chạy `PRAGMA quick_check`, gặp `database is locked` (là `sqlite3.DatabaseError`) → trả `False` → `_reset()` xóa file và `-journal` của giao dịch đang chạy, rồi tạo file mới rỗng. Trên Linux/Mac kết nối kia ghi tiếp vào file đã mất; trên Windows xóa thất bại, ra `SiteIndexError`. `reset_count` tăng 1.
- **Khi nào xảy ra:** timeout 5 giây nên 2 tab bình thường không gặp (đã thử). Gặp khi chương trình khác giữ file lâu: người dùng mở file bằng DB Browser, phần mềm diệt virus / sao lưu quét file, ổ mạng chậm.
- **Hậu quả:** chỉ mất file tạm, lần sau tải lại; không đụng website.
- **Gợi ý sửa (Thợ Máy):** trong `_is_healthy`, `sqlite3.OperationalError` có chữ `locked`/`busy` thì ném lại (để `_connect` đổi thành `SiteIndexError` "đang bận"), chỉ trả `False` với lỗi thật sự hỏng (`file is not a database`, `malformed`).

### SL-T037-2 · Thấp (đề xuất) · Site quá `MAX_PAGES` bị cắt lặng lẽ

- **Tái hiện:** `test_more_than_max_pages_is_cut_silently` (ghi nhận hành vi, đang qua). Site báo 60 trang, client đọc 50 rồi dừng, không có dấu hiệu nào.
- **Đánh giá:** site hiện 29 URL, giới hạn 5.000 bài + 5.000 trang, nên **chưa cần sửa ngay**. Nhưng nên báo khi làm Giai đoạn 5: kiểm link hỏng sẽ báo **sai** "link hỏng" cho bài bị cắt; kiểm trùng meta (T-036) bỏ sót. Gợi ý: `list_published` (hoặc `SiteIndex`) có cờ `truncated` khi `X-WP-TotalPages > MAX_PAGES`; giao diện hiện một dòng "Danh sách chưa đủ, chỉ đọc N mục đầu"; Giai đoạn 5 không báo link hỏng khi cờ bật.
- Liên quan: máy chủ bỏ qua `per_page` trả > 10.000 mục thì `save` từ chối, mỗi lần `get` lại tải lại từ site (`test_server_ignoring_per_page_gives_cache_error_not_crash`). Không chết, chỉ chậm; không cần sửa.

## Rủi ro và điểm cần chú ý (không phải lỗi, cho phiếu sau)

- `is_stale(now=...)` / `get(now=...)` truyền giờ không có múi giờ thì `TypeError`. Chỉ code gọi sai mới gặp; T-036/T-039 nhớ dùng giờ có múi giờ.
- Chữ thuần chưa escape (Thợ Máy đã ghi): đã thử `<img onerror>` bị bỏ thẻ, nhưng `&lt;script&gt;` giải mã thành `<script>`. Nơi hiện lên giao diện phải `html.escape`. Ký tự đảo chiều (U+202E) trong đường dẫn vẫn được nhận: khi hiện link cho người dùng nên hiện dạng đã mã hóa.
- `by_link()` so link nguyên văn. Giai đoạn 5 nên chuẩn hóa (chữ hoa tên máy, `:443`, dấu `/` cuối) trước khi so, nếu không link đúng vẫn bị coi là không có.
- Kiểm thử "thư mục chỉ đọc" thật bằng `chmod` không làm được trên cloud (chạy bằng root); đã giả bằng lỗi `sqlite3.connect`. Nên chạy lại bộ test trên Windows.

## Đề xuất

- Thợ Máy sửa SL-T037-1 (nhỏ, 1 hàm) rồi bỏ dấu `xfail`.
- Lá Chắn: xem mục 5 (test tên `publish`) và đề xuất danh sách đường gọi cố định của Thợ Máy cho T-042.
- SL-T037-2: ghi vào phiếu Giai đoạn 5 (kiểm link hỏng).

## Lượt 2 (2026-10-16 → 2026-10-17) · **ĐẠT**

Kiểm lại commit `1fd1415` của Thợ Máy (diff `git diff ac5ed8a 1fd1415 -- seo_app`). Phiên Soi Lỗi đầu (Chỉ Huy B) viết phần A rồi dừng ở `09069b4`; phiên sau (Chỉ Huy A) làm phần B, chạy toàn bộ trên Windows và kết luận.

### Tóm tắt (cho chủ dự án)

Hai lỗi lượt 1 đã sửa đúng, kể cả trên Windows: file tạm đang bị chương trình khác mở thì để yên, không xóa; site quá dài thì có cờ báo "danh sách chưa đủ". Tìm thêm **3 lỗi mức Thấp**, không chặn gộp: cờ "chưa đủ" không bật nếu máy chủ giấu số trang; một kiểu mở file hiếm trên Windows vẫn làm file bị xóa; khi file bị khóa, app chờ tới khoảng 14 giây. Cả ba chỉ đụng tới file tạm trên máy, không đụng website.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t037.py` | Phần A (`09069b4`): 26 test `test_r2_*`, sửa `…cut_silently` thành `…cut_but_flagged`. Phần B (`17209ab`, `0f82302`): thêm 26 test (21 qua, 5 `xfail strict`: SL-T037-3 × 4, SL-T037-4 × 1) |
| `docs/team/reports/T-037-soi-loi.md` | Mục này |

Không sửa code ứng dụng.

### Bằng chứng (Windows 11, Git Bash)

```
$ uv run pytest tests/test_soi_loi_t037.py tests/test_site_index.py -q   (trước phần B)
167 passed, 1 skipped in 21.86s

$ uv run pytest tests/test_soi_loi_t037.py -q   (sau phần B)
134 passed, 5 xfailed in 16.73s

$ uv run pytest
4904 passed, 11 skipped, 21 xfailed, 1 warning in 468.38s (0:07:48)
(0 hỏng, 0 lỗi; 21 xfail = 16 có từ trước + 5 của SL-T037-3/4)

$ uv run ruff check .
All checks passed!
```

`1 skipped` của `tests/test_site_index.py` là test symlink (Windows không cho tạo symlink khi chưa bật Developer Mode), có từ lượt 1.

### Đối chiếu việc được giao

**A. Đã kiểm ở phiên trước (đều đạt, chạy lại trên Windows vẫn qua):**
- **SL-T037-1:** file bị khóa (kết nối khác trong cùng tiến trình, có `-journal` giao dịch dở) không bị xóa, nội dung và `-journal` giữ nguyên, `reset_count` = 0; `load` trả `None`; `refresh`/`get` vẫn trả danh sách kèm `cache_error` "đang bận". Nhả khóa xong đọc và ghi lại bình thường. File hỏng thật vẫn bị dọn.
- **SL-T037-2:** cờ `truncated` bật khi bài **hoặc** trang vượt `MAX_PAGES`, không bật khi đúng bằng. Tối đa 2 × `MAX_PAGES` request, chỉ `GET`. Cờ qua cache đúng (`True`/`False`), giữ cả khi không ghi được cache. Giá trị lạ hoặc thiếu = cache hỏng. Cache `SCHEMA_VERSION` 1 bị bỏ, tạo lại thành 2.
- **Danh sách cho phép:** `PublishedList` là `list` có thêm đúng một thuộc tính dữ liệu `truncated`, không có hàm mới. Test cấp module vẫn chặn `publish_post`, `PublishNow`, `_publish_draft`, `PublishedWriter`.

**B. Kiểm thêm ở phiên này:**

| Tình huống | Kết quả |
|---|---|
| Khóa bởi **tiến trình khác thật** (`subprocess` chạy `sqlite3`, `BEGIN EXCLUSIVE` + `DELETE`, có `-journal`) | Đạt: file và `-journal` giữ nguyên từng byte; `get` trả danh sách mới kèm "đang bận"; nhả khóa thì đọc lại bài cũ; `reset_count` = 0 |
| Khóa ở **luồng khác**, ngắn hơn timeout (0,3 giây) | Đạt: chờ rồi đọc được, không báo bận, không xóa |
| Khóa ở luồng khác, lâu hơn timeout | Đạt: `load` = `None`, `is_stale` = `True`, `refresh` báo bận, `save` ném `SiteIndexError` "bận" |
| Khóa bị chiếm **ngay sau** bước kiểm file (khe giữa `_prepare` và lúc đọc) | Đạt: lỗi bận đổi thành `SiteIndexError`, không rơi vào nhánh "hỏng", không xóa |
| File **chỉ đọc thật** (Windows: thuộc tính Read-only) | Đạt: đọc được cache; `refresh` trả danh sách mới kèm `cache_error`; file không bị xóa |
| Chỉ đọc + cache cũ (schema 1) | Đạt: không chết; Windows không xóa được nên báo không ghi được, Mac/Linux tạo lại sạch |
| Windows: chương trình khác mở file, chia sẻ "không cho gì" / "chỉ đọc" / "đọc-ghi-xóa" | Đạt: không xóa ("không cho gì" → báo không mở được; "chỉ đọc" → SQLite tự mở chế độ chỉ đọc). Đo tay bằng `CreateFileW` |
| Windows: chương trình khác mở file, chia sẻ **chỉ cho xóa** | **Lỗi SL-T037-4** |
| Trạng thái chỉ nhận đúng `"publish"`: thử `" publish"`, `"publish "`, `"PUBLISH"`, `"publish\x00"`, `"publіsh"` (chữ `і` Kirin), `["publish"]`, `None`, `1`, `True`, `{"raw": "publish"}`, thiếu khóa | Đạt: tất cả bị bỏ, ở cả bài và trang |
| Phân trang mới (`_get_pages_checked`), 3 trang bài + 2 trang trang | Đạt: đúng 5 request, mọi request `GET`, không body, `status=publish`, đúng `_fields`, không `context=edit`, chỉ `/wp/v2/posts` và `/wp/v2/pages`; mục `future`/`draft`/sai tên miền/`http://` ở trang 2 bị bỏ |
| Trang 2 lỗi 500 / 401 / không phải danh sách, khi cache đã cũ | Đạt: `get` ném `WordPressError`, **không** ghi danh sách dở, cache cũ nguyên vẹn |
| Máy chủ không gửi / gửi sai `X-WP-TotalPages` | **Lỗi SL-T037-3** |
| Thời gian chờ khi file bị khóa | **Lỗi SL-T037-5** |

### Lỗi tìm thấy (lượt 2)

#### SL-T037-3 · Thấp · Thiếu header số trang thì danh sách bị cắt mà cờ `truncated` vẫn `False`

- **Tái hiện:** `test_r2_missing_total_pages_header_is_not_silently_complete` (`xfail strict`, 4 trường hợp). Site có 300 bài (3 trang đầy, mỗi trang 100); máy chủ không gửi `X-WP-TotalPages`, hoặc gửi `""`, `"abc"`, `"60.0"`.
- **Mong đợi:** đọc tiếp tới trang rỗng (trong giới hạn `MAX_PAGES`), hoặc bật `truncated`. Không được vừa thiếu mục vừa báo "đủ".
- **Thực tế:** `_get_pages_checked` coi header thiếu/sai là 1 trang → đọc 100 mục rồi dừng, `truncated = False`. Đo tay thêm `"-5"`, `"0"`, `"1e2"`: cũng vậy.
- **Khi nào xảy ra:** plugin bảo mật hoặc proxy/CDN bỏ các header `X-WP-*`. Site hiện 29 URL (< 100) nên **chưa** ảnh hưởng.
- **Hậu quả:** Giai đoạn 5 tin cờ `truncated` sẽ báo nhầm "link hỏng"; T-036/T-039 bỏ sót bài.
- **Gợi ý sửa:** header thiếu/không đọc được mà trang trả đủ `PER_PAGE` mục thì đọc tiếp trang sau (dừng ở trang rỗng; tới `MAX_PAGES` mà vẫn đầy thì bật `truncated`); tối thiểu là bật `truncated`. `_get_all_pages` (chuyên mục/thẻ) có cùng hành vi từ trước, ngoài phạm vi phiếu.

#### SL-T037-4 · Thấp · Windows: file đang được chương trình khác mở (chế độ "chỉ cho xóa") vẫn bị xóa

- **Tái hiện:** `test_r2_file_opened_by_other_program_share_delete_is_not_deleted` (chỉ chạy trên Windows, `xfail strict`). Mở file cache bằng `CreateFileW(GENERIC_READ, FILE_SHARE_DELETE)` rồi gọi `load` và `refresh`.
- **Mong đợi:** file đang được mở thì để yên (như SL-T037-1).
- **Thực tế:** SQLite không mở được (`unable to open database file`, không có chữ `locked`/`busy`) → `_is_healthy` trả `False` → `_reset` xóa được file (Windows cho xóa vì có `FILE_SHARE_DELETE`) → `reset_count` = 1, tạo file mới.
- **Khi nào xảy ra:** hiếm; phần lớn phần mềm diệt virus/sao lưu mở với "đọc-ghi-xóa" (đã thử, đạt).
- **Hậu quả:** chỉ mất file tạm, tải lại được.
- **Gợi ý sửa:** đảo cách kiểm trong `_is_healthy`: chỉ coi là hỏng khi chắc chắn hỏng (`sqlite_errorname` là `SQLITE_NOTADB`/`SQLITE_CORRUPT`, `quick_check` khác `ok`, hoặc sai cột); lỗi khác (`SQLITE_CANTOPEN`, `SQLITE_IOERR`, `SQLITE_BUSY`, `SQLITE_LOCKED`) thì báo `SiteIndexError`, không xóa. Không gấp.

#### SL-T037-5 · Thấp (đề xuất) · File bị khóa làm `get()` treo khoảng 14 giây

- **Tái hiện (đo tay, Windows, timeout mặc định 5 giây, tiến trình khác giữ `BEGIN EXCLUSIVE`):** `load` mất **7,05 giây**; `get` mất **14,17 giây** rồi trả đúng danh sách kèm "đang bận". Cách đo: tiến trình con giữ khóa như `_HOLDER_SCRIPT` trong file test, gọi `store.load(...)` và `store.get(...)`, đo bằng `time.monotonic()`.
- **Nguyên nhân:** `get` chờ hết timeout ở `load` (`_is_healthy`), rồi `refresh` → `save` → `_prepare` → `_is_healthy` chờ thêm lần nữa. Trên Windows mỗi lần chờ khoảng 7 giây.
- **Hậu quả:** giao diện đứng khoảng 14 giây mỗi lần gọi `get` khi người dùng đang mở file bằng DB Browser; mỗi lần còn tải lại danh sách từ site.
- **Gợi ý:** `load` đã báo bận thì `refresh` bỏ bước ghi (trả `cache_error` ngay), hoặc giảm timeout của `_is_healthy`. Không viết test (đo thời gian dễ chập chờn); ghi lại để T-036/T-039 biết khi gọi `get` lúc vẽ trang.

### Rủi ro và lưu ý cho phiếu sau

- `list(items)` làm mất cờ `truncated`; nơi dùng nên đọc `SiteIndex.truncated`.
- Câu báo khi file **chỉ đọc** là "bị lỗi… Thử tải lại", trong khi tải lại không giúp được; nên nói "không ghi được". Khi file bị chương trình khác giữ hẳn, câu báo chép `strerror` tiếng Anh của Windows ("The process cannot access the file…"): không lộ bí mật, chỉ lẫn tiếng Anh.
- `PublishedSource.list_published` vẫn khai báo trả `list[PublishedItem]`; `refresh` đọc cờ bằng `getattr`, nên nguồn trả `list` thường luôn ra `truncated = False`. Nguồn mới muốn báo cắt phải trả `PublishedList`.

### Kết luận lượt 2

**ĐẠT.** SL-T037-1 và SL-T037-2 sửa đúng, có test, chạy đúng trên Windows với khóa từ tiến trình và luồng khác. Ba lỗi mới đều Thấp, chỉ đụng file tạm, không chặn gộp:
- SL-T037-3: nên sửa trước Giai đoạn 5 (kiểm link hỏng); ghi vào phiếu đó hoặc T-042.
- SL-T037-4, SL-T037-5: để T-042 hoặc phiếu dọn lỗi Thấp.

Chuyển Lá Chắn (W2, W4, F1, D2).

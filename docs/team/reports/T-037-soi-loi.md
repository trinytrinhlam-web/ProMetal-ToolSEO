# Báo cáo T-037 · Soi Lỗi · Danh sách bài đã đăng + cache SQLite

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-037](../tickets/T-037-danh-sach-bai-da-dang-cache.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành · **ĐẠT CÓ ĐIỀU KIỆN** |

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

## Lượt 2 (2026-10-16) · **CHƯA XONG** (dừng theo yêu cầu bàn giao)

Kiểm lại commit `1fd1415` của Thợ Máy. Đã thêm 26 test `test_r2_*` vào `tests/test_soi_loi_t037.py`, chạy riêng file này: **113 qua, 0 hỏng**. `uv run ruff check .`: sạch.

Đã kiểm (đều đạt):
- **SL-T037-1:** khi file bị khóa và có giao dịch ghi dở (`-journal`), file và `-journal` **không bị xóa** (inode và nội dung giữ nguyên). `reset_count` = 0. `load` trả `None`. `refresh`/`get` vẫn trả danh sách, kèm `cache_error` "đang bận", không ném lỗi. Nhả khóa xong, cache cũ đọc lại bình thường và `refresh` ghi bình thường. File hỏng thật vẫn bị dọn như trước. Thân test `test_locked_file_is_busy_not_corrupt` không đổi, chỉ bỏ dòng `xfail`.
- **SL-T037-2:** cờ `truncated` bật khi bài **hoặc** trang vượt `MAX_PAGES`, **không** bật khi đúng bằng `MAX_PAGES`. Số request luôn tối đa 2 × `MAX_PAGES`, chỉ `GET`. Cờ lưu vào cache rồi đọc lại đúng (cả `True` lẫn `False`). Cờ vẫn giữ khi không ghi được cache. Giá trị lạ (`"2"`, `"true"`, `""`, có khoảng trắng, `"yes"`…) hoặc thiếu thì cache bị coi là hỏng. Cache `SCHEMA_VERSION` 1 bị bỏ, tạo lại thành 2. Ghi chú: ghi tay số `1` vào cột `TEXT` thì SQLite tự đổi thành chuỗi `"1"`, đọc ra `True`; đây là đúng, không phải lỗi. Đã sửa test cũ `…cut_silently` thành `…cut_but_flagged`.
- **Danh sách cho phép:** `PublishedList` là lớp con của `list`, chỉ thêm một thuộc tính dữ liệu `truncated` (mặc định `False`), không có hàm mới. Test cấp module vẫn chặn `publish_post`, `PublishNow`, `_publish_draft`, `PublishedWriter`.
- Lưu ý cho phiếu sau: `list(items)` làm mất cờ `truncated`. Nơi dùng nên đọc `SiteIndex.truncated`, đừng tự chép danh sách.

**Còn thiếu:**
- Chưa chạy lại toàn bộ `uv run pytest` sau khi Thợ Máy gộp `main`. Thợ Máy báo 4.858 qua; Soi Lỗi chưa tự xác nhận.
- Chưa có kết luận cuối. Theo phần đã kiểm thì nghiêng về **ĐẠT**, chờ kết quả chạy toàn bộ.
- Chưa gửi tin cho Chỉ Huy B (theo yêu cầu dừng).

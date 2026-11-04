# Biên bản bảo mật T-122 · Cache số liệu Search Console trong máy (Giai đoạn 6, đợt 1) · đầy đủ

> **Model:** Claude Opus 5.5. Chủ dự án quyết ngày 04/11: hết hạn mức Fable thì dùng Opus.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-122](../tickets/T-122-cache-so-lieu-search-console.md) · mức **đầy đủ** · báo cáo [Thợ Máy](T-122-tho-may.md) (lượt 1, 2), [Soi Lỗi](T-122-soi-loi.md) (lượt 1, 2) |
| Phạm vi | <ul><li>**Nhánh:** `team/T-122` tại `7ceb057`, diff `a499a13..7ceb057` (5 file: `seo_app/storage/search_cache.py` 1.181 dòng, 2 file test, 2 báo cáo). Đọc toàn bộ mã.</li><li>**Đối chiếu:** `seo_app/images/data_dir.py`, `plan_cache.py`, `image_tags.py`, `is_site_link`, thiết kế T-120 mục 3.</li><li>**So chéo:** client T-121 (`origin/team/T-121` `b873a5d`) và gói tính toán T-123 (trên `main` máy `bad6db7`).</li><li>Không gọi Google hay website thật, không sửa mã.</li></ul> |
| Ngày | 2026-11-04 (13:15–13:55, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: gộp `main` được ngay. <ul><li>0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới**:<ul><li>LC-T122-1: file lưu tạm bị sửa tay theo hai kiểu lạ thì phần mềm báo «không mở được» mãi, không tự bỏ file;</li><li>LC-T122-2: `clear()` để lọt lỗi quyền truy cập nguyên dạng.</li></ul></li><li>Cả 9 trọng tâm Chỉ Huy giao **đạt**. LC-T120-9, -10, -15 đạt.</li><li>Thử đột biến: 30/38 bị bắt; nên thêm 4 ca test ghim (G2).</li><li>SL-T122-1, -2, -3 đóng đúng (tôi xác nhận lại).</li><li>Sửa 2 lỗi Thấp ở T-124 hay một lượt nhỏ; điều kiện cho T-124, T-125 ở mục 8.</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Phần lưu tạm số liệu Google trong máy an toàn để gộp.**
  - Không lưu mật khẩu hay khóa, không ghi ra ngoài thư mục phần mềm.
  - Chỉ dùng câu lệnh cơ sở dữ liệu cố định, nên không thể bị chèn lệnh.
  - Mỗi lần đọc đều kiểm lại từng con số.
- **Đã thử nhiều tình huống xấu:** thư mục `data` bị thay bằng lối tắt; file bị sửa tay nhiều kiểu; ngày lạ (năm 1, năm 9999); ký tự hỏng; hai cửa sổ cùng ghi. Phần mềm không để lọt lỗi lạ, không dùng số sai.
- **Ba phần dùng đúng một luật nhận địa chỉ trang:** phần lưu, phần lấy số liệu (T-121) và phần tính toán (T-123). Tôi thử hơn 30.000 địa chỉ, không lệch, không nhận địa chỉ ngoài website.
- **Hai lỗi nhỏ mới (Thấp):**
  - Nếu ai cố ý sửa file lưu tạm theo vài kiểu đặc biệt, phần mềm sẽ báo «không mở được file» mãi, không tự xóa để lấy lại. Cách thoát: xóa file đó, hoặc bấm nút xóa bản lưu tạm (sẽ có ở phiếu giao diện).
  - Nút xóa bản lưu tạm có thể hiện lỗi lạ thay vì câu tiếng Việt, khi Windows từ chối quyền đọc thư mục.
  - Cả hai không lộ gì, không mất dữ liệu thật: bản lưu tạm lấy lại được từ Google. Sửa ở phiếu sau.
- **Không có gì anh/chị phải quyết.**

## 1. Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T122-1 | Thấp | Bước kiểm file (`_is_healthy`, `_prepare`) đọc `sqlite_master` bằng bộ giải mã mặc định. Hai lỗi ở bước này không được coi là «file lạ» mà bị ném lại: lỗi giải mã UTF-8, và lỗi «unsupported file format» (`SQLITE_ERROR`). Vì vậy mọi lần đọc, ghi đều báo `MSG_OPEN`, và file không bao giờ tự bị bỏ | `seo_app/storage/search_cache.py:1112-1132` (`_is_healthy`), `:525-533` (`_prepare`) | <ul><li>**Đầu vào** (cần quyền ghi vào thư mục phần mềm, hay một lần hỏng hiếm), một trong hai: (a) byte UTF-8 hỏng trong tên bảng hay câu tạo bảng; (b) số «schema format» ở đầu file đổi thành 5.</li><li>**Đã chạy:** `load` báo `MSG_OPEN` («có thể chương trình khác đang giữ file, hoặc không có quyền ghi»), file còn nguyên. Ghi số liệu mới cũng `MSG_OPEN` («Số liệu vừa lấy chưa được lưu»). Lần sau vẫn vậy. Chỉ `clear()` hay xóa tay mới cứu được.</li><li>**Mức độ:** không dùng số sai, không lộ gì (đóng an toàn). Nhưng trái hợp đồng «file lạ, hỏng thì bỏ» của module, và câu báo đổ lỗi sai chỗ.</li><li>**Ở kho khác:** `image_tags` không bị vì đọc bằng `bytes`. `plan_cache` có sẵn cùng mẫu: `_is_healthy` ném `OperationalError` (đã chạy); ngoài phạm vi phiếu này.</li></ul> | <ul><li>Trong `_is_healthy` và `_prepare`: đặt `text_factory = _decode_text`, coi `_Corrupt` là file lạ (trả `False`, bỏ file).</li><li>Trong `_is_healthy`: coi mọi `DatabaseError` không phải bận, khóa, lỗi vào ra hay lỗi quyền là file lạ; gồm cả «unsupported file format».</li><li>Thêm 2 ca test cho hai kiểu sửa tay trên: `load` trả `None`, `reset_count == 1`, ghi lại được.</li></ul> |
| LC-T122-2 | Thấp | `clear()` gọi `dir_has_link` ngoài khối `try`. Nếu lúc kiểm gặp `OSError` (ví dụ `PermissionError` khi Windows từ chối `lstat` một tầng thư mục), lỗi lọt ra nguyên dạng thay vì `SearchCacheError` | `search_cache.py:450-457` | <ul><li>**Đã chạy** (giả `dir_has_link` ném `PermissionError`): `load`, `save_post_dates` ra `MSG_IO` câu cố định; `clear()` để lọt `PermissionError`.</li><li>**Hậu quả:** trang T-125 gặp lỗi bất ngờ, chỉ hiện loại lỗi (T-118), không lộ đường dẫn. Cùng loại với SL-T122-3 (Thấp)</li></ul> | Đưa lời gọi `dir_has_link` vào trong `try` của `clear()`, bắt `OSError` thành `MSG_IO`. Thêm 1 ca test |

Không có lỗi Nghiêm trọng, Cao, Trung bình.

## 2. Chín trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `data/` là liên kết (junction, symlink, hard link) | **Đạt.** Chi tiết ngay dưới bảng | Test, đột biến |
| 2 | Một dòng sai thì bỏ cả cache; mã băm phạm vi đổi thì bỏ cache | **Đạt.** Chi tiết ngay dưới bảng | `probe_t122.py` mục C, đột biến |
| 3 | SQL chỉ dùng tham số | **Đạt.** Chi tiết ngay dưới bảng | Soát cây cú pháp |
| 4 | Trần dung lượng, giữ 16 tháng | **Đạt.** Chi tiết ngay dưới bảng | Test, đột biến |
| 5 | Mốc năm biên (`OverflowError`, `ValueError`) | **Đạt.** Không lỗi Python nào lọt ra. Chi tiết ngay dưới bảng | `probe_t122.py` mục C |
| 6 | Surrogate lẻ | **Đạt.** Chi tiết ngay dưới bảng | `probe_t122.py` mục B |
| 7 | Hai tiến trình cùng ghi | **Đạt.** Chi tiết ngay dưới bảng | `race_t122.py` |
| 8 | File SQLite bị sửa tay | **Đạt, trừ LC-T122-1.** Chi tiết ngay dưới bảng | `probe_t122.py` mục A |
| 9 | `site_base` không nới lọc so với `site_prefix` của T-121 và `site_base` của T-123 | **Đạt.** Chi tiết ngay dưới bảng | `cross_t122.py`, bản gộp |

**Trọng tâm 1: `data/` là liên kết**

- `_prepare` và `clear()` gọi `dir_has_link(data/, PROJECT_ROOT)` trước `mkdir` và trước mọi lần mở, nên không lặp SL-T117-1.
- `_is_link` gỡ symlink, junction, reparse point và hard link (`st_nlink > 1`) ở chỗ đặt file và ở `-journal`, `-wal`, `-shm`, không đụng đích của liên kết.
- Test chạy thật trên Windows qua: junction bằng `_winapi.CreateJunction`, hard link bằng `os.link`. Đột biến N01, N02, N03, N31 bị bắt.
- Thư mục thì không có hard link.
- Liên kết đặt vào đúng khoảnh khắc giữa lần kiểm và lần mở thì không chặn được. Cùng lớp với sổ rủi ro dòng 20/10: phải chạy được chương trình trên máy trước.

**Trọng tâm 2: một dòng sai, đổi phạm vi**

- `_read_days`, `_read_queries`, `_read_post_dates`, `_parse_meta` kiểm lại từng dòng như thiết kế 2.4. Lỗi nào cũng thành `_Corrupt`; `load` bỏ file và trả `None`.
- Phạm vi khác thì `load` bỏ file. Ghi với phạm vi khác thì xóa mọi bảng trong cùng giao dịch.
- Mã băm là SHA-256 của `GSC_SITE_URL + "\n" + site_base(WORDPRESS_URL)`. `_check_scope` chặn ký tự < 32, nên không giả được dấu phân cách.
- Đã thử 23 file sửa tay năm biên: 21 bị bỏ cả cache; 2 còn lại là góp ý G1.
- Đột biến N08–N11, N32–N38 (mục 4).

**Trọng tâm 3: SQL chỉ dùng tham số**

- Soát cây cú pháp: 43 lệnh `execute`/`executemany`. Đối số câu lệnh đều là chữ cố định, hay tuple hằng (`_CREATE_TABLES`, `_WIPE`, `_MASTER_SQL`).
- Chỗ duy nhất không phải một chuỗi cố định là `"BEGIN IMMEDIATE" if write else "BEGIN"`, tức chọn giữa hai chuỗi cố định.
- Không f-string, `.format` hay `%` trong SQL. Trần dung lượng đo bằng `page_count × page_size`, không ghép số vào câu lệnh.

**Trọng tâm 4: trần dung lượng, giữ 16 tháng**

- Trần: ≤ 300.000 dòng ngày (kiểm trước và sau khi chèn); ≤ 50.000 dòng mỗi khoảng từ khóa; ≤ 6 khoảng.
- File ≤ 64 MB: khi mở đo `st_size`; khi ghi đo `page_count × page_size` trong giao dịch, quá thì hoàn tác.
- Mỗi lần ghi số liệu ngày, bỏ các ngày cũ hơn 486 ngày. Khi đọc, phần đã lấy dài quá 486 ngày là file lạ.
- Đột biến N18–N20, N22–N24 bị bắt. N21 sống vì lần đếm sau khi chèn vẫn chặn.

**Trọng tâm 5: mốc năm biên**

- **Ghi:** 65 lệnh với năm 1, 9999, 1999, 2201, `date.min`/`max`, `datetime.min`/`max` có múi ±23:59, giờ không múi giờ, sai kiểu. Đều ra `MSG_BAD_DATA`.
- `_stamp` kiểm năm cả trước lẫn sau khi đổi múi giờ (SL-T122-2 đóng).
- **Đọc:** 23 file sửa tay năm biên ở mọi cột ngày giờ: 0 lỗi lọt; 21 bị bỏ cả cache; 2 mốc `fetched_at` có múi ±23:59 vẫn đọc nhận (góp ý G1).

**Trọng tâm 6: surrogate lẻ**

- 9 ký tự lạ × 5 đầu vào. Ký tự: U+D800, U+DFFF, NUL, DEL, NEL, U+202E, U+200B, BOM, xuống dòng. Đầu vào: thuộc tính, `WORDPRESS_URL`, trang của `save_days`, trang của `save_queries`, từ khóa.
- 0 lỗi Python lọt. Surrogate ở phạm vi ra `MSG_BAD_SCOPE`; ở trang, từ khóa ra `MSG_BAD_DATA` (SL-T122-3 đóng).
- Ký tự lạ không phải surrogate ở phạm vi (NEL, U+202E…) được nhận, vì phạm vi chỉ dùng để băm, không lưu, không hiện.

**Trọng tâm 7: hai tiến trình cùng ghi**

- 3 tiến trình chạy 6 giây: ghi ngày; ghi từ khóa và ngày đăng; đọc. 173 thao tác: 0 lỗi, 0 lần «bận», 0 lần bỏ cache, lần đọc cuối đủ dữ liệu.
- Mọi lần ghi dùng `BEGIN IMMEDIATE`, chờ 1 giây rồi báo `MSG_BUSY`.
- Soi Lỗi đã thử thêm: 3 tiến trình × 10 giây, khóa độc quyền, nhật ký nóng sau `os._exit`.

**Trọng tâm 8: file SQLite bị sửa tay**

- `sqlite_master` phải khớp đúng các bảng app tạo. Kiểm hai lần: trước khi mở (`_is_healthy`) và **trong** giao dịch của thao tác.
- Đã thử tráo file: trigger cài chen vào giữa hai lần kiểm bị bắt, file bị bỏ.
- Lớp phòng thêm: `trusted_schema = OFF`, giới hạn độ dài 1.000.000, giới hạn 400 triệu bước, `quick_check`.
- Đã thử thêm, đều xử lý đúng:
  - chế độ WAL;
  - file mã hóa UTF-16 cùng cấu trúc: đọc đúng;
  - giá trị `info` dài 1,2 triệu ký tự: bỏ file;
  - phiên bản đọc 3 ở đầu file: bỏ file.
- Hai kiểu sửa làm cache kẹt: LC-T122-1.

**Trọng tâm 9: `site_base` không nới lọc**

- `site_base` của T-122 giống từng dòng bản T-123 (trên `main` máy `bad6db7`).
- So chéo 13 cách viết `WORDPRESS_URL` × 30.026 địa chỉ (26 mẫu + 30.000 địa chỉ dò ngẫu nhiên):

  | So | Lệch |
  |---|---|
  | `site_base` với bản T-123 | 0 |
  | Tiền tố với `site_prefix` T-121 `b873a5d` (mọi cách viết T-121 nhận) | 0 |
  | Dòng T-121 nhận mà cache bỏ | 0 |
  | Dòng cache nhận mà T-121 bỏ | 0 |
  | Cache nhận địa chỉ ngoài website (với cách viết của website thật) | 0 |
  | Cache lưu mà T-123 bỏ | 1.260, **đều** là `%` giải mã ra UTF-8 hỏng: T-123 cố ý coi là «dòng lạ» và đếm |

- Trên bản gộp `main` + T-122 + T-121, ca so chéo `test_lan_2_site_rules_match_t121_and_t123` của Soi Lỗi chạy thật và qua.

## 3. Điều kiện LC-T120 của phiếu

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T120-9 | Đạt, trừ LC-T122-1 | <ul><li>Kiểm như `plan_cache`.</li><li>Một dòng sai: bỏ cả cache. Mã băm phạm vi đổi: bỏ cache.</li><li>`data/` là liên kết: không mở (`dir_has_link` từ đầu).</li><li>SQL chỉ dùng `?` (mục 2).</li></ul> |
| LC-T120-10 | Đạt | <ul><li>Năm được kiểm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError`, `ValueError` (mục 2, trọng tâm 5).</li><li>Đột biến N13, N15, N16 bị bắt.</li><li>N14, N17 sống vì test chưa ghim; mã thật chặn đúng (G2).</li></ul> |
| LC-T120-15 | Đạt | <ul><li>Plugin `sys.addaudithook` khi chạy 2 file test: 0 kết nối, 0 tra tên.</li><li>Hai sự kiện ghi được đều vô hại:<ul><li>`bind(('::1', 0))` lúc nhập urllib3 (thử máy có IPv6 không);</li><li>một tiến trình con Python chỉ chạy SQLite trên file tạm (ca nhật ký nóng của Soi Lỗi).</li></ul></li><li>File `.env` mồi đặt ở gốc worktree: mã băm trước, sau như nhau.</li><li>Ca biên mục 2.4 có test (báo cáo Thợ Máy, mục LC-T120-15) và bị thử đột biến (mục 4).</li><li>Không có trang mới.</li></ul> |

## 4. Thử đột biến

Mỗi đột biến sửa đúng một chỗ của `search_cache.py` trên bản chép (`git archive 7ceb057`), rồi chạy 2 file test với `-x`. Bản gốc: 210 qua.

| Mã | Đột biến | Kết quả |
|---|---|---|
| N01 | Bỏ `dir_has_link` khi mở | Bắt |
| N02 | Bỏ kiểm hard link | Bắt |
| N03 | `_is_link` luôn `False` | Bắt |
| N04 | Bỏ kiểm `sqlite_master` **trong** giao dịch | Sống: `_is_healthy` vừa kiểm ngay trước; lớp này chỉ chặn file bị tráo giữa hai lần kiểm. Đã thử tay: bắt được (G2) |
| N05 | Bỏ `trusted_schema = OFF` | Sống: lớp phòng; phép so cấu trúc chặn khung nhìn, trigger trước |
| N06 | Bỏ giới hạn số bước | Sống: lớp phòng |
| N07 | Bỏ giới hạn độ dài giá trị | Sống: lớp phòng; `substr` và phép đo `length(CAST(… AS BLOB))` vẫn chặn |
| N08 | Đọc bỏ qua mã băm phạm vi | Bắt |
| N09 | Đọc không kiểm địa chỉ trang | Bắt |
| N10 | Đọc không kiểm `final` khớp ngày tạm | Bắt |
| N11 | Cho `NaN`, vô cực qua phép kiểm số | Bắt |
| N12 | `_utf8_ok` luôn `True` (surrogate) | Bắt |
| N13 | `_stamp` bỏ kiểm năm **sau** khi đổi múi giờ | Bắt |
| N14 | `_stamp` bỏ kiểm năm **trước** khi đổi múi giờ | **Sống, thiếu test** (G2). Năm 1, 9999 vẫn bị chặn nhờ lớp bắt lỗi tràn và phép kiểm sau khi đổi. Chỉ mốc `1999-12-31T23:00` múi −23:00 lọt (thành năm 2000 giờ Việt Nam), vô hại |
| N15 | `_parse_time` bỏ kiểm năm | Bắt |
| N16 | `_parse_day` bỏ kiểm năm | Bắt |
| N17 | `_day_arg` bỏ kiểm năm | **Sống, thiếu test** (G2). Đã thử: bỏ phép kiểm này thì `save_days(today=năm 1)` lọt `OverflowError`, còn `save_post_dates` ghi được ngày năm 1 rồi lần đọc sau bỏ cả cache. Mã thật chặn đúng cả hai (`probe_t122.py` mục C) |
| N18 | Bỏ trần 64 MB khi ghi | Bắt |
| N19 | Bỏ trần 64 MB khi mở | Bắt |
| N20 | Bỏ đếm dòng ngày sau khi chèn | Bắt |
| N21 | Bỏ trần dòng ngày trước khi ghi | Sống: lần đếm sau khi chèn vẫn chặn. N22 bỏ cả hai thì bị bắt |
| N22 | Bỏ cả hai trần dòng ngày | Bắt |
| N23 | Bỏ xóa ngày cũ hơn 16 tháng | Bắt |
| N24 | Giữ mọi khoảng từ khóa | Bắt |
| N25 | `_check_scope` bỏ chặn ký tự điều khiển | Bắt |
| N26 | Giải mã UTF-8 dễ dãi | Bắt |
| N27 | `_page` bỏ so tiền tố | Bắt |
| N28 | `_page` bỏ `is_site_link` | Bắt |
| N29 | `site_base` về bản cũ (SL-T122-1) | Bắt |
| N30 | Bỏ `quick_check` | Sống: lớp phòng; SQLite báo hỏng khi đọc thì file vẫn bị bỏ |
| N31 | Quên `-wal` trong danh sách file nhật ký | Bắt |
| N32 | Từ khóa không cần đã làm sạch | Bắt |
| N33 | Bỏ so số dòng mỗi khoảng | Bắt |
| N34 | Bỏ so phiên bản cấu trúc | Bắt |
| N35 | Ghi không xóa dữ liệu của phạm vi khác | Bắt |
| N36 | Ghi không kiểm `final` khớp ngày tạm | Bắt |
| N37 | Đọc bỏ kiểm quan hệ của phần đã lấy | Bắt |
| N38 | Bỏ kiểm mã bài của ngày đăng | Bắt |

30/38 bị bắt. 8 sống:
- 6 là lớp chặn trùng: lớp còn lại vẫn đủ.
- 2 (N14, N17) là phép kiểm năm: mã có và chặn đúng, nhưng test chưa ghim (G2).

## 5. Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets 5 file: 0 kết quả, mồi bị bắt. Lịch sử git chỉ có dữ liệu thử giả (mật khẩu giả cố ý tách chuỗi) và câu nhắc trong báo cáo |
| S2 | Đạt | Câu lỗi cố định; `MSG_IO` chỉ chèn `strerror` (không đường dẫn). File không lưu thuộc tính hay `WORDPRESS_URL`, chỉ mã băm (`test_file_keeps_no_property_or_secret`) |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi |
| W1 | Không áp dụng | Không gọi WordPress |
| W2 | Không áp dụng | |
| W3 | Không áp dụng | |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Không có prompt |
| A2 | Không áp dụng | |
| A3 | Đạt | Từ khóa của người lạ chỉ nằm trong máy (`data/`, git chặn), không gửi đi đâu (thiết kế 3.4, cách A) |
| U1 | Không áp dụng | Không có giao diện. T-125: hiện câu của `SearchCacheError` (mục 8) |
| U2 | Không áp dụng | |
| U3 | Không áp dụng | |
| F1 | Đạt | Chỉ ghi `data/search_cache.sqlite` và file nhật ký của nó. `data/` là liên kết thì không mở; file là liên kết thì chỉ gỡ liên kết. Đột biến N01–N03, N31 bị bắt |
| F2 | Không áp dụng | Không có ảnh |
| F3 | Đạt | Không `eval`, `exec`, `pickle`. File là dữ liệu chưa tin cậy: kiểm cấu trúc, `trusted_schema = OFF`, giới hạn độ dài, số bước. bandit 0 lỗi |
| D1 | Đạt | Chỉ thư viện chuẩn (`sqlite3`, `hashlib`, `zoneinfo`). `pyproject.toml`, `uv.lock` không đổi |
| D2 | Đạt | `.gitignore:22` (`data/`) chặn cả file cache lẫn file nhật ký (`git check-ignore`) |
| D3 | Đạt | Audit hook: 0 kết nối, 0 tra tên (LC-T120-15) |

## 6. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy, vì không đổi thư viện | `git diff a499a13 7ceb057 -- pyproject.toml uv.lock` trống |
| bandit | 0 lỗi, 997 dòng (`search_cache.py`) | Có `PYTHONUTF8=1` |
| detect-secrets | 5 file đổi: `{}`. Mồi (bản chép `search_cache.py` thêm 2 khóa giả): bị bắt | Chạy trên bản chép, đứng tại thư mục chép, đường dẫn tương đối, `--all-files`, `PYTHONUTF8=1` |
| Soát lịch sử git | Sạch | `git log -p a499a13..7ceb057` |
| pytest | <ul><li>Nhánh: 2 file, **210 qua**, 3 bỏ qua (symlink file trên Windows; 2 ca ghép cần T-121, T-123).</li><li>Bản gộp `main` máy `bad6db7` + T-122: 9 file (thêm test T-123), **528 qua**, 2 bỏ qua; ca ghép T-123 chạy thật.</li><li>Bản gộp thêm T-121 `b873a5d`: 2 file, **212 qua**, 1 bỏ qua (symlink); ca so chéo chạy thật.</li></ul> | <ul><li>`git merge-tree` không xung đột ở cả hai lần.</li><li>Mã T-122 giữ nguyên sau gộp.</li><li>`seo_app` nạp từ chính bản gộp.</li><li>Không chạy toàn bộ pytest, theo tin giao.</li></ul> |
| ruff | `ruff check .` sạch; `ruff format --check` 3 file sạch | |

## 7. Báo nhầm đã loại

- **1.260 địa chỉ cache lưu mà T-123 bỏ:**
  - đều có `%` giải mã ra UTF-8 hỏng; T-123 cố ý bỏ các dòng này và đếm vào `skipped_rows`;
  - T-121 cũng nhận chúng, nên không lệch với đường lấy số liệu;
  - Soi Lỗi đã ghi cùng hiện tượng (15 ca `%C3`).
- **Sự kiện `socket.bind ::1` và `subprocess.Popen` trong móc kiểm:** không phải gọi mạng (xem LC-T120-15).
- **Phạm vi nhận NEL, U+202E…:** phạm vi chỉ được băm, không lưu, không hiện. T-121 và client WordPress đều từ chối các giá trị đó.

## 8. Điều kiện

**Gộp `main` được ngay.** Chỉ Huy chép vào phiếu:

1. **LC-T122-1, LC-T122-2 (Thấp) → T-124** (phiếu ghép, sửa cùng lúc khi gom `site_base`), hay một lượt nhỏ của T-122 trước T-125. Cùng lượt đó thêm 4 ca test ghim của G2. Không chặn gộp.
2. **T-125:**
   - hiện câu của `SearchCacheError`;
   - khi `MSG_OPEN` hay `MSG_BROKEN` lặp lại, có nút «Xóa bản lưu tạm» gọi `clear()`: đây là đường thoát cho LC-T122-1 tới khi sửa xong;
   - không đưa `SearchCache` qua `st.cache_data` (GN-1 của Soi Lỗi).
3. **T-124:**
   - coi `fetched_at` ở tương lai là cũ (GN-2 của Soi Lỗi);
   - gom 3 bản `site_base` về một hàm, giữ bảng ca chung;
   - đồng hồ bị chỉnh lùi (`covered_end` sau hôm nay) thì gọi `clear()`.
4. **Ngoài phạm vi (mở phiếu dọn riêng, Thấp):** `plan_cache._is_healthy` có cùng mẫu với LC-T122-1. Đã chạy: nó ném `OperationalError` thay vì trả `False`. `site_index` không bị theo phép thử này.

## 9. Góp ý (không xếp lỗi)

- **G1. `_parse_time` không kiểm năm sau khi đổi múi giờ** (khác `_stamp`).
  - File sửa tay có `2000-01-01T00:00:00+23:59` đọc ra mốc năm 1999 giờ Việt Nam.
  - Không tràn, không lỗi; chỉ lệch với hợp đồng «một giá trị lạ thì bỏ».
  - Muốn đối xứng với `_stamp`: kiểm lại năm sau khi đổi.
- **G2. Thêm 4 ca test ghim.** Mã hiện đúng, chỉ thiếu test; đột biến N04, N14, N17 đang sống.
  - Cài trigger ngay sau `_prepare`: `load` phải trả `None` (lớp kiểm cấu trúc trong giao dịch; đã chạy thử: bắt được, file bị bỏ).
  - `save_days(today=date(1, 1, 1))`: phải ra `SearchCacheError`.
  - `save_post_dates({7: date(1, 1, 1)})`: phải ra `SearchCacheError`, cache cũ còn nguyên.
  - `save_queries(fetched_at=1999-12-31T23:00` múi −23:00`)`: phải ra `SearchCacheError` (ghim quy tắc kiểm năm trước khi đổi múi giờ).
- **G3.** Đồng ý GN-1, GN-2, GN-4, GN-5, GN-7 của Soi Lỗi.

## 10. Lệnh đã chạy

```
# Thư mục nháp của phiên; .venv của wt-T-122
python -X utf8 probe_t122.py
  A. 7 kiểu sửa tay: 2 kiểu kẹt MSG_OPEN (UTF-8 hỏng ở sqlite_master; schema format 5) → LC-T122-1
  B. 9 ký tự lạ × 5 đầu vào: lọt lỗi Python 0
  C. ghi 65 lệnh năm biên: lọt 0; đọc 23 file sửa tay năm biên: lọt 0, bỏ cache 21, nhận 2 (G1)
python -X utf8 healthy_same_pattern.py      # _is_healthy: search_cache, plan_cache ném lỗi; image_tags False
python -X utf8 cross_t122.py gen|t121|cmp …  # 13 cách viết × 30.026 địa chỉ: lệch 0 (mục 2, trọng tâm 9)
python -X utf8 race_t122.py …               # 3 tiến trình × 6 giây: 173 thao tác, 0 lỗi
python - (giả dir_has_link ném PermissionError)   # clear() để lọt PermissionError → LC-T122-2
python - (cài trigger ngay sau _prepare)          # bị bắt trong giao dịch, file bị bỏ (G2)
soát cây cú pháp search_cache.py                 # 43 lệnh SQL, đều chữ cố định

uv run pytest -p lc_audit_plugin tests/test_search_cache.py tests/test_soi_loi_t122.py -q
                                                 # 210 passed, 3 skipped; .env mồi không đổi
python -X utf8 mutate_t122.py <bản chép> …       # 38 đột biến: 30 bị bắt, 8 sống (mục 4)
python - (giả bỏ kiểm năm của _day_arg, _stamp)  # N17: lọt OverflowError; N14: mốc 1999 −23:00 lọt (G2)
git merge-tree --write-tree bad6db7 7ceb057      # không xung đột → commit thử e74eec2 (không đẩy)
git merge-tree --write-tree e74eec2 b873a5d      # không xung đột → commit thử 9b1509d (không đẩy)
PYTHONPATH=<bản gộp> python -m pytest …          # 528 passed, 2 skipped / 212 passed, 1 skipped
uv run ruff check .; uv run ruff format --check …   # sạch
PYTHONUTF8=1 uvx detect-secrets scan --all-files …  # 5 file {}; mồi bị bắt
PYTHONUTF8=1 uvx bandit -r seo_app/storage/search_cache.py   # No issues identified
uv --version                                     # 0.13.4
```

- Không gọi Google, WordPress thật; không chạy cloud; không chạy toàn bộ pytest; không sửa mã hay test.
- Script, bản chép, bản gộp thử để ở thư mục nháp, không commit.

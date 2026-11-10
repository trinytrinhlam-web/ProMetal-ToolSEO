# Biên bản bảo mật T-131 · Dọn kho dữ liệu phụ: kiểm file và chặn `data/` là liên kết cho `site_index`, `plan_cache`, kho nháp `drafts.py` · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 10/11 sau lượt 2 (Thợ Máy `147c9f1`, Soi Lỗi `fcc1d1d` ĐẠT). Phiếu cuối để đóng Giai đoạn 4 (điều kiện 2 của Lá Chắn T-129).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-131](../tickets/T-131-don-kho-du-lieu-phu.md). Nhánh `team/T-131`: Thợ Máy lượt 1 `e53ee48` (`site_index`, `plan_cache`), Soi Lỗi lượt 1 `5b83fde` (ĐẠT CÓ ĐIỀU KIỆN, SL-T131-1 Thấp), gộp `main` `7153f0a` ở `cd575a9`, Thợ Máy lượt 2 `147c9f1` (SL-T131-1, `drafts.py`, docstring `set_gsc_site_url`), Soi Lỗi lượt 2 `fcc1d1d` (ĐẠT, 0 lỗi mới). Đầu nhánh **`fcc1d1d`**, đã push |
| Phạm vi | **Đầy đủ**: toàn bộ diff của phiếu so với gốc đã gộp `main` (`git diff 7153f0a..fcc1d1d`): `seo_app/storage/drafts.py` (+395: `_connect`, `_prepare`, `_move_aside`, `_Checked`, `_is_link`, `_remove_link`, `_guard`, `_expected_schema`, `_app_tables`, `_create_tables`, `_is_healthy`), `site_index.py` (+299), `plan_cache.py` (+70), `env_file.py` (docstring), 3 file test mới, 2 file test cũ sửa (R5). Đọc cùng code không đổi mà lớp mới bọc: 11 thao tác của `DraftStore` (`save`, `load`, `list_drafts`, `delete`, `load_send_state`, `send_state_if_exists`, `save_send_state`, `find_plan_draft`, `load_plan_write`, `save_plan_write`, `list_plan_writes`), `data_dir.dir_has_link`/`is_link` (T-117), nơi hiện `recovered_from` ở ba trang. Không chạm website, Google; không chạy cloud |
| Ngày | 2026-11-10 (giao ≈ 12:50, xong 16:34, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, SQLite 3.53.1, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; không vòng chờ dài. Máy chưa bật Developer Mode: ca symlink bỏ qua, liên kết thử bằng junction và hard link |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `d4a015e`: `git merge-tree` không xung đột; `main` từ `7153f0a` không sửa file nào của phiếu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp có từ trước T-131** (LC-T131-1: hai kiểu sửa tay file nháp làm một thao tác báo lỗi mãi, file không được cất đi; test `xfail(strict=True)`). Cả **8 trọng tâm** Chỉ Huy giao đạt; LC-T129-1, SL-T117-1, mẫu LC-T122-1, T-124 ĐK 4 **đã làm đúng**; **SL-T131-1 đã đóng** (xác nhận lại). Khóa chống gửi trùng (T-086, T-089, T-092, T-130) **không bị nới**; không ca nào xóa dấu «đã gửi». R5 đúng. Điều kiện chỉ cho phiếu gom kiểm file và máy Mac, không chặn gộp |

## Tóm tắt (cho chủ dự án)

Ba file dữ liệu phụ trong máy (danh sách bài đã đăng, kế hoạch đọc từ Sheet, **kho nháp bài viết**) nay được kiểm như file số liệu Google (T-122). **An toàn để gộp**, và với kho nháp tôi xác nhận **không mất dấu «đã gửi»** chống gửi trùng:

- **Thư mục `data` là lối tắt trỏ ra ngoài:** cả ba kho không tạo, không mở, không ghi, không đổi tên gì ở đó, chỉ báo một câu cố định. Tôi thử bằng lối tắt thật (junction) trỏ tới thư mục ngoài có sẵn file nháp hợp lệ: 0 lần mở SQLite, thư mục đích nguyên từng byte.
- **File nháp bị chương trình khác cài thêm bảng, trigger, hay chỗ đặt file là lối tắt:** phần mềm **cất file sang một bên (giữ lại, không xóa)** rồi dùng file mới; trigger không bao giờ chạy; dấu «đã gửi» còn nguyên trong file cất đi. File nháp bị khóa lúc mở app: chỉ báo «đang bận», giữ nguyên file, nhả khóa là dùng tiếp.
- **File nháp các bản trước** (trước T-086, trước T-100) mở được như cũ, bảng thiếu được tạo thêm, nháp và dấu «đã gửi» giữ nguyên (ca của Thợ Máy, tôi đọc mã và chạy lại).
- **Lỗi nhỏ Soi Lỗi tìm ra (SL-T131-1)** đã sửa đúng: cache kế hoạch gỡ lối tắt ở file phụ **trước** khi SQLite mở file, như hai kho kia.
- **Tôi tìm thêm một lỗi nhỏ có từ trước (LC-T131-1):** hai kiểu sửa tay file nháp (một ô chữ bị hỏng mã; hai byte đầu file ghi phiên bản lạ) làm danh sách nháp hay việc lưu nháp báo «File nháp bị lỗi» mãi, file không được cất đi. Phải có chương trình lạ ghi được vào thư mục `data` mới xảy ra; nháp, dấu «đã gửi» không mất (vẫn đọc được). Sửa ở phiếu gom kiểm file, không chặn.
- **Việc của anh/chị lúc này:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Lớp bọc `_Checked`: kiểm trong cùng giao dịch với mỗi thao tác, không phá so-rồi-đặt của T-089, T-092 — **đạt**

- `_connect` (`drafts.py:1217`): mỗi thao tác một kết nối `isolation_level=None` (không tự mở giao dịch), `_guard`, rồi trao `_Checked(conn)`; xong thì `COMMIT`, lỗi (kể cả `DraftError` thao tác tự ném, `DraftGoneError` của T-092) thì `ROLLBACK` rồi ném tiếp. `_ForeignFile` không phải `DraftError` nên thao tác nào bắt `DraftError` cũng không nuốt; `_connect` đổi thành `DraftError(_MSG_BROKEN)` và đặt `_ready = False` để lần mở sau kiểm lại file.
- `_Checked.execute` (`:1756-1760`): câu đầu tiên là `BEGIN`/`BEGIN IMMEDIATE` thì chạy đúng câu đó rồi kiểm; câu ghi (`INSERT`, `DELETE`, `UPDATE`, `REPLACE`) thì `BEGIN IMMEDIATE` rồi kiểm; câu đọc thì `BEGIN` rồi kiểm. Tôi liệt kê **mọi** câu `BEGIN` trong các thao tác: `save(must_exist=True)` `:971`, `send_state_if_exists` `:1082`, `save_send_state(expected=…)` `:1109`, `save_plan_write(expected=…)` `:1172`, đều đúng chữ `"BEGIN IMMEDIATE"`/`"BEGIN"` (không dấu `;`, không `EXCLUSIVE`), nên nhánh «câu đầu là BEGIN» luôn khớp. Đối tượng trao cho thao tác chỉ bị gọi `execute` (grep: không `executemany`, `commit`, `rollback`, `cursor`).
- **So rồi đặt giữ nguyên:** ở `save(must_exist=True)`, `save_send_state`, `save_plan_write`, khóa ghi (`BEGIN IMMEDIATE`) được giành **trước** câu kiểm cấu trúc và trước câu «nháp còn / trạng thái cũ», đúng thứ tự T-089, T-092; `send_state_if_exists` giữ khóa đọc tới hết thao tác. Soi Lỗi lượt 2 thử hai luồng thật (hai kho giành «đang gửi», xóa đúng lúc tab kia lưu): đúng; đột biến R1 (`BEGIN` thường thay `BEGIN IMMEDIATE`) bị bắt. Các file test T-086, T-089, T-092, T-130 qua trong lô của tôi (mục Kết quả công cụ quét).
- Cấu trúc khác app tạo phát hiện giữa thao tác: `_ForeignFile` **trước câu đầu tiên** của thao tác (chưa đọc, chưa ghi gì); `test_kiem_cau_truc_trong_cung_giao_dich_voi_thao_tac` (6 thao tác), `test_file_bi_cai_trigger_khi_dang_chay_thi_khong_ghi`.

### 2. Chỗ đặt file là liên kết: **đổi tên** sang một bên, không xóa — **đạt, đồng ý cách chọn**

`_prepare` (`:1247`): `_is_link(self.path)` (symlink, junction, reparse point qua `data_dir.is_link`; **hard link** qua `st_nlink > 1`) → `_move_aside` (`:1291`): `self.path.replace(target)` đổi tên **chính liên kết**, không đi theo; mang theo file nhật ký; không ghi đè tên đã có (`exists() or is_symlink()`). Khác các kho lưu tạm (xóa liên kết) là đúng: kho nháp giữ dữ liệu người dùng và dấu «đã gửi»; tên đổi (`drafts.hong-YYYYmmdd-HHMMSS[-n].sqlite`) là lối vào dữ liệu đó, không lộ đường dẫn (ba trang chỉ hiện `.name`). Probe E: hard link tới file nháp hợp lệ ngoài dự án → đổi tên, file ngoài nguyên từng byte, kho mới là file thường (`st_nlink == 1`). Grep: trong `drafts.py` không còn `unlink` nào trên chính file nháp.

### 3. `data/` là liên kết: không tạo, không mở, không đổi tên gì — **đạt** (SL-T117-1)

`dir_has_link(self.path.parent, PROJECT_ROOT)` là việc **đầu tiên** của `_prepare` ở **mỗi** lần mở (không còn `return` sớm theo `_ready` trước bước này): `DraftError(MSG_DATA_DIR_LINK)` trước `mkdir`, trước mọi `sqlite3.connect`, trước mọi đổi tên; `OSError` khi kiểm (quyền) thành câu cố định. `site_index._prepare`, `clear`; `plan_cache._prepare`, `clear` cùng mẫu (có `clear` trong `try`, như LC-T122-2). Probe F (junction thật ở `data/<thư mục con>` trỏ tới thư mục ngoài có file nháp hợp lệ): `list_drafts`, `save` → đúng câu `MSG_DATA_DIR_LINK`, **0** lần `sqlite3.connect`, thư mục đích nguyên. Ca SL-T117-1 `[kho-nhap]` của Soi Lỗi T-117 đã gỡ `xfail` và qua (3 kho).

### 4. File nhật ký là liên kết thì gỡ **trước** khi SQLite mở — **đạt** (SL-T131-1 đóng)

- `drafts._prepare`: vòng `_remove_link` trên `-journal`, `-wal`, `-shm` đứng ngay sau `dir_has_link`, trước `_is_link(self.path)`, trước `is_file()`, trước `_is_healthy`, `_create_tables` và trước kết nối của thao tác; `_remove_link` chỉ `unlink` (junction: `rmdir`) **chính liên kết**. `test_ten_nhat_ky_la_lien_ket_go_truoc_khi_sqlite_mo` (3 tên, đếm `sqlite3.connect` bằng `ConnectSpy`), `test_shm_la_hard_link_khong_bao_gio_ghi_xuyen` (chế độ WAL, file ngoài 68 KB nguyên).
- `plan_cache._prepare` (`plan_cache.py:249`): nay `dir_has_link` → `_is_link(self.path)` → `_reset` → gỡ liên kết ở ba tên nhật ký → **rồi mới** `_is_healthy`; đúng thứ tự `site_index` (`site_index.py:346`) và `search_cache`. 4 ca SL-T131-1 của Soi Lỗi (`[plan-cache]`, `[plan-cache--journal|-wal|-shm]`) gỡ `xfail` và qua trong lô của tôi. R5: `git diff 5b83fde..fcc1d1d -- tests/test_soi_loi_t131.py` chỉ xóa hằng `SL_T131_1` và `marks=SL_T131_1` ở tham số `plan-cache` (và đổi dòng `import` để thêm kho nháp cho lượt 2); thân test không đổi. Đúng.

### 5. `trusted_schema = OFF`, trần số bước, trần độ dài — **đạt**

`_guard` (`drafts.py:1794`) đặt `PRAGMA trusted_schema = OFF`, `setlimit(SQLITE_LIMIT_LENGTH, 4 × MAX_DRAFT_BYTES)`, `set_progress_handler` dừng sau `_MAX_VM_STEPS` = 50 triệu bước; gọi trên **mọi** kết nối mở file nháp: `_connect`, `_create_tables`, `_is_healthy` (`_expected_schema` chỉ mở `:memory:`). `site_index._guard` cùng mẫu (50 triệu bước, 1 MB; đo của Thợ Máy: cỡ lớn nhất dùng chưa tới 1 %); `plan_cache` có từ T-100. Quá số bước (`SQLITE_INTERRUPT`), giá trị quá dài (`SQLITE_TOOBIG`) không nằm trong `_KEEP_FILE_CODES` nên ở bước kiểm là «file lạ», trong thao tác thì `_ready = False` để lần sau kiểm lại. `test_ket_noi_kho_nhap_duoc_rao`, `test_qua_so_buoc_la_file_la`, `test_o_dai_qua_tran_la_file_la`; `site_index`: `test_site_index_connections_are_guarded`, `test_site_index_too_many_steps_counts_as_foreign_file`.

### 6. File lạ hay hỏng: đổi tên, không xóa — **đạt**

`_is_healthy` (`:1899`) trả `False` **chỉ khi chắc chắn**: `_app_tables` khác (so trọn `sqlite_master` với lược đồ dựng trong bộ nhớ từ chính ba câu tạo bảng, đọc thành byte nên UTF-8 hỏng trong `sqlite_master` là «khác», `LIMIT` + đếm dòng lặp như LC-T070-1), `quick_check` khác `ok`, ô dài quá trần, hay SQLite báo mã ngoài `_KEEP_FILE_CODES` (hỏng, không phải cơ sở dữ liệu, «unsupported file format», quá dài, quá số bước). Khi đó `_prepare` gọi `_move_aside` (đổi tên, mang theo nhật ký), rồi `_create_tables` trên file mới. Probe C: file bị `ANALYZE` (`sqlite_stat1`) và cài trigger `AFTER INSERT ON drafts` xóa `send_states` → đổi tên; file cất đi còn đúng 1 nháp, dòng «đã gửi 501», trigger còn nguyên nhưng **không chạy** (app không chèn vào file đó); file mới chỉ có ba bảng. Thợ Máy 10 ca cấu trúc lạ (trigger ×2, khung nhìn, bảng, chỉ mục, `ANALYZE`, câu tạo bảng khác chữ ×4), UTF-8 hỏng trong `sqlite_master`. Bảng thiếu (file cũ) không phải «lạ»: `_create_tables` tạo thêm trong giao dịch ghi có kiểm lại.

### 7. File bận lúc mở lần đầu: chỉ báo bận, giữ file — **đạt**

`_is_healthy` ném lại lỗi bận/khóa và mọi mã `_KEEP_FILE_CODES` (3, 5, 6, 7, 8, 10, 13, 14, 15); `_prepare` đổi thành `DraftError(_db_message)` «đang bận…», `_ready` vẫn `False`, **không** `_move_aside`. Probe D (kết nối khác giữ `BEGIN EXCLUSIVE`): «File nháp đang bận…», không có file `.hong-`; nhả khóa thì `list_drafts` chạy, dấu «đã gửi 501» còn. Trước T-131 ca này bị coi là hỏng (Thợ Máy nêu): T-131 **sửa đúng hướng giữ dữ liệu**. `test_file_ban_luc_kiem_khong_bi_doi_ten`.

### 8. Không mất dấu «đã gửi» trong mọi ca — **đạt** (với ghi nhận G2 của Soi Lỗi)

- Các hàm trạng thái gửi (`load_send_state`, `send_state_if_exists`, `save_send_state`, `_trim_orphan_send_states`, đường T-130 giữ dòng mồ côi) **không đổi dòng nào** (diff chỉ chạm phần mở kho, kiểm file, hàm mới). Đường xóa dòng `send_states` vẫn chỉ hai như T-130.
- Đường mới của T-131 không xóa gì: bận → giữ file; cấu trúc lạ giữa thao tác → cuộn lại, chưa ghi; file lạ, chỗ đặt file là liên kết → **đổi tên**, dấu còn trong file cất đi (probe C, E; ca Soi Lỗi hard link còn «đã gửi 501»); `data/` là liên kết → không đụng. File cũ ba đời giữ nguyên dấu. Hai tab so rồi đặt: mục 1.
- **G2 (Soi Lỗi, Thợ Máy đã nêu):** file bị cất đi thì app không còn thấy dấu đó; tab đang mở bài gặp «nháp không còn» (T-092), lưu lại thì nháp mới không có khóa gửi trùng → có thể gửi thêm **một bài nháp** trùng (không đăng, W1 vẫn giữ: «Đăng ngay», «Hẹn giờ» cần người bấm xác nhận và công tắc đang tắt). Chỉ khi chương trình khác sửa file; trước T-131 file hỏng cũng vậy, nay thêm các kiểu «lạ» (bảng, trigger, liên kết). Chấp nhận ở phiếu này; điều kiện B.2 cho phiếu sau (chép dòng `send_states` qua khuôn `SendState` từ file cất đi sang file mới).

## Lỗi phát hiện

| Mã | Mức | Mô tả | Ở đâu | Đầu vào · đã chạy · hậu quả | Sửa |
|---|---|---|---|---|---|
| **LC-T131-1** | **Thấp, có từ trước T-131** | Hai kiểu sửa tay file nháp mà bước kiểm file (`_is_healthy`) **không nhận ra**, làm một thao tác báo `_MSG_BROKEN` **mãi**, file không được cất sang một bên, trong app không có cách thoát (cùng lớp GN-1 của Soi Lỗi T-131 ở ba kho lưu tạm) | `drafts.py`: `_is_healthy` (`:1899`, chỉ kiểm cấu trúc, `quick_check`, ô quá dài; không kiểm mã chữ của ô, không kiểm byte 18–19 đầu file), `_connect` (`:1217`: lỗi không bận → `_ready = False` → lần sau `_is_healthy` lại «khỏe» → lặp) | <ul><li>**(a)** một ô TEXT của bảng `drafts` (ví dụ `title`) chứa UTF-8 hỏng (ghi bằng `CAST(? AS TEXT)`): `list_drafts` → `OperationalError: Could not decode` → «File nháp bị lỗi…» ở **mọi** lần (probe A: 2/2); `load` nháp đó và trạng thái gửi vẫn đọc được; file không đổi tên. Trang Bài viết trống hẳn, không nháp nào mở được từ danh sách.</li><li>**(b)** byte 18 đầu file («write version») = 3: SQLite mở **chỉ đọc**; đọc được, mọi lần `save` → `SQLITE_READONLY` (mã 8, giữ file đúng ý) nhưng câu báo «bị lỗi… Thử tải lại trang» sai, không bao giờ tự thoát (probe B: 2/2).</li><li>**Mức Thấp:** phải ghi được vào `data/` (lớp «phải chiếm máy trước»); không lộ gì, không mất dữ liệu (nháp, dấu «đã gửi» còn trong file, chỉ không hiện); sửa tay được. Có từ trước T-131 (bản cũ cùng hành vi).</li></ul> | Trong phiếu gom kiểm file 5 kho (Thợ Máy đề xuất): (a) `list_drafts`, `find_plan_draft` đọc ô bằng `text_factory = bytes` rồi giải mã từng dòng, dòng hỏng bỏ qua và đếm (đúng hợp đồng «nháp hỏng thì bỏ qua và báo»); (b) `_is_healthy` coi byte 18 hay 19 > 2 là file lạ (cất sang một bên), như Soi Lỗi GN-1 cho ba kho kia. Test `tests/test_la_chan_t131.py::test_lc_t131_1_hand_edited_draft_file_does_not_stay_stuck` (2 tham số, `xfail(strict=True)`; `--runxfail` hỏng đúng chỗ). Gỡ dấu theo R5 khi sửa |

Không có lỗi Nghiêm trọng, Cao, Trung bình; không lỗi mới do T-131 gây ra.

## Đánh giá lỗi, ghi nhận của Soi Lỗi, Thợ Máy; R5

| Mục | Lá Chắn |
|---|---|
| **SL-T131-1** · Thấp · `plan_cache` gỡ liên kết ở tên nhật ký sau khi mở | Đồng ý Thấp. **Đã đóng** ở `147c9f1` (mục 4); kho nháp làm đúng thứ tự ngay từ đầu |
| Soi Lỗi GN-1 (byte 18 > 2, ba kho lưu tạm) | Đúng; kho nháp cùng kiểu, tôi ghi thành LC-T131-1 (b) vì ở kho nháp nó chặn việc **lưu bài** |
| Soi Lỗi GN-2 (`plan_cache` tạo bảng hai câu, khe lần đầu) | Đồng ý giữ; phiếu gom |
| Soi Lỗi GN-3, Thợ Máy đề xuất `search_cache._KEEP_FILE_CODES` thêm 13 | Đồng ý; phiếu gom |
| Soi Lỗi lượt 2 G1 (trang Bài viết, Kế hoạch tạo `DraftStore` mỗi lần vẽ → `_is_healthy` mỗi lần vẽ) | Có từ trước; ~20 ms kho thực tế; phiếu sau dùng lại một kho như trang Soạn bài. Không bảo mật |
| Soi Lỗi lượt 2 G2 | Mục 8; điều kiện B.2 |
| Thợ Máy «chỗ để ngỏ» 1–6 (lượt 2) | Đồng ý cả: lớp bọc thay vì đổi chữ ký `_connect` (giữ `test_t092_nhap_bi_xoa`), đổi tên thay vì xóa, `BEGIN IMMEDIATE` từ câu đầu, mọi câu đọc chung một ảnh chụp, đọc thử cả ô `data` ở lần kiểm, không đụng `search_cache` |
| Thợ Máy lượt 1 «chỗ để ngỏ» 1–5 | Đồng ý: mã 13 (đầy ổ) giữ file (test T-042); trần 50 triệu bước, 1 MB có đo; `reset_count` giữ hành vi cũ; `plan_cache` tạo bảng cách cũ (GN-2) |
| R5 `tests/test_site_index.py::test_extra_table_does_not_break_cache` → `test_extra_table_drops_the_cache` (kỳ vọng ngược) | **Duyệt**: LC-T129-1 (tôi đặt) đòi so trọn `sqlite_master` như `search_cache`, `plan_cache`; bảng lạ phải là file lạ. Ca mới chặt hơn (`reset_count == 1`, tải lại đúng 1 lần, lần sau đọc cache) |
| R5 `tests/test_soi_loi_t117.py` | Chỉ gỡ dấu `xfail` (2 tham số ở lượt 1, `[kho-nhap]` ở lượt 2), đổi `ids=` thành `pytest.param(id=)` cùng tên; thân test không đổi. Đúng |
| R5 `tests/test_soi_loi_t131.py` | Mục 4. Đúng |

## Thử độc lập (Fable)

Script `probe_t131.py` (thư mục nháp của phiên; `DraftStore` trên thư mục tạm, `PROJECT_ROOT` trỏ vào đó, chờ khóa rút còn 0,3 s; không mạng, không Streamlit).

| Phần | Ca | Kết quả |
|---|---|---|
| A | ô `title` của nháp có UTF-8 hỏng | `list_drafts` lỗi 2/2 lần, file không đổi tên; `load`, `send_state_if_exists` vẫn đọc được → **LC-T131-1 (a)** |
| B | byte 18 đầu file = 3 | `list_drafts` ok; `save` lỗi 2/2 lần «bị lỗi»; file không đổi tên → **LC-T131-1 (b)** |
| C | `ANALYZE` + trigger `AFTER INSERT ON drafts` xóa `send_states` | đổi tên `drafts.hong-20261110-162003.sqlite`; file cất đi còn 1 nháp + «đã gửi 501», trigger không chạy; file mới 3 bảng; `load_send_state` nháp cũ ở kho mới → `None` (G2) |
| D | kết nối khác giữ `BEGIN EXCLUSIVE` lúc mở lần đầu | «File nháp đang bận…», không `.hong-`; nhả khóa → đọc được, dấu «đã gửi 501» còn |
| E | chỗ đặt file là hard link tới file nháp hợp lệ ngoài dự án | đổi tên; file ngoài nguyên từng byte; kho mới là file thường (`st_nlink == 1`) |
| F | `data/<con>` là junction tới thư mục ngoài có file nháp hợp lệ | `list_drafts`, `save` → đúng `MSG_DATA_DIR_LINK`; **0** lần `sqlite3.connect`; thư mục đích nguyên (lần gọi thứ ba của probe dùng mã nháp sai dạng nên bị chặn ở bước kiểm mã, lỗi của probe) |
| — | câu báo của mọi ca | không chứa đường dẫn thư mục tạm |

Ngoài ra: đọc mã đối chiếu từng câu SQL của 11 thao tác với luật `_Checked` (mục 1); grep `drafts.py`: không `unlink` trên chính file nháp, không `pickle`/`eval`, mọi câu SQL tham số `?` (chỉ `_oversized_sql` ghép tên bảng, tên cột **hằng** từ `_COLUMNS`).

## Danh sách kiểm tra (điều kiện của phiếu)

| Mã | Đạt | Bằng chứng |
|---|---|---|
| LC-T129-1 (`site_index` kiểm như `search_cache`) | ✔ | `site_index.py`: `_app_tables` so trọn `sqlite_master` trước khi mở (`_is_healthy`, `_create_tables`) **và** trong cùng giao dịch (`_connect`: `BEGIN`/`BEGIN IMMEDIATE` rồi so với `_expected_schema`, khác → `_Corrupt`; `save` bỏ rồi ghi lại một lần); `_guard`; `_decode_text` cho `sqlite_master`; trigger, bảng lạ, khung nhìn, chỉ mục → bỏ file (7 ca Thợ Máy). Kho nháp rà cùng kiểu (mục 1, 5, 6) |
| SL-T117-1 (`dir_has_link` từ đầu, 3 kho) | ✔ | Mục 3; ca `test_sl_t117_1_other_data_stores_never_write_through_link` 3 tham số qua |
| Mẫu LC-T122-1 (`plan_cache._is_healthy`) | ✔ | `text_factory = _decode_text`, `_Corrupt` → `False`; mọi mã ngoài `_KEEP_FILE_CODES` (gồm «unsupported file format») → `False`; `site_index`, kho nháp cùng mẫu (kho nháp đọc `sqlite_master` thành byte) |
| Lá Chắn T-124 ĐK 4 | ✔ | `plan_cache._is_healthy` (trên); docstring `set_gsc_site_url` ghi rõ nơi gọi phải `parse_property` trước, đường duy nhất `save_property` đúng thứ tự |
| Yêu cầu 1–5 của phiếu | ✔ | 1: `site_index` (trên); 2: mục 3; 3: mẫu LC-T122-1; 4: `drafts.py` làm sau khi gộp `main` có T-130 (`cd575a9`), chỉ phần mở kho, kiểm file, trạng thái gửi không đổi dòng nào (mục 8); 5: test ghim từng phần, Thợ Máy và Soi Lỗi chạy 60–76 file nơi gọi và quét gói, tôi chạy lô liên quan |
| W1 (không mở đường đăng/gửi trùng) | ✔ | Khóa so rồi đặt giữ nguyên (mục 1); G2 chỉ cho gửi thêm **nháp** khi file đã bị chương trình khác sửa |
| W2 (không xóa dữ liệu) | ✔ | Kho nháp không xóa file nào (đổi tên); kho lưu tạm chỉ xóa file cache của app, không xóa khi `data/` là liên kết |
| U1, U2 | ✔ | Câu báo cố định, `strerror` không kèm đường dẫn; tên file cất đi do app đặt, hiện qua `.name` |
| F1, F3 (`docs/team/security.md`) | ✔ | Không đi theo liên kết (gỡ hay đổi tên chính liên kết); file là dữ liệu chưa tin cậy: cấu trúc so trọn, `trusted_schema = OFF`, trần |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 24 file liên quan trên `fcc1d1d` (T-131 ×3; kho nháp, trạng thái gửi, T-086, T-089, T-092, T-130, T-117, T-100; `site_index`, `plan_cache`, `search_cache`, T-122; T-113, T-129 nơi gọi) | **1.154 qua, 5 bỏ qua** (đều ca symlink: Windows chưa bật Developer Mode), 0 xfail, 0 hỏng, 19 phút 34 giây | ✔ |
| Ca mới `tests/test_la_chan_t131.py` | 2 `xfailed` (strict); `--runxfail`: 2 hỏng đúng chỗ (`AssertionError: kho kẹt mãi…`) | ✔ |
| Probe A–F | đúng hướng; 0 câu báo lộ đường dẫn | ✔ |
| `ruff check .`; `ruff format --check` 7 file + file test mới | sạch; `env_file.py` lệch định dạng 4 dòng ở chữ ký `set_gsc_site_url` **có từ trước** (Thợ Máy chỉ sửa docstring), 7 file còn lại đúng khuôn | ✔ |
| bandit 4 file (`PYTHONUTF8=1`) | 3, đều báo nhầm: B105 `env_file.py:70` tên biến `PASSWORD_HASH_VAR` (có từ trước); B101 `drafts.py:968` `assert` thu hẹp kiểu (có từ trước); B608 `drafts.py:1889` `_oversized_sql` chỉ ghép tên bảng, tên cột hằng | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 4 file mã + 3 file test mới + 2 báo cáo; file test của tôi; biên bản này | 2 báo nhầm cùng một chữ: `env_file.py:70` (tên biến, có từ trước) và dòng 266 báo cáo Thợ Máy chép lại; file test mới 0; biên bản này: 0 | ✔ |
| Ký tự ẩn (Cf, Cc, CR), NFC trong 7 file | 0; đều NFC | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `config/` không đổi | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `d4a015e`) không xung đột; từ `7153f0a`, `main` không sửa file nào của phiếu | ✔ |

## Ghi nhận (không xếp lỗi)

1. **Khe giữa lần kiểm liên kết và lần SQLite mở file** (`_prepare` → `sqlite3.connect`): chương trình khác đặt liên kết đúng khe đó thì SQLite đi theo. Cùng lớp «phải chiếm máy trước» đã chấp nhận ở T-117, T-122; lớp kiểm cấu trúc trong giao dịch chặn phần «cấu trúc», không chặn phần «đường dẫn».
2. **`_prepare` chạy ở mỗi lần mở** (6–8 `lstat`): rẻ, đúng ý «kiểm ở mỗi lần mở». Trang Bài viết, Kế hoạch tạo kho mới mỗi lần vẽ nên `_is_healthy` chạy mỗi lần vẽ (Soi Lỗi G1, có từ trước).
3. **`_WRITE_HEADS`** nhận câu ghi theo chữ đầu (`INSERT`, `DELETE`, `UPDATE`, `REPLACE`); thêm loại câu khác (`WITH … DELETE`, `CREATE`) phải thêm vào, như Thợ Máy ghi. Mọi câu hiện là hằng trong `drafts.py`.
4. **Hard link nhận bằng `st_nlink > 1`** (cùng `search_cache`, `site_index`, `plan_cache`): trên ổ báo `st_nlink` lạ, file nháp sẽ bị cất đi mỗi lần mở; `data/` nằm trong thư mục phần mềm (NTFS, APFS) nên không gặp; nếu đổi chỗ `data/` sang ổ mạng thì phải thử lại.
5. **Lược đồ kỳ vọng dựng bằng SQLite đang chạy**: câu `CREATE` trong `sqlite_master` do SQLite ghi lại; file nháp của máy này do chính SQLite của máy tạo, `data/` không chia sẻ giữa hai máy. Đổi phiên bản Python/SQLite mà cách ghi câu đổi thì file bị **đổi tên** (không mất), tên báo ở ba trang; chạy test trên Mac (điều kiện B.3) sẽ cho thêm một bản SQLite khác đối chứng.
6. **`recovered_from.name`** là tên do app đặt (dấu thời gian, số thứ tự), không có chữ ngoài; `write.py:4501` đưa thẳng vào câu Markdown (không qua `escape_markdown`) vẫn an toàn vì chỉ có chữ số, `.`, `-`.
7. Probe F lần gọi thứ ba dùng mã nháp «abc» nên bị `_ID_PATTERN` chặn trước `_connect`: lỗi của probe, không phải kho.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp. Giai đoạn 4: điều kiện 2 của Lá Chắn T-129 (phiếu dọn kho dữ liệu phụ) **đã xong**; LC-T131-1 là lỗi Thấp có từ trước, không chặn đóng Giai đoạn 4.

**B. Cho việc sau** (không chặn T-131):

1. **Phiếu gom kiểm file 5 kho** (Thợ Máy đề xuất, Soi Lỗi đồng ý): sửa **LC-T131-1** (a) và (b) ở kho nháp, gỡ dấu `xfail` theo R5; Soi Lỗi GN-1 (byte 18–19 > 2 là file lạ ở ba kho lưu tạm), GN-2 (`plan_cache` tạo bảng trong một giao dịch có kiểm lại), GN-3 (`search_cache._KEEP_FILE_CODES` thêm 13); gom `_guard`, `_app_tables`, `_is_healthy`, `_is_link`, `_journal_paths` về một module có bảng ca test chung. Lá Chắn kiểm rút gọn.
2. **Phiếu sau (Thấp, giữ khóa gửi trùng khi file bị cất đi, G2):** khi `_move_aside`, chép các dòng `send_states` đọc được qua khuôn `SendState` từ file cất đi (kết nối có `_guard`, chỉ `SELECT`) sang file mới, hay ít nhất câu báo nói rõ «dấu đã gửi nằm trong file cất đi». Lá Chắn kiểm rút gọn.
3. **Khi có máy Mac** (T-063 ĐK 3): chạy `test_t131_kho_du_lieu_phu.py`, `test_t131_kho_nhap.py`, `test_soi_loi_t131.py`, `test_la_chan_t131.py` (ca symlink đang bỏ qua trên Windows).
4. **Chữ (phiếu chữ sau):** câu «File nháp cũ bị hỏng nên đã được cất sang một bên…» ở ba trang nói thêm trường hợp «là lối tắt» (Thợ Máy đề xuất); `_db_message` khi `SQLITE_READONLY` nên nói «file chỉ đọc» thay vì «bị lỗi» (gộp với LC-T131-1 b).

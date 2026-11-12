# Biên bản bảo mật T-136 · Gom kiểm file 5 kho SQLite, LC-T131-1, câu báo kho nháp · rút gọn

> **Model:** **Claude Opus 5.5**. Hạn mức tuần của Fable đã hết; Chỉ Huy B giao lượt này chạy Opus 5.5 (12/11). Biên bản này **không** phải lượt kiểm bằng Fable.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Opus 5.5** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-136](../tickets/T-136-gom-kiem-file-5-kho.md) (điều kiện B.1, B.2, B.4 và LC-T131-1 của Lá Chắn T-131; Soi Lỗi T-131 GN-1 → GN-3). Nhánh `team/T-136` từ `main` `71322c4`: Thợ Máy `c48aedd` (mã, test), `81a3016` (báo cáo); Soi Lỗi rút gọn `52edfa1` (ĐẠT, 0 lỗi mới, G1–G3). Đầu nhánh **`52edfa1`**, đã push |
| Phạm vi | **Rút gọn**, theo 5 trọng tâm Chỉ Huy giao: diff `71322c4..52edfa1` (`seo_app/storage/sqlite_file.py` mới; lớp mỏng ở `drafts.py`, `image_tags.py`, `site_index.py`, `plan_cache.py`, `search_cache.py`; câu báo ở `home.py`, `plan.py`, `write.py`; R5 `tests/test_la_chan_t131.py`), đọc cùng `data_dir.is_link` / `folders._is_link_stat` và `_prepare` của 5 kho. **Không nâng lên đầy đủ:** phiếu không đổi dòng nào của logic trạng thái gửi (đọc, ghi, so rồi đặt, dọn dòng mồ côi); B.2 làm bằng câu báo. Không chạm website, Google; không chạy cloud |
| Ngày | 2026-11-12 (giao ≈ 13:55, xong 14:22, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, SQLite 3.53.1, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; lô test chạy nền. Máy chưa bật Developer Mode, không có `os.mkfifo` |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được** (`main` `01fc45c`: `git merge-tree` không xung đột; từ `71322c4` `main` chỉ đổi tài liệu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (LC-T136-1, chỉ Mac/Linux: bước đọc đầu file mới mở thẳng đường dẫn, gặp FIFO thì treo; test `xfail(strict=True)`). Bốn trọng tâm còn lại **đạt**: module chung không nới phòng thủ nào đã qua Lá Chắn; kho thẻ ảnh đổi định nghĩa liên kết **chặt hơn**, không hở, không bắt nhầm file đám mây; dấu ô chữ hỏng không lọt ra ngoài kho; ngưỡng byte 18–19 đúng chuẩn SQLite; câu báo không lộ đường dẫn, có thoát Markdown; R5 chỉ gỡ dấu `xfail`. LC-T131-1 (a), (b) **đóng** |

## Tóm tắt (cho chủ dự án)

Phiếu này gom phần «kiểm file» của 5 kho dữ liệu trong máy về một chỗ và sửa lỗi nhỏ tôi tìm ra ở T-131. **Gộp được.**

- **Phòng thủ không bị nới:** lối tắt, file phụ đi kèm, giới hạn chống file độc, cách cất file nháp lạ sang một bên (không xóa) đều giữ như trước ở cả 5 kho. Kho thẻ ảnh còn nhận ra thêm vài kiểu lối tắt hiếm trên Windows; file của OneDrive, Google Drive vẫn không bị coi là lối tắt.
- **Lỗi T-131 đã sửa đúng:** một nháp bị hỏng mã chữ nay chỉ vắng khỏi danh sách (các nháp khác vẫn hiện, khóa chống gửi trùng của nháp đó vẫn còn); file ghi «phiên bản» lạ được cất sang một bên rồi dùng file mới, không kẹt mãi.
- **Câu báo mới** (file nháp bị cất đi, file chỉ đọc) nói rõ hơn, không in đường dẫn trong máy.
- **Một lỗi nhỏ mới, chỉ trên Mac/Linux (LC-T136-1):** nếu một chương trình lạ đã vào được máy và đặt một loại «ống dẫn» đặc biệt vào chỗ file lưu tạm, trang Kế hoạch hay Theo dõi sẽ đứng mãi. Máy Windows không bị. Sửa vài dòng, nên làm trước khi dùng app trên Mac.
- **Việc của anh/chị lúc này:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Module chung `sqlite_file.py` không nới lỏng phòng thủ đã qua Lá Chắn — **đạt, trừ LC-T136-1 (mới)**

Đọc từng lớp mỏng, đối chiếu với bản đã qua Lá Chắn (T-122, T-124, T-131):

| Lớp phòng thủ | Trước T-136 | Sau T-136 | Đánh giá |
|---|---|---|---|
| `data/` là liên kết | `dir_has_link` đầu `_prepare` mỗi kho | Không đổi (không nằm trong module chung) | Giữ |
| Chính file, file nhật ký là liên kết | `_is_link` riêng mỗi kho (symlink, junction, reparse point trỏ đi chỗ khác, hard link), gỡ **trước** mọi lần SQLite mở | `sqlite_file.is_link` (`:66`), `remove_link` (`:79`) cùng định nghĩa; thứ tự trong `_prepare` các kho không đổi | Giữ; kho thẻ ảnh chặt hơn (mục 2) |
| `trusted_schema = OFF`, trần số bước, trần độ dài | `_guard` riêng | `sqlite_file.guard` (`:90`), mỗi kho truyền đúng hằng của mình lúc gọi | Giữ (test hạ trần vẫn có tác dụng, ca `test_lowered_step_limit_still_stops_queries` 5 kho) |
| So trọn `sqlite_master`, đọc danh sách có `LIMIT`, dòng lặp là «khác» | `_app_tables` riêng | `app_rows` (3 kho lưu tạm), `app_table_names` (nháp, thẻ ảnh), cùng `_master_rows` | Giữ; trần dựng mẫu trong bộ nhớ 64 dòng thay 16/32 không đổi kết quả |
| UTF-8 hỏng trong `sqlite_master` là file lạ (LC-T122-1) | `_decode_text` → `_Corrupt` | `strict_text` → `_Undecodable` → `False` (3 kho lưu tạm); nháp, thẻ ảnh đọc byte | Giữ |
| Lỗi môi trường giữ file | 3 bộ mã riêng (`search_cache` thiếu 13) | `KEEP_FILE_CODES` chung có 13 (GN-3) | Chặt hơn (đầy ổ không xóa file) |
| Tạo bảng trong một giao dịch ghi có kiểm lại | `site_index`, `search_cache`; `plan_cache` tạo từng câu | `create_tables` chung, cả `plan_cache` (GN-2) | Chặt hơn; `_Corrupt` từ `_prepare` của `plan_cache` được `load`, `save` bắt như cũ |
| File lạ: kho nháp, kho thẻ ảnh **đổi tên**, 3 kho lưu tạm xóa | `_move_aside` / `_reset` | Không đổi | Giữ |
| Đầu file byte 18–19 > 2 | Không kiểm (kẹt mãi) | `newer_file_format` (`:189`) trong `is_healthy` 4 kho và `_is_healthy` kho thẻ | Mới, đúng (mục 3), **nhưng** mở file bằng `open()` trước khi biết là file thường: **LC-T136-1** |

Grep `sqlite_file.py`: không `pickle`, `eval`, không ghép chữ vào SQL (chỉ `MASTER_SQL` hằng, tham số `?`); không nhập gì từ `seo_app.storage`. Bandit B610 ở `:257` là báo nhầm (tham số tên `extra`, không phải Django).

### 2. Kho thẻ ảnh đổi định nghĩa liên kết sang `data_dir.is_link` — **đạt: không hở, không bắt nhầm file đám mây**

- **Cũ** (`image_tags._is_link` trước T-136): `is_symlink() or is_junction()` hay hard link. **Mới**: `folders._is_link_stat` (symlink, hay reparse point có **bit name-surrogate** `0x20000000`) hay hard link. Junction (`0xA0000003`) và symlink Windows (`0xA000000C`) có bit đó, nên mọi thứ bản cũ coi là liên kết bản mới vẫn coi là liên kết: **không có kẽ hở**. Thêm: các reparse point name-surrogate khác (ví dụ liên kết WSL `0xA000001D`), như 4 kho kia đã làm từ T-131.
- **File đám mây** OneDrive Files On-Demand dùng nhóm thẻ `0x9000xx1A` (không có bit `0x20000000`); Google Drive for Desktop dùng ổ ảo hay file thường: **không** bị coi là liên kết, như trước. Thử thật trên máy này (probe D): file thường, hard link, thư mục, đường không có, junction thật, reparse point **không** name-surrogate có thật (`AppExecLink` `0x8000001B` trong `WindowsApps`): bản cũ và bản mới cho **cùng** kết quả ở cả 6 ca. Thư mục OneDrive của máy (742 mục đầu) không có file giữ chỗ nên không thử trực tiếp được; kết luận dựa trên thẻ, cùng loại với ca `AppExecLink`.
- Kho thẻ ảnh vẫn có `is_file()` trước bước kiểm file (`image_tags.py:458`) nên không dính LC-T136-1.

### 3. LC-T131-1 — **đóng**

**(a) Dấu ô chữ hỏng không lọt ra giao diện hay WordPress.** `_Checked.keep_bad_text()` (`drafts.py:1784`) chỉ được gọi trong ba thao tác liệt kê (`list_drafts`, `find_plan_draft`, `list_plan_writes`), trên kết nối riêng của thao tác đó (đóng khi xong); `_app_tables` vẫn đọc `sqlite_master` thành byte rồi trả lại bộ giải mã. Dấu `_BAD_TEXT` là một `object()` không phải chữ:

- `list_drafts` bỏ dòng có dấu (đếm `skipped`) **trước** khi dựng `DraftSummary`;
- `find_plan_draft` đưa mã sang `load` → `_check_id` từ chối vì không phải chữ → bỏ qua;
- `list_plan_writes` kiểm `isinstance(…, str)` cho mã, `_read_plan_write` ném `TypeError` → `DraftError` cho ô dữ liệu → bỏ qua.

Không đường nào khác đặt bộ giải mã này; `load`, trạng thái gửi, bước gửi WordPress đọc qua kết nối thường (`DraftSnapshot` dựng từ ô `data`). Probe B: ô tiêu đề hỏng + một dòng mã hỏng + hai dòng `plan_writes` hỏng → `list_drafts` 1 nháp, `skipped = 2`, mọi giá trị trong `DraftSummary` là `str`; `find_plan_draft` trả `None`; `list_plan_writes` trả `[]`; khóa gửi của nháp hỏng tiêu đề vẫn «đã gửi 501»; không file nào bị đổi tên.

**(b) Ngưỡng byte 18–19.** Chuẩn định dạng SQLite: byte 18 (phiên bản ghi) và 19 (phiên bản đọc) là 1 (nhật ký thường) hay 2 (WAL); lớn hơn 2 thì SQLite chỉ đọc (byte 18) hay không đọc được (byte 19). App không bao giờ ghi giá trị khác. Probe A: giá trị 0, 1, 2 → không phải file lạ; 3, 255 → file lạ (cả hai byte); file WAL thật `[2, 2]` → không phải file lạ; file 19 byte, file trống → để SQLite xét. Ca `[utf8-hong-trong-o]`, `[byte-18-la-3]` của tôi (gỡ dấu) qua.

### 4. Câu báo `MSG_RECOVERED`, `_MSG_READONLY` — **đạt**

- `MSG_RECOVERED` (`drafts.py:183`) có đúng một chỗ chèn `{name}`; tên là tên app tự đặt (`drafts.hong-YYYYmmdd-HHMMSS[-n].sqlite`), chỉ `.name`, không đường dẫn. Cả ba trang đưa tên qua `escape_markdown` (`home.py:63`, `plan.py:163`, `write.py:4500`: trang Soạn bài trước đây **chưa** thoát, nay thoát: tốt hơn). Câu nói thêm trường hợp lối tắt và nhắc xem WordPress trước khi gửi lại (B.2, B.4).
- `_MSG_READONLY` (`:177`) là hằng, chỉ trả khi mã lỗi đúng 8 (`_db_message`, `:1907`). Probe C: file nháp thật đặt chỉ đọc → đúng câu này, không đường dẫn.
- Thoát Markdown làm tên hiện có dấu `\` trong mã nguồn nhưng Streamlit hiện đúng tên (như trang Bài viết, Kế hoạch từ T-131).

### 5. R5 — **đạt**

`git diff 71322c4..52edfa1 -- tests/test_la_chan_t131.py`: chỉ xóa khối `@pytest.mark.xfail(strict=True, …)` 7 dòng; thân test, tham số, `ids` giữ nguyên. Không ca cũ nào khác đổi (diff test chỉ thêm `test_t136_kiem_file_chung.py`, `test_soi_loi_t136.py`).

## Lỗi phát hiện

| Mã | Mức | Mô tả | Ở đâu | Đầu vào · hậu quả | Sửa |
|---|---|---|---|---|---|
| **LC-T136-1** | **Thấp** (chỉ Mac/Linux) | Bước đọc đầu file mới `newer_file_format` mở thẳng đường dẫn bằng `path.open("rb")` (đọc, **có chờ**) trước khi biết đó là file thường. Ba kho lưu tạm gọi `_is_healthy` ở **mỗi** lần mở mà không kiểm «file thường» trước | `sqlite_file.py:189-197` (`:193` `open`); nơi gọi `site_index.py:358`, `plan_cache.py:263`, `search_cache.py:561` (`exists()` rồi `_is_healthy`). Kho nháp (`drafts.py:1292-1299`), kho thẻ ảnh (`image_tags.py:458`) có `is_file()` trước nên không bị | <ul><li>**Đầu vào:** chương trình lạ ghi được vào `data/` (cùng lớp «phải chiếm máy trước» T-117, T-122, T-131) thay `data/site_index.sqlite` (hay `plan_cache`, `search_cache`) bằng một **FIFO** (`mkfifo`).</li><li>**Hậu quả:** trên Mac/Linux, `open()` chế độ đọc của FIFO chờ đầu ghi **mãi**; trang dùng kho đó (Kế hoạch, Soạn bài bước SEO, Theo dõi; với `search_cache`, lần lấy số liệu còn giữ `_FETCH_LOCK` nên mọi tab khác chỉ thấy «đang bận») đứng mãi, mỗi lần tải lại thêm một luồng treo. Không lộ, không mất dữ liệu.</li><li>**Trước T-136:** bước đầu tiên chạm file là `sqlite3.connect`; SQLite mở đọc-ghi (không chờ trên FIFO theo hành vi Linux, macOS) và đọc bằng `pread`/`lseek` (lỗi «illegal seek» ngay) nên chỉ báo lỗi. Đây là **lùi** do phiếu (đọc mã và hành vi POSIX đã biết; máy này không tạo được FIFO).</li><li>**Cùng gốc:** chỗ đặt file là **thư mục** thì `open()` ném lỗi quyền, câu báo đổi (Soi Lỗi G1; probe A, E lặp lại được).</li></ul> | Trong `newer_file_format`: chỉ đọc khi là **file thường**: `os.lstat` → không `S_ISREG` thì trả `False`; mở bằng `os.open` có `O_NONBLOCK` (Mac/Linux) rồi `os.fstat` kiểm lại `S_ISREG` trước khi đọc 20 byte; không phải file thường thì `False` để SQLite và kho xét như trước T-136. Sửa luôn được G1. Test `tests/test_la_chan_t136.py` (2 ca `xfail(strict=True)`: `…skips_a_folder` chạy được trên Windows, `--runxfail` hỏng đúng chỗ `PermissionError`; `…never_waits_on_a_fifo` chỉ chạy trên Mac/Linux, có luồng phụ và tự gỡ treo sau 3 giây). Gỡ dấu theo R5 khi sửa |

Không có lỗi Nghiêm trọng, Cao, Trung bình.

## Đánh giá ghi nhận của Soi Lỗi; R5

| Mục | Lá Chắn |
|---|---|
| Soi Lỗi kết luận ĐẠT, 71 ca so bản cũ/mới (62 y hệt, 6 khác đúng phiếu, 3 khác câu báo) | Đồng ý; 3 ca khác câu báo (G1) cùng gốc với LC-T136-1 |
| **G1** chỗ đặt file lưu tạm là thư mục: câu báo «Permission denied» sai nguyên nhân | Đồng ý; nâng phần **FIFO** cùng gốc thành LC-T136-1 (Thấp, Mac/Linux) vì là treo, không chỉ là câu chữ. Sửa chung một chỗ |
| **G2** «bài trùng vẫn chỉ là nháp» chỉ đúng khi công tắc Hẹn giờ/Đăng ngay tắt | Đồng ý. Không đổi kết luận: cất file nháp chỉ xảy ra khi chương trình khác sửa file; câu `MSG_RECOVERED` nhắc xem WordPress; khi bật công tắc, màn hình xác nhận (T-102, T-112) vẫn là chốt chặn. Ghi vào kịch bản buổi thử thật Hẹn giờ/Đăng ngay (T-128) một bước: cất file nháp rồi thử gửi lại |
| **G3** ca symlink chưa chạy trên Windows | Đồng ý; cộng 1 ca FIFO của tôi (điều kiện B.2) |
| Thợ Máy «chỗ để ngỏ» 1–6 | Đồng ý cả: lớp mỏng giữ tên cũ (test vá được); kho thẻ ảnh giữ `_is_healthy` riêng; B.2 bằng câu báo (không đọc thêm gì từ file lạ: đúng hướng phòng thủ, và không đụng logic trạng thái gửi); chỉ bỏ dòng hỏng, không cất cả file; ngưỡng «lớn hơn 2»; `_MSG_READONLY` chỉ cho kho nháp |
| R5 `tests/test_la_chan_t131.py` | Mục 5. Đúng |

## Thử độc lập (Opus 5.5)

Script `probe_t136.py` (thư mục nháp của phiên; file tạm, không mạng, không Streamlit) và ca test tạm thành file test chính thức `tests/test_la_chan_t136.py`.

| Phần | Ca | Kết quả |
|---|---|---|
| A ngưỡng | byte 18, 19 lần lượt 0, 1, 2, 3, 255; file WAL thật; file 19 byte; file trống; thư mục | 0–2 không lạ, 3 và 255 lạ; WAL `[2, 2]` không lạ; file ngắn, trống để SQLite xét; thư mục **ném `PermissionError`** (G1, LC-T136-1) |
| B dấu ô chữ hỏng | ô tiêu đề hỏng, một dòng mã hỏng, hai dòng `plan_writes` hỏng | `list_drafts` 1 nháp + `skipped = 2`, giá trị đều `str`; `find_plan_draft` → `None`; `list_plan_writes` → `[]`; khóa «đã gửi 501» còn; không đổi tên file |
| C câu báo | `MSG_RECOVERED` với tên app đặt; file nháp chỉ đọc thật | 1 chỗ chèn, thoát Markdown, không đường dẫn; câu «chỉ đọc» đúng, không đường dẫn |
| D liên kết | 6 ca (file thường, hard link, thư mục, không có, junction, `AppExecLink`) | Định nghĩa cũ của kho thẻ ảnh và định nghĩa chung cho cùng kết quả ở cả 6 ca |
| E G1 | thư mục ở chỗ `site_index.sqlite` | «Không tạo được file lưu tạm danh sách bài (Permission denied).», thư mục còn nguyên |
| Test LC-T136-1 | `tests/test_la_chan_t136.py` | 1 `xfailed` (thư mục), 1 bỏ qua (FIFO: máy không có `os.mkfifo`); `--runxfail`: hỏng đúng `PermissionError` |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 35 file liên quan trên `52edfa1` + file test mới (T-136 ×2, T-131 ×4, T-117 ×2, T-116 nhóm 1, `site_index` ×6, `plan_cache`, `search_cache`, T-122, thẻ ảnh ×4, kho nháp ×4, trạng thái gửi T-086, T-089, T-092, T-130, T-100) | **2.874 qua, 7 bỏ qua** (đều ca symlink: Windows chưa bật Developer Mode), **7 xfail có từ trước** (SL-T070-4, kho thẻ ảnh), **0 hỏng**, 19 phút 6 giây | ✔ |
| `ruff check .`; `ruff format --check` 11 file | sạch; đúng khuôn | ✔ |
| bandit 6 file `seo_app/storage` (`PYTHONUTF8=1`) | 4, đều báo nhầm: B610 `sqlite_file.py:257` (tham số tên `extra`); B608 `drafts.py:1870`, `image_tags.py:129` (ghép tên bảng, tên cột hằng, có từ T-131, T-074); B101 `drafts.py:980` (`assert` có từ trước) | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 10 file mã, test + 2 báo cáo + file test mới; biên bản này | 0; biên bản: 0 | ✔ |
| Ký tự ẩn, CR, NFC trong 10 file | 0; đều NFC | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `config/` không đổi | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `01fc45c`) không xung đột | ✔ |

## Ghi nhận (không xếp lỗi)

1. `newer_file_format` mở file bằng Python trước SQLite: trên Windows, `open()` mặc định cho chia sẻ đọc-ghi, khóa của SQLite nằm ở vùng byte xa đầu file nên không xung đột; đóng ngay sau 20 byte.
2. Kho thẻ ảnh nay gỡ thêm vài kiểu reparse point name-surrogate hiếm ở chỗ đặt file (chặt hơn, đúng ý F1).
3. Ô `data` của một nháp bị hỏng mã chữ vẫn báo «File nháp bị lỗi» khi mở đúng nháp đó (Thợ Máy chỗ để ngỏ 4): theo nháp, không kẹt cả kho; khóa gửi của nháp đó vẫn đọc được.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được.** Máy Windows không bị LC-T136-1; Chỉ Huy chạy toàn bộ test khi gộp.

**B. Cho việc sau:**

1. **Sửa LC-T136-1 trước khi dùng app trên Mac/Linux** (nên làm ngay ở một lượt nhỏ của T-136 hay phiếu dọn: vài dòng ở `newer_file_format`, sửa luôn Soi Lỗi G1); gỡ 2 dấu `xfail` của `tests/test_la_chan_t136.py` theo R5. Lá Chắn kiểm rút gọn.
2. **Khi có máy Mac** (T-063 ĐK 3, Lá Chắn T-131 B.3): chạy thêm `tests/test_la_chan_t136.py` (ca FIFO) cùng các ca symlink T-131, T-136.
3. **Kịch bản buổi thử thật Hẹn giờ/Đăng ngay (T-128):** thêm một bước theo Soi Lỗi G2: file nháp bị cất sang một bên rồi thử gửi lại một bài đã gửi, xác nhận màn hình xác nhận và câu `MSG_RECOVERED` đủ để người dùng không gửi trùng.

## Lượt 2 · LC-T136-1, Soi Lỗi G1; xét SL-T136-1, G4; đọc soát ca R (2026-11-12)

> **Model:** **Claude Opus 5.5** (hạn mức tuần Fable vẫn hết; Chỉ Huy B giao). Không phải lượt kiểm bằng Fable.

| Mục | Nội dung |
|---|---|
| Được kiểm | Thợ Máy lượt 2: `348f6f3` (mã, test), `47fe6af` (báo cáo, mục «Lượt 2»). Soi Lỗi thử cục bộ G2 (không commit), Chỉ Huy B chép tóm tắt và ca R nguyên văn cho Lá Chắn đọc |
| Phạm vi | Rút gọn: diff `2e43ebb..47fe6af` (`sqlite_file.newer_file_format`, `_OPEN_FLAGS`; 9 ca mới ở `test_t136_kiem_file_chung.py`; R5 ở `test_la_chan_t136.py`); xét mức SL-T136-1 và G4 của Soi Lỗi; đọc soát ca R cho kịch bản T-128. Không sửa mã; không chạm website, Google; không chạm thư mục app chủ dự án đang chạy |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN, gộp `main` được ngay** (`main` `01fc45c`: `git merge-tree` không xung đột). **LC-T136-1 đóng, Soi Lỗi G1 đóng**; không nới lớp nào; R5 đúng; trên Windows chỉ đổi câu báo G1 về như trước T-136. **SL-T136-1: Thấp** (đồng ý Soi Lỗi), không do T-136 tạo ra, **không chặn gộp T-136**, **không chặn cứng** việc bật công tắc; **khuyến nghị sửa ở phiếu riêng trước khi bật công tắc Hẹn giờ/Đăng ngay cho bài thật** (như Lá Chắn T-092 B.1 → T-130), Lá Chắn kiểm **đầy đủ**. **G4: câu chữ**, gộp vào phiếu đó. **Ca R: sửa 6 chỗ** (bản cuối ở thư mục ghi chú chung) |

### Tóm tắt (cho chủ dự án)

- **Lỗi nhỏ trên Mac/Linux ở lượt trước đã sửa đúng:** chỗ đặt file lưu tạm mà không phải file thường thì app không còn đứng; câu báo trở về như cũ. Máy Windows không đổi gì khác.
- **Soi Lỗi tìm ra một đường có thể gửi trùng (SL-T136-1):** khi file nháp bị chương trình khác làm hỏng và app cất nó sang một bên, app chỉ nhắc một lần; sau đó trang Bài viết nói «Chưa có bài nào…» và lúc gửi lại không nhắc gì. Hiếm (phải có thứ làm hỏng file nháp trước). Hậu quả: một bài trùng trên website (bài nháp nếu chưa bật Hẹn giờ/Đăng ngay). Tôi xếp mức Thấp, đề nghị sửa ở một phiếu nhỏ **trước khi anh/chị bật Hẹn giờ/Đăng ngay cho bài thật**.
- **Bài kiểm tay «ca R»** cho buổi thử thật: tôi sửa để lệnh chép dự phòng không bao giờ ghi đè bản sao file nháp của anh/chị, và cả ca không bật Hẹn giờ/Đăng ngay.
- **Việc của anh/chị lúc này:** không có.

### 1. LC-T136-1, Soi Lỗi G1 — **đóng**

- `newer_file_format` (`sqlite_file.py:198-226`) nay: `os.lstat` không phải file thường → `False` (không mở); mở bằng `os.open` với `_OPEN_FLAGS` = `O_RDONLY` + `O_NONBLOCK` + `O_NOFOLLOW` + `O_BINARY` (cờ hệ điều hành không có là 0); `os.fstat` trên chính fd không phải file thường → `False`, không đọc; đọc 20 byte; fd luôn đóng (`finally`); mọi `OSError` → `False`.
  - **FIFO** (Mac/Linux): bị loại ở `lstat`, không mở. Đổi thành FIFO đúng khe `lstat` → `open`: mở không chờ (`O_NONBLOCK`), bị loại ở `fstat`.
  - **Liên kết** đặt vào đúng khe đó: Mac/Linux `O_NOFOLLOW` từ chối; Windows không có cờ này, nên có thể đọc 20 byte của file đích chỉ để tính một giá trị đúng/sai (không ghi, không hiện): vô hại, cùng loại khe `stamp()` đã ghi nhận ở T-125. Lớp gỡ liên kết của từng kho vẫn chạy trước như cũ.
  - **«Không phải file thường hay đọc lỗi thì `False`»** không nới gì: kho vẫn tự gỡ liên kết, nhật ký trước; SQLite mở tiếp và báo như trước T-136 (thư mục: «Không mở được…»; FIFO: lỗi vào ra, không chờ, vì SQLite mở đọc-ghi và đọc bằng `pread`/`lseek`). Đầu file đọc lỗi nhất thời mà byte 18 thật sự lớn hơn 2: lần đó kho giữ file, lần kiểm sau bắt.
- Probe A, E chạy lại: thư mục → `False`; `site_index` với thư mục ở chỗ file → «Không mở được file lưu tạm danh sách bài (có thể chương trình khác đang giữ file, hoặc không có quyền ghi)…», thư mục còn nguyên.
- 9 ca mới của Thợ Máy (lớp `FakeOs` giả `lstat`/`fstat` vì Windows không tạo được FIFO): FIFO và thư mục không mở; đổi giữa chừng mở 1 lần, không đọc; fd mở là được đóng; cờ mở đúng; lỗi quyền → `False`; 3 kho lưu tạm giữ thư mục và câu cũ. Đọc từng ca: đúng hành vi cần ghim.
- **R5:** `git diff 2e43ebb..348f6f3 -- tests/test_la_chan_t136.py` chỉ xóa hằng `LC_T136_1` và hai dòng `@LC_T136_1`; thân test không đổi. Ca thư mục qua trên Windows; ca FIFO vẫn bỏ qua trên Windows và phải chạy trên Mac (B.2).
- Lượt 2 chỉ đổi `sqlite_file.py` và test; lớp mỏng của 5 kho, kho nháp, trạng thái gửi không đổi dòng nào.

### 2. SL-T136-1 — **Thấp**; không chặn gộp T-136; khuyến nghị sửa ở phiếu riêng trước khi bật công tắc cho bài thật

**Tôi sửa lại đánh giá G2 ở lượt 1.** Tôi đã viết «khi bật công tắc, màn hình xác nhận (T-102, T-112) vẫn là chốt chặn». Không đúng: khung «Xem lại trước khi gửi» chỉ bắt đọc lại bài, không biết bài đã có trên website. Chốt chống gửi trùng duy nhất là dấu «đã gửi» trong kho nháp (T-086, T-089, T-130), và dấu đó đi theo file bị cất.

**Cơ chế đúng như Soi Lỗi tả** (đọc mã, probe):

- Kho dùng chung của trang Soạn bài gặp byte 18 = 3: lần lưu đầu báo «chỉ đọc» (G4), lần sau cất file; từ đó `send_state_if_exists` của bài trong kho mới là `None` (probe G4).
- `home.py:62-63` chỉ hiện `MSG_RECOVERED` khi chính kho của lần vẽ đó vừa cất file; `home.py:299` ghi «Chưa có bài nào phần mềm đã gửi lên WordPress.» khi kho mới trống.
- Hai đường gửi trùng của Soi Lỗi đúng: tab mở bài trước lần gửi ở tab khác (T-092 chỉ giữ điều tab biết); F5, tab mới, mở lại app.

**Mức Thấp**, vì:

- **Điều kiện hiếm:** file nháp phải bị cất (chương trình khác sửa hay làm hỏng file, ổ lỗi, lối tắt); dữ liệu `data/` nằm trong thư mục phần mềm trên ổ máy, không đồng bộ đám mây. Sau đó người dùng phải chủ động gửi lại: đường 1 cần bấm «Lưu lại», chọn hình thức, tick xác nhận; đường 2 cần viết lại bài.
- **Hậu quả có giới hạn:** công tắc tắt (mặc định) thì chỉ ra một bài **nháp** trùng (không công khai, xóa được). Công tắc bật thì là một bài hẹn giờ hay đăng trùng, công khai tới khi người dùng xóa. Không lộ dữ liệu; W1 vẫn giữ (đăng vẫn phải bấm xác nhận).
- **Không do T-136 tạo ra:** cùng lớp G2 tôi ghi ở T-131; T-136 thêm một nguyên nhân cất file (byte 18–19, theo LC-T131-1 b của tôi) và câu báo tốt hơn.

**Có chặn bật công tắc không:** **không chặn cứng.** Theo cách đã làm với khoảng hở cùng loại ở Lá Chắn T-092 (B.1, khuyến nghị trước khi bật công tắc; đã làm ở T-130): **khuyến nghị sửa trước khi bật công tắc Hẹn giờ/Đăng ngay cho bài thật**; Chỉ Huy và chủ dự án quyết. Nếu bật trước khi sửa: ghi một dòng sổ rủi ro, và README nhắc «thấy câu "File nháp cũ bị hỏng…" thì xem WordPress trước khi gửi bất kỳ bài nào». Không chặn buổi thử thật với bài thử có người theo dõi.

**Sửa ở đâu:** **phiếu riêng**, không phải T-136 lượt 3. Chỗ sửa ở giao diện ba trang và cổng của nút gửi (đụng logic khóa gửi trùng), nên **Lá Chắn đầy đủ**; T-136 (gom kiểm file) gộp được ngay.

**Hướng sửa:** đồng ý hướng của Soi Lỗi, kèm yêu cầu bảo mật:

1. **Dấu hiệu sống qua lần mở lại app.** Biến trong bộ nhớ mất khi tắt app, không phủ đường 2. Xét theo **tên file** `drafts.hong-*.sqlite` trong `data/`: sau `dir_has_link`, chỉ liệt kê tên, khớp đúng khuôn tên app tự đặt (`drafts.hong-YYYYmmdd-HHMMSS[-n].sqlite`).
2. **Không mở, không đọc file đã cất:** không SQLite, không chép dòng `send_states`. Không hiện đường dẫn đầy đủ; tên qua `escape_markdown`.
3. **Lời nhắc thường trực khi còn file đã cất:** trang Bài viết thay «Chưa có bài nào…» bằng lời nhắc (không chỉ một lần). Bước Xuất bản của bài **chưa có** dấu «đã gửi» trong kho hiện tại, ở **mọi** hình thức (cả Nháp), đòi tick «Tôi đã xem trên WordPress: bài này chưa có» trước khi nút gửi bật. Tick không có sẵn, không nhớ sang bài khác.
4. **Chỉ thêm cổng:** không nới so rồi đặt (T-089), không đổi T-092, T-130. Lời nhắc hết khi người dùng xóa hay dời file đã cất; câu nhắc nói rõ chỉ xóa sau khi đã đối chiếu WordPress.
5. **Nên thêm:** bài gắn dòng kế hoạch mà Sheet đã có «Mã bài WordPress» (đã qua `PlanRow`) thì bước Xuất bản nhắc mã đó.
6. **Test:** hai đường của Soi Lỗi (`xfail(strict=True)` trước khi sửa); ca mở lại app (đường 2 sau khi tắt app); ca tên lạ trong `data/` không được tính.

### 3. G4 — **câu chữ**; gộp vào phiếu sửa SL-T136-1

Probe G4: kho dùng chung đã mở, byte 18 đổi thành 3. Lần lưu đầu báo `_MSG_READONLY` («File nháp đang ở chế độ chỉ đọc… Bỏ chế độ chỉ đọc rồi thử lại.»); lần sau cất file.

- **Không có hệ quả bảo mật:** sai nguyên nhân một lần; lần đọc vẫn qua kiểm cấu trúc trong giao dịch; file được cất ở thao tác kế.
- **Gợi ý sửa:** `_db_message` hay `_connect` của kho nháp gặp mã 8 mà `sqlite_file.newer_file_format(self.path)` đúng thì coi là file lạ (`_MSG_BROKEN`, `_ready = False`).
- Không chặn gộp T-136.

### 4. Ca R (kịch bản T-128) — **sửa 6 chỗ**

Bản cuối: `T-136-la-chan-ca-R-ban-cuoi.md` trong thư mục ghi chú chung của nhóm phiên Chỉ Huy B (Chỉ Huy chép vào kịch bản T-128).

1. **Bước 1 không ghi đè bản sao cũ.** `Copy-Item` ghi đè im lặng (đã thử PowerShell 5.1 trên máy này). Chạy lại ca sau một lần dở sẽ chép file nháp mới đè lên bản sao tốt duy nhất, rồi bước dọn xóa nốt file đã cất. Lệnh mới dừng khi còn bản sao hay file `sau-ca-R` của lần trước.
2. **Bỏ bật công tắc và bước Hẹn giờ.** Soi Lỗi đã thử bằng WordPress giả; trên website thật bước đó chỉ còn rủi ro bấm nhầm «Tạo thêm…» ra bài hẹn giờ thật.
3. **Không soạn bài thật** từ bước 3 tới hết ca (nháp tạo lúc đó bị xóa ở bước dọn).
4. **Ảnh chụp chỉ giữ trong máy.**
5. **Nên chạy sau phiếu sửa SL-T136-1**; kỳ vọng ghi hai kiểu (hiện tại, đã sửa).
6. **Đánh lại số bước** (8 bước), sửa dòng bảng mục 7, mục 6, mục 2.

Ba lệnh (bước 1, 3, 8) chạy thử trên một thư mục `data` giả trong thư mục nháp của tôi (không chạm thư mục dự án):

| Lệnh | Kết quả |
|---|---|
| Bước 1 | Tạo bản sao (`True`); chạy lại → `DUNG`; còn file `-journal` → `DUNG` |
| Bước 3 | Sửa byte 18 `1 -> 3`; chạy lại → `DUNG` |
| Bước 8 | Trả đúng file (`True`); chạy lại → báo lỗi, không đổi gì |

Ca R an toàn cho máy chủ dự án: không gửi gì lên website, không gọi mạng, không đọc `.env`, không in đường dẫn khi chạy đúng (câu lỗi có thể in đường dẫn: kịch bản dặn không chép). Ca chỉ đổi 1 byte của file nháp đã có bản sao, và trả lại file ở bước cuối.

### 5. Thử, công cụ quét (lượt 2)

| Việc | Kết quả |
|---|---|
| pytest 36 file liên quan trên `47fe6af` (35 file lượt 1 + `test_la_chan_t136.py`) | **2.884 qua, 8 bỏ qua** (7 ca symlink, 1 ca FIFO: Windows), **7 xfail có từ trước** (SL-T070-4), **0 hỏng**, 21 phút 35 giây |
| Probe A, E (`probe_t136.py`); probe G4; chạy thử 3 lệnh ca R | như mục 1, 3, 4 |
| `ruff check .` | sạch |
| detect-secrets (`PYTHONUTF8=1`) biên bản này | 0 |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `01fc45c`) không xung đột |

### Điều kiện (cập nhật sau lượt 2)

**A. Gộp `main`: được ngay.**

**B.**

1. ~~Sửa LC-T136-1~~: **đã xong** ở `348f6f3`.
2. **Khi có máy Mac:** chạy `tests/test_la_chan_t136.py` (ca FIFO nay không còn dấu `xfail`: phải qua) cùng các ca symlink T-131, T-136.
3. **Kịch bản T-128:** dùng **ca R bản cuối** (mục 4), thay cho mục B.3 lượt 1.
4. **Phiếu mới (Thấp): sửa SL-T136-1 và G4** theo mục 2, 3; Lá Chắn **đầy đủ**. **Khuyến nghị xong trước khi bật công tắc Hẹn giờ/Đăng ngay cho bài thật**; nếu bật trước thì ghi sổ rủi ro và README như mục 2.

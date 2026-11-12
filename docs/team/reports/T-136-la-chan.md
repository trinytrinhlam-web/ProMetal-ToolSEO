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

# Báo cáo T-074 · Dọn thẻ ảnh lượt 2 (sau T-070)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-074](../tickets/T-074-don-the-anh-luot-2.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành: đủ yêu cầu 1–6. SL-T070-4 và LC-T052-5 để nguyên (đã hoãn, đúng phiếu) |

## Tóm tắt (cho chủ dự án)

File nhớ thẻ ảnh sửa tay (`data/image_tags.sqlite`) nay chặn được cả hai cách lách mà Soi Lỗi và Lá Chắn tìm ra ở T-070: file có một dòng mục lục bị lặp để giấu đoạn lệnh, và chương trình khác sửa file đúng lúc giữa bước kiểm và bước ghi. Tôi thử lại đúng các cách đó: đoạn lệnh giấu trong file không chạy lần nào, file lạ tự được đổi tên sang một bên (giữ lại) và app tạo file mới. Có thêm giới hạn độ dài cho mỗi giá trị trong file, nên lệnh tạo dữ liệu khổng lồ bị chặn ngay; file có một ô dữ liệu quá dài cũng tự được đổi tên, không làm phần thẻ sửa tay báo lỗi mãi.

Về nhận ảnh AI theo tên: tên file như "AI01.png", "dalle3_cong.png", "Gemini2_….png", thư mục "AIgen", "Ảnh mô phỏng" nay là **ảnh AI**. Tên ảnh từ máy ảnh, điện thoại, Zalo vẫn là ảnh thật. Đánh đổi: khoảng 1 trong 1.000–2.000 tên file **ngẫu nhiên** trộn chữ và số mà có "ai" kẹp giữa hai số (ví dụ "6Ai5lnBH.jpg") bị coi là ảnh AI; ảnh đó chỉ mất mã công trình, khu vực, trước/sau, không lộ chữ nào.

Người dùng chưa thấy gì khác trên giao diện: chưa màn hình nào dùng phần này (màn hình chọn ảnh T-056 sẽ dùng).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/image_tags.py` | `_app_tables` đọc vào danh sách (`:586`); hàm mới `_begin` mở giao dịch trước khi kiểm (`:559`), dùng ở `_connect` (`:412`), `_prepare` (`:455`), `_is_healthy` (`:628`); `set`, `clear`, `clear_all` mở giao dịch ghi (`:304`, `:336`, `:345`); `_guard` đặt giới hạn độ dài (`:547`, hằng `_MAX_SQLITE_LENGTH` `:84`); `_is_too_big` (`:673`) dùng ở `_is_healthy` (`:645`) và `_db_message` (`:687`); `_is_healthy` đọc thử mọi ô (`_OVERSIZED_SQL` `:122-136`, `:636`); sửa docstring module (`:15-28`) và `_guard` (`:537-545`) |
| `seo_app/images/tags.py` | `_starts_new_word`, `_tokens` có thêm `split_digits` độc lập với `split_case` (`:423`, `:431`); dấu hiệu AI dựng ở 3 cách tách (`:464`); tên file tách thêm chỗ chữ dính số (`_has_ai_marker` `:486`, gọi ở `:939`); thêm `AIgen` (`:278`) và `mô phỏng` (`:270`); docstring |
| `tests/test_images_tags.py` | 69 ca test mới (`test_t074_*`); sửa kỳ vọng một test T-070 của chính Thợ Máy cho thiết kế mới (`test_t070_schema_is_read_before_any_other_query`, xem mục 2) |
| `tests/test_soi_loi_t070.py` | Chỉ gỡ 6 khối `@pytest.mark.xfail(...)` (SL-T070-1 ×3, -2, -3, -5): 44 dòng xóa, 0 dòng thêm; không đổi thân test, `assert`, `parametrize` |
| `docs/team/reports/T-074-tho-may.md` | Báo cáo này |

`git diff --stat da87dbf..HEAD`: chỉ 4 file code/test ở trên (+ báo cáo). Không sửa `seo_app/storage/drafts.py`, `app/**`, `config/**`. Không thêm thư viện.

## Cách sửa từng mục

### 1. LC-T070-1 (= SL-T070-1) · dòng lặp trong `sqlite_master`

- `_app_tables` đọc `sqlite_master` vào **danh sách** (vẫn `LIMIT` = số dòng mong đợi + 1, không đọc vô hạn); nhiều dòng hơn số mong đợi (4), hay có hai dòng trùng `(loại, tên)`, thì trả `None` (file lạ). Phần so từng bảng với `_expected_schema` giữ nguyên.
- Dòng lặp nằm **trong** giới hạn (file tạo dở chỉ có bảng thẻ cộng một dòng chỉ mục lặp: 3 dòng) cũng bị bắt nhờ kiểm trùng.
- Test: `test_t074_duplicate_master_row_is_a_strange_file` (5 kiểu: lặp chỉ mục `info` như thử T1 của Lá Chắn, lặp chỉ mục `manual_tags` như Soi Lỗi, lặp cả hai, chỉ lặp mà không có trigger, lặp trong giới hạn; mỗi kiểu: `quick_check` vẫn "ok", `_is_healthy` = `False`, lưu "Tân Phú" đọc lại đúng "Tân Phú" qua hai lần tạo kho, file lạ giữ nguyên từng byte), `test_t074_duplicate_master_row_swapped_in_while_running_is_caught` (2 kiểu, thay file khi app đang chạy), `test_t074_app_tables_rejects_more_rows_than_expected_or_repeated_rows`. 3 test `xfail` SL-T070-1 của Soi Lỗi nay qua.

### 2. LC-T070-2 · kiểm và dùng trong cùng một giao dịch

- Hàm mới `_begin`: `BEGIN IMMEDIATE` cho thao tác ghi, `BEGIN` cho thao tác đọc; chạy ngay sau `_guard`, **trước** `_app_tables`; giao dịch giữ tới khi thao tác xong (commit/rollback ở `with conn`).
  - `_connect(write=…)`: `set`, `clear`, `clear_all` dùng giao dịch ghi; `get_many`, `list_manual` (và `get`, `resolve`, `resolve_many` đi qua chúng) dùng giao dịch đọc.
  - `_prepare`: kết nối tạo bảng mở `BEGIN IMMEDIATE`, kiểm `_app_tables` rồi mới `CREATE TABLE`/`INSERT`. File lạ thì chưa ghi gì, báo "File lưu thẻ ảnh bị lỗi…", `_ready` vẫn `False`, nên lần sau `_is_healthy` kiểm lại và đổi tên file lạ.
  - `_is_healthy` cũng mở `BEGIN` trước `_app_tables`, nên cấu trúc không đổi được giữa `_app_tables`, `quick_check` và các bước sau.
- Vì sao chặn được: ở chế độ nhật ký thường (app dùng chế độ này), khóa của giao dịch giữ tới khi xong; chương trình khác muốn đổi cấu trúc phải ghi, nên nhận "database is locked". Ở chế độ WAL (file người khác đặt sẵn), giao dịch đọc thấy một ảnh chụp cố định kể từ câu kiểm `sqlite_master`, nên cấu trúc lúc dùng vẫn là cấu trúc lúc kiểm (theo cách SQLite định nghĩa giao dịch WAL; chưa có test riêng cho WAL, xem Đề xuất 2).
- Cải thiện phụ (suy luận từ cách giao dịch hoạt động, chưa thử riêng): hai câu `CREATE TABLE` nay nằm trong một giao dịch, nên tab khác không còn thấy file mới "có một bảng" như Lá Chắn T-070 ghi ở mục "Đua nhẹ khi hai tab cùng tạo file lần đầu".
- Test giả lập như T2: `test_t074_structure_cannot_change_between_check_and_use` bọc `_app_tables`; ngay sau **mỗi** lần kiểm (7 lần: `set`, `get`, `clear`, `list_manual`, rồi mở lại từ đầu qua `_is_healthy`, `_prepare`, `set`), "chương trình khác" (kết nối riêng, không chờ khóa) thêm một trigger sửa khu vực. Kết quả: **7/7 lần bị chặn** ("database is locked"), file không có trigger, khu vực đọc lại đúng "Tân Phú". Trên code cũ test này hỏng (trigger được thêm vào). `test_t074_change_made_between_operations_is_caught_at_next_check`: trigger thêm vào **giữa** hai thao tác vẫn bị bắt ở lần kiểm sau, như T-070.
- `test_t074_parallel_reads_and_writes_do_not_deadlock`: 4 luồng cùng lưu, đọc, liệt kê trên một kho (như nhiều tab): không lỗi, không kẹt (xem "Rủi ro").
- **Đổi kỳ vọng một test cũ của Thợ Máy** (`test_t070_schema_is_read_before_any_other_query`, viết ở T-070, không phải test của Soi Lỗi): câu đầu tiên sau giới hạn số bước nay là `BEGIN`/`BEGIN IMMEDIATE`, rồi mới tới câu đọc `sqlite_master`. Test nay kiểm chặt hơn: đúng loại giao dịch cho từng kết nối (kiểm file: đọc; tạo bảng: ghi; `get`: đọc; `set`: ghi) và `sqlite_master` vẫn là câu đọc đầu tiên.

### 3. SL-T070-2 · giới hạn độ dài, `SQLITE_TOOBIG` là hỏng

- `_guard` đặt `conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1_000_000)` (`_MAX_SQLITE_LENGTH`, mặc định của SQLite là 1 tỷ): `randomblob`, `zeroblob`, `hex`, `replace` vượt 1 triệu byte báo `SQLITE_TOOBIG` ngay; `printf('%.*c', …)` trả rỗng. Dòng dài nhất app ghi (đường dẫn 1.024 ký tự, mỗi ký tự 4 byte) vẫn lưu, đọc, liệt kê được (`test_t074_longest_row_the_app_writes_fits_under_length_limit`).
- `_is_too_big` nhận mã 18; `_is_healthy` coi là hỏng (trả `False`, không ném lại); `_db_message` trả câu "File lưu thẻ ảnh bị lỗi…"; `_connect` đặt lại `_ready` (như mọi lỗi trừ bận/khóa).
- **Thêm ngoài chữ của phiếu, cần để điều trên có tác dụng:** `_is_healthy` đọc thử mọi ô của hai bảng (`_OVERSIZED_SQL`, chỉ ghép tên bảng, tên cột hằng). Lý do (đã thử, E3): file có **một ô** dài quá giới hạn vẫn qua `quick_check` ("ok"), nhưng mọi lần đọc tới ô đó báo `SQLITE_TOOBIG`; không có bước đọc thử thì `_is_healthy` = `True`, kho báo lỗi 3/3 lần và không bao giờ đổi tên file (kẹt mãi, đúng điều Lá Chắn cảnh báo). Có bước này: file bị đổi tên ngay ở lần kiểm đầu. Trước T-074 file như vậy chỉ bị bỏ dòng hỏng; chính giới hạn độ dài mới làm nó thành "kẹt", nên hai việc phải đi cùng nhau.
  - Chi phí (E4): trên file thật lớn nhất (20.000 thẻ, đường dẫn dài) `_is_healthy` từ 0,47 triệu lên 1,31 triệu bước (0,32 → 0,64 giây trên máy này), chỉ chạy khi kho kiểm lại file (lần đầu, hoặc sau một lỗi). Giới hạn 50 triệu bước còn dư khoảng 38 lần; `test_t070_step_limit_leaves_room_for_the_largest_real_file` (chạy với 1/10 giới hạn) vẫn qua.
- Câu `CREATE` khổng lồ trong `sqlite_master`: chính câu kiểm cấu trúc báo `SQLITE_TOOBIG` (E2). Trước bản sửa, `_is_healthy` ném lại lỗi này nên file sẽ kẹt ở câu "Không mở được…"; nay là hỏng, file bị đổi tên (`test_t074_huge_create_statement_is_moved_aside_not_jammed`).
- Docstring: bỏ câu "file dựng sẵn không làm treo app"; nay ghi rõ lớp kiểm cấu trúc là lớp chặn chính (chỉ câu SQL của app được chạy trên file), giới hạn số bước và độ dài là lớp phòng sau và **không phải giới hạn thời gian** (E5).
- Test: `test_t074_guard_limits_length_of_every_value`, `test_t074_file_with_oversized_cell_is_moved_aside_not_jammed` (6 kiểu: chữ quá dài, chữ nhiều byte, khóa là khối byte, cột số chứa khối byte, khóa và giá trị bảng `info` quá dài), `test_t074_oversized_cell_swapped_in_while_running_resets_then_recovers` (3 kiểu). Test `xfail` SL-T070-2 của Soi Lỗi nay qua.

### 4. SL-T070-3 · tên file tách chỗ chữ dính số; "AIgen"

- `_tokens` có thêm `split_digits`, độc lập với `split_case`. Tên **file** nay tách ở dấu cách, dấu câu, gạch dưới **và** chỗ chữ dính số, nhưng vẫn không tách theo chữ hoa: "AI01" → "ai 01", "dalle3" → "dalle 3", "Gemini2.5" → "gemini 2 5"; "xAI3kQ" → "xai 3 kq" (không có "ai" đứng riêng, **vẫn là ảnh thật**). Tên **thư mục** đọc như cũ (tách cả chữ hoa lẫn số). Dấu hiệu AI dựng ở cả 3 cách tách nên khớp với mọi kiểu đọc.
- "AIgen": thêm vào `_AI_JOINED` (chữ hoa đứng trước chữ thường không tách được, nên "AIgen" là một từ "aigen"); "AIGen", "aigen", "AIgen 2025", file "AIgen_01.png" đều là ảnh AI.
- Đánh đổi (E6, 20.000 tên mỗi loại): tên ngẫu nhiên trộn chữ hoa, chữ thường, số dài 6, 12, 20 ký tự bị coi là ảnh AI 9, 19, 11 lần (khoảng 0,05–0,1 %), đều là tên có "ai" kẹp giữa số hay sát số ở đầu/cuối ("6Ai5lnBH2jkl", "AI81TwIHKnI9"); tên kiểu Zalo (chữ số thập lục phân): 0/20.000. 16 kiểu tên của máy ảnh, điện thoại, ứng dụng chat (`IMG_E0001`, `IMG20250315102030`, `MVIMG_…`, `DJI_0001`, `GOPR0001`, `P1000123`, `received_…`, `FB_IMG_…`, `z5432…_7f3a…`, `MAI1`, `TRAI2`…) vẫn là ảnh thật (có test).
- `is_ai_name` không đổi (đọc kiểu tên thư mục), như Soi Lỗi đã ghi: T-056 chỉ dùng nó cho tên thư mục gốc.
- Test: `test_t074_ai_file_names_with_digits_stuck_are_ai` (15 tên), `test_t074_camera_and_chat_file_names_with_digits_stay_real` (16 tên), `test_t074_aigen_and_simulated_folders_are_ai` (10 tên, ở hai tầng, kèm `is_ai_name`), `test_t074_folder_names_still_split_the_old_way`. Test `xfail` SL-T070-3 (8 ca) nay qua.

### 5. SL-T070-5 · "mô phỏng"

- Thêm `mô phỏng` vào `_AI_PHRASES` (tự có dạng không dấu "mo phong" và viết liền "mophong"). Không thêm "ảnh dựng" ("Ảnh dựng khung" là ảnh thật, có test). "Nhà anh Phong", "Mô tơ cổng cuốn", "Mộ Phong" vẫn là ảnh thật (`test_t074_words_near_simulated_stay_real`). Test `xfail` SL-T070-5 (3 ca) nay qua.

### 6. Gỡ `xfail`

- Gỡ đúng các khối đã XPASS: SL-T070-1 (3 test), SL-T070-2 (1), SL-T070-3 (1 khối, 8 ca), SL-T070-5 (1 khối, 3 ca). `git diff da87dbf..HEAD -- tests/test_soi_loi_t070.py`: 44 dòng xóa đều thuộc 6 khối `@pytest.mark.xfail(...)`, 0 dòng thêm.
- Giữ `xfail` của SL-T070-4 (7 ca, đã hoãn): vẫn XFAIL như mong đợi.

## Bằng chứng

Máy Windows 11 Pro của chủ dự án, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-074`, nhánh `team/T-074`. Máy đang chạy song song các agent khác.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py \
    tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx
(2026-10-21 09:51–09:55 +07, tại 6851e1b, commit code cuối)
SKIPPED [1] tests\test_images_tags.py:1641: máy không cho tạo symlink (Windows chưa bật Developer Mode)
SKIPPED [1] tests\test_soi_loi_t052.py:538: máy không cho tạo symlink (Windows chưa bật Developer Mode)
SKIPPED [1] tests\test_images_folders.py:368: chỉ tạo được trên Mac/Linux
SKIPPED [1] tests\test_images_folders.py:381: chỉ tạo được trên Mac/Linux
SKIPPED [4] tests\test_images_folders.py:62: Máy Windows này không cho tạo symlink (lỗi 1314); xem test junction
1087 passed, 8 skipped, 7 xfailed in 166.89s (0:02:46)

$ uv run ruff check .
All checks passed!
```

- So với T-070 (Lá Chắn: 1003 qua, 8 bỏ qua, 22 xfail): thêm 15 ca `xfail` nay qua và 69 test mới; 7 xfail còn lại đều là SL-T070-4. 8 bỏ qua như cũ (2 ca symlink của T-052, 6 ca của T-048: Windows chưa bật Developer Mode, hoặc chỉ chạy được trên Mac/Linux).
- Test viết trước, chạy trên code cũ (`da87dbf`) để thấy đỏ: 10 test kho thẻ đầu tiên của T-074 cho `9 failed, 1 passed` (ca qua là `…between_operations…`, vốn bắt được từ T-070).
- Test nhiều luồng chạy riêng 5 lần liền: 5/5 qua (6–28 giây mỗi lần, dao động vì máy đang tải nặng).
- Không chạy toàn bộ `uv run pytest` (theo `rules.md`: Chỉ Huy chạy trên Windows khi gộp).

Thử ngoài repo (script trong thư mục tạm của phiên, file SQLite trong thư mục tạm, không sửa code):

| # | Thử gì | Kết quả |
|---|---|---|
| E1 | Giới hạn 1 triệu byte, file có ô chữ 2 MB | `substr(ô, 1, 10)`, `length(ô)`: `SQLITE_TOOBIG`; `quick_check`, `integrity_check`: "ok". `randomblob`, `zeroblob`, `hex`, `replace` quá giới hạn: `SQLITE_TOOBIG` ngay; `printf('%.*c', 3000000, 'x')`: rỗng |
| E2 | Câu đọc thử mọi ô (`length(CAST(… AS BLOB)) > ?`) | Ô chữ, khối byte, khối byte trong cột số, chữ nhiều byte (400.000 ký tự, 1,2 MB): đều `SQLITE_TOOBIG`; file UTF-16 hợp lệ: không báo. Câu `CREATE` 1,5 MB: câu đọc `sqlite_master` báo `SQLITE_TOOBIG` |
| E3 | Bỏ bước đọc thử, file có ô 1,2 MB | `_is_healthy` = `True`; `list_manual` báo lỗi 3/3 lần, `recovered_from` = `None` (kẹt). Có bước đọc thử: `_is_healthy` = `False` |
| E4 | Số bước của `_is_healthy` trên file 20.000 thẻ, đường dẫn dài | Có đọc thử: 1.305.360 bước, 0,64 s; không có: 465.343 bước, 0,32 s |
| E5 | Truy vấn đệ quy, mỗi dòng `randomblob(999999)`, có đủ hai giới hạn | Bị dừng ở 200.000 bước sau 45,1 s; ở 1.000.000 bước sau 218,3 s. Suy ra: 50 triệu bước khoảng 3 giờ |
| E6 | Tên file | Như mục 4 |
| E7 | 4 luồng × 15 vòng (lưu, đọc, liệt kê, `resolve_many`) trên một kho, bản cũ `da87dbf` (nạp từ `git show`) và bản mới, 3 lượt xen kẽ | Bản cũ 3,03 / 2,11 / 2,54 s; bản mới 3,44 / 2,16 / 2,21 s; cả hai 0 lỗi |

## Đối chiếu tiêu chí xong

- [x] YC1 LC-T070-1: `image_tags.py:586-609`; `test_t074_duplicate_master_row_*`, `test_t074_app_tables_rejects_*`; 3 test SL-T070-1 qua
- [x] YC2 LC-T070-2: `_begin` `:559`, `_connect` `:412`, `_prepare` `:455`, `_is_healthy` `:628`; test giả lập T2 `test_t074_structure_cannot_change_between_check_and_use`
- [x] YC3 SL-T070-2: `setlimit` `:547`, `_is_healthy` `:636`, `:645`, `_is_too_big` `:673`, `_db_message` `:687`, đặt lại `_ready` `:419-425`; docstring `:15-28`, `:537-545`; test SL-T070-2 qua
- [x] YC4 SL-T070-3 và "AIgen": `tags.py:423-451`, `:464`, `:486`, `:939`, `:278`; test SL-T070-3 qua; "xAI3kQ" vẫn là ảnh thật
- [x] YC5 SL-T070-5: `tags.py:270`; test SL-T070-5 qua
- [x] YC6: chỉ gỡ các khối `xfail` đã XPASS, không đổi điều kiện kiểm
- [x] Test liên quan qua, `uv run ruff check .` sạch
- [x] Không làm SL-T070-4, LC-T052-5 (đã hoãn); không sửa file ngoài phạm vi
- [x] Báo cáo nộp tại `docs/team/reports/T-074-tho-may.md`

## Rủi ro và điểm cần chú ý

- **Giới hạn số bước và độ dài không phải giới hạn thời gian** (E5): nếu một câu SQL lạ chạy được trên file thẻ thì vẫn có thể chạy tới khoảng 3 giờ trước khi bị dừng. Sau T-074 điều này chỉ xảy ra khi lớp kiểm cấu trúc bị lách (nay so khớp đúng từng dòng, không thừa, không lặp, trong cùng giao dịch), tức là chỉ câu SQL của app được chạy. Docstring đã ghi đúng mức. Xem Đề xuất 1.
- **Giao dịch đọc giữ khóa đọc suốt thao tác** (trước đây nhả sau từng câu): tab khác đang lưu thẻ phải chờ tới khi thao tác đọc xong mới ghi được (chờ tối đa 5 giây, quá thì báo "đang bận"). Đo E7 (4 luồng cùng đọc, ghi): bản mới không chậm hơn bản cũ, 0 lỗi "đang bận". Streamlit chạy mọi tab trong một tiến trình (nhiều luồng) nên E7 sát cách dùng thật; chưa thử hai tiến trình app cùng mở một file (hai cửa sổ `run.bat`).
- **Tên file ngẫu nhiên nhận nhầm là ảnh AI** khoảng 0,05–0,1 % (mục 4): hướng an toàn, ảnh chỉ mất thẻ công trình; tên của máy ảnh, điện thoại, Zalo phổ biến không bị.
- **`_is_healthy` chậm gấp đôi** trên file lớn nhất (0,64 giây), chỉ khi kho kiểm lại file.
- **Suy luận, chưa thử:** file bị sửa ở mức từng trang để chỉ mục khóa chính chứa khóa khác với bảng (khóa quá dài chỉ nằm trong chỉ mục) có thể qua `quick_check` (vốn không so chỉ mục với bảng) và bước đọc thử (chỉ đọc bảng); khi đó thao tác đọc qua chỉ mục có thể báo lỗi lặp lại thay vì đổi tên file. Muốn vậy phải sửa tay từng byte của file; hậu quả chỉ là phần thẻ sửa tay báo lỗi, ảnh vẫn dùng thẻ đọc từ tên thư mục.
- Ca symlink vẫn bỏ qua trên máy này (điều kiện T-063, như T-070).

## Đề xuất

1. (Chỉ Huy quyết; phiếu sau nếu cần) Cho bộ đếm trong `_guard` dừng theo **giờ thật** (`time.monotonic()`, ví dụ 10–30 giây mỗi kết nối) bên cạnh số bước, biến E5 thành giới hạn thời gian thật; khoảng 5 dòng trong `image_tags.py`. Không làm ở phiếu này vì phiếu chỉ yêu cầu `setlimit` (SL-T070-2 của Soi Lỗi ghi "và/hoặc").
2. Soi Lỗi (rút gọn): thử thêm cấu trúc bị đổi khi file ở chế độ WAL, hai tiến trình (không chỉ hai luồng) cùng ghi, tên file ngẫu nhiên kiểu khác.
3. Lá Chắn (rút gọn): chạy lại T1, T2, T2b, T3 trên bản này; cân nhắc mục "suy luận, chưa thử" ở trên.
4. T-069 (README): thêm "mô phỏng", "AIgen" và tên file kiểu "AI01…" vào danh sách chữ làm ảnh thành ảnh AI.

## Câu hỏi cho chủ dự án

Không có.

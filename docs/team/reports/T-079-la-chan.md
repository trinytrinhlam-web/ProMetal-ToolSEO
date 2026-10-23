# Biên bản bảo mật T-079 · Đọc ảnh bằng thư mục đã mở từng tầng (vá SL-T063-2) · Lá Chắn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable, chủ dự án đã duyệt) |
| Phiếu được kiểm | [T-079](../tickets/T-079-doc-anh-bang-fd-tung-tang.md) · mức kiểm **đầy đủ** (F1; yêu cầu bảo mật riêng F1, F3) |
| Phạm vi | diff `fa2cc39...team/T-079` (tới `6e84375`): `seo_app/images/folders.py` (+174/−35), `seo_app/storage/drafts.py` (+14/−4), 7 file test, 3 báo cáo; code xung quanh (`_resolve_inside`, `_disk_names`, `_checked_file`, `_Scan`). Đọc báo cáo [Thợ Máy](T-079-tho-may.md), [Soi Lỗi Windows](T-079-soi-loi.md), [Soi Lỗi Linux](T-079-soi-loi-linux.md), biên bản của tôi [T-063](T-063-la-chan.md), [T-076](T-076-la-chan.md), [T-048](T-048-la-chan.md) |
| Máy kiểm | **Windows 11 Pro 10.0.26300**, Python 3.12.15 (uv 0.13.4), **người dùng thường** (tạo được junction; không tạo được symlink file: lỗi 1314). Máy chạy song song agent khác. Phần Linux: số liệu phiên cloud Ubuntu 24.04 của Soi Lỗi (đã đọc kỹ cách thử). Không có máy Mac |
| Ngày | 2026-10-22 → 2026-10-23 (chủ dự án cho dừng tối 22/10, sáng 23/10 làm tiếp; việc dở ở commit `6e84375`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (LC-T079-1 = SL-T079-1, LC-T079-2 mới, LC-T079-3 = SL-T079-L-1). **SL-T063-2 (Cao trên Mac/Linux) đã đóng.** Gộp `main` được ngay; bỏ được điều kiện "T-079 trước khi chạy app trên Mac/Linux" khi T-079 đã gộp |

## Tóm tắt (cho chủ dự án)

Lỗ hổng chính (một chương trình lạ trên máy tráo thư mục con thành "lối tắt" đúng lúc app đọc ảnh, làm app đọc nhầm một file nằm ngoài thư mục ảnh; mức **Cao** trên Mac/Linux) **đã được vá đúng**. Trên máy Windows này tôi dựng lại đúng phép thử "ép kẻ tấn công luôn thắng" của tôi ở T-063: bản cũ lọt nội dung, bản T-079 chặn. Trên Linux, phiên cloud của Soi Lỗi cho app đọc hơn 1,3 triệu lượt trong lúc bị tráo liên tục: không lần nào lọt (bản cũ cùng cách thử lọt hàng nghìn lần). Các lớp chặn cũ còn nguyên, app không chậm đi rõ (kiểm một ảnh thêm khoảng 1 phần nghìn giây), không rò tài nguyên, câu báo lỗi không lộ đường dẫn trên máy.

Còn **3 lỗi nhỏ (Thấp), không chặn gộp**: (1) trên Windows, nếu kẻ tấn công đặt được ngay cạnh thư mục ảnh một thư mục có tên **trông y hệt** (cùng chữ có dấu nhưng gõ theo kiểu khác) **và** thắng cuộc đua tráo, thì vẫn đọc được file bên ngoài; cuộc đua này trên Windows không thắng được trên thực tế (tôi thử hơn 8.000 lượt: 0 lần); (2) khi bị tráo, câu báo lỗi có thể nói về file bên ngoài (ví dụ "Ảnh quá lớn (523 MB)"), chỉ hiện cho chính người dùng app, kẻ tấn công không thấy; (3) câu báo đôi khi sai nghĩa ("không có quyền" thay vì "vừa bị thay đổi, hãy thử lại"). Cách sửa cả 3 đều nhỏ, tôi đã thử trên bản sao code: đóng được cả 3, không hỏng test nào. Đề nghị gom vào một phiếu dọn lỗi trước khi hết Giai đoạn 3, hoặc anh/chị quyết ghi sổ rủi ro.

**Mac/Linux:** sau khi gộp T-079, bỏ được điều kiện "phải vá trước khi chạy app trên Mac/Linux". Riêng Mac vẫn giữ việc cũ: chạy bộ test trên máy Mac thật trước khi dùng (chờ có máy Mac).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T079-1 (= SL-T079-1, mở rộng) | **Thấp** · chỉ Windows | Windows so "đường dẫn thật" của handle với `gốc/parts` bằng `_path_key` = NFC + `casefold`, **lỏng hơn cách NTFS phân biệt tên**: NTFS không gộp dạng Unicode (NFC/NFD), `ß` khác `ss`, dấu Kelvin U+212A khác `k`, thư mục bật phân biệt hoa thường thì `ANH` khác `anh`. Một thư mục "anh em" tên trông y hệt (cạnh gốc, cạnh một tầng của đường dẫn gốc, hay ngay trong gốc) là thư mục **khác** trên ổ nhưng qua phép so. Ngoài đường đọc, `stat` (Soi Lỗi tìm), **đường xem thư mục `_scan_held` (code T-048) cũng so như vậy** | `seo_app/images/folders.py:349-358` (`_win_handle_at`), `:1053` (`_scan_held`), `:382-388` (`_path_key`), `:156-158` (`_name_key`) | Chương trình lạ chạy trên máy, ghi được vào thư mục chứa gốc (tạo `Ảnh kho sân` dạng NFD cạnh `Ảnh kho sân` NFC) và vào thư mục ảnh (tạo junction, không cần quyền quản trị), **thắng cuộc đua 4 nhịp** (`x` là thư mục thật lúc `lstat(x)`, junction lúc `lstat(x/ảnh)`, thật lúc `resolve`, junction lúc mở) → `read_image_bytes` trả nội dung, `stat_image` trả cỡ, `list_folder` trả tên, cỡ file ngoài gốc. **Ép thắng** (`lc79_forced.py`): T-079 lọt cả 4 kiểu tên anh em, lọt cả đọc qua liên kết sang thư mục NFD trong gốc; chặn được đích ngoài gốc tên thường. Ép thắng ở đường xem thư mục: lọt tên (test mới). **Tráo thật** (tiến trình riêng, đích anh em NFD): 8.208 vòng, **0 lọt**. **Vì sao Thấp:** như SL-T063-2 trên Windows (Lá Chắn T-063): đua không thắng được trên thực tế (Windows không đổi chỗ nguyên tử, khóa thư mục đang mở); thêm điều kiện ghi được vào thư mục chứa gốc; chương trình chạy bằng quyền của chủ máy vốn tự đọc được các file đó. **Không áp dụng Mac/Linux** (đường đọc, `stat` đi bằng fd từng tầng, không so chuỗi; quét dùng `_scan_by_fd`), nên không mở lại mức Cao của SL-T063-2 | So đường dẫn thật **đúng như Windows**: phần gốc phải trùng **từng chữ** với gốc đã `resolve` (cùng hàm `GetFinalPathNameByHandleW` trả, không cần gộp gì); phần sau gốc so không phân biệt hoa thường theo bảng của Windows (`CompareStringOrdinal(…, bIgnoreCase=TRUE)`), **không** gộp dạng Unicode, **không** `casefold`. Dùng chung cho `_opened_stat`, `_open_image` và `_scan_held`. Đã thử trên bản sao code: 8 ca SL-T079-1 + ca xem thư mục của tôi XPASS, ép thắng 7/7 ca bị chặn, 722 test khác không hỏng. Khi sửa: thử lại ổ Google Drive thật (chỉ đọc thuộc tính) và ổ mạng |
| LC-T079-2 (mới) | **Thấp** · mọi hệ điều hành | `_checked_file` kiểm loại file, cờ ẩn, cỡ trên `lstat` **theo chuỗi đường dẫn** (`_resolve_inside`) và báo lỗi **trước** lớp kiểm trên mục đã mở. `lstat` đó đi xuyên một tầng giữa vừa bị tráo thành liên kết (chính khe SL-T063-2, -3), nên câu báo **mô tả file ngoài thư mục ảnh**: "Ảnh quá lớn (X MB), tối đa 40,0 MB.", "File ảnh rỗng (0 byte).", "Đây không phải là file ảnh.", "App không đọc file ẩn…". T-079 đóng đường trả số liệu khi **thành công** (`_opened_stat`), chưa đóng đường **báo lỗi** này. Trái mục tiêu phiếu ("không bao giờ trả … số liệu của file nằm ngoài thư mục ảnh") | `folders.py:797-808` (`_checked_file`), `:600-615` (`lstat` theo chuỗi) | Kẻ tráo thắng đúng lúc `lstat(x/ảnh)` (Linux thắng thật được: Soi Lỗi Linux đo bản cũ lọt cỡ 1.457/68.215 vòng ở đúng khe này) → người dùng xem/kiểm ảnh → câu báo cho biết cỡ (làm tròn 0,1 MB, chỉ khi quá giới hạn), rỗng hay loại của một file ngoài gốc do kẻ tấn công chọn. Ép thắng trên Windows: cả `main` lẫn T-079 báo "Ảnh quá lớn (5,0 MB), tối đa 1,0 MB." với file ngoài 5 MB. **Vì sao Thấp:** chỉ người dùng app thấy câu báo; kẻ tấn công không thấy giao diện; câu báo không đi ra AI, WordPress hay log (`drafts.py:955` chỉ giữ để hiện); thông tin thô | Khi một kiểm ở `_checked_file` hỏng, trước khi báo, mở mục `gốc/parts` không đi theo liên kết (Mac/Linux: `_posix_open_dir` + `os.stat(…, dir_fd=, follow_symlinks=False)`; Windows: `_win_open` chỉ thuộc tính + so đường dẫn thật) và so định danh với `lst`; khác thì "Ảnh vừa bị thay đổi…". Đã thử trên bản sao: 6 ca test mới XPASS, không hỏng test khác. (Câu "Không tìm thấy", "không phải là thư mục" ở `_resolve_inside`, `list_folder` cũng có thể tả mục ngoài khi bị tráo, nhưng chỉ ở mức có/không, loại: ghi nhận, không bắt sửa) |
| LC-T079-3 (= SL-T079-L-1) | **Thấp** · Linux/Mac, chỉ sai câu báo | Đang bị tráo, `resolve(strict=True)` trả `EINVAL` → app báo "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." thay vì "vừa bị thay đổi, hãy thử lại". **Giữ mức Thấp** (Soi Lỗi đề xuất): an toàn, không đọc gì ngoài gốc, không lộ gì; người dùng chỉ hiểu sai nguyên nhân | `folders.py:617`, `:622-623` (code T-048) | Soi Lỗi Linux đo thật: ~1.100 lần/8 giây khi bị tráo nguyên tử; test `tests/test_soi_loi_t079_linux.py::test_sl_t079_l_1_…` ×3 (`xfail` strict, chỉ chạy trên Linux/Mac) | Như Soi Lỗi: trong `_resolve_inside`, vòng `lstat` đã xác nhận mọi tầng là thư mục thật, nên `OSError` EINVAL, ELOOP, ENOTDIR từ `resolve` là `_ChangedError`; giữ `PermissionError` là "Không đọc được…". Gộp chung phiếu dọn với LC-T079-1, -2 |

Không có lỗi Nghiêm trọng, Cao hay Trung bình.

Test chứng minh lỗi mới (chỉ thêm, `xfail(strict=True)`): `tests/test_la_chan_t079.py`, 10 ca: 6 ca LC-T079-2 (`read_image_bytes`, `stat_image` × file ngoài quá cỡ / rỗng / là thư mục; chạy mọi hệ điều hành, giả đúng một bước `lstat`), 1 ca LC-T079-1 ở đường xem thư mục (Windows, junction thật, ép thắng), 3 ca đối chứng (qua). Chạy `--runxfail`: 7 ca hỏng đúng ở câu kiểm ("câu báo nói về file ngoài thư mục ảnh: 'Ảnh quá lớn (2,0 MB), tối đa 1,0 MB.'", "liệt kê được file ngoài thư mục ảnh").

## Việc 1 · Soát diff

Đọc toàn bộ diff `seo_app/` và code xung quanh.

| Phần | Đánh giá | Bằng chứng |
|---|---|---|
| Mac/Linux đọc (`_open_image`) | **Đúng định hướng đã duyệt ở T-063.** Mở thư mục cha từng tầng từ gốc đã `resolve` (`_posix_open_dir`: `O_DIRECTORY \| O_NOFOLLOW \| O_CLOEXEC \| O_NONBLOCK`), rồi mở file trong chính thư mục đã mở với `O_NOFOLLOW \| O_NONBLOCK \| O_NOCTTY \| O_CLOEXEC`. Không tầng nào đi theo liên kết; thư mục đã mở vẫn là thư mục thật dù tên bị tráo sau đó. fd thư mục đóng trong `finally`; `_posix_open_dir` đóng fd khi lỗi giữa chừng (`BaseException`) | `folders.py:231`, `:391-409`, `:908-918` |
| Mac/Linux `stat` (`_opened_stat`) | Như trên rồi `os.stat(tên, dir_fd=, follow_symlinks=False)`: không mở file, không đi theo symlink | `:858-869` |
| Windows đọc | `os.open(đường dẫn đã kiểm)` rồi hỏi **đường dẫn thật của chính handle vừa mở** (`_win_handle_at`), phải là `gốc/parts`; không hỏi được → từ chối. Đúng bổ sung "Windows nên vá thẳng" của tôi ở T-063 (trừ LC-T079-1) | `:919-927`, `:349-358` |
| Windows `stat` | Handle **chỉ quyền thuộc tính**, mở chính mục cuối không đi theo (`_win_open`), hỏi đường dẫn thật + `_win_handle_is_link` + `os.fstat` trên handle đó. Không đọc nội dung. Đo: trong lúc giữ handle này, chương trình khác vẫn ghi, đổi tên, xóa được file (handle quyền đọc cùng chế độ chia sẻ thì chặn đổi tên, lỗi 32), nên không cản Drive hay phần mềm khác | `:870-879`, `:284-306` |
| Sau khi mở | File thường, không ẩn, không quá cỡ, **cùng định danh** với mục vừa kiểm; số liệu (cỡ, giờ sửa, `file_id`) lấy từ mục đã mở | `:881-889`, `:829-835`, đọc `:938-944` |
| `_open_error` (SL-T063-5) | FileNotFound → "Không tìm thấy", PermissionError → "Không đọc được", lỗi khác (ELOOP, ENOTDIR, …) → `_ChangedError`. Dùng ở `_listed_names`, `_scan_by_fd` và 2 hàm mới. An toàn trước (lỗi lạ bị coi là "vừa bị thay đổi", không bao giờ đi tiếp) | `:412-423`, `:706-707`, `:1040-1041` |
| `_win_open` tách từ `_win_hold_dir` | Cùng cờ, cùng chế độ chia sẻ (không `FILE_SHARE_DELETE`), cùng cách đóng: hành vi giữ thư mục khi quét không đổi | `:284-316` |
| `ImageEntry.file_id` | `compare=False, repr=False`: so, băm, `repr` như cũ; chỉ `stat_image` điền; không phải đường dẫn | `:477` |
| `drafts.py` (LC-T076-3) | Lần hỏi lại tên cũ phải cùng kết quả **và** cùng `file_id`; ảnh ở tên của danh sách phải cùng cỡ, giờ sửa **và** `file_id`. Chặt hơn, không lỏng hơn; ổ không có số inode thì như cũ | `drafts.py:943-953` |
| Câu báo | Hằng cố định (`_MSG_IMAGE_CHANGED`, `_MSG_CANNOT_OPEN`), ném `from None`, không đường dẫn | `:95-96` |
| Lớp chặn T-048, T-076 | **Giữ nguyên**: `_parse_rel`, `_is_safe_name`, `_resolve_inside`, `_disk_names`, `_found_names`, `_checked_file`, `_Scan._scan_held`, `_read_entries`, `_visit`, `_is_link_stat`, `_win_final_path`, `_win_handle_is_link`, `_path_key` không đổi (diff; khớp so AST của Soi Lỗi). `_listed_names`, `_scan_by_fd` chỉ đổi cách đổi lỗi | diff `fa2cc39...6e84375` |

**Ghi nhận khi soát (không thành lỗi):** trên Windows, `_is_link_stat(os.fstat(fd))` trong `_opened_stat` **không có tác dụng**: Python không điền `st_reparse_tag` khi `fstat` (đo trên junction: `fstat` cho `0x0`, `lstat` cho `0xa0000003`). Mở chính junction thì đường dẫn thật của handle là **đường dẫn của chính nó**, nên `_win_handle_at` cũng không chặn ca "mục cuối thành liên kết đúng lúc mở" (đo: qua). Lớp chặn thật cho ca này là `_win_handle_is_link` và so định danh (junction thì thêm "không phải file thường"). Vậy 2 "đột biến sống sót" trong báo cáo Soi Lỗi được **so định danh** che, không phải `_win_handle_at` như báo cáo viết; kết luận "thừa lớp, không phải lỗ hổng" vẫn đúng. Khi sửa LC-T079-1: **giữ** `_win_handle_is_link` và so định danh. (Không thử được symlink file: người dùng thường không tạo được, lỗi 1314.)

## Việc 2 · SL-T063-2, -3 đã đóng; LC-T076-3 đóng

### Windows: phép ép thắng của Lá Chắn T-063, dựng lại

Script `lc79_forced.py` (thư mục nháp, mở rộng từ `t063_win_forcedwin.py` của T-063): mỗi khi app `lstat`, `os.open` hay `_win_open` một đường dẫn tận cùng là ảnh, thư mục con `x` **chắc chắn** là junction trỏ tới đích; mọi bước khác (`resolve`, `FindFirstFileW`) thấy `x` là thư mục thật chứa ảnh mồi. Người dùng thường, thư mục tạm.

| Đích của junction | `main` `fa2cc39` | **T-079** | Bản sao có cách sửa LC-T079-1, -2 |
|---|---|---|---|
| Ngoài gốc, tên thường (đúng phép thử T-063) | lọt nội dung + cỡ | **chặn** ("Ảnh vừa bị thay đổi…" cả đọc lẫn `stat`) | chặn |
| Anh em của gốc, tên NFD | lọt | lọt (LC-T079-1) | chặn |
| Anh em, dấu Kelvin thay `k` | lọt | lọt (LC-T079-1) | chặn |
| Anh em, `ß` thay `ss` | lọt | lọt (LC-T079-1) | chặn |
| Anh em khác hoa thường (thư mục cha bật phân biệt hoa thường) | lọt | lọt (LC-T079-1) | chặn |
| Thư mục khác **trong** gốc, tên NFD (đọc qua liên kết, không ra ngoài) | đọc qua liên kết | đọc qua liên kết | chặn |
| Ngoài gốc, file 5 MB, giới hạn 1 MB | "Ảnh quá lớn (5,0 MB)…" | "Ảnh quá lớn (5,0 MB)…" (LC-T079-2) | "Ảnh vừa bị thay đổi…" |

→ **SL-T063-2, -3 đóng trên Windows cho đích thường bằng chính code** (không còn dựa vào "đua khó thắng"); phần còn lại là LC-T079-1. Hai test Windows của tôi ở T-063 (`test_sl_t063_2_windows_…`, `test_sl_t063_3_windows_…`) nay qua, không còn `xfail`.

### Windows: tráo thật

Script `lc79_race.py` (từ `t063_win_probe.py` của T-063): **tiến trình riêng** đổi tên thư mục `x` (có ảnh mồi) đi, đặt junction `x` trỏ tới đích, gỡ, trả tên, liên tục; luồng app gọi `read_image_bytes`, `stat_image`, `list_folder(0, "x")`. Mỗi vòng = 1 đọc + 1 `stat` + 1 xem.

| Lượt | Cấu hình | `main`: vòng · lọt | **T-079**: vòng · lọt |
|---|---|---|---|
| A | 3 luồng app, 2 tiến trình tấn công, 30 s | đích anh em NFD: 5.381 · 0 | đích ngoài: 4.973 · **0**; đích anh em NFD: 5.863 · **0** |
| B | 1 luồng app nghỉ 2 ms, **nới khe** 2 ms trước mỗi `lstat`/mở ảnh, 2 tiến trình, 30 s | ngoài: 1.338 · 0; anh em: 1.249 · 0 | ngoài: 1.177 · **0**; anh em: 1.278 · **0** |
| C | như B nhưng **1 tiến trình tấn công** (tráo được 148–1.866 lần/30 s) | ngoài: 2.206 · 0 (1.866 lần tráo); anh em: 406 · 0 (673) | ngoài: 391 · **0** (265); anh em: 455 · **0** (683); anh em, không nới khe: 612 · **0** (148) |
| Đối chứng dương | bật/tắt junction **tại chỗ** trên `x` rỗng (LC-T048-2), 4 luồng, 20 s | | 5.718 vòng, 14.094 lần tráo: **lọt 14 tên** (đã biết, LC-T048-2), 0 nội dung, 0 cỡ |

- T-079: **14.749 vòng** (≈29.500 lần đọc/`stat` khi bị tấn công, 8.208 vòng với đích anh em): **0 lọt nội dung, 0 lọt cỡ, 0 lọt tên, 0 câu báo lộ đường dẫn, 0 lỗi lạ**. Khớp T-063 (0/>15.000), T-048 (0/11.192), Soi Lỗi T-079 (0/>5.000).
- Ở lượt A, B kẻ tấn công chỉ tráo được 0–5 lần mỗi tiến trình: Windows từ chối đổi tên thư mục đang có handle mở, và hai tiến trình tấn công giẫm chân nhau (một tiến trình chạy một mình, không có app: 541 lần/5 s). Vì vậy tôi **không** coi A, B là bằng chứng đủ, chạy thêm C (1 tiến trình, tráo được hàng trăm lần) và đối chứng dương (bộ đếm bắt được lọt khi lọt thật).

### Linux: số liệu phiên cloud của Soi Lỗi (đã đọc kỹ cách thử)

- Cách thử **đúng khe mạnh nhất**: tráo **nguyên tử** (`renameat2(RENAME_EXCHANGE)`) bằng tiến trình riêng, cả root lẫn `nobody`, 6 kiểu (thư mục con, tầng trên, tầng giữa, chính file, liên kết trong gốc, không nguyên tử có giữ trạng thái), có quét cả cây chen vào.
- **T-079: 0 lọt nội dung, 0 lọt cỡ/giờ sửa/định danh, 0 lọt tên, 0 lần đọc qua liên kết qua 1.349.659 vòng**; số fd trước = sau; câu báo 0 lần lộ đường dẫn.
- **Đối chứng trên bản cũ, cùng máy, cùng cách:** lọt nội dung 2.717/68.215 (root), 1.219/37.710 (`nobody`), tầng trên 2.599, tầng giữa 1.729, đọc qua liên kết 2.094 → cách thử **bắt được lỗi khi lỗi còn**. Test tráo thật 1,5 giây mới (`test_real_atomic_swap_race_never_leaks_outside_content_or_size`) hỏng 3/3 lần trên bản cũ, qua 5/5 trên T-079.
- Test cấu trúc khóa đúng tính chất mà Thợ Máy không giả lập được trên Windows ("thư mục đã mở vẫn là thư mục thật dù tên bị tráo", tầng trên và tầng giữa, đọc và `stat`). 8 file test liên quan trên Linux: 0 hỏng; SL-T063-1 → -5 qua không còn `xfail`; SL-T063-4 chạy thật trên ext4 phân biệt hoa thường: qua.
- Điểm phụ: cloud chạy Python 3.12.3 (máy Windows 3.12.15), `fs.protected_symlinks=0`: không ảnh hưởng (app không đi theo symlink nào; các hàm dùng không đổi giữa hai bản vá).

→ **SL-T063-2, -3 đóng trên Linux.** Mac đi đúng nhánh code của Linux (`openat`, `fstatat`, `O_NOFOLLOW`); chưa chạy trên Mac thật (xem Việc 5).

### Lỗi khác của phiếu

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| SL-T063-5 | Đóng | `_open_error`; test `test_open_error_message` ×4 qua (Windows); ca `posix_only` qua trên Linux |
| SL-T063-1 | Đóng (lỗi của test) | Test viết lại theo định danh, `assert` giữ nguyên; qua trên Windows và Linux |
| SL-T063-4 | Đóng | Gỡ `xfail`; qua trên thư mục tạm phân biệt hoa thường (Windows, Soi Lỗi) và ext4 (Linux) |
| **LC-T076-3** (= SL-T076-2) | **Đóng** | `drafts.py:943-953` so `file_id`; test của tôi `test_lc_t076_3_cached_listing_and_one_rename_on_case_sensitive_folder` và 2 ca SL-T076-2 nay qua (gỡ `xfail`, chỉ dòng xóa); 3 test mới (5 ca) của Thợ Máy kiểm bản sao khác định danh bị từ chối |

## Việc 3 · Xét SL-T079-1, SL-T079-L-1

- **SL-T079-1 → LC-T079-1, giữ Thấp, không nâng.** Ép thắng lọt thật (đã dựng lại, thêm ca thư mục trong gốc và đường xem thư mục), nhưng tráo thật trên Windows 0/8.208 vòng với đích anh em, cùng lý do Windows như SL-T063-2 (Thấp ở T-063). Không áp dụng Mac/Linux, nên không mở lại mức Cao. **Không chặn gộp** T-079, **không chặn** T-056. Sửa ở `folders.py` (cả `_scan_held`), phiếu dọn mới (Điều kiện 1).
- **SL-T079-L-1 → LC-T079-3, giữ Thấp.** Chỉ sai câu báo, an toàn; không chặn gì; sửa cùng phiếu dọn.

## Việc 4 · F1, F3 và các điểm riêng

| Điểm | Kết quả | Bằng chứng |
|---|---|---|
| Lớp chặn T-048, T-076 giữ | **Đạt** | Việc 1; test T-048 (`tests/test_images_folders_soi_loi.py`), T-076 (`tests/test_soi_loi_t076.py`, `tests/test_la_chan_t076.py`) qua; 3 `xfail` R2 cũ giữ nguyên |
| Không rò fd/handle | **Đạt** | Windows (`lc79_leak_perf.py leak`): 3.600 vòng × 8 lời gọi qua mọi nhánh (đọc được, không tìm thấy, file ẩn, quá cỡ, không hỏi được đường dẫn thật, ép thắng đích ngoài bị chặn, ép thắng đích anh em lọt): **chênh 0 handle**. Linux: fd trước = sau (Soi Lỗi), test `test_level_swapped_before_opening_is_refused_without_fd_leak` |
| Câu báo không lộ đường dẫn | **Đạt** | 0 lần trong mọi lượt tráo thật (Windows ≈44.000 lời gọi, Linux ≈4 triệu); mọi câu là hằng, ném `from None`; test `raises_safely`. LC-T079-2 là lộ **số liệu thô** của file ngoài, không phải đường dẫn |
| Không mở đường đọc mới ra ngoài gốc | **Đạt** | Mọi lần mở mới đi từ gốc đã `resolve` xuống bằng fd từng tầng (Mac/Linux) hoặc theo đường dẫn đã kiểm rồi kiểm lại bằng đường dẫn thật của handle (Windows; trừ LC-T079-1). `stat_image` Windows chỉ xin quyền thuộc tính (test `test_windows_stat_image_asks_attributes_only`); Drive thật không bị tải file (Thợ Máy, Soi Lỗi đo, chỉ đọc). Không có `open(`/`Path(` mới nhận đường dẫn từ người dùng |
| F3 | **Đạt** | Không ghi file, không `eval`/`pickle`/`yaml.load`; `ctypes` chỉ gọi API hệ điều hành với cờ cố định; ảnh đọc nhị phân (`os.fdopen(fd, "rb")`) |
| Hiệu năng | **Đạt** (không chậm rõ) | Bảng dưới |

**Đo tốc độ** (Windows, máy đang có 2 agent khác chạy; 60 KB/ảnh):

| Cách đo | `main` | T-079 |
|---|---|---|
| Tiến trình riêng, 300 ảnh, 3 lượt: 300 `stat_image` | 2,39 / 2,48 / 2,62 s | 3,41 / 3,48 / 3,25 s |
| … 300 `read_image_bytes` | 39,09 (lần đầu, phần mềm diệt virus quét) / 11,39 / 11,66 s | 12,90 / 13,46 / 14,20 s |
| **Cùng tiến trình, xen kẽ từng ảnh** (200 ảnh × 5 vòng, trung vị mỗi lần): `stat_image` | 5,97 ms | **7,01 ms** |
| … `read_image_bytes` | 32,52 ms | **33,12 ms** |

Tách nhỏ phần thêm của Windows: mở handle chỉ thuộc tính 0,19 ms, hỏi đường dẫn thật 0,22 ms (để so: `resolve` vốn có 0,78 ms). Cách đo xen kẽ loại được dao động do máy bận giữa các tiến trình: `stat_image` thêm **khoảng 1 ms mỗi ảnh**, đọc ảnh ngang nhau. `stat_image`/`read_image_bytes` chỉ chạy cho ảnh đã chọn hay đang xem (nháp vài chục ảnh: thêm vài chục ms), xem thư mục không đổi. Soi Lỗi đo trước đó khi máy rảnh hơn: cùng mức; Linux: +0,03 ms mỗi `stat`.

## Việc 5 · Có bỏ điều kiện "T-079 trước Mac/Linux" được chưa

**Được, khi T-079 đã gộp vào `main`.**

- **Linux:** SL-T063-2, -3 đóng bằng số đo thật (Việc 2). Các lỗi còn lại trên Linux là LC-T079-2, -3 (Thấp, chỉ câu báo).
- **Mac:** cùng nhánh code với Linux (`_OPEN_BY_DIR_FD`: `openat`, `fstatat` có từ macOS 10.10), nên SL-T063-2 đóng theo cấu trúc. Phần riêng của Mac **chưa chạy**: mã lỗi của `openat(O_DIRECTORY | O_NOFOLLOW)` trên symlink (code nhận cả ELOOP lẫn ENOTDIR, lỗi lạ thì coi là "vừa bị thay đổi"), APFS không phân biệt hoa thường và dạng Unicode, cờ ẩn `UF_HIDDEN`, tráo nguyên tử `renamex_np(RENAME_SWAP)`. Đây là **điều kiện cũ** (LC-T048-1, Lá Chắn T-063 điều kiện 3, T-076 điều kiện 4), không phải điều kiện mới của T-079: trước khi dùng app trên Mac, chạy bộ test thư mục ảnh trên máy Mac thật (Điều kiện 2).

## Việc 6 · Thử gộp

| Gộp | Kết quả |
|---|---|
| `origin/main` `8fc7dd3` (= `fa2cc39` + 3 commit chỉ tài liệu) | Không xung đột; code và test của cây gộp giống hệt nhánh (kết quả test nhánh áp dụng nguyên) |
| `main` trên máy chủ dự án `f722ea3` (chưa đẩy; **đã có T-039, T-069**) | `git merge-tree`: không xung đột. Cây gộp `775b19c` (worktree tạm, không đẩy, đã xóa) chạy 17 file test (14 file liên quan + 3 file T-039): **1962 passed, 38 skipped, 21 xfailed, 0 hỏng** (21 xfail = 18 như trên nhánh + 3 LC-T039-2 đã biết của T-039) |
| Nhánh đang làm `team/T-066`, `team/T-071` | Không đụng `folders.py`, `drafts.py`; `merge-tree` với T-079: không xung đột |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có bí mật; `detect-secrets` (PYTHONUTF8=1) 0 mục thật; lịch sử nhánh chỉ có chuỗi mồi "SECRET" trong test |
| S2 | Đạt | Câu báo là hằng, không đường dẫn, không xích lỗi hệ điều hành (0 lần lộ qua mọi lượt tráo); `ImageEntry.file_id` `repr=False` |
| S3 | Không áp dụng | Không thêm biến cấu hình |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Đạt | Module vẫn chỉ đọc (`O_RDONLY`, handle chỉ thuộc tính); test mới chỉ ghi trong thư mục tạm |
| W3 | Không áp dụng | Không có HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1–A3 | Không áp dụng | Không dựng prompt, không gọi AI; `file_id` không gửi đi đâu |
| U1–U3 | Không áp dụng | Không có giao diện, không đụng đăng nhập |
| F1 | **Đạt (có điều kiện)** | SL-T063-2, -3 đóng (Windows ép thắng + tráo thật; Linux 0/1.349.659). Còn LC-T079-1 (Thấp, Windows, chỉ khi ép thắng), LC-T079-2 (Thấp, câu báo) → Điều kiện 1 |
| F2 | Đạt | Giới hạn cỡ kiểm trên mục đã mở (`:888`, đọc `:944`); EXIF không liên quan |
| F3 | Đạt | Việc 4 |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi (so `fa2cc39` và `main` `f722ea3`); không import mới (chỉ `dataclasses.field`, thư viện chuẩn); pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi; script thử ở thư mục nháp, không commit |
| D3 | Đạt | Test mới chỉ dùng thư mục tạm, `_winapi.CreateJunction`; không gọi mạng |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (69 gói, `certifi==2026.10.19`, `pillow==13.0.0`) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có |
| bandit | `folders.py`, `drafts.py` bản `main` và bản T-079: cùng đúng 1 mục B101 (`assert`, `drafts.py:505`, có từ T-016, ngoài diff). **0 mục mới** | Có |
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trên thư mục riêng chứa 13 file của diff (có `tests/test_la_chan_t079.py`), patch `git diff fa2cc39` và 1 file mồi có chữ tiếng Việt: mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`), **0 mục ở file thật**. Đã xóa mồi | Có |
| Soát lịch sử git | `git log -p fa2cc39..HEAD \| grep -iE "api[_-]?key\|password\|secret\|token"`: 23 dòng, đều là dữ liệu mồi `SECRET` trong test và tên công cụ trong báo cáo | Có |
| pytest (nhánh) | 14 file: `tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_soi_loi_t079_linux.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_images_process.py tests/test_app_pages.py tests/test_la_chan_t079.py -rxX` (23/10, 07:35–07:39): **1467 passed, 38 skipped, 18 xfailed, 0 hỏng**. 18 xfail = 3 cũ (R2-1 ×2, R2-2) + 8 SL-T079-1 + 7 LC-T079 | Có |
| pytest (cây gộp `main` `f722ea3` + T-079) | 14 file trên + `tests/test_onpage_links.py tests/test_soi_loi_t039.py tests/test_la_chan_t039.py` (23/10, 7 phút 57 giây): **1962 passed, 38 skipped, 21 xfailed, 0 hỏng**. 21 xfail = 18 của nhánh + 3 LC-T039-2 (đã biết, biên bản Lá Chắn T-039) | Có: plugin in `__file__` cho thấy `folders.py`, `drafts.py` nạp từ cây gộp |
| pytest (bản sao có cách sửa) | 9 file thư mục ảnh, nháp: 722 passed, 25 skipped, 3 xfailed (R2 cũ), **đúng 15 XPASS(strict)** = 8 SL-T079-1 + 1 LC-T079-1 + 6 LC-T079-2; không hỏng gì khác | Có (plugin in `__file__`) |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check tests/test_la_chan_t079.py`: đã format | Có |

## Báo nhầm đã loại

- bandit B101 `drafts.py:505`: `assert` thu hẹp kiểu có từ T-016, ngoài diff, không phải kiểm tra an toàn.
- `git log` khớp "secret": chỉ chuỗi mồi trong test (`SECRET-NGOAI-GOC`) và tên công cụ `detect-secrets` trong báo cáo.
- "Tráo thật trên Windows 0 lọt nên LC-T079-1 không có thật": **loại**. Ép thắng lọt; lỗi nằm trong phép so của code, Windows chỉ cứu bằng tính chất hệ điều hành (như SL-T063-2 ở T-063). Xếp Thấp, không bỏ.
- "Bộ thử tráo thật lượt A, B cho 0 lọt nên an toàn": **không dùng làm bằng chứng chính** vì kẻ tấn công gần như không tráo được; bằng chứng là lượt C (tráo hàng trăm lần) + đối chứng dương + ép thắng.

## Ghi nhận (không thành lỗi)

- **Thư mục thật được dời vào gốc** (ca 8g của Soi Lỗi Linux): chương trình có quyền ghi vào thư mục cha của một thư mục khác dời hẳn thư mục đó vào chỗ `x` trong thư mục ảnh thì app đọc được file trong đó, vì lúc ấy nó **thật sự nằm trong** thư mục ảnh. T-079 đảm bảo "file đọc được nằm trong thư mục ảnh lúc mở, đến qua thư mục thật", không đảm bảo "chưa từng ở chỗ khác". Cùng loại hard link LC-T048-6; Thấp. Đề nghị ghi sổ rủi ro cạnh LC-T048-6 (Điều kiện 3).
- Mac/Linux: thư mục chỉ có quyền "đi qua" (`--x`) nay không đọc được ảnh bên trong (mở thư mục cần quyền đọc danh sách). Chặt hơn, khớp với quét.
- `_open_error` coi mọi lỗi lạ (EMFILE, EIO…) là "vừa bị thay đổi": câu chưa đúng nghĩa nhưng an toàn trước (không đi tiếp).
- Nhánh `else` của `_opened_stat`, `_open_image` giả định Windows; máy POSIX không có `openat` (macOS cũ hơn 10.10, không còn được hỗ trợ) sẽ báo lỗi thay vì lọt. Test `posix_only` trên Mac sẽ lộ ngay nếu xảy ra.
- `_is_link_stat` trên `os.fstat` của Windows không có tác dụng (mục Việc 1); không phải lỗ hổng vì còn `_win_handle_is_link` và so định danh.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **Phiếu dọn lỗi mới (Thợ Máy), trước khi hết Giai đoạn 3; không chặn gộp T-079, không chặn T-056.** Sửa LC-T079-1 (cả `_win_handle_at` lẫn `_scan_held`), LC-T079-2, LC-T079-3 trong `seo_app/images/folders.py` theo cách ở bảng lỗi; gỡ `xfail`: 8 ca SL-T079-1 (`tests/test_soi_loi_t079.py`), 7 ca LC-T079 (`tests/test_la_chan_t079.py`), 3 ca SL-T079-L-1 (`tests/test_soi_loi_t079_linux.py`, chỉ thấy XPASS trên Linux/Mac: cần lượt cloud Linux hoặc nhớ gỡ tay). Thử lại ổ Google Drive thật (chỉ đọc thuộc tính) và ổ mạng. Soi Lỗi + Lá Chắn rút gọn. Nếu chủ dự án chọn không sửa thì ghi sổ rủi ro: *"2026-10-23 — Đọc thư mục ảnh (T-079): trên Windows, thư mục 'anh em' tên trông y hệt thư mục ảnh vẫn qua phép so đường dẫn khi kẻ tấn công thắng cuộc đua tráo (LC-T079-1); câu báo lỗi có thể tả cỡ, loại một file ngoài thư mục ảnh khi bị tráo (LC-T079-2); câu báo 'không có quyền' thay 'vừa bị thay đổi' (LC-T079-3). Chấp nhận vì cuộc đua không thắng được trên thực tế trên Windows, câu báo chỉ người dùng app thấy. Lá Chắn T-079 xếp Thấp."*
2. **Mac (điều kiện cũ, giữ):** trước khi dùng app trên Mac, chạy trên máy Mac thật `tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_soi_loi_t079_linux.py tests/test_la_chan_t079.py tests/test_drafts_images.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py -rsxX` (các ca `posix_only` phải **chạy**, không bỏ qua), thêm ca khác hoa thường trên APFS của T-076. Điều kiện "T-079 trước khi chạy app trên Mac/Linux" của Lá Chắn T-063 **bỏ** khi T-079 đã gộp.
3. **Sổ rủi ro (chủ dự án quyết):** ghi ca "thư mục thật được dời vào gốc" cạnh LC-T048-6, ví dụ: *"2026-10-23 — Đọc thư mục ảnh (T-079, ca 8g của Soi Lỗi Linux): chương trình có quyền ghi vào thư mục cha của một thư mục khác dời hẳn thư mục đó vào trong thư mục ảnh thì app đọc được file trong đó (lúc ấy nó thật sự nằm trong thư mục ảnh). Chấp nhận vì muốn làm phải có quyền gần như chủ thư mục bị dời, cùng loại hard link LC-T048-6. Lá Chắn T-079 xếp Thấp."*
4. **Kiểm lại bằng Claude Fable sau 01/11** (biên bản này chạy tạm Opus 5.5).

## Thử độc lập của Lá Chắn (script ở thư mục nháp, không commit; bản sao ở thư mục ghi chú chung `T-079-la-chan-scripts/`)

| Script | Việc |
|---|---|
| `lc79_forced.py <code>` | Ép thắng 7 kiểu đích (bảng Việc 2) |
| `lc79_race.py` (`LC79_CODE=<code>`; `--mode rename\|fsctl --target ngoai\|twin --app-threads N --attacker-procs M --pause-ms --widen-ms`) | Tráo thật bằng tiến trình riêng, đối chứng dương |
| `lc79_attacker_alone.py <giây>` | Tốc độ tráo khi không có app |
| `lc79_leak_perf.py leak <code>` / `perf <main> <t079>` | Rò handle; tốc độ theo tiến trình riêng |
| `lc79_perf2.py <folders.py main> <folders.py t079>` | Tốc độ xen kẽ trong cùng tiến trình, tách nhỏ phần thêm |
| `lc79_junction_self.py <code>`, `lc79_symlink_probe.py <code>` | Đường dẫn thật khi mở chính junction; symlink file (không tạo được: lỗi 1314) |
| `code_fix_seo_app_images/folders.py` (bản sao `folders.py` có cách sửa LC-T079-1, -2: `_win_same_path`, `_confirm_checked`) | Chứng minh cách sửa đóng được lỗi, không hỏng test khác (chạy bằng `PYTHONPATH=<thư mục chứa seo_app>` + plugin `lc_where.py` in nơi nạp module) |
| `race1.log`, `race2.log`, `race3.log` | Kết quả tráo thật lượt A, B, C |

`code_main` = `git archive fa2cc39 seo_app`, `code_t079` = `git archive 089d115 seo_app` (`seo_app/` giống hệt `6e84375`). Mọi file thử nằm trong thư mục tạm riêng, file "bí mật" là mồi tự tạo; không đọc file thật nào của máy, không đụng ổ Google Drive.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 3 Thấp (LC-T079-1 = SL-T079-1 mở rộng sang đường xem thư mục; LC-T079-2 mới: câu báo tả file ngoài gốc khi bị tráo; LC-T079-3 = SL-T079-L-1). Bản vá đúng: SL-T063-2, -3 (Cao trên Mac/Linux) đóng (Windows: ép thắng đích thường bị chặn, tráo thật 0/14.749 vòng; Linux: 0/1.349.659 vòng, bản cũ lọt hàng nghìn); SL-T063-1, -4, -5 và LC-T076-3 đóng. F1, F3 đạt: lớp chặn T-048, T-076 giữ nguyên, không rò handle, câu báo không lộ đường dẫn, không mở đường đọc mới ra ngoài gốc, không chậm rõ. **Gộp `main` được ngay** (không xung đột với `origin/main` lẫn `main` đã có T-039, T-069); T-056 làm tiếp được. Bỏ điều kiện "T-079 trước Mac/Linux" khi đã gộp; Mac vẫn chạy bộ test trên máy thật trước khi dùng.

Lá Chắn không sửa code ứng dụng; chỉ thêm `tests/test_la_chan_t079.py` (10 ca, 7 `xfail(strict=True)`) và biên bản này. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

# Báo cáo T-080 · Dọn 3 lỗi Thấp đọc ảnh sau T-079 (LC-T079-1, -2, -3) · Soi Lỗi (phần Windows)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-080](../tickets/T-080-don-loi-thap-doc-anh-sau-t079.md) · mức kiểm **rút gọn**, phần **Windows**. Phần Linux: báo cáo `docs/team/reports/T-080-soi-loi-linux.md` trên nhánh `team/T-080-linux` (`133774c`), tôi chỉ đọc để đối chiếu, không gộp |
| Ngày nộp | 2026-10-23 |
| Máy kiểm | **Windows 11 Pro 10.0.26300**, Python 3.12.15 (uv 0.13.4), người dùng thường, NTFS cục bộ (đã bật đường dẫn dài) và ổ chia sẻ `\\localhost\C$`. Máy đang chạy song song toàn bộ pytest của Chỉ Huy và agent khác. Ổ Google Drive, USB của chủ dự án: **không thử lại** (Thợ Máy đã làm, chủ dự án chỉ đồng ý mức chỉ đọc thuộc tính) |
| Mã nguồn | Nhánh `team/T-080` tại `3aca3c0` (gốc `main` `417efea`, đã có T-079). Đối chứng: bản sao `git archive 417efea seo_app`. Tôi thêm `tests/test_soi_loi_t080.py` (commit `d597805`, `5ac610b`) |
| Kết quả | Hoàn thành phần Windows. **Kết luận: ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới** (SL-T080-1, SL-T080-2: chỉ sai câu báo, có từ trước T-080); xác nhận **SL-T080-L-1** của lượt Linux **cũng xảy ra trên Windows**. **Chuyển Lá Chắn rút gọn được** |

## Tóm tắt (cho chủ dự án)

Ba lỗi nhỏ Lá Chắn để lại sau T-079 **đã được sửa đúng** trên Windows. Tôi dựng lại phép "ép kẻ tấn công luôn thắng" của Lá Chắn và làm rộng hơn (gõ tên ảnh khác chữ hoa/thường, đánh lừa cả bước hỏi tên trên ổ, tráo ở tầng trên, file bên ngoài quá lớn/rỗng/là thư mục): bản trước T-080 để lọt nội dung, cỡ, tên file bên ngoài và báo những câu kiểu "Ảnh quá lớn (5,0 MB)" về file bên ngoài; **bản T-080 chặn hết 380/380 ca**.

Tôi còn cho một chương trình khác tráo thư mục thật liên tục: bản trước T-080 **đọc được file bên ngoài 61 lần** khi thư mục "anh em" có tên trông y hệt (một chữ K đặc biệt), tức lỗ hổng này **không chỉ là lý thuyết** như ta tưởng ở T-079. Bản T-080, cùng cách thử, hơn 21.000 lần tráo, 86.000 vòng đọc/kiểm/xem: **không lần nào lọt nội dung, cỡ hay tên**, không câu báo nào tả file bên ngoài hay lộ đường dẫn trên máy.

Dùng bình thường không thấy gì khác: thư mục, ảnh tên tiếng Việt (kể cả kiểu gõ dấu khác nhau), tên dài, chữ hoa/thường lẫn lộn, gõ tên khác chữ hoa/thường đều đọc được, kết quả **giống hệt** bản cũ trên ổ máy và ổ mạng; tốc độ như cũ.

Tôi tìm thêm **2 lỗi nhỏ (Thấp), có từ trước, không chặn**: khi thư mục vừa bị dời đi đúng lúc app đọc (thường là lúc bị tráo), app đôi khi báo "Không đọc được… (không có quyền hoặc ổ đĩa vừa bị ngắt)" thay vì "vừa bị thay đổi, hãy thử lại". Lỗi câu báo lượt Linux tìm ra ("nằm ngoài thư mục ảnh" thay "vừa bị thay đổi") cũng xảy ra trên Windows. Cả ba chỉ sai câu chữ, vẫn an toàn; nên gom vào một phiếu dọn sau, hoặc ghi nhận.

## Phạm vi và cách kiểm

Diff `git diff 417efea..3aca3c0`: `seo_app/images/folders.py` (+98/−37), `tests/test_images_folders.py` (+188/−1, 51 ca), `tests/test_soi_loi_t079.py`, `tests/test_la_chan_t079.py` (chỉ gỡ `xfail`), báo cáo Thợ Máy. Tôi:

1. Đọc toàn bộ diff và so **thân từng hàm** (AST, bỏ docstring) giữa `main` và T-080.
2. Ép thắng trên Windows (`sl80_forced_win.py`): 6 đích × 2 tầng × 4 loại file ngoài × 4 kiểu ép × đọc/`stat`, thêm xem thư mục; chạy trên cả `main` và T-080.
3. Tráo thật bằng **tiến trình riêng**, 3 luồng app (`sl80_race_win.py`), đếm lọt nội dung, cỡ, tên, câu tả file ngoài, câu "không có quyền", lộ đường dẫn, lỗi lạ, handle; đối chứng dương LC-T048-2.
4. Không chặn oan và tốc độ: cùng tiến trình, xen kẽ `main`/T-080 (`sl80_perf_same.py`), ổ máy và ổ mạng.
5. Soát test: 2 file chỉ gỡ `xfail` (so AST), 51 ca mới.
6. Lỗi mới: `tests/test_soi_loi_t080.py`, `xfail(strict=True)`.

Script ở thư mục ghi chú chung của nhóm phiên, `T-080-soi-loi-scripts/` (không commit). Mọi file thử nằm trong thư mục tạm riêng, file "bí mật" là mồi tự tạo.

## Xác nhận từng lỗi đã sửa

So AST hàm giữa `main` và T-080: **đổi** `_win_handle_at`, `_Scan._scan_held`, `_resolve_inside`, `_checked_file`, `_opened_stat`, `stat_image`, `read_image_bytes`; **thêm** `_same_win_path`, `_changed_while_resolving`, `_check_file`; **bỏ** `_path_key`; **giữ nguyên** mọi lớp chặn cũ (`_parse_rel`, `_is_safe_name`, `_disk_names`, `_found_names`, `_listed_names`, `_match_disk_name`, `_posix_open_dir`, `_open_error`, `_open_image`, `_win_open`, `_win_hold_dir`, `_win_handle_is_link`, `_win_final_path`, `_win_listed_name`, `_is_link_stat`, `_Scan._scan_by_fd`, `_read_entries`, `_visit`…). Khớp báo cáo Thợ Máy.

### LC-T079-1 (= SL-T079-1): so đường dẫn thật từng chữ — **đã sửa**

- `_same_win_path` (`seo_app/images/folders.py:387-405`) so **từng chữ**, chỉ bỏ tiền tố `\\?\`, `\\?\UNC\` và dấu `\` cuối. Dùng ở `_win_handle_at` (`:353-363`, tức `_opened_stat` `:935` và `_open_image` `:977`) và `_scan_held` (`:1114`). `_path_key` (NFC + `casefold`) đã bỏ.
- Đọc ảnh Windows: `resolve` không trả đúng `gốc/chữ đã gõ` thì hỏi tên trên ổ (`:996-998`) rồi mở và so theo tên đó, nên `ref` gõ khác hoa thường vẫn đọc được mà phép so vẫn chặt.
- **Ép thắng** (bảng dưới): T-080 chặn mọi đích anh em (NFD, dấu Kelvin, `ß`, khác hoa thường trên thư mục bật phân biệt hoa thường) và thư mục NFD trong gốc, ở cả đọc, `stat`, xem thư mục; `main` lọt.
- **Tráo thật** (bảng dưới): `main` **lọt nội dung 61 lần** với đích anh em dấu Kelvin (39/2.783 vòng và 22/3.160 vòng; lượt thứ ba 0/1.154). Đường lọt: `x` là junction lúc `lstat` ảnh và lúc `resolve`; `is_relative_to` của Python so theo chữ thường (`K` U+212A viết thường thành `k`), nên `_resolve_inside` chấp nhận đường dẫn trong thư mục anh em; bản cũ **mở thẳng đường dẫn `resolve` trả** (không cần thắng lúc mở), so đường dẫn thật bằng `_path_key` (gộp hoa thường) nên qua, và định danh của file mở ra trùng `lstat` (cũng đi xuyên junction). T-080 không mở theo đường dẫn đó nữa: **0 lọt / 15.375 vòng**, cùng đích. Lá Chắn T-079 chỉ tráo thật với đích NFD (bị `is_relative_to` chặn) nên đo 0; **LC-T079-1 trên bản cũ thắng được ngoài thực tế**, không chỉ khi ép. Tôi thêm test tất định cho đúng đường này (`test_kelvin_sibling_seen_by_lstat_and_resolve_is_not_opened`: `main` hỏng ở ca đọc, T-080 qua).

### LC-T079-2: câu báo không tả file ngoài thư mục ảnh — **đã sửa**

- `_checked_file` (`:837-855`): `lstat` qua thì đi tiếp như cũ; hỏng thì lấy lại mục trong thư mục ảnh (`_disk_names` + `_opened_stat`, phải cùng định danh, không thì "Ảnh vừa bị thay đổi…") rồi báo theo **mục đó** (`_check_file` `:857-863`). Câu báo ném ngoài khối bắt lỗi, không xích lỗi.
- Ép thắng: 228 ca file ngoài quá lớn / rỗng / là thư mục: `main` báo **204** câu tả file ngoài ("Ảnh quá lớn (5,0 MB), tối đa 1,0 MB.", "File ảnh rỗng (0 byte).", "Đây không phải là file ảnh."); T-080: **0** (mọi ca "Ảnh vừa bị thay đổi…"), kể cả khi `ref` gõ chữ hoa và khi ép cả bước hỏi tên trên ổ.
- Ảnh có vấn đề thật vẫn báo đúng: `test_problem_of_image_inside_folder_is_still_described` (Thợ Máy, cả `ref` gõ chữ hoa) qua; tôi đọc thêm nhánh mục là thư mục, file ẩn: đúng.

### LC-T079-3 (gồm SL-T079-L-1): "vừa bị thay đổi" thay "không có quyền" — **đã sửa ở `resolve`**

- `_changed_while_resolving` (`:443-461`), dùng ở `:660-663`: `RuntimeError`, ELOOP, EINVAL, ENOTDIR (Mac/Linux) và lỗi Windows 1921 → `_ChangedError`; Windows xét theo mã lỗi Windows (`winerror`), lỗi Windows khác (ổ mạng, ổ vừa rút) giữ "Không đọc được…". Đúng ý phiếu. 24 ca `test_resolve_error_after_checked_levels` kiểm đủ các nhánh.
- Linux thật: lượt cloud đo 0 câu "không có quyền" khi bị tráo, 3 ca SL-T079-L-1 XPASS (báo cáo Linux).
- **Trên Windows khi tráo thật vẫn còn câu "Không đọc được… (không có quyền…)"** ở chỗ khác `resolve` (`_opened_stat`, `_read_entries`) và ở `resolve` gặp lỗi 5 (junction đang bị xóa): xem SL-T080-1, SL-T080-2. Không phải lỗi của cách sửa (phiếu chỉ giao `resolve`), nhưng cùng loại.

### Nhánh Mac/Linux (đọc code, không chạy được ở máy này)

- `_checked_file` khi kiểm hỏng: `_listed_names` (mở thư mục từng tầng `O_NOFOLLOW`, đọc tên bằng fd), `lstat` lại theo tên, so định danh; `_opened_stat` mở thư mục cha từng tầng rồi `stat(..., dir_fd, follow_symlinks=False)`, so `(st_dev, st_ino)`. Câu báo chỉ tả mục nằm trong thư mục ảnh. Đúng.
- `_changed_while_resolving`: trên Mac/Linux không đụng `exc.winerror` (chỉ đọc khi `os.name == "nt"`), xét `errno`. `read_image_bytes`: điều kiện hỏi lại tên có `not _OPEN_BY_DIR_FD` nên Mac/Linux không thêm bước nào; `_open_image` đi `dir_fd` như T-079 (`path` không dùng).
- `stat_image`: kiểm file thường / ẩn / cỡ chuyển từ `_opened_stat` ra ngay sau nó, cùng ý nghĩa.
- Đối chiếu lượt Linux thật: 3.422.839 vòng tráo, 0 lọt, 0 câu tả file ngoài, 0 câu "không có quyền"; 31 ca T-080 chạy được trên Linux qua.

## Thử trên Windows

### Ép kẻ tráo "luôn thắng" (`sl80_forced_win.py`, mở rộng từ `lc79_forced.py` của Lá Chắn T-079)

Mỗi ca: gốc có ảnh mồi `x/bi-mat.jpg` (hoặc `a/b/bi-mat.jpg`: tráo tầng trên); tầng bị tráo thành junction trỏ vào đích đúng lúc app gọi bước bị ép. Kiểu ép: `lstat-open` (lúc `lstat`, mở, mở handle thuộc tính mục ảnh: đúng phép Lá Chắn), `+findfirst` (thêm lúc hỏi tên trên ổ), `go-hoa` (như trên, `ref` gõ CHỮ HOA: đi nhánh hỏi lại tên khi đọc, mới ở T-080), `resolve` (chỉ lúc `resolve`). File ở đích: bí mật / 5 MB (giới hạn 1 MB) / rỗng / là thư mục. Thêm xem thư mục `x/y` (junction từ lúc giữ thư mục tới hết lúc đọc danh sách, như test LC-T079-1). 396 ca mỗi bản, 380 ép được (16 ca `go-hoa` trên thư mục phân biệt hoa thường dừng ở "Không tìm thấy" trước khi tới bước bị ép, đúng).

| Đích | `main` 417efea (66 ca/đích): lọt nội dung · cỡ · tên · qua liên kết · câu tả file ngoài | **T-080** |
|---|---|---|
| Ngoài gốc, tên thường | 0 · 0 · 0 · – · **36** | **0 · 0 · 0 · – · 0** (66/66 từ chối) |
| Anh em, tên NFD | **6 · 6 · 1** · – · **36** | **0** (66/66 từ chối) |
| Anh em, dấu Kelvin | **6 · 6 · 1** · – · **36** | **0** (49 từ chối, 17 ra ảnh mồi) |
| Anh em, `ß` thay `ss` | **6 · 6 · 1** · – · **36** | **0** (66/66 từ chối) |
| Anh em khác hoa thường (thư mục bật phân biệt hoa thường; 50 ca ép được) | **4 · 4 · 1** · – · **24** | **0** (33 từ chối, 17 ra ảnh mồi) |
| Thư mục khác trong gốc, tên NFD | – · – · – · **13** · **36** | **0** (49 từ chối, 17 ra ảnh mồi) |
| **Cộng** | **22 · 22 · 4 · 13 · 204** | **0 · 0 · 0 · 0 · 0** |

- "Ra ảnh mồi" trên T-080: kiểu ép `resolve` với đích Kelvin / khác hoa thường / NFD trong gốc. `resolve` trả đường dẫn trong thư mục anh em (`is_relative_to` so chữ thường, `_name_key` gộp hoa thường, dạng Unicode: lớp T-048 giữ nguyên) nhưng T-080 không mở theo đường dẫn đó (hỏi lại tên trên ổ, mở `gốc/tên`) nên đọc ra đúng ảnh mồi. Đúng.
- Kiểu ép `resolve` với đích ngoài gốc / NFD / `ß`: "Đường dẫn nằm ngoài thư mục ảnh được phép." (51 ca, cả hai bản): **SL-T080-L-1 phần Windows**.
- 0 câu báo lộ đường dẫn tạm, `ngoai`, `SECRET`; sau mỗi ca thư mục trở lại nguyên trạng (380/380).

### Tráo thật bằng tiến trình riêng (`sl80_race_win.py`)

Một tiến trình riêng liên tục: đổi tên `x` (có ảnh mồi) đi, đặt junction `x` trỏ tới đích, gỡ, trả tên. 3 luồng app gọi liên tục `read_image_bytes`, `stat_image`, `list_folder(0, "x")` (mỗi vòng 3 lời gọi). 20 giây mỗi lượt; một số lượt nới khe 2 ms trước mỗi `lstat`/mở mục ảnh và nghỉ 1 ms (như máy bận), hoặc `ref` gõ CHỮ HOA.

| Đích (lượt) | `main`: lần tráo · vòng · **lọt nội dung · cỡ · tên** | **T-080**: lần tráo · vòng · **lọt nội dung · cỡ · tên** |
|---|---|---|
| Ngoài gốc, tên thường | 2.256 · 9.143 · 0 · 0 · 0 | 15 · 4.708 · 0 · 0 · 0 (2 lượt; kẻ tráo gần như không tráo được, không dùng làm bằng chứng chính) |
| Ngoài gốc, `ref` gõ chữ hoa | 1.966 · 7.568 · 0 · 0 · 0 | 2.414 · 8.670 · **0 · 0 · 0** |
| Anh em NFD | 2.336 · 9.282 · 0 · 0 · 0 | 2.395 · 9.350 · **0 · 0 · 0** |
| Anh em NFD, `ref` gõ chữ hoa | 2.056 · 7.950 · 0 · 0 · 0 | 1.703 · 6.443 · **0 · 0 · 0** |
| Anh em NFD, nới khe | 129 · 1.590 · 0 · 0 · 0 | 2.537 · 6.716 · **0 · 0 · 0** |
| **Anh em dấu Kelvin** (3 lượt) | 1.081 · 7.097 · **61** · 0 · 0 | 2.927 · 15.375 · **0 · 0 · 0** |
| Anh em `ß` | 2.308 · 9.157 · 0 · 0 · 0 | 2.338 · 9.246 · **0 · 0 · 0** |
| Ngoài gốc, file 5 MB (giới hạn 1 MB) | 2.205 · 8.869 · 0 · 0 · 0 | 2.174 · 8.704 · **0 · 0 · 0** |
| … nới khe | 1.794 · 4.918 · 0 · 0 · **1** (LC-T048-3, đã biết) | 3.045 · 7.209 · **0 · 0 · 0** |
| Ngoài gốc, file rỗng | 123 · 2.408 · 0 · 0 · 0 | 281 · 2.583 · **0 · 0 · 0** |
| Ngoài gốc, là thư mục | 1.585 · 6.363 · 0 · 0 · 0 | 1.712 · 7.085 · **0 · 0 · 0** |
| **Cộng** | 13 lượt, 17.839 lần tráo, 74.345 vòng: **lọt nội dung 61, lọt tên 1** | **14 lượt, 21.541 lần tráo, 86.089 vòng (258.267 lời gọi): 0 lọt nội dung, 0 lọt cỡ, 0 lọt tên** |

- T-080: **0 câu báo tả file ngoài** (cả lượt file ngoài quá lớn, rỗng, là thư mục), **0 câu lộ đường dẫn**, **0 lỗi xích lỗi hệ điều hành**, **0 lỗi lạ** (không phải `ImageFolderError`); sau khi dừng tráo app đọc đúng ảnh mồi (14/14). Handle tiến trình chênh như `main` (luồng, ống của tiến trình con).
- Lọt tên 1 lần trên `main` (lượt nới khe): nhánh dự phòng khi không giữ được thư mục (lỗi 32 lúc kẻ tráo đang đổi tên `x`), "tráo rồi tráo lại" quanh `scandir` = **LC-T048-3** (đã biết, mã T-048, T-080 không đổi). T-080 không gặp trong các lượt này nhưng cùng mã nên cùng khả năng.
- **Đối chứng dương** (bật/tắt junction tại chỗ trên `x` rỗng, LC-T048-2, 4 luồng, 15 s): `main` lọt **107** tên / 18.011 vòng, T-080 **77** / 17.706: bộ đếm bắt được lọt thật; đây là LC-T048-2 đã biết (`xfail` R2-1), không đổi ở T-080.
- Phân bố câu báo của T-080 khi bị tráo (gộp 14 lượt): "Không tìm thấy…" 173.220; "liên kết tắt" 17.892; "Thư mục vừa bị thay đổi" 6.884; "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)" 2.174; "Ảnh vừa bị thay đổi" 461; **"Đường dẫn nằm ngoài thư mục ảnh" 12.416, "tên ngắn hoặc tên khác" 2.281 (SL-T080-L-1)**; **"Không đọc được… (không có quyền hoặc ổ đĩa vừa bị ngắt)" 2.317 (SL-T080-1, -2)**. `main` cùng phân bố (1.837 câu "Không đọc được").

## Không chặn oan, tốc độ, handle

### Kết quả giống `main` (`sl80_perf_same.py`, cùng tiến trình)

Cây thử 300 ảnh 60 KB, 3 tầng, 12 thư mục: gốc tên có dấu dạng NFD; thư mục `Cổng sắt Tân Phú` (NFC), `Cửa kéo Thủ Đức` (NFD), tên dài 71 ký tự, `CongAI Mixed-Case`; thư mục con `Trước`, `sau khi hàn` (NFD), `IMG DIR`; tên ảnh có dấu NFC/NFD, `.jpg/.JPG/.png/.webp`. Mỗi thư mục `list_folder` (gõ đúng và gõ chữ hoa), cả cây, mỗi ảnh `stat_image` và `read_image_bytes` với `ref` theo danh sách / gõ CHỮ HOA / gõ chữ thường; gốc gõ đúng / chữ thường / chữ hoa.

| Ổ | Phép kiểm | Giống `main` | T-080 báo lỗi |
|---|---|---|---|
| NTFS cục bộ | 5.505 | **5.505** | **0** |
| Ổ mạng `\\localhost\C$` (120 ảnh) | 2.265 | **2.265** | **0** |

Test giữ lại: `test_normal_folders_are_read_listed_and_checked` (gốc gõ 3 kiểu), `test_ref_typed_in_other_case_reads_by_disk_names`.

### Tốc độ (xen kẽ từng ảnh `main` / T-080, trung vị, 5 vòng; máy đang bận)

| Việc | NTFS lượt 1 | NTFS lượt 2 | Ổ mạng (3 vòng) |
|---|---|---|---|
| `stat_image` | 8,01 / 8,53 ms | 4,70 / 4,64 ms | 22,15 / 21,30 ms |
| `read_image_bytes` | 35,92 / 36,36 ms | 15,99 / 16,02 ms | 39,86 / 39,54 ms |
| `list_folder` (25 ảnh) | 12,46 / 10,99 ms | 6,92 / 6,93 ms | 17,40 / 17,58 ms |
| `read_image_bytes`, `ref` gõ chữ hoa | 35,04 / 39,82 ms | 16,29 / 17,42 ms | 40,40 / 47,33 ms |

Ngang nhau. Chỉ đọc với `ref` gõ khác tên trên ổ chậm thêm khoảng 1 ms (ổ máy) đến 7 ms (ổ mạng, 3 tầng): bước hỏi lại tên từng tầng, đúng thiết kế (Thợ Máy ghi nhận; `ref` của app lấy từ danh sách nên hiếm gặp).

### Không rò handle (`sl80_leak.py`)

2.000 vòng × 12 lời gọi (đọc, `stat`, xem; `ref` gõ chữ hoa; ảnh quá lớn, rỗng, là thư mục, không có; đường dẫn thật của handle khác hoa thường bị từ chối ở cả đọc, `stat`, xem): handle **165 → 166** ở cả `main` lẫn T-080. T-080 từ chối đủ 8.000 lần tên khác hoa thường; `main` nhận cả (so lỏng).

## Soát test

### 2 file chỉ gỡ `xfail`

So AST của `tests/test_soi_loi_t079.py`, `tests/test_la_chan_t079.py` giữa `417efea` và T-080 sau khi bỏ định nghĩa `SL_T079_1`, `LC_T079_1`, `LC_T079_2` và đối số `marks=` của bản cũ: **giống hệt** bản mới. Diff chỉ có dòng xóa và dòng `pytest.param(...)` bỏ `marks=` (ruff gộp dòng). Dấu Kelvin U+212A của ca `anh-em-dau-kelvin` còn nguyên (`ascii()` cho `"Kho"`). 8 + 7 ca nay qua.

### 51 ca mới trong `tests/test_images_folders.py`

| Test (dòng) | Số ca | Kiểm đúng ý? |
|---|---|---|
| `test_same_win_path_compares_every_character` (`:1480`) | 9 | Có: tiền tố đường dẫn dài, UNC, gốc ổ đĩa, dấu `\` cuối; 4 kiểu tên anh em và thư mục khác đều **không** trùng |
| `test_windows_final_path_in_lookalike_folder_is_refused` (`:1496`) | 12 | Có: giả đường dẫn thật của handle nằm trong thư mục anh em (4 kiểu) ở cả 3 chỗ so (đọc, `stat`, xem). Giả lập; ca junction thật ở `test_soi_loi_t079.py`, `test_la_chan_t079.py` |
| `test_windows_ref_typed_in_other_case_opens_by_disk_names` (`:1541`) | 2 | Có: không chặn oan trên NTFS và ổ trả lại chữ đã mở (giả Google Drive) |
| `test_problem_of_image_inside_folder_is_still_described` (`:1555`) | 2 | Có: ảnh quá lớn, rỗng, là thư mục trong gốc vẫn báo đúng, cả `ref` gõ chữ hoa |
| `test_problem_seen_only_by_path_lstat_is_reported_as_changed` | 2 | Có: `lstat` thấy quá cỡ, mục lấy lại dùng được → "vừa bị thay đổi", không nói cỡ |
| `test_resolve_error_after_checked_levels` (`:1617`) | 24 | Có: 8 loại lỗi × 3 lời gọi; ca lỗi Windows 59 bắt đúng đột biến "xét theo `errno`" |

Đếm: 9 + 12 + 2 + 2 + 2 + 24 = **51**; 20 ca chỉ Windows, 31 ca chạy cả Mac/Linux (khớp Thợ Máy và lượt Linux).

## Lỗi mới

Test trong `tests/test_soi_loi_t080.py`, `xfail(strict=True)`. Chạy `--runxfail`: 10 ca hỏng đúng ở câu kiểm (`assert 'không có quyền' not in 'Không đọc được…'`, `assert 'thay đổi' in 'Đường dẫn nằm ngoài thư mục ảnh được phép.'` / `… 'tên ngắn hoặc tên khác…'`).

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T080-1 | **Thấp** (Windows; chỉ sai câu báo, an toàn; có từ T-079) | Windows coi mọi lần mở handle hỏi thuộc tính hỏng là "không có quyền": `_win_open` trả `None` (mất mã lỗi), `_opened_stat` báo "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." kể cả lỗi 3 (thư mục chứa ảnh vừa bị dời đi sau khi kiểm). T-080 còn đi qua bước này ở nhánh báo lỗi mới của `_checked_file`. Thêm: `resolve` gặp lỗi 5 (junction đang bị xóa) cũng ra câu này (Thợ Máy cố ý giữ: không phân biệt được với lỗi quyền thật chỉ bằng mã lỗi) | `folders.py:930-933` (`_opened_stat`), `:288-310` (`_win_open`), `:660-663` | (1) Tất định: `test_sl_t080_1_folder_moved_before_attribute_handle_is_not_permission_error` ×3 (`stat_image` ảnh thường, ảnh quá cỡ; `read_image_bytes` ảnh quá cỡ: `x` bị dời đi đúng lúc mở handle). (2) Tráo thật T-080: 1.139 lần ở `_opened_stat` (đo mã lỗi: 3), 138 lần ở `resolve` (mã lỗi 5); `main` cùng mức (1.077 và 114) | "Ảnh vừa bị thay đổi…" hoặc "Không tìm thấy…" (bản Mac/Linux của bước này báo "Không tìm thấy") | "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." |
| SL-T080-2 | **Thấp** (Windows; chỉ sai câu báo; có từ T-048) | Xem thư mục khi không giữ được thư mục (lỗi 32: kẻ tráo, hay chương trình khác đang đổi tên nó) thì đi nhánh dự phòng: kiểm đường đi rồi `scandir` theo tên; thư mục vừa bị dời đi thì `_read_entries` báo "Không đọc được thư mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." | `folders.py:1120-1127` (`_scan_held` dự phòng), `:1132-1137` (`_read_entries`) | (1) `test_sl_t080_2_folder_moved_before_listing_is_not_permission_error` (giả `_win_open` không giữ được như lỗi 32, dời `x` đúng lúc `scandir`). (2) Tráo thật T-080: 1.039 lần (mã lỗi 3 khi `scandir`); `main` 645 | "Thư mục vừa bị thay đổi…" hoặc "Không tìm thấy…" | "Không đọc được thư mục này (không có quyền hoặc ổ đĩa vừa bị ngắt)." |
| SL-T080-L-1 (lượt Linux; **phần Windows**) | **Thấp** (như lượt Linux; có từ T-048) | Vòng `lstat` vừa thấy `x` là thư mục thật, `resolve(strict=True)` đi trọn qua `x` lúc nó là junction (hay lúc handle của `resolve` đang mở thì `x` bị đổi tên): ra ngoài gốc → "Đường dẫn nằm ngoài thư mục ảnh được phép."; ra mục khác trong gốc → "Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục)." | `folders.py:664-665`, `:669-673` | (1) `test_sl_t080_l_1_windows_swap_during_resolve_is_reported_as_changed` ×6 (đọc, `stat`, xem × junction ra ngoài / tới `y` trong gốc) + 6 ca đối chứng qua (từ chối an toàn, không lộ gì). (2) Tráo thật T-080: 12.416 lần "nằm ngoài", 2.281 lần "tên ngắn…"; ép `resolve`: 51 ca | "Thư mục vừa bị thay đổi…" | Hai câu trên. Trên Windows `_MSG_ALIAS` còn nghĩa thật (tên ngắn 8.3), nên chỉ đổi khi định danh của `resolve` khác mục `lstat` vừa thấy |

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Cả ba lỗi: không đọc, không trả số liệu, không lộ đường dẫn; chỉ làm người dùng hiểu sai nguyên nhân khi đang bị tấn công hoặc khi thư mục vừa bị dời đi (đồng bộ Drive, người dùng đổi tên trong lúc app đang đọc).

**Cách sửa gợi ý (Thợ Máy cân nhắc, không bắt buộc ở phiếu này):**
- SL-T080-1: `_win_open` trả kèm mã lỗi (`ctypes.get_last_error()`); lỗi 2, 3 ở `_opened_stat` → `_ChangedError` (mục vừa được kiểm). Lỗi 5 của `resolve`: kiểm lại vòng `lstat`; tầng nào biến mất hay thành liên kết thì "vừa bị thay đổi", còn nguyên thì giữ "Không đọc được".
- SL-T080-2: trong nhánh dự phòng của `_scan_held`, `scandir` báo `FileNotFoundError` → `_ChangedError`. Gọn nhất là sửa cùng LC-T048-2, -3 (liệt kê qua chính handle đang giữ), khi đó nhánh này gần như không còn.
- SL-T080-L-1 (Windows): sau `resolve`, nếu ra ngoài gốc → `_ChangedError` (vòng `lstat` vừa thấy không tầng nào là liên kết); nếu tên khác: `lstat(resolved)` khác định danh mục cuối vừa thấy → `_ChangedError`, cùng định danh (tên 8.3) → giữ `_MSG_ALIAS`.

## Ghi nhận (không thành lỗi)

- `_resolve_inside` (mã T-048, giữ nguyên) vẫn chấp nhận đường dẫn `resolve` nằm trong thư mục anh em dấu Kelvin / khác hoa thường, hay thư mục NFD khác trong gốc (`is_relative_to` so chữ thường, `_name_key` gộp hoa thường và dạng Unicode). Đây chính là đường lọt thật của bản cũ. T-080 không còn mở theo đường dẫn này (chỉ dùng để quyết có hỏi lại tên), số liệu lấy từ vòng `lstat` và mục mở theo tên trên ổ, so đường dẫn thật từng chữ: ép `resolve` ra ảnh mồi, tráo thật 0 lọt. Nếu sau này có code mới dùng `path` mà `_checked_file` trả, phải nhớ điều này (đề nghị Lá Chắn xem có nên ghi chú vào docstring của `_resolve_inside`).
- Câu "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)." khi tráo (2.174 lần): câu có sẵn, nêu cả hai nguyên nhân, không sai.
- LC-T048-2 (R2-1), LC-T048-3: còn nguyên như trước (đối chứng dương, 1 lọt tên trên `main`). Không thuộc T-080.

## Bằng chứng

Máy Windows 11 Pro 10.0.26300, Python 3.12.15, worktree `wt-T-080`, nhánh `team/T-080` (code `3aca3c0` + test của tôi). Máy đang chạy toàn bộ pytest của Chỉ Huy song song.

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t079_linux.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py tests/test_app_pages.py tests/test_soi_loi_t080.py -rxX
1378 passed, 38 skipped, 13 xfailed in 109.40s (0:01:49)
  0 hỏng, 0 XPASS. 13 xfail = 3 cũ của T-048 (R2-1 ×2, R2-2) + 10 của tôi (SL-T080-1 ×3, SL-T080-2,
  SL-T080-L-1 phần Windows ×6). 38 bỏ qua: ca chỉ chạy trên Mac/Linux (có 3 ca SL-T079-L-1), cần ổ
  phân biệt hoa thường, như Thợ Máy ghi

$ uv run pytest tests/test_soi_loi_t080.py --runxfail
10 failed, 24 passed in 3.71s      (10 ca xfail hỏng đúng ở câu kiểm, xem mục Lỗi mới)

# cùng file test, chạy trên bản sao code main 417efea (python -m pytest từ thư mục bản sao):
11 failed, 13 passed, 10 xfailed in 3.77s
  11 ca hỏng: test_forced_swap_with_ref_typed_in_other_case_never_describes_outside ×10 (anh em NFD,
  Kelvin: lọt nội dung, cỡ; file ngoài quá cỡ: "Ảnh quá lớn (2,0 MB)"),
  test_kelvin_sibling_seen_by_lstat_and_resolve_is_not_opened[read_image_bytes] (đọc ra nội dung file ngoài)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t080.py
1 file already formatted
```

- **File mới `tests/test_soi_loi_t080.py`** (34 ca): 24 qua, 10 `xfail(strict)` (SL-T080-1 ×3, SL-T080-2 ×1, SL-T080-L-1 phần Windows ×6). Trên bản sao code `main` 417efea: 11 ca ép thắng / Kelvin hỏng đúng chỗ, tức test bắt được lỗi cũ. Trên Mac/Linux chỉ 2 ca không chặn oan chạy (`test_normal_folders_are_read_listed_and_checked[dung]`, `test_ref_typed_in_other_case_reads_by_disk_names`: tự bỏ qua trên ổ phân biệt hoa thường), các ca khác chỉ Windows; tôi chưa chạy được trên Mac/Linux.
- **Gộp thử** với `origin/team/T-080-linux` (`git merge-tree`): không xung đột.
- **Quét bí mật:** `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trên thư mục riêng chứa `tests/test_soi_loi_t080.py`, patch `git diff 417efea HEAD` và 1 file mồi tiếng Việt: mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`), **0 mục ở file thật**. Đã xóa mồi.

## Đối chiếu tiêu chí xong (phần Windows)

- [x] (1) LC-T079-1: so từng chữ ở `_win_handle_at` và `_scan_held`; ép thắng 0/380 lọt (bản cũ 22 nội dung, 22 cỡ, 4 tên); tráo thật 0 lọt (bản cũ lọt nội dung 61 lần, đích Kelvin)
- [x] (1) LC-T079-2: 0 câu tả file ngoài (bản cũ 204 khi ép); ảnh có vấn đề thật vẫn báo đúng
- [x] (1) LC-T079-3: `resolve` gặp liên kết → "vừa bị thay đổi"; Windows giữ "Không đọc được…" cho lỗi ổ thật. Câu "không có quyền" khi tráo ở chỗ khác: SL-T080-1, -2 (Thấp, có từ trước)
- [x] (1) Nhánh Mac/Linux: đọc kỹ, khớp kết quả lượt Linux thật
- [x] (2) Thử trên Windows: ép thắng 7 kiểu đích (thêm tầng trên, `ref` gõ chữ hoa, ép bước hỏi tên), tráo thật tiến trình riêng nhiều luồng; đối chứng dương bắt được lọt
- [x] (3) Không chặn oan: 5.505 + 2.265 phép kiểm giống `main`, 0 lỗi; tốc độ ngang; không rò handle. Drive, USB không thử lại (đúng lời giao)
- [x] (4) 2 file chỉ gỡ `xfail` (so AST giống hệt); 51 ca mới kiểm đúng ý
- [x] (5) Lỗi mới có test `xfail(strict=True)` mã SL-T080-1, -2 (và SL-T080-L-1 phần Windows); không sửa code ứng dụng
- [x] Test liên quan + `ruff check .` (mục Bằng chứng)

## Rủi ro và điểm cần chú ý

- **LC-T079-1 trên bản cũ thắng được ngoài thực tế** (đích anh em dấu Kelvin, khác hoa thường): biên bản T-079 xếp Thấp dựa trên "tráo thật 0 lọt" với đích NFD. T-080 đã đóng, nên không cần làm gì thêm, nhưng Lá Chắn nên biết khi xét lại mức của các lỗi cùng loại (phép so lỏng ở `_resolve_inside`).
- Kẻ tráo trên Windows tráo được ít (vài trăm đến vài nghìn lần mỗi lượt 20 giây, nhiều lần hỏng vì app đang giữ handle); bằng chứng chính là ép thắng + đối chứng dương + lượt Kelvin (bắt được lọt thật trên bản cũ). Lượt "ngoài gốc, tên thường" của T-080 kẻ tráo gần như không tráo được (15 lần); các lượt khác cũng trỏ ra ngoài gốc nên che được ca này.
- Ổ không thử: exFAT, ổ mạng máy chủ Linux (Samba), ổ đám mây khác (như Thợ Máy ghi). So từng chữ dựa vào việc ổ báo đường dẫn thật khớp tên trong danh sách; ổ nào không khớp sẽ báo "vừa bị thay đổi" (an toàn, không lọt, nhưng không dùng được ảnh).
- Máy bận: một lượt chạy `tests/test_soi_loi_t080.py` mất 3 phút 29 giây (lượt khác 15 giây); test của tôi không có giới hạn thời gian.

## Đề xuất

- **Chỉ Huy:** phần Windows ĐẠT CÓ ĐIỀU KIỆN; chuyển **Lá Chắn rút gọn** (F1). Gộp `team/T-080-linux` cùng `team/T-080` (không xung đột với commit của tôi).
- **Điều kiện (không chặn gộp T-080, không chặn T-056):** một phiếu dọn sau (Thợ Máy) cho SL-T080-1, SL-T080-2, SL-T080-L-1 (cả hai nền), theo cách gợi ý ở mục Lỗi mới; gỡ `xfail` khi XPASS (`tests/test_soi_loi_t080.py`, `tests/test_soi_loi_t080_linux.py`). SL-T080-2 nên làm cùng LC-T048-2, -3 nếu có phiếu đó. Hoặc Chỉ Huy cho ghi nhận, không sửa (chỉ sai câu chữ).
- **Lá Chắn:** xét ghi chú cho `_resolve_inside` (đường dẫn trả về có thể nằm trong thư mục anh em; không dùng để mở).

## Câu hỏi cho chủ dự án

Không có.

## Kết luận phần Windows: **ĐẠT CÓ ĐIỀU KIỆN**

Ba lỗi của phiếu đã sửa đúng trên Windows: so đường dẫn thật từng chữ chặn mọi thư mục anh em (ép thắng 0/380, tráo thật 0 lọt qua 21.541 lần tráo; bản cũ lọt nội dung 61 lần thật với đích dấu Kelvin), câu báo không còn tả file ngoài (0 so với 204), lỗi `resolve` khi bị tráo báo "vừa bị thay đổi". Không chặn oan (7.770 phép kiểm giống `main`), tốc độ ngang, không rò handle; 2 file chỉ gỡ `xfail` đúng, 51 ca mới đúng ý. Còn **2 lỗi Thấp mới** (SL-T080-1, -2) và SL-T080-L-1 phần Windows, đều chỉ sai câu báo, có từ trước T-080, không chặn. **Chuyển Lá Chắn rút gọn được.**

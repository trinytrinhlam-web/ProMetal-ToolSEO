# Báo cáo T-082 · Sửa câu báo đọc ảnh khi bị tráo thư mục (SL-T080-1, -2, -L-1) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-082](../tickets/T-082-cau-bao-doc-anh-sau-t080.md) · mức kiểm **rút gọn**, Windows. **Không chạy cloud Linux** (chủ dự án chưa đồng ý): 6 ca chỉ Linux/Mac kiểm bằng đọc mã |
| Ngày nộp | 2026-10-27 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (uv 0.13.4), người dùng thường, NTFS cục bộ và `\\localhost\C$`. Máy chạy song song agent khác |
| Mã nguồn | Nhánh `team/T-082` tại `552f870` (gốc `main` `b60054f`, đã có T-080). Đối chứng: bản sao `git archive b60054f seo_app` |
| Kết quả | Hoàn thành phần Windows. **Kết luận: ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới** (SL-T082-1: test hỏng oan trên Mac; SL-T082-2: một ca câu báo còn sót của SL-T080-L-1, Windows). 3 lỗi của phiếu đóng đúng ý; mọi ca vẫn bị từ chối, 0 lọt. **Không lỗi nào phải sửa trước Lá Chắn; chuyển Lá Chắn rút gọn được** |

## Tóm tắt (cho chủ dự án)

Ba lỗi câu báo của phiếu **đã được sửa đúng**: khi thư mục ảnh bị dời đi hay bị tráo đúng lúc app đọc, app không còn nói "không có quyền" hay "nằm ngoài thư mục ảnh" nữa mà báo "vừa bị thay đổi, hãy thử lại" (hoặc "Không tìm thấy…" khi mục vừa bị dời đi). Tôi thử lại đủ các cách tấn công cũ, trên ổ máy lẫn ổ mạng: **không lần nào đọc được gì bên ngoài thư mục ảnh**, mọi trường hợp vẫn bị từ chối như trước; dùng bình thường kết quả giống hệt bản cũ, tốc độ như cũ. Khi một chương trình khác tráo thư mục liên tục, số lần app báo sai "không có quyền" giảm từ 217 xuống 12, câu "nằm ngoài thư mục ảnh" không còn.

Còn **2 lỗi nhỏ (Thấp), không chặn**: (1) 3 ca thử mới của phiếu sẽ báo hỏng oan khi sau này chạy trên máy Mac (máy Mac coi hai tên thư mục thử là một), sửa một dòng; (2) một trường hợp hiếm còn câu báo sai nghĩa: thư mục bị **đổi tên** đúng lúc app đọc thì app nói "tên ngắn hoặc tên khác" thay vì "vừa bị thay đổi". Cả hai không ảnh hưởng an toàn.

## Phạm vi và cách kiểm

Diff `git diff b60054f..552f870`: `seo_app/images/folders.py` (+85/−16), `tests/test_images_folders.py` (+240/−1: 35 ca mới, 1 dòng kiểm câu báo của test T-048), `tests/test_soi_loi_t080.py` (−26: gỡ 3 dấu `xfail`), báo cáo Thợ Máy. Tôi:

1. Đọc toàn bộ diff, đối chiếu từng lỗi với cách sửa tôi gợi ý ở T-080 và điều kiện 2 của Lá Chắn T-080 (Việc 4).
2. Ép kẻ tráo "luôn thắng" (`sl80_forced_win.py` của tôi, thêm tuỳ chọn mở gốc qua `\\localhost\C$`) trên `main` `b60054f` và T-082; chạy thêm nguyên bản `lc79_forced.py`, `lc80_forced_unc.py` của Lá Chắn.
3. Tráo thật bằng tiến trình riêng (`sl80_race_win.py`), đếm lọt và phân bố câu báo.
4. Thử đột biến 13 kiểu trên các chỗ mới (`sl82_mutate.py`).
5. Soát test: dòng đổi trong test T-048, gỡ `xfail` (so AST), 35 ca mới, 6 ca Linux/Mac (đọc mã).
6. Không chặn oan: so kết quả `main` (đã có T-080) với T-082 trên cây ảnh thường (`sl80_perf_same.py`).

Script, số liệu thô: thư mục ghi chú chung của nhóm phiên, `T-082-soi-loi-scripts/` (không commit). Mọi file thử nằm trong thư mục tạm riêng, file "bí mật" là mồi tự tạo.

## Xác nhận từng lỗi đã đóng

### SL-T080-L-1 · `resolve` đi qua tầng vừa bị tráo — **đóng đúng ý, còn một ca sót (SL-T082-2)**

- `resolve` ra ngoài gốc → `_ChangedError` ("Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại.") thay `_LinkError(_MSG_OUTSIDE)` (`seo_app/images/folders.py:711-712`). Cả hai là `_LinkError`: vẫn từ chối, khi quét vẫn đếm vào `links`. `_MSG_OUTSIDE` đã bỏ; không còn chỗ nào dùng (grep `seo_app/`, `app/`, `tests/`).
- `resolve` ra tên khác (khác khóa tên): so định danh mục ở **`gốc/tên resolve trả`** với mục cuối vừa `lstat` (`_still_same_entry`, `:465-476`, dùng ở `:716-725`). Cùng mục (tên ngắn 8.3, hard link) → giữ `_MSG_ALIAS`; khác, mất, là liên kết, không hỏi được → `_ChangedError`. Đúng điều kiện Lá Chắn T-080 ("Windows giữ `_MSG_ALIAS` cho tên ngắn 8.3 thật"); Thợ Máy dùng một luật cho mọi HĐH thay vì tách "Mac/Linux luôn báo thay đổi" như gợi ý lượt Linux: tôi đồng ý, gọn hơn và đúng nghĩa với hard link.
- **Không `lstat` đường dẫn `resolve` trả** (có thể nằm trong thư mục anh em): ghép `root.joinpath(*actual)`. `actual` lấy từ `resolved.relative_to(root)` nên chỉ là tên (không `..`, không ổ đĩa), ghép vào gốc thật. Đột biến dùng `resolved` thay vào bị test `test_resolve_through_swapped_level_is_reported_as_changed[...-anh-em-kelvin]` bắt (mục Đột biến).
- Ca anh em dấu Kelvin cùng tên tầng con (junction `x` → `x` của thư mục anh em): `actual` trùng `parts` nên không vào nhánh tên khác, `_resolve_inside` trả bình thường; như T-080, cờ `exact` sai nên đọc ảnh hỏi lại tên trên ổ và so đường dẫn thật từng chữ → "Ảnh vừa bị thay đổi…". Ép `resolve` với đích này: ra ảnh mồi (mục Ép thắng).

### SL-T080-1 · Windows báo "không có quyền" khi thư mục vừa bị dời — **đóng đúng ý**

- `_opened_stat` (`:990-997`): đặt mã lỗi Windows về 0 rồi gọi `_win_open`; hỏng với lỗi 2 hay 3 → `_MSG_NOT_FOUND` ("Không tìm thấy ảnh hoặc thư mục này (có thể đã đổi tên, đã xóa…)"), lỗi khác giữ "Không đọc được…". Test của tôi nhận "Không tìm thấy" hay "vừa bị thay đổi" nên chọn "Không tìm thấy" (giống nhánh Mac/Linux và giữ đúng test cũ `test_stat_of_file_deleted_before_opened_stat_is_a_plain_error`) là hợp lý. Đặt mã lỗi về 0 trước khi gọi có test riêng (`test_windows_stale_error_code_is_not_used`) và đột biến bỏ dòng đó bị bắt.
- `resolve` gặp lỗi Windows 5 (`:701-709`): kiểm lại từng tầng của vòng `lstat` (`_levels_changed`, `:479-485`); tầng mất, thành liên kết, thành mục khác → "vừa bị thay đổi"; còn nguyên → giữ "Không đọc được". Chỉ áp cho lỗi 5 và chỉ trên Windows (`os.name == "nt"` đứng trước nên Mac/Linux không đụng `winerror`). Đúng gợi ý của tôi.

### SL-T080-2 · xem thư mục, thư mục vừa bị dời — **đóng đúng ý**

- `_read_entries` (`:1199-1202`): `os.scandir` báo `FileNotFoundError` → `_ChangedError`; lỗi khác giữ "Không đọc được thư mục này…". Áp chung mọi nhánh gọi `_read_entries` (giữ handle, mở bằng fd, nhánh dự phòng): cả ba chỉ gọi cho thư mục vừa kiểm nên đúng nghĩa. Quét cả cây: thư mục con vừa bị dời nay đếm vào `links` thay `unreadable` (Thợ Máy ghi ở Rủi ro 6): chấp nhận được, tổng số bỏ qua không đổi.

### Điều kiện 2 của Lá Chắn T-080 (Việc 4) — **đạt**

- (a) Docstring `_resolve_inside` (`:659-673`), `_checked_file` (`:890-901`): đường dẫn `resolve` trả **chỉ để so chuỗi**, không được mở, `stat`, liệt kê; nêu lý do (dấu Kelvin, thư mục anh em).
- (b) `_checked_file` trả `(gốc, lstat, exact)`, không trả đường dẫn (`:904-910`); `stat_image`, `read_image_bytes` cập nhật; `list_folder` đặt tên `_path` cho giá trị không dùng. Test `test_checked_file_does_not_hand_out_resolved_path` kiểm. Grep: không chỗ nào ngoài module gọi `_checked_file`/`_resolve_inside`.
- `_resolve_inside` vẫn trả đường dẫn (để `_checked_file` so; đổi kiểu trả sẽ hỏng test cũ bọc hàm này): chấp nhận, docstring đã ghi.

### Lớp chặn giữ nguyên

So AST hàm giữa `b60054f` và `552f870`: đổi `_resolve_inside`, `_checked_file`, `stat_image`, `_opened_stat`, `read_image_bytes`, `_Scan._read_entries`, `list_folder` (chỉ tên biến); thêm `_still_same_entry`, `_levels_changed`, hằng `_ERROR_ACCESS_DENIED`; bỏ `_MSG_OUTSIDE`. Mọi chỗ đổi chỉ đổi **loại câu báo của một lần từ chối** (hay chọn giữa hai câu từ chối), không chỗ nào biến từ chối thành chấp nhận: `_ChangedError` là `_LinkError` là `ImageFolderError`; `_MSG_NOT_FOUND`, `_MSG_UNREADABLE` cũng là `ImageFolderError`. Các lớp `_is_link_stat`, `_same_win_path`, `_win_handle_at`, `_win_handle_is_link`, so định danh, `_posix_open_dir`, `_disk_names`, `_open_image`, `_scan_held`, `_scan_by_fd`, `_visit` không đổi.

## Mọi ca vẫn bị từ chối

### Ép kẻ tráo "luôn thắng"

`sl80_forced_win.py` (của tôi ở T-080; thêm tuỳ chọn `--unc`: gốc mở qua `\\localhost\C$`, tráo làm trên ổ máy): 6 đích (ngoài gốc; anh em NFD, dấu Kelvin, `ß`, khác hoa thường trên thư mục phân biệt hoa thường; thư mục NFD trong gốc) × tầng cha / tầng trên × file ngoài bí mật / 5 MB / rỗng / là thư mục × 4 kiểu ép (`lstat`+mở, thêm lúc hỏi tên trên ổ, `ref` gõ chữ hoa, chỉ lúc `resolve`) × đọc, `stat`; thêm xem thư mục. Qua ổ mạng bỏ đích "khác hoa thường" (máy chủ SMB không mở thư mục trong thư mục phân biệt hoa thường, như Lá Chắn ghi).

| Bản | Ổ | Ca ép được | Lọt nội dung · cỡ · tên · qua liên kết | Câu tả file ngoài | Lộ đường dẫn | Sạch sau |
|---|---|---|---|---|---|---|
| `main` `b60054f` | NTFS | 380 | 0 · 0 · 0 · 0 | 0 | 0 | 380/380 |
| **T-082** | NTFS | 380 | **0 · 0 · 0 · 0** | **0** | **0** | 380/380 |
| `main` `b60054f` | `\\localhost\C$` | 330 | 0 · 0 · 0 · 0 | 0 | 0 | 330/330 |
| **T-082** | `\\localhost\C$` | 330 | **0 · 0 · 0 · 0** | **0** | **0** | 330/330 |

- Câu báo của T-082 **giống hệt** `main` ở mọi ca, **trừ 51 ca** kiểu ép `resolve` (đích ngoài gốc, NFD, `ß`; cả hai ổ): "Đường dẫn nằm ngoài thư mục ảnh được phép." → **"Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại."** Đúng SL-T080-L-1, không ca nào đổi từ từ chối sang chấp nhận.
- Kiểu ép `resolve` với đích Kelvin / khác hoa thường / NFD trong gốc: ra **ảnh mồi** ở cả hai bản (51 ca ổ máy, 34 ca ổ mạng): `resolve` trả đường dẫn trong thư mục anh em nhưng app không mở theo nó (Việc 4 của Lá Chắn), đọc đúng ảnh trong gốc.
- 16 ca ổ máy "không ép được" ở cả hai bản: `ref` gõ chữ hoa trên thư mục phân biệt hoa thường dừng ở "Không tìm thấy" trước bước bị ép (đúng).

Script của Lá Chắn chạy nguyên bản trên T-082: `lc79_forced.py` (ổ máy, 7 kiểu đích × đọc, `stat`) **14/14** "Ảnh vừa bị thay đổi…", sạch sau 7/7; `lc80_forced_unc.py` (`\\localhost\C$`, 6 kiểu đích) **12/12** "Ảnh vừa bị thay đổi…", sạch sau 6/6. Khớp số Thợ Máy ghi.

### Tráo thật bằng tiến trình riêng (`sl80_race_win.py`, 3 luồng app, 20 giây mỗi lượt)

| Đích (lượt) | `main` `b60054f`: lần tráo · vòng · lọt · "Không đọc được" | **T-082**: lần tráo · vòng · lọt · "Không đọc được" |
|---|---|---|
| Ngoài gốc | 73 · 3.229 · 0 · 12 | 244 · 3.848 · **0** · 3 |
| Anh em dấu Kelvin | 475 · 4.255 · 0 · 61 | 627 · 3.779 · **0** · 0 |
| Anh em dấu Kelvin, `ref` gõ chữ hoa | 426 · 2.931 · 0 · 45 | 252 · 2.884 · **0** · 1 |
| Anh em NFD | 228 · 3.086 · 0 · 35 | 147 · 2.699 · **0** · 3 |
| Ngoài gốc, file 5 MB (giới hạn 1 MB) | 254 · 2.230 · 0 · 40 | 152 · 2.657 · **0** · 1 |
| Ngoài gốc, nới khe 2 ms | 168 · 2.429 · 0 · 24 | 213 · 2.770 · **0** · 4 |
| **Cộng** | 1.624 lần tráo, 18.160 vòng: 0 lọt, **217** câu "Không đọc được" | **1.635 lần tráo, 18.637 vòng (55.911 lời gọi): 0 lọt nội dung, cỡ, tên; 0 câu tả file ngoài; 0 lộ đường dẫn; 0 lỗi lạ; 12 câu "Không đọc được"** |

- Sau mỗi lượt app đọc đúng ảnh mồi (6/6), handle như `main`.
- **Đối chứng dương** (bật/tắt junction tại chỗ, LC-T048-2 đã biết, 4 luồng, 15 s): `main` lọt 22 tên / 10.646 vòng, T-082 lọt 7 / 6.945. Bộ đếm bắt được lọt thật; không đổi ở T-082 (ngoài phạm vi).
- Câu báo khi bị tráo, T-082 so với `main`: **"Đường dẫn nằm ngoài thư mục ảnh được phép." 657 → 0**; "Thư mục vừa bị thay đổi…" 425 → 1.209; "Không đọc được… (không có quyền…)" 217 → 12 (11 lần ở `_read_entries` với lỗi không phải "không thấy", 1 lần ở bước hỏi tên trên ổ `_win_listed_name`); **"Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác…)" 162 → 165: còn nguyên, xem SL-T082-2**.
- Kẻ tráo lượt này tráo được ít (máy rất bận); bằng chứng chính vẫn là ép thắng + đối chứng dương.

### Thử đột biến (`sl82_mutate.py`: mỗi đột biến một bản sao `seo_app` + `tests`; chạy 6 file test thư mục ảnh của phiếu)

| Đột biến | Test hỏng |
|---|---|
| M1 ra ngoài gốc báo câu cũ "nằm ngoài thư mục ảnh" | 7: `test_resolve_check_alone_blocks_junction_outside` (test T-048 đã đổi dòng kiểm), `test_resolve_through_swapped_level_…[ngoai-goc]` ×3, SL-T080-L-1 Windows `[ngoai-goc]` ×3 |
| M13 bỏ hẳn phép kiểm `is_relative_to` | 10: `test_resolve_check_alone_blocks_junction_outside` (test T-048: lớp chặn thứ hai vẫn được khóa sau khi đổi dòng kiểm), `…swapped_level…[ngoai-goc]` ×3, đối chứng `test_swap_during_resolve_is_refused_safely_on_windows[ngoai-goc]` ×3, SL-T080-L-1 Windows `[ngoai-goc]` ×3 |
| M2 tên khác luôn "tên ngắn hoặc tên khác" | 9: `…swapped_level…[trong-goc]` ×3, `[anh-em-kelvin]` ×3, SL-T080-L-1 Windows `[trong-goc]` ×3 |
| M3 tên khác luôn "vừa bị thay đổi" | 3: hard link ×2, tên ngắn 8.3 thật |
| M4 so định danh bằng chính đường dẫn `resolve` trả | 3: `…swapped_level…[anh-em-kelvin]` (app `lstat` trong thư mục anh em) |
| M11 bỏ so định danh khi tên khác | 12: `…swapped_level…[trong-goc / anh-em-kelvin]` ×6, lỗi 5 + thư mục khác ×3, SL-T080-L-1 Windows `[trong-goc]` ×3 |
| M5 bỏ đặt mã lỗi về 0 trước `_win_open` | 1: `test_windows_stale_error_code_is_not_used` |
| M6 lỗi 2, 3 vẫn "Không đọc được" | 7: mã lỗi ×4, SL-T080-1 ×3 |
| M7 `scandir` không thấy vẫn "Không đọc được" | 2: `test_folder_gone_right_before_listing_is_reported_as_changed`, SL-T080-2 |
| M8 lỗi 5 không kiểm lại tầng | 9: tầng dời đi / thành junction / thành thư mục khác × 3 lời gọi |
| M9 lỗi 5 luôn "vừa bị thay đổi" | 3: tầng không đổi × 3 lời gọi (lỗi quyền thật phải giữ "Không đọc được") |
| M10 cờ `exact` luôn đúng | 16: `ref` gõ khác hoa thường (Thợ Máy, của tôi), ép thắng `ref` gõ chữ hoa ×12, `test_checked_file_does_not_hand_out_resolved_path` |
| M12 kiểm lại tầng cho **mọi** lỗi Windows (không chỉ lỗi 5) | **0: sống sót, vô hại.** Tầng không đổi vẫn "Không đọc được" (ca lỗi ổ mạng 59 giữ đúng câu); chỉ khác khi lỗi lạ trùng lúc tầng vừa đổi, lúc đó "vừa bị thay đổi" cũng đúng nghĩa. Không cần thêm test |

Mọi chỗ mới có test bắt, trừ M12 (chỉ nới phạm vi một phép kiểm câu báo, không đổi chặn hay không chặn).

### Không chặn oan (`sl80_perf_same.py`, cùng tiến trình, `main` `b60054f` so với T-082)

Cây 300 ảnh 60 KB, 3 tầng, 12 thư mục (gốc tên NFD; thư mục, ảnh tên có dấu NFC/NFD, tên dài, hoa thường lẫn lộn, `.jpg/.JPG/.png/.webp`); mỗi thư mục `list_folder` (gõ đúng, gõ chữ hoa), cả cây, mỗi ảnh `stat_image`, `read_image_bytes` với `ref` theo danh sách / chữ hoa / chữ thường; gốc gõ đúng / chữ thường / chữ hoa.

| Ổ | Phép kiểm | Giống `main` | T-082 báo lỗi |
|---|---|---|---|
| NTFS cục bộ | 5.505 | **5.505** | **0** |
| `\\localhost\C$` | 2.265 | **2.265** | **0** |

Ổ mạng (120 ảnh, 2 vòng) chạy lúc máy quá tải (khoảng 400 ms mỗi lời gọi ở cả hai bản) nên chỉ dùng phần so kết quả, không dùng số đo tốc độ. Tốc độ (ổ máy, xen kẽ, trung vị 3 vòng, `main` / T-082): `stat_image` 6,60 / 6,75 ms; `read_image_bytes` 35,99 / 34,70 ms; `list_folder` 13,12 / 11,50 ms; đọc `ref` gõ chữ hoa 34,72 / 35,17 ms: ngang nhau (T-082 không đụng đường chạy bình thường, chỉ thêm một lệnh đặt mã lỗi và một danh sách `lstat` đã có).

## Soát test

### Dòng đổi trong test T-048 `test_resolve_check_alone_blocks_junction_outside` (Chỉ Huy đã duyệt)

Diff đúng một khối: xóa `assert "ngoài thư mục" in str(exc)`, thêm 2 dòng chú thích và `assert isinstance(exc, folders._LinkError) and "thay đổi" in str(exc)`. **Phần còn lại giữ nguyên** (tạo junction ra ngoài, tắt `_is_link_stat` và `Path.is_junction`, gọi `read_image_bytes`, `raises_safely`). Câu kiểm mới **vẫn khóa đúng lớp chặn thứ hai**: lỗi phải là `_LinkError` (chỉ `_ChangedError` từ `_resolve_inside` thỏa cả hai điều kiện; câu "Ảnh vừa bị thay đổi…" của lớp so đường dẫn thật sau đó là `ImageFolderError` thường, không qua). Đột biến bỏ phép kiểm `is_relative_to` làm test này hỏng (mục Đột biến).

### Gỡ `xfail` trong `tests/test_soi_loi_t080.py` (R5)

So AST bản `b60054f` (bỏ các decorator `pytest.mark.xfail`) với bản mới: **giống hệt**. Chỉ gỡ ở 3 test: `test_sl_t080_1_…` (3 ca), `test_sl_t080_2_…` (1 ca), `test_sl_t080_l_1_windows_…` (6 ca); không đổi câu kiểm, dữ liệu thử. Đúng R5 (không xóa, không nới test; chỉ bỏ dấu khi lỗi đã sửa).

### 35 ca mới trong `tests/test_images_folders.py`

| Test | Ca | Kiểm đúng ý? |
|---|---|---|
| `test_resolve_through_swapped_level_is_reported_as_changed` | 9 | Có: ra ngoài gốc / tới `y` trong gốc / tới `y` của anh em dấu Kelvin × đọc, `stat`, xem → `_LinkError` + "thay đổi"; app **không `lstat` gì trong đích** (theo dõi `os.lstat`). Giả `resolve` (không junction thật): đủ cho nhánh câu báo; ca junction thật ở `test_soi_loi_t080.py` |
| `test_resolve_to_other_name_of_same_file_keeps_alias_message` | 2 | Có: hard link, `resolve` trả tên kia → giữ "tên ngắn hoặc tên khác" |
| `test_real_short_8_3_name_keeps_alias_message` | 1 | Có: tên ngắn 8.3 thật (máy này có): đọc, kiểm, xem đều giữ câu cũ |
| `test_resolve_access_denied_checks_levels_again` | 12 | Có: lỗi 5 + `x` dời đi / thành junction / thành thư mục khác → "vừa bị thay đổi"; không đổi gì → "Không đọc được" |
| `test_windows_attribute_handle_error_code_picks_message` | 8 | Có: lỗi 2, 3 → "Không tìm thấy"; 5, 32 → "Không đọc được"; cả ảnh quá cỡ (đường LC-T079-2) |
| `test_windows_stale_error_code_is_not_used` | 1 | Có: mã lỗi cũ không lẫn vào |
| `test_folder_gone_right_before_listing_is_reported_as_changed` | 1 | Có: xem thẳng → "vừa bị thay đổi"; quét cả cây → `links` 1, `unreadable` 0, ảnh khác vẫn ra |
| `test_checked_file_does_not_hand_out_resolved_path` | 1 | Có: chỉ trả gốc, `lstat`, cờ |

Đếm 9 + 2 + 1 + 12 + 8 + 1 + 1 + 1 = **35**; 13 ca chạy được trên Mac/Linux. Xem SL-T082-1 về 3 ca dấu Kelvin trên Mac.

### 6 ca chỉ Linux/Mac (`tests/test_soi_loi_t080_linux.py`) — đọc mã, **dự đoán XPASS cả 6**

Test bọc `os.path.realpath` (đường `Path.resolve` của Python 3.12 gọi tới): đúng lúc `resolve`, `x` thành symlink tới `ngoai/` (ngoài gốc) hay tới `y/` (trong gốc), rồi trở lại thư mục thật.

- `ngoai-goc` × đọc / `stat` / xem: `resolve` ra `tmp/ngoai/...` → `is_relative_to(gốc)` sai → `_ChangedError` (`:711-712`) → câu "Thư mục vừa bị thay đổi…" có "thay đổi" → **XPASS**.
- `trong-goc` × đọc / `stat` / xem: `resolve` ra `gốc/y/bi-mat.jpg` (hay `gốc/y`) → tên khác → `_still_same_entry(gốc/y/…, last)`: lúc đó `x` đã trở lại, `gốc/y/bi-mat.jpg` là file khác (inode khác ảnh mồi), `gốc/y` khác inode `gốc/x` → `_ChangedError` → **XPASS**.
- Trên Mac/Linux `exc.winerror` không bị đọc (`os.name == "nt"` đứng trước). `_ChangedError` ném ngoài khối `except` nên không xích lỗi: 6 ca đối chứng `test_swap_during_resolve_is_refused_safely` vẫn qua.

Hệ quả: lượt Linux/Mac sau sẽ thấy **6 XPASS(strict) = FAILED** tới khi xóa 6 dòng khối `@pytest.mark.xfail(...)` của `test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed` (khớp Rủi ro 2 của Thợ Máy). Đây là suy luận từ đọc mã, chưa chạy.

## Lỗi mới

Hai lỗi Thấp, không lỗi nào làm lọt hay nới lớp chặn:

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|---|
| SL-T082-2 | **Thấp** (Windows; chỉ sai câu báo, vẫn từ chối; phần còn sót của SL-T080-L-1) | Thư mục chứa ảnh bị **đổi tên** (không phải tráo thành liên kết) đúng lúc `resolve` đang giữ handle: Windows trả đường dẫn thật theo tên mới, `_resolve_inside` thấy tên khác, rồi `_still_same_entry(gốc/tên mới/…)` đúng là **cùng mục** (file dời theo thư mục) nên chọn câu "tên ngắn hoặc tên khác", dù tên đã gõ không phải tên ngắn. Ở T-080 tôi đã tả ca này trong SL-T080-L-1 ("hay lúc handle của `resolve` đang mở thì `x` bị đổi tên") | `seo_app/images/folders.py:716-725` | Tráo thật (`sl80_race_win.py`; kẻ tráo đổi tên `x` sang một tên khác **trong gốc** rồi đặt junction): T-082 ra câu này **165 lần** / 18.637 vòng (xem thư mục 139, `stat` 19, đọc 7), `main` 162. Ép thắng không bắt được vì phép ép của tôi chỉ dời thư mục ra ngoài gốc. Chưa có test `xfail` (xem dưới) | "Thư mục vừa bị thay đổi…" | "Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục)." |

Cách sửa gợi ý (Thợ Máy cân nhắc): ở nhánh tên khác, chỉ giữ câu "tên ngắn hoặc tên khác" khi **cả** mục ở tên `resolve` trả **lẫn** mục ở chữ đã gõ (`gốc/parts`) đều vẫn là mục vừa `lstat`. Tên ngắn 8.3 thật thỏa cả hai (tên ngắn vẫn trỏ tới mục), còn thư mục vừa bị đổi tên thì chữ đã gõ không còn trỏ tới đó → "vừa bị thay đổi". Không làm hỏng test 8.3 và hard link hiện có (cả hai tên vẫn còn). Nếu kẻ tráo trả tên lại trước bước kiểm này thì vẫn ra câu cũ (không phân biệt được), chấp nhận. Lượt này tôi **chưa thêm test `xfail`** cho SL-T082-2; đề nghị Thợ Máy thêm test cùng lúc sửa (giả `resolve` trả đường dẫn theo tên mới của thư mục vừa bị đổi tên trong gốc).

Một lỗi nhỏ trong **test mới** của phiếu (chỉ ảnh hưởng lượt chạy trên Mac):

| # | Mức (đề xuất) | Mô tả | Vị trí | Cách tái hiện | Mong đợi | Thực tế (suy luận, chưa chạy được trên Mac) |
|---|---|---|---|---|---|---|
| SL-T082-1 | **Thấp** (chỉ test; chỉ Mac, ổ APFS mặc định) | Ca `anh-em-kelvin` của `test_resolve_through_swapped_level_is_reported_as_changed` tạo hai thư mục `Ảnh kho` và `Ảnh Kho` (dấu Kelvin U+212A) rồi `assert len(os.listdir(base)) == 2`. APFS mặc định không phân biệt dạng Unicode lẫn hoa thường; U+212A phân rã chuẩn thành `K` (U+004B), nên hai tên là **một** thư mục: lệnh tạo đích ghi đè `gốc/y/a.jpg`, rồi câu `assert` hỏng. 3 ca (đọc, `stat`, xem) sẽ **hỏng oan** trên Mac, đúng lúc chạy bộ test trên máy Mac thật theo điều kiện cũ của Lá Chắn | `tests/test_images_folders.py:1659-1663` | Chạy `tests/test_images_folders.py -k anh-em-kelvin` trên Mac (APFS không phân biệt hoa thường). Trên Windows (NTFS không gộp U+212A với `k`) và Linux (ext4) không xảy ra | Ổ coi hai tên là một thì **bỏ qua** ca đó (`pytest.skip`), như các test khác của dự án làm với ổ phân biệt hoa thường | `AssertionError: ổ coi hai tên là một` |

Cách sửa (một dòng, Thợ Máy): đổi `assert len(os.listdir(base)) == 2, "ổ coi hai tên là một"` thành `if len(os.listdir(base)) != 2: pytest.skip("ổ coi hai tên là một")`, và đặt câu kiểm này **trước** khi ghi `outside / "y" / "a.jpg"` (để khỏi ghi đè ảnh trong gốc). Không có `xfail` để thêm: lỗi nằm trong chính test và không tái hiện được trên Windows; tôi ghi ở đây để không ai coi 3 ca hỏng trên Mac là lỗi của app. Các test cùng kiểu của tôi (`tests/test_soi_loi_t080.py`, `test_soi_loi_t079.py`) đều `windows_only` nên không bị.

## Bằng chứng

Máy Windows 11 Pro 10.0.26300, Python 3.12.15, worktree `wt-T-082`, nhánh `team/T-082` (code `552f870`). Máy đang chạy song song nhiều lượt pytest của phiên khác (rất chậm).

```
# Đúng lệnh trong tiêu chí xong của phiếu:
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py -rsxX
445 passed, 24 skipped, 3 xfailed in 227.79s (0:03:47)
  0 hỏng, 0 XPASS; 3 xfail = R2-1 ×2, R2-2 (T-048, không thuộc phiếu); khớp số Thợ Máy

# Mọi file test gọi tới folders.py (grep "images.folders|ImageLibrary" trong tests/, 29 file) + tests/test_app_pages.py:
1 failed, 2629 passed, 51 skipped, 14 xfailed in 4234.03s (1:10:34)
  1 ca hỏng: tests/test_drafts_images.py::test_lc_t055_1_case_variant_stays_ai_whatever_scanned_is[ref-theo-nhap]
  hỏng ở bước pytest tạo thư mục tạm: OSError [WinError 1450] Insufficient system resources
  (máy quá tải vì nhiều lượt pytest chạy cùng lúc), không phải lỗi code. Chạy riêng lại:
$ uv run pytest "tests/test_drafts_images.py::test_lc_t055_1_case_variant_stays_ai_whatever_scanned_is"
5 passed in 42.10s
  14 xfail đều có từ trước, không liên quan: R2-1 ×2, R2-2 (T-048), SL-T067-1 ×4, SL-T070-4 ×7
  51 bỏ qua: ca chỉ Mac/Linux (có 6 ca SL-T080-L-1 và 6 ca đối chứng của tests/test_soi_loi_t080_linux.py), cần symlink

$ uv run ruff check .
All checks passed!
```

- Đột biến (13 kiểu) và ép thắng: mục "Mọi ca vẫn bị từ chối".
- Không thêm file test, không đổi file code nào; chỉ thêm báo cáo này. Script thử ở thư mục ghi chú chung.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Xác nhận SL-T080-1 (`_opened_stat` lỗi 2/3; `resolve` lỗi 5), SL-T080-2 (`_read_entries`), SL-T080-L-1 (`_resolve_inside`) đóng đúng ý; phần còn sót: SL-T082-2 (Thấp)
- [x] Mọi ca vẫn bị từ chối: ép thắng NTFS 380 ca, `\\localhost\C$` 330 ca, script Lá Chắn 14 + 12 lời gọi, tráo thật 18.637 vòng: 0 lọt nội dung, cỡ, tên; 0 câu tả file ngoài; 0 lộ đường dẫn
- [x] Điều kiện 2 của Lá Chắn T-080 (Việc 4 (a) docstring, (b) `_checked_file` trả cờ) đạt; Windows giữ "tên ngắn" cho 8.3 thật
- [x] Dòng đổi trong test T-048 đúng, phần còn lại giữ nguyên, vẫn khóa lớp chặn thứ hai (đột biến M13)
- [x] Gỡ `xfail` đúng R5 (so AST: chỉ bỏ dấu)
- [x] 35 ca mới kiểm đúng ý; 13 đột biến, 12 bị bắt (M12 vô hại)
- [x] 6 ca Linux/Mac: đọc mã, dự đoán XPASS cả 6 (không chạy cloud theo lời giao)
- [x] Lỗi mới ghi mã SL-T082-1, -2; không sửa code ứng dụng. **Chưa có** `tests/test_soi_loi_t082.py`: SL-T082-1 là lỗi của chính test (không tái hiện được trên Windows), SL-T082-2 chưa có test (đề nghị thêm cùng lúc sửa)
- [x] Test liên quan + `uv run ruff check .` (mục Bằng chứng)

## Rủi ro và điểm cần chú ý

- **6 ca Linux/Mac chưa chạy** (không chạy cloud theo lời giao). Đọc mã: XPASS cả 6, tức lượt Linux/Mac sau sẽ báo **6 FAILED (XPASS strict)** tới khi xóa dấu `xfail`. 13 ca mới chạy được trên Mac/Linux cũng chưa ai chạy; theo đọc mã qua trên Linux, còn trên Mac 3 ca dấu Kelvin hỏng oan (SL-T082-1).
- **"Ra ngoài gốc" nay luôn là "vừa bị thay đổi"** (Thợ Máy, Rủi ro 3): đúng khi `_is_link_stat` nhận ra mọi loại liên kết. Các lượt thử của đội tới nay (NTFS, ổ mạng, Google Drive, USB FAT32, ext4) chưa gặp loại mục nào mà `resolve` đi theo còn `lstat` không coi là liên kết (suy luận từ số liệu cũ, tôi không thử lại ổ Drive, USB); nếu có, app vẫn từ chối, chỉ câu báo kém rõ.
- **Đếm khi quét cả cây** (Thợ Máy, Rủi ro 6): thư mục con vừa bị dời đi giữa lúc kiểm và lúc đọc danh sách nay vào `links`, giao diện hiện "Bỏ qua: 1 lối tắt" (`app/views/write.py:1395-1411`) thay vì "1 mục không đọc được". Cùng cách đếm với mọi ca `_ChangedError` khác khi quét, chỉ xảy ra khi bị tráo hay đồng bộ Drive đúng lúc đó; ghi nhận, không thành lỗi.
- **Lỗi Windows 5 của `resolve`** chỉ thành "vừa bị thay đổi" khi lúc kiểm lại tầng vẫn còn khác; tráo rồi trả lại trước đó thì vẫn "Không đọc được…" (đúng như gợi ý của tôi, không phân biệt được với lỗi quyền thật).

## Đề xuất

- **Chỉ Huy:** chuyển **Lá Chắn rút gọn** (F1). Không lỗi nào phải sửa trước.
- **Thợ Máy (nên làm trong phiếu này, trước khi gộp; không chặn Lá Chắn):** sửa SL-T082-1 (một dòng trong test của chính T-082: `assert` → `pytest.skip`, đặt trước khi ghi đích). SL-T082-2 (chỉ câu báo, Thấp): sửa luôn trong phiếu này theo cách gợi ý kèm test, hoặc Chỉ Huy cho ghi nhận/đẩy sang phiếu dọn sau; nếu sửa thì Soi Lỗi chạy lại phép tráo thật đếm câu "tên ngắn".
- **Khi có lượt Linux (chủ dự án đồng ý) hay máy Mac thật:** chạy `tests/test_soi_loi_t080_linux.py tests/test_images_folders.py -rsxX`; 6 ca SL-T080-L-1 XPASS thì chỉ xóa khối `@pytest.mark.xfail(...)` của `test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed`.

## Câu hỏi cho chủ dự án

Không có.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** T-082 sửa đúng 3 lỗi câu báo (SL-T080-1, -2, -L-1) và điều kiện Việc 4 của Lá Chắn T-080 mà không nới lớp chặn nào: ép thắng 710 ca (ổ máy và ổ mạng) và tráo thật 18.637 vòng đều 0 lọt, câu báo không tả file ngoài, không lộ đường dẫn; không chặn oan, tốc độ như cũ; test mới đủ chặt (12/13 đột biến bị bắt, cái còn lại vô hại). Còn 2 lỗi Thấp: SL-T082-1 (3 ca test hỏng oan trên Mac, sửa một dòng) và SL-T082-2 (thư mục bị đổi tên đúng lúc `resolve` vẫn báo "tên ngắn hoặc tên khác"). **Không lỗi nào phải sửa trước Lá Chắn; chuyển Lá Chắn rút gọn được.** Điều kiện: SL-T082-1 sửa trước khi gộp (hay trước lượt chạy Mac); SL-T082-2 sửa trong phiếu này hoặc Chỉ Huy cho ghi nhận/đẩy phiếu sau.

# Báo cáo T-080 · Dọn 3 lỗi Thấp đọc ảnh sau T-079 (LC-T079-1, -2, -3) · Thợ Máy

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-080](../tickets/T-080-don-loi-thap-doc-anh-sau-t079.md) |
| Ngày nộp | 2026-10-23 |
| Nhánh | `team/T-080` (tạo từ `main` `417efea`, đã có T-079). Commit: `da5846a` (sửa `folders.py`, gỡ `xfail`), `bc68739` (test mới), `62a16f5` (đọc ảnh Windows chỉ hỏi lại tên khi cần), `a88c4e8` (báo cáo), commit bổ sung phần ổ USB vào báo cáo (không đổi code) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4, người dùng thường; máy chạy song song agent khác. Không có Linux/Mac |
| Kết quả | **Hoàn thành trên Windows**, đã thử thêm ổ USB FAT32 thật (không phải sửa gì). Phần Mac/Linux: đọc code kỹ và chạy giả lập; 3 ca SL-T079-L-1 (chỉ chạy trên Linux/Mac) chờ lượt cloud Linux |

## Tóm tắt (cho chủ dự án)

Ba lỗi nhỏ Lá Chắn để lại sau T-079 đã được sửa:

1. **Thư mục "anh em" tên trông y hệt** (LC-T079-1). Khi kiểm "file đang mở có thật nằm trong thư mục ảnh không", app nay so địa chỉ **đúng từng chữ** như ổ đĩa phân biệt, không coi chữ có dấu gõ kiểu khác, "ß" với "ss", chữ K đặc biệt hay chữ hoa/thường là một. Tôi dựng lại phép thử "ép kẻ tấn công luôn thắng" của Lá Chắn: bản cũ đọc được file bên ngoài ở 5/7 kiểu, bản mới chặn cả 7.
2. **Câu báo lỗi nói về file bên ngoài** (LC-T079-2). Khi bị tráo, app không còn báo kiểu "Ảnh quá lớn (5,0 MB)" về một file nằm ngoài thư mục ảnh, chỉ báo "Ảnh vừa bị thay đổi, hãy thử lại". Ảnh có vấn đề thật (quá lớn, rỗng, là thư mục) vẫn được báo đúng như trước.
3. **Câu báo sai nghĩa** (LC-T079-3). Khi bị tráo, app báo "vừa bị thay đổi, hãy thử lại" thay vì "không có quyền".

Dùng bình thường không thấy gì khác. Tôi thử trên ổ cứng, ổ mạng chia sẻ, hai ổ Google Drive và ổ USB FAT32 của máy (với Drive và USB: chỉ đọc thông tin, không mở nội dung, không ghi gì, không ghi tên file nào ra): kết quả giống hệt bản cũ, tốc độ như cũ. Trên USB (chủ dự án cho thử), cả 727 ảnh đều dùng được, kể cả khi gõ tên khác chữ hoa/thường, không ảnh nào bị báo "vừa bị thay đổi" oan, nên không phải sửa thêm gì. Phần chạy trên Mac/Linux tôi chỉ kiểm được bằng đọc code và giả lập; còn 3 ca chỉ chạy trên Linux/Mac cần một lượt cloud Linux.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/folders.py` | `_same_win_path` (so đường dẫn thật từng chữ) thay `_path_key`, dùng ở `_win_handle_at` (đọc, `stat`) và `_Scan._scan_held` (xem thư mục); đọc ảnh Windows mở theo tên ổ báo; `_checked_file` báo theo mục lấy lại trong thư mục ảnh (`_check_file`); `_changed_while_resolving` cho `_resolve_inside` |
| `tests/test_images_folders.py` | Thêm 51 ca T-080 (31 ca chạy cả trên Mac/Linux) |
| `tests/test_soi_loi_t079.py` | Chỉ gỡ `xfail` SL-T079-1 (8 ca) |
| `tests/test_la_chan_t079.py` | Chỉ gỡ `xfail` LC-T079-2 (6 ca), LC-T079-1 (1 ca) |
| `docs/team/reports/T-080-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `config/**`, `seo_app/storage/**`; không thêm thư viện (chỉ `import errno` của thư viện chuẩn).

## Cách sửa từng lỗi

### LC-T079-1 (= SL-T079-1) · so đường dẫn thật đúng như ổ phân biệt tên (Windows)

Gốc lỗi: `_path_key` so đường dẫn thật của handle với `gốc/parts` sau khi gộp NFC + `casefold`, lỏng hơn NTFS (NTFS không gộp dạng Unicode, `ß` khác `ss`, dấu Kelvin U+212A khác `K`, thư mục bật phân biệt hoa thường thì `ANH` khác `Anh`).

Cách sửa (`_same_win_path`): so **từng chữ**, chỉ bỏ tiền tố đường dẫn dài (`\\?\`, `\\?\UNC\`) và dấu `\` cuối. Muốn so từng chữ được thì bên đem so phải viết đúng như ổ báo tên:

- **Gốc**: `resolve(strict=True)` của Python dùng đúng hàm hỏi đường dẫn thật (`GetFinalPathNameByHandleW`), nên gốc trong đường dẫn thật của handle trùng từng chữ với gốc đã `resolve`.
- **Phần sau gốc**: tên trên ổ (tên thư mục cha liệt kê ra). `stat_image` vốn mở theo `_disk_names`; xem thư mục (`_scan_held`) vốn đi theo tên `_disk_names` và tên trong danh sách quét. **Đọc ảnh trên Windows**: nếu `resolve` vừa trả đúng `gốc/chữ đã gõ` (thường gặp: `ref` lấy từ danh sách thư mục; ổ Google Drive trả lại chữ đã mở) thì mở theo đúng chữ đó; khác (ví dụ `ref` gõ khác hoa thường trên NTFS) thì hỏi `_disk_names` rồi mở theo tên trên ổ. Trước đây đọc ảnh mở theo đường dẫn `resolve` trả và so lỏng nên không cần bước này. Bỏ được bước hỏi tên ở trường hợp thường là quan trọng: trên Google Drive bước đó tốn khoảng 7–8 ms mỗi ảnh (đo trên ổ H:, I:).

An toàn của cả hai cách mở như nhau: đường dẫn thật của handle phải trùng từng chữ `gốc/parts`, tức file đã mở nằm đúng chỗ đó trong thư mục ảnh lúc mở; một tầng bị tráo thành junction thì đường dẫn thật là đường dẫn đích, khác. Không còn hàm `_path_key`; `_name_key` (khóa so tên của `_match_disk_name`, `_resolve_inside`) giữ nguyên.

Tôi không dùng cách "phần sau gốc so không phân biệt hoa thường bằng `CompareStringOrdinal`" (gợi ý của Lá Chắn) vì phiếu yêu cầu không gộp hoa thường khi thư mục bật phân biệt hoa thường; so từng chữ chặt hơn mà đọc thật trên NTFS, ổ mạng, Google Drive vẫn được (mục Bằng chứng). Mac/Linux không có phép so chuỗi này (đọc, `stat`, quét đi bằng fd từng tầng) nên không đổi.

### LC-T079-2 · câu báo không tả file ngoài thư mục ảnh

Gốc lỗi: `_checked_file` kiểm loại, cỡ trên `lstat` theo chuỗi đường dẫn và báo lỗi trước lớp kiểm trên mục đã mở; tầng giữa vừa bị tráo thì `lstat` tả file ngoài thư mục ảnh.

Cách sửa (`_checked_file`, `_check_file`):

- Kiểm `lstat` như cũ; **qua thì đi tiếp như cũ** (không tốn thêm gì khi ảnh dùng được).
- **Hỏng** thì chưa báo: lấy lại mục trong thư mục ảnh bằng chính lớp T-079 (`_disk_names` rồi `_opened_stat`: Mac/Linux mở thư mục từng tầng `O_NOFOLLOW`; Windows handle chỉ hỏi thuộc tính + đường dẫn thật từng chữ), phải **cùng định danh** với `lstat`, không thì "Ảnh vừa bị thay đổi…". Cùng định danh thì **kiểm lại trên chính mục đó** và báo theo mục đó, nên câu báo luôn tả mục nằm trong thư mục ảnh (kể cả trên ổ không có số inode); mục đó lại dùng được (vừa sửa xong) thì "Ảnh vừa bị thay đổi…".
- Câu báo được ném ngoài khối bắt lỗi, nên không xích lỗi cũ.
- `_opened_stat` nay chỉ lấy số liệu mục trong thư mục ảnh (không phải liên kết, cùng định danh); phần kiểm file thường/ẩn ("vừa bị thay đổi") và cỡ của `stat_image` chuyển ra ngay sau nó, giữ nguyên ý nghĩa.

Phạm vi: các câu của `_checked_file` (cỡ, rỗng, không phải file ảnh, file ẩn). Các câu "Không tìm thấy", "liên kết tắt", "ẩn" của `_resolve_inside` và "không phải là thư mục" của `list_folder` vẫn có thể tả mục ngoài khi bị tráo, nhưng chỉ ở mức có/không, loại: Lá Chắn T-079 ghi nhận, không bắt sửa; tôi không đổi.

### LC-T079-3 (gồm SL-T079-L-1) · "vừa bị thay đổi" thay "không có quyền"

Cách sửa (`_resolve_inside`, `_changed_while_resolving`): vòng `lstat` vừa thấy mọi tầng là mục thật, không phải liên kết, nên `resolve(strict=True)` gặp liên kết là đường dẫn vừa bị tráo → `_ChangedError` ("Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại."; khi quét thì đếm vào `links` như các ca tráo khác):

- vòng liên kết: `RuntimeError` (Python 3.12 đổi ELOOP thành lỗi này), ELOOP, lỗi Windows 1921;
- Mac/Linux: EINVAL (đúng ca SL-T079-L-1: tầng là symlink lúc `resolve` xem, thành thư mục lại lúc đọc đích), ENOTDIR.

Giữ "Không đọc được…" cho không có quyền, lỗi ổ đĩa (EIO…) và **mọi lỗi Windows khác**: Python đổi lỗi Windows lạ (ổ mạng, ổ vừa rút) thành EINVAL, nên trên Windows xét theo mã lỗi Windows chứ không theo `errno` (không thì "ổ đĩa vừa bị ngắt" thành "hãy thử lại").

### Gỡ `xfail`

Chỉ xóa dấu `xfail` (định nghĩa `SL_T079_1`, `LC_T079_2`, `LC_T079_1` và chữ `marks=…` trong `pytest.param`), không đổi `assert` hay dữ liệu thử nào: diff hai file chỉ có dòng xóa và 8 dòng `pytest.param(...)` bỏ `marks=` (ruff gộp một ca về một dòng). Dấu Kelvin U+212A của ca `anh-em-dau-kelvin` giữ nguyên (kiểm bằng `ascii()`).

3 ca SL-T079-L-1 (`tests/test_soi_loi_t079_linux.py`, chỉ chạy trên Linux/Mac) **giữ `xfail`** như lời giao: trên máy này chúng tự bỏ qua. Theo đọc code chúng sẽ XPASS (EINVAL thật của `readlink` → "vừa bị thay đổi"); xem mục "Phần chưa kiểm được".

## Bằng chứng

### Test liên quan và ruff

```
# Mốc trước khi sửa (team/T-080 = main 417efea), 11 file như lời giao:
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_soi_loi_t079_linux.py tests/test_la_chan_t079.py tests/test_drafts_images.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py tests/test_app_pages.py -rxX
2 failed, 1155 passed, 38 skipped, 18 xfailed in 695.76s (0:11:35)
  2 failed: test_app_pages.py home.py, plan.py "AppTest script run timed out after 30(s)" (máy bận; lượt sau qua)
  18 xfail = 3 cũ của T-048 (R2-1 ×2, R2-2) + 8 SL-T079-1 + 7 LC-T079

# Sau khi sửa (code cuối, cùng 11 file):
1223 passed, 38 skipped, 3 xfailed in 129.97s (0:02:09)
  3 xfail = R2-1 ×2, R2-2 (T-048, không thuộc phiếu này); 0 hỏng, 0 XPASS
  so mốc: +51 ca mới, 15 xfail thành qua, 2 ca quá giờ nay qua

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/images/folders.py tests/test_images_folders.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py
4 files already formatted
```

- Trước khi gỡ dấu, 15 ca `xfail(strict)` của Windows (8 SL-T079-1, 6 LC-T079-2, 1 LC-T079-1) đều XPASS (`15 failed` do strict, `15 passed`, `2 skipped` POSIX).
- 38 skipped: các ca chỉ chạy trên Mac/Linux (có 3 ca SL-T079-L-1), cần ổ phân biệt hoa thường… như mốc.
- **Test mới chạy trên bản cũ** (bản sao `git archive` có `folders.py` của `main`, thư mục nháp): 38/51 ca hỏng đúng chỗ (`_same_win_path` chưa có, 12 ca thư mục anh em, 2 ca câu báo theo `lstat`, 15 ca lỗi `resolve` "vừa bị thay đổi"); 13 ca còn lại là hành vi đúng ở cả hai bản (ảnh có vấn đề thật báo đúng, `ref` gõ khác hoa thường, lỗi "Không đọc được").

### Ép kẻ tấn công "luôn thắng" (`lc79_forced.py` của Lá Chắn T-079, chạy nguyên bản)

| Đích của junction | `main` `417efea` (T-079) | **T-080** |
|---|---|---|
| Ngoài gốc, tên thường | "Ảnh vừa bị thay đổi…" | "Ảnh vừa bị thay đổi…" |
| Anh em của gốc, tên NFD | **lọt nội dung + cỡ** | "Ảnh vừa bị thay đổi…" |
| Anh em, dấu Kelvin | **lọt nội dung + cỡ** | "Ảnh vừa bị thay đổi…" |
| Anh em, `ß` thay `ss` | **lọt nội dung + cỡ** | "Ảnh vừa bị thay đổi…" |
| Anh em khác hoa thường (thư mục cha phân biệt hoa thường) | **lọt nội dung + cỡ** | "Ảnh vừa bị thay đổi…" |
| Thư mục khác trong gốc, tên NFD (đọc qua liên kết) | **lọt nội dung + cỡ** | "Ảnh vừa bị thay đổi…" |
| Ngoài gốc, file 5 MB, giới hạn 1 MB | **"Ảnh quá lớn (5,0 MB), tối đa 1,0 MB."** | "Ảnh vừa bị thay đổi…" |

Cả đọc (`read_image_bytes`) lẫn `stat_image`; sau mỗi ca thư mục trở lại nguyên trạng.

### Ổ thật (`probe_t080.py`; so bản T-080 với `main`)

Với mỗi ảnh: `stat_image` (cỡ, giờ sửa, `file_id` trùng `lstat`), cùng `ref` với `main`, đường dẫn thật của handle file và handle thư mục so với gốc + tên trên ổ (trùng từng chữ / chỉ khác hoa thường / khác dạng Unicode / khác hẳn); `list_folder` các thư mục chứa ảnh và thư mục gốc so với `main` (số ảnh, tên ảnh, thư mục con, số bỏ qua). Gốc gõ ba kiểu: đúng, chữ thường hết, chữ hoa hết. Chỉ in Đúng/Sai và số đếm.

| Ổ | Ảnh × kiểu gõ gốc | Đường dẫn thật trùng từng chữ (file và thư mục) | `stat_image` đúng số liệu, cùng `ref` với `main` | `list_folder` giống `main` | Đọc nội dung giống `main` |
|---|---|---|---|---|---|
| NTFS cục bộ (cây thử 6 ảnh: tên có dấu, NFD, hoa thường, `Strasse Kho`) | 6 × 3 | 18/18 | 18/18 | 18/18 | 18/18 |
| Ổ mạng `\\localhost\C$` (cùng cây thử, qua SMB) | 6 × 3 | 18/18 | 18/18 | 18/18 | 18/18 |
| Google Drive for Desktop `H:\My Drive` | 8 × 3 | 24/24 | 24/24 | 6/6 | không đọc (chỉ thuộc tính) |
| Google Drive for Desktop `I:\My Drive` | 8 × 3 | 24/24 | 24/24 | 6/6 | không đọc (chỉ thuộc tính) |

Không ổ nào có ca "chỉ khác hoa thường" hay "khác dạng Unicode". Trên Google Drive, gốc gõ chữ hoa hết thì `resolve` trả lại đúng chữ đã gõ và đường dẫn thật của handle cũng theo đúng chữ đã mở (khớp LC-T076-1); app mở theo đúng chữ đó nên vẫn trùng từng chữ.

### Ổ USB FAT32 thật (chủ dự án đồng ý qua Chỉ Huy B, 2026-10-23; `probe_usb_t080.py`)

Giới hạn giữ đúng lời đồng ý: chỉ đọc danh sách thư mục, thuộc tính (`lstat`), handle chỉ hỏi thuộc tính và đường dẫn thật của handle, hỏi tên trong thư mục cha; **không mở nội dung file nào, không ghi gì vào ổ, không in tên file, thư mục hay nhãn ổ nào** (chỉ số đếm và câu báo cố định của app). `read_image_bytes` mở nội dung nên **không gọi**; thay vào đó làm lại đúng các bước kiểm của đường đọc ảnh tới ngay trước khi đọc (`_checked_file`, chọn tên để mở, so đường dẫn thật từng chữ, so định danh, cỡ) trên handle chỉ hỏi thuộc tính, cho cả bản T-080 lẫn `main`. Bỏ qua mục ẩn/hệ thống như app.

- Ổ `F:`: **FAT32**, ổ rời; ổ báo **không** phân biệt hoa thường khi tìm (không có cờ `FILE_CASE_SENSITIVE_SEARCH`), có giữ chữ hoa thường.
- Lượt thử rộng: cả cây thư mục không ẩn (336 thư mục, tối đa 8 tầng).

| Phép thử | Kết quả |
|---|---|
| Đường dẫn thật của handle so với tên trong danh sách, 3.782 mục (file: 95 tên 8.3 chữ hoa, 1.103 tên 8.3 có chữ thường, 2.239 tên dài; thư mục: 6, 154, 185) | **3.782/3.782 trùng từng chữ**; 0 chỉ khác hoa thường, 0 khác dạng Unicode, 0 không hỏi được |
| 727 ảnh, gốc là ổ: `stat_image` và bước kiểm đọc theo tên trong danh sách / gõ chữ hoa / gõ chữ thường | 727 / 727 / 699 (28 ảnh vốn đã chữ thường) **được**, `ref` trả về theo tên trên ổ; **giống `main`** từng ca |
| 277 ảnh, gốc là một thư mục ảnh trên USB, gốc gõ đúng / chữ thường / chữ hoa (3 lượt); mỗi lượt `ref` theo tên trong danh sách / gõ chữ hoa / gõ chữ thường | Mỗi lượt 277 / 277 / 170 (107 ảnh vốn đã chữ thường) **được**, giống `main` |
| `list_folder` (gốc là ổ: 164 lần; gốc là thư mục ảnh: 50 lần × 3 kiểu gõ gốc; mỗi thư mục gõ đúng, chữ hoa, chữ thường) | **Giống `main`** từng lần (số ảnh, tên ảnh, thư mục con, số bỏ qua); **0** lần báo "vừa bị thay đổi" hay đếm thư mục con vào liên kết |

**Không có mục nào bị báo "vừa bị thay đổi" oan**, nên **không sửa code** (không cần bước so không phân biệt hoa thường cho ổ không phân biệt hoa thường). Ổ FAT32 báo đường dẫn thật theo đúng tên trong danh sách, kể cả tên 8.3 có chữ thường (nhóm tôi lo nhất).

### Không rò handle (`leak_perf_t080.py leak`)

3.000 vòng × 18 lời gọi qua mọi nhánh mới (đọc, `stat`, xem thư mục; `ref` gõ khác hoa thường; ảnh quá lớn, rỗng, là thư mục, không có; thư mục anh em bị từ chối; lỗi `resolve`), mỗi vòng 14 lỗi gọn: **handle trước 165, sau 164 (chênh −1)**.

### Tốc độ (`leak_perf_t080.py perf`: cùng tiến trình, xen kẽ từng ảnh `main`/T-080, 200 ảnh 60 KB ở 3 tầng thư mục, 5 vòng, trung vị)

| Việc | Ổ cứng lượt 1 (`main` / T-080) | Ổ cứng lượt 2 | Ổ mạng `\\localhost\C$` lượt 1 | Ổ mạng lượt 2 |
|---|---|---|---|---|
| `stat_image` | 4,40 / 4,44 ms | 3,62 / 3,75 ms | 31,45 / 31,27 ms | 31,29 / 31,63 ms |
| `read_image_bytes` | 16,25 / 15,90 ms | 14,44 / 13,39 ms | 53,27 / 52,87 ms | 53,12 / 52,72 ms |
| `list_folder` (200 ảnh, 3 tầng) | 29,31 / 30,55 ms | 27,71 / 28,04 ms | 105,20 / 105,33 ms | 109,01 / 108,89 ms |

Ngang nhau. (Bản đầu của tôi luôn hỏi tên từng tầng khi đọc: qua ổ mạng chậm thêm khoảng 9 ms/ảnh, trên Google Drive bước hỏi tên tốn 7–8 ms/ảnh; nên bản cuối chỉ hỏi khi `resolve` không trả đúng chữ đã gõ.)

### Thử đột biến (`mutate_t080.py`: mỗi đột biến một bản sao riêng, 7 file test thư mục ảnh)

| Đột biến | Test hỏng (số ca) |
|---|---|
| M1 so đường dẫn thật kiểu cũ (NFC + `casefold`) | 25: `test_same_win_path_*` ×4, `test_windows_final_path_in_lookalike_folder_is_refused` ×12, SL-T079-1 ×8, LC-T079-1 |
| M2 so không phân biệt hoa thường (`upper()`, không gộp dạng Unicode) | 12: các ca hoa thường và `ß` (`test_same_win_path_*` ×2, thư mục anh em ×6, SL-T079-1 ×4, trong đó ca thư mục cha phân biệt hoa thường) |
| M3 xem thư mục (`_scan_held`) so kiểu cũ | 6: thư mục anh em ×4 (`list_folder`), LC-T079-1, ổ mạng UNC (`test_unc_network_root_blocks_junction_and_hides_paths`) |
| M4 câu báo theo `lstat` như cũ | 8: LC-T079-2 ×6, `test_problem_seen_only_by_path_lstat_is_reported_as_changed` ×2 |
| M5 lấy lại mục theo chữ đã gõ (không theo tên trên ổ) | 2: `test_problem_of_image_inside_folder_is_still_described` ×2 (`ref` gõ chữ hoa) |
| M6 đọc ảnh Windows luôn theo chữ đã gõ | 2: `test_windows_ref_typed_in_other_case_opens_by_disk_names[ntfs]`, `test_r2_short_name_of_normal_file_and_dir_is_refused` |
| M13 điều kiện hỏi lại tên so bằng `Path` (không phân biệt hoa thường) | 2: như M6 |
| M7 lỗi `resolve` luôn "không đọc được" (như cũ) | 15: `test_resolve_error_after_checked_levels` |
| M8 mọi lỗi `resolve` là "vừa bị thay đổi" | 9: ca không có quyền, lỗi ổ đĩa, lỗi Windows ổ mạng |
| M9 lỗi Windows xét theo `errno` | 3: ca lỗi Windows ổ mạng |
| M10 `stat_image` bỏ kiểm file thường/ẩn trên mục đã mở | 2: test của Soi Lỗi T-079 |
| M11 `stat_image` bỏ kiểm cỡ trên mục đã mở | 2: `test_stat_checks_size_on_the_opened_file` |
| M12 `_opened_stat` bỏ so định danh | 2: thay file tại chỗ, LC-T079-2 đối chứng |

Không đột biến nào sống sót.

### Nhánh Mac/Linux chạy bằng giả lập trên Windows (`posix_sim.py` của Thợ Máy T-079)

Bật `_OPEN_BY_DIR_FD`, giả `dir_fd` (chỉ thử luồng code: gọi đúng hàm, đóng fd, đổi lỗi thành câu báo; không giả được tính chất thật của fd). 7 file test: bản T-080 `12 failed, 537 passed, 25 skipped`; **không ca nào hỏng riêng ở bản mới** so với bản cũ. 12 ca hỏng là test chỉ dành cho nhánh Windows (hỏi đường dẫn thật, `_win_open`), bộ giả lập cho code đi nhánh Mac/Linux nên các test đó không áp dụng; bộ giả kiểm không còn fd thư mục nào chưa đóng sau mỗi test.

### Quét bí mật

`PYTHONUTF8=1 uvx detect-secrets scan --all-files` trong thư mục riêng chứa 4 file đã sửa, patch `git diff 417efea HEAD` và 1 file mồi tiếng Việt: chỉ file mồi có mục, bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`); **0 mục ở file thật**. Đã xóa file mồi.

Script thử nằm ở thư mục ghi chú chung của nhóm phiên, `T-080-tho-may-scripts/` (không commit).

## Đối chiếu tiêu chí xong

- [x] (1) LC-T079-1: so từng chữ ở `_win_handle_at` (đọc, `stat`) và `_scan_held` (xem thư mục); ép thắng 7/7 kiểu bị chặn; đọc thật trên NTFS, ổ mạng, Google Drive, USB FAT32 vẫn được (Drive, USB chỉ đọc thông tin, không mở nội dung, không in tên)
- [x] (2) LC-T079-2: câu báo chỉ tả mục trong thư mục ảnh (6 ca LC-T079-2 qua; ca 5 MB của Lá Chắn: "vừa bị thay đổi"); ảnh có vấn đề thật vẫn báo đúng (`test_problem_of_image_inside_folder_is_still_described`)
- [x] (3) LC-T079-3: "vừa bị thay đổi" khi `resolve` gặp liên kết (`test_resolve_error_after_checked_levels`, 24 ca); 3 ca SL-T079-L-1 chờ Linux
- [x] (4) Gỡ `xfail`: 8 ca SL-T079-1, 7 ca LC-T079 (chỉ xóa dấu); 3 ca SL-T079-L-1 giữ, ghi bên dưới
- [x] (5) Lớp chặn T-048, T-076, T-079 giữ nguyên (mọi test của các phiếu đó qua; `_resolve_inside` chỉ đổi cách đổi lỗi `resolve`; `_disk_names`, `_found_names`, `_listed_names`, `_match_disk_name`, `_posix_open_dir`, `_open_error`, `_win_open`, `_win_hold_dir`, `_win_handle_is_link`, `_win_final_path` không đổi); không rò handle; tốc độ như cũ
- [x] Chỉ sửa file được phép; test liên quan + `ruff check .` sạch

## Phần chưa kiểm được trên Linux/Mac

- **3 ca SL-T079-L-1** (`tests/test_soi_loi_t079_linux.py::test_sl_t079_l_1_resolve_race_is_reported_as_changed[read_image_bytes|stat_image|list_folder]`): cần lượt cloud Linux. Mong đợi XPASS(strict) (pytest báo hỏng); khi đó xóa khối `@pytest.mark.xfail(...)` ngay trên `@pytest.mark.parametrize("call", ...)` của test đó (dòng 244-249). Nếu vẫn XFAIL thì báo lại Thợ Máy.
- Các ca chỉ chạy trên Mac/Linux của các file liên quan (`tests/test_soi_loi_t079_linux.py` 9 ca, 2 ca trong `tests/test_soi_loi_t079.py`, các ca `posix_only` của `tests/test_images_folders.py` và `tests/test_images_folders_t063.py`): theo đọc code không đổi kết quả. Nhánh Mac/Linux của `_opened_stat`, `_open_image` vẫn gọi `_posix_open_dir` trực tiếp (test dò tên hàm gọi trong `test_soi_loi_t079_linux.py` vẫn đúng); đọc ảnh Mac/Linux không thêm bước hỏi tên.
- 6 ca LC-T079-2 và các ca lỗi `resolve` không gắn mã Windows chạy cả trên Linux/Mac (đi nhánh `_listed_names` + mở thư mục từng tầng): mới chạy thật trên Windows và qua giả lập.
- Mac (điều kiện cũ, giữ): chạy bộ test thư mục ảnh trên máy Mac thật trước khi dùng app trên Mac.

Lệnh cho lượt cloud Linux (root và `nobody`, như T-079):

```
uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_soi_loi_t079_linux.py tests/test_la_chan_t079.py tests/test_drafts_images.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py -rsxX
```

## Rủi ro và điểm cần chú ý

- **So từng chữ dựa vào việc ổ báo đường dẫn thật khớp tên trong danh sách thư mục** (tên đã lưu, hay đúng chữ đã mở). Đã đo đúng trên NTFS, ổ mạng SMB (máy chủ NTFS), Google Drive for Desktop, USB FAT32. **Chưa thử**: exFAT (thẻ nhớ, USB lớn); ổ mạng máy chủ Linux (Samba); ổ đám mây khác. Nếu một ổ báo đường dẫn thật khác chữ hoa thường so với danh sách, ảnh trên ổ đó sẽ báo "Ảnh vừa bị thay đổi, hãy thử lại" (an toàn trước, không lọt gì, nhưng không dùng được ảnh). `probe_usb_t080.py` (chỉ đọc thông tin, không in tên) chạy được ngay cho ổ mới.
- Đọc ảnh trên Windows với `ref` gõ khác tên trên ổ (hiếm: `ref` lấy từ danh sách thư mục hoặc từ `stat_image`) thêm một bước hỏi tên từng tầng, như `stat_image` vốn có.
- `_checked_file` chỉ tốn thêm khi ảnh có vấn đề (lấy lại mục trong thư mục ảnh rồi mới báo). Ổ không cho mở handle hỏi thuộc tính (rất hiếm) thì ảnh có vấn đề báo "Không đọc được mục này…" thay câu cụ thể.
- `_open_image` giữ chữ ký `(root, parts, path)` vì test của Soi Lỗi bọc hàm này theo đúng chữ ký; `path` nay là `gốc/parts` viết như ổ báo tên.
- Hằng `_NAMES_FROM_RESOLVE` vẫn sai nghĩa với tên (Lá Chắn T-076 ghi nhận): ngoài phạm vi, không đổi.

## Đề xuất

- **Chỉ Huy:** chuyển Soi Lỗi rút gọn rồi Lá Chắn rút gọn (F1). Lượt cloud Linux chạy lệnh ở trên, xóa `xfail` SL-T079-L-1 khi XPASS.
- Ổ USB `F:` FAT32: đã thử (mục Bằng chứng), dùng được. Khi có thẻ nhớ hay USB exFAT, chạy `probe_usb_t080.py` một lượt (chỉ đọc thông tin) trước khi dùng ảnh từ đó; nếu có ảnh "chỉ khác hoa thường" thì thêm bước so không phân biệt hoa thường cho ổ không phân biệt hoa thường (cờ ổ `FILE_CASE_SENSITIVE_SEARCH`).
- Ghi nhận, để nguyên: câu "Không tìm thấy / liên kết tắt / ẩn" của `_resolve_inside` khi bị tráo (mức có/không, Lá Chắn T-079 không bắt sửa); ENOTDIR ở vòng `lstat` (`ref` dạng `a.jpg/b.jpg` trên Linux báo "không đọc được" thay "không tìm thấy").

## Câu hỏi cho chủ dự án

Không có. (Câu hỏi trước "cho thử ổ USB `F:`": chủ dự án đồng ý, Chỉ Huy B chuyển ngày 2026-10-23; đã thử, kết quả ở mục Bằng chứng.)

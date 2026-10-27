# Báo cáo T-082 · Sửa câu báo đọc ảnh khi bị tráo thư mục (SL-T080-1, -2, -L-1) · Thợ Máy

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-082](../tickets/T-082-cau-bao-doc-anh-sau-t080.md) |
| Ngày nộp | 2026-10-27 (giờ máy lúc viết báo cáo: 17:56) |
| Nhánh | `team/T-082` (tạo từ `main` `b60054f`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4, người dùng thường; máy chạy song song agent khác. Không có Linux/Mac, **không chạy cloud** (theo lời giao) |
| Kết quả | **Hoàn thành trên Windows.** 10 ca `xfail` của Windows (SL-T080-1 ×3, SL-T080-2, SL-T080-L-1 ×6) XPASS, đã gỡ dấu. 6 ca chỉ chạy trên Linux/Mac (`tests/test_soi_loi_t080_linux.py`) **chưa kiểm được**, giữ `xfail` |

## Tóm tắt (cho chủ dự án)

Khi thư mục ảnh bị dời đi hay bị tráo đúng lúc app đọc, app không còn báo các câu sai nghĩa "Không đọc được… (không có quyền hoặc ổ đĩa vừa bị ngắt)" hay "Đường dẫn nằm ngoài thư mục ảnh được phép." nữa, mà báo "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại." (hoặc "Không tìm thấy ảnh hoặc thư mục này…" khi mục vừa bị dời đi, giống bản Mac/Linux). Chỉ đổi câu chữ: mọi trường hợp vẫn bị từ chối như trước, không lớp chặn nào bị nới. Tôi chạy lại các phép "ép kẻ tấn công luôn thắng" của Lá Chắn và Soi Lỗi (ổ máy và ổ mạng): vẫn 0 lần lọt. Dùng bình thường không thấy gì khác. Phần chạy trên Mac/Linux chưa kiểm được (không chạy cloud).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/folders.py` | `_resolve_inside`: `resolve` ra ngoài gốc → "vừa bị thay đổi"; ra mục khác → "vừa bị thay đổi", tên khác của **chính mục đó** (tên ngắn 8.3) → giữ "tên ngắn hoặc tên khác"; lỗi Windows 5 thì kiểm lại từng tầng. `_opened_stat` (Windows): lỗi 2, 3 → "Không tìm thấy…". `_read_entries`: thư mục vừa kiểm mà không thấy → "vừa bị thay đổi". `_checked_file` không trả đường dẫn `resolve` nữa, chỉ trả cờ. Docstring `_resolve_inside`, `_checked_file`, `_win_open`. Thêm `_still_same_entry`, `_levels_changed`, `_ERROR_ACCESS_DENIED`; bỏ `_MSG_OUTSIDE` (hết chỗ dùng) |
| `tests/test_images_folders.py` | Thêm 35 ca T-082 (13 ca chạy cả trên Mac/Linux). Sửa **một dòng kiểm câu báo** của test T-048 `test_resolve_check_alone_blocks_junction_outside` (xem mục Rủi ro 1) |
| `tests/test_soi_loi_t080.py` | Chỉ gỡ 3 dấu `xfail` (SL-T080-1, SL-T080-2, SL-T080-L-1 phần Windows): diff chỉ có dòng xóa |
| `docs/team/reports/T-082-tho-may.md` | Báo cáo này |

Không sửa `app/**`, `config/**`, `seo_app/storage/**`, `tests/test_soi_loi_t080_linux.py`; không thêm thư viện.

## Cách sửa từng lỗi

### SL-T080-L-1 · `resolve` đi qua tầng vừa bị tráo (mọi HĐH)

Vòng `lstat` của `_resolve_inside` vừa thấy mọi tầng là mục thật (không liên kết), tên an toàn (không `..`), gốc đã `resolve`. Nên:

- `resolve` ra **ngoài gốc** chỉ có thể vì một tầng vừa bị tráo thành liên kết → `_ChangedError` (trước: `_LinkError("Đường dẫn nằm ngoài…")`). Cả hai đều là `_LinkError`: vẫn từ chối, khi quét vẫn đếm vào `links`.
- `resolve` ra **tên khác** (khác khóa tên): `lstat` mục ở `gốc/tên resolve trả` và so định danh với mục cuối vừa `lstat` (`_still_same_entry`). **Cùng mục** (tên ngắn 8.3 thật của Windows) → giữ `_MSG_ALIAS` như điều kiện của Lá Chắn T-080; **mục khác, không còn, là liên kết, hay không hỏi được** → `_ChangedError`. Ổ không có số inode thì giữ `_MSG_ALIAS` (như `_same_file`).
- Mục để so được ghép **từ gốc và tên**, không `lstat` chính đường dẫn `resolve` trả (Việc 4: đường dẫn đó có thể nằm trong thư mục anh em của gốc). Test mới kiểm app không `lstat` gì trong thư mục đích ngoài gốc hay thư mục anh em dấu Kelvin.

Tôi dùng một luật cho mọi HĐH (so định danh), không tách "Mac/Linux luôn báo thay đổi" như gợi ý của Soi Lỗi Linux: trên Mac/Linux không có tên ngắn nên mục ở tên khác gần như luôn khác định danh → "vừa bị thay đổi"; riêng ca hai tên là hard link của cùng một file thì báo "tên ngắn hoặc tên khác của cùng một mục" (đúng nghĩa, vẫn từ chối).

### SL-T080-1 · Windows báo "không có quyền" khi thư mục vừa bị dời đi

- **`_opened_stat`** (ca đo được 1.139 lần khi tráo thật): đặt mã lỗi Windows về 0 ngay trước `_win_open`, mở hỏng thì đọc `ctypes.get_last_error()`. Lỗi 2 (không thấy file) hay 3 (không thấy thư mục trên đường đi) mà `_disk_names` vừa thấy mục ở đúng tên đó → **"Không tìm thấy ảnh hoặc thư mục này (có thể đã đổi tên, đã xóa…)"**, đúng câu bản Mac/Linux của bước này đang báo. Lỗi khác (5, 32…) giữ "Không đọc được…". Không đổi `_win_open` (vẫn trả `fd | None`), vì nhiều test cũ thay `_win_open` bằng hàm trả `None`.
  - Tôi chọn "Không tìm thấy" thay vì "vừa bị thay đổi": test SL-T080-1 nhận cả hai, nhưng test cũ của Soi Lỗi `tests/test_soi_loi_t079.py::test_stat_of_file_deleted_before_opened_stat_is_a_plain_error` (file bị xóa ngay trước bước này) chỉ nhận "Không tìm thấy" hay "Không đọc được". Bản nháp đầu báo "vừa bị thay đổi" làm hỏng test đó, nên tôi đổi theo, không sửa test của người khác.
  - Đặt mã lỗi về 0 trước khi gọi để mã lỗi của lần gọi Windows trước (ví dụ bước hỏi tên trên ổ) không lẫn vào câu báo; có test riêng cho chỗ này.
- **`resolve` gặp lỗi 5** (junction đang bị xóa, 138 lần khi tráo thật): theo gợi ý của Soi Lỗi, kiểm lại từng tầng của vòng `lstat` (`_levels_changed`): tầng nào vừa mất, thành liên kết hay thành mục khác (khác định danh) → "vừa bị thay đổi"; còn nguyên → giữ "Không đọc được" (không phân biệt được với lỗi quyền thật chỉ bằng mã lỗi). Chỉ áp cho lỗi Windows 5; lỗi khác (ổ mạng 59, ổ rút…) giữ nguyên như T-080.

### SL-T080-2 · xem thư mục không giữ được thư mục, thư mục vừa bị dời đi (Windows)

`_read_entries` chỉ được gọi cho thư mục vừa kiểm xong (giữ được handle, mở bằng fd, hay kiểm đường đi ở nhánh không giữ được), nên `os.scandir` báo `FileNotFoundError` là thư mục vừa bị dời đi hay xóa → `_ChangedError` (trước: "Không đọc được thư mục này (không có quyền…)"). Lỗi khác (không có quyền…) giữ nguyên. Không làm LC-T048-2, -3 (liệt kê qua chính handle đang giữ): chưa có phiếu, ngoài phạm vi.

### Việc 4 của Lá Chắn T-080 · đường dẫn `resolve` chỉ để so

- (a) **Docstring** `_resolve_inside`, `_checked_file`: đường dẫn `resolve` trả chỉ để so chuỗi, chỗ gọi không được mở, `stat` hay liệt kê (nêu lý do: dấu Kelvin, thư mục anh em); đọc, `stat`, xem thư mục đi qua `_disk_names`, `_opened_stat`, `_open_image`, `_Scan`.
- (b) **Làm chặt**: `_checked_file` trả `(gốc, lstat, exact)` thay vì `(gốc, đường dẫn resolve, lstat)`; `exact` = "`resolve` trả đúng `gốc/parts` từng chữ" (chính phép so `read_image_bytes` vẫn làm). `list_folder` đổi tên biến không dùng `directory` → `_path`. `_resolve_inside` vẫn trả đường dẫn (để `_checked_file` so; đổi kiểu trả về sẽ làm hỏng các test cũ bọc `_resolve_inside`).

## Bằng chứng

### Test liên quan và ruff

```
# Mốc trước khi sửa (b60054f), lệnh của phiếu + tests/test_soi_loi_t080_linux.py:
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py tests/test_soi_loi_t080_linux.py -rxX
400 passed, 36 skipped, 13 xfailed in 40.26s
  13 xfail = R2-1 ×2, R2-2 (T-048) + SL-T080-1 ×3, SL-T080-2, SL-T080-L-1 phần Windows ×6

# Code mới, trước khi gỡ dấu: 10 ca SL-T080 đều XPASS(strict); thêm 3 test cũ hỏng (đã xử lý, xem trên và mục Rủi ro 1)

# Code cuối, đúng lệnh của phiếu:
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py -rsxX
445 passed, 24 skipped, 3 xfailed in 34.82s
  3 xfail = R2-1 ×2, R2-2 (T-048, không thuộc phiếu này); 0 hỏng, 0 XPASS
  so mốc: +35 ca mới, 10 xfail thành qua; 24 bỏ qua = ca chỉ Mac/Linux hay cần symlink (máy không cho tạo, lỗi 1314) như mốc

# Test của mọi file khác gọi tới folders.py (grep "images.folders|ImageLibrary" trong tests/), thêm test_app_pages.py:
$ uv run pytest tests/test_soi_loi_t080_linux.py tests/test_soi_loi_t079_linux.py tests/test_app_images.py tests/test_drafts_images.py tests/test_images_process.py tests/test_images_tags.py tests/test_la_chan_t056.py tests/test_la_chan_t074.py tests/test_la_chan_t076.py tests/test_soi_loi_t049.py tests/test_soi_loi_t052.py tests/test_soi_loi_t055.py tests/test_soi_loi_t056.py tests/test_soi_loi_t067.py tests/test_soi_loi_t070.py tests/test_soi_loi_t071.py tests/test_soi_loi_t074.py tests/test_soi_loi_t076.py tests/test_soi_loi_t077.py tests/test_soi_loi_t086.py tests/test_soi_loi_t089.py tests/test_t086_send_state.py tests/test_t089_send_draft.py tests/test_app_pages.py -rfxX
2185 passed, 27 skipped, 11 xfailed in 1403.00s (0:23:22)
  0 hỏng, 0 XPASS; 11 xfail đều có từ trước, không liên quan (SL-T067 ×4, SL-T070-4 ×7)
  27 bỏ qua, trong đó 12 ca của tests/test_soi_loi_t080_linux.py (chỉ chạy trên Linux/Mac)
  (máy bận vì agent khác chạy song song nên lâu)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_images_folders.py seo_app/images/folders.py tests/test_soi_loi_t080.py
3 files already formatted
```

- **Test mới chạy trên bản cũ** (`git archive HEAD` ra thư mục nháp, chỉ thay `tests/test_images_folders.py` bằng bản mới): **24/35 ca hỏng đúng chỗ** (9 ca `resolve` qua tầng bị tráo, 9 ca lỗi 5 có tầng đổi, 4 ca lỗi 2/3, 1 ca thư mục mất lúc đọc danh sách, 1 ca `_checked_file` còn trả đường dẫn); 11 ca còn lại là ca đối chứng giữ câu cũ (tên ngắn 8.3 thật, hard link, lỗi 5 không đổi gì, lỗi 5/32 lúc mở handle, mã lỗi cũ không lẫn vào), qua ở cả hai bản.
- Ca 8.3 thật chạy được trên máy này (ổ có tên ngắn): đọc, kiểm, xem thư mục bằng `THUMUC~1/…` vẫn ra "tên ngắn hoặc tên khác".

### Ép kẻ tấn công "luôn thắng" (script của Lá Chắn và Soi Lỗi T-080, chạy nguyên bản trên code T-082)

| Script | Kết quả |
|---|---|
| `lc79_forced.py` (Lá Chắn, ổ máy): 7 kiểu đích (ngoài gốc, anh em NFD / Kelvin / `ß` / khác hoa thường, trong gốc NFD, ngoài gốc quá cỡ) × đọc, `stat` | **0 lọt**: cả 14 lời gọi "Ảnh vừa bị thay đổi…"; thư mục sạch sau 7/7 |
| `lc80_forced_unc.py` (Lá Chắn, qua `\\localhost\C$`): 6 kiểu đích (bỏ "khác hoa thường" như bản gốc) | **0 lọt**: cả 12 lời gọi "Ảnh vừa bị thay đổi…"; sạch sau 6/6 |
| `sl80_forced_win.py` (Soi Lỗi): 396 ca, 4 kiểu ép (`lstat`/`open`, + hỏi tên, `ref` gõ chữ hoa, chỉ lúc `resolve`), đọc / `stat` / xem thư mục | **0 lọt nội dung, 0 lọt cỡ, 0 lọt tên, 0 câu tả file ngoài, 0 lộ đường dẫn**, sạch sau 396/396. Bảng câu báo giống hệt bản T-080 (`forced_code_t080.json` của Soi Lỗi), trừ 51 ca kiểu ép `resolve`: "Đường dẫn nằm ngoài thư mục ảnh được phép." → **"Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại."** (đúng SL-T080-L-1). 16 ca "không ép được" giống T-080 |

### Quét bí mật

`PYTHONUTF8=1 uvx detect-secrets scan --all-files` trên 3 file đã sửa, kèm một file mồi có chữ tiếng Việt và khóa AWS giả (đặt tạm trong worktree, xóa ngay sau lượt quét): file mồi bị bắt 3 loại (lượt quét chạy thật), **3 file đã sửa: 0 mục**. Báo cáo này không chứa khóa hay đường dẫn máy.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: sửa SL-T080-1 (`_opened_stat` lỗi 2/3; `resolve` lỗi 5), SL-T080-2 (`_read_entries`), SL-T080-L-1 (`_resolve_inside`) theo gợi ý của Soi Lỗi; điều kiện 2 của Lá Chắn T-080: Việc 4 (a) docstring và (b) `_checked_file` trả cờ; Windows giữ `_MSG_ALIAS` cho tên ngắn 8.3 thật (`test_real_short_8_3_name_keeps_alias_message`)
- [x] Yêu cầu 2: không nới lớp chặn nào; mọi ca vẫn từ chối (`_ChangedError` là `_LinkError`); ép thắng ổ máy và `\\localhost\C$` vẫn 0 lọt (mục Ép thắng). Không chạy lại phép tráo thật (đua) của Soi Lỗi: việc của lượt kiểm thử
- [x] Yêu cầu 3 (phần Windows): 10 ca XPASS, đã gỡ dấu `xfail` trong `tests/test_soi_loi_t080.py` (chỉ xóa dấu)
- [ ] Yêu cầu 3 (phần Linux/Mac): **chưa kiểm được** (không chạy cloud theo lời giao), giữ `xfail` 6 ca `tests/test_soi_loi_t080_linux.py` (xem Rủi ro 2)
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục Bằng chứng)
- [x] Có test cho phần logic mới (35 ca, 24 ca bắt được lỗi trên bản cũ)
- [x] Báo cáo nộp tại `docs/team/reports/T-082-tho-may.md`

## Rủi ro và điểm cần chú ý

1. **Đã sửa một dòng kiểm câu báo của test cũ** `tests/test_images_folders.py::test_resolve_check_alone_blocks_junction_outside` (test của chính vai Thợ Máy ở T-048, commit `ca32762`; file nằm trong phạm vi phiếu cho sửa). Test này tắt lớp kiểm liên kết rồi xem lớp thứ hai (`resolve` + `is_relative_to`) còn chặn không, và kiểm câu "ngoài thư mục". Phiếu yêu cầu đổi đúng câu đó, nên tôi đổi dòng `assert "ngoài thư mục" in str(exc)` thành `assert isinstance(exc, folders._LinkError) and "thay đổi" in str(exc)` (kèm chú thích); phần còn lại của test giữ nguyên, lớp thứ hai vẫn chặn. Không sửa test nào của agent khác. Chỉ Huy/Soi Lỗi xem lại giúp.
2. **6 ca Linux/Mac giữ `xfail(strict=True)`**. Theo đọc code chúng sẽ XPASS: chúng đi đúng nhánh của 6 ca Windows đã XPASS (ra ngoài gốc → "vừa bị thay đổi"; tới `y` trong gốc → so định danh khác → "vừa bị thay đổi"), và 13 ca mới chạy được trên Mac/Linux kiểm cùng nhánh bằng `resolve` giả. Hệ quả: khi chạy trên Linux/Mac, 6 ca này sẽ báo **XPASS(strict) = FAILED** tới khi gỡ dấu. Trước lượt cloud Linux hay máy Mac thật, cần biết điều này; thấy XPASS thì chỉ xóa 6 dòng dấu `xfail`. Ngoài ra chưa ai chạy 13 ca mới trên Linux/Mac.
3. **"Ra ngoài gốc" nay luôn là "vừa bị thay đổi"**. Đúng khi lớp kiểm liên kết (`_is_link_stat`) nhận ra mọi loại liên kết. Nếu sau này gặp một loại liên kết lạ mà lớp đó bỏ sót, người dùng sẽ thấy "vừa bị thay đổi, hãy thử lại" mỗi lần thay vì "nằm ngoài thư mục ảnh": vẫn từ chối, chỉ câu báo kém rõ.
4. **Câu báo SL-T080-1 ở `_opened_stat` là "Không tìm thấy…"**, không phải "vừa bị thay đổi" (lý do ở trên: giữ đúng test cũ của Soi Lỗi, giống Mac/Linux). Câu này có ý "có thể đã đổi tên, đã xóa" nên không sai nghĩa.
5. **Lỗi 5 của `resolve`**: chỉ phát hiện được khi lúc kiểm lại tầng vẫn còn khác; tầng bị tráo rồi trả lại trước khi kiểm lại thì vẫn "Không đọc được…" (như gợi ý của Soi Lỗi, không phân biệt được với lỗi quyền thật).
6. **Đếm khi quét**: thư mục con vừa bị dời đi giữa lúc kiểm và lúc đọc danh sách nay đếm vào `links` (như mọi ca `_ChangedError` khác khi quét), trước là `unreadable`. Chỉ xảy ra khi bị tráo; tổng số mục bỏ qua không đổi.
7. Code T-048 còn một chỗ `lstat` đường dẫn `resolve` trả: `_resolve_inside` khi `parts` rỗng (chính thư mục gốc). Số liệu chỉ dùng kiểm "là thư mục" và so định danh, không đọc gì. Tôi để nguyên (ngoài yêu cầu "chỉ đổi câu báo").

## Đề xuất

1. **Chỉ Huy:** trước lượt cloud Linux (khi chủ dự án đồng ý) hay khi chạy trên Mac thật, chạy `tests/test_soi_loi_t080_linux.py` cùng `tests/test_images_folders.py` với `-rsxX`; 6 ca SL-T080-L-1 XPASS thì gỡ dấu `xfail` (chỉ xóa dấu).
2. **Thợ Máy (phiếu sau, nếu Chỉ Huy thấy cần):** Linux trả ELOOP khi mở file vừa thành symlink (`_open_image`, `O_NOFOLLOW`) đang báo "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)."; Soi Lỗi Linux gợi ý tách thành "Ảnh vừa bị thay đổi…". Tôi không làm vì là gợi ý tùy chọn, không có test nào và không kiểm được trên Linux. LC-T048-2, -3 (liệt kê qua chính handle đang giữ) cũng còn để ngỏ.

## Lượt 2 (2026-10-27 tới 2026-10-28, sau Soi Lỗi rút gọn ĐẠT CÓ ĐIỀU KIỆN `7e2b4b3`)

Chỉ Huy B giao sửa 2 lỗi Thấp của [báo cáo Soi Lỗi T-082](T-082-soi-loi.md), trước khi qua Lá Chắn. Nhánh từ `7e2b4b3`.

### Đã sửa

| Lỗi | Sửa | File |
|---|---|---|
| **SL-T082-1** (chỉ test, Mac): ca `anh-em-kelvin` tạo thư mục `Ảnh Kho` (dấu Kelvin) cạnh `Ảnh kho`; APFS mặc định coi hai tên là một nên lệnh tạo đích ghi đè ảnh trong gốc rồi `assert` hỏng oan | Theo gợi ý của Soi Lỗi: trước khi ghi đích, ổ đã thấy tên dấu Kelvin (tức coi hai tên là một) thì `pytest.skip("ổ coi hai tên là một")`; bỏ `assert` sau khi ghi. Trên Windows (NTFS) và Linux (ext4) ca vẫn chạy | `tests/test_images_folders.py` (test của chính T-082) |
| **SL-T082-2** (Windows, câu báo): thư mục `x` bị **đổi tên** trong gốc đúng lúc `resolve` giữ handle, `resolve` trả đường dẫn theo tên mới; mục ở tên mới đúng là mục vừa `lstat` nên app báo "tên ngắn hoặc tên khác" | Theo gợi ý của Soi Lỗi: ở nhánh tên khác của `_resolve_inside`, chỉ giữ câu "tên ngắn hoặc tên khác" khi **cả** mục ở tên `resolve` trả **lẫn** mục ở chữ đã gõ (`gốc/parts`) vẫn là mục vừa `lstat` (`_still_same_entry` cả hai); chữ đã gõ không còn trỏ tới mục → `_ChangedError` ("Thư mục vừa bị thay đổi…"). Vẫn từ chối. Tên ngắn 8.3 thật và hard link thỏa cả hai nên giữ câu cũ. Thêm docstring | `seo_app/images/folders.py` |

Thêm 3 test `test_folder_renamed_during_resolve_is_reported_as_changed` (đọc, `stat`, xem thư mục; chạy cả trên Mac/Linux): `resolve` giả đổi tên `x` thành `x-moi` trong gốc rồi trả đường dẫn theo tên mới, mong "vừa bị thay đổi" và `_LinkError`. Không sửa test nào của agent khác.

Giới hạn (như Soi Lỗi đã nêu, chấp nhận): thư mục bị đổi tên rồi trả lại tên cũ trước bước kiểm này thì vẫn ra câu "tên ngắn hoặc tên khác" (không phân biệt được).

### Bằng chứng lượt 2

```
# Test mới trên bản lượt 1 (git archive HEAD = 7e2b4b3, chỉ thay tests/test_images_folders.py):
3 failed (test_folder_renamed_during_resolve_is_reported_as_changed ×3: ra "tên ngắn hoặc tên khác"), 12 passed
  12 qua ở cả hai bản: 9 ca resolve qua tầng bị tráo, 2 ca hard link, 1 ca tên ngắn 8.3 thật (giữ câu "tên ngắn")

# Lệnh test của phiếu, code lượt 2:
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py -rfxX
448 passed, 24 skipped, 3 xfailed in 53.63s
  so lượt 1: +3 ca mới; 3 xfail = R2-1 ×2, R2-2 (T-048); 0 hỏng, 0 XPASS

# Các file test khác gọi tới folders.py + test_app_pages.py (cùng danh sách lượt 1):
1 failed, 2184 passed, 27 skipped, 11 xfailed in 3328.90s (0:55:28)
  1 hỏng: tests/test_app_images.py::test_spot_is_real_picker_and_nothing_scanned_until_opened,
  "AppTest script run timed out after 30(s)" (máy bận: cùng bộ test lượt 1 chạy 23 phút, lượt này 55 phút)
  Chạy lại riêng ca đó: 1 passed; chạy lại cả tests/test_app_images.py: 58 passed
  11 xfail như lượt 1 (SL-T067 ×4, SL-T070-4 ×7), 0 XPASS

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/images/folders.py tests/test_images_folders.py
2 files already formatted
```

- Ép thắng chạy lại trên code lượt 2: `lc79_forced.py` (ổ máy) 7/7 kiểu đích, `lc80_forced_unc.py` (`\\localhost\C$`) 6/6: **0 lọt**, cả đọc lẫn `stat` đều "Ảnh vừa bị thay đổi…", thư mục sạch sau. `sl80_forced_win.py` (Soi Lỗi) 396 ca: 0 lọt nội dung, cỡ, tên; 0 câu tả file ngoài; 0 lộ đường dẫn; sạch sau 396/396; bảng câu báo giống hệt lượt 1 (phép ép này không đổi tên thư mục trong gốc nên không chạm SL-T082-2).
- Chưa chạy lại phép tráo thật (đua) để đếm câu "tên ngắn" (Soi Lỗi đề nghị tự chạy lại sau khi sửa).
- 6 ca Linux/Mac của `tests/test_soi_loi_t080_linux.py` vẫn giữ `xfail`, chưa kiểm được (như lượt 1, Rủi ro 2); 16 ca mới chạy được trên Mac/Linux (13 lượt 1 + 3 lượt 2) cũng chưa ai chạy ở đó.

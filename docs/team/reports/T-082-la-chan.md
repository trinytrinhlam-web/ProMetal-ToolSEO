# Biên bản bảo mật T-082 · Sửa câu báo đọc ảnh khi bị tráo thư mục (SL-T080-1, -2, -L-1) · Lá Chắn (rút gọn)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable, chủ dự án đã duyệt) |
| Phiếu được kiểm | [T-082](../tickets/T-082-cau-bao-doc-anh-sau-t080.md) · mức kiểm **rút gọn** (F1) |
| Phạm vi | diff `b60054f..453208b` (`team/T-082`: lượt 1 `552f870`, lượt 2 sửa SL-T082-1, -2): `seo_app/images/folders.py` (+88/−16), `tests/test_images_folders.py` (+269/−1: 38 ca mới, 1 dòng kiểm câu báo của test T-048), `tests/test_soi_loi_t080.py` (−26: gỡ 3 dấu `xfail`), 2 báo cáo. Đọc báo cáo [Thợ Máy](T-082-tho-may.md) (2 lượt), [Soi Lỗi](T-082-soi-loi.md), biên bản của tôi [T-080](T-080-la-chan.md) (Việc 4, Điều kiện 2) |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (uv 0.13.4), người dùng thường; NTFS cục bộ và ổ chia sẻ `\\localhost\C$` (SMB). Máy chạy song song agent khác. Không chạy cloud Linux, không có Mac: phần Linux/Mac kiểm bằng đọc mã |
| Ngày | 2026-10-28 |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. SL-T080-1, -2, -L-1 (và SL-T082-1, -2 của Soi Lỗi) đóng; điều kiện 2 của Lá Chắn T-080 đạt; không lớp chặn nào bị nới. **Gộp `main` được ngay** |

## Tóm tắt (cho chủ dự án)

T-082 chỉ sửa câu chữ của thông báo lỗi khi thư mục ảnh bị dời đi hay bị tráo đúng lúc app đọc: app nay báo "Thư mục vừa bị thay đổi trong lúc đọc, hãy thử lại" (hoặc "Không tìm thấy…" khi mục vừa bị dời đi) thay vì các câu sai nghĩa "không có quyền", "nằm ngoài thư mục ảnh", "tên ngắn hoặc tên khác". Tôi kiểm từng chỗ sửa: mọi trường hợp vẫn bị từ chối như trước, không chỗ nào bị nới.

Tôi chạy lại các phép "ép kẻ tấn công luôn thắng" của mình trên ổ máy và qua ổ mạng, thêm một phép thử mới tráo thư mục thật đúng lúc app hỏi vị trí thật của ảnh: 0 lần đọc được gì bên ngoài thư mục ảnh, câu báo không lộ đường dẫn trên máy, không tả file bên ngoài. Bản đang dùng (`main`) cũng không lọt nhưng báo sai nghĩa; bản T-082 báo đúng. **Gộp được ngay.**

Phần chạy trên Mac/Linux mới kiểm bằng đọc mã (không chạy cloud). Lần chạy Mac/Linux tới, 6 ca test cũ sẽ báo "hỏng" vì lỗi chúng ghi lại đã được sửa: chỉ cần gỡ dấu "lỗi đã biết" của 6 ca đó.

## Lỗi phát hiện

**Không phát hiện lỗi mới.** Không viết `tests/test_la_chan_t082.py` (phiếu chỉ yêu cầu khi có lỗi).

| Lỗi của phiếu | Kết quả | Bằng chứng |
|---|---|---|
| SL-T080-L-1 (`resolve` đi qua tầng vừa bị tráo) | Đóng | Ra ngoài gốc → `_ChangedError` (`seo_app/images/folders.py:712-713`); ra tên khác → so định danh, cùng mục (tên ngắn 8.3 thật, hard link) giữ "tên ngắn hoặc tên khác", khác → `_ChangedError` (`:717-728`). Phép thử mới Việc 2 |
| SL-T080-1 (Windows, "không có quyền" khi thư mục vừa bị dời) | Đóng | `_opened_stat` lỗi 2, 3 → "Không tìm thấy…" (`:993-1001`); `resolve` lỗi 5 → kiểm lại từng tầng (`:701-711`, `_levels_changed` `:479-485`) |
| SL-T080-2 (xem thư mục, thư mục vừa bị dời) | Đóng | `_read_entries` `FileNotFoundError` → `_ChangedError` (`:1202-1205`) |
| SL-T082-2 (thư mục bị **đổi tên** đúng lúc `resolve`, lượt 2) | Đóng | Chỉ giữ "tên ngắn…" khi **cả** tên `resolve` trả **lẫn** chữ đã gõ vẫn trỏ tới mục vừa `lstat` (`:726`). Phép thử `doi-ten` Việc 2: "vừa bị thay đổi" |
| SL-T082-1 (3 ca test hỏng oan trên Mac, lượt 2) | Đóng (đọc mã) | Ổ đã thấy tên dấu Kelvin thì `pytest.skip` trước khi ghi đích; trên Windows ca vẫn chạy và qua |
| Điều kiện 2 của Lá Chắn T-080 (Việc 4 (a), (b)) | Đạt | Việc 3 |

## Việc 1 · Soát diff

So thân từng hàm (AST, bỏ docstring) giữa `b60054f` và `453208b` (`lc80_ast.py`): **đổi** `_resolve_inside`, `_checked_file`, `stat_image`, `_opened_stat`, `read_image_bytes`, `list_folder` (chỉ đổi tên biến), `_Scan._read_entries`; **thêm** `_still_same_entry`, `_levels_changed`, hằng `_ERROR_ACCESS_DENIED`; **bỏ** `_MSG_OUTSIDE` (không còn chỗ dùng ở `seo_app/`, `app/`, `tests/`); **86 phần giữ nguyên**, gồm mọi lớp chặn cũ (`_parse_rel`, `_is_safe_name`, `_is_link_stat`, `_same_file`, `_same_win_path`, `_win_handle_at`, `_win_handle_is_link`, `_win_final_path`, `_win_open` (chỉ đổi docstring), `_posix_open_dir`, `_disk_names`, `_found_names`, `_listed_names`, `_open_image`, `_scan_held`, `_scan_by_fd`, `_visit`).

| Chỗ đổi | Đánh giá F1 | Bằng chứng |
|---|---|---|
| `_resolve_inside`: ra ngoài gốc | Vẫn từ chối: `_ChangedError` là `_LinkError` như `_LinkError(_MSG_OUTSIDE)` cũ (khi quét vẫn đếm `links`) | `:712-713` |
| `_resolve_inside`: ra tên khác | Hai nhánh đều **ném lỗi** (`_MSG_ALIAS` hay `_ChangedError`); phép so chỉ chọn câu. Mục đem so ghép **từ gốc và tên** (`root.joinpath(*actual)`, `current`), không theo đường dẫn `resolve` trả (có thể nằm trong thư mục anh em): test theo dõi `os.lstat` xác nhận app không `lstat` gì trong đích ngoài gốc hay thư mục anh em. `actual` lấy từ `relative_to(root)` nên chỉ là tên, không `..`, không ổ đĩa | `:717-728`; `test_resolve_through_swapped_level_is_reported_as_changed` |
| `_resolve_inside`: `resolve` lỗi 5 | Chỉ Windows, chỉ lỗi 5; `_levels_changed` `lstat` lại **đúng các tầng** vòng kiểm vừa `lstat` (`gốc/parts[:k]`), rồi chọn giữa hai câu từ chối | `:701-711`, `:479-485` |
| `_opened_stat` (Windows) | Đặt mã lỗi về 0 rồi mở; hỏng thì vẫn ném (lỗi 2, 3 → "Không tìm thấy…", khác → "Không đọc được…") | `:993-1001` |
| `_read_entries` | `FileNotFoundError` → `_ChangedError`; vẫn ném, vẫn bỏ kết quả thư mục đó (`_scan_dir`) | `:1202-1205` |
| `_checked_file` | Trả `(gốc, lstat, exact)`; `exact` đúng phép so chuỗi T-080 vẫn làm ở `read_image_bytes`, nay làm trong `_checked_file` nên đường dẫn `resolve` không ra khỏi hàm | `:892-917`, `:1064` |
| Lớp chặn | Không chỗ nào biến từ chối thành chấp nhận: mọi nhánh mới kết thúc bằng `raise`; phép so đường dẫn thật từng chữ, so định danh, mở từng tầng không đổi | AST ở trên |
| Thư viện, cấu hình | Không `import` mới; `uv.lock`, `pyproject.toml`, `.gitignore`, `app/`, `config/` không đổi | `git diff --stat b60054f..453208b -- uv.lock pyproject.toml .gitignore app config`: rỗng |
| Test T-048 đổi một dòng (Chỉ Huy đã duyệt) | Chấp nhận: `test_resolve_check_alone_blocks_junction_outside` vẫn tắt lớp kiểm liên kết và đòi lớp thứ hai (`is_relative_to`) chặn; câu kiểm mới đòi `_LinkError` **và** "thay đổi" (câu "Ảnh vừa bị thay đổi" của lớp so đường dẫn thật là `ImageFolderError` thường, không qua). Đột biến bỏ `is_relative_to` làm test hỏng (Soi Lỗi M13) | `tests/test_images_folders.py:771-773` |
| Gỡ `xfail` | `tests/test_soi_loi_t080.py`: chỉ dòng xóa (0 dòng thêm), 3 khối `@pytest.mark.xfail` | `git diff b60054f..453208b -- tests/test_soi_loi_t080.py` |

## Việc 2 · Mọi ca vẫn bị từ chối, câu báo không tả file ngoài

### Ép thắng của tôi (chạy nguyên bản) trên `main` `d9e6b5c` và T-082 `453208b`

| Script | `main` | **T-082** |
|---|---|---|
| `lc79_forced.py` (ổ máy, 7 kiểu đích × đọc, `stat`) | 14/14 "Ảnh vừa bị thay đổi…", sạch 7/7 | **14/14 "Ảnh vừa bị thay đổi…", sạch 7/7** |
| `lc80_forced_unc.py` (qua `\\localhost\C$`, 6 kiểu đích) | 12/12 như trên, sạch 6/6 | **12/12 như trên, sạch 6/6** |

### Phép thử mới cho đúng các nhánh T-082 sửa (`lc82_resolve_probe.py`)

Đúng lúc app gọi `resolve`, tầng `x` (thư mục thật có ảnh mồi) bị đổi **thật** trên ổ: thành junction tới `y` (thư mục khác trong gốc), ra ngoài gốc, tới `x` của thư mục anh em dấu Kelvin, hay bị **đổi tên** thành `x-moi` trong gốc; mỗi kiểu trả `x` về ngay sau `resolve` hoặc giữ tới hết lời gọi; gọi đọc, `stat`, xem thư mục. 24 ca mỗi ổ.

| Kiểu | `main` (ổ máy = qua UNC) | **T-082** (ổ máy = qua UNC) |
|---|---|---|
| junction tới `y` trong gốc (trả / giữ) | "tên ngắn hoặc tên khác" 6/6 | **"Thư mục vừa bị thay đổi" 6/6** |
| junction ra ngoài gốc (trả / giữ) | "nằm ngoài thư mục ảnh" 6/6 | **"Thư mục vừa bị thay đổi" 6/6** |
| junction tới thư mục anh em dấu Kelvin: trả ngay | ra ảnh mồi 3/3 | **ra ảnh mồi 3/3** (app không mở đường dẫn anh em `resolve` trả) |
| … giữ | "Thư mục vừa bị thay đổi" 3/3 | **"Thư mục vừa bị thay đổi" 3/3** |
| đổi tên `x` thành `x-moi` (trả / giữ) | "tên ngắn hoặc tên khác" 6/6 | **"Thư mục vừa bị thay đổi" 6/6** (SL-T082-2) |

Cả hai bản, cả hai ổ: **0 lọt nội dung, cỡ, danh sách; 0 câu lộ đường dẫn; 0 lỗi lạ; sạch sau 24/24.** T-082 chỉ đổi câu báo, đúng nghĩa ở mọi ca.

### Số liệu của đội (đã đọc cách thử)

- Soi Lỗi (lượt 1): ép thắng 380 ca ổ máy + 330 ca qua UNC, tráo thật 18.637 vòng: 0 lọt; câu "nằm ngoài" 657 → 0, "không có quyền" 217 → 12; đột biến 12/13 bị bắt (M12 vô hại).
- Thợ Máy (lượt 2): `lc79_forced.py`, `lc80_forced_unc.py`, `sl80_forced_win.py` 396 ca: 0 lọt.

### Câu báo, handle

| Điểm | Kết quả | Bằng chứng |
|---|---|---|
| Câu báo không lộ đường dẫn, không tả file ngoài | **Đạt** | Mọi câu là hằng; nhánh trong `except` ném `from None`; nhánh tên khác ném ngoài khối bắt lỗi. 0 câu lộ đường dẫn ở mọi phép thử trên |
| Không rò handle | **Đạt** | `lc80_leak.py` 800 vòng × 26 lời gọi: 162 → 163 ở **cả `main` lẫn T-082** (như T-080, không do phiếu này) |
| Không chặn oan | Đạt (số Soi Lỗi) | 5.505/5.505 (ổ máy), 2.265/2.265 (UNC) phép kiểm giống `main`; tốc độ ngang |

**Ghi nhận (không thành lỗi):** câu "Không tìm thấy…" mới ở `_opened_stat` có thể nói **có/không** của một mục ngoài thư mục ảnh khi một tầng bị tráo thành junction ra ngoài (ổ báo lỗi 2, 3). Cùng loại thông tin "có/không" T-079, T-080 đã ghi nhận và không bắt sửa (chính `_resolve_inside` vốn báo "Không tìm thấy" như vậy); không có cỡ, loại hay nội dung; chỉ người dùng app thấy.

## Việc 3 · Điều kiện 2 của Lá Chắn T-080 (Việc 4)

- (a) **Đạt.** Docstring `_resolve_inside` (`:659-674`) và `_checked_file` (`:893-905`) ghi rõ: đường dẫn `resolve` trả chỉ để so chuỗi, không được mở, `stat`, liệt kê; nêu lý do (`is_relative_to` so chữ thường, dấu Kelvin, thư mục anh em).
- (b) **Đạt.** `_checked_file` trả cờ `exact` thay vì đường dẫn; test `test_checked_file_does_not_hand_out_resolved_path`. `_resolve_inside` vẫn trả đường dẫn (để `_checked_file` so; đổi kiểu trả làm hỏng test cũ bọc hàm này): chấp nhận, vì hai chỗ gọi còn lại bỏ qua nó (`list_folder` `_path` `:838`, `_Scan._scan_held` nhánh không giữ được `_path`) và docstring đã cấm dùng. Khi kiểm định phiếu sau đụng `folders.py`: soát code mới không dùng đường dẫn `_resolve_inside` trả.
- Windows giữ "tên ngắn hoặc tên khác" cho tên ngắn 8.3 thật: `test_real_short_8_3_name_keeps_alias_message` **chạy thật** trên máy này (ổ có tên 8.3, không bị bỏ qua) và qua.

## Việc 4 · 6 ca chỉ Linux/Mac (đọc mã, không chạy cloud)

Đồng ý với Soi Lỗi: `tests/test_soi_loi_t080_linux.py::test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed` ×6 sẽ **XPASS** (nên báo FAILED vì `strict`):

- `ngoai-goc` × đọc/`stat`/xem: `resolve` ra ngoài gốc → `is_relative_to` sai (Linux so phân biệt hoa thường) → `_ChangedError` (`:712-713`).
- `trong-goc` × đọc/`stat`/xem: `resolve` ra `gốc/y/…` → tên khác → `_still_same_entry(gốc/y/…)` khác inode ảnh mồi (hay `gốc/y` khác inode `gốc/x`) → `_ChangedError` (`:726-728`).
- Mac/Linux không đọc `winerror` (`os.name == "nt"` đứng trước, `:705`); 6 ca đối chứng cùng file (từ chối an toàn, không lộ gì) giữ nguyên.

16 ca mới chạy được trên Mac/Linux (13 lượt 1 + 3 lượt 2): đọc mã thấy qua trên ext4; trên APFS 3 ca dấu Kelvin tự bỏ qua (SL-T082-1 đã sửa). Chưa ai chạy thật trên Linux/Mac: đây là việc của lượt Linux/Mac sau (Ghi chú cuối), không phải lỗi.

## Việc 5 · Thử gộp với `origin/main`

| Gộp | Kết quả |
|---|---|
| `origin/main` `d9e6b5c` (27 commit sau `b60054f`: T-084 `app/views/settings.py` dùng `ImageLibrary.roots()`, 3 `__init__.py` gói mới, test, tài liệu; không đụng `folders.py`) | `git merge-tree --write-tree`: **không xung đột**; cây gộp chỉ khác `origin/main` ở 5 file của T-082, `folders.py` giống hệt nhánh |
| Cây gộp `898793b` (worktree tạm ngoài repo, không đẩy, đã xóa) | 30 file test gọi `folders.py` (grep `images.folders\|ImageLibrary` trong `tests/` của cây gộp, có `tests/test_settings_images.py` của T-084) + `tests/test_app_pages.py`: **2644 passed, 51 skipped, 14 xfailed, 0 hỏng** (34 phút, máy bận). 14 xfail đã biết, như Soi Lỗi: R2-1 ×2, R2-2 (T-048), SL-T067 ×4, SL-T070-4 ×7. Kiểm `__file__`: `folders.py` nạp từ cây gộp |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có bí mật; detect-secrets 0 mục thật; lịch sử nhánh chỉ có chữ `SECRET~1` trong chú thích code cũ và tên công cụ trong báo cáo |
| S2 | Đạt | Câu báo là hằng, không đường dẫn (Việc 2) |
| S3 | Không áp dụng | Không thêm biến cấu hình |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Đạt | Module vẫn chỉ đọc; chỗ mới chỉ `lstat`; test mới chỉ ghi trong thư mục tạm |
| W3 | Không áp dụng | Không có HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1–A3 | Không áp dụng | Không dựng prompt, không gọi AI |
| U1–U3 | Không áp dụng | Không đụng giao diện, đăng nhập (câu báo hiện ở giao diện vẫn là hằng không đường dẫn) |
| F1 | **Đạt** | Việc 1–2: chỉ đổi câu, mọi ca vẫn từ chối, 0 lọt (ép thắng, phép thử mới, ổ máy và UNC) |
| F2 | Đạt | Giới hạn cỡ kiểm trên mục đã mở, không đổi |
| F3 | Đạt | Không ghi file, không `eval`/`pickle`/`yaml.load`; `ctypes` chỉ thêm `set_last_error`/`get_last_error` |
| D1 | Đạt | Không thư viện mới; pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi; script thử ở thư mục nháp |
| D3 | Đạt | 38 ca mới dùng thư mục tạm, `resolve`/`lstat`/`scandir` giả; bộ chặn mạng của `conftest.py` vẫn bật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (`pillow==13.0.0`, `certifi==2026.10.19`, `requests==2.34.2`, `streamlit==1.65.0`) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có |
| bandit | `folders.py` bản `b60054f` (988 dòng) và T-082 (1.040 dòng): **No issues identified** cả hai | Có |
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan --all-files` (1.5.0) trên thư mục riêng chứa 5 file của diff, patch `git diff b60054f 453208b` và 1 file mồi có chữ tiếng Việt: mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`), **0 mục ở file thật**. Đã xóa mồi | Có |
| Soát lịch sử git | `git log -p b60054f..453208b \| grep -inE "api[_-]?key\|password\|secret\|token"`: 2 dòng (tên công cụ `detect-secrets` trong báo cáo Thợ Máy; chú thích `SECRET~1` có sẵn trong code) | Có |
| pytest (nhánh `453208b`) | Lệnh của phiếu + 2 file chỉ Linux/Mac: `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py tests/test_soi_loi_t080_linux.py tests/test_soi_loi_t079_linux.py`: **448 passed, 48 skipped, 3 xfailed, 0 hỏng** (50 giây). 3 xfail = R2-1 ×2, R2-2 (T-048). 48 bỏ qua = 24 ca chỉ Mac/Linux hay cần symlink (như Thợ Máy) + 24 ca của 2 file chỉ Linux/Mac | Có |
| pytest (cây gộp) | Việc 5 | Có |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check` 3 file code/test của diff: đã format | Có |

## Báo nhầm đã loại

- `git log` khớp "secret": tên công cụ trong báo cáo và chú thích `SECRET~1` (ví dụ tên ngắn 8.3) có từ T-048.
- Handle 162 → 163: có ở cả `main` lẫn T-082 với cùng 20.800 lời gọi, không tăng theo số vòng.

## Ghi nhận (không thành lỗi)

- "Ra ngoài gốc" nay luôn là "vừa bị thay đổi" (Thợ Máy, Rủi ro 3): đúng khi lớp kiểm liên kết nhận ra mọi loại liên kết; nếu gặp loại lạ mà lớp đó bỏ sót, app vẫn từ chối, chỉ câu báo kém rõ.
- Khi quét cả cây, thư mục con vừa bị dời đi giữa lúc kiểm và lúc đọc danh sách nay đếm vào `links` (giao diện: "lối tắt") thay `unreadable`; tổng số bỏ qua không đổi.
- Giới hạn Soi Lỗi đã nêu: thư mục bị đổi tên rồi trả tên cũ trước bước so thì vẫn "tên ngắn hoặc tên khác" (không phân biệt được); vẫn từ chối.
- Còn để ngỏ, ngoài phạm vi phiếu: LC-T048-2, -3 (liệt kê qua chính handle đang giữ); trên Linux, file vừa thành symlink lúc mở báo "Không mở được ảnh (không có quyền hoặc file vừa bị đổi)" (gợi ý của Soi Lỗi Linux, câu nêu cả hai nguyên nhân nên không sai).

## Điều kiện

Không có điều kiện mới. Việc còn treo của cả khối đọc ảnh (không chặn gộp):

1. **Lượt Linux/Mac sau** (cloud khi chủ dự án đồng ý, hay máy Mac thật theo điều kiện cũ): chạy `tests/test_images_folders.py tests/test_soi_loi_t080_linux.py -rsxX`; 6 ca `test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed` XPASS thì chỉ xóa khối `@pytest.mark.xfail(...)` của test đó; 16 ca mới của T-082 phải qua (3 ca dấu Kelvin bỏ qua trên APFS là đúng).
2. **Kiểm lại bằng Claude Fable sau 01/11** (biên bản này chạy tạm Opus 5.5).

## Thử độc lập của Lá Chắn (script ở thư mục nháp, không commit; bản sao ở thư mục ghi chú chung `T-082-la-chan-scripts/`)

| Script | Việc |
|---|---|
| `lc79_forced.py <code>`, `lc80_forced_unc.py <code>` (của T-079, T-080, chạy nguyên) | Ép thắng ổ máy, qua `\\localhost\C$` (UNC chạy từ PowerShell) |
| `lc82_resolve_probe.py <code> [--unc]` (mới) | Tráo thật đúng lúc `resolve`: junction tới thư mục khác trong gốc, ra ngoài gốc, tới thư mục anh em; đổi tên thư mục |
| `lc80_leak.py <code> [vòng]`, `lc80_ast.py <folders cũ> <folders mới>` | Rò handle; so thân từng hàm |

`code_main` = `git archive d9e6b5c seo_app` (`folders.py` giống `b60054f`), `code_t082` = `git archive 453208b seo_app`. Mọi file thử nằm trong thư mục tạm riêng, file "bí mật" là mồi tự tạo; không đụng ổ Google Drive, USB của chủ dự án.

## Kết luận

**ĐẠT.** T-082 sửa đúng 3 lỗi câu báo (SL-T080-1, -2, -L-1), 2 lỗi Soi Lỗi tìm thêm (SL-T082-1, -2) và điều kiện Việc 4 của Lá Chắn T-080 (docstring; `_checked_file` không trả đường dẫn `resolve`), mà không nới lớp chặn nào: mọi nhánh sửa vẫn kết thúc bằng từ chối, ép thắng và phép thử tráo thật đúng lúc `resolve` (ổ máy và qua ổ mạng) đều 0 lọt, câu báo không lộ đường dẫn, không tả file ngoài thư mục ảnh, không rò handle. **Gộp `main` được ngay** (không xung đột với `origin/main` `d9e6b5c`; cây gộp 2644 test qua, 0 hỏng).

Lá Chắn không sửa code ứng dụng, không thêm test (không có lỗi LC-T082); chỉ thêm biên bản này. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

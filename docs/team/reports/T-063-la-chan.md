# Biên bản bảo mật T-063 · Xét lỗ hổng SL-T063-2 (đọc file ngoài thư mục ảnh) · Lá Chắn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản chưa dùng được Fable (chủ dự án đã duyệt). **Cần kiểm lại bằng Claude Fable sau 01/11.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable) |
| Phiếu được kiểm | [T-063](../tickets/T-063-chay-test-t048-tren-mac-linux.md) · lỗ hổng [SL-T063-2](T-063-soi-loi.md) Soi Lỗi tìm trên cloud Linux |
| Phạm vi | `seo_app/images/folders.py` (`read_image_bytes`, `stat_image`, `_resolve_inside` — không đổi trên nhánh này), báo cáo Soi Lỗi T-063, phiếu nháp [T-079](../tickets/T-079-doc-anh-bang-fd-tung-tang.md) (trên `main`), biên bản [T-048 Lá Chắn](T-048-la-chan.md). Chỉ **thêm** 2 test vào `tests/test_images_folders_t063.py` (+102 dòng), không sửa code app |
| Máy kiểm | **Windows 11 Pro 10.0.26300**, Python **3.12.15** (uv), chạy bằng **người dùng thường** (`IsUserAnAdmin()=False`). `os.O_NOFOLLOW` **không có** trên Windows; `_winapi.CreateJunction` tạo junction **không cần quyền admin** |
| Ngày | 2026-10-22 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** — SL-T063-2 mức **Cao (Linux/Mac) / Thấp (Windows)**. Bắt buộc T-079 vá + Lá Chắn kiểm lại **trước khi chạy app trên Mac/Linux**. Thứ tự T-079/T-056 để chủ dự án quyết (xem Điều kiện) |

## Tóm tắt (cho chủ dự án)

Soi Lỗi chạy trên Linux tìm ra: nếu máy đã có một chương trình lạ đang chạy, có quyền ghi vào thư mục ảnh, và nó **liên tục tráo một thư mục con thành lối tắt trỏ ra ngoài** đúng lúc app đọc ảnh, thì trên **Linux/Mac** app đọc nhầm **nội dung một file nằm ngoài thư mục ảnh**. Theo bảng mức của dự án, "đọc được file ngoài thư mục ảnh" là mức **Cao**.

Tôi thử đúng cách tráo đó trên **chính máy Windows này**, bằng người dùng thường, nhiều kiểu, hơn **15.000 lần đọc** trong lúc bị tấn công: **không lần nào lọt nội dung, không lần nào lọt cỡ file** (Lá Chắn T-048 trước đây cũng 0/11.192). Lý do: Windows **không tráo chỗ nguyên tử được** như Linux, và khi app đang mở thư mục thì Windows **khóa**, không cho chương trình kia đổi tên để tráo. Nên trên Windows lỗ hổng này **không khai thác được trên thực tế** (mức **Thấp**) — chỉ còn lỗi "lọt tên file" đã biết từ T-048 (cũng Thấp, không lọt nội dung).

Nhưng khi tôi **ép** kẻ tấn công "luôn thắng" (để kiểm tra bản thân đoạn code), thì Windows **vẫn lọt nội dung** — tức là **lỗi nằm trong code**, Windows chỉ may mắn được hệ điều hành cứu, không phải code chặn. Vì phần mềm nhắm cả Mac (chủ dự án chưa có máy Mac, để lại sau) và vì cách sửa đã có sẵn và rẻ, **phải sửa** (phiếu T-079) rồi Lá Chắn kiểm lại **trước khi app chạy trên Mac hay Linux**. Trên Windows thì chưa gấp.

**Cần chủ dự án quyết:** làm T-079 trước rồi mới làm màn hình chọn ảnh (T-056) — an toàn nhất; hay làm T-056 trên Windows trước (Windows đã an toàn với lỗi này) và để T-079 làm trước khi có Mac. Nếu chọn cách sau thì ghi một dòng vào sổ rủi ro.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| SL-T063-2 | **Cao (Linux/Mac)** · **Thấp (Windows)** | Thư mục con bị tráo thành liên kết (symlink/junction) **hai lần** — đúng lúc `lstat` mục cuối và đúng lúc `open` — thì `read_image_bytes` trả **nội dung file ngoài gốc** | `folders.py:487` (`lstat` theo chuỗi đường dẫn, đi xuyên tầng giữa), `:501`/`:508` (`resolve` + `is_relative_to` lúc thư mục là thật), `:636` (`os.open(path)`; `O_NOFOLLOW` chỉ chặn tầng cuối, **Windows không có** `O_NOFOLLOW`), `:643-644` (so `(st_dev,st_ino)` với chính `lstat` đã đi xuyên nên khớp) | Linux: đo thật lọt 1.062–1.253/35k (root), 512–634/18k (nobody). Windows: **0/>15.000** (cách tráo thật); **ép "luôn thắng" thì Windows VẪN lọt** (code có lỗi) | **T-079:** Mac/Linux đọc/`stat` bằng chuỗi fd mở từng tầng (`O_NOFOLLOW` từng tầng, `fstat` trên fd), không đi theo chuỗi đường dẫn. Windows: giữ các lớp hiện có **và** hỏi đường dẫn thật từ chính handle file vừa mở (`GetFinalPathNameByHandleW`) bắt buộc trong gốc, hoặc giữ handle thư mục cha như `_scan_held` |
| SL-T063-1 | Thấp (lỗi của test, không phải app) | `test_unreadable_subfolder_is_counted_not_fatal` giả `os.scandir` bằng `Path(path).name`, hỏng `TypeError` trên Mac/Linux (app quét bằng `os.scandir(fd)`) | `tests/test_images_folders.py:548` | App xử lý đúng (bản viết lại `...when_scandir_gets_fd` qua trên mọi máy). Chỉ làm `uv run pytest` đỏ oan trên Mac/Linux | T-079 viết lại test cũ nhận thư mục khóa theo định danh (`os.fstat(fd)`/`os.stat(path)`). Không phải lỗi bảo mật |
| SL-T063-3 | Thấp | Như SL-T063-2 nhưng ở `stat_image`: trả **cỡ, giờ sửa** của file ngoài gốc cùng tên (không phải nội dung) | `folders.py:487`, `:621` | Linux lọt 1.482–3.095/35k. Windows: **0/>15.000**; ép "luôn thắng" thì lọt cỡ (220 byte = file ngoài gốc). Hậu quả nhỏ: lộ cỡ/giờ sửa một file, không lộ nội dung | Cùng cách sửa SL-T063-2 (một lần vá cả hai) |
| SL-T063-4 | Thấp | Ổ **phân biệt hoa thường**: `check_chosen_image(scanned=…)` đổi ảnh nháp sang file khác chỉ khác hoa thường | `drafts.py:886`, `:903-905` | `congai/cong.png` → `CongAI/cong.png` (ảnh khác). Chỉ Linux / Mac-APFS phân biệt hoa thường; **Windows NTFS không dính**. Hậu quả: hiện/tải nhầm ảnh người dùng không chọn | **Đã sửa ở T-076** (đã gộp). Gộp T-076 thì bỏ `xfail` SL-T063-4 (mục Rủi ro Soi Lỗi) |
| SL-T063-5 | Thấp | Linux trả `ENOTDIR` (không phải `ELOOP`) cho `openat(O_DIRECTORY\|O_NOFOLLOW)` trên symlink, nên thư mục bị tráo bị đếm nhầm vào `unreadable` và báo "không có quyền" | `folders.py:744`, `:746` | **Vẫn an toàn** (không đọc qua liên kết), chỉ sai câu báo và số đếm | T-079: coi `ENOTDIR` lúc mở tầng `parts` là "liên kết/vừa bị thay đổi" (`_ChangedError`); sửa chú thích "ELOOP" |

Không có lỗi Nghiêm trọng. Mọi câu lỗi trong mọi lần thử trên Windows (hơn 40.000 vòng read+stat+list): **0 lần lộ đường dẫn tuyệt đối**, 0 lỗi lạ ngoài `ImageFolderError`.

## Xác nhận đường đi SL-T063-2 trong code (việc 1)

`_checked_file` (`folders.py:599`) → `_resolve_inside(root, ("x","bi-mat.jpg"))` (`:480-518`):

1. Vòng `for part in parts` (`:484-499`): `os.lstat(current)` **theo chuỗi đường dẫn chữ** `gốc/x/bi-mat.jpg` (`:487`). Lúc lstat mục cuối `x/bi-mat.jpg`, nếu `x` là liên kết thì lstat **đi xuyên** `x` ra file ngoài gốc; `_is_link_stat(last)` chỉ kiểm mục **tận cùng** (`bi-mat.jpg` là file thường) nên không bắt được tầng giữa `x`.
2. `resolve(strict=True)` + `is_relative_to(gốc)` (`:501`, `:508`): nếu lúc này `x` là thư mục **thật**, đường dẫn giải ra vẫn trong gốc → **qua**. Trả về `(resolved = gốc/x/bi-mat.jpg, last = lstat đã-đi-xuyên-ra-ngoài)`.
3. `read_image_bytes` (`:636`): `os.open(path, flags)` **theo chuỗi đường dẫn chữ** lần nữa. `flags` có `O_NOFOLLOW` chỉ khi `getattr(os,"O_NOFOLLOW",0)` — **Windows trả 0**, nên trên Windows tầng cuối cũng không được `O_NOFOLLOW` bảo vệ; mà dù có thì `O_NOFOLLOW` cũng chỉ chặn tầng cuối, không chặn tầng giữa `x`. Nếu lúc `open`, `x` lại là liên kết → mở **file ngoài gốc**.
4. So định danh (`:643-644`): `(opened.st_dev, st_ino) == (last.st_dev, st_ino)`. Vì `last` (bước 2) **cũng** là file ngoài gốc (lstat đã đi xuyên), nên khớp → **qua** → trả nội dung ngoài gốc.

Điều kiện lọt: `x` phải là **thư mục thật** lúc `lstat(x)` (bước 1a) và lúc `resolve` (bước 2), nhưng là **liên kết** lúc `lstat(x/bi-mat.jpg)` (bước 1b) và lúc `open` (bước 3). Trên Linux tráo **nguyên tử** (`renameat2(RENAME_EXCHANGE)`) nên đua này thắng được; đúng như Soi Lỗi mô tả "bước 3 ca 8a/8b".

## Thử trên Windows (việc 2) — số liệu

Script `t063_win_probe.py` (thư mục nháp của phiên, **không commit**): một hoặc nhiều **tiến trình riêng** tráo liên tục thư mục con `x`; nhiều **luồng app** gọi `read_image_bytes`, `stat_image`, `list_folder(0,"x")` trên `x/bi-mat.jpg`. Trong gốc là ảnh mồi `DECOY` (6 byte), ngoài gốc là file mồi `SECRET` (220 byte, khác cỡ rõ). Mọi file trong thư mục tạm; **không đọc file thật nào của máy**. Chạy **người dùng thường** (không admin). Máy đang có lượt pytest toàn bộ + 2 agent khác chạy song song (tải cao, có lợi cho kẻ tấn công vì nhiều điểm ngắt).

| Cách tráo | Cấu hình | Số tráo | Vòng read+stat+list | **Lọt nội dung** | **Lọt cỡ** | **Lọt tên** | Lộ đường dẫn |
|---|---|---|---|---|---|---|---|
| Đổi tên thư mục ↔ junction (`CreateJunction`), không nguyên tử | 3 luồng app, 25s | 164 | 7.769 | **0** | **0** | 0 | 0 |
| — nt — | 1 luồng app, 20s | 960 | 1.987 | **0** | **0** | 0 | 0 |
| — nt — | 2 luồng app, 30s | 364 | 5.585 | **0** | **0** | 0 | 0 |
| Bật/tắt reparse **tại chỗ** (`FSCTL_SET/DELETE_REPARSE_POINT`) trên `x` rỗng (= LC-T048-2) | 4 luồng app, 20s | 15.937 | 9.743 | **0** | **0** | **146** | 0 |
| **Ép "luôn thắng"** (monkeypatch `os.lstat`/`os.open` tráo junction đúng lúc; không phải đua) | 1 lần | — | 1 | **LỌT** | **LỌT** | — | 0 |

- **Cách tráo thật (3 dòng đầu):** tổng hơn **15.000** lần `read_image_bytes` và `stat_image` trong lúc bị tấn công → **0 lọt nội dung, 0 lọt cỡ, 0 lọt tên**. Kẻ tấn công bị **chặn nặng** (ví dụ 164 tráo nhưng 10.810 lần lỗi): khi bất kỳ luồng app nào đang mở `x` hay `x/bi-mat.jpg`, Windows từ chối `rename`/`rmdir` thư mục đó (chia sẻ vi phạm). Đây là lý do **cấu trúc** khiến Windows chống được: (a) **không có đổi chỗ nguyên tử** (không có `renameat2(RENAME_EXCHANGE)`); muốn biến thư mục có ảnh thành junction phải làm rỗng nó trước (đổi tên đi) → **không nguyên tử**, đi qua trạng thái "không tồn tại" (ra `FileNotFoundError`, an toàn); (b) **khóa file** chặn tráo đúng trong cửa sổ app đang dùng. Khớp Lá Chắn T-048: 11.192 lần đọc, 0 lọt nội dung.
- **Chứng cứ harness bắt được lỗi (positive control):** cách bật/tắt reparse **tại chỗ** (không đổi tên nên không bị khóa → 15.937 tráo) lọt **146 tên** ngoài gốc / 9.743 vòng (≈1,5%, khớp T-048 47–176/~3.000). Đây đúng là **LC-T048-2** (lọt **tên**, mức Thấp), chứng minh harness của tôi **phát hiện được leak khi có thật** — nên con số "0 lọt nội dung" không phải vì harness hỏng. Cách này **không** lọt nội dung/cỡ vì `x` rỗng (không có ảnh mồi), và khi `x` là junction cả-thư-mục thì đường **đọc file** bị `_resolve_inside` chặn ngay ở `lstat(x)` (`_LinkError`); tên chỉ lọt qua khe **liệt kê** (handle giữ vs `scandir` theo tên).
- **Ép "luôn thắng":** khi tôi monkeypatch để `x` **chắc chắn** là junction đúng lúc `lstat`/`open` mục cuối (như fixture `swap_world` của Soi Lỗi trên POSIX), Windows **lọt cả nội dung lẫn cỡ**. Kết luận: **lỗ hổng nằm trong code `folders.py`, dùng chung mọi hệ điều hành**; Windows không khai thác được là nhờ **đặc tính hệ điều hành** (đua khó thắng), **không nhờ** `folders.py` chặn. Đây là lý do phải vá (T-079) chứ không dựa mãi vào "đua khó thắng".

Hai test mới (`tests/test_images_folders_t063.py`, chỉ thêm, `skipif(not IS_WINDOWS)` + `xfail(strict=True)`): `test_sl_t063_2_windows_swap_cannot_read_outside_content`, `test_sl_t063_3_windows_swap_gives_no_outside_size` — dùng junction (không cần admin), ép "luôn thắng", chứng minh lỗ hổng **CODE** trên Windows. Khi T-079 vá, hai test này thành XPASS(strict) → phải bỏ `xfail`, buộc bản vá **thật sự phủ cả Windows**.

## Xếp mức SL-T063-2 theo `security.md` mục 3 và mô hình đe dọa (việc 3)

| Nền tảng | Mức | Lý do |
|---|---|---|
| **Linux/Mac** | **Cao** | Đo thật lọt **nội dung** file ngoài gốc (Soi Lỗi, có test tái hiện chắc chắn). Bảng `security.md` mục 3: "đọc được file ngoài thư mục ảnh" = Cao. Mac có `renamex_np(RENAME_SWAP)` nguyên tử → suy luận cũng bị (chưa có máy Mac để đo) |
| **Windows** | **Thấp** | Cách tráo thật **0 lọt nội dung / 0 lọt cỡ** qua >15.000 lần đọc (tôi) + 11.192 (T-048); chặn bởi đặc tính hệ điều hành (không đổi chỗ nguyên tử, khóa file). Còn lại là **lọt tên** (LC-T048-2) đã xếp Thấp. Lưu ý: code **vẫn có lỗi** (ép "luôn thắng" thì lọt) nên Thấp là **nhờ hệ điều hành**, một lớp phòng thủ **ngoài ý muốn**, dễ vỡ nếu đổi ổ đĩa/Windows đổi hành vi/có primitive tráo nhanh hơn |

**Mô hình đe dọa dự án** (máy cá nhân của chủ dự án, Windows 11, một người dùng; Mac để lại):
- Điều kiện khai thác (như LC-T048-2): phải có **chương trình lạ đang chạy** trên máy, **có quyền ghi** vào một thư mục con của thư mục ảnh, tráo đúng lúc người dùng xem/chọn ảnh. **Không có đường từ xa:** Google Drive không đồng bộ symlink/junction; USB có liên kết đặt sẵn thì bị chặn ngay.
- Hậu quả nếu khai thác được (chỉ Linux/Mac hiện tại): ảnh xem trước / gửi AI viết alt / **tải lên thư viện Media WordPress** (file Media có địa chỉ công khai dù bài là nháp) là một file khác trên máy người dùng không chọn (phải là ảnh Pillow mới mở được ở bước T-049). Trên **máy dùng chung nhiều tài khoản** (kịch bản Mac tương lai), tài khoản khác có quyền ghi vào thư mục ảnh chung có thể khiến app (chạy bằng quyền chủ máy) đọc file mà tài khoản đó không tự đọc được.
- **Trên môi trường hiện tại của chủ dự án (chỉ Windows):** nguy cơ thực tế là **Thấp** (lọt nội dung không tái hiện; chỉ còn lọt tên Thấp, và tên file gốc không gửi ra ngoài máy — thiết kế T-046, T-052). Vì vậy **không bắt buộc chặn T-056 vì lý do Windows**.

## Định hướng sửa T-079 và cổng T-056 (việc 4)

**Duyệt định hướng T-079** (phiếu nháp trên `main`), có bổ sung theo kết quả Windows của tôi:

1. **Mac/Linux (yêu cầu 1 của T-079): ĐÚNG.** Đọc/`stat` bằng chuỗi fd mở từng tầng (`_posix_open_dir` đã có, `openat(O_NOFOLLOW|O_DIRECTORY)` từng tầng), rồi `os.stat(tên, dir_fd=fd, follow_symlinks=False)` và `os.open(tên, O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC, dir_fd=fd)`, `fstat` trên fd đã mở. Không còn tầng nào bị đi xuyên. Vá luôn SL-T063-3 (cùng gốc).
2. **Windows (yêu cầu 2): BỔ SUNG.** Kết quả của tôi cho thấy đường **đọc** trên Windows **không có** `_win_hold_dir`/`GetFinalPathNameByHandle` như đường **quét** — chỉ dựa `_resolve_inside` + so định danh, và **code vẫn có lỗi** (ép thắng thì lọt). Vì vậy T-079 **nên vá cả Windows**, không để Windows dựa vào "đua khó thắng": sau khi `os.open(path)`, hỏi **đường dẫn thật của chính handle** (`GetFinalPathNameByHandleW`, đã có `_win_final_path`) và bắt buộc `is_relative_to(gốc)` + khớp `parts`; hoặc mở theo chuỗi handle thư mục cha (`FILE_FLAG_OPEN_REPARSE_POINT`, không chia sẻ xóa) rồi `openat`-kiểu bằng `NtCreateFile`/`os.open(dir_fd=...)` (Windows không có `openat` chuẩn qua `os`, nên cách handle-đường-dẫn-thật đơn giản hơn). **Chấp nhận** nếu T-079 chọn giải pháp POSIX trước và với Windows **ghi rõ giải trình** "Windows an toàn nhờ không đổi chỗ nguyên tử + khóa file, đo 0/>26.000" kèm giữ hai test `xfail` Windows làm mốc — nhưng khuyến nghị vá thẳng.
3. **SL-T063-5, SL-T063-1: ĐÚNG** như T-079 (coi `ENOTDIR`/`NotADirectoryError` là `_ChangedError`; viết lại test theo định danh). "Chỉ thêm test" của phiếu T-063 không cho tôi sửa test cũ — để T-079 làm.
4. **Gỡ `xfail` khi vá xong:** SL-T063-2, -3 (POSIX **và** 2 test Windows mới của tôi), -5; và SL-T063-4 (khi đã gộp T-076). Lần chạy toàn bộ trên Windows **không** báo XPASS của SL-T063-4 (NTFS không phân biệt hoa thường → test tự bỏ qua); phải nhớ thủ công.

**Có phải chặn gộp T-056 không?** → **Không bắt buộc chặn vì lý do Windows.** T-056 (màn hình chọn ảnh) chạy trên Windows — nền tảng hiện tại của chủ dự án — là **an toàn** với SL-T063-2 (lọt nội dung không tái hiện; chỉ còn lọt tên Thấp đã biết). T-056 không đụng đường đọc, không làm lỗ hổng nặng thêm. **Nhưng** T-079 là **bắt buộc trước khi app chạy trên Mac/Linux** (gồm cả phiên cloud Linux), vì ở đó mức là **Cao**. Thứ tự hai phiếu là quyết định rủi ro của chủ dự án (xem Điều kiện).

## Xét lại SL-T063-1, -3, -4, -5 (việc 5)

Giữ nguyên mức Soi Lỗi đề xuất: **tất cả Thấp.** Lý do từng lỗi ở bảng "Lỗi phát hiện". Ghi chú:
- SL-T063-1: không phải lỗi bảo mật (lỗi của test cũ chỉ đúng với Windows). App xử lý đúng.
- SL-T063-3: cùng gốc SL-T063-2, hậu quả nhỏ hơn (lộ cỡ/giờ sửa, không nội dung). Windows 0 như SL-T063-2.
- SL-T063-4: đã sửa ở T-076 (đã gộp); Windows NTFS không dính.
- SL-T063-5: vẫn an toàn, chỉ sai câu báo/số đếm.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff chỉ thêm test; không có bí mật. `detect-secrets` (PYTHONUTF8=1) trên file test: `results {}` |
| S2 | Đạt | Mọi câu `ImageFolderError` không chứa đường dẫn tuyệt đối: 0 lộ trong >40.000 vòng thử. `folders.py` không in bí mật |
| S3 | Không áp dụng | Không thêm biến cấu hình |
| W1 | Không áp dụng | Phiếu không đụng WordPress |
| W2 | Đạt | `folders.py` chỉ đọc (`O_RDONLY`); test không ghi/xóa thư mục ảnh |
| W3 | Không áp dụng | Không có HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Không có prompt AI |
| A2 | Không áp dụng | — |
| A3 | Đạt | Tên file gốc **không** gửi AI (thiết kế T-046); lỗ hổng không làm lộ ra ngoài máy |
| U1 | Không áp dụng | Không có giao diện trong phiếu |
| U2 | Không áp dụng | — |
| U3 | Không áp dụng | — |
| F1 | **Không đạt (có điều kiện)** | SL-T063-2 Cao trên **Linux/Mac** (đọc file ngoài gốc khi bị tráo). Windows: **đạt trên thực tế** (0/>15.000), nhưng code vẫn có lỗ. Điều kiện: **T-079** vá + kiểm lại trước Mac/Linux |
| F2 | Đạt | Không đổi giới hạn cỡ ảnh / EXIF; `folders.py` giữ `MAX_IMAGE_BYTES`, chỉ nhận đuôi ảnh |
| F3 | Đạt | File test đọc/ghi `utf-8`, không `eval`/`pickle`/`yaml.load`; chỉ `_winapi.CreateJunction` (tạo junction, không chạy nội dung file như code) |
| D1 | Không áp dụng | Không đổi `uv.lock` / thư viện |
| D2 | Đạt | `.gitignore` không đổi; script thử ở thư mục nháp, không commit |
| D3 | Đạt | Test không gọi mạng thật (import `socket` chỉ để tạo UNIX socket POSIX; `_winapi` là API hệ điều hành) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy — phiếu chỉ thêm test, **không đổi `uv.lock`**; lần quét gần nhất T-075 (`certifi` 2026.10.19, môi trường này đúng bản đó) | — |
| bandit | Không áp dụng — không sửa code `seo_app`/`app`/`scripts` | — |
| detect-secrets | **Sạch** (`results {}`) trên `tests/test_images_folders_t063.py`, chạy `PYTHONUTF8=1` (file có chữ tiếng Việt nên có quét thật, không bỏ qua lặng lẽ) | Có |
| Soát lịch sử git | Diff phiếu chỉ +102 dòng test, không có chuỗi giống bí mật | Có |
| pytest / ruff | `tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py -rs` → **252 passed, 17 skipped, 5 xfailed** (3 cũ + 2 Windows mới của tôi), 0 hỏng trên Windows. `uv run ruff check .` → **All checks passed**; `ruff format --check` file test: đã format | Có |

## Báo nhầm đã loại

- "Windows cũng an toàn nên lỗi không có thật" — **loại**: ép "luôn thắng" cho thấy code lọt trên Windows; Windows chỉ được hệ điều hành cứu. Không hạ lỗi xuống "không có".
- "Harness báo 0 vì hỏng" — **loại**: positive control (bật/tắt reparse tại chỗ) lọt 146 tên, chứng minh harness bắt được leak thật.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **Bắt buộc:** Phiếu **T-079** vá SL-T063-2, -3 (và -5), Lá Chắn kiểm lại (gồm gỡ 2 test `xfail` Windows của tôi + các `xfail` POSIX khi XPASS), **trước khi app chạy trên Mac hoặc Linux** (kể cả phiên cloud Linux). Chủ dự án chưa có Mac (việc Mac để lại) nên chưa gấp, nhưng nên làm sớm vì cách sửa rẻ và đúng.
2. **T-056 (màn hình chọn ảnh) — chủ dự án quyết thứ tự:**
   - **Cách A (an toàn nhất, khuyến nghị):** làm **T-079 trước**, rồi mới gộp T-056.
   - **Cách B:** gộp **T-056 trên Windows trước** (Windows đã an toàn với SL-T063-2), T-079 vẫn **bắt buộc trước Mac/Linux**. Nếu chọn B, ghi một dòng sổ rủi ro (`security.md` mục 6): *"2026-10-22 — gộp T-056 trên Windows trước khi vá SL-T063-2; chấp nhận vì lọt nội dung không tái hiện trên Windows (0/>15.000), còn Cao trên Mac/Linux nên T-079 bắt buộc trước khi chạy Mac/Linux — An Manu."*
3. **Khi có máy Mac:** chạy lại bộ test đọc thư mục ảnh (gồm `tests/test_images_folders_t063.py`, `tests/test_soi_loi_t076.py`, `tests/test_la_chan_t076.py`) + các mục "chờ máy Mac" ở báo cáo Soi Lỗi T-063 (cờ ẩn `UF_HIDDEN`, APFS hoa thường, NFD, mã lỗi macOS cho SL-T063-5, SL-T063-2 đo thật trên Mac).
4. **Kiểm lại bằng Fable sau 01/11** (biên bản này chạy tạm Opus 5.5).

## Rủi ro và điểm cần chú ý

- SL-T063-2 là **Cao trên Mac/Linux**: theo `security.md` nếu giữ nguyên code thì khối đọc ảnh **KHÔNG ĐẠT cho Mac/Linux**. Biên bản này kết luận **ĐẠT CÓ ĐIỀU KIỆN** vì nền tảng hiện tại của chủ dự án là **Windows** (ở đó Thấp) và Mac để lại; điều kiện 1 giữ đúng yêu cầu bảo mật cao nhất khi tới Mac/Linux.
- Hai test `xfail(strict=True)` Windows mới: trên Windows **phải** xfail (code lọt khi ép thắng); khi T-079 vá → XPASS(strict) → đỏ, **nhắc bỏ `xfail`**. Trên Linux chúng tự bỏ qua (`skipif(not IS_WINDOWS)`).
- Các rủi ro đã ghi sổ còn nguyên và **không** thuộc phạm vi T-079: LC-T048-6 (hard link; ổ `st_ino=0`), hai dòng sổ rủi ro mục 6 `security.md`.
- Script thử (`t063_win_probe.py`, `t063_win_forcedwin.py`) ở thư mục nháp của phiên, **không commit**.

## Đối chiếu việc cần làm

- [x] (1) Xác nhận đường đi SL-T063-2 trong code (`folders.py:487/501/508/636/643-644`)
- [x] (2) Thử trên Windows (người dùng thường): tráo thật >15.000 lần đọc → 0 lọt nội dung/cỡ/tên; positive control lọt 146 tên; ép "luôn thắng" → Windows lọt (code có lỗi)
- [x] (3) Xếp mức: **Cao (Linux/Mac) / Thấp (Windows)**, theo mô hình đe dọa
- [x] (4) Duyệt + bổ sung định hướng T-079 (Windows cần vá/giải trình); **không bắt buộc chặn T-056 vì lý do Windows**, chủ dự án quyết thứ tự
- [x] (5) Xét SL-T063-1, -3, -4, -5: giữ Thấp
- [x] (6) Thêm 2 test Windows `xfail(strict=True)` (chỉ thêm), không sửa code app; script thử để nháp

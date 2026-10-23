# Biên bản bảo mật T-080 · Dọn 3 lỗi Thấp đọc ảnh sau T-079 (LC-T079-1, -2, -3) · Lá Chắn (rút gọn)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable, chủ dự án đã duyệt) |
| Phiếu được kiểm | [T-080](../tickets/T-080-don-loi-thap-doc-anh-sau-t079.md) · mức kiểm **rút gọn** (F1) |
| Phạm vi | diff `417efea..170f7a3` (`team/T-080`): `seo_app/images/folders.py` (+98/−37), 6 file test, 3 báo cáo. Code xung quanh: `_resolve_inside`, `_disk_names`, `_found_names`, `_win_open`, `_open_image`, `_Scan`. Đọc báo cáo [Thợ Máy](T-080-tho-may.md), [Soi Lỗi Windows](T-080-soi-loi.md), [Soi Lỗi Linux](T-080-soi-loi-linux.md), biên bản của tôi [T-079](T-079-la-chan.md) |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (uv 0.13.4), người dùng thường; NTFS cục bộ và ổ chia sẻ `\\localhost\C$` (SMB, máy chủ Windows). Máy chạy song song agent khác. Linux: số liệu phiên cloud của Soi Lỗi (đã đọc cách thử). Không có Mac. Không thử ổ Google Drive, USB của chủ dự án |
| Ngày | 2026-10-23 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 lỗi mới do T-080**; còn 3 lỗi Thấp có từ trước (SL-T080-1, -2, -L-1), làm ở **T-082** sau T-056 (chủ dự án đã duyệt). LC-T079-1, -2, -3 **đã đóng**. **Gộp `main` được ngay, và nên gộp trước T-056**: bản `main` hiện tại có đường lọt thật mà T-080 vá (Việc 4) |

## Tóm tắt (cho chủ dự án)

T-080 sửa đúng 3 lỗi nhỏ tôi để lại ở T-079 và an toàn để gộp. Tôi tự làm lại phép "ép kẻ tấn công luôn thắng" trên ổ máy và cả qua ổ mạng: bản đang dùng (`main`) đọc nhầm nội dung một file khác (nằm ngoài thư mục ảnh, hoặc đi qua "lối tắt") ở 5/7 kiểu (qua ổ mạng 4/6) và báo "Ảnh quá lớn (5,0 MB)" về file bên ngoài; bản T-080 chặn hết, chỉ báo "Ảnh vừa bị thay đổi, hãy thử lại". Các lớp chặn cũ còn nguyên, không rò tài nguyên, câu báo không lộ đường dẫn trên máy, dùng bình thường không chậm đi.

Điều cần biết: Soi Lỗi chứng minh lỗi "thư mục anh em tên trông y hệt" trên bản `main` hiện tại **khai thác được thật** (61 lần đọc được file bên ngoài khi một chương trình lạ tráo thư mục liên tục; tôi chạy lại phép thử chắc chắn của Soi Lỗi trên bản `main`: đúng). Ở T-079 tôi xếp lỗi này Thấp vì phép thử của tôi không lọt; theo đúng chuẩn của dự án lẽ ra là **Cao**. T-080 vá hẳn lỗi này, nên tôi đề nghị **gộp T-080 vào `main` ngay**, trước khi gộp màn hình chọn ảnh T-056. Muốn khai thác phải có chương trình lạ đang chạy trên máy và thư mục ảnh nằm trên ổ NTFS của máy (USB FAT32 không bị).

Còn 3 lỗi nhỏ có từ trước: khi thư mục vừa bị dời hay bị tráo đúng lúc app đọc, câu báo đôi khi sai nghĩa ("không có quyền", "nằm ngoài thư mục ảnh" thay vì "vừa bị thay đổi, hãy thử lại"). App vẫn từ chối, không đọc gì ra ngoài. Làm ở phiếu T-082 sau T-056 như anh/chị đã duyệt; không cái nào cần làm sớm hơn.

## Lỗi phát hiện

**Không phát hiện lỗi mới do T-080.** Không viết `tests/test_la_chan_t080.py` (phiếu chỉ yêu cầu khi có lỗi).

Xếp mức lỗi Soi Lỗi tìm ra (đều có từ trước T-080, chỉ sai câu báo, vẫn từ chối):

| # | Mức | Mô tả | Vị trí | Đường đi thật | Quyết định |
|---|---|---|---|---|---|
| SL-T080-1 | **Thấp** (Windows) | `_win_open` trả `None` (mất mã lỗi) nên `_opened_stat` báo "Không đọc được mục này (không có quyền…)" cả khi thư mục chứa ảnh vừa bị dời đi (lỗi 3); `resolve` gặp lỗi 5 (junction đang bị xóa) cũng vậy | `seo_app/images/folders.py:931-933`, `:288-310`, `:660-663` | Thư mục bị dời/tráo đúng giữa lúc kiểm và lúc mở handle → câu sai nguyên nhân; không mở được gì, không lộ gì. Soi Lỗi đo: 1.139 + 138 lần khi tráo thật (bản cũ cùng mức) | T-082, sau T-056 |
| SL-T080-2 | **Thấp** (Windows) | Xem thư mục không giữ được thư mục (lỗi 32) đi nhánh dự phòng; thư mục vừa bị dời thì `_read_entries` báo "Không đọc được thư mục này (không có quyền…)" | `:1120-1127`, `:1132-1137` | Như trên, ở đường xem thư mục. Nhánh dự phòng là chỗ của LC-T048-2, -3 (đã biết) | T-082 (nên làm cùng LC-T048-2, -3 nếu có phiếu) |
| SL-T080-L-1 | **Thấp** (mọi HĐH) | Vòng `lstat` vừa thấy tầng `x` là thư mục thật, `resolve(strict=True)` đi trọn qua `x` lúc nó là liên kết → "Đường dẫn nằm ngoài thư mục ảnh được phép." hoặc "…không hợp lệ (tên ngắn hoặc tên khác…)" | `:664-665`, `:669-673` | Chỉ khi đang bị tráo; vẫn từ chối (`_LinkError`), không lộ đường dẫn (test đối chứng của Soi Lỗi qua) | T-082 |

**Xét lại LC-T079-1 trên bản `main` hiện tại:** khai thác được thật (Soi Lỗi), lẽ ra mức **Cao**; T-080 đã vá → không phải lỗi của T-080, nhưng phải gộp T-080 trước T-056 (Việc 4, Điều kiện 1).

**Vì sao không cái nào cần sớm hơn T-056:** cả ba chỉ xuất hiện khi thư mục bị dời hay bị tráo trong vài phần nghìn giây giữa hai bước kiểm; app luôn từ chối, thử lại là được; không có đường đọc, `stat` hay liệt kê nào ra ngoài thư mục ảnh.

## Việc 1 · Soát diff

So thân từng hàm (AST, bỏ docstring) giữa `417efea` và T-080 (`lc80_ast.py`): **đổi** `_win_handle_at`, `_resolve_inside`, `_checked_file`, `stat_image`, `_opened_stat`, `read_image_bytes`, `_Scan._scan_held`; **thêm** `_same_win_path`, `_changed_while_resolving`, `_check_file`, hằng `_ERROR_CANT_RESOLVE_FILENAME`; **bỏ** `_path_key`; **83 phần giữ nguyên**, gồm mọi lớp chặn cũ (`_parse_rel`, `_is_safe_name`, `_name_key`, `_match_disk_name`, `_is_link_stat`, `_is_hidden_stat`, `_same_file`, `_win_open`, `_win_hold_dir`, `_win_handle_is_link`, `_win_final_path`, `_win_listed_name`, `_posix_open_dir`, `_open_error`, `_root`, `_disk_names`, `_found_names`, `_listed_names`, `_open_image` (chỉ đổi docstring), `list_folder`, `_Scan.run`, `_scan_dir`, `_scan_by_fd`, `_read_entries`, `_visit`). Khớp Soi Lỗi.

| Phần | Đánh giá | Bằng chứng |
|---|---|---|
| `_same_win_path` | Đúng. So **từng chữ** sau khi bỏ tiền tố `\\?\` / `\\?\UNC\` (thứ tự kiểm đúng: UNC trước) và dấu `\` cuối. Chỉ có thể **chặt hơn** `_path_key` cũ: không gộp hoa thường, dạng Unicode, `ß`, dấu Kelvin. Gốc ổ đĩa (`C:\`), gốc UNC (`\\máy\chia-sẻ\`), gốc ghi sẵn `\\?\` đều so được vì hai bên cùng do `GetFinalPathNameByHandleW` sinh ra (`resolve` của Python dùng đúng hàm này) | `folders.py:387-405`; test `test_same_win_path_compares_every_character` (9 ca), `test_extended_length_prefixed_root`, `test_unc_network_root_blocks_junction_and_hides_paths` qua |
| Dùng ở 3 chỗ so | `_opened_stat` (handle chỉ thuộc tính, `:935`), `_open_image` (`:977`), `_scan_held` (`:1114`). Vẫn giữ `_win_handle_is_link` và so định danh (`:940`, `:1000-1003`), đúng lời dặn ở T-079 | diff |
| Chọn tên để mở khi đọc (Windows) | **Không tạo kẽ hở mới.** An toàn nằm ở phép so sau khi mở: đường dẫn thật của handle phải trùng từng chữ `gốc/parts`, `parts` là tên an toàn (đã qua `_is_safe_name`: không `..`, không dấu phân cách), gốc là đường dẫn thật vừa `resolve`; trùng thì file đã mở nằm đúng chỗ đó trong thư mục ảnh lúc mở. Cách chọn tên (chữ đã gõ khi `resolve` trả đúng `gốc/chữ đã gõ`, không thì `_disk_names`) chỉ quyết đọc được hay báo "vừa bị thay đổi" oan, không quyết đọc ở đâu. Đường dẫn `resolve` trả (có thể nằm trong thư mục anh em, xem Việc 4) **chỉ đem so chuỗi**, không mở | `:996-998`; ép thắng Việc 2 (cả kiểu `ref` gõ chữ hoa, ép lúc hỏi tên: Soi Lỗi 380 ca) |
| `_checked_file` / `_check_file` (LC-T079-2) | Đúng. `lstat` qua thì đi tiếp như cũ; hỏng thì lấy lại mục bằng `_disk_names` + `_opened_stat` (mục nằm trong thư mục ảnh: đường dẫn thật trùng từng chữ / fd từng tầng, không phải liên kết, **cùng định danh** với `lstat`) rồi báo theo **mục đó**; mục đó dùng được thì "vừa bị thay đổi". Câu báo ném ngoài `contextlib.suppress` nên không xích lỗi cũ (`__context__` rỗng). Không câu nào tả `lstat` khi kiểm hỏng | `:837-863` |
| `_opened_stat` | Chỉ còn lấy số liệu + so liên kết, định danh; kiểm loại/ẩn/cỡ chuyển về chỗ gọi (`stat_image` `:886-888`, `_checked_file` `:854`), cùng ý nghĩa | `:898-942` |
| `read_image_bytes` | Cỡ, nội dung lấy từ file đã mở (`:1000-1011`), như T-079 | diff |
| `_changed_while_resolving` (LC-T079-3) | Đúng. Vòng liên kết (`RuntimeError`, ELOOP, lỗi Windows 1921), EINVAL, ENOTDIR (Mac/Linux) → `_ChangedError`; Windows xét `winerror`, lỗi Windows khác giữ "Không đọc được". `_ChangedError` là `_LinkError` nên vẫn từ chối (khi quét: đếm vào `links`) | `:443-461`, `:660-663` |
| Chỗ gọi ngoài module | `drafts.py`, `process.py` chỉ gọi `stat_image`, `read_image_bytes`, `list_folder` và bắt `ImageFolderError` để hiện câu; không ai dùng `_resolve_inside`/`_checked_file` hay đường dẫn chúng trả | grep `seo_app/`, `app/` |
| Thư viện, cấu hình | Chỉ thêm `import errno` (thư viện chuẩn). `uv.lock`, `pyproject.toml`, `.gitignore`, `app/`, `config/` không đổi | `git diff --stat 417efea..team/T-080 -- uv.lock pyproject.toml .gitignore app config`: rỗng |
| Gỡ `xfail` | `tests/test_la_chan_t079.py` (file của tôi), `tests/test_soi_loi_t079.py`, `tests/test_soi_loi_t079_linux.py`: diff chỉ xóa định nghĩa dấu, chữ `marks=…` và khối `@pytest.mark.xfail`; không đổi câu kiểm, dữ liệu thử | `git diff 417efea..team/T-080 -- tests/test_la_chan_t079.py tests/test_soi_loi_t079_linux.py` |

## Việc 2 · LC-T079-1, -2, -3 đã đóng

### Ép thắng (dựng lại phép của tôi ở T-079, chạy nguyên `lc79_forced.py`)

Mỗi khi app `lstat`, `os.open`, `_win_open` mục ảnh, tầng `x` chắc chắn là junction trỏ tới đích; mọi bước khác thấy `x` là thư mục thật có ảnh mồi.

| Đích của junction | `main` 417efea · ổ máy | **T-080** · ổ máy | `main` · qua `\\localhost\C$` | **T-080** · qua `\\localhost\C$` |
|---|---|---|---|---|
| Ngoài gốc, tên thường | "vừa bị thay đổi" | "vừa bị thay đổi" | "vừa bị thay đổi" | "vừa bị thay đổi" |
| Anh em của gốc, tên NFD | **lọt nội dung + cỡ** | "vừa bị thay đổi" | **lọt nội dung + cỡ** | "vừa bị thay đổi" |
| Anh em, dấu Kelvin thay `k` | **lọt** | "vừa bị thay đổi" | **lọt** | "vừa bị thay đổi" |
| Anh em, `ß` thay `ss` | **lọt** | "vừa bị thay đổi" | **lọt** | "vừa bị thay đổi" |
| Anh em khác hoa thường (thư mục cha phân biệt hoa thường) | **lọt** | "vừa bị thay đổi" | không thử (máy chủ SMB không mở thư mục trong thư mục phân biệt hoa thường) | không thử |
| Thư mục khác trong gốc, tên NFD | **lọt** | "vừa bị thay đổi" | **lọt** | "vừa bị thay đổi" |
| Ngoài gốc, file 5 MB (giới hạn 1 MB) | **"Ảnh quá lớn (5,0 MB)…"** | "vừa bị thay đổi" | **"Ảnh quá lớn (5,0 MB)…"** | "vừa bị thay đổi" |

Cả đọc lẫn `stat`; mỗi ca xong thư mục trở lại nguyên trạng. Phần qua ổ mạng là **mới** (Thợ Máy, Soi Lỗi chỉ thử ổ mạng ở mức "không chặn oan"): tôi kiểm thêm rằng mở file qua junction phía máy chủ thì đường dẫn thật của handle là **đường dẫn đích** (`…\ngoai\a.jpg`), cả handle đọc lẫn handle chỉ thuộc tính, và thư mục anh em dấu Kelvin, NFD, `ß` qua UNC đều không qua phép so từng chữ (`lc80_unc_final.py`). Nên phép so đường dẫn thật có tác dụng qua ổ mạng máy chủ Windows.

### Số liệu của đội (đã đọc cách thử)

- Soi Lỗi Windows: ép thắng 0/380 ca lọt (bản cũ 22 nội dung, 22 cỡ, 4 tên, 13 qua liên kết, 204 câu tả file ngoài); tráo thật T-080 0 lọt / 86.089 vòng, 21.541 lần tráo; đối chứng dương LC-T048-2 bắt được lọt tên (cách đếm có tác dụng).
- Soi Lỗi Linux: 3.422.839 vòng tráo thật (root và `nobody`), 0 lọt nội dung/cỡ/tên, 0 câu tả file ngoài, 0 câu "không có quyền"; bản cũ cùng cách thử 60.046 câu tả file ngoài, 148.048 câu "không có quyền". 3 ca SL-T079-L-1 XPASS thật, đã gỡ `xfail`.
- Thợ Máy: ổ thật NTFS, SMB, 2 ổ Google Drive (chỉ thuộc tính), USB FAT32 3.782/3.782 mục đường dẫn thật trùng từng chữ, 0 báo oan.

→ **LC-T079-1** (cả đọc, `stat`, xem thư mục), **LC-T079-2** (`read_image_bytes`, `stat_image`), **LC-T079-3** (lỗi `resolve`) đóng.

## Việc 3 · F1

| Điểm | Kết quả | Bằng chứng |
|---|---|---|
| Không đọc, `stat`, liệt kê gì ngoài thư mục ảnh | **Đạt** | Việc 1, 2. Mọi lần mở mới: Mac/Linux fd từng tầng `O_NOFOLLOW`; Windows mở rồi so đường dẫn thật từng chữ với `gốc/parts`. Đường dẫn `resolve` trả không bao giờ được mở |
| Lớp chặn T-048, T-076, T-079 giữ nguyên | **Đạt** | AST Việc 1; test các phiếu đó qua (Việc 5); 3 `xfail` cũ của T-048 (R2-1 ×2, R2-2) giữ nguyên |
| Câu báo không tả file ngoài, không lộ đường dẫn | **Đạt** (trừ ghi nhận cũ) | Ép thắng 0 câu tả file ngoài (bản cũ có); câu báo là hằng, ném `from None` hoặc ngoài khối bắt lỗi. Còn lại như T-079 đã ghi nhận, không bắt sửa: câu "Không tìm thấy", "liên kết tắt", "ẩn" của `_resolve_inside` và "không phải là thư mục" của `list_folder` có thể nói có/không, loại của mục ngoài khi bị tráo (không cỡ, không nội dung) |
| Không rò handle | **Đạt** | `lc80_leak.py`: 1.500 vòng × 26 lời gọi (đọc/`stat`/xem bình thường, `ref` gõ CHỮ HOA, ảnh quá lớn/rỗng/là thư mục trong gốc, đường dẫn thật trong thư mục anh em ở cả 3 chỗ so kể cả trong nhánh báo lỗi mới, `resolve` lỗi): handle 165 → 166 ở **cả `main` lẫn T-080** (chênh như nhau, không do T-080). Thợ Máy 165 → 164, Soi Lỗi 165 → 166 |
| Hiệu năng | Đạt (số của Thợ Máy, Soi Lỗi) | `stat_image`, đọc, xem ngang `main` trên NTFS và SMB; chỉ đọc `ref` gõ khác tên trên ổ thêm 1–7 ms (bước hỏi lại tên, đúng thiết kế) |

## Việc 4 · Xét lại mức LC-T079-1 trên `main`; ghi chú `_resolve_inside`

**LC-T079-1 trên `main` hiện tại khai thác được thật.** Soi Lỗi tráo thật với thư mục anh em dấu Kelvin: `main` lọt nội dung 61 lần (39/2.783 và 22/3.160 vòng). Đường lọt cần ít nhịp hơn đường tôi thử ở T-079: `x` là junction lúc `lstat` mục ảnh và lúc `resolve` (hai lúc liền nhau); `is_relative_to` của Python so theo chữ thường (dấu Kelvin U+212A thành `k`) nên `_resolve_inside` nhận đường dẫn trong thư mục anh em; bản cũ mở thẳng đường dẫn đó, `_path_key` gộp nên qua, định danh trùng `lstat` (cũng đi xuyên junction). Tôi chạy lại test tất định của Soi Lỗi `test_kelvin_sibling_seen_by_lstat_and_resolve_is_not_opened` trên bản sao `main`: **hỏng ca đọc** (đọc ra nội dung file ngoài); trên T-080: qua 2/2.

Ở T-079 tôi tráo thật chỉ với đích anh em NFD (bị `is_relative_to` chặn trước), đo 0 lọt và xếp Thấp. Theo đúng chuẩn tôi dùng ở T-063 (lọt nội dung khi tráo thật = **Cao**, như SL-T063-2 trên Mac/Linux), LC-T079-1 trên `main` đúng ra là **Cao trên Windows** khi thư mục ảnh nằm trên ổ tạo được junction (NTFS: thư mục trên ổ máy, Google Drive chế độ phản chiếu). USB FAT32 không tạo được junction nên không bị. Điều kiện khai thác: chương trình lạ đang chạy trên máy, ghi được vào thư mục chứa thư mục ảnh và vào thư mục ảnh. **T-080 vá lỗi này** (không mở theo đường dẫn `resolve`, so từng chữ), nên đây **không phải lỗi của T-080**; hệ quả duy nhất: `main` đang mang lỗi mà T-080 vá, nên **gộp T-080 ngay, trước T-056** (Điều kiện 1).

**Đề xuất ghi chú `_resolve_inside` của Soi Lỗi: đồng ý, nâng thành việc của T-082.** Đường dẫn `_resolve_inside` (và `_checked_file`) trả **có thể nằm trong thư mục anh em** trên Windows (đã chứng minh ở trên); T-080 chỉ đem so chuỗi, nhưng code sau này lỡ mở nó là lọt lại (Cao). T-082 phải: (a) ghi rõ trong docstring `_resolve_inside`, `_checked_file`: đường dẫn trả về chỉ để so, không được mở, `stat`, liệt kê; (b) nên làm chặt hơn: `_checked_file` không trả đường dẫn mà trả cờ "`resolve` trùng `gốc/parts` từng chữ", để không ai dùng nhầm được.

## Việc 5 · Thử gộp với `origin/main`

| Gộp | Kết quả |
|---|---|
| `origin/main` `367c3bf` (đã có T-066, T-071; gốc chung `417efea`) | `git merge-tree --write-tree`: **không xung đột**. `folders.py` và mọi file test của T-080 giống hệt nhánh; `main` chỉ thêm `seo_app/ai/base.py`, `seo_app/images/html.py`, `seo_app/wordpress/client.py`, test T-066/T-071 và tài liệu |
| Cây gộp `9bdca22` (worktree tạm ngoài repo, không đẩy, đã xóa) | 22 file test dùng thư mục ảnh (mọi file test có `ImageLibrary`/`read_image_bytes`/`stat_image`, thêm `tests/test_app_pages.py`): **2212 passed, 51 skipped, 24 xfailed, 0 hỏng** (3 phút 38 giây). 24 xfail = 13 như trên nhánh + 4 SL-T067 + 7 SL-T070-4 (đã biết, không liên quan). Kiểm `__file__`: `folders.py`, `html.py` nạp từ cây gộp |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có bí mật; detect-secrets 0 mục thật; lịch sử nhánh chỉ có chuỗi mồi `SECRET` trong test |
| S2 | Đạt | Câu báo là hằng, không đường dẫn, không xích lỗi hệ điều hành (Việc 3) |
| S3 | Không áp dụng | Không thêm biến cấu hình |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Đạt | Module vẫn chỉ đọc (`O_RDONLY`, handle chỉ thuộc tính); test mới chỉ ghi trong thư mục tạm |
| W3 | Không áp dụng | Không có HTML |
| W4 | Không áp dụng | Không gọi mạng (ổ mạng SMB chỉ là đường dẫn file) |
| A1–A3 | Không áp dụng | Không dựng prompt, không gọi AI |
| U1–U3 | Không áp dụng | Không có giao diện, không đụng đăng nhập |
| F1 | **Đạt** | Việc 1–3; LC-T079-1, -2, -3 đóng; còn SL-T080-1, -2, -L-1 (Thấp, câu báo) → T-082 |
| F2 | Đạt | Giới hạn cỡ kiểm trên mục đã mở (`:888`, `:1004`, `:1009-1010`); câu cỡ chỉ tả mục trong thư mục ảnh |
| F3 | Đạt | Không ghi file, không `eval`/`pickle`/`yaml.load`; `ctypes` chỉ gọi API hệ điều hành với cờ cố định |
| D1 | Đạt | Không thư viện mới (chỉ `errno`); `uv.lock` không đổi; pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi; script thử ở thư mục nháp, không commit |
| D3 | Đạt | Test mới dùng thư mục tạm, junction; bộ chặn mạng của `conftest.py` vẫn bật; không gọi mạng thật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (`pillow==13.0.0`, `certifi==2026.10.19`) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có |
| bandit | `folders.py` bản `main` (944 dòng) và T-080 (988 dòng): **No issues identified** cả hai | Có |
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan --all-files` (1.5.0) trên thư mục riêng chứa 10 file của diff, patch `git diff 417efea team/T-080` và 1 file mồi có chữ tiếng Việt: mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`), **0 mục ở file thật**. Đã xóa mồi | Có |
| Soát lịch sử git | `git log -p 417efea..team/T-080 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 15 dòng, đều là chuỗi mồi `SECRET` trong test và tên công cụ trong báo cáo | Có |
| pytest (nhánh `170f7a3`) | `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t079_linux.py tests/test_soi_loi_t080.py tests/test_soi_loi_t080_linux.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_images_tags.py tests/test_app_pages.py`: **1378 passed, 50 skipped, 13 xfailed, 0 hỏng** (2 phút 25 giây). 13 xfail = R2-1 ×2, R2-2 (T-048) + SL-T080-1 ×3, SL-T080-2, SL-T080-L-1 phần Windows ×6. 50 bỏ qua = 38 ca chỉ Mac/Linux hay cần ổ phân biệt hoa thường (như Soi Lỗi) + 12 ca của `tests/test_soi_loi_t080_linux.py` | Có |
| pytest (cây gộp) | Việc 5: 2212 passed, 0 hỏng | Có |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check` 7 file code/test của diff: đã format | Có |

## Báo nhầm đã loại

- `git log` khớp "secret": chỉ chuỗi mồi `SECRET-NGOAI-GOC` trong test và tên công cụ `detect-secrets`, `Secret Keyword` trong báo cáo.
- Handle 165 → 166 khi đo rò: có ở cả `main` lẫn T-080 với cùng 39.000 lời gọi (Soi Lỗi đo cùng mức), không tăng theo số vòng: không phải rò của T-080.
- "Qua ổ mạng, đường dẫn thật có thể không lộ junction phía máy chủ nên so từng chữ vô tác dụng": **loại** cho máy chủ Windows (đo: đường dẫn thật là đường dẫn đích; ép thắng qua UNC bị chặn). Máy chủ Samba (Linux) chưa thử (Ghi nhận).

## Ghi nhận (không thành lỗi)

- **Ổ chưa thử:** exFAT (thẻ nhớ, USB lớn), ổ mạng máy chủ Samba, ổ đám mây khác. So từng chữ dựa vào việc ổ báo đường dẫn thật khớp tên trong danh sách thư mục; ổ nào không khớp sẽ báo "Ảnh vừa bị thay đổi" oan (an toàn trước, không lọt). Khi chủ dự án dùng thẻ nhớ exFAT: chạy `probe_usb_t080.py` của Thợ Máy (chỉ đọc thông tin) trước.
- Với ổ cho chạy junction phía máy chủ Samba hay symlink phía máy chủ (`follow symlinks`), máy chủ tự đi theo liên kết mà máy khách không thấy: đó là nội dung máy chủ chọn phục vụ, không phải file trên máy người dùng; ngoài phạm vi T-080.
- Qua SMB, thư mục nằm trong thư mục bật phân biệt hoa thường không mở được (app báo "Chưa thấy thư mục ảnh"): ca hiếm, không liên quan T-080.
- `_resolve_inside` vẫn chấp nhận đường dẫn `resolve` trong thư mục anh em dấu Kelvin / khác hoa thường (code T-048): xem Việc 4, việc của T-082.
- Khi T-056 kiểm định: soát code mới **chỉ** đọc ảnh qua `read_image_bytes`/`stat_image`/`list_folder`, không gọi `_resolve_inside`, `_checked_file` hay dùng đường dẫn chúng trả.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **Gộp T-080 vào `main` trước T-056** (càng sớm càng tốt): `main` hiện tại mang LC-T079-1 khai thác được thật (Việc 4) mà T-080 vá. Gộp ngay được: không xung đột, test cây gộp 0 hỏng.
2. **T-082** (Thợ Máy, sau T-056, chủ dự án đã duyệt; không chặn T-080, không chặn T-056): SL-T080-1, -2, -L-1 theo cách gợi ý của Soi Lỗi, **và** ghi chú/làm chặt `_resolve_inside`, `_checked_file` (Việc 4 (a) bắt buộc, (b) nên làm). Ràng buộc an toàn khi sửa: chỉ đổi câu báo, mọi ca vẫn **từ chối** (`_ChangedError` là `_LinkError`); trên Windows giữ `_MSG_ALIAS` cho tên ngắn 8.3 thật (chỉ đổi khi định danh của `resolve` khác mục `lstat` vừa thấy); ép thắng (ổ máy và qua `\\localhost\C$`, script `lc79_forced.py`, `lc80_forced_unc.py`) vẫn 0 lọt. **Chỉ Huy bỏ `tests/test_la_chan_t080.py` khỏi lệnh test của T-082** (không có file này vì T-080 không có lỗi LC-T080).
3. **Mac (điều kiện cũ, giữ):** trước khi dùng app trên Mac, chạy bộ test thư mục ảnh trên máy Mac thật (`-rsxX`, các ca `posix_only` phải chạy), thêm `tests/test_soi_loi_t080_linux.py`.
4. **Kiểm lại bằng Claude Fable sau 01/11** (biên bản này chạy tạm Opus 5.5).

## Thử độc lập của Lá Chắn (script ở thư mục nháp, không commit; bản sao ở thư mục ghi chú chung `T-080-la-chan-scripts/`)

| Script | Việc |
|---|---|
| `lc79_forced.py <code>` (của T-079, chạy nguyên) | Ép thắng 7 kiểu đích trên ổ máy |
| `lc80_forced_unc.py <code>` | Như trên nhưng gốc mở qua `\\localhost\C$` (chạy từ PowerShell: Bash của phiên này không vào được ổ chia sẻ) |
| `lc80_unc_final.py <code>` | Đường dẫn thật của handle khi mở qua junction (ổ máy, UNC); thư mục anh em qua UNC |
| `lc80_leak.py <code> [vòng]` | Rò handle qua mọi nhánh mới |
| `lc80_ast.py <folders main> <folders t080>` | So thân từng hàm |

`code_main` = `git archive 417efea seo_app`, `code_t080` = `git archive 170f7a3 seo_app`. Test tất định Kelvin của Soi Lỗi chạy trên bản sao (thư mục chứa `seo_app`, `pyproject.toml`, `tests/conftest.py`, `tests/test_soi_loi_t080.py`; kiểm `__file__` nạp từ bản sao). Mọi file thử nằm trong thư mục tạm riêng, file "bí mật" là mồi tự tạo; không đọc file thật nào của máy, không đụng ổ Google Drive, USB.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** T-080 đóng đúng LC-T079-1 (so đường dẫn thật từng chữ ở đọc, `stat`, xem thư mục; không mở theo đường dẫn `resolve`), LC-T079-2 (câu báo chỉ tả mục trong thư mục ảnh), LC-T079-3 (lỗi `resolve` khi bị tráo là "vừa bị thay đổi"). Ép thắng của tôi trên ổ máy và qua ổ mạng: bản cũ lọt, T-080 chặn hết; lớp chặn cũ giữ nguyên (AST), không rò handle, câu báo không lộ đường dẫn. 0 lỗi mới; 3 lỗi Thấp có từ trước (SL-T080-1, -2, -L-1) làm ở T-082 sau T-056, không cái nào cần sớm hơn. **Gộp `main` được ngay** (không xung đột với `origin/main` `367c3bf`, cây gộp 2212 test qua) **và nên gộp trước T-056**, vì Soi Lỗi chứng minh `main` hiện tại lọt được nội dung file ngoài thật (LC-T079-1 lẽ ra mức Cao; tôi xếp thấp ở T-079).

Lá Chắn không sửa code ứng dụng, không thêm test (không có lỗi LC-T080); chỉ thêm biên bản này. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

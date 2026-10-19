# Báo cáo T-048 · Kiểm thử: đọc thư mục ảnh an toàn

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-048](../tickets/T-048-doc-thu-muc-anh-an-toan.md) |
| Ngày nộp | 2026-10-19 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Tôi đã cố bắt app đọc file nằm ngoài thư mục ảnh bằng nhiều cách: lối tắt (junction) lồng nhau, lối tắt trỏ thẳng vào cả ổ đĩa, ổ ảo `subst`, ổ mạng ánh xạ thành ký tự ổ đĩa, đường dẫn mạng, đường dẫn dài hơn 260 ký tự, tên file lạ, và tráo thư mục đúng lúc app đang đọc. **Không cách nào đọc được nội dung file ngoài thư mục ảnh**, câu lỗi không lộ đường dẫn, app không ghi gì vào thư mục ảnh, thư mục 5.000+ mục và cây thư mục 120 tầng không làm treo.

Có 5 lỗi, không lỗi nào chặn gộp:

- **Trung bình (2):** (L1) nếu có người tráo một thư mục con thành lối tắt đúng lúc app đang xem, app có thể **liệt kê tên, cỡ và ngày sửa** của ảnh ở chỗ khác (vẫn không đọc được nội dung); (L2) một file có tên hỏng mã ký tự sẽ làm trang xem thư mục báo lỗi khi giao diện hiện tên.
- **Thấp (3):** câu báo "còn nữa" bị đổi dấu phẩy thành dấu chấm; thư mục có đúng 5.000 mục bị báo "còn nữa" dù đã xem hết; thư mục ẩn (ví dụ thùng rác `$RECYCLE.BIN` trên USB) bị giấu khi xem nhưng vẫn đọc được nếu ai đó gõ sẵn đường dẫn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_images_folders_soi_loi.py` | Mới: 70 ca qua + 9 ca `xfail(strict=True)` ghi lại L1–L5 |
| `docs/team/reports/T-048-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `conftest.py`, `timing.py`.

## Bằng chứng

Máy Windows 11 Pro 10.0.26300, Python 3.12.15, worktree `wt-T-048`, nhánh `team/T-048` (Thợ Máy `e572de8`, test của tôi `dd0e547`), 2026-10-19.

```
$ git pull
Already up to date.

$ uv run pytest tests/test_images_folders_soi_loi.py -q -p no:cacheprovider
70 passed, 9 xfailed in 22.72s        (0 bỏ qua: junction ổ đĩa, UNC \\localhost\C$, tên 8.3 đều chạy thật)

$ uv run pytest -q -p no:cacheprovider
5826 passed, 17 skipped, 44 xfailed, 1 warning in 822.47s (0:13:42)
                                      (= 5.756 của Thợ Máy + 70 ca mới; xfail 35 + 9 ca mới)

$ uv run ruff check .
All checks passed!
```

Thử tay (script trong thư mục tạm, không commit; đã gỡ ổ ảo và ổ mạng ngay sau khi thử, `subst` và `net use` sau đó đều trống):

| Thử | Kết quả |
|---|---|
| `subst Z: <tmp>`, `IMAGE_FOLDERS=Z:\anh` (cả `Z:/anh`, `Z:/anh/`) | Dùng được, `resolve` ra đường dẫn thật trên `C:`; junction trong gốc vẫn bị chặn; câu lỗi không có `Z:` hay `C:\...` |
| `net use Y: \\localhost\C$\<tmp> /persistent:no`, gốc `Y:\anh` | `resolve` ra UNC `\\localhost\C$\...`; đọc ảnh được, junction bị chặn; `st_ino` trên SMB có giá trị (kiểm "cùng file" vẫn chạy) |
| Gốc ghi dạng `\\?\C:\...` và dạng UNC | Dùng được, junction bị chặn (có test) |
| Junction tới `\\?\Volume{GUID}\` (giống ổ gắn vào thư mục; tạo ổ gắn thật cần quyền quản trị nên không thử) | Bị chặn (reparse tag `0xA0000003`), không quét vào ổ đĩa (có test) |
| `COM0.jpg`, `LPT0.jpg`, `CONIN$.jpg` trên Windows 11 này | Tạo ra file thường, không phải thiết bị. Code đã chặn `CONIN$`, `COM¹`; `COM0/LPT0` không cần chặn |
| Ký tự giống dấu chấm/gạch chéo (`．．`, `․․`, `∕`, `／`, `⧵`) | Windows coi là chữ thường, không thoát khỏi gốc (có test) |

## Lỗi tìm thấy

### L1 · Trung bình · Tráo thư mục thành junction giữa lúc kiểm và lúc quét: liệt kê được file ngoài gốc

`list_folder` kiểm thư mục (`_resolve_inside`, `folders.py:347`) rồi mới `os.scandir(directory)` (`folders.py:496`). Khi quét cả cây, thư mục con được kiểm lúc gặp (`_visit`, `folders.py:524`) nhưng chỉ được `scandir` sau đó, khi tới lượt (`folders.py:550` → `:496`); khoảng chờ này có thể dài tới hết ngân sách (5.000 mục, 10 giây). `os.scandir` đi xuyên junction, nên nếu thư mục bị tráo trong khoảng đó thì kết quả có tên, cỡ, ngày sửa của file ngoài gốc, kèm `ImageRef` trỏ vào chúng.

- **Tái hiện:** `test_list_folder_dir_swapped_to_junction_after_check` (tráo `album/` ngay trước `scandir`), `test_recursive_scan_subdir_swapped_to_junction_before_its_turn` (tráo sau khi đã quét xong thư mục cha).
- **Mong đợi:** không có `bi-mat.jpg` (file ở `ngoai/`) trong kết quả, hoặc báo `ImageFolderError`.
- **Thực tế:** `bi-mat.jpg` có trong `listing.images`.
- **Mức độ:** nội dung file vẫn **không** đọc được: `read_image_bytes` kiểm lại cả đường đi và so `(st_dev, st_ino)` sau khi mở (tôi đã thử tráo thư mục cha và tráo file thành junction ngay trước `os.open`: đều bị chặn, `test_read_detects_parent_dir_swapped_to_junction_before_open`, `test_read_detects_file_replaced_by_directory_junction`). Muốn khai thác phải có quyền ghi vào thư mục ảnh trên máy (Drive for Desktop không đồng bộ junction). Tôi xếp Trung bình vì đây vẫn là "đọc thư mục ngoài phạm vi" (F1); Lá Chắn quyết định mức cuối.
- **Gợi ý sửa:** sau khi `scandir` xong một thư mục, kiểm lại thư mục đó (không phải liên kết, `resolve()` vẫn nằm trong gốc, `(st_dev, st_ino)` trùng lúc kiểm); sai thì bỏ toàn bộ kết quả của thư mục đó và đếm vào `skipped.links`. Với thư mục con, kiểm thêm một lần ngay trước `scandir`. Vẫn còn khe nhỏ "tráo rồi tráo lại", ghi vào sổ rủi ro; lớp chặn nội dung là phép so inode ở `read_image_bytes`.

### L2 · Trung bình · Tên có surrogate lẻ lọt vào kết quả, giao diện sẽ lỗi khi hiện

`_is_safe_name` chỉ chặn ký tự loại `Cc` (`folders.py:78`). NTFS cho phép tên UTF-16 lẻ cặp (`x\ud800y.jpg`); Linux cho phép tên byte sai UTF-8 (Python đọc ra `\udcff`). Cả hai là ký tự loại `Cs`, không mã hóa được UTF-8. Tôi đã thử: gán tên này vào protobuf của Streamlit (`Markdown.body`) thì lỗi `UnicodeEncodeError: surrogates not allowed`, nên trang xem thư mục có file như vậy sẽ hỏng khi T-056 hiện tên.

- **Tái hiện:** `test_listing_never_returns_names_that_cannot_be_utf8_encoded`, `test_image_ref_rejects_lone_surrogates` (2 ca).
- **Mong đợi:** tên bị bỏ qua, đếm vào `skipped.bad_names`; `ImageRef` từ chối.
- **Thực tế:** tên có trong `listing.images`; `ImageRef(0, "x\ud800y.jpg")` được nhận và đọc được nội dung.
- **Gợi ý sửa:** trong `_is_safe_name` từ chối thêm loại `Cs` (một điều kiện). Không ảnh hưởng tên tiếng Việt.

### L3 · Thấp · Câu "còn nữa" bị đổi dấu phẩy thành dấu chấm

`folders.py:371-374`: `.replace(",", ".")` áp cho cả câu, không chỉ con số, nên câu thành "mới xem 5.000 mục đầu**.** còn nữa chưa xem".

- **Tái hiện:** `test_entry_budget_notice_keeps_sentence_comma`.
- **Mong đợi:** "… mục đầu, còn nữa …". **Thực tế:** "… mục đầu. còn nữa …".
- **Gợi ý sửa:** chỉ đổi dấu trong con số: `f"{self._max_entries:,}".replace(",", ".")` rồi ghép vào câu.

### L4 · Thấp · Thư mục có đúng `max_entries` mục bị báo "còn nữa"

`_out_of_budget` (`folders.py:484`) dừng khi đã xem đủ `max_entries` mục mà không xem còn mục nào không. Thư mục có đúng 5.000 mục (hay 3 mục với `max_entries=3`) bị `truncated=True` và hiện câu "còn nữa chưa xem" dù đã xem hết.

- **Tái hiện:** `test_folder_with_exactly_budget_entries_is_not_truncated` (đối chứng `..._one_less_than_budget_...` qua).
- **Mong đợi:** `truncated=False`, `notice=""`. **Thực tế:** `truncated=True`.
- **Gợi ý sửa:** lấy mục kế tiếp trước rồi mới kiểm ngân sách số mục (có mục thứ 5.001 mới báo "còn nữa").

### L5 · Thấp · Thư mục ẩn bị giấu khi xem nhưng vẫn đọc được bằng `ImageRef` gõ sẵn; tên ngắn 8.3 đi vòng luật tên

Khi quét, thư mục ẩn/hệ thống và tên bắt đầu bằng dấu chấm bị bỏ qua. Nhưng `_resolve_inside` (`folders.py:298-308`) chỉ kiểm liên kết cho từng phần đường dẫn, không kiểm thuộc tính ẩn; `_checked_file` chỉ kiểm thuộc tính ẩn của **file cuối**. Ngoài ra Windows còn tạo tên ngắn 8.3 (đã thử: `.secretdir` → `SECRET~1`), tên này qua được `_is_safe_name` và mở được thư mục `.bi-mat`.

- **Tái hiện:** `test_hidden_directory_cannot_be_reached_by_crafted_ref`, `test_short_8dot3_alias_cannot_reach_dot_directory`.
- **Mong đợi:** `ImageFolderError`. **Thực tế:** trả nội dung ảnh trong thư mục ẩn.
- **Mức độ:** vẫn nằm trong gốc, nên không phạm F1. Ví dụ thật: gốc là ổ USB `E:\` thì ảnh đã xóa trong `E:\$RECYCLE.BIN\...` đọc được nếu nháp (G3-9) chứa sẵn `ImageRef` đó. Tên 8.3 còn làm **một file có hai `ImageRef`** khác nhau (ảnh hưởng cache ảnh xem trước, chống trùng ở G3-3/G3-9).
- **Gợi ý sửa:** trong `_resolve_inside`, từ chối phần đường dẫn có `_is_hidden_stat`; sau `resolve()` so `resolved.relative_to(root).parts` với `parts` (so không phân biệt hoa thường), khác thì từ chối (bắt được tên 8.3).

## Đối chiếu yêu cầu phiếu

- [x] **YC1** không lộ đường dẫn tuyệt đối: `repr`/`str` của mọi đối tượng trả về (`ImageLibrary`, `FolderListing`, `ImageEntry`, `ImageRef`, `SkipCounts`, `SubFolder`, `RootInfo`) và câu lỗi của mọi loại hỏng (không thấy, là thư mục, rỗng, quá lớn, không có quyền khi `open`/`scandir`/`lstat` với `OSError` chứa đường dẫn) đều không có `tmp_path` ở dạng `\`, `/`, `\\?\` (`test_repr_and_str_of_every_result_object_hide_absolute_paths`, `test_error_messages_hide_paths_for_every_failure_kind`). Gốc UNC: câu lỗi không có `localhost`, `C$`.
- [x] **YC2** chặn liên kết: junction lồng nhau, junction tới cả ổ đĩa, junction trong gốc `subst`/ổ mạng/UNC/`\\?\` đều bị chặn. Còn L1 (chỉ liệt kê, khi bị tráo đúng lúc) và L5 (trong gốc).
- [x] **YC3** đuôi và dung lượng: đúng 40 MB nhận, 40 MB + 1 byte bị loại khi quét, `stat_image`, `read_image_bytes` (câu "40,0 MB"); RLO và ký tự rộng 0 không giả được đuôi (`anh\u202egpj.exe` vẫn là `.exe`).
- [x] **YC4** ngân sách: 5.005 file thật dừng ở 5.000, dưới 10 giây, `page=10**9` đưa về trang 25; cây 120 tầng không đệ quy, không treo; `page`, `page_size`, `max_depth`, `root_index` lạ (âm, 0, bool, float, chuỗi, `None`, `10**30`) đều báo lỗi gọn. Còn L3, L4 (Thấp).
- [x] **YC5** tên là dữ liệu chưa tin cậy: module trả nguyên tên. Còn L2.
- [x] **YC6** test junction chạy thật trên Windows. Mac/Linux: **chưa chạy được** trên máy này (xem đề xuất).
- [x] Chỉ đọc: không test nào thấy file trong thư mục ảnh bị đổi.
- [x] `uv run pytest` 0 hỏng, `uv run ruff check .` sạch.

## Đánh giá các điểm Thợ Máy nhờ thử

1. **Junction lồng, mount point, đường dẫn dài, `subst`, ổ mạng:** đạt (bảng thử tay ở trên và 5 test Windows).
2. **Ký tự định dạng Unicode (Cf: RLO, ký tự rộng 0):** không giúp thoát khỏi gốc, không giả được đuôi file. Tôi đánh giá **không bắt buộc chặn ở module này**; chỉ cần ghi điều kiện cho giao diện (T-056): hiện tên bằng chữ thường (escape HTML/Markdown) và cô lập hướng chữ (`unicode-bidi: isolate` hoặc bọc U+2068…U+2069) để RLO không đảo phần chữ xung quanh. Nếu muốn chặt hơn, có thể từ chối 9 ký tự điều khiển hướng chữ (U+202A–U+202E, U+2066–U+2069) vì tên ảnh thật không cần chúng. Riêng loại **Cs thì phải chặn** (L2).
3. **TOCTOU:** đường đọc nội dung chịu được (2 test qua); đường liệt kê thì không (L1).
4. **Hard link ra ngoài:** đúng như Thợ Máy ghi, không phát hiện được; `test_hard_link_limitation_is_documented` ghi lại hành vi. Cách giảm (tùy chọn): từ chối file có `st_nlink > 1`, đổi lại có thể từ chối nhầm ảnh do phần mềm sao lưu tạo hard link. Đề nghị ghi vào sổ rủi ro.
5. **Ngân sách và tham số lạ:** đạt, trừ L3, L4. `rel_path` lạ (`a/../b`, `./a`, `a//b`, `C:a`, `\\server\share`, `\\.\PhysicalDrive0`, `CON`, `nul.txt`, tên kết thúc dấu chấm/khoảng trắng, `~`, `%USERPROFILE%`, `$HOME`) đều bị từ chối hoặc chỉ là "không tìm thấy", không khai triển biến môi trường hay thư mục nhà.
6. **Câu lỗi, `repr`/`str`:** đạt.
7. **Lệnh:** xem Bằng chứng.

## Rủi ro và điểm cần chú ý

- **Chưa chạy trên Mac/Linux.** 4 test symlink, test tên lạ, FIFO (của Thợ Máy) và nhánh tên sai UTF-8 của L2 chỉ chạy trên Mac/Linux.
- **Hệ thống file có `st_ino = 0`** (một số ổ FAT/exFAT, ổ ảo) làm tắt phép so "cùng file" ở `read_image_bytes` (`folders.py:442`). Ổ mạng SMB và NTFS ở máy này có `st_ino`. Chưa thử được với Drive for Desktop thật và USB exFAT.
- **Mỗi lần chuyển trang là một lần quét lại** (tối đa 5.000 mục / 10 giây). Khi bị cắt vì hết giờ, trang 2 của lần quét sau có thể không nối tiếp trang 1 của lần trước. Giao diện (T-056/G3-10) nên giữ kết quả quét trong phiên và chỉ quét lại khi người dùng bấm.
- Ngân sách thời gian không cắt ngang được một lệnh `scandir` đang bị ổ chậm giữ (Thợ Máy đã ghi).
- Dọn thư mục tạm có junction tới cả ổ đĩa: tôi gỡ junction bằng `os.rmdir` trong `finally` để không công cụ dọn nào đi xuyên vào ổ đĩa.

## Đề xuất

- Chỉ Huy giao lại Thợ Máy sửa L1, L2 (Trung bình) trước khi hết Giai đoạn 3; L3, L4, L5 gộp chung một phiếu dọn nhỏ (sửa xong thì bỏ `xfail` ở 9 test tương ứng).
- Ghi vào điều kiện của T-056: escape tên file/thư mục, cô lập hướng chữ, không dùng `ImageLibrary._folders`, giữ kết quả quét trong phiên.
- Ghi vào sổ rủi ro: hard link, khe "tráo rồi tráo lại" còn lại sau khi sửa L1, ổ có `st_ino = 0`.
- Chạy `tests/test_images_folders*.py` trên một máy Mac khi có dịp.

## Câu hỏi cho chủ dự án

Không có.

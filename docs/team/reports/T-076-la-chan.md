# Biên bản bảo mật T-076 · Thư mục ảnh trả tên theo tên trên ổ (sau T-055) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-076](../tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) |
| Phạm vi | Rút gọn (F1; yêu cầu bảo mật riêng F1, F3). Diff `d9e279f...team/T-076` (đầu nhánh lúc kiểm `a1a48da`; code ứng dụng đổi ở `d41eff0`, sau đó chỉ có test và báo cáo): `seo_app/images/folders.py` (+113/−6), `seo_app/storage/drafts.py` (+73/−57), `tests/test_images_folders.py` (+197), `tests/test_drafts_images.py` (+174/−33), `tests/test_soi_loi_t055.py` (−12, chỉ gỡ `xfail`), `tests/test_soi_loi_t076.py` (mới, +514), 2 báo cáo. Thử gộp với `origin/main` `291879a` (đã có T-055, T-075, T-077) |
| Ngày | 2026-10-21 (16:00–16:45 +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (LC-T076-1, mới), **1 Thấp** (LC-T076-2 = SL-T076-1, giữ mức). F1, F3 đạt. **LC-T055-1 chỉ đóng trên ổ thường (NTFS, ổ chia sẻ Windows); trên ổ Google Drive for Desktop của Windows thì chưa** (LC-T076-1). LC-T055-2, -3 đóng (LC-T055-2 còn phần dư LC-T076-2). Điều kiện 2a của T-056 **chưa bỏ được**. Gộp `main`: không xung đột, test liên quan qua trên cây gộp, nhưng **chưa nên gộp ngay**: sửa LC-T076-1 ở T-076 lượt 2 trước (điều kiện 1) |
| **Kết luận lượt 2** (2026-10-22) | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**: LC-T076-1 đóng (cả trên ổ Google Drive for Desktop thật), LC-T076-2 đóng; còn **1 Thấp** LC-T076-3 (= SL-T076-2) → T-079. Điều kiện 2a của T-056 hạ xuống khuyến nghị (giữ test). Xem mục [Lượt 2](#lượt-2-2026-10-22-rút-gọn-lc-t076-1-lc-t076-2) |

## Tóm tắt (cho chủ dự án)

Bản sửa **an toàn với file trên máy**. Tôi tráo thư mục, xóa, đổi tên và cài "lối tắt" trỏ ra ngoài đúng lúc app đang kiểm tên thư mục: app chỉ báo lỗi gọn, không mở file nào, không lấy được gì ngoài thư mục ảnh, câu báo không có đường dẫn trên máy. Trên ổ thường của máy (ổ C, D, USB định dạng NTFS), lỗi cũ của tôi ở T-055 đã hết hẳn: nháp ghi `congai` mà trên ổ là `CongAI` thì ảnh luôn là **ảnh AI**, câu mô tả ảnh có «Minh họa» và phải duyệt lại, mở thư mục theo cách nào cũng vậy.

Nhưng có **1 lỗi Trung bình mới**. Máy này có ổ Google Drive for Desktop (G:, H:, I:), là chỗ chủ dự án để ảnh. Tôi thử trên đó, **chỉ đọc** (không mở, không sửa, không ghi lại tên file hay thư mục nào của chủ dự án): khi app hỏi "tên thật của thư mục này là gì", ổ Drive trả lại **đúng chữ đã gõ** chứ không phải tên thật. Bản sửa dựa vào câu trả lời đó, nên trên ổ Drive lỗi cũ vẫn còn: ảnh AI có thể bị coi là ảnh công trình thật, alt không có «Minh họa». Có 2 trường hợp còn kém hơn bản đang dùng trên `main`. Hôm nay chưa màn hình nào dùng phần này (màn hình chọn ảnh T-056 chưa làm) nên chưa có hậu quả thật.

Cách sửa nhỏ: lấy tên từ **danh sách thư mục** (cách này tôi đã thử đúng trên ổ Drive của máy). Tôi khuyên Thợ Máy sửa thêm một lượt rồi mới gộp vào `main`; màn hình chọn ảnh T-056 vẫn phải giữ cách "đi từ thư mục ảnh gốc xuống". Lỗi Thấp của Soi Lỗi giữ mức Thấp, nên sửa luôn trong lượt đó vì cùng chỗ.

## Lỗi phát hiện

Số dòng theo `a1a48da`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T076-1 | **Trung bình** | **Trên Windows, "tên trên ổ" lấy từ `resolve`, mà ổ Google Drive for Desktop trả lại đúng chữ đã gõ.** `_disk_names` dùng `resolved.relative_to(root).parts` khi `_NAMES_FROM_RESOLVE` (mọi máy Windows). **Đo thật trên máy chủ dự án** (script nháp, chỉ đọc, chỉ in Đúng/Sai): ổ Drive H:, I: (G:, H:, I: báo hệ thống file "FAT32", là ổ ảo của Drive for Desktop): `os.path.realpath("H:/my drive")` → `H:\my drive`, trên ổ là `My Drive`; **4/4** thư mục người dùng tạo trong My Drive, gõ đảo hoa thường: `resolve` trả lại chữ đã gõ. Cùng lúc `os.scandir` và `FindFirstFileW` cho tên trên ổ (4/4). Gọi thẳng code T-076 trên ổ Drive: `_disk_names` cách Windows trả chữ đã gõ, cách xem thư mục cha (`_listed_names`) trả tên trên ổ, so định danh qua (4 thư mục người dùng tạo + `My Drive` ở 2 ổ). Ổ NTFS C: đối chứng: đúng ở mọi cách. Vậy trên ổ Drive, `stat_image` và `list_folder` trả `ImageRef` theo chữ đã gõ (so định danh vẫn qua vì cùng một mục). Docstring khẳng định ngược lại | `folders.py:66-71`, `:566-567`; docstring `folders.py:16-18`, `:551-560`, `:632-634`, `:721-723`; `drafts.py:836-849`, `:784-788`, `:894-925` | Trên ổ, thư mục `CT012 - Cổng inox - Tân Phú/CongAI/cong.png` (ảnh AI nhờ tách chữ hoa); nháp ghi `…/congai/cong.png`, nguồn `"that"`, alt đã duyệt (sửa tay, hay chọn ảnh khi thư mục còn tên `Congai` rồi đổi thành `CongAI`). Ổ Drive giả lập đúng như đã đo (`Path.resolve` trả chữ đã gõ; danh sách thư mục là của ổ thật). Thử 1 (cây gộp, nhánh, `main` `d9e279f`): **(B)** "mở thư mục chứa ảnh" theo đường dẫn trong nháp, `check_draft_images(…, scanned=list_folder(0, "…/congai").images)` → **ảnh thật** `that/CT012/Tân Phú`, alt không «Minh họa», vẫn "đã duyệt" (= LC-T055-1, như `main`); **(F)** chọn lại ảnh trong danh sách đó → `ImageRef` `…/congai/…`, thẻ ảnh thật (như `main`); **(D)** không `scanned`, thư mục công trình đông nên danh sách bị cắt → **ảnh thật** (`main`: "không dùng được", hướng an toàn); **(E)** `scanned` đi đúng từ gốc xuống (điều kiện 2a), danh sách bị cắt → **ảnh thật** (`main`: ảnh AI). (A) không `scanned`, danh sách xem hết, và (C) `scanned` từ gốc, danh sách xem hết: ảnh AI (lớp phòng thứ hai bắt được). Ổ NTFS thật: cả 6 luồng ra ảnh AI ở nhánh và cây gộp. **D, E kém hơn `main` trên ổ Drive** vì T-076 bỏ phép đổi `ref` sang `ImageRef` của kết quả quét (`:894-898`) và, khi danh sách bị cắt, giữ tên `stat_image` trả (`:784-788`, cách sửa LC-T055-3), tin đó là tên trên ổ. "Bị cắt" là quá 5.000 mục hoặc quét quá 10 giây (ổ Drive chậm). **Hậu quả:** như LC-T055-1: ảnh AI giới thiệu như ảnh công trình thật CT012 ở Tân Phú, alt không «Minh họa» vẫn "đã duyệt" (trái điều kiện Lá Chắn T-052 số 3, quy tắc C6). Không đọc ngoài thư mục ảnh, không lộ bí mật. **Chưa có đường đi trong code hôm nay:** `app/` không gọi `check_draft_images`, `list_folder`, `stat_image` (`git grep` trên nhánh và `origin/main`; chỉ `PreviewCache.get` gọi `stat_image`, không đọc thẻ), nên không xếp Cao. Test `xfail(strict=True)`: `tests/test_la_chan_t076.py` (6 ca, kèm 4 ca đối chứng đang qua) | **T-076 lượt 2 (Thợ Máy), trước khi gộp `main`:** trên Windows lấy tên từng tầng từ **danh sách thư mục**, không từ `resolve`: (a) `FindFirstFileW` từng tầng (một lần hỏi ổ mỗi tầng; `cFileName` là tên trên ổ; module đã có sẵn `ctypes` cho `kernel32`; đúng trên ổ Drive và NTFS của máy này), hoặc (b) dùng luôn `_listed_names` trên Windows (đã đúng 4/4 trên ổ Drive thật; Soi Lỗi đo chậm hơn trên ổ mạng). Giữ nguyên bước `lstat` ở tên mới và so định danh (`:570-579`); không lấy được tên thì báo lỗi, **không quay về chữ đã gõ**. Sửa chú thích `_NAMES_FROM_RESOLVE` và các docstring nêu trên. Thêm vào `name_source` của Thợ Máy một kiểu "ổ trả lại chữ đã gõ khi `resolve`" (như `typed_resolve` trong `tests/test_la_chan_t076.py`). Gỡ dấu `@XFAIL` trong `tests/test_la_chan_t076.py` khi XPASS, không đổi `assert`. Mô phỏng cách (b) (`_NAMES_FROM_RESOLVE = False` khi chạy test): cả 10 ca của file qua |
| LC-T076-2 (= SL-T076-1) | Thấp (**giữ mức**) | Lớp phòng thứ hai đổi sang tên của danh sách thư mục khi chỉ trùng cỡ và giờ sửa: bản sao cùng cỡ, cùng giờ sửa ở thư mục khác được nhận là "cùng ảnh" | `drafts.py:926-933` | Như Soi Lỗi tả: đổi tên 2 thư mục đúng khe vài mili giây giữa `stat_image` và `list_folder` của lớp phòng thứ hai, có bản sao y hệt (Explorer giữ giờ sửa khi chép), nháp ghi `"that"` cho ảnh trong thư mục AI → ảnh ở `…/Congai/` (file khác) dùng được, thẻ ảnh thật. **F1 giữ:** lần `stat_image` thứ hai qua đủ lớp chặn, mọi lần đọc sau qua `read_image_bytes`. File được dùng nằm ở thư mục không mang tên AI và mang thẻ theo chính chỗ của nó; nội dung trùng ảnh AI vì người dùng đã chép ảnh AI sang thư mục ảnh thật. Chương trình lạ chạy trên máy làm được nhiều hơn mà không cần khe này (ghi đè thẳng file). Nên giữ **Thấp**. Trên ổ Drive (LC-T076-1) đường đổi tên này chạy cả khi không có ai tráo, nhưng vẫn so cỡ, giờ sửa của cùng một file, nên không thêm hậu quả | Cách (a) của Soi Lỗi: danh sách xem hết mà không có đúng tên `stat_image` trả thì không dùng được (`_MSG_FOLDER_NAME`); bị cắt thì giữ như nay; bỏ hẳn bước đổi tên. Lớp phòng thứ hai thành "đóng khi nghi ngờ". **Khuyên làm cùng lượt 2** của LC-T076-1 (cùng chỗ code, rẻ; 2 test dùng ổ giả "trả chữ đã gõ" của Thợ Máy phải đổi theo, Soi Lỗi đã thử). Nếu tách ra phiếu khác thì không bắt buộc trước T-056. Gỡ `xfail` SL-T076-1 khi XPASS |

## Kiểm lại lỗi cũ và các việc được giao

| Mã / việc | Kết quả | Bằng chứng |
|---|---|---|
| Việc 1 · soát diff `seo_app/` | Xong | `folders.py`: `_match_disk_name` (`:147-165`), `_disk_names` (`:548-580`), `_listed_names` (`:582-612`), `list_folder` gọi `_disk_names` sau `_resolve_inside` (`:644-647`), `_checked_file` trả thêm gốc (`:698-709`), `stat_image` (`:718-728`), `read_image_bytes` chỉ đổi dòng nhận (`:736`). `drafts.py`: `stat_image` rồi `ref = entry.ref` (`:917-918`), `_FolderNames` biết `truncated` (`:765-793`), `stat_image` lại khi đổi tên (`:926-933`), `scanned` chỉ so trùng hẳn (`:894-898`, `:924`), `_MSG_FOLDER_NAME` (`:109-112`), docstring `scanned` (`:843-849`) |
| **LC-T055-1** (Trung bình, của tôi) | **Đóng trên ổ thường; chưa đóng trên ổ Google Drive for Desktop của Windows → LC-T076-1** | **Thử 1, 4 của T-055 dựng lại** (`lc_t076_exp1.py`, 6 luồng A–F ở trên). Điều kiện đầu: `tags_for_image(CongAI).is_ai = True`, `tags_for_image(congai).is_ai = False` (trên cây gộp có T-077). Ổ NTFS: nhánh và cây gộp **6/6 ảnh AI**, alt «Minh họa», bỏ "đã duyệt"; `list_folder(0, "…/congai").rel_dir` = `…/CongAI`; `main` `d9e279f`: B, F ra ảnh thật (lỗi cũ tái hiện đúng), D "không dùng được". Ổ Drive giả lập: B, D, E, F ra ảnh thật. Ổ chia sẻ Windows (`\\localhost\C$`), thư mục phân biệt hoa thường: Soi Lỗi đã thử, đúng. Mac/Linux: cách xem thư mục cha đúng khi chạy giả trên NTFS và trên ổ Drive thật (cả 2 lần không qua `fd`); phần mở bằng `fd` chưa chạy trên máy nào (T-063) |
| Điều kiện 2a của T-056 bỏ được chưa | **Chưa** | Vì LC-T076-1: trên ổ Drive, `list_folder` theo đường dẫn trong nháp vẫn trả chữ đã gõ (B, F). Thêm nữa, trên ổ Drive cả cách đi từ gốc (2a) cũng hở khi danh sách thư mục cha bị cắt (E), nên 2a giữ bắt buộc **và** LC-T076-1 phải sửa trước T-056. Hạ 2a xuống khuyến nghị khi: LC-T076-1 sửa xong (6 ca `xfail` thành XPASS), T-063 chạy phần Mac qua |
| **LC-T055-2** (= SL-T055-4, Thấp) | **Đóng**, còn phần dư LC-T076-2 | `stat_image` lại ở tên mới, khác cỡ hay giờ sửa thì không dùng được, dùng `entry` của lần kiểm mới (`drafts.py:930-933`); danh sách bị cắt không nhận tên chỉ trùng không phân biệt hoa thường (`:784-788`). Ở `folders.py` thêm một lớp: tên trên ổ phải trỏ đúng mục vừa kiểm (`:572-579`). 3 test SL-T055-4 qua (không `xfail`) |
| **LC-T055-3** (= SL-T055-5, Thấp) | **Đóng** (trên ổ Drive gắn với LC-T076-1) | Windows: `stat_image` không xem thư mục cha; Mac/Linux: `_listed_names` không giới hạn số mục, chỉ thời gian, dừng khi gặp tên trùng hẳn (`:156-158`). Danh sách thư mục cha bị cắt thì giữ tên `stat_image` (`drafts.py:784-788`): đúng khi tên đó là tên trên ổ; trên ổ Drive thì không (luồng D, E của LC-T076-1). Test SL-T055-5 qua |
| Việc 3 · F1: lớp chặn T-048 giữ nguyên | **Đạt** | `_parse_rel`, `_is_safe_name`, `_resolve_inside` (`..`, đường tuyệt đối, ổ khác, UNC, tên thiết bị, 8.3, ẩn, symlink, junction, `is_relative_to(gốc)`), `_Scan` (giữ thư mục, `O_NOFOLLOW` từng tầng, so đường thật, ngân sách) **không đổi một dòng** (`git diff` chỉ thêm hàm mới). `read_image_bytes` vẫn `O_NOFOLLOW`, so inode, giới hạn cỡ (`:736-760`). `_resolve_inside` vẫn chạy **trước** bước lấy tên. Test T-048 (`tests/test_images_folders_soi_loi.py`, phần T-048 của `tests/test_images_folders.py`) qua, không sửa; 3 `xfail` R2-1 ×2, R2-2 vẫn `xfail` |
| F1: bước xác nhận tên không mở đường đọc mới ra ngoài gốc | **Đạt** | Tên trên ổ chỉ được dùng sau `_is_safe_name` và giới hạn 1.024 ký tự (`:570-571`), rồi `lstat` ở tên đó và **so định danh** với mục đã kiểm trong gốc (`:572-579`): khác thì `_ChangedError`. `stat_image` dựng `ImageRef` mới qua `ImageRef(...)` (kiểm lại dạng chữ, đuôi ảnh). `list_folder` quét theo tên mới, `_Scan` kiểm lại đường đi như cũ. Mac/Linux: thư mục cha mở bằng `fd` từng tầng `O_NOFOLLOW` từ gốc, chỉ đọc tên (`scandir` không trả `.`, `..`). Khi một tầng giữa bị tráo thành junction, `os.lstat` theo đường dẫn có thể đi qua junction tới một mục ngoài gốc, nhưng chỉ để lấy số định danh so sánh, không trả gì ra (cùng kiểu với `lstat` từng tầng của `_resolve_inside`, có từ T-048). **Thử 2** (`lc_t076_exp2.py`, cây gộp): tráo tầng giữa thành junction trỏ ra thư mục ngoài có `sub/a.jpg` cùng tên (777 byte), xóa tầng giữa, đổi tên tầng giữa, đúng lúc `_disk_names` chạy × gõ đúng / gõ khác hoa thường × cách Windows / cách xem thư mục cha × `stat_image` / `list_folder` (24 ca): 24/24 lỗi gọn ("Thư mục vừa bị thay đổi…" hay "Không tìm thấy…"), **0 lần trả số liệu hay tên file ngoài gốc, 0 lần mở file ảnh**, câu báo không có đường dẫn, không xích lỗi hệ điều hành. Soi Lỗi `test_link_swapped_in_after_path_check` (8 ca) qua |
| F1: câu báo không lộ đường dẫn | **Đạt** | Câu mới đều cố định: `_MSG_SLOW` (`folders.py:82`), `_MSG_FOLDER_NAME` (`drafts.py:109-112`); lỗi mới `raise … from None` (`folders.py:575-577`, `:603-608`). `_FolderNames` chỉ chuyển tiếp câu của `ImageFolderError` (`drafts.py:771-776`) |
| F3 | **Đạt** | Không đọc/ghi file chữ, không `pickle`, `eval`, `yaml`, không SQL mới. Nháp vẫn đọc bằng pydantic, dựng lại `DraftImage` trước khi kiểm (`drafts.py:906`) |
| Việc 4 · SL-T076-1 | **Giữ Thấp** (= LC-T076-2) | Xem bảng lỗi. Sửa ở T-076 lượt 2 cùng LC-T076-1 (khuyên); tách riêng thì không bắt buộc trước T-056 |
| Việc 5 · gộp với `origin/main` | **Không xung đột; test qua; chưa nên gộp ngay** | `git merge-tree --write-tree origin/main team/T-076`: `origin/main` `dd1a217` → cây `4bdf8ed`; sau khi `main` lên `291879a` (chỉ đổi `docs/team/board.md`, `dong-bo.md`) → cây `bad779e`, cùng code. `main` đổi từ gốc `seo_app/images/tags.py`, `seo_app/storage/image_tags.py` (T-077), là module `drafts.py` dùng: 14 file test liên quan qua trên cây gộp (mục công cụ). Chưa nên gộp vì LC-T076-1 (điều kiện 1) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, `--all-files`, thư mục riêng chứa 8 file của diff, `tests/test_la_chan_t076.py`, patch `git log -p d9e279f..team/T-076`, 1 file mồi có chữ tiếng Việt): bắt đủ **2 dòng mồi**, **0 mục** ở file thật; đã xóa mồi. Không file nhị phân (`git diff --numstat`) |
| S2 | Đạt | `folders.py`, `drafts.py` không ghi log; câu báo mới cố định (bảng trên); `repr` của `ImageLibrary` vẫn giấu đường dẫn (`folders.py:464-466`) |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Diff không có code WordPress |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không tạo HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Không dựng prompt |
| A2 | Không áp dụng | Không gọi AI. Ảnh thật/AI do code quyết (`_safe_tags`, `drafts.py:796-816`, không đổi): xem LC-T076-1 |
| A3 | Không áp dụng | Không gửi AI |
| U1 | Không áp dụng | Không có giao diện; tên lấy từ ổ vẫn là dữ liệu chưa tin cậy (điều kiện escape của T-056 giữ) |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng mật khẩu |
| F1 | Đạt (có điều kiện) | Không đọc ra ngoài thư mục ảnh (bảng trên, thử 2). Điều kiện: LC-T076-1 (thẻ ảnh AI/thật trên ổ Drive), symlink thật và phần `fd` trên Mac (T-063) |
| F2 | Không áp dụng | Không xử lý byte ảnh; giới hạn cỡ vẫn ở `_check_size` (`folders.py:711-716`) |
| F3 | Đạt | Bảng trên |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi so với gốc; không import mới. pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Bộ chặn mạng tự bật (`tests/conftest.py`). `tests/test_soi_loi_t076.py` gọi `fsutil` có sẵn của Windows (danh sách đối số cố định, không `shell`, chỉ cho thư mục tạm của test), không gọi mạng; `tests/test_la_chan_t076.py` chỉ dùng thư mục tạm, không đụng ổ Drive |

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, `uv` 0.13.4, worktree `wt-T-076`, nhánh `team/T-076` tại `a1a48da`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (69 gói, `certifi==2026.10.19`) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có |
| bandit | `folders.py` + `drafts.py`: 1 mục B101 (`drafts.py:505`, `assert saved.saved_at is not None`), có từ T-016 (ở `d9e279f` là dòng 504). Test mới (bỏ B101): `tests/test_soi_loi_t076.py` B404, B603 (`fsutil`); `tests/test_la_chan_t076.py`: 0 | Có. Báo nhầm (mục dưới) |
| detect-secrets | **`PYTHONUTF8=1`**: bắt đủ mồi (khóa AWS giả, `password = …` trong file có «Đà Nẵng»), 0 mục khác. **Không** `PYTHONUTF8`: cùng thư mục ra `{}` (bỏ qua lặng lẽ, đúng LC-T049-4). Đã xóa mồi | Có |
| Soát lịch sử git | `git log -p d9e279f..team/T-076 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 3 dòng, đều là lệnh `detect-secrets` trong báo cáo. Mẫu khóa thật (`sk-ant-`, `sk-proj-`, `AIza…`, `AKIA…`, PEM, `ghp_`, `xox`): 0 | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check tests/test_la_chan_t076.py`: đã đúng định dạng | Có |
| pytest (nhánh) | `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_app_pages.py tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py -q -p no:cacheprovider -rsxX` (16:14–16:17): **1480 passed, 9 skipped, 8 xfailed, 0 hỏng**. File của tôi: `tests/test_la_chan_t076.py` **4 passed, 6 xfailed** | Có. Khớp số của Soi Lỗi. 9 bỏ qua: symlink cần quyền trên Windows (7), phần chỉ Mac/Linux (2). 8 xfail: R2-1 ×2, R2-2 (T-048), SL-T067-1 ×4, SL-T076-1. Chạy `--runxfail`: 6 ca của tôi hỏng đúng ở `assert` (ra `…/congai/…`, thẻ `that/CT012`), không do lỗi dựng test |
| pytest (cây gộp) | Cây gộp `4bdf8ed` giải nén bằng `git archive`, chạy bằng `.venv` của worktree; 11 file trên + `tests/test_soi_loi_t077.py`, `tests/test_la_chan_t074.py`, `tests/test_soi_loi_t074.py` (thẻ ảnh T-077) (16:18–16:21): **1760 passed, 9 skipped, 8 xfailed, 0 hỏng**. Thêm `tests/test_la_chan_t076.py` + `tests/test_soi_loi_t076.py`: 49 passed, 7 xfailed | Có: plugin in `__file__` cho thấy `seo_app/images/tags.py`, `seo_app/storage/drafts.py` nạp từ thư mục cây gộp. Cây `bad779e` (`main` mới) chỉ khác ở 2 file `docs/team/` |

**Chưa chạy được (không ghi là đạt):** symlink thật (Windows này lỗi 1314), phần `fd` của `_listed_names` và ổ APFS/NFD thật (T-063, Mac). Ổ Drive chỉ thử ở mức hỏi tên thư mục (chỉ đọc); chưa đặt ảnh thật vào Drive để chạy cả luồng nháp, vì sẽ ghi lên Drive của chủ dự án (luồng nháp chạy trên ổ giả lập đúng hành vi đã đo). Ổ USB định dạng FAT32/exFAT trên Windows chưa thử (cách sửa bằng danh sách thư mục không phụ thuộc loại ổ). Không chạy toàn bộ pytest (Chỉ Huy chạy khi gộp).

## Báo nhầm đã loại

- **bandit B101** `drafts.py:505`: `assert` có từ T-016, chỉ để kiểu dữ liệu.
- **bandit B404, B603** `tests/test_soi_loi_t076.py:28`, `:135`: `subprocess.run([fsutil, "file", "setCaseSensitiveInfo", <thư mục tạm>, "enable"])`, danh sách đối số cố định, không `shell`, `timeout=30`, chỉ bật phân biệt hoa thường cho thư mục tạm của test; không bật được thì test bỏ qua.
- **detect-secrets**: các mục duy nhất là chuỗi mồi tôi tự đặt.

## Thử độc lập của Lá Chắn

Script ngoài repo (thư mục nháp của phiên; bản sao ở thư mục ghi chú chung `T-076-la-chan-scripts/`), chạy bằng `.venv` của worktree (`python -I -X utf8 <script> <thư mục code>`). Bản `main` cũ giải nén từ `git archive d9e279f`, cây gộp từ `git archive 4bdf8ed`.

| # | Thử gì | Kết quả |
|---|---|---|
| D1–D4 | **Ổ Google Drive for Desktop thật** (H:, I:), chỉ đọc, chỉ in Đúng/Sai, không in hay lưu tên nào của chủ dự án, không mở file, không ghi: `realpath`, `FindFirstFileW`, `GetShortPathNameW`, `os.scandir` gốc ổ, code T-076 (`_resolve_inside` + `_disk_names` hai cách) với `My Drive` và 4 thư mục người dùng tạo, gõ đảo hoa thường. Đối chứng ổ NTFS C: | Drive (`My Drive` ở H:, I: và 4 thư mục người dùng tạo, 6 lần hỏi): `resolve` trả **chữ đã gõ** 6/6, `FindFirstFileW` và danh sách thư mục cho tên trên ổ 6/6; T-076 cách Windows sai 6/6, cách xem thư mục cha đúng 6/6, so định danh qua; không có tên 8.3. NTFS: đúng ở mọi cách |
| 1 | Thử 1, 4 của T-055 dựng lại: nháp `…/congai/cong.png`, trên ổ `CongAI`, 6 luồng A–F (không quét / quét theo nháp / quét từ gốc / danh sách cha bị cắt / chọn lại ảnh) × ổ NTFS / ổ Drive giả lập × nhánh / cây gộp / `main` | NTFS: nhánh, cây gộp 6/6 ảnh AI. Drive giả lập: B, D, E, F ảnh thật (LC-T076-1); `main`: B, F ảnh thật, D không dùng được, E ảnh AI |
| 2 | F1: tráo junction ra ngoài / xóa / đổi tên tầng giữa đúng lúc `_disk_names` chạy, 24 ca | 24/24 lỗi gọn; 0 lần trả số liệu, tên file ngoài gốc; 0 lần mở file ảnh; câu báo không có đường dẫn |
| 3 | Mô phỏng cách sửa (b) của LC-T076-1 (Windows lấy tên bằng `_listed_names`) với `tests/test_la_chan_t076.py --runxfail` | 10/10 qua |

## Ghi nhận (không thành lỗi)

- **Mac và ổ Drive chậm:** từ T-076, mỗi `stat_image` trên Mac/Linux đọc tên các thư mục cha (không nhớ giữa các lần gọi), giới hạn 10 giây mỗi lần; `list_folder` có thể tới 2 × 10 giây. Nháp nhiều ảnh trên ổ chậm có thể kiểm rất lâu. Không phải lỗ hổng; T-056 nên kiểm ảnh nháp một lần khi mở nháp (đề xuất Lá Chắn T-055 đã có), T-063 đo trên Mac. Nếu lượt 2 chọn cách (b) cho Windows thì cùng lưu ý này áp dụng cho Windows (cách (a) `FindFirstFileW` không phải đọc cả thư mục).
- **Phép chặn tên 8.3 trên ổ Drive** (`_resolve_inside`, `folders.py:538-545`) dựa vào `resolve`, nên trên ổ Drive nó không làm gì. Ổ Drive không có tên 8.3 (`GetShortPathNameW` trả lại nguyên tên), nên hôm nay không có đường đi; nếu lượt 2 có hàm lấy tên theo danh sách thư mục trên Windows thì phép chặn này có thể dùng chung hàm đó.
- **`ai_roots` theo tên gốc:** trên ổ Drive, `RootInfo.label` là chữ trong `IMAGE_FOLDERS`, không phải tên trên ổ. Khi T-056 tính `ai_roots` bằng `is_ai_name` (điều kiện 2d), nên dùng tên trên ổ của thư mục gốc, hoặc hướng dẫn ghi `IMAGE_FOLDERS` đúng chữ hoa thường như trên ổ (T-069). Rủi ro thấp: chủ dự án tự ghi `.env`.
- Ảnh **không dùng được** vẫn có thẻ đọc theo chữ trong nháp (đã ghi ở T-055; T-056 điều kiện 2b).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **T-076 lượt 2 (Thợ Máy), trước khi gộp `main`:** sửa **LC-T076-1** theo cách đề xuất (Windows lấy tên từ danh sách thư mục, không từ `resolve`; sửa chú thích, docstring; thêm kiểu ổ "resolve trả chữ đã gõ" vào test; gỡ `@XFAIL` của `tests/test_la_chan_t076.py` khi XPASS). Khuyên sửa luôn **LC-T076-2** (cách (a) của Soi Lỗi, gỡ `xfail` SL-T076-1). Sau đó Soi Lỗi rút gọn, Lá Chắn rút gọn (F1). Lý do không gộp ngay dù chưa có màn hình nào dùng: bản này trên ổ Drive kém hơn `main` ở luồng D, E và docstring hứa điều không đúng trên ổ Drive, dễ làm T-056 dựa vào. Chủ dự án muốn gộp trước thì phải ghi quyết định chấp nhận rủi ro; khi đó LC-T076-1 vẫn phải sửa trước khi gộp T-056.
2. **T-056 (Họa Sĩ):** điều kiện **2a giữ bắt buộc** (không bỏ được), 2b–2d giữ. Test của 2a chạy thêm trên ổ giả "resolve trả chữ đã gõ" (như `typed_resolve` trong `tests/test_la_chan_t076.py`), cả ca danh sách thư mục cha bị cắt. 2a hạ xuống khuyến nghị khi điều kiện 1 xong và T-063 qua; Lá Chắn T-056 xác nhận.
3. **T-063 (Mac):** chạy thêm `tests/test_images_folders.py`, `tests/test_soi_loi_t076.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py` (phần `fd` của `_listed_names`, symlink thật, NFD thật); đo `stat_image` và kiểm nháp nhiều ảnh trên Google Drive for Desktop của Mac.
4. **Chỉ Huy:** sau khi gộp, chạy toàn bộ pytest trên Windows như thường lệ.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 1 Trung bình (LC-T076-1), 1 Thấp (LC-T076-2 = SL-T076-1). F1, F3 đạt: mọi lớp chặn T-048 giữ, bước xác nhận tên không mở đường đọc mới ra ngoài gốc (24 ca tráo, xóa, đổi tên), câu báo không lộ đường dẫn. LC-T055-1 đóng trên ổ thường, **chưa đóng trên ổ Google Drive for Desktop của Windows** (đo thật trên máy chủ dự án); LC-T055-2, -3 đóng. Điều kiện 2a của T-056 chưa bỏ được. Gộp `main` không xung đột, test liên quan qua trên cây gộp, nhưng chưa nên gộp ngay: sửa LC-T076-1 ở T-076 lượt 2 trước.

Lá Chắn không sửa code ứng dụng hay test của người khác; chỉ thêm `tests/test_la_chan_t076.py` (6 ca `xfail(strict=True)` LC-T076-1, 4 ca đối chứng). Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

---

## Lượt 2 (2026-10-22, rút gọn): LC-T076-1, LC-T076-2

| Mục | Nội dung |
|---|---|
| Lời giao | Chỉ Huy B (chủ dự án đã duyệt): kiểm rút gọn (F1) sau Thợ Máy lượt 2 và Soi Lỗi lượt 2 |
| Phạm vi | Diff `ca1e91d..7dcb553` (code lượt 2: `3930e94` LC-T076-1, `491609b` LC-T076-2; sau đó chỉ có test và báo cáo): `seo_app/images/folders.py` (+66/−18), `seo_app/storage/drafts.py` (+25/−14), `tests/test_images_folders.py` (+95/−5), `tests/test_drafts_images.py` (+31/−3), `tests/test_soi_loi_t076.py` (+250/−14), `tests/test_la_chan_t076.py` (−12, chỉ gỡ `xfail`), 2 báo cáo. Đã đọc: báo cáo Thợ Máy, Soi Lỗi mục "Lượt 2", ghi chú cuối phiếu (trên `origin/main`), phiếu T-079, báo cáo Soi Lỗi T-063 (nhánh `team/T-063`). Thử gộp với `origin/main` `cc9167f` |
| Ngày | 2026-10-22 (09:45–10:20 +07) |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (LC-T076-3 = SL-T076-2, giữ mức; có thêm một biến thể). **LC-T076-1 đóng** (cả trên ổ Google Drive for Desktop thật của máy này), **LC-T076-2 đóng**. F1, F3 đạt; T-076 không làm nặng thêm SL-T063-2. **Gộp `main` được ngay** |

### Tóm tắt lượt 2 (cho chủ dự án)

Lỗi Trung bình tôi tìm ra hôm qua **đã được sửa đúng**. Tôi thử lại trên chính ổ Google Drive của máy này (chỉ đọc: không mở, không sửa file nào, không ghi lại tên thư mục nào): nay app luôn lấy đúng tên thật của thư mục (6/6 lần), nên ảnh trong thư mục kiểu `CongAI` luôn là **ảnh AI**, câu mô tả có «Minh họa» và phải duyệt lại. Tôi thử lại cả 6 cách mở ảnh của nháp trên ổ thường và trên ổ giả lập kiểu Google Drive: 24/24 lần đều ra ảnh AI. App vẫn **an toàn với file trên máy**: tráo thư mục, xóa, đổi tên, cài lối tắt ra ngoài đúng lúc app đang hỏi tên thư mục (60 lần thử) thì app chỉ báo lỗi gọn, không lấy được gì ngoài thư mục ảnh.

Còn **1 lỗi nhỏ (Thấp)** Soi Lỗi tìm ra: nếu đúng lúc app đang kiểm có người đổi tên thư mục ảnh AI, mà ở thư mục khác lại có sẵn một bản sao y hệt ảnh đó, app có thể dùng bản sao như ảnh thật. Tôi tìm thêm một cách khác của cùng lỗi; cách này chỉ xảy ra với thư mục "phân biệt chữ hoa/thường", mà ổ của máy Windows, Mac và ổ Google Drive mặc định không như vậy. Không đọc được gì ngoài thư mục ảnh. Cách sửa nhỏ, nên làm ở phiếu T-079 sắp tới.

Gộp T-076 vào bản chính **được ngay**: không đụng phần nào khác, các bài kiểm liên quan đều qua. Màn hình chọn ảnh T-056 không còn bắt buộc "chỉ đi từ thư mục ảnh gốc xuống", chỉ cần giữ bài kiểm cho trường hợp này.

### Lỗi phát hiện (lượt 2)

Số dòng theo `7dcb553`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T076-3 (= SL-T076-2) | Thấp (**giữ mức**) | **Bước "hỏi lại tên cũ" của LC-T076-2 không so định danh file giữa các lần hỏi.** Khi danh sách thư mục cho tên khác tên `stat_image` vừa trả, `_check_images` hỏi lại tên cũ và so `ImageEntry` (tên, cỡ, giờ sửa) với lần trước, rồi nhận ảnh ở tên của danh sách nếu cùng tên, cùng cỡ, cùng giờ sửa. Ghi chú cuối phiếu ghi cách này là "hỏi lại tên cũ … và so định danh", nhưng phép so định danh chỉ có **bên trong** một lần `stat_image` (`folders.py:605-613`), không có giữa các lần hỏi. Lần hỏi lại chỉ cho biết tên **lúc hỏi lại**. Thêm nữa, `_FolderNames` nhớ danh sách mỗi thư mục cho **cả một lần kiểm nháp** (`drafts.py:769-775`), nên danh sách có thể cũ hơn nhiều so với lần `stat_image` của ảnh đang kiểm | `drafts.py:929-944`, `:769-775` | (1) **Soi Lỗi:** đổi tên đi rồi đổi lại quanh lúc xem danh sách (ổ không phân biệt hoa thường: 3 lần đổi trong khe vài mili giây; ổ phân biệt hoa thường: đi rồi về) → bản sao `Congai/cong.png` (cùng cỡ, cùng giờ sửa) được dùng, thẻ `that`/CT012, alt không «Minh họa», vẫn "đã duyệt". Tôi chạy lại 2 test `xfail` của Soi Lỗi với `--runxfail`: hỏng đúng ở câu so định danh (file được dùng có số định danh khác file đã chọn). (2) **Biến thể mới (Lá Chắn):** thư mục công trình **phân biệt** hoa thường (bật bằng `fsutil` trên thư mục tạm), có `congai/cong.png` là bản sao y hệt ảnh AI `X/cong.png` (`shutil.copy2` giữ giờ sửa, như Explorer). Nháp 2 ảnh: ảnh 1 ở `truoc/` làm danh sách thư mục công trình được đọc và nhớ; ngay sau đó `X` đổi tên thành `CongAI` **một lần, không đổi lại**; ảnh 2 nháp ghi `CongAI/cong.png` (nguồn `"that"`, alt đã duyệt) → **dùng bản sao ở `congai/`**, thẻ ảnh thật CT012, alt không «Minh họa», vẫn "đã duyệt" (script `lc_t076_l2_exp3.py`; test `tests/test_la_chan_t076.py::test_lc_t076_3_cached_listing_and_one_rename_on_case_sensitive_folder`, `xfail(strict=True)`). Khe ở đây là thời gian giữa hai ảnh của nháp (có thể vài giây với nháp nhiều ảnh), không phải vài mili giây. Cùng kịch bản trên ổ thường (không phân biệt hoa thường): ảnh 2 **không dùng được** (an toàn). **Vì sao vẫn Thấp:** phải có cùng lúc: thư mục phân biệt hoa thường (không phải mặc định của Windows, Mac; ổ Google Drive của chủ dự án không phân biệt), hai thư mục chỉ khác hoa thường cùng tồn tại, bản sao y hệt ảnh AI đặt ở thư mục không mang tên AI, nháp ghi `"that"` cho ảnh ở thư mục AI (nháp sửa tay hay thẻ sửa tay), và một lần đổi tên đúng lúc app đang kiểm nháp. File được dùng nằm trong thư mục ảnh và mang thẻ theo chính chỗ của nó: bản sao ảnh AI mà người dùng đặt vào thư mục ảnh thật thì chọn thẳng cũng ra "ảnh thật". **F1 giữ:** mọi lần hỏi qua đủ lớp chặn, đọc sau này qua `read_image_bytes` | **Cách (a) của Soi Lỗi (khuyên):** danh sách xem hết mà không có đúng tên `stat_image` trả thì ảnh không dùng được (`_MSG_FOLDER_NAME`); bỏ nhánh nhận tên của danh sách (`drafts.py:938-944` thành một câu báo). Thử trên bản sao code ở thư mục nháp: test LC-T076-3 của tôi và 2 ca SL-T076-2 thành XPASS; đúng 3 test Soi Lỗi đã nêu phải đổi theo (`test_single_case_insensitive_match_takes_real_name`, `test_lc_t076_2_folder_renamed_between_checks_is_unavailable` của Thợ Máy; `test_mac_nfd_folder_names_keep_ai_and_real_tags` của Soi Lỗi T-055). Cả 3 giả một kiểu ổ mà từ lượt 2 `ImageLibrary` thật không còn (`stat_image` trả lại chữ đã gõ). Hoặc (b): so định danh file giữa các lần hỏi (hàm riêng của `ImageLibrary`, không đưa đường dẫn ra ngoài module; ổ không có số định danh thì không dùng được). **Nơi sửa:** T-079 như Chỉ Huy định được, nhưng phiếu T-079 hiện cấm sửa `seo_app/storage/**`: Chỉ Huy phải cho sửa `seo_app/storage/drafts.py` và 3 test trên (Thợ Máy sửa 2 test của mình, Soi Lỗi sửa test T-055 của mình). Gỡ `xfail` SL-T076-2 ×2, LC-T076-3 khi XPASS. Không bắt buộc trước T-056 về bảo mật (Thấp); T-079 vốn đã chặn T-056 nên làm cùng là rẻ. Hoặc chủ dự án ghi sổ rủi ro |

### Kiểm lại lỗi cũ và các việc được giao (lượt 2)

| Mã / việc | Kết quả | Bằng chứng |
|---|---|---|
| Việc 1 · **LC-T076-1** (Trung bình) | **Đóng** | `_disk_names` (`folders.py:580-614`) không còn lấy tên từ `resolve`. Windows gọi `_found_names` (`:616-627`): mỗi tầng hỏi thư mục cha đúng một mục bằng `FindFirstFileW` (`_win_listed_name`, `:327-345`), tầng sau đi theo tên trên ổ của tầng trước, cùng luật `_match_disk_name` với cách của Mac/Linux. Hỏi không được thì báo lỗi (`Không tìm thấy…`, `Không đọc được…`), không quay về chữ đã gõ; vẫn `lstat` ở tên mới và so định danh (`:605-613`). **Ổ Google Drive for Desktop thật** (H:, I:; chỉ đọc, chỉ in Đúng/Sai, script `lc_t076_l2_drivefs_probe5.py`): code lượt 2 cho đúng tên trên ổ **6/6** (`My Drive` ở 2 ổ, 4 thư mục người dùng tạo; 1 và 2 tầng; gõ đảo hoa thường), chạy 2 lượt; `resolve` vẫn sai 6/6 (chỗ hỏng nằm ở ổ, code đã tránh); cách của Mac cũng đúng 6/6; mỗi lần lấy tên 2–5 ms khi ổ đã "nóng" (lượt đầu có lúc tới 85 ms). **Thử 1 dựng lại** (6 luồng A–F: không quét, quét theo nháp, quét từ gốc, danh sách cha bị cắt có/không quét, chọn lại ảnh) × ổ NTFS / ổ giả lập Drive (`typed_resolve`) × cách Windows / cách Mac: **24/24 ảnh AI**, alt «Minh họa», bỏ "đã duyệt"; `list_folder(0, "…/congai").rel_dir` là `…/CongAI`. 6 ca LC-T076-1 trong `tests/test_la_chan_t076.py` qua; Thợ Máy chỉ gỡ `@XFAIL` (`git diff ca1e91d..7dcb553 -- tests/test_la_chan_t076.py`: chỉ có dòng xóa, không đổi `assert`). Linux (Soi Lỗi T-063, cloud, mã `006b13b`): 5 file test của T-076 không hỏng ca nào do T-076 (1 hỏng `test_unreadable_subfolder_is_counted_not_fatal` là SL-T063-1, test cũ chỉ viết cho Windows, hỏng cả trên `main`); phần `fd` của `_listed_names` với symlink thật qua |
| **LC-T055-1** (Trung bình, T-055) | **Đóng** trên Windows (NTFS, ổ chia sẻ, Google Drive for Desktop, thư mục phân biệt hoa thường); Linux: phần `fd` qua; Mac: chờ máy Mac | Như dòng trên. Ổ phân biệt hoa thường (Linux, thư mục bật bằng `fsutil`): `congai` là thư mục khác, không trỏ tới `CongAI`, nên lỗi này không xảy ra |
| Điều kiện **2a** của T-056 | **Hạ xuống khuyến nghị** (giữ test bắt buộc) | Gốc lỗi (tên theo chữ gõ) đã sửa và đã đo trên đúng loại ổ chủ dự án dùng. Phần T-063 liên quan tới 2a (`_listed_names` bằng `fd` trên Linux) đã qua; T-063 "không đạt" là vì SL-T063-2 ở đường đọc, không liên quan 2a. **Kèm:** (i) T-056 vẫn phải có test của 2a: nháp `…/congai/cong.png`, trên ổ `CongAI`; mở nháp, mở thư mục (kể cả theo đường dẫn ghi trong nháp), chọn lại ảnh → ảnh AI, alt «Minh họa»; chạy cả trên ổ giả `typed_resolve` và ca danh sách thư mục cha bị cắt. Test là bắt buộc; còn đi từ gốc hay theo đường dẫn trong nháp thì Họa Sĩ chọn. (ii) Trước khi dùng app trên máy Mac: phần Mac của T-063 chạy các ca khác hoa thường của T-076 trên APFS (tên NFD thật); hỏng thì 2a quay lại thành điều kiện. Chủ dự án hiện chưa có máy Mac nên (ii) không chặn gì bây giờ. Lá Chắn T-056 kiểm (i) |
| **LC-T076-2** (= SL-T076-1, Thấp) | **Đóng**, còn phần dư LC-T076-3 | `drafts.py:938-944`: danh sách cho tên khác thì hỏi lại tên cũ; khác kết quả lần trước thì không dùng được; giống thì `stat_image` ở tên mới, phải đúng tên (`again.ref == real`), cùng cỡ, cùng giờ sửa. Với `ImageLibrary` thật, tên `stat_image` trả và tên trong danh sách đều do thư mục cha liệt kê ra, nên nhánh đổi tên chỉ còn chạy khi thư mục đổi tên giữa các lần xem. Ca tráo một lần của Soi Lỗi (`test_sl_t076_1_…`) qua. Đây là cách Chỉ Huy đã chấp nhận (không phải đổi test Soi Lỗi T-055); về bảo mật tôi đồng ý, trừ phần dư LC-T076-3 |
| Việc 3 · F1: lớp chặn T-048 | **Giữ** | `git diff ca1e91d..7dcb553 -- seo_app/images/folders.py` không đụng `_parse_rel`, `_is_safe_name`, `_resolve_inside`, `_checked_file`, `_Scan`, `read_image_bytes`; chỉ thêm `_win_listed_name`, `_found_names`, khai báo `FindFirstFileW`/`FindClose` trong `_kernel32`, sửa `_disk_names` và 2 chỗ gọi. Test T-048 (`tests/test_images_folders_soi_loi.py`) không đổi, qua; 3 `xfail` R2-1 ×2, R2-2 giữ |
| F1: bước hỏi tên từng tầng | **Đạt** | `FindFirstFileW` chỉ được hỏi bằng tên đã qua `_is_safe_name` (không có `*`, `?`, `<`, `>`, `"`, `:`, `\`, `/`; không `.`, `..`; không chấm hay khoảng trắng cuối; không tên thiết bị); các tầng trước là tên trên ổ đã trùng khóa với tên gõ. Chỉ lấy tên (`cFileName`): không mở file, không đọc cả thư mục. Tên ngắn 8.3: ổ trả tên dài, khác khóa → "Không tìm thấy". Hỏi theo đường dẫn, nên khi một tầng giữa bị tráo thành junction thì `FindFirstFileW` tầng sau có thể đi xuyên junction và trả tên một mục ngoài gốc **cùng khóa với chữ đã gõ**; bước `lstat` + so định danh sau đó (`:605-613`) từ chối, không trả tên hay số liệu nào. **Thử 2 lượt 2** (`lc_t076_l2_exp2.py`): tráo junction ra ngoài gốc / xóa / đổi tên tầng giữa ở 3 thời điểm (trước khi lấy tên; **giữa hai tầng hỏi** `FindFirstFileW`; ngay trước `lstat` kiểm lại) × gõ đúng / gõ khác hoa thường × cách Windows / cách Mac × `stat_image` / `list_folder`: **60/60 lỗi gọn**, 0 lần trả số liệu hay tên file ngoài gốc, 0 lần mở file ảnh, câu báo không có đường dẫn, không xích lỗi hệ điều hành; mọi lần tráo đều kích hoạt đúng lúc |
| F1: SL-T063-2 (T-063, đường đọc) | **T-076 không làm nặng thêm** | `read_image_bytes` giữ nguyên so với `main` (chỉ đổi dòng nhận kết quả `_checked_file`). Số đo của Soi Lỗi T-063 (Linux, tráo nguyên tử liên tục): đọc lọt nội dung `main` 1.253/37.032 lần, T-076 1.062/35.125 (cùng mức). SL-T063-3 (`stat_image` lọt cỡ, giờ sửa) **giảm**: 3.095/37.032 → 363/35.125, vì kẻ tráo phải thắng thêm lần `lstat` kiểm lại. Bước hỏi tên mới chỉ trả tên (cùng khóa với chữ gõ), không trả nội dung hay số liệu. Mức SL-T063-2 do phiên Lá Chắn T-063 xét |
| F1: câu báo | **Đạt** | Lỗi mới của `_win_listed_name` là `_MSG_NOT_FOUND`/`_MSG_UNREADABLE` (câu cố định, ném thẳng, không xích lỗi hệ điều hành); `drafts.py` chỉ thêm chỗ ném `_MSG_FOLDER_NAME` |
| F3 | **Đạt** | Không đổi cách đọc file, JSON, SQL; `ctypes` chỉ thêm khai báo kiểu cho 2 hàm có sẵn của `kernel32` |
| Việc 4 · gộp `main` | **Được ngay** | `git merge-tree --write-tree origin/main team/T-076` (`origin/main` `cc9167f`): cây `c9cb0d8`, **không xung đột**. `origin/main` lúc kiểm **chưa có code T-065** (còn ở `team/T-065`, chờ cho gộp), nên thử thêm `main` + `team/T-065` (commit tạm, không đẩy) + T-076: cây `fb6afe6`, không xung đột; `main` + `team/T-063` + T-076: không xung đột. Test liên quan qua trên cả 2 cây gộp (mục công cụ). **SL-T063-4:** test `xfail(strict=True)` trong `tests/test_images_folders_t063.py` (nhánh `team/T-063`) thành **XPASS(strict)** khi có T-076. Tôi thử trên Windows bằng thư mục tạm bật phân biệt hoa thường (plugin `lc_cs_tmp.py`): `main` 2 XFAIL, `main` + T-076 2 XPASS. Trên Windows thường test này tự bỏ qua, nên lần chạy toàn bộ của Chỉ Huy sẽ không báo; gộp T-063 và T-076 theo thứ tự nào thì phiếu gộp sau phải gỡ dấu `xfail` đó (điều kiện 3) |

### Danh sách kiểm tra (lượt 2)

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, `--all-files`, thư mục riêng: 8 file đổi ở lượt 2, `tests/test_la_chan_t076.py` bản mới, patch `git log -p ca1e91d..7dcb553`, 1 file mồi có chữ tiếng Việt): bắt **đủ 2 dòng mồi**, **0 mục** ở file thật; không `PYTHONUTF8` thì ra `{}` (bỏ qua lặng lẽ, LC-T049-4). Đã xóa mồi. Không file nhị phân |
| S2 | Đạt | Không ghi log; câu báo mới cố định (bảng trên) |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1–W4 | Không áp dụng | Không có code WordPress, không gọi mạng |
| A1–A3 | Không áp dụng | Không dựng prompt, không gọi AI; ảnh thật/AI do code quyết (`_safe_tags` không đổi), xem LC-T076-3 |
| U1–U3 | Không áp dụng | Không có giao diện, không đụng đăng nhập |
| F1 | Đạt | Bảng trên (thử 2: 60/60). LC-T076-3 không phải lỗi F1 (không đọc ra ngoài thư mục ảnh) |
| F2 | Không áp dụng | Không xử lý byte ảnh; giới hạn cỡ giữ ở `_check_size` |
| F3 | Đạt | Bảng trên |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi từ `ca1e91d`; không import mới; pip-audit sạch |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới (Soi Lỗi, Thợ Máy, ca LC-T076-3 của tôi) chỉ dùng thư mục tạm và `fsutil` có sẵn của Windows (danh sách đối số cố định, không `shell`); không gọi mạng, không đụng ổ Drive thật |

### Kết quả công cụ quét (lượt 2)

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, `uv` 0.13.4, worktree `wt-T-076`, nhánh `team/T-076` tại `7dcb553`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (69 gói) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có |
| bandit | `folders.py` + `drafts.py`: chỉ B101 cũ (`drafts.py:505`). Test (bỏ B101): B404, B603 ở `tests/test_la_chan_t076.py:32`, `:232` và `tests/test_soi_loi_t076.py:33`, `:151` (gọi `fsutil`) | Có. Báo nhầm (mục dưới) |
| detect-secrets | Xem S1 | Có |
| Soát lịch sử git | `git log -p ca1e91d..7dcb553`, tìm `api[_-]?key`, `password`, `secret`, `token` (không phân biệt hoa thường): 4 dòng, đều là lệnh `detect-secrets` trong báo cáo. Mẫu khóa thật (`sk-ant-`, `sk-proj-`, `AIza…`, `AKIA…`, PEM, `ghp_`, `xox`): 0 | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check tests/test_la_chan_t076.py`: đã đúng định dạng | Có |
| pytest (nhánh) | 12 file: `tests/test_images_folders.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_app_pages.py tests/test_images_folders_soi_loi.py tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py -q -p no:cacheprovider -rsxX` (09:50–09:54): **1532 passed, 9 skipped, 9 xfailed, 0 hỏng**. Khớp số Soi Lỗi lượt 2. 9 xfail: 7 có từ trước (R2-1 ×2, R2-2 của T-048; SL-T067-1 ×4) + 2 SL-T076-2. Sau khi tôi thêm ca LC-T076-3: `tests/test_la_chan_t076.py` **10 passed, 1 xfailed** (`--runxfail`: hỏng đúng ở câu so định danh) | Có |
| pytest (cây gộp `c9cb0d8` = `main` + T-076) | Giải nén bằng `git archive`, chạy bằng `.venv` của worktree; 12 file trên + `tests/test_soi_loi_t077.py`, `tests/test_la_chan_t074.py`, `tests/test_soi_loi_t074.py` (thẻ ảnh T-077, T-074 trên `main`), 09:55–09:59: **1812 passed, 9 skipped, 9 xfailed, 0 hỏng**. `tests/test_la_chan_t076.py` bản mới: 10 passed, 1 xfailed | Có: plugin in `__file__` cho thấy `seo_app/images/tags.py`, `seo_app/storage/drafts.py` nạp từ thư mục cây gộp |
| pytest (cây gộp `fb6afe6` = `main` + T-065 + T-076) | 15 file trên + `tests/test_soi_loi_t065.py`, 09:59–10:02: **1829 passed, 9 skipped, 9 xfailed, 0 hỏng**. `tests/test_la_chan_t076.py` bản mới: 10 passed, 1 xfailed | Có (như trên; `config/content.toml` là bản T-065) |

**Chưa chạy được (không ghi là đạt):** symlink thật trên Windows này (lỗi 1314); phần Mac (chưa có máy Mac); đặt ảnh thật vào Google Drive để chạy cả luồng nháp trên ổ Drive (sẽ ghi lên Drive của chủ dự án; luồng nháp chạy trên ổ giả lập đúng hành vi đã đo). Không chạy toàn bộ pytest (Chỉ Huy chạy khi gộp).

### Báo nhầm đã loại (lượt 2)

- **bandit B404, B603** `tests/test_la_chan_t076.py:32`, `:232` (của tôi) và `tests/test_soi_loi_t076.py:33`, `:151` (Soi Lỗi): `subprocess.run([fsutil, "file", "setCaseSensitiveInfo", <thư mục tạm>, "enable"])`, danh sách đối số cố định, không `shell`, `timeout=30`; chỉ bật phân biệt hoa thường cho thư mục tạm của test; không bật được thì test bỏ qua.
- **bandit B101** `drafts.py:505`: có từ T-016.
- **detect-secrets**: các mục duy nhất là chuỗi mồi tôi tự đặt.

### Thử độc lập của Lá Chắn (lượt 2)

Script ngoài repo (thư mục nháp của phiên; bản sao ở thư mục ghi chú chung `T-076-la-chan-scripts/luot-2/`), chạy bằng `.venv` của worktree (`python -I -X utf8 <script> <thư mục code>`). Không sửa code ứng dụng.

| # | Thử gì | Kết quả |
|---|---|---|
| D5 | Ổ Google Drive for Desktop thật (H:, I:), code lượt 2: `_resolve_inside` + `_disk_names` hai cách, `_win_listed_name`; chỉ đọc, chỉ in Đúng/Sai và số giây | Đúng tên trên ổ 6/6 (2 lượt); `resolve` sai 6/6; cách Mac đúng 6/6; 2–5 ms mỗi lần khi ổ đã nóng |
| 1 | Thử 1 của lượt 1: 6 luồng A–F × NTFS / Drive giả lập × cách Windows / cách Mac | 24/24 ảnh AI, alt «Minh họa», bỏ "đã duyệt" |
| 2 | F1: tráo junction / xóa / đổi tên tầng giữa ở 3 thời điểm (có "giữa hai tầng hỏi `FindFirstFileW`"), 60 ca | 60/60 lỗi gọn; 0 lần lọt số liệu, tên ngoài gốc; 0 lần mở file ảnh |
| 3 | **LC-T076-3:** danh sách thư mục nhớ cho cả nháp + một lần đổi tên giữa hai ảnh; thư mục phân biệt / không phân biệt hoa thường | Phân biệt: bản sao được dùng như ảnh thật; không phân biệt: "không dùng được" |
| 4 | Cách (a) của Soi Lỗi trên bản sao code | LC-T076-3 và 2 ca SL-T076-2 thành XPASS; đúng 3 test Soi Lỗi đã nêu phải đổi |
| 5 | SL-T063-4 (nhánh `team/T-063`) trên thư mục tạm phân biệt hoa thường | `main`: 2 XFAIL; `main` + T-076: 2 XPASS(strict) |

### Ghi nhận lượt 2 (không thành lỗi)

- **Tên ngắn 8.3 trên ổ "resolve trả chữ đã gõ":** `read_image_bytes` vẫn chặn 8.3 bằng `resolve` (`_resolve_inside`), nên trên ổ vừa trả lại chữ đã gõ khi `resolve` vừa có tên 8.3 thì đọc được qua tên ngắn, còn `stat_image` từ chối (Soi Lỗi thử bằng `exp_83.py`). Vẫn là cùng một file trong thư mục ảnh (F1 giữ). Chưa thấy ổ thật nào có cả hai điều kiện (ổ Google Drive của máy này không có tên 8.3, đo ở lượt 1). T-079 làm lại đường đọc nên có thể cho `_checked_file` dùng chung bước lấy tên trên ổ.
- **Ổ ảo lạ trả lại chữ của truy vấn khi `FindFirstFileW`:** chưa thấy; ổ Google Drive của máy này đã đo là đúng. Nếu gặp, lớp phòng thứ hai của nháp vẫn đối chiếu với danh sách thư mục, trừ khi danh sách thư mục cha bị cắt.
- **Hằng `_NAMES_FROM_RESOLVE`** nay sai nghĩa với tên (Thợ Máy giữ vì test Soi Lỗi đặt hằng này; chú thích đã ghi đúng). Đổi tên ở T-079, Soi Lỗi sửa test theo.
- **Thiếu quyền xem danh sách một thư mục trên đường đi** thì ảnh "không dùng được" (đóng khi nghi ngờ; Soi Lỗi thử thật bằng `icacls`). Đúng hướng.
- **Tốc độ:** trên ổ Drive thật mỗi lần lấy tên 2–5 ms (1–2 tầng); Soi Lỗi đo trên ổ cục bộ và SMB: chậm hơn `main` một chút. T-056 nên kiểm ảnh nháp một lần khi mở nháp (đề xuất cũ).
- Tôi sửa file test của chính mình `tests/test_la_chan_t076.py`: thêm ca `xfail(strict=True)` LC-T076-3 và cập nhật lời mô tả đầu file, tiêu đề mục (LC-T076-1 nay qua); không đổi `assert` của các ca cũ.

### Điều kiện (lượt 2)

1. **LC-T076-3** (Thấp): sửa theo cách (a) ở **T-079** (như Chỉ Huy định; Chỉ Huy cho sửa thêm `seo_app/storage/drafts.py` và 3 test kể trên) hoặc ở một phiếu dọn; gỡ `xfail` SL-T076-2 ×2 (`tests/test_soi_loi_t076.py`), LC-T076-3 (`tests/test_la_chan_t076.py`) khi XPASS. Không bắt buộc trước T-056 về bảo mật; chủ dự án có thể chọn ghi sổ rủi ro thay.
2. **T-056 (Họa Sĩ):** điều kiện 2a của Lá Chắn T-055 **hạ xuống khuyến nghị**; test của 2a vẫn bắt buộc (nháp `…/congai/cong.png`, trên ổ `CongAI`; mở nháp, mở thư mục, chọn lại ảnh → ảnh AI, alt «Minh họa»; chạy cả trên ổ giả `typed_resolve` và ca danh sách thư mục cha bị cắt). 2b, 2c, 2d giữ nguyên.
3. **Khi gộp T-076 và T-063** (thứ tự nào cũng vậy): phiếu gộp sau gỡ `xfail` SL-T063-4 trong `tests/test_images_folders_t063.py` (chỉ thấy XPASS trên Linux, Mac hay thư mục phân biệt hoa thường).
4. **T-063 phần Mac** (khi có máy Mac, trước khi dùng app trên Mac): chạy các ca khác hoa thường của T-076 trên APFS; hỏng thì 2a quay lại thành điều kiện của T-056.
5. **Chỉ Huy:** sau khi gộp, chạy toàn bộ pytest trên Windows như thường lệ.

### Kết luận lượt 2

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (LC-T076-3 = SL-T076-2). LC-T076-1 và LC-T076-2 đóng; LC-T055-1 đóng trên Windows, kể cả ổ Google Drive for Desktop thật của máy chủ dự án. F1, F3 đạt: lớp chặn T-048 giữ nguyên, bước hỏi tên từng tầng không mở đường đọc mới ra ngoài gốc (60 ca tráo, xóa, đổi tên), câu báo không lộ đường dẫn; T-076 không làm nặng thêm SL-T063-2 và làm giảm SL-T063-3. Điều kiện 2a của T-056 hạ xuống khuyến nghị (giữ test). **Gộp `main` được ngay**: không xung đột với `origin/main` `cc9167f` (kể cả khi T-065, T-063 gộp trước), test liên quan qua trên cây gộp; nhớ gỡ `xfail` SL-T063-4 khi gộp cả T-063.

Lá Chắn không sửa code ứng dụng hay test của người khác. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

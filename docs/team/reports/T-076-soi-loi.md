# Báo cáo T-076 · Thư mục ảnh trả tên theo tên trên ổ · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-076](../tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (kiểm đầy đủ). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn (rút gọn, F1) được |

## Tóm tắt (cho chủ dự án)

Bản sửa của Thợ Máy làm đúng cả 4 yêu cầu của phiếu. Tôi thử trên ổ thật của máy này: thư mục tên kiểu `CongAI` mà bài nháp ghi `congai` (hay ghi chữ hoa, chữ thường lẫn lộn cả tên công trình tiếng Việt) thì ảnh trong đó **luôn là ảnh AI**, câu mô tả ảnh có «Minh họa» và phải duyệt lại, kể cả khi mở thư mục theo đúng đường dẫn ghi trong nháp. Tôi còn bật chế độ "phân biệt chữ hoa/thường" cho một thư mục thử trên Windows để có **cả** `CongAI` lẫn `congai` cùng lúc: app không lẫn hai thư mục. Thư mục ảnh có 5.200 mục thì ảnh trong thư mục con vẫn dùng được. Thư mục bị xóa hay bị đổi thành "lối tắt" đúng lúc app đang kiểm: app báo lỗi gọn, không lộ đường dẫn trên máy, không đọc ra ngoài thư mục ảnh. Trên Windows app không chậm hơn trước.

Tôi ghi **1 lỗi mức Thấp** (SL-T076-1): nếu đúng lúc app đang kiểm, có người đổi tên thư mục ảnh AI đi và đổi một thư mục khác có **bản sao y hệt** của ảnh (cùng cỡ, cùng giờ sửa, như khi chép bằng File Explorer) thành tên gần giống, app có thể dùng bản sao đó như **ảnh thật**. Rất khó xảy ra (phải đổi tên đúng khoảnh khắc vài phần nghìn giây), không đọc được gì ngoài thư mục ảnh. Cách sửa nhỏ, tôi đã thử trên bản sao.

Trên máy Mac app phải đọc thêm tên trong các thư mục mỗi lần kiểm một ảnh. Thử giả lập trên ổ mạng ở máy này: chậm hơn khoảng 2–3 lần ở bước kiểm ảnh (48 ảnh mất khoảng 2 giây thay vì 1 giây); ổ cục bộ thì gần như không khác. Cần đo lại trên Mac thật (phiếu T-063).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t076.py` | Mới: 13 hàm test, 46 ca (45 qua, 1 `xfail(strict=True)` SL-T076-1) |
| `docs/team/reports/T-076-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của người khác.

## Bằng chứng

Máy Windows 11 Pro của chủ dự án, Python 3.12.15, worktree `wt-T-076`, nhánh `team/T-076` (code của Thợ Máy tại `3bb126e`, không đổi). Máy đang chạy song song các agent khác (số giây chỉ để tham khảo).

```
$ uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py \
    tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py \
    tests/test_images_tags.py tests/test_app_pages.py tests/test_images_process.py \
    tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py -q -p no:cacheprovider -rsxX
(2026-10-21 15:00–15:06 +07, trước khi thêm file của tôi)
1435 passed, 9 skipped, 7 xfailed in 361.58s (0:06:01)

$ uv run pytest <10 file trên> tests/test_soi_loi_t076.py -q -p no:cacheprovider -rsxX
(2026-10-21 15:33–15:37 +07, có file của tôi)
1480 passed, 9 skipped, 8 xfailed in 244.48s (0:04:04)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t076.py
1 file already formatted

$ PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # trong thư mục nháp chứa bản chép 2 file của tôi
"results": {}   (file mồi có chữ tiếng Việt: có PYTHONUTF8 bắt 2/2, không có thì 0; đã xóa)
```

- Lượt đầu khớp đúng số của Thợ Máy. Lượt cuối thêm đúng 45 qua và 1 `xfail` (SL-T076-1) của tôi. 9 bỏ qua đều do máy Windows (6 ca T-048: symlink cần quyền hoặc chỉ chạy trên Mac/Linux; 1 ca `test_drafts_images.py` symlink; 2 ca symlink của T-052). 7 `xfail` có từ trước, không thuộc phiếu: R2-1 ×2, R2-2 (T-048), SL-T067-1 ×4. Không còn `xfail` nào của SL-T055.
- Không có file `tests/test_soi_loi_t048*.py` hay `tests/test_la_chan_t048*.py`; test Soi Lỗi của T-048 nằm ở `tests/test_images_folders_soi_loi.py` (đã chạy, không đổi trong nhánh). Thêm `test_images_process.py`, `test_soi_loi_t052.py`, `test_soi_loi_t067.py` vì có gọi `stat_image`/`list_folder` (như Thợ Máy).
- 4 test trước là `xfail` của SL-T055-4 (×3), SL-T055-5 nay qua (chạy riêng: `4 passed`).

### Thử đột biến

Chép `seo_app` sang thư mục nháp, sửa một chỗ, chạy `tests/test_soi_loi_t076.py` với `PYTHONPATH` trỏ vào bản sửa (đã kiểm `seo_app` được nạp từ bản sửa). Script ở thư mục nháp, không commit.

| Đột biến | Test của tôi hỏng (trên 45 ca qua) |
|---|---|
| M1 · `stat_image`, `list_folder` trả lại chữ đã gõ (như trước T-076) | 25 |
| M2 · `_match_disk_name` bỏ ưu tiên tên trùng hẳn | 5 |
| M3 · `_disk_names` bỏ so định danh mục ở tên trên ổ | 4 |
| M4 · `_check_images` bỏ so cỡ, giờ sửa khi lớp phòng thứ hai đổi tên | 1 (`test_folder_swapped_during_check_does_not_switch_to_another_file`; test của Thợ Máy bắt 2) |
| M5 · `_check_images` giữ `ref` theo nháp (không dùng `entry.ref`) | 4 |

## Kiểm từng việc của lời giao

### Việc 1 · Yêu cầu 1–4 của phiếu

| YC | Kết quả | Bằng chứng |
|---|---|---|
| 1 · `list_folder`/`stat_image` trả `ImageRef` theo tên trên ổ (LC-T055-1) | **ĐẠT** | `folders.py:548-580` (`_disk_names`), `:582-612` (`_listed_names`), `:647` (`list_folder`), `:718-728` (`stat_image`). Thử hoa/thường, tên tiếng Việt viết hoa toàn bộ (`ct012 - cổng INOX - tân phú`, `TÂN PHÚ`, `ĐÀ NẴNG`, `CỔNG SỐ 1`), sâu 20 tầng gõ chữ thường ở mọi tầng (test), cả hai cách lấy tên: luôn ra tên trên ổ, cả tên file (`Anh.JPG`); đường 151 tầng gõ đúng tên vẫn chạy, dưới 1 giây (script). NFC/NFD giả lập Mac: `_match_disk_name` (test của Thợ Máy), test `MacDisk` của T-055 qua; NTFS có 3 thư mục "Bệ cửa" viết 3 kiểu (dựng sẵn, NFD, 2 dấu đảo thứ tự, cùng khóa NFC): gõ kiểu nào ra đúng thư mục kiểu đó, kiểu thứ 4 không có trên ổ thì "không tìm thấy" (`test_three_spellings_of_the_same_vietnamese_letter`). Nháp `…/congai/cong.png`, trên ổ `CongAI`: ảnh AI, alt «Minh họa», bỏ "đã duyệt", chú thích «Ảnh minh họa (AI)» với `scanned` rỗng, `list_folder` theo thư mục ghi trong nháp (một tầng và đệ quy từ thư mục công trình gõ khác hoa thường), `ImageRef` dựng từ chữ trong nháp, **ở cả hai cách lấy tên** (`test_lc_t055_1_draft_case_variant_stays_ai_both_name_sources`, 8 ca; test nháp của Thợ Máy chỉ chạy cách của hệ điều hành đang chạy). Docstring `check_draft_images` ghi điều kiện `scanned` (`drafts.py:843-849`); `_MSG_FOLDER_NAME` có "mở lại từ thư mục ảnh gốc" (`drafts.py:109-112`) |
| 2 · Đổi tên đúng lúc kiểm (LC-T055-2) | **ĐẠT**, có **SL-T076-1** (Thấp) | `drafts.py:926-933` (`real_ref`, `stat_image` lại) ở tên theo danh sách, khác cỡ hay giờ sửa thì không dùng được; `:784-788`: danh sách bị cắt không nhận tên chỉ trùng không phân biệt hoa thường. Tráo ngay sau khi kiểm đường đi (trong `stat_image`/`list_folder`): báo "vừa bị thay đổi", cả hai cách lấy tên (test của Thợ Máy). Tráo giữa `stat_image` và lớp phòng thứ hai, file khác cỡ: không dùng được, kèm câu "mở lại từ thư mục ảnh gốc" (`test_folder_swapped_during_check_does_not_switch_to_another_file`, so **định danh** file). Bản sao cùng cỡ, cùng giờ sửa: lẫn sang file khác → SL-T076-1 |
| 3 · Gốc hơn 5.000 mục (LC-T055-3) | **ĐẠT** | Ổ thật, gốc **5.200** ảnh tên số (xếp trước "CT012…"), không giảm ngân sách: `list_folder(0).truncated = True`; ảnh `…/truoc/IMG_0001.jpg` dùng được, thẻ CT012; nháp `…/congai/…` và `CT012 - CỔNG INOX - TÂN PHÚ/CONGAI/…` ra ảnh AI «Minh họa», ở cả hai cách lấy tên (0,3–0,6 giây mỗi ảnh; script `exp_crowded.py`). Ổ thật phân biệt hoa thường, danh sách thư mục công trình bị cắt (ngân sách 1 mục): mỗi nháp vẫn đúng thư mục của nó (`test_case_sensitive_disk_draft_keeps_the_named_folder[...-danh-sach-bi-cat]`) |
| 4 · Gỡ `xfail` SL-T055-4, -5 | **ĐẠT** | Xem việc 3 |

### Việc 2 · Lớp chặn của T-048

| Lớp chặn | Kết quả | Bằng chứng |
|---|---|---|
| `..`, đường tuyệt đối, ổ khác, UNC, tên thiết bị, 8.3, ẩn, symlink/junction trên đường đi, `resolve` phải trong gốc | Giữ | `_parse_rel`, `_is_safe_name`, `_resolve_inside` không đổi một dòng (`git diff d9e279f..HEAD -- seo_app/images/folders.py`: chỉ thêm hàm mới, `_checked_file` trả thêm gốc). `_resolve_inside` vẫn chạy **trước** bước lấy tên. Test T-048 (Thợ Máy, Soi Lỗi) qua, không sửa |
| `O_NOFOLLOW`, so inode khi đọc, giới hạn cỡ | Giữ | `read_image_bytes` chỉ đổi dòng nhận kết quả `_checked_file` (`folders.py:736`) |
| Giới hạn số mục, thời gian khi quét | Giữ | `_Scan` không đổi. Bước lấy tên mới (Mac/Linux) không giới hạn số mục (đúng yêu cầu 3), có giới hạn `max_seconds`; ổ chậm khi kiểm nháp: ảnh không dùng được, câu "chậm" không có đường dẫn (`test_slow_disk_while_checking_draft_is_unavailable_and_safe`) |
| Đường lấy tên mới không đi ra ngoài gốc | Đạt | Mac/Linux mở thư mục cha từng tầng bằng `O_NOFOLLOW` từ gốc (`_posix_open_dir`); Windows không xem thư mục (tên từ `resolve`). Sau đó `lstat` mục ở tên trên ổ, so định danh với mục vừa kiểm (`folders.py:572-579`). Thử tráo junction (Windows) / symlink trỏ ra ngoài gốc, có `a.jpg` cùng tên, ngay sau khi kiểm đường đi: cả hai cách lấy tên, `stat_image` và `list_folder`, gõ đúng và gõ khác hoa thường: lỗi gọn, không trả tên hay số liệu file ngoài gốc (`test_link_swapped_in_after_path_check`, 8 ca). Đột biến M3 (bỏ so định danh) làm 4 ca này hỏng |
| Câu báo không lộ đường dẫn máy | Đạt | Câu mới `_MSG_SLOW` cố định; mọi lỗi mới `raise … from None`. Test của tôi kiểm câu báo không có đường dẫn tạm và không xích lỗi hệ điều hành (`raises_safely`) cho xóa giữa chừng, tráo liên kết, tên không có trên ổ |
| `xfail` cũ của T-048 | Giữ | R2-1 ×2, R2-2 vẫn `xfail(strict=True)` (hành vi không đổi) |

### Việc 3 · Soát test (`git diff d9e279f..team/T-076 -- tests/`)

- `tests/test_soi_loi_t055.py`: `0 dòng thêm, 12 dòng xóa` (`git diff --numstat`), đúng 3 khối `@pytest.mark.xfail(strict=True, reason=…)` (SL-T055-4 ×2 hàm, SL-T055-5). Không đổi thân test, `assert`, `parametrize`.
- `tests/test_images_folders.py`: `197 thêm, 0 xóa`, chỉ thêm (mục "tên trên ổ (T-076)").
- `tests/test_drafts_images.py`: `174 thêm, 33 xóa`. Test cũ bị đổi, **không test nào bị làm yếu**:
  - `test_scanned_ref_becomes_the_key` → `test_ref_is_the_disk_name_with_or_without_scan`: kiểm cả có và không có `scanned`, thêm `ref == entry.ref`, CT012, không phải ảnh AI. Ổ phân biệt hoa thường: trước đòi "dùng được với file của kết quả quét" (đổi file), nay đòi **không** đổi file: đổi hành vi có chủ đích, theo hướng an toàn.
  - `test_scanned_refs_match_other_unicode_form` → `test_scanned_ref_never_switches_to_another_file`: NTFS nay "không dùng được" thay vì lấy file NFC của kết quả quét (file khác tên). Đổi hành vi có chủ đích; nháp do app lưu luôn ghi đúng tên trên ổ, chỉ gặp khi nháp bị sửa tay. Thêm test hai thư mục NFC/NFD cùng có.
  - `test_unconfirmed_folder_name_is_unavailable`: ca `quet-chua-toi` đổi tên thành `khong-con`; giả `FakeDisk` cũ không có `truncated`, nên ca cũ cũng là "danh sách xem hết, không có tên": cùng điều kiện, thêm kiểm câu "mở lại từ thư mục ảnh gốc". Ca "danh sách bị cắt" chuyển sang test mới (nay dùng được, LC-T055-3).
  - `test_exact_folder_name_wins_on_case_sensitive_disk` thêm ca bị cắt; `test_single_case_insensitive_match_takes_real_name` thêm kiểm `stat_image` được gọi lại ở tên mới.
- **Một test cũ của Soi Lỗi T-055 nay kiểm yếu hơn ý của nó (không do sửa test):** `test_sl_t055_4_folder_swapped_during_check_on_real_disk` so `stat_image(result.ref).size == result.entry.size`. Từ T-076 `entry` lấy theo lần kiểm lại, nên câu này luôn đúng kể cả khi ảnh đã đổi sang file khác (đột biến M4: test này vẫn qua). Tôi không sửa test cũ; thêm `test_folder_swapped_during_check_does_not_switch_to_another_file` so **định danh** file (M4 làm test này hỏng).

### Việc 4 · Tìm lỗi mới

#### SL-T076-1 · Thấp · Lớp phòng thứ hai nhận bản sao cùng cỡ, cùng giờ sửa là "cùng ảnh"

- **Tái hiện** (`test_sl_t076_1_swapped_copy_with_same_size_and_time_is_not_used`, ổ thật Windows): nháp (nguồn "that", alt đã duyệt) ghi `CT012 - Cổng inox - Tân Phú/CongAI/cong.png`. Cùng thư mục công trình có `Khac/cong.png` là **bản sao** của ảnh đó (cùng nội dung, cùng giờ sửa: File Explorer giữ giờ sửa khi chép). Giữa lúc `stat_image` và lúc lớp phòng thứ hai xem danh sách thư mục công trình, `CongAI` bị đổi tên thành `CongAI cu`, `Khac` đổi thành `Congai`.
- **Mong đợi:** ảnh không dùng được (thư mục vừa đổi), hoặc đúng file đã chọn và vẫn là ảnh AI (việc 1 của lời giao: "không lẫn sang file khác").
- **Thực tế:** `available=True`, `ref` là `…/Congai/cong.png` (file khác: số định danh khác), thẻ `source='that'`, mã CT012, alt không có «Minh họa» vẫn "đã duyệt" (trái điều kiện Lá Chắn T-052 số 3).
- **Nguyên nhân:** `drafts.py:926-933`: danh sách thư mục thấy đúng một tên trùng không phân biệt hoa thường (`Congai`), `stat_image` lại ở đó và chỉ so `(size, modified)`. Cỡ và giờ sửa không phải định danh file. Trên Windows (đã thử cả ổ chia sẻ SMB của Windows) và theo cách của Mac/Linux, `stat_image` **đã** trả tên trên ổ, nên danh sách chỉ nói khác khi thư mục vừa bị đổi giữa hai lần gọi: lúc đó "đổi sang tên của danh sách" chỉ thêm rủi ro.
- **Điều kiện xảy ra:** đổi tên đúng khe vài mili giây khi app đang kiểm nháp (người dùng hay Drive đồng bộ), có bản sao cùng cỡ cùng giờ sửa ở thư mục khác, nháp ghi "that" cho ảnh trong thư mục AI (sửa tay, hay chọn trước khi đổi tên thư mục). Không đọc ra ngoài thư mục ảnh (F1 giữ). Nên **Thấp**.
- **Hướng sửa** (chọn một):
  - (a) Bỏ đổi tên ở lớp phòng thứ hai: danh sách xem hết mà không có đúng tên `stat_image` trả thì không dùng được (`_MSG_FOLDER_NAME`); bị cắt thì giữ như nay. Tôi thử trên bản sao (thư mục nháp): SL-T076-1 thành `XPASS(strict)`; 2 test dùng ổ giả "trả lại đúng chữ đã gõ" phải đổi theo (`test_single_case_insensitive_match_takes_real_name`, `test_mac_nfd_folder_names_keep_ai_and_real_tags`): ở ổ đó ảnh khác hoa thường sẽ "không dùng được" thay vì đổi tên (hướng an toàn, người dùng chọn lại từ thư mục gốc). Các test khác của `test_drafts_images.py`, `test_soi_loi_t055.py`, `test_soi_loi_t076.py` qua (361 qua).
  - (b) Giữ cách đổi tên nhưng so **định danh** file (`st_dev`, `st_ino`) thay cho cỡ và giờ sửa, ví dụ một hàm riêng của `ImageLibrary` so hai `ImageRef` (đường dẫn tuyệt đối không ra khỏi module). Ổ không có số định danh (`st_ino = 0`) thì không dùng được.

### Đã thử, không có lỗi

- **Ổ SMB (`\\localhost\C$`) trên máy này:** `resolve` của `…\ct012 - cổng INOX - tân phú\congai\cong.png` ra `…\CT012 - Cổng inox - Tân Phú\CongAI\Cong.PNG`; `stat_image`, `list_folder` trả tên trên ổ ở cả hai cách. Rủi ro "ổ trả lại đúng chữ đã gõ" (báo cáo Thợ Máy) **không** xảy ra với ổ chia sẻ của Windows; ổ NAS chạy Samba, Google Drive for Desktop trên Windows chưa thử được (không đụng Drive thật của chủ dự án).
- **Ổ thật phân biệt hoa thường có cả `CongAI` lẫn `congai`** (Windows: `fsutil file setCaseSensitiveInfo` cho thư mục tạm, không cần quyền quản trị; Linux sẵn có; Mac APFS mặc định bỏ qua): `stat_image`, `list_folder` (một tầng, đệ quy) trả đúng thư mục đã gõ, đúng cỡ, đọc đúng byte; `CONGAI`, `Congai` không tìm thấy; nháp `CongAI` là ảnh AI, nháp `congai` là ảnh thật CT012 giữ alt đã duyệt, cả khi danh sách bị cắt và khi `scanned` là kết quả quét của thư mục kia (`test_case_sensitive_disk_*`, 6 ca).
- **Tên chỉ khác dấu tiếng Việt** (`Tan Phu`/`Tân Phú`, `Da Nang`/`Đà Nẵng`, `Cong so 1`/`Cổng số 1` cùng nằm một chỗ): gõ hoa, thường, đảo hoa thường ra đúng thư mục cùng dấu, không bao giờ sang thư mục kia (6 ca). `_match_disk_name` với nhiều tên cùng khóa: trùng hẳn luôn thắng dù đứng trước hay sau; không trùng hẳn thì từ chối.
- **Thư mục bị xóa ngay sau khi kiểm đường đi** (trước khi lấy tên): `stat_image`, `list_folder`, gõ đúng và gõ khác hoa thường, cả hai cách: lỗi gọn ("vừa bị thay đổi" hoặc "không tìm thấy"), không sập (8 ca).
- **Kết quả quét cũ** (quét lúc thư mục còn tên `Congai`, sau đó đổi thành `CongAI`): ảnh là ảnh AI theo tên mới, `scanned` không quyết thẻ (2 ca).
- **Thư mục sâu:** 20 tầng gõ chữ thường ở mọi tầng: ra đúng tên trên ổ ở mọi tầng (2 ca). Đường 151 tầng (gõ đúng tên): chạy được ở cả hai cách, dưới 1 giây (script).

### Hiệu năng

Script `exp_perf.py` (thư mục nháp): gốc 200 thư mục công trình, một thư mục 3.000 ảnh, 300 thư mục mỗi thư mục một ảnh, một đường 151 tầng. Lấy lần nhanh nhất trong 3 lần (nháp 300 ảnh: 2 lần); "Mac" là cách xem thư mục cha chạy trên Windows (mở theo đường dẫn, không phải theo `fd` như trên Mac thật). Code `main` dựng từ `d9e279f` bằng `git archive`. Máy đang chạy agent khác nên số dao động; ổ SMB chạy 2 lượt, ghi khoảng.

| Việc (giây) | `main` cục bộ | T-076 Windows cục bộ | T-076 cách Mac cục bộ | `main` SMB | T-076 Windows SMB | T-076 cách Mac SMB |
|---|---|---|---|---|---|---|
| 48 lần `stat_image` trong thư mục 3.000 ảnh, tên đúng | 0,27 | 0,23 | 0,32 | 0,77–0,94 | 0,89–1,32 | 1,91–2,49 |
| như trên, nháp gõ khác hoa thường | 0,28 | 0,26 | 0,64 | 0,90–1,56 | 1,11–1,17 | 2,68–3,66 |
| `list_folder` thư mục 3.000 ảnh | 0,59 | 0,36 | 0,30 | 0,24–0,28 | 0,26–0,29 | 0,23–0,33 |
| `stat_image` sâu 151 tầng | 0,12 | 0,12 | 0,69 | 0,37–0,57 | 0,47–0,48 | 0,69–0,87 |
| `check_draft_images` 300 ảnh / 300 thư mục | 7,4 | 3,1 | 8,4 | 12,1–12,5 | 11,0–13,6 | 14,9–24,0 |

- **Windows:** không chậm hơn `main` (tên lấy từ `resolve`, chỉ thêm một lần `lstat`).
- **Mac (suy từ số trên, chưa đo trên Mac thật):** mỗi lần `stat_image` đọc tên của mọi thư mục trên đường đi, kể cả thư mục chứa ảnh, tới khi gặp tên trùng hẳn; nháp gõ khác hoa thường thì đọc hết. Trước T-076, kiểm nháp không đọc thư mục chứa ảnh, và mỗi thư mục cha chỉ đọc một lần cho cả nháp. Ổ mạng chậm hơn khoảng 2–3 lần ở `stat_image` (xem trước 48 ảnh khoảng 2 giây), kiểm nháp chậm hơn khoảng 20–100%. Ổ cục bộ gần như không khác. Thêm: trên Mac `list_folder` có thể mất tới 2 × `max_seconds` (10 giây lấy tên các thư mục cha, rồi 10 giây quét); đường rất sâu mở lại từ gốc ở mỗi tầng (số lần mở tăng theo bình phương số tầng; 151 tầng vẫn dưới 1 giây ở đây). Tôi không xếp thành lỗi vì phiếu không đặt giới hạn tốc độ và ổ cục bộ không khác; ghi để T-063 đo trên Mac với thư mục Drive thật.

## Đối chiếu tiêu chí (lời giao)

- [x] Việc 1: yêu cầu 1–4 làm thật (bảng "Việc 1"), trừ SL-T076-1 (Thấp)
- [x] Việc 2: lớp chặn T-048 giữ; test T-048 và `xfail` cũ chạy lại, không đổi
- [x] Việc 3: `test_soi_loi_t055.py` chỉ gỡ 3 khối `xfail`; test cũ trong `test_drafts_images.py`, `test_images_folders.py` không bị làm yếu (một test cũ của T-055 yếu đi do đổi nghĩa `entry`, đã bù bằng test mới)
- [x] Việc 4: thư mục sâu, nhiều mục, ổ chậm, xóa giữa chừng, tên chỉ khác dấu, hai thư mục chỉ khác hoa thường trên ổ phân biệt hoa thường
- [x] Việc 5: lỗi mới có test `xfail(strict=True)` kèm mã SL-T076-1 trong `tests/test_soi_loi_t076.py`; không sửa code ứng dụng
- [x] Test liên quan qua, `ruff check .` sạch

## Rủi ro và điểm cần chú ý

- **Phần mở thư mục bằng `fd` của `_listed_names` chưa chạy trên máy nào** (chỉ có trên Mac/Linux; trên Windows test chạy cách Mac bằng đường dẫn). T-063 cần chạy `tests/test_images_folders.py`, `tests/test_soi_loi_t076.py` trên Mac (có ca symlink thật, NFD thật; ca ổ phân biệt hoa thường sẽ bỏ qua trên APFS mặc định).
- **Ổ trả lại đúng chữ đã gõ khi `resolve`:** ổ chia sẻ Windows thì không (đã thử). Ổ NAS Samba, Google Drive for Desktop trên Windows, ổ ảo (WinFsp, Dokan) chưa thử. Trên ổ như vậy, nháp vẫn được lớp phòng thứ hai bắt trừ khi thư mục cha bị cắt; còn `list_folder` theo đường dẫn gõ tay thì trả chữ đã gõ. Nếu sửa SL-T076-1 theo cách (a) thì trên ổ đó ảnh nháp khác hoa thường thành "không dùng được" (hướng an toàn).
- `tests/test_soi_loi_t076.py` gọi `fsutil` (công cụ có sẵn của Windows) để bật phân biệt hoa thường cho **thư mục tạm của test**; không bật được thì test bỏ qua. Không đổi cài đặt hệ thống.
- Ảnh **không dùng được** vẫn có thẻ đọc theo chữ trong nháp (đã ghi ở T-055; T-056 điều kiện 2b).

## Đề xuất

- **Thợ Máy (phiếu dọn, hay trước T-056):** sửa SL-T076-1 theo cách (a) hoặc (b), gỡ `xfail` khi `XPASS`. Cách (a) đơn giản hơn và hợp với việc `stat_image` nay đã trả tên trên ổ.
- **T-063 (Mac):** chạy thêm `tests/test_soi_loi_t076.py`; đo xem trước 48 ảnh trong thư mục Drive 3.000 ảnh và kiểm một nháp nhiều ảnh trong cùng thư mục. Nếu chậm: trên Mac lấy tên của một mục bằng `getattrlist` (`ATTR_CMN_NAME`) hay `fcntl(F_GETPATH)` thay vì đọc cả thư mục cha, hoặc nhớ tên đã xác nhận trong một lần kiểm nháp.
- **T-056:** giữ khuyến nghị của Lá Chắn T-055 (đi từ thư mục gốc; kiểm ảnh nháp một lần khi mở nháp, không gọi lại mỗi lần Streamlit chạy lại; lưu lại theo `checked.ref`).

## Kết luận

- **ĐẠT CÓ ĐIỀU KIỆN.** Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T076-1).
- **Chuyển Lá Chắn được** (rút gọn, F1). Điều kiện: Chỉ Huy quyết SL-T076-1 (sửa trong phiếu này hay phiếu dọn trước T-056); T-063 chạy phần Mac và đo tốc độ.

## Câu hỏi cho chủ dự án

Không có.

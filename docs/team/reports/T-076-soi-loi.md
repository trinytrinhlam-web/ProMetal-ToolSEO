# Báo cáo T-076 · Thư mục ảnh trả tên theo tên trên ổ · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-076](../tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (kiểm đầy đủ). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn (rút gọn, F1) được |
| Lượt 2 | 2026-10-22, rút gọn: **ĐẠT CÓ ĐIỀU KIỆN** (SL-T076-1 đã sửa; 1 Thấp mới SL-T076-2), chuyển Lá Chắn được. Xem mục "Lượt 2" cuối báo cáo |

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

---

## Lượt 2 (2026-10-22, rút gọn): LC-T076-1, LC-T076-2

| Mục | Nội dung |
|---|---|
| Lời giao | Chỉ Huy B (chủ dự án đã duyệt), kiểm rút gọn sau Thợ Máy lượt 2 |
| Nhánh | `team/T-076`, đầu nhánh lúc kiểm `006b13b` (code lượt 2: `3930e94` LC-T076-1, `491609b` LC-T076-2) |
| Đã đọc | Biên bản Lá Chắn `docs/team/reports/T-076-la-chan.md`, báo cáo Thợ Máy mục "Lượt 2", ghi chú cuối phiếu (trên `origin/main` `400fa8c`) |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (SL-T076-2). SL-T076-1 đã sửa. **Chuyển Lá Chắn (rút gọn, F1) được** |

### Tóm tắt (cho chủ dự án)

Lá Chắn thấy ổ Google Drive trên máy Windows trả lại đúng chữ đã gõ khi app hỏi "tên thật của thư mục". Nay app hỏi tên ngay ở **thư mục chứa nó**. Tôi thử lại trên ổ thường thật và trên ổ giả lập đúng kiểu Google Drive: nháp ghi `congai`, trên ổ là `CongAI`, thì ảnh **luôn là ảnh AI**, câu mô tả có «Minh họa» và phải duyệt lại. Khi app không hỏi được (thư mục vừa bị xóa, hay không có quyền xem thư mục chứa nó; tôi thử thật bằng cách bỏ quyền trên một thư mục tạm) thì app báo lỗi gọn, ảnh "không dùng được", không đoán theo chữ trong nháp.

Lỗi nhỏ tôi ghi ở lượt 1 (SL-T076-1, bản sao y hệt được dùng thay ảnh AI khi thư mục bị đổi tên đúng lúc) **đã hết** với kiểu đổi tên một lần. Nhưng còn một khe hẹp hơn (**SL-T076-2, Thấp**): nếu thư mục bị đổi tên đi **rồi đổi lại** đúng trong vài phần nghìn giây app đang kiểm, app vẫn có thể dùng bản sao như ảnh thật. Rất khó xảy ra, không đọc được gì ngoài thư mục ảnh. Cách sửa tôi đề xuất ở lượt 1 (cách (a)) đóng hẳn khe này; đổi lại phải sửa 3 test cũ cho khớp (1 của tôi, 2 của Thợ Máy): hai test giả một kiểu ổ mà từ lượt 2 app không còn gặp, một test đếm đúng bước "hỏi lại" của cách hiện nay.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t076.py` | `name_source` thêm kiểu "`resolve` trả chữ đã gõ" (như `typed_resolve` của Lá Chắn), nên mọi test tên trên ổ của tôi chạy thêm kiểu này (21 ca). Thêm 2 hàm test chỉ chạy trên Windows (mục vừa mất giữa hai tầng hỏi: 4 ca; ổ trả tên khác khóa: 3 ca), 1 hàm giữ câu so tên ở lần hỏi tên mới của lớp phòng thứ hai (`test_copy_under_a_third_spelling_at_last_check_is_not_used`, đột biến M10 bên dưới) và 2 hàm `xfail(strict=True)` SL-T076-2. Docstring đầu file, docstring SL-T076-1 (ghi đã sửa). Không đổi `assert` của test cũ. Tổng 18 hàm, 77 ca (75 qua, 2 `xfail`) |
| `docs/team/reports/T-076-soi-loi.md` | Mục này |

Không sửa code ứng dụng, không sửa test của người khác.

### Bằng chứng (lượt 2)

Máy Windows 11 Pro của chủ dự án, Python 3.12.15, worktree `wt-T-076`, nhánh `team/T-076` tại `006b13b` (code không đổi). Máy chạy song song agent khác (số giây chỉ để tham khảo).

```
$ uv run pytest tests/test_images_folders.py tests/test_drafts_images.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_storage_drafts.py \
    tests/test_images_tags.py tests/test_app_pages.py tests/test_images_folders_soi_loi.py \
    tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t067.py \
    -q -p no:cacheprovider -rsxX
(2026-10-22 09:16–09:26 +07, trước khi sửa file của tôi)
1503 passed, 9 skipped, 7 xfailed in 581.17s (0:09:41)

$ <cùng lệnh, có file của tôi>
(2026-10-22 09:36–09:38 +07)
1532 passed, 9 skipped, 9 xfailed in 137.75s (0:02:17)

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t076.py
1 file already formatted

$ PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # thư mục nháp chứa bản chép file test và báo cáo
"results": {}   (file mồi có chữ tiếng Việt: có PYTHONUTF8 bắt 2/2, không có thì 0; đã xóa)
```

- 8 file của lời giao lượt 2, thêm 4 file như lượt 1 (test Soi Lỗi T-048 và các file gọi `stat_image`/`list_folder`). Lượt đầu khớp số của Thợ Máy (1.503 qua, 9 bỏ qua, 7 `xfail`). 9 bỏ qua đều do máy Windows; 7 `xfail` có từ trước, không thuộc phiếu (R2-1 ×2, R2-2 của T-048; SL-T067-1 ×4). Không còn `xfail` nào của LC-T076-1 hay SL-T076-1.
- Lượt cuối: 1.503 + 29 ca qua mới của tôi (file của tôi từ 46 ca lên 77 ca: 75 qua, 2 `xfail`) = 1.532 qua; 9 `xfail` = 7 có từ trước + 2 ca SL-T076-2. 0 hỏng.

### Việc 1 · LC-T076-1: Windows lấy tên ở thư mục cha (`FindFirstFileW`)

| Điều cần xác nhận | Kết quả | Bằng chứng |
|---|---|---|
| Không còn lấy tên từ `resolve` | **ĐẠT** | `_disk_names` (`folders.py:580-614`) gọi `_found_names` (Windows, `:616-627`: mỗi tầng hỏi thư mục cha đúng một mục bằng `_win_listed_name`, `:327-345`) hoặc `_listed_names` (Mac/Linux); bỏ tham số `resolved`. Chú thích `_NAMES_FROM_RESOLVE` (`:71-76`) và các docstring nói đúng cách mới |
| Ổ giả "`resolve` trả chữ đã gõ" (như `typed_resolve` của Lá Chắn): nháp `…/congai/cong.png`, trên ổ `CongAI` → ảnh AI, «Minh họa», bỏ "đã duyệt" | **ĐẠT** | `test_lc_t055_1_draft_case_variant_stays_ai_both_name_sources[resolve-tra-chu-da-go-*]` (4 ca: không quét, `list_folder` theo thư mục ghi trong nháp một tầng và đệ quy từ thư mục công trình gõ khác hoa thường, `ImageRef` dựng từ chữ trong nháp). 6 ca của Lá Chắn (B, D, E, F: quét theo nháp, danh sách thư mục cha bị cắt, chọn lại ảnh) nay qua, đã gỡ `xfail`. Mọi test tên trên ổ khác của tôi (ổ phân biệt hoa thường, tên chỉ khác dấu, 3 kiểu chữ "ệ", xóa, tráo liên kết, kết quả quét cũ, sâu 20 tầng) cũng chạy kiểu này: qua |
| Ổ NTFS thật | **ĐẠT** | Cùng các test ở kiểu "hệ điều hành" (`resolve` thật). Script thử lại trên ổ thật: thư mục bật phân biệt hoa thường có cả `CongAI` lẫn `congai` (`fsutil`): mỗi tên ra đúng chính nó, đúng cỡ; nháp `CongAI` ảnh AI, nháp `congai` ảnh thật, cả khi danh sách bị cắt. Ổ chia sẻ SMB (`\\localhost\C$`): `stat_image`, `list_folder` ra `…/CongAI/Cong.PNG` |
| Hỏi không được: mục vừa mất | **ĐẠT** | Mục bị xóa ngay sau khi kiểm đường đi: `test_folder_deleted_right_after_path_check` (12 ca, cả 3 kiểu). **Mới:** mục bị xóa **giữa hai tầng hỏi** (hỏi được thư mục công trình, rồi `CongAI` mất trước lần hỏi kế): "Không tìm thấy…", danh sách lần hỏi chỉ có tầng đầu, nháp "không dùng được", với `resolve` thật và `resolve` trả chữ đã gõ (`test_entry_vanishing_between_lookup_levels_is_not_found`, 4 ca) |
| Hỏi không được: không có quyền xem thư mục cha | **ĐẠT** (thử thật bằng script) | Script `exp_acl.py` (thư mục tạm): `icacls <thư mục công trình> /deny <người dùng>:(RD)` (bỏ quyền xem danh sách, chỉ thư mục đó), gỡ và xóa ngay sau khi thử. Kiểm đường đi (`_resolve_inside`) **vẫn qua** ở cả 3 kiểu, nên lỗi nằm đúng ở bước lấy tên: `stat_image` (tên đúng và gõ khác hoa thường), `list_folder` đều báo "Không đọc được mục này (không có quyền hoặc ổ đĩa vừa bị ngắt).", không có đường dẫn máy, không xích lỗi hệ điều hành; nháp "không dùng được". Không lần nào trả chữ đã gõ. Thợ Máy có test giả lỗi 5 của `FindFirstFileW` (`test_windows_lookup_failure_is_a_plain_message`) |
| Ổ trả một tên khác khóa (tên khác hẳn, dài hơn, kiểu 8.3) | **ĐẠT** | Không nhận tên ổ trả, không quay về chữ đã gõ: `stat_image`, `list_folder` báo lỗi gọn, nháp "không dùng được" (`test_lookup_answer_with_another_name_is_refused`, 3 ca, trên ổ `resolve` trả chữ đã gõ). Thợ Máy có test tên 8.3 thật (`test_short_8_3_name_refused_when_resolve_keeps_typed_text`) |
| Lớp chặn T-048, câu báo | **Giữ** | `_resolve_inside`, `_Scan`, `read_image_bytes` không đổi một dòng ở lượt 2 (`git diff a1a48da..006b13b -- seo_app/images/folders.py`); test T-048 (`tests/test_images_folders_soi_loi.py`) và `tests/test_soi_loi_t055.py` không đổi, qua. Tráo junction ra ngoài gốc đúng lúc lấy tên: `test_link_swapped_in_after_path_check` nay 12 ca (thêm kiểu `resolve` trả chữ đã gõ): lỗi gọn, không trả tên hay số liệu ngoài gốc |

### Việc 2 · LC-T076-2: cách "hỏi lại tên cũ" có cho cùng kết quả với cách (a) trên ổ thật không

**Với kiểu tráo một lần (SL-T076-1): có.** Test của tôi `test_sl_t076_1_swapped_copy_with_same_size_and_time_is_not_used` (ổ thật, bản sao cùng cỡ, cùng giờ sửa) nay qua: lần hỏi lại `CongAI/cong.png` ra `Congai/cong.png` (ổ không phân biệt hoa thường tìm ra thư mục mới), khác kết quả cũ, nên "không dùng được", thẻ ảnh AI. `test_folder_swapped_during_check_does_not_switch_to_another_file` (khác cỡ) cũng qua.

**Còn khe: SL-T076-2 (Thấp, mới).** Lần hỏi lại chỉ cho biết tên cũ **lúc hỏi lại**, không cho biết tên lúc xem danh sách. Nếu thư mục đổi tên đi lúc xem danh sách rồi đổi lại trước lần hỏi lại, thì hỏi lại ra đúng kết quả cũ, và lớp phòng thứ hai lại nhận ảnh ở tên của danh sách khi cùng cỡ, cùng giờ sửa. Cách (a) (danh sách nói khác thì không dùng được) không có khe này. Từ lượt 2, `ImageLibrary` thật luôn trả tên trên ổ (Windows hỏi thư mục cha, Mac/Linux đọc thư mục cha), nên nhánh "nhận tên của danh sách" chỉ còn chạy được khi thư mục bị đổi tên giữa các lần xem.

#### SL-T076-2 · Thấp · Thư mục đổi tên đi rồi đổi lại đúng lúc kiểm: vẫn nhận bản sao ở tên khác

- **Tái hiện** (ổ thật NTFS, đổi tên thật, chỉ canh thời điểm bằng `monkeypatch`):
  - `test_sl_t076_2_folder_renamed_away_and_back_still_switches_to_copy` (ổ không phân biệt hoa thường, mặc định của Windows và Mac): nháp (nguồn "that", alt đã duyệt) ghi `CT012 - Cổng inox - Tân Phú/CongAI/cong.png` (ảnh AI nhờ tách chữ hoa); thư mục `Khac` có bản sao `cong.png` cùng nội dung, cùng giờ sửa (File Explorer giữ giờ sửa khi chép). Ngay trước lúc lớp phòng thứ hai xem danh sách thư mục công trình: `CongAI` → `CongAI cu`, `Khac` → `Congai`; xem xong đổi lại như cũ; ngay sau lần hỏi lại tên cũ lại đổi như lần đầu.
  - `test_sl_t076_2_case_sensitive_disk_one_rename_away_and_back` (ổ phân biệt hoa thường thật, `fsutil`): có sẵn `CongAI/cong.png` và bản sao `congai/cong.png`. Chỉ cần `CongAI` vắng mặt đúng lúc xem danh sách (đổi tên đi, xem xong đổi lại).
- **Mong đợi:** không dùng được, hoặc đúng file đã chọn và vẫn là ảnh AI (việc 1 lượt 1: "đổi tên đúng lúc kiểm → báo không dùng được, không lẫn sang file khác").
- **Thực tế** (script `exp_sl2.py` in đủ kết quả ca thứ nhất): ba lần `stat_image`: `CongAI/cong.png` ra `CongAI/cong.png`; hỏi lại `CongAI/cong.png` ra `CongAI/cong.png` (giống hệt); `Congai/cong.png` ra `Congai/cong.png`. Ảnh **dùng được**, `ref` là `…/Congai/cong.png` (bản sao, số định danh khác file đã chọn), thẻ `that` / CT012 / Tân Phú, alt «Bản lề cổng inox bị gỉ trước khi sửa» không «Minh họa», **vẫn "đã duyệt"**. Ca thứ hai cũng dùng bản sao. `--runxfail`: cả hai hỏng đúng ở câu so định danh file.
- **Nguyên nhân:** `drafts.py:938-944`: hỏi lại tên cũ rồi `stat_image` ở tên của danh sách, so tên và (cỡ, giờ sửa); không lần nào so định danh file, và các lần hỏi ở những thời điểm khác nhau.
- **Điều kiện xảy ra:** đổi tên đi và đổi lại trong khe vài mili giây giữa các lần hỏi (ổ không phân biệt hoa thường: đổi 3 lần, có bản sao ở thư mục khác; ổ phân biệt hoa thường: đổi đi rồi đổi lại, có bản sao ở thư mục chỉ khác hoa thường), nháp ghi "that" cho ảnh trong thư mục AI (sửa tay, hay chọn trước khi đổi tên). Hẹp hơn SL-T076-1. Không đọc ra ngoài thư mục ảnh (F1 giữ: mọi lần hỏi qua đủ lớp chặn, đọc sau qua `read_image_bytes`). Nên **Thấp**.
- **Hướng sửa:**
  - (a) Như lượt 1: danh sách xem hết mà không có đúng tên `stat_image` trả thì không dùng được (`_MSG_FOLDER_NAME`); bỏ nhánh nhận tên của danh sách. Thử trên bản sao code lượt 2 (thư mục nháp): 2 ca SL-T076-2 thành `XPASS(strict)`; 3 test phải đổi theo: `test_single_case_insensitive_match_takes_real_name`, `test_lc_t076_2_folder_renamed_between_checks_is_unavailable` (của Thợ Máy; test sau chỉ hỏng ở câu đếm lần gọi `stat_image`, kết quả vẫn "không dùng được") và `test_mac_nfd_folder_names_keep_ai_and_real_tags` (Soi Lỗi T-055). Ba test này dùng ổ giả mà `stat_image` trả lại chữ đã gõ; từ lượt 2 `ImageLibrary` thật không còn kiểu đó. Nếu Chỉ Huy chọn (a), Soi Lỗi nhận sửa test T-055 của mình theo nghĩa mới (giả ổ Mac mà `stat_image` trả tên NFD, hoặc đòi "không dùng được").
  - (b) Giữ cách hiện tại nhưng so **định danh** file (`st_dev`, `st_ino`) của ảnh ở tên mới với ảnh đã kiểm (cần một hàm riêng của `ImageLibrary`, đường dẫn tuyệt đối không ra khỏi module).
  - Hoặc chủ dự án chấp nhận rủi ro (ghi sổ rủi ro), vì rất hẹp.

### Việc 3 · Soát test (`git diff a1a48da..team/T-076 -- tests/`)

- `tests/test_soi_loi_t076.py`: `0 thêm, 4 xóa`, đúng khối `@pytest.mark.xfail(strict=True, reason="SL-T076-1…")`.
- `tests/test_la_chan_t076.py` (so với bản của Lá Chắn `ca1e91d`): `0 thêm, 12 xóa`: hằng `XFAIL` (7 dòng) và 5 dòng `@XFAIL`. Không đổi `assert`, dữ liệu thử, `typed_resolve`.
- `tests/test_drafts_images.py`: `31 thêm, 3 xóa`. `test_single_case_insensitive_match_takes_real_name` **không bị làm yếu**: giữ mọi câu kiểm cũ (dùng được, `ref` và `entry.ref` là `CongAI/cong.png`, ảnh AI), danh sách lần gọi `stat_image` thêm đúng lần hỏi lại tên cũ (`["congai/cong.png", "congai/cong.png", "CongAI/cong.png"]`), tức kiểm thêm bước mới; 2 dòng còn lại là docstring. Thêm `test_lc_t076_2_folder_renamed_between_checks_is_unavailable`.
- `tests/test_images_folders.py`: `95 thêm, 5 xóa`: 5 dòng xóa là chú thích mục, dòng `@pytest.fixture(params=[...])` (nay thêm kiểu thứ ba) và 2 dòng docstring; không xóa câu kiểm nào. Thêm `typed_resolve`, 3 test chỉ chạy trên Windows.
- `tests/test_soi_loi_t055.py`, `tests/test_images_folders_soi_loi.py`: không đổi.

### Thử đột biến (lượt 2)

Chép `seo_app` sang thư mục nháp, sửa một chỗ, chạy 5 file `tests/test_soi_loi_t076.py`, `tests/test_la_chan_t076.py`, `tests/test_images_folders.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py` với `PYTHONPATH` trỏ vào bản sửa (đã kiểm `seo_app` nạp từ bản sửa). Script `mutate2.py` ở thư mục nháp, không commit.

| Đột biến | Test hỏng |
|---|---|
| M6 · Windows lấy tên theo chữ đã gõ (như lượt 1 trên ổ Drive): `_found_names` trả nguyên phần đã gõ | 42 (Soi Lỗi T-076 20, Lá Chắn T-076 7, Thợ Máy thư mục ảnh 8, nháp 7) |
| M7 · Nhận tên ổ trả về mà không so khóa với tên đã gõ | 1 (`test_short_8_3_name_refused_when_resolve_keeps_typed_text` của Thợ Máy). Tên khác hẳn thì bước so định danh cuối (`lstat` ở tên mới) vẫn chặn, nên test "tên khác khóa" của tôi không phân biệt được đột biến này; chỉ tên 8.3 (cùng mục) mới lọt |
| M8 · Hỏi lỗi thì quay về chữ đã gõ | 7 (Soi Lỗi 4: mục vừa mất giữa hai tầng hỏi; Thợ Máy 3: lỗi 2, 3, 5 của `FindFirstFileW`) |
| M9 · Bỏ bước hỏi lại tên cũ | 4 (Soi Lỗi 2: SL-T076-1 hỏng, 1 ca SL-T076-2 thành `XPASS`; Thợ Máy 2) |
| M10 · Bỏ câu so tên ở lần hỏi tên mới (`again.ref != real`) | **0** lúc đầu. Thêm `test_copy_under_a_third_spelling_at_last_check_is_not_used` (bản sao mang tên thứ ba `CONGAI` đúng lúc hỏi tên mới): nay **1** (chạy riêng file của tôi) |

Số M6–M9 đếm trước khi thêm test M10. Test M10 không đổi kết quả với code đúng và vẫn qua với cách (a).

### Đo thời gian (lượt 2)

Script `exp_perf.py` của lượt 1 (gốc 200 thư mục công trình, một thư mục 3.000 ảnh, 300 thư mục mỗi thư mục một ảnh, đường 151 tầng), lấy lần nhanh nhất trong 3 lần (nháp 300 ảnh: 2 lần), cách của Windows. `main` = `d9e279f`, lượt 1 = `a1a48da` (tên từ `resolve`), lượt 2 = `006b13b` (`FindFirstFileW` từng tầng), dựng bằng `git archive`. Mỗi cột một lượt đo, máy đang chạy agent khác nên số dao động.

| Việc (giây) | `main` cục bộ | lượt 1 cục bộ | lượt 2 cục bộ | `main` SMB | lượt 1 SMB | lượt 2 SMB |
|---|---|---|---|---|---|---|
| 48 lần `stat_image` trong thư mục 3.000 ảnh, tên đúng | 0,090 | 0,092 | 0,153 | 0,603 | 1,198 | 0,791 |
| như trên, nháp gõ khác hoa thường | 0,072 | 0,088 | 0,183 | 0,673 | 0,840 | 0,864 |
| `list_folder` thư mục 3.000 ảnh | 0,177 | 0,195 | 0,267 | 0,235 | 0,246 | 0,262 |
| `stat_image` sâu 151 tầng | 0,050 | 0,047 | 0,135 | 0,370 | 0,510 | 0,708 |
| `check_draft_images` 300 ảnh / 300 thư mục | 1,23 | 1,54 | 1,89 | 8,47 | 12,0 | 13,0 |

Mỗi tầng của đường dẫn thêm một lần hỏi ổ, nên lượt 2 chậm hơn `main` một chút: 48 ảnh xem trước thêm khoảng 0,06 giây trên ổ cục bộ, khoảng 0,2 giây trên ổ SMB; kiểm nháp 300 ảnh chậm hơn khoảng 50%; đường rất sâu chậm hơn rõ (151 tầng: 2–3 lần). Không phụ thuộc số ảnh trong thư mục (không đọc cả thư mục). Không xếp thành lỗi; trên ổ Google Drive chưa đo được (không đụng Drive thật của chủ dự án). T-056 vẫn nên kiểm ảnh nháp một lần khi mở nháp.

### Rủi ro và điểm cần chú ý (lượt 2)

- **Ổ ảo trả lại chữ của truy vấn khi `FindFirstFileW`:** ổ NTFS, ổ chia sẻ Windows (đã thử) và Google Drive for Desktop (Lá Chắn đo) trả tên đã lưu. Một ổ ảo tự viết (WinFsp, Dokan) về lý thuyết có thể trả lại chữ của truy vấn; khi đó lớp phòng thứ hai của nháp vẫn đối chiếu với danh sách thư mục, trừ khi danh sách thư mục cha bị cắt (Thợ Máy đã ghi). Chưa có ổ như vậy để thử.
- **Đổi hành vi có chủ đích:** người dùng không có quyền xem danh sách một thư mục trên đường đi (vẫn mở được thư mục con) thì ảnh nay "không dùng được"; trước lượt 2 (tên từ `resolve`) vẫn dùng được. Hiếm với thư mục ảnh cá nhân; đúng ý lời giao ("hỏi không được thì báo lỗi gọn").
- **Phép chặn tên 8.3 của `read_image_bytes`** vẫn dựa vào `resolve` (`_resolve_inside`), nên trên ổ vừa trả lại chữ đã gõ khi `resolve` **vừa** có tên 8.3, `read_image_bytes` đọc được file qua tên ngắn, còn `stat_image`, `list_folder` nay từ chối. Đã thử bằng script `exp_83.py` (ổ NTFS có tên 8.3, `resolve` giả trả chữ đã gõ): `read_image_bytes(ImageRef(0, "THUMUC~1/ANHRAT~1.JPG"))` đọc được, `stat_image` báo "Không tìm thấy…"; với `resolve` thật cả hai từ chối. Vẫn là cùng một file trong thư mục ảnh (F1 giữ). Chưa thấy ổ thật nào có cả hai điều kiện (Google Drive không có tên 8.3, theo Lá Chắn; ổ chia sẻ Windows trả tên trên ổ khi `resolve`), và ảnh của nháp, ảnh xem trước (`PreviewCache.get`) đều đi qua `stat_image` trước khi đọc. Lá Chắn đã ghi nhận; tôi cũng chỉ ghi nhận, không thành lỗi. Nếu muốn khép hẳn: `_checked_file` gọi luôn bước lấy tên trên ổ.
- Hằng `_NAMES_FROM_RESOLVE` nay sai nghĩa với tên (Thợ Máy giữ vì test của tôi đặt nó). Khi đổi tên hằng, Soi Lỗi sửa theo trong `tests/test_soi_loi_t076.py`.
- Phần mở thư mục bằng `fd` của Mac/Linux vẫn chưa chạy trên máy nào (từ 2026-10-22 chủ dự án chưa có máy Mac; T-063 chạy bằng máy cloud Linux khi chủ dự án đồng ý).

### Kết luận lượt 2

- **ĐẠT CÓ ĐIỀU KIỆN.** LC-T076-1 sửa đúng (ổ giả "`resolve` trả chữ đã gõ", ổ NTFS thật, ổ SMB, ổ phân biệt hoa thường thật; hỏi không được thì báo lỗi gọn, không quay về chữ đã gõ, kể cả thiếu quyền thật). SL-T076-1 đã sửa. Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T076-2).
- **Chuyển Lá Chắn được** (rút gọn, F1). Điều kiện: Chỉ Huy quyết SL-T076-2: sửa theo cách (a) (Soi Lỗi sửa test T-055 của mình theo), cách (b), hay chủ dự án ghi sổ rủi ro. Không bắt buộc trước T-056 về bảo mật (Thấp, F1 giữ), nhưng sửa rẻ nếu chọn (a).

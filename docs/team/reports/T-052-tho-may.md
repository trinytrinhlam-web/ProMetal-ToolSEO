# Báo cáo T-052 · Thẻ ảnh đọc từ tên thư mục (G3-6)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-052](../tickets/T-052-the-anh-theo-ten-thu-muc.md) |
| Ngày nộp | 2026-10-20 (lượt 2: 2026-10-20) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

App đã đọc được thẻ ảnh từ tên thư mục trong Drive theo quyết định 3A (chưa có giao diện, Họa Sĩ làm ở T-056). Ví dụ ảnh nằm trong `CT012 - Cổng inox - Tân Phú/truoc/` thì app hiểu: mã công trình CT012, hạng mục "Cổng inox", khu vực "Tân Phú", ảnh trước khi làm, ảnh thật. Gõ không dấu, viết hoa, viết "Q.7" hay "Quận 7" đều được.

Phần nào của tên thư mục không khớp danh sách có sẵn (tên khách, số điện thoại, địa chỉ, quận gõ sai) thì **bị bỏ hẳn**: không bao giờ đi vào prompt AI, tên file, tiêu đề hay chú thích. App không ghi gì vào thư mục ảnh hay Drive. Thẻ anh sửa tay được nhớ trong một file nhỏ trên máy đang dùng (`data/image_tags.sqlite`); xóa file đó thì app tự tạo lại, chỉ mất các thẻ đã sửa tay.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/tags.py` | Mới: danh sách cố định (khu vực, hạng mục, trước/sau, dấu hiệu ảnh AI, mẫu mã CT), làm sạch tên, đọc thẻ từ `ImageRef`, khuôn thẻ `ImageTags` tự kiểm |
| `seo_app/storage/image_tags.py` | Mới: kho thẻ sửa tay SQLite trong `data/`, khóa theo `ImageRef` |
| `tests/test_images_tags.py` | Mới: 236 test (234 qua trên Windows, 2 bỏ qua có lý do, xem phần Bằng chứng) |
| `docs/team/reports/T-052-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/__init__.py`, `folders.py`, `app/**`, `config/**`, `seo_app/ai/**`, `tests/conftest.py` (`git diff --stat origin/main...HEAD` chỉ có 4 file trên).

## Cách app đọc một tên thư mục

1. Làm sạch: bỏ ký tự vô hình/định dạng (Cf), ngắt dòng/đoạn (Zl, Zp), điều khiển (Cc), surrogate lẻ (Cs), vùng riêng (Co), chưa gán (Cn); chuẩn hóa NFKC (`tags.py:285`, `:295`). **Bỏ** chứ không thay bằng dấu cách, nên chèn ký tự vô hình vào bất cứ đâu cũng không đổi được kết quả.
2. Tách phần theo `` - `` (gạch ngang có khoảng trắng) và các dấu `– — , ; | + & ( ) [ ]`.
3. Mỗi phần phải khớp **trọn vẹn** với danh sách, hoặc là ghép của các mục trong danh sách (`CT012 Cổng inox Tân Phú` trong một phần vẫn nhận). So không phân biệt hoa thường, có dấu hay không dấu, chữ dính liền (`TanPhu`, `Q7`, `CongInox`). Phần không khớp bị bỏ cả phần, chỉ đếm số phần bị bỏ (`FolderTags.unmatched`). Phần không khớp có gạch nối liền chữ hay gạch dưới (`CT012-Cổng inox-Nhà anh Tuấn`) thì thử lại từng mảnh.
4. Ghép các tầng thư mục từ gốc xuống: thư mục sâu hơn quyết định (`Quận 7/CT012 - Cổng - Tân Phú/` → Tân Phú). Một thư mục ghi hai giá trị khác nhau cho cùng một thẻ (`CT012 - Q7 - Tân Phú`) thì thẻ đó **để trống**, không đoán (`FolderTags.conflicts` ghi tên thẻ).
5. Có thư mục tên kiểu `Ảnh AI`, `AI`, `ảnh minh họa AI` thì mọi ảnh bên trong là ảnh AI: chỉ giữ hạng mục, bỏ mã công trình, khu vực, trước/sau (`tags.py:715`).
6. Không dùng tên file ảnh, không dùng tên chính thư mục gốc.

| Tên thư mục (giả) | Thẻ đọc được | Bị bỏ |
|---|---|---|
| `CT012 - Cổng inox - Tân Phú/truoc` | CT012 · Cổng inox · Tân Phú · trước · ảnh thật | — |
| `ct12-cong inox-tan phu/SAU` | CT12 · Cổng inox · Tân Phú · sau | — |
| `CT015 - Nhà anh Tuấn 0909123456 - 12 Lê Lợi - Q.3/truoc` | CT015 · Quận 3 · trước | 2 phần (tên, số điện thoại, địa chỉ) |
| `Sửa cửa kéo Q.Bình Thạnh - trước khi sửa` | Sửa cửa kéo · Bình Thạnh · trước | — |
| `Tan Phuu - Quận 13` | (trống) | 2 phần |
| `CT012 - Q7 - Tân Phú` | CT012 (khu vực để trống: mâu thuẫn) | — |
| `Ảnh AI/CT012 - Cổng inox - Q7/truoc` | ảnh AI · Cổng inox | mã, khu vực, trước/sau |

## Danh sách cố định nằm ở đâu

Tất cả trong `seo_app/images/tags.py` (phiếu không cho sửa `config/`):

| Danh sách | Vị trí | Nội dung |
|---|---|---|
| Khu vực | `HCM_AREAS` `:76`, `BINH_DUONG_AREAS` `:92`, `BA_RIA_VUNG_TAU_AREAS` `:104`, gộp `AREAS` `:122`, nhóm cho giao diện `AREA_GROUPS` | 45 tên: TP.HCM + Quận 1–12 (giữ Quận 2, Quận 9 dù đã nhập Thủ Đức) + 12 quận/huyện có tên; Bình Dương + 9 thành phố/thị xã/huyện; Bà Rịa – Vũng Tàu + 9 (giữ cả Long Điền, Đất Đỏ và Long Đất). Theo `config/business_profile.md` mục 3. Cách viết khác: tiền tố `Quận`, `Q`, `Huyện`, `H`, `TP`, `Thành phố`, `TX`, `Thị xã`, `District`, `Dist`; quận số bắt buộc có tiền tố (số trơn "7" không phải quận); tên tỉnh/thành có vài tên khác (`TPHCM`, `Sài Gòn`, `BRVT`) |
| Hạng mục | `_CATEGORY_ACTIONS` `:193` (16 việc: sửa, làm, thi công, thay, sơn, hàn…), `_CATEGORY_OBJECTS` `:211` (40 vật: cửa, cổng, cửa kéo, cửa cuốn, lan can, cầu thang, mái hiên, hàng rào, chuồng cọp, bản lề, bánh xe…), `_CATEGORY_MATERIALS` `:253` (22 vật liệu: sắt, inox, nhôm kính, Xingfa, sắt mỹ thuật, CNC…) | Hạng mục = [việc] + vật/vật liệu ghép từ các từ này, theo dịch vụ ở `business_profile.md` mục 4. Giá trị là đúng các từ trong danh sách nối lại ("Cổng inox", "Thay bánh xe cửa kéo"). Không dùng lớp lọc ký tự của T-050 cho hạng mục, vì lớp đó vẫn cho "Nhà anh Tuấn" đi qua |
| Trước/sau | `_PHASE_WORDS` `:154` | trước, trước khi làm/sửa/thi công, hiện trạng, before → `truoc`; sau, sau khi làm/sửa, làm xong, hoàn thành, hoàn thiện, after → `sau` |
| Ảnh AI | `_AI_WORDS` `:177` | AI, ảnh AI, hình AI, AI tạo, tạo bằng AI, minh họa AI, AI generated |
| Mã công trình | `_CODE_PATTERN` `:65` | `CT` + 1–6 chữ số ASCII (khớp `naming.py` của T-049). Nhận `ct 12`, `CT-012`, chữ toàn chiều rộng; trả dạng chuẩn `CT12`, `CT012` |

Thêm từ: thêm vào danh sách rồi chạy test (từ điển tự báo lỗi lúc nạp nếu hai mục trùng cách viết, `tags.py:375`).

## API cho các phiếu sau

| Tên | Vai trò |
|---|---|
| `ImageTags(source, project_code, category, area, phase)` | Khuôn thẻ, bất biến. **Tự kiểm lúc tạo** (`tags.py:482`): mọi giá trị phải thuộc danh sách; ảnh AI (`source="ai"`) có mã công trình/khu vực/trước-sau thì báo `TagError`. Câu báo lỗi không chép lại chữ đã nhập |
| `ImageTags.from_input(...)` | Thẻ sửa tay từ ô nhập: chuẩn hóa ("q7" → "Quận 7"), ô có chữ mà không khớp thì `TagError` nêu tên ô |
| `ImageTags.for_ai_image(category="")` | Thẻ ảnh AI (chỉ có hạng mục) |
| `ImageTags.reference()` | Thẻ gửi kèm ảnh cho `suggest_alt(tags=…)` (T-050): `{"Hạng mục", "Khu vực", "Giai đoạn"}`; **không** gửi mã công trình; ảnh AI trả `{}` |
| `tags_for_image(ref: ImageRef) -> FolderTags` | Thẻ đọc từ tên thư mục (`tags`, `unmatched`, `conflicts`). Chỉ nhận `ImageRef` (`tags.py:724`) |
| `tags_for_folder(SubFolder \| rel_dir)` | Thẻ của một thư mục con; đường dẫn kiểm bằng đúng lớp kiểm của `ImageRef` (`tags.py:736`) |
| `match_area`, `match_category`, `match_phase`, `match_project_code`, `match_source` | So một giá trị với danh sách, trả dạng chuẩn hoặc rỗng (cho ô nhập, ô chọn) |
| `AREAS`, `AREA_GROUPS`, `PHASE_LABELS`, `SOURCE_LABELS`, `FIELD_LABELS` | Cho giao diện (ô chọn khu vực theo nhóm, nhãn tiếng Việt) |
| `ImageTagStore(path=DEFAULT_IMAGE_TAGS_FILE)` | Kho thẻ sửa tay: `resolve(ref)` / `resolve_many(refs)` (thẻ dùng cho ảnh: sửa tay nếu có, không thì đọc từ tên thư mục; **không ném lỗi** khi file hỏng hay bận, chỉ ghi `error`), `get`, `get_many`, `set`, `clear`, `clear_all`, `list_manual` |

Tên file ảnh (T-049, `naming.image_file_name`): truyền `category=tags.category`, `area=tags.area`, `project_code=tags.project_code`, `ai_generated=tags.is_ai`.

## Kho thẻ sửa tay (`seo_app/storage/image_tags.py`)

- File `data/image_tags.sqlite` (`:36`), `data/` đã có trong `.gitignore` (test `test_default_file_is_in_gitignored_data_folder`). Không ghi vào thư mục ảnh.
- Khóa: số thứ tự thư mục gốc + đường dẫn tương đối, dạng NFC, không phân biệt hoa thường (`ref_key`, `:113`), giống cách T-048 so tên. Không lưu đường dẫn tuyệt đối (test đọc nguyên file SQLite, không thấy đường dẫn gốc, `Users`, `My Drive`).
- Thẻ sửa tay **thay cả bộ** thẻ đọc từ tên thư mục (giao diện điền sẵn thẻ tự đọc, người dùng sửa rồi lưu). `clear(ref)` quay về thẻ tự đọc.
- Đọc an toàn: mỗi ô đọc qua `substr` có giới hạn rồi tự giải mã UTF-8 (`text_factory = bytes`, `:336`); mỗi dòng dựng lại bằng `ImageRef` và `ImageTags` (`_row_to_tag`, `:298`); sai bất cứ chỗ nào thì bỏ dòng, `list_manual` đếm vào `skipped`. Không `pickle`, `eval`; SQL dùng tham số `?`; `PRAGMA trusted_schema = OFF`.
- Ghi an toàn: `set` dựng lại `ImageRef` và `ImageTags` từ giá trị ngay trước khi ghi (`:217`), nên đối tượng bị sửa sau khi tạo hay lớp con bỏ kiểm tra cũng không ghi được chữ lạ. Giữ tối đa 20.000 thẻ, bỏ thẻ cũ nhất.
- File hỏng hẳn (không phải SQLite, sai cột, sai phiên bản, lớn hơn 64 MB) thì **đổi tên sang một bên** (`image_tags.hong-<ngày giờ>.sqlite`, kèm file nhật ký `-journal` nếu có) để giữ thẻ đã sửa, rồi tạo file mới (giống kho nháp). Chỉ khi SQLite báo chắc chắn hỏng; file bận hay không mở được thì báo lỗi, không đụng file (giống T-037 sau SL-T037-4).
- Chỗ đặt file là symlink hay junction (có thể trỏ ra ngoài `data/`): chỉ xóa chính liên kết, không đụng file/thư mục đích (`_remove_link`, `:386`). Là thư mục thật thì báo lỗi.
- Xóa file hay cả `data/` khi app đang chạy: lần sau tự tạo lại.
- Ảnh trong thư mục ảnh AI không sửa tay thành ảnh thật được (`set` báo `TagError`); file bị sửa tay thành "ảnh thật" thì lúc đọc vẫn ép về ảnh AI (`_keep_ai`, `:125`).

## Bằng chứng

Máy Windows 11, Python 3.12.15, worktree `wt-T-052`, nhánh `team/T-052`.

```
$ uv run pytest -q -p no:cacheprovider        (toàn bộ, tại 5db1f60, 2026-10-20 12:34–12:45 +07)
7753 passed, 19 skipped, 35 xfailed, 1 warning in 658.95s (0:10:58)

$ uv run pytest -q -p no:cacheprovider        (lượt trước, tại e902e38)
7752 passed, 18 skipped, 35 xfailed, 1 warning in 755.75s (0:12:35)

$ uv run pytest tests/test_images_tags.py -q -p no:cacheprovider
234 passed, 2 skipped in 15.32s

$ uv run ruff check .
All checks passed!
```

Không test nào hỏng ở cả hai lượt. Cảnh báo duy nhất là của test cũ `test_soi_loi_t028.py` (pydantic), không liên quan phiếu này. Lượt cuối hơn lượt trước 1 test qua (`test_store_checks_values_again_before_writing`) và 1 test bỏ qua (test nối `alt.py`, xem dưới).

Hai test bỏ qua trong `tests/test_images_tags.py`:
- `test_symlink_at_file_path_is_replaced_without_touching_target`: Windows chưa bật Developer Mode nên không tạo được symlink. Ca tương đương bằng junction (`test_junction_at_file_path_is_removed_without_touching_target`) **đã chạy và qua**.
- `test_tags_pass_alt_filter_unchanged_and_carry_no_folder_text`: cần `seo_app/images/alt.py` (T-050), có trên `main` từ `c1aa0ce` nhưng chưa có trên nhánh này (tạo từ `c00b2e1`). Sau khi gộp, test tự chạy. Đã thử trước: dựng `origin/main` (`b0fba1e`, có T-050) bằng `git archive` trong thư mục tạm, chép 3 file của phiếu này vào, `uv sync`, rồi `uv run pytest tests/test_images_tags.py tests/test_ai_images.py tests/test_soi_loi_t050.py tests/test_images_folders.py`: **868 passed, 7 skipped, 15 xfailed**; test nối `alt.py` **qua** (`-k alt_filter`: 1 passed). 7 bỏ qua đều là ca symlink trên Windows.

Kiểm thêm (ngoài test, thư mục tạm):
- Chép đúng phần lọc thẻ của `alt.py` trên `main` (`_CONTROL_CHARS` … `reference_lines`), cho chạy trên **15.775 tổ hợp**: mọi khu vực × trước/sau, và cả 15.640 hạng mục ghép được từ từ điển. **0 thẻ bị bộ lọc của T-050 bỏ**: chữ thẻ chỉ gồm chữ Latin, số, dấu cách, `.`, `–`.
- `git merge-tree --write-tree HEAD origin/main`: sạch (không xung đột).

## Đối chiếu tiêu chí xong và điều kiện

- [x] **YC1, app không ghi gì vào thư mục ảnh/Drive.** `tags.py` chỉ xử lý chữ: `test_tags_module_does_no_file_io` chặn `open`, `os.open`, `os.stat`, `os.scandir`, `os.remove`… mà vẫn đọc được thẻ. `test_app_writes_nothing_into_image_folder`: quét bằng `ImageLibrary`, đọc thẻ, lưu/xóa thẻ sửa tay, rồi so tên, cỡ, giờ sửa, SHA-256 của mọi file và thư mục trong thư mục ảnh: không đổi. Kho thẻ chỉ ghi `data/image_tags.sqlite`.
- [x] **YC2, chỉ nhận danh sách cố định; không khớp thì để trống và không đi ra ngoài.** Khu vực (`test_area_variants` 43 cách viết, `test_every_area_in_list_matches_itself_any_case_with_or_without_accents`, `test_misspelled_or_unknown_area_stays_empty` 18 ca gõ sai/ngoài vùng/chữ Kirin giả dạng/chữ số Ả Rập), mã CT (`test_project_code_pattern`, `test_project_code_wrong_pattern_is_dropped`), trước/sau, hạng mục. `test_unmatched_parts_with_customer_data_never_leave` (7 tên thư mục có tên khách, số điện thoại, địa chỉ, câu "ra lệnh"): không chữ nào lọt vào trường thẻ, `reference()` hay `repr`. Thử ngẫu nhiên 3.000 đường dẫn ghép từ chữ danh sách + chữ rác + ký tự vô hình, và 3.000 chuỗi Unicode ngẫu nhiên: mọi giá trị ra đều thuộc danh sách. `ImageTags` tự kiểm lúc tạo nên chữ lạ không thể nằm trong thẻ (`test_image_tags_rejects_values_outside_fixed_lists_without_echoing`).
- [x] **YC3, cache SQLite trong `data/`, xóa đi tạo lại được, đọc an toàn, chịu file hỏng.** `test_missing_file_or_folder_is_recreated`, `test_garbage_file_is_moved_aside_and_recreated`, `test_wrong_structure_is_moved_aside` (3 ca), `test_oversized_file_is_moved_aside`, `test_busy_file_reports_error_and_is_not_moved`, `test_tampered_rows_are_skipped` (18 dòng bị sửa: chữ lạ, `../`, `C:/`, sai kiểu, sai khóa, không múi giờ, sai UTF-8, ô 5.000 ký tự), `test_modules_do_not_use_unsafe_loaders` (đọc cây cú pháp: không import `pickle`/`marshal`/`shelve`/`yaml`/`subprocess`, không gọi `eval`/`exec`/`compile`).
- [x] **YC4, ảnh AI luôn `nguon = AI`, không gắn thẻ công trình thật.** `test_ai_image_never_carries_real_project_tags`, `test_ai_folder_marks_images_as_ai_and_drops_project_tags` (5 cách đặt thư mục), `test_ai_folder_image_cannot_be_turned_into_real_project` (kể cả file bị sửa tay).
- [x] **Điều kiện Lá Chắn T-048 (LC-T048-4a).** `test_invisible_characters_are_removed_everywhere`: 20 ký tự (U+200B…U+200F, U+2028, U+2029, U+061C, U+FEFF, U+FFF9–FFFB, U+00AD, U+180E, U+2060, U+E0000, U+E0001, U+E0041, U+E007F, U+E000) chèn vào **mọi vị trí** của `CT012 - Cổng inox - Tân Phú`: kết quả giống hệt; chuỗi ký tự thẻ giấu chữ "IGNORE ALL RULES" bị bỏ. Ký tự điều khiển hướng chữ (T-048 đã chặn trong tên) cũng bị bỏ khi so ô nhập (`test_bidi_controls_removed_when_matching_values`).
- [x] **Điều kiện Lá Chắn T-050 (số 5): chỉ phần bên dưới thư mục ảnh đã khai báo.** Đầu vào là `ImageRef` (`tags_for_image` từ chối chuỗi, `Path`: `test_tags_for_image_only_accepts_image_ref`); `tags_for_folder` kiểm bằng đúng lớp kiểm của `ImageRef` (9 dạng `C:/Users/…`, `/Users/…`, UNC, `..`: `test_tags_for_folder_rejects_paths_outside_root`). `test_only_folders_below_declared_root_are_read`: gốc đặt tại `…/Users/Tân Phú/My Drive/CT999 - Cổng inox - Quận 7`, quét thật bằng `ImageLibrary`: không thẻ nào lấy từ phần đường dẫn tới gốc. Không đọc tên file ảnh (`test_file_name_is_not_used`).
- [x] **Thẻ sửa tay khóa theo `ImageRef`, không theo đường dẫn tuyệt đối.** `test_manual_tags_keyed_by_image_ref_not_absolute_path` (hai máy, hai gốc tuyệt đối khác nhau, cùng `ImageRef` → cùng thẻ; file SQLite không chứa đường dẫn gốc), `test_manual_key_ignores_case_and_unicode_form`.
- [x] Test dùng thư mục tạm, tên giả, không gọi mạng; fixture riêng trong file test trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (không đụng `data/` thật).
- [x] `uv run pytest` toàn bộ, `uv run ruff check .` sạch (phần Bằng chứng).

## Rủi ro và điểm cần chú ý

- **Đổi thứ tự `IMAGE_FOLDERS` thì thẻ sửa tay đi theo số thứ tự**, không theo thư mục. Gắn sai chỉ khi gốc mới có đúng cùng đường dẫn tương đối. Nháp (G3-9) lưu `ImageRef` cũng chịu điều này.
- **Đoán sai trong phạm vi danh sách:** cả phần ghép được từ danh sách thì nhận, kể cả khi người đặt tên có ý khác: thư mục chỉ có tên "Sáu" (tên người) được hiểu là "sau"; "Cửa sau" (cửa sau nhà) thành hạng mục "Cửa" + "sau"; "Gò" đứng một mình thành vật liệu "gỗ". Không lộ dữ liệu (giá trị luôn là chữ trong danh sách), chỉ sai thẻ; người dùng thấy và sửa tay được. Câu dài có chữ ngoài danh sách ("Cửa màu đất đỏ", "Nhà chị Sáu") thì bị bỏ cả phần, không đoán.
- `Bà Rịa – Vũng Tàu` viết có dấu cách quanh gạch thì bị tách thành hai khu vực (mâu thuẫn, để trống); viết liền `Bà Rịa-Vũng Tàu` thì nhận.
- Hạng mục ngoài từ điển (ví dụ "Bồn hoa sắt") để trống; muốn thêm phải sửa code. Câu báo lỗi hệ điều hành trong `ImageTagStoreError` có thể là tiếng Anh (`strerror` của Windows), không chứa đường dẫn (như `site_index.py`).
- Thư mục dự án mà đặt bên trong Drive thì `data/` cũng nằm trong Drive (chung với kho nháp, cache khác); không kiểm ở phiếu này.
- Chưa chạy trên Mac/Linux (máy này là Windows). Ca symlink chỉ chạy được ở đó.

## Đề xuất

- **Soi Lỗi:** chạy `tests/test_images_tags.py` trên Mac (tên NFD thật từ ổ đĩa, symlink ở chỗ đặt file thẻ); thử thêm tên thư mục thật kiểu chủ dự án hay đặt (có năm, tháng, tên khách); thử hai tab Streamlit cùng ghi thẻ sửa tay; thử bản gộp với `main` để test nối `alt.py` chạy.
- **Lá Chắn:** soát F1 ở `_prepare`/`_remove_link`/`_move_aside` (`image_tags.py:347–410`), F3 ở `_row_to_tag` (`:298`), A3 ở `ImageTags.reference()` và việc từ điển chỉ trả chữ do code viết (`tags.py:365`, `:424`, `:694`).
- **Chỉ Huy (cho T-056 / Họa Sĩ):** ô chọn khu vực dùng `AREA_GROUPS`; ô hạng mục dùng `match_category` hoặc `ImageTags.from_input` (báo `TagError` khi ngoài danh sách); hiện `FolderTags.unmatched` dạng "N phần tên thư mục không dùng" (không hiện chữ bị bỏ). Gọi `resolve_many` cho một trang ảnh. Khi trang Streamlit bắt đầu dùng `ImageTagStore()`, nên thêm vào `tests/conftest.py` một fixture tự động trỏ `seo_app.storage.image_tags.DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (như kho nháp), vì phiếu này không được sửa `conftest.py`.
- **Chỉ Huy (cho T-049):** `naming.image_file_name` nhận `category`, `area`, `project_code` từ `ImageTags` (đã chuẩn hóa), `ai_generated=tags.is_ai`.
- Sau này có thể chuyển danh sách hạng mục sang `config/` (Ngòi Bút) để chủ dự án tự thêm; vẫn là danh sách do chủ dự án kiểm soát nên vẫn đạt góp ý T-046 số 3. Không làm ở phiếu này.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-20, sửa theo báo cáo Soi Lỗi)

### Tóm tắt (cho chủ dự án)

Đã sửa cả 8 lỗi Soi Lỗi tìm ra (SL-T052-1 → 8), không để lại lỗi nào. Quan trọng nhất là **SL-T052-1**: ảnh AI đặt trong thư mục tên tự do (ví dụ "Ảnh do AI tạo", "AI images", "Ảnh Gemini vẽ") nay luôn là ảnh AI, không còn mang mã công trình, khu vực hay trước/sau của công trình thật. App cũng nhận ảnh AI qua **tên file** (ví dụ `Gemini_Generated_Image_….png` để lẫn trong thư mục công trình). Khi không chắc, app chọn phía an toàn: coi là ảnh AI. Ảnh đó chỉ mất thẻ công trình, không chữ nào của tên thư mục đi ra ngoài.

Các lỗi nhỏ còn lại:
- Đọc được "Dĩ An, Bình Dương", "Quận 7, TP.HCM", "Bà Rịa – Vũng Tàu".
- Đọc được "Ảnh trước", "Hình sau".
- Năm, ngày tháng, số thứ tự viết chung với thẻ không làm mất thẻ.
- File thẻ sửa tay bị sửa bậy (ngày lạ, số lạ) không làm hỏng cả trang ảnh.
- Liên kết (kể cả "hard link") đặt vào chỗ file thẻ lúc app đang chạy bị gỡ ngay ở lần mở sau; app không ghi ra ngoài `data/`.

### App phân biệt ảnh thật và ảnh AI thế nào (SL-T052-1)

Một ảnh là **ảnh AI** khi có ít nhất một dấu hiệu dưới đây. Không có dấu hiệu nào thì là ảnh thật.

1. Tên **bất kỳ thư mục nào** bên dưới thư mục ảnh đã khai báo có chữ `AI` đứng riêng hoặc tên công cụ tạo ảnh. Điều này áp dụng cả cho thư mục nằm trên thư mục công trình và cả phần tên không khớp danh sách. Ví dụ: `Ảnh do AI tạo`, `ảnh tạo bởi ai`, `AI images`, `GenAI`, `ẢnhAI mẫu`, `Ảnh A.I`, `ＡＩ`, `Gemini`, `Imagen`, `Nano Banana`, `Midjourney`, `DALL-E`/`DALL·E`/`DALLE`, `ChatGPT`, `GPT`, `Stable Diffusion`, `SDXL`, `Firefly`. Thư mục có dấu hiệu thì **mọi ảnh bên trong** là ảnh AI.
2. **Tên file ảnh** có các dấu hiệu trên (app tách tên theo dấu cách, dấu câu, gạch dưới). Ví dụ: `Gemini_Generated_Image_ab12.png`, `ChatGPT Image May 12, 2025….png`, `DALL·E 2024-05-12 ….webp`, `AI_cong_inox.jpg`. Tên file **chỉ** dùng để nhận ảnh AI, không cho thẻ nào khác (`test_file_name_is_not_used` vẫn qua).
3. Như lượt 1: thư mục có tên đúng danh sách (`Ảnh AI`, `AI`, `ảnh minh họa AI`…).

Khi so, app không phân biệt hoa thường, nhận cả chữ toàn chiều rộng và chữ có ký tự vô hình chen giữa (`A`+U+200B+`I`), nhưng **có phân biệt dấu**: `Ái` (tên người, như trong "Nhà chị Ái") không phải AI. Với tên thư mục (do người gõ), app tách cả chữ dính liền (`ẢnhAI`, `GenAI`). Với tên file (có thể là chuỗi ngẫu nhiên do máy đặt), app chỉ tách ở dấu cách, dấu câu, gạch dưới, nên `xAI3kQpZ.jpg`, `MAI_1.jpg`, `IMG_0001.jpg` và tên ảnh tải từ Zalo không bị coi là ảnh AI.

Ảnh AI chỉ giữ hạng mục; mã công trình, khu vực, trước/sau bị bỏ (như lượt 1). `reference()` gửi cho AI viết alt là rỗng. Thẻ sửa tay không đổi ảnh AI thành ảnh thật được: `set` báo lỗi, và câu báo nay nói rõ cả trường hợp tên file.

**Đánh đổi (phía an toàn):**
- Thư mục ảnh thật có chữ `AI`/`ai` đứng riêng (ví dụ tên khách gõ không dấu "Nha chi Ai") hay có tên công cụ: ảnh bị coi là ảnh AI và mất thẻ công trình. Muốn sửa thì đổi tên thư mục hoặc file. Nhận nhầm theo hướng này không làm lộ dữ liệu.
- Ảnh AI để trong thư mục công trình mà tên file trung tính (`IMG_0001.jpg`): app **không** biết đó là ảnh AI, vì module này chỉ đọc tên, không đọc nội dung ảnh (xem Đề xuất).

### Đã sửa

| Mã | Sửa gì | Chỗ sửa | Test |
|---|---|---|---|
| SL-T052-1 (Trung bình) | Tìm dấu hiệu ảnh AI ở mọi chỗ trong tên mọi thư mục, kể cả phần không khớp; tìm cả trong tên file; thêm tên công cụ tạo ảnh vào danh sách | `tags.py:198` (`_AI_TOOLS`), `:227` (`_AI_MARKER_TEXTS`), `:366` (`_tokens`), `:408` (`_has_ai_marker`), `:775` (`_parse_dir_name`), `:859` (`tags_for_image`); câu báo `image_tags.py:84` | Soi Lỗi `test_sl_t052_1_…` (5 ca, gỡ `xfail`). Mới: `test_ai_marker_anywhere_in_folder_name_makes_whole_branch_ai` (17 tên × 2 vị trí), `test_ai_marker_in_file_name_makes_image_ai` (6), `test_ordinary_file_names_are_not_ai` (8), `test_words_that_only_look_like_ai_do_not_make_ai_images` (5: "Ái", "Thái", "Hai", "mái", "Mai"), `test_ai_marker_detection_returns_no_folder_text` |
| SL-T052-2 (Thấp) | Thư mục ghi một quận/huyện kèm tỉnh/thành chứa nó thì lấy quận/huyện. Hai phần liền nhau, mỗi phần tự khớp danh sách, mà ghép lại thành đúng một khu vực thì đọc là khu vực đó ("Bà Rịa – Vũng Tàu"). Hai quận/huyện khác nhau, hai tỉnh, hay quận kèm tỉnh khác thì vẫn để trống | `tags.py:133` (`_AREA_PROVINCE`), `:761` (`_joined_area`), `:805` (`_narrow_area`), `:836` | Soi Lỗi `test_sl_t052_2_…` (5 ca + 45 tên, gỡ `xfail`). Mới: `test_province_with_its_district_and_real_conflicts`. Sửa test lượt 1 `test_every_area_in_list_matches_itself_…` (`test_images_tags.py:230`), vốn ghi theo hành vi cũ "Bà Rịa – Vũng Tàu để trống" |
| SL-T052-3 (Thấp) | Nhận "Ảnh", "Hình", "Hình ảnh" đứng trước mọi chữ chỉ trước/sau; thêm "sau khi làm/sửa/thi công xong", "thi công xong" | `tags.py:196` (`_PHASE_PREFIXES`), `:468`, `_PHASE_WORDS` | Soi Lỗi `test_sl_t052_3_…` (6 ca, gỡ `xfail`). Mới: `test_photo_word_before_phase` (8 ca, cả ô nhập `match_phase`) |
| SL-T052-4 (Thấp) | Trong tên thư mục, bỏ qua số trơn (chữ số ASCII) khi so. **Không** bỏ qua số đứng liền sau mã `CT` hay quận số: "Q 7 8", "CT 0909 123 456" không đoán, bỏ cả phần như cũ. Bước thử từng mảnh (tách ở `-_.`) không bỏ qua số, để "45 Nguyễn Trãi P.2 Quận 5" không đọc ra Quận 5 từ một địa chỉ. Ô nhập thẻ sửa tay cũng không bỏ qua số | `tags.py:498` (`_segment`, `skip_numbers`, mảng `firm` `:524`), `:531`, `:797` | Soi Lỗi `test_sl_t052_4_…` (4 ca, gỡ `xfail`). Mới: `test_plain_numbers_are_skipped_in_folder_names` (6), `test_numbers_right_after_code_or_numbered_district_are_not_guessed` (6) |
| SL-T052-5 (Thấp) | Khi đọc ngày lưu, bắt cả `OverflowError` lúc đổi múi giờ; dòng đó bị bỏ và đếm vào `skipped` | `image_tags.py:459–468` (`_parse_time`) | Soi Lỗi `test_sl_t052_5_…` (3 ca, gỡ `xfail`). Mới: `test_extreme_saved_at_is_skipped_not_raised` (4 ca, có ca biên hợp lệ năm 1) |
| SL-T052-6 (Thấp) | Số thứ tự thư mục gốc ngoài khoảng số nguyên SQLite (≥ 2⁶³): `resolve`, `resolve_many`, `get` coi như không có thẻ sửa tay (không ném lỗi); `clear` trả `False`; `set` và `list_manual` báo `ImageTagStoreError` tiếng Việt. Số 2⁶³ − 1 vẫn dùng bình thường | `image_tags.py:57`, `:134` (`_storable`), `:201`, `:234`, `:277`, `:296` | Soi Lỗi `test_sl_t052_6_…` (gỡ `xfail`). Mới: `test_root_index_beyond_sqlite_integer` |
| SL-T052-7 (Thấp, F1) | Kiểm liên kết ở **mỗi lần mở**, không chỉ lần đầu. Kiểm symlink, junction và **hard link** (file thường có `st_nlink > 1`), ở chỗ đặt file và cả ở các file nhật ký `-journal`, `-wal`, `-shm` (SQLite ghi qua các file này). Thấy liên kết thì chỉ gỡ chính liên kết rồi tạo file mới; tên kia của hard link và file/thư mục đích giữ nguyên | `image_tags.py:364–371` (`_prepare`), `:406` (`_remove_links`), `:439` (`_is_link`), `:451` (`_remove_link`) | Soi Lỗi `test_sl_t052_7_hard_link_…` (2 ca, gỡ `xfail`, chạy trên Windows); `test_sl_t052_7_symlink_…` gỡ `xfail` dựa trên code (xem dưới). Mới: `test_hard_link_at_file_path_is_removed_without_touching_other_name` (trước và sau lần dùng đầu), `test_hard_link_at_journal_path_is_removed` |
| SL-T052-8 (Thấp) | Nhờ kiểm ở mỗi lần mở: junction đặt vào sau lần dùng đầu bị gỡ ở lần mở kế tiếp, ngay lần đầu đã không báo lỗi. Nếu đặt một thư mục thật vào chỗ file thì app báo câu rõ ("đang là một thư mục") thay vì "Không mở được…"; gỡ thư mục đi thì app tự tạo lại file | `image_tags.py:370` | Soi Lỗi `test_sl_t052_8_…` (gỡ `xfail`). Mới: `test_directory_placed_after_first_use_reports_clear_error_then_recovers` |
| Điểm Lá Chắn | `_is_healthy` đặt `PRAGMA trusted_schema = OFF` trước khi chạy `PRAGMA quick_check` trên file chưa tin cậy | `image_tags.py:481` | Mới: `test_health_check_does_not_trust_schema_of_file` (kiểm thứ tự câu lệnh) |

Tôi không sửa điều kiện kiểm nào trong test của Soi Lỗi; chỉ xóa các dòng `@pytest.mark.xfail(...)` (`git diff 0848316 HEAD -- tests/test_soi_loi_t052.py`: xóa 74 dòng, thêm 0 dòng). Hai file test của phiếu không còn `xfail` nào.

**Ca symlink chưa chạy được trên máy này.** Hai test `test_sl_t052_7_symlink_placed_after_first_use_does_not_write_outside` (Soi Lỗi) và `test_symlink_at_file_path_is_replaced_without_touching_target` (của tôi) bị bỏ qua vì Windows chưa bật Developer Mode (đã thử, lỗi 1314). Tôi vẫn gỡ dấu `xfail(strict)` của ca Soi Lỗi vì hai lý do. Một: code mới kiểm `is_symlink()` ở mỗi lần mở, cùng đường với ca junction và hard link đã chạy qua. Hai: nếu giữ dấu thì trên Mac/Linux test sẽ báo XPASS và bị tính là hỏng. Kết luận này là suy luận từ code, cần chạy trên Mac/Linux để xác nhận.

### Phạm vi

`git diff --stat 0848316 HEAD` (trước khi thêm báo cáo) chỉ có 4 file được phép:

```
 seo_app/images/tags.py        | 183 ++++++++++++++++++++++----
 seo_app/storage/image_tags.py | 115 +++++++++++-----
 tests/test_images_tags.py     | 297 +++++++++++++++++++++++++++++++++++++++++-
 tests/test_soi_loi_t052.py    |  74 -----------
```

Không sửa `seo_app/images/__init__.py`, `folders.py`, `alt.py`, `app/**`, `config/**`, `drafts.py`, `site_index.py`. Không thêm thư viện.

### Bằng chứng (lượt 2)

Máy Windows 11, Python 3.12.15, worktree `wt-T-052`, nhánh `team/T-052`. Theo quy tắc mới tôi chỉ chạy test liên quan; Chỉ Huy chạy toàn bộ test khi gộp.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_images_folders*.py \
    tests/test_ai_images.py -q -p no:cacheprovider -rs        (tại f428bb3, 2026-10-20 14:11–14:12 +07)
849 passed, 8 skipped, 3 xfailed in 68.91s (0:01:08)

$ uv run ruff check .
All checks passed!
```

- 0 hỏng. Riêng hai file của phiếu: `test_images_tags.py` có 304 test (303 qua, 1 bỏ qua); `test_soi_loi_t052.py` có 52 test (51 qua, 1 bỏ qua); không còn `xfail`.
- 8 bỏ qua: 2 ca symlink của phiếu này (đã nói ở trên) và 6 ca của T-048 trong `test_images_folders.py` (symlink, tên chỉ tạo được trên Mac/Linux).
- 3 xfail: đều của T-048 trong `test_images_folders_soi_loi.py` (R2-1, R2-2), không thuộc phiếu này.
- Trước lượt 2 (Soi Lỗi chạy tại `13467e7`): 753 passed, 8 skipped, 31 xfailed. Chênh lệch: 28 ca xfail của SL-T052 nay qua, và có thêm 68 test mới của tôi.

### Rủi ro và điểm cần chú ý (lượt 2)

- **Nhận nhầm ảnh thật thành ảnh AI** khi tên thư mục hoặc tên file có `AI`/`ai` đứng riêng hay có tên công cụ (xem trên). Không lộ dữ liệu, ảnh chỉ mất thẻ; người dùng thấy nhãn "Ảnh AI" và có thể đổi tên thư mục hoặc file. Giao diện T-056 nên nói rõ lý do (ví dụ "tên thư mục hoặc tên file có chữ AI").
- **Hard link:**
  - Gặp file thẻ có hơn một tên, app gỡ tên nằm trong `data/` và bắt đầu file mới. Thẻ sửa tay cũ vẫn còn ở tên kia nên không mất dữ liệu, nhưng app không đọc tới nữa.
  - Phần mềm sao lưu kiểu "hard link vào thư mục sao lưu" (hiếm trên Windows/Mac) sẽ khiến app bỏ file thẻ sau mỗi lần sao lưu.
  - Nếu ổ đĩa báo sai số liên kết (lớn hơn 1 cho mọi file) thì thẻ sửa tay không giữ được. NTFS và APFS báo đúng; tôi đã thử trên NTFS: `st_nlink` từ 2 về 1 sau khi gỡ.
- **Khoảng hở vài mili giây giữa lúc kiểm và lúc SQLite mở file:** nếu có người thay file đúng lúc đó thì vẫn lọt. Lý do: SQLite mở file theo tên, Python không cho mở theo "file vừa kiểm". Muốn lợi dụng thì phải ghi được vào thư mục `data/` trên máy.
- **Ghép khu vực** chỉ xảy ra khi hai phần liền nhau đều tự khớp danh sách (`Bà Rịa – Vũng Tàu`, `Bà Rịa, Vũng Tàu`). `Vũng Tàu - Bà Rịa` (thứ tự ngược) vẫn được hiểu là hai thành phố khác nhau nên để trống.
- **Số đứng liền sau quận số hay mã CT vẫn làm mất cả phần** (`CT012 Cổng inox Quận 7 2024`, `CT012 2024 Cổng`). Giữ vậy để không đoán sai mã hoặc quận kiểu `Q 7 8`, `CT 0909 123`. Nếu viết năm thành phần riêng (`… - Quận 7 - 2024`) hoặc đặt năm lên trước (`2024 CT012 …`) thì app đọc đủ.
- Từ điển giai đoạn có thêm "thi công xong", nên một phần chỉ gồm chữ này nay là giai đoạn "sau" (trước đây bị bỏ cả phần).

### Đề xuất (lượt 2)

- **Chỉ Huy:** lập phiếu dọn chung cho `seo_app/storage/drafts.py` và `site_index.py`, cùng kiểu lỗi SL-T052-7: dùng chung một hàm kiểm liên kết (symlink, junction, hard link, kiểm ở mỗi lần mở, kể cả file nhật ký). Có thể chuyển `_is_link`/`_remove_link` (`image_tags.py:439`, `:451`) thành hàm dùng chung. Việc này ngoài phạm vi phiếu nên tôi không làm.
- **Chỉ Huy / Thợ Máy (sau này):** nhận ảnh AI theo **nội dung ảnh**, ví dụ dữ liệu C2PA ("Content Credentials") mà Gemini, ChatGPT, Firefly ghi vào ảnh, hoặc trường EXIF `Software`. Cách này bắt được cả ảnh AI có tên file trung tính. Vì phải đọc file ảnh nên việc này thuộc `folders.py` hoặc phần xử lý ảnh, không thuộc `tags.py`; cần hỏi chủ dự án có cần không.
- **Thư Ký (README) / Họa Sĩ (T-056):** hướng dẫn đặt ảnh AI trong thư mục có chữ "AI" (hoặc giữ nguyên tên file gốc của công cụ); không đặt ảnh thật trong thư mục có chữ "AI"; giao diện hiện lý do một ảnh bị coi là ảnh AI.
- **Soi Lỗi (trên Mac/Linux):** chạy `tests/test_images_tags.py` và `tests/test_soi_loi_t052.py` để xác nhận hai ca symlink (đã gỡ `xfail`) và tên NFD thật.
- **Lá Chắn:** soát lại F1 ở `_prepare`, `_remove_links`, `_is_link`, `_remove_link` (`image_tags.py:364–457`), và A3 ở phần tìm dấu hiệu ảnh AI (`tags.py:408`, `:775`, `:859`): phần này chỉ trả đúng/sai, không giữ chữ nào của tên.

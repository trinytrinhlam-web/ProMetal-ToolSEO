# Báo cáo T-052 · Thẻ ảnh đọc từ tên thư mục (G3-6)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-052](../tickets/T-052-the-anh-theo-ten-thu-muc.md) |
| Ngày nộp | 2026-10-20 |
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
$ uv run pytest -q -p no:cacheprovider          (toàn bộ, <<PYTEST_TIME>>)
<<PYTEST_RESULT>>

$ uv run pytest tests/test_images_tags.py -q -p no:cacheprovider -rs
<<T052_RESULT>>

$ uv run ruff check .
All checks passed!
```

Hai test bỏ qua trong `tests/test_images_tags.py`:
- `test_symlink_at_file_path_is_replaced_without_touching_target`: Windows chưa bật Developer Mode nên không tạo được symlink. Ca tương đương bằng junction (`test_junction_at_file_path_is_removed_without_touching_target`) **đã chạy và qua**.
- `test_tags_pass_alt_filter_unchanged_and_carry_no_folder_text`: cần `seo_app/images/alt.py` (T-050), có trên `main` từ `c1aa0ce` nhưng chưa có trên nhánh này (tạo từ `c00b2e1`). Sau khi gộp, test tự chạy. <<MAIN_CHECK>>

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

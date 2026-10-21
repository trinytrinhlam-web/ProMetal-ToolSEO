# Báo cáo T-055 · Nháp lưu lựa chọn ảnh (G3-9) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-055](../tickets/T-055-nhap-luu-lua-chon-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành. Lượt 1: **ĐẠT CÓ ĐIỀU KIỆN**. **Lượt 2 (2026-10-21): ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn được**; SL-T055-1 → 3 đã sửa, 2 lỗi mới mức Thấp (mục "Lượt 2"). **Lượt 3 (2026-10-21): sửa dữ liệu test theo LC-T055-4, 9 file test liên quan 0 hỏng, nhánh sẵn sàng gộp** (mục "Lượt 3" cuối báo cáo) |

## Tóm tắt (cho chủ dự án)

Nháp nhớ ảnh đã chọn đúng như thiết kế: chỉ ghi "thư mục ảnh số mấy + đường dẫn bên trong", mở lại vẫn giữ lựa chọn, nháp cũ (trước phiếu này, do chính bản app hiện tại trên `main` lưu) mở được và không mất chữ. Tôi thử sửa tay nháp theo hơn 50 cách (số lạ, đường dẫn ra ngoài, đường dẫn tuyệt đối, ký tự vô hình…): **không cách nào làm app đụng tới file ngoài thư mục ảnh**.

Tìm được 3 lỗi, không có lỗi Nghiêm trọng hay Cao:

- **SL-T055-1 (Trung bình):** nháp ghi đường dẫn khác chữ hoa/thường (`GenAI` thành `genai`) thì ảnh AI bị coi là **ảnh thật**, còn mang mã công trình và khu vực. Cần sửa tay nháp, hoặc người dùng đổi hoa/thường tên thư mục sau khi chọn ảnh.
- **SL-T055-2 (Trung bình):** alt đã duyệt khi ảnh còn là ảnh thật vẫn là "đã duyệt" khi mở lại nháp mà ảnh nay là ảnh AI. Alt đó không có chữ «Minh họa» nên ảnh AI sẽ được mô tả như ảnh công trình thật.
- **SL-T055-3 (Thấp):** một dạng nháp sửa tay bị đếm sai số "ảnh hỏng đã bỏ".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t055.py` | Mới: 103 test qua và 7 test `xfail(strict=True)` ghi 3 lỗi SL-T055-1 → 3 |
| `docs/team/reports/T-055-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của người khác.

## Bằng chứng

Máy Windows 11 của chủ dự án, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055`.

```
$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py
    tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
    tests/test_images_folders.py tests/test_images_tags.py tests/test_app_pages.py
905 passed, 14 skipped, 7 xfailed in 333.77s (0:05:33)
(14 bỏ qua đều có từ trước, vì máy Windows không cho tạo symlink hoặc test quyền kiểu POSIX:
 test_drafts_images.py:568, test_soi_loi_t016_t020.py:232/260/273/333, test_images_folders.py:62/368/381,
 test_images_tags.py:1346. File mới không bỏ qua test nào trên máy này.)
(7 xfailed: đúng 7 test SL-T055-x; chạy --runxfail thì cả 7 hỏng ở dòng assert, không phải lỗi khác)

$ uv run pytest tests/test_soi_loi_t055.py      # sau khi đổi tên biến cho detect-secrets
103 passed, 7 xfailed in 31.97s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t055.py
"results": {}
```

## Dòng test cũ được sửa (`tests/test_soi_loi_t016_t020.py:744`)

Đồng ý với thay đổi `{"schema_version": 2}` → `{"schema_version": 3}`. Ca này (`test_wrong_shape_rows_give_draft_error`, dòng 734–758) kiểm "nháp ghi phiên bản khuôn **kế tiếp, chưa biết** thì báo `DraftError` và không lộ chữ trong file". Khi viết test (T-016) khuôn là 1 nên 2 là "chưa biết"; nay khuôn là 2 (`drafts.py:80`) nên 3 mới là "chưa biết". Đã đọc lại cả ca: phiên bản 3 đi qua `_no_images_before_v2` (`drafts.py:348`, nháp không có phần nào nên không đổi gì) rồi bị `_known_version` (`drafts.py:365`) từ chối, đúng ý cũ. Phần chặn lộ khóa giả `sk-ant-abc` vẫn nguyên.

Để lần nâng khuôn sau không bị quên, tôi thêm `test_schema_version_guard_for_old_test_line` (`test_soi_loi_t055.py:670`): kiểm `SCHEMA_VERSION + 1 == 3`; khi khuôn lên 3 test này đỏ, nhắc sửa cả dòng 744. Gợi ý cho lần sau: dòng 744 dùng `SCHEMA_VERSION + 1` thay cho số cố định.

## Lỗi tìm được

### SL-T055-1 · Trung bình · Nháp đổi hoa/thường đường dẫn làm ảnh AI thành ảnh thật

- **Tái hiện:** thư mục ảnh có `CT012 - Cổng inox - Tân Phú/GenAI/cong.png` ("GenAI" được T-052 nhận là thư mục ảnh AI nhờ tách chữ hoa, `tags.py:359`). Nháp sửa tay ghi `rel_path` là `.../genai/cong.png`, `source` là `"that"`. Gọi `check_chosen_image` (hay `check_draft_images`) **không** kèm `scanned`, có hay không có `tag_store`.
- **Mong đợi:** ảnh AI (hoặc không dùng được), không mang mã công trình. Đây là điều kiện Lá Chắn T-052 số 3 ghi trong phiếu: "nháp không bao giờ kéo ảnh AI về ảnh thật".
- **Thực tế:** `available=True`, `tags = ImageTags(source='that', project_code='CT012', category='Cổng inox', area='Tân Phú')`.
- **Nguyên nhân:** `stat_image` so tên không phân biệt hoa thường (`folders.py:510-517`) nên tìm ra đúng file, nhưng thẻ đọc từ **chữ trong nháp** (`drafts.py:790-792` gọi `tags_for_image(ref)` / `resolve_many` với `ref` của nháp). Chữ thường "genai" không còn chỗ tách chữ hoa nên không còn dấu hiệu AI.
- **Đường không cần sửa tay:** chọn ảnh khi thư mục tên `Genai` (chưa là ảnh AI), sau đó đổi tên thư mục thành `GenAI`: mở lại nháp, chưa quét, vẫn ra ảnh thật (`test_sl_t055_1_case_only_folder_rename_keeps_ai`).
- **Đã đúng khi** truyền `scanned` có ảnh đó (`drafts.py:782`): khóa về đúng `ImageRef` trên ổ, thẻ ra AI (`test_scanned_refs_fix_case_variant`).
- **Test:** `test_sl_t055_1_case_variant_cannot_launder_ai_folder` (2 ca), `test_sl_t055_1_case_only_folder_rename_keeps_ai` (`test_soi_loi_t055.py:452-489`). Chỉ chạy trên ổ không phân biệt hoa thường (Windows, Mac mặc định); ổ phân biệt hoa thường thì tên khác là file khác, lỗi không xảy ra.
- **Hướng sửa (Chỉ Huy chọn):** thẻ phải đọc từ **tên thật trên ổ**, không từ chữ trong nháp. Trong phạm vi `drafts.py`: khi ảnh không có trong `scanned`, xem thư mục chứa ảnh (`library.list_folder(root, thư_mục_cha)`, chỉ đọc tên, không mở file) để lấy đúng `ImageRef`; hoặc coi ảnh có chữ khác tên thật là "không dùng được". Cách gọn hơn cần sửa T-048 (`stat_image` trả `ImageRef` theo tên thật), ngoài phạm vi phiếu này.

### SL-T055-2 · Trung bình · Alt "đã duyệt" của ảnh nay là ảnh AI không có «Minh họa»

- **Tái hiện:** chọn ảnh thật, duyệt alt «Bản lề cổng inox bị gỉ trước khi sửa» (nháp lưu `alt_approved=true`). Sau đó ảnh thành ảnh AI theo một trong các đường: người dùng bấm "đổi sang ảnh AI" (`ImageTagStore.set(source="ai")`, đúng điều kiện T-052 cho T-056), thư mục mang dấu hiệu AI, T-070 nhận thêm tên AI, hoặc nháp sửa tay. Mở lại nháp, `check_draft_images`.
- **Mong đợi:** ảnh AI thì alt đã duyệt bắt đầu «Minh họa» (quy tắc C6 của Lá Chắn T-051: code bảo đảm, không trông vào người hay AI); nếu không thì không còn "đã duyệt" để người dùng duyệt lại hoặc gợi ý lại với `ai_generated=True`.
- **Thực tế:** `checked.is_ai=True` nhưng `checked.image.alt_approved=True`, alt vẫn là câu tả ảnh công trình thật. Ảnh AI tạo mới trong nháp sửa tay cũng giữ alt đã duyệt không có tiền tố.
- **Nguyên nhân:** `_check_images` (`drafts.py:794-815`) đổi thẻ sang AI nhưng trả nguyên `image` (alt, cờ duyệt, chú thích) đọc từ nháp.
- **Test:** `test_sl_t055_2_approved_alt_of_ai_image_has_prefix` (3 ca, `test_soi_loi_t055.py:509-533`); đối chứng `test_approved_alt_with_prefix_stays_approved` (qua).
- **Hướng sửa:** trong `_check_images`, khi thẻ cuối cùng là AI mà alt không bắt đầu `AI_ALT_PREFIX` thì trả bản `image` có `alt_approved=False`. Nên xử lý luôn chú thích của ảnh AI thiếu «Ảnh minh họa (AI)» (cùng quy tắc C6; tôi không ghi test riêng vì chú thích không có cờ duyệt). Nếu Chỉ Huy muốn để giao diện lo, thì ghi thành điều kiện cho T-056.

### SL-T055-3 · Thấp · Nháp khuôn 1 có `"chosen_image": null` bị đếm là ảnh hỏng

- **Tái hiện:** nháp khuôn 1 (`schema_version: 1`) mà mỗi phần có `"chosen_image": null` (chỉ có khi sửa tay, hay chép nửa chừng từ khuôn 2). Mở nháp.
- **Mong đợi:** `dropped_images == 0` (không có ảnh nào bị mất).
- **Thực tế:** `dropped_images == 2` (mỗi phần một). Giao diện theo đề xuất của Thợ Máy sẽ báo "2 ảnh đã chọn bị hỏng nên đã bỏ".
- **Nguyên nhân:** `_no_images_before_v2` đếm mọi phần **có khóa** `chosen_image`, kể cả `null` (`drafts.py:355-358`).
- **Test:** `test_sl_t055_3_v1_null_images_are_not_counted_as_dropped` (`test_soi_loi_t055.py:690`).
- **Hướng sửa:** chỉ đếm khi `part["chosen_image"] is not None`. Cùng chỗ: `schema_version` ghi dạng chữ `"2"` hay `true` cũng đi đường khuôn cũ, bỏ hết ảnh (hướng an toàn, chỉ khi sửa tay) và đếm theo cách trên.

## Đối chiếu yêu cầu (việc Chỉ Huy giao)

**1. F1: chỉ lưu (số gốc, đường dẫn tương đối); nháp sửa tay không bao giờ đọc được file ngoài thư mục ảnh**

- [x] JSON lưu chỉ có số gốc và đường dẫn tương đối, không có thư mục máy dưới mọi dạng viết (test của Thợ Máy `test_saved_json_has_only_index_and_relative_path`; khuôn `extra="forbid"`, `drafts.py:122-123`).
- [x] Số gốc sửa tay: âm, `-2⁶³`, `-2⁶³-1`, `2⁶³-1`, `2⁶³`, `2⁶⁴`, `10³⁰`, `1000`, chữ `"0"`/`"1"`, `0.0`, `1.0`, `true`, `false`, danh sách, đối tượng: chỉ bỏ ảnh đó, chữ giữ nguyên, kiểm ảnh không đụng ổ đĩa (`test_hand_edited_root_index_drops_image_keeps_text`, 16 ca). Số viết tay trong JSON `1e3`, `1e400`, `-1e400`, `NaN`, `Infinity`, `0.5`, `1E2`: bỏ ảnh (`test_hand_edited_root_index_json_numbers`, 8 ca). `-0` là gốc 0 (đúng). Chặn ở `drafts.py:181` (`strict=True`, 0…999).
- [x] Đường dẫn sửa tay, 31 dạng trỏ tới file đặt sẵn **ngoài** thư mục ảnh: `..` theo `/` và `\`, `%2e%2e`, dấu chấm toàn khổ `．．`, `‥`, `..` kèm ký tự vô hình/đảo hướng, `~`, `$HOME`, `%USERPROFILE%`, đường dẫn tuyệt đối Windows/POSIX, `\\?\`, `//?/`, `\\.\`, UNC `\\localhost\C$`, `file:///`, đường dẫn bỏ dấu ổ, `C:tên`, `::$DATA`, chấm/cách cuối, `\x00`, xuống dòng. Mỗi ca theo dõi mọi lời gọi `os.lstat`/`os.stat`/`os.open`: **không lần nào chạm file ngoài gốc**, ảnh không dùng được, câu báo không có đường dẫn máy (`test_hand_edited_path_never_touches_file_outside_root`, 31 ca).
- [x] Tên lạ nhưng hợp lệ (`~`, `%2e%2e`, `$HOME`, `%USERPROFILE%`) là thư mục **bên trong** gốc, không giãn ra thư mục nhà hay biến môi trường (`test_kept_odd_names_stay_inside_root`).
- [x] Mở nháp (`load`) không đụng thư mục ảnh; ổ chỉ được hỏi qua `check_draft_images` → `ImageLibrary.stat_image` (`test_loading_a_draft_never_touches_the_image_folders`; Thợ Máy: `test_check_goes_through_stat_image`, `test_check_does_not_scan_or_read_files`).
- [x] Windows: file ẩn (thuộc tính Hidden) không dùng được; tên ngắn 8.3 (`THUMUC~1/ANHRAT~1.JPG`) bị từ chối; khác hoa thường thì đọc đúng file **trong** gốc (`test_hidden_file_in_draft_is_unavailable`, `test_short_8_3_name_in_draft_is_rejected`, `test_case_variant_reads_the_same_file_inside_root`). Junction: test của Thợ Máy.

**2. Nguồn ảnh theo hướng an toàn; thẻ dựng lại qua `ImageTags(...)`**

- [x] Bảng 2 × 4: nháp ghi thật/AI × thẻ hiện tại thật / thư mục AI / thẻ sửa tay AI / gốc AI. Ra ảnh AI khi **một trong hai** nói AI, ảnh AI không mang mã CT, khu vực, trước/sau (`test_source_matrix_ai_wins`, 8 ca).
- [x] Thư mục AI ở tầng trên thư mục mang tên công trình: vẫn AI, không mã CT (`test_ai_folder_above_project_folder_wins`).
- [x] Thẻ hiện tại sai khuôn: dựng lại qua `ImageTags(...)` hỏng thì về ảnh AI, chỉ giữ hạng mục đã kiểm (`test_bad_current_tags_are_rebuilt_and_fall_back_to_ai`, nhánh `drafts.py:690-699` chưa có test).
- [ ] **SL-T055-1**: chữ hoa/thường trong nháp kéo được ảnh AI về ảnh thật khi chưa truyền `scanned`.

**3. Alt, chú thích, prompt đọc từ nháp**

- [x] 8 dạng chữ độc (`<img onerror>`, `<script>`, `![](javascript:)`, `[](data:)`, `<a href=javascript:>`, `<iframe>`, ký tự đảo hướng/vô hình/ANSI, Markdown nhiều dòng) trong alt, chú thích: không còn thẻ, link, ký tự lạ, một dòng (`test_alt_and_caption_from_draft_are_inert`, 8 ca). Prompt: giữ chữ để sao chép, bỏ ký tự điều khiển/vô hình (`test_prompt_from_draft_is_plain_text`, 8 ca). Chữ giống mẫu lệnh (`{prompt}`, `${HOME}`, `__import__`) giữ nguyên là chữ (`test_template_and_code_like_text_is_kept_literally`).
- [x] Chữ cỡ 2,6 MB trong nháp: cắt về 500 / 1000 / 4000 ký tự, không bỏ ảnh (`test_huge_text_in_draft_is_bounded`, 3 ca).
- [ ] **SL-T055-2**: alt đã duyệt của ảnh nay là ảnh AI không có «Minh họa».

**4. Nháp cũ, nháp hỏng phần ảnh, `schema_version`, lưu rồi mở lại**

- [x] Nháp khuôn 1 **do chính code trên `main` (08e803e) lưu ra** (có nghiên cứu, dàn ý, rà soát, câu bỏ qua): mở được, đủ chữ, chọn ảnh rồi lưu lại thành khuôn 2, mở lại giữ ảnh (`test_real_v1_draft_from_main_opens_and_resaves_as_v2`); mở ở khuôn 1 hay khuôn 2 chữ như nhau (`test_v1_keeps_every_text_field_like_v2`).
- [x] `schema_version`: lưu ra 2, khuôn 1 nâng lên 2, khuôn kế tiếp (3), `10⁶`, `-2⁶³` báo "bị hỏng" không lộ chữ trong file (`test_future_versions_fail_whole_draft_without_leaking`, `test_schema_version_guard_for_old_test_line`).
- [x] Nhiều ảnh (tên tiếng Việt có gạch nối dài, ảnh AI tạo mới, phần không chọn ảnh): lưu rồi mở lại giữ nguyên từng lựa chọn (`test_round_trip_many_images_keeps_every_choice`).
- [x] Phần ảnh hỏng ở mức khuôn: chỉ mất ảnh đó (test của Thợ Máy, 20 ca + các ca số gốc ở trên).
- [ ] **SL-T055-3** (Thấp): đếm sai số ảnh bỏ.

## Rủi ro và điểm cần chú ý

- **Giới hạn đã biết, cùng loại surrogate lẻ Thợ Máy đã ghi:** JSON hỏng ở mức đọc file nằm trong phần ảnh (số gốc 5.000 chữ số, mảng lồng 300 tầng) thì **cả nháp** báo "Nháp này bị hỏng" chứ không chỉ mất ảnh. App không sập, câu báo không chép chữ trong file (`test_json_level_breakage_in_image_is_a_draft_error_not_a_crash`). Chỉ xảy ra khi sửa tay; sửa thì phải đổi cách đọc JSON của cả kho nháp.
- Nháp nhận `chosen_image` cả ở phần **không có chỗ cần ảnh** (`image` rỗng), ví dụ phần mở bài; `{}` thành "ảnh AI tạo mới" không có prompt. Không hại gì ở tầng lưu; T-056/T-054 nên chỉ dùng ảnh của phần có chỗ cần ảnh.
- Ổ **phân biệt** hoa thường (Linux, APFS tùy chọn): nếu cùng thư mục có `IMG_1.jpg` và `img_1.jpg`, khóa theo `scanned` (`drafts.py:771`, so không phân biệt hoa thường như T-052) có thể trỏ sang file kia. Cùng thư mục nên cùng thẻ; thiết kế giống `ref_key` của T-052. Thấp, chỉ ghi nhận.
- Không chạy được trên Mac/Linux (máy này là Windows): các test có `pytest.skip` theo hệ (ổ phân biệt hoa thường, thuộc tính ẩn, tên 8.3) cần chạy lại trên Mac theo T-063.

## Đề xuất

- **Thợ Máy (T-055):** sửa SL-T055-1, SL-T055-2, SL-T055-3 trong `seo_app/storage/drafts.py` (đều trong phạm vi phiếu), rồi gỡ `xfail` tương ứng trong `tests/test_soi_loi_t055.py`. Nếu Chỉ Huy cho SL-T055-1 cách sửa ở T-048 (`stat_image` trả `ImageRef` theo tên thật) thì cần phiếu riêng cho `seo_app/images/**`.
- **T-056 (Họa Sĩ), dù đã sửa hay chưa:** khi mở nháp nên truyền `scanned` nếu có; dùng `checked.tags` để quyết ảnh thật/AI; ảnh AI thì chỉ dùng alt có «Minh họa» (hoặc gợi ý lại với `ai_generated=True`).
- **T-070 (thẻ ảnh, ngoài phạm vi phiếu này, phát hiện khi thử):** thư mục tên `MidJourney` (chữ J viết hoa) **không** được nhận là ảnh AI vì bị tách thành "Mid Journey", trong khi `Midjourney`, `midjourney` thì có (`tags.py:359-363`, danh sách `_AI_TOOLS` `tags.py:198`). Tên file thì không bị (file không tách chữ hoa).
- **Lần nâng khuôn nháp sau:** sửa `tests/test_soi_loi_t016_t020.py:744` thành `SCHEMA_VERSION + 1` để khỏi phải sửa tay mỗi lần.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-21): kiểm lại sau khi Thợ Máy sửa

Kiểm trên nhánh `team/T-055`, đầu nhánh `2c95844` (Thợ Máy lượt 2). Kết luận: **ĐẠT CÓ ĐIỀU KIỆN**, **chuyển Lá Chắn được**.

### Tóm tắt (cho chủ dự án)

Ba lỗi của lượt 1 đã sửa thật:

- Nháp ghi tên thư mục khác chữ hoa/thường không còn làm ảnh AI thành ảnh thật: khi mở nháp, app xem tên thư mục thật trên ổ.
- Ảnh nay là ảnh AI thì alt luôn bắt đầu «Minh họa», chú thích bắt đầu «Ảnh minh họa (AI)», và alt phải đổi thì không còn "đã duyệt". Tôi thử hơn 6.000 câu alt khác nhau (mỗi câu cả lúc đã duyệt lẫn chưa duyệt) và lưu rồi mở nháp 5 lần liền: tiền tố không bao giờ bị lặp, alt đã có tiền tố không bị mất "đã duyệt" oan.
- Nháp cũ ghi "chưa chọn ảnh" không còn bị báo nhầm là ảnh hỏng.

Cách sửa thứ nhất có thêm bước xem tên thư mục trên ổ. Tôi thử bước này trên ổ thật: đổi tên, xóa, tráo liên kết (junction) giữa chừng, thư mục ẩn, thư mục không có quyền đọc, tên tiếng Việt ở hai dạng mã Unicode (thử thật trên Windows, giả lập cách Mac lưu tên). Kết quả: app không sập, không đọc ra ngoài thư mục ảnh, không mở file ảnh nào, câu báo không lộ đường dẫn máy.

Có 2 lỗi mới, **đều mức Thấp**, chỉ gặp ở cấu hình hiếm:

- **SL-T055-4:** trên ổ **phân biệt** chữ hoa/thường (Linux, một số ổ Mac) có hai thư mục chỉ khác hoa thường, hoặc thư mục bị đổi tên đúng lúc đang mở nháp, thì app có thể trỏ sang **một file ảnh khác** cùng tên mà vẫn báo "dùng được".
- **SL-T055-5:** thư mục ảnh có hơn 5.000 mục (hoặc ổ quá chậm) thì ảnh thật đã chọn ở các thư mục bên trong báo "chưa kiểm được", dù tên trong nháp đúng. Lượt 1 không bị.

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Hai lỗi Thấp không chặn phiếu: Chỉ Huy mở phiếu dọn, hoặc ghi vào sổ rủi ro.

### Kiểm từng lỗi cũ

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| SL-T055-1 (Trung bình) | **Đã sửa** | 3 test lượt 1 đã gỡ `xfail` và qua (`test_sl_t055_1_case_variant_cannot_launder_ai_folder` ×2, `test_sl_t055_1_case_only_folder_rename_keeps_ai`). Code: `_FolderNames.real_ref` (`drafts.py:761`) xem tên thư mục con từ gốc xuống bằng `ImageLibrary.list_folder` (không đệ quy, `page_size=1`, `:773`), trùng hẳn trước, rồi trùng không phân biệt hoa thường và NFC/NFD phải đúng một (`:786`); thẻ đọc theo tên thật (`:915-917`). Thêm: ổ NTFS có cả "Tân Phú" NFC lẫn NFD cạnh nhau vẫn chọn đúng (`test_ntfs_nfc_and_nfd_sibling_folders_are_told_apart`); giả ổ Mac lưu tên NFD, nháp ghi NFC và "genai": ra ảnh AI không mã công trình, ảnh thật giữ CT012 và Tân Phú (`test_mac_nfd_folder_names_keep_ai_and_real_tags`) |
| SL-T055-2 (Trung bình) | **Đã sửa** | 3 test lượt 1 đã gỡ `xfail` và qua (`test_sl_t055_2_approved_alt_of_ai_image_has_prefix`). Code: `_ai_wording` (`drafts.py:307`) dùng ngay `clean_suggestion(ai_generated=True)` của `alt.py` qua `_ai_prefixed` (`:176`), chạy khi mở nháp (`:655`) và khi kiểm ảnh (`:944`). Thử thêm: (1) 6.022 alt/chú thích, mỗi câu thử cả đã duyệt và chưa duyệt, 12.044 ca (gồm «minh hoạ», «Hình minh họa:», «Ảnh minh họa (AI):», chỉ dấu câu, HTML, ký tự vô hình, NFD, dài 600 ký tự, 6.000 chuỗi ngẫu nhiên có dấu, một nửa bắt đầu bằng các kiểu tiền tố): kết quả luôn bắt đầu bằng tiền tố (hoặc rỗng), chạy lại không đổi gì, alt đã có tiền tố không bao giờ mất "đã duyệt"; thêm 20.000 alt kiểu thật (tiền tố viết đủ kiểu «minh hoạ», «MINH HỌA», «Bức hình ảnh minh họa», «Minh hoạ (AI) -»… ghép với từ thật): không lần nào ra hai chữ «minh họa», chạy lại không đổi gì (script tạm, không commit). Chỉ chữ dính liền vô nghĩa như «minh hoạypg» mới thành «Minh họa minh hoạypg», do mẫu bỏ tiền tố của `alt.py` (T-050/T-051) cần ranh giới từ; không thực tế, ngoài phạm vi phiếu này. (2) 5 ngả thành ảnh AI (nháp ghi AI, thư mục AI viết thường, thẻ sửa tay AI, gốc AI, ảnh tạo bằng AI): alt đã có «Minh họa» giữ nguyên và vẫn đã duyệt; chú thích được thêm tiền tố mà không kéo alt mất duyệt (`test_prefixed_alt_never_loses_approval` ×5). (3) Mở, kiểm, lưu lại bằng `checked.image` 5 lần, duyệt lại ở lần 2: không lặp «Minh họa minh họa», chú thích trống vẫn trống, từ lần 3 không đổi gì và giữ "đã duyệt" (`test_prefix_is_not_repeated_over_many_save_open_cycles`) |
| SL-T055-3 (Thấp) | **Đã sửa** | Test lượt 1 đã gỡ `xfail` và qua. Code: chỉ đếm khi `chosen_image` khác `null` (`drafts.py:407`). Đối chứng: `false`, `0`, `""`, `[]`, `{}` (sửa tay) vẫn bị bỏ và đếm 1, chữ của bài giữ nguyên (`test_v1_non_null_image_values_are_still_counted` ×5) |

Nháp khuôn 1 do code của `main` lưu ra vẫn mở được, đủ chữ, lưu lại thành khuôn 2 (`test_real_v1_draft_from_main_opens_and_resaves_as_v2`, `test_v1_keeps_every_text_field_like_v2` vẫn qua).

### Soát test của Thợ Máy (`git diff 934c21b..2c95844`)

Lượt 2 chỉ đổi 4 file: `seo_app/storage/drafts.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py`, báo cáo Thợ Máy. `tests/test_soi_loi_t016_t020.py` không bị đụng thêm.

- `tests/test_soi_loi_t055.py`: đúng 16 dòng bị xóa, là 4 khối `@pytest.mark.xfail(...)` (4 dòng mỗi khối). Không đổi dòng `assert` hay dữ liệu thử nào. Đúng như Thợ Máy ghi.
- `tests/test_drafts_images.py`, 3 test của lượt 1 bị đổi, **không test nào bị làm yếu**:
  - `test_check_does_not_scan_or_read_files` (cấm `list_folder` và `read_image_bytes`) thay bằng `test_check_reads_no_file_and_lists_only_folders_on_the_path`: vẫn cấm `read_image_bytes`; `list_folder` chỉ được gọi đúng `[(0, ""), (0, "CT012 - …")]`, không đệ quy, mỗi thư mục một lần; ảnh nháp ghi AI và gốc AI không được xem. Thêm `test_scanned_images_need_no_folder_listing` (có `scanned` thì vẫn cấm `list_folder`). Đây là thay đổi hành vi có chủ đích của cách sửa SL-T055-1, và điều kiện kiểm còn chặt hơn. Tôi kiểm thêm phía "không mở file" bằng cách theo dõi `os.open`, `open` và chỗ giữ thư mục của Windows: chỉ có 2 thư mục được mở, không file ảnh nào (`test_check_opens_no_image_file`).
  - `test_save_load_save_is_stable`: alt của ảnh AI mẫu nay có sẵn «Minh họa», chữ độc vẫn giữ để thử bộ lọc. Lý do: lần mở đầu cố ý thêm tiền tố; việc này có test riêng `test_opening_draft_that_says_ai_already_adds_prefix`. Ý "lưu, mở, lưu lại ra đúng JSON" giữ nguyên.
  - `test_scanned_ref_becomes_the_key`: trước kiểm `ref` theo chữ trong nháp, nay kiểm `ref` và `entry.ref` theo tên thư mục trên ổ, kèm thẻ CT012, không phải ảnh AI. Kiểm nhiều hơn, không ít hơn.

### Lỗi mới

#### SL-T055-4 · Thấp · Tên thư mục "thật" không được kiểm lại là cùng file đã kiểm

- **Tái hiện 1 (ổ phân biệt hoa thường):** gốc có cả `GenAI/cong.png` (ảnh AI) lẫn `genai/cong.png` (file khác). Danh sách thư mục gốc bị cắt (thư mục quá 5.000 mục hay quét quá 10 giây) nên chỉ thấy `GenAI`. Nháp ghi `genai/cong.png`, nguồn "that". `check_chosen_image`.
- **Tái hiện 2 (ổ Windows/Mac, đổi tên đúng lúc):** nháp ghi `genai/cong.png`, trên ổ là `Genai/cong.png`. Giữa lúc `stat_image` và lúc xem tên, `Genai` đổi thành `Genai cu`, còn thư mục `Khac` (có `cong.png` khác) đổi thành `GenAI`.
- **Mong đợi:** ảnh "dùng được" thì `ref` là đúng file vừa kiểm; không chắc thì báo không dùng được.
- **Thực tế:** `available=True`, `ref` và `entry.ref` chuyển sang `GenAI/cong.png` là **file khác**, còn `entry` (cỡ, giờ sửa) vẫn là số liệu file cũ (tái hiện 2: `entry.size` 16, file ở `ref` 30 byte). Ngược lại, nháp (sửa tay, nguồn "that") ghi `GenAI/cong.png` mà danh sách bị cắt chỉ thấy `genai` thì ảnh trong thư mục AI ra **ảnh thật**, alt đã duyệt không có «Minh họa» vẫn "đã duyệt", `ref` trỏ sang `genai/cong.png` (ca thứ hai của tái hiện 1). Ca này trái điều kiện Lá Chắn T-052 số 3, nhưng cần cùng lúc: sửa tay nháp, ổ phân biệt hoa thường có hai thư mục chỉ khác hoa thường, và danh sách bị cắt.
- **Nguyên nhân:** `_FolderNames._child` (`drafts.py:768-789`) nhận "trùng không phân biệt hoa thường, đúng một" trong danh sách **có thể đã bị cắt** (không xem `listing.truncated`), rồi `_check_images` thay `ref`, `entry` (`:915-917`) mà không `stat_image` lại tên mới.
- **Hậu quả:** không đọc ra ngoài thư mục ảnh (F1 vẫn giữ, ảnh khác cũng nằm trong gốc và đọc qua `ImageLibrary`). Nhưng giao diện có thể đọc và đăng một ảnh khác ảnh người dùng đã chọn. Chỉ xảy ra trên ổ phân biệt hoa thường có hai thư mục chỉ khác hoa thường kèm danh sách bị cắt, hoặc khi thư mục bị đổi tên đúng lúc mở nháp.
- **Test:** `test_sl_t055_4_real_name_must_point_to_the_checked_file` (2 ca, giả ổ phân biệt hoa thường, chạy như nhau trên mọi máy), `test_sl_t055_4_folder_swapped_during_check_on_real_disk` (ổ thật; bỏ qua trên ổ phân biệt hoa thường) (`test_soi_loi_t055.py:756`, `:777`).
- **Hướng sửa (trong `drafts.py`):** sau `real_ref`, gọi `library.stat_image(real)` và so cỡ, giờ sửa với `entry` cũ, khác thì báo `_MSG_FOLDER_NAME`; và/hoặc khi `listing.truncated` mà không có tên trùng hẳn thì không nhận trùng không phân biệt hoa thường.

#### SL-T055-5 · Thấp · Thư mục cha quá nhiều mục thì ảnh thật bình thường cũng "chưa kiểm được"

- **Tái hiện:** thư mục ảnh gốc có hơn 5.000 mục (ví dụ ảnh điện thoại đồng bộ thẳng vào gốc, cạnh các thư mục công trình), hoặc ổ chậm khiến xem gốc quá 10 giây. Thư mục `CT012 - Cổng inox - Tân Phú` nằm sau mục thứ 5.000. Nháp ghi **đúng** tên như trên ổ `CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg`. Mở nháp, không có `scanned`.
- **Mong đợi:** như lượt 1, ảnh dùng được, thẻ ảnh thật CT012.
- **Thực tế:** `available=False`, câu báo «Chưa kiểm được tên thư mục chứa ảnh này… Hãy mở thư mục chứa ảnh để app kiểm lại.» cho **mọi** ảnh thật trong các thư mục con của gốc đó, không chỉ ca khác hoa thường. Thử trên ổ thật Windows (NTFS xếp tên theo thứ tự, chữ số trước chữ cái): gốc có 4.990 ảnh tên `2024xxxxx.jpg` vẫn dùng được (mất 2,3 giây); 5.200 ảnh thì ảnh ở `CT012…/GenAI` và `CT099…/truoc` đều "chưa kiểm được". Lời khuyên trong câu báo khó làm theo: màn hình duyệt ảnh xem gốc cũng dừng ở 5.000 mục nên không thấy thư mục đó; còn nếu giao diện chỉ truyền `scanned` là trang đang xem (`FolderListing.images`, tối đa 200 ảnh) thì ảnh ở trang khác vẫn chưa kiểm được.
- **Nguyên nhân:** `_check_images` gọi `real_ref` cho mọi ảnh nháp ghi là ảnh thật không có trong `scanned` (`drafts.py:910-917`), mà `list_folder` có giới hạn 5.000 mục / 10 giây (`folders.py:47-48`).
- **Đánh giá:** Thợ Máy đã ghi rủi ro này ("Thư mục rất lớn hay Drive chậm") và chọn hướng an toàn (không đoán theo chữ trong nháp). Tôi ghi thành lỗi Thấp vì đây là bước lùi so với lượt 1 và câu báo có thể không làm theo được. Muốn sửa gọn cần `stat_image` trả tên thật trên ổ (phiếu T-048, ngoài phạm vi; trên Windows `_resolve_inside` đã có sẵn tên thật, `folders.py:513`). Chỉ Huy chọn: mở phiếu, hoặc ghi sổ rủi ro kèm hướng dẫn "không để quá 5.000 mục ngay trong thư mục ảnh".
- **Test:** `test_sl_t055_5_plain_real_image_usable_when_parent_listing_is_cut` (`test_soi_loi_t055.py:804`, cắt danh sách bằng `monkeypatch`, chạy như nhau trên mọi máy).

### Đã thử, không có lỗi

- **Đổi tên, xóa, tráo junction giữa chừng** (giữa `stat_image` và lúc xem tên): ảnh không dùng được, không sập, câu báo không có đường dẫn máy (`test_folder_renamed_or_deleted_during_check` ×2, `test_junction_swapped_in_during_check_is_unavailable`).
- **Thư mục ẩn trên đường đi** (`attrib +h`): `stat_image` chặn trước («App không đọc thư mục hay file ẩn…»). **Thư mục không có quyền liệt kê** (`icacls /deny RD`): không dùng được, câu báo «Không đọc được thư mục này…», không lộ đường dẫn. (Thử bằng script tạm, không commit, vì cần đổi quyền trên ổ.)
- **Có mở file ảnh không:** không. Chỉ mở 2 thư mục (gốc và thư mục công trình) để đọc tên (`test_check_opens_no_image_file`).
- **Tốc độ** (ổ NTFS cục bộ, máy đang chạy song song 2 agent khác): gốc 1.000 ảnh 0,3 giây; gốc 4.990 ảnh 2,3 giây; thư mục cha 3.000 ảnh 0,4 giây; thư mục **chứa** ảnh không bị xem (3.000 ảnh: 0,04 giây). Mỗi thư mục chỉ xem một lần cho cả nháp. Không có giới hạn thời gian chung: tệ nhất, mỗi thư mục khác nhau trên đường đi có thể tốn tới 10 giây khi ổ rất chậm (suy luận từ `DEFAULT_MAX_SECONDS`, chưa đo trên Google Drive thật).
- **Tên file khác hoa thường** (`GenAI.png` / `genai.png`, `Gemini_x.png` / `gemini_x.png`): không đổi kết quả AI vì tên file không tách chữ hoa (`tags.py:858-859`). Đã chạy `tags_for_image`: `GenAI.png`, `genai.png` đều ảnh thật; `Gemini_x.png`, `gemini_x.png`, `GEMINI_X.PNG` đều ảnh AI. Thợ Máy để tên file theo nháp là đúng.

### Rủi ro và điểm cần chú ý (lượt 2)

- Ảnh **không dùng được** (USB rút, danh sách lỗi) thì thẻ vẫn đọc theo chữ trong nháp: nháp sửa tay `…/genai/…` hiện thẻ ảnh thật CT012 nhưng ảnh không dùng được (thấy ở các ca đổi tên, xóa, junction). Thợ Máy đã ghi. T-056 không nên hiện thẻ của ảnh không dùng được như thẻ đã kiểm.
- `checked.image.rel_path` vẫn là chữ trong nháp (`genai`), còn `checked.ref` theo tên trên ổ (`GenAI`). Giao diện lưu lại bằng `checked.image` thì lần mở sau lại phải xem tên thư mục. Nên lưu theo `checked.ref` (hay `DraftImage.from_library(checked.entry, …)`).
- `scanned` được tin là tên trên ổ: nếu giao diện giữ kết quả quét cũ (trước khi người dùng đổi tên thư mục) thì thẻ theo tên cũ. T-056 nên quét lại khi mở nháp.
- Các test có `skip` theo hệ (ổ phân biệt hoa thường, junction, NFC/NFD hai thư mục) cần chạy lại trên Mac/Linux theo T-063.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t055.py` | Thêm 17 test qua và 4 test `xfail(strict=True)` cho SL-T055-4 (3), SL-T055-5 (1); docstring đầu file thêm phần lượt 2. Không sửa test cũ |
| `docs/team/reports/T-055-soi-loi.md` | Mục này |

Không sửa code ứng dụng, không sửa test của người khác.

### Bằng chứng (lượt 2)

Máy Windows 11 của chủ dự án, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055`.

```
# Đầu nhánh 2c95844, trước khi thêm test của tôi
$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py
    tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
    tests/test_images_folders.py tests/test_images_tags.py tests/test_app_pages.py
936 passed, 14 skipped in 270.19s (0:04:30)        (khớp báo cáo Thợ Máy)

# Sau khi thêm test lượt 2
$ (cùng lệnh)
953 passed, 14 skipped, 4 xfailed in 230.23s (0:03:50)
(14 bỏ qua đều có từ trước, vì máy Windows không cho tạo symlink hoặc test quyền kiểu POSIX.
 4 xfailed: đúng 4 test SL-T055-4/-5. Chạy --runxfail thì cả 4 hỏng ở dòng assert:
 ref 'GenAI/cong.png' != 'genai/cong.png' (×2), size 30 != 16, available=False "Chưa kiểm được tên thư mục…")

$ uv run pytest tests/test_soi_loi_t055.py
127 passed, 4 xfailed in 18.13s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t055.py
"results": {}
```

### Kết luận lượt 2

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn được.**

- SL-T055-1, -2, -3: đã sửa, có test.
- Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T055-4, SL-T055-5).
- Điều kiện: Chỉ Huy mở phiếu dọn cho SL-T055-4 (sửa nhỏ trong `drafts.py`) và quyết SL-T055-5 (phiếu T-048 hay sổ rủi ro); chạy các test có `skip` theo hệ trên Mac theo T-063.
- Gợi ý cho Lá Chắn: soát `_FolderNames` theo F1 (mọi lần xem đều qua `ImageLibrary.list_folder`, không ghép đường dẫn tuyệt đối), và SL-T055-4 (đổi `ref` sang file chưa kiểm lại).

## Lượt 3 (2026-10-21): sửa dữ liệu test sau T-070 (LC-T055-4)

Theo biên bản Lá Chắn `docs/team/reports/T-055-la-chan.md`: dòng LC-T055-4 và mục "Điều kiện" số 1. Nhánh `team/T-055`, đầu nhánh trước lượt này `3e2c1fa` (đã có `main` mới nhất từ `15a9726`, và lượt 3 của Thợ Máy cho `tests/test_drafts_images.py`). Số dòng trong mục này là số dòng **sau lượt 3**.

### Tóm tắt (cho chủ dự án)

- Phiếu T-070 (đã ở `main`) dạy app nhận tên thư mục "genai" là ảnh AI, viết hoa hay thường đều vậy. File test của tôi lại dùng "genai"/"Genai" làm ví dụ cho tên **không** phải ảnh AI. Vì thế trên nhánh đã có `main`, 1 test của tôi hỏng và 4 test khác vẫn qua nhưng không còn kiểm đúng điều cần kiểm. Code của app không sai.
- Tôi đổi ví dụ sang cùng cặp Thợ Máy đã dùng: "CongAI" (ảnh AI, vì chữ "AI" viết hoa đứng tách ra) và "congai", "Congai" (ảnh thật). Các test dựa vào cặp tên này có thêm một câu kiểm lại ví dụ ngay đầu: nếu sau này app đổi cách nhận tên làm ví dụ sai đi, test báo hỏng ngay chứ không lặng lẽ qua.
- Thử cố ý làm hỏng lại cách sửa lỗi cũ (SL-T055-1, SL-T055-2): bộ test của tôi lại bắt được đúng như trước T-070 (15 test báo hỏng; trước khi sửa chỉ 11, và 4 test quan trọng không bắt).
- 9 file test liên quan: **0 hỏng**. Chỉ sửa file test của tôi, không sửa code của app. **Nhánh sẵn sàng gộp `main`** (điều kiện 1 của Lá Chắn đã xong; chỉ đổi dữ liệu test nên không cần Lá Chắn kiểm lại).

### Đã thay đổi (lượt 3)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t055.py` | `CAMEL_AI_PATH` thành `…/CongAI/cong.png` (`:68`); hằng `GENAI_VARIANT` thay bằng `CASE_VARIANT` (`…/congai/cong.png`, `:69`), dời lên đầu file. Thêm hàm điều kiện đầu `assert_ai_only_by_case` (`:210`, giống hàm cùng tên của Thợ Máy). Đổi chữ trong dữ liệu `GenAI`/`genai`/`Genai` → `CongAI`/`congai`/`Congai` ở 12 hàm test (bảng "Từng test"), câu báo `skip` đổi chữ theo. Docstring đầu file thêm đoạn "Lượt 3" |
| `docs/team/reports/T-055-soi-loi.md` | Mục này, dòng "Kết quả" ở đầu báo cáo |

Không sửa `seo_app/**`, không sửa `tests/test_drafts_images.py` hay test nào khác (`git diff --stat`: chỉ 2 file trên). Không đổi câu `assert` nào ngoài chữ trong dữ liệu (`…/GenAI/a.png` → `…/CongAI/a.png` ở `:900`), không đổi điều kiện `skip`, không thêm hay gỡ `xfail` (SL-T055-4 ×3, SL-T055-5 vẫn `xfail(strict=True)`). Số test giữ nguyên: 131.

### Kiểm cặp tên trước khi dùng

Chạy `tags_for_image(ImageRef(0, …))` và `is_ai_name(…)` trên nhánh hiện tại (đã có T-070), bằng script của Thợ Máy (`check_names.py`, không commit) cộng một lệnh tạm cho các đường dẫn riêng của file tôi:

| Đường dẫn trong file test | Ảnh AI | Ghi chú |
|---|---|---|
| `CT012 - Cổng inox - Tân Phú/CongAI/cong.png`, `CongAI/cong.png`, `Tân Phú/CongAI/a.png` | có | hạng mục "Cổng"; không mã công trình, không khu vực |
| `CT012 - Cổng inox - Tân Phú/congai/cong.png` | không | `that`, CT012, Tân Phú, "Cổng inox" |
| `congai/cong.png`, `Congai/cong.png` (ngay trong gốc) | không | `that` |
| `Tân Phú/congai/a.png` | không | `that`, Tân Phú |
| `genai`, `Genai`, `GenAI`, `GENAI` (mọi đường dẫn trên) | có | lý do phải đổi |

Ảnh trong `CongAI` có hạng mục "Cổng" chứ không phải "Cổng inox" (Thợ Máy đã nhắc). Không test nào của tôi kiểm hạng mục của ảnh này nên không ảnh hưởng.

### Từng test

Ba nhóm: (A) hỏng hoặc qua oan sau T-070, nay kiểm đúng ý và có câu điều kiện đầu; (B) không qua oan hẳn (bắt lỗi qua `ref`) nhưng có câu "là ảnh AI" qua oan, nay thêm câu điều kiện đầu; (C) chỉ đổi tên cho khớp, không kiểm thẻ AI nên không cần câu điều kiện đầu.

| Nhóm | Test | Trước (nhánh đã có `main`) | Sau |
|---|---|---|---|
| A | `test_sl_t055_1_case_only_folder_rename_keeps_ai` (`:494`) | **Hỏng** ở `assert picked.source == SOURCE_REAL` (`Genai` nay là ảnh AI ngay lúc chọn) | Chọn ảnh khi thư mục là `Congai` (ảnh thật), đổi thành `CongAI`: qua. Điều kiện đầu: `CongAI` là AI, `Congai` không |
| A | `test_sl_t055_1_case_variant_cannot_launder_ai_folder` ×2 (`:480`) | Qua oan: chữ `genai` trong nháp tự là ảnh AI | Ổ có `CongAI`, nháp ghi `congai`: chỉ ra ảnh AI khi thẻ đọc theo tên trên ổ |
| A | `test_prefixed_alt_never_loses_approval[thu-muc-AI-hoa-thuong]` (`:1010`) | Qua oan | Như trên; câu điều kiện đầu chỉ chạy cho ca này |
| A | `test_prefix_is_not_repeated_over_many_save_open_cycles` (`:1025`) | Qua oan | Như trên |
| A | `test_scanned_refs_fix_case_variant` (`:511`) | Qua, phần `is_ai` qua oan (Lá Chắn không nêu vì đường `scanned` không đi qua `_FolderNames`) | Có kết quả quét: `ref` về `CongAI`, ảnh AI |
| B | `test_mac_nfd_folder_names_keep_ai_and_real_tags` (`:873`) | Bắt lỗi ở dòng so `ref`, dòng `is_ai` qua oan | Dòng `is_ai` (`:879`) lại bắt được |
| B | `test_ntfs_nfc_and_nfd_sibling_folders_are_told_apart` (`:887`) | Như trên | `Tân Phú/CongAI` / `Tân Phú/congai`; điều kiện đầu theo đúng cặp này |
| B | `test_check_opens_no_image_file` (`:905`) | Bắt lỗi ở `opened`, phần `is_ai` qua oan | Như trên |
| B | `test_sl_t055_4_real_name_must_point_to_the_checked_file` ×2 (`:770`, `xfail`) | `xfail` vẫn đúng (hỏng ở dòng so `ref`), nhưng câu `is_ai` của ca thứ hai hết ý nghĩa (Lá Chắn: ví dụ ra ảnh AI ở cả hai phía) | Cặp `CongAI`/`congai`: khi SL-T055-4 được sửa và gỡ `xfail`, câu `is_ai` lại kiểm thật. Câu điều kiện đầu đặt sẵn; còn `xfail` thì câu này hỏng cũng bị tính là "hỏng như dự kiến", nên đã ghi chú trong test, và cùng cặp tên được kiểm ở các test nhóm A (không `xfail`) |
| C | `test_sl_t055_4_folder_swapped_during_check_on_real_disk` (`:795`, `xfail`), `test_folder_renamed_or_deleted_during_check` ×2 (`:937`), `test_junction_swapped_in_during_check_is_unavailable` (`:959`) | Qua (bắt lỗi qua `available` hay cỡ file, không qua thẻ AI) | Chỉ đổi tên thư mục (`GenAI cu` → `CongAI cu`…). Bắt buộc với 3 test sau: fixture `root` nay tạo `CongAI`, không còn `GenAI` |

`--runxfail` cho 4 test `xfail`: vẫn hỏng đúng chỗ như lượt 2: `ref` `CongAI/cong.png` ≠ `congai/cong.png` (×2, `:785`), cỡ 30 ≠ 16 (`:815`), `available=False` "Chưa kiểm được tên thư mục…" (`:837`). Câu điều kiện đầu ở `:780` qua.

### Thử đột biến (test có kiểm đúng ý không)

Theo lời giao: chép `app/`, `config/`, `seo_app/`, `tests/`, `pyproject.toml` sang thư mục nháp của phiên, thêm `return ref` ở đầu `_FolderNames.real_ref` (`drafts.py:761`) trong **bản sao**, chạy `tests/test_soi_loi_t055.py` bằng Python của worktree với `PYTHONPATH` trỏ vào bản sao (đã kiểm `seo_app.storage.drafts.__file__` nằm trong bản sao; `diff` với worktree chỉ khác đúng dòng đột biến). Không commit, không sửa file nào của repo. Ba bản: nhánh trước khi đưa `main` vào (`91305e0`, chưa có T-070, lấy bằng `git archive`), đầu nhánh `3e2c1fa` (có T-070, chưa sửa), và bản đã sửa.

| Bản | Không đột biến | Tắt `real_ref` |
|---|---|---|
| `91305e0` (trước T-070) | 0 hỏng | **15 hỏng**: 11 test bắt thật + 4 test `xfail` SL-T055-4/-5 thành "qua bất ngờ" (`XPASS(strict)`) |
| `3e2c1fa` (có T-070, chưa sửa) | **1 hỏng** (`…case_only_folder_rename…`) | 11 hỏng: chỉ 6 bắt thật + 1 vốn đã hỏng + 4 `XPASS(strict)`. **Không bắt:** `…case_variant_cannot_launder…` ×2, `test_prefixed_alt…[thu-muc-AI-hoa-thuong]`, `test_prefix_is_not_repeated…` (đúng 4 test Lá Chắn nêu) |
| Đã sửa (lượt 3) | **0 hỏng** | **15 hỏng**, đúng 15 test như bản trước T-070: 11 bắt thật + 4 `XPASS(strict)` |

Các test SL-T055-1 (`…case_variant_cannot_launder…` ×2, `…case_only_folder_rename…`) và SL-T055-2 (`test_prefixed_alt…[thu-muc-AI-hoa-thuong]`, `test_prefix_is_not_repeated…`) lại bắt được lỗi như trước T-070.

Thêm 3 đột biến bằng plugin của Thợ Máy (`mutate_t055.py`, sửa trong bộ nhớ, không đụng file):

| Đột biến | Trước khi sửa (`3e2c1fa`) | Sau khi sửa |
|---|---|---|
| `ref` theo tên trên ổ nhưng **thẻ theo chữ trong nháp** (đúng lỗi SL-T055-1) | 1 hỏng, là test vốn đã hỏng: **không test nào bắt được** | **8 test bắt** (`…case_variant…` ×2, `…case_only_folder_rename…`, `test_prefixed_alt…[thu-muc-AI-hoa-thuong]`, `test_prefix_is_not_repeated…`, `test_mac_nfd…`, `test_ntfs…`, `test_check_opens_no_image_file`). Plugin báo thêm `test_scanned_refs_fix_case_variant` hỏng, nhưng chạy riêng thì qua: do plugin nhớ chung giữa các test, không tính |
| Luật nhận tên đổi: thêm `congai` là ảnh AI (như T-070 đã làm với `genai`) | không áp dụng | 9 hỏng, cả 9 ở câu điều kiện đầu (`:215`): đúng 9 test có câu điều kiện đầu ngoài `xfail` |
| Bỏ bước "trùng hẳn trước" | 2 hỏng (1 vốn đã hỏng) | 1 hỏng (`test_ntfs…`), như trước |

### Bằng chứng (lượt 3)

Máy Windows 11 của chủ dự án, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055`. Có 2 agent khác chạy song song trên máy.

```
$ uv run pytest tests/test_soi_loi_t055.py                 # trước khi sửa (3e2c1fa)
FAILED tests/test_soi_loi_t055.py::test_sl_t055_1_case_only_folder_rename_keeps_ai
1 failed, 126 passed, 4 xfailed in 11.54s

$ uv run pytest tests/test_soi_loi_t055.py                 # sau khi sửa
127 passed, 4 xfailed in 12.76s

$ uv run pytest tests/test_soi_loi_t055.py --runxfail -k "sl_t055_4 or sl_t055_5"
4 failed, 127 deselected      (hỏng ở :785 ×2, :815, :837 như mô tả trên)

$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py
    tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
    tests/test_images_folders.py tests/test_images_tags.py tests/test_app_pages.py
1068 passed, 14 skipped, 4 xfailed in 149.11s (0:02:29)
(Thợ Máy lượt 3: 1 failed, 1067 passed; test hỏng đó là test của tôi, nay qua. 14 bỏ qua như
 lượt 2, đều vì máy Windows này không cho tạo symlink hay test quyền kiểu POSIX: test_drafts_images.py:633,
 test_soi_loi_t016_t020.py:232/260/273/333, test_images_folders.py:62/368/381, test_images_tags.py:1540.
 4 xfailed là SL-T055-4 ×3, SL-T055-5)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t055.py
"results": {}
```

### Đối chiếu (lượt 3, điều kiện 1 của Lá Chắn)

- [x] Đổi cặp tên thử sang cặp chỉ là ảnh AI nhờ tách chữ hoa (`CongAI` / `congai` / `Congai`, cùng cặp với Thợ Máy), đã kiểm bằng `tags_for_image` trên nhánh hiện tại trước khi dùng
- [x] Thêm `assert` điều kiện đầu cho các test SL-T055-1, SL-T055-2 và các test khác có kiểm "là ảnh AI" với cặp tên này
- [x] Đột biến tắt `_FolderNames.real_ref` trên bản sao: các test SL-T055-1, SL-T055-2 lại bắt được lỗi như trước T-070 (đúng 15 test như bản `91305e0`)
- [x] Không đổi điều kiện kiểm, không gỡ hay thêm `xfail` (SL-T055-4, -5 giữ `xfail`), không sửa code ứng dụng hay `tests/test_drafts_images.py`
- [x] 9 file test liên quan 0 hỏng, `ruff` sạch

### Kết luận lượt 3

**Nhánh `team/T-055` sẵn sàng gộp `main`** về phía Soi Lỗi: điều kiện 1 của Lá Chắn (LC-T055-4) đã xong ở cả hai file test. Kết luận lượt 2 giữ nguyên (ĐẠT CÓ ĐIỀU KIỆN; SL-T055-4, -5 mức Thấp chờ phiếu dọn; các điều kiện khác của Lá Chắn thuộc T-056, phiếu dọn, T-063).

### Đề xuất (lượt 3)

- Đồng ý đề xuất của Thợ Máy: phiếu dọn (điều kiện 3 của Lá Chắn) sửa docstring `_FolderNames` (`seo_app/storage/drafts.py:748-751`), vẫn ghi `"genai"` không phải ảnh AI.
- Khi phiếu dọn sửa SL-T055-4 và gỡ `xfail`: câu điều kiện đầu trong `test_sl_t055_4_real_name_must_point_to_the_checked_file` tự có hiệu lực, không cần sửa thêm.

# Báo cáo T-055 · Nháp lưu lựa chọn ảnh (G3-9) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-055](../tickets/T-055-nhap-luu-lua-chon-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành. Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** để chuyển sang Lá Chắn |

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

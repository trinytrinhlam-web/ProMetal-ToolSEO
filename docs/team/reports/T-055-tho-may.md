# Báo cáo T-055 · Nháp lưu lựa chọn ảnh (G3-9)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-055](../tickets/T-055-nhap-luu-lua-chon-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành; còn **1 test cũ** cần sửa một dòng ngoài phạm vi phiếu (xem "Cần Chỉ Huy quyết") |

## Tóm tắt (cho chủ dự án)

Bài đang soạn giờ nhớ được ảnh đã chọn cho từng chỗ cần ảnh: ảnh thật lấy từ thư mục USB/Drive, hoặc ảnh AI (nhớ prompt). Kèm theo là alt (và đã duyệt hay chưa), chú thích, hạng mục. Chưa có giao diện (Họa Sĩ làm ở T-056).

Nháp chỉ ghi "thư mục ảnh số mấy + đường dẫn bên trong thư mục đó", không bao giờ ghi đường dẫn đầy đủ trên máy. Khi mở lại nháp, app kiểm lại từng ảnh: USB chưa cắm, ảnh đã xóa hay đổi chỗ thì báo "không dùng được", nhưng vẫn giữ lựa chọn để cắm USB lại là dùng tiếp. Ảnh đã là ảnh AI thì nháp không bao giờ làm nó thành "ảnh thật". Nháp cũ (trước phiếu này) vẫn mở bình thường; phần ảnh trong nháp bị hỏng thì chỉ mất ảnh đó, chữ của bài còn nguyên.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | Khuôn ảnh đã chọn `DraftImage`, trường `DraftPart.chosen_image`, khuôn nháp lên 2 (khuôn 1 vẫn mở được), bỏ riêng ảnh hỏng khi đọc file, hàm kiểm lại ảnh trên máy `check_draft_images` / `check_chosen_image` |
| `tests/test_drafts_images.py` | Mới: 150 test |
| `docs/team/reports/T-055-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/**`, `seo_app/storage/__init__.py`, `app/**`, `config/**`, test cũ (`git diff --stat origin/main...HEAD` chỉ có 3 file trên). Không thêm thư viện.

## Khuôn dữ liệu ảnh trong nháp (khuôn 2)

Mỗi phần của bài (`DraftPart`) có thêm `chosen_image` (`null` nếu chưa chọn ảnh). Ví dụ một dòng trong `data/drafts.sqlite`:

```json
"parts": [
  {"heading": "Mục 1", "versions": ["…"], "current": 0, "image": "ảnh bản lề gỉ",
   "chosen_image": {
     "source": "that",
     "root_index": 0,
     "rel_path": "CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg",
     "category": "Cổng inox",
     "alt": "Bản lề cổng inox bị gỉ trước khi sửa",
     "alt_approved": true,
     "caption": "Bản lề gỉ sau 3 năm mưa nắng",
     "prompt": ""}},
  {"heading": "Mục 2", "versions": ["…"], "current": 0, "image": "minh họa cổng",
   "chosen_image": {
     "source": "ai", "root_index": null, "rel_path": "", "category": "Cổng inox",
     "alt": "Minh họa cổng inox hai cánh", "alt_approved": true,
     "caption": "Ảnh minh họa (AI): cổng inox hai cánh",
     "prompt": "Cổng inox hai cánh trước một nhà phố,\nánh sáng buổi sáng"}}
]
```

| Trường | Ý nghĩa và cách kiểm (`seo_app/storage/drafts.py`) |
|---|---|
| `root_index`, `rel_path` | Ảnh trong thư mục ảnh = `ImageRef` của T-048 (số thứ tự gốc, đường dẫn tương đối). Kiểm bằng chính `ImageRef(...)` mỗi lần tạo, kể cả khi đọc file (`:228`): chặn `..`, ổ đĩa, `/…`, UNC, gạch ngược, tên thiết bị, ký tự lạ, đuôi không phải ảnh. `root_index` là số nguyên thật (không nhận `true`, `"0"`, `1.5`), từ 0 tới `MAX_ROOT_INDEX = 999` (`:87`). `root_index = null` là ảnh tạo bằng AI (khi đó `rel_path` phải rỗng) |
| `source` | `"that"` (ảnh thật) hoặc `"ai"`. **Chỉ đúng chữ `"that"`** mới là ảnh thật; giá trị khác (`"AI"`, `"real"`, số, thiếu trường) đọc thành `"ai"` (`:191`). Ảnh tạo bằng AI luôn là `"ai"` (`:225`) |
| `category` | Hạng mục, dựng lại qua `ImageTags(category=…)` (`:196`): chỉ nhận đúng dạng chuẩn trong danh sách cố định của T-052; sai thì để trống, không giữ chữ lạ (chữ tự do có thể là tên, số điện thoại khách). Nháp **không** lưu mã công trình, khu vực, trước/sau: luôn đọc lại từ tên thư mục và thẻ sửa tay lúc mở |
| `alt`, `caption` | Lọc như chữ AI bằng `clean_alt_text` của T-050 (bỏ thẻ HTML, link Markdown, ký tự vô hình/điều khiển, gộp một dòng; địa chỉ trần bị chèn ký tự rộng 0 như T-031), bỏ surrogate lẻ, tối đa `MAX_ALT_CHARS = 500` / `MAX_CAPTION_CHARS = 1000` (`:132`). Giới hạn lưu rộng hơn quy tắc viết alt (125/200 trong `config/content.toml`) để đổi cấu hình không cắt mất alt đã duyệt |
| `alt_approved` | Cờ "người dùng đã duyệt alt", chỉ nhận `true`/`false` thật. Alt rỗng thì luôn `false` |
| `prompt` | Prompt ảnh AI: giữ nhiều dòng, bỏ ký tự điều khiển (trừ xuống dòng, tab), ký tự vô hình/đảo hướng chữ, surrogate lẻ; tối đa `MAX_PROMPT_CHARS = 4000` (`:140`). Chỉ là chữ: không bỏ thẻ, không escape (ô sửa và `st.code` không phải Markdown, bản sao chép phải đúng chữ), không chạy hay diễn giải gì |

Mọi trường lạ bị từ chối (`extra="forbid"`), không có chỗ cho khóa API hay đường dẫn tuyệt đối. Bộ lọc chạy lại không đổi gì: mở rồi lưu lại ra đúng JSON cũ (test `test_save_load_save_is_stable`, `test_cleaning_is_idempotent`).

## Khi mở nháp

1. **Đọc file** (`DraftStore.load`): khuôn 1 (trước phiếu này) được nâng lên khuôn 2 (`:364`). Ảnh sai khuôn (sửa tay) **chỉ bỏ ảnh đó**, đếm vào `snapshot.dropped_images` (`:294`, `:505`); phần chữ sai khuôn vẫn báo lỗi cả nháp như trước. Dữ liệu ảnh nằm trong nháp khuôn 1 là sửa tay (khuôn 1 không có ảnh): bỏ và đếm (`:342`). Phiên bản lạ (0, 3, 999, chữ…) vẫn báo "Nháp này bị hỏng".
2. **Kiểm trên máy** (`check_draft_images(snapshot, library, tag_store=…, scanned=…, ai_roots=…)`, `:705`), trả `{số thứ tự phần: CheckedImage}`:
   - Dựng lại `DraftImage` rồi `ImageRef(...)` (`:779`), hỏi `library.stat_image(ref)` (`:802`). Không tin số gốc: gốc không còn khai báo, USB chưa cắm, file mất, đi qua junction/symlink, quá lớn… thì `entry = None` kèm `message` (câu tiếng Việt của T-048, không có đường dẫn máy). Lựa chọn vẫn nằm trong nháp.
   - Không quét thư mục, không mở file ảnh (Drive "chỉ trực tuyến" không bị tải về; test `test_check_does_not_scan_or_read_files`). Đọc ảnh sau này vẫn phải qua `library.read_image_bytes(checked.ref)`.
   - `scanned`: kết quả quét trên giao diện (`FolderListing.images`). Ảnh trùng (không phân biệt hoa thường, NFC/NFD) thì `checked.ref` là **đúng `ImageRef` của kết quả quét** (`:782`), dùng làm khóa lựa chọn (điều kiện Lá Chắn T-048).
   - Thẻ: `tag_store.resolve_many` một lần cho cả nháp (`:788`); không có `tag_store` thì đọc từ tên thư mục. Nguồn ảnh theo hướng an toàn (`_safe_tags`, `:682`): là ảnh AI nếu nháp ghi AI, **hoặc** thẻ hiện tại nói AI, **hoặc** gốc nằm trong `ai_roots`; ảnh AI không mang mã công trình, khu vực, trước/sau. Nháp không bao giờ làm ảnh AI thành ảnh thật, không thêm hay đổi thẻ của ảnh thật.
   - Ảnh tạo bằng AI: `ref`, `entry` là `None`, thẻ ảnh AI với hạng mục ghi trong nháp.

## Bằng chứng

Máy Windows 11, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055`.

```
$ uv run pytest tests/test_drafts_images.py
149 passed, 1 skipped
(bỏ qua 1: test symlink chỉ chạy trên Mac/Linux; bản Windows là test junction, đã chạy)

$ uv run pytest tests/test_drafts_images.py tests/test_storage_drafts.py tests/test_soi_loi_t016_t020.py
    tests/test_soi_loi_t021_t017.py tests/test_app_drafts.py tests/test_images_folders.py
    tests/test_images_tags.py tests/test_app_pages.py
FAILED tests/test_soi_loi_t016_t020.py::test_wrong_shape_rows_give_draft_error[change7]
1 failed, 801 passed, 14 skipped in 153.01s (0:02:33)
(14 bỏ qua: 1 của file mới như trên; 13 có sẵn trong test cũ, đều vì máy Windows này không cho
tạo symlink hoặc test quyền kiểu POSIX, ví dụ test_soi_loi_t016_t020.py:232, test_images_folders.py:62)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/storage/drafts.py tests/test_drafts_images.py
"results": {}

$ uvx bandit -q seo_app/storage/drafts.py
1 Low: B101 assert ở drafts.py:453 (assert saved.saved_at có từ T-016, không thuộc phiếu này)
```

Ca hỏng duy nhất: `tests/test_soi_loi_t016_t020.py::test_wrong_shape_rows_give_draft_error[change7]` (xem dưới).

## Cần Chỉ Huy quyết: một test cũ ghim số phiên bản

`tests/test_soi_loi_t016_t020.py:744` (Soi Lỗi T-016) dùng `{"schema_version": 2}` làm ví dụ "phiên bản lạ, phải báo lỗi". Phiếu này tăng khuôn lên 2 đúng như yêu cầu 3, nên nháp khuôn 2 giờ là hợp lệ và ca đó hỏng (`DID NOT RAISE DraftError`). Ý của test (phiên bản chưa biết thì báo lỗi) vẫn đúng và đã có test mới cho 0, 3, 999, -1, chữ, `null` (`test_unknown_schema_versions_are_rejected`).

Đề xuất: đổi đúng một dòng `{"schema_version": 2}` thành `{"schema_version": 3}` (hoặc `999`). File này ngoài phạm vi phiếu (chỉ được sửa `drafts.py` và test mới), nên tôi **chưa sửa**, chờ Chỉ Huy cho phép hoặc giao Soi Lỗi. Tôi không tránh bằng cách nhảy số phiên bản (lên 3) vì như vậy là lách test.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1, F1: chỉ lưu (chỉ số gốc, đường dẫn tương đối) (`test_saved_json_has_only_index_and_relative_path`: JSON trong SQLite không chứa thư mục tạm dưới mọi dạng viết; `test_bad_relative_paths_are_rejected_when_created` 16 dạng đường dẫn xấu; `test_absolute_path_of_real_file_is_rejected`)
- [x] Yêu cầu 2, góp ý Lá Chắn T-046 số 11, điều kiện Lá Chắn T-048: dựng lại `ImageRef(...)` rồi `stat_image`, không tin số gốc (`test_check_goes_through_stat_image`, `test_root_index_out_of_range_is_kept_but_unavailable`, `test_broken_image_is_dropped_and_text_kept` 20 ca, `test_image_through_junction_is_unavailable`); khóa theo `ImageRef` của kết quả quét (`test_scanned_ref_becomes_the_key`, `test_scanned_refs_match_other_unicode_form`, `test_from_library_takes_scan_ref_and_tags`)
- [x] Điều kiện Lá Chắn T-052 số 3: thẻ dựng lại qua `ImageTags(...)` (`test_category_is_rebuilt_through_image_tags`); nguồn ảnh nghiêng về AI, không bao giờ kéo ảnh AI về ảnh thật (`test_draft_says_ai_wins_over_manual_real_tag`, `test_ai_folder_or_file_wins_over_draft_real`, `test_manual_ai_tag_wins_over_draft_real`, `test_unknown_source_values_read_as_ai` 10 ca, `test_generated_image_is_always_ai`, `test_draft_cannot_add_or_change_tags_of_real_image`)
- [x] Alt, chú thích, prompt là chữ chưa tin cậy: lọc, giới hạn độ dài, không chạy gì (`test_alt_and_caption_are_cleaned_one_line`, `test_text_limits`, `test_long_texts_in_file_are_cut_not_dropped`, `test_prompt_keeps_lines_and_drops_hidden_characters`, `test_prompt_is_kept_as_plain_text`)
- [x] Yêu cầu 3: nháp khuôn 1 vẫn mở được, tăng `schema_version` (`test_v1_draft_still_opens_and_is_upgraded` dùng nguyên khuôn JSON của T-016; lưu lại thì ghi khuôn 2); nháp hỏng phần ảnh không mất chữ (`test_every_image_broken_still_opens_with_all_text`, `test_v1_draft_with_image_data_drops_only_the_image`)
- [x] F3: đọc bằng `json` của pydantic, không `pickle`/`eval`; SQL vẫn dùng tham số `?` (không đổi)
- [ ] Test liên quan qua hết: còn 1 ca test cũ ghim số phiên bản, chờ Chỉ Huy (mục trên)
- [x] `uv run ruff check .` sạch; báo cáo đã đẩy lên `team/T-055`

## Rủi ro và điểm cần chú ý

- **JSON có mã `\ud800` lẻ** (chỉ có khi sửa tay file): bộ đọc JSON của pydantic từ chối cả nháp trước khi tới phần ảnh, nên trường hợp này vẫn mất cả nháp (báo "Nháp này bị hỏng"), như mọi trường khác từ T-016. App không bao giờ ghi ra dạng này. Có test ghi nhận (`test_lone_surrogate_escape_in_file_fails_like_before`). Sửa thì phải đổi cách đọc JSON của cả kho nháp, ngoài phạm vi.
- **Đổi thứ tự `IMAGE_FOLDERS`** thì ảnh trong nháp đi theo số thứ tự, không theo thư mục (giống thẻ sửa tay T-052). Gốc mới không có đúng đường dẫn đó thì báo "không dùng được"; có đúng đường dẫn đó thì trỏ nhầm ảnh. Giao diện nên hiện tên gốc (`roots()[i].label`) cạnh ảnh để người dùng thấy.
- **Ảnh tạo bằng AI chỉ nhớ prompt**, không nhớ file ảnh đã tạo (T-053 chưa có chỗ lưu ảnh AI). Mở lại nháp thì phải tạo lại ảnh. Khi T-053 có kho ảnh AI (ví dụ khóa bằng mã băm) thì thêm một trường ở khuôn 3.
- Phiếu dùng `clean_alt_text` (`seo_app/images/alt.py`) và `ImageTags`, `tags_for_image`, `ImageTagStore.resolve_many`, `ref_key` (T-052). T-068 và T-070 đang sửa các module này; nếu đổi cách lọc alt thì chạy lại `tests/test_drafts_images.py` (test bộ lọc chạy lại không đổi gì sẽ báo).
- `CheckedImage.entry.name` và `ref.rel_path` là tên file/thư mục trên máy: dữ liệu chưa tin cậy, giao diện phải escape và cô lập hướng chữ như T-056 đã ghi.
- Pydantic kiểm lại cả đối tượng `DraftImage` khi gắn vào `DraftPart`: giao diện tạo ảnh sai khuôn sẽ bị `ValidationError` ngay (tự lưu nháp đã bắt `ValueError` và hiện "Chưa lưu được nháp").

## Đề xuất

- **Chỉ Huy:** cho phép sửa một dòng ở `tests/test_soi_loi_t016_t020.py:744` (`2` → `3`), hoặc giao Soi Lỗi.
- **T-056 (Họa Sĩ), cách dùng:**
  - Lưu: `DraftPart(..., chosen_image=DraftImage.from_library(entry, resolved.tags, alt=…, alt_approved=…, caption=…))` với `entry` lấy từ `FolderListing.images` (không tự gõ `ImageRef`); ảnh AI tạo mới: `DraftImage(source="ai", prompt=…, category=…, alt=…)`. Khi người dùng bấm "đổi sang ảnh AI", lưu cả `source="ai"` vào nháp.
  - Mở: sau `open_draft`, gọi `check_draft_images(snap, library, tag_store=ImageTagStore(), scanned=<ảnh đang quét nếu có>, ai_roots=<gốc có tên ảnh AI, dùng is_ai_name của T-070>)`. Dùng `checked.tags` (không dùng `image.source` hay `image.category` trực tiếp) cho `suggest_alt(ai_generated=…)` và `image_file_name`. Hiện `checked.message` khi `not checked.available` và không phải ảnh AI tạo mới; hiện `snap.dropped_images` nếu > 0 ("N ảnh đã chọn trong nháp bị hỏng nên đã bỏ; chữ của bài vẫn giữ").
  - Trước khi dùng alt đã duyệt: kiểm lại theo `load_alt_rules().max_chars` (nháp cho lưu tới 500 ký tự).
- **T-054:** đọc ảnh bằng `library.read_image_bytes(checked.ref)`; alt/chú thích từ nháp đã ở dạng `clean_ai_text`, vẫn phải `unbreak_autolinks` và escape như điều kiện T-050.
- **Thư Ký / Chỉ Huy:** nếu muốn `from seo_app.storage import DraftImage, check_draft_images` thì thêm vào `seo_app/storage/__init__.py` (ngoài phạm vi phiếu này; hiện import từ `seo_app.storage.drafts`).
- **Soi Lỗi:** thử thêm nháp do bản app cũ (trước T-055) lưu thật trên máy chủ dự án; ảnh trùng tên khác hoa thường trên Mac (NFD); gốc là ổ FAT.
- **Lá Chắn:** soát `_safe_tags` (`drafts.py:682`) và đường bỏ ảnh hỏng (`:294`, `:342`) theo F1 và điều kiện T-048/T-052.

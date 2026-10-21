# Báo cáo T-055 · Nháp lưu lựa chọn ảnh (G3-9)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-055](../tickets/T-055-nhap-luu-lua-chon-anh.md) |
| Ngày nộp | 2026-10-20 (lượt 3: 2026-10-21) |
| Kết quả | Hoàn thành (kèm sửa 1 dòng test cũ ngoài phạm vi, Chỉ Huy B duyệt). **Lượt 2:** đã sửa SL-T055-1 → 3 (mục "Lượt 2"). **Lượt 3:** sửa dữ liệu test sau T-070 theo LC-T055-4 (mục "Lượt 3" cuối báo cáo) |

## Tóm tắt (cho chủ dự án)

Bài đang soạn giờ nhớ được ảnh đã chọn cho từng chỗ cần ảnh: ảnh thật lấy từ thư mục USB/Drive, hoặc ảnh AI (nhớ prompt). Kèm theo là alt (và đã duyệt hay chưa), chú thích, hạng mục. Chưa có giao diện (Họa Sĩ làm ở T-056).

Nháp chỉ ghi "thư mục ảnh số mấy + đường dẫn bên trong thư mục đó", không bao giờ ghi đường dẫn đầy đủ trên máy. Khi mở lại nháp, app kiểm lại từng ảnh: USB chưa cắm, ảnh đã xóa hay đổi chỗ thì báo "không dùng được", nhưng vẫn giữ lựa chọn để cắm USB lại là dùng tiếp. Ảnh đã là ảnh AI thì nháp không bao giờ làm nó thành "ảnh thật". Nháp cũ (trước phiếu này) vẫn mở bình thường; phần ảnh trong nháp bị hỏng thì chỉ mất ảnh đó, chữ của bài còn nguyên.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | Khuôn ảnh đã chọn `DraftImage`, trường `DraftPart.chosen_image`, khuôn nháp lên 2 (khuôn 1 vẫn mở được), bỏ riêng ảnh hỏng khi đọc file, hàm kiểm lại ảnh trên máy `check_draft_images` / `check_chosen_image` |
| `tests/test_drafts_images.py` | Mới: 150 test |
| `tests/test_soi_loi_t016_t020.py` | **Sửa 1 dòng ngoài phạm vi, Chỉ Huy B duyệt** (2026-10-20): dòng 744 `{"schema_version": 2}` → `{"schema_version": 3}`. Lý do: ca này kiểm "phiên bản khuôn lạ thì báo lỗi"; từ phiếu này số 2 là phiên bản hợp lệ nên ca cũ hỏng (`DID NOT RAISE DraftError`). Ý của test giữ nguyên; test mới còn kiểm 0, 3, 999, -1, chữ, `null`, danh sách (`test_unknown_schema_versions_are_rejected`). Soi Lỗi xem lại dòng này khi kiểm |
| `docs/team/reports/T-055-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/**`, `seo_app/storage/__init__.py`, `app/**`, `config/**`; test cũ chỉ sửa đúng dòng trên (`git diff --stat origin/main...HEAD` chỉ có 4 file trên). Không thêm thư viện.

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
802 passed, 14 skipped in 85.64s (0:01:25)
(sau khi sửa dòng 744 của test cũ; lượt trước khi sửa: 1 failed, 801 passed, 14 skipped)
(14 bỏ qua: 1 của file mới như trên; 13 có sẵn trong test cũ, đều vì máy Windows này không cho
tạo symlink hoặc test quyền kiểu POSIX, ví dụ test_soi_loi_t016_t020.py:232, test_images_folders.py:62)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/storage/drafts.py tests/test_drafts_images.py
"results": {}

$ uvx bandit -q seo_app/storage/drafts.py
1 Low: B101 assert ở drafts.py:453 (assert saved.saved_at có từ T-016, không thuộc phiếu này)
```

## Test cũ ghim số phiên bản (đã xử lý, Chỉ Huy B duyệt)

`tests/test_soi_loi_t016_t020.py:744` (Soi Lỗi T-016) dùng `{"schema_version": 2}` làm ví dụ "phiên bản lạ, phải báo lỗi". Phiếu này tăng khuôn lên 2 đúng như yêu cầu 3, nên lượt chạy đầu có đúng 1 ca hỏng: `test_wrong_shape_rows_give_draft_error[change7]` (`DID NOT RAISE DraftError`; lượt đó 1 failed, 801 passed, 14 skipped). Tôi không lách bằng cách nhảy số phiên bản lên 3, mà hỏi Chỉ Huy B; Chỉ Huy B cho đổi đúng dòng đó thành `{"schema_version": 3}`. Ý của test giữ nguyên (phiên bản chưa biết thì báo lỗi), test mới kiểm thêm 0, 3, 999, -1, chữ, `null`, danh sách. Soi Lỗi xem lại dòng này khi kiểm.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1, F1: chỉ lưu (chỉ số gốc, đường dẫn tương đối) (`test_saved_json_has_only_index_and_relative_path`: JSON trong SQLite không chứa thư mục tạm dưới mọi dạng viết; `test_bad_relative_paths_are_rejected_when_created` 16 dạng đường dẫn xấu; `test_absolute_path_of_real_file_is_rejected`)
- [x] Yêu cầu 2, góp ý Lá Chắn T-046 số 11, điều kiện Lá Chắn T-048: dựng lại `ImageRef(...)` rồi `stat_image`, không tin số gốc (`test_check_goes_through_stat_image`, `test_root_index_out_of_range_is_kept_but_unavailable`, `test_broken_image_is_dropped_and_text_kept` 20 ca, `test_image_through_junction_is_unavailable`); khóa theo `ImageRef` của kết quả quét (`test_scanned_ref_becomes_the_key`, `test_scanned_refs_match_other_unicode_form`, `test_from_library_takes_scan_ref_and_tags`)
- [x] Điều kiện Lá Chắn T-052 số 3: thẻ dựng lại qua `ImageTags(...)` (`test_category_is_rebuilt_through_image_tags`); nguồn ảnh nghiêng về AI, không bao giờ kéo ảnh AI về ảnh thật (`test_draft_says_ai_wins_over_manual_real_tag`, `test_ai_folder_or_file_wins_over_draft_real`, `test_manual_ai_tag_wins_over_draft_real`, `test_unknown_source_values_read_as_ai` 10 ca, `test_generated_image_is_always_ai`, `test_draft_cannot_add_or_change_tags_of_real_image`)
- [x] Alt, chú thích, prompt là chữ chưa tin cậy: lọc, giới hạn độ dài, không chạy gì (`test_alt_and_caption_are_cleaned_one_line`, `test_text_limits`, `test_long_texts_in_file_are_cut_not_dropped`, `test_prompt_keeps_lines_and_drops_hidden_characters`, `test_prompt_is_kept_as_plain_text`)
- [x] Yêu cầu 3: nháp khuôn 1 vẫn mở được, tăng `schema_version` (`test_v1_draft_still_opens_and_is_upgraded` dùng nguyên khuôn JSON của T-016; lưu lại thì ghi khuôn 2); nháp hỏng phần ảnh không mất chữ (`test_every_image_broken_still_opens_with_all_text`, `test_v1_draft_with_image_data_drops_only_the_image`)
- [x] F3: đọc bằng `json` của pydantic, không `pickle`/`eval`; SQL vẫn dùng tham số `?` (không đổi)
- [x] Test liên quan qua hết (phần Bằng chứng), sau khi sửa 1 dòng test cũ được Chỉ Huy B duyệt (mục trên)
- [x] `uv run ruff check .` sạch; báo cáo đã đẩy lên `team/T-055`

## Rủi ro và điểm cần chú ý

- **JSON có mã `\ud800` lẻ** (chỉ có khi sửa tay file): bộ đọc JSON của pydantic từ chối cả nháp trước khi tới phần ảnh, nên trường hợp này vẫn mất cả nháp (báo "Nháp này bị hỏng"), như mọi trường khác từ T-016. App không bao giờ ghi ra dạng này. Có test ghi nhận (`test_lone_surrogate_escape_in_file_fails_like_before`). Sửa thì phải đổi cách đọc JSON của cả kho nháp, ngoài phạm vi.
- **Đổi thứ tự `IMAGE_FOLDERS`** thì ảnh trong nháp đi theo số thứ tự, không theo thư mục (giống thẻ sửa tay T-052). Gốc mới không có đúng đường dẫn đó thì báo "không dùng được"; có đúng đường dẫn đó thì trỏ nhầm ảnh. Giao diện nên hiện tên gốc (`roots()[i].label`) cạnh ảnh để người dùng thấy.
- **Ảnh tạo bằng AI chỉ nhớ prompt**, không nhớ file ảnh đã tạo (T-053 chưa có chỗ lưu ảnh AI). Mở lại nháp thì phải tạo lại ảnh. Khi T-053 có kho ảnh AI (ví dụ khóa bằng mã băm) thì thêm một trường ở khuôn 3.
- Phiếu dùng `clean_alt_text` (`seo_app/images/alt.py`) và `ImageTags`, `tags_for_image`, `ImageTagStore.resolve_many`, `ref_key` (T-052). T-068 và T-070 đang sửa các module này; nếu đổi cách lọc alt thì chạy lại `tests/test_drafts_images.py` (test bộ lọc chạy lại không đổi gì sẽ báo).
- `CheckedImage.entry.name` và `ref.rel_path` là tên file/thư mục trên máy: dữ liệu chưa tin cậy, giao diện phải escape và cô lập hướng chữ như T-056 đã ghi.
- Pydantic kiểm lại cả đối tượng `DraftImage` khi gắn vào `DraftPart`: giao diện tạo ảnh sai khuôn sẽ bị `ValidationError` ngay (tự lưu nháp đã bắt `ValueError` và hiện "Chưa lưu được nháp").

## Đề xuất

- **T-056 (Họa Sĩ), cách dùng:**
  - Lưu: `DraftPart(..., chosen_image=DraftImage.from_library(entry, resolved.tags, alt=…, alt_approved=…, caption=…))` với `entry` lấy từ `FolderListing.images` (không tự gõ `ImageRef`); ảnh AI tạo mới: `DraftImage(source="ai", prompt=…, category=…, alt=…)`. Khi người dùng bấm "đổi sang ảnh AI", lưu cả `source="ai"` vào nháp.
  - Mở: sau `open_draft`, gọi `check_draft_images(snap, library, tag_store=ImageTagStore(), scanned=<ảnh đang quét nếu có>, ai_roots=<gốc có tên ảnh AI, dùng is_ai_name của T-070>)`. Dùng `checked.tags` (không dùng `image.source` hay `image.category` trực tiếp) cho `suggest_alt(ai_generated=…)` và `image_file_name`. Hiện `checked.message` khi `not checked.available` và không phải ảnh AI tạo mới; hiện `snap.dropped_images` nếu > 0 ("N ảnh đã chọn trong nháp bị hỏng nên đã bỏ; chữ của bài vẫn giữ").
  - Trước khi dùng alt đã duyệt: kiểm lại theo `load_alt_rules().max_chars` (nháp cho lưu tới 500 ký tự).
- **T-054:** đọc ảnh bằng `library.read_image_bytes(checked.ref)`; alt/chú thích từ nháp đã ở dạng `clean_ai_text`, vẫn phải `unbreak_autolinks` và escape như điều kiện T-050.
- **Thư Ký / Chỉ Huy:** nếu muốn `from seo_app.storage import DraftImage, check_draft_images` thì thêm vào `seo_app/storage/__init__.py` (ngoài phạm vi phiếu này; hiện import từ `seo_app.storage.drafts`).
- **Soi Lỗi:** xem lại dòng `tests/test_soi_loi_t016_t020.py:744` đã sửa; thử thêm nháp do bản app cũ (trước T-055) lưu thật trên máy của chủ dự án; ảnh trùng tên khác hoa thường trên Mac (NFD); gốc là ổ FAT.
- **Lá Chắn:** soát `_safe_tags` (`drafts.py:682`) và đường bỏ ảnh hỏng (`:294`, `:342`) theo F1 và điều kiện T-048/T-052.

## Lượt 2 (2026-10-20): sửa 3 lỗi Soi Lỗi tìm ra

Theo báo cáo Soi Lỗi `docs/team/reports/T-055-soi-loi.md` (SL-T055-1 → 3). Số dòng trong mục này là số dòng **sau lượt 2**.

### Tóm tắt (cho chủ dự án)

- **SL-T055-1 (Trung bình), đã sửa:** nháp ghi tên thư mục khác chữ hoa/thường (`GenAI` thành `genai`) không còn làm ảnh AI thành "ảnh thật". Khi mở nháp, app xem tên thật của các thư mục chứa ảnh trên ổ (chỉ đọc tên, không mở file ảnh) rồi mới đọc thẻ.
- **SL-T055-2 (Trung bình), đã sửa:** ảnh nay là ảnh AI thì alt luôn có chữ «Minh họa» đứng đầu (chú thích có «Ảnh minh họa (AI)»), và alt đó không còn "đã duyệt": người dùng đọc lại rồi duyệt.
- **SL-T055-3 (Thấp), đã sửa:** không còn báo nhầm "ảnh hỏng đã bỏ" khi nháp cũ ghi "chưa chọn ảnh".

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | Tên thư mục thật trên ổ (`_FolderNames`, `:745`) dùng trong `_check_images` (`:908`); tiền tố ảnh AI (`_ai_prefixed` `:176`, `_ai_wording` `:307`) dùng khi mở nháp (`clean_loaded`, `:655`) và khi kiểm ảnh (`:944`); đếm ảnh bỏ (`:407`) |
| `tests/test_drafts_images.py` | 150 → 174 test: thêm test cho 3 lỗi; đổi 1 test của lượt 1 (xem "Thay đổi so với lượt 1"); 1 test ổn định lưu/mở dùng alt ảnh AI đã có tiền tố |
| `tests/test_soi_loi_t055.py` | Chỉ gỡ 4 dấu `xfail` (7 test: SL-T055-1 ×3, SL-T055-2 ×3, SL-T055-3 ×1), không đổi điều kiện kiểm |
| `docs/team/reports/T-055-tho-may.md` | Mục này |

Không sửa `seo_app/images/**`, `app/**`, `config/**`; không thêm thư viện.

### Cách sửa

**SL-T055-1.** Gốc lỗi: thẻ đọc từ tên thư mục phân biệt hoa thường ("GenAI" được nhận là ảnh AI nhờ tách chữ hoa, "genai" thì không), còn ổ Windows/Mac và `stat_image` thì không phân biệt, nên chữ trong nháp quyết định thẻ. Cách sửa trong `drafts.py` (theo gợi ý thứ nhất của Soi Lỗi, không cần sửa T-048):

- Ảnh nháp ghi là **ảnh thật**, không có trong `scanned`, `stat_image` thấy ảnh: `_FolderNames.real_ref` (`:761`) xem `library.list_folder(gốc, thư_mục, page_size=1)` từ gốc xuống từng tầng (không đệ quy), lấy tên thư mục con trùng tên trong nháp: trùng hẳn trước (ổ phân biệt hoa thường có thể có cả "GenAI" lẫn "genai", là hai thư mục khác nhau), rồi trùng không phân biệt hoa thường và phải **đúng một** (`:768`). `ref`, `entry.ref` và thẻ (`resolve_many`, `tags_for_image`) theo tên thật đó.
- So không phân biệt hoa thường đúng cách của thư mục ảnh: NFC + `casefold` (`_name_key`, `:739`, như `folders._name_key` và `ref_key`).
- Không kiểm được tên thật (thư mục quá 5.000 mục hay quét quá giờ nên chưa thấy, hai tên chỉ khác hoa thường, lỗi đọc thư mục): ảnh **không dùng được**, kèm câu báo không có đường dẫn máy (`_MSG_FOLDER_NAME`, `:108`); không đoán theo chữ trong nháp. Lựa chọn vẫn nằm trong nháp; giao diện truyền `scanned` (kết quả quét thư mục chứa ảnh) là hết.
- Không cần bước này khi: ảnh có trong `scanned` (đã là `ImageRef` trên ổ), nháp ghi AI hay gốc nằm trong `ai_roots` (đã là ảnh AI), ảnh nằm ngay trong gốc (không có thư mục), ảnh tạo bằng AI. Tên file giữ như nháp vì tên file không đổi thẻ (`tags_for_image` nhận ảnh AI theo tên file mà không tách chữ hoa, cả ở bản T-070).
- Mỗi thư mục chỉ xem một lần cho cả nháp, kể cả khi lỗi (`:768`); `tag_store.resolve_many` vẫn chỉ gọi một lần.
- Nguồn ảnh vẫn theo hướng an toàn như lượt 1 (`_safe_tags`): AI nếu nháp ghi AI **hoặc** thẻ hiện tại (theo tên thật) nói AI **hoặc** gốc trong `ai_roots`. **`is_ai_name` chưa có trên `main`** (T-070 chưa gộp, `git grep is_ai_name origin/main` không ra gì) nên tên thư mục gốc chưa được tự kiểm trong `drafts.py`: ghi ở Đề xuất.

**SL-T055-2.** Chọn **cả hai**: thêm tiền tố **và** bỏ "đã duyệt" khi alt phải thêm tiền tố.

- Thêm tiền tố bằng đúng hàm của `alt.py`: `clean_suggestion(AltSuggestion(...), ai_generated=True, max_chars=MAX_ALT_CHARS, caption_max_chars=MAX_CAPTION_CHARS)` (`_ai_prefixed`, `:176`): bỏ tiền tố tự viết («Minh hoạ», «Ảnh minh họa»…), cắt thân theo ranh giới từ trong giới hạn lưu của nháp, ghi lại đúng một tiền tố chuẩn. Bỏ tiền tố rồi không còn chữ (alt chỉ là «minh họa») thì để trống.
- Lý do bỏ "đã duyệt": người dùng duyệt câu tả ảnh công trình thật; câu đã đổi (thêm «Minh họa») chưa ai đọc, và nội dung có thể không còn đúng cho ảnh minh họa. Nên alt ảnh AI **không bao giờ thiếu «Minh họa»** (kể cả lúc chưa duyệt), và người dùng phải duyệt lại.
- Alt, chú thích đã có tiền tố: giữ nguyên, vẫn "đã duyệt" (`test_ai_text_with_prefix_is_kept_and_stays_approved`). Ảnh thật: không đụng (`test_real_image_text_is_untouched`). Chú thích trống thì để trống.
- Hai chỗ: khi mở nháp (`clean_loaded`, `:655`) cho ảnh nháp ghi AI; và trong `check_draft_images` (`:944`) cho mọi ảnh mà thẻ cuối cùng nói AI (thư mục AI, thẻ sửa tay AI, gốc AI, tên thật trên ổ). Kết quả nằm ở `CheckedImage.image`.
- Không đổi `DraftImage(...)` lúc tạo (giao diện tự lưu khi người dùng đang gõ, tự sửa chữ lúc đó làm ô nhập nhảy chữ); giao diện phải dùng `clean_suggestion(ai_generated=True)` hay tiền tố khi người dùng duyệt alt ảnh AI (Đề xuất).

**SL-T055-3.** Chỉ đếm khi `chosen_image` khác `null` (`:407`). Trường hợp `schema_version` ghi dạng chữ/`true` (chỉ khi sửa tay) giữ như cũ: bỏ ảnh, hướng an toàn.

### Thay đổi so với lượt 1 (Lá Chắn xem)

- Lượt 1 ghi "kiểm ảnh không quét thư mục". Nay `check_draft_images` **có** gọi `ImageLibrary.list_folder` cho thư mục trên đường tới ảnh nháp ghi là ảnh thật (không đệ quy, `page_size=1`). Vẫn không mở file ảnh nào (`read_image_bytes` không được gọi), `list_folder` chỉ đọc tên và `stat` nên Drive "chỉ trực tuyến" không bị tải về, mọi đường đi vẫn qua `ImageLibrary` (chặn `..`, liên kết, ra ngoài gốc như T-048). Test lượt 1 `test_check_does_not_scan_or_read_files` đổi thành `test_check_reads_no_file_and_lists_only_folders_on_the_path` (kiểm đúng các thư mục được xem: `[(0, ""), (0, "CT012 - …")]`, không đệ quy, mỗi thư mục một lần; ảnh nháp ghi AI và gốc AI không xem) và thêm `test_scanned_images_need_no_folder_listing` (có `scanned` thì không gọi `list_folder`).
- `DraftStore.load` nay sửa alt, chú thích của ảnh nháp ghi AI (thêm tiền tố, bỏ "đã duyệt"). Mở rồi lưu lại vẫn ra đúng JSON (sau lần mở đầu): `test_opening_draft_that_says_ai_already_adds_prefix`. Test lượt 1 `test_save_load_save_is_stable` đổi alt ảnh AI mẫu thành alt đã có tiền tố (chữ độc vẫn giữ nguyên để kiểm bộ lọc).

### Bằng chứng (lượt 2)

Máy Windows 11 của chủ dự án, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055`.

```
$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py
    tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
    tests/test_images_folders.py tests/test_images_tags.py tests/test_app_pages.py
936 passed, 14 skipped in 275.39s (0:04:35)
(lượt Soi Lỗi trên 934c21b: 905 passed, 14 skipped, 7 xfailed. Nay 7 test xfail đã qua, thêm 24 test
 mới của tôi; 0 failed, 0 xfailed. 14 bỏ qua đều có từ trước, vì máy Windows này không cho tạo symlink
 hay test quyền kiểu POSIX: test_drafts_images.py:633, test_soi_loi_t016_t020.py:232/260/273/333,
 test_images_folders.py:62/368/381, test_images_tags.py:1346)

$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py   # sau commit đổi tên biến
283 passed, 1 skipped in 24.96s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/storage/drafts.py tests/test_drafts_images.py
    tests/test_soi_loi_t055.py
"results": {}

$ uvx bandit -q seo_app/storage/drafts.py
1 Low: B101 assert (assert saved.saved_at, có từ T-016, như lượt 1)
```

### Đối chiếu (lượt 2)

- [x] SL-T055-1: `test_sl_t055_1_case_variant_cannot_launder_ai_folder` (2 ca), `test_sl_t055_1_case_only_folder_rename_keeps_ai` (Soi Lỗi, đã gỡ `xfail`); của tôi: `test_case_variant_of_ai_folder_reads_real_name_and_stays_ai` (2 ca), `test_exact_folder_name_wins_on_case_sensitive_disk`, `test_single_case_insensitive_match_takes_real_name`, `test_unconfirmed_folder_name_is_unavailable` (3 ca), `test_folder_listing_error_is_reported_once_per_folder`, `test_image_in_root_needs_no_folder_listing`, `test_scanned_ref_becomes_the_key` (thêm kiểm tên thật, thẻ)
- [x] SL-T055-2: `test_sl_t055_2_approved_alt_of_ai_image_has_prefix` (3 ca, đã gỡ `xfail`); của tôi: `test_ai_image_text_gets_prefix_and_needs_review` (5 cách ảnh thành ảnh AI), `test_ai_text_with_prefix_is_kept_and_stays_approved`, `test_real_image_text_is_untouched`, `test_opening_draft_that_says_ai_already_adds_prefix`, `test_ai_text_prefix_edge_cases` (4 ca), `test_long_ai_alt_keeps_prefix_within_limit`
- [x] SL-T055-3: `test_sl_t055_3_v1_null_images_are_not_counted_as_dropped` (đã gỡ `xfail`), `test_v1_draft_counts_only_real_image_data_as_dropped`
- [x] Gỡ đủ 7 `xfail(strict=True)` khi XPASS, không đổi dòng `assert` nào của Soi Lỗi (`git diff 934c21b -- tests/test_soi_loi_t055.py` chỉ có dòng bị xóa)
- [x] Test liên quan qua, `ruff check .` sạch (phần Bằng chứng)

### Rủi ro và điểm cần chú ý (lượt 2)

- **Ảnh không dùng được** (USB chưa cắm, file mất): không xem được ổ nên thẻ vẫn đọc từ chữ trong nháp; nháp sửa tay `genai` trên USB đang rút sẽ hiện thẻ ảnh thật nhưng ảnh không dùng được (không đọc, không tải lên được). Cắm lại là kiểm đúng.
- **Thư mục rất lớn hay Drive chậm:** `list_folder` của thư mục gốc có thể xem tới 5.000 mục; quá thì ảnh báo "Chưa kiểm được tên thư mục…" cho tới khi giao diện truyền `scanned`. Chậm thêm một lần quét mỗi thư mục trên đường đi, chỉ cho ảnh chưa có trong `scanned`.
- `checked.ref` khi không có `scanned`: tên thư mục theo ổ, **tên file theo nháp** (có thể khác hoa thường với tên trên ổ). Đọc, kiểm vẫn đúng file; so ảnh nên dùng khóa không phân biệt hoa thường (`ref_key`), hoặc truyền `scanned`.
- `clean_suggestion` trên `main` (T-068 đã gộp) khác bản trên nhánh này ở vài ca biên (alt chỉ có dấu câu như «???»). Test của tôi tránh các ca đó; Chỉ Huy chạy lại `tests/test_drafts_images.py` sau khi gộp.

### Đề xuất (lượt 2)

- **T-056 (Họa Sĩ):** dùng `checked.image` (không dùng `snapshot.parts[i].chosen_image`) để hiện, duyệt, lưu lại alt/chú thích; truyền `scanned` khi đã quét thư mục chứa ảnh; hiện `checked.message` khi ảnh không dùng được. Khi người dùng duyệt alt của ảnh AI (hoặc bấm "đổi sang ảnh AI"), chạy `clean_suggestion(..., ai_generated=True)` trước khi lưu, để alt đã duyệt luôn có «Minh họa» ngay từ lúc lưu.
- **T-070 / T-056:** sau khi `is_ai_name` lên `main`, tính `ai_roots` bằng `is_ai_name(library.roots()[i].label)` khi gọi `check_draft_images` (hoặc phiếu nhỏ cho `drafts.py` tự tính). Lưu ý: `label` là chữ trong `IMAGE_FOLDERS` (người dùng gõ), có thể khác hoa thường với tên thật trên ổ, cùng loại lỗi SL-T055-1 ở tầng gốc.
- **T-048 (tùy Chỉ Huy):** nếu `stat_image` trả `ImageRef` theo tên thật trên ổ (trên Windows `resolve` đã cho tên thật khi kiểm tên 8.3, `folders.py:513-517`; trên Mac `resolve` giữ chữ đã gõ nên cần cách khác) thì `drafts.py` bỏ được bước xem thư mục.
- **Lá Chắn:** soát `_FolderNames` (`drafts.py:745`: chỉ đi qua `list_folder`, không ghép đường dẫn tuyệt đối, câu báo không có đường dẫn) và `_ai_wording` (`:307`) theo F1, C6.
- **Soi Lỗi:** chạy lại trên Mac (APFS không phân biệt hoa thường, tên NFD) và ổ phân biệt hoa thường; thử thư mục gốc hơn 5.000 mục.

## Lượt 3 (2026-10-21): sửa dữ liệu test sau T-070 (LC-T055-4)

Theo biên bản Lá Chắn `docs/team/reports/T-055-la-chan.md`: dòng LC-T055-4 và mục "Điều kiện" số 1. Nhánh `team/T-055` đã có `main` mới nhất (Chỉ Huy đưa vào ở `15a9726`). Số dòng trong mục này là số dòng **sau lượt 3**.

### Tóm tắt (cho chủ dự án)

- Phiếu T-070 (đã ở `main`) dạy app nhận tên thư mục "genai" là ảnh AI, viết hoa hay thường đều vậy. Test của phiếu này lại dùng "genai" làm ví dụ cho tên **không** phải ảnh AI. Vì thế, trên nhánh đã có `main`, 1 test của tôi hỏng, và 2 test khác vẫn qua nhưng không còn kiểm đúng điều cần kiểm. Code của app vẫn đúng.
- Tôi đổi ví dụ sang "CongAI" (là ảnh AI, vì chữ "AI" viết hoa đứng tách ra) và "congai" (không phải ảnh AI). Đầu mỗi test có thêm một câu kiểm lại ví dụ: nếu sau này app đổi cách nhận tên làm ví dụ sai đi, test báo hỏng ngay chứ không lặng lẽ qua.
- Chỉ sửa file test, không sửa code của app.
- Test của tôi qua hết. Còn đúng 1 test hỏng, ở file của Soi Lỗi (`test_sl_t055_1_case_only_folder_rename_keeps_ai`), cùng nguyên nhân. Theo lời giao, Soi Lỗi sửa file đó sau tôi.

### Đã thay đổi (lượt 3)

| File | Thay đổi |
|---|---|
| `tests/test_drafts_images.py` | Đổi cặp tên thử `GenAI`/`genai`/`GENAI` sang `CongAI`/`congai`/`CONGAI` ở 4 test (7 ca). Thêm hàm kiểm điều kiện đầu `assert_ai_only_by_case` (`:886`), gọi ở đầu cả 4 test. Import thêm `tags_for_image`. Sửa chú thích của `CAMEL_AI_PATH` (`:881-883`) |
| `docs/team/reports/T-055-tho-may.md` | Mục này, dòng "Kết quả" ở đầu báo cáo |

Không sửa `seo_app/**`, không sửa `tests/test_soi_loi_t055.py` hay test nào khác (`git diff --stat`: chỉ 2 file trên).

### Kiểm cặp tên trước khi dùng

Chạy `tags_for_image(ImageRef(0, …))` và `is_ai_name(…)` trên nhánh hiện tại (đã có T-070), bằng script tạm trong thư mục nháp của phiên (không commit):

| Tên thư mục (trong `CT012 - Cổng inox - Tân Phú/…/cong.png`) | Ảnh AI | Thẻ |
|---|---|---|
| `CongAI` | có (tách chữ hoa: "Cong AI") | `ai`, không mã công trình, không khu vực; hạng mục "Cổng" |
| `congai`, `Congai`, `CONGAI` | không | `that`, `CT012`, `Tân Phú`, "Cổng inox" |
| `GenAI`, `genai`, `Genai`, `GENAI` | có, cả 4 kiểu | `ai`: đây là lý do phải đổi |

`is_ai_name`: `CongAI` → đúng; `congai`, `Congai`, `CONGAI` → sai. Ghi chú: ảnh trong `CongAI` có hạng mục "Cổng" (chữ "Cong" khớp vật "Cổng", thư mục sâu hơn được ưu tiên), không phải "Cổng inox" như ảnh trong `GenAI`. Test của tôi không kiểm hạng mục của ảnh này nên không ảnh hưởng; Soi Lỗi nên biết khi đổi `test_soi_loi_t055.py`.

### Từng test

| Test | Trước (nhánh đã có `main`) | Sau |
|---|---|---|
| `test_case_variant_of_ai_folder_reads_real_name_and_stays_ai` (2 ca, `:904`) | Qua, nhưng phần "vẫn là ảnh AI, alt có «Minh họa»" qua oan: chữ `genai` trong nháp tự là ảnh AI | Trên ổ `CongAI`, nháp ghi `congai`: chỉ ra ảnh AI khi thẻ đọc theo tên trên ổ. Câu điều kiện đầu đặt **trước** bước bỏ qua (`skip`) nên chạy cả trên ổ phân biệt hoa thường |
| `test_exact_folder_name_wins_on_case_sensitive_disk` (`:943`) | **Hỏng** (`assert not result.is_ai`: `genai` nay là ảnh AI) | Ổ có cả `CongAI` lẫn `congai`, nháp ghi `congai`: ra đúng thư mục `congai`, ảnh thật |
| `test_single_case_insensitive_match_takes_real_name` (`:953`) | Qua, phần `is_ai` qua oan | Ổ có `CongAI`, nháp ghi `congai`: ra `CongAI`, ảnh AI |
| `test_unconfirmed_folder_name_is_unavailable` (3 ca, `:966`) | Qua | Nháp ghi `congai`; ca "hai tên cùng khóa" là `CongAI`/`CONGAI`. Câu điều kiện đầu ghi rõ lý do không được đoán: đoán theo chữ trong nháp là ra ảnh thật |

Các câu `assert` cũ giữ nguyên, chỉ đổi chữ trong dữ liệu (`genai/cong.png` → `congai/cong.png`…). Ví dụ `GenAI`/`genai` ở mục "Lượt 2" phía trên là theo nhánh trước khi có T-070; nay ứng với `CongAI`/`congai`.

### Thử đột biến (test có kiểm đúng ý không)

Plugin pytest tạm trong thư mục nháp của phiên (không commit, không sửa file nào của repo) làm hỏng cách sửa SL-T055-1 ngay trong bộ nhớ, rồi chạy `tests/test_drafts_images.py`. Số test hỏng càng nhiều càng tốt (test bắt được lỗi):

| Đột biến | Trước khi sửa | Sau khi sửa |
|---|---|---|
| Không xem tên thật (`_FolderNames.real_ref` trả nguyên chữ nháp, như thử của Lá Chắn) | 10 hỏng, trong đó 1 là test vốn đã hỏng | 9 hỏng, đều bắt đúng |
| Bỏ bước "trùng hẳn trước" (lấy luôn tên trùng không phân biệt hoa thường đầu tiên) | 2 hỏng, trong đó 1 là test vốn đã hỏng | 2 hỏng, đều bắt đúng |
| `ref` theo tên trên ổ nhưng **thẻ theo chữ trong nháp** (đúng lỗi SL-T055-1) | 1 hỏng, chính là test vốn đã hỏng: **không test nào bắt được** | **3 hỏng** (`test_case_variant…` ×2, `test_single_case…`) |
| Luật nhận tên đổi: thêm `congai` là ảnh AI (như T-070 đã làm với `genai`) | không áp dụng | 7 hỏng, cả 7 ở câu điều kiện đầu (`:891`) |
| Không đột biến | 1 hỏng | 0 hỏng |

### Bằng chứng (lượt 3)

Máy Windows 11 của chủ dự án, Python 3.12, worktree `wt-T-055`, nhánh `team/T-055` (đầu nhánh trước lượt 3: `15a9726`). Có 2 agent khác chạy song song trên máy.

```
$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py      # trước khi sửa
FAILED tests/test_drafts_images.py::test_exact_folder_name_wins_on_case_sensitive_disk
FAILED tests/test_soi_loi_t055.py::test_sl_t055_1_case_only_folder_rename_keeps_ai
2 failed, 298 passed, 1 skipped, 4 xfailed in 24.53s

$ uv run pytest tests/test_drafts_images.py                                  # sau khi sửa
173 passed, 1 skipped in 10.21s

$ uv run pytest tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py
    tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
    tests/test_images_folders.py tests/test_images_tags.py tests/test_app_pages.py
FAILED tests/test_soi_loi_t055.py::test_sl_t055_1_case_only_folder_rename_keeps_ai
1 failed, 1067 passed, 14 skipped, 4 xfailed in 165.09s (0:02:45)
(Lá Chắn trên cây gộp: 2 failed, 1066 passed, 14 skipped, 4 xfailed. Test hỏng còn lại thuộc file
 của Soi Lỗi, chờ Soi Lỗi sửa; không phải hỏng vì quá giờ. 14 bỏ qua như lượt 2, đều vì máy Windows
 này không cho tạo symlink hay test quyền kiểu POSIX. 4 xfailed là SL-T055-4 ×3, SL-T055-5, có từ
 lượt 2 của Soi Lỗi)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_drafts_images.py
"results": {}
```

### Đối chiếu (lượt 3, điều kiện 1 của Lá Chắn)

- [x] Đổi cặp tên thử sang cặp chỉ là ảnh AI nhờ tách chữ hoa (`CongAI` / `congai` / `CONGAI`), đã kiểm bằng `tags_for_image` trên nhánh hiện tại trước khi dùng
- [x] Thêm `assert` điều kiện đầu (`tags_for_image(tên trên ổ).tags.is_ai and not tags_for_image(tên trong nháp).tags.is_ai`) cho các test SL-T055-1 (kèm phần SL-T055-2 "alt có «Minh họa»") trong file của tôi
- [x] Không đổi điều kiện kiểm của test nào, không sửa code ứng dụng, không sửa `tests/test_soi_loi_t055.py`
- [ ] 9 file test liên quan qua hết trên nhánh: **còn 1 test hỏng ở file của Soi Lỗi**, chờ Soi Lỗi sửa (mục dưới)

### Còn lại cho Soi Lỗi (`tests/test_soi_loi_t055.py`)

- `test_sl_t055_1_case_only_folder_rename_keeps_ai` (`:479`) vẫn hỏng: `assert picked.source == SOURCE_REAL` (`:487`), vì `Genai` nay là ảnh AI ngay từ lúc chọn. Cặp thay thế: chọn ảnh khi thư mục tên `Congai` (ảnh thật), rồi đổi tên thành `CongAI`.
- 4 test Lá Chắn nêu là qua oan cũng nằm trong file này: `test_sl_t055_1_case_variant_cannot_launder_ai_folder` (×2, `:465`), `test_prefixed_alt_never_loses_approval[thu-muc-AI-hoa-thuong]`, `test_prefix_is_not_repeated_over_many_save_open_cycles`. Các chỗ khác dùng `CAMEL_AI_PATH`/`GENAI_VARIANT` (`:62`, `:723`) cũng nên đổi cùng lúc.
- Lưu ý: ảnh trong `CongAI` có hạng mục "Cổng" chứ không phải "Cổng inox" (bảng "Kiểm cặp tên" ở trên).

### Đề xuất (lượt 3)

- **Phiếu dọn ở điều kiện 3 của Lá Chắn** (có đụng `drafts.py`): docstring của `_FolderNames` (`seo_app/storage/drafts.py:748-751`) còn ghi `"GenAI"` là ảnh AI còn `"genai"` thì không. Sau T-070 câu này sai. Lượt này chỉ được sửa dữ liệu test nên tôi không sửa; nên đổi sang `CongAI`/`congai` trong phiếu đó.

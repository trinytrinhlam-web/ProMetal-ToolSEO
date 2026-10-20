# Báo cáo T-070 · Dọn lỗi thẻ ảnh (sau T-052)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-070](../tickets/T-070-don-loi-the-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành (yêu cầu 4 để nguyên vì chủ dự án chưa quyết, đúng phiếu) |

## Tóm tắt (cho chủ dự án)

App nhận ra ảnh AI từ tên thư mục và tên file tốt hơn: các cách gọi hay gặp như "Ảnh minh họa", "trí tuệ nhân tạo", "genai", và tên các công cụ tạo ảnh phổ biến (Copilot, Designer, Leonardo, Ideogram, Flux, Grok, Kling, Dreamina, ComfyUI, Runway, Krea, Seedream, Canva…) nay đều làm ảnh được coi là **ảnh AI**, nên không bị giới thiệu như công trình thật. Tên khách có chữ giống "AI" nhưng có dấu (Thái, Mai, Ái, Minh Hòa) vẫn là ảnh thật. Có thêm hàm `is_ai_name` để màn hình chọn ảnh (T-056) kiểm cả tên thư mục gốc.

File nhớ thẻ sửa tay (`data/image_tags.sqlite`) nay được kiểm cấu trúc trước khi đọc: file bị làm độc không còn làm treo app, file bị thay khi đang chạy được nhận ra rồi tự đổi tên sang một bên (giữ lại) và tạo file mới. File thẻ cũ do bản T-052 tạo vẫn dùng bình thường.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/tags.py` | Thêm công cụ AI (`_AI_TOOLS`, `:203`), cụm tiếng Việt (`_AI_PHRASES`, `:259`), dạng viết liền và tên file `OIG…` (`_AI_JOINED`, `:271`); dấu hiệu tự có dạng không dấu và dạng viết liền (`_build_ai_markers`, `:444`); hàm công khai `is_ai_name` (`:933`) |
| `seo_app/storage/image_tags.py` | Kiểm `sqlite_master` khớp đúng trước mọi truy vấn (`_expected_schema` `:514`, `_app_tables` `:531`, `_is_healthy` `:549`), kiểm lại ở mỗi lần mở (`_connect` `:383`); giới hạn số bước SQLite (`_guard` `:497`, `_MAX_VM_STEPS` `:70`); đặt lại `_ready` với mọi lỗi trừ bận/khóa (`:388`); `get_many` ép ảnh AI theo từng ảnh được hỏi (`:250`) |
| `tests/test_images_tags.py` | Thêm 115 ca test T-070 (danh sách ở phần Bằng chứng) |
| `tests/test_soi_loi_t052.py` | Chỉ gỡ 3 khối `@pytest.mark.xfail(...)` của SL-T052-9, -10, -11 (24 dòng xóa, 0 dòng thêm); không đổi thân test hay điều kiện kiểm |
| `docs/team/reports/T-070-tho-may.md` | Báo cáo này |

Không sửa `folders.py`, `process.py`, `alt.py`, `naming.py`, `seo_app/storage/drafts.py`, `app/**`, `config/**`, `tests/conftest.py`. Không thêm thư viện. `git diff --stat origin/main...HEAD`: chỉ 4 file code/test ở trên (+ báo cáo).

## Yêu cầu 1 · Dấu hiệu ảnh AI (LC-T052-1 a–e, SL-T052-11)

### Danh sách dấu hiệu cuối cùng

Tìm ở **mọi chỗ** trong tên mọi thư mục bên dưới gốc và trong tên file ảnh (như T-052). So không phân biệt hoa thường, **có phân biệt dấu** (để "Ái", "Thái", "Hòa" không thành AI); mỗi dấu hiệu tự có thêm dạng không dấu và dạng viết liền.

| Nhóm | Dấu hiệu | Từ đâu |
|---|---|---|
| Chữ AI | `AI`, `A.I.`, `ảnh AI`, `hình AI`, `AI tạo`, `ảnh AI tạo`, `tạo bằng AI`, `ảnh tạo bằng AI`, `minh họa AI`, `ảnh minh họa AI`, `AI generated` | T-052 |
| Công cụ (T-052) | Gemini, Imagen, Nano Banana, Midjourney, DALL-E, DALLE, ChatGPT, GPT, Stable Diffusion, SDXL, Firefly | T-052 |
| Công cụ (phiếu yêu cầu) | **Copilot, Designer, Bing Image Creator, Leonardo, Ideogram, Flux, Grok, Kling, Dreamina, ComfyUI, Runway, Krea, Seedream, Canva** | T-070 |
| Công cụ (thêm ngoài phiếu) | `Bing` đứng riêng, `Image Creator`, Jimeng (Dreamina bản Trung Quốc), Recraft, NightCafe, SeaArt, Hailuo, Sora | T-070 |
| Cụm tiếng Việt | **`minh họa`, `minh hoạ`** (dấu kiểu cũ), **`trí tuệ nhân tạo`**; thêm ngoài phiếu: `phối cảnh` (ảnh dựng 3D), `render`, `do máy tạo`, `tạo tự động` | T-070 |
| Viết liền / tên file | **`GenAI`** (cả `genai`, `GENAI`), `AI image(s)`, `AI art`, `OIG`, `OIG1`–`OIG4` (tên file của Bing Image Creator/Copilot); dạng viết liền tự sinh: `anhai`, `hinhai`, `minhhoa`, `trituenhantao`, `stablediffusion`, `bingimagecreator`… | T-070 |

Cụm tiếng Việt **chỉ là dấu hiệu**, không vào danh sách "khớp trọn" (danh sách đó so không dấu): nếu vào, thư mục "Minh Hòa" (tên người, có dấu) bỏ dấu ra "minh hoa" sẽ thành AI.

**Canva: coi là ảnh AI.** Lý do: ảnh làm trên Canva là ảnh thiết kế (banner, ảnh ghép, có thể tạo bằng Magic Media/Dream Lab của Canva), không phải ảnh chụp công trình; tả nó như công trình thật ở Quận 7 là sai. Coi là AI là hướng an toàn Lá Chắn khuyên (chỉ mất thẻ công trình). Ảnh thật chỉ thêm logo trên Canva thì để ở thư mục công trình với tên gốc. Xem câu hỏi cuối báo cáo.

### Đánh đổi có chủ ý (ghi rõ theo phiếu)

| Tên | Kết quả | Vì sao / cách xử lý |
|---|---|---|
| "Nhà anh Thái", "chị Mai", "Nhà chị Ái", "anh Hải", "Thai", "anh Hai", "Mai Anh" | **Ảnh thật** | Không trùng dấu hiệu nào (so có dấu; "mai", "thai", "hai" không phải dấu hiệu) |
| "Minh Hòa", "Minh Hoà", "Bình Minh", "Thanh Hóa", "Khánh Hòa", "Hòa Bình" | **Ảnh thật** | Có dấu nên khác "minh họa" |
| "Phôi cánh cổng" (có dấu), "Cổng tự động", "Mái tôn", "Cty Home Design" | **Ảnh thật** | Khác dấu hiệu |
| "Cty Home **Designer**" (tên công ty khách) | **Ảnh AI** | "Designer" là tên Microsoft Designer (tên file mặc định `Designer (3).png`). Không chắc thì nghiêng về AI: ảnh chỉ mất mã CT, khu vực, trước/sau, không lộ chữ. Muốn giữ thẻ: đổi tên thư mục (ví dụ "Cty Home Design") |
| "Nha anh Minh Hoa" (gõ **không dấu**) | **Ảnh AI** | Không dấu thì không phân biệt được "Minh Hòa" với "minh họa". Cách xử lý: gõ có dấu |
| "Phoi canh cong" (không dấu, = "phôi cánh cổng") | **Ảnh AI** | Trùng "phối cảnh" không dấu. Gõ có dấu thì thật |
| "Thuốc hàn Flux" | **Ảnh AI** | "Flux" là tên mô hình tạo ảnh. Hiếm gặp trong tên thư mục ảnh công trình |
| "Nha chi Ai", "Lô A, I", "Gemini Tower" | Ảnh AI (như T-052) | Đã ghi ở T-052 |

Test: `test_t070_real_names_are_not_mistaken_for_ai` (18 tên, kiểm cả tên thư mục và tên file), `test_t070_ambiguous_names_lean_to_ai_and_leak_nothing` (4 tên, kiểm không chữ nào của tên đi ra).

### Không nhận được bằng tên (cần ghi README T-069 / nhận theo nội dung về sau)

Tên file mặc định không chứa tên công cụ: Midjourney (`tenngười_câu-lệnh_mã.png`), Bing Image Creator bản tải về (`_<mã ngẫu nhiên>.jpeg`), Stable Diffusion A1111 (`00001-1234567890.png`), Leonardo bản cũ (`Default_….jpg`). Những ảnh này chỉ được nhận là AI khi nằm trong thư mục có tên dấu hiệu (ví dụ `Ảnh AI`).

### `is_ai_name(name) -> bool` (LC-T052-1 e, cho T-056)

`seo_app/images/tags.py:933`. Nhận `str` hoặc `os.PathLike`; nhận đường dẫn thì chỉ xét **tên cuối** (`"G:/My Drive/Ảnh AI"` → `True`, `"G:/AI/Ảnh công trình"` → `False`); kiểu khác (`None`, `bytes`, `ImageRef`) → `TypeError`. Cùng cách nhận với thư mục bên dưới gốc (test `test_is_ai_name_agrees_with_folder_tags`). Chỉ trả đúng/sai, không đọc ổ đĩa (test chặn `open`, `os.stat`, `os.scandir`…).

## Yêu cầu 2 · Kho thẻ chịu file độc (LC-T052-2, SL-T052-9, SL-T052-10)

- **Kiểm `sqlite_master` khớp đúng, trước mọi truy vấn khác** (`_app_tables`, `image_tags.py:531`): chỉ được có bảng `manual_tags`, `info` và chỉ mục tự sinh của khóa chính. Câu `CREATE TABLE` mong đợi được dựng bằng chính `_CREATE_TABLES` của app trong một SQLite trong bộ nhớ (`_expected_schema`, `:514`), nên khớp đúng cách SQLite ghi lại câu lệnh, không phụ thuộc phiên bản. Bảng chưa có thì được (file mới, tạo dở); có thêm bất cứ thứ gì (khung nhìn, trigger, bảng ảo, `WITHOUT ROWID`, `CHECK`, cột sinh, kiểu cột khác, chỉ mục, bảng lạ) thì coi là hỏng → đổi tên sang một bên (giữ nguyên nội dung) và tạo file mới. Đọc `sqlite_master` chỉ phân tích câu lệnh, không chạy khung nhìn hay trigger. `quick_check` chạy **sau** bước này (vì `quick_check` có kiểm `CHECK`, cột sinh).
- **Kiểm lại ở mỗi lần mở** (`_connect`, `:383`, tốn khoảng 1 ms): file bị thay khi app đang chạy bị bắt **trước** lệnh ghi, nên trigger độc không kịp chạy; lần mở đó báo lỗi tiếng Việt, lần sau tự đổi tên file lạ.
- **Đặt lại `_ready`** (`:388`): mọi lỗi SQLite trừ bận/khóa (thiếu bảng/cột, hỏng, quá số bước) → lần sau kiểm lại file. Thiếu bảng thì tạo lại bảng thiếu, **không mất** thẻ còn trong file (test `test_t070_missing_table_while_running_recovers_without_losing_tags`).
- **`set_progress_handler`** (`_guard`, `:497`), ở cả 3 chỗ mở file: dừng truy vấn chạy quá `_MAX_VM_STEPS = 50.000.000` bước (lớp phòng thứ hai, cho khe giữa lúc kiểm và lúc đọc nếu một chương trình khác sửa file đúng lúc đó). Đo trên máy Windows này (Python 3.12.15, SQLite 3.53.1): việc nặng nhất của file hợp lệ (`quick_check`, liệt kê, lưu kèm dọn thẻ cũ trên file 60.000 dòng, 176 MB, gấp gần ba lần giới hạn 64 MB) tốn dưới 2,1 triệu bước; truy vấn đệ quy vô hạn chạy khoảng 26 triệu bước/giây → bị dừng sau khoảng 2 giây. Kiểm file mà quá số bước thì coi là hỏng (đổi tên, giữ lại). Test `test_t070_step_limit_leaves_room_for_the_largest_real_file` chạy file đủ 20.000 thẻ với **một phần mười** giới hạn: vẫn qua.
- File do bản T-052 tạo (cùng câu `CREATE TABLE`) vẫn được nhận, không bị đổi tên (`test_t070_file_made_by_t052_is_still_accepted`, câu lệnh T-052 chép cứng trong test để ai sửa `_CREATE_TABLES` sau này sẽ thấy đỏ).

14 kiểu file độc trong test (`HOSTILE_FILES`, `tests/test_images_tags.py:1695`), mỗi kiểu thử hai lúc: có sẵn trước khi mở và thay vào khi app đang chạy: `info` là khung nhìn đệ quy; `manual_tags` là khung nhìn đệ quy; khung nhìn trỏ bảng không có; trigger chạy truy vấn đệ quy; trigger sửa dữ liệu; `WITHOUT ROWID`; bảng ảo `fts5`; `CHECK`; cột sinh; kiểu cột khác; chỉ mục thêm; chỉ mục biểu thức; bảng lạ kèm theo; chỉ có bảng lạ (SL-T052-10). Truy vấn đệ quy trong test có giới hạn và test hạ giới hạn số bước, nên lớp kiểm mà hỏng thì test đỏ nhanh chứ không treo.

**Thử "làm hỏng" để chắc test không qua oan:** chạy riêng (không sửa file) với `_app_tables` bị thay bằng bản chỉ kiểm tên bảng: **28/28 ca file độc đỏ**, cả lượt chạy xong trong 3 giây (lớp giới hạn số bước vẫn chặn được treo).

## Yêu cầu 3 · `get_many` ép ảnh AI theo ảnh được hỏi (LC-T052-3)

`image_tags.py:250`: mỗi `ref` được hỏi đều qua `_keep_ai(…, tags_for_image(ref).tags)` (chỉ tính cho ảnh có thẻ sửa tay). Test `test_t070_get_applies_ai_rule_to_the_ref_asked`: thẻ "ảnh thật, CT012, Quận 7" lưu cho `…/khoai/x.png` ("khoai" là củ khoai, ảnh thật); hỏi bằng `…/KhoAI/x.png` (cùng khóa vì không phân biệt hoa thường, nhưng "Kho AI" là ảnh AI) → `get`, `get_many`, `resolve` đều trả ảnh AI, chỉ giữ hạng mục. Ca `genai`/`GenAI` của Lá Chắn (T12) nay cả hai đều là AI nên không còn khác nhau; tôi dùng `khoai`/`KhoAI` thay.

## Yêu cầu 4 · LC-T052-5 (để nguyên)

Chủ dự án **chưa quyết** giữa (a) ghi sổ rủi ro, mở rộng dòng LC-T048-6 cho file trong `data/` (Lá Chắn khuyên), và (b) `PRAGMA journal_mode = MEMORY`. Theo phiếu, tôi **để nguyên** (vẫn dùng file nhật ký `-journal` mặc định; liên kết ở `-journal`, `-wal`, `-shm` vẫn được gỡ ở mỗi lần mở như T-052). Nếu chọn (b): đổi một dòng trong `_connect` và `_prepare`, kèm test; khe vài mili giây ở chính file `.sqlite` vẫn còn ở cả hai cách.

## Yêu cầu 5 · Gỡ `xfail`

SL-T052-9, -10, -11 báo XPASS → gỡ đúng 3 khối `@pytest.mark.xfail(...)`, không đổi thân test (`git diff origin/main -- tests/test_soi_loi_t052.py`: 24 dòng xóa, 0 dòng thêm). `tests/test_soi_loi_t052.py` nay không còn `xfail` nào.

## Bằng chứng

Máy Windows 11 Pro, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-070`, nhánh `team/T-070`. Chỉ chạy test liên quan (theo `rules.md`); toàn bộ test do Chỉ Huy chạy khi gộp.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx
(2026-10-20 17:46–17:47 +07, bản cuối, sau khi định dạng lại test)
861 passed, 8 skipped in 54.46s

$ uv run ruff check .
All checks passed!
```

- **0 hỏng, 0 xfail.** 8 bỏ qua có lý do: 2 ca symlink của T-052 (`tests/test_images_tags.py:1540`, `tests/test_soi_loi_t052.py:538`, Windows chưa bật Developer Mode) + 6 ca của T-048 (`tests/test_images_folders.py:62` ×4, `:368`, `:381`).
- Test mới trong `tests/test_images_tags.py` (115 ca): `test_t070_more_ai_folder_names_make_whole_branch_ai` (33 tên thư mục, mỗi tên thử ở hai tầng), `test_t070_default_file_names_of_ai_tools_make_image_ai` (23 tên file), `test_t070_real_names_are_not_mistaken_for_ai` (18), `test_t070_ambiguous_names_lean_to_ai_and_leak_nothing` (4), `test_is_ai_name_checks_last_name_only_and_returns_bool`, `test_is_ai_name_agrees_with_folder_tags`, `test_t070_health_check_rejects_files_the_app_never_makes` (14), `test_t070_file_swapped_while_running_is_caught_then_replaced` (14), `test_t070_missing_table_while_running_recovers_without_losing_tags`, `test_t070_file_made_by_t052_is_still_accepted`, `test_t070_schema_is_read_before_any_other_query`, `test_t070_query_running_too_long_is_stopped_not_hung`, `test_t070_health_check_running_too_long_counts_as_broken`, `test_t070_step_limit_leaves_room_for_the_largest_real_file`, `test_t070_get_applies_ai_rule_to_the_ref_asked`.
- Test cũ của T-052 (cả của Soi Lỗi) qua nguyên, không sửa điều kiện nào.

## Đối chiếu tiêu chí xong

- [x] YC1: dấu hiệu AI mới + `is_ai_name` + test thư mục, tên file, đối chứng (`tags.py:203`, `:259`, `:271`, `:933`; các test `test_t070_*_ai*`, `test_is_ai_name_*`; SL-T052-11 qua)
- [x] YC2: `sqlite_master` khớp đúng trước mọi truy vấn, đặt lại `_ready`, `set_progress_handler`; test khung nhìn, trigger, `WITHOUT ROWID` và 11 kiểu khác (`image_tags.py:497–575`; SL-T052-9, -10 qua)
- [x] YC3: `get_many` áp `_keep_ai` theo từng `ref`; test đổi tên chỉ khác hoa thường (`image_tags.py:250`)
- [x] YC4: để nguyên, ghi ở trên (chờ chủ dự án)
- [x] YC5: gỡ 3 `xfail` khi XPASS, không đổi điều kiện kiểm
- [x] Test liên quan qua, `ruff check .` sạch, báo cáo đã nộp

## Rủi ro và điểm cần chú ý

- **Nhận ảnh AI vẫn chỉ dựa vào tên.** Ảnh AI đặt trong thư mục công trình với tên file không có tên công cụ (Midjourney, Bing tải về, A1111) vẫn là "ảnh thật". Lớp chặn cuối vẫn là người duyệt ở T-056.
- **Nhận nhầm ảnh thật thành AI nhiều hơn T-052** (Designer, Canva, Flux, Bing, render, tên không dấu "Minh Hoa"/"Phoi canh"): hướng an toàn, ảnh chỉ mất thẻ công trình; nhưng `ImageTagStore.set` **không cho** đổi ảnh trong thư mục AI thành ảnh thật (từ T-052), nên người dùng phải đổi tên thư mục. T-056 nên nói rõ lý do.
- **Giới hạn số bước** là ngưỡng đo trên một máy; máy chậm hơn thì file độc bị dừng sau lâu hơn (vài giây), file thật vẫn còn dư hơn 20 lần. File có hơn khoảng 2 triệu dòng (app chỉ giữ 20.000) sẽ bị coi là hỏng và đổi tên (giữ lại).
- **Khe còn lại:** một chương trình khác sửa cấu trúc file đúng giữa lúc app kiểm và lúc app đọc (trong cùng một kết nối) thì chỉ còn lớp giới hạn số bước chặn (không treo, chỉ báo lỗi một lần). LC-T052-5 (file `-journal`) vẫn như cũ.
- Ca symlink vẫn chưa chạy trên máy này (điều kiện T-063).

## Đề xuất

- **Soi Lỗi (rút gọn):** thử thêm tên ảnh AI và tên khách thật theo thói quen đặt tên của chủ dự án; thử file độc kiểu khác (WAL dựng sẵn, `sqlite_master` sửa bằng `writable_schema`); xác nhận 3 `xfail` gỡ đúng (chỉ dòng `xfail`).
- **Lá Chắn (rút gọn, A3, F1, F3):** soát cách so `sqlite_master` (`_app_tables`, so cả loại, tên, bảng, câu lệnh), ngưỡng `_MAX_VM_STEPS`, và quyết định Canva/Designer.
- **T-056:** lấy thẻ bằng `resolve`/`resolve_many` (không dùng `get`); gọi `is_ai_name(tên thư mục gốc)` và coi mọi ảnh trong gốc đó là ảnh AI (hoặc cảnh báo ở Cài đặt); hiện lý do "tên thư mục hoặc tên file có chữ AI / tên công cụ tạo ảnh"; chỉ hiện `recovered_from.name`; thêm fixture `conftest.py` trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (điều kiện Lá Chắn T-052 số 2).
- **T-069 (README):** liệt kê các chữ làm ảnh thành ảnh AI; dặn để ảnh AI trong thư mục `Ảnh AI`; dặn gõ tên thư mục ảnh thật **có dấu** và tránh chữ Designer, Canva, Flux, render, "phối cảnh".
- **Về sau:** nhận ảnh AI theo nội dung (C2PA, EXIF `Software`), lập phiếu riêng khi có thời gian.

## Câu hỏi cho chủ dự án

1. LC-T052-5: **(a)** ghi sổ rủi ro (đề xuất, như Lá Chắn khuyên) hay **(b)** đặt `PRAGMA journal_mode = MEMORY`?
2. Ảnh trong thư mục hay có tên file chứa chữ "Canva" có coi là ảnh AI không? Đề xuất: **Có** (đã làm như vậy; trả lời "Không" thì bỏ một dòng trong `_AI_TOOLS`).

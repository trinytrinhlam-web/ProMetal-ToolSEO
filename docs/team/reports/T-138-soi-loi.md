# Báo cáo T-138 · Tạm dùng Gemini Flash cho mọi việc AI · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-138](../tickets/T-138-tam-dung-gemini-flash.md) · báo cáo Thợ Máy [`T-138-tho-may.md`](T-138-tho-may.md) |
| Nhánh | `team/T-138` đầu `d82ad6d` (gốc `main` `3202035`). Gộp thử `main` cục bộ `756941c` (đã có dòng sổ rủi ro ngày 18/11): **không xung đột** (`git merge-tree`, cây `f5bc821`); `app/`, `seo_app/`, `tests/`, `config/`, `README.md`, `pyproject.toml`, `uv.lock` của cây gộp **y hệt** nhánh (`main` chỉ đổi tài liệu) |
| Ngày nộp | 2026-11-18 (giao 13:37, xong 15:16, +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T138-1 → -3, đều là chữ hướng dẫn; SL-T138-1 **bắt buộc** sửa ở lượt 2). Cả bốn trọng tâm Chỉ Huy giao: **đúng**. (1) R5: không ca nào thành test rỗng; 23 đột biến phá điều bảo vệ: ở 21 đột biến ca mới bắt bằng hoặc hơn ca cũ (K1b tương đương, sống ở cả hai bên); 2 chỗ ca mới kiểm ít hơn ca cũ (G-1, G-2), tôi đã thêm ca bù. (2) Tắt tìm web: bài đối thủ AI trả về bị bỏ **ở code**, không tới trang, dàn ý, bài, file nháp; bật tìm web: lời dặn giống hệt `main` từng chữ. (3) Fixture tách `data/` thật sự ăn: lô 98 file có WordPress giả chạy ngay trong worktree, 10.730 qua, 0 hỏng; móc kiểm ghi lại **0** lần đụng `data/`, không có thư mục `data/` sau lượt. (4) `config/ai.toml` đọc được, 9 việc `gemini-3.8-flash`, nghiên cứu `web_search = false`. 4 ghi nhận, không chặn |

## Tóm tắt (cho chủ dự án)

- Phần mềm dùng Gemini Flash miễn phí cho mọi việc AI. Khi không tìm được Google, bước **Chuẩn bị** không còn danh sách «bài đối thủ».
  - Tôi thử cả trường hợp AI không nghe lời, vẫn tự bịa một bài đối thủ. Phần mềm bỏ bài đó: không hiện trên trang, không đưa vào dàn ý, bài viết hay bản nháp đã lưu.
  - Khi bật lại tìm Google (Claude, hoặc Gemini trả phí), mọi thứ chạy như trước, lời dặn AI giống hệt bản cũ.
- Bộ kiểm thử của đội không còn ghi vào thư mục `data` của phần mềm. Tôi chạy 98 file kiểm thử có website giả và theo dõi từng lần ghi file: 0 lần đụng tới `data`.
- Còn 3 chỗ chữ cần sửa (không ảnh hưởng dữ liệu):
  1. **README mục 7.2** vẫn ghi việc viết alt dùng Claude Sonnet và dặn «báo Chỉ Huy để ghi sổ rủi ro trước». Anh/chị đã chấp nhận dùng Gemini miễn phí cho việc viết alt (18/11, đã ghi sổ rủi ro), nên README phải ghi đúng. Việc này bắt buộc ở lượt 2.
  2. Ghi chú «quay lại Claude» (đầu file `config/ai.toml` và README) thiếu một bước: bật lại tìm Google (`web_search = true` ở bước nghiên cứu). Làm đúng ghi chú hiện tại thì Claude vẫn không tìm Google.
  3. Bước **Chuẩn bị** còn một khung chữ nói AI «đọc các bài đứng đầu Google», và sau khi phân tích còn một khung «Các bài đứng đầu Google còn thiếu gì?» để trống, ngay dưới dòng nhắc «Đang tắt tìm Google».

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t138.py` | Mới: 9 ca. 6 qua; 3 `xfail(strict=True)` ghim SL-T138-1 → -3 (mục 7) |
| `docs/team/reports/T-138-soi-loi.md` | Báo cáo này |

Không sửa mã, cấu hình, README hay test của Thợ Máy; không commit file phiếu.

## 1. Trọng tâm 1 — R5: 22 ca đổi kỳ vọng còn kiểm đúng điều bảo vệ cũ không

**Cách thử.** Hai bản sao trong thư mục nháp của phiên: nhánh `d82ad6d` và `main` `3202035`. Mỗi đột biến sửa **một chỗ** trong mã hay cấu hình để phá đúng một điều bảo vệ, rồi chạy **ca mới trên nhánh** và **ca cũ trên `main`** (tên cũ). Chỉ «failed» mới tính là bắt. Lượt gốc (không đột biến): nhánh 548 qua, `main` 24 qua. Script `mutate138.py` trả file về bản gốc sau mỗi lượt; cuối cùng `tar --compare` với `git archive` của cả hai bản sao: không file nào khác nội dung.

**Đột biến** (mỗi mã là một chỗ sửa):

| Mã | Phá điều gì |
|---|---|
| R1 | `AIRouter` dựng hãng AI cho **mọi** việc lúc dựng (cả việc ảnh), thay vì chỉ các việc viết |
| P1 | Đòi khóa của cả 3 hãng, không chỉ hãng đang cấu hình |
| P2 | Câu báo thiếu khóa không nêu tên biến khóa (`…_API_KEY`) |
| P5 | Nút «Phân tích từ khóa» mở dù chưa dựng được AI |
| P6 | Câu báo khi dựng AI Claude chứa chính khóa Claude (lộ khóa) |
| S1 | Thử mù: đổi hãng không đổi ô tên mô hình |
| S2 | Thử mù: mở trang, ô tên mô hình **không** điền sẵn từ cấu hình |
| S5 | Trang Cài đặt đòi khóa của mọi hãng trong bảng việc (cả việc ảnh) |
| L1 | `ai.toml` sai cú pháp: lỗi thô của `tomllib` lọt ra, không câu tiếng Việt |
| L2 | Bộ đọc bỏ qua dòng `web_search` (luôn tắt) |
| L3 | Bộ đọc đảo ngược `web_search` |
| C1, C2, C3 | `config/ai.toml`: việc `links`, `outline`, `plan` được ghi `web_search = true` |
| A1 | `config/ai.toml`: việc `alt` `max_tokens = 4000` |
| K1 | `content.toml` sai bảng mã: lỗi thô lọt ra |
| K1b | `content.toml` sai cú pháp: lỗi thô `TOMLDecodeError` lọt ra khỏi bộ đọc |
| K2 | `[alt]`, `[images]` sai làm khóa cả trang Soạn bài |
| W1 | Trang không hiện bài đối thủ |
| W2 | Trang không hiện «Bài của mình phải có thêm» |
| W3 | Tiêu đề bài đối thủ không thoát Markdown |
| D1 | Đổi tên file danh sách bài mặc định |
| I1 | Lỗi khi AI viết alt: câu chung, không nêu khóa thiếu |
| I2 | Lỗi khi AI viết alt: lọt ra trang (`st.exception`) |

**Kết quả từng ca** (✓ = ca hỏng, tức bắt; ✗ = ca vẫn qua):

| # | Ca (tên mới) | Điều bảo vệ | Đột biến: ca mới / ca cũ | Nhận xét |
|---|---|---|---|---|
| 1 | `test_settings_blind.py::test_model_name_suggested_from_config_and_follows_provider` | Ô tên mô hình của thử mù lấy từ cấu hình, đổi theo hãng | S1 ✓/✓; **S2 ✗/✓** | **Kiểm ít hơn** (G-1): ca cũ kiểm cả ô điền sẵn lúc mở trang, ca mới chỉ kiểm sau khi đổi hãng. S2 sống qua cả 385 ca của 7 file thử mù. Đã bù bằng ca Soi Lỗi (S2 bị bắt) |
| 2 | `test_soi_loi_t051.py::test_alt_task_follows_owner_decision_with_small_budget` | `alt` effort thấp, `max_tokens` nhỏ, không tìm web | A1 ✓/✓ | Hãng, mô hình ghim theo quyết định 18/11, đúng phiếu |
| 3 | `test_soi_loi_t051.py::test_old_tasks_still_load_next_to_alt` | Chỉ việc nghiên cứu được tìm web | C1, C2, C3, L3 ✓/✓; L2 ✗/✓ | L2: G-2 |
| 4 | `…::test_sl_t051_1_enabled_image_needs_gemini_key_only_when_called` | Bật việc ảnh thì khóa Gemini chỉ bị đòi khi gọi việc ảnh | R1 ✓/✓ | Bản mẫu «viết bằng Claude, ảnh bằng Gemini» giữ đúng điều cũ |
| 5 | `…::test_real_ai_toml_broken_on_disk_is_handled_like_t010[cut]` | File cắt dở báo «cú pháp» bằng câu tiếng Việt | L1 ✓/✓ | Chỗ cắt mới vẫn giữa dòng `model` của `[tasks.alt]`, cùng kiểu chuỗi dở |
| 6 | `…::test_write_page_with_committed_config_needs_only_configured_keys` | Trang Soạn bài chỉ đòi khóa của hãng đang cấu hình | P1 ✓/✓ | Có chặn rỗng `names and len(names) < 3` |
| 7 | `…::test_sl_t051_1_write_page_with_image_enabled_does_not_ask_for_gemini_key` | Bật việc ảnh, trang không đòi khóa Gemini | R1 ✓/✓ | |
| 8 | `…::test_write_page_survives_broken_real_content_toml[ansi]`, `[cut]` (cùng `[alt-sai-dang]`) | `content.toml` hỏng thì trang vẫn chạy, báo đúng câu | K1 ✓/✓ (`[ansi]`); K1b ✗/✗ (`[cut]`); K2 ✗/✗ (`[alt-sai-dang]`) | K1b là đột biến **tương đương**: trang tự bắt `TOMLDecodeError` với cùng câu (`write.py:4534-4535`). K2 do ca 11 bắt ở cả hai bên. Khóa đặt theo hãng đang cấu hình chỉ là điều kiện để trang chạy |
| 9 | `test_soi_loi_t062.py::test_write_flow_with_image_enabled_never_builds_gemini` | Viết bài khi việc ảnh bật: không bao giờ dựng Gemini | R1 ✓/✓ | |
| 10 | `…::test_models_tab_with_image_enabled_and_only_claude_key` | Cài đặt không đòi khóa Gemini khi chỉ việc ảnh dùng Gemini | S5 ✓/✓ | R1 không liên quan (trang Cài đặt không dựng AI) |
| 11 | `…::test_bad_alt_and_images_do_not_lock_write_page` | `[alt]`, `[images]` sai chỉ khóa việc ảnh | K2 ✓/✓ | |
| 12 | `test_t062_image_config.py::test_enabling_real_image_block_needs_gemini_key_only_for_images` | Như ca 4, trên file thật | R1 ✓/✓ | |
| 13 | `…::test_write_page_with_image_enabled_and_only_claude_key` | Như ca 7 | R1 ✓/✓; P6 ✓ (nhánh) | |
| 14 | `test_app_pages.py::test_without_api_key_ai_buttons_are_locked` | Không khóa: câu báo nêu tên biến khóa, nút AI khóa | P2, P5 ✓/✓; P1 ✓/✗ | Ca mới bắt thêm P1 |
| 15 | `…::test_full_flow_research_outline_write` | Kết quả nghiên cứu hiện, rồi tới dàn ý, bài | **W2 ✓/✗**; W1 ✗/✓ | Mới kiểm **thêm** «Bài của mình phải có thêm». Tắt tìm web nên ca này kiểm chiều ngược (đối thủ **không** hiện); W1 vẫn bị bắt ở ca 20 và `test_t138_gemini_flash.py::…[bat-tim-web]` |
| 16 | `test_site_index.py::test_default_file_sits_next_to_drafts` | File danh sách bài mặc định là `data/site_index.sqlite` | D1 ✓/✓ | Hằng lấy lúc nạp file test, trước khi fixture trỏ đi: đúng |
| 17 | `test_ai.py::test_project_ai_config_is_valid` | Việc bắt buộc có mặt, hãng, mô hình hợp lệ; chỉ nghiên cứu được tìm web | C1, C2, C3, L3 ✓/✓; L2 ✗/✓ | L2: G-2 |
| 18 | `test_phase2_fixes.py::test_project_ai_config_still_loads` | Bộ kiểm chặt nạp được file dự án, đọc đúng `web_search` | L3 ✓/✓; L2 ✗/✓ | L2: G-2 |
| 19 | `test_t103_plan_prompt.py::test_plan_task_in_config_matches_outline_and_never_searches_web` | `plan` không tìm web, khớp `outline` | C1, C2, C3, L3 ✓/✓; L2 ✗/✓ | L2: G-2 |
| 20 | `test_config_tolerance.py::test_research_page_shows_competitor_title_escaped` | Tiêu đề bài đối thủ hiện đã thoát Markdown | W1, W3 ✓/✓ | Bản mẫu bật tìm web: cần, vì tắt thì không còn bài đối thủ để kiểm |
| 21 | `test_app_images.py::test_alt_ai_errors_shown_as_message` | Lỗi AI viết alt hiện bằng `st.error`, nêu khóa thiếu | P2, I1, I2 ✓/✓ | |

**Tóm lại:**
- Không ca nào thành test rỗng: ca mới nào cũng bắt ít nhất một đột biến phá đúng điều nó bảo vệ, và chính đột biến đó cũng làm hỏng ca cũ.
- 23 đột biến nhắm điều bảo vệ của các ca trong bảng (không tính P6, xem G-3): ở 21 đột biến ca mới bắt bằng hoặc hơn ca cũ; trong đó K1b là đột biến tương đương (sống ở cả hai bên), W2 chỉ ca mới bắt.
- Hai chỗ ca mới kiểm ít hơn ca cũ, mục 6:
  - S2 (G-1): không ca nào khác bắt, tôi đã bù;
  - L2 (G-2): 3 ca khác trên nhánh vẫn bắt.
- Ngoài bảng: một ca **không đổi** nhưng nay rỗng một phần vì cấu hình đã commit đổi hãng (G-3, P6).

## 2. Trọng tâm 2 — Yêu cầu 3: tắt tìm web thì bỏ đối thủ ở code; bật thì như cũ

- **Bỏ ở code:** `ContentWriter.research` (`seo_app/content/workflow.py:236-247`) đọc `web_search` của việc `research`; tắt thì `competitors = []` **sau** `clean_research`. Không dựa vào lời dặn.
- **Không có lối vào khác:** chỉ `workflow.py` dựng `Research` từ kết quả AI. `drafts.py` chỉ đọc lại nháp đã lưu (nháp soạn lúc còn tìm Google giữ đối thủ thật, đúng lựa chọn của Thợ Máy).
- **Đột biến mã mới:** 9/9 bị bắt:

| Mã | Phá điều gì | Ca bắt |
|---|---|---|
| T1 | Tắt tìm web mà vẫn giữ bài đối thủ AI trả | `test_competitors_are_dropped_only_when_web_search_is_off[tat-tim-web]`, `test_write_page_step_one_tells_when_web_search_is_off[tat-tim-web]`, `test_app_pages::test_full_flow_research_outline_write`; ca cả luồng của Soi Lỗi `[tat]` |
| T2 | Luôn bỏ bài đối thủ (cả khi bật) | `…[bat-tim-web]` (2 ca), `test_research_page_shows_competitor_title_escaped`; ca Soi Lỗi `[bat-doi-chung]` |
| T3 | Tắt tìm web vẫn gửi lời dặn tìm web | `test_competitors_are_dropped_only_when_web_search_is_off[tat-tim-web]` |
| T4 | Lời dặn khi tắt đòi kể bài đối thủ | `test_prompt_without_web_search_asks_for_no_competitors` |
| T5 | Không có dòng nhắc | `test_write_page_step_one_tells_when_web_search_is_off[tat-tim-web]`, `test_write_page_with_committed_config_shows_the_note` |
| T6 | Dòng nhắc hiện cả khi bật | `…[bat-tim-web]` |
| T7 | `research_searches_web` bỏ qua cấu hình | như T5 |
| T8 | `ai.toml` hỏng thì dòng nhắc làm sập trang (bỏ `try/except`) | `test_soi_loi_t051.py::test_write_page_with_image_block_touched_never_crashes_or_shows_key[bat-nua]` |
| T9 | Bật tìm web mà không qua `clean_research` | `test_competitors_are_dropped_only_when_web_search_is_off[bat-tim-web]` |

- **Cả luồng trên trang** (ca mới của Soi Lỗi): AI giả **không** làm theo lời dặn, vẫn trả một bài đối thủ có dấu nhận riêng.
  - Tắt tìm web: dấu đó không có trên trang, trong `research` của phiên, trong lời dặn dàn ý và viết bài, trong file nháp (đọc mọi byte của kho nháp trong thư mục tạm), kể cả sau «Phân tích lại».
  - Bật (đối chứng): có ở cả bốn chỗ, nên ca «tắt» không rỗng.
- **Bật tìm web như cũ:** `research_prompt(k, web_search=True)` giống hệt `research_prompt(k)` của `main` `3202035` từng chữ, 7/7 từ khóa thử (thường, có «» và xuống dòng, ký tự điều khiển và chữ đảo chiều, NFD, 500 ký tự, chữ dạng địa chỉ web và link Markdown).
  - Hãng AI nhận đúng `TaskConfig` của việc (công cụ tìm web chỉ gắn khi `web_search` bật: `anthropic_provider.py:95`, `openai_provider.py:121`, `gemini_provider.py:179`).
  - Trang không có dòng nhắc, vòng chờ giữ chữ cũ.
- **Dòng nhắc:** «Đang tắt tìm Google: AI không đọc bài đối thủ.» hiện ngay dưới ô từ khóa khi tắt.
  - `research_searches_web()` chỉ đọc file cấu hình, không cần khóa.
  - `load_ai_config` gói mọi lỗi đọc file thành `AIError`, nên cấu hình hỏng chỉ làm mất dòng nhắc, không làm sập trang (T8).
- **Còn sót:** SL-T138-3.

## 3. Trọng tâm 3 — Yêu cầu 6: test không ghi `data/` thật

- **Fixture trỏ được thật:** ba kho đọc đường mặc định **lúc tạo kho** (`field(default_factory=lambda: DEFAULT_…)`: `site_index.py:126`, `plan_cache.py:107`, `search_cache.py:284`). Các trang đọc `module.DEFAULT_…_FILE` **lúc chạy** (`write.py:2518`, `plan.py:150-181`, `tracking.py:328-494`, `home.py:50-72`). Chỉ `seo_app/storage/__init__.py` xuất lại `DEFAULT_DRAFTS_FILE` (bản chép lúc nạp), nhưng không chỗ nào dùng bản đó: mọi nơi đọc qua module.
- **Đủ kho:** năm kho trong `seo_app/storage` đều được trỏ (`sqlite_file` không có file).
  - Ngoài `seo_app/storage`, chỗ ghi `data/` duy nhất là cache ảnh xem trước `PREVIEW_CACHE_DIR` (`seo_app/images/process.py:103`). Mọi file test giao diện ảnh tự trỏ nó sang thư mục tạm, qua fixture tự chạy `previews` của `test_app_images.py` (từng file xuất lại `previews = ui.previews`).
- **Đột biến:** 4/4 bị bắt bởi `test_t138_khong_ghi_data_that.py`:
  - F1: fixture không tự chạy;
  - F2: quên trỏ `plan_cache`;
  - F3: thêm một kho mới trong `seo_app/storage` mà conftest chưa trỏ;
  - F4: kho đọc đường mặc định lúc nạp module, nên fixture trỏ không ăn.

  Ba lượt F1, F2, F4 đều tạo `data/` trong bản sao. Script xóa thư mục đó sau mỗi lượt (chỉ trong thư mục nháp).
- **Lô chạy thật trong worktree `wt-T-138`** (trước khi chạy: không có `data/`):
  - **Tệp chạy:** 98 file. Gồm mọi file nhắc WordPress giả, `site_index`, `plan_cache`, `search_cache`, `SiteIndexStore`, `PlanCacheStore`, `SearchCacheStore`, cùng ba test trang, test T-138 và test của Soi Lỗi.
  - **Móc kiểm:** plugin pytest `audit_data` (thư mục nháp) dùng `sys.addaudithook`, ghi mọi lần mở, `sqlite3.connect`, tạo thư mục, đổi tên, xóa nằm trong `data/` của worktree. Đối chứng: test tạo `data/`, mở SQLite, ghi file rồi xóa hết thì móc ghi đủ 7 lần.
  - **Kết quả:** 10.730 qua, 6 bỏ qua, 3 xfail (3 ca ghim của Soi Lỗi), **0 hỏng**, 53 phút 46 giây.
    - Móc kiểm ghi lại **0** lần đụng `data/` của worktree (`hits=0`), kể cả kiểu tạo rồi xóa.
    - Sau lượt, worktree **không có** thư mục `data/`; `git status` chỉ còn 2 file mới của Soi Lỗi.

## 4. Trọng tâm 4 — `config/ai.toml`

- **Đọc được:** UTF-8 không BOM, 0 ký tự CR trong blob, chữ NFC. `tomllib` và bộ kiểm chặt `load_ai_config()` đều nạp được 9 việc.
- **Đúng cấu hình phiếu:**
  - 9 việc (research, outline, write, rewrite, review, meta, links, plan, alt) đều `provider = "gemini"`, `model = "gemini-3.8-flash"`;
  - `[tasks.research]` `web_search = false`, không việc nào khác tìm web;
  - `effort`, `max_tokens` giữ nguyên như `main`; khối `[tasks.image]` vẫn tắt.
- **Ghi chú quay lại Claude:** tên mô hình đúng với bản trên `main` (`claude-opus-5-5`, việc `alt` `claude-sonnet-5-5`). Còn thiếu bước bật lại `web_search = true`: SL-T138-2.
- **Chạy test với cấu hình Claude cũ:** để biết các ca đọc hãng từ cấu hình có chạy đúng khi quay lại Claude không.
  - `config/ai.toml` của `main` đặt vào bản sao nhánh, 14 file (mọi file test Thợ Máy sửa, hai file test T-138, file của Soi Lỗi): 451 qua, **5 hỏng**, 2 bỏ qua, 1 xfail.
    - 4 ca hỏng ghim **quyết định hiện tại**, đúng chủ đích phiếu: hai ca ghim Gemini, hai ca ghim «tắt tìm web».
    - Ca thứ 5 (`test_config_header_tells_how_to_go_back_and_names_usable_models`) hỏng vì lượt này dùng nguyên đầu file của `main`, chưa có ghi chú mới.
    - Mọi ca khác qua, kể cả các ca R5 còn lại.
  - Sát thực tế hơn: giữ đầu file của nhánh, chỉ đổi đúng như ghi chú, 9 file chính.
    - (a) Làm đúng ghi chú hiện tại (vẫn `web_search = false`): 233 qua, **2 hỏng**, cả hai là ca ghim Gemini.
    - (b) Quay lại đủ như trước 18/11 (thêm `web_search = true`): 231 qua, **4 hỏng**, gồm 2 ca ghim Gemini và 2 ca ghim «tắt tìm web».
  - Xem G-4.

## 5. Lỗi mới

| # | Mức | Mô tả | Vị trí | Đề xuất sửa | Test ghim |
|---|---|---|---|---|---|
| SL-T138-1 | Thấp · **bắt buộc ở lượt 2** | README 7.2, đoạn «Việc viết alt cho ảnh», còn sai so với cấu hình mới: «hãng ghi ở `[tasks.alt]` (đang ghi Claude Sonnet)», «Nên dùng Claude (đang ghi sẵn)», và «Muốn dùng khóa miễn phí cho việc viết alt thì báo Chỉ Huy để ghi vào sổ rủi ro trước». `[tasks.alt]` nay là Gemini khóa miễn phí; chủ dự án đã chấp nhận (18/11 13:45, sổ rủi ro `security.md` mục 6 trên `main` `756941c`, LC-T050-4 điều kiện 6) | `README.md:207`, `:209`, `:210` | Ghi đúng: alt đang dùng Gemini Flash khóa miễn phí, ảnh công trình (đã bỏ GPS, EXIF) có thể được Google dùng để cải tiến sản phẩm và người duyệt xem được; chủ dự án đã chấp nhận ngày 18/11 (sổ rủi ro); quay lại Claude hay bật thanh toán thì không còn điều này. Kèm: chú thích `[tasks.alt]` trong `config/ai.toml:97` («Quyết định 4A: Claude Sonnet») thêm «tạm Gemini từ 18/11» | `test_readme_noi_dung_hang_dang_viet_alt` (tự thành ca thường khi `alt` quay lại Claude) |
| SL-T138-2 | Thấp | Ghi chú «quay lại Claude» không nhắc bật lại tìm web. Làm đúng ghi chú thì Claude chạy bước nghiên cứu **không** tìm Google (vẫn `web_search = false`), khác với trước 18/11. Dữ liệu không sai (code bỏ đối thủ, trang có dòng nhắc), chỉ không trở về như cũ. Gạch đầu dòng Gemini trả phí của README thì đã có câu này | `config/ai.toml:37-39`, `README.md:166` | Thêm «và ở `[tasks.research]` đổi lại `web_search = true`» vào cả hai chỗ. Chú thích `[tasks.research]  # … đọc các bài đứng đầu Google` (`config/ai.toml:41`) nên ghi «(tắt tìm web từ 18/11)» | `test_ghi_chu_quay_lai_claude_nhac_bat_lai_tim_web` |
| SL-T138-3 | Thấp | Tắt tìm web mà bước 1 vẫn nói AI đọc bài đứng đầu Google, ngay cạnh dòng nhắc «Đang tắt tìm Google: AI không đọc bài đối thủ.»: (a) khung hướng dẫn trước khi phân tích «AI xác định người tìm muốn gì và **đọc các bài đứng đầu Google** để tìm chỗ họ còn thiếu»; (b) sau khi phân tích, khung «🔎 Các bài đứng đầu Google còn thiếu gì?» hiện **trống**. Người dùng có thể nghĩ app lỗi. Thợ Máy đã đổi chữ vòng chờ vì đúng lý do này, còn sót hai chỗ | `app/views/write.py:2208-2211`, `:2224-2228` | Khi `not searches_web`: đổi chữ khung hướng dẫn; ẩn khung đối thủ khi danh sách trống (hoặc ghi một dòng «Đang tắt tìm Google»). Phiếu chỉ cho «một dòng nhắc», nên Chỉ Huy quyết làm ở lượt 2 hay phiếu sau | `test_tat_tim_web_buoc_1_khong_con_chu_doc_bai_dung_dau_google` |

Ba ca ghim đã chạy `--runxfail`: hỏng đúng lý do (chữ «đang ghi Claude Sonnet» có trong đoạn README; ghi chú không có `web_search = true`; chữ «đứng đầu Google» có ở cả trước lẫn sau khi phân tích).

**Báo sớm (đã xử lý):** trong lúc kiểm, tôi nhắn Chỉ Huy B rằng cấu hình mới gửi ảnh công trình cho Gemini khóa miễn phí khi viết alt, mà LC-T050-4 đòi chủ dự án quyết và ghi sổ rủi ro trước. Chủ dự án chấp nhận 13:45; Chỉ Huy ghi sổ rủi ro (`756941c`). Phần còn lại là README (SL-T138-1).

## 6. Ghi nhận (không chặn)

- **G-1 (R5, ca 1):** ca mới `test_model_name_suggested_from_config_and_follows_provider` không còn kiểm ô tên mô hình **điền sẵn lúc mở trang** (đường `S[mkey] = _suggest(...)` ở `app/views/settings.py`). Ca cũ kiểm việc này vì ứng viên 1 mặc định là Claude, có mô hình trong cấu hình. Nay ứng viên 1 mặc định là hãng đầu tiên có khóa (OpenAI, chưa có mô hình trong cấu hình), nên ca mới phải chọn hãng trước.
  - Đột biến S2 sống qua ca này và cả 385 ca của 7 file thử mù.
  - Tôi đã thêm ca `test_thu_mu_dien_san_mo_hinh_tu_cau_hinh_ngay_khi_mo_trang`: chỉ đặt khóa của hãng đầu tiên trong cấu hình, hãng nào cũng được. Ca này bắt S2. Thợ Máy không cần sửa thêm.
- **G-2 (R5, ca 3, 17, 18, 19):** bốn ca nay so `web_search` của nghiên cứu với `false`, cũng là giá trị mặc định. Vì vậy bộ đọc «bỏ qua dòng `web_search`» (L2) không bị bốn ca này bắt; ca cũ thì bắt.
  - Chú thích của `test_project_ai_config_still_loads` («không bỏ qua giá trị để lấy mặc định») chỉ đúng khi file ghi `true`.
  - L2 vẫn bị 3 ca khác trên nhánh bắt:
    - `test_phase2_fixes.py::test_good_ai_config_values_still_load`;
    - `test_config_tolerance.py::test_research_page_shows_competitor_title_escaped` (hàm mẫu `research_web_search_toml` tự kiểm giá trị đọc lại);
    - `test_t138_gemini_flash.py::test_write_page_step_one_tells_when_web_search_is_off[bat-tim-web]`.
  - Tôi thêm ca `test_bo_doc_cau_hinh_doc_dung_web_search_ca_hai_chieu` (bắt L2).
- **G-3 (ca không đổi, ngoài bảng R5):** `test_soi_loi_t051.py::test_write_page_with_image_block_touched_never_crashes_or_shows_key[bat-du]` đặt khóa **Claude** nhưng dùng file đã commit, nay mọi việc là Gemini. Vì vậy không hãng nào được dựng, và phần «không lộ khóa» không còn chạm khóa nào.
  - Đột biến P6 (câu báo khi dựng Claude chứa khóa): sống ở nhánh, ca cũ trên `main` bắt.
  - Điều bảo vệ vẫn còn ở ca khác: ca 13 bắt P6.
  - Đề xuất (một dòng, lượt 2 hay phiếu dọn): ca này đặt khóa bằng `set_configured_keys` như các ca trong bảng R5.
- **G-4 (báo cáo Thợ Máy):** câu «Khi quay lại Claude hay bật tìm Google, chỉ cần sửa `config/ai.toml`. Test không cần sửa lại» chưa đúng hẳn (mục 4).
  - Quay lại Claude đủ như trước 18/11 thì 4 ca phải sửa cùng:
    - `test_soi_loi_t051.py::test_alt_task_follows_owner_decision_with_small_budget`;
    - `test_soi_loi_t051.py::test_old_tasks_still_load_next_to_alt`;
    - `test_t138_gemini_flash.py::test_every_task_uses_gemini_flash_and_research_does_not_search`;
    - `test_t138_gemini_flash.py::test_write_page_with_committed_config_shows_the_note`.
  - Làm đúng ghi chú hiện tại thì 2 ca đầu nhóm Gemini phải sửa.
  - Các ca này ghim **quyết định hiện tại** đúng như phiếu đòi, nên phải sửa cùng lúc với `config/ai.toml`. Nên ghi rõ điều này trong ghi chú quay lại Claude, hoặc trong báo cáo.

Ngoài ra, khuôn `Research` gửi cho AI vẫn tả `competitors` là «bài đứng đầu Google… chép đúng từ kết quả tìm kiếm», và `new_angles` là «điều đối thủ thiếu» (`seo_app/content/models.py:8-20`), cả khi tắt tìm web. Lời dặn bảo để trống và code bỏ hết, nên vô hại; không cần sửa.

## 7. Test của Soi Lỗi (`tests/test_soi_loi_t138.py`)

| Ca | Kiểm | Kết quả |
|---|---|---|
| `test_doi_thu_bia_khong_toi_trang_dan_y_bai_viet_va_nhap[tat]` | AI giả không nghe lời, vẫn trả bài đối thủ: tắt tìm web (bản mẫu) thì dấu nhận không có trên trang, trong `research`, lời dặn dàn ý, viết bài, file nháp, kể cả sau «Phân tích lại» | qua |
| `…[bat-doi-chung]` | Bật (bản mẫu): có ở cả bốn chỗ | qua |
| `test_tat_tim_web_lan_nghien_cuu_gui_dung_cau_hinh_khong_cong_cu` | Hãng AI nhận việc `research` với `web_search` tắt; lời dặn «KHÔNG tìm được trên web» | qua |
| `test_thu_mu_dien_san_mo_hinh_tu_cau_hinh_ngay_khi_mo_trang` | Bù G-1 | qua; bắt S2 |
| `test_bo_doc_cau_hinh_doc_dung_web_search_ca_hai_chieu[bat]`, `[tat]` | Bù G-2 | qua; bắt L2 |
| `test_readme_noi_dung_hang_dang_viet_alt` | SL-T138-1 | xfail strict |
| `test_ghi_chu_quay_lai_claude_nhac_bat_lai_tim_web` | SL-T138-2 | xfail strict |
| `test_tat_tim_web_buoc_1_khong_con_chu_doc_bai_dung_dau_google` | SL-T138-3 | xfail strict |

Các ca không phụ thuộc file cấu hình đã commit đang bật hay tắt tìm web (dùng bản mẫu), nên quay lại Claude vẫn đúng.
- Đã chạy với ba cấu hình Claude (của `main`, (a), (b) ở mục 4): không ca nào của Soi Lỗi hỏng.
- Khi `alt` về Claude, ca SL-T138-1 tự thành ca thường và qua.

## 8. Lệnh đã chạy

```text
# Windows 11, Python 3.12.15, venv của wt-T-138. Không gọi AI thật, Google thật, WordPress thật.
# Bản sao trong thư mục nháp của phiên: git archive d82ad6d (nhánh), git archive 3202035 (main),
# bản sao nhánh + config/ai.toml của main (cấu hình Claude). Kiểm seo_app nạp từ đúng bản sao.

# Đột biến (mutate138.py, chạy bản gốc trước; «failed» mới tính là bắt)
python mutate138.py <nhánh> new …   → gốc 548 passed; 38 lượt (kể cả lượt rộng S2w, L2w, W1w)
python mutate138.py <main>  old …   → gốc 24 passed; 23 lượt
python mutate138.py <nhánh> new … P6,S2s,L2s,T1s,T2s → gốc 10 passed, 3 xfailed; 5/5 bắt
python mutate138.py <nhánh|main> … S5 → bắt cả hai bên
#   S5 chạy lúc lượt P6 của nhánh vừa xong ca cuối, nên lần so file cuối cùng của lượt đó báo
#   settings.py khác (S5 đang sửa); kết quả từng lượt không bị ảnh hưởng. Sau mọi lượt:
#   git archive | tar --compare: cả hai bản sao không file nào khác nội dung.

# Lời dặn bật tìm web so với main: 7/7 từ khóa giống hệt (cmp_prompt.py)

# File test của Soi Lỗi (worktree)
uv run pytest tests/test_soi_loi_t138.py -p no:randomly   → 6 passed, 3 xfailed
uv run pytest … --runxfail -k "readme or ghi_chu or buoc_1" → 3 failed (đúng lý do)

# Cấu hình Claude (bản sao nhánh, config/ai.toml của main), 14 file
uv run pytest <14 file> -p no:randomly   → 5 failed, 451 passed, 2 skipped, 1 xfailed (6:08)
# Làm theo ghi chú quay lại Claude trên đầu file của nhánh (mk_claude_cfg.py), 9 file
#   (a) vẫn web_search = false → 2 failed, 233 passed, 2 xfailed
#   (b) web_search = true      → 4 failed, 231 passed, 2 xfailed

# Lô test không ghi data/: trong worktree wt-T-138 (trước: không có data/), 98 file
PYTHONPATH=<thư mục nháp>/plugin AUDIT_DATA_ROOTS=<wt-T-138> AUDIT_DATA_LOG=<thư mục nháp>/audit-batch.log \
  uv run pytest <98 file> -p audit_data -p no:randomly -p no:cacheprovider
  → 10730 passed, 6 skipped, 3 xfailed in 3226.49s (0:53:46)
  → audit-batch.log: hits=0; sau lượt: không có data/; git status: chỉ 2 file mới của Soi Lỗi
# Đối chứng plugin: test tạo data/, mở SQLite, ghi file rồi xóa → hits=7

uv run ruff check .                     → All checks passed!
uv run ruff format --check tests/test_soi_loi_t138.py → already formatted
PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # bản sao 2 file của Soi Lỗi + file mồi tiếng Việt
  → chỉ file mồi bị báo (bắt được); 2 file của Soi Lỗi: 0
# Ký tự ẩn (Cf), CR, NFC trong 2 file của Soi Lỗi: 0, 0, NFC
git merge-tree --write-tree 756941c d82ad6d → f5bc821, không xung đột; mã của cây gộp y hệt nhánh
```

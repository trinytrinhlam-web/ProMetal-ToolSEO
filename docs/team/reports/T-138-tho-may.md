# Báo cáo T-138 · Tạm dùng Gemini Flash cho mọi việc AI: cấu hình, test ghim cấu hình, bước nghiên cứu không tìm web

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-138](../tickets/T-138-tam-dung-gemini-flash.md) · quyết định chủ dự án 2026-11-18 |
| Nhánh | `team/T-138`, từ `main` `3202035`; mã, cấu hình, test, README `7bbe500`; yêu cầu 6 `6309116`; 5 ca ghim cấu hình tìm thêm `2bdee5f`; báo cáo ở commit ngay sau |
| Ngày nộp | 2026-11-18 (giờ máy, +07) |
| Kết quả | Hoàn thành: yêu cầu 1–5 và yêu cầu 6 (Chỉ Huy thêm sau: test không ghi vào `data/` thật) |

## Tóm tắt (cho chủ dự án)

- Phần mềm **dùng Gemini Flash miễn phí** (`gemini-3.8-flash`) cho mọi việc AI. Chỉ cần khóa Gemini anh/chị đã nhập; không cần khóa Claude.
- Vì gói Gemini miễn phí **không tìm được Google**, bước «Chuẩn bị» của trang Soạn bài:
  - không còn liệt kê «bài đối thủ». Trước đây khi không tìm được Google, AI có thể tự bịa ra các bài đó.
  - Nay AI chỉ phân tích người tìm muốn gì, bài mình nên có thêm gì, câu hỏi hay gặp.
  - Trang ghi rõ một dòng: «Đang tắt tìm Google: AI không đọc bài đối thủ.»
- README mục 7 có đoạn «Đang dùng Gemini Flash miễn phí»:
  - giới hạn: không tìm Google, có lúc báo bận (lỗi 503);
  - cách quay lại Claude, hoặc bật thanh toán Gemini để dùng bản Pro và bật lại tìm Google.
- Ghi chú đầu file `config/ai.toml` có sẵn cách quay lại Claude, và tên mô hình Gemini còn dùng được.
- Việc phụ: bộ kiểm thử của đội không còn ghi file lưu tạm vào thư mục `data` của phần mềm. Trước đây chạy kiểm thử có thể tạo, ghi đè file danh sách bài, kế hoạch, số liệu Google trong `data` của thư mục chạy kiểm thử.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `config/ai.toml` | Giữ đúng bản cấu hình Chỉ Huy chép sang:<ul><li>9 việc dùng `provider = "gemini"`, `model = "gemini-3.8-flash"`;</li><li>`[tasks.research]` đặt `web_search = false`;</li><li>có ghi chú quay lại Claude.</li></ul> Tôi chỉ sửa ví dụ tên mô hình Gemini ở phần chú thích đầu file: `"gemini-3-pro"` (Google báo «Không có mô hình») thành `"gemini-3.8-flash"` (gói miễn phí dùng được) và `"gemini-3.1-pro-preview"` (phải bật thanh toán) |
| `seo_app/content/prompts.py` | `research_prompt(keyword, *, web_search=True)`.<ul><li>Bật: đúng lời dặn cũ, từng chữ.</li><li>Tắt: `_research_prompt_offline`. Lời dặn nói không tìm được web; chỉ nêu ý định, góc mới, câu hỏi từ hiểu biết chung; **để TRỐNG** danh sách bài đối thủ; không bịa tên bài, đường dẫn.</li><li>Từ khóa qua cùng lớp lọc `_keyword` như cũ.</li></ul> |
| `seo_app/content/workflow.py` | `ContentWriter.research`: đọc `web_search` của việc `research`, chọn lời dặn theo đó. **Tắt tìm web thì bỏ mọi bài đối thủ AI vẫn trả về** (không tin lời dặn). `clean_research` không đổi (kho nháp cũng gọi hàm này) |
| `app/views/write.py` | <ul><li>`research_searches_web()`: chỉ đọc `config/ai.toml`, không tạo AI, không cần khóa. Cấu hình lỗi thì coi như có tìm web, nên không thêm câu nhắc sai.</li><li>Bước 1 có dòng nhắc `MSG_NO_WEB_SEARCH` «Đang tắt tìm Google: AI không đọc bài đối thủ.» khi việc nghiên cứu tắt tìm web.</li><li>Vòng chờ khi tắt tìm web đổi thành «AI đang phân tích từ khóa…», thay cho «AI đang tìm và đọc các bài đứng đầu Google…».</li></ul> |
| `README.md` | Mục 7: đoạn «Đang dùng Gemini Flash miễn phí» (giới hạn; cách quay lại Claude; bật thanh toán Gemini để dùng Pro và bật lại tìm Google) |
| `tests/ai_config_samples.py` (mới, không phải file test) | Dùng chung cho các test ghim cấu hình.<ul><li>`configured_providers`, `configured_key_envs`, `set_configured_keys`: khóa của các hãng **đang được cấu hình**, trừ việc ảnh.</li><li>`ai_text_on(provider)`: bản mẫu `config/ai.toml` với mọi việc đang bật chuyển sang một hãng, để dựng «viết bằng Claude, ảnh bằng Gemini» trong `tmp_path`.</li><li>`research_web_search_toml(tmp_path, on)`: bản mẫu với bước nghiên cứu bật hay tắt tìm web, để kiểm phần chỉ có khi bật (bài đối thủ hiện trên trang).</li></ul> |
| 5 file test ghim cấu hình | 15 ca hỏng với cấu hình mới đã sửa để kiểm điều bảo vệ (bảng R5) |
| 5 file test khác: `test_ai`, `test_phase2_fixes`, `test_t103_plan_prompt`, `test_config_tolerance`, `test_app_images` | Thêm 5 ca ghim cấu hình cũ, sửa cùng cách (bảng R5). Không có trong danh sách 14 ca của phiếu; lượt chạy dài 157 file tìm ra |
| `tests/test_app_pages.py` | Thêm 1 ca đổi kỳ vọng (`test_full_flow_research_outline_write`, bảng R5) |
| `tests/test_t138_gemini_flash.py` (mới) | 10 ca (mục Đối chiếu) |
| `tests/conftest.py` (yêu cầu 6) | Fixture tự chạy `_never_touch_real_caches`: trỏ `DEFAULT_SITE_INDEX_FILE`, `DEFAULT_PLAN_CACHE_FILE`, `DEFAULT_SEARCH_CACHE_FILE` sang thư mục tạm riêng cho từng test, như hai fixture có sẵn của kho nháp, kho thẻ ảnh. Năm kho trong `seo_app/storage` nay đều được trỏ; `sqlite_file` không có file |
| `tests/test_t138_khong_ghi_data_that.py` (mới, yêu cầu 6) | 6 ca: mọi `DEFAULT_…_FILE` của mọi module `seo_app/storage` trỏ ra ngoài thư mục dự án (kho mới quên trỏ thì hỏng); luồng có WordPress giả không tạo, không đổi file nào trong `data/` thật; đối chứng trong ca; 3 fixture đều tự chạy |
| `tests/test_site_index.py` | Ca giá trị mặc định thật đọc hằng lúc nạp file test (R5) |

### Chỗ để ngỏ, tôi đã chọn

1. **Bỏ đối thủ ở `ContentWriter.research`, không ở `clean_research`.** `clean_research` còn chạy khi mở lại nháp đã lưu (`drafts.py`). Nháp soạn lúc còn tìm Google có thể có đối thủ thật, nên giữ nguyên.
2. **Ba điều bảo vệ của T-051, T-062 thử bằng bản mẫu «viết bằng Claude, ảnh bằng Gemini»** trong `tmp_path`:
   - việc ảnh bật thì chỉ đòi khóa Gemini khi gọi;
   - trang Soạn bài không đòi khóa Gemini;
   - không tạo AI Gemini khi chỉ viết.

   Với file đã commit (mọi việc là Gemini), không thử được điều nào: các việc viết tự đòi khóa Gemini.
   - Ca «trang Soạn bài chỉ đòi khóa của hãng đang được cấu hình» nay đặt khóa đúng các hãng trong file đã commit, không ghim Claude.
3. **Ca ghim quyết định của chủ dự án đổi thành ghim cấu hình hiện tại**, kèm chú thích «chủ dự án 18/11 tạm Gemini» (alt 4A: Claude Sonnet; nghiên cứu có tìm web). Phần bảo vệ tách riêng và giữ: chỉ việc `research` được tìm web, `links` và `plan` không bao giờ.
4. **Dòng nhắc đặt ngay dưới ô từ khóa** ở bước 1, hiện cả trước khi bấm «Phân tích». Ngoài dòng nhắc, tôi đổi thêm chữ vòng chờ, vì chữ cũ nói «tìm và đọc các bài đứng đầu Google». Không thêm dòng nào khác.

## Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới |
|---|---|---|
| `test_settings_blind.py::test_model_name_suggested_from_config_and_follows_provider` | Có khóa Claude, OpenAI; ô mô hình của ứng viên 1 điền mô hình Claude đầu tiên trong cấu hình | Lấy hãng đầu tiên có trong cấu hình (nay Gemini), có khóa hãng đó và một hãng khác. Chọn hãng đó → ô điền đúng mô hình đang dùng; đổi hãng → điền gợi ý của hãng mới. Vẫn kiểm «gợi ý từ cấu hình, đổi theo hãng» |
| `test_soi_loi_t051.py::test_alt_task_is_claude_sonnet_with_small_budget` | Tên ca như bên trái; alt = `("anthropic", "claude-sonnet-5-5", "low", 2000, False)` | **Đổi tên** thành `test_alt_task_follows_owner_decision_with_small_budget`; alt = `("gemini", "gemini-3.8-flash", "low", 2000, False)`, chú thích 4A và 18/11 |
| `test_soi_loi_t051.py::test_old_tasks_still_load_next_to_alt` | `research.web_search is True`; chỉ `research` tìm web | Bảo vệ: việc có tìm web ⊆ {`research`}. Hiện tại: `research.web_search is False` (18/11) |
| `test_soi_loi_t051.py::test_sl_t051_1_enabled_image_needs_gemini_key_only_when_called` | Bật khối ảnh trên file đã commit (viết bằng Claude), chỉ khóa Claude | Bật khối ảnh trên bản mẫu «viết bằng Claude» (`ai_text_on`); kiểm như cũ |
| `test_soi_loi_t051.py::test_real_ai_toml_broken_on_disk_is_handled_like_t010[cut]` | Cắt file sau `model = "claude-sonnet-5-5"` + 12 ký tự | Cắt 12 ký tự sau `model = "` trong mục `[tasks.alt]` (hãng nào cũng vậy); vẫn báo «cú pháp» |
| `test_soi_loi_t051.py::test_write_page_with_committed_config_needs_only_claude_key` | Tên ca như bên trái; chỉ có khóa Claude → trang không đòi khóa, nút AI mở | **Đổi tên** thành `test_write_page_with_committed_config_needs_only_configured_keys`. Chỉ có khóa của các hãng trong file đã commit (ít hơn 3 hãng) → như cũ, không lộ khóa |
| `test_soi_loi_t051.py::test_sl_t051_1_write_page_with_image_enabled_does_not_ask_for_gemini_key` | File đã commit + khối ảnh bật + khóa Claude | Bản mẫu «viết bằng Claude» + khối ảnh bật + khóa Claude; vẫn không đòi khóa Gemini |
| `test_soi_loi_t051.py::test_write_page_survives_broken_real_content_toml[ansi]`, `[cut]` (cùng `[alt-sai-dang]`, chung thân test) | Đặt khóa Claude | Đặt khóa các hãng đang được cấu hình; kiểm như cũ (trang vẫn chạy, báo đúng câu) |
| `test_soi_loi_t062.py::test_write_flow_with_image_enabled_never_builds_gemini` | File đã commit + khối ảnh bật + khóa Claude | Bản mẫu «viết bằng Claude» + khối ảnh bật + khóa Claude; vẫn chạy trọn 3 bước, không tạo AI Gemini |
| `test_soi_loi_t062.py::test_models_tab_with_image_enabled_and_only_claude_key` | Như trên, trang Cài đặt | Như trên (bản mẫu) |
| `test_soi_loi_t062.py::test_bad_alt_and_images_do_not_lock_write_page` | Khóa Claude | Khóa các hãng đang được cấu hình |
| `test_t062_image_config.py::test_enabling_real_image_block_needs_gemini_key_only_for_images` | File đã commit + khối ảnh bật | Bản mẫu «viết bằng Claude» + khối ảnh bật |
| `test_t062_image_config.py::test_write_page_with_image_enabled_and_only_claude_key` | Như trên, trang Soạn bài | Như trên (bản mẫu) |
| `test_app_pages.py::test_without_api_key_ai_buttons_are_locked` | Câu báo nêu `ANTHROPIC_API_KEY` | Câu báo nêu biến khóa của một hãng đang được cấu hình (nay `GEMINI_API_KEY`); nút vẫn khóa |
| `test_app_pages.py::test_full_flow_research_outline_write` | Sau «Phân tích», trang hiện bài đối thủ của AI giả | Trang hiện kết quả nghiên cứu (góc mới). Bài đối thủ hiện **đúng khi** việc nghiên cứu được tìm web (nay tắt nên không hiện) |
| `test_site_index.py::test_default_file_sits_next_to_drafts` (yêu cầu 6) | So `site_index.DEFAULT_SITE_INDEX_FILE` lúc chạy ca | So `REAL_DEFAULT_FILE`, lấy lúc nạp file test, trước khi conftest trỏ sang thư mục tạm (như `test_images_tags.py` với kho thẻ ảnh); vẫn đòi `data/site_index.sqlite` |
| `test_ai.py::test_project_ai_config_is_valid` | `research.web_search is True`; mọi việc khác không tìm web | Bỏ dòng ghim `research.web_search is True`: bật hay tắt do chủ dự án chọn (18/11 tắt, ghim ở `test_t138_gemini_flash`). Giữ phần kiểm việc bắt buộc có mặt, hãng, mô hình, `max_tokens`, mọi việc khác không tìm web |
| `test_phase2_fixes.py::test_project_ai_config_still_loads` | `research.web_search is True` | Bộ kiểm chặt vẫn nạp được file của dự án, và `research.web_search` đúng giá trị ghi trong file (đọc thẳng bằng `tomllib`), không lấy mặc định |
| `test_t103_plan_prompt.py::test_plan_task_in_config_matches_outline_and_never_searches_web` | Danh sách việc có tìm web `== ["research"]` | Tập việc có tìm web ⊆ {`research`}. `plan` vẫn không tìm web, cùng hãng, mô hình, effort với `outline` |
| `test_config_tolerance.py::test_research_page_shows_competitor_title_escaped` | File đã commit (nghiên cứu có tìm web); tiêu đề bài đối thủ chứa `![x](…)` hiện ra đã thoát | Bản mẫu bật tìm web (`research_web_search_toml`): tắt thì code bỏ hết bài đối thủ (yêu cầu 3), ca không còn gì để kiểm. Kiểm như cũ |
| `test_app_images.py::test_alt_ai_errors_shown_as_message` | Không có khóa AI: câu báo nêu `ANTHROPIC_API_KEY` | Câu báo nêu biến khóa của hãng đang cấu hình cho việc `alt` (nay `GEMINI_API_KEY`); vẫn hiện bằng `st.error`, không `st.exception` |

Tổng 22 ca:
- 15 ca hỏng ngay với cấu hình mới. Phiếu ghi 14 (`test_soi_loi_t051` ×7); tôi đếm được 8 ca hỏng ở `test_soi_loi_t051`.
- 5 ca cuối cũng hỏng với cấu hình mới, nhưng không có trong danh sách của phiếu; lượt chạy dài mới thấy.
- 2 ca `test_full_flow_research_outline_write`, `test_default_file_sits_next_to_drafts` đổi theo yêu cầu 3 và 6.

Không ca nào bị nới điều bảo vệ. Các điều sau vẫn được kiểm:
- trang chỉ đòi khóa của hãng đang được cấu hình;
- việc ảnh bật thì khóa Gemini chỉ bị đòi khi gọi;
- hỏng `config/*.toml` thì trang vẫn chạy;
- không lộ khóa;
- chỉ việc nghiên cứu được tìm web.

Chỉ phần «đang dùng hãng nào» đổi theo quyết định 18/11.

## Bằng chứng

```text
# Windows 11, Python 3.12.15, ruff 0.16.10. Không gọi AI thật, Google thật, WordPress thật.

# Trên main + cấu hình mới (trước khi sửa test): 15 ca hỏng (bảng R5). Sau khi sửa: 5 file đó qua hết.

# Lượt dài, trên đúng commit 6309116 (git status chỉ còn file báo cáo này), 157 file liên quan:
#   - đọc config/ai.toml hay gọi load_ai_config;
#   - gọi research_prompt, clean_research, ContentWriter;
#   - đọc README;
#   - dùng site_index, plan_cache, search_cache hay WordPress giả;
#   - trang: test_app_pages, test_app_images, test_soi_loi_t084, test_t101_settings_google…;
#   - test quét cả cây mã nguồn; test mới.
uv run pytest -q -p no:randomly <157 file>
  5 failed, 16125 passed, 23 skipped, 6 xfailed in 5849.26s (1:37:29)
#   5 hỏng: 5 ca ghim cấu hình cũ ngoài danh sách phiếu (5 dòng cuối bảng R5), sửa ở 2bdee5f.
#   6 xfailed: lỗi Soi Lỗi ghi từ trước (đọc thư mục ảnh R2-1, R2-2; SL-T026-3; SL-T036-10).
#   23 skipped: symlink, FIFO, quyền kiểu POSIX, os.environb (chỉ có trên Mac/Linux hay khi
#   Windows bật Developer Mode).

# Lượt sau khi sửa, trên mã của 2bdee5f (lúc chạy chưa commit; commit đúng các file đó, không sửa
# thêm), 31 file:
#   - 6 file vừa sửa;
#   - mọi file dùng ai_config_samples;
#   - 20 file có nhắc cấu hình AI, khóa API hay mở trang mà lượt dài chưa chạy.
uv run pytest -q -p no:randomly -rfEsx <31 file>
  2293 passed, 4 xfailed, 1 warning in 1395.72s (0:23:15)
#   4 xfailed: lỗi Soi Lỗi ghi từ trước (R4-3, SL-T028-1).
#   1 warning: Pydantic, ở ca T-028 cố ý đưa luồng trả lời hỏng (có từ trước).
# Sau cả hai lượt: worktree không có thư mục data/ (không test nào ghi data/ thật).

# Đối chứng yêu cầu 6 (chỉ trong worktree wt-T-138, script ở thư mục nháp):
#   bỏ autouse của _never_touch_real_caches (sửa tạm conftest) rồi chạy test_t138_khong_ghi_data_that.py
#   → 3 failed, 3 passed; data/ của worktree có plan_cache.sqlite, search_cache.sqlite, site_index.sqlite.
#   conftest trả về đúng byte (SHA-256); xóa đúng 3 file đó và thư mục data/ rỗng (trước đó chưa có).

uv run ruff check .                     → All checks passed!
# Quét bí mật: 20 file đổi (lấy từ 7bbe500, 6309116, 2bdee5f) và báo cáo này, có khóa giả đối
# chứng (bắt được). Các chỗ báo đều có từ trước:
#   - mật khẩu thử PASSWORD ở test_app_pages.py:14 và test_settings_blind.py:19
#     (commit 863f1f4, 0853559);
#   - khóa giả dùng để thử che khóa ở test_phase2_fixes.py:196 (3aa1591);
#   - docstring «https://tên:mật-khẩu@…» ở write.py (7aa4dbd), và dòng báo cáo này nhắc lại mẫu đó.
#   Không chỗ nào của phiếu này.
# Ký tự ẩn, CR, NFC: 0 trong phần phiếu thêm. test_config_tolerance.py có sẵn 3 ký tự rộng 0
# (U+200B, U+2060, U+FEFF) làm dữ liệu test, có từ trước.
# Gộp thử (git merge-tree):
#   - với main 3202035 → không xung đột;
#   - với team/T-137 619c229 (cũng sửa write.py, README) → không xung đột.
```

## Đối chiếu tiêu chí

| Yêu cầu | Đáp ứng | Test |
|---|---|---|
| 1. Commit `config/ai.toml`, sửa ví dụ tên mô hình | Bản cấu hình của Chỉ Huy + ví dụ tên mô hình | `test_every_task_uses_gemini_flash_and_research_does_not_search`, `test_config_header_tells_how_to_go_back_and_names_usable_models` |
| 2. Test ghim cấu hình kiểm điều bảo vệ | 20 ca (bảng R5), `tests/ai_config_samples.py` | 10 file test đã sửa |
| 3. Nghiên cứu khi tắt tìm web | Lời dặn riêng; code bỏ đối thủ; dòng nhắc bước 1 | `test_prompt_with_web_search_is_unchanged`, `test_prompt_without_web_search_asks_for_no_competitors`, `test_prompt_without_web_search_keeps_the_keyword_frame`, `test_competitors_are_dropped_only_when_web_search_is_off` (bật/tắt; AI vẫn trả đối thủ khi tắt → bị bỏ), `test_write_page_step_one_tells_when_web_search_is_off` (bật/tắt), `test_write_page_with_committed_config_shows_the_note` |
| 4. Test nơi gọi, test trang | 157 file liên quan, rồi 31 file sau khi sửa thêm (mục Bằng chứng) | |
| 5. README | Mục 7 | |
| 6. Test không ghi `data/` thật | Fixture tự chạy trỏ ba file lưu tạm sang thư mục tạm | `test_every_storage_default_file_points_outside_the_project`, `test_flow_with_fake_wordpress_never_writes_real_data_folder`, `test_control_without_redirect_the_flow_writes_into_data`, `test_conftest_redirects_are_autouse` (3 ca); đối chứng thật: tắt fixture thì hỏng (mục Bằng chứng) |

## Rủi ro và điểm cần chú ý

- **Bài viết lúc này không dựa trên bài đối thủ thật.** AI chỉ dùng hiểu biết chung, nên «Bài mình phải có thêm» kém sắc hơn khi còn tìm Google. Chất liệu thật của xưởng càng quan trọng.
- **Gemini Flash miễn phí có lúc báo bận (503)** hay hết hạn mức trong ngày. App báo câu tiếng Việt; người dùng bấm lại sau.
- **Nháp cũ soạn lúc còn tìm Google** vẫn giữ danh sách đối thủ đã lưu, vì `clean_research` không bỏ.
- Khi quay lại Claude hay bật tìm Google, chỉ cần sửa `config/ai.toml`. Test không cần sửa lại, vì đã đọc hãng từ cấu hình.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-098 · Kế hoạch: khuôn dữ liệu, đọc CSV/TSV/chữ dán, đề xuất thay đổi có AI, sửa SL-7

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-098](../tickets/T-098-ke-hoach-khuon-doc-de-xuat.md) · thiết kế [T-094 mục 1.2–1.4, 2.4, 6](T-094-tho-may.md) · điều kiện [Lá Chắn T-094](T-094-la-chan.md) |
| Nhánh | `team/T-098` (worktree `D:\ProMetal-ToolSEO\wt-T-098`), gốc `main` `15bfaca` |
| Ngày nộp | 2026-10-28 07:56 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành (yêu cầu 1–3). Đáp ứng LC-T094-1, -2, -3 (phần dữ liệu), -18, -19, -20, -21. Gỡ `xfail` SL-7 |

## Tóm tắt (cho chủ dự án)

- Phần **logic của trang Kế hoạch** đã có (giao diện làm ở T-101): app đọc kế hoạch từ **file CSV/TSV/TXT/MD** hoặc **chữ dán** (kể cả chép một vùng ô từ Excel, Google Sheets, hay bảng Markdown như các file trong `docs/plan/`), nhận cột theo tên («Từ khóa chính», «Từ khóa», «keyword»…), đọc ngày kiểu Việt Nam (`20/11/2026`, không bao giờ hiểu nhầm kiểu Mỹ), rồi **so với kế hoạch hiện tại** để đưa ra danh sách «Thêm / Cập nhật / Bỏ» kèm lý do.
- Ghi chú định hướng viết tự do (như mẫu trên giao diện demo) thì **AI đọc** và đề xuất; app kiểm từng đề xuất, đề xuất sai bị bỏ. AI không đưa được địa chỉ web nào vào kế hoạch, không đổi được trạng thái nào ngoài «Bỏ», và việc này **không bao giờ tìm web**.
- App **cảnh báo** (không tự sửa): từ khóa trùng dòng khác, trùng bài đã đăng trên website, ngày đã qua, bài đã hẹn giờ hay đã đăng mà bị đổi, và **nhiều từ khóa chỉ khác tên quận/phường** (nguy cơ Google coi là trang cửa ngõ, như nhận xét L5 trong `review_ke_hoach_v1.md`). «Bỏ» và đề xuất có cảnh báo không tick sẵn; app không bao giờ xóa dòng.
- Ghi chú có **số điện thoại, email** (có thể của khách) thì app **chưa gửi cho AI**, báo để anh/chị che hoặc xác nhận.
- Vá luôn lỗi nhỏ **SL-7** có từ Giai đoạn 2: từ khóa (sắp đến từ Google Sheets) không còn «giả» được khung dữ liệu trong mọi lời dặn AI.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/model.py` | Mới. `PlanRow` (pydantic `extra="forbid"`, `frozen`, `:369`): tự làm sạch, tự kiểm từng trường; bộ làm sạch chung `clean_text` (`:147`); nhãn cố định (`:50-107`) và cách gọi khác; đọc ngày `parse_plan_date` (`:205`), giờ `parse_plan_time` (`:246`), thời điểm có múi giờ `parse_plan_datetime` (`:268`); mã bài `parse_key`, `next_key` (`:300`, `:309`); cột tab «KeHoach» `SHEET_COLUMNS` (`:111`) cho T-100; `article_kind` (`:323`); dò, che số điện thoại/email `personal_info`, `mask_personal_info` (`:340-355`) |
| `seo_app/plan/parse.py` | Mới. `read_file` (`:126`), `read_paste` (`:154`) → `ParsedPlan`; tên cột đồng nghĩa (`_HEADER_NAMES`); bảng CSV (tự nhận «,», «;», tab), TSV, bảng chép từ Excel, bảng Markdown; không có cột từ khóa → chữ tự do cho AI; câu báo gom theo loại kèm số dòng; `resolve_target` (`:435`) đổi «Trang dịch vụ đích» thành **mã bài** đã đăng |
| `seo_app/plan/propose.py` | Mới. `Proposal`, `ProposalSet`; `compare_rows` (`:132`, so bảng), `from_ai` (`:239`, kiểm kết quả AI), `check_proposals` (`:329`, cảnh báo) |
| `seo_app/content/models.py` | Thêm `PlanSuggestion`, `PlanSuggestions` (`:70-98`), khuôn AI trả về |
| `seo_app/content/prompts.py` | Thêm `ke_hoach_hien_tai`, `ke_hoach_moi` vào `DATA_TAGS` (`:17-20`); `_keyword` (`:56`, SL-7) dùng ở 5 lời dặn có từ khóa trong câu chỉ thị (`research_prompt`, `outline_prompt`, `write_prompt`, `review_prompt`, `rewrite_prompt`); `plan_prompt` (`:512`) |
| `seo_app/content/workflow.py` | Thêm `ContentWriter.plan_changes` (`:377`), `_plan_task` (`:417`), `PersonalInfoError` (`:56`), hằng `PLAN_*` (`:44-54`) |
| `tests/test_soi_loi_t003_t009.py` | Gỡ 5 dòng `@pytest.mark.xfail(...)` của `test_keyword_cannot_fake_a_frame` (SL-7). Thân test không đổi, 0 dòng thêm |
| `tests/test_t040_prompts.py` | Sửa 1 dòng (`:329`), Chỉ Huy B duyệt: xem mục «Test cũ đã đổi» |
| `tests/test_plan_model.py`, `test_plan_parse.py`, `test_plan_propose.py`, `test_plan_ai.py` | Mới: 209 ca |
| `docs/team/reports/T-098-tho-may.md` | Báo cáo này |

Không sửa `seo_app/wordpress/**`, `app/**`, `seo_app/storage/**`, `seo_app/google/**`, `config/**`.

## Test cũ đã đổi

| File, dòng | Đổi | Lý do |
|---|---|---|
| `tests/test_t040_prompts.py:329` (`test_data_rules_and_tags_unchanged`, test chốt của Ngòi Bút T-040) | Tuple `DATA_TAGS` mong đợi thêm 2 khung mới `"ke_hoach_hien_tai", "ke_hoach_moi"` ở cuối; 1 dòng `-`, 1 dòng `+` | LC-T094-19 và thiết kế T-094 mục 1.4 bắt thêm 2 khung này vào `DATA_TAGS` (để chữ kế hoạch không tự đóng khung ở **mọi** lời dặn). Test chốt đòi đúng 7 khung cũ nên hỏng ở lượt chạy 02:46–02:59 (`1 failed, 5935 passed`). Hỏi Chỉ Huy B, Chỉ Huy chọn A (duyệt theo R5, 28/10): chỉ sửa đúng dòng đó. Ý test giữ nguyên: 7 khung cũ vẫn đủ, đúng thứ tự, không đổi; hai câu kiểm `DATA_RULES` không đụng |
| `tests/test_soi_loi_t003_t009.py:209-213` | Gỡ dấu `xfail` (chỉ xóa dòng) | SL-7 đã sửa, test XPASS (LC-T094-19) |

## Cách làm, chỗ khác hay thêm so với thiết kế

1. **`[tasks.plan]` chưa có** (T-103 thêm vào `config/ai.toml`): `_plan_task` dùng mục `[tasks.plan]` nếu máy đã có; chưa có thì **tạm** lấy hãng, mô hình, effort của `[tasks.outline]` (thiết kế mục 6: «cùng hãng/mô hình với `outline` cho tới khi chủ dự án đổi»), đổi tên việc thành `plan`, `max_tokens` ít nhất 16.000. Cả hai đường đều **tắt `web_search`** bằng `dataclasses.replace` trong code (LC-T094-19, như việc alt ở T-062). Lời dặn `plan_prompt` là bản chạy được; phần chữ để Ngòi Bút viết lại ở T-103.
2. **Trang dịch vụ đích chỉ giữ mã bài** (`target_id`), không giữ địa chỉ: link phải là `https://` đúng tên máy của site (`is_site_link`) **và** có trong danh sách bài đã đăng; ô ghi số thì số đó phải là mã bài có trong danh sách. Không có danh sách (`index`) thì bỏ trống ô và báo.
3. **Trạng thái từ bảng:** chỉ «Bỏ» tạo đề xuất «Bỏ». Dòng mới chỉ nhận «Chưa viết», «Đang viết» (các trạng thái app ghi sau khi gửi WordPress không lấy từ file); Mã bài WordPress, ngày đăng thực tế, cập nhật lúc trong file **không** được đề xuất (chỉ app ghi, thiết kế 1.7). `PlanRow` vẫn đọc được các cột này để T-100 dựng dòng từ Sheet.
4. **Khớp theo từ khóa thì không đổi từ khóa:** file ghi «LAN CAN CAU THANG SAT» khớp dòng «lan can cầu thang sắt» (so không dấu) nhưng không đề xuất đổi cách viết. Khớp theo Mã bài thì đổi từ khóa được.
5. **Ô trống trong bảng không xóa** giá trị đang có (bảng chỉ có 2 cột thì 14 cột kia giữ nguyên).
6. **Ô sai thì bỏ trống ô đó và báo**; chỉ bỏ cả dòng khi thiếu từ khóa, từ khóa sai độ dài, hay Mã bài trùng dòng trên. Câu báo gom theo loại: «Ô «Ngày dự kiến» không đọc được, đã bỏ trống ô đó (37 dòng: dòng 2, 5, 9, 12, 20, …).» Số dòng là thứ tự dòng trong bảng (dòng tiêu đề là 1).
7. **Thêm so với thiết kế:** đọc bảng Markdown (kế hoạch trong `docs/plan/` viết dạng này); ô «Ngày giờ đăng» (`20/11/2026 08:30`, yêu cầu phần mềm 3.1) tách ra ngày và giờ; CSV tự nhận dấu «;» (Excel đặt vùng châu Âu).
8. **AI không đặt được** slug, trang đích, trạng thái (ngoài «Bỏ»), Mã bài WordPress: khuôn `PlanSuggestion` không có các trường đó (trường lạ bị bỏ qua). Khuôn không có giá trị mặc định (như mọi khuôn AI khác của app: khuôn «strict» của OpenAI đòi đủ mọi trường).
9. **SL-7:** `_keyword` gộp từ khóa một dòng, `_neutralize` (NFKC, bỏ ký tự vô hình, đổi `<` trước tên khung thành `‹`), đổi «» thành ‹›. `meta_prompt`, `blind_test_prompt` vốn đặt từ khóa **trong** khung `<de_bai>` nên đã được vô hiệu từ trước; `internal_links_prompt` không có từ khóa.

## Đối chiếu điều kiện Lá Chắn (LC-T094)

| Mã | Đáp ứng ở đâu | Test |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress, AI thật | Không có đường gọi mạng mới; AI giả `PlanProvider` (thay `make_provider`), danh sách bài là `SiteIndex`/`PublishedItem` dựng trong bộ nhớ; bộ chặn mạng `tests/conftest.py` vẫn bật | Cả 4 file test |
| **LC-T094-2** Câu báo cố định | Lỗi đọc file, chữ dán: hằng trong `parse.py` (`FILE_TOO_BIG`, `FILE_BAD_TYPE`, `FILE_BAD_ENCODING`, `TOO_MANY_ROWS`, `TOO_MANY_COLUMNS`, `BAD_TABLE`, `PASTE_TOO_LONG`, `TEXT_TOO_LONG`), không chép tên file hay chữ trong ô; câu báo ô sai chỉ nêu **tên cột chuẩn** và số dòng (`_Notes`); cảnh báo đề xuất chỉ nêu mã bài (`WARN_*`); mục AI sai chỉ đếm (`NOTE_AI_DROPPED`); lỗi kế hoạch AI là hằng `PLAN_*`, `PERSONAL_INFO` (chỉ số lượng); lỗi `csv`, giải mã đổi thành câu cố định `from None` | `test_bad_cells_are_left_empty_and_reported_by_row_without_cell_text`, `test_warnings_are_grouped_and_capped`, `test_warnings_and_reasons_never_copy_plan_text`, `test_ai_invalid_items_are_dropped_and_only_counted`, `test_personal_info_blocks_sending_until_user_agrees` (câu báo không có số, email) |
| **LC-T094-3** Chữ hiện thuần (phần dữ liệu) | Hiển thị là việc của T-101; T-098 bảo đảm dữ liệu đưa ra đã bỏ ký tự đảo hướng chữ (U+202A–U+202E, U+2066–U+2069) và ký tự vô hình ở **mọi** trường `PlanRow` và ở lý do AI (`clean_text`), không chỉ từ khóa (chỗ thiếu #7 của Lá Chắn). Chữ trả về là chữ thuần chưa escape, docstring ghi rõ phải hiện bằng ô bảng / `st.text` / `escape_markdown` | `test_clean_text_removes_control_invisible_and_bidi_characters`, `test_plan_row_cleans_every_text_field`, `test_control_bidi_and_invisible_characters_are_removed`, `test_ai_reason_is_cleaned_text` |
| **LC-T094-18** Một bộ làm sạch `PlanRow`, giới hạn | Mọi nguồn (file, chữ dán, Sheet qua T-100, cache, AI) dựng `PlanRow`; validator `mode="before"` gọi `clean_text` (NFC; bỏ Cc trừ khoảng trắng, Cf, Cs, Co, Cn, ký tự «mặc định bỏ qua»). File: kiểm **byte trước khi giải mã** (`read_file`, ≤ 1 MB); ≤ 1.000 dòng, ≤ 26 cột (kiểm **trong lúc** đọc, `_limited_rows`), ô ≤ 2.000 ký tự (cắt và báo), chữ dán ≤ 20.000; chỉ `utf-8`/`utf-8-sig` (không đoán); CSV bằng `csv` chuẩn; ngày không nhận `mm/dd`, năm 2020–2035 cho mọi dạng (cả số ngày kiểu Sheets) | `test_file_size_checked_in_bytes_before_decoding`, `test_two_megabyte_file_rejected`, `test_one_thousand_rows_ok_one_more_rejected`, `test_too_many_columns_rejected_but_trailing_empty_cells_ignored`, `test_long_cell_is_cut_and_reported`, `test_only_utf8_no_guessing` (cp1258, UTF-16, byte hỏng), `test_dates_rejected` (`11/25/2026`, `1000`, `99999`…), U+202E, U+0000 ở trên |
| **LC-T094-19** SL-7, khung `plan`, không tìm web | `_keyword` ở 5 lời dặn; gỡ `xfail` `test_keyword_cannot_fake_a_frame` (XPASS); `plan_prompt`: kế hoạch hiện tại `<ke_hoach_hien_tai>`, chữ dán `<ke_hoach_moi>` (thêm vào `DATA_TAGS`), lời dặn hệ thống có `DATA_RULES`; `_plan_task` luôn `web_search=False` dù `config/ai.toml` bật | `test_keyword_cannot_fake_a_frame` (qua), `test_keyword_cannot_close_or_open_any_frame_in_any_prompt` (7 lời dặn × 4 kiểu tấn công gồm `</du_lieu_tham_khao>`, `</ke_hoach_moi>`, U+200B, `＜/…＞`), `test_plan_prompt_data_cannot_close_frames`, `test_plan_task_from_config_never_searches_the_web`, `test_plan_changes_uses_outline_model_without_web_search_until_plan_task_exists` |
| **LC-T094-20** Kết quả AI chưa tin cậy | `from_ai`: ≤ 100 mục (thừa bị bỏ, có đếm); mục sai bị bỏ: hành động lạ, lý do trống / > 300 ký tự / có HTML, nhãn lạ, ngày sai hay ngoài khoảng, chữ có HTML, «Thêm» có Mã bài hay thiếu từ khóa, «Cập nhật»/«Bỏ» với Mã bài không có thật, một Mã bài hai lần; câu báo chỉ đếm. Trang đích chỉ nhận mã bài trong danh sách bài đã đăng (bảng), AI không có trường địa chỉ, slug, trang đích; địa chỉ trong lý do, ghi chú chỉ là chữ. «Bỏ» không tick sẵn (`Proposal.preselected`); «Bỏ» chỉ đổi Trạng thái, không hàm nào xóa dòng | `test_ai_invalid_items_are_dropped_and_only_counted` (17 kiểu), `test_ai_more_than_100_items_extra_dropped` (150 mục), `test_ai_same_key_twice_keeps_first`, `test_ai_cannot_set_address_slug_or_target`, `test_target_outside_published_list_is_dropped` (7 kiểu: site khác, `http`, `user@`, tên miền đuôi giả, bài chưa đăng, số lạ, `javascript:`), `test_target_link_on_site_becomes_post_id_never_an_address`, `test_table_never_drops_unless_status_says_so` |
| **LC-T094-21** A3: số điện thoại, email | `personal_info` dò số Việt Nam (`0…`, `+84…`, `84…`, cách bằng dấu cách/chấm/gạch, 9–10 chữ số sau đầu số) và email trên chữ đã làm sạch (ký tự vô hình chen giữa không che được); `plan_changes` báo `PersonalInfoError` và **không gọi AI** khi có, trừ khi `allow_personal=True` (người dùng đã thấy cảnh báo và đồng ý), hoặc chữ đã che bằng `mask_personal_info` («[đã ẩn]»). Ghi chú của thợ trong kế hoạch hiện tại **không** gửi AI (`_plan_line` chỉ gửi mã, từ khóa, ngày, trạng thái, ưu tiên). Phần «điền Ghi chú của thợ vào Soạn bài» là của T-102: dùng chính `personal_info`, `mask_personal_info` | `test_personal_info_counts` (7 ca), `test_mask_personal_info`, `test_personal_info_blocks_sending_until_user_agrees`, `test_personal_info_hidden_by_invisible_characters_is_still_found`, `test_plan_prompt_never_sends_notes` |

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15 (uv), worktree `wt-T-098`. Máy chạy song song phiên khác.

Test mới, test SL-7, và test của **mọi** nơi dùng phần đã sửa (`prompts.*_prompt`, `DATA_TAGS`, `_neutralize`, `_block`, `ContentWriter`, `content.models`, `content.workflow`; danh sách lấy bằng `grep` trên `tests/`), thêm `tests/test_app_pages.py` (lớp viết bài AI) và test lời dặn alt (`seo_app/images/alt.py` dùng `_block`): 54 file.

```
$ uv run pytest -q -p no:cacheprovider -rfEX \
    test_plan_model.py test_plan_parse.py test_plan_propose.py test_plan_ai.py test_ai_images.py
    test_ai_openai_gemini.py test_ai_openai_gemini_soi_loi.py test_app_drafts.py test_app_pages.py
    test_blind_test.py test_business_profile.py test_config_tolerance.py test_content_edge_cases.py
    test_content_workflow.py test_edit_unescape.py test_env_file.py test_la_chan_t039.py
    test_la_chan_t040.py test_link_escape.py test_onpage_links.py test_onpage_meta.py
    test_onpage_schema.py test_phase2_fixes.py test_profile_blocks.py test_profile_tag_t032.py
    test_prompt_data_frames.py test_safety.py test_sanitize.py test_sanitize_autolink.py
    test_sanitize_hardening.py test_soi_loi_round3.py test_soi_loi_round4.py test_soi_loi_round5.py
    test_soi_loi_round6.py test_soi_loi_round7.py test_soi_loi_t003_t009.py
    test_soi_loi_t019_luot2.py test_soi_loi_t021_t017.py test_soi_loi_t024.py test_soi_loi_t026.py
    test_soi_loi_t029.py test_soi_loi_t031.py test_soi_loi_t036.py test_soi_loi_t039.py
    test_soi_loi_t040.py test_soi_loi_t041.py test_soi_loi_t051.py test_t040_prompts.py
    test_t041_links_ai.py test_t041_meta.py test_t041_schema.py test_t041_seo_ui.py
    test_t062_alt_prompt.py test_soi_loi_t050.py          # (đều trong tests/)
(2026-10-28 07:35:51 → 07:55:38 +0700, bản sẽ commit)
5936 passed, 4 skipped, 13 xfailed in 1183.05s (0:19:43)
```

- 0 hỏng, 0 XPASS. 13 `xfailed` là dấu có từ trước của phiếu khác trong `tests/test_la_chan_t039.py` (LC-T039-2, T-096 sửa), `tests/test_soi_loi_round4.py`, `tests/test_soi_loi_t026.py`, `tests/test_soi_loi_t036.py`, `tests/test_soi_loi_t041.py` (SL-T041-8); không có ca nào của T-098.
- Lượt trước (02:46:30 → 02:59:42) trên bản chưa sửa test chốt: `1 failed, 5935 passed, 4 skipped, 13 xfailed`; ca hỏng là `test_data_rules_and_tags_unchanged` (mục «Test cũ đã đổi»).
- 4 file test mới riêng: `209 passed`.

```
$ uv run ruff check .
All checks passed!
```

- SL-7: `uv run pytest --runxfail tests/test_soi_loi_t003_t009.py -k keyword_cannot_fake_a_frame` → `1 passed` trước khi gỡ dấu. `git diff tests/test_soi_loi_t003_t009.py`: 5 dòng `-` (dấu `xfail`), 0 dòng `+`.
- Nhập từng module trong tiến trình mới (bắt vòng nhập: `plan` ↔ `content`): `seo_app.plan.model`, `.parse`, `.propose`, `seo_app.content.workflow`, `seo_app.storage.drafts`, `app.views.write` đều nhập được.
- File nguồn và test không chứa ký tự điều khiển, ký tự vô hình nằm trần (đều viết dạng `\u…`); đã soát bằng script.
- Không gọi AI, WordPress, Google hay mạng thật; không đọc `.env`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: làm đúng dòng T-098 của thiết kế (`seo_app/plan/model.py`, `parse.py`, `propose.py`; `ContentWriter.plan_changes`, `prompts.plan_prompt`, `PlanSuggestions`; SL-7), giữ ranh giới file với T-096, T-097 (không đụng `seo_app/publish/`, `seo_app/google/`, `seo_app/onpage/links.py`, `env_file.py`)
- [x] Yêu cầu 2: LC-T094-1, -2, -3 (phần dữ liệu), -18, -19, -20, -21 (bảng trên)
- [x] Yêu cầu 3: test cho phần logic mới (209 ca); test cũ vẫn qua (mục «Bằng chứng»)
- [x] Test liên quan + `uv run ruff check .` sạch
- [x] Báo cáo `docs/team/reports/T-098-tho-may.md`

## Rủi ro và điểm cần chú ý

1. **Dò số điện thoại có thể nhầm** dãy số dài 10–11 chữ số bắt đầu bằng 0 hay 84 (mã hàng, số tài khoản): chỉ là cảnh báo, người dùng bấm «vẫn gửi». Số điện thoại viết bằng chữ («không chín không chín…») không dò được.
2. **Cảnh báo trang cửa ngõ** dựa trên danh sách địa danh TP.HCM viết sẵn («quận/q/phường/p/huyện/xã» + số hay một-hai chữ, và 12 tên quận huyện cũ không có chữ «quận»). Chưa dùng danh sách 168 phường, xã mới (thiết kế mục 8: phiếu sau). Có thể nhầm «phương án» thành «phường Án…» khi so khuôn: chỉ thêm cảnh báo.
3. **Trùng bài đã đăng** dùng 3 phép so (slug bằng nhau, hệ số Dice ≥ 0,8, mọi từ của từ khóa ≥ 3 từ nằm trong tiêu đề): từ khóa 2 từ («cửa sắt») không bị coi là trùng dù nằm trong nhiều tiêu đề (cố ý).
4. **`[tasks.plan]` tạm dùng mô hình `outline`** tới khi T-103 thêm mục riêng. Máy thiếu cả hai mục thì báo thiếu `[tasks.outline]` (câu báo sẵn có của app).
5. Bảng Markdown có ô chứa dấu «|» (viết `\|`) bị tách sai cột: hiếm trong kế hoạch.
6. T-100 dựng dòng từ Google Sheets cần dùng đúng đường đọc của `parse.py` (tên cột, đổi ô) hoặc dựng `PlanRow` trực tiếp; `SHEET_COLUMNS` khớp đúng thứ tự trường `PlanRow` (có test).

## Đề xuất

- **T-101 (Họa Sĩ):** hiện `Proposal.after`/`before`/`reason`/`warnings`, `ParsedPlan.warnings`, `ProposalSet.notes` bằng ô bảng hay `st.text` (LC-T094-3, -32); `PersonalInfoError` → hiện cảnh báo kèm hai nút «Che số điện thoại, email» (`mask_personal_info`) và «Vẫn gửi» (`allow_personal=True`); tick sẵn theo `Proposal.preselected`. Tải file: chỉ đuôi `.csv`, `.tsv`, `.txt`, `.md`; kiểm kích thước trước khi đọc (LC-T094-33), rồi gọi `read_file`.
- **T-102 (Họa Sĩ):** khi điền «Ghi chú của thợ» từ dòng kế hoạch vào Soạn bài, dùng `personal_info` / `mask_personal_info` (LC-T094-21); loại trang → `article_kind`.
- **T-103 (Ngòi Bút):** viết lại phần chữ `plan_prompt`; thêm `[tasks.plan]` (không `web_search`) vào `config/ai.toml` và mẫu vào `TASK_EXAMPLES` của `seo_app/ai/registry.py` nếu muốn câu báo thiếu mục có mẫu (file đó ngoài phạm vi T-098).
- **Soi Lỗi / Lá Chắn:** soát kỹ `resolve_target`, `from_ai`, giới hạn đọc file, `_keyword` ở 5 lời dặn.

## Câu hỏi cho chủ dự án

Không có.

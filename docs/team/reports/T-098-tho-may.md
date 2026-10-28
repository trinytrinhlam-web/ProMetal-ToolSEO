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

---

## Lượt 2 (2026-10-28 13:16 +07:00) · Soi Lỗi rút gọn ĐẠT CÓ ĐIỀU KIỆN (`84f32ec`)

Chỉ Huy B giao: sửa SL-T098-1 (bắt buộc), SL-T098-2, các lỗi Thấp và góp ý nhỏ, an toàn, trong phạm vi phiếu; cái nào không sửa thì ghi lý do.

### Tóm tắt (cho chủ dự án)

- AI không còn lách được thẻ HTML vào kế hoạch bằng ký tự vô hình hay chữ toàn chiều rộng.
- File kế hoạch nhiều bảng (như kế hoạch 6 tháng) nay đọc **mọi bảng**, không chỉ bảng đầu; bảng không có cột từ khóa thì báo số bảng bỏ qua.
- Dò số điện thoại nhận thêm `(+84) 909…`, `+84 (0) 909…`, `(028) 3812 3456`, `0909 - 123 - 456`; chữ toàn chiều rộng không lọt; dò nhanh với chữ dài.
- Cảnh báo «trang cửa ngõ» không còn bắt nhầm «phụ kiện», «quay chậm», «xài lâu».
- Kế hoạch 1.000 dòng so trong vài giây thay vì gần một phút.
- Đọc thêm: giờ có giây (`08:00:00`, như Google Sheets hiện), `SA/CH/AM/PM`, ngày giờ trong một ô số; tên cột «Ngày xuất bản», «Deadline», «Từ khóa SEO»…; dòng tên bảng phía trên dòng tiêu đề; «B-1» và «B-001» là một mã.

### Đã sửa

| Mã | Sửa | Chỗ |
|---|---|---|
| **SL-T098-1** (Trung bình) | Đường AI kiểm thẻ HTML trên **chữ đã làm sạch** (bỏ ký tự vô hình trước) và cả bản NFKC (`＜script＞`), như bài học T-041; áp cho từ khóa, từ khóa phụ, tiêu đề dự kiến, ghi chú và lý do | `propose.py` `_has_html_text`, dùng ở `_ai_values`, `_ai_item` |
| **SL-T098-2** (Trung bình) | Đọc **mọi** bảng Markdown có cột từ khóa (`_tables_to_plan`), gộp dòng, Mã bài trùng giữa các bảng giữ dòng đầu, câu báo mỗi bảng mở đầu «Bảng N:», bảng không có cột từ khóa báo số bảng (`UNREAD_TABLES`); giới hạn 1.000 dòng tính chung | `parse.py` `_tables_to_plan`, `_rows_to_plan` |
| SL-T098-3 | `csv.reader(..., strict=True)`: dấu ngoặc kép không đóng ra câu cố định `BAD_TABLE` | `parse.py` `_read_table` |
| SL-T098-4 | Ô Markdown: chỉ chia ở dấu gạch đứng chưa escape; dấu gạch đứng đã escape (gạch chéo ngược rồi gạch đứng, ví dụ tiêu đề «Sửa cửa cuốn \| Pro-Metal») thành một gạch đứng trong ô; chỉ bỏ đúng một gạch đứng ở đầu và một ở cuối dòng (dòng mở đầu bằng hai gạch đứng liền nhau giữ ô đầu trống) | `parse.py` `_md_cells` |
| SL-T098-5 | Biểu thức số điện thoại: đầu số `0`, `84`, `+84`, `(+84)`, `+84 (0)`, `(028)`; tới 3 ký tự cách (dấu cách, chấm, gạch, ngoặc) giữa các chữ số. Dạng dính chữ «sđt0909…» vẫn không dò (Soi Lỗi khuyên không, dễ nhầm mã hàng) | `model.py` `_PHONE_RE` |
| SL-T098-6 | Dò và che trên chữ đã NFKC, đúng chữ AI nhận | `model.py` `_visible_for_ai` |
| SL-T098-7 | Email: neo đầu, giới hạn độ dài từng phần → tuyến tính (20.000 ký tự liền: 7 ms, trước 4–5 s) | `model.py` `_EMAIL_RE` |
| SL-T098-8 | Viết tắt «q», «p» chỉ là địa danh khi theo sau là số hay dấu chấm; «quận/phường/huyện/xã» + tên phải có dấu cách | `propose.py` `_LOCATION` |
| SL-T098-9 | So trùng theo **đúng dòng** (`id`), không theo mã (dòng chưa mã không bị loại hết); dòng cũ chưa có mã được đề xuất đổi thì được **cấp mã** (T-100 ghi Sheet theo mã), lý do ghi «Cấp mã bài B-00N…», `Proposal.changes` có `key` | `propose.py` `check_proposals`, `_table_change` |
| SL-T098-11 | Khóa từ khóa, khuôn địa danh, tập từ bài đã đăng tính một lần mỗi dòng; cấp mã bằng `_Keys` (không quét lại danh sách mỗi dòng mới) → tuyến tính | `propose.py` `check_proposals`, `_post_index`, `_Keys` |
| SL-T098-10 | Nhận bảng chép từ Excel/Google Sheets theo **dòng của bảng** (`csv`, tính cả ô nhiều dòng trong ngoặc kép), không theo dòng vật lý | `parse.py` `_looks_tabbed` |
| G1 | Thêm tên cột «Ngày đăng dự kiến», «Ngày xuất bản», «Ngày đăng bài», «Publish», «Deadline», «Từ khóa SEO», «Keyword chính», «Từ khóa mục tiêu», «Target keyword»; báo «N cột không nhận ra tên nên không đọc» (chỉ số đếm, LC-T094-2) | `parse.py` `_HEADER_NAMES`, `_header_map` |
| G2 | Giờ có giây (`08:00:00`, bỏ giây), giờ có buổi viết tắt `SA/CH/AM/PM`; ô ngày giờ ISO `2026-06-12T08:00:00`, `12/06/2026 08:00:00`; số ngày có phần lẻ `46337.5` = ngày + 12:00. Chữ buổi viết đủ «sáng/chiều» **không** nhận: test của Soi Lỗi `test_hostile_ai_items_are_dropped_or_kept_as_designed` đòi «8:00 sáng» bị từ chối | `model.py` `_TIME_RE`, `parse_plan_time`, `split_date_time` |
| G3 | «Ngày dự kiến đã qua» chỉ khi «Thêm» hay khi đề xuất **đổi** ngày | `propose.py` `check_proposals` |
| G4 | Mọi thay đổi ở dòng «Đã hẹn giờ»/«Đã đăng» đều có `WARN_RELEASED` (không tick sẵn) | `propose.py` `check_proposals` |
| G5 | Chữ AI (từ khóa, từ khóa phụ, tiêu đề, ghi chú, lý do) có số điện thoại, email → cảnh báo `WARN_PERSONAL` | `propose.py` `from_ai`, `_has_personal` |
| G7 | Dòng tiêu đề tìm trong 5 dòng đầu (bỏ dòng tên bảng phía trên); ô Markdown in đậm/nghiêng/mã bỏ dấu bọc; Mã bài viết lại ít nhất 3 chữ số («B-1» = «B-001» = «B-0001»); đoán dấu phân cách CSV không tính chữ trong ngoặc kép | `parse.py` `_find_header`, `_md_cells`, `_csv_delimiter`; `model.py` `parse_key` |
| G8 (phần trong phạm vi) | AI đề xuất hơn 20 thay đổi một lần thì mọi đề xuất AI có cảnh báo `WARN_MANY_AI` (không tick sẵn) | `propose.py` `AI_MANY`, `from_ai` |

### Để lại (lý do)

| Mục | Lý do |
|---|---|
| G6 `DATA_RULES` chưa nêu 2 khung mới | Việc của T-103 (Ngòi Bút): LC-T094-42 giao giữ và viết lại `DATA_RULES`; lời dặn `plan` đã tự nói hai khung là dữ liệu |
| G8 phần còn lại | Của phiếu sau: T-100 trung hòa chữ bắt đầu `=` `+` `-` `@` khi ghi Sheet (LC-T094-28); T-101 hiện chữ thuần; T-101/T-102 gọi `personal_info` khi điền ghi chú vào Soạn bài |
| G2 chữ «sáng», «chiều» viết đủ | Test (không `xfail`) của Soi Lỗi đòi từ chối «8:00 sáng»; giữ như vậy, chỉ nhận dạng viết tắt mà Sheets/Excel hiện |
| SL-T098-5 dạng dính chữ «sđt0909123456» | Soi Lỗi không xếp lỗi (dễ nhầm mã hàng) |

### Test

- Gỡ 12 dấu `xfail` trong `tests/test_soi_loi_t098.py` (SL-T098-1 → -11) sau khi chạy `--runxfail`: **55 dòng xóa, 0 dòng thêm**, mọi dòng xóa là dấu `@pytest.mark.xfail(...)` (đã soát bằng `git diff`).
- Test của tôi đổi theo hành vi mới có chủ đích: `tests/test_plan_model.py` (`test_key_format`: «b-1» → «B-001», «kv-00012» → «KV-012»; `test_times`: thêm giây, SA/CH/AM/PM; `test_times_rejected`: bỏ `08:00:00`, thêm «13 PM», «0 AM», «8:00 sáng»…; thêm `test_split_date_time`), `tests/test_plan_parse.py` (mã `B-004`; thêm 6 test lượt 2), `tests/test_plan_propose.py` (thêm 7 test lượt 2). 4 file test của tôi: 251 ca.
- Nơi gọi `seo_app/plan` (grep): chỉ `seo_app/content/prompts.py` (`plan_prompt`), `seo_app/content/workflow.py` (`plan_changes`); có test ở `tests/test_plan_ai.py`, `tests/test_soi_loi_t098.py`.

```
$ uv run pytest -q -p no:cacheprovider -rfEX tests/test_plan_model.py tests/test_plan_parse.py \
    tests/test_plan_propose.py tests/test_plan_ai.py tests/test_soi_loi_t098.py \
    tests/test_soi_loi_t003_t009.py tests/test_t040_prompts.py tests/test_content_workflow.py \
    tests/test_prompt_data_frames.py tests/test_content_edge_cases.py
(2026-10-28 13:15:12 → 13:16:03 +0700)
625 passed in 47.84s

$ uv run ruff check .
All checks passed!
```

- Trước khi gỡ dấu: `uv run pytest --runxfail tests/test_soi_loi_t098.py tests/test_plan_model.py` → `303 passed`.
- Lượt 2 chỉ sửa 3 file trong `seo_app/plan/` và test; không đụng `seo_app/content/`, `app/`, `seo_app/wordpress/`, `seo_app/storage/`, `config/`.

---

## Lượt 3 (2026-10-28 15:51 +07:00) · Soi Lỗi lượt 2 (`9e7cea6`), Lá Chắn (`b520623`): sửa 6 lỗi Thấp SL-T098-12 → -17

Chỉ Huy B giao: sửa cả 6 lỗi Thấp trước khi gộp (Soi Lỗi và Lá Chắn đều khuyên, ưu tiên -13, -17, -12), theo gợi ý của Soi Lỗi; không lùi 11 lỗi đã đóng và các điều kiện LC-T094.

### Đã sửa

| Mã | Sửa | Chỗ |
|---|---|---|
| SL-T098-12 | Đọc CSV/TSV `strict` trước; **chỉ** «file hết mà ngoặc kép chưa đóng» (câu lỗi `unexpected end of data` của `csv`) là `BAD_TABLE` (giữ SL-T098-3); lỗi `strict` khác (ô mở đầu bằng chữ trong ngoặc kép rồi có chữ sau: «"Đức" là hãng tốt») thì đọc lại không `strict` như lượt 1. Bảng dán: `_looks_tabbed` vốn rơi về đếm dòng vật lý khi `csv` lỗi, nên nhận đúng là bảng | `parse.py` `_csv_rows` |
| SL-T098-13 | Bảng Markdown: dòng tiêu đề là dòng **ngay trước dòng phân cách** «\|---\|» (không dò); CSV/TSV: chỉ bỏ qua dòng phía trên có tối đa **một ô có chữ** (dòng tên bảng), gặp dòng có từ hai ô mà không có cột từ khóa thì thôi. Bảng «Mục – Nội dung» và `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md` không còn ra dòng giả | `parse.py` `_markdown_tables`, `_find_header`, `_rows_to_plan(header_at=…)` |
| SL-T098-14 | Viết tắt «p», «q» **đứng riêng** rồi tên là địa danh (chữ đã `keyword_key` nên dấu chấm thành dấu cách: «P. Tân Định» là «p tan dinh»); «phụ kiện» («phu») vẫn không bị bắt | `propose.py` `_LOCATION` |
| SL-T098-15 | Cảnh báo số điện thoại/email chỉ xét chữ **do AI đưa**: lý do; với «Thêm» mọi trường chữ, với «Cập nhật» chỉ trường AI đổi; «Bỏ» chỉ lý do. Ghi chú cũ có số khách không làm bỏ tick | `propose.py` `_has_personal` |
| SL-T098-16 | Số ngày có phần lẻ **toàn chữ số 0** («46337.0») là ngày trần, không đặt giờ 00:00 | `model.py` `_SERIAL_TIME_RE` |
| SL-T098-17 | `_Keys` tính số lớn nhất trực tiếp (`model.key_number`), dựng không bao giờ báo lỗi; chỉ khi cần cấp mã mới mới xét giới hạn. **Khác gợi ý một chút:** quá `B-99999` thì tìm số trống từ `B-001` (kế hoạch tối đa 1.000 dòng nên luôn còn), thay vì báo «hết mã» ngay; hết thật mới báo `PlanKeyError` câu cố định `KEYS_EXHAUSTED`. `PlanKeyError` là `ValueError` riêng; `ContentWriter.plan_changes` đổi nó thành `AIError` cùng câu (không lọt ra giao diện như lỗi lạ). `model.next_key` cũng báo `PlanKeyError` câu cố định | `propose.py` `_Keys`; `model.py` `key_number`, `next_key`, `PlanKeyError`; `workflow.py` `plan_changes` |

### Không lùi

- 11 lỗi đã đóng (SL-T098-1 → -11) và mọi test của Soi Lỗi vẫn qua: `--runxfail` trên `tests/test_soi_loi_t098.py` + 4 file kế hoạch: `558 passed` trước khi gỡ dấu.
- Điều kiện LC-T094 không đổi: dữ liệu vẫn qua `PlanRow` (bộ làm sạch chung); kiểm thẻ HTML trên chữ đã làm sạch và NFKC; dò số điện thoại/email trên chữ NFKC; biểu thức mới không quay lui (`_SERIAL_TIME_RE` chỉ thêm một lớp ký tự; `_LOCATION` bớt nhánh dấu chấm; `_csv_rows` đọc tối đa hai lượt, mỗi lượt tuyến tính và vẫn dừng ngay khi quá 1.000 dòng / 26 cột).

### Test

- Gỡ 6 dấu `xfail` (SL-T098-12 → -17) trong `tests/test_soi_loi_t098.py`: **35 dòng xóa, 0 dòng thêm**, mọi dòng xóa là dòng dấu `@pytest.mark.xfail(...)` (soát bằng `git diff`). Không đổi điều kiện ca nào.
- Thêm test của tôi: `tests/test_plan_propose.py` (cấp mã sau `B-99999` dùng số trống; hết mã thật ra câu cố định), `tests/test_plan_parse.py` (CSV gặp dòng hai ô thì thôi dò tiêu đề; ngoặc kép mở tới hết file vẫn `BAD_TABLE`; Markdown lấy dòng trước dòng phân cách), `tests/test_plan_ai.py` (`PlanKeyError` thành `AIError` câu cố định).

```
$ uv run pytest -q -p no:cacheprovider -rfEX tests/test_plan_model.py tests/test_plan_parse.py \
    tests/test_plan_propose.py tests/test_plan_ai.py tests/test_soi_loi_t098.py \
    tests/test_soi_loi_t003_t009.py tests/test_t040_prompts.py tests/test_content_workflow.py \
    tests/test_prompt_data_frames.py tests/test_content_edge_cases.py
(2026-10-28 15:50:13 → 15:51:27 +0700)
745 passed in 70.26s (0:01:10)

$ uv run ruff check .
All checks passed!
```

- `tests/test_la_chan_t098.py` không có (Lá Chắn không thêm file test).
- Lượt 3 sửa `seo_app/plan/model.py`, `parse.py`, `propose.py`, `seo_app/content/workflow.py` (chỉ `plan_changes`) và test; không đụng `app/`, `seo_app/wordpress/`, `seo_app/storage/`, `config/`.

## Lượt 4 (2026-10-28 19:02 +07:00) · Soi Lỗi lượt 3 (`2e0d29b`): sửa 3 lỗi Thấp SL-T098-18 → -20

Chỉ Huy B giao (28/10 18:50, sau khi T-098 gộp `main` `24013b3`): sửa 3 lỗi Thấp trước T-100, T-101, theo gợi ý của Soi Lỗi; không lùi SL-T098-1 → -17 và các điều kiện LC-T094 (thẻ HTML, ký tự vô hình, số điện thoại/email, không có biểu thức chạy lâu).

### Tóm tắt (cho chủ dự án)

- File CSV quên đóng một dấu ngoặc kép: nay luôn báo «Không đọc được bảng…», kể cả khi phía dưới còn ô có ngoặc kép (trước đó các dòng ở giữa bị gộp vào một ô, không báo).
- Bảng «brief» (dòng tên ở trên rồi các dòng «Từ khóa, …», «Ngày, …») không còn ra bài giả; nội dung được coi là ghi chú để AI đọc.
- Dòng mới tự ghi Mã bài (ví dụ «B-004») giữ đúng mã đó, dù đứng sau một dòng mới chưa có mã; đưa lại cùng file thì không ra đề xuất lạ.

### Đã sửa

| Mã | Sửa | Chỗ |
|---|---|---|
| SL-T098-18 | Sau lượt đọc lại không `strict`, `_merged_by_quote` đi theo đúng cách `csv` đọc ngoặc kép: ngoặc chỉ mở ô khi đứng đầu ô; «""» trong ngoặc là một dấu ngoặc. Nó báo `BAD_TABLE` trong 2 trường hợp: (1) phần trong ngoặc **qua nhiều dòng** rồi «đóng» ở một dấu ngoặc có chữ theo sau, thật ra là dấu mở của một ô phía dưới; (2) tới hết file mà ngoặc vẫn chưa đóng. Trường hợp (2) là dạng gần mới: ô «"Đức" là hãng» đứng **trước** làm lượt `strict` dừng sớm, rồi một ngoặc phía dưới không đóng. **Khác gợi ý «ô nào có xuống dòng thì là lỗi»:** bảng chép từ Google Sheets có cả ô nhiều dòng (SL-T098-10) lẫn ô «"Đức" là hãng» (SL-T098-12) vẫn đọc được; theo gợi ý thì bảng đó sẽ báo lỗi oan. Mỗi ký tự xét một lần (tìm bằng `re`/`str.find`, không quay lui) | `parse.py` `_csv_rows`, `_merged_by_quote` |
| SL-T098-19 | CSV/TSV: đã bỏ qua dòng tên thì dòng tiêu đề phải nhận ra **ít nhất hai cột**, hoặc mọi ô có chữ đều là tên cột (bảng một cột «Từ khóa» dưới dòng tên vẫn đọc, cột «Từ khóa» ghi trùng hai lần cũng vậy). «BRIEF BÀI VIẾT / Từ khóa, sửa cửa cuốn / Ngày, …» thành chữ tự do như lượt 1. Đánh đổi: dòng tên + tiêu đề chỉ có «Từ khóa» và một cột lạ (ví dụ «Người phụ trách») cũng thành chữ tự do; AI vẫn đọc được, không mất chữ. Bảng không có dòng tên giữ như cũ | `parse.py` `_find_header` |
| SL-T098-20 | `compare_rows` **giữ trước** mọi mã mới ghi sẵn trong bảng (mã chưa có trong kế hoạch, dòng không «Bỏ»), rồi mới cấp mã cho dòng mới chưa có mã và dòng cũ chưa có mã. Hai dòng ghi cùng một mã mới: dòng đầu giữ, dòng sau được cấp mã mới (như trước); dòng «Bỏ» không giữ mã | `propose.py` `compare_rows` |

### Không lùi

- Mọi test của Soi Lỗi (SL-T098-1 → -20) qua; trong `tests/test_soi_loi_t098.py` không còn dấu `xfail` nào.
- Điều kiện LC-T094 không đổi: lượt này không đụng `PlanRow`, bộ làm sạch, kiểm thẻ HTML, dò số điện thoại/email. Biểu thức mới duy nhất là `(?<![^\n<dấu phân cách>])"`, chỉ nhìn lùi một ký tự. Test `test_quote_check_time_grows_linearly`: chữ dài gấp 8 thì thời gian dưới 16 lần.
- So bản `main` (`24013b3`) với bản mới:
  - 11 file thật trong `docs/plan/`: kết quả giống hệt (số dòng, chữ tự do, câu báo, dòng bỏ).
  - 40.000 CSV ngẫu nhiên có ô ngoặc chuẩn, ô nhiều dòng, «"Đức" là hãng», ô `""`: không có `BAD_TABLE` mới nào. Khác biệt duy nhất là ca dòng tên + tiêu đề có cột lạ (đánh đổi của SL-T098-19 ở trên).
  - Khi thêm ô ngoặc không đóng: mọi `BAD_TABLE` mới đều có ngoặc không đóng.
  - Script thử ở thư mục scratchpad, không commit.

### Test

- Gỡ 3 dấu `xfail` (SL-T098-18 → -20) trong `tests/test_soi_loi_t098.py`: **18 dòng xóa, 0 dòng thêm**; mọi dòng xóa là dòng dấu `@pytest.mark.xfail(...)` (soát bằng `git diff`). Không đổi điều kiện ca nào.
- Thêm 10 test của tôi:
  - `tests/test_plan_parse.py`, 7 test:
    - ngoặc không đóng sau ô «"Đức" là hãng» vẫn `BAD_TABLE`;
    - ô nhiều dòng (có «""») cùng ô «"Đức" là hãng» đọc đủ, cả CSV lẫn bảng dán;
    - thời gian kiểm ngoặc tuyến tính;
    - dòng tên + tiêu đề chỉ có «Từ khóa» vẫn là kế hoạch;
    - brief dưới dòng tên là chữ tự do, cả CSV lẫn bảng dán.
  - `tests/test_plan_propose.py`, 3 test:
    - mã ghi sẵn được giữ, đưa lại cùng bảng thì không có đề xuất;
    - dòng cũ chưa mã không lấy mã ghi sẵn;
    - mã ghi trùng hay ở dòng «Bỏ» không được giữ.

```
$ uv run pytest -q tests/test_plan_model.py tests/test_plan_parse.py tests/test_plan_propose.py \
    tests/test_plan_ai.py tests/test_soi_loi_t098.py tests/test_soi_loi_t003_t009.py \
    tests/test_t040_prompts.py tests/test_content_workflow.py tests/test_prompt_data_frames.py \
    tests/test_content_edge_cases.py
(2026-10-28 19:00:44 → 19:02:21 +0700)
781 passed in 91.08s (0:01:31)

$ uv run ruff check .
All checks passed!
```

- Lượt 4 chỉ sửa `seo_app/plan/parse.py`, `seo_app/plan/propose.py` và test; không đụng `app/`, `seo_app/content/`, `seo_app/google/`, `config/`.
- Ghi cho T-101 (như lượt 3): `compare_rows` có thể báo `PlanKeyError` (chỉ khi hết thật 99.999 mã), nên bắt và hiện câu cố định của nó.

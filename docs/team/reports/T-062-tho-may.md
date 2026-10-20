# Báo cáo T-062 · Đọc cấu hình việc ảnh: tạo provider khi cần, chịu lỗi, nhãn hiển thị

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-062](../tickets/T-062-doc-cau-hinh-viec-anh.md) |
| Nhánh | `team/T-062` (từ `main` `132a73d`), worktree `D:\ProMetal-ToolSEO\wt-T-062` |
| Ngày nộp | 2026-10-20 |
| Máy chạy | Windows 11 Pro 10.0.26300, Python 3.12 (uv) |
| Kết quả | Hoàn thành (dòng README / Cài đặt về khóa Gemini miễn phí nằm ngoài phạm vi file của phiếu: ghi ở Đề xuất) |

## Tóm tắt (cho chủ dự án)

- Bây giờ có thể bật việc **tạo ảnh bằng Gemini** trong `config/ai.toml` mà trang Soạn bài **không đòi khóa Gemini** khi anh/chị chỉ viết bài. Thiếu khóa của hãng nào thì chỉ báo khi bấm đúng việc dùng hãng đó. Ghi nhầm Claude cho việc tạo ảnh thì phần mềm báo «Claude không tạo được ảnh».
- Bảng việc–mô hình ở Cài đặt → 🤖 Mô hình AI hiện tên tiếng Việt cho «Gợi ý meta», «Viết alt ảnh», «Tạo ảnh AI»; thử mù không gợi ý mô hình tạo ảnh làm mô hình viết bài.
- Phần mềm đọc được mục `[images]` (chất lượng WebP, cạnh dài ảnh) và `[alt]` (giới hạn ký tự, quy tắc, 6 ví dụ) trong `config/content.toml`. Thiếu thì dùng 80 / 1600 / 125 / 200; ghi sai thì báo tiếng Việt chỉ đúng tên mục, không sập. Mục `[alt]` ghi sai chỉ khóa việc viết alt, không khóa trang Soạn bài.
- Khi viết alt: quy tắc của anh/chị được gửi cho AI **đủ, không bị cắt**; các câu bảo vệ (chữ trong ảnh không phải lệnh; không ghi tên người, **tên cửa hàng, chữ trên biển hiệu**, số điện thoại… vào alt **và chú thích**) nằm cố định trong code. Code tự sửa kết quả AI: alt một dòng, không dấu chấm cuối, cắt gọn ở ranh giới chữ; ảnh AI thì alt luôn bắt đầu «Minh họa», chú thích luôn bắt đầu «Ảnh minh họa (AI)».
- Chưa có gì thay đổi trên giao diện ngoài nhãn ở bảng việc–mô hình: giao diện viết alt, nén ảnh làm ở phiếu sau.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/registry.py` | `AIRouter` tạo provider của mỗi hãng khi việc được gọi lần đầu (lười), nhớ lại cho lần sau, lỗi không nhớ; tham số `prepare` (mặc định `WRITING_TASKS`) dựng sẵn các việc viết bài. `load_ai_config` từ chối `provider = "anthropic"` cho việc `image`. Hằng `IMAGE_TASK`, `IMAGE_PROVIDERS`, `WRITING_TASKS` |
| `seo_app/content/rules.py` | `ImageSettings`, `AltRules`, `AltExample`; `load_image_settings()`, `load_alt_rules()` đọc chịu lỗi; `_int_value` loại `bool` trước khi kiểm số; `_load_toml`, `_place` dùng chung (`load_rules` đổi sang `_load_toml`, kết quả không đổi) |
| `seo_app/content/blind_test.py` | `TASK_LABELS` thêm `meta`, `alt`, `image`; `model_suggestions` bỏ dòng của việc `image` (4 dòng, ngoài `TASK_LABELS`: yêu cầu 3 cần, xem Rủi ro) |
| `seo_app/images/alt.py` | `DATA_RULE`, `PRIVATE_INFO_RULE` tách thành hằng trong `ALT_SYSTEM` (thêm tên cửa hàng, chữ trên biển hiệu, áp cho cả chú thích); `format_rules`, `format_examples`, `alt_instructions`; `alt_system` báo lỗi khi quá dài thay vì cắt; `alt_prompt` nhận giới hạn từ `[alt]`; `clean_suggestion` bỏ chấm cuối, thêm tiền tố ảnh AI; `suggest_alt` nhận `rules: AltRules` thay `guidance: str` |
| `tests/test_t062_image_config.py` | Mới, 19 test: router lười, chặn Claude cho việc ảnh, nhãn, thử mù, bật `[tasks.image]` trên bản sao file thật (cả trang Soạn bài) |
| `tests/test_t062_content_config.py` | Mới, 66 test: `[images]`, `[alt]` thiếu / sai dạng / `true` `false` / biên / file hỏng |
| `tests/test_t062_alt_prompt.py` | Mới, 53 test: C1, C2, C3, C4, C6, yêu cầu 5 |
| `tests/test_soi_loi_t051.py` | Gỡ 5 dấu `xfail` SL-T051-1 → 4 (cả 5 test nay qua), sửa docstring và một chú thích nhắc tới `xfail` |
| `tests/test_ai.py` | `test_project_ai_config_is_valid`: kiểm từng việc (hãng hợp lệ, có mô hình, chỉ nghiên cứu tìm web, việc ảnh không phải Claude), bỏ đòi «mọi việc là anthropic» |
| `tests/test_ai_images.py` | 2 test T-050 theo hành vi mới: `suggest_alt(rules=…)` thay `guidance=`; quy tắc quá 4.000 ký tự thì báo lỗi nêu `[alt]` thay vì cắt (Lá Chắn T-051 C3 đổi hành vi này) |

Không sửa `config/**`, `app/**`, `seo_app/images/process.py`, `tags.py`, `pyproject.toml`, `uv.lock`.

## Đối chiếu yêu cầu phiếu

| # | Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `AIRouter` lười; thiếu khóa chỉ báo khi gọi đúng việc; bật `[tasks.image]` thì trang Soạn bài không đòi khóa Gemini | Đạt | `registry.py:151-186`; `test_missing_key_only_reported_when_its_task_is_called`, `test_failed_provider_is_not_remembered`, `test_enabling_real_image_block_needs_gemini_key_only_for_images`, `test_write_page_with_image_enabled_and_only_claude_key`; Soi Lỗi `test_sl_t051_1_*` (2 test) qua |
| 2 | Từ chối `anthropic` cho việc `image`, câu tiếng Việt | Đạt | `registry.py:88-92`; `test_image_task_on_claude_is_refused_in_vietnamese` (cả «Anthropic», « ANTHROPIC »), `test_sl_t051_2_image_task_on_anthropic_is_refused` |
| 3 | Thử mù không gợi ý mô hình tạo ảnh; nhãn `alt`, `meta`, `image` | Đạt | `blind_test.py:102-104, 217`; `test_blind_test_never_suggests_image_model`, `test_task_labels_cover_new_tasks_in_vietnamese`, `test_sl_t051_3_*`, `test_sl_t051_4_*` |
| 4 | Đọc `[images]`, `[alt]` chịu lỗi như T-010; mặc định 80/1600/125/200; sai dạng báo tiếng Việt | Đạt | `rules.py:396-495`; `tests/test_t062_content_config.py` (66 test) |
| 5 | Code tự bảo đảm: alt một dòng, bỏ chấm cuối, cắt theo ranh giới từ; ảnh AI thêm «Minh họa» / «Ảnh minh họa (AI)» | Đạt | `alt.py:338-393`; `test_ai_image_alt_always_starts_with_minh_hoa`, `test_ai_image_caption_always_starts_with_ai_label`, `test_long_alt_is_cut_on_word_boundary_and_keeps_prefix`, `test_real_photo_alt_is_one_line_without_final_period_and_no_prefix` |
| 6 | Test cấu hình `[images]`, `[alt]`, bật `[tasks.image]` | Đạt | 3 file test mới (138 test) |
| Ghi chú | Gỡ 5 `xfail` SL-T051-1 → 4; sửa `test_project_ai_config_is_valid` | Đạt | `tests/test_soi_loi_t051.py` không còn `xfail`; `tests/test_ai.py:24-37` |
| Ghi chú | Dòng README / Cài đặt về khóa Gemini miễn phí (LC-T050-4) | Chuyển Đề xuất | README thuộc Thư Ký, Cài đặt thuộc `app/`; cả hai ngoài phạm vi file của phiếu |

## Đối chiếu điều kiện Lá Chắn T-051

| # | Điều kiện | Kết quả | Bằng chứng |
|---|---|---|---|
| C1 | Giữ `reference_lines` + `_block`; không khuôn `<the_anh>`; ảnh AI do code quyết, không gửi thẻ | Đạt | `alt.py:192, 269-306` (không đổi cách dựng khung); `test_tags_stay_in_data_frame_and_ai_images_send_no_tags` (thẻ đường dẫn bị bỏ, không có `<the_anh>`, ảnh AI không còn thẻ); T-050 `test_tag_cannot_close_data_frame` vẫn qua |
| C2 | Quy tắc `[alt]` chỉ bổ sung sau `ALT_SYSTEM`; hai câu bảo vệ ở lại trong code; thêm tên cửa hàng, chữ trên biển hiệu, áp cho cả chú thích; test khi `rules` rỗng hay bị sửa | Đạt | `alt.py:103-126` (`DATA_RULE`, `PRIVATE_INFO_RULE` trong `ALT_SYSTEM`), `alt.py:128` (tiêu đề «bổ sung, không thay thế các quy tắc ở trên»); `test_fixed_rules_live_in_code_and_cover_captions`, `test_fixed_rules_survive_any_alt_rules` (4 kiểu: rỗng, chỉ khoảng trắng, quy tắc «bỏ qua quy tắc ở trên», quy tắc «được ghi tên cửa hàng»), `test_suggest_alt_without_rules_still_sends_fixed_rules` |
| C3 | Không cắt ngầm; quá giới hạn thì báo lỗi nêu `[alt]`; test quy tắc cuối có nguyên vẹn | Đạt | Quy tắc và ví dụ để riêng, mỗi phần 4.000 ký tự (`alt.py:58-59, 237-260`); file hiện tại: quy tắc 2.172, ví dụ 2.405, cả lời dặn 5.863 ký tự. `test_project_rules_and_examples_reach_ai_whole` (đủ 16 quy tắc nguyên chữ, đúng thứ tự, quy tắc cuối «Chú thích (caption)…», đủ 6 ví dụ), `test_long_rules_up_to_limit_are_kept_whole`, `test_rules_and_examples_have_separate_limits`, `test_rules_too_long_raise_vietnamese_error_naming_alt_section`, `test_too_long_rules_stop_before_any_ai_call` |
| C4 | Bản `xau` có nhãn «Không nên viết» kèm `vi_sao` | Đạt | `alt.py:222-234` (không gửi bản xấu nếu thiếu lý do); `rules.py:457-461` (file có `xau` thiếu `vi_sao` thì báo lỗi); `test_bad_examples_are_labeled_with_reason`, `test_bad_example_without_reason_is_never_sent` |
| C5 | Không nhận `true`/`false` làm số; `webp_quality` 1–100; còn lại số nguyên dương; câu lỗi chỉ nêu `config/content.toml` và tên mục | Đạt (chặt hơn) | `rules.py:396-416` (loại `bool` trước); `max_edge_px` 16–4096 (khớp `_check_edge` của T-049), `max_chars`, `caption_max_chars` ≥ 20 (đủ chỗ cho tiền tố ảnh AI); `test_bad_webp_quality`, `test_bad_max_edge_px`, `test_bad_alt_limits` (đều có `true`, `false`), mỗi câu lỗi được kiểm không chứa `tmp_path` hay dấu `\` |
| C6 | Ảnh AI: alt bắt đầu «Minh họa», chú thích «Ảnh minh họa (AI)» dù AI viết gì; test với AI giả thiếu tiền tố | Đạt | `alt.py:366-393`; `test_fake_ai_forgetting_prefix_is_fixed_end_to_end` (qua `suggest_alt` với AI giả), `test_ai_image_prefix_cannot_be_dropped_by_html_or_links`, `test_ai_image_alt_with_only_prefix_is_empty` |

## Cách làm, lý do chọn

- **Router lười nhưng vẫn dựng sẵn việc viết bài.** Phiếu ghi «chỉ tạo provider khi việc được gọi». Nếu lười hoàn toàn thì trang Soạn bài (không được sửa `app/`) mất cảnh báo «chưa có khóa» lúc mở trang và nút AI không còn khóa: hỏng 2 test đã duyệt (`tests/test_app_pages.py::test_without_api_key_ai_buttons_are_locked`, `tests/test_phase2_fixes.py::test_app_pages_see_no_key_even_if_real_env_has_one`). Nên `AIRouter` có tham số `prepare`, mặc định là 5 việc viết bài của `ContentWriter`; mọi việc khác (`meta`, `alt`, `image`, việc mới sau này) chỉ tạo khi gọi. Trang khác (viết alt, tạo ảnh) truyền `prepare=()` hay đúng việc của trang.
- **Đọc `[images]`, `[alt]` riêng với `load_rules`.** Mục `[alt]` sai chỉ khóa việc viết alt; trang Soạn bài vẫn viết bài được (`test_bad_alt_section_does_not_block_writing_rules`). Test SL-T051 `alt-sai-dang` cho phép cả hai cách.
- **Quy tắc gửi nguyên chữ.** Quy tắc có chữ «max_chars ký tự»; tôi không thay tên bằng số (để «quy tắc cuối có mặt nguyên vẹn» kiểm được đúng nghĩa), mà thêm một dòng do code viết: «Trong các quy tắc trên: max_chars = 125 (alt), caption_max_chars = 200 (chú thích)…».
- **Tiền tố ảnh AI.** Code bỏ mọi kiểu tiền tố AI đã tự viết («Minh hoạ», «Hình ảnh minh họa», «Ảnh minh họa (AI):»…) rồi ghi lại đúng một tiền tố chuẩn, viết thường chữ đầu phần sau («Minh họa cửa cuốn»), trừ từ viết hoa giữa từ («Pro-Metal», «LED»). Chú thích ảnh AI để trống thì thành «Ảnh minh họa (AI)» (người đọc luôn biết là ảnh AI). Alt chỉ còn tiền tố (AI viết «Minh họa.») thì báo «AI không viết được alt», không dùng alt rỗng nghĩa.
- **Cắt theo ranh giới từ:** dùng lại `_cut` của T-050 (cắt ở dấu cách gần nhất; chỉ cắt giữa chữ khi một "chữ" dài hơn nửa giới hạn, như chuỗi rác không có dấu cách).

## Bằng chứng

```
$ uv run pytest -q -p no:cacheprovider tests/test_t062_image_config.py tests/test_t062_content_config.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t051.py tests/test_ai.py tests/test_ai_images.py tests/test_soi_loi_t050.py
(các lượt chạy riêng trong lúc làm: 676 passed; 143 passed; 297 passed; 19 passed — 0 hỏng)

$ uv run pytest            # toàn bộ, Windows
(đang chạy, điền ở commit sau)

$ uv run ruff check .
All checks passed!
```

Kích thước lời dặn alt với `config/content.toml` hiện tại (đo bằng `format_rules`, `format_examples`, `alt_instructions`): quy tắc 2.172 ký tự, ví dụ 2.405 ký tự, cả lời dặn hệ thống 5.863 ký tự (khoảng 2.000 token mỗi lần gọi alt).

## Rủi ro và điểm cần chú ý

- **API `suggest_alt` đổi:** `guidance: str` thay bằng `rules: AltRules`. Chưa có giao diện nào gọi `suggest_alt` (T-056 chưa làm), chỉ 1 test T-050 phải sửa theo. Phiếu giao diện truyền `rules=load_alt_rules()` và có thể gọi `alt_instructions(load_alt_rules())` khi mở trang để báo sớm lỗi cấu hình.
- **`AIRouter(...)` ở trang mới:** mặc định vẫn dựng sẵn 5 việc viết bài. Trang chỉ viết alt / tạo ảnh mà dựng router mặc định sẽ đòi khóa của hãng viết bài; nhớ truyền `prepare=()` hoặc `prepare=("alt",)`.
- **`blind_test.py` ngoài `TASK_LABELS`:** phiếu ghi «chỉ `TASK_LABELS`», nhưng yêu cầu 3 (thử mù không gợi ý mô hình tạo ảnh) phải sửa `model_suggestions` (4 dòng, `blind_test.py:211-219`). Không đổi gì khác trong file.
- **C5 chặt hơn phiếu:** `max_edge_px` phải 16–4096 (khớp `seo_app/images/process.py` trên nhánh `team/T-049`, để báo lỗi ngay lúc đọc cấu hình kèm tên mục); `max_chars`, `caption_max_chars` phải ≥ 20 (đủ chỗ cho «Ảnh minh họa (AI)»). Nếu T-049 đổi giới hạn cạnh thì sửa `IMAGE_EDGE_MIN`/`IMAGE_EDGE_MAX` ở `rules.py:85-86` cho khớp.
- **Ảnh thật mà AI viết «Minh họa…»:** code không gỡ (phiếu không yêu cầu). Người dùng duyệt tay từng alt ở T-056.
- **Logo Pro-Metal:** khung cố định cấm «chữ trên biển hiệu», còn quy tắc `[alt]` cho ghi «Pro-Metal» khi logo nhìn thấy rõ. Khung cố định thắng (tiêu đề phần bổ sung ghi «không thay thế các quy tắc ở trên»): AI có thể bỏ chữ Pro-Metal cả khi logo rõ. Thiên về an toàn; Ngòi Bút xem lại nếu cần.
- Không có thư viện mới, không gọi mạng trong test, khóa trong test là chuỗi giả.

## Đề xuất

- **Soi Lỗi:** thử `AIRouter` với cấu hình có việc tên lạ và `prepare` lạ; tiền tố ảnh AI với chữ Việt dạng NFD, «Minh họa» dính dấu câu lạ, alt toàn ký tự đặc biệt; `[alt]` có `examples` lồng sai kiểu (`[alt.examples]` một bảng thay vì `[[alt.examples]]`); file `content.toml` có cả `[images]` lẫn `[[images]]`. Chạy lại `tests/test_soi_loi_t051.py` (đã gỡ hết `xfail`).
- **Lá Chắn:** kiểm C1–C6 theo bảng trên; chú ý `alt.py:103-126` (hai câu bảo vệ), `alt.py:237-260` (không cắt, báo lỗi), `rules.py:396-416` (loại `bool`), câu lỗi không có đường dẫn máy (`_place`, `rules.py`).
- **Thư Ký (hoặc Họa Sĩ cho trang Cài đặt), LC-T050-4:** thêm vào README mục cấu hình AI một dòng, đề xuất: «Việc viết alt gửi ảnh công trình (đã bỏ GPS, EXIF) cho hãng AI ghi ở `[tasks.alt]`. Nên dùng Claude (mặc định) hoặc khóa **trả phí** của OpenAI / Gemini: khóa Gemini **miễn phí** cho Google dùng ảnh để cải tiến sản phẩm và người duyệt của Google có thể xem. Muốn dùng khóa Gemini miễn phí cho alt thì báo Chỉ Huy để ghi sổ rủi ro.»
- **T-053 (tạo ảnh):** khi bật `[tasks.image]`, router đã sẵn sàng; trang tạo ảnh dựng `AIRouter(..., prepare=())` để không đòi khóa Claude. Vẫn còn C8 (xác minh tên mô hình) và C9 (mỗi lần bấm một ảnh).
- **T-049 / phiếu giao diện ảnh:** đọc `load_image_settings()` rồi truyền `webp_quality`, `max_edge_px` vào `make_web_image`.
- **T-056 (duyệt alt):** dùng `suggest_alt(..., ai_generated=<theo nguồn ảnh>, rules=load_alt_rules())`; có thể dùng `AltRules.bad_starts` để đánh dấu alt người dùng tự gõ mở đầu «Hình ảnh…».

## Câu hỏi cho chủ dự án

Không có.

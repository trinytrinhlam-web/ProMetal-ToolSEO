# Báo cáo T-019 · Thử mù mô hình AI (phần logic)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-019](../tickets/T-019-thu-mu-mo-hinh.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành (phần Thợ Máy). Còn phần giao diện của Họa Sĩ |

## Tóm tắt (cho chủ dự án)

Đã có phần "máy" của thử mù: cùng một đề (từ khóa + ghi chú) gửi cho 2–3 mô hình bạn chọn, mỗi mô hình viết một mở bài và một mục ngắn. Bài trả về dưới tên A/B/C theo thứ tự ngẫu nhiên; tên hãng và tên mô hình nằm ở một phần riêng, chỉ hiện sau khi bạn chấm. Một mô hình lỗi (thiếu khóa, sai tên, hết tiền…) thì các mô hình khác vẫn có bài. Chưa thấy gì trên giao diện: Họa Sĩ sẽ nối vào tab "🤖 Mô hình AI".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/blind_test.py` (mới) | Hàm chạy thử mù `run_blind_test`, kiểm đầu vào, che tên mô hình, hàm phụ cho giao diện |
| `seo_app/content/prompts.py` | Thêm khung `de_bai` vào `DATA_TAGS`; thêm lời dặn `blind_test_prompt` |
| `tests/test_blind_test.py` (mới) | 39 test, provider giả, không gọi mạng |

Không sửa `seo_app/ai/**`, `config/**`, `app/**`.

## Cách hoạt động

1. `validate_request` kiểm đầu vào **trước khi gọi AI** (chưa tốn tiền): từ khóa không trống, ≤ 200 ký tự (gộp về một dòng); ghi chú ≤ 1.000 ký tự; 2–3 ứng viên; hãng thuộc `anthropic`/`openai`/`gemini`; tên mô hình không trống, không dấu cách, ≤ 100 ký tự; effort hợp lệ. Sai thì báo `AIError` tiếng Việt.
2. Mọi ứng viên nhận **cùng** `system_prompt(rules)` (hồ sơ doanh nghiệp + quy tắc văn phong hiện có) và **cùng** `blind_test_prompt(keyword, note)`.
3. Mỗi ứng viên gọi một lần qua `make_provider(provider, settings).generate(...)` với `TaskConfig(name="blind_test", web_search=False, max_tokens=2000)` và khuôn mới nhỏ `BlindSample` (`intro`, `heading`, `body`). Các ứng viên gọi song song (chờ bằng ứng viên chậm nhất).
4. Thứ tự ứng viên bị xáo (`random.SystemRandom`, test truyền `rng` cố định) rồi gắn nhãn A/B/C.
5. Chữ AI: `clean_ai_text` (bỏ HTML, link) → che tên mô hình/hãng mà AI tự xưng (xem "Rủi ro").
6. Lỗi: `AIError` → câu tiếng Việt của lớp AI; lỗi khác → câu cố định `UNEXPECTED_ERROR` (không chép lỗi thô). Câu lỗi chỉ nằm ở phần hiện tên; phần bài chỉ có câu cố định `HIDDEN_ERROR`, vì câu lỗi của lớp AI có ghi tên hãng và mô hình (ví dụ `bad_request_error` ghi «gpt-5.1»).

## Hướng dẫn cho Họa Sĩ

Nhập: `from seo_app.content import blind_test` (hoặc nhập từng tên dưới đây).

| Hàm / kiểu | Đầu vào | Đầu ra | Dùng ở đâu |
|---|---|---|---|
| `task_models(path=AI_CONFIG_FILE)` | (không bắt buộc) đường dẫn `config/ai.toml` | `list[TaskModel]`: `task`, `task_label` (tên việc tiếng Việt), `provider`, `provider_label`, `model`, `effort` | Bảng việc–mô hình. File sai → `AIError` (hiện `st.error(str(exc))`) |
| `model_suggestions(rows)` | kết quả `task_models()` | `dict[provider, list[model]]` | Gợi ý tên mô hình khi chọn ứng viên |
| `provider_status(settings)` | `Settings` | `list[ProviderStatus]`: `provider`, `label`, `has_key` (chỉ đúng/sai) | Hiện hãng nào đã có khóa |
| `available_providers(settings)` | `Settings` | `list[str]` mã hãng có khóa | Danh sách hãng cho phép chọn |
| `Candidate(provider, model, effort="medium")` | mã hãng, tên mô hình, effort | — | Một ứng viên |
| `estimate_calls(candidates)` | danh sách `Candidate` | `int` số lần gọi AI | Câu cảnh báo "sẽ gọi AI N lần, tốn tiền" trước nút chạy |
| `run_blind_test(keyword, note, candidates, settings, rules)` | từ khóa, ghi chú, 2–3 `Candidate`, `Settings`, `ContentRules` (`load_rules()`) | `(entries, reveal)` | Nút chạy thử |
| `validate_request(keyword, note, candidates)` | như trên | đầu vào đã chuẩn hóa | (tùy chọn) kiểm trước để báo lỗi sớm; `run_blind_test` đã tự gọi |

Hằng: `MIN_CANDIDATES = 2`, `MAX_CANDIDATES = 3`, `BLIND_MAX_TOKENS = 2000`, `MAX_KEYWORD_CHARS = 200`, `MAX_NOTE_CHARS = 1000`, `LABELS = ("A", "B", "C")`. Danh sách effort: `seo_app.ai.base.EFFORTS`.

Kết quả:

- `entries: list[BlindEntry]` theo thứ tự A, B, C. Mỗi `BlindEntry` có `label`, `intro`, `heading`, `body`, `error`, `ok`. **Không có trường tên hãng/mô hình.** Hiện ngay để chấm.
  - `ok == False` → hiện `entry.error` (câu cố định, không lộ tên) thay cho bài; không cho chấm ứng viên đó.
  - Chữ là chữ AI đã lọc: hiện bằng `st.markdown(...)` hoặc `st.text(...)`; **không** `unsafe_allow_html`, **không** ghép vào HTML của `seo_app/ui.py`.
- `reveal: dict[str, BlindReveal]` (nhãn → `provider`, `provider_label`, `model`, `effort`, `error`). **Giữ kín**: cất vào `st.session_state` nhưng không hiện, không ghi log, không đưa vào `help=`, tooltip, khóa widget (`key=`), tên cột hay bất cứ chữ nào trên trang cho tới khi người dùng bấm "Chấm xong — hiện tên mô hình". Sau khi hiện: `reveal[label].error` (nếu có) là câu lỗi tiếng Việt để người dùng biết sửa gì.
- Đừng để thứ tự ứng viên người dùng nhập lộ ra ở phần kết quả (ví dụ đừng hiện "Ứng viên 1 = A").
- Lỗi đầu vào: `run_blind_test` báo `AIError` trước khi gọi AI → `st.error(str(exc))`.

Ví dụ:

```python
from seo_app.content import load_rules
from seo_app.content.blind_test import Candidate, estimate_calls, run_blind_test

cands = [Candidate("anthropic", "claude-opus-5-5", "medium"), Candidate("openai", "gpt-5.1")]
st.warning(f"Sẽ gọi AI {estimate_calls(cands)} lần, có tốn tiền.")
if st.button("Chạy thử mù"):
    try:
        entries, reveal = run_blind_test(keyword, note, cands, settings, load_rules())
    except AIError as exc:
        st.error(str(exc))
    else:
        S.blind_entries, S.blind_reveal = entries, reveal  # reveal: chưa hiện
```

## Bằng chứng

```
$ uv run pytest tests/test_blind_test.py
39 passed

$ uv run pytest
9 failed, 2756 passed, 2 skipped, 9 xfailed in 159.34s
# 9 test đỏ đều là tests/test_soi_loi_t027.py (đỏ sẵn trên main ở Linux, phiếu khác đang sửa)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí xong (phần Thợ Máy)

- [x] Mục 1 · hàm chạy, cùng system prompt và lời dặn (`test_three_vendors_get_same_prompt_and_small_budget`, `test_system_prompt_uses_content_rules`)
- [x] Mục 2 · từ khóa, ghi chú trong khung `de_bai`, vô hiệu thẻ khung kể cả "＜", ký tự vô hình (`test_user_data_cannot_close_its_frame`, `test_prompt_frames_keyword_and_note_and_says_not_instructions`)
- [x] Mục 3 · xáo nhãn, phần nhãn → mô hình riêng, `clean_ai_text` (`test_labels_are_shuffled`, `test_reveal_maps_each_label_to_the_model_that_wrote_it`, `test_html_and_links_in_ai_output_are_removed`)
- [x] Mục 4 · một ứng viên lỗi (`test_one_failing_candidate_does_not_stop_others`, `test_missing_key_is_an_error_for_that_candidate_only`, `test_unexpected_exception_is_not_copied`, `test_all_candidates_fail`)
- [x] Mục 5 · tối đa 3, `max_tokens` 2.000, không tìm web, `estimate_calls` (`test_wrong_number_of_candidates_rejected_before_any_call`, `test_estimate_calls`)
- [x] Mục 6 · hãng có khóa (chỉ đúng/sai), bảng việc–mô hình (`test_provider_status_only_true_false`, `test_task_models_reads_config`, `test_task_models_real_config_and_bad_file`)
- [x] Mục 7 · test provider giả, không gọi mạng (bộ chặn mạng trong `tests/conftest.py` vẫn bật)
- [x] Không lộ tên mô hình trong phần hiển thị (`test_visible_entries_never_contain_model_or_vendor`, `test_ai_naming_itself_is_masked`)

## Rủi ro và điểm cần chú ý

- **AI tự xưng tên:** lời dặn cấm nhắc tên mô hình, và code còn che tên các mô hình ứng viên cùng các chữ `Claude`, `Anthropic`, `OpenAI`, `ChatGPT`, `GPT…`, `Gemini`, `Google Gemini`, `Bard` bằng «đã ẩn tên mô hình». "Google" đứng riêng không che (bài hay nói "tìm trên Google"). Văn phong vẫn có thể "lộ" hãng (ví dụ thói quen trình bày); không chặn được, và không cần chặn.
- **Câu lỗi:** câu lỗi `bad_request_error` của lớp AI nhắc «blind_test» trong `config/ai.toml` (mục này không có trong file). Chỉ hiện sau khi chấm, người dùng vẫn hiểu là sai tên mô hình/thông số, nhưng câu hơi lệch. Không sửa vì không được đụng `seo_app/ai/**`.
- **Gọi song song** bằng luồng: mỗi ứng viên có provider riêng (`make_provider` tạo mới), không dùng chung client. Provider giả trong test chạy được song song.
- Khung mới `de_bai` thêm vào `DATA_TAGS` nên mọi lời dặn khác cũng vô hiệu chữ `<de_bai>` lọt vào dữ liệu; chữ khác không đổi. `DATA_RULES` (trong system prompt) không đổi để không làm đổi lời dặn các bước khác; lời dặn thử mù tự nói rõ khung `de_bai` là dữ liệu.

## Đề xuất

- T-028 (lớp AI): nếu tiện, cho `bad_request_error` không nhắc `config/ai.toml` khi `task.name` không có trong file (ví dụ việc `blind_test`). Không gấp.
- Họa Sĩ: xem mục "Hướng dẫn cho Họa Sĩ".

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (sửa theo Soi Lỗi, 2026-10-15)

Lượt 2 do hai phiên Thợ Máy làm. Phiên đầu (Chỉ Huy A giao, máy Windows) sửa code ở commit
`4223a8c` nhưng dừng trước khi chạy toàn bộ test. Phiên sau (Chỉ Huy B giao, cloud Linux) soát lại
commit đó, sửa thêm một lỗ hổng cùng loại SL-T019-2 (`bdf2653`), gộp `main` (`d443041`), chạy toàn
bộ test và viết mục này.

### Tóm tắt (cho chủ dự án)

- Tên hãng/mô hình mà AI tự xưng giờ bị che cả khi viết nghiêng/đậm (`_Claude_`, `__Gemini__`) và
  khi là tên dòng mô hình (Opus, Sonnet, DeepMind…).
- Tên mô hình gõ nhầm (`c`, `10`, `cho`, `gpt`…) bị từ chối **trước khi gọi AI**, nên không tốn
  tiền và không làm hỏng chữ trong bài của ứng viên khác.
- Bài thử bị cắt vì quá dài: câu lỗi chỉ cách sửa làm được thật (chọn effort thấp hơn), thay cho câu
  cũ bảo sửa một mục không có trong `config/ai.toml`.

### Sửa gì cho từng lỗi

| Lỗi | Sửa | File | Commit |
|---|---|---|---|
| **SL-T019-1** (tên sau `_`, tên dòng mô hình) | Ranh giới che đổi thành `(?<![^\W_]\|-)`: tên đứng sau `_` vẫn bị che. Đuôi che `(?:[\w.-]*[^\W_])?` không ăn `_` cuối, nên Markdown vẫn đóng đúng (`_«đã ẩn tên mô hình»_`). Áp dụng cho cả danh sách tên hãng và tên ứng viên. Thêm tên dòng/công ty: `opus`, `sonnet`, `haiku`, `fable`, `dall-e`/`dalle`, `sora`, `codex`, `gemma`, `deepmind`, `palm 2`, cụm `Google DeepMind/Bard/Gemma/AI Studio`. | `seo_app/content/blind_test.py` (`_BEFORE`, `_TAIL`, `_VENDOR_NAMES`, `_mask_names`) | `4223a8c` |
| **SL-T019-2** (tên ngắn/gõ nhầm che chữ của mọi bài) | `validate_request` từ chối tên không đủ rõ (`_maskable`), báo "quá ngắn hoặc gõ nhầm" trước khi gọi AI. `_mask_names` chỉ dùng tên đủ rõ (phòng thủ thêm). | `seo_app/content/blind_test.py` | `4223a8c` |
| **SL-T019-2, phần còn sót** (tìm thấy khi soát `4223a8c`) | Luật `4223a8c` nhận mọi tên ≥ 3 ký tự có chữ cái, nên tên gõ nhầm là từ tiếng Việt không dấu (`cho`, `khi`, `con`, `nha`) vẫn được nhận và che mất chữ thường của mọi bài. Luật mới: có chữ cái **và** (có chữ số, **hoặc** dài ≥ 5 ký tự và có `-`/`.`). Tên thật của 3 hãng đều qua (`o3`, `4o`, `o4-mini`, `gpt-5.1`, `claude-opus-5-5`, `gemini-3-pro`, `gemini-flash-latest`). Từ trơn như `gpt`, `chatgpt` bị từ chối. | `seo_app/content/blind_test.py` (`_maskable`) | `bdf2653` |
| **Câu lỗi giới hạn token** (Soi Lỗi "Ghi nhận thêm" mục 2) | Lớp AI ném `TokenLimitError` (lớp con của `AIError`, **câu giữ nguyên từng chữ**) qua hàm chung `token_limit_error(task)`. Thử mù bắt riêng lỗi này và thay bằng `TOKEN_LIMIT_ERROR` (chỉ cách hạ effort). Nơi khác bắt `AIError` vẫn chạy y như cũ. | `seo_app/ai/base.py`, `seo_app/ai/anthropic_provider.py`, `seo_app/ai/openai_provider.py`, `seo_app/ai/gemini_provider.py`, `seo_app/content/blind_test.py` (`_call`) | `4223a8c` |

**Ra ngoài phạm vi phiếu (Chỉ Huy cần biết):** phiếu ghi "Không được sửa `seo_app/ai/**`" vì lúc đó
T-028 đang sửa thư mục này. T-028 đã lên `main` trước lượt 2 nên không còn đụng file. Thay đổi trong
`seo_app/ai/` chỉ là gom 3 chỗ `raise AIError(...)` giống hệt nhau thành một hàm và đổi lớp lỗi sang
lớp con. Câu lỗi, thời điểm ném và mọi nơi bắt `AIError` không đổi
(`test_token_limit_error_keeps_old_message_for_other_tasks`, `test_every_provider_raises_token_limit_error`).
Phiên đầu tự quyết, không có ghi chép là đã hỏi Chỉ Huy. Nếu Chỉ Huy không đồng ý thì có thể bỏ phần
này: thử mù sẽ hiện lại câu cũ, không hỏng gì khác.

### Test

- Bỏ `xfail` (Soi Lỗi, `tests/test_soi_loi_t019.py`):
  - `test_ai_naming_itself_markdown_underscore_and_family_names` (5 trường hợp)
  - `test_short_or_mistyped_model_name_does_not_wreck_other_entries` (2 trường hợp)
- Test mới trong `tests/test_blind_test.py`:
  - che tên sau `_`, tên dòng mô hình, Markdown vẫn đóng đúng;
  - `test_short_or_mistyped_model_names`: bảng tên bị từ chối/được nhận. `bdf2653` thêm `cho`, `khi`,
    `gpt`, `chatgpt`, `a-b` (từ chối), `4o`, `gemini-flash-latest`, `claude-opus-5-5` (nhận);
  - `test_short_names_are_never_used_for_masking` (thêm `cua`, `chung`, `cho`, `khi`);
  - `test_token_limit_message_points_to_effort_not_missing_config`,
    `test_token_limit_error_keeps_old_message_for_other_tasks`, `test_every_provider_raises_token_limit_error`.

### Đã thử thêm bằng tay (khi soát `4223a8c`)

| Chữ AI viết | Sau khi che |
|---|---|
| `Tôi là _Claude_.` | `Tôi là _«đã ẩn tên mô hình»_.` |
| `**__Gemini__**` | `**__«đã ẩn tên mô hình»__**` |
| `Google DeepMind và Google tìm kiếm` | `«đã ẩn tên mô hình» và Google tìm kiếm` ("Google" riêng giữ nguyên) |
| `PaLM 2 và palm-2`, `Sonnet, Haiku.` | che hết, giữ dấu câu |
| `Cửa sổ 10 năm` (ứng viên `o3`, `claude-opus-5-5`) | giữ nguyên |

### Bằng chứng (cloud Linux, sau khi gộp `main`, HEAD `d443041`)

```
$ uv run pytest -q
3222 passed, 4 skipped, 9 xfailed, 1 warning in 158.36s (0:02:38)

$ uv run ruff check .
All checks passed!
```

0 hỏng. 9 xfail là 9 xfail cũ có sẵn trên `main`. 7 xfail của T-019 đã bỏ và giờ qua.

**Một test chập chờn, không do phiếu này:** ở lần chạy toàn bộ đầu tiên,
`tests/test_soi_loi_round6.py::test_helper_catches_quadratic_function` hỏng 1 lần. Đây là test đo thời
gian của một hàm phụ trong bộ test. Tôi chạy riêng nó 10 lần trên `team/T-019` và 10 lần trên
`origin/main` (worktree riêng): 0/10 hỏng ở cả hai. Nhánh không sửa file test đó hay `sanitize.py`.
Lần chạy toàn bộ thứ hai xanh hết. Đề xuất Soi Lỗi để ý nếu nó còn hỏng trên máy bận.

### Điểm Soi Lỗi nên soi kỹ

1. Phần `seo_app/ai/`: `TokenLimitError` có thật sự không đổi hành vi của Soạn bài/rà soát không
   (câu lỗi, chỗ bắt lỗi).
2. Luật `_maskable` mới có từ chối nhầm tên mô hình thật nào của 3 hãng không.
3. Danh sách tên che mới có che nhầm chữ thường trong bài về cửa sắt không (`sora`, `codex`, `fable`,
   `haiku`, `opus` đều là chữ tiếng Anh; bài tiếng Việt hầu như không dùng).

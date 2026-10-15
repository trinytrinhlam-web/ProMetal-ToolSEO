# Báo cáo T-019 · Kiểm thử: thử mù mô hình AI

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-019](../tickets/T-019-thu-mu-mo-hinh.md) |
| Nhánh | `team/T-019` (kiểm trên `0d09f4d`: Thợ Máy + Họa Sĩ), worktree `D:\ProMetal-ToolSEO\wt-T-019` |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |
| Kết luận | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Thử mù chạy đúng.
- Bài hiện dưới tên A/B/C theo thứ tự thật sự ngẫu nhiên. Tên mô hình chỉ hiện sau khi bấm "Chấm xong".
- Một hãng lỗi (thiếu khóa, sai khóa, thiếu thư viện) thì các hãng khác vẫn có bài. Câu lỗi bằng tiếng Việt, không có traceback, không lộ khóa.
- Chữ AI hiện không có HTML hay link Markdown. Không có hãng nào được chọn sẵn ngầm.

Tìm được 2 lỗi, đều mức **Thấp**, không liên quan bảo mật:
- **SL-T019-1:** nếu AI tự xưng tên theo vài kiểu ít gặp, tên đó không được che, nên có thể lộ hãng trước khi chấm.
- **SL-T019-2:** một ứng viên gõ tên mô hình quá ngắn hoặc gõ nhầm (ví dụ `c`) thì chữ trong bài của **mọi** ứng viên bị che lung tung.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t019.py` | **Mới**, 27 trường hợp: 20 qua, 7 `xfail(strict=True)` cho SL-T019-1 (5) và SL-T019-2 (2). |

Không sửa code ứng dụng.

## Lỗi tìm được

| Mã | Mức | Ở đâu | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|
| **SL-T019-1** | Thấp | `seo_app/content/blind_test.py:54-57` (`_VENDOR_WORDS`), `:221-227` (`_mask_names`) | Provider giả viết vào bài: `Tôi là _Claude_`, `Bài do __Gemini__ viết` (nghiêng/đậm Markdown bằng gạch dưới), `Tôi là Claude Opus 5.5`, `Bản Sonnet viết nhanh`, `Google DeepMind`. Test: `test_ai_naming_itself_markdown_underscore_and_family_names` (5 trường hợp). | Trước khi chấm, bài không còn chữ nào nhận ra hãng hay dòng mô hình. | (a) Mẫu che có `(?<![\w-])`, mà `\w` gồm cả `_`, nên tên đứng sau `_` (cách viết nghiêng/đậm Markdown rất phổ biến) **không bị che**: `_Claude_` còn nguyên và hiện thành chữ nghiêng *Claude*. (b) Tên dòng mô hình không nằm trong danh sách: `Claude Opus 5.5` thành `«đã ẩn tên mô hình» Opus 5.5`; `Sonnet` và `DeepMind` còn nguyên. Lời dặn đã cấm AI tự xưng tên, nên chỉ xảy ra khi AI không nghe lời. Không lộ khóa. |
| **SL-T019-2** | Thấp | `seo_app/content/blind_test.py:213` (`validate_request` nhận tên mô hình 1 ký tự), `:221-227`, `:277` (che tên của **mọi** ứng viên, kể cả ứng viên lỗi) | Hai ứng viên: `c` (gõ nhầm, máy chủ báo lỗi) và một mô hình đúng viết `Cửa cuốn của chúng tôi bền 10 năm.`. Tương tự với tên `10`. Test: `test_short_or_mistyped_model_name_does_not_wreck_other_entries`. | Hoặc tên quá ngắn bị từ chối trước khi gọi AI, hoặc bài của ứng viên kia còn nguyên. | Bài của ứng viên **đúng** thành `«đã ẩn tên mô hình» «đã ẩn tên mô hình» «đã ẩn tên mô hình» «đã ẩn tên mô hình» tôi bền 10 năm.` Mẫu che không phân biệt hoa thường và ăn cả đuôi chữ, nên che mọi từ bắt đầu bằng "c" (`Cửa`, `cuốn`, `của`, `chúng`). Với tên `10` thì số liệu "10 năm" bị che. Bài bị hỏng làm sai kết quả chấm, mà người dùng không biết vì sao. |

### Ghi nhận thêm (không tính là lỗi của phiếu này)

- **Link trần trong chữ AI (có sẵn từ trước, cả app):** `clean_ai_text` bỏ link Markdown `[..](..)`, link tham chiếu,
  ảnh và `<https://…>`, nhưng để nguyên địa chỉ trần như `https://evil.com/x`, `www.evil.com`, `a@evil.com`. Khi hiện
  bằng `st.markdown`, Streamlit (GFM) biến chúng thành link bấm được. Trang Soạn bài cũng hiện chữ AI theo cùng cách,
  nên phiếu này "lọc như phần Soạn bài" là đúng. Ở thử mù, đề bài là chữ người dùng tự gõ, không có dữ liệu từ web,
  nên rủi ro thấp. Đề xuất Chỉ Huy cân nhắc một phiếu riêng cho `sanitize`. Theo `security.md`, link ra ngoài phải được
  người dùng thấy trước khi gửi; ở đây link hiện rõ, chưa vi phạm.
- **`BLIND_MAX_TOKENS = 2000` khi chọn effort cao (suy luận, chưa thử với máy chủ thật):** chữ suy nghĩ của OpenAI
  (`max_output_tokens`) và Claude (`max_tokens`) tính chung vào giới hạn này. Ứng viên chọn effort high/xhigh/max dễ bị
  cắt ngang, và câu lỗi của lớp AI bảo "Tăng max_tokens của việc «blind_test» trong config/ai.toml", nhưng mục này
  không có trong file, người dùng không làm theo được. Thợ Máy đã ghi phần câu lỗi 400. Đề xuất: giới hạn effort của thử
  mù ở mức medium, hoặc nâng giới hạn khi effort cao.
- **Thời gian chờ:** các ứng viên gọi song song, nhưng mỗi provider có timeout 15 phút và tự thử lại tối đa 3 lần. Một
  hãng treo thì cả lượt thử có thể chờ rất lâu, dưới vòng quay "Đang gửi đề…". Không sai, chỉ là trải nghiệm.
- **Đoán bằng cách loại trừ:** nếu một ứng viên lỗi mà người dùng đoán được ứng viên nào lỗi (ví dụ vừa gõ tên lạ), thì
  bài còn lại là của ứng viên kia. Đây là giới hạn tự nhiên của thử mù, không cần sửa.
- `load_rules` không bắt `FileNotFoundError` khi thiếu `config/content.toml` (có từ trước, Soạn bài cũng vậy). Lỗi
  `ContentRulesError` (sai cú pháp, sai bảng mã) thì tab này báo đúng tiếng Việt
  (`test_ui_broken_content_rules_shows_vietnamese_error`).

## Đã thử và qua

- **Thứ tự nhãn ngẫu nhiên thật:** chạy 600 lượt không cố định hạt giống, như giao diện: mỗi ứng viên rơi vào mỗi nhãn
  A/B/C đều trên 120 lần (kỳ vọng 200) (`test_label_order_is_uniform_without_fixed_seed`). Ứng viên nhập đầu tiên không
  luôn là A.
- **Phần hiện trước khi chấm giống hệt nhau giữa các hãng:** cùng bài thì mọi nhãn hiện y hệt nhau, `BlindEntry` không có
  trường nào mang tên hãng (`test_entries_have_same_shape_for_every_vendor`). Ba ứng viên lỗi theo ba cách khác nhau
  (thiếu thư viện, thiếu khóa, lỗi lạ có khóa trong câu) thì phần bài y hệt nhau, chỉ có `HIDDEN_ERROR`
  (`test_all_fail_differently_but_look_the_same`).
- **AI tự xưng tên, các dạng thường gặp đều bị che:** `**Claude**`, `Claude's`, `ChatGPT`, `GPT-5.1-mini`,
  `Google Gemini`, `[Claude](https://…)`, chữ hoa, tên ứng viên kèm đuôi (`test_ai_naming_itself_is_masked`).
- **Một hãng lỗi:**
  - Thiếu thư viện google-genai: `make_provider` thật, ứng viên đó ra câu "uv sync" (`test_missing_library_for_one_vendor`).
  - Thiếu khóa OpenAI: `test_missing_key_for_one_vendor`.
  - Sai khóa: thư viện openai thật, mạng giả trả 401 có khóa trong câu. Câu lỗi cố định, khóa không có ở bài hay ở phần
    hiện tên (`test_wrong_key_real_library_never_shows_key`).
- **Không có hãng mặc định:** ứng viên không ghi hãng bị từ chối, `Candidate` bắt buộc có hãng (`test_no_default_vendor`).
  Trên giao diện, chỉ có khóa Gemini thì mọi ô hãng chỉ có Gemini, Claude không được chọn sẵn ngầm
  (`test_ui_only_keyed_vendor_offered_no_hidden_default`).
- **Giao diện, chạy `run_blind_test` thật (chỉ thay provider):**
  - Bài tự xưng "Tôi là <mô hình>, một mô hình của OpenAI": trước khi chấm, phần kết quả không có tên mô hình hay hãng.
    Sau khi chấm, bảng có đủ tên (`test_ui_end_to_end_names_hidden_until_reveal`).
  - Chữ AI có `<img onerror>`, `<script>`, `javascript:`, ảnh và link tham chiếu: phần kết quả không còn thứ nào, các ô
    Markdown đều `allow_html = False` (`test_ui_ai_html_and_links_are_not_rendered`).
  - Hai hãng đều thiếu thư viện: không traceback, chỉ có câu cố định. Sau khi chấm mới có câu "uv sync" của đúng hãng.
    Khóa không có trên trang (`test_ui_all_candidates_fail_no_traceback_no_key`).
- **Không gọi mạng:** bộ chặn mạng của `tests/conftest.py` vẫn bật. Thư viện thật chỉ chạy với `httpx2.MockTransport`.
- **Mọi trang và bước vẫn mở được:** `tests/test_app_pages.py` qua (nằm trong lần chạy toàn bộ dưới đây).

## Bằng chứng

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_soi_loi_t019.py
20 passed, 7 xfailed

# Trước khi thêm test (team/T-019 = 0d09f4d), Windows
$ uv run pytest -q -rfE
2771 passed, 10 skipped, 9 xfailed in 335.03s (0:05:35)

# Sau khi thêm test, Windows
$ uv run pytest -q -rfE
2791 passed, 10 skipped, 16 xfailed in 267.62s (0:04:27)
```

0 hỏng, 0 lỗi. So với trước: **+20 passed, +7 xfailed**, khớp đúng 27 trường hợp mới. 9 xfail cũ không đổi.
Lần chạy trước mất 335 giây vì máy đang chạy việc khác cùng lúc. Không có test hỏng hay chập chờn.

Tôi chạy 7 xfail mới với `--runxfail` để chắc chúng thất bại đúng lý do: chữ `claude`/`gemini`/`opus`/`sonnet`/`deepmind`
còn trong bài, và bài của ứng viên đúng bị che.

## Đối chiếu tiêu chí xong

- [x] Thử mù chạy được với 2–3 ứng viên khác hãng.
- [ ] Không lộ tên mô hình trước khi chấm: đúng với mọi dạng thường gặp, còn sót dạng `_Tên_` và tên dòng mô hình (SL-T019-1).
- [x] Chữ AI không qua HTML, không còn link Markdown.
- [x] Một hãng lỗi / thiếu khóa / thiếu thư viện: các hãng khác vẫn chạy, câu lỗi tiếng Việt, không traceback, không lộ khóa.
- [x] Không có hãng mặc định ngầm.
- [x] `uv run pytest` 0 hỏng trên Windows, `uv run ruff check .` sạch.

## Điều kiện để ĐẠT

1. Thợ Máy sửa **SL-T019-1** trong `blind_test.py`, khoảng vài dòng:
   - Mẫu che không coi `_` là chữ đứng trước. Ví dụ đổi `(?<![\w-])` thành `(?<![^\W_]|-)`, áp dụng cả cho tên ứng viên.
   - Thêm tên dòng mô hình vào danh sách che: `opus`, `sonnet`, `deepmind` (cân nhắc `haiku`, vì đó cũng là từ thường).
   - Sửa xong thì bỏ `xfail` của `test_ai_naming_itself_markdown_underscore_and_family_names`.
2. Nên sửa luôn **SL-T019-2** (không bắt buộc): chỉ che tên ứng viên khi tên đủ dài và có chữ cái (ví dụ ≥ 3 ký tự), hoặc
   `validate_request` từ chối tên mô hình quá ngắn. Sửa xong thì bỏ `xfail` của
   `test_short_or_mistyped_model_name_does_not_wreck_other_entries`.

## Đề xuất

- Chỉ Huy cân nhắc một phiếu `sanitize` cho link trần (`https://…`, `www.…`, email) trong chữ AI. Việc này áp dụng cả app,
  xem "Ghi nhận thêm".
- Thợ Máy hoặc Họa Sĩ: giới hạn effort của thử mù, hoặc nâng `BLIND_MAX_TOKENS` khi effort cao (xem "Ghi nhận thêm").
- Lá Chắn: A1, U1, S2 tôi đã thử ở trên và đều qua. Riêng SL-T019-1 không phải lỗi bảo mật.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (kiểm lại, 2026-10-15)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`), bên Chỉ Huy B, cloud Linux · model: Claude Opus 5.5 |
| Kiểm trên | `team/T-019` tại `94a2813` (Thợ Máy A `4223a8c` + Thợ Máy B `bdf2653`, đã gộp `main`) |
| Kết luận | **ĐẠT** |

### Tóm tắt (cho chủ dự án)

- Hai lỗi lượt 1 đã sửa đúng. AI tự xưng tên kiểu `_Claude_`, Opus, Sonnet, DeepMind… đều bị che. Tên mô hình gõ nhầm (`c`, `10`, `cho`, `gpt`) bị từ chối trước khi gọi AI, nên không tốn tiền và không làm hỏng bài khác.
- Phần sửa trong lớp AI (`seo_app/ai/`) không đổi gì ở trang Soạn bài: câu lỗi giống từng chữ, chỗ bắt lỗi vẫn bắt được.
- Không có tên mô hình thật nào của 3 hãng bị từ chối nhầm (thử 42 tên). Chữ tiếng Việt về cửa sắt không bị che nhầm.
- Tìm thêm 2 lỗi nhỏ, mức **Thấp**, **không chặn**:
  - **SL-T019-3:** số phiên bản đứng sau tên còn lộ, ví dụ "Opus 5.5" thành "«đã ẩn» 5.5".
  - **SL-T019-4:** riêng Claude, khi bài thử bị cắt vì quá dài, câu lỗi vẫn bảo sửa `config/ai.toml`.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t019_luot2.py` | **Mới**, 103 trường hợp: 99 qua, 4 `xfail(strict=True)` (SL-T019-3: 3, SL-T019-4: 1). |

Không sửa code ứng dụng. Không xóa, `skip` hay nới lỏng test nào.

### Xác nhận lỗi lượt 1

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| SL-T019-1 | **Đã sửa** | Ở `tests/test_soi_loi_t019.py`, Thợ Máy chỉ bỏ 2 dòng `xfail` (`git diff e3cee76..HEAD`), thân test và danh sách chữ cấm giữ nguyên. Thêm `test_vendor_words_still_masked` (9 câu: `_Claude_`, `**__Gemini__**`, Sora/Codex/Gemma, PaLM 2, dall-e-3, `ChatGPT's`…). Giao diện: `_Claude_` hiện thành `_«đã ẩn tên mô hình»_`, Markdown vẫn đóng đúng. |
| SL-T019-2 | **Đã sửa** | 2 trường hợp cũ (`c`, `10`) qua, test không đổi. Thêm `test_mistyped_names_rejected_before_any_call`: 20 tên gõ nhầm, gồm từ Việt không dấu, tên hãng trơn, `--`, `..`. Tất cả bị từ chối và **không có lần gọi AI nào**. Trên giao diện, nút Chạy bị khóa kèm câu "quá ngắn hoặc gõ nhầm" (`test_ui_mistyped_model_blocks_run_without_calling`). |

### Ba điểm Thợ Máy nhờ soi

**(1) `TokenLimitError` không đổi hành vi Soạn bài.** Đạt.
- `TokenLimitError` là lớp con của `AIError`. Mọi chỗ bắt lỗi vẫn là `except AIError`: `app/views/write.py:379` (`ai_call`), `:876`, `app/views/settings.py`, và `except AIError: raise` trong 3 provider. Chỉ `blind_test._call` bắt riêng lớp con. Không có chỗ nào so `type(exc) is AIError`.
- Thư viện thật OpenAI và Gemini, mạng giả trả bài bị cắt kèm JSON dở dang, với việc `write`, `review`, `rewrite`: câu lỗi giống **từng chữ** câu cũ ở `e3cee76` (`test_token_limit_real_library_same_message_and_still_aierror`, 6 trường hợp).
- Trang Soạn bài qua AppTest, AI giả chạm giới hạn ở bước viết và ở bước rà soát: hiện đúng câu cũ (lấy `max_tokens` từ `config/ai.toml`), không hiện câu của thử mù, không sập, ở lại bước dàn ý (`test_write_page_token_limit_shows_same_message`). Đối chứng: luồng thường vẫn tới bước bài viết.
- Thư viện thật Anthropic bị cắt vẫn ra câu "không đúng khuôn…" của T-028, không đổi (`test_token_limit_anthropic_real_library_message_unchanged`). Xem SL-T019-4.

**(2) Luật `_maskable`.** Đạt.
- 42 tên thật của 3 hãng đều được nhận, cả ở `validate_request` (`test_real_model_names_are_accepted`). Danh sách gồm `o1`, `o3`, `4o`, `o4-mini`, `gpt-5.1`, `ft:gpt-4o-mini:org::abc123`, `computer-use-preview` (không có số), `claude-opus-4@20250514`, `claude-3-5-haiku-latest`, `models/gemini-2.5-pro`, `gemini-flash-lite-latest`, `gemma-3-27b-it`…
- Ghi nhận: một vài tên gõ nhầm có chữ số vẫn được nhận (`a1`, `x1`, `cửa1`). Hậu quả chỉ là che đúng chữ đó, ví dụ "A1" trong bài. Không đáng sửa.

**(3) Danh sách che mới với bài tiếng Việt.** Đạt.
- 13 câu về cửa sắt giữ nguyên (`test_vietnamese_door_text_untouched`): "Ô pớt", "ô-pớt", "thợ sơn", "son môi", "anh Sơn", "Hải Phòng", "hai ku-pi-đông", "chị Hài", "pơ-mu", mác thép, số điện thoại, "tìm trên Google"… Âm tiết tiếng Việt không chứa được các cụm `opus`, `sonnet`, `haiku`, `sora`, `gemma`, `bard`, `codex`, `fable`.
- Ghi nhận, không tính lỗi: danh từ riêng tiếng Anh bắt đầu bằng các chữ trong danh sách vẫn bị che, vì đuôi che ăn tiếp chữ. Ví dụ "bản lề Opus", "cửa sổ Sora", "Claude Monet", "Bardi", "sonneteer", mã hàng "GPT-2000". Việc che chỉ ảnh hưởng phần hiện trước khi chấm, không đụng bài thật, nên chấp nhận được. Ngược lại, "DALL·E 3" (dấu chấm giữa) không bị che. AI viết bài chữ khó tự xưng là DALL·E, nên bỏ qua.

### Lỗi mới

| Mã | Mức | Ở đâu | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|
| **SL-T019-3** | Thấp, không chặn | `seo_app/content/blind_test.py` (`_VENDOR_WORDS`, `_TAIL`) | AI viết `Tôi là Claude Opus 5.5`, `Tôi là GPT 6.1.`, `Gemini 3 Pro viết bài.` Test: `test_version_number_after_vendor_word_is_masked` (3 trường hợp, `xfail(strict)`). | Không còn số phiên bản đi kèm tên. | Thành `«đã ẩn tên mô hình» «đã ẩn tên mô hình» 5.5`, `… 6.1`, `… 3 Pro`. Người quen số phiên bản đoán được hãng. Chỉ xảy ra khi AI không nghe lời dặn cấm tự xưng. Gợi ý: sau một chữ đã che, che thêm phần `\s+\d[\w.]*` (và `Pro`/`Flash`…). Không được che số đứng riêng trong bài: đối chứng `test_version_like_numbers_in_article_are_kept` ("dày 5.5 mm"). |
| **SL-T019-4** | Thấp, không chặn | `seo_app/ai/anthropic_provider.py:51-60` (nhánh `ValidationError`), `blind_test._call` | Ứng viên Claude, thư viện `anthropic` thật, máy chủ giả trả JSON bị cắt kèm `stop_reason = max_tokens` (đúng như máy chủ thật làm khi chạm giới hạn). Test: `test_blind_token_limit_anthropic_real_library_points_to_effort` (`xfail(strict)`). | Sau khi hiện tên, câu lỗi chỉ cách hạ effort (`TOKEN_LIMIT_ERROR`), như OpenAI và Gemini (`test_blind_token_limit_real_library_points_to_effort` qua). | Ra câu "…tăng max_tokens của việc «blind_test» trong config/ai.toml", mục người dùng không làm theo được. Lý do: thư viện anthropic kiểm khuôn trước khi biết lý do dừng, nên lỗi không đi qua `token_limit_error`. Test cũ của Thợ Máy chỉ dùng stream giả không ném `ValidationError`, nên không bắt được. Gợi ý: ở nhánh đó ném `TokenLimitError` với câu T-028 giữ nguyên, hoặc thử mù nhận ra câu này. |

### Thử trên giao diện (AppTest)

`test_ui_full_flow_three_vendors_names_hidden_until_scored`: 3 hãng, đi đủ luồng: chọn 3 ứng viên → cảnh báo → chạy → chấm → hiện tên.
- **Cảnh báo:** có "gọi AI 3 lần… tốn tiền", nhãn nút ghi "3 lần".
- **Ba ứng viên giả:**
  - Claude viết bài, trong bài tự xưng tên.
  - OpenAI chạm giới hạn token.
  - Gemini lỗi, câu lỗi chứa tên mô hình và chữ "Google Gemini".
- **Trước khi chấm:**
  - Không tên mô hình nào có ở bất cứ đâu trên trang (markdown, caption, cảnh báo, lỗi, bảng).
  - Không có "Google Gemini", "Claude", "max_tokens", "config/ai.toml" trong phần kết quả.
  - Hai ứng viên lỗi hiện cùng một câu `HIDDEN_ERROR`, không có `st.error`.
  - Chỉ bài có chữ mới có thanh điểm. Chữ tiếng Việt giữ nguyên.
- **Sau khi chấm:**
  - Bảng có đủ 3 tên, điểm đúng như đã chọn (8).
  - Câu lỗi hiện kèm tên: OpenAI ra câu hạ effort, Gemini ra câu gốc.
  - Nút "Chấm xong" bị khóa. Không lộ khóa nào.

### Bằng chứng (cloud Linux)

```
$ uv run ruff check .
All checks passed!

# Trước khi thêm test (94a2813)
$ uv run pytest -q
3222 passed, 4 skipped, 9 xfailed, 1 warning in 179.29s

# Sau khi thêm test
$ uv run pytest -q tests/test_soi_loi_t019_luot2.py
99 passed, 4 xfailed

$ uv run pytest -q
3321 passed, 4 skipped, 13 xfailed, 1 warning in 163.93s
```

0 hỏng. So với trước: +99 passed, +4 xfailed, khớp đúng 103 trường hợp mới. 4 xfail mới đã chạy với `--runxfail` và hỏng đúng lý do: còn chuỗi `5.5`, `6.1`, `3 Pro`; câu của Claude còn `config/ai.toml`.

### Ghi nhận thêm: test chập chờn, có sẵn trên `main`, không do T-019

`tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail` (T-028):
- Hỏng 1 lần trong một lần chạy toàn bộ (lần chạy toàn bộ sau xanh).
- Chạy riêng file đó: hỏng **10/10** trên `team/T-019` và **25/25** trên `origin/main` (worktree riêng, cùng file test và cùng `ignoring_custom_headers`).
- Lỗi: `KeyError('OPENAI_CUSTOM_HEADERS')`. Luồng khác duyệt `os.environ` (`dict(os.environ)`, `urllib.request.getproxies()`) đúng lúc `ignoring_custom_headers` gỡ biến. Khóa `_ENV_LOCK` chỉ chặn các luồng cùng tạo client, không chặn luồng đọc.

Liên quan tới thử mù:
- Thử mù là chỗ đầu tiên gọi `make_provider` song song ở nhiều luồng.
- Lỗi chỉ xảy ra khi máy có đặt một biến `*_CUSTOM_HEADERS`. httpx đọc proxy lúc tạo client, mà việc này nằm trong khóa, nên rủi ro thực tế thấp.

Đề xuất: Chỉ Huy lập phiếu riêng cho Thợ Máy (T-028 tiếp) để sửa code hoặc sửa test. Không chặn T-019.

### Đối chiếu tiêu chí xong

- [x] Thử mù chạy được với 2–3 ứng viên khác hãng (giao diện 3 hãng, đủ luồng).
- [x] Không lộ tên mô hình trước khi chấm: các dạng của lượt 1 đã che. Còn số phiên bản (SL-T019-3, Thấp).
- [x] Chữ AI không qua HTML, không còn link Markdown (test lượt 1 vẫn qua).
- [x] Một hãng lỗi / thiếu khóa / thiếu thư viện / chạm giới hạn: hãng khác vẫn chạy, câu lỗi tiếng Việt, không traceback, không lộ khóa.
- [x] Không có hãng mặc định ngầm.
- [x] Phần sửa ở `seo_app/ai/` không đổi hành vi Soạn bài.
- [x] `uv run pytest` 0 hỏng trên Linux, `uv run ruff check .` sạch.

### Đề xuất

- Chuyển T-019 sang Lá Chắn. Phần đáng soi là `seo_app/ai/` ngoài phạm vi ban đầu của phiếu: tôi đã xác nhận không đổi câu lỗi và không đổi chỗ bắt lỗi.
- SL-T019-3 và SL-T019-4 là Thấp. Sửa ngay trong T-019 hay để phiếu sau, Chỉ Huy quyết. Sửa xong thì bỏ `xfail` của 2 test tương ứng.
- Lập phiếu cho test chập chờn của T-028 (xem trên).

### Câu hỏi cho chủ dự án

Không có.

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

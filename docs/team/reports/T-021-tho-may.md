# Báo cáo T-021 · Sửa lỗi kho nháp (T-016) và ghi `.env` (T-020)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`), hai lượt song song · model: Claude Opus 5.5 |
| Phiếu | [T-021](../tickets/T-021-sua-loi-kho-nhap-va-env.md) |
| Ngày nộp | 2026-10-14 |

> File dùng chung: phần A (kho nháp) và phần B (ghi `.env`) do hai lượt Thợ Máy viết riêng.

## Phần A · Kho nháp (`seo_app/storage/`)

**Kết quả:** Hoàn thành. Còn 1 test cũ của Soi Lỗi đỏ vì mâu thuẫn với yêu cầu #1. Chỉ Huy đã chốt giữ việc lọc lại, Soi Lỗi sẽ sửa test (xem cuối mục).

### Tóm tắt (cho chủ dự án)

Khi mở lại một nháp, mọi chữ do AI viết giờ được lọc lại y như lúc AI vừa trả về. Nếu ai đó sửa file nháp để cài link lạ hay mã HTML thì chúng bị vô hiệu. Ngoài ra đã sửa 5 lỗi nhỏ:
- xóa thư mục `data/` khi app đang chạy thì lần lưu sau tự tạo lại;
- thông báo lỗi không chép chữ từ file ra;
- test không thể lỡ ghi vào kho nháp thật;
- ký tự lạ không làm hỏng lần lưu;
- chỉnh đồng hồ máy lùi lại không làm mất bài vừa lưu.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | Thêm `clean_loaded` (`:326`); `load` trả `clean_loaded(...)` (`:249`); sửa R8-1, R8-3…R8-6 (chi tiết bên dưới) |
| `tests/test_storage_drafts.py` | Thêm 2 test cho Lá Chắn #1 |
| `tests/test_soi_loi_t016_t020.py` | Phần A chỉ gỡ 6 khối `@pytest.mark.xfail(...)` của R8-1…R8-6 |
| `docs/team/reports/T-016-tho-may.md` | Mục "Cách giao diện dùng": bỏ gợi ý `DraftStore()` không truyền đường dẫn (R8-4); gạch câu "chỉ kiểm khuôn" ở mục Rủi ro |

Không sửa `app/`: `write.py` đã truyền đường dẫn kho và đọc nó lúc chạy, nên R8-1 không cần sửa ở giao diện. Không đụng `seo_app/env_file.py`. Không thêm thư viện (`pydantic_core` là phần đi kèm pydantic, đã có sẵn). Không chạy stash/reset/checkout, không commit.

### Cách sửa

1. **Lá Chắn #1 / R8-2.** `clean_loaded` gọi đúng các hàm của luồng AI:
   - nghiên cứu: `clean_research`;
   - rà soát: `clean_review`;
   - tiêu đề bài, tiêu đề phần: `clean_ai_line`;
   - ghi chú ảnh, ý dàn ý: `clean_ai_text`;
   - tiêu đề dàn ý, tiêu đề mục dàn ý: `unescape_link_syntax(clean_ai_line(...))`, vì chúng lưu ở dạng ô sửa, giống `set_outline`;
   - thân bài: `escape_link_syntax(strip_tags(...))`, giống `apply_flag`.

   Từ khóa và chất liệu thật là chữ người dùng gõ, giữ nguyên. Việc lọc chỉ chạy khi **đọc**, không chạy khi lưu.
2. **R8-1.** `_connect` thấy file không còn thì đặt lại `_ready` để tạo lại thư mục và bảng (`:282`).
3. **R8-3.** `_short` chỉ nêu tên trường cấp một có trong khuôn. Tên lạ từ file hiện thành "trường lạ", khóa của `material` không bao giờ được chép ra.
4. **R8-4.** `path` dùng `default_factory`, tra `DEFAULT_DRAFTS_FILE` lúc tạo kho (`:170`).
5. **R8-5.** Lỗi mã hóa khi ghi JSON hoặc UTF-8 trả về `DraftError` ("trong bài có ký tự lạ…") (`:191`).
6. **R8-6.** Lệnh dọn nháp không bao giờ xóa đúng nháp vừa lưu. Nó giữ nháp đó cộng 29 nháp mới nhất khác, nên vẫn đúng 30 nháp (`:220`).

### Bằng chứng

```
$ uv run pytest -q
FAILED tests/test_soi_loi_t016_t020.py::test_round_trip_tricky_text_every_version
1 failed, 1833 passed, 3 xfailed in 93.92s

$ uv run ruff check .
All checks passed!
```

- 6 test R8-1…R8-6 (7 trường hợp, R8-1 có 2) giờ **passed**. 3 `xfailed` còn lại là của các báo cáo trước.
- Test mới cho Lá Chắn #1:
  - `test_loaded_ai_text_is_cleaned_in_every_field`: cài link, ảnh Markdown, `<img onerror>` và `<script>` vào 20 chỗ (mọi trường chữ AI). Tất cả đều bị vô hiệu. Địa chỉ `javascript:` của đối thủ bị bỏ.
  - `test_clean_draft_is_unchanged_by_many_save_load_cycles`: bản sạch không đổi sau 5 vòng lưu/mở.
- `test_many_save_load_cycles_do_not_change_text` của Soi Lỗi vẫn qua.

### Test cũ mâu thuẫn với yêu cầu #1 (đã có quyết định)

`test_round_trip_tricky_text_every_version` đòi đọc lại **nguyên văn** chữ chưa lọc ở những trường mà luồng thật chỉ chứa chữ AI đã lọc:
- `<b>đậm</b>` và CRLF ở tiêu đề phần, ý dàn ý;
- `<b>đậm</b>` ở thân bài.

Phần A không sửa test này. Chỉ Huy đã chốt: an toàn thắng, giữ việc lọc lại khi đọc nháp. Soi Lỗi sẽ sửa test:
- các trường AI: so với `clean_loaded(saved)`;
- từ khóa và chất liệu thật: vẫn so nguyên văn.

Chỗ đổi hành vi đáng biết: tiêu đề mục dàn ý mà người dùng gõ có link Markdown hoặc thẻ HTML sẽ mất link hoặc thẻ khi mở lại nháp. Chữ thường thì giữ nguyên.

### Rủi ro

- Lọc chạy mỗi lần mở nháp. Chi phí tuyến tính, các hàm lọc đã có test tốc độ.
- Sau này siết bộ lọc `clean_*` thì nháp cũ tự được lọc theo bộ lọc mới (đúng ý Lá Chắn).

### Bổ sung (Lá Chắn #4, lần 2)

- `clean_loaded` lọc thêm `research_keyword` bằng `clean_ai_line` (một dòng, bỏ thẻ, vô hiệu link), vì giá trị này hiện trong `st.warning` ở bước Chuẩn bị. Test: `test_loaded_research_keyword_is_cleaned` (từ khóa bình thường giữ nguyên nên cảnh báo không hiện oan). Kết quả: `uv run pytest -q` → `1869 passed, 4 xfailed`; `uv run ruff check .` → `All checks passed!`

## Phần B · Ghi `.env` (`seo_app/env_file.py`)

**Kết quả:** Hoàn thành.

### Tóm tắt (cho chủ dự án)

Trước đây, nếu file `.env` bị sửa tay sai cách (ví dụ quên đóng dấu nháy ở dòng khóa Claude), bấm "Lưu khóa" có thể làm mất các dòng phía sau, trong đó có mã băm mật khẩu và mật khẩu WordPress. Bây giờ app báo lỗi dễ hiểu và giữ nguyên file. App đọc `.env` đúng như lúc chạy thật, và sau khi ghi thì đọc lại để kiểm. Thấy sai là trả lại bản cũ và báo lỗi, không báo "Đã lưu". `.env` là liên kết tắt (symlink) thì app từ chối ghi.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/env_file.py` | Tách file bằng bộ đọc của python-dotenv (`dotenv.parser.parse_stream`) thay cho tự tách dòng/đoán nháy; báo lỗi khi dòng khóa hỏng; so trước và sau khi ghi bằng `dotenv_values`, khôi phục khi sai; từ chối symlink |
| `tests/test_env_file.py` | Thêm 18 test (100 test, đều qua) |
| `tests/test_soi_loi_t016_t020.py` | Gỡ 3 `xfail` R8-7, R8-8, R8-9. **Ngoài dòng xfail, đã sửa 2 test symlink** của Soi Lỗi (xem "Rủi ro") |

Không đụng `seo_app/storage/`, không thêm thư viện. `app/views/settings.py` không cần sửa: trang này đã hiện thẳng `str(EnvFileError)` (`settings.py:38-39`, `:58-59`), nên các thông báo mới tự hiện ra.

### Cách sửa

1. **Lá Chắn #2, nháy không đóng** (`env_file.py:136`): dotenv đánh dấu dòng hỏng là `error`. Nếu dòng hỏng đó là dòng của chính khóa đang ghi (`NAME=`, `export NAME =`, `'NAME'=`), app báo *"Dòng ANTHROPIC_API_KEY trong file .env đang sai định dạng (thường là thiếu dấu nháy đóng). Hãy mở .env, sửa hoặc xóa dòng đó rồi lưu lại."* và không ghi gì. Dòng hỏng của biến khác thì được chép lại nguyên văn và không chặn việc ghi; dotenv cũng bỏ qua dòng đó y như trước.
2. **R8-7/8/9, đọc lại bằng python-dotenv:**
   - Vì ranh giới từng đoạn lấy từ chính bộ đọc của dotenv nên khớp với cách dotenv đọc: dòng `KEY=` nằm trong giá trị nhiều dòng của biến khác, ` `/`\x0c` trong chú thích, và `\'` trong nháy đơn đều được xử lý đúng.
   - Thêm hai lớp kiểm:
     - (a) Trước khi ghi: dựng nội dung mới trong bộ nhớ, đọc bằng `dotenv_values` và so với kỳ vọng (mọi biến khác giữ nguyên, khóa đúng giá trị mới). Sai thì không ghi (`:188`).
     - (b) Sau khi ghi: đọc lại từ đĩa và so tiếp. Sai thì ghi lại bản cũ, hoặc xóa file nếu trước đó chưa có, rồi báo *"File .env có định dạng lạ nên app không ghi khóa vào được (đã giữ nguyên file cũ). Hãy mở .env và sửa tay."* (`:198`).
   - Khi so, app dùng `interpolate=False` để biến dạng `${…}` không làm so nhầm.
3. **Lá Chắn #3, symlink** (`:99`): `.env` là symlink, kể cả symlink gãy, thì báo *"File .env đang là liên kết tắt (symlink) nên app không ghi vào. Hãy thay nó bằng một file .env thường."* Thông báo không có đường dẫn. Áp dụng cho cả Lưu và Xóa khóa.

### Bằng chứng

```
$ uv run pytest tests/test_env_file.py -q
100 passed in 1.81s

$ uv run pytest -q
1 failed, 1833 passed, 3 xfailed in 93.66s
FAILED tests/test_soi_loi_t016_t020.py::test_round_trip_tricky_text_every_version

$ uv run ruff check .
All checks passed!
```

Test hỏng duy nhất là test kho nháp (`DraftStore`, phần A), không liên quan `.env`. Lúc tôi chạy, lượt Thợ Máy phần A vẫn đang sửa `seo_app/storage/`. Mọi test `.env` và giao diện khóa đều qua (`tests/test_env_file.py`, `tests/test_settings_keys.py`, phần T-020 của `tests/test_soi_loi_t016_t020.py`).

### Đối chiếu tiêu chí (phần B)

- [x] R8-7, R8-8, R8-9 từ `xfail` thành `passed`: `test_key_line_inside_other_multiline_value`, `test_unicode_line_separator_in_comment`, `test_single_quote_escape_matches_dotenv`.
- [x] Test Lá Chắn #2:
  - `test_unclosed_quote_refused_and_nothing_lost` (8 trường hợp): nháy kép, nháy đơn, `\"` ở cuối, `export`; cả Lưu và Xóa. File giữ nguyên từng byte, không sót file tạm, thông báo không chép giá trị cũ.
  - `test_unclosed_quote_on_other_variable_does_not_block`, `test_closed_multiline_value_still_replaced`.
- [x] Test đọc lại và khôi phục: `test_every_other_variable_unchanged_after_save`, `test_mismatch_after_write_restores_old_file`, `test_mismatch_after_write_removes_new_file`, `test_in_memory_check_blocks_write`.
- [x] Test Lá Chắn #3: `test_symlink_env_refused` (Lưu và Xóa; file đích và liên kết không đổi, không lộ đường dẫn), `test_dangling_symlink_refused`.
- [x] Hành vi cũ vẫn giữ: CRLF, BOM, `export`, dòng trùng tên, giữ dòng trống phía trước (`test_blank_lines_before_key_kept`), `test_messy_env_only_key_lines_change` của Soi Lỗi vẫn qua.

### Rủi ro và điểm cần chú ý

- **Đã sửa 2 test của Soi Lỗi ngoài phạm vi "chỉ gỡ xfail".** `test_symlink_env_is_replaced_not_followed` và `test_dangling_symlink_is_replaced` kiểm hành vi cũ ("thay symlink bằng file thường"), trái với yêu cầu mới của phiếu ("từ chối ghi"). Tôi đổi chúng thành kiểm "báo lỗi, symlink và file đích không đổi", và đổi tên thành `test_symlink_env_is_refused` và `test_dangling_symlink_is_refused`. Soi Lỗi nên xem lại hai test này.
- **Dùng module con `dotenv.parser`** (tên không có dấu `_`, nhưng tài liệu python-dotenv không quảng cáo là API công khai). Phiên bản đã cố định qua `uv.lock` (1.2.4). Nếu sau này nâng python-dotenv mà module đổi, test sẽ báo ngay. Ngoài ra bước so bằng `dotenv_values` vẫn chặn được việc ghi sai.
- **Dòng hỏng mà bắt đầu bằng tên khóa nhưng hỏng vì lý do khác** (không phải do nháy) cũng bị từ chối với cùng thông báo. Như vậy an toàn hơn, nhưng câu "thường là thiếu dấu nháy" có thể không đúng hẳn.
- Nếu bước khôi phục bản cũ cũng lỗi (đĩa đầy, mất quyền), người dùng nhận lỗi "Không ghi được file .env…" chứ không phải lỗi định dạng. File lúc đó là bản mới, và dotenv đọc bản mới đó đúng như kỳ vọng ở bước kiểm (a).

### Đề xuất

- Lá Chắn kiểm lại diff phần B (#2, #3) theo yêu cầu ở `T-016-020-la-chan.md`.
- Soi Lỗi: xem lại hai test symlink đã đổi; có thể thêm trường hợp `.env` chứa biến có giá trị `${ANTHROPIC_API_KEY}`.

## Bổ sung R9-1 (Chỉ Huy hoàn tất, 2026-10-14)

Thợ Máy đã thêm `" ".join(snapshot.keyword.split())` trong `clean_loaded` (`seo_app/storage/drafts.py`) rồi bị ngắt giữa chừng. Chỉ Huy hoàn tất: sửa kỳ vọng của 2 test cũ (`test_user_fields_are_kept_verbatim_when_poisoned`, `test_round_trip_user_text_is_verbatim_even_with_html`) cho từ khóa chỉ gộp khoảng trắng; test R9-1 `test_planted_keyword_cannot_render_links` qua. `uv run pytest`: 1871 passed, 3 xfailed; `uv run ruff check .` sạch. Phần sửa này chỉ siết thêm, Lá Chắn soát lại trong lượt kiểm bằng Fable sau 01/11.

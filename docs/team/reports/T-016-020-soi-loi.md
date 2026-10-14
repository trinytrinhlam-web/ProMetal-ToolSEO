# Báo cáo T-016 + T-020 · Kiểm thử kho nháp và nhập khóa API trong app

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-016](../tickets/T-016-luu-nhap-bai-dang-soan.md), [T-020](../tickets/T-020-nhap-khoa-api-trong-app.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. **Đạt có điều kiện**: không có lỗi Nghiêm trọng/Cao, có 2 lỗi Trung bình (T-016) và 7 lỗi Thấp |

## Tóm tắt (cho chủ dự án)

Nhập khóa API trong app (T-020) chạy an toàn: khóa không lộ ra màn hình, bộ nhớ phiên, thông báo lỗi hay log; không ai chèn được biến khác vào `.env` qua ô nhập (đã thử 21 cách). Chỉ còn vài trường hợp hiếm khi file `.env` đã bị sửa tay theo kiểu lạ: app báo "đã lưu" nhưng khóa chưa có hiệu lực.

Kho nháp (T-016) lưu và mở lại đúng nguyên vẹn, kể cả tiếng Việt, emoji và mọi phiên bản. File hỏng không làm app sập. Có 2 lỗi nên sửa trước khi đóng phiếu: (1) xóa file nháp trong lúc app đang chạy thì app không lưu được nữa cho tới khi tắt mở lại; (2) phần nghiên cứu và rà soát đọc từ file nháp không được lọc lại link/HTML.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t016_t020.py` (mới) | 102 test: 92 qua, 10 `xfail(strict=True)` ứng với 9 lỗi R8-1…R8-9 |
| `docs/team/reports/T-016-020-soi-loi.md` (mới) | Báo cáo này |

Không sửa code ứng dụng, không sửa `tests/conftest.py`, không chạy lệnh git đổi thư mục làm việc, không commit.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t016_t020.py -q
92 passed, 10 xfailed in 5.25s

$ uv run pytest -q
1804 passed, 13 xfailed in 93.41s   (13 xfail = 3 có từ trước + 10 của báo cáo này)

$ uv run ruff check .
All checks passed!
```

Chạy `--runxfail` để chắc mỗi xfail hỏng đúng vì lỗi đã mô tả (không phải lỗi của test): cả 10 hỏng đúng chỗ (xem cột "Thực tế" bên dưới).

Trang Soạn bài (`app/views/write.py`, Họa Sĩ đang sửa cho T-017): **không** có test nào đỏ ở lần chạy này.

## Lỗi tìm thấy

| Mã | Phiếu | Mức | Tóm tắt | Test |
|---|---|---|---|---|
| R8-1 | T-016 | **Trung bình** | Xóa file nháp / thư mục `data/` khi app đang chạy → mọi lần lưu sau đều lỗi tới khi khởi động lại app | `test_deleting_drafts_file_while_running_recovers[file\|folder]` |
| R8-2 | T-016 | **Trung bình** | `research` / `review` đọc từ file không được lọc lại link Markdown và thẻ HTML | `test_planted_links_and_html_in_research_and_review_are_disabled` |
| R8-3 | T-016 | Thấp | Thông báo lỗi kiểm khuôn chép tên trường từ file (khóa của `material`) → link lọt vào `st.error` | `test_error_message_does_not_echo_file_content` |
| R8-4 | T-016 | Thấp | `DraftStore()` không truyền đường dẫn luôn trỏ `data/drafts.sqlite` thật, kể cả trong test | `test_default_store_follows_patched_default_path` |
| R8-5 | T-016 | Thấp | Chữ có ký tự surrogate lẻ → `save` ném `PydanticSerializationError` thay vì `DraftError` | `test_lone_surrogate_gives_draft_error` |
| R8-6 | T-016 | Thấp | Đồng hồ máy bị chỉnh lùi khi đã có 30 nháp → nháp vừa lưu bị xóa ngay, `save` vẫn báo thành công | `test_clock_going_back_does_not_drop_just_saved_draft` |
| R8-7 | T-020 | Thấp | Dòng `ANTHROPIC_API_KEY=` nằm **trong** giá trị nhiều dòng của biến khác → sửa nhầm biến đó, khóa không có hiệu lực, app vẫn báo "Đã lưu" | `test_key_line_inside_other_multiline_value` |
| R8-8 | T-020 | Thấp | `splitlines()` tách cả U+2028, U+0085, `\x0c`… nên dòng chú thích chứa ký tự đó bị coi là dòng khóa → khóa không có hiệu lực, app vẫn báo "Đã lưu" | `test_unicode_line_separator_in_comment` |
| R8-9 | T-020 | Thấp | python-dotenv coi `\'` là escape trong nháy đơn, `env_file` thì không → giá trị cũ nhiều dòng bị cắt dở, phần đuôi thành biến mới | `test_single_quote_escape_matches_dotenv` |

### Chi tiết

**R8-1 (Trung bình).** Tái hiện: `store.save(...)`; xóa `drafts.sqlite` (hoặc cả thư mục `data/`); `store.save(...)` lần nữa.
Mong đợi: tạo lại file và lưu được (CLAUDE.md: "cache SQLite; xóa đi vẫn tạo lại được").
Thực tế: `DraftError: File nháp bị lỗi nên không đọc/ghi được. Thử tải lại trang.` Nguyên nhân: `_prepare` chỉ chạy một lần (`seo_app/storage/drafts.py:279`, cờ `_ready`), lần sau `sqlite3.connect` tạo file rỗng không có bảng (hoặc không mở được vì mất thư mục). Trang Soạn bài giữ `DraftStore` bằng `st.cache_resource` (`app/views/write.py:195`), nên lời khuyên "tải lại trang" **không** có tác dụng: phải tắt app. Người dùng mất bài đang viết nếu không để ý dòng cảnh báo nhỏ. Gợi ý sửa: khi lỗi "no such table"/không mở được thì đặt lại `_ready = False` và thử `_prepare` một lần.

**R8-2 (Trung bình theo tiêu chí kiểm thử; rủi ro thực tế thấp).** Tái hiện: sửa dòng trong `drafts.sqlite` để `research.intent = ["[bấm vào đây](https://evil.example/x) <script>…"]`, rồi `load`.
Mong đợi: link và thẻ HTML bị vô hiệu như khi AI trả về (`clean_ai_text` trong `seo_app/content/workflow.py`).
Thực tế: giữ nguyên (`drafts.py:105`, `:111` chỉ kiểm khuôn). Trang Soạn bài hiện các chữ này bằng `st.markdown` (`write.py:506`, `:518`, `:700`…), nên link hiện ra bấm được. Chỉ phần thân bài (`versions`) được escape lại. Muốn ghi được file này thì phải có quyền trên máy (Thợ Máy đã nêu), nên đây là lớp phòng thủ thứ hai; nhưng phiếu ghi rõ "dữ liệu đọc từ file coi là chưa tin cậy". Gợi ý: validator chạy `clean_ai_text` cho các trường chữ của `Research`/`Review` khi đọc nháp (idempotent nên không đổi bản đúng). `Competitor.url` kiểu `javascript:` đã được `markdown_link` chặn ở giao diện.

**R8-3 (Thấp).** `material = {"[bấm vào đây](https://evil.example/x)": 123}` → `DraftError` có chữ `material.[bấm vào đây](https://evil.example/x)` (`_short`, `drafts.py:327`), mà `write.py` hiện bằng `st.error` (Markdown). Gợi ý: chỉ nêu tên trường cấp 1 (`material`), hoặc cắt và escape phần vị trí.

**R8-4 (Thấp).** `path: Path = DEFAULT_DRAFTS_FILE` (`drafts.py:166`) gắn lúc import, nên `monkeypatch` của `conftest.py` không có tác dụng với `DraftStore()`. Trang Soạn bài hiện truyền đường dẫn rõ ràng nên chưa sao, nhưng mục "Cách giao diện dùng" trong báo cáo T-016 lại gợi ý `return DraftStore()`: ai làm theo thì test sẽ ghi vào `data/` thật. Gợi ý: `field(default_factory=lambda: drafts.DEFAULT_DRAFTS_FILE)` hoặc `path: Path | None = None` rồi tra lúc dùng.

**R8-5 (Thấp).** `store.save(DraftSnapshot(keyword="abc\ud800"))` → `PydanticSerializationError` (ở `drafts.py:184`). Trang Soạn bài bắt `ValueError` nên không sập; chỉ sai hợp đồng "lỗi kho nháp luôn là `DraftError`". Khó gặp thật (trình duyệt gửi UTF-8 hợp lệ).

**R8-6 (Thấp).** Có 30 nháp, đồng hồ máy bị chỉnh lùi 1 giờ, lưu bài mới → bài mới có `saved_ts` nhỏ nhất nên bị lệnh dọn (`drafts.py:206`) xóa ngay; `save` trả về bình thường, mở lại thì "Không tìm thấy nháp". Gợi ý: không bao giờ xóa đúng `id` vừa lưu (`... AND id != ?`).

**R8-7, R8-8, R8-9 (Thấp, T-020).** Chỉ xảy ra khi `.env` đã bị sửa tay theo kiểu lạ, không xảy ra qua ô nhập. Hậu quả chung: app báo "Đã lưu khóa" nhưng `load_settings()` không thấy khóa mới (R8-7, R8-8), hoặc sinh thêm một biến từ phần đuôi của giá trị cũ (R8-9). Không lộ khóa. Nguyên nhân: `env_file` tự tách dòng (`seo_app/env_file.py:143`, `splitlines`) và tự đoán nháy (`:88`, `:97`, `:109`) khác cách python-dotenv đọc. Gợi ý gọn: sau khi ghi, đọc lại bằng `dotenv_values` và so: khóa phải đúng giá trị mới, các biến khác phải giữ nguyên; sai thì khôi phục bản cũ và báo "File .env có định dạng lạ, hãy sửa tay". Tách dòng nên dùng `split("\n")` giữ `\r` thay cho `splitlines`.

## Đối chiếu yêu cầu kiểm thử

**T-020**
- [x] Khóa không lộ ở giao diện, `session_state` sau khi lưu / lỗi / gõ mà không lưu rồi sang trang khác, thông báo lỗi, log, `repr`, traceback: `test_ui_failed_write_shows_friendly_error_without_path_or_key`, `test_ui_key_typed_but_not_saved_leaves_session_on_other_page`, `test_no_log_or_print_of_key`, `test_validation_error_traceback_has_no_key`, `test_settings_repr_does_not_show_key`, `test_check_result_repr_has_no_key`.
- [x] Chèn biến khác qua ô nhập: 21 kiểu (xuống dòng `\n` `\r`, U+2028/2029, NEL, `\x0b` `\x0c` `\x1c`, NUL, ký tự độ rộng 0, đảo chiều, BOM, dấu `=` toàn khổ, `${…}`, `\n` dạng chữ, nháy, `;`, chữ có dấu, chữ số Ả Rập, quá 513 ký tự) đều bị từ chối, file không đổi một byte: `test_injection_attempts_rejected_and_file_unchanged`; qua giao diện: `test_ui_injection_through_input_keeps_env`; tên biến lén (`ANTHROPIC_API_KEY\n`, `APP_PASSWORD_HASH`…): `test_variable_name_cannot_be_smuggled`.
- [x] CRLF, BOM, dòng LF lẫn trong file CRLF, dòng trùng tên, `export`, khoảng trắng quanh `=`, giá trị nhiều dòng trong nháy, chú thích, dòng cuối không xuống dòng: mọi dòng khác giữ nguyên từng byte (`test_messy_env_only_key_lines_change`, `test_clear_on_messy_env_keeps_other_bytes`, `test_repeated_saves_are_stable`). Ngoại lệ là 3 kiểu hiếm R8-7…R8-9.
- [x] `.env` là symlink: liên kết bị thay bằng file thường, file đích ngoài thư mục app không bị ghi (`test_symlink_env_is_replaced_not_followed`); symlink tới thư mục: lỗi dễ hiểu, không lộ đường dẫn; symlink trỏ vào chỗ không có: tạo file thường, không tạo file đích.
- [x] `.env` chỉ đọc: giả lỗi quyền ở 3 chỗ (đọc, tạo file tạm, thay file) → thông báo có chữ ".env", không có đường dẫn hay khóa, file cũ còn nguyên, không sót file tạm (`test_read_only_env_gives_friendly_error_without_path[read|mkstemp|replace]`). Máy test chạy bằng root nên `chmod` không chặn được; test `chmod 444` thật chỉ kiểm "không sập, không lộ đường dẫn" (trên Mac/Linux, `os.replace` vẫn thay được file chỉ đọc khi thư mục ghi được, đây là hành vi bình thường).

**T-016**
- [x] Lưu rồi đọc lại nguyên vẹn: tiếng Việt, dạng NFD không bị chuẩn hóa, emoji ngoài BMP, CRLF/CR/tab/NUL, dấu `\`, chữ giống SQL, HTML, chuỗi rỗng; mọi phiên bản và phiên bản đang chọn; 200 phiên bản; giờ lưu +07:00 (`test_round_trip_tricky_text_every_version`, `test_round_trip_many_versions`). Lưu/mở 10 vòng không thêm dấu `\` (`test_many_save_load_cycles_do_not_change_text`).
- [x] Giới hạn 30: lưu 35 nháp → còn đúng 30 mới nhất, 5 nháp cũ nhất không mở được (`test_limit_30_drops_exactly_the_oldest`); ghi đè cùng mã không tạo nháp mới. Ngoại lệ R8-6.
- [x] Giới hạn 5 MB: tính theo byte UTF-8, không theo số ký tự (`test_limit_counts_utf8_bytes_not_characters`); sát giới hạn lưu được, quá giới hạn bị từ chối và bản cũ còn nguyên; dòng quá lớn cài vào file bị từ chối khi mở.
- [x] File hỏng không làm sập: file rỗng, toàn byte 0, đầu giống SQLite nhưng hỏng, chữ thường, CSDL bị cắt đôi; bản hỏng được giữ lại nguyên byte (`test_corrupt_files_never_crash`, `test_truncated_real_database_never_crashes`).
- [x] Khuôn sai: JSON `null`/`[]`/chuỗi/không phải JSON, lồng 100.000 tầng, số vô cực, 11 kiểu sai khuôn (bước -1/5, phiên bản rỗng, `current` âm, 21 ô chất liệu, thiếu múi giờ, phiên bản khuôn 2, mã không khớp, trường lạ chứa "khóa") → `DraftError`, thông báo không chép giá trị (`test_bad_json_in_row_gives_draft_error`, `test_wrong_shape_rows_give_draft_error`). Dòng danh sách sai kiểu bị bỏ qua và đếm (`test_planted_listing_rows_with_wrong_types_are_skipped`).
- [x] Chèn SQL qua mã nháp (10 kiểu, gồm `None`, số, bytes, chữ hoa, chữ số toàn khổ, xuống dòng cuối, `' OR '1'='1`) và qua nội dung (`'); DROP TABLE drafts; --` ở từ khóa, tiêu đề, chất liệu): bị chặn / lưu như dữ liệu thường, bảng còn nguyên.
- [ ] Nội dung độc trong file khi đọc lại phải bị vô hiệu: **đạt với thân bài** (`test_planted_links_in_article_versions_are_disabled`, gồm cả link kiểu khai báo `[a]: url`), **chưa đạt** với nghiên cứu / rà soát (R8-2) và thông báo lỗi (R8-3).

## Rủi ro và điểm cần chú ý

- R8-2 và R8-3 cần người có quyền ghi file trên máy mới khai thác được; Lá Chắn quyết định có chấp nhận tạm hay không.
- Không thử được trên Windows thật: khóa file khi đang mở (`os.replace` trên file đang bị chương trình khác mở sẽ lỗi `PermissionError`, đã được bắt và báo dễ hiểu theo test giả lập).
- Ô nhập khóa vẫn giữ khóa trong `session_state` trong lúc gõ (Họa Sĩ đã nêu). Test xác nhận: sang trang khác thì khóa bị bỏ khỏi `session_state`.

## Đề xuất

- Thợ Máy: sửa R8-1 và R8-2 trước khi đóng T-016; R8-3…R8-6 sửa cùng lúc (mỗi lỗi vài dòng). Sửa xong gỡ dấu `xfail` tương ứng trong `tests/test_soi_loi_t016_t020.py` (test sẽ báo XPASS).
- Thợ Máy: R8-7…R8-9 có thể gộp bằng một bước "đọc lại bằng python-dotenv và so" sau khi ghi `.env`.
- Thư Ký / Thợ Máy: sửa mục "Cách giao diện dùng" trong `T-016-tho-may.md` (đang gợi ý `DraftStore()` không truyền đường dẫn, xem R8-4).

## Câu hỏi cho chủ dự án

Không có.

---

## Lần 2 · Kiểm lại T-021 và kiểm thử T-017 (2026-10-14)

**Kết quả: ĐẠT.**
- Mọi lỗi R8-1…R8-9 đã sửa: các test xfail cũ nay qua.
- T-017 đạt mọi điểm Chỉ Huy yêu cầu kiểm.
- Còn 1 lỗi mới mức Thấp (R9-1). Lỗi này chỉ xảy ra khi file nháp bị sửa tay.

### Tóm tắt (cho chủ dự án)

- **Kho nháp.** Mở lại một nháp thì mọi chữ do AI viết đều được lọc lại: link lạ và mã HTML cài vào file bị vô hiệu ở mọi chỗ. Nháp bình thường lưu/mở nhiều lần không đổi một chữ nào.
- **File `.env`.**
  - Dòng khóa thiếu dấu nháy đóng: app báo lỗi và không làm mất dòng nào.
  - Ghi xong mà đọc lại thấy sai: app trả lại đúng bản cũ, từng byte.
  - `.env` là liên kết tắt (symlink): app từ chối ghi.
- **Trang Soạn bài.** Tự lưu, mở và xóa nháp đều đúng. Bài mới không mang chất liệu thật của bài cũ. Các ô nhập không mất chữ khi chuyển bước. Test không ghi vào `data/` thật.

### Đã thay đổi (lần 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t021_t017.py` (mới) | 32 test: 31 qua, 1 `xfail(strict=True)` cho R9-1 |
| `tests/test_soi_loi_t016_t020.py` | Theo quyết định của Chỉ Huy, sửa `test_round_trip_tricky_text_every_version`: chữ AI so với `clean_loaded(saved)`, từ khóa và chất liệu so nguyên văn. Thêm `test_round_trip_user_text_is_verbatim_even_with_html`. Siết 2 test symlink do Thợ Máy đổi (xem dưới). |
| `tests/test_soi_loi_round5.py` | `test_clean_grows_linearly_on_nested_parentheses` trước đo bằng đồng hồ thường (`time.perf_counter`), nay chuyển sang `tests/timing.py` (đo thời gian CPU) |

### Bằng chứng

```
$ uv run pytest -q
1869 passed, 4 xfailed in 79.47s   (4 xfail = 3 có từ trước + R9-1)

$ uv run pytest -q tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py
136 passed, 1 xfailed in 7.51s

$ uv run ruff check .
All checks passed!
```

Sau khi chạy toàn bộ test, thư mục `data/` thật vẫn trống (`ls -la data/`).

### Hai test symlink Thợ Máy đã đổi

Thợ Máy đổi hai test này đúng theo yêu cầu mới của phiếu ("từ chối ghi"). Tuy vậy chúng còn lỏng: chỉ thử thao tác Lưu, và không kiểm liên kết còn trỏ đúng chỗ cũ. Tôi đã siết lại như sau:
- `test_symlink_env_is_refused[set|clear]` kiểm:
  - cả Lưu lẫn Xóa;
  - file đích còn nguyên từng byte;
  - liên kết vẫn là symlink và vẫn trỏ đúng file cũ (`readlink`);
  - không sót file tạm;
  - thông báo không chứa đường dẫn, tên thư mục, tên file đích hay khóa, và có nói rõ là symlink.
- `test_dangling_symlink_is_refused[set|clear]` kiểm:
  - cả Lưu lẫn Xóa;
  - liên kết giữ nguyên;
  - không tạo file đích, không tạo file nào khác;
  - thông báo không lộ đường dẫn.

Code hiện tại qua cả 4 trường hợp.

### Đối chiếu các điểm Chỉ Huy giao

**Kho nháp (T-021 phần A)**
- [x] Nháp đúng không đổi sau nhiều vòng lưu/mở:
  - `test_clean_draft_unchanged_after_many_save_open_cycles`: nháp giống thật, 8 vòng; có `[cần bổ sung: …]`, CRLF, `\`, link nội bộ đã escape.
  - `test_cleaning_is_idempotent_on_random_text`: 900 nháp chữ ngẫu nhiên gồm `[]()<>!`*\:#`, CRLF, `<!--`, `](`. Kiểm `clean_loaded(clean_loaded(x)) == clean_loaded(x)` ở mọi trường.
- [x] Nháp độc bị vô hiệu ở mọi trường: `test_poison_is_disabled_in_every_ai_field` duyệt tự động mọi chuỗi trong nháp (≥ 18 chỗ). Mẫu độc gồm link nội dòng, ảnh, link kiểu khai báo `[ref]: url`, `<img onerror>`, `<script>`.
  - Thân bài: link bị escape.
  - Chữ AI khác: địa chỉ link bị bỏ hẳn.
  - URL `javascript:` của đối thủ bị bỏ.
  - Tên bài đối thủ chỉ được bỏ thẻ HTML. Đây là thiết kế có sẵn: giao diện hiện tên này qua `markdown_link`, hàm này escape mọi ký tự Markdown. Test kiểm đúng chữ sau khi qua `markdown_link`.
- [x] Từ khóa và chất liệu thật giữ nguyên văn: `test_user_fields_are_kept_verbatim_when_poisoned`. Riêng `research_keyword` được lọc theo Lá Chắn #4 (thay đổi Thợ Máy làm trong lúc tôi kiểm).
- [x] Hiển thị thật: `test_poisoned_draft_does_not_render_links_or_html` mở nháp độc và chạy qua đủ 5 bước. Không chỗ hiển thị Markdown nào có `](https://evil…`, `<script` hay `onerror`.
- [x] R8-1: xóa file nháp thì lần lưu sau tạo lại file, không báo nhầm "file hỏng" (`test_recreated_after_delete_keeps_limit_and_reports_nothing_wrong`). R8-3: thông báo lỗi không chép chữ nào từ file, đã thử 4 kiểu (`test_error_messages_never_echo_planted_text`).

**Ghi `.env` (T-021 phần B)**
- [x] Dòng khóa thiếu nháy đóng không làm mất dòng khác: `test_unclosed_quote_never_loses_following_lines`, 10 trường hợp gồm nháy kép, nháy đơn, `export … =`, dòng trống phía trước, `\"` ở cuối; mỗi trường hợp thử cả Lưu và Xóa.
  - File giữ nguyên từng byte, kể cả các dòng `APP_PASSWORD_HASH`, `WORDPRESS_APP_PASSWORD` phía sau.
  - Không sót file tạm, thông báo không chép giá trị cũ.
  - Qua giao diện: báo "sai định dạng", không báo "Đã lưu", không lộ khóa (`test_ui_reports_format_error_not_saved`).
- [x] Dòng hỏng của biến khác không chặn việc ghi và không mất dòng nào (`test_unclosed_quote_on_other_variable_keeps_every_line`).
- [x] Khôi phục khi đọc lại sai, giả lập đĩa ghi sai ở lần ghi đầu:
  - file có BOM + CRLF được trả lại đúng từng byte (`test_restore_old_file_when_read_back_differs`);
  - trước đó chưa có file thì file mới bị xóa (`test_restore_removes_new_file_when_none_existed`);
  - bước khôi phục cũng lỗi thì thông báo vẫn dễ hiểu, không lộ khóa hay đường dẫn (`test_restore_failure_still_gives_friendly_error`).
- [x] Biến khác chứa `${ANTHROPIC_API_KEY}` (Thợ Máy đề nghị): dòng đó giữ nguyên, khóa ghi đúng (`test_other_variable_referencing_key_is_untouched`).

**Trang Soạn bài (T-017).** Họa Sĩ đã có 18 trường hợp trong `tests/test_app_drafts.py`. Tôi thêm các test sau:
- [x] Mở và xóa nháp:
  - Đang mở nháp A, xóa nháp B: A vẫn mở và dùng được (`test_deleting_other_draft_keeps_open_one`).
  - Mở nháp hỏng: báo lỗi, bài đang soạn không bị xóa trắng (`test_failed_open_keeps_current_work`).
- [x] Bài mới không mang chất liệu thật của bài cũ:
  - Đang mở A rồi mở B: chất liệu, dàn ý và các phần của A không sót sang B, nháp A không bị ghi đè (`test_opening_draft_b_does_not_carry_material_of_open_draft_a`).
  - Mở nháp rồi bấm "Viết bài mới": trang trống, nháp cũ còn nguyên (`test_new_article_after_opened_draft_starts_clean`).
- [x] Test không ghi vào `data/` thật: `test_tests_never_write_real_data_folder` chạy trọn luồng tự lưu. Kho nháp nằm ở thư mục tạm, `DraftStore()` cũng trỏ thư mục tạm (R8-4 đã sửa), file thật không đổi.
- [x] Sau khi rời bước 1, các ô nhập không mất chữ: `test_inputs_keep_text_after_leaving_step_one`. Đủ 3 ô chất liệu, từ khóa, tiêu đề dàn ý và tiêu đề mục còn nguyên sau 4 lần chạy. Quay lại bước 1 thì ô hiện đúng chữ đã gõ, nháp lưu đủ.

**Test tốc độ chập chờn**
- `test_soi_loi_round6`/`round7` đã dùng `tests/timing.py` (thời gian CPU), không phải đồng hồ thường, nên không cần đổi.
- Lần trượt Họa Sĩ gặp là `test_helper_catches_quadratic_function`. Test này kiểm chính bộ đo có bắt được hàm bình phương hay không. Tôi đo 6 lần trên máy này, tỉ lệ thời gian 14–20 lần, ngưỡng là 9. Lần trượt là do máy quá bận làm nhiễu cả phép đo thời gian CPU (bộ nhớ đệm, xung nhịp CPU). Tôi chưa nới test này, vì nới thì chính bộ đo sẽ dễ bỏ sót hàm chậm thật.
- Test duy nhất còn đo bằng đồng hồ thường là `tests/test_soi_loi_round5.py::test_clean_grows_linearly_on_nested_parentheses`, đã chuyển sang `timing.py`.

### Lỗi mới

| Mã | Phiếu | Mức | Lỗi | Test |
|---|---|---|---|---|
| R9-1 | T-017 / T-021 | Thấp | Từ khóa đọc từ nháp được giữ nguyên văn (đúng quyết định). Nhưng nếu file nháp bị sửa tay để từ khóa có **dòng trống**, dòng "Từ khóa: …" dưới tiêu đề trang thoát khỏi khối HTML, và phần sau dòng trống được hiện như Markdown, có link bấm được. | `test_planted_keyword_cannot_render_links` (xfail) |

R9-1 chi tiết:
- **Tái hiện:** sửa `keyword` trong `drafts.sqlite` thành `"cổng\n\n[bấm vào đây](https://evil.example/k)"`, rồi mở nháp.
- **Mong đợi:** không hiện link.
- **Thực tế:** `ui.page_header` (`seo_app/ui.py:15`) đặt `html.escape(subtitle)` vào `<p>…</p>` với `unsafe_allow_html=True`. `html.escape` không xử lý xuống dòng, nên dòng trống kết thúc khối HTML.
- **Thực tế ít gặp:** ô từ khóa trên giao diện chỉ nhận một dòng, nên chỉ xảy ra khi file nháp bị sửa tay. Mức Thấp.
- **Gợi ý sửa, một trong hai cách:**
  - (a) `page_header` gộp mọi khoảng trắng của phụ đề về một dấu cách;
  - (b) `DraftSnapshot` không nhận `keyword` có xuống dòng.

### Rủi ro và điểm cần chú ý

- Trong lúc tôi kiểm, Thợ Máy vẫn sửa `seo_app/storage/drafts.py` (thêm lọc `research_keyword`, Lá Chắn #4). Test của tôi đã theo bản lúc 14:07. Nếu có thay đổi sau đó thì cần chạy lại.
- Thay đổi hành vi đã được chốt: tiêu đề mục dàn ý mà người dùng tự gõ có link hoặc thẻ HTML sẽ mất link/thẻ khi mở lại nháp.

### Đề xuất

- Họa Sĩ hoặc Thợ Máy sửa R9-1 bằng một dòng (cách a hoặc b). Sửa xong thì gỡ dấu `xfail` trong `tests/test_soi_loi_t021_t017.py`.
- Lá Chắn có thể xem lại phần B: bước khôi phục bản cũ ghi lại cả quyền `600`, đúng như lần ghi đầu.

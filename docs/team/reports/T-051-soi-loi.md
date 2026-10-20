# Báo cáo T-051 · Soi Lỗi rút gọn: prompt alt và cấu hình việc ảnh

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-051](../tickets/T-051-prompt-alt-va-cau-hinh-anh.md) · báo cáo Ngòi Bút: [T-051-ngoi-but](T-051-ngoi-but.md) |
| Ngày nộp | 2026-10-20 |
| Mức kiểm | Rút gọn (cấu hình đọc được, test cấu hình qua) |
| Kết quả | Hoàn thành · **ĐẠT**, chuyển sang Lá Chắn rút gọn được |

## Tóm tắt (cho chủ dự án)

Hai file cấu hình mới của Ngòi Bút đọc được bằng đúng bộ đọc của phần mềm, và không làm thay đổi gì ở các việc viết bài đang chạy. Việc **tạo ảnh** bằng Gemini đang để tắt đúng như Ngòi Bút ghi: tôi bật thử trên bản sao tạm và xác nhận nếu bật bây giờ thì trang Soạn bài đòi khóa Gemini dù chỉ viết bài. Vì vậy phải chờ phiếu T-062 xong mới bật. 6 ví dụ alt đều ngắn (41–80 ký tự, giới hạn 125), không nhồi từ khóa, không bịa nơi chốn hay tên khách. Ảnh AI luôn mở đầu bằng «Minh họa». Không tìm thấy lỗi nào trong T-051. Có 2 việc nhỏ Chỉ Huy cần biết trước khi giao T-062 (mục Lỗi và ghi nhận).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t051.py` | Mới: 36 test qua và 5 test `xfail(strict=True)` cho các việc còn chờ T-062 (SL-T051-1 → 4) |
| `docs/team/reports/T-051-soi-loi.md` | Báo cáo này |

Không sửa `config/`, `seo_app/`, `app/` hay test cũ.

## Kết quả kiểm

### 1. Hai file TOML đọc được, mục mới không làm hỏng việc cũ, file hỏng vẫn chịu lỗi như T-010

- Diff của Ngòi Bút chỉ **thêm dòng**, không xóa dòng nào: `git diff --numstat origin/main...fc39367 -- config/` ra `33 0 config/ai.toml`, `89 0 config/content.toml`.
- Cả hai file lưu UTF-8, không BOM, xuống dòng LF, chữ Việt dạng NFC (đếm ký tự không lệch giữa Windows và Mac).
- `load_ai_config()` đọc được 7 việc: research, outline, write, rewrite, review, meta, **alt**. Chỉ `research` bật tìm web (`test_old_tasks_still_load_next_to_alt`).
- `[tasks.alt]` (`config/ai.toml:71-77`): anthropic, `claude-sonnet-5-5`, effort `low`, `max_tokens` 2000, không tìm web (`test_alt_task_is_claude_sonnet_with_small_budget`).
- `load_rules()` của file mới **bằng hệt** `load_rules()` của file đã bỏ hai mục `[images]`, `[alt]` (`test_new_sections_do_not_change_old_rules`).
- `[images]` (`config/content.toml:78-85`): `webp_quality = 80` (số nguyên 1–100), `max_edge_px = 1600` (đúng quyết định 5A).
- File hỏng hay thiếu mục, dùng chính nội dung file thật (`test_real_ai_toml_broken_on_disk_is_handled_like_t010`, `test_real_content_toml_broken_on_disk_is_handled_like_t010`, `test_write_page_survives_broken_real_content_toml`):

| File | Trường hợp | Kết quả |
|---|---|---|
| ai.toml | Có BOM (Notepad cũ) | Đọc được, giống hệt file gốc |
| ai.toml | Lưu kiểu ANSI (cp1258) | `AIError` «không lưu ở dạng UTF-8…» |
| ai.toml | Lưu dở giữa `[tasks.alt]` | `AIError` «viết sai cú pháp» |
| ai.toml | Chỉ xóa `#` ở 2 dòng đầu khối ảnh (quên dòng model) | `AIError` «Việc «image»: chưa ghi tên mô hình (model).»; trang Soạn bài báo lỗi này, khóa nút AI, không sập |
| content.toml | Có BOM | Đọc được, giống hệt |
| content.toml | Lưu kiểu ANSI | `ContentRulesError` «UTF-8»; trang Soạn bài báo, không sập |
| content.toml | Lưu dở giữa ví dụ alt đầu tiên | `ContentRulesError` «cú pháp»; trang Soạn bài báo, không sập |
| content.toml | Thiếu cả `[images]` và `[alt]` | Việc cũ chạy y như trước |
| content.toml | `max_chars = "125"` (chữ thay vì số) | Việc cũ chạy y như trước (bộ đọc hiện chưa đọc `[alt]`; T-062 sẽ đọc và báo lỗi tiếng Việt) |

### 2. Khối `[tasks.image]` đang tắt, bật thử trên bản tạm

- Khối nằm ở `config/ai.toml:94-97`, đúng 4 dòng «# [tasks.image]», «# provider», «# model», «# max_tokens» như chú thích hướng dẫn ở dòng 83 (`test_image_block_has_the_four_lines_the_comment_names`). Hàm bật thử trong test dùng được cả khi khối đã bật thật (sau T-053), nên các test này không phải viết lại (`test_enable_helper_also_works_when_block_is_already_on`).
- Với cấu hình đang commit và **chỉ có khóa Claude**: trang Soạn bài không báo thiếu khóa nào, nút «🔎 Phân tích từ khóa» bấm được, khóa giả không hiện ra màn hình (`test_write_page_with_committed_config_needs_only_claude_key`). `tests/test_app_pages.py` (mở mọi trang) vẫn qua trong lần chạy toàn bộ.
- Bật thử trong `tmp_path` (không đụng file thật), cả kiểu xóa «# » và kiểu chỉ xóa «#» để lại dấu cách: đọc ra `gemini`, `gemini-nano-banana-2.1`, `max_tokens` 2000; 7 việc còn lại không đổi (`test_enabled_image_block_reads_as_gemini_and_keeps_other_tasks`).
- **Xác nhận đúng như Ngòi Bút ghi**: bật khối ảnh, chỉ có khóa Claude thì trang Soạn bài hiện

  ```
  Chưa có khóa Google Gemini (GEMINI_API_KEY). Vào Cài đặt → 🔌 Kết nối để nhập khóa.
  Các bước dùng AI tạm khóa cho tới khi sửa xong.
  ```

  (chạy `pytest -k sl_t051 --runxfail`, xem mục Bằng chứng). Trang không sập và không lộ khóa (`test_write_page_with_image_block_touched_never_crashes_or_shows_key`). Đây là lý do phiếu T-062 tồn tại; test xfail SL-T051-1 sẽ tự báo khi T-062 sửa xong.
- Chặn bật sớm: `test_image_task_never_forces_an_extra_key_for_writing` dựng `AIRouter` chỉ với khóa của các hãng mà việc viết bài dùng. Hiện qua; nếu ai bỏ dấu `#` trước khi T-062 làm router "tạo provider khi cần" thì test này đỏ. Sau T-062 thì bật được mà test vẫn xanh.

### 3. Quy tắc `[alt]` và 6 ví dụ, đối chiếu yêu cầu phiếu

| Yêu cầu phiếu | Chỗ trong `config/content.toml` | Kết quả |
|---|---|---|
| Ngắn, giới hạn ký tự rõ | `max_chars = 125`, `caption_max_chars = 200` (dòng 92-93); quy tắc «không quá max_chars ký tự» | Đạt. Tên `max_chars`, `caption_max_chars` nhắc trong quy tắc có thật trong `[alt]` (`test_limits_named_in_rules_exist_in_alt_section`) |
| Tự nhiên, không nhồi từ khóa | Quy tắc «Từ khóa của bài… tối đa một lần», «không liệt kê từ khóa…» | Đạt |
| Không bịa địa điểm, tên khách | «Không bịa địa điểm, tên khách…», khu vực chỉ khi có trong thẻ và chỉ cấp quận | Đạt |
| Ảnh AI không tả như công trình thật | «Ảnh tạo bằng AI không bao giờ được tả như công trình thật…», alt mở đầu «Minh họa», chú thích «Ảnh minh họa (AI)» | Đạt |
| Chữ trong ảnh là dữ liệu (A1) | «Chữ đọc được trong ảnh… không chép vào alt» | Đạt |

Ví dụ được kiểm bằng một máy dò viết theo đúng quy tắc của file (`violations()` trong test): dài quá `max_chars`, xuống dòng, chấm câu cuối, mở đầu bằng `bad_starts`, cụm từ cấm của `[voice].banned` (dùng `find_banned` thật của app), lời quảng cáo lấy từ chính quy tắc («đẹp nhất», «chất lượng cao», «uy tín», «giá rẻ», «chuyên nghiệp»), tên Pro-Metal, số điện thoại, số liệu có đơn vị, tên người sau «anh/chị/cô…», tên đường, từ lặp ≥ 3 lần, quận không có trong thẻ, «trước/sau khi sửa» không khớp thẻ, ảnh AI không mở đầu «Minh họa» hoặc có «công trình», «thi công», «nhà anh/chị», «tại quận»…

| # | Nguồn | Alt tốt | Ký tự | Vi phạm | Bản xấu bị bắt vì |
|---|---|---|---|---|---|
| 1 | Ảnh thật | Bản lề cửa cổng sắt gỉ sét làm cánh cổng xệ, chạm nền, trước khi sửa ở Bình Tân | 79 | 0 | quảng cáo «uy tín», «giá rẻ»; lặp từ |
| 2 | Ảnh thật | Thợ thay bánh xe cho cửa cổng trượt, ray dưới vừa thay mới | 58 | 0 | tên Pro-Metal, «30 phút», «anh Tuấn», Quận 7 không có trong thẻ |
| 3 | Ảnh thật | Cửa cuốn kẹt lưng chừng, lá cửa bên trái trật khỏi ray, trước khi sửa ở Tân Bình | 80 | 0 | mở đầu «Hình ảnh», số điện thoại, tên đường |
| 4 | Ảnh thật | Cửa kéo sắt sơn xanh vừa sơn lại, đóng kín, sau khi sửa ở Quận 3 | 64 | 0 | «đẹp nhất», «10 năm» |
| 5 | Ảnh AI | Minh họa mặt cắt ray dưới và bánh xe cửa cổng trượt, mũi tên chỉ hướng trượt | 76 | 0 | không mở đầu «Minh họa», «công trình», Pro-Metal, Gò Vấp |
| 6 | Ảnh AI | Minh họa cửa cuốn nhà phố đang mở một nửa | 41 | 0 | không mở đầu «Minh họa», «nhà chị», «sau khi sửa» |

- Số ký tự khớp bảng trong báo cáo Ngòi Bút. 6 alt tốt khác nhau; alt ảnh thật không mở đầu «Minh họa».
- Máy dò được thử ngược với 16 câu sai cố ý, mỗi câu sai một quy tắc: bắt đủ 16 (`test_violation_checker_catches_each_rule`), nên "0 vi phạm" ở trên có ý nghĩa.
- `test_good_examples_follow_their_own_rules`, `test_bad_examples_really_break_a_rule`, `test_good_examples_are_all_different_and_real_ones_do_not_pose_as_ai`, `test_alt_rules_cover_ticket_requirements`: qua.

### 4. Tên mô hình đối chiếu T-046

| Việc | Trong `config/ai.toml` | T-046 | Ghi chú |
|---|---|---|---|
| alt | `claude-sonnet-5-5` | «Claude Sonnet» (câu 4A, `T-046-tho-may.md:236`), không ghi mã | Khớp mã chính thức của Claude Sonnet 5.5 theo tài liệu Claude API (bảng mô hình cập nhật 2026-10-06); Sonnet 5.5 nhận đủ effort `low`…`max`. Lời gọi của `AnthropicProvider` (stream, `output_config.effort`, `fallbacks="default"` kèm beta `server-side-fallback-2026-07-01`, không gửi `thinking`, `tool_choice`, `temperature`) hợp với Sonnet 5.5 theo tài liệu. **Suy luận từ tài liệu, chưa gọi thật** (test không gọi mạng) |
| image (đang tắt) | `gemini-nano-banana-2.1` | Đề xuất ở `T-046-tho-may.md:151, 236` | Khớp. File ghi rõ «CHƯA XÁC MINH bằng lệnh gọi thật» (`config/ai.toml:85-86`) |
| Các mô hình ảnh khác và giá | 0,034/0,050; 0,034; 0,067/0,101; 0,134 USD; `gpt-image-2` 0,053 USD | `T-046-tho-may.md:150-151` (0,0336/0,0504; 0,0336; 0,067/0,101; 0,134; 0,053) | Khớp (làm tròn 3 chữ số), đều ghi «chưa xác minh» |

T-046 còn ghi chưa xác minh `google-genai` 2.30.1 có hàm tạo ảnh `interactions.create` hay không (`T-046-tho-may.md:151`): việc của T-053, không thuộc cấu hình.

## Lỗi và ghi nhận

Không có lỗi trong phạm vi T-051. Các mục dưới đây là việc còn chờ phiếu khác hoặc gợi ý; mục có test thì test đánh dấu `xfail(strict=True)`: **khi T-062 sửa xong, test báo XPASS và Thợ Máy phải gỡ dấu `xfail`**.

| Mã | Mức | Việc | Ai làm |
|---|---|---|---|
| SL-T051-1 | Chặn bật `[tasks.image]` (đã biết) | Bật khối ảnh thì trang Soạn bài đòi khóa Gemini | T-062 YC1 |
| SL-T051-2 | Thấp | Ghi `provider = "anthropic"` cho việc ảnh vẫn đọc được, chưa báo «Claude không tạo được ảnh» (chú thích đầu file đã dặn, code chưa chặn) | T-062 YC2 |
| SL-T051-3 | Thấp, **thấy ngay khi T-051 gộp** | Cài đặt → 🤖 Mô hình AI: bảng việc–mô hình hiện tên thô «alt» (và «meta», có từ trước) vì `TASK_LABELS` chưa có nhãn | T-062 YC3 |
| SL-T051-4 | Thấp | Bật khối ảnh thì thử mù gợi ý `gemini-nano-banana-2.1` làm mô hình viết bài | T-062 YC3 |
| SL-T051-5 | Thấp (phiếu) | Phiếu T-062 YC4 ghi tên khóa `max_alt_chars`, `max_caption_chars`, nhưng file cấu hình dùng `max_chars`, `caption_max_chars` | Chỉ Huy sửa phiếu T-062 trước khi giao |
| SL-T051-6 | Thấp | `alt_system()` của T-050 cắt lời dặn ở 4.000 ký tự. Quy tắc `[alt]` nối lại dài 2.054 ký tự (vừa), nhưng quy tắc kèm 6 ví dụ theo khuôn Ngòi Bút đề xuất dài 4.263 ký tự: cắt cứng sẽ mất gần hết ví dụ ảnh AI cuối, cắt giữa câu | T-062 khi nối `[alt]` vào prompt |
| SL-T051-7 | Gợi ý nội dung | Ví dụ 1: «gỉ sét **làm** cánh cổng xệ» là đoán nguyên nhân (quy tắc 1: không đoán điều ảnh không cho thấy); quy tắc 2 tả đúng hơn: «bị gỉ sét, cánh cửa xệ xuống». Ví dụ 4: hạng mục là sơn nhưng alt ghi «sau khi **sửa**», đọc như «vừa sơn lại… sau khi sửa» | Ngòi Bút, nếu muốn; không chặn |

### Cách tái hiện

- **SL-T051-1:** chép `config/ai.toml` ra thư mục tạm, xóa `# ` ở 4 dòng 94-97, đặt `ANTHROPIC_API_KEY` giả, không có `GEMINI_API_KEY`, mở trang Soạn bài với file đó. Mong đợi: viết bài được, chỉ việc tạo ảnh báo thiếu khóa. Thực tế: cảnh báo «Chưa có khóa Google Gemini (GEMINI_API_KEY)…», mọi bước AI bị khóa. Test: `test_sl_t051_1_enabled_image_needs_gemini_key_only_when_called`, `test_sl_t051_1_write_page_with_image_enabled_does_not_ask_for_gemini_key`.
- **SL-T051-2:** như trên nhưng đổi `provider = "gemini"` thành `"anthropic"`. Mong đợi: `AIError` «Claude không tạo được ảnh…». Thực tế: đọc được, không báo gì. Test: `test_sl_t051_2_image_task_on_anthropic_is_refused`.
- **SL-T051-3:** `blind_test.task_models()` với cấu hình đang commit. Mong đợi: mọi việc có nhãn tiếng Việt. Thực tế: `['meta', 'alt']` dùng tên thô. Test: `test_sl_t051_3_every_task_has_a_vietnamese_label`.
- **SL-T051-4:** `blind_test.model_suggestions(task_models(<file đã bật ảnh>))["gemini"]`. Mong đợi: không có mô hình tạo ảnh. Thực tế: `['gemini-nano-banana-2.1']`. Test: `test_sl_t051_4_blind_test_does_not_suggest_image_model`.
- **SL-T051-5:** `docs/team/tickets/T-062-doc-cau-hinh-viec-anh.md` (trên `main`) dòng 34 so với `config/content.toml:92-93`. Làm theo phiếu thì code đọc sai tên, luôn rơi về mặc định 125/200, và vì mặc định trùng giá trị hiện tại nên không ai thấy cho tới khi chủ dự án đổi số trong file.
- **SL-T051-6:** `git show origin/team/T-050:seo_app/images/alt.py`, dòng 45 (`GUIDANCE_MAX_LENGTH = 4000`) và 166 (`guidance.strip()[:GUIDANCE_MAX_LENGTH]`); đo độ dài bằng kịch bản ở mục Bằng chứng.

## Bằng chứng

```
$ git pull --ff-only            # trong wt-T-051, đầu phiên
Already up to date.             # HEAD fc39367

$ uv run pytest tests/test_soi_loi_t051.py -q -rxX
36 passed, 5 xfailed in 20.69s

$ uv run pytest tests/test_soi_loi_t051.py -q -k sl_t051 --runxfail   # lý do hỏng thật của 5 xfail
E   seo_app.ai.base.AIError: Chưa có khóa Google Gemini (GEMINI_API_KEY). Vào Cài đặt → 🔌 Kết nối để nhập khóa.
E   Failed: DID NOT RAISE AIError
E   AssertionError: assert ['meta', 'alt'] == []
E   AssertionError: assert 'gemini-nano-banana-2.1' not in ['gemini-nano-banana-2.1']
E   AssertionError: ['Chưa có khóa Google Gemini (GEMINI_API_KEY). Vào Cài đặt → 🔌 Kết nối để nhập khóa. Các bước dùng AI tạm khóa cho tới khi sửa xong.']
5 failed, 35 deselected in 20.01s   # SL-T051-2 chạy lại sau khi sửa hàm bật thử: vẫn «DID NOT RAISE AIError»

$ uv run python -X utf8 -c "<đo độ dài [alt]>"
rules joined 2054
examples joined 2208 total 4263

$ uv run pytest
ĐANG CHẠY (chưa có kết quả)

$ uv run ruff check .
All checks passed!
```

Máy chạy: Windows 11 Pro, Python 3.12 (uv). Lần chạy riêng file đầu tiên mất 4 phút 15 giây vì máy đang chạy test của agent khác song song; các lần sau khoảng 20 giây.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Hai file TOML đọc được bằng bộ đọc của app, mục mới không làm hỏng việc cũ (mục 1)
- [x] File hỏng hoặc thiếu mục chịu lỗi như T-010, trang Soạn bài không sập (mục 1)
- [x] `[tasks.image]` đang tắt không làm trang Soạn bài đòi khóa Gemini; bật thử trên bản tạm xác nhận đúng như Ngòi Bút ghi (mục 2)
- [x] Quy tắc `[alt]` và 6 ví dụ đạt yêu cầu phiếu, ví dụ không vi phạm chính quy tắc (mục 3)
- [x] Tên mô hình khớp T-046, chỗ chưa xác minh được ghi rõ (mục 4)
- [x] Có test cấu hình (`tests/test_soi_loi_t051.py`), không gọi mạng, khóa là chuỗi giả, không cần `.env`
- [ ] `uv run pytest` toàn bộ: đang chạy
- [x] `uv run ruff check .` sạch

## Đề xuất

- **Chỉ Huy, trước khi giao T-062:** sửa tên khóa ở YC4 thành `max_chars`, `caption_max_chars` (SL-T051-5); ghi thêm vào T-062 việc gỡ 5 dấu `xfail` SL-T051-1 → 4 trong `tests/test_soi_loi_t051.py` khi làm xong, và cách đưa `[alt]` vào prompt không bị cắt giữa chừng ở 4.000 ký tự (SL-T051-6: đưa quy tắc vào lời dặn, ví dụ để riêng hoặc nâng giới hạn có lý do).
- **Ngòi Bút (không gấp):** cân nhắc sửa câu ví dụ 1 và 4 (SL-T051-7).
- Khi T-053 bật `[tasks.image]`: chạy lại `tests/test_soi_loi_t051.py`. Hàm bật thử chịu được khối đã bật; nếu T-053 đổi mô hình hay hãng thì sửa giá trị mong đợi trong `test_enabled_image_block_reads_as_gemini_and_keeps_other_tasks`.

## Câu hỏi cho chủ dự án

Không có.

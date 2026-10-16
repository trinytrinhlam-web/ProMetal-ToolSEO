# Báo cáo T-034 · Kiểm thử: lỗi Thấp của lớp AI và thử mù (sau T-019)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`), bên Chỉ Huy B, cloud Linux · model: Claude Opus 5.5 |
| Phiếu | [T-034](../tickets/T-034-loi-thap-lop-ai-sau-t019.md) |
| Báo cáo được kiểm | [T-034-tho-may.md](T-034-tho-may.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | **Đạt có điều kiện**: 7/7 lỗi đã sửa đúng; có 2 lỗi mới mức Thấp (SL-T034-1, SL-T034-2) |

## Tóm tắt (cho chủ dự án)

- Cả 7 lỗi của phiếu đều đã sửa đúng. Không thấy câu lỗi nào chép chữ của máy chủ hay để lộ khóa.
- Lỗi chạy song song (SL-T019-5) đã hết. Chạy riêng file test T-028 30 lần lúc máy rảnh và 30 lần lúc máy bận (3 bộ test khác chạy cùng): **60/60 lần qua**.
- Còn 2 lỗi nhỏ mới:
  - Thử mù chưa che phần có gạch nối sau số phiên bản, ví dụ "Gemini 2.5 **Flash-Lite**".
  - Lưới an toàn chưa bắt trường hợp thư viện bỏ hẳn module `_client` khi nâng bản. Hiện chưa xảy ra, và test sẽ báo đỏ nếu chỗ đọc biến bị dời đi.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t034.py` | **Mới**, 187 trường hợp: 182 qua, 5 `xfail(strict)` cho 2 lỗi mới |
| `docs/team/reports/T-034-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng.

## Kết quả theo trọng tâm

| # | Mục | Kết quả | Test chính |
|---|---|---|---|
| 1 | SL-T019-5: không gỡ biến, trỏ tạm `os` của module thư viện | **Đạt**, trừ SL-T034-2 | xem 1a–1f |
| 2 | SL-T019-3: che số phiên bản sau tên | **Đạt**, trừ SL-T034-1 | `test_version_after_masked_name_is_masked` (13 ca), `test_numbers_and_words_without_vendor_untouched`, `test_vietnamese_door_text_still_untouched`, `test_numbers_not_glued_to_name_are_kept`, `test_masking_adversarial_text_is_fast` |
| 3 | SL-T019-4: Claude bị cắt thì ra câu hạ effort | **Đạt** | `test_blind_anthropic_cut_gives_exact_effort_message` (đúng từng chữ `TOKEN_LIMIT_ERROR`), `test_anthropic_cut_found_after_pings`, `test_anthropic_cut_too_far_away_keeps_plain_message`, `test_anthropic_cut_then_error_event_keeps_plain_message`, `test_anthropic_bad_schema_other_reasons_not_token_limit`, `test_anthropic_status_branches_unchanged` |
| 4 | LC-T028-3: nén hỏng thì ra "dữ liệu lạ" | **Đạt** | `test_broken_compression_is_strange_data_everywhere` (gzip, deflate; JSON, SSE, text; cả provider lẫn nút Kiểm tra khóa), `test_real_network_loss_still_says_no_connection`, `test_retry_mix_reports_last_error` |
| 5 | LC-T019-1: ký tự lạ trong tên mô hình | **Đạt** | `test_strange_model_characters_rejected_without_echo` (25 dạng), `test_real_model_names_pass_new_character_check` (42 + 12 tên thật), `test_ui_markdown_model_name_blocked_no_link` |
| 6 | LC-T019-2: không lộ đường dẫn máy | **Đạt** | `test_missing_config_message_has_no_machine_path`, `test_other_config_read_errors_have_no_machine_path` |
| 7 | Câu lỗi cố định, không chép chữ máy chủ, không lộ khóa | **Đạt** | Mọi test trên có kiểm `SERVER_TEXT` và khóa giả không xuất hiện |

### Chi tiết mục 1 (SL-T019-5)

- **1a. Header lạ không tới client ở cả 4 chỗ tạo client.** `test_all_four_creation_sites_in_parallel`: 16 luồng chạy cùng lúc, mỗi luồng 4 lần. Chạy cả 2 provider và 2 hàm Kiểm tra khóa (Anthropic, OpenAI) với thư viện thật và mạng giả. Kết quả: 32 client và 32 yêu cầu đều không có header lạ. Header tổ chức / dự án của OpenAI chỉ mang `Omit`, tức là không gửi. Biến trả lại nguyên vẹn, `os` của module được trả lại, khóa nhả.
- **1b. Luồng khác dùng `os` của module thư viện đúng lúc đang trỏ tạm.** `test_other_threads_using_library_os_while_patched`. Bốn luồng liên tục gọi qua `anthropic._client.os` và `openai._client.os` các hàm sau:
  - `os.name`, `os.sep`, `os.path.join`, `os.fspath`, `os.getpid`
  - `os.getenv("PATH")`, `getenv` có giá trị mặc định
  - `os.environ.get("HTTPS_PROXY")`, `os.environ["HTTPS_PROXY"]`, `in`, `dict(os.environ)`

  Cùng lúc đó, 3 luồng khác bật/tắt khối che. Kết quả: 0 lỗi. Test kiểm thêm rằng luồng đọc **thật sự** gặp lúc `os` đang bị trỏ tạm. `test_filtered_view_inside_block_behaves_like_os` kiểm `len`, `set`, `copy()` của khung nhìn: chỉ thiếu đúng 4 biến bị bỏ qua.
- **1c. Ngoại lệ giữa chừng** (`ValueError`, `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`): `os` của module được trả lại đúng, khóa nhả. Lỗi ở khối trong của một lần gọi lồng không làm hỏng khối ngoài: thư viện vẫn không thấy biến, client tạo trong khối ngoài vẫn sạch.
- **1d. Gọi lồng (`RLock`).** Lồng 5 tầng không treo. Luồng khác phải chờ khối ngoài cùng xong mới vào được (thứ tự `trong → ngoài → khác`). Khi đang ở cách cũ (gỡ biến) mà gọi lồng, biến vẫn ẩn tới khi khối ngoài xong.
- **1e. Thư viện đổi cấu trúc.**
  - Không có tên `os`, hoặc `os` là một lớp bọc khác `os` thật: quay về cách gỡ biến. Client tạo ra vẫn sạch, module kia không bị ảnh hưởng, không tự thêm tên `os`. **Đạt.**
  - Thư viện vẫn cài nhưng **không còn module `_client`**: không quay về cách cũ. → **SL-T034-2**.
- **1f. 4 test Thợ Máy đã đổi dòng kiểm.** Kết luận: **không nới lỏng mục tiêu**, có một điểm cần ghi rõ.
  - **Chặt hơn:** thêm điều kiện `os.environ` của máy giữ nguyên giá trị. Biến rỗng `""` cũng phải bị che.
  - **Hẹp hơn:** câu cũ `name not in os.environ` che biến khỏi **mọi** module của thư viện. Câu mới `library_sees(name) == []` chỉ xét 2 module `_client`.

  Phần hẹp hơn vẫn ổn, vì 3 lẽ:
  - Mục tiêu thật là "header lạ không tới client". Các test kiểm mục tiêu này từ đầu tới cuối không đổi gì và vẫn qua.
  - `test_library_sees_helper_detects_visible_variable` chứng minh `library_sees` thật sự thấy biến khi chưa che, nên dòng kiểm mới không rỗng nghĩa.
  - Tôi thêm `test_only_client_modules_read_ignored_env`. Test này quét mã nguồn thư viện đang cài: chỉ 2 module `_client` (và client Azure / Google Cloud mà app không dùng) nhắc tới 4 biến, và đọc bằng `os.environ.get(`. Nâng thư viện mà chỗ đọc biến dời đi thì test này đỏ ngay.

## Lỗi mới

### SL-T034-1 · Thấp · Biến thể có gạch nối sau số phiên bản còn lộ trong bài thử mù

- **Cách tái hiện:**
  - `_mask_names("Viết bởi Gemini 2.5 Flash-Lite.", ["claude-opus-5-5", "gpt-6.1", "gemini-3-pro"])`
  - Tương tự: `"Tôi là Claude Opus 5.5-preview."`, `"Tôi là Gemini 1.5 Pro-002."`
- **Mong đợi:** che cả phần biến thể. Đây là tên chính thức của hãng ("Gemini 2.5 Flash-Lite").
- **Thực tế:**
  - `«đã ẩn tên mô hình» Flash-Lite.`
  - `… 5.5-preview.`
  - `… Pro-002.`
- **Nguyên nhân:** trong `_VERSION` (`seo_app/content/blind_test.py`), phần nhìn trước `(?![\w.-]*[^\W_])` không cho ăn từ có `-` theo sau. Mục đích là để giữ "5.5mm", nhưng nó chặn luôn "Flash-Lite", "5.5-preview".
- **Hướng sửa gợi ý:** cho phép thêm đuôi `-<biến thể/số>` sau mỗi phần đã che, ví dụ `(?:-(?:lite|preview|exp|\d+))*`. Vẫn giữ nguyên "5.5mm" và số đứng riêng.
- **Test:** `test_hyphenated_variant_after_version_is_masked`, 3 ca, `xfail(strict)`.

### SL-T034-2 · Thấp · Lưới an toàn không quay về cách cũ khi thư viện không còn module `_client`

- **Cách tái hiện:** `sys.modules["openai._client"] = None`, tức là gói `openai` vẫn cài nhưng không nhập được `openai._client`. Sau đó vào `ignoring_custom_headers()`.
- **Mong đợi:** theo yêu cầu của Chỉ Huy, thư viện đổi cấu trúc thì quay về cách cũ: gỡ biến tạm thời, vì không biết bản mới đọc biến ở đâu.
- **Thực tế:** `seo_app/ai/base.py`, nhánh `except ImportError: continue`, bỏ qua module đó. Không gỡ biến, nên `OPENAI_CUSTOM_HEADERS` vẫn nằm trong `os.environ`, chỗ đọc mới của thư viện sẽ thấy.
- **Mức độ:** Thấp. Bản thư viện hiện tại không bị. Nếu nâng thư viện mà dời chỗ đọc biến, các test sau sẽ đỏ trước khi tới tay người dùng:
  - `test_only_client_modules_read_ignored_env` (mới)
  - `test_libraries_would_add_custom_headers_without_fix`
  - các test header từ đầu tới cuối
- **Hướng sửa gợi ý:** khi `import_module(module_name)` báo `ImportError`:
  - Gói gốc (`anthropic` / `openai`) **nhập được**: đặt `fallback = True`.
  - Gói gốc **không cài**: mới `continue`.
- **Test:** `test_library_without_client_module_falls_back`, 2 ca, `xfail(strict)`.

## Ghi nhận khác (không phải lỗi của phiếu)

- **`br` không được giải nén.** `uv.lock` không có `brotli`, nên httpx để nguyên byte của nội dung `br` chứ không giải nén. Vì vậy `br` "hỏng" không phải lỗi giải nén. Ở trường hợp này, OpenAI với kiểu SSE hoặc text ra câu cố định "AI trả về dữ liệu không đúng khuôn". Câu vẫn cố định, không chép chữ máy chủ, nút Kiểm tra khóa vẫn ra "dữ liệu lạ". Test `test_br_without_decoder_gives_fixed_message` khóa hành vi này.
- **Thử lại khi lỗi giải nén.** Thư viện thử lại cả khi gặp lỗi giải nén. Câu báo luôn theo lần thử cuối: nén hỏng rồi mất mạng ra "Không kết nối được", mất mạng rồi nén hỏng ra "dữ liệu lạ". Đúng như mong đợi (`test_retry_mix_reports_last_error`).
- **Che nhầm số sau tên hãng.** Đúng như Thợ Máy đã nêu, số đứng **ngay sau** tên hãng cũng bị che, ví dụ "dùng GPT 5 lần" ra "dùng «đã ẩn tên mô hình» lần". Bài về cửa sắt hầu như không gặp. Số đứng riêng, số khác dòng, "5.5mm" dính chữ đều giữ nguyên.
- **Tốc độ che.** Chuỗi xấu dài 40.000–80.000 ký tự che xong dưới 0,2 giây. Không có biểu thức chính quy chạy quá lâu.

## Bằng chứng

```
$ uv run ruff check .
All checks passed!

$ uv run pytest -q
3565 passed, 4 skipped, 12 xfailed, 1 warning in 141.99s
# = 3383 + 182 test mới; 12 xfailed = 7 có sẵn + 5 của SL-T034-1/2

$ uv run pytest -q tests/test_soi_loi_t034.py
182 passed, 5 xfailed

# tests/test_soi_loi_t028.py chạy riêng, máy rảnh (4 nhân)
rảnh: pass=30 fail=0

# test_soi_loi_t028.py + test_soi_loi_t034.py, trong lúc 3 vòng pytest khác chạy song song
# (load average 4.5 trên 4 nhân)
bận: pass=30 fail=0   (mỗi lần: 302 passed, 7 xfailed)
```

## Đối chiếu tiêu chí

- [x] SL-T019-5: header lạ không tới client ở 4 chỗ, kể cả song song; luồng khác dùng `os` của thư viện vẫn đúng; ngoại lệ, gọi lồng đều ổn; 60/60 lần chạy T-028 qua
- [ ] Thư viện đổi cấu trúc: đạt khi thiếu/đổi `os`; **chưa đạt** khi thiếu hẳn `_client` (SL-T034-2)
- [x] 4 test đổi dòng kiểm: không nới lỏng mục tiêu (xem 1f)
- [ ] SL-T019-3: đạt, riêng biến thể có gạch nối còn lộ (SL-T034-1)
- [x] SL-T019-4, LC-T028-3, LC-T019-1, LC-T019-2: đạt
- [x] Câu lỗi cố định, không chép chữ máy chủ, không lộ khóa
- [x] Test không gọi mạng; `pytest` và `ruff` sạch

## Đề xuất

- **SL-T034-2:** nên sửa ngay trong T-034, khoảng 3 dòng, trước khi Lá Chắn kiểm, vì đây là đúng điều kiện an toàn Chỉ Huy đã nêu.
- **SL-T034-1:** sửa trong T-034 nếu Thợ Máy còn lượt, không thì ghi sổ.
- **Cho Lá Chắn:** soi kỹ `_OsWithoutIgnored`. Trong lúc đang trỏ tạm, `environ` là khung nhìn **chỉ đọc**: nếu code của 2 module `_client` ghi vào `os.environ` thì sẽ gặp `TypeError`. Bản thư viện hiện tại không ghi, đã kiểm bằng cách đọc mã nguồn.

## Câu hỏi cho chủ dự án

Không có.

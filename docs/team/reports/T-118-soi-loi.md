# Báo cáo T-118 · Dọn lỗi Thấp sau rà soát Fable · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-118 «Dọn lỗi Thấp sau rà soát Fable» (bản Chỉ Huy B gửi, chưa commit lên `main`) · mức kiểm **rút gọn**, Windows · yêu cầu bảo mật U2, U3, F3. Không gọi AI thật, không đụng website, không chạy cloud |
| Ngày nộp | 2026-11-02 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15, Streamlit 1.65.0, Chrome trong khung trình duyệt của app. Máy đang chạy toàn bộ test trên `main` |
| Mã nguồn | `team/T-118` tại `1e70f3f` (mã + test `bb3f51f`, gốc `main` `935d381`). Gộp thử với `main` cục bộ `b953e5e` (đã có T-117, biên bản T-116) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới, có từ trước** (SL-T118-1: tên mô hình dạng `<https:ten-mien/…>` vẫn thành link mở được trong `st.error`, do bộ làm sạch chung `escape_link_syntax` T-031; không chặn Lá Chắn). Cả 4 nhóm sửa đúng, không nới gì: trang lỗi bất ngờ đã kiểm trên Streamlit thật với 4 kiểu lỗi, không còn đường dẫn hay traceback. R5 đúng phạm vi duyệt. Không lùi T-034, T-090, T-104, T-105, T-109, T-113. Thử đột biến: test bắt đủ 10/10. Gộp `main` `b953e5e` sạch. `.claude/launch.json` đã trả về bản gốc |

## Tóm tắt (cho chủ dự án)

- **Lỗi bất ngờ trên trang không còn lộ đường dẫn.** Đã mở trang thật, thử 4 kiểu lỗi: khi tải trang, khi bấm nút, lỗi cú pháp có tên file, lỗi trong một phần trang. Trang chỉ hiện loại lỗi (ví dụ «ValueError») và một câu chung tiếng Anh của Streamlit; đường dẫn không có cả trong mã trang. Chi tiết đầy đủ vẫn in ở cửa sổ đen đang chạy app, để người hỗ trợ xem.
- Các sửa khác đúng ý, không nới chỗ nào:
  - câu báo khi file `.env` bị chương trình khác sửa đúng lúc lưu;
  - bản lưu tạm kế hoạch, danh sách bài có giờ tải bị sửa tay thì coi như cũ, không làm hỏng trang;
  - che biến môi trường dạng byte;
  - trả lại `os` khi nạp thư viện lỗi.
- **Một lỗi nhỏ mới (Thấp, có từ trước), SL-T118-1:** tên mô hình viết kiểu `<https:ten-mien/…>` (có dấu ngoặc nhọn) vẫn thành link bấm được trong câu báo lỗi. Bộ làm sạch chung chỉ chặn được các dạng khác. Bộ này cũng dùng cho chữ AI hiện trên trang. Không chặn phiếu.

## Việc 1 · `showErrorDetails = "type"` — **đạt**, kiểm trên trang Streamlit thật

- Đọc mã Streamlit 1.65 (`elements/exception.py`): với lỗi chưa bắt (`apply_show_error_details=True`), giá trị `"type"` làm **máy chủ** thay câu lỗi bằng câu chung và không dựng traceback. Chi tiết **không** được gửi xuống trình duyệt, không chỉ bị ẩn trên giao diện.
- Không có `~/.streamlit/config.toml` trên máy, nên cấu hình của dự án là cấu hình duy nhất có hiệu lực.
- App không tự gọi `st.exception` ở đâu (`git grep` trong `app/`, `seo_app/`). Đây là đường duy nhất không áp `showErrorDetails`.
- **Thử thật** (`sl118_crash.py`):
  - Chạy `uv --directory wt-T-118 run streamlit run …` ở cổng trống 8799, thư mục làm việc là nhánh, nên đọc đúng `.streamlit/config.toml` của nhánh. Đã thêm tạm một mục vào `.claude/launch.json` rồi trả về **đúng bản gốc** (băm SHA-256 trùng).
  - Lỗi mang đường dẫn `C:\Users\ADMIN\bi-mat-sl118\du-an\khoa.json`.

| Kiểu lỗi | Trang hiện | Đường dẫn trong mã trang |
|---|---|---|
| Lỗi khi tải trang (`ValueError`) | «ValueError: This app has encountered an error. The original error message is redacted…» | không |
| Lỗi trong hàm gọi lại của nút (`on_click`) | như trên | không |
| `SyntaxError` có tên file là đường dẫn | «SyntaxError: This app has encountered an error…» | không |
| Lỗi trong `@st.fragment` | «ValueError: …redacted…» | không |

  Nút «Ask Google», «Ask ChatGPT» trong hộp lỗi chỉ mang câu đã che (loại lỗi + câu chung), đã kiểm `href`. Nhật ký máy chủ (cửa sổ chạy app) vẫn có traceback đầy đủ, đúng như chú thích trong `config.toml`.
- Test của Thợ Máy (`AppTest`, `set_option`) cùng kết quả, kèm đối chứng `"full"` lộ đường dẫn.

## Việc 2 · LC-T034-1, -2, -3 — **đạt**, kèm SL-T118-1

**LC-T034-1:**
- Cả 7 chỗ chèn tên mô hình vào câu báo đều qua `model_label`: Anthropic 403/404, OpenAI 403/404, Gemini 403/404, câu lỗi 400 chung.
- `git grep` không còn chỗ nào chèn `task.model` thô vào câu báo. Trang Thử mù (Cài đặt) đã tự làm sạch câu lỗi từ T-044. Bảng kết quả Thử mù dùng `st.dataframe`, dòng TOML dùng `st.code`, nên không thành link.
- Thử thật trên `st.error` (`sl118_links.py`, cổng 8798, `launch.json` trả lại bản gốc), với đối chứng là câu chưa làm sạch:

| Tên mô hình | Chưa làm sạch | Qua `model_label` |
|---|---|---|
| `https://evil.example/x`, `http://x.y/…`, `www.evil.example`, `ban@evil.example`, `[bấm](https://evil.example)` | thành link | **không** thành link |
| `mailto:ban@evil.example`, `ftp://evil.example/f` (không ngoặc) | không / không | không |
| **`<https:evil.example/khong-gach>`** | link | **vẫn là link, trình duyệt mở `https://evil.example/khong-gach`** → SL-T118-1 |
| `<https://…>`, `<HTTPS://…>`, `<ftp://…>`, `<http:\\…>` | link | vẫn là thẻ link, nhưng địa chỉ hỏng (ký tự rộng 0), `new URL()` báo không hợp lệ |
| `<mailto:ban@evil.example>` | link | vẫn là link `mailto:` (địa chỉ có ký tự rộng 0) |
| `<ban@evil.example>` | link | không |

**LC-T034-2:** `environb`, `getenvb` đi qua lớp lọc. Trên Windows, `os` thật không có hai tên này nên `_OsWithoutIgnored` cũng báo `AttributeError` như thật. Test của Thợ Máy giả lập phía Mac/Linux.

**LC-T034-3:** đã đọc cả hàm `ignoring_custom_headers`. Vòng trỏ `os` và bước gỡ biến nằm trong `try`; `finally` trả `os.environ` và từng module đã trỏ. Nạp module thứ hai lỗi thì module thứ nhất vẫn được trả lại (test Thợ Máy).

## Việc 3 · SL-T105-1 — **đạt**

- `_write_value`: đọc lại được mà parse khác, **và** chữ trên ổ khác chữ vừa ghi, thì ném `EnvFileChangedError` (câu «đã khác bản vừa ghi… đã được trả về bản trước khi lưu»). Chỉ khi chữ giống hệt mới còn «định dạng lạ».
- Phép so chữ đáng tin, vì `_read_env_text` và `_atomic_write` đều mở với `newline=""` và giữ BOM, nên không có chênh do kiểu xuống dòng.
- Câu «đã được trả về bản trước khi lưu» chỉ đến sau khi bỏ bản vừa ghi đã **thành công** (nhánh không trả được đi trước, câu riêng). Vì vậy câu đúng sự thật.
- `set_password` có câu riêng `MSG_ENV_CHANGED`.
- 2 test Soi Lỗi T-105 (`tests/test_soi_loi_t105.py`) nay qua.

## Việc 4 · LC-T113-2 — **đạt**

- `_parse_time` của `plan_cache` và `site_index`: `astimezone` tràn thì thành `_Corrupt`, tức coi như cache hỏng hay cũ, không lỗi trang. Đã thử: `9999-12-31T17:00:00+00:00`, `9999-12-31T23:59:59-05:00`, `0001-01-01T00:00:00+05:00`, `0001-01-01T06:59:59+07:00` đều ném `OverflowError` và bị bắt.
- Nhánh `ValueError` thêm vào chỉ để phòng xa: tôi không tìm được giá trị nào làm `astimezone` ném `ValueError`.
- Giờ tải **ở tương lai** (không tràn) đã bị coi là cũ từ trước, nhờ ngưỡng `_CLOCK_SKEW` 5 phút. Không có ca «cache mới mãi».
- Các ca LC-T113-2 trong `tests/test_la_chan_t113.py` (kho và trang) nay qua.

## Việc 5 · R5, U2/U3/F3 — **đạt**

| File test | Thay đổi | Trong phạm vi duyệt |
|---|---|---|
| `test_env_file.py::test_mismatch_after_write_restores_old_file` | `match="định dạng lạ"` thành `EnvFileChangedError, match="khác bản vừa ghi"`; phần kiểm file trả bản cũ, số lần ghi giữ nguyên | có (Chỉ Huy duyệt 02/11 17:55) |
| `test_t105_set_password.py::test_readback_mismatch_…` | đổi tên, câu mong đợi `MSG_ENV_FORMAT` thành `MSG_ENV_CHANGED`; các phần kiểm khác giữ nguyên | có (test T-105 tương ứng) |
| `test_soi_loi_t105.py` | chỉ gỡ 2 dấu `xfail(strict=True)` của SL-T105-1, thân test giữ nguyên | có (sửa xong thì gỡ dấu) |
| `test_la_chan_t113.py` | gỡ dấu `xfail` LC-T113-2 khỏi các tham số, thân test giữ nguyên | có |

Không test cũ nào khác bị đổi.
- U2: câu báo không đường dẫn; trang lỗi bất ngờ đã che, như Việc 1.
- U3: không đụng đăng nhập.
- F3: ghi `.env` vẫn qua bộ ghi nguyên tử UTF-8.

## Việc 6 · Không lùi; gộp thử

- Test chọn lọc trên nhánh, 32 file: `test_t118_don_thap`, `test_ai`, `test_ai_t026`, `test_ai_t028`, `test_ai_t034`, `test_soi_loi_t026`, `test_soi_loi_t028`, `test_soi_loi_t034`, `test_ai_openai_gemini`, `test_ai_openai_gemini_soi_loi`, `test_settings_blind`, `test_soi_loi_t044`, `test_app_t044_safe_text`, `test_env_file`, `test_hash_password_script`, `test_config`, `test_la_chan_t090`, `test_soi_loi_t090`, `test_t090_env_bang_ma`, `test_soi_loi_t104`, `test_t104_set_password`, `test_soi_loi_t105`, `test_t105_set_password`, `test_plan_cache`, `test_site_index`, `test_site_index_t042`, `test_t041_site_index`, `test_t109_website_status`, `test_soi_loi_t109`, `test_la_chan_t113`, `test_soi_loi_t113`, `test_t113_website_status`.
  - Kết quả: **2077 qua, 6 bỏ qua, 4 xfail có từ trước, 0 hỏng, không XPASS** (4 phút).
  - **T-034, T-090, T-104, T-105, T-109, T-113 không lùi.**
  - Test Soi Lỗi mới `tests/test_soi_loi_t118.py`: 1 qua, 6 xfail. `ruff check`, `ruff format --check`: sạch.
- Gộp thử với `main` cục bộ `b953e5e`: `git merge-tree` **không xung đột** (cây `308792f`).
  - Từ `935d381`, `main` chỉ thêm T-117 (`data_dir.py`, `process.py`, `image_tags.py`) và biên bản T-116, không trùng file với T-118.
  - Riêng `tests/test_soi_loi_t117.py` (SL-T117-1) có `xfail` nhắm vào `plan_cache`, `site_index`, hai file T-118 có sửa. Vì vậy đã gộp thật ở worktree tạm (commit treo `59c8a10`, không đẩy; `seo_app` nạp từ chính worktree tạm) rồi chạy 9 file: `test_soi_loi_t117`, `test_t117_data_dir_links`, `test_plan_cache`, `test_site_index`, `test_la_chan_t113`, `test_t118_don_thap`, `test_env_file`, `test_soi_loi_t105`, `test_t105_set_password`.
  - Kết quả: **349 qua, 6 bỏ qua, 3 xfail (SL-T117-1, vẫn đúng dấu), 0 hỏng, không XPASS**.
  - Worktree tạm đã gỡ.

## Thử đột biến (`sl118_mutate.py`)

Mỗi đột biến chạy trên một bản sao `git archive` riêng (kể cả `.streamlit/`), với 7 file: `test_t118_don_thap`, `test_env_file`, `test_t105_set_password`, `test_soi_loi_t105`, `test_la_chan_t113`, `test_ai_t034`, `test_soi_loi_t034`. Đối chứng không đổi: 492 qua, 5 bỏ qua.

| Đột biến | Test hỏng |
|---|---|
| T1 `showErrorDetails = "full"` | 2 |
| T2 `model_label` không làm sạch | 42 |
| T3 riêng câu Gemini 404 dùng tên thô | 6 |
| T4 `environb` không lọc | 1 |
| T5 `getenvb` không lọc | 1 |
| T6 `environb`/`getenvb` không «giống `os` thật» (Windows trả đồ giả thay vì `AttributeError`) | 4, gồm 2 test T-034 |
| T7 bỏ phép so chữ (SL-T105-1 về câu «định dạng») | 6 |
| T8 `set_password` bỏ nhánh `EnvFileChangedError` | 2 |
| T9 `plan_cache` bỏ bắt tràn giờ | 5, gồm 2 ca trang |
| T10 `site_index` bỏ bắt tràn giờ | 4, gồm 1 ca trang |

Kết luận: test bắt được mọi đột biến làm đổi hành vi. LC-T034-3 (dời vòng vào `try`) có test riêng của Thợ Máy (`test_patched_module_restored_when_second_module_fails`), không đột biến lại.

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T118-1** | Thấp (có từ trước ở bộ làm sạch chung `escape_link_syntax`, T-031; còn sót của LC-T034-1) | Markdown coi `<scheme:…>` là link tự động. `model_label` (gọi `escape_link_syntax`) chỉ chèn ký tự rộng 0 vào `://` và `@`, không gỡ dấu `<`. Vì vậy `<https:evil.example/x>` (không có `//`) qua nguyên vẹn, và trên trang Streamlit thật trình duyệt mở thành `https://evil.example/x`. Các dạng `<https://…>`, `<HTTPS://…>`, `<ftp://…>`, `<mailto:…>`, `<http:\\…>` vẫn hiện thành thẻ link (địa chỉ hỏng, riêng `mailto:` mở trình gửi thư). Trái lời hứa «không bao giờ thành link» của `model_label`. Nguồn tên: người dùng gõ ở Thử mù, hay `config/ai.toml`. Bộ làm sạch này cũng dùng cho chữ AI hiện trên trang (T-031), nên chữ AI có `<https:…>` cũng thành link ở trang xem. Bài gửi WordPress đi qua bộ dựng T-096 có phép kiểm link riêng, không kiểm ở phiếu này | `tests/test_soi_loi_t118.py::test_sl_t118_1_angle_bracket_model_never_becomes_a_link` (6 ca, `xfail(strict=True)`; `--runxfail`: hỏng đúng 6 dạng). Đối chứng mẫu dò `test_autolink_pattern_matches_markdown` (qua) |

Gợi ý sửa: trong `escape_link_syntax`, đổi `<` thành `\<` (hay `&lt;`) khi ngay sau là `chữ{2,32}:` hoặc dạng email, rồi thêm các dạng trên vào test của T-031 và T-118. Không chặn Lá Chắn với T-118.

## Ghi nhận

- **GN-1:** câu chung của trang lỗi bất ngờ là tiếng Anh (của Streamlit), kèm nút «Ask Google/ChatGPT» (chỉ mang câu đã che). Đúng lựa chọn `"type"` của chủ dự án.
- **GN-2:** nhánh `except ValueError` trong `_parse_time` không có ca thật nào chạy tới: mọi giờ tràn tôi thử đều ném `OverflowError`. Nhánh này chỉ để phòng xa, vô hại.

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t118.py`: 6 `xfail(strict=True)` SL-T118-1, 1 đối chứng mẫu dò. Chạy: `uv run pytest tests/test_soi_loi_t118.py -rxX`.
- Script (thư mục ghi chú chung, `T-118-soi-loi-scripts/`):
  - `sl118_crash.py`: trang lỗi bất ngờ, 4 kiểu, chọn bằng `?kieu=trang|nut|cuphap|fragment`;
  - `sl118_links.py`: tên mô hình trong `st.error`, có đối chứng;
  - `sl118_mutate.py`: thử đột biến.

  Hai trang thử chạy bằng `uv --directory <worktree> run streamlit run <script> --server.port <cổng trống>`.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện.

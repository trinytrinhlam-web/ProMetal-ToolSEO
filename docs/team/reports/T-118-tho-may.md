# Báo cáo T-118 · Dọn lỗi Thấp sau rà soát Fable: ẩn chi tiết lỗi trên trang, LC-T034-1..3, SL-T105-1, LC-T113-2

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-118](../tickets/T-118-don-thap-sau-fable.md) |
| Nhánh | `team/T-118`, từ `main` `935d381` (đã có T-105, T-113); commit mã và test `bb3f51f`, lượt 2 `3339360`; lượt 3: gộp `main` `29499dd`, sửa một test cũ (commit cùng mục «Lượt 3» này) |
| Ngày nộp | 2026-11-02 (giờ máy, +07); lượt 2: 2026-11-03; lượt 3: 2026-11-03 22:38 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- **Lỗi bất ngờ trên trang chỉ hiện loại lỗi**, đúng lựa chọn ngày 02/11. Trang không còn hiện câu lỗi gốc, các dòng mã hay đường dẫn thư mục trên máy, chỉ còn tên loại lỗi và một câu chung (tiếng Anh, do Streamlit viết sẵn). Chi tiết vẫn in ở cửa sổ đen đang chạy app. Các câu báo tiếng Việt mà phần mềm tự bắt được không đổi.
- **Tên mô hình AI trong câu báo không thành link bấm được**, kể cả khi ghi dạng địa chỉ web, email hay đặt trong ngoặc nhọn `<…>` (dạng cuối sửa ở lượt 2).
- **Công cụ đặt mật khẩu và trang Cài đặt:** khi file `.env` vừa lưu đọc lại đã khác bản vừa ghi (thường do chương trình khác ghi vào đúng lúc đó, hoặc ổ đĩa ghi không trọn), câu báo nói đúng như vậy, không còn bảo đi tìm một dòng sai định dạng không có. File vẫn được trả về bản cũ như trước.
- **Trang Bài viết, trang Kế hoạch không còn lỗi** khi giờ tải trong file cache trên máy bị sửa tay thành giờ lạ. Cache đó bị bỏ, phần mềm đọc lại từ Google Sheets, website như lần đầu.
- Hai chỗ nhỏ bên trong lớp AI cũng đã sửa (che thêm biến môi trường dạng byte; trả lại đúng khi gói thư viện hỏng). Người dùng không thấy gì khác.
- Lượt 3: sửa một bài kiểm tra cũ vẫn chờ câu lỗi gốc hiện trên trang. Nay nó kiểm điều ngược lại: câu lỗi gốc **không** hiện. Phần mềm không đổi gì.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `.streamlit/config.toml` | `[client] showErrorDetails = "type"`, kèm chú thích tiếng Việt (chủ dự án chọn 02/11; Lá Chắn T-001 #8, T-116 nhóm 3) |
| `seo_app/ai/base.py` | **LC-T034-1:** hàm `model_label(model)` = `escape_link_syntax(model)`: tên mô hình chèn vào câu báo không thành link. Tên thật của 3 hãng đi qua không đổi; chạy lại không đổi gì. Dùng ở câu lỗi 400 (`bad_request_error`). Lượt 2 thêm bước đổi `<` thành `&lt;` (SL-T118-1, mục Lượt 2). **LC-T034-2:** `_EnvironbWithoutIgnored`; `_OsWithoutIgnored.__getattr__` trả bản đã lọc cho `environb`, `getenvb` khi `os` thật có hai tên này, còn nếu không có (Windows) thì lỗi y như `os` thật. **LC-T034-3:** trong `ignoring_custom_headers`, vòng trỏ `module.os` và bước gỡ biến dời vào trong `try/finally`; bước gỡ biến lưu từng biến ngay khi gỡ |
| `seo_app/ai/anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py` | 6 câu «không được dùng mô hình «…»», «Không có mô hình «…»» dùng `model_label(task.model)` (LC-T034-1) |
| `seo_app/env_file.py` | **SL-T105-1:** lớp lỗi `EnvFileChangedError` và câu chung `_CHANGED_RESTORED`. Trong `_write_value`, sau khi bỏ bản vừa ghi: chữ đọc lại **khác** chữ vừa ghi thì ném `EnvFileChangedError` (câu: «đã khác bản vừa ghi (thường do chương trình khác ghi vào đúng lúc đó …, hoặc ổ đĩa ghi không trọn)…; đã trả về bản trước khi lưu»); chữ giống mà đọc ra khác (không thể xảy ra vì nội dung đã kiểm trước khi ghi) vẫn là `EnvFileFormatError`, để phòng xa. Theo gợi ý của Soi Lỗi T-105 |
| `scripts/hash_password.py` | Câu `MSG_ENV_CHANGED` cho `EnvFileChangedError` (SL-T105-1) |
| `seo_app/storage/plan_cache.py`, `seo_app/storage/site_index.py` | **LC-T113-2:** `_parse_time` bắt `OverflowError`/`ValueError` khi đổi giờ tải sang múi giờ app (năm 10000, năm 0) → `_Corrupt`, nên `load()` trả `None` như hợp đồng LC-T094-29 |
| `tests/test_t118_don_thap.py` | **Mới**, 13 hàm test, 98 ca (1 ca chỉ chạy trên Mac/Linux): lỗi bất ngờ trên trang (`AppTest`, kèm ca đối chứng `"full"`); tên mô hình xấu ở 7 câu báo × 6 dạng; tên thật không đổi; `model_label` chạy lại không đổi; `environb`/`getenvb` (giả lập Mac/Linux, khớp `os` thật trên Windows); lỗi lạ khi nạp module; 2 ca SL-T105-1 so đúng nguyên câu. Lượt 2 thêm 2 hàm, 43 ca (nay 15 hàm, 141 ca) |
| `tests/test_la_chan_t113.py` | Gỡ dấu `xfail` LC-T113-2: bỏ định nghĩa `LC_T113_2` và 2 chỗ gắn `marks=` (9 ca). Dữ liệu thử và thân test giữ nguyên (R5) |
| `tests/test_soi_loi_t105.py` | Gỡ 2 dấu `xfail(strict=True)` SL-T105-1 (chỉ xóa dấu, R5) |
| `tests/test_env_file.py`, `tests/test_t105_set_password.py` | Đổi câu mong đợi của 2 test cũ theo SL-T105-1 (Chỉ Huy duyệt 02/11 17:55; bảng cũ → mới ngay dưới) |
| `docs/team/reports/T-118-tho-may.md` | Báo cáo này |

**Test cũ đổi theo SL-T105-1 (R5, Chỉ Huy duyệt 02/11 17:55).** Hai test này giả «đĩa ghi sai» trên đúng đường «đọc lại được mà khác chữ vừa ghi» mà SL-T105-1 sửa. Bộ ghi không phân biệt được «đĩa ghi sai» với «chương trình khác ghi vào» (cùng một trạng thái trên ổ), nên câu mới không khẳng định chắc nguyên nhân: «thường do chương trình khác ghi vào đúng lúc đó …, hoặc ổ đĩa ghi không trọn».

| Test | Trước | Sau | Giữ nguyên |
|---|---|---|---|
| `tests/test_env_file.py::test_mismatch_after_write_restores_old_file` | `pytest.raises(EnvFileError, match="định dạng lạ")` | `pytest.raises(EnvFileChangedError, match="khác bản vừa ghi")`; nhập thêm `EnvFileChangedError`; chú thích ghi lý do và ngày duyệt | File trả bản cũ từng byte (`read(env_path) == original`); đúng 2 lần ghi (`len(calls) == 2`) |
| `tests/test_t105_set_password.py::test_readback_mismatch_still_reported_as_format` → **đổi tên** `test_readback_mismatch_reported_as_changed` | Đòi `f"Chưa lưu mật khẩu mới. {script.MSG_ENV_FORMAT}"` | Đòi `f"Chưa lưu mật khẩu mới. {script.MSG_ENV_CHANGED}"`; docstring của hàm và một câu trong docstring đầu file nói lại cho đúng | Mã thoát 1; `.env` trả bản cũ từng byte |

Không đụng `app/**`, cách băm, so mật khẩu (`seo_app/auth.py`), `seo_app/content/blind_test.py`.

**Hai chỗ lệch với phạm vi ghi trong phiếu:**
- **LC-T113-2** sửa ở `seo_app/storage/plan_cache.py` và `seo_app/storage/site_index.py`, không phải `seo_app/plan/**`. Hai kho cache này nằm ở `storage`, và 9 ca `xfail` của Lá Chắn đòi sửa cả hai.
- **LC-T034-1** không sửa `seo_app/content/blind_test.py`. Câu lỗi của thử mù (tên do người dùng gõ) đã được chặn link ngay ở chỗ hiện từ T-044: `escape_link_syntax` ở `app/views/settings.py:308`, `:400`, `:414`, có test `test_app_t044_safe_text.py`. Chỗ còn hở là các câu `AIError` mang tên mô hình từ `config/ai.toml`: bộ đọc cấu hình nhận mọi tên không rỗng (`registry.py:105`), và các trang khác (`write.py`, `plan.py`, `settings.py:208`, `:390`) hiện lỗi đó mà không chặn link. Vì thế phần sửa nằm ở chỗ dựng câu, trong lớp AI.

```
$ git diff --stat 935d381..bb3f51f
 .streamlit/config.toml           |   4 +
 scripts/hash_password.py         |  12 ++
 seo_app/ai/anthropic_provider.py |   8 +-
 seo_app/ai/base.py               | 100 ++++++++++----
 seo_app/ai/gemini_provider.py    |   7 +-
 seo_app/ai/openai_provider.py    |   8 +-
 seo_app/env_file.py              |  21 +++
 seo_app/storage/plan_cache.py    |   7 +-
 seo_app/storage/site_index.py    |   7 +-
 tests/test_env_file.py           |   6 +-
 tests/test_la_chan_t113.py       |   8 +-
 tests/test_soi_loi_t105.py       |  15 ---
 tests/test_t105_set_password.py  |  12 +-
 tests/test_t118_don_thap.py      | 276 +++++++++++++++++++++++++++++++++++++++
 14 files changed, 428 insertions(+), 63 deletions(-)
```

Cộng thêm báo cáo này (commit sau). Gộp thử (`git merge-tree --write-tree`) không xung đột với cả hai: `origin/main` `7485b94` và `main` cục bộ `b953e5e` (đã gộp T-117 và các biên bản T-116). Hai bản đó không đổi file nào của phiếu kể từ `935d381`.

## Bằng chứng

```
# 1. Gốc 935d381, trước khi sửa: 11 ca xfail đúng như biên bản
$ uv run pytest tests/test_la_chan_t113.py tests/test_soi_loi_t105.py -q -rxX
11 passed, 11 xfailed in 57.09s     (9 LC-T113-2: load() của plan_cache, site_index, trang Bài viết,
                                     trang Kế hoạch; 2 SL-T105-1)

# 2. Đã sửa mã, dấu xfail còn nguyên: đều XPASS (strict nên báo hỏng, đúng mong đợi)
$ uv run pytest tests/test_la_chan_t113.py -q -rxX
[XPASS(strict)] LC-T113-2: … (×9)
$ uv run pytest tests/test_soi_loi_t105.py … -q -rxX
[XPASS(strict)] SL-T105-1: … (×2)

# 3. Đối chứng: file test mới chạy trên mã CŨ 935d381 (worktree tạm ở thư mục nháp, đã gỡ;
#    bản sao test chỉ bỏ dòng nhập model_label vì mã cũ chưa có hàm này)
58 failed, 37 passed, 1 skipped
   hỏng đúng chỗ: cấu hình showErrorDetails (1), lỗi bất ngờ trên trang (1), tên mô hình thành
   link (42 = 6 dạng × 7 câu), environb giả lập (1), lỗi lạ khi nạp module (1); 11 ca model_label
   (mã cũ chưa có); ca canh «đường thường» cũng hỏng vì lỗi LC-T034-3 của ca trước để
   anthropic._client.os kẹt ở khung lọc (đúng hậu quả của lỗi). Qua: 35 ca tên thật, đối chứng
   "full", ca khớp os thật

# 4. Chạy thật AppTest (script thử ở thư mục nháp): trang ném RuntimeError có đường dẫn
showErrorDetails = "type": message = câu chung «This app has encountered an error. The original
   error message is redacted…», stack_trace = [], type = "RuntimeError"
showErrorDetails = "full": message = câu gốc có đường dẫn, stack_trace có «File "C:\…"»

# 5. Bản cuối (đúng commit bb3f51f; mã băm gộp 14 file đổi 2cd91157… giống nhau lúc đầu và lúc
#    cuối mọi nhóm, và lúc commit). 47 file test liên quan, chạy 4 nhóm nối nhau
nhóm A (13 file: test mới, LC-T113-2, SL-T105-1, bộ ghi .env, T-104, T-105, cache)
   631 passed, 6 skipped in 204.02s
nhóm B (13 file: lớp AI, thử mù)            1744 passed, 4 xfailed, 1 warning in 184.18s
nhóm C (10 file: T-090, Cài đặt, cấu hình)   554 passed, 6 skipped in 108.43s
nhóm D (11 file: mọi trang app, trang Kế hoạch, T-101, T-109, T-113)
   478 passed in 242.92s
tổng: 3407 passed, 12 skipped, 4 xfailed, 0 hỏng

$ uv run ruff check .                        # ruff 0.16.10
All checks passed!

# 6. Quét bí mật, PYTHONUTF8=1, 12 file đổi
$ PYTHONUTF8=1 uvx detect-secrets scan …
seo_app/ai/base.py:30  Basic Auth Credentials   (có từ trước: bản main báo ở dòng 28, dời 2 dòng
                                                 vì thêm dòng nhập)
seo_app/env_file.py:58  Secret Keyword          (có từ trước: tên hằng PASSWORD_HASH_VAR)
```

- **12 mục bỏ qua** đều do Windows:
  - `test_t118_don_thap.py:192` (`environb` thật, chỉ có trên Mac/Linux);
  - `test_env_file.py:292` (quyền `600`), `:594` ×2, `:615` (symlink);
  - `test_site_index.py:321` (symlink);
  - `test_soi_loi_t016_t020.py:232` ×2, `:260`, `:273` ×2 (symlink), `:333` (quyền POSIX).
- **4 `xfail`** đều đã biết, có từ trước: SL-T026-3 ×2, SL-T028-1 ×2. Cảnh báo duy nhất là cảnh báo Pydantic có từ trước của `test_soi_loi_t028.py`.
- Lần chạy đầu của bước 5 (một lượt 47 file liền) bị ngắt cùng phiên lúc máy tải nặng, nên tôi chạy lại theo 4 nhóm trên cùng bản mã.

**47 file test liên quan:**

| Nhóm | File |
|---|---|
| A | `test_t118_don_thap.py`, `test_la_chan_t113.py`, `test_soi_loi_t105.py`, `test_env_file.py`, `test_t105_set_password.py`, `test_soi_loi_t104.py`, `test_t104_set_password.py`, `test_hash_password_script.py`, `test_plan_cache.py`, `test_site_index.py`, `test_site_index_t042.py`, `test_soi_loi_t037.py`, `test_soi_loi_t042_paging_cache.py` |
| B | `test_ai.py`, `test_ai_images.py`, `test_ai_openai_gemini.py`, `test_ai_openai_gemini_soi_loi.py`, `test_ai_t026.py`, `test_ai_t028.py`, `test_ai_t034.py`, `test_soi_loi_t026.py`, `test_soi_loi_t028.py`, `test_soi_loi_t034.py`, `test_blind_test.py`, `test_soi_loi_t019.py`, `test_soi_loi_t019_luot2.py` |
| C | `test_t090_env_bang_ma.py`, `test_t090_meta_emoji_moi.py`, `test_soi_loi_t090.py`, `test_la_chan_t090.py`, `test_soi_loi_t016_t020.py`, `test_settings_keys.py`, `test_settings_blind.py`, `test_config.py`, `test_config_tolerance.py`, `test_app.py` |
| D | `test_app_pages.py`, `test_app_t044_safe_text.py`, `test_soi_loi_t044.py`, `test_t101_home_page.py`, `test_t101_plan_page.py`, `test_t101_settings_google.py`, `test_plan_sync.py`, `test_t109_website_status.py`, `test_soi_loi_t109.py`, `test_t113_website_status.py`, `test_soi_loi_t113.py` |

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `client.showErrorDetails = "type"` kèm chú thích tiếng Việt; `AppTest` chứng minh lỗi bất ngờ không còn câu gốc, traceback, đường dẫn (`test_unexpected_error_shows_type_only`, đối chứng `test_full_details_would_show_the_path`)
- [x] Yêu cầu 2: LC-T034-1 (`model_label` ở 7 câu báo; 42 ca tên xấu không thành link, 35 ca tên thật không đổi); LC-T034-2 (`environb`, `getenvb` qua lớp lọc; lỗi như `os` thật trên Windows); LC-T034-3 (vòng trỏ trong `try/finally`; ca lỗi lạ khi nạp module)
- [x] Yêu cầu 3: SL-T105-1, câu chung đúng sự thật «đã khác bản vừa ghi (thường do chương trình khác ghi vào …, hoặc ổ đĩa ghi không trọn)» cho cả `set_password` lẫn trang Cài đặt; 2 ca `xfail` của Soi Lỗi XPASS rồi gỡ dấu; 2 test cũ đổi câu mong đợi theo duyệt của Chỉ Huy (bảng cũ → mới ở trên)
- [x] Yêu cầu 4: LC-T113-2, giờ tải tràn trong cache thì cache coi như hỏng (`load()` → `None`), trang Bài viết, trang Kế hoạch không lỗi; 9 ca `xfail` XPASS rồi gỡ dấu
- [x] Yêu cầu 5: không lùi T-034, T-090, T-104, T-105, T-109, T-113 (các file test của các phiếu đó trong 47 file đều qua)
- [x] Test liên quan: 3407 passed, 0 hỏng; `uv run ruff check .` sạch; `detect-secrets` (`PYTHONUTF8=1`) không có mục mới
- [x] U2: trang không hiện đường dẫn, câu lỗi gốc khi có lỗi bất ngờ. U3: không đổi cách băm, so mật khẩu. F3: đọc, ghi `.env` vẫn qua bộ ghi UTF-8 nguyên tử cũ; không `eval`, `pickle`
- [x] Báo cáo nộp tại `docs/team/reports/T-118-tho-may.md`
- [x] Lượt 2 (SL-T118-1): tên mô hình dạng `<scheme:…>` không còn là link tự động ở mọi câu báo và cả 3 kiểu trang hiện; 6 ca `xfail` của Soi Lỗi XPASS rồi gỡ dấu; 21 file liên quan 2055 passed, 0 hỏng; `ruff` sạch
- [ ] Toàn bộ `uv run pytest` trên Windows: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Câu chung của Streamlit bằng tiếng Anh.** Với `"type"`, trang hiện «RuntimeError» kèm câu «This app has encountered an error. The original error message is redacted to prevent data leaks…». Cấu hình không đổi được câu này sang tiếng Việt. Đây chỉ là lỗi **chưa bắt**; mọi lỗi phần mềm tự bắt vẫn có câu tiếng Việt như cũ. Ngoài ra, `st.exception()` gọi tay thì không theo cấu hình này, nhưng `app/`, `seo_app/` không có chỗ nào gọi (`grep`).
- **`model_label` dùng `escape_link_syntax`**, chuẩn chung của dự án cho chữ hiện bằng Markdown (T-031, T-044). Tên có `<` từng chưa bị chặn: Soi Lỗi bắt được đúng chỗ này (SL-T118-1), nay đã sửa ở lượt 2 (mục dưới). Tên có `@` (kiểu Vertex AI) sẽ có thêm một ký tự rộng 0 trước `@` khi hiện trong câu báo; app gọi API trực tiếp, tên thật không có `@`.
- **SL-T105-1:** bộ ghi không phân biệt được «chương trình khác vừa sửa file» với «ổ ghi sai», vì cả hai để lại cùng một trạng thái trên ổ: chữ khác chữ vừa ghi. Câu mới tả đúng sự việc («đọc lại ngay sau khi lưu đã khác bản vừa ghi») và nêu cả hai nguyên nhân, không khẳng định chắc (điều kiện của Chỉ Huy khi duyệt). Bước trả bản cũ vẫn đè mất thay đổi của chương trình kia, nếu có (Quan sát 2 của Lá Chắn T-104, không đổi).
- **LC-T113-2:** phiếu nói «coi như cache cũ». Theo đúng ca `xfail` của Lá Chắn, cache có giờ tràn bị coi như hỏng: `load()` trả `None`, trang đọc lại từ Google Sheets, website như khi chưa có cache, lần ghi sau tạo lại cache bình thường.
- **LC-T034-2:** máy này là Windows, nơi `os` không có `environb`. Ca `environb` thật chỉ chạy trên Mac/Linux (bỏ qua ở đây); nhánh đó được phủ bằng ca giả lập `os` của Mac/Linux.

## Đề xuất

- **Họa Sĩ (tùy chọn, Thấp):** nếu chủ dự án muốn câu tiếng Việt cho cả lỗi **chưa bắt**, có thể bọc phần chạy trang trong `app/main.py` bằng một khối bắt lỗi chung, hiện câu tiếng Việt cố định; `showErrorDetails = "type"` vẫn giữ làm lớp dưới. Cấu hình của Streamlit không dịch được câu chung của nó.
- **Thợ Máy (tùy chọn, Thấp):** bộ đọc `config/ai.toml` (`registry.py:105`) có thể từ chối tên mô hình có dấu cách, `<`, `>`, `[`, `]`; tên thật của 3 hãng không có các ký tự này. Hiện chưa cần, vì `model_label` đã chặn link ở mọi câu báo.
- **Chỉ Huy:** T-116 nhóm 3 còn nêu các mục «ghi sổ» chưa ghi (T-016-020 #5, T-022-024 #3), ngoài phạm vi phiếu này.
- **Đề xuất 4 (lượt 2, Thấp, phiếu riêng):** cho bộ làm sạch chung `escape_link_syntax` (T-031) chặn cả link tự động ngoặc nhọn `<scheme:…>` (SL-T118-1 phần chữ AI). Phải giữ phép đảo `unescape_link_syntax`, và chạy test mọi nơi gọi (trang Soạn bài, dàn ý, gửi WordPress).

## Lượt 2 · SL-T118-1 (Soi Lỗi, 03/11)

| Mục | Nội dung |
|---|---|
| Lỗi | SL-T118-1 (Thấp, có từ trước ở bộ làm sạch chung `escape_link_syntax` của T-031): tên mô hình dạng `<https:evil.example/x>` (ngoặc nhọn, không có `//`) vẫn là link tự động của CommonMark. Soi Lỗi đã thử trên trang thật: trình duyệt mở `https://evil.example/x`. `model_label` lượt 1 (tức `escape_link_syntax`) không gỡ dấu `<` |
| Sửa | `seo_app/ai/base.py`: `model_label(model) = escape_link_syntax(model).replace("<", "&lt;")`. Markdown vẫn hiện `<` cho người đọc, nhưng không còn dấu `<` thật để mở link tự động `<scheme:…>` hay thẻ HTML. Các dạng khác (`https://`, `www.`, email, `[chữ](…)`) vẫn qua `escape_link_syntax` như lượt 1. Chạy lại không đổi gì; tên thật của 3 hãng không đổi |
| Vì sao không dùng `escape_markdown` | Nhiều trang đã escape **cả câu báo** bằng `escape_markdown`: trang Kế hoạch (`plain()` trong `show()`, `app/views/plan.py:195-202`) và trang Bài viết (`app/views/home.py:114`, `:132`, `:184`, `:190`). Hàm này không chạy lại an toàn: `escape_markdown(escape_markdown("claude-opus-5-5"))` = `claude\\\-opus\\\-5\\\-5`, tức trên trang hiện `claude\-opus\-5\-5`. Nếu `model_label` cũng dùng nó thì tên thật trong câu báo ở các trang đó sẽ lộ dấu `\`. Còn `&lt;` hiện đúng ở cả 3 kiểu trang (hiện thẳng, qua `escape_link_syntax`, qua `escape_markdown`), vì `escape_markdown` không escape `&`, `;` |
| Test | 6 ca `xfail(strict=True)` của Soi Lỗi (`tests/test_soi_loi_t118.py`) XPASS trên mã mới, rồi gỡ dấu (chỉ xóa khối trang trí, R5). Thêm vào `tests/test_t118_don_thap.py`: `test_angle_bracket_model_never_becomes_a_link_on_any_page` (4 dạng `<…>` × 7 câu báo × 3 kiểu trang hiện; không còn `<` thật, không khớp mẫu link tự động, bộ dò T-044 sạch) và `test_model_label_still_reads_as_the_name` (15 tên: giải mã `&lt;`, bỏ ký tự rộng 0 thì ra đúng tên gốc; tên thật không đổi một ký tự; chạy lại không đổi) |

```
# Bản gốc còn dấu của tests/test_soi_loi_t118.py (git show HEAD:…, chép ra thư mục nháp), chạy trên mã mới
$ uv run pytest <bản gốc> -q -rxX
[XPASS(strict)] SL-T118-1: … (×6)
6 failed, 1 passed in 1.07s          (6 «hỏng» = XPASS strict, đúng mong đợi; 1 qua = ca đối chứng mẫu dò)

# Gỡ dấu, chạy 2 file của lượt này
$ uv run pytest tests/test_soi_loi_t118.py tests/test_t118_don_thap.py -q -rfEsxX
147 passed, 1 skipped in 92.44s     (bỏ qua: ca environb thật, chỉ có trên Mac/Linux)

# 21 file test liên quan (lớp AI, thử mù, chặn link T-044, trang Kế hoạch, trang Bài viết, mọi trang);
# mã băm 3 file đổi 9b7472d2… giống nhau lúc đầu, lúc cuối lượt chạy và lúc commit 3339360
$ uv run pytest <21 file> -q -rfEsxX
2055 passed, 1 skipped, 4 xfailed, 1 warning in 691.86s (0:11:31)
   bỏ qua: ca environb thật (Mac/Linux); 4 xfail có từ trước: SL-T026-3 ×2, SL-T028-1 ×2;
   cảnh báo: Pydantic có từ trước của test_soi_loi_t028.py

$ uv run ruff check .                        # ruff 0.16.10
All checks passed!

# Quét bí mật, PYTHONUTF8=1, 4 file đổi của lượt 2
$ PYTHONUTF8=1 uvx detect-secrets scan …
seo_app/ai/base.py:30  Basic Auth Credentials   (có từ trước, như lượt 1)
```

**21 file:** `test_soi_loi_t118.py`, `test_t118_don_thap.py`, `test_ai.py`, `test_ai_images.py`, `test_ai_openai_gemini.py`, `test_ai_openai_gemini_soi_loi.py`, `test_ai_t026.py`, `test_ai_t028.py`, `test_ai_t034.py`, `test_soi_loi_t026.py`, `test_soi_loi_t028.py`, `test_soi_loi_t034.py`, `test_blind_test.py`, `test_soi_loi_t019.py`, `test_soi_loi_t019_luot2.py`, `test_app_t044_safe_text.py`, `test_soi_loi_t044.py`, `test_settings_blind.py`, `test_t101_plan_page.py`, `test_t101_home_page.py`, `test_app_pages.py`.

**Chưa sửa ở lượt này (ngoài chỗ LC-T034-1), ghi đề xuất:** Soi Lỗi nêu bộ làm sạch chung `escape_link_syntax` (T-031) cũng dùng cho chữ AI hiện trên trang, nên chữ AI có `<https:…>` cũng thành link ở trang xem. Sửa ở hàm chung thì phải giữ được phép đảo `unescape_link_syntax` (gỡ lớp làm sạch trước khi gửi WordPress, T-031) và kiểm lại mọi nơi gọi. Nên làm ở một phiếu riêng (Đề xuất 4).

## Lượt 3 · test cũ hỏng sau khi ẩn chi tiết lỗi (Chỉ Huy B, 03/11)

| Mục | Nội dung |
|---|---|
| Việc | Lần chạy toàn bộ test trên `main` cục bộ `29499dd` (đã gộp T-118, T-073): 22.456 qua, 2 hỏng. `tests/test_link_escape.py::test_timing_helper_has_absolute_limit` hỏng oan vì máy bận (chạy lại qua, không sửa). `tests/test_soi_loi_t058.py::test_st_image_bytes_rac_bao_loi_ro_rang` hỏng thật, chạy riêng vẫn hỏng |
| Nguyên nhân | T-118 đặt `client.showErrorDetails = "type"`. Trang nay chỉ hiện loại lỗi và câu chung của Streamlit («This app has encountered an error. The original error message is redacted…»), dấu vết lỗi rỗng. Dòng 305 cũ lại chờ câu lỗi gốc của Pillow hiện trên trang. Thử trên mã đã gộp: phần tử lỗi chỉ có 3 trường `type`, `message`, `width_config`; `message` là câu chung, không có «cannot identify image file» |
| Gộp | `git merge main`: tua thẳng `9ed433b` → `29499dd` (nhánh đã nằm trong `main`, không có commit gộp). `uv sync`: chỉ cài lại gói của dự án (`pyproject.toml` đổi chú thích `[tool.uv]` của T-078, `uv.lock` không đổi) |

**Sửa test cũ (R5, Chỉ Huy duyệt 03/11):**

| Chỗ | Cũ | Mới |
|---|---|---|
| `tests/test_soi_loi_t058.py:304` | `assert [loi.proto.type for loi in at.exception] == ["PIL.UnidentifiedImageError"]` | Giữ nguyên |
| `tests/test_soi_loi_t058.py:305` | `assert "cannot identify image file" in at.exception[0].message` | Ghép `str(loi.proto)` của **mọi** phần tử lỗi trên trang (câu báo, dấu vết lỗi và mọi trường khác), kiểm **không** có «cannot identify image file» và **không** có «BytesIO» (câu gốc của Pillow là «cannot identify image file <_io.BytesIO object at 0x…>»), kèm 3 dòng chú thích ghi lý do và lần duyệt |

Ý cũ của test vẫn giữ: Pillow 13 báo đúng loại lỗi, không treo, không sập tiến trình, không đưa bytes rác ra trình duyệt. Ý mới là quyết định của chủ dự án ngày 02/11: câu lỗi gốc không lộ ra trang. Tên test, thân trang thử, dòng 304 không đổi.

**Đối chứng** (chạy trong thư mục nháp, không sửa repo): cùng trang đó, đặt `client.showErrorDetails` = `type` thì cả hai chữ đều không có; đặt `full` (mặc định của Streamlit) thì cả hai chữ đều có. Nghĩa là test mới sẽ đỏ nếu sau này ai bỏ dòng `showErrorDetails = "type"`, không qua oan.

**Rà test khác đọc lỗi trên trang** (`grep -rn "\.exception\b" tests/`, 155 dòng ngoài `test_t118_don_thap.py`): 23 dòng không phải dạng `assert not at.exception` trần, đã xem từng dòng.

- `test_soi_loi_t058.py:82`: chỉ so loại lỗi (`DeprecationWarning`), không đọc câu báo.
- `test_la_chan_t086.py:52`, `:54`; `test_soi_loi_t021_t017.py:490`; `test_soi_loi_t041.py:634`, `:665`, `:790`; `test_soi_loi_t051.py:471-473`; `test_soi_loi_t084.py:341`; `test_soi_loi_t090.py:188`, `:242`; `test_t041_seo_ui.py:622`, `:652`, `:737`; `test_t090_env_bang_ma.py:144`, `:151`, `:155`: kiểm **không có** lỗi. Câu lỗi chỉ dùng làm chữ in ra khi test hỏng (nay in câu chung, vẫn đúng loại lỗi).
- `test_t101_home_page.py:94`, `test_la_chan_t113.py:77`: đi qua `assert_plain` (`test_t101_plan_page.py:226`), cũng chỉ kiểm không có lỗi.
- `test_app_images.py:611`: chỉ là chuỗi mô tả của test.

Không test nào khác đọc `stack_trace`, so câu chung của Streamlit, hay tự đặt `client.showErrorDetails` (ngoài `test_t118_don_thap.py`, đã có bộ đặt và trả lại giá trị riêng). Trong `app/`, `seo_app/` không có `st.exception(`. Kết luận: chỉ ca dòng 305 lệch theo `showErrorDetails`, đúng như lần chạy toàn bộ.

**Lưu ý:** như mọi test `AppTest`, ca này đọc cấu hình từ `.streamlit/config.toml` của thư mục đang chạy (gốc dự án), đúng cách app thật chạy. `test_t118_don_thap.py::test_config_shows_only_error_type` ghim giá trị `type` trong file đó.

**Kiểm thử** (không chạy toàn bộ pytest, theo dặn dò):

```
$ uv run pytest tests/test_soi_loi_t058.py -q -k bytes_rac
1 passed, 59 deselected in 4.11s

$ uv run pytest tests/test_soi_loi_t058.py tests/test_t118_don_thap.py tests/test_app_pages.py -q
218 passed, 1 skipped in 115.04s (0:01:55)   (bỏ qua: ca environb thật, chỉ có trên Mac/Linux)
   mã băm test_soi_loi_t058.py eb2fe307… giống nhau lúc bắt đầu và lúc xong lượt chạy

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t058.py
1 file already formatted
```

## Câu hỏi cho chủ dự án

Không có.

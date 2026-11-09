# Báo cáo T-125 · Trang «📈 Theo dõi» và mục Search Console trong Cài đặt (Giai đoạn 6, đợt 3) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-125](../tickets/T-125-trang-theo-doi.md), nhánh `team/T-125`: mã và test Họa Sĩ `2cc720b`, gộp `main` `8a09fcb`, báo cáo `216ff2f` (gốc `team/T-124` `682f62c`); thiết kế T-120 mục 1, 4.1, 4.4 |
| Ngày nộp | 2026-11-07 (08:30 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp**. SL-T125-1: mỗi lần bấm trên trang Theo dõi mất 2,2–2,9 giây với website cỡ thật, vì trang đọc lại toàn bộ bản lưu tạm ở mỗi lần chạy lại. SL-T125-2: «Xóa bản lưu tạm» bấm lúc tab khác đang lấy số liệu thì vẫn xóa, bản lưu tạm mất phần đầu 16 tháng mà không báo. Cả 9 trọng tâm Chỉ Huy giao đều **đúng**: mở trang và Cài đặt không gọi mạng, chữ Google hiện chữ thuần, biểu đồ chỉ số và ngày, lưu thuộc tính đúng đối tượng của lần tìm, hai tab có BUSY, câu cố định khi có bài không khớp địa chỉ, nút xóa bản lưu tạm hỏi lại, hai cảnh báo, không lùi trang khác. Điều kiện: sửa SL-T125-1, -2 ở lượt 2 (bản sửa nháp: 2 ca `xfail` thành XPASS, 45 ca khác qua) hay chuyển phiếu sau, tùy Chỉ Huy. Không chặn Lá Chắn |

## Tóm tắt (cho chủ dự án)

- **Trang Theo dõi làm đúng và an toàn.**
  - Mở trang, mở Cài đặt không hỏi Google; chỉ khi anh bấm nút mới hỏi.
  - Chữ lấy từ Google và website (từ khóa người lạ gõ, đường dẫn, tên bài) chỉ hiện như chữ thường, không thành link bấm được, kể cả khi cố tình viết dạng link.
  - Lưu thuộc tính chỉ nhận đúng thuộc tính vừa tìm thấy.
- **Lỗi 1 (nhỏ, nên sửa): trang hơi chậm.** Với website cỡ của anh, mỗi lần đổi khoảng ngày hay chọn bài phải chờ khoảng 2–3 giây, vì phần mềm đọc lại toàn bộ số liệu đã lưu dù không có gì mới. Website lớn gấp ba thì khoảng 6 giây. Bản sửa thử còn khoảng 1 giây.
- **Lỗi 2 (nhỏ, hiếm gặp):** nếu mở hai cửa sổ, một cửa sổ đang lấy số liệu mà cửa sổ kia bấm «Xóa bản lưu tạm», phần mềm vẫn xóa. Cửa sổ đang lấy vẫn báo «đã lấy xong» nhưng chỉ còn khoảng 6 tháng số liệu thay vì 16 tháng, và các lần bấm sau không tự lấy bù.
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t125.py` | Mới: **6 ca: 4 qua, 2 `xfail(strict=True)`** của 2 lỗi mới. Không gọi mạng; mọi file lưu tạm trong thư mục tạm |
| `docs/team/reports/T-125-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Họa Sĩ, phiếu hay file khác. Test dùng lại dữ liệu mẫu, fixture và client giả đếm lệnh của `tests/test_t125_tracking_page.py`, `tests/test_t125_settings_search_console.py`. File đo tạm `tests/test_zz_probe_t125_perf.py` đã xóa (số đo ghi ở mục 2).

## 1. Chín trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả |
|---|---|---|
| 1 | **Mở trang và Cài đặt không gọi mạng** | **Đúng.** Đọc mã: mọi đường gọi mạng (`refresh`, `find_properties`, `check_connection`, client WordPress) nằm sau `if st.button(…)`; mở trang chỉ đọc file lưu tạm khi file đã có (không tạo file). Ca của Họa Sĩ (client giả đếm lệnh, có đối chứng) qua. Tôi thêm: ở Cài đặt, sau khi đã bấm «Tìm thuộc tính», «Kiểm tra», đổi ô chọn và chạy lại trang nhiều lần, `find_properties`, `check_connection` vẫn đúng 1 lần mỗi hàm |
| 2 | **Chữ Google hiện chữ thuần; bảng dùng `safe_rows`** | **Đúng.** Mọi bảng có chữ ngoài đi qua `safe_rows` (trang Theo dõi) hay `plan_sync.safe_text` + `visible` (Cài đặt); không `unsafe_allow_html`, không cột link. Tôi thêm ca quét **mọi** chữ Markdown trên trang (markdown, chú thích, ô báo, tên ô mở rộng, nhãn số liệu) khi xem bài có từ khóa dạng `**đậm** [x](…)`, `=HYPERLINK(…)`, xem từng cách gõ, rồi bài có tiêu đề `**Đậm** [bấm](…) <b>x</b>`: không còn link hay chữ đậm chưa thoát. Ký tự đảo hướng: tiêu đề bài qua `_clean_text` của client WordPress (bỏ loại Cf), đường dẫn qua `page_label` (`clean_text` sau khi giải mã `%`), từ khóa qua client T-121 (`clean_text`), tên máy kiểm dạng tên miền ASCII; ở Cài đặt thuộc tính, tên máy, email qua `visible` (ký tự vô hình, đảo hướng thành «�») |
| 3 | **Biểu đồ chỉ có số và ngày** | **Đúng.** `CLICK_CHART`, `POSITION_CHART` là hằng; `chart_data` chỉ có `tuan` (`dd/mm/yyyy` do code viết), `click` (số), `vi_tri` (số hay rỗng); tên bài đặt ngoài biểu đồ qua `escape_markdown`. Ca của Họa Sĩ qua |
| 4 | **«Tìm thuộc tính» truyền đúng đối tượng trong `session_state` vào `save_property`** | **Đúng.** `_save_property` lấy `S["gsc-found"]` (kết quả lần bấm) và truyền nguyên đối tượng; ô chọn chỉ có `found.usable_site_urls`. Ca của Họa Sĩ (so `is`) qua; ca của tôi cũng so `is` sau khi đã đổi ô chọn và chạy lại trang |
| 5 | **Hai tab cùng bấm «Lấy số liệu»: tab thứ hai thấy BUSY** | **Đúng.** Trang gọi `refresh` (khóa `_FETCH_LOCK` của T-124), không tự dựng client; tab sau nhận `MSG_BUSY` (ô thông tin), 0 client. Ca của Họa Sĩ qua |
| 6 | **Câu cố định khi `skipped_items > 0`** | **Đúng.** «N bài, trang có địa chỉ không khớp địa chỉ website trong cài đặt (WORDPRESS_URL) nên không gắn được số liệu.» Ca của Họa Sĩ qua |
| 7 | **Nút «Xóa bản lưu tạm»** | Hỏi lại rồi mới xóa; file lỗi thì ô xóa mở sẵn (Lá Chắn T-122 mục 8.2). **Nhưng** không xét lần lấy số liệu đang chạy ở tab khác: **SL-T125-2** |
| 8 | **Cảnh báo biến môi trường đè, quyền cao hơn «Hạn chế»** | **Đúng.** `env_file.gsc_site_url_overridden()` (biến có mặt, kể cả rỗng) ở mỗi lần mở Cài đặt và sau khi lưu; quyền «Chủ sở hữu», «Toàn quyền» cảnh báo ở cả «Tìm thuộc tính» và «Kiểm tra». Ca của Họa Sĩ qua |
| 9 | **Không lùi trang khác, test Cài đặt** | **Đúng.** `test_app_pages` mở được trang mới; 14 file test của trang Cài đặt (gồm `test_soi_loi_t084` cấm in giá trị `.env`, `test_t101_settings_google` đếm nhãn) qua (mục 4). Họa Sĩ không đổi test cũ nào: `2cc720b` chỉ thêm 2 file test mới |

## 2. Lỗi mới

### SL-T125-1 · Thấp · Mỗi lần bấm trên trang Theo dõi đọc lại toàn bộ bản lưu tạm

- **Đo** (file đo tạm, AppTest, Windows 11; máy đang chạy toàn bộ test của Chỉ Huy, CPU ~48%):
  - Bản lưu tạm cỡ website thật như Thợ Máy T-122 ước tính: 200 trang × 486 ngày = 97.200 dòng ngày, 2 kỳ × 5.000 từ khóa, 6,8 MB.
  - Mỗi lần đổi khoảng ngày, chọn bài: **2,2–2,9 giây**.
  - Tách một lần chạy lại (2,44 giây): đọc và kiểm bản lưu tạm **1,25 giây**, `build_tracking` **0,76 giây**, `aggregate` 0,21 giây, `site_totals` 0,10 giây, danh sách bài 0,02 giây.
  - Cỡ gần trần của T-122 (600 trang × 486 ngày = 291.600 dòng, 19,4 MB): một lần chạy lại **6,13 giây** (đọc bản lưu tạm 3,12 giây, `build_tracking` 2,13 giây, `aggregate` 0,50 giây, `site_totals` 0,25 giây).
- **Vì sao:** `load_cache` gọi `SearchCacheStore.load` ở **mỗi** lần chạy lại. Hàm này mở file, chạy `quick_check`, kiểm từng dòng, dù file không đổi. Sau đó `build_tracking` dựng lại cả bảng khớp bài.
  - Thợ Máy T-122 đã đề nghị cho T-125: giữ `SearchCache` đã đọc trong `st.session_state` kèm giờ sửa và cỡ file, chỉ đọc lại khi hai giá trị đó đổi. Trang chưa làm.
- **Tái hiện** (`test_sl_t125_1_reruns_do_not_reload_an_unchanged_cache`): mở trang, rồi đổi khoảng, chọn bài, đổi kỳ so sánh → `SearchCacheStore.load` bị gọi thêm 3 lần, file không đổi.
- **Hậu quả:** mỗi cú bấm trên trang đứng 2–3 giây, website lớn hơn thì lâu hơn. Không sai số liệu. Xếp Thấp vì chỉ ảnh hưởng tốc độ.
- **Gợi ý sửa:** giữ `(đường dẫn, st_mtime_ns, st_size, thuộc tính, WORDPRESS_URL) → SearchCache` trong phiên; đọc lại khi khóa đổi. `SearchCache` không pickle được nhưng `session_state` không cần pickle (`.streamlit/config.toml` không bật `enforceSerializableSessionState`). Có thể giữ cả `SiteTracking` theo cùng khóa cộng mốc tải danh sách bài và kế hoạch, bớt thêm 0,76 giây.
- **Đối chứng cho bản sửa:** `test_page_shows_new_data_after_the_cache_file_changes` (đang qua) canh để bản sửa không giữ số cũ khi tab khác vừa ghi thêm.
- **Bản sửa nháp** (chỉ phần bản lưu tạm, mục 3), cỡ 200 trang, cùng máy: mỗi lần bấm còn **0,9–1,2 giây**; lần bấm đầu sau khi mở trang 2,4 giây. Phần còn lại chủ yếu là `build_tracking`.

### SL-T125-2 · Thấp · «Xóa bản lưu tạm» không xét lần lấy số liệu đang chạy ở tab khác

- **Tái hiện bằng script** (`probe_clear.py` ở thư mục nháp): tab A «Lấy số liệu mới» lần đầu, dừng sau 10/16 đoạn. Trong lúc khóa `_FETCH_LOCK` đang giữ, tab B gọi đúng việc nút «Xóa» làm (`SearchCacheStore.clear()`): xóa được. Tab A ghi tiếp các đoạn sau vào file mới rồi báo **DONE** «Đã lấy số liệu tới hết ngày 01/11/2026». Bản lưu tạm chỉ còn **176/486 ngày** (từ 12/05/2026). Hôm sau bấm lại: DONE, vẫn từ 12/05/2026 (`refresh` chỉ lấy tiếp về phía mới, không lấy bù phía cũ).
- **Ca test** (`test_sl_t125_2_clearing_is_refused_while_another_tab_fetches`): giữ khóa lấy số liệu, bấm «Xóa bản lưu tạm» → «Xóa»: file bị xóa, không có câu «tab khác».
- **Hậu quả:** người dùng thấy «đã lấy xong», nhưng khoảng dài (3 tháng trở lên phía cũ, «Cùng kỳ năm trước») báo «chưa đủ số liệu» mà không rõ vì sao, tới khi xóa lại lần nữa. Không sai số đã có. Hiếm: cần hai cửa sổ, một cái đang lấy (lần đầu khoảng một phút). Xếp Thấp.
- **Gợi ý sửa:** xóa trong khóa lấy số liệu; khóa đang giữ thì báo `MSG_BUSY`, không xóa.
  - Gọn nhất là một hàm công khai ở `seo_app/tracking/refresh.py` (Thợ Máy; T-125 không được sửa `seo_app/**`), ví dụ `clear_cache(store)` trả câu cố định, để trang không đụng `_FETCH_LOCK` riêng.
  - Đối chứng `test_clearing_still_works_when_no_fetch_is_running` (đang qua): không có lần lấy nào thì xóa ngay.

## 3. Thử bản sửa nháp

Bản nháp (không commit; `fix_draft.py` ở thư mục nháp của phiên, chỉ sửa `app/views/tracking.py`): `load_cache` giữ bản đã đọc trong phiên theo (đường dẫn, giờ sửa, cỡ file, phạm vi); `_clear_cache` giữ `_FETCH_LOCK` trong lúc xóa, khóa bận thì báo `MSG_BUSY`. Chạy trên worktree tạm từ `216ff2f`:

```
$ pytest tests/test_t125_tracking_page.py tests/test_t125_settings_search_console.py tests/test_soi_loi_t125.py -q
[XPASS(strict)] SL-T125-1 …
[XPASS(strict)] SL-T125-2 …
2 failed, 45 passed in 75.32s
# 2 «failed» đúng là 2 XPASS(strict) của SL-T125-1, -2 (gỡ dấu xfail thì qua);
# 45 qua gồm đủ 41 ca của Họa Sĩ và 4 ca đối chứng của Soi Lỗi
```

Bản nháp chỉ để chứng minh sửa được. Phần SL-T125-2 trong bản nháp dùng `_FETCH_LOCK` (biến riêng của `refresh.py`); bản sửa thật nên qua hàm công khai của Thợ Máy (mục 2).

## 4. Test đã chạy (chỉ test liên quan)

| Nhóm | File | Kết quả |
|---|---|---|
| T-125 + mở mọi trang | `test_t125_tracking_page`, `test_t125_settings_search_console`, `test_app_pages`, `test_app` | **65 qua** (05/11, cùng commit `216ff2f`) |
| Trang Cài đặt | `test_app_t044_safe_text`, `test_settings_blind`, `test_settings_images`, `test_settings_keys`, `test_soi_loi_t016_t020`, `test_soi_loi_t019`, `test_soi_loi_t021_t017`, `test_soi_loi_t023`, `test_soi_loi_t044`, `test_soi_loi_t062`, `test_soi_loi_t084`, `test_soi_loi_t112`, `test_t101_settings_google`, `test_t112_settings_switch` | **519 qua**, 6 bỏ qua (có từ trước) |
| Soi Lỗi T-125 | `test_soi_loi_t125` | **4 qua, 2 xfail** |

Gộp thử: `216ff2f` + `main` cục bộ `e25afa1` (đã có T-124 `06a1b0e`, phiếu T-133): **không xung đột**.
- Chạy 7 file trên bản gộp (`seo_app` nạp từ chính bản gộp): T-125 của Họa Sĩ, Soi Lỗi T-125, `test_app_pages`, `test_soi_loi_t084`, `test_t101_settings_google`, `test_tracking_refresh`.
- Lượt đầu: 209 qua, 2 `xfail`, 1 hỏng «AppTest script run timed out after 30(s)». Lúc đó máy đang chạy toàn bộ test của Chỉ Huy (CPU 67%, 12 tiến trình Python); bộ lọc đầu ra cắt mất tên ca.
- Chạy lại cả 7 file: **210 qua, 2 `xfail`, 0 hỏng**. Ca hỏng lượt đầu là hỏng oan do máy bận.
- `ruff check .` trên bản gộp: sạch.

`uv run ruff check .`: sạch. `ruff format --check tests/test_soi_loi_t125.py`: sạch.

## 5. Ghi nhận (không phải lỗi)

- **GN-1 · Kết quả «Tìm thuộc tính» không tự bỏ khi `WORDPRESS_URL` đổi.** Mục «dùng được» tính theo website lúc tìm; sửa `.env` rồi lưu ngay từ kết quả cũ thì lần lấy số liệu sau báo câu cố định «không phải của website» (client T-121 kiểm lại). Bấm «Tìm thuộc tính» lại là xong; chấp nhận được.
- **GN-2 · Mở trang với bản lưu tạm của thuộc tính khác** (vừa đổi thuộc tính ở Cài đặt): file cũ bị bỏ ngay khi mở trang, trang báo «Chưa có số liệu». Đây là hành vi của kho T-122 (thiết kế 2.7 bước 5), đúng ý.
- **GN-3 · Hai giới hạn Họa Sĩ đã ghi** (mục 6 báo cáo Họa Sĩ): số trong bảng là chữ (bấm tiêu đề cột xếp theo chữ); chưa có nút lấy từ khóa cho khoảng tự chọn. Đồng ý để phiếu sau.

## 6. Bằng chứng

```
# Nhánh team/T-125 tại 216ff2f + file test mới, Windows 11, Python 3.12.15
$ uv run pytest tests/test_soi_loi_t125.py -q -rx
XFAIL test_sl_t125_1_reruns_do_not_reload_an_unchanged_cache      (--runxfail: assert 3 == 0)
XFAIL test_sl_t125_2_clearing_is_refused_while_another_tab_fetches (--runxfail: file đã bị xóa)
4 passed, 2 xfailed
$ uv run ruff check .                                   # All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t125.py # 1 file already formatted

# Nhóm test liên quan trên 216ff2f (05/11): T-125 + mở mọi trang 65 passed; 14 file trang Cài đặt
# 519 passed, 6 skipped

# Đo tốc độ (file đo tạm tests/test_zz_probe_t125_perf.py, đã xóa; AppTest, máy đang chạy toàn bộ
# test của Chỉ Huy):
200 trang × 486 ngày (6,8 MB): mỗi lần bấm 2,17–2,85 s; một lần chạy lại 2,44 s = đọc bản lưu tạm
  1,25 s + build_tracking 0,76 s + aggregate 0,21 s + site_totals 0,10 s + …
600 trang × 486 ngày (19,4 MB): một lần chạy lại 6,13 s = đọc 3,12 s + build_tracking 2,13 s + …
Bản sửa nháp, 200 trang: 2,39 s (lần đầu), 1,18 s, 1,20 s, 0,93 s

# SL-T125-2 (probe_clear.py ở thư mục nháp): tab A dừng sau 10/16 đoạn, khóa đang giữ; tab B xóa: được;
# tab A: DONE «Đã lấy số liệu tới hết ngày 01/11/2026…»; bản lưu tạm 12/05/2026 .. 03/11/2026 (176 ngày);
# hôm sau bấm lại: DONE, vẫn từ 12/05/2026

# Quét ký tự ẩn file test: sạch. Quét bí mật, PYTHONUTF8=1: results {}; đối chứng (bản sao thêm khóa
# giả, trong thư mục đang quét): bắt được (Secret Keyword).
```

Các worktree tạm (`fix`, `gop`) đã gỡ; commit gộp tạm không đẩy.

## 7. Đề xuất

- **Lượt 2 T-125 (Họa Sĩ, kèm Thợ Máy cho SL-T125-2):** sửa SL-T125-1, -2; gỡ đúng 2 dấu `xfail` (R5), không đổi thân test.
- **Lá Chắn T-125:** không có điểm bảo mật mới; hai lỗi đều không đổi chữ hiện ra hay đường gọi mạng.

# Báo cáo T-125 lượt 2 · Trang «📈 Theo dõi»: không đọc lại bản lưu tạm khi file không đổi, xóa trong khóa lấy số liệu

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B (Họa Sĩ T-125 đang nghỉ) |
| Phiếu | [T-125](../tickets/T-125-trang-theo-doi.md) · lỗi từ [biên bản Soi Lỗi](T-125-soi-loi.md) mục 2 |
| Nhánh | `team/T-125`, từ `1c55e9e`; mã và test `93d9f78`, báo cáo ở commit ngay sau |
| Ngày nộp | 2026-11-07 (giờ máy, +07) |
| Kết quả | Hoàn thành: SL-T125-1, SL-T125-2 đã sửa |

## Tóm tắt (cho chủ dự án)

- Trang «📈 Theo dõi» **nhanh hơn khoảng 5 lần** khi bấm đổi khoảng ngày, chọn bài, đổi kỳ so sánh: trước mất 2,1–2,5 giây mỗi lần bấm, nay còn khoảng 0,3–0,6 giây (website cỡ thật: 200 trang, 16 tháng số liệu).
  - Trang không đọc lại toàn bộ file lưu tạm ở mỗi lần bấm nữa. Chỉ khi file đổi (vừa lấy số liệu mới, tab khác vừa ghi, vừa xóa) mới đọc và kiểm lại đủ như trước.
- Nút «Xóa bản lưu tạm» không xóa khi tab khác đang lấy số liệu: trang báo «đang lấy ở tab khác», chờ xong rồi xóa. Trước đây xóa giữa chừng làm mất phần số liệu cũ mà vẫn báo «đã lấy xong».
- Không đổi gì trên giao diện, không gọi mạng khi mở trang.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/search_cache.py` | Thêm `SearchCacheStore.stamp()`: «dấu file» gồm ổ đĩa, mã file, cỡ, giờ sửa (nano giây), **số đếm thay đổi** ở byte 24–27 đầu file SQLite (tăng mỗi lần ghi xong, kể cả hai lần ghi cùng cỡ trong cùng một nhịp đồng hồ), cỡ và giờ sửa của file `-wal` nếu có. Chỉ `lstat` và đọc 100 byte đầu; không mở SQLite, không ghi, không đi theo liên kết. Liên kết, thư mục, lỗi đọc: `None` (nơi gọi đọc lại như thường) |
| `seo_app/tracking/refresh.py` | Thêm `clear_cache(store) -> ClearResult` (SL-T125-2): xóa trong **cùng khóa** `_FETCH_LOCK` với `refresh`. Khóa đang giữ (tab khác đang lấy) thì không xóa, trả `ClearResult(False, MSG_BUSY, busy=True)`. Lỗi của cache ra câu cố định. Khóa luôn được nhả. Đang xóa thì `refresh` ở tab khác nhận BUSY |
| `app/views/tracking.py` | SL-T125-1. <ul><li>`load_cache`: giữ bản đã đọc trong `st.session_state` (khóa `trk-cache-memo`) theo (dấu file, phạm vi, múi giờ). Dấu khác thì đọc, kiểm lại đủ (LC-T120-9). Khóa giữ là dấu lấy trước khi đọc, nên file đổi trong lúc đọc thì lần sau đọc lại; lỗi đọc không giữ.</li><li>`tracking_for`: giữ thêm kết quả `build_tracking` khi bản lưu tạm, địa chỉ website, danh sách bài, dòng kế hoạch không đổi (Soi Lỗi gợi ý).</li><li>`_clear_cache` gọi `clear_cache`: bị từ chối thì ô báo vàng (`MSG_BUSY`), lỗi thì ô đỏ.</li><li>Không `st.cache_data`, `st.cache_resource` (LC-T120-21)</li></ul> |
| `tests/test_soi_loi_t125.py` | Gỡ 2 dấu `xfail` đã XPASS (R5) và dòng `import pytest` không còn dùng; thân test không đổi |
| `tests/test_t125_tho_may.py` | Mới, 22 ca (1 ca symlink file bỏ qua trên máy không cho tạo symlink) |
| `docs/team/reports/T-125-tho-may.md` | Báo cáo này |

### Chỗ để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Giữ ở đâu | Trong phiên (`st.session_state`), mỗi tab một bản | Chỉ Huy cho chọn phiên hay bộ nhớ tiến trình. Bản trong phiên không dùng chung giữa các luồng, không cần khóa, tự mất khi đóng tab. Mỗi tab tốn thêm bộ nhớ cỡ một bản đọc (vài chục MB ở cỡ trần) |
| 2 | Dấu file | Thêm «số đếm thay đổi» SQLite và mã file, không chỉ cỡ + giờ sửa | Giờ sửa trên Windows có thể trùng cho hai lần ghi sát nhau, cỡ file có thể giữ nguyên (ghi đè trang cũ). Có ca test cho cả hai |
| 3 | Lớp giữ | `dict` thường, không phải lớp khai báo trong trang | Streamlit chạy lại cả file trang mỗi lần nên lớp khai báo trong trang là lớp mới mỗi lần; `isinstance` với bản giữ của lần trước luôn sai (đã gặp khi sửa) |
| 4 | Câu khi bị từ chối xóa | Dùng đúng `MSG_BUSY` của `refresh` | Theo lời giao. Câu «Chờ tab đó xong rồi mở lại trang» vẫn đúng việc: mở lại rồi bấm xóa nếu còn cần |

## Đo thời gian (trước / sau)

File đo tạm (AppTest, như Soi Lỗi mục 2; đã xóa, không commit), Windows 11, máy có phiên khác chạy cùng lúc. Bản lưu tạm cỡ website thật: 200 trang × 486 ngày + 2 kỳ × 5.000 từ khóa, 6,8 MB; 200 bài trong danh sách đã đăng. Mỗi vòng: mở trang rồi 5 lần bấm (đổi khoảng 7 ngày, chọn bài, đổi kỳ so sánh, đổi khoảng 28 ngày, chọn bài khác). «Trước» chạy trên worktree tạm tách rời ở `1c55e9e` (đã gỡ), xen kẽ với «sau».

| Vòng | Trước: mỗi lần bấm | Sau: mỗi lần bấm |
|---|---|---|
| 1 | 2,12 – 2,50 s | 0,31 – 0,59 s |
| 2 | 2,71 – 4,03 s | 0,40 – 0,92 s |
| 3 | 2,87 – 3,48 s | 0,56 – 0,93 s |

- Nhanh hơn khoảng 4–6 lần. Máy bận dần nên vòng sau chậm hơn ở cả hai bản.
- Phần còn lại mỗi lần bấm là cộng số theo kỳ vừa chọn (`aggregate`, `site_totals`) và vẽ bảng: phần này đổi theo lựa chọn nên vẫn phải tính lại.
- Lần mở trang đầu tiên vẫn đọc, kiểm đủ (7–22 s ở cả hai bản, gồm cả thời gian nạp thư viện của AppTest; máy càng bận càng lâu): không đổi, đúng LC-T120-9.

## Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới |
|---|---|---|
| `test_soi_loi_t125.py::test_sl_t125_1_reruns_do_not_reload_an_unchanged_cache` | `xfail(strict=True)` SL-T125-1 | XPASS sau khi sửa: gỡ dấu, thân test không đổi |
| `test_soi_loi_t125.py::test_sl_t125_2_clearing_is_refused_while_another_tab_fetches` | `xfail(strict=True)` SL-T125-2 | XPASS sau khi sửa: gỡ dấu, thân test không đổi |

Gỡ thêm dòng `import pytest` (chỉ dùng cho hai dấu đó, ruff báo thừa). Không đổi kỳ vọng ca nào khác. Hai ca đối chứng của Soi Lỗi (`test_page_shows_new_data_after_the_cache_file_changes`, `test_clearing_still_works_when_no_fetch_is_running`) vẫn qua.

## Bằng chứng

```
# Windows 11, Python 3.12.15, ruff 0.16.10. Trên đúng commit 93d9f78 (git status chỉ còn file báo
# cáo này chưa commit). 25 file: T-122 (test_search_cache, test_soi_loi_t122), T-123 (6 file
# test_tracking_*, test_soi_loi_t123), T-124 (test_tracking_refresh, test_env_file_gsc,
# test_t124_chuan_hoa_va_cache, test_soi_loi_t124), T-125 (test_t125_tracking_page,
# test_t125_settings_search_console, test_soi_loi_t125, test_t125_tho_may), Cài đặt
# (test_soi_loi_t084, test_t101_settings_google), test_app_pages, và test quét cả cây mã nguồn
# (test_images_process, test_la_chan_t096, test_soi_loi_t034, test_t103_plan_prompt,
# test_wordpress_release)
$ uv run pytest -q -rfEsxX <25 file>
1605 passed, 2 skipped in 480.11s (0:08:00)
#   0 hỏng; 2 bỏ qua là ca symlink file (Windows chưa bật Developer Mode)

$ uv run ruff check .                     # toàn repo
All checks passed!
$ uv run ruff format --check <5 file mã, test đã sửa>
5 files already formatted

# Quét bí mật: bản sao 5 file đổi ở thư mục nháp, PYTHONUTF8=1, detect-secrets --all-files
results: {}
# Đối chứng: thêm một khóa giả vào bản sao refresh.py → bắt được (Secret Keyword). Đã xóa.
# Ký tự ẩn, CR (script ở thư mục nháp): 0 trong 6 file.
# Gộp thử: git merge-tree với main cục bộ mới 31d8cec: không xung đột.
```

**Thử đột biến** (script ở thư mục nháp: sửa cố ý một chỗ, chạy `test_t125_tho_may.py`, `test_soi_loi_t125.py`, trả file về nguyên văn và kiểm SHA-256): 11 đột biến, **9 bị bắt**.

| Mã | Đột biến | Kết quả |
|---|---|---|
| M01 | Trang luôn đọc lại | Bị bắt |
| M03 | Khóa giữ không có phạm vi (đổi thuộc tính vẫn dùng bản cũ) | Bị bắt |
| M04–M06 | Dấu file bỏ số đếm thay đổi; bỏ mã file; bỏ WAL | Bị bắt cả 3 |
| M07 | `clear_cache` không giữ khóa | Bị bắt |
| M08, M09 | `build_tracking` luôn dựng lại; bỏ qua đầu vào đổi | Bị bắt cả 2 |
| M11 | Bị từ chối xóa vẫn báo ô đỏ | Bị bắt |
| M02 | Giữ bản đọc dù file đổi trong lúc đọc | **Sống, tương đương**: khóa giữ là dấu lấy trước khi đọc nên lần sau vẫn đọc lại. Phép kiểm dấu lần hai sau khi đọc là thừa: đã bỏ cho gọn (ca `test_file_written_during_reading_is_read_again` vẫn ghim hành vi) |
| M10 | Dấu file đi theo liên kết (`stat` thay `lstat`) | **Sống trên máy này**: chỉ thử được bằng symlink file; ca `test_stamp_of_a_folder_or_link_is_none` có phần symlink, bị bỏ qua trên Windows chưa bật Developer Mode (chạy được trên Mac/Linux) |

## Đối chiếu tiêu chí

- [x] **SL-T125-1**: trang không đọc lại bản lưu tạm khi file không đổi (`test_sl_t125_1_reruns_do_not_reload_an_unchanged_cache` đã gỡ `xfail`), không dựng lại bảng khớp bài (`test_reruns_reuse_the_tracking_table_too`). Đọc lại khi file đổi (`test_page_shows_new_data_after_the_cache_file_changes`, `test_file_written_during_reading_is_read_again`), phạm vi đổi (`test_changed_property_reads_the_file_again`), danh sách bài đổi (`test_new_post_list_rebuilds_the_tracking_table`); lỗi đọc không giữ (`test_page_has_no_streamlit_cache_and_reads_errors_each_time`); mỗi phiên tự đọc (`test_a_new_session_reads_the_file_itself`). Dấu file: 7 ca `test_stamp_*`
- [x] **LC-T120-9**: mỗi lần file đổi, trang gọi `SearchCacheStore.load` (kiểm đủ như T-122); dấu file chỉ quyết định có đọc lại hay không
- [x] **LC-T120-21**: không `st.cache_data`, `st.cache_resource`, `st.fragment` (ca đọc mã nguồn trang); mở trang, chạy lại không gọi mạng (`no_network.count == 0`)
- [x] **SL-T125-2**: hàm công khai `refresh.clear_cache` (`test_sl_t125_2_clearing_is_refused_while_another_tab_fetches` đã gỡ `xfail`; `test_clear_cache_refuses_while_a_fetch_holds_the_lock`, `test_clear_cache_holds_the_lock_while_clearing`, `test_clear_cache_from_two_threads_never_runs_twice_at_once`, `test_clear_cache_error_is_a_fixed_message_and_releases_the_lock`, `test_clear_cache_releases_the_lock_on_unexpected_errors`); trang báo ô vàng, giữ số liệu (`test_clear_refused_shows_a_warning_and_keeps_the_numbers`); xóa được thì bỏ bản giữ (`test_clearing_drops_the_session_copy`)
- [x] Gỡ `xfail` khi XPASS, chỉ xóa dấu (R5, bảng trên)
- [x] Đo trước/sau (mục Đo)
- [x] Test T-122 → T-125, Cài đặt (`test_soi_loi_t084`, `test_t101_settings_google`), `test_app_pages.py`, test quét cả cây mã nguồn; `uv run ruff check .` sạch
- [ ] Toàn bộ `uv run pytest`: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Bộ nhớ:** mỗi tab giữ một bản lưu tạm đã đọc và bảng khớp bài (cỡ website thật vài chục MB, cỡ trần lớn hơn). Đóng tab thì mất. Nhiều tab cùng mở trang Theo dõi thì nhân lên theo số tab.
- **Dấu file trên ổ mạng, ổ đồng bộ đám mây:** giờ sửa, mã file có thể kém tin cậy hơn ổ thường. «Số đếm thay đổi» SQLite vẫn đổi theo mỗi lần ghi nên không bỏ sót thay đổi do chính phần mềm ghi.
- Cửa sổ rất ngắn khi trang đọc 100 byte đầu file đúng lúc tab khác xóa file: trên Windows lệnh xóa có thể báo lỗi một lần (câu cố định), bấm lại là xong.

## Đề xuất

- **Lá Chắn T-125:** điểm mới cần xem: `stamp()` mở file chỉ đọc 100 byte đầu (sau `lstat`, chỉ file thường); bản giữ trong `session_state` là dữ liệu đã kiểm, không chép ra đâu.
- **Phiếu sau (Thấp):** lần mở trang đầu vẫn đọc, kiểm đủ (cỡ trần khoảng 3 giây đọc + 2 giây dựng bảng, theo số Soi Lỗi). Có thể nhanh hơn nếu `build_tracking`, `aggregate` dùng chỉ mục theo trang thay vì duyệt mọi dòng mỗi kỳ.

## Câu hỏi cho chủ dự án

Không có.

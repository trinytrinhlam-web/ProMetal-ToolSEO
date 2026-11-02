# Báo cáo T-113 · Nối nút «Cập nhật trạng thái từ website» (T-109) vào trang Kế hoạch; trung hòa ô công thức ở trang Kết nối

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | T-113 (Chỉ Huy B giao 31/10; file phiếu chưa có trên `main`, đọc bản ở thư mục tạm của Chỉ Huy) |
| Ngày nộp | 2026-10-31 12:46 |
| Nhánh | `team/T-113` (từ `main` cục bộ `bb25dde`: có T-101, T-102, T-109) |
| Kết quả | Hoàn thành: yêu cầu 1–6, điều kiện Lá Chắn T-109 cho lượt nối nút (a → f), G1, G2 của Soi Lỗi T-109. Không đổi test cũ. Tự tìm ra và sửa: trang Kế hoạch tạo file cache bài đã đăng khi chỉ mở trang |

## Tóm tắt (cho chủ dự án)

- Ở trang **Kế hoạch**, nút **«🌐 Cập nhật trạng thái từ website»** giờ làm trọn việc:
  - bấm thì phần mềm hỏi website trạng thái các bài đã gửi (chỉ hỏi, không sửa bài nào);
  - phần mềm so với Google Sheet rồi hiện khung **«Thay đổi trạng thái từ website»**: dòng nào nên đổi (ví dụ «Đã gửi nháp → Đã đăng», kèm ngày đăng thật trên website) và các cảnh báo (bài «Lỡ lịch», bài không còn thấy, bài về nháp…);
  - bạn tick những dòng muốn ghi (không dòng nào tick sẵn; có nút «Chọn tất cả»), rồi bấm **«✍️ Ghi … thay đổi vào Google Sheet»**. Phần mềm chỉ đổi 3 ô của dòng đó: Trạng thái, Ngày đăng thực tế, Cập nhật lúc.
  - Dòng vừa bị sửa ở nơi khác thì không ghi, có bảng báo. Lần kiểm đã quá 5 phút thì nút ghi khóa, phần mềm mời bạn bấm kiểm lại.
- Nhãn «Lỡ lịch» ở trang Kế hoạch và trang Bài viết nay dùng chung một mốc (15 phút) với phần lõi, nên luôn khớp nhau.
- Trang **Kết nối WordPress**: bảng chuyên mục, thẻ khi tải về file CSV mở bằng Excel không còn thành công thức (ô bắt đầu bằng `=`, `+`, `-`, `@` được thêm một dấu cách đầu).

## Kế hoạch ngắn (trước khi sửa)

1. Thay hàm `ask_website` chỉ-đọc của T-101 bằng nút **đọc**: `post_statuses` → `website.check_website` với đúng kết quả đó; giữ cột «Trên website» của T-101 (chỉ để xem).
2. Khung mới: cảnh báo, bảng thay đổi qua `safe_rows`, ô tick không tick sẵn, nút **ghi** riêng → `website.apply_website_changes`; lần kiểm cũ thì khóa nút ghi; bắt mọi lỗi thành câu cố định.
3. `website.LATE_AFTER` thay hằng riêng ở `plan.py`, `home.py`; giờ dùng `settings.now()`.
4. Trang Kết nối: ô Tên, Slug của bảng chuyên mục/thẻ qua `safe_text`.
5. Grep nơi gọi và test ghim hành vi cũ (nhãn nút, câu chú thích cột, hằng 15 phút, bảng chuyên mục): không test cũ nào ghim nhãn nút «🌐 Trạng thái trên website», câu «chưa tự đổi», hằng `LATE_AFTER` của trang; bảng chuyên mục trong test cũ có tên mở đầu «M», «[», nên không đổi. Không phải đổi test cũ (không cần R5).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/plan.py` | Nút đọc `ask_website` (`:661`): hỏi website rồi `check_website`; khung `web_check_box` (`:742`): cảnh báo, bảng `web_rows` (`:704`), ô tick, «Chọn tất cả», nút ghi; `apply_web` (`:802`); `web_result_box` (`:831`); «Tải lại» bỏ lần kiểm (`forget_web_check`, `:656`); `cached_index` không tạo file cache (`:171`); `web_label` dùng `website.LATE_AFTER` (`:636`); nhãn nút đổi thành «🌐 Cập nhật trạng thái từ website» (câu báo của lõi gọi đúng tên này); chú thích cột «Trên website» nói có đường ghi |
| `app/views/home.py` | Bỏ hằng `LATE_AFTER` riêng, dùng `website.LATE_AFTER` và `settings.now()` (`:211`) |
| `app/views/wordpress.py` | `cell()` (`:34`): ô chữ qua `safe_text`; bảng chuyên mục/thẻ dùng `cell()` cho Tên, Slug (`:160`) |
| `tests/test_t113_website_status.py` | Mới: 14 ca |

Không sửa `seo_app/**`, `config/**`, `write.py`, `settings.py` (Họa Sĩ khác đang làm T-112 ở hai file đó).

## Đối chiếu yêu cầu phiếu và điều kiện Lá Chắn T-109

| Yêu cầu / điều kiện | Cách làm | Test |
|---|---|---|
| YC 1, đk 1a: nút đọc và nút ghi riêng, chỉ khi bấm; không tự chạy khi mở trang hay chạy lại | Đọc: nút `plan-web`. Ghi: nút `plan-web-write` trong khung riêng, chỉ có khi đã có lần kiểm. Không tick sẵn; «Chọn tất cả» là một lần bấm riêng của người dùng | `test_read_button_only_reads_and_nothing_is_preticked`, `test_pick_all_is_an_explicit_click`, `test_page_rerun_does_not_ask_website_again` (mở trang, chạy lại 2 lần: 0 lệnh website mới, 0 lệnh ghi Sheet) |
| Đk 1b, G2: truyền thẳng `post_statuses`, đúng mã đã hỏi, `sheet_id`, `now=settings.now()` | `check_website(plan, states, ids, sheet_id=settings.google_sheet_id, now=settings.now())`; `S.plan_web` (bộ đôi chữ) chỉ cho cột «Trên website» | `test_check_gets_real_states_and_settings` (giá trị là `PostState`, mã 501–503, mã Sheet, giờ có múi giờ) |
| YC 2, đk 1e: thay đổi (dòng, ô, cũ → mới, lý do), cảnh báo chữ thuần, qua `safe_text`; người dùng chọn từng thay đổi | Bảng `web_rows` qua `safe_rows` (`sync.safe_text`); cảnh báo của lõi (cả `ODD_CELL`, `UNSURE_ROW`) qua `show()` (`escape_markdown`); ô tick mỗi thay đổi, nhãn chỉ có số dòng, Mã bài, mã bài website (số) | `test_read_button_only_reads_and_nothing_is_preticked`, `test_write_only_ticked_changes` (chỉ dòng đã tick được ghi, dòng không tick giữ nguyên) |
| YC 3, đk 1c: lần kiểm cũ thì báo «kiểm lại»; Sheet đổi giữa chừng, lỗi mạng ra câu cố định | Giao diện khóa nút ghi khi lần kiểm quá `website.CHECK_MAX_AGE` (câu mời kiểm lại); lõi vẫn tự từ chối (`MSG_STALE`, `MSG_OTHER_SHEET`, `MSG_NO_COLUMNS`): giao diện hiện câu đó, bỏ lần kiểm để người dùng kiểm lại | `test_stale_check_blocks_write_and_asks_to_check_again`, `test_core_refusal_is_fixed_text_and_check_is_dropped`, `test_row_changed_elsewhere_is_conflict` (bảng xung đột), `test_sheet_error_while_writing_is_fixed_text` (mồi trong lời Google không hiện), `test_website_error_is_fixed_text` (mồi trong lời WordPress không hiện) |
| Đk 1d: client Google, WordPress mới mỗi lần bấm | `wordpress_client()`, `sheets_client()` của trang, tạo mới mỗi lần; phiên chỉ giữ `WebCheck`, `WebApplyResult` (dữ liệu) | (đọc mã) |
| Đk 1f: bắt `SheetsError`, `SheetPlanError`, `ValueError`, `WordPressError` | `ask_website`, `apply_web` | như YC 3 |
| YC 4, G1: dùng chung `website.LATE_AFTER` | `plan.py:636`, `home.py:211` | `test_late_constant_is_shared_with_core` (đọc mã: không còn `timedelta(minutes=15)`; đổi hằng của lõi thì nhãn «Lỡ lịch» đổi theo) |
| YC 5: bảng chuyên mục, thẻ trung hòa ô `=`, `+`, `-`, `@` | `cell()` → `safe_text` | `test_category_table_neutralizes_formula_cells` (`=HYPERLINK(…)`, `+1+1`, `@SUM(A1)`, `-x`, tab; ô thường giữ nguyên) |
| YC 6: không lùi T-101, T-102, T-109; mọi trang mở được | — | Mục Bằng chứng |
| W2, R3: không gửi gì lên WordPress | Chỉ `post_statuses` (GET) | `test_write_only_ticked_changes`, `test_read_button_only_reads…` (mọi request WordPress là GET) |
| LC-T094-28: ghi Sheet chỉ ô app được ghi, RAW | Lõi; test kiểm lại từ giao diện | `test_write_only_ticked_changes` (chỉ 3 cột Trạng thái, Ngày đăng thực tế, Cập nhật lúc; mọi lệnh `RAW`) |

## Bằng chứng

```
# Test liên quan: T-113 (mới), T-109 (lõi, Soi Lỗi), T-101 (3 file của tôi + Lá Chắn, Soi Lỗi),
# T-102 (4 file), mở mọi trang, trang Kết nối (T-044, T-031, T-085, T-088, T-093, T-106, T-108),
# trang Bài viết mở đầu (T-084 Soi Lỗi), kho nháp: 24 file. Kèm plugin dò mọi file mới trong
# data/ của worktree sau mỗi test.
$ PYTHONUTF8=1 uv run pytest tests/test_t113_website_status.py tests/test_t109_website_status.py \
    tests/test_soi_loi_t109.py tests/test_t101_plan_page.py tests/test_t101_home_page.py \
    tests/test_t101_settings_google.py tests/test_la_chan_t101.py tests/test_soi_loi_t101.py \
    tests/test_t102_publish.py tests/test_t102_formula_cells.py tests/test_soi_loi_t102.py \
    tests/test_la_chan_t102.py tests/test_app_pages.py tests/test_app_wordpress.py \
    tests/test_app_t044_safe_text.py tests/test_soi_loi_t044.py tests/test_soi_loi_t031.py \
    tests/test_soi_loi_t085.py tests/test_soi_loi_t088.py tests/test_la_chan_t093.py \
    tests/test_t106_trang_ket_noi.py tests/test_soi_loi_t106.py tests/test_soi_loi_t084.py \
    tests/test_app_drafts.py -q -rxXfs -p find_data_writer
2459 passed, 7 xfailed in 1282.86s (0:21:22)
# Code của commit nộp, 11:15 → 11:37 (giờ máy, `date`; máy đang chạy cả toàn bộ test trên main).
# 7 xfail có sẵn, của phiếu khác: SL-T102-1 × 3, LC-T102-1, SL-T106-1 × 2, SL-T108-1.
# Lượt trước đó (10:48 → 11:07, trước khi sửa cached_index): 2457 passed, 7 xfailed, 1 failed:
# test_soi_loi_t084.py::test_whole_settings_page_never_shows_env_values_or_paths. Chạy riêng ca đó
# trên cùng code: 1 passed; lượt cuối: qua. Hỏng oan vì máy bận (AppTest quá giờ chờ), không
# phải lỗi (phiếu không sửa trang Cài đặt).

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/plan.py app/views/home.py app/views/wordpress.py \
    tests/test_t113_website_status.py docs/team/reports/T-113-hoa-si.md
"results": {}
```

`uv run ruff format --check app/views/wordpress.py` báo một chỗ có từ trước (`st.success(...)` ở mục 1); phần tôi viết không bị báo.

**Thử làm hỏng code để xem test mới có bắt được không** (bản sao worktree, mỗi lần một chỗ, chạy `tests/test_t113_website_status.py`; script `mutate_t113.py` ở thư mục ghi chú chung, mục `T-113-hoa-si-scripts`):

| Chỗ làm hỏng | Kết quả |
|---|---|
| Ô tick tick sẵn | bắt được |
| Bỏ khóa nút ghi khi lần kiểm cũ | bắt được |
| Đưa bộ đôi chữ của cột «Trên website» vào `check_website` (G2) | bắt được |
| Hằng «Lỡ lịch» riêng ở trang Kế hoạch | bắt được |
| Hằng «Lỡ lịch» riêng ở trang Bài viết | bắt được |
| Ghi mọi thay đổi, không theo ô tick | bắt được |
| Tự hỏi website khi mở trang | bắt được |
| Không bắt lỗi lõi từ chối (`SheetPlanError`) | bắt được |
| Bảng chuyên mục/thẻ không trung hòa ô công thức | bắt được |
| Không làm hỏng gì | 14 qua |

**Không mở app thật:** khung mới chỉ hiện khi có kế hoạch từ Google Sheets và bài trên website, mà phiếu cấm khai báo Google, WordPress thật. Mọi đường đi qua client thật với website, Google giả (AppTest).

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–6 (bảng trên)
- [x] Test liên quan + `uv run ruff check .` (mục Bằng chứng); toàn bộ test do Chỉ Huy chạy khi gộp
- [x] Báo cáo `docs/team/reports/T-113-hoa-si.md`

## Rủi ro và điểm cần chú ý

- Bảng thay đổi lấy dòng từ danh sách đang hiện (có thể là bản lưu trên máy ≤ 5 phút). Lúc ghi, lõi đọc lại Sheet và so từng ô với bản đã xem, nên Sheet vừa đổi thì ra xung đột, không ghi nhầm.
- Chưa thử với website, Google Sheets thật (phiếu cấm); mọi đường qua client thật với website, Google giả.
- Ô chọn thẻ/chuyên mục ở mục «Tạo thử một bài nháp» của trang Kết nối vỡ nếu website trả tên thẻ không phải chữ (có từ trước; client thật luôn trả chữ). Không sửa (ngoài phạm vi), chỉ ghi lại.
- **Ghi xuống đĩa khi chỉ mở trang (tự tìm ra, đã sửa phần của trang Kế hoạch):** lượt test liên quan đầu tiên để lại `data/site_index.sqlite` thật trong worktree. Trang Kế hoạch (code T-101) mở kho cache bài đã đăng mỗi lần vẽ trang khi đã khai báo WordPress, mà mở kho là tạo file. Sửa: chưa có file thì không mở kho (`plan.py` `cached_index`), test `test_opening_plan_page_does_not_create_site_index`. Lượt test cuối chạy kèm plugin dò mọi file mới trong `data/` sau mỗi test: trang Kế hoạch không còn ghi; **còn 8 ca** ghi file này, đều ở `tests/test_soi_loi_t102.py` (5) và `tests/test_la_chan_t102.py` (3), đi qua bước Xuất bản của `write.py` (ngoài phạm vi phiếu, không sửa).

## Đề xuất

- **Thư Ký:** README «Kế hoạch và Google Sheets» thêm đoạn nút «Cập nhật trạng thái từ website» (tick rồi ghi, «Lỡ lịch» là gì, lần kiểm cũ quá 5 phút thì bấm lại).
- **Soi Lỗi hoặc Thợ Máy (phiếu nhỏ, nhắc lại đề xuất T-101):** fixture tự động trong `tests/conftest.py` trỏ `site_index.DEFAULT_SITE_INDEX_FILE` và `plan_cache.DEFAULT_PLAN_CACHE_FILE` sang thư mục tạm cho mọi test. Hôm nay 8 ca của T-102 (`test_soi_loi_t102.py`, `test_la_chan_t102.py`) ghi vào `data/` thật của thư mục chạy test. Lưu ý thêm: `write.py` giữ kho này qua `st.cache_resource` theo đường dẫn, nên trỏ đường dẫn lúc chạy test là đủ.

## Câu hỏi cho chủ dự án

Không có.

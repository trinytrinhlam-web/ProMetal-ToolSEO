# Báo cáo T-122 · Cache số liệu Search Console trong máy (Giai đoạn 6, đợt 1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-122](../tickets/T-122-cache-so-lieu-search-console.md) |
| Nhánh | `team/T-122`, từ `main` `a499a13`; commit mã và test `b9514f7` |
| Ngày nộp | 2026-11-04 (giờ máy, +07) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã có chỗ **lưu tạm trong máy** số liệu lấy từ Google Search Console. Nhờ vậy trang theo dõi (làm ở phiếu sau) mở ra là có ngay số liệu, không phải hỏi Google mỗi lần.
  - Chỗ lưu là file `data/search_cache.sqlite`, giữ số theo ngày của từng trang, từ khóa của từng kỳ và ngày đăng bài.
  - Xóa file thì lần bấm «Lấy số liệu mới» sau lấy lại được, vì Google giữ số liệu 16 tháng.
- File được kiểm kỹ mỗi lần đọc. Chỉ một con số sai, hay anh đổi thuộc tính Search Console hoặc địa chỉ website, là bỏ cả file, lấy lại từ đầu.
- Nếu thư mục `data` bị thay bằng lối tắt trỏ ra chỗ khác, phần mềm không ghi gì vào đó và báo câu tiếng Việt.
- Có trần dung lượng 64 MB. Website cỡ của anh dùng khoảng 13 MB khi đầy đủ 16 tháng.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/search_cache.py` | Mới. Gồm: `SearchCacheStore`, `CacheScope` (thuộc tính + `WORDPRESS_URL`, chỉ lưu mã băm), `CachedDay`, `CachedQuery` (đúng khuôn 3.1), `QueryRange`, `SearchCache` (kết quả đọc, có `final_end` tức E, `queries_for`, `has_range`). Lỗi trả ra `SearchCacheError` với câu cố định. Chi tiết ở các mục dưới |
| `tests/test_search_cache.py` | Mới, 133 ca (132 qua, 1 bỏ qua trên Windows): ghi, đọc, nối đoạn, giữ 16 tháng, trần, phạm vi, file bị sửa tay (41 kiểu), cấu trúc lạ (5 kiểu), liên kết, file bận, SQL chỉ dùng tham số |
| `docs/team/reports/T-122-tho-may.md` | Báo cáo này |

Không sửa file nào có sẵn. Không nhập `seo_app/tracking` (nhánh T-123 chưa gộp). Không thêm thư viện; chỉ dùng `sqlite3` có sẵn của Python.

**Hàm chính:**

| Hàm | Việc |
|---|---|
| `load(scope)` | Đọc toàn bộ cache của phạm vi, kiểm từng dòng. Trả `None` khi: chưa có gì; cache hỏng, lạ; cache của phạm vi khác (đã bỏ file). Ném `SearchCacheError` khi: `data/` là liên kết; file đang bận; lỗi đọc |
| `save_days(scope, rows, *, start, end, first_provisional, fetched_at, today)` | Thay trọn số liệu của một đoạn ngày (≤ 31 ngày, một lệnh Q1). Bỏ ngày cũ hơn 486 ngày. Mọi việc trong một giao dịch |
| `save_queries(scope, rows, *, start, end, fetched_at, truncated)` | Ghi một khoảng từ khóa (≤ 93 ngày, một lệnh Q2). Lấy lại khoảng đã có thì thay. Giữ 6 khoảng mới lấy nhất |
| `save_post_dates(scope, dates, *, keep=None)` | Ghi ngày đăng (giờ PT) theo mã bài. `keep`: mã các bài còn trong danh sách đã đăng; bài khác bị bỏ |
| `clear()` | Xóa file |

## Khớp với hai `Protocol` của T-123

Hai dataclass `frozen` của phiếu này **trùng tên trường, đúng thứ tự** với khuôn 3.1, cũng là hai `Protocol` `CachedDayLike`, `CachedQueryLike` ở `seo_app/tracking/model.py` (nhánh `team/T-123`):

| Kiểu | Trường | Kiểu giá trị khi đọc ra |
|---|---|---|
| `CachedDay` | `day`, `page`, `clicks`, `impressions`, `position_sum`, `final` | `date` thuần (không `datetime`), `str`, `int`, `int`, `float`, `bool` thật |
| `CachedQuery` | `start`, `end`, `page`, `query`, `clicks`, `impressions`, `position_sum` | `date`, `date`, `str`, `str`, `int`, `int`, `float` |

- Cột `final` là `INTEGER` trong SQLite; khi đọc, chỉ nhận đúng `0`/`1` rồi đổi sang `bool`. Ngày lưu dạng `YYYY-MM-DD`, đọc ra `date`.
- Đó đúng là hai điều kiện T-123 đòi: T-123 bỏ những dòng có `final` không phải `bool` hay `day` không phải `date`.
- `test_round_trip_types_match_tracking_protocols` kiểm tên trường, thứ tự và kiểu từng giá trị đọc ra.
- Hai phiếu chưa gộp nên chưa thử chung. Phép thử chung (`CachedDay` thật → `match.build_tracking`, `CachedQuery` thật → `keywords.keyword_table`) để ở T-124 như Chỉ Huy dặn.

## Chỗ thiết kế để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Tên file: phiếu ghi `search_cache.sqlite`, thiết kế 3.1 ghi `search_console.sqlite` | Theo phiếu: `data/search_cache.sqlite` | Khớp tên module, như `site_index.py` → `site_index.sqlite` |
| 2 | Cột `start`, `end` của `query_range` | Đặt tên `start_day`, `end_day` | `END` là từ khóa SQL. Tên trường của `CachedQuery` vẫn là `start`, `end` |
| 3 | E (ngày chốt cuối) | Thêm khóa `first_provisional` trong `info`: ngày đầu tiên còn là số tạm, đi theo đoạn mới nhất. `SearchCache.final_end` = ngày trước ngày đó (hay `covered_end`) | Nếu chỉ dựa vào cờ `final` của từng dòng: ngày tạm không có lượt hiển thị nào thì không có dòng, E bị tính lố, ngày tạm số 0 bị đếm như ngày đã chốt |
| 4 | Thứ tự ghi đoạn | Chỉ nhận một trong ba trường hợp: (a) cache trống; (b) đoạn mới nhất: bắt đầu không muộn hơn ngày sau `covered_end` và không muộn hơn ngày tạm đầu tiên, kết thúc từ `covered_end` trở đi; (c) đoạn nằm trọn trong phần đã chốt, không có số tạm. Khác thì báo `MSG_BAD_RANGE`, không ghi | Đúng luồng 1.3 (ghi từ cũ tới mới, lần sau lấy từ ngày tạm đầu tiên). Giữ được: phần đã lấy luôn liền mạch, số tạm luôn ở cuối |
| 5 | Địa chỉ trùng sau khi bỏ `#…` | Cache tự bỏ `#…` rồi cộng dồn trong cùng ngày (cùng khoảng, với từ khóa) | Khóa chính `(day, page)` không cho hai dòng trùng. Đặt ở cache thì T-124 không thể quên |
| 6 | Từ khóa chưa làm sạch | Từ chối (không tự làm sạch): phải `clean_text(q) == q`, 1–200 ký tự | Làm sạch là việc của client T-121 (thiết kế 2.4). Cache chỉ kiểm, để lỗi lộ ra sớm |
| 7 | Phạm vi khác | `load` bỏ hẳn file, không chỉ trả `None`. Ghi với phạm vi khác thì xóa mọi bảng trong cùng giao dịch rồi mới ghi | Ghi theo đoạn: nếu chỉ ghi đè thì số liệu phạm vi cũ còn lẫn trong các đoạn khác |
| 8 | Lỗi khi đọc | `None` cho trống, hỏng, phạm vi khác. `SearchCacheError` câu cố định cho `data/` là liên kết, file bận, lỗi đọc | Để giao diện báo đúng nguyên nhân thay vì «chưa có số liệu» |
| 9 | File hỏng lúc đang ghi | Bỏ file rồi thử lại **một lần** trên file mới | Dữ liệu đang ghi vẫn đúng; cache hỏng thì vốn sẽ bị bỏ |
| 10 | Trần 64 MB | Đo `page_count × page_size` trong giao dịch, trước khi ghi xong. Quá trần thì hoàn tác | Không dùng `PRAGMA max_page_count`, vì lệnh đó phải ghép số vào câu SQL; mọi câu SQL ở đây là chữ cố định |
| 11 | Giữ 16 tháng | Theo `today` (giờ PT) nơi gọi truyền vào; hàm không tự đọc đồng hồ | Test được; T-124 đã có «hôm nay PT» |
| 12 | Năm hợp lệ | 2000–2200 cho mọi ngày, mốc giờ | Như T-123; cộng trừ quanh khoảng này không bao giờ tràn `date` (LC-T120-10) |

## Bằng chứng

```
# Trên đúng commit b9514f7 (git status sạch), Windows 11, Python 3.12.15
$ uv run pytest tests/test_search_cache.py -q -rs
SKIPPED [1] tests\test_search_cache.py:754: máy này không cho tạo symlink file (Windows cần quyền
            Developer Mode)
132 passed, 1 skipped in 13.70s

$ uv run ruff check .                        # ruff 0.16.10, toàn repo
All checks passed!

# Quét bí mật, PYTHONUTF8=1, 2 file mới
$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/storage/search_cache.py tests/test_search_cache.py
results: {}
# Đối chứng: bản sao search_cache.py thêm một khóa giả, ở thư mục nháp → bắt được (Secret Keyword).
# Đã xóa bản sao.

# Đo (script ở thư mục nháp; đếm số bước bằng bộ đếm thay cho _guard)
# Website thiết kế ước tính: 486 ngày × 200 trang, 6 khoảng × 5.000 từ khóa
dòng ngày 97,200; dòng từ khóa 30,000; file 13.0 MB (trần 64 MB)
ghi 16 đoạn ngày 6.2 s; đọc toàn bộ 1.14 s
số bước máy ảo mỗi kết nối khi đọc: 1,911,000 (kiểm file) · 0 · 2,874,000 (đọc)   (trần 400,000,000)
# Lớn nhất: 486 ngày × 617 trang, 6 khoảng × 50.000 từ khóa
khoảng 6: không lưu (… đã tới mức tối đa nên không lưu thêm phần này …)   ← trần 64 MB chặn đúng
dòng ngày 299,862; dòng từ khóa 250,000; file 60.1 MB
đọc toàn bộ 6.59 s; số bước: 8,263,000 · 0 · 15,797,000   (dưới 4% trần)
```

## Đối chiếu tiêu chí xong

- [x] **Yêu cầu 1:** bảng và kiểu đúng mục 3.1, thêm khóa `first_provisional` (chỗ #3). Các ca:
  - ghi theo đoạn trong một giao dịch: `test_chunks_extend_coverage_and_track_provisional_days`, `test_older_final_chunk_inside_coverage_is_replaced`; lỗi thì không ghi gì: `test_bad_rows_are_refused_and_nothing_is_written`, `test_chunk_must_join_the_stored_range`;
  - giữ 16 tháng: `test_retention_keeps_16_months`, `test_too_old_cache_restarts_from_new_chunk`;
  - ≤ 6 khoảng từ khóa: `test_query_ranges_replace_and_keep_newest_six`;
  - trần: `test_day_row_cap`, `test_query_row_cap`, `test_file_size_cap_refuses_write`.
- [x] **Yêu cầu 2:** một dòng sai là bỏ cả cache: `test_one_bad_value_drops_the_whole_cache`, 41 kiểu sửa tay (số, ngày, địa chỉ, cờ `final`, `info`, khoảng, từ khóa, ngày đăng). Đổi thuộc tính hay `WORDPRESS_URL` là bỏ cache: `test_other_scope_drops_the_cache_on_load`, `test_other_scope_wipes_old_data_on_save`
- [x] **Yêu cầu 3:** `data/` là liên kết (junction thật trên Windows) thì `load`, ghi, `clear` đều báo `MSG_DATA_DIR_LINK`, thư mục đích vẫn trống (`test_data_dir_link_is_never_opened`). Hard link ở chỗ file, `-journal`, `-wal` thì chỉ bị gỡ, file ngoài giữ nguyên (`test_hard_link_at_cache_path_is_removed_not_followed`)
- [x] **Yêu cầu 4:** năm kiểm trước khi đổi múi giờ, cộng trừ; không lọt `OverflowError`, `ValueError`. Khi ghi: `test_bad_chunk_arguments_give_fixed_message` (năm 1, `date.max`, giờ năm 1 và 9999, giờ không múi giờ). Khi đọc: `gio-nam-1`, `gio-nam-9999`, `phan-da-lay-nam-1`, `tam-nam-1`, `ngay-nam-9999` trong `test_one_bad_value_drops_the_whole_cache`; ca đối chứng `test_fetched_at_year_is_checked_before_converting` cho thấy đổi thẳng thì ra `OverflowError`
- [x] **LC-T120-9:** kiểm như `plan_cache`, đủ các ca sau:
  - `sqlite_master` khớp đúng, kiểm trong cùng giao dịch; bảng, khung nhìn, trigger, chỉ mục lạ hay mất bảng thì bỏ (`test_schema_changes_drop_the_cache`);
  - file không phải SQLite, quá lớn thì bỏ (`test_not_a_database_is_dropped_then_write_works`, `test_too_large_file_is_dropped`);
  - SQL chỉ là chữ cố định với tham số `?`, không f-string hay `.format` (`test_sql_only_uses_constant_text_and_parameters`, đọc mã nguồn);
  - không lưu thuộc tính, chỉ mã băm (`test_file_keeps_no_property_or_secret`).
- [x] **LC-T120-10:** như yêu cầu 4
- [x] **LC-T120-15:** test không gọi mạng (bộ chặn của `conftest.py`). Các ca biên của mục 2.4 với dữ liệu ghi vào và đọc ra:
  - số: `bool`, số thực, `NaN`, vô cực, âm, click lớn hơn hiển thị, hiển thị 0, quá 10⁹, vị trí 0 hay dưới 1;
  - địa chỉ: staging, `www.`, `http://`, tên miền khác, quá 2.000 ký tự;
  - từ khóa: chưa làm sạch, rỗng, quá 200 ký tự.
- [x] Test liên quan, `uv run ruff check .` qua. Không sửa hàm dùng chung nào
- [x] Báo cáo này
- [ ] Toàn bộ `uv run pytest`: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Thời gian đọc.** Đọc là kiểm **từng dòng**, đúng chủ ý «một dòng sai là bỏ cả cache».
  - Website cỡ thiết kế ước tính (97.200 dòng ngày): khoảng 1,1 giây. Khi dồn đủ trần (300.000 dòng ngày, 250.000 dòng từ khóa): khoảng 6,6 giây.
  - Giao diện nên đọc một lần rồi giữ trong phiên (xem Đề xuất).
- **Mỗi lần mở chạy `quick_check`** (như `plan_cache`); đã tính trong số đo trên.
- **Ghi đoạn sai thứ tự bị từ chối** (`MSG_BAD_RANGE`). T-124 phải ghi từ cũ tới mới; lần sau bắt đầu đúng từ ngày tạm đầu tiên, hay ngày sau `covered_end` khi không còn số tạm.
- **Đồng hồ máy bị chỉnh lùi.** Nếu `covered_end` sau «hôm nay PT», đoạn mới không thỏa luật nối nên bị từ chối. T-124 nên gọi `clear()` rồi lấy lại 16 tháng.
- **Liên kết đặt vào đúng lúc** giữa lần kiểm và lần mở thì không chặn được, như mọi kho khác (`data_dir.py` đã ghi). Cần ghi được vào thư mục cài app mới làm được việc này.
- **Ca symlink file chỉ chạy trên Mac/Linux.** Trên Windows nó bị bỏ qua vì tạo symlink file cần quyền Developer Mode. Junction và hard link đã chạy thật trên Windows.
- **Hai tab cùng ghi:** tab sau chờ 1 giây rồi báo «đang bận». Không có gì hỏng. Khóa «chỉ một lần lấy cùng lúc» (LC-T120-22) là việc của T-124.

## Đề xuất

- **T-124 (lấy số liệu):**
  - Ghi đoạn từ cũ tới mới. Lấy E từ `SearchCache.final_end`; ngày bắt đầu lần sau là `first_provisional` hay `covered_end + 1`. Gặp `covered_end` sau hôm nay thì `clear()`.
  - Truyền `first_provisional` của từng đoạn: `first_incomplete_date`, hay 3 ngày cuối của đoạn mới nhất khi thiếu `metadata`.
  - Dùng `fetched_at` trong cache cho mốc «vừa lấy lúc …» (LC-T120-22, dùng chung các tab).
  - Thêm một ca dùng `CachedDay`, `CachedQuery` thật của phiếu này với `seo_app.tracking`.
- **T-125 (giao diện):**
  - Bắt `SearchCacheError` khi đọc và hiện câu của nó.
  - Giữ `SearchCache` đã đọc trong `st.session_state`, kèm giờ sửa và cỡ file; chỉ đọc lại khi hai giá trị đó đổi, để không mất khoảng 1 giây mỗi lần bấm.
- **Soi Lỗi:** các ca thêm nên thử:
  - file ở chế độ WAL do chương trình khác đặt;
  - `-journal` còn sót sau khi app tắt ngang;
  - ghi xen kẽ `save_days` và `save_queries` từ hai tab;
  - đoạn rỗng (không có dòng nào) giữa phần đã lưu.

## Câu hỏi cho chủ dự án

Không có.

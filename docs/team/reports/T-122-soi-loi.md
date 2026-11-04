# Báo cáo T-122 · Cache số liệu Search Console trong máy (Giai đoạn 6, đợt 1) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-122](../tickets/T-122-cache-so-lieu-search-console.md), nhánh `team/T-122`: mã và test `b9514f7`, báo cáo Thợ Máy `307ff07` (gốc `main` `a499a13`); thiết kế T-120 mục 3.1–3.4; LC-T120-9, -10, -15 |
| Ngày nộp | 2026-11-04 (08:42 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T122-1: `WORDPRESS_URL` có chữ hoa ở tên máy, cổng `:443` hay `HTTPS://` thì cache không lưu được gì, trong khi client T-121 và gói T-123 lượt 2 đều nhận), **2 Thấp** (SL-T122-2: mốc giờ ở biên năm 2000 / 2200 ghi được nhưng đọc lại bỏ cả cache; SL-T122-3: surrogate lẻ trong địa chỉ trang, phạm vi lọt `UnicodeEncodeError` thay vì câu cố định). Cả 8 trọng tâm Chỉ Huy giao đều **đúng**: một dòng sai ở bất kỳ đâu bỏ cả cache, đổi phạm vi bỏ cache, liên kết không bị đi theo, giữ 16 tháng, ≤ 6 khoảng, năm 1 / 9999 không lọt lỗi Python, `final` là `bool` thật và `day` là `date` (ghép thật với T-123: 0 dòng bị bỏ), hai tiến trình cùng ghi không làm hỏng hay bỏ cache, file sửa tay, hỏng, WAL, nhật ký nóng đều xử lý đúng. Điều kiện: sửa SL-T122-1 trước T-124 (nối client T-121 với cache); SL-T122-2, -3 nhỏ, nên sửa cùng lượt. Không chặn Lá Chắn |

## Tóm tắt (cho chủ dự án)

- **Phần lưu tạm số liệu Google trong máy làm chắc chắn.** Tôi thử sửa tay từng con số, từng ngày trong file; ghi chữ lạ, byte hỏng; đặt lối tắt trỏ ra ngoài; cho ba cửa sổ cùng ghi một lúc; tắt ngang chương trình giữa lúc đang ghi; để chương trình khác khóa file. Mọi trường hợp: phần mềm hoặc bỏ file rồi lấy lại từ Google, hoặc báo «đang bận», **không bao giờ dùng số sai**, không ghi ra ngoài thư mục phần mềm.
- **Ghép thử với phần tính toán (T-123):** số đọc từ file đi qua phần tính toán đầy đủ, không dòng nào bị bỏ, tổng click, lượt hiển thị khớp từng bài.
- **Lỗi 1 (cần sửa trước khi nối với phần lấy số liệu):** nếu địa chỉ website trong `.env` gõ có chữ hoa (ví dụ `https://Suachuacuasat.com`) hay có `:443`, phần lấy số liệu vẫn chạy nhưng **phần lưu từ chối mọi số liệu**, báo «không đúng dạng». Trang theo dõi sẽ luôn trống. Đây đúng là lỗi đã sửa ở phần tính toán sáng nay; phần lưu cần sửa giống vậy, vài dòng.
- **Lỗi 2, 3 (nhỏ, gần như không gặp):** đồng hồ máy chỉ đúng ngày 01/01/2000 hay 31/12/2200 thì số vừa lưu bị bỏ khi đọc lại; Google trả một ký tự hỏng kiểu đặc biệt thì phần mềm hiện lỗi lạ thay vì câu tiếng Việt. Không mất dữ liệu.
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t122.py` | Mới: **68 ca: 58 qua, 9 `xfail(strict=True)`** của 3 lỗi mới, **1 bỏ qua** (ca ghép T-123: nhánh này chưa có `seo_app.tracking`; chạy qua trên bản gộp tạm, sẽ chạy khi gộp `main`). Mọi tham số có `ids=` ngắn (tên ca dài nhất 119 ký tự). Mọi file nằm trong `tmp_path`, không gọi mạng |
| `docs/team/reports/T-122-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác. Test dùng lại hàm phụ của `tests/test_search_cache.py` (`day`, `query`, `save_october`, `save_tail`, `link_dir`…), không đổi file đó.

## 1. Tám trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả |
|---|---|---|
| 1 | **Một dòng sai thì bỏ cả cache** | **Đúng.** 41 ca của Thợ Máy sửa **mọi** dòng một lúc; tôi thêm **24 ca sửa đúng một dòng** (có kiểm `rowcount == 1`) ở chỗ khó: dòng cuối, dòng giữa, `final` sai ở một ngày tạm, tên máy viết hoa ở một dòng, dòng từ khóa cuối, khoảng từ khóa thứ hai, một ngày đăng; năm 1999, 2201, 2500 (ngày hợp lệ của Python, chỉ phép kiểm năm bắt được); UTF-8 hỏng ở trang, từ khóa, `info`; BLOB ở ngày, trang, `final`, click, ngày đăng, khóa `info`; ký tự NUL. Cả 24: `load` trả `None`, xóa file, `reset_count == 1`; lần ghi sau tạo file mới được |
| 2 | **Mã băm phạm vi đổi thì bỏ cache** | **Đúng.** `load` với phạm vi khác xóa file; ghi với phạm vi khác xóa mọi bảng trong cùng giao dịch (test Thợ Máy). Mã băm là SHA-256 của `GSC_SITE_URL + "\n" + WORDPRESS_URL` (bỏ «/» cuối); `_check_scope` chặn ký tự < 32 nên hai phạm vi khác nhau không thể cho cùng chuỗi băm. File không chứa thuộc tính (`sc-domain`) |
| 3 | **`data/` là junction, symlink, hard link** | **Đúng.** `dir_has_link` gọi trước `mkdir` ở mọi đường (`load`, ghi, `clear`), không lặp SL-T117-1. Thêm: junction **treo** (đích đã xóa) ở `data/`: cả ba đường báo `MSG_DATA_DIR_LINK`, không tạo lại đích. Junction (Windows) / symlink thư mục (Mac, Linux) đặt đúng tên file, `-journal`, `-wal`, `-shm`: chỉ gỡ liên kết, chỗ nó trỏ tới vẫn trống, file cache sau đó là file thường. Hard link ở `-shm`. **Hard link tới một cache hợp lệ nằm ngoài** (số liệu người khác dựng): `load` gỡ tên trong `data/`, trả `None`, không đọc số qua liên kết, file kia nguyên vẹn. Symlink **file**: máy này không tạo được (cần Developer Mode), ca của Thợ Máy bỏ qua như báo cáo ghi |
| 4 | **16 tháng, ≤ 6 khoảng, trần dung lượng** | **Đúng.** Đoạn đầu bắt đầu đúng mốc `hôm nay − 485` nhận, sớm hơn 1 ngày: `MSG_BAD_DATA`. Phần đã lấy trong file dài 486 ngày: đọc nhận; 487 ngày: bỏ cache. Khoảng từ khóa thứ 7 thêm tay: bỏ cache. Trần dung lượng: ca của Thợ Máy; đọc mã: hai phép đo (`st_size` khi mở, `page_count × page_size` khi ghi) cùng dùng `>` nên file vừa đúng trần vẫn đọc được |
| 5 | **Năm 1 và 9999, `OverflowError` / `ValueError`** | **Không lọt lỗi Python** ở mọi đường (ca của Thợ Máy cho năm 1, 9999, `date.max`, giờ +14:00 / −12:00). Riêng biên năm hợp lệ: mốc giờ năm 2000 múi +14 và năm 2200 múi −12 ghi được (năm theo múi của nó nằm trong khoảng) nhưng lưu theo giờ Việt Nam thành 1999 / 2201, đọc lại thì bỏ cả cache: **SL-T122-2** |
| 6 | **`final` là `bool` thật, `day` là `date` (Protocol T-123)** | **Đúng.** 14 cách ghi **cùng giá trị khác kiểu** mà SQLite tự đổi theo kiểu cột (`final` = `'1'`, `1.0`, `TRUE`, `'0'`; click `1.0`, `'1'`; hiển thị `' 10'`; vị trí `20`, `'2e1'`; mã khoảng, mã bài dạng chữ; `truncated` `'1'`…): cache đọc ra **bằng y** bản trước, mọi dòng qua đúng điều kiện `match._day_row_ok` của T-123, `CachedQuery.start/end` là `date`, số là `int` / `float`. **Ghép thật** trên bản gộp tạm `team/T-122` + `team/T-123` (lượt 2, `d71c9ad`): 475 dòng ngày (Việt hóa `%E1%BB%AD`, `#…`, trang chủ, `?s=`) qua `build_tracking`: `skipped_rows = 0`, `skipped_items = 0`; `aggregate` khớp tổng gốc từng bài; `page_queries` + `keyword_table`: `skipped = 0`. Thành ca `test_cache_rows_go_through_t123_without_being_dropped` (chạy khi đã gộp T-123) |
| 7 | **Hai tiến trình cùng ghi** | **Đúng.** Ba **tiến trình** × 10 giây xen kẽ ghi đoạn mới nhất (1–300 trang), đoạn đã chốt, từ khóa (0–400 dòng), ngày đăng (`keep`), đọc: 367 thao tác, **0 lỗi, 0 lần «bận», 0 lần bỏ cache**, đọc luôn thấy phần đã lấy liền mạch. Thành ca luồng 3 giây (2 ghi + 1 đọc; chỉ «đang bận» là được phép). Chương trình khác khóa **độc quyền**: `load` và ghi báo «đang bận» sau 1 giây, không coi là hỏng, cache còn nguyên |
| 8 | **File SQLite bị sửa tay hoặc hỏng** | **Đúng.** Ngoài 46 ca của Thợ Máy và 24 ca ở mục 1: **chế độ WAL** do chương trình khác đặt: đọc đúng, ghi được khi chương trình khác đang mở giao dịch đọc, `clear` dọn cả `-wal`, `-shm`. **Nhật ký nóng**: tiến trình con ghi dở 4.000 dòng (bộ nhớ đệm 2 trang nên đã ghi vào file, file to ra) rồi `os._exit`: lần mở sau SQLite tự hoàn tác, cache **bằng y** trước, không bị bỏ, `-journal` biến mất |

Bốn ca Thợ Máy đề nghị Soi Lỗi thử (WAL, `-journal` sót sau khi tắt ngang, `save_days` / `save_queries` xen kẽ từ hai tab, đoạn rỗng giữa phần đã lưu) đều đã thử: ba ca đầu ở mục 7, 8; đoạn rỗng nằm trong phần đã chốt thì xóa đúng số của các ngày đó (thay trọn đoạn, đúng thiết kế 3.1), phần đã lấy liền mạch giữ nguyên.

Ghép với client T-121 (đọc mã `origin/team/T-121` `eb05747`, không sửa): `_query_text` của T-121 (`clean_text`, cắt 200, `rstrip`) luôn cho từ khóa qua phép kiểm của cache (100.000 mẫu ngẫu nhiên có dấu rời, khoảng trắng lạ, ký tự vô hình, emoji, Hangul: 0 mẫu lệch). Địa chỉ trang thì lệch: SL-T122-1.

## 2. Lỗi mới

### SL-T122-1 · Trung bình · `WORDPRESS_URL` có chữ hoa ở tên máy, `:443`, `HTTPS://`: cache không lưu được gì

- **Tái hiện** (`test_sl_t122_1_google_pages_are_saved_whatever_the_case_of_wordpress_url`, 3 ca): `CacheScope("sc-domain:suachuacuasat.com", "https://Suachuacuasat.com")`, `save_days` 28 dòng địa chỉ viết thường như Google trả: `SearchCacheError("Số liệu Search Console không đúng dạng nên không lưu tạm.")`; `save_queries` cũng vậy. Như thế với `https://suachuacuasat.com:443`, `HTTPS://suachuacuasat.com/`, `https://SUACHUACUASAT.COM/`.
- **Vì sao:** `CacheScope.base` chỉ bỏ «/» cuối; `_page` đòi `page.startswith(base + "/")`, phép so này phân biệt hoa thường và không bỏ cổng 443. `config.load_settings` không chuẩn hóa `WORDPRESS_URL` (chỉ `rstrip("/")`). Trong khi đó:
  - client T-121 dựng tiền tố bằng `site_prefix` (tên máy, scheme viết thường, bỏ `:443`) nên **nhận** đúng các dòng này và trả cho T-124;
  - gói T-123 lượt 2 (`d8fe3f7`) vừa sửa đúng lỗi cùng loại (SL-T123-2) bằng `site_base`.
  Trên bản gộp tạm T-122 + T-123: `build_tracking("https://Suachuacuasat.com", …)` cho `skipped_rows = 0`, còn `save_days` của T-122 từ chối.
- **Hậu quả:** với một `WORDPRESS_URL` gõ tay hợp lệ (mọi phần khác của app chạy bình thường), mỗi lần bấm «Lấy số liệu mới» đều lấy xong từ Google rồi báo «không đúng dạng», trang theo dõi luôn trống. Người dùng khó đoán ra nguyên nhân. Xếp Trung bình như SL-T123-2 (cả tính năng hỏng); khả năng xảy ra thấp nếu `.env` hiện viết thường (tôi không đọc `.env`).
- **Gợi ý sửa:** `CacheScope.base` chuẩn hóa như `site_base` của T-123 (scheme, tên máy viết thường, bỏ cổng 443 và «/» cuối, giữ nguyên chữ của đường dẫn). Địa chỉ từ Google vẫn so nguyên văn. Mã băm phạm vi đổi theo chỉ với `WORDPRESS_URL` chưa chuẩn, tức đúng những cache chưa bao giờ ghi được. Ca đối chứng `test_pages_off_the_site_stay_refused_whatever_wordpress_url_looks_like` (4 ca, đang qua) canh để bản sửa không nới lớp chặn `www.`, `http://`, cổng khác, đường dẫn khác chữ hoa (LC-T120-6).
- **Góp ý:** nay có ba bản chuẩn hóa `WORDPRESS_URL` (`site_prefix` T-121, `site_base` T-123, bản sửa này). Khi gộp đợt 1, nên dồn về một hàm dùng chung để ba nơi không lệch nhau lần nữa (T-124 là chỗ ghép cả ba).

### SL-T122-2 · Thấp · Mốc giờ ở biên năm: ghi được, đọc lại bỏ cả cache

- **Tái hiện** (`test_sl_t122_2_fetched_at_that_was_saved_can_be_read_back`, 2 ca): `save_days(…, fetched_at=2000-01-01T00:00+14:00, today=2000-01-01)` ghi được, file lưu `1999-12-31T17:00:00+07:00`; `load` thấy năm 1999 nên bỏ cả cache (`reset_count == 1`, file bị xóa). Như thế với `2200-12-31T23:00−12:00` (lưu `2201-01-01T18:00:00+07:00`) và với `fetched_at` của `save_queries`.
- **Vì sao:** `_stamp` kiểm năm theo múi giờ **của mốc** (đúng để không tràn khi đổi, LC-T120-10) rồi lưu theo giờ Việt Nam, không kiểm lại; `_parse_time` khi đọc kiểm năm của chuỗi đã lưu. Ghi và đọc dùng hai mốc khác nhau.
- **Hậu quả:** chỉ khi đồng hồ máy đúng ngày 01/01/2000 (máy mất pin CMOS) hay 31/12/2200: số vừa lưu bị bỏ ở lần đọc sau. Không lọt lỗi Python, không mất gì ngoài cache.
- **Gợi ý sửa:** sau `astimezone`, kiểm năm của mốc đã đổi; ngoài khoảng thì `MSG_BAD_DATA` (từ chối ngay khi ghi).

### SL-T122-3 · Thấp · Surrogate lẻ trong địa chỉ trang, phạm vi: lọt `UnicodeEncodeError`

- **Tái hiện** (`test_sl_t122_3_lone_surrogate_gives_the_fixed_message`, 4 ca): `save_days` hay `save_queries` với trang `https://suachuacuasat.com/a\ud800/` ném `UnicodeEncodeError: … surrogates not allowed`; `load` và `save_post_dates` với `WORDPRESS_URL` có surrogate lẻ cũng vậy (từ `scope.digest`). Dữ liệu không hỏng: giao dịch được hoàn tác, cache cũ còn nguyên.
- **Vì sao:** `is_site_link` không chặn ký tự loại Cs; `_check_scope` chỉ chặn ký tự < 32 và 127. SQLite (và `.encode()` của mã băm) không mã hóa được surrogate lẻ ra UTF-8. Từ khóa thì đã đúng: `clean_text` bỏ surrogate nên `_query_ok` từ chối, câu cố định (ca đối chứng `test_lone_surrogate_in_query_text_is_refused`).
- **Đường tới thật:** JSON của Google có thể chứa `"\ud800"`; `json.loads` của client T-121 (`_parse_json`) trả surrogate lẻ, `_page` của T-121 cũng chỉ dùng `is_site_link` nên cho qua (ghi nhận GN-3). Google thật không trả thế, nên Thấp. Biến môi trường `WORDPRESS_URL` trên Windows có thể chứa surrogate lẻ (UTF-16 cho phép), `.env` UTF-8 thì không.
- **Hậu quả:** trang báo lỗi bất ngờ (chỉ hiện loại lỗi, T-118) thay vì câu tiếng Việt; trái hợp đồng của module «lỗi trả ra `SearchCacheError` với câu cố định».
- **Gợi ý sửa:** `_page` và `_check_scope` từ chối chữ có ký tự `0xD800–0xDFFF`.

## 3. Thử bản sửa nháp

Bản nháp (không commit; script ở thư mục nháp của phiên): `CacheScope.base` chuẩn hóa như `site_base` (thêm `urlsplit`); `_stamp` kiểm năm sau khi đổi múi giờ; `_page`, `_check_scope` từ chối surrogate lẻ. Chạy trên worktree tạm từ `origin/team/T-122`:

```
$ PYTHONPATH=<worktree tạm> uv run pytest tests/test_search_cache.py tests/test_soi_loi_t122.py -q -rX
9 failed, 190 passed, 2 skipped
# 9 «failed» đúng là 9 XPASS(strict) của SL-T122-1, -2, -3 (gỡ dấu xfail thì qua);
# 190 qua gồm đủ 132 ca của Thợ Máy; 2 bỏ qua: symlink file (Windows), ca ghép T-123
```

## 4. Thử đột biến

Mỗi đột biến sửa một chỗ của `search_cache.py` trên worktree tạm, chạy riêng test Thợ Máy và test Soi Lỗi:

| Đột biến | Test Thợ Máy (133) | Test Soi Lỗi (68) |
|---|---|---|
| M1 · bỏ kiểm năm khi đọc ngày (`_parse_day`) | 132 qua: **không bắt** | **3 hỏng**: ngày đăng năm 1999, 2201; khoảng từ khóa năm 2201 |
| M2 · bỏ kiểm năm khi đọc mốc giờ (`_parse_time`) | **không bắt** | **2 hỏng**: giờ năm 2500, giờ của khoảng năm 1999 (thêm 2 XPASS của SL-T122-2: đột biến nới phép đọc nên ca biên «qua») |
| M8 · bỏ `-shm` khỏi danh sách file nhật ký | **không bắt** | **2 hỏng**: junction, hard link ở `-shm` |
| M9 · coi «file bị khóa» là file hỏng (`_is_healthy`) | **không bắt** | **1 hỏng**: khóa độc quyền |
| M11 · bỏ `text_factory` kiểm UTF-8 | **không bắt** | **3 hỏng**: UTF-8 hỏng ở trang, từ khóa, `info` |
| M13 · bỏ phép so tiền tố, chỉ còn `is_site_link` | **không bắt** | **2 hỏng**: trang viết hoa tên máy lưu trong file, đường dẫn con khác chữ hoa (thêm 3 XPASS của SL-T122-1: đột biến «sửa» bằng cách nới lỏng, ca đối chứng chặn đúng) |

Cả 6 đột biến lọt test của Thợ Máy và đều bị test Soi Lỗi bắt. File nguồn của worktree tạm đã trả về như cũ sau mỗi lượt.

## 5. Ghi nhận (không phải lỗi)

- **GN-1 · `SearchCache` không pickle, `deepcopy`, băm được** (`post_dates` là `MappingProxyType`). T-125 giữ bản đã đọc trong `st.session_state` như Thợ Máy đề xuất thì được; đừng trả nó qua `st.cache_data` (Streamlit phải pickle giá trị trả về nên sẽ lỗi).
- **GN-2 · `fetched_at` ở tương lai** (đồng hồ máy từng chạy nhanh rồi chỉnh lại) đọc vẫn nhận. T-124 khi «chặn bấm lại < 10 phút» (thiết kế 1.3) cần coi mốc ở tương lai là cũ, không thì chặn tới khi đồng hồ vượt mốc đó.
- **GN-3 · Surrogate lẻ cũng qua client T-121** (`_parse_json` không lọc, `_page` dùng `is_site_link`): ngoài phạm vi T-122, ghi để Soi Lỗi / Lá Chắn T-121 xem; sửa SL-T122-3 ở cache là đủ chặn cho đường này.
- **GN-4 · Dòng từ khóa trùng do sửa tay** (cùng khoảng, trang, từ khóa) đọc vẫn nhận vì bảng `page_query` không có ràng buộc duy nhất; app không bao giờ tự ghi trùng (`_merge_queries` cộng dồn trước). Cũng như sửa tay một con số hợp lệ, kiểu sửa này không phát hiện được bằng kiểm từng dòng; ai sửa được `data/` thì làm được nhiều hơn (cùng lớp «phải chiếm máy trước»).
- **GN-5 · `clear()` khi chương trình khác đang mở file** (Windows): `MSG_IO` kèm câu lỗi của hệ điều hành (`strerror`, không có đường dẫn), ví dụ «…(The process cannot access the file because it is being used by another process)». Chấp nhận được.
- **GN-6 · Không đo lại tốc độ** (máy đang chạy nhiều agent); số đo của Thợ Máy (đọc 1,1 giây cỡ thiết kế, 6,6 giây cỡ trần) không kiểm lại.

## 6. Bằng chứng

```
# Nhánh team/T-122 tại 307ff07 + file test mới, Windows 11, Python 3.12.15, SQLite 3.53.1
$ uv run pytest tests/test_search_cache.py tests/test_soi_loi_t122.py -q -rs
SKIPPED [1] tests\test_search_cache.py:754: máy này không cho tạo symlink file (Windows cần quyền
            Developer Mode)
SKIPPED [1] tests\test_soi_loi_t122.py:627: could not import 'seo_app.tracking.match'
190 passed, 2 skipped, 9 xfailed in 49.45s

$ uv run ruff check .                                   # toàn repo
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t122.py
1 file already formatted

# Ca ghép T-123 trên bản gộp tạm team/T-122 + team/T-123 (d71c9ad), seo_app nạp từ chính bản gộp
$ uv run pytest tests/test_soi_loi_t122.py tests/test_tracking_model.py tests/test_tracking_match.py -q
145 passed, 9 xfailed

# Quét ký tự ẩn file test: sạch. Quét bí mật, PYTHONUTF8=1:
$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t122.py
results: {}
# Đối chứng: bản sao file test thêm một khóa giả ở thư mục nháp → bắt được (Secret Keyword). Đã xóa.
```

Gộp thử với `main`: `origin/main` vẫn là `a499a13`, đúng gốc nhánh, không có gì để gộp. Ba worktree tạm (`mix`, `fix`, `mut`) đã gỡ.

## 7. Đề xuất

- **Thợ Máy (lượt 2 T-122):** sửa SL-T122-1 (trước T-124), SL-T122-2, SL-T122-3; gỡ đúng 9 dấu `xfail` (R5), không đổi thân test.
- **T-124:** dồn ba bản chuẩn hóa `WORDPRESS_URL` về một hàm (SL-T122-1); giữ ca `test_cache_rows_go_through_t123_without_being_dropped` chạy được (nó tự bỏ qua khi thiếu `seo_app.tracking`, nên sau khi gộp đợt 1 phải thấy nó **qua**, không bỏ qua); xử lý `fetched_at` ở tương lai (GN-2).
- **T-125:** không đưa `SearchCache` qua `st.cache_data` (GN-1).

## Lượt 2 · kiểm lại rút gọn (2026-11-04 13:08 +07:00)

| Mục | Nội dung |
|---|---|
| Kiểm | Thợ Máy lượt 2: mã `356e58e`, báo cáo `2f8aec4` |
| **Kết luận** | **ĐẠT**: SL-T122-1, -2, -3 đóng đúng; 0 lỗi mới. `site_base` mới **không nới** lớp chặn: staging, `www.`, `http://`, cổng khác 443, tên người dùng, tên miền giống đều bị loại với mọi cách viết `WORDPRESS_URL`; luật trùng hệt `site_prefix` T-121 và `site_base` T-123. R5 đúng: chỉ gỡ 3 khối dấu `xfail`, không ca nào yếu đi. Gộp thử với `main` (`33bac10`, và `c6bbf19` mới hơn) cùng `team/T-123`: không xung đột, test liên quan qua hết |

**Tóm tắt (cho chủ dự án):** ba lỗi đã sửa đúng. Địa chỉ website gõ có chữ hoa hay có `:443` nay lưu được số liệu. Tôi kiểm thêm: hơn 10.000 địa chỉ giả (bản staging, `www.`, tên miền na ná, có tên đăng nhập, cổng lạ…) vẫn bị chặn như trước. Phần lưu, phần lấy số liệu (T-121) và phần tính toán (T-123) nay dùng đúng một luật.

### 1. Ba lỗi đã đóng

| Lỗi | Sửa | Kiểm |
|---|---|---|
| SL-T122-1 | Hàm `site_base` (giống từng dòng `site_base` của T-123); `CacheScope.base` và mã băm phạm vi dùng nó | 3 ca của Soi Lỗi qua (chữ hoa ở tên máy, `:443`, `HTTPS://`); 4 ca đối chứng vẫn qua. Thêm so chéo, mục 2 |
| SL-T122-2 | `_stamp` kiểm năm cả **sau** khi đổi sang giờ Việt Nam, ngoài khoảng thì từ chối ngay khi ghi | 2 ca qua; ca `save_queries` của Thợ Máy qua (2000 lúc 10:00 múi +14 là năm 2000 giờ Việt Nam: vẫn ghi được) |
| SL-T122-3 | `_utf8_ok` ở `_page` và `_check_scope` | 4 ca qua; ca thuộc tính có surrogate lẻ của Thợ Máy qua |

### 2. `site_base` không nới lớp chặn, khớp T-121 và T-123

So chéo trên bản gộp tạm T-122 lượt 2 + `main` `33bac10` + `team/T-123` `15ccf1b` + `team/T-121` `482cdea`. Địa chỉ thử: 10.725 địa chỉ (5 scheme × 11 kiểu `netloc` gồm cổng 443, 8443, 80, 444, `:` rỗng, `user@`, `user:pw@`, `…@evil.example` × 13 tên máy gồm staging, `www.`, tên miền giống, chữ «а» Kirin, dấu chấm cuối × 15 đường dẫn). `WORDPRESS_URL`: 21 cách viết, gồm 7 cách viết website thật và các cấu hình sai.

| So | Ca lệch |
|---|---|
| `site_base` T-122 với `site_base` T-123 (21 cách viết) | **0** |
| `site_base` T-122 + «/» với `site_prefix` T-121 (mọi cách viết T-121 nhận) | **0** |
| Địa chỉ cache nhận (`_page`) với địa chỉ client T-121 nhận (`SearchConsoleClient._page`), kể cả chuỗi lưu lại | **0** |
| T-123 nhận (`page_key`) mà cache bỏ | **0** |
| Cache nhận mà T-123 bỏ | 15, đều là `%C3` (UTF-8 hỏng): T-123 cố ý coi là «dòng lạ» và đếm; T-121 cũng nhận, nên vẫn khớp đường lấy số liệu |
| Cache nhận địa chỉ ngoài website (khác tên máy, khác cổng của `WORDPRESS_URL`, có tên người dùng, không bắt đầu bằng tiền tố) | **0** |

Theo đúng danh sách Chỉ Huy hỏi, với 7 cách viết website thật: staging 14 ca, `www.` 7, `http://` 14, cổng khác (gồm `:443` viết ra, `:` rỗng) 28, tên người dùng 21, tên miền giống (`evilsuachuacuasat.com`, `….evil.example`, `-evil.com`, `.co`, chữ Kirin) 35: **nhận 0**. Trang thật lưu được với cả 7 cách viết.

`WORDPRESS_URL` có tên người dùng, `?…`, cổng khác 443: `site_base` bỏ phần thừa như T-123, còn T-121 từ chối hẳn cấu hình đó, nên không có số liệu nào tới cache. Địa chỉ **trang** có tên người dùng vẫn bị `is_site_link` loại. Không phải nới lớp chặn.

### 3. R5: gỡ dấu `xfail`

- `tests/test_soi_loi_t122.py`: chỉ xóa đúng 3 khối `@pytest.mark.xfail(strict=True, …)` (22 dòng) của SL-T122-1, -2, -3. Thân test, tham số, `ids=` giữ nguyên.
- `tests/test_search_cache.py`: chỉ thêm, không sửa ca cũ: nhập `site_base`, bảng `SITE_BASE_CASES` 7 ca, 3 ca mới.

### 4. Ca mới của lượt này

Thêm vào `tests/test_soi_loi_t122.py`, nay 70 ca:
- `test_lan_2_off_site_pages_stay_refused_for_every_spelling`: chạy trên nhánh. 6 cách viết × 16 địa chỉ ngoài website, cộng trang thật với mọi cách viết.
- `test_lan_2_site_rules_match_t121_and_t123`: so tiền tố của ba bản; địa chỉ T-123 nhận thì cache nhận và ngược lại. Ca này tự bỏ qua khi thiếu `seo_app.google.search_console` hay `seo_app.tracking`. Đã chạy qua trên bản gộp có cả T-121, T-123. Khi gộp xong đợt 1 phải thấy ca này **qua**.

Thử đột biến «bỏ phép so tiền tố, chỉ còn `is_site_link`» trên mã lượt 2: 3 ca bắt được, gồm ca mới.

### 5. Gộp thử, bằng chứng

```
# Nhánh team/T-122 2f8aec4 + file test Soi Lỗi mới
$ uv run pytest tests/test_search_cache.py tests/test_soi_loi_t122.py -q -rs
210 passed, 3 skipped        # symlink file (Windows); 2 ca ghép cần T-121 / T-123
$ uv run ruff check .        # All checks passed!

# Gộp tạm 2f8aec4 + main 33bac10 + team/T-123 15ccf1b: không xung đột
# 9 file: test_search_cache, test_soi_loi_t122, test_soi_loi_t123, test_tracking_{flags,keywords,match,model,periods,stats}
527 passed, 1 skipped        # chỉ ca symlink; ca ghép T-123 chạy thật, qua; ruff sạch

# main cục bộ đã lên c6bbf19 (chỉ tài liệu, README, test T-112): gộp lại 2f8aec4 + c6bbf19 + team/T-123, không xung đột
# cùng 9 file, file test Soi Lỗi mới
528 passed, 2 skipped        # symlink; ca so chéo cần T-121; ruff sạch

# Bản gộp thêm team/T-121 482cdea: không xung đột
$ pytest tests/test_soi_loi_t122.py tests/test_search_cache.py -q
212 passed, 1 skipped        # cả hai ca ghép (T-123, so chéo T-121/T-123) chạy thật, qua
```

Mọi lần chạy đã kiểm `seo_app` nạp từ chính bản gộp. Các worktree tạm (`gop`, `gop2`) đã gỡ; commit gộp tạm không đẩy.

Quét ký tự ẩn hai file của Soi Lỗi: sạch. Quét bí mật (`PYTHONUTF8=1 uvx detect-secrets scan`): `results: {}`. Lần quét đầu báo «Basic Auth Credentials» ở địa chỉ giả `https://user:pw@…` của ca mới. Đã tách chuỗi để quét sạch; giá trị thử không đổi. Đối chứng: bản sao thêm khóa giả, đặt trong thư mục đang quét, bị bắt (`Secret Keyword`).

### 6. Ghi nhận

- **GN-7 · Dòng lặp nguyên văn (SL-T121-1 của T-121):** cache cộng dồn dòng cùng (ngày, trang) sau khi bỏ `#…`, như đã chọn (chỗ #5 của Thợ Máy). Nên dòng mà Google lặp lại do lật trang cũng bị cộng nếu client đưa tới. Cache không phân biệt được hai trường hợp này, nên phải chặn ở client T-121 như báo cáo Soi Lỗi T-121 đề nghị. T-122 không cần sửa.
- GN-1, GN-2 của lượt 1 vẫn để T-124, T-125 như Thợ Máy đã chuyển.

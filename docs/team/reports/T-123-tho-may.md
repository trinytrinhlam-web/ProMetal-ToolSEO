# Báo cáo T-123 · Lõi tính toán theo dõi bài (Giai đoạn 6, đợt 1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-123](../tickets/T-123-loi-tinh-toan-theo-doi.md) |
| Nhánh | `team/T-123`, từ `main` `a499a13`; commit mã và test `a895d6d`, lượt 2 `d8fe3f7` |
| Ngày nộp | 2026-11-03 (giờ máy, +07); lượt 2: 2026-11-04 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đã có phần **tính toán** cho trang theo dõi bài trên Google. Phần này chưa có giao diện, chưa lấy số liệu thật.
  - Gán số liệu Search Console cho đúng từng bài, từng trang trên website. Địa chỉ không thuộc website (bản staging, `www.`, `http://`) bị bỏ.
  - Cộng số theo 7, 28, 91 ngày hay khoảng tự chọn, so với kỳ trước.
  - Gắn nhãn «tụt hạng», «mất click», «chưa có lượt hiển thị», «nhiều hiển thị ít click» và 3 nhãn khác.
  - Gộp từ khóa gõ có dấu và không dấu thành một dòng.
- Ngưỡng các nhãn đang theo **khuyến nghị A của câu hỏi 5**, vì anh chưa trả lời. Mỗi ngưỡng là một con số có tên trong code; anh muốn số khác thì chỉ sửa đúng con số đó.
- Ngày tính theo **giờ Google** (giờ California), có xét hai ngày đổi giờ 08/03 và 01/11. Một «ngày Google» bắt đầu lúc 14:00 hay 15:00 giờ Việt Nam.
- Phần này không gọi mạng, không đọc ghi file. Giao diện (T-125) và bước lấy số liệu (T-124) sẽ dùng lại nó.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/tracking/__init__.py` | Mới. Giới thiệu gói, các module |
| `seo_app/tracking/model.py` | Mới. Hai `Protocol` cho khuôn số liệu cache ở mục 3.1: `CachedDayLike`, `CachedQueryLike`. Đúng tên trường `CachedDay`, `CachedQuery` của T-122, khai báo dạng thuộc tính chỉ đọc để dataclass `frozen` khớp. Các kiểu kết quả: `PageKey`, `DayTotal`, `PageStats` (CTR, vị trí theo lượt hiển thị), `Comparison`, `FlagKind`, `Flag`, `MatchStatus`, `PlanMatch`, `TrackedPage`, `SiteTracking`, `KeywordVariant`, `KeywordGroup`, `KeywordTable` |
| `seo_app/tracking/periods.py` | Mới. `GOOGLE_TIMEZONE` (`America/Los_Angeles`), `google_today`, `google_day`, `published_day` (`date_gmt` UTC của WordPress → ngày PT). `Period` tự kiểm khi tạo. `last_days` (7/28/91), `previous_period`, `year_before` (lùi 364 ngày), `custom_period` (≤ 486 ngày, trong phần cache đã có), `week_blocks`. Ngày ngoài năm 2000–2200 là `PeriodError`, câu cố định, hay `None` (LC-T120-10) |
| `seo_app/tracking/match.py` | Mới. `page_key` làm đủ 5 bước của mục 1.4. `page_label`: đường dẫn «Trang khác» đã làm sạch, cắt 120 ký tự (LC-T120-19). `match_plan` nối dòng kế hoạch với bài. `build_tracking` gán số liệu từng ngày cho bài, trang và «Trang khác»; dòng ngoài website hay sai dạng bị bỏ và đếm (LC-T120-6). `MATCH_TEXT` là câu cố định cho từng kết quả nối |
| `seo_app/tracking/stats.py` | Mới. `aggregate` (mặc định chỉ số đã chốt, `SHOW_PROVISIONAL = False`: câu 3, khuyến nghị A). `compare` (`LOW_DATA_IMPRESSIONS = 30` → «ít dữ liệu»). `site_totals`, `weekly`. `numbers_ok`, `row_numbers_ok` kiểm số của một dòng. Viết số kiểu Việt Nam: `number_text` «9.800», `percent_text` «4,2%», `change_text` «+12 (+30%)», `ctr_change_text` «+0,3 điểm», `rank_change_text` «lên 2,1 bậc». Làm tròn kiểu 5 lên (`round_half_up`) |
| `seo_app/tracking/flags.py` | Mới. `page_flags` đặt 7 nhãn của mục 1.6; ngưỡng là 10 hằng có tên (câu 5, khuyến nghị A). Câu giải thích chỉ chèn số và ngày. `attention_counts` và `attention_text` dựng dòng «Cần chú ý: …» |
| `seo_app/tracking/keywords.py` | Mới. `query_text` làm sạch lại và cắt 200 ký tự. `keyword_table` gộp theo `fold_key`, đánh dấu từ khóa chính, từ khóa mới. `has_keyword`. `page_queries` lấy dòng từ khóa của một trang trong đúng khoảng. Ghi chú cố định `HIDDEN_QUERIES_NOTE` |
| `tests/test_tracking_model.py` | Mới, 5 ca. Dữ liệu giả dùng chung (`Day`, `Query` giống hệt khuôn T-122). Kiểu dữ liệu. Ca kiểm gói là hàm thuần: đọc mã nguồn, không nhập `socket`, `requests`, `sqlite3`, `pathlib`, `os`, `streamlit`, `seo_app.google`, `seo_app.storage`…, không gọi `open`, `eval` |
| `tests/test_tracking_periods.py` | Mới, 51 ca: giờ PT (hai ngày đổi giờ, 14:00/15:00 giờ Việt Nam), `date_gmt` lạ, khoảng ngày, tuần, ngày biên không tràn |
| `tests/test_tracking_match.py` | Mới, 70 ca: `page_key`, dòng ngoài website, đường dẫn «Trang khác», số sai dạng, bài đổi slug, nối dòng kế hoạch |
| `tests/test_tracking_stats.py` | Mới, 19 ca: cộng dồn, số tạm, so kỳ, chữ chênh lệch, làm tròn |
| `tests/test_tracking_flags.py` | Mới, 46 ca: từng nhãn ở đúng ngưỡng, câu giải thích, dòng tóm tắt |
| `tests/test_tracking_keywords.py` | Mới, 16 ca: gộp cách gõ, từ khóa chính, từ khóa mới, từ khóa lạ |
| `docs/team/reports/T-123-tho-may.md` | Báo cáo này |

Không sửa file nào có sẵn: không đụng `seo_app/google/**`, `seo_app/storage/**`, `seo_app/plan/**`, `app/**`. Gói chỉ **nhập** `PlanRow`, `clean_text`, `fold_key`, nhãn trạng thái từ `seo_app/plan/model.py`, và `PublishedItem`, `is_site_link`, `MAX_LINK_CHARS` từ `seo_app/wordpress/client.py`. Không thêm thư viện; `zoneinfo` dùng `tzdata` đã có.

### Cách dùng (cho T-124, T-125)

```python
tracking = match.build_tracking(settings.wordpress_url, site_index.items, cached_days, plan_rows)
period = periods.last_days(E, 28)              # E: ngày chốt cuối, lấy từ cache
before = periods.previous_period(period)       # hay year_before(period) nếu cache đủ (inside)
for page in tracking.pages:                    # mọi bài, trang; tracking.others: «Trang khác»
    cmp = stats.compare(stats.aggregate(page.days, period), stats.aggregate(page.days, before))
    labels = flags.page_flags(page, cmp, end=period.end, published=post_dates.get(page.item.id),
                              keywords=None)   # bảng từ khóa kỳ này nếu đã lấy
rows = keywords.page_queries(cached_queries, site=url, key=page.key, period=period)
table = keywords.keyword_table(rows, previous_rows_or_None, main_keyword=page.plan.keyword)
```

## Chỗ thiết kế để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Dòng kế hoạch có mã bài, nhưng Sheet vẫn ghi «Đã hẹn giờ» trong khi bài đã đăng | Khớp theo mã bài **trước** khi xét trạng thái | Bài có trong danh sách đã đăng thì chắc chắn đã lên website. Trạng thái trên Sheet có thể chậm |
| 2 | Dòng chưa có mã | So slug **chỉ** với dòng «Đã đăng» | Dòng «Chưa viết» mà slug trùng một bài cũ sẽ nhận nhầm số của bài cũ |
| 3 | Nhiều dòng cùng một bài | Không nối dòng nào, ghi «trùng». Riêng dòng khớp theo mã vẫn giữ bài khi dòng kia chỉ khớp theo slug | Như T-109: trùng thì cảnh báo, không đoán |
| 4 | Dòng «Bỏ» | Không theo dõi | Tôn trọng quyết định trên kế hoạch; bài (nếu có) vẫn có trong bảng, chỉ không mang thông tin kế hoạch |
| 5 | Nhãn «chưa có lượt hiển thị» khi chưa rõ ngày đăng | Vẫn gắn, câu ghi «chưa rõ ngày đăng». Trang (page) không xét ngày đăng | Lỡ gắn nhầm cho bài mới chỉ thêm một gợi ý vô hại. Bỏ sót thì không thấy bài có vấn đề |
| 6 | Bài đăng chưa tới 14 ngày | Gắn «🌱 Mới đăng» **thay** «👻» | Đúng ý bảng 1.6 |
| 7 | Nhãn cho «Trang khác» | Không gắn | Địa chỉ cũ sau khi đổi slug luôn «mất click»: chỉ là nhiễu |
| 8 | So ngưỡng vị trí, CTR | So trên số đã làm tròn như khi hiện (1 chữ số), làm tròn kiểu 5 lên | Hiện «4,0 → 7,0» thì phải gắn «xuống 3 bậc». Hàm `round` của Python đưa 0,25% về «0,2%» |
| 9 | Tuần không đủ 7 ngày ở đầu khoảng | Bỏ | Tuần thiếu ngày làm biểu đồ tụt giả |
| 10 | Từ khóa không có chữ Latin, chữ số (`fold_key` rỗng) | Giữ riêng từng từ, không gộp. Từ khóa chính như vậy thì không xét 🎯 | Nếu không, mọi từ khóa kiểu này gộp chung thành một dòng rỗng, và 🎯 sẽ gắn sai |
| 11 | Khoảng năm hợp lệ | 2000–2200 cho mọi ngày dùng để tính | Đủ rộng cho app; cộng trừ quanh khoảng này không bao giờ tràn `date` (LC-T120-10) |
| 12 | Kiểm từng dòng số liệu | Kiểm lại ở `build_tracking`, `aggregate`, `keyword_table` dù T-121, T-122 đã kiểm | Lớp chặn thêm: số lạ không lan ra giao diện (LC-T120-5) |

## Bằng chứng

```
# Trên đúng commit a895d6d (git status sạch), Windows 11, Python 3.12.15
$ uv run pytest tests/test_tracking_model.py tests/test_tracking_periods.py \
    tests/test_tracking_match.py tests/test_tracking_stats.py tests/test_tracking_flags.py \
    tests/test_tracking_keywords.py -q
207 passed in 4.41s          (5 + 51 + 70 + 19 + 46 + 16 ca)

$ uv run ruff check .                        # ruff 0.16.10, toàn repo
All checks passed!
$ uv run ruff format --check seo_app/tracking tests/test_tracking_*.py
13 files already formatted

# Quét bí mật, PYTHONUTF8=1, 13 file mới
$ PYTHONUTF8=1 uvx detect-secrets scan seo_app/tracking/*.py tests/test_tracking_*.py
results: {}
# Đối chứng: bản sao flags.py thêm một dòng khóa giả ở thư mục nháp → bắt được 1 (Secret
# Keyword), tức là máy quét có đọc file tiếng Việt. Đã xóa bản sao.

# Tốc độ (script ở thư mục nháp): 486 ngày × 200 trang, mức nhiều nhất của thiết kế 3.2
97200 dòng; build_tracking 0.41 s; cộng 2 kỳ + nhãn 200 trang 0.06 s
```

- Test chạy dưới bộ chặn mạng của `tests/conftest.py`. `test_package_is_pure_functions` đọc mã nguồn 7 file của gói: không nhập module mạng, file, cơ sở dữ liệu, giao diện, cũng không nhập `seo_app.google` (T-121) hay `seo_app.storage` (T-122).
- Mọi mã thoát ký tự lạ trong test viết dạng `\N{TÊN}`. Một script đã quét 13 file: không còn ký tự vô hình nằm thẳng trong mã nguồn.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1 (`model.py`): `CachedDayLike`, `CachedQueryLike` là `Protocol`; có `PageStats`, `Comparison`, `Flag`, `TrackedPage`. Dataclass `frozen` giống khuôn T-122 dùng thẳng được (`test_frozen_dataclasses_like_t122_fit_the_protocols`)
- [x] Yêu cầu 2 (`periods.py`), các ca trong `test_tracking_periods.py`:
  - giờ PT, gồm ca đổi giờ 08/03 và 01/11: `test_published_day_across_pt_daylight_saving`, `test_google_today_from_vietnam_clock`;
  - kỳ 7/28/91, kỳ trước, cùng kỳ năm trước: `test_last_days_previous_and_year_before`;
  - kỳ tự chọn: `test_custom_period_limits`;
  - tuần: `test_week_blocks_end_on_last_day`.
- [x] Yêu cầu 3 (`match.py`): `page_key` theo 5 bước (`test_page_key_normalizes`, với `%E1%BB%AD` hoa và thường, `#…`, `?…`, NFD → NFC, «/» cuối). Còn lại:
  - khớp bài, trang, «Trang khác»: `test_rows_go_to_posts_pages_and_other_pages`;
  - bài đổi slug: `test_renamed_slug_old_address_goes_to_other_pages`;
  - slug trùng hai bài: `test_match_plan_slug_needs_exactly_one_post`;
  - một bài một dòng: `test_match_plan_one_post_one_row`.
- [x] Yêu cầu 4 (`stats.py`): cộng dồn và vị trí theo lượt hiển thị (`test_aggregate_sums_days_inside_period_only`: (2×10 + 6×30)/40 = 5, không phải 4); so kỳ, «ít dữ liệu» (`test_compare_low_data_threshold`, `test_change_texts_vietnamese_style`)
- [x] Yêu cầu 5 (`flags.py`): 4 nhãn phiếu đòi và 3 nhãn còn lại của bảng 1.6, mỗi nhãn có ca ngay ngưỡng. Ngưỡng là hằng có tên (`test_thresholds_are_named_constants_of_question_5`)
- [x] Yêu cầu 6 (`keywords.py`): gộp có dấu, không dấu (`test_variants_with_and_without_accents_are_grouped`); từ khóa chính, từ khóa mới (`test_main_keyword_and_new_keywords`, `test_previous_not_fetched_means_no_new_flag`)
- [x] **LC-T120-6**: dòng staging, `www.`, `http://`, `…com.evil…`, `evilsuachuacuasat.com`, sai cổng, có tên người dùng, sai tiền tố đều bị bỏ và đếm, dù Google có trả (`test_page_key_rejects_rows_outside_website`, `test_rows_outside_website_are_dropped_even_if_google_returns_them`, `test_page_key_site_with_path_and_trailing_slash`)
- [x] **LC-T120-10** (kèm `ValueError` như T-118): năm được kiểm trước khi đổi múi giờ hay cộng trừ; không lọt `OverflowError`, `ValueError`. Các ca:
  - `test_google_day_checks_year_before_converting`, có ca đối chứng cho thấy đổi thẳng năm 1 thì ra `OverflowError`;
  - `test_date_arithmetic_never_overflows`, `test_previous_and_year_before_out_of_range_give_period_error`;
  - `test_published_day_rejects_bad_values` (năm 9999, năm 1, tháng 13, 30/02, 24 giờ);
  - ngày lạ trong dòng cache: `test_bad_rows_are_skipped_and_counted`;
  - ngày đăng, ngày cuối kỳ lạ khi gắn nhãn: `test_bad_published_date_never_overflows`, `test_bad_period_end_never_overflows`.
- [x] **LC-T120-11** (phần T-123: dữ liệu chữ thuần):
  - từ khóa làm sạch lại, cắt 200 ký tự (`test_query_text_cleans_and_cuts`, `test_bad_query_rows_are_skipped`);
  - câu của nhãn không chép chữ Google hay WordPress (`test_reasons_never_carry_google_or_wordpress_text`).
  - Phần `safe_rows` trước `st.dataframe`, không `LinkColumn`, là việc của T-125.
- [x] **LC-T120-15**: test không gọi mạng; gói là hàm thuần (`test_package_is_pure_functions`). Ca biên của mục 2.4 thuộc phần này đều có test:
  - số: `bool`, số thực ở chỗ số nguyên, `NaN`, `inf`, click lớn hơn hiển thị, hiển thị 0, vị trí 0 / dưới 1 / trên 10.000, quá 10⁹;
  - đường dẫn: quá 2.000 ký tự, ngoài website;
  - từ khóa: quá 2.048 ký tự, rỗng sau khi làm sạch.
- [x] **LC-T120-19** (phần «Trang khác»): đường dẫn giải mã `%` ra ký tự đảo hướng, vô hình, điều khiển đều bị `clean_text` bỏ; cắt 120 ký tự; chỉ là chữ (`test_page_label_is_cleaned_plain_text`). Tên máy ở «Kiểm tra» thuộc T-121 (client Q3) và T-125 (hiện), xem Đề xuất
- [x] Test liên quan và `uv run ruff check .` qua (mục Bằng chứng). Không sửa hàm dùng chung nào, nên không có nơi gọi nào phải chạy lại
- [x] Báo cáo này
- [ ] Toàn bộ `uv run pytest`: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Vị trí trung bình theo lượt hiển thị** là suy luận từ định nghĩa (thiết kế 1.5). Lượt thử thật cần so với bảng «Trang» của Search Console.
- **Site dùng đường dẫn kiểu `?p=123`** (không phải slug): bài nào có link chứa «?» bị bỏ khỏi bảng, đếm vào `skipped_items`, vì thiết kế 1.4 bước 3 không gán dòng có «?» cho bài. suachuacuasat.com dùng slug (`/sua-cua-keo-tphcm/`) nên không ảnh hưởng. Nếu site đổi kiểu đường dẫn thì phải xem lại.
- **Hai địa chỉ chỉ khác `%2F` và «/»** (`/a%2Fb/` và `/a/b/`) ra cùng khóa vì đường dẫn được giải mã. WordPress không tạo đường dẫn có `%2F`, nên coi như không xảy ra.
- **«Trang khác» có hai đường dẫn chỉ khác ký tự vô hình**: hai dòng giữ riêng số liệu (khóa không làm sạch), nhưng nhãn hiện ra giống nhau. Không gộp là cố ý: gộp có thể gán nhầm số của địa chỉ lạ cho bài thật.
- **E (ngày chốt cuối)** và phần cache đã có (`available`) do T-122, T-124 cung cấp. `page_flags` hiểu ngày không có dòng nào là 0 lượt hiển thị, nên chỉ được gọi khi cache đã phủ cả kỳ đang xem và kỳ so sánh. Giao diện phải kiểm bằng `Period.inside`.
- **Tên `Protocol`** là `CachedDayLike`, `CachedQueryLike`, khác tên dataclass của T-122 để khỏi nhầm khi nhập. Chỉ tên trường phải khớp. T-122 đổi tên trường thì `test_frozen_dataclasses_like_t122_fit_the_protocols` không bắt được, vì ca này dùng bản sao. Nên thêm một ca dùng dataclass thật của T-122 khi gộp (Đề xuất).

## Đề xuất

- **T-122 (Thợ Máy, đang làm song song):** giữ đúng tên trường của khuôn 3.1. Cột `final` đọc ra phải là `bool` thật (SQLite trả `0`/`1`: đổi sang `bool` trước khi dựng dataclass), vì T-123 bỏ những dòng có `final` không phải `bool`. Ngày đọc ra phải là `date`, không phải `datetime`.
- **Khi gộp T-122 và T-123:** thêm một ca dùng `CachedDay`, `CachedQuery` thật của T-122 với `match.build_tracking`, `keywords.keyword_table`. Nên làm ở phiếu T-124, phiếu đầu tiên có cả hai.
- **T-124:** lấy `E` và phần cache đã có từ thông tin của T-122. Đổi `date_gmt` của `post_statuses` sang ngày PT bằng `periods.published_day`. Gọi `stats.compare(…, None)` khi cache chưa phủ kỳ so sánh.
- **T-125 (Họa Sĩ):** cần làm đúng ba điểm sau.
  - Bảng nào có chữ từ Google hay WordPress (`TrackedPage.label`, `KeywordGroup.text`, từng cách gõ trong `variants`) đều qua `safe_rows` trước `st.dataframe`; không dùng `LinkColumn` (LC-T120-11). Link tới bài chỉ dựng từ `item.link` bằng `markdown_link`; không bao giờ dựng từ `label` của «Trang khác».
  - Dùng các chữ cố định có sẵn: `match.MATCH_TEXT`, `flags.LABELS`, `flags.HINTS`, `flags.attention_text`, `keywords.HIDDEN_QUERIES_NOTE`, các hàm `stats.*_text`.
  - Ngày hiện ra kèm chú thích «ngày theo giờ Google».
- **T-121 / T-125, LC-T120-19 phần tên máy:** ba tên máy ngoài website ở «Kiểm tra» (Q3) thuộc client T-121. Nếu cần một hàm kiểm dạng tên miền dùng chung thì nên đặt ở T-121; T-123 không làm để tránh hai bản.
- **Soi Lỗi:** các ca thêm nên thử:
  - `published` là `datetime` (lớp con của `date`);
  - `Period` có `start` là `date` lớp con lạ;
  - dòng cache có `page` là lớp con của `str`;
  - bảng từ khóa có hơn 50 nhóm;
  - `round_half_up` với số rất lớn.

## Câu hỏi cho chủ dự án

Không có. Câu 3 và câu 5 của T-120 đang theo khuyến nghị A. Anh chọn khác thì chỉ sửa hằng: `stats.SHOW_PROVISIONAL` và các ngưỡng đầu file `seo_app/tracking/flags.py`.

## Lượt 2 · SL-T123-2, SL-T123-1 (Soi Lỗi, 04/11)

**Tóm tắt (cho chủ dự án):** sửa hai lỗi Soi Lỗi tìm ra.
- Địa chỉ website trong `.env` gõ có chữ hoa (ví dụ `https://SuaChuaCuaSat.com`) thì trang theo dõi không còn trống nữa.
- Tỉ lệ click đúng «x,x5%» nay luôn làm tròn lên (28,75% hiện «28,8%»).

| Mục | Nội dung |
|---|---|
| SL-T123-2 (Trung bình) | `page_key` so `url.startswith(WORDPRESS_URL + "/")` có phân biệt hoa thường. `WORDPRESS_URL` có chữ hoa ở tên máy (`config.py` chỉ bỏ «/» cuối) thì mọi bài, mọi dòng thành «dòng lạ», bảng trống |
| Sửa SL-T123-2 | `seo_app/tracking/match.py`: hàm mới `site_base(site)` chuẩn hóa **riêng** `WORDPRESS_URL`: scheme và tên máy viết thường, bỏ cổng 443 mặc định và «/» cuối, đường dẫn giữ nguyên. `page_key` so tiền tố với `site_base(site) + "/"` |
| Vì sao đúng chiều | Địa chỉ từ Google, WordPress vẫn so **nguyên văn**, như bộ lọc phía Google (RE2 phân biệt hoa thường). Lớp chặn của LC-T120-6 giữ nguyên: staging, `www.`, `http://`, tên miền khác, cổng khác, tên người dùng, địa chỉ Google viết hoa tên máy (ca cũ `test_page_key_rejects_rows_outside_website` không đổi). Soi Lỗi có 12 ca canh, đều qua |
| Cổng 443 | Cùng nguyên nhân, cùng hàm: `https://suachuacuasat.com:443` (`is_site_link` coi là đúng website) cũng làm bảng trống. Tôi sửa luôn cho trùng tiền tố của client T-121, có ca test |
| SL-T123-1 (Thấp) | `shown_ctr_percent`, `percent_text` nhân 100 bằng số thực: 23/80 × 100 = 28,749999… → «28,7%». Soi Lỗi đếm 229/3.400 ca đúng nửa bị làm tròn xuống |
| Sửa SL-T123-1 | `seo_app/tracking/stats.py`: `shown_ctr_percent` tính từ hai số nguyên trên `Decimal` (`clicks × 100 / impressions`) rồi làm tròn 5 lên. `percent_text` nhân 100 trên `Decimal(repr(tỉ lệ))`. Vị trí, chênh vị trí, phần trăm chênh click không bị lỗi này (Soi Lỗi đã thử), nên không đổi |
| Test | 7 ca `xfail(strict=True)` của Soi Lỗi XPASS trên mã mới, rồi gỡ dấu (chỉ xóa 3 khối dấu, 9 dòng; R5). Thêm 16 ca: `test_site_base_lowercases_scheme_and_host_only` (7), `test_wordpress_url_spelling_does_not_empty_the_table` (3), `test_google_url_spelling_is_still_compared_verbatim`, `test_ctr_percent_rounds_exact_halves_up` (4), `test_ctr_change_uses_the_shown_half_up_numbers`. Không đổi kỳ vọng ca cũ nào |

**Kiểm T-121 (đọc code `origin/team/T-121` `eb05747`, không sửa):** client T-121 **không** có lỗi chữ hoa.
- `site_prefix(WORDPRESS_URL)` dựng `https://<tên máy viết thường><đường dẫn>/` từ `urlsplit`, vì `urlsplit` tự viết thường scheme và `hostname`. Hàm cũng bỏ cổng 443 và từ chối cổng khác, `http://`, tên người dùng.
- Bộ lọc gửi Google (`page_filter_expression`) và bước kiểm từng dòng (`_page`) đều dùng tiền tố đã chuẩn hóa này.
- Tôi so thật bằng một worktree tạm tách rời của nhánh T-121 (đã gỡ ngay sau đó). Với mọi `WORDPRESS_URL` T-121 nhận, tiền tố của T-121 và `site_base + "/"` của T-123 **trùng nhau**: chữ hoa, cổng 443, đường dẫn con có chữ hoa.

```
# Bản gốc còn dấu của tests/test_soi_loi_t123.py (git show HEAD:…, chép ra thư mục nháp), mã mới
$ uv run pytest <bản gốc> -q -rf
FAILED test_ctr_exact_half_always_rounds_up[28,75|51,25|14,25] - [XPASS(strict)] SL-T123-1 …
FAILED test_every_exact_half_ctr_rounds_up - [XPASS(strict)] SL-T123-1 …
FAILED test_site_url_case_does_not_drop_everything[hoa-dau|hoa-het|scheme-hoa] - [XPASS(strict)] SL-T123-2 …
7 failed, 87 passed in 12.36s       (7 «hỏng» = XPASS strict, đúng mong đợi)

# Đã gỡ dấu, trên đúng commit d8fe3f7 (git status sạch): 7 file test liên quan
$ uv run pytest tests/test_tracking_model.py tests/test_tracking_periods.py tests/test_tracking_match.py \
    tests/test_tracking_stats.py tests/test_tracking_flags.py tests/test_tracking_keywords.py \
    tests/test_soi_loi_t123.py -q
317 passed in 8.93s                 (207 ca lượt 1 + 16 ca lượt 2 + 94 ca Soi Lỗi)

$ uv run ruff check .                        # ruff 0.16.10, toàn repo
All checks passed!

# So tiền tố T-121 (worktree tạm tách rời eb05747) với T-123
'https://Suachuacuasat.com'      T-121 'https://suachuacuasat.com/'   T-123 'https://suachuacuasat.com/'   trùng
'HTTPS://SUACHUACUASAT.COM/'     T-121 'https://suachuacuasat.com/'   T-123 'https://suachuacuasat.com/'   trùng
'https://suachuacuasat.com:443'  T-121 'https://suachuacuasat.com/'   T-123 'https://suachuacuasat.com/'   trùng
'https://Example.com/Blog/'      T-121 'https://example.com/Blog/'    T-123 'https://example.com/Blog/'    trùng
'https://example.com:8443' và 'http://suachuacuasat.com': T-121 từ chối WORDPRESS_URL (không lấy số liệu)
```

- Hàm `site_base`, `percent_text`, `shown_ctr_percent` chỉ được gọi trong gói `seo_app/tracking` (`grep` cả `seo_app/`). Gói chưa gộp `main`, nên test mọi nơi gọi là đúng 7 file trên.
- Quét ký tự ẩn trên 5 file đổi: sạch. `ruff format --check` file của Soi Lỗi sau khi gỡ dấu: sạch.

**Chưa làm ở lượt này, ghi đề xuất** (góp ý của Soi Lỗi, không xếp lỗi):
- **G1, rủi ro ghép nối:** khi có dòng sai khuôn (sai kiểu), mọi bài có thể hiện 👻.
  - T-122 đã khóa kiểu đọc ra (`b9514f7`: `final` là `bool`, `day` là `date`, có test).
  - Còn hai việc nên làm ở T-124: ca ghép nối với dataclass thật của T-122; đếm riêng «dòng sai khuôn» với «dòng ngoài website», để T-125 không gắn 👻 khi có dòng sai khuôn.
- **G3:** giao diện ghi «trạng thái trên Sheet chưa cập nhật» khi dòng kế hoạch khớp theo mã mà trạng thái chưa là «Đã đăng». Việc của T-125.
- **G5:** `round_half_up` với số từ 10²⁷ trở lên ném lỗi. Trần 10⁹ lượt hiển thị một dòng không chạm tới mức đó. Ghi là giới hạn đã biết.

# Báo cáo T-123 · Lõi tính toán theo dõi bài (Giai đoạn 6, đợt 1) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-123](../tickets/T-123-loi-tinh-toan-theo-doi.md), Thợ Máy đầu nhánh `2548d1f` (gốc `main` `a499a13`); thiết kế T-120 mục 1.4–1.7, 2.6, 3.1 |
| Ngày nộp | 2026-11-04 (07:45 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T123-2: `WORDPRESS_URL` có chữ hoa ở tên máy thì bảng theo dõi trống), **1 Thấp** (SL-T123-1: CTR đúng nửa có lúc làm tròn xuống). Mọi ca biên theo tin giao (đổi giờ PT, 16 tháng, năm 1 / 9999, `%E1%BB%AD`, `#…`, đổi slug, slug trùng, vị trí 0, click > hiển thị, từ khóa vô hình) **đúng**. 3 chỗ tự chọn Chỉ Huy hỏi: khớp mã trước trạng thái **đồng ý**, slug chỉ cho dòng «Đã đăng» **đồng ý**, làm tròn 5 lên **đúng ý, sai ở CTR** (SL-T123-1). Một rủi ro ghép nối với T-122 (dòng sai kiểu bị bỏ lặng lẽ, mọi bài thành 👻) cần khóa ở T-122 / T-124. Điều kiện: sửa SL-T123-2 trước khi nối giao diện (T-125); SL-T123-1 sửa cùng lượt hay để T-125, tùy Chỉ Huy |

## Tóm tắt (cho chủ dự án)

- **Phần tính toán cho trang theo dõi Google nhìn chung đúng.** Tôi thử các ngày đổi giờ ở Mỹ (08/03, 01/11), khoảng ngày dài tối đa 16 tháng, ngày lạ (năm 1, năm 9999), đường dẫn tiếng Việt viết nhiều kiểu, bài đổi đường dẫn, hai bài trùng đường dẫn, số liệu vô lý (vị trí 0, click nhiều hơn lượt hiển thị), từ khóa toàn ký tự vô hình: phần mềm xử lý đúng, không lỗi.
- **Lỗi 1 (cần sửa trước khi làm giao diện):** nếu địa chỉ website trong `.env` gõ có chữ hoa (ví dụ `https://SuaChuaCuaSat.com`) thì trang theo dõi sẽ **trống trơn**, không nói lý do, dù các trang khác của phần mềm vẫn chạy bình thường. Sửa nhỏ, vài dòng.
- **Lỗi 2 (nhỏ):** một số tỉ lệ click đúng «x,x5%» bị làm tròn **xuống** thay vì lên (ví dụ 28,75% hiện «28,7%» thay vì «28,8%»). Chỉ lệch 0,1 điểm ở con số hiện ra, khoảng 7% số trường hợp «đúng nửa».
- **Một chỗ cần ghép cẩn thận với phần lưu số liệu (T-122):** nếu phần lưu trả ngày, cờ «đã chốt» sai kiểu, phần tính toán bỏ hết số liệu mà không báo, và **mọi bài hiện nhãn «👻 Chưa có lượt hiển thị»**. Tôi đề nghị khóa chỗ này bằng test ở T-122 và ở phiếu ghép T-124.
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t123.py` | Mới: **94 ca: 87 qua, 7 `xfail(strict=True)`** của 2 lỗi mới. Mọi tham số có `ids=` ngắn. Không gọi mạng, không đọc ghi file |
| `docs/team/reports/T-123-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác.

## 1. Ca biên theo tin giao

| Ca | Kết quả |
|---|---|
| **Đổi giờ PT 08/03, 01/11** | `published_day` đúng tới từng giây ở 8 mốc (ví dụ `2026-03-08T07:59:59` UTC là 07/03, `08:00:00` là 08/03; `2026-11-02T07:59:59` là 01/11, `08:00:00` là 02/11). `google_today` từ giờ Việt Nam: ngày Google bắt đầu 15:00 (mùa đông) / 14:00 (mùa hè), đúng ở 8 mốc. Kỳ 7, 28, 91 ngày qua ngày đổi giờ vẫn đúng số ngày, tuần đủ 7 ngày |
| **Kỳ ở biên 16 tháng** | 486 ngày nhận, 487 ngày `PeriodError` (cả `last_days`, `custom_period`); kỳ tự chọn ngoài phần đã có: `PeriodError` |
| **Năm 1, năm 9999** | `Period`, `last_days` với năm 1, 9999, `datetime`, chữ, `None`, `bool`: luôn `PeriodError`, không lỗi Python. `google_day`, `google_today` với năm 1, 9999, `datetime.min` / `max` có múi giờ, giờ không múi giờ: `None` / `PeriodError`, không `OverflowError`. `published_day` với năm 1, 9999, 1999, 2201, 29/02/2026, tháng 13, 24 giờ, dấu cách, chữ số toàn chiều rộng: `None`. Kỳ trước / cùng kỳ năm trước của kỳ đầu năm 2000: `PeriodError` (LC-T120-10) |
| **`%E1%BB%AD` hoa / thường** | `%E1%BB%AD`, `%e1%bb%ad`, viết lẫn `%E1%bb%Ad`, chữ thật «ử», có `#…`, có `#a?b=1`: cùng một khóa `/sửa-cua` |
| **Hai dòng chỉ khác `#…`** | Ba dòng cùng ngày (khác `#…`, «/» cuối, cách viết `%`): cộng thành **một** ngày của đúng bài, vị trí trung bình theo lượt hiển thị (3 click, 40 hiển thị, tổng vị trí 150) |
| **`?` trong `#…`** | `/a/#x?s=1` là trang `/a` (phần sau `#` không tính); `/a/?s=1#x` là «Trang khác» `/a?s=1` |
| **Bài đổi slug** | Địa chỉ cũ vào «Trang khác»; số địa chỉ mới gán cho bài; dòng kế hoạch có mã bài khớp bài (số của địa chỉ mới); dòng «Đã đăng» chỉ có slug cũ: «Không thấy bài» (không đoán) |
| **Slug trùng hai bài** | Dòng chỉ có slug: «Slug trùng nhiều bài», không nối; dòng có mã bài của một trong hai bài vẫn khớp đúng bài đó |
| **`position` bằng 0; click > hiển thị** | Cùng 6 dạng số lạ khác (vị trí < 1, hiển thị 0, click âm, `NaN`, `bool`, vị trí > 10.000): dòng ngày bị bỏ và đếm, dòng từ khóa bị bỏ và đếm |
| **Từ khóa toàn ký tự vô hình** | Bị bỏ và đếm; từ khóa chính toàn ký tự vô hình không bao giờ thành «từ khóa chính» (`has_keyword` trả `None`, không gắn 🎯) |
| **`final` không phải `bool`, `day` không phải `date`** | Dòng bị bỏ, chỉ đếm vào `skipped_rows`. Hậu quả: xem mục 4 |

Ngoài ra đã thử (dò bằng script, không thêm ca): đường dẫn có `%3F` (dấu «?» thật trong đường dẫn), `%23`, `%2F`, `%zz`, `%C3` (UTF-8 hỏng → dòng lạ), `//abc`, cổng `:443`, khoảng trắng, `%00`, ký tự đảo hướng (nhãn đã làm sạch); từ khóa chỉ có dấu câu, chữ Hán (giữ riêng, không gộp); `fold_key` gộp «Đẹp đá» với «dep da».

## 2. Ba chỗ Thợ Máy tự chọn mà Chỉ Huy hỏi

| # | Chỗ | Nhận xét |
|---|---|---|
| 1 | **Khớp theo mã bài trước trạng thái** | **Đồng ý.** Bài có trong danh sách đã đăng thì chắc chắn đã lên website, còn Sheet có thể chậm (bài hẹn giờ tự lên, chủ dự án bấm Đăng trong trang quản trị, T-109 chưa chạy). Thiết kế 1.4 cũng liệt kê bước khớp mã trước bước «chưa lên website». Hệ quả phụ (đã thử): dòng «Chưa viết» có mã bài gõ nhầm sẽ giành bài, và dòng «Đã đăng» thật chỉ khớp theo slug thành «trùng». Người dùng vẫn thấy (câu «Nhiều dòng kế hoạch cùng một bài»), nên không xếp lỗi; xem góp ý G3 |
| 2 | **Slug chỉ dùng cho dòng «Đã đăng»** | **Đồng ý.** Dòng «Chưa viết» trùng slug bài cũ (viết bài thay thế) không nhận số của bài cũ. Dòng «Đã gửi nháp», «Đã hẹn giờ» do app gửi luôn có mã bài, nên chỉ dòng gõ tay mới bị bỏ qua, theo hướng an toàn |
| 8 | **Làm tròn kiểu 5 lên** | **Đúng ý, nhưng sai ở CTR** (SL-T123-1): `round_half_up` làm tròn trên chữ số viết ra (`repr`) là đúng, nhưng CTR đã nhân 100 bằng số thực **trước** đó. Vị trí, chênh vị trí, phần trăm chênh click không bị. So ngưỡng trên số đã làm tròn khớp số hiện ra: «3,96 → 6,96» hiện «4,0 → 7,0» và gắn «xuống 3 bậc»; CTR 0,95% hiện «1,0%» nên không gắn «dưới 1%», 0,94% thì gắn |

## 3. Lỗi mới

### SL-T123-2 · Trung bình · `WORDPRESS_URL` có chữ hoa ở tên máy: bảng theo dõi trống

- **Tái hiện** (`test_site_url_case_does_not_drop_everything`, 3 ca): `build_tracking("https://Suachuacuasat.com", [bài /bai-1/], [số ngày của /bai-1/])` cho `pages = ()`, `skipped_items = 1`, `skipped_rows = 1`. Cũng vậy với `https://SUACHUACUASAT.COM`, `HTTPS://suachuacuasat.com`.
- **Vì sao:** `config.load_settings` chỉ bỏ «/» cuối của `WORDPRESS_URL`, không đổi chữ thường. `is_site_link` so tên máy không phân biệt hoa thường (như HTTP, DNS) nên vẫn nhận. Nhưng `page_key` còn đòi `url.startswith(site + "/")`, phép so này phân biệt hoa thường. Link bài từ WordPress và địa chỉ từ Google đều viết thường, nên **mọi** bài và **mọi** dòng thành «dòng lạ».
- **Hậu quả:** trang theo dõi (T-125) trống, không bài nào, không nhãn nào, chỉ có số «dòng lạ». Mọi phần khác của app vẫn chạy với `WORDPRESS_URL` đó, nên người dùng khó đoán ra nguyên nhân. Xếp Trung bình vì cả tính năng hỏng với một cấu hình gõ tay hợp lệ. Khả năng xảy ra thấp nếu `.env` hiện viết thường (tôi không đọc `.env`).
- **Gợi ý sửa:** chuẩn hóa **chỉ** `site` (`WORDPRESS_URL`): scheme và tên máy viết thường, phần đường dẫn giữ nguyên. Địa chỉ Google, WordPress vẫn so nguyên văn: test của Thợ Máy coi địa chỉ Google có tên máy viết hoa là dòng lạ (`test_page_key_rejects_rows_outside_website`), cách sửa này giữ được điều đó. Ca `test_rows_outside_website_stay_dropped_whatever_the_case` (12 ca, đang qua) canh để bản sửa không nới lớp chặn staging, `www.`, `http://`, tên miền khác, cổng khác (LC-T120-6).

### SL-T123-1 · Thấp · CTR đúng nửa có lúc làm tròn xuống

- **Tái hiện** (`test_ctr_exact_half_always_rounds_up`, 3 ca; `test_every_exact_half_ctr_rounds_up`): 23/80 = 28,75% hiện «28,7%»; 41/80 = 51,25% hiện «51,2%»; 57/400 = 14,25% hiện «14,2%». Trong khi đó 1/400 = 0,25% hiện «0,3%» (ví dụ của chính báo cáo Thợ Máy). Quét mọi CTR đúng nửa với lượt hiển thị ≤ 2.000: **229 / 3.400** ca bị làm tròn xuống.
- **Vì sao:** `shown_ctr_percent` và `percent_text` tính `ctr * 100` bằng số thực: 23/80 × 100 = `28.749999999999996`. Sau đó `round_half_up` làm tròn trên `repr` của số đó nên ra 28,7.
- **Hậu quả:** chữ CTR lệch 0,1 điểm ở các ca đúng nửa; «chênh CTR» (`ctr_change_text`) cũng có thể lệch 0,1. Ngưỡng «dưới 1%» của 👀 không bị ảnh hưởng (0,95% vẫn hiện «1,0%»).
- **Gợi ý sửa:** nhân 100 trên số thập phân: `Decimal(repr(ratio)) * 100` (hay tính từ hai số nguyên `clicks`, `impressions`) rồi mới làm tròn.

**Thử bản sửa nháp** cho cả hai lỗi (worktree tạm, đã xóa): `site` viết thường scheme, tên máy; CTR nhân 100 trên `Decimal(repr(…))`. Kết quả: 7 ca `xfail` thành XPASS, 294 ca khác qua, gồm đủ 207 ca của Thợ Máy. Bản sửa nháp đầu tiên viết thường cả địa chỉ Google thì làm hỏng 2 ca của Thợ Máy, nên đã chỉnh lại như gợi ý trên.

## 4. Rủi ro ghép nối với T-122: dòng sai kiểu bị bỏ lặng lẽ

- **Đã thử:** dòng số liệu có `final = 1` (số nguyên, như SQLite trả), `day` là `datetime` hay chữ `"2026-10-01"`: `build_tracking` bỏ dòng, chỉ đếm vào `skipped_rows`. Nếu **mọi** dòng như vậy (T-122 quên đổi kiểu), mọi bài có 0 lượt hiển thị. `page_flags` khi đó gắn **«👻 Chưa có lượt hiển thị»** cho mọi bài, và dòng tóm tắt sẽ là «Cần chú ý: N bài chưa có lượt hiển thị». Đã thử: bài 1 có 28 ngày số liệu (`final = 1`), bài 2 không có số liệu: cả hai đều thành 👻.
- **Không xếp lỗi của T-123:** gói làm đúng khuôn 3.1 (`final: bool`, `day: date`), và việc kiểm thêm là lớp chặn thiết kế muốn có (LC-T120-5). Nhưng hậu quả của một lần lệch kiểu là **sai mà trông như đúng**.
- **Đề nghị khóa ở 3 chỗ:**
  - T-122 có test khẳng định dòng đọc ra có `type(final) is bool`, `type(day) is date`;
  - T-124 (phiếu đầu tiên có cả T-122 và T-123) thêm ca ghép nối với `CachedDay`, `CachedQuery` thật, như Thợ Máy đã đề xuất;
  - đếm riêng «dòng sai khuôn» (sai kiểu, số lạ) và «dòng ngoài website», để T-125 báo «dữ liệu lưu tạm sai khuôn» và không gắn 👻 khi có dòng sai khuôn.
- Cùng loại: `page_flags(published=…)` nhận `datetime` thay vì `date` thì coi như «chưa rõ ngày đăng». Bài mới đăng khi đó không nhận 🌱 mà có thể nhận 👻 «chưa rõ ngày đăng». T-124 phải đưa đúng `periods.published_day(...)`.

## 5. Điều kiện Lá Chắn T-120 (phần T-123)

| Mã | Kết quả |
|---|---|
| LC-T120-6 | Đạt (có ngoại lệ là SL-T123-2 ở chiều ngược: bỏ nhầm cả dòng đúng website). Thợ Máy có test staging, `www.`, `http://`, tên miền khác, cổng, tên người dùng; tôi thêm 12 ca canh khi sửa SL-T123-2 |
| LC-T120-10 | Đạt: năm được kiểm trước khi đổi múi giờ hay cộng trừ, không lọt `OverflowError` / `ValueError` ở mọi ca năm 1 / 9999 / `datetime.min`, `max` (mục 1) |
| LC-T120-11 | Đạt phần dữ liệu: từ khóa làm sạch, cắt 200 ký tự; câu nhãn chỉ có số và ngày. `safe_rows`, không `LinkColumn` là việc T-125 |
| LC-T120-15 | Đạt: test không gọi mạng; `test_package_is_pure_functions` của Thợ Máy qua |
| LC-T120-19 | Đạt phần «Trang khác»: đường dẫn giải mã ra ký tự đảo hướng, vô hình, `NUL` thì nhãn đã bỏ; cắt 120 ký tự |

## 6. Góp ý (không xếp lỗi)

- **G1.** Mục 4 (rủi ro ghép nối, đếm riêng dòng sai khuôn).
- **G2.** Nhãn «Trang khác» có thể trùng nhau dù khóa khác: `/a%3Fb/` (dấu «?» thật trong đường dẫn) và `/a?b` đều hiện «/a?b»; `%2F` và «/» cùng khóa (Thợ Máy đã ghi). Ít gặp, chỉ ảnh hưởng chữ hiện.
- **G3.** Dòng kế hoạch khớp theo mã mà trạng thái chưa phải «Đã đăng»: giao diện nên ghi thêm «trạng thái trên Sheet chưa cập nhật». Như vậy mã bài gõ nhầm ở dòng «Chưa viết» dễ thấy hơn.
- **G4.** Địa chỉ có `?` rỗng (`/abc/?`) là «Trang khác», không gán cho bài `/abc/`. Theo đúng thiết kế bước 3; ghi lại để biết.
- **G5.** `round_half_up` ném `decimal.InvalidOperation` với số từ 10²⁷ trở lên, và phần trăm chênh click hiện chữ số rác với số trên 2⁵³. Không tới được với trần 10⁹ lượt hiển thị một dòng, nên ghi «giới hạn đã biết».
- **G6.** Thợ Máy đề nghị Soi Lỗi thử thêm vài ca. Đã thử:
  - `Period` với `datetime` (lớp con của `date`): `PeriodError` (có ca test);
  - dòng có `page` là lớp con của `str`: theo mã thì nhận (`isinstance`);
  - bảng từ khóa hơn 50 nhóm: theo mã thì trả đủ (cắt 50 là việc giao diện);
  - `round_half_up` số rất lớn: như G5 (đã chạy thử).

## Lệnh đã chạy

```
uv run pytest tests/test_soi_loi_t123.py -q                                   # 87 qua, 7 xfail
uv run pytest tests/test_tracking_*.py -q                                     # 207 qua (test của Thợ Máy)
uv run pytest <2 file trên> (worktree tạm, bản sửa nháp)                       # 7 XPASS, 294 qua
uv run python <script dò: CTR đúng nửa ≤ 2.000 lượt hiển thị, page_key, build_tracking, match_plan, periods, keywords>
uv run ruff check .; uv run ruff format --check tests/test_soi_loi_t123.py   # sạch
PYTHONUTF8=1 uvx detect-secrets scan --all-files <bản chép 8 file + file mồi>  # chỉ file mồi bị bắt
```

- Quét ký tự ẩn trên 7 file mã, 7 file test, báo cáo Thợ Máy: sạch.
- T-123 chỉ thêm file mới (`git diff --stat a499a13 2548d1f`: 14 file mới, không sửa file có sẵn), nên không có nơi gọi hàm dùng chung nào phải chạy lại.
- `origin/main` (`a499a13`) là tổ tiên của nhánh: gộp là tiến thẳng.
- Không gọi Google, WordPress thật; không chạy cloud; không chạy toàn bộ pytest.

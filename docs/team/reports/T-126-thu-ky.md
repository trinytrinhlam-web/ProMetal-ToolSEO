# Báo cáo T-126 · README «Theo dõi trên Google» (Search Console)

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-126](../tickets/T-126-readme-theo-doi-google.md) (Chỉ Huy B giao phần 1 ngày 05/11) |
| Nhánh | `team/T-126` (từ `main` cục bộ `8caab2f`) |
| Ngày nộp phần 1 | 2026-11-05 10:56 (+07:00, theo đồng hồ máy) |
| Kết quả | **Phần 1 xong** (yêu cầu 1, 2 của phiếu). Phần 2 (yêu cầu 3: cách đọc số, nút «Đưa vào kế hoạch») làm sau T-125. Chỉ sửa `README.md` và chú thích trong `.env.example`, không sửa code |
| Phần 3 | 2026-11-10 11:20 (+07:00): yêu cầu 3 của phiếu (cách đọc số) và điều kiện B.2 của Lá Chắn T-124, sau khi T-125 gộp `main`; Chỉ Huy B giao ngày 10/11, gọi là «phần 3». Phần nút «Đưa vào kế hoạch» chờ T-127. Xem mục «Phần 3» cuối báo cáo |

## Phần 1

### Tóm tắt (cho chủ dự án)

- README có **mục 15 «Theo dõi trên Google (Search Console)»**. Anh/chị làm trước 3 bước phía Google, mỗi bước làm một lần, dùng cho cả hai máy:
  1. bật «Google Search Console API» trong đúng project Google Cloud đang dùng cho Sheets;
  2. chép email tài khoản dịch vụ ở **Cài đặt → 📗 Google**;
  3. thêm email đó vào Search Console với quyền **«Hạn chế»**.
- Mục 15 cũng dặn:
  - chọn thuộc tính nào (nên dùng loại «Tiền tố URL»);
  - không dùng thuộc tính của bản thử website (staging);
  - gặp lỗi 403 thì **không nâng quyền** mà báo Chỉ Huy;
  - cách gỡ quyền khi không dùng nữa.
- Trang 📈 Theo dõi và phần chọn thuộc tính trong app **chưa có**. README ghi rõ điều này, và dặn chưa cần sửa `GSC_SITE_URL` trong `.env`.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md:604-659` (mục 15 mới, sau mục 14, trước «Dành cho người phát triển») | Đoạn mở đầu (chỉ đọc, dùng lại file khóa mục 14); khung «Hiện tại» (app chưa có phần này); «Trước khi bắt đầu» (có tài khoản dịch vụ, đăng nhập bằng chủ sở hữu, «thuộc tính» / «tài sản» / *property*); bước 1 bật API (đúng project, không cấp vai trò); bước 2 chép email (chú thích «quyền Người chỉnh sửa» trong app là nói về Sheet); bước 3 thêm email quyền «Hạn chế», không «Toàn quyền», không chủ sở hữu, Search Console không nhận thì dừng, báo Chỉ Huy; bảng «Chọn thuộc tính nào» (hai loại, dạng app lưu, staging, `http://`); bảng «Khi app báo lỗi» (4 câu: hai câu 403, thuộc tính không phải của website, sai dạng); «Giữ an toàn» (xem lại quyền, đổi khóa không đổi email, «Xoá quyền truy cập») |
| `README.md:556`, `:561` (mục 14) | Câu mở đầu thêm «(và thuộc tính Search Console bạn thêm nó vào, mục 15)». Bước 2 đổi «Chỉ cần bật API này.» thành «Phần kế hoạch chỉ cần API này; phần theo dõi Google (mục 15) bật thêm Google Search Console API trong cùng project.» Câu cũ sẽ sai khi chủ dự án làm bước 1 của mục 15 |
| `.env.example:53-59` | Chú thích `GSC_SITE_URL`: thuộc tính của website (README mục 15); nên chọn trong app ở Cài đặt → Google, mục Search Console (đang làm), app tự ghi dòng này; chỉ 2 dạng, chữ thường không dấu: `https://example.com/` («Tiền tố URL», nên dùng: `https://`, có `/` cuối, không đường con, tên miền giống hệt `WORDPRESS_URL` kể cả `www.`) và `sc-domain:example.com` («Tên miền», app chỉ lấy số liệu của `WORDPRESS_URL`); không dùng thuộc tính staging hay `http://`. Dòng `GSC_SITE_URL=` giữ nguyên, rỗng |

### Đối chiếu

**Yêu cầu 1** (phiếu; thiết kế `T-120-tho-may.md` mục 1.2, 2.1, 2.7, 2.8):

| Ý | README mục 15 |
|---|---|
| Bật «Google Search Console API» trong project đang dùng cho Sheets, không cấp thêm vai trò (1.2 bước 1) | Bước 1 |
| Chép email tài khoản dịch vụ ở Cài đặt → Google (1.2 bước 2) | Bước 2. App hiện email ở khung «🔑 Tài khoản dịch vụ Google (file khóa)» (`app/views/settings.py:573-598`, `st.code`) |
| «Cài đặt» → «Người dùng và quyền» → «Thêm người dùng» → quyền «Hạn chế»; không «Toàn quyền», không chủ sở hữu; chỉ chủ sở hữu làm được (1.2 bước 3) | Bước 3, «Trước khi bắt đầu» |
| Có cả hai loại thì chọn tiền tố; chỉ có tên miền thì dùng, app tự lọc (1.2) | Bảng «Chọn thuộc tính nào» |
| Không chọn thuộc tính staging (1.2, 2.7) | Bảng và gạch đầu dòng dưới bảng; bước 3 ý 1 «website chính»; câu báo «… (ví dụ thuộc tính staging)» |
| 403 không nâng quyền, hỏi Chỉ Huy (phiếu) | Bảng «Khi app báo lỗi» dòng 2; bước 3 (Search Console không nhận email thì báo Chỉ Huy) |
| Cùng file khóa, không khóa thứ hai; hai lớp chỉ đọc (2.1) | Đoạn mở đầu; bước 3 ý 3 |
| Câu báo cố định (2.8) | 4 câu trích khớp nguyên văn đầu câu trong `seo_app/google/search_console.py` |
| 1.2 bước 4 (trong app: «Tìm thuộc tính», lưu, «Kiểm tra») | **Không viết**: app chưa có (grep `app/` không thấy «Search Console», `GSC_SITE_URL`). Khung «Hiện tại» nói phần này viết thêm khi làm xong |

**Yêu cầu 2** (`.env.example`): đủ ba ý của phiếu, gồm hai dạng hợp lệ, nên chọn ở Cài đặt và không dùng staging. Chỉ đổi dòng chú thích.

**Đối chiếu code** (script Python đọc UTF-8, chạy trên nhánh, gọi thẳng hàm của `seo_app/google/search_console.py`): «thiếu/sai: 0» trên 38 điểm.
- 4 câu báo trong bảng là đầu câu thật: `_MSG_API_OFF`, `_MSG_BY_STATUS[403]`, `_MSG_NOT_SITE`, `_MSG_BAD_PROPERTY`.
- 3 nhãn giao diện có thật: «📗 Google», «🔑 Tài khoản dịch vụ Google (file khóa)», câu chú thích email «… (quyền Người chỉnh sửa):».
- `parse_property` nhận `https://example.com/`, `sc-domain:example.com`. Từ chối bằng câu sai dạng: `http://`, thiếu `/` cuối, chữ hoa, đường con, cổng, rỗng.
- `covers_site`:
  - tiền tố phải cùng tên máy (`www.` phải giống);
  - tên miền phủ cả `www.`;
  - `evilexample.com` không phủ;
  - thuộc tính staging (tiền tố `https://www.staging-m.example.com/` hay `sc-domain:staging-m.example.com`) không phủ `https://example.com`.
- Phạm vi `webmasters.readonly`; `from_settings` dùng `GOOGLE_SERVICE_ACCOUNT_FILE` với phạm vi đó; chỉ hai lệnh (`GET sites`, `POST query`).
- Mọi «mục N» trong README trỏ tới mục có thật.

**Trang trợ giúp Google** «Quản lý chủ sở hữu, người dùng và quyền» (`support.google.com/webmasters/answer/7687615?hl=vi`, đọc ngày 05/11):
- Đường đi: «Cài đặt > Người dùng và quyền» → «Thêm người dùng».
- Chỉ chủ sở hữu thêm, xóa người dùng được.
- Trình đơn cạnh người dùng có «Thay đổi quyền», «Xoá quyền truy cập».
- Bảng quyền: «Người dùng bị hạn chế» xem được «Hiệu suất». «Cài đặt tài sản» chỉ xem. Không «Gửi sơ đồ trang web», không «Thêm người dùng».
- Câu README «cài đặt của Search Console thì chỉ xem, không sửa được» viết theo bảng này.

### Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ uv run pytest tests/test_config.py tests/test_hash_password_script.py tests/test_la_chan_t090.py tests/test_t090_env_bang_ma.py -q
62 passed
$ uv run pytest tests/test_soi_loi_t112.py tests/test_soi_loi_t106.py -k readme -q
5 passed, 69 deselected
$ (script đối chiếu README mục 15, .env.example với code)   thiếu/sai: 0
$ PYTHONUTF8=1 uvx detect-secrets scan README.md .env.example docs/team/reports/T-126-thu-ky.md
  "results": {}
```

- Các test đã chạy:
  - `test_config.py` có hai ca đọc `.env.example`: đủ tên biến, không có giá trị thật.
  - Ba file còn lại chép `.env.example` thật hay dựng `.env` từ nó.
  - Năm ca `readme` đọc README mục 11 và dòng «Trạng thái».
- Không chạy toàn bộ pytest, không chạy ruff (không đổi file `.py`).
- `detect-secrets` có mồi đối chứng: chép 3 file vào thư mục nháp, thêm vào bản chép dòng mở đầu một khóa riêng (như trong file khóa Google) và một khóa AWS mẫu, quét từ chính thư mục đó: bắt được cả hai («Private Key», «AWS Access Key»).
- README và `.env.example` không chứa:
  - email tài khoản dịch vụ (chỉ có đuôi `.iam.gserviceaccount.com`, như mục 14);
  - mã project, đường dẫn file khóa thật, tên miền thật.

  Ví dụ dùng `ten-mien-cua-ban` (như mục 6) và `example.com` (như `.env.example`).

### Rủi ro và điểm cần chú ý

- **Nhãn trên giao diện Search Console chưa đối chiếu trên trang thật.**
  - Các nhãn đã lấy từ trang trợ giúp tiếng Việt, mà Google ghi trang đó có thể do AI dịch: «Cài đặt», «Người dùng và quyền», «Thêm người dùng», «Thay đổi quyền», «Xoá quyền truy cập».
  - «Hạn chế» / «Toàn quyền» trong ô chọn quyền và nút «Thêm» lấy theo thiết kế T-120 mục 1.2.
  - Cột «Nhận ra trong Search Console» (thuộc tính tên miền chỉ ghi tên miền, thuộc tính tiền tố ghi `https://…`) viết theo hiểu biết của tôi, chưa xem trên tài khoản thật.
- **Thêm tài khoản dịch vụ làm người dùng Search Console chưa xác minh với tài khoản thật** (T-120 mục 1.2; Lá Chắn T-121 điều kiện B4 (a)). README có lối dừng: Search Console không nhận email, hay chỉ cho thêm làm chủ sở hữu, thì báo Chỉ Huy. Nên đưa ý này vào buổi thử thật với Google.
- **Hai chỗ chỉ đúng tới khi T-124, T-125 xong**: khung «Hiện tại» của README mục 15 và chữ «(đang làm)» trong `.env.example`. Phần 2 phải sửa lại.
- Hai câu ở mục 14 đổi để không mâu thuẫn với mục 15. Không có test nào ghim hai câu này: đã grep `tests/` theo «README», «.env.example».

### Để lại cho phần 2 (sau T-125)

- Cách dùng trong app: «Tìm thuộc tính», chọn, lưu, «Kiểm tra». Bỏ khung «Hiện tại» và chữ «(đang làm)».
- Cách đọc số (yêu cầu 3), nút «Đưa vào kế hoạch».
- Câu báo mới của T-124, T-125 (đang lấy ở tab khác, 429, giới hạn 20 lệnh…).
- Cảnh báo biến môi trường `GSC_SITE_URL` đè `.env` (LC-T120-23).
- Mục 4 (menu có «📈 Theo dõi») và dòng «Trạng thái» đầu README.

### Câu hỏi cho chủ dự án

Không có.

## Phần 3 (2026-11-10, sau khi T-125 gộp `main`)

Chỉ Huy B giao ngày 10/11. Phần này làm yêu cầu 3 của phiếu (cách đọc số trên trang «📈 Theo dõi»), cộng điều kiện B.2 của Lá Chắn T-124:
- lần đầu khoảng một phút, khoảng 18 lần hỏi Google;
- bấm lại trong 10 phút thì không có gì mới;
- nghĩa của «số tạm»;
- thuộc tính chỉ chọn qua «Tìm thuộc tính»;
- biến môi trường `GSC_SITE_URL` đè `.env`.

Trước khi viết, nhánh `team/T-126` được tua thẳng (`--ff-only`) tới `main` cục bộ `7153f0a`. Bản `main` này đã có T-124, T-125 và biên bản Lá Chắn phần 1.

### Tóm tắt (cho chủ dự án)

- **README mục 15 nay hướng dẫn trọn từ đầu tới cuối:**
  - việc phía Google (bước 1–3);
  - chọn thuộc tính và kiểm tra trong app (bước 4–5, làm trên từng máy);
  - lấy số liệu;
  - đọc số;
  - bản lưu tạm;
  - các câu báo lỗi thường gặp.
- **Phần đọc số giải thích:**
  - ngày trên trang là ngày theo giờ Google;
  - số trễ 2–3 ngày, «số tạm» không hiện, không tính;
  - tổng của phần mềm có thể cao hơn biểu đồ Search Console;
  - Google ẩn bớt từ khóa;
  - 7 nhãn (tụt hạng, mất click…) với ngưỡng cụ thể.
- **README ghi rõ trang chưa thử với Search Console thật.** Sau buổi thử, Lá Chắn xem kết quả rồi mới dùng số để quyết định việc gì.
- **Nút «Đưa vào kế hoạch»** chờ phiếu T-127: README chỉ ghi chỗ, viết sau.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md:7` (dòng «Trạng thái») | Thêm «theo dõi lượt hiển thị, lượt click, vị trí từng bài trên Google qua Search Console (mục 15; chờ buổi thử với Search Console thật)» |
| `README.md:65` (mục 4, menu) | Thêm **Theo dõi** (số liệu Google của từng bài, mục 15), đúng thứ tự `PAGES` trong `app/main.py` |
| `README.md:604-757` (mục 15) | (1) Đoạn mở đầu: trang đã có, nằm giữa Kế hoạch và Cài đặt. (2) Khung «Hiện tại… chưa làm xong» thay bằng khung «Chưa thử với Search Console thật» (`:608`). (3) «Trước khi bắt đầu»: bước 4–5 làm trên từng máy. (4) Ba ghi nhận N1–N3 của Lá Chắn phần 1. (5) Mới: **Bước 4** chọn thuộc tính (`:646`), **Bước 5** Kiểm tra (`:656`), **Lấy số liệu** (`:663`), **Đọc số** (`:675`, bảng 7 nhãn `:706`), **Bản lưu tạm trên máy** (`:728`). (6) Bảng **Khi app báo lỗi** (`:737`) từ 4 lên 9 dòng, bỏ chú thích «hiện khi phần theo dõi làm xong» |
| `.env.example:54-63` | Chú thích `GSC_SITE_URL`: bỏ «(đang làm)»; ghi đường chọn trong app (khung Search Console, nút «Tìm thuộc tính», rồi «Lưu thuộc tính đã chọn»), «Đừng tự gõ»; thêm dòng «Máy có biến môi trường GSC_SITE_URL (kể cả để trống) thì biến đó được dùng thay dòng này.» Dòng `GSC_SITE_URL=` giữ nguyên, rỗng |

### Đối chiếu

| Ý (phiếu yêu cầu 3, tin Chỉ Huy, Lá Chắn T-124 B.2) | README mục 15 | Code trên `7153f0a` |
|---|---|---|
| Lần đầu khoảng một phút, khoảng 18 lần hỏi | «Lấy số liệu» | `MSG_FETCH_HELP`, `MSG_EMPTY_CACHE` («khoảng một phút»). Số 18 tính bằng `_fetch_start`, `_chunk_end`, `_default_periods` của `refresh.py`: 16 đoạn ngày × trang (16 tháng, `KEEP_DAYS` 486, mỗi đoạn ≤ 31 ngày) và 2 kỳ từ khóa |
| Bấm lại trong 10 phút | «Lấy số liệu» | `REFRESH_COOLDOWN = 10 phút`, `MSG_RECENT`, `_is_recent` |
| Nghĩa «số tạm»; trễ 2–3 ngày | «Đọc số» | `MSG_PROVISIONAL`, `stats.SHOW_PROVISIONAL = False`, `_first_provisional`; thiết kế T-120 mục 2.6 |
| Ngày theo giờ Google | «Đọc số» | `google_today` (giờ PT), dòng trạng thái «(ngày theo giờ Google)» của `tracking.py` |
| Thuộc tính chỉ chọn qua «Tìm thuộc tính» | Bước 4 ý 3 | `save_property`: chỉ nhận `found.usable_site_urls` của lần tìm trong phiên, câu `MSG_NOT_OFFERED`; `settings.py` `_save_property` |
| Biến môi trường đè `.env`, kể cả rỗng | Bước 4 ý 3; `.env.example` | `load_settings` (`if name in env`), `env_file.gsc_site_url_overridden`, câu `MSG_GSC_OVERRIDDEN` |
| Tổng theo trang khác biểu đồ Search Console | «Đọc số» | `MSG_TOTALS_NOTE`, `stats.site_totals`. Trang trợ giúp Google: dữ liệu biểu đồ «được tổng hợp theo tài sản» |
| Từ khóa bị ẩn | «Đọc số», «Từ khóa» | `keywords.HIDDEN_QUERIES_NOTE` |
| Ý nghĩa các nhãn | Bảng 7 nhãn, «Cần chú ý chỉ đếm 5 nhãn đầu» | `flags.py`: `LABELS`, thứ tự, `ATTENTION`, các hằng ngưỡng (30 lượt hiển thị, 3 bậc, vị trí 1–10, 10 click, một nửa, 14 ngày, 200 lượt hiển thị, CTR 1%, 100 lượt hiển thị) |
| Nút «Xóa bản lưu tạm» | «Bản lưu tạm trên máy» | `clear_panel`, `clear_cache` (không xóa khi tab khác đang lấy: `MSG_BUSY`), `MSG_CLEARED`. Đổi thuộc tính hay `WORDPRESS_URL` thì bản cũ tự bỏ (`SearchCacheStore.load`) |
| «Đưa vào kế hoạch» (T-127) | Một gạch đầu dòng giữ chỗ | Nút `trk-to-plan` đang khóa, `MSG_PLAN_LATER` |
| Lá Chắn phần 1 N1 | Bước 3 ý 3, bảng lỗi dòng 403 | «Theo trang trợ giúp của Google… buổi thử sẽ xác nhận»; «theo Google, «Hạn chế» là đủ» |
| Lá Chắn phần 1 N2 | Bước 3 ý 1 | «Chỉ thêm email vào đúng thuộc tính của website này…» |
| Lá Chắn phần 1 N3 | Bảng «Chọn thuộc tính nào», dòng dưới bảng | «không có đường con (`https://ten-mien-cua-ban/blog/` bị từ chối)» |

**Script đối chiếu** (đọc UTF-8, gọi thẳng hằng và hàm của code trên nhánh): «tổng: 192 thiếu/sai: 0».
- 75 câu, nhãn trích trong mục 15 có cả trong code lẫn trong README.
- 7 nhãn đúng chữ, đúng thứ tự `LABELS`; «Cần chú ý» = 5 nhãn đầu.
- 18 con số khớp hằng của code.
- «khoảng 18 lần hỏi» tính lại ở 2 ngày khác nhau.
- Bản lưu tạm: đổi phạm vi thì bỏ; xóa trong khóa.
- Mọi «mục N», «bước N» có thật.
- `.env.example`: không còn «đang làm», dòng biến rỗng.
- Không email, không tên miền thật.

### Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ git merge --ff-only 7153f0a  # trước khi viết
$ (script đối chiếu README mục 15, .env.example với code)   tổng: 192 thiếu/sai: 0
$ uv run pytest tests/test_config.py tests/test_hash_password_script.py tests/test_la_chan_t090.py tests/test_t090_env_bang_ma.py -q
62 passed
$ uv run pytest tests/test_soi_loi_t112.py tests/test_soi_loi_t106.py -k readme -q
5 passed, 69 deselected
$ uv run pytest tests/test_t092_nhap_bi_xoa.py -k "env_example or siteseo_caption" -q
2 passed, 27 deselected
$ PYTHONUTF8=1 uvx detect-secrets scan README.md .env.example docs/team/reports/T-126-thu-ky.md
  "results": {}
```

- Các test đã chạy:
  - các file đọc `.env.example` (đủ tên biến, không giá trị thật, chép làm `.env`, chú thích tài khoản Biên tập viên);
  - các ca đọc README (mục 11, dòng «Trạng thái», chú thích SiteSEO).
- `detect-secrets` có mồi đối chứng, như các phần trước.
- Không chạy toàn bộ pytest, ruff (chỉ đổi tài liệu).

### Rủi ro và điểm cần chú ý

- **README viết trước buổi thử thật** (kịch bản T-133). Ba ý theo thiết kế và trang trợ giúp của Google, chưa thấy trên số thật:
  - «Hạn chế» là đủ;
  - so từng bài với thẻ «Trang» thì khớp;
  - lần đầu khoảng một phút.

  Buổi thử khác đi thì sửa README theo kết quả thật.
- **Ngưỡng nhãn là mặc định** (T-120 câu hỏi 5, khuyến nghị A; `flags.py` ghi chủ dự án chưa trả lời). Đổi hằng trong `flags.py` thì phải sửa bảng nhãn; chạy lại script đối chiếu sẽ thấy ngay.
- **Gỡ biến môi trường:** README chỉ ghi «nhờ người hỗ trợ gỡ», không ghi từng bước Windows, Mac. Lý do: ít gặp, và cách gỡ khác nhau tùy biến được đặt ở đâu.
- **Lời khuyên cho câu «Không mở được file lưu tạm…»** («tắt chương trình khác: sao lưu, diệt virus») là ví dụ, dựa theo chính câu báo của app («có thể chương trình khác đang giữ file»).
- **Nút «Đưa vào kế hoạch»:** viết khi T-127 gộp `main`.
- **Lá Chắn phần 1 N4** (chú thích email trong Cài đặt) thuộc T-125, không phải README. Kết quả «Tìm thuộc tính» của T-125 đã ghi «(thêm vào Search Console, quyền «Hạn chế»)»; khung 🔑 vẫn chỉ nói về Sheet, README bước 2 đã giải thích.

### Câu hỏi cho chủ dự án

Không có.

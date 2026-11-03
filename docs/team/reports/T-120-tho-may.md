# Báo cáo T-120 · Thiết kế Giai đoạn 6: theo dõi bài qua Google Search Console

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-120](../tickets/T-120-thiet-ke-giai-doan-6.md) |
| Nhánh | `team/T-120` (từ `main` `29499dd`) |
| Ngày nộp | 2026-11-03 18:21 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành (phiếu thiết kế, không sửa code) |

## Tóm tắt (cho chủ dự án)

- **Giai đoạn 6 cho anh xem từng bài trên Google**: mỗi bài (và mỗi trang dịch vụ) được Google cho hiện bao nhiêu lần (lượt hiển thị), được bấm bao nhiêu lần (click), tỉ lệ bấm (CTR), đứng trung bình ở vị trí thứ mấy, và người ta gõ từ khóa gì để thấy bài. Số lấy từ Google Search Console, chỗ anh vẫn xem bằng tay.
- **Dùng lại tài khoản dịch vụ Google** đang dùng cho Google Sheets, không tạo khóa mới. Phần mềm **chỉ xem**, không sửa gì trên Search Console. Anh làm một lần: bật «Google Search Console API» trong Google Cloud, thêm email của tài khoản dịch vụ vào Search Console với quyền **«Hạn chế»** (chỉ xem), rồi chọn website ở trang Cài đặt.
- **Cách xem**: chọn khoảng 7 ngày, 28 ngày, 3 tháng (hoặc tự chọn), so với kỳ trước. Phần mềm tự đánh dấu bài **tụt hạng**, bài **mất click**, bài **đăng lâu mà chưa thấy trên Google**, bài **nhiều người thấy mà ít người bấm** (tiêu đề, mô tả chưa hấp dẫn). Mỗi bài có danh sách từ khóa, gộp cả cách gõ có dấu và không dấu («sửa cửa sắt» và «sua cua sat»).
- **Số của Google luôn chậm 2–3 ngày**, và Google tính ngày theo giờ Mỹ. Phần mềm ghi rõ «số liệu tới hết ngày …». Số của trang staging (`www.staging-m.suachuacuasat.com`, đang có trong Search Console) không bị lẫn vào.
- Số liệu chỉ lấy **khi anh bấm nút**, không chạy ngầm. Bản lưu tạm trong máy chỉ vài MB, giữ tối đa 16 tháng (bằng thời gian Google giữ). Xóa đi thì bấm lấy lại được. Hai máy, mỗi máy tự lấy từ Google, nên luôn thấy giống nhau. Mặc định **không** ghi lên Google Sheets, **không** gửi từ khóa cho AI.
- Từ khóa là chữ do người lạ gõ trên Google. Phần mềm chỉ hiện nó như chữ thường: không bao giờ chạy, không thành link.
- **Không cần cài thư viện mới.**
- Đề xuất **6 phiếu**: 5 phiếu code, 1 phiếu hướng dẫn. Chạy 3 đợt rồi thử thật; 3 phiếu đầu chạy song song được và không phải chờ anh trả lời.
- **7 câu hỏi** ở cuối báo cáo. **Câu 1: đặt trang này ở đâu trong menu**; mục 4 có phác thảo cho 3 phương án.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-120-tho-may.md` | Báo cáo này. Không sửa code, cấu hình, test |
| `docs/team/tickets/T-120-thiet-ke-giai-doan-6.md` | Chép nguyên văn phiếu của Chỉ Huy vào nhánh (theo dặn dò khi giao) |

## Nguồn đã dùng

**Code trong repo** (nhánh `team/T-120` = `main` lúc `29499dd`), dẫn `file:dòng`:

| Chỗ | Điều rút ra |
|---|---|
| `seo_app/config.py:34`, `:71`, `:95`, `:151`; `.env.example:54` | Biến `GSC_SITE_URL` **đã có sẵn** (chưa nơi nào dùng), `Settings.status()` có mục «Search Console». Không cần biến mới |
| `seo_app/google/service_account.py:44`, `:150`, `:372-386` (`_credentials`) | File khóa được kiểm lại mỗi lần tạo client; đối tượng xác thực tạo với **đúng một** phạm vi `SHEETS_SCOPE`. Search Console cần thêm một phạm vi chỉ đọc ở **đúng chỗ này** |
| `seo_app/google/sheets.py:91-111` (`_ROUTES`), `:291-314` (`_refuse_redirect`, `_read_limited`), `:346-391` (`_TokenRequest`), `:609-628` (`from_settings`), `:755`, `:788-813`, `:893-909`, `:920-928` | Lớp vận chuyển đã qua Lá Chắn Fable (T-116 nhóm 4): danh sách lệnh cố định kiểm trước khi gửi, không theo chuyển hướng, giờ chờ 30 giây, giới hạn cỡ câu trả lời, xin mã qua lớp riêng, câu lỗi cố định. Client Search Console dùng lại nguyên các phần này. Ghi chú: `_answer` (`:902`) đọc JSON **không** chặn `NaN`/`Infinity`; với số liệu Search Console (số thực) phải chặn |
| `seo_app/storage/site_index.py:1-10`, `:38`, `:59`; `seo_app/wordpress/client.py:48`, `:839-875`, `:1163-1190` | Danh sách bài **và trang** đã đăng (`PublishedItem`: `id`, `type`, `slug`, `link`, `title`…), link đã kiểm `https://` đúng tên máy; cache 6 giờ. **Không có ngày đăng** (`_PUBLISHED_FIELDS` không có `date_gmt`) |
| `seo_app/wordpress/client.py:199-203`, `:805-814`, `:1659` (`post_statuses`) | Lệnh chỉ đọc đã có, trả `date_gmt` của tối đa 1.000 bài (chỉ bài, không trang): dùng để biết ngày đăng khi cần, không sửa client WordPress |
| `seo_app/wordpress/client.py:2322` (`is_site_link`) | Bộ kiểm «địa chỉ đúng website» dùng lại cho địa chỉ trang Search Console trả |
| `seo_app/plan/model.py:111-128` (`SHEET_COLUMNS`), `:159` (`clean_text`), `:183` (`fold_key`), `:402-415` (`personal_info`, `mask_personal_info`) | Sheet kế hoạch **không có cột địa chỉ bài**: khớp qua «Mã bài WordPress» (cột N), «Slug» (cột K). Có sẵn bộ làm sạch chữ, khóa so không dấu, bộ dò số điện thoại và email |
| `seo_app/storage/plan_cache.py:315-326` | Mẫu chặn `NaN` khi đọc JSON (`_reject_constant`); bài học LC-T113-2 (mốc sát năm 9999 làm tràn khi đổi múi giờ) |
| `seo_app/images/data_dir.py:35`, `:43` (`is_link`, `dir_has_link`) | Bộ kiểm «`data/` không phải liên kết» của T-117, dùng cho cache mới |
| `seo_app/env_file.py:54`, `:378-413`, `:431` | Mẫu ghi một biến vào `.env` có bộ kiểm chặt (mã Sheet); báo khi biến môi trường của máy đè `.env` |
| `app/main.py:25-31` (`PAGES`), `app/views/home.py:280-313`, `app/views/plan.py:218-229` (`safe_rows`), `:1041`; `seo_app/text.py:44-56` | Menu 5 mục; trang Bài viết có hai cột «Tiếp theo trong kế hoạch», «Đã gửi WordPress»; bảng hiện chữ thuần có trung hòa công thức; `escape_markdown`, `markdown_link` |
| `git show 863f1f4:app/views/rankings.py` | Trang demo «Thứ hạng» ngày 06/10 (khoảng thời gian, chọn bài, 4 ô số có so sánh, biểu đồ click và vị trí theo tuần, bảng từ khóa, bảng mọi bài). Trang này bị bỏ khi làm lại giao diện tập trung viết bài cùng ngày (`55b75eb`) |
| `uv.lock:17`, `:406`, `:1429`, `:1653`, `:1732`; `pyproject.toml:12`, `:27` | `google-auth` 2.62.0 và `requests` 2.34.2 **đã khai báo**; `tzdata` 2026.5 có sẵn; `altair` 6.3.0 chỉ có nhờ Streamlit 1.65.0 (chưa khai báo) |

**Tài liệu của chủ dự án**: `docs/plan/bang_dieu_khien_theo_doi_vi.md` (chỉ số muốn theo dõi), `docs/plan/review_ke_hoach_v1.md:152` (Search Console có thuộc tính `www.staging-m.suachuacuasat.com`), `:155` (chưa có nguồn số liệu từ khóa), `:174` («có dữ liệu rồi mới chọn bài»), `docs/plan/README.md`.

**Tài liệu công khai của Google** (chỉ đọc trang web, không gọi API):

| Trang | Điều rút ra |
|---|---|
| `developers.google.com/webmaster-tools/v1/searchanalytics/query` | `POST …/sites/{siteUrl}/searchAnalytics/query`; phạm vi `webmasters.readonly` hoặc `webmasters`; ngày `YYYY-MM-DD` **theo giờ Thái Bình Dương (PT)**, tính cả hai đầu; `dimensions` (`date`, `page`, `query`…); bộ lọc `equals`, `contains`, `includingRegex` (cú pháp RE2), chỉ nhóm `and`; `aggregationType` `auto`/`byPage`/`byProperty` (`byProperty` không dùng được khi nhóm hay lọc theo trang); `rowLimit` 1–25.000 (mặc định 1.000), `startRow` để lật trang; `dataState` `final` (mặc định), `all`, `hourly_all`; trả `rows[].keys`, `clicks`, `impressions` (số thực), `ctr` (0–1), `position`, `responseAggregationType`, `metadata.first_incomplete_date` (khi `dataState = all` và nhóm theo ngày); xếp theo click giảm dần (theo ngày tăng dần khi nhóm theo ngày); ngày không có số liệu thì không có dòng; không bảo đảm trả **mọi** dòng |
| `…/webmaster-tools/v1/api_reference_index`, `…/sites`, `…/sites/list` | Địa chỉ gốc `https://www.googleapis.com/webmasters/v3` (Search Analytics, Sites), `https://searchconsole.googleapis.com/v1` (URL Inspection); `GET /sites` trả `siteEntry[]` (`siteUrl`, `permissionLevel`: `siteOwner`, `siteFullUser`, `siteRestrictedUser`, `siteUnverifiedUser`); thuộc tính tên miền dạng `sc-domain:example.com`, tiền tố dạng `https://www.example.com/` |
| `…/webmaster-tools/limits` | Hạn mức «tải» ngắn hạn (khung 10 phút; quá thì đợi 15 phút) và dài hạn (khung 1 ngày); nhóm/lọc theo trang và từ khóa là tốn nhất, khoảng ngày dài tốn hơn, hỏi lặp lại cùng số liệu cũng tốn; 1.200 lệnh/phút mỗi thuộc tính và mỗi người dùng; URL Inspection 2.000 lệnh/ngày, 600/phút mỗi thuộc tính; quá hạn mức trả lỗi `quotaExceeded` |
| `…/webmaster-tools/v1/how-tos/all-your-data` | Tối đa 50.000 dòng mỗi ngày mỗi loại tìm kiếm; lật trang bằng `startRow` tới khi hết dòng; số liệu thường có sau 2–3 ngày; tìm ngày mới nhất bằng một lệnh nhóm theo ngày 10 ngày gần nhất; tổng theo trang khác tổng theo website |
| `…/webmaster-tools/v1/urlInspection.index/inspect` | `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`, chỉ trả trạng thái đã lập chỉ mục (không thử trang trực tiếp) |
| `support.google.com/webmasters/answer/2451999` | Quyền: Chủ sở hữu, Toàn quyền, **Hạn chế** (xem được báo cáo Hiệu suất); chỉ chủ sở hữu thêm được người dùng (Cài đặt → Người dùng và quyền → Thêm người dùng); tối đa 100 người không phải chủ sở hữu. Trang này **không** nói riêng về tài khoản dịch vụ |
| `support.google.com/webmasters/answer/96568`, `/answer/17011259`, `/answer/7576553`; `developers.google.com/search/blog/2022/10/performance-data-deep-dive` | Ngày theo giờ California; số liệu thường có sau 2–3 ngày; số liệu gán cho **địa chỉ chuẩn (canonical)** của trang, nhóm theo địa chỉ cuối sau chuyển hướng; từ khóa hiếm (ít hơn vài chục người gõ trong 2–3 tháng) và từ khóa có thông tin cá nhân **bị ẩn**, nên cộng các dòng từ khóa ra ít hơn tổng; biểu đồ tính theo website, bảng «Trang» tính theo trang |
| Trợ giúp Google Analytics, blog Search Central 01/2018 (qua tìm kiếm) | Search Console giữ số liệu Hiệu suất **16 tháng** |

**Không** gọi Search Console, Google Sheets hay website thật; không đọc `.env`.

---

## 1. Luồng người dùng (yêu cầu 1)

### 1.1 Toàn cảnh

```
 (một lần) Chủ dự án: bật Google Search Console API · thêm email tài khoản dịch vụ, quyền «Hạn chế»
        │
        ▼
 Cài đặt → Google → Search Console: «Tìm thuộc tính» → chọn thuộc tính khớp website → lưu
        │
        ▼
 Trang theo dõi (vị trí trong menu: câu hỏi 1) ── «🔄 Lấy số liệu mới» ──► Search Console (chỉ đọc)
        │                                                                   │
        │          số liệu từng ngày × từng trang, từ khóa của 2 kỳ đang xem ◄┘
        ▼
 Cache trong máy (data/search_console.sqlite)
        │
        ▼
 Khớp địa chỉ trang ↔ danh sách bài, trang đã đăng (SiteIndex) ↔ dòng kế hoạch (Mã bài WordPress)
        │
        ▼
 Bảng bài: click, hiển thị, CTR, vị trí, so kỳ trước, nhãn ──► chi tiết một bài: biểu đồ, từ khóa
```

### 1.2 Kết nối thuộc tính Search Console (làm một lần)

**Hai loại thuộc tính** (tài liệu `sites`):

| Loại | `siteUrl` | Gồm những gì | Với app này |
|---|---|---|---|
| Tên miền (Domain) | `sc-domain:suachuacuasat.com` | mọi địa chỉ của tên miền: `https://`, `http://`, `www.`, mọi tên miền con, **kể cả** `www.staging-m.suachuacuasat.com` | dùng được; app luôn lọc đúng phần của website (mục 2.7) |
| Tiền tố URL (URL-prefix) | `https://suachuacuasat.com/` (có `/` cuối) | chỉ địa chỉ bắt đầu đúng như vậy; `http://…` hay `www.…` là thuộc tính khác | dùng được, gọn nhất: tài khoản dịch vụ chỉ thấy đúng website |

Quy tắc của app (kiểm mỗi lần tạo client, phiếu T-121):

- `GSC_SITE_URL` chỉ nhận hai dạng: `sc-domain:<tên miền>` (chữ thường không dấu, số, `-`, `.`; tên miền tiếng Việt phải ở dạng `xn--`) hoặc `https://<tên máy>/`. Từ chối `http://…` (website chạy `https://`, mọi link app nhận đều phải `https://`).
- Thuộc tính phải **phủ** `WORDPRESS_URL`: dạng tên miền thì tên máy của website bằng tên miền đó hoặc là tên miền con của nó; dạng tiền tố thì `WORDPRESS_URL` + `/` bắt đầu bằng tiền tố. Thuộc tính staging `https://www.staging-m.suachuacuasat.com/` không phủ `https://suachuacuasat.com` nên bị từ chối bằng câu cố định.
- Mọi lệnh lấy số liệu có bộ lọc trang theo tiền tố của **website** (mục 2.7). Vậy với thuộc tính tên miền, số liệu của staging, `www.`, `http://` không vào app.

**Việc chủ dự án làm** (README hướng dẫn từng bước, phiếu T-126):

1. Google Cloud, **đúng project** của tài khoản dịch vụ đang dùng cho Sheets: «API và dịch vụ» → «Thư viện» → bật **Google Search Console API**. Không cấp thêm vai trò (role) nào cho tài khoản dịch vụ trong project.
2. Phần mềm, Cài đặt → Google: chép email tài khoản dịch vụ (đã hiện sẵn ở đó).
3. Search Console, chọn thuộc tính của website → «Cài đặt» → «Người dùng và quyền» → «Thêm người dùng» → dán email → quyền **«Hạn chế»** (Restricted) → «Thêm». Không chọn «Toàn quyền», không thêm làm chủ sở hữu. Chỉ chủ sở hữu thuộc tính làm được bước này.
4. Phần mềm, Cài đặt → Google → Search Console: bấm «Tìm thuộc tính», chọn thuộc tính, bấm lưu (câu hỏi 2), rồi «Kiểm tra».

Nếu có sẵn cả hai loại, nên chọn **tiền tố** `https://suachuacuasat.com/`: tài khoản dịch vụ chỉ thấy đúng website, không thấy số liệu staging. Nếu chỉ có thuộc tính tên miền thì dùng nó, app tự lọc.

Thêm tài khoản dịch vụ làm người dùng Search Console là cách làm phổ biến, nhưng trang trợ giúp quyền của Google không nói riêng về tài khoản dịch vụ: **chưa xác minh** với tài khoản của chủ dự án, kiểm ở lượt thử thật.

**Trong app** (mục «Search Console» của Cài đặt → Google, phác thảo ở mục 4.4):

- «Tìm thuộc tính»: `GET /sites`. Hiện các thuộc tính tài khoản dịch vụ thấy được, kèm quyền (Chủ sở hữu / Toàn quyền / Hạn chế / Chưa xác minh) và «khớp website hay không». Thuộc tính không phủ `WORDPRESS_URL` hay quyền «Chưa xác minh» thì không chọn được. Quyền cao hơn «Hạn chế» thì Cảnh báo «chỉ cần quyền Hạn chế, nên hạ xuống».
- Lưu: ghi `GSC_SITE_URL` vào `.env` như cách ghi mã Sheet (câu hỏi 2, lựa chọn A), hoặc chủ dự án tự gõ (lựa chọn B).
- «Kiểm tra»: (a) thuộc tính có trong danh sách `/sites` và quyền là gì; (b) một lệnh nhóm theo ngày 10 ngày gần nhất → «có số liệu tới hết ngày …» hoặc «chưa có số liệu»; (c) với thuộc tính tên miền: một lệnh nhóm theo trang 28 ngày, **không** lọc, chỉ để đếm phần lượt hiển thị nằm ngoài website («2% nằm ở www.staging-m…: không tính»). Nếu gần hết lượt hiển thị nằm ngoài website thì báo «Google đang ghi số liệu cho địa chỉ khác `WORDPRESS_URL` (ví dụ có `www.`)», vì khi đó bộ lọc sẽ ra số 0.

### 1.3 Lấy số liệu (chỉ khi bấm nút)

Nút «🔄 Lấy số liệu mới» (phiếu T-124):

1. Kiểm `GSC_SITE_URL`, `WORDPRESS_URL`, file khóa (phạm vi Search Console), như `SheetsClient.from_settings`.
2. Danh sách bài đã đăng (SiteIndex): cũ hơn 6 giờ thì tải lại bằng lệnh đọc WordPress đang có (`list_published`). WordPress lỗi thì dùng bản cũ, báo «danh sách bài lúc …»; số liệu vẫn lấy được, chỉ có thể còn trang chưa khớp bài.
3. Tính khoảng cần lấy. Lần đầu: **16 tháng** (486 ngày, đúng phần Google còn giữ; đủ so «cùng kỳ năm trước» cho mọi khoảng tới 3 tháng). Các lần sau: từ ngày đầu tiên còn là số **tạm** (hoặc ngày sau ngày đã chốt cuối cùng) tới hôm nay theo giờ PT.
4. Chia khoảng thành từng đoạn ≤ 31 ngày, mỗi đoạn một lệnh «ngày × trang» (khuôn Q1, mục 2.3), lật trang khi đủ 25.000 dòng. Dòng có ngày ≥ `metadata.first_incomplete_date` đánh dấu **tạm**. Ghi cache từng đoạn, từ cũ tới mới. Gặp lỗi thì dừng, giữ phần đã lấy, lần sau lấy tiếp.
5. Từ khóa: lệnh «trang × từ khóa» (khuôn Q2) cho kỳ đang xem và kỳ so sánh mặc định (28 ngày, kỳ trước liền kề). Kỳ khác mà cache chưa có thì phần từ khóa có nút «Lấy từ khóa cho khoảng này».
6. Ngày đăng: với **bài** (không phải trang) có 0 lượt hiển thị trong cả hai kỳ, hỏi `post_statuses` (chỉ đọc, đã có) để biết `date_gmt`, phục vụ nhãn «chưa có lượt hiển thị» / «mới đăng» (mục 1.6).
7. Kết quả: «Đã lấy số liệu tới hết ngày 31/10 (ngày theo giờ Google). 2 ngày gần nhất còn tạm, chưa tính.» Kèm số dòng lạ bị bỏ (nếu có).

Số lệnh: lần đầu khoảng 16 + 2; các lần sau 1–2 + 2. Bấm lại trong vòng 10 phút mà ngày chốt cuối chưa đổi thì không gửi lệnh, báo «vừa lấy lúc …; Google cập nhật khoảng một lần mỗi ngày» (tài liệu hạn mức: hỏi lặp lại cùng số liệu cũng tốn hạn mức).

### 1.4 Khớp địa chỉ trang với bài WordPress và dòng kế hoạch

Search Console gán số liệu cho **địa chỉ chuẩn** của trang. Khóa so khớp `page_key(url)` (phiếu T-123):

| Bước | Quy tắc |
|---|---|
| 1 | `is_site_link(url, WORDPRESS_URL)` đúng **và** bắt đầu bằng `WORDPRESS_URL` + `/`. Sai thì bỏ dòng, đếm «dòng lạ» |
| 2 | Bỏ phần `#…` (vẫn là cùng một trang); hai dòng trùng khóa sau khi bỏ thì cộng dồn |
| 3 | Có `?…` (ví dụ `?s=`, `?p=`): giữ riêng, xếp vào «Trang khác», không gán cho bài |
| 4 | Đường dẫn: giải mã `%` (UTF-8 hỏng → dòng lạ), chuẩn NFC, bỏ `/` cuối (trừ trang chủ); giữ nguyên chữ hoa, chữ thường |
| 5 | Link của mọi `PublishedItem` trong SiteIndex chuẩn hóa cùng cách → bảng tra khóa → bài hoặc trang (`id`, `type`, `title`) |

Dòng kế hoạch → bài:

- `PlanRow.wp_post_id` bằng `id` của một bài (`type = post`) trong SiteIndex.
- Dòng chưa có mã: so `PlanRow.slug` với `slug` của bài; chỉ nhận khi đúng **một** bài khớp.
- Dòng chưa lên website (Chưa viết, Đang viết, Đã gửi nháp, Đã hẹn giờ) → «Chưa lên website», không có số liệu.
- **Không bao giờ** dùng địa chỉ lấy từ Sheet (như LC-T094-20: Sheet chỉ giữ mã bài): địa chỉ luôn lấy từ SiteIndex (WordPress) và Search Console, cả hai đã qua `is_site_link`.

Trang không khớp bài nào → mục «Trang khác trên website»: trang chủ (nếu không phải trang tĩnh), chuyên mục, thẻ, địa chỉ cũ trước khi đổi slug (Google còn giữ số liệu cũ ở địa chỉ cũ), trang tìm kiếm, trang ảnh đính kèm. Mỗi dòng hiện đường dẫn đã giải mã (chữ thuần, cắt 120 ký tự) kèm số liệu.

Tracking gồm cả **trang** WordPress (các trang dịch vụ như `/sua-cua-keo-tphcm/`), không chỉ bài: `review_ke_hoach_v1.md` khuyên «tối ưu 29 URL đang có trước khi viết mới».

### 1.5 Xem theo khoảng ngày, so hai kỳ

- **E** = ngày đã chốt cuối cùng trong cache (giờ PT). Khoảng: 7 ngày, **28 ngày** (mặc định), 3 tháng (91 ngày, tròn 13 tuần), hoặc tự chọn (hai ô ngày, trong phạm vi cache, tối đa 16 tháng). Khoảng N ngày là `[E − N + 1, E]`.
- **So với**: kỳ trước liền kề `[E − 2N + 1, E − N]` (mặc định), hoặc cùng kỳ năm trước (lùi 364 ngày để giữ đúng thứ trong tuần; chỉ khi cache có đủ). 7, 28, 91 ngày là bội của 7 nên hai kỳ luôn có cùng số ngày thứ Bảy, Chủ nhật.
- Số của một trang trong một kỳ, cộng từ bảng «ngày × trang»:
  - click = Σ click; hiển thị = Σ lượt hiển thị; CTR = click / hiển thị;
  - vị trí trung bình = Σ(vị trí × lượt hiển thị) / Σ lượt hiển thị. Đây là trung bình theo lượt hiển thị. Suy luận rằng Search Console tính đúng như vậy cho một trang trong cả khoảng; **kiểm ở lượt thử thật** bằng cách so với bảng «Trang» trong Search Console.
- Chênh lệch hiện: click «+12 (+30%)», hiển thị, CTR «+0,3 điểm», vị trí «lên 2,1 bậc» (xanh) / «xuống 3,4 bậc» (đỏ); số nhỏ hơn là đứng cao hơn. Viết số kiểu Việt Nam: `9.800`, `4,2%`.
- **Ít dữ liệu**: một trong hai kỳ dưới 30 lượt hiển thị thì không so vị trí, CTR, ghi «ít dữ liệu».
- **Tổng toàn website** cộng theo từng trang. Biểu đồ của Search Console tính theo website (một lượt tìm có hai trang của site chỉ tính một lượt hiển thị), nên tổng của app **có thể cao hơn chút**. Giao diện ghi chú điều này; bảng «Trang» của Search Console thì phải khớp.

### 1.6 Đánh dấu bài

Nhãn do code đặt, câu giải thích do code viết sẵn (chèn số, không chèn chữ của Google). Ngưỡng mặc định ở câu hỏi 5; đặt thành hằng số có tên trong `seo_app/tracking/flags.py`, đổi được không phải sửa logic.

| Nhãn | Điều kiện mặc định (so kỳ đang xem với kỳ so sánh) | Gợi ý hiện kèm |
|---|---|---|
| 🔻 **Tụt hạng** | cả hai kỳ ≥ 30 lượt hiển thị, và vị trí trung bình kém đi ≥ 3 bậc **hoặc** từ trang 1 (≤ 10) rơi ra ngoài (> 10) | Xem từ khóa nào tụt (mục 1.7); kiểm bài còn đúng ý định tìm kiếm, có bài mới của đối thủ |
| 📉 **Mất click** | kỳ trước ≥ 10 click, kỳ này ≤ một nửa | Như trên; kiểm tiêu đề có bị đổi |
| 👻 **Chưa có lượt hiển thị** | 0 lượt hiển thị cả hai kỳ; với bài: đã đăng ≥ 14 ngày trước E (ngày đăng từ `post_statuses`, đổi sang ngày PT) | Kiểm Google đã lập chỉ mục chưa (Search Console → Kiểm tra URL; câu hỏi 6), có link nội bộ tới bài chưa |
| 🌱 **Mới đăng** | bài đăng < 14 ngày trước E | Chờ thêm; Google cần vài ngày tới vài tuần |
| 👀 **Nhiều hiển thị, ít click** | ≥ 200 lượt hiển thị, vị trí ≤ 10, CTR < 1% | Tiêu đề, mô tả SEO có thể chưa hấp dẫn. Sửa trong SiteSEO trên website (app không sửa bài đã đăng) |
| 🔺 **Lên hạng** | ngược với «Tụt hạng» | — |
| 🎯 **Từ khóa chính chưa có** | bài có dòng kế hoạch, ≥ 100 lượt hiển thị, nhưng không từ khóa nào trùng từ khóa chính (so không dấu, `fold_key`) | Bài đang được tìm bằng từ khác (xem bảng từ khóa) |

Dòng tóm tắt đầu trang: «Cần chú ý: 2 bài tụt hạng · 3 bài chưa có lượt hiển thị · 1 bài nhiều hiển thị ít click». Bấm vào thì lọc bảng.

### 1.7 Từ khóa của một bài

- Bảng: từ khóa (chữ thuần), click, hiển thị, CTR, vị trí, chênh vị trí so kỳ trước (nếu kỳ trước có). Mặc định 50 dòng đầu theo click, có nút xem thêm.
- **Gộp có dấu, không dấu**: các từ khóa có cùng `fold_key` («sửa cửa sắt», «sua cua sat», «Sửa  cửa sắt») gộp một dòng (cộng click, hiển thị; vị trí trung bình theo lượt hiển thị), mở ra xem từng cách gõ. Người dùng ở Việt Nam hay gõ không dấu, nên gộp lại mới thấy đúng sức của một từ khóa.
- Dòng có `fold_key` trùng **từ khóa chính** của dòng kế hoạch thì gắn nhãn «từ khóa chính».
- «Từ khóa mới»: có ở kỳ này, không có ở kỳ trước.
- Ghi chú cố định dưới bảng: «Google ẩn từ khóa hiếm và từ khóa có thông tin cá nhân, nên cộng các dòng ở đây ít hơn tổng của bài» (tài liệu Google, mục Nguồn).
- Biểu đồ của bài: click mỗi tuần và vị trí trung bình mỗi tuần (trục đảo: lên cao là tốt). Tuần là khối 7 ngày kết thúc ở E, để tuần cuối luôn đủ ngày.

### 1.8 Đối chiếu với bảng điều khiển chủ dự án soạn (`bang_dieu_khien_theo_doi_vi.md`)

| Trong tài liệu | Giai đoạn 6 |
|---|---|
| Tổng click, hiển thị, CTR, vị trí trung bình | Có (mục 1.5) |
| Theo dõi từng trang, xu hướng theo tuần | Có (bảng bài, biểu đồ tuần) |
| Theo dõi từ khóa cụ thể, từ khóa mới | Có theo từng bài (mục 1.7); «số từ khóa vào top 10» cho cả site có thể thêm sau từ cùng số liệu |
| Mục tiêu số theo tháng | **Không**: là số phỏng đoán của kế hoạch bản v1 (`review_ke_hoach_v1.md`) |
| Google Analytics 4 (người dùng, chuyển đổi, cuộc gọi), Ahrefs, citation, backlink | Không (mục 7) |
| Xuất Sheets hàng tuần | Không mặc định (câu hỏi 4) |

---

## 2. API (yêu cầu 2)

### 2.1 Phạm vi quyền, tài khoản dịch vụ

- Phạm vi mới duy nhất: `https://www.googleapis.com/auth/webmasters.readonly`. **Không bao giờ** dùng `…/auth/webmasters` (đọc-ghi).
- `seo_app/google/service_account.py` thêm `SEARCH_CONSOLE_SCOPE` và tham số `scope` cho `load_service_account` (mặc định `SHEETS_SCOPE`, nên client Sheets không đổi gì). Chỉ nhận đúng hai phạm vi cố định; phạm vi khác → `ServiceAccountError` câu cố định. `_credentials(info, scope)` vẫn tạo đối tượng với **đúng một** phạm vi.
- Mỗi client một đối tượng xác thực, một mã truy cập, một phạm vi: mã của Sheets không đọc được Search Console, mã của Search Console không ghi được Sheet.
- Cùng file khóa `GOOGLE_SERVICE_ACCOUNT_FILE`, **không có khóa thứ hai**. File được kiểm lại từ đầu mỗi lần bấm (ngoài thư mục dự án, ngoài thư mục ảnh, `token_uri` đúng của Google…), như Sheets.
- Hai lớp «chỉ đọc» độc lập: phạm vi `readonly` của mã truy cập, và quyền «Hạn chế» trên thuộc tính. Code lỡ gọi lệnh ghi thì Google vẫn từ chối.

### 2.2 Có cần thư viện mới không

| Cách | Thư viện | Đánh giá |
|---|---|---|
| **A. `google-auth` + `requests` + lớp vận chuyển của `sheets.py`** | Cả hai **đã khai báo** trong `pyproject.toml` (T-097); `uv.lock` không đổi | **Khuyến nghị**. Dùng lại đúng các lớp chặn Lá Chắn đã kiểm: không theo chuyển hướng, giờ chờ, giới hạn cỡ, xin mã qua `_TokenRequest` |
| B. `google-api-python-client` (thư viện chính thức của Google) | Gói mới, kéo thêm vài gói phụ thuộc (`httplib2`, `google-api-core`…) | Không cần: app chỉ gọi 2 lệnh REST. Gói này gọi mạng qua `httplib2` của nó, nên các lớp chặn trên không áp được; phải duyệt và quét thêm thư viện |
| Biểu đồ | `st.vega_lite_chart` có sẵn trong Streamlit (đặc tả dạng dict, đảo được trục vị trí) | Không nhập `altair` trực tiếp. Gói có sẵn nhờ Streamlit, nhưng dùng thẳng thì phải khai báo (R6, như `google-auth`) |
| Ngày theo giờ PT | `zoneinfo` + `tzdata` (đã có) | |
| Cache | `sqlite3` (thư viện chuẩn) | |

Kết luận: **không thêm thư viện**, không cần chủ dự án duyệt gì về thư viện. Nếu sau này muốn dùng B thì phải hỏi riêng (R6).

Client Search Console **nhập** các phần dùng chung từ `seo_app/google/sheets.py` (`_TokenRequest`, `_refuse_redirect`, `_read_limited`, `_Bearer`, `_NoAuth`, `_Redirected`, `_TooLarge`, `_close_and_status`, `_refresh_message`), **không sửa `sheets.py`**. Dời chúng sang một module chung (`seo_app/google/transport.py`) là việc dọn sau. Lý do chưa dời ngay: test Sheets vá tên trong `sheets.py`, dời hàm sẽ làm lệch chỗ vá (bài học shared-helper T-041, T-091).

### 2.3 Đường gọi cố định của client Search Console

Như `_ROUTES` của Sheets: danh sách cố định, kiểm **trước khi gửi** ở một chỗ (`_check_call`), sai là không gửi.

| Lệnh | Địa chỉ | Dùng khi | Ràng buộc |
|---|---|---|---|
| `sites` | `GET https://www.googleapis.com/webmasters/v3/sites` | Cài đặt: «Tìm thuộc tính», «Kiểm tra» | Không tham số, không thân; câu trả lời ≤ 256 KB, ≤ 200 mục |
| `query` | `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query` | Lấy số liệu, «Kiểm tra» | `{siteUrl}` đúng bằng `quote(GSC_SITE_URL, safe="")` của thuộc tính đã kiểm (ví dụ `https%3A%2F%2Fsuachuacuasat.com%2F`); thân đúng một trong 3 khuôn dưới |
| `inspect` (chỉ khi câu hỏi 6 = B) | `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` | Kiểm một bài đã lập chỉ mục chưa | Thân `{inspectionUrl, siteUrl, languageCode}`, `inspectionUrl` là link của bài trong SiteIndex |

Ba khuôn thân của `query` (mọi khuôn: `type = "web"`, `aggregationType = "byPage"`, không khóa nào khác):

| Khuôn | `dimensions` | `dataState` | Khoảng ngày | `rowLimit` · `startRow` | `dimensionFilterGroups` |
|---|---|---|---|---|---|
| **Q1** ngày × trang | `["date", "page"]` | `all` | ≤ 31 ngày | 25.000 · bội của 25.000, ≤ 200.000 | `[{groupType: "and", filters: [{dimension: "page", operator: "includingRegex", expression: <tiền tố>}]}]` |
| **Q2** trang × từ khóa | `["page", "query"]` | `final` | ≤ 93 ngày | 5.000 · bội của 5.000, ≤ 50.000 | như Q1 |
| **Q3** kiểm tra | `["page"]` hoặc `["date"]` | `final` | ≤ 28 ngày | ≤ 200 · 0 | Q3 nhóm theo trang: **không** lọc (chỉ đếm phần ngoài website, mục 1.2); Q3 nhóm theo ngày: như Q1 |

- `<tiền tố>` = `^` + `re.escape(WORDPRESS_URL + "/")`, ví dụ `^https://suachuacuasat\.com/`. Dựng từ `WORDPRESS_URL` lúc tạo client, `_check_call` dựng lại và so **nguyên văn**. Tên máy phải là chữ ASCII (cú pháp RE2 của Google).
- Ngày: `YYYY-MM-DD` dựng từ `date.isoformat()`; đầu ≤ cuối; cuối ≤ hôm nay theo PT; đầu ≥ hôm nay − 486 ngày (16 tháng).
- Chỉ `www.googleapis.com` (đúng hai đường trên) và máy chủ mã `https://oauth2.googleapis.com/token` (thêm `searchconsole.googleapis.com` nếu câu hỏi 6 = B). Không có lệnh ghi nào tới Search Console (không `sites.add`, `sites.delete`, `sitemaps.submit`…).
- Như Sheets: giờ chờ ≤ 30 giây; `allow_redirects=False` và móc `_refuse_redirect`; đọc theo luồng; `_NoAuth` (không đọc `.netrc`) và `_Bearer` (che mã khi in); xin mã qua `_TokenRequest`; client tạo mới mỗi lần bấm, không giữ qua các lần (không `st.cache_resource`).

### 2.4 Kiểm câu trả lời (dữ liệu chưa tin cậy)

| Phần | Kiểm | Sai thì |
|---|---|---|
| Thân | JSON object; không trùng khóa (`object_pairs_hook`); không `NaN`/`Infinity` (`parse_constant`, như `plan_cache._reject_constant`); bắt `RecursionError`; ≤ 8 MB (`query`), ≤ 256 KB (`sites`) | Bỏ cả lần gọi, câu cố định «dữ liệu không đúng dạng (mã …)» |
| `responseAggregationType` | có thì phải là `byPage` | Như trên |
| `rows` | không có = không có số liệu; có thì là danh sách, ≤ `rowLimit` | Như trên |
| `keys` | danh sách chữ, đúng số chiều đã hỏi. Ngày: `YYYY-MM-DD` hợp lệ, trong khoảng đã hỏi. Trang: ≤ 2.000 ký tự, qua `is_site_link` và tiền tố website (Q3 không lọc: dòng ngoài website chỉ lấy tên máy, kiểm đúng dạng tên miền, để đếm và hiện tối đa 3 tên máy; không giữ địa chỉ). Từ khóa: ≤ 2.048 ký tự, qua `clean_text` (bỏ ký tự điều khiển, ký tự vô hình, ký tự đảo hướng chữ; NFC), cắt còn 200 ký tự; rỗng sau làm sạch thì bỏ | Bỏ dòng, đếm |
| `clicks`, `impressions` | số thật (không `bool`), hữu hạn, là số nguyên; 0 ≤ click ≤ hiển thị ≤ 10⁹; hiển thị ≥ 1 | Bỏ dòng |
| `ctr` | 0 … 1 | Không dùng để tính (app tự tính lại) |
| `position` | hữu hạn, 1 ≤ vị trí ≤ 10.000 | Bỏ dòng |
| `metadata.first_incomplete_date` | ngày hợp lệ trong khoảng đã hỏi. Tài liệu ghi tên trường dạng `first_incomplete_date`; lượt thử thật xác nhận tên thật. Đoạn cũ (đã chốt hết) không có trường này là bình thường | Sai dạng, hoặc thiếu ở đoạn mới nhất (đoạn kết thúc hôm nay PT): coi 3 ngày cuối của đoạn là số tạm (hướng an toàn) |
| Tỉ lệ dòng bị bỏ | > 10% số dòng của một lần gọi | Bỏ cả lần gọi |
| `siteEntry` (`sites`) | ≤ 200 mục; `siteUrl` qua bộ đọc thuộc tính (1.2); `permissionLevel` thuộc 4 giá trị | Bỏ mục |

### 2.5 Giới hạn số dòng, hạn mức

| Giới hạn của Google (mục Nguồn) | App làm |
|---|---|
| ≤ 25.000 dòng một lệnh, lật bằng `startRow` | Lật tới khi một trang trả ít hơn `rowLimit`; trần `startRow` (2.3) để không lặp mãi |
| ≤ 50.000 dòng mỗi ngày mỗi loại tìm kiếm; chỉ trả «các dòng đầu» | Website nhỏ (vài chục tới vài trăm trang có lượt hiển thị mỗi ngày) không chạm. Chạm trần thì đánh dấu «có thể thiếu dòng» trên giao diện |
| Hạn mức tải ngắn hạn (10 phút) / dài hạn (1 ngày); trang × từ khóa và khoảng dài là tốn nhất | Q1 chia đoạn ≤ 31 ngày; Q2 chỉ cho 2 kỳ đang xem; mỗi lần bấm ≤ 20 lệnh (cần nhiều hơn thì dừng, giữ phần đã lấy, lần bấm sau lấy tiếp), chạy lần lượt, không song song; chặn bấm lại < 10 phút (1.3) |
| 1.200 lệnh/phút mỗi thuộc tính, mỗi người dùng | App gửi vài lệnh mỗi lần bấm |
| Quá hạn mức: lỗi `quotaExceeded` (429) | Thử lại **1 lần** sau 2 giây (cộng ngẫu nhiên). Vẫn 429: «Search Console đang giới hạn số lần lấy số liệu (mã 429). Đợi 15 phút rồi bấm lại.» Giữ phần đã lấy |
| URL Inspection 2.000 lệnh/ngày, 600/phút mỗi thuộc tính | Chỉ khi câu hỏi 6 = B: một lệnh mỗi lần bấm, cho một bài |

### 2.6 Độ trễ số liệu, múi giờ

- Ngày của Search Console là ngày theo **giờ Thái Bình Dương (PT, California)**: UTC−8 mùa đông, UTC−7 mùa hè. Việt Nam UTC+7, nên một «ngày Google» bắt đầu lúc 14:00 hoặc 15:00 giờ Việt Nam. Năm 2026, PT đổi giờ ngày 08/03 và 01/11.
- «Hôm nay PT» = `datetime.now(ZoneInfo("America/Los_Angeles")).date()`. Chỉ dùng **ngày**, không giờ phút, cho mọi số liệu. Đồng hồ máy lệch vài phút không ảnh hưởng.
- **E** (ngày chốt cuối) = ngày trước `first_incomplete_date`, hoặc ngày lớn nhất có số liệu khi không có `metadata`. Số liệu thường có sau 2–3 ngày.
- Mọi ngày hiện ra kèm chú thích «ngày theo giờ Google (giờ Thái Bình Dương của Mỹ), chậm hơn giờ Việt Nam 14–15 tiếng».
- Ngày đăng bài (`date_gmt` của WordPress, giờ UTC) đổi sang ngày PT trước khi tính «đăng được bao nhiêu ngày».
- Mốc ngày đọc từ ngoài (Google, cache, WordPress) kiểm khoảng năm **trước** khi cộng trừ hay đổi múi giờ, và bắt `OverflowError` (bài học LC-T113-1, LC-T113-2).
- Số tạm (`dataState = all`): mặc định **không** hiện, không tính so sánh (câu hỏi 3).

### 2.7 Lọc đúng thuộc tính chính (không lẫn staging)

1. Thuộc tính phải phủ `WORDPRESS_URL` (1.2): chọn nhầm thuộc tính staging thì bị từ chối, không lấy số.
2. Mọi lệnh lấy số liệu (Q1, Q2) lọc trang theo tiền tố của website **ngay tại Google**: với thuộc tính tên miền, dòng của `www.staging-m…`, `www.…`, `http://…` không về máy.
3. Ở máy: mọi dòng kiểm lại `is_site_link` và tiền tố (2.4). Google lỡ trả dòng ngoài website thì dòng đó bị bỏ.
4. «Kiểm tra» (Q3, không lọc) chỉ đếm phần nằm ngoài website, để phát hiện cấu hình sai (website thật ở `www.` mà `WORDPRESS_URL` không có `www.`). Q3 không lưu dòng nào.
5. Đổi `GSC_SITE_URL` hay `WORDPRESS_URL` → mã băm phạm vi trong cache khác → bỏ cả cache, lấy lại (3.1).

### 2.8 Câu báo lỗi cố định

Không chép lời Google, không chép đường dẫn file khóa, không chép từ khóa. Mã lý do (`error.errors[].reason`) chỉ đọc khi là chữ ASCII trong danh sách cố định (như `_refresh_message` của Sheets), chỉ để chọn câu.

| Khi | Câu |
|---|---|
| Thuộc tính sai dạng, `http://` | «Thuộc tính Search Console chưa khai báo hoặc sai dạng. Chọn lại ở Cài đặt → Google (dạng https://ten-mien/ hoặc sc-domain:ten-mien).» |
| Không phủ website | «Thuộc tính Search Console đã chọn không phải của website trong WORDPRESS_URL (ví dụ thuộc tính staging). Chọn lại ở Cài đặt → Google.» |
| 403 | «Tài khoản dịch vụ chưa có quyền xem thuộc tính này (mã 403). Thêm email của tài khoản dịch vụ vào Search Console (Cài đặt → Người dùng và quyền, quyền «Hạn chế»), và kiểm tra đã bật Google Search Console API trong Google Cloud.» |
| 404 | «Không tìm thấy thuộc tính trong Search Console (mã 404). Kiểm tra lại thuộc tính ở trang Cài đặt.» |
| 400 | «Search Console báo yêu cầu không hợp lệ (mã 400).» |
| 429 | Như 2.5 |
| 5xx | «Máy chủ Search Console đang lỗi (mã …). Thử lại sau ít phút.» |
| Mạng, giờ chờ, SSL, chuyển hướng, quá cỡ, dữ liệu hỏng, xin mã | Như các câu tương ứng của client Sheets, đổi chữ «Google Sheets» thành «Search Console» |

---

## 3. Lưu số liệu (yêu cầu 3)

### 3.1 Cache SQLite

File `data/search_console.sqlite`. `data/` và `*.sqlite` đã bị `.gitignore` chặn. Làm như `plan_cache.py`, `site_index.py` (phiếu T-122):

```sql
CREATE TABLE info (key TEXT PRIMARY KEY, value TEXT NOT NULL);
  -- schema_version; scope_hash = sha256(GSC_SITE_URL + "\n" + WORDPRESS_URL);
  -- fetched_at (giờ Việt Nam, kèm +07:00); covered_start, covered_end (ngày PT đã lấy liền mạch)
CREATE TABLE page_day (
  day TEXT NOT NULL, page TEXT NOT NULL, clicks INTEGER NOT NULL, impressions INTEGER NOT NULL,
  position_sum REAL NOT NULL, final INTEGER NOT NULL, PRIMARY KEY (day, page)
) WITHOUT ROWID;
CREATE TABLE query_range (
  id INTEGER PRIMARY KEY, start TEXT NOT NULL, end TEXT NOT NULL, fetched_at TEXT NOT NULL,
  row_count INTEGER NOT NULL, truncated INTEGER NOT NULL, UNIQUE (start, end)
);
CREATE TABLE page_query (
  range_id INTEGER NOT NULL, page TEXT NOT NULL, query TEXT NOT NULL, clicks INTEGER NOT NULL,
  impressions INTEGER NOT NULL, position_sum REAL NOT NULL
);
CREATE TABLE post_date (post_id INTEGER PRIMARY KEY, published TEXT NOT NULL);  -- ngày đăng (PT)
```

Kiểu dữ liệu, khuôn cho phiếu T-122 (cache) và T-123 (tính toán) làm song song. T-122 định nghĩa hai dataclass; T-123 viết `Protocol` cùng tên trường, nên hai phiếu không sửa chung file:

```python
@dataclass(frozen=True)
class CachedDay:          # một ngày × một trang (khuôn Q1)
    day: date             # ngày theo giờ PT
    page: str             # địa chỉ đã kiểm: https, đúng website, đã bỏ "#…"
    clicks: int           # 0 ≤ clicks ≤ impressions
    impressions: int      # 1 … 10**9
    position_sum: float   # vị trí × lượt hiển thị (≥ impressions)
    final: bool           # False: số tạm (ngày ≥ first_incomplete_date)

@dataclass(frozen=True)
class CachedQuery:        # một trang × một từ khóa trong một khoảng (khuôn Q2)
    start: date
    end: date
    page: str
    query: str            # đã clean_text, ≤ 200 ký tự
    clicks: int
    impressions: int
    position_sum: float
```

- Lưu `position_sum` (không lưu trung bình) để cộng dồn đúng ở mọi khoảng ngày. Lưu địa chỉ đã kiểm, **không** lưu khóa so khớp: cách chuẩn hóa (1.4) đổi được mà không phải đổi cấu trúc cache.
- Ghi: mỗi đoạn ngày thay trọn trong một giao dịch (xóa `page_day` của khoảng đó rồi chèn). `covered_end` chỉ tăng khi đoạn liền sau đã ghi xong.
- Đọc là dữ liệu chưa tin cậy: `trusted_schema = OFF`, giới hạn độ dài và số bước (`_guard`), kiểm `sqlite_master`, `quick_check`; kiểm lại **từng dòng** như 2.4; một dòng sai hay `scope_hash` khác → bỏ cả cache, lấy lại. SQL chỉ dùng tham số `?`.
- `data/` hay file là liên kết (symlink, junction, hard link) → không mở (`data_dir.dir_has_link`, T-117), câu `MSG_DATA_DIR_LINK`.
- Không lưu bí mật, không lưu mã truy cập, không lưu email tài khoản dịch vụ.

### 3.2 Giữ bao lâu, dung lượng

- `page_day`: giữ ≤ 486 ngày (16 tháng, bằng Google). Mỗi lần lấy xóa phần cũ hơn. Giữ lâu hơn thì cache không còn «xóa đi tạo lại được» (Google không trả số cũ hơn 16 tháng), trái quyết định đã chốt «trong máy chỉ có cache».
- `page_query`: giữ ≤ 6 khoảng gần nhất (bỏ khoảng lấy lâu nhất). `post_date`: chỉ bài còn trong SiteIndex.
- Ước tính: website có vài chục tới vài trăm trang có lượt hiển thị mỗi ngày → 486 ngày × ≤ 200 trang/ngày ≈ 97.000 dòng × khoảng 120 byte ≈ 12 MB lúc nhiều nhất, thường vài MB. Từ khóa 28 ngày của site nhỏ vài nghìn dòng (≈ 1 MB mỗi khoảng).
- Trần chống phình: ≤ 300.000 dòng `page_day`, ≤ 50.000 dòng mỗi khoảng từ khóa, file ≤ 64 MB. Quá trần thì không ghi thêm, báo, giữ phần đang có.

### 3.3 Làm mới khi nào

- **Chỉ khi bấm** «🔄 Lấy số liệu mới». Mở trang thì vẽ từ cache, **không** gọi mạng, không có luồng nền.
- Cache trống: «Chưa có số liệu. Bấm «Lấy số liệu mới» (lần đầu lấy 16 tháng, khoảng một phút).»
- Gợi ý (không tự lấy): lần lấy cuối đã quá 24 giờ, hoặc E cách hôm nay PT quá 3 ngày → «Có thể đã có số liệu mới».
- Chặn bấm lại < 10 phút khi E chưa đổi (1.3).
- Hai máy: mỗi máy có cache riêng, cùng lấy từ Search Console, nên số giống nhau. Không cần đồng bộ cache.

### 3.4 Có ghi lên Google Sheets không

| Cách | Hệ quả |
|---|---|
| **A. Không ghi** (khuyến nghị, câu hỏi 4) | Search Console chính là nơi dữ liệu dùng chung (như quyết định «Thứ hạng: Google Search Console API»). Từ khóa của người lạ không đi ra khỏi máy. Client Sheets giữ nguyên (chỉ tab «KeHoach», 5 lệnh cố định đã kiểm) |
| B. Ghi tab riêng «TheoDoi»: mỗi bài mỗi tháng một dòng (Mã bài, mã bài WordPress, tháng, click, hiển thị, CTR, vị trí), **không** ghi từ khóa | Giữ được số quá 16 tháng; xem được trên Sheet. Phải mở thêm lệnh ghi Sheets cho tab mới (đổi danh sách lệnh đã kiểm), thêm một phiếu cỡ M, Lá Chắn đầy đủ |

---

## 4. Giao diện (yêu cầu 4)

Ba phương án vị trí; **chủ dự án chọn** ở câu hỏi 1. Phần lõi (phiếu T-121 → T-124) giống nhau cho cả ba, chỉ phiếu giao diện T-125 phụ thuộc lựa chọn.

### 4.1 Phương án A: trang mới «📈 Theo dõi» trên menu

Menu: Bài viết · Soạn bài · Kế hoạch · **📈 Theo dõi** · Cài đặt · Kết nối WordPress. Bố cục theo trang demo «Thứ hạng» anh đã xem ngày 06/10.

```
Theo dõi trên Google                                              [🔄 Lấy số liệu mới]
Số liệu tới hết 31/10 (ngày theo giờ Google) · lấy lúc 14:05 hôm nay
Khoảng: (7 ngày) (28 ngày) (3 tháng) (Tùy chọn)   So với: [Kỳ trước ▾]   ☐ Chỉ bài trong kế hoạch
┌───────────────┬────────────────┬──────────────┬─────────────────────────────┐
│ Lượt click    │ Lượt hiển thị  │ CTR          │ Vị trí trung bình           │
│ 412  ▲ +22%   │ 9.800  ▲ +15%  │ 4,2% ▲ +0,3  │ 12,4  ▲ lên 1,4 bậc         │
└───────────────┴────────────────┴──────────────┴─────────────────────────────┘
Cần chú ý: 🔻 2 bài tụt hạng · 👻 3 bài chưa có lượt hiển thị · 👀 1 bài nhiều hiển thị, ít click
 Bài / trang                 Mã KH   Click  ±    Hiển thị  ±     CTR   Vị trí  ±      Nhãn
 Sửa cửa kéo bị kẹt ray      B-012     35  +10    1.200   +300  2,9%    8,1  ▲2,0   🔺 Lên hạng
 Cổng sắt bị xệ cánh         B-007      4   -9      800    -50  0,5%   14,2  ▼4,1   🔻 Tụt hạng
 Sửa cửa kéo TP.HCM (trang)  —        120   +8    3.100   +200  3,9%    5,3  ▲0,2
 Lan can cầu thang bị gỉ     B-015      0    —        0     —     —      —          👻 đăng 20 ngày
Chi tiết: [Sửa cửa kéo bị kẹt ray ▾]
  (biểu đồ click mỗi tuần)              (biểu đồ vị trí mỗi tuần, lên cao là tốt)
  Từ khóa (28 ngày)            Click  Hiển thị   CTR   Vị trí   ±
  ▸ sửa cửa kéo bị kẹt  🎯       28       700   4,0%     6,4   ▲1,1   (gộp 2 cách gõ)
    cửa kéo bị kẹt ray            5       300   1,7%     9,0   mới
  Google ẩn từ khóa hiếm, nên cộng các dòng ít hơn tổng của bài.
▸ Trang khác trên website (trang chủ, chuyên mục, địa chỉ cũ…): 12 trang
```

### 4.2 Phương án B: tab «📈 Hiệu quả trên Google» trong trang Kế hoạch

```
Kế hoạch
[🗂️ Kế hoạch]  [📈 Hiệu quả trên Google]
(tab Hiệu quả)  Số liệu tới hết 31/10 · [🔄 Lấy số liệu mới] · Khoảng 28 ngày · so kỳ trước
 Mã    Từ khóa chính            Trạng thái  Click  ±    Hiển thị  ±    Vị trí  ±     Nhãn
 B-012 sửa cửa kéo bị kẹt ray   Đã đăng       35  +10    1.200  +300     8,1  ▲2,0  🔺
 B-007 cổng sắt bị xệ cánh      Đã đăng        4   -9      800   -50    14,2  ▼4,1  🔻
 B-015 lan can cầu thang gỉ     Đã đăng        0    —        0     —       —        👻 20 ngày
 B-020 cổng lùa kẹt ray         Đã hẹn giờ     —    —        —     —       —        chưa lên website
▸ Bài, trang ngoài kế hoạch (29 trang có sẵn)        ▸ Chi tiết một dòng: biểu đồ, từ khóa
```

### 4.3 Phương án C: trên trang Bài viết (cột số liệu + hộp chi tiết)

```
Bài viết
[Đang viết …]
Tiếp theo trong kế hoạch            │ Đã gửi WordPress
                                    │ Sửa cửa kéo bị kẹt ray  Đã đăng #123
                                    │   28 ngày: 35 click · vị trí 8,1 ▲2,0          [📈]
                                    │ Cổng sắt bị xệ cánh     Đã đăng #118
                                    │   4 click · vị trí 14,2 ▼4,1 · 🔻 tụt hạng      [📈]
Trên Google (28 ngày, tới 31/10): 412 click · 9.800 hiển thị · 3 bài cần chú ý  [🔄 Lấy số liệu]
(bấm 📈: hộp nổi có biểu đồ và từ khóa của bài)
```

### 4.4 So sánh, và phần chung cho cả ba

| Tiêu chí | A. Trang «Theo dõi» | B. Tab trong Kế hoạch | C. Trên Bài viết |
|---|---|---|---|
| Menu | 6 mục | giữ 5 mục | giữ 5 mục |
| Chỗ cho khoảng ngày, so kỳ, biểu đồ, từ khóa | rộng | vừa | chật (hộp nổi) |
| Gần chỗ quyết định viết gì tiếp | phải chuyển trang | ngay cạnh kế hoạch | cạnh «Tiếp theo trong kế hoạch» |
| Trang dịch vụ, bài không nằm trong kế hoạch | đủ | phần phụ bên dưới | chỉ bài app đã gửi (thêm link «xem tất cả») |
| Ảnh hưởng trang đang chạy | không | trang Kế hoạch vốn đã dài (nguồn, đề xuất, trạng thái website) | trang mở đầu tiên thêm phần, thêm nút |
| Đã có bản demo | có (trang «Thứ hạng» ngày 06/10) | chưa | chưa |
| Độ lớn phiếu giao diện | L | L (sửa `plan.py` 1.087 dòng, nhiều test) | M–L |

**Mục «Search Console» trong Cài đặt → 🔑 Google** (cả ba phương án đều cần):

```
── Search Console ─────────────────────────────────────────────────────────────
Email tài khoản dịch vụ: seo-app@du-an.iam.gserviceaccount.com   (chép để thêm vào Search Console)
Cách thêm: Search Console → Cài đặt → Người dùng và quyền → Thêm người dùng → dán email → «Hạn chế».
Thuộc tính đang dùng: https://suachuacuasat.com/   ·  quyền: Hạn chế ✔
[🔎 Tìm thuộc tính]  [✅ Kiểm tra]
  Thuộc tính tài khoản dịch vụ thấy được          Quyền      Khớp website
  ( ) sc-domain:suachuacuasat.com                 Hạn chế    ✔ (tự lọc bỏ staging)
  (•) https://suachuacuasat.com/                  Hạn chế    ✔
  ( ) https://www.staging-m.suachuacuasat.com/    Hạn chế    ✘ không phải website, không chọn được
[Lưu thuộc tính đã chọn]
Kiểm tra: có số liệu tới hết 31/10 (giờ Google). 2% lượt hiển thị nằm ngoài https://suachuacuasat.com/: không tính.
```

**Hiển thị an toàn** (mọi phương án):

- Chữ từ Google (từ khóa, đường dẫn trang, tên thuộc tính) và từ WordPress (tiêu đề) chỉ hiện qua `st.dataframe(safe_rows(…))`, `st.text` hay `escape_markdown`. Không `unsafe_allow_html` cho chữ này. Trung hòa công thức khi tải CSV từ bảng (LC-T101-1).
- Link chỉ cho địa chỉ qua `is_site_link`, dựng bằng `markdown_link`; đường dẫn «Trang khác» hiện như chữ, không bấm được.
- Biểu đồ (`st.vega_lite_chart`) chỉ có ngày và số. Tên bài nằm ở tiêu đề biểu đồ, dựng bằng `escape_markdown`, không nằm trong chú thích nổi.
- Nhãn `segmented_control`/`pills` cố định (lưu ý trong `CLAUDE.md`).

---

## 5. Bảo mật từng phần (yêu cầu bảo mật riêng)

| Phần | Rủi ro | Biện pháp trong thiết kế | `security.md` |
|---|---|---|---|
| **Khóa tài khoản dịch vụ** | Lộ file khóa: người có nó đọc được Search Console và Sheet đã chia sẻ | Dùng lại **đúng một** file khóa, kiểm lại mỗi lần (2.1); không khóa thứ hai; mã truy cập chỉ trong bộ nhớ; không in, không ghi log; câu lỗi cố định; khi lộ: xóa khóa trong Google Cloud, tạo khóa mới, sửa `.env` hai máy (mục 7.1 đã có). Phạm vi mới **chỉ đọc**, quyền trên thuộc tính «Hạn chế», nên lộ khóa không sửa được gì trên Search Console | 2.1, 2.7, 7 |
| | Quyền cấp quá mức | Trang Cài đặt đọc `permissionLevel` (`sites`), quyền cao hơn «Hạn chế» thì Cảnh báo | 2.7 |
| **Đường gọi mới tới Google** | Gọi API khác, đổi đường, lệnh ghi | Danh sách lệnh cố định kiểm trước khi gửi; chỉ `www.googleapis.com` (đúng 2 đường), máy chủ mã của Google; không có `PUT`/`DELETE`; thân đúng 1 trong 3 khuôn; bộ lọc dựng từ `WORDPRESS_URL`; không theo chuyển hướng; giờ chờ; giới hạn cỡ (2.3) | 2.7 |
| | Tốn hạn mức, treo app | ≤ 20 lệnh mỗi lần bấm, lần lượt, trần lật trang, thử lại 429 một lần, chặn bấm lại (2.5) | 2.7 |
| **Số liệu, địa chỉ từ Google** (chưa tin cậy) | Số lạ làm hỏng phép tính, `NaN` lan ra giao diện | Kiểm từng dòng (2.4): số nguyên thật, không `bool`, không `NaN`, khoảng hợp lệ; JSON không trùng khóa | F3 |
| | Dòng của staging hay website khác lẫn vào | Phủ website + lọc ở Google + kiểm lại ở máy (2.7) | — |
| **Từ khóa (chữ người lạ gõ)** khi hiện lên giao diện | Thẻ HTML, Markdown, link, ký tự đảo hướng chữ hay ký tự vô hình làm chữ hiện sai | `clean_text` (bỏ ký tự điều khiển, vô hình, đảo hướng; NFC), cắt 200 ký tự; hiện bằng bảng/chữ thuần (4.4); không bao giờ thành link | U1 |
| | Thông tin cá nhân của người tìm (số điện thoại, tên) | Google đã ẩn từ khóa có thông tin cá nhân và từ khóa hiếm (mục Nguồn). Số liệu chỉ nằm trong máy; không ghi log | A3 |
| **Từ khóa khi ghi Sheet** | Chèn công thức, lộ chữ người lạ ra Sheet dùng chung | Mặc định **không ghi** (3.4). Câu hỏi 4 = B: chỉ ghi số tổng, không ghi từ khóa, `RAW` + `to_cell` | 2.3 |
| **Từ khóa khi đưa vào lời dặn AI** | Lệnh giấu trong từ khóa điều khiển AI (prompt injection) | Giai đoạn 6 **không** gửi từ khóa cho AI. Câu hỏi 7 = B: từ khóa thành đề xuất kế hoạch qua **bộ đề xuất bảng** (code, không AI), qua `PlanRow`, người dùng tick mới ghi; bỏ từ khóa có số điện thoại/email (`personal_info`). Khi bài được viết, từ khóa vào lời dặn trong khung dữ liệu như mọi từ khóa (T-098, SL-7). Từ khóa hiếm bị Google ẩn, nên muốn «cài» một từ khóa phải có vài chục người gõ nó trong 2–3 tháng | 2.4, A1, A2 |
| **Không lộ số liệu ra ngoài máy** | Số liệu, từ khóa đi ra ngoài | Cache trong `data/` (git chặn); không gửi AI, không ghi Sheet (mặc định), không log; nút tải CSV của bảng chỉ lưu file trên máy người dùng | 2.9 |
| **Cache trong máy** | File bị sửa tay, `data/` bị thay bằng liên kết | Đọc như dữ liệu ngoài, sai là bỏ cả cache; không mở khi là liên kết (T-117); kiểm năm trước khi đổi múi giờ (3.1) | F1, F3 |
| **Ghi `GSC_SITE_URL` vào `.env`** (câu hỏi 2 = A) | Chèn dòng lạ vào `.env` | Bộ kiểm chặt (2 dạng, chỉ `[a-z0-9.:/-]`, không xuống dòng, `#`, dấu nháy), ghi nguyên tử, so lại sau khi ghi (như `set_google_sheet_id`); báo khi biến môi trường đè `.env` | 2.1 |
| **Proxy, chứng chỉ của máy** | Biến môi trường đổi đường đi | Sổ rủi ro 28/10 đã áp cho `requests`, `google-auth`, nay gồm cả Search Console (cùng thư viện) | 6 |
| **Test** | Test gọi Google thật | `tests/fake_google.py` thêm Search Console; bộ chặn mạng vẫn bật | D3 |

Không đề xuất chấp nhận rủi ro mới nào.

**Điều kiện đề xuất cho các phiếu code** (để Lá Chắn rút gọn T-120 xét, đổi thành mã LC-T120-x nếu đồng ý):

| # | Điều kiện | Phiếu |
|---|---|---|
| Đ1 | `webmasters.readonly` là phạm vi duy nhất cho Search Console; `load_service_account` chỉ nhận 2 phạm vi cố định; test chứng minh phạm vi khác bị từ chối và client Sheets vẫn chỉ có phạm vi Sheets | T-121 |
| Đ2 | Danh sách lệnh cố định, kiểm trước khi gửi ở một chỗ; thân đúng 1 trong 3 khuôn; `{siteUrl}` đúng thuộc tính đã kiểm; bộ lọc so nguyên văn với tiền tố dựng từ `WORDPRESS_URL` | T-121 |
| Đ3 | Chỉ các máy chủ ở 2.3; không theo chuyển hướng; giờ chờ ≤ 30 giây; câu trả lời ≤ 8 MB; `_NoAuth`, `_Bearer`, `_TokenRequest` | T-121 |
| Đ4 | Câu lỗi cố định (2.8); mã lý do chỉ đọc từ danh sách ASCII cố định | T-121 |
| Đ5 | Kiểm từng dòng như 2.4 (kể cả `bool`, `NaN`, JSON trùng khóa, tỉ lệ dòng hỏng) | T-121 |
| Đ6 | Thuộc tính phải phủ website; từ chối `http://` và thuộc tính staging; dòng ngoài tiền tố bị bỏ cả khi Google trả | T-121, T-123 |
| Đ7 | Không có lệnh ghi nào tới Search Console; test kiểm danh sách lệnh không có `PUT`/`DELETE` | T-121 |
| Đ8 | ≤ 20 lệnh mỗi lần bấm, không song song, thử lại 429 tối đa 1 lần, trần `startRow` | T-121, T-124 |
| Đ9 | Cache kiểm như `plan_cache` (3.1); một dòng sai → bỏ cả cache; mã băm phạm vi đổi → bỏ cache; không mở khi `data/` là liên kết | T-122 |
| Đ10 | Mốc ngày giờ từ cache, Google, WordPress kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError` | T-122, T-123, T-124 |
| Đ11 | Chữ từ Google chỉ hiện dạng chữ thuần (4.4); không `unsafe_allow_html`; chú thích nổi của biểu đồ chỉ có số và ngày | T-123 (dữ liệu chữ thuần), T-125 |
| Đ12 | Ghi `GSC_SITE_URL` qua `env_file` với bộ kiểm chặt, ghi nguyên tử, báo khi biến môi trường đè | T-124 |
| Đ13 | Từ khóa không vào lời dặn AI, không ghi Sheet (trừ câu hỏi 7 = B theo đúng cách ở bảng trên) | T-124, T-125, T-127 |
| Đ14 | Trang theo dõi kiểm đăng nhập như mọi trang; không gọi mạng khi mở trang; client tạo mới mỗi lần bấm | T-125 |
| Đ15 | Test không gọi mạng; mọi ca biên ở 2.4 có test; thêm trang vào `PAGES` thì `tests/test_app_pages.py` tự mở | Mọi phiếu |

---

## 6. Chia phiếu (yêu cầu 5)

Số phiếu tạm từ **T-121** (`board.md`: số tiếp theo là T-120); Chỉ Huy đánh lại nếu đã dùng. Độ lớn như T-094: **S** ≈ dưới 150 dòng code; **M** ≈ 150–400 dòng code + test; **L** ≈ 400–900 dòng code + nhiều test, thường 2 lượt Soi Lỗi/Lá Chắn.

### Nhóm 1: logic, chạy bằng dữ liệu giả (không cần Google, không cần website)

| Phiếu | Mục tiêu | Agent | File được sửa | Phụ thuộc | Độ lớn | Lá Chắn |
|---|---|---|---|---|---|---|
| **T-121** Client Search Console | `SEARCH_CONSOLE_SCOPE`, tham số `scope` của `load_service_account` (2.1); `seo_app/google/search_console.py`: `SearchConsoleClient.from_settings` (kiểm thuộc tính và file khóa mỗi lần), `list_sites()`, `query(...)` theo 3 khuôn, `_check_call`, kiểm câu trả lời (2.4), lật trang, thử lại 429, câu lỗi (2.8); bộ đọc thuộc tính, kiểm «phủ website», dựng tiền tố lọc. Nhập lớp vận chuyển từ `sheets.py`, không sửa `sheets.py` | Thợ Máy | mới: `seo_app/google/search_console.py`, `tests/test_google_search_console.py`; sửa: `seo_app/google/service_account.py`, `tests/fake_google.py` (chỉ thêm đường Search Console) | Không | **M–L** | Đầy đủ: Đ1–Đ8. Sửa hàm dùng chung `load_service_account`: chạy mọi test Google (`test_google_*`, `test_t100_google_identity`, `test_t101_settings_google`, `test_la_chan_t097`, `test_soi_loi_t097`) |
| **T-122** Cache số liệu | `seo_app/storage/search_cache.py`: `SearchCacheStore`, bảng và kiểu ở 3.1, ghi theo đoạn, giữ 16 tháng, ≤ 6 khoảng từ khóa, trần (3.2), kiểm khi đọc, mã băm phạm vi, chặn liên kết `data/` | Thợ Máy | mới: `seo_app/storage/search_cache.py`, `tests/test_search_cache.py` | Không | **M** | Đầy đủ: Đ9, Đ10 |
| **T-123** Lõi tính toán | Gói mới `seo_app/tracking/`: `model.py` (`Protocol` của hai kiểu ở 3.1, kết quả `PageStats`, `Comparison`, `Flag`, `TrackedPage`), `periods.py` (ngày PT, kỳ 7/28/91/tùy chọn, kỳ trước, cùng kỳ năm trước, tuần), `match.py` (`page_key`, khớp SiteIndex, dòng kế hoạch, «Trang khác»; 1.4), `stats.py` (cộng dồn, vị trí theo lượt hiển thị, so hai kỳ; 1.5), `flags.py` (nhãn, ngưỡng là hằng có tên; 1.6), `keywords.py` (gộp `fold_key`, từ khóa chính, từ khóa mới; 1.7). Hàm thuần: không mạng, không file | Thợ Máy | mới: các file trên (cùng `seo_app/tracking/__init__.py`), `tests/test_tracking_*.py` | Không (dùng `PublishedItem`, `PlanRow` có sẵn) | **M–L** | Rút gọn: Đ6, Đ10, Đ11 |
| **T-124** Lấy số liệu, lưu thuộc tính | `seo_app/tracking/refresh.py`: khoảng cần lấy, chia đoạn ≤ 31 ngày, đánh dấu tạm/chốt, từ khóa 2 kỳ, làm mới SiteIndex khi cũ, ngày đăng qua `post_statuses`, ghi từng đoạn, dừng ở lỗi đầu, chặn bấm lại; `check_connection` cho «Kiểm tra» (1.2). `env_file`: `validate_gsc_site_url`, `set_gsc_site_url`, `clear_gsc_site_url` (câu hỏi 2 = A) | Thợ Máy | mới: `seo_app/tracking/refresh.py`, test; sửa: `seo_app/env_file.py` | T-121, T-122, T-123; câu hỏi 2, 3 | **M** | Đầy đủ: Đ8, Đ10, Đ12, Đ13. Sửa `env_file.py` dùng chung: chạy mọi test `.env` (`test_env_file*`, test T-104, T-105, `test_t101_settings_google`) |

### Nhóm 2: giao diện, tài liệu

| Phiếu | Mục tiêu | Agent | File được sửa | Phụ thuộc | Độ lớn | Lá Chắn |
|---|---|---|---|---|---|---|
| **T-125** Giao diện theo dõi | Trang/tab theo câu hỏi 1 (mục 4); mục «Search Console» trong Cài đặt → Google (4.4); biểu đồ `st.vega_lite_chart`; hiển thị an toàn (4.4) | Họa Sĩ | A: mới `app/views/tracking.py`, sửa `app/main.py` (`PAGES`); B: `app/views/plan.py`; C: `app/views/home.py`. Cả ba: `app/views/settings.py`, test AppTest | T-124; câu hỏi 1, 3, 5 | **L** | Đầy đủ: Đ11, Đ14 |
| **T-126** README «Theo dõi trên Google» | Việc chủ dự án làm (1.2: bật API, thêm người dùng quyền Hạn chế, chọn thuộc tính); cách đọc số (trễ 2–3 ngày, ngày theo giờ Google, tổng theo trang khác biểu đồ Search Console, từ khóa bị ẩn, nhãn); chú thích `GSC_SITE_URL` trong `.env.example` (2 dạng, chọn ở Cài đặt, không dùng thuộc tính staging) | Thư Ký | `README.md`, `.env.example` (chỉ chú thích) | Phần việc chủ dự án làm: viết ngay sau T-121; phần màn hình: sau T-125 | **S** | Rút gọn |

### Phiếu tùy theo câu trả lời

| Phiếu | Khi nào | Mục tiêu | Agent | Độ lớn |
|---|---|---|---|---|
| **T-127** «Đưa vào kế hoạch» | Câu hỏi 7 = B | Tick từ khóa ở bảng từ khóa → thành đề xuất «Thêm» ở trang Kế hoạch qua bộ đề xuất bảng có sẵn (không AI; kiểm trùng, trùng bài đã đăng, trang cửa ngõ như T-098); ≤ 10 từ khóa mỗi lần; bỏ từ khóa có số điện thoại/email | Thợ Máy (hàm trong `seo_app/plan/propose.py`) + Họa Sĩ (nút) | S–M |
| Kiểm lập chỉ mục | Câu hỏi 6 = B | Lệnh `inspect` (2.3), đổi trạng thái của Google thành câu tiếng Việt theo danh sách cố định (giá trị lạ → «trạng thái khác, xem trong Search Console») | Thợ Máy + Họa Sĩ | S–M |
| Ghi tab «TheoDoi» | Câu hỏi 4 = B | Mở thêm lệnh ghi Sheets cho tab mới, ghi số tổng theo tháng (3.4) | Thợ Máy | M |

### Đi kèm

| Việc | Ai | Ghi chú |
|---|---|---|
| **Thử thật** | Chỉ Huy + chủ dự án | (1) Chủ dự án làm 2 việc phía Google (1.2). (2) Cài đặt: «Tìm thuộc tính» thấy đúng thuộc tính, quyền Hạn chế; «Kiểm tra» báo ngày có số liệu, phần ngoài website (staging) không tính. (3) Lấy số liệu; so 2 bài với Search Console (Hiệu suất → bảng «Trang», 28 ngày): click, hiển thị phải khớp, vị trí lệch ≤ 0,1. (4) Xác nhận tên trường `metadata` thật. (5) Bấm lại ngay → bị chặn. (6) Search Console → Người dùng và quyền: không có gì thay đổi. Kết quả ghi báo cáo; không ghi file khóa, email đầy đủ vào báo cáo |
| Lá Chắn rà cả Giai đoạn 6 | Lá Chắn | Sau T-125, trước khi đóng giai đoạn |

### Thứ tự và song song

```
Đợt 1 (song song, 3 phiên):  T-121 client · T-122 cache · T-123 lõi tính toán   (không chờ câu trả lời nào)
Đợt 2:                       T-124 lấy số liệu, lưu thuộc tính   (sau đợt 1; câu hỏi 2, 3)
                             T-126 phần «việc chủ dự án làm» viết song song được
Đợt 3:                       T-125 giao diện   (câu hỏi 1, 3, 5) · T-126 hoàn tất
Đợt 4:                       Thử thật · T-127 (nếu câu 7 = B) · Lá Chắn rà Giai đoạn 6
```

File không chồng nhau giữa các phiếu cùng đợt: T-121 ở `seo_app/google/` và `tests/fake_google.py`, T-122 ở `seo_app/storage/`, T-123 tạo gói `seo_app/tracking/` (T-124 chỉ thêm `refresh.py` vào gói đó ở đợt sau). Hai chỗ đụng code dùng chung: `service_account.py` (T-121) và `env_file.py` (T-124); đã ghi lệnh chạy test mọi nơi gọi ở cột Lá Chắn.

---

## 7. Ngoài phạm vi Giai đoạn 6 (ghi lại để không quên)

- **Google Analytics 4** (cuộc gọi, Zalo, gửi form: chỉ số chuyển đổi thật mà `review_ke_hoach_v1.md` mục 4.3 nhấn mạnh): API khác, có thể cần thư viện khác, hỏi riêng khi cần.
- Lượng tìm kiếm của từ khóa (Keyword Planner), Ahrefs, citation, backlink.
- Loại tìm kiếm khác (Hình ảnh, Video, Tin tức, Discover), số liệu theo giờ, theo thiết bị, theo quốc gia: thêm sau được trên cùng client (thêm khuôn thân).
- Sơ đồ trang (sitemap), yêu cầu lập chỉ mục: cần quyền ghi, không làm.
- Sửa bài cũ theo số liệu («Cập nhật bài cũ»): vẫn ngoài phạm vi (T-094 câu 6).
- Cảnh báo tự động khi tụt hạng (email, thông báo): cần chạy nền, trái quyết định «app không cần chạy nền».
- Giữ số liệu quá 16 tháng: chỉ khi câu hỏi 4 = B.
- **Ghi nhận cho Chỉ Huy** (không thuộc T-120): trang tài liệu `searchanalytics.query` của Google ghi rằng kết quả nhiều định dạng FAQ không còn xuất hiện trên Google Search từ 07/05/2026, và loại «FAQ» sẽ bị bỏ khỏi API vào 08/2026. Schema FAQPage của app (T-038) vì vậy không còn đem lại kết quả FAQ trên Google; nên báo chủ dự án để quyết có giữ bước này không.

---

## 8. Câu hỏi cho chủ dự án (yêu cầu 6)

Mỗi câu trả lời bằng một chữ cái. Câu chưa có trả lời thì phiếu đợt 1 vẫn làm được; phần cần câu trả lời theo lựa chọn khuyến nghị (an toàn nhất) cho tới khi anh chọn khác.

**Câu 1. Đặt phần theo dõi Google ở đâu trong menu?** (phác thảo ở mục 4)
- **A (khuyến nghị).** Trang mới **«📈 Theo dõi»** trên menu, giữa «Kế hoạch» và «Cài đặt». Hệ quả: menu có 6 mục; đủ chỗ cho chọn khoảng ngày, so kỳ, biểu đồ, từ khóa; bố cục giống trang demo «Thứ hạng» anh đã xem ngày 06/10; các trang đang có không đổi.
- **B.** Thêm tab **«📈 Hiệu quả trên Google»** trong trang Kế hoạch. Hệ quả: số liệu nằm ngay cạnh kế hoạch, theo Mã bài; trang Kế hoạch dài thêm; trang dịch vụ, bài ngoài kế hoạch nằm ở phần phụ.
- **C.** Thêm số liệu vào trang **Bài viết** (mỗi bài đã gửi một dòng số, bấm 📈 mở hộp chi tiết). Hệ quả: không thêm mục menu; chỗ hẹp, khó so kỳ và xem từ khóa; trang dịch vụ phải qua link «xem tất cả».

**Câu 2. Chọn thuộc tính Search Console thế nào?**
- **A (khuyến nghị).** Ở Cài đặt → Google, phần mềm tìm các thuộc tính tài khoản dịch vụ thấy được, anh bấm chọn, phần mềm ghi vào `.env` (như cách dán link Google Sheet). Hệ quả: không phải mở `.env`; phần mềm chỉ cho chọn thuộc tính đúng website, không cho chọn staging. Nếu có cả thuộc tính tiền tố `https://suachuacuasat.com/` thì nên chọn nó.
- **B.** Anh tự mở `.env`, gõ `GSC_SITE_URL`. Hệ quả: phần mềm không ghi thêm biến nào vào `.env`; gõ sai thì báo lỗi khi bấm lấy số liệu.

**Câu 3. Có hiện số liệu tạm của 1–2 ngày gần nhất không?**
Google chốt số liệu sau 2–3 ngày; số của 1–2 ngày gần nhất còn thay đổi.
- **A (khuyến nghị).** Không, chỉ hiện số đã chốt, ghi rõ «số liệu tới hết ngày …». Hệ quả: số không tự đổi sau đó, so sánh luôn đủ ngày.
- **B.** Có, hiện thêm số tạm, đánh dấu «tạm», không tính vào so sánh. Hệ quả: thấy sớm hơn 1–2 ngày; số tạm có thể đổi khi Google chốt.

**Câu 4. Có ghi số liệu theo dõi lên Google Sheets không?**
- **A (khuyến nghị).** Không. Số liệu nằm trên Search Console, mỗi máy tự lấy; trong máy chỉ có bản lưu tạm. Hệ quả: không mở thêm quyền ghi Sheet; từ khóa người khác gõ không ra khỏi máy; xem số cũ tối đa 16 tháng.
- **B.** Có, thêm tab **«TheoDoi»**: mỗi bài mỗi tháng một dòng số tổng (không ghi từ khóa). Hệ quả: giữ được số lâu hơn 16 tháng, xem được trên Sheet; thêm một phiếu, mở thêm lệnh ghi Sheets.

**Câu 5. Ngưỡng đánh dấu bài (mục 1.6)?**
Mặc định: **tụt hạng** khi kém đi ≥ 3 bậc hoặc rơi khỏi trang 1 (cả hai kỳ ≥ 30 lượt hiển thị); **mất click** khi còn ≤ một nửa (kỳ trước ≥ 10 click); **chưa có lượt hiển thị** khi bài đã đăng ≥ 14 ngày; **nhiều hiển thị, ít click** khi ≥ 200 lượt hiển thị, vị trí ≤ 10, CTR < 1%.
- **A (khuyến nghị).** Dùng mặc định, sau một hai tháng xem lại. Hệ quả: đổi số sau chỉ là sửa hằng số, không đổi cách làm.
- **B.** Anh đặt số khác (ghi luôn số muốn dùng).

**Câu 6. Có kiểm «Google đã đưa bài vào kết quả tìm kiếm chưa» (lập chỉ mục) ngay trong phần mềm không?**
- **A (khuyến nghị).** Để sau. Bài «chưa có lượt hiển thị» kèm hướng dẫn kiểm bằng tay trong Search Console (ô «Kiểm tra URL»). Hệ quả: Giai đoạn 6 gọn hơn; làm thêm sau được (phiếu nhỏ).
- **B.** Làm luôn: nút «Kiểm tra trên Google» cạnh bài chưa có lượt hiển thị. Hệ quả: thêm một phiếu nhỏ và một lệnh gọi Google; nếu quyền «Hạn chế» không đủ cho lệnh này (chưa rõ, kiểm khi thử thật) thì phải nâng quyền, hoặc bỏ tính năng.

**Câu 7. Có cho đưa từ khóa thật từ Google sang Kế hoạch không?**
Bảng từ khóa của bài hay có những từ người ta gõ mà website chưa có bài riêng: gợi ý tốt cho bài mới («có dữ liệu rồi mới chọn bài», `review_ke_hoach_v1.md`).
- **A.** Chỉ xem; muốn dùng thì anh tự chép sang kế hoạch. Hệ quả: Giai đoạn 6 không đụng trang Kế hoạch.
- **B (khuyến nghị).** Thêm nút «Đưa vào kế hoạch»: tick vài từ khóa (tối đa 10 mỗi lần) → thành đề xuất «Thêm bài» ở trang Kế hoạch, anh duyệt như mọi đề xuất (không qua AI, vẫn cảnh báo trùng bài đã có, trang cửa ngõ). Hệ quả: thêm một phiếu nhỏ cuối giai đoạn; từ khóa có số điện thoại hay email bị bỏ.

**Việc chủ dự án làm phía Google** (không phải câu hỏi; README hướng dẫn): bật Google Search Console API trong project Google Cloud đang dùng cho Sheets; thêm email tài khoản dịch vụ vào Search Console, quyền «Hạn chế» (mục 1.2). Hai việc này nên làm sớm để kịp lượt thử thật.

---

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: luồng người dùng: kết nối thuộc tính (tên miền / tiền tố, thêm tài khoản dịch vụ, quyền Hạn chế), lấy số liệu theo bài, khớp địa chỉ với bài WordPress và dòng kế hoạch, khoảng ngày, so hai kỳ, nhãn tụt hạng / chưa có lượt hiển thị (mục 1)
- [x] Yêu cầu 2: phạm vi `webmasters.readonly`, thư viện (không cần mới), đường gọi cố định, giới hạn dòng và hạn mức, độ trễ 2–3 ngày, giờ PT, lọc đúng thuộc tính chính không lẫn staging (mục 2)
- [x] Yêu cầu 3: cache SQLite, không ghi Sheets mặc định, giữ 16 tháng, làm mới bằng nút, dung lượng (mục 3)
- [x] Yêu cầu 4: 3 phương án vị trí có phác thảo chữ, không tự chọn (mục 4, câu hỏi 1)
- [x] Yêu cầu 5: 6 phiếu chính + 3 phiếu tùy câu trả lời, thứ tự, song song, độ lớn (mục 6)
- [x] Yêu cầu 6: 7 câu hỏi có A/B (câu 1 có C) và khuyến nghị, câu đầu là vị trí trong menu (mục 8)
- [x] Yêu cầu bảo mật riêng: rủi ro từng phần, 15 điều kiện đề xuất (mục 5)
- [x] Báo cáo tại `docs/team/reports/T-120-tho-may.md`, có «Tóm tắt (cho chủ dự án)»
- [x] Không sửa code, cấu hình, test; không gọi Google thật hay website thật; không đọc `.env`; không chạy pytest (phiếu không đổi code, máy đang chạy toàn bộ test)

## Rủi ro và điểm cần chú ý (chưa xác minh)

- **Tài khoản dịch vụ làm người dùng Search Console**: cách làm phổ biến, nhưng trang trợ giúp quyền của Google không nói riêng về tài khoản dịch vụ. Kiểm ở lượt thử thật trước khi giao T-125.
- **Quyền «Hạn chế»** đủ cho số liệu Hiệu suất (trang trợ giúp ghi vậy). Với URL Inspection, bảng quyền chỉ ghi «Fetch only» cho người dùng Hạn chế: chưa rõ lệnh API có chạy không (chỉ liên quan câu 6 = B).
- **Tên trường `metadata`**: tài liệu viết `first_incomplete_date`. Nếu tên thật khác, app coi 3 ngày cuối là tạm (an toàn, chỉ chậm thêm 1 ngày); sửa sau thử thật.
- **Vị trí trung bình theo lượt hiển thị**: suy luận từ định nghĩa, so khớp với bảng «Trang» của Search Console ở lượt thử thật.
- **Tổng toàn website** của app cộng theo trang, có thể cao hơn biểu đồ Search Console (tính theo website): giao diện và README giải thích.
- **Từ khóa bị ẩn**: cộng các dòng từ khóa luôn ít hơn tổng của bài; với website nhỏ, phần bị ẩn có thể lớn.
- **Chưa biết chủ dự án có loại thuộc tính nào** (tên miền, tiền tố); đã biết có thuộc tính staging. Thiết kế chạy với cả hai loại.
- **`WORDPRESS_URL` khác địa chỉ chuẩn Google đang dùng** (ví dụ có/không `www.`): bộ lọc sẽ ra số 0; «Kiểm tra» phát hiện và báo (1.2).
- **Lần lấy đầu** khoảng 18 lệnh: bấm liên tục nhiều lần có thể chạm hạn mức tải ngắn hạn; app giữ phần đã lấy, báo đợi 15 phút.
- **Đổi slug bài**: số liệu cũ nằm ở địa chỉ cũ («Trang khác»), bài mới đổi slug như mới đăng một thời gian.
- **Đồng hồ máy sai ngày**: «hôm nay PT» sai, nhưng app chỉ hỏi khoảng ngày hợp lệ (≤ hôm nay, ≥ 16 tháng trước). Sai lệch chỉ làm thiếu hay thừa một ngày ở biên, không hỏng dữ liệu.
- Lớp vận chuyển dùng chung bằng cách nhập tên `_…` từ `sheets.py`. Đây là ràng buộc ngầm: sau này sửa `sheets.py` phải chạy cả test Search Console. Ghi vào docstring hai module ở T-121.

## Đề xuất

- **Chỉ Huy**: đánh số phiếu; gửi chủ dự án 7 câu hỏi, câu 1 trước; giao đợt 1 (T-121, T-122, T-123) ngay, không cần chờ câu trả lời; nhắc chủ dự án làm hai việc phía Google sớm. Cân nhắc báo chủ dự án ghi nhận FAQ (mục 7).
- **Lá Chắn** (rút gọn T-120): xét 15 điều kiện ở mục 5; khi kiểm lại bằng Fable nhóm 4 về sau, thêm Search Console vào phạm vi.
- **Thư Ký** (T-126): thêm vào chú thích `GSC_SITE_URL` trong `.env.example`: hai dạng hợp lệ, nên chọn ở Cài đặt, không dùng thuộc tính staging.
- **Soi Lỗi** (ca biên gợi ý cho T-121 → T-124): ngày đổi giờ của PT (08/03, 01/11); trả đúng 25.000 dòng để lật trang; `metadata` thiếu hay sai tên; dòng staging khi thuộc tính tên miền; `%E1%BB%AD` hoa, thường; hai dòng chỉ khác `#…`; `bool` thay cho số; `position` bằng 0; click lớn hơn hiển thị; `responseAggregationType` lạ; JSON trùng khóa; `NaN`; từ khóa toàn ký tự vô hình; bài đổi slug; dòng kế hoạch có slug trùng hai bài.

# Báo cáo T-128 · Sổ rủi ro 3 giới hạn `modified_gmt` và kịch bản buổi thử thật Hẹn giờ / Đăng ngay

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-128](../tickets/T-128-so-rui-ro-va-kich-ban-thu-that.md) (Chỉ Huy B giao 04/11; làm 04/11, nghỉ vì hết hạn mức, làm tiếp 05/11) |
| Nhánh | `team/T-128` (từ `main` cục bộ `2a7b408`) |
| Ngày nộp | 2026-11-05 10:19 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành yêu cầu 1–3. Sửa `docs/team/security.md` mục 6; thêm `docs/team/reports/T-128-kich-ban-thu-that.md` và báo cáo này. Không sửa code, README |
| Lượt 2 | 2026-11-05 12:33 (+07:00): sửa kịch bản theo biên bản Lá Chắn T-128 (`952aaca`): LC-T128-1, -2, -3 và ghi nhận N1–N5. Xem mục «Lượt 2» cuối báo cáo |

## Tóm tắt (cho chủ dự án)

- **Sổ rủi ro** có thêm 3 dòng anh/chị đồng ý ngày 04/11. Đó là ba khe rất hẹp của cách phần mềm kiểm «bài nháp có bị ai sửa không» ngay trước khi hẹn giờ hay đăng:
  1. ai đó sửa bài đúng trong cùng một giây;
  2. sửa đúng lúc giữa hai lệnh của phần mềm;
  3. chỉ đổi ảnh đại diện bằng trình soạn cổ điển.

  Cả ba cần người có tài khoản sửa bài đang sửa đúng bài nháp vừa tạo, trong vài giây.
- **Kịch bản buổi thử thật** đã soạn sẵn từng bước, anh/chị báo rảnh là làm được. File `docs/team/reports/T-128-kich-ban-thu-that.md`, gồm:
  - chuẩn bị: việc anh/chị quyết phía website, bài thử, Sheet bản sao;
  - 6 ca thử (0 tới 5), thêm ca Sheet;
  - cách dọn sau buổi thử;
  - bảng ghi kết quả cho Lá Chắn.
- Buổi thử có **hai bài thử hiện công khai vài phút** (một bài hẹn giờ 15 phút, một bài Đăng ngay) rồi gỡ ngay. Anh/chị đọc nội dung trước khi bấm. Khoảng 1 giờ 30.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/security.md` mục 6, `:178-180` (3 dòng mới, ngày 2026-11-04) | Giới hạn 1 «cùng giây»; giới hạn 2 «khe giữa lệnh đọc kiểm và lệnh ghi của app»; giới hạn 3 «sửa chỉ phần meta». Mỗi dòng có rủi ro (dẫn `release_draft` `client.py:1545-1550`), lý do chấp nhận (WordPress không có khóa lạc quan `If-Match`; cần người đang sửa đúng bài nháp vừa tạo trong vài giây của một cú bấm; nội dung đã xác nhận bằng mã băm T-102), người quyết định «Chủ dự án (04/11)». Dòng 3 thêm: trình soạn khối luôn đổi giờ sửa nên khe hẹp; cách thu hẹp không bắt buộc (xin thêm `featured_media`, Lá Chắn T-115) |
| `docs/team/reports/T-128-kich-ban-thu-that.md` (mới, 266 dòng) | Kịch bản cho Chỉ Huy, chủ dự án ngồi cùng. Mục 0 tóm tắt; 1 quy tắc (không bí mật, chủ dự án tự đăng nhập và tự xóa hẳn, một tab, không mở trình soạn khi app đang gửi, điểm dừng); 2 bảng việc → ca; 3 chuẩn bị (việc phía website chủ dự án quyết, máy, bài thử, Sheet bản sao, ca 0); 4 các ca 1–5, xem bài hiển thị thật, ca S, (f) suốt buổi; 5 khi có sự cố; 6 dọn (10 dòng); 7 bảng kết quả cho Lá Chắn; 8 sau buổi thử |

## Đối chiếu

### Yêu cầu 1: ba giới hạn (`docs/team/reports/T-115-la-chan.md`, mục 4 «Tự tái hiện cả ba», điều kiện 3)

| Giới hạn (biên bản) | Dòng sổ |
|---|---|
| 1. Cùng giây: `modified_gmt` tính tới giây; sửa cùng giây với lệnh ghi cuối của app thì giờ không đổi | `:178` |
| 2. Khe giữa lệnh đọc kiểm và lệnh ghi (vài trăm mili giây): lệnh ghi của app đặt giờ sửa mới, client nhớ giờ đó nên lần sửa kia bị «rửa» | `:179` |
| 3. Sửa chỉ meta (ảnh đại diện qua trình soạn cổ điển, plugin ghi khóa meta riêng): giờ sửa không đổi | `:180` |
| Lý do chấp nhận: không khóa lạc quan; cần người đang sửa đúng nháp vừa tạo, vài giây; nội dung xác nhận bằng mã băm (T-102); trình soạn khối luôn đổi giờ sửa | cả 3 dòng; ý trình soạn khối ở `:180` |
| Mức Thấp; Lá Chắn T-112 (Fable) đồng ý (`T-112-la-chan.md` mục 2) | ghi trong cột rủi ro |
| Chủ dự án đồng ý 04/11 (phiếu T-128, tin Chỉ Huy B) | cột người quyết định «Chủ dự án (04/11)» |

Số dòng code `client.py:1545-1550` kiểm trên nhánh (`known = self._modified.get(post_id)` … `raise ReleaseError(_RELEASE_CHANGED, **fail)`).

### Yêu cầu 2: đủ mục (a)–(g) (`T-112-la-chan.md` «Điều kiện» B4; bảng lượt 3 mục 5 và lượt 3 Fable mục 4)

| Mục | Ca trong kịch bản |
|---|---|
| (a) `publish_posts` | Ca 0 bước 1 («Đăng bài: ✅») |
| (b) Abilities có đổi `modified_gmt` không | Ca 2 (đối chứng: không ghi SEO) + ca 3 (ghi SEO); kết quả CÓ ĐỔI thì bỏ ca 5, cần phiếu client |
| (c) múi giờ, giờ hẹn trong trang quản trị | Ca 0 bước 2; ca 2 bước 2, 5 |
| (d) trình soạn khối hay cổ điển | Ca 0 bước 3 |
| (e) WP-Cron đăng đúng giờ | Ca 4 (hẹn 15 phút, xem tự đăng; lỡ lịch thì mở trang chủ, đợi thêm) |
| (f) câu báo không lộ gì lạ | Quy tắc 8 (điểm dừng), mục «Suốt buổi · (f)» |
| (g) `srcset`/GPS (T-059 ghi nhận 2); «< 5 triệu» (T-091 điều kiện 4) | Ca 1 bước 1, 4, 5 |

Các ý khác của LC-T094-44 (`T-094-la-chan.md:138`), và các việc Fable T-116 nhóm 2 gom vào buổi thử:

| Ý | Ca trong kịch bản |
|---|---|
| Thử trên Sheet bản sao | Mục 3.4, ca S |
| Không ghi bí mật vào báo cáo | Quy tắc 1, dọn bước 10 |
| Hẹn giờ, đăng chỉ bài chủ dự án duyệt | Quy tắc 2, mục 3.1 |
| Header `Date` | Ca 0 bước 4, ca 2 bước 4 |
| Biên tập viên hẹn giờ được qua REST | Ca 2 |
| Xem bài hiển thị thật | Mục 4.1 |
| T-110 điều kiện 3 (Media ẩn danh, gắn ảnh không 403) | Ca 1 bước 3, 6 |
| T-097 điều kiện 5 (tùy chọn) | Mục 3.4 |
| Nguồn T-112 B4 «cuối cùng chuyển về nháp/xóa» | Ca 2, ca 3 bước chuyển về nháp; mục 6 |

**Câu chữ trong kịch bản.** 73 câu báo, tên nút, nhãn ô trích trong kịch bản đều có trong `app/`, `seo_app/` trên nhánh. Kiểm bằng script Python đọc UTF-8, có nối chuỗi viết tách dòng: «tổng: 73 thiếu: 0».

**Luật dòng kế hoạch.** Ca S ghi đúng luật đọc từ code:
- `seo_app/plan/sync.py` `write_status`: trạng thái chỉ đi tới, câu `STATUS_LATER`.
- `seo_app/plan/website.py`: chỉ đi tới. Bài về nháp thì cảnh báo `NOTICE_BACK_TO_DRAFT`, không ghi; `NOTICE_LATE` «Lỡ lịch»; `NOTICE_MISSING` sau khi xóa.

Bản nháp đầu của tôi viết «Cập nhật trạng thái từ website ghi lại về nháp»; đọc code thấy sai nên đã sửa trước khi nộp.

## Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ PYTHONUTF8=1 uvx detect-secrets scan docs/team/security.md docs/team/reports/T-128-kich-ban-thu-that.md docs/team/reports/T-128-thu-ky.md
  "results": {}
$ (script đối chiếu câu trích)  tổng: 73 thiếu: 0
```

Kịch bản không chứa mật khẩu ứng dụng, mật khẩu, tên hay nội dung file khóa, mã hay link Sheet, email tài khoản dịch vụ, tên tài khoản WordPress. Địa chỉ website viết `<tên-miền>`. Không chạy pytest, ruff (chỉ đổi tài liệu).

## Rủi ro và điểm cần chú ý

- **Nhãn trang quản trị WordPress, Google Sheets** (bộ lọc «đã lên lịch», «Sửa nhanh», «Tệp → Tạo bản sao»…) viết theo nghĩa, kèm tên tiếng Anh. Tôi chưa đối chiếu trên trang thật.
- **Google có thể chưa nối.** Theo `TIEN-DO.md`, tạo tài khoản dịch vụ là việc của chủ dự án «khi tới bước thử thật». Chưa nối thì mục 3.4 và ca S ghi «chưa làm»; Lá Chắn xét có cần làm trước khi dùng không.
- **(b) suy ra từ đối chứng**, không đọc thẳng `modified_gmt`, để không phải dùng mật khẩu ứng dụng ngoài app. Ca 2 không ghi SEO mà hẹn giờ được, còn ca 3 ghi SEO thì bị chặn ⇒ Abilities đổi giờ sửa. Điều kiện: không ai mở bài trong trình soạn lúc đang gửi (quy tắc 5).
- **Ca 4, ca 5 đăng bài công khai** trên website thật (không có website thử). Kịch bản giảm rủi ro bằng: chủ dự án duyệt nội dung, quyết trước về plugin tự báo bài mới, gỡ ngay, xóa cache, kiểm địa chỉ ra «không tìm thấy». Chủ dự án vẫn nên biết là vài phút đó khách có thể thấy bài.
- **Bước kiểm tên máy chủ Google** (T-097 đk 5) bằng `Get-DnsClientCache` chỉ để tham khảo: bộ nhớ tên miền của Windows có cả tên do trình duyệt tra.

## Câu hỏi cho chủ dự án

Không có câu mới. Các việc phía website (sao lưu, plugin tự báo bài mới, duyệt bài thử) đã ghi ở mục 3.1 của kịch bản để anh/chị quyết khi bắt đầu buổi thử.

## Lượt 2 (2026-11-05, sau biên bản Lá Chắn T-128)

Lá Chắn (`952aaca`, `T-128-la-chan.md`) kết luận ĐẠT CÓ ĐIỀU KIỆN:
- 3 lỗi Thấp phải sửa trước buổi thử: LC-T128-1, -2, -3;
- ghi nhận N1–N5 nên sửa cùng đợt (điều kiện 2).

Lượt này sửa đủ cả 8 ý, chỉ trong `docs/team/reports/T-128-kich-ban-thu-that.md` (nay 308 dòng). Không sửa `security.md`, code, README.

### Tóm tắt (cho chủ dự án)

- **Kết luận chặt hơn.** Câu hỏi chính của buổi thử là «ghi SEO có làm đổi giờ sửa bài không». Giờ chỉ kết luận «không đổi» khi **ít nhất 3 lần** gửi có ghi SEO đều qua, vì một lần qua có thể chỉ là may.
- **Tên tác giả.** Khi bài thử hiện công khai, anh/chị xem tên tác giả có lộ tên đăng nhập của tài khoản phần mềm không. Trước khi dùng thật, nên:
  - đặt tên hiển thị khác, ví dụ «Pro-Metal»;
  - đặt mật khẩu đăng nhập của tài khoản này thật mạnh.
- **Dọn kỹ hơn.**
  - Xóa **ảnh thử trước**, rồi mới xóa hẳn bài.
  - Thêm bước xóa pingback (WordPress tự báo cho bài được link tới).
  - Mục 3.1 có thêm một việc anh/chị quyết trước buổi: tắt tạm pingback, hay chấp nhận rồi xóa khi dọn.
- **Lúc chờ bài hẹn giờ 15 phút tự đăng, không ai mở website hay trang quản trị.** Nhờ vậy biết được lịch chạy của website có tự chạy không. Buổi thử dài khoảng 1 giờ 30 tới 2 giờ.

### Đã thay đổi (kịch bản, số dòng sau khi sửa)

| Ý của Lá Chắn | Chỗ sửa |
|---|---|
| **LC-T128-1** kết luận (b) | Mục 4 thêm «Luật đọc (b)» `:160-167`: CÓ ĐỔI khi một lần gửi bật «Ghi SEO» có cả «Đã ghi SEO vào hộp SiteSEO của bài nháp.» lẫn «Bài nháp trên website đã bị sửa…» (ca 2 đã qua, không ai mở bài); KHÔNG ĐỔI chỉ khi ≥ 3 lần gửi bật «Ghi SEO» đều qua (ca 3, 4, 5; thiếu thì lặp ca 3, mỗi lần chuyển về nháp); không có «Đã ghi SEO…» thì chưa kết luận, không tính. Ca 3 `:169-180` (lần thứ nhất: qua thì «chưa kết luận»). Ca 4 bước 1–2 `:186-190` (bật «Ghi SEO» khi chưa có CÓ ĐỔI; bị chặn vì (b) thì làm lại với «Ghi SEO» tắt để kiểm (e), bỏ ca 5). Ca 5 `:202-210` (chỉ làm khi chưa có CÓ ĐỔI; lần thứ ba; bị chặn thì bài vẫn là nháp). Mục 2 dòng (b) `:50` («gần như luôn bị chặn»), mục 7 dòng (b) `:277` (ghi từng lần) |
| **LC-T128-2** tác giả công khai | Mục 4.1 ô «Tác giả» `:221-226` (tên tác giả trên bài, trang tác giả `/author/…/`, `/wp-json/wp/v2/users`, cửa sổ ẩn danh; chỉ ghi có/không, không chép tên). Mục 7 dòng «Tác giả công khai» `:287`; mục 2 dòng LC-T128-2 `:57`. Mục 8 `:300-305`: chủ dự án quyết trước khi dùng thật (Biệt danh, Tên hiển thị công khai; mật khẩu đăng nhập dài, ngẫu nhiên; trang tác giả vẫn lộ tên đăng nhập, muốn giấu thì dùng chức năng chặn liệt kê người dùng của plugin bảo mật hay đổi tác giả); Lá Chắn xét |
| **LC-T128-3** (i) thứ tự dọn | Mục 6 bước 3 `:257-258` xóa ảnh thử trước (Media dạng danh sách, cột «Đã tải lên» (Uploaded to) là tên bài thử), bước 4 `:259` mới xóa hẳn bài. Quy tắc 3 `:34`, tóm tắt `:22`. Mục 7 thêm dòng «Ảnh thử» `:288` (tên file ảnh từng ca) |
| **LC-T128-3** (ii) pingback | Mục 3.1 `:69-71`: pingback, tắt tạm ô «Cố gắng thông báo cho các blog được liên kết tới từ bài viết» ở **Cài đặt → Thảo luận** hay chấp nhận. Dịch vụ cập nhật (**Cài đặt → Viết**, Ping-O-Matic) gộp vào ý «Plugin tự báo bài mới» `:66`. Mục 3.3 `:84`: bài thử không link ra website khác. Mục 6 bước 5 `:260` (**Bình luận** → loại **Pings** → xóa pingback có tên bài thử), bước 6 `:261` bật lại; dòng «Dọn» mục 7: 11 bước |
| N1 dấu `[` `]` | Mục 3.3 `:83`: chỉ ra dòng **Cảnh báo** (khung vàng), không chặn |
| N2 múi giờ | Ca 2 bước 2 `:151`: có câu «Không đọc được múi giờ của website…» thì ghi vào (c) |
| N3 bật công tắc | Mục 8 `:308`: chỉ bật để dùng thật khi có **cả hai**: Lá Chắn đồng ý kết quả buổi thử, và Lá Chắn đã rà soát Giai đoạn 5 (LC-T094-41) |
| N4 lịch chạy, cache | Ca 4 bước 3–4 `:191-199`: lúc chờ không đụng website (đóng tab trang quản trị, không thao tác app; ca 5, ca S làm sau bước 4); quá giờ 2–3 phút mở trang quản trị: đã xuất bản thì «tự đăng» (ĐẠT); chưa thì F5 sau 1 phút, lúc này mới lên thì ghi «chỉ đăng sau khi có người mở trang», Lá Chắn xét; bỏ cách mở trang chủ để kích (SpeedyCache). Mục 2 dòng (e) `:53`, mục 7 dòng (e) `:280`, mục 8 |
| N5 điện thoại | Ca 1 bước 5 `:134`, mục 4.1 ô «Điện thoại» `:227`: kiểm GPS trên điện thoại ở ca 4/5 lúc bài công khai (không cần đăng nhập); mục 7 dòng (g)-1 |
| Mục 1 «Ghi cho sau» | Mục 8: (b) = CÓ ĐỔI thì phiếu client «đọc lại giờ sửa sau lệnh SEO» làm khe 2 rộng thêm đúng bằng thời gian lệnh SEO; phiếu đó phải sửa dòng khe 2 của sổ rủi ro hay chọn cách khác, Lá Chắn xét lại |
| Khác | Bảng đầu: «Khi nào» 1 giờ 30 tới 2 giờ; dòng Soạn, Nguồn ghi lượt 2 |

**Tôi thêm ngoài gợi ý của Lá Chắn** (đề nghị Lá Chắn đọc lại):
1. **Ca 0 bước 1 `:102`, quy tắc 1 `:31`: không chép tên ở dòng «Tài khoản: …».** Trang Kết nối in tên hiển thị (`users/me` → `name`: `seo_app/wordpress/client.py:1121`, `app/views/wordpress.py:123`). Tài khoản chưa đặt tên hiển thị thì tên này chính là tên đăng nhập. Kịch bản lượt 1 lại dặn «ghi lại» dòng này, nên nay chỉ ghi vai trò, kèm «trùng / không trùng» vào dòng «Tác giả công khai».
2. **Ca 5 và ca S bước 3 không còn làm trong lúc chờ ca 4.** Lượt 1 cho làm ca 5 trong lúc chờ. Nhưng mọi lệnh của app tới website là lượt tải không qua cache, nên cũng kích lịch chạy. Làm vậy, (e) có thể «đạt» chỉ nhờ chính buổi thử. Buổi thử dài thêm khoảng 10 phút.
3. **Luật đọc (b): lỗi ghi SEO lặp lại thì ghi «chưa kết luận» và báo Lá Chắn.** Lá Chắn chỉ dặn «chưa kết luận, ghi lại câu báo».

### Đối chiếu

- **Mã WordPress 6.9.4** của website (bản sao trong máy, chỉ đọc):
  - `wp-includes/default-filters.php:405-407`: `init` → `wp_cron`.
  - `wp-includes/cron.php:990-1004`: `wp_cron()` gắn `_wp_cron` vào `shutdown`, tức lịch chạy được kích ở **cuối** lượt tải. Vì vậy lần mở trang quản trị đầu tiên còn hiện trạng thái **trước** khi chính nó kích lịch chạy (ca 4 bước 4).
  - `wp-admin/edit.php:238` nạp `heartbeat`, và `wp-includes/js/heartbeat.js:63` có `mainInterval: 60`: tab danh sách bài đang mở gửi yêu cầu lên website khoảng mỗi phút.
  - Nhãn: `Pings` (`wp-admin/includes/class-wp-comments-list-table.php:514`), `Uploaded to` (`class-wp-media-list-table.php:368`), `Attempt to notify any blogs linked to from the post` (`wp-admin/options-discussion.php:52`), `Nickname` và `Display name publicly as` (`wp-admin/user-edit.php:506`, `:518`).
- **App:**
  - Câu múi giờ: `client.py:700-704`.
  - Câu đoạn dạng shortcode mức `warn` (`seo_app/publish/render.py:539`, `:590-597`), hiện bằng `st.warning`: khung vàng (`app/views/write.py:3180`).
  - LC-T094-41 ở `T-094-la-chan.md:125` ghi đủ hai điều kiện bật công tắc.
- **Script đối chiếu câu trích** (73 câu lượt 1 + 8 câu mới): «tổng: 81 thiếu: 0».
- **Kịch bản không có:**
  - email, `@`, tên file khóa;
  - tên đăng nhập hay tên tài khoản WordPress;
  - địa chỉ thật. Cả 4 địa chỉ đều dạng `https://<tên-miền>/…`.

### Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ PYTHONUTF8=1 uvx detect-secrets scan docs/team/reports/T-128-kich-ban-thu-that.md docs/team/reports/T-128-thu-ky.md
  "results": {}
$ (script đối chiếu câu trích)  tổng: 81 thiếu: 0
```

- `detect-secrets` có mồi đối chứng: chép hai file vào thư mục nháp, thêm dòng mở đầu một khóa riêng và một khóa AWS mẫu, rồi quét từ chính thư mục đó. Bắt được cả hai.
- Không chạy pytest, ruff (chỉ đổi tài liệu).

### Rủi ro và điểm cần chú ý

- **Cách đọc (e) dựa trên WordPress 6.9.4**, bản kích lịch chạy ở `shutdown`. Nếu website chạy bản khác, lần mở đầu có thể đã thấy bài xuất bản do chính lần mở đó (khe rất nhỏ). Lá Chắn lưu ý khi đọc dòng (e).
- **Ca 5 nay có thể chạy khi (b) chưa kết luận.** Điều này đúng luật Lá Chắn: ca 5 là một trong 3 lần. Nếu Abilities có đổi giờ sửa thì ca 5 bị chặn và bài vẫn là nháp, nên không có bài công khai ngoài ý muốn.
- **Nhãn tiếng Việt của WordPress chưa đối chiếu trên trang thật.** Bản sao trong máy không có file tiếng Việt. Các nhãn «Thảo luận», «Đã tải lên», «Biệt danh», «Tên hiển thị công khai», «Cố gắng thông báo…» đều có kèm tên tiếng Anh đã kiểm trong mã.
- **Không sửa `security.md`**, vì Chỉ Huy giao chỉ sửa kịch bản. Lá Chắn mục 1 có một gợi ý chữ, không bắt buộc: ghi giống nhau ở cả 3 dòng `:178-180` hai ý «Fable T-112 đồng ý» và «tự tái hiện được». Chỉ Huy quyết.

### Câu hỏi cho chủ dự án

Không có câu mới. Có hai việc mới để anh/chị quyết:
- lúc bắt đầu buổi thử: pingback (kịch bản mục 3.1);
- sau buổi thử: tên hiển thị và mật khẩu đăng nhập của tài khoản phần mềm (mục 8).

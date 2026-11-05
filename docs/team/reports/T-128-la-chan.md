# Biên bản bảo mật T-128 · Sổ rủi ro 3 giới hạn `modified_gmt` và kịch bản buổi thử thật Hẹn giờ / Đăng ngay · rút gọn

> **Model:** Claude **Opus 5.5** (dòng «You are powered by»: Opus 5.5). Chỉ Huy B giao chạy Opus 5.5; chủ dự án 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus 5.5, ghi rõ model.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-128](../tickets/T-128-so-rui-ro-va-kich-ban-thu-that.md) · [báo cáo Thư Ký](T-128-thu-ky.md) · [kịch bản buổi thử](T-128-kich-ban-thu-that.md) |
| Phạm vi | Rút gọn, chỉ đọc: `team/T-128` tại `fb1dece` (từ `main` cục bộ `2a7b408`), 3 file tài liệu: `docs/team/security.md` §6 (+3 dòng), kịch bản (266 dòng), báo cáo Thư Ký. Đối chiếu: Lá Chắn T-115 (mục 4, điều kiện 3), T-112 (phần B mục 4; lượt 3 mục 5), T-094 (LC-T094-41, -44); mã app trên nhánh (câu báo, nhãn nút, luật hẹn giờ); mã WordPress 6.9.4 của website (`D:\Suachuacuasat`, chỉ đọc) cho hành vi lõi |
| Máy | Windows 11 Pro, uv 0.13.4 (đạt ngưỡng `uvx`, T-078). Không chạy pytest (phiếu chỉ tài liệu). Không gọi website, không gọi Google |
| Ngày | 2026-11-05 (10:43–11:00, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (LC-T128-1, -2, -3: chỗ thiếu trong kịch bản). **3 dòng sổ rủi ro đúng biên bản T-115; mức và lý do chấp nhận hợp lý.** Kịch bản đủ (a)–(g) và các ý của LC-T094-44, không lộ bí mật, có bước dọn, bài thử là nháp hay hẹn giờ xa, Đăng ngay chỉ với bài chủ dự án duyệt, có bảng kết quả. **Gộp `main` được ngay.** Ba chỗ Thấp sửa **trước buổi thử** (mục 7) |

## Tóm tắt (cho chủ dự án)

- **Sổ rủi ro ghi đúng** ba khe hẹp anh/chị đồng ý ngày 04/11, đúng như biên bản T-115. Mức Thấp và lý do chấp nhận hợp lý.
- **Kịch bản buổi thử an toàn và gần đủ.** Không chứa mật khẩu, khóa, mã Sheet hay email tài khoản dịch vụ. Bài thử là nháp hay hẹn giờ xa; chỉ hai bài anh/chị duyệt mới lên công khai vài phút. Có 10 bước dọn và bảng ghi kết quả.
- **Tôi đề nghị thêm 3 chỗ nhỏ vào kịch bản trước buổi thử:**
  1. Câu hỏi quan trọng nhất của buổi thử là ghi SEO có làm đổi «giờ sửa bài» không. Muốn kết luận «không đổi» thì cần **ít nhất 3 lần gửi có ghi SEO** đều qua: một lần qua có thể chỉ là may (hai lệnh rơi vào cùng một giây).
  2. Khi bài thử lên công khai, xem **tên tác giả** hiện trên bài. Nếu đó là tên đăng nhập của tài khoản phần mềm thì người ngoài biết tên đăng nhập. Trước khi dùng thật nên đặt tên hiển thị khác (ví dụ «Pro-Metal») và giữ mật khẩu đăng nhập của tài khoản này thật mạnh.
  3. Khi dọn: **xóa ảnh thử trước, rồi mới xóa hẳn bài thử**. Xóa bài trước thì ảnh của bài nháp thành ảnh «không gắn» và hiện trong danh sách ảnh công khai. Xóa thêm các **pingback** (WordPress tự báo cho bài được link tới) nếu bài thử công khai có link.
- **Việc của anh/chị:** lúc này không có. Tới buổi thử thì làm như kịch bản.

## 1. Ba dòng sổ rủi ro (`security.md` §6, `:178-180`)

| Ý | Biên bản T-115 | Dòng sổ | Ý kiến |
|---|---|---|---|
| Giới hạn 1 · cùng giây | mục 4 ý 1 | `:178` | Đúng |
| Giới hạn 2 · khe giữa lệnh đọc kiểm và lệnh ghi (vài trăm mili giây, lần sửa kia bị «rửa») | mục 4 ý 2 | `:179` | Đúng |
| Giới hạn 3 · sửa chỉ meta (hộp chọn ảnh đại diện của trình soạn cổ điển, plugin ghi khóa meta riêng); trình soạn khối luôn đổi giờ sửa; thu hẹp bằng `featured_media` (không bắt buộc) | mục 4 ý 3, đoạn «Vì sao chấp nhận được» | `:180` | Đúng |
| Lý do: không có khóa lạc quan `If-Match`; cần người đang sửa đúng bài nháp vừa tạo trong vài giây; nội dung đã xác nhận bằng mã băm (T-102) | điều kiện 3 | cả ba dòng | Đúng |
| Dẫn mã `release_draft` `client.py:1545-1550` | — | `:178` | Đúng: các dòng này trên nhánh là phép so `known` → `_RELEASE_CHANGED`; `client.py` không đổi từ T-112 |

- **Mức Thấp, chấp nhận: đồng ý.** Ai sửa được bài nháp của tài khoản phần mềm phải có quyền `edit_others_posts` (Biên tập viên, Quản trị viên), tức đã tự đăng bài được. Plugin chạy trên website thì vốn đã làm được mọi việc. Khe không cho thêm quyền gì.
- Chữ (không bắt buộc): dòng `:178` ghi «Lá Chắn T-112 Fable đồng ý» mà dòng `:179`, `:180` không ghi; dòng `:179`, `:180` ghi «tự tái hiện được» mà dòng `:178` không ghi. Thật ra T-115 tái hiện cả ba, Fable T-112 (mục 2) đồng ý cả ba. Có thể ghi giống nhau ở cả ba dòng.
- **Ghi cho sau:** nếu buổi thử ra (b) = CÓ ĐỔI rồi có phiếu client «đọc lại giờ sửa sau lệnh ghi SEO», thì lần đọc lại đó sẽ nhận luôn mọi lần sửa của người khác trong lúc lệnh SEO đang chạy. Tức là **khe 2 rộng thêm** đúng bằng thời gian lệnh SEO. Phiếu đó phải sửa lại dòng `:179` (hay chọn cách khác), Lá Chắn xét lại.

## 2. Kịch bản buổi thử

### 2.1 Có đủ (a)–(g) và các ý của LC-T094-44 không: **đủ**

| Mục (T-112 phần B mục 4 / LC-T094-44) | Kịch bản | Ghi chú |
|---|---|---|
| (a) quyền `publish_posts` | Ca 0 bước 1 | — |
| (b) ghi SEO qua Abilities có đổi `modified_gmt` không | Ca 2 (đối chứng) + ca 3 | Cách kết luận cần chặt hơn: LC-T128-1 |
| (c) múi giờ, giờ hẹn trong trang quản trị | Ca 0 bước 2; ca 2 bước 2, 5 | App so theo độ lệch giờ (`client.py:705-707`), nên «UTC+7» cũng không bị cảnh báo, đúng như kịch bản viết. Ghi chú N2 |
| (d) trình soạn khối hay cổ điển | Ca 0 bước 3 | — |
| (e) WP-Cron đăng bài hẹn giờ đúng giờ | Ca 4 | Ghi chú N4 |
| (f) câu báo không lộ gì lạ | Quy tắc 8, mục «Suốt buổi · (f)» | 7 câu dừng đều có trong mã |
| (g) `srcset`, GPS; «< 5 triệu» | Ca 1 bước 4, 5 | Ghi chú N5 |
| Sheet bản sao; không bí mật; chỉ bài chủ dự án duyệt; header `Date`; Biên tập viên hẹn giờ qua REST; xem bài hiển thị thật | 3.4 + ca S; quy tắc 1, 2; ca 0 bước 4 + ca 2; ca 2; mục 4.1 | Mục 4.1 thiếu phần tác giả: LC-T128-2 |

Câu báo, nhãn nút mà kịch bản trích: tôi chạy một script riêng (chỉ đọc file `.py` dưới `app/`, `seo_app/` trên nhánh). Có 65 đoạn trích: 64 đoạn có nguyên văn trong mã, đoạn còn lại («khác giờ Việt Nam») được ghép lúc chạy (`client.py:709`). Khớp kết quả 73/73 của Thư Ký.

### 2.2 Không lộ bí mật: **đạt**

- Quy tắc 1 cấm ghi mật khẩu ứng dụng, mật khẩu đăng nhập, tên hay nội dung file khóa, email tài khoản dịch vụ. Mã Sheet chỉ ghi 4 ký tự cuối, đúng như app hiện (`mask_sheet_id`, `seo_app/google/sheets.py:230-231`). Cấm chụp `.env`, trang Hồ sơ có mật khẩu ứng dụng, khung tài khoản dịch vụ ở Cài đặt. Bước dọn 10 soát lại ảnh chụp.
- Bản thân kịch bản: địa chỉ chỉ viết `https://<tên-miền>/…`. Grep diff `fb1dece` không thấy email, link Sheet, chuỗi dạng mật khẩu ứng dụng hay đường dẫn máy. detect-secrets sạch (mục 6).
- Mọi lệnh trong kịch bản chỉ đọc và không cần mật khẩu: `curl.exe -sI` trang công khai, `Get-DnsClientCache` lọc `*googleapis.com`, mở `/wp-json/wp/v2/media` bằng cửa sổ ẩn danh.

### 2.3 Bài thử là nháp hay hẹn giờ xa; Đăng ngay chỉ với bài chủ dự án duyệt: **đạt**

- Ca 1 là nháp. Ca 2, ca 3 hẹn giờ **30 ngày sau**, rồi chuyển về nháp ngay. Chỉ ca 4 (hẹn 15 phút, để kiểm (e) như T-112 phần B yêu cầu) và ca 5 (Đăng ngay) lên công khai. Cả hai phải được chủ dự án duyệt nội dung ngay trước khi bấm (quy tắc 2, đầu ca 4, đầu ca 5) và được gỡ ngay. Quy tắc 8: có bài công khai ngoài ca 4, ca 5 là dừng.
- Ca 5 chỉ làm khi (b) = KHÔNG ĐỔI. Công tắc bật trong phiên, tắt lại khi dọn (bước 6).

### 2.4 Bước dọn: **có**, còn hai chỗ phải sửa (LC-T128-3)

### 2.5 Bảng kết quả cho Lá Chắn: **có** (mục 7, 16 dòng)

Cần thêm: dòng tác giả (LC-T128-2), số lần gửi có ghi SEO ở dòng (b) (LC-T128-1), tên file ảnh của từng ca (LC-T128-3).

## 3. Lỗi phát hiện

### LC-T128-1 · Thấp · Một lần ca 3 qua chưa đủ để kết luận (b) = «KHÔNG ĐỔI»

- **Chỗ:** ca 3 bước 2 (`T-128-kich-ban-thu-that.md:155-161`); bảng mục 7, dòng (b).
- **Vì sao:** phép so dùng `modified_gmt` tính **tới giây**, chính là giới hạn 1 của sổ rủi ro. Ở ca 3, lệnh ghi SEO qua Abilities chạy ngay sau lệnh ghi trước của app (đặt ảnh đại diện, hay tạo nháp), chỉ cách nhau một lượt hỏi bài. Giả sử Abilities có đổi giờ sửa, mà hai lệnh lại rơi vào **cùng một giây**: giờ sửa vẫn bằng giờ app nhớ, app hẹn giờ được, kịch bản sẽ kết luận «KHÔNG ĐỔI». Kết luận sai không làm mất an toàn (lúc dùng thật client vẫn từ chối, bài vẫn là nháp). Nhưng nó dẫn tới bật công tắc trong khi Hẹn giờ/Đăng ngay kèm «Ghi SEO» gần như lần nào cũng bị chặn. Câu tôi viết ở biên bản T-112 («sẽ **luôn** bị `_RELEASE_CHANGED`») cũng nên hiểu là «gần như luôn», vì cùng lý do.
- Chiều ngược lại: chỉ được kết luận «CÓ ĐỔI» khi lệnh ghi SEO **thành công**. Lệnh ghi SEO đi đường meta mà lỗi giữa chừng cũng ra `_RELEASE_CHANGED` (`client.py:1423`, `:1428`), kèm một câu lỗi SEO.
- **Sửa (Thư Ký), thêm luật đọc (b):**
  - **CÓ ĐỔI:** một lần gửi bật «Ghi SEO» (ca 3, ca 4 hay ca 5) có cả câu «Đã ghi SEO vào hộp SiteSEO của bài nháp.» lẫn câu «Bài nháp trên website đã bị sửa sau lần phần mềm ghi cuối…», trong khi ca 2 đã qua và không ai mở bài.
  - **KHÔNG ĐỔI:** chỉ khi **ít nhất 3 lần** gửi bật «Ghi SEO» đều hẹn giờ hay đăng được (ca 3, ca 4, ca 5; thiếu thì lặp ca 3, mỗi lần chuyển bài về nháp như ca 2 bước 6).
  - Lần gửi bật «Ghi SEO» mà không có câu «Đã ghi SEO…»: chưa kết luận, ghi lại câu báo.
  - Ca 4 bị chặn vì (b): làm lại ca 4 với «Ghi SEO» tắt để vẫn kiểm được (e), rồi bỏ ca 5.
  - Bảng mục 7, dòng (b): ghi số lần gửi có ghi SEO và kết quả từng lần.

### LC-T128-2 · Thấp · «Xem bài hiển thị thật» chưa kiểm tên tác giả: bài công khai có thể làm lộ tên đăng nhập của tài khoản phần mềm

- **Chỗ:** mục 4.1; bảng mục 7; mục 8.
- **Vì sao:** bài app đăng có tác giả là tài khoản Biên tập viên của app. Khi tài khoản này có bài công khai, người lạ xem được:
  - tên hiển thị trên bài (theme in ra);
  - trang tác giả `/author/<slug>/`;
  - `GET /wp-json/wp/v2/users`, không cần đăng nhập. Danh sách này chỉ có người đã có bài công khai (`class-wp-rest-users-controller.php:319-322`) và trả về `slug` = `user_nicename` (`:1095`).

  Tài khoản tạo theo `TIEN-DO.md:132` chỉ có tên đăng nhập, nên tên hiển thị và slug **chính là tên đăng nhập**. Biết tên đăng nhập rồi thì người lạ có thể dò mật khẩu ở trang đăng nhập. Tài khoản này lại có quyền `unfiltered_html` (sổ rủi ro dòng 2026-10-28), nên lộ mật khẩu thì nặng hơn tài khoản thường. Thêm nữa, dòng tác giả là tên đăng nhập trông không tốt với người đọc và với SEO (phần tác giả).
- **Sửa (Thư Ký):**
  - Mục 4.1 thêm một ô: «Tên tác giả trên bài, link trang tác giả và `https://<tên-miền>/wp-json/wp/v2/users` (cửa sổ ẩn danh, lúc bài đang công khai): có hiện tên đăng nhập của tài khoản phần mềm không. Chỉ ghi có/không, không chép tên.»
  - Bảng mục 7 thêm dòng «Tác giả công khai».
  - Mục 8: trước khi dùng thật, chủ dự án quyết:
    - đặt **Biệt danh** và **Tên hiển thị công khai** của tài khoản phần mềm (Người dùng → Hồ sơ), ví dụ «Pro-Metal»;
    - đặt mật khẩu **đăng nhập** của tài khoản này dài, ngẫu nhiên (app chỉ dùng mật khẩu ứng dụng);
    - slug trang tác giả vẫn là tên đăng nhập. Muốn giấu luôn thì dùng chức năng chặn liệt kê người dùng của plugin bảo mật (bản sao trong máy, thư mục ngày 26/02/2025, có Loginizer; website hiện nay có thể khác), hoặc đổi tác giả của bài.
  - Lá Chắn xét theo kết quả buổi thử.

### LC-T128-3 · Thấp · Bước dọn: xóa hẳn bài trước ảnh làm ảnh thử hiện công khai; chưa dọn pingback

- **(i) Thứ tự** (`:227-228`): bước 3 xóa vĩnh viễn bài, bước 4 mới xóa ảnh.
  - Khi xóa hẳn một bài, WordPress chuyển ảnh của bài lên cấp cha của bài (`post.php:3834-3835`, `:3862-3863`). Bài không có cha nên ảnh thành «không gắn».
  - Ảnh không gắn bị coi như đã công khai (`class-wp-rest-posts-controller.php:1765-1779`). Vì vậy ảnh của các bài nháp ca 1–3 (chưa từng công khai, T-110) sẽ hiện trong `/wp-json/wp/v2/media` cho tới khi làm bước 4.
  - Sau bước 3, cột «Đã tải lên» (Uploaded to) trong Media không còn tên bài thử, nên khó nhận ra ảnh thử: dễ xóa nhầm ảnh thật hay sót ảnh thử.
  - **Sửa:** đổi thứ tự. Vào Media → Thư viện (dạng danh sách), nhận ảnh thử theo cột «Đã tải lên» là tên bài thử, xóa vĩnh viễn ảnh **trước**, rồi mới xóa vĩnh viễn bài. Bảng mục 7 ghi tên file ảnh của từng ca.
- **(ii) Pingback:**
  - WordPress mặc định bật «Cố gắng thông báo cho các blog được liên kết tới từ bài viết» (`default_pingback_flag` = 1, `wp-admin/includes/schema.php:433`).
  - Khi bài lên công khai (ca 4, ca 5), WordPress đánh dấu `_pingme` (`post.php:8014-8016`), rồi lịch chạy gửi pingback tới mọi link trong bài (`comment.php:3019-3034`), kể cả link nội bộ tới bài thật của website. Bài thật có thể nhận bình luận «Pingback: Bài thử…» trỏ tới một trang đã xóa.
  - Website còn báo cho dịch vụ cập nhật (`ping_sites`, mặc định Ping-O-Matic, `schema.php:450`).
  - **Sửa:**
    - Mục 3.1 thêm việc chủ dự án quyết, giống phần plugin tự báo bài mới: tắt tạm ô đó ở **Cài đặt → Thảo luận**, hay chấp nhận.
    - Mục 3.3: bài thử không chèn link ra website khác.
    - Mục 6 thêm một bước: **Bình luận** → xóa pingback đến từ bài thử (nếu có).

## 4. Ghi nhận (không tính lỗi, nên sửa cùng đợt)

- **N1 · mục 3.3:** dấu `[` `]` trong tiêu đề bài chỉ ra dòng **Cảnh báo**, không bị «chặn» (`seo_app/publish/render.py:590-597`, mức `warn`). Lời khuyên tránh dấu ngoặc vuông vẫn đúng; chỉ sửa chữ cho khớp.
- **N2 · (c):** website không trả múi giờ thì app hiện câu «Không đọc được múi giờ của website…» (`client.py:700-704`). Gặp câu này thì ghi vào (c).
- **N3 · mục 8:** LC-T094-41 (`T-094-la-chan.md:125`) cho bật công tắc để dùng thật khi đã có **buổi thử thật và Lá Chắn rà soát Giai đoạn 5**. Mục 8 nên ghi đủ cả hai ý, hoặc Chỉ Huy ghi vào bảng việc nếu đã có kế hoạch khác.
- **N4 · (e):** website có SpeedyCache (bản sao trong máy, và kịch bản cũng nhắc tới). Trang lấy từ cache không chạy PHP, nên mở trang chủ có thể không kích được lịch chạy. Cần ghi rõ bài tự đăng **trước** hay chỉ **sau** khi có người mở trang. Nếu chỉ lên sau khi mở trang thì Lá Chắn xét (có thể cần lịch chạy thật của hosting).
- **N5 · (g)-1 trên điện thoại:** muốn xem trước bài nháp trên điện thoại thì phải đăng nhập trang quản trị trên điện thoại. Kiểm ở ca 4, ca 5, lúc bài đang công khai, thì không cần đăng nhập.
- **N6 · (b):** bản WordPress trong máy chỉ có SiteSEO **1.1.6** (thư mục ngày 26/02/2025, chưa có Abilities), còn website chạy 1.4.2 (`TIEN-DO.md`). Vì vậy không đọc mã để trả lời trước được; (b) chỉ trả lời được bằng buổi thử.

## 5. Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | 3 file không có bí mật (detect-secrets kèm file mồi; grep diff) |
| S2 | Đạt | Kịch bản cấm ghi, chụp bí mật (quy tắc 1, dọn bước 10) |
| W1 | Đạt (thủ tục) | Bài thử là nháp hay hẹn giờ xa; chỉ ca 4, ca 5 công khai, có duyệt; công tắc bật trong phiên, tắt khi dọn |
| W2 | Đạt khi sửa LC-T128-3 (ii) | Không sửa bài thật, trừ: mở xem một bài cũ (ca 0 bước 3, không lưu); pingback có thể ghi bình luận lên bài thật |
| S3, W3, W4, A1–A3, U1–U3, F1–F3, D1–D3 | Không áp dụng | Phiếu chỉ có tài liệu: không code, thư viện, test |

## 6. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| `uv --version` trước `uvx` | 0.13.4 | ✔ |
| detect-secrets (`PYTHONUTF8=1`; chép 3 file ra thư mục ngoài git cùng file mồi tiếng Việt, `scan --all-files .`) | 3 file: 0 kết quả; file mồi: bị bắt | ✔ |
| Grep diff `fb1dece` (email, link Sheet, chuỗi dạng mật khẩu ứng dụng, `.json`, đường dẫn máy, khóa) | 0. Địa chỉ duy nhất là `https://<tên-miền>/…` | ✔ |
| Script đối chiếu câu trích (chỉ đọc mã) | 65 đoạn: 64 có nguyên văn, 1 ghép lúc chạy | ✔ |
| Gộp thử với `main` cục bộ `8caab2f` | `git merge-tree`: không xung đột (cây `a8313f8`), hai bên không chung file | ✔ |
| pytest | Không chạy (phiếu chỉ tài liệu, theo giao việc) | — |

## 7. Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **Gộp `main`: được ngay.** Phiếu chỉ có tài liệu; sổ rủi ro đã đúng.
2. **Trước buổi thử** (Thư Ký, vài dòng trong kịch bản): sửa LC-T128-1, -2, -3 theo các gợi ý ở mục 3; N1–N5 nên sửa cùng lúc. Lá Chắn đọc lại các chỗ sửa (rút gọn, vài phút), hoặc Chỉ Huy tự đối chiếu theo gợi ý.
3. **Sau buổi thử:** Lá Chắn đọc bảng mục 7 (như mục 8 của kịch bản), kể cả dòng tác giả mới, rồi kết luận có cho dùng Hẹn giờ / Đăng ngay không.

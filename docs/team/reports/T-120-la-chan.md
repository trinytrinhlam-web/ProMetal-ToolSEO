# Biên bản bảo mật T-120 · Đọc thiết kế Giai đoạn 6 (theo dõi bài qua Google Search Console) · rút gọn

> **Model:** chạy **tạm Claude Opus 5.5** vì hạn mức Fable tuần này đã hết tới 04/11 10:00 (Chỉ Huy B giao). Cần kiểm lại bằng Claude Fable, nên gộp vào lượt Fable cho nhóm Google (T-116 nhóm 4).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (**Opus tạm**, xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-120](../tickets/T-120-thiet-ke-giai-doan-6.md) · báo cáo thiết kế [T-120-tho-may.md](T-120-tho-may.md) |
| Phạm vi | Rút gọn, **chỉ đọc**: nhánh `team/T-120` tại `3a2e9f7` (từ `main` `29499dd`). Chỉ 2 file tài liệu: báo cáo thiết kế (671 dòng) và bản chép phiếu. Đối chiếu `docs/team/security.md`, và code mà thiết kế dựa vào: `seo_app/config.py`, `seo_app/google/service_account.py`, `seo_app/google/sheets.py` (lớp vận chuyển), `seo_app/wordpress/client.py` (`is_site_link`, `post_statuses`), `seo_app/plan/model.py` (`clean_text`), `app/views/plan.py` (`safe_rows`), `app/views/settings.py`, `seo_app/images/data_dir.py`, `.gitignore`. Không gọi Google hay website thật, không sửa code, không chạy pytest |
| Ngày | 2026-11-03 (22:35–23:05, giờ máy +07) |
| **Kết luận** | **ĐẠT** cho phiếu tài liệu (không bí mật, không dữ liệu khách). **Thiết kế đủ để mở phiếu code**, với điều kiện Chỉ Huy chép **24 điều kiện bảo mật LC-T120-1 → -24** vào đúng phiếu (mục «Điều kiện theo phiếu»). Không chỗ nào phải thiết kế lại. 9 chỗ thiếu đã có cách sửa, nằm trong các điều kiện LC-T120-16 → -24 |

## Tóm tắt (cho chủ dự án)

- **Thiết kế theo dõi Google an toàn và đủ để bắt đầu viết code.** Những điểm quan trọng nhất đều đúng hướng:
  - Phần mềm dùng lại **đúng một** file khóa Google đang có, xin quyền **chỉ đọc** cho Search Console, và anh/chị cấp cho tài khoản phần mềm quyền **«Hạn chế»** (chỉ xem). Có hai lớp «chỉ đọc» độc lập: code có lỡ gửi lệnh sửa thì Google cũng từ chối.
  - Số liệu **chỉ lấy khi anh/chị bấm nút**; mở trang không gọi mạng. Số liệu chỉ nằm trong máy, mặc định không ghi lên Google Sheet, không gửi cho AI.
  - Từ khóa người lạ gõ trên Google được coi là **chữ chưa tin cậy**: làm sạch, chỉ hiện như chữ thường, không bao giờ thành link.
  - Số của trang staging không lẫn vào: phần mềm chỉ nhận thuộc tính khớp website, lọc ngay ở Google rồi kiểm lại trong máy.
- **Tôi bổ sung 9 điều kiện** để các phiếu code làm cho đúng. Ví dụ:
  - Kiểm «thuộc tính có đúng website không» theo từng phần của tên miền, để một tên như `evilsuachuacuasat.com` không lọt.
  - Biểu đồ không chứa chữ nào lấy từ Google.
  - Trang Cài đặt cũng không tự gọi Google khi vừa mở.
  - Hai tab bấm «Lấy số liệu» cùng lúc thì chỉ một tab chạy.
  - Nếu anh/chị cho đưa từ khóa sang Kế hoạch (câu 7 = B) thì chỉ nhận từ khóa ngắn, chữ và số, bỏ số điện thoại, email.
- **Về 7 câu hỏi:** không câu nào có lựa chọn làm hở bảo mật. Về phía bảo mật, tôi đồng ý với các khuyến nghị của Thợ Máy, nhất là **câu 4 = A** (không ghi Sheet) và **câu 6 = A** (để sau).

## Bằng chứng (phiếu tài liệu)

| Kiểm | Kết quả |
|---|---|
| Thay đổi chỉ là tài liệu | `git diff --name-only 29499dd..3a2e9f7`: `docs/team/reports/T-120-tho-may.md`, `docs/team/tickets/T-120-thiet-ke-giai-doan-6.md`. Không code, cấu hình, test, thư viện |
| Không bí mật (S1) | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 2 file: `results: {}`. Mồi khóa giả trong bản sao phiếu (có chữ tiếng Việt): bắt được 1; đã xóa mồi. Email trong phác thảo Cài đặt (`seo-app@du-an.iam…`) là email mẫu; không có `private_key`, không có khóa |
| Không gọi mạng thật | Thợ Máy ghi chỉ đọc trang tài liệu công khai, không gọi Search Console, Sheets, website, không đọc `.env`; tôi cũng không gọi |

## Đối chiếu với code hiện có (điều thiết kế dựa vào)

| Thiết kế nói | Kiểm | Đúng? |
|---|---|---|
| `GSC_SITE_URL` đã có, chưa dùng | `seo_app/config.py:34` (trong danh sách biến), `:151`; `.env.example:54` | Đúng. Biến này cũng đọc từ biến môi trường của máy, nên biến môi trường đè `.env` (xem LC-T120-23) |
| Xác thực Google hiện tạo với đúng một phạm vi, không mạo danh | `service_account.py:44` (`SHEETS_SCOPE`), `:372-380` (`_credentials`, `scopes=[SHEETS_SCOPE]`); docstring `:20-22`: không `google.auth.default()`, không `with_subject` | Đúng |
| Lớp vận chuyển của Sheets dùng lại được | `sheets.py:260` `_NoAuth`, `:267` `_Bearer`, `:279` `_TooLarge`, `:283` `_Redirected`, `:291` `_refuse_redirect`, `:302` `_read_limited`, `:317` `_close_and_status`, `:346` `_TokenRequest` (`allow_redirects=False`, giờ chờ riêng: `:371-372`) | Đúng |
| `_answer` của Sheets không chặn `NaN` | `sheets.py:893-902`: `json.loads` không `parse_constant` | Đúng. Với Sheets không sao (ô là chữ); client Search Console phải chặn (LC-T120-5) |
| `is_site_link` từ chối địa chỉ lạ | `wordpress/client.py:2322-2346`: chỉ `https`, đúng tên máy (kể cả từ chối tên miền con), không tên/mật khẩu trong địa chỉ, không khoảng trắng, ký tự điều khiển, vô hình, `" ' < > \``, `\`, quá dài; cổng phải khớp | Đúng. Không kiểm phần đường dẫn; thiết kế thêm kiểm tiền tố `WORDPRESS_URL` + `/` (đúng) |
| `clean_text` làm sạch từ khóa | `plan/model.py`: NFC; bỏ Cc (trừ khoảng trắng), Cf (gồm ký tự đảo hướng chữ), Cs, Co, Cn, ký tự «mặc định bỏ qua»; gộp khoảng trắng | Đúng, đủ cho chữ một dòng |
| `safe_rows` trung hòa công thức khi tải CSV | `app/views/plan.py:218-229` | Đúng; phải dùng cho **mọi** bảng có chữ từ Google (LC-T120-11) |
| Cache trong `data/` bị git chặn | `.gitignore:22-24` (`data/`, `*.sqlite`, `*.sqlite3`) | Đúng |
| Chặn `data/` là liên kết | `seo_app/images/data_dir.py:35` (`is_link`), `:43` (`dir_has_link`) | Có; cache mới phải dùng (LC-T120-9). SL-T117-1 nói các cache cũ chưa dùng hết; cache mới đừng lặp lại |
| Ngày đăng lấy bằng lệnh chỉ đọc có sẵn | `wordpress/client.py:1659` (`post_statuses`) | Đúng |

## Điều kiện theo phiếu (Chỉ Huy chép vào phiếu)

Đồng ý cả 15 điều kiện Đ1–Đ15 của Thợ Máy (mục 5 báo cáo thiết kế), đổi thành LC-T120-1 → -15, có bổ sung ở cột «Lá Chắn thêm». LC-T120-16 → -24 là điều kiện mới.

| Mã | Điều kiện | Lá Chắn thêm | Phiếu |
|---|---|---|---|
| LC-T120-1 | = Đ1: `webmasters.readonly` là phạm vi duy nhất cho Search Console; `load_service_account` chỉ nhận 2 phạm vi cố định; client Sheets vẫn chỉ có phạm vi Sheets | Phạm vi chỉ lấy từ hằng trong module, không bao giờ từ `.env`, `config/` hay giao diện. Test: phạm vi lạ, danh sách 2 phạm vi, chuỗi rỗng đều bị từ chối | T-121 |
| LC-T120-2 | = Đ2: danh sách lệnh cố định, kiểm trước khi gửi ở một chỗ; thân đúng 1 trong 3 khuôn; `{siteUrl}` đúng thuộc tính đã kiểm; bộ lọc so nguyên văn với tiền tố dựng từ `WORDPRESS_URL` | Thân so **đủ khóa và đủ giá trị**, không chỉ «có các khóa cần». Khóa lạ (kể cả `searchType`), `type` khác `web`, `dataState` ngoài danh sách đều bị từ chối | T-121 |
| LC-T120-3 | = Đ3: chỉ các máy chủ ở mục 2.3; không theo chuyển hướng; giờ chờ ≤ 30 giây; câu trả lời ≤ 8 MB (`query`), ≤ 256 KB (`sites`); `_NoAuth`, `_Bearer`, `_TokenRequest` | Xem LC-T120-18 (test chứng minh từng lớp được nối đúng) | T-121 |
| LC-T120-4 | = Đ4: câu lỗi cố định; mã lý do chỉ đọc từ danh sách ASCII cố định | Không chép `siteUrl`, đường dẫn trang, từ khóa, câu của Google vào câu lỗi hay câu `st.error` | T-121 |
| LC-T120-5 | = Đ5: kiểm từng dòng như mục 2.4 (`bool`, `NaN`/`Infinity`, JSON trùng khóa, `RecursionError`, tỉ lệ dòng hỏng) | Chặn `NaN` ngay ở bộ đọc JSON của client mới (`parse_constant`), không dựa vào `_answer` của Sheets | T-121 |
| LC-T120-6 | = Đ6: thuộc tính phải phủ website; từ chối `http://` và thuộc tính staging; dòng ngoài tiền tố bị bỏ cả khi Google trả | Xem LC-T120-17 (kiểm theo từng phần tên miền) | T-121, T-123 |
| LC-T120-7 | = Đ7: không lệnh ghi nào tới Search Console; test kiểm danh sách lệnh không có `PUT`/`DELETE` | Thêm: không `sites.add`/`delete`, `sitemaps.*`, URL Inspection (trừ câu 6 = B, khi đó qua Lá Chắn riêng) | T-121 |
| LC-T120-8 | = Đ8: ≤ 20 lệnh mỗi lần bấm, không song song, thử lại 429 tối đa 1 lần, trần `startRow` | Xem LC-T120-22 (chỉ một lần lấy chạy cùng lúc) | T-121, T-124 |
| LC-T120-9 | = Đ9: cache kiểm như `plan_cache`; một dòng sai → bỏ cả cache; mã băm phạm vi đổi → bỏ cache; không mở khi `data/` là liên kết | Dùng `data_dir.dir_has_link` ngay từ đầu (không lặp SL-T117-1); SQL chỉ tham số `?` | T-122 |
| LC-T120-10 | = Đ10: mốc ngày giờ từ cache, Google, WordPress kiểm năm trước khi đổi múi giờ hay cộng trừ; bắt `OverflowError` | Thêm `ValueError` như T-118 (LC-T113-2) | T-122, T-123, T-124 |
| LC-T120-11 | = Đ11: chữ từ Google chỉ hiện dạng chữ thuần; không `unsafe_allow_html`; chú thích nổi của biểu đồ chỉ có số và ngày | **Mọi** bảng có chữ từ Google (từ khóa, đường dẫn, «Trang khác», tên thuộc tính) đi qua `safe_rows` trước `st.dataframe`; không cột `LinkColumn` nào cho chữ từ Google | T-123, T-125 |
| LC-T120-12 | = Đ12: ghi `GSC_SITE_URL` qua `env_file` với bộ kiểm chặt, ghi nguyên tử, báo khi biến môi trường đè | Giá trị lưu phải là một mục vừa nhận từ `sites` trong cùng phiên **và** qua bộ kiểm, không nhận chữ gõ tay ở đường này | T-124 |
| LC-T120-13 | = Đ13: từ khóa không vào lời dặn AI, không ghi Sheet (trừ câu 7 = B theo LC-T120-24) | | T-124, T-125, T-127 |
| LC-T120-14 | = Đ14: trang theo dõi kiểm đăng nhập như mọi trang; không gọi mạng khi mở trang; client tạo mới mỗi lần bấm | Xem LC-T120-21 (áp cả cho Cài đặt) | T-125 |
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-16** | **Không mạo danh, không phạm vi rộng**: không `with_subject` (ủy quyền toàn miền), không `google.auth.default()`, không phạm vi `cloud-platform` hay `webmasters` (đọc-ghi); mỗi client một đối tượng xác thực, đúng một phạm vi | Test: đối tượng xác thực của client Search Console có đúng `[webmasters.readonly]`, không có `subject` | T-121 |
| **LC-T120-17** | **Kiểm «phủ website» theo từng phần tên miền**: `sc-domain:` chỉ nhận chữ thường ASCII/`xn--`, nhãn hợp lệ, không cổng, IP, `@`, đường dẫn, dấu chấm cuối. Tên máy của website phải **bằng** tên miền hoặc **kết thúc bằng `.` + tên miền**. Không dùng `endswith(tên miền)` trần: `evilsuachuacuasat.com` sẽ lọt. Dạng tiền tố: đúng `https://<tên máy của WORDPRESS_URL>/` | Test: `sc-domain:evilsuachuacuasat.com`, `sc-domain:suachuacuasat.com.evil.com`, `sc-domain:SUACHUACUASAT.com`, `sc-domain:suachuacuasat.com.`, `sc-domain:1.2.3.4`, `https://suachuacuasat.com:8443/`, `https://suachuacuasat.com/blog/` đều bị từ chối hay xử lý đúng | T-121 |
| **LC-T120-18** | **Test chứng minh từng lớp chặn được nối đúng ở client mới**, không chỉ «có nhập»: 3xx bị từ chối, thân quá cỡ bị cắt và báo, giờ chờ truyền đúng, `.netrc` không được đọc, mã truy cập xin qua `_TokenRequest`, `repr` của phần xác thực không lộ mã | Docstring của `sheets.py` và module mới ghi chéo: sửa một bên phải chạy test cả hai | T-121 |
| **LC-T120-19** | **Đường dẫn đã giải mã và tên máy từ Google** (mục «Trang khác», 3 tên máy ngoài website ở «Kiểm tra»): qua `clean_text` sau khi giải mã `%`, cắt độ dài, hiện như chữ, không bao giờ thành link. Tên máy kiểm đúng dạng tên miền trước khi hiện | Giải mã `%` ra ký tự đảo hướng, ký tự vô hình thì bị `clean_text` bỏ | T-123, T-125 |
| **LC-T120-20** | **Biểu đồ dựng từ khuôn cố định trong code**: dữ liệu nhúng chỉ có số và ngày; không chữ nào từ Google hay WordPress nằm trong đặc tả Vega-Lite (tên bài đặt **ngoài** biểu đồ, bằng `st.markdown(escape_markdown(…))`). Không `expr` dựng từ chữ ngoài, không kênh `href`, không nguồn dữ liệu `url` | Vega có lịch sử lỗi chạy mã qua biểu thức; giữ đặc tả cố định là cách chắc nhất | T-125 |
| **LC-T120-21** | **Không gọi mạng khi mở trang**, áp cho cả trang theo dõi **và** mục Search Console trong Cài đặt («Tìm thuộc tính», «Kiểm tra» chỉ chạy khi bấm). Không `st.cache_data`/`st.cache_resource` có hạn quanh lệnh gọi mạng, không `st.fragment(run_every=…)`, không tự làm mới | Test AppTest: mở trang và Cài đặt dưới bộ chặn mạng, giả client đếm lệnh = 0 | T-124, T-125 |
| **LC-T120-22** | **Chỉ một lần lấy số liệu chạy cùng lúc** trong một tiến trình app: khóa cấp module. Tab thứ hai bấm thì báo «đang lấy ở tab khác», không gửi lệnh. Mốc «vừa lấy lúc …» để chặn bấm lại lưu trong cache (dùng chung các tab), không trong `session_state` | Tránh tốn gấp đôi hạn mức và hai lượt ghi xen nhau | T-124 |
| **LC-T120-23** | **Cảnh báo biến môi trường `GSC_SITE_URL` đè `.env`** theo đúng điều kiện của `load_settings`: biến **có mặt** là đè, kể cả rỗng (`name in os.environ`, như `password_hash_overridden` T-105). Không chép cách `.strip()` của thẻ Sheet (`settings.py:609`, lệch đã biết) | | T-124, T-125 |
| **LC-T120-24** | (Chỉ khi câu 7 = B) **Từ khóa sang Kế hoạch**: chỉ nhận từ khóa qua bộ lọc chặt hơn ô từ khóa thường. Chỉ chữ (kể cả tiếng Việt), số, khoảng trắng, `-`; ≤ 80 ký tự; bỏ từ khóa có số điện thoại/email (`personal_info`). Hiện nguyên văn cho người dùng tick; ≤ 10 mỗi lần; không AI ở bước này; đề xuất ghi nguồn «Search Console». Vẫn qua mọi bộ kiểm của dòng kế hoạch; khi bài được viết, từ khóa vào lời dặn AI trong khung dữ liệu như hiện nay (T-098) | Kẻ xấu muốn «cài» lệnh vào từ khóa phải có nhiều người gõ cùng một câu trong 2–3 tháng (Google ẩn từ khóa hiếm). Bộ lọc ký tự làm câu lệnh dài, có dấu câu không lọt | T-127 |

## Chỗ thiếu hay rủi ro trong thiết kế (kèm cách sửa)

| # | Chỗ | Rủi ro nếu bỏ qua | Mức nếu lọt vào code | Cách sửa |
|---|---|---|---|---|
| 1 | Kiểm «phủ website» chỉ ghi «tên máy bằng tên miền hoặc là tên miền con» | Viết bằng `endswith` trần thì `sc-domain:evilsuachuacuasat.com` qua kiểm. Hậu quả nhẹ: chỉ đọc số của thuộc tính mà tài khoản dịch vụ được cấp; bộ lọc tiền tố vẫn chặn dòng lạ | Thấp | LC-T120-17 |
| 2 | Không nói tới ủy quyền toàn miền | Ai thêm `with_subject` «cho tiện» thì tài khoản dịch vụ hành động thay người dùng Workspace | Trung bình | LC-T120-16 |
| 3 | Lớp vận chuyển «nhập» từ `sheets.py` | Nhập mà quên nối (ví dụ quên móc `_refuse_redirect`, quên `allow_redirects=False`) thì vẫn chạy được, không ai thấy | Trung bình | LC-T120-18 |
| 4 | Đường dẫn «Trang khác», tên máy ở «Kiểm tra» | Ký tự đảo hướng sau khi giải mã `%` làm đường dẫn hiện sai, dễ nhầm trang | Thấp | LC-T120-19 |
| 5 | «Tên bài ở tiêu đề biểu đồ, dựng bằng `escape_markdown`» | Đặt tên bài vào đặc tả Vega-Lite thì chữ ngoài nằm trong một bộ dựng có ngôn ngữ biểu thức; `escape_markdown` không có nghĩa ở đó | Thấp | LC-T120-20 |
| 6 | «Không gọi mạng khi mở trang» mới nói cho trang theo dõi | Mục Search Console trong Cài đặt tự gọi `sites` khi mở thì tốn hạn mức, lộ việc dùng | Thấp | LC-T120-21 |
| 7 | Chặn bấm lại < 10 phút nhưng không nói hai tab cùng bấm | Hai lượt lấy song song, tốn gấp đôi hạn mức tải, ghi xen nhau (giao dịch SQLite vẫn giữ file đúng) | Thấp | LC-T120-22 |
| 8 | «Báo khi biến môi trường đè» chưa nói điều kiện | Chép cách `.strip()` của thẻ Sheet thì biến rỗng không được cảnh báo, app lại bỏ `.env` | Thấp | LC-T120-23 |
| 9 | Câu 7 = B dùng bộ lọc chung | Từ khóa dài, có dấu câu là chỗ dễ giấu lệnh cho AI khi bài được viết | Thấp | LC-T120-24 |

Không chỗ nào cần thiết kế lại. Thiết kế đã có sẵn các lớp quan trọng: chỉ đọc hai lớp, danh sách lệnh cố định, kiểm từng dòng, lọc staging ba lớp, không chạy ngầm, không thư viện mới.

## Câu hỏi cho chủ dự án: nhận xét bảo mật

| Câu | Nhận xét Lá Chắn |
|---|---|
| 1 (vị trí trong menu) | Không khác nhau về bảo mật; cả ba phải kiểm đăng nhập (U2) và theo LC-T120-11, -14, -21 |
| 2 (chọn thuộc tính) | A an toàn với LC-T120-12, -23 (chỉ lưu mục vừa nhận từ Google, qua bộ kiểm chặt). B cũng an toàn: gõ sai thì bị bộ kiểm ở client từ chối |
| 3 (số tạm) | Không ảnh hưởng bảo mật |
| 4 (ghi Sheets) | **Đồng ý A.** Giữ nguyên 5 lệnh Sheets đã kiểm, chữ người lạ không ra khỏi máy. Nếu B: chỉ ghi số tổng, lệnh ghi tab mới phải qua Lá Chắn đầy đủ |
| 5 (ngưỡng nhãn) | Không ảnh hưởng bảo mật |
| 6 (kiểm lập chỉ mục) | **Đồng ý A.** B thêm một máy chủ Google, và chưa rõ quyền «Hạn chế» có đủ không. Nếu B: phải qua Lá Chắn riêng |
| 7 (từ khóa sang Kế hoạch) | A ít rủi ro nhất. B chấp nhận được với LC-T120-24 |

## Phiếu nào chạy trước được

Đồng ý thứ tự của Thợ Máy.
- **Đợt 1** chạy song song được: T-121 client, T-122 cache, T-123 lõi tính toán. Mỗi phiếu ở thư mục riêng, không chờ câu trả lời.
- Hai chỗ đụng code dùng chung đã có lệnh chạy test mọi nơi gọi (bài học T-041, T-091): `service_account.py` (T-121) và `env_file.py` (T-124).
- Mức Lá Chắn:
  - **Đầy đủ:** T-121 (đường gọi mới tới Google, phạm vi), T-122, T-124, T-125.
  - **Rút gọn:** T-123 (hàm thuần), T-126 (tài liệu).
  - Nên dùng **Fable** cho T-121 khi có hạn mức.

## Ghi nhận (không xếp lỗi)

- **Sổ rủi ro dòng 28/10** (biến proxy, chứng chỉ của máy áp cho kết nối WordPress và Google qua `requests`, `google-auth`) đã phủ Search Console, vì dùng cùng thư viện. Không cần dòng mới.
- **Việc chưa xác minh** (Thợ Máy đã liệt kê): tài khoản dịch vụ làm người dùng Search Console, quyền «Hạn chế» đủ cho số liệu, tên trường `metadata`. Cả ba **hỏng theo hướng an toàn**: không lấy được số hay coi thêm ngày là số tạm, không mở thêm quyền. Kiểm ở lượt thử thật.
- **Không nâng quyền khi thử thật gặp lỗi 403.** Nếu quyền «Hạn chế» không đủ, phải hỏi lại chủ dự án và Lá Chắn. Không tự chọn «Toàn quyền».
- **Ghi nhận FAQ** của Thợ Máy (kết quả FAQ không còn hiện trên Google từ 05/2026) là việc SEO, không phải bảo mật; chuyển Chỉ Huy.
- **Kiểm lại bằng Fable:** thêm phần Search Console vào phạm vi lượt Fable nhóm Google, như Thợ Máy đề xuất.

## Điều kiện

| # | Việc | Ai | Hạn |
|---|---|---|---|
| 1 | Chép LC-T120-1 → -24 vào phiếu T-121 → T-127 theo cột «Phiếu» ở trên | Chỉ Huy | Khi lập phiếu code Giai đoạn 6 |

Không có điều kiện nào chặn gộp tài liệu T-120.

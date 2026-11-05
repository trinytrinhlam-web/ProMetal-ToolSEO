# T-121 · Client Google Search Console (Giai đoạn 6, đợt 1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-03 |
| Giai đoạn | Giai đoạn 6 |
| Mức ưu tiên | Cao (mở đường cho T-124) |
| Phụ thuộc | T-120 (thiết kế, đã gộp `main`) |
| Trạng thái | Xong (gộp `main` 2026-11-05) |

## Mục tiêu

Client chỉ đọc tới Google Search Console API, dùng lại tài khoản dịch vụ đang dùng cho Sheets: liệt kê thuộc tính (`sites.list`), lấy số liệu Hiệu suất (`searchanalytics.query`) theo 3 khuôn thân cố định, kiểm từng câu trả lời như dữ liệu chưa tin cậy.

## Bối cảnh

- Thiết kế T-120 mục 1.2 (kết nối thuộc tính), 2.1–2.8 (phạm vi, thư viện, đường gọi, kiểm câu trả lời, giới hạn, ngày giờ, lọc thuộc tính chính, câu lỗi), mục 6 dòng T-121.
- `CLAUDE.md` Lộ trình Giai đoạn 6; `docs/team/security.md`.

## Phạm vi

- **Được sửa:** mới: `seo_app/google/search_console.py`, `tests/test_google_search_console.py`; sửa: `seo_app/google/service_account.py` (thêm `SEARCH_CONSOLE_SCOPE`, tham số `scope` của `load_service_account`), `tests/fake_google.py` (chỉ thêm đường Search Console); `seo_app/google/sheets.py` **chỉ docstring** ghi ràng buộc lớp vận chuyển dùng chung.
- **Không được sửa:** `app/**`, `seo_app/storage/**`, `seo_app/tracking/**`, `.env.example`, `config/**`, logic trong `sheets.py`.

## Yêu cầu

1. `SEARCH_CONSOLE_SCOPE` (`webmasters.readonly`), `load_service_account` chỉ nhận 2 phạm vi cố định (2.1).
2. `SearchConsoleClient.from_settings` (kiểm thuộc tính và file khóa mỗi lần), `list_sites()`, `query(...)` theo 3 khuôn thân, `_check_call` một chỗ, lật trang, thử lại 429 tối đa 1 lần, câu lỗi cố định (2.3–2.8).
3. Kiểm câu trả lời từng dòng (2.4): `bool`, `NaN`/`Infinity` (`parse_constant`), JSON trùng khóa, `RecursionError`, tỉ lệ dòng hỏng.
4. Bộ đọc thuộc tính, kiểm «phủ website» theo từng phần tên miền (không `endswith` trần), dựng tiền tố lọc từ `WORDPRESS_URL`; từ chối `http://`, staging (1.2, 2.7).
5. Nhập lớp vận chuyển từ `sheets.py` (không sửa logic); test chứng minh từng lớp chặn được nối đúng ở client mới (3xx, thân quá cỡ, giờ chờ, `.netrc`…).
6. Sửa hàm dùng chung `load_service_account`: chạy mọi test Google (`tests/test_google_*`, `test_t100_google_identity`, `test_t101_settings_google`, `test_la_chan_t097`, `test_soi_loi_t097`) và grep test theo hành vi bị ghim.
7. Ca biên Soi Lỗi gợi ý ở T-120 mục «Đề xuất»: 25.000 dòng lật trang, `metadata` thiếu/sai tên, dòng staging khi thuộc tính tên miền, `%E1%BB%AD` hoa/thường, `#…`, `bool` thay số, `position` 0, click > hiển thị, `responseAggregationType` lạ, JSON trùng khóa, `NaN`.

## Quy tắc chung

- Không gọi Google thật hay website thật; test chỉ dùng dữ liệu giả (`tests/fake_google.py`, bộ chặn mạng của `tests/conftest.py`).
- Không thêm thư viện (thiết kế: không cần thư viện mới).
- Chủ dự án chưa trả lời 7 câu hỏi của T-120: phần nào phụ thuộc câu trả lời thì làm theo **lựa chọn khuyến nghị** và để hằng số/tên rõ ràng để đổi sau.
- Máy đang chạy nhiều agent: chỉ chạy test liên quan (kể cả test mọi nơi gọi hàm dùng chung mình sửa), `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp.

## Yêu cầu bảo mật riêng

Nguyên văn từ biên bản Lá Chắn T-120 (`docs/team/reports/T-120-la-chan.md` mục «Điều kiện theo phiếu»); thiết kế chi tiết ở `docs/team/reports/T-120-tho-may.md`.

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
| LC-T120-15 | = Đ15: test không gọi mạng; mọi ca biên ở 2.4 có test; trang mới thêm vào `PAGES` | | Mọi phiếu |
| **LC-T120-16** | **Không mạo danh, không phạm vi rộng**: không `with_subject` (ủy quyền toàn miền), không `google.auth.default()`, không phạm vi `cloud-platform` hay `webmasters` (đọc-ghi); mỗi client một đối tượng xác thực, đúng một phạm vi | Test: đối tượng xác thực của client Search Console có đúng `[webmasters.readonly]`, không có `subject` | T-121 |
| **LC-T120-17** | **Kiểm «phủ website» theo từng phần tên miền**: `sc-domain:` chỉ nhận chữ thường ASCII/`xn--`, nhãn hợp lệ, không cổng, IP, `@`, đường dẫn, dấu chấm cuối. Tên máy của website phải **bằng** tên miền hoặc **kết thúc bằng `.` + tên miền**. Không dùng `endswith(tên miền)` trần: `evilsuachuacuasat.com` sẽ lọt. Dạng tiền tố: đúng `https://<tên máy của WORDPRESS_URL>/` | Test: `sc-domain:evilsuachuacuasat.com`, `sc-domain:suachuacuasat.com.evil.com`, `sc-domain:SUACHUACUASAT.com`, `sc-domain:suachuacuasat.com.`, `sc-domain:1.2.3.4`, `https://suachuacuasat.com:8443/`, `https://suachuacuasat.com/blog/` đều bị từ chối hay xử lý đúng | T-121 |
| **LC-T120-18** | **Test chứng minh từng lớp chặn được nối đúng ở client mới**, không chỉ «có nhập»: 3xx bị từ chối, thân quá cỡ bị cắt và báo, giờ chờ truyền đúng, `.netrc` không được đọc, mã truy cập xin qua `_TokenRequest`, `repr` của phần xác thực không lộ mã | Docstring của `sheets.py` và module mới ghi chéo: sửa một bên phải chạy test cả hai | T-121 |

## Tiêu chí xong

- [ ] Yêu cầu 1–7 và mọi điều kiện LC-T120 ở trên có test
- [ ] Test liên quan + `uv run ruff check .` qua
- [ ] Báo cáo `docs/team/reports/T-121-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: đầy đủ. Lá Chắn: **đầy đủ** (đường gọi mới tới Google, phạm vi); dùng **Fable** khi có hạn mức. Ước lượng: **M–L**.

## Ghi chú của Chỉ Huy

- Lập 2026-11-03 theo thiết kế T-120 (Lá Chắn rút gọn ĐẠT, Opus tạm) và chỉ đạo «làm liên tục, không cần hỏi». Đợt 1 gồm T-121, T-122, T-123, chạy song song được (thư mục riêng). Worktree `wt-T-121`, nhánh `team/T-121`.
- 2026-11-05 12:37 (Chỉ Huy B): gộp `main` cùng đợt 1 Giai đoạn 6 (T-121, T-122, T-123); Windows 23.548 test qua, 0 hỏng. Đã đẩy. Điều kiện Lá Chắn cho phiếu sau đã chép vào T-124.

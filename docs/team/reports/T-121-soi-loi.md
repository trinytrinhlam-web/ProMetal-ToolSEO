# Báo cáo T-121 · Client Google Search Console (Giai đoạn 6, đợt 1) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-121 «Client Google Search Console» · mức kiểm **đầy đủ**, Windows · điều kiện LC-T120-1 → -8, -15 → -18. Không gọi Google thật, không đụng website, không chạy cloud |
| Ngày nộp | 2026-11-04 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15, `requests` 2.34.2, `google-auth` 2.62.0, uv 0.13.4. Máy đang chạy 4 agent và toàn bộ test của Chỉ Huy, nên chỉ chạy test liên quan |
| Mã nguồn | `team/T-121` tại `eb05747` (gốc `main` `a499a13`). Gộp thử với `main` cục bộ `33bac10` (đã có T-112) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (SL-T121-1: dòng lặp nguyên văn bị cộng dồn, nên trang lặp làm số liệu gấp bội mà không báo; không chặn Lá Chắn). Cả 7 trọng tâm Chỉ Huy giao đều đạt. 21 file test Google (gồm mọi nơi gọi `load_service_account`): 1.662 qua, 3 bỏ qua, 0 hỏng. Test mới: 158 ca (156 qua, 2 `xfail`). Thử đột biến: 81 đột biến, test của Thợ Máy bắt 67, test mới của Soi Lỗi bắt thêm 12, còn 2 sống đã xét là chấp nhận được. Gộp `main` `33bac10` không xung đột: 23 file test liên quan 1.820 qua, 3 bỏ qua, 2 `xfail`, 0 hỏng |

## Tóm tắt (cho chủ dự án)

- **Phần đọc số liệu Search Console làm đúng và an toàn.**
  - Phần mềm chỉ gửi hai loại lệnh đọc tới Google: lấy danh sách thuộc tính, lấy số liệu Hiệu suất. Mọi lệnh khác bị chặn trước khi gửi, kể cả lệnh do lập trình viên sau này lỡ viết sai.
  - Quyền xin Google là quyền **chỉ đọc**. Phần Google Sheet đang chạy không bị ảnh hưởng.
  - Thuộc tính na ná website (`evilsuachuacuasat.com`, `suachuacuasat.com.evil.com`, bản staging, `http://`, viết hoa, chữ cái tiếng Nga trông y hệt chữ «a»…) đều bị từ chối trước khi đọc file khóa.
  - Số liệu lạ từ Google (`NaN`, số khổng lồ, đúng/sai thay cho số, khóa lặp) bị bỏ, không làm sập phần mềm. Câu báo lỗi là câu tiếng Việt cố định, không chép lời Google.
- **Một lỗi nhỏ mới (Thấp), SL-T121-1:** nếu Google trả lại một dòng hai lần (trang sau lặp lại trang trước), phần mềm cộng cả hai, nên số click và lượt hiển thị bị gấp đôi mà không báo. Website hiện còn nhỏ nên gần như không gặp. Nên sửa trước khi làm trang Theo dõi (T-124).
- Vài điểm cần xem khi thử thật với Google (mục Ghi nhận): mã lỗi thật khi hết hạn mức, cỡ câu trả lời khi website lớn.

## Việc 1 · Đường gọi cố định và thân lệnh (LC-T120-2, -7) — **đạt**

- Đọc `_check_call`, `_known_body`, `_send`, `_call`. Chỉ `_call` gọi `session.request`. Trong `_send`, `_check_call` chạy trước khi xin mã và trước khi gửi. Test cây cú pháp mới khóa cả hai điều này.
- Thân lệnh được so bằng JSON đã sắp khóa với thân dựng lại của 4 khuôn, nên phải đủ khóa và đủ giá trị.
- Thử thêm 21 thân sai kiểu, ngoài 40 ca của Thợ Máy. Tất cả bị chặn, không lệnh nào ra mạng:

  | Nhóm | Ca |
  |---|---|
  | Kiểu đúng/sai | `startRow`/`rowLimit` = `true` |
  | Chữ hoa, giá trị lạ | `type` `WEB`/`discover`/`news`, `dataState` `ALL`, `aggregationType` `BYPAGE`, thêm chiều `device` |
  | Ngày | là `date`, có giờ, có khoảng trắng, chữ số toàn khoảng |
  | Bộ lọc | dấu chấm không thoát, thiếu `/` cuối, thiếu `^`, `excludingRegex`, `equals`, `NaN`, lớp con `str` nói dối khi so |
  | Khóa | khóa số, khóa số thay khóa chữ |

- Ba kiểu khác mà nội dung JSON y hệt khuôn (`OrderedDict` đảo thứ tự, `tuple`, lớp con `str` có `__eq__` luôn đúng và `__str__` = `evil`) được gửi. Đã kiểm thân **gửi đi** đúng y khuôn, nên không lọt được nội dung khác. `Decimal`, lớp con `int` bị chặn (đúng như Thợ Máy ghi).
- Đường gọi: thử 11 biến thể của `sites` và 4 phương thức khác cho `query`, đều bị chặn:
  - `get` chữ thường, `HEAD`, `OPTIONS`, `/` cuối, `:443`, tên máy viết hoa;
  - `www.googleapis.com@evil.example`, `www.googleapis.com.evil.example`;
  - `sites/{id}` (GET, tức `sites.get`), `sitemaps`, địa chỉ xin mã;
  - `query` với `PUT`, `DELETE`, `GET`, `post`.

## Việc 2 · Thuộc tính theo từng phần tên miền (LC-T120-6, -17) — **đạt**

- Bảy ca phiếu ghi, cùng 16 biến thể, chạy qua `from_settings` với file khóa **không có**: mọi ca bị từ chối bằng câu cố định trước khi đọc file, không lệnh mạng nào. Câu báo không có tên miền, `evil`, `staging-m`.

  | Ca | Kết quả |
  |---|---|
  | `sc-domain:evilsuachuacuasat.com`, `…com.evil.com`, `staging-m.…`, `com.suachuacuasat`, `cuasat.com`, `com.vn`, `https://www.suachuacuasat.com/` | «không phải của website» |
  | `sc-domain:SUACHUACUASAT.com`, `…com.`, `1.2.3.4`, `https://…:8443/`, `https://…/blog/` | «sai dạng» |
  | chữ `а` Kirin, dấu chấm `。` (IDNA coi là «.»), dấu chấm toàn khoảng `．`, `%2E`, `https://…com./`, `https://…com//`, `127.0.0.1`, `[::1]`, `a:b@`, tab, ký tự `NUL` | «sai dạng» |

- Bảy thuộc tính đúng dạng mà không phủ website cũng bị client từ chối khi truyền thẳng (không qua `from_settings`).
- So tên máy của `WORDPRESS_URL`:
  - thuộc tính tên miền phủ tên miền con `blog.suachuacuasat.com`;
  - không phủ `xsuachuacuasat.com`, `suachuacuasat.co`;
  - `WORDPRESS_URL` có dấu chấm cuối thì không dùng được.
- `WORDPRESS_URL` viết hoa (`https://SuaChuaCuaSat.com`, `HTTPS://…`, `…COM:443`): bộ lọc gửi Google viết thường, dòng của Google vẫn được nhận. Ở lõi T-123 cùng tình huống này là lỗi SL-T123-2 (theo ghi chú của phiên Soi Lỗi T-123). Client T-121 không mắc.
- «Tìm thuộc tính» (`sites.list`):
  - `siteUrl` có ký tự điều khiển, vô hình, đảo chiều chữ, khoảng trắng: bỏ mục (8 ca);
  - chữ ASCII không đúng dạng (`[x](https://…)`, `<b>…</b>`): không bao giờ «chọn được» (xem GN-5).

## Việc 3 · Kiểm câu trả lời (LC-T120-5) — **đạt**

- **`NaN` chặn ngay ở bộ đọc JSON.** Ca của Thợ Máy chỉ có câu trả lời một dòng. Khi đó bỏ dòng `NaN` cũng là 100% dòng hỏng, nên ca vẫn qua dù bỏ `parse_constant` (đột biến M44 sống với test Thợ Máy). Ca mới đặt **một** dòng `NaN` giữa 20 dòng đúng (≈ 5%, dưới ngưỡng 10%) ở 5 chỗ: click, hiển thị, vị trí, `ctr`, trường lạ. Thêm một ca `NaN` trong `metadata`. Cả câu trả lời đều bị bỏ.
- **Số khổng lồ:** số nguyên 401 chữ số (`float()` của nó ném `OverflowError`) và `1e400`/`-1e400` (JSON đọc thành `inf`, `parse_constant` không thấy), ở click, hiển thị, vị trí, `ctr`. Chỉ bỏ dòng đó và đếm, không sập. Bỏ phép kiểm `±2^53` thì phần mềm sập (đột biến M22).
- Số thực rất dài (8 MB chữ số): đọc trong 0,02 giây, không treo.
- JSON trùng khóa trong `metadata`: bỏ cả câu trả lời.
- Ngày lạ trong dòng (xuống dòng cuối, chữ số toàn khoảng, chữ `O` thay số `0`, `+`, `Z`): bỏ dòng.
- Địa chỉ quá 2.000 ký tự nhờ phần `#…` dài: bỏ dòng (phép đo tính trên chữ Google trả, trước khi bỏ `#`).
- `bool`, vị trí 0, click > hiển thị, `responseAggregationType` lạ, tỉ lệ 10% đúng biên: test của Thợ Máy đủ, đột biến đều bị bắt.
- `-0.0`, `2.0`, `1e-400` đọc thành số nguyên.

## Việc 4 · Lật trang ở 25.000 dòng — **đạt, kèm SL-T121-1**

- Test Thợ Máy có ba ca: đúng 25.000 dòng thì lật trang, trang sau rỗng thì dừng, Q2 dừng ở trần 10 trang.
- Ca mới:
  - Q1 trả đủ 25.000 dòng mọi trang: dừng ở trang thứ 8 (`startRow` 175.000), `truncated`, 200.000 dòng, không gửi lệnh thứ 9;
  - 429 ở trang 2: thử lại một lần rồi lấy tiếp (`startRow` 0, 5.000, 5.000);
  - trang 2 không có `metadata`: không xóa ngày đầu tiên còn số tạm đọc ở trang 1;
  - trang 2 lỗi 500: báo lỗi, không trả kết quả nửa vời (T-124 lấy lại đoạn đó);
  - trang 2 có 5.001 dòng: bỏ cả lần lấy.
- **SL-T121-1:** trang sau lặp lại trang trước thì số liệu bị cộng gấp đôi (mục Lỗi mới).

## Việc 5 · 429 thử lại một lần, trần số lệnh (LC-T120-8) — **đạt**

- `query` (test Thợ Máy) và `sites` (ca mới): 429 rồi thành công thì đúng 2 lệnh, chờ 1 lần; 429 hai lần thì báo «đợi 15 phút», đúng 2 lệnh.
- 500, 502, 503, 504: **không** thử lại (1 lệnh, không chờ). Ca của Thợ Máy không đếm số lệnh, nên đột biến «thử lại cả 5xx» sống với test Thợ Máy (M13).
- Trần 1 lệnh gặp 429: không gửi lệnh thứ hai, báo «Đã gửi đủ 1 lệnh». Thử lại cũng tính vào trần.
- 429 kèm `Retry-After: 86400`: vẫn chỉ chờ 2–2,5 giây.
- Lệnh xin mã: xem GN-1.

## Việc 6 · Lớp vận chuyển nhập từ `sheets.py` (LC-T120-3, -18) — **đạt**

- `search_console._TokenRequest is sheets._TokenRequest`. Các lớp `_Bearer`, `_refuse_redirect`, `_read_limited` cũng nhập, không chép. Docstring hai module ghi chéo «sửa một bên chạy test cả hai». `sheets.py` chỉ đổi docstring (đã xem diff).
- Ca mới cho từng lớp:
  - **3xx ở lệnh POST `query`** (301, 302, 303, 307, 308; 307 và 308 giữ thân khi đi theo): không đọc thân (đếm lần đọc = 0), không gửi lại thân, không gọi tới `Location`. Chỉ một lệnh Search Console. Ca của Thợ Máy chỉ thử `GET sites`.
  - **`.netrc` thật** (biến `NETRC`, file có mật khẩu cho cả `www.googleapis.com` lẫn `oauth2.googleapis.com`; đối chứng: `requests` đọc được file này): không lệnh nào mang `Authorization: Basic`, lệnh Search Console chỉ mang `Bearer`.
  - **Giờ chờ** 7 s, 0,5 s truyền đúng cho cả lệnh xin mã lẫn lệnh Search Console. 0, âm, `NaN`, vô cùng thành 30 s.
  - **Cỡ câu trả lời:** `sites` đúng 256 KB thì nhận, thêm 1 byte thì bỏ; `Content-Length` khai 1 TB thì bỏ trước khi đọc.
- Đột biến M01 → M08, M64 đều bị test Thợ Máy bắt: bỏ móc 3xx, bỏ giờ chờ, `stream=False`, mã gắn vào header trần (`.netrc` đè), bỏ `max_redirects`, xin mã qua phiên khác, giới hạn `sites` thành 8 MB, bỏ kiểm dạng mã.

## Việc 7 · `load_service_account` (hàm dùng chung), phạm vi (LC-T120-1, -16) — **đạt**

- Chạy 21 file test Google: `test_google_*`, `test_la_chan_t097/t100/t101/t113`, `test_plan_sync`, `test_soi_loi_t097/t100/t101/t109/t113`, `test_t100_google_identity`, `test_t101_home_page/plan_page/settings_google`, `test_t102_formula_cells/publish`, `test_t109/t113_website_status`. Đây là mọi file nhập `fake_google`, `fake_plan_sheet` hay `seo_app.google`.
- Kết quả: **1.662 qua, 3 bỏ qua** (có từ trước: hai ca symlink vì máy chưa bật Developer Mode, một ca quyền kiểu chmod), 0 hỏng.
- Grep nơi gọi:
  - ba nơi gọi cũ (`app/views/plan.py:336`, `app/views/settings.py:585`, `seo_app/google/sheets.py:632`) không truyền `scope`, nên vẫn phạm vi Sheets;
  - `scope` là tham số chỉ-tên, không lệch vị trí.
- Grep test ghim hành vi:
  - `test_google_service_account.py:79` và `test_google_sheets.py:324` ghim phạm vi Sheets mặc định, vẫn qua;
  - test cây cú pháp của `test_google_service_account.py` quét mọi file `seo_app/google/*.py` (nay có `search_console.py`), vẫn qua;
  - không test nào vá `_credentials` hay ghim chữ ký hàm.
- Không có chỗ nào lấy phạm vi từ `.env`, `config/`, `app/`.
- Ca mới:
  - phạm vi lớp con `str`, `http://`, `/` cuối, phạm vi đọc-ghi, tên ngắn, `frozenset`: bị từ chối **trước** khi đọc file;
  - hai tài khoản nạp từ cùng file khóa: tài khoản Sheets không bị đổi phạm vi, lệnh xin mã của client Search Console ký đúng `webmasters.readonly`;
  - đối tượng xác thực có `webmasters.readonly` **kèm** phạm vi khác (Sheets, đọc-ghi `webmasters`, `cloud-platform`, hay lặp hai lần): client từ chối, không gửi lệnh nào. Test của Thợ Máy chỉ thử tài khoản thiếu hẳn phạm vi chỉ đọc, nên đột biến «chỉ cần có phạm vi chỉ đọc trong danh sách» (M40) lọt.

## Việc 8 · Câu lỗi (LC-T120-4), R5, phạm vi sửa, gộp thử — **đạt**

- Câu lỗi:
  - mọi ca mới đều kiểm câu báo không có lời Google, mã truy cập, email, tên miền, `evil`, và `__cause__` rỗng;
  - `_MSG_NETWORK` chỉ chèn tên lớp lỗi; `_MSG_TIMEOUT` chỉ chèn số giây.
- R5 và phạm vi sửa:
  - diff chỉ có 6 file đúng phạm vi phiếu;
  - `fake_google.py` chỉ thêm (2 hằng, 1 hàm, docstring);
  - không test cũ nào bị xóa hay nới.
- Gộp thử với `main` `33bac10` (worktree tạm, không đẩy):
  - `git merge-tree` không xung đột;
  - `main` từ `a499a13` chỉ thêm T-112, không đụng `seo_app/google/`, `fake_google.py`, `conftest.py`.
  - Chạy 23 file trên bản gộp (21 file Google, `test_soi_loi_t121.py`, `test_t112_settings_switch.py` vì T-112 sửa trang Cài đặt có phần Google): **1.820 qua, 3 bỏ qua, 2 `xfail`** (SL-T121-1), 0 hỏng. Đã kiểm `seo_app` nạp từ bản gộp.
  - Worktree tạm đã gỡ.

## Thử đột biến (`sl121_mutate.py`)

- 81 đột biến: 75 ở `search_console.py`, 6 ở `service_account.py`.
- Cách chạy:
  - tất cả dùng chung một bản sao `git archive` của `eb05747`, chạy với `PYTHONDONTWRITEBYTECODE=1`;
  - mỗi đột biến chạy test của Thợ Máy trước (`-x`); đột biến ở `service_account.py` chạy thêm `test_google_service_account.py`, `test_google_sheets.py`;
  - sống thì chạy test của Soi Lỗi.
- Đối chứng không đổi: 309 qua (Thợ Máy); test Soi Lỗi 148 qua + 2 `xfail` ở lượt chính, 156 qua + 2 `xfail` ở lượt chạy lại sau khi thêm ca. `seo_app` nạp từ bản sao.

| Kết quả | Số | Đột biến |
|---|---|---|
| Test Thợ Máy bắt | 67 | lớp vận chuyển (M01–M08, M64); đường gọi, thân (M09–M11, M61–M63, M65, M68, M72–M74); 429 và trần lệnh (M12, M14, M15, M59, M60); lật trang (M17, M18, M75); JSON, dòng (M45–M47, M49, M19, M76, M21, M23–M30, M32, M50, M66, M67, M71); câu lỗi (M69); thuộc tính (M33–M39, M41–M43); «Kiểm tra», «Tìm thuộc tính» (M54–M56, M58); `service_account.py` (S1, S2, S4, S5) |
| Chỉ test Soi Lỗi bắt | 12 | M13 thử lại cả 5xx; M16 đọc `metadata` ở mọi trang; M22 bỏ kiểm `±2^53` (sập `OverflowError`); M31 bỏ đo độ dài trước khi bỏ `#`; M40 chỉ cần «có» phạm vi chỉ đọc; M44 bỏ `parse_constant`; M48 bỏ trần `rowLimit`; M51 «Kiểm tra» không báo `truncated`; M52 «Kiểm tra» bỏ tỉ lệ 10%; M53 «Kiểm tra» bỏ đo độ dài; M57 `siteUrl` bỏ kiểm ký tự in được; S3 phạm vi nhận lớp con `str` |
| Sống cả hai, chấp nhận | 2 | M70 bỏ lọc ASCII mã lý do: tương đương, vì mã lý do chỉ để so với tập cố định, không bao giờ hiện. S6 bỏ phép kiểm lại phạm vi trong `_credentials`: phép kiểm phòng xa, vì `_credentials` chỉ được gọi sau phép kiểm đầu hàm `load_service_account` (S4 bị bắt). |

- M16 và M40 sống ở lượt đầu. Đã thêm `test_metadata_trang_dau_khong_bi_trang_sau_xoa` và `test_client_tu_choi_tai_khoan_co_them_pham_vi`, chạy lại thì bị bắt. M70, S6 chạy lại với bộ test cuối: vẫn sống (309 qua; 156 qua + 2 `xfail`), đúng như đã xét.
- Hai ca của Thợ Máy qua vì lý do khác, không phải nhờ phép kiểm đang thử:
  - `test_json_la_bi_bo_ca_cau_tra_loi` (`nan`, `infinity`…): câu trả lời chỉ có một dòng, nên bỏ dòng `NaN` cũng là 100% dòng hỏng;
  - `test_rows_sai_khuon_bo_ca_cau_tra_loi` (201 dòng cho khuôn 200 dòng): dòng có 2 khóa cho khuôn 1 chiều, nên cả 201 dòng đều hỏng.
  - Không cần sửa, vì ca của Soi Lỗi đã khóa đúng phép kiểm (M44, M48).

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T121-1** | Thấp | `_merge` cộng mọi dòng cùng (ngày, trang, từ khóa). Thiết kế 1.4 và docstring muốn thế cho các dòng **chỉ khác `#…`**, nhưng dòng **lặp nguyên văn** cũng bị cộng. Google không bao giờ trả hai dòng cùng khóa trong một kết quả, nên dòng lặp là dữ liệu lạ. Hai tình huống làm số liệu sai mà không báo. (1) Google lặp trang (bỏ qua `startRow`): test của Thợ Máy `test_tran_so_dong_thi_dung_va_bao_co_the_thieu` đang ghim đúng hành vi này. 10 trang giống hệt cho 100 lượt hiển thị thay cho 10, kèm `truncated` («có thể thiếu dòng»), trong khi thật ra số bị gấp 10. (2) Số liệu `dataState = all` (Q1) đổi giữa hai lệnh lật trang: một dòng nằm ở cả hai trang thì bị cộng đôi, và một dòng khác bị sót. Website hiện nhỏ nên Q1 khó chạm 25.000 dòng; Q2 (5.000 dòng mỗi trang, 93 ngày) sẽ lật trang khi website lớn lên | `tests/test_soi_loi_t121.py::test_sl_t121_1_dong_trung_nguyen_van_trong_mot_cau_tra_loi_khong_cong_don`, `::test_sl_t121_1_trang_sau_lap_lai_trang_truoc_khong_cong_gap_doi` (2 ca, `xfail(strict=True)`; `--runxfail`: hỏng đúng lý do, 20 lượt hiển thị thay cho 10). Hai ca nhận cả hai cách sửa: bỏ dòng lặp (đếm `dropped`) hay bỏ cả câu trả lời |

Gợi ý sửa:
- Trong `_fetch`, nhớ khóa **thô** đã gặp trong lần lấy (bộ `keys` nguyên văn, trước khi bỏ `#`).
- Gặp lại thì bỏ dòng và tính vào `dropped`. Quy tắc 10% có sẵn sẽ bỏ cả lần lấy khi cả trang bị lặp.
- Khi sửa phải viết lại hai dòng cuối của `test_tran_so_dong_thi_dung_va_bao_co_the_thieu`, cho mỗi trang dòng riêng (R5: Chỉ Huy duyệt).
- Không chặn Lá Chắn. Nên sửa trước T-124.

## Ghi nhận

- **GN-1 · Lệnh xin mã tự thử lại 3 lần.**
  - Máy chủ mã (`oauth2.googleapis.com`) trả 429, 500, 503, 504 hay 408 thì thư viện `google-auth` tự thử lại: tổng 3 lệnh xin mã, chờ thật khoảng 1 rồi 2 giây. Đây là `time.sleep` của thư viện, không qua `sleep` của client.
  - Đo trên Google giả: 3 lệnh xin mã, 0 lệnh Search Console, khoảng 3 giây, câu cố định «Không lấy được mã truy cập…».
  - Lệnh xin mã không tính vào trần 20 lệnh. Có từ T-097 (client Sheets dùng chung `_TokenRequest`). LC-T120-8 nói về lệnh Search Console nên không trái. Ghi để T-124 biết thời gian chờ tối đa.
- **GN-2 · 403 vì hạn mức.**
  - Thiết kế (theo tài liệu Google) ghi quá hạn mức là 429.
  - Nếu lượt thử thật gặp 403 kèm mã lý do hạn mức (`rateLimitExceeded`, `userRateLimitExceeded`, `dailyLimitExceeded`, `quotaExceeded`), câu hiện ra sẽ là «chưa có quyền xem thuộc tính… thêm email…», hướng người dùng đi sai.
  - Khi đó thêm các mã này vào danh sách đọc (như `accessNotConfigured`), với câu «đợi 15 phút».
- **GN-3 · Cỡ câu trả lời Q1 khi website lớn.**
  - Google mặc định trả JSON có thụt lề. Tôi ước 200–290 byte mỗi dòng Q1, tức 5–7 MB cho trang 25.000 dòng, dưới trần 8 MB.
  - Website rất lớn (đường dẫn dài) có thể chạm trần. Khi đó phần mềm báo «lớn bất thường… khoảng ngày ngắn hơn», tức hỏng theo hướng an toàn. Website hiện tại không chạm.
  - Lượt thử thật có thể đo cỡ thật.
- **GN-4 · Tỉ lệ 10% tính theo từng lần gọi** (đúng thiết kế 2.4).
  - Lần gọi ít dòng (Q1 cho 1–2 ngày gần nhất, ≤ 9 dòng) chỉ cần một địa chỉ Google trả mà `is_site_link` từ chối (ví dụ có dấu `'`) là bỏ cả lần gọi. Bấm lại vẫn vậy, cho tới khi địa chỉ đó hết trong Search Console.
  - Chưa rõ Google có trả địa chỉ như thế không. Đề nghị lượt thử thật xem `dropped`.
  - Nếu gặp, T-124 nên báo «có dòng lạ» thay cho «thử lại sau».
- **GN-5 · «Tìm thuộc tính» giữ mục không đúng dạng.**
  - `list_sites` giữ `siteUrl` không đọc được (`http://`, đường con, chữ ASCII lạ như `[x](https://…)`) với `kind=""`, `usable=False`, để hiện «không dùng được». Thiết kế 2.4 ghi «Bỏ mục».
  - Cách của Thợ Máy hợp lý cho người dùng: thấy vì sao thuộc tính `http://` không chọn được.
  - T-124 phải hiện `site_url` bằng chữ thuần, như docstring `SiteEntry` đã ghi (LC-T120-11, -19). Test của tôi chỉ đòi «không bao giờ chọn được», không ghim giữ hay bỏ.
- **GN-6 · «Kiểm tra» hiện tên máy trùng website.**
  - Trang `http://suachuacuasat.com/…`, hay trang `https` có ký tự lạ, được đếm «ngoài website» với tên máy `suachuacuasat.com`. Test của Thợ Máy ghim ca `http://`.
  - T-124 nên ghi thêm «(địa chỉ http:// hoặc lạ)» khi tên máy trùng website, kẻo người dùng khó hiểu.
- **GN-7 · `_known_body` không bắt `RecursionError`.** Thân lồng sâu khoảng 200.000 tầng làm lọt lỗi Python thay vì câu cố định. Chỉ code trong app dựng thân, không có đường nhập từ ngoài, nên vô hại; ghi để biết.

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t121.py`, 42 hàm, 158 ca: 156 qua, 2 `xfail(strict=True)` SL-T121-1. Tham số dài đều có `ids` ngắn.
  - Chạy: `uv run pytest tests/test_soi_loi_t121.py -rxX`.
  - Kiểm hai ca `xfail`: thêm `--runxfail -k sl_t121_1`.
- Script (thư mục ghi chú chung, `T-121-soi-loi-scripts/`): `sl121_mutate.py`, thử đột biến trên bản sao `git archive`, một bản sao cho mọi đột biến, `PYTHONDONTWRITEBYTECODE=1`. Chạy từ worktree: `.venv/Scripts/python.exe -X utf8 sl121_mutate.py [tên…]`.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện.

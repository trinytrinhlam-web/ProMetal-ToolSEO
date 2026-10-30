# Báo cáo T-100 · Đồng bộ kế hoạch với Google Sheets, cache, nối nháp với dòng kế hoạch · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-100](../tickets/T-100-dong-bo-ke-hoach-cache-nhap.md), Thợ Máy đầu nhánh `04febcc` (gốc `main` `b241e79`); phạm vi gồm cả SL-T097-5 và G2 / LC-T103-1 |
| Ngày nộp | 2026-10-29 (00:59 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T100-1 → -3, đều là cảnh báo giá **oan** của G2: không mất dữ liệu, không ghi sai Sheet, người dùng vẫn tick được). Đồng bộ Sheet, cache, kho nháp, SL-T097-5: **không lỗi**. R5: 9 dòng test đổi đúng điều kiện Chỉ Huy duyệt. Điều kiện: Chỉ Huy chọn sửa 3 lỗi Thấp ngay (lượt 2 ngắn) hay ghi nhận để sau; không chặn Lá Chắn |
| **Kết luận lượt 2** (đầu nhánh `57bac59`, 2026-10-30) | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T100-1 → -3, G1 đóng; LC-T100-1 → -3 sửa đúng hướng, không phá đồng bộ, kho nháp, khóa gửi trùng; R5 đúng. **8 Thấp mới** (SL-T100-4 → -11: 2 ở phần Sheet, 6 ở hàm dò giá mới, trong đó 3 hồi quy). Chi tiết: mục [«Lượt 2»](#lượt-2-2026-10-30-0916-0700--soát-lượt-sửa-của-thợ-máy-57bac59) |

## Tóm tắt (cho chủ dự án)

- **Đồng bộ với Google Sheets an toàn.** Tôi thử mất mạng đúng lúc đang thêm dòng (Google đã thêm xong nhưng phần mềm không nhận được trả lời), hai máy cùng sửa một ô, duyệt trên bản lưu cũ, bản lưu bị sửa tay. Không lần nào phần mềm **thêm dòng trùng** hay **ghi đè** ô người khác vừa sửa: dòng nào đã khác thì phần mềm dừng, hiện «trước / bây giờ / đề xuất» để anh/chị xem.
- **Mọi ô ghi lên Sheet ở dạng giữ nguyên** (Google không biến chữ thành công thức); chữ bắt đầu bằng «=», «+», «-», «@» được thêm một dấu cách đầu để file tải về mở bằng Excel không chạy công thức.
- **Bản lưu tạm kế hoạch** (để mở trang nhanh, xem khi mất mạng) hỏng, bị chương trình khác giữ, chỉ đọc, hay bị thay bằng thư mục: trang vẫn hiện kế hoạch đọc từ Google kèm một câu báo; không xóa nhầm file.
- **Nháp cũ** (trước T-100) mở được, giữ ảnh đã chọn, giữ dấu «ảnh đã duyệt», giữ trạng thái «đã gửi»; lưu lại thì lên khuôn mới. Nút «Gửi nháp» (hai tab cùng gửi, mất mạng giữa chừng, gửi dở, ảnh bị thay) qua đủ các bài thử cũ.
- **Cảnh báo giá** trong đề xuất của AI bắt đúng các kiểu giá («150.000đ», «1,5 triệu», «500k», «bảng giá», «trọn gói»…); năm, kích thước, số nhà thường không bị cảnh báo. **Còn 3 lỗi nhỏ**: địa chỉ viết tắt kiểu Google Maps («45 Đ. Số 7»), số đếm có «nghìn», «triệu» («hơn 2 nghìn công trình»), ghi chú rất dài (trên 900 ký tự) bị cảnh báo giá oan. Chỉ là cảnh báo thừa (dòng đó không được tick sẵn), không mất gì.
- File khóa Google: lỗi cũ (đường có «..» bị chặn oan) đã sửa đúng; các đường vòng qua lối tắt thư mục vẫn bị chặn đúng.
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t100.py` | Mới: **73 ca: 63 qua, 10 `xfail(strict=True)`** của 3 lỗi mới. Không gọi Google, WordPress, AI thật (Sheet giả trên `FakeGoogle`, file SQLite thật trong thư mục tạm) |
| `docs/team/reports/T-100-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác.

## Kiểm từng mục

### 1. Đồng bộ: «chưa rõ» không thêm trùng, xung đột, `RAW`

Cách kiểm: Sheet giả **có trạng thái** (`tests/fake_plan_sheet.py`) đi qua `SheetsClient` thật (đường cố định, kiểm thân lệnh trước khi gửi); gài lỗi kiểu «Google làm xong rồi câu trả lời mới hỏng» (`apply=True`): mất mạng, hết giờ, mã 503.

| Tình huống | Kết quả |
|---|---|
| Thêm 3 dòng; lệnh thêm **thứ hai** đứt mạng sau khi Google đã thêm | Dòng 1, 2 «đã ghi» (dòng 2 xác nhận bằng đọc lại), dòng 3 «chưa ghi» (không gửi). Bấm lại với đúng bản đã xem: dòng 1, 2 là xung đột «đã có», chỉ thêm dòng 3. Mỗi Mã bài đúng **một** dòng |
| Lệnh thêm trả **503** sau khi Google đã thêm | Coi là «chưa rõ» (không phải «chưa ghi»), đọc lại thấy Mã bài → «đã ghi»; câu báo có mã 503, không chép lời máy chủ; bấm lại: xung đột, không thêm lần hai |
| Lệnh thêm **hết giờ**, đọc lại cũng lỗi | «Chưa rõ», câu báo bảo bấm «Tải lại»; tải lại rồi so lại **cùng file kế hoạch**: không còn đề xuất «Thêm» nào, Sheet có đúng một dòng |
| Đường AI («them», Mã bài do code cấp): đứt mạng, đọc lại lỗi, bấm áp dụng lại với bản cũ | Xung đột «đã có», không thêm lần hai |
| Ghi ô không rõ kết quả (thật ra đã ghi), rồi **máy khác sửa đúng ô đó**, bấm lại | Xung đột (bản «bây giờ» là giá trị của máy kia), ô của máy kia giữ nguyên, không có lệnh ghi thứ hai |
| Máy khác đã ghi **đúng giá trị** đề xuất | Tính là đã ghi, không gửi lệnh ghi |
| Giữa lúc xem và lúc áp dụng, người dùng **kéo đổi chỗ cột** «Ưu tiên» với «Ghi chú của thợ», chèn một cột riêng ở đầu, máy khác sửa ghi chú | Ghi đúng ô theo tên cột của bản vừa đọc; ghi chú (cột khác) và cột riêng giữ nguyên, không xung đột; dòng mới thêm để trống cột riêng |
| Duyệt trên **bản lưu** (cache còn mới); sau lúc lưu, máy khác đổi ô | Xung đột, Sheet giữ ô của máy kia |
| Cache **bị sửa tay** (từ khóa B-001 khác Sheet, mã băm tính lại cho khớp) | Không ghi được gì (ô Từ khóa khác bản gốc): cache sửa tay không lái được lệnh ghi sang dòng khác |
| Ô vừa sửa ở nơi khác chứa chuỗi mồi | Câu báo, lý do, nhãn xung đột không có chuỗi mồi (LC-T094-2); bản «bây giờ» có chữ để hiện trong bảng (T-101 hiện bằng chữ thuần) |
| **Mọi** lệnh ghi qua client thật: ghi ô, thêm dòng, ghi trạng thái, «Chuẩn bị trang tính» | Không lệnh nào có `USER_ENTERED` (cả đường lẫn thân lệnh); ghi ô `RAW`; thêm dòng `valueInputOption=RAW`, `insertDataOption=INSERT_ROWS` (chèn dòng, không ghi đè) |
| Chữ dạng công thức `=HYPERLINK("http://x")`, `+84 909 …`, `-giảm giá`, `@thợ Hùng` ở Từ khóa, Ghi chú, Tiêu đề dự kiến (thêm dòng và sửa dòng) | Trên Sheet có **một dấu cách đầu**; đọc lại thì `PlanRow` bỏ dấu cách, đề xuất tiếp trên dòng đó không sinh xung đột giả; ghi không rõ kết quả rồi bấm lại: tính là đã ghi. Tab, CR, dấu cách, U+00A0, U+200B, U+FEFF đứng trước «=», «@»: `clean_text` bỏ trước, rồi vẫn được thêm dấu cách |

**Ghi trạng thái sau khi gửi (LC-T094-30):**

| Tình huống | Kết quả |
|---|---|
| Lệnh ghi trạng thái đứt sau khi Google đã ghi | «Chưa rõ», việc còn nợ lưu ở `drafts.sqlite`; lần thử lại đọc Sheet, thấy đã đúng → bỏ việc, **không ghi lần hai**; chỉ gọi Sheets (module `sync` không có đường tới WordPress, test canh của Thợ Máy) |
| Mất mạng lúc gửi xong (chưa kết nối) rồi dòng bị đổi: «Đã đăng» (máy khác đi tiếp), Mã bài WordPress khác (bài khác gắn vào), «Bỏ», chữ lạ | Thử lại không ghi ô nào, bỏ việc còn nợ, trạng thái trên Sheet giữ nguyên (không bao giờ lùi) |
| Ô Trạng thái gõ khác («Da gui nhap», «ĐÃ GỬI NHÁP», dấu cách thừa), ô Mã bài WordPress là chữ «501» | Nhận là đã đúng, không ghi |
| «Viết bài» trên dòng có ô Trạng thái **trống** (dòng gõ tay, hay gặp nhất) | `open_row` đọc lại Sheet, `plan_ref` dựng được (trạng thái «Chưa viết») |

**Cache hỏng, cũ, bị khóa (LC-T094-29):**

| Tình huống | Kết quả |
|---|---|
| Chương trình khác giữ **khóa ghi độc quyền** (`BEGIN EXCLUSIVE`) | Trang có kế hoạch vừa đọc từ Sheet, câu báo «… đang bận. Thử lại sau giây lát.»; file **không bị xóa** (`reset_count` 0); nhả khóa thì lần sau ghi cache bình thường. Trang chờ khoảng 3,6 giây (đọc cache chờ 1,8 giây, ghi cache chờ 1,8 giây trên máy Windows này): chấp nhận được với ca hiếm |
| File hỏng **ở giữa** (một trang dữ liệu 4 KB bị ghi đè) | `quick_check` bắt được, bỏ file, đọc lại Sheet, không câu báo thừa |
| File **chỉ đọc** (Windows) | Trang vẫn có kế hoạch đọc từ Sheet, câu báo cố định |
| **Thư mục** chiếm tên file cache | Trang vẫn có kế hoạch, câu báo; thư mục không bị xóa |
| Cache cũ, Google lỗi 500 có chuỗi mồi | Hiện bản lưu, «Đang hiện bản lưu lúc 01:05 29/10/2026» (giờ Việt Nam), không chuỗi mồi |

Thợ Máy đã có: cache của Sheet khác không dùng, cache cũ/«ở tương lai» thì tải lại, trigger không chạy, file không phải SQLite, cấu trúc lạ, dòng sai khuôn → bỏ cả cache; tôi đọc và chạy: đúng.

### 2. Kho nháp: khuôn 1, 2, 3; `plan`, `SendState` mới với luồng gửi T-086, T-089

- Test của Thợ Máy (`tests/test_t100_drafts_plan.py`) đã phủ: khuôn 3 có `plan` và ảnh; khuôn 2 giữ ảnh; file nháp tạo trước T-100 (chưa có bảng `plan_writes`), khuôn 1 và 2 đã gửi: mở được, giữ ảnh, giữ trạng thái gửi, lưu lại lên khuôn 3 mà mọi trường cũ còn nguyên; khuôn ≥ 4 lạ; `plan` hỏng trong file thì bỏ phần đó, bài vẫn mở; `SendState` dòng cũ đọc với giá trị mặc định, dòng mâu thuẫn là lỗi; so-rồi-đặt thấy trường mới. Tôi đọc và chạy: đúng.
- Tôi thêm 3 ca:
  - Nháp khuôn 2 có **băm ảnh đã duyệt** (`approved_sha256`, T-089): test của Thợ Máy dùng ảnh không có băm (trường rỗng không ghi ra JSON) nên chưa phủ. Kết quả: mở bằng app mới giữ băm, lưu lại lên khuôn 3 vẫn có băm (không bắt duyệt lại ảnh oan, không mất chốt chặn ảnh bị thay).
  - Dòng trạng thái gửi do **app cũ** ghi (3 trường): bấm gửi lại bằng app mới, so-rồi-đặt «đang gửi» (T-089) vẫn qua; tab thứ hai cầm bản cũ thì không qua.
  - Nháp gắn dòng kế hoạch **tự lưu nhiều lần**: không mất `plan`, không đụng trạng thái gửi; `find_plan_draft` vẫn tìm ra, Sheet khác thì không.
- Luồng gửi thật trên giao diện (AppTest: hai tab, ngắt giữa chừng, gửi dở, băm ảnh, mã bài lạ): `test_t086_send_state.py`, `test_t089_send_draft.py`, `test_soi_loi_t086.py`, `test_soi_loi_t089.py`, `test_la_chan_t086.py`, `test_storage_send_state.py`, `test_app_drafts.py`, `test_app_images.py`, `test_app_pages.py` **đều qua** trên nhánh và trên bản gộp (mục 5).

### 3. SL-T097-5 và G2

**SL-T097-5** (`_inside_by_identity` đi theo đường thật): đúng ý.

| Đường gõ tới file khóa | Kết quả |
|---|---|
| `<dự án>/../ngoai/…`, `<thư mục ảnh>/../…`, `<dự án>/con/../../…` (test cũ của Soi Lỗi T-097, gỡ `xfail`) | Nhận (file ở ngoài) |
| `<ngoài>/../du-an/bi-mat/k.json` (đi ra rồi vòng vào dự án) | Chặn |
| Junction ở ngoài trỏ **vào** dự án | Chặn (danh tính theo đường thật) |
| Junction **trong** dự án trỏ ra ngoài | Vẫn chặn như trước T-100 (phép so chuỗi theo đường gõ); gõ thẳng đường thật ở ngoài thì nhận |
| Hai chữ ổ khác nhau cùng số thư mục (Google Drive for Desktop) | Không tin danh tính (test của Thợ Máy) |

**G2 / LC-T103-1** (cảnh báo giá trong chữ AI đưa vào dòng kế hoạch):

- 5 ca `xfail` LC-T103-1 của Lá Chắn (trên `team/T-103`, chưa vào nhánh này) chạy với code T-100 bằng `--runxfail`: **5/5 qua**, test canh «giá cũ trong ghi chú AI không đổi thì không cảnh báo» qua. Khi gộp T-103 phải gỡ 5 dấu `xfail` đó (nếu không, `strict` báo XPASS), đúng như Chỉ Huy đã ghi.
- Bắt đúng ở mọi trường chữ AI: «1tr5», «500 nghìn đồng», «99$», «Bảng giá … 2026» (tiêu đề), «giá rẻ» (từ khóa phụ), «trọn gói». AI đổi từ khóa chính sang «bảng giá cửa cuốn»: chính từ khóa không bị coi là nói giá. «Giá … bao nhiêu» (câu hỏi, không nêu giá) không cảnh báo, đúng quy tắc «không nói giá; báo giá qua Zalo thì được».
- **Không cảnh báo oan** (17 ca): năm («năm 2026», «từ 2019», «bảo hành 2 năm»), kích thước («3200 mm x 2400 mm», «40x80 dày 1,4 ly», «2m4», «1.2mm», «100 kg», «500 W, 220 V», «5 độ, 2 cm»), số nhà thường («số 12 hẻm 45», «12/3 Lê Lợi», «88 đường 3/2»), giờ, mã bài, «2 đồng hồ», «tỷ lệ», «xu hướng».
- **Cảnh báo oan** (3 lỗi Thấp, mục «Lỗi và góp ý»): số nhà có tên đường viết tắt «Đ.», kiệt «K.» (SL-T100-1); số đếm có «nghìn», «ngàn», «triệu» (SL-T100-2); ghi chú dài hơn 900 ký tự ở chỗ cắt khúc (SL-T100-3).

### 4. R5: 9 dòng test cũ đổi (Chỉ Huy duyệt A), gỡ `xfail` SL-T097-5

| File | Dòng đổi | Đúng điều kiện duyệt? |
|---|---|---|
| `tests/test_drafts_images.py` | `== SCHEMA_VERSION == 2` → `3`; `stored["schema_version"] == 2` → `3`; tham số khuôn lạ `[0, 3, …]` → `[0, 4, …]`; `DraftSnapshot(schema_version=3)` → `4` | Có: lưu lại lên khuôn 3; khuôn 4 lạ (giữ đủ 0, 999, -1, "abc", None, [2]) |
| `tests/test_soi_loi_t016_t020.py` | `{"schema_version": 3}` → `4` (ca «phiên bản kế tiếp chưa biết») | Có: khuôn ≥ 4 lạ |
| `tests/test_soi_loi_t041.py` | `assert data["schema_version"] == 2` → `data["schema_version"] = 2` | Có: ca vẫn dựng nháp khuôn 2 «như `main` lưu» (không có `seo`), mở được, giữ ảnh, SEO trống, đủ các khẳng định cũ; ý «nháp lưu mới là khuôn mấy» chuyển sang test mới `test_t100_new_save_writes_v3_and_v4_is_unknown` (lưu mới là khuôn 3, mở được, giữ ảnh; 4 và 99 là lạ). Không nới |
| `tests/test_soi_loi_t055.py` | Hai `== 2` → `== 3`; test canh `:687` `SCHEMA_VERSION + 1 == 3` → `== 4` | Có: test canh vẫn canh đúng dòng `test_soi_loi_t016_t020.py` (cùng lên 4) |
| `tests/test_soi_loi_t097.py` | Gỡ đúng 6 dòng dấu `xfail` SL-T097-5, không đổi thân test | Có: 3 ca nay qua |

Đủ **9 dòng**, mỗi dòng chỉ đổi số khuôn. Không xóa, không bỏ qua, không nới test nào. Grep `schema_version|SCHEMA_VERSION` trong `tests/`: các chỗ còn lại là khuôn của kho thẻ ảnh, kho bài đã đăng, cache kế hoạch (khác kho nháp) hay dùng `SCHEMA_VERSION` theo tên (`test_t041_drafts_seo.py`) hay khuôn 1 cố ý: **không còn test nào ghim khuôn nháp 2** hay coi 3 là lạ.

### 5. Chạy test, thử với `main` mới nhất

| Chạy | Kết quả |
|---|---|
| Nhánh `04febcc`: 40 file test liên quan (kho nháp, gửi nháp, ảnh, kế hoạch, Google, các trang app; danh sách ở «Bằng chứng») | **4.394 passed, 21 skipped, 0 failed** (24 phút; 21 bỏ qua có từ trước: symlink cần quyền đặc biệt trên Windows, quyền kiểu POSIX, ca chỉ chạy trên Mac/Linux, ổ không phân biệt hoa thường) |
| `tests/test_soi_loi_t100.py` trên nhánh | **63 passed, 10 xfailed** |
| Bản gộp thử với `main` mới nhất **`b8ac183`** (có T-091, T-096 lượt 5), kèm file của tôi | Gộp **không xung đột** (worktree tạm, không nhánh, không push, đã gỡ); 41 file: **4.450 passed, 21 skipped, 10 xfailed, 0 failed**; bản cuối file của tôi trên bản gộp: 63 passed, 10 xfailed |

### 6. Gỡ chốt bảo vệ trên bản sao (đột biến)

Trên một `git worktree` tạm của nhánh (đã gỡ), gỡ từng chốt rồi chạy `tests/test_soi_loi_t100.py`:

| Chốt bị gỡ | Test của tôi |
|---|---|
| M1 `_key_present` luôn «không thấy» | Đỏ |
| M2 lệnh thêm «chưa rõ» thì thêm lại | Đỏ |
| M3 bỏ so ô với bản gốc (ghi đè ô vừa sửa ở nơi khác) | Đỏ |
| M4 `safe_text` không thêm dấu cách | Đỏ |
| M5 ghi trạng thái lùi được | Đỏ |
| M6 khuôn 2 bỏ ảnh như trước T-100 | Đỏ |
| M7 bỏ dò giá | Đỏ |
| M8 cache: lỗi «bận» lúc đọc cũng xóa file | **Lọt**: với khóa độc quyền, lỗi «bận» xảy ra ở bước kiểm sức khỏe file (nhánh khác), và Windows không cho xóa file SQLite đang mở. Chỉ là cache (xóa vẫn tạo lại), không xếp lỗi |
| M9 so-rồi-đặt T-089 bỏ so | Đỏ |

### 7. Điều kiện Lá Chắn

| Mã | Kết quả | Bằng chứng (test của tôi) |
|---|---|---|
| LC-T094-1 | Đạt: Sheet giả trên `FakeGoogle`, bộ chặn mạng bật | cả file |
| LC-T094-2 | Đạt: chuỗi mồi ở ô Sheet, lời máy chủ (503, 500) không lọt vào câu báo, lý do, nhãn xung đột, câu báo cache | `test_conflict_message_never_copies_cell_text`, `test_server_error_after_append_…`, `test_old_cache_and_google_down_…` |
| LC-T094-18 | Đạt: dữ liệu từ Sheet và từ cache đi cùng `parse_sheet` → `PlanRow` | `test_formula_like_cells_round_trip_…`, `test_tampered_cache_…` |
| LC-T094-28 | Đạt: chỉ ô của cột app, theo Mã bài, so từng ô với bản gốc; không xóa dòng; `RAW`; chữ dạng công thức có dấu cách đầu; giờ `+07:00` | mục 1 |
| LC-T094-29 | Đạt: cache sửa tay không lái được lệnh ghi; đọc lại Sheet trước khi ghi, trước khi mở Soạn bài; cache hỏng, khóa, chỉ đọc không làm hỏng trang. Ghi chú: «sai một dòng → bỏ cả cache» làm theo nghĩa **dòng ô sai khuôn** (kiểu ô, JSON); dòng thiếu từ khóa thì bỏ dòng có câu báo, y như đọc thẳng từ Sheet (đúng: Sheet thật cũng có dòng như vậy) | mục 1 |
| LC-T094-30 | Đạt: nháp cũ mở, khuôn lên 3, giữ so-rồi-đặt T-089 (cả với dòng của app cũ), việc ghi Sheet còn nợ trong `drafts.sqlite`, thử lại chỉ ghi Sheet, vẫn kiểm xung đột | mục 1, 2 |
| LC-T094-31 | Đạt (test của Thợ Máy: tab tên gần giống «Kehoach», «KeHoach » không bị đụng; tiêu đề thiếu ghi vào cuối dòng 1) | `test_every_write_is_raw_…` chạy «Chuẩn bị trang tính» qua client thật |
| LC-T103-1 | Đạt về ý (5/5 ca của Lá Chắn qua); còn cảnh báo oan SL-T100-1 → -3 | mục 3 |

## Lỗi và góp ý

| # | Mức | Mô tả | Vị trí | Trước Lá Chắn? | Test |
|---|---|---|---|---|---|
| SL-T100-1 | Thấp | Số nhà có tên đường viết tắt kiểu Google Maps («Công trình ở 45 Đ. Số 7, Bình Tân», «123 Đ.Nguyễn Văn Linh») hay kiệt ở Đà Nẵng («12 K. Lê Duẩn») bị coi là giá: «Đ.», «K.» sau số khớp đơn vị tiền «đ», «k» (`\d[\d.,]*\s*(đ\|k)\d*(?!\w)`, dấu «.» không phải chữ). Đề xuất AI có địa chỉ công trình bị cảnh báo giá oan, không tick sẵn | `seo_app/plan/propose.py:398` (`_has_price` dùng `mentions_price` của `seo_app/onpage/meta.py:661`, biểu thức `_PRICE` `:566`) | Có | `test_sl_t100_1_…` (3 ca) |
| SL-T100-2 | Thấp | Số đếm có «nghìn», «ngàn», «triệu» bị coi là giá: «Xưởng đã làm hơn 2 nghìn công trình», «Từ khóa có khoảng 1 nghìn lượt tìm mỗi tháng», «Hơn 5 ngàn khách», «3 triệu lượt xem». Cảnh báo oan, không tick sẵn. (Bước SEO T-036 đã có tiền lệ sửa kiểu này: loại trừ «đồng hồ», «tỷ lệ», «xu hướng», SL-T036-5, -10) | như trên | Có | `test_sl_t100_2_…` (4 ca) |
| SL-T100-3 | Thấp | Ghi chú dài hơn 900 ký tự dò giá theo khúc 900 ký tự (bước 700): chỗ cắt khúc làm mất phần loại trừ. Từ khóa chính «cửa sắt giá rẻ» bắt đầu ở ký tự 688 → 699 hay 1088 → 1099 của ghi chú 2.000 ký tự: khúc sau bắt đầu giữa từ khóa thành «rẻ …», «giá rẻ …» không còn nằm trong từ khóa (24 vị trí bị cảnh báo); «2 đồng hồ» vắt qua ký tự 900 thành «2 đồng» ở cuối khúc đầu. Cùng chữ đó trong ghi chú ngắn, hay nằm xa chỗ cắt: không cảnh báo | `seo_app/plan/propose.py:398` (`_PRICE_WINDOW`, `_PRICE_STEP`) | Có | `test_sl_t100_3_…` (3 ca) và ca đối chứng |

Cách sửa gợi ý (Thợ Máy chọn; không cần đụng `meta.py` của bước SEO):

- SL-T100-1, -2: trong `_has_price`, dò bằng `_PRICE.finditer` rồi bỏ qua chỗ khớp có ngữ cảnh không phải tiền: đơn vị «đ»/«k» ngay sau là «.» rồi chữ cái (tên đường, kiệt viết tắt); số + «nghìn/ngàn/triệu» mà ngay sau là danh từ đếm («công trình», «lượt», «khách», «người», «bộ», «cái», «m2», …). Giữ cảnh báo cho «1,5 triệu», «500 nghìn đồng», «2 triệu» đứng cuối câu.
- SL-T100-3: chỉ tính chỗ khớp **bắt đầu** trong phần «riêng» của khúc (không nằm trong 200 ký tự gối cuối, trừ khúc cuối), và dò từ khóa trên **cả ghi chú** (không trên khúc) rồi bỏ chỗ khớp nằm trọn trong một lần xuất hiện của từ khóa; hay gối khúc theo ranh giới từ (khoảng trắng gần nhất).

**Góp ý (không xếp lỗi):**

- **G1** (phòng xa): `apply_proposals` không tự từ chối đề xuất «Thêm» **chưa có Mã bài**. Hiện mọi đường dựng đề xuất (`compare_rows`, `from_ai`) đều cấp mã nên chưa xảy ra; nhưng nếu sau này có đường khác (T-101 dựng lại đề xuất từ session…), lệnh thêm «chưa rõ» mà Google đã thêm sẽ bị báo «chưa ghi» (đọc lại tìm Mã bài rỗng), bấm lại thành **dòng trùng** (đã thử bằng script: 2 lần thêm). Gợi ý: `_addition` trả `Conflict` khi `after.key` trống.
- **G2** (cần thử thật ở T-101): Sheet có tab tên chỉ khác chữ hoa («Kehoach»): tên tab của Google không phân biệt hoa thường, nên «Chuẩn bị trang tính» có thể bị Google từ chối tạo «KeHoach» (mã 400, câu báo chung). Nên có câu báo riêng «đổi tên tab … thành KeHoach».
- **G3** (cần thử thật ở T-101): Sheet chủ dự án tự làm (đủ tên cột, chưa bấm «Chuẩn bị trang tính») thì cột «Ngày dự kiến» chưa có định dạng ngày: ô app ghi (số ngày kiểu Sheets, `RAW`) có thể hiện thành số «46345». Đọc lại vẫn đúng (bộ đọc nhận số ngày). README hay câu báo nên nhắc bấm «Chuẩn bị trang tính» một lần.
- **G4** (câu báo): «Viết bài» trên dòng **đã «Bỏ»**, hay dòng có ô Trạng thái chữ lạ («xyz», tên gọi không có trong danh sách) **ngay từ lúc mở**: ghi «Đang viết» (và mọi lần ghi sau khi gửi) bị từ chối (đúng, không ghi), nhưng câu báo là «trạng thái hay Mã bài WordPress trên Sheet đã khác lúc mở bài (sửa ở nơi khác)» trong khi không ai sửa; việc còn nợ bị bỏ nên dòng kế hoạch không bao giờ được cập nhật mà người dùng không biết lý do thật (script `probe_dropped_row.py`). Gợi ý: câu riêng khi trạng thái hiện tại bằng `expect_status` mà không thuộc thứ tự («Dòng đang ở trạng thái Bỏ / ô Trạng thái không đọc được, phần mềm không ghi tiếp»), và T-101/T-102 không cho «Viết bài» trên dòng «Bỏ».
- **Ghi nhận** (đúng thiết kế, không phải lỗi): ghi chú cũ có giá mà AI không đổi thì không cảnh báo; lý do của AI (không ghi lên Sheet) không dò giá; khe hở 1–2 giây hai máy ghi cùng một ô, lệnh ghi > 200 ô tách nhiều lệnh, dòng chưa có mã được cấp mã ở lần ghi không rõ kết quả rồi báo «không còn thấy dòng» (Thợ Máy đã ghi trong báo cáo).

## Cách tái hiện

```bash
uv run pytest -q tests/test_soi_loi_t100.py -rX
```

Script dò (ngoài repo, thư mục ghi chú chung của nhóm phiên): `T-100-soi-loi-scripts/probe_g2.py` (bảng có/không cảnh báo), `probe_g2b.py` (quét vị trí từ khóa trong ghi chú 2.000 ký tự), `probe_keyless_add.py` (G1), `probe_dropped_row.py` (G4), `probe_columns_moved.py` (đổi chỗ cột), `probe_lock_time.py` (thời gian chờ khi cache bị khóa), `mutate_t100.py` (mục 6, chạy trong worktree tạm).

## Bằng chứng

- `tests/test_soi_loi_t100.py` trên nhánh: **63 passed, 10 xfailed**.
- 40 file test liên quan trên nhánh `04febcc`: **4.394 passed, 21 skipped, 0 failed**. Danh sách: `test_app_drafts`, `test_app_images`, `test_app_pages`, `test_drafts_images`, `test_google_service_account`, `test_google_sheets`, `test_images_folders_t063`, `test_la_chan_t056`, `test_la_chan_t076`, `test_la_chan_t086`, `test_la_chan_t097`, `test_plan_ai`, `test_plan_cache`, `test_plan_model`, `test_plan_parse`, `test_plan_propose`, `test_plan_sync`, `test_soi_loi_t016_t020`, `test_soi_loi_t021_t017`, `test_soi_loi_t041`, `test_soi_loi_t055`, `test_soi_loi_t056`, `test_soi_loi_t076`, `test_soi_loi_t081`, `test_soi_loi_t086`, `test_soi_loi_t089`, `test_soi_loi_t097`, `test_soi_loi_t098`, `test_storage_drafts`, `test_storage_send_state`, `test_t041_drafts_seo`, `test_t041_links_ai`, `test_t041_meta`, `test_t041_seo_ui`, `test_t083_alt_tien_to`, `test_t086_send_state`, `test_t089_send_draft`, `test_t090_meta_emoji_moi`, `test_t100_drafts_plan`, `test_t100_google_identity`.
- Bản gộp thử với `main` `b8ac183` (41 file, gồm file của tôi): **4.450 passed, 21 skipped, 10 xfailed, 0 failed** (28 phút 35 giây; 10 xfail là đúng 10 ca lỗi mới của tôi; 21 bỏ qua như trên nhánh). File của tôi trong lần chạy đó là bản 66 ca; bản cuối (73 ca) chạy riêng trên bản gộp: **63 passed, 10 xfailed**.
- LC-T103-1 (5 ca của Lá Chắn từ `team/T-103`, `--runxfail`) với code T-100: 6 passed (5 ca + test canh).
- `uv run ruff check .` sạch; `ruff format --check` file test sạch; quét ký tự ẩn: file của tôi và mọi file T-100 đổi sạch (ký tự lạ trong `test_soi_loi_t016_t020.py`, `test_soi_loi_t055.py` là dữ liệu test cố ý, có từ trước, không nằm ở dòng T-100 đổi); `PYTHONUTF8=1 uvx detect-secrets scan` các file T-100 và file của tôi: 0 phát hiện (mồi «AKIA…» trong file tiếng Việt tạm: bắt được, đã xóa).
- Giờ nộp: 2026-10-29 00:59 +07:00 (đồng hồ máy).

## Đối chiếu tiêu chí xong (phần việc Soi Lỗi)

| Việc Chỉ Huy giao | Kết quả |
|---|---|
| 1. Đồng bộ: không thêm dòng trùng khi `unsure`; xung đột khi bảng tính và máy cùng đổi; luôn `RAW`; cache hỏng, cũ, bị khóa | Đạt (mục 1) |
| 2. Kho nháp khuôn 1, 2, 3; `plan`, `SendState` không phá luồng gửi T-086, T-089 | Đạt (mục 2) |
| 3. SL-T097-5, G2 đúng ý; G2 không cảnh báo oan với số thường | SL-T097-5 đạt; G2 đúng ý, năm và kích thước không oan; **số nhà viết tắt, số đếm nghìn/triệu, ghi chú dài: oan** (SL-T100-1 → -3) |
| 4. Soát 9 dòng test đổi, grep test ghim khuôn khác | Đạt (mục 4) |
| 5. Chạy test kho nháp, gửi nháp, kế hoạch, Google; thử với `main` mới nhất | Đạt (mục 5) |
| 6. Báo cáo, `xfail(strict=True)` cho lỗi mới, commit lên `team/T-100`, không gộp `main` | Đạt |

## Đề xuất

- Lượt 2 ngắn của Thợ Máy cho SL-T100-1 → -3 (chỉ `propose.py`, gỡ 10 dấu `xfail`), rồi Soi Lỗi soát nhanh; hay Chỉ Huy ghi nhận để sau nếu muốn đưa T-100 sang Lá Chắn ngay (3 lỗi chỉ là cảnh báo thừa).
- Khi gộp T-103: gỡ 5 dấu `xfail` LC-T103-1 trong `tests/test_la_chan_t103.py`.
- T-101 nên thử thật G2, G3 (tab khác chữ hoa, cột ngày chưa định dạng) với một Google Sheet thử.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-30 09:16 +07:00) · soát lượt sửa của Thợ Máy (`57bac59`)

| Mục | Nội dung |
|---|---|
| Phiếu giao | Chỉ Huy B, 30/10 08:30: xác nhận SL-T100-1 → -3, G1; phần Lá Chắn bắt sửa (LC-T100-1 → -3) không phá đồng bộ, kho nháp, khóa gửi trùng; R5 các dấu `xfail` gỡ; lỗi mới do lượt 2 |
| Đầu nhánh soát | `57bac59` (Thợ Máy lượt 2), trên `9840e13` (gộp `main` `0122d4b`: T-103, T-104); Lá Chắn `789713a` |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T100-1 → -3 và G1 **đóng** (mọi ca đã báo qua); LC-T100-1 → -3 sửa đúng hướng; đồng bộ, kho nháp, khóa gửi trùng không bị phá; R5 đúng. **8 lỗi Thấp mới** (SL-T100-4 → -11): 2 ở phần Sheet (LC-T100-3, LC-T100-1 còn biến thể), 6 ở hàm dò giá mới (3 hồi quy so với lượt 1, 2 mới, 1 biến thể gần LC-T100-2 còn lọt). 0 Nghiêm trọng, 0 Cao, 0 Trung bình. Không lỗi nào chặn gộp (chưa có giao diện dùng tới); nên sửa trước T-101, T-102 như hạn của Lá Chắn |

### Tóm tắt (cho chủ dự án)

- **Lỗi cũ đã sửa:** địa chỉ «45 Đ. Số 7», số đếm «hơn 2 nghìn công trình», ghi chú dài không còn bị cảnh báo giá oan. Đề xuất «thêm bài» chưa có Mã bài không bao giờ được gửi lên Sheet (trước đây có thể thành dòng trùng).
- **Phần Lá Chắn bắt sửa chạy đúng:** Sheet đủ 1.000 dòng thì phần mềm báo và không thêm dòng mới; cảnh báo giá bắt thêm «Giá thay motor 1.200.000», «VNĐ 500.000», «5tr»…; bài mở từ Sheet khác thì không ghi trạng thái nhầm Sheet. Nháp và khóa chống gửi trùng không bị ảnh hưởng.
- **Còn 8 lỗi nhỏ**, đều chưa ảnh hưởng vì chưa có nút bấm nào dùng tới (trang Kế hoạch T-101, bước Xuất bản T-102 chưa làm):
  - Hàm dò giá viết lại **bỏ sót** vài cách ghi giá trước đây vẫn bắt («Bộ bản lề 150.000 Đ.», «bảo dưỡng 300 nghìn lần đầu», «cổng 15 triệu nhà anh Tuấn») và **báo oan** vài cách viết khác («lắp giá đỡ cách sàn 2.500 mm», «được đánh giá cao bởi 12.000 khách», từ khóa gõ không dấu).
  - Vẫn sót cách ghi «Tiền thay motor 1.200.000», «Thay motor hết 1.200.000».
  - Chữ AI cố tình lặp từ khóa thì việc dò giá chậm dần (tới vài chục giây với 100 đề xuất).
  - Nếu phần mềm đưa nhầm mã Sheet lúc ghi trạng thái, vẫn có thể ghi nhầm Sheet.
  - Sheet đã quá 1.000 dòng: dòng chưa có mã vẫn có thể được cấp một mã trùng với dòng nằm ngoài phần phần mềm đọc được.
- **Không có gì phải anh/chị quyết.**

### R5: các dấu `xfail` được gỡ

| File | Gỡ | Dòng xóa / thêm | Đúng? |
|---|---|---|---|
| `tests/test_la_chan_t103.py` | 1 dấu LC-T103-1 (test nhiều tham số, 5 ca) | 4 / 0 | Có: chỉ dấu; 5 ca nay qua (sau khi gộp `main`, đúng như lượt 1 đã báo trước) |
| `tests/test_la_chan_t100.py` | 5 dấu: LC-T100-1 (3), LC-T100-2 (1 dấu, 8 ca), LC-T100-3 (1) | 7 / 0 | Có: chỉ dấu, thân test giữ nguyên, nay qua |
| `tests/test_soi_loi_t100.py` | 3 dấu SL-T100-1 (3 ca), -2 (4 ca), -3 (3 ca) | 13 / 0 | Có: chỉ dấu; 10 ca nay qua |
| `tests/test_plan_sync.py` (test của Thợ Máy) | Không gỡ dấu; đổi 2 dòng: hàm giả `write_then_other_tab` nhận thêm `sheet_id` để chuyển tiếp | 2 / 2 | Có: bắt buộc vì `retry_pending` nay gọi `write_status(…, sheet_id=…)`; khẳng định của test giữ nguyên |

Không xóa, không bỏ qua, không nới test nào. Test canh của Lá Chắn (số đếm có dấu chấm nghìn) và mọi ca giá, số thường của tôi ở lượt 1 giữ nguyên, đều qua.

### Từng lỗi cũ

| Lỗi | Kiểm lại | Kết quả |
|---|---|---|
| SL-T100-1 | 3 ca đã báo qua; biến thể «Kiệt 12 K.Lê Duẩn» (không dấu cách sau «K.») qua. Biến thể chữ thường «45 đ. số 7», «123 đ.Nguyễn Văn Linh» vẫn bị cảnh báo oan, và cách sửa làm lọt giá thật «150.000 Đ.»: gộp thành SL-T100-5 | **Đóng** (ca đã báo) |
| SL-T100-2 | 4 ca đã báo qua; «10k lượt xem», «Hơn hai nghìn khách» qua. Danh sách danh từ đếm quá rộng làm lọt giá: SL-T100-6 | **Đóng** (ca đã báo) |
| SL-T100-3 | 3 ca qua; nay dò trên cả chữ, không cắt khúc (Thợ Máy thử từ khóa ở mọi vị trí của ghi chú 2.000 ký tự) | **Đóng** |
| G1 | «Thêm» không Mã bài, lệnh thêm «chưa rõ», bấm lại hai lần: cả hai lần là xung đột `CONFLICT_NO_KEY`, **0** lệnh thêm dòng; `_key_present("")` trả «chưa rõ» | **Đóng** |

### Phần Lá Chắn bắt sửa (không phá luồng cũ)

| Mã | Kiểm | Kết quả |
|---|---|---|
| LC-T100-1 | Sheet đủ 1.001 dòng: câu báo `MSG_FULL`, «Thêm» thành `CONFLICT_FULL`, không lệnh thêm, sửa dòng đọc được vẫn ghi. Biến thể: lúc xem còn 999 dòng, **máy khác thêm 2 dòng** trước khi bấm áp dụng: chặn đúng, dòng sửa vẫn ghi. Ghi trạng thái dòng ngoài vùng đọc `BLOCKED` (giữ việc); «Viết bài» trên dòng đó báo `MSG_FULL` (test của Thợ Máy) | Đúng; **còn** SL-T100-11 (cấp mã mới cho dòng chưa có mã trên Sheet đầy) |
| LC-T100-2 | 8 ca của Lá Chắn qua. Thêm 15 cách viết phải bắt: «5tr», «5 TR», «1.5tr», «Giá 500.000», «VNĐ 500.000», «500.000 VNĐ», «500.000vnđ», «150k/m2», «500K», «giá 350.000/bộ», «Tiền công 200.000», «2 triệu rưỡi», «năm trăm nghìn», «1,2 triệu», «99$»: bắt hết. 8 cách viết số thường, mã, kích thước («Cửa 1.200 x 2.400 mm», «Giá đỡ ray đặt cao 1.200 mm», «Inox 304, mã B-012, CT012», «Năm 2026», «10.000 lượt tìm»…): không cảnh báo | Đúng với ca của Lá Chắn; **còn** SL-T100-5, -6 (hồi quy), -7 (oan mới), -8 (hồi quy), -9 (biến thể gần), -10 (chậm) |
| LC-T100-3 | Không đưa `sheet_id`: so với Sheet thật của client; nháp của Sheet khác → `BLOCKED`, không đọc, không ghi, giữ việc; nháp đúng Sheet → ghi (đối chứng) | Đúng; **còn** SL-T100-4 (đưa `sheet_id` lệch với client thì vẫn ghi nhầm) |
| Đồng bộ, kho nháp, khóa gửi trùng | Lượt 2 không đổi `drafts.py`, `plan_cache.py`, `app/`. Bộ test chọn lọc (đồng bộ, cache, kho nháp, trạng thái gửi, T-086, T-089, dò giá, Google, T-103): xem «Bằng chứng (lượt 2)» | Không lùi |

### Lỗi mới (lượt 2)

| # | Mức | Mô tả | Vị trí | Trước Lá Chắn? | Test |
|---|---|---|---|---|---|
| SL-T100-4 | Thấp | LC-T100-3 đóng chưa trọn: `write_status`, `record_status`, `retry_pending` so mã băm Sheet của việc với `sheet_id` **nơi gọi đưa** (có thì dùng, bỏ qua Sheet thật của client). Client nối Sheet A mà nơi gọi đưa mã Sheet B (client cũ còn giữ trong phiên sau khi đổi `GOOGLE_SHEET_ID`, hay truyền nhầm biến): trạng thái của nháp mở từ Sheet B vẫn **ghi vào dòng cùng mã của Sheet A**, việc còn nợ bị bỏ. Đúng cái hại LC-T100-3 muốn chặn | `seo_app/plan/sync.py:860` (`_connected_hash`: `sheet_id` thắng `client.sheet_hash`) | Có | `test_sl_t100_4_…` |
| SL-T100-5 | Thấp | Luật bỏ qua tên đường viết tắt (sửa SL-T100-1) dựa vào **chữ hoa** «Đ»/«K» + dấu cách trước + dấu chấm sau: (a) **hồi quy**: giá thật «Bộ bản lề 150.000 Đ.», «Thay bản lề hết 150.000 Đ. Khách đồng ý» không còn được cảnh báo (lượt 1 bắt được); (b) địa chỉ gõ chữ thường «45 đ. số 7», «123 đ.Nguyễn Văn Linh» vẫn bị cảnh báo oan | `seo_app/plan/propose.py:463` | Có | `test_sl_t100_5_…` (4 ca) |
| SL-T100-6 | Thấp | **Hồi quy**: danh sách danh từ đếm (sửa SL-T100-2) có «lần», «nhà», «căn», «hộ»… là chữ hay đứng ngay sau giá: «Bảo dưỡng cửa cuốn 300 nghìn lần đầu», «Cổng 15 triệu nhà anh Tuấn ở Thủ Đức», «Làm cửa 8 triệu căn hộ quận 2» không còn được cảnh báo (lượt 1 bắt được) | `seo_app/plan/propose.py:430` (`_COUNT_NOUNS`), `:450` | Có | `test_sl_t100_6_…` (3 ca) |
| SL-T100-7 | Thấp | **Mới ở lượt 2**: `_PRICE_LABEL` coi chữ «giá» trong từ ghép là nhãn giá: «giá đỡ», «giá kệ» (đồ sắt), «đánh giá», rồi số có dấu chấm nghìn trong vòng 3 từ: **kích thước** «Lắp giá đỡ cách sàn 2.500 mm», «Làm giá kệ sắt 1.200 x 600 mm» và **số đếm** «Được đánh giá cao bởi 12.000 khách», «Đánh giá của hơn 10.000 khách hàng» bị cảnh báo giá oan, không tick sẵn. Cùng gốc, có từ trước (cả bước SEO): «Khách đánh giá tốt dịch vụ» khớp cụm «giá tốt» | `seo_app/plan/propose.py:404`, cụm `_PRICE_PHRASES` | Có | `test_sl_t100_7_…` (5 ca) |
| SL-T100-8 | Thấp | **Hồi quy**: `_keyword_spans` so từ khóa chính **có dấu**; từ khóa gõ không dấu trong Sheet («cua sat gia re», «bang gia cua cuon») không còn che chữ có dấu trong ghi chú («cửa sắt giá rẻ», «bảng giá cửa cuốn») nên bị cảnh báo giá oan. Lượt 1 (và bước SEO, SL-T041-3) so không dấu | `seo_app/plan/propose.py:468` | Có | `test_sl_t100_8_…` (2 ca) |
| SL-T100-9 | Thấp | Biến thể gần LC-T100-2 còn lọt (có từ lượt 1): số tiền không đơn vị sau «tiền», «hết», «tốn», «trả», «công thợ»: «Tiền thay motor 1.200.000», «Thay motor hết 1.200.000», «Khách trả 2.500.000 cho cổng», «Tốn 800.000 tiền vật tư», «Công thợ 300.000 một ngày». Trong khi «Giá thay motor 1.200.000», «Tiền công 200.000» thì bắt | `seo_app/plan/propose.py:404` (chỉ «giá», «phí», «tiền công») | Có | `test_sl_t100_9_…` (5 ca) |
| SL-T100-10 | Thấp | **Mới ở lượt 2**: `outside()` so mỗi chỗ khớp với **mọi** lần xuất hiện của từ khóa (danh sách, không chia đôi như `_KeywordSpans` của bước SEO): chữ AI lặp từ khóa ngắn dày đặc làm thời gian tăng theo bình phương: «5k » lặp, từ khóa «5k 5k»: 500 ký tự 6 ms, 2.000 ký tự 104 ms (gấp 16 lần khi chữ dài gấp 4; không từ khóa: gấp 3,6). 100 mục AI độc như vậy: khoảng 10–25 giây treo trang. Test tốc độ của Thợ Máy dùng từ khóa không lặp nên không thấy | `seo_app/plan/propose.py:488` | Có | `test_sl_t100_10_…` |
| SL-T100-11 | Thấp | Biến thể gần LC-T100-1 còn hở: Sheet đầy chỉ chặn «Thêm». Dòng **chưa có mã** đọc được vẫn được `compare_rows` cấp mã kế tiếp theo các mã đọc được (đường «Cập nhật»), mà mã đó có thể đã có ở dòng ngoài vùng đọc: thử Sheet 1.003 dòng, dòng 2 chưa mã được cấp «B-1000», trong khi «B-1000» đã ở dòng 1.002 → Sheet có **hai dòng B-1000**; về sau ghi trạng thái cho bài B-1000 thấy dòng 2 | `seo_app/plan/sync.py:538` (`_update` không xét `fresh.full` khi đổi Mã bài) | Có | `test_sl_t100_11_…` |

Cách sửa gợi ý (Thợ Máy chọn):

- SL-T100-4: client có `sheet_hash` thì luôn so với nó (nơi gọi đưa thêm `sheet_id` thì cả hai phải khớp); chỉ dùng `sheet_id` khi client không cho biết Sheet.
- SL-T100-5: quyết định theo **hình dạng số** thay vì chữ hoa: số có dấu chấm nghìn («150.000») luôn là tiền; bỏ qua «đ.», «Đ.», «k.», «K.» chỉ khi số trước nó là số nhà (không dấu chấm nghìn, ngắn) và sau dấu chấm là chữ (tên đường).
- SL-T100-6: bỏ «lần», «nhà», «căn», «hộ», «bài», «cái», «chiếc»… khỏi danh sách đếm, hay chỉ coi là số đếm khi đơn vị là «nghìn/ngàn/triệu» mà danh từ đi kèm là số đông («lượt», «khách», «người», «công trình», «truy cập»…).
- SL-T100-7: «giá» chỉ là nhãn khi không đứng sau «đánh» và không đứng trước «đỡ», «kệ», «treo», «trị»; cụm «giá tốt», «giá từ»… cũng không tính sau «đánh».
- SL-T100-8: tìm từ khóa trên chữ đã bỏ dấu (như `_KeywordSpans` của `seo_app/onpage/meta.py`: bỏ dấu từng ký tự, giữ vị trí).
- SL-T100-9: thêm «tiền» (trừ «mặt tiền», đã có test canh của Thợ Máy), «hết», «tốn», «trả», «công thợ» vào nhóm chữ đứng trước số tiền không đơn vị; giữ test canh «10.000 lượt tìm», «Mặt tiền 5.000 mm».
- SL-T100-10: gộp và sắp các khoảng từ khóa, so bằng chia đôi (`bisect`), như `_KeywordSpans.covers`.
- SL-T100-11: trong `_update`, Mã bài mới khác mã cũ (cấp mã cho dòng chưa có mã) mà `fresh.full` thì `Conflict` `CONFLICT_FULL`, như «Thêm».

**Góp ý (không xếp lỗi):**

- **G5:** Sheet đầy mà còn nhiều việc ghi trạng thái cho dòng ngoài vùng đọc: các việc đó nay `BLOCKED` (giữ lại) và `retry_pending` đi tiếp, mỗi việc **đọc lại cả Sheet một lần**, ở mỗi lần mở trang. Vài chục việc như vậy dễ chạm hạn mức đọc của Google (lỗi 429, trang chậm). Gợi ý: đọc Sheet một lần cho cả lượt thử lại, hay dừng ở việc `STATUS_FULL` đầu tiên.
- G2, G3, G4 của lượt 1 (tab khác chữ hoa, cột ngày chưa định dạng, câu báo dòng «Bỏ»): chưa đổi, đúng như Thợ Máy ghi (việc giao diện, thử thật).

### Bằng chứng (lượt 2)

- `tests/test_soi_loi_t100.py`: **99 passed, 22 xfailed** (121 ca) (thêm 48 ca lượt 2: G1, LC-T100-1 biến thể, LC-T100-3 đối chứng, 15 dạng giá phải bắt, 8 dạng số thường; 22 `xfail` của 8 lỗi mới).
- Bộ test chọn lọc 18 file trên `57bac59`: **1.227 passed, 22 xfailed, 0 failed** (39 phút; 22 xfail là đúng 22 ca của 8 lỗi mới). Gồm `test_plan_sync`, `test_plan_cache`, `test_t100_drafts_plan`, `test_la_chan_t100`, `test_plan_propose`, `test_la_chan_t103`, `test_google_sheets`, `test_storage_send_state`, `test_storage_drafts`, `test_t086_send_state`, `test_t089_send_draft`, `test_soi_loi_t089`, `test_la_chan_t089`, `test_soi_loi_t103`, `test_t103_plan_prompt`, `test_soi_loi_t097`, `test_t100_google_identity` và file của tôi. Máy đang chạy toàn bộ test của Chỉ Huy cùng lúc nên chỉ chạy chọn lọc.
- Script dò (thư mục ghi chú chung, `T-100-soi-loi-scripts/`): `probe_round2_price.py` (bảng phải bắt / không được báo, so lượt 1 với lượt 2), `probe_round2_sync.py` (G1, SL-T100-4, thời gian), `probe_round2_time.py`, `probe_full_key_assign.py` (SL-T100-11).
- `uv run ruff check .` sạch; `ruff format --check` file test sạch; quét ký tự ẩn: sạch; `PYTHONUTF8=1 uvx detect-secrets scan` file của tôi và 6 file đổi ở lượt 2: 0 phát hiện (mồi «AKIA…» bắt được, đã xóa).

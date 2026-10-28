# Biên bản bảo mật T-100 · Đồng bộ kế hoạch với Google Sheets, cache, nối nháp

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-100](../tickets/T-100-dong-bo-ke-hoach-cache-nhap.md) (Thợ Máy `ca48c5a`, `04febcc`; Soi Lỗi `07bca14`; gốc `main` `b241e79`) · điều kiện [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3; riêng LC-T094-28, -29, -30, -31; liên quan LC-T094-5, -11, -18. Thêm: SL-T097-5, G2 / LC-T103-1 |
| Phạm vi | **Rút gọn**. Diff `b241e79..07bca14`: `seo_app/plan/sync.py` (mới, 1.067 dòng), `seo_app/storage/plan_cache.py` (mới, 453), `seo_app/storage/drafts.py` (+318/−11), `seo_app/plan/propose.py` (+43/−5), `seo_app/google/service_account.py` (+22/−2); test mới `fake_plan_sheet.py`, `test_plan_sync.py`, `test_plan_cache.py`, `test_t100_drafts_plan.py`, `test_t100_google_identity.py`, `test_soi_loi_t100.py`; 9 dòng test cũ ghim khuôn nháp 2 (Chỉ Huy duyệt A), gỡ 3 `xfail` SL-T097-5. Đọc thêm: client `seo_app/google/sheets.py` (T-097: vùng đọc, `RAW`, lệnh thêm dòng), `parse._header_map`, `parse._row` (T-098), `mentions_price` (`seo_app/onpage/meta.py`), thiết kế T-094 mục 1.5–1.7, 2.4–2.6. Không đổi: `app/`, `config/`, `seo_app/wordpress/`, `pyproject.toml`, `uv.lock`, `.gitignore`, `.env.example` |
| Ngày | 2026-10-29 (01:32–02:05 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp mới** (LC-T100-1, -2, -3) cộng 3 Thấp của Soi Lỗi (SL-T100-1 → -3, giữ mức). **Không lỗi nào bắt buộc sửa trước khi gộp T-100** (phần này chưa nối vào giao diện). LC-T100-1, -2 sửa trước khi T-101 nối «Áp dụng» và đề xuất AI; LC-T100-3 trước khi T-102 gọi `record_status`. Gộp `main` được: không xung đột; 32 file test liên quan qua trên cây gộp, trừ đúng 5 ca `xfail` LC-T103-1 nay qua (XPASS) phải gỡ dấu khi gộp (điều kiện 4) |

## Tóm tắt (cho chủ dự án)

Phần đồng bộ kế hoạch với Google Sheets **an toàn để gộp** (giao diện làm ở T-101, T-102). Mọi chữ đọc từ Sheet đều được làm sạch như chữ trong file. Mọi ô ghi lên Sheet là chữ thường (không thành công thức, cả khi tải về mở bằng Excel). Trước mỗi lần ghi, app đọc lại Sheet: ô nào vừa bị sửa ở nơi khác thì không ghi. App không bao giờ xóa dòng. Ghi trạng thái lại chỉ ghi Sheet, không gửi lại bài. File lưu tạm trên máy bị hỏng hay bị sửa tay thì app bỏ đi và tải lại; file đó không chứa khóa hay mã Sheet. Nháp cũ vẫn mở được, khóa chống gửi trùng không đổi.

Tôi tìm thêm 3 lỗi nhỏ, đều chưa ảnh hưởng vì chưa có nút bấm nào dùng tới:

1. Khi Sheet có từ 1.000 dòng kế hoạch trở lên, app chỉ đọc 1.000 dòng đầu mà không báo. Bài mới thêm nằm ngoài phần app đọc được, nên thêm lại lần nữa sẽ thành dòng trùng.
2. Cảnh báo «AI nhắc tới giá» còn lọt cách viết hay gặp như «Giá thay motor 1.200.000», «Chi phí 800.000», «VNĐ 500.000».
3. Nếu đổi sang Sheet khác (ví dụ thử trên Sheet bản sao rồi quay lại Sheet thật) rồi mới gửi bài mở từ Sheet cũ, trạng thái bài có thể bị ghi vào dòng cùng mã của Sheet đang dùng.

## Lỗi phát hiện

### LC-T100-1 · Sheet đủ 1.000 dòng: dòng thêm nằm ngoài vùng đọc, thêm trùng không biết

| Mục | Nội dung |
|---|---|
| Mức | **Thấp** (cần Sheet từ 1.000 dòng kế hoạch; không mất dữ liệu cũ, không đụng website; sinh dòng trùng Mã bài, dữ liệu sau dòng 1.001 bị bỏ qua không báo) |
| Chỗ | Client đọc đúng vùng `'KeHoach'!A1:Z1001` (`seo_app/google/sheets.py:71`): Google trả tối đa 1.001 dòng đầu. `sync.read_sheet`/`parse_sheet` (`sync.py:222`, `:279`) không xét vùng đã đầy. `apply_proposals` (`:401`) bỏ qua số dòng `append_row` trả về; `_addition` (`:478`) chỉ so Mã bài với các dòng đọc được; `_key_present` (`:592`) trả «chưa có» khi Mã bài nằm ngoài vùng đọc |
| Tái hiện | Sheet giả cắt lệnh đọc như Google (`probe_full_sheet.py`; Sheet giả của test hiện có trả mọi dòng nên không thấy). Sheet có 1.000 dòng kế hoạch: app đọc 1.000 dòng, **không cảnh báo**. «Thêm» bài mới → Google thêm ở dòng 1.002; đọc lại không thấy. Dán lại đúng bài đó → đề xuất «Thêm» cùng mã `B-1001`, **ghi lần nữa** (dòng 1.002 và 1.003 cùng mã). Lệnh thêm «chưa rõ» (Google đã thêm, mạng đứt) → `_key_present` không thấy → báo «chưa ghi» → bấm lại → thêm trùng (dòng 1.004, 1.005). `tests/test_la_chan_t100.py`: 3 ca `xfail(strict=True)` (`test_lc_t100_1_…`), hỏng đúng ở `assert plan.warnings`, `assert 2 <= 1`, `assert not result.not_written` |
| Vì sao quan trọng | Việc 2 của phiếu: không thêm dòng trùng khi «chưa rõ». LC-T094-18 giới hạn 1.000 dòng cho mọi nguồn kế hoạch; file, chữ dán quá giới hạn thì báo («Bảng có hơn 1.000 dòng»), Sheet thì im lặng cắt. Danh sách từ khóa dán vào Sheet dễ vượt 1.000 dòng |
| Cách sửa gợi ý | Google trả đủ `MAX_ROWS` dòng (vùng đầy, có thể còn dòng sau): (a) câu báo cố định «Kế hoạch đã tới 1.000 dòng, phần mềm chỉ đọc 1.000 dòng đầu…»; (b) không thêm dòng mới (`Conflict` câu cố định); (c) `_key_present` trả «chưa rõ» (`None`), không trả «chưa có». Thêm: số dòng `append_row` trả về lớn hơn `MAX_ROWS` thì báo. Sửa Sheet giả để test cắt lệnh đọc như Google |
| Ai sửa, hạn | Thợ Máy (lượt sửa T-100). Trước khi T-101 nối nút «Áp dụng» |

### LC-T100-2 · Cảnh báo giá trong chữ AI còn lọt cách viết giá thường gặp

| Mục | Nội dung |
|---|---|
| Mức | **Thấp** (cách sửa LC-T103-1 chưa đủ; vẫn cần người dùng duyệt đề xuất, rồi duyệt bài) |
| Chỗ | `propose._has_price` (`propose.py:398`) dò bằng `mentions_price` (`seo_app/onpage/meta.py:661`, biểu thức `_PRICE` `:566`): số tiền phải có đơn vị đứng **sau** (đ, k, nghìn, triệu, VNĐ…); «giá» chỉ tính khi theo sau là «rẻ, tốt, chỉ, từ…» |
| Tái hiện | `probe_price.py`: 20 cách viết giá trong ghi chú do AI đề xuất, **lọt 11**: «Giá thay motor 1.200.000», «Giá: 500.000», «giá 350.000/bộ», «Đơn giá 1.200.000/m2», «Báo giá 2.500.000 cho cửa 3m», «Chi phí 800.000 một lần», «Phí khảo sát 200.000», «VNĐ 500.000», «VND 1.500.000», tiếng lóng «2 củ», «15 chai». Đề xuất đó vẫn **tick sẵn**. Bắt được: «1tr5», «1,5tr», «500 ngàn», «150.000 đồng», «₫500.000», «500.000VND», «giá chỉ 99», «2-3 triệu», «rẻ hơn». `tests/test_la_chan_t100.py::test_lc_t100_2_…` (8 ca, `xfail(strict=True)`, không gồm tiếng lóng) |
| Cách sửa gợi ý | Dò thêm số có dấu chấm nghìn đi sau «giá, đơn giá, báo giá, chi phí, phí» (trong vài từ, có thể có «:») hay đi sau «VNĐ, VND». Không cảnh báo số đếm: test canh `test_counts_with_thousand_dots_are_not_prices` («10.000 lượt tìm mỗi tháng», «từ năm 2009») đang qua, phải giữ. Làm cùng SL-T100-1 → -3 (cùng hàm). Sửa `_PRICE` dùng chung với bước SEO thì chạy test mọi nơi gọi |
| Ai sửa, hạn | Thợ Máy (lượt sửa T-100). Trước khi T-101 hiện đề xuất AI có tick sẵn |

### LC-T100-3 · Ghi trạng thái sau khi gửi không so Sheet của nháp

| Mục | Nội dung |
|---|---|
| Mức | **Thấp** (ghi sai một dòng kế hoạch của Sheet khác; không đụng website, không lộ gì) |
| Chỗ | `sync.record_status` (`sync.py:706`) → `write_status` (`:646`): đọc lại và ghi vào Sheet **đang kết nối**, so Mã bài, trạng thái, Mã bài WordPress, nhưng không so `write.sheet_hash` (mã băm Sheet nơi mở nháp). `retry_pending` (`:736`) có lọc theo mã băm, `find_plan_draft` cũng nhận mã băm; riêng lần ghi đầu thì không |
| Tái hiện | Nháp mở từ Sheet bản sao (`DraftPlanRef.sheet_hash` của mã khác), client nối Sheet thật có dòng `B-001` «Chưa viết»: `record_status(…, status_write(ref, «Đã gửi nháp», wp_post_id=501))` **ghi** Trạng thái, Mã bài WordPress, Cập nhật lúc vào dòng `B-001` của Sheet thật. `tests/test_la_chan_t100.py::test_lc_t100_3_…` (`xfail(strict=True)`, hỏng ở `assert sheet.updates == []`) |
| Vì sao quan trọng | Thử thật Giai đoạn 5 làm trên **Sheet bản sao** (LC-T094-44), rồi đổi `GOOGLE_SHEET_ID` về Sheet thật: nháp thử còn trên máy, gửi (hay hẹn giờ) nháp đó thì dòng cùng mã của Sheet thật thành «Đã gửi nháp» kèm mã bài của bài thử. Hai Sheet chép từ nhau có cùng Mã bài, trạng thái, nên các phép so hiện có đều qua |
| Cách sửa gợi ý | Trước khi ghi, so `write.sheet_hash` với mã băm Sheet của client (client cho biết mã Sheet, hay `record_status` nhận `sheet_id` như `retry_pending`); khác thì không ghi, giữ việc còn nợ cho đúng Sheet của nó, câu báo cố định. Test gọi được cả hai cách |
| Ai sửa, hạn | Thợ Máy (lượt sửa T-100). Trước khi T-102 gọi `record_status` |

## Đối chiếu điều kiện Lá Chắn T-094

| Mã | Đạt? | Bằng chứng |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress thật | **Đạt** | Sheet giả có trạng thái `tests/fake_plan_sheet.py` gắn vào `FakeGoogle`, đi qua `SheetsClient` thật; khóa RSA sinh lúc chạy; bộ chặn mạng `tests/conftest.py` không đổi. `sync.py` chỉ nhập `seo_app.google.sheets`, `seo_app.plan`, `seo_app.storage` (không nhập gì của `seo_app.wordpress`) |
| **LC-T094-2** Câu báo cố định | **Đạt** | Hằng `MSG_*`, `CONFLICT_*`, `STATUS_*` (`sync.py:89-136`), `_MSG_*` (`plan_cache.py:263-264`, `drafts.py`): chỉ có Mã bài đã chuẩn hóa, tên cột chuẩn, số dòng; lỗi Google là `str(SheetsError)` (câu cố định T-097); lỗi SQLite, OS thành câu cố định `from None` |
| **LC-T094-3**, **-5** (phần dữ liệu) | **Đạt** | `parse_sheet` là đường duy nhất đổi ô Sheet hay ô cache thành kế hoạch, qua `parse._row` → `PlanRow` (bỏ ký tự điều khiển, vô hình, đảo hướng). Hiện chữ thuần là việc T-101 |
| **LC-T094-18** (nguồn Sheet) | **Đạt, trừ LC-T100-1** | Vùng đọc cố định ≤ 26 cột, ≤ 1.001 dòng; client kiểm kiểu từng ô, thân trả lời ≤ 2 MB (T-097); ô qua `parse._cell` (≤ 2.000 ký tự, báo). Quá 1.000 dòng thì im lặng cắt: LC-T100-1 |
| **LC-T094-28** Ghi Sheet | **Đạt, trừ LC-T100-1, -3** | Chỉ cột của `SHEET_COLUMNS` tìm **theo tên trên bản vừa đọc**; dòng theo Mã bài (đúng một dòng; trùng → không ghi); so ô sắp ghi, Mã bài, Từ khóa với bản gốc theo bản đồ cột của từng bản (đổi chỗ cột không làm so sai); ô đã đúng giá trị đề xuất thì tính là đã ghi; lệnh ghi ô chạy **trước** lệnh thêm dòng trong một lần áp dụng (số dòng còn đúng); không lệnh xóa dòng, cột; `RAW` chặn ở lớp kiểm của client (`sheets.py:417-421`); `safe_text` (`sync.py:945`) thêm dấu cách trước chữ mở đầu `=` `+` `-` `@` tab CR (ô đầy thì bỏ các ký tự đó); giờ ghi `_moment_text` có `+07:00`, từ `datetime.now(model.TIMEZONE)`; ngày là số ngày của Sheets, Mã bài WordPress là số |
| **LC-T094-29** Cache | **Đạt** | SQL chỉ tham số `?`; mỗi thao tác: `PRAGMA trusted_schema = OFF`, giới hạn bước máy ảo, kiểm `sqlite_master` (đúng 2 bảng, không trigger, khung nhìn, chỉ mục) **trong cùng giao dịch** (`plan_cache.py:208-232`); ghi đè trong một giao dịch `BEGIN IMMEDIATE` (nguyên tử); liên kết tắt hay file hỏng, lạ → xóa (chỉ xóa chính liên kết); giới hạn từng dòng, tổng, số dòng; mã băm toàn bộ ô phải khớp; lưu **mã băm SHA-256** của mã Sheet, không lưu mã gốc, khóa, mã truy cập; mọi dòng đọc lại qua `PlanRow`; `apply_proposals`, `write_status`, `open_row`, `prepare_sheet` luôn đọc lại Sheet |
| **LC-T094-30** Kho nháp | **Đạt, trừ LC-T100-3** | Khuôn 3; khuôn 1, 2 vẫn mở (khuôn 2 giữ ảnh); phần `plan` sai khuôn thì bỏ, nháp vẫn mở; `SendState` thêm trường có mặc định, kiểm khớp nhau; dòng trạng thái gửi cũ đọc được; dòng hỏng vẫn ném `DraftError` (đóng an toàn như T-089); so rồi đặt của T-089 giữ nguyên. Việc ghi Sheet còn nợ ở bảng `plan_writes` của `drafts.sqlite`, so rồi đặt / so rồi xóa trong `BEGIN IMMEDIATE`, tối đa 200 việc; `retry_pending` chỉ gọi `write_status`, lọc theo mã băm Sheet |
| **LC-T094-31** «Chuẩn bị trang tính» | **Đạt** | Chỉ khi gọi `prepare_sheet`; 4 loại yêu cầu trên đúng `sheetId` tab «KeHoach» vừa đọc (client kiểm lại); tiêu đề thiếu ghi vào cuối dòng 1 sau ô có chữ cuối cùng, quá 26 cột thì từ chối; danh sách chọn là hằng của code |
| **LC-T094-11** (SL-T097-5) | **Đạt** | `_inside_by_identity` đi ngược theo đường **thật** (`resolve`); hai đường thật khác chữ ổ thì không so danh tính (ổ Google Drive for Desktop). Thử thật trên máy: khóa gõ qua ổ ảo `subst X:` trỏ vào thư mục dự án → `resolve` ra đường thật, **vẫn bị nhận là trong dự án** (cả hai chiều); ổ ảo đã gỡ. Cách viết `\\localhost\D$`, `\\?\Volume{…}` vẫn so danh tính (test SL-T097-3 của T-097) |
| **LC-T103-1** (G2) | **Đóng khi gỡ dấu** | `WARN_PRICE` cho chữ AI đổi có giá, không tick sẵn; 5 ca `xfail` LC-T103-1 (đã trên `main`) qua với code T-100 → XPASS khi gộp, gỡ dấu (R5). Cách viết giá còn lọt: LC-T100-2 |

## Thử tấn công và kiểm (không gọi Google, WordPress, AI thật)

Script ở thư mục nháp của phiên, bản sao trong thư mục ghi chú chung `T-100-la-chan-scripts/`. Chạy trong worktree: `PYTHONUTF8=1 uv run python <script>`.

**Dữ liệu Sheet chưa tin cậy.** Ô có công thức: client đọc `UNFORMATTED_VALUE` (giá trị đã tính, không đọc chữ công thức), app không bao giờ ghi công thức (`RAW` + `safe_text`). Chữ độc, ký tự lạ, ô rất dài: qua `PlanRow` (≤ 2.000 ký tự/ô), cache giữ ô thô có giới hạn. Dòng giả: Mã bài gõ khác dạng (`b-1`, `B-0001`) chuẩn hóa về một mã → trùng → không ghi dòng đó, có câu báo. Đổi cấu trúc cột: cột tìm theo tên ở mỗi lần đọc; thiếu cột cần ghi → `Conflict`, thiếu Mã bài / Từ khóa → `SheetPlanError` trước khi ghi. Sheet dài hơn vùng đọc: **LC-T100-1**.

**Không thêm trùng, không ghi đè sai.** «Chưa rõ» khi ghi ô: báo «chưa rõ», lần sau ô đã đúng giá trị thì tính là đã ghi. «Chưa rõ» khi thêm dòng: đọc lại tìm Mã bài, không bao giờ tự thêm lại (trừ Sheet đầy: LC-T100-1). Xung đột: ô sắp ghi, Mã bài, Từ khóa khác bản gốc → không ghi, trả «trước / bây giờ / đề xuất». Cache cũ: bản người dùng xem từ cache vẫn bị so với bản đọc lại; mã mới cấp từ cache cũ mà đã có trên Sheet → `CONFLICT_EXISTS`. Ghi trạng thái: không lùi, «Bỏ» / chữ lạ / Mã bài WordPress lạ → không ghi. Ghi sang Sheet khác: **LC-T100-3**.

**Cache trên máy.** Ghi nguyên tử (một giao dịch); file hỏng, sửa tay, có trigger, sai mã băm → bỏ cả cache (`test_plan_cache.py` 29 ca của Thợ Máy, Soi Lỗi thử khóa EXCLUSIVE, hỏng giữa file, chỉ đọc). Không bí mật. Quyền file: mặc định như `drafts.sqlite`, `image_tags.sqlite` (chỉ `.env` đặt 600); `data/`, `*.sqlite` đã bị `.gitignore` chặn (Quan sát 2).

**Kho nháp khuôn 3.** Nháp khuôn 1, 2 mở được, lưu lại thành khuôn 3 giữ mọi khóa cũ (test của Thợ Máy, Soi Lỗi); `SendState` mới không đổi cách so rồi đặt; dòng hỏng đóng an toàn. `find_plan_draft` lọc bằng `instr` trên JSON gọn (dấu ngoặc kép trong chữ bài luôn được ghi thoát) rồi mở lại để xác nhận.

**G2.** `probe_price.py`: lọt 11/20 cách viết giá (**LC-T100-2**). Giá nằm trong từ khóa chính (kể cả từ khóa AI đề xuất) không cảnh báo: đúng chính sách của bước SEO (Quan sát 4).

## Xếp mức 3 lỗi Thấp của Soi Lỗi

| Mã | Ý kiến Lá Chắn |
|---|---|
| SL-T100-1 («45 Đ. Số 7», «12 K. Lê Duẩn» bị coi là giá) | **Giữ Thấp**, không phải lỗi bảo mật: báo thừa theo hướng an toàn (không tick sẵn) |
| SL-T100-2 («2 nghìn công trình», «3 triệu lượt xem») | **Giữ Thấp**, như trên |
| SL-T100-3 (cắt khúc 900/700 làm mất phần loại trừ từ khóa) | **Giữ Thấp**, như trên |

Cả ba nên sửa cùng LC-T100-2 (cùng `_has_price`): báo oan nhiều thì người dùng quen bỏ qua cảnh báo giá. Test canh của tôi giữ cho cách sửa không coi số đếm là giá.

Góp ý G1 của Soi Lỗi («Thêm» chưa có Mã bài bị thêm trùng khi «chưa rõ»; hiện chưa đường nào dựng ra): đồng ý, nên chặn ngay trong `_addition` ở cùng lượt sửa (một dòng, cùng loại với LC-T100-1). G2–G4: không phải bảo mật.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (`PYTHONUTF8=1`) trên 19 file đổi, bản vá nhánh, file test mới, kèm file mồi tiếng Việt: mồi bắt 2/2; chỉ khóa **giả** có từ trước trong `test_soi_loi_t016_t020.py` (mục Báo nhầm). Lịch sử `b241e79..07bca14`: 0 dạng khóa thật, 0 `"type": "service_account"` |
| S2 | Đạt | LC-T094-2 |
| S3 | Không áp dụng | Không biến `.env` mới |
| W1–W4 | Không áp dụng | Không gọi WordPress |
| A1–A3 | Đạt (A2: LC-T100-2) | Không lời dặn AI mới; chữ Sheet vào lời dặn đã qua khung (T-098, T-103) |
| U1–U3 | Không áp dụng | Không đổi `app/` |
| F1 | Đạt | Cache ở `data/plan_cache.sqlite` cố định; liên kết tắt → xóa chính liên kết; khóa file: LC-T094-11 |
| F3 | Đạt | SQLite chưa tin cậy: kiểm cấu trúc, `trusted_schema = OFF`, giới hạn |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi, đã chặn `data/`, `*.sqlite` |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, worktree `wt-T-100` tại `07bca14`; có nhiều phiên khác chạy test song song.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 19 file đổi, bản vá nhánh, `tests/test_la_chan_t100.py`, **file mồi tiếng Việt**: mồi bắt **2/2**; file thật: 8 mục ở `test_soi_loi_t016_t020.py` + 1 dòng ngữ cảnh của bản vá (khóa giả có từ trước). Quét lại biên bản này và file test cùng file mồi mới: 0 mục, mồi 2/2 | Có. Đã xóa cả hai file mồi |
| bandit 1.9.4 | `PYTHONUTF8=1`, 5 module đổi (3.469 dòng): 3 mục Thấp đều có từ trước (Báo nhầm) | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p b241e79..07bca14`: 0 dạng khóa thật | Có |
| pytest (nhánh) | `tests/test_la_chan_t100.py`: 2 passed, **12 xfailed**; `--runxfail`: 12 ca hỏng đúng chỗ (mục Lỗi) | Có |
| ruff | `ruff check`, `ruff format --check` file test mới: sạch; cả cây gộp: dưới | Có |
| Thử gộp | `main` trên máy `209615a` (có T-103, T-091, T-096 lượt 5) + `07bca14`: `git merge-tree --write-tree` **không xung đột** (cây `e6c8c0e`); hai bên không sửa chung file nào. Commit tạm `69dc232` trong worktree riêng (`git commit-tree`, không nhánh, đã gỡ), thêm `tests/test_la_chan_t100.py`: `ruff` cả cây sạch; 32 file test kế hoạch, Google, kho nháp, gửi nháp (T-086, T-089), lời dặn T-103, `test_app_pages.py`: **2.411 passed, 10 skipped, 22 xfailed** (12 của tôi, 10 của Soi Lỗi), **5 failed = đúng 5 ca `xfail(strict=True)` LC-T103-1 nay qua** (code T-100 đã cảnh báo giá; gỡ dấu khi gộp, điều kiện 4), 17 phút 7 giây (máy chạy song song nhiều lượt test khác) | Có |

## Quan sát (không tính là lỗi)

1. **Khe dòng dời chỗ:** giữa lần đọc lại và lệnh ghi (1–2 giây), ai đó sắp xếp hay chèn dòng trên Google Sheets thì lệnh ghi theo số dòng rơi vào dòng khác. Cùng loại với khe «ghi cùng một ô» thiết kế 2.5 đã nhận (T-094 Ghi nhận 2), nhưng hậu quả là ô của bài khác bị ghi. Sheets không có lệnh ghi có điều kiện. Có thể đọc lại sau khi ghi, so ô Mã bài của các dòng vừa ghi, khác thì báo (phiếu sau). Không phải lỗi bảo mật.
2. **Quyền file cache:** `data/plan_cache.sqlite` giữ mọi ô của Sheet, kể cả «Ghi chú của thợ» (có thể có tên, số điện thoại khách). Quyền mặc định như `drafts.sqlite`, `image_tags.sqlite`; không khóa, không mã Sheet; `.gitignore` chặn. README có thể nhắc: máy dùng chung tài khoản Windows thì người khác đọc được.
3. **Công thức trong ô Sheet:** app đọc giá trị đã tính, nên ô `=IMPORTXML(…)` đưa được chữ từ trang ngoài vào kế hoạch. Vẫn là chữ chưa tin cậy (`PlanRow`, khung lời dặn AI); ai sửa được Sheet thì vốn sửa được chữ đó.
4. **Giá trong từ khóa chính:** `_has_price` không tính chỗ nằm trong từ khóa, kể cả từ khóa AI đề xuất («báo giá cổng inox giá rẻ», có test của Thợ Máy). Khớp chính sách bước SEO (T-040, T-041); từ khóa là ô hiện rõ nhất trong bảng duyệt.
5. Kho nháp `drafts.sqlite` không kiểm trigger, khung nhìn như cache (có từ T-016); T-100 thêm bảng `plan_writes` theo cùng cách. File nằm trên máy; không do T-100.

## Báo nhầm đã loại

- detect-secrets «Secret Keyword», «Base64 High Entropy String» ở `tests/test_soi_loi_t016_t020.py:40, 71, 99, 102, 123, 370, 381, 747` và một dòng ngữ cảnh (không đổi) của bản vá có khóa giả dạng `sk-ant-…`: khóa **giả** của test có từ trước (bản gốc `b241e79` có đúng 8 mục ở cùng dòng); T-100 chỉ đổi dòng 744.
- bandit B105 `seo_app/google/service_account.py:45` (`TOKEN_URI`), `:110` (câu báo có chữ «token_uri»): có từ T-097, là địa chỉ và câu báo, không phải mật khẩu. B101 `seo_app/storage/drafts.py:894` (`assert`, có từ 14/10).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-100 vào `main`.

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T100-1:** vùng đọc đầy → câu báo, không thêm dòng mới, `_key_present` trả «chưa rõ»; gỡ 3 `xfail` khi XPASS. Kèm G1 của Soi Lỗi (chặn «Thêm» chưa có Mã bài trong `_addition`) | Thợ Máy (lượt sửa T-100) | Trước khi T-101 nối «Áp dụng» |
| 2 | **LC-T100-2** cùng SL-T100-1 → -3 (một hàm `_has_price`); giữ test canh số đếm | Thợ Máy (lượt sửa T-100) | Trước khi T-101 hiện đề xuất AI tick sẵn |
| 3 | **LC-T100-3:** so mã băm Sheet của nháp trước khi ghi trạng thái | Thợ Máy (lượt sửa T-100) | Trước khi T-102 gọi `record_status` |
| 4 | Khi gộp `main` vào `team/T-100`: 5 ca `xfail` LC-T103-1 (`tests/test_la_chan_t103.py`) XPASS → gỡ đúng 5 dấu (R5), như Thợ Máy đã định | Thợ Máy | Lượt sửa sau Lá Chắn |
| 5 | **T-101:** hiện chữ Sheet, `Conflict.now` bằng chữ thuần (LC-T094-3); giữ `listing.plan` (bản người dùng đã xem) trong `session_state` tới lúc «Áp dụng»; không tự dựng `Proposal` ngoài `compare_rows` / `from_ai`. **T-102:** `find_plan_draft` với mã băm Sheet đang dùng; chỉ gọi `record_status` sau khi sửa điều kiện 3 | T-101, T-102 | Khi làm các phiếu đó |
| 6 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

3 lỗi Thấp đều có lượt sửa, không cần chủ dự án chấp nhận rủi ro; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

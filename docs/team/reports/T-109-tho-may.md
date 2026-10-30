# Báo cáo T-109 · Lõi: đưa trạng thái bài trên website về Google Sheets

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | T-109 `T-109-dong-bo-trang-thai-website-ve-sheet.md` (Chỉ Huy commit lên `main`, nhánh này không chứa) |
| Nhánh | `team/T-109` (từ `main` `eef13b5`) |
| Ngày nộp | 2026-10-30 22:32 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đã làm phần lõi cho nút **«Cập nhật trạng thái từ website»** ở trang Kế hoạch. Phần mềm hỏi website trạng thái các bài đã gửi, rồi đề xuất sửa cột Trạng thái trên Google Sheet:
  - bài hẹn giờ đã lên: «Đã hẹn giờ» → «Đã đăng»;
  - bài anh/chị tự hẹn giờ trong trang quản trị WordPress: «Đã gửi nháp» → «Đã hẹn giờ», kèm giờ hẹn;
  - giờ hẹn bị đổi trong trang quản trị: sửa ô «Ngày đăng thực tế».
- Bài hẹn giờ quá 15 phút mà chưa lên có nhãn **«Lỡ lịch»** kèm cách xử lý.
- Phần mềm **chỉ cảnh báo, không tự sửa Sheet** khi bài bị xóa, nằm trong thùng rác, về nháp, để riêng tư, hay dòng ghi «Bỏ» mà bài vẫn còn.
- Không bao giờ lùi trạng thái, không thêm hay xóa dòng; chỉ ghi khi anh/chị bấm. Dòng vừa bị sửa trên Sheet (ở máy khác hay sửa tay) thì không ghi đè. Sheet trong Cài đặt vừa đổi thì không ghi gì.
- Chưa có nút trên giao diện: nối nút ở lượt sau của T-101 hoặc T-102.

## Kế hoạch đã làm

1. Hàm thuần `check_website` (không mạng): so kết quả `WordPressClient.post_statuses` với các dòng đã nối bài (cột «Mã bài WordPress», T-100), trả danh sách thay đổi có kiểu và danh sách cảnh báo.
2. Hàm ghi `apply_website_changes`: dùng lại các bước của đường ghi T-100 (so mã băm Sheet, đọc lại, tìm dòng theo Mã bài, so từng ô với bản đã xem, `update_cells` luôn `RAW`).
3. Làm ở **mô-đun mới** `seo_app/plan/website.py`. Mô-đun dùng các hàm có sẵn của `sync.py`, **không sửa** `sync.py`, nên không đổi hàm dùng chung nào; nơi gọi cũ không bị ảnh hưởng (bài học T-091, T-101).
4. Test trên Sheet giả của T-100 (`FakePlanSheet`), đi qua đúng `SheetsClient` thật.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/website.py` (mới) | `check_website(plan, states, asked, *, sheet_id, now)` → `WebCheck` (`updates`: `WebUpdate`; `notices`: `WebNotice`; mã băm Sheet; giờ kiểm). `apply_website_changes(client, check, updates=None, *, sheet_id, now)` → `WebApplyResult` (`written`, `already`, `conflicts`, `unsure`, `not_written`, `error`, `message`). Hằng `LATE_AFTER = 15 phút`; câu báo cố định |
| `tests/test_t109_website_status.py` (mới) | 30 hàm test, 68 ca |

### Quy tắc so (Sheet → website)

Chỉ xét dòng có Mã bài WordPress nằm trong danh sách đã hỏi. Thứ tự trạng thái: `Chưa viết` → `Đang viết` → `Đã gửi nháp` → `Đã hẹn giờ` → `Đã đăng`, chỉ đi tới.

| Website | Sheet đang ở | Kết quả |
|---|---|---|
| `publish` | trước «Đã đăng» | Đề xuất **«Đã đăng»**; «Ngày đăng thực tế» = giờ đăng trên website |
| `publish` | «Đã đăng», ngày khác | Đề xuất sửa **ngày** (`DATE`) |
| `future` | trước «Đã hẹn giờ» | Đề xuất **«Đã hẹn giờ»** + giờ hẹn (bài tự hẹn trong trang quản trị, câu hỏi 5A) |
| `future` | «Đã hẹn giờ», giờ khác | Đề xuất sửa **ngày** (hẹn lại trong trang quản trị) |
| `future` | «Đã đăng» | Cảnh báo `AHEAD`, không ghi |
| `future`, quá giờ hẹn > 15 phút | bất kỳ | Thêm cảnh báo **«Lỡ lịch»** (nhãn, không ghi Sheet) kèm hướng dẫn cron |
| `draft`, `pending` | «Chưa viết», «Đang viết» | Đề xuất **«Đã gửi nháp»** |
| `draft`, `pending` | «Đã hẹn giờ», «Đã đăng» | Cảnh báo `BACK_TO_DRAFT` (bài về nháp), không ghi |
| `private` | bất kỳ | Cảnh báo `PRIVATE`, không ghi |
| bất kỳ | «Bỏ» | Cảnh báo `DROPPED`, không ghi |
| Không có trong kết quả (đã xóa, thùng rác, không còn quyền xem) | bất kỳ | Cảnh báo `MISSING`, không ghi (thiết kế 1.7) |
| Mục website sai khuôn (trạng thái lạ như `trash`, `inherit`; mã không khớp) | bất kỳ | Coi như không thấy: `MISSING` |
| Giờ website sai khuôn hay ngoài năm 2020–2035 | | Vẫn đổi trạng thái, **không** ghi ngày, cảnh báo `ODD_DATE` |
| Một bài nối nhiều dòng (đếm trên mọi ô đã đọc, cả dòng trùng Mã bài), Mã bài trùng, dòng chưa có Mã bài | | Cảnh báo `SHARED_POST`, `DUPLICATE_KEY`, `NO_KEY`; không đề xuất gì |

### Đường ghi (yêu cầu 2)

1. `updates` phải là thay đổi của chính lần kiểm. Giao diện không tự dựng được `WebUpdate`; sai hay trùng thì `ValueError`, chưa ghi gì.
2. So mã băm Sheet bằng `_connected_hash` của T-100 (cùng cách `write_status`, LC-T100-3, SL-T100-4). Sheet đang nối khác Sheet đã kiểm thì `SheetPlanError`: chưa đọc, chưa ghi.
3. Đọc lại cả tab (`read_sheet`). Thiếu cột Mã bài, Trạng thái hay Mã bài WordPress thì `SheetPlanError`, chưa ghi gì.
4. Với mỗi thay đổi:
   - tìm dòng theo **Mã bài**: không thấy, trùng mã, hay Sheet đầy 1.000 dòng mà không thấy dòng thì `WebConflict`;
   - so ô Trạng thái, Mã bài WordPress, Ngày đăng thực tế với bản người dùng đã xem: khác thì `WebConflict`, câu báo nêu tên cột chuẩn;
   - Sheet đã đúng giá trị mới thì xếp vào `already`.
5. Ghi bằng `update_cells` (luôn `RAW`), chỉ 3 ô: Trạng thái, Ngày đăng thực tế, Cập nhật lúc. Mỗi lệnh tối đa `MAX_UPDATES` ô; các ô của một dòng không bị tách sang hai lệnh.
   - Không ghi Mã bài WordPress (đó là ô dùng để nối dòng với bài).
   - Không thêm dòng, không xóa gì.
6. Lệnh ghi lỗi:
   - không chắc đã ghi chưa (`unsure`): **không tự ghi lại**, câu báo dặn kiểm lại; lần kiểm sau đọc lại và so như trên;
   - lỗi chắc chắn chưa ghi: dừng, các dòng còn lại vào `not_written`.

Vì sao không gọi `write_status` cho từng dòng: hàm đó đọc lại cả Sheet **mỗi lần gọi**, nên 50 dòng thành 50 lần đọc. Hàm đó cũng ghi thêm Mã bài WordPress, và không so ô Ngày đăng thực tế với bản đã xem. Ở đây đọc lại **một lần** rồi ghi theo lô, như `apply_proposals`.

### An toàn (yêu cầu 3; LC-T094 «Chung», điều kiện T-100, T-101)

- **Dữ liệu website chưa tin cậy.** Mỗi mục trong `states` phải đúng mã đã hỏi và có `id` trùng khóa. Trạng thái chỉ nhận 5 giá trị (`POST_STATUSES` của client). `date_gmt` phải đúng 19 ký tự `YYYY-MM-DDTHH:MM:SS` và nằm trong khoảng năm của kế hoạch. Mã đã hỏi chỉ nhận số nguyên dương thật, không nhận `bool` hay chữ.
- **Dữ liệu Sheet chưa tin cậy.** Mọi dòng qua `parse_sheet`/`PlanRow` (T-100). Mã lạ trong cột Mã bài WordPress (chữ, 0, số âm, quá lớn, số lẻ, công thức) làm dòng không đọc được, nên không nối và không đề xuất gì.
- **LC-T094-2.** Câu báo là câu cố định: chỉ có Mã bài chuẩn hóa, mã bài WordPress (số), số dòng, nhãn trạng thái chuẩn, giờ do app định dạng. Không chép chữ ô Sheet hay lời website; test gài chuỗi mồi vào ô và lời Google.
- **LC-T101-1, LC-T094-28.** `WebUpdate` không mang chữ ô Sheet: trạng thái cũ/mới là nhãn chuẩn của code, ngày là `datetime`. Giá trị ghi lên Sheet là nhãn của code và giờ do app dựng (`2026-11-05 09:00+07:00`), nên không bao giờ mở đầu bằng `=`, `+`, `-`, `@`; test kiểm từng ô đã ghi. Bảng hiện các thay đổi này trên giao diện vẫn phải là chữ thuần (LC-T094-3, việc của T-101/T-102).
- **LC-T094-1.** Test không gọi Google, WordPress thật.

## Cách giao diện dùng (cho T-101 lượt sau / T-102)

```python
ids = sorted({row.plan.wp_post_id for row in plan.rows if row.plan.wp_post_id})
states = wp_client.post_statuses(ids)  # chỉ đọc
result = website.check_website(plan, states, ids, sheet_id=settings.google_sheet_id)
# hiện result.updates (label, reason, status_before → status_after, published_*) và result.notices
# (message) bằng chữ thuần; người dùng tick → chosen ⊆ result.updates
outcome = website.apply_website_changes(sheets_client, result, chosen,
                                        sheet_id=settings.google_sheet_id)
# outcome.message; SheetPlanError / SheetsError: câu cố định, chưa ghi gì
```

- `check_website` không cần mạng, gọi được ngay sau `post_statuses`. `result.late` cho nhãn «Lỡ lịch».
- `app/views/plan.py` và `app/views/home.py` đang có hằng `LATE_AFTER` và cách tính «Lỡ lịch» riêng (T-101). Khi nối nút, nên dùng `website.LATE_AFTER` / `result.late` để hai chỗ không lệch nhau (`app/**` ngoài phạm vi phiếu này).

## Kiểm thử

- `tests/test_t109_website_status.py`: **68 qua**. Phủ đủ các ca yêu cầu 4:
  - bài đã đăng, đã hẹn giờ (kể cả tự hẹn trong trang quản trị, hẹn lại);
  - lỡ lịch: biên 14, 15, 16 phút và 1 ngày;
  - bị xóa, thùng rác, không còn quyền đọc;
  - về nháp, riêng tư, «Bỏ»;
  - mục website lạ (`trash`, `auto-draft`, `inherit`, `PUBLISH`, mã không khớp, `id=True`, chữ, `None`), giờ lạ (6 dạng);
  - mã lạ trên Sheet (7 dạng); mã hỏi sai kiểu;
  - một bài nối nhiều dòng (cả dòng trùng Mã bài bị ẩn), dòng chưa có Mã bài;
  - **Sheet đổi giữa chừng**: sửa Trạng thái, Mã bài WordPress, Ngày đăng thực tế (cả chữ lạ); máy khác đã ghi đúng giá trị mới; dòng bị xóa, đổi Mã bài, nhân đôi; đổi Sheet; cột bị đổi tên;
  - lỗi ghi `unsure` (không tự ghi lại; lần kiểm sau thấy Sheet đã đúng), lỗi 403, lỗi đọc lại;
  - ghi theo lô và dừng sau lỗi; chỉ ghi đúng thay đổi đã chọn; thay đổi giả hay trùng bị từ chối;
  - câu báo không chép chữ ô; ô ghi không thành công thức; `RAW`, không thêm dòng.
- 12 file test liên quan (T-109, `test_plan_sync`, `test_soi_loi_t100`, `test_la_chan_t100`, `test_t100_drafts_plan`, `test_t100_google_identity`, `test_plan_model`, `test_plan_parse`, `test_plan_cache`, `test_plan_propose`, `test_t101_plan_page`, `test_google_sheets`): **1025 qua, 0 hỏng**.
- `uv run ruff check .`: All checks passed. `ruff format --check` 2 file mới: sạch. Quét ký tự vô hình trần và `detect-secrets` (`PYTHONUTF8=1`) 2 file mới: sạch.
- Máy đang chạy toàn bộ test nên chỉ chạy test chọn lọc như dặn.

## Ghi nhận

- Khe hở đã biết của T-100 vẫn áp dụng (thiết kế 2.5): hai máy ghi **cùng một ô** trong 1–2 giây giữa lần đọc lại và lệnh ghi thì bản ghi sau thắng. Sheets không có lệnh ghi có điều kiện.
- `pending` (chờ duyệt) được coi như nháp. Tài khoản Biên tập viên của app không tạo bài `pending`; chỉ gặp khi có người đổi trong trang quản trị.

## Lượt 2 · SL-T109-1 → -3, góp ý G3 → G6 (Soi Lỗi `09870bd`, Lá Chắn `a40a107`)

Ngày nộp lượt 2: 2026-10-30 23:45 (+07:00, theo lệnh `date`). Chỉ Huy B giao 23:45; nhánh từ `a40a107`.

### Tóm tắt (cho chủ dự án)

Sửa 3 lỗi nhỏ, đều chỉ gặp khi ô trên Google Sheet được gõ lạ. Không lỗi nào làm mất dữ liệu.

- **Mã bài, Mã bài WordPress có nhiều dấu cách hay ký tự vô hình ở đầu ô.** Trước đây phần mềm có thể đọc ô đó khác với bảng anh/chị đang xem: không thấy dòng trùng, rồi ghi vào dòng mà bảng đang ẩn. Nay mọi chỗ đọc lại một ô đều đọc giống hệt bảng. Lúc ghi còn kiểm thêm: dòng tìm được phải đúng là dòng trong bảng, khác thì không ghi.
- **Ô Trạng thái hay Ngày đăng thực tế gõ chữ tự do (ví dụ «Xong rồi», «hôm qua»).** Phần mềm không đề xuất gì cho dòng đó, chỉ nhắc đúng ô cần sửa. Trước đây nó đề xuất rồi lần nào ghi cũng báo sai lý do «vừa bị sửa ở nơi khác».
- Thêm 4 góp ý nhỏ:
  - lần kiểm cũ quá 5 phút thì phải kiểm lại rồi mới ghi;
  - dòng «Bỏ» mà bài đã xóa thì không nhắc nữa;
  - thiếu cột thì báo ngay khi bấm kiểm;
  - giờ đăng lệch website dưới 2 phút thì coi như đúng.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/sync.py` | **Sửa tận gốc SL-T109-1, -2:** thêm `_reader_text` (chữ ô đúng như bộ đọc bảng `parse._cell`: tối đa `MAX_CELL_CHARS` = 2.000 ký tự, làm sạch **sau**). `_key_of`, `_post_id_of`, `_status_of` đọc qua đó, thay vì cắt 30 / 30 / 100 ký tự **trước** khi làm sạch |
| `seo_app/plan/website.py` | Chi tiết ở bảng dưới |
| `tests/test_soi_loi_t109.py` (của Soi Lỗi) | Gỡ 3 dấu `xfail(strict=True)` (SL-T109-1, -2, -3): 6 ca XPASS. Chỉ xóa dòng dấu (R5) |
| `tests/test_t109_website_status.py` (của Thợ Máy) | Thêm 8 hàm test, 21 ca (mục Kiểm thử) |

Các thay đổi trong `seo_app/plan/website.py`:

| Mục | Thay đổi |
|---|---|
| SL-T109-1 | Lúc kiểm: Mã bài không ứng đúng một dòng (`key_rows[key] != (số dòng,)`) thì chỉ cảnh báo `UNSURE_ROW`. Lúc ghi (`_cells_for`): `fresh.find(key)` phải có và đúng số dòng của `key_rows`, như `sync.open_row`; khác thì `WebConflict` |
| SL-T109-3 | Lúc kiểm, đọc ô Trạng thái, Ngày đăng thực tế bằng **đúng hàm lúc ghi** (`_status_of`, `_moment_of` trên ô gốc); `*_before` lấy từ đó. Ô không đọc được thì cảnh báo `ODD_CELL`: «Ô «Trạng thái» / «Ngày đăng thực tế» của dòng … không đọc được…». Không đề xuất, vì ghi đè chữ người dùng gõ là không an toàn. `_moment_of` cũng đọc qua `_reader_text` |
| G3 | Dòng «Bỏ» mà website không trả bài: không cảnh báo |
| G4 | `CHECK_MAX_AGE = 5 phút`. `apply_website_changes` từ chối lần kiểm cũ hơn, hay giờ máy lùi quá 1 phút so với lúc kiểm: `SheetPlanError(MSG_STALE)`, chưa đọc, chưa ghi (điều kiện 1c của Lá Chắn làm ngay ở lõi) |
| G5 | `check_website` thiếu cột Mã bài, Trạng thái hay Mã bài WordPress thì `SheetPlanError` ngay, cùng câu `MSG_NO_COLUMNS` như lúc ghi |
| G6 | `DATE_TOLERANCE = 2 phút` (mức lệch đồng hồ thiết kế 3.1 cho phép). Giờ website lệch ô Ngày đăng thực tế không quá 2 phút thì coi như cùng giờ: không đề xuất sửa ngày, đổi trạng thái thì giữ nguyên ô ngày |

Ô ODD_DATE không còn đi kèm dòng chỉ có cảnh báo («Bỏ», riêng tư, về nháp): một dòng một câu báo.

### Nơi gọi hàm dùng chung đã đổi (bài học T-041, T-091)

`grep -rn "_key_of\|_post_id_of\|_status_of" seo_app app tests`. Nơi gọi `_key_of`, `_post_id_of`, `_status_of`:
- `sync.parse_sheet` (`key_rows`, dùng cho đề xuất T-100/T-101, `open_row`, `write_status`, `_key_present`);
- `sync._fresh_row` (áp dụng đề xuất cho dòng chưa có mã);
- `sync.write_status`, `record_status`, `retry_pending` (T-100, T-102 sẽ gọi);
- `website.py`.

`app/` không gọi trực tiếp; trang Kế hoạch (T-101) dùng qua `read_sheet`/`get_plan`/`open_row`.

Hành vi đổi theo hướng khớp bộ đọc bảng: dòng có Mã bài gõ sau nhiều ký tự trắng nay vào `key_rows`, nên tìm được khi ghi trạng thái. Test mới `test_t100_status_write_finds_row_with_leading_blanks`: trước đây báo «Không còn thấy dòng». Không test cũ nào ghim cách cắt 30 ký tự (đã grep `tests/`); chạy test của mọi nơi gọi ở mục Kiểm thử.

### Không làm (ghi lý do)

- ~~Nửa sau của G6~~: Chỉ Huy duyệt 31/10 00:45, đã làm (mục «Bổ sung lượt 2» dưới).
- **G2** (`states` sai kiểu): Chỉ Huy quyết 31/10 để lượt nối nút (điều kiện 1b của Lá Chắn), không làm ở T-109.

### Kiểm thử lượt 2

- `tests/test_t109_website_status.py` + `tests/test_soi_loi_t109.py`: **141 qua, 0 hỏng**. 6 ca của Soi Lỗi trước là `xfail` nay qua thật.
- Test mới lượt 2 (21 ca):
  - `_key_of`, `_post_id_of`, `_status_of` đọc ô có 40 dấu cách, 40 ký tự vô hình, 1.500 dấu cách ở đầu giống bộ đọc bảng;
  - `write_status` của T-100 tìm được dòng như vậy;
  - hai cách tìm dòng lệch nhau thì cảnh báo lúc kiểm, xung đột lúc ghi;
  - ô Trạng thái «Xong rồi», chữ mồi, ô Ngày «hôm qua»: chỉ cảnh báo, câu nêu đúng ô, không chép chữ ô;
  - dòng «Bỏ», bài đã xóa: không cảnh báo;
  - lần kiểm cũ 0 / 5 / 6 / 60 phút, giờ máy lùi 2 phút: cũ thì từ chối trước khi đọc Sheet;
  - thiếu từng cột Mã bài, Trạng thái, Mã bài WordPress: báo lúc kiểm;
  - giờ lệch 1, 2, 3 phút hai phía.
- Test liên quan: 25 file. Gồm T-097 (`test_google_sheets`, `test_la_chan_t097`, `test_soi_loi_t097`), T-098 (`test_plan_model`, `test_plan_parse`, `test_plan_propose`, `test_plan_ai`, `test_soi_loi_t098`), T-100 (`test_plan_sync`, `test_plan_cache`, `test_t100_drafts_plan`, `test_t100_google_identity`, `test_soi_loi_t100`, `test_la_chan_t100`), T-101 (`test_t101_plan_page`, `test_t101_home_page`, `test_t101_settings_google`, `test_soi_loi_t101`, `test_la_chan_t101`), T-103 (`test_t103_plan_prompt`, `test_soi_loi_t103`, `test_la_chan_t103`), T-109 (2 file), `test_wordpress_release`. Kết quả: **2286 qua, 2 xfail, 0 hỏng, không XPASS** (5 phút 28 giây). 2 xfail là LC-T101-1, có từ trước, sửa ở T-102.
- `uv run ruff check .`: All checks passed. `ruff format --check` các file đã sửa: sạch.

### Bổ sung lượt 2 · nửa sau G6 (Chỉ Huy duyệt 31/10 00:45)

- `check_website`: bài `future` / `publish` mà website không trả giờ thì cũng là giờ lạ. `post_statuses` (T-099) đổi giờ sai khuôn thành chuỗi rỗng, nên chuỗi rỗng ở hai trạng thái này nghĩa là giờ hỏng. Cảnh báo `ODD_DATE` là câu cố định, không chép giá trị website. Trạng thái vẫn được đề xuất đổi, ô ngày không ghi. Bài nháp, chờ duyệt, riêng tư không có giờ thì không báo. Dòng chỉ có cảnh báo («Bỏ», riêng tư…) không báo thêm.
- Ca test cũ đổi kỳ vọng (Chỉ Huy duyệt 31/10 00:45, R5):

| Ca | Cũ | Mới |
|---|---|---|
| `test_soi_loi_t109.py::test_odd_website_values_never_crash_late_or_leak` | cảnh báo giờ lạ đúng các bài `range(401, 407)`: bài 407 (hẹn giờ, `date_gmt=None`) **không** có | `range(401, 408)`: bài 407 **có** cảnh báo giờ lạ. Mọi kiểm khác của ca giữ nguyên: dưới 2 giây, không «Lỡ lịch», không ghi ngày, đúng 7 đề xuất, 408–410 là «không thấy», không lộ chữ |

- Test mới: `test_scheduled_or_published_without_date_is_odd_date` (2 ca) và `test_draft_without_date_is_not_odd` (3 ca).
- Chạy lại: 2 file T-109 **146 qua**. Bộ 25 file liên quan (như trên) **2291 qua, 2 xfail (LC-T101-1, có từ trước), 0 hỏng** (3 phút 58 giây). `uv run ruff check .` sạch; `ruff format --check` sạch.

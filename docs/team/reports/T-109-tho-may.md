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

# Báo cáo T-100 · Đồng bộ kế hoạch: cache SQLite, kiểm xung đột khi ghi Sheets, nối nháp với dòng kế hoạch

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-100](../tickets/T-100-dong-bo-ke-hoach-cache-nhap.md) · thiết kế [T-094 mục 1.5–1.7, 2.4–2.6, 6](T-094-tho-may.md) · điều kiện [Lá Chắn T-094](T-094-la-chan.md) («Chung», «T-100») |
| Nhánh | `team/T-100` (worktree `D:\ProMetal-ToolSEO\wt-T-100`), gốc `main` `b241e79` |
| Ngày nộp | 2026-10-28 23:52 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành (yêu cầu 1–6). 9 dòng test cũ đổi theo phương án A Chỉ Huy duyệt (mục «Test cũ đã đổi»). Đáp ứng LC-T094-1, -2, -3 (phần dữ liệu), -5 (phần T-100), -28, -29, -30, -31. Thêm (Chỉ Huy duyệt): SL-T097-5 (gỡ 3 `xfail`), G2 / LC-T103-1 |

## Tóm tắt (cho chủ dự án)

- Phần **logic đồng bộ kế hoạch với Google Sheets** đã có (giao diện làm ở T-101, T-102):
  - Đọc tab «KeHoach», nhận cột **theo tên** (đổi thứ tự cột, thêm cột riêng đều được). Lưu tạm trên máy để trang mở ngay và vẫn xem được khi mất mạng; cũ hơn 5 phút thì tải lại.
  - «Áp dụng thay đổi»: app đọc lại Sheet, so từng ô sắp ghi với bản anh/chị đã xem. Ô nào vừa bị sửa ở máy kia hay trên Google Sheets thì **không ghi** dòng đó, báo rõ mã bài và tên cột. Hai máy sửa hai cột khác nhau của cùng dòng thì không chặn nhau. App **không bao giờ xóa dòng**, không ghi vào cột riêng của anh/chị.
  - Gửi bài xong: app tự ghi **4 ô** (Trạng thái, Mã bài WordPress, Ngày đăng thực tế, Cập nhật lúc), không bao giờ lùi trạng thái (bài «Đã đăng» không bị ghi lại thành «Đã gửi nháp»). Mất mạng thì việc ghi được nhớ trên máy và thử lại sau; thử lại **chỉ ghi Sheet, không gửi lại bài**.
  - Nút «Chuẩn bị trang tính»: tạo tab «KeHoach», dòng tiêu đề, danh sách chọn. Tab có sẵn mà thiếu cột thì cột thiếu được thêm vào **cuối** dòng tiêu đề, không dời cột có sẵn.
- Mất mạng đúng lúc thêm dòng mới: app đọc lại Sheet xem dòng đã lên chưa, **không bao giờ thêm trùng**.
- Chữ có dạng công thức («=…», «+…», «-…», «@…») được thêm một dấu cách đầu, để file tải về mở bằng Excel không chạy thành công thức. Giờ ghi lên Sheet luôn là giờ Việt Nam có ghi «+07:00».
- Hai lỗi nhỏ Chỉ Huy giao thêm:
  - File khóa Google gõ đường dẫn có «..» đi ngang thư mục dự án không còn bị chặn oan; file khóa trên ổ Google Drive này không còn bị nhầm là nằm trong thư mục ảnh ở ổ Google Drive khác.
  - Đề xuất của AI có **giá** («150.000đ», «1,5 triệu», «500k», «bảng giá») thì có cảnh báo và không tick sẵn, vì Pro-Metal không công bố giá.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/sync.py` | Mới.<br>- Đọc: `parse_sheet` (`:222`) dùng đúng bộ đọc bảng của T-098 (`parse._header_map`, `parse._row`), `read_sheet` (`:279`), `get_plan` (`:296`) có cache.<br>- Áp dụng đề xuất có kiểm xung đột: `apply_proposals` (`:401`), `_update` (`:501`), `_addition` (`:478`).<br>- Ghi 4 ô trạng thái: `status_write`, `write_status` (`:624`, `:646`), `record_status` (`:706`), `retry_pending` (`:736`).<br>- Mở Soạn bài từ dòng: `open_row`, `plan_ref` (`:759`, `:781`).<br>- «Chuẩn bị trang tính»: `prepare_sheet` (`:845`).<br>- Chuyển giá trị: `safe_text`, `to_cell` (`:945`, `:956`). |
| `seo_app/storage/plan_cache.py` | Mới. `PlanCacheStore` (cache `data/plan_cache.sqlite`), `sheet_hash`. Lưu **đúng các ô** Google trả, mã băm Sheet, giờ tải, mã băm toàn bộ ô. Kiểm `sqlite_master` trong cùng giao dịch trước mọi truy vấn (như kho thẻ T-074). |
| `seo_app/storage/drafts.py` | - Khuôn 3 (`SCHEMA_VERSION = 3`; khuôn 1, 2 vẫn mở; khuôn 2 giữ ảnh: `:705`).<br>- `DraftPlanRef` (`:574`) và `DraftSnapshot.plan` (`:690`, sai khuôn thì bỏ, nháp vẫn mở).<br>- `SendState` (`:798`) thêm `mode`, `scheduled_for`, `released`, `release_unknown`, có kiểm khớp nhau.<br>- `PlanStatusWrite` (`:618`) và bảng `plan_writes` (việc ghi Sheet còn nợ): `load_plan_write`, `save_plan_write` (so rồi đặt), `list_plan_writes` (`:1056-1100`).<br>- `find_plan_draft` (`:1033`). |
| `seo_app/plan/propose.py` | G2 / LC-T103-1: `WARN_PRICE` (`:81`), `_has_price` (`:398`, dò bằng `mentions_price` của bước SEO, theo khúc gối nhau cho ghi chú dài), `_ai_texts` (`:388`, dùng chung với cảnh báo số điện thoại) |
| `seo_app/google/service_account.py` | SL-T097-5: `_inside_by_identity` (`:239`) đi ngược theo đường **thật** (`resolve`), không theo chữ của đường gõ; `_other_drive_letter` (`:269`): hai đường thật ở hai ổ khác chữ thì không tin danh tính (ổ Google Drive for Desktop) |
| `tests/test_soi_loi_t097.py` | Gỡ 3 dấu `xfail` của SL-T097-5: **6 dòng xóa, 0 dòng thêm** (R5) |
| `tests/test_drafts_images.py`, `test_soi_loi_t016_t020.py`, `test_soi_loi_t041.py`, `test_soi_loi_t055.py` | Đổi đúng 9 dòng ghim khuôn nháp 2 (Chỉ Huy duyệt A 28/10); `test_soi_loi_t041.py` thêm 1 ca `test_t100_new_save_writes_v3_and_v4_is_unknown` (điều kiện 1, 2). Mục «Test cũ đã đổi» |
| `tests/fake_plan_sheet.py` | Mới. Google Sheet giả **có trạng thái** gắn vào `FakeGoogle` (T-097): test đi qua đúng `SheetsClient` thật |
| `tests/test_plan_sync.py`, `test_plan_cache.py`, `test_t100_drafts_plan.py`, `test_t100_google_identity.py` | Mới: 152 ca |
| `tests/test_plan_propose.py` | Thêm 8 ca giá (5 ca của Lá Chắn T-103 viết lại, ghi chú dài, giá trong từ khóa, giá cũ AI không đổi) |
| `docs/team/reports/T-100-tho-may.md` | Báo cáo này |

Không sửa `seo_app/wordpress/**`, `app/**`, `config/**`, `seo_app/plan/parse.py`, `seo_app/plan/model.py`.

## Test cũ đã đổi (R5)

LC-T094-30 bắt tăng phiên bản cấu trúc nháp, nên khuôn nháp lên **3**. 9 dòng test cũ của người khác ghim «khuôn hiện tại là 2» hay «3 là khuôn lạ», làm hỏng 8 ca (lượt chạy 23:25–23:51: `2902 passed, 8 failed`, không ca nào khác hỏng).

**Chỉ Huy duyệt A 28/10** (Chỉ Huy B, hai tin: duyệt A, rồi xác nhận gồm cả dòng thứ 9). Đổi đúng 9 dòng:

| File, dòng | Cũ | Mới |
|---|---|---|
| `tests/test_drafts_images.py:197` | `assert loaded.schema_version == SCHEMA_VERSION == 2` | `… == 3` |
| `tests/test_drafts_images.py:219` | `assert stored["schema_version"] == 2` | `… == 3` |
| `tests/test_drafts_images.py:473` | `parametrize("version", [0, 3, 999, -1, "abc", None, [2]])` | `[0, 4, 999, …]` |
| `tests/test_drafts_images.py:485` | `DraftSnapshot(schema_version=3)` (phải lỗi) | `schema_version=4` |
| `tests/test_soi_loi_t016_t020.py:744` | `{"schema_version": 3},` (khuôn lạ) | `{"schema_version": 4},` |
| `tests/test_soi_loi_t041.py:366` | `assert data["schema_version"] == 2` | `data["schema_version"] = 2` |
| `tests/test_soi_loi_t055.py:654` | `assert loaded.schema_version == SCHEMA_VERSION == 2` | `… == 3` |
| `tests/test_soi_loi_t055.py:669` | `assert stored["schema_version"] == 2` | `… == 3` |
| `tests/test_soi_loi_t055.py:687` (test canh dòng t016_t020:744) | `assert SCHEMA_VERSION + 1 == 3` | `… == 4` |

`git diff --numstat`: `test_drafts_images.py` 4/4, `test_soi_loi_t016_t020.py` 1/1, `test_soi_loi_t055.py` 3/3. `test_soi_loi_t041.py` 17/1: 1 dòng đổi, cộng 16 dòng của ca mới (điều kiện 1, 2).

**Điều kiện 2, `test_soi_loi_t041.py:366`: chọn gán `= 2`.**
- Ý của ca (`test_v2_draft_as_saved_by_main_opens_with_image_and_empty_seo`) không phải «nháp vừa lưu» mà là «nháp khuôn 2 như `main` lưu trước T-041». Ca dựng nháp đó bằng tay từ một nháp vừa lưu (xóa khóa `seo`).
- Với khuôn 3, nháp vừa lưu là khuôn 3, nên phải **gán** `2` để đúng là nháp khuôn 2 cũ. Đổi assert thành `== 3` sẽ làm ca thành «nháp khuôn 3 thiếu SEO», sai ý.
- Kiểm «nháp lưu mới ghi khuôn 3» nằm ở ca mới cùng file `test_t100_new_save_writes_v3_and_v4_is_unknown`: lưu mới ghi `3`, mở được, giữ ảnh; khuôn 4, 99 bị từ chối.

**Điều kiện 1: mỗi file đổi có ca chứng minh khuôn 3 mở được và khuôn 4 trở lên là lạ.**

| File | Khuôn 3 mở được | Khuôn 4 trở lên là lạ |
|---|---|---|
| `test_drafts_images.py` | `test_round_trip_keeps_every_image_field` (`== 3`) | `test_unknown_schema_versions_are_rejected[4]`, `[999]`; `test_constructing_old_version_upgrades` (`schema_version=4`) |
| `test_soi_loi_t016_t020.py` | `test_round_trip_tricky_text_every_version` (`:516`, lưu rồi mở nháp khuôn 3, giữ nguyên) | `test_wrong_shape_rows_give_draft_error` (`{"schema_version": 4}`) |
| `test_soi_loi_t041.py` | `test_t100_new_save_writes_v3_and_v4_is_unknown` (mới) | cùng ca (4 và 99) |
| `test_soi_loi_t055.py` | `test_real_v1_draft_from_main_opens_and_resaves_as_v2` (nháp khuôn 1 lưu lại thành khuôn 3, mở lại giữ lựa chọn ảnh) | `test_schema_version_guard_for_old_test_line` (`DraftSnapshot(schema_version=SCHEMA_VERSION + 1)` lỗi) |

**Điều kiện 3:** `tests/test_t100_drafts_plan.py::test_old_draft_on_users_machine_opens_and_resaves_as_v3` (khuôn 1 và khuôn 2).
- Dựng file nháp như trước T-100: chưa có bảng `plan_writes`; nháp khuôn 1 (không ảnh, không SEO) hay khuôn 2 (có ảnh đã chọn), đã gửi nháp (có trạng thái gửi, mã bài 501).
- Mở bằng kho mới: mở được, không cất file sang bên, ảnh giữ nguyên, không ảnh nào hỏng, trạng thái gửi giữ nguyên.
- Lưu lại: JSON ghi khuôn 3, **mọi khóa, giá trị cũ còn nguyên** (so từng khóa lồng nhau), trạng thái gửi vẫn đúng, mở lại vẫn đủ ảnh.
- Thêm các ca cũ của tôi: `test_v2_draft_keeps_its_image_and_has_no_plan`, `test_v1_draft_still_drops_only_image_data`, `test_old_send_state_row_reads_with_defaults`.

## Cách dùng cho T-101, T-102

- **Trang Kế hoạch (T-101):**
  - Vẽ trang: `get_plan(PlanCacheStore(), settings.google_sheet_id, client hay None, index=…)` trả `PlanListing(plan, notice)`.
  - Đề xuất: `compare_rows(listing.plan.plan_rows(), parsed.rows, …)` hay `ContentWriter.plan_changes(listing.plan.plan_rows(), …)`.
  - «Áp dụng»: `apply_proposals(client, listing.plan, đề_xuất_đã_tick, index=…)`. `listing.plan` (bản người dùng đã xem) phải giữ trong `session_state` từ lúc đề xuất tới lúc bấm. Hiện `result.message`; mỗi `Conflict` có `proposal.before` («trước»), `now` («bây giờ»), `proposal.after` («đề xuất»). Xong thì `get_plan(…, refresh=True)`.
  - `apply_proposals` ném `SheetsError` (đọc lại lỗi) và `SheetPlanError` (thiếu cột Mã bài / Từ khóa); cả hai là câu cố định, chưa ghi gì. `compare_rows` có thể ném `PlanKeyError` (hết mã; ghi chú từ T-098).
  - Mở trang: `retry_pending(client, DraftStore(), sheet_id)` (nút «Thử ghi lại» cũng gọi hàm này).
  - Cài đặt: `prepare_sheet(client)`; nếu `result.missing` có cột thì hiện nút «Thêm cột còn thiếu», bấm thì `prepare_sheet(client, add_missing=True)`.
- **Bước Xuất bản và «Viết bài» (T-102):**
  - «Viết bài»: `find_plan_draft(key, sheet_hash(sheet_id))` → có nháp thì mở nháp đó. Không có: `open_row(client, key, index=…)` (đọc lại Sheet), tạo nháp với `plan=plan_ref(row, sheet_id)`, rồi `record_status(client, store, draft_id, status_write(ref, STATUS_WRITING))` (4A).
  - Gửi xong: `record_status(client, store, draft_id, status_write(snapshot.plan, STATUS_DRAFT_SENT / SCHEDULED / PUBLISHED, wp_post_id=…, published_at=giờ hẹn hay giờ đăng))`. `record_status` lưu việc vào kho nháp **trước** khi gọi Google.
- Mọi chữ trong `PlanRow`, `Conflict.now` đã làm sạch nhưng **chưa escape**. Giao diện hiện bằng ô bảng, `st.text`, hay `escape_markdown` (LC-T094-3). `warnings`, `message` là câu cố định, chỉ có Mã bài và tên cột chuẩn.

## Đối chiếu điều kiện Lá Chắn

| Mã | Đáp ứng ở đâu | Test |
|---|---|---|
| LC-T094-1 (test không gọi Google, WordPress thật) | Sheet giả `tests/fake_plan_sheet.py` gắn vào `FakeGoogle`, đi qua `SheetsClient` thật; máy chủ mã giả; khóa RSA sinh lúc chạy; bộ chặn mạng của `conftest.py` không đổi. `sync.py` không nhập gì của `seo_app.wordpress` | `test_sync_module_never_talks_to_wordpress` và mọi test trong `test_plan_sync.py` |
| LC-T094-2 (câu báo cố định) | Mọi câu báo mới là hằng (`MSG_*`, `CONFLICT_*`, `STATUS_*` trong `sync.py`; `_MSG_*` trong `plan_cache.py`, `drafts.py`). Chỉ nêu Mã bài (đã chuẩn hóa), tên cột chuẩn, số dòng; lỗi Google lấy `str(SheetsError)` (câu cố định của T-097) | `test_get_plan_shows_cached_copy_when_google_fails`, `test_rejected_update_stops_and_appends_are_not_sent`, `test_status_conflicts_are_not_written`, `test_duplicate_keys_keep_first_row_and_warn_without_cell_text` (mồi `MOI` trong lời máy chủ và trong ô) |
| LC-T094-3 (phần dữ liệu; hiện là T-101) | Mọi dòng từ Sheet và cache qua `PlanRow` (bỏ ký tự điều khiển, vô hình, đảo hướng chữ U+202A–202E, U+2066–2069) | `test_dirty_cells_go_through_plan_row`, `test_cached_rows_go_through_plan_row` |
| LC-T094-5 (phần T-100: mọi dòng từ Sheets / cache qua `PlanRow`) | `parse_sheet` là đường duy nhất đổi ô Sheet hay ô cache thành kế hoạch | như trên |
| LC-T094-28 (ghi Sheet) | Chỉ các cột của `SHEET_COLUMNS` (tìm theo tên), chỉ ô đổi + «Cập nhật lúc», dòng tìm theo Mã bài; so ô sắp ghi, ô Mã bài, Từ khóa với bản gốc (`_update`); Mã bài trùng → không ghi (`_fresh_row`, `write_status`); không có lệnh xóa dòng, cột nào; mọi ô `RAW` (client T-097 chặn ở lớp kiểm); `safe_text` thêm dấu cách đầu cho chữ bắt đầu `=`, `+`, `-`, `@`, tab, CR; giờ ghi `_moment_text`: giờ Việt Nam, chữ có `+07:00`, từ `datetime.now(model.TIMEZONE)` | `test_update_writes_only_changed_cells_raw_with_time`, `test_cell_changed_elsewhere_is_not_written`, `test_two_machines_editing_different_columns_do_not_block`, `test_duplicate_or_missing_key_is_not_written`, `test_foreign_columns_are_never_written`, `test_drop_only_sets_status_and_never_deletes_rows`, `test_add_appends_row_by_column_name`, `test_safe_text_defuses_formula_start`, `test_time_written_is_vietnam_time_even_from_utc_clock` |
| LC-T094-29 (cache) | SQL chỉ tham số `?`; kiểm `sqlite_master` (đúng 2 bảng, không trigger, khung nhìn, chỉ mục, bảng lạ) **trong cùng giao dịch** trước mọi truy vấn; giới hạn số bước, độ dài giá trị; mỗi ô kiểm kiểu, mã băm toàn bộ ô phải khớp; sai một dòng, sai phiên bản, khác mã băm Sheet → bỏ cả cache; chỉ lưu mã băm SHA-256 của mã Sheet; mọi dòng đọc lại qua `PlanRow`; `apply_proposals`, `write_status`, `open_row`, `prepare_sheet` luôn đọc lại Sheet trước khi ghi / mở Soạn bài | `test_plan_cache.py` (17 cách sửa tay, file không phải SQLite, trigger không chạy khi ghi, không có mã Sheet trong file, SQL tham số), `test_open_row_reads_the_sheet_again`, `test_reading_again_fails_before_anything_is_written` |
| LC-T094-30 (kho nháp) | Khuôn 3 với `DraftSnapshot.plan`, `SendState` mở rộng; nháp khuôn 1, 2 và dòng trạng thái gửi cũ vẫn mở; so rồi đặt của T-089 giữ nguyên (so cả trường mới); việc ghi Sheet còn nợ ở bảng `plan_writes` của `drafts.sqlite`; `retry_pending` chỉ gọi `write_status` (không nhập gì của WordPress), vẫn kiểm xung đột; bỏ việc bằng so rồi xóa (tab khác vừa ghi việc mới thì giữ) | `test_t100_drafts_plan.py` (48 ca), `test_record_status_keeps_write_until_sheet_has_it`, `test_retry_skips_other_sheet_and_stops_on_error`, `test_retry_does_not_remove_a_newer_write_from_another_tab` |
| LC-T094-31 («Chuẩn bị trang tính») | Chỉ khi gọi `prepare_sheet` (nút); chỉ 4 loại yêu cầu (`addSheet`, `updateSheetProperties`, `repeatCell`, `setDataValidation`) trên đúng `sheetId` tab «KeHoach» vừa đọc (client kiểm lại); tiêu đề thiếu ghi vào cuối dòng 1 sau ô có chữ cuối cùng; danh sách chọn là `model.INTENTS`, `KINDS`, `PRIORITIES`, `STATUSES` | `test_prepare_creates_tab_and_header` (có tab «Kehoach», «KeHoach␠» không bị đụng), `test_prepare_reports_missing_columns_without_writing`, `test_prepare_adds_missing_columns_at_the_end`, `test_prepare_refuses_when_no_room_left`, `test_prepare_formats_only_the_plan_tab` |

## Hai việc Chỉ Huy duyệt thêm

- **SL-T097-5** (Soi Lỗi T-097 lượt 2): sửa theo gợi ý («chỉ đi ngược thư mục cha của `real`»), thêm ghi nhận lượt 2 số 1 (ổ Google Drive cho các ổ cùng số nhận dạng).
  - Hai đường thật ở **hai chữ ổ khác nhau** thì không so danh tính.
  - Cách viết khác của cùng một ổ (`\\localhost\D$`, `\\?\Volume{…}`) vẫn so danh tính, nên SL-T097-3 không lùi: các ca chỉ chạy trên Windows của T-097 đều qua trên máy này.
  - 3 ca `xfail` thành XPASS, đã gỡ dấu.
- **G2 / LC-T103-1** (Soi Lỗi, Lá Chắn T-103): chữ AI **đưa vào dòng** có giá thì có `WARN_PRICE`, nên không tick sẵn.
  - Với «Thêm»: mọi trường chữ; với «Cập nhật»: chỉ trường AI đổi. Giá có sẵn trong ghi chú cũ không tính; chỗ nằm trong từ khóa chính không tính.
  - **Lưu ý khi gộp:** 5 ca `xfail(strict=True)` LC-T103-1 trong `tests/test_la_chan_t103.py` nằm ở nhánh `team/T-103`, chưa có trên nhánh này. Tôi chạy file đó (lấy từ nhánh `team/T-103`) trên code T-100 với `--runxfail`: 5 ca LC-T103-1 và ca «giá cũ AI không đổi» đều qua.
  - Vậy gộp cả T-100 lẫn T-103 thì 5 ca đó thành XPASS (strict).
  - **Chờ bước gỡ dấu** (Chỉ Huy giao 28/10): khi Chỉ Huy báo T-103 đã gộp `main`, tôi gộp `main` vào `team/T-100` rồi gỡ 5 dấu đó (chỉ xóa dấu, R5).

## Bằng chứng

```
$ uv run pytest -q tests/test_plan_sync.py tests/test_plan_cache.py tests/test_t100_drafts_plan.py \
    tests/test_t100_google_identity.py tests/test_plan_model.py tests/test_plan_parse.py \
    tests/test_plan_propose.py tests/test_plan_ai.py tests/test_soi_loi_t098.py \
    tests/test_soi_loi_t003_t009.py tests/test_t040_prompts.py tests/test_content_workflow.py \
    tests/test_prompt_data_frames.py tests/test_google_sheets.py tests/test_google_service_account.py \
    tests/test_soi_loi_t097.py tests/test_la_chan_t097.py
(2026-10-28 23:36:48 → 23:39:21 +0700)
1613 passed, 3 skipped in 149.11s

# 27 file dùng kho nháp / SendState (grep `seo_app.storage.drafts`: kho nháp, gửi nháp T-086, T-089,
# trang Soạn bài, ảnh, SEO T-041, T-083, T-090)
$ uv run pytest -q tests/test_app_drafts.py tests/test_app_images.py tests/test_drafts_images.py … (27 file)
(2026-10-28 23:25:39 → 23:51 +0700, máy đang chạy song song test của phiên khác)
8 failed, 2902 passed, 18 skipped in 1516.46s
# 8 ca hỏng = đúng 8 ca ghim khuôn nháp 2 (mục «Test cũ đã đổi»), trước khi đổi; không ca nào khác

# Sau khi Chỉ Huy duyệt A: 4 file test cũ đã đổi + file kho nháp của tôi
$ uv run pytest -q tests/test_drafts_images.py tests/test_soi_loi_t016_t020.py \
    tests/test_soi_loi_t041.py tests/test_soi_loi_t055.py tests/test_t100_drafts_plan.py
(2026-10-28 23:55:18 → 23:57:14 +0700)
615 passed, 7 skipped in 112.21s
# 23 file còn lại của lượt 27 file đã qua hết ở lượt 23:25–23:51; code không đổi sau lượt đó
# (chỉ đổi 9 dòng test cũ và thêm test)

$ uv run pytest -q tests/test_app_pages.py
(23:38:38 → 23:39:16) 18 passed

# Google, trước khi gỡ dấu SL-T097-5 (chạy cả ca xfail như ca thường)
$ uv run pytest -q --runxfail tests/test_soi_loi_t097.py tests/test_la_chan_t097.py \
    tests/test_google_service_account.py tests/test_google_sheets.py
688 passed, 3 skipped

# 5 ca LC-T103-1 + ca «giá cũ AI không đổi», lấy từ nhánh team/T-103, chạy trên code T-100
$ uv run pytest -q --runxfail tests/<bản sao test_la_chan_t103.py> -k "lc_t103_1 or old_price"
6 passed

$ uv run ruff check .
All checks passed!
$ PYTHONUTF8=1 uvx detect-secrets scan <11 file đổi>
(không có kết quả)
```

- Mỗi module mới và module đổi đều nhập được khi là module đầu tiên trong một tiến trình mới (không vòng nhập): `seo_app.onpage.links`, `seo_app.storage`, `seo_app.plan.sync`…
- `tests/test_soi_loi_t097.py`: `git diff` chỉ 6 dòng xóa (3 dấu `@pytest.mark.xfail(...)`), 0 dòng thêm.

## Rủi ro và điểm cần chú ý

- **Khe hở ghi cùng một ô** (thiết kế 2.5, Lá Chắn T-094 ghi nhận 2): hai máy ghi đúng một ô trong 1–2 giây giữa lần đọc lại và lệnh ghi thì bản ghi sau thắng. Sheets không có lệnh ghi có điều kiện; chủ dự án dùng hai máy luân phiên nên rất hiếm. Không phải rủi ro bảo mật.
- Ghi đề xuất **nhiều hơn 200 ô** thì chia thành nhiều lệnh (mỗi đề xuất nằm trọn trong một lệnh). Lệnh sau lỗi thì các lệnh trước đã ghi: `ApplyResult` tách rõ đã ghi / chưa ghi / chưa rõ.
- Lệnh ghi ô lỗi giữa chừng (`unsure`): báo «chưa rõ», bấm «Tải lại» rồi áp dụng lại. Lần sau ô nào trên Sheet đã đúng giá trị đề xuất thì tính là đã ghi, không báo xung đột.
  - Riêng dòng **chưa có Mã bài** được cấp mã ở lần lỗi đó: lần sau dòng đã có mã nên báo «không còn thấy dòng», phải đề xuất lại trên bản mới. Hướng an toàn.
- `parse_sheet` dùng hai hàm nội bộ của `parse.py` (`_header_map`, `_row`, cùng gói `seo_app.plan`), để Sheet, file và chữ dán đi đúng **một** bộ đọc bảng. Không sửa `parse.py`.
- Cache lưu ô thô. Dòng mà `PlanRow` từ chối (thiếu từ khóa…) là nội dung thật của Sheet, nên được hiện như lúc đọc thẳng từ Sheet (bỏ dòng, có câu báo), không coi là cache hỏng. Cache hỏng là: sai khuôn ô, sai cấu trúc file, sai mã băm.
- `find_plan_draft` lọc nhanh bằng `instr` trên chữ JSON. Dấu ngoặc kép trong chữ của bài luôn được JSON ghi thoát nên không khớp nhầm; nháp tìm được luôn được **mở lại** để xác nhận.
- Xóa nháp hay nháp bị dọn (quá 30 nháp) **không** xóa việc ghi Sheet còn nợ của nó: bài đã lên website thì dòng kế hoạch vẫn phải cập nhật. Giữ tối đa 200 việc.
- Thử trên Google thật để lượt thử thật của Giai đoạn 5 (thiết kế mục 6 «Đi kèm»): sắp xếp lại, sửa tay cùng lúc trên trình duyệt để thấy báo xung đột.

## Đề xuất

- T-101, T-102: dùng đúng các hàm ở mục «Cách dùng»; giữ `listing.plan` (bản gốc) trong `session_state` tới lúc «Áp dụng».
- Khi T-103 đã gộp `main`: Chỉ Huy báo, tôi gộp `main` vào `team/T-100` và gỡ 5 dấu `xfail` LC-T103-1 (mục trên).

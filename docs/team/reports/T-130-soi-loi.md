# Báo cáo T-130 · Giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-130 `docs/team/tickets/T-130-giu-trang-thai-gui-khi-xoa-nhap.md` |
| Nhánh | `team/T-130`, đầu nhánh `302ba7a` (Họa Sĩ; từ `main` `50a40a6`, đã có T-092). Thử gộp với `main` cục bộ `06a1b0e` (thêm T-124: lấy số liệu Search Console, gom chuẩn hóa `WORDPRESS_URL` trong client WordPress): **không xung đột**, cây `1ddffd7` |
| Ngày nộp | 2026-11-07 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT**, chuyển Lá Chắn được. **0 lỗi** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). Đủ 5 trọng tâm: xóa nháp đã gửi, đang gửi, gửi dở giữ trạng thái gửi; nháp lưu lại ở **bất kỳ** tab nào (kể cả tab chưa từng biết) vẫn khóa gửi trùng; nháp chưa gửi xóa như cũ; dọn dòng mồ côi không bao giờ đụng nháp còn; popover «🗑️ Xóa» nhắc đúng; không lùi T-086, T-089, T-092; R5 đúng. Gộp thử `main` cục bộ `06a1b0e`: không xung đột; 20 file liên quan trên cây gộp: 667 qua, 0 hỏng. 2 ghi nhận (G1 ngoài phạm vi phiếu) |

## Tóm tắt (cho chủ dự án)

- **Đã đúng.** Xóa nháp của bài đã gửi lên website nay **không** làm mất «khóa gửi trùng»: tab nào lưu lại nháp đó, kể cả tab chưa từng thấy lần gửi, vẫn bị khóa, không ra bài thứ hai trên website. Tôi thử ba tab cùng một bài, bỏ bài ở một tab, lần gửi chưa rõ kết quả, kho nháp đầy: đều đúng.
- Nút **«🗑️ Xóa»** của bài đã gửi nhắc rõ «xóa nháp **không** xóa bài trên website», kèm mã bài; bài đã hẹn giờ hay đã đăng cũng nhắc đúng như vậy.
- Ghi chú «đã gửi» của nháp đã xóa được dọn tự động (giữ 200 ghi chú mới nhất), không bao giờ đụng nháp đang có.
- **Một điểm ngoài phạm vi phiếu (không phải lỗi của phiếu này):** xóa nháp đã gửi rồi bấm **«Viết từ kế hoạch»** cùng dòng thì phần mềm tạo nháp **mới** (mã mới), không mang khóa của nháp cũ. Tôi chưa kiểm sâu phần này; ghi lại để Chỉ Huy cân nhắc phiếu sau.
- **Việc của bạn:** không có.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t130.py` | Mới: 6 ca, qua cả 6. Mượn khung trang Soạn bài, ảnh giả, WordPress giả của `test_app_images` và hàm của `test_t086_send_state`, `test_t092_nhap_bi_xoa` |
| `docs/team/reports/T-130-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu, không gọi website thật.

## Kiểm theo trọng tâm

### 1. Xóa nháp đã gửi, đang gửi, gửi dở giữ trạng thái gửi; lưu lại ở bất kỳ tab nào vẫn khóa

Đọc mã: `DraftStore.delete` (`seo_app/storage/drafts.py:991`) chỉ xóa dòng nháp; phần kho đầy bỏ bớt trong `save` (`:930`) cũng vậy; dòng trạng thái gửi ở lại theo đúng mã nháp. Lưu lại cùng mã thì dòng đó gắn lại (bảng `send_states` khóa theo mã nháp); «Lưu lại thành nháp» (`recreate_draft`) so rồi đặt với «chưa gửi» nên không đè dòng có sẵn. Bước Xuất bản đọc `load_send_state` (không đòi nháp còn), nên **ngay cả trước khi lưu lại**, mọi tab đang mở bài đó đã thấy khóa theo dòng giữ lại; lớp «điều tab biết» của T-092 vẫn nằm bên dưới cho ca dòng giữ lại bị dọn hay file nháp bị xóa. Chỉ có hai đường xóa dòng trạng thái gửi: `save_send_state(None)` (lần gửi chưa tạo gì trả về «chưa gửi», nháp còn) và `_trim_orphan_send_states` (chỉ dòng mồ côi).

| Thử | Kết quả |
|---|---|
| 16 ca của Họa Sĩ (kho 12, trang 4), chạy trên cây gộp | qua |
| **Ba tab (G1 của tôi ở T-092), chạy hết bằng giao diện:** tab A đứng ở Xuất bản thấy «đã gửi 777»; tab B mở bài từ trước lần gửi, chưa vẽ lại; nháp bị xóa; tab B làm tiếp | Tab B: khung báo «Tab này biết bài đã gửi» (đọc dòng giữ lại); bấm «Lưu lại thành nháp»: nháp có lại kèm «đã gửi 777». Tab A, tab B, phiên mới mở nháp đều phải tick «Tạo thêm…»; bấm gửi (nếu nút mở) không ra bài nào. Ở T-092, tab A mất khóa, ra bài thứ hai |
| Tab A thấy nháp không còn, chọn «🗑️ Bỏ bài này» → «Bỏ hẳn» | Chỉ xóa trắng trang tab A; dòng trạng thái gửi giữ lại vẫn còn; tab B (mở từ trước) lưu lại vẫn khóa; website vẫn một bài |
| Nháp «gửi dở» (chưa rõ kết quả, chưa có mã) bị xóa; tab mở từ trước, chưa biết, lưu lại | Nháp có lại kèm «gửi dở»; bước Xuất bản đòi tick «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi» |

### 2. Nháp chưa gửi xóa như cũ

Nháp chưa gửi không có dòng trạng thái gửi nào (phần mềm không ghi dòng «chưa gửi»), nên xóa không để lại gì: ca `test_delete_unsent_draft_leaves_nothing` của Họa Sĩ qua.

### 3. Dọn dòng mồ côi an toàn

Đọc mã `_trim_orphan_send_states` (`drafts.py:1213`): chỉ xét dòng **không có nháp đi kèm** (`id NOT IN (SELECT id FROM drafts)`), giữ `max_orphan_send_states` dòng có `rowid` lớn nhất, chạy trong cùng giao dịch với lần xóa, lần lưu. Mỗi lần ghi trạng thái gửi là `INSERT OR REPLACE` (bảng `send_states` có `rowid`, khóa `id TEXT`): dòng ghi lại bị thay bằng dòng mới, `rowid` lớn nhất trong các dòng còn, nên «`rowid` lớn nhất» đúng là «ghi gần nhất». Bảng nháp có mã `NULL` thì `NOT IN` không bao giờ đúng: không dọn gì (hướng an toàn). Giới hạn âm thành 0.

| Thử | Kết quả |
|---|---|
| 6 ca của Họa Sĩ (dọn giữ mới nhất, không đụng nháp còn kể cả dòng hỏng, thứ tự theo lần ghi, giới hạn 0 và âm, mã `NULL`, mặc định 200) | qua |
| **Kho đầy** (`max_drafts=4`) cả 4 nháp đã gửi, cùng nhiều dòng mồ côi hơn giới hạn (`max_orphan_send_states=3`); dòng mồ côi cũ nhất được ghi lại (kết quả lần gửi ghi sau lúc xóa, SL-T089-2); lưu nháp mới làm kho đầy bỏ «còn 0» | Trạng thái gửi của mọi nháp còn trong kho nguyên vẹn; giữ đúng 3 dòng mồ côi ghi gần nhất (theo thứ tự ghi: «đã xóa 5», «còn 0» vừa thành mồ côi, «đã xóa 3» vừa ghi lại); «đã xóa 4» cũ nhất bị dọn; «đã xóa 3» mang đúng kết quả ghi lại (bài 999) |

### 4. Popover «🗑️ Xóa»

Đọc mã `delete_warning` (`app/views/write.py:965`): đã gửi (có mã, không «đang gửi», không «chưa rõ kết quả lệnh hẹn giờ/đăng») → câu «đã gửi lên website (bài mã …)»; đang gửi, gửi dở, lệnh hẹn giờ/đăng chưa rõ, dòng hỏng, file bận → câu «chưa rõ kết quả»; chưa gửi → không nhắc. U1: chữ cố định, mã bài là số nguyên (khuôn `SendState`: `int`, `strict`), không `unsafe_allow_html`.

| Thử | Kết quả |
|---|---|
| Ca của Họa Sĩ: đã gửi, gửi dở, chưa rõ kết quả, dòng hỏng, chưa gửi; bấm «Xóa hẳn» nháp đã gửi | qua |
| Bài **đã hẹn giờ** (`future`, đã chuyển), bài **đã đăng** (`publish`, đã chuyển) | «Bài này đã gửi lên website (bài mã 4321). Xóa nháp **không** xóa bài trên website…»; không nhắc như «chưa rõ kết quả» |

### 5. Không lùi T-086, T-089, T-092

Chạy trên cây gộp (mục 7): lô B (T-086, T-089: 6 file, 136 passed) và lô A (T-092 của Họa Sĩ và của tôi, kho nháp: 113 passed), lô D («Gửi nháp», bước Xuất bản T-102, T-112: 125 passed), 0 hỏng. Đọc mã: luồng gửi (`send_and_record`, `record_outcome`, so rồi đặt, băm ảnh) không đổi; T-130 chỉ đổi phần xóa, dọn trong kho, câu nhắc popover và lần đọc dòng giữ lại lúc thấy nháp không còn (`kept_send_read`). 20 đột biến T-092 Họa Sĩ chạy lại trên cây T-130 vẫn bị bắt (báo cáo Họa Sĩ).

### 6. R5

| Chỗ | Đối chiếu |
|---|---|
| `tests/test_storage_send_state.py::test_send_state_removed_with_its_draft` → `test_send_state_kept_as_orphan_when_its_draft_goes` (T-086) | Chỉ Huy đã duyệt. Giữ đủ các bước cũ (kho đầy bỏ «một», xóa «hai»), đổi mong đợi theo hành vi mới (dòng ở lại, đúng trạng thái), **thêm** bước lưu lại «một» có lại khóa. Không nới |
| `tests/test_t092_nhap_bi_xoa.py::test_must_exist_does_not_recreate_deleted_draft` | Đổi mong đợi «sau khi xóa `send_states` rỗng» thành «dòng ở lại, lần ghi so rồi đặt hỏng không đổi dòng đó»: đúng yêu cầu 5 («test nào khác ghim hành vi xóa nháp là xóa trạng thái gửi»). Phần chính (không tạo lại, câu lỗi riêng) giữ nguyên |
| 7 ca T-092 khác của Họa Sĩ (`test_recreate_writes_send_state_before_draft` ×2, `test_draft_saved_back_without_state_keeps_this_tab_locked`, `test_recreate_keeps_unsure_lock` ×2, `test_sent_state_seen_at_publish_step_is_known`, `test_own_send_known_when_deleted_before_any_read`, `test_unsure_knowledge_locks_only_when_draft_gone[nhap-bi-xoa]`) | Tôi đọc từng chỗ đổi: chỉ thêm một dòng `lose_kept_state` (giả dòng giữ lại cũng mất) và câu docstring; **không bỏ khẳng định nào**. Không thêm thì các ca qua nhờ dòng giữ lại, không còn kiểm đường «điều tab biết» của T-092 (đường vẫn cần khi dòng mồ côi bị dọn, file nháp bị xóa): đổi để **giữ ý ca**, không nới. Nên Chỉ Huy ghi nhận cùng lần duyệt yêu cầu 5 |
| `tests/test_soi_loi_t092.py` (của tôi) | Không đổi. Hai ca SL-T092-1 nay qua nhờ dòng giữ lại (khóa từ kho) thay vì điều tab biết; vẫn đúng ý (không ra bài thứ hai); đường điều tab biết do các ca `lose_kept_state` ở trên giữ |

Họa Sĩ không thêm `skip` hay `xfail`, không xóa test.

### 7. Gộp thử với `main` cục bộ `06a1b0e`

- `git merge-tree` nhánh (`302ba7a`) với `main` cục bộ `06a1b0e`: **không xung đột**, cây `1ddffd7`. Từ gốc nhánh `50a40a6`, `main` thêm T-124 (đổi `seo_app/wordpress/client.py`, `seo_app/env_file.py`, `seo_app/google/search_console.py`, `seo_app/storage/search_cache.py`, `seo_app/tracking/`), không chung file nào với T-130 (`seo_app/storage/drafts.py`, `app/views/write.py`, test); vẫn chạy lô «Gửi nháp» vì client WordPress đổi.
- Chạy chọn lọc trên cây `1ddffd7` qua `run_list.sh` (kiểm danh sách, thiếu file thì dừng; dòng đầu mỗi lô đã xem), 4 lô nối tiếp, mỗi lúc một tiến trình:

| Lô | File | Kết quả |
|---|---|---|
| A · T-130, T-092, kho nháp | `test_t130_giu_trang_thai_gui`, `test_soi_loi_t130`, `test_storage_send_state`, `test_storage_drafts`, `test_t092_nhap_bi_xoa`, `test_soi_loi_t092` | 113 passed, 0 failed |
| B · T-086, T-089 | `test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`, `test_t089_send_draft`, `test_soi_loi_t089`, `test_la_chan_t089` | 136 passed, 0 failed |
| C · nháp cũ, kế hoạch, trang | `test_app_drafts`, `test_drafts_images`, `test_t100_drafts_plan`, `test_t101_home_page`, `test_app_pages` | 293 passed, 1 skipped (`test_drafts_images.py:645`, symlink chỉ thử trên Mac/Linux, có từ trước), 0 failed |
| D · «Gửi nháp», Xuất bản | `test_app_images`, `test_t102_publish`, `test_t112_release_rules` | 125 passed, 0 failed |

Cộng: **667 passed, 1 skipped, 0 failed, 0 xfail, 0 XPASS**.

### 8. Đột biến (của tôi, nhỏ)

Họa Sĩ đã chạy 31 đột biến (11 của T-130, 20 của T-092 trên cây mới; 31/31 bị bắt). Tôi chạy thêm 3 trên bản sao cây gộp (`mutate130.py`), với file của tôi: **3/3 bị bắt**; bản sao trả nguyên sau mỗi lượt (so với `git show` cây gộp: khớp).

| Đột biến | Ca bắt đầu tiên |
|---|---|
| K1 xóa nháp xóa luôn trạng thái gửi (như trước T-130) | `test_g1_ba_tab_tab_khong_biet_luu_lai_moi_tab_van_khoa` |
| K2 dọn dòng mồ côi giữ dòng **cũ nhất** (`ORDER BY rowid ASC`) | `test_kho_day_va_nhieu_dong_mo_coi_khong_dung_trang_thai_nhap_con` |
| K3 popover: bài đã hẹn giờ/đã đăng nhắc như «chưa rõ kết quả» | `test_popover_bai_da_hen_gio_hay_da_dang_noi_ma_bai[da-hen-gio]` |

## Lỗi tìm ra

Không có.

## Ghi nhận (không tính lỗi)

- **G1 · «Viết từ kế hoạch» sau khi xóa nháp đã gửi (ngoài phạm vi T-130):** `find_plan_draft` chỉ tìm trong bảng nháp; nháp của dòng kế hoạch đã bị xóa thì `app/views/write.py:755` tạo nháp **mới, mã mới**, không gắn dòng trạng thái gửi giữ lại của nháp cũ, nên không khóa gửi trùng theo kho. Dòng kế hoạch trên Google Sheet đã ghi «Đã gửi nháp» kèm mã bài (T-102), nhưng lần bắt đầu viết lại cũng ghi trạng thái vào dòng đó (`record_status`); tôi chưa kiểm lần ghi ấy có đè «Đã gửi nháp» không, cũng chưa kiểm trang Kế hoạch, trang Bài viết hiện dòng đã gửi thế nào. Phiếu T-130 chỉ nói nháp cũ được lưu lại cùng mã nên không tính lỗi. Đề xuất Chỉ Huy cân nhắc phiếu sau: khi bắt đầu từ dòng kế hoạch đã có mã bài, nhắc như popover «Xóa».
- **G2 · Các rủi ro Họa Sĩ đã nêu** (dòng trạng thái gửi đã xóa trước T-130 không lấy lại được; quá 200 lần xóa bài đã gửi thì dòng cũ nhất bị dọn; xóa cả file nháp mất hết): đồng ý mức nhẹ; cả ba ca vẫn còn lớp «điều tab biết» của T-092 cho tab đã biết.

## Lệnh đã chạy

- `pytest tests/test_soi_loi_t130.py` (cây nhánh): lần đầu 5 passed, 1 failed: ca dọn dòng mồ côi của tôi viết sai **thứ tự** mong đợi (tập dòng giữ lại đúng); sửa thứ tự theo lần ghi, thêm kiểm dòng cũ nhất bị dọn: qua. Cả file chạy lại trong lô A: qua.
- Cây gộp `1ddffd7`, 4 lô chọn lọc, 20 file: 667 passed, 1 skipped, 0 failed. Hai lần ngắt giữa chừng (lệnh bị dừng; ứng dụng khởi động lại ~08:00): kiểm lại bản sao (`tar --compare` với `git archive`), không còn tiến trình cũ, chạy lại từ đầu.
- Đột biến: mục 8.
- `uv run ruff check .`: sạch.
- `detect-secrets` (`PYTHONUTF8=1`), quét bản sao trong thư mục ngoài git cùng file mồi tiếng Việt: sạch (chỉ file mồi bị báo; file test và báo cáo không có gì).
- Script: thư mục ghi chú chung `T-130-soi-loi-scripts/` (`run_list.sh`, `mutate130.py`).

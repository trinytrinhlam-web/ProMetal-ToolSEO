# Báo cáo T-130 · Giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-130](../tickets/T-130-giu-trang-thai-gui-khi-xoa-nhap.md) |
| Ngày nộp | 2026-11-05 |
| Nhánh | `team/T-130` (từ `main` `50a40a6`, đã có T-092) |
| Kết quả | Hoàn thành yêu cầu 1–5. Đổi test T-086 `test_send_state_removed_with_its_draft` (Chỉ Huy đã duyệt R5) và 8 test T-092 của tôi ghim hành vi cũ hay cần giữ đúng ý ca (bảng «Đổi test cũ») |

## Tóm tắt (cho chủ dự án)

Trước đây, xóa nháp của một bài **đã gửi** lên website thì phần mềm quên luôn việc đã gửi. Nếu một tab khác còn mở bài đó mà chưa từng thấy lần gửi, bấm «💾 Lưu lại thành nháp» là nháp có lại nhưng **không còn khóa gửi trùng**, gửi tiếp là ra bài thứ hai trên website. Nay phần mềm giữ lại ghi chú «đã gửi» của bài kể cả khi nháp bị xóa (hay bị bỏ vì kho nháp đầy): nháp được lưu lại ở **bất kỳ** tab nào vẫn khóa gửi trùng như trước. Ghi chú cũ được dọn tự động (giữ 200 ghi chú gần nhất, không bao giờ đụng ghi chú của nháp còn đang có).

Nút «🗑️ Xóa» của nháp đã gửi nay nhắc rõ: «Bài này đã gửi lên website (bài mã …). Xóa nháp **không** xóa bài trên website: muốn bỏ bài thì xóa trong trang quản trị WordPress.» Lần gửi chưa rõ kết quả thì nhắc bài có thể đã có trên website. Nháp chưa gửi thì xóa như cũ, không nhắc gì thêm.

## Yêu cầu → cách làm → test

| # | Yêu cầu | Cách làm | Test (`tests/test_t130_giu_trang_thai_gui.py` nếu không ghi file) |
|---|---|---|---|
| 1 | Xóa nháp đã gửi (đang gửi, gửi dở) thì giữ trạng thái gửi (dòng mồ côi); nháp chưa gửi xóa như cũ | `DraftStore.delete` (`seo_app/storage/drafts.py:991`) chỉ xóa dòng nháp, **không** xóa dòng `send_states` nữa. Kho đầy bỏ bớt nháp cũ (`save`, `:930`) cũng vậy. Nháp chưa gửi không có dòng trạng thái gửi nào nên xóa như cũ. Dòng giữ lại gắn lại đúng nháp khi nháp được lưu lại (cùng mã nháp): «Lưu lại thành nháp» so rồi đặt với «chưa gửi» nên giữ nguyên dòng có sẵn. Trang: lúc thấy nháp không còn, đọc thêm dòng giữ lại (`kept_send_read`, `app/views/write.py:955`, `:1040`, tham số `extra` của `known_send_state`, `:907`) để khung báo nói đúng «Tab này biết bài đã gửi» | `test_delete_keeps_send_state_as_orphan` (4 ca: đã gửi, gửi dở, gửi tiếp chưa rõ, dòng hỏng: dòng giữ nguyên chữ, nháp lưu lại thì gắn lại), `test_delete_unsent_draft_leaves_nothing`, `test_prune_keeps_send_state_of_pruned_draft`, `test_unknowing_tab_saves_back_and_stays_locked` (khoảng hở cuối của T-092), `test_draft_saved_back_by_unknowing_tab_locks_fresh_session` (G1 của Soi Lỗi T-092 với phiên mới), `test_recreate_does_not_overwrite_row_written_in_between` (tab khác ghi kết quả mới đúng lúc «Lưu lại»: không bị đè); `tests/test_storage_send_state.py::test_send_state_kept_as_orphan_when_its_draft_goes` |
| 2 | Cách dọn dòng mồ côi an toàn, có giới hạn | `_trim_orphan_send_states` (`drafts.py:1213`), chạy trong cùng giao dịch ở mỗi lần xóa (`:1002`) và mỗi lần lưu (`:937`, cũng là lúc kho đầy bỏ bớt). Chỉ xét dòng **không có nháp đi kèm** (`id NOT IN (SELECT id FROM drafts)`), nên không bao giờ đụng trạng thái gửi của nháp còn trong kho. Giữ `max_orphan_send_states` dòng ghi gần nhất (mặc định `MAX_ORPHAN_SEND_STATES = 200`, `:146`, như việc ghi Sheet còn nợ T-100), bỏ phần còn lại. Thứ tự theo lần ghi gần nhất (`rowid`: mỗi lần ghi trạng thái gửi là `INSERT OR REPLACE`, một dòng mới). Bảng nháp có dòng mã `NULL` (sửa tay) thì `NOT IN` không bao giờ đúng: không dọn gì (hướng an toàn) | `test_orphans_trimmed_to_newest`, `test_trim_never_touches_send_state_of_existing_draft` (kể cả dòng cũ nhất, dòng hỏng), `test_trim_order_follows_last_write`, `test_trim_zero_keeps_no_orphan` (0 và số âm), `test_trim_skips_when_drafts_table_has_null_id`, `test_default_orphan_limit` |
| 3 | Popover «🗑️ Xóa» của nháp đã gửi nhắc xóa nháp không xóa bài trên website | `delete_warning` (`write.py:965`) dùng trong `drafts_panel` (`:1108`): đã gửi (có mã, không «đang gửi», không «chưa rõ kết quả lệnh hẹn giờ/đăng») → `MSG_DELETE_SENT` kèm mã bài (`:240`); đang gửi, gửi dở, lệnh hẹn giờ/đăng chưa rõ kết quả, dòng hỏng, file bận → `MSG_DELETE_UNSURE` (`:244`); chưa gửi → không nhắc. Câu cố định, mã bài là số | `test_delete_popover_warns_for_sent_draft` (đọc cảnh báo trong từng popover theo nút «Xóa hẳn» của nó; bấm «Xóa hẳn» nháp đã gửi: nháp mất, trạng thái gửi ở lại) |
| 4 | Không lùi T-086, T-089, T-092 | Luồng gửi, khóa đơn điệu, so rồi đặt, băm ảnh không đổi. Khóa của T-092 theo «điều tab biết» vẫn giữ: cần khi dòng mồ côi bị dọn hay file nháp bị xóa (test T-092 thêm bước giả dòng giữ lại cũng mất, `lose_kept_state`, để vẫn kiểm đường đó) | các file test kho nháp, gửi nháp, hai tab, T-086, T-089, T-092, `test_app_pages.py` (mục «Bằng chứng») |
| 5 | Đổi test T-086 `test_send_state_removed_with_its_draft` và test ghim hành vi «xóa nháp là xóa trạng thái gửi» | Bảng «Đổi test cũ» | — |

## Thiết kế: vì sao thế này

1. **Giữ mọi dòng trạng thái gửi, nguyên chữ.** Phần mềm không bao giờ ghi dòng «chưa gửi» (chưa gửi là không có dòng nào), nên dòng nào còn cũng là một khóa: đã gửi, đang gửi, gửi dở, lệnh hẹn giờ/đăng chưa rõ kết quả, hay dòng hỏng (khóa «gửi dở»). Giữ cả khi kho đầy bỏ bớt nháp cũ, vì với tab còn mở bài đó thì cũng là «nháp không còn» như bị xóa.
2. **Dọn theo số dòng, không theo tuổi.** Bảng `send_states` không có cột giờ; giờ trong JSON là giờ ghi trạng thái (lúc gửi), không phải lúc xóa; thêm cột là đổi khuôn file. Dòng mồ côi chỉ có ích khi một tab còn mở bài **từ trước** lần gửi mà chưa vẽ lại lần nào (tab đã vẽ lại thì đã biết, T-092); phiên Streamlit không sống qua lần mở lại app, nên dòng đã cũ hơn 200 lần xóa bài đã gửi không còn tab nào cần. Thứ tự theo lần ghi gần nhất: dòng vừa được ghi lại sau lúc xóa (kết quả lần gửi đang chạy, SL-T089-2) là dòng mới nhất, được giữ.
3. **Không đổi khuôn file nháp** (không thêm bảng, cột): file cũ dùng tiếp như thường; dòng trạng thái gửi đã bị xóa trước T-130 thì không lấy lại được (như trước).
4. **Khung báo «nháp không còn»** đọc thêm dòng giữ lại: tab chưa từng thấy lần gửi nay vẫn được báo «Tab này biết bài đã gửi (hoặc gửi dở)… lưu lại thì nháp vẫn nhớ việc đó». Đọc hỏng (dòng hỏng, file bận) thì bỏ qua, không bịa trạng thái: khóa vẫn nằm trong kho.
5. **Popover đọc trạng thái gửi từng nháp** trong danh sách: tối đa 30 lần đọc nhỏ mỗi lần vẽ bước Chuẩn bị (danh sách tối đa `MAX_DRAFTS`). Không thêm lệnh đọc gộp vào kho (ngoài phạm vi phần xóa).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | `delete` và phần kho đầy bỏ bớt trong `save` giữ trạng thái gửi; `_trim_orphan_send_states`; `MAX_ORPHAN_SEND_STATES`, trường `max_orphan_send_states`; docstring `send_state_if_exists`. Không đụng khối SEO |
| `app/views/write.py` | `delete_warning`, `MSG_DELETE_SENT`, `MSG_DELETE_UNSURE`, câu nhắc trong popover «🗑️ Xóa» (`drafts_panel`); `kept_send_read` và tham số `extra` của `known_send_state` (khung báo đọc dòng giữ lại); docstring `autosave`, `kept_send_knowledge`, `send_lock_state` theo hành vi mới |
| `tests/test_t130_giu_trang_thai_gui.py` | Mới: 16 ca (kho 12, trang 4) |
| `tests/test_storage_send_state.py` | Đổi test T-086 (R5, Chỉ Huy duyệt) |
| `tests/test_t092_nhap_bi_xoa.py` | Đổi 8 test T-092 của tôi (R5, bảng dưới); thêm `lose_kept_state` |

`app/views/home.py` không có nút Xóa (trang Bài viết chỉ liệt kê bài đã gửi từ nháp còn trong kho), không cần sửa.

## Đổi test cũ (R5)

| Chỗ | Cũ | Mới | Lý do |
|---|---|---|---|
| `tests/test_storage_send_state.py::test_send_state_removed_with_its_draft` → đổi tên `test_send_state_kept_as_orphan_when_its_draft_goes` (T-086); docstring đầu file | Kho đầy bỏ «một»: chỉ còn dòng trạng thái của «hai»; xóa «hai»: `load_send_state` ra `None` | Kho đầy bỏ «một»: còn cả hai dòng, dòng «một» đúng trạng thái cũ; xóa «hai»: dòng «hai» còn đúng trạng thái; lưu lại «một»: `send_state_if_exists` ra đúng trạng thái (có lại khóa) | Yêu cầu 1, 5 của phiếu. **Chỉ Huy đã duyệt** trong tin giao T-130. Giữ đủ các bước cũ (dọn, xóa), đổi mong đợi theo hành vi mới, thêm bước lưu lại |
| `tests/test_t092_nhap_bi_xoa.py::test_must_exist_does_not_recreate_deleted_draft` | Sau khi xóa, `send_states` rỗng | Sau khi xóa, dòng trạng thái gửi còn; lần ghi so rồi đặt hỏng không đổi dòng đó | Ghim hành vi cũ «xóa nháp là xóa trạng thái gửi» (yêu cầu 5). Phần chính (không tạo lại, câu lỗi) giữ nguyên |
| `…::test_recreate_writes_send_state_before_draft` (2 ca) | Xóa nháp rồi «Lưu lại» khi kho bận | Thêm `lose_kept_state` sau khi xóa | Dòng giữ lại làm lần lưu lại không cần ghi gì, ca không còn kiểm thứ tự ghi; thêm bước giả dòng giữ lại cũng mất để giữ đúng ý ca (ca `save_send_state` hỏng mong `None` đã hỏng thật khi chưa thêm) |
| `…::test_draft_saved_back_without_state_keeps_this_tab_locked` (G1) | Xóa, tab khác lưu lại không kèm trạng thái gửi | Thêm `lose_kept_state` sau khi xóa | Nay dòng giữ lại gắn lại khi lưu lại (kho không còn «chưa gửi»), ca hỏng ở khẳng định «kho vẫn chưa gửi»; giữ đúng ý ca (điều tab biết chỉ lên không xuống). Ca mới `test_draft_saved_back_by_unknowing_tab_locks_fresh_session` kiểm đường T-130 |
| `…::test_recreate_keeps_unsure_lock` (2 ca) | Gửi dở / dòng hỏng, xóa, «Lưu lại» | Thêm `lose_kept_state` sau khi xóa | Ca dòng hỏng hỏng thật (dòng hỏng giữ lại, `load_send_state` ném lỗi); giữ đúng ý ca: «Lưu lại» ghi điều tab biết. Đường dòng hỏng giữ lại: `test_delete_keeps_send_state_as_orphan[dong-hong]` |
| `…::test_sent_state_seen_at_publish_step_is_known` | Xóa nháp ngay sau lần đọc ở bước Xuất bản | Thêm `lose_kept_state` trong hàm giả | Vẫn qua nhưng không còn kiểm `_wp_seen` (dòng giữ lại đã đủ); giữ đúng ý ca |
| `…::test_own_send_known_when_deleted_before_any_read` | Xóa nháp ngay khi lần gửi vừa ghi xong | Thêm `lose_kept_state` trong hàm giả | Vẫn qua nhưng không còn kiểm nhánh «kết quả lần gửi của chính tab»; giữ đúng ý ca |
| `…::test_unsure_knowledge_locks_only_when_draft_gone[nhap-bi-xoa]` | Xóa nháp «gửi dở» | Thêm `lose_kept_state` sau khi xóa | Vẫn qua nhờ dòng giữ lại; giữ đúng ý ca (khóa «gửi dở» theo điều tab biết khi nháp không còn) |

Docstring các ca trên thêm một câu ghi T-130. Không `skip`, không `xfail`, không xóa test. 3 ca T-092 vẫn qua mà không cần đổi, nay kiểm luôn đường T-130 (`test_recreate_keeps_sent_state_this_tab_knows`, `test_known_sent_stays_locked_until_confirmed_while_gone`, `test_click_through_lock_while_gone_sends_nothing`); test của Soi Lỗi T-092 không đổi.

## Thử gỡ chỗ sửa (đột biến)

Cùng script của T-092 (chép cây làm việc ra thư mục nháp, sửa đúng một chỗ, chạy các test được kỳ vọng bắt chỗ đó bằng venv của worktree; đã kiểm `seo_app` nạp từ bản sao; script ở thư mục nháp của phiên, không đưa vào repo): 11 đột biến mới của T-130 và chạy lại 20 đột biến của T-092 trên cây mới (để chắc các test T-092 đã đổi vẫn giữ đúng ý).

| Đột biến | Kết quả |
|---|---|
| N1 xóa nháp xóa luôn trạng thái gửi (như trước T-130) | bắt được |
| N2 kho đầy bỏ bớt xóa luôn trạng thái gửi | bắt được |
| N3 dọn hết dòng mồ côi (bỏ qua giới hạn) | bắt được |
| N4 xóa nháp không dọn dòng mồ côi | bắt được |
| N5 lần lưu không dọn dòng mồ côi | bắt được |
| N6 dọn giữ dòng cũ nhất thay vì mới nhất | bắt được |
| N7 dọn đụng cả trạng thái gửi của nháp còn trong kho | bắt được |
| N8 lúc thấy nháp không còn không đọc dòng giữ lại | bắt được (`test_unknowing_tab_saves_back_and_stays_locked`) |
| N9 popover «Xóa» không nhắc | bắt được |
| N10 popover: bài đã gửi nhắc như chưa rõ (mất mã bài) | bắt được |
| N11 popover: lệnh hẹn giờ/đăng chưa rõ kết quả nhắc như đã gửi | bắt được |
| M1–M20 của T-092 trên cây T-130 | cả 20 bị bắt |

Lần chạy đầu, **M7** của T-092 («Lưu lại» ghi trạng thái gửi không so rồi đặt) **không** bị bắt: từ T-130, lần lưu lại đọc dòng giữ lại ngay trước khi ghi, nên ca T-092 `test_recreate_keeps_newer_row_written_after_delete` (dòng mới hơn ghi sau lúc xóa) nay ghi đúng giá trị đó dù không so. Chỉ còn một kẽ hở cho phép so ấy: tab khác ghi đúng giữa lần đọc và lần ghi. Thêm `test_recreate_does_not_overwrite_row_written_in_between` giả đúng kẽ hở đó; chạy lại M7: bị bắt. Tổng **31/31**.

## Bảo mật (W1, W2, U1)

- **W1** (không mở thêm đường gửi): chỉ giữ thêm khóa; không đổi luồng gửi, màn hình xác nhận, so rồi đặt. Dọn dòng mồ côi không bao giờ đụng trạng thái gửi của nháp còn trong kho.
- **W2** (không xóa gì trên website): không có lệnh nào tới website. Câu nhắc nói rõ xóa nháp không xóa bài trên website và chỉ người dùng tự xóa trong trang quản trị.
- **U1:** câu nhắc là chữ cố định, mã bài là số nguyên; không `unsafe_allow_html`.
- Quét: `PYTHONUTF8=1 uvx detect-secrets scan` 6 file đổi: 1 phát hiện có sẵn (ví dụ `https://tên:mật-khẩu@…` trong docstring `app/views/write.py`, không phải bí mật); `PYTHONUTF8=1 uvx bandit` 2 file nguồn: 1 Low có sẵn (B101 `assert saved.saved_at is not None` trong `save`).

## Bằng chứng

```
# Các file test liên quan (Chỉ Huy dặn không chạy toàn bộ pytest): kho nháp, gửi nháp, hai tab,
# T-086, T-089, T-092 (cả của Soi Lỗi, Lá Chắn), T-100 (kho nháp nối kế hoạch), T-102, T-112
# (bước Xuất bản), test_app_pages.py và file mới của T-130: 45 file, như T-092 lượt 2 thêm
# tests/test_t130_giu_trang_thai_gui.py
$ PYTHONUTF8=1 uv run pytest -q -rxXf tests/test_app_drafts.py tests/test_app_images.py \
    tests/test_drafts_images.py tests/test_la_chan_t086.py tests/test_la_chan_t089.py \
    tests/test_la_chan_t100.py tests/test_plan_sync.py tests/test_soi_loi_t016_t020.py \
    tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t041.py tests/test_soi_loi_t042.py \
    tests/test_soi_loi_t055.py tests/test_soi_loi_t056.py tests/test_soi_loi_t086.py \
    tests/test_soi_loi_t089.py tests/test_soi_loi_t100.py tests/test_soi_loi_t102.py \
    tests/test_soi_loi_t107.py tests/test_soi_loi_t110.py tests/test_soi_loi_t115.py \
    tests/test_soi_loi_t117.py tests/test_storage_drafts.py tests/test_storage_send_state.py \
    tests/test_t041_drafts_seo.py tests/test_t041_links_ai.py tests/test_t041_seo_ui.py \
    tests/test_t086_send_state.py tests/test_t089_send_draft.py tests/test_t092_nhap_bi_xoa.py \
    tests/test_t100_drafts_plan.py tests/test_t101_home_page.py tests/test_t101_plan_page.py \
    tests/test_t102_publish.py tests/test_wordpress_routes_t042.py tests/test_app_pages.py \
    tests/test_la_chan_t056.py tests/test_la_chan_t102.py tests/test_t118_don_thap.py \
    tests/test_config.py tests/test_t090_meta_emoji_moi.py tests/test_soi_loi_t092.py \
    tests/test_t112_release_rules.py tests/test_soi_loi_t112.py tests/test_t112_settings_switch.py \
    tests/test_t130_giu_trang_thai_gui.py
2805 passed, 8 skipped, 4 xfailed in 3690.71s (1:01:30)
# 2026-11-05 13:18:33 → 14:20:09 (máy chạy song song 4 lượt test khác). Không ca nào hỏng, không
# XPASS. 4 xfail đều có sẵn trên main: SL-T107-3 (1), SL-T117-1 (3). 8 ca bỏ qua do hệ điều hành.

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/storage/drafts.py app/views/write.py \
    tests/test_t130_giu_trang_thai_gui.py tests/test_t092_nhap_bi_xoa.py tests/test_storage_send_state.py
5 files already formatted
```

Trước khi sửa test, chạy riêng các file kho nháp, T-086 trạng thái gửi, T-092 trên code mới: đúng 5 ca hỏng, đều là ca ghim «xóa nháp là xóa trạng thái gửi» (bảng «Đổi test cũ»). Phần giao diện (câu nhắc trong popover, khung báo) kiểm bằng AppTest, chưa mở trình duyệt thật.

`main` cục bộ nay là `c1aa6bf` (thêm phiếu, tài liệu): `git merge-tree` với nhánh không xung đột; từ `50a40a6` `main` không đổi file code nào (`app/`, `seo_app/`, `tests/conftest.py`).

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: xóa nháp đã gửi (đang gửi, gửi dở, dòng hỏng; cả khi kho đầy bỏ bớt) giữ trạng thái gửi thành dòng mồ côi; nháp được lưu lại ở bất kỳ tab nào, phiên nào vẫn khóa; nháp chưa gửi xóa như cũ.
- [x] Yêu cầu 2: dọn dòng mồ côi an toàn: chỉ dòng không có nháp, giữ 200 dòng ghi gần nhất, dọn ở mỗi lần xóa và mỗi lần lưu (mục «Thiết kế» 2).
- [x] Yêu cầu 3: popover «🗑️ Xóa» của nháp đã gửi nhắc bài đã lên website (mã bài) và xóa nháp không xóa bài trên website.
- [x] Yêu cầu 4: không lùi T-086, T-089, T-092 (45 file test liên quan qua; 20 đột biến T-092 vẫn bị bắt).
- [x] Yêu cầu 5: đổi test T-086 (Chỉ Huy duyệt) và 8 test T-092 ghim hành vi cũ hay cần giữ đúng ý ca, bảng cũ → mới.
- [x] Test liên quan + `uv run ruff check .`; đột biến 31/31 bị bắt.
- [x] Báo cáo `docs/team/reports/T-130-hoa-si.md`.
- [ ] Soi Lỗi, Lá Chắn rút gọn (chưa tới lượt).

## Rủi ro và điểm cần chú ý

1. **Dòng trạng thái gửi đã bị xóa trước T-130** (nháp xóa trước khi gộp phiếu này) không lấy lại được; khóa theo «điều tab biết» của T-092 vẫn còn cho tab đã biết.
2. **Hơn 200 lần xóa bài đã gửi** thì dòng mồ côi cũ nhất bị dọn (lý do ở «Thiết kế» 2); khóa theo điều tab biết (T-092) vẫn còn.
3. **Cả file nháp bị xóa** (`data/drafts.sqlite`) thì mất hết nháp lẫn trạng thái gửi, như trước.
4. Trang Bài viết (`home.py`, mục bài đã gửi) chỉ đọc nháp còn trong kho, không liệt kê bài của nháp đã xóa (như trước).

## Đề xuất

Không có.

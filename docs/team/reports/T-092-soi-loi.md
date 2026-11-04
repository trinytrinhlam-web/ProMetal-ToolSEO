# Báo cáo T-092 · Nháp bị xóa ở tab khác · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-092 `docs/team/tickets/T-092-nhap-bi-xoa-o-tab-khac.md` |
| Nhánh | `team/T-092`, đầu nhánh `bc8a611` (Họa Sĩ: `acb54b1` code, `7860e99` chú thích «Chép sang SiteSEO», `bc8a611` báo cáo; từ `main` `29499dd`). Thử gộp với `main` cục bộ `33bac10` (có T-112), rồi `c6bbf19` (thêm README SL-T112-4): **không xung đột**, cây `02646b5`, `08e50f2` |
| Ngày nộp | 2026-11-04 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp (SL-T092-1)**. Trọng tâm phiếu đạt: tự lưu không lặng lẽ tạo lại nháp đã bị xóa; tạo lại thì giữ trạng thái gửi tab biết; không lùi T-086, T-089; nháp cũ mở được; yêu cầu 4–6 đúng. SL-T092-1 (bước Xuất bản của tab **biết** bài đã gửi mở khóa gửi trùng khi nháp bị xóa ở tab khác) đúng mục tiêu phiếu: nên sửa ở lượt 2; không chặn Lá Chắn, không chặn gộp khi công tắc Hẹn giờ/Đăng ngay tắt; **bắt buộc sửa trước khi bật công tắc**. Gộp thử `main` cục bộ `33bac10`: không xung đột (cây `02646b5`); `main` cục bộ nay là `c6bbf19` (thêm README SL-T112-4, tài liệu): cũng không xung đột (cây `08e50f2`). 23 file liên quan trên cây gộp: 1.295 qua, 0 hỏng |

## Tóm tắt (cho chủ dự án)

- **Phần chính đã đúng.** Một bài mở ở hai tab, xóa nháp ở tab này thì tab kia **không còn lặng lẽ tạo lại** nháp: tab kia hiện khung vàng, hỏi «Lưu lại thành nháp» hay «Bỏ bài này». Lưu lại thì nháp nhớ việc bài đã gửi, nút gửi khóa như trước. Các luồng gửi nháp cũ (hai tab, gửi dở, ngắt giữa chừng) không bị ảnh hưởng; nháp cũ vẫn mở được.
- **Còn 1 chỗ hở nhỏ (Thấp).** Tab kia đang ở bước Xuất bản và **đã biết** bài đã gửi (thấy trong kho nháp): sau khi nháp bị xóa ở tab này, nút «Gửi nháp» ở tab kia **mở lại ngay**, dù khung vàng nói «Tab này biết bài đã gửi». Bấm là ra **bài thứ hai** trên website. Lúc Hẹn giờ/Đăng ngay đã bật, bài thứ hai còn được **hẹn giờ đăng công khai** (tôi đã thử). Cách sửa nhỏ: nháp không còn thì không cho gửi cho tới khi bạn chọn «Lưu lại» hay «Bỏ».
- **Việc của bạn:** không có. Trong lúc chờ sửa: đừng xóa nháp của bài đã gửi khi bài đó còn mở ở tab khác.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t092.py` | Mới: 6 ca (4 qua, 2 `xfail(strict=True)` SL-T092-1: Nháp, Hẹn giờ). Mượn khung trang Soạn bài, ảnh giả, WordPress giả của `test_app_images`, WordPress giả cho Hẹn giờ (`live`) của `test_t102_publish` |
| `docs/team/reports/T-092-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu, không gọi website thật.

## Kiểm theo trọng tâm

### 1. Tự lưu không lặng lẽ tạo lại; tạo lại giữ trạng thái gửi tab biết

Đọc mã: `DraftStore.save(..., must_exist=True)` kiểm và ghi trong một giao dịch giữ khóa ghi (`BEGIN IMMEDIATE`, `seo_app/storage/drafts.py:907-911`), lỗi thì `with conn` cuộn lại; `send_state_if_exists` (`:1011`) kiểm nháp và đọc trạng thái gửi trong một giao dịch đọc; `_connect` tạo lại file khi file nháp bị xóa lúc app chạy (lần ghi so rồi đặt sau đó báo `DraftGoneError`, không tạo lại); dọn kho đầy bỏ cả trạng thái gửi của nháp bị bỏ (đúng ca «kho đầy» của phiếu). Trang: `autosave` (`app/views/write.py:910`) chỉ so rồi đặt khi nháp đã có trong kho (`_draft_saved_at`, `open_draft` đặt khi mở nháp), `recreate_draft` (`:875`) ghi trạng thái gửi trước, nháp sau.

| Thử | Kết quả |
|---|---|
| 23 ca của Họa Sĩ (kho 6, trang 15, yêu cầu 5: 2), chạy trên cây gộp | qua |
| Nháp bị xóa rồi được tab khác lưu lại (cùng mã) | Tab này hết khung báo, tự lưu tiếp như hai tab cùng sửa một nháp (tab lưu sau thắng), không ra nháp thứ hai |
| Cả file nháp bị xóa khi app đang chạy | Báo, không tạo lại; bấm «Lưu lại thành nháp» thì có lại đúng nội dung |
| Đối chứng: tab **tự** gửi bài 501, rồi nháp bị xóa ở tab khác | Vẫn phải tick «Tạo thêm…» mới gửi được (cờ `_wp_sent` của tab); website một bài |
| Đối chứng: nháp **còn**, tab thấy «đã gửi 777» | Khóa qua 3 lần vẽ |
| Tab **biết** «đã gửi 777» (thấy trong kho, không tự gửi), nháp bị xóa ở tab khác | Khung báo đúng «Tab này biết bài đã gửi», nhưng nút gửi **mở**: bấm là tạo bài 501 (Nháp); Hẹn giờ: tick xác nhận, tạo bài và **hẹn giờ** (`future`) → **SL-T092-1** |
| Ba tab: tab chưa từng thấy trạng thái gửi bấm «Lưu lại» (khung báo đã cảnh báo «tab này không biết…»), tab biết «đã gửi 777» vẽ lại | Tab biết không thấy khung báo (nháp đã có lại), lần đọc kho «chưa gửi» ghi đè điều tab biết: nút mở, bấm là ra bài thứ hai → **G1** |

### 2. Không lùi T-086, T-089 (hai tab, ngắt giữa chừng, gửi dở, băm ảnh)

Lô B trên cây gộp (6 file: `test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`, `test_t089_send_draft`, `test_soi_loi_t089` (đã đổi theo R5), `test_la_chan_t089`): **136 passed, 0 failed**. Luồng «Gửi nháp» đầy đủ (`test_app_images`), bước Xuất bản T-102, T-112: lô D, qua (mục 6). Đọc mã: luồng gửi (`send_and_record`, `record_outcome`, `finish_send`, bước Xuất bản) không đổi; T-092 chỉ đọc `_wp_seen`, `_wp_sent`, `_wp_maybe_draft`, `_wp_result`.

### 3. Nháp cũ vẫn mở được

`test_old_draft_still_opens_and_saves` (khuôn 1) của Họa Sĩ, `tests/test_drafts_images.py`, `tests/test_t100_drafts_plan.py` (khuôn 1, 2): qua (lô A).

### 4. Yêu cầu 4–6

- **Yêu cầu 4:** `client.showErrorDetails = "type"` đã có ở `.streamlit/config.toml:19` từ T-118, Họa Sĩ không sửa; `tests/test_t118_don_thap.py`, `tests/test_app_pages.py` qua.
- **Yêu cầu 5:** chú thích «Chép sang SiteSEO» khớp README trên `main` `33bac10` (mục 10, `README.md:401`: tiêu đề, mô tả dán vào hộp SiteSEO; «Đường dẫn thì app đã gửi kèm bài»), thêm chỗ dán khi sửa tay (ô đường dẫn của bài, không phải hộp SiteSEO) đúng đề xuất Lá Chắn T-095. Đúng hành vi: T-102 gửi `slug` kèm bài. `.env.example`: tên đăng nhập của «tài khoản Biên tập viên riêng», mật khẩu ứng dụng «tạo trên chính tài khoản đó», đúng đề xuất; `tests/test_config.py` qua.
- **Yêu cầu 6:** `keyword_problem` dùng `odd_char_messages`. `odd_char_kinds` xét đúng các ký tự `has_odd_chars` thấy, nên có ký tự lạ thì câu báo không bao giờ rỗng (không lọt «ghi được»); có cả ký tự điều khiển lẫn emoji mới thì ra hai câu. `tests/test_t041_seo_ui.py`, `tests/test_t090_meta_emoji_moi.py` qua.

### 5. R5

| Chỗ | Đối chiếu |
|---|---|
| `tests/test_t041_seo_ui.py:710-728` (`ODD_KEYWORD_MESSAGE`, thêm ca `emoji-moi`) | Đúng duyệt (yêu cầu 6, Chỉ Huy). Câu mới đầy đủ hơn, không bớt ca, vẫn Chặn, vẫn kiểm bước Xuất bản |
| `tests/test_soi_loi_t089.py::test_draft_deleted_elsewhere_while_sending_comes_back_locked` (ca của tôi, T-089) | Thêm 3 dòng (nháp **không** bị tạo lại; có khung báo; bấm «Lưu lại thành nháp») và 2 dòng docstring; giữ nguyên mọi khẳng định khóa («đã gửi 501», phiên mới nút khóa). Đúng ý ca (nháp bị xóa giữa lúc gửi, quay lại vẫn khóa), không nới; là hệ quả trực tiếp của yêu cầu 1. Tôi (người viết ca) đồng ý; còn chờ Chỉ Huy duyệt chính thức như Họa Sĩ xin |

Họa Sĩ không thêm `skip` hay `xfail`, không xóa test; `xfail` mới duy nhất là 2 ca SL-T092-1 của tôi.

### 6. Gộp thử với `main` cục bộ (`33bac10`, rồi `c6bbf19`)

- `git merge-tree` nhánh (`bc8a611`) với `main` cục bộ `33bac10` (có T-112): **không xung đột**, cây `02646b5`. Hai bên cùng sửa `app/views/write.py` ở hai vùng khác nhau (T-092: tự lưu, mở nháp, chú thích, câu từ khóa; T-112: bước Xuất bản, Cài đặt).
- Chạy chọn lọc trên cây `02646b5` qua `run_list.sh` (kiểm danh sách, thiếu file thì dừng; dòng đầu mỗi lô đã xem), 4 lô nối tiếp, mỗi lúc một tiến trình (RAM còn ít):

| Lô | File | Kết quả |
|---|---|---|
| A · T-092, kho nháp, nháp cũ | `test_t092_nhap_bi_xoa`, `test_soi_loi_t092`, `test_storage_drafts`, `test_storage_send_state`, `test_app_drafts`, `test_drafts_images`, `test_t100_drafts_plan` | 342 passed, 1 skipped, 2 xfailed (SL-T092-1), 0 failed |
| B · T-086, T-089 | `test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`, `test_t089_send_draft`, `test_soi_loi_t089`, `test_la_chan_t089` | 136 passed, 0 failed |
| C · yêu cầu 4–6 | `test_t041_seo_ui`, `test_soi_loi_t041`, `test_t090_meta_emoji_moi`, `test_config`, `test_t118_don_thap` | 627 passed, 1 skipped, 0 failed |
| D · «Gửi nháp», Xuất bản (T-102, T-112), các trang | `test_app_images`, `test_t102_publish`, `test_t112_release_rules`, `test_soi_loi_t112`, `test_app_pages` | 190 passed, 1 xfailed (SL-T112-4, lúc đó chưa sửa trên `main`), 0 failed |

Cộng: **1.295 passed, 2 skipped, 3 xfailed, 0 failed, 0 XPASS**. 2 ca bỏ qua do hệ điều hành, có từ trước (`test_drafts_images.py:645` symlink chỉ thử trên Mac/Linux; `test_t118_don_thap.py:232` Windows không có `os.environb`).
- **`main` cục bộ mới `c6bbf19`** (T-112 lượt 4: README luật Hẹn giờ SL-T112-4, gỡ 1 `xfail`; biên bản T-116 nhóm 5): gộp **không xung đột**, cây `08e50f2`. So với cây `02646b5` chỉ khác `README.md`, `tests/test_soi_loi_t112.py`, tài liệu: không đổi code, nên các lô trên vẫn đúng cho code. Chạy lại mọi ca đọc README (`test_t092_nhap_bi_xoa` ca chú thích «Chép sang SiteSEO», `test_soi_loi_t112`, `test_soi_loi_t106`, `test_la_chan_t093`, `-k "readme or siteseo_caption"`): **6 passed**.

### 7. Đột biến (của tôi, nhỏ)

Họa Sĩ đã chạy 16 đột biến (16/16 bị bắt). Tôi chạy thêm 3 trên bản sao cây gộp (`mutate092.py`), với file của tôi:

| Đột biến | Kết quả |
|---|---|
| N1 tự lưu không coi nháp đã có trong kho (`stored = False`: ghi đè không so) | Bị bắt (`test_doi_chung_tab_tu_gui_van_khoa_sau_khi_nhap_bi_xoa`) |
| N2 không bao giờ báo nháp không còn | Bị bắt (như trên) |
| N3 «Lưu lại thành nháp» không ghi trạng thái gửi | Sống sót với file của tôi (không ca nào của tôi bấm «Lưu lại» khi tab biết bài đã gửi); bộ ca của Họa Sĩ bắt (`test_recreate_keeps_sent_state_this_tab_knows`) |

Bản sao được trả nguyên sau mỗi lượt (so với `git show` cây gộp: khớp).

## Lỗi tìm ra

### SL-T092-1 · Thấp · Tab biết bài đã gửi, nháp bị xóa ở tab khác: bước Xuất bản mở khóa gửi trùng

- **Chỗ:** `app/views/write.py`: bước Xuất bản khóa gửi trùng chỉ theo trạng thái đọc từ kho (`saved_send_state()`) và cờ của chính tab (`_wp_sent`, `_wp_maybe_draft`) (`:4184-4193`). Nháp bị xóa thì kho đọc ra «chưa gửi»; điều tab biết (`_draft_send_known`, `known_send_state()`, `:848`) chỉ dùng cho khung báo và cho «Lưu lại thành nháp», bước Xuất bản không dùng. Lần gửi giành «đang gửi» với `seen = (None, False)` (`:4124`, `:4225`) không đòi nháp còn trong kho.
- **Thử:** bài mở ở bước Xuất bản; tab khác gửi xong bài 777 (tab này vẽ lại: «đã gửi», phải tick «Tạo thêm…»); tab khác xóa nháp; tab này vẽ lại: khung vàng «Tab này biết bài đã gửi…», **nút «📤 Gửi nháp» mở**, bấm là tạo bài 501 (website có bài thứ hai; kho có dòng trạng thái gửi «đã gửi 501» không có nháp đi kèm). Hẹn giờ (công tắc bật): tick xác nhận, bấm: tạo bài 501 và lệnh `{"status": "future", …}` đi (bài thứ hai được hẹn giờ đăng công khai). Ngay lần vẽ đầu sau khi xóa nút đã mở (bấm đúng lần đó thì T-089 chặn vì `_wp_seen` cũ khác kho; lần vẽ sau thì không).
- **Hậu quả:** đúng điều phiếu muốn chặn («không bị mất khóa gửi trùng chỉ vì người dùng xóa nháp ở tab này trong lúc tab khác vẫn mở bài đó»): T-092 chặn đường tự lưu, còn đường bấm gửi thẳng ở bước Xuất bản. Không phải lỗi lùi (có từ trước T-092). Khung báo nói tab biết bài đã gửi và «lưu lại thì … nút gửi vẫn khóa như trước», dễ hiểu lầm là đang khóa. Công tắc tắt (mặc định): bài nháp thứ hai, mức **Thấp** như Lá Chắn T-089 đặt cho lỗi gốc. Công tắc bật: bài thứ hai lên công khai (trùng nội dung, hại SEO): **sửa trước khi bật công tắc**.
- **Test:** `test_sl_t092_1_tab_biet_da_gui_nhap_bi_xoa_khong_gui_trung`, `test_sl_t092_1_hen_gio_cung_mo_khoa` (xfail strict; `--runxfail` hỏng đúng ở «website có bài thứ hai»); đối chứng `test_doi_chung_tab_tu_gui_…`, `test_doi_chung_nhap_con_…` qua.
- **Gợi ý (chọn một):** (a) lần gửi đòi nháp còn trong kho: giành «đang gửi» kiểu so rồi đặt cùng giao dịch với kiểm nháp còn (như `save(must_exist=True)`), nháp không còn thì không gửi, báo «Nháp không còn trong kho: bấm «Lưu lại thành nháp» hay «Bỏ bài này» trước»; (b) bước Xuất bản lấy `known_send_state()` làm trạng thái khóa khi nháp không còn (khóa như `saved`); (c) đề xuất 1 của Họa Sĩ (giữ trạng thái gửi khi xóa nháp đã gửi) chặn được cả SL-T092-1 lẫn G1. Cách (a) gọn nhất, không phụ thuộc lần tự lưu đã chạy hay chưa.

## Ghi nhận (không tính lỗi)

- **G1 · Ba tab, điều tab biết bị ghi đè khi tab khác lưu lại nháp:** tab A biết «đã gửi 777»; nháp bị xóa; tab B (chưa từng thấy trạng thái gửi; khung báo đã nói rõ «Nếu bài đã được gửi lên website ở tab khác thì tab này không biết: lưu lại rồi gửi nữa sẽ tạo thêm một bài») vẫn bấm «Lưu lại thành nháp»: nháp có lại **không** trạng thái gửi; tab A vẽ lại không thấy khung báo, lần đọc kho «chưa gửi» ghi đè `_draft_send_known`, nút mở, bấm là ra bài thứ hai (thử tạm, không commit). Là biến thể của «khoảng hở còn lại» Họa Sĩ đã nêu (mục Rủi ro 1), cần người dùng bỏ qua cảnh báo; đề xuất 1 của Họa Sĩ (giữ trạng thái gửi khi xóa) chặn được. Nếu làm gợi ý (b) của SL-T092-1 thì nên giữ điều tab biết theo kiểu «chỉ lên, không xuống» (đã gửi không bị một lần đọc «chưa gửi» xóa), như khóa đơn điệu của T-086.
- **G2 · Yêu cầu 4 không có thay đổi:** đã có từ T-118 trên `main`, Họa Sĩ chỉ kiểm. Đúng.

## Lệnh đã chạy

- `pytest tests/test_soi_loi_t092.py` (cây nhánh): 4 passed, 2 xfailed; `--runxfail -k sl_t092_1`: hỏng đúng ở «website có bài thứ hai» (Nháp: tạo bài 501; Hẹn giờ: tạo bài 501 và lệnh `future` đi).
- Thử tạm (không commit): ba tab (G1): tab biết «đã gửi 777» mất khóa sau khi tab không biết bấm «Lưu lại»; website có bài thứ hai.
- Cây gộp `02646b5`, 4 lô chọn lọc, 23 file: 1.295 passed, 2 skipped, 3 xfailed, 0 failed. Cây gộp `08e50f2` (`main` `c6bbf19`), ca đọc README: 6 passed.
- Đột biến: N1, N2 bị bắt; N3 sống sót ở file của tôi, bị bộ ca Họa Sĩ bắt.
- `uv run ruff check .`: sạch.
- `detect-secrets` (`PYTHONUTF8=1`), quét bản sao trong thư mục ngoài git cùng file mồi tiếng Việt: sạch (chỉ file mồi bị báo; file test và báo cáo không có gì).
- Script: thư mục ghi chú chung `T-092-soi-loi-scripts/` (`run_list.sh`, `mutate092.py`).

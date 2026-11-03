# Báo cáo T-092 · Nháp bị xóa ở tab khác: tự lưu không lặng lẽ tạo lại, giữ khóa gửi trùng

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-092](../tickets/T-092-nhap-bi-xoa-o-tab-khac.md) |
| Ngày nộp | 2026-11-03 |
| Nhánh | `team/T-092` (từ `main` `29499dd`) |
| Kết quả | Hoàn thành: yêu cầu 1–3 (trọng tâm), 5, 6; yêu cầu 4 đã có từ T-118, chỉ kiểm. Đổi 2 test cũ theo R5 (bảng «Đổi test cũ»): một test Chỉ Huy đã duyệt (yêu cầu 6), một test **xin duyệt** khi gộp (hệ quả trực tiếp của yêu cầu 1) |

## Tóm tắt (cho chủ dự án)

Trước đây, nếu một bài đang mở ở hai tab mà bạn xóa nháp ở tab này, thì tab kia tự lưu và **lặng lẽ tạo lại** nháp. Nháp tạo lại đã quên việc bài đã gửi lên website, nên nút «Gửi nháp» mở lại, bấm là ra bài trùng. Nay tab kia không tự tạo lại nữa: đầu trang hiện khung vàng «**Nháp của bài này không còn trong kho nháp** (có thể vừa bị xóa ở tab khác)…» kèm hai nút **💾 Lưu lại thành nháp** và **🗑️ Bỏ bài này**. Bấm lưu lại thì nháp có lại đúng nội dung đang có ở tab đó; nếu tab đó biết bài đã gửi (hay gửi dở) thì nháp vẫn nhớ, nút gửi vẫn khóa như trước. Tab chưa từng thấy bài được gửi thì khung nói rõ: gửi ở tab khác thì tab này không biết, lưu lại rồi gửi nữa sẽ tạo thêm một bài.

Kèm theo ba việc nhỏ: câu báo từ khóa chính có biểu tượng cảm xúc rất mới nay nói đúng «phần mềm chưa nhận ra» (không còn nói «không nhìn thấy»); chú thích khung «Chép sang SiteSEO» nói rõ tiêu đề, mô tả dán vào hộp SiteSEO, còn đường dẫn thì phần mềm đã gửi kèm bài (muốn sửa tay thì dán vào **ô đường dẫn của bài**, không phải hộp SiteSEO); file mẫu `.env.example` ghi rõ tên đăng nhập là của **tài khoản Biên tập viên riêng** và mật khẩu ứng dụng **tạo trên chính tài khoản đó**.

## Yêu cầu → cách làm → test

| # | Yêu cầu | Cách làm | Test (`tests/test_t092_nhap_bi_xoa.py` nếu không ghi file) |
|---|---|---|---|
| 1 | Tự lưu của tab còn mở không lặng lẽ tạo lại nháp đã bị xóa; báo rõ, hỏi tạo lại; tạo lại thì giữ trạng thái gửi tab đó biết | **Kho:** `DraftStore.save(..., must_exist=True)` (`seo_app/storage/drafts.py:876`): so rồi đặt trong một giao dịch giữ khóa ghi từ đầu (`BEGIN IMMEDIATE`, `:907-911`), nháp không còn thì không ghi gì, báo `DraftGoneError` (`:159`, con của `DraftError`, câu cố định `:143`). `send_state_if_exists` (`:1011`): kiểm nháp còn và đọc trạng thái gửi trong **một** giao dịch đọc (`BEGIN`, `:1019`); `None` khi nháp không còn, kể cả còn dòng trạng thái gửi mồ côi. **Trang:** `autosave` (`app/views/write.py:910`): nháp đã có trong kho thì mỗi lần chạy gọi `send_state_if_exists` (`:928`), nhớ vào `_draft_send_known`; lưu thì `save(must_exist=True)` (`:943`). Nháp không còn: không lưu, `gone_notice` (`:893`) hiện khung báo cố định (`MSG_DRAFT_GONE`, `MSG_GONE_SENT` / `MSG_GONE_UNKNOWN`, `:226-237`) và hai nút. «💾 Lưu lại thành nháp» → `recreate_draft` (`:875`): ghi trạng thái gửi tab biết (`known_send_state`, `:848`) **trước**, chỉ khi kho chưa có dòng nào (`expected=(None, False)`), rồi mới tạo lại nháp. «🗑️ Bỏ bài này» → «Bỏ hẳn» → `discard_gone_draft` (`:840`): xóa trắng trang như khi xóa đúng nháp đang mở | Kho: `test_must_exist_does_not_recreate_deleted_draft`, `test_must_exist_overwrites_draft_still_there`, `test_must_exist_after_prune_or_drafts_file_removed`, `test_send_state_if_exists`, `test_must_exist_check_and_write_in_one_write_transaction`, `test_send_state_if_exists_reads_in_one_transaction`. Trang: `test_autosave_does_not_recreate_draft_deleted_in_other_tab` (xóa bằng nút «Xóa hẳn» ở tab 2 thật), `test_recreate_on_request_keeps_content`, `test_recreate_keeps_sent_state_this_tab_knows`, `test_sent_state_seen_at_publish_step_is_known`, `test_own_send_known_when_deleted_before_any_read`, `test_recreate_keeps_unsure_lock` (gửi dở, dòng hỏng), `test_recreate_keeps_newer_row_written_after_delete`, `test_recreate_writes_send_state_before_draft` (2 ca), `test_deleted_between_check_and_save_is_not_recreated`, `test_discard_clears_page_and_never_recreates` |
| 2 | Không lùi T-086, T-089 (hai tab, ngắt giữa chừng, gửi dở, băm ảnh) | Không sửa luồng gửi (`send_and_record`, `record_outcome`, `finish_send`, `apply_send`, `publish_panel` giữ nguyên); chỉ **đọc** `_wp_seen`, `_wp_sent`, `_wp_maybe_draft`, `_wp_result`. Hai tab cùng sửa một nháp **còn** trong kho vẫn ghi đè như trước (tab lưu sau thắng) | `test_two_tabs_editing_same_draft_still_autosave`; mọi file test gửi nháp, kho nháp, hai tab của T-056/T-086/T-089/T-100/T-102 (mục «Bằng chứng») |
| 3 | Nháp cũ vẫn mở được; test cho ca mới | Đường mở nháp (`load`, `open_draft`) không đổi; lần lưu so rồi đặt chỉ cần nháp còn trong kho, không quan tâm khuôn | `test_old_draft_still_opens_and_saves` (khuôn 1, trước T-055: mở, sửa, lưu, nâng lên khuôn 3); `test_new_draft_first_save_still_creates`; `tests/test_drafts_images.py`, `tests/test_t100_drafts_plan.py` (khuôn 1, 2) vẫn qua |
| 4 | `client.showErrorDetails = "type"` | Đã có ở `.streamlit/config.toml:19` (T-118). **Không sửa** | `tests/test_t118_don_thap.py`, `tests/test_app_pages.py` qua |
| 5 | Chú thích «Chép sang SiteSEO»; chú thích `.env.example` | `siteseo_panel` (`app/views/write.py:2647`): «Bấm biểu tượng ở góc từng khung để chép. Trong trang sửa bài nháp của WordPress: tiêu đề, mô tả dán vào hộp SiteSEO. Đường dẫn thì phần mềm đã gửi kèm bài; muốn sửa tay thì dán vào ô đường dẫn (slug) của bài, không phải hộp SiteSEO. Muốn phần mềm tự ghi tiêu đề, mô tả: bật «Ghi SEO lên website» ở bước Xuất bản.» Lá Chắn T-095 đề xuất theo README lúc đó («đường dẫn dán vào ô đường dẫn (slug) của bài»). Nhưng từ T-102 phần mềm **đã gửi đường dẫn kèm bài** (`create_draft_with_images(..., slug=package.slug)`, `app/views/write.py:3690`); README trên `main` (`README.md:401`) còn câu cũ, README của T-112 (chưa gộp) đã sửa thành «Đường dẫn thì app đã gửi kèm bài (mục 11); khung này để xem, hay chép khi muốn sửa tay». Chú thích theo đúng hành vi và README của T-112, giữ ý chính của đề xuất (đường dẫn vào ô của bài, không vào hộp SiteSEO). Không sửa README (ngoài phạm vi, T-112 đã sửa). `.env.example:23-28`: «Tên đăng nhập của tài khoản Biên tập viên riêng cho app (không dùng tài khoản quản trị), không phải tên đặt cho Application Password. Xem README mục 6.»; «Application Password (mật khẩu ứng dụng) tạo trên chính tài khoản đó: đăng nhập bằng tài khoản Biên tập viên, vào Hồ sơ > Application Passwords. …» | `test_siteseo_caption_says_where_each_box_goes` (so với README phần chung của README cũ và README T-112: «tiêu đề, mô tả dán vào hộp SiteSEO»), `test_env_example_names_the_editor_account`; `tests/test_config.py` (đủ biến, không giá trị thật) qua |
| 6 | Câu báo từ khóa chính có emoji mới dùng `odd_char_messages` | `keyword_problem` (`app/views/write.py:2598`): `" ".join(onpage_meta.odd_char_messages(KEYWORD_LABEL, text))` đúng như đề xuất Thợ Máy T-090; bỏ hằng `MSG_KEYWORD_ODD` không còn dùng. Vẫn Chặn đúng các ký tự như trước (`has_odd_chars` giữ làm điều kiện) | `tests/test_t041_seo_ui.py::test_bad_keyword_is_flagged_on_seo_and_publish_steps` (đổi câu ở `:711`, thêm ca `emoji-moi` U+1FAE9: bước SEO «Chặn» + câu «chưa nhận ra», bước Xuất bản «⚠️ SEO: … Từ khóa chính») |

## Thiết kế: vì sao thế này

1. **So rồi đặt theo việc nháp còn hay không, không theo giờ lưu.** Phiếu gợi ý «dấu phiên bản». So theo giờ lưu (`saved_at`) thì mọi lần hai tab cùng sửa một nháp **còn** trong kho cũng thành xung đột, phải thêm màn hình xử lý xung đột và đổi luồng hai tab của T-086/T-089: ngoài phiếu, dễ lùi. Cách đã làm chỉ chặn đúng ca phiếu nêu (nháp đã bị xóa: tab khác bấm «Xóa hẳn», kho đầy bỏ bớt, file nháp bị xóa khi app đang chạy); hai tab cùng sửa vẫn như trước. Kiểm và ghi trong một giao dịch giữ khóa ghi: lần xóa ở tab khác không chen vào giữa được (test `…_in_one_write_transaction` cho tab khác xóa đúng giữa lần kiểm và lần ghi: lần xóa phải đợi).
2. **Mỗi lần chạy kiểm nháp còn, kèm đọc trạng thái gửi** (một giao dịch đọc). Nhờ vậy trang báo ngay cả khi người dùng chưa sửa gì, và tab luôn có trạng thái gửi mới nhất khi nháp còn. Tốn thêm một lần đọc SQLite nhỏ mỗi lần chạy (trang đã đọc kho vài lần mỗi lần chạy).
3. **«Trạng thái gửi tab biết»** (`known_send_state`): lần đọc cuối khi nháp còn (lúc tự lưu) và lần đọc ở bước Xuất bản (`_wp_seen`), lấy dòng ghi muộn nhất. Cần cả hai: lần đọc ở bước Xuất bản chạy trước lần tự lưu trong cùng lần chạy, nên tab khác gửi rồi xóa nháp đúng giữa hai lần đọc đó thì chỉ `_wp_seen` biết (test `…_seen_at_publish_step_is_known`). Lúc thấy nháp không còn thì gộp ngay vào `_draft_send_known`: tab đứng ở bước Xuất bản, mỗi lần vẽ lại đọc ra «chưa gửi» (dòng đã bị xóa cùng nháp) và ghi đè `_wp_seen` (lỗi này tìm được khi chạy test lần đầu, đã sửa). Không lần đọc nào thấy gì mà chính tab này vừa gửi (gửi xong trang chạy lại ngay bằng `st.rerun`, lần tự lưu của lần gửi không chạy; nháp bị xóa ngay sau lần gửi, trước lần đọc kế tiếp) thì lấy kết quả lần gửi của tab (`_wp_sent`, `_wp_result`, `_wp_maybe_draft`; test `…_own_send_known_when_deleted_before_any_read`). Dòng hỏng thì coi như lần gửi trước chưa rõ kết quả (khóa «gửi dở», giữ mã bài nếu biết).
4. **Tạo lại: trạng thái gửi trước, nháp sau.** Ghi trạng thái gửi kiểu so rồi đặt với «chưa gửi»: kho đã có dòng ghi sau lúc xóa (kết quả lần gửi đang chạy, SL-T089-2; tab khác) thì dòng đó mới hơn, giữ nguyên. Hỏng giữa hai bước thì chỉ còn dòng trạng thái gửi không có nháp đi kèm (vô hại, Lá Chắn T-089 đã nhận định), không bao giờ có nháp tạo lại thiếu khóa (test `…_writes_send_state_before_draft` cho hỏng ở từng bước).
5. **Xóa ở chính tab đang mở:** như cũ (xóa trắng trang, không hỏi), chỉ sửa câu chú thích trong code.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | `DraftGoneError`; `save(..., must_exist=False)` so rồi đặt khi `must_exist`; `send_state_if_exists`. Không đụng khối SEO, `delete`, các bảng |
| `app/views/write.py` | `autosave` kiểm nháp còn, lưu so rồi đặt; `gone_notice`, `recreate_draft`, `known_send_state`, `discard_gone_draft`, `ask_recreate`; 3 câu báo; `DRAFT_FLAGS` thêm 2 khóa; câu `keyword_problem` (yêu cầu 6); chú thích `siteseo_panel` (yêu cầu 5). Không sửa vùng bước Xuất bản |
| `.env.example` | Chú thích `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD` (yêu cầu 5) |
| `tests/test_t092_nhap_bi_xoa.py` | Mới: 23 test (kho 6, trang 15, yêu cầu 5: 2) |
| `tests/test_t041_seo_ui.py` | Câu `ODD_KEYWORD_MESSAGE` mới, thêm ca `emoji-moi` (yêu cầu 6, R5 đã duyệt) |
| `tests/test_soi_loi_t089.py` | `test_draft_deleted_elsewhere_while_sending_comes_back_locked` theo hành vi mới (R5, xin duyệt) |

## Đổi test cũ (R5)

| Chỗ | Cũ | Mới | Lý do |
|---|---|---|---|
| `tests/test_t041_seo_ui.py:710-714` (`ODD_KEYWORD_MESSAGE`, test `test_bad_keyword_is_flagged_on_seo_and_publish_steps`) | «Từ khóa chính có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ nơi khác).» | Câu của `odd_char_messages`: thêm «Xóa ô rồi gõ lại chữ thường.» (ca ESC, U+E000). Thêm ca `emoji-moi` (U+1FAE9) mong câu «… phần mềm chưa nhận ra nên không ghi được (có thể là biểu tượng cảm xúc rất mới). …» | Yêu cầu 6. **Chỉ Huy B đã duyệt** trong tin giao T-092. Không bớt ca, vẫn Chặn, vẫn kiểm không chép từ khóa, vẫn kiểm bước Xuất bản |
| `tests/test_soi_loi_t089.py:684-714` (`test_draft_deleted_elsewhere_while_sending_comes_back_locked`, Soi Lỗi T-089) | Tab 1 làm tiếp → lần tự lưu **tạo lại** nháp → khẳng định nháp có trong kho, «đã gửi 501», phiên mới nút khóa | Tab 1 làm tiếp → khẳng định nháp **không** bị tạo lại và có khung báo; bấm «💾 Lưu lại thành nháp» → nháp có trong kho; giữ nguyên hai khẳng định khóa («đã gửi 501», phiên mới nút khóa). Docstring thêm 2 dòng ghi T-092 | Hệ quả trực tiếp yêu cầu 1 (tự lưu không lặng lẽ tạo lại). Test cũ đòi đúng hành vi phiếu bỏ đi. Không bớt khẳng định nào về khóa, thêm khẳng định mới. **Xin Chỉ Huy duyệt** khi gộp |

Không `skip`, không `xfail` mới, không xóa test.

## Thử gỡ chỗ sửa (đột biến)

Script chép cây làm việc (`app`, `seo_app`, `tests`, `config`, `.streamlit`, `README.md`, `.env.example`, `pyproject.toml`) ra thư mục nháp, sửa đúng một chỗ, chạy các test được kỳ vọng bắt chỗ đó bằng venv của worktree (`PYTHONPATH` trỏ bản sao; đã kiểm `seo_app` nạp từ bản sao). Script ở thư mục nháp của phiên, không đưa vào repo.

| Đột biến | Kết quả |
|---|---|
| M1 tự lưu ghi đè không so (`save(snap)` thay `save(snap, must_exist=stored)`) | bắt được (`…_deleted_between_check_and_save_…`) |
| M2 bỏ lần kiểm nháp còn mỗi lần chạy | bắt được (`…_discard_…`: chạy lại không sửa gì thì không còn báo) |
| M3 kho: so rồi đặt không giữ khóa ghi (bỏ `BEGIN IMMEDIATE`) | bắt được (`…_in_one_write_transaction`: tab khác xóa được giữa lần kiểm và lần ghi) |
| M4 kho: đọc trạng thái gửi không cùng giao dịch (bỏ `BEGIN`) | bắt được (`…_reads_in_one_transaction`: đọc ra «nháp còn, chưa gửi» cho nháp đã gửi) |
| M5 kho: bỏ qua `must_exist` | bắt được (3 test) |
| M6 tạo lại nháp trước, trạng thái gửi sau | bắt được (2 ca `…_writes_send_state_before_draft`) |
| M7 tạo lại: ghi trạng thái gửi không so | bắt được (`…_keeps_newer_row_written_after_delete`) |
| M8 tạo lại: không ghi trạng thái gửi | bắt được (3 ca) |
| M9 bỏ lần đọc ở bước Xuất bản (`_wp_seen`) | bắt được (`…_seen_at_publish_step_is_known`) |
| M10 bỏ qua dòng hỏng | bắt được (`…_keeps_unsure_lock[dòng hỏng]`) |
| M11 bỏ kết quả lần gửi của chính tab | bắt được (`…_own_send_known_when_deleted_before_any_read`) |
| M12 không gộp lúc thấy nháp không còn | bắt được (`…_seen_at_publish_step_is_known`) |
| M13 lặng lẽ tạo lại như trước T-092 | bắt được (3 test, gồm test Soi Lỗi T-089 đã đổi) |
| M14 «Bỏ hẳn» không xóa trắng | bắt được |
| M15 câu từ khóa emoji mới như cũ (yêu cầu 6) | bắt được (ca ESC, U+E000, `emoji-moi`) |
| M16 chú thích «Chép sang SiteSEO» như cũ (yêu cầu 5) | bắt được |

Lần chạy đầu, M9 và M12 **không** bị bắt: test khi ấy cho chính tab này gửi, nên nhánh «kết quả lần gửi của tab» (M11) che mất. Đã viết lại test đó theo đúng ca chỉ lần đọc ở bước Xuất bản mới biết (tab **khác** gửi bài 777), chạy lại M9, M11, M12: cả ba bắt được.

## Bảo mật (W1, W2, U1)

- **W1:** không đổi luồng gửi, hình thức gửi, màn hình xác nhận. Nháp tạo lại không mở khóa thêm so với trước lúc bị xóa: chỉ ghi trạng thái gửi tab biết khi kho chưa có dòng nào; dòng có sẵn (mới hơn) giữ nguyên.
- **W2:** không có lệnh nào lên website. «Bỏ hẳn» chỉ xóa trắng trang của tab đó, không xóa gì trong kho (dòng trạng thái gửi mồ côi, nếu có, giữ nguyên).
- **U1:** khung báo là chữ cố định; câu lỗi của kho nháp (khi lưu lại hỏng) qua `escape_markdown`; không `unsafe_allow_html`.
- Quét: `PYTHONUTF8=1 uvx detect-secrets scan` 6 file đã đổi: 2 phát hiện, đều có sẵn từ trước (docstring ví dụ `https://tên:mật-khẩu@…` trong `app/views/write.py`, chuỗi mồi `MAT-KHAU-GIA-L4` trong `tests/test_t041_seo_ui.py`); file mới, `.env.example`, `drafts.py` không có gì. `PYTHONUTF8=1 uvx bandit` 2 file nguồn: 1 Low (B101 `assert saved.saved_at is not None`, có sẵn).

## Bằng chứng

```
# Các file test liên quan (Chỉ Huy dặn không chạy toàn bộ pytest): mọi file nhắc tới gửi nháp
# (grep "send_and_record|finish_send|record_outcome|save_send_state|load_send_state") hay kho
# nháp, tự lưu (grep "DraftStore|autosave|Xóa hẳn|draft_id"), cộng test_app_pages.py,
# test_la_chan_t056.py, test_la_chan_t102.py, test_t118_don_thap.py (yêu cầu 4),
# test_config.py (.env.example), test_t090_meta_emoji_moi.py (yêu cầu 6): 40 file
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
    tests/test_config.py tests/test_t090_meta_emoji_moi.py
2699 passed, 8 skipped, 7 xfailed in 2439.21s (0:40:39)
# 22:32:58 → 23:13:43. Không ca nào hỏng, không XPASS. 7 xfail đều có sẵn trên main:
# SL-T102-1 (3 ca, T-112 sửa, chưa gộp), SL-T107-3 (1), SL-T117-1 (3).

# Sau lần chạy trên, viết lại một test trong file T-092 (mục «Thử gỡ chỗ sửa»); code không đổi.
$ PYTHONUTF8=1 uv run pytest -q tests/test_t092_nhap_bi_xoa.py
23 passed in 65.28s

# Sau đó đổi câu chú thích «Chép sang SiteSEO» (đường dẫn đã gửi kèm bài, mục yêu cầu 5) và test
# chú thích; chạy lại phần liên quan, đột biến M16 vẫn bị bắt:
$ PYTHONUTF8=1 uv run pytest -q \
    tests/test_t092_nhap_bi_xoa.py::test_siteseo_caption_says_where_each_box_goes \
    tests/test_t041_seo_ui.py
51 passed in 109.25s

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check app/views/write.py seo_app/storage/drafts.py \
    tests/test_t092_nhap_bi_xoa.py tests/test_t041_seo_ui.py tests/test_soi_loi_t089.py
5 files already formatted
```

**Thử trên trình duyệt thật** (app chạy từ worktree, cổng 8505, cấu hình tạm: mật khẩu thử, không WordPress, không khóa AI; `launch.json` sao lưu trước, trả lại đúng bản cũ sau, cùng mã băm SHA-256; file mật khẩu thử đã xóa): tab 1 gõ từ khóa (nháp tạo, «💾 Đã lưu lúc 23:15»); tab 2 «🗑️ Xóa» → «Xóa hẳn» nháp đó; tab 1 gõ thêm chất liệu thật: đầu trang hiện khung vàng «**Nháp của bài này không còn trong kho nháp** …» kèm câu «Nếu bài đã được gửi lên website ở tab khác thì tab này không biết…», nút «💾 Lưu lại thành nháp» (nút chính) và «🗑️ Bỏ bài này»; kho nháp 0 nháp (không tạo lại). Bấm «💾 Lưu lại thành nháp»: toast «Đã lưu lại nháp», khung báo hết, «💾 Đã lưu lúc 23:17», chữ vừa gõ còn. Tab 2 xóa lần nữa, tab 1 chuyển bước: khung báo hiện lại; «🗑️ Bỏ bài này» → «Bỏ hẳn bài đang soạn ở tab này? Không lấy lại được.» → «Bỏ hẳn»: trang trống, toast «Đã bỏ bài đang soạn ở tab này», kho 0 nháp. Không lỗi console; log máy chủ chỉ có dòng `ConnectionResetError` (WinError 10054) của asyncio trên Windows khi một tab ngắt kết nối, không liên quan app.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: tự lưu không lặng lẽ tạo lại nháp đã bị xóa; báo rõ, hỏi lưu lại hay bỏ; lưu lại thì giữ trạng thái gửi tab biết (`app/views/write.py:836-955`, `seo_app/storage/drafts.py:876-911`, `:1011-1025`; 21 test mới, thử trên trình duyệt thật).
- [x] Yêu cầu 2: không lùi T-086, T-089 (40 file test liên quan qua; luồng gửi không sửa; `test_two_tabs_editing_same_draft_still_autosave`).
- [x] Yêu cầu 3: nháp cũ vẫn mở được (`test_old_draft_still_opens_and_saves`; test khuôn 1, 2 của T-055, T-100 vẫn qua); test cho các ca mới.
- [x] Yêu cầu 4: đã có từ T-118 (`.streamlit/config.toml:19`), không sửa; `tests/test_t118_don_thap.py`, `tests/test_app_pages.py` qua.
- [x] Yêu cầu 5: chú thích «Chép sang SiteSEO» đúng hành vi (đường dẫn đã gửi kèm bài từ T-102) và khớp README của T-112; `.env.example` ghi rõ tài khoản Biên tập viên riêng, mật khẩu ứng dụng tạo trên chính tài khoản đó (2 test mới; `tests/test_config.py` qua).
- [x] Yêu cầu 6: câu báo từ khóa dùng `odd_char_messages`; `tests/test_t041_seo_ui.py:711` đổi theo (R5, Chỉ Huy đã duyệt), thêm ca emoji mới.
- [x] Mọi test luồng gửi nháp và kho nháp + `uv run ruff check .` (toàn bộ test do Chỉ Huy chạy khi gộp).
- [x] Thử gỡ chỗ sửa: 16/16 đột biến bị bắt.
- [x] Báo cáo `docs/team/reports/T-092-hoa-si.md`.
- [ ] Chỉ Huy duyệt đổi `tests/test_soi_loi_t089.py` (R5, bảng «Đổi test cũ»).
- [ ] Soi Lỗi, Lá Chắn rút gọn (chưa tới lượt).

## Rủi ro và điểm cần chú ý

1. **Khoảng hở còn lại (đúng phạm vi «tab đó đang biết»):** bài được gửi ở tab khác rồi xóa luôn ở đó trong lúc tab này không chạy lần nào: tab này không biết bài đã gửi; lưu lại thì nháp không có khóa. Khung báo nói rõ ca này (`MSG_GONE_UNKNOWN`). Chặn hẳn thì phải giữ trạng thái gửi khi xóa nháp đã gửi (đổi `delete`, đổi test T-086 `test_send_state_removed_with_its_draft`): xem «Đề xuất».
2. **Khóa «gửi dở» thừa trong ca rất hiếm (hướng an toàn):** tab vừa thấy «đang gửi» của tab khác ở bước Xuất bản, lần gửi đó hỏng mà chưa tạo gì (trả về «chưa gửi»), rồi nháp bị xóa: lưu lại ra «gửi dở», phải tick «Tôi đã kiểm tra…» mới gửi được.
3. **File nháp bận lâu (quá 5 giây):** lần kiểm mỗi lần chạy hỏng nên dòng dưới tiêu đề là «⚠️ Chưa lưu được nháp: File nháp đang bận…» kể cả khi không có gì để lưu (trước đây vẫn «💾 Đã lưu lúc …»). Đúng sự thật (chưa kiểm được), không làm sập trang.
4. **Gộp với T-112:** T-112 sửa `app/views/write.py` ở bước Xuất bản và README; tôi không sửa vùng đó, chỉ đọc các khóa `_wp_seen`, `_wp_sent`, `_wp_maybe_draft`, `_wp_result` (T-112 không đổi tên khóa nào). `git merge-tree` nhánh này (`7860e99`) với `origin/team/T-112` (`7186974`) và với `main` mới (`a499a13`): không xung đột (`main` mới không đổi file nào của phiếu này). Cây gộp với T-112 (xuất bằng `git archive`, chạy bằng venv của worktree): `tests/test_t092_nhap_bi_xoa.py`, test T-089 đã đổi, `tests/test_t041_seo_ui.py`, `tests/test_t112_release_rules.py`, `tests/test_t086_send_state.py`: **111 qua, 0 hỏng**. Lần gộp thử trước đó (trước khi sửa chú thích) hỏng đúng test chú thích, nhờ vậy thấy README của T-112 đã đổi câu về đường dẫn (mục yêu cầu 5).

## Đề xuất

1. (Cần quyết, không gấp) Giữ trạng thái gửi khi xóa nháp **đã gửi** (dòng mồ côi như SL-T089-2), để nháp tạo lại ở bất kỳ tab nào cũng khóa, kể cả tab không biết. Đổi hành vi `delete` và test T-086 nên cần Chỉ Huy hoặc Lá Chắn quyết; cần thêm cách dọn dòng mồ côi cũ.
2. (Nhỏ) Popover «🗑️ Xóa» của nháp đã gửi nhắc «Bài đã gửi lên website (mã …): xóa nháp không xóa bài trên website».

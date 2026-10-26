# Báo cáo T-086 · Trạng thái gửi nháp không chỉ nằm trong phiên

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-086](../tickets/T-086-trang-thai-gui-nhap.md) |
| Ngày nộp | 2026-10-26 |
| Nhánh | `team/T-086` (từ `main` `504ab15`) |
| Kết quả | Hoàn thành: yêu cầu 1–6; SL-T056-8 → -11, LC-T056-1, Ghi nhận 1–3 của Lá Chắn T-056; gỡ `xfail` 7 ca (5 Soi Lỗi, 2 Lá Chắn). Thêm một lỗi tìm ra khi thử trình duyệt thật (Streamlit chạy lần mới song song với lần đang gửi), đã sửa |

## Tóm tắt (cho chủ dự án)

- Trước đây app chỉ nhớ «bài này đã gửi / đang gửi» trong lúc trang còn mở. Tải lại trang (F5), đóng tab, hay mở bài khác rồi mở lại là app quên: bấm «Gửi nháp» lần nữa ra **bài nháp thứ hai**, ảnh (có GPS) tải lên lần hai.
- Nay app ghi «đang gửi» vào nháp trên máy **ngay trước** khi gửi, và ghi «đã gửi, bài nháp mã …» ngay khi website trả lời. Mở lại nháp lúc nào cũng thấy «Bài này đã gửi lên WordPress (bài nháp mã 501, lúc …)» kèm nút mở bài nháp; nút «Gửi nháp» khóa tới khi bạn tick «Tạo thêm một bài nháp mới». Lần gửi trước chưa có kết quả (đang gửi ở cửa sổ khác, bị tải lại trang giữa chừng): app nhắc kiểm Bài viết → Nháp và Media, khóa tới khi bạn tick «Tôi đã kiểm tra…».
- Lỡ bấm nút khác hay bấm đúp trong lúc đang gửi: app đợi lần gửi xong rồi hiện đúng kết quả (mã bài, link, ảnh đã lên) thay vì báo «không biết kết quả»; vẫn nhắc kiểm trang quản trị trước khi gửi lại cho chắc.
- File ảnh bị thay bằng ảnh khác cùng tên sau khi bạn duyệt (kể cả đúng lúc đang gửi, kể cả cùng dung lượng, cùng giờ sửa): app so «dấu vân tay» (băm) của ảnh lúc duyệt với ảnh sắp tải; khác thì dừng, chưa gửi gì, hiện ảnh mới để bạn xem và duyệt lại.
- Nháp cũ vẫn mở như trước. Đã thử trên trình duyệt thật với một WordPress giả chạy trên máy: F5 giữa lúc gửi, bấm sang trang khác giữa lúc gửi, bấm đúp: mỗi lần bấm có chủ ý ra đúng một bài nháp.

## Yêu cầu → cách làm → test

`T:` là `tests/test_t086_send_state.py` (giao diện, 17 test), `K:` là `tests/test_storage_send_state.py` (kho nháp, 16 test), `SL:` là `tests/test_soi_loi_t056.py`, `LC:` là `tests/test_la_chan_t056.py`, còn lại ở `tests/test_app_images.py`.

| # | Yêu cầu (nguồn) | Cách làm | Test |
|---|---|---|---|
| 1 | (a) Ghi «đang gửi / đã gửi (mã bài)» vào nháp **trước** khi gửi, đọc lại khi mở nháp; «đang gửi» không có kết quả là «gửi dở» (SL-T056-8, -11) | `seo_app/storage/drafts.py`: `SendState` (`pending`, `post_id`, `updated_at` có múi giờ; khuôn chặt, không trường chữ) ở bảng riêng `send_states`: lần tự lưu nháp không ghi đè, không đổi giờ lưu nháp. `DraftStore.load_send_state`/`save_send_state`; xóa nháp, nháp bị dọn thì bỏ trạng thái theo. `write.py`: `send_and_record` ghi `pending=True` (giữ mã bài cũ) ngay trước `create_draft_with_images`, ghi kết quả ngay sau; chưa ghi được «đang gửi» thì **không gửi**. `draft_panel` đọc trạng thái trong nháp **mỗi lần vẽ** (`saved_send_state`): `pending` hay dòng hỏng → khóa «gửi dở» (`unsure_message`, ô «Tôi đã kiểm tra…»); có `post_id` → khóa «đã gửi» (`sent_message`, link mở bài nháp, ô «Tạo thêm một bài nháp mới») | `T: test_pending_written_before_first_request`, `…_reopened_sent_draft_needs_new_draft_confirmation`, `…_reopened_pending_draft_is_unsure`, `…_broken_send_state_in_draft_locks`, `…_stop_inside_request_keeps_pending_in_draft`, `…_cannot_write_pending_does_not_send`, `…_error_before_any_draft_clears_pending`, `…_result_not_saved_to_draft_is_reported_and_stays_unsure`; `K:` 16 ca; `SL: test_switch_draft_and_back_keeps_send_lock[gui-xong, gui-do]`, `SL: test_new_session_after_send_needs_confirmation` (gỡ `xfail`) |
| 2 | (b) Đối tượng giữ kết quả, sửa tại chỗ (SL-T056-9) | `S._wp_sending = holder` (dict) là chỗ dừng cuối cùng trước khi gửi; `send_and_record` ghi kết quả vào `holder` **tại chỗ**, không đọc/ghi `st.session_state`, không `st.*` (đều là chỗ Streamlit dừng lần chạy); `holder["done"]` (sự kiện luồng) bật khi lệnh gửi xong, kể cả khi lỗi. Lần chạy sau thấy dấu còn: `finish_send` (đầu `init_state`, trước cả mở nháp khác) **đợi** `done` (lần chạy mới có thể chạy song song, xem «Quyết định» số 1), tối đa 60 giây, rồi lấy kết quả trong `holder`; quá giờ thì giữ dấu, báo «vẫn đang chạy» | `SL: test_real_interruption_keeps_result` (gỡ `xfail`), `T: test_real_stop_after_send_records_post_in_draft`, `T: test_new_run_waits_for_send_still_running`, `T: test_send_still_running_after_wait_keeps_mark`, `test_stop_when_leaving_spinner_keeps_result`; trình duyệt thật |
| 3 | (c) Thứ tự ghi khóa đơn điệu: làm việc bảo vệ trước, bỏ dấu sau (LC-T056-1 a, b) | (a) `finish_send`: dựng khóa «gửi dở» và câu báo trước, rồi `apply_send` (khóa, kết quả, bỏ khóa thừa, bỏ dấu `_wp_sending` sau cùng). (b) `draft_panel`: bỏ tick hai ô xác nhận rồi mới bỏ cờ `_wp_reset_guards`. Dừng ở dòng nào thì dấu (cờ) còn, lần sau làm lại | `LC: test_lc_t056_1_second_stop_while_marking_keeps_lock`, `…_while_resetting_guards_unticks` (gỡ `xfail`); `T: test_second_stop_at_first_lock_write_keeps_result`, `T: test_second_stop_while_locking_without_result_keeps_lock` |
| 4 | (d) Băm nội dung ảnh lúc duyệt và ngay trước khi tải; khác thì dừng, bắt duyệt lại (SL-T056-10, Ghi nhận 1) | `web_info` băm SHA-256 đúng byte đã đọc để ra dòng GPS đang hiện; `alt_editor` gắn băm đó với lần duyệt (`altsha-<id>`; bỏ duyệt, chọn ảnh khác, bỏ ảnh thì bỏ). `send_draft` băm byte đọc để tải; khác thì dừng, chưa gửi gì, bỏ duyệt (`replaced_after_approval`): kiểm lại ảnh, tính lại dòng GPS, ảnh xem trước dựng từ chính file (`make_preview`) cho ảnh bị thay tại chỗ (cache ảnh xem trước theo cỡ, giờ sửa còn giữ bản cũ) | `SL: test_file_replaced_while_sending_stops` (gỡ `xfail`), `T: test_file_replaced_in_place_stops_and_shows_new_file` (cùng cỡ, giờ sửa đặt lại như cũ), `T: test_approval_bound_to_shown_version` |
| 5 | Gom Ghi nhận 2, 3 của Lá Chắn T-056 | Ghi nhận 2: `check_in_pool` bắt lỗi lạ → câu cố định `MSG_CHECK_FAILED` (trả câu báo thay kết quả, như ổ chậm); `choose_image` cũng vậy. Ghi nhận 3: câu lỗi AI (`row.error`) và câu báo của lần quét (`listing.notice`) qua `escape_markdown` | `T: test_unexpected_error_in_image_check_fixed_message`, `T: test_ai_error_and_folder_notice_are_escaped`; `test_alt_ai_errors_shown_as_message` (so chữ đã escape) |
| 6 | Nháp cũ (không có trạng thái gửi) vẫn mở được như trước | Bảng riêng: nháp cũ không có dòng nào là «chưa gửi»; file tạo trước T-086 được tạo thêm bảng khi mở, không bị cất sang một bên; khuôn `DraftSnapshot` không đổi | `K: test_old_draft_file_without_send_states_opens`; `tests/test_storage_drafts.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py` không đổi, vẫn qua |

Gỡ `xfail` (chỉ xóa dấu, thân test không đổi): 4 dấu, 5 ca trong `tests/test_soi_loi_t056.py` (SL-T056-8 × 2, -9, -10, -11); 2 ca trong `tests/test_la_chan_t056.py` (LC-T056-1). Cả 7 ca báo `XPASS(strict)` trước khi gỡ. Riêng `tests/test_la_chan_t056.py` phải bỏ thêm dòng `import pytest` vì sau khi gỡ dấu không còn dùng (ruff F401).

## Quyết định thiết kế cần Soi Lỗi, Lá Chắn xem

1. **Streamlit chạy lần mới song song với lần đang gửi** (tìm ra khi thử trình duyệt thật). Với `runner.fastReruns` (mặc định bật, `streamlit/runtime/app_session.py:566-583`), cú bấm trong lúc đang gửi làm Streamlit dừng ScriptRunner cũ (`request_stop`) và **tạo ngay ScriptRunner mới**; luồng cũ vẫn đang chờ website, chỉ dừng ở chỗ dừng kế tiếp sau khi lệnh gửi xong. Mô tả «lần chạy dừng ở chỗ dừng kế tiếp rồi mới tới lần sau» (biên bản Soi Lỗi, Lá Chắn T-056) chỉ đúng trong `AppTest` (không có fastReruns). Hậu quả với bản đầu của T-086: lần mới thấy dấu khi chưa có kết quả, báo «không biết kết quả» (an toàn, vẫn khóa, nhưng SL-T056-9 không đạt trên trình duyệt thật: bài 502 lên, trang báo «ngắt giữa chừng»). Sửa: `holder["done"]`, `finish_send` đợi (`1a71a78`, ô thông báo lúc đợi `1eb96f9`); thử lại trên trình duyệt thật: hiện «Đã tạo bài nháp (mã 503)» và lời báo bị ngắt. Test mô phỏng chạy song song bằng một luồng khác điền kết quả (`T: test_new_run_waits_for_send_still_running`).
2. **Lần gửi bị ngắt mà vẫn giữ được kết quả: hiện kết quả và vẫn khóa «gửi dở»** (phải tick «Tôi đã kiểm tra…» mới gửi tiếp), không chỉ khóa «đã gửi». Lý do: các test đang qua của Soi Lỗi (`test_real_interruption_never_sends_twice`, `test_switch_page_while_sending_keeps_lock`) và Lá Chắn (`test_gps_warning_right_before_button_while_locked`) cùng tình huống ngắt như SL-T056-9 và đòi khóa «gửi dở»; SL-T056-9 đòi hiện kết quả. Làm cả hai giữ đúng mọi test, và là hướng thận trọng khi người dùng đã bấm loạn lúc đang gửi. Mở lại nháp sau đó thì theo trạng thái ghi trong nháp: «đã gửi (mã bài)».
3. `finish_send` ghi câu «gửi dở» trước rồi mới thay bằng kết quả thật (đúng thứ tự «bảo vệ trước» của LC-T056-1 a); dừng giữa hai lần ghi thì lần sau làm lại.
4. **Băm chỉ nhớ trong phiên.** Nháp mở lại (phiên khác) mà không xem lại khung ảnh ở bước Viết & kiểm tra thì chưa có băm lúc duyệt, lần gửi chỉ kiểm cỡ, giờ sửa, định danh như T-056. Lưu băm vào nháp cần thêm trường cho `DraftImage` (ngoài phần «trạng thái gửi» phiếu cho sửa): đề xuất phiếu Thợ Máy. Xem lại khung ảnh là đủ: băm gắn với bản đang hiện.
5. Không ghi được «đang gửi» vào nháp (file nháp đang bận, hỏng) thì không gửi, báo rõ. Ghi kết quả hỏng thì vẫn hiện kết quả, báo «Chưa ghi được kết quả gửi vào nháp», nháp giữ «đang gửi» (mở lại thì khóa «gửi dở»).
6. Ghi nhận 2: `restore_images` (kiểm ảnh lúc mở nháp) **không** bọc lỗi lạ: bỏ ảnh khi lỗi thì lần tự lưu sau xóa ảnh khỏi nháp; Lá Chắn không tìm ra đường đi thật tới lỗi lạ ở đó.
7. Hai tab cùng mở một nháp: trạng thái trong nháp được đọc lại mỗi lần vẽ, tab kia thấy «đang gửi / đã gửi» ở lần chạy kế tiếp; hai tab bấm gửi đúng cùng lúc (trước khi tab kia ghi «đang gửi») vẫn có thể ra hai bài: không chặn được nếu không khóa liên tiến trình, ngoài phạm vi.

## Yêu cầu bảo mật riêng (tự soát)

| Mã | Kết quả |
|---|---|
| W1 | Vẫn chỉ `create_draft_with_images` (bài luôn `draft`); gửi lại luôn phải tick xác nhận khi nháp đã gửi hay chưa rõ kết quả, kể cả sau khi mở lại nháp, tải lại trang |
| W2 | Không thêm lệnh nào sửa, xóa bài hay ảnh có sẵn trên website; link «Mở bài nháp trong WordPress» của nháp mở lại dựng bằng `client.edit_link(post_id)` (địa chỉ từ `WORDPRESS_URL`, `post_id` là số nguyên đã kiểm khuôn) |
| U1 | Không thêm `unsafe_allow_html` (vẫn 9 chỗ như `main`, phần mới không có). Chữ mới hiện ra: câu cố định, câu `DraftError` (cố định), giờ, mã bài (số), đều qua `escape_markdown`; thêm escape cho câu lỗi AI và câu báo của lần quét (Ghi nhận 3) |
| F2 | Đọc ảnh vẫn qua `ImageLibrary` (giới hạn cỡ, điểm ảnh, chặn lối tắt như cũ); băm dùng đúng byte đã đọc để nén; ảnh xem trước dựng lại bằng `make_preview` (được phép theo LC-T058-2) chỉ cho ảnh bị thay tại chỗ |

## Thử gỡ chỗ sửa

Bản sao worktree (`git ls-files`), `PYTHONPATH` trỏ bản sao, môi trường của worktree; mỗi đột biến chạy các test nên bắt nó (script trong ghi chú bàn giao `T-086-hoa-si-scripts/`).

| Đột biến | Kết quả |
|---|---|
| M1 không ghi «đang gửi» trước khi gửi | bắt được (2 test hỏng) |
| M2 không ghi kết quả vào nháp | bắt được |
| M3 lần chạy sau bỏ qua kết quả trong đối tượng giữ kết quả | bắt được |
| M4 `finish_send` bỏ dấu trước khi dựng khóa | lần đầu **không bắt** (khóa ghi trong nháp vẫn giữ nút khóa); thêm `T: test_second_stop_at_first_lock_write_keeps_result` (dừng ở dòng khóa đầu tiên: mất kết quả) → bắt được |
| M5 bỏ cờ bỏ tick trước khi bỏ tick | bắt được |
| M6 không so băm lúc gửi | bắt được (2 test) |
| M7 nút gửi không đọc trạng thái trong nháp | bắt được (3 test) |
| M8 ảnh bị thay tại chỗ: ảnh xem trước vẫn lấy từ cache | bắt được |
| M9 kiểm lại ảnh không bắt lỗi lạ | bắt được |
| M10 lần chạy mới không đợi lần gửi đang chạy song song | bắt được (2 test) |

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | `SendState`, bảng `send_states`, `load_send_state`/`save_send_state`; dọn, xóa nháp bỏ trạng thái theo; `_is_healthy` kiểm cả bảng mới |
| `app/views/write.py` | Gửi nháp: `send_and_record`, `record_outcome`, `apply_send`, `finish_send` (đợi lần gửi song song), `saved_send_state`, `unsure_message`, `sent_message`, `replaced_after_approval`; khóa theo trạng thái trong nháp; băm ảnh (`content_hash`, `web_info`, `altsha-<id>`); `check_in_pool` trả câu báo; escape hai chỗ |
| `tests/test_storage_send_state.py` (mới) | 16 test kho nháp |
| `tests/test_t086_send_state.py` (mới) | 17 test giao diện (AppTest, WordPress giả, ngắt lần chạy thật, phiên mới cùng kho nháp, chạy song song) |
| `tests/test_app_images.py` | `test_alt_ai_errors_shown_as_message`: so chữ đã escape (Ghi nhận 3) |
| `tests/test_soi_loi_t056.py`, `tests/test_la_chan_t056.py` | Gỡ dấu `xfail` 7 ca (và `import pytest` thừa) |
| `docs/team/reports/T-086-hoa-si.md` | Báo cáo này |

## Bằng chứng

```
$ uv run pytest <48 file: 44 file liên quan của T-056 lượt 2 (tests/test_app*.py, test_images_*.py,
  test_soi_loi_t056, test_drafts_images, test_soi_loi_t055, test_wordpress_shortcodes, …)
  + test_la_chan_t056, test_storage_drafts, test_t086_send_state, test_storage_send_state>
4866 passed, 31 skipped, 13 xfailed in 1290.19s (0:21:30)
# Bắt đầu ở 1a71a78; 13 xfailed đều ở file Soi Lỗi cũ (round4, t003_t009, images_folders_soi_loi,
# t054, t061, t070, t071). tests/test_soi_loi_t056.py, tests/test_la_chan_t056.py không còn xfail.

$ uv run pytest tests/test_t086_send_state.py tests/test_storage_send_state.py tests/test_app_images.py \
    tests/test_soi_loi_t056.py tests/test_la_chan_t056.py tests/test_app_pages.py   # code cuối 1eb96f9
147 passed in 843.60s (0:14:03)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/write.py seo_app/storage/drafts.py \
    tests/test_t086_send_state.py tests/test_storage_send_state.py tests/test_app_images.py \
    tests/test_soi_loi_t056.py tests/test_la_chan_t056.py docs/team/reports/T-086-hoa-si.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Trước khi gỡ `xfail`: 7 ca `XPASS(strict)` (`tests/test_soi_loi_t056.py` 5, `tests/test_la_chan_t056.py` 2).

### Mở app thật (cổng 8502, WordPress giả)

Cấu hình tạm `wt-T-086-hoa-si` trong `D:\ProMetal-ToolSEO\.claude\launch.json` (không start `seo-app-main`), ảnh giả Pillow, mật khẩu thử tạo trong phiên, một nháp mẫu (script `T-056-hoa-si-scripts/setup_app_8502.py`). WordPress giả: script của Soi Lỗi T-056 (`fake_wp_https.py`), `https://localhost:8743`, chỉ nghe `127.0.0.1`, chậm 6 giây ở lệnh tải ảnh và lệnh tạo nháp; chứng chỉ tự ký cho `localhost` chỉ dùng cho lần thử, app vẫn kiểm chứng chỉ (`REQUESTS_CA_BUNDLE` trong file môi trường tạm). Không gửi gì tới website thật, không đọc `.env`.

| Ca | Kết quả |
|---|---|
| Bấm «Gửi nháp», giữa lúc tải ảnh xem kho nháp | `{"pending":true,"post_id":null,…}` đã có trước khi website trả lời |
| F5 giữa lúc gửi, đăng nhập lại, mở nháp | Phiên cũ vẫn gửi xong, ghi `post_id: 501`; phiên mới: «Bài này đã gửi lên WordPress (bài nháp mã 501, lúc 09:07 · 26/10/2026)…», nút «Mở bài nháp trong WordPress», ô «Tạo thêm một bài nháp mới», nút gửi khóa |
| Tick «Tạo thêm…», gửi, 3 giây sau bấm «Bài viết», quay lại (bản đầu) | Bài 502 lên, nháp ghi 502, nhưng trang báo «Lần gửi trước bị ngắt giữa chừng…, app không biết kết quả» (Quyết định số 1) |
| Như trên, sau khi sửa | Trang đợi lần gửi xong rồi hiện «Đã tạo bài nháp trên WordPress (mã 503), kèm 1 ảnh», link, danh sách ảnh, lời báo bị ngắt; khóa «gửi dở» (ô «Tôi đã kiểm tra…» chưa tick, nút khóa) |
| Nháp có «đang gửi» (ghi tay vào kho, như phiên khác còn đang gửi), mở nháp | «Lần gửi trước (bắt đầu lúc 09:13 · 26/10/2026) chưa có kết quả: có thể vẫn đang gửi ở cửa sổ khác, hoặc đã bị ngắt…: **bài nháp có thể đã có trên website**…», nút khóa |
| Tick xác nhận, bấm đúp «Gửi nháp» | Đúng 1 bài (505), 1 ảnh; trang hiện kết quả, khóa «đã gửi» |
| Lần 2 (dữ liệu mới, code `1eb96f9`): gửi, sang «Bài viết», quay lại ngay | Lúc đợi trang hiện ngay ô «⏳ Lần gửi nháp vừa bấm vẫn đang chạy, đợi gửi xong rồi mới hiện kết quả…» (bản `1a71a78` dùng vòng quay: trang trống khoảng 10 giây); xong thì «Đã tạo bài nháp trên WordPress (mã 501), kèm 1 ảnh», khóa «gửi dở»; WordPress giả nhận đúng 1 bài, 1 ảnh |

Log WordPress giả lần 1: 5 bài (501–505) cho 5 lần bấm có chủ ý, mỗi bài 1 ảnh; lần 2: 1 bài, 1 ảnh. Mỗi lần xong: dừng app và WordPress giả, trả `launch.json` về đúng bản cũ (so từng byte, SHA-256 `a5607e8c…`), xóa `data/` của worktree.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–6, có test (gồm ngắt lần chạy thật, phiên mới cùng kho nháp): bảng trên.
- [x] Test liên quan qua (7 file của phiếu và 41 file khác chạm trang Soạn bài, ảnh, nháp: 4.866 qua, 0 hỏng; 6 file gửi nháp chạy lại trên code cuối: 147 qua), `uv run ruff check .` sạch (mục Bằng chứng). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.
- [ ] Soi Lỗi, Lá Chắn rút gọn (chưa tới lượt).
- [x] Báo cáo tại `docs/team/reports/T-086-hoa-si.md`.

## Rủi ro và điểm cần chú ý

1. Lần chạy mới đợi lần gửi song song tối đa 60 giây; trong lúc đó trang chỉ có ô «⏳ Lần gửi nháp vừa bấm vẫn đang chạy…» ở đầu trang (`st.spinner` của Streamlit 1.65 là phần tử tạm, không hiện trên trang chưa có phần tử nào, nên dùng ô thông báo thường: `1eb96f9`). Website rất chậm (quá 60 giây) thì trang báo «vẫn đang chạy» và lần chạy sau đợi tiếp.
2. Test `AppTest` không có fastReruns nên không tự tái hiện được chạy song song; test mô phỏng bằng luồng khác điền kết quả. Soi Lỗi nên thử lại trên trình duyệt thật (script WordPress giả của Soi Lỗi T-056 dùng được ngay).
3. Băm chỉ nhớ trong phiên (Quyết định số 4).
4. Khuôn `SendState` mới đọc từ file là dữ liệu chưa tin cậy: khuôn chặt, giới hạn 4 KB, hỏng thì khóa «gửi dở» (không đoán); `post_id` chỉ dùng để hiện số và dựng link qua `client.edit_link` (địa chỉ từ `WORDPRESS_URL`).

## Đề xuất

- **Thợ Máy (phiếu nhỏ):** lưu băm nội dung ảnh đã duyệt trong `DraftImage` (phần còn lại của SL-T056-2 và Ghi nhận 1), để nháp mở lại hôm khác vẫn so được với bản đã duyệt mà không cần xem lại khung ảnh.
- **Soi Lỗi, Lá Chắn:** khi xét «chỗ dừng» của Streamlit, tính cả fastReruns (lần mới chạy ngay, song song); các test ngắt bằng `request_rerun` trong `AppTest` chỉ phủ phần «dừng ở chỗ dừng kế tiếp».

## Câu hỏi cho chủ dự án

Không có.

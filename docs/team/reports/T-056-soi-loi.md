# Báo cáo T-056 · Giao diện chỗ cần ảnh (G3-10) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-056](../tickets/T-056-giao-dien-cho-can-anh.md) |
| Ngày nộp | 2026-10-24 (lượt 1 và kiểm lại lượt 2) |
| Nhánh | `team/T-056` (gốc `main` `cf8d824`). Lượt 1 kiểm `4303374`; lượt 2 kiểm `692fb07` (code `2d5316e`) |
| Kết quả | **Lượt 2: ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn được ngay.** 7 lỗi lượt 1 (SL-T056-1 → -7) **đã sửa thật**: SL-T056-1 thử cả trên trình duyệt thật với WordPress giả trên máy (bấm đúp, bấm muộn, đổi trang giữa lúc gửi: không gửi trùng). Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **4 Thấp** (SL-T056-8 → -11), không lỗi nào chặn gộp. Soát R5 lượt 2: **đạt**. Thử gỡ 9 chỗ sửa lượt 2: test bắt đủ 9. (Lượt 1: ĐẠT CÓ ĐIỀU KIỆN, 1 Trung bình, 6 Thấp; thử gỡ 30 chỗ sửa: test cũ bắt 27, 2 chỗ đã có test lấp, 1 đột biến không hợp lệ) |

## Tóm tắt (cho chủ dự án)

**Lượt 2 (kiểm lại sau khi Họa Sĩ sửa):**

- Cả 7 lỗi tôi báo ở lượt 1 đã được sửa thật. Lỗi quan trọng nhất (bấm đúp hay bấm nút khác trong lúc đang gửi thì tạo hai bài nháp) tôi thử trên trình duyệt thật với một "WordPress giả" chạy ngay trên máy, website chậm 6 giây mỗi bước: bấm đúp, bấm lần hai khi đang tải ảnh, bấm sang trang khác rồi quay lại: **lần nào cũng chỉ có đúng một bài nháp cho một lần gửi**, nút gửi khóa lại kèm lời nhắc.
- Còn 4 lỗi nhỏ (Thấp), không cái nào tạo bài trùng khi bạn ở yên trên bài đang gửi:
  1. Gửi xong một bài, mở bài khác rồi mở lại bài vừa gửi: nút «Gửi nháp» bật lại, không nhắc «đã gửi».
  2. Bấm gì đó **trong lúc** đang gửi: bài vẫn lên website, nhưng app báo «gửi dở, không biết kết quả» thay vì «Đã tạo bài nháp» (an toàn, chỉ là mất thông tin; bạn phải tự mở trang quản trị xem).
  3. File ảnh bị thay bằng ảnh khác cùng tên **đúng lúc** đang gửi (khe vài giây) thì ảnh mới vẫn lên.
  4. Tải lại trang (F5) hay đóng trình duyệt giữa lúc gửi: lần gửi cũ vẫn chạy xong; mở lại bài đó thì app không biết là đã gửi, bấm gửi là ra bài nháp thứ hai (tôi đã thấy thật trên trình duyệt). Phần này cần nháp nhớ "đã gửi", là việc của Thợ Máy.

**Lượt 1:**

- Màn hình chọn ảnh làm đúng gần hết các điều kiện an toàn đã đặt ra: tên file, tên thư mục lạ (chữ đảo chiều, ký tự vô hình, dấu Markdown, tên kiểu Mac) hiện đúng nguyên văn; không hiện đường dẫn trên máy; AI chỉ xem đúng ảnh bạn bấm, và chỉ bản ảnh đã bỏ hết thông tin máy; ảnh AI luôn lên web là «Minh họa»; trước nút «Gửi nháp» có nhắc GPS công khai và liệt kê đoạn dạng `[...]`. Tôi đã thử thêm ảnh HEIC của iPhone, ảnh chép dở, thư mục rỗng, thư mục 3.000 ảnh, AI trả chữ độc, xóa nháp đang mở, «Viết bài mới» từ trang Bài viết: đều chạy đúng. Mở app thật trên trình duyệt (ảnh giả, không khóa AI, không website) cũng thấy đúng như vậy.
- **Một lỗi cần sửa trước khi gộp (mức Trung bình):** trong lúc app đang gửi nháp (tải ảnh có thể mất vài chục giây), nếu bạn lỡ bấm đúp hay bấm nút khác, bài nháp và ảnh đã lên website nhưng app "quên" là đã gửi: nút «Gửi nháp» vẫn bật, không có lời nhắc nào, bấm lại là website có **hai bài nháp và ảnh (có GPS) bị tải lên hai lần**. Cách sửa nhỏ: ghi dấu "đang gửi" trước khi gửi.
- Sáu lỗi nhỏ (Thấp), nên sửa cùng lượt: (1) file ảnh bị thay bằng ảnh khác **cùng tên** sau khi bạn duyệt alt thì app vẫn tải ảnh mới lên (kể cả khi ảnh mới có GPS mà bạn chưa xem); (2) đoạn `[...]` vắt qua hai mục của bài không được liệt kê; (3) nhắc số điện thoại bỏ sót tổng đài 8 số (1900 6868) và số viết `0909–123–456`, `0909/123/456`; (4) ảnh đại diện bạn chọn bị trả về ảnh đầu khi sang trang khác rồi quay lại; (5) một ảnh dùng ở hai chỗ, bấm «Đây là ảnh AI» ở chỗ này thì chỗ kia vẫn ghi «Ảnh thật»; (6) ảnh mở từ nháp: mỗi lần bấm «AI viết alt» app lại xem thư mục trên ổ ngay trong trang (ổ Google Drive chậm thì trang chờ lâu hơn).
- Không lỗi nào làm ảnh AI lên web như ảnh thật, làm lộ đường dẫn, mật khẩu, hay chạy được đoạn `[...]` trên website.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t056.py` | Lượt 1: 22 ca (10 `xfail` SL-T056-1 → -7, Họa Sĩ đã gỡ ở lượt 2). Lượt 2 thêm 12 ca: 7 qua (ngắt thật lúc gửi, đổi trang lúc gửi, ổ chậm khi gửi, 4 dạng số điện thoại), 5 `xfail(strict=True)` SL-T056-8 → -11. Nay 34 ca: 29 qua, 5 `xfail`. Dùng lại ảnh giả, WordPress giả, AI giả của `tests/test_app_images.py` |
| `docs/team/reports/T-056-soi-loi.md` | Báo cáo này (thêm mục «Kiểm lại lượt 2») |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm lại lượt 2 (2026-10-24)

Họa Sĩ sửa SL-T056-1 → -7 (`0841ee5`, `393f492`, `2d5316e`; báo cáo `T-056-hoa-si.md` mục «Lượt 2») và gỡ 10 `xfail` của tôi. Tôi kiểm trên `692fb07`: đọc diff `write.py` (+259/−134 dòng), chạy lại cách tái hiện của chính tôi và thêm biến thể Chỉ Huy nêu, thử trên trình duyệt thật với WordPress giả, thử gỡ chỗ sửa.

### Phát hiện chính về cách Streamlit dừng lần chạy

Bản sửa SL-T056-1 dựa trên ý «ghi kết quả ngay sau khi gọi, trước mọi lệnh `st.*`». Nhưng trong Streamlit 1.65, **mọi lần đọc/ghi `st.session_state` cũng là điểm dừng**: `SafeSessionState.__getitem__/__setitem__/__delitem__/__contains__` gọi `_yield_callback()` (= `_maybe_handle_execution_control_request`) **trước** thao tác (`streamlit/runtime/state/safe_session_state.py:120-138`; `st.session_state.x = …` đi qua `session_state_proxy.py:149-162` tới đó). Cú bấm đến trong lúc lệnh gửi chạy thì lần chạy dừng ngay ở dòng `S._wp_result = {…}` (`write.py`, nhánh `else` của khối gửi), kết quả không được ghi. Bản sửa vẫn **an toàn** nhờ dấu `_wp_sending` đặt trước khi gửi: lần sau `init_state` thấy dấu còn → «gửi dở», khóa nút. Nhưng kết quả thật bị mất (SL-T056-9). Test của Họa Sĩ `test_stop_when_leaving_spinner_keeps_result` ném `StopException` ở lúc thoát vòng quay, chỗ chỉ tới được khi cú bấm đến sau lệnh ghi cuối. Test lượt 2 của tôi gửi yêu cầu chạy lại thật qua bộ điều phối (`ScriptRequests.request_rerun`), đúng đường một cú bấm trên trình duyệt; kết quả khớp với trình duyệt thật.

### SL-T056-1 → -7: kết quả lượt 2

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| SL-T056-1 (Trung bình) | **Đã sửa** (không còn gửi trùng trong phiên) | Test lượt 1 qua; mới `test_real_interruption_never_sends_twice` (ngắt thật lúc gửi: 1 bài, 1 ảnh, khóa, chạy lại không gửi thêm, tick xác nhận mới gửi được), `test_switch_page_while_sending_keeps_lock` (bấm sang «Bài viết» lúc gửi, quay lại: khóa). **Trình duyệt thật**, WordPress giả chậm 6 giây/bước: bấm đúp → đúng 1 bài (501), 1 ảnh, hiện «Đã tạo bài nháp (mã 501)», khóa; bấm lần hai lúc đang tải ảnh → 1 bài (502), khóa, nhắc «gửi dở»; bấm sang «Bài viết» lúc đang gửi rồi quay lại → 1 bài (503), khóa, ô xác nhận đã bỏ tick. Thử gỡ R1, R2, R9: test bắt được. Còn lại: SL-T056-8, -9, -11 |
| SL-T056-2 | **Đã sửa** cho file bị thay trước khi bấm gửi | `test_replaced_file_after_approval_stops_send` qua (dừng, 0 request); Họa Sĩ `test_replaced_file_needs_new_look_and_approval` (duyệt lại rồi gửi đúng file mới). Thử gỡ R3: bắt được. Còn khe **trong lúc** gửi: SL-T056-10 |
| SL-T056-3 | **Đã sửa** | `test_shortcode_across_sections_listed` qua («Nội dung, vắt qua nhiều mục»). Đọc mã: thứ tự ghép (tiêu đề mục, thân, alt, chú thích) đúng thứ tự `article_parts`. Thử gỡ R4: bắt được |
| SL-T056-4 | **Đã sửa** | 4 dạng lượt 1 qua; thêm 4 dạng mới qua (`1900.68.68`, `19006868`, `+84 (0) 909 123 456`, `0909_123_456`). Ngày «12/10/2026», «2024–2025», «1600 x 1200 cm» không bị nhắc (test Họa Sĩ). Ghi chú: «12/10/2026 10:30» có nhắc (10 chữ số liền dấu ngăn), nhắc thừa vô hại. Thử gỡ R5: bắt được |
| SL-T056-5 | **Đã sửa** | `test_featured_image_kept_after_switching_pages` qua. Thử gỡ R6: bắt được |
| SL-T056-6 | **Đã sửa** | `test_mark_ai_shows_in_other_spot_with_same_image`, `test_two_spots_mark_ai_store_failure_both_sent_as_ai` qua. Thử gỡ R7: bắt được |
| SL-T056-7 | **Đã sửa** cho «AI viết alt», «Đây là ảnh AI», «Gửi nháp» | `test_draft_image_not_rescanned_in_page_thread` qua; mới `test_slow_drive_when_sending_stops_without_request` (kiểm lại quá 15 giây: dừng, 0 request). Lần kiểm khi **mở nháp** vẫn trong luồng trang (Họa Sĩ nêu lý do: quá giờ mà bỏ ảnh thì lần tự lưu sẽ xóa ảnh khỏi nháp; chấp nhận được, Lá Chắn xem). Thử gỡ R8: bắt được |
| Ghi nhận 4 lượt 1 | **Đã sửa** | `folder_listing` chỉ bỏ lần chờ của chính thư mục (đọc mã) |

### Thử trên trình duyệt thật với WordPress giả trên máy

- App worktree ở cổng 8513 (cấu hình tạm `wt-T-056-soi-loi-l2`), ảnh giả Pillow trong thư mục tạm, mật khẩu thử tạo trong phiên, không khóa AI.
- WordPress giả: script Python (`http.server` + `ssl`, chỉ nghe `127.0.0.1:8743`), trả lời như `Site` trong `tests/test_app_images.py`, chậm 6 giây ở lệnh tải ảnh và lệnh tạo nháp, ghi mọi request ra file. Chứng chỉ tự ký cho `localhost` chỉ dùng cho lần thử. App vẫn **kiểm tra chứng chỉ** (không tắt SSL, R5): file môi trường tạm đặt `REQUESTS_CA_BUNDLE` trỏ tới chứng chỉ đó, `requests` vẫn `verify=True`.
- Không gửi gì tới website thật. Xong thì dừng app và WordPress giả, trả `launch.json` về đúng bản cũ (so từng byte, SHA-256 `a5607e8c…f169`), xóa `data/` của worktree. Không start `seo-app-main`.

| Ca | Kết quả (log WordPress giả) |
|---|---|
| Bấm đúp «Gửi nháp» | 1 lần tải ảnh, 1 bài (501), đặt ảnh đại diện; trang: «Đã tạo bài nháp trên WordPress (mã 501), kèm 1 ảnh», nút khóa tới khi tick «Tạo thêm một bài nháp mới» |
| Tick «Tạo thêm…», bấm, 5 giây sau (đang tải ảnh) bấm lần nữa | 1 bài (502); trang: «Lần gửi trước bị ngắt giữa chừng…, app không biết kết quả», khóa (SL-T056-9: mất kết quả, không trùng) |
| Tick xác nhận, bấm, 3 giây sau bấm «Bài viết», quay lại | 1 bài (503); trang: «gửi dở», khóa, ô xác nhận đã bỏ tick |
| Tick xác nhận, bấm, 3 giây sau tải lại trang (F5) | Phiên cũ vẫn gửi xong: bài 504. Phiên mới: đăng nhập, mở lại nháp, bước 5: nút **bật**, không nhắc; bấm → bài **505** (SL-T056-11) |

Tổng: 5 bài cho 4 lần bấm có chủ ý, bài thừa duy nhất do tải lại trang.

### Lỗi mới lượt 2

Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t056.py` (đã thử `--runxfail`: 5 ca hỏng đúng câu kiểm cuối).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T056-8 | Thấp | Mở bài khác rồi mở lại bài vừa gửi: mất khóa «đã gửi»/«gửi dở» | `test_switch_draft_and_back_keeps_send_lock[gui-xong]`, `[gui-do]`: gửi bài A (xong, hoặc ngắt thật giữa chừng), «Mở» bài B ở «Bài đang soạn dở», «Mở» lại A, bước 5 | Vẫn phải tick xác nhận mới gửi được | Nút bật, không nhắc gì; bấm là bài nháp thứ hai. `_wp_sent`, `_wp_maybe_draft`, `_wp_sending` nằm trong `COMPOSE_KEYS`, `clear_compose` xóa khi mở bài khác (cả «Viết bài mới») | Giữ trạng thái gửi theo `draft_id` trong phiên (khóa riêng, không xóa khi đổi bài), mở lại bài thì lấy lại `_wp_sent`/`_wp_maybe_draft` của bài đó |
| SL-T056-9 | Thấp | Bấm gì đó trong lúc gửi: bài đã lên nhưng app báo «gửi dở», mất kết quả | `test_real_interruption_keeps_result` (yêu cầu chạy lại thật trong lúc gửi); trình duyệt thật ca 2 | Hiện «Đã tạo bài nháp (mã …)», link sửa, danh sách ảnh đã lên (công khai) | «Lần gửi trước bị ngắt giữa chừng…, app không biết kết quả»; mất link, danh sách ảnh. Dừng ở chính dòng ghi `S._wp_result` (mục «Phát hiện chính») | Trước khi gửi đặt một đối tượng giữ kết quả vào session (`S._wp_sending = holder = {}`), sau khi gửi xong **sửa tại chỗ** `holder["result"] = …` (sửa đối tượng không qua `st.session_state`, không phải điểm dừng); `init_state` thấy `holder` có kết quả thì hiện kết quả thay cho «gửi dở» |
| SL-T056-10 | Thấp | File ảnh bị thay đúng lúc đang gửi vẫn lên | `test_file_replaced_while_sending_stops`: thay file (ảnh khác, có GPS) ngay trước lần đọc để nén (sau bước kiểm lại) | Dừng như SL-T056-2 | Ảnh mới (có GPS) lên website với alt cũ. Khe giữa `recheck` và `read_image_bytes` trong `send_draft`: vài giây khi nhiều ảnh lớn | Sau khi đọc, so `len(data)` với `fresh.entry.size` (và/hoặc hỏi lại `stat_image` sau khi đọc, so cỡ, giờ sửa, `file_id`); khác thì dừng |
| SL-T056-11 | Thấp (Lá Chắn xem lại mức) | Tải lại trang (F5, đóng tab) giữa lúc gửi: mở lại nháp, gửi lại không cần xác nhận | `test_new_session_after_send_needs_confirmation` (phiên AppTest mới, cùng kho nháp); trình duyệt thật ca 4 (bài 504, 505) | Phiên mới mở lại nháp vẫn phải tick xác nhận | Nút bật, không nhắc. Dấu trong `st.session_state` mất theo phiên; nháp không nhớ "đã gửi / đang gửi". Cùng gốc với Ghi nhận 2 lượt 1, nay có đường đi cụ thể: người dùng tưởng app treo, tải lại trang | Thêm trường "đang gửi / đã gửi (mã bài)" vào `DraftSnapshot` (`seo_app/storage/drafts.py`, Thợ Máy), `write.py` ghi trước khi gửi, đọc khi mở nháp (Họa Sĩ). Ngoài phạm vi `write.py`, không chặn gộp T-056 |

### Thử gỡ chỗ sửa lượt 2 (bản sao `git archive` `692fb07` + file test mới)

| Đột biến | Kết quả | Chi tiết |
|---|---|---|
| R1 bỏ dấu «đang gửi» | bắt được (test hỏng) | 1 failed in 9.44s (12 s) |
| R2 init_state không xét dấu «đang gửi» còn sót | bắt được (test hỏng) | 1 failed in 7.76s (10 s) |
| R3 changed() không so file (SL-T056-2) | bắt được (test hỏng) | 1 failed in 7.93s (10 s) |
| R4 bỏ xét nội dung ghép (SL-T056-3) | bắt được (test hỏng) | 1 failed in 5.79s (8 s) |
| R5 PHONE_LIKE như lượt 1 (SL-T056-4) | bắt được (test hỏng) | 1 failed, 2 passed in 12.30s (15 s) |
| R6 bỏ _featured khỏi KEEP_KEYS (SL-T056-5) | bắt được (test hỏng) | 1 failed in 10.23s (13 s) |
| R7 mark_ai chỉ đổi chỗ đang bấm (SL-T056-6) | bắt được (test hỏng) | 1 failed in 7.38s (10 s) |
| R8 kiểm lại trong luồng trang (SL-T056-7) | bắt được (test hỏng) | 1 failed in 5.60s (8 s) |
| R9 bỏ tick ô xác nhận sau khi gửi (như trước) | bắt được (test hỏng) | 1 failed in 8.40s (11 s) |

Cả 9 bị test bắt (test của Soi Lỗi hay của Họa Sĩ). Riêng nhánh `except BaseException` của khối gửi không thử gỡ: dấu `_wp_sending` đã là lớp phòng chính (R1, R2), nhánh đó chỉ ghi câu báo sớm hơn một lần chạy.

### Soát R5 lượt 2

- `tests/test_soi_loi_t056.py`: `git diff 7648550..692fb07` chỉ xóa 10 dấu `@pytest.mark.xfail(...)`; tham số số điện thoại đổi từ `pytest.param(..., marks=xfail)` sang `@pytest.mark.parametrize("alt", PHONE_VARIANTS)`, giữ đủ 4 dạng; thân test không đổi.
- `tests/test_app_images.py`: chỉ thêm 9 test và 1 import (`contextmanager`, `StopException`); không dòng test cũ nào bị xóa hay đổi.
- Không `skip`, không nới điều kiện nào.

### U1, U2, A3 và các điều kiện lượt 1

- Không thêm chỗ `unsafe_allow_html` nào (vẫn 6 chỗ như lượt 1, phần mới của T-056 chỉ HTML cố định); câu báo mới (`MSG_SEND_INTERRUPTED`, `MSG_SLOW_CHECK`, «Nội dung, vắt qua nhiều mục») là chữ cố định, hiện qua `escape_markdown`.
- `check_in_pool` chạy `check_chosen_image` trong luồng quét; mọi giá trị lấy từ `st.session_state` (`tag_store()`, `scanned_entries()`, `ai_root_indexes()`) tính ở luồng trang trước khi gửi việc, luồng quét không đụng `st.session_state`. `scanned` vẫn chỉ từ các lần quét (LC-T055-1).
- Mọi điều kiện của bảng lượt 1 vẫn đạt: test liên quan qua trên code `2d5316e` (mục «Bằng chứng lượt 2»).

### Kết luận lượt 2

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn được ngay.** SL-T056-1 (điều kiện gộp lượt 1) đã sửa thật; không còn lỗi Trung bình trở lên. Điều kiện:

1. SL-T056-8, -9, -10 (Thấp, đều trong `write.py`, sửa nhỏ): Họa Sĩ sửa luôn trước khi gộp hoặc Chỉ Huy lập phiếu theo dõi.
2. SL-T056-11 (Thấp, cần `seo_app/storage/drafts.py`): Chỉ Huy lập phiếu Thợ Máy + Họa Sĩ; nên xong trước khi dùng nút gửi thật thường xuyên. Lá Chắn xem lại mức.

### Bằng chứng lượt 2

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_app_pages.py tests/test_content_edge_cases.py \
    tests/test_wordpress_shortcodes.py tests/test_wordpress_images.py tests/test_images_folders.py \
    tests/test_images_tags.py tests/test_storage_drafts.py tests/test_drafts_images.py \
    tests/test_soi_loi_t055.py tests/test_ai_images.py tests/test_soi_loi_t056.py -rxX
1764 passed, 13 skipped, 5 xfailed in 468.65s (0:07:48)   # code 2d5316e; 5 xfail = SL-T056-8 → -11

$ uv run pytest tests/test_soi_loi_t056.py --runxfail -k "<4 lỗi mới>"   # 5 ca hỏng đúng câu kiểm cuối
5 failed, 29 deselected in 42.91s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t056.py docs/team/reports/T-056-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Test vẫn không gọi mạng thật (WordPress giả, AI giả trong test). WordPress giả của phần thử trình duyệt chỉ nghe `127.0.0.1`; mật khẩu thử của app, mật khẩu ứng dụng WordPress thử chỉ nằm trong file môi trường tạm của phiên.

## Bảng điều kiện → kết quả → bằng chứng (lượt 1)

Điều kiện lấy từ mục «Ghi chú của Chỉ Huy» của phiếu và yêu cầu 1–3. «Đột biến Mx»: gỡ chỗ sửa tương ứng trên bản sao `git archive HEAD`, test có hỏng không (mục «Thử gỡ chỗ sửa»). Số dòng theo `app/views/write.py` ở `4303374`.

| # | Điều kiện (nguồn) | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Tên file/thư mục escape, cô lập hướng chữ (Soi Lỗi T-048, LC-T048-4 b, LC-T052 e) | **ĐẠT** | `shown_name`/`name_md` (:579–593). Test Họa Sĩ `test_names_from_disk_escaped_isolated_never_html`; M1, M2 bắt được. Thêm `test_weird_names_nfd_rlo_markdown` (gốc tên có RLO U+202E, `$x^2$`, `red[đỏ]`, `_y_`; thư mục NFD; file có U+200B): không ký tự đảo hướng/vô hình nào lên trang, `$` `_` `[` đã escape, thẻ đọc đúng từ tên NFD. Trình duyệt thật: gốc RLO hiện «Anh �gpj.exe», thư mục `[bấm](evil.example) _đậm_ <U+200B>ẩn $x$` hiện nguyên chữ, không thành link |
| 2 | Giữ kết quả quét trong phiên; quét trong luồng riêng (Soi Lỗi T-048, Thợ Máy T-048 điểm 7) | **ĐẠT** cho «Chọn ảnh từ thư mục»; **một phần** cho ảnh mở từ nháp (SL-T056-7) | `folder_listing` (:1137) + `_scan_pool`. Test Họa Sĩ `test_scan_in_own_thread_…`, `test_slow_drive_…`; M13 bắt được. Ảnh của nháp: mở nháp, «AI viết alt», «Đây là ảnh AI», «Gửi nháp» gọi `list_folder` từng tầng trong luồng `ScriptRunner.scriptThread` (`test_draft_image_not_rescanned_in_page_thread`) |
| 3 | Luôn hiện alt để duyệt, không tự áp alt AI (Chỉ Huy 2026-10-20, Soi Lỗi T-050) | **ĐẠT** | AI viết xong `altok=False` (:874); sửa chữ bỏ duyệt (`unapprove`); M20 bắt được |
| 4 | Không `ImageLibrary._folders`; không đường dẫn tuyệt đối (LC-T048, yêu cầu 3) | **ĐẠT** | `test_no_absolute_path_on_the_page`; `test_unexpected_send_error_fixed_message_and_lock` (lỗi lạ chứa `C:\Users\bi-mat…` không lộ). Trình duyệt thật: `document.body.innerText` không có `X:\`, `AppData`, `\Users\` |
| 5 | Chỉ quét khi mở thư mục hoặc bấm quét lại (LC-T048) | **ĐẠT** (ghi chú) | `test_spot_is_real_picker_and_nothing_scanned_until_opened`. Mở nháp có ảnh thì kiểm thư mục (Họa Sĩ Rủi ro 3: do người dùng bấm «Mở»); xem SL-T056-7 |
| 6 | Báo gốc đi qua lối tắt (LC-T048 Ghi nhận) | **ĐẠT** | `test_root_through_link_is_reported_without_path` (junction thật); M23 bắt được |
| 7 | `st.image` chỉ nhận byte `PreviewCache.get`/`make_preview` (LC-T058-2, Lá Chắn T-049 đk 3) | **ĐẠT** | Một chỗ duy nhất `preview_bytes` (:731); M3 bắt được |
| 8 | Bắt `ImageFolderError`, `ImageProcessError` → câu tiếng Việt; lỗi khác câu cố định (Lá Chắn T-049) | **ĐẠT** | `test_preview_errors_…`; thêm `test_heic_chosen_and_truncated_jpeg_blocked` (JPEG chép dở: nút «Chọn» khóa), `test_alt_after_file_deleted_shows_message_without_ai_call`, `test_unexpected_send_error_…` |
| 9 | Hiện `WebImage.notice`; «Ảnh không có vị trí GPS» (Lá Chắn T-049, T-067) | **ĐẠT** | `test_gps_text_notice_and_image_settings`; HEIC không GPS hiện đúng câu |
| 10 | Không cho đặt thư mục cache (Lá Chắn T-049) | **ĐẠT** | Đọc mã: `preview_cache()` (:523) luôn `PREVIEW_CACHE_DIR`, không ô nhập nào |
| 11 | `suggest_alt` chỉ khi bấm, ảnh đã chọn, không hàng loạt (Lá Chắn T-050 a, A3) | **ĐẠT** | `test_alt_only_on_click_…` (duyệt thư mục, chọn ảnh: 0 lần gọi AI); M25 (AI viết alt ngay khi chọn) bắt được |
| 12 | Alt, chú thích trong ô nhập; không `unsafe_allow_html` (Lá Chắn T-050 b, U1) | **ĐẠT** | `test_evil_ai_alt_stays_text_and_listed`: AI trả `[bấm](javascript:…)`, `<img onerror>`, `<script>`, số điện thoại, `[code_snippet id=3]` → ô alt đã lọc link, thẻ; không phần tử `allow_html` nào có chữ độc; lên WordPress «[» «]» thành `&#91;` `&#93;`, không thẻ HTML nào của AI |
| 13 | Lỗi AI hiện đúng câu `AIError`, không `st.exception` (Lá Chắn T-050 c, T-062) | **ĐẠT** | `test_alt_ai_errors_shown_as_message`; M26 bắt được |
| 14 | Nhắc khi alt có dãy số giống số điện thoại (Lá Chắn T-050 d, «nên») | **ĐẠT CÓ GHI CHÚ** | `PHONE_LIKE` (:120) chỉ nhận ≥ 9 chữ số; bỏ sót 4 dạng (SL-T056-4) |
| 15 | `ai_generated` theo thẻ, `rules=load_alt_rules()`, `prepare=("alt",)`; ảnh AI ra «Minh họa»; `load_image_settings()` (Lá Chắn T-062) | **ĐẠT** | M5 bắt được; `test_gps_text_notice_and_image_settings` |
| 16 | Chỉ gửi AI byte của `make_ai_image` (Soi Lỗi T-066) | **ĐẠT** | M4 bắt được |
| 17 | Thẻ bằng `resolve`/`resolve_many`, theo trang ≤ 200 ảnh (Lá Chắn T-052 a, T-074 i) | **ĐẠT** | `test_tags_read_per_page_at_most_200`; M24 bắt được |
| 18 | Hiện rõ Ảnh thật/Ảnh AI trước khi viết alt; một bấm đổi sang ảnh AI (Lá Chắn T-052 b) | **ĐẠT**, trừ ca một ảnh ở hai chỗ (SL-T056-6) | `test_mark_ai_saves_manual_tag_…`; trình duyệt thật thấy SL-T056-6 |
| 19 | Gốc tên có dấu hiệu AI → mọi ảnh là ảnh AI; xét cả tên sau `resolve()` (Lá Chắn T-052 c, T-070 g) | **ĐẠT** | M22 bắt được |
| 20 | `recovered_from` chỉ `.name` (Lá Chắn T-052 d) | **ĐẠT** (test cũ yếu, đã lấp) | M21 (hiện cả đường dẫn) test cũ **không bắt** vì so đường dẫn thô với chữ đã escape Markdown; thêm `test_broken_tag_file_note_has_no_folder_path` (bỏ dấu escape rồi mới so), bắt được M21 |
| 21 | `FolderTags.unmatched` chỉ dạng số (Lá Chắn T-052 e) | **ĐẠT** | `test_unmatched_folder_words_only_counted` |
| 22 | Fixture trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (Lá Chắn T-052 f) | **ĐẠT** | `tests/conftest.py::_never_touch_real_image_tags` (tự động, mỗi test một thư mục `the-anh*`); `REAL_DEFAULT_FILE` của `test_images_tags.py` đọc lúc nạp module nên không bị ảnh hưởng; `test_images_tags.py` qua |
| 23 | Hiện lý do ảnh là ảnh AI (Lá Chắn T-070 h) | **ĐẠT** | Thêm `test_ai_by_file_name_and_folder_name_with_reason` (tên file có «midjourney», thư mục `CongAI`) |
| 24 | Thẻ đã kiểm của chính ảnh vào `DraftImage`; ảnh AI lên `minh-hoa-ai-…`, `[AI] …` (Lá Chắn T-054 4a, T-071 3a) | **ĐẠT** | `test_send_ai_image_named_and_titled_as_ai`, `test_marked_ai_image_sent_as_ai`; M9 bắt được |
| 25 | Chỉ gửi khi bấm; nhắc GPS công khai ngay trước nút (Lá Chắn T-046 số 8, T-054 4b, yêu cầu 2) | **ĐẠT** | `test_send_draft_with_real_image`; M10 bắt được; trình duyệt thật: khung vàng GPS nằm ngay trên nút |
| 26 | Hiện đủ `str(exc)`, `uploaded`, `maybe_uploaded`; `maybe_draft` nhắc, khóa, không tự gửi lại (Lá Chắn T-054 4c, T-071 3b) | **ĐẠT** cho lỗi website; **không** khi lần chạy bị ngắt (SL-T056-1) | M14, M15 bắt được; thêm `test_maybe_draft_lock_survives_page_switch` |
| 27 | Liệt kê đoạn dạng shortcode trong tiêu đề, nội dung, alt, chú thích; hàm công khai ở `seo_app/` (LC-T061-4) | **ĐẠT CÓ GHI CHÚ** | `seo_app/wordpress/shortcodes.py` dùng đúng `_SHORTCODE_OPEN`/`_drop_invisible`; `client.py` không sửa (`git diff cf8d824..HEAD -- seo_app/` chỉ có file mới). M11 bắt được. Đoạn vắt qua hai mục không được liệt kê (SL-T056-3) |
| 28 | 2a: đi từ gốc qua `SubFolder.rel_path`; test 2a bắt buộc trên ổ thường, `typed_resolve`, danh sách bị cắt (LC-T055-1, Lá Chắn T-076 lượt 2) | **ĐẠT** (test đủ 8 ca, chạy trên Windows) | M16, M17 bắt được. Ghi nhận 1 bên dưới (nhánh danh sách bị cắt dùng tên trong nháp) |
| 29 | Hiện, duyệt, chèn bằng `checked.*`; `checked.message`; `dropped_images` (LC-T055 b) | **ĐẠT** | M29, M30 bắt được |
| 30 | Xem trước và tải lên cùng `checked.ref`; kiểm lại ngay trước khi tải (LC-T055-2) | **ĐẠT CÓ GHI CHÚ** | M8 bắt được. Kiểm lại không so nội dung file: SL-T056-2 |
| 31 | `ai_roots` vào `check_draft_images` (LC-T055 d) | **ĐẠT** | M12 bắt được |
| 32 | Lưu thẻ hỏng → trong phiên vẫn ảnh AI, không gửi như ảnh thật (Lá Chắn T-074 j) | **ĐẠT** (test cũ yếu, đã lấp) | M7 (bỏ nhánh `_ai_marked` của `slot_tags`) test cũ **không bắt**; thêm `test_two_spots_mark_ai_store_failure_both_sent_as_ai` (cùng ảnh ở hai chỗ, lưu thẻ hỏng: cả hai lên web như ảnh AI), bắt được M7 |
| 33 | Yêu cầu 1: chọn ảnh, xem trước, duyệt alt (nút viết lại), prompt ảnh AI xem/sửa/sao chép, gửi nháp kèm ảnh | **ĐẠT** | Test Họa Sĩ; trình duyệt thật |
| 34 | Yêu cầu 3: `tests/test_app_pages.py` vẫn qua | **ĐẠT** | Mục «Bằng chứng» |
| — | T-063, T-079, T-080, T-081 gộp trước; `TIEN-DO.md` 4b (Code Snippets ≥ 3.9.2); README (Thư Ký, LC-T069-2) | Không thuộc Soi Lỗi | Chỉ Huy, Thư Ký |

## Lỗi tìm thấy (lượt 1, đã sửa ở lượt 2)

Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t056.py` (sửa xong thì gỡ `xfail`; test hỏng ở đúng câu kiểm cuối, đã thử `--runxfail`).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| **SL-T056-1** | **Trung bình** | «Gửi nháp» bị ngắt giữa chừng thì mất kết quả; gửi lại tạo bài nháp thứ hai, tải ảnh lần hai | `test_interrupted_send_locks_resend`. Trên app thật: bấm «Gửi nháp», trong lúc đang tải ảnh bấm đúp hay bấm nút/ô khác. Streamlit dừng lần chạy ở lệnh `st.*` kế tiếp (thoát `st.spinner`: `streamlit/elements/spinner.py:137-142` gửi tin nhắn → `script_runner.py:506-515`, `:569-570` ném `RerunException`); lớp này kế thừa `BaseException` (`scriptrunner_utils/exceptions.py:22`) nên lọt qua `except Exception` (`write.py:1939`) | Lần chạy sau nhắc «bài nháp có thể đã có», khóa nút tới khi người dùng xác nhận đã kiểm (như `maybe_draft`) | Bài nháp và ảnh đã lên site giả; `_wp_result`, `_wp_sent`, `_wp_maybe_draft` chưa ghi; nút bật, không câu nhắc; bấm lại: **2 bài nháp, 2 lần tải ảnh** (thử: `posts 2 uploads 2`) | Trước `create_draft_with_images` (:1927) đặt `S._wp_maybe_draft = True` (hoặc khóa "đang gửi"), chỉ gỡ khi đã ghi kết quả thành công; hoặc `try/finally` ghi khóa khi chưa có kết quả |
| SL-T056-2 | Thấp (Lá Chắn xem lại mức: liên quan GPS công khai) | File ảnh bị thay (cùng tên, nội dung khác) sau khi duyệt alt vẫn được tải lên | `test_replaced_file_after_approval_stops_send`: chọn `IMG_0002.jpg` (không GPS), AI viết alt, duyệt, sang bước 5; thay file bằng ảnh khác **có GPS** cùng tên; bấm «Gửi nháp» | Dừng như khi ảnh đổi tên/thành ảnh AI («ảnh vừa thay đổi»), chưa gửi gì, xem lại ảnh rồi duyệt lại | Ảnh mới lên site giả, còn GPS (16°3′15.84″N, 108°12′7.92″E) với alt duyệt cho ảnh cũ. `changed()` (:707-713) chỉ so `ref`, ảnh AI, alt, chú thích | Trong `changed()` so thêm `fresh.entry` với `checked.entry` (cỡ, giờ sửa, `file_id` khi có). Ảnh mở lại từ nháp hôm khác không so được (nháp không lưu dấu file, thiết kế T-055): ghi vào đề xuất |
| SL-T056-3 | Thấp | Đoạn dạng shortcode vắt qua hai mục không được liệt kê | `test_shortcode_across_sections_listed`: mục 1 kết thúc «Mã nhúng [code_snippet id=3», mục 2 có «…cuối bài].» | Liệt kê như mọi đoạn khác (LC-T061-4: mọi đoạn trong nội dung) | Không cảnh báo; nội dung gửi đi là một chuỗi và `_has_shortcode` của client nhận ra shortcode trên chuỗi đó. `shortcode_findings` (:1826) xét riêng từng mục | Xét thêm cả nội dung ghép (đúng thứ tự `article_parts`, phần chữ); đoạn mới thì ghi «Nội dung (nhiều mục)» |
| SL-T056-4 | Thấp | Nhắc số điện thoại bỏ sót | `test_phone_like_variants_warn` × 4: «Gọi 1900 6868…», «Hotline 1800.6789…», «0909–123–456…» (gạch ngang dài), «0909/123/456» | Có nhắc | Không nhắc: `PHONE_LIKE` (:120) cần ≥ 9 chữ số, chỉ nhận dấu cách, chấm, «-», ngoặc | Nhận ≥ 8 chữ số và thêm «–», «—», «/», «_» vào dấu ngăn (chỉ để nhắc, nhắc thừa không hại) |
| SL-T056-5 | Thấp | Ảnh đại diện đã chọn mất khi sang trang khác rồi quay lại | `test_featured_image_kept_after_switching_pages`; trình duyệt thật: chọn «Ảnh ở mục «Cổng sau khi sửa»», sang Bài viết, quay lại | Giữ ảnh đã chọn (như từ khóa, alt…) | Ô về ảnh đầu; gửi thì ảnh đầu làm ảnh đại diện. Khóa `_featured` không trong `KEEP_KEYS` (:107) | Thêm `_featured` vào `KEEP_KEYS` (đã có bước bỏ khi không còn trong `ready`, :2020) |
| SL-T056-6 | Thấp | Một ảnh ở hai chỗ: bấm «Đây là ảnh AI» ở chỗ 1, chỗ 2 vẫn hiện «📷 Ảnh thật» | `test_mark_ai_shows_in_other_spot_with_same_image`; trình duyệt thật: chỗ 2 vẫn «📷 Ảnh thật», «Thẻ: Mã CT012…», nút «Đây là ảnh AI», «Đã duyệt» ✓, alt không «Minh họa», trong khi dòng dưới ô alt nói «Ảnh AI: alt mở đầu «Minh họa»…» | Chỗ 2 cũng hiện ảnh AI (Lá Chắn T-052 b) | `chosen_panel` (:962) dùng `checked.is_ai` của `pick` cũ; chỉ `slot_tags` (:654) biết. Khi gửi thì dừng, bắt duyệt lại nên không lên web sai | `chosen_panel` dùng `slot_tags(checked).is_ai`, hoặc `mark_ai` cập nhật mọi chỗ cùng `ref` |
| SL-T056-7 | Thấp | Ảnh mở từ nháp: mỗi lần «AI viết alt», «Đây là ảnh AI», «Gửi nháp» lại quét thư mục cha ngay trong luồng trang | `test_draft_image_not_rescanned_in_page_thread`: mở nháp có ảnh thật; bấm «🔄 AI viết lại alt» → 2 lần `list_folder` trong `ScriptRunner.scriptThread` | Không quét lại trong luồng trang (Soi Lỗi T-048: quét trong luồng riêng) | `recheck` (:691) truyền `scanned_entries()` chỉ gồm các lần quét của khung chọn ảnh; ảnh của nháp không có ở đó nên `_FolderNames` xem từng tầng mỗi lần (mỗi tầng tới 10 giây trên ổ chậm, không báo "đang quét ở nền") | Giữ kết quả `list_folder` của lần kiểm khi mở nháp trong phiên (vẫn là kết quả quét thật, hợp LC-T055-1), hoặc chạy lần kiểm qua `_scan_pool` |

## Thử như người dùng thật (lượt 1)

**AppTest (test mới, đều qua):** HEIC chọn, xem trước, AI viết alt được; JPEG chép dở bị khóa kèm câu tiếng Việt; thư mục rỗng có câu báo; thư mục 3.000 ảnh: 250 trang, 12 ảnh/trang, mở 0,6 giây, sang trang 0,6 giây (máy có 2 agent khác chạy); tên độc (RLO, U+200B, NFD, `$…$`, Markdown); AI trả chữ độc (link, `<img onerror>`, `<script>`, số điện thoại, shortcode); ảnh AI theo tên file/tên thư mục kèm lý do; «Viết bài mới» ở trang Bài viết khi bài cũ có ảnh, alt đã duyệt (bài mới trống, nháp cũ nguyên, nháp mới riêng); xóa nháp đang mở rồi sang trang khác và quay lại (không sống lại); lỗi lạ khi gửi (câu cố định, không lộ chữ lỗi gốc, khóa nút); `maybe_draft` còn khóa sau khi sang trang khác; ảnh bị xóa sau khi chọn rồi bấm «AI viết alt» (câu báo, 0 lần gọi AI).

**App thật** (worktree, cổng 8513, qua khung trình duyệt; `IMAGE_FOLDERS` trỏ 3 gốc ảnh giả Pillow trong thư mục tạm: «Anh cong trinh», «Ảnh AI», «Anh <U+202E>gpj.exe»; mật khẩu thử tạo trong phiên; không khóa AI, không WordPress):

1. Mở nháp mẫu, «📁 Chọn ảnh từ thư mục»: ô «Thư mục con (4)» hiện `[bấm](evil.example) _đậm_ �ẩn $x$`, `CT030 - Cổng sắt - Thủ Đức` (tên NFD) đúng nguyên văn; vào thư mục con thì ô là ô mới, trống (lỗi Họa Sĩ đã sửa: đạt).
2. File chữ đổi đuôi `.jpg`: câu báo, nút «Chọn» khóa. Chọn `IMG_0001.jpg`: xem trước, «📷 Ảnh thật», thẻ, «📍 Ảnh có vị trí GPS…».
3. Chọn cùng ảnh cho chỗ 2, gõ alt, duyệt cả hai; bước 5: «Chỗ cần ảnh đã có ảnh, alt đã duyệt: 2/2», báo chưa khai báo WordPress (nút khóa), ô «Ảnh đại diện», khung GPS ngay trên nút.
4. Chọn ảnh đại diện «Cổng sau khi sửa», sang «Bài viết» rồi quay lại: bước 5, alt còn nguyên, **ảnh đại diện về «Bản lề cổng»** (SL-T056-5).
5. Bước 3, bấm «Đây là ảnh AI» ở chỗ 1: chỗ 2 vẫn «📷 Ảnh thật» (SL-T056-6).
6. Ô «Thư mục ảnh»: gốc có RLO hiện «Anh �gpj.exe» (không đảo chữ). `innerText` cả trang: không có đường dẫn ổ đĩa, không U+202E, U+200B.

Không bấm «Gửi nháp» tới website nào (không khai báo WordPress). Xong thì dừng app, trả `D:\ProMetal-ToolSEO\.claude\launch.json` về bản sao lưu (so từng byte: giống; SHA-256 `a5607e8c…f169` như trước khi sửa), xóa `data/` của worktree. Không start `seo-app-main`.

## Thử gỡ chỗ sửa (lượt 1, bản sao `git archive` `4303374`)

Mỗi đột biến thay đúng một đoạn trong `app/views/write.py` của bản sao (thư mục tạm), chạy test chỉ định; test phải hỏng.

| Đột biến | Kết quả |
|---|---|
| M1 `shown_name` không cô lập hướng chữ · M2 `name_md` không escape · M3 `st.image` nhận byte gốc · M4 AI nhận byte gốc · M5 `ai_generated=False` · M6 `mark_ai` không nhớ ảnh AI · M8 gửi không kiểm lại · M9 `DraftImage` thẻ mặc định · M10 bỏ cảnh báo GPS · M11 shortcode không xét alt · M12 mở nháp không `ai_roots` · M13 quét trong luồng trang · M14 lỗi gửi không escape · M15 `maybe_draft` không khóa · M16 bỏ so không phân biệt hoa thường · M17 bỏ nhánh danh sách bị cắt · M18 bỏ `remember_inputs` · M19 bỏ nhắc số điện thoại · M20 sửa alt không bỏ duyệt · M22 bỏ tên sau `resolve()` · M23 không báo lối tắt · M24 `resolve_many` cả lần quét · M25 AI viết alt ngay khi chọn · M26 lỗi AI câu cố định · M27 `post.status` không báo · M29 `dropped_images` không báo · M30 mở nháp dùng thẻ trong nháp | **27/27 bắt được** (test cũ của Họa Sĩ) |
| M7 `slot_tags` bỏ nhánh `_ai_marked` | Test cũ **không bắt** → thêm `test_two_spots_mark_ai_store_failure_both_sent_as_ai`: **bắt được** |
| M21 câu báo file thẻ hỏng hiện đường dẫn đầy đủ | Test cũ **không bắt** → thêm `test_broken_tag_file_note_has_no_folder_path`: **bắt được** |
| M28 (hiện thêm tên thư mục đã escape) | Không hợp lệ: tên thư mục đã escape, cô lập hướng chữ được phép hiện (dòng «Thư mục:»), không phải vi phạm điều kiện e |

## Soát R5 (lượt 1)

- `tests/test_content_edge_cases.py::test_publish_now_requires_confirmation`: bỏ đúng 1 dòng `assert not button(at, send).disabled  # Nháp: được gửi` (nút demo «Gửi sang WordPress» không còn ở «Nháp»), thay bằng kiểm có nút thật «📤 Gửi nháp» và kiểm «Hẹn giờ» không cần ô xác nhận. Phần an toàn chính giữ nguyên: «Đăng ngay» khóa nút cho tới khi tick «Tôi đã đọc lại bài và đồng ý đăng ngay». Nút «Gửi nháp» thật (chỉ khi bấm, bài luôn nháp) có test riêng ở `tests/test_app_images.py`. **Không nới điều kiện nào.**
- `tests/conftest.py`: chỉ thêm fixture tự động `_never_touch_real_image_tags`, đúng điều kiện 2f T-052; không sửa fixture cũ.
- `git diff cf8d824..HEAD --stat`: không xóa, `skip` hay `xfail` thêm test nào.

## U1, U2, A3 (lượt 1)

- **U1:** 6 chỗ `unsafe_allow_html` trong `write.py`; chỗ mới của T-056 chỉ có 2 khung giữ chỗ HTML cố định (`img-ph`, :921, :1339), không chữ từ máy, AI, người dùng (đối chiếu `test_names_from_disk…`, `test_evil_ai_alt…`). Chữ từ WordPress (`message`, `status`, câu lỗi) qua `escape_markdown`; tên file, địa chỉ ảnh đã lên qua `st.text`; `edit_link` do client dựng (`client.py:1227`), `source_url` đã kiểm `is_site_link`.
- **U2:** trang Soạn bài vẫn sau màn hình đăng nhập (`app/main.py` không đổi); app thật chạy `localhost`. Không đường dẫn tuyệt đối (điều kiện 4). Còn trang Cài đặt → Ảnh in đường dẫn `IMAGE_FOLDERS` (có từ trước, Họa Sĩ đã nêu, ngoài phạm vi).
- **A3:** ảnh chưa chọn không rời máy (M25); AI chỉ nhận byte `make_ai_image` (M4); test không gọi mạng thật (WordPress giả `fake_wordpress`, AI giả `fake_ai`, bộ chặn mạng của `conftest.py`).

## Ghi nhận (không phải lỗi, để Lá Chắn quyết)

1. **2a (nay là khuyến nghị):** khi danh sách thư mục cha bị cắt, «📂 Mở thư mục chứa ảnh» gọi `list_folder` với phần còn lại lấy từ `checked.ref` (:1189-1196), kể cả ảnh không còn dùng được, khi đó `ref` là chữ trong nháp. Thử: nháp ghi `…/TRUOC/DA_XOA.jpg` (thư mục thật `truoc`, ảnh đã xóa), cha bị cắt → `list_folder(0, "…/TRUOC")`, trả tên trên ổ `truoc`. Họa Sĩ đã nêu (Rủi ro 2). `list_folder` vẫn chặn `..`, lối tắt, đường dẫn tuyệt đối.
2. Bài đã gửi thành công chỉ được nhớ trong phiên (`_wp_sent`): mở lại nháp hôm khác, «Gửi nháp» tạo thêm bài nháp mà không có ô xác nhận. Cần trường mới trong `DraftSnapshot` (`seo_app`, ngoài phạm vi T-056). **Lượt 2:** có đường đi cụ thể (tải lại trang giữa lúc gửi), thành SL-T056-11.
3. Alt dài hơn 500 ký tự bị cắt khi lưu, gửi (`MAX_ALT_CHARS`); giao diện đã nhắc từ 125 ký tự.
4. Hai luồng quét (`_scan_pool`): ổ mạng treo hẳn có thể giữ cả hai (Họa Sĩ Rủi ro 5); thêm: một lần quét khác xong thì `S.pop("_scan_pending")` (:1163) xóa cả lần quét đang chờ của thư mục khác, quay lại thư mục chậm sẽ gửi thêm một lần quét nữa. **Lượt 2:** phần `_scan_pending` đã sửa; từ lượt 2 lần kiểm lại ảnh (`check_in_pool`) cũng dùng chung 2 luồng này, nên ổ treo hẳn giữ cả 2 luồng thì mọi lần quét, kiểm lại (kể cả gốc USB) đều báo «ổ chậm» tới khi ổ trả lời.

## Kết luận lượt 1

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn được ngay** (Lá Chắn kiểm song song với lượt sửa). Lượt 2: điều kiện 1, 2 đã xong (mục «Kiểm lại lượt 2»).

Điều kiện trước khi gộp `main`:

1. Họa Sĩ sửa **SL-T056-1** (Trung bình), gỡ `xfail` của `test_interrupted_send_locks_resend`; Soi Lỗi kiểm lại rút gọn.
2. Nên sửa cùng lượt SL-T056-2 → -7 (Thấp, đều trong `app/views/write.py`); không sửa thì Chỉ Huy lập phiếu theo dõi. SL-T056-2 nên sửa cùng SL-T056-1 nếu Lá Chắn nâng mức (GPS công khai).
3. Giữ 2 test lấp chỗ hổng (`test_two_spots_mark_ai_store_failure_both_sent_as_ai`, `test_broken_tag_file_note_has_no_folder_path`) khi sửa.

## Bằng chứng lượt 1

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_app_pages.py tests/test_content_edge_cases.py \
    tests/test_wordpress_shortcodes.py tests/test_wordpress_images.py tests/test_images_folders.py \
    tests/test_images_tags.py tests/test_storage_drafts.py tests/test_drafts_images.py \
    tests/test_soi_loi_t055.py tests/test_ai_images.py tests/test_soi_loi_t056.py -rxX
1738 passed, 13 skipped, 10 xfailed in 305.13s (0:05:05)   # 10 xfail = SL-T056-1 → -7

# Trước khi thêm file của Soi Lỗi (11 file của phiếu, code 4303374):
1726 passed, 13 skipped in 355.83s (0:05:55)

$ uv run pytest tests/test_soi_loi_t056.py --runxfail -k "<7 lỗi>"   # 10 ca hỏng đúng câu kiểm cuối
10 failed, 12 deselected in 24.53s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t056.py docs/team/reports/T-056-soi-loi.md
"results": {}
```

Máy Windows 11, có 2 agent Soi Lỗi khác chạy song song. Không đọc `.env`, không có khóa thật; mật khẩu thử của app chỉ nằm trong thư mục tạm của phiên.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Đối chiếu từng điều kiện «Ghi chú của Chỉ Huy» với code và test (bảng trên), thử gỡ chỗ sửa trên bản sao (30 đột biến).
- [x] Thử như người dùng thật: AppTest (22 ca mới) và app thật trên trình duyệt.
- [x] U1/U2/A3, R5 (mục riêng).
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T056-n; không sửa code ứng dụng.
- [x] Test liên quan và `ruff` (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.
- [x] Lượt 2: kiểm lại SL-T056-1 → -7 (test, biến thể, trình duyệt thật với WordPress giả), thử gỡ 9 chỗ sửa, soát R5, lỗi mới SL-T056-8 → -11 có test `xfail(strict=True)`.

## Rủi ro và điểm cần chú ý

- Lượt 1: SL-T056-1 tái hiện bằng AppTest và đọc mã Streamlit. Lượt 2: thử thêm trên trình duyệt thật với WordPress giả trên máy (không phải website thật: không có staging). WordPress giả trả lời như site giả của test, không chạy plugin, không kiểm quyền thật.
- Lần gửi thật đầu tiên nên theo Họa Sĩ Rủi ro 1 (một bài, tải ảnh về kiểm GPS) và chờ Chỉ Huy xác nhận `TIEN-DO.md` mục 4b.

## Đề xuất

- **Họa Sĩ:** SL-T056-8, -9, -10 theo cột «Gợi ý sửa» của mục «Lỗi mới lượt 2» (sửa nhỏ, đều trong `write.py`). (SL-T056-1 → -7 đã sửa ở lượt 2.)
- **Thợ Máy + Họa Sĩ (phiếu mới):** SL-T056-11, nháp nhớ "đang gửi / đã gửi (mã bài)"; nên xong trước khi dùng nút gửi thật thường xuyên.
- **Thợ Máy (sau, cùng Giai đoạn 5):** nháp nhớ dấu file ảnh đã duyệt (cỡ, giờ sửa) để mở lại nháp hôm khác vẫn biết ảnh bị thay (phần còn lại của SL-T056-2); nháp nhớ "đã gửi lên WordPress, mã bài" để không tạo nháp trùng (Ghi nhận 2, nay là SL-T056-11).
- **Họa Sĩ (phiếu nhỏ, đã nêu):** trang Cài đặt → Ảnh không in đường dẫn `IMAGE_FOLDERS`.

## Câu hỏi cho chủ dự án

Không có.

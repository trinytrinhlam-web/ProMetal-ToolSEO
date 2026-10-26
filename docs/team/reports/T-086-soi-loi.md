# Báo cáo T-086 · Trạng thái gửi nháp không chỉ nằm trong phiên · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-086](../tickets/T-086-trang-thai-gui-nhap.md) |
| Ngày nộp | 2026-10-26 |
| Nhánh | `team/T-086` (kiểm `e2e345f`, gốc `main` `504ab15`) |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm thử trình duyệt thật với WordPress giả). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn rút gọn được ngay.** SL-T056-8, -9, -10, -11 và LC-T056-1 **đã sửa thật**. Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T086-1, -2), không chặn gộp. Soát R5: **đạt**. Thử gỡ 5 chỗ sửa: test bắt đủ 5 |

## Tóm tắt (cho chủ dự án)

- Lỗi «gửi trùng bài nháp» đã được sửa thật. Tôi thử trên trình duyệt thật với một "WordPress giả" chạy ngay trên máy (chậm 6 giây mỗi bước, ảnh lớn 28 MB): bấm «Gửi nháp» ba lần liên tiếp, bấm sang trang khác giữa lúc gửi rồi quay lại, tải lại trang (F5) giữa lúc gửi rồi mở lại bài: **mỗi lần chỉ có đúng một bài nháp**. Mở lại bài lúc nào cũng thấy «Bài này đã gửi lên WordPress (bài nháp mã …)», phải tick «Tạo thêm một bài nháp mới» mới gửi thêm được.
- Bấm nút khác trong lúc đang gửi: app đợi gửi xong rồi hiện đúng kết quả (mã bài, link, ảnh đã lên). File nháp bị sửa tay chỗ ghi trạng thái gửi: app khóa nút và nhắc kiểm trang quản trị, không đoán. Nháp cũ (tạo trước bản sửa) vẫn mở bình thường. Băm ảnh không làm chậm: ảnh 28 MB mất 0,02 giây (nén ảnh mất 2,5 giây).
- Còn 2 lỗi nhỏ:
  1. Mở **cùng một bài ở hai tab** và bấm «Gửi nháp» ở cả hai cách nhau vài giây (lúc tab kia còn đang nén ảnh) thì vẫn ra **hai bài nháp**, không tab nào nhắc (tôi đã thấy thật: bài 501 và 502).
  2. File ảnh bị thay tại chỗ bằng ảnh khác **cùng dung lượng, cùng giờ sửa** (phải cố ý làm): khung xem trước vẫn hiện ảnh cũ, nhưng app duyệt và gửi ảnh mới.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t086.py` | Mới: 32 ca (30 qua, 2 `xfail(strict=True)` SL-T086-1, -2). Dùng lại ảnh giả, WordPress giả, AI giả của `tests/test_app_images.py` và hàm giúp của `tests/test_t086_send_state.py` |
| `docs/team/reports/T-086-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng lỗi cũ và yêu cầu

| Lỗi / yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| SL-T056-8 (mở bài khác rồi mở lại: mất khóa) | **Đã sửa** | `SL: test_switch_draft_and_back_keeps_send_lock[gui-xong, gui-do]` qua; trạng thái đọc từ nháp mỗi lần vẽ (`draft_panel`, `saved_send_state`); thử gỡ T2: test hỏng |
| SL-T056-9 (bấm gì đó lúc gửi: mất kết quả) | **Đã sửa** | `SL: test_real_interruption_keeps_result` qua; `test_interrupt_at_each_write_after_send` (ngắt ở 5 vị trí ghi sau khi website trả lời: luôn hiện kết quả, 1 bài, khóa, nháp ghi «đã gửi 501»). Trình duyệt thật: bấm sang «Bài viết» lúc đang tạo bài, quay lại: «Đã tạo bài nháp trên WordPress (mã 504)», lời báo bị ngắt, khóa «gửi dở» |
| SL-T056-10 (file bị thay lúc gửi vẫn lên) | **Đã sửa** cho file bị thay sau khi xem, duyệt | `SL: test_file_replaced_while_sending_stops` qua (thay giữa lần kiểm lại và lần đọc), Họa Sĩ `test_file_replaced_in_place_stops_and_shows_new_file` (cùng cỡ, giờ sửa); thử gỡ T4: test hỏng. Còn ca file bị thay **trước** khi chọn mà ảnh xem trước lấy từ cache: SL-T086-2 |
| SL-T056-11 (F5 giữa lúc gửi: gửi lại không xác nhận) | **Đã sửa** | `SL: test_new_session_after_send_needs_confirmation` qua; trình duyệt thật: F5 lúc đang tải ảnh, đăng nhập lại, mở nháp: «Bài này đã gửi lên WordPress (bài nháp mã 505, lúc 10:19 · 26/10/2026)», nút «Mở bài nháp trong WordPress», nút gửi khóa; thử gỡ T1: test hỏng |
| LC-T056-1 (thứ tự khóa: bỏ dấu trước) | **Đã sửa** | `LC: test_lc_t056_1_*` qua; `test_double_interrupt_each_write` (ngắt lần một trong lúc gửi, lần hai ở **từng** lần ghi 1–7 của các lần chạy sau): luôn 1 bài, khóa «gửi dở», hiện kết quả, không còn dấu sót; thử gỡ T5 (bỏ dấu trước khi dựng khóa): test hỏng |
| Yêu cầu 1 (ghi trước khi gửi, đọc khi mở) | **Đạt** | Như SL-T056-8, -11; Họa Sĩ `test_pending_written_before_first_request` |
| Yêu cầu 2 (đối tượng giữ kết quả) | **Đạt** | Như SL-T056-9. `send_and_record` không đọc/ghi `st.session_state`, không `st.*` (đọc mã); `holder["done"]` đặt trong `finally` |
| Yêu cầu 3 (thứ tự đơn điệu) | **Đạt** | Như LC-T056-1; ngắt ở 25 vị trí ghi liên tiếp sau khi website trả lời (thử tạm, không giữ trong test): 25/25 đều 1 bài, khóa, có kết quả |
| Yêu cầu 4 (băm lúc duyệt, lúc tải) | **Đạt có ghi chú** | Như SL-T056-10; ghi chú SL-T086-2 |
| Yêu cầu 5 (Ghi nhận 2, 3 của Lá Chắn) | **Đạt** | Họa Sĩ `test_unexpected_error_in_image_check_fixed_message`, `test_ai_error_and_folder_notice_are_escaped` qua |
| Yêu cầu 6 (nháp cũ vẫn mở) | **Đạt** | Tạo file nháp bằng **chính mã của `main` `504ab15`** (`git show 504ab15:seo_app/storage/drafts.py`), mở bằng mã mới: đọc được nháp, tự thêm bảng `send_states`, không bị cất sang một bên (`recovered_from` là `None`), trạng thái «chưa gửi», ghi «đang gửi» được |
| Nháp bị sửa tay trường trạng thái | **Đạt** | `test_tampered_send_state_locks` × 14 (kiểu sai, `post_id` 0/âm/thập phân/chuỗi/quá 2⁶³, giờ không múi, trường lạ, thiếu trường, `[]`, `null`, 5.000 byte, kiểu cột số nguyên, byte lạ): trang không lỗi, khóa «gửi dở» kèm câu báo, không request nào. `test_extreme_but_valid_send_state_shows_sent` × 3 (năm 9999, năm 1, mã 2⁶³−1): khóa «đã gửi» |
| Không chặn oan, không chậm | **Đạt** | «Tạo thêm một bài nháp mới», «Tôi đã kiểm tra…» (trình duyệt thật, 4 lần gửi có chủ ý đều lên đúng 1 bài), Họa Sĩ `test_error_before_any_draft_clears_pending` (lỗi 4xx: không khóa); băm SHA-256 ảnh 28 MB (6000×4000): 18 ms so với `make_web_image` 2.452 ms (0,7%) |

## Thử trên trình duyệt thật với WordPress giả trên máy

- App worktree ở cổng 8513 (cấu hình tạm `wt-T-086-soi-loi`), ảnh giả Pillow trong thư mục tạm (thêm một ảnh 6000×4000, 28 MB, để nén mất khoảng 2,5 giây), mật khẩu thử tạo trong phiên, không khóa AI.
- WordPress giả: script của Soi Lỗi T-056 (`fake_wp_https.py`), chỉ nghe `127.0.0.1:8743`, chậm 6 giây ở lệnh tải ảnh và lệnh tạo bài, ghi mọi request ra file. Chứng chỉ tự ký mới cho `localhost` (bản cũ đã hết hạn), chỉ dùng cho lần thử; app vẫn kiểm tra chứng chỉ (`REQUESTS_CA_BUNDLE` trong file môi trường tạm, không tắt SSL).
- Không gửi gì tới website thật. Xong thì dừng app và WordPress giả, trả `D:\ProMetal-ToolSEO\.claude\launch.json` về đúng bản cũ (so từng byte, SHA-256 `a5607e8c…f169`), xóa `data/` của worktree, cổng 8513, 8743 đã đóng. Không start `seo-app-main`.

| Ca | Kết quả (log WordPress giả) |
|---|---|
| Hai tab (hai phiên) cùng mở nháp ở bước Xuất bản, bấm «Gửi nháp» ở tab 1 rồi 1 giây sau ở tab 2 | **2 bài (501, 502), 2 lần tải ảnh**. Tab 1 hiện «Đã tạo bài nháp (mã 501)», tab 2 «(mã 502)»; không tab nào nhắc có hai bài; nháp giữ mã của tab ghi sau cùng (SL-T086-1) |
| Tick «Tạo thêm…», bấm **ba lần liên tiếp** | 1 bài (503), 1 ảnh; trang hiện kết quả, khóa «đã gửi» |
| Tick «Tạo thêm…», bấm, 5 giây sau (app còn đang nén ảnh) bấm «Bài viết», quay lại | Chưa gửi gì (lần chạy dừng trước khi gửi), ô «Tạo thêm…» đã bỏ tick: đúng |
| Như trên nhưng 10 giây sau (đang tạo bài) bấm «Bài viết», quay lại ngay | 1 bài (504); trang hiện «Đã tạo bài nháp (mã 504)», lời báo bị ngắt, khóa «gửi dở» |
| Tick «Tôi đã kiểm tra…», bấm, 10 giây sau tải lại trang (F5), đăng nhập, mở nháp | Phiên cũ gửi xong bài 505; phiên mới: «Bài này đã gửi lên WordPress (bài nháp mã 505, lúc 10:19 · 26/10/2026)», nút gửi khóa |

Tổng: 5 bài; 4 lần gửi có chủ ý ra đúng 1 bài mỗi lần; bài thừa duy nhất là ca hai tab.

## Lỗi tìm thấy

Mỗi lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t086.py` (`--runxfail`: hỏng đúng câu kiểm cuối).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T086-1 | Thấp | Hai tab cùng một nháp: bấm gửi cách nhau vài giây vẫn ra hai bài | Trình duyệt thật (bảng trên, ca 1). Test `test_other_tab_starts_sending_while_this_tab_prepares`: «tab 1» ghi «đang gửi» vào nháp đúng lúc tab 2 đọc ảnh để nén | Tab 2 dừng, chưa gửi gì, nhắc nháp vừa được gửi ở cửa sổ khác | Tab 2 không đọc lại trạng thái: `draft_panel` đọc lúc vẽ, rồi `send_and_record` ghi đè «đang gửi» (`save_send_state` là `INSERT OR REPLACE`, không so trạng thái cũ) và gửi. Khe hở là toàn bộ thời gian kiểm lại, nén ảnh của tab kia (vài giây với ảnh lớn), không chỉ «đúng cùng lúc» như Quyết định 7 của Họa Sĩ | Ghi «đang gửi» kiểu **so rồi đặt** trong một giao dịch SQLite (`BEGIN IMMEDIATE`; trạng thái trong nháp vẫn như lúc người dùng bấm, tức `previous_post` và không «đang gửi», thì mới ghi; khác thì dừng). Một máy, nhiều tab đều đi qua cùng file SQLite nên chặn được, không cần khóa liên tiến trình khác |
| SL-T086-2 | Thấp (phải cố ý thay file) | Ảnh xem trước lấy từ cache theo (ảnh, cỡ, giờ sửa), còn băm và dòng GPS đọc từ file hiện tại: duyệt gắn với nội dung người dùng chưa thấy | `test_preview_shown_matches_approved_content`: lưới đã tạo ảnh xem trước của `IMG_0002.jpg`; file bị thay tại chỗ (cùng cỡ, đặt lại giờ sửa, có GPS); chọn ảnh, viết alt, duyệt, gửi | Ảnh xem trước dựng từ đúng byte đã băm (hay lần gửi dừng) | Khung hiện ảnh cũ 320×240 (cache), dòng «📍 Ảnh có vị trí GPS» của file mới; ảnh mới 64×48 có GPS lên website. `PreviewCache` (`process.py:897`, khóa theo cỡ, giờ sửa) và `web_info` (đọc file, băm) có thể khác bản khi file bị thay tại chỗ; `_replaced` chỉ có hiệu lực sau khi lần gửi đã phát hiện | Trong `web_info` dựng ảnh xem trước từ chính `data` đã băm (`make_preview(data)`, giữ byte JPEG nhỏ trong phiên theo băm) và `slot_preview` hiện bản đó; hoặc so băm của byte cache với băm của file trước khi hiện |

## Thử gỡ chỗ sửa (bản sao `git archive` `e2e345f` + file test mới)

| Đột biến | Kết quả |
|---|---|
| T1 không ghi «đang gửi» vào nháp trước khi gửi | bắt được |
| T2 nút gửi không đọc trạng thái trong nháp | bắt được |
| T3 lần chạy mới không đợi lần gửi song song | bắt được |
| T4 không so băm lúc gửi | bắt được |
| T5 `apply_send` bỏ dấu «đang gửi» trước khi dựng khóa | bắt được (Họa Sĩ M4 cần test bổ sung mới bắt; `test_double_interrupt_each_write` cũng bắt) |

## Soát R5

- `tests/test_soi_loi_t056.py`: `git diff 504ab15..e2e345f` chỉ xóa 4 dấu `@pytest.mark.xfail(...)` (5 ca); thân test không đổi.
- `tests/test_la_chan_t056.py`: xóa 2 dấu `xfail` và dòng `import pytest` không còn dùng.
- `tests/test_app_images.py::test_alt_ai_errors_shown_as_message`: đổi so chữ thô sang chữ đã `escape_markdown` vì app nay escape câu lỗi AI (Ghi nhận 3 của Lá Chắn T-056); vẫn kiểm đủ câu, vẫn kiểm không có `st.exception`, alt rỗng. Không nới.
- Không `skip`, không xóa test.

## U1, W1, W2, F2 (soát nhanh)

- U1: phần mới không thêm `unsafe_allow_html`; chữ mới là câu cố định, số, giờ, qua `escape_markdown`; giá trị lạ trong nháp không hiện ra (khuôn `SendState` không có trường chữ; sửa tay thì khóa, câu báo cố định).
- W1, W2: vẫn chỉ `create_draft_with_images` (bài luôn `draft`); link «Mở bài nháp trong WordPress» của nháp mở lại dựng bằng `client.edit_link(post_id)` (`post_id` số nguyên đã kiểm khuôn, mã 2⁶³−1 vẫn hiện đúng).
- F2: đọc ảnh vẫn qua `ImageLibrary`; băm dùng đúng byte đọc để nén.
- Test không gọi mạng thật (WordPress giả, AI giả); WordPress giả của phần trình duyệt chỉ nghe `127.0.0.1`.

## Ghi nhận (không phải lỗi)

1. Băm chỉ nhớ trong phiên (Quyết định 4 của Họa Sĩ): đồng ý đề xuất phiếu Thợ Máy lưu băm trong `DraftImage`.
2. Lúc duyệt mà `web_info` đọc ảnh lỗi (ví dụ Drive đang đồng bộ), lần duyệt không gắn băm, lần gửi chỉ so cỡ, giờ sửa, định danh. Hiếm.
3. Ảnh đã bị thay (`_replaced`): mỗi lần vẽ dựng lại ảnh xem trước từ file (`make_preview` ảnh 24 MP khoảng 0,35 giây, cộng thời gian đọc trên ổ chậm); dấu giữ suốt phiên. Chỉ ảnh hưởng tốc độ.
4. Lần chạy mới đợi tối đa 60 giây khi lần gửi song song chưa xong; website chậm hơn thì mỗi lần bấm lại đợi tiếp (Họa Sĩ Rủi ro 1). Chấp nhận được.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn rút gọn được ngay.** Mục tiêu của phiếu (không gửi trùng trong mọi tình huống một tab: tải lại trang, đóng tab, mở bài khác, bấm liên tục) đạt, kể cả trên trình duyệt thật với cơ chế chạy song song (`fastReruns`) của Streamlit. Điều kiện:

1. SL-T086-1, -2 (Thấp, đều trong `write.py`/phần trạng thái gửi của `drafts.py`, sửa nhỏ): Họa Sĩ sửa luôn hoặc Chỉ Huy lập phiếu theo dõi. Không chặn gộp.
2. Giữ các test mới khi sửa (ngắt ở từng lần ghi, ngắt hai lần, trạng thái sửa tay).

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_soi_loi_t056.py tests/test_la_chan_t056.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_soi_loi_t055.py \
    tests/test_app_pages.py tests/test_t086_send_state.py tests/test_storage_send_state.py \
    tests/test_soi_loi_t086.py -rxX
541 passed, 1 skipped, 2 xfailed in 653.84s (0:10:53)   # code e2e345f; 2 xfail = SL-T086-1, -2

# Trước khi thêm file của Soi Lỗi (7 file của tiêu chí xong + 2 file mới của Họa Sĩ):
511 passed, 1 skipped in 810.79s (0:13:30)

$ uv run pytest tests/test_soi_loi_t086.py --runxfail -k "starts_sending or preview_shown"
2 failed   # hỏng đúng câu kiểm cuối: 5 request tới website; ảnh xem trước (320, 240), ảnh lên (64, 48)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t086.py docs/team/reports/T-086-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Không đọc `.env`; mật khẩu thử của app, mật khẩu ứng dụng WordPress thử chỉ nằm trong file môi trường tạm của phiên.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] 4 lỗi của Soi Lỗi và LC-T056-1 đã sửa thật: cách tái hiện cũ (test cũ qua) và biến thể mới (F5, mở bài khác, bấm ba lần, ngắt hai lần liên tiếp, hai tab, file bị thay cùng cỡ, giờ sửa, nháp cũ, nháp sửa tay).
- [x] Không chặn oan, không chậm rõ.
- [x] R5.
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T086-n; không sửa code ứng dụng.
- [x] Test liên quan và `ruff` (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.

## Rủi ro và điểm cần chú ý

- `AppTest` không có `fastReruns`: các test ngắt chỉ phủ "lần chạy dừng ở chỗ dừng kế tiếp"; phần "lần chạy mới chạy song song" dựa vào test luồng của Họa Sĩ và lần thử trình duyệt thật ở trên.
- Lần gửi thật đầu tiên (T-059) vẫn nên một bài, một ảnh, một tab.

## Đề xuất

- **Họa Sĩ:** SL-T086-1, -2 theo cột «Gợi ý sửa».
- **Thợ Máy:** băm ảnh đã duyệt trong `DraftImage` (Ghi nhận 1, Quyết định 4 của Họa Sĩ).

## Câu hỏi cho chủ dự án

Không có.

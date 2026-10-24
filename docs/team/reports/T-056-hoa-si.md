# Báo cáo T-056 · Giao diện chỗ cần ảnh (G3-10)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-056](../tickets/T-056-giao-dien-cho-can-anh.md) |
| Ngày nộp | 2026-10-23 · lượt 2: 2026-10-24 |
| Nhánh | `team/T-056` (từ `main` `cf8d824`) |
| Kết quả | Hoàn thành. Lượt 2 đã sửa SL-T056-1 → -7 của Soi Lỗi (mục «Lượt 2»). Chờ Lá Chắn; nút «Gửi nháp» chờ Chỉ Huy xác nhận Code Snippets ≥ 3.9.2 trước khi gộp |

## Tóm tắt (cho chủ dự án)

- Trang Soạn bài không còn phần «Bản demo» ở chỗ cần ảnh. Mỗi chỗ cần ảnh giờ chọn được ảnh thật từ thư mục đã khai báo (USB, Google Drive): mở thư mục, xem ảnh nhỏ, bấm «Chọn». App hiện rõ ảnh đó là **Ảnh thật** hay **Ảnh AI** (kèm lý do), thẻ công trình đọc từ tên thư mục, và ảnh có vị trí GPS hay không.
- Alt (mô tả ảnh) và chú thích nằm trong ô để bạn sửa; bấm «AI viết alt» thì AI mới xem đúng ảnh đó (bản đã bỏ hết thông tin máy, GPS). Gợi ý của AI phải được bạn tick «Đã duyệt» mới gửi đi; alt có dãy số giống số điện thoại thì app nhắc.
- Ảnh AI: khung prompt xem, sửa, sao chép được. Tạo ảnh ngay trong app vẫn **hoãn** như chủ dự án đã chốt: bạn tạo ảnh ở Gemini, lưu vào thư mục có chữ «AI», rồi chọn ở đây. Ảnh trong thư mục AI tự lên web với tên «minh-hoa-ai-…», alt «Minh họa…».
- Bước Xuất bản, hình thức «Nháp»: nút **«Gửi nháp»** gửi thật bài nháp kèm ảnh lên website. Ngay trước nút, app nhắc ảnh (có GPS) xem được công khai ngay khi tải lên, và liệt kê các đoạn dạng `[...]` nên xóa. Lỗi giữa chừng thì app liệt kê ảnh đã lên thư viện và không tự gửi lại. «Hẹn giờ», «Đăng ngay» vẫn là bản demo (Giai đoạn 5).
- Sửa thêm một lỗi có sẵn: sang trang khác ở menu rồi quay lại thì mất từ khóa, chất liệu thật, alt, và nháp bị ghi đè bằng ô trống. Nay quay lại vẫn còn nguyên.
- **Lượt 2 (2026-10-24):** sửa 7 lỗi Soi Lỗi tìm ra. Quan trọng nhất: đang gửi nháp mà lỡ bấm đúp hay bấm nút khác thì trước đây app quên là đã gửi, bấm lại thành **hai bài nháp, ảnh (có GPS) tải hai lần**; nay app luôn nhớ (đã gửi thì hiện kết quả và khóa nút; gửi dở thì nhắc kiểm trang quản trị, khóa nút tới khi bạn xác nhận). Thêm: file ảnh bị thay bằng ảnh khác cùng tên sau khi duyệt thì dừng, bắt xem lại và duyệt lại; nhắc số tổng đài 1900/1800; giữ ảnh đại diện khi đổi trang; cùng ảnh ở hai chỗ thì đánh dấu ảnh AI một lần là cả hai chỗ; ổ Google Drive chậm không giữ trang khi kiểm lại ảnh.

## Lượt 2 (2026-10-24): sửa lỗi Soi Lỗi

Theo `docs/team/reports/T-056-soi-loi.md`. Mọi sửa trong `app/views/write.py`; gỡ `xfail` của 10 ca trong `tests/test_soi_loi_t056.py` (chỉ xóa dấu, thân test giữ nguyên: 10 ca XPASS, chạy `--runxfail` cả 22 ca qua trước khi gỡ).

| Mã | Lỗi | Cách sửa | Test |
|---|---|---|---|
| **SL-T056-1** (Trung bình) | Đang gửi mà bấm đúp/bấm nút khác: Streamlit dừng lần chạy ở lệnh `st.*` kế tiếp (thoát vòng quay) bằng `BaseException`, kết quả chưa kịp ghi; bấm lại thành 2 bài nháp, ảnh tải 2 lần | (1) Đặt dấu `_wp_sending` ngay trước khi gọi `create_draft_with_images`; ghi kết quả **ngay sau khi gọi**, vẫn trong khối vòng quay, trước mọi lệnh `st.*`. (2) `except BaseException`: ghi «gửi dở» (`mark_send_interrupted`: câu báo, khóa như `maybe_draft`) rồi để Streamlit dừng. (3) `init_state`: thấy dấu còn mà chưa có kết quả thì coi là gửi dở. (4) Bấm đúp: Streamlit vẫn báo nút đã bấm dù lần vẽ mới là khóa, nên xét lại điều kiện ngay lúc bấm (`if clicked and allowed`). Đã gửi: hiện kết quả, khóa tới khi tick «Tạo thêm một bài nháp mới»; gửi dở: nhắc kiểm Bài viết → Nháp, Media, khóa tới khi tick «Tôi đã kiểm tra…»; không tự gửi lại | Soi Lỗi `test_interrupted_send_locks_resend`; mới: `test_double_click_does_not_send_twice`, `test_stop_when_leaving_spinner_keeps_result` (dừng đúng chỗ thật: lúc thoát vòng quay), `test_stop_during_image_upload_locks_resend` (dừng giữa lúc tải ảnh), `test_leftover_sending_mark_locks_send` |
| SL-T056-2 | File ảnh bị thay (cùng tên) sau khi duyệt alt vẫn được tải lên | `file_changed` so cỡ, giờ sửa, định danh trên ổ (`file_id`) của lần chọn với lần kiểm ngay trước khi tải (trong `changed`): dừng, chưa gửi gì, khung ảnh chuyển sang file mới (xem trước, GPS của file mới), bỏ «Đã duyệt». `mark_ai` cũng bỏ duyệt khi file đổi | Soi Lỗi `test_replaced_file_after_approval_stops_send`; mới `test_replaced_file_needs_new_look_and_approval` (duyệt lại rồi gửi đúng file mới, còn GPS) |
| SL-T056-3 | Đoạn dạng shortcode vắt qua hai mục không được liệt kê | `shortcode_findings` xét thêm chữ của cả nội dung ghép đúng thứ tự gửi (tiêu đề mục, thân, alt, chú thích của ảnh); đoạn chưa thấy khi xét từng phần ghi «Nội dung, vắt qua nhiều mục» | Soi Lỗi `test_shortcode_across_sections_listed`; mới `test_shortcode_from_body_into_image_caption_listed` |
| SL-T056-4 | Nhắc số điện thoại bỏ sót 1900/1800 8 số, «–», «/» | `PHONE_LIKE`: tổng đài `1800`/`1900` kèm từ 4 chữ số, hoặc từ 9 chữ số; dấu ngăn thêm «–», «—», «/», «_». Không nhắc ngày tháng (8 chữ số), năm, kích thước | Soi Lỗi `test_phone_like_variants_warn` × 4; mới `test_dates_and_sizes_are_not_phone_numbers` |
| SL-T056-5 | Ảnh đại diện đã chọn mất khi đổi trang | `_featured` vào `KEEP_KEYS` (đã có bước bỏ khi ảnh đó không còn sẵn sàng) | Soi Lỗi `test_featured_image_kept_after_switching_pages`; trình duyệt thật |
| SL-T056-6 | Cùng ảnh ở hai chỗ: đánh dấu ảnh AI ở chỗ này, chỗ kia vẫn «Ảnh thật» | `mark_ai` đổi **mọi** chỗ dùng cùng ảnh (kiểm lại từng chỗ, alt thêm «Minh họa», duyệt lại); khung ảnh hiện Ảnh thật/AI và thẻ theo `slot_tags` | Soi Lỗi `test_mark_ai_shows_in_other_spot_with_same_image`, `test_two_spots_mark_ai_store_failure_both_sent_as_ai`; trình duyệt thật |
| SL-T056-7 | Ảnh mở từ nháp: mỗi lần «AI viết alt», «Đây là ảnh AI», «Gửi nháp» lại xem thư mục từng tầng trong luồng trang | `check_in_pool`: lần kiểm lại (`check_chosen_image`) chạy trong luồng quét, chờ tối đa 15 giây; quá giờ thì báo «Ổ đĩa đang chậm…», không gọi AI, không gửi (lần kiểm vẫn chạy tiếp ở nền). `scanned` vẫn chỉ là ảnh của các lần quét (LC-T055-1). Lần kiểm lúc mở nháp vẫn chạy trong luồng trang (cố ý: quá giờ mà bỏ ảnh thì lần tự lưu sau sẽ xóa ảnh khỏi nháp) | Soi Lỗi `test_draft_image_not_rescanned_in_page_thread`; mới `test_recheck_on_slow_drive_does_not_hold_page` |
| Ghi nhận 4 | Lần quét xong bỏ cả lần chờ của thư mục khác | `folder_listing` chỉ bỏ `_scan_pending` của chính thư mục vừa quét | Đọc mã |

Thử đột biến (bản sao `git archive`, dùng lại môi trường của worktree): trên `write.py` của lượt 1, 7/8 test mới hỏng (ca còn lại kiểm «không nhắc nhầm ngày tháng», đúng là phải qua cả trên bản cũ); bỏ riêng phần «xét lại điều kiện lúc bấm» thì `test_double_click_does_not_send_twice` hỏng (`(2, 2) == (1, 1)`: gửi 2 lần).

Không sửa trong lượt này (ngoài phạm vi `write.py`, ghi lại để Chỉ Huy lập phiếu):
- Phần còn lại của SL-T056-2: nháp mở lại hôm khác không biết file ảnh đã bị thay (nháp không lưu dấu file, cần trường mới trong `seo_app/storage/drafts.py`, Thợ Máy).
- Ghi nhận 2 của Soi Lỗi: «đã gửi» chỉ nhớ trong phiên; mở lại nháp hôm khác vẫn gửi được bài nháp mới không cần xác nhận (cần trường mới trong `DraftSnapshot`, Thợ Máy).
- Ghi nhận 1 (2a, nhánh danh sách bị cắt): giữ như lượt 1, để Lá Chắn quyết (Rủi ro 2).

Mở lại app thật (cổng 8502, cấu hình tạm như lượt 1, đã trả `launch.json` về đúng bản cũ, mã băm `a5607e8c…`; xóa `data/` của worktree): chọn cùng ảnh cho hai chỗ, bấm «Đây là ảnh AI» ở chỗ 1 thì cả hai chỗ hiện «🤖 Ảnh AI» kèm lý do, không còn nút đánh dấu (SL-T056-6); alt «…gọi 1900 6868» có nhắc (SL-T056-4); bước 5 chọn ảnh đại diện «Cổng sau khi sửa», sang «Bài viết» rồi quay lại vẫn giữ (SL-T056-5). SL-T056-1, -2, -7 cần website hay ổ chậm nên chỉ thử bằng test.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/write.py` | Chỗ cần ảnh thật (chọn thư mục/ảnh, xem trước, thẻ, Ảnh thật/AI, alt, prompt), nháp nhớ ảnh, bước Xuất bản «Nháp» gửi thật kèm ảnh; giữ ô nhập khi sang trang khác |
| `app/assets/style.css` | Khung chỗ cần ảnh (`st-key-imgbox-…`), khung chọn ảnh, ảnh nhỏ trong lưới |
| `seo_app/wordpress/shortcodes.py` (mới) | `find_shortcodes`: tìm đoạn dạng shortcode, dùng đúng `_SHORTCODE_OPEN`/`_drop_invisible` của `client.py` (không sửa `client.py`) |
| `tests/test_wordpress_shortcodes.py` (mới) | 26 test cho `find_shortcodes` (đối chiếu `_has_shortcode`, ký tự vô hình, chữ dài) |
| `tests/test_app_images.py` (mới) | 57 test giao diện (AppTest, AI giả, WordPress giả, ảnh Pillow trong thư mục tạm); lượt 2 thêm 8 |
| `tests/test_soi_loi_t056.py` (của Soi Lỗi) | Lượt 2: chỉ gỡ dấu `xfail` của 10 ca đã sửa xong |
| `tests/conftest.py` | Fixture tự động trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (điều kiện 2f) |
| `tests/test_content_edge_cases.py` | `test_publish_now_requires_confirmation`: «Nháp» nay là nút thật «📤 Gửi nháp»; vẫn kiểm «Đăng ngay» phải tick xác nhận |
| `docs/team/reports/T-056-hoa-si.md` | Báo cáo này |

`seo_app/demo.py`: không còn dữ liệu mẫu nào của phần ảnh (đã bỏ từ Giai đoạn 2), nên không sửa.

## Cách giao diện chạy (tóm tắt kỹ thuật)

- **Chọn ảnh:** «📁 Chọn ảnh từ thư mục» mở khung chọn ngay trong chỗ cần ảnh: chọn thư mục gốc (tên cuối, từ `ImageLibrary.roots()`), thư mục con (ô chọn, tên đã cô lập hướng chữ), lưới 12 ảnh/trang. Mỗi lần mở thư mục là một lần `list_folder` chạy trong luồng riêng (`ThreadPoolExecutor`, chờ tối đa 15 giây rồi báo «đang quét ở nền»), kết quả giữ trong phiên (`_scans`). «🔄 Quét lại» mới quét lại.
- **Khóa ảnh:** `ImageEntry` của lần quét → `DraftImage.from_library(entry, tags)` → `check_chosen_image(…, scanned=<ảnh của trang>, ai_roots=…)` → `CheckedImage` giữ trong `pick-<id>`. Nháp lưu `DraftImage.from_library(checked.ref, thẻ đã kiểm, alt, …)`.
- **Mở nháp:** `check_draft_images(snap, library, tag_store, ai_roots)` một lần; hiện và dùng `checked.image/tags/ref`; ảnh không dùng được hiện `checked.message`; `dropped_images > 0` thì báo.
- **Gửi nháp:** chỉ khi bấm; với mỗi ảnh: `check_chosen_image` lại (cùng `ref`), đổi tên/thư mục/thành ảnh AI thì dừng; `make_web_image(read_image_bytes(ref), **[images])`; `DraftImage(web, alt, caption, tags=<thẻ đã kiểm>, featured)`; nội dung: `<h2>` tiêu đề mục + đoạn `<p>` (`paragraphs_to_html`) + ảnh; `create_draft_with_images`.

## Bảng điều kiện → cách làm → test

Mọi test dưới đây ở `tests/test_app_images.py` trừ khi ghi khác. Số dòng theo `app/views/write.py` của commit cuối.

| # | Điều kiện (nguồn) | Cách làm | Test |
|---|---|---|---|
| 1 | Tên file/thư mục: escape, cô lập hướng chữ (Soi Lỗi T-048, LC-T048-4 b, LC-T052 e) | `shown_name` (ký tự Cc/Cf/Cs/Co/Cn/Zl/Zp → «�», bọc U+2068…U+2069), `name_md` = `escape_markdown(shown_name)`; ô chọn dùng chữ thường | `test_names_from_disk_escaped_isolated_never_html` (thư mục `[bấm](evil.example) _đậm_ <U+200B>ẩn אב`, file `anh<U+200B>_[x](y).jpg`: không link, không ký tự rộng 0, có cô lập, không vào HTML) |
| 2 | Giữ kết quả quét trong phiên; quét trong luồng riêng (Soi Lỗi T-048, Thợ Máy T-048 điểm 7) | `folder_listing` (:1137) + `_scan_pool` (:529): kết quả theo (gốc, thư mục, trang) trong `_scans`; quá 15 giây trả «đang quét ở nền» | `test_scan_in_own_thread_kept_in_session_rescan_on_request` (luồng `quet-anh…`, chuyển trang rồi quay lại không quét lại), `test_slow_drive_does_not_hold_the_page` |
| 3 | Chỉ quét khi mở thư mục hoặc bấm quét lại (LC-T048) | Không quét lúc vẽ trang; chỉ khi bấm «Chọn ảnh từ thư mục», chọn thư mục con, «Quét lại» | `test_spot_is_real_picker_and_nothing_scanned_until_opened`, test số 2 |
| 4 | Không dùng `ImageLibrary._folders`; không đường dẫn tuyệt đối (LC-T048, yêu cầu 3) | Chỉ `roots()` (tên cuối) + đường dẫn tương đối | `test_no_absolute_path_on_the_page` (quét mọi chữ trên trang; kiểm mã nguồn không có `._folders`) |
| 5 | Báo gốc đi qua lối tắt (LC-T048, mục Ghi nhận) | `_through_link`/`root_notes` (:546–572): tầng nào của đường dẫn khai báo là symlink/junction thì cảnh báo, không hiện đường dẫn | `test_root_through_link_is_reported_without_path` (junction thật trên Windows) |
| 6 | `st.image` chỉ nhận byte từ `PreviewCache.get`/`make_preview` (LC-T058-2, Lá Chắn T-049 đk 3) | `preview_bytes` (:731) là chỗ duy nhất lấy byte cho `st.image` | `test_st_image_only_gets_preview_cache_bytes` (theo dõi mọi lần gọi `st.image`: chỉ `bytes` của `PreviewCache.get`, JPEG ≤ 320 px, không phải byte gốc) |
| 7 | Bắt `ImageFolderError`, `ImageProcessError` → câu tiếng Việt; lỗi khác → câu cố định, không dấu vết lỗi (Lá Chắn T-049) | `preview_bytes`, `web_info`, `ai_write_alt`, `send_draft` | `test_preview_errors_are_vietnamese_without_trace` (file chữ đổi đuôi `.jpg`; lỗi lạ chứa `C:\Users\bi-mat…` không lộ) |
| 8 | Hiện `WebImage.notice`; «Ảnh không có vị trí GPS» khi `gps is None` (Lá Chắn T-049, T-067) | `web_info` (:742) nén thử một lần, giữ kết quả trong phiên | `test_gps_text_notice_and_image_settings`, `test_choose_image_write_alt_approve_and_save` («📍 Ảnh có vị trí GPS») |
| 9 | Không cho đặt thư mục cache (Lá Chắn T-049) | `preview_cache()` luôn dùng `PREVIEW_CACHE_DIR` của app; không có ô nhập nào | Không có ô nhập (đọc mã); test trỏ thư mục tạm bằng `monkeypatch` |
| 10 | `suggest_alt` chỉ khi bấm, chỉ ảnh đã chọn; không hàng loạt (Lá Chắn T-050 a) | Nút «✨ AI viết alt» trong khung ảnh đã chọn; lưới ảnh không gọi AI | `test_alt_only_on_click_for_chosen_image_with_ai_copy` (duyệt thư mục, chọn ảnh: 0 lần gọi AI; bấm: đúng 1) |
| 11 | Alt, chú thích trong ô nhập; không `unsafe_allow_html` (Lá Chắn T-050 b) | `st.text_input`; sửa chữ → bỏ «Đã duyệt» | `test_alt_needs_approval_and_phone_numbers_warn`, test số 1 (phần tử Markdown có `allow_html` không chứa chữ từ máy) |
| 12 | Lỗi AI hiện đúng câu `AIError`, không `st.exception` (Lá Chắn T-050 c, T-062) | `ai_write_alt` (:843) trả `str(exc)`, hiện bằng `st.error` | `test_alt_ai_errors_shown_as_message` (thiếu khóa; hãng AI báo lỗi) |
| 13 | Nhắc khi alt có dãy số giống số điện thoại (Lá Chắn T-050 d) | `PHONE_LIKE` (9 chữ số trở lên, có thể ngăn bằng dấu cách, chấm, gạch, ngoặc) | `test_alt_needs_approval_and_phone_numbers_warn` |
| 14 | `suggest_alt(…, ai_generated=<theo thẻ>, rules=load_alt_rules())`, router `prepare=("alt",)`; ảnh AI ra «Minh họa»; `make_web_image` nhận `load_image_settings()` (Lá Chắn T-062) | `ai_write_alt`, `web_info`, `send_draft` | `test_alt_only_on_click_for_chosen_image_with_ai_copy`, `test_ai_root_folder_makes_every_image_ai`, `test_gps_text_notice_and_image_settings` |
| 15 | Chỉ gửi AI byte của `make_ai_image` (Soi Lỗi T-066) | `ImageInput(make_ai_image(read_image_bytes(ref)).data, "image/jpeg")` | `test_alt_only_on_click_for_chosen_image_with_ai_copy` (byte AI nhận = byte `make_ai_image`) |
| 16 | Thẻ bằng `resolve`/`resolve_many`, không `get`/`get_many` (Lá Chắn T-052 a) | `choose_image` dùng `resolve`, lưới dùng `resolve_many` | `test_tags_read_per_page_at_most_200` (kiểm mã nguồn) |
| 17 | Hiện rõ Ảnh thật/Ảnh AI trước khi viết alt; một bấm đổi sang ảnh AI (`set(source="ai")`); `ai_generated` và tên file theo thẻ sau bước này (Lá Chắn T-052 b) | Huy hiệu + nút «🤖 Đây là ảnh AI» (`mark_ai` :795) | `test_mark_ai_saves_manual_tag_and_rewrites_alt`, `test_marked_ai_image_sent_as_ai[luu-the-duoc]` (lên web: thẻ `source="ai"`, `minh-hoa-ai-…`, `[AI] …`), `test_send_ai_image_named_and_titled_as_ai` |
| 18 | Thư mục gốc tên có dấu hiệu AI → mọi ảnh là ảnh AI (Lá Chắn T-052 c) | `ai_root_indexes` → `ai_roots` của mọi lần kiểm | `test_ai_root_folder_makes_every_image_ai`, `test_open_draft_in_ai_root_is_ai` |
| 19 | `recovered_from` chỉ hiện `.name` (Lá Chắn T-052 d) | `note_tag_store` (:624) | `test_broken_tag_file_reported_by_name_only` |
| 20 | `FolderTags.unmatched` chỉ dạng số (Lá Chắn T-052 e) | «N phần tên thư mục không khớp…»; dòng thẻ chỉ có giá trị của danh sách cố định | `test_unmatched_folder_words_only_counted` |
| 21 | Fixture trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm (Lá Chắn T-052 f) | `tests/conftest.py::_never_touch_real_image_tags` (tự động) | Mọi test; cache ảnh xem trước trỏ tạm trong `tests/test_app_images.py` (một test T-049 kiểm giá trị mặc định thật của nó) |
| 22 | `is_ai_name` với `RootInfo.label` **và** tên gốc sau `resolve()` (Lá Chắn T-070 g) | `root_notes` (:555) | `test_ai_root_folder_makes_every_image_ai` (tên), `test_root_link_to_ai_folder_counts_as_ai` (gốc «Anh chung» là junction tới «Ảnh AI tạo») |
| 23 | Hiện lý do ảnh bị coi là ảnh AI (Lá Chắn T-070 h) | `ai_reason` (:774) | `test_ai_root_folder_makes_every_image_ai`, `test_mark_ai_saves_manual_tag_and_rewrites_alt` |
| 24 | `DraftImage` chỉ nhận thẻ `ImageTags` đã kiểm của chính ảnh; ảnh AI lên với `minh-hoa-ai-…`, tiêu đề `[AI] …` (Lá Chắn T-054 4a, T-071 3a) | `send_draft` (:1855) | `test_send_draft_with_real_image` (`type(tags) is ImageTags`, bằng thẻ của `pick`), `test_send_ai_image_named_and_titled_as_ai` |
| 25 | Chỉ gọi `create_draft_with_images` khi bấm «Gửi nháp»; nhắc GPS công khai **ngay trước** nút (Lá Chắn T-046 số 8, T-054 4b, yêu cầu 2) | `draft_panel` (:1999) | `test_send_draft_with_real_image` (trước khi bấm: 0 request; phần tử ngay trước nút là cảnh báo GPS) |
| 26 | Hiện đủ `str(exc)`, `exc.uploaded`, `exc.maybe_uploaded` bằng chữ thường/`escape_markdown`; `maybe_draft` nhắc kiểm Bài viết → Nháp, không tự gửi lại (Lá Chắn T-054 4c, T-071 3b) | `send_result` (:1955); `maybe_draft` khóa nút tới khi tick «Tôi đã kiểm tra…» | `test_send_errors_shown_in_full_and_maybe_draft_locks_resend[create]`, `[upload]` |
| 27 | `post.status` khác `draft` thì báo (Soi Lỗi T-054 G9) | `send_result` | `test_post_not_draft_is_flagged` |
| 28 | Một ảnh ở hai chỗ dùng lại cùng đối tượng (Soi Lỗi T-054 G10) | Khóa (ref, alt, chú thích) | `test_same_image_in_two_spots_uploaded_once` (1 lần tải, 2 `<figure>`) |
| 29 | Liệt kê đoạn dạng shortcode trong tiêu đề, nội dung, alt, chú thích; nhắc «WordPress sẽ chạy… nên xóa»; hàm công khai trong `seo_app/` (LC-T061-4) | `seo_app/wordpress/shortcodes.py::find_shortcodes`; `shortcode_findings` (:1826) xét đúng chữ sẽ gửi | `tests/test_wordpress_shortcodes.py` (26), `test_shortcode_like_segments_listed_before_send`, `test_no_shortcode_warning_for_plain_article` |
| 30 | **2a** (LC-T055-1, giữ bắt buộc test theo Lá Chắn T-076): nháp ghi `…/congai/cong.png`, trên ổ `CongAI` → ảnh AI, alt «Minh họa»; cả ổ giả `typed_resolve` và danh sách thư mục cha bị cắt | Đi từ gốc xuống qua `SubFolder.rel_path` (`walk_to_folder` :1172); xem mục Rủi ro số 2 | `test_2a_lowercase_folder_in_draft_stays_ai` × 8 (ổ thường/`typed_resolve` × xem hết/bị cắt × «Mở thư mục chứa ảnh»/theo đúng chữ trong nháp) |
| 31 | Hiện, duyệt, chèn bằng `checked.*`; ảnh không dùng được hiện `checked.message`; `dropped_images > 0` thì báo (LC-T055 b) | `restore_images` (:388) | `test_open_draft_uses_checked_image_not_draft_fields`, `test_open_draft_unusable_image_shows_checked_message` × 2, `test_broken_image_in_draft_dropped_and_reported` |
| 32 | Xem trước và tải lên cùng `checked.ref`; gọi lại `check_chosen_image` ngay trước khi tải (LC-T055-2) | `recheck`/`changed` (:691–713) trong `send_draft` | `test_image_checked_again_right_before_upload` (thẻ đổi sang AI ở «tab khác» → dừng, 0 request), `test_deleted_image_stops_send` |
| 33 | Truyền `ai_roots` vào `check_draft_images` (LC-T055 d) | `restore_images` | `test_open_draft_in_ai_root_is_ai` |
| 34 | `resolve_many` theo trang ≤ 200 ảnh (SL-T074-1, Lá Chắn T-074 i) | Một lần cho 12 ảnh của trang | `test_tags_read_per_page_at_most_200` (15 ảnh: 12 rồi 3) |
| 35 | Lưu thẻ hỏng → trong phiên vẫn là ảnh AI, hiện lỗi, không viết alt/gửi như ảnh thật (Lá Chắn T-074 j) | `_ai_marked` + `slot_tags` | `test_mark_ai_store_failure_still_ai_in_session`, `test_marked_ai_image_sent_as_ai[luu-the-hong]` |
| 36 | Yêu cầu 1: chọn thư mục/ảnh, xem trước, duyệt alt (nút viết lại), ảnh AI kèm prompt xem/sửa/sao chép, gửi nháp kèm ảnh | Như trên; tạo ảnh AI trong app: nút khóa (đang hoãn) | `test_choose_image_write_alt_approve_and_save`, `test_ai_kind_prompt_view_edit_and_saved`, các test gửi nháp |
| 37 | Yêu cầu 3: `tests/test_app_pages.py` vẫn qua | — | Xem mục Bằng chứng |

Thêm (lỗi tìm ra khi làm): `test_switching_pages_keeps_inputs_and_draft`, `test_subfolder_box_is_fresh_after_moving`, `test_unpick_clears_image_and_alt`.

Điều kiện không thuộc việc của Họa Sĩ: T-063 chạy Mac/Linux, T-079, T-080, T-081 gộp trước (đã gộp); xác nhận `TIEN-DO.md` mục 4b (Chỉ Huy); README (Thư Ký, gồm LC-T069-2); lượt Lá Chắn toàn Giai đoạn 3.

## Bằng chứng

```
$ uv run pytest <41 file test liên quan: tests/test_app*.py (6 file), tests/test_images_*.py (5),
  test_drafts_images, test_wordpress_shortcodes, test_soi_loi_t052/t054/t055/t061/t062/t070/t071/
  t074/t077, test_la_chan_t071/t074/t076, test_shortcode_t061, test_ai_images, test_sanitize,
  test_ui_escape, test_edit_unescape, test_config_tolerance, test_content_edge_cases,
  test_phase2_fixes, test_soi_loi_round3/4/5, test_soi_loi_t003_t009/t016_t020/t031/t051,
  test_t062_image_config>
FAILED tests/test_content_edge_cases.py::test_publish_now_requires_confirmation
1 failed, 4599 passed, 31 skipped, 21 xfailed in 762.10s (0:12:42)

# Test cũ (Soi Lỗi T-002) giả định «Nháp» dùng nút demo «Gửi sang WordPress». Nay «Nháp» là nút
# thật «📤 Gửi nháp»; sửa test cho đúng, giữ nguyên phần chính: «Đăng ngay» phải tick xác nhận.
$ uv run pytest tests/test_content_edge_cases.py tests/test_soi_loi_t019_luot2.py tests/test_soi_loi_t021_t017.py
167 passed in 55.28s

$ uv run pytest tests/test_app_images.py tests/test_wordpress_shortcodes.py   # code cuối
75 passed in 183.44s (0:03:03)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan <7 file đã đổi>
"results": {}
```

Máy Windows 11, có 2 agent khác chạy song song.

### Mở app thật (cổng 8502)

Chạy `uv run --env-file <file tạm> streamlit run app/main.py --server.headless true --server.port 8502` qua khung trình duyệt của Claude, mật khẩu thử tạo trong phiên, ảnh giả do Pillow tạo trong thư mục tạm (2 thư mục gốc: «Anh cong trinh», «Ảnh AI»), một nháp mẫu ở bước Viết & kiểm tra; không khóa AI, không WordPress. Đã xem:

1. Chỗ cần ảnh: khung nét đứt, «Ảnh thật / Ảnh AI», ô ảnh «Chưa chọn ảnh», nút «📁 Chọn ảnh từ thư mục».
2. Khung chọn ảnh: «Thư mục ảnh: Anh cong trinh» (chỉ tên), «Thư mục con (2)», «Đang xem: Anh cong trinh › CT012 - Cổng inox - Tân Phú › truoc», lưới 3 ảnh nhỏ; file chữ đổi đuôi `.jpg` hiện «File này không phải ảnh… (có thể bị đổi đuôi hoặc hỏng)» và nút «Chọn» bị khóa.
3. Chọn IMG_0001: ảnh xem trước, «Thư mục: Anh cong trinh › CT012 - Cổng inox - Tân Phú › truoc», «📷 Ảnh thật», «🤖 Đây là ảnh AI», «Thẻ: Mã CT012 · Cổng inox · Tân Phú · Trước khi làm», «📍 Ảnh có vị trí GPS…», ô alt, chú thích, «✨ AI viết alt», «✅ Đã duyệt».
4. «AI viết alt» không có khóa: hộp đỏ «Chưa có khóa Anthropic (Claude) (ANTHROPIC_API_KEY)…», trang không lỗi.
5. Gõ alt có «0909 123 456»: nhắc «Alt hoặc chú thích có dãy số giống số điện thoại…».
6. Chỗ thứ hai, «Ảnh AI»: khung prompt (sao chép được), «🎨 Tạo ảnh» khóa, «✏️ Sửa prompt»; chọn gốc «Ảnh AI»: «🤖 Mọi ảnh trong thư mục gốc này là ảnh AI…», ảnh chọn xong có «🤖 Ảnh AI» và lý do, lời nhắc «Minh họa».
7. Bước 5 «Nháp»: «Chỗ cần ảnh đã có ảnh, alt đã duyệt: 2/2», báo chưa khai báo WordPress (nút khóa), chọn ảnh đại diện, khung vàng liệt kê «Alt ảnh ở mục «Cổng sau khi sửa»: [code_snippet id=3]» kèm lời nhắc, cảnh báo GPS công khai ngay trên nút «📤 Gửi nháp».
8. Sang «Bài viết» rồi quay lại: vẫn ở bước 5, từ khóa và 2 alt đã duyệt còn nguyên.

Lỗi thấy khi mở app thật và đã sửa (có test): ô «Thư mục con» giữ lựa chọn cũ sau khi vào thư mục con (trình duyệt không xóa lựa chọn khi khóa ô bị xóa) nên không chọn tiếp được; nhãn ô duyệt và nút «Prompt khác» bị cắt chữ.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–3 của phiếu và mọi điều kiện trong «Ghi chú của Chỉ Huy» có test (bảng trên).
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục Bằng chứng). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.
- [x] Báo cáo tại `docs/team/reports/T-056-hoa-si.md`.
- [ ] Soi Lỗi, Lá Chắn (chưa tới lượt).

## Rủi ro và điểm cần chú ý

1. **Nút «Gửi nháp» gửi thật lên website** (ảnh công khai ngay khi tải, kể cả khi bài là nháp). Chỉ Huy cần xác nhận `TIEN-DO.md` mục 4b (Code Snippets ≥ 3.9.2) trước khi gộp, như phiếu ghi. Lần gửi thật đầu tiên nên theo T-059 / Lá Chắn T-054 điều kiện 6 (một bài, tải ảnh về kiểm GPS).
2. **2a (LC-T055-1, nay là khuyến nghị):** chọn ảnh luôn đi từ gốc qua `SubFolder.rel_path`. Riêng «📂 Mở thư mục chứa ảnh»: khi danh sách thư mục cha **bị cắt** (hơn 5.000 mục hoặc quét quá 10 giây) mà chưa thấy thư mục cần mở, app mở thẳng phần còn lại bằng `list_folder(<tên trên ổ lấy từ checked.ref>)`; `list_folder` trả tên trên ổ (T-076) và ảnh chọn ở đó vẫn qua `check_chosen_image`. Không có cách này thì người dùng không tới được thư mục đó (danh sách bị cắt không có nó). Test 2a phủ cả ca này (cũng với đúng chữ ghi trong nháp). Lá Chắn xem có chấp nhận không; nếu không, bỏ nhánh đó (`walk_to_folder`, 4 dòng).
3. Lúc mở nháp, `check_draft_images` (T-055) tự xem danh sách từng tầng thư mục cho ảnh thật (lớp phòng thứ hai, không đệ quy): đó là lần quét do người dùng bấm «Mở» nháp, không phải lúc vẽ trang.
4. **Thân bài gửi lên là đoạn văn thường**: mỗi đoạn một `<p>`, dấu Markdown (`**đậm**`, gạch đầu dòng) hiện nguyên chữ trên website. Chuyển Markdown sang HTML là việc Giai đoạn 5 (phiếu T-031 ghi ngoài phạm vi). Đoạn trích, chuyên mục, meta SEO chưa gửi (bước SEO còn demo).
5. Luồng quét chạy nền: nếu ổ mạng treo hẳn, lúc tắt app Python có thể phải đợi lần quét đó xong (luồng không phải luồng nền «daemon»). Trang vẫn không bị treo.
6. Sửa lỗi sang trang khác mất ô nhập (`remember_inputs`, khóa `_kept`) đụng cả từ khóa, chất liệu thật, tiêu đề mục, bước đang làm (có sẵn từ trước, không riêng phần ảnh). Có test; Soi Lỗi nên thử thêm luồng «Viết bài mới» và «Mở» nháp từ trang Bài viết.
7. Khi kiểm trên máy: công cụ xem trước của Claude đọc cấu hình ở `D:\ProMetal-ToolSEO\.claude\launch.json`, lần đầu chạy nhầm cấu hình `seo-app-main` (repo chính, cổng 8501) khoảng 1 phút; tôi dừng ngay, không mở trang nào trên đó (trước đó cổng 8501 không có app nào chạy). Sau đó thêm tạm cấu hình 8502 vào file đó rồi trả lại đúng bản cũ (so từng byte với bản sao: giống hệt). Dữ liệu thử trong `wt-T-056/data/` đã xóa.

## Đề xuất

- **Thư Ký (sau phiếu này):** README phần ảnh: cách chọn ảnh, ảnh AI (tạo ở Gemini, lưu thư mục có chữ «AI»), nút «Đây là ảnh AI», LC-T069-2 (xóa `data/image_tags.sqlite` thì mất dấu «ảnh AI» đã gắn tay), cảnh báo GPS công khai khi «Gửi nháp».
- **Họa Sĩ (phiếu nhỏ):** trang Cài đặt → Ảnh vẫn in đường dẫn tuyệt đối của `IMAGE_FOLDERS` (`app/views/settings.py:474-477`, có từ trước, ghi chú U2 của Lá Chắn T-048); nên đổi sang `ImageLibrary.roots()` và báo «đi qua lối tắt» như trang Soạn bài. Ngoài phạm vi phiếu này nên chưa sửa.
- **Thợ Máy (Giai đoạn 5):** hàm chuyển thân bài Markdown → HTML an toàn để «Gửi nháp» giữ được chữ đậm, danh sách.
- Khi T-053 (tạo ảnh AI) được làm: nối nút «🎨 Tạo ảnh», «🔄 Prompt khác» (đã có chỗ trên giao diện, đang khóa).

## Câu hỏi cho chủ dự án

Không có.

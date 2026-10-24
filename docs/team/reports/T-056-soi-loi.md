# Báo cáo T-056 · Giao diện chỗ cần ảnh (G3-10) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-056](../tickets/T-056-giao-dien-cho-can-anh.md) |
| Ngày nộp | 2026-10-24 |
| Nhánh | `team/T-056` (kiểm từ `4303374`, gốc `main` `cf8d824`) |
| Kết quả | Hoàn thành (kiểm đầy đủ). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được ngay. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T056-1, phải sửa trước khi gộp), **6 Thấp** (SL-T056-2 → -7). Soát R5: **đạt**. Thử gỡ 30 chỗ sửa trên bản sao: test cũ bắt 27, 2 chỗ không bắt đã có test lấp, 1 đột biến không hợp lệ |

## Tóm tắt (cho chủ dự án)

- Màn hình chọn ảnh làm đúng gần hết các điều kiện an toàn đã đặt ra: tên file, tên thư mục lạ (chữ đảo chiều, ký tự vô hình, dấu Markdown, tên kiểu Mac) hiện đúng nguyên văn; không hiện đường dẫn trên máy; AI chỉ xem đúng ảnh bạn bấm, và chỉ bản ảnh đã bỏ hết thông tin máy; ảnh AI luôn lên web là «Minh họa»; trước nút «Gửi nháp» có nhắc GPS công khai và liệt kê đoạn dạng `[...]`. Tôi đã thử thêm ảnh HEIC của iPhone, ảnh chép dở, thư mục rỗng, thư mục 3.000 ảnh, AI trả chữ độc, xóa nháp đang mở, «Viết bài mới» từ trang Bài viết: đều chạy đúng. Mở app thật trên trình duyệt (ảnh giả, không khóa AI, không website) cũng thấy đúng như vậy.
- **Một lỗi cần sửa trước khi gộp (mức Trung bình):** trong lúc app đang gửi nháp (tải ảnh có thể mất vài chục giây), nếu bạn lỡ bấm đúp hay bấm nút khác, bài nháp và ảnh đã lên website nhưng app "quên" là đã gửi: nút «Gửi nháp» vẫn bật, không có lời nhắc nào, bấm lại là website có **hai bài nháp và ảnh (có GPS) bị tải lên hai lần**. Cách sửa nhỏ: ghi dấu "đang gửi" trước khi gửi.
- Sáu lỗi nhỏ (Thấp), nên sửa cùng lượt: (1) file ảnh bị thay bằng ảnh khác **cùng tên** sau khi bạn duyệt alt thì app vẫn tải ảnh mới lên (kể cả khi ảnh mới có GPS mà bạn chưa xem); (2) đoạn `[...]` vắt qua hai mục của bài không được liệt kê; (3) nhắc số điện thoại bỏ sót tổng đài 8 số (1900 6868) và số viết `0909–123–456`, `0909/123/456`; (4) ảnh đại diện bạn chọn bị trả về ảnh đầu khi sang trang khác rồi quay lại; (5) một ảnh dùng ở hai chỗ, bấm «Đây là ảnh AI» ở chỗ này thì chỗ kia vẫn ghi «Ảnh thật»; (6) ảnh mở từ nháp: mỗi lần bấm «AI viết alt» app lại xem thư mục trên ổ ngay trong trang (ổ Google Drive chậm thì trang chờ lâu hơn).
- Không lỗi nào làm ảnh AI lên web như ảnh thật, làm lộ đường dẫn, mật khẩu, hay chạy được đoạn `[...]` trên website.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t056.py` | Mới: 22 ca (12 qua, 10 `xfail(strict=True)` của SL-T056-1 → -7). Dùng lại ảnh giả, WordPress giả, AI giả của `tests/test_app_images.py` |
| `docs/team/reports/T-056-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Bảng điều kiện → kết quả → bằng chứng

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

## Lỗi tìm thấy

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

## Thử như người dùng thật

**AppTest (test mới, đều qua):** HEIC chọn, xem trước, AI viết alt được; JPEG chép dở bị khóa kèm câu tiếng Việt; thư mục rỗng có câu báo; thư mục 3.000 ảnh: 250 trang, 12 ảnh/trang, mở 0,6 giây, sang trang 0,6 giây (máy có 2 agent khác chạy); tên độc (RLO, U+200B, NFD, `$…$`, Markdown); AI trả chữ độc (link, `<img onerror>`, `<script>`, số điện thoại, shortcode); ảnh AI theo tên file/tên thư mục kèm lý do; «Viết bài mới» ở trang Bài viết khi bài cũ có ảnh, alt đã duyệt (bài mới trống, nháp cũ nguyên, nháp mới riêng); xóa nháp đang mở rồi sang trang khác và quay lại (không sống lại); lỗi lạ khi gửi (câu cố định, không lộ chữ lỗi gốc, khóa nút); `maybe_draft` còn khóa sau khi sang trang khác; ảnh bị xóa sau khi chọn rồi bấm «AI viết alt» (câu báo, 0 lần gọi AI).

**App thật** (worktree, cổng 8513, qua khung trình duyệt; `IMAGE_FOLDERS` trỏ 3 gốc ảnh giả Pillow trong thư mục tạm: «Anh cong trinh», «Ảnh AI», «Anh <U+202E>gpj.exe»; mật khẩu thử tạo trong phiên; không khóa AI, không WordPress):

1. Mở nháp mẫu, «📁 Chọn ảnh từ thư mục»: ô «Thư mục con (4)» hiện `[bấm](evil.example) _đậm_ �ẩn $x$`, `CT030 - Cổng sắt - Thủ Đức` (tên NFD) đúng nguyên văn; vào thư mục con thì ô là ô mới, trống (lỗi Họa Sĩ đã sửa: đạt).
2. File chữ đổi đuôi `.jpg`: câu báo, nút «Chọn» khóa. Chọn `IMG_0001.jpg`: xem trước, «📷 Ảnh thật», thẻ, «📍 Ảnh có vị trí GPS…».
3. Chọn cùng ảnh cho chỗ 2, gõ alt, duyệt cả hai; bước 5: «Chỗ cần ảnh đã có ảnh, alt đã duyệt: 2/2», báo chưa khai báo WordPress (nút khóa), ô «Ảnh đại diện», khung GPS ngay trên nút.
4. Chọn ảnh đại diện «Cổng sau khi sửa», sang «Bài viết» rồi quay lại: bước 5, alt còn nguyên, **ảnh đại diện về «Bản lề cổng»** (SL-T056-5).
5. Bước 3, bấm «Đây là ảnh AI» ở chỗ 1: chỗ 2 vẫn «📷 Ảnh thật» (SL-T056-6).
6. Ô «Thư mục ảnh»: gốc có RLO hiện «Anh �gpj.exe» (không đảo chữ). `innerText` cả trang: không có đường dẫn ổ đĩa, không U+202E, U+200B.

Không bấm «Gửi nháp» tới website nào (không khai báo WordPress). Xong thì dừng app, trả `D:\ProMetal-ToolSEO\.claude\launch.json` về bản sao lưu (so từng byte: giống; SHA-256 `a5607e8c…f169` như trước khi sửa), xóa `data/` của worktree. Không start `seo-app-main`.

## Thử gỡ chỗ sửa (bản sao `git archive HEAD`)

Mỗi đột biến thay đúng một đoạn trong `app/views/write.py` của bản sao (thư mục tạm), chạy test chỉ định; test phải hỏng.

| Đột biến | Kết quả |
|---|---|
| M1 `shown_name` không cô lập hướng chữ · M2 `name_md` không escape · M3 `st.image` nhận byte gốc · M4 AI nhận byte gốc · M5 `ai_generated=False` · M6 `mark_ai` không nhớ ảnh AI · M8 gửi không kiểm lại · M9 `DraftImage` thẻ mặc định · M10 bỏ cảnh báo GPS · M11 shortcode không xét alt · M12 mở nháp không `ai_roots` · M13 quét trong luồng trang · M14 lỗi gửi không escape · M15 `maybe_draft` không khóa · M16 bỏ so không phân biệt hoa thường · M17 bỏ nhánh danh sách bị cắt · M18 bỏ `remember_inputs` · M19 bỏ nhắc số điện thoại · M20 sửa alt không bỏ duyệt · M22 bỏ tên sau `resolve()` · M23 không báo lối tắt · M24 `resolve_many` cả lần quét · M25 AI viết alt ngay khi chọn · M26 lỗi AI câu cố định · M27 `post.status` không báo · M29 `dropped_images` không báo · M30 mở nháp dùng thẻ trong nháp | **27/27 bắt được** (test cũ của Họa Sĩ) |
| M7 `slot_tags` bỏ nhánh `_ai_marked` | Test cũ **không bắt** → thêm `test_two_spots_mark_ai_store_failure_both_sent_as_ai`: **bắt được** |
| M21 câu báo file thẻ hỏng hiện đường dẫn đầy đủ | Test cũ **không bắt** → thêm `test_broken_tag_file_note_has_no_folder_path`: **bắt được** |
| M28 (hiện thêm tên thư mục đã escape) | Không hợp lệ: tên thư mục đã escape, cô lập hướng chữ được phép hiện (dòng «Thư mục:»), không phải vi phạm điều kiện e |

## Soát R5

- `tests/test_content_edge_cases.py::test_publish_now_requires_confirmation`: bỏ đúng 1 dòng `assert not button(at, send).disabled  # Nháp: được gửi` (nút demo «Gửi sang WordPress» không còn ở «Nháp»), thay bằng kiểm có nút thật «📤 Gửi nháp» và kiểm «Hẹn giờ» không cần ô xác nhận. Phần an toàn chính giữ nguyên: «Đăng ngay» khóa nút cho tới khi tick «Tôi đã đọc lại bài và đồng ý đăng ngay». Nút «Gửi nháp» thật (chỉ khi bấm, bài luôn nháp) có test riêng ở `tests/test_app_images.py`. **Không nới điều kiện nào.**
- `tests/conftest.py`: chỉ thêm fixture tự động `_never_touch_real_image_tags`, đúng điều kiện 2f T-052; không sửa fixture cũ.
- `git diff cf8d824..HEAD --stat`: không xóa, `skip` hay `xfail` thêm test nào.

## U1, U2, A3

- **U1:** 6 chỗ `unsafe_allow_html` trong `write.py`; chỗ mới của T-056 chỉ có 2 khung giữ chỗ HTML cố định (`img-ph`, :921, :1339), không chữ từ máy, AI, người dùng (đối chiếu `test_names_from_disk…`, `test_evil_ai_alt…`). Chữ từ WordPress (`message`, `status`, câu lỗi) qua `escape_markdown`; tên file, địa chỉ ảnh đã lên qua `st.text`; `edit_link` do client dựng (`client.py:1227`), `source_url` đã kiểm `is_site_link`.
- **U2:** trang Soạn bài vẫn sau màn hình đăng nhập (`app/main.py` không đổi); app thật chạy `localhost`. Không đường dẫn tuyệt đối (điều kiện 4). Còn trang Cài đặt → Ảnh in đường dẫn `IMAGE_FOLDERS` (có từ trước, Họa Sĩ đã nêu, ngoài phạm vi).
- **A3:** ảnh chưa chọn không rời máy (M25); AI chỉ nhận byte `make_ai_image` (M4); test không gọi mạng thật (WordPress giả `fake_wordpress`, AI giả `fake_ai`, bộ chặn mạng của `conftest.py`).

## Ghi nhận (không phải lỗi, để Lá Chắn quyết)

1. **2a (nay là khuyến nghị):** khi danh sách thư mục cha bị cắt, «📂 Mở thư mục chứa ảnh» gọi `list_folder` với phần còn lại lấy từ `checked.ref` (:1189-1196), kể cả ảnh không còn dùng được, khi đó `ref` là chữ trong nháp. Thử: nháp ghi `…/TRUOC/DA_XOA.jpg` (thư mục thật `truoc`, ảnh đã xóa), cha bị cắt → `list_folder(0, "…/TRUOC")`, trả tên trên ổ `truoc`. Họa Sĩ đã nêu (Rủi ro 2). `list_folder` vẫn chặn `..`, lối tắt, đường dẫn tuyệt đối.
2. Bài đã gửi thành công chỉ được nhớ trong phiên (`_wp_sent`): mở lại nháp hôm khác, «Gửi nháp» tạo thêm bài nháp mà không có ô xác nhận. Cần trường mới trong `DraftSnapshot` (`seo_app`, ngoài phạm vi T-056).
3. Alt dài hơn 500 ký tự bị cắt khi lưu, gửi (`MAX_ALT_CHARS`); giao diện đã nhắc từ 125 ký tự.
4. Hai luồng quét (`_scan_pool`): ổ mạng treo hẳn có thể giữ cả hai (Họa Sĩ Rủi ro 5); thêm: một lần quét khác xong thì `S.pop("_scan_pending")` (:1163) xóa cả lần quét đang chờ của thư mục khác, quay lại thư mục chậm sẽ gửi thêm một lần quét nữa.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn được ngay** (Lá Chắn kiểm song song với lượt sửa).

Điều kiện trước khi gộp `main`:

1. Họa Sĩ sửa **SL-T056-1** (Trung bình), gỡ `xfail` của `test_interrupted_send_locks_resend`; Soi Lỗi kiểm lại rút gọn.
2. Nên sửa cùng lượt SL-T056-2 → -7 (Thấp, đều trong `app/views/write.py`); không sửa thì Chỉ Huy lập phiếu theo dõi. SL-T056-2 nên sửa cùng SL-T056-1 nếu Lá Chắn nâng mức (GPS công khai).
3. Giữ 2 test lấp chỗ hổng (`test_two_spots_mark_ai_store_failure_both_sent_as_ai`, `test_broken_tag_file_note_has_no_folder_path`) khi sửa.

## Bằng chứng

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

## Rủi ro và điểm cần chú ý

- SL-T056-1 chỉ tái hiện được bằng AppTest (ném `StopException` ngay sau khi gửi xong, đúng chỗ Streamlit ngắt lần chạy) và đọc mã Streamlit 1.65; không thử trên website thật (không có staging, nút gửi thật). Cơ chế ngắt lần chạy khi người dùng bấm là hành vi mặc định của Streamlit (`runner.fastReruns`).
- Lần gửi thật đầu tiên nên theo Họa Sĩ Rủi ro 1 (một bài, tải ảnh về kiểm GPS) và chờ Chỉ Huy xác nhận `TIEN-DO.md` mục 4b.

## Đề xuất

- **Họa Sĩ (lượt sửa T-056):** SL-T056-1 → -7 theo cột «Gợi ý sửa».
- **Thợ Máy (sau, cùng Giai đoạn 5):** nháp nhớ dấu file ảnh đã duyệt (cỡ, giờ sửa) để mở lại nháp hôm khác vẫn biết ảnh bị thay (phần còn lại của SL-T056-2); nháp nhớ "đã gửi lên WordPress, mã bài" để không tạo nháp trùng (Ghi nhận 2).
- **Họa Sĩ (phiếu nhỏ, đã nêu):** trang Cài đặt → Ảnh không in đường dẫn `IMAGE_FOLDERS`.

## Câu hỏi cho chủ dự án

Không có.

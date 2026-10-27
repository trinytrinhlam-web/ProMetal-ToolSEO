# Báo cáo T-041 · Bước 4 «SEO» của Soạn bài chạy thật (phần giao diện)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-041](../tickets/T-041-buoc-seo-that.md) |
| Ngày nộp | 2026-10-26 |
| Nhánh | `team/T-041` (từ `13a554c`: `main` có T-056, T-085, T-086, T-087 + phần logic của Thợ Máy) |
| Kết quả | Hoàn thành yêu cầu 1–6 của phiếu, nút chép sang SiteSEO, chạy khi chưa kết nối WordPress, công tắc «Ghi SEO lên website» (phần giao diện của T-042), xóa mẫu demo bước SEO; mỗi điều kiện có test (23 test `AppTest`). **Còn lại, cần Chỉ Huy:** (1) 15 test client WordPress hỏng trên nhánh do phần logic, không do giao diện (mục «Phát hiện» số 1); (2) trang Kết nối WordPress chưa hiện `siteseo_status` (ngoài các file được giao, mục «Phát hiện» số 3) |

## Tóm tắt (cho chủ dự án)

- Bước **4 · SEO** của trang Soạn bài không còn là bản demo. Mở một bài đang soạn rồi sang bước SEO:
  - **Meta title, meta description**: bấm «✨ AI gợi ý tiêu đề và mô tả SEO»; mỗi ô có nút 🔄 để AI viết lại riêng ô đó (ô kia giữ nguyên), nút ↶ ↷ để quay lại bản trước / tới bản sau. Bạn tự sửa chữ cũng thành một bản mới, quay lại được bản AI.
  - Số ký tự đếm đúng như Google thấy (title tính cả đuôi « | Pro-Metal»), nhãn màu **Nên** (xanh) / **Cảnh báo** (cam) / **Chặn** (đỏ) kèm lý do.
  - **Đường dẫn (slug)**: tự gợi ý từ từ khóa, sửa được (tự bỏ dấu, nối bằng gạch ngang), nút 🔄 gợi ý lại.
  - Kiểm trùng với bài đã đăng trên website: tiêu đề, mô tả, slug trùng hệt bài khác thì «Chặn», giống nhiều thì «Cảnh báo», kèm tên bài bị trùng.
  - **Xem trước kiểu Google** và khung **«Chép sang SiteSEO»** (tiêu đề đã gắn đuôi, mô tả, slug; góc mỗi khung có nút chép). Ô đang «Chặn» thì không cho chép, ghi rõ lý do.
  - **Liên kết nội bộ**: AI gợi ý chỗ đặt link tới bài đã đăng (phần mềm chọn bài đích, AI chỉ chọn cụm từ có sẵn trong bài), bảng «Dùng / Cụm từ trong bài / Trỏ tới bài» (bỏ tick dòng không muốn), nút «🔄 Tải lại danh sách bài» khi vừa đăng bài mới.
  - **Schema Hỏi đáp (FAQ)**: bài có mục «Câu hỏi thường gặp» thì hiện đoạn mã schema để xem và chép, kèm ô «Dùng schema Hỏi đáp (FAQ) này cho bài».
  - Mọi lựa chọn **tự lưu vào nháp** như các bước trước (đóng tab, mở lại vẫn còn).
- Chưa kết nối WordPress: chỉ một dòng báo nhẹ «chưa kết nối»; meta, slug, chép SiteSEO, schema vẫn dùng được.
- Bước **5 · Xuất bản**:
  - Dòng «SEO: …» trong «Kiểm tra trước khi gửi» nay là thật (trước ghi «bản demo, chưa gửi»).
  - Công tắc **«Ghi SEO lên website»**, mặc định **tắt**. Bật thì ngay sau khi tạo bài nháp, phần mềm ghi tiêu đề SEO, mô tả SEO, từ khóa chính vào hộp SiteSEO của **chính bài nháp vừa tạo**, rồi hỏi lại website để chắc bài vẫn là nháp. Ô đang «Chặn» thì không ghi, có dòng báo trước khi gửi và trong câu kết quả.
- Đã thử trên trình duyệt thật với một WordPress giả chạy trên máy (không gửi gì lên suachuacuasat.com).

## Chủ dự án tự mở app xem bước SEO

Phần này có trong app **sau khi Chỉ Huy gộp T-041 vào `main`**.

1. Bấm đúp `run.bat`, đăng nhập, chọn menu **Soạn bài**.
2. Mở một bài trong «📂 Bài đang soạn dở» đã có bài viết (bước 3), hoặc soạn bài mới tới bước 3.
3. Bấm **4 · SEO**. Bấm «✨ AI gợi ý tiêu đề và mô tả SEO» (cần khóa AI đã nhập ở Cài đặt; chưa có khóa thì các nút AI mờ, vẫn tự gõ được).
4. Thử 🔄 ở từng ô, ↶ ↷, tự sửa chữ; xem nhãn màu, số ký tự, khung xem trước Google bên phải.
5. Bấm biểu tượng chép ở góc các khung «Chép sang SiteSEO», dán vào hộp SiteSEO của bài nháp trong trang quản trị WordPress.
6. Liên kết nội bộ (cần WordPress đã kết nối và có bài đã đăng cùng chủ đề): bấm «✨ AI gợi ý liên kết», bỏ tick «Dùng» ở dòng không muốn.
7. Mở «Schema (dữ liệu có cấu trúc cho Google)». Bài cần có mục «Câu hỏi thường gặp» (hay «Hỏi đáp»), mỗi câu hỏi là dòng in đậm hay tiêu đề con kết thúc bằng «?».
8. Sang **5 · Xuất bản**: xem dòng «SEO: …»; để công tắc «Ghi SEO lên website» tắt nếu muốn chép tay. Lưu ý: không có trang thử, «📤 Gửi nháp» tạo **bài nháp thật** trên website.

## Yêu cầu → cách làm → test

Mọi test ở `tests/test_t041_seo_ui.py` (`AppTest`, AI giả, WordPress giả, file cache danh sách bài trong thư mục tạm; không gọi AI, WordPress, mạng thật).

| # | Yêu cầu (nguồn) | Cách làm (`app/views/write.py`) | Test |
|---|---|---|---|
| 1a | Ô title/description, 🔄 viết lại riêng từng ô, quay lại bản trước (phiếu 1) | `meta_field`: ô sửa + 🔄 (`suggest_meta(writer, "title"/"description")`, truyền ô kia làm `current_*`) + ↶ ↷ (`meta_step`). Các bản giữ trong `seo_<ô>_versions`/`_ver` qua `DraftMetaVersions` (≤ 20 bản, không bỏ bản đang dùng). Người dùng sửa → bản mới (`meta_edited`). Gợi ý AI xong thì `st.rerun()` (nút ↶ ↷ vẽ theo trạng thái mới; lỗi này `AppTest` tìm ra) | `test_ai_meta_then_rewrite_each_box_and_undo`, `test_user_edit_is_a_new_version_counted_nfc_with_brand` |
| 1b | Đếm ký tự NFC, màu Nên / Cảnh báo / Chặn (phiếu 1; SL-T041-2) | `check_lines`: huy hiệu `:green/orange/red-badge[…]` theo `worst(...)` của kiểm dạng và kiểm trùng; số ký tự là `check.length` (title tính cả đuôi, chữ đã NFC). Ô sửa giữ title **không** đuôi (`strip_brand` cho gợi ý AI) | `test_user_edit_is_a_new_version_counted_nfc_with_brand` (gõ NFD, đếm NFC + đuôi), `test_blocked_title_is_red_and_not_copyable` |
| 1c | Xem trước kiểu Google, kiểm lại escape (phiếu 1) | `ui.serp_preview(check.value, host › slug, description)`: `html.escape` mọi chữ (chỗ `unsafe_allow_html` duy nhất của bước, có từ bản demo) | `test_serp_preview_escapes_everything` |
| 2 | Slug: gợi ý, sửa, kiểm trùng (phiếu 2) | `slug_field`: `make_slug(từ khóa)`, sửa thì `make_slug("", given=…)`, 🔄 gợi ý lại; `check_slug` + `check_slug_duplicates` | `test_slug_suggest_edit_and_normalize`, `test_duplicates_from_site_are_plain_text`, `test_reload_listing_button_refreshes` |
| 3 | Bảng «Dùng / Cụm từ trong bài / Trỏ tới bài», nút «Tải lại danh sách bài» (phiếu 3) | `links_panel`: `select_candidates` (bài hướng dẫn) → `writer.internal_links` → `DraftLink.from_link`; `st.data_editor` chỉ cho sửa cột «Dùng»; «Trỏ tới bài» là tiêu đề bài trên site (ô bảng = chữ thuần) hay «bài #id». `published_listing` giữ danh sách trong phiên; nút tải lại → `site_listing(..., refresh=True)` | `test_internal_links_from_ai_table_and_saved`, `test_use_column_untick_is_kept`, `test_reload_listing_button_refreshes` |
| 4 | Schema FAQ, chữ thuần, không HTML (phiếu 4; LC-T038 đk 3) | `faq_panel`: `build_article_faq(current_parts())`; `json_ld` **chỉ** bằng `st.code(..., language="json")`; câu báo `issues` qua `escape_markdown`; ô «Dùng schema …» (`seo_use_faq`) | `test_faq_schema_shown_only_as_code`, `test_seo_step_is_real_and_works_without_wordpress` (câu `MSG_NO_FAQ`) |
| 5 | Tự lưu mọi lựa chọn vào nháp (phiếu 5) | `snapshot()` thêm `seo=seo_snapshot()` (`DraftSeo`: các bản meta + bản đang dùng, slug, liên kết + «Dùng», `use_faq`); `open_draft` → `restore_seo`. Khóa `seo_*` vào `COMPOSE_PREFIXES`; `seo_slug`, `seo_use_faq` vào `KEEP_KEYS` (đổi trang ở menu không mất) | `test_seo_choices_saved_and_restored` (phiên mới mở lại nháp), `test_switching_pages_keeps_seo_choices`, `test_internal_links_from_ai_table_and_saved`, `test_use_column_untick_is_kept`, `test_faq_schema_shown_only_as_code` |
| 6 | Bỏ nhãn «Bản demo» của bước; `test_app_pages.py` vẫn qua (phiếu 6) | Bỏ `count_badge`, `step_seo` demo, các khóa demo (`title_v`, `desc_v`, `meta_title`, `meta_desc`, `next_meta`); dòng SEO ở «Kiểm tra trước khi gửi» thành thật (`seo_check`, không gọi website) | `test_seo_step_is_real_and_works_without_wordpress`, `test_publish_checklist_shows_real_seo_state`; `tests/test_app_pages.py` qua |
| 7 | Nút chép title/description/slug để dán vào SiteSEO (ghi chú 2026-10-16) | `siteseo_panel`: `final_seo` (dựa trên `siteseo_copy`): title đã `with_brand`, mỗi trường một `st.code` (nút chép sẵn); trường bị Chặn → «chưa chép được» + lý do (chữ thuần) | `test_siteseo_copy_has_final_texts`, `test_blocked_title_is_red_and_not_copyable` (thẻ HTML, `%%`, `[gallery]`), `test_duplicates_from_site_are_plain_text` (trùng hệt) |
| 8 | Chưa kết nối WordPress: báo nhẹ, phần khác vẫn dùng được (ghi chú 2026-10-16) | `site_listing(store, None)` → `notice` (`MSG_NOT_CONNECTED`) hiện bằng một `st.caption`; kiểm trùng với danh sách rỗng; nút AI liên kết mờ | `test_seo_step_is_real_and_works_without_wordpress` |
| 9 | Công tắc «Ghi SEO lên website» mặc định tắt; sau khi tạo nháp gọi `set_seo_meta`, hiện `result.message` chữ thường (ghi chú 2026-10-17, T-042) | `seo_toggle` (bước 5). `send_draft` lấy chữ (`seo_request`) **trước** dấu «đang gửi»; `send_and_record` gọi `write_seo` **sau** `record_outcome` (nháp đã ghi «đã gửi»), bằng chính client vừa tạo nháp; câu kết quả hiện bằng `st.info(escape_markdown(...))` | `test_seo_write_is_off_by_default`, `test_seo_written_after_draft_with_brand_and_rechecked` |
| 10 | Xóa mẫu SEO không dùng trong `seo_app/demo.py` | Xóa `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` (không còn chỗ nào dùng) | `tests/test_app_pages.py` (mở mọi trang, mọi bước) |

## Điều kiện kiểm định → test

| Điều kiện | Cách làm | Test |
|---|---|---|
| Lá Chắn T-038 đk 3: `json_ld` bằng `st.code`, không `unsafe_allow_html` | như yêu cầu 4 | `test_faq_schema_shown_only_as_code` (không khối HTML nào có «FAQPage») |
| Lá Chắn T-036 số 5: `FieldCheck.messages` (có tên bài trên site) chữ thuần | `check_lines`, `siteseo_panel`: `st.caption(escape_markdown(...))` | `test_duplicates_from_site_are_plain_text` (tên bài `<img onerror>` + `[…](javascript:…)`), `test_blocked_title_is_red_and_not_copyable` |
| Lá Chắn T-037: tiêu đề/meta từ site hiện chữ thuần; `truncated` thì không kết luận «link hỏng» | Tiêu đề bài: ô bảng `data_editor` hay `escape_markdown`; bước SEO không kiểm link nào (link chỉ chèn lúc dựng HTML ở GĐ5), danh sách chưa đủ chỉ hiện `MSG_TRUNCATED` | `test_duplicates_from_site_are_plain_text`, `test_internal_links_from_ai_table_and_saved`, `test_truncated_listing_is_only_a_notice` |
| Lá Chắn T-039 đk 2b: nháp lưu `DraftLink.from_link`, không địa chỉ; 2c: chữ site/AI (`rejected`) chữ thuần | `S.seo_links = [DraftLink.from_link(...)]`; `rejected` qua `escape_markdown`; prompt AI chỉ có mã bài, không link/slug | `test_internal_links_from_ai_table_and_saved` (không «http» trong nháp, không link/slug trong prompt) |
| Lá Chắn T-042: công tắc mặc định tắt; không nạp mã bài vào client; client không ở `st.cache_resource`; câu báo chữ thường; title qua `with_brand` | `wordpress_client(write_seo=...)` tạo client mới mỗi lần vẽ (không cache); ghi SEO trong cùng lần gửi, bằng chính client vừa `create_draft` (mã bài trong `_created_post_ids` của nó); không lưu client qua các lần bấm nên không cần `session_state` | `test_seo_write_is_off_by_default` (không request SiteSEO, không câu báo SEO), `test_seo_written_after_draft_with_brand_and_rechecked`, `test_seo_write_needs_client_that_created_the_draft` |
| LC-T042-2: ghi qua Abilities xong hỏi lại trạng thái bài, không còn nháp thì báo | `write_seo`: `seo.written and seo.route == "abilities"` → `client._own_draft(post_id)`; lỗi → nối «Kiểm lại ngay sau khi ghi SEO: …» vào câu kết quả | `test_post_published_during_seo_write_is_reported`, `test_seo_written_after_draft_with_brand_and_rechecked` (đúng 2 lệnh GET bài 501) |
| T-086 Ghi nhận 2: không dùng mã bài lưu trong nháp để ghi lên website | `write_seo` chỉ dùng `result["post_id"]` của **lần gửi này**; mở lại nháp đã gửi không có đường nào ghi SEO | `test_reopened_sent_draft_never_writes_seo_to_stored_post` (nháp lưu mã 777: không request nào tới 777; tạo thêm nháp mới thì chỉ ghi cho 501), `test_seo_write_needs_client_that_created_the_draft` |
| Góp ý G4 Soi Lỗi T-041: không hiện «Bài hướng dẫn chưa có trang dịch vụ đích…» | `links_panel` bỏ đúng câu `NO_ORDER_NOTICE`, các câu báo khác vẫn hiện | `test_internal_links_from_ai_table_and_saved` |
| U1 | Không thêm `unsafe_allow_html` (vẫn đúng các chỗ như trước; chỗ xem trước Google có từ bản demo, chữ qua `html.escape`) | `test_serp_preview_escapes_everything`, các test trên |
| U2, D3 | Trang vẫn qua cổng đăng nhập như cũ; test dùng AI giả, WordPress giả, bộ chặn mạng của `conftest` | cả bộ test |

## Quyết định thiết kế cần Soi Lỗi, Lá Chắn xem

1. **«Chặn» vì trùng hệt bài đã đăng = không chép, không ghi.** `siteseo_copy` (Thợ Máy) chỉ Chặn theo dạng chữ; kiểm trùng cho mức «Chặn» riêng. Giao diện gộp hai thứ trong `final_seo` (dùng chung cho khung chép, `seo_request`, dòng kiểm ở bước 5): nhãn đỏ «Chặn» thì không chép được và không ghi lên SiteSEO (chỉ ghi các trường còn lại, câu kết quả nói «Không ghi Tiêu đề SEO: …»). Tìm ra khi thử app thật (tiêu đề trùng bài đã đăng vẫn chép và ghi được).
2. **Ghi SEO nằm trong vùng «không lệnh `st.*`» của T-086.** `seo_request()` đọc trang trước `S._wp_sending = holder`; `write_seo` không chạm `st.session_state`, chạy sau `record_outcome` nên nháp đã ghi «đã gửi (mã bài)» trước khi gọi SiteSEO. Lần chạy mới (fastReruns) vẫn đợi `holder["done"]` như T-086, nên câu kết quả SEO không mất. Thời gian trong vùng này dài thêm tối đa 4 lệnh (dò Abilities, kiểm còn nháp, ghi, hỏi lại).
3. **Lỗi khi ghi SEO không làm hỏng kết quả gửi nháp:** `WordPressError` → câu cố định của client; lỗi lạ → câu cố định `MSG_SEO_UNEXPECTED` (không chép lỗi thô), kết quả «Đã tạo bài nháp (mã …)» và trạng thái trong nháp giữ nguyên (`test_unexpected_seo_error_keeps_draft_result`).
4. **LC-T042-2 dùng hàm riêng `client._own_draft`** (client chưa có hàm công khai «hỏi lại bài còn là nháp»). Đề xuất phiếu sửa client sau mở hàm này ra công khai; tôi không được sửa `seo_app/wordpress/**`.
5. **Danh sách bài đã đăng** tải một lần mỗi phiên (và qua file cache `data/site_index.sqlite` giữa các phiên, đã thấy trên app thật: phiên mới không gọi lại website). Bước 5 chỉ tải khi công tắc bật (cần kiểm trùng trước khi ghi); dòng kiểm ở bước 5 không tải (chỉ xem thì không gọi website, giữ đúng các test T-086 đếm request).
6. **Sửa ở bước 5 giữ tối thiểu** (T-089 đang sửa bước 5): `wordpress_client(write_seo=...)`, 1 dòng trong `send_draft`, 1 dòng trong `send_and_record`, 2 dòng trong `send_result`, 1 dòng gọi `seo_toggle()` và 1 dòng `wordpress_client(...)` trong `draft_panel`, 1 dòng `seo_check()` trong `step_publish`. Mọi phần còn lại nằm trong khối SEO.
7. **Test bảng «Dùng»:** `AppTest` không sửa được ô `st.data_editor`, nên `test_use_column_untick_is_kept` thay `st.data_editor` bằng hàm trả bảng đã sửa (như người dùng bỏ tick). Đã thử tick thật trên trình duyệt: nháp lưu `use=True`.
8. Ô meta trống hiện «Chặn · 0 ký tự» (mức của `check_title`/`check_description` cho chữ trống). Hơi gắt với bài mới mở bước SEO; giữ đúng logic, chủ dự án thấy khó chịu thì đổi sau.

## Phát hiện (cần Chỉ Huy)

1. **15 test client WordPress hỏng trên nhánh `team/T-041`, do phần logic, không do giao diện.** `tests/test_wordpress_seo_meta_t042.py::test_bad_text_is_blocked_before_any_request` (6 ca: `\x00`, `\x7f` × 3 trường) và `tests/test_soi_loi_t042.py::test_more_bad_text_is_blocked_before_any_request` (9 ca: `\x07`, `\x1b`, `\x9b` × 3 trường): «DID NOT RAISE WordPressError». Nguyên nhân: `94ba458` (Thợ Máy T-041 phần 1, LC-T036-1) làm `normalize_meta` bỏ ký tự Cc; `_seo_text` (`seo_app/wordpress/client.py:1621`) kiểm `_CONTROL_CHARS` trên chữ **đã** chuẩn hóa nên không còn thấy ký tự điều khiển: chữ có ký tự điều khiển bị lặng lẽ bỏ ký tự rồi ghi, thay vì bị chặn như T-042 đòi. Thử: `normalize_meta('Cửa\x00sắt') == 'Cửasắt'`; ở `94ba458^` hàm này chỉ bỏ Cf. Chạy hai nhóm test này trên bản sao `git archive`: `94ba458^` 102 qua, `94ba458` 15 hỏng. Hai file test này không có trong danh sách test Thợ Máy chạy (báo cáo Thợ Máy mục «Bằng chứng»). Đề xuất (Thợ Máy): kiểm `_CONTROL_CHARS` cả trên `raw` như các kiểm khác (`for text in (raw, value, folded)`), hoặc Chỉ Huy duyệt đổi test. Ngoài các file tôi được sửa.
2. `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` hỏng một lần khi máy rất bận (đã biết, Thợ Máy ghi ở lượt 2); chạy riêng 2/2 qua.
3. **Trang Kết nối WordPress chưa hiện `info.siteseo_status`** (ghi chú 2026-10-17 của phiếu). `app/views/wordpress.py` không nằm trong các file được giao cho lượt này; việc nhỏ (thêm một dòng `st.caption(escape_markdown(info.siteseo_status))` và một test). Chỉ Huy giao thêm thì tôi làm ngay trên nhánh này.
4. Góp ý nhỏ (Thấp, không chặn): bài có mục «Câu hỏi thường gặp» nhưng chưa có câu hỏi đúng dạng thì schema báo «Bài chưa có mục Hỏi đáp…» (câu của `schema.py`, dễ hiểu nhầm; Thợ Máy viết lại khi tiện). Chưa có khóa AI thì câu «Chưa có liên kết nội bộ nào: bấm «AI gợi ý liên kết»» trỏ tới nút đang mờ (dòng cảnh báo thiếu khóa ở đầu trang đã giải thích).

## Thử gỡ chỗ làm (đột biến)

Bản sao `git archive HEAD`, `PYTHONPATH` trỏ bản sao, môi trường của worktree; mỗi đột biến chạy các test nên bắt nó (script `T-041-hoa-si-scripts/mutate.py` trong thư mục ghi chú chung).

| Đột biến | Kết quả |
|---|---|
| M1 «Chặn» vì trùng vẫn cho chép, vẫn ghi | bắt được (2 test) |
| M2 công tắc bị bỏ qua (luôn tạo yêu cầu ghi SEO) | lần đầu **không bắt**: client tạo với `write_seo=False` vẫn chặn (lớp thứ hai, không request nào), nhưng trang hiện thừa câu «Chưa bật ghi SEO…» → siết `test_seo_write_is_off_by_default` (không câu báo SEO nào khi tắt) → bắt được |
| M3 không hỏi lại trạng thái bài sau khi ghi (LC-T042-2) | bắt được (2 test) |
| M4 ghi tiêu đề chưa gắn đuôi thương hiệu | bắt được |
| M5 câu báo có tên bài trên website không escape | bắt được |
| M6 schema hiện bằng HTML thay vì `st.code` | bắt được |
| M7 hiện câu «chưa có trang dịch vụ đích» (G4) | bắt được |
| M8 nháp không lưu phần SEO | bắt được (2 test) |
| M9 bỏ tick «Dùng» không được nhớ | bắt được |
| M10 ghi SEO gặp lỗi lạ làm vỡ trang | bắt được |
| M11 chữ người dùng sửa không thành bản mới | bắt được |
| M12 không gọi ghi SEO sau khi tạo nháp | bắt được |
| M13 ô sửa title giữ cả đuôi thương hiệu của gợi ý AI | bắt được |

## Thử trên trình duyệt thật

Worktree, cổng 8502 (cấu hình tạm trong `D:\ProMetal-ToolSEO\.claude\launch.json`, đã trả đúng bản cũ, SHA-256 `a5607e8c…f169`); WordPress giả https://localhost:8747 (chỉ `127.0.0.1`, chứng chỉ tự ký, app tin bằng `REQUESTS_CA_BUNDLE`, không tắt kiểm SSL), có danh sách bài đã đăng (một bài tên `**Sửa cổng inox** [giá rẻ](javascript:alert(1))`), Abilities của SiteSEO. Hai nháp mẫu (script `setup_app_t041.py`). Không có khóa AI. Xong đã xóa `data/` của worktree, đóng cổng.

- Nháp A: bước SEO mở lại đúng «Bản 2/2», mô tả, slug, bảng liên kết (tên bài lấy từ website), ô schema đã tick, JSON-LD trong khung mã có nút chép. Màn hình rộng: ô và nút 🔄 ↶ ↷ cùng hàng.
- Sửa title thành bản 3/3 trùng meta title bài đã đăng: «Chặn · 53 ký tự», câu báo hiện nguyên văn tên bài (dấu `**`, `[…](javascript:…)` là chữ thường, không thành link). Lần đầu khung chép vẫn cho chép title này → sửa (quyết định số 1), thử lại: «Tiêu đề SEO: chưa chép được. …».
- Tick «Dùng» ở bảng: nháp lưu `use=True` ngay.
- Bước 5: dòng «⚠️ SEO: Tiêu đề SEO chưa dùng được (xem bước SEO)»; bật công tắc: «Sẽ không ghi Tiêu đề SEO…»; «Gửi nháp»: website giả nhận đúng thứ tự tạo nháp 501 → dò Abilities → kiểm còn nháp → ghi SEO (chỉ mô tả, từ khóa chính, không có tiêu đề) → hỏi lại bài 501; trang hiện «Đã tạo bài nháp trên WordPress (mã 501)», «Đã ghi SEO vào hộp SiteSEO của bài nháp. Không ghi Tiêu đề SEO: …», khóa «đã gửi» của T-086. Nhật ký request: `T-041-hoa-si-scripts/requests-app-that.jsonl`.
- Nháp B (chưa có SEO): ô trống «Chặn · 0 ký tự», slug gợi ý `gia-cong-inox`, schema báo câu cố định. «Tải lại danh sách bài»: website giả nhận lại 2 lệnh đọc danh sách.

## Bằng chứng

Windows 11, Git Bash, worktree `wt-T-041` (máy rất bận: các phiên khác cùng chạy test).

```
$ uv run pytest tests/test_t041_seo_ui.py                       # code cuối
23 passed in 57.39s

$ uv run pytest <32 file mở trang Soạn bài hay kho nháp: tests/test_app*.py, test_t041_seo_ui.py,
    test_t086_send_state.py, test_storage_send_state.py, test_soi_loi_t056.py, test_la_chan_t056.py,
    test_soi_loi_t086.py, test_la_chan_t086.py, test_content_edge_cases.py, test_config_tolerance.py,
    test_edit_unescape.py, test_phase2_fixes.py, test_soi_loi_round3/4/5.py, test_ui_escape.py, …>
    # write.py bản cuối (1de271b); sau đó chỉ đổi test, chạy lại riêng ở dòng trên
2505 passed, 7 skipped, 6 xfailed in 888.23s (0:14:48)

$ uv run pytest <38 file liên quan: tests/test_app*.py, các file test_t041_*, test_onpage_*, test_soi_loi_t036…t042,
    test_la_chan_t039/t040/t056, test_storage_drafts.py, test_drafts_images.py, test_site_index*.py,
    test_wordpress_seo_meta_t042.py, test_t040_prompts.py, test_content_rules.py, test_content_workflow.py, …>
    # chạy lúc phần 3–4 đang sửa (write.py đổi giữa chừng); các ca hỏng không liên quan write.py
FAILED tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted
FAILED tests/test_wordpress_seo_meta_t042.py::test_bad_text_is_blocked_before_any_request[…]   # 6 ca, Phát hiện số 1
FAILED tests/test_soi_loi_t042.py::test_more_bad_text_is_blocked_before_any_request[…]         # 9 ca, Phát hiện số 1
16 failed, 2912 passed, 2 skipped, 8 xfailed in 1808.28s (0:30:08)

$ uv run pytest "tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted"   # chạy riêng, 2 lần
1 passed in 9.48s
1 passed in 9.89s

$ python -c "from seo_app.onpage.meta import normalize_meta; print(repr(normalize_meta('Cửa\x00sắt')))"
'Cửasắt'

$ pytest tests/test_wordpress_seo_meta_t042.py tests/test_soi_loi_t042.py -k bad_text_is_blocked_before_any_request
    # bản sao git archive 94ba458^ (trước Thợ Máy phần 1)
102 passed, 286 deselected in 2.78s
    # bản sao git archive 94ba458
15 failed, 87 passed, 286 deselected in 3.29s

$ uv run ruff check .
All checks passed!

PS> $env:PYTHONUTF8="1"; uvx detect-secrets scan app/views/write.py seo_app/demo.py tests/test_t041_seo_ui.py `
      docs/team/reports/T-041-hoa-si.md moi-tieng-viet.py      # file mồi tiếng Việt có khóa giả, xóa ngay sau khi quét
moi-tieng-viet.py: AWS Access Key, Base64 High Entropy String, Secret Keyword, Secret Keyword
files with results: 1                                          # chỉ file mồi: máy quét đọc được file tiếng Việt, 4 file thật sạch
```

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/write.py` | Bước SEO thật: `published_listing`, `site_store`, `brand_suffix`, các bản meta (`meta_versions`, `set_meta_versions`, `add_meta_versions`, `meta_edited`, `meta_step`, `suggest_meta`), `check_lines`, `meta_field`, `slug_field`, `site_host`, `final_seo`, `siteseo_panel`, `links_panel`, `faq_panel`, `step_seo`; nháp `seo_snapshot`/`restore_seo`; bước 5 `seo_request`, `seo_check`, `seo_toggle`, `write_seo` (chỗ nối: xem quyết định số 6). Bỏ `count_badge`, `step_seo` demo, khóa demo |
| `seo_app/demo.py` | Xóa `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` |
| `tests/test_t041_seo_ui.py` (mới) | 23 test giao diện (bảng trên) |
| `docs/team/reports/T-041-hoa-si.md` | Báo cáo này |

## Lượt 2 (2026-10-27)

Sau lượt 3 của Thợ Máy (sửa lỗi lùi ở «Phát hiện» số 1: chữ SEO có ký tự điều khiển, ký tự lạ nay bị **Chặn** kèm câu nhắc ở mọi đường; câu schema mới `MSG_NO_FAQ_QUESTION`). Chỉ Huy mở thêm phạm vi `app/views/wordpress.py` cho «Phát hiện» số 3.

### Tóm tắt (cho chủ dự án)

- Trang **Kết nối WordPress**: bấm «Kiểm tra kết nối» xong có thêm dòng «SiteSEO: ghi được», «SiteSEO: chưa bật (bật Abilities trong SiteSEO…)» hay «SiteSEO: chưa dò được…», để biết công tắc «Ghi SEO lên website» có dùng được không.
- Bước **SEO**: dán vào ô meta title/description chữ có ký tự điều khiển vô hình (thường lẫn vào khi chép từ nơi khác) thì ô hiện nhãn đỏ «Chặn» kèm câu «… Xóa ô rồi gõ lại chữ thường.»; khung «Chép sang SiteSEO» không cho chép ô đó; bước Xuất bản báo «chưa dùng được», bật «Ghi SEO lên website» thì báo trước và không ghi ô đó lên website. Không có lỗi đỏ.
- Bài có mục «Câu hỏi thường gặp» mà chưa có câu hỏi đúng dạng: phần Schema nói rõ cách viết câu hỏi (trước đó báo nhầm «chưa có mục Hỏi đáp»).
- Câu dưới «Liên kết nội bộ» khi nút «AI gợi ý liên kết» đang mờ nay nói đúng lý do (AI chưa dùng được, hay chưa có danh sách bài đã đăng) thay vì mời bấm nút.

### Yêu cầu → cách làm → test

Test ở `tests/test_t041_seo_ui.py` (thêm 9, tổng 32).

| # | Yêu cầu (tin nhắn Chỉ Huy B) | Cách làm | Test |
|---|---|---|---|
| 1 | Trang Kết nối WordPress hiện `info.siteseo_status`, thoát Markdown | `app/views/wordpress.py`: dòng thứ ba trong danh sách quyền: `f"- {plain(info.siteseo_status)}"` (`plain` = `escape_markdown`, như các dòng khác của trang) | `test_wordpress_page_shows_siteseo_status[True/False/None]` |
| 2a | Dán chữ có ký tự điều khiển: nhãn Chặn, câu nhắc rõ | Không đổi code giao diện: ô sửa → `DraftMetaVersions` (lượt 3 giữ ký tự lạ) → `check_title`/`check_description` Chặn → `check_lines` (huy hiệu đỏ, câu qua `escape_markdown`). Ô và nháp giữ đúng chữ đã dán | `test_pasted_control_chars_are_blocked_not_copied` |
| 2b | Nút chép và công tắc ghi xử lý đúng trường bị chặn: không lỗi đỏ, không ghi | `final_seo` (lượt 1) nhận `None` từ `siteseo_copy` → khung chép «chưa chép được» + câu nhắc; `seo_check` «chưa dùng được»; `seo_request` bỏ trường đó, `seo_toggle` báo trước, câu kết quả nói «Không ghi …» | `test_pasted_control_chars_are_blocked_not_copied`, `test_blocked_control_chars_are_not_written` (lệnh ghi chỉ có từ khóa chính; không request nào mang ký tự lạ, thô hay dạng `\u001b`; không `st.error`, không lỗi trang) |
| 2c | Câu schema mới hiện đúng | Không đổi code: `faq_panel` hiện `issues` qua `escape_markdown` | `test_faq_section_without_proper_questions_says_so` (có `MSG_NO_FAQ_QUESTION`, không còn `MSG_NO_FAQ`, không JSON-LD, không ô «Dùng schema») |
| 3 | Câu liên kết nội bộ khi chưa có khóa AI khớp nút mờ | `links_panel`: chưa có liên kết thì: AI chưa dùng được → «Nút … đang tắt vì AI chưa dùng được (xem cảnh báo ở đầu trang)»; chưa có danh sách bài → «Nút … cần danh sách bài đã đăng trên website (xem dòng báo ở đầu bước SEO)»; có bài đích → giữ «bấm «AI gợi ý liên kết»»; danh sách có mà không bài nào cùng chủ đề → chỉ câu «Chưa có bài đã đăng nào cùng chủ đề…» như cũ | `test_links_hint_without_ai_key`, `test_links_hint_without_wordpress`, `test_links_hint_when_button_works` |
| 4 | Không sửa `seo_app/**` | Không sửa | — |

### Ghi chú

- Từ khóa chính (gõ ở bước Chuẩn bị, không qua bộ kiểm meta) có ký tự điều khiển thì client từ chối **cả** lệnh ghi SEO bằng câu cố định «Từ khóa chính có ký tự điều khiển. Gõ lại chữ thường.» (hiện chữ thường, không ghi gì, bài nháp vẫn tạo bình thường). Giữ như vậy (an toàn, hiếm gặp); nếu muốn vẫn ghi tiêu đề, mô tả khi chỉ từ khóa hỏng thì `seo_request` bỏ riêng từ khóa (`seo_write_problem`), làm ở phiếu sau.
- Không mở app thật lượt này: thay đổi giao diện chỉ là một dòng chữ trên trang WordPress và câu chú thích; đường chữ bị Chặn đi đúng các hàm đã thử trên trình duyệt ở lượt 1 (khung chép, công tắc, gửi nháp).

### Bằng chứng lượt 2

Windows 11, Git Bash, worktree `wt-T-041`.

```
$ uv run pytest tests/test_t041_seo_ui.py
32 passed

$ uv run pytest tests/test_t041_seo_ui.py tests/test_app_images.py tests/test_app_t044_safe_text.py \
    tests/test_app_wordpress.py tests/test_app_pages.py tests/test_t041_drafts_seo.py \
    tests/test_t041_links_ai.py tests/test_t041_meta.py tests/test_t041_schema.py \
    tests/test_t041_site_index.py tests/test_soi_loi_t041.py        # code cdc47d0
497 passed in 578.93s (0:09:38)

$ uv run ruff check .
All checks passed!
```

Thử gỡ chỗ làm (bản sao `git archive`, như lượt 1): L2-M1 bỏ dòng trạng thái SiteSEO → bắt được (3 test); L2-M2 dòng trạng thái không thoát Markdown → bắt được (3 test); L2-M3 câu liên kết luôn mời bấm dù nút mờ → bắt được.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `app/views/wordpress.py` | Dòng «SiteSEO: …» (`info.siteseo_status`, đã thoát Markdown) |
| `app/views/write.py` | `links_panel`: câu khi chưa có liên kết theo lý do nút mờ |
| `tests/test_t041_seo_ui.py` | 9 test mới (bảng trên) |
| `docs/team/reports/T-041-hoa-si.md` | Mục này |

## Lượt 3 (2026-10-27)

Sau Soi Lỗi lượt 2 (cả phiếu ĐẠT CÓ ĐIỀU KIỆN, `f21bc3a`): sửa SL-T041-9, -10, -11 (Thấp). **SL-T041-8** (emoji Unicode 16 bị Chặn nhầm) **chưa làm**: chờ Lá Chắn quyết hướng sửa.

### Tóm tắt (cho chủ dự án)

- **Từ khóa chính** có ký tự lạ (thường lẫn vào khi dán), có chữ website không nhận (ví dụ «<2m»), hay dài quá 200 ký tự:
  - bước SEO có dòng «Từ khóa chính» nhãn đỏ «Chặn», kèm câu nhắc sửa ở bước 1 · Chuẩn bị;
  - bước Xuất bản báo «SEO: Từ khóa chính chưa dùng được»; bật «Ghi SEO lên website» thì báo trước «Sẽ không ghi Từ khóa chính»;
  - khi gửi, phần mềm vẫn ghi tiêu đề, mô tả hợp lệ, chỉ bỏ riêng từ khóa (trước đây: mất luôn cả tiêu đề, mô tả, hoặc lặng lẽ bỏ ký tự rồi ghi).
- Bước **Xuất bản**: mở lại bài ở bước này rồi bật «Ghi SEO lên website», dòng kiểm SEO và câu báo của công tắc nay luôn nói cùng một điều.
- Tiêu đề, mô tả có chữ website không nhận (`[gallery]`, «<2m», «&#37»): nhãn dưới ô nay đỏ «Chặn» kèm đúng lý do như khung chép (trước đây xanh «Nên»).

### Lỗi → cách sửa → test

Chỉ sửa `app/views/write.py`, dùng các hàm kiểm có sẵn của Thợ Máy; không sửa `seo_app/**`. Test mới ở `tests/test_t041_seo_ui.py` (thêm 7, tổng 39); `SL:` là `tests/test_soi_loi_t041.py`.

| Mã | Cách sửa | Test |
|---|---|---|
| SL-T041-9 | `keyword_problem()`: từ khóa (gõ ở bước Chuẩn bị) kiểm như client sẽ kiểm: `has_odd_chars` (cả ký tự riêng, chưa gán mà client lặng lẽ bỏ), `seo_write_problem` (câu cố định của client), giới hạn `MAX_SEO_KEYWORD_CHARS` của client (nhập hằng); trống cũng báo. `final_seo` thêm trường «Từ khóa chính» (chữ đã chuẩn hóa hay `None` + lý do), nên `seo_request` bỏ riêng từ khóa hỏng khỏi lệnh ghi (vào `skipped`, câu báo trước và câu kết quả nêu tên), `seo_check` nêu «Từ khóa chính chưa dùng được». `keyword_line()` ở cột trái bước SEO: nhãn «Chặn» + câu nhắc (chữ thuần), chỉ hiện khi hỏng | `test_bad_keyword_is_flagged_on_seo_and_publish_steps[ESC/U+E000/nho-hon-so/qua-dai]`, `test_bad_keyword_does_not_lose_title_and_description`; `SL: test_sl_t041_9_bad_keyword_is_skipped_alone[ESC/U+E000]`, `SL: test_sl_t041_9_bad_keyword_is_warned_before_sending` (gỡ `xfail`) |
| SL-T041-10 | `seo_check()`: công tắc bật thì `published_listing()` (cùng danh sách trong phiên mà `seo_request` dùng) **trước** khi vẽ dòng kiểm; công tắc tắt thì vẫn không tải (chỉ xem bước Xuất bản không gọi website) | `test_publish_step_loads_listing_only_when_toggle_is_on`; `SL: test_sl_t041_10_publish_checklist_agrees_with_seo_toggle` (gỡ `xfail`) |
| SL-T041-11 | `meta_field`: nhãn dưới ô lấy `siteseo_copy(...).checks[0/1]` (kết quả kiểm đã nâng lên Chặn khi client từ chối ghi, đúng kết quả khung chép dùng) thay cho `check_title`/`check_description` trần | `test_description_badge_matches_copy_box` (ô mô tả); `SL: test_sl_t041_11_field_badge_is_red_when_copy_is_refused[shortcode/nho-hon-so/ma-ky-tu]` (gỡ `xfail`) |

Gỡ `xfail` (chỉ xóa dấu): 4 dấu, 7 ca trong `tests/test_soi_loi_t041.py`; `git diff f21bc3a..a735c7e -- tests/test_soi_loi_t041.py` là 23 dòng xóa, 0 dòng thêm. Trước khi gỡ, cả 7 ca báo `XPASS(strict)`. Ca `xfail` còn lại duy nhất: SL-T041-8.

### Quyết định

1. **Không thêm khung chép «Từ khóa chính»** (đã thử rồi bỏ): test của Soi Lỗi `test_absurd_hand_edited_seo_block_keeps_page_working` đòi không còn khung chép nào khi cả ba ô bị Chặn, và bố cục đã duyệt có ba khung. Từ khóa hỏng có nhãn riêng ở cột trái; từ khóa đúng thì đã hiện ở đầu trang.
2. **Giữ nguyên chữ «✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng»** dù nay kiểm cả từ khóa (hỏng thì dòng ⚠️ nêu tên): đổi chữ thì `SL: test_sl_t041_10_…` qua oan (không bao giờ thấy chữ cũ).
3. Dòng kiểm ở bước 5 khi công tắc bật có thể gọi website (tải danh sách bài) như lệnh ghi; website lỗi thì `site_listing` trả câu báo, không ném lỗi (như bước SEO).

### Bằng chứng lượt 3

Windows 11, Git Bash, worktree `wt-T-041` (Lá Chắn đang kiểm song song cùng thư mục: `tests/test_la_chan_t041.py` của Lá Chắn chưa commit, tôi không chạy, không commit).

```
$ uv run pytest tests/test_soi_loi_t041.py tests/test_t041_seo_ui.py      # a735c7e trước khi thêm 7 test của tôi
174 passed, 1 xfailed                                                         # xfailed: SL-T041-8

$ uv run pytest tests/test_app_images.py tests/test_app_pages.py tests/test_app_t044_safe_text.py \
    tests/test_app_wordpress.py tests/test_soi_loi_t041.py tests/test_t041_drafts_seo.py \
    tests/test_t041_links_ai.py tests/test_t041_meta.py tests/test_t041_schema.py \
    tests/test_t041_seo_ui.py tests/test_t041_site_index.py                  # code a735c7e
535 passed, 1 xfailed in 608.02s (0:10:08)                                    # xfailed: SL-T041-8

$ uv run ruff check .
All checks passed!
```

Thử gỡ chỗ sửa (bản sao `git archive` của `a735c7e`, script `T-041-hoa-si-scripts/mutate_l3.py`):

| Đột biến | Kết quả |
|---|---|
| L3-M1 gửi thẳng từ khóa chính chưa kiểm (như trước SL-T041-9) | bắt được (3 test) |
| L3-M2 bước SEO không hiện nhãn từ khóa hỏng | bắt được (4 test) |
| L3-M3 bỏ kiểm ký tự riêng / chưa gán của từ khóa | bắt được (3 test) |
| L3-M4 bỏ giới hạn độ dài từ khóa của client | bắt được |
| L3-M5 dòng kiểm bước 5 không tải danh sách khi công tắc bật (như trước SL-T041-10) | bắt được (2 test) |
| L3-M6 dòng kiểm bước 5 luôn tải danh sách (chỉ xem cũng gọi website) | bắt được |
| L3-M7 nhãn ô tiêu đề dùng kiểm trần (như trước SL-T041-11) | bắt được (3 test) |
| L3-M8 nhãn ô mô tả dùng kiểm trần | bắt được |

### Đã thay đổi (lượt 3)

| File | Thay đổi |
|---|---|
| `app/views/write.py` | `keyword_problem`, `keyword_line`; `final_seo` thêm trường từ khóa; `siteseo_panel` chỉ chép ba trường; `seo_request` bỏ riêng từ khóa hỏng; `seo_check` tải danh sách khi công tắc bật; `meta_field` dùng kết quả kiểm của khung chép |
| `tests/test_soi_loi_t041.py` | Gỡ 4 dấu `xfail` (SL-T041-9 → -11), không đổi thân test |
| `tests/test_t041_seo_ui.py` | 7 test mới (bảng trên) |
| `docs/team/reports/T-041-hoa-si.md` | Mục này |

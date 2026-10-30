# Báo cáo T-102 · Bước Xuất bản thật: màn hình xác nhận, hẹn giờ, đăng ngay (công tắc mặc định tắt)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-102](../tickets/T-102-buoc-xuat-ban-that.md) |
| Ngày nộp | 2026-10-30 |
| Nhánh | `team/T-102` (từ `c8986da`: `main` `fd28bbc` + T-099 lượt 2). Không gộp `main` |
| Kết quả | Xong yêu cầu 1–3 của phiếu: cả ba hình thức gửi bằng gói của bộ dựng T-096, màn hình xác nhận có mã băm, Hẹn giờ và Đăng ngay qua `release_draft` (công tắc **mặc định tắt**), khóa khi không rõ kết quả, mở Soạn bài từ dòng kế hoạch và ghi trạng thái dòng sau khi gửi. 43 ca test mới; 4 test cũ sửa theo R5 Chỉ Huy duyệt (mục 6). **Khi gộp:** 2 test của T-101 sẽ lệch (mục 7) |

## 1. Tóm tắt (cho chủ dự án)

- Bước **5 · Xuất bản** của trang Soạn bài nay gửi đúng bài bạn thấy trên màn hình:
  - Bài nháp giữ định dạng (chữ đậm, danh sách), có link nội bộ đã chọn ở bước SEO, đường dẫn (slug), chuyên mục thật của website (bấm «🔄 Tải chuyên mục từ website» rồi chọn).
  - Trước nút gửi có khung **«Xem lại link, địa chỉ trong bài»**: bảng mọi link và mọi địa chỉ web còn dạng chữ, cột «Dấu hiệu lạ» và «Tên máy (dạng ASCII)» đứng đầu bảng. Địa chỉ giả dạng tên website (ví dụ chữ «а» Nga thay chữ «a») hiện rõ dạng `xn--…` kèm cảnh báo.
  - Bài vừa sửa sau khi xem (danh sách bài trên website đổi, chữ đổi…) thì phần mềm không gửi, báo xem lại.
- **Hẹn giờ** và **Đăng ngay** đã làm xong nhưng đang **tắt**: chọn hai ô này chỉ thấy câu giải thích, không có nút gửi. Chỉ bật sau lượt thử thật trên website. Khi bật:
  - Hẹn giờ: ngày, giờ điền sẵn (từ kế hoạch, hay ngày mai 08:00), nhãn ghi rõ thứ, ngày, giờ Việt Nam; giờ đã qua, chưa tới 10 phút nữa, xa hơn một năm thì không cho gửi.
  - Màn hình xác nhận đầy đủ (tiêu đề, đường dẫn, chuyên mục, SEO, mọi link, địa chỉ, ảnh và GPS, đoạn dạng shortcode). Phải tick «Tôi đã đọc lại toàn bài và danh sách trên» mới bấm được; sửa gì sau khi tick thì app tự bỏ tick.
  - Đăng ngay ghi rõ «Hiện công khai ngay khi bấm» và bắt buộc bật «Ghi SEO lên website».
  - Lệnh hẹn giờ/đăng là bước **cuối cùng**, sau khi bài nháp, ảnh, SEO đã lên. Không rõ kết quả (mất mạng đúng lúc) thì khóa gửi lại, dặn mở trang quản trị kiểm tra; app không bao giờ tự gửi lại.
- **Viết bài từ kế hoạch** (nút «Viết bài» của trang Kế hoạch, phiếu T-101): app đọc lại đúng dòng trên Google Sheet rồi điền sẵn từ khóa, ghi chú của thợ (số điện thoại, email đã che, có nhắc khi ghi chú nói giá), slug, trang dịch vụ đích (link bắt buộc), loại bài, ngày giờ dự kiến; ghi «Đang viết» vào dòng. Dòng đã có bài đang soạn thì mở lại bài đó, không tạo bài thứ hai.
- Gửi xong, app ghi vào dòng kế hoạch: «Đã gửi nháp» / «Đã hẹn giờ» / «Đã đăng», Mã bài WordPress, ngày đăng. Google lỗi thì bài **không** bị gửi lại; việc ghi Sheet được giữ để thử lại ở trang Kế hoạch.
- Đã thử trên trình duyệt thật với một WordPress giả chạy trên máy (không gửi gì lên suachuacuasat.com).

## 2. Việc đã làm (dòng T-102 của thiết kế T-094 mục 6)

Mọi thay đổi ở `app/views/write.py` (và bỏ `CATEGORIES` ở `seo_app/demo.py`). Không sửa `seo_app/**` khác, `config/**`.

| Thiết kế | Chỗ làm |
|---|---|
| Cả ba hình thức gửi bằng bộ dựng T-096 (định dạng, link nội bộ, slug, chuyên mục thật) | `build_package` (`:2955`) dựng gói từ đúng chữ thô trong phiên (`links=chosen_links()`, `required_ids=required_links()`, `slug`, `categories`, `seo=package_seo()`, `date_gmt`); `send_draft` (`:3265`) dựng lại trên đúng ảnh sắp tải, gửi `package.content_parts(...)` và `title/categories/tags/excerpt/slug` của gói qua `send_and_record` (`:3471`). Đã bỏ `article_parts`/`paragraphs_to_html`. Chuyên mục: `category_picker` (`:2855`, `list_categories` chỉ khi bấm) |
| Màn hình xác nhận (3.5) + băm | `review_panel` (`:3196`) = `review_header` (`:3163`) + `review_notices` (`:3063`) + `review_tables` (`:3079`). Nháp: dạng rút gọn (vẫn đủ bảng link, địa chỉ trần, nhúng). Hẹn giờ/Đăng ngay: thêm ảnh, shortcode, ô tick `confirm_box` (`:3038`) |
| Hẹn giờ (ngày/giờ điền sẵn từ kế hoạch), Đăng ngay qua `release_draft` | `schedule_picker` (`:2818`: `local_to_utc`, `schedule_label`, `check_schedule`), `default_publish_time` (`:2804`), `release_post` (`:3611`, nơi **duy nhất** gọi `release_draft`) |
| Kết quả, khóa khi không rõ | `record_outcome` (`:3667`: `SendState` có `mode`, `scheduled_for`, `released`, `release_unknown`), `apply_send` (`:3729`), `unsure_message` (`:3813`), `sent_message` (`:3834`), `release_result` (`:3932`) |
| Ghi dòng kế hoạch (1.7) | `record_plan` (`:3578`) qua `record_status` của T-100; client Sheets tạo trong lần bấm (`sheets_client`, `:3569`), không giữ trong phiên |
| Mở Soạn bài từ dòng kế hoạch (1.6) | `init_state` (`:355`) đọc và bỏ `_start_plan_key` cùng `_start_keyword`; `start_from_plan` (`:612`), `fill_from_plan` (`:669`), `plan_details` (`:691`); nháp giữ `DraftPlanRef` (`snapshot`, `:531`), mở lại nháp lấy lại phần kế hoạch từ bản lưu trên máy (`plan_details_from_cache`, `:704`). Loại bài, trang đích vào `select_candidates` (`links_panel`, `:2522`); tiêu đề dự kiến chỉ hiện chữ thường ở bước Dàn ý (`:1993`) |
| Xóa `CATEGORIES` khỏi `demo.py` | `seo_app/demo.py`: bỏ khối «bước 5: Xuất bản» (không còn nơi nào dùng) |

## 3. Điều kiện bảo mật → chỗ làm → test

Test ở `tests/test_t102_publish.py` trừ khi ghi khác.

### Chung (LC-T094-1 → -3)

| Mã | Chỗ làm | Test |
|---|---|---|
| LC-T094-1 | WordPress giả (`FakeWordPress`), Google Sheet giả có trạng thái (`FakePlanSheet` trên `FakeGoogle`, nối `SheetsClient` thật), AI giả; bộ chặn mạng vẫn bật | mọi test của file |
| LC-T094-2 | Câu báo là câu cố định của client (`ReleaseError`, `SheetsError`, `SheetPlanError`, T-100 `StatusResult.message`); lỗi lạ quanh lệnh chuyển: `MSG_RELEASE_UNEXPECTED`, không chép lời gốc | `test_release_unsure_locks_and_never_resends`, `test_unexpected_error_around_release_counts_as_maybe_sent`, `test_plan_row_unreadable_opens_keyword_only`, `test_sheet_failure_after_send_keeps_debt_and_never_resends` (mồi trong lời máy chủ không hiện) |
| LC-T094-3 | Chữ trên màn hình xác nhận: ô bảng, `st.text`, `escape_markdown`; `shown_text` (`:2796`) bỏ ký tự điều khiển, đổi hướng, vô hình (`normalize_meta`), cắt dài; không thêm `unsafe_allow_html` nào (vẫn 7 chỗ như `main`) | `test_review_shows_site_and_ai_text_plain`, `test_draft_review_lists_every_link_and_bare_address`, `test_categories_loaded_on_click_and_sent`, `test_planned_title_is_only_a_hint` |

### T-102 (LC-T094-36 → -41)

| Mã | Chỗ làm | Test |
|---|---|---|
| LC-T094-36 | Mọi hình thức gửi `content_parts` của gói; chữ sửa tay cũng qua bộ dựng; bài có link nội bộ (hay link bắt buộc) thì tải lại danh sách bài **ngay trước** khi dựng gói gửi (`package_index(fresh=True)`, `:2903`), trước mọi lệnh ghi; còn dòng Chặn → nút khóa | `test_draft_sends_exactly_the_builder_package`, `test_internal_link_reloads_listing_right_before_sending`, `test_review_flags_odd_hosts_and_sends_no_zero_width` |
| LC-T094-37 | Hẹn giờ/Đăng ngay: đủ phần 3.5 (giờ Việt Nam kèm thứ, «Hiện công khai ngay khi bấm», link, địa chỉ trần, ảnh + GPS, shortcode, SEO, kiểm tra). Nháp: rút gọn nhưng vẫn có bảng mọi link và địa chỉ trần. Ô tick, nút ghi rõ hành động (`send_label`, `:3021`) | `test_schedule_flow_confirms_then_releases_last`, `test_publish_now_needs_seo_written`, `test_draft_review_lists_every_link_and_bare_address`, `test_date_label_has_weekday` |
| LC-T094-38 | Mã băm tính lúc hiện (`S._wp_shown`), ô tick nhớ mã đã xác nhận (`remember_confirm`); mã đổi thì bỏ tick, báo `MSG_CONFIRM_RESET`; lúc bấm dựng lại, so **trước lệnh mạng ghi đầu tiên** (`package.matches`), khác → không gửi. Nháp cũng so (mã của màn hình người dùng vừa xem). `release_draft` chỉ sau tải ảnh, tạo nháp, ảnh đại diện, ghi SEO trong cùng lần bấm | `test_untick_when_schedule_changes_after_confirming`, `test_untick_when_article_image_or_seo_switch_changes` (chữ bài, alt ảnh, công tắc SEO), `test_changed_between_view_and_click_sends_nothing`, `test_schedule_flow_confirms_then_releases_last` (thứ tự), `test_publish_now_with_seo_written` (SEO trước lệnh đăng) |
| LC-T094-39 | «Đang gửi» giữ tới khi biết kết quả `release_draft` (`send_and_record`: `pending = holder["release"] is not None`); không rõ → khóa (`release_unknown`), dặn kiểm trang quản trị, không tự gửi lại. Đăng ngay khi SEO chưa ghi → Chặn; Hẹn giờ → Cảnh báo (của bộ dựng) | `test_release_unsure_locks_and_never_resends`, `test_interrupted_after_release_keeps_result_and_lock`, `test_double_click_releases_once`, `test_two_tabs_only_one_release`, `test_other_tab_sends_while_preparing`, `test_publish_now_needs_seo_written` |
| LC-T094-40 | Chỉ qua `record_status` (4 ô, kiểm xung đột, lưu việc còn nợ trước); lỗi Sheet không làm gửi lại WordPress | `test_draft_send_writes_plan_status_and_post_id` (chỉ các ô Trạng thái, Mã bài WordPress, Cập nhật lúc), `test_schedule_writes_scheduled_with_time`, `test_sheet_failure_after_send_keeps_debt_and_never_resends` |
| LC-T094-41 | Công tắc `RELEASE_SWITCH = "_release_enabled"` (`:290`), mặc định tắt (`release_enabled`, `:2791`): tắt thì Hẹn giờ/Đăng ngay chỉ có câu `MSG_RELEASE_OFF`, không nút gửi, không đường tới `release_draft`. Chưa có nút bật trên giao diện (mục 5, quyết định 1) | `test_switch_off_hides_schedule_and_publish` (2 ca) |

### Lá Chắn T-099 (Điều kiện 2 lượt 1; L2-1 → L2-3)

| Điều kiện | Chỗ làm | Test |
|---|---|---|
| Một `release_draft` mỗi lần bấm, trên chính client vừa tạo nháp; mã bài chỉ lấy từ kết quả tạo nháp của lần bấm này | `release_post` dùng `result["post_id"]` của `create_draft_with_images` trong cùng `send_and_record`; AST test T-099 (`tests/test_wordpress_release.py`) vẫn qua: tên `release_draft` chỉ ở một hàm | `test_schedule_flow_confirms_then_releases_last`, `test_double_click_releases_once`, `test_two_tabs_only_one_release` |
| L2-1: lệnh **cuối cùng** trên client, nối tiếp sau ảnh đại diện, ghi SEO | `send_and_record`: `create_draft_with_images` → `record_outcome` → `write_seo` → `release_post`; ghi Sheet sau đó dùng client Google riêng | `test_schedule_flow_confirms_then_releases_last` (hai lệnh cuối: hỏi còn nháp, rồi chuyển), `test_publish_now_with_seo_written` (`["seo", "release"]`), `test_send_uses_a_fresh_client_made_in_the_click` |
| L2-2: tạo client ngay trong lần bấm; không giữ trong `st.session_state`, `st.cache_resource`, `st.cache_data`, biến toàn cục; không `deepcopy`, `pickle` | `publish_panel` tạo client **mới** trong nhánh `if clicked and allowed` (`:4066`), không dùng client đã hỏi quyền đăng bài, chuyên mục lúc vẽ; số `st.cache_resource` không đổi so với `main` (5, đều là kho, thư viện ảnh) | `test_send_uses_a_fresh_client_made_in_the_click` (client tạo nháp **là** client hẹn giờ, **khác** client lúc vẽ) |
| Ghi kết quả trước lệnh `st.*` kế tiếp | `release_post` → `record_outcome` ngay trong `send_and_record` (không `st.*`, không đọc phiên) | `test_interrupted_after_release_keeps_result_and_lock` |
| L2-3: `unsure`, `went_public`, `Exception` khác `ReleaseError` → «có thể đã gửi»: khóa, dặn kiểm trang quản trị, câu cố định | `release_post` (`:3611`); `went_public` ghi đúng là đã đăng; hiện `str(err)` của `ReleaseError` bằng chữ thường | `test_release_unsure_locks_and_never_resends`, `test_schedule_that_went_public_is_urgent`, `test_unexpected_error_around_release_counts_as_maybe_sent`, `test_release_refused_keeps_draft` |
| `when_utc` từ `local_to_utc`, cùng giá trị cho mã băm | `schedule_picker` trả `when`; `PublishOrder.when_utc` dùng cho `date_gmt` của gói (mã băm) và `release_draft` | `test_schedule_flow_confirms_then_releases_last` (`date_gmt` = `date_gmt_text(when)`) |

### Lá Chắn T-100 (mục 5, LC-T100-3, SL-T100-4) và T-103 (điều kiện 2)

| Điều kiện | Chỗ làm | Test |
|---|---|---|
| T-100: `find_plan_draft` với mã băm Sheet **đang dùng** | `start_from_plan` (`sheet_hash(settings.google_sheet_id)`) | `test_write_from_plan_reopens_its_draft_without_reading_sheet`, `test_draft_of_another_sheet_is_not_reused` |
| T-100: `record_status(…, sheet_id=settings.google_sheet_id)` (LC-T100-3, SL-T100-4 đã sửa ở lõi) | `start_from_plan`, `record_plan` | `test_draft_from_another_sheet_is_blocked_and_kept` |
| T-100: `BLOCKED` hiện câu báo, giữ việc còn nợ; thử lại chỉ ghi Sheet | `record_plan` hiện `StatusResult.message`; không bao giờ gửi lại WordPress (thử lại ở trang Kế hoạch, T-101) | `test_draft_from_another_sheet_is_blocked_and_kept`, `test_sheet_failure_after_send_keeps_debt_and_never_resends` |
| LC-T094-29, -35: đọc lại Sheet trước khi mở Soạn bài; «Viết bài» không gửi gì lên WordPress | `open_row` mỗi lần; trang dịch vụ đích chỉ đổi thành mã bài từ **danh sách bài lưu trên máy** (`cached_site_index`, `:722`), không gọi website | `test_write_from_plan_rereads_row_fills_compose_and_marks_writing` (`site.fake.requests == []`) |
| T-103 2a: chữ kế hoạch vào lời dặn AI chỉ qua `_block` / `_keyword` | Từ khóa → ô từ khóa (`_keyword`); ghi chú → «Kinh nghiệm của xưởng» (`_material` → `_block`); tiêu đề dự kiến chỉ hiện, không gửi AI; từ khóa phụ không dùng | `test_planned_title_is_only_a_hint` |
| T-103 2b: ghi chú qua `personal_info` / `mask_personal_info`, nhắc giá | `fill_from_plan` (`:669`): che bằng `[đã ẩn]`, câu `MSG_PLAN_MASKED`; `mentions_price` → `MSG_PLAN_PRICE` | `test_write_from_plan_rereads_row_fills_compose_and_marks_writing` |
| T-103 2c: `[plan].default_time` qua `parse_plan_time`, sai thì 08:00; không đọc nhãn từ cấu hình | `default_publish_time` (`:2804`) | `test_default_time_from_plan_config` (3 ca: «19:30», «25:00», mảng) |

### Bảng «Việc bắt buộc Giai đoạn 5» (thiết kế T-094 mục 7, các dòng giao T-102)

| Dòng | Test |
|---|---|
| 2 (mọi hình thức đi qua bộ dựng) | `test_draft_sends_exactly_the_builder_package` |
| 3, 11 (liệt kê mọi `href`, địa chỉ lạ, «@», tên máy `xn--…`) | `test_review_flags_odd_hosts_and_sends_no_zero_width` (hai địa chỉ Kirin của thiết kế: «а» trong tên, «о» ở đuôi `.cоm`; và `@evil.example`), `test_draft_review_lists_every_link_and_bare_address` |
| 4 (một đường tới `publish`/`future`, có xác nhận) | `test_schedule_flow_confirms_then_releases_last`, `test_untick_when_*`, `test_switch_off_hides_schedule_and_publish` |
| 7 (gỡ U+200B trước khi gửi) | `test_review_flags_odd_hosts_and_sends_no_zero_width` (HTML gửi đi không còn U+200B) |
| 8, 13 (chữ đã gỡ không vào `st.markdown`; U1 cho câu link) | `test_review_shows_site_and_ai_text_plain` |
| 9 (tải lại danh sách bài, Chặn khóa nút) | `test_internal_link_reloads_listing_right_before_sending` |

## 4. Test

- `tests/test_t102_publish.py`: **43 ca** (38 hàm), qua hết.
- 17 file luồng gửi, trang app, `test_wordpress_release.py` trên code cuối (test cũ chưa sửa): **772 qua**, 4 hỏng, đúng 4 test cũ ghim hành vi trước T-102 (mục 6).
- Sau khi sửa 4 test đó theo R5: chạy lại đủ 5 file (`test_app_images`, `test_content_edge_cases`, `test_la_chan_t089`, `test_soi_loi_t041`, `test_t102_publish`): **278 qua, 0 hỏng**.
- 18 file khác có đụng trang Soạn bài (`test_config_tolerance`, `test_soi_loi_round3/4/5`, `test_ui_escape`, `test_t041_links_ai`…): **2.402 qua**, 6 bỏ qua, 5 `xfail` (không có XPASS).
- `uv run ruff check .`, `ruff format --check`: sạch.
- `detect-secrets` (Git Bash, `PYTHONUTF8=1`, đường dẫn tương đối, file mồi tiếng Việt đặt trong thư mục quét: mồi bị bắt): file mới, file sửa không có bí mật. Một dòng «Basic Auth Credentials» ở docstring `site_host` (địa chỉ mẫu có tên và mật khẩu trước dấu «@») có từ T-041, là chữ mẫu. Mã Sheet giả thứ hai trong test viết dạng ghép chuỗi để không thành «chuỗi ngẫu nhiên». Quét cả 4 file test cũ đã sửa: chỉ còn hằng mật khẩu thử có sẵn từ trước ở đầu `test_content_edge_cases.py` (không do T-102).
- Trình duyệt thật: app nhánh này với WordPress giả trên máy (cấu hình tạm `seo-app-t102-hoasi`, đã trả `launch.json` đúng SHA-256 `a5607e8c…f169`, đã xóa `data/` thử): Nháp gửi được (danh sách bài tải lại ngay trước khi tạo nháp), khóa «đã gửi»; Hẹn giờ hiện câu «đang tắt». Lần thử này tìm ra bảng địa chỉ trong khung hẹp chỉ hiện cột «Địa chỉ» (địa chỉ chữ Kirin trông y hệt tên website): đã đưa cột «Dấu hiệu lạ», «Tên máy (dạng ASCII)» lên đầu, giới hạn độ rộng cột, nới khung gửi (`st.columns([2, 3])`).

## 5. Quyết định cần Chỉ Huy biết

1. **Công tắc LC-T094-41** là khóa phiên `_release_enabled`, mặc định tắt, chưa có nút trên giao diện: nút bật nằm ở trang Cài đặt (ngoài phạm vi phiếu này). Đề nghị phiếu sau, sau lượt thử thật LC-T094-44: thêm công tắc ở Cài đặt (như ghi SEO), Lá Chắn xét cách lưu.
2. **Không gọi website khi chỉ xem**: danh sách bài chỉ tải lại lúc bấm gửi và chỉ khi bài có link; chuyên mục tải khi bấm; quyền đăng bài và múi giờ chỉ hỏi ở Hẹn giờ/Đăng ngay, mỗi phiên một lần (nút «Kiểm tra lại»). Giữ được các test T-086 «chưa gọi website».
3. **Ảnh đại diện đặt ở hai chỗ**: bộ dựng kiểm ảnh đại diện theo từng chỗ nên chỗ có ảnh đại diện dùng đối tượng riêng; sau khi `content_parts` kiểm xong, `shared_uploads` (`:3433`) gộp lại đúng ảnh đó (cùng băm, alt, chú thích, thẻ, GPS) nên vẫn chỉ tải một lần (Soi Lỗi T-054 G10).
4. **Nháp cũng so mã băm** của màn hình vừa xem (không cần tick): bài đổi giữa lúc xem và lúc bấm thì không gửi.
5. **Sau khi ghi trạng thái dòng kế hoạch thành công**, `DraftPlanRef` của nháp nhận trạng thái và Mã bài WordPress vừa ghi: lần gửi lại có xác nhận (bài mới) không bị báo nhầm «dòng vừa bị sửa ở nơi khác».
6. **Trang dịch vụ đích** chỉ đổi được thành mã bài khi máy đã có danh sách bài lưu (LC-T094-35 cấm gọi WordPress lúc bấm «Viết bài»). Chưa có thì câu nhắc `MSG_PLAN_NO_LISTING`: mở bước SEO một lần rồi mở lại bài.
7. **Slug sai dạng là dòng Chặn** của bộ dựng nên khóa cả «Gửi nháp» (trước T-102 slug không được gửi). Câu báo nói rõ dạng đúng.

## 6. Test cũ đã sửa (R5: Chỉ Huy B duyệt 30/10 18:45, kèm điều kiện)

| Test | Cũ | Mới (đáp ứng điều kiện duyệt) |
|---|---|---|
| `tests/test_app_images.py::test_send_draft_with_real_image` | Ghim mảnh HTML của `paragraphs_to_html` (tiêu đề phần là mảnh riêng `'<h2>…</h2>'`) | So với khối của bộ dựng T-096 (`'<h2>…</h2>
<p>…</p>'`, LC-T094-36). Giữ mọi kiểm ảnh cũ (thẻ `ImageTags`, alt, chú thích, tên file, WebP còn GPS, alt trên Media, bài nháp) và thêm: ảnh ngay sau khối của phần mình, `<figure>` có alt và `<figcaption>` đã làm sạch, `srcset` chỉ file đầy đủ `… 1x` (T-059), «[» «]» trong bài thành `&#91;` `&#93;` (T-061, thêm «[gallery]» vào đoạn mở bài để kiểm), không còn `{{`/`}}` |
| `tests/test_content_edge_cases.py::test_publish_now_requires_confirmation` | Ghim nút demo «📤 Gửi sang WordPress» và ô xác nhận demo của Đăng ngay | Công tắc tắt: Hẹn giờ, Đăng ngay không có nút gửi nào, có câu «đang **tắt**». Ý «đăng ngay cần xác nhận» giữ ở `test_t102_publish.py`: `test_publish_now_with_seo_written` (thêm: chưa tick thì nút khóa, chưa lệnh nào), `test_schedule_flow_confirms_then_releases_last`, `test_untick_when_*` (mã băm), `test_switch_off_hides_schedule_and_publish` (không đường tới `release_draft` khi tắt) |
| `tests/test_la_chan_t089.py::test_lc_t089_1_confirmed_send_elsewhere_creating_nothing_keeps_this_post` | Gọi `send_and_record` với chữ tiêu đề; client giả `create_draft_with_images(self, title, parts)` | Truyền gói `build_article(…)` và `package.sections`; client giả nhận `**fields` nhưng **ghi lại** từng lệnh và test kiểm đúng tiêu đề, khối, `{"categories": (), "tags": (), "excerpt": …, "slug": ""}`. Mọi kiểm «đang gửi», khóa gửi trùng giữ nguyên |
| `tests/test_soi_loi_t041.py::test_absurd_hand_edited_seo_block_keeps_page_working` | Gửi nháp được dù slug sửa tay «Cửa Sắt/../../etc» | Kiểm «Gửi nháp» khóa và câu slug của bộ dựng; xóa slug ở bước SEO, bật «Ghi SEO» rồi gửi; giữ các kiểm còn lại (chỉ từ khóa chính được ghi, «424242», `<script`, «gallery» không đi) |

## 7. Việc khi gộp và phiếu sau

- **T-101 (chưa gộp):** `test_write_button_opens_compose_without_wordpress` và `test_start_from_plan_row_opens_compose_without_wordpress` kiểm `_start_plan_key` còn nằm trong phiên và Sheet không có lệnh ghi. Hợp đồng ghi đó là trạng thái **trước khi T-102 xong**; với T-102, Soạn bài bỏ khóa này và ghi «Đang viết» (thiết kế 1.6 bước 4, câu hỏi 4A), Sheet được đọc 3 lần (T-101 một, T-102 hai). Gộp hai nhánh thì sửa hai test đó.
- **`config/content.toml`:** chú thích mục `[plan]` còn ghi «phần mềm chưa dùng mục này… T-102 sẽ đọc»; nay đã đọc `default_time`. Cần người được sửa `config/**` cập nhật chú thích.
- **README** «Hẹn giờ và Đăng ngay» (phiếu Thư Ký theo thiết kế), công tắc Cài đặt (quyết định 1).

## 8. Commit

- `7c5efb2` T-102: bước Xuất bản thật (Nháp, Hẹn giờ, Đăng ngay) và nối dòng kế hoạch: phần chính, kể cả gộp ảnh đại diện (`shared_uploads`), trang dịch vụ đích từ danh sách bài lưu trên máy, bỏ `CATEGORIES`.
- `4419428` client mới trong lần bấm (L2-2), bảng xác nhận (cột cờ lên đầu, độ rộng cột, khung gửi rộng hơn), thêm test (lời commit này nhắc lại cả gộp ảnh đại diện và trang dịch vụ đích, thật ra hai phần đó đã nằm ở `7c5efb2`).
- `afc3afd` địa chỉ bài sau khi hẹn giờ/đăng hiện qua `shown_text`; thêm ca địa chỉ Kirin ở đuôi tên miền; sửa docstring.
- `c9221f3` sửa 4 test cũ theo R5 (mục 6); thêm kiểm «Đăng ngay chưa tick thì nút khóa».
- Commit cuối: báo cáo này.

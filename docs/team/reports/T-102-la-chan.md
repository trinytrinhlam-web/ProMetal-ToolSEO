# Biên bản bảo mật T-102 · Bước Xuất bản thật: màn hình xác nhận, hẹn giờ, đăng ngay · đầy đủ

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | T-102 (phiếu ở checkout chính; Họa Sĩ `7c5efb2` → `5c37be0`, Soi Lỗi `7dec772`) |
| Phạm vi | **Đầy đủ.** Diff `944160c..7dec772` (gốc chung với `main` là đầu T-101): `app/views/write.py` (+1.190: bước Xuất bản, mở bài từ dòng kế hoạch), `app/views/home.py`, `app/views/plan.py` (G1, LC-T101-1), `seo_app/demo.py`; test mới `test_t102_publish.py` (41 hàm), `test_t102_formula_cells.py`, `test_soi_loi_t102.py`; R5: 4 test cũ, 2 test T-101, `test_la_chan_t101.py`. Đọc thêm: `seo_app/content/prompts.py` (`_keyword`, `_block`, `_material`), `seo_app/plan/model.py` (`PlanRow`), client WordPress (`release_draft`, `create_draft_with_images`). Điều kiện: LC-T094-1 → -3, -36 → -41 ([T-094](T-094-la-chan.md)); điều kiện cho T-102 ở biên bản T-096, T-099, T-100, T-101, T-103; mục «Việc bắt buộc khi làm Giai đoạn 5» của `board.md`; đóng LC-T101-1. Gộp thử `origin/main` `a416e74` |
| Ngày | 2026-10-30 (Chỉ Huy giao 23:05; làm 23:13 → 23:50 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay khi công tắc Hẹn giờ/Đăng ngay tắt** (như hiện tại): công tắc tắt thì **không có đường nào** tới `future`/`publish`. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T102-1 của Soi Lỗi, giữ mức), **1 Thấp mới** (**LC-T102-1**: Đăng ngay mà đặt ảnh đại diện hỏng vẫn đăng). Hai lỗi chỉ gặp khi bật công tắc; **phải sửa trước khi bật** (danh sách ở mục «Trước khi bật công tắc»). **LC-T101-1 đóng.** Lỗi mới có test `xfail(strict=True)` trong `tests/test_la_chan_t102.py`. Không sửa code ứng dụng |

## Tóm tắt (cho chủ dự án)

- Bước **5 · Xuất bản** an toàn để đưa vào dùng **ở dạng Nháp**: bài gửi đi đúng là bài bạn thấy trên màn hình xác nhận (cả link, địa chỉ, ảnh), không còn đường nào ghép chữ chưa lọc. Hẹn giờ và Đăng ngay **đang tắt**, tôi đã thử mọi cách bật «gần đúng»: không có nút gửi, không lệnh nào tới website.
- Khi bật thử trong test: phải tick «Tôi đã đọc lại…» mới gửi được; sửa bất kỳ thứ gì sau khi tick thì app tự bỏ tick; giờ đã qua, quá gần, đồng hồ lệch thì không hẹn giờ; mất mạng đúng lúc thì khóa, không tự gửi lại; hai cửa sổ cùng bấm chỉ ra một lệnh.
- Viết bài từ dòng kế hoạch: app đọc lại dòng trên Google Sheet, che số điện thoại, email trong ghi chú, nhắc khi ghi chú nói giá; chữ kế hoạch tới AI đều nằm trong «khung dữ liệu» (AI không coi là lệnh).
- **2 điểm phải sửa trước khi bật Hẹn giờ/Đăng ngay:** chọn «Đăng ngay» mà lúc gửi (1) ghi SEO lên website bị lỗi, hay (2) đặt ảnh đại diện bị lỗi, thì app **vẫn đăng bài công khai**, thiếu phần đó. Bài đúng là bạn muốn đăng, nhưng lên khác bản bạn đã xác nhận. Nên sửa để app giữ bài ở dạng nháp và báo rõ.
- **Việc của bạn:** không có lúc này. Trước khi bật công tắc sẽ có một buổi thử thật cùng bạn (danh sách ở cuối).

## Lỗi phát hiện

Số dòng theo `7dec772`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T102-1 | Thấp | **Đăng ngay không xét kết quả đặt ảnh đại diện** (cùng loại SL-T102-1). `send_and_record` gọi `create_draft_with_images` rồi `release_post` chỉ xét `result["ok"]` (bài nháp đã tạo). Lệnh đặt ảnh đại diện hỏng chỉ thành câu `_FEATURED_NOT_SET` trong `result["message"]` (`DraftWithImages.featured_media = None`), lệnh đăng vẫn đi | `app/views/write.py:3583-3587`, `:3644-3650` | Công tắc bật, «Đăng ngay», SEO ghi được, đã tick; lệnh `POST /wp/v2/posts/<mã>` `{"featured_media": …}` trả 500 → lệnh `{"status": "publish"}` vẫn gửi (`tests/test_la_chan_t102.py`: `[{'status': 'publish'}]`). Bài lên công khai **không có ảnh đại diện** người dùng đã thấy, đã tick xác nhận (ảnh đại diện nằm trong mã băm LC-T094-8); theme, ảnh chia sẻ mạng xã hội, trang danh mục dùng ảnh khác hoặc không ảnh. LC-T094-38 ghi `release_draft` chỉ sau khi «ảnh đại diện, ghi SEO **đã xong**». Không lộ dữ liệu, sửa được trong trang quản trị; chỉ gặp khi bật công tắc | Một luật chung với SL-T102-1: với **Đăng ngay**, chỉ gọi `release_draft` khi mọi phần đã xác nhận đã lên website (ảnh đại diện đặt được khi bài có ảnh, SEO ghi được); thiếu thì bài vẫn là nháp, nháp ghi «đã gửi nháp» (không khóa), câu báo nói chưa đăng vì sao. **Hẹn giờ**: Cảnh báo (còn sửa được trước giờ đăng), như thiết kế cho SEO. Gỡ 1 dấu `xfail` |

### Xếp mức lỗi của Soi Lỗi

| Mã | Soi Lỗi | Lá Chắn | Vì sao | Sửa trước |
|---|---|---|---|---|
| SL-T102-1 | Trung bình | **Trung bình, giữ** | Tự tái hiện: `--runxfail` 3 ca (500, `written=False`, `unavailable`) đều gửi `{"status": "publish"}`. Đọc mã: `write_seo` chỉ ghi câu vào `result["seo"]`, `release_post` không xét; Chặn «Đăng ngay mà SEO chưa ghi» của bộ dựng chỉ theo **ý định** (công tắc ghi SEO). Trái điều kiện viết rõ LC-T094-39 («Đăng ngay khi SEO chưa ghi lên website → Chặn») trên đường quan trọng nhất; bài công khai ngay với tiêu đề, mô tả SEO mặc định | **Trước khi bật công tắc**; sửa chung với LC-T102-1 |
| G1 (dòng kế hoạch ghi «Đã gửi nháp» khi lệnh chuyển không rõ kết quả) | Ghi nhận | Ghi nhận, đồng ý; **nên** sửa trước khi bật | Sheet nói «nháp» trong khi bài có thể đã công khai; «Cập nhật trạng thái từ website» (chỉ đọc) sửa lại sau. Nên: không rõ kết quả thì không ghi trạng thái chuyển (hay ghi kèm ý «chưa rõ») | Trước khi bật (nên) |
| G2 (công tắc xét một lần) | Ghi nhận | Đồng ý | Xét ở đầu `publish_panel` cùng lần chạy với cú bấm, trước khi tạo client; xét thêm trong `send_draft` là lớp phòng rẻ | Khi làm nút công tắc |
| G3 (Nháp: mã băm cùng lần chạy) | Ghi nhận | Đồng ý | Nháp không công khai; màn hình vẫn có bảng link, địa chỉ | |
| G4 (chưa có nút bật ở Cài đặt) | Ghi nhận | Đồng ý, thành điều kiện | LC-T094-41 đòi công tắc riêng trong Cài đặt | Trước khi bật |

## Kết quả theo câu Chỉ Huy hỏi

### 1. Gộp `main` được khi công tắc tắt: **được**

- `release_enabled()` (`write.py:2806-2808`) chỉ đúng khi `st.session_state["_release_enabled"] is True`. Không widget nào mang khóa này, không đọc `st.query_params`, không khôi phục từ nháp (`open_draft` chỉ đặt khóa đã biết; `KEEP_KEYS` không có), không hằng nào bật sẵn (`grep`: khóa chỉ có ở `write.py:291`, `:2808`). Giá trị gần đúng (`1`, `"True"`, `[True]`) vẫn tắt (6 ca Soi Lỗi).
- Tắt thì `publish_panel` (`:3983-3986`) chỉ hiện `MSG_RELEASE_OFF` rồi trả về, **trước** khi tạo client, vẽ nút: Hẹn giờ, Đăng ngay không có nút `wp-send`. Chuỗi gọi duy nhất tới lệnh chuyển: `publish_panel` → `send_draft` → `send_and_record` → `release_post` → `release_draft` (grep `app/`: `release_draft` chỉ ở `:3650`; T-099 AST test vẫn qua). «Nháp» đặt `holder["release"] = None` (`:3434-3436`) nên không bao giờ tới `release_draft`; client chỉ tạo bài `draft` (T-099).
- Trang khác: `home.py`, `plan.py` chỉ gọi `post_statuses` (chỉ đọc); `wordpress.py` chỉ `create_draft` (nháp thử).

### 2. Phải xong **trước khi bật công tắc** (để lập phiếu thử thật LC-T094-44)

Bắt buộc:

1. **SL-T102-1 và LC-T102-1** (một luật chung, mục «Lỗi phát hiện»): Đăng ngay chỉ gửi lệnh đăng khi ảnh đại diện và SEO đã lên website; Hẹn giờ thì Cảnh báo. Gỡ 3 + 1 dấu `xfail`.
2. **Nút công tắc trong Cài đặt** (LC-T094-41, G4): công tắc riêng cho Hẹn giờ/Đăng ngay, mặc định tắt, như «Ghi SEO lên website» của T-041; Lá Chắn xét cách lưu (không để giá trị trong file nháp, `.env` hay thứ người khác sửa được bật thay người dùng); `send_draft` xét lại công tắc (G2).
3. **Thử thật LC-T094-44** (Chỉ Huy, chủ dự án): Sheet bản sao; bài chủ dự án duyệt; website trả header `Date` đúng (thiếu thì app Chặn hẹn giờ); tài khoản Biên tập viên hẹn giờ, đăng được qua REST; xem bài hiển thị thật (không nhúng lạ, không link lạ do theme, plugin); không ghi Application Password, file khóa, mã Sheet đầy đủ, email dịch vụ vào báo cáo thử.
4. **Lá Chắn rà Giai đoạn 5** (LC-T094-41 đòi) sau lượt thử, trước khi bật.

Nên (cùng phiếu sửa, không bắt buộc):

5. LC-T094-23 phần «nên» (so `modified_gmt` trước lệnh chuyển; Ghi nhận 1 biên bản T-099).
6. G1: lệnh chuyển không rõ kết quả thì không ghi trạng thái chuyển vào dòng kế hoạch (hay ghi kèm «chưa rõ»).
7. Ô «Tạo thêm một bài nháp mới» khi đang chọn Hẹn giờ/Đăng ngay: chữ ô nên nói đúng việc sẽ làm (tạo bài mới **và** hẹn giờ/đăng), dù nút gửi và ô xác nhận đã ghi rõ (Ghi nhận 2).
8. README «Hẹn giờ và Đăng ngay» (Thư Ký), câu «chưa dùng» ở `[plan]` của `config/content.toml`.

### 3. Có đường nào tới `future`/`publish` ngoài ý người dùng: **không**

Công tắc tắt: không (câu 1). Công tắc bật (chỉ trong test):

| Đường thử | Kết quả | Bằng chứng |
|---|---|---|
| Chưa tick «Tôi đã đọc lại…» | Nút khóa, 0 lệnh | `test_publish_now_with_seo_written` |
| Sửa chữ, ảnh, alt, giờ, hình thức, chuyên mục, công tắc SEO **sau** khi tick | Bỏ tick (`confirm_box`, `:3060-3071`: mã băm lúc tick ≠ mã băm đang hiện), 0 lệnh | `test_untick_when_*`; Soi Lỗi |
| Sửa và bấm **cùng một lần chạy** | Lần chạy dựng lại gói trước khi vẽ ô tick → mã khác → bỏ tick, nút khóa | Soi Lỗi `test_sua_roi_bam_trong_cung_lan_chay_khong_gui` |
| Bài đổi giữa lúc vẽ và lúc gửi (danh sách bài tải lại) | `send_draft` dựng lại gói (`fresh=True`) và so `package.matches(order.expected)` **trước lệnh ghi đầu tiên** (`:3417`); trước đó chỉ có lệnh đọc danh sách bài (LC-T094-36 đòi) | `test_changed_between_view_and_click_sends_nothing` |
| Giờ đã qua, < 10 phút, > 1 năm | Chặn (`check_schedule` theo đồng hồ máy) + `release_time_problem` theo giờ máy chủ (T-099) | Soi Lỗi; `test_schedule_too_soon_is_blocked` |
| Đồng hồ website lệch, thiếu `Date` | Không lệnh chuyển, bài là nháp, không khóa | Soi Lỗi (Date +5 phút) |
| Lệnh chuyển hết giờ, 5xx, lỗi lạ | Khóa «có thể đã…», không tự gửi lại, kể cả mở lại ở phiên mới | `test_release_unsure_locks_and_never_resends`, `test_unexpected_error_…`, Soi Lỗi 504 |
| Bấm đúp, hai tab, tab khác gửi lúc đang chuẩn bị | Một lệnh chuyển (khóa so-rồi-đặt T-089 + giành mã T-099) | `test_double_click_releases_once`, `test_two_tabs_only_one_release`, `test_other_tab_sends_while_preparing` |
| Bài website tạo ra không phải nháp | `release_draft` từ chối (không thuộc `_created_post_ids`), trang báo trạng thái lạ | đọc mã client T-099 |
| «Nháp» | Không bao giờ có lệnh chuyển (`holder["release"] = None`) | `test_draft_sends_exactly_the_builder_package` |

Hai chỗ lệch: SL-T102-1, LC-T102-1 (bài được đăng đúng ý «Đăng ngay» nhưng thiếu SEO hay ảnh đại diện đã xác nhận). Không đường nào đăng khi người dùng chọn Nháp hay chưa xác nhận.

### 4. Dữ liệu dòng kế hoạch, AI vào bài và lời dặn: **đúng điều kiện T-103**

- **T-103 đk 2a:** từ khóa vào lời dặn qua `_keyword` (`prompts.py:57-62`: gộp dòng, vô hiệu thẻ khung, đổi «» thành ‹›); ghi chú vào ô «Kinh nghiệm của xưởng» (`write.py:690-693`), tới AI qua `_material` → `_block("chat_lieu_that", …)` (`prompts.py:94-96`, vô hiệu thẻ khung); tiêu đề dự kiến chỉ hiện bằng `st.text` ở bước Dàn ý (`write.py:2005-2006`), không gửi AI; từ khóa phụ không dùng. **2b:** ghi chú qua `personal_info` / `mask_personal_info` (`[đã ẩn]`, câu `MSG_PLAN_MASKED`), `mentions_price` → `MSG_PLAN_PRICE` (`:690-697`). **2c:** `default_publish_time` (`:2826-2837`) đọc `[plan].default_time` qua `parse_plan_time`, sai thì 08:00, không đọc nhãn.
- `PlanRow` bỏ ký tự đổi hướng chữ, ký tự vô hình ở tiêu đề dự kiến, ghi chú, từ khóa (thử U+202E, U+2066, U+2067, U+200B: bỏ hết) (LC-T094-3).
- Chữ bài (AI viết từ các khung trên) chỉ tới WordPress qua gói bộ dựng T-096 (LC-T094-36): escape, chặn shortcode, không `<a>` ngoài link nội bộ trong danh sách bài, liệt kê mọi `href` và địa chỉ trần trên màn hình xác nhận. Slug kế hoạch qua `make_slug` rồi bộ dựng (sai dạng là Chặn). «Trang dịch vụ đích» chỉ thành mã bài từ danh sách bài lưu trên máy (`cached_site_index`, không gọi website, LC-T094-35), thành link bắt buộc (`required_ids`).
- **T-100:** `find_plan_draft(key, sheet_hash(<Sheet đang dùng>))` (`:644`), không có thì `open_row` đọc lại Sheet (`:655`); sau khi gửi `record_status(…, sheet_id=…)` (`:3616-3618`), `BLOCKED` hiện câu của kết quả, việc còn nợ giữ, lỗi Sheet không làm gửi lại WordPress (LC-T094-40). «Đang viết» ghi đúng một lần (khóa `_start_*` bị bỏ sau khi dùng).
- **T-101 đk 2 (G1):** `start_from_plan` chỉ gắn dòng khi từ khóa của lần bấm trùng từ khóa dòng đọc lại (`:659-661`); ô gõ tay ở trang Bài viết bỏ `_start_plan_key`, `_open_draft` cũ; khóa sót không kèm từ khóa bị bỏ (`:370`).

### 5. Gửi trùng, «Gửi nháp» kèm ảnh, gắn ảnh T-110 trên bản gộp `origin/main` `a416e74`

- `git merge-tree --write-tree`: **không xung đột** (cây `d43db44`). Chung file với `main` (từ `944160c`): `write.py` (tự gộp: bản gộp có câu `GPS_PUBLIC_WARNING` mới của T-110), `client.py` (bản gộp **đúng bằng** của `main`: T-099 lượt 2 + T-110), `test_app_images.py` (tự gộp: ca `test_send_draft_with_real_image` có cả kỳ vọng lệnh gắn ảnh của T-110 lẫn khối bộ dựng của T-102), file T-099.
- Chạy chọn lọc trên bản gộp, 3 lô song song, **36 file**: T-102, T-110, T-099, T-100 (lô A); «Gửi nháp» T-056, T-086, T-089, `test_app_images.py`, `test_storage_send_state.py` (lô B); T-041, T-059, T-101, T-103, mở mọi trang, `test_content_edge_cases.py`, `test_app_wordpress.py` (lô C): **1.757 passed, 7 xfailed, 0 failed** (lô A 1.037 + 7 xfailed, 8 phút; lô B 248, 26 phút; lô C 472, 7 phút). 7 xfailed đều có chủ đích: SL-T102-1 × 3, SL-T110-1 × 3, LC-T110-1. `tests/test_la_chan_t102.py` trên bản gộp: 2 passed, 1 xfailed.
- Gửi trùng: khóa «đang gửi» giữ tới khi biết kết quả lệnh chuyển (`send_and_record`: tạo nháp xong vẫn ghi `pending=True` kèm mã bài khi có lệnh chuyển, `:3583`; `release_post` ghi kết quả, `:3683-3686`); ghi nháp hỏng thì nháp vẫn «đang gửi» (khóa, hướng an toàn). Lệnh gắn ảnh T-110 nằm trong `create_draft_with_images`, trước ảnh đại diện, trước SEO, trước lệnh chuyển; gắn lỗi thì chỉ là câu báo (với Đăng ngay ảnh sẽ công khai cùng bài, nên không cần chặn).

## Đối chiếu điều kiện

| Điều kiện | Kết quả | Bằng chứng |
|---|---|---|
| LC-T094-1 (test không gọi thật) | Đạt | `FakeWordPress`, `FakeGoogle` + `FakePlanSheet` qua `SheetsClient` thật, AI giả; bộ chặn mạng bật |
| LC-T094-2 (câu báo cố định) | Đạt | Câu lỗi là `str()` của lớp lỗi câu cố định (`ReleaseError`, `SheetsError`, `SheetPlanError`, `StatusResult.message`); lỗi lạ quanh lệnh chuyển: `MSG_RELEASE_UNEXPECTED`; mồi trong lời máy chủ không hiện (ca Họa Sĩ, Soi Lỗi) |
| LC-T094-3 (chữ thuần) | Đạt | Số `unsafe_allow_html=True` không đổi so với `main` (`write.py` 7, `home.py` 2, `plan.py` 0); chữ mới hiện qua ô bảng (`cell_text`), `st.text`, `escape_markdown(shown_text(…))`; link, địa chỉ bài, trang sửa bài hiện dạng chữ không bấm được; `st.link_button` chỉ với `edit_link` client tự dựng từ `WORDPRESS_URL` và mã số |
| LC-T094-36 (mọi hình thức đúng gói bộ dựng) | Đạt | `send_and_record` gửi `package.title`, `content_parts`, `categories`, `excerpt`, `slug` của gói; tải lại danh sách bài ngay trước khi dựng gói gửi khi bài có link (`package_index(fresh=True)`); còn Chặn thì không gửi (`:3405-3416`) |
| LC-T094-37 (màn hình xác nhận) | Đạt | `review_header` (giờ Việt Nam kèm thứ, «Hiện công khai ngay khi bấm», tiêu đề, đường dẫn, chuyên mục, SEO), `review_tables` (mọi link với cờ, tên máy ASCII; địa chỉ trần; nhúng; ảnh + GPS; shortcode), Nháp rút gọn vẫn có bảng link, địa chỉ |
| LC-T094-38 (mã băm, thứ tự) | Đạt, trừ LC-T102-1 | Mã băm lúc hiện (`_wp_shown`), ô tick nhớ mã (`remember_confirm`), so trước lệnh ghi đầu tiên; thứ tự tạo nháp → ghi SEO → lệnh chuyển. «Đã xong» chưa xét kết quả ảnh đại diện (LC-T102-1) |
| LC-T094-39 (khóa gửi trùng phủ lệnh chuyển; Đăng ngay khi SEO chưa ghi → Chặn) | **Đạt phần khóa; chưa đạt phần Chặn** (SL-T102-1) | Khóa: như câu 5. Chặn: chỉ theo ý định |
| LC-T094-40 (ghi dòng kế hoạch qua T-100) | Đạt | `record_plan` qua `record_status`; lỗi Sheet không gửi lại WordPress |
| LC-T094-41 (công tắc mặc định tắt) | Đạt cho lúc gộp | Tắt: không nút, câu lý do, không đường tới `release_draft`. Nút trong Cài đặt: trước khi bật |
| T-096 (LC-T094-3 phần hiển thị) | Đạt | Như LC-T094-3 |
| T-099 đk 2 lượt 1; L2-1 → L2-3 | Đạt | Một `release_draft` mỗi lần bấm, trên client vừa tạo nháp (`result["post_id"]` của chính lần gửi); client mới trong nhánh bấm (`:4088`), không nằm trong `holder`, phiên, cache; ghi kết quả vào nháp trước mọi `st.*`; `ReleaseError` không chắc / đã công khai / `Exception` khác → khóa, câu cố định, hiện chữ thường; `when_utc` từ `local_to_utc`, cùng giá trị cho `date_gmt` của gói |
| T-100 (mục 5; lượt 3–4) | Đạt | Câu 4 |
| T-101 đk 1 (LC-T101-1), đk 2 (G1) | **Đạt, LC-T101-1 đóng** | Mục dưới; G1 câu 4 |
| T-103 đk 2 (a, b, c) | Đạt | Câu 4 |
| Board «Việc bắt buộc Giai đoạn 5» | Đạt | Bộ dựng T-096 cho mọi hình thức; liệt kê mọi `href`, địa chỉ lạ, `@`, `xn--`; một đường tới `publish`/`future` có xác nhận và test; từ khóa Sheet qua `_keyword` (SL-7); gỡ U+200B trước khi gửi; chữ đã gỡ không vào `st.markdown` |

### LC-T101-1: đóng

Mọi bảng có chữ Sheet, chữ dán, AI, website trên ba trang T-101/T-102: trang Kế hoạch 4 bảng qua `safe_rows` (`plan.py:449`, `:474`, `:572`, `:796`), màn hình xác nhận 5 bảng qua `cell_text` (`write.py:3116-3182`), bảng liên kết SEO (`st.data_editor`, `write.py:2600`) hai cột chữ qua `safe_text`. 2 ca của `tests/test_la_chan_t101.py` qua, chỉ xóa 2 dấu `xfail` và `import pytest` thừa (R5 đúng). Ngoài phạm vi (có từ trước, Ghi nhận 3): bảng chuyên mục, thẻ ở trang Kết nối WordPress.

## Danh sách kiểm tra

| Mục | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets: 2 mục có từ trước (dưới) |
| S2 | Đạt | LC-T094-2 |
| S3 | Không áp dụng | `.env.example`, `pyproject.toml`, `uv.lock`, `app/main.py` không đổi |
| W1 | Đạt có điều kiện | Mặc định nháp; Hẹn giờ/Đăng ngay chỉ qua xác nhận có mã băm, có test; công tắc tắt. SL-T102-1, LC-T102-1 trước khi bật |
| W2 | Đạt | Chỉ bài client vừa tạo được sửa, chuyển (T-099, T-110); ghi Sheet chỉ 4 ô qua T-100 |
| W3 | Đạt | LC-T094-36 |
| W4 | Đạt | Không đổi lớp mạng; client mới mỗi lần bấm |
| A1 | Đạt | T-103 đk 2a |
| A2 | Đạt | AI không có công cụ hành động; chữ AI chỉ tới website qua bộ dựng |
| A3 | Đạt | Ghi chú kế hoạch che số điện thoại, email trước khi vào chất liệu thật (gửi AI) |
| U1 | Đạt | LC-T094-3 |
| U2 | Đạt | Không trang mới |
| F1, F2 | Đạt, không đổi | Đọc ảnh, kiểm băm byte đã duyệt như T-086, T-089 |
| F3 | Đạt | Đọc `config/content.toml` bằng `tomllib` |
| D1, D2 | Đạt | Không thư viện mới |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| ruff | `ruff check .` trên nhánh: sạch | |
| bandit (`PYTHONUTF8=1`) | `write.py`, `plan.py`, `home.py`: 0 | |
| detect-secrets (`PYTHONUTF8=1`, mồi tiếng Việt cùng lần quét: bắt được) | 17 file của phiếu: 2 mục: «Basic Auth Credentials» ở docstring `site_host` (`write.py`, chữ mẫu, 27/10) và «Secret Keyword» hằng mật khẩu thử ở `test_content_edge_cases.py:46` (14/10) | Có từ trước, không phải bí mật |
| pip-audit | Không chạy lại: `uv.lock` không đổi | |
| pytest | `tests/test_la_chan_t102.py`: 2 passed, 1 xfailed (`--runxfail`: hỏng đúng ở `[{'status': 'publish'}] == []`); SL-T102-1 `--runxfail`: 3 ca hỏng đúng lý do. Bản gộp: câu 5 | |

## Ghi nhận (không xếp lỗi)

1. **Cỡ bài:** đề xuất của biên bản T-096 (Ghi nhận 1: giới hạn cỡ thân bài khi dựng, vì bài cố ý dài 5 MB dựng mất vài phút) chưa làm; bước Xuất bản dựng gói ở **mỗi lần vẽ**. Chỉ làm chậm máy của chính người dùng (chữ do người dùng dán hay AI viết, AI có giới hạn độ dài). Nên thêm giới hạn khi sửa SL-T102-1.
2. **«Tạo thêm một bài nháp mới»** khi đang chọn Đăng ngay: tick ô này rồi tick xác nhận thì app tạo **và đăng** bài mới (bài thứ hai công khai). Nút gửi ghi rõ «🚀 Gửi và đăng công khai ngay», ô xác nhận phải tick lại, nên không phải lỗi; chữ ô nên nói đúng việc (điều 7 ở câu 2).
3. **Bảng chuyên mục, thẻ ở trang Kết nối WordPress** (`wordpress.py:149`, có từ Giai đoạn 1): tên, slug từ website vào `st.dataframe` chưa qua `safe_text` (cùng loại LC-T101-1). Chữ do người quản trị website đặt; hại chỉ khi tải CSV, mở bằng Excel và bật chỉnh sửa. Nên dọn ở phiếu dọn sau.
4. `BuiltArticle.matches` với chuỗi ngoài ASCII ném `TypeError` (Ghi nhận 2 biên bản T-096): không tới được (mã băm so là chuỗi hex app tự tính hay `None`).
5. Với Hẹn giờ, ảnh gắn lỗi (T-110) thì ảnh còn trong danh sách Media công khai tới giờ đăng; câu báo T-110 đã nói. Không cần chặn.

## Điều kiện

1. **Gộp `main`:** được ngay (công tắc tắt). Chỉ Huy chạy toàn bộ test khi gộp.
2. **Trước khi bật công tắc Hẹn giờ/Đăng ngay:** điều 1 → 4 (bắt buộc) ở câu 2: sửa SL-T102-1 + LC-T102-1, nút công tắc ở Cài đặt (Lá Chắn xét cách lưu), thử thật LC-T094-44, Lá Chắn rà Giai đoạn 5. Điều 5 → 8: nên làm cùng.
3. Kiểm lại biên bản này bằng Claude Fable sau 01/11.

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 1 Trung bình (SL-T102-1, giữ mức), 1 Thấp mới (LC-T102-1). **Gộp `main` được ngay khi công tắc tắt.** SL-T102-1, LC-T102-1 sửa trước khi bật công tắc. LC-T101-1 đóng.

# Báo cáo T-102 · Bước Xuất bản thật: màn hình xác nhận, hẹn giờ, đăng ngay · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-102](../tickets/T-102-buoc-xuat-ban-that.md) (đọc ở checkout chính) |
| Nhánh | `team/T-102`, đầu nhánh `5c37be0` (đã gộp `team/T-101` `944160c`); thử gộp với `origin/main` `eef13b5` |
| Ngày nộp | 2026-10-30 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T102-1), 0 Thấp. **Không lỗi nào phải sửa trước Lá Chắn hay trước khi gộp** (công tắc Hẹn giờ/Đăng ngay đang tắt); SL-T102-1 **phải sửa trước khi bật công tắc** (LC-T094-41, -44). Gộp `main` không xung đột |

## Tóm tắt (cho chủ dự án)

- **Hẹn giờ và Đăng ngay đang tắt đúng như dặn.** Tôi thử cả cách bật «gần đúng» (số 1, chữ «True»…): vẫn tắt, không có nút gửi, không lệnh nào lên website. Đọc mã nguồn: lệnh đăng chỉ có một đường duy nhất, và đường đó đi qua công tắc.
- **Khi bật công tắc trong test, màn hình xác nhận giữ đúng bài đã xem.** Sửa tiêu đề, đường dẫn hay chữ bài rồi bấm gửi ngay (kể cả sửa và bấm cùng một lúc): phần mềm tự bỏ tick, không gửi gì. Giờ hẹn đã qua thì không cho gửi. Đồng hồ website lệch thì không hẹn giờ, bài vẫn là nháp. Mất mạng đúng lúc hẹn giờ thì khóa gửi lại, kể cả khi mở lại ở cửa sổ mới.
- **1 lỗi cần sửa trước khi bật Hẹn giờ/Đăng ngay (Trung bình):** chọn «Đăng ngay» có bật «Ghi SEO lên website», nhưng lúc gửi lệnh ghi SEO bị lỗi (website lỗi, SiteSEO chưa cho ghi). Khi đó phần mềm **vẫn đăng bài công khai**, với tiêu đề, mô tả SEO mặc định. Lá Chắn đã dặn trường hợp này phải chặn. Hiện công tắc đang tắt nên chưa ai gặp được.
- «Gửi nháp» kèm ảnh, ảnh đại diện, SEO, khóa gửi trùng vẫn chạy như cũ. Đã thử trên bản gộp với code mới nhất (cả phần gắn ảnh vào bài nháp của T-110).
- **Việc của bạn:** không có.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t102.py` | Mới: 19 ca (16 qua, 3 `xfail(strict=True)` SL-T102-1). Mượn khung trang Soạn bài và WordPress giả (`live`) của `test_t102_publish.py`, `test_app_images.py`, `test_t086_send_state.py` như các file T-086, T-089; mọi ca, mọi kiểm là của Soi Lỗi |
| `docs/team/reports/T-102-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu. Không gọi WordPress, Google, AI thật.

## Kiểm theo yêu cầu

### 1. Không đường nào tới `future`/`publish` khi công tắc tắt; bật thì chỉ qua xác nhận có mã băm

- **Công tắc tắt** (`_release_enabled` là `1`, `"True"`, `[True]`; Hẹn giờ và Đăng ngay, 6 ca): không nút `wp-send`, câu «đang **tắt**», `release_draft` không được gọi, **0 request** tới website.
- **Đọc mã nguồn** (`write.py`): `release_draft` chỉ trong `release_post`; `release_post` chỉ trong `send_and_record`; `send_and_record` chỉ trong `send_draft`; `send_draft` chỉ trong `publish_panel`. Trong `publish_panel`, `release_enabled()` xét **trước** cả lúc tạo client, trước lệnh gửi. `create_draft_with_images` chỉ ở `send_and_record`, không còn `create_draft`, không còn `paragraphs_to_html`.
- **Mã băm** (công tắc bật trong test):
  - sửa tiêu đề, slug hay chữ bài **rồi bấm gửi trong cùng một lần chạy** (như ô chữ mất tiêu điểm đúng lúc bấm): bỏ tick, 0 lệnh ghi, không `release_draft`, nút khóa;
  - sửa tiêu đề hay slug ở lần chạy sau khi tick (Đăng ngay): bỏ tick, câu «…bỏ tick…», nút khóa, 0 lệnh ghi.
- Bấm hai lần, hai tab, tab khác gửi lúc đang chuẩn bị, ngắt sau lệnh chuyển: ca của Họa Sĩ (`test_double_click_releases_once`, `test_two_tabs_only_one_release`, `test_other_tab_sends_while_preparing`, `test_interrupted_after_release_keeps_result_and_lock`), chạy lại trên bản gộp: qua.
- **Tải lại trang giữa chừng:** lệnh hẹn giờ trả 504 (không rõ kết quả); mở lại nháp ở **phiên mới** (như tải lại trang, mở tab khác): nút khóa, câu «có thể đã…», không chép lời máy chủ; đúng 1 lệnh chuyển.
- **Giờ hẹn đã qua trong ngày** (ngày hôm nay, một giờ trước): dòng Chặn «đã qua», nút khóa dù đã tick, 0 lệnh ghi.
- **Đồng hồ website lệch** (header `Date` +5 phút): bài nháp vẫn tạo, ảnh vẫn lên, **không lệnh chuyển nào**; nháp ghi «đã gửi nháp» (`released`, `release_unknown`, `pending` đều tắt), câu báo «lệch giờ website»; chạy lại không gửi thêm.
- **Lệnh chuyển là lệnh cuối:** đúng một lệnh chuyển, là request cuối cùng; mọi lệnh ảnh (tải, ghi alt, và gắn ảnh vào bài nháp trên bản gộp có T-110) đều trước nó.

### 2. Không lùi «Gửi nháp», ảnh đại diện, `srcset`, SEO; nội dung đúng gói bộ dựng

- Chạy trên bản gộp (mục 5): T-086, T-089 (9 file «Gửi nháp», khóa gửi trùng), `test_app_images.py` (ảnh, `srcset` T-059, «[» «]» T-061), T-041, T-059 (SEO SiteSEO), T-099, T-110: qua.
- Nội dung gửi là `content_parts` của gói T-096 (`test_draft_sends_exactly_the_builder_package` của Họa Sĩ; đọc mã: không còn đường `paragraphs_to_html`, `article_parts`).

### 3. Dữ liệu dòng kế hoạch, Sheet, AI là chưa tin cậy

Đọc `start_from_plan`, `fill_from_plan`, `plan_details`: chỉ tin **Mã bài** (`parse_key`), đọc lại dòng trên Sheet (`open_row`), từ khóa phải trùng từ khóa của lần bấm (G1 T-101); ghi chú che số điện thoại, email (`mask_personal_info`) rồi vào ô «Kinh nghiệm của xưởng» (chất liệu thật, đi vào lời dặn AI qua khung dữ liệu sẵn có, T-103 đk 2a), nhắc khi nói giá; slug qua `make_slug`; trang dịch vụ đích chỉ thành mã bài từ danh sách bài lưu trên máy; giờ qua `parse_plan_time` (HH:MM hợp lệ, giờ 24, phút 60 bị bỏ); ngày đã qua thì ô Hẹn giờ tự về ngày mai; tiêu đề dự kiến chỉ hiện làm gợi ý. Ca của Họa Sĩ cho phần này (`test_write_from_plan_rereads_row_…`, `test_planned_title_is_only_a_hint`, `test_plan_key_with_another_keyword_is_not_attached`…) chạy lại trên bản gộp: qua.

### 4. Tên bị xóa, đổi (bài học T-101)

Tên cấp module bị bỏ so với `main`: `write.py` bỏ `article_parts`, `demo_note`, `demo_toast`, `draft_panel` (đổi thành `publish_panel`); `seo_app/demo.py` bỏ `CATEGORIES`. `git grep` trên cây gộp (`tests/`, `app/`, `seo_app/`, `scripts/`): `article_parts` chỉ là hàm riêng của `test_soi_loi_t096.py`; `draft_panel` chỉ còn trong lời mô tả của `test_la_chan_t056.py`, `test_la_chan_t089.py` (không phải code, hai file qua); `CATEGORIES` ở `test_soi_loi_t091.py` là hằng riêng của file đó; `demo_note`, `demo_toast`: không còn đâu. Không file nào hỏng vì tên bị xóa.

### 5. Gộp thử với `origin/main` `eef13b5`

`git merge-tree --write-tree origin/main HEAD` (`main` có T-110 gắn ảnh vào nháp và câu `GPS_PUBLIC_WARNING`, T-107 lượt 3 tắt HEIC, T-101): **không xung đột** (cây `7e86785`; `main` cục bộ cũng là `eef13b5`). Thay đổi của T-102 so với `main` sau gộp: đúng 14 file (`write.py`, `home.py`, `plan.py`, `demo.py`, test, báo cáo). Trên bản gộp (thêm file test của tôi), 33 file, 3 phần song song: **1.735 passed, 6 xfailed, 0 failed** (1.035 + 232 + 468). 6 xfail: 3 SL-T102-1 của tôi, 3 SL-T110-1 (đã có ở `main`).

- Phần 1: `test_t102_publish.py`, `test_t102_formula_cells.py`, `test_soi_loi_t102.py`, T-110 (`test_t110_gan_anh_vao_bai_nhap.py`, `test_soi_loi_t110.py`, `test_la_chan_t093.py`), T-099 (`test_wordpress_release.py`, `test_soi_loi_t099.py`, `test_la_chan_t099.py`), T-100 (`test_plan_sync.py`, `test_soi_loi_t100.py`, `test_la_chan_t100.py`).
- Phần 2 («Gửi nháp»): `test_app_images.py`, T-056 (`test_soi_loi_t056.py`, `test_la_chan_t056.py`), T-086 (3 file), T-089 (3 file).
- Phần 3: T-041 (`test_t041_seo_ui.py`, `test_soi_loi_t041.py`), T-059 (`test_t059_siet_ghi_seo_va_srcset.py`, `test_soi_loi_t059.py`), T-101 (`test_t101_plan_page.py`, `test_t101_home_page.py`, `test_t101_settings_google.py`, `test_soi_loi_t101.py`, `test_la_chan_t101.py`), `test_soi_loi_t103.py`, `test_app_pages.py`, `test_content_edge_cases.py`.

### R5: test cũ đã đổi

| Test | Điều kiện duyệt | Đối chiếu diff |
|---|---|---|
| `test_app_images.py::test_send_draft_with_real_image` (18:45) | Giữ đủ kiểm ảnh | Chỉ đổi ghim mảnh HTML cũ thành khối của bộ dựng (`parts[:2]`, ảnh `parts[2:]`); giữ mọi kiểm ảnh (thẻ `ImageTags`, alt, chú thích, tên file, WebP còn GPS, alt trên Media, bài nháp, nút khóa sau khi gửi) và **thêm**: ảnh đúng chỗ sau phần của nó, `srcset` chỉ file đầy đủ, `alt`, `<figcaption>`, «[gallery]» thành `&#91;…&#93;`, không `{{`. Đạt |
| `test_content_edge_cases.py::test_publish_now_requires_confirmation` (18:45) | Giữ ý «đăng ngay cần xác nhận» bằng ca bật công tắc | Ca này nay kiểm công tắc tắt (không nút, câu «đang tắt»); ý cần xác nhận nằm ở `test_t102_publish.py::test_publish_now_with_seo_written` (bật công tắc: chưa tick thì nút khóa, chưa lệnh nào), cùng các ca `test_untick_when_*`. Đạt |
| `test_la_chan_t089.py::test_lc_t089_1_…` (18:45) | Client giả kiểm khóa gửi, không nuốt `**kwargs` | Client giả nhận `**fields` nhưng **ghi lại** từng lệnh; test so đúng tiêu đề, khối, `{"categories": (), "tags": (), "excerpt": …, "slug": ""}`; mọi kiểm «đang gửi», khóa gửi trùng giữ nguyên. Đạt |
| `test_soi_loi_t041.py::test_absurd_hand_edited_seo_block_keeps_page_working` (18:45) | Slug «Cửa Sắt/../../etc» khóa nút | Thêm: nút «Gửi nháp» khóa, câu slug của bộ dựng; xóa slug rồi phần cũ chạy tiếp, các kiểm cũ giữ nguyên. Đạt |
| `test_t101_plan_page.py::test_write_button_opens_compose_without_wordpress`, `test_t101_home_page.py::test_start_from_plan_row_…` (19:05) | Trang Kế hoạch/Bài viết không ghi Sheet; Soạn bài ghi «Đang viết» một lần | Bộ theo dõi `record_status` ghi số lệnh ghi **ngay trước** lần gọi: `(Đang viết, 0, 0, 0)`; đúng 1 lệnh ghi, chỉ ô Trạng thái, Cập nhật lúc; lần chạy sau không ghi lại; khóa `_start_plan_key` bỏ sau khi dùng; 0 request WordPress. Kiểm «không lệnh ghi Sheet» cũ thay bằng kiểm chặt hơn ở đúng thời điểm. Đạt |
| `test_soi_loi_t103.py` (19:50, trên nhánh T-101, đã ở `main`) | Dùng mẫu riêng, giữ ý test | `SAMPLE_PLAN`, `SAMPLE_PASTE` đúng từng chữ với `PLAN_ROWS` (bỏ cột trạng thái không dùng) và `PLAN_PASTE_EXAMPLE` của `demo.py` ở `0122d4b`; các kiểm giữ nguyên. Đạt |
| `test_la_chan_t101.py` (19:52) | Chỉ xóa dấu `xfail` | Xóa 2 dấu `xfail(strict=True)` LC-T101-1 và `import pytest` thành thừa; thân test giữ nguyên. Đạt |

### Đột biến (đo sức test mới)

8 đột biến trên `write.py` (script `mutate102.py`), mỗi lần chạy `tests/test_soi_loi_t102.py` (dừng ở ca hỏng đầu): **7 bị bắt**.

| Đột biến | Kết quả |
|---|---|
| W1 công tắc luôn bật | bắt (`test_cong_tac_chi_bat_khi_dung_true`) |
| W2 công tắc bật theo giá trị gần đúng (`bool(...)`) | bắt (cùng ca) |
| W3 không bỏ tick khi bài đổi | bắt (`test_sua_sau_khi_tick_thi_bo_tick`) |
| W4 không bỏ tick, không so mã băm lúc gửi | bắt (`test_sua_roi_bam_trong_cung_lan_chay_khong_gui`) |
| W5 lệnh chuyển trước lệnh ghi SEO | sống sót với file của tôi (ca hẹn giờ không ghi SEO); ca `test_publish_now_with_seo_written` của Họa Sĩ bắt |
| W6 bỏ hẳn công tắc ở `publish_panel` | bắt |
| W7 lệnh chuyển không rõ kết quả mà không khóa | bắt (`test_khong_ro_ket_qua_mo_lai_o_phien_moi_van_khoa`) |
| W8 bỏ kiểm giờ hẹn của màn hình | bắt (`test_gio_hen_da_qua_trong_ngay_bi_chan`) |

## Lỗi tìm ra

### SL-T102-1 · Trung bình · Đăng ngay mà lệnh ghi SEO hỏng lúc gửi vẫn đăng công khai (LC-T094-39)

- **Chỗ:** `app/views/write.py`, `send_and_record` (`write_seo(client, holder)` rồi `release_post(client, store, holder)`) và `release_post`: không xét kết quả ghi SEO. Chặn «Đăng ngay mà SEO chưa ghi lên website» hiện chỉ ở bộ dựng T-096 (`seo_app/publish/render.py`, dòng Chặn khi `seo.write` tắt), tức chỉ xét **ý định** (công tắc «Ghi SEO lên website»), không xét kết quả.
- **Thử** (công tắc Hẹn giờ/Đăng ngay bật trong test, «Ghi SEO lên website» bật, đã tick): `set_seo_meta` ném lỗi 500, trả `SeoWriteResult(written=False, reason="error")`, hay trả `reason="unavailable"` (SiteSEO chưa cho ghi). Cả 3 ca: lệnh đăng vẫn gửi, thân `{"status": "publish"}`, bài lên công khai.
- **Hậu quả:** trái LC-T094-39 («Đăng ngay khi SEO chưa ghi lên website → Chặn»): bài công khai ngay với tiêu đề, mô tả SEO mặc định của SiteSEO, Google có thể lấy ngay. Hiện **không gặp được** vì công tắc tắt (LC-T094-41); gặp ngay khi bật, chỉ cần lệnh ghi SEO lỗi một lần (website chậm, SiteSEO tắt Abilities…).
- **Test:** `test_sl_t102_1_dang_ngay_ma_seo_ghi_hong_thi_khong_dang` (3 xfail).
- **Gợi ý:** `write_seo` ghi lại kết quả có cấu trúc (đã ghi đủ các trường được bật hay chưa); với Đăng ngay, chưa ghi được thì **không** gọi `release_draft`: bài vẫn là nháp, nháp ghi «đã gửi nháp» (không khóa), câu báo nói rõ chưa đăng vì SEO chưa ghi. Hẹn giờ: giữ Cảnh báo như thiết kế.

## Ghi nhận (không tính lỗi)

- **G1 · Ghi trạng thái dòng kế hoạch khi lệnh chuyển không rõ kết quả:** `record_plan` ghi «Đã gửi nháp» trong khi bài có thể đã được hẹn giờ, đăng. Đúng một phần (bài nháp đã tạo), bước «Cập nhật trạng thái từ website» (`post_statuses`) sửa lại sau; cân nhắc không ghi hay ghi kèm ý «chưa rõ».
- **G2 · Công tắc xét một lần ở `publish_panel`** (cùng lần chạy với lệnh gửi nên đủ); lớp phòng thêm: `send_draft` xét lại `release_enabled()` trước khi đặt `holder["release"]`.
- **G3 · Nháp không tick:** mã băm của Nháp lấy từ chính lần chạy có cú bấm, nên chỉ bắt thay đổi giữa lúc vẽ và lúc gửi trong cùng lần chạy (danh sách bài tải lại), không bắt chữ đổi cùng lúc bấm. Nháp không công khai, màn hình vẫn hiện bảng link, địa chỉ: chấp nhận được.
- **G4 · Bật công tắc:** chưa có nút ở Cài đặt (quyết định 1 của Họa Sĩ); khi làm, Lá Chắn xét cách lưu như công tắc ghi SEO.

## Lệnh đã chạy

- `uv run pytest tests/test_soi_loi_t102.py`: 16 passed, 3 xfailed; `--runxfail` 3 ca SL-T102-1: hỏng đúng ở `[{'status': 'publish'}] == []`.
- Bản gộp với `origin/main` `eef13b5`, 33 file: 1.735 passed, 6 xfailed, 0 failed.
- Đột biến: 7/8 bị test của tôi bắt, W5 bị ca của Họa Sĩ bắt.
- `uv run ruff check .`: sạch. `detect-secrets` (`PYTHONUTF8=1`) trên file test, báo cáo: sạch.
- Script: thư mục ghi chú chung `T-102-soi-loi-scripts/mutate102.py`.

# Báo cáo T-127 · Nút «Đưa vào kế hoạch»: từ khóa Google thành đề xuất «Thêm bài» chờ duyệt

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-127](../tickets/T-127-dua-tu-khoa-vao-ke-hoach.md) · câu 7 = B (chủ dự án, 04/11) · LC-T120-13, -15, -24 |
| Nhánh | `team/T-127`, từ `team/T-125` (`09fdad2`); mã và test `523b0ce`, `0505f31`, báo cáo `0c1f286`; lượt 2 `8ce3383`, báo cáo lượt 2 ở commit ngay sau |
| Ngày nộp | 2026-11-10 (giờ máy, +07) |
| Kết quả | Hoàn thành: yêu cầu 1–5; lượt 2: SL-T127-1 đã sửa (mục «Lượt 2» cuối báo cáo) |

## Tóm tắt (cho chủ dự án)

- Trang «📈 Theo dõi», dưới bảng từ khóa của một bài, nay có ô **«Chọn từ khóa đưa vào kế hoạch (tối đa 10)»** và nút **«➕ Đưa vào kế hoạch»**.
  - Bấm nút thì mở trang Kế hoạch. Mỗi từ khóa đã chọn thành một đề xuất «Thêm bài», nguồn «Search Console».
  - Bạn tick duyệt rồi bấm «Áp dụng» như mọi đề xuất khác. Phần mềm không ghi thẳng vào Google Sheet, không gọi AI.
- Ô chọn chỉ có từ khóa «sạch»:
  - chỉ chữ tiếng Việt hoặc a–z, số, khoảng trắng, dấu «-»;
  - tối đa 80 ký tự;
  - không có số điện thoại, email, địa chỉ web.
- Từ khóa không đạt thì không có trong ô chọn. Trang chỉ báo **số lượng** từ khóa bị bỏ, không chép lại nội dung.
- Đề xuất có cảnh báo giống như khi nạp kế hoạch: trùng một dòng kế hoạch đã có, trùng bài đã đăng, hoặc nhiều bài gần giống nhau (trang cửa ngõ). Đề xuất có cảnh báo không được tick sẵn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/propose.py` | <ul><li>`google_keyword(text)`: bộ lọc chặt (LC-T120-24), trả `None` khi không nhận. Thứ tự kiểm: chuẩn NFC, gộp dấu cách, ≤ 80 ký tự, chỉ ký tự trong `_KEYWORD_LETTERS` (a–z, đ, 12 nguyên âm tiếng Việt với đủ 5 dấu thanh, cả hoa lẫn thường: 186 ký tự), số 0–9, dấu cách, «-». Phải có ít nhất một chữ; `personal_info` không thấy gì; không có chữ `www`/`http`/`https`.</li><li>`from_google_keywords(current, keywords, posts=, today=) -> ProposalSet`: lấy tối đa 10 từ khóa. Mỗi từ khóa qua `google_keyword`, rồi qua `PlanRow.model_validate` (mọi bộ kiểm dòng kế hoạch). Từ khóa trùng nhau trong cùng lần (cùng `keyword_key`) chỉ lấy một. Mỗi dòng mới nhận Mã bài kế tiếp, trạng thái «Chưa viết», rồi qua `check_proposals` như T-098.</li><li>Câu báo cố định chỉ đếm số: `NOTE_GOOGLE_TOO_MANY`, `NOTE_GOOGLE_SKIPPED`, `NOTE_GOOGLE_REPEATED`.</li></ul> |
| `app/views/tracking.py` | <ul><li>`plan_box(table)` thay nút giữ chỗ của T-125. Gồm `st.multiselect` chỉ có từ khóa qua bộ lọc (`max_selections=10`, khóa `trk-plan-pick`), câu đếm từ khóa không có trong ô chọn, và nút «➕ Đưa vào kế hoạch» (`trk-to-plan`, khóa khi chưa chọn gì).</li><li>Khi bấm: đặt `st.session_state["plan_google_keywords"] = tuple(đã chọn)` rồi gọi `st.switch_page("views/plan.py")`.</li></ul> |
| `app/views/plan.py` | `take_google_keywords(base, keywords)`. Chạy ngay sau khi trang đọc kế hoạch: lấy ra (`pop`) khóa trên, dựng đề xuất trên kế hoạch vừa đọc, đưa vào ô duyệt có sẵn (`keep_proposals`) kèm dòng «Từ khóa chọn ở trang 📈 Theo dõi…». Chỉ nhận `tuple`. Chưa đọc được kế hoạch thì chỉ cảnh báo. Hết Mã bài trống (`PlanKeyError`) thì báo câu cố định như nút đề xuất khác. |
| `tests/test_t127_dua_vao_ke_hoach.py` | Test mới, 65 ca (bảng đối chiếu ở dưới) |

### Chỗ để ngỏ, tôi đã chọn

1. **Chuyển trang bằng `session_state` và `st.switch_page`.**
   - Trang Theo dõi chỉ chuyển danh sách chữ đã chọn. Đề xuất được dựng ở trang Kế hoạch trên kế hoạch vừa đọc từ Sheet, nên Mã bài kế tiếp và phép kiểm trùng luôn đúng lúc.
   - Ghi Sheet vẫn chỉ qua «Áp dụng». Bước này đọc lại Sheet trước khi ghi (T-100), không có đường mới.
2. **Ô chọn nhiều (`st.multiselect`, tối đa 10)** thay cho cột tick trong bảng.
   - Bảng từ khóa T-125 là bảng chỉ đọc. Ô chọn hiện chữ thuần và có sẵn giới hạn 10.
   - Ô chọn hiện đúng chữ như trong bảng từ khóa. Chữ chuẩn hóa (NFC, gộp dấu cách) chỉ dùng trong đề xuất.
3. **Lọc hai lần.** Lần đầu ở trang Theo dõi (dựng ô chọn), lần sau trong `from_google_keywords`. Dữ liệu chuyển qua phiên không được tin.
4. **«Chữ» là chữ tiếng Việt hoặc a–z, không phải mọi chữ Unicode** (`0505f31`).
   - Bản đầu `523b0ce` nhận mọi ký tự loại «chữ» của Unicode. Tôi thấy bộ lọc đó cho lọt:
     - chữ trông giống chữ Latin («с» Cyrillic);
     - chữ viết từ phải sang trái;
     - «chữ» vô hình U+3164;
     - «chữ» trông như dấu câu: U+02BC giống «'», U+01C3 giống «!»;
     - chữ toàn chiều rộng.
   - Các ký tự đó làm hỏng mục đích «không có dấu câu, hiện nguyên văn». Bảng 186 chữ chặn hết.
   - Đổi lại, từ khóa có chữ ngoài tiếng Việt và a–z (chữ Trung, Hàn, «ü», «ñ»…) bị bỏ. Với website này việc đó rất hiếm. Muốn nới thì chỉ sửa `_keyword_letters()`.
5. **Dấu cách.**
   - Chỉ nhận dấu cách thường; nhiều dấu cách liền nhau được gộp làm một.
   - Tab, xuống dòng, dấu cách lạ (U+00A0, U+3000) làm **bỏ cả từ khóa**, không tự đổi thành dấu cách.
6. **Từ khóa trùng dòng kế hoạch có sẵn vẫn thành đề xuất**, kèm cảnh báo «trùng B-xxx» và không tick sẵn, giống T-098. Người dùng tự quyết.

## Đổi kỳ vọng ca test cũ (R5)

Không đổi ca test cũ nào. Ca `test_t125_tracking_page.py:541` kiểm nút giữ chỗ bị khóa. Ca này vẫn đúng: nút khóa cho tới khi chọn ít nhất một từ khóa.

## Bằng chứng

```text
# Windows 11, Python 3.12.15, ruff 0.16.10. Chạy trên đúng commit 0505f31 (git status sạch).
uv run pytest -q -p no:randomly tests/test_t127_dua_vao_ke_hoach.py
  65 passed

# 28 file liên quan:
#   - kế hoạch, T-098: test_plan_propose, test_plan_model, test_plan_parse, test_soi_loi_t098,
#     test_plan_ai
#   - T-100: test_plan_sync, test_plan_cache, test_t100_drafts_plan, test_soi_loi_t100,
#     test_la_chan_t100
#   - T-101: test_t101_plan_page, test_t101_home_page, test_soi_loi_t101
#   - T-103: test_t103_plan_prompt, test_soi_loi_t103, test_la_chan_t103
#   - T-109, T-113: test_soi_loi_t109, test_t109_website_status, test_t113_website_status
#   - T-125: test_t125_tracking_page, test_soi_loi_t125, test_t125_tho_may
#   - test_t127_dua_vao_ke_hoach, test_app_pages
#   - test quét cả cây mã nguồn: test_images_process, test_la_chan_t096, test_soi_loi_t034,
#     test_wordpress_release
uv run pytest -q -p no:randomly -rfEsxX <28 file trên>
  2249 passed, 1 skipped in 484.78s
  # 0 hỏng. 1 bỏ qua: ca symlink file của T-125 (máy Windows này chưa bật Developer Mode).

uv run ruff check .                     → All checks passed!
uv run ruff format --check <4 file>     → 4 files already formatted

# Quét bí mật:
#   - bản sao 4 file lấy từ 0505f31 (git show) ở thư mục nháp, PYTHONUTF8=1,
#     detect-secrets --all-files → 0 phát hiện;
#   - đối chứng: khóa AWS giả trong cùng thư mục → bắt được.
#   - Bản đầu báo nhầm «Secret Keyword» ở biến tên «secret» trong test; đã đổi thành «phone_text».
# Ký tự ẩn, CR, NFC (script ở thư mục nháp): 0 trong 4 file.
# Gộp thử: git merge-tree --write-tree với main cục bộ 7153f0a (đã có T-125, T-130, T-132)
#   → không xung đột. Từ 09fdad2, main không sửa file nào của phiếu này.
```

## Đối chiếu tiêu chí

| Yêu cầu | Đáp ứng | Test (`test_t127_dua_vao_ke_hoach.py`) |
|---|---|---|
| 1. Hàm trong `propose.py`: ≤ 10, không AI, kiểm trùng như T-098 | `from_google_keywords` | `test_keywords_become_add_proposals_from_search_console`, `test_at_most_ten_keywords_each_time`, `test_same_keyword_twice_in_one_batch_is_taken_once`, `test_warnings_like_table_proposals` (trùng B-012, trùng bài 5, cửa ngõ), `test_odd_input_gives_no_proposal` |
| 2. Bộ lọc chặt, câu báo cố định | `google_keyword`, `NOTE_GOOGLE_SKIPPED` | `test_strict_filter_keeps_plain_keywords` (8 ca), `test_strict_filter_drops_everything_else` (41 ca: dấu câu, công thức, Markdown, HTML, xuống dòng, tab, ký tự rộng 0, RLO, số điện thoại, email, `www`/`https`, chỉ số, rỗng, > 80, chữ trông giống, chữ vô hình, không phải chuỗi), `test_letters_are_vietnamese_or_a_to_z_only`, `test_dropped_keywords_are_only_counted` |
| 3. Nút: tick ≤ 10, sang Kế hoạch dạng đề xuất chờ duyệt, chữ thuần | `plan_box`, `take_google_keywords` | `test_picker_offers_only_keywords_that_pass_the_filter` (công thức, Markdown không có trong ô chọn; nút khóa), `test_picked_keywords_become_proposals_on_the_plan_page`, `test_picked_keywords_when_the_table_changes`, `test_hand_off_without_a_readable_plan_only_warns` |
| 4. Không vào lời dặn AI (LC-T120-13) | Không gọi AI ở bước này | `test_no_ai_in_this_step` (cây cú pháp của 2 hàm không gọi `from_ai`, `plan_changes`, `ContentWriter`, `AIRouter`, `complete`) |
| 5. Không lùi Kế hoạch, T-098, T-125, `test_app_pages` | 28 file liên quan | mục Bằng chứng |
| LC-T120-13: không ghi Sheet | Chỉ để đề xuất trong phiên; ghi qua «Áp dụng» có sẵn | ca bấm nút: `plan_proposals` có đề xuất, `no_network.count == 0` |
| LC-T120-15: test không gọi mạng | Bộ chặn mạng chung (`tests/conftest.py`, autouse) chặn mọi kết nối ở mọi ca. 3 ca trang còn đếm lời gọi client Google và WordPress (`no_network.count == 0`). Không thêm trang (`PAGES` không đổi). | 4 ca trang |
| LC-T120-24 | Lọc chặt; hiện nguyên văn để tick; ≤ 10 (`max_selections`, cắt ở trang, cắt trong hàm); không AI; nguồn «Search Console»; qua `PlanRow` và `check_proposals`; khi viết bài, từ khóa vào lời dặn AI như mọi từ khóa (T-098, không đổi) | các dòng trên |

## Rủi ro và điểm cần chú ý

- **Câu lệnh chỉ có chữ và dấu cách vẫn lọt** nếu ≤ 80 ký tự (ví dụ «bo qua huong dan viet quang cao»). LC-T120-24 đã chấp nhận rủi ro này: Google ẩn từ khóa hiếm, và từ khóa nằm trong khung dữ liệu của lời dặn AI như T-098.
- **Số điện thoại viết bằng chữ** («không chín không chín…») không bị nhận ra. Viết bằng số thì bị bỏ, kể cả khi tách nhóm như «0909 123 456».
- **Từ khóa có chữ ngoài tiếng Việt và a–z bị bỏ** (mục chọn 4).
- **Nút dùng `st.switch_page("views/plan.py")`.** Đổi tên file trang Kế hoạch thì phải sửa chỗ này; ca bấm nút sẽ bắt được.
- **Từ khóa đã chọn chỉ nằm trong phiên** cho tới khi trang Kế hoạch đọc. Nếu trang Kế hoạch chưa đọc được Sheet, danh sách bị bỏ kèm cảnh báo, người dùng chọn lại.

## Đề xuất

- Lá Chắn kiểm **đầy đủ** theo LC-T120-24, như phiếu ghi.
- Soi Lỗi kiểm rút gọn.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 · SL-T127-1 (2026-11-10)

| Mục | Nội dung |
|---|---|
| Lỗi | SL-T127-1 ([biên bản Soi Lỗi](T-127-soi-loi.md), Thấp). Nút «Đưa vào kế hoạch» kiểm trùng bài đã đăng bằng `cached_index()`: bản lưu trên máy cũ bao lâu cũng dùng, không tải lại, không báo |
| Commit | `8ce3383` (mã và test); báo cáo lượt 2 ở commit ngay sau |
| Kết quả | Đã sửa theo đúng gợi ý của Soi Lỗi |

### Tóm tắt (cho chủ dự án)

- Khi đưa từ khóa sang Kế hoạch, phần mềm so với danh sách bài đã đăng **còn mới**, giống cách nạp kế hoạch:
  - danh sách trên máy cũ hơn 6 giờ thì tải lại từ website;
  - không tải được thì đề xuất có dòng báo «Chưa tải được danh sách bài đã đăng…»;
  - chưa kết nối WordPress thì có dòng báo «chưa kết nối».
- Danh sách còn mới thì không gọi website, như trước.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/plan.py` | `take_google_keywords`: `index, notice = fresh_index()` thay cho `index = cached_index()`. Câu báo `notice` (nếu có) vào ghi chú đề xuất, sau dòng «Từ khóa chọn ở trang 📈 Theo dõi…». Đúng cách của `read_source` và `read_sheet_link` (T-098) |
| `tests/test_soi_loi_t127.py` | Gỡ dấu `xfail(strict=True)` của ca SL-T127-1, vì ca đã XPASS. Thân test không đổi |
| `tests/test_t127_dua_vao_ke_hoach.py` | Thêm 1 ca. Danh sách trên máy lưu cách đây 7 giờ; website trả thêm bài 99 «Cửa kéo mẫu 01». Kết quả mong đợi: tải lại đúng 1 lần, đề xuất «cửa kéo mẫu 01» có cảnh báo trùng bài 99, không có câu báo về danh sách |

### Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới |
|---|---|---|
| `test_soi_loi_t127.py::test_sl_t127_1_stale_published_list_is_refreshed_or_told` | `xfail(strict=True)` | Bỏ dấu (đã XPASS); thân test không đổi |

### Bằng chứng

```text
# Windows 11, Python 3.12.15, ruff 0.16.10. Chạy trên đúng commit 8ce3383 (git status sạch).
uv run pytest -q -p no:randomly tests/test_soi_loi_t127.py tests/test_t127_dua_vao_ke_hoach.py
  trước khi gỡ dấu: 1 failed (XPASS strict của SL-T127-1), 93 passed
  sau khi gỡ dấu:   95 passed

# Đối chứng (script ở thư mục nháp; trả file về đúng byte, kiểm bằng SHA-256):
#   cho take_google_keywords dùng lại cached_index()
#   → 2 ca SL-T127-1 hỏng (ca của Soi Lỗi và ca mới của Thợ Máy).

# 34 file liên quan:
#   - nơi gọi propose.py và seo_app.plan;
#   - trang Kế hoạch: test_app_pages, test_t101_*, test_t113_website_status,
#     test_soi_loi_t113, test_la_chan_t113;
#   - trang Theo dõi: test_t125_tracking_page, test_soi_loi_t125, test_t125_tho_may;
#   - test_t127_dua_vao_ke_hoach, test_soi_loi_t127;
#   - test quét cả cây mã nguồn.
uv run pytest -q -p no:randomly -rfEsxX <34 file>
  2484 passed, 1 skipped in 612.59s
  # 0 hỏng. 1 bỏ qua: ca symlink file của T-125 (máy Windows này chưa bật Developer Mode).

uv run ruff check .                     → All checks passed!
uv run ruff format --check <3 file>     → đã đúng khuôn
# Quét bí mật: 3 file lấy từ 8ce3383, có khóa giả đối chứng (bắt được) → 0 phát hiện.
# Ký tự ẩn, CR, NFC: 0.
# Gộp thử: git merge-tree với main cục bộ 7153f0a → không xung đột.
#   main không sửa file nào của phiếu này.
```

### Rủi ro và điểm cần chú ý

- **Sau khi bấm «Đưa vào kế hoạch», trang Kế hoạch có thể gọi website** để đọc danh sách bài, khi bản trên máy cũ hơn 6 giờ. Trang hiện vòng chờ «Đang tải danh sách bài đã đăng trên website…». Đây là việc người dùng bấm, giống hai đường đề xuất T-098.
- Lời gọi chỉ chạy khi có từ khóa vừa chuyển sang. Khóa chuyển trang được lấy ra (`pop`) trước khi tải, nên tải lại trang không chạy lại. Mở trang như thường không thêm lời gọi nào.

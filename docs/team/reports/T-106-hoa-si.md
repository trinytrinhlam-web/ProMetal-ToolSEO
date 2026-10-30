# Báo cáo T-106 + T-108 · Trang Kết nối WordPress: cảnh báo quyền `unfiltered_html`, bỏ ô chọn ảnh ở bài nháp thử

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | T-106 (Thấp; giao qua tin nhắn của Chỉ Huy B ngày 2026-10-30, **chưa có file phiếu** trong `docs/team/tickets/`), [T-108](../tickets/T-108-ket-noi-wordpress-bo-o-anh-tao-thu.md) (Trung bình, chặn đóng Giai đoạn 3) |
| Ngày nộp | 2026-10-30 09:40 |
| Nhánh | `team/T-106` (từ `97188da` = `main` trên máy `0122d4b` + T-093) |
| Kết quả | Hoàn thành: T-108 yêu cầu 1–4 (LC-T093-1 đã đóng, gỡ `xfail`), T-106 yêu cầu 1–4. Đổi kỳ vọng 2 test cũ của Soi Lỗi T-044 (8 ca) theo phương án A, **Chỉ Huy duyệt A 30/10** (R5, mục «Đổi test cũ») |

## Tóm tắt (cho chủ dự án)

- **Bài nháp thử ở trang Kết nối WordPress không còn ảnh (T-108).** Trước đây ô «Ảnh đại diện» tải **nguyên file** bạn chọn lên thư viện Media của website. File đó còn số seri máy, tên chủ máy, ảnh nhỏ trước khi cắt…, và xem được công khai ngay. Nay mục này chỉ tạo bài nháp chữ để kiểm kết nối. Muốn thử gửi ảnh thì dùng «Gửi nháp» ở trang Soạn bài: ảnh ở đó đã được làm sạch trước khi lên website.
- **Cảnh báo khi tài khoản WordPress không giữ được ảnh còn GPS (T-106).** Bấm «Kiểm tra kết nối»:
  - nếu tài khoản thiếu một quyền của WordPress (`unfiltered_html`), app báo vàng: ảnh trong bài có thể mất vị trí GPS khi xem trên điện thoại, kèm cách sửa (dùng vai **Biên tập viên**, không nâng lên Quản trị viên);
  - nếu website không cho biết quyền, app báo xanh một câu trung tính;
  - nếu tài khoản có quyền thì không hiện gì thêm.
- Tài khoản Biên tập viên hiện tại của bạn có quyền này, nên bình thường bạn sẽ không thấy cảnh báo.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/wordpress.py` | T-108: bỏ ô chọn ảnh, ô alt, lệnh `upload_media`, dòng «Ảnh đại diện đã tải lên»; `create_draft(..., featured_media=None)` (`:185`); thêm lời dặn dùng «Gửi nháp» ở Soạn bài (`:158-162`). T-106: `unfiltered_html_note` (`:33`), hiện sau dòng quyền ở mục 1 (`:126-129`) |
| `README.md` | Đoạn tạo thử (`:115`): bài nháp thử chỉ có chữ; thử ảnh thì dùng «Gửi nháp» ở Soạn bài |
| `tests/test_la_chan_t093.py` | Gỡ dấu `xfail` LC-T093-1 (chỉ xóa 4 dòng dấu, thân test giữ nguyên) |
| `tests/test_t106_trang_ket_noi.py` | Mới: 15 ca (T-106: có quyền, thiếu quyền theo vai, không biết, dữ liệu lạ; T-108: không còn ô ảnh, bài thử không tải ảnh) |
| `tests/test_soi_loi_t044.py` | Đổi phần kỳ vọng của 2 test (8 ca) theo phương án A, Chỉ Huy duyệt A 30/10 (mục «Đổi test cũ») |

File phiếu T-108 **không** đưa vào nhánh (Chỉ Huy commit phiếu lên `main`, tránh xung đột khi gộp); chỉ đọc ở checkout chính.

## T-108 · Bỏ ô chọn ảnh ở «Tạo thử một bài nháp» (LC-T093-1)

| # | Yêu cầu | Cách làm | Test |
|---|---|---|---|
| 1 | Bỏ ô chọn ảnh và lệnh tải ảnh; nút tạo thử vẫn tạo bài nháp chữ thuần | Xóa `st.file_uploader`, ô «Mô tả ảnh (alt)», `client.upload_media`, dòng địa chỉ ảnh. Bài tạo bằng `create_draft` như cũ, `featured_media=None` | `test_draft_form_has_no_image_field` (không `file_uploader`, ô nhập duy nhất là «Tiêu đề», mã nguồn không còn `upload_media`/`file_uploader`); `test_test_draft_is_text_only_and_never_uploads` (client thật + WordPress giả: `file_uploader` giả không bao giờ được gọi, **0 request** tới `/wp/v2/media`, đúng 1 lệnh tạo bài `status: draft`, `featured_media` rỗng, nội dung 2 đoạn); LC-T093-1 của Lá Chắn (XPASS → gỡ dấu, nay qua) |
| 2 | README đoạn tạo thử nói đúng | `README.md:115`: «tạo thử một bài nháp chỉ có chữ, không có ảnh… Muốn thử gửi ảnh thì dùng «Gửi nháp» ở trang Soạn bài: ảnh ở đó đã qua bước làm sạch…». Trên trang cũng có câu đó (`wordpress.py:160-161`) | `test_draft_form_has_no_image_field` (câu ««Gửi nháp» ở trang Soạn bài») |
| 3 | Không lùi test trang Kết nối, T-001, T-087 cũ | Chạy mọi file test mở trang Kết nối (`grep -l 'views/wordpress.py'`: 8 file) + `test_app_pages.py`, `test_phase2_fixes.py` (sửa lỗi T-001), `test_soi_loi_t060.py`. T-087 chỉ là README, không có test riêng | Mục Bằng chứng. 8 ca của Soi Lỗi T-044 đi qua nhánh tải ảnh đã bỏ: đổi kỳ vọng theo phương án A (mục «Đổi test cũ») |
| 4 | Cùng nhánh với T-106, một báo cáo | Nhánh `team/T-106`, báo cáo này | — |

### Đổi test cũ (R5): Chỉ Huy duyệt A 30/10

Hai test trong `tests/test_soi_loi_t044.py` (Soi Lỗi T-044) chạy qua nhánh tải ảnh mà T-108 đã bỏ, nên hỏng 8 ca trên code mới. Tôi hỏi Chỉ Huy, đề xuất A (giữ tên ca và tham số độc hại, chỉ đổi kỳ vọng) hay B (xóa). **Chỉ Huy duyệt A 30/10.** Không xóa ca nào, không `skip`, không `xfail`; tên ca, bộ tham số, đoạn dựng website giả và `file_uploader` giả giữ nguyên.

| Ca (8 tham số) | Điều kiện cũ | Điều kiện mới |
|---|---|---|
| `test_uploaded_image_url_line_is_plain` × 6 (`source_url`: `https://evil.example/wp-content/uploads/anh.jpg`, `www.evil.example/anh.jpg`, `[anh](https://evil.example/a.jpg)`, `<https://evil.example/a.jpg>`, `<img src=x onerror="alert(1)">`, `ban@evil.example`) | Điền ô «Mô tả ảnh»; trang có đúng 1 dòng «Ảnh đại diện đã tải lên: {source_url}» hiện chữ thường; lệnh tạo nháp có `"featured_media": 9`, `status: draft`; tiêu đề hiện chữ thường | `file_uploader` giả **vẫn trả file**, website giả **vẫn nhận ảnh** (trả `source_url` độc hại). Bấm «Tạo bài nháp» (bỏ bước điền ô alt, ô không còn) thì: **0 request** tới `/wp/v2/media`; không dòng nào có «Ảnh đại diện»; `source_url` và tên file `anh cua.jpg` không có trong chữ nào trên trang (cả bản Markdown lẫn chữ người đọc thấy); đúng 1 lệnh tạo nháp, `status: draft`, **không có** `featured_media`; tiêu đề vẫn hiện chữ thường («Đã tạo bài nháp #42: **Bài [x](https://evil.example)**»); `assert_page_plain` |
| `test_upload_error_with_hostile_filename_is_plain` × 2 (`sai-duoi`: `www.evil.example.exe`; `rong`: `[x](https:⁄⁄evil.example)ban@evil.example.png`, 0 byte) | 1 câu lỗi chép tên file «File '…'» hiện chữ thường; không request nào tới `/wp/v2/` | `file_uploader` giả **vẫn trả file tên độc hại**; thêm website giả nhận ảnh và nhận lệnh tạo nháp. Bấm «Tạo bài nháp» thì: không câu lỗi; bài nháp chữ tạo được («Đã tạo bài nháp #42: **Bài thử**»); tên file không có trong chữ nào trên trang; **0 request** tới `/wp/v2/media`; đúng 1 lệnh tạo nháp, `status: draft`, không có `featured_media`; `assert_page_plain` |

**Điều kiện 1 của Chỉ Huy (ca phải chứng minh không lệnh tải ảnh nào được gửi, không chỉ «không thấy ô»):** website giả nhận ảnh nên nếu trang gửi lệnh tải thì lệnh thành công và nằm trong `fake_wp.requests`. Ca kiểm số lệnh tới `/wp/v2/media` bằng 0 **và** lệnh tạo nháp có đi (đúng 1), nên lần bấm chắc chắn đã chạy tới website. Đối chứng: chạy 8 ca mới trên trang cũ (`git show HEAD:app/views/wordpress.py`, còn ô ảnh, bản sao trong thư mục tạm): **8 failed**.

**Bảo mật (W2, F1, U1):** trang không còn đường nào ghi lên thư viện Media (W2: chỉ còn `create_draft` trạng thái nháp, không đụng bài, ảnh có sẵn). Trang không còn nhận file từ máy người dùng (F1). Không thêm `unsafe_allow_html` (U1).

## T-106 · Cảnh báo quyền `unfiltered_html` trên trang Kết nối

`ConnectionInfo.can_unfiltered_html` (T-091) chỉ có đúng/sai. Vì vậy trạng thái «không biết» do giao diện suy ra (`unfiltered_html_note`, `wordpress.py:33`):

| Trạng thái | Khi nào | Trang hiện | Test |
|---|---|---|---|
| Có quyền | `can_unfiltered_html is True` | Không hiện gì thêm (yêu cầu 3). REST trả quyền theo vai, không thấy `DISALLOW_UNFILTERED_HTML`, nên «có» chỉ là dấu hiệu tốt; không viết câu «chắc chắn giữ GPS» | `test_account_with_unfiltered_html_shows_nothing_more` (editor, administrator: không `st.warning`, không `st.info`) |
| Thiếu, vai thấp hơn Biên tập viên | `False`, tài khoản viết được bài, vai không phải `editor`/`administrator` | `st.warning`: «Ảnh trong bài có thể **mất vị trí GPS khi xem trên điện thoại**…» + «Cách sửa: nhờ người quản trị website đặt tài khoản này ở vai trò **Biên tập viên (Editor)**. Không cần, và không nên, nâng lên Quản trị viên.» | `test_author_without_unfiltered_html_is_told_to_use_editor` (3 ca qua client thật: `false`, không có khóa, chuỗi `"true"`) |
| Thiếu, đã là Biên tập viên trở lên | `False`, vai có `editor` hay `administrator` | `st.warning`: cùng câu mất GPS + «website đã bỏ quyền này khỏi vai trò (thường do plugin quản lý quyền hoặc cấu hình website): báo người làm web xem lại. Đừng nâng tài khoản lên Quản trị viên chỉ vì việc này.» (khuyên Editor lúc này là sai vì đã là Editor) | `test_editor_without_unfiltered_html_is_told_site_disables_it` (editor, administrator) |
| Không biết | Website không cho biết quyền viết bài (câu trả lời thiếu `capabilities`, sai kiểu, hay tài khoản quá thấp như `subscriber`), hoặc đối tượng kết nối không có trường này (Ghi nhận 4 Soi Lỗi T-091) | `st.info` trung tính: «Chưa biết ảnh trong bài có giữ được vị trí GPS khi xem trên điện thoại không: website chưa cho biết đủ quyền của tài khoản này. Bấm «Kiểm tra kết nối» lại sau khi tài khoản có quyền viết bài.» | `test_unknown_permissions_give_neutral_note` (3 ca qua client thật), `test_old_connection_object_without_the_field_is_unknown` |

- **Yêu cầu 4 (không in tên đăng nhập, mật khẩu, đường dẫn):** cả ba câu là chữ cố định, không ghép dữ liệu nào. Test `assert_no_account_details` kiểm từng câu không chứa tên đăng nhập, mật khẩu ứng dụng, tên hiển thị, địa chỉ website, `/wp-json`.
- **U1:** hiện bằng `st.warning`/`st.info` (Markdown thường). Mỗi trang dựng trong test qua `assert_page_plain` của Soi Lỗi T-044: không link, không HTML. Trang vẫn không có `unsafe_allow_html` (`test_page_still_has_no_html`).
- **Dữ liệu lạ:** vai trò sai kiểu (số, `None`, danh sách) không làm vỡ trang, vẫn nhận ra `editor` (`test_odd_roles_do_not_crash_and_editor_is_found`).
- **Không dùng `ConnectionInfo.unfiltered_html_status`** (câu Thợ Máy soạn sẵn ở T-091). Câu đó chỉ có một dạng: khuyên «dùng vai trò Biên tập viên» cả khi tài khoản đã là Biên tập viên, và không có dạng «không biết». Phiếu cấm sửa `seo_app/**` nên tôi viết câu ở giao diện. Xem Đề xuất.

## Bằng chứng

```
# Trước khi gỡ dấu:
$ PYTHONUTF8=1 uv run pytest "tests/test_la_chan_t093.py::test_lc_t093_1_wordpress_page_upload_follows_decision_2a"
[XPASS(strict)] LC-T093-1: trang Kết nối WordPress tải nguyên file ảnh, bỏ qua quyết định 2A

# Mọi file test mở trang Kết nối (grep -l 'views/wordpress.py\|"wordpress.py"' tests/: 8 file,
# kể cả test_la_chan_t093.py) + test_app_pages.py, test_phase2_fixes.py (sửa lỗi T-001),
# test_soi_loi_t060.py, test_la_chan_t071.py (upload_media ở client) + test mới: 13 file
$ PYTHONUTF8=1 uv run pytest tests/test_app_pages.py tests/test_app_wordpress.py \
    tests/test_app_t044_safe_text.py tests/test_soi_loi_t044.py tests/test_soi_loi_t031.py \
    tests/test_soi_loi_t085.py tests/test_soi_loi_t088.py tests/test_soi_loi_t060.py \
    tests/test_t041_seo_ui.py tests/test_la_chan_t071.py tests/test_phase2_fixes.py \
    tests/test_la_chan_t093.py tests/test_t106_trang_ket_noi.py -q -rxXf
XFAIL tests/test_la_chan_t093.py::test_lc_t093_2_uploaded_images_attached_to_new_draft
XFAIL tests/test_la_chan_t093.py::test_lc_t093_3_heic_decoding_not_exposed_to_libheif_1_23_6
2733 passed, 2 xfailed in 1005.21s (0:16:45)
# Code của commit nộp, chạy 09:20 → 09:37 (giờ máy, `date`). 2 xfail là LC-T093-2, -3 (phiếu khác).
# Trước khi đổi 2 test T-044, cùng bộ file: 8 failed (đúng 8 ca ở mục «Đổi test cũ»), 2725 passed.

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/wordpress.py README.md tests/test_t106_trang_ket_noi.py \
    tests/test_soi_loi_t044.py tests/test_la_chan_t093.py docs/team/reports/T-106-hoa-si.md
# 1 kết quả: tests/test_soi_loi_t044.py:39 `PASSWORD = "mat-khau-thu-123"` (mật khẩu thử có sẵn
# từ trước, dòng không đổi); không có gì mới.
```

`uv run ruff format --check app/views/wordpress.py` báo một chỗ có từ trước (`st.success(...)` ở mục 1, bản `HEAD` cũng báo y hệt); phần tôi viết không bị báo.

**Thử làm hỏng code để xem test mới có bắt được không** (bản sao worktree, mỗi lần một chỗ, chạy `tests/test_t106_trang_ket_noi.py`):

| Chỗ làm hỏng trong `wordpress.py` | Kết quả |
|---|---|
| Không hiện câu nào | bắt được (10 hỏng) |
| «Không biết» thành cảnh báo mất GPS | bắt được (3) |
| Có quyền vẫn báo | bắt được (2) |
| Bỏ câu riêng cho tài khoản đã là Biên tập viên | bắt được (3) |
| Khuyên «hoặc Quản trị viên (Administrator)» | bắt được (3) |
| Chép tên đăng nhập vào câu báo | bắt được (5) |
| Vai trò sai kiểu làm vỡ trang | bắt được (1) |
| Bài thử gửi kèm ảnh đại diện | bắt được (1) |
| Bỏ lời dặn «Gửi nháp» ở Soạn bài | bắt được (1) |
| Không làm hỏng gì | 15 qua |

Script `mutate_t106.py` và kết quả để ở thư mục ghi chú chung của đội, mục `T-106-hoa-si-scripts` (ngoài repo).

**Không mở app thật:** cảnh báo chỉ hiện sau «Kiểm tra kết nối» với website trả quyền tài khoản, mà phiếu cấm đụng website thật. Mọi trường hợp đã chạy bằng AppTest qua client WordPress thật với WordPress giả.

**Chủ dự án tự kiểm tra:** mở app → Kết nối WordPress → «Kiểm tra kết nối». Với tài khoản Biên tập viên hiện tại: không có cảnh báo vàng về GPS. Mục 3 «Tạo thử một bài nháp» chỉ còn Tiêu đề, Nội dung, Chuyên mục, Thẻ, không còn ô chọn ảnh.

## Đối chiếu tiêu chí xong

**T-108**
- [x] Yêu cầu 1: bỏ ô chọn ảnh và lệnh tải ảnh, bài nháp chữ vẫn tạo được (`test_test_draft_is_text_only_and_never_uploads`, LC-T093-1)
- [x] Yêu cầu 2: README đoạn tạo thử (`README.md:115`)
- [x] Yêu cầu 3: test trang Kết nối, T-001 cũ qua; 2 test T-044 đổi kỳ vọng theo phương án A, Chỉ Huy duyệt A 30/10
- [x] Yêu cầu 4: cùng nhánh `team/T-106`, một báo cáo
- [x] Gỡ `xfail` LC-T093-1 sau XPASS, chỉ xóa dấu
- [x] Test liên quan + `uv run ruff check .` (mục Bằng chứng)

**T-106** (theo tin nhắn giao việc của Chỉ Huy B, chưa có file phiếu)
- [x] 1. Thiếu quyền: cảnh báo dễ hiểu (ảnh mất GPS trên điện thoại), cần vai Biên tập viên, không khuyên Quản trị viên
- [x] 2. Không biết: câu trung tính
- [x] 3. Có quyền: không hiện gì thêm
- [x] 4. Không in tên đăng nhập, mật khẩu, đường dẫn
- [x] Test `AppTest` cho các trường hợp; không sửa `seo_app/**`, `config/**`

## Rủi ro và điểm cần chú ý

- «Không biết» suy từ `can_edit_posts`: tài khoản viết được bài mà website trả `capabilities` thiếu riêng khóa `unfiltered_html` thì coi là **thiếu** (WordPress liệt kê đủ quyền của vai, thiếu khóa nghĩa là không có). Đây là suy luận theo cách `check_connection` đọc (`client.py:799`), không thử trên website thật.
- Câu cảnh báo mục 1 có sẵn từ trước («Nên dùng tài khoản có vai trò Biên tập viên (Editor) hoặc Quản trị viên (Administrator)», `wordpress.py:123-124`, hiện khi thiếu quyền viết bài hay tải ảnh) vẫn nhắc Quản trị viên. Không đổi vì ngoài phạm vi (xem Đề xuất).

## Đề xuất

- **Họa Sĩ hoặc Thư Ký (phiếu nhỏ):** câu cảnh báo có sẵn «… Biên tập viên (Editor) hoặc Quản trị viên (Administrator)» (`wordpress.py:123-124`) trái với quyết định dùng tài khoản Biên tập viên riêng (CLAUDE.md, Lá Chắn T-059). Nên bỏ «hoặc Quản trị viên». Cần grep test ghim câu này trước khi đổi.
- **Thợ Máy (khi được sửa `seo_app/wordpress/client.py`):** `ConnectionInfo.can_unfiltered_html` nên có giá trị «không biết» (`None` khi `capabilities` thiếu hay sai kiểu), để giao diện không phải suy từ `can_edit_posts`. Khi đó cũng bỏ hay sửa `unfiltered_html_status` cho khớp ba câu ở trên.
- **Thư Ký:** README bước 10 («Đúng thì thấy…») có thể thêm một dòng: không thấy cảnh báo vàng «Ảnh trong bài có thể mất vị trí GPS…»; thấy thì làm theo câu trong cảnh báo.

## Câu hỏi cho chủ dự án

Không có.

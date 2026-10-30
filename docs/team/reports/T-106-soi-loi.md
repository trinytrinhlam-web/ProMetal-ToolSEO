# Báo cáo T-106 + T-108 · Trang Kết nối WordPress: cảnh báo `unfiltered_html`, bài nháp thử không ảnh · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-106 (giao qua tin nhắn Chỉ Huy B 30/10, chưa có file phiếu), [T-108](../tickets/T-108-ket-noi-wordpress-bo-o-anh-tao-thu.md) (đọc ở checkout chính) |
| Nhánh | `team/T-106` (đầu nhánh `c77cace` = `main` `0122d4b` + T-093 + T-106/T-108); `main` mới nhất trên máy là `0122d4b`, tổ tiên của nhánh: gộp là tua thẳng, không xung đột |
| Ngày nộp | 2026-10-30 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T106-1, SL-T108-1). **Không lỗi nào bắt buộc sửa trước Lá Chắn**; LC-T093-1 (Trung bình) đã đóng thật |

## Tóm tắt (cho chủ dự án)

- **Trang Kết nối WordPress không còn đường nào tải ảnh lên website.** Tôi thử cả trang với một ô chọn file giả luôn đưa ảnh còn số seri máy: trang không hỏi file, không lệnh nào tới thư viện Media. Nút «Tạo bài nháp» vẫn tạo đúng **một bài nháp chữ**.
- **Cảnh báo quyền `unfiltered_html` đúng cả 3 trường hợp** (18 kiểu tài khoản, qua client thật với website giả): có quyền thì im lặng; thiếu thì cảnh báo vàng dễ hiểu (ảnh có thể mất GPS trên điện thoại), khuyên vai Biên tập viên, hoặc báo người làm web nếu đã là Biên tập viên; website không cho biết thì một câu xanh trung tính. Câu báo không có tên đăng nhập, mật khẩu, địa chỉ website.
- **2 lỗi nhỏ (Thấp), không cần sửa trước Lá Chắn:**
  1. Với tài khoản Cộng tác viên, trang hiện **hai lời khuyên ngược nhau**: câu mới «không nên nâng lên Quản trị viên», câu cũ ngay trên nó «nên dùng… Biên tập viên hoặc Quản trị viên». Câu cũ có từ trước, nên bỏ chữ «hoặc Quản trị viên».
  2. README dòng đầu (Trạng thái) vẫn ghi trang Kết nối «tạo bài nháp có ảnh đại diện».
- **Việc của bạn:** không có. Tài khoản Biên tập viên hiện tại có quyền này nên bạn sẽ không thấy cảnh báo mới.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t106.py` | Mới: 26 ca (23 qua, 3 `xfail(strict=True)`: SL-T106-1 2 ca, SL-T108-1 1 ca). Website giả riêng `_Site` (adapter `requests`, ghi mọi lệnh gửi đi, nhận cả lệnh tải ảnh để nếu trang lỡ tải thì lệnh đi trót lọt), ô chọn file giả luôn trả ảnh có số seri. Không dùng `FakeWordPress`, hàm mở trang hay bảng kỳ vọng của Họa Sĩ |
| `docs/team/reports/T-106-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác. Không gọi website thật (bộ chặn mạng của `tests/conftest.py` bật suốt).

## Kiểm theo yêu cầu

### 1. Trang Kết nối không còn đường tải ảnh

- **Đọc cây cú pháp** `app/views/wordpress.py`: lệnh gọi client đúng 4 lệnh `check_connection`, `list_categories`, `list_tags`, `create_draft`; không có `file_uploader`, `camera_input`, `upload_media`, `upload_media_file`, `_post_media`, `create_draft_with_images`, `set_featured_image`, `_request`, `getvalue`, `requests`. `create_draft` không nhận `**kwargs`, `featured_media` chỉ là `None`.
- **Cả `app/`**: lệnh tải ảnh chỉ còn `create_draft_with_images` ở `app/views/write.py` («Gửi nháp» của Soạn bài, ảnh đã qua `make_web_image`). `app/views/plan.py` có `file_uploader` nhưng là đọc file kế hoạch trên máy, không gửi lên website.
- **Chạy cả trang** (kiểm kết nối → tải chuyên mục, thẻ → tạo nháp có tiêu đề `<b>`, `[gallery]`, nội dung có `<img onerror>`, chọn chuyên mục, thẻ) với ô chọn file giả luôn trả ảnh `IMG_0001 so seri.jpg`: ô chọn file **không được gọi lần nào**; mọi lệnh gửi đi thuộc 6 đường đọc / tạo bài; **đúng 1 lệnh ghi** `POST /wp/v2/posts`; không chữ nào của ảnh giả (`SERIAL-T106`, tên file, `uploads`) lên trang.

### 2. Nút tạo thử vẫn tạo bài nháp chữ, đúng `draft`

Thân lệnh tạo: `status` `"draft"`, khóa chỉ trong `status`, `title`, `content`, `categories`, `tags` (không `featured_media`), chuyên mục `[3]`, thẻ `[7]` đúng mục đã chọn; nội dung không còn `<img`, tiêu đề không còn `<b>`. Trang báo «Đã tạo bài nháp #42». Bấm tạo nháp sau khi kiểm kết nối: câu báo GPS giữ nguyên, vẫn 1 lệnh ghi, 0 lần hỏi file.

### 3. Cảnh báo `unfiltered_html`: 3 trường hợp

18 kiểu tài khoản, qua `check_connection` thật (website giả trả `users/me` khác nhau):

| Trường hợp | Kiểu tài khoản thử | Trang hiện |
|---|---|---|
| Có quyền | editor, administrator, author được plugin cấp thêm (`unfiltered_html: true`) | Không câu nào về GPS |
| Thiếu, vai thấp | author (không khóa, `false`, `1`, `"true"`), contributor (Cộng tác viên lõi) | `st.warning`: mất GPS khi xem trên điện thoại, khuyên **Biên tập viên (Editor)**, «không nên nâng lên Quản trị viên» |
| Thiếu, đã là Biên tập viên trở lên | editor `false`, administrator thiếu khóa, author + editor | `st.warning`: mất GPS, báo **người làm web**, «Đừng nâng tài khoản lên Quản trị viên» |
| Không biết | thiếu `capabilities`, `null`, danh sách, chữ, `{}`, subscriber, `edit_posts: "true"` | `st.info` «Chưa biết…», không nói mất GPS |

- Mọi câu: không có tên đăng nhập, mật khẩu ứng dụng (có và không dấu cách), địa chỉ website, tên site, tên hiển thị, `wp-json`, `http`, `](`, `<`, chữ «Administrator».
- Vai trò lạ từ website (`[x](https://evil.example)`, `<b>editor</b>`, `editor` + ký tự rộng 0) không thành «editor» và không vào câu báo.
- Câu dễ hiểu. Không câu mới nào khuyên nâng lên Quản trị viên; **nhưng câu cũ cùng trang thì có**, xem SL-T106-1.

### 4. R5: 2 ca T-044 và `xfail` LC-T093-1

- **`tests/test_soi_loi_t044.py`** (`git diff 97188da..c77cace`): chỉ đổi thân 2 test; khối tham số (`SOURCE_URLS` 6 địa chỉ độc hại, 2 file tên độc hại `sai-duoi`, `rong`) giữ nguyên, `fake_file_uploader` vẫn trả file độc hại, website giả vẫn nhận ảnh. Đối chiếu điều kiện Chỉ Huy duyệt (phương án A):

  | Điều kiện | `test_uploaded_image_url_line_is_plain` (6) | `test_upload_error_with_hostile_filename_is_plain` (2) |
  |---|---|---|
  | Giữ file độc hại | Có | Có |
  | Không lệnh nào tới `/wp/v2/media` | Có | Có |
  | Không dòng ảnh | Có (không markdown nào có «Ảnh đại diện») | Gián tiếp: 0 lệnh media nên không có địa chỉ ảnh để hiện |
  | `featured_media` rỗng | Có | Có |
  | Tên file, địa chỉ ảnh không lên trang | Có (cả chữ Markdown lẫn chữ người đọc thấy) | Tên file: có; địa chỉ ảnh: gián tiếp như trên |
  | Bài nháp chữ vẫn tạo được | Có (1 lệnh `draft`, câu «Đã tạo bài nháp #42») | Có |

  Phần bỏ đi (ô alt, dòng «Ảnh đại diện đã tải lên», câu lỗi chép tên file) là phần trang không còn. `assert_page_plain` giữ ở cả 2. **Đúng điều kiện duyệt.**
- **`tests/test_la_chan_t093.py`**: chỉ xóa 4 dòng dấu `xfail` của LC-T093-1, thân test giữ nguyên; ca qua (trang không còn hỏi file nên không lệnh tải nào). `xfail` LC-T093-2, -3 (phiếu khác) giữ nguyên. **Đúng R5.**
- Không test cũ nào khác bị đổi (`git diff --stat 97188da..c77cace -- tests/`: 2 file trên + file test mới).

### 5. Không lùi test trang Kết nối, T-001, T-087; README

- Test ghim câu, nút cũ: chỉ 2 ca T-044 trên (đã duyệt). Chữ «Ảnh đại diện đã tải lên» còn trong lời mô tả đầu `test_soi_loi_t044.py` và lời mô tả một ca `test_soi_loi_t060.py`, không phải phần kiểm.
- T-087 là README «Chọn ảnh cho bài»: không đổi.
- README đoạn tạo thử (`README.md:115`) khớp chữ trên trang (`wordpress.py:158-162`). **Dòng Trạng thái (`README.md:7`) chưa khớp**: SL-T108-1.
- Chạy (mục 6): mọi file mở trang Kết nối, `test_app_pages.py`, `test_phase2_fixes.py` (sửa lỗi T-001), file client WordPress liên quan.

### 6. Gộp thử với `main` mới nhất trên máy

`main` trên máy là `0122d4b` (`git merge-base --is-ancestor main HEAD`: đúng), nên gộp là tua thẳng, `git merge-tree` không xung đột. Chạy trên đúng nội dung nhánh (bản sao từ `HEAD` + file test của tôi), 19 file chia 3 phần song song: **3.261 passed, 5 xfailed, 0 failed** (18 / 783 / 2.460 passed). 5 xfail: 3 ca của tôi, LC-T093-2 và LC-T093-3 (phiếu khác).

- Phần 1: `test_app_pages.py` (mở mọi trang).
- Phần 2: `test_app_wordpress.py`, `test_app_t044_safe_text.py`, `test_soi_loi_t044.py`, `test_soi_loi_t031.py`, `test_t106_trang_ket_noi.py`, `test_soi_loi_t106.py`, `test_la_chan_t093.py`.
- Phần 3: `test_soi_loi_t085.py`, `test_soi_loi_t088.py`, `test_soi_loi_t060.py`, `test_t041_seo_ui.py`, `test_la_chan_t071.py`, `test_phase2_fixes.py` (T-001), `test_prompt_data_frames.py` (T-001), `test_wordpress_client.py`, `test_wordpress_t085.py`, `test_t091_don_client_wordpress.py`, `test_soi_loi_t091.py`.

### Đột biến (đo sức test mới)

12 đột biến trên `app/views/wordpress.py` (script `mutate106.py`), mỗi lần chạy `tests/test_soi_loi_t106.py`: **12/12 bị bắt**.

| Đột biến | Ca bắt đầu tiên |
|---|---|
| P1 không hiện câu nào | `author-thieu` |
| P2 bỏ nhánh «không biết» theo quyền viết bài | `khong-capabilities` |
| P3 bỏ câu riêng cho Biên tập viên trở lên | `editor-bi-bo` |
| P4 coi Tác giả có quyền như Biên tập viên | `author-thieu` |
| P5 chỉ hiện câu cảnh báo, bỏ câu «không biết» | `khong-capabilities` |
| P6 câu báo chép tên đăng nhập | `author-thieu` |
| P7 «không biết» thành cảnh báo | `khong-capabilities` |
| P8 có quyền vẫn báo | `editor-co` |
| P9 khuyên thêm «hoặc Quản trị viên (Administrator)» | `author-thieu` |
| P10 bài thử gửi kèm ảnh đại diện | ca đọc cây cú pháp; ca chạy cả trang cũng bắt |
| P11 thêm lại ô chọn ảnh và `upload_media` | như trên |
| P12 tải ảnh qua `_post_media` | như trên |

P10–P12 chạy riêng ca chạy cả trang (`test_ca_trang_chi_gui_mot_lenh_ghi_la_bai_nhap_chu`): cả 3 hỏng, nên ca này không dựa vào việc đọc mã nguồn.

## Lỗi tìm ra

### SL-T106-1 · Thấp · Câu cũ của mục 1 vẫn khuyên «Quản trị viên» ngay cạnh câu mới bảo đừng nâng

- **Chỗ:** `app/views/wordpress.py:121-125` (có từ trước T-106): khi tài khoản thiếu quyền viết bài **hoặc** tải ảnh, trang hiện «Tài khoản thiếu quyền viết bài hoặc tải ảnh. Nên dùng tài khoản có vai trò Biên tập viên (Editor) hoặc Quản trị viên (Administrator).»
- **Thử:** tài khoản Cộng tác viên lõi (`edit_posts` có, `upload_files`, `unfiltered_html` không): trang hiện **cả** câu cũ đó **và** câu mới «Cách sửa: … Biên tập viên (Editor). Không cần, và không nên, nâng lên Quản trị viên.». Tài khoản website không cho biết quyền: câu cũ (khuyên Quản trị viên) cạnh câu «Chưa biết…».
- **Hậu quả:** hai lời khuyên ngược nhau trên cùng màn hình; câu cũ trái quyết định dùng tài khoản Biên tập viên riêng (CLAUDE.md, Lá Chắn T-059) và trái README bước 10 («thấy `administrator` là app đang dùng nhầm tài khoản quản trị»). Yêu cầu 3 của T-106 («không khuyên cấp quyền Quản trị») đúng ở câu mới nhưng chưa đúng ở trang. Họa Sĩ đã nêu trong «Rủi ro», «Đề xuất» và để ngoài phạm vi.
- **Test:** `test_sl_t106_1_trang_khong_khuyen_nang_len_quan_tri` (2 xfail). Không test nào ghim câu cũ (grep `Quản trị viên (Administrator)`, `thiếu quyền viết bài hoặc tải ảnh` trong `tests/`: chỉ test mới của Họa Sĩ, dạng «không có»).
- **Gợi ý:** bỏ «hoặc Quản trị viên (Administrator)» ở câu cũ.

### SL-T108-1 · Thấp · README dòng Trạng thái còn nói trang Kết nối tạo bài nháp có ảnh đại diện

- **Chỗ:** `README.md:7`: «kết nối WordPress (kiểm tra kết nối, xem chuyên mục/thẻ, tạo bài nháp có ảnh đại diện)».
- **Hậu quả:** trái giao diện mới và trái chính đoạn `README.md:115` vừa sửa. Yêu cầu 2 của T-108 chỉ nêu «đoạn tạo thử», nên dòng này sót.
- **Test:** `test_sl_t108_1_readme_trang_thai_khop_trang_ket_noi` (1 xfail).
- **Gợi ý:** «… xem chuyên mục/thẻ, tạo thử bài nháp chữ)».

## Ghi nhận (không tính lỗi)

- **G1 · `upload_media`, `upload_media_file` của client không còn nơi gọi trong app** (chỉ còn test). Hàm vẫn tải nguyên byte được đưa vào, không qua `make_web_image`. Phiếu cấm sửa `seo_app/**` nên để nguyên; phiếu sau có thể bỏ hay khóa hàm này để không ai nối lại đường tải nguyên file (LC-T093-1).
- **G2 · Ca cũ chạy qua nhánh đã bỏ nay qua «suông»:** `tests/test_soi_loi_t044.py::test_null_source_url_does_not_crash_page` vẫn dựng ảnh `source_url: null` và ô chọn file giả, nhưng trang không còn tải ảnh nên ca chỉ còn kiểm «không vỡ, 1 câu thành công». Không sai, chỉ không còn kiểm điều tên ca nói.
- **G3 · Câu «đã ở vai trò Biên tập viên trở lên»** cho tài khoản **Quản trị viên** thiếu quyền vẫn nói «Đừng nâng tài khoản lên Quản trị viên» (tài khoản đã là Quản trị viên) và không nhắc đây là dùng nhầm tài khoản quản trị (README bước 10). Hiếm, chữ chưa sát.
- **G4 · «Không biết» với subscriber** nói «website chưa cho biết đủ quyền», thực ra website đã cho biết là không có quyền viết bài. Hướng dẫn kèm theo («Kiểm tra kết nối lại sau khi tài khoản có quyền viết bài») vẫn đúng.
- **G5 · Giới hạn đã nêu** (Họa Sĩ, Thợ Máy T-091): REST trả quyền theo vai (`allcaps`), nên `DISALLOW_UNFILTERED_HTML` hay site nhiều site con vẫn báo «có quyền»; trang im lặng ở các ca đó.

## Lệnh đã chạy

- `uv run pytest tests/test_soi_loi_t106.py`: 23 passed, 3 xfailed; chạy lại 3 ca `xfail` với `--runxfail`: hỏng đúng ở dòng kiểm câu Quản trị viên / dòng README.
- Bản sao `HEAD` (= gộp với `main` `0122d4b`), 19 file: 3.261 passed, 5 xfailed, 0 failed.
- Đột biến: 12/12 bị bắt.
- `uv run ruff check .`: sạch. `detect-secrets scan tests/test_soi_loi_t106.py docs/team/reports/T-106-soi-loi.md` (`PYTHONUTF8=1`): sạch.
- Script đột biến: thư mục ghi chú chung `T-106-soi-loi-scripts/mutate106.py`.

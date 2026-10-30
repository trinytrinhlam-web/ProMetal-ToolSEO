# Biên bản bảo mật T-106 + T-108 · Trang Kết nối WordPress: cảnh báo quyền `unfiltered_html`, bài nháp thử không ảnh · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | T-106 (giao qua tin nhắn Chỉ Huy B 30/10, chưa có file phiếu), [T-108](../tickets/T-108-ket-noi-wordpress-bo-o-anh-tao-thu.md) (đọc ở checkout chính) · kiểm **rút gọn** (W2, F1, U1) |
| Phạm vi | Diff `c51fe4f..43d0a97` trên `team/T-106` (sau khi đưa T-093 vào nhánh): `app/views/wordpress.py`, `README.md:115`, `tests/test_la_chan_t093.py` (gỡ dấu `xfail` LC-T093-1), `tests/test_soi_loi_t044.py` (2 test, 8 ca, R5 Chỉ Huy duyệt A 30/10), test mới `tests/test_t106_trang_ket_noi.py`, `tests/test_soi_loi_t106.py`, 2 báo cáo. Không đổi `seo_app/**`, `config/**`, `uv.lock`. Soát thêm mọi chỗ trong `app/**` có thể tải ảnh lên website. Số dòng theo `43d0a97` |
| Báo cáo đã đọc | [Họa Sĩ](T-106-hoa-si.md), [Soi Lỗi](T-106-soi-loi.md) (SL-T106-1, SL-T108-1); [Lá Chắn T-093](T-093-la-chan.md) (LC-T093-1) |
| Ngày | 2026-10-30 (10:11 → 10:18 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T106-1, SL-T108-1 của Soi Lỗi, giữ Thấp); Lá Chắn không có lỗi mới. **LC-T093-1 đã đóng**: không còn đường nào trong `app/**` tải ảnh chưa làm sạch lên website. Câu cảnh báo `unfiltered_html` đạt U1 và không khuyên cấp quyền quá mức. R5 đạt. **Gộp `main` được ngay** (`main` trên máy `0122d4b` là tổ tiên của nhánh: tua thẳng; gộp thử với `team/T-107` không xung đột) |

## Tóm tắt (cho chủ dự án)

- Lỗi Trung bình ở trang **Kết nối WordPress** đã sửa đúng: mục «Tạo thử một bài nháp» nay chỉ tạo bài nháp chữ, không còn nhận và tải ảnh. Tôi soát cả app: ảnh chỉ còn lên website qua «Gửi nháp» ở trang Soạn bài, sau bước làm sạch (bỏ số seri máy, tên chủ máy, ảnh nhỏ nhúng…).
- Câu cảnh báo mới về quyền «HTML tự do» chỉ hiện khi tài khoản thiếu quyền, khuyên dùng vai **Biên tập viên** và nói rõ không nâng lên Quản trị viên. Câu không chứa tên đăng nhập, mật khẩu hay địa chỉ nào.
- Còn 2 lỗi nhỏ, không chặn: ngay trên trang đó, một câu **cũ** vẫn khuyên «Biên tập viên hoặc Quản trị viên» (nên bỏ chữ «hoặc Quản trị viên»); dòng giới thiệu đầu README còn nói trang này tạo bài nháp có ảnh đại diện.

## Lỗi phát hiện

Không phát hiện lỗi mới (Lá Chắn). Lỗi của Soi Lỗi: mục «Mức lỗi của Soi Lỗi».

## Kiểm từng việc

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| **1. LC-T093-1 đóng:** không còn đường nào ở `app/**` tải ảnh chưa làm sạch lên website | **Đóng** | `wordpress.py` bỏ `st.file_uploader`, ô «Mô tả ảnh», `client.upload_media`, dòng «Ảnh đại diện đã tải lên»; `create_draft(..., featured_media=None)` (`:180-186`). Soát cả `app/**` (`grep upload_media\|_post_media\|file_uploader\|/wp/v2/media\|create_draft_with_images\|set_featured_image`): chỉ còn `write.py:2748` `create_draft_with_images` với `WordPressImage` dựng từ `make_web_image` (`:2651`), và `plan.py:34` (`st.file_uploader` của trang Kế hoạch bản demo: giá trị không được đọc, không gửi đi đâu, không phải ảnh). `upload_media`, `upload_media_file`, `set_featured_image` của client không còn chỗ gọi trong `app/**`; `create_draft_with_images` chỉ nhận `WebImage` đã xử lý (`_check_web_image`). Test của tôi `test_lc_t093_1_wordpress_page_upload_follows_decision_2a` nay qua (đã gỡ `xfail`); `test_t106_trang_ket_noi.py` (không còn ô ảnh, 0 lệnh tới `/wp/v2/media`); 8 ca T-044 đổi kỳ vọng (mục 3) đều 0 lệnh tới Media dù website giả nhận ảnh |
| **2. Câu cảnh báo `unfiltered_html`** | **Đạt** | `unfiltered_html_note` (`wordpress.py:33-70`) trả 3 câu **cố định**, không ghép dữ liệu nào từ website hay `.env`: có quyền thì không hiện gì; thiếu quyền, vai thấp hơn Biên tập viên thì khuyên «đặt tài khoản này ở vai trò **Biên tập viên (Editor)**. Không cần, và không nên, nâng lên Quản trị viên»; thiếu quyền mà đã là Biên tập viên trở lên thì «báo người làm web xem lại. Đừng nâng tài khoản lên Quản trị viên chỉ vì việc này»; không biết thì một câu trung tính. Khớp sổ rủi ro dòng 2026-10-28 (tài khoản Biên tập viên có `unfiltered_html` là chấp nhận có chủ đích, «không cấp thêm quyền»). Không tên đăng nhập, mật khẩu, đường dẫn (test `assert_no_account_details`). `info.roles` chỉ dùng để so có `editor`/`administrator` (client đã lọc thành bộ chữ, `client.py:794`), không in ra; chữ website khác trên trang vẫn qua `plain()` (`escape_markdown`, T-044). Hiện bằng `st.warning`/`st.info`; trang không có `unsafe_allow_html`. Đóng luôn T-059 ĐK 2 và T-091 ĐK 3 (phần giao diện) khi nhánh gộp |
| **3. R5: 2 ca T-044 đổi đúng điều kiện duyệt, gỡ `xfail` đúng** | **Đạt** | `test_soi_loi_t044.py::test_uploaded_image_url_line_is_plain` × 6: giữ 6 `source_url` độc hại, `file_uploader` giả vẫn trả file, website giả vẫn nhận ảnh; bỏ bước điền ô alt (ô không còn); kiểm mới: trang chữ thường, **0** lệnh tới `/wp/v2/media`, không dòng «Ảnh đại diện», địa chỉ ảnh và tên file không có trong chữ nào trên trang (cả Markdown lẫn chữ hiện), đúng 1 lệnh tạo nháp `status: draft`, **không** khóa `featured_media`; câu tiêu đề vẫn kiểm chữ thường như cũ. `test_upload_error_with_hostile_filename_is_plain` × 2: giữ 2 tên file độc hại; website giả nhận ảnh và nhận lệnh tạo nháp; kiểm không câu lỗi, bài nháp chữ tạo được, tên file không lên trang, 0 lệnh Media, 1 lệnh tạo nháp không `featured_media`. Đúng phương án A Chỉ Huy duyệt (vẫn dùng file độc hại, kiểm không lệnh nào tới Media, không dòng ảnh, `featured_media` rỗng, tên file và địa chỉ ảnh không lộ); câu kiểm cũ bị thay chỉ là câu ghim đường tải ảnh đã bỏ, câu kiểm mới chặt hơn. `test_la_chan_t093.py`: chỉ xóa dấu `xfail` LC-T093-1 (4 dòng), thân test giữ nguyên. Không `skip`, không xóa ca |
| **4. Mức 2 lỗi Thấp của Soi Lỗi** | Mục dưới | — |
| **5. Thử gộp** | **Không xung đột** | `main` trên máy `0122d4b` là tổ tiên của `team/T-106` (gộp là tua thẳng). `git merge-tree --write-tree` với `team/T-107` (`1375e62`, nay là `main` + T-093): sạch; hai nhánh chỉ cùng chạm `tests/test_la_chan_t093.py` ở hai dấu `xfail` khác nhau |
| W2 | **Đạt** | Trang Kết nối chỉ còn ghi `create_draft` trạng thái nháp, không ghi vào bài, ảnh có sẵn, không lệnh nào tới thư viện Media |
| F1 | **Đạt** | Trang không còn nhận file từ máy người dùng |
| U1 | **Đạt** | Không thêm `unsafe_allow_html` (chữ duy nhất trong file là câu chú thích nói trang không dùng); câu mới cố định; chữ website qua `plain()` |

## Mức lỗi của Soi Lỗi

| Mã | Mức Lá Chắn | Lý do |
|---|---|---|
| SL-T106-1 (câu cũ `wordpress.py:121-125` khuyên «Biên tập viên (Editor) hoặc Quản trị viên (Administrator)» ngay cạnh câu mới bảo đừng nâng) | **Thấp** (giữ; có từ trước T-106) | Đúng như Soi Lỗi tả: tài khoản Cộng tác viên, hay website không cho biết quyền, thấy hai lời khuyên ngược nhau. Lời khuyên «Quản trị viên» trái quyết định dùng tài khoản Biên tập viên riêng (CLAUDE.md, Lá Chắn T-059) và README bước 10. Người làm theo thì mật khẩu ứng dụng có quyền quản trị: lộ ra thì nặng hơn nhiều so với dòng sổ rủi ro 2026-10-28 đã chấp nhận. Chưa ai bị dẫn tới đó (tài khoản thật là Biên tập viên), chữ đúng nằm ngay cạnh, nên Thấp. Nên sửa sớm (bỏ «hoặc Quản trị viên (Administrator)»: một dòng; gỡ 2 `xfail` của Soi Lỗi) |
| SL-T108-1 (`README.md:7` còn «tạo bài nháp có ảnh đại diện») | **Thấp** (giữ) | Chỉ là chữ hướng dẫn lệch với trang mới; không mở lại đường tải ảnh nào. Thư Ký sửa cùng lần README kế tiếp; gỡ `xfail` khi sửa |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets (`PYTHONUTF8=1`) | 8 file đổi: 3 dấu «Secret Keyword» | **Báo nhầm**: mật khẩu thử giả trong test (`tests/test_soi_loi_t044.py:39`, có từ T-044; `tests/test_t106_trang_ket_noi.py:25`, mật khẩu ứng dụng giả chỉ dùng trong test) và một dòng báo cáo Họa Sĩ chép lại dòng test đó. Không khóa, mật khẩu thật nào. Biên bản này: `{}` |
| bandit | `PYTHONUTF8=1 uvx bandit -r app/views/wordpress.py`: 0 vấn đề | — |
| pip-audit | Không chạy lại: `uv.lock` không đổi (lượt quét cuối Giai đoạn 3 ở T-093) | — |
| ruff | `uv run ruff check .`: All checks passed! | — |
| pytest (nhánh `43d0a97`, chọn lọc) | `tests/test_t106_trang_ket_noi.py`, `tests/test_soi_loi_t106.py`, `tests/test_soi_loi_t044.py`, `tests/test_app_wordpress.py`, `tests/test_la_chan_t093.py`, `tests/test_app_pages.py`, `PYTHONUTF8=1`: **113 passed, 5 xfailed, 0 failed** (132,9 s). 5 xfail đều đã biết: SL-T106-1 × 2, SL-T108-1 (Soi Lỗi), LC-T093-2, LC-T093-3 (T-093, LC-T093-3 đang sửa ở T-107) | — |

## Sau T-107, T-108: Giai đoạn 3 còn thiếu gì để đóng

Đối chiếu mục 5 biên bản T-093:

| Việc | Trạng thái |
|---|---|
| LC-T093-1 (Trung bình) | **Xong** khi nhánh `team/T-106` gộp `main` (biên bản này) |
| LC-T093-3 (Cao) | T-107 đang làm: phải xong, qua Soi Lỗi và Lá Chắn rút gọn, gộp `main` |
| T-078 phần còn lại (gốc LC-T075-1 Cao): `required-version = ">=0.13.4"` trong `pyproject.toml`, README cách nâng `uv` | **Chưa giao** (Thợ Máy, Thư Ký). Việc nhỏ, nên làm trước khi đóng |
| Quyết định của chủ dự án (`TIEN-DO.md` mục 4): LC-T093-2 (gắn ảnh vào bài nháp hay ghi sổ), N1 → N5 (LC-T061-4; OSS-Fuzz libheif; GPLv2 pillow-heif; LC-T052-5, SL-T070-4); xác nhận mang sang T-064, T-072, T-053, phần Mac, phần Linux | **Chờ chủ dự án** |
| Sửa câu sổ rủi ro mục 6 (dòng `unfiltered_html`: mã chèn chạy trong phiên người đang đăng nhập xem bài; dòng LC-T048-6: thay số dòng cũ bằng `_same_file`) | Chờ chủ dự án đồng ý, Chỉ Huy sửa |
| Không chặn đóng: SL-T106-1 (nên sửa sớm, một dòng), SL-T108-1; chạy test trên Mac (chưa dùng app trên Mac tới lúc đó), lượt Linux cần cloud; kiểm lại bằng Fable sau 01/11 | Mang sang |

Khi T-107 gộp, T-078 phần còn lại xong và chủ dự án quyết các mục trên (sửa hay ghi sổ), Giai đoạn 3 đóng được.

## Báo nhầm đã loại

- detect-secrets: 3 dấu «Secret Keyword» là mật khẩu thử giả trong test (xem trên).

## Ghi nhận (không phải lỗi)

1. Phiếu T-106 chưa có file trong `docs/team/tickets/` (giao qua tin nhắn); Chỉ Huy nên lập file phiếu khi gộp để biên bản này có chỗ dẫn.
2. Đề xuất của Họa Sĩ (client trả «không biết» cho `can_unfiltered_html` thay vì để giao diện suy từ `can_edit_posts`) là hướng đúng, cho phiếu dọn client sau; hiện cách suy của giao diện an toàn (thiếu khóa coi là thiếu quyền, chỉ dẫn tới câu cảnh báo).

## Điều kiện

1. **Gộp `main`:** được ngay. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ.
2. **SL-T106-1 (Thấp):** bỏ «hoặc Quản trị viên (Administrator)» ở câu cũ của mục 1 (`wordpress.py:121-125`), gỡ 2 `xfail` của Soi Lỗi (chỉ xóa dấu). Phiếu nhỏ Họa Sĩ, nên làm sớm.
3. **SL-T108-1 (Thấp):** Thư Ký sửa `README.md:7`, gỡ `xfail`.
4. **Lá Chắn:** kiểm lại biên bản này bằng Claude Fable sau 01/11.

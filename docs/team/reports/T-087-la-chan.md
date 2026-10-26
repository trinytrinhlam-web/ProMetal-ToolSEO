# Biên bản bảo mật T-087 · README: chọn ảnh, ảnh AI, ảnh công khai khi gửi nháp · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-087](../tickets/T-087-readme-chon-anh.md) · kiểm **rút gọn** (phiếu tài liệu; yêu cầu bảo mật riêng D1) |
| Phạm vi | Diff `504ab15..4fbd6f6` (1 commit): `README.md` (mục 9 «Chọn ảnh cho bài» dòng 269–301, mục 10 «Gửi bài nháp lên WordPress» dòng 303–333, sửa dòng 7, 16, 46, 97, 139, 161–162, 202, 213–215, 242–243, 251, 258–259, 265–267; mục cũ 9, 10 đổi số thành 11, 12) và báo cáo Thư Ký. Không file code, cấu hình, test nào đổi. Đối chiếu với giao diện thật `app/views/write.py` của `main` (`main` từ `504ab15` tới `2e04066` chỉ đổi tài liệu, nên code giống hệt) |
| Báo cáo đã đọc | [Thư Ký](T-087-thu-ky.md); điều kiện 3, 4 của [Lá Chắn T-056](T-056-la-chan.md); LC-T069-1, LC-T069-2 của [Lá Chắn T-069](T-069-la-chan.md) |
| Ngày | 2026-10-26 (09:59 → 10:13 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 2 Thấp (LC-T087-1, LC-T087-2). D1 đạt (không bí mật, không đường dẫn máy thật). Mọi điều kiện chép vào phiếu đều có trong README và nói đúng điều app làm. **Gộp `main` được ngay** (không xung đột với `origin/main` `2e04066`, `team/T-085`, `team/T-086`); nên sửa LC-T087-2 trước lần gửi thật đầu tiên (T-059) |
| **Kết luận lượt 2** (2026-10-26) | **ĐẠT** · LC-T087-1, LC-T087-2 đã sửa đúng ý, 0 lỗi còn mở. **Gộp `main` được ngay** (đầu nhánh `6ecbe95`). Xem mục [Kiểm lại lượt 2](#kiểm-lại-lượt-2-2026-10-26) |
| **Kết luận lượt 3** (2026-10-26) | **ĐẠT** · khối «Lời dặn tạm thời» viết lại đúng app sau T-086, vẫn dặn một tab tới khi T-089 xong; 0 lỗi. **Gộp `main` được ngay** (nhánh `team/T-087-l3`, đầu nhánh `4e4d301`). Xem mục [Kiểm lại lượt 3](#kiểm-lại-lượt-3-2026-10-26) |

## Tóm tắt (cho chủ dự án)

Phần README mới **an toàn để gộp** và nói đúng app hiện nay: tôi soát từng tên nút, từng câu nhắc README chép lại (41 chỗ) với giao diện thật, đều khớp. Đủ các điều bảo mật bạn cần biết: ảnh (kể cả GPS) công khai ngay khi tải lên, kể cả khi bài còn là nháp; app không tự xóa ảnh; AI chỉ xem ảnh bạn bấm, bản đã bỏ GPS; alt phải duyệt; đoạn `[...]` nên xóa; lỗi giữa chừng thì kiểm Bài viết → Nháp và Media; lời dặn tạm khi gửi; dấu «ảnh AI» gắn tay chỉ nhớ trên máy này. Không có khóa, mật khẩu hay đường dẫn máy thật nào.

Có 2 chỗ nên viết rõ hơn, đều mức Thấp:

1. **Ảnh công khai rộng hơn README nói.** README viết «ai có đường dẫn ảnh đều mở được». Thật ra WordPress cho **bất kỳ ai, không cần đăng nhập** xem danh sách ảnh trong thư viện Media của website (tôi đọc mã nguồn WordPress để chắc), và app tải ảnh lên mà không gắn vào bài nháp, nên ảnh hiện trong danh sách đó ngay. Người lạ tìm được ảnh (và vị trí GPS trong ảnh) mà không cần ai gửi đường dẫn, kể cả ảnh của bài thử bạn định xóa. Nên sửa câu này, và dặn lần gửi thử đầu tiên chọn ảnh có GPS ở chỗ đã công khai (xưởng, cửa hàng), không phải nhà khách. Nên sửa trước lần gửi thật đầu tiên.
2. README dặn xóa đoạn `[...]` trước khi gửi, nhưng chỉ chỉ cách xóa ở nội dung, alt, chú thích. Đoạn nằm ở **tiêu đề bài, tiêu đề mục** thì app chưa có ô sửa; README nên dặn xóa đoạn đó trong WordPress **trước khi** bấm Lưu/Đăng.

Gộp vào `main` được ngay; Thư Ký sửa 2 chỗ trên trong một lượt ngắn (hoặc cùng lần sửa README khi T-086 gộp).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T087-2 | Thấp | **README nói ảnh công khai «qua đường dẫn», nhưng WordPress liệt kê công khai mọi ảnh app tải lên.** Client tải ảnh **không gắn vào bài** (không gửi `post`; `seo_app/wordpress/client.py:1297` của `main`: «Không gửi `status`, `post`»), nên ảnh có `post_parent = 0`. Mã nguồn WordPress (`wordpress-develop` nhánh trunk `f72b766`, đọc qua GitHub công khai, không gọi website): `GET /wp/v2/media` không đòi đăng nhập ở ngữ cảnh `view` (`class-wp-rest-posts-controller.php` `get_items_permissions_check`, dòng 160-172); truy vấn lấy `post_status = inherit` (`class-wp-rest-attachments-controller.php:357-362`); từng mục qua `check_read_permission` (`posts-controller:467-472`), mà mục `inherit` **không có bài cha thì coi như đã đăng** (`:1807-1813`). Câu trả lời có `source_url`, `alt_text`, `caption`, `title` (ngữ cảnh `view`, `attachments-controller:1786-1800`) | `README.md:317` (và `:330`, lời dặn lần gửi đầu); câu nhắc trên giao diện cũng cùng ý «qua đường dẫn» (`write.py:152-155`, `GPS_PUBLIC_WARNING`) | Chủ dự án làm theo `:330`: lần gửi thử đầu tiên chọn một ảnh «📍 Ảnh có vị trí GPS» (ảnh công trình thường chụp ở nhà khách), gửi bài nháp, kiểm GPS rồi định xóa. Đọc `:317` thấy «ai có đường dẫn ảnh đều mở được», nghĩ chưa ai có đường dẫn nên ảnh thử coi như kín, để đó vài hôm hay quên xóa. Trong lúc đó bất kỳ ai mở `https://<website>/wp-json/wp/v2/media` (suy luận, chưa đo: công cụ dò website WordPress hay đọc các danh sách REST công khai này) đều thấy ảnh, tải về, đọc tọa độ nhà khách, của một bài **không bao giờ đăng**. Cùng đường đi với bài nháp bỏ dở. Chưa thử trên website thật (không được gọi site thật): website có plugin chặn REST cho người chưa đăng nhập thì không bị; mặc định WordPress thì bị. Xếp **Thấp** vì chủ dự án đã chấp nhận ảnh có GPS công khai (sổ rủi ro 2026-10-14, quyết định 5A), README đã nói rõ «công khai ngay khi tải lên, kể cả khi bài còn là nháp»; chỗ thiếu là mức độ «tìm thấy được», ảnh hưởng tới cách chọn ảnh thử và việc dọn bài bỏ dở | Thư Ký sửa `README.md:317`: «**Ảnh xem được công khai ngay khi tải lên, kể cả khi bài còn là nháp**: ảnh vào thư viện Media của website, mà WordPress cho **bất kỳ ai, không cần đăng nhập**, xem danh sách Media (kèm địa chỉ ảnh, alt, chú thích). Người lạ tìm được ảnh mà không cần ai gửi đường dẫn, mở ảnh là đọc được vị trí GPS còn trong ảnh. App **không tự xóa** ảnh đã tải lên, kể cả khi bạn xóa bài nháp; muốn gỡ ảnh thì xóa trong **Media → Thư viện**. Xóa rồi thì đường dẫn không mở được nữa, nhưng ai đã tải ảnh về vẫn còn bản sao.» Sửa `:330`: «chọn ảnh app báo «📍 Ảnh có vị trí GPS» **chụp ở nơi đã công khai** (xưởng, cửa hàng), đừng dùng ảnh nhà khách cho lần thử; kiểm xong xóa ngay». **Trước lần gửi thật đầu tiên (T-059).** Câu nhắc trên giao diện (`write.py:152-155`) sửa cùng ý ở một phiếu Họa Sĩ sau (không chặn) |
| LC-T087-1 | Thấp | **Thiếu cách xử lý đoạn `[...]` nằm ở tiêu đề bài, tiêu đề mục.** README `:309` dặn «Nên xóa các đoạn đó rồi mới gửi (ở bước Viết & kiểm tra: nội dung bấm ✏️ Sửa ở từng mục, alt và chú thích sửa ở khung ảnh)». Nhưng khung cảnh báo của app liệt kê cả «Tiêu đề bài», «Tiêu đề mục «…»» (`write.py:1903`, `:1909`), mà ở bước Viết & kiểm tra không có ô sửa hai thứ đó: tiêu đề mục chỉ hiện (`section_card` `:1654-1658`), nút ✏️ Sửa chỉ sửa thân đoạn (`:1708-1716`, `save_manual` `:1459-1464`); tiêu đề bài (`article_title`) không có ô nhập nào | `README.md:309` | Nghiên cứu từ khóa đọc trang đối thủ (dữ liệu ngoài, A1); một trang cài sẵn chữ dạng `[code_snippet id=…]` làm AI chép vào tiêu đề một mục. App liệt kê đúng ở «Tiêu đề mục «…»». Chủ dự án làm theo README, không tìm được chỗ xóa, gửi nháp. Sau đó mở bài trong WordPress, sửa vài chữ rồi bấm Lưu/Đăng: trình soạn có thể đổi `&#91;` thành «[», shortcode nằm trong `<h2>` của nội dung chạy khi WordPress dựng bài (đúng nguy cơ LC-T061-4 muốn chặn). Xếp **Thấp**: cần dữ liệu ngoài cài sẵn đúng tên shortcode đã đăng ký; app đã vô hiệu lúc gửi (T-061) và nhắc rõ trên giao diện; Code Snippets trên site là 4.0.0 (đã xác nhận ở T-056) | Thêm sau câu `:309`: «Đoạn nằm ở **tiêu đề bài** hay **tiêu đề mục** thì chưa sửa được ở bước này: gửi nháp xong, mở bài trong WordPress và xóa đoạn đó **trước khi** bấm Lưu hay Đăng (hoặc quay lại bước **Dàn ý** sửa tiêu đề rồi để AI viết lại bài).» Sửa cùng lượt với LC-T087-2, hoặc cùng lần sửa README khi T-086 gộp |

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình.

## Đối chiếu điều kiện bảo mật đã chép vào phiếu

| Điều kiện (nguồn) | Kết quả | Bằng chứng |
|---|---|---|
| Yêu cầu 1: cách chọn ảnh: mở thư mục, chọn, Ảnh thật/Ảnh AI (kèm lý do), GPS, «AI viết alt» (chỉ ảnh đã chọn, bản đã bỏ thông tin máy), tick «Đã duyệt» | **Đạt** | `README.md:269-285`. «AI chỉ xem đúng ảnh này, và là bản sao đã bỏ GPS, thông tin máy chụp» (`:282`) khớp `ai_write_alt` (`write.py:904-938`, byte `make_ai_image` `:918`); `:139` (mục 7.2) «App chỉ gửi ảnh cho hãng AI khi bạn bấm ✨ AI viết alt … mỗi lần một ảnh» khớp `:1082-1089` (Lá Chắn T-056 bảng điều kiện số 14, 15). «Đọc lại alt … không có tên, số điện thoại, địa chỉ khách. Rồi tick ✅ Đã duyệt. Sửa chữ thì phải tick lại» (`:283`) khớp `alt_editor` `:1119-1132`, `unapprove` `:836-837`; «chưa duyệt thì chưa gửi bài được» (`:285`) khớp `slot_problem` `:767-779`, `draft_panel` `:2114-2118`, `:2137` |
| Yêu cầu 2: ảnh AI tạo ngoài app, thư mục có chữ «AI»/«minh họa»; nút «Đây là ảnh AI» không đổi lại được; LC-T069-2 | **Đạt** | `:287-301`, `:242-245`, `:258-259`, `:265-267`. «Chọn Ảnh AI ở đầu khung chỉ để hiện prompt. Ảnh có phải ảnh AI hay không là do tên thư mục, tên file, hoặc nút dưới đây» (`:296`): đúng, nguồn ảnh theo thẻ (`slot_tags` `:678-683`, `choose_image` `:886-901`), không theo ô «Loại ảnh». «Trong app không đổi lại thành ảnh thật được» (`:300`) khớp `mark_ai` `:846-883`, `ai_reason` `:833`. «Cũng có thể khai báo riêng thư mục ảnh AI … mọi ảnh trong đó là ảnh AI» (`:242`) khớp `root_notes` `:579-596` (Lá Chắn T-056 bảng số 21) |
| LC-T069-2 (Lá Chắn T-069): dấu «ảnh AI» gắn tay mất khi xóa `data/image_tags.sqlite`, đổi thứ tự `IMAGE_FOLDERS`, mở trên máy kia; dặn để ảnh AI trong thư mục có chữ AI | **Đạt**, đúng cách sửa đề xuất | `:258` (chỉ nhớ trên máy đang dùng; muốn hai máy cùng thấy thì để ảnh AI vào thư mục có chữ AI), `:265` (xóa file thì mất dấu, chọn lại thành Ảnh thật, kiểm lại các ảnh đó), `:301` (đủ 3 đường: xóa file, đổi thứ tự, máy kia), `:214` (đổi thứ tự `IMAGE_FOLDERS`). «Khi chọn lại» là đúng chữ: nháp đã lưu ảnh với nguồn AI thì mở lại nháp vẫn là ảnh AI (nháp chỉ kéo về phía ảnh AI, `drafts.py:797-817`) |
| LC-T069-1 (Lá Chắn T-069, Thư Ký sửa thêm): thư mục phần mềm có `.env`, đừng để trong Google Drive, OneDrive | **Đạt**, dùng đúng câu đề xuất | `:215` (gần như nguyên văn câu đề xuất, «thẻ ảnh» đổi thành «dấu «ảnh AI» gắn tay» cho đúng app hiện nay), nhắc lại lúc tải phần mềm `:16`. Khuyến nghị 1 bên dưới |
| Yêu cầu 3, điều kiện 4 Lá Chắn T-056: «Gửi nháp» chỉ tạo bài nháp; ảnh (kể cả GPS) công khai ngay khi tải lên, kể cả bài nháp; app không tự xóa ảnh; đoạn `[...]` nên xóa; lỗi giữa chừng kiểm Bài viết → Nháp, Media → Thư viện | **Đạt** (kèm LC-T087-1, -2) | `:316` (chỉ nháp, không sửa bài có sẵn: `client.py` bước 3, «bài luôn draft»); `:317` (công khai, không tự xóa, kể cả khi xóa bài nháp: WordPress xóa bài không xóa Media); `:309` (đoạn `[...]`, đúng câu nhắc của app `write.py:2132-2136`); `:323-324` (lỗi lúc kiểm lại: «Chưa gửi gì lên website.» `:2006`; lỗi giữa chừng: kiểm Bài viết → Nháp và Media → Thư viện, khóa tới khi tick «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi» `:2138-2145`) |
| Yêu cầu 4, điều kiện 3 Lá Chắn T-056: lời dặn tạm (đợi kết quả, không tải lại trang, không bấm nút khác); lần gửi thật đầu tiên một bài, một ảnh, tải ảnh về kiểm GPS | **Đạt** (kèm LC-T087-2 cho `:330`) | `:326-333`. `:328` gồm cả «không đóng tab», «không bấm đúp» (SL-T056-1, -9, -11, LC-T056-1); `:329` «đừng bấm gửi lại sau khi mở lại bài» (SL-T056-8, -11): đúng `main` hôm nay (`_wp_sent` nằm trong `COMPOSE_KEYS` `:102-110`, mất khi mở bài khác hay tải lại trang). Địa chỉ ảnh để tải về là `source_url` app in ra (`send_result` `:2093-2098`), client đã kiểm là `https://` trên đúng website (`is_site_link`) nên dặn dán vào trình duyệt là an toàn |
| Yêu cầu 5, D1: tiếng Việt, không đường dẫn máy thật, không khóa | **Đạt** | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-087-thu-ky.md`: `{}`. Đường dẫn trong README chỉ là ví dụ chung (`E:/anh-cong-trinh;G:/My Drive/Anh SEO` `:208`, `/Volumes/USB/anh-cong-trinh` `:210`, `G:/My Drive/Ảnh AI` `:242`); không `C:\Users\…`, tên máy, email, khóa |
| T-086 chưa gộp: README đúng `main`, không hứa điều T-086 chưa làm | **Đạt** | «Lời dặn tạm thời (tới khi app nhớ được việc gửi cả khi tải lại trang)» (`:326`) không hứa ngày, không tả luồng mới. Nhãn README trích ở luồng gửi («📤 Gửi nháp», «Tạo thêm một bài nháp mới», «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi») vẫn giữ nguyên trong `team/T-086` (`git show origin/team/T-086:app/views/write.py`, dòng 2377, 2383, 2388), nên gộp T-086 không làm README sai thành nguy hiểm; chỉ khối lời dặn tạm cần viết lại (Điều kiện 3) |

## README không hứa điều code không làm

- Soát **41 nhãn nút, câu nhắc** README chép lại (từ «📷 Chỗ cần ảnh», «📁 Chọn ảnh từ thư mục», «⬆ Lên một cấp» tới «Chưa lưu được dấu «ảnh AI» trên máy này», «Trong lần làm việc này app vẫn coi…»): cả 41 có trong `app/views/write.py` của `main` (`grep -cF` từng chuỗi, mỗi chuỗi ≥ 1).
- «Bài một ảnh thì ảnh đó là ảnh đại diện» (`:308`): đúng, client tự đặt ảnh duy nhất làm ảnh đại diện. Đã thử ở lượt Lá Chắn T-056 (WordPress giả: bài một ảnh có lệnh `featured_media` cho ảnh đó).
- «Tên file do app đặt từ thẻ (thiếu thẻ thì từ alt) … không lấy tên file, tên thư mục trên máy» (`:318`): đúng `seo_app/images/naming.py` (docstring dòng 1-11, `_base_name` từ dòng 40).
- «App nhận ảnh JPG, PNG, WebP, HEIC (iPhone), AVIF, mỗi ảnh tối đa 40 MB» (`:277`): đúng `folders.py:53-54` (thêm `.heif`).
- «mở lại bài, app kiểm lại ảnh trên máy và báo nếu ảnh đã bị xóa hay đổi tên» (`:285`): đúng, và không hứa nhận ra ảnh bị thay nội dung (phần còn lại của SL-T056-2 chưa làm).
- **Không hướng dẫn điều gì làm giảm an toàn:** không bảo tắt kiểm tra nào, không bảo để khóa ngoài `.env`, không bảo chép hay đồng bộ `data/`. Cách gỡ dấu «ảnh AI» bấm nhầm (`:300`, đổi tên file) là việc người dùng tự làm ngoài app, đúng thiết kế «trong app không đổi lại được» (điều kiện 2(b) Lá Chắn T-052); khuyến nghị 3 bên dưới. Đổi `[images]` (`:318`) đi qua bộ đọc cấu hình đã kiểm (T-062).

## Đã chạy thử

1. **Mã nguồn WordPress** (cho LC-T087-2): tải `class-wp-rest-posts-controller.php`, `class-wp-rest-attachments-controller.php` từ `raw.githubusercontent.com/WordPress/wordpress-develop/trunk` (commit `f72b766`) vào thư mục nháp, chỉ đọc bằng `grep`/`sed`, không chạy. Kết quả như cột «Mô tả» của LC-T087-2. Không gọi website thật.
2. **detect-secrets có mồi:** bản sao README (có chữ tiếng Việt) trong thư mục nháp, thêm 3 chuỗi giả (khóa dạng `sk-ant-…`, mật khẩu WordPress giả, khóa AWS mẫu), quét bằng `PYTHONUTF8=1` (đứng trong thư mục đó, đường dẫn tương đối): bắt đủ (Base64 High Entropy String, Secret Keyword ×2, AWS Access Key). Đã xóa bản mồi. Ghi chú cho lần sau: quét bằng đường dẫn tuyệt đối ra ngoài thư mục đang đứng thì một lần thử của tôi không ra kết quả nào, nên luôn quét bằng đường dẫn tương đối từ gốc repo như lệnh trong `security.md`.
3. **Thử gộp:** `git merge-tree --write-tree` của `team/T-087` với `origin/main` (`2e04066`), `origin/team/T-085`, `origin/team/T-086`: không xung đột. `team/T-086` không sửa `README.md`.
4. `uv run ruff check .`: All checks passed! Không chạy pytest: phiếu chỉ đổi `README.md` và báo cáo (`git diff --name-only 504ab15..4fbd6f6`); Thư Ký đã chạy `tests/test_app_pages.py` và 3 test ảnh làm chứng cho các câu README (21 passed).

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets `{}` (README, báo cáo Thư Ký), có mồi; `git diff 504ab15..4fbd6f6` không có khóa, mật khẩu |
| S2 | Không áp dụng | Không code |
| S3 | Không áp dụng | Không biến cấu hình mới; `.env.example` không đổi |
| W1 | Đạt | README nói đúng: chỉ tạo nháp (`:316`); «Hẹn giờ», «Đăng ngay» vẫn là bản demo (`:97`) |
| W2 | Đạt | README nói đúng: app không sửa bài có sẵn, không tự xóa ảnh (`:316-317`) |
| W3 | Đạt (kèm LC-T087-1) | Dặn xóa đoạn `[...]` (`:309`) |
| W4 | Không áp dụng | Không đổi kết nối |
| A1 | Không áp dụng | Không prompt; LC-T087-1 nêu dữ liệu ngoài làm đường đi |
| A2 | Không áp dụng | — |
| A3 | Đạt | README nói đúng ảnh gửi hãng AI: chỉ khi bấm, một ảnh, bản đã bỏ GPS (`:139`, `:282`); khuyến nghị 2 cho prompt dán ra ngoài |
| U1 | Không áp dụng | Không code giao diện |
| U2 | Đạt | README không có đường dẫn máy thật, không nội dung `.env` |
| U3 | Không áp dụng | — |
| F1 | Đạt | README giữ «app chỉ đọc ảnh, không ghi gì vào thư mục ảnh» (`:257`); không bảo đặt thư mục phần mềm trong thư mục ảnh (`:215`) |
| F2 | Đạt (kèm LC-T087-2) | README nói đúng ảnh web giữ GPS, công khai (`:317-318`) |
| F3 | Không áp dụng | — |
| D1 | Đạt | Không bí mật trong tài liệu (yêu cầu bảo mật riêng của phiếu); không thư viện mới |
| D2 | Đạt | `.gitignore` không đổi; README dặn không để `.env`, `data/` trong thư mục đồng bộ (`:16`, `:215`) |
| D3 | Không áp dụng | Không test mới |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-087-thu-ky.md`: `"results": {}`; biên bản này: `{}` | Có mồi (mục «Đã chạy thử» số 2) |
| Soát lịch sử git | Dòng thêm của `git diff 504ab15..4fbd6f6`: không khóa, mật khẩu, đường dẫn máy | Đọc từng dòng |
| ruff | All checks passed! | — |
| pip-audit, bandit | Không chạy: phiếu không đổi thư viện, không đổi code Python | — |

## Báo nhầm đã loại

Không có.

## Khuyến nghị (không phải lỗi, không bắt buộc)

1. `:16`: GitHub Desktop mặc định lưu dự án vào thư mục Documents, mà Windows hay tự đồng bộ Documents lên OneDrive (lý do nêu ở LC-T069-1). Có thể thêm: «GitHub Desktop mặc định chọn thư mục Documents; nếu Documents đang đồng bộ lên OneDrive thì chọn thư mục khác, ví dụ ngay trên ổ C hay D.»
2. `:292`: prompt ảnh do AI viết từ bài (có thể lấy ý từ «Chất liệu thật»). Có thể thêm: «Đọc prompt trước khi dán sang công cụ khác: bỏ tên, địa chỉ, số điện thoại khách nếu có.»
3. `:300`: cách gỡ dấu bấm nhầm nên nói rõ «chỉ khi chắc ảnh là ảnh chụp thật».
4. **Đề xuất cho Chỉ Huy (Thợ Máy, cần chủ dự án duyệt):** sau khi tạo bài nháp, gắn ảnh vào chính bài đó (`POST /wp/v2/media/<mã>` với `post = <mã bài nháp>`, chỉ ảnh vừa tạo). Khi đó WordPress xét quyền theo bài cha là nháp, nên ảnh **không còn** trong danh sách Media công khai tới khi bài được đăng (đường dẫn trực tiếp vẫn mở được). Giảm hẳn đường đi của LC-T087-2 cho bài thử, bài bỏ dở. Phải giữ đúng chốt chặn của T-060, T-085 (chỉ ghi vào ảnh vừa tạo, khóa JSON cố định).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **LC-T087-2 (Thấp) → Thư Ký, sửa `README.md:317`, `:330` theo câu đề xuất. Hạn: trước lần gửi thật đầu tiên (T-059).** Có thể làm ngay trong T-087 lượt 2 (vài câu, Lá Chắn kiểm rút gọn) hoặc gộp T-087 trước rồi sửa ở phiếu README kế tiếp, miễn trước T-059. Câu nhắc trên giao diện (`write.py:152-155`) sửa cùng ý ở một phiếu Họa Sĩ sau, không chặn.
2. **LC-T087-1 (Thấp) → Thư Ký, thêm câu sau `README.md:309`.** Cùng lượt với điều kiện 1, hoặc cùng lần sửa README khi T-086 gộp.
3. **Khi T-086 gộp → Thư Ký** viết lại khối «Lời dặn tạm thời» (`:326-329`) cho đúng app mới (Thư Ký đã tự đề xuất trong báo cáo). Lá Chắn kiểm rút gọn.
4. **Lá Chắn:** kiểm lại biên bản này bằng Claude Fable sau 01/11.

## Kiểm lại lượt 2 (2026-10-26)

Thư Ký sửa ở `6ecbe95` (báo cáo `T-087-thu-ky.md` mục «Lượt 2»). Đọc `git diff b426bd9..6ecbe95 -- README.md` (4 chỗ, chỉ chữ trong `README.md`), đối chiếu với code và mã nguồn WordPress đã đọc ở lượt 1. 10:32 → 10:35 +07, giờ máy.

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T087-2 | **Đóng** | `README.md:317` nay nói ảnh vào thư viện Media, WordPress cho bất kỳ ai không cần đăng nhập xem danh sách (kèm địa chỉ ảnh, alt, chú thích), người lạ tìm được ảnh không cần đường dẫn: đúng mã nguồn WordPress (`GET /wp/v2/media` ngữ cảnh `view`, mục `inherit` không có bài cha coi như đã đăng; `source_url`, `alt_text`, `caption` ở ngữ cảnh `view`) và đúng client (ảnh không gắn bài: `POST /wp/v2/media` chỉ nhận tham số `_fields`, `client.py:105`; lệnh ghi alt không gửi `post`, `:1297`). Câu «Xóa chỉ gỡ ảnh khỏi website: ai đã tải ảnh về vẫn còn bản sao» thận trọng hơn câu tôi đề xuất (không hứa «đường dẫn không mở được nữa» khi chưa biết site có lớp lưu tạm): đồng ý. `:330` dặn ảnh thử chụp ở nơi đã công khai (xưởng, cửa hàng), không dùng ảnh nhà khách; `:333` xóa ngay bài nháp và ảnh thử, chỉ đúng chỗ (**Bài viết → Nháp**, **Media → Thư viện**) |
| LC-T087-1 | **Đóng** | `README.md:309` thêm: đoạn ở tiêu đề bài, tiêu đề mục chưa sửa được ở bước Viết & kiểm tra (đúng: tiêu đề mục chỉ hiện `write.py:1654-1658`, ✏️ Sửa chỉ sửa thân đoạn `:1708-1716`), gửi xong xóa trong WordPress **trước khi** bấm Lưu hay Đăng. «Cách khác» (sửa ở Dàn ý, để AI viết lại) có nêu đúng hậu quả: viết lại tạo mục mới (`set_article` `:286-296`, mã mục mới), nên mất phần sửa tay, phải chọn lại ảnh, duyệt lại alt. Ghi chú: tiêu đề bài do AI viết lại (`seo_app/content/workflow.py:220`), nên cách này không chắc bỏ được đoạn ở tiêu đề bài; vẫn an toàn vì khung cảnh báo ở bước Xuất bản liệt kê lại nếu đoạn còn (Thư Ký đã ghi trong báo cáo). Không bắt buộc sửa thêm |
| D1 | **Đạt** | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-087-thu-ky.md`: `{}`; dòng thêm của diff không có khóa, mật khẩu, đường dẫn máy, email |
| Không sai sự thật | **Đạt** | Không câu mới nào hứa điều app chưa làm; không đụng khối «Lời dặn tạm thời» (`:326-329`, điều kiện 3 giữ cho lúc T-086 gộp) |
| Thử gộp | **Không xung đột** | `git merge-tree --write-tree`: `origin/main` `9a1308d`, `origin/team/T-085`, `origin/team/T-086`; `main` không sửa `README.md` từ gốc nhánh. `uv run ruff check .`: All checks passed! |

**Kết luận lượt 2: ĐẠT.** 0 lỗi còn mở; **gộp `main` được ngay**. Việc theo sau, không chặn: điều kiện 3 (Thư Ký viết lại «Lời dặn tạm thời» khi T-086 gộp), điều kiện 4 (kiểm lại bằng Claude Fable sau 01/11); 3 khuyến nghị và đề xuất gắn ảnh vào bài nháp (Thợ Máy, cần chủ dự án duyệt) để Chỉ Huy quyết.

## Kiểm lại lượt 3 (2026-10-26)

Thư Ký viết lại khối «Lời dặn tạm thời» sau khi T-086 gộp (điều kiện 3 biên bản này; điều kiện 5, 6 biên bản Lá Chắn T-086), nhánh `team/T-087-l3` (`4e4d301`, từ `main` `8eac87c`). Đọc `git diff 8eac87c..4e4d301 -- README.md` (chỉ mục 10) và mục «Lượt 3» báo cáo Thư Ký, đối chiếu `app/views/write.py` của `main` sau T-086. 18:09 → 18:12 +07, giờ máy.

| Điểm kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Khối mới «App nhớ việc đã gửi» đúng app hiện tại | **Đạt** | Ghi «đang gửi» vào nháp trước khi gửi, «đã gửi» kèm mã bài khi website trả lời (`send_and_record`, `record_outcome`), đọc lại mỗi lần vẽ nút gửi (`draft_panel`), như biên bản Lá Chắn T-086 mục «Đối chiếu điều kiện 2». 11 câu, nhãn README trích đều có nguyên văn trong `write.py` (`grep -cF` mỗi chuỗi = 1): «Bài này đã gửi lên WordPress (bài nháp mã …», «Gửi lại sẽ tạo thêm một bài nháp mới…», «… bài nháp có thể đã có trên website», ô «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi», «Tạo thêm một bài nháp mới», ô «⏳ Lần gửi nháp vừa bấm vẫn đang chạy…», «Lần gửi này bị ngắt giữa chừng», «Lần gửi nháp trước vẫn đang chạy (website chậm?)», 60 giây (`SEND_WAIT_SECONDS`), «Chưa gửi gì lên website: chưa ghi được trạng thái gửi vào nháp». Danh sách nguyên nhân «chưa có kết quả» (tải lại trang, đóng tab, mất mạng đúng lúc đang gửi, gửi ở cửa sổ khác) chép đúng ý câu của app (`unsure_message`); tải lại trang lúc đang gửi rồi mở lại sau khi lần gửi đã xong thì app hiện «đã gửi», cũng khóa: hướng an toàn |
| Không hứa điều app chưa làm | **Đạt** | Không nói app chặn được hai tab; không nói app nhận ra ảnh bị thay giữa hai lần mở nháp (băm ảnh hiện chỉ nhớ trong phiên, T-089); «Chưa gửi gì lên website» bỏ dấu chấm vì câu của app có hai dạng |
| Vẫn dặn một tab tới khi T-089 xong | **Đạt** | «**Lời dặn tạm thời** (tới khi app chặn được việc gửi cùng một bài từ hai tab)»: đừng mở cùng một bài ở hai tab rồi bấm gửi ở cả hai, mỗi lần gửi một tab (SL-T086-1, sửa ở T-089 yêu cầu 2) |
| Lần gửi thật đầu tiên | **Đạt** | «một bài, một ảnh, **một tab**», ảnh có GPS chụp ở nơi đã công khai (xưởng, cửa hàng), không dùng ảnh nhà khách; tải ảnh về kiểm GPS; kiểm xong xóa ngay (giữ nguyên câu đã sửa ở lượt 2, LC-T087-2) |
| D1 | **Đạt** | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-087-thu-ky.md`: `{}`; dòng thêm của diff không có khóa, mật khẩu, đường dẫn máy, email |
| Thử gộp | **Không xung đột** | `git merge-tree --write-tree` với `origin/main` `0735c5d`, `origin/team/T-041`, `origin/team/T-088`, `origin/team/T-089`; không nhánh nào trong đó sửa `README.md`. `uv run ruff check .`: All checks passed! |

**Kết luận lượt 3: ĐẠT.** 0 lỗi; **gộp `main` được ngay**. Việc theo sau, không chặn: khi T-089 gộp (chặn được hai tab), Thư Ký bỏ hay viết lại khối «Lời dặn tạm thời» (giữ lời dặn lần gửi thật đầu tiên tới khi T-059 xong); Lá Chắn kiểm lại biên bản này bằng Claude Fable sau 01/11.

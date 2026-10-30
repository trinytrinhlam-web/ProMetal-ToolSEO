# Biên bản bảo mật T-093 · Rà soát toàn bộ Giai đoạn 3 (ảnh) trước khi đóng giai đoạn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-093](../tickets/T-093-la-chan-ra-soat-giai-doan-3.md) · rà soát cả giai đoạn (yêu cầu 1–4) |
| Phạm vi | `main` trên máy `0122d4b` (nhánh `team/T-093` tạo từ `209615a`, tiến nhanh lên `0122d4b`: chỉ thêm T-104 `set_password`, không đổi mã ảnh). Đường ảnh: `seo_app/images/` (`folders.py`, `process.py`, `alt.py`, `tags.py`, `naming.py`, `html.py`), `seo_app/storage/drafts.py`, `seo_app/sanitize.py` (`sanitize_html`), `seo_app/wordpress/client.py` (phần ảnh), `app/views/write.py` (chỗ cần ảnh, gửi nháp), `app/views/settings.py` (tab Ảnh), `app/views/wordpress.py` (tạo thử bài nháp). Biên bản Lá Chắn T-046 → T-091 (kiểm kê ở Phụ lục), `docs/team/security.md` mục 6, kết quả thử thật T-059 |
| Ngày | 2026-10-29 01:51 → 02:00 (máy dừng), 2026-10-30 07:28 → 07:54 +07, giờ máy |
| **Kết luận** | **KHÔNG ĐẠT để đóng Giai đoạn 3 ngay.** Lỗi mới: 0 Nghiêm trọng, **1 Cao** (LC-T093-3: libheif 1.23.6 trong pillow-heif dính lỗ hổng đã biết, đường giải mã HEIC đang dùng), **1 Trung bình** (LC-T093-1: trang Kết nối WordPress tải nguyên file ảnh, bỏ qua quyết định 2A), **1 Thấp** (LC-T093-2: ảnh không gắn vào bài nháp, danh sách Media công khai; đã nêu ở LC-T087-2, chưa phiếu nào giữ). Đường ảnh chính (thư mục → xử lý → AI → nháp → WordPress) **đạt** F1, F2, A3, W2, W3, U1, U2. Đóng được sau 4 việc ở mục 5 |

## Tóm tắt (cho chủ dự án)

- **Đường ảnh chính của «Soạn bài» an toàn:** ảnh chỉ đọc trong thư mục đã khai báo; ảnh lên website dựng lại từ điểm ảnh, chỉ giữ GPS, ngày chụp, hãng, đời máy (đúng quyết định 2A); AI chỉ nhận bản ảnh sạch và vài thẻ cố định, không tên file, tên thư mục; chữ alt, chú thích, nội dung bài đều được lọc trước khi gửi, nên dù tài khoản Biên tập viên có quyền «HTML tự do» thì app cũng không đưa mã lạ lên website.
- **Cần làm trước khi đóng giai đoạn (4 việc):**
  1. **Gấp (Cao):** thư viện đọc ảnh HEIC của iPhone (libheif bản 1.23.6, nằm trong pillow-heif) có lỗ hổng vừa công bố ngày 26/10: một file HEIC dựng cố ý có thể làm app sập hay hỏng bộ nhớ. Chưa có bản pillow-heif mới để nâng. Cách chặn ngay: tắt giải mã song song (một dòng cấu hình) hoặc tạm tắt đọc HEIC (ảnh Zalo là JPEG nên gần như không ảnh hưởng). Khi pillow-heif có bản mới thì nâng (cần bạn duyệt).
  2. **Trung bình:** trang **Kết nối WordPress → Tạo thử một bài nháp** tải **nguyên file** ảnh bạn chọn: số seri máy, tên chủ máy, ảnh nhỏ nhúng trong file, chú thích ẩn… đều lên website công khai, và trang không nhắc ảnh (kể cả GPS) xem được ngay. Nên bỏ ô chọn ảnh ở trang này (đã có «Gửi nháp» làm đúng cách) hoặc cho ảnh đi qua đúng đường xử lý.
  3. Phần còn lại của việc nâng công cụ `uv` (máy Windows đã xong): thêm dòng chặn bản cũ vào cấu hình và hướng dẫn README.
  4. **Vài quyết định nhỏ của bạn:** gắn ảnh vào bài nháp hay chấp nhận ghi sổ (ảnh đã tải xem được trong danh sách Media công khai trước khi bài đăng); vài lỗi Thấp đang hoãn có ghi sổ rủi ro không (mục 4).
- Các việc khác (máy Mac, chạy thử trên Linux, cảnh báo quyền HTML trên trang Kết nối, kiểm lại bằng Fable) mang sang, không chặn đóng giai đoạn.

## 1. Điều kiện, lỗi Lá Chắn còn mở của Giai đoạn 3 (yêu cầu 1)

Kiểm kê đủ các biên bản T-046 → T-091 ở **Phụ lục**. Đối chiếu khách quan: mọi `xfail(strict=True)` còn trong `tests/` (`grep`), phần Giai đoạn 3 đúng bằng các mục «Mở» dưới đây (R2-1 = LC-T048-2, R2-2 = LC-T048-5, SL-T067-1 = LC-T067-1, SL-T070-4, SL-T080-L-1) cộng 3 test mới của biên bản này.

**Đóng ở biên bản này:**

| Mục | Kết quả |
|---|---|
| T-056 ĐK 6 (Lá Chắn rà soát cả giai đoạn) | Xong (biên bản này) |
| T-047 ĐK 3, LC-T058-4 (lượt quét cuối Giai đoạn 3) | Xong (mục 6): `pip-audit` 209 gói cố định, nguồn PyPI và OSV: không lỗ hổng; `uv pip check`: chỉ một chỗ lệch có chủ đích (Streamlit `pillow<13` với Pillow 13.0.0, quyết định T-058); thư viện C: libde265 1.1.3 là bản mới nhất; **libheif 1.23.6 dính lỗ hổng mới → LC-T093-3** |
| LC-T058-1 (GHSA-654x-cwwv-5j9c chưa vá cho Pillow 13.0.0) | **Đóng**: khuyến cáo nay ghi khoảng ảnh hưởng `>= 11.2.1, < 13.0.0`, bản vá «13.0.0» (cập nhật 23/10, GitHub Advisory Database). App vẫn không xuất ảnh sang Arrow (`process.py:31`) |
| T-091 ĐK 0 (Lá Chắn xem lại diff test lượt 2) | **Đạt (R5)**: `git diff ed5d86b af26c8a -- tests/`, 5 file. `test_t089_send_draft.py::assert_huge_id_reported_and_locked` đổi đúng phương án A Chỉ Huy duyệt 28/10 (mã từ 2⁶³ coi như sai khuôn: câu «bài nháp có thể đã có…»), giữ 1 bài, «đang gửi», nút khóa qua 2 lần chạy, **thêm** kiểm không câu nào, không lệnh nào mang mã đó; `test_wordpress_t085.py` trả lại 5 kiểm «không chép»; `test_la_chan_t091.py`, `test_soi_loi_t091.py` chỉ xóa dấu `xfail` (13 dòng, không xóa câu kiểm); `test_t091_don_client_wordpress.py` (file của Thợ Máy) thay ca ghim phép tắt bằng ca «luôn lọc sau khi giải mã» đúng cách sửa Lá Chắn đề xuất |

**Cần xong trước khi đóng giai đoạn:**

| Mục | Mức | Ai giữ | Việc |
|---|---|---|---|
| **LC-T093-3** (mới) | Cao | Chưa có phiếu (Thợ Máy) | Mục 3 |
| **LC-T093-1** (mới; phần còn lại của T-001 #3 đã dời sang Giai đoạn 3) | Trung bình | Chưa có phiếu (Họa Sĩ hay Thợ Máy) | Mục 3 |
| LC-T075-1 phần còn lại: `required-version = ">=0.13.4"` trong `pyproject.toml`, README cách nâng `uv` | Cao (gốc) | T-078 (phần Thợ Máy, Thư Ký **chưa giao**) | Máy Windows đã xong (`uv 0.13.4`, kiểm 30/10). `pyproject.toml` chưa có `required-version` |
| Quyết định của chủ dự án cho các lỗi Thấp chưa sửa, chưa ghi sổ: LC-T093-2; LC-T052-5 và SL-T070-4 (T-070 ĐK 4); T-047 lỗi số 2, số 3; LC-T061-4 | Thấp | Chủ dự án | Sửa hay ghi sổ (mục 4 có câu đề xuất). Theo `security.md` mục 3, lỗi Thấp không sửa thì vào sổ rủi ro |

**Mang sang, không chặn đóng giai đoạn (đã có phiếu hay hạn sau):**

| Mục | Ai giữ / hạn |
|---|---|
| LC-T048-2, -3, -4 (c), -5 | T-064 (Hoãn, chủ dự án chốt 20/10) |
| LC-T067-1 | T-072 (Hoãn, 20/10) |
| T-049 ĐK 5; T-051 C8, C9; T-062 ĐK 5; góp ý 6 của T-046 (ảnh AI) | T-053 (Hoãn, 20/10): áp dụng khi làm tạo ảnh AI |
| T-059 ĐK 2 = T-091 ĐK 3: cảnh báo quyền `unfiltered_html` trên trang Kết nối WordPress (client xong ở T-091) | Họa Sĩ, **chưa lập phiếu**; hạn trước khi hết Giai đoạn 4 |
| T-089 Ghi nhận lượt 4 số 2 (nháp bị xóa ở tab khác); T-084 tùy chọn `client.showErrorDetails = "type"` | T-092 (Chờ) |
| T-091 ĐK 2 phần còn lại (`SiteIndexStore.save` bắt `OverflowError`; Ghi nhận 1, 3); T-091 ĐK 4 (thử thật tiêu đề «< 5 triệu», `srcset`) | Phiếu dọn client sau, lượt thử thật kế tiếp (Giai đoạn 4) |
| Chạy bộ test thư mục ảnh, nháp ảnh trên **máy Mac thật** (LC-T048-1 phần Mac; T-052 ĐK 5 tên NFD; T-055 ĐK 4; T-063 ĐK 3 = T-079 ĐK 2 = T-080 ĐK 3; T-076 phần Mac) | T-063 phần Mac, chờ máy Mac (chủ dự án chưa có máy từ 22/10). Tới lúc đó **chưa dùng app trên Mac** |
| Lượt Linux/Mac của SL-T080-L-1 (6 `xfail` trong `tests/test_soi_loi_t080_linux.py`, 16 ca mới chưa chạy), T-082 ĐK 1 | Cần chủ dự án cho chạy cloud, hoặc máy Mac |
| Đối chiếu 8 chứng chỉ trung gian bị lộ với danh sách chặn của Windows, macOS (đề xuất T-075) | Lá Chắn, cùng T-078 |
| Không bắt buộc: module dùng chung thay hai bản hàm chép (T-084); câu chú thích `base.py` (T-066 Đề nghị 3); 3 khuyến nghị README (T-087); T-089 Ghi nhận lượt 4 số 1; sửa câu chữ phiếu T-060 về `index.php` (T-060 ĐK 4, Chỉ Huy) | — |
| Không rõ (không thấy ghi kết quả): T-061 ĐK 2 phần thử vòng sửa `[caption]` trong trang quản trị; T-049 ĐK 7 phần ảnh HEIC, MPO thật (chưa có file) | Lượt thử thật kế tiếp |
| Kiểm lại mọi biên bản Giai đoạn 3 bằng Claude Fable sau 01/11 | Lá Chắn. Danh sách ở `docs/team/board.md` (dòng «Fable») mới tới T-068, thiếu T-055, T-056, T-059 → T-091 (Chỉ Huy bổ sung) |

## 2. Rà chéo chỗ nối của đường ảnh (yêu cầu 2)

| Chỗ nối | Kết quả | Bằng chứng |
|---|---|---|
| Thư mục → xử lý (F1, F2) | **Đạt** (trừ LC-T093-3) | Byte chỉ qua `ImageLibrary.read_image_bytes` (đọc chống tráo thư mục T-079, T-080, T-082; giới hạn dung lượng); `process.py` nhận định dạng theo nội dung (`ALLOWED_FORMATS`, `:60`), giới hạn 80 triệu điểm ảnh kể cả HEIC trước khi giải mã, bắt lỗi giải mã thành câu cố định; HEIF đăng ký một chỗ, tắt ảnh nhỏ, ảnh độ sâu, ảnh phụ (`_register_heif`, `:128-139`) nhưng để `DECODE_THREADS` mặc định 4 → LC-T093-3 |
| Xử lý → WordPress (quyết định 2A, 5A) | **Đạt** cho «Gửi nháp»; **không đạt** ở đường phụ (LC-T093-1) | `make_web_image` (`:769`) dựng lại từ điểm ảnh, EXIF dựng mới theo danh sách giữ (`_KeptExif`: GPS so lại từng giá trị sau khi nén, ngày chụp, hãng, đời máy); không IFD1, số seri, tên chủ máy, MakerNote, XMP, chú thích; chỉ hồ sơ màu RGB. Byte tải đúng bằng byte đã băm lúc duyệt (T-086, T-089). Trang Kết nối WordPress thì tải nguyên file (`app/views/wordpress.py:124-135`) |
| Xử lý → AI viết alt (A3) | **Đạt** | AI nhận `make_ai_image(read_image_bytes(ref))` (`write.py:1032`), qua lớp kiểm `prepare_images` (`ai/base.py:491`; phần còn lại của LC-T050-2 đã ghi sổ). Chữ đi kèm chỉ là thẻ (giá trị trong danh sách cố định: `ImageTags`, mã `CT` + số, hạng mục, quận) và từ khóa, qua `_short_text` (chữ Latin, số, dấu cho phép, không giống đường dẫn); không tên file, tên thư mục |
| AI → nháp, giao diện (U1) | **Đạt** | Gợi ý qua `clean_suggestion`; hiện bằng `escape_markdown`; ô «✅ Đã duyệt» ghi băm của đúng bản ảnh đang hiện (`altsha-<id>`), lưu `approved_sha256` trong nháp; mở lại mà ảnh khác thì bỏ duyệt (T-089). Nháp đọc lại qua khuôn chặt, `clean_loaded` |
| Nháp → WordPress (W2, W3) | **Đạt** | `figure_html` (`html.py:115`): `src` phải `https://`, không khoảng trắng, nháy, `<>`, `\`, dấu phẩy, qua `is_safe_url`; alt, chú thích thành chữ thường rồi `html.escape`; `srcset` chỉ chính file đầy đủ `1x` (T-059); qua `sanitize_html` rồi kiểm lại thẻ `<img>`. `sanitize_html` (`sanitize.py:792`) dựng lại HTML từ đầu theo danh sách cho phép: không `style`, không thuộc tính sự kiện, `href`/`src`/`cite`/`srcset` qua `is_safe_url` (giải mã ký tự, bỏ khoảng trắng, ký tự điều khiển), chữ escape, «[», «]» thành mã ký tự. Media: `alt_text` chữ thường, tiêu đề, chú thích `html.escape` + `escape_shortcodes`, `source_url` phải `https` trên đúng website (`_describe_draft_media`, `client.py:1437`). Chỉ ghi vào ảnh, bài vừa tạo (T-060, T-085) |
| Quyền `unfiltered_html` của tài khoản Biên tập viên × lớp lọc của app | **Đạt** | WordPress không lọc lại HTML của tài khoản này, nên lớp lọc của app là lớp duy nhất; đã đọc lại cả hai đường (`create_draft` với `sanitize_html`, `figure_html`, Media): không đường nào gửi HTML chưa lọc. Hệ quả khi lộ mật khẩu ứng dụng: mục 4 |
| WordPress → giao diện (U1, U2) | **Đạt** | Kết quả gửi: câu cố định, chữ từ website qua `escape_markdown`; danh sách ảnh đã tải hiện bằng `st.text`; không đường dẫn máy; lỗi client là câu cố định (T-060, T-088) |
| Ảnh công khai sớm (GPS) | **Còn LC-T093-2** | Câu nhắc trước nút gửi nói ảnh «xem được công khai **qua đường dẫn**» (`write.py:218`), nhưng ảnh không gắn bài (không gửi `post`) nên `GET /wp/v2/media` không cần đăng nhập liệt kê được (LC-T087-2: README đã sửa, câu trên giao diện và đề xuất gắn ảnh chưa ai giữ) |
| Tên thư mục, đường dẫn (U2) | **Đạt** | Soạn bài và Cài đặt chỉ hiện tên tầng cuối qua cùng một luật (hai bản hàm chép có test giữ, T-084); `ImageLibrary.__repr__` không in đường dẫn; không `print`, `logging` nào trong `seo_app/images`, `seo_app/storage`, `seo_app/wordpress`, `write.py`, `settings.py` |
| Tên file tải lên | **Đạt** | `image_file_name` chỉ từ thẻ (danh sách cố định) và alt đã duyệt, không từ tên file gốc (`naming.py`). Riêng đường phụ của trang Kết nối WordPress lấy tên file gốc (LC-T093-1) |
| Dữ liệu trên máy (D2) | **Đạt** | `data/`, `*.sqlite` trong `.gitignore`; nháp, thẻ sửa tay, ảnh xem trước chỉ trên máy |

## 3. Lỗi tìm thấy

Test `xfail(strict=True)` trong `tests/test_la_chan_t093.py` (commit `a1c075a`, `78cdf91`); `--runxfail`: cả ba hỏng đúng câu kiểm.

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| **LC-T093-3** | **Cao** (`security.md` mục 3: «thư viện có lỗ hổng đã biết đang bị dùng tới») | pillow-heif 1.8.1 (bản mới nhất trên PyPI, kiểm 30/10) mang sẵn **libheif 1.23.6**. libheif 1.23.7 (phát hành 26/10) là bản vá bảo mật: **GHSA-35mc-3887-rr37** (cao, CVSS 7.5, **chỉ 1.23.6**: dùng vùng nhớ đã giải phóng khi giải mã song song các ô ảnh lưới có chung một mục mã hóa, với tùy chọn mặc định; hậu quả sập, hỏng heap, chưa ai chứng minh chạy được mã), cùng nhiều lỗi «làm treo CPU» mức cao (file vài kB giải mã hàng chục giây). `pip-audit` không thấy vì lỗi nằm ở thư viện C trong wheel (đúng lý do T-047, T-058 bắt quét riêng thư viện C) | `test_lc_t093_3_heic_decoding_not_exposed_to_libheif_1_23_6`: đăng ký HEIF như app (`_register_heif`): HEIF bật, `libheif_info()["libheif"] == "1.23.6"`, `DECODE_THREADS == 4`. Đường thật: file HEIC dựng cố ý nằm trong thư mục ảnh (Drive chung, file nhận qua Zalo, USB), người dùng duyệt thư mục đó → app dựng ảnh xem trước → libheif giải mã song song (ảnh iPhone vốn là ảnh lưới nên đường giải mã song song là đường thường ngày) | Không giải mã HEIC bằng libheif 1.23.6 với giải mã song song | HEIF bật, 1.23.6, 4 luồng | **Ngay:** tắt giải mã song song theo đúng cách tránh của khuyến cáo (`heif_context_set_max_decoding_threads(ctx, 0)`): trong `_register_heif` đặt `heif_options.DECODE_THREADS = 0` (pillow-heif truyền giá trị này vào `_pillow_heif.load_file`, `heif.py:319-321`), hoặc tạm bỏ `"HEIF"` khỏi `ALLOWED_FORMATS` (ảnh Zalo là JPEG; chưa có ảnh HEIC thật nào được dùng, T-049 ĐK 7). **Sau:** khi pillow-heif có bản mang libheif ≥ 1.23.7 thì nâng (thư viện: chủ dự án duyệt, Lá Chắn rút gọn D1); lúc đó các lỗi «làm treo CPU» mới hết. Test chấp nhận cả ba cách |
| **LC-T093-1** | **Trung bình** (phần còn lại của T-001 #3, mức Trung bình, đã dời sang Giai đoạn 3: `T-003-006-008-009-la-chan.md:75`) | Trang **Kết nối WordPress → Tạo thử một bài nháp** (`app/views/wordpress.py:124-135`) gửi `upload_media(image.getvalue(), image.name)`: nguyên byte file người dùng chọn, không qua `make_web_image`. Số seri máy, tên chủ máy, MakerNote, XMP, chú thích, IPTC, ảnh nhỏ IFD1 (có thể là ảnh **trước khi** cắt, che) lên thư viện Media công khai ngay; tên file gốc thành tên trên website (`slugify`, ví dụ `nha-anh-tuan-0909….jpg`); chỉ xét đuôi file, không kiểm định dạng thật, không giới hạn cỡ ngoài mặc định 200 MB của Streamlit. Trang và README (`:115-117`) dặn «tạo thử một bài nháp có ảnh đại diện», nói «khách không thấy bài», **không** nhắc ảnh (kể cả GPS) công khai ngay như câu nhắc của «Gửi nháp» | `test_lc_t093_1_wordpress_page_upload_follows_decision_2a`: mở trang, chọn file JPEG có đủ metadata (bộ dữ liệu `_jpeg_day_du` của `tests/test_images_process.py`), bấm «Tạo bài nháp»: byte tới `upload_media` còn đủ 12 dấu (`SERIAL-BODY-123`, `Nguyen Van Chu May`, `MAKERNOTE-RIENG`, `XMP-BI-MAT`, `ANH-NHO-IFD1`…) | Ảnh lên website từ mọi đường đều theo quyết định 2A, có câu nhắc công khai trước nút | Nguyên file | **Cách gọn (khuyên):** bỏ ô chọn ảnh khỏi mục tạo thử (mục đích là thử kết nối; «Gửi nháp» ở Soạn bài đã là đường ảnh đúng), sửa câu README `:115`. **Hoặc:** cho ảnh đi qua `open_image`/`make_web_image` (2A, giới hạn cỡ, định dạng thật), tên file không lấy từ tên gốc, thêm `GPS_PUBLIC_WARNING` trước nút. Test chấp nhận cả hai (không còn tải thì đạt) |
| **LC-T093-2** | **Thấp** (đã nêu ở LC-T087-2 và Đề xuất 4 của biên bản T-087; phần README đã sửa, phần còn lại chưa phiếu nào giữ) | Ảnh «Gửi nháp» không gắn vào bài nháp (không lệnh nào gửi `post`; `_describe_draft_media` chỉ gửi alt, tiêu đề, chú thích). WordPress lõi (`class-wp-rest-posts-controller.php`, `check_read_permission`, đọc mã trunk công khai 29/10): mục `inherit` không có bài cha thì ai cũng đọc được, nên `GET /wp-json/wp/v2/media` không cần đăng nhập liệt kê mọi ảnh app đã tải (`source_url` còn GPS), kể cả của bài chưa đăng, bài bỏ dở, lần gửi hỏng. Câu nhắc trên giao diện vẫn nói «qua đường dẫn» (`write.py:218-220`) | `test_lc_t093_2_uploaded_images_attached_to_new_draft`: gửi nháp một ảnh tới WordPress giả có ghi bài cha: ảnh 101 không có bài cha (`{101: None}`, mong `{101: 42}`) | Ảnh của bài nháp có bài cha là bài đó (danh sách Media công khai không có tới khi bài đăng) | Không có bài cha | Thợ Máy: sau khi tạo nháp, `POST /wp/v2/media/<mã>` với `post = <mã bài nháp>` cho đúng ảnh vừa tạo (giữ chốt T-060, T-085: chỉ ảnh vừa tạo, khóa JSON cố định); Họa Sĩ: câu `GPS_PUBLIC_WARNING` nói đúng như README (thư viện Media ai cũng xem được). Đường dẫn trực tiếp vẫn mở được, tên file đoán được: chỉ bớt đường tìm thấy. Nếu chủ dự án chọn chấp nhận: ghi sổ (mục 4, dòng N4) rồi Lá Chắn gỡ test |

## 4. Sổ rủi ro mục 6 (yêu cầu 3)

| Dòng | Còn đúng không | Đề xuất |
|---|---|---|
| 2026-10-14 · ảnh tải lên giữ GPS | **Đúng** | Có thể thêm cho rõ (chủ dự án quyết): ảnh vào thư viện Media là công khai ngay, kể cả bài nháp và lần gửi hỏng; danh sách Media xem được không cần đăng nhập (LC-T087-2, LC-T093-2); bản thu nhỏ WordPress tự tạo không còn GPS, ảnh đại diện của theme dùng bản này (chủ dự án chấp nhận 28/10); ảnh trong bài ghi sẵn `srcset` file đầy đủ (T-059) |
| 2026-10-15, 2026-10-28 · biến proxy, chứng chỉ của máy | **Đúng** | — |
| 2026-10-28 · quyền `unfiltered_html` | **Đúng về cơ chế, câu hậu quả nên rõ hơn** | Câu «chèn được mã chạy trên trang bài (không vào được trang quản trị)» chỉ đúng nửa: mật khẩu ứng dụng không đăng nhập được trang quản trị, **nhưng** mã chèn vào bài chạy trong phiên của người đang đăng nhập mở bài đó (kể cả quản trị viên), nên làm thay họ được việc quản trị. Đề nghị: «… chèn được mã chạy trên trang bài; mã chạy trong phiên của người đang đăng nhập xem bài (kể cả quản trị viên), nên có thể làm thay họ việc quản trị.» Ghi thêm: HTML app gửi chỉ qua lớp lọc của app (T-093 đọc lại: đạt); cảnh báo quyền trên giao diện còn chờ (T-091 ĐK 3) |
| 2026-10-20 · LC-T048-6 (hard link; ổ không có số inode) | **Đúng về nội dung; số dòng đã cũ** | `folders.py:163`, `:644` nay là dòng trống và một lệnh `raise`. Đề nghị thay bằng tên hàm: «phép so "cùng một file" (`_same_file` trong `folders.py`: ổ không có số inode thì luôn coi là cùng)» |
| 2026-10-23 · thư mục dời vào gốc (T-079) | **Đúng** | — |
| 2026-10-23 · ảnh dựng cố ý qua lớp kiểm ảnh gửi AI | **Đúng** | `prepare_images` (`ai/base.py:491`); app chỉ gửi bản `make_ai_image` (`write.py:1032`) |
| **Dòng mới đề xuất** (chủ dự án quyết, mỗi dòng: sửa hay ghi sổ) | | **N1 · LC-T061-4:** sửa và lưu bài trong trình soạn của WordPress có thể đưa «[» trần trở lại (mã ký tự app ghi bị giải mã), nên shortcode có thể chạy sau khi người dùng tự sửa bài; giảm bởi cảnh báo liệt kê đoạn dạng shortcode trước khi gửi (T-056) và Code Snippets 4.0.0 đã tắt chạy theo file. **N2 · T-047 lỗi số 2:** hai mục OSS-Fuzz của libheif (OSV-2020-2308, OSV-2023-1129) vẫn chưa có bản sửa (kiểm 30/10: cả v1.23.7 vẫn trong danh sách ảnh hưởng); hậu quả có thể sập app khi giải mã HEIC dựng cố ý; xem lại mỗi cuối giai đoạn. **N3 · T-047 lỗi số 3:** wheel pillow-heif mang mã chịu giấy phép GPLv2 (bộ mã hóa x265); app không phát hành ra ngoài nên chỉ là lưu ý. **N4 · LC-T093-2** nếu chọn không gắn ảnh vào bài. **N5 · LC-T052-5** (khe file `-journal` của SQLite) **và SL-T070-4** nếu chọn không sửa |

## 5. Kết luận giai đoạn (yêu cầu 4)

**Giai đoạn 3 chưa đóng được ngay.** Đường ảnh chính đạt mọi điều kiện bảo mật đã đặt từ T-046 tới T-091; chỗ hở nằm ở thư viện C (mới công bố) và ở một đường phụ có từ Giai đoạn 1 mà các phiếu Giai đoạn 3 chưa nối tới. Đóng được khi đủ:

1. **LC-T093-3 (Cao):** phiếu gấp cho Thợ Máy: `DECODE_THREADS = 0` (hay tạm tắt HEIF), gỡ `xfail`; Soi Lỗi, Lá Chắn rút gọn. Theo dõi bản pillow-heif mang libheif ≥ 1.23.7 để nâng (chủ dự án duyệt).
2. **LC-T093-1 (Trung bình):** phiếu sửa trang Kết nối WordPress (khuyên bỏ ô chọn ảnh ở mục tạo thử, sửa README `:115`), gỡ `xfail`; hoặc chủ dự án chấp nhận và ghi sổ.
3. **T-078 phần còn lại:** giao Thợ Máy (`required-version`), Thư Ký (README); phần máy Mac chờ máy.
4. **Quyết định của chủ dự án** cho LC-T093-2 và các dòng N1 → N5 (sửa hay ghi sổ), và xác nhận mang sang các phiếu hoãn T-064, T-072, T-053, phần Mac, phần Linux.

Không chặn đóng (mang sang): cảnh báo `unfiltered_html` trên giao diện (Họa Sĩ, lập phiếu, hạn trước khi hết Giai đoạn 4), T-092, phiếu dọn client Giai đoạn 4, chạy test trên Mac (tới lúc đó chưa dùng app trên Mac), lượt Linux cần cloud, kiểm lại bằng Fable sau 01/11.

## 6. Kết quả công cụ quét, test

| Công cụ | Kết quả |
|---|---|
| `pip-audit` | `uv export --no-hashes --no-emit-project` (209 gói cố định), `uvx pip-audit -r … --no-deps --disable-pip` (chạy với bộ giải phụ thuộc thì vấp chỗ lệch có chủ đích của Pillow): nguồn PyPI và nguồn OSV đều «No known vulnerabilities found» |
| Phiên bản (`.venv` của nhánh) | Pillow 13.0.0, pillow-heif 1.8.1 (libheif 1.23.6, libde265 1.1.3, x265 4.3), streamlit 1.65.0, requests 2.34.2, certifi 2026.10.19, urllib3 2.8.0; `uv 0.13.4` trên máy |
| `uv pip check` | 1 chỗ lệch: Streamlit cần `pillow<13`, có 13.0.0 (có chủ đích, T-058) |
| Thư viện C | libheif: GHSA của 1.23.7 (đọc trang phát hành, GHSA-35mc-3887-rr37) → LC-T093-3; OSV-2020-2308, OSV-2023-1129 vẫn không có bản sửa (N2). libde265: 1.1.3 là bản mới nhất, đã có các bản vá của 1.1.1, 1.1.2 |
| detect-secrets (`PYTHONUTF8=1`) | `{}`: `tests/test_la_chan_t093.py`, biên bản này |
| ruff | `uv run ruff check .`: All checks passed! |
| pytest (chọn lọc, máy đang chạy toàn bộ test của `main`) | `tests/test_la_chan_t093.py`, `tests/test_app_wordpress.py`, `tests/test_pillow_heif_setup.py`: 8 qua, 3 xfail (LC-T093-1, -2, -3), 0 hỏng; `--runxfail`: 3 ca hỏng đúng câu kiểm. Test của LC-T093-3 trả lại bảng định dạng của Pillow, tùy chọn pillow-heif (`test_pillow_heif_setup.py` chạy sau vẫn qua, không bị bỏ) |
| Soát R5 | Không sửa, không xóa test của agent khác; chỉ thêm `tests/test_la_chan_t093.py` |

## Ghi nhận (không phải lỗi)

1. Kiểm kê ở Phụ lục do hai agent phụ đọc biên bản lập (chỉ đọc). Lá Chắn đã kiểm lại mọi mục «Mở», «Không rõ» dùng ở mục 1 (đối chiếu `xfail`, phiếu, `board.md`, mã) và sửa bốn mục đóng ở biên bản này.
2. `docs/team/board.md` còn ghi T-104 «đang làm» dù đã gộp ở `0122d4b`; danh sách «Fable» thiếu nhiều phiếu (Chỉ Huy sửa; Lá Chắn không sửa `board.md`).
3. Nhánh `team/T-093` dựa trên `main` trên máy chưa push (`0122d4b`) nên chỉ commit, chưa push.

## Phụ lục · Kiểm kê điều kiện, lỗi Lá Chắn Giai đoạn 3 (T-046 → T-091)

Viết gọn: «Đóng (T-xxx)» = đóng ở phiếu đó; ĐK = điều kiện. Mục nào cũng kèm «kiểm lại bằng Fable sau 01/11» (một dòng chung ở mục 1).

| Biên bản | Trạng thái |
|---|---|
| T-046 | Không lỗi, không ĐK. Góp ý 6 (ảnh AI) → T-053 (Hoãn) |
| T-047 | Lỗi 1 (Pillow 12.3.0) Đóng (T-058). Lỗi 2 (2 mục OSS-Fuzz libheif) **Mở**: kiểm 30/10 vẫn chưa có bản sửa → N2. Lỗi 3 (GPLv2) **Mở** → N3. ĐK 1, 2 Đóng (T-058, T-049). ĐK 3 (quét cuối GĐ3) Đóng (T-093) |
| T-048 | LC-T048-1 Đóng phần Linux (T-063, T-079), Mac chờ máy. LC-T048-2, -3, -4 (c), -5 **Mở** → T-064 (Hoãn); -4 (a), (b) Đóng (T-052, T-056); -6 Đã ghi sổ. ĐK 2: -6 ghi sổ, -2/-3 → T-064. ĐK 3 → T-064 (gồm bọc `os.fstat`). ĐK 4 Đóng |
| T-049 | LC-T049-1 → -3 Đóng (T-067); LC-T049-4 Đóng (`security.md` mục 5). ĐK 3, 4, 6 Đóng; ĐK 5 → T-053 (Hoãn); ĐK 7 Đóng một phần (chưa có ảnh HEIC, MPO thật) |
| T-050 | LC-T050-1, -3 Đóng (T-066); -2 Đóng phần sửa được, phần còn lại đã ghi sổ; -4 Đóng (T-069); SL-T050-1, -2 Đóng. ĐK 2 → 6 Đóng |
| T-051 | LC-T051-1, -2 Đóng (T-065, T-062). C2 → C7 Đóng (T-062). C8, C9 → T-053 (Hoãn) |
| T-052 | LC-T052-1, -2, -3 Đóng (T-070, T-074, T-056); -4 Đóng (README; gợi ý cảnh báo ở Cài đặt không bắt buộc); **-5 Mở** (chủ dự án chưa quyết) → N5. ĐK 1 → 4 Đóng; ĐK 5 Linux Đóng, Mac (NFD) chờ máy |
| T-054 | LC-T054-1 → -6 Đóng (T-061, T-071, T-060). ĐK 1 → 6 Đóng (ĐK 6 ở T-059) |
| T-055 | LC-T055-1 Đóng trên Windows, Linux (T-076), Mac chờ; LC-T055-2, -3, -4, SL-T055-1 Đóng. ĐK 2, 3, 5 Đóng; ĐK 4 Mac chờ |
| T-056 | LC-T056-1, SL-T056-8 → -11 Đóng (T-086, T-089). ĐK 1 → 5 Đóng; ĐK 6 Đóng (T-093) |
| T-058 | LC-T058-1 Đóng (T-093: GHSA-654x nay ghi vá ở 13.0.0); LC-T058-2, -3 Đóng; LC-T058-4 / ĐK 4 Đóng (T-093). ĐK 1, 2 Đóng; ĐK 3 không phát sinh |
| T-059 | SL-T059-1 Đóng (T-091). ĐK 3 Đóng. **ĐK 2 Mở** (cảnh báo `unfiltered_html`: client xong T-091, giao diện chưa; hạn trước hết GĐ4) |
| T-060 | LC-T060-1 → -3, SL-T060-1 Đóng (T-085, T-088). ĐK 4 (câu chữ phiếu về `index.php`) Mở, không bắt buộc |
| T-061 | LC-T061-1 Đóng (T-075); -2, -3, -5 Đóng (T-060, T-085); **-4 Mở** (đã giảm thiểu) → N1. ĐK 2: phần thử vòng sửa `[caption]` không thấy ghi kết quả |
| T-062 | LC-T062-1, SL-T062-1 → -3 Đóng (T-065, T-068). ĐK 3, 4 Đóng; ĐK 5 → T-053 |
| T-063 | SL-T063-1 → -5 Đóng (T-076, T-079). ĐK 2 Đóng (cách A); ĐK 3 (Mac) chờ máy |
| T-065 | Đóng (SL-T065-1 sửa ở lượt 2) |
| T-066 | Đóng; Đề nghị 1, 2 Đóng; Đề nghị 3 (câu chú thích `base.py`) không bắt buộc |
| T-067 | **LC-T067-1 Mở** → T-072 (Hoãn). ĐK 2, 3 Đóng |
| T-068 | LC-T068-1, SL-T068-1 → -3 Đóng (T-083). ĐK 1, 2 Đóng |
| T-069 | LC-T069-1, -2 Đóng (T-087). ĐK 1, 2 Đóng |
| T-070 | LC-T070-1, -2, SL-T070-2, -3, -5 Đóng (T-074); **SL-T070-4 Mở** (`xfail`, hoãn) → N5. ĐK 1 → 3 Đóng; **ĐK 4 Mở** (chủ dự án quyết SL-T070-4, LC-T052-5) |
| T-071 | LC-T071-1, SL-T071-1 Đóng (T-060, T-081). ĐK 1 → 4 Đóng (ĐK 4 ở T-059) |
| T-074 | LC-T074-1, SL-T074-1 Đóng (T-077). ĐK 1 → 4 Đóng |
| T-075 | **LC-T075-1 (Cao) Mở một phần**: máy Windows xong (`uv 0.13.4`), còn `required-version`, README (T-078, chưa giao), máy Mac (chưa có). Đề xuất đối chiếu 8 chứng chỉ trung gian bị lộ: chưa làm (T-078) |
| T-076 | LC-T076-1 → -3 Đóng (T-076 lượt 2, T-079). ĐK Đóng trừ phần Mac (T-063) |
| T-077 | Đóng |
| T-079 | LC-T079-1 → -3 Đóng (T-080). ĐK 1 Đóng; ĐK 2 (Mac) chờ máy; ĐK 3 Đã ghi sổ |
| T-080 | SL-T080-1, -2 Đóng (T-082); SL-T080-L-1 Đóng trên Windows, Linux/Mac chưa chạy lại (6 `xfail`). ĐK 1, 2 Đóng; ĐK 3 (Mac) chờ máy |
| T-081 | SL-T081-1 Đóng (T-083) |
| T-082 | SL-T082-1, -2 Đóng (lượt 2). **ĐK 1 Mở** (lượt Linux/Mac: gỡ 6 `xfail` SL-T080-L-1, chạy 16 ca mới; cần cloud hay máy Mac) |
| T-083 | SL-T083-1 Đóng (lượt 2) |
| T-084 | SL-T084-1 Đóng (T-090). ĐK 1, 2 Đóng; tùy chọn `showErrorDetails` → T-092 (Chờ); module dùng chung không bắt buộc |
| T-085 | LC-T085-1, SL-T085-1 → -3 Đóng (T-088) |
| T-086 | LC-T086-1, SL-T086-1, -2 Đóng (T-089). ĐK 1 → 6 Đóng |
| T-087 | LC-T087-1, -2 Đóng (README). **ĐK 1 phần giao diện Mở** (câu `GPS_PUBLIC_WARNING`) và Đề xuất 4 (gắn ảnh vào bài nháp) chưa quyết → gom vào LC-T093-2. ĐK 3 Đóng; khuyến nghị 1 → 3 không bắt buộc |
| T-088 | SL-T088-1 Đóng (T-091). ĐK 1 Đóng |
| T-089 | SL-T089-1, -2, LC-T089-1 Đóng; mọi ĐK Đóng (README sau T-089). Ghi nhận lượt 4 số 2 → T-092 (Chờ); số 1 không bắt buộc |
| T-090 | LC-T090-1, -2 Đóng (T-104) |
| T-091 | LC-T091-1, SL-T091-1 → -3 Đóng. ĐK 0 Đóng (T-093); ĐK 1 Đóng; ĐK 2 phần còn lại chưa có phiếu (GĐ4); **ĐK 3 Mở** (= T-059 ĐK 2); ĐK 4 chờ lượt thử thật kế tiếp |

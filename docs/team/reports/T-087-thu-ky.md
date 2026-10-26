# Báo cáo T-087 · README: chọn ảnh, ảnh AI, ảnh công khai khi gửi nháp

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-087](../tickets/T-087-readme-chon-anh.md) |
| Ngày nộp | 2026-10-26 · lượt 2: 2026-10-26 (sửa LC-T087-1, -2 của Lá Chắn, mục «Lượt 2» cuối báo cáo) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

README có thêm hai mục cho màn hình chọn ảnh vừa gộp:

- **Mục 9 «Chọn ảnh cho bài»:** cách mở thư mục và chọn ảnh ở chỗ cần ảnh; cách đọc dấu Ảnh thật / Ảnh AI (kèm lý do), thẻ, vị trí GPS; nút «AI viết alt» (chỉ gửi đúng ảnh đó, bản đã bỏ GPS và thông tin máy chụp); tick «Đã duyệt». Phần ảnh AI: tạo ngoài app (ví dụ Gemini), lưu vào thư mục có chữ «AI» hay «minh họa». Nút «Đây là ảnh AI» không đổi lại được trong app, và dấu này chỉ nhớ trên máy đang dùng.
- **Mục 10 «Gửi bài nháp lên WordPress»:** «Gửi nháp» chỉ tạo bài nháp. Ảnh (kể cả GPS) xem được công khai ngay khi tải lên, và app không tự xóa ảnh. Mục này còn có: danh sách đoạn `[...]` nên xóa, cách làm khi lỗi giữa chừng, lời dặn tạm thời (đợi kết quả, không tải lại trang, không bấm nút khác), và cách kiểm GPS ở lần gửi thật đầu tiên.

Các câu cũ của T-069 nói «chưa có màn hình chọn ảnh» đã sửa cho đúng app hiện nay. Đã sửa luôn hai điều kiện Lá Chắn T-069 còn mở: LC-T069-2 (mất dấu «ảnh AI» gắn tay) và LC-T069-1 (thư mục phần mềm có cả `.env`, đừng để trong Google Drive, OneDrive). Hai mục cũ đổi số: «Cập nhật phiên bản mới» thành 11, «Xử lý sự cố» thành 12. Không chỗ nào trỏ tới hai mục này theo số.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md` | Thêm mục 9 (dòng 269–301) và mục 10 (dòng 303–333). Sửa phần đầu (dòng 7, 16, 46), mục 7 (dòng 97, 139, 161–162), mục 8 (dòng 202, 213–215, 242–243, 251, 258–259, 265–267). Đổi số mục 9, 10 cũ thành 11, 12 |
| `docs/team/reports/T-087-thu-ky.md` | Báo cáo này |

Không sửa code, `config/**`, `.env.example`. Không thấy thiếu biến nào trong `.env.example` (phiếu này không có biến mới).

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_pages.py \
    tests/test_app_images.py::test_ai_root_folder_makes_every_image_ai \
    tests/test_app_images.py::test_mark_ai_saves_manual_tag_and_rewrites_alt \
    tests/test_app_images.py::test_send_draft_with_real_image -q
21 passed in 55.01s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan README.md
results: {}   (0 mục)
# Mồi: bản sao README (có chữ tiếng Việt, ngoài repo) thêm khóa giả AWS và ANTHROPIC_API_KEY giả
# → bắt đủ: AWS Access Key, Base64 High Entropy String, Secret Keyword. Đã xóa bản mồi.

$ git diff README.md | grep -E "^\+" | grep -inE "api[_-]?key|password|secret|token|Users/|ADMIN|ProMetal-ToolSEO|@|C:/|D:/|sk-|AKIA"
3:+2. Chọn **File → Clone repository**, chọn `ProMetal-ToolSEO`, …
# Chỉ trúng tên repo có sẵn trong dòng cũ, không phải đường dẫn máy.
```

Không có test đọc README. Ba test ảnh ở trên làm chứng cho các câu README: thư mục gốc tên ảnh AI làm mọi ảnh thành ảnh AI; nút «Đây là ảnh AI» lưu dấu và viết lại alt; gửi nháp kèm ảnh thật. Chạy từ `main` `504ab15` (nhánh `team/T-087`).

**Đã thử trên máy** (script tạm trong scratchpad, không commit):

1. **Kiểm GPS ảnh WebP trên Windows** (README dòng 332). Làm như sau:
   - Tạo ảnh JPEG có GPS, chạy qua đúng `make_web_image` của app (`has_gps: True`), rồi hỏi Windows qua Shell (`ExtendedProperty`). Kết quả: `System.GPS.Latitude = 10,47,30 N`, `Longitude = 106,37,12 E`. Ảnh không GPS thì cả hai rỗng.
   - Đọc khóa registry `SystemFileAssociations\.webp\FullDetails`: danh sách này có nhóm `System.PropGroup.GPS` gồm Latitude, Longitude, Altitude, giống hệt `.jpg`. Vậy thẻ **Details** trong **Properties** có hiện phần GPS.
   - Máy có `Microsoft.WebpImageExtension` 1.2.31.0, Windows giao diện tiếng Anh (`en-US`), nên README ghi nhãn tiếng Anh (**Properties**, **Details**, **Latitude**, **Longitude**).
   - Chưa thử trên Mac; README có ghi rõ điều này.
2. **Dấu «ảnh AI» gắn tay** (`ImageTagStore`, kho tạm). Kết quả:
   - Gắn xong: `ai`.
   - Đổi tên file: `that` (README dòng 300, cách gỡ khi bấm nhầm).
   - Cùng đường dẫn nhưng thư mục gốc số khác: `that` (đổi thứ tự `IMAGE_FOLDERS` thì mất dấu, dòng 214, 301).
   - Xóa file kho rồi mở lại: `that` (dòng 265, 301).
   - Chỉ đổi chữ hoa, thường: vẫn `ai`. README không nói tới trường hợp này.
3. **Tên file trên website:** `image_file_name(category="Cổng inox", area="Tân Phú", project_code="CT012")` → `cong-inox-tan-phu-ct012.webp`; ảnh AI → `minh-hoa-ai-cong-inox.webp` (dòng 318).

## Đối chiếu từng yêu cầu với code

Số dòng `app/views/write.py` theo `504ab15`.

**Yêu cầu 1: cách chọn ảnh (README mục 9, dòng 269–285)**

| Câu README | Code |
|---|---|
| Khung **📷 Chỗ cần ảnh** ở bước Viết & kiểm tra, cho mục có nhãn **📷 cần ảnh** ở Dàn ý | `image_slot` :941-967 (nhãn :946), gọi từ `section_card` :1721-1722; nhãn dàn ý :1611-1612 |
| **📁 Chọn ảnh từ thư mục**; ô **Thư mục ảnh** (chỉ tên), **Thư mục con**, **⬆ Lên một cấp**, **🔄 Quét lại**; 12 ảnh mỗi trang | :1015, `folder_browser` :1285-1384 (:1299-1308, :1352-1361, :1338, :1339), `BROWSE_PAGE_SIZE` :122 |
| Chỉ xem thư mục khi mở; ổ chậm thì quét nền, bấm **🔄 Xem kết quả** | `folder_listing` :1200-1233, :1328-1334 |
| JPG, PNG, WebP, HEIC, AVIF; tối đa 40 MB; lối tắt, mục ẩn, file khác bị bỏ qua, có ghi số | `seo_app/images/folders.py:53-54`; `skipped_text` :1265-1282 |
| Nút **Chọn**; ảnh xem trước, tên file, thư mục | `image_grid` :1408-1415; `chosen_panel` :1018-1023 |
| **📷 Ảnh thật** / **🤖 Ảnh AI**, dòng «Vì sao là ảnh AI: …» | :1025-1043, `ai_reason` :825-833 |
| «Thẻ: Mã CT012 · …» / «Chưa có thẻ (tên thư mục chưa theo quy ước).» | `tags_md` :632-641, :1044-1045 |
| Hai câu GPS (chép nguyên văn) | :1057-1063 |
| **✨ AI viết alt** / **🔄 AI viết lại alt**: chỉ ảnh đã chọn, byte của `make_ai_image` (bỏ hết metadata) | `alt_editor` :1082-1089, `ai_write_alt` :904-938 (:918); Lá Chắn T-056 bảng điều kiện số 10, 15 |
| Alt tối đa 125, chú thích tối đa 200, có nhắc | :1099-1111; `config/content.toml:96-97` |
| **✅ Đã duyệt**, sửa chữ phải tick lại; nhắc số điện thoại | :1119-1132, `unapprove` :836-837 |
| Ảnh chưa có alt, chưa duyệt thì chưa gửi bài được | `slot_problem` :767-779, `draft_panel` :2114-2118, :2137 |
| **📂 Mở thư mục chứa ảnh**, **🔁 Chọn ảnh khác**, **✖ Bỏ ảnh** | :1067-1072 |
| Ảnh, alt, chú thích lưu cùng bài đang soạn dở; mở lại thì kiểm lại ảnh | `slot_draft_image` :695-702, `restore_images` :412-437 |

**Yêu cầu 2: ảnh AI (README dòng 287–301, mục 8 dòng 242, 258, 265–267)**

| Câu README | Code |
|---|---|
| Tạo ảnh trong app đang hoãn, **🎨 Tạo ảnh**, **🔄 Prompt khác** khóa; prompt sao chép, **✏️ Sửa prompt**; tạo ở Gemini, lưu thư mục có chữ «AI» | `ai_prompt_panel` :987-1004 (câu dặn của app :1001-1004) |
| Thư mục có chữ «minh họa» cũng là ảnh AI | `_AI_PHRASES` `seo_app/images/tags.py:269-280`; đã chạy thử `Ảnh minh họa/x.png` → ảnh AI (T-069) |
| Alt «Minh họa…», chú thích (nếu có) «Ảnh minh họa (AI)…», tên file `minh-hoa-ai-…`, không mã, khu vực, trước/sau | `seo_app/storage/drafts.py:309-321` (chú thích rỗng thì không thêm), `seo_app/images/naming.py:39-48` |
| Chọn «Ảnh AI» ở đầu khung chỉ để hiện prompt | `kind-…` chỉ dùng cho `ai_prompt_panel` (:958-959); nguồn ảnh theo thẻ (`slot_tags` :678-683, `choose_image` :886-901) |
| Nút **🤖 Đây là ảnh AI**: alt, chú thích thêm tiền tố, duyệt lại, mọi chỗ dùng cùng ảnh đổi theo; không đổi lại được trong app | `mark_ai` :846-883, nút và lời giải thích :1034-1043, `ai_reason` :833 |
| Dấu chỉ nhớ trên máy, trong `data/image_tags.sqlite`; xóa file, đổi thứ tự `IMAGE_FOLDERS`, máy kia thì chọn lại là ảnh thật (LC-T069-2) | `tag_store` :537-539, `seo_app/storage/image_tags.py:59`, khóa `(root_index, ref_key)` :90-94; đã thử (mục Bằng chứng, số 2) |
| Khai báo riêng thư mục ảnh AI trong `IMAGE_FOLDERS` thì mọi ảnh là ảnh AI; khung ghi «🤖 Mọi ảnh trong thư mục gốc này là ảnh AI» | `root_notes` :579-596, :1320-1324; test `test_ai_root_folder_makes_every_image_ai` (qua) |
| Hai dòng lỗi mới: «File lưu thẻ ảnh sửa tay bị hỏng…», «Chưa lưu được dấu «ảnh AI»…» (chép nguyên văn phần đầu) | `note_tag_store` :648-656; `mark_ai` :861-865 |

**Yêu cầu 3: «Gửi nháp» (README mục 10, dòng 303–324)**

| Câu README | Code |
|---|---|
| Khung **Kiểm tra trước khi gửi**, dòng «Chỗ cần ảnh đã có ảnh, alt đã duyệt: …» | `step_publish` :2180, :2191 |
| Chỗ cần ảnh trống thì bài không có ảnh ở đó | :2119-2120 |
| **Ảnh đại diện**: bài từ 2 ảnh chọn ở ô (mặc định ảnh đầu); bài 1 ảnh thì ảnh đó | :2121-2125; `seo_app/wordpress/client.py:1288` |
| Khung **Có đoạn dạng shortcode**: liệt kê `[...]`, nên xóa | `shortcode_findings` :1890-1923, :2126-2136 |
| Lời nhắc ngay trên nút | `GPS_PUBLIC_WARNING` :152-155, :2153-2156 |
| Gửi xong: «Đã tạo bài nháp trên WordPress (mã …)», nút **Mở bài nháp trong WordPress**, danh sách ảnh; khóa, tick **Tạo thêm một bài nháp mới** | `send_result` :2057-2098; :2146-2152 |
| Chỉ tạo bài nháp, không sửa bài có sẵn | `client.py:1114-1135` (bước 3: «bài luôn draft; không bao giờ sửa bài có sẵn») |
| Ảnh công khai ngay khi tải, kể cả nháp; app không tự xóa | `GPS_PUBLIC_WARNING` :152-155; `client.py:1117-1119`, :1138-1139 |
| WebP, cạnh dài tối đa 1600 px, giữ GPS; tên file từ thẻ (thiếu thì từ alt) | `config/content.toml:84-85`; `naming.py:1-11`, `:39-48` |
| Thân bài: `<h2>` + `<p>`, Markdown không chuyển; meta SEO, chuyên mục chưa gửi | `article_parts` :1871-1887, `seo_app/text.py:29-35`; `send_draft` gọi `create_draft_with_images(sent_title(), …)` không kèm chuyên mục (:2017) |
| Lỗi lúc kiểm lại, nén ảnh: «Chưa gửi gì lên website.» | `send_draft` :1951-2007 |
| Lỗi giữa chừng: liệt kê ảnh đã lên, không tự gửi lại; kiểm Bài viết → Nháp, Media → Thư viện; khóa tới khi tick «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi» khi không chắc | :2018-2034, `MSG_SEND_INTERRUPTED` :144-148, :2138-2145, :2081-2090 |

**Yêu cầu 4: lời dặn tạm thời (README dòng 326–333)**

- Đợi kết quả, không F5, không đóng tab, không bấm nút khác, không bấm đúp: theo Lá Chắn T-056 điều kiện 3 và SL-T056-1, -9, -11, LC-T056-1 (`docs/team/reports/T-056-la-chan.md`).
- Thêm câu «bài đã gửi thì đừng bấm gửi lại sau khi mở lại bài». Lý do: SL-T056-8 (mở bài khác rồi mở lại thì mất khóa) và Ghi nhận 2 của Soi Lỗi («đã gửi» chỉ nhớ trong phiên). Code: `COMPOSE_KEYS` :102-110 có `_wp_sent`, bị xóa cùng bài (`reset_compose` :207-222).
- Lần gửi đầu: một bài, một ảnh có GPS, tải ảnh về kiểm. Địa chỉ ảnh lấy ở danh sách app in ra (`send_result` :2093-2098). Cách kiểm GPS trên Windows đã thử (mục Bằng chứng, số 1).

**Yêu cầu 5:** viết tiếng Việt, giữ bố cục mục đánh số và bảng «App báo / Cách xử lý» như README cũ. Không có khóa. Đường dẫn ví dụ đều là dạng chung, lấy từ `.env.example` (`G:/My Drive/Ảnh AI` có từ T-069).

## Sửa thêm ngoài yêu cầu 1–5 (cùng chủ đề, đã kiểm code)

1. **LC-T069-1** (điều kiện Lá Chắn T-069 còn mở, Chỉ Huy ghi «sửa chữ README sau»). Dòng 215 dùng câu Lá Chắn đề xuất: thư mục phần mềm có `.env` (khóa AI, mật khẩu WordPress) và `data/`, nên đừng để trong Google Drive, OneDrive hay thư mục ảnh. Dòng 16 (mục 1, lúc clone) nhắc ngắn cùng ý.
2. **Câu cũ của T-069 sai sau khi T-056 gộp** (đã ghi rủi ro này trong báo cáo T-069):
   - dòng 139: «Giao diện chưa có nút viết alt» → nói rõ app chỉ gửi ảnh cho hãng AI khi bấm nút;
   - dòng 202: «Màn hình chọn ảnh trong bài chưa có»;
   - dòng 242: trước đây dặn «đừng khai báo riêng thư mục ảnh AI». Nay T-056 đã làm điều kiện 2(c) của Lá Chắn T-052: tên thư mục gốc có dấu hiệu AI thì mọi ảnh trong đó là ảnh AI (`root_notes` :579-596). README đổi thành «cũng có thể khai báo riêng», và dòng 213, 243, 251 sửa theo (app có xét tên thư mục gốc, nhưng chỉ để nhận ảnh AI);
   - dòng 258: «thẻ sửa tay (khi có màn hình chọn ảnh)» → «dấu «ảnh AI» gắn bằng nút». Giao diện hiện chỉ gắn tay đúng một thứ là dấu ảnh AI (`tag_store().set` chỉ có ở `mark_ai` :860);
   - dòng 214: nói rõ thêm thứ tự `IMAGE_FOLDERS` cũng giữ ảnh đã chọn trong bài đang soạn dở.
3. **Phần đầu và mục 7** (dòng 7, 46, 97, 161–162): «Xuất bản» không còn là bản demo hoàn toàn (hình thức Nháp chạy thật); trỏ tới mục 9, 10.
4. **Mục 10, phần «Cần biết khi gửi»:**
   - Tên file ảnh trên web có mã công trình, không có tên khách.
   - Thân bài chưa chuyển định dạng Markdown, meta SEO và chuyên mục chưa gửi (Họa Sĩ T-056, Rủi ro 4).
   - Ảnh vẫn còn trên website khi xóa bài nháp. Đây là cách WordPress làm (xóa bài không xóa Media), không phải code của app.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–5 (bảng trên)
- [x] Báo cáo tại `docs/team/reports/T-087-thu-ky.md`
- [x] `PYTHONUTF8=1 uvx detect-secrets scan README.md`: 0 mục (thử mồi bắt đủ); `uv run ruff check .` sạch; `tests/test_app_pages.py` qua

## Rủi ro và điểm cần chú ý

- **Phải sửa lại README khi T-086 gộp.** «Lời dặn tạm thời» (dòng 326–329) viết theo app hiện nay, chưa nhớ việc gửi qua lần tải lại trang. Khi T-086 gộp, bỏ hay viết lại khối này cho đúng app mới.
- **Kiểm GPS trên Windows** dựa vào ứng dụng «WebP Image Extensions» của Microsoft (có sẵn trên máy này, bản 1.2.31.0). Máy khác thiếu ứng dụng này thì Details có thể không hiện GPS cho file WebP. Chỗ này chưa thử.
- Nhãn trên Windows ghi tiếng Anh vì máy chủ dự án dùng Windows tiếng Anh; máy tiếng Việt thì tên nút khác.
- Câu «xóa bài nháp thì ảnh vẫn còn» là hành vi của WordPress, không kiểm được bằng test của app (test không gọi website thật). Lần thử thật (T-059) có thể xác nhận.
- Danh sách nhãn nút chép từ `app/views/write.py`. Họa Sĩ đổi nhãn thì phải sửa README theo, nhất là T-086 (cùng file `write.py`).

## Đề xuất

- **Khi T-086 gộp (Chỉ Huy giao Thư Ký):** sửa khối «Lời dặn tạm thời» và câu «bài đã gửi thì đừng bấm gửi lại» (README dòng 326–329) theo cách app mới nhớ trạng thái gửi.
- **Khi T-084 gộp:** soát lại README dòng 211 (Cài đặt → 🖼️ Ảnh hiện «✅ tìm thấy» / «⚠️ không thấy trên máy này»), vì trang đó sẽ đổi.
- **Mục «Dành cho người phát triển»** (cuối README): sơ đồ thư mục `seo_app/` còn thiếu `ai/`, `content/`, `images/`, `storage/`, `onpage/`. Không thuộc phiếu này nên chưa sửa; có thể gom vào một phiếu tài liệu nhỏ sau.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-26): sửa LC-T087-1, LC-T087-2

Theo biên bản [Lá Chắn T-087](T-087-la-chan.md) (ĐẠT CÓ ĐIỀU KIỆN, điều kiện 1, 2). Chỉ sửa `README.md`. Không làm điều kiện 3 (viết lại «Lời dặn tạm thời» khi T-086 gộp), như Chỉ Huy dặn.

| Mã | Chỗ | Câu cũ | Câu mới |
|---|---|---|---|
| LC-T087-2 | `README.md:317` | «ai có đường dẫn ảnh đều mở được, kèm vị trí GPS còn trong ảnh. App **không tự xóa** … xóa trong **Media → Thư viện** của trang quản trị.» | «ảnh vào thư viện Media của website, mà WordPress cho **bất kỳ ai, không cần đăng nhập**, xem danh sách Media (kèm địa chỉ ảnh, alt, chú thích). Người lạ tìm được ảnh mà không cần ai gửi đường dẫn, mở ảnh là đọc được vị trí GPS còn trong ảnh. App **không tự xóa** … xóa trong **Media → Thư viện** của trang quản trị. Xóa chỉ gỡ ảnh khỏi website: ai đã tải ảnh về vẫn còn bản sao.» |
| LC-T087-2 | `README.md:330` | «chọn ảnh app báo «📍 Ảnh có vị trí GPS». Gửi xong, …» | «chọn ảnh app báo «📍 Ảnh có vị trí GPS» **chụp ở nơi đã công khai** (xưởng, cửa hàng); đừng dùng ảnh nhà khách cho lần thử. Gửi xong, …» |
| LC-T087-2 | `README.md:333` | «Xong thì xóa bài nháp và ảnh thử trong trang quản trị nếu không dùng.» | «Kiểm xong thì xóa ngay bài nháp và ảnh thử trong trang quản trị (**Bài viết → Nháp**, **Media → Thư viện**).» |
| LC-T087-1 | `README.md:309` (thêm cuối mục 3) | (chưa có) | «Đoạn nằm ở **tiêu đề bài** hay **tiêu đề mục** thì chưa sửa được ở bước này: gửi nháp xong, mở bài trong WordPress và xóa đoạn đó **trước khi** bấm Lưu hay Đăng. (Cách khác: sửa tiêu đề ở bước **Dàn ý** rồi duyệt lại để AI viết lại toàn bài; cách này mất phần đã sửa tay và phải chọn lại ảnh.)» |

**Chỗ khác câu đề xuất của Lá Chắn (đã kiểm code):**

- `:317`: câu đề xuất có «Xóa rồi thì đường dẫn không mở được nữa». README viết «Xóa chỉ gỡ ảnh khỏi website: ai đã tải ảnh về vẫn còn bản sao». Lý do: chưa biết website có lớp lưu tạm (CDN, plugin nén ảnh) giữ ảnh thêm một thời gian hay không; phiếu thử thật T-059 mới kiểm được. Nên không hứa «không mở được nữa».
- `:309`: câu đề xuất có «(hoặc quay lại bước **Dàn ý** sửa tiêu đề rồi để AI viết lại bài)». README thêm hậu quả của cách này, vì code cho thấy:
  - viết lại bài tạo các mục mới (`set_article`, `app/views/write.py:286-296`, mỗi mục một mã mới);
  - ảnh đã chọn, alt đã duyệt, phần sửa tay gắn với mã mục cũ nên không còn hiện; app cũng tự nhắc «Duyệt lại dàn ý sẽ viết lại toàn bài, thay bài hiện tại» (`:1623-1624`);
  - tiêu đề bài là do AI viết (`seo_app/content/workflow.py:220`), không chắc giữ đúng tiêu đề dàn ý. Nếu còn đoạn `[...]`, khung cảnh báo sẽ liệt kê lại trước khi gửi.

**Đối chiếu với code** cho LC-T087-2: client tải ảnh không gắn vào bài. Lệnh `POST /wp/v2/media` chỉ được nhận tham số `_fields` (`seo_app/wordpress/client.py:105`). Lệnh ghi alt chỉ gửi `alt_text`, `title`, `caption`, docstring ghi «Không gửi `status`, `post`» (`:1290-1306`). Phần WordPress liệt kê công khai lấy theo biên bản Lá Chắn (đọc mã nguồn WordPress); tôi không gọi website.

**Kiểm tra lượt 2:**

```
$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-087-thu-ky.md
results: {}   (0 mục)
$ uv run ruff check .
All checks passed!
```

Không chạy lại pytest: lượt này chỉ đổi chữ trong `README.md` và báo cáo.

**Chưa làm (không thuộc lời giao lượt 2):** 3 khuyến nghị không bắt buộc của Lá Chắn: GitHub Desktop mặc định lưu vào Documents (có thể đồng bộ OneDrive); đọc prompt trước khi dán sang công cụ khác; chỉ đổi tên file để gỡ dấu «ảnh AI» khi chắc là ảnh chụp thật. Chỉ Huy quyết có làm không.

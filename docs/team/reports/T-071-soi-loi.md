# Báo cáo T-071 · Dọn lỗi Thấp phần chèn ảnh vào nháp (sau T-054) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-071](../tickets/T-071-don-loi-thap-chen-anh-nhap.md) |
| Ngày nộp | 2026-10-23 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T071-1). Soát R5 cho 7 chỗ test ngoài phạm vi: **đạt** |

## Tóm tắt (cho chủ dự án)

- Bản sửa của Thợ Máy làm đúng cả 6 yêu cầu. Khi website trục trặc **đúng lúc tạo bài nháp** (chậm, mất mạng, lỗi máy chủ, trả lời sai dạng), phần mềm báo «bài nháp có thể vẫn đã được tạo, kiểm Bài viết → Nháp trước khi gửi lại»; khi website từ chối rõ ràng thì báo «chưa tạo bài nháp». Tôi thử 14 kiểu trục trặc ở cả 5 bước của một lần gửi (70 ca): câu báo luôn đúng, không bao giờ vừa nói «có thể đã có» vừa nói «chưa tạo».
- Website trả lời lạ lúc tải ảnh (không xác nhận «vừa tạo ảnh mới», hay trả cùng một mã cho hai ảnh) thì phần mềm dừng, không ghi đè mô tả của ảnh đã có. Tên file ảnh chỉ lấy từ thẻ trong danh sách cố định; thẻ bị sửa lén hay sai kiểu (14 kiểu) đều bị chặn trước khi gửi bất cứ gì.
- Tìm thấy **1 lỗi nhỏ (Thấp)**: nếu AI tự viết tiền tố trong ngoặc vuông kiểu «[Minh họa]: cổng inox…» thì alt và chú thích của ảnh AI lên website vẫn còn dấu «\» (ví dụ `Minh họa \: Cổng inox…`). Chỉ là chữ xấu, không mở được lệnh lạ nào trên website. Nên sửa trước khi có nút «Gửi nháp» (T-056); chỗ sửa nằm ở file ngoài phạm vi phiếu này nên cần Chỉ Huy quyết.
- Soát 7 chỗ trong test của agent khác mà phiếu được phép sửa: chỉ đổi cách tạo ảnh cho hợp kiểu mới, không bỏ hay nới điều kiện kiểm nào.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t071.py` | Mới: 145 ca (143 qua, 2 `xfail(strict=True)` của SL-T071-1). Site giả riêng, cài lỗi theo từng bước; không dùng lại dữ liệu, site giả của Thợ Máy |
| `docs/team/reports/T-071-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| YC1 · LC-T054-2 (lỗi ở lệnh tạo nháp) | **ĐẠT** | `client.py:1089` (`creating`), `:1102` (`unsure`), `:1110`, `:1118-1121`; tài liệu `DraftImagesError` `:447-459`. Test `test_loi_o_tung_buoc_bao_dung_bai_nhap_va_anh`: 5 bước (tải ảnh 1, ghi alt ảnh 1, tải ảnh 2, ghi alt ảnh 2, tạo nháp) × 14 kiểu lỗi (hết giờ, hết giờ lúc nối, mất mạng, SSL, đứt giữa chừng, 500, 503 trang HTML, 302, 200 trang HTML, 400, 403, 404, 429, lỗi lạ không phải lỗi mạng) = 70 ca. Mỗi ca kiểm: danh sách ảnh đã lên đúng bước; `maybe_draft` bật **đúng và chỉ** khi lỗi ở lệnh tạo nháp mà không phải 4xx; `maybe_uploaded` đúng; `status_code` giữ nguyên; câu báo không bao giờ có cả «có thể vẫn đã được tạo» lẫn «chưa tạo bài nháp»; 4xx ở lệnh tạo nháp nói «Chưa tạo bài nháp»; lỗi lạ trước lệnh tạo nháp vẫn nói «Chưa tạo bài nháp»; không lộ khóa; lệnh lỗi là lệnh cuối (ảnh lỗi thì không tạo nháp, nháp lỗi thì không đặt ảnh đại diện); sau lỗi, `set_featured_image(42, …)` bị từ chối, không gửi gì (bài chưa chắc do app tạo). Thêm ca bài không có ảnh: hết giờ lúc tạo nháp vẫn báo «có thể đã có» |
| YC2 · LC-T054-3 (dấu «\» ở alt, chú thích ảnh AI) | **ĐẠT** cho lỗi gốc; còn **SL-T071-1** (Thấp, biến thể khác nguồn) | `html.py:52`, `:79`. Test: 3 cặp nhãn đầu dòng qua `clean_suggestion(ai_generated=True)` (cả nhãn thứ hai giữa dòng, nhãn liền nhau) → alt, `<figcaption>` trình duyệt đọc đúng «Minh họa [Sau khi sửa]: …», «Ảnh minh họa (AI): [Mẹo]: …»; `alt_text`, `title` (`[AI] …`), `caption` gửi REST đúng chữ, không «\», không «[» «]» trần ở bất kỳ chuỗi JSON nào. Người dùng gõ thêm chữ trước nhãn (alt và chú thích ảnh thật): không «\». **Shortcode trong chú thích sau khi gỡ «\»**: `[code_snippet id=1]:`, `[/code_snippet]:`, `[[code_snippet id=1]]:`, `[embed]https://…[/embed]:` trong chú thích ảnh AI: người đọc thấy đúng chữ, mọi chuỗi gửi đi không còn «[» «]» trần (T-061 không nới) |
| YC3 · LC-T054-5 (mã 201, mã ảnh trùng) | **ĐẠT** | `client.py:993` (`new_only`), `:1066`. Test: tải ảnh trả 200, 202, 203, 206, 207 (kèm mã 55 của «ảnh có sẵn») → dừng sau đúng một lệnh, không ghi alt cho ảnh 55, không tạo nháp, nhắc «có thể vẫn đã lên». Ảnh **thứ ba** trả lại mã của ảnh **đầu** (không liền nhau) → dừng; ảnh 101 chỉ được ghi một lần «Ảnh một», ảnh 102 «Ảnh hai», không có lệnh ghi «Ảnh ba». Đối chứng: cùng một `DraftImage` đặt hai chỗ vẫn chỉ tải một lần, không bị coi là trùng mã |
| YC4 · LC-T054-6 (chốt cuối `figure_html`) | **ĐẠT** | `html.py:55`, `:128-129`. Chú thích `ảnh src="<đúng địa chỉ ảnh>" alt="giả"` (đúng kiểu đánh lừa chốt cũ) với 4 bộ lọc giả làm hỏng ảnh: đổi `src` thành `data-src`, đổi địa chỉ ảnh, đổi `alt` thành `title`, biến thẻ ảnh thành chữ → cả 4 báo `ImageHtmlError`. Qua `create_draft_with_images`: dừng trước lệnh tạo nháp, liệt kê ảnh đã lên. Đối chứng: chú thích có chữ `<img src="…" alt="x">` (người dùng gõ) với bộ lọc thật vẫn ra đúng một ảnh, chữ hiện nguyên |
| YC5 · LC-T054-4 (`DraftImage` nhận `ImageTags`) | **ĐẠT** | `client.py:416`, `:1160-1165`, `:1181`. `DraftImage(…, ai_generated=…/category=…/area=…/project_code=…)` → `TypeError` (4 ca). Ảnh AI **chỉ** theo `tags.source`: ảnh thật có alt «Minh họa cổng inox» không thành ảnh AI (tên `minh-hoa-cong-inox.webp`, tiêu đề không `[AI]`); ảnh có `source="ai"` thì `minh-hoa-ai-…`, `[AI] …`. Nối với T-052: thẻ đọc từ thư mục `CT012 - Cổng inox - Tân Phú/minh họa/…` là ảnh AI không mang mã công trình, khu vực → tên `minh-hoa-ai-cong-inox.webp`, lệnh ghi alt của ảnh AI không có «CT012», «Tân Phú». Thẻ ảnh thứ **hai** bị sửa lén sau khi tạo (14 kiểu: ảnh AI thêm mã công trình / khu vực / trước-sau, ảnh thật có khu vực đổi thành AI, nguồn `"AI"`, `" ai"`, `"ai\u200b"`, mã là số, mã chữ số toàn khổ `CT１２`, khu vực `None`, hạng mục `bytes`, hạng mục có `\r\n`, hạng mục là tên khách, truyền `FolderTags` thay `ImageTags`) → `WordPressError` câu cố định «Thẻ của ảnh thứ 2 không hợp lệ…», **0 lệnh** gửi đi, không chép chữ của thẻ. `ImageTags`/`ImageTags.from_input` ảnh AI kèm mã công trình, khu vực, trước/sau → `TagError` |
| YC6 · gỡ `xfail` SL-T054-1, -3 | **ĐẠT** | `git diff a9338f7..team/T-071 -- tests/test_soi_loi_t054.py`: đúng 2 khối `@pytest.mark.xfail(...)` bị xóa (4 + 5 dòng); thân `test_sl_t054_3_…` (`:770-778`) không đổi chữ nào; `test_sl_t054_1_…` (`:483`) chỉ đổi lời gọi `DraftImage` (chỗ 5, mục soát R5), 5 `assert` giữ nguyên. Cả 4 ca qua |

## Soát R5: 7 chỗ test ngoài phạm vi

Đối chiếu `git diff a9338f7..team/T-071` với bảng mục 4 của báo cáo Thợ Máy. `git diff --numstat`: `test_shortcode_t061.py` +2/−1, `test_soi_loi_t061.py` +2/−1, `test_soi_loi_t054.py` +28/−15 (khớp số Thợ Máy ghi). Lọc mọi dòng thêm/xóa có `assert`, `parametrize`, `xfail`, `raises` trong 3 file: **không dòng `assert` hay `parametrize` nào bị xóa hay sửa**; chỉ có 2 khối `xfail` bị xóa (YC6) và 3 dòng thêm ở chỗ 4.

| # | Chỗ (số dòng bản cũ → bản mới) | Kết quả |
|---|---|---|
| 1 | `test_soi_loi_t054.py:289` → `:291-294` | **Đúng, cơ học.** `category="Cổng inox", area="Tân Phú"` → `tags=ImageTags(category="Cổng inox", area="Tân Phú")`, cùng giá trị; `assert` tên file `cong-inox-tan-phu.webp` và vòng kiểm chữ khách giữ nguyên |
| 2 | `:337` → `:342-346` | **Đúng, cơ học.** Cùng 3 giá trị thẻ; `assert` tập tham số ⊆ {…} giữ nguyên |
| 3 | `:338` → `:347-349` | **Đúng, cơ học.** `ai_generated=True` → `ImageTags(source=SOURCE_AI, category="Cổng inox")` |
| 4 | `:363` → `:374-383` (`test_ten_file_khong_the_chen_header_hay_doi_duoi`) | **Đạt, có ghi chú (không thuần cơ học nhưng không nới).** Giữ đủ **7 chuỗi độc** (`parametrize` không đổi) và **2 `assert`** header cũ. Đường cũ (`category` chữ tự do) không còn, nên chuỗi độc nay đi qua alt (chữ tự do duy nhất còn vào tên file), cộng 3 dòng chặt hơn: `ImageTags(category=chuỗi độc)` → `TagError`; `tags=chuỗi độc` → `WordPressError`, 0 lệnh. Khác biệt duy nhất: alt đi qua `plain_image_text` trước (bỏ `\r`, `\n`), nên `image_file_name` không còn nhận chữ thô như trước. Tôi bù bằng `test_ten_file_tu_chu_doc_tho_van_dung_khuon` (7 chuỗi × `category`, `area`, `alt` × ảnh thật/AI, gọi thẳng `image_file_name` với chữ thô) và `test_anh_ai_alt_doc_khong_chen_duoc_header` (7 chuỗi làm alt ảnh AI qua client): đều ra đúng khuôn `[a-z0-9-]+\.webp` |
| 5 | `:472` → `:487-489` | **Đúng, cơ học**, kèm gỡ `xfail` SL-T054-1 (YC6); 5 `assert` giữ nguyên |
| 6 | `test_shortcode_t061.py:419` → `:420` | **Đúng, cơ học.** `ai_generated=True` → `tags=ImageTags(source=SOURCE_AI)`; 6 `assert` giữ nguyên |
| 7 | `test_soi_loi_t061.py:243` → `:244` | **Đúng, cơ học.** Như chỗ 6; 14 ca `NASTY` và 7 `assert` giữ nguyên |

Ngoài 7 chỗ: chỉ có dòng import (`ImageTags`, `SOURCE_AI`, `TagError`) và câu docstring đầu `test_soi_loi_t054.py`. Test cũ của chính T-054 trong `tests/test_wordpress_images.py` (trong phạm vi phiếu, mục 3 báo cáo Thợ Máy): đọc diff, các ca bị thay đều là ca không còn dựng được (`category=5`, `area="x"*201`, `ai_generated="yes"`, mã công trình chữ tự do) và được thay bằng ca chặt hơn cùng ý; không `assert` nào bị nới.

## Thử đột biến (test có bắt được lỗi cũ không)

Trên **bản sao** của nhánh (`git archive HEAD` vào thư mục nháp, không đụng worktree), gỡ từng chỗ sửa của T-071 rồi chạy riêng `tests/test_soi_loi_t071.py` (08:48–08:52). Mỗi chỗ sửa bị gỡ đều làm hỏng ít nhất một test của tôi; bản không gỡ: 143 qua, 2 `xfail`.

| Chỗ sửa bị gỡ | Test hỏng |
|---|---|
| YC2: bỏ bước gỡ `]\:` (`html.py:79`) | 6 (3 nhãn ảnh AI, người dùng gõ thêm chữ, 2 chú thích dạng shortcode) |
| YC4: chốt cuối tìm trong cả `<figure>` như cũ | 5 (4 bộ lọc giả, 1 qua `create_draft_with_images`) |
| YC3: không kiểm `201` | 5 (200, 202, 203, 206, 207) |
| YC3: không kiểm mã ảnh trùng | 1 (ảnh thứ ba trả mã ảnh đầu) |
| YC1: không bao giờ bật `maybe_draft` | 10 (9 ca lệnh tạo nháp của ma trận, bài không có ảnh) |
| YC1: quy tắc cũ «không có mã hoặc ≥ 500» | 3 (chuyển hướng 302 ở 3 bước) |
| YC1: lỗi lạ ở lệnh tạo nháp vẫn khẳng định «Chưa tạo bài nháp» | 1 |
| YC5: dùng thẳng thẻ, không dựng lại (`replace`) | 13/14 ca thẻ bị sửa (ca `FolderTags` vẫn bị bước kiểm đúng lớp chặn) |
| YC5: bỏ qua `tags.source` (luôn coi là ảnh thật) | 12 |

## Tìm lỗi mới

- **Tên file, alt, chú thích với thẻ lạ**: thẻ bị sửa lén hay sai kiểu (14 kiểu, mục YC5), 7 chuỗi độc ở hạng mục, khu vực, alt (cả ảnh AI): không lọt. 5.184 bộ thẻ hợp lệ dài khác nhau (hạng mục ghép hành động + đồ vật + 1–2 vật liệu, 3 khu vực, `CT123456`): mọi tên ≤ 60 ký tự, đúng khuôn; tên quá dài thì cắt theo ranh giới chữ, mã công trình còn nguyên hoặc mất hẳn (2.997 bộ), không bao giờ cụt giữa mã (xem Ghi nhận).
- **Lỗi mạng giữa chừng** (ảnh đã lên mà nháp chưa tạo): ma trận 70 ca ở YC1. Không ca nào tạo nháp sau khi ảnh lỗi, không ca nào thiếu ảnh trong danh sách đã lên, không ca nào sai cờ «ảnh đang tải có thể vẫn đã lên» (`maybe_uploaded`).
- **Ảnh AI có thẻ mã công trình, khu vực**: không tạo được (`TagError`), sửa lén thì bị chặn trước mọi lệnh, đọc từ thư mục công trình thì T-052 bỏ mã và khu vực (mục YC5).
- **Shortcode trong chú thích sau khi gỡ escape**: mục YC2. Gỡ «\» chỉ đụng chuỗi `]\:`, không tạo được «[» mới; mọi «[» «]» vẫn thành `&#91;` `&#93;`.
- **Dò dấu «\» còn sót**: 46 chuỗi có nhãn «[…]» (đầu dòng, giữa dòng, nhãn lồng, nhãn liền, sau `>`/`-`/`1.`, có ký tự rộng 0, bị cắt độ dài, có tiền tố AI tự viết trong ngoặc) × ảnh AI/ảnh thật × alt/chú thích, qua `clean_suggestion` rồi `plain_image_text`, cộng 28 nhãn × 4 kiểu người dùng gõ thêm chữ trước nhãn: chỉ còn một nhóm giữ dấu «\» → **SL-T071-1**.

## Lỗi tìm thấy

### SL-T071-1 · Thấp · Ảnh AI: AI viết «[Minh họa]: …» thì alt, chú thích lên website còn dấu «\»

- **Cách tái hiện:** `clean_suggestion(AltSuggestion(alt="[Minh họa]: Cổng inox 2 cánh sơn tĩnh điện", caption="[Ảnh minh họa (AI)]: cổng sau khi sơn"), ai_generated=True)`, rồi gửi bằng `DraftImage(…, tags=ImageTags(source=SOURCE_AI))`. Cùng lỗi với `[Ảnh minh họa]:`, `[Hình minh họa]:`, `[Minh hoạ]:`, `[MINH HỌA]:`, `[Minh họa]:chữ` (không cách), `[Minh họa][cổng sắt] sơn đen` (dấu «[» thay dấu «:»).
- **Mong đợi:** như khi AI viết «[Minh họa] cổng inox» hay «Minh họa: cổng inox»: alt «Minh họa cổng inox…», chú thích «Ảnh minh họa (AI): cổng…», không có «\».
- **Thực tế:** alt trong `<img>`, `alt_text`, tiêu đề media là `Minh họa \: Cổng inox 2 cánh sơn tĩnh điện`; chú thích `Ảnh minh họa (AI): \: cổng sau khi sơn` (dạng «[»: `Minh họa \[cổng sắt] sơn đen mờ`). Ảnh thật không bị (không bỏ tiền tố).
- **Nguyên nhân:** `escape_link_syntax` thêm «\» sau «]» của nhãn đầu dòng (`[Minh họa]\:`); `_strip_ai_prefix` (`seo_app/images/alt.py:363-386`) bỏ tiền tố AI tự viết **kèm dấu «]» đóng** nhưng để lại dấu «\» (không có trong `_AFTER_PREFIX`, `:358`), nên dấu «\» mồ côi, không còn «]» đứng trước. Bước gỡ mới của T-071 (`html.py:52`, `:79`) chỉ nhận `]\:` nên không gỡ được. Có từ T-062 (lỗi cũ, không do T-071 gây ra), nhưng đúng phạm vi ý của YC2 («alt, chú thích ảnh AI mở đầu `[…]:` không còn dấu `\`»).
- **Hậu quả:** chỉ là chữ xấu trên website (alt, chú thích công khai); không thành link, thẻ hay shortcode (mọi «[» vẫn thành `&#91;`). AI hay viết nhãn kiểu «[…]:», và T-062 đã thấy AI bọc tiền tố trong ngoặc vuông (`_WRAPPERS` có «[»), nên dễ gặp hơn lỗi gốc.
- **Test:** `tests/test_soi_loi_t071.py::test_sl_t071_1_anh_ai_tien_to_trong_ngoac_vuong_con_gach_cheo` (2 ca, `xfail(strict=True)`).
- **Gợi ý sửa (Thợ Máy):** trong `_strip_ai_prefix`, khi bỏ ngoặc đóng mà ngay sau còn dấu «\» do `escape_link_syntax` thêm (trước «:», «[», «(») thì bỏ luôn dấu «\» đó, rồi mới `lstrip(_AFTER_PREFIX)`; hoặc bỏ tiền tố trên chữ **chưa** escape. File `alt.py` nằm ngoài «Được sửa» của T-071: Chỉ Huy quyết cho làm ở T-071 lượt 2 (mở phạm vi) hay phiếu dọn riêng. **Hạn: trước T-056** (cùng hạn của lỗi gốc LC-T054-3).

## Ghi nhận (không phải lỗi của T-071)

- **Báo thừa «có thể đã có»**: hết giờ **lúc nối** (`ConnectTimeout`, lệnh chưa tới website) ở lệnh tạo nháp cũng báo «bài nháp có thể vẫn đã được tạo». Hướng an toàn, người dùng chỉ kiểm mục Nháp thêm một lần (Thợ Máy đã nêu ở mục 8).
- **Bài không có ảnh**: lỗi không rõ ở lệnh tạo nháp, câu báo vẫn dặn kiểm «Media → Thư viện» và «tải lại ảnh lần nữa», kèm câu «Chưa có ảnh nào lên thư viện Media.». Thừa chữ, không sai hướng.
- **Tên file ảnh AI không có hạng mục** lặp tiền tố: alt ảnh AI luôn mở đầu «Minh họa» (T-062) nên tên ra `minh-hoa-ai-minh-hoa-cong-inox-2-canh-mau-den.webp`. Có từ T-049/T-062, ngoài phiếu; hình thức (SEO tên file).
- **Tên file dài cắt ở 60 ký tự** (thiết kế T-046/T-049): hạng mục ghép dài (hai vật liệu, ví dụ `Sửa chữa cổng trượt sắt mạ kẽm sơn tĩnh điện`) thì mất hẳn mã công trình, có khi cụt tên khu vực (`…-ba-ria-vung.webp`). Không lộ chữ lạ, không cụt giữa mã; ngoài phiếu. `match_category` nhận cả vật liệu lặp («sắt mạ kẽm sắt mạ kẽm»), cũng ngoài phiếu.
- **Hai việc Lá Chắn T-061 gợi ý «T-060 hoặc T-071»** không có trong phiếu T-071 nên chưa làm: hàm công khai tìm đoạn dạng shortcode cho cảnh báo của T-056 (LC-T061-4, «T-071 hoặc phần logic của T-056»), và `upload_media` luôn ghi đè cả ba ô (LC-T061-3). Chỉ Huy nhớ đưa vào T-056 / T-060.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** YC1–YC6 làm thật, có test độc lập, mỗi chỗ sửa đều có test bắt khi bị gỡ; soát R5 đạt. **Chuyển Lá Chắn rút gọn được ngay.** Điều kiện: SL-T071-1 (Thấp) sửa và gỡ `xfail` **trước khi gộp T-056**; chỗ sửa ở `seo_app/images/alt.py`, ngoài phạm vi T-071, nên Chỉ Huy chọn: T-071 lượt 2 (mở phạm vi) hay phiếu dọn riêng. Không cần giữ T-071 lại vì lỗi này (lỗi có từ T-062, T-071 không làm nặng thêm).

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, worktree `wt-T-071`, nhánh `team/T-071` (đầu nhánh lúc kiểm `6046a8f`, gốc `a9338f7`). Máy đang chạy song song các agent khác.

```
$ uv run pytest -q -p no:cacheprovider tests/test_wordpress_images.py tests/test_soi_loi_t054.py \
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_client.py \
    tests/test_images_tags.py tests/test_app_pages.py tests/test_soi_loi_t071.py -rxXf
(2026-10-23 08:53:09 → 08:54:38)
1168 passed, 1 skipped, 8 xfailed in 84.26s (0:01:24)

$ uv run ruff check .
All checks passed!
```

- 8 file: 7 file lời giao và file mới của tôi. 0 hỏng, 0 XPASS. Trước khi thêm file của tôi (08:22–08:26): `1025 passed, 1 skipped, 6 xfailed`; riêng `tests/test_soi_loi_t071.py`: `143 passed, 2 xfailed`.
- 8 `xfailed`: SL-T061-1 (4 ca), SL-T061-2 (2 ca) trong `tests/test_soi_loi_t061.py` (thuộc T-060, không liên quan), và SL-T071-1 (2 ca, lỗi mới).
- 1 `skipped`: `tests/test_images_tags.py:1777` («máy không cho tạo symlink (Windows chưa bật Developer Mode)»), do máy.
- Thử đột biến: mục «Thử đột biến» (bản sao `git archive HEAD`, chạy bằng `.venv` của worktree; kiểm `seo_app` được nạp từ bản sao ở cả 10 lượt).
- Quét bí mật: chép `tests/test_soi_loi_t071.py` và báo cáo này vào thư mục riêng, thêm một file mồi có chữ tiếng Việt (một khóa AWS giả, một dòng mật khẩu giả), chạy `PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files .` (detect-secrets 1.5.0): mồi **bắt đủ 2/2**, hai file của tôi: **0**. Đã xóa mồi.
- Script dò lỗi và script đột biến (không commit): thư mục ghi chú chung của các phiên, `T-071-soi-loi-scripts/`.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] Xác nhận YC1–YC6 bằng test độc lập với `FakeWordPress` (mục «Kiểm từng yêu cầu»)
- [x] Soát R5 cho 7 chỗ test ngoài phạm vi (mục «Soát R5»)
- [x] Tìm lỗi mới; lỗi ghi thành test `xfail(strict=True)` SL-T071-1
- [x] Test liên quan và `uv run ruff check .` (mục «Bằng chứng»)
- [x] Không sửa code ứng dụng

## Rủi ro và điểm cần chú ý

- Chỉ thử với site giả. Mã `201` của WordPress lõi, và việc plugin/CDN trên site có đổi `201` thành `200` hay không, cần xác nhận ở phiếu thử thật T-059 (Thợ Máy đã nêu): nếu bị đổi, mọi lần gửi nháp kèm ảnh dừng ở ảnh đầu (câu báo rõ, an toàn).
- Test giả định 4xx ở lệnh tạo nháp nghĩa là website chưa tạo bài. Đúng với WordPress lõi khi lệnh không gửi `meta`, `sticky`, `template` (lệnh của app không gửi); plugin lạ có thể khác.

## Đề xuất

- **SL-T071-1**: Thợ Máy sửa ở `seo_app/images/alt.py` (`_strip_ai_prefix`) trước T-056; gỡ `xfail` khi XPASS.
- **Cho Chỉ Huy (phiếu T-056)**: dựng `DraftImage(…, tags=checked.tags)` (ảnh AI phải truyền thẻ, mặc định là ảnh thật); hiện `exc.maybe_draft` cùng `exc.uploaded`, `exc.maybe_uploaded` (đề xuất của Thợ Máy, tôi đồng ý).

## Câu hỏi cho chủ dự án

Không có.

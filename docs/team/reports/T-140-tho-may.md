# Báo cáo T-140 · Thiết kế: ảnh tự chọn từ thư mục và ảnh minh họa AI miễn phí (Cloudflare Workers AI)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-140](../tickets/T-140-thiet-ke-anh-tu-chon-va-anh-ai-cloudflare.md) |
| Nhánh | `team/T-140` (từ `main` `c5d1fd2`) |
| Ngày nộp | 2026-11-18 14:16 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành (thiết kế, không sửa mã) |

## Tóm tắt (cho chủ dự án)

**Ảnh trong thư mục: app tự chọn, không hỏi.**

- Mỗi «chỗ cần ảnh» trong bài có một câu mô tả, ví dụ «cận cảnh bản lề cổng inox bị gỉ». App đọc câu đó, tìm các chữ có trong danh sách thẻ (cổng, bản lề, inox, Tân Phú, trước khi sửa…), rồi so với thẻ của ảnh (lấy từ tên thư mục như «CT012 - Cổng inox - Tân Phú/truoc»).
- Ảnh khớp rõ (đúng vật, đúng chất liệu…) thì app tự gắn vào chỗ đó. Không khớp thì chỗ đó dùng ảnh minh họa AI.
- App **chỉ đọc tên thư mục, tên file**, không gửi ảnh cho AI nào để so, và không mở file ảnh khi tìm. Nhờ vậy Google Drive không phải tải cả nghìn ảnh về máy.
- Một ảnh không dùng hai lần trong một bài. Ảnh đã đăng ở bài khác thì app tránh, nhờ một sổ nhỏ ghi lại ảnh đã gửi (sổ này chỉ có trên máy đó).
- Ảnh tự chọn vẫn hiện ở bước ảnh và ở màn hình xem lại trước khi gửi. Bạn đổi hay bỏ được.

**Ảnh minh họa AI: miễn phí, app tự tạo bằng Cloudflare Workers AI.**

- Mô hình FLUX.1 [schnell] của Cloudflare tạo một ảnh **vuông 1024×1024** trong vài giây.
- Gói miễn phí cho 10.000 «neuron» mỗi ngày. Một ảnh tốn khoảng 58 neuron, nên **khoảng 170 ảnh mỗi ngày**, dư cho vài chục bài.
- Hạn mức đặt lại lúc **7 giờ sáng** giờ Việt Nam. App tự đếm, sắp hết thì báo trước.
- Cloudflare ghi rõ trong tài liệu: **không dùng chữ bạn gửi hay ảnh tạo ra để huấn luyện AI**, và không giữ lại sau khi tạo xong. App chỉ gửi đi một câu mô tả ảnh bằng tiếng Anh, không gửi ảnh hay thông tin khách nào.
- Ảnh AI luôn ghi rõ là ảnh minh họa: alt bắt đầu «Minh họa», chú thích dưới ảnh «Ảnh minh họa (AI)», tên file `minh-hoa-ai-…`. Ảnh AI chỉ minh họa khái niệm (bộ phận, dấu hiệu hư, cách làm), **không bao giờ giả làm công trình xưởng đã làm**.

**Việc bạn cần làm** (khi có phiếu code, README sẽ có hướng dẫn từng bước):

- Tạo tài khoản Cloudflare miễn phí.
- Tạo một «mã truy cập» (API token) chỉ có quyền Workers AI.
- Dán mã đó và mã tài khoản vào file `.env`.

**Có 4 câu hỏi cho bạn**, ở cuối báo cáo. Câu nào cũng có khuyến nghị sẵn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-140-tho-may.md` | Báo cáo này (mới) |

- Không sửa mã, cấu hình, test.
- Không gọi Cloudflare thật, không tạo token.
- Tài liệu Cloudflare do một agent phụ của phiên này đọc ngày 2026-11-18, chỉ đọc trang tài liệu chính thức (nguồn ở mục 0).
- Phiếu T-053 (tạo ảnh AI bằng Gemini, đang hoãn) được thay bằng thiết kế này. Ghi chú vào T-053 là việc của Chỉ Huy.

## 0. Nguồn đã đọc

**Trong dự án:**

- Phiếu T-053, T-056, T-062.
- Báo cáo thiết kế T-046 (mục 4 ảnh AI, mục 5 thẻ), biên bản Lá Chắn T-046 (góp ý 3, 5, 6).
- Mã: `seo_app/images/` (`folders.py`, `tags.py`, `process.py`, `naming.py`, `alt.py`), `seo_app/ai/` (`registry.py`, `base.py`: `prepare_images`, `redact_secrets`), `seo_app/storage/drafts.py` (`DraftImage`), `seo_app/storage/sqlite_file.py` (T-136), `seo_app/google/sheets.py` (lớp vận chuyển dùng chung), `seo_app/wordpress/client.py` (`DraftImage` phía client), `seo_app/publish/render.py` (`ArticleImage`), `app/views/write.py` (chỗ cần ảnh, màn hình xác nhận), `config/ai.toml`, `config/content.toml`, `seo_app/content/prompts.py`.

**Tài liệu Cloudflare** (đọc 2026-11-18; ngày trong ngoặc là ngày cập nhật ghi trên trang):

| Chủ đề | Nguồn |
|---|---|
| Mô hình flux-1-schnell, ví dụ gọi | https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/ |
| Khuôn đầu vào, đầu ra | https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/schema-input.json, `…/schema-output.json` |
| Đường gọi REST `ai/run`, quyền | https://developers.cloudflare.com/api/resources/ai/methods/run/ |
| Hướng dẫn REST, vỏ JSON trả lời | https://developers.cloudflare.com/workers-ai/get-started/rest-api/ (15/09/2026) |
| Giá, hạn mức miễn phí, giờ đặt lại | https://developers.cloudflare.com/workers-ai/platform/pricing/ (12/11/2026) |
| Giới hạn tần suất | https://developers.cloudflare.com/workers-ai/platform/limits/ (17/09/2026) |
| Mã lỗi | https://developers.cloudflare.com/workers-ai/platform/errors/ (06/11/2026) |
| Dùng dữ liệu, lưu giữ | https://developers.cloudflare.com/workers-ai/platform/data-usage/ (16/10/2026) |
| Điều khoản Developer Platform | https://www.cloudflare.com/service-specific-terms-developer-platform/ (28/09/2026) |
| Tạo token, quyền, giới hạn IP, thời hạn | https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ (06/11/2026), https://developers.cloudflare.com/fundamentals/api/reference/permissions/ (15/11/2026), https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/ (20/04/2026) |
| Tìm mã tài khoản | https://developers.cloudflare.com/fundamentals/account/find-account-and-zone-ids/ (03/08/2026) |
| Danh sách mô hình, mô hình sắp ngừng | https://developers.cloudflare.com/workers-ai/models/ (12/08/2026), https://developers.cloudflare.com/changelog/post/2026-11-05-planned-model-deprecations/ |

## 1. Tự chọn ảnh thư mục

### 1.1. Đầu vào của một chỗ cần ảnh

| Nguồn | Có gì | Ghi chú |
|---|---|---|
| `img-<id>` (mô tả ảnh trong dàn ý, `OutlineItem.image`) | Câu tiếng Việt: ảnh nên đặt ở mục này để làm gì | Người dùng đã duyệt ở bước Dàn ý. **Nguồn chính** |
| `heading-<id>` (tiêu đề mục) | Chữ tiếng Việt | Bổ sung khi mô tả thiếu vật |
| Từ khóa chính, dòng kế hoạch | Chữ tiếng Việt | Bổ sung khu vực, hạng mục chung của bài |

### 1.2. Rút «mặt thẻ» từ chữ (không AI)

- Hàm mới `text_facets(text) -> TextFacets` trong `seo_app/images/tags.py`.
- Quét chữ tự do bằng **đúng danh sách cố định** của module: `_CATEGORY_OBJECTS`, `_CATEGORY_MATERIALS`, `_CATEGORY_ACTIONS`, `AREAS` (kèm `_AREA_ALIASES`, `_AREA_PREFIXES`), `_PHASE_WORDS`.
- Khớp cụm dài nhất trước, so không dấu, không phân biệt hoa thường; cùng bước làm sạch `clean_folder_name`.
- Kết quả **chỉ gồm giá trị của danh sách** (như mọi thẻ), nên không có chữ tự do nào đi tiếp.
- Thêm vài chữ chỉ giai đoạn hay gặp trong mô tả: «hư hỏng», «bị gỉ», «xệ», «kẹt» → nghiêng `truoc`; «hoàn thiện», «sau khi sửa» → `sau` (đã có trong `_PHASE_WORDS`). Danh sách thêm do Thợ Máy đề xuất, Ngòi Bút duyệt chữ.

### 1.3. Ứng viên

- **Lọc theo thư mục trước, chỉ đọc tên** (giữ ngân sách quét 5.000 mục, 10 giây của T-048):
  1. Với từng thư mục gốc còn dùng được (`ImageLibrary.roots()`): `list_folder(root, "", recursive=False)` lấy thư mục con tầng đầu, tính `tags_for_folder` từng thư mục.
  2. Chấm điểm thư mục bằng chính hàm chấm ở 1.4, trên thẻ thư mục. Bỏ thư mục có hạng mục khác hẳn.
  3. Với tối đa 5 thư mục điểm cao nhất: `list_folder(root, rel, recursive=True, page_size=200)` từng trang, tối đa 1.000 ảnh mỗi lần tự chọn.
  4. Thẻ ảnh lấy bằng `ImageTagStore.resolve_many` theo từng trang (≤ 200, điều kiện Lá Chắn T-074 i). Thẻ sửa tay đè thẻ thư mục, như bây giờ.
- **Không mở file ảnh nào** khi tìm (quét chỉ đọc tên và `stat`). Chỉ ảnh được chọn mới bị đọc (xem trước, nén WebP), như khi người dùng tự chọn.
- Giữ LC-T055-1: không bao giờ gọi `list_folder` với thư mục lấy từ nháp; luôn đi từ thư mục gốc xuống.
- **Ảnh AI có sẵn trong thư mục** (thư mục, tên file có dấu hiệu AI) cũng là ứng viên, vẫn là ảnh AI (`ImageTags.source = "ai"`, không thẻ công trình).

### 1.4. Chấm điểm (số nguyên, cố định, test được)

| Thành phần | Điểm | Ví dụ |
|---|---|---|
| Vật trùng đúng (cùng cụm: «cửa kéo» – «cửa kéo») | +6 | Mô tả «bánh xe cửa kéo», ảnh «Thay bánh xe cửa kéo» |
| Vật cùng họ (một bên chung hơn: «cửa» – «cửa kéo») | +3 | |
| Chất liệu trùng | +2 | inox – inox |
| Chất liệu khác hẳn (hai bên đều có, không trùng) | −2 | cổng inox – cổng sắt |
| Việc trùng (sửa, thay, sơn…) | +1 | |
| Khu vực trùng khu vực của bài | +2 | Bài «sửa cổng Tân Phú», ảnh ở Tân Phú |
| Giai đoạn trùng (trước, sau) | +2 | Mô tả «bị gỉ» (trước), ảnh `truoc` |
| Giai đoạn ngược | −2 | |

- **Ngưỡng «đủ hợp»:** có vật trùng đúng, hoặc tổng ≥ 5 **và** có vật cùng họ. Không có vật nào trùng thì **không bao giờ** tự chọn (khu vực, giai đoạn không đủ).
- **Không đủ ngưỡng:** chỗ đó sang ảnh minh họa AI (mục 2).
- **Hòa điểm:** ưu tiên ảnh chưa dùng ở bài khác; rồi giai đoạn hợp; rồi ảnh mới sửa gần nhất (`ImageEntry.modified`); rồi thứ tự `ImageRef` (ổn định giữa các lần chạy).
- **Gán theo thứ tự các chỗ trong bài**, tham lam: chỗ đầu chọn trước. Ảnh đã gán cho một chỗ thì bỏ khỏi danh sách của các chỗ sau. Một ảnh không dùng hai lần trong bài; bản sao (cùng tên, cùng cỡ, cùng giờ sửa) tính là một ảnh.

### 1.5. Ảnh đã dùng ở bài khác: dữ liệu cần có

| Cách | Ưu | Nhược | Chọn |
|---|---|---|---|
| Đọc ảnh trong các nháp còn trong kho | Không thêm gì | Kho chỉ giữ 30 nháp; nháp xóa thì mất | Không |
| **Sổ ảnh đã gửi** (SQLite mới trong `data/`), ghi khi «Gửi nháp» thành công | Đúng sự thật (chỉ ảnh đã lên website), không cần đọc file | Mỗi máy một sổ: máy kia không biết | **Có** |
| Ghi dấu vào WordPress Media (mô tả, meta) | Hai máy cùng thấy | Phải sửa media cũ hay mở thêm trường (trái W2, T-061 bỏ `description`) | Không |
| Ghi vào Google Sheet | Hai máy cùng thấy | Nặng, ngoài phạm vi kế hoạch | Không |

- **Dấu vân tay mỗi ảnh:** tên file (chữ thường), cỡ byte, giờ sửa làm tròn giây, kèm `ImageRef`. Không băm nội dung (băm phải đọc cả file, Drive sẽ tải về).
- Ảnh dời thư mục trên cùng máy vẫn nhận ra (tên, cỡ, giờ sửa không đổi).
- Ghi sổ chỉ khi website xác nhận bài nháp đã tạo, cho đúng các ảnh thư mục đã tải.
- Sổ giữ tối đa 10.000 dòng. Xóa sổ chỉ mất phần «tránh lặp lại», không mất gì khác.

### 1.6. Có gửi ảnh cho AI để so không

**Không.** Chỉ dùng thẻ và tên file. Lý do:

- Ảnh công trình có thể có biển số nhà, mặt người, chữ trên biển hiệu.
- Gemini gói miễn phí có thể dùng dữ liệu để cải tiến sản phẩm (sổ rủi ro 18/11 chỉ chấp nhận cho việc viết alt, theo từng lần bấm).
- So hàng trăm ảnh bằng AI chậm và tốn lượt.
- Điều kiện Lá Chắn T-050 số 3: AI chỉ xem ảnh khi người dùng bấm, cho ảnh đã chọn.

Thẻ thư mục theo quy ước 3A đã đủ tốt; tên thư mục chưa theo quy ước thì chỗ đó dùng ảnh AI, không đoán.

### 1.7. Khi nào chạy

- **Tự động một lần cho mỗi bài**, khi bài đã viết xong và người dùng mở phần chỗ cần ảnh.
  - Chạy trong luồng riêng như quét thư mục hiện nay, có dòng «Đang tìm ảnh trong thư mục…».
  - Kết quả nhớ trong nháp.
- **Chỉ điền chỗ chưa có quyết định.** Chỗ người dùng đã chọn tay hay đã bấm «Để trống chỗ này» thì không bao giờ bị đè.
- Có nút «🔄 Tìm lại ảnh cho các chỗ còn trống» khi người dùng thêm ảnh vào thư mục.

## 2. Ảnh AI qua Cloudflare Workers AI

### 2.1. Sự thật từ tài liệu (dùng trong thiết kế)

| Điểm | Theo tài liệu | Còn phải xác minh bằng **một lần gọi thử** (chủ dự án hoặc Chỉ Huy, ngoài bộ test) |
|---|---|---|
| Đường gọi | `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell`, header `Authorization: Bearer <token>` | |
| Thân lệnh | JSON, chỉ hai trường: `prompt` (chuỗi 1–2048 ký tự, bắt buộc), `steps` (số nguyên ≤ 8, mặc định 4); khuôn **không nhận trường lạ** | Ví dụ trên trang mô hình có gửi `seed`, trái với khuôn: **không gửi `seed`** |
| Trả lời | Vỏ chung `{"result": …, "success": true, "errors": [], "messages": []}`; đầu ra của mô hình là `{"image": "<base64>"}` | Ảnh nằm ở `result.image` (ghép hai trang, chưa có ví dụ riêng); JPEG hay PNG (trang mô hình dùng JPEG, trang API chung nói PNG); cỡ ảnh (tài liệu không ghi; không chỉnh được width/height) |
| Giá | 4,80 neuron mỗi ô 512×512 + 9,60 neuron mỗi bước; 0,011 USD mỗi 1.000 neuron | Ô lẻ có làm tròn lên không: tài liệu không ghi |
| Miễn phí | 10.000 neuron/ngày ở cả gói Free và Paid; đặt lại 00:00 UTC (7:00 giờ Việt Nam); gói Free hết hạn mức thì mọi lệnh sau báo lỗi | |
| Hết hạn mức | Mã 3036 «Account limited», HTTP 429 | Thân lỗi REST trông thế nào: tài liệu không mô tả |
| Quá tải | Mã 3040 «Out of capacity», HTTP 429, thử lại được | |
| Tần suất | 720 lệnh/phút cho nhóm tạo ảnh | Không ảnh hưởng: app gọi từng ảnh một |
| Dữ liệu | Không dùng nội dung khách (đầu vào, đầu ra) để huấn luyện; không giữ sau khi xử lý (trừ khi bật lưu log, cache, AI Gateway); giữ siêu dữ liệu vận hành (mô hình, giờ, cỡ, số neuron, mã lỗi). Trang mô hình: Cloudflare tự chạy, «Zero data retention: Yes» | |
| Bộ lọc an toàn | Tài liệu không nói prompt bị chặn thì báo lỗi hay trả ảnh đen | App tự kiểm ảnh trống (2.6) |
| Chuyển hướng, URL | Mô hình `@cf/…` trả ảnh ngay trong câu trả lời; mô hình «Third-party» (Recraft…) trả URL trên r2.dev | **Chỉ dùng mô hình `@cf/` trả base64** |

**Số ảnh mỗi ngày** (tự tính, coi ảnh 1024×1024 là 4 ô):

| Số bước | Neuron/ảnh | Ảnh/ngày (10.000 neuron) |
|---|---|---|
| 4 (mặc định, khuyến nghị) | 57,6 | 173 |
| 8 (nét hơn) | 96,0 | 104 |

Một bài 4–6 chỗ cần ảnh, tạo lại mỗi ảnh một lần: khoảng 700 neuron, tức khoảng 14 bài mỗi ngày.

**Mô hình khác** (để sau, không làm ở đợt này):

- **flux-2-klein-4b:** cho chọn cỡ ảnh (ảnh ngang), khoảng 104 neuron/ảnh 1024×1024 (95 ảnh/ngày). Nhưng phải gửi multipart, và mô hình ghi «Partner».
- **Bốn mô hình Stable Diffusion** ngừng ngày 20/11/2026 (HTTP 410, mã 5028): **không dùng**.

### 2.2. Đặt mã ở đâu

| Phần | Module | Việc |
|---|---|---|
| Client Cloudflare | `seo_app/ai/cloudflare_images.py` (mới) | Một lệnh `generate(prompt, steps) -> GeneratedImage` |
| Ảnh AI → ảnh web sạch | `seo_app/images/generated.py` (mới) | Mở có kiểm, dựng lại từ điểm ảnh, đi qua `make_web_image`, kiểm WebP sạch |
| Kho ảnh AI đã tạo | `seo_app/images/generated.py` | Thư mục `data/ai_images/` (2.7) |
| Đếm lượt, sổ ảnh đã gửi | `seo_app/storage/image_usage.py` (mới) | SQLite qua `sqlite_file` của T-136 |
| Cấu hình | `seo_app/ai/registry.py`, `config/ai.toml`, `seo_app/config.py`, `.env.example` | Hãng `cloudflare` chỉ cho việc `image` |

- **Không thêm thư viện:** `requests` đã là thư viện trực tiếp (client WordPress, Google); `base64`, `json` có sẵn.
- **Lớp vận chuyển:** dùng lại `_Bearer`, `_refuse_redirect`, `_read_limited`, `_Redirected`, `_TooLarge` của `seo_app/google/sheets.py`.
  - Đề xuất chuyển các hàm này sang module chung nhỏ (ví dụ `seo_app/http_guard.py`), để module ảnh không phải nhập từ gói Google.
  - Phiếu code chạy test của cả client Sheets, Search Console và Cloudflare (như ghi chú LC-T120-18 trong `sheets.py`).

### 2.3. Đường gọi cố định

- **Máy chủ** cố định `https://api.cloudflare.com`.
- **Đường dẫn** ghép từ hằng số và hai giá trị đã kiểm:
  - `account_id` phải đúng 32 ký tự hex thường (kiểm lúc đọc `.env`; sai thì câu lỗi không chép lại giá trị);
  - `model` phải nằm trong danh sách cho phép trong mã, đợt này chỉ có `@cf/black-forest-labs/flux-1-schnell`.
  - Tên mô hình lạ trong `config/ai.toml` thì báo «chưa hỗ trợ mô hình này», không gọi.
- **Không có tham số query.** Không đọc biến môi trường nào để đổi địa chỉ hay thêm header (như T-026, T-028).
- **Lệnh, header:** `POST`, `Content-Type: application/json`, header `Authorization` gắn qua `_Bearer` (`repr` không lộ token). Không gửi header nào khác do người dùng hay file cấu hình đặt.
- **Chuyển hướng:** `allow_redirects=False`, phiên `max_redirects = 0`, móc `_refuse_redirect`. Gặp 3xx thì đóng, không đọc thân, báo lỗi cố định.
- **Giờ chờ** 60 giây (tạo ảnh mất vài giây). Đọc câu trả lời theo luồng, tối đa 16 MB (`_read_limited`).
- **Thử lại:** không tự thử lại lệnh tạo ảnh (mỗi lần là một lần tốn neuron). Riêng 3040 (quá tải) báo «thử lại sau ít phút».
- **Kiểm tra kết nối** ở Cài đặt (không tốn neuron): `GET https://api.cloudflare.com/client/v4/user/tokens/verify`, đường cố định thứ hai.
  - Chỉ đọc `result.status == "active"`.
  - Lệnh này **không** chứng minh token có quyền Workers AI. Câu báo nói rõ «token hợp lệ; quyền tạo ảnh sẽ biết ở lần tạo ảnh đầu».

### 2.4. Thân lệnh và câu trả lời

- **Thân:** `{"prompt": <prompt cuối>, "steps": <số bước>}`. Đúng hai trường, `steps` từ `[tasks.image] steps` (1–8, mặc định 4).
- Prompt cuối dài 1–2048 ký tự (sau khi ghép đuôi cố định ở 3.3); dài hơn thì báo lỗi, **không cắt ngầm**.
- **Câu trả lời được nhận khi:**
  - HTTP 200;
  - JSON là object, `success is True`;
  - `result` là object, `result.image` là chuỗi;
  - chiều dài chuỗi ≤ 12 triệu ký tự **trước khi** giải mã;
  - `base64.b64decode(…, validate=True)` không lỗi;
  - byte giải ra ≤ 9 MB.
- **Bị từ chối, không đọc gì khác:** thiếu `image`; `image` là URL hay không phải base64; có trường `url`.
  - Không bao giờ tải ảnh theo địa chỉ trong câu trả lời (góp ý Lá Chắn T-046 số 6).
- **Câu lỗi tiếng Việt cố định**, không chép lời máy chủ, không chép mã tài khoản:

| Trường hợp | Câu báo (ý) |
|---|---|
| 401, 403 (token sai, hết hạn, thiếu quyền; 3023 tài khoản bị chặn) | «Mã truy cập Cloudflare không dùng được (sai, hết hạn hoặc thiếu quyền Workers AI). Xem Cài đặt → Kết nối.» |
| 429 kèm mã 3036 | «Hôm nay đã hết lượt tạo ảnh miễn phí của Cloudflare. Lượt mới có lúc 7 giờ sáng.» (ghi luôn bộ đếm của ngày đó là đầy) |
| 429 kèm 3040, hay 429 không rõ mã | «Cloudflare đang quá tải. Thử lại sau ít phút.» |
| 400 (prompt sai khuôn, 5004, 3003), 404/410 (3042, 5007, 5028) | «Cloudflare từ chối lệnh tạo ảnh (mã HTTP …). Thử sửa prompt; vẫn lỗi thì báo Chỉ Huy.» |
| 408, hết giờ chờ, mất mạng | «Không nhận được ảnh từ Cloudflare (mạng chậm hoặc mất mạng). Thử lại.» (có thể đã tốn neuron: ghi bộ đếm như đã tạo) |
| 5xx, trả lời sai khuôn, quá lớn, chuyển hướng | Câu cố định kèm mã HTTP |

- **Mã lỗi Cloudflare** (3036, 3040…) chỉ đọc khi đúng là số nguyên trong `errors[].code`, và chỉ so với danh sách đã biết. Chữ `message` của máy chủ không bao giờ hiện lên trang.

### 2.5. Biến `.env` và token tối thiểu

- **Biến mới:** `CLOUDFLARE_ACCOUNT_ID` và `CLOUDFLARE_API_TOKEN`, thêm vào `ENV_VARS` của `seo_app/config.py` (test cũ kiểm `.env.example` đủ tên).
  - `.env.example` có chú thích tiếng Việt, không có giá trị.
  - `Settings` giữ token với `repr=False`. Trang Cài đặt chỉ hiện «đã nhập / chưa nhập».
- **Che khóa trong câu lỗi:** `redact_secrets` thêm mẫu token mới của Cloudflare (tiền tố `cfut_`, theo trang tạo token); mẫu `bearer …` đã có.
- **Token tối thiểu**, hướng dẫn cho README (Thư Ký):
  - Tạo token tùy chỉnh, phạm vi **Account**, chỉ một tài khoản, chỉ các quyền **Workers AI**.
  - Hai trang tài liệu ghi lệch nhau: hướng dẫn REST đòi cả `Workers AI Read` và `Workers AI Edit`, còn trang API của lệnh `run` nhận một trong hai. Không có quyền «Run» riêng.
  - **Khuyến nghị:** bắt đầu bằng chỉ `Workers AI Read`. Lần gọi thử báo 403 thì thêm `Workers AI Edit`. Ghi kết quả vào sổ rủi ro.
  - Không cấp quyền nào ngoài Workers AI (DNS, Workers, Pages, R2…).
  - **Nên đặt ngày hết hạn** (ví dụ 1 năm). Lọc theo IP chỉ khi mạng có IP cố định (IP nhà mạng thường đổi). Lệnh kiểm token không chịu bộ lọc IP.
  - Mã tài khoản lấy ở Workers & Pages → Account Details, hay ngay trên trang hướng dẫn REST của Workers AI.

### 2.6. Ảnh trả về → ảnh web sạch

Hàm mới `make_generated_web_image(data: bytes) -> WebImage` trong `seo_app/images/generated.py`:

1. **Mở có kiểm** bằng `process._open`/`open_image`:
   - chỉ `JPEG`, `PNG`, `WEBP`;
   - giới hạn số điểm ảnh của module;
   - cạnh ảnh trong khoảng 256–2048 px;
   - ảnh tĩnh (một khung).
2. **Từ chối ảnh trống:** độ lệch màu của mọi kênh rất nhỏ, tức ảnh gần như một màu (ví dụ đen hẳn khi bộ lọc an toàn chặn). Câu báo: «Cloudflare trả về ảnh trống (prompt có thể bị chặn). Sửa prompt rồi tạo lại.»
3. **Dựng lại từ điểm ảnh** như `make_ai_image`:
   - ảnh mới RGB, dán điểm ảnh, bỏ `im.info`;
   - không EXIF, XMP, ICC, chú thích, chunk chữ.
   - Ghi tạm ra PNG trong bộ nhớ, rồi đưa qua **`make_web_image`** (điều kiện Lá Chắn T-049 số 5: ảnh AI trả về đi qua `make_web_image`).
   - Vì ảnh vào không còn EXIF, WebP ra không có EXIF, không GPS.
   - `make_web_image` không phóng to: ảnh 1024 px giữ 1024 px.
4. **Kiểm byte WebP ra** bằng bộ kiểm cấu trúc `_check_webp` của `seo_app/ai/base.py` (bộ kiểm của `prepare_images`): chỉ có `VP8`/`VP8L`/`VP8X`/`ALPH`, không `EXIF`/`XMP`/`ICCP`, không ảnh động.
   - Đây là byte sẽ lên WordPress, nên «ảnh trả về chở dữ liệu lạ» được chặn ở đúng chỗ ra.
   - Bản gốc Cloudflare không bao giờ được lưu hay gửi đi.
5. **Không thêm EXIF đánh dấu AI** (đề xuất cũ của T-046). Đánh dấu bằng chữ cố định:
   - tên file `image_file_name(..., ai_generated=True)` → `minh-hoa-ai-…`;
   - tiêu đề Media `[AI] …` (client đã làm khi `tags.source == "ai"`);
   - alt «Minh họa…», chú thích «Ảnh minh họa (AI)…» (`clean_alt_text`, `_ai_wording` đã làm).
   - Muốn thêm EXIF thì phải sửa danh sách cho phép 2A, Lá Chắn soát riêng: không cần.

### 2.7. Kho ảnh AI đã tạo (`data/ai_images/`)

Hiện `DraftImage` của ảnh AI chỉ nhớ prompt. Ảnh tạo xong phải nằm trên máy tới lúc «Gửi nháp» (không tải lên WordPress sớm: ảnh lên Media là công khai ngay).

- **File** `data/ai_images/<sha256>.webp` (tên là băm SHA-256 của chính byte WebP).
  - Ghi nguyên tử (file tạm rồi đổi tên).
  - `dir_has_link` trước mọi lần đọc, ghi, xóa (T-117).
  - Kiểm thư mục nằm trong `.gitignore` như `PreviewCache` (`_cache_dir_is_ignored`).
  - Mỗi file ≤ 2 MB.
- **Đọc lại** (mở nháp, lúc gửi): băm byte phải khớp tên và khớp nháp; rồi kiểm lại như bước 4 ở 2.6. Sai thì coi như mất ảnh, chỗ đó báo «Ảnh AI không còn trên máy này, bấm Tạo lại».
- **`DraftImage`** (khuôn nháp 4, nháp cũ đọc như cũ) thêm cho ảnh AI tạo trong app:
  - `generated_sha256` (64 hex);
  - `generator` (hằng `"cloudflare:flux-1-schnell"`);
  - `steps`;
  - `history`: tối đa 3 lần tạo trước (băm + prompt), để «quay lại ảnh trước» theo luật chung của dự án (mọi phần AI tạo đều có nút làm lại và quay lại bản trước).
  - Trường `prompt` có sẵn giữ **đúng prompt tiếng Anh đã gửi**. Mô tả tiếng Việt vẫn ở dàn ý.
  - `approved_sha256` (T-089) dùng chung cách: ảnh người dùng đã xem, duyệt alt phải đúng ảnh sẽ tải.
- **Dọn:**
  - giữ mọi file còn được nháp trong kho nhắc tới (kể cả `history`);
  - file không ai nhắc tới, cũ hơn 14 ngày thì xóa lúc mở app;
  - cả thư mục quá 500 file hay 500 MB thì xóa file không ai nhắc tới, cũ nhất trước.
  - Chỉ xóa tên khớp đúng mẫu `^[0-9a-f]{64}\.webp$` trong đúng thư mục này. Xóa file trong máy không đụng W2 (W2 là website).
- **Hai máy:** nháp và ảnh AI đều chỉ ở máy đang dùng (như kho nháp hiện nay). Mở bài ở máy kia thì tạo lại ảnh.

### 2.8. Đếm lượt, chặn trước khi chạm hạn mức

- **Kho** `data/image_usage.sqlite`, dùng `sqlite_file` của T-136: so cấu trúc, `trusted_schema = OFF`, `dir_has_link`.
  - Bảng `cf_usage(day TEXT PRIMARY KEY, neurons REAL, images INTEGER)`, `day` là ngày UTC.
  - Cùng file có bảng sổ ảnh đã gửi ở 1.5.
- **Ước tính mỗi ảnh:** `số_ô × 4,80 + steps × 9,60`; số ô lấy từ cỡ ảnh thật nhận được (làm tròn lên theo ô 512). Trước khi gọi, ước tính với 1024×1024.
- **Trần app tự đặt:** 9.000 neuron mỗi ngày UTC (chừa 10% cho sai số và cho máy kia). Chạm trần thì không gọi, báo câu 3036 kèm «ước tính trên máy này».
- **Ghi bộ đếm** ngay khi gửi lệnh (kể cả lệnh lỗi mạng, hết giờ: có thể đã tốn neuron). Nhận 3036 thì ghi đầy cho ngày đó.
- **Hiện ở bước ảnh:** «Hôm nay còn khoảng N ảnh AI (ước tính, đặt lại lúc 7:00)».
- **Giới hạn:** hai máy dùng chung một tài khoản Cloudflare thì mỗi máy chỉ đếm phần của mình. Lỗi 3036 của Cloudflare là chốt chặn cuối, có câu báo dễ hiểu.

### 2.9. Cấu hình (`config/ai.toml`, `registry.py`)

```toml
[tasks.image]  # tạo ảnh minh họa (Cloudflare Workers AI, miễn phí 10.000 neuron/ngày)
provider = "cloudflare"
model = "@cf/black-forest-labs/flux-1-schnell"
steps = 4      # 1–8; 4 ≈ 58 neuron/ảnh, 8 ≈ 96 neuron/ảnh
```

- `PROVIDERS["cloudflare"] = ("Cloudflare Workers AI", "CLOUDFLARE_API_TOKEN")`.
- `IMAGE_PROVIDERS = ("cloudflare",)`: Gemini, OpenAI tạo ảnh chưa có mã (T-053 không làm), thêm lại khi có.
- `cloudflare` cho việc khác `image` thì báo «Cloudflare chỉ dùng để tạo ảnh».
- `steps` kiểm như `_positive_int` (không nhận `true`/`false`), trong khoảng 1–8.
- Thiếu `CLOUDFLARE_ACCOUNT_ID`/`CLOUDFLARE_API_TOKEN` chỉ báo khi tạo ảnh (provider lười, T-062).
- Ghi chú hướng dẫn trong `config/ai.toml` do Ngòi Bút viết lại (bỏ các dòng Gemini «CHƯA XÁC MINH»).

## 3. Prompt ảnh

### 3.1. Tiếng Anh

FLUX.1 hiểu tiếng Anh tốt nhất. Prompt tiếng Việt cho ra ảnh kém, dễ ra chữ lạ. Prompt gửi Cloudflare **luôn bằng tiếng Anh**. Người dùng thấy cả mô tả tiếng Việt (dàn ý) và prompt tiếng Anh.

### 3.2. Ai viết prompt tiếng Anh

- **Việc AI mới** `[tasks.image_prompt]`, cùng hãng với việc meta, hiện là Gemini Flash miễn phí.
  - **Đầu vào:** mô tả ảnh tiếng Việt, tiêu đề mục, mặt thẻ (vật, chất liệu, giai đoạn). Không gửi chữ nào của thư mục ảnh hay của khách (A3).
  - **Lời dặn:** dữ liệu tách khỏi chỉ thị (A1, khung `_block` như các prompt khác).
  - **Trả về khuôn** `ImagePrompt(prompt_en: str ≤ 600 ký tự, alt_vi: str ≤ 125 ký tự)`.
- **Mã kiểm kết quả AI** (A2), sai thì bỏ, báo «Viết lại prompt»:
  - một dòng, không ký tự điều khiển hay vô hình;
  - không link, email, số điện thoại (`has_link`, bộ dò thông tin cá nhân của T-100);
  - không tên «Pro-Metal», tên miền website;
  - không tên quận, huyện (`AREAS`, so không dấu).
- **`alt_vi`** đi qua `clean_alt_text` với `ai_generated=True`: luôn mở đầu «Minh họa». Người dùng vẫn tick duyệt alt như mọi ảnh.
  - Không gọi AI đọc ảnh cho ảnh AI: không cần, và không tốn lượt Gemini.

### 3.3. Luật cố định trong mã (không sửa được qua `config/`)

Ngòi Bút viết chữ, Lá Chắn duyệt. Đuôi tiếng Anh do mã ghép vào **mọi** prompt (như `ALT_SYSTEM`: phần bảo vệ nằm trong mã, `config/` chỉ bổ sung). FLUX không có prompt phủ định, nên viết theo kiểu khẳng định:

- không chữ, không số, không logo, không hình mờ, không biển hiệu đọc được;
- người (nếu có) ở xa hay quay lưng, không thấy rõ mặt;
- không thương hiệu;
- bối cảnh chung (nhà phố, xưởng nói chung), không địa chỉ, không tên nơi.

### 3.4. Không giả «công trình đã làm»

- Ảnh AI chỉ minh họa **khái niệm**: bộ phận (bản lề, ray, bánh xe), dấu hiệu hư (gỉ, xệ, cong), dụng cụ, bước làm, kiểu dáng chung.
- Lời dặn cấm cảnh «thợ của xưởng đang làm tại nhà khách», «công trình hoàn thiện của chúng tôi».
- Mô tả trong dàn ý đòi ảnh công trình thật thì vẫn chỉ minh họa phần khái niệm.
- **Ngòi Bút sửa lời dặn dàn ý** (`seo_app/content/prompts.py`): câu hiện tại «ưu tiên ảnh thật của xưởng» đổi thành tả vật, tình trạng cần thấy trong ảnh, không gắn công trình hay khách cụ thể. Mô tả kiểu đó hợp cho cả so thẻ (mục 1) lẫn viết prompt.
- **Chú thích «Ảnh minh họa (AI)» hiện dưới ảnh** trên website (`figcaption`), không chỉ trong alt.

### 3.5. Sửa và tạo lại

| Nút | Việc | Tốn |
|---|---|---|
| ✏️ Sửa prompt | Sửa thẳng prompt tiếng Anh (≤ 2048 ký tự sau khi ghép đuôi) | 0 |
| 📝 Viết lại prompt | AI viết lại prompt từ mô tả tiếng Việt | 1 lần gọi Gemini |
| 🔄 Tạo lại | Gửi lại prompt hiện tại; ảnh khác vì không gửi `seed` | ~58 neuron |
| ↩️ Ảnh trước | Quay lại một trong 3 ảnh trước (`history`) | 0 |

## 4. Giao diện (Họa Sĩ làm sau)

**Bước ảnh trên trang Soạn bài:**

- **Dòng đầu:** «Đã tự chọn 2 ảnh từ thư mục, 3 chỗ dùng ảnh minh họa AI. Hôm nay còn khoảng N ảnh AI (ước tính, đặt lại 7:00).»
- **Nút cả bài:** «✨ Tạo ảnh minh họa cho N chỗ còn trống» (câu hỏi 2), kèm «🔄 Tìm lại ảnh trong thư mục».
- **Mỗi chỗ:**
  - Nhãn nguồn: `📁 Tự chọn từ thư mục`, `✨ Ảnh minh họa AI`, `🖐 Bạn chọn`.
  - Ảnh xem trước: `st.image` chỉ nhận ảnh JPEG xem trước app tự dựng (`make_preview`, LC-T058-2), kể cả ảnh AI.
  - Nút: Đổi ảnh (mở thư mục như bây giờ), Tạo lại / Ảnh trước / Sửa prompt (ảnh AI), «Để trống chỗ này» (nhớ trong nháp, tự chọn không điền lại).
  - Alt, chú thích, tick duyệt: như hiện nay. «AI viết alt» chỉ cho ảnh thư mục, theo từng lần bấm (T-050).
- **Câu báo** hết lượt, lỗi token, quá tải: cố định, hiện bằng `st.warning`, có `escape_markdown`.

**Màn hình xác nhận (bước Xuất bản):**

- Liệt kê cả ảnh AI: nhãn «Ảnh minh họa (AI)», ảnh xem trước nhỏ, alt, chú thích, băm byte WebP.
- `shown_images` thêm nhánh cho ảnh AI: `ArticleImage.of(…, sha256=<băm WebP>, has_gps=False, tags=ImageTags.for_ai_image(category))`.
- Gói gửi dựng `wordpress.DraftImage(image=WebImage(...), alt, caption, tags=ImageTags(source="ai", …))`. Client đã đặt tên `minh-hoa-ai-…`, tiêu đề `[AI] …`.

**Cài đặt → 🔌 Kết nối, mục mới «Cloudflare Workers AI (tạo ảnh minh họa)»:**

- mã tài khoản, token: «đã nhập / chưa nhập» (không bao giờ hiện giá trị, kể cả 4 ký tự);
- nút «Kiểm tra kết nối» (lệnh kiểm token, không tốn neuron);
- «Hôm nay đã dùng khoảng X neuron trên máy này»;
- dòng ngắn về dữ liệu: chỉ gửi prompt chữ, Cloudflare không dùng để huấn luyện.

## 5. Bảo mật (cho Lá Chắn)

| Điểm | Thiết kế |
|---|---|
| Dữ liệu gửi Cloudflare | Chỉ prompt chữ tiếng Anh (từ mô tả đã duyệt, đuôi cố định) và số bước. Không gửi ảnh, tên thư mục, tên file, khu vực, tên khách. Mã tài khoản nằm trong đường dẫn (không phải bí mật, nhưng không hiện lên trang) |
| Chính sách dữ liệu | Cloudflare không dùng đầu vào, đầu ra để huấn luyện; không giữ sau khi xử lý; giữ siêu dữ liệu vận hành; flux-1-schnell do Cloudflare tự chạy, «Zero data retention: Yes» (nguồn mục 0). App **không** dùng AI Gateway, log hay cache của Cloudflare |
| Dữ liệu gửi Gemini (viết prompt) | Mô tả ảnh, tiêu đề mục: chữ của bài sẽ đăng công khai, không có dữ liệu khách (A3). Gói miễn phí: đã nằm trong sổ rủi ro 18/11 (mọi việc AI dùng Gemini miễn phí) |
| Token | Chỉ trong `.env`; `Settings` `repr=False`; không in, không log; `redact_secrets` thêm mẫu `cfut_…`. Token chỉ quyền Workers AI, phạm vi một tài khoản, nên có hạn dùng (2.5) |
| Đường gọi | Hai đường cố định (`ai/run/<mô hình trong danh sách>`, `user/tokens/verify`); `account_id` đúng 32 hex; không query; không header từ cấu hình hay biến môi trường; không theo chuyển hướng (`_refuse_redirect`); giờ chờ 60 giây; thân trả lời ≤ 16 MB |
| Ảnh trả về | Chỉ base64 trong JSON; không tải theo URL; giới hạn trước khi giải mã; mở có kiểm; dựng lại từ điểm ảnh; WebP ra qua `_check_webp` (2.6). Ảnh gốc của Cloudflare không lưu, không gửi đi |
| Ảnh AI là ảnh AI | `ImageTags(source="ai")`: không mã công trình, khu vực, trước/sau (đã có kiểm trong `ImageTags`). Tên file, tiêu đề Media, alt, chú thích đều đánh dấu |
| Kho ảnh AI, kho đếm | Trong `data/`, `dir_has_link`, gitignore, tên file theo mẫu, kiểm băm khi đọc; SQLite qua `sqlite_file` (T-136) |
| Chữ AI viết (prompt, alt) | A2: kiểm khuôn, độ dài, link, thông tin cá nhân, tên nơi (3.2) |
| Giấy phép FLUX.1 [schnell] | Tài liệu Cloudflare chỉ dẫn tới điều khoản của Black Forest Labs (bfl.ai), không ghi tên giấy phép. Phải đọc trang đó **trước khi bật** cho bài thật (việc của Lá Chắn hay Thư Ký) |

**Đề xuất sửa điều kiện C9 của Lá Chắn T-051** (cần Lá Chắn duyệt):

- C9 hiện nay: «chỉ tạo ảnh khi người dùng bấm, mỗi lần một ảnh; không tự tạo hàng loạt», với lý do chi phí.
- Với Cloudflare gói miễn phí, chi phí bằng 0. Thay bằng:
  - (a) chỉ tạo khi người dùng bấm (một nút cho cả bài, hay từng chỗ);
  - (b) mỗi lần bấm tối đa 8 ảnh, tạo lần lượt từng ảnh;
  - (c) kiểm trần neuron trước mỗi ảnh (2.8);
  - (d) không bao giờ tự tạo khi chỉ mở trang hay mở nháp.
- C8 (xác minh tên mô hình) đổi thành: **một lần gọi thử thật** trước khi bật, xác nhận vị trí `result.image`, định dạng (JPEG/PNG), cỡ ảnh, quyền token tối thiểu.

## 6. Chia phiếu code

Số phiếu do Chỉ Huy cấp. Ký hiệu tạm A–F.

| Phiếu | Ai | Việc | Kiểm định |
|---|---|---|---|
| **A** · Client Cloudflare, ảnh AI sạch, kho ảnh AI | Thợ Máy | <ul><li>`seo_app/ai/cloudflare_images.py`: 2.3, 2.4.</li><li>`seo_app/images/generated.py`: 2.6, 2.7.</li><li>`registry.py` (2.9), `config.py` + `.env.example` (2.5), `redact_secrets`.</li><li>Có thể chuyển lớp vận chuyển dùng chung ra module riêng.</li><li>Test với Cloudflare giả (adapter `requests` như `FakeWordPress`): mọi mã lỗi, thân sai khuôn, URL thay vì base64, quá lớn, chuyển hướng, ảnh trống, ảnh có EXIF/GPS/XMP (ra WebP sạch), không gọi mạng.</li></ul> | Soi Lỗi; **Lá Chắn đầy đủ** |
| **B** · Tự chọn ảnh thư mục, sổ ảnh đã gửi, đếm lượt | Thợ Máy | <ul><li>`tags.text_facets` (1.2); `seo_app/images/autopick.py` (1.3–1.5); `seo_app/storage/image_usage.py` (2.8 và sổ 1.5).</li><li>Test chấm điểm cố định (bảng ca tiếng Việt có dấu, không dấu, dính chữ), không mở file ảnh khi tìm (đếm `read_image_bytes`), ngân sách quét, không trùng ảnh trong bài.</li></ul> | Soi Lỗi; Lá Chắn rút gọn (F1, F3) |
| **C** · Luật prompt ảnh, lời dặn dàn ý | Ngòi Bút | <ul><li>Đuôi an toàn 3.3 (đưa Thợ Máy đặt vào mã), lời dặn việc `image_prompt`, mục `[image_prompt]` (bổ sung) trong `config/content.toml`, ví dụ tốt/xấu.</li><li>Sửa lời dặn dàn ý (3.4); ghi chú `[tasks.image]`, `[tasks.image_prompt]` trong `config/ai.toml`.</li></ul> | Lá Chắn rút gọn (A1) |
| **D** · Việc AI viết prompt, khuôn nháp 4 | Thợ Máy | <ul><li>`ImagePrompt`, hàm viết prompt có kiểm (3.2).</li><li>`DraftImage` thêm trường ảnh AI (2.7), nháp cũ đọc như cũ.</li><li>Chỉ phần khuôn `DraftImage`, không đụng phần mở kho, trạng thái gửi.</li></ul> | Soi Lỗi; Lá Chắn rút gọn (A1, A2) |
| **E** · Giao diện | Họa Sĩ | <ul><li>Mục 4: bước ảnh, màn hình xác nhận, đường gửi ảnh AI, Cài đặt.</li><li>Test AppTest với Cloudflare giả: một cú bấm tạo nhiều ảnh, hết lượt giữa chừng, tự chọn không đè lựa chọn tay, «Để trống chỗ này», gửi nháp có ảnh AI (tên file, tiêu đề `[AI]`, không GPS), băm ảnh đã duyệt.</li></ul> | Soi Lỗi; **Lá Chắn đầy đủ** (đường gửi) |
| **F** · README, sổ rủi ro | Thư Ký | Tạo tài khoản, token tối thiểu, `.env`, hạn mức, dữ liệu gửi đi; sổ rủi ro (Cloudflare, Gemini viết prompt, giấy phép FLUX) | Lá Chắn rút gọn |

**Thứ tự gộp:**

1. A, B, C chạy song song (khác file).
2. D sau C (cần lời dặn).
3. E sau A, B, D.
4. F cùng lúc với E.
5. Trước khi bật cho bài thật: **buổi thử thật** (một lần gọi Cloudflare thật, kiểm 2.1 cột phải; tạo ảnh cho một bài nháp thử; xem trên website) và Lá Chắn đọc kết quả.

**Test chung:**

- Không gọi Cloudflare, Gemini thật.
- Ảnh giả tạo trong test.
- Tham số lớn có `ids` ngắn (bài học `os.environ` lộ khi tên ca quá dài).

## 7. Câu hỏi cho chủ dự án

1. **Kiểu ảnh AI: giống ảnh chụp, hay tranh vẽ minh họa?**
   - A (khuyến nghị): giống ảnh chụp, cảnh chung, có chú thích «Ảnh minh họa (AI)» hiện ngay dưới ảnh. Người đọc nhận ra bộ phận, dấu hiệu hư dễ hơn.
   - B: tranh vẽ, đồ họa kỹ thuật. Không ai nhầm là ảnh công trình, nhưng kém sinh động.
2. **Tạo ảnh AI: một cú bấm cho cả bài, hay tự tạo ngay khi viết xong bài?**
   - A (khuyến nghị): một nút «Tạo ảnh minh họa cho các chỗ còn trống». App tự làm hết, chỉ cần bấm một lần; không tốn lượt khi bài còn đang sửa.
   - B: tự tạo ngay sau khi viết xong bài, không bấm gì.
   - Ảnh trong thư mục thì tự chọn luôn như bạn đã chốt.
3. **Ảnh vuông 1024×1024 có được không?**
   - A (khuyến nghị): được. Mô hình rẻ nhất (khoảng 170 ảnh/ngày), Cloudflare tự chạy, gửi lệnh đơn giản.
   - B: cần ảnh ngang. Sau này đổi sang mô hình FLUX.2 klein (khoảng 95 ảnh/ngày), phải làm thêm một phiếu.
4. **Ảnh thật tự chọn: có giới hạn số ảnh mỗi bài không?**
   - A (khuyến nghị): không giới hạn. App chỉ lấy khi khớp rõ (đúng vật), còn lại dùng ảnh AI.
   - B: tối đa 1–2 ảnh thật mỗi bài, còn lại ảnh AI.

## Đối chiếu tiêu chí xong

- [x] Việc 1, tự chọn ảnh thư mục: mục 1 (thuật toán, ngưỡng, không trùng, dữ liệu ảnh đã dùng, không gửi ảnh cho AI).
- [x] Việc 2, ảnh AI qua Cloudflare: mục 2 (đường gọi cố định, chỉ base64, giới hạn cỡ, mở có kiểm, WebP, không EXIF, tên file, «Minh họa», `.env`, token tối thiểu, câu lỗi, đếm và chặn).
- [x] Việc 3, prompt ảnh: mục 3.
- [x] Việc 4, giao diện: mục 4.
- [x] Việc 5, bảo mật: mục 5 (kèm nguồn chính sách dữ liệu).
- [x] Việc 6, chia phiếu, test, thứ tự gộp, câu hỏi: mục 6, 7.
- [x] Không gọi Cloudflare thật, không tạo token, không sửa mã.

## Rủi ro và điểm cần chú ý

- **Tài liệu Cloudflare tự mâu thuẫn ở 3 chỗ:** `seed`, định dạng ảnh (JPEG hay PNG), quyền token. Cỡ ảnh không được ghi.
  - Thiết kế chọn cách an toàn: không gửi `seed`; nhận cả JPEG, PNG; cạnh 256–2048 px; bắt đầu bằng quyền Read.
  - Vẫn phải **gọi thử một lần** trước khi bật.
- **Hạn mức chung cho hai máy:** bộ đếm mỗi máy chỉ thấy phần của mình; lỗi 3036 là chốt cuối.
- **Ảnh AI chỉ nằm trên máy tạo ra** tới lúc gửi nháp. Máy kia mở bài thì phải tạo lại.
- **Tự chọn dựa vào quy ước tên thư mục 3A.** Thư mục đặt tên tự do thì ít ảnh được chọn (an toàn: dùng ảnh AI, không đoán).
- **Mô hình có thể bị Cloudflare ngừng** (như 4 mô hình SD ngừng 20/11/2026). Tên mô hình nằm trong `config/ai.toml` và danh sách cho phép trong mã; đổi mô hình có thể cần phiếu code nếu khuôn lệnh khác.
- **Bộ lọc nội dung của FLUX không được ghi trong tài liệu.** App bắt ảnh trống, còn ảnh «lạ» thì người dùng thấy ở bước duyệt.

## Đề xuất

- **Chỉ Huy:** ghi T-053 «thay bằng T-140»; hỏi chủ dự án 4 câu ở mục 7; đưa thiết kế cho Lá Chắn đọc (như T-094, T-120) trước khi lập phiếu code.
- **Sau đợt này:** đổi sang ảnh ngang (FLUX.2 klein) nếu chủ dự án cần; nhận mặt thẻ trong mô tả bằng AI (hiện chỉ dùng danh sách cố định).

## Câu hỏi cho chủ dự án

Xem mục 7 (4 câu, mỗi câu có khuyến nghị).

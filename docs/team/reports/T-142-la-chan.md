# Biên bản bảo mật T-142 · Client Cloudflare Workers AI, ảnh AI sạch, kho ảnh AI (đợt 1 · A chế độ tự động) · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt 20/11 và kiểm lại sau khi hạn mức mở lại cùng ngày). Chỉ Huy B giao 20/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | T-142 (phiếu A của T-141, đợt 1): Thợ Máy lượt 1 `035c598`, Soi Lỗi `28bb809` (ĐẠT CÓ ĐIỀU KIỆN, 2 Thấp), Thợ Máy lượt 2 `ab6b524` (sửa SL-T142-1, -2) trên nền gộp `84eb41f` (`origin/int/T-137-138` = `main` + T-137 + T-138). Nhánh `team/T-142` head **`ab6b524`**, worktree `wt-T-142`, cây sạch, đã push |
| Phạm vi | **Đầy đủ**, 8 trọng tâm Chỉ Huy giao. Đọc hết `seo_app/ai/cloudflare_images.py` (496 dòng, mới), `seo_app/images/generated.py` (386 dòng, mới), `tests/fake_cloudflare.py` (101), diff `seo_app/ai/registry.py` (+40), `seo_app/config.py` (+10), `seo_app/content/blind_test.py` (1 dòng), `.env.example` (+13); 4 file test T-142 (Thợ Máy 39 + 16 + 36 hàm, Soi Lỗi 18 hàm/94 ca); phần vận chuyển dùng chung trong `seo_app/google/sheets.py` (`_Bearer`, `_refuse_redirect`, `_read_limited`, `_close_and_status`), `process._open`, `_cache_dir_is_ignored`, `_check_webp`, `ImageTags.for_ai_image`. Báo cáo Thợ Máy, Soi Lỗi, phiếu T-142, biên bản thiết kế T-140 (LC-T140-1 → -20) và T-141 (LC-T141-18, -20). **Chỉ đọc; không sửa mã; không gọi Cloudflare thật** (mọi thử trên adapter giả dưới bộ chặn mạng của `conftest`); test chỉ chạy trong `wt-T-142` |
| Ngày | 2026-11-20 (giao buổi sáng tại `ab6b524`; dừng 12:30 vì hết hạn mức, ghi sổ dở `T-142-la-chan-dang-do.md`; tiếp sau khi hạn mức mở lại (Chỉ Huy B nhắn); xong 13:40, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Lô 93 file test liên quan chạy nền trong worktree (không chạy toàn bộ; không chạy trong thư mục app thật) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được** (`main` `ddcd23c`: `git merge-tree` không xung đột; nhánh đã chứa `int/T-137-138`): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. Cả 8 trọng tâm đạt; 13 mục của phiếu có mã và test ghim từng lớp. 2 Thấp của Soi Lỗi đã sửa đúng ở lượt 2, R5 giữ (chỉ gỡ 3 dấu `xfail`). 5 ghi nhận của Soi Lỗi: G-2 (4 header mặc định của `requests`) và lệch thiết kế 2.9 **chấp nhận**; G-3, G-4 thành điều kiện B.3, B.2; G-1, G-5 ghi nhận. **Giữ nguyên điều kiện LC-T140-17**: gọi thử Cloudflare thật một lần cùng chủ dự án trước khi bật cho bài thật (B.1). Thêm B.4: bộ lọc ký tự prompt (LC-T141-18) phải nằm ở T-145 trước khi gọi, vì client chỉ kiểm độ dài |

## Tóm tắt (cho chủ dự án)

Phiếu này làm phần «máy» để app tự tạo ảnh minh họa miễn phí bằng Cloudflare (mô hình FLUX), theo quyết định của anh/chị ngày 18/11. Chưa có nút nào trên màn hình; các phiếu sau mới nối vào. **Gộp được.**

- **App chỉ nói chuyện với đúng một địa chỉ của Cloudflare**, bằng hai lệnh cố định (tạo ảnh, kiểm mã truy cập). Địa chỉ nằm trong mã, không đọc từ file cấu hình; Cloudflare có bảo «đi sang chỗ khác» app cũng không đi; app không tải ảnh theo bất kỳ đường link nào, chỉ nhận ảnh gửi kèm trong câu trả lời, và giới hạn cỡ trước khi mở.
- **Mã truy cập Cloudflare chỉ nằm trong file `.env`**, không in ra màn hình, không ghi log, không lọt vào câu báo lỗi (tôi thử cả trường hợp máy chủ cố ý nhét mã vào lời đáp: câu báo vẫn là câu cố định).
- **Ảnh nhận về được «vẽ lại» từ điểm ảnh** rồi nén WebP: không còn dữ liệu ẩn nào (EXIF, GPS, hồ sơ màu, chú thích). Ảnh lạ (quá to, quá nhỏ, ảnh động, ảnh trống, file hỏng) bị từ chối với câu báo rõ ràng. Ảnh AI do mã gắn nhãn «Minh họa», tên file `minh-hoa-ai-…`, không mang mã công trình hay khu vực của khách.
- **Ảnh lưu trong `data/ai_images` của máy** theo mã băm; app kiểm thư mục không phải lối tắt trước mỗi lần đọc, ghi, xóa; file bị sửa thì không dùng; dọn tự động chỉ xóa đúng file của app.
- **Việc của anh/chị (trước khi bật tạo ảnh thật):** tạo mã truy cập đúng loại theo hướng dẫn trong `.env.example` (mã của chính bạn, một tài khoản, chỉ quyền «Workers AI Read», có ngày hết hạn, giữ gói Free), rồi **gọi thử một lần cùng Chỉ Huy** để chốt 5 điều chưa biết (vị trí ảnh trong câu trả lời, định dạng, cỡ, số neuron thật, quyền Read đủ không). Tôi đọc kết quả rồi mới cho bật cho bài thật.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Đường gọi cố định, 2 đường, không chuyển hướng, không tải URL, chỉ base64, giới hạn cỡ trước giải mã — **đạt**

- `API_HOST = "api.cloudflare.com"`, `API_BASE` ghép từ hằng; hai đường `accounts/{account_id}/ai/run/{model}` và `VERIFY_PATH = "user/tokens/verify"`. `account_id` khớp `^[0-9a-f]{32}$`, `model` phải nằm trong `ALLOWED_MODELS` (1 mục; thêm dấu `/` ở đuôi hay `@cf/x` bị từ chối, thử độc lập). `_call` **kiểm lại tên máy chủ** của URL vừa ghép ngay trước khi gửi (lớp 2), không query, không header ngoài `Content-Type` và `Authorization` (qua `_Bearer`, `repr` là `_Bearer(***)`).
- Không chuyển hướng ba lớp: `allow_redirects=False`, `Session.max_redirects = 0`, móc `_refuse_redirect` (3xx đóng trước khi đọc thân; dùng chung với Sheets, LC-T097-1). Thử độc lập: 302 có `Location` ra máy lạ → câu «chuyển hướng (mã 302); app không đi theo», **đúng 1 lệnh**, không lệnh thứ hai.
- Giới hạn cỡ theo thứ tự đúng: `Content-Length` khai > trần → từ chối trước khi đọc; thân đọc theo luồng (`stream=True`, `_read_limited`) ≤ 16 MiB (lệnh kiểm token ≤ 64 KiB); JSON chặt (`_parse_json`: `NaN`/`Infinity`, trùng khóa, `RecursionError` → `_BAD`; thử độc lập cả ba); `result.image` phải là chuỗi ≤ 12.000.000 ký tự **trước** `b64decode(validate=True)`; byte ≤ 9 MiB; có `url` ở gốc hay trong `result`, hay `image` dạng `data:` → từ chối, không tải gì (thử độc lập: 1 lệnh, `kind=shape`). Giờ chờ 60 s (kẹp trần), `max_retries=0`, không tự thử lại.
- Không AI Gateway: không chuỗi `gateway` nào trong mã; tên máy chủ là hằng.

### 2. Token chỉ ở `.env`, không lộ ở log/giao diện/câu lỗi, `verify_token` chỉ quyền tối thiểu — **đạt**

- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` vào `ENV_VARS`; `Settings` giữ hai trường với `repr=False` (đột biến K01, K02 của Soi Lỗi bị bắt). Token khớp `^[A-Za-z0-9_-]{20,256}$`; sai mẫu (19 ký tự, 257 ký tự, có xuống dòng) hay `account_id` chữ hoa → câu lỗi chỉ nêu **tên biến**, không chép giá trị (thử độc lập).
- Không `import logging`, không `print`, không `streamlit` trong hai module mới. `CloudflareImageClient.__repr__` → `CloudflareImageClient(***)`; `CloudflareImage.__repr__` chỉ model và steps.
- Mọi ngoại lệ của `requests` (chuỗi lỗi chứa URL, tức mã tài khoản) thành câu cố định `from None`; `MSG_NETWORK_OTHER` chỉ mang **tên lớp** ngoại lệ. Thử độc lập 7 câu trả lời lạ (HTML 200 chứa token và mã tài khoản; 401 với `message` chứa token; 3036 trong 200; `code` là chuỗi; …): không câu lỗi, `repr`, hay traceback nào chứa token hay mã tài khoản; `__context__` không nối.
- `verify_token`: `GET user/tokens/verify`, chỉ đọc `result.status` trong `("active","disabled","expired")`; trường khác (kể cả `policies` có chữ lạ) bị bỏ; status lạ → `shape`. Lệnh này chỉ cần token có quyền kiểm chính nó — tối thiểu. Câu báo nói rõ chưa chứng minh quyền Workers AI (phiếu mục 6).

### 3. Ảnh về → dựng lại điểm ảnh → WebP sạch qua `_check_webp`, không EXIF/ICC/XMP; tên `minh-hoa-ai-…`; «Minh họa» do mã gắn — **đạt**

- `make_generated_web_image`: kiểm cạnh/chất lượng trước; `_open(data, formats=("JPEG","PNG","WEBP"))` (dùng lại bộ mở có trần điểm ảnh, HEIC bị loại); ảnh động, cạnh ngoài 256–2048, ảnh gần một màu (`getextrema` chênh ≤ 8) bị từ chối; `convert("RGB")` rồi **`Image.frombytes`** dựng ảnh mới (mất `info`, `exif`, `icc_profile`, `comment`); qua `make_web_image` (không phóng to); cổng cuối `web.gps is None and _check_webp(web.data) is None`, không thì `MSG_NOT_CLEAN`. Byte gốc của Cloudflare không được lưu, không đi đâu.
- Thử độc lập: JPEG có EXIF `ImageDescription`, GPS, ICC, COM → WebP chỉ còn hai khóa mặc định của Pillow (`background`, `loop`), không còn dấu nhận nào trong byte, `gps=None`, sha khớp. PNG 2049 px, 200 px, một màu, GIF, rác → từ chối (câu báo mới, xem trọng tâm 6).
- `wrap_generated`: sha256 + `ImageTags.for_ai_image(category)` (chỉ `source="ai"` và hạng mục khớp danh sách cố định; thử độc lập: `category="cong-sat"` thành «Cổng sắt», không có mã công trình/khu vực/giai đoạn), `TagError` → thẻ rỗng; tên file `generated_file_name(..., ai_generated=True)` → `minh-hoa-ai-…`. Alt/figcaption «Minh họa…» giữ cơ chế T-062/T-083 ở lớp nháp (ngoài phiếu này; ca Soi Lỗi vẫn qua).

### 4. Kho `data/ai_images`: không ghi ra ngoài khi `data/` là liên kết; cách ly test — **đạt** (test cách ly: điều kiện B.2)

- `AIImageStore`: `_no_link` (`dir_has_link(self._dir, PROJECT_ROOT)`) trước **mỗi** `save`, `load`, `cleanup`, `_drop`; `save` còn kiểm `_cache_dir_is_ignored` (`.gitignore` dòng 22 `data/`, không dòng `!`), `mkdir` rồi kiểm liên kết lại, `is_link(path)` trên chính file, `mkstemp` + `os.replace` (nguyên tử), chỉ nhận byte ≤ 2 MiB qua `_check_webp`. `load`: `_valid_sha` tên, `lstat` S_ISREG, cỡ, băm khớp tên, `_check_webp` lại. `cleanup(keep)`: chỉ `^[0-9a-f]{64}\.webp$`, file thường không liên kết, giữ `keep` (nháp + `history`), ngưỡng 14 ngày / 500 file / 500 MB.
- Thử độc lập trên Windows: thư mục kho là **junction** trỏ ra ngoài → `load`, `save` từ chối với câu «Thư mục dữ liệu … là liên kết», `cleanup(keep=[], now=0)` xóa 0, file bên ngoài còn nguyên; file bị nối thêm 1 byte → `MSG_STORE_CHANGED`, câu không chứa đường dẫn; byte không phải WebP → `MSG_STORE_BAD`.
- Cách ly test: `conftest` có autouse `_never_touch_real_caches` (T-138) trỏ `PREVIEW_CACHE_DIR` nhưng **chưa có `AI_IMAGES_DIR`** (G-4 của Soi Lỗi đúng). Test T-142 tự truyền thư mục tạm nên lô 93 file chạy xong worktree **không có `data/`**; nhưng ai gọi `AIImageStore()` mặc định trong test sau này sẽ ghi vào `data/ai_images` thật → **B.2** (T-143 đang thêm).

### 5. `registry.py`: `cloudflare` chỉ ở `IMAGE_ONLY_PROVIDERS`, chỉ cho `[tasks.image]`, `steps` 1–8; lệch thiết kế 2.9 — **đạt, chấp nhận lệch**

- `IMAGE_PROVIDERS = ("gemini","openai","cloudflare")`, `IMAGE_ONLY_PROVIDERS = {"cloudflare": (...)}`; `load_ai_config` từ chối `cloudflare` ở việc khác `image` (câu «chỉ dùng để tạo ảnh»), hãng lạ vẫn bị từ chối; `image_steps` loại `bool`, ngoài 1–8, không phải `int` (ca Thợ Máy 0, 9, −1, `true`, `"4"`, 4.5, `[4]`; đột biến R02, R05 bị bắt). `make_provider("cloudflare")` → `AIError` có chủ đích: ảnh Cloudflare đi qua `cloudflare_images`, không qua lớp provider chat.
- Lệch thiết kế 2.9 (không đưa `cloudflare` vào `PROVIDERS`): **chấp nhận**. Lợi: thử mù, «Kiểm tra khóa», `provider_status` vẫn chỉ 3 hãng viết; trang Soạn bài không đòi khóa Cloudflare (tạo lười như T-062); đột biến R06 («thêm cloudflare vào PROVIDERS») bị ca Soi Lỗi bắt. `provider_label` tra cả hai bảng nên bảng việc–mô hình không `KeyError` (`blind_test.py`, 1 dòng).

### 6. Câu báo ảnh AI hỏng (lượt 2) — **đạt**

- `_ai_image_error` ánh xạ câu của `process._open` sang câu riêng: không phải ảnh/HEIC/HEIF → `MSG_FORMAT`; quá lớn/quá nhiều điểm ảnh → `MSG_TOO_BIG`; lỗi nén → `MSG_ENCODE`; `_MSG_OLD_PILLOW` giữ nguyên; còn lại → `MSG_BROKEN`. Mọi câu đều nói «Ảnh Cloudflare trả về …», không còn gợi ý Google Drive, đổi đuôi, iPhone (thử độc lập 5 ca; ca `PHOTO_HINTS` của Soi Lỗi qua sau khi gỡ `xfail`). Câu không chứa đường dẫn, không chữ của máy chủ.

### 7. 4 header mặc định của `requests`; sổ rủi ro biến proxy — **đạt; proxy thành điều kiện B.3**

- Header thật gửi đi (bắt trên adapter giả): `Accept`, `Accept-Encoding`, `Connection`, `User-Agent` (4 mặc định của `requests.Session`) + `Authorization`, `Content-Type`, `Content-Length`. Thân đúng `{"prompt","steps"}`, không `seed`/`width`/`height`.
- LC-T140-1 «không header ngoài `Content-Type`, `Authorization`» tôi hiểu là **app không thêm** header nào: 4 header kia do thư viện đặt, không lấy từ `config/`/`.env`, giống hệt client Sheets và Search Console (cùng `requests.Session`), và `*_CUSTOM_HEADERS` đã bị chặn từ T-034. `User-Agent: python-requests/x.y` chỉ lộ **phiên bản thư viện** cho Cloudflare, không lộ gì của máy hay người dùng. **Không trái LC-T140-1.** Khuyến nghị K.1: khi gom lớp vận chuyển về một module chung (LC-T140-18 đã dự liệu), đặt `User-Agent` cố định cho cả ba client.
- Sổ rủi ro `security.md` dòng 2026-10-15 và 2026-10-28 (biến `HTTPS_PROXY`, `SSL_CERT_FILE`…) nêu thư viện AI, WordPress, Google — **chưa nêu Cloudflare**, dù client này đi cùng `requests` nên cùng chịu. G-3 của Soi Lỗi đúng → **B.3**: thêm một dòng (mức Thấp, cùng lý do).

### 8. Giữ điều kiện «gọi thử Cloudflare thật một lần cùng chủ dự án trước khi bật» — **giữ** (B.1)

- Chưa có gì chạy thật (phiếu này không nối nút; `app/` chưa dùng client). 5 ẩn số của LC-T140-17 (vị trí/kiểu `result.image`, định dạng và cỡ ảnh thật, số neuron một ảnh, quyền Read đủ không, lệnh kiểm token chạy với loại token đã tạo) chỉ chốt được bằng lần gọi thật. Danh sách kiểm giữ nguyên như T-140 mục 5; ảnh thử không lên website. Lá Chắn đọc kết quả rồi mới cho bật cho bài thật.

## Lỗi phát hiện

Không lỗi mới (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). Điểm duy nhất tôi cân nhắc xếp Thấp rồi **không xếp**: `check_prompt` chỉ kiểm trống và ≤ 2.048 ký tự, còn **nhận** ký tự điều khiển (NUL), ký tự đảo hướng (U+202E) và xuống dòng. Phiếu T-142 mục 2 ghi rõ phần nội dung prompt (trần 900, ký tự, từ cấm) do **T-145** kiểm trước khi gọi theo LC-T141-18, nên client đúng phạm vi phiếu. Tôi đặt **B.4** để T-145 không bỏ sót, kèm khuyến nghị thêm lớp 2 trong client.

## Đánh giá lỗi, ghi nhận của Soi Lỗi; R5

| Mục Soi Lỗi | Mức SL | Đánh giá Lá Chắn |
|---|---|---|
| SL-T142-1: 2 ca chỉ đặt khóa Claude rồi dựng AI từ `config/ai.toml` đã commit, hỏng khi gộp T-138 (Gemini) | Thấp | **Đồng ý mức, đã sửa đúng** (lượt 2: ca dùng khuôn `ai_config_samples`, không phụ thuộc hãng trong file commit). 2 ca `GOP_T138` của Soi Lỗi qua trên nền gộp `84eb41f` |
| SL-T142-2: ảnh Cloudflare hỏng báo câu của ảnh thư mục | Thấp | **Đồng ý mức, đã sửa đúng** (`_ai_image_error`, trọng tâm 6); 4 ca ghim qua |
| G-1: thiếu ca `NaN` ở client (Soi Lỗi bù) | ghi nhận | Mã đã chặn (`parse_constant`), thử độc lập xác nhận; ca bù của Soi Lỗi giữ |
| G-2: 4 header mặc định của `requests` so LC-T140-1 | ghi nhận | **Chấp nhận**, không trái (trọng tâm 7); K.1 |
| G-3: sổ rủi ro proxy thiếu Cloudflare | ghi nhận | **Thành điều kiện B.3** |
| G-4: chưa có autouse fixture cho `AI_IMAGES_DIR` | ghi nhận | **Thành điều kiện B.2** (T-143) |
| G-5: (a) `MAX_IMAGE_BYTES` không bao giờ chặn (12 M ký tự base64 ≤ 9.000.000 byte); (b) cạnh 256–2048 kiểm **sau** khi `_open` giải mã trọn ảnh (tới 80 M điểm ảnh ≈ 240 MB RAM); (c) 60 s là giờ chờ mỗi lần đọc, không cho cả lệnh | ghi nhận | **Đồng ý cả ba, giữ mức ghi nhận.** (a) thừa vô hại (tôi tính lại độc lập, trùng). (b) nguồn là Cloudflare qua TLS, trần điểm ảnh của module vẫn chặn; khuyến nghị K.2 kiểm `image.size` trước `load()` khi dọn. (c) giống mọi client `requests` của app (Sheets, Search Console, WordPress), đã chấp nhận từ T-097; với lượt chạy tự động (T-149) nên có hạn tổng cho cả lệnh ở module vận chuyển chung (K.2) |

**Đột biến của Soi Lỗi** (69 lượt trên bản `035c598`: 62 bắt, 7 sống, lý do từng con đã nêu): các chốt tôi quan tâm nhất đều có ca bắt — không tự thử lại (M32), tên máy chủ (M11, M12), đọc kho không kiểm liên kết (G09, chỉ ca Soi Lỗi bắt), `repr=False` (K01, K02), `cloudflare` vào `PROVIDERS` (R06). 7 con sống Soi Lỗi đã giải thích là đột biến tương đương hoặc ngoài chốt; tôi không thấy con nào mở lối đi thật.

**R5 (lượt 2):** `git diff 28bb809..ab6b524 -- tests/test_soi_loi_t142.py` **chỉ gỡ 3 dấu `xfail(strict=True)`** (SL-T142-2: 4 ca; `GOP_T138`: 2 ca), không đổi thân hay kỳ vọng ca nào; không ca cũ nào khác đổi. Đạt R5. Còn lại docstring đầu file và hằng `GOP_T138` không ai dùng (Thợ Máy đã ghi) — dọn lúc tiện, không điều kiện.

## Thử độc lập (Fable)

Kịch bản `probe_t142.py` (ngoài repo, scratchpad) trên `FakeCloudflare` của `tests/fake_cloudflare.py` gắn vào `requests.Session`, không mạng, không Streamlit; kết quả đã nêu ở từng trọng tâm. Tóm tắt:

| Ca | Kết quả |
|---|---|
| Header, thân, kwargs thật của lệnh tạo ảnh | 7 header (4 mặc định + 3 của app); thân `{"prompt","steps"}`; `stream=True`, `timeout=60.0`; `repr` che token |
| HTML 200 chứa token; 302 ra máy lạ; `image` dạng `data:`; có `url`; 401 `message` chứa token; 3036 trong 200; `code` chuỗi | Mỗi ca 1 lệnh, câu cố định đúng `kind` (`shape`/`auth`/`quota_day`/`rate`), không lộ token hay mã tài khoản ở `str`, `repr`, traceback; không `__context__` |
| `verify_token`: `status=active` kèm `policies` chứa chữ lạ; `status` lạ | Trả `'active'`, chỉ đọc status; lạ → `shape` |
| JPEG bẩn (EXIF + GPS + ICC + COM) → `wrap_generated` | WebP sạch, không dấu nhận, `gps=None`, thẻ AI + hạng mục, sha khớp |
| PNG 2049 px, 200 px, một màu; GIF; rác | Từ chối, câu «Ảnh Cloudflare trả về …» |
| Kho: tên, băm lệch, byte lạ, junction (load/save/cleanup) | Đúng như trọng tâm 4 |
| Bộ kiểm: `steps` bool/0/9/4.0/"4"; `model` lệch; `account_id`/token sai mẫu; `_parse_json` NaN/trùng khóa/lồng 100.000 tầng; `_known_code` | Đúng; `_known_code` lấy `int` đầu trong 20 mã, bỏ `bool` |
| Gọi `generate` trong `threading.Thread` | Xong, có ảnh, `streamlit` không bị nạp |

## Danh sách kiểm tra (13 mục của phiếu T-142)

| # | Mục | Mã | Test ghim |
|---|---|---|---|
| 1 | Đường gọi cố định, 2 đường, `account_id` mẫu, `model` danh sách, không header lạ, không chuyển hướng, 60 s, ≤ 16 MB, TLS mặc định, không Gateway | ✓ (`API_HOST`, `_call` kiểm tên máy chủ, `max_redirects=0`, hook) | ✓ Thợ Máy + Soi Lỗi (đột biến M11, M12) |
| 2 | Thân `{"prompt","steps"}`, `steps` 1–8 loại `bool`, prompt 1–2048 không cắt | ✓ | ✓ |
| 3 | 200 + JSON chặt, `success`, `result.image` ≤ 12 M ký tự, `b64decode(validate=True)`, ≤ 9 MB, từ chối `url`, mã lỗi `int` trong danh sách, câu cố định | ✓ | ✓ (G-1 bù) |
| 4 | `kind` đúng bảng 2.4 trên `CloudflareImageError(AIError)` | ✓ | ✓ |
| 5 | `max_retries=0`, không tự thử lại, ngoại lệ `requests` thành câu cố định, không `logging` | ✓ | ✓ (M32) |
| 6 | `verify_token` chỉ `result.status`, chỉ khi bấm (nút ở T-146) | ✓ | ✓ |
| 7 | Ảnh → `_open` 3 định dạng, cạnh 256–2048, một khung, không một màu, dựng lại điểm ảnh, `make_web_image`, `_check_webp` | ✓ | ✓ |
| 8 | Kho sha256, nguyên tử, `dir_has_link` mọi thao tác, ≤ 2 MB, băm khớp, dọn an toàn | ✓ | ✓ (G09) |
| 9 | Thẻ AI do mã gắn, tên `minh-hoa-ai-…` | ✓ | ✓ |
| 10 | `registry.py`: `cloudflare` chỉ việc `image`, `steps`, tạo lười | ✓ | ✓ (R02, R05, R06) |
| 11 | `config.py`, `.env.example`: biến, `repr=False`, chú thích | ✓ (`.env.example` dòng 75–82, không giá trị) | ✓ (K01, K02) |
| 12 | Không `streamlit`, chạy trong `Thread` | ✓ | ✓ (+ thử độc lập) |
| 13 | Test với Cloudflare giả dưới bộ chặn mạng, đủ ca, `ids=` ngắn | ✓ (`fake_cloudflare.py`; `ids=` 13/11/10 chỗ) | ✓ |

## Kết quả công cụ quét

| Công cụ | Kết quả |
|---|---|
| `uv run ruff check .` | sạch |
| `bandit` (PYTHONUTF8=1) trên 2 module mới | 1 Low **B105 giả** (`cloudflare_images.py:110`: chuỗi câu báo `MSG_BAD_TOKEN`, không phải bí mật) |
| `detect-secrets` (PYTHONUTF8=1) trên diff T-142 và biên bản này | `{}` |
| Ký tự ẩn/điều khiển trong file mới | 0 |
| `grep` `import streamlit|logging|print(` trong 2 module mới | 0 |
| Lô test liên quan, 93 file (4 file T-142, `test_images_process`, `test_images_tags`, T-117 ×2, `test_t138_khong_ghi_data_that`, `test_settings_keys`, `test_t101_settings_google`, `test_soi_loi_t084`, `test_app_pages`, mọi file gọi `load_ai_config`/`ENV_VARS`/`make_web_image`/`_check_webp`/`for_ai_image`/`image_file_name`/`IMAGE_*PROVIDERS`/`cloudflare`), `-p no:randomly`, chạy nền trong `wt-T-142` | 12.181 qua, 0 hỏng, 2 bỏ qua (tạo symlink cần Developer Mode; `os.environb` không có trên Windows), 16 xfail đều có từ trước (LC-T107-3 ×4, R4-3 ×2, SL-T026-3 ×2, SL-T028-1 ×2, SL-T036-10, SL-T067-1 ×4, SL-T107-3), 1 cảnh báo; 1 giờ 16 phút |
| Thư mục `data/` trong worktree sau lô test | không có |
| `git merge-tree` với `main` `ddcd23c` | không xung đột |

## Ghi nhận (không xếp lỗi)

- `MAX_IMAGE_CHARS` × 3/4 = 9.000.000 byte < `MAX_IMAGE_BYTES` 9.437.184: trần byte không bao giờ chạm vì trần ký tự chặt hơn (trùng G-5a của Soi Lỗi). Thừa, vô hại; giữ cả hai cũng được.
- Ảnh tới 80 M điểm ảnh (trần của `process`) vẫn được giải mã trọn rồi mới bị cạnh 256–2048 từ chối (G-5b): một PNG 9 MB nén tốt có thể làm tốn vài trăm MB RAM một lúc. Chỉ xảy ra khi Cloudflare (qua TLS) trả ảnh lạ; không mở lối ra ngoài. K.2.
- Giờ chờ 60 s tính cho mỗi lần đọc (G-5c): máy chủ nhỏ giọt có thể giữ lệnh lâu hơn 60 s (như mọi client `requests` của app). Với lượt chạy tự động, hạn tổng một lệnh nên đặt ở module vận chuyển chung. K.2.
- `_image_bytes` ném `TypeError` nội bộ cho mọi lệch khuôn; `generate` đổi thành `CloudflareImageError(kind="shape")` — đúng, nhưng ai gọi thẳng `_image_bytes` (hàm riêng) sẽ thấy `TypeError`. Không điều kiện.
- `_known_code` chỉ xem 20 mục đầu của `errors`; mã 3036 đứng sau 20 mục rác sẽ thành câu lỗi chung theo mã HTTP (429 → `rate`). Chấp nhận: hướng an toàn, chỉ kém chính xác câu báo.
- `FakeCloudflare` không nhận `allow_redirects` (Session không chuyển kwarg này cho adapter) — nên lớp chặn chuyển hướng được chứng minh bằng ca 302, không bằng kwarg. Thợ Máy có ca ghim `max_redirects` và hook.
- Thiết kế 2.9 lệch (trọng tâm 5): chấp nhận, ghi ở đây để T-140 không bị coi là chưa làm.
- Docstring và hằng `GOP_T138` sót trong `test_soi_loi_t142.py` (Thợ Máy đã ghi).
- Phiếu này chưa nối vào `app/`; `grep` cho thấy chỉ `registry.py` nhắc tới `cloudflare_images`. Các điều kiện E/F của T-140 (hiển thị, README, sổ rủi ro) thuộc phiếu sau.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

| Mã | Điều kiện | Ở đâu |
|---|---|---|
| **B.1** | **Gọi thử Cloudflare thật một lần cùng chủ dự án trước khi bật cho bài thật** (LC-T140-17, giữ nguyên danh sách kiểm T-140 mục 5; prompt trung tính; không cố tạo 3036; ảnh thử không lên website). Lá Chắn đọc kết quả rồi mới cho bật | Trước khi bật (sau khi nối nút) |
| **B.2** | `tests/conftest.py`: fixture autouse trỏ `seo_app.images.generated.AI_IMAGES_DIR` (cùng chỗ với `PREVIEW_CACHE_DIR`) sang thư mục tạm, kèm một ca ghim «kho mặc định trong test không nằm trong thư mục dự án» (G-4) | T-143 (đang làm) hoặc phiếu đầu tiên đụng `conftest` |
| **B.3** | `docs/team/security.md` sổ rủi ro: thêm một dòng cho client Cloudflare (biến proxy, chứng chỉ của máy — cùng `requests`, cùng mức Thấp, cùng lý do dòng 15/10 và 28/10) (G-3) | Thư Ký, phiếu F của T-140 (README/sổ rủi ro) |
| **B.4** | Bộ lọc prompt cuối theo LC-T141-18/LC-T140-9 (một dòng; chỉ ký tự in được, không điều khiển/vô hình/đảo hướng; không chữ số; không link, email, số điện thoại; không «Pro-Metal», tên miền, quận huyện; danh sách từ cấm) phải chạy **trước** `CloudflareImageClient.generate`, sai thì không gửi. Khuyến nghị thêm lớp 2 vào `check_prompt` («một dòng, chỉ ký tự in được»); nếu sửa `cloudflare_images.py` thì chạy lại 4 file test T-142 | T-145 |
| K.1 (khuyến nghị) | Khi gom lớp vận chuyển (`_Bearer`, `_refuse_redirect`, `_read_limited`, `_close_and_status`) về một module chung cho Sheets, Search Console, Cloudflare: đặt `User-Agent` cố định, chạy test cả ba client (LC-T140-18) | Phiếu dọn sau đợt 1 |
| K.2 (khuyến nghị) | Cùng phiếu dọn: hạn tổng cho cả lệnh (không chỉ mỗi lần đọc) ở module vận chuyển chung; `make_generated_web_image` kiểm `image.size` trước `load()` để ảnh quá cạnh bị từ chối trước khi giải mã trọn (G-5b, G-5c) | Phiếu dọn sau đợt 1, trước khi bật lượt chạy tự động |

Xong: 13:40 (giờ máy). Commit chỉ biên bản này trên `team/T-142`.

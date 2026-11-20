# Báo cáo T-142 · Client Cloudflare Workers AI, ảnh AI sạch, kho ảnh AI · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-142](../tickets/T-142-client-cloudflare-anh-ai-sach.md) · báo cáo Thợ Máy [`T-142-tho-may.md`](T-142-tho-may.md) · điều kiện Lá Chắn T-140 (LC-T140-1 → -8, -13, -17, -18), T-141 (LC-T141-9, -12) |
| Nhánh | `team/T-142` đầu `035c598` (gốc `main` `ddcd23c`). Mọi lần chạy trên đúng mã này (worktree `wt-T-142`, hay bản sao `git archive 035c598` trong thư mục nháp của phiên) |
| Ngày nộp | 2026-11-20 (giao 2026-11-19 13:38; máy tắt giữa chừng, chạy tiếp 2026-11-20 09:09; xong 10:28, +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: chuyển Lá Chắn (đầy đủ) được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp**: SL-T142-1 (2 ca test hỏng khi gộp với T-138), SL-T142-2 (câu báo sai ngữ cảnh khi ảnh Cloudflare hỏng). Cả 6 trọng tâm Chỉ Huy giao: **đúng**. 69 đột biến các chốt chính: 62 bị bắt; 7 sống gồm 1 lỗ test (đã bù, nay bắt), 5 lớp kiểm chồng nhau, 1 lần kiểm chỉ có ích khi bị chen ngang đúng lúc. Test của Soi Lỗi: 94 ca (88 qua, 6 xfail strict ghim 2 lỗi). 96 file của mọi nơi gọi `registry.py`, `config.py`, kho ảnh, lớp ảnh, ba test trang: 12.127 qua, 0 hỏng, móc kiểm 0 lần đụng `data/`. 5 ghi nhận, không chặn |

## Tóm tắt (cho chủ dự án)

- **Bộ phận gọi Cloudflare tạo ảnh minh họa làm đúng thiết kế.** Tôi thử trên Cloudflare giả:
  - chỉ gọi đúng một địa chỉ của Cloudflare, không đi theo lời chuyển hướng;
  - không bao giờ tải ảnh theo đường link;
  - câu trả lời lạ (hỏng, quá lớn, sai dạng) đều thành câu báo tiếng Việt cố định;
  - mỗi lần lỗi chỉ gọi một lần (không tự gọi lại, không tốn thêm lượt miễn phí).
- **Mã truy cập Cloudflare không lộ:** tôi cho «máy chủ» cố ý trả lại mã truy cập, mã tài khoản trong câu lỗi, ở 9 mã lỗi khác nhau. Câu báo, dấu vết lỗi và mọi trang của app đều không có hai mã đó.
- **Ảnh nhận về luôn sạch:** ảnh cố ý nhét dữ liệu lạ (vị trí GPS, ghi chú ẩn, hồ sơ màu, dữ liệu dính sau cuối file) ra WebP sạch hoàn toàn. Ảnh có tên `minh-hoa-ai-…`, alt bắt đầu «Minh họa», chú thích «Ảnh minh họa (AI)».
- **Kho ảnh AI trên máy:** thư mục `data` là lối tắt thì app không đọc, không ghi, không xóa gì ở nơi khác. Kiểm thử không ghi vào `data` của phần mềm (theo dõi từng lần ghi: 0 lần).
- **Còn 2 chỗ nhỏ cần sửa:**
  1. Khi gộp cùng phiếu T-138 (tạm dùng Gemini), 2 ca kiểm thử của phiếu này hỏng (lỗi ở bài kiểm thử, không ở phần mềm).
  2. Ảnh Cloudflare trả về bị hỏng thì app báo câu dành cho ảnh trong thư mục, ví dụ «Google Drive chưa đồng bộ?», dễ làm anh/chị đi kiểm nhầm chỗ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t142.py` | Mới: 94 ca. 88 qua; 6 `xfail(strict=True)` ghim SL-T142-1, -2 (mục 7) |
| `docs/team/reports/T-142-soi-loi.md` | Báo cáo này |

Không sửa mã, test của Thợ Máy; không commit file phiếu.

## 1. Trọng tâm 1 — client: đường gọi, chuyển hướng, chỉ base64, giới hạn cỡ, câu trả lời lạ

- **Đường gọi:** chỉ `https://api.cloudflare.com/client/v4/` cộng hai đường `accounts/<mã>/ai/run/@cf/black-forest-labs/flux-1-schnell` và `user/tokens/verify`. Mã tài khoản đúng 32 hex thường, mô hình trong danh sách cho phép, tên máy kiểm lại ngay trước khi gửi (`cloudflare_images.py:447-450`).
- **Không theo chuyển hướng:** `allow_redirects=False`, phiên `max_redirects = 0`, móc `_refuse_redirect` (3xx đóng ngay, không đọc thân).
- **Không tải theo địa chỉ:** câu trả lời có `url` (trong `result` hay ngoài cùng), hay `image` là đường link, đều bị từ chối; Cloudflare giả có sẵn ảnh ở địa chỉ đó mà không lệnh GET nào được gửi.
- **Giới hạn cỡ trước khi giải mã:** thân trả lời đọc theo luồng ≤ 16 MB (đếm sau giải nén); chuỗi base64 ≤ 12.000.000 ký tự kiểm **trước** `b64decode(validate=True)`; lệnh kiểm token ≤ 64 KB (ca Soi Lỗi, chỉ ca này bắt đột biến M30).
- **Câu trả lời lạ** đều thành `CloudflareImageError` câu cố định, có `kind`, không lọt traceback:
  - JSON hỏng, mảng, khóa trùng, lồng sâu 100.000 tầng, không phải UTF-8;
  - `success` không đúng `true`, thiếu `result`, ảnh rỗng, base64 lẻ, có dấu cách;
  - `NaN`, `Infinity`, `-Infinity` trong câu trả lời đúng khuôn (ca Soi Lỗi, bù lỗ G-1);
  - 3xx có và không có `Location`; 200 mà `Content-Type` không phải JSON.
- **Ảnh hỏng sau khi giải base64** (ca Soi Lỗi, đi trọn client → `wrap_generated`):
  - PNG giả (chữ ký PNG + rác), GIF, HEIC, chữ SVG: bị từ chối, câu cố định, không traceback, không đường dẫn;
  - PNG khai 30.000 × 30.000 hay 9.000 × 9.000 điểm ảnh: từ chối nhanh theo trần 80 triệu điểm ảnh;
  - câu báo của các ca này còn sai ngữ cảnh: SL-T142-2.
- **Loại lỗi** (`kind`, bảng 2.4 của thiết kế T-141) đúng: 3036 → `quota_day`; 3040, 5xx → `busy`; 429 → `rate`; 401, 403, 3023 → `auth`; 408, hết giờ → `timeout`; lỗi mạng → `network`; 4xx khác, mã đã biết → `bad_request`; còn lại → `shape`.
- **Không tự thử lại:** đúng **một** lệnh cho mỗi lần lỗi, thử 8 kiểu (503, 429, 3040, 3036, 408, hết giờ, mất mạng, ảnh sai) (ca Soi Lỗi; đột biến M32 «tự thử lại một lần khi busy/rate» bị 12 ca bắt, ca cũ của Thợ Máy chỉ thử 503).

## 2. Trọng tâm 2 — ảnh ra WebP sạch, tên, thẻ, alt «Minh họa»

- **Ảnh bẩn đi trọn đường** (client giả → `wrap_generated`), mỗi ảnh mang một dấu nhận riêng ở mọi chỗ chứa siêu dữ liệu:
  - **JPEG:** EXIF (có GPS, mô tả), ICC, COM, APP1 XMP, APP13 Photoshop, dữ liệu dính sau EOI;
  - **PNG:** `tEXt`, `zTXt`, `iTXt` XMP, `eXIf`, `iCCP`, khối riêng `prVt`, dữ liệu dính sau IEND;
  - **WebP:** EXIF, XMP, ICCP, khối lạ `ZZZZ`, dữ liệu dính sau RIFF.

  Kết quả ở cả ba: WebP ra không còn dấu nhận, `_check_webp` không báo, `info` không có `exif`/`icc_profile`/`xmp`, `gps is None`.
- **Lớp kiểm cuối** (`web.gps`, `_check_webp`, `generated.py:148`) tự bắt WebP bẩn khi lớp trước hỏng (ca Soi Lỗi giả `make_web_image` trả WebP còn GPS, hay còn khối EXIF mà báo `gps=None`). Trước ca này, bỏ lớp kiểm cuối (G06, G06b) không ca nào hỏng.
- **Thẻ, tên, alt:** `wrap_generated` gắn `ImageTags.for_ai_image`; hạng mục có mã công trình hay khu vực («CT012 - Cổng inox - Tân Phú») bị bỏ cả, không giữ chữ. Tên `minh-hoa-ai-….webp`. Qua lớp alt sẵn có (`clean_suggestion(ai_generated=tags.is_ai)`): alt bắt đầu «Minh họa», chú thích «Ảnh minh họa (AI)».
- **Chạy từ luồng nền:** nạp `cloudflare_images`, `generated` không kéo theo `streamlit` (đã kiểm `sys.modules`, cả các module nạp gián tiếp).

## 3. Trọng tâm 3 — token chỉ trong `.env`, không lộ ra log, giao diện, câu lỗi

- **Máy chủ trả lại mã truy cập, mã tài khoản** trong `errors[].message`, `messages`, `result`, hay trang HTML: thử 9 mã HTTP (200, 400, 401, 403, 404, 408, 429, 500, 503) × 3 kiểu thân × 2 lệnh (tạo ảnh, kiểm token). Hai mã không có trong `str`, `repr`, `args` và **dấu vết lỗi đầy đủ** (`traceback.format_exception`) của lỗi; mỗi lần đúng một lệnh.
- **Lỗi của `requests` chứa URL và token** (9 loại: mất mạng, hết giờ, SSL, khúc hỏng, giải nén hỏng, URL sai, lỗi chung, `OSError`, `ValueError`): câu cố định; dấu vết lỗi không có URL. Đột biến M28 (nối lỗi gốc bằng `from exc` thay `from None`) qua được ca của Thợ Máy (chỉ xem `__suppress_context__`), chỉ ca của Soi Lỗi bắt.
- **Dựng client với giá trị sai dạng** (mã tài khoản chữ hoa, token có dấu cách và đường link): câu cố định, không chép giá trị.
- **Mọi trang của app** (6 trang, mở với `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` giả và `[tasks.image]` dùng Cloudflare): không chuỗi nào của trang, kể cả nhãn, giá trị ô nhập, mọi tab, có hai mã đó.
- **Không `logging`** ở hai module mới; `Settings` giữ hai giá trị với `repr=False` (đột biến K01, K02 bị bắt).

## 4. Trọng tâm 4 — kho `data/ai_images`: cách ly trong test, không ghi ra ngoài khi `data/` là liên kết

- **Lối tắt ở tầng `data/ai_images`** (không chỉ `data/`, như ca của Thợ Máy): lưu, đọc báo `MSG_DATA_DIR_LINK`; dọn trả 0. Một file đúng tên, cũ 30 ngày, nằm ở thư mục đích **ngoài** kho thì vẫn còn nguyên.
  - Ca này bắt được đột biến G09 (đọc không kiểm lối tắt). Ca của Thợ Máy để thư mục ngoài trống nên đột biến đó qua.
  - Ca này cũng bắt được G19 + G20: bỏ cùng lúc kiểm lối tắt của kho và của từng lần xóa, thì file ở ngoài bị xóa.
- **Một «file» trong kho là lối tắt** (junction tên `<băm>.webp` trỏ ra ngoài): đọc, lưu bị từ chối; dọn (ép trần 0 file) không xóa gì ở thư mục đích.
- **Cách ly trong test:**
  - Mọi ca của T-142 tự truyền thư mục tạm.
  - Ca «thư mục git sẽ commit» không tạo thư mục nào.
  - Chạy 3 file test của Thợ Máy với móc kiểm `audit_data` (`sys.addaudithook`, ghi mọi lần mở, tạo, đổi tên, xóa trong `data/`): 200 qua, **0 lần** đụng `data/` của worktree, không có thư mục `data/` sau lượt.
  - Lô 96 file (mọi nơi gọi, ba test trang, test T-142 và của Soi Lỗi) chạy trong worktree với cùng móc kiểm: **0 lần** đụng `data/`, không có thư mục `data/` sau lượt, `git status` chỉ có 2 file mới của Soi Lỗi.
- **Còn để ngỏ:** chưa có fixture tự chạy trỏ `AI_IMAGES_DIR` sang thư mục tạm (G-4).

## 5. Trọng tâm 5 — `registry.py`: Cloudflare chỉ cho `[tasks.image]`, `steps` 1–8, không vào `PROVIDERS`

- `provider = "cloudflare"` (cả viết hoa «CloudFlare») ở **mọi** việc khác `image` (research, outline, write, rewrite, review, meta, links, plan, alt, một việc mới): `load_ai_config` báo «… chỉ dùng để tạo ảnh».
- `steps` của `[tasks.image]`: 0, 9, −1, `true`, `false`, `"4"`, 4.5, `[4]` bị từ chối lúc đọc (ca của Thợ Máy); đột biến R02, R05 bị bắt.
- `make_provider` với mọi hãng (cả `cloudflare`), không khóa: luôn `AIError`, không bao giờ `KeyError`.
- **Thử mù:** đủ khóa 3 hãng cộng khóa Cloudflare, `[tasks.image]` dùng Cloudflare. Ô chọn hãng của ứng viên chỉ có 3 hãng viết bài; `provider_status` 3 dòng. Đột biến R06 (thêm `cloudflare` vào `PROVIDERS`) bị bắt.
- **Tab Kết nối:** hiện chưa có mục Cloudflare (T-146 làm); mã Cloudflare không hiện ở bất kỳ trang nào (mục 3).
- **Chỗ có thể xung đột khi gộp:**
  - `team/T-143`, `team/T-148` vẫn ở `ddcd23c` (chưa đẩy gì): gộp thử không xung đột, không file chung.
  - Lúc T-148 đẩy, chỗ chồng là 2 dòng đầu `make_provider` (Thợ Máy đã báo) và lớp lỗi `kind`.
  - Gộp với `team/T-138` (`f2014f4`, Lá Chắn đã cho gộp): không xung đột chữ, nhưng 2 ca test hỏng: SL-T142-1.

## 6. Trọng tâm 6 — đột biến các chốt chính

**Cách thử.**
- Bản sao `git archive 035c598` trong thư mục nháp, script `mutate142.py`.
- Mỗi đột biến sửa một chỗ, chạy file test của Thợ Máy cùng file của Soi Lỗi.
- Bản gốc chạy trước: 285 qua, 6 xfail.
- Chỉ «failed» tính là bắt; đếm riêng ca hỏng của Thợ Máy (TM) và của Soi Lỗi (SL).
- Máy tắt sau khi chạy xong cả 69 lượt. Đã kiểm `tar --compare` với `git archive`: bản sao không file nào khác nội dung.

| Nhóm | Đột biến | Bắt | Sống |
|---|---|---|---|
| Client (`cloudflare_images.py`) | 34 | 32 | M15, M33 |
| Ảnh sạch, kho (`generated.py`) | 26 | 21 | G08b, G18, G19, G20, G23 |
| `registry.py`, `config.py` | 9 | 9 | — |
| **Cộng** | **69** | **62** | **7** |

- **Chỉ ca Soi Lỗi bắt (5):**
  - M28: nối lỗi gốc có URL vào dấu vết lỗi;
  - M30: kiểm token đọc tới 16 MB;
  - G06, G06b: bỏ, hay làm yếu lớp kiểm cuối;
  - G09: đọc kho không kiểm lối tắt.
- **Cả hai cùng bắt (11):** M11, M12, M27, M31, M32, G05, G08, G22, R01, R03, R06.
- **Chỉ ca Thợ Máy bắt:** 46.
- **7 đột biến sống:**
  - **M15** (bộ đọc nhận `NaN`/`Infinity`): lỗ thật của test. Ca «nan» của Thợ Máy đặt `NaN` vào `success` nên bị chặn ở bước sau. Ca bù của Soi Lỗi (G-1) bắt được: 3 ca hỏng khi chạy lại M15.
  - **M33** (lớp chặn 3xx thứ hai): tương đương, móc `_refuse_redirect` vẫn chặn mọi 3xx trước.
  - **G08b** (kiểm lối tắt lần hai, sau khi tạo thư mục): chỉ có ích khi bị chen ngang đúng lúc, không dựng được bằng test. G08 (bỏ cả hai lần) bị bắt.
  - **G18, G19, G20, G23** (các lớp kiểm lối tắt, file thường khi dọn và khi lưu): chồng nhau, bỏ một lớp thì lớp kia chặn.
    - Bỏ cùng lúc G19 + G20 thì ca Soi Lỗi bắt (file ở ngoài bị xóa).
    - Bỏ cùng lúc G18 và kiểm lối tắt của `_drop` thì không ca nào hỏng: xóa một lối tắt chỉ xóa chính nó, không xóa thư mục đích (Windows còn từ chối xóa junction bằng `unlink`).

## 7. Lỗi mới

| # | Mức | Mô tả | Vị trí | Đề xuất sửa | Test ghim |
|---|---|---|---|---|---|
| SL-T142-1 | Thấp | 2 ca test chỉ đặt khóa **Claude** rồi dựng AI từ bản sao `config/ai.toml` đã commit (lúc làm phiếu: Claude). Gộp với `team/T-138` (mọi việc dùng Gemini, Lá Chắn đã cho gộp): không xung đột chữ nhưng hai ca hỏng («Chưa có khóa Google Gemini», nút «Phân tích từ khóa» bị khóa). Đã gộp thử thật (`git merge-tree`, cây `f1131d9`, T-138 `f2014f4`): 2 hỏng, 26 qua trong file đó. Phần mềm không sai, chỉ test | `tests/test_t142_config_registry.py:114` (`test_router_never_asks_for_cloudflare_when_writing`), `:174` (`test_write_page_does_not_ask_for_cloudflare_key`), hàm mẫu `_real_with_cloudflare` `:43` | `_real_with_cloudflare` tự đổi các việc viết sang Claude (như `ai_text_on("anthropic")` của T-138), hay đặt khóa đúng các hãng đang cấu hình (`set_configured_keys`, có sau khi gộp T-138). Ai gộp sau thì sửa | `test_ca_router_t142_van_qua_khi_cau_hinh_la_gemini`, `test_ca_trang_t142_van_qua_khi_cau_hinh_la_gemini` (giả cấu hình đã commit là Gemini rồi chạy lại đúng hai ca đó) |
| SL-T142-2 | Thấp | Ảnh Cloudflare trả về hỏng hay không đúng dạng thì `make_generated_web_image` để nguyên câu báo của `process._open`, viết cho ảnh trong thư mục: «Ảnh bị hỏng hoặc chưa tải xong (**Google Drive chưa đồng bộ?**)…», «File này không phải ảnh JPEG, PNG hoặc WebP… (**có thể bị đổi đuôi**…)», «Tạm chưa nhận **ảnh HEIC của iPhone**…», «… **Hãy thu nhỏ ảnh trước.**». Ở lượt chạy tự động (T-149), câu này sẽ hiện ở bước duyệt, làm chủ dự án đi kiểm nhầm chỗ. Module đã có câu riêng `MSG_BROKEN` («Ảnh Cloudflare trả về bị hỏng…») nhưng chỉ dùng khi `convert`, lưu PNG hỏng | `seo_app/images/generated.py:120` (`_open(data, formats=GENERATED_FORMATS)` không bọc) | Bắt `ImageProcessError` của `_open` và đổi thành câu của ảnh AI (ví dụ `MSG_BROKEN`; riêng quá nhiều điểm ảnh có thể dùng `MSG_SIZE`). Không đổi `process._open` (ảnh thật vẫn cần câu cũ) | `test_anh_cloudflare_hong_bao_cau_cua_anh_ai[hong, gif, heic, 81-trieu]` |

Sáu ca ghim đã chạy `--runxfail`: hỏng đúng lý do (câu «Google Drive», «đổi đuôi», «iPhone», «thu nhỏ ảnh»; «Chưa có khóa Google Gemini», nút bị khóa).

## 8. Ghi nhận (không chặn)

- **G-1 (lỗ test, đã bù):** `test_odd_json_is_refused[nan]` không thử được bộ đọc từ chối `NaN`/`Infinity` (LC-T140-4): `NaN` nằm ở `success`, bị chặn ở bước kiểm `success is True`. Bỏ `parse_constant` (M15) không ca nào hỏng. Ca `test_bo_doc_json_tu_choi_nan_ca_khi_phan_con_lai_dung_khuon` để câu trả lời đúng khuôn, chỉ thêm một trường `NaN`/`Infinity`/`-Infinity`.
- **G-2 (header):** ngoài `Content-Type`, `Authorization`, lệnh gửi đi còn 4 header mặc định của `requests`: `User-Agent: python-requests/2.34.2`, `Accept`, `Accept-Encoding: gzip, deflate`, `Connection` (cùng `Content-Length`). Client Search Console, Sheets cũng vậy. LC-T140-1 ghi «không header ngoài `Content-Type`, `Authorization`»: không header nào lấy từ cấu hình hay biến môi trường, nhưng nếu hiểu theo chữ thì cần `session.headers.clear()`. Lá Chắn quyết.
- **G-3 (biến môi trường của máy):** phiên `requests` đọc biến proxy, chứng chỉ (`HTTPS_PROXY`, `REQUESTS_CA_BUNDLE`…), như client WordPress, Google. Sổ rủi ro (dòng 15/10, 28/10) nêu thư viện AI, WordPress, Google, **chưa nêu Cloudflare**. Đề xuất ghi thêm Cloudflare vào dòng đó.
- **G-4 (cách ly kho ảnh AI cho phiếu sau):** test T-142 tự truyền thư mục tạm, đúng phiếu (không được sửa `conftest.py`). Nhưng chưa có fixture tự chạy trỏ `generated.AI_IMAGES_DIR` (`generated.py:59`) sang thư mục tạm. Ca canh «mọi `DEFAULT_…_FILE` của `seo_app/storage` trỏ ra ngoài dự án» của T-138 cũng không thấy hằng này (khác module, khác kiểu tên). T-149, T-146 dùng kho mặc định sẽ ghi `data/ai_images` của thư mục chạy test (như G-5 của T-137). Đề xuất: T-143 (đang sửa `conftest.py`) hay phiếu sau thêm fixture, mở rộng ca canh của T-138 sang `seo_app/images` (cả `PREVIEW_CACHE_DIR`).
- **G-5 (giới hạn):**
  - `MAX_IMAGE_BYTES` (9 MiB = 9.437.184 byte) không bao giờ chặn được: 12.000.000 ký tự base64 giải ra tối đa 9.000.000 byte. Vô hại, vì trần ký tự đã chặn trước; test chỉ thử được bằng cách hạ hằng.
  - Cạnh 256–2048 điểm ảnh kiểm **sau** khi `_open` giải mã cả ảnh. Ảnh tới 80 triệu điểm ảnh vẫn được giải mã trọn (khoảng 240 MB RAM) rồi mới bị từ chối; có thể kiểm `image.size` trước `load()`. Nguồn là Cloudflare qua TLS nên khó khai thác.
  - Giờ chờ 60 giây là cho mỗi lần đọc, không cho cả lệnh (như mọi client `requests` của app).

Chỗ lệch thiết kế mà Thợ Máy đã ghi (Cloudflare không vào `PROVIDERS`; `IMAGE_PROVIDERS` giữ Gemini, OpenAI; kiểm mã tài khoản lúc tạo client, không lúc đọc `.env`): tôi kiểm lại, không thấy hệ quả xấu. Kiểm lúc tạo client nghĩa là mã sai dạng không làm hỏng các trang khác, và câu báo không chép giá trị.

## 9. Test của Soi Lỗi (`tests/test_soi_loi_t142.py`, 94 ca)

| Nhóm | Ca | Kết quả |
|---|---|---|
| Mã truy cập không lọt | `test_loi_may_chu_co_ma_truy_cap_khong_lot_ra` (9 mã HTTP × 3 kiểu thân, mỗi ca thử cả tạo ảnh lẫn kiểm token), `test_loi_requests_khong_de_url_trong_dau_vet_loi` (9 loại lỗi), `test_loi_dung_client_khong_chep_gia_tri` | 37 qua |
| Không tự thử lại, giới hạn | `test_moi_lan_loi_chi_mot_lenh_toi_cloudflare` (8 kiểu), `test_bo_doc_json_tu_choi_nan_ca_khi_phan_con_lai_dung_khuon` (3), `test_kiem_token_doc_than_tra_loi_co_gioi_han` | 12 qua |
| Ảnh sạch | `test_anh_ban_qua_ca_duong_ra_webp_khong_con_dau_nhan` (JPEG, PNG, WebP), `test_lop_kiem_cuoi_bat_webp_ban` (2), `test_anh_ai_luon_minh_hoa_ten_minh_hoa_ai_khong_the_cong_trinh` | 6 qua |
| Kho | `test_tang_ai_images_la_loi_tat_khong_doc_ghi_xoa`, `test_file_trong_kho_la_loi_tat_khong_bi_theo` | 2 qua |
| Registry, trang | `test_cloudflare_chi_dung_cho_viec_anh` (10 việc × 2 cách viết), `test_make_provider_khong_bao_gio_keyerror` (4), `test_khong_trang_nao_hien_ma_cloudflare` (6 trang), `test_thu_mu_khong_co_cloudflare` | 31 qua |
| Lỗi chưa sửa | SL-T142-1 (2 ca), SL-T142-2 (4 ca) | 6 xfail strict |

## 10. Lệnh đã chạy

```text
# Windows 11, Python 3.12.15, venv của wt-T-142. Không gọi Cloudflare, AI, Google, WordPress thật
# (Cloudflare giả gắn vào phiên requests, bộ chặn mạng của conftest bật).

# 3 file test của Thợ Máy, kèm móc kiểm data/ (worktree)
uv run pytest tests/test_t142_cloudflare_client.py tests/test_t142_generated_images.py \
    tests/test_t142_config_registry.py -p audit_data -p no:randomly
  → 200 passed in 42.11s; audit: hits=0; không có data/

# File của Soi Lỗi (worktree)
uv run pytest tests/test_soi_loi_t142.py -p no:randomly          → 88 passed, 6 xfailed
uv run pytest … --runxfail -k "hong_bao or van_qua"               → 6 failed (đúng lý do)

# Gộp thử với T-138 (git merge-tree, cây f1131d9 = T-138 f2014f4 + T-142 035c598), bản sao nháp
uv run pytest tests/test_t142_*.py → 2 failed, 198 passed (SL-T142-1)
# Gộp thử với T-143, T-148 (cả hai còn ở ddcd23c): không xung đột, không file chung

# Đột biến (mutate142.py, bản sao 035c598): gốc 285 passed, 6 xfailed; 69 lượt: 62 bắt, 7 sống
# Đột biến ghép (combo.py): G19+G20 → bắt (ca Soi Lỗi); G18 + bỏ is_link của _drop → sống
# (tương đương); M15 với ca bù → 3 failed (bắt)
# tar --compare với git archive 035c598 sau khi máy tắt: không file nào khác nội dung

# Lô mọi nơi gọi: 96 file trong worktree — mọi file test nhắc load_ai_config, AIRouter,
# make_provider, PROVIDERS, IMAGE_*, ENV_VARS, load_settings, Settings(, blind_test, .env.example,
# _check_webp, cloudflare, generated; cộng test_t101_settings_google, test_settings_images, file
# của Soi Lỗi (có test_app_pages, test_soi_loi_t084, test_images_process, mọi test_t142_*)
uv run pytest <96 file> -p audit_data -p no:randomly -p no:cacheprovider
  → 12127 passed, 25 skipped, 13 xfailed, 1 warning in 4223.24s (1:10:23)
#   13 xfailed: 6 ca ghim của Soi Lỗi, 7 xfail có từ trước. 1 warning: Pydantic, ca T-028 cố ý
#   đưa luồng trả lời hỏng (có từ trước).
  → audit-callers.log: hits=0; sau lượt: không có data/

uv run ruff check .                                   → All checks passed!
uv run ruff format --check tests/test_soi_loi_t142.py → already formatted
PYTHONUTF8=1 uvx detect-secrets scan --all-files .   # bản sao 2 file của Soi Lỗi + file mồi tiếng Việt
  → chỉ file mồi bị báo (bắt được); 2 file của Soi Lỗi: 0
# Ký tự ẩn (Cf), CR, NFC trong 2 file của Soi Lỗi: 0, 0, NFC
```

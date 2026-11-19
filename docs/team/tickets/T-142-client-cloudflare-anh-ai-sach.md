# T-142 · Client Cloudflare Workers AI, ảnh AI sạch, kho ảnh AI (phiếu A)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không. **Đợt 1**, song song T-143, T-148 và T-144 → T-153 (khác file, mục Phạm vi). Làm từ `main` mới nhất |
| Trạng thái | Mới |

## Mục tiêu

App gọi được Cloudflare Workers AI (mô hình FLUX.1 [schnell]) để tạo **một** ảnh minh họa từ một prompt tiếng Anh, nhận ảnh base64, dựng lại thành WebP sạch (không siêu dữ liệu) và lưu vào kho ảnh AI trên máy. Phiếu này chưa nối vào lượt chạy (T-149) hay giao diện (T-146, T-150), chưa bật cho bài thật.

## Bối cảnh

- Thiết kế T-140 (`docs/team/reports/T-140-tho-may.md`): mục 2.1–2.9 (đường gọi, thân lệnh, câu trả lời, `.env`, ảnh trả về, kho ảnh AI, đếm lượt, cấu hình), mục 5 (bảo mật), mục 6 phiếu A.
- Thiết kế T-141 (`docs/team/reports/T-141-tho-may.md`): 1.7 (ảnh trong luồng tự động), 1.9, 2.4 (loại lỗi), 7.1 dòng A.
- Biên bản Lá Chắn T-140 (`T-140-la-chan.md`, `fb9d2ef`): mục 1 (đối chiếu tài liệu Cloudflare), mục 3 (LC-T140-1 → -20). Biên bản Lá Chắn T-141 (`T-141-la-chan.md`, `03568dc`): mục 8 dòng A.
- Tài liệu (đọc 18/11): `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell`; thân chỉ `prompt` (1–2048 ký tự) và `steps` (≤ 8, mặc định 4); trả `result.image` base64; mã lỗi 3036 (hết hạn mức ngày, 429), 3040 (quá tải, 429), 3023 (403); 5007 là HTTP 400.

## Yêu cầu

1. **Client `seo_app/ai/cloudflare_images.py` (mới), đường gọi cố định:**
   - chỉ máy chủ `api.cloudflare.com`, hai đường: `accounts/{account_id}/ai/run/{model}` và `user/tokens/verify`;
   - `account_id` khớp `^[0-9a-f]{32}$` lúc đọc `.env`, sai thì câu lỗi không chép giá trị;
   - `model` lấy từ danh sách cho phép trong mã (đợt này một mục); chữ trong `config/ai.toml` chỉ để chọn, không vào URL;
   - không query, không header ngoài `Content-Type` và `Authorization` (qua `_Bearer`, `repr` che token);
   - không theo chuyển hướng (`allow_redirects=False`, `max_redirects = 0`, `_refuse_redirect`); giờ chờ ≤ 60 giây; đọc thân trả lời theo luồng ≤ 16 MB (`_read_limited`); TLS mặc định;
   - không bao giờ đi qua AI Gateway.
2. **Thân lệnh:** đúng hai trường `{"prompt", "steps"}`, không `seed`, `width`, `height`, `num_steps`. `steps` đọc bằng bộ kiểm như `_positive_int` (loại `bool`), 1–8. Prompt cuối 1–2048 ký tự; dài hơn thì báo lỗi, không cắt. (Trần 900 ký tự của prompt chi tiết do T-145 kiểm trước khi gọi, LC-T141-18.)
3. **Câu trả lời:**
   - chỉ nhận HTTP 200 + JSON, đọc bằng bộ đọc chặt như client Search Console (từ chối `NaN`/`Infinity`, khóa trùng, bắt `RecursionError`; `Content-Type` JSON);
   - `success is True`, `result` là object, `result.image` là chuỗi ≤ 12.000.000 ký tự; `base64.b64decode(validate=True)`; byte ≤ 9 MB;
   - có trường `url`, hay `image` không phải base64: từ chối, không tải gì theo địa chỉ;
   - `errors[].code` chỉ đọc khi là `int` trong danh sách đã biết (3003, 3023, 3036, 3040, 3042, 5004, 5007, 5028); `message`, `messages` không bao giờ lên trang; câu báo tiếng Việt cố định theo bảng 2.4 của thiết kế T-140 (5007 là HTTP 400).
4. **Loại lỗi cho lượt chạy** (T-141 2.4): lỗi mang `kind` đúng tên của bảng 2.4 (`busy`, `rate`, `quota_day`, `network`, `timeout`, `auth`, `bad_request`, `shape`): 3036 → `quota_day`; 3040, 5xx → `busy`; 401, 403, 3023 → `auth`; lỗi mạng → `network`; quá giờ → `timeout`. Đặt `kind` trên lớp lỗi riêng của client (lớp con của `AIError`) vì `AIError.kind` chung do T-148 thêm cùng đợt; hai bên dùng cùng tên thuộc tính `kind`.
5. **Không tự thử lại** lệnh tạo ảnh (`HTTPAdapter` giữ `max_retries=0`); mọi thử lại do lượt chạy (T-149) quyết. Mọi ngoại lệ của `requests` và lỗi lạ thành câu tiếng Việt cố định (chuỗi lỗi của `requests` chứa URL, tức mã tài khoản). Không `logging` yêu cầu hay câu trả lời.
6. **Kiểm tra kết nối:** hàm kiểm token `GET /user/tokens/verify`, chỉ đọc `result.status` (`active`, `disabled`, `expired`); chỉ chạy khi người dùng bấm (nút ở T-146); câu báo nói rõ chưa chứng minh quyền Workers AI. Lệnh này chỉ đúng với token của người dùng (My Profile → API Tokens).
7. **Ảnh về → WebP sạch, `seo_app/images/generated.py` (mới):**
   - mở bằng `process._open` với `formats=("JPEG", "PNG", "WEBP")`, cạnh 256–2048 px, giới hạn điểm ảnh của module, một khung; từ chối ảnh gần một màu;
   - dựng lại từ điểm ảnh (ảnh mới, bỏ `info`, không `exif`, `icc_profile`, `pnginfo`, `comment`); qua `make_web_image` (không phóng to); byte ra qua `_check_webp`;
   - chỉ byte WebP đã kiểm được lưu, hiện, gửi; byte gốc của Cloudflare không lưu, không gửi đi.
8. **Kho `data/ai_images/`** (trong `generated.py`):
   - tên file là SHA-256 của byte WebP, mẫu `^[0-9a-f]{64}\.webp$`; ghi nguyên tử; `dir_has_link` trước mỗi lần đọc, ghi, xóa; mỗi file ≤ 2 MB;
   - đọc lại phải khớp băm với tên file (và với nháp), rồi `_check_webp` lại;
   - dọn chỉ xóa tên đúng mẫu trong đúng thư mục, giữ file còn được nháp nhắc tới (kể cả `history`); ngưỡng 14 ngày / 500 file / 500 MB.
9. **Ảnh AI do mã gắn nhãn:** lúc bọc ảnh nhận về: `ImageTags.for_ai_image(category)` với `category` từ danh sách cố định; tên file `image_file_name(..., ai_generated=True)` (`minh-hoa-ai-…`); không mã công trình, khu vực, giai đoạn.
10. **`registry.py`:** thêm hãng `cloudflare`, chỉ cho việc `image` (`IMAGE_PROVIDERS`); đọc `steps` của `[tasks.image]` (1–8, loại `bool`); provider tạo lười như T-062: thiếu khóa Cloudflare chỉ báo khi gọi việc ảnh, trang Soạn bài không đòi khóa Cloudflare.
11. **`config.py`, `.env.example`:** `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` vào `ENV_VARS`; `Settings` giữ token với `repr=False`; `.env.example` có chú thích tiếng Việt (token người dùng, phạm vi một tài khoản, chỉ quyền Workers AI Read, có ngày hết hạn, chỉ hiện một lần).
12. **Gọi được từ luồng nền:** module không import `streamlit`; chạy được trong `threading.Thread` thường; client tạo cho từng lượt, không giữ trong `st.session_state`.
13. **Test** với Cloudflare giả: adapter `requests` gắn vào phiên (như `FakeWordPress`), dưới bộ chặn mạng của `conftest`:
    - mọi mã lỗi; thân sai khuôn; `url` thay base64; chuỗi quá dài; byte quá lớn; chuyển hướng; `account_id` sai dạng; token không lộ trong `repr`, câu lỗi;
    - ảnh bẩn (EXIF + GPS + XMP + ICC + COM + `tEXt`, cả JPEG, PNG, WebP) → WebP sạch; ảnh động, ảnh 4096 px, ảnh đen → bị từ chối;
    - kho: tên sai mẫu, file bị sửa (băm lệch), `data/` là liên kết, dọn giữ file còn được nhắc;
    - test ghim **từng lớp được nối** (như LC-T120-18), không chỉ «có nhập».

## Phạm vi

- **Được sửa:** `seo_app/ai/cloudflare_images.py` (mới), `seo_app/images/generated.py` (mới), `seo_app/ai/registry.py`, `seo_app/config.py`, `.env.example`, `seo_app/images/process.py` (chỉ khi cần tách hàm dựng lại điểm ảnh dùng chung; không đổi hành vi hiện có), test mới `tests/test_t142_*.py`.
- **Không được sửa:** `seo_app/ai/base.py` và các provider Gemini, OpenAI, Anthropic (T-148 làm cùng đợt: thêm `AIError.kind`, thêm mẫu `cfut_` vào hàm che bí mật trong câu lỗi); `tests/conftest.py` (T-143 sửa trong đợt 1; test của phiếu này tự truyền thư mục tạm); `seo_app/storage/**`; `app/**`; `config/**` (Ngòi Bút).
- **Ngoài phạm vi:** nối vào lượt chạy (T-149), giao diện (T-146, T-150), khuôn nháp 4 (T-145), lần gọi thử thật (buổi thử cùng chủ dự án).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

S1, S2, S3, A2 (ảnh trả về), F1 (file trong `data/`), D1 (không thư viện mới: `requests` đã có), D3.

- **LC-T140-1** (đường gọi cố định), **-2** (token, mã tài khoản: chỉ `.env`, `repr=False`, lỗi `requests` thành câu cố định, không `logging`; mẫu `cfut_` do T-148 thêm), **-3** (thân lệnh hai trường, `steps` 1–8, prompt dài thì báo lỗi, không cắt), **-4** (câu trả lời: bộ đọc chặt, chỉ base64, mã lỗi đã biết, `message` không lên trang), **-5** (ảnh về → WebP sạch qua `_check_webp`), **-6** (kho `data/ai_images/`), **-7** (không tự thử lại, `max_retries=0`), **-8** (kiểm token chỉ khi bấm, chỉ đọc `result.status`), **-13** (ảnh AI do mã gắn nhãn), **-17** (lần gọi thử thật trước khi bật: ở buổi thử, không ở phiếu), **-18** (test với Cloudflare giả đủ ca; nếu chuyển lớp vận chuyển sang module chung `seo_app/http_guard.py` thì chạy test của **cả ba** client Sheets, Search Console, Cloudflare).
- **LC-T141-9** (gọi được từ luồng nền, không `st.*`, không giữ client), **LC-T141-12** (lỗi trả `kind` cho lượt chạy; client không tự thử lại).

## Tiêu chí xong

- [ ] Yêu cầu 1–13, có test.
- [ ] Test liên quan + test mọi nơi gọi `registry.py`, `config.py` (cấu hình AI, `ENV_VARS`, `.env.example`, trang dùng `load_settings`) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-142-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (đủ ca lỗi, ảnh bẩn, kho ảnh AI).
- Lá Chắn: **đầy đủ** (LC-T141-24).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-142`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO` (app thật chạy từ đó; test có thể ghi `data/`).
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`. Toàn bộ test do Chỉ Huy chạy khi gộp.
- Tham số test lớn kèm `ids=` ngắn (tên ca dài trên Windows làm lộ biến môi trường).
- Test không gọi AI, Cloudflare, Google, WordPress thật. Lần gọi thử Cloudflare thật chỉ ở buổi thử cùng chủ dự án (LC-T140-17, LC-T141-23).
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, bản sao ngoài git có file mồi) sạch trước khi nộp.
- Đổi kỳ vọng test cũ: theo R5 (bảng cũ / mới / vì sao trong báo cáo, Chỉ Huy duyệt).

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu A, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-142`, nhánh `team/T-142`.

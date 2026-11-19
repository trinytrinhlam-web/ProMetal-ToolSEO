# Báo cáo T-141 · Thiết kế chế độ tự động: từ khóa hay kế hoạch → bài hoàn chỉnh → duyệt một lần ở bước Xuất bản

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-141](../tickets/T-141-thiet-ke-che-do-tu-dong.md) |
| Nhánh | `team/T-141` (từ `main` `bbe916b`, đã gộp `team/T-140`: thiết kế `523a959`, biên bản Lá Chắn `fb9d2ef`) |
| Ngày nộp | 2026-11-19 (+07:00, giờ theo lệnh `date`, ghi ở commit) |
| Kết quả | Hoàn thành (thiết kế, không sửa mã) |

## Tóm tắt (cho chủ dự án)

**Cách dùng mới**

- **Soạn theo từ khóa:** gõ từ khóa (thêm ghi chú của thợ nếu có), bấm «🤖 Soạn tự động». App tự làm hết: phân tích từ khóa, dàn ý, viết bài, tự rà soát và sửa câu, SEO, chọn ảnh trong thư mục hay tạo ảnh AI, viết alt, chú thích. Xong thì bài dừng ở **bước 5 · Xuất bản**.
- **Theo kế hoạch:** trang Kế hoạch có nút «🤖 Viết các bài tới hạn». App lấy tối đa 5 dòng có Ngày dự kiến trong 7 ngày tới, viết lần lượt từng bài. Bài xong vào danh sách **«Chờ duyệt»** ở trang Bài viết.
- Mỗi bài mất khoảng **3–6 phút**; 5 bài khoảng 15–30 phút (ước tính, đo lại ở buổi thử). Trong lúc chạy bạn vẫn dùng app được; trang hiện bước đang làm, có nút «Dừng».

**Duyệt một lần ở bước cuối**

- Màn hình cuối hiện đủ: cả bài, từng ảnh (kèm alt, chú thích), SEO, link, cảnh báo. Mỗi phần có nút **«Sửa»** đưa bạn về đúng bước; sửa xong bấm «↩ Về bước duyệt».
- **Chỗ tô vàng là chỗ nên xem:** thiếu chất liệu thật (AI đã viết chung, không bịa số), câu AI chưa tự sửa được, ảnh thật app tự chọn (xem có nhà khách, biển số không), ảnh AI.
- Thay cho tick duyệt từng ảnh: **một ô tick** «Tôi đã đọc bài và xem từng ảnh ở trên». Chưa tick thì chưa gửi được. Sửa gì sau khi tick thì phải tick lại.
- **Không gì lên website khi bạn chưa bấm** Gửi nháp / Hẹn giờ / Đăng ngay. Màn hình xác nhận, khóa chống gửi trùng giữ nguyên. Ngày giờ hẹn điền sẵn theo dòng kế hoạch.
- Lưu ý: nút Hẹn giờ, Đăng ngay vẫn tắt cho tới khi xong buổi thử thật (đang dừng ở Ca 3). Tới lúc đó bài tự động gửi lên dạng Nháp.

**Hạn mức AI miễn phí**

- Mỗi bài cần khoảng **8 lần gọi Gemini**; 5 bài khoảng 40 lần. Ảnh AI khoảng 4 ảnh mỗi bài; hạn mức miễn phí của Cloudflare đủ cho khoảng 40 bài mỗi ngày.
- Google **không công bố** hạn mức gói miễn phí của Gemini Flash (tài liệu đọc 19/11 chỉ bảo xem trong AI Studio). Hạn mức ngày đặt lại lúc khoảng **15 giờ chiều** giờ Việt Nam.
- Hết lượt giữa chừng: app dừng, giữ nguyên các bài đã xong và chỗ đang dở; bạn bấm «▶ Chạy tiếp» sau giờ đặt lại. App không tự chạy lại.
- **Giữ cửa sổ đen của app mở** trong lúc chạy. Đóng tab trình duyệt: app vẫn chạy tiếp. Tắt app: lượt chạy dừng; mở lại bấm «Chạy tiếp».

**Có 6 câu hỏi cho bạn** ở mục 8. Câu nào cũng có khuyến nghị sẵn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-141-tho-may.md` | Báo cáo này (mới) |

- Không sửa mã, cấu hình, test. Không gọi AI, Google, WordPress, Cloudflare thật.
- Tài liệu Google đọc ngày 2026-11-19 qua một agent đọc trang (mục 0).

## 0. Nguồn đã đọc

**Trong dự án:**

- Phiếu T-141; `CLAUDE.md` (quyết định 18/11, 19/11; Quy trình nội dung).
- Thiết kế T-140 (`523a959`) và biên bản Lá Chắn T-140 (`fb9d2ef`, LC-T140-1 → -20).
- Nhánh `team/T-137` (biên bản Lá Chắn `e27d1df`), `team/T-138` (báo cáo Thợ Máy `d82ad6d`, `config/ai.toml`: mọi việc Gemini `gemini-3.8-flash`, nghiên cứu tắt tìm web).
- Biên bản Lá Chắn T-050, T-056, T-086, T-089, T-094 (LC-T094-21, -29, -35, -38, -41), T-103, T-120 (LC-T120-24); `docs/team/security.md` dòng 2026-11-18 (Gemini miễn phí, kể cả viết alt).
- Mã:
  - `app/views/write.py`: 5 bước, `init_state`, `snapshot`/`open_draft`, `autosave`, `start_from_plan`/`fill_from_plan`/`plan_details`, `image_slot`, `alt_editor`, `slot_problem`, `web_info`, bước SEO, `publish_panel`, `confirm_box`, `send_draft`, `send_and_record`.
  - `app/views/plan.py` (`start_writing`, `write_picker`), `app/views/home.py` (khung «Đang viết» còn là bản demo).
  - `seo_app/content/workflow.py` (`ContentWriter`, `write_and_review`), `prompts.py`, `models.py`, `rules.py` (`MISSING_PATTERN`).
  - `seo_app/ai/gemini_provider.py` (thử lại `HttpRetryOptions(attempts=3)`, giờ chờ 15 phút, câu lỗi 429/5xx).
  - `seo_app/storage/drafts.py` (`MAX_DRAFTS = 30`, `save`, `SendState`, `find_plan_draft`), `seo_app/plan/model.py` (cột Sheet, trạng thái), `seo_app/plan/sync.py` (`open_row`, `status_write`, `write_status`, `record_status`), `seo_app/publish/render.py` (link bắt buộc).

**Tài liệu Google** (đọc 2026-11-19; ba trang `ai.google.dev/gemini-api/docs/…` chuyển sang `aistudio.google.com/docs/…`; không trang nào ghi ngày cập nhật):

| Trang | Điều dùng trong thiết kế |
|---|---|
| `…/docs/rate-limits` | Không ghi số lần/phút, lần/ngày của các mô hình Flash ở gói miễn phí: «View your active rate limits in AI Studio». Hạn mức **tính theo project, không theo khóa**. Số lần/ngày **đặt lại lúc nửa đêm giờ Thái Bình Dương** |
| `…/docs/troubleshooting` | Gặp 429 `RESOURCE_EXHAUSTED` hay 503 `UNAVAILABLE`: thử lại lùi dần (exponential backoff) có ngẫu nhiên, chỉ với lỗi tạm thời, có trần số lần |
| `…/docs/pricing` | Gói miễn phí: «Content used to improve our products»; tìm Google (grounding) của Gemini 3.x Flash: không có ở gói miễn phí. Trang dài, agent đọc trọn phần đầu, phần sau là bản tóm tắt |

## 1. Luồng tự động một bài (Việc 1)

### 1.1. Hai cửa vào

| Cửa | Bấm ở đâu | Đầu vào |
|---|---|---|
| Từ khóa | Soạn bài, bước 1: «🤖 Soạn tự động» (cũng có ở popover «✍️ Viết bài mới» trang Bài viết) | Từ khóa; 3 ô chất liệu thật (không bắt buộc) |
| Kế hoạch | «🤖 Viết các bài tới hạn» (mục 4) | Dòng kế hoạch đọc lại từ Sheet: từ khóa, «Ghi chú của thợ» (đã che số điện thoại, email) vào ô «Kinh nghiệm của xưởng», slug, trang dịch vụ đích, loại bài, ngày giờ dự kiến |

- Hồ sơ doanh nghiệp luôn nằm trong lời dặn hệ thống, như hiện nay.
- Nút cũ «🔎 Phân tích từ khóa» (làm từng bước) vẫn còn.
- Bài đang soạn dở cũng bấm «Soạn tự động» được: app chỉ làm phần còn thiếu.

### 1.2. Thứ tự bước

```
bấm «Soạn tự động» (hay lô bài tới hạn)          lưu nháp sau MỖI bước
  ① Nghiên cứu (AI)
  ② Dàn ý (AI) → mã kiểm thay người duyệt
  ③ Viết (AI, lời dặn chế độ tự động)
  ④ Rà soát (AI) → mã tự áp câu sửa đạt chốt → chấm lại (AI)
  ⑤ SEO: meta (AI) + mã chọn bản đạt; slug, từ khóa chính, FAQ (mã); liên kết nội bộ (AI) + mã kiểm
  ⑥ Ảnh: tự chọn thư mục (mã) → chữ ảnh cho cả bài (AI, một lần) → tạo ảnh AI (Cloudflare)
  ⑦ Xong: nháp ở bước 5 · Xuất bản, trạng thái «Chờ duyệt»
```

| Bước | Ai làm | Việc trong `config/ai.toml` | Lưu vào nháp | Không làm được thì |
|---|---|---|---|---|
| ① Nghiên cứu | AI | `research` (không tìm web, T-138) | `research` | Dừng bài |
| ② Dàn ý | AI + mã kiểm (1.3) | `outline` | `outline_title`, `outline` | AI làm lại 1 lần; vẫn hỏng thì dừng bài |
| ③ Viết | AI | `write` | `parts` (bản 1), `gaps` (1.4) | Dừng bài |
| ④ Rà soát, tự sửa | AI ×2 + mã (1.5) | `review` | `parts` (bản 2 nếu có sửa), `review`, `auto_fixed` | Lần chấm lại lỗi: giữ bài đã sửa, dấu vàng «chưa chấm lại» |
| ⑤ SEO | AI + mã (1.6) | `meta`, `links` | `seo` | Ô hỏng để trống, dấu vàng; bài vẫn xong |
| ⑥ Ảnh | mã + AI + Cloudflare (1.7) | `image_prompt` (việc mới của T-140 D) | `chosen_image` từng chỗ | Chỗ không có ảnh để trống, dấu vàng |
| ⑦ Xong | mã | — | `step = 4`, trạng thái «Chờ duyệt» | — |

Bài chỉ coi là «dừng» khi hỏng ở ①–③ (chưa có bài). Hỏng ở ④–⑥ thì bài vẫn tới bước cuối, phần thiếu thành dấu vàng.

### 1.3. Dàn ý tự duyệt: mã kiểm thay người duyệt

Quyết định 19/11 bỏ bước người dùng duyệt dàn ý (Quy trình nội dung bước 4). Mã kiểm dàn ý trước khi viết:

- 3–8 mục; mục nào cũng có tiêu đề (≤ 120 ký tự) và ít nhất một ý; tiêu đề mục không trùng nhau.
- Tối đa 8 chỗ cần ảnh mỗi bài (LC-T140-7); mô tả ảnh ≤ 300 ký tự, dài hơn thì bỏ chỗ ảnh đó (dấu vàng).
- Tiêu đề H1 có từ khóa chính (so không dấu), 20–90 ký tự. Không đạt: AI làm lại 1 lần; vẫn không đạt thì dùng tiêu đề AI kèm dấu vàng.
- Ý có số điện thoại, email (`personal_info`) thì che (`mask_personal_info`), dấu vàng.

Ngòi Bút sửa chữ lời dặn (phiếu C, mục 7):

- Lời dặn dàn ý: ảnh tả vật, tình trạng cần thấy, không gắn công trình hay khách cụ thể (T-140 mục 3.4); bỏ câu «ưu tiên ảnh thật của xưởng».
- Lời dặn viết: «Dàn ý đã được người dùng duyệt» đổi thành «Dàn ý do app tự lập; người dùng duyệt cả bài ở bước cuối».

### 1.4. Chất liệu thật và chỗ thiếu (quyết định 4)

- **Nguồn:** «Ghi chú của thợ» của dòng kế hoạch (qua `fill_from_plan`: che số điện thoại, email theo LC-T094-21; ghi chú có giá thì nhắc theo Lá Chắn T-103 đk 2b) và hồ sơ doanh nghiệp. Cửa từ khóa: các ô chất liệu thật bạn gõ (nếu có).
- **Lời dặn viết ở chế độ tự động** (Ngòi Bút):
  - không bịa số liệu, giá, tên khách (như hiện nay);
  - chỗ cần chất liệu thật mà chưa có thì **viết chung** (không số, không tên), **không** chèn «[cần bổ sung: …]» vào bài;
  - liệt kê các chỗ đó vào trường riêng `gaps`.
- **Khuôn `Draft` thêm `gaps`:** mỗi mục gồm số phần, câu viết chung (chép nguyên văn), cần bổ sung gì (≤ 200 ký tự). Mã kiểm như `clean_flags`: câu phải có thật trong phần đó, không thì bỏ; tối đa 10 mục; chữ qua `clean_ai_text`.
- **AI vẫn lỡ viết «[cần bổ sung: …]»:** mã giữ nguyên chữ, tô đỏ như bây giờ (`MISSING_PATTERN`). Bộ dựng bài **chặn Hẹn giờ, Đăng ngay** khi còn chữ này (nó sẽ hiện nguyên văn trên website); Nháp chỉ cảnh báo. Hiện bộ dựng chưa chặn: thêm ở phiếu H.
- **Bước cuối:** câu viết chung tô vàng, kèm «Nên bổ sung: …» và nút «Sửa» (sang bước 3, mở ô sửa của phần đó).

### 1.5. Rà soát và tự sửa: luật nào tự áp, luật nào chỉ cảnh báo

Giữ đúng một lượt tự sửa như `write_and_review` hiện nay (viết → rà soát → áp câu sửa → chấm lại), để không sửa vòng quanh, không tốn lượt. Thêm **chốt mã** trước khi tự áp một câu sửa.

| Góp ý | Tự áp? | Điều kiện, cách hiện |
|---|---|---|
| AI có câu thay thế | **Tự áp** khi qua cả 5 chốt | (1) câu gốc có thật trong phần đó (`clean_flags`); (2) câu thay không dài quá 2 lần câu gốc; (3) **không thêm chữ số mới** (mọi dãy số trong câu thay phải có trong câu gốc); (4) không thêm giá, link, email, số điện thoại (`mentions_price`, `has_link`, `personal_info`); (5) không có cụm từ cấm (`find_banned`) |
| AI có câu thay nhưng trượt chốt | Không | Dấu vàng «Câu cần xem lại», kèm gợi ý, nút Áp dụng / Bỏ qua như bây giờ |
| AI đề nghị bỏ câu (câu thay rỗng) | Không | Dấu vàng: tự bỏ câu dễ làm gãy ý |
| Cụm sáo rỗng mã tìm thấy (`banned_flags`) | Không | Dấu vàng (không có câu thay) |
| Điểm văn phong dưới 80 | — | Dấu vàng ở bảng kiểm (như bây giờ) |
| Chữ «[cần bổ sung: …]» | — | Đỏ; chặn Hẹn giờ, Đăng ngay (1.4) |

`apply_flag` vẫn lọc thẻ, link trên kết quả ghép (như hiện nay).

### 1.6. SEO tự điền

- **Meta:** một lần gọi `meta` (cả tiêu đề và mô tả). Mã đã lọc sẵn (`filter_ai_titles`, `filter_ai_descriptions`). Chọn bản đầu tiên không bị «Chặn» ở `siteseo_copy` và không trùng hệt bài đã đăng (`check_*_duplicates`, theo danh sách bài **đã lưu trên máy**). Các bản đạt khác giữ làm bản 2, 3 (nút ↶ ↷). Mọi gợi ý đều hỏng: gọi lại 1 lần; vẫn hỏng thì ô trống, dấu vàng.
- **Slug:** dòng kế hoạch có slug thì dùng (`make_slug(given=…)`), không thì `make_slug(từ khóa)`. Trùng bài đã đăng: dấu vàng, sửa ở bước SEO.
- **Từ khóa chính:** chính từ khóa, kiểm như `keyword_problem`.
- **Liên kết nội bộ:**
  - Chỉ khi máy đã có danh sách bài đã đăng (`site_store().load`). **Không gọi website** trong lượt chạy (LC-T094-35). Chưa có danh sách: bỏ bước này, dấu vàng «bấm Tải lại danh sách bài ở bước SEO».
  - `select_candidates` theo loại bài, trang dịch vụ đích của dòng kế hoạch, rồi `internal_links`; mọi gợi ý đạt `check_suggestions` được dùng (`use=True`).
  - Thiếu link bắt buộc tới trang dịch vụ đích (`missing_required`): gọi lại 1 lần. Vẫn thiếu thì bộ dựng chặn như hiện nay, bước cuối hiện đỏ kèm «Sửa» sang bước SEO.
- **Schema FAQ:** mã dựng (`build_article_faq`). Hợp lệ thì tick sẵn «Dùng schema» (chỉ ghi nhớ trong nháp, chưa gửi lên website, như T-132).
- **«Ghi SEO lên website»:** câu hỏi 4.

### 1.7. Ảnh (gộp với T-140)

**Thứ tự:**

1. **Tự chọn ảnh thư mục** cho mọi chỗ cần ảnh (T-140 mục 1, phiếu B): chỉ đọc tên thư mục, tên file; không mở file; không gọi mạng.
2. **Chữ ảnh cho cả bài, một lần gọi AI** (`image_prompt`):
   - chỗ dùng ảnh AI: `prompt_en`, `alt_vi`;
   - chỗ đã có ảnh thật: `alt_vi` và chú thích, viết từ mô tả chỗ cần ảnh, tiêu đề mục, mặt thẻ (giá trị trong danh sách cố định). **Không gửi ảnh** (câu hỏi 1).
3. **Tạo ảnh AI qua Cloudflare** lần lượt; tối đa 8 ảnh mỗi bài; kiểm trần neuron trước từng ảnh (LC-T140-7).
4. **Mã bọc ảnh AI:** `ImageTags.for_ai_image`, tên `minh-hoa-ai-…`, alt «Minh họa…», chú thích «Ảnh minh họa (AI)…» (LC-T140-13).

**Khác thiết kế T-140:**

- T-140 mục 3.2 viết prompt mỗi chỗ một lần gọi. Ở đây gộp **mọi chỗ của bài vào một lần gọi**, đỡ lượt Gemini.
  - Khuôn mới: `ImageTexts(items=[ImageText(slot, prompt_en, alt_vi, caption_vi)])`.
  - Mã kiểm từng mục: số chỗ đúng và không trùng; prompt qua bộ kiểm LC-T140-9; alt qua `clean_alt_text`; chú thích ≤ 200 ký tự.
  - Mục hỏng thì chỉ chỗ đó trống (dấu vàng «chưa viết được prompt»), không làm hỏng cả bài.
- Alt ảnh thật mặc định viết từ chữ (câu hỏi 1 = A), dấu vàng «AI chưa nhìn ảnh: xem alt có đúng ảnh không». Nút «✨ AI xem ảnh, viết lại alt» giữ nguyên, theo từng lần bấm (Lá Chắn T-050 đk 3a không đổi).

**Giữ của T-140:**

- Ảnh tự chọn không bao giờ tự «Đã duyệt» khi chạy (LC-T140-12 a); duyệt ở ô chung bước cuối (mục 3.5).
- Mỗi chỗ tạo ảnh một lần mỗi lượt chạy. «Chạy tiếp» không làm lại chỗ đã có ảnh (tự chọn, đã tạo, bạn chọn, «Để trống chỗ này»): đúng nhánh B của LC-T140-14.
- Lỗi Cloudflare (3036, 401, 403, 5xx, mạng): dừng tạo ảnh của bài đó (LC-T140-7). Bài vẫn xong phần còn lại; chỗ chưa có ảnh: dấu vàng, bấm tạo ảnh sau ở bước 3.

### 1.8. Lưu nháp sau từng bước

**Khuôn nháp 4** (gộp với khuôn 4 của T-140 phiếu D, nâng khuôn **một lần**) thêm `DraftSnapshot.auto` (trống với bài soạn tay):

| Trường | Ý nghĩa |
|---|---|
| `origin` | `"keyword"` hay `"plan"` |
| `done` | Các bước đã xong (tên bước cố định) |
| `stop` | Mã lý do dừng cố định (`busy`, `rate`, `quota_day`, `network`, `auth`, `shape`, `refusal`, `token_limit`, `user`, `conflict`, `app_closed`…). Không chữ tự do: trang đổi mã thành câu tiếng Việt cố định |
| `attempts` | Số lần thử lại (0–20) |
| `images_made` | Số ảnh AI đã tạo trong lượt (0–8, C9) |
| `notes` | Mã dấu vàng cố định (ghi chú đã che, ghi chú có giá, chưa có danh sách bài…) |
| `gaps` | Chỗ thiếu chất liệu thật (1.4) |
| `started_at`, `updated_at` | Có múi giờ |

**Ghi:**

- Sau mỗi bước, lượt chạy ghi bằng `DraftStore.save` có **so rồi đặt theo giờ lưu** (`expected_saved_at`, tham số mới).
  - Tab khác hay bạn vừa sửa chính nháp đó: lượt chạy dừng (`conflict`), không ghi đè.
  - Tự lưu của trang cũng dùng cách này (mục 2.5).
- F5, mất mạng giữa chừng: nháp có đủ tới bước vừa xong; mở lại thấy «Dừng ở bước …», bấm «Chạy tiếp».
- Không đụng phần mở kho, trạng thái gửi, khối SEO của `drafts.py` (T-130, T-136, LC-T140-20), trừ tham số so giờ lưu của `save`.

### 1.9. Đặt mã ở đâu

- **Gói mới `seo_app/auto/`:**
  - `steps.py`: mỗi bước là hàm thuần trên `DraftSnapshot`, không Streamlit;
  - `runner.py`: luồng nền, sổ việc đang chạy, dừng, chạy tiếp, thử lại;
  - `compose.py`: đổi kết quả AI sang đúng dạng ô sửa mà trang đang dùng (như `set_outline`, `set_article`), chọn meta;
  - `plan_start.py`: phần thuần của `start_from_plan`, `fill_from_plan`, `plan_details` (nay nằm trong `write.py`, gắn với `st.session_state`). Trang và lượt chạy dùng chung; trang chỉ còn gán vào phiên;
  - `batch.py`: bài tới hạn (mục 4).
- **`ContentWriter`:** `write(…, auto=True)` (lời dặn tự động, khuôn có `gaps`), `image_texts(…)`, chốt tự áp `auto_fixable(flag, part)`.
- **Test bắt buộc:**
  - nháp do lượt chạy tạo, mở bằng trang (AppTest), ra đúng như soạn tay: dàn ý chưa escape, chữ bài đã escape, ảnh, SEO;
  - hàm trong `seo_app/auto/` không gọi `st.*` (test quét mã);
  - cả lượt chạy với AI giả, Cloudflare giả: **0 request tới WordPress**.

## 2. Chạy lâu trong Streamlit (Việc 2)

### 2.1. Luồng nền chỉ sống khi app sống

- **Một luồng làm việc cho cả app** (`ThreadPoolExecutor(max_workers=1)`, giữ bằng `st.cache_resource` như `_scan_pool`). Bài chạy lần lượt; bấm thêm thì xếp hàng («thứ 2 trong hàng»).
- **Luồng không gọi `st.*`, không đọc `st.session_state`** (như `send_and_record`). Luồng tự tạo `AIRouter`, `DraftStore`, client Cloudflare, client Sheets; không giữ client trong phiên.
- **Sổ việc trong bộ nhớ** (cùng `st.cache_resource`): mã nháp, Mã bài kế hoạch đang xử lý, bước đang làm, giờ bắt đầu bước, số lần gọi AI, cờ dừng. Không bí mật, không chữ AI.
- **App không chạy nền khi tắt:**
  - luồng chỉ là một phần của tiến trình app (cửa sổ `run.bat` / `run.command`); tắt cửa sổ, tắt máy thì lượt chạy dừng theo;
  - không lịch hẹn, không dịch vụ hệ điều hành nào;
  - mở lại app: **không tự chạy tiếp**, chỉ hiện «Dừng giữa chừng» và nút «▶ Chạy tiếp» (như C9 d: mở trang không gọi mạng).
- Đóng tab trình duyệt (app vẫn mở): lượt chạy tiếp tục; mở lại trang thấy tiến độ.

### 2.2. Hiện tiến độ

- **Khung «🤖 Đang soạn tự động»** trên Soạn bài (và dòng gọn ở Bài viết, Kế hoạch):
  - 7 bước với ✅ / ⏳ (kèm thời gian) / ⚠️;
  - «AI đang viết toàn bài… 1:42»;
  - số lần gọi Gemini, số ảnh đã tạo.
- **Cập nhật bằng vòng chờ trong lần chạy trang** (`time.sleep` 1–2 giây rồi vẽ lại khung, như `finish_send` chờ lần gửi):
  - chỉ **đọc** sổ việc trong bộ nhớ: không gọi mạng, không AI, không ghi đĩa;
  - lượt chạy xong thì `st.rerun()`, mở nháp ở bước 5;
  - không dùng `st.fragment(run_every=…)` (giữ đúng chữ LC-T140-14).
- **Bài đang chạy thì trang mở ở chế độ chỉ xem:** không ô sửa, không tự lưu, để không ghi đè việc của luồng.

### 2.3. Dừng, chạy tiếp, chạy lại

| Nút | Làm gì |
|---|---|
| ⏸ Dừng | Đặt cờ. Luồng dừng **sau** lần gọi đang chạy (không cắt ngang được một lần gọi AI). Nháp giữ tới bước xong cuối cùng |
| ▶ Chạy tiếp | Chạy từ bước chưa xong đầu tiên, trên nội dung **hiện có** trong nháp (kể cả chỗ bạn vừa sửa) |
| 🔁 Chạy lại từ bước này | Ở bước 2, 3, 4 và phần ảnh. Bỏ kết quả từ bước đó trở đi rồi chạy; hỏi lại trước (bài hiện tại bị thay). Ảnh bạn chọn tay, «Để trống chỗ này» giữ nguyên |
| ✖ Bỏ khỏi hàng | Bài chưa tới lượt |

### 2.4. Lỗi 503, hạn mức: phân loại, thử lại có giới hạn

**Hiện nay:** thư viện Gemini tự thử lại 2 lần khi 429, 5xx, rớt mạng (`HttpRetryOptions(attempts=3)`). Câu lỗi 429 «Gemini đang giới hạn số lần gọi…», 5xx «Gemini báo lỗi 503…». Mọi lỗi là một `AIError` chung, nên lượt chạy không biết nên chờ hay dừng.

**Thêm (phiếu G):** `AIError.kind` do lớp provider đặt (cả 3 hãng). Câu tiếng Việt giữ nguyên.

| `kind` | Khi nào | Lượt chạy làm gì |
|---|---|---|
| `busy` | 500, 502, 503, 504 | Chờ 30 giây, rồi 2 phút; vẫn lỗi thì dừng bài «Gemini đang quá tải» |
| `rate` | 429 giới hạn theo phút | Chờ theo `retryDelay` máy chủ đưa (tối đa 2 phút; không có thì 60 giây), thử tối đa 2 lần |
| `quota_day` | 429 hết hạn mức ngày (chi tiết có mã hạn mức theo ngày), 429 thanh toán, hay sổ đếm của máy đã chạm trần bạn ghi | **Dừng cả lô**, báo giờ đặt lại |
| `network`, `timeout` | Rớt mạng, quá 15 phút | Thử lại 1 lần sau 30 giây, rồi dừng bài |
| `auth`, `model`, `bad_request` | Khóa sai, tên mô hình sai, 400 | Dừng cả lô (phải sửa cấu hình) |
| `shape` | AI trả sai khuôn | Thử lại bước đó 1 lần |
| `refusal`, `token_limit` | AI từ chối, bài dài quá `max_tokens` | Dừng bài |

- **Trần:** mỗi bước thử lại tối đa 2 lần, mỗi bài tối đa 6 lần; lô dừng khi 2 bài liền dừng vì `busy`.
- Không bao giờ chép chữ máy chủ lên trang; chi tiết lỗi chỉ đọc khi đúng kiểu đã biết (như LC-T140-4).
- **Cần xác nhận ở buổi thử:** khuôn chi tiết của lỗi 429 (mã hạn mức theo ngày, `retryDelay`). Tôi không gọi Gemini thật nên chưa thấy khuôn này.
- **Giãn nhịp:** hai lần gọi Gemini cách nhau ít nhất 6 giây (≤ 10 lần/phút), đổi được ở mục `[auto]` mới của `config/ai.toml`.
- **Sổ đếm lần gọi Gemini** trên máy này, theo mô hình, theo ngày giờ Thái Bình Dương (ngày Google đặt lại hạn mức). Gộp với kho đếm neuron của T-140 phiếu B (`sqlite_file`). Trần do bạn ghi (`[auto]`, 0 = chưa biết: không chặn, chỉ hiện số đã dùng).

### 2.5. Hai tab, hai máy, F5, mất mạng

| Tình huống | Xử lý |
|---|---|
| Hai tab cùng máy | Sổ việc trong bộ nhớ dùng chung: tab thứ hai thấy «đang chạy», không bắt đầu lần nữa; nút Dừng ở tab nào cũng được |
| Tab đang mở bài đó từ trước khi lượt chạy bắt đầu | Tự lưu so giờ lưu (`expected_saved_at`): nháp đã đổi thì không ghi, báo «Nháp vừa được cập nhật ở nơi khác: mở lại» |
| «Viết bài» ở trang Kế hoạch đúng dòng lô đang xử lý | Sổ việc giữ cả Mã bài đang xử lý: mở bài đang chạy, không tạo nháp thứ hai |
| Hai máy | Kho nháp mỗi máy riêng. Lô chỉ lấy dòng Sheet đang «Chưa viết» (đọc lại ngay trước khi lấy) rồi ghi «Đang viết»; máy kia đọc thấy «Đang viết» thì bỏ qua |
| Hai máy bấm cùng lúc | Khe nhỏ: `write_status` coi «Đang viết» → «Đang viết» là đã đúng, nên hai máy có thể cùng viết một dòng (hai nháp trên hai máy). Không bài nào lên website khi chưa bấm; lần gửi thứ hai bị lớp ghi Sheet báo dòng đã khác (T-100) |
| F5, đóng tab | Lượt chạy không bị ảnh hưởng; trang mới đọc sổ việc |
| Mất mạng | `network`: thử lại 1 lần, rồi dừng bài, giữ chỗ dừng |
| Máy ngủ, tắt app | Lượt chạy dừng; mở lại thấy «Dừng giữa chừng», bấm «Chạy tiếp». README dặn tắt chế độ ngủ khi chạy lô |
| Hạn mức Cloudflare, Gemini dùng chung hai máy | Sổ đếm mỗi máy riêng; lỗi hết hạn mức của máy chủ (3036, 429) là chốt cuối |

## 3. Màn hình duyệt cuối, bước 5 (Việc 3)

### 3.1. Bố cục (từ trên xuống)

1. **Dòng trạng thái:** «🤖 Bài tự động · sẵn sàng duyệt · 3 chỗ vàng · 0 chỗ chặn» (hay «Dừng ở bước …» kèm «▶ Chạy tiếp»).
2. **Bài viết:** tiêu đề và toàn bài (Markdown qua `ui.highlight`, chữ đã escape), tô vàng, đỏ. Mỗi phần một nút «✏️ Sửa» (sang bước 3, mở đúng phần).
3. **Ảnh:** mỗi chỗ một thẻ:
   - ảnh xem trước đủ lớn để đọc được chữ trong ảnh (LC-T140-15);
   - nhãn 📁 Tự chọn / ✨ Ảnh AI / 🖐 Bạn chọn; alt, chú thích; GPS; dấu vàng;
   - «✏️ Sửa» sang bước 3, đúng chỗ ảnh (đổi, tạo lại, bỏ, sửa alt).
4. **SEO:** tiêu đề SEO, mô tả, slug, từ khóa chính (nhãn Nên / Cảnh báo / Chặn), xem trước Google, bảng link nội bộ, FAQ; «✏️ Sửa» sang bước 4.
5. **Dàn ý, nghiên cứu** (thu gọn): «✏️ Sửa dàn ý» sang bước 2; sửa xong «🔁 Chạy lại từ bước viết».
6. **Gửi sang WordPress** (khung đang có):
   - Nháp / Hẹn giờ / Đăng ngay; ngày giờ điền sẵn từ dòng kế hoạch; chuyên mục; ảnh đại diện;
   - bảng mọi link, ô «Ghi SEO lên website», cảnh báo GPS;
   - **ô duyệt chung** (3.5); nút gửi.

### 3.2. Nút «Sửa» và quay lại

- «Sửa» ghi `_from_review` cùng chỗ cần mở (phần, chỗ ảnh) rồi chuyển bước. Bước đó có thanh trên cùng «Đang sửa bài tự động · ↩ Về bước duyệt».
- Mọi chỗ sửa làm đổi mã băm màn hình, nên ô duyệt chung tự bỏ tick (`confirm_box` đang có). Phải xem lại rồi tick lại.

### 3.3. Dấu vàng (chỉ cảnh báo, không khóa nút)

| Dấu | Nguồn | Hiện ở |
|---|---|---|
| Thiếu chất liệu thật | `gaps` (1.4) | Câu viết chung, kèm «Nên bổ sung: …» |
| Câu cần xem lại | Góp ý chưa tự áp, cụm sáo rỗng (1.5) | Câu trong bài |
| Văn phong dưới 80, chưa chấm lại | Lần chấm cuối | Bảng kiểm |
| Ảnh thật tự chọn | Phiếu B | Thẻ ảnh: «Xem kỹ: nhà khách, biển số, mặt người, số điện thoại?» |
| Alt viết từ mô tả | Câu hỏi 1 = A | Thẻ ảnh |
| Ảnh có GPS | `web_info` | Thẻ ảnh; cảnh báo trước nút gửi giữ nguyên |
| Ảnh AI | Ảnh Cloudflare | Thẻ ảnh (chú thích «Ảnh minh họa (AI)» sẽ hiện dưới ảnh) |
| Chỗ cần ảnh còn trống | Không khớp, Cloudflare lỗi, prompt bị từ chối | Thẻ ảnh, kèm «Sửa» |
| Ghi chú kế hoạch có số điện thoại, email (đã che) hay có giá | `fill_from_plan` | Đầu trang |
| Không tìm Google khi nghiên cứu | T-138 | Dòng nhỏ |
| Chưa có danh sách bài đã đăng | Không có bản lưu | Phần SEO: «chưa gợi ý link» |
| SEO không ghi lên website | Công tắc tắt | Khung gửi (như hiện nay) |

### 3.4. Điều gì chặn gửi (nút khóa)

| Chặn | Nguồn | Ghi chú |
|---|---|---|
| Lượt chạy dừng trước khi viết xong bài | Mới | Bấm «Chạy tiếp» hay tự viết |
| Ô duyệt chung chưa tick, hay bài đổi sau khi tick | Mới (thay tick từng ảnh) | Mọi hình thức, **cả Nháp** |
| Còn «[cần bổ sung: …]» trong bài | Mới | Chỉ Hẹn giờ, Đăng ngay; Nháp chỉ cảnh báo |
| Dòng «Chặn» của bộ dựng (link hỏng, link tới nháp, nhúng trang, thiếu link bắt buộc…) | Có sẵn | |
| Ảnh không dùng được, chưa có alt | `slot_problem` | Có sẵn |
| Khóa gửi trùng (đang gửi, đã gửi, không rõ kết quả, file nháp bị cất) | T-086, T-089, T-092, T-130, T-137 | Có sẵn |
| Hẹn giờ: giờ đã qua, dưới 10 phút, quá một năm; tài khoản không có quyền đăng | Có sẵn | |
| Đăng ngay: thiếu ảnh đại diện, SEO chưa lên website | T-112 | Có sẵn |
| Công tắc Hẹn giờ / Đăng ngay tắt | LC-T094-41 | Có sẵn (không có nút) |
| Chưa kết nối WordPress | Có sẵn | |

### 3.5. Ô duyệt chung thay tick duyệt từng ảnh (cho Lá Chắn)

**Hiện nay:** mỗi ảnh có ô alt, chú thích và tick «✅ Đã duyệt». Tick ghi `altok-<id>` và `altsha-<id>` (băm byte file đúng lúc đang hiện). Lúc gửi, byte đọc để tải phải cùng băm (T-086); băm lưu trong nháp, mở lại mà ảnh khác thì bắt duyệt lại (T-089).

**Đề xuất cho bài tự động** (bài soạn tay giữ tick từng ảnh, không đổi gì):

1. Chỗ ảnh «sẵn sàng» khi ảnh dùng được và có alt (không đòi tick riêng).
2. Màn hình cuối dựng gói gồm mọi ảnh đó. Mã băm gói có băm byte WebP, alt, chú thích từng ảnh (`ArticleImage`).
3. Ô «☐ Tôi đã đọc bài và xem từng ảnh, alt, chú thích ở trên (không có nhà khách, biển số, số điện thoại)», đòi tick ở **mọi** hình thức gửi, cả Nháp. Tick thì mã ghi:
   - cho **đúng từng ảnh đang hiện**: `altok = True`, `altsha = băm byte file đang hiện` (đúng hai giá trị tick từng ảnh đang ghi);
   - `_wp_confirmed = mã băm màn hình` (LC-T094-38).
4. Lúc gửi giữ nguyên mọi lớp kiểm: so `altsha` với byte đọc để tải; dựng lại gói và so mã băm ngay trước lệnh ghi đầu tiên.
5. Sửa alt, đổi ảnh, file bị thay cùng tên: ảnh đó mất duyệt, mã băm màn hình đổi, ô chung bỏ tick.

**Câu đề xuất thay điều kiện LC-T140-12** (Lá Chắn duyệt):

> **LC-T140-12 (sửa theo T-141):** ảnh tự chọn **không bao giờ tự duyệt** khi lượt chạy tự động chạy. Bài tự động chỉ gửi được khi ô duyệt chung ở màn hình cuối đã tick; tick đó ghi duyệt cho đúng các ảnh đang hiện, gắn băm byte từng ảnh (T-086, T-089) và mã băm màn hình (LC-T094-38); ô này đòi tick ở cả Nháp. Ở màn hình cuối, mỗi ảnh hiện đủ lớn, có nhãn «📁 Tự chọn», huy hiệu GPS, dấu vàng «xem kỹ nhà khách»; `GPS_PUBLIC_WARNING` vẫn hiện trước nút gửi; đổi, bỏ ảnh qua «Sửa» một cú bấm; «Để trống chỗ này» và lựa chọn tay không bao giờ bị đè. Bài soạn tay giữ tick từng ảnh như cũ.

### 3.6. Giữ nguyên

- Màn hình xác nhận và mã băm; khóa gửi trùng T-086 → T-137; công tắc Hẹn giờ / Đăng ngay mặc định tắt; Đăng ngay chỉ khi ảnh đại diện và SEO đã lên (T-112); cảnh báo GPS trước nút gửi.
- Lượt chạy tự động **không có đường nào** tới `create_draft_with_images`, `release_draft`, `set_seo_meta`, và không đọc gì từ website. Test: đếm request WordPress = 0 trong cả lượt chạy, cả lô.

## 4. «Viết các bài tới hạn» (Việc 4)

### 4.1. Chọn dòng

- **Nguồn:** bản kế hoạch trên máy (`plan_cache`) để hiện số bài; lúc bấm thì đọc lại Sheet (LC-T094-29).
- **Dòng được chọn** khi đủ mọi điều kiện:
  1. có Mã bài, từ khóa hợp lệ (`PlanRow`);
  2. Trạng thái **«Chưa viết»**. Dòng «Đang viết» bỏ qua (đang viết ở máy khác, hay dở dang: mở bằng «Viết bài» như cũ);
  3. Ngày dự kiến từ hôm nay tới 6 ngày sau (7 ngày lịch). Dòng đã quá ngày: câu hỏi 2;
  4. Loại trang không phải «Cập nhật bài cũ» (như nút «Viết bài», T-101);
  5. máy này chưa có nháp của Mã bài đó (`find_plan_draft`).
- **Thứ tự:** ngày dự kiến, giờ đăng, Ưu tiên (Cao trước), Mã bài. Lấy tối đa 5, và không quá số chỗ còn trong kho nháp (câu hỏi 3).
- **Bấm nút → popover xác nhận:**
  - danh sách «Mã bài · từ khóa · ngày giờ»;
  - ước tính «khoảng 40 lần gọi Gemini, 20 ảnh AI, 15–30 phút»; «hôm nay máy này đã gọi Gemini X lần»;
  - nút «Bắt đầu».

### 4.2. Chạy lô

- **Lần lượt từng dòng:**
  1. đọc lại dòng (`open_row`); còn «Chưa viết» và còn hợp lệ thì làm tiếp;
  2. tạo nháp gắn kế hoạch (`plan_ref`, phần thuần của `fill_from_plan`);
  3. ghi «Đang viết» (`record_status`, như nút «Viết bài»);
  4. chạy luồng tự động một bài (mục 1).
- Dòng vừa đổi trên Sheet, ghi «Đang viết» lỗi: bỏ dòng đó, ghi lý do, sang dòng sau.
- Hết hạn mức ngày (`quota_day`): dừng lô. Dòng chưa tới lượt không bị đụng (vẫn «Chưa viết»), lần bấm sau lấy lại.
- **Không bao giờ** gửi, hẹn giờ, đăng hàng loạt (LC-T094-35): mỗi bài gửi riêng ở bước cuối.

### 4.3. Danh sách «Chờ duyệt»

- **Ở trang Bài viết**, thay khung «Đang viết» đang là bản demo. Ba nhóm thẻ đọc từ kho nháp và sổ việc:
  - «⏳ Đang chạy»: bước, thời gian; nút Dừng;
  - «🟡 Chờ duyệt»: bài chạy xong, chưa gửi; từ khóa, Mã bài, ngày giờ dự kiến, số chỗ vàng; nút «Mở để duyệt» (Soạn bài, bước 5);
  - «⚠️ Dừng giữa chừng»: lý do; nút «Chạy tiếp».
- **Trang Kế hoạch:** nút, tiến độ lô dạng gọn, liên kết sang Bài viết.
- **Đổi một nhãn để khỏi nhầm:** khung «Đã gửi WordPress» đang dùng chữ «Chờ duyệt» cho trạng thái `pending` của WordPress; đổi thành «Chờ duyệt trên website».
- Danh sách chỉ có trên máy đã viết (kho nháp là của máy). Máy kia thấy dòng «Đang viết» trên Sheet.

### 4.4. Hẹn giờ theo dòng, ghi trạng thái Sheet

- Mở bài: ngày giờ của dòng điền sẵn vào ô Hẹn giờ (`plan_details`, như hiện nay). Hình thức chọn sẵn «Hẹn giờ» khi công tắc bật và giờ còn hợp lệ; không thì «Nháp».
- Gửi xong: ghi trạng thái về Sheet như hiện nay (T-100, T-102: «Đã gửi nháp» / «Đã hẹn giờ» / «Đã đăng»; lỗi thì giữ việc còn nợ, thử lại ở trang Kế hoạch).

## 5. Đối chiếu điều kiện cũ của Lá Chắn (Việc 5)

| # | Điều kiện cũ | Chế độ tự động đụng thế nào | Đề xuất |
|---|---|---|---|
| 1 | **T-050 đk 3a, LC-T050-4, sổ rủi ro 18/11:** AI chỉ xem ảnh khi người dùng bấm, cho ảnh đã chọn; giảm rủi ro bằng cách «tránh gửi ảnh có mặt người, số nhà, biển hiệu» | Nếu AI tự xem ảnh thật tự chọn thì không ai nhìn ảnh trước khi ảnh tới Google | **Câu hỏi 1 = A: không đổi điều kiện.** Lượt chạy không gửi ảnh thật cho AI; alt viết từ chữ; «AI xem ảnh» chỉ khi bấm. (Chọn B thì điều kiện đổi thành «AI xem ảnh thật tự chọn trong lượt chạy bạn bấm, chỉ byte `make_ai_image`, mỗi ảnh một lần», sổ rủi ro thêm một dòng) |
| 2 | **T-050 đk 3b, T-056:** alt, chú thích hiện trong ô để người dùng sửa và **duyệt từng ảnh** | Không còn tick từng ảnh | Ô duyệt chung (3.5). Alt, chú thích vẫn sửa trong ô nhập ở bước 3; ở màn hình cuối hiện chữ thuần (escape) |
| 3 | **T-086, T-089:** băm ảnh đã duyệt, lưu trong nháp; mở lại mà ảnh khác thì duyệt lại | Băm đặt lúc tick từng ảnh | **Giữ nguyên cơ chế**, chỉ đổi chỗ đặt băm: tick chung ghi băm từng ảnh. Lúc gửi vẫn so |
| 4 | **LC-T140-12:** ảnh tự chọn tick duyệt từng ảnh | Trái quyết định 19/11 | Thay bằng câu ở 3.5 |
| 5 | **LC-T140-14, C9 sửa:** chỉ tạo ảnh khi bấm; tối đa 8 ảnh mỗi lần bấm; nhánh B: một lần sau bước viết, ghi dấu | Ảnh tạo trong lượt chạy | Cú bấm là «Soạn tự động», «Viết các bài tới hạn», «Chạy tiếp». Tối đa 8 ảnh mỗi bài, 40 ảnh mỗi lần bấm lô; kiểm trần trước từng ảnh; mỗi chỗ tạo một lần mỗi lượt (`images_made`, ảnh đã có không tạo lại); không bao giờ khi mở trang, mở nháp, chạy lại trang; tiến độ chỉ đọc bộ nhớ |
| 6 | **LC-T094-21 (A3):** số điện thoại, email trong ghi chú kế hoạch: cảnh báo trước khi gửi AI | Lô không có người xem cảnh báo trước | **Che tự động** (`mask_personal_info`) trước khi vào lời dặn, đúng việc `fill_from_plan` đang làm; không bao giờ gửi bản chưa che; dấu vàng ở bước cuối |
| 7 | **T-094, T-103 đk 2a, 2b, LC-T120-24:** chữ kế hoạch (cả từ khóa Google đưa vào kế hoạch) là dữ liệu chưa tin cậy vào lời dặn AI; trước đây người dùng còn đọc dàn ý trước khi AI viết | Mất chốt người giữa dàn ý và bài | Chốt người dời về bước cuối (đọc cả bài). Giữ khung `_block`, `_keyword`, `DATA_RULES`. Thêm chốt mã trên kết quả AI: dàn ý (1.3), câu tự sửa không thêm số, giá, link, số điện thoại (1.5). Tiêu đề dự kiến: câu hỏi 5 (chọn A thì tiêu đề vào lời dặn trong khung `dan_y`) |
| 8 | **LC-T094-35:** không hẹn giờ, đăng hàng loạt; «Viết bài» không gửi gì lên WordPress | Lô viết nhiều bài | **Giữ nguyên:** lô chỉ viết; 0 lệnh WordPress, kể cả đọc (dùng danh sách bài đã lưu); test đếm |
| 9 | **LC-T094-38:** mã băm xác nhận | — | Giữ; với bài tự động áp cả cho Nháp |
| 10 | **LC-T094-41:** công tắc Hẹn giờ / Đăng ngay mặc định tắt | — | Giữ |
| 11 | **Lá Chắn T-042:** «Ghi SEO lên website» mặc định tắt | Phải chép tay vào SiteSEO, trái mục tiêu «duyệt một lần» | Câu hỏi 4: bật sẵn cho bài tự động, vẫn nằm trong mã băm, vẫn tắt được |
| 12 | **Quy trình nội dung bước 4** (duyệt dàn ý) | Chủ dự án thay 19/11 | Mã kiểm dàn ý (1.3) và duyệt cả bài ở bước cuối |
| 13 | **«Không sản xuất nội dung hàng loạt»** | Chủ dự án thay 19/11 | Tối đa 5 bài mỗi lần bấm, chạy lần lượt, duyệt từng bài; khóa nút khi đã có 5 bài chờ duyệt (câu hỏi 3) |
| 14 | **T-137:** file nháp bị cất thì tick «bài này chưa có trên website» | — | Giữ, áp cả bài tự động |

**Chỗ mới Lá Chắn cần đọc** (không thuộc điều kiện cũ nào):

- Luồng nền trong app: không gọi `st.*`; sổ việc không giữ bí mật, không chữ AI; câu lỗi cố định; dừng khi app tắt; không tự chạy khi mở lại.
- Vòng chờ tiến độ chỉ đọc bộ nhớ.
- `DraftStore.save(expected_saved_at=…)`.
- `AIError.kind` ở 3 provider (câu lỗi không đổi; chi tiết lỗi máy chủ chỉ đọc kiểu đã biết).
- Chốt tự áp câu sửa (1.5).
- Bộ dựng chặn «[cần bổ sung: …]» khi Hẹn giờ, Đăng ngay.
- Lời gọi `image_prompt` gộp cả bài: đầu vào vẫn chỉ mô tả, tiêu đề mục, mặt thẻ (LC-T140-10).

## 6. Hạn mức (Việc 6)

### 6.1. Số lần gọi AI mỗi bài (đường bình thường)

| Bước | Việc | Gemini | Cloudflare |
|---|---|---|---|
| Nghiên cứu | `research` | 1 | |
| Dàn ý | `outline` | 1 (+1 nếu làm lại) | |
| Viết | `write` | 1 | |
| Rà soát, chấm lại | `review` | 2 (1 nếu không có câu tự sửa) | |
| Meta | `meta` | 1 (+1 nếu mọi gợi ý hỏng) | |
| Liên kết nội bộ | `links` | 1 (0 nếu chưa có danh sách bài; +1 nếu thiếu link bắt buộc) | |
| Chữ ảnh (prompt, alt, chú thích) | `image_prompt` | 1 (0 nếu bài không có chỗ ảnh) | |
| Tạo ảnh AI | — | | Khoảng 4 ảnh (0–8) × khoảng 58 neuron |
| **Tổng** | | **8** (ít nhất 6, nhiều nhất 11) | Khoảng 230 neuron |

- Gemini đang bận thì một lần gọi có thể thành 2–3 request (thư viện tự thử lại); Google đếm cả các request đó.
- Chữ ước tính mỗi bài: khoảng 60 nghìn token vào (hồ sơ doanh nghiệp nằm trong mọi lời dặn) và 20 nghìn token ra, kể cả phần «suy nghĩ».
- Thời gian ước tính: 3–6 phút mỗi bài (bước viết với `effort = "high"` lâu nhất), cộng giãn nhịp khoảng 1 phút.

### 6.2. Năm bài

| | Gemini | Cloudflare |
|---|---|---|
| Thường | Khoảng 40 lần gọi | Khoảng 20 ảnh, 1.150 neuron (13% trần 9.000 của app) |
| Nhiều nhất | Khoảng 55 lần gọi | 40 ảnh, 2.300 neuron (26%) |

### 6.3. Gemini miễn phí có vượt không

- **Chưa biết chắc.** Tài liệu Google (19/11) không ghi số lần/ngày của gói miễn phí cho mô hình Flash, chỉ bảo xem trong AI Studio. Hạn mức tính theo project: hai máy dùng cùng khóa thì chia chung.
- Đặt lại lúc nửa đêm giờ Thái Bình Dương: **15:00 giờ Việt Nam** (từ tháng 11 tới tháng 3), 14:00 (từ tháng 3 tới tháng 11). App tính theo múi giờ `America/Los_Angeles`, không viết cứng.

| Nếu hạn mức ngày là | Số bài mỗi ngày (8 lần gọi/bài, chưa tính sửa tay) | Lô 5 bài |
|---|---|---|
| 20 lần | 2 | Không hết trong một ngày |
| 50 lần | 6 | Vừa đủ, sát |
| 100 lần | 12 | Thoải mái |
| 250 lần | 31 | Thoải mái |

- **Theo phút:** giãn nhịp 6 giây nên tối đa 10 lần/phút. AI Studio cho thấy thấp hơn (ví dụ 5 lần/phút) thì tăng lên 12 giây ở `[auto]`.

### 6.4. Cloudflare có vượt không

Không. Trần 9.000 neuron của app đủ khoảng 155 ảnh mỗi ngày, tức khoảng 40 bài (theo ước tính 57,6 neuron/ảnh của T-140; lần gọi thử LC-T140-17 đo lại).

### 6.5. Cách chia

1. Lô tối đa 5 bài, chạy lần lượt, giãn nhịp.
2. **Trước khi chạy,** app ước số lần gọi cần, so với số đã dùng hôm nay và trần bạn ghi. Thiếu thì đề nghị viết ít bài hơn: «Hôm nay còn đủ cho 2 bài. Viết 2 bài trước?».
3. **Hết hạn mức giữa lô:** dừng; giữ bài đã xong; dòng chưa tới lượt không bị đụng; bấm chạy tiếp sau giờ đặt lại.
4. Sửa tay (viết lại một phần, gợi ý lại meta, AI viết alt) cũng tốn lượt trong cùng hạn mức.
5. **Nếu hạn mức thấp:**
   - (a) «chế độ tiết kiệm lượt» (sau đợt này): gộp meta, liên kết, chữ ảnh vào một lần gọi (8 → 6), bỏ lần chấm lại (6 → 5);
   - (b) AI Studio cho thấy mô hình Flash-Lite có hạn mức riêng thì chuyển các việc nhỏ (`meta`, `links`, `alt`, `image_prompt`) sang mô hình đó trong `config/ai.toml` (hạn mức tính theo từng mô hình);
   - (c) bật thanh toán Gemini (câu hỏi 6).

## 7. Chia phiếu code, thứ tự gộp (Việc 7)

Số phiếu do Chỉ Huy cấp. Giữ ký hiệu A–F của T-140 (Lá Chắn đã duyệt), phiếu mới của T-141 là G, H, J, K, L.

### 7.1. Phiếu T-140 sau khi gộp

| Phiếu | Ai | Thêm, đổi vì T-141 | Lá Chắn |
|---|---|---|---|
| **A** · Client Cloudflare, ảnh AI sạch, kho ảnh AI | Thợ Máy | Gọi được từ luồng nền (không `st.*`); lỗi trả `kind` cho lượt chạy | Đầy đủ |
| **B** · Tự chọn ảnh, sổ ảnh đã gửi, đếm neuron | Thợ Máy | Hàm thuần gán ảnh cho cả bài (kèm lý do từng chỗ); kho đếm dùng chung cho sổ đếm Gemini (phiếu G) | Rút gọn |
| **C** · Lời dặn ảnh, dàn ý | Ngòi Bút | Gộp **mọi** lời dặn chế độ tự động: dàn ý (1.3), viết (`gaps`, không «[cần bổ sung]»), chữ ảnh cho cả bài (1.7); ghi chú mục `[auto]` trong `config/ai.toml` | Rút gọn (A1, A2) |
| **D** · Việc AI chữ ảnh, khuôn nháp 4 | Thợ Máy | `image_texts` một lần cho cả bài (thay mỗi chỗ một lần); khuôn nháp 4 thêm `auto` (1.8); `save(expected_saved_at=…)` | **Đầy đủ** (đụng `save`) |
| **E** · Cài đặt | Họa Sĩ | Chỉ còn trang Cài đặt: mục Cloudflare (T-140 mục 4) và dòng «Hôm nay máy này đã gọi Gemini X lần». Phần Soạn bài của E chuyển sang J (cùng file `write.py`) | Rút gọn (U1, S2, LC-T140-2) |
| **F** · README, sổ rủi ro | Thư Ký | Thêm chế độ tự động: cách dùng, giữ app mở, tắt chế độ ngủ, hạn mức Gemini (xem trong AI Studio), dấu vàng, ô duyệt chung. Sổ rủi ro: luồng nền; chữ kế hoạch vào AI không qua duyệt dàn ý; ảnh tự chọn chỉ được người dùng nhìn ở bước cuối | Rút gọn |

### 7.2. Phiếu mới

| Phiếu | Ai | Việc | File chính | Lá Chắn |
|---|---|---|---|---|
| **G** · Loại lỗi AI, sổ đếm Gemini, giãn nhịp | Thợ Máy | `AIError.kind` ở 3 provider, câu giữ nguyên (2.4); sổ đếm lần gọi theo ngày Thái Bình Dương; đọc `[auto]` chịu lỗi (giãn nhịp, trần ngày) | `seo_app/ai/*.py`, kho đếm của B | Đầy đủ (lớp AI) |
| **H** · Lõi chạy tự động một bài | Thợ Máy | `seo_app/auto/` (`steps`, `runner`, `compose`, `plan_start`); `ContentWriter.write(auto=True)`, chốt tự áp; bộ dựng chặn «[cần bổ sung]» ở Hẹn giờ, Đăng ngay; dời phần thuần của `start_from_plan`; test mục 1.9 | `seo_app/auto/*`, `seo_app/content/workflow.py`, `seo_app/publish/render.py`, `app/views/write.py` (chỉ chỗ gọi hàm dời đi) | Đầy đủ |
| **J** · Giao diện chế độ tự động trên Soạn bài | Họa Sĩ | Nút «Soạn tự động»; khung tiến độ; chỉ xem khi đang chạy; Dừng / Chạy tiếp / Chạy lại; màn hình duyệt cuối (mục 3), ô duyệt chung, «Sửa» và quay lại; bước ảnh theo T-140 mục 4 (nhãn nguồn, tạo lại, ảnh trước, sửa prompt) | `app/views/write.py`, `app/assets/style.css` | Đầy đủ (đường gửi) |
| **K** · «Viết các bài tới hạn» (lõi) | Thợ Máy | Chọn dòng, đọc lại, ghi «Đang viết», hàng đợi lô, ước lượt, giới hạn kho nháp (mục 4) | `seo_app/auto/batch.py` | Rút gọn (dùng lại `open_row`, `record_status`) |
| **L** · Giao diện lô bài tới hạn, «Chờ duyệt» | Họa Sĩ | Nút, popover xác nhận ở Kế hoạch; khung Đang chạy / Chờ duyệt / Dừng giữa chừng ở Bài viết (thay demo «Đang viết»); đổi nhãn «Chờ duyệt trên website» | `app/views/plan.py`, `app/views/home.py` | Rút gọn |

Mọi phiếu code: Soi Lỗi kiểm. Test không gọi AI, Cloudflare, Google, WordPress thật; tham số lớn có `ids` ngắn.

### 7.3. Thứ tự gộp

| Đợt | Phiếu | Vì sao |
|---|---|---|
| 1 | A, B, C, G song song | Khác file |
| 2 | D | Sau C (khuôn lời dặn chữ ảnh, `gaps`) |
| 3 | H | Cần A, B, C, D, G. D và H cùng sửa `workflow.py` nên phải lần lượt |
| 4 | J, K, E song song | J sau H (`write.py`); K sau H; E sau A, G (`settings.py`) |
| 5 | L, F | L sau K; F cùng J, L |
| 6 | Trước khi bật (7.4) | |

**Nếu cần sớm:** tách H, J làm hai lượt. Lượt 1 không có Cloudflare (chỗ ảnh AI để trống, ghi prompt như hiện nay), không cần A; chủ dự án dùng được «Soạn tự động» cho chữ, SEO, ảnh thư mục sớm hơn. Lượt 2 cắm ảnh Cloudflare vào bước ⑥ khi A xong.

### 7.4. Trước khi bật cho bài thật

1. Lần gọi thử Cloudflare (LC-T140-17).
2. Xem hạn mức Gemini trong AI Studio (số lần/phút, lần/ngày của `gemini-3.8-flash`), ghi vào `[auto]`. Gặp lỗi 429 theo ngày thì chép khuôn chi tiết (không có bí mật) để xác nhận cách nhận ra; không cố đốt hạn mức để thử.
3. Chạy thử 1 bài theo từ khóa và một lô 2 dòng trên Sheet bản sao (như T-128): đo thời gian, số lần gọi; gửi Nháp, xem trên website, rồi xóa.
4. Lá Chắn đọc kết quả rồi mới cho dùng với bài thật.

## 8. Câu hỏi cho chủ dự án

1. **Alt của ảnh thật app tự chọn: AI có nhìn ảnh không?**
   - A (khuyến nghị): không. AI viết alt từ mô tả chỗ cần ảnh và tên thư mục; ảnh không rời máy, không tốn thêm lượt Gemini. Ở bước cuối, ảnh nào alt chưa khớp thì bấm «✨ AI xem ảnh, viết lại alt» cho riêng ảnh đó.
   - B: AI tự xem mọi ảnh thật app tự chọn. Gemini miễn phí: Google có thể dùng ảnh; mỗi ảnh thêm một lần gọi.
2. **Dòng kế hoạch đã quá Ngày dự kiến mà chưa viết: có viết luôn không?**
   - A (khuyến nghị): có, xếp trước; ngày hẹn giờ điền sẵn là ngày mai, giờ của dòng (bạn sửa được).
   - B: không, chỉ lấy dòng có ngày từ hôm nay tới 6 ngày sau.
3. **Đã có nhiều bài «Chờ duyệt» chưa gửi: có cho viết tiếp không?**
   - A (khuyến nghị): khi đã có 5 bài chờ duyệt, nút «Viết các bài tới hạn» tạm khóa, nhắc duyệt bớt. Đúng ý «duyệt từng bài», và kho nháp (giữ 30 nháp, đầy thì bỏ nháp cũ nhất) không làm mất bài chưa gửi.
   - B: không khóa; app chỉ báo khi kho nháp sắp đầy.
4. **«Ghi SEO lên website» cho bài tự động: bật sẵn?**
   - A (khuyến nghị): bật sẵn ở bước cuối (bạn vẫn tắt được). Tiêu đề, mô tả SEO tự vào hộp SiteSEO, không phải chép tay; cách ghi này đã thử thật ở T-059. Lá Chắn cần đồng ý (hiện mặc định tắt).
   - B: giữ mặc định tắt như bây giờ.
5. **Tiêu đề dự kiến trong kế hoạch: dùng làm tiêu đề bài?**
   - A (khuyến nghị): có, khi ô có chữ và qua kiểm (có từ khóa chính, không quá 70 ký tự, không link); ô trống thì AI đặt.
   - B: AI luôn đặt tiêu đề; tiêu đề dự kiến chỉ hiện để tham khảo, như bây giờ.
6. **Nếu Gemini miễn phí chỉ đủ dưới 5 bài mỗi ngày?**
   - A (khuyến nghị): đo trước ở buổi thử (xem AI Studio, chạy thử 1 bài). Chỉ Huy báo lại số bài mỗi ngày thật, rồi bạn quyết.
   - B: bật thanh toán Gemini ngay (có tốn phí; ít báo bận hơn, dùng được bản Pro, bật lại tìm Google).

## Đối chiếu tiêu chí xong

- [x] Việc 1, luồng tự động một bài: mục 1 (thứ tự bước, AI và mã, dàn ý tự duyệt, chất liệu thật và chỗ thiếu, luật tự sửa, SEO, ảnh theo T-140, lưu sau từng bước).
- [x] Việc 2, chạy lâu trong Streamlit: mục 2 (luồng nền, tiến độ, dừng, chạy tiếp, 503 và hạn mức, hai tab, hai máy, không chạy nền khi tắt app).
- [x] Việc 3, màn hình duyệt cuối: mục 3 (bố cục, «Sửa», dấu vàng, chặn và cảnh báo, ô duyệt chung, khóa gửi trùng, công tắc).
- [x] Việc 4, «Viết các bài tới hạn»: mục 4 (chọn dòng, chạy lô, «Chờ duyệt» ở trang Bài viết, ngày giờ hẹn, ghi Sheet).
- [x] Việc 5, đối chiếu điều kiện Lá Chắn: mục 5 (14 điều kiện, câu thay LC-T140-12 ở 3.5).
- [x] Việc 6, hạn mức: mục 6.
- [x] Việc 7, chia phiếu, thứ tự gộp với A–F, câu hỏi: mục 7, 8.
- [x] Không sửa mã; không gọi AI, Google, WordPress, Cloudflare thật.

## Rủi ro và điểm cần chú ý

- **Không còn ai đọc dàn ý trước khi AI viết.** Chất lượng dựa vào màn hình cuối. Dấu vàng chỉ chỗ nên xem, nhưng vẫn nên đọc lướt cả bài.
- **Hạn mức Gemini miễn phí chưa biết.** Thấp thì lô 5 bài không chạy hết trong một ngày. Gemini Flash miễn phí hay báo bận (503) giờ cao điểm: lô chậm, có thể dừng.
- **Kho nháp chỉ giữ 30 nháp;** lưu nháp thứ 31 thì nháp cũ nhất bị bỏ, kể cả bài chờ duyệt chưa gửi. Kiểm chỗ trống trước lô, câu hỏi 3. Sau đợt này nên để kho ưu tiên bỏ nháp đã gửi.
- **Bài chờ duyệt chỉ nằm trên máy đã viết.**
- **Luồng nền và Streamlit:** lỡ gọi `st.*` trong luồng thì lượt chạy hỏng âm thầm. Có test quét mã; Soi Lỗi thử dừng, F5, hai tab, tắt app giữa chừng.
- **Khuôn nháp 4 gộp hai thiết kế:** nâng khuôn một lần; nháp cũ đọc như cũ.
- **AI không theo lời dặn mới về «[cần bổ sung]»:** bài còn chữ này thì Hẹn giờ, Đăng ngay bị chặn.
- **Ảnh tự chọn có thể có nhà khách:** chỉ người nhìn ra (app không mở ảnh để kiểm). Ô duyệt chung bắt buộc ở cả Nháp vì vậy.
- **Khuôn lỗi 429 theo ngày của Gemini** chưa thấy tận mắt; nhận sai thì lô thử lại vô ích tới khi chạm trần mỗi bài (6 lần), rồi dừng.

## Đề xuất

- **Chỉ Huy:**
  - hỏi 6 câu ở mục 8;
  - đưa thiết kế cho Lá Chắn đọc (đầy đủ), nhất là mục 3.5 và mục 5;
  - nhờ Họa Sĩ xem mục 3, 4.3 trước khi lập phiếu J, L;
  - sửa nội dung phiếu T-140 A–F theo 7.1 trước khi lập phiếu code.
- **Sau đợt này:**
  - chế độ tiết kiệm lượt (6.5 a);
  - dùng cột «Từ khóa phụ, ý cần có» của kế hoạch khi lập dàn ý;
  - kho nháp ưu tiên bỏ nháp đã gửi khi đầy.

## Câu hỏi cho chủ dự án

Xem mục 8 (6 câu, mỗi câu có khuyến nghị).

# Báo cáo T-153 · Khuôn prompt ảnh chi tiết cho FLUX · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-153 «Khuôn prompt ảnh chi tiết cho FLUX» (Ngòi Bút) · mức kiểm **rút gọn**, Windows. Không gọi AI, Cloudflare thật; chỉ chạy test trong `wt-T-153` |
| Ngày nộp | 2026-11-20 |
| Mã nguồn | `team/T-153` tại `b77bbe9` (gốc `team/T-144` `4b8fe56`, đã có T-137, T-138). `main` `ddcd23c` là tổ tiên của nhánh. Gộp thử với `team/T-142` `a9ee007` (đã qua Lá Chắn, chờ gộp; cùng sửa lớp AI và `blind_test.py`) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới** (SL-T153-1: luật «Màu chủ đạo… dưới 25 ký tự» kèm ví dụ dài hơn mức; SL-T153-2: một ca test của phiếu hỏng khi gộp với `team/T-142`; không chặn Lá Chắn). Cấu hình đọc được, không đổi kết quả bộ đọc cũ; khối Cloudflare còn tắt, không đòi khóa; chữ bàn giao qua bộ kiểm, ca dài nhất 883 ≤ 900; R5 hợp lý. 59 file test liên quan trên nhánh: 5.216 qua, 8 `xfail` cũ, 0 hỏng. Gộp thử T-142: 769 qua, 1 hỏng (SL-T153-2) |

## Tóm tắt (cho chủ dự án)

- **Phần chữ cho ảnh minh họa AI đã đúng ý và an toàn.**
  - Mỗi ảnh sẽ được tả đủ 13 thành phần (vật chính, tình trạng, góc máy, ánh sáng…).
  - Phần mềm luôn tự gắn câu đầu và câu cuối an toàn: bề mặt trơn, không chữ, người (nếu có) ở xa và quay lưng.
  - Ba ví dụ ghép xong dài 650–676 ký tự, ca dài nhất có thể 883, đều dưới mức 900. Không chữ số, không link, số điện thoại, tên doanh nghiệp.
- **Cấu hình đọc được, không ảnh hưởng phần khác.** Mục luật mới không lọt vào lời dặn viết bài, alt hay meta. Việc mới «Viết chữ cho ảnh» chạy bằng Gemini Flash như các việc khác. Khối tạo ảnh bằng Cloudflare **còn tắt**; phần mềm không đòi khóa Cloudflare.
- **Hai lỗi nhỏ mới (Thấp):**
  - luật dặn AI viết màu «dưới 25 ký tự», nhưng chính ví dụ trong luật và cả 3 ví dụ mẫu đều dài hơn;
  - một test của phiếu này sẽ đỏ khi gộp chung với phiếu Cloudflare T-142 (phần mềm không sai, chỉ bộ test).
  - Cả hai sửa nhanh, không chặn việc kiểm bảo mật.

## Việc 1 · Cấu hình đọc được, khối Cloudflare còn tắt — **đạt**

- `config/content.toml`: mục mới `[image_prompt]` (11 luật, 3 ví dụ) đọc được bằng `tomllib`. Bỏ hẳn khối này đi thì 5 bộ đọc cũ cho kết quả **y hệt** (`load_rules`, `load_alt_rules`, `load_meta_rules`, `load_image_settings`, mục `[plan]`; test mới). Mục mới chưa đi vào lời dặn viết bài, alt hay meta nào: các bộ đọc chỉ đọc đúng mục của mình.
- `config/ai.toml`: `[tasks.image_prompt]` đọc được (Gemini Flash, effort `low`, `max_tokens` 8.000, không tìm web), tổng 10 việc. Việc này không nằm trong 5 việc viết bài dựng sẵn khi mở trang. Chủ dự án quay lại Claude cho các việc viết mà để `image_prompt` ở Gemini: trang Soạn bài không đòi khóa Gemini; chỉ khi gọi đúng việc này mới báo thiếu khóa, câu tiếng Việt (test mới).
- Khối `[tasks.image]` Cloudflare (`provider = "cloudflare"`, `@cf/black-forest-labs/flux-1-schnell`, `steps = 4`) để dấu # đủ 4 dòng, ghi «CHỈ BẬT SAU LẦN GỌI THỬ CÙNG CHỦ DỰ ÁN», khóa để trong `.env`. Hết các dòng Gemini «CHƯA XÁC MINH», giá ước tính.
- Không có mã nào đòi khóa Cloudflare: trên nhánh chưa có hãng này; T-142 không sửa `app/`, ảnh Cloudflare chỉ đi qua `cloudflare_images` khi được gọi.

## Việc 2 · Chữ an toàn, độ dài — **đạt, kèm SL-T153-1**

- Kiểm độc lập (script `sl153_chu.py`) chữ bàn giao trong báo cáo Ngòi Bút:
  - kiểu ảnh 48 ký tự; mệnh đề đầu 54 ≤ 60; đuôi 142 ≤ 200. Không chữ số, không link, email, số điện thoại, không «Pro-Metal», không câu phủ định («no», «not», «without»), không từ cấm (so cả từ lẫn chuỗi con);
  - 32 giá trị chọn (9 vị trí, 3 người, 4 góc, 3 cỡ cảnh, 4 ống kính, 5 ánh sáng, 4 bố cục): sạch;
  - 3 ví dụ ghép đủ 13 thành phần: 658, 650, 676 ký tự ≤ 900, qua bộ kiểm; các giá trị chọn trong ví dụ đúng là giá trị của danh sách;
  - ca dài nhất (mọi trường đúng trần mã, cụm chọn dài nhất, 3 chi tiết): 883 ≤ 900. Khớp báo cáo Ngòi Bút.
- Không mặt người rõ, không chữ, logo, số nhà, thương hiệu: mệnh đề đầu và đuôi tả bề mặt trơn, người «small and facing away»; luật 3 cấm nhắc tới các thứ đó kể cả để nói «không có». Không giả «công trình đã làm»: ví dụ tốt chỉ tả bộ phận, dấu hiệu hư, một bước làm; ví dụ xấu 3 là đúng cảnh «công trình hoàn thiện của chúng tôi», có nhãn «Không nên viết».
- Ví dụ chỉ dùng thông tin bịa, không số điện thoại, tên miền (test Ngòi Bút). Ví dụ xấu 1 có tên quận thật «Tan Phu»: GN-2.
- **SL-T153-1 (Thấp):** luật «Màu chủ đạo… dưới 25 ký tự» kèm ví dụ 27 ký tự; màu của cả 3 ví dụ tốt 25–27 ký tự; chi tiết phụ đầu của ví dụ 1 đúng 35 ký tự (luật «dưới 35»). Mục Lỗi mới.

## Việc 3 · Test mọi nơi đọc hai file cấu hình — **đạt**

- Grep mọi file test đọc `config/content.toml`, `config/ai.toml` hay qua hàm nạp (kể cả nhập muộn: `load_*`, `AI_CONFIG_FILE`, `CONTENT_CONFIG_FILE`, `TASK_LABELS`, `task_models`, `blind_test`, `AIRouter`, `ContentWriter`), cộng `test_app_pages.py`, `test_soi_loi_t084.py`, `test_t101_settings_google.py` (trang Cài đặt hiện bảng việc–mô hình): **59 file**, chạy 4 lô.
- Kết quả (4 lô, 14:36 → 15:04): **5.216 qua, 8 `xfail`**, 0 hỏng, 0 `XPASS`. Tám ca `xfail` đều có từ trước: SL-T026-3 ×2, SL-T036-10 ×1, SL-T045-1 ×3, SL-T045-2 ×2. File mới `test_soi_loi_t153.py` chạy riêng: 2 qua, 2 `xfail`.

## Việc 4 · R5, phạm vi sửa — **đạt**

- `test_soi_loi_t051.py`, `test_soi_loi_t062.py`: đổi theo khối Cloudflare mới.
  - `IMAGE_LINES` thay `max_tokens` bằng `steps`.
  - Các test cơ chế (khóa Gemini chỉ bị đòi khi gọi việc ảnh, thử mù không gợi ý mô hình ảnh, quên dòng `model`) bật khối với bản mẫu Gemini, giữ nguyên ý.
  - Bỏ đúng một phép so (`max_tokens == 2000`) vì khối mới không có dòng này. Không test nào bị tắt hay bỏ qua. Bảng R5 trong báo cáo Ngòi Bút đủ, đúng.
- `seo_app/content/blind_test.py` (ngoài phạm vi phiếu): thêm một nhãn `"image_prompt": "Viết chữ cho ảnh (prompt, alt)"`. Cần vì bất biến SL-T051-3 (việc nào trong `ai.toml` cũng có nhãn tiếng Việt), nhãn chỉ để hiện; gộp với T-142 không xung đột. Xem GN-1.
- Không sửa `prompts.py`, mục `[auto]`.

## Gộp thử với `team/T-142` — **có lỗi, SL-T153-2**

- T-142 đã qua Lá Chắn, chờ gộp; cùng sửa `seo_app/ai/registry.py`, `seo_app/content/blind_test.py`. `git merge-tree`: không xung đột chữ.
- Trên bản gộp (worktree tạm, không đẩy), 16 file (T-153, 4 file T-142, test cấu hình, thử mù, T-144, `test_app_pages`): **769 qua, 1 hỏng** (đúng ca SL-T153-2), 4 phút. Bốn file test của T-142 và `test_app_pages` qua với cấu hình mới của T-153. `test_soi_loi_t153.py` trên bản gộp: 2 qua, 2 `xfail`. Đã kiểm `seo_app` nạp từ bản gộp; worktree tạm đã gỡ.
- **SL-T153-2:** ca `test_enabled_cloudflare_block_loads_once_the_provider_exists` của Ngòi Bút rẽ nhánh theo `"cloudflare" in PROVIDERS`. T-142 thêm hãng này vào `IMAGE_ONLY_PROVIDERS` (hãng chỉ tạo ảnh), không vào `PROVIDERS`. Vì vậy trên bản gộp ca đi nhánh «chưa có hãng» và hỏng «DID NOT RAISE AIError». Nhánh nào gộp sau cũng làm `main` đỏ. Mục Lỗi mới.

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T153-1** | Thấp | Mục `[image_prompt]` dặn AI viết mỗi trường ngắn hơn trần mã (vì AI đếm ký tự không chính xác), nhưng ví dụ không theo đúng mức đó: luật «Màu chủ đạo: hai hay ba màu, dưới 25 ký tự: «black, rust orange and grey»» (27 ký tự); màu của ví dụ tốt 1, 2, 3 là 27, 25, 26 ký tự; chi tiết phụ «the hinge knuckle with fresh grease» đúng 35 ký tự (luật «dưới 35»). AI học theo ví dụ nên dễ vượt mức xin; trần mã của T-145 (30, 40) vẫn đỡ, nhưng phần dự phòng một phần tám mất | `tests/test_soi_loi_t153.py::test_sl_t153_1_vi_du_theo_dung_muc_cua_luat` (`xfail(strict=True)`; `--runxfail`: hỏng, 5 chữ vượt mức) |
| **SL-T153-2** | Thấp | `tests/test_t153_cau_hinh_anh.py::test_enabled_cloudflare_block_loads_once_the_provider_exists` đoán T-142 sẽ thêm «cloudflare» vào `PROVIDERS`. T-142 (đã qua Lá Chắn) thêm vào `IMAGE_ONLY_PROVIDERS`, nên gộp `team/T-153` và `team/T-142` thì ca này hỏng «DID NOT RAISE AIError» (đã gộp thử thật). Ứng dụng không sai; chỉ bộ test đỏ khi gộp | `tests/test_soi_loi_t153.py::test_sl_t153_2_ca_bat_khoi_cloudflare_van_qua_khi_da_co_t142` (`xfail(strict=True)`: dựng lại hợp đồng hãng chỉ tạo ảnh của T-142 rồi chạy ca của Ngòi Bút; `--runxfail`: hỏng đúng «DID NOT RAISE AIError») |

Gợi ý sửa:

- SL-T153-1: rút ví dụ màu xuống dưới 25 ký tự («black, rust and grey», «silver and dark grey», «black, grey, warm beige») và chi tiết phụ dưới 35 («the greased hinge knuckle»); hoặc nâng mức luật lên ngay dưới trần mã. Thêm phép so «ví dụ theo đúng mức của luật» vào test của Ngòi Bút.
- SL-T153-2: rẽ nhánh theo hãng tạo ảnh (`"cloudflare" in ai_registry.IMAGE_PROVIDERS`, hay `getattr(ai_registry, "IMAGE_ONLY_PROVIDERS", {})`) thay `PROVIDERS`. Sửa trước khi gộp nhánh thứ hai trong hai nhánh T-142, T-153.
- Không chặn Lá Chắn.

## Ghi nhận

- **GN-1 · Một dòng mã ngoài phạm vi phiếu.** Nhãn `TASK_LABELS["image_prompt"]` trong `seo_app/content/blind_test.py`.
  - Cần cho bất biến SL-T051-3; thiếu thì `test_sl_t051_3_every_task_has_a_vietnamese_label` hỏng ngay trên nhánh.
  - Nhãn chỉ để hiện: thử mù vẫn chỉ bỏ mô hình của việc `image` khi gợi ý.
  - Gộp với T-142 (cũng sửa file này) không xung đột.
  - Phiếu T-145 được giao dòng này; đề nghị Chỉ Huy, Lá Chắn xác nhận cho giữ ở T-153.
- **GN-2 · Ví dụ xấu 1 có tên quận thật «Tan Phu» và tên «Pro-Metal».** Đây đúng là thứ ví dụ muốn cấm, có nhãn «Không nên viết», cùng kiểu ví dụ xấu có sẵn của `[alt]` («… Pro-Metal sửa xong»). Không phải thông tin cá nhân. Chỉ lưu ý: ví dụ xấu cũng được gửi nguyên văn cho AI mỗi lần gọi.
- **GN-3 · Cho lần gọi thử Cloudflare** (thêm vào điều Ngòi Bút đã nêu về vế «any person» ở đuôi): ví dụ 2 tả «the ground floor front of a townhouse». Mặt tiền nhà phố ở Việt Nam thường có bảng hiệu, số nhà, nên khi thử nên xem FLUX có vẽ chữ, số không, dù mệnh đề đầu và đuôi đã tả «plain unmarked surfaces».
- **GN-4 · R5 bỏ phép so `max_tokens == 2000`:** đúng, vì khối Cloudflare không có dòng `max_tokens`. Trên bản gộp, T-142 kiểm `steps` (1–8) và test của nó qua.

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t153.py`, 4 hàm, 4 ca: 2 qua, 2 `xfail(strict=True)` (SL-T153-1, SL-T153-2).
  - Chạy: `uv run pytest tests/test_soi_loi_t153.py -rxX`.
  - Kiểm hai ca `xfail`: thêm `--runxfail -k sl_t153`.
- Script (thư mục ghi chú chung, `T-153-soi-loi-scripts/`):
  - `sl153_chu.py`: kiểm độc lập hằng, danh sách chọn, ví dụ ghép đủ, ca dài nhất;
  - `run_lots.sh`: chạy 4 lô test liên quan, lô nào xong thì bỏ qua (máy hay khởi động lại).
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 3 phát hiện.

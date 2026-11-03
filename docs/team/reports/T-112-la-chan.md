# Biên bản bảo mật T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay: luật Đăng ngay, công tắc ở Cài đặt (phương án A), so `modified_gmt` (T-115) · đầy đủ

> **Model:** lượt này **chạy Fable 5.1** (dòng «You are powered by» của lời nhắc hệ thống: Fable 5.1, kiểm theo luật 08:05 của Chỉ Huy B). Quy trình và mức độ lỗi: `docs/team/security.md`. Phần đối chiếu toàn vùng client WordPress + đăng bài (T-116 nhóm 2) ở biên bản riêng [`T-116-la-chan-nhom-2.md`](T-116-la-chan-nhom-2.md); biên bản này trả lời các câu về **T-112** (kể cả T-115 đã gộp vào nhánh).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **chạy Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-112](../tickets/T-112-chuan-bi-bat-hen-gio-dang-ngay.md) (phiếu chưa commit, đọc ở repo chính) · kiểm **đầy đủ** (W1–W4, U1, U2, F3, D1–D3; LC-T094-23, -38, -39, -41, -44) |
| Phạm vi | diff `7485b94..b4f7900` trên `team/T-112` (= `origin/main` `7485b94` + `team/T-115` `a7572f7` + T-112; 26 file): `app/views/write.py` (+103: `release_missing`, `release_post` giữ nháp, `write_seo` → `seo_ok`, `send_and_record` → `featured_missing`, `record_plan` G1, `send_draft` G2, `AGAIN_LABELS`), `app/views/settings.py` (+67: tab «📅 Hẹn giờ, đăng», `release_tab`), `seo_app/wordpress/client.py` (+96, T-115: `_modified`, `_remember_modified`, `_taint_modified`, `_same_modified`, `_release_check` so `modified_gmt`, `_RELEASE_CHANGED`), `README.md` (+83), 5 file test mới (`test_t112_release_rules`, `test_t112_settings_switch`, `test_soi_loi_t112`, `test_t115_modified_gmt`, `test_soi_loi_t115`), 11 file test đổi chuỗi `_fields`/gỡ dấu `xfail` (R5), 5 báo cáo. Kèm code xung quanh đã đọc trọn: `client.py` (2.782 dòng), bước Xuất bản của `write.py` (2.731–4.191), `seo_app/publish/*`, `seo_app/sanitize.py`, `seo_app/storage/drafts.py` (`SendState`, `save_send_state`) |
| Báo cáo đã đọc | [Họa Sĩ](T-112-hoa-si.md) (2 lượt), [Thư Ký](T-112-thu-ky.md), [Soi Lỗi](T-112-soi-loi.md) (ĐẠT CÓ ĐIỀU KIỆN: SL-T112-1 Trung bình, SL-T112-2/-3 Thấp), [Thợ Máy T-115](T-115-tho-may.md), [Soi Lỗi T-115](T-115-soi-loi.md), Lá Chắn T-115 (Opus, `b9da4b3` trên `team/T-115`, chưa có trên nhánh này: ĐẠT, ba giới hạn `modified_gmt`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4 (đạt ngưỡng `uvx`, LC-T078-1). Máy đang chạy toàn bộ test trên `main` nên chỉ chạy test chọn lọc. Không gọi website thật, không cloud |
| Ngày | 2026-11-03 (08:05–09:10, nghỉ vì hết hạn mức, 12:33–12:36; giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới** của Lá Chắn. Đồng ý mức của Soi Lỗi: **SL-T112-1 Trung bình**, SL-T112-2, -3 Thấp. **Gộp `main` được ngay khi công tắc tắt** (mặc định). **Trước khi bật công tắc** phải xong danh sách ở mục «Điều kiện bắt buộc trước khi bật». Cách lưu công tắc **A (chỉ trong phiên) đạt LC-T094-41**. Hẹn giờ khi SEO lỗi chỉ cảnh báo: **chấp nhận được**, kèm một khuyến nghị không chặn. LC-T094-23: **đóng đủ** (giữ kết luận Lá Chắn T-115 Opus); ba giới hạn `modified_gmt`: **đồng ý Thấp, ghi sổ rủi ro** |

## Tóm tắt (cho chủ dự án)

- **An toàn, gộp được ngay.** Phần mềm vẫn **chỉ gửi bài dạng Nháp** cho tới khi bạn tự bật công tắc Hẹn giờ / Đăng ngay ở Cài đặt (phải tick «Tôi hiểu…», công tắc tự tắt khi tải lại trang hay tắt app, không lưu ở đâu cả). Tôi đọc hết mã và tự thử: không đường nào đưa bài lên công khai ngoài ý bạn, không tham số địa chỉ hay file nào bật được công tắc.
- **Khi đã bật**, Đăng ngay chỉ đăng khi ảnh đại diện và phần SEO đã lên website; ai đó vừa sửa bài nháp trong trang quản trị thì phần mềm không đăng (T-115). Tôi thử lại độc lập các lối hỏng (lệnh trả lời lạ, bị sửa ngoài app, hẹn giờ quá gần, website đăng ngay thay vì hẹn giờ): phần mềm dừng đúng chỗ, câu báo cố định.
- **Một lỗi phải sửa trước khi bật Đăng ngay** (Soi Lỗi tìm ra, tôi đồng ý mức Trung bình): bật «Ghi SEO lên website» mà tiêu đề hay mô tả SEO đang bị «Chặn» ở bước SEO thì phần mềm bỏ ô đó, ghi phần còn lại rồi **vẫn đăng công khai** với tiêu đề/mô tả SEO mặc định. Chưa nguy hiểm hôm nay vì công tắc đang tắt.
- **Trước khi bật** còn cần: sửa lỗi trên, sửa hai câu README, và **buổi thử thật trên website cùng Chỉ Huy** (có mục kiểm cụ thể ở dưới, kể cả việc WordPress của bạn có tự đăng bài hẹn giờ đúng giờ không).
- Ba khe rất hẹp của cách so «giờ sửa bài» (ai đó sửa đúng trong cùng một giây với phần mềm…): tôi đồng ý ghi sổ rủi ro, không cần sửa. Muốn lợi dụng phải là người đã có tài khoản sửa/đăng bài trên website, tức người đó tự đăng được rồi.

## Trả lời câu hỏi của Chỉ Huy (03/11 08:05)

### 1a. Gộp `main` được khi công tắc tắt không? **Được ngay.**

- Mọi nhánh mã mới chỉ chạy khi hình thức gửi khác Nháp: `publish_panel` (`write.py:4073`) không vẽ nút gửi khi `release_enabled()` tắt; `send_draft` (`:3364`) xét lại lúc bấm (G2). Với Nháp, phần đổi chỉ là: `write_seo` ghi thêm `seo_ok` (`:2812`, chỉ đọc ở `release_missing`), `send_and_record` ghi thêm `featured_missing` (`:3633`), nhãn ô gửi lại cho Nháp giữ nguyên chữ cũ (`AGAIN_LABELS["draft"]`), `sent_message(saved, mode)` mặc định `"draft"`.
- T-115 chỉ đổi hành vi của `release_draft` (so `modified_gmt`); các lệnh tạo nháp, ảnh đại diện, ghi SEO chỉ **xin thêm** trường `modified_gmt` và nhớ nó. `_own_draft` không từ chối thêm ca nào (đánh dấu «không biết» chỉ chặn lệnh chuyển).
- Thử gộp: `git merge-tree --write-tree origin/main HEAD` **không xung đột** (cây `4f71527`); nhánh đã gộp đúng `7485b94` ở `5445028` nên cây gộp = nhánh (code không khác). `uv.lock`, `pyproject.toml` không đổi. Với `origin/main` mới `33dd87f` (12:35: thêm T-115, T-117, T-119, biên bản T-116 nhóm 1, 3, 4) cũng **không xung đột** (cây `c5d22c5`); phần `main` thêm là T-115 (đã có trên nhánh này), T-117 (`data/` là liên kết: `seo_app/images/data_dir.py`, `process.py`, `image_tags.py`, không đụng vùng này) và tài liệu.
- Test chọn lọc trên nhánh (mục «Kết quả công cụ quét»): **785 qua / 4 xfail (= SL-T112-1 ×2, SL-T112-2, SL-T112-3) / 0 hỏng / 0 XPASS**, 16 phút 18; **6.058 qua / 3 xfail (= SL-T106-1 ×2, SL-T108-1: README, Thấp, đã biết) / 0 hỏng / 0 XPASS**, 25 phút 58.

### 1b. Điều kiện **bắt buộc trước khi bật công tắc** (xem mục «Điều kiện», phần B)

### 1c. Cách lưu A (chỉ trong phiên) có đạt LC-T094-41 không? **Đạt.**

| Ý của LC-T094-41 / phiếu | Mã | Tôi kiểm |
|---|---|---|
| Mặc định tắt, không lưu ở đâu | Khóa `_release_enabled` chỉ trong `st.session_state`; không ghi `.env`, `config/`, `data/`, nháp | `grep` cả `app/`, `seo_app/`: chỉ `settings.py:720,724` ghi khóa này; `write.py:2855` chỉ đọc và đòi đúng `is True` (giá trị gần đúng `"true"`, `1` không bật: Soi Lỗi 6 ca) |
| Bật phải chủ ý | Tick «Tôi hiểu…» (`release_ack`) trước; nút bật bị khóa khi chưa tick; `_release_toggle_changed` còn đòi tick lần nữa (lớp chặn đôi); bỏ tick là tắt (`_release_ack_changed`) | Đọc mã + test Họa Sĩ (7 ca), Soi Lỗi (đột biến P9, P11) |
| Không bật được qua tham số địa chỉ, file nháp, ô nhập khác | Không chỗ nào đọc `st.query_params` cho khóa này; khuôn nháp chặt (`SendState`, `DraftSnapshot` không có trường công tắc); mỗi lần vẽ trang Cài đặt dựng lại hai ô theo công tắc thật | Soi Lỗi 2 ca tham số địa chỉ trên chính trang Soạn bài, 1 ca gán thẳng; Họa Sĩ 1 ca nháp sửa tay |
| Xét lại lúc bấm gửi (G2 Lá Chắn T-102) | `send_draft:3364` → `MSG_RELEASE_OFF_SEND`, 0 request | Test Họa Sĩ; đột biến P6 bị bắt |
| Có câu giải thích, nói rõ tắt app là tự tắt | `MSG_RELEASE_ON`, `MSG_RELEASE_OFF_HERE`, `MSG_RELEASE_OFF` | Đọc chữ |

Điểm còn lại là **mỗi tab trình duyệt một công tắc** (phiên Streamlit riêng): tắt ở tab B không tắt tab A. Đây là hệ quả tự nhiên của A, không phải khe: tab A vẫn phải chọn hình thức, xem lại, tick xác nhận, bấm gửi; và phiên nào cũng hết khi tải lại. README phải nói đúng (SL-T112-3). Tôi **không** đề nghị đổi sang lưu file: lưu file là thứ phương án A cố tránh (bật một lần rồi quên).

### 1d. Hẹn giờ mà SEO (hay phần khác) lỗi chỉ cảnh báo, người dùng quyết: **chấp nhận được**

- Đúng thiết kế T-094 mục 3 (chủ dự án đã duyệt khi gộp T-094): Đăng ngay khi SEO chưa ghi → **Chặn**; Hẹn giờ → **Cảnh báo**. Lý do của Họa Sĩ (mục 2.1) đúng: bài hẹn giờ chưa công khai, còn ít nhất 10 phút (thường là tới hôm sau) để sửa SEO trong trang quản trị, và app không hẹn giờ được nháp đã có nên chặn thì chỉ thêm việc, không an toàn hơn.
- Sau T-115, phạm vi «vẫn hẹn, cảnh báo» **hẹp lại**: lệnh đặt ảnh đại diện lỗi thì client coi là «không biết giờ sửa» và **không** hẹn giờ (bài vẫn nháp, câu `_RELEASE_CHANGED`). Chỉ còn ca **SEO** chưa lên (SiteSEO chưa cho ghi, lệnh ghi bị từ chối/5xx, trả lời lạ, hỏi lại sau Abilities không được) là vẫn hẹn giờ kèm `MSG_SCHEDULE_MISSING`. README đang viết ngược (SL-T112-2) → sửa.
- **Khuyến nghị không chặn:** cảnh báo hiện **một lần** ở kết quả gửi; `SendState` và dòng kế hoạch không ghi «SEO chưa lên», nên tải lại trang là hết nhắc. Nên ghi dấu đó vào nháp (hay cột ghi chú của dòng kế hoạch) để trang Bài viết / Kế hoạch còn nhắc tới giờ đăng. Làm ở phiếu sửa SL-T112-1 hoặc phiếu dọn sau.

### 2. Ba giới hạn của phép so `modified_gmt` (Lá Chắn T-115 Opus đề nghị ghi sổ rủi ro): **đồng ý, mức Thấp**

Tôi đọc lại mã T-115 trên nhánh này (`client.py:1358-1362`, `:1423-1430`, `:1462-1470`, `:1545-1550`, `:2139-2157`) và thử lại bằng WordPress giả (probe ca A10: `modified_gmt` khác → `_RELEASE_CHANGED`, 0 lệnh chuyển; A6: không đổi → vẫn chuyển). Ba giới hạn Opus nêu (sửa cùng giây; sửa đúng khe giữa lệnh đọc kiểm và lệnh ghi của app; sửa chỉ meta không đổi giờ sửa) là thật và **không bịt được từ phía client** (WordPress không có khóa lạc quan `If-Match`). Cả ba đòi một **tài khoản WordPress sửa được bài** đang sửa đúng bài nháp vừa tạo, trong vài giây của một cú bấm; tài khoản như vậy (Biên tập viên) tự đăng bài được rồi, nên khe không cho thêm quyền gì. Nội dung app gửi là nội dung người dùng đã xác nhận bằng mã băm. → **Thấp, ghi sổ rủi ro một dòng** như Opus đề nghị; không bắt buộc sửa trước khi bật. Thu hẹp rẻ cho khe thứ ba (tùy chọn, khi có phiếu đụng client): lệnh kiểm nháp xin thêm `featured_media` và so với ảnh app vừa đặt.

### 3. Vùng nhóm 2 và bảng đối chiếu Opus: xem [`T-116-la-chan-nhom-2.md`](T-116-la-chan-nhom-2.md)

## Lỗi phát hiện

Không có lỗi mới của Lá Chắn. Đánh giá lỗi Soi Lỗi ở mục dưới.

## Đánh giá lỗi Soi Lỗi

| Mã | Mức Soi Lỗi | Ý kiến Lá Chắn | Tôi kiểm |
|---|---|---|---|
| **SL-T112-1** · Đăng ngay vẫn đăng khi tiêu đề hay mô tả SEO đang «Chặn» | Trung bình | **Đồng ý Trung bình; sửa trước khi bật công tắc; không chặn gộp** (công tắc tắt thì không tới được). Cơ chế: `seo_request` (`write.py:2731`) bỏ trường bị Chặn (`None` → `""`), `package_seo` (`:2990`) đưa chuỗi rỗng vào gói (mã băm có `title=""`), `write_seo` (`:2799`) lấy `seo_ok = seo.written` mà client ghi **một phần** vẫn là `written=True`, `release_missing` (`:3766`) chỉ xét `seo_ok`; bộ dựng (`render.py:628`) chỉ Chặn Đăng ngay khi **tắt** «Ghi SEO». Người dùng có hai dấu hiệu (màn hình xác nhận hiện «Tiêu đề SEO: (trống)», chú thích «Sẽ không ghi…») nhưng nút không khóa; trái LC-T094-39 và yêu cầu 1 của phiếu. Mức bằng SL-T102-1 (cùng hậu quả, có báo trước) | Chạy 2 ca `xfail` của Soi Lỗi với `--runxfail`: hỏng đúng chỗ «lệnh đăng đã đi» (`[{'status': 'publish'}] == []`). Cách sửa gọn: bộ dựng thêm dòng **Chặn** khi `seo.write` và hình thức Đăng ngay mà tiêu đề hay mô tả SEO trống (nút khóa ngay ở màn hình xác nhận), **và** `release_missing` coi `skipped` có tiêu đề/mô tả là «SEO chưa lên» (chốt chặn thứ hai). Từ khóa chính bị bỏ: cảnh báo là đủ (không hiện công khai) |
| SL-T112-2 · README nói Hẹn giờ «vẫn hẹn» khi ảnh đại diện chưa lên | Thấp | Đồng ý; sửa cùng G1 (ca T-115 «bài bị sửa trong trang quản trị thì không hẹn giờ/đăng», câu «Website từ chối…» chưa đúng: app từ chối) | Đọc `README.md:487`, so với `test_schedule_with_featured_failure_is_refused_by_client` |
| SL-T112-3 · README nói tắt công tắc ở tab khác thì tab đang mở không gửi được | Thấp | Đồng ý (mục 1c) | Đọc `README.md:459`; cơ chế phiên Streamlit |

## Thử độc lập

- **Probe `probe_nhom2.py`** (WordPress giả của `tests/fake_wordpress.py`, không mạng; chi tiết ở biên bản nhóm 2): phần liên quan T-112/T-115 — A1 tạo nháp luôn `status=draft`; A2–A4 thân mang `status` khác `draft` không có dấu `_RELEASE`, 4 dấu giả, 7 khuôn lệnh chuyển sai: **chặn, 0 request**; A5 bài không phải của client: 0 request; A6 hẹn giờ đúng khuôn `{status, date_gmt}` và `_fields` cố định; A7 gọi lại trên bài đã chuyển: 0 request; A8 hẹn giờ mà website đăng ngay: câu KHẨN, đúng một lệnh chuyển; A9 hẹn giờ quá gần / đã qua / thiếu header `Date`: chặn **trước** lệnh chuyển, không «unsure»; A10 `modified_gmt` khác: `_RELEASE_CHANGED`, 0 lệnh chuyển. 41 PASS, 0 FAIL thật.
- **Test của phiếu**: `test_t112_release_rules.py` (13 ca), `test_t112_settings_switch.py` (7), `test_soi_loi_t112.py` (14 + 4 `xfail`), `test_t115_modified_gmt.py`, `test_soi_loi_t115.py` chạy trên nhánh (số liệu mục công cụ). Soi Lỗi còn thử đột biến 11 chỗ (10 bị bắt, 1 là lớp chặn đôi) — tôi không lặp lại.
- **Đọc mã** `release_post` (`write.py:3692-3763`): đường **duy nhất** gọi `release_draft` (grep cả `app/`, `seo_app/`: không chỗ nào khác); chạy sau ảnh đại diện và ghi SEO trên **cùng** client của lần bấm; mã bài lấy từ kết quả `create_draft_with_images` của chính lần đó, không từ nháp, Sheet hay website. Kết quả `unsure`/`went_public` ghi `SendState` (khóa gửi lại) trước khi lên trang; `record_plan` không ghi dòng kế hoạch khi `unsure` (G1); ca T-115 từ chối rõ ràng thì ghi «Đã gửi nháp» kèm mã bài — đúng sự thật, **đồng ý** cách Họa Sĩ/Chỉ Huy giữ (02/11 19:00).
- **Mã băm xác nhận** (LC-T094-38): `build_article` băm mode, `date_gmt`, tiêu đề, đoạn trích, slug, chuyên mục, thẻ, HTML từng phần, ảnh (băm byte, alt, chú thích, ảnh đại diện, GPS, thẻ ảnh), ba ô SEO và công tắc ghi SEO; `confirm_box` buộc tick vào đúng mã băm vừa vẽ; `send_draft` dựng lại gói với danh sách bài **tải lại** rồi so (`hmac.compare_digest`) trước lệnh ghi đầu tiên; còn dòng Chặn thì không gửi.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| W1 | Đạt | Công tắc mặc định tắt; chỉ `release_draft` gửi được `future`/`publish`, qua `release_post`; Đăng ngay thêm điều kiện ảnh đại diện + SEO đã lên; T-115 thêm điều kiện bài chưa bị sửa |
| W2 | Đạt | Không thêm lệnh ghi; chỉ xin thêm `modified_gmt`; vẫn chỉ bài/ảnh client vừa tạo |
| W3 | Đạt (không đổi) | Không đụng nội dung bài, bộ lọc |
| W4 | Đạt | Khóa gửi trùng (so rồi đặt) không đổi; Đăng ngay bị giữ ghi «đã gửi nháp» (không «không rõ»); lệnh chuyển không rõ → khóa |
| U1 | Đạt | Chữ mới đều hằng; nơi hiện qua `escape_markdown`; `MSG_PUBLISH_HELD` chỉ chèn chữ cố định và mã bài (số) |
| U2 | Đạt | `_RELEASE_CHANGED`, `MSG_RELEASE_OFF_SEND`, `MSG_PLAN_RELEASE_UNSURE`… không đường dẫn, không `WORDPRESS_URL`, không lời máy chủ |
| F3 | Đạt | Không `eval`, không đọc file mới |
| D1 | Đạt | Không thư viện mới; `uv.lock` không đổi so với `main` → pip-audit sáng 02/11 (69 gói, 0 lỗ hổng) còn hiệu lực |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test mới dùng WordPress giả (`fake_wordpress`), AppTest; bộ chặn mạng của `conftest` vẫn chạy |
| S1–S3, A1–A3, U3, F1, F2 | Không áp dụng | Phiếu không đụng bí mật, AI, đăng nhập, ảnh |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Dùng lại kết quả sáng 02/11 (lock không đổi so với `main`): 69 gói, 0 lỗ hổng | ✔ |
| bandit (`PYTHONUTF8=1`) | `seo_app/wordpress`, `seo_app/publish`, `seo_app/sanitize.py`, `app/views/write.py`, `settings.py`, `wordpress.py`: **0** | ✔ |
| detect-secrets (`PYTHONUTF8=1`, 14 file mã/test/README/báo cáo) | 2 «Basic Auth Credentials» báo nhầm: `client.py:1023` (chú thích ví dụ `htps://tên:mật-khẩu@site`, LC-T042-4 đã biết), `write.py:2493` (docstring `site_host` ví dụ `https://tên:mật-khẩu@…`) | ✔ |
| Soát lịch sử git `7485b94..b4f7900` | 0 mẫu mật khẩu ứng dụng / khóa API / khóa riêng | ✔ |
| ruff | `ruff check` các file đổi và file test của phiếu: sạch | ✔ |
| pytest chọn lọc, lô 1 (11 file: T-112, T-115, T-099, T-102, `test_wordpress_release`) | **785 qua / 4 xfail (= SL-T112-1 ×2, SL-T112-2, SL-T112-3) / 0 hỏng / 0 XPASS**, 16 phút 18 | ✔ |
| pytest chọn lọc, lô 2 (48 file vùng nhóm 2: client, bộ lọc, bộ dựng, gửi nháp, trang Kết nối) | **6.058 qua / 3 xfail (= SL-T106-1 ×2, SL-T108-1: README, Thấp, đã biết) / 0 hỏng / 0 XPASS**, 25 phút 58 | ✔ |

## Báo nhầm đã loại

- detect-secrets ×2 ở trên: chú thích/docstring ví dụ, không phải bí mật.
- Probe: 3 ca «FAIL» đều do tôi đặt kỳ vọng sai (`x < y` hợp lệ theo LC-T061-2; `[` trong `src` ảnh được escape thành `&#91;`; địa chỉ có tab cuối bị `strip()`), ghi ở biên bản nhóm 2.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay**, công tắc vẫn tắt. Chỉ Huy chạy toàn bộ test khi gộp.

**B. Bắt buộc trước khi bật công tắc Hẹn giờ / Đăng ngay** (một phiếu nhỏ cho 1–3, rồi buổi thử thật):

1. **Sửa SL-T112-1** (Họa Sĩ hoặc Thợ Máy; `app/views/write.py`, `seo_app/publish/render.py`): Đăng ngay có tiêu đề hay mô tả SEO bị Chặn/trống khi đang bật «Ghi SEO» → dòng **Chặn** ở màn hình xác nhận (nút khóa) **và** `release_missing` coi `skipped` tiêu đề/mô tả là SEO chưa lên; gỡ 2 `xfail` khi XPASS (chỉ xóa dấu, R5). Hẹn giờ: giữ cảnh báo.
2. **SL-T112-2, SL-T112-3, G1** (Thư Ký, `README.md` mục 11): Hẹn giờ mà ảnh đại diện lỗi thì **không** hẹn, bài vẫn nháp; chỉ SEO chưa lên mới «vẫn hẹn, cảnh báo»; mỗi tab một công tắc; ca «bài bị sửa trong trang quản trị sau khi app ghi thì app không hẹn giờ/đăng». Gỡ 2 `xfail` README khi XPASS.
3. **Khuyến nghị (không chặn):** ghi «SEO chưa lên» vào nháp / dòng kế hoạch để còn nhắc tới giờ đăng (mục 1d).
4. **Buổi thử thật LC-T094-44** (chủ dự án có mặt, Chỉ Huy làm, bài thử nháp rồi hẹn giờ xa, cuối cùng chuyển về nháp/xóa), kiểm và ghi vào báo cáo thử: (a) tài khoản `phan-mem-seo` có `publish_posts` (trang Kết nối báo); (b) ghi SEO qua Abilities có làm đổi `modified_gmt` không — nếu có thì Đăng ngay/Hẹn giờ kèm «Ghi SEO» sẽ **luôn** bị `_RELEASE_CHANGED` và cần phiếu client đọc lại giờ sửa sau lệnh SEO (điều kiện 4 của Lá Chắn T-115); (c) múi giờ website («Hồ Chí Minh»), giờ hẹn hiện đúng trong trang quản trị; (d) website dùng trình soạn nào (khối hay cổ điển: khe 3 của `modified_gmt`); (e) **WP-Cron có chạy bài hẹn giờ đúng giờ không** (hosting tắt `WP_CRON` mà không có cron hệ thống thì bài hẹn giờ kẹt «Lỡ lịch»): hẹn một bài thử 15 phút sau và xem nó tự đăng; (f) câu báo trên màn hình không lộ gì lạ; (g) hai việc thử thật còn nợ từ trước, làm luôn trong buổi này: nguồn trang ảnh của bài có `srcset="…webp 1x"` và điện thoại tải đúng file đầy đủ (T-059 điều kiện 2), tiêu đề SEO có «< 5 triệu» ghi lên hộp SiteSEO hiện đúng dấu «<» (T-091 điều kiện 4). Sau buổi thử, Thư Ký đọc lại README mục 11.
5. **Sổ rủi ro** `security.md` §6 (chủ dự án quyết, Thư Ký ghi): một dòng ba giới hạn `modified_gmt` (mục 2) — câu đề xuất ở biên bản Lá Chắn T-115 (điều kiện 3).
6. **Nên gộp T-118 (`client.showErrorDetails = "type"`) trước khi bật**: lỗi bất ngờ đúng lúc đăng thì trang chỉ hiện loại lỗi, không đường dẫn (chủ dự án chọn 02/11). Khuyến nghị, không bắt buộc.

**C.** Kiểm lại toàn vùng bằng Fable (T-116 nhóm 2): xong, biên bản riêng; 0 lỗi mới.

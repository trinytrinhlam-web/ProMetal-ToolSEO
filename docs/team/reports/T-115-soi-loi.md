# Báo cáo T-115 · Client WordPress: so `modified_gmt` ngay trước lệnh chuyển (LC-T094-23) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-115 `T-115-client-so-modified-gmt.md` (đọc ở checkout chính; nhánh này không chứa phiếu) |
| Nhánh | `team/T-115`, đầu nhánh `00bad96` (Thợ Máy, tách từ `d6df633`); thử gộp với `main` `4ee27d8` (có T-110 lượt 2–3; `origin/main` nay `c7a8df9` chỉ thêm tài liệu) và `main` cục bộ `935d381` (thêm T-113, T-105) |
| Ngày nộp | 2026-11-02 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5, dọn `test_soi_loi_t102.py`). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T115-1). **Không lỗi nào phải sửa trước Lá Chắn hay trước khi gộp** (công tắc Hẹn giờ/Đăng ngay đang tắt); nên sửa SL-T115-1 trước khi bật công tắc. R5 đúng phạm vi. Gộp `main`: không xung đột chữ, **1 ca T-110 của tôi phải thêm `,modified_gmt` khi gộp** (mục 9) |

## Tóm tắt (cho chủ dự án)

- **Phần kiểm «bài có bị sửa ngoài phần mềm không» chạy đúng.** Tôi dựng một website giả nhớ giờ sửa từng bài như WordPress (tính theo giây), rồi cho «người khác» sửa bài ở mọi lúc: ngay sau khi tạo nháp, giữa lúc đặt ảnh đại diện và ghi SEO, ngay trước khi hẹn giờ. Lần nào phần mềm cũng **không hẹn giờ, không đăng**, bài vẫn là nháp, câu báo cố định. Không ai sửa thì hẹn giờ, đăng ngay vẫn chạy.
- Thử 20 kiểu giờ sửa lạ website có thể trả (có múi giờ, có phần giây, chữ số lạ, rỗng, số, NaN, chuỗi rất dài…): đều không chuyển. Hai lần bấm, hai tab, hai bài tách nhau đúng.
- **1 lỗi nhỏ (Thấp):** nếu website trả lời **lạ** lệnh đặt ảnh đại diện hay ghi SEO (ví dụ nói về bài khác), phần mềm báo «chưa đặt được» nhưng vẫn hẹn giờ/đăng được. Chỉ gặp khi website trả lời sai; phía trang (T-112) cũng đang chặn trường hợp này. Sửa nhanh (dời một dòng).
- **Khi gộp vào `main`:** một test cũ của tôi (T-110) ghim danh sách trường xin website, phải thêm `modified_gmt` vào 3 chỗ. Không xung đột chữ nào khác.
- **Đã dọn:** test T-102 của tôi không còn tạo file `data/site_index.sqlite` trong thư mục dự án khi chạy.
- **Việc của bạn:** không có. Khi thử thật (Thợ Máy đã ghi): ghi SEO qua SiteSEO có làm đổi «giờ sửa cuối» của bài không.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t115.py` | Mới: 92 ca (82 qua, 10 `xfail(strict=True)` SL-T115-1). Website giả riêng `_ModSite` (adapter `requests`): đồng hồ riêng tính theo giây, mọi lệnh ghi REST vào bài đặt `modified_gmt` mới (`wp_update_post`), chỉ trả trường `_fields` xin, Abilities của SiteSEO chỉ đổi meta (hoặc đổi giờ theo tùy chọn), lối «sửa ngoài app». Ca giao diện cuối mượn khung bước Xuất bản của `test_t102_publish` như file T-102 của tôi |
| `tests/test_soi_loi_t102.py` | Commit riêng `3bb0838`: fixture tự động trỏ `DEFAULT_SITE_INDEX_FILE` sang thư mục tạm (như `test_t041_seo_ui.py`); trước đó chạy file này tạo `data/site_index.sqlite` ở thư mục dự án (ghi nhận Soi Lỗi T-109). 16 qua, 3 xfail như cũ; chạy xong không còn thư mục `data/` |
| `docs/team/reports/T-115-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu, không gọi website thật.

## Kiểm theo yêu cầu

### 1. Mọi đường tới `future`/`publish` qua phép so

- Chỉ `release_draft` gửi lệnh mang dấu chuyển (`_request(…, release=_RELEASE)`); trong hàm đó, mọi chỗ dùng `_RELEASE_CHANGED` đứng trước lệnh gửi (đọc mã nguồn bằng `ast`). Các đường khác không gửi được `status` (lớp chặn T-099 giữ nguyên).
- Không ai sửa: Đăng ngay và Hẹn giờ đều chuyển; lệnh kiểm ngay trước lệnh chuyển xin `id,status,modified_gmt`; đúng một lệnh chuyển, là lệnh cuối.
- Bị sửa ngoài app (bảng mục 2) ở **cả hai** hình thức: không chuyển.

### 2. Bị sửa ngoài app, biên giây

Website giả cho «người khác» lưu bài (`wp_update_post`: đổi nội dung, giờ sửa) 1 giây sau một bước; mỗi bước cách nhau 2 giây.

| Lúc sửa | Ghi SEO qua | Hình thức | Kết quả |
|---|---|---|---|
| Sau lệnh tạo nháp (trước ảnh đại diện) | meta, Abilities | Đăng ngay, Hẹn giờ | Không chuyển |
| Sau ảnh đại diện (trước ghi SEO) | meta, Abilities | Đăng ngay, Hẹn giờ | Không chuyển |
| Sau ghi SEO (trước lệnh chuyển) | meta, Abilities | Đăng ngay, Hẹn giờ | Không chuyển |

Mỗi ca (12): `ReleaseError` đúng câu `_RELEASE_CHANGED`, không `unsure`, không `went_public`; 0 lệnh chuyển, bài trên website vẫn `draft`; lệnh cuối là lệnh kiểm; **không trả mã bài**: gọi lại thì bị từ chối ngay («không phải bài client này tạo»), 0 lệnh. Hai lần sửa ở hai bước đầu không bị lệnh ghi sau của app «rửa» (lệnh đọc trước mỗi lệnh ghi đã đánh dấu «không biết»).

- **Biên giây:** lệnh ghi cuối của app lúc `…:00.9`, người khác sửa lúc `…:01.1` (cách 0,2 giây nhưng sang giây mới): bị bắt. Không ai sửa thì để 300 ngày vẫn hẹn giờ được.
- Sửa **cùng giây** với lệnh ghi cuối thì không phân biệt được (giới hạn Thợ Máy đã ghi; tôi thử lại: lệnh chuyển vẫn đi). Xem G1.

### 3. Giá trị lạ

- **Ở lệnh kiểm ngay trước lệnh chuyển** (20 dạng, đều lấy từ đúng giờ đã nhớ): thêm `+07:00`, thêm `Z`, thêm `.000`, dấu cách thay `T`, `t` thường, chữ số toàn góc, xuống dòng cuối, dấu cách đầu, chuỗi lặp 1.000 lần, rỗng, `0000-00-00T00:00:00`, số `0`, `1.5`, `NaN`, `Infinity`, `null`, `true`, danh sách, dict, thiếu khóa: **đều không chuyển** (`_is_date_gmt` chỉ nhận đúng `YYYY-MM-DDTHH:MM:SS` chữ số ASCII, so bằng từng chữ).
- **Ở lệnh ghi của app** (tạo, ảnh đại diện, meta × thiếu, rỗng, có múi giờ, số, NaN, danh sách, chuỗi dài = 21 ca): «không biết», không chuyển dù lệnh kiểm cuối trả đúng giờ.
- Mọi lệnh cùng trả một giá trị lạ giống nhau (`"x"`): không chuyển.

### 4. Ghi SEO qua Abilities

- Câu trả lời ability không có `modified_gmt`: client **giữ** giá trị nhớ từ lệnh ghi trước; SiteSEO chỉ đổi meta (như `update_post_meta`) thì hẹn giờ/đăng được. Ability được gọi đúng một lần, SEO lưu đúng chữ.
- Nếu SiteSEO **có** đổi giờ sửa khi ghi: không chuyển (hỏng theo hướng an toàn, như Thợ Máy viết). Cần kiểm ở lần thử thật (yêu cầu 4 của phiếu).

### 5. Lệnh ghi lỗi

| Lệnh | Lỗi | Kết quả |
|---|---|---|
| Ảnh đại diện (LC-T102-1 ở lớp client) | 500, 503 rỗng, 400, 403, hết giờ, mất mạng, 200 không phải JSON, lỗi lạ (8) | «Không biết»: không chuyển, kể cả khi website chưa đổi gì |
| Ảnh đại diện | đã chạy xong trên website nhưng mất câu trả lời (hết giờ) | Không chuyển |
| Meta (ghi SEO dự phòng) | 500, 502 HTML, hết giờ, 200 không phải JSON | Không chuyển |
| Meta | 400, 401, 403 (site không cho ghi khóa meta) | Giữ giá trị nhớ (website không đổi gì): chuyển được, đúng thiết kế |
| Lệnh đọc bài trước khi ghi ảnh đại diện | 500 | Lệnh ghi không gửi, website không đổi: chuyển được |
| Ảnh đại diện, meta | **trả lời lạ** (mã bài sai kiểu, bài khác, không còn nháp, thiếu trạng thái) mà mang đúng giờ sửa mới | **Vẫn chuyển**: xem **SL-T115-1** |

### 6. Hai client, hai tab, hai bài

- Hai client (hai lần bấm, hai tab): mỗi client nhớ riêng. Client B không chuyển được bài của client A (0 lệnh), không ghi được ảnh đại diện hay SEO vào bài đó (chặn trước khi gửi), nên không làm hỏng giá trị nhớ của A; A vẫn đăng được. Bài của B bị sửa ngoài app thì chỉ B bị từ chối.
- Một client, hai bài: bài bị sửa không kéo theo bài kia.

### 7. Trang Soạn bài (bước Xuất bản T-102)

Công tắc bật trong test, Hẹn giờ, tick xác nhận, gửi; lệnh kiểm ngay trước lệnh chuyển báo giờ sửa khác (ai đó vừa lưu bài): **0 lệnh chuyển**, trang hiện đúng câu `_RELEASE_CHANGED`, nháp ghi «đã gửi nháp, chưa hẹn giờ» (`released=False`, không «không rõ»), mã bài đúng.

### 8. R5

`git diff d6df633..00bad96 -- tests/`: 11 file test cũ, đúng ba lần duyệt, không ca nào nới.

| Duyệt | File: dòng (ở `00bad96`) |
|---|---|
| Thêm `,modified_gmt` vào chuỗi `_fields` mong đợi (10:55) | `test_shortcode_t061.py:273` (`POST_FIELDS`), `:508`, `:529`; `test_soi_loi_t054.py:621`, `:628`; `test_soi_loi_t061.py:315`, `:323` (dạng mã hóa URL `%2Cmodified_gmt`); `test_wordpress_seo_meta_t042.py:202`; `test_wordpress_release.py:148`; `test_soi_loi_t099.py:186`: **10 chuỗi**, cộng `test_soi_loi_t061.py:285` thêm `"modified_gmt"` vào `SAFE_FIELDS` (Chỉ Huy xác nhận 14:20). Tổng **11 chỗ**, khớp bảng Thợ Máy từng dòng (tin giao ghi «13 chỗ»: tôi đếm được 11, không thiếu chỗ nào ghim chuỗi cũ) |
| Thêm `modified_gmt` vào câu trả lời giả tạo/kiểm nháp (10:55) và lệnh ghi ảnh đại diện/meta (14:20) | `test_app_images.py:64` (hằng), `:1003-1004`, `:1006-1009`, `:1027-1028`; `test_la_chan_t099.py:39`, `:49-50`, `:67-68`, `:116-117`; `test_soi_loi_t099.py:54`, `:84-85`, `:92-93`, `:802-803`; `test_wordpress_release.py:59`, `:96-97`, `:124-125`, `:627-628`; `test_t102_publish.py:106-107`, `:114`; `test_soi_loi_t102.py:171`; `test_la_chan_t102.py:49`. Chỉ thêm một trường có giá trị hợp lệ; các ca cố ý thử câu trả lời lạ/thiếu (truyền `check=` riêng, `UNSURE_ANSWERS`, lệnh lỗi, lệnh không còn nháp) giữ nguyên. Hai ca «thiếu `Date`» (`test_la_chan_t099.py:116`) và «đồng hồ lệch» (`test_soi_loi_t102.py:171`) có thêm `modified_gmt` để vẫn thử đúng ý cũ (không bị phép so mới chặn trước) |
| Gỡ `xfail` LC-T102-1 (13:20) | `test_la_chan_t102.py`: xóa 4 dòng dấu, thân ca giữ nguyên; bỏ `import pytest` không còn dùng (ruff) |

Còn một chuỗi cũ ở `test_soi_loi_t042.py:429` (`id,status,title,link,featured_media`): ca đó không gửi lệnh nào (mọi `base_url` thử đều bị từ chối khi dựng client), nên kiểm không bao giờ chạy, không đỏ. Ghi lại để biết (G4).

### 9. Không lùi; gộp thử với `main` `4ee27d8`

- **Cây nhánh** (`00bad96` + dọn `3bb0838` + file test của tôi), **cả bộ test** (xem «Ghi chú về lượt chạy» dưới): 21.714 passed, 65 skipped, 57 xfailed, **0 failed**. 57 xfail đều có chủ đích (10 của SL-T115-1, còn lại của phiếu khác, có sẵn trên `d6df633`); 65 skipped là ca chỉ chạy trên Mac/Linux hay cần quyền symlink. Một lượt chạy song song khác trên cùng cây có thêm 1 lỗi dựng ca (`tmp_path` báo «not a normalized and relative path») ở `test_onpage_links.py`; chạy lại riêng file đó: 282 qua.
- **Gộp thử với ref `main` cục bộ `4ee27d8`** (T-110 lượt 2–3, T-109, T-114, T-078): `git merge-tree` **không xung đột chữ** (cây `4665a92`; hai bên cùng sửa `client.py`, `test_app_images.py`, `test_soi_loi_t054.py`, `test_soi_loi_t061.py`, `test_soi_loi_t099.py` ở chỗ khác nhau). Nhưng **1 ca đỏ sau khi gộp**: `test_soi_loi_t110.py::test_l2_lenh_tai_anh_xin_post_lenh_khac_giu_fields` (của tôi, T-110 lượt 2, chỉ có ở `main`) ghim đủ chuỗi `_fields` của 9 lệnh «Gửi nháp», trong đó lệnh tạo nháp, ảnh đại diện (`id,status,title,link,featured_media`) và lệnh đọc trước khi ghi (`id,status,meta`). Cùng kiểu đổi (1) đã duyệt: thêm `,modified_gmt` vào 3 chuỗi đó (2 biến `post` dùng chung một chuỗi, 1 chuỗi `GET`). Phải đổi lúc gộp (cần Chỉ Huy duyệt R5; tôi là chủ ca này, đồng ý). Các file T-110 khác trên cây gộp: 383 qua. Cả bộ test trên cây gộp `4ee27d8`: 22.188 passed, **2 failed**, 65 skipped, 53 xfailed. Hai ca đỏ: ca T-110 nói trên, và `test_pyasn1_version.py::test_pyasn1_da_cai_tu_ban_da_va` (venv của worktree T-115 còn `pyasn1` 0.6.4 theo `uv.lock` của nhánh; `main` đã nâng 0.6.5 ở T-114: `uv sync` theo khóa của `main` là qua, không phải lỗi lùi). Cùng một lượt chạy lặp lại: y hệt.
- **`main` cục bộ `935d381`** (thêm T-113, T-105; sửa `app/views/plan.py`, `home.py`, `wordpress.py`, `seo_app/plan/`, `seo_app/env_file.py`, không đụng `client.py`): gộp không xung đột (cây `6055be8`); test T-113, T-105, T-109 không ghim chuỗi `_fields` nào T-115 đổi (grep), nên không thêm ca đỏ nào ngoài ca T-110 trên. Không chạy lại test trên cây này.

### Đột biến

14 lượt (script `mutate115.py`), mỗi lần chạy `tests/test_soi_loi_t115.py`: **12/13 đột biến bị bắt, 1 tương đương**; bản «sửa thử» SL-T115-1 làm đúng 10 ca SL-T115-1 qua (XPASS) và không ca nào khác hỏng.

| Đột biến | Ca bắt đầu tiên |
|---|---|
| K1 bỏ phép so trước lệnh chuyển | `test_bi_sua_ngoai_app_…[sau-tao-publish-seo-meta]` |
| K2 «không biết» vẫn cho chuyển | như trên |
| K3 lệnh đọc trước lệnh ghi không so (bị «rửa») | như trên |
| K4 lệnh ghi sau xóa dấu «không biết» | như trên |
| K5 ảnh đại diện lỗi không đánh dấu | `test_lenh_anh_dai_dien_loi_…[500]` |
| K6 meta lỗi không đánh dấu | `test_lenh_ghi_meta_loi[500]` |
| K7 lệnh kiểm không xin `modified_gmt` | `test_khong_ai_sua_thi_chuyen_…[publish]` (website giả chỉ trả trường được xin) |
| K8 lệnh tạo, ảnh đại diện không xin `modified_gmt` | như trên |
| K9 lệnh đọc, meta không xin `modified_gmt` | như trên |
| K10 lệnh kiểm không kiểm dạng giờ | sống sót, **tương đương**: giá trị nhớ đã kiểm dạng, so bằng từng chữ |
| K11 nhận mọi chuỗi là giờ | `test_moi_lenh_cung_tra_mot_gia_tri_la_…` |
| K12 bị sửa thì vẫn trả mã bài | `test_bi_sua_ngoai_app_…[sau-tao-publish-seo-meta]` |
| K13 lệnh tạo không nhớ giờ | `test_khong_ai_sua_thi_chuyen_…[publish]` |
| F1 sửa thử SL-T115-1 (dời `_remember_modified` sau khi kiểm câu trả lời, đánh dấu «không biết» ở nhánh lạ) | 10 ca SL-T115-1 XPASS, 0 ca khác hỏng |

## Lỗi tìm ra

### SL-T115-1 · Thấp · Lệnh ghi ảnh đại diện/meta trả lời lạ: client vẫn nhớ giờ sửa từ câu trả lời đó

- **Chỗ:** `seo_app/wordpress/client.py`, `set_featured_image` và `_seo_via_meta`: `self._remember_modified(post_id, data)` chạy **trước** `if not _is_own_draft_answer(data, post_id)`. Câu trả lời lạ (mã bài sai kiểu `"42"`/`42.0`, bài khác `43`, trạng thái `pending`, thiếu trạng thái) vẫn được tin để nhớ giờ sửa, rồi hàm mới báo lỗi (`_IMAGE_ODD_ANSWER`, `_seo_error`).
- **Thử:** lệnh ghi chạy xong trên website (giờ sửa mới), câu trả lời lạ nhưng mang đúng giờ sửa mới; app báo «chưa đặt được ảnh đại diện» / ghi SEO hỏng; rồi `release_draft(mode="publish")`: **đăng công khai** (10/10 ca).
- **Hậu quả:** trái thiết kế của chính phiếu («mọi trường hợp không chắc… đều coi là «không biết»») và lời «T-115 chặn luôn LC-T102-1 ở lớp client» (ca `xfail` của Lá Chắn đã gỡ dựa trên lời này): lối «trả lời lạ» của lệnh ảnh đại diện vẫn đăng được ở lớp client. Chỉ gặp khi website trả lời sai; công tắc Hẹn giờ/Đăng ngay đang tắt; phía trang, T-112 (chưa gộp) cũng chặn Đăng ngay khi ảnh đại diện/SEO hỏng. **Thấp.**
- **Test:** `test_sl_t115_1_lenh_ghi_tra_loi_la_thi_khong_biet_khong_chuyen` (10 xfail: 2 lệnh × 5 kiểu trả lời).
- **Gợi ý:** ở cả hai hàm, kiểm `_is_own_draft_answer` trước; nhánh lạ gọi `_taint_modified(post_id)` rồi mới báo lỗi; chỉ `_remember_modified` khi câu trả lời đúng. Bản sửa thử F1 trên: đúng 10 ca này qua, không ca nào khác hỏng.

## Ghi nhận (không tính lỗi)

- **G1 · Khe cùng giây (Thợ Máy đã ghi).** Người khác sửa trong cùng giây với lệnh ghi cuối của app thì `modified_gmt` giống nhau, không phân biệt được; thử lại: lệnh chuyển vẫn đi.
- **G2 · Khe giữa lệnh đọc kiểm và lệnh ghi của app (chưa ghi).** Trước mỗi lệnh ghi (ảnh đại diện, SEO), app đọc bài để so; người khác lưu bài **đúng lúc giữa** lệnh đọc đó và lệnh ghi thì lệnh ghi của app đặt giờ sửa mới, client nhớ giờ đó, lần sửa kia bị «rửa»: thử bằng website giả, bài được đăng với nội dung người khác vừa sửa. Khe chỉ vài trăm mili giây, cùng loại với G1 và với khe sau lệnh ghi SEO Thợ Máy nêu; không bịt được nếu WordPress không có khóa lạc quan (`If-Match`). Nên ghi vào sổ rủi ro cùng G1.
- **G3 · Sửa chỉ meta không đổi giờ sửa (chưa ghi).** `modified_gmt` chỉ đổi khi bài đi qua `wp_update_post`. Sửa chỉ meta, ví dụ đặt ảnh đại diện bằng hộp chọn ảnh của trình soạn **cổ điển** (AJAX `set-post-thumbnail`, chưa bấm Lưu), hay plugin ghi khóa meta riêng, thì giờ sửa không đổi: thử bằng website giả, lệnh chuyển vẫn đi với ảnh đại diện người khác vừa đổi. Trình soạn khối (Gutenberg) lưu mọi thứ qua REST nên luôn đổi giờ. Đây là giới hạn của cách so `modified_gmt` (LC-T094-23); Lá Chắn cân nhắc ghi sổ rủi ro.
- **G4 · Chuỗi `_fields` cũ còn ở `test_soi_loi_t042.py:429`** trong một ca không gửi lệnh nào (xem R5); nếu ca đó gửi được lệnh thì sẽ đỏ, tức vẫn canh được.
- **G5 · `data/site_index.sqlite` sẵn có trong worktree `wt-T-115`** (do lượt chạy trước khi dọn tạo ra, file bị `.gitignore` bỏ qua): tôi để nguyên, không phải file tôi tạo.

## Lệnh đã chạy

- `pytest tests/test_soi_loi_t115.py`: 82 passed, 10 xfailed; `--runxfail` 10 ca SL-T115-1: hỏng đúng chỗ «không có `ReleaseError`» (lệnh chuyển vẫn đi).
- `pytest tests/test_soi_loi_t102.py` sau khi dọn: 16 passed, 3 xfailed, không tạo `data/`.
- Thử giới hạn (`probe_limits.py`): cùng giây, giữa đọc và ghi, sửa chỉ meta: cả ba lệnh chuyển vẫn đi (G1–G3).
- Cây nhánh (cả bộ test): 21.714 passed, 65 skipped, 57 xfailed, 0 failed. Cây gộp `main` `4ee27d8` (cả bộ test): 22.188 passed, 2 failed (ca T-110 phải đổi khi gộp; `pyasn1` của venv), 65 skipped, 53 xfailed.
- **Ghi chú về lượt chạy:** tôi định chạy bộ chọn lọc (114 file trên cây nhánh, 116 file trên cây gộp, chia 2 phần mỗi cây), nhưng gõ sai đường dẫn script chia phần và lỗi bị ẩn (đẩy vào `/dev/null`), nên không có file danh sách nào, `pytest` chạy **cả bộ test**: 4 lượt (2 trên mỗi cây, mỗi lượt khoảng 2 giờ 55 phút; lượt 31/10 cũng vậy và bị ngắt khi máy tắt), đúng lúc máy đang chạy toàn bộ test trên `main`. Trái lời dặn «chỉ chạy test chọn lọc», làm máy chậm thêm; lần sau tôi kiểm file danh sách có thật trước khi chạy. Kết quả vẫn dùng được (đủ hơn bộ chọn lọc).
- Đột biến: 12/13 bị bắt, 1 tương đương; F1 đúng 10 ca.
- `uv run ruff check .`: sạch. `detect-secrets` (`PYTHONUTF8=1`) trên file test, báo cáo: sạch (có file mồi tiếng Việt trong cùng lần quét: chỉ mồi bị báo).
- Script: thư mục ghi chú chung `T-115-soi-loi-scripts/` (`mutate115.py`, `probe_limits.py`).

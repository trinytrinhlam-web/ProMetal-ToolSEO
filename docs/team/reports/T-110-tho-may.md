# Báo cáo T-110 · Gắn ảnh «Gửi nháp» vào bài nháp (LC-T093-2, chủ dự án chọn 1A)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | T-110 (phiếu ở checkout chính, chưa vào nhánh này theo dặn của Chỉ Huy) |
| Ngày nộp | 2026-10-30 18:10 (giờ máy, +07) |
| Kết quả | Hoàn thành (chờ Soi Lỗi rút gọn, Lá Chắn rút gọn W2, W3, F1) |

## Tóm tắt (cho chủ dự án)

- Khi bấm «Gửi nháp», phần mềm nay **gắn từng ảnh vào chính bài nháp vừa tạo**. Vì vậy ảnh không còn hiện trong danh sách Media công khai của website (danh sách ai cũng xem được, không cần đăng nhập) cho tới khi bài được đăng.
- Đường dẫn trực tiếp tới file ảnh vẫn mở được nếu ai biết đường dẫn: WordPress không chặn file ảnh. Câu nhắc trên nút «Gửi nháp» đã sửa cho đúng điều này.
- Nếu gắn ảnh không được (mất mạng, website lỗi), bài nháp vẫn tạo xong như thường. Phần mềm báo rõ: ảnh có thể còn hiện trong danh sách Media, và cách kiểm trong trang quản trị. Không tải lại ảnh, không tạo bài thứ hai.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `create_draft_with_images`: ngay sau lệnh tạo nháp, **trước** lệnh kiểm nháp và đặt ảnh đại diện (hai lệnh đó vẫn là hai lệnh cuối như cũ), gọi `_attach_draft_images` gắn từng ảnh vừa tải vào bài nháp vừa tạo. `_attach_media` (mới): `POST /wp/v2/media/<mã>` thân **chỉ** `{"post": <mã bài>}`, `_fields=id,post`; chỉ ảnh trong `_uploaded_media_ids` (mới: ảnh chính client vừa tải, website xác nhận `201 Created`, thêm ở `_post_media` khi `new_only`) và bài trong `_created_post_ids`; câu trả lời phải đúng mã ảnh và `post` đúng mã bài (số nguyên thật). `DraftWithImages.unattached` (mới, mặc định rỗng). Lớp chặn hai tầng, đều **trước khi gửi**: `ALLOWED_JSON_KEYS` của `POST /wp/v2/media/<mã>` thêm `post`, nhưng `_is_media_attach` (mới, trong `_is_plain_request`) chỉ cho dạng thân đúng `{"post": <số nguyên dương ≤ 2⁶³−1>}` ở đúng đường đó; `_owns_attach` (mới, trong `_request`, theo điều kiện 2 của Chỉ Huy 30/10) đòi mã ảnh trên đường thuộc `_uploaded_media_ids` và mã bài thuộc `_created_post_ids` của chính client. Câu báo `_IMAGES_NOT_ATTACHED`, `_ATTACH_NOT_OWN`, `_ATTACH_ODD_ANSWER` |
| `app/views/write.py` | **Chỉ** câu `GPS_PUBLIC_WARNING`: ảnh và GPS xem được công khai qua đường dẫn trực tiếp ngay khi tải lên; phần mềm gắn ảnh vào bài nháp nên ảnh không hiện trong danh sách Media công khai cho tới khi bài đăng; gắn không được thì phần mềm báo sau khi gửi; không tự xóa ảnh. Giữ cụm «xem được công khai» mà test giao diện cũ tìm |
| `tests/test_la_chan_t093.py` | Gỡ 1 dấu `xfail` (LC-T093-2) khi XPASS, chỉ xóa dòng dấu |
| `tests/test_t110_gan_anh_vao_bai_nhap.py` (mới) | 52 test (mục «Test») |

## Đối chiếu yêu cầu phiếu

| Yêu cầu | Đáp ứng |
|---|---|
| 1. Gắn từng ảnh vào bài nháp vừa tạo, chỉ bài, ảnh của chính client; khóa `post` chỉ ở đúng đường này | `_attach_draft_images` → `_attach_media` (lệnh riêng sau khi tạo nháp: lúc ghi alt bài chưa có). Hai tập `_created_post_ids`, `_uploaded_media_ids` của chính đối tượng client. `_is_media_attach` trong `_is_plain_request`: `post` chỉ ở `POST /wp/v2/media/<mã>`, thân chỉ một khóa đó. `_owns_attach` trong `_request`: ảnh, bài phải của chính client, kể cả khi gọi thẳng `_request`. Các đường khác không có `post` trong `ALLOWED_JSON_KEYS` |
| 2. Lỗi khi gắn: không tải lại, không tạo bài trùng, câu báo cố định, giữ khóa gửi trùng | Lỗi ở một ảnh (mạng, 4xx, 5xx, 3xx, câu trả lời lạ, lỗi lạ): dừng, không thử lại, không tải lại, không ném lỗi; `create_draft_with_images` vẫn trả `DraftWithImages` (bài nháp đã có) với `unattached` và `message` = `_IMAGES_NOT_ATTACHED` (số ảnh; ảnh có thể còn trong danh sách Media công khai; kiểm Media → Thư viện; không cần gửi lại). App hiện `message` bằng `st.warning(escape_markdown(…))` sẵn có (`write.py:2972`); «đã gửi (mã bài)» ghi như cũ, nên khóa gửi trùng T-086, T-089 không đổi |
| 3. Ảnh đại diện, nội dung, `srcset` không đổi | Lệnh tạo nháp, `srcset`, ảnh đại diện giữ nguyên (`test_noi_dung_srcset_anh_dai_dien_khong_doi`); ảnh đại diện lỗi vẫn báo `_FEATURED_NOT_SET` như cũ, hai câu ghép nếu cả hai lỗi |
| 4. `GPS_PUBLIC_WARNING` | Như bảng «Đã thay đổi» |
| 5. Không lùi phiếu cũ | Mục «Hàm dùng chung, test cũ» |

## Test

| Test | Kiểm |
|---|---|
| `test_gan_tung_anh_vao_bai_nhap_truoc_anh_dai_dien` | Thứ tự đủ: tải ảnh, ghi alt (×2), tạo nháp, gắn ảnh (×2), kiểm nháp, ảnh đại diện; thân đúng `{"post": 42}`, `_fields=id,post`; `unattached` rỗng, `message` rỗng |
| `test_noi_dung_srcset_anh_dai_dien_khong_doi`, `test_khong_co_anh_thi_khong_gan_gi`, `test_mot_anh_dung_nhieu_lan_chi_gan_mot_lan` | Phần cũ không đổi; bài không ảnh: 0 lệnh gắn; một ảnh dùng hai chỗ: tải, gắn một lần |
| `test_gan_loi_thi_van_tra_bai_nhap_bao_cau_co_dinh` (13 ca) | 403, 400, 500, 302, hết giờ, mất mạng, không phải JSON, thiếu `post`, `post` 0, khác bài, dạng chữ, khác ảnh, danh sách: vẫn trả bài 42, ảnh đại diện vẫn đặt, `unattached == (101, 102)`, câu cố định (không mồi lời máy chủ, không `WORDPRESS_URL`), 1 lệnh gắn (không thử lại), 2 lệnh tải, 1 lệnh tạo |
| `test_gan_anh_sau_loi_thi_bao_dung_so_anh_chua_gan`, `test_loi_la_khi_gan_khong_thanh_loi_gui_nhap` | Ảnh thứ hai lỗi: chỉ báo 1 ảnh; lỗi lạ (`RuntimeError`) không thành lỗi gửi nháp |
| `test_anh_dai_dien_loi_va_gan_duoc_thi_chi_bao_anh_dai_dien`, `test_site_tao_bai_khong_phai_nhap_thi_khong_gan_anh` (5 ca), `test_bai_bi_dang_sau_luc_gan_thi_anh_dai_dien_bao_loi` | Ảnh đại diện lỗi 500: ảnh vẫn gắn; website trả bài vừa tạo không phải nháp (`publish`, `future`, `pending`, `private`, rỗng): 0 lệnh gắn, 0 lệnh sau lệnh tạo, báo cả hai; bài bị đăng sau lúc gắn: ảnh đã gắn, ảnh đại diện báo lỗi như cũ |
| `test_chi_gan_anh_client_vua_tai_vao_bai_client_vua_tao`, `test_anh_khong_duoc_xac_nhan_vua_tao_thi_khong_thanh_anh_cua_client` | Ảnh lạ, bài lạ, `True`, chữ, client khác: từ chối, 0 request; ảnh website trả mã khác 201 không vào tập |
| `test_khoa_post_chi_o_dung_dang_lenh_gan_anh` (16 ca), `test_lenh_gan_anh_dung_dang_cua_client_qua_lop_chan` | Ảnh, bài là của client mà `post` kèm khóa khác, kiểu sai, 0, âm, 2⁶³, số thực, `null`, mảng, `Post`, `post_parent`; ở đường tải ảnh, bài, tạo bài, ability: chặn trước khi gửi; đối chứng đúng dạng thì gửi |
| `test_lop_chan_chi_nhan_anh_va_bai_cua_chinh_client` (4 ca), `test_client_khac_khong_gan_duoc_anh_bai_cua_client_nay` | Điều kiện 2 của Chỉ Huy: gọi thẳng `_request` với ảnh không phải client tải, bài không phải client tạo, cả hai, mã ảnh thay mã bài, client khác: chặn, 0 request |
| `test_chi_attach_media_gui_khoa_post` | Đọc mã nguồn: dict khóa `"post"` chỉ trong `_attach_media` |
| `test_cau_nhac_gps_noi_dung_su_that_moi` | Câu nhắc mới có đủ ý |
| `tests/test_la_chan_t093.py::test_lc_t093_2_uploaded_images_attached_to_new_draft` | XPASS rồi gỡ dấu: ảnh 101 có bài cha 42 trên site giả nhớ bài cha |

## Hàm dùng chung, test cũ (yêu cầu 5)

| Chỗ sửa | Nơi gọi (grep `seo_app/`, `app/`, `tests/`, cả nhập muộn) | Ảnh hưởng |
|---|---|---|
| `create_draft_with_images` thêm lệnh gắn sau lệnh tạo | `app/views/write.py:2748` (`send_draft`); test của T-054, T-056, T-060, T-061, T-071, T-081, T-083, T-086, T-089, T-059 | 19 hàm test cũ ghim số lệnh, dãy lệnh, khóa: đã đổi kỳ vọng sau khi Chỉ Huy duyệt (bảng «Test cũ đã đổi») |
| `_request` thêm `_owns_attach` | mọi hàm client | Chỉ xét khi thân có khóa `post` (trước đây bị chặn ở mọi đường); `test_soi_loi_t085.py::test_khoa_json_theo_dung_duong` qua **không cần sửa**: `{"post": 1}` gọi thẳng vào ảnh 9 vẫn bị chặn vì không phải ảnh, bài của client |
| `_post_media` thêm ảnh vào `_uploaded_media_ids` khi `new_only` | `upload_media`, `create_draft_with_images` | Không đổi request, câu báo |
| `_is_plain_request`: luật `post` | `_request` | Chỉ thêm điều kiện khi thân có khóa `post` (trước đây bị chặn ở mọi đường) |
| `ALLOWED_JSON_KEYS` của `POST /wp/v2/media/<mã>` thêm `post` | `_is_plain_request` | `test_wordpress_t085.py::test_moi_duong_co_danh_sach_khoa_json_khong_co_id_name` vẫn đúng |
| `DraftWithImages` thêm `unattached` (mặc định rỗng, ở cuối) | `write.py` đọc `post`, `images`, `message` | Không đổi |
| `GPS_PUBLIC_WARNING` | `write.py:3069`; test `test_app_images.py:1112`, `test_la_chan_t056.py:189` tìm «xem được công khai» | Cụm này giữ nguyên |

### Test cũ đã đổi

Chỉ Huy duyệt 30/10 (R5), cả 3 nhóm A, B, C như đề nghị; không nới điều kiện nào khác. Mỗi chỗ sửa có chú thích «T-110 (Chỉ Huy duyệt 30/10)». Ca nhóm C của T-085 (`test_khoa_json_theo_dung_duong`) không phải sửa nữa (xem bảng trên).

| Nhóm | Ca (file::hàm) | Dòng cũ | Dòng mới |
|---|---|---|---|
| A | `test_app_images.py::test_send_draft_with_real_image`, `::test_send_ai_image_named_and_titled_as_ai`, `::test_marked_ai_image_sent_as_ai` | `(media,) = site.media_writes()` | `*writes, attach = site.media_writes()`; `assert attach == {"post": POST_ID}`; `(media,) = writes` |
| A | `test_soi_loi_t056.py::test_evil_ai_alt_stays_text_and_listed` | `(media,) = site.media_writes()` | như trên, với `ui.POST_ID` |
| A | `test_soi_loi_t061.py::test_moi_lenh_ghi_khong_con_ngoac_vuong_tran` (14 ca) | `assert methods.count(("POST", f"{MEDIA}/102")) == 1` | `… == 2`; lệnh cuối vào ảnh 102 có thân đúng `{"post": 42}` |
| A | `test_soi_loi_t081.py::test_gui_site_gia_alt_chu_thich_dung_chu_khong_gach_cheo` (6 ca), `::test_gui_site_gia_shortcode_link_the_sau_tien_to_van_bi_vo_hieu` (18 ca), qua hàm phụ `_sent` | `assert len(posts) == 1 and len(writes) == 1` | `assert len(posts) == 1 and len(writes) == 2 and writes[1] == {"post": 42}` (lệnh ghi alt vẫn là `writes[0]`) |
| A | `test_soi_loi_t083.py::test_gui_site_gia_tien_to_kieu_moi_van_vo_hieu_shortcode` (3 ca) | `assert len(posts) == 1 and len(writes) == 1` | như trên |
| A | `test_t081_alt_gach_cheo.py::test_bo_gach_cheo_khong_mo_lai_shortcode_hay_link` (8 ca), `::test_gui_site_gia_alt_chu_thich_anh_ai_khong_gach_cheo` (5 ca), qua hàm phụ `_send_ai_image` | `assert len(writes) == 1` | `assert len(writes) == 2 and writes[1] == {"post": 42}` |
| A | `test_shortcode_t061.py::test_nhap_kem_anh_alt_chu_thich_va_truong_media_khong_con_shortcode` (10 ca) | `[describe] = posts_of(fake_wp, "POST", f"{MEDIA}/101")` | `[describe, attach] = …`; `assert body(attach) == {"post": 42}` |
| B | `test_shortcode_t061.py::test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung` | `expected` là dict (đường → `_fields`), so dãy đường rồi so `_fields` theo dict | `expected` là danh sách (phương thức, đường, `_fields`), thêm `("POST", f"{MEDIA}/101", {"_fields": ["id,post"]})` sau lệnh tạo; so cả dãy một lần. Vòng kiểm «không `content`, `excerpt`, `description`, `caption`» giữ nguyên |
| B | `test_soi_loi_t060.py::test_moi_lenh_that_cua_app_van_di_ra[create_draft_with_images]` | `("POST", POSTS, ["_fields"]), ("GET", f"{POSTS}/42", …)` | chèn `("POST", f"{MEDIA}/101", ["_fields"])` giữa hai mục đó |
| B | `test_soi_loi_t061.py::test_lenh_ghi_dung_nguyen_dia_chi_ke_ca_truy_van` | dãy 5 lệnh | chèn `("POST", f"{MEDIA}/101" + "?_fields=id%2Cpost")` sau lệnh tạo |
| B | `test_wordpress_images.py::test_thu_tu_lenh_va_moi_duong_trong_danh_sach` | dãy 7 lệnh | chèn `("POST", f"{MEDIA}/101")`, `("POST", f"{MEDIA}/102")` sau lệnh tạo; `body(requests[-1]) == {"featured_media": 102}`, `result.message == ""` giữ nguyên |
| C | `test_soi_loi_t054.py::test_moi_lenh_deu_qua_danh_sach_duong_khong_tham_so_la` | nhánh `elif path(request).startswith(MEDIA): assert query == {"_fields": ["id,source_url,alt_text"]}` | thêm nhánh trước: lệnh vào `MEDIA/<mã>` có thân đúng `{"post": 42}` thì `query == {"_fields": ["id,post"]}` |
| C | `test_soi_loi_t061.py::test_moi_lenh_ghi_wp_v2_deu_co_fields_an_toan` | `assert len(writes) == 8`; `SAFE_FIELDS` không có `post` | `assert len(writes) == 9` (thêm lệnh gắn); `SAFE_FIELDS` thêm `post` (chỉ test này dùng) |
| C | `test_wordpress_images.py::test_khong_bao_gio_publish_future_va_chi_gui_truong_can_thiet` | mọi lệnh vào Media: `set(data) <= {"alt_text", "title", "caption"}` | lệnh vào Media có thân đúng `{"post": 42}` thì bỏ qua kiểm khóa ghi alt (kiểm «không `publish`, `future`, `status`» phía trên vẫn chạy cho lệnh đó) |

## Bằng chứng

```
$ uv run pytest -q -p no:cacheprovider -rX tests/test_la_chan_t093.py   # trước khi gỡ dấu
[XPASS(strict)] LC-T093-2: ảnh gửi nháp không gắn vào bài nháp, REST liệt kê công khai

$ uv run pytest -q -p no:cacheprovider <44 file test liên quan>      # trước khi sửa test cũ
77 failed, 6013 passed, 9 xfailed                # đúng 19 hàm ở bảng «Test cũ đã đổi»

$ uv run pytest -q -p no:cacheprovider tests/test_t110_gan_anh_vao_bai_nhap.py \
      tests/test_la_chan_t093.py tests/test_soi_loi_t085.py
795 passed, 1 xfailed                            # xfail: LC-T093-3, không thuộc phiếu

$ uv run pytest -q -p no:cacheprovider <44 file liên quan> tests/test_t110_gan_anh_vao_bai_nhap.py
6142 passed, 9 xfailed in 2191.63s (0:36:31)     # 30/10 17:30 → 18:06, máy đang chạy toàn bộ test

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan <4 file của phiếu>
2 «Basic Auth Credentials» ở hai dòng chú thích ví dụ «tên:mật-khẩu@…» có từ trước
(client.py từ 23/10, write.py từ 27/10, git blame), không phải khóa thật, phiếu này không sửa.
```

44 file liên quan: mọi file test có `create_draft_with_images`, `send_draft`, «Gửi nháp», `/wp/v2/media`, `upload_media`, `_post_media` (client WordPress, gửi nháp kèm ảnh T-054, T-056, T-071, T-081, T-083, T-086, T-089, chặn shortcode T-061, lớp chặn T-060, T-085, T-088, `srcset` T-059, kiểm của Soi Lỗi, Lá Chắn). 9 xfail có từ trước, không thuộc phiếu.

**Thử «làm hỏng» code** (sửa tạm, chạy `test_t110_gan_anh_vao_bai_nhap.py`, `test_la_chan_t093.py`, trả nguyên file; script so lại: giống hệt):

| Làm hỏng | Số test đỏ |
|---|---|
| Không gắn ảnh | 24 |
| `_attach_media` không kiểm ảnh của client | 1 |
| `_attach_media` không kiểm bài của client | 1 (lớp `_owns_attach` vẫn chặn) |
| Không kiểm `post` trong câu trả lời | 4 |
| Luật dạng thân `post` lỏng (cho kèm khóa khác) | 1 |
| Gắn lỗi vẫn thử ảnh sau | 20 |
| Bỏ `_owns_attach` ở `_request` | 5 |
| `_owns_attach` chỉ kiểm bài, không kiểm ảnh | 1 |
| Ảnh tải không đòi «vừa tạo» cũng thành ảnh của client | 1 |

## Rủi ro và điểm cần chú ý

1. **Chưa thử trên website thật.** Theo mã WordPress lõi: lệnh sửa ảnh nhận `post`, cần quyền sửa bài cha (Biên tập viên có), câu trả lời có `post`. Khi bài cha là nháp, `check_read_permission` không cho người chưa đăng nhập đọc ảnh, nên danh sách Media công khai bỏ ảnh đó. Nên kiểm ở lượt thử thật: gửi một nháp, mở `https://<site>/wp-json/wp/v2/media` ở cửa sổ ẩn danh, ảnh vừa gửi không có trong danh sách.
2. **Ảnh của lần gửi hỏng trước khi tạo nháp** (`DraftImagesError`, ảnh đã lên mà chưa có bài) vẫn không có bài cha, nên vẫn hiện trong danh sách Media công khai. Câu báo cũ `_DRAFT_IMAGES_LEFT` chỉ nói «xem được công khai qua đường dẫn». Ngoài phạm vi phiếu (yêu cầu chỉ nói lỗi khi gắn); đề xuất phiếu sau sửa câu báo cho đủ ý.
3. Bài nháp được đăng sau (trong trang quản trị) thì ảnh đã gắn sẽ hiện trong danh sách Media công khai: đúng ý thiết kế («cho tới khi bài đăng»).
4. Nhánh này tách từ `main` `fd28bbc`, chưa có T-099 lượt 2 (sửa cùng `_is_plain_request`, đoạn khác: luật `data`). Khi gộp, hai chỗ sửa nằm ở các dòng khác nhau; Chỉ Huy nên chạy lại test client khi gộp cả hai.

## Đề xuất

- Lượt thử thật (Chỉ Huy, chủ dự án): kiểm như «Rủi ro» 1.
- Phiếu sau: `_DRAFT_IMAGES_LEFT` nói thêm ảnh của lần gửi hỏng có thể hiện trong danh sách Media công khai («Rủi ro» 2).

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-30): LC-T110-1, SL-T110-1

Theo biên bản Lá Chắn `T-110-la-chan.md` (ĐẠT CÓ ĐIỀU KIỆN, `7497a4f`) và Soi Lỗi `T-110-soi-loi.md` (ĐẠT CÓ ĐIỀU KIỆN, `f85b2bb`), làm trước khi đóng Giai đoạn 3. Nhánh đã gộp `main` cục bộ `eef13b5` trước khi sửa (fast-forward: có T-099 lượt 2, T-107 lượt 3, T-101). Chỉ Huy chọn cách **A** lúc 20:40: chỉ gắn khi website trả `post` null/0; thiếu hay lạ thì không gắn.

### Tóm tắt (cho chủ dự án)

- Lệnh tải ảnh nay hỏi website thêm một thông tin: ảnh đó đã thuộc bài nào chưa. Ảnh mới tải thì chưa thuộc bài nào: phần mềm gắn vào bài nháp như lượt 1.
- Nếu website trả lại một ảnh **có sẵn**, đang thuộc bài khác (chỉ xảy ra khi plugin lạ trả lời sai), phần mềm **không đụng** tới ảnh đó: không ghi alt, không chuyển ảnh sang bài nháp, dừng gửi và báo lỗi như khi website không xác nhận tạo ảnh mới.
- Website không nói rõ ảnh thuộc bài nào: phần mềm không gắn và báo «chưa gắn được» kèm cách kiểm.
- Lần gửi hỏng trước khi tạo được nháp: câu báo nay nói rõ ảnh đã tải đang hiện công khai trong danh sách Media của website, và cách kiểm, xóa (Media → Thư viện). Câu nhắc trên nút «Gửi nháp» cũng nói điều này.

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | **LC-T110-1:** `_MEDIA_UPLOAD_FIELDS = "id,source_url,alt_text,post"` (riêng cho lệnh tải ảnh; lệnh ghi alt vẫn `_MEDIA_FIELDS`). `_post_media` (khi `new_only`): `post` là số nguyên dương (`_positive_id`, ≤ 2⁶³−1) → `WordPressError(_MEDIA_NOT_CREATED)`, như mã khác 201: không ghi alt, không gắn, không tạo nháp; `post` là `None` hay số nguyên `0` → ảnh của client (`_uploaded_media_ids`); thiếu khóa (`_NO_PARENT_FIELD`) hay giá trị lạ (chữ, `bool`, âm, số thực, quá 2⁶³−1, mảng…) → không vào tập, các bước khác như cũ, lệnh gắn bị `_attach_media`/`_owns_attach` từ chối, kết quả có `unattached` và câu `_IMAGES_NOT_ATTACHED`. **SL-T110-1:** `_DRAFT_IMAGES_LEFT` nói ảnh chưa gắn vào bài nào nên đang hiện công khai trong danh sách Media (kể cả GPS), không tự xóa, cách xóa; `_DRAFT_IMAGE_MAYBE` thêm «nếu có, ảnh đó … đang hiện công khai trong danh sách Media, hãy xóa nếu không dùng» |
| `app/views/write.py` | **Chỉ** 3 câu: `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED` thêm «ảnh chưa gắn vào bài nào thì đang hiện công khai trong danh sách Media (kể cả vị trí GPS)… (xóa ảnh không dùng)»; `GPS_PUBLIC_WARNING` thêm «lần gửi hỏng trước khi tạo được nháp cũng báo, vì ảnh đã tải khi đó chưa gắn vào bài nào nên hiện trong danh sách này». Giữ nguyên mọi cụm chữ test cũ đang tìm («xem được công khai», «Lần gửi trước bị ngắt giữa chừng», «có thể vẫn đã lên thư viện Media», «gắn không được thì phần mềm báo»…), nên **không** phải đổi test nào ghim câu báo |
| `tests/test_la_chan_t110.py` | Gỡ 1 dấu `xfail` (LC-T110-1), chỉ xóa dòng dấu |
| `tests/test_soi_loi_t110.py` | Gỡ 1 dấu `xfail` phủ 3 ca (SL-T110-1), chỉ xóa dòng dấu; thêm `"post": None` ở site giả (bảng dưới) |
| `tests/test_t110_gan_anh_vao_bai_nhap.py` | Thêm 19 ca (mục «Test mới») |
| 10 file test khác | Thêm `"post": None` ở câu trả lời tải ảnh của site giả; 4 file đổi chuỗi `_fields` của lệnh tải ảnh (hai bảng dưới) |

Trước khi gỡ dấu: chạy `-rX`, đủ 4 ca XPASS(strict) (1 LC-T110-1, 3 SL-T110-1).

### Test cũ đã đổi: site giả trả `"post": None` (Chỉ Huy duyệt 30/10 20:40, cách A)

WordPress thật, khi `_fields` có `post`, trả `"post": null` cho ảnh vừa tải. Mỗi chỗ chỉ thêm khóa đó vào câu trả lời lệnh tải ảnh (`POST /wp/v2/media`); không đổi hay bỏ kiểm nào. Các site chỉ dùng cho `upload_media` đứng riêng (không gắn ảnh) không phải sửa.

| File | Dòng | Cũ → mới |
|---|---|---|
| `tests/test_app_images.py` | 1012 (`Site.create_media`) | `{"id": media_id, "source_url": f"{UPLOADS}{name}"}` → thêm `"post": None` |
| `tests/test_soi_loi_t054.py` | 185 (`Site.create_media`, dùng chung cho T-093, T-110…) | `{"id": media_id, "source_url": self.source_url(media_id)}` → thêm `"post": None` |
| `tests/test_soi_loi_t071.py` | 224 (`Site.create_media`) | như trên |
| `tests/test_shortcode_t061.py` | 324–325 (`create_media` trong `site`) | `return (201, {"id": …, "source_url": …}, {})` → `answer = {…, "post": None}`; `return (201, answer, {})` (tách dòng vì độ dài) |
| `tests/test_soi_loi_t061.py` | 166–167 (`create_media` trong `site`) | như trên |
| `tests/test_t081_alt_gach_cheo.py` | 93 (`create_media`) | thêm `"post": None` |
| `tests/test_wordpress_images.py` | 199–201 (`Site.create_media`) | `answer = {"id", "source_url", "mime_type"}` → thêm `"post": None` (tách dòng) |
| `tests/test_soi_loi_t081.py` | 293 (`site`) | `(201, {"id": FIRST_ID, "source_url": url}, {})` → thêm `"post": None` |
| `tests/test_soi_loi_t083.py` | 338 (`site`) | như trên |
| `tests/test_soi_loi_t060.py` | 656 (`real_site.created_media`) | thêm `"post": None` |
| `tests/test_soi_loi_t110.py` | 80–81 (`_ParentSite._answer`, lệnh tải) | `201, {"id", "source_url", "alt_text": ""}` → thêm `"post": None` |

### Test cũ đã đổi: `_fields` của lệnh tải ảnh (Chỉ Huy duyệt 30/10 20:25)

Chỉ đổi chuỗi mong đợi của **lệnh tải** (`POST /wp/v2/media`) từ `id,source_url,alt_text` thành `id,source_url,alt_text,post`; lệnh ghi alt (`/media/<mã>`) giữ chuỗi cũ. Các file khác có chuỗi `_fields` của Media (ghim lệnh ghi alt, hay gọi thẳng `_request` với `_fields` tự đặt) vẫn qua, không sửa.

| Ca | Cũ | Mới |
|---|---|---|
| `test_la_chan_t060.py::test_lc_t060_doi_chung_than_json_va_fields_that_cua_app_van_gui` | `("POST", "/wp/v2/media", None, [_MEDIA_FIELDS])` | `… [_MEDIA_UPLOAD_FIELDS]` (thêm nhập `_MEDIA_UPLOAD_FIELDS`) |
| `test_shortcode_t061.py::test_upload_media_truong_media_khong_con_shortcode` | `assert query(upload) == MEDIA_FIELDS` | `== UPLOAD_FIELDS` (hằng mới `{"_fields": ["id,source_url,alt_text,post"]}`); `query(update) == MEDIA_FIELDS` giữ |
| `test_shortcode_t061.py::test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung` | `("POST", MEDIA, MEDIA_FIELDS)` | `("POST", MEDIA, UPLOAD_FIELDS)` |
| `test_soi_loi_t054.py::test_moi_lenh_deu_qua_danh_sach_duong_khong_tham_so_la` | nhánh `path.startswith(MEDIA)` → `id,source_url,alt_text` cho cả lệnh tải | thêm nhánh trước: `path == MEDIA` → `id,source_url,alt_text,post`; nhánh lệnh ghi alt giữ |
| `test_soi_loi_t061.py::test_lenh_ghi_dung_nguyen_dia_chi_ke_ca_truy_van` | `("POST", MEDIA + media_fields)` | `("POST", MEDIA + media_fields + "%2Cpost")` |

### Test mới (lượt 2), trong `tests/test_t110_gan_anh_vao_bai_nhap.py`

| Test | Kiểm |
|---|---|
| `test_lenh_tai_anh_xin_them_post` | Mọi lệnh tải ảnh có `_fields=id,source_url,alt_text,post` |
| `test_post_null_hay_0_thi_gan` (2 ca) | `post` `None`, `0`: gắn đủ 2 ảnh vào bài 42, không câu báo |
| `test_thieu_post_thi_khong_gan_bao_cau_co_dinh` | Thiếu `post`: 0 lệnh gắn; bài nháp, ảnh đại diện, lệnh ghi alt như cũ; `unattached == (101, 102)`; câu `_IMAGES_NOT_ATTACHED` |
| `test_post_so_duong_la_anh_co_san_tu_choi_nhu_ma_khac_201` (3 ca: 7, 1, 2⁶³−1) | `DraftImagesError` bắt đầu bằng `_MEDIA_NOT_CREATED`; 0 lệnh ghi alt, 0 lệnh tạo nháp, dừng ngay ảnh đầu |
| `test_post_so_duong_o_upload_media_rieng_cung_tu_choi` | `upload_media` đứng riêng: ảnh có bài cha 7 → lỗi, không lệnh nào ghi vào ảnh đó |
| `test_post_sai_kieu_thi_khong_gan` (11 ca) | `"7"`, `""`, `"0"`, `True`, `False`, `-1`, `1.5`, `0.0`, 2⁶³, `[7]`, `{"id": 7}`: 0 lệnh gắn, câu báo cố định |

### Bằng chứng (lượt 2)

```
$ uv run pytest -q -p no:cacheprovider -rX tests/test_la_chan_t110.py tests/test_soi_loi_t110.py \
      tests/test_t110_gan_anh_vao_bai_nhap.py                      # trước khi gỡ dấu
4 XPASS(strict): 1 LC-T110-1, 3 SL-T110-1

$ uv run pytest -q -p no:cacheprovider tests/test_t110_gan_anh_vao_bai_nhap.py \
      tests/test_la_chan_t110.py tests/test_soi_loi_t110.py tests/test_la_chan_t093.py
142 passed

$ uv run pytest -q -p no:cacheprovider <85 file chọn lọc>        # 30/10 22:27 → 23:19
5 failed, 8724 passed, 1 skipped, 3 xfailed in 3116.96s (0:51:56)
                                       # 5 ca đều ghim `_fields` lệnh tải ảnh (bảng trên)
$ uv run pytest -q -p no:cacheprovider tests/test_la_chan_t060.py tests/test_shortcode_t061.py \
      tests/test_soi_loi_t054.py tests/test_soi_loi_t061.py      # sau khi đổi chuỗi `_fields`
311 passed

$ uv run ruff check .
All checks passed!
```

85 file chọn lọc: mọi file test có `create_draft_with_images`, `send_draft`, «Gửi nháp», `upload_media`, `_post_media`, `/wp/v2/media`, `fake_wp`, `FakeWordPress`, `wordpress.client`, `GPS_PUBLIC_WARNING`, `MSG_SEND_`, cộng `test_wordpress_release.py`, `test_la_chan_t099.py`, `test_soi_loi_t099.py`, `test_t089_send_draft.py`, `test_t086_send_state.py`. Gồm client WordPress, «Gửi nháp», T-054, T-059, T-060, T-071, T-085, T-086, T-088, T-089, T-091, T-099, T-110 (T-102 chưa có ở `main`). 3 xfail có từ trước (SL-T106-1 ×2, SL-T108-1), không thuộc phiếu.

Thử «làm hỏng» code (sửa tạm, chạy 3 file test T-110, trả nguyên file; script so lại: giống hệt):

| Làm hỏng | Số test đỏ |
|---|---|
| Lệnh tải không xin `post` | 1 |
| Nhận ảnh có bài cha (bỏ lệnh từ chối) | 4 |
| Thiếu `post` coi như `null` (cách B) | 1 |
| Nhận mọi giá trị `post` lạ | 12 |
| Nhận `False` như `0` | 2 |

### Còn lại

- Ghi nhận G2 của Soi Lỗi (giữa lúc tải ảnh và lúc gắn, vài giây tới vài phút, ảnh vẫn trong danh sách công khai): không đổi, như biên bản.
- Kiểm trên website thật như «Rủi ro» 1 của lượt 1: thêm một ý, trang `wp-json/wp/v2/media` mở ở cửa sổ ẩn danh sau khi gửi nháp không có ảnh vừa gửi.

---

## Lượt 3 (2026-10-31): SL-T110-2, SL-T110-3, G4

Theo mục «Lượt 2» trong `T-110-soi-loi.md` (Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN, `f0ff53a`) và quyết định G4 của Chỉ Huy (chặt hơn). Nhánh đã gộp `main` cục bộ `3cdd096` trước khi sửa (có T-102), không xung đột.

### Tóm tắt (cho chủ dự án)

- Website trả lại một ảnh có thể là ảnh **có sẵn** (thuộc bài khác) thay vì ảnh mới: câu báo nay chỉ dặn **kiểm tra** Media → Thư viện, nói rõ ảnh đó có thể đang thuộc bài khác nên để nguyên. Trước đây câu báo bảo «xóa nếu không dùng», dễ làm xóa nhầm ảnh của bài đã đăng.
- Website không cho biết ảnh vừa tải là ảnh mới hay ảnh có sẵn: phần mềm nay **dừng**, không ghi gì vào ảnh đó (trước đây vẫn ghi alt). WordPress chuẩn luôn cho biết, nên lúc gửi bình thường không đổi gì.
- Mở lại một bài «gửi dở» ở lần mở app sau: câu khóa nay nói thêm ảnh đã tải mà chưa gắn vào bài nào đang hiện công khai trong danh sách Media, và cách kiểm, xóa.

### Đã thay đổi (lượt 3)

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | **G4:** `_post_media` (khi `new_only`) nay chỉ nhận `post` là `None` hay số nguyên `0`; thiếu khóa hay giá trị lạ → `_ReturnedMediaError(_MEDIA_PARENT_UNKNOWN)`, như số dương: không ghi alt, không gắn, không tạo nháp. Áp cho cả «Gửi nháp» (`create_draft_with_images`) lẫn `upload_media` đứng riêng (Chỉ Huy chọn cách A 31/10 08:55: hai đường không lệch nhau). **SL-T110-2:** lớp lỗi riêng `_ReturnedMediaError` cho mọi trường hợp lệnh tải ảnh không xác nhận được là ảnh mới (mã khác 201: `_MEDIA_NOT_CREATED` giữ nguyên chữ; ảnh có bài cha: câu mới `_MEDIA_HAS_PARENT`, không còn «cần mã 201»; không rõ bài cha: `_MEDIA_PARENT_UNKNOWN`). `_draft_images_error(…, returned_media=…)`: lỗi loại này nối đuôi mới `_DRAFT_IMAGE_RETURNED` (chỉ dặn kiểm, ảnh đang thuộc bài khác thì để nguyên, ảnh mới chưa gắn nếu có thì đang hiện công khai trong danh sách Media; không có chữ «xóa»). Lỗi mạng, 5xx, câu trả lời hỏng ở lệnh tải ảnh giữ đuôi `_DRAFT_IMAGE_MAYBE` của lượt 2 |
| `app/views/write.py` | **Chỉ** câu `unsure_message` (khóa «gửi dở», SL-T110-3): thêm «Ảnh đã tải lên mà chưa gắn vào bài nào thì đang hiện công khai trong danh sách Media (kể cả vị trí GPS)… (xóa ảnh không dùng)». Giữ cụm «bài nháp có thể đã có trên website» mà các test T-086, T-089 tìm |
| `tests/test_soi_loi_t110.py` | Gỡ 2 dấu `xfail` (SL-T110-2 phủ 2 ca, SL-T110-3), chỉ xóa dòng dấu; đổi kỳ vọng 5 hàm ghim «thiếu/lạ `post` vẫn ghi alt» và chữ cũ (bảng dưới) |
| `tests/test_t110_gan_anh_vao_bai_nhap.py` | Đổi kỳ vọng 4 hàm của tôi (lượt 2) theo G4 và câu mới; thêm 4 ca (mục «Test mới») |
| 17 file test cũ | Thêm `"post": None` vào câu trả lời lệnh tải ảnh của site giả (27 chỗ, bảng dưới); `test_wordpress_images.py` đổi thêm 1 chữ câu báo ở lối mã khác 201 |

Trước khi gỡ dấu: 3 ca XPASS(strict) (SL-T110-2 ×2, SL-T110-3).

### Test cũ đã đổi: kỳ vọng «thiếu/lạ `post`» và chữ câu báo (Chỉ Huy duyệt 31/10 00:45)

| Ca | Cũ | Mới |
|---|---|---|
| `test_soi_loi_t110.py::test_l2_post_so_duong_dung_ngay_khong_ghi_alt_khong_gan_khong_tao` (4 ca) | `startswith(wp._MEDIA_NOT_CREATED)` | `startswith(wp._MEDIA_HAS_PARENT)` |
| `test_soi_loi_t110.py::test_l2_post_thieu_hay_la_thi_khong_gan_bai_van_tao` (25 ca) → đổi tên `test_l2_post_thieu_hay_la_dung_ngay_khong_ghi_alt_khong_gan_khong_tao` | bài 42 vẫn tạo, `unattached == (101, 102)`, câu `_IMAGES_NOT_ATTACHED` | `DraftImagesError` bắt đầu bằng `_MEDIA_PARENT_UNKNOWN`; chỉ 1 lệnh (tải ảnh); không ghi alt (`media[101] == {"post": None}`), không tạo, không gắn; ảnh 9 nguyên |
| `test_soi_loi_t110.py::test_l2_post_la_ma_la_anh_co_san_thi_khong_doi_bai_cha` (5 ca) | `unattached == (9,)`, bài cha 7 (alt vẫn bị ghi) | `DraftImagesError`; `media[9] == OLD_9` (bài cha 7, alt cũ giữ nguyên) |
| `test_soi_loi_t110.py::test_l2_xet_tung_anh_anh_dau_trong_anh_sau_la` | ảnh 101 gắn, ảnh 102 chưa gắn, bài vẫn tạo | dừng ở ảnh 102: `uploaded == [101]`, câu `_MEDIA_PARENT_UNKNOWN`, 0 lệnh gắn, ảnh 102 không bị ghi alt |
| `test_soi_loi_t110.py::test_l2_upload_media_rieng_cung_xet_post` (8 ca) | «khong-ro» (thiếu, `"7"`, `NaN`, quá 2⁶³−1) vẫn tải và ghi alt; «tu-choi» bắt đầu bằng `_MEDIA_NOT_CREATED` | «khong-ro» dừng như «tu-choi», bắt đầu bằng `_MEDIA_PARENT_UNKNOWN`; «tu-choi» bắt đầu bằng `_MEDIA_HAS_PARENT`; nhánh còn lại (null, 0) `_uploaded_media_ids == {101}`. Kiểm «không chữ "xóa"», «Media → Thư viện» giữ |
| `test_t110_gan_anh_vao_bai_nhap.py::test_thieu_post_thi_khong_gan_bao_cau_co_dinh` → `test_thieu_post_thi_dung_khong_ghi_alt_khong_gan` | bài vẫn tạo, ảnh không gắn | dừng: câu `_MEDIA_PARENT_UNKNOWN` + `_DRAFT_IMAGE_RETURNED`, 0 lệnh ghi alt, 0 lệnh tạo |
| `test_t110_gan_anh_vao_bai_nhap.py::test_post_sai_kieu_thi_khong_gan` (11 ca) → `test_post_sai_kieu_thi_dung_khong_ghi_alt_khong_gan` | như trên | như trên |
| `test_t110_gan_anh_vao_bai_nhap.py::test_post_so_duong_la_anh_co_san_tu_choi_nhu_ma_khac_201` (3 ca), `::test_post_so_duong_o_upload_media_rieng_cung_tu_choi` | `_MEDIA_NOT_CREATED` | `_MEDIA_HAS_PARENT` |
| `test_wordpress_images.py::test_t071_tai_anh_khong_phai_201_thi_dung_khong_ghi_alt` (3 ca) | `"có thể vẫn đã lên" in str(err)` | `"có thể là ảnh có sẵn" in str(err)` (đuôi `_DRAFT_IMAGE_RETURNED`); `"201" in str(err)` giữ |

### Test cũ đã đổi: site giả trả `"post": None` (Chỉ Huy duyệt 31/10 08:55, cách A)

Mỗi chỗ chỉ thêm khóa `"post": None` vào câu trả lời lệnh tải ảnh (`POST /wp/v2/media`); vài dòng phải ngắt cho đủ 100 ký tự. Không đổi hay bỏ kiểm nào. Chỉ sửa chỗ làm ca đỏ vì thiếu `post`: chạy lại 17 file, 3.587 qua, không ca nào đỏ vì lý do khác.

| File | Dòng (sau khi sửa) |
|---|---|
| `tests/test_la_chan_t060.py` | 164, 224, 233 |
| `tests/test_la_chan_t071.py` | 55 |
| `tests/test_la_chan_t085.py` | 39 |
| `tests/test_soi_loi_t054.py` | 833, 851, 861 |
| `tests/test_soi_loi_t060.py` | 342, 607 |
| `tests/test_soi_loi_t061.py` | 466 (`media_site.create`) |
| `tests/test_soi_loi_t085.py` | 364, 383 |
| `tests/test_soi_loi_t088.py` | 408 |
| `tests/test_soi_loi_t091.py` | 268 (`created`), 405 |
| `tests/test_soi_loi_t099.py` | 751 (`_media_site`) |
| `tests/test_wordpress_client.py` | 288, 311, 328 |
| `tests/test_wordpress_images.py` | 1003 (`same_id`) |
| `tests/test_wordpress_round2_t042.py` | 89 |
| `tests/test_wordpress_routes_t042.py` | 186 |
| `tests/test_wordpress_t060.py` | 216, 409 (`media_site`) |
| `tests/test_wordpress_t085.py` | 311 (`uploaded`) |
| `tests/test_wordpress_t088.py` | 197 (`uploaded`) |

### Test mới (lượt 3), trong `tests/test_t110_gan_anh_vao_bai_nhap.py`

| Test | Kiểm |
|---|---|
| `test_anh_website_tra_lai_chi_dan_kiem_khong_bao_xoa` (3 ca: mã 200, 201 có bài cha, 201 thiếu `post`) | Câu bắt đầu đúng hằng, kết thúc bằng `_DRAFT_IMAGE_RETURNED`; không có «xóa»; không «cần mã 201» ở hai lối 201; `maybe_uploaded`, 0 lệnh ghi vào ảnh 9 |
| `test_loi_may_chu_o_lenh_tai_anh_giu_cau_cu` | Lỗi 502 ở lệnh tải ảnh: vẫn đuôi `_DRAFT_IMAGE_MAYBE` (ảnh mới có thể đã lên) |

### Bằng chứng (lượt 3)

```
# 2026-10-31 09:05–10:17, worktree wt-T-110 (đã gộp main 3cdd096), chỉ chạy test chọn lọc
$ uv run pytest -q tests/test_t110_gan_anh_vao_bai_nhap.py tests/test_la_chan_t110.py \
    tests/test_soi_loi_t110.py
222 passed
$ uv run pytest -q <17 file thêm "post": None>
3587 passed
$ uv run pytest -q <88 file: client WordPress, Gửi nháp, write.py, mọi file ghim câu báo hay site giả tải ảnh, cùng test T-102>
8874 passed, 1 skipped, 7 xfailed in 4290.47s (1:11:30)   # máy đang bận chạy toàn bộ test; 7 xfailed, 1 skipped là của phiếu khác
$ uv run ruff check .
All checks passed!
```

Thử «làm hỏng» code (sửa tạm, chạy 3 file test T-110, trả nguyên file; script so lại: giống hệt):

| Làm hỏng | Số test đỏ |
|---|---|
| Thiếu/lạ `post` vẫn nhận (bỏ G4) | 48 |
| Ảnh có bài cha dùng lại câu «cần mã 201» | 11 |
| Lối ảnh website trả lại dùng đuôi cũ xui xóa | 6 |
| Mọi lỗi tải ảnh dùng đuôi mới (cả 5xx) | 1 |
| Câu khóa «gửi dở» bỏ ý danh sách Media | 1 |

### Còn lại

- Ghi nhận G5 của Soi Lỗi (một ảnh lạ thì ảnh sau cũng không gắn): nay một ảnh lạ là dừng cả lần gửi trước khi tạo nháp, nên G5 không còn ý nghĩa.
- Lượt thử thật (G3): xem câu trả lời lệnh tải ảnh có `"post": null`. Website có plugin tự gắn ảnh mới vào một bài, hay lược bỏ trường `post`, thì «Gửi nháp» sẽ dừng ở ảnh đầu với câu báo cố định.

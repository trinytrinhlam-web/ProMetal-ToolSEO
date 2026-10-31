# Biên bản bảo mật T-110 · Gắn ảnh «Gửi nháp» vào bài nháp (LC-T093-2, chủ dự án chọn 1A) · rút gọn (W2, W3, F1)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | T-110 (phiếu ở checkout chính; code Thợ Máy `fc45a15`, test Soi Lỗi `f85b2bb`) |
| Phạm vi | **Rút gọn: W2, W3, F1** và 4 câu Chỉ Huy hỏi. Diff `fd28bbc..f85b2bb`: `seo_app/wordpress/client.py` (`_is_media_attach`, luật khóa `post` trong `_is_plain_request`, `ALLOWED_JSON_KEYS` của `POST /wp/v2/media/<mã>` thêm `post`, `_uploaded_media_ids` thêm ở `_post_media` khi `new_only`, `_attach_draft_images`, `_attach_media`, `_owns_attach` trong `_request`, `DraftWithImages.unattached`, 3 câu báo mới), `app/views/write.py` (chỉ `GPS_PUBLIC_WARNING`), 10 file test cũ đổi 18 hàm (R5, nhóm A/B/C), gỡ dấu `xfail` LC-T093-2, 2 file test mới. Gộp thử với `main` `17b2a31` (có T-099 lượt 2, T-107) |
| Ngày | 2026-10-30 (Chỉ Huy giao 19:05; làm 19:30 → 20:25 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (giải xung đột vị trí ở `client.py` bằng cách giữ cả hai hàm; đã kiểm trên bản gộp thử). 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp**: **LC-T110-1** (nâng từ G1 của Soi Lỗi: website trả `201` kèm ảnh có sẵn thì ảnh đó bị chuyển khỏi bài cũ sang bài nháp, trái W2) và **SL-T110-1** (giữ Thấp). **LC-T093-2 đóng** (đường chính). Không lỗi nào phải sửa trước khi gộp; **LC-T110-1 và SL-T110-1 sửa trước khi đóng Giai đoạn 3** (lượt 2 ngắn), hoặc chủ dự án ghi sổ rủi ro. Lỗi mới có test `xfail(strict=True)` trong `tests/test_la_chan_t110.py`. Không sửa code ứng dụng |

## Tóm tắt (cho chủ dự án)

- Phần «gắn ảnh vào bài nháp» **an toàn và đúng ý 1A**: phần mềm chỉ gắn ảnh nó vừa tải vào bài nháp nó vừa tạo; mọi cách khác (ảnh có sẵn, bài có sẵn, bài đã đăng, gỡ ảnh khỏi bài) đều bị chặn trước khi gửi. Ảnh gửi kèm bài nháp không còn hiện trong danh sách Media công khai cho tới khi bài được đăng. Gắn không được thì bài nháp vẫn xong, phần mềm báo rõ cách kiểm.
- Gộp chung với phần «hẹn giờ, đăng ngay» (T-099) không làm lỏng lớp chặn nào của hai bên.
- 2 điểm nhỏ nên sửa trước khi đóng Giai đoạn 3 (sửa nhanh):
  1. Nếu một plugin trên website trả lời sai «đã tạo ảnh mới» trong khi thật ra trả lại một ảnh **có sẵn**, phần mềm sẽ gắn ảnh có sẵn đó sang bài nháp mới (ảnh rời khỏi bài cũ). Website bình thường không làm vậy.
  2. Khi gửi hỏng **trước** lúc tạo được bài nháp, ảnh đã tải vẫn hiện trong danh sách Media công khai nhưng câu báo chưa nói điều này.
- **Việc của bạn:** không có. Ở lần thử thật tới: gửi một bài nháp kèm ảnh, mở `https://suachuacuasat.com/wp-json/wp/v2/media` bằng cửa sổ ẩn danh, ảnh vừa gửi không được có trong danh sách.

## Lỗi phát hiện

Số dòng theo `f85b2bb`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T110-1 | Thấp | **Lệnh gắn ảnh tin mã `201`** (nâng từ G1 Soi Lỗi). `_post_media` thêm mã ảnh vào `_uploaded_media_ids` chỉ dựa vào `201 Created` (`client.py:1728`); `_attach_media` gắn mọi ảnh trong tập vào bài nháp. Lệnh tải không xin `post` (`_MEDIA_FIELDS = "id,source_url,alt_text"`), nên client không biết ảnh trả về đã có bài cha | `seo_app/wordpress/client.py:1728`, `:1898-1918` | Website (plugin chống trùng ảnh, plugin sửa câu trả lời REST) trả `201` kèm mã ảnh **có sẵn** 9 đang thuộc bài đã đăng 7 → client ghi alt, tiêu đề vào ảnh 9 (đã có từ T-054, LC-T071-1 chỉ chặn được mã khác `201`) **và nay gửi thêm `{"post": 42}`**: ảnh 9 rời bài 7 sang bài nháp 42 (`probe_t110.py g1`: bài cha 7 → 42). Hậu quả trên website: ảnh không còn «tải lên cho» bài 7, `[gallery]` không ghi mã của bài 7 mất ảnh đó, trang đính kèm của ảnh 9 thành không công khai tới khi bài 42 đăng; ảnh trong nội dung bài 7 vẫn hiện (đường dẫn file không đổi). Trái W2 (không sửa dữ liệu đã có). WordPress lõi luôn tạo ảnh mới với `201`, nên chỉ gặp khi website trả lời sai. Test: `test_lc_t110_1_anh_co_san_site_tra_201_khong_bi_chuyen_bai_cha` (xfail), 2 ca đối chứng | Xin thêm `post` ở lệnh tải ảnh (`_fields` riêng cho lệnh tải), chỉ coi là ảnh của client khi `post` trống (ảnh mới tải qua REST chưa có bài cha); không trống thì làm như mã khác `201` (`_MEDIA_NOT_CREATED`: không ghi alt, không gắn). Phải đổi kỳ vọng các test ghim `_fields` của lệnh tải (cần Chỉ Huy duyệt R5) |

### Xếp mức lỗi của Soi Lỗi

| Mã | Soi Lỗi | Lá Chắn | Vì sao | Sửa trước |
|---|---|---|---|---|
| SL-T110-1 | Thấp | **Thấp, giữ** | Gửi hỏng trước khi có nháp (tạo nháp 400, 500, hết giờ) thì ảnh đã tải không có bài cha, vẫn trong danh sách Media công khai. `probe_t110.py sl1`: `DraftImagesError` liệt kê đúng ảnh 101, 102, 0 lệnh gắn; câu `_DRAFT_IMAGES_LEFT` có nói «xem được công khai qua đường dẫn», dặn tự xóa nếu không dùng, nhưng **không** nói ảnh hiện trong danh sách Media công khai; `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED` cũng vậy. Câu nhắc GPS mới lại hứa «gắn không được thì phần mềm báo». Ảnh là của chính người dùng, GPS công khai là quyết định 2026-10-14; phần hở là lúc ảnh lộ ra (trước khi đăng, hay không bao giờ đăng nếu bỏ dở) và câu báo | **Trước khi đóng Giai đoạn 3** (đây là phần còn lại của LC-T093-2, lỗi của đợt rà soát Giai đoạn 3): thêm vào 3 câu báo ý «ảnh có thể hiện trong danh sách Media công khai cho tới khi gắn vào bài hay xóa». Không phải trước khi gộp |
| G1 | Ghi nhận | **Nâng thành LC-T110-1 (Thấp)** | Có đường đi cụ thể làm sửa dữ liệu đã có trên website (W2), cách sửa rẻ | Như LC-T110-1 |
| G2 | Ghi nhận | Ghi nhận, đồng ý | Khoảng vài giây từ lúc tải tới lúc gắn ảnh vẫn liệt kê công khai: nội dung bài cần địa chỉ ảnh nên phải tải trước khi tạo nháp. Lần gửi bị ngắt giữa chừng thuộc SL-T110-1 | |
| G3 | Ghi nhận | Ghi nhận, đồng ý | Chưa thử website thật: xem «Việc của bạn» ở trên | Lần thử thật tới |

## Kết quả theo câu Chỉ Huy hỏi

### 1. LC-T093-2 đóng được chưa: **được (đường chính)**

- Sau lệnh tạo nháp, `_attach_draft_images` gắn từng ảnh vừa tải: `POST /wp/v2/media/<mã>` thân **đúng** `{"post": 42}`, `_fields=id,post`, kiểm câu trả lời đúng mã ảnh, đúng bài cha (`probe_t110.py luong`: thứ tự tải, alt, tải, alt, tạo nháp, gắn, gắn, kiểm nháp, ảnh đại diện; `unattached` rỗng). Theo WordPress lõi (`WP_REST_Posts_Controller::get_items` bỏ mục `check_read_permission` trả sai; mục `inherit` có bài cha thì xét quyền đọc bài cha, bài nháp thì người chưa đăng nhập không đọc được), ảnh của bài nháp không có trong `GET /wp-json/wp/v2/media` khi chưa đăng nhập, `GET /wp/v2/media/<mã>` trả 401.
- `tests/test_la_chan_t093.py::test_lc_t093_2_uploaded_images_attached_to_new_draft` (ca của tôi) qua; dấu `xfail` chỉ xóa 4 dòng dấu.
- Phần còn lại không thuộc đường chính: gửi hỏng trước khi có nháp hay bị ngắt giữa chừng (SL-T110-1), vài giây trước lúc gắn (G2), gắn lỗi (đã báo bằng câu cố định, `unattached`), chưa thử website thật (G3).

### 2. G1 có phải sửa trước khi gộp không: **không**

Nâng thành LC-T110-1 (Thấp). Chỉ gặp khi website trả lời sai `201` cho ảnh có sẵn; cùng điều kiện đó đã làm ghi đè alt từ T-054 (T-110 thêm việc đổi bài cha); sửa tay được trong trang quản trị (gắn lại ảnh vào bài cũ). Đề nghị sửa ở lượt 2 ngắn trước khi đóng Giai đoạn 3, cùng SL-T110-1.

### 3. SL-T110-1: **Thấp, nên sửa trước khi đóng Giai đoạn 3** (bảng «Xếp mức» ở trên)

### 4. Gộp thử với `main` `17b2a31`: hai lớp chặn không nới nhau

- `git merge-tree`: xung đột **vị trí** ở `client.py` (hai hàm mới `_is_image_upload` của T-099 lượt 2 và `_is_media_attach` của T-110 cùng chỗ); thân `_is_plain_request` tự gộp được, có đủ cả luật `data` (T-099) lẫn luật `post` (T-110); `tests/test_la_chan_t093.py` tự gộp (dấu LC-T093-2 và LC-T093-3 đều đã gỡ). Giải bằng cách giữ cả hai hàm (`resolve_gop_110.py`, chỉ trên bản sao): so từng dòng, bản gộp **đúng bằng** `main` + phần sửa của T-110, và **đúng bằng** T-110 + phần sửa của `main` (không mất, không thừa dòng nào).
- Luật `data` xét **trước** luật thân JSON, không dính khóa `post`; luật `post` nằm trong nhánh thân JSON không mang dấu, còn lệnh mang dấu `_RELEASE` phải đúng khuôn `_is_release_request` (không chứa `post`); `_owns_attach` chỉ xét lệnh có khóa `post`, lệnh khác trả `True`.
- Thử trên bản gộp (`probe_t110.py`, 263 ca, 0 hỏng): đăng ngay sau khi gắn được; sau lệnh đăng, gắn lại (qua `_attach_media` hay gọi thẳng `_request`) và đăng lần 2 đều bị từ chối, 0 request; lệnh chuyển kèm `post`, lệnh gắn mang dấu `_RELEASE`: chặn; luồng chuyển đang giữ bài (T-099 giành mã) thì lệnh gắn của luồng khác bị từ chối; thân byte `post=7` vào đường gắn (3 dạng): **chặn** (SL-T099-1); tải ảnh 6 đuôi vẫn đi.
- Script T-099 chạy lại trên bản gộp: `probe_t099.py` 215 ca, 0 hỏng; `probe_t099_l2.py` 2.307 ca, chỉ 2 cờ đã biết (Ghi nhận L2-3 của T-099: lỗi giả của chính script), y như trên nhánh T-099: 288/288 thân byte bị chặn ở 12 đường khác, nhiều luồng luôn đúng 1 lệnh chuyển.
- Trên **nhánh T-110 đứng riêng** (chưa có SL-T099-1), thân byte `post=7` vào `POST /wp/v2/media/101` qua được lớp chặn (`probe_t110.py data`); WordPress lõi không đọc thân đó (như phân tích SL-T099-1), và gộp với `main` thì bị chặn. Không xếp lỗi.
- Test chọn lọc trên bản gộp (máy đang chạy toàn bộ test ở phiên khác), 2 lô **50 file**: đủ 48 file test có chạm đường gửi nháp kèm ảnh, Media (grep `create_draft_with_images`, `send_draft`, «Gửi nháp», `media_writes`, `describes(`, `/wp/v2/media/`, `upload_media`, `_post_media`, `DraftWithImages`, `_uploaded_media_ids`, `GPS_PUBLIC_WARNING`; có cả `tests/test_t089_send_draft.py`, file từng bị sót ở T-091) cùng file test T-099 và client WordPress: **6.517 ca: 6.510 passed, 7 xfailed, 0 failed** (24 phút + 12 phút). 7 xfailed đều có chủ đích: LC-T110-1 (của tôi), SL-T110-1 × 3 (Soi Lỗi), SL-T106-1 × 2, SL-T108-1 (của `main`).

## Kết quả theo yêu cầu bảo mật của phiếu

**W2 (không xóa, ghi đè dữ liệu đã có): đạt, trừ LC-T110-1.**

- Hai lớp độc lập: `_attach_media` kiểm ảnh thuộc `_uploaded_media_ids`, bài thuộc `_created_post_ids`; `_request` kiểm lại (`_owns_attach`) kể cả khi gọi thẳng; `_is_media_attach` kiểm dạng (đúng `POST /wp/v2/media/<mã>`, thân chỉ một khóa `post`, mã bài là số nguyên dương thật).
- `probe_t110.py chan` (nhánh 254 ca, gộp 263 ca, 0 hỏng): đúng dạng của client thì gửi; **36 dạng gọi thẳng** bị chặn, 0 request: ảnh lạ, bài lạ, cả hai; `post` 0 (gỡ bài cha), âm, `True`, chữ, số thực, `null`, mảng, dict, 2⁶³; kèm `alt_text`, `status`; `Post`, `POST`, `post ` (dấu cách), `post_parent`, `parent`; `post` ở tham số truy vấn (đường Media chỉ nhận `_fields`); `post` ở đường bài, tạo bài, tải ảnh, ability, `GET`; kèm header form, `X-HTTP-Method-Override`, `_method`, dấu `_RELEASE`; mã ảnh 19 chữ số, có số 0 đầu, đường có `/` cuối, `/edit`. `_attach_media` với ảnh lạ, bài lạ, `True`, chữ: từ chối, 0 request. Client khác không gắn được ảnh, bài của client này. Ảnh trả `200` (đòi hay không đòi `201`) không thành ảnh của client.
- Bài website trả về không phải nháp (`publish`, `future`, `pending`, `private`, rỗng, `Draft`): 0 lệnh gắn, không lệnh nào sau lệnh tạo; báo chưa gắn.
- Không lệnh nào có `publish`, `future` (W1 giữ). Không có lệnh xóa.

**Gắn lỗi (yêu cầu 2 của phiếu): đạt.** 29 kiểu trả lời lỗi (401, 403, 404, 409, 429, 500, 502, 503, 301, 307, hết giờ, mất mạng, SSL, lỗi lạ trong adapter, `RecursionError`, HTML, rỗng, 204, danh sách, `null`, thiếu `post`, `post` 0/`null`/khác/chữ/`True`/`42.0`, mã ảnh khác, mã ảnh dạng chữ): bài nháp vẫn trả về, ảnh đại diện vẫn đặt, `unattached = (101, 102)`, **1** lệnh gắn (không thử lại), 2 lệnh tải, 1 lệnh tạo (không tải lại, không tạo trùng), câu cố định `_IMAGES_NOT_ATTACHED` (không lời máy chủ, không địa chỉ); ảnh thứ hai lỗi thì chỉ báo 1 ảnh. App hiện câu này bằng `st.warning(escape_markdown(…))` (`write.py:2975`), khóa gửi trùng T-086, T-089 không đổi (kết quả vẫn là «đã gửi» với mã bài).

**W3 (HTML gửi lên đã lọc): đạt, không đổi.** Lệnh tạo nháp, nội dung, `srcset` (T-059), ảnh đại diện giữ nguyên (`test_noi_dung_srcset_anh_dai_dien_khong_doi`); lệnh gắn chỉ mang một số nguyên. `GPS_PUBLIC_WARNING` là chữ cố định.

**F1 (không đọc/ghi ngoài thư mục được phép): đạt, không đổi.** Diff không chạm đường đọc file ảnh (`seo_app/images/folders.py`) hay ghi file nào.

**R5:** 10 file test cũ chỉ đổi đúng các dòng trong bảng A/B/C của báo cáo Thợ Máy (đối chiếu từng dòng): nhóm A thêm kỳ vọng lệnh gắn `{"post": 42}` cạnh lệnh ghi alt; nhóm B chèn lệnh gắn vào dãy lệnh (riêng `test_shortcode_t061.py::test_moi_lenh_ghi_co_fields_co_dinh_khong_dung_noi_dung` đổi dict thành danh sách, so cả dãy kèm truy vấn một lần, vòng kiểm «không hỏi `content`, `excerpt`, `description`, `caption`» giữ nguyên: chặt hơn trước); nhóm C chỉ bỏ qua lệnh gắn đúng dạng `{"post": 42}`, và ở `test_wordpress_images.py` dòng `continue` đặt **sau** kiểm «không `publish`, `future`, `status`». Không nới điều kiện nào khác.

## Danh sách kiểm tra (rút gọn)

| Mục | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets: 2 mục là chú thích ví dụ có từ trước (dưới) |
| S2 | Đạt | 3 câu báo mới cố định; lời máy chủ (mồi) không lọt vào `message` ở 29 kiểu lỗi |
| W1 | Đạt | Không lệnh nào mang `publish`/`future`; lệnh gắn không đổi trạng thái bài |
| W2 | Đạt có điều kiện | LC-T110-1 |
| W3 | Đạt | Không đổi |
| W4 | Đạt | Lệnh gắn đi qua `_request` cũ (https, timeout, không theo chuyển hướng) |
| F1 | Đạt | Không đổi |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi |
| D3 | Đạt | Site giả; bộ chặn mạng bật; script tự chặn socket |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| ruff | `ruff check .` trên nhánh: sạch | |
| bandit (`PYTHONUTF8=1`) | `client.py`, `write.py`: 0 | |
| detect-secrets (`PYTHONUTF8=1`, mồi tiếng Việt cùng lần quét: bắt được) | 7 file của phiếu: 2 mục «Basic Auth Credentials», đều là chú thích ví dụ địa chỉ có tên và mật khẩu giả có từ trước (`client.py`, 23/10; `write.py:2174`, 27/10; git blame) | Không phải bí mật |
| pytest | `tests/test_la_chan_t110.py`: 2 passed, 1 xfailed (`--runxfail`: ca xfail hỏng đúng lý do, có lệnh `{"post": 42}` vào ảnh 9). Bản gộp: câu 4 | |
| Script dò | `probe_t110.py`: nhánh 254 ca, bản gộp 263 ca, 0 hỏng | Tự chặn socket |

## Ghi nhận (không xếp lỗi)

1. Ảnh gắn lỗi do hết giờ có thể đã gắn thật trên website; câu báo nói «có thể vẫn hiện», chiều an toàn.
2. `_attach_draft_images` dừng ở ảnh lỗi đầu tiên, không gắn tiếp ảnh sau: ít lệnh hơn, câu báo đúng số ảnh chưa xác nhận.
3. Bài nháp được đăng sau (trong trang quản trị) thì ảnh đã gắn hiện trong danh sách Media công khai: đúng ý 1A.

## Điều kiện

1. **Gộp `main`:** giải xung đột `client.py` bằng cách giữ cả `_is_image_upload` (T-099 lượt 2) và `_is_media_attach` (T-110), như bản gộp thử; chạy lại test client WordPress khi gộp (Chỉ Huy chạy toàn bộ).
2. **Trước khi đóng Giai đoạn 3** (lượt 2 ngắn của T-110, Thợ Máy): LC-T110-1 (xin `post` ở lệnh tải, chỉ nhận ảnh chưa có bài cha; gỡ 1 dấu `xfail`; grep: 8 file test nhắc `_fields` của lệnh Media, ca nào ghim chuỗi của lệnh tải thì phải đổi, cần Chỉ Huy duyệt R5) và SL-T110-1 (3 câu báo; gỡ 3 dấu `xfail` của Soi Lỗi; 4 file test có nhắc các câu này, kiểm ca nào so nguyên câu). Không sửa thì chủ dự án quyết ghi sổ rủi ro (lỗi Thấp).
3. **Lần thử thật tới** (Chỉ Huy, chủ dự án): gửi một nháp kèm ảnh, mở danh sách Media bằng cửa sổ ẩn danh, ảnh vừa gửi không có trong danh sách; tài khoản Biên tập viên gắn được ảnh (không lỗi 403).

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 2 Thấp (LC-T110-1 mới, nâng từ G1; SL-T110-1 giữ Thấp). **Gộp `main` được ngay** (giữ cả hai hàm khi giải xung đột). LC-T093-2 đóng. LC-T110-1, SL-T110-1 sửa trước khi đóng Giai đoạn 3.

## Xem lại lượt 2–3 (rút gọn) · 2026-10-31

| Mục | Nội dung |
|---|---|
| Phạm vi | Thợ Máy lượt 2 `f8e8815` (gốc `main` `eef13b5`), lượt 3 `94c19e2` (sau khi gộp `main` `3cdd096` có T-102, `87c2fb4`); Soi Lỗi lượt 2 `f0ff53a`, lượt 3 `b7c018b`. Code: `seo_app/wordpress/client.py` (`_MEDIA_UPLOAD_FIELDS` xin thêm `post`; `_post_media` với `new_only`: chỉ mã 201 **và** `post` trống (`null`, `0`) mới là ảnh của client, `post` số dương → `_MEDIA_HAS_PARENT`, thiếu hay lạ → `_MEDIA_PARENT_UNKNOWN`, cả hai qua lớp lỗi riêng `_ReturnedMediaError`; câu `_DRAFT_IMAGE_RETURNED`; sửa `_DRAFT_IMAGES_LEFT`, `_DRAFT_IMAGE_MAYBE`), `app/views/write.py` (chỉ chữ `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED`, `GPS_PUBLIC_WARNING`, `unsure_message`). R5: site giả trả thêm `"post": None` (11 file lượt 2, 17 file lượt 3), chuỗi `_fields` của lệnh tải, chữ câu báo cũ, ca ghim «thiếu/lạ vẫn ghi alt» |
| Ngày | 2026-10-31 (Chỉ Huy giao 11:10; làm 11:32 → 13:32 +07, giờ máy đo bằng `date`; dừng 11:33 → 12:32 vì hết hạn mức; test cây gộp 52 phút vì máy tải 100%) |
| **Kết luận lượt 2–3** | **ĐẠT**, gộp `main` được ngay (với `main` cục bộ `bb25dde` không xung đột). **LC-T110-1 đóng**; SL-T110-1, -2, -3 đóng (đồng ý Soi Lỗi). 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp còn mở; Lá Chắn không có lỗi mới. **Đóng Giai đoạn 3 về phía T-110 được** (về bảo mật); nên có một lần gửi nháp kèm ảnh trên website thật để chắc website trả `"post": null` (mục «Ghi nhận lượt 2–3»). Gộp với phần T-115 đang làm: không xung đột chữ, **1 ca test sẽ đỏ** (mục 5) |

### Tóm tắt (cho chủ dự án)

- Điểm nhỏ tôi báo ở lượt 1 **đã sửa thật**: nếu website trả lời sai «đã tạo ảnh mới» mà thật ra trả lại một ảnh **có sẵn**, phần mềm nay nhận ra (hỏi thêm «ảnh này thuộc bài nào») và **không đụng** vào ảnh đó: không ghi alt, không gắn sang bài nháp, không tạo bài nháp. Tôi thử gần 1.000 kiểu trả lời: không lần nào ảnh có sẵn bị sửa.
- Các câu báo khi gửi hỏng nay nói đúng: ảnh đã tải mà chưa gắn bài thì đang hiện trong danh sách Media công khai; ảnh website trả lại (có thể của bài khác) thì chỉ dặn kiểm, **không** bảo xóa.
- Phần gắn ảnh của Giai đoạn 3 đã xong về bảo mật. **Việc của bạn:** không có; lần thử thật tới sẽ gửi một bài nháp kèm ảnh để xem website trả lời đúng như phần mềm chờ.

### 1. LC-T110-1 đóng

- `_post_media` (`client.py:1792-1812`): `new_only` (cả hai nơi gọi: `upload_media`, `create_draft_with_images`) thì mã khác 201, `post` số dương, `post` thiếu hay lạ đều ném `_ReturnedMediaError` **trước** khi mã ảnh vào `_uploaded_media_ids`, trước mọi lệnh ghi alt, gắn ảnh. Chỉ `post` là `None` hay số nguyên `0` (không `False`, `0.0`, `"0"`) mới là ảnh của client. WordPress lõi trả `post: null` cho ảnh mới tải qua REST (`WP_REST_Attachments_Controller::prepare_item_for_response`: `post_parent` rỗng thì `null`).
- `probe_t110_l3.py` (cây gộp `main` + T-110, **946 ca, 0 hỏng**): mã 200, 201, 202 × 19 giá trị `post` (thiếu, `null`, `0`, `7`, `1`, 2⁶³−1, 2⁶³, `"7"`, `"0"`, `""`, `True`, `False`, `0.0`, `7.5`, `-1`, `[]`, `{}`, `[7]`, `"null"`): ảnh là của client **đúng và chỉ** khi 201 + `null`/`0`; mỗi ca đúng 1 lệnh, lệnh tải xin `_fields=id,source_url,alt_text,post`. `upload_media` 36 ca ảnh có sẵn 9 (bài cha 7): **0 lệnh ghi** vào ảnh 9, ảnh 9 giữ alt và bài cha, báo lỗi. «Gửi nháp» 72 ca (ảnh có sẵn đứng đầu, hay sau một ảnh mới): 0 lệnh ghi ảnh 9, không tạo nháp, không lệnh gắn, `DraftImagesError` liệt kê đúng ảnh đã lên (101 hay không ảnh nào).
- Ca xfail của tôi `test_lc_t110_1_anh_co_san_site_tra_201_khong_bi_chuyen_bai_cha` nay qua (R5: lượt 2 chỉ xóa 5 dòng dấu, lượt 3 không đụng file của tôi). `probe_t110.py` lượt 1 chạy lại trên cây gộp: 262/263 ca như cũ; ca còn lại là ca ghi «hiện trạng G1» (chờ có lệnh ghi vào ảnh 9): nay **không còn** lệnh ghi nào, đúng là lỗi đã sửa.

### 2. Không ảnh có sẵn nào bị ghi alt, đổi bài cha ở mọi đường

- Lệnh ghi vào ảnh (`POST /wp/v2/media/<mã>`) chỉ có ở: ghi alt, tiêu đề, chú thích sau khi tải (`upload_media`, `_describe_draft_media`), chạy **sau** `_post_media(new_only=True)` đã xác nhận ảnh mới; gắn ảnh (`_attach_media`) chỉ cho mã trong `_uploaded_media_ids`, lớp `_request` kiểm lại (`_owns_attach`). `app/` không gọi `_request` thẳng (grep). Trang Kết nối WordPress không còn tải ảnh (T-106).
- Giới hạn còn lại (không xếp lỗi, mục «Ghi nhận lượt 2–3»): website trả 201 + `post: null` cho một ảnh **có sẵn nhưng chưa gắn bài nào** thì không phân biệt được với ảnh mới (đã thử: client ghi alt vào ảnh đó).

### 3. Câu báo

- Câu mới cố định, không chép lời máy chủ, không địa chỉ (probe gài mồi trong câu trả lời và địa chỉ ảnh: không lọt câu nào). Lối website trả lại ảnh (`_DRAFT_IMAGE_RETURNED`): «có thể là ảnh có sẵn, đang thuộc bài khác… để nguyên», không «hãy xóa». «Hãy tự xóa nếu không dùng» chỉ còn ở `_DRAFT_IMAGES_LEFT` (ảnh **chính lần gửi này** đã tải, đã xác nhận là ảnh mới) và ở các câu chung của trang (`MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED`, `unsure_message`: «xóa ảnh không dùng» sau khi tự kiểm, không khẳng định ảnh nào). Câu nhắc GPS nói đúng cả lối gửi hỏng trước khi có nháp. Hiển thị vẫn qua `escape_markdown`.

### 4. W2, W3, F1

- **W2: đạt** (mục 1, 2). **W3: đạt, không đổi** (lượt 2–3 không đụng nội dung bài, chỉ trường hỏi khi tải ảnh và chữ câu báo). **F1: đạt, không đổi** (không đụng đọc/ghi file).

### 5. Gộp thử

- `main` cục bộ `bb25dde` (T-078, T-109, T-114, ghi chú `[plan]`): `git merge-tree --write-tree` **không xung đột** (cây `7c519a9`); `client.py` của cây gộp đúng bằng của nhánh (`main` sau `d6df633` không đụng file T-110 sửa). Test chọn lọc trên cây gộp, 2 lô song song, **51 file** (mọi file test có chạm tải ảnh, «Gửi nháp», Media, câu báo gửi hỏng, cùng T-099, T-102): **6.866 ca: 6.858 passed, 7 xfailed, 1 failed** (lô a 3.741 + 4 xfailed, 34 phút; lô b 3.117 + 3 xfailed, 52 phút). 7 xfailed là lỗi đã biết của `main` (SL-T102-1 × 3, LC-T102-1, SL-T106-1 × 2, SL-T108-1). Ca hỏng `tests/test_app_wordpress.py::test_create_draft_from_form` là **hỏng oan**: `RuntimeError: AppTest script run timed out after 30(s)` lúc máy tải 100% (phiên khác chạy toàn bộ test); chạy riêng qua cả trên cây gộp (49 giây) lẫn trên nhánh (42 giây); ca này không đụng đường tải ảnh (trang Kết nối WordPress tạo nháp thử chỉ có chữ). Không chạy `test_pyasn1_version.py` (venv của worktree còn pyasn1 cũ, không liên quan).
- `team/T-115`: nhánh **chưa có commit nào** (đầu nhánh `d6df633` là `main`), nên gộp nhánh thì không có gì xung đột. Phần Thợ Máy đang làm dở trong `wt-T-115` (chưa commit, 12 file, đọc lúc 12:4x, chỉ đọc): 6 file chung với T-110 (`client.py`, `test_app_images.py`, `test_shortcode_t061.py`, `test_soi_loi_t054.py`, `test_soi_loi_t061.py`, `test_soi_loi_t099.py`), `git merge-file` 3 bên (gốc `d6df633`) **không xung đột chữ** cả 6. Chồng phần đó lên cây gộp rồi chạy 3 file test T-110: **1 ca đỏ, 380 qua**: `tests/test_soi_loi_t110.py::test_l2_lenh_tai_anh_xin_post_lenh_khac_giu_fields` (Soi Lỗi lượt 2) ghim nguyên dãy `_fields` của lệnh tạo nháp, kiểm nháp, ảnh đại diện mà T-115 thêm `modified_gmt`. **Khi gộp T-115 (sau T-110), Thợ Máy T-115 đổi các chuỗi `_fields` trong ca này theo R5**, không đổi thứ tự lệnh hay chuỗi `_fields` của lệnh tải, gắn ảnh.
- Thứ tự lệnh khi có cả hai phiếu: lệnh gắn ảnh (T-110) chạy giữa lệnh tạo nháp và lệnh ảnh đại diện. WordPress lõi không đổi `modified_gmt` của bài khi đổi bài cha của ảnh, nên không vướng cách so giờ sửa của T-115; nếu website (plugin) có đổi thì T-115 chỉ dừng lệnh chuyển (hướng an toàn). Nên xem ở lượt thử thật.

### Ghi nhận lượt 2–3 (không xếp lỗi)

1. **Giới hạn đã biết:** ảnh có sẵn **chưa gắn bài nào** mà website trả 201 + `post: null` thì client coi là ảnh mới (ghi alt, gắn vào nháp). Câu trả lời không có gì để phân biệt; WordPress lõi luôn tạo ảnh mới, chỉ plugin trả lời sai mới gặp; ảnh đó không thuộc bài nào nên hại nhỏ hơn ca LC-T110-1 đã sửa. Không cần ghi sổ rủi ro.
2. **G4 chặt:** website (plugin bảo mật, bộ lọc trường REST) không trả khóa `post` thì **mọi** lần tải ảnh dừng (an toàn nhưng «Gửi nháp kèm ảnh» không dùng được). Lần thử thật tới nên gửi một nháp kèm ảnh, xem lệnh tải trả `"post": null` (cùng G3 của Soi Lỗi: mở danh sách Media bằng cửa sổ ẩn danh, ảnh vừa gửi không có trong danh sách).
3. G6, G7 của Soi Lỗi (câu `_MEDIA_HAS_PARENT` khẳng định «không phải ảnh mới», `_MEDIA_PARENT_UNKNOWN` nói «thiếu» cả khi sai dạng): đồng ý không xếp lỗi, hướng dẫn vẫn an toàn.

### Kết quả công cụ quét (lượt 2–3)

| Công cụ | Kết quả |
|---|---|
| ruff | `ruff check .` trên nhánh: sạch |
| bandit (`PYTHONUTF8=1`) | `client.py`, `write.py`: 0 |
| detect-secrets (`PYTHONUTF8=1`, mồi tiếng Việt cùng lần quét: bắt được) | 7 file của lượt 2–3: 2 mục «Basic Auth Credentials», đều là chữ mẫu địa chỉ có tên và mật khẩu giả có từ trước (chú thích LC-T042-4 trong `client.py`, docstring `site_host` trong `write.py`); không phải bí mật |
| Script dò | `probe_t110_l3.py` 946 ca, 0 hỏng; `probe_t110.py` 263 ca (1 ca «hiện trạng» nay đúng như đã sửa) |

**Kết luận lượt 2–3:** **ĐẠT.** LC-T110-1 đóng; SL-T110-1, -2, -3 đóng; 0 lỗi mới, 0 lỗi còn mở. Gộp `main` được ngay. Đóng Giai đoạn 3 về phía T-110 được (về bảo mật); lần thử thật xem website trả `"post": null`. Khi gộp T-115: đổi chuỗi `_fields` ở 1 ca của `test_soi_loi_t110.py` theo R5.

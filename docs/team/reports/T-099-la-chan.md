# Biên bản bảo mật T-099 · Client WordPress: hẹn giờ, đăng ngay, đọc trạng thái bài · đầy đủ (soát kỹ nhất)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-099](../tickets/T-099-client-hen-gio-dang-ngay.md) (code Thợ Máy `3c60948`, test Soi Lỗi `86219e4`) |
| Phạm vi | **Đầy đủ, soát kỹ nhất** (đường duy nhất tới `future`/`publish`). Diff `9e0115e..86219e4` (nhánh đã có T-091): `seo_app/wordpress/client.py` (`_RELEASE`, `_is_release_request`, `_PARAM_VALUES`, `release_draft`, `_release_check`, `_released_from`, `post_statuses`, `ConnectionInfo` múi giờ; sửa `_is_plain_request`, `_request`, `_FORBIDDEN_JSON_KEYS`, `ALLOWED_PARAMS`), `seo_app/publish/schedule.py` (mới), 3 file test mới, 1 test cũ đổi (R5, Chỉ Huy duyệt). Đọc cả code quanh chỗ sửa (`create_draft`, `set_seo_meta`, `set_featured_image`, `_own_draft`, `_is_own_draft_answer`, `_positive_id`, `_json`) và cách WordPress lõi đọc thân lệnh (`WP_REST_Request::get_parameter_order`, `parse_body_params`, `wp_insert_post` với `future`). Điều kiện LC-T094-1 → -3, LC-T094-22 → -27 |
| Ngày | 2026-10-29 → 30 (Chỉ Huy giao 29/10 01:20; làm 29/10 01:32 → khoảng 02:00, máy dừng; làm tiếp 30/10 07:28 → 08:03 +07, giờ máy đo bằng `date`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp**: 1 mới của Lá Chắn (**LC-T099-1**: hai luồng dùng chung một client cùng chuyển một bài thì gửi 2 lệnh chuyển) và SL-T099-1 của Soi Lỗi (giữ Thấp). **Không tìm thấy đường nào làm bài bị đăng hay hẹn giờ ngoài ý người dùng** khi dùng đúng thiết kế. **Không lỗi nào phải sửa trước khi gộp** (`release_draft` chưa có nơi gọi); **LC-T099-1, SL-T099-1 sửa trước khi T-102 nối màn hình xác nhận**. Lỗi mới có test `xfail(strict=True)` trong `tests/test_la_chan_t099.py`. Không sửa code ứng dụng |

## Tóm tắt (cho chủ dự án)

- Phần «hẹn giờ, đăng ngay» (chưa có nút nào dùng tới) **an toàn**. Tôi đi tìm mọi cách làm một bài bị đăng hay hẹn giờ mà bạn không muốn, và không tìm thấy cách nào:
  - chỉ bài nháp phần mềm vừa tạo trong chính lần bấm đó mới chuyển được; bài có sẵn trên website, mã bài lạ, mã quá lớn đều bị từ chối trước khi gửi gì;
  - mất mạng, website lỗi hay trả lời lạ thì phần mềm báo «có thể đã…», **không bao giờ tự gửi lại**;
  - giờ hẹn đã qua, quá gần (dưới 10 phút), quá xa (trên 1 năm), đồng hồ máy lệch website hơn 2 phút, hay không đọc được giờ của website đều bị chặn;
  - không còn lối nào khác gửi lệnh «đăng» lên website, kể cả các mẹo đổi lệnh qua tham số hay tiêu đề.
- 2 điểm nhỏ (không chặn gộp, nên sửa trước khi làm màn hình xác nhận): (1) nếu sau này lỡ viết code dùng chung một «bộ kết nối» cho hai việc chạy cùng lúc, một bài có thể nhận 2 lệnh chuyển; cách dùng đúng thiết kế không gặp, sửa mất vài dòng (tôi đã thử). (2) một lớp chặn chưa soát loại thân lệnh ít dùng; WordPress hiện bỏ qua thân đó, nên chưa thành lỗ.
- **Việc của bạn:** không có.

## Lỗi phát hiện

Số dòng theo `86219e4`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T099-1 | Thấp | **Kiểm «bài của client» và bỏ mã bài không cùng một bước:** `release_draft` kiểm mã thuộc `_created_post_ids` ở đầu hàm (`client.py:1388`), gửi lệnh kiểm nháp (chờ mạng), rồi mới `discard` (`:1419`). Hai luồng dùng **chung** một đối tượng client cùng gọi cho một bài thì cả hai qua bước kiểm, cùng gửi lệnh chuyển: trái lời hứa trong docstring «từ đây không lệnh nào của client sửa tiếp bài này» | `seo_app/wordpress/client.py:1388`, `:1419` | Hai luồng, một client, một bài: lệnh kiểm nháp của luồng 1 đang chờ thì luồng 2 vào, cả hai đi tiếp → **2 lệnh chuyển** vào một bài (`probe_t099.py luong`: kết quả `['ok', 'ok']`, 2 lệnh). Cùng hình thức thì lệnh thứ hai lặp lại thay đổi cũ; khác hình thức (một hẹn giờ, một đăng ngay) thì bài có thể lên công khai sớm. **Không xảy ra khi dùng đúng thiết kế:** mỗi lần bấm tạo client mới (LC-T094-23), Streamlit chạy mỗi phiên trên một luồng, hai tab là hai client. Chỉ gặp nếu sau này client bị giữ chung (`st.cache_resource`, biến toàn cục) cho nhiều lần chạy. Đây là lớp phòng cho đường quan trọng nhất. Test: `test_lc_t099_1_hai_luong_chung_mot_client_chi_mot_lenh_chuyen` (xfail), 2 ca đối chứng | Giành mã bài **một bước** ở đầu hàm: `self._created_post_ids.remove(post_id)` (`KeyError` → từ chối); bị chặn **trước** lệnh chuyển (hình thức sai, giờ sai, lệnh kiểm nháp lỗi mạng, đồng hồ lệch) thì trả mã lại; bài «không còn nháp» thì không trả. Giữ mọi thứ trong thân `release_draft` (test đọc mã nguồn đòi vậy). Đã thử trên bản sao (`patch_sua_mau_099.py`): ca xfail thành XPASS, 645 ca khác qua (`test_wordpress_release.py`, `test_publish_schedule.py`, `test_soi_loi_t099.py`, `test_soi_loi_t037.py`, `test_safety.py`), script dò: 1 lệnh chuyển |

### Xếp mức lỗi của Soi Lỗi

| Mã | Soi Lỗi | Lá Chắn | Vì sao | Sửa trước |
|---|---|---|---|---|
| SL-T099-1 | Thấp | **Thấp, giữ** | `_is_plain_request` (`client.py:215-292`) nhận thân `data=` (byte) ở mọi đường mà không soát khóa, `status`. Tôi thử lại: `POST /wp/v2/posts/42` với `data=b"status=publish"` qua lớp chặn. **Chưa thành lỗ**, vì: (1) `requests` không gắn `Content-Type` cho byte; (2) lớp chặn chỉ nhận `Content-Type` loại ảnh, nên `application/x-www-form-urlencoded`, `application/json` bị chặn (đã thử), cả `data` kiểu `dict`, `str`, `files` cũng bị chặn; (3) WordPress lõi với `POST` chỉ đọc thân qua `$_POST` (PHP chỉ điền khi `Content-Type` dạng form) hay JSON (khi `Content-Type` JSON); `parse_body_params` (coi thiếu `Content-Type` là dạng form) chỉ chạy với phương thức khác `POST`, mà đổi phương thức (`_method`, `X-HTTP-Method-Override`) đã bị chặn. Lời hứa «chỉ lệnh có dấu mới gửi được `status` khác nháp» vì vậy đang dựa vào cách WordPress đọc thân, chưa vào lớp chặn | Trước T-102 (thêm nơi gọi client mới): chỉ nhận `data` ở `POST /wp/v2/media` kèm `Content-Type` thuộc `IMAGE_TYPES` (gợi ý của Soi Lỗi) |

## Kết quả theo việc Chỉ Huy giao

**1. Cổng bảo mật mục 3 và LC-T094 của T-099: đạt** (bảng «Đối chiếu điều kiện» và «Danh sách kiểm tra» bên dưới).

**2. Mọi đường làm bài bị đăng, hẹn giờ ngoài ý người dùng: không tìm thấy đường nào khi dùng đúng thiết kế.** Script `probe_t099.py` (thư mục nháp, không commit; Google, WordPress giả, đồng hồ máy cố định): **215 ca, 0 hỏng**.

| Đường | Kết quả | Bằng chứng |
|---|---|---|
| Bài không do app tạo | Chặn, **0 request** | Mã `_created_post_ids` chỉ do `create_draft` thêm (`:1187`, khi site xác nhận `draft`; grep `seo_app/`, `app/`: không chỗ nào khác). Probe: client mới gọi `release_draft(42)` → 0 request. Mã đọc từ `post_statuses` không thành bài được sửa (0 request). Site báo bài đã `publish`, `future`, `pending`, `private`, `trash`, `Draft`: chỉ 1 lệnh kiểm (GET), không lệnh chuyển, mã bị bỏ |
| Mã giả, quá lớn | Chặn, 0 request | `type(post_id) is int` và thuộc tập (`:1388`); mã trong tập đã qua `_positive_id` (≤ 2⁶³−1, T-091). Probe: `True`, `42.0`, `"42"`, `2**63`, `-1`, `0`, `None` → 0 request |
| Gửi lại khi không chắc | **Không bao giờ tự gửi lại** | Mã bị bỏ khỏi tập **trước** lệnh chuyển (`:1419`), nên mọi lần gọi lại trên cùng client bị từ chối (0 request). Probe 9 ca lỗi không rõ (hết giờ, 500, 502 HTML, 301 + `Location`, 200 không JSON, thiếu `status`, mã khác, `draft`, giờ khác): `unsure=True`, đúng 1 lệnh chuyển, gọi lại 0 request, câu không chép mồi, không chép `WORDPRESS_URL`, không gọi địa chỉ chuyển hướng. 4xx (400, 401, 403, 404, 409, 429): «vẫn là nháp», gọi lại 0 request. Hẹn giờ mà site đăng ngay: `went_public`, câu khẩn, không lệnh nào thêm |
| Hai tab, chạy lại giữa chừng | Không đường | Hai tab là hai phiên, hai client: tab kia không có mã bài trong tập → 0 request. Chạy lại (rerun) tạo client mới → không chuyển được bài của lần chạy trước. Khóa gửi trùng ở tầng nháp (T-086, T-089) và LC-T094-39 (T-102) phủ phần giao diện. Riêng **một client dùng chung cho hai luồng**: LC-T099-1 |
| Giờ hẹn sai múi, đã qua, `date_gmt` | Chặn đúng | `date_gmt_text` (`schedule.py:98`) chỉ nhận `datetime` có múi giờ, đổi UTC, bỏ phần lẻ giây; khuôn thân đòi `date_gmt` ASCII `YYYY-MM-DDTHH:MM:SS` (`_is_release_request`). Probe: giờ hẹn `+07:00` 15:00:00.999999 → gửi `08:00:00` UTC; giờ không múi, chữ, số → 0 request (cả lệnh kiểm). 6 mức lệch đồng hồ × 7 khoảng hẹn (−1 phút, 0, 9 phút 59 giây, 10 phút, 10 phút 1 giây, 365 ngày, 365 ngày 1 giây): gửi đúng khi và chỉ khi lệch ≤ 2 phút và khoảng hẹn trong [10 phút, 365 ngày] **theo giờ máy chủ**; mọi lần gửi có `date_gmt ≥ giờ máy chủ + 10 phút`. `local_to_utc` từ chối giờ nhảy, giờ lặp (New York 08/03 02:30, 01/11 01:30) |
| Header `Date` giả | Chặn hay vô hại | Thiếu, rỗng, chữ hỏng, `-0000`, asctime, lặp hai lần, ngày 99, dài quá → chặn ở cả hai hình thức, không lệnh chuyển. `Date` đúng dạng nhưng sai giờ: phải khớp đồng hồ máy trong 2 phút, nếu không thì chặn; khớp thì biên 10 phút vẫn còn. Muốn lợi dụng phải làm sai **cả** giờ website lẫn đồng hồ máy cùng chiều (tức là chiếm máy) |
| Đồng hồ máy lệch | Chặn > 2 phút | Probe ±2 phút 1 giây, 2 giờ: chặn; ±1 phút 59 giây: gửi |
| Đồng hồ PHP của website khác giờ `Date` (Ghi nhận G5 của Soi Lỗi) | Bắt được ngay sau lệnh | WordPress đổi `future` thành `publish` khi giờ hẹn < 60 giây sau giờ PHP. Biên 10 phút che lệch tới khoảng 9 phút; lệch hơn thì câu trả lời là `publish` → `went_public`, câu khẩn, không gửi thêm. Bài lên sớm hơn giờ hẹn là bài người dùng đã xác nhận đăng: Thấp, hạn chế của thiết kế |

**3. Không đường nào khác gửi `status` khác nháp: đạt** (trừ lớp phòng SL-T099-1, chưa thành lỗ).

- `probe_t099.py chan`: gọi thẳng `_request` 31 kiểu, **0 lệnh lọt**: không dấu mà `json` có `status` `publish`, `future`, `pending`, `private`, `Draft`, có `date`, `date_gmt`, `DATE_GMT`; `params` `status`, `_method`, `rest_route`; header `X-HTTP-Method-Override`; `data` kèm `Content-Type` dạng form hay JSON; `data` kiểu `dict`, `str`; `files`. Có dấu `_RELEASE` mà thêm tiêu đề, `date`, `pending`, thiếu ngày, ngày có đuôi `Z`, chữ số toàn khổ, `_fields` khác, thiếu `params`, thêm tham số, thêm header, thêm `data`; dấu giả (`object()`, `True`, chữ). Dấu đúng ở đường khác (tạo bài, `pages`, `media`, `GET`, ability SiteSEO): chặn. Phiên có header ghi đè phương thức, `params` `status`, `Content-Type` dạng form: chặn cả lệnh có dấu.
- `probe_t099.py dua`: chạy mọi luồng thường của client (kiểm kết nối, chuyên mục, thẻ, bài đã đăng, tạo nháp có chuyên mục, thẻ, đoạn trích, slug, tải ảnh, ảnh đại diện, ghi SEO): 12 lệnh, **không lệnh nào** mang `status` khác `draft` hay ngày, kể cả trong tham số của lệnh ghi.
- Đọc mã: `_RELEASE` chỉ ở định nghĩa (`:184`), `_is_plain_request` (`:235`), `release_draft` (`:1405`, `:1422`); `_request` (`:1940-1944`) gỡ `release` khỏi tùy chọn, không tới `requests`. Test đọc mã nguồn của Thợ Máy canh điều này và canh «`release_draft` chỉ được gọi từ một hàm của `app/views/write.py`» (hiện 0 nơi gọi).

**4. Không lùi T-059, T-086, T-089, T-091: đạt.** `ALLOWED_ROUTES` không đổi (chỉ chú thích); `_positive_id`, `_json` không đổi; `_created_post_ids` chỉ thêm chỗ **bỏ** mã (`release_draft`, `_release_check`), `set_seo_meta`, `set_featured_image` vẫn đòi mã thuộc tập, nên sau khi chuyển không lệnh nào sửa tiếp bài (probe: 0 request). `_FORBIDDEN_JSON_KEYS` thêm `date` (không lệnh cũ nào gửi). `_PARAM_VALUES` kiểm giá trị `status` của `GET /wp/v2/posts`: `list_published` vẫn gửi `status=publish` được. Test cây gộp: việc 5.

**5. Thử gộp với `main` trên máy: đạt.** `main` `0122d4b` (thêm T-103, T-104 sau lượt đầu): `git merge-tree --write-tree main team/T-099` → cây `6f19c54`, **không xung đột**. `main` không đụng `client.py`, `schedule.py`; chỗ dính nhau: `config.py` (client nhập `DEFAULT_TIMEZONE`, `Settings`, vẫn còn), `onpage/meta.py` (`_seo_text` dùng), `publish/render.py`, `review.py`. Lượt 76 file trên cây gộp với `main` `209615a` (29/10 01:37) bị ngắt khi máy dừng. Chạy lại có chọn lọc trên cây gộp mới, 32 file chạm cả hai phía (4 file test T-099 và file của tôi, `test_soi_loi_t037.py`, `test_safety.py`; ghi SEO, `_seo_text`, `normalize_meta` của T-041, T-042, T-090; bộ dựng T-096; T-091; «Gửi nháp» T-086, T-089; client WordPress T-060, T-085, T-088; trang Kết nối; cấu hình), 30/10 07:28–08:00: **3.523 passed, 6 xfailed, 1 failed**. 6 xfail = 1 LC-T099-1 + 5 SL-T099-1. Ca hỏng `test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (đo khóa luồng): chạy riêng trên cây gộp 2 lần đều qua; Thợ Máy và Lá Chắn T-091 cũng gặp ca này khi máy bận: hỏng oan, không do T-099. `probe_t099.py` trên cây gộp: 215 ca, 0 hỏng.

**6. R5 (test cũ đã đổi): đúng điều kiện duyệt.** `tests/test_soi_loi_t037.py::test_status_publish_or_future_only_in_list_published`: chỉ đổi danh sách mong đợi (so `==`, đúng 4 cặp duyệt: `list_published` `'publish'`, `release_draft` `'future'`, `'publish'`, `post_statuses` `POST_STATUS_FILTER`) và docstring; thân phép dò cây cú pháp không đổi. Không test cũ nào khác bị đổi.

## Đối chiếu điều kiện LC-T094 của phiếu

| Mã | Kết quả | Ở đâu, bằng chứng |
|---|---|---|
| LC-T094-1 | Đạt | Test dùng `FakeWordPress`; `tests/conftest.py` không đổi; `schedule.py` không gọi mạng |
| LC-T094-2 | Đạt | Câu `_RELEASE_*`, `_STATUS_BAD_IDS` (`client.py:517-564`), `MSG_*` (`schedule.py`) cố định; câu 4xx đi qua `_error_from` (không chép lời máy chủ); probe gài mồi ở lời máy chủ và trong lỗi lạ: `str(err)` không có mồi, không có `WORDPRESS_URL`. Lưu ý: nhánh lỗi lạ dùng `from exc` (lỗi gốc gắn kèm, traceback đầy đủ có mồi): giao diện chỉ được hiện `str(err)` (điều kiện T-102) |
| LC-T094-3 | Phần client đạt; giao diện thuộc T-101, T-102 | `link` qua `is_site_link`, `date_gmt` khuôn ASCII, `timezone_string` khuôn IANA; `timezone_warning` chỉ chèn độ lệch đã kiểm là số |
| LC-T094-22 | Đạt | Việc 3. Khuôn duy nhất `_is_release_request` (`:295-320`); `release is _RELEASE` (`:235-239`); dấu gỡ khỏi tùy chọn (`:1942`); `date` không bao giờ nhận; tạo bài chỉ `draft` |
| LC-T094-23 | Đạt, trừ phần «nên» (so `modified_gmt`) | Mã thuộc tập của chính client; hỏi lại còn nháp ngay trước lệnh (`_release_check`, `:1449-1472`); bỏ mã khỏi tập trước lệnh chuyển. Phần «nên» chưa làm: Ghi nhận 1. Thêm lớp phòng hai luồng: LC-T099-1 |
| LC-T094-24 | Đạt | Việc 2 (giờ, `Date`, đồng hồ). Giờ máy chủ lấy từ chính câu trả lời lệnh kiểm nháp; thiếu, sai dạng → chặn, không lấy đồng hồ máy thay |
| LC-T094-25 | Đạt | `_released_from` (`:1474-1505`): đúng mã, đúng trạng thái, `future` thì `date_gmt` đúng chuỗi đã gửi; hẹn giờ mà `publish` → câu khẩn theo `security.md` 7.2, không gửi thêm; lỗi không rõ → `unsure`, không tự gửi lại |
| LC-T094-26 | Đạt | `post_statuses`, `_state_from` (`:1507-1570`) chỉ `GET`; `include` ≤ 100 mã kiểm khuôn (`_ID_LIST`), `status` hằng, `context=edit`, `_fields` hằng không nội dung; tối đa 1.000 mã, chia lệnh ≤ 100. Probe: 250 mã → 3 lệnh `GET`; mục lạ (mã chưa hỏi, `inherit`, 2⁶³, `True`, chữ) bị bỏ; đầu vào `0`, `-1`, `True`, `"5"`, `5.0`, 2⁶³, 1.001 mã, chữ, byte, dict, số đơn → 0 request; mã đọc được không thành bài được sửa |
| LC-T094-27 | Đạt | `_site_timezone`, `_site_offset` kiểm khuôn, −12 … +14; `timezone_warning` câu cố định; `schedule_label` tính từ giờ người dùng chọn |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (`PYTHONUTF8=1`) trên 8 file của phiếu và file test của tôi: 3 kết quả, đều không phải bí mật (`client.py:930` chú thích ví dụ địa chỉ có tên, mật khẩu, có từ trước; `tests/test_soi_loi_t037.py:155` địa chỉ giả có từ trước; `T-099-tho-may.md:120` chép lại ví dụ đó). `git log -p 9e0115e..HEAD`: không khối khóa, khóa API, mã truy cập |
| S2 | Đạt (lưu ý `from exc`) | LC-T094-2 ở trên |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Đạt phần client | Mặc định nháp; `future`/`publish` chỉ qua `release_draft` (đường duy nhất, có test đọc mã nguồn); bước xác nhận của người dùng và công tắc mặc định tắt thuộc T-102 (LC-T094-37, -38, -41) |
| W2 | Đạt | Chỉ bài nháp client vừa tạo; không xóa; sau khi chuyển không lệnh nào sửa tiếp bài; bài người khác (đã đăng, hẹn giờ, chờ duyệt, riêng tư) không bao giờ bị chuyển |
| W3 | Đạt | Lệnh chuyển không mang nội dung, tiêu đề (khuôn chỉ `status`, `date_gmt`); `_fields` câu trả lời không có nội dung |
| W4 | Đạt | Dùng `_request` có sẵn (https, giờ chờ, không theo chuyển hướng); probe 301 + `Location`: không gọi địa chỉ mới |
| A1–A3 | Không áp dụng | Không gọi AI |
| U1–U3 | Không áp dụng | Chưa có giao diện (điều kiện T-102) |
| F1–F3 | Không áp dụng | Không đọc ghi file |
| D1 | Đạt | Không thư viện mới (`schedule.py` dùng thư viện chuẩn `email.utils`, `zoneinfo`); `pyproject.toml`, `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test dùng site giả; bộ chặn mạng bật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy lại: `uv.lock` không đổi (lượt gần nhất T-097, 28/10 14:58: sạch) | |
| bandit 1.9.4 (`PYTHONUTF8=1`) | `seo_app/wordpress/client.py`, `seo_app/publish/schedule.py`: 0 | |
| detect-secrets 1.5.0 (`PYTHONUTF8=1`) | 3 kết quả, không phải bí mật (S1) | Hai dòng có ở gốc `9e0115e` |
| ruff | `uv run ruff check .`: sạch | |
| pytest | `tests/test_la_chan_t099.py`: 2 passed, 1 xfailed (chạy 3 lần đều vậy; `--runxfail`: ca xfail hỏng đúng lý do, 2 lệnh chuyển). Cây gộp: việc 5 | |
| Script dò | `probe_t099.py`: 215 ca, 0 hỏng | Tự chặn socket |

## Ghi nhận (không xếp lỗi)

1. **LC-T094-23 phần «nên» (so `modified_gmt`) chưa làm** (Rủi ro 1 Thợ Máy, G1 Soi Lỗi). Ai đó sửa nháp trong trang quản trị đúng trong khe vài giây giữa lúc app tạo nháp và lúc chuyển thì bài lên khác bản đã xác nhận. Khe hở rất ngắn, mã bài mới chưa ai biết, nội dung app gửi đã được mã băm T-102 khóa. **Chấp nhận cho lúc gộp**; nên làm trước khi bật công tắc Hẹn giờ, Đăng ngay (LC-T094-41), cùng phiếu đổi `_fields` (phải đổi 5 file test cũ ghim chuỗi `_fields`, cần Chỉ Huy duyệt R5).
2. **Lỗi gốc gắn kèm** (`raise … from exc` ở nhánh lỗi lạ của `release_draft`, `_release_check`): `str(err)` sạch, nhưng traceback đầy đủ có lời lỗi gốc (probe: có mồi, có địa chỉ website). T-102 chỉ hiện `str(err)`, không `st.exception`.
3. G2, G3, G4, G6 của Soi Lỗi: đồng ý không xếp lỗi (câu báo chưa sát ở ca hiếm nhưng luôn chiều an toàn; 4xx sau khi plugin đã lưu thì câu «vẫn là nháp» sai nhưng không gửi lại).
4. `ConnectionInfo.timezone_string` là chữ website đã kiểm khuôn nhưng chưa được hiện ở đâu; khi hiện thì chữ thuần (LC-T094-3).

## Điều kiện

1. **Trước khi T-102 nối màn hình xác nhận (Thợ Máy, phiếu dọn ngắn):** LC-T099-1 (giành mã bài một bước, trả lại khi bị chặn trước lệnh chuyển; gỡ 1 dấu `xfail`), SL-T099-1 (chỉ nhận `data` ở `POST /wp/v2/media` kèm `Content-Type` ảnh; gỡ 5 dấu `xfail`).
2. **T-102 (Họa Sĩ), thêm vào LC-T094-36 → -41:**
   - Gọi `release_draft` đúng **một** lần mỗi lần bấm, trên **chính** client vừa tạo nháp trong lần bấm đó, sau ảnh đại diện và ghi SEO; không giữ client trong `st.session_state`, `st.cache_resource` hay biến toàn cục (LC-T094-23, LC-T099-1).
   - Ghi kết quả vào kho nháp **trước** mọi lệnh `st.*` tiếp theo (chạy lại giữa chừng không làm mất kết quả, LC-T094-39).
   - Bắt `ReleaseError`: `unsure` hay `went_public` thì khóa gửi lại, hiện `str(err)` bằng chữ thường (không `st.exception`: Ghi nhận 2), `edit_link` không bấm được.
   - `when_utc` từ `schedule.local_to_utc(...)`; cùng giá trị cho `build_article(date_gmt=schedule.date_gmt_text(when_utc))` để mã băm khớp.
3. **Trước khi bật công tắc Hẹn giờ, Đăng ngay (LC-T094-41):** lượt thử thật LC-T094-44 (website có header `Date` đúng, tài khoản Biên tập viên đặt được `future` qua REST); cân nhắc Ghi nhận 1.

**Kết luận:** **ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 2 Thấp (LC-T099-1 mới; SL-T099-1 giữ Thấp). **Gộp `main` được ngay** (không lỗi nào phải sửa trước khi gộp; `release_draft` chưa có nơi gọi). LC-T099-1, SL-T099-1 sửa trước khi T-102 nối màn hình xác nhận.

## Xem lại lượt 2 (rút gọn) · 2026-10-30

| Mục | Nội dung |
|---|---|
| Phạm vi | Diff `ce451fe..7c2a827`. Thợ Máy lượt 2 `1040586`: `seo_app/wordpress/client.py` (`release_draft` giành mã bài bằng `_created_post_ids.remove` ngay đầu hàm, `try … finally` trả mã khi bị chặn trước lệnh chuyển; `_release_check` trả `(còn nháp, giờ máy chủ)`, không đụng tập mã; `_is_image_upload` mới và một dòng trong `_is_plain_request`), gỡ 6 dấu `xfail`, 27 ca mới trong `tests/test_wordpress_release.py`. Soi Lỗi lượt 2 `7c2a827`: 317 dòng test mới trong `tests/test_soi_loi_t099.py`. Thử gộp với `main` `fd28bbc` |
| Ngày | 2026-10-30 13:03 → 14:30 (+07, giờ máy đo bằng `date`; chạy test cây gộp 57 phút vì máy tải 80–99%) |
| **Kết luận lượt 2** | **ĐẠT**, gộp `main` được ngay. **LC-T099-1 và SL-T099-1 đóng thật**, không mở lỗ mới, không chặn oan lệnh tải ảnh. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp còn mở; Lá Chắn không có lỗi mới. **T-102 nối màn hình xác nhận được** khi nhánh này đã lên `main`: giữ điều kiện T-102 của lượt 1, thêm 3 ý ở «Điều kiện lượt 2». Điều kiện trước khi bật công tắc Hẹn giờ, Đăng ngay giữ nguyên |

### Tóm tắt (cho chủ dự án)

- Hai điểm nhỏ của lượt 1 **đã sửa thật**:
  - nếu sau này có nhiều việc cùng chuyển một bài, nay **chỉ đúng một lệnh** «hẹn giờ / đăng» được gửi. Tôi thử từ 2 tới 32 việc chạy cùng lúc, 178 lần: lần nào cũng đúng một lệnh;
  - lớp chặn chỉ nhận dữ liệu dạng ảnh ở đúng lệnh tải ảnh; tải ảnh thật (đủ 6 loại đuôi) vẫn chạy bình thường.
- Mạng lỗi, website lỗi hay trả lời lạ **sau** lúc gửi: phần mềm vẫn **không bao giờ gửi lại**. Bị chặn **trước** lúc gửi (giờ sai, mất mạng lúc kiểm): bài vẫn là nháp, bấm lại được.
- Màn hình xác nhận (T-102) **làm được rồi**. **Việc của bạn:** không có.

### Việc 1: LC-T099-1 đóng thật

- `client.py:1415-1461`: `set.remove` vừa kiểm vừa bỏ mã trong **một** lệnh. Mã bài luôn là `int` đúng kiểu (`type(post_id) is int`; phần tử trong tập đều qua `_positive_id`), nên băm và so sánh chạy hết trong C, không nhả GIL giữa chừng (Python 3.12.15 của dự án). Luồng đến sau gặp `KeyError` → «chỉ bài nháp vừa tạo», 0 request.
- `probe_t099_l2.py luong` (1.172 ca, 0 hỏng): 2, 3, 5, 8, 16, 32 luồng chung một client, xuất phát cùng lúc (`Barrier`), đổi luồng liên tục (`sys.setswitchinterval(1e-6)`), lệnh kiểm nháp có/không chờ: 178 vòng, mỗi vòng **đúng 1** lệnh kiểm, **đúng 1** lệnh chuyển, 3 request, 1 «ok», còn lại «chỉ bài nháp vừa tạo» (gộp: 178 ok, 908 từ chối). 150 vòng trộn 3 luồng hình thức sai (giành rồi trả) với 3 luồng đúng: không vòng nào quá 1 lệnh chuyển; mã còn trong tập ⇔ chưa có lệnh chuyển. 40 vòng 4 luồng thử lại liên tục khi 3 lần kiểm đầu thiếu `Date`: đúng 1 lệnh chuyển, 1 ok. 40 vòng 5 luồng × 30 lần gọi khi lệnh chuyển lỗi 503: đúng 1 lệnh chuyển, 1 «không chắc», còn lại từ chối, 0 request.
- Ca xfail cũ của tôi (`test_lc_t099_1_hai_luong_chung_mot_client_chi_mot_lenh_chuyen`) nay qua. `probe_t099.py` lượt 1 chạy lại: 215 ca, 0 hỏng; hai luồng ra `['ReleaseError', 'ok']`, 1 lệnh chuyển.

### Việc 2: trả mã lại và giữ mã ở từng nhánh

Đọc từng nhánh `release_draft` (`client.py:1415-1490`) và thử từng nhánh (`probe_t099_l2.py truoc`, `sau`, `base`):

| Nhánh | Mã bài | Đã thử |
|---|---|---|
| Mã không phải `int`, không thuộc tập | Không giành, 0 request | |
| **Bị chặn trước lệnh chuyển:** hình thức sai (chữ lạ, rỗng, viết hoa, có dấu cách, byte, `draft`), Đăng ngay kèm giờ, giờ hẹn sai (thiếu, ngây, `date`, chuỗi, số, múi giờ trả `None`, năm 1), quá gần, quá khứ, quá xa (400 ngày, năm 9999), phiên có header đổi phương thức, `params`, `Content-Type`, lệnh kiểm nháp lỗi (500, 503, 404, 401, 301, hết giờ, mất mạng, lỗi lạ, JSON hỏng), thiếu/sai `Date`, `-0000`, đồng hồ lệch ±3 phút | **Trả lại** (`finally`); 0 lệnh chuyển, tối đa 1 request (lệnh kiểm, chỉ đọc); không «không chắc»; sửa xong gọi lại trên chính client: đi được, tổng đúng 1 lệnh chuyển | 35 nhánh (368 ca cùng 2 dòng dưới) |
| Website nói bài **không còn nháp** (publish, future, pending, private, trash, mã khác, danh sách, thiếu `status`, `Draft`) | **Không trả**; gọi lại `release_draft`, `set_seo_meta`, `set_featured_image`: từ chối, 0 request | 9 dạng |
| Lỗi thô trước lệnh chuyển (`tzinfo` hỏng) | Trả lại, 0 request (Ghi nhận L2-3) | 4 ca |
| **Đã gửi, website từ chối 4xx** (400, 401, 403, 404, 405, 409, 410, 413, 422, 429) | **Không trả**; câu «vẫn là nháp», không «không chắc» | 10 mã |
| **Đã gửi, kết quả không rõ:** hết giờ (đọc, nối), mất mạng, `ChunkedEncodingError`, `ContentDecodingError`, `SSLError`, `RequestException`, lỗi lạ trong adapter (`RuntimeError`, `RecursionError`, `MemoryError`, `UnicodeDecodeError`), 3xx (300 → 308 kèm `Location`), 5xx (500 → 504, 520, 599), JSON hỏng, HTML, rỗng, 204, danh sách, `null`, mã sai/chuỗi/`True`/`42.0`, thiếu/sai trạng thái; hẹn giờ trả giờ khác, thiếu giờ, giờ kèm đuôi múi giờ | **Không trả**; `unsure=True`; câu báo không chép lời máy chủ; gọi lại mọi lệnh ghi: từ chối, 0 request | 58 dạng trả lời, 399 ca, 0 hỏng |
| Hẹn giờ mà website đăng ngay | **Không trả**; `went_public=True` | |
| `BaseException` (kiểu `KeyboardInterrupt`) ở lệnh kiểm / ở lệnh chuyển | Trả lại / **không trả** (lỗi ra thẳng, không phải `ReleaseError`) | 7 ca, 0 hỏng |

- **Không có nhánh nào cho gửi lại khi website có thể đã nhận lệnh.** Chỉ hai chỗ thêm mã vào tập: `create_draft` (`:1211`) và `finally` (`:1461`); `give_back = False` (`:1458`) là lệnh cuối của khối `try`, `finally` chạy xong **trước** dòng gửi (`:1465`). Sau lệnh gửi, mọi lỗi kể cả lỗi lạ thành `ReleaseError` (`except Exception`); `_released_from` không ném lỗi thô (304 ca `link`, `date_gmt` lạ kiểu: 0 lỗi thô, 0 link ngoài website lọt).
- Thử «làm hỏng» trên bản sao (bỏ dòng `give_back = False`, tức trả mã cả khi sắp gửi): 3 file test T-099 **61 ca đỏ**, script dò dừng ngay ca đầu. Bộ test ghim đúng điều này.

### Việc 3: SL-T099-1 đóng, không mở lỗ khác, không chặn oan tải ảnh

- `_is_image_upload` (`client.py:298-316`) và một dòng ở `_is_plain_request` (`:257`): có `data` thì phải `POST /wp/v2/media` đúng chữ, không kèm `json`, đúng **một** header `Content-Type` (tên không phân biệt hoa thường), giá trị đúng chữ trong `IMAGE_TYPES`. Luật cũ vẫn giữ: header chỉ `Content-Type`, `Content-Disposition`; phiên không có `Content-Type`, `params`; không tên header nào có chữ «method».
- `probe_t099_l2.py anh` (361 ca, 0 hỏng): thân byte ở **12 đường còn lại** của `ALLOWED_ROUTES` (mẫu phủ đủ 13/13 đường) × 6 thân (`status=publish`, `status=future&date_gmt=…`, JSON, `id=7&featured_media=1`, `_method=DELETE`, byte PNG) × 4 kiểu header (không có, ảnh, form, JSON): **288/288 bị chặn, 0 request**. Ở `POST /wp/v2/media`: 26 dạng sai (không header, chỉ `Content-Disposition`, hai `Content-Type` khác hay giống, kèm `charset`, dấu cách đầu/cuối, chữ hoa, `svg`, form, multipart, JSON, `text/html`, giá trị byte, tên header có dấu cách, `X-HTTP-Method-Override`, header lạ, `CaseInsensitiveDict`, `OrderedDict`, kèm `json`, `bytearray`, `memoryview`, `str`, dấu `_RELEASE`, `params` `status`/`_method`), 7 phương thức khác, 8 dạng đường gần đúng, phiên có `Content-Type`: đều bị chặn, 0 request.
- **Không chặn oan:** `upload_media` với đủ 6 đuôi (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.avif`) gửi được, **nguyên byte**, đúng `Content-Type`; tên header viết thường hay hoa toàn bộ (một header) vẫn đi. Trong `seo_app/`, `app/` chỉ `_post_media` gửi `data` (grep). Ở `POST /wp/v2/media`, byte ảnh vẫn là thân «mờ» đúng thiết kế: với `Content-Type` ảnh, PHP không điền `$_POST`, WordPress lưu thành tệp Media, không đổi trạng thái bài nào.

### Việc 4: dấu `xfail` gỡ đúng R5, thử gộp với `main`

- R5: `git diff ce451fe..1040586`: `tests/test_la_chan_t099.py` chỉ xóa 5 dòng dấu (`@pytest.mark.xfail(…)` của LC-T099-1), `tests/test_soi_loi_t099.py` chỉ xóa 4 dòng dấu (SL-T099-1, phủ 5 ca); thân ca, điều kiện không đổi. `tests/test_wordpress_release.py` (+142) và `tests/test_soi_loi_t099.py` ở `7c2a827` (+317) chỉ thêm. `tests/test_la_chan_t099.py` trên nhánh: 3 passed.
- Gộp thử với `main` `fd28bbc` (T-100 lượt 3–4, T-106 + T-108, T-093, T-103, T-104, T-091, T-096 lượt 5): `git merge-tree --write-tree` ra cây `f1c8947` **không xung đột**; hai bên không chung file nào (nhánh 6 file, `main` 75 file kể từ `ce451fe`). `app/views/wordpress.py` của `main` (T-106) không còn tải ảnh, không gửi `data`. Chạy chọn lọc trên cây gộp **44 file** (mọi file test có tải ảnh, `/wp/v2/media`, `release_draft`, `_is_plain_request`, thân byte, cùng file test mới của `main` có dùng client WordPress: T-093, T-096, T-106, mở mọi trang): **6.823 ca: 6.816 passed, 5 xfailed, 1 skipped, 1 failed** (57 phút 27 giây). 5 xfailed là lỗi đã biết của `main` (LC-T093-2, LC-T093-3, SL-T041-8, SL-T106-1, SL-T108-1); LC-T093-2 (ảnh gửi nháp) vẫn xfail, không đổi. Ca hỏng `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` là **hỏng oan** do máy tải nặng (Ghi nhận L2-5): chạy riêng xen kẽ 3 lần mỗi cây, `main` `fd28bbc` **1 qua, 2 hỏng**, cây gộp 2 qua, 1 hỏng, cùng lỗi `DID NOT RAISE SiteIndexError`; file test và `seo_app/storage/site_index.py` hai cây giống hệt, T-099 không chạm. Grep cây gộp: trong `seo_app/`, `app/` chỉ `_post_media` gửi `data`; mọi file test gọi `_request` có `data=` (T-056, T-060, T-085, T-099) đều nằm trong 44 file đã chạy.

### Kết quả công cụ quét (lượt 2)

| Công cụ | Kết quả |
|---|---|
| ruff | `ruff check .`: sạch |
| bandit (`PYTHONUTF8=1`) | `client.py`: 0 |
| detect-secrets (`PYTHONUTF8=1`, mồi tiếng Việt cùng lần quét: bắt được) | 6 file đổi: 2 mục «Basic Auth Credentials», đều là một chữ mẫu có từ 23/10 (địa chỉ ví dụ chứa tên và mật khẩu giả, chú thích `client.py:954`, LC-T042-4) và dòng trích chữ đó trong biên bản Thợ Máy lượt 1; không phải bí mật |
| Script dò | `probe_t099.py` (lượt 1): 215 ca, 0 hỏng; `probe_t099_l2.py`: 2.307 ca, 2 cờ đều thuộc Ghi nhận L2-3 |

### Ghi nhận lượt 2 (không xếp lỗi)

1. **L2-1 (= G7 Soi Lỗi): giành mã chỉ khóa «chuyển» với «chuyển».** `set_featured_image`, `set_seo_meta` vẫn «kiểm tập → hỏi website → ghi». Thử (`probe_t099_l2.py ghi`): luồng ảnh đại diện qua bước kiểm trước khi luồng chuyển giành mã, lệnh hỏi của nó trả «nháp», rồi lệnh đăng đi, lệnh ghi ảnh đại diện tới website **sau** lệnh đăng. Chỉ gặp khi hai việc chạy song song trên chung một client (trái thiết kế); dữ liệu ghi là ảnh đại diện của chính bài, đã xác nhận. Thành điều kiện T-102.
2. **L2-2: bản chép client có tập mã riêng.** Client dùng phiên thật chép được bằng `copy.deepcopy` và `pickle` (cách `st.cache_data` trả kết quả): bản chép giữ mã bài nhưng tập riêng, lớp giành mã không còn tác dụng giữa các bản. Trái thiết kế (client tạo trong lần bấm); thành điều kiện T-102.
3. **L2-3: giờ hẹn có `tzinfo` hỏng** (`utcoffset` ném `ValueError`, `RuntimeError`) ra khỏi `release_draft` dạng lỗi thô (không phải `ReleaseError`); mã đã trả lại, 0 request. App không tạo được giờ như vậy (`when_utc` từ `schedule.local_to_utc`, `ZoneInfo`). Hai «cờ» của script là chữ trong chính lỗi giả của tôi, không phải lời website.
4. **L2-4 (= G8 Soi Lỗi):** luồng bị từ chối vì luồng khác đang giữ mã nhận câu «chỉ bài nháp vừa tạo» (nghĩa đúng là «đang bận»). Chỉ gặp khi trái thiết kế; chiều an toàn.
5. **L2-5 (không thuộc T-099, cho Chỉ Huy):** ca `test_r2_long_lock_in_other_thread_is_busy_not_deleted` (Soi Lỗi T-037) hỏng cả trên `main` khi máy tải nặng. Luồng giữ khóa chỉ chờ 10 giây (`release.wait(10)`), trong lúc đó test làm 5 thao tác nối tiếp, cộng các hằng chờ khóa (`_HEALTH_TIMEOUT`, `_WRITE_TIMEOUT` 1 giây, `_SQLITE_TIMEOUT` 0,1 giây) đã khoảng 8 giây; máy chậm thì quá 10 giây, luồng nhả khóa, lệnh ghi cuối đi được. Nên nới thời gian giữ khóa của test (đổi test, cần Chỉ Huy duyệt R5); không phải lỗi ứng dụng.
6. Ghi nhận 1 → 4 của lượt 1 giữ nguyên (`modified_gmt` «nên», `from exc`, G2–G6, `timezone_string`).

### Điều kiện lượt 2

1. **T-102 nối màn hình xác nhận được** khi nhánh này đã lên `main`. Giữ Điều kiện 2 của lượt 1 (một lần `release_draft` mỗi lần bấm, trên chính client vừa tạo nháp; không giữ client trong `st.session_state`, `st.cache_resource`, biến toàn cục; ghi kết quả trước lệnh `st.*` tiếp theo; `unsure`, `went_public` thì khóa gửi lại, hiện `str(err)` bằng chữ thường; `when_utc` từ `local_to_utc`, cùng giá trị cho mã băm), thêm:
   - `release_draft` là lệnh **cuối cùng** trên client trong lần bấm, chạy **nối tiếp** sau ảnh đại diện, ghi SEO; không chạy song song lệnh nào khác trên cùng client (L2-1);
   - tạo client ngay trong lần bấm; không chép (`copy.deepcopy`, `pickle`), không trả qua `st.cache_data` (L2-2);
   - ngoài `ReleaseError`, bắt thêm `Exception` quanh `release_draft`: hiện câu cố định, coi như **có thể đã gửi** (khóa gửi lại, dặn kiểm trang quản trị), không hiện lời lỗi gốc (L2-3).
2. **Trước khi bật công tắc Hẹn giờ, Đăng ngay (LC-T094-41):** giữ Điều kiện 3 của lượt 1 (thử thật LC-T094-44; cân nhắc `modified_gmt`).

**Kết luận lượt 2:** **ĐẠT.** LC-T099-1, SL-T099-1 đóng thật; 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp còn mở; Lá Chắn không có lỗi mới. Gộp `main` được ngay. T-102 nối màn hình xác nhận được (giữ điều kiện trên).

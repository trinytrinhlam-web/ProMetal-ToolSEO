# Báo cáo T-099 · Client WordPress: hẹn giờ, đăng ngay, đọc trạng thái · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-099](../tickets/T-099-client-hen-gio-dang-ngay.md) |
| Nhánh | `team/T-099` (đầu nhánh `3c60948` = `main` `b241e79` + T-091); thử gộp với `main` `209615a` (mới nhất trên máy) |
| Ngày nộp | 2026-10-29 |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm soát R5). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T099-1). **Không lỗi nào bắt buộc sửa trước Lá Chắn** |

## Tóm tắt (cho chủ dự án)

- **Đường đổi bài từ nháp sang hẹn giờ / đăng ngay chạy đúng và chặt** trên website giả riêng của tôi (giữ trạng thái bài như WordPress thật, có đồng hồ riêng, làm đúng luật «hẹn giờ sát giờ thì WordPress đăng luôn»):
  - chỉ bài nháp **chính lần gửi này** tạo mới chuyển được. Bài của người khác, bài đã đăng, đã hẹn giờ, chờ duyệt, riêng tư, trong thùng rác, bài đã xóa, mã lạ, mã quá lớn: không có lệnh ghi nào lên website;
  - ngay trước khi chuyển, phần mềm hỏi lại website bài còn là nháp không, và lấy giờ của website để kiểm giờ hẹn. Giờ đã qua, gần hơn 10 phút, xa hơn 1 năm, đồng hồ máy tính lệch website hơn 2 phút, website không cho biết giờ: chặn, bài vẫn là nháp;
  - khi không chắc lệnh đã chạy chưa (mất mạng, hết giờ, chuyển hướng, lỗi máy chủ, trả lời lạ hay thiếu trường), phần mềm báo «có thể đã hẹn giờ/đăng, mở trang quản trị kiểm tra» và **không bao giờ tự gửi lại**, kể cả khi bấm lại;
  - hẹn giờ mà website lỡ đăng ngay: câu báo **KHẨN** kèm cách chuyển về nháp, đúng `security.md` mục 7.
- **1 lỗi nhỏ (Thấp), không cần sửa trước Lá Chắn:** lớp chặn lệnh gọi WordPress chỉ soát thân lệnh dạng JSON. Thân dạng byte thô thì không soát, nên về lý thuyết một đoạn code sau này gửi nhầm «status=publish» bằng byte thô sẽ lọt lớp chặn. Hôm nay WordPress **không đọc** thân dạng đó, nên chưa có lỗ thật; nên sửa cho lớp chặn tự đủ, không dựa vào WordPress.
- **Một điểm Lá Chắn để «nên»** chưa làm (Thợ Máy đã nêu): chưa so giờ sửa bài để phát hiện ai đó sửa nháp trong trang quản trị giữa lúc tạo và lúc đăng. Khoảng đó chỉ vài giây đến vài phút trong cùng một lần bấm.
- **Việc của bạn:** không có.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t099.py` | Mới: 171 ca (166 qua, 5 `xfail(strict=True)` của SL-T099-1). Website giả riêng `_WpSite` (adapter `requests`): giữ bài, trạng thái, `date_gmt`, đồng hồ máy chủ (header `Date`), luật `wp_insert_post` «`future` chưa tới 60 giây sau giờ máy chủ → `publish`», chèn câu trả lời lạ theo từng đường. Không dùng `FakeWordPress`, hàm dựng site hay bảng kỳ vọng của Thợ Máy |
| `docs/team/reports/T-099-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác. Không gọi website thật (bộ chặn mạng của `tests/conftest.py` bật suốt; script dò ngoài pytest tự chặn socket ở dòng đầu). Hai chỗ về hành vi WordPress lõi tôi đọc thẳng mã nguồn WordPress (`class-wp-rest-request.php`, `class-wp-rest-server.php`, nhánh `master` trên GitHub, đọc 2026-10-29), không gọi website nào của dự án.

## Kiểm theo yêu cầu

### 1. Chỉ nháp do app tạo, đúng mã, mới được hẹn giờ / đăng

| Thử | Kết quả |
|---|---|
| Mã `True`, `"42"`, `42.0`, `0`, `-42`, `MAX_ID + 1`, `2**64`, `None`, `[42]`, mã bài khác có trên site (43, nháp của người khác) | `ReleaseError` «chỉ bài nháp phần mềm vừa tạo», **0 request**, bài 43 vẫn nháp |
| Bài do **client khác** (lần gửi khác) tạo | Từ chối, 0 lệnh ghi |
| Site báo bài đang `publish`, `future`, `pending`, `private`, `trash`, `Draft`, `"draft "`, `auto-draft`, `inherit` | Chỉ một lệnh đọc, **không lệnh chuyển**; mã bài bị bỏ khỏi danh sách bài của client: gọi lại → 0 request |
| Bài bị xóa (404 ở lệnh kiểm) | Không lệnh chuyển; câu báo không chép lời máy chủ, địa chỉ website |
| Câu trả lời lệnh kiểm lạ: mã khác, mã chữ `"42"`, mã `True`, thiếu mã, thiếu trạng thái, danh sách, chữ, `null` | Không lệnh chuyển, bài vẫn nháp |
| Lệnh kiểm lỗi: 500, 404, 301, mất mạng, hết giờ, không phải JSON | Báo «vẫn là nháp», `unsure=False`, 0 lệnh ghi; bài **vẫn** của client, lần sau (site ổn) hẹn giờ được, đúng 1 lệnh chuyển |
| Hình thức sai: `"Publish"`, `"draft"`, `"private"`, `"pending"`, `None`, `b"publish"`, `"future "`; Đăng ngay kèm giờ; Hẹn giờ thiếu giờ | 0 request, bài vẫn của client |
| `post_statuses` đọc 250 bài rồi `release_draft(1000)` | Từ chối: mã đọc từ website không thành «bài app được sửa» |

### 2. Trạng thái trước và sau khi đổi

Website giả giữ trạng thái thật, nên mỗi ca kiểm **bài trên site**, không chỉ câu báo:

- Hẹn giờ đúng: đúng thứ tự `GET /wp/v2/posts/42?context=edit&_fields=id,status` (ngay trước) rồi **một** `POST /wp/v2/posts/42?_fields=id,status,date_gmt,link` thân đúng `{"status": "future", "date_gmt": "2026-11-03T01:00:00"}`; bài trên site thành `future` đúng giờ; kết quả trả `future` và đúng chuỗi giờ.
- Đăng ngay: thân đúng `{"status": "publish"}`, bài thành `publish`.
- Sau khi chuyển: `release_draft` lần nữa (cả hai hình thức), `set_featured_image`, `set_seo_meta` vào bài đó đều bị chặn, 0 request, bài giữ `future`.
- Mọi ca bị chặn trước lệnh chuyển: bài trên site vẫn `draft`, danh sách lệnh ghi chỉ có lệnh tạo nháp lúc đầu.

### 3. Không gửi lại khi không chắc

18 câu trả lời lạ cho lệnh hẹn giờ: mất mạng, hết giờ, 301 có `Location`, 302 không `Location`, 500, 502 HTML, 503 rỗng, 200 không phải JSON, 200 danh sách, thiếu trạng thái, thiếu mã, mã khác, mã chữ, vẫn `draft`, `pending`, `future` thiếu `date_gmt`, `date_gmt` lệch 1 giây, `date_gmt` có `Z`.

- Mọi ca: `ReleaseError(unsure=True)`, câu có «có thể đã» (hoặc «khác giờ đã chọn»), **không** chép lời máy chủ (`MOI-T099`, `evil`), không chép địa chỉ website.
- Đúng **1** lệnh chuyển; gọi lại `release_draft` → 0 request (mã bài đã bỏ trước khi gửi).
- Đăng ngay với 7 ca tương tự: câu «có thể đã hiện công khai».
- 4xx (400, 401, 403, 404, 409, 429): «vẫn là nháp», `unsure=False`, không chép lời máy chủ.
- Site đồng hồ chạy quá giờ hẹn giữa lúc kiểm và lúc chuyển (luật WordPress đổi `future` thành `publish`): `went_public=True`, câu **KHẨN**, bài trên site là `publish`, đúng 1 lệnh chuyển, không lệnh nào khác.

### 4. Giờ hẹn

- **Biên theo giờ máy chủ** (header `Date`): đã qua 1 giây, đúng bây giờ, 9 phút 59,999 giây: chặn. 10 phút, 10 phút + 0,5 giây, 365 ngày, **365 ngày + 0,5 giây** (gửi đúng 365 ngày vì bỏ phần lẻ giây): gửi được. 365 ngày + 1 giây, 11 năm: chặn.
- **Sai dạng** (0 request, bài vẫn của client): giờ không múi giờ, `date`, chữ, số, `datetime.max` ở múi −5 (tràn khi đổi UTC).
- **Múi giờ bất kỳ:** `03:30:59,9` ở UTC+2:30 → gửi `2026-11-03T01:00:59` (đổi UTC, bỏ phần lẻ giây).
- **Header `Date`:** thiếu, rác, `-0000`, dạng asctime, giây 60, có tab: chặn, `unsure=False`, 0 lệnh ghi. `+0700`, RFC 850, năm 2 chữ số, `UT`: nhận. Lệch +3 phút, −3 phút: chặn; +1 phút 59 giây: nhận.
- **Đồng hồ máy lệch** ±3 phút, +400 ngày: chặn.
- **Giờ mùa hè** (`local_to_utc`, Europe/Berlin): 29/03/2026 02:30 (giờ không có) và 25/10/2026 02:30 (giờ lặp) bị từ chối; giờ hè/đông đổi đúng (06:00, 07:00 UTC). Giờ Việt Nam 08:00:45 → `2026-11-03T01:00:00`, nhãn «Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)».
- Dò thêm `parse_server_date` (script `probe_date.py`): mọi chuỗi sai đều ra `None` hoặc ra giờ lệch xa (năm `0001` thành 2001, `EST`), và bước so lệch 2 phút chặn tiếp. Không chuỗi nào làm hàm ném lỗi.

### 5. Không đường nào khác đổi `status` / gửi `date_gmt`; test canh T-037 (R5)

- Gọi thẳng `client._request("POST", "/wp/v2/posts/<mã>", …)` theo 19 cách: không dấu (`publish`, `date_gmt`, `date`), dấu giả (`object()`, `True`, chữ `"_RELEASE"`), dấu thật mà sai khuôn (thêm khóa, `date`, `private`, `pending`, `trash`, `future` thiếu giờ, giờ có `Z`, có `+07:00`, chữ số toàn khổ, `_fields` khác, thêm tham số, thêm header, `status` dạng byte): **mọi cách bị chặn, 0 request**, bài vẫn nháp.
- Dấu thật trên đường khác (`POST /wp/v2/posts`, `/pages/42`, `/media/42`, `PUT`, `PATCH`, đuôi `/`): chặn.
- Lệnh tạo nháp chỉ gửi `"status": "draft"`, không `date`, `date_gmt`; lệnh ảnh đại diện chỉ `{"featured_media": 7}`.
- **Khe tìm ra:** thân `data=` (byte) không qua luật khóa JSON, xem **SL-T099-1**.
- **R5:** `tests/test_soi_loi_t037.py::test_status_publish_or_future_only_in_list_published` chỉ đổi danh sách kỳ vọng (vẫn so `==`, đúng 4 cặp đã duyệt: `list_published` `'publish'`, `release_draft` `'future'` và `'publish'`, `post_statuses` `POST_STATUS_FILTER`) và lời mô tả. Phần duyệt cây cú pháp giữ nguyên. Đúng điều kiện Chỉ Huy duyệt. Không test cũ nào khác bị đổi (`git diff 9e0115e..3c60948 -- tests/`: thêm 2 file test mới, sửa đúng một test canh nói trên).

### 6. Không lùi T-059, T-086, T-089, T-091

- Diff `client.py` chỉ xóa: lời đầu module, dòng import, một chú thích `ALLOWED_ROUTES`, dòng `ALLOWED_PARAMS` của `GET /wp/v2/posts` (thêm `include`, `context`), `_FORBIDDEN_JSON_KEYS` (thêm `date`), `_is_plain_request` (chữ ký thêm `release`, hai dòng luật thân JSON) và lời gọi trong `_request`. `_json`, `_positive_id`, `_without_lone_surrogates`, `_ability_confirms`, `_own_draft`, `create_draft`, `set_seo_meta`, `set_featured_image`, `create_draft_with_images` **không đổi dòng nào**. `ALLOWED_ROUTES` không thêm đường.
- Nơi gọi: `release_draft`, `post_statuses`, `timezone_warning`, `schedule.py` chưa có ai gọi ngoài client và test (T-102 sẽ gọi). `GET /wp/v2/posts` chỉ do `list_published` (`status=publish`, không `context`) và `post_statuses` dùng: luật giá trị mới không chặn oan `list_published`.
- Test ghim hành vi: grep theo tên (`_FORBIDDEN_JSON_KEYS`, `ALLOWED_*`, `_created_post_ids`, `_positive_id`, `MAX_ID`, `check_connection`, `ConnectionInfo`…) **và** theo hành vi (`include`, `date_gmt`, `"date"`, `status` publish/future, `send_draft`, `app.views.write`, file nhập `test_app_images`, `test_t086_send_state`, `fake_wordpress`): 88 file, chạy trên bản gộp (mục 7).

### 7. Gộp thử với `main` mới nhất trên máy

- `git merge-tree --write-tree main HEAD` (`main` `209615a`, đã có T-091, T-096 lượt 5, T-097 lượt 2, T-098 lượt 4, T-103): **không xung đột** (cây `3f3ecf0`). `main` chỉ đổi `seo_app/publish/render.py`, `review.py` trong vùng gần T-099; không đụng file của T-099.
- Chạy 88 file test liên quan trên bản gộp (thêm file test của tôi), chia 4 phần chạy song song, mỗi phần một bản sao riêng: **11.499 passed, 26 xfailed, 1 skipped, 0 failed** (2.980 / 3.145 / 2.827 / 2.547 passed). Một cảnh báo pydantic có sẵn ở `tests/test_soi_loi_t028.py`, không liên quan.

### Đột biến (đo sức test)

26 đột biến trên bản sao (script `mutate099.py`), mỗi lần chạy `tests/test_soi_loi_t099.py`, `tests/test_wordpress_release.py`, `tests/test_publish_schedule.py`. **26/26 bị bắt**, và đột biến nào cũng có ca của file Soi Lỗi bắt (test độc lập tự đủ sức, không dựa vào test của Thợ Máy).

| Đột biến | Ca hỏng: Soi Lỗi / Thợ Máy (`release`) / `schedule` |
|---|---|
| M1 dấu giả nào cũng nhận | 3 / 6 / 0 |
| M2 bỏ kiểm bài của client | 31 / 16 / 0 |
| M3 site báo không còn nháp mà không bỏ mã bài | 9 / 9 / 0 |
| M4 chỉ bỏ mã bài khi thành công | 18 / 27 / 0 |
| M5 bỏ kiểm lệch đồng hồ | 5 / 8 / 6 |
| M6 biên 10 phút thành 9 phút | 1 / 3 / 0 |
| M7 nhận quá 365 ngày thêm 1 ngày | 1 / 1 / 2 |
| M8 bỏ so `date_gmt` trả về | 3 / 3 / 0 |
| M9 bỏ câu báo khẩn đăng ngay | 1 / 1 / 0 |
| M10 4xx coi như không chắc | 6 / 6 / 0 |
| M11 5xx coi như vẫn là nháp | 4 / 4 / 0 |
| M12 header `Date` không múi giờ coi là UTC | 2 / 2 / 2 |
| M13 thân lệnh chuyển cho thêm khóa | 1 / 3 / 0 |
| M14 `date_gmt` chỉ khớp đầu chuỗi | 2 / 1 / 0 |
| M15 bỏ kiểm giá trị `include` | 7 / 12 / 0 |
| M16 `post_statuses` thêm mã vào bài của client | 1 / 2 / 0 |
| M17 bỏ khoảng −12…14 của `gmt_offset` | 1 / 2 / 0 |
| M18 thiếu `Date` thì lấy đồng hồ máy | 6 / 13 / 0 |
| M19 giờ hẹn gắn UTC thay vì đổi múi giờ | 4 / 1 / 2 |
| M20 không chắc thì gửi lại một lần | 8 / 19 / 0 |
| M21 không bỏ phần lẻ giây khi so khoảng | 1 / 0 / 1 |
| M22 kiểm nháp nhận chữ hoa, dấu cách thừa | 2 / 1 / 0 |
| M23 kiểm nháp nhận mã dạng chữ | 1 / 1 / 0 |
| M24 bỏ lớp chặn `date_gmt` ngoài lệnh chuyển | 1 / 2 / 0 |
| M25 `status` của lệnh đọc nhận mọi giá trị | 2 / 4 / 0 |
| M26 lệnh kiểm nháp lỗi mà vẫn gửi lệnh chuyển | 7 / 6 / 0 |

## Lỗi tìm ra

### SL-T099-1 · Thấp · Thân `data=` (byte) không qua luật khóa JSON / `status` của lớp chặn

- **Chỗ:** `seo_app/wordpress/client.py:215-292` (`_is_plain_request`). Luật «khóa thân thuộc `ALLOWED_JSON_KEYS`, không `id`, `name`, `date`, `date_gmt`, `status` chỉ `draft`» (LC-T060-1, LC-T094-22) chỉ áp cho `json=`. `data=` (byte) được nhận ở **mọi** đường, và `requests` không gắn `Content-Type` cho byte.
- **Thử** (`probe_data_body.py`, `_request` thật, website giả ghi lại lệnh): `POST /wp/v2/posts/42` thân `status=publish`; `status=future&date_gmt=…`; `id=7&featured_media=1`; `POST /wp/v2/posts` thân `status=publish&title=x`; `POST …/seo-data-update/run` thân `name=…`; cả `GET /wp/v2/posts/42` có thân: **đều được gửi đi**, không `Content-Type`.
- **Vì sao hôm nay chưa thành lỗ:** đọc mã WordPress lõi: với `POST`, tham số thân lấy từ `$_POST` của PHP (`WP_REST_Server::serve_request`), mà PHP chỉ điền `$_POST` khi `Content-Type` là dạng form. Dòng «thiếu `Content-Type` thì coi như dạng form» của `WP_REST_Request::parse_body_params` chỉ chạy với phương thức **khác** `POST` (`get_parameter_order`). Đổi phương thức (`_method`, `X-HTTP-Method-Override`) đã bị chặn; `Content-Type` chỉ nhận loại ảnh. Hiện chỉ `_post_media` dùng `data=` (đúng đường `/wp/v2/media`, có `Content-Type` ảnh).
- **Hậu quả:** lời hứa của LC-T094-22 và chú thích `_RELEASE` («chỉ lệnh mang dấu này mới gửi được `status` khác `draft` và `date_gmt`») đang dựa vào cách PHP, WordPress đọc thân lệnh, không vào lớp chặn. Một đoạn code sau này lỡ gửi `data=` vào đường bài viết sẽ không bị lớp chặn bắt. Có từ trước T-099 (T-060, T-085), lộ ra khi soát mục 5.
- **Test:** `test_sl_t099_1_than_data_khong_qua_duoc_lop_chan` (5 xfail).
- **Gợi ý:** chỉ nhận `data` ở đúng `POST /wp/v2/media` và chỉ khi có `Content-Type` thuộc `IMAGE_TYPES`; đường khác có `data` thì từ chối.

## Ghi nhận (không tính lỗi, để Lá Chắn cân nhắc)

- **G1 · LC-T094-23 «nên» so `modified_gmt` chưa làm** (Thợ Máy đã nêu). Ai đó sửa nháp trong trang quản trị giữa lúc tạo và lúc chuyển thì bài lên công khai khác bản đã xác nhận (rủi ro dòng 9 của Lá Chắn T-094). Khoảng đó là vài giây đến vài phút trong cùng một lần bấm (T-102). Lá Chắn quyết có cần trước T-102 không.
- **G2 · Câu báo chưa sát ở hai ca hiếm (an toàn, chỉ là chữ):** hẹn giờ mà câu trả lời **thiếu** `date_gmt` dùng câu «giờ hẹn khác giờ đã chọn… sửa giờ hẹn»; đăng ngay mà site trả `future` (nháp đã được người khác đặt ngày tương lai) dùng câu «có thể đã hiện công khai hoặc vẫn là nháp», thực ra bài đã hẹn giờ. Cả hai đều `unsure=True`, khóa gửi lại, dặn mở trang quản trị.
- **G3 · 4xx coi là «vẫn là nháp»:** đúng với WordPress lõi (403 `rest_cannot_publish`, 400 tham số, 401 đăng nhập đều trả trước khi sửa bài). 404 (bài vừa bị xóa) thì câu ghép thành «có thể đã bị xóa (mã 404). … bài vẫn là nháp trên website», hơi ngược, không hại. Plugin trả 4xx **sau** khi đã sửa bài thì câu «vẫn là nháp» sai, nhưng không gửi lại.
- **G4 · Header `Date` lặp hai lần** (`requests` nối thành «X, X») hay dạng asctime: bị chặn «không đọc được giờ của website». Đúng LC-T094-24 (sai dạng → chặn); máy chủ chuẩn không gửi vậy. Nếu gặp thật thì người dùng hẹn giờ trong trang quản trị.
- **G5 · Giờ máy chủ là giờ của máy chủ web / CDN** (header `Date`), không phải đồng hồ PHP của WordPress. Hai đồng hồ lệch hơn ~9 phút (CDN đặt `Date`, máy gốc lệch giờ) thì WordPress có thể đăng ngay; app bắt được ngay sau lệnh (`went_public`, câu khẩn). Hạn chế của thiết kế, biên 10 phút che phần lớn.
- **G6 · `timezone_warning`** so độ lệch **hiện tại** của múi giờ app (Thợ Máy đã nêu): chỉ sai với múi có giờ mùa hè; giờ Việt Nam không bị.

## Không chặn oan

Những ca đúng đều gửi được: biên 10 phút và 365 ngày, phần lẻ giây ở biên, header `Date` có `+0700`, RFC 850, năm 2 chữ số, lệch 1 phút 59 giây; lệnh kiểm lỗi một lần rồi lần sau vẫn hẹn giờ được; bị chặn vì giờ thì bài vẫn của client (Thợ Máy cũng có ca này); `list_published` vẫn chạy với luật giá trị mới; `post_statuses` 250 mã chia đúng 3 lệnh ≤ 100 mã.

## Lệnh đã chạy

- `uv run pytest tests/test_soi_loi_t099.py`: 166 passed, 5 xfailed.
- Bản sao nhánh: `tests/test_soi_loi_t099.py tests/test_wordpress_release.py tests/test_publish_schedule.py`: 467 passed, 5 xfailed.
- Bản gộp với `main` `209615a`, 88 file liên quan: 11.499 passed, 26 xfailed, 1 skipped, 0 failed.
- Đột biến: 26/26 bị bắt.
- `uv run ruff check .`: sạch. `detect-secrets scan tests/test_soi_loi_t099.py` (`PYTHONUTF8=1`): sạch.
- Script dò, đột biến: thư mục ghi chú chung `T-099-soi-loi-scripts/` (`probe_date.py`, `probe_data_body.py`, `mutate099.py`).

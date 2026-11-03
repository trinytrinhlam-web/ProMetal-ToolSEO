# Biên bản bảo mật T-115 · Client WordPress: so `modified_gmt` ngay trước lệnh chuyển (LC-T094-23) · rút gọn (W2, W3)

> **Model:** chạy Claude Opus 5.5 (phiên Lá Chắn này không chạy Fable); cần kiểm lại bằng Claude Fable như các biên bản trong T-116.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | T-115 (phiếu ở checkout chính; Thợ Máy lượt 1 `496e8da`, `00bad96`, lượt 2 `a7572f7`; Soi Lỗi `d121d7c`; gộp `main` `935d381` ở `c984878`) |
| Phạm vi | **Rút gọn: W2, W3, LC-T094-23** và 5 câu Chỉ Huy hỏi. Code: `seo_app/wordpress/client.py` (`_POST_FIELDS`, `_POST_META_FIELDS`, `_RELEASE_CHECK_FIELDS` thêm `modified_gmt`; `_modified` riêng từng client; `_remember_modified`, `_taint_modified`, `_same_modified`; `create_draft`, `_own_draft`, `_seo_via_meta`, `set_featured_image` nhớ/đánh dấu; `release_draft` so trước lệnh chuyển, câu `_RELEASE_CHANGED`). R5: chuỗi `_fields` mong đợi, câu trả lời giả có `modified_gmt`, `SAFE_FIELDS` T-061, gỡ `xfail` LC-T102-1, SL-T115-1. Gốc: biên bản đầy đủ T-102 (LC-T094-23 «nên làm cùng lúc», LC-T102-1) |
| Ngày | 2026-11-02 (làm 17:28 → 19:00 +07, giờ máy đo bằng `date`; 3 lô test nền chết khi phiên dừng lúc 17:3x, chạy lại lô gộp T-112 18:44 → 18:54) |
| **Kết luận** | **ĐẠT**, **gộp `main` được ngay**. **LC-T094-23 đóng đủ**, kể cả phần «nên» (so `modified_gmt`); LC-T102-1 nay còn bị chặn thêm ở lớp client. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp; Lá Chắn không có lỗi mới; SL-T115-1 đóng (đồng ý Soi Lỗi). Không đường nào tới `future`/`publish` bỏ qua phép so; giá trị nhớ không bị câu trả lời lạ «rửa». **Ba giới hạn** của cách so (cùng giây; khe giữa lệnh đọc kiểm và lệnh ghi; sửa chỉ meta) **nên ghi sổ rủi ro một dòng**, không bắt buộc sửa trước khi bật công tắc. Gộp với `origin/main`: không xung đột, code y hệt nhánh. **Gộp với `team/T-112`: không xung đột chữ nhưng 1 ca test của T-112 đỏ** (`test_t112_release_rules.py::test_schedule_goes_on_but_warns_what_is_missing`): T-112 cho Hẹn giờ đi tiếp khi lệnh ảnh đại diện lỗi 500, T-115 chặn. **Đề nghị giữ luật của T-115** (WordPress 6.9.4 đổi giờ sửa trước khi xử lý ảnh đại diện, nên lệnh lỗi vẫn có thể đã sửa bài); T-112 đổi ca đó theo R5 khi gộp (mục 5) |

## Tóm tắt (cho chủ dự án)

- Trước khi hẹn giờ hay đăng, phần mềm nay hỏi lại website «bài nháp có bị ai sửa sau lần phần mềm ghi cuối không». Bị sửa (trong trang quản trị, plugin, người khác), hay website trả lời không rõ ràng, thì phần mềm **không hẹn giờ, không đăng**, bài vẫn là nháp, và báo bạn mở trang quản trị xem lại.
- Tôi đã thử nhiều cách đánh lừa (website trả lời lạ, trả giờ sai dạng, lệnh ghi lỗi giữa chừng): không cách nào làm phần mềm đăng bài đã bị sửa mà nó không biết.
- Còn ba khe rất hẹp WordPress không cho phép bịt (ví dụ ai đó sửa bài đúng trong cùng một giây với phần mềm). Tôi đề nghị ghi vào sổ rủi ro; không cần sửa trước khi bật Hẹn giờ/Đăng ngay.
- **Việc của bạn:** quyết định ghi sổ rủi ro dòng đề xuất ở mục «Điều kiện» (hay yêu cầu thu hẹp thêm khe thứ ba).

## Kết quả theo câu Chỉ Huy hỏi

### 1. LC-T094-23 đóng ở mức nào: **đóng đủ (cả phần «nên»)**

LC-T094-23 (biên bản T-094): phần bắt buộc (chỉ bài client này vừa tạo trong lần gửi, hỏi lại còn nháp ngay trước lệnh, bỏ mã sau khi chuyển) đã có từ T-099; phần **«nên»** («so `modified_gmt` với giá trị app nhận ở lệnh ghi cuối của mình… → dừng, báo») nay có:

- Nhớ: `create_draft` (`client.py:1290`, chỉ khi website xác nhận nháp), `_seo_via_meta` (`:1430`), `set_featured_image` (`:1470`) nhớ `modified_gmt` của câu trả lời **chỉ khi** câu trả lời đúng là của nháp đó (lượt 2, SL-T115-1). Lệnh ghi lỗi giữa chừng, câu trả lời lạ: đánh dấu «không biết» (`_taint_modified`).
- Kiểm trước mỗi lệnh ghi: `_own_draft` (`:1358`) so giờ sửa đang có với giá trị nhớ; khác thì đánh dấu «không biết» (lần sửa ngoài app giữa hai lệnh ghi của app không bị lệnh ghi sau xóa dấu vết).
- So trước lệnh chuyển: `release_draft` (`:1539-1550`) lấy `modified_gmt` từ chính lệnh kiểm nháp (`_RELEASE_CHECK_FIELDS = "id,status,modified_gmt"`), `known is None or modified != known` → `ReleaseError(_RELEASE_CHANGED)`, `give_back = False` (gọi lại trên client đó: 0 request), không gửi lệnh chuyển.
- Ghi SEO qua Abilities: app hỏi lại bài sau lệnh ghi (`_own_draft`, có từ T-042) nên Abilities có đổi giờ sửa thì cũng thành «không biết» (Soi Lỗi, script của tôi: chặn); không đổi thì giữ giá trị nhớ, vẫn chuyển (đáp ứng yêu cầu 4 của phiếu, không cần lệnh đọc thêm).

### 2. Có đường nào tới `future`/`publish` không qua phép so: **không**

- Lệnh chuyển chỉ gửi ở một chỗ, `release_draft` (`:1566`, mang dấu `_RELEASE`, khuôn `_is_release_request`); phép so (`:1545`) đứng **trước** `release_time_problem` và lệnh gửi, không tham số nào bỏ qua (đọc mã bằng `ast`: phép so đứng trước lời gọi gửi; `_RELEASE` chỉ dùng trong `release_draft` và lớp chặn). Mã bài phải thuộc `_created_post_ids`, mà mọi chỗ thêm mã vào tập (`create_draft`, trả mã khi bị chặn trước lệnh chuyển) đều đã có mục trong `_modified`; mục `None` là chặn.
- App (T-102) chỉ gọi `release_draft` ở `release_post`; không đổi ở phiếu này.

### 3. Giá trị nhớ không bị «rửa» bởi câu trả lời lạ: **đúng**

`probe_t115.py` (46 ca, 0 hỏng; dùng WordPress giả có đồng hồ `_ModSite` của Soi Lỗi):

| Thử | Kết quả |
|---|---|
| Sửa ngoài app sau khi tạo, rồi **hai** lệnh ghi của app trả lời đúng (ảnh đại diện, SEO) | Vẫn chặn: «không biết» không bao giờ trở lại «biết» (`_remember_modified` giữ `None`) |
| Lệnh ảnh đại diện trả lời lạ (bài khác, không phải dict, `pending`, mã dạng chữ) kèm đúng giờ sửa mới | Chặn (lượt 2) |
| Lệnh ảnh đại diện đã ghi mà mất câu trả lời (hết giờ) | Chặn |
| Lệnh tạo không trả hay trả sai dạng `modified_gmt` (thiếu, `null`, `""`, số, có dấu cách, đuôi `Z`) | Chặn từ đầu |
| Lệnh kiểm trước lệnh chuyển trả 12 dạng lạ (thiếu, `null`, `""`, `0`, `[]`, `{}`, đuôi `Z`, `.000`, dấu cách, chữ `t` thường, giờ khác, năm 9999) | Chặn, 0 lệnh chuyển |
| Không ai sửa (Hẹn giờ, Đăng ngay; SEO qua meta hay Abilities không đổi giờ) | Vẫn chuyển (không chặn oan) |
| Abilities đổi giờ sửa | Chặn |
| Hai client | Client khác không chuyển được bài của client này; tập giá trị nhớ riêng |

### 4. Ba giới hạn: **ghi sổ rủi ro, không bắt buộc sửa trước khi bật công tắc**

Tự tái hiện cả ba bằng script (lệnh chuyển vẫn đi):

1. **Cùng giây:** `modified_gmt` của WordPress tính tới giây; sửa trong cùng giây với lệnh ghi cuối của app thì giờ không đổi.
2. **Khe giữa lệnh đọc kiểm và lệnh ghi của app** (vài trăm mili giây): lệnh ghi của app đặt giờ sửa mới, client nhớ giờ đó nên lần sửa kia bị «rửa» (script: bài lên với nội dung người khác vừa sửa).
3. **Sửa chỉ meta** (đổi ảnh đại diện bằng hộp chọn ảnh của trình soạn cổ điển qua AJAX, plugin ghi khóa meta riêng): giờ sửa không đổi (script: ảnh đại diện lúc chuyển là ảnh người khác đặt).

Vì sao chấp nhận được: WordPress không có khóa lạc quan (`If-Match`) nên client không bịt được khe 1, 2; cả ba cần người **đang sửa đúng bài nháp vừa tạo**, trong vài giây giữa các lệnh của cùng một cú bấm (mã bài mới, chưa ai biết, trừ người xem danh sách Nháp); nội dung app gửi đã được người dùng xác nhận bằng mã băm (T-102); trình soạn khối (Gutenberg) lưu qua REST nên luôn đổi giờ sửa (khe 3 hẹp nếu website dùng trình soạn khối). Muốn thu hẹp khe 3 (không bắt buộc): lệnh kiểm xin thêm `featured_media` và so với ảnh đại diện app vừa đặt (rẻ, cùng chỗ). Lượt thử thật LC-T094-44 nên xem website dùng trình soạn nào.

### 5. Gộp thử

- `origin/main` `7485b94` (sau `935d381` chỉ thêm tài liệu): `git merge-tree --write-tree` **không xung đột** (cây `d262410`); với `935d381` cũng sạch (cây `48951fd`). Cây gộp `d262410` **không khác code nhánh** (`git diff a7572f7 d262410` trên `seo_app/`, `app/`, `tests/`, `config/`, `scripts/`, `pyproject.toml`, `uv.lock`: trống) vì nhánh đã gộp `main` `935d381` ở `c984878`. Nên kết quả test trên nhánh dùng được cho cây gộp: Thợ Máy lượt 2, 81 file chọn lọc (mọi file dùng client WordPress, T-099, T-102, T-110, T-115): **11.176 passed, 0 failed**; Soi Lỗi chạy cả bộ trên nhánh lượt 1 (0 failed); script của tôi trên nhánh: 46 ca, 0 hỏng. (Lô 60 file tôi chạy trên cây này bị ngắt khi phiên dừng, không chạy lại vì cây không khác code.)
- `team/T-112` `245e199` (Họa Sĩ sẽ gộp T-115 vào): **không xung đột chữ** (cây `d26fb14`); 4 file chung (`README.md`, `app/views/write.py`, `tests/test_la_chan_t102.py`, `tests/test_soi_loi_t102.py`) tự gộp (cả hai nhánh cùng gỡ dấu `xfail` LC-T102-1). Chạy trên cây gộp 9 file (2 file test mới của T-112, `test_t102_publish.py`, file Soi Lỗi/Lá Chắn T-102, T-115, `test_wordpress_release.py`, `test_content_edge_cases.py`): **478 passed, 1 failed** (10 phút).
- **Xung đột ý nghĩa với T-112:** ca `tests/test_t112_release_rules.py::test_schedule_goes_on_but_warns_what_is_missing` («Hẹn giờ mà ảnh đại diện hỏng: vẫn hẹn giờ… cảnh báo») cho lệnh đặt ảnh đại diện trả 500 rồi chờ lệnh hẹn giờ đi; trên cây gộp lệnh hẹn giờ **không** đi (`[] == [{'status': 'future', …}]`) vì T-115 coi lệnh ghi lỗi là «không biết giờ sửa» rồi chặn. **Luật của T-115 là đúng:** mã WordPress 6.9.4 của chính website (bản sao trong `D:\Suachuacuasat`, chỉ đọc) cho thấy `WP_REST_Posts_Controller::update_item` gọi `wp_update_post` (luôn đặt lại `post_modified`, `wp-includes/post.php:4698-4699`) **trước** `handle_featured_media`, meta, chuyên mục; nên lệnh trả lỗi (4xx sau bước đó, 5xx, hết giờ) vẫn có thể đã sửa bài, và client không phân biệt được với một lần sửa ngoài app cùng lúc. Đọc lại giờ sửa sau lệnh lỗi để «làm mốc mới» thì mở thêm một khe «rửa» dài bằng cả lệnh lỗi (tới hết thời gian chờ). Đề nghị: **giữ luật T-115**; Họa Sĩ khi gộp đổi ca này theo R5 (Chỉ Huy duyệt): ảnh đại diện hỏng thì Hẹn giờ **không** đi, bài vẫn là nháp, trang hiện câu `_RELEASE_CHANGED` cùng câu báo ảnh đại diện; luật «Hẹn giờ cảnh báo phần thiếu» của T-112 vẫn đúng cho phần thiếu không do lệnh ghi lỗi (ví dụ SEO chưa bật ghi lên website). Câu nhắc tôi ghi ở biên bản T-102 («Hẹn giờ: Cảnh báo») áp cho trường hợp đó, không cho lệnh ghi lỗi.

## Đối chiếu yêu cầu bảo mật

| Mục | Kết quả | Ghi chú |
|---|---|---|
| LC-T094-23 | **Đóng** | Câu 1 |
| W1 | Đạt | Thêm một điều kiện chặn trước lệnh chuyển; không đường mới tới `future`/`publish` |
| W2 | Đạt | Không thêm lệnh ghi nào; chỉ xin thêm trường `modified_gmt` ở lệnh đã có; không sửa bài nào ngoài nháp client vừa tạo |
| W3 | Đạt, không đổi | Không đụng nội dung bài |
| S2 / LC-T094-2 | Đạt | `_RELEASE_CHANGED` câu cố định; không chép giờ, lời máy chủ |
| `_fields` (LC-T060-2) | Đạt | `modified_gmt` không phải trường dựng bằng `the_content` |
| R5 | Đúng phạm vi duyệt | Soi Lỗi soát 11 chỗ `_fields` + `SAFE_FIELDS`, câu trả lời giả, gỡ `xfail`; tôi soát 2 file của mình: `test_la_chan_t099.py` chỉ thêm `modified_gmt` vào câu trả lời giả; `test_la_chan_t102.py` gỡ dấu `xfail` LC-T102-1 (và `import pytest` thừa), site giả trả thêm `modified_gmt` |

## Kết quả công cụ quét

| Công cụ | Kết quả |
|---|---|
| ruff | `ruff check .` trên nhánh: sạch |
| bandit (`PYTHONUTF8=1`) | `client.py`: 0 |
| detect-secrets (`PYTHONUTF8=1`, mồi tiếng Việt cùng lần quét: bắt được) | 5 file của phiếu: 1 mục «Basic Auth Credentials», chú thích ví dụ có từ trước trong `client.py` (LC-T042-4); không phải bí mật |
| Script dò | `probe_t115.py` 46 ca, 0 hỏng; ba giới hạn tái hiện được |

## Ghi nhận (không xếp lỗi)

1. G4 Soi Lỗi (chuỗi `_fields` cũ ở `test_soi_loi_t042.py:429`, ca không gửi lệnh): vô hại, để nguyên.
2. `_RELEASE_CHANGED` không trả mã bài: người dùng xem lại bài trong trang quản trị rồi hẹn giờ/đăng ở đó (câu báo nói rõ); app không cho thử lại trên bài đó (đúng hướng an toàn).

## Điều kiện

1. **Gộp `main`:** được ngay. Chỉ Huy chạy toàn bộ test khi gộp.
2. **Khi Họa Sĩ gộp T-115 vào T-112:** đổi ca `test_schedule_goes_on_but_warns_what_is_missing` theo R5 (Chỉ Huy duyệt) như mục 5: lệnh ảnh đại diện lỗi thì Hẹn giờ không đi, bài vẫn nháp, câu báo đúng; không nới luật của client.
3. **Sổ rủi ro** (chủ dự án quyết): một dòng «So `modified_gmt` trước lệnh hẹn giờ/đăng (T-115) không bắt được: sửa trong cùng giây với lệnh ghi cuối của app; sửa đúng khe giữa lệnh đọc kiểm và lệnh ghi của app; sửa chỉ phần meta không qua lưu bài (ví dụ đổi ảnh đại diện bằng trình soạn cổ điển). Lý do: WordPress không có khóa lạc quan; cần người đang sửa đúng bài nháp vừa tạo trong vài giây của một cú bấm; nội dung đã xác nhận bằng mã băm». Không bắt buộc trước khi bật công tắc.
4. **Lượt thử thật LC-T094-44:** xem ghi SEO qua Abilities có đổi `modified_gmt` không (đổi thì Hẹn giờ/Đăng ngay luôn bị chặn sau khi ghi SEO, cần đọc lại sau lệnh ghi SEO như yêu cầu 4 của phiếu), website dùng trình soạn nào (khe 3).
5. Kiểm lại bằng Claude Fable (T-116).

**Kết luận:** **ĐẠT.** LC-T094-23 đóng đủ; 0 lỗi mới, 0 lỗi còn mở. Gộp `main` được ngay. Ba giới hạn ghi sổ rủi ro. Khi gộp vào T-112: đổi 1 ca của T-112 theo R5 (giữ luật T-115).

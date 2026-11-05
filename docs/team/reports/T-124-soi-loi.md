# Báo cáo T-124 · Lấy số liệu Search Console, lưu thuộc tính (Giai đoạn 6, đợt 2) · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-124](../tickets/T-124-lay-so-lieu-luu-thuoc-tinh.md), nhánh `team/T-124`: mã và test `ac6a53a`, R5 `c8cbb5b`, báo cáo Thợ Máy `03333cc` (gốc `main` `8caab2f`); thiết kế T-120 mục 1.2, 1.3, 2.4–2.6, 3.3 |
| Ngày nộp | 2026-11-05 (13:12 +07:00) |
| **Kết luận** | **ĐẠT**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Cả 4 trọng tâm Chỉ Huy giao đều **đúng**. (1) `refresh.py`: mô phỏng 4.800 lần bấm qua 6 năm (độ trễ chốt số 1–5 ngày, đồng hồ máy lùi, bỏ lâu không mở, lỗi chèn), 0 lần sai. (2) `env_file`: 2 lớp kiểm và cảnh báo biến môi trường đè đúng như phiếu. (3) Hàm chuẩn hóa dùng chung **không nới lọc**: so chéo 15.015 địa chỉ × 41 cách viết `WORDPRESS_URL` giữa cây trước T-124 và cây T-124, 0 địa chỉ ngoài website lọt; chỉ chặt hơn ở đường con có «.» (`/..`, `/b.log`…) và từ cấm, đúng một luật với client WordPress. (4) Ghép thật dataclass T-122 qua `Protocol` T-123 đúng. 7.050 ca test liên quan qua, 0 hỏng; gộp thử `main` `09ac0ab` không xung đột. Thử đột biến: 4/5 đột biến lọt test Thợ Máy, đều bị test Soi Lỗi bắt. 2 ghi nhận nên xem trước buổi thử thật (GN-1, GN-2: thiết kế, không phải lỗi mã). Không chặn Lá Chắn |

## Tóm tắt (cho chủ dự án)

- **Phần lấy số liệu Google làm đúng.** Tôi cho máy giả lập hơn 4.800 lần bấm «Lấy số liệu mới» trong 6 năm, có lúc bấm liên tục, có lúc bỏ cả năm không mở, có lúc đồng hồ máy chạy sai, có lúc Google lỗi giữa chừng. Lần nào cũng đúng: không gửi quá 20 lệnh, không lấy trùng, không nhận nhầm số tạm thành số chốt, lỗi thì giữ phần đã lấy và lần sau lấy tiếp.
- **Địa chỉ website nay chỉ có một luật** ở cả 3 chỗ (lấy số liệu, lưu tạm, tính toán). Tôi so hơn 600.000 cặp địa chỉ giữa luật cũ và luật mới: luật mới không để lọt địa chỉ nào ngoài website (bản staging, `www.`, tên miền na ná, có tên đăng nhập, cổng lạ…).
- **Lưu thuộc tính vào `.env`** chỉ nhận thuộc tính vừa tìm thấy; máy có biến môi trường đè thì báo.
- **Không có lỗi mới.** Có 2 điểm về cách Google trả số liệu nên kiểm trong buổi thử thật với Google (mục 5).
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t124.py` | Mới: **24 ca, cả 24 qua**. Mọi tham số có `ids=` ngắn (tên ca dài nhất dưới 100 ký tự). Không gọi mạng (Google giả, client giả); mọi file trong `tmp_path` |
| `docs/team/reports/T-124-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác. Test dùng lại `Search`, `Factory`, `FakeWordPress`, `run`… của `tests/test_tracking_refresh.py` (không đổi file đó); fixture viết lại trong file (không nhập fixture, khỏi `noqa`).

## 1. Bốn trọng tâm Chỉ Huy giao

### 1.1 `refresh.py` — **đúng**

Đọc toàn bộ module, rồi mô phỏng: client giả cùng giao diện `refresh` dùng (trần 20 lệnh, lỗi 503 chèn theo thứ tự lệnh), Search Console giả **sát thật** (ngày chốt chỉ tiến lên, không bao giờ đổi ngày đã chốt thành tạm; độ trễ thật 1–5 ngày; thiếu hay sai `metadata` ở đoạn mới nhất chỉ khi độ trễ thật ≤ 3 ngày, đúng giả định của thiết kế 2.4), cache SQLite thật. Mỗi bước chọn ngẫu nhiên: bấm lại ngay, vài phút, vài giờ, 1 ngày, 2–40 ngày, 400–600 ngày (quá 16 tháng), đồng hồ máy lùi 1–6 ngày (Google vẫn ở ngày thật).

| Bất biến kiểm sau **mỗi** lần bấm | 60 hạt × 80 bước = 4.800 lần bấm |
|---|---|
| Mọi đoạn ≤ 31 ngày, trong [hôm nay máy − 485, hôm nay máy] | 0 sai |
| ≤ 20 lệnh mỗi lần bấm (đoạn ngày + từ khóa) | 0 sai |
| Không chèn lỗi thì DONE hay RECENT; cache không từ chối đoạn nào (`MSG_BAD_RANGE`, `MSG_BAD_DATA`) | 0 sai |
| RECENT không gửi lệnh nào | 0 sai |
| Ngày «đã chốt» trong cache luôn mang đúng số thật (không chốt nhầm số tạm) | 0 sai |
| DONE thì phần đã lấy tới đúng hôm nay máy | 0 sai |

Thành ca `test_many_months_of_clicks_keep_every_invariant` (3 hạt × 30 bước, ~4 giây mỗi hạt). Lần mô phỏng đầu của tôi báo «vấn đề» vì Search Console giả cho ngày đã chốt quay lại thành tạm, việc Google không làm; sau khi sửa mô hình thì 0.

Từng ý Chỉ Huy hỏi:

| Ý | Kết quả |
|---|---|
| Chia đoạn ≤ 31 ngày | Lần đầu 16 đoạn (15 cũ + 31 ngày cuối), tối thiểu cho 486 ngày; đoạn đầu kéo tới `covered_end` (luật nối liền của cache): khi cache đúng bất biến, `covered_end − ngày tạm đầu ≤ 30` nên luôn kéo được trong 31 ngày (đọc mã `_covered_after` của T-122) |
| Tạm / chốt | Đúng ở mọi ca mô phỏng; `final` của dòng khớp `first_provisional` truyền cho cache ở cả 3 trường hợp (trong đoạn, trước đoạn, sau đoạn) |
| Dừng ở lỗi đầu | Đúng: lỗi chèn ở lệnh thứ n thì phần đã ghi giữ nguyên, lần bấm sau lấy tiếp đúng chỗ (mô phỏng) |
| Chặn bấm lại | Đúng: < 10 phút, cùng ngày PT, đủ từ khóa hai kỳ thì RECENT, 0 lệnh; mốc ở tương lai quá 5 phút coi như cũ (GN-2 của Soi Lỗi T-122 đã làm) |
| Khóa cấp module | `acquire(blocking=False)`, nhả trong `finally`; tab sau nhận BUSY trước khi dựng client (ca hai luồng của Thợ Máy) |
| Một client mỗi lần bấm | Đúng; RECENT cũng dựng client (chỉ đọc file khóa, không lệnh nào) |
| ≤ 20 lệnh | Trần ở client T-121; lần đầu 18 lệnh; 429 làm vượt thì dừng, giữ phần đã ghi |

Ngoài ra: ngày đăng hỏi theo lô **1.000 bài** (giới hạn `post_statuses`), lần bấm sau hỏi nốt (`test_more_than_1000_quiet_posts_are_asked_in_batches`, WordPress giả giữ đúng giới hạn của client thật). Ca này chưa có ở test Thợ Máy (WordPress giả của Thợ Máy không giới hạn): bỏ phép cắt `[:MAX_STATUS_LOOKUP]` thì chỉ ca này bắt được (mục 4).

### 1.2 `env_file` — **đúng**

- `validate_gsc_site_url`: chỉ `sc-domain:[a-z0-9.-]{1,253}` hay `https://[a-z0-9.-]{1,253}/`, toàn chuỗi; không xuống dòng, dấu cách, `=`, `#`, nháy: không chèn được biến khác vào `.env` (59 ca của Thợ Máy).
- Chỉ lưu thuộc tính vừa nhận từ `sites`: `save_property` đòi mục **dùng được** trong `PropertyList`, rồi `parse_property`, rồi `set_gsc_site_url` kiểm chữ và đòi nằm trong danh sách. Tôi thêm ca **mục dựng tay qua được bộ kiểm chữ nhưng sai dạng tên miền** (`https://a..b/`, `sc-domain:-bad-.com`…): `parse_property` chặn, `.env` không đổi. Ca của Thợ Máy chỉ dùng giá trị mà cả hai lớp cùng chặn, nên bỏ lớp `parse_property` thì test Thợ Máy vẫn qua (mục 4).
- Biến môi trường: `gsc_site_url_overridden` dùng `GSC_SITE_URL in env`, đúng điều kiện `load_settings` (`values.update({name: env[name] … if name in env})`): có mặt là đè, kể cả rỗng. Trên Windows `os.environ` không phân biệt hoa thường ở tên biến, cả hai cùng dùng `os.environ` nên vẫn khớp.

### 1.3 Hàm chuẩn hóa dùng chung — **không nới lọc**

So chéo **cây trước T-124** (`8caab2f`: 3 bản riêng `site_prefix` T-121, `site_base` T-122, `site_base` T-123) với **cây T-124** (một `site_base` ở `seo_app/wordpress/client.py`). Hai cây chạy cùng một script, ghi ra JSON rồi so.
- **Địa chỉ trang:** 15.015 địa chỉ, gồm 5 scheme × 11 kiểu `netloc` × 13 tên máy × 21 đường dẫn:
  - `netloc`: cổng 443, 8443, 80, 444, `:` rỗng, `:0443`, `user@`, `user:pw@`, `…@evil.example`, `evil.example@…`;
  - tên máy: staging, `www.`, `evilsuachuacuasat.com`, `….evil.example`, `-evil.com`, `.co`, chữ «а» Kirin, dấu chấm cuối;
  - đường dẫn: `/..`, `/./`, `/b.log`, `%2e%2e`, `wp-json`, `#…`, `?…`, `%C3`, ký tự đảo hướng.
- **`WORDPRESS_URL`:** 41 cách viết, gồm chữ hoa, `:443`, `HTTPS://`, «/» cuối, thư mục con, tên người dùng, cổng khác, `?`, `#`, `/..`, `/blog/..`, `/./`, `/b.log`, `/%2e%2e`, `/wp-json`, `/WP-Admin`, `/prometal-x`, tab, xuống dòng, dấu cách đầu, chữ không ASCII.

| So (cây cũ → cây mới) | Kết quả |
|---|---|
| Cache T-122 nhận (`_page`): **mới nhận, cũ bỏ** | **0** |
| Client T-121 nhận (`SearchConsoleClient._page`): **mới nhận, cũ bỏ** | **0** |
| Lõi T-123 nhận (`page_key`): **mới nhận, cũ bỏ** | **0** |
| Cùng nhận mà khác chuỗi, khác khóa | **0** |
| Cây mới: cache nhận địa chỉ ngoài website (khác tên máy, cổng, có tên người dùng, không bắt đầu bằng tiền tố) | **0** (290 địa chỉ được nhận, cả 290 đúng website) |
| `site_prefix` đổi | 8 cách viết, đều **cũ nhận, mới bỏ**: `/..`, `/blog/..`, `/./`, `/b.log`, `/blog/../x`, `/wp-json`, `/WP-Admin`, `/prometal-x` (luật đường con chung, đúng yêu cầu 5) |
| `site_base` đổi | 2 cách viết, đều chặt hơn: `" https://…"` (dấu cách đầu) và `"https://sua\tchua…"` (tab giữa). Bản cũ để `urlsplit` lặng lẽ bỏ khoảng trắng rồi chuẩn hóa thành website thật; bản mới (`_canonical_origin` đòi chuỗi gốc đúng `scheme://netloc`) giữ nguyên, nên không trang nào khớp. `config` bỏ dấu cách hai đầu; client WordPress và Search Console đều từ chối khoảng trắng: không ảnh hưởng thật |
| Link bài (`build_tracking`, LC-T123-1): **mới nhận, cũ bỏ** | 7.545 link, **cả 7.545 đúng website**: tên máy viết hoa 4.842, cổng 443 viết ra 1.458, scheme viết hoa 1.002, còn lại là kết hợp. `site_link` chỉ chạy sau `is_site_link`, nên link website khác dù viết hoa vẫn bị bỏ. 9 ca mới: `WWW.`, staging, `http://`, cổng khác, tên miền giống, chữ «А» Kirin viết hoa, tên người dùng (phép kiểm này là cần: `site_link` bỏ phần tên người dùng, mục 4 K3) |

**Luật đường con `/..`:** cổng vào client WordPress (`_is_plain_site_url`) và client Search Console (`site_prefix`) nay cùng nhận hay cùng bỏ ở mọi đường con thử (`/..`, `/./`, `/b.log`, `/blog/../x`, `/%2e%2e`, `/wp-json`, `/WP-Admin`, `/prometal-x`, `//x`, `/b%20log`, chữ không ASCII…). Hai cổng chỉ còn khác ở **tên máy** (client WordPress nhận cổng khác 443; Search Console không nhận vì thuộc tính không có cổng), không phải luật đường con.

**Nơi gọi hàm dùng chung:** ba nơi cũ dùng đúng một hàm (`search_cache.site_base`, `match.site_base` là cùng đối tượng nhập từ `wordpress.client`). Ca `test_three_filters_take_the_same_pages_and_only_on_site_pages` khóa điều này: 6 cách viết × 34 địa chỉ, cache và client T-121 nhận đúng cùng chuỗi, lõi T-123 nhận cùng tập, trang ngoài website bị loại ở cả ba.

### 1.4 Thử chung dataclass thật T-122 qua `Protocol` T-123 — **đúng**

Ca của Thợ Máy `test_dataclass_that_cua_cache_qua_protocol_cua_loi_theo_doi` qua. Hai ca ghép của Soi Lỗi T-122, nay đã chạy thật vì `main` có cả T-121, T-123, đều qua (không bỏ qua):
- `test_cache_rows_go_through_t123_without_being_dropped`;
- `test_lan_2_site_rules_match_t121_and_t123`.

Thêm ca ghép **client T-121 thật → cache T-122** (Google giả có một dòng surrogate lẻ mỗi đoạn): client bỏ và đếm (T-121 lượt 2 đã chặn surrogate, đóng GN-3 của Soi Lỗi T-122), lần lấy đầu DONE, 486 ngày, ghi chú «16 dòng số liệu không đúng dạng bị bỏ».

## 2. Test đã chạy (chỉ test liên quan)

| Nhóm | File | Kết quả |
|---|---|---|
| A · T-121, T-122, T-123, T-124 | `test_google_search_console`, `test_soi_loi_t121`, `test_search_cache`, `test_soi_loi_t122`, `test_soi_loi_t123`, 7 file `test_tracking_*` (gồm `refresh`), `test_t124_chuan_hoa_va_cache`, `test_env_file_gsc` | **1.250 qua**, 1 bỏ qua (symlink file, Windows) |
| B · `.env` | `test_env_file`, `test_config`, `test_config_tolerance`, `test_hash_password_script`, Lá Chắn/Soi Lỗi T-090, T-101, T-104, T-105, `test_t090_env_bang_ma`, `test_t101_settings_google`, `test_t104_set_password`, `test_t105_set_password`, `test_settings_keys`, `test_t112_settings_switch`, `test_soi_loi_t016_t020`, `test_soi_loi_t021_t017` | **505 qua**, 10 bỏ qua (có từ trước) |
| C · test quét mã nguồn cả gói | grep `rglob(`, `.glob(`, `ast.parse`, `os.walk` trên `seo_app/`: `test_google_service_account`, `test_images_process`, `test_la_chan_t096`, `test_soi_loi_t034`, `test_t103_plan_prompt`, `test_wordpress_release`, `test_soi_loi_t110`, `test_soi_loi_t115`, `test_t110_gan_anh_vao_bai_nhap` (`test_tracking_model` ở nhóm A) | **1.217 qua**, 3 bỏ qua |
| D · luật `WORDPRESS_URL`, `is_site_link` | grep `_is_plain_site_url`, `_SITE_PATH`, `site_base`, `site_prefix`, `is_site_link`, câu «chỉ được là địa chỉ website»: `test_la_chan_t041`, `test_onpage_links`, `test_plan_sync`, `test_soi_loi_t037`, `t042` (3 file), `t054`, `t060`, `t085`, `t088`, `test_wordpress_published`, `test_wordpress_round2_t042`, `test_wordpress_routes_t042`, `test_wordpress_seo_meta_t042`, `test_wordpress_site_link_t042`, `test_wordpress_t060` | **4.054 qua** |
| Soi Lỗi T-124 | `test_soi_loi_t124` | **24 qua** |

Tổng **7.050 qua, 0 hỏng**. `uv run ruff check .`: sạch.

## 3. R5: hai ca test cũ Thợ Máy đổi

| Ca | Nhận xét |
|---|---|
| `test_google_search_console.py` (T-121): ca nhận `b.log` chuyển sang danh sách từ chối | **Đúng**: phiếu yêu cầu 5 đòi một luật đường con, luật của client WordPress không nhận «.». Ca nhận thay bằng `Blog_2/a-b~c` (đủ ký tự được phép); phép thoát «.» của bộ lọc RE2 vẫn kiểm riêng (`test_bieu_thuc_loc_thoat_dau_cham_trong_tien_to`); thêm 7 địa chỉ bị từ chối. Không ca nào yếu đi |
| `test_tracking_model.py::test_package_is_pure_functions` (T-123) | **Đúng**: `refresh.py` là lớp nối (thiết kế T-120 mục 6), phải nhập client, cache. Lõi 7 file giữ nguyên danh sách cấm, thêm: lõi không được nhập `refresh`, gói không được có file chưa xếp loại. `refresh.py` vẫn bị kiểm `open`, `eval`, `exec`, `compile`, `__import__`. Chặt hơn ở hai điểm, chỉ nới đúng chỗ cần |

`git diff 8caab2f 03333cc -- tests/`: chỉ hai file này đổi ca cũ; còn lại là file mới.

## 4. Thử đột biến

Mỗi đột biến sửa một chỗ trên worktree tạm (`03333cc`), chạy 3 file test mới của Thợ Máy và file của Soi Lỗi riêng, rồi trả file về nguyên văn (kiểm lại nội dung):

| Đột biến | Test Thợ Máy | Test Soi Lỗi |
|---|---|---|
| K1 · `save_property` bỏ `parse_property` | 231 qua: **không bắt** | **4 hỏng**: ca mục dựng tay qua bộ kiểm chữ, sai dạng tên miền |
| K3 · `build_tracking` bỏ `is_site_link` trước `site_link` | **không bắt** | **2 hỏng**: link có tên người dùng (`https://user@SUACHUACUASAT.COM/a/`). `site_link` bỏ phần tên người dùng, nên thiếu phép kiểm này thì link đó thành bài của website. Lượt đầu (22 ca) cũng sống; đã thêm 2 ca |
| K7 · ngày đăng bỏ cắt `[:MAX_STATUS_LOOKUP]` | **không bắt** (WordPress giả không giới hạn) | **1 hỏng**: website hơn 1.000 bài chưa có lượt hiển thị |
| K13 · `_is_healthy` coi file bị khóa là file hỏng | **không bắt** trên Windows: hệ điều hành chặn xóa file đang mở nên `reset_count` vẫn 0, ca chỉ đòi «một `SearchCacheError`» (câu thật thành «Không đọc, ghi được…» thay vì «đang bận»; trên Mac/Linux file bị xóa thật) | **1 hỏng**: `test_soi_loi_t122.py::test_exclusive_lock_is_busy_not_corrupt` đòi đúng câu «đang bận» |
| K2 · `_canonical_origin` bỏ phép đòi chuỗi gốc đúng `scheme://netloc` | không bắt | không bắt: **sống, chấp nhận được**. Chỉ đổi kết quả với `WORDPRESS_URL` có khoảng trắng; `config` đã bỏ dấu cách hai đầu và hai cổng vào đều từ chối khoảng trắng (mục 1.3) |

Bốn trong năm đột biến lọt test của Thợ Máy và đều bị test Soi Lỗi bắt. Đột biến còn lại tương đương về hành vi. Mọi file đã trả về nguyên văn (script kiểm lại nội dung).

## 5. Ghi nhận (không phải lỗi mã)

- **GN-1 · Thiếu `metadata` mà độ trễ thật > 3 ngày thì số tạm bị chốt nhầm, không bao giờ lấy lại.**
  - Thiết kế 2.4: đoạn mới nhất thiếu hay sai `first_incomplete_date` thì «coi 3 ngày cuối là số tạm (hướng an toàn)». T-124 làm đúng như vậy.
  - Thử: độ trễ thật 5 ngày, Google không trả `metadata`. Ngày thứ 4, thứ 5 tính từ hôm nay được ghi là «đã chốt» với số tạm (0 click). Lần bấm sau chỉ lấy từ ngày tạm trong cache, nên hai ngày đó **giữ số sai mãi** (script ở thư mục nháp, đã chạy: `('2026-10-30', 0, 5)`, `('2026-10-31', 0, 1)`).
  - Google thật thường luôn trả `metadata` khi `dataState = all`, nên rủi ro thấp.
  - Đề nghị: buổi thử thật (Lá Chắn T-121 B.4, T-128) ghi lại câu trả lời của đoạn mới nhất. Nếu có lúc thiếu `metadata` thì nới lên 5–7 ngày, hay mỗi lần bấm lấy lại 7 ngày cuối (vẫn 1 lệnh).
- **GN-2 · Đoạn ngắn và luật «quá 10% dòng lạ thì bỏ cả lần gọi» của client T-121.**
  - Bấm hằng ngày thì đoạn mới nhất chỉ 3–4 ngày, ít dòng. Một dòng lạ trong câu trả lời Google (thử bằng surrogate lẻ) là quá 10%: client bỏ cả lần gọi, `refresh` FAILED. Bấm lại vẫn FAILED vì cùng dòng đó, tới khi khoảng ngày đủ dài để dòng lạ dưới 10%. Đã chạy thử: lần lấy đầu DONE (đoạn 31 ngày), hôm sau FAILED.
  - Đây là luật của thiết kế 2.4 và client T-121, không phải của T-124; dữ liệu đã lưu không hỏng. Google thật hầu như không trả dòng lạ.
  - Nếu muốn mượt hơn: chỉ áp luật 10% khi lần gọi có từ, ví dụ, 20 dòng trở lên. Việc này cho Chỉ Huy, Lá Chắn quyết.
- **GN-3 · «Kiểm tra», «Tìm thuộc tính» không giữ khóa của `refresh`.** Hai nút này chạy được song song với một lần lấy ở tab khác (thêm ≤ 3 lệnh). Khớp chữ của LC-T120-22 («một lần **lấy số liệu**»), ghi để Lá Chắn biết.
- **GN-4 · Lỗi WordPress khi hỏi ngày đăng chỉ ghi chú.** Lần bấm lại trong 10 phút là RECENT (từ khóa đã đủ), nên ngày đăng phải chờ hết 10 phút mới hỏi lại. Chấp nhận được.
- **GN-5 · LC-T120-12 dựa vào T-125 truyền đúng kết quả «Tìm thuộc tính».**
  - `PropertyList`, `SiteEntry` dựng tay được. Hai lớp kiểm (`parse_property` và bộ kiểm chữ của `.env`) vẫn chỉ cho lưu chuỗi đúng dạng thuộc tính.
  - T-125 phải giữ `find_properties(...)` trong `session_state` và không dựng `PropertyList` từ chữ người dùng gõ (Thợ Máy đã dặn ở Đề xuất).
- **GN-6 · Bài mà WordPress không trả ngày đăng** (bài vừa gỡ giữa hai lần tải danh sách) được hỏi lại ở mọi lần bấm, trong lô 1.000. Nếu có hơn 1.000 bài như vậy thì bài sau không bao giờ tới lượt. Gần như không xảy ra.

## 6. Bằng chứng

```
# Nhánh team/T-124 tại 03333cc + file test mới, Windows 11, Python 3.12.15
$ uv run pytest tests/test_soi_loi_t124.py -q
24 passed in 16.89s
$ uv run pytest <nhóm A> -q                 # 14 file
1250 passed, 1 skipped in 176.58s
$ uv run pytest <nhóm B> -q                 # 18 file .env
505 passed, 10 skipped in 203.50s
$ uv run pytest <nhóm C> -q                 # 9 file quét mã nguồn
1217 passed, 3 skipped in 155.62s
$ uv run pytest <nhóm D> -q                 # 17 file luật WORDPRESS_URL
4054 passed in 324.55s
$ uv run ruff check .                       # All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t124.py    # 1 file already formatted

# So chéo chuẩn hóa: cùng script chạy trên cây 8caab2f và cây 03333cc (seo_app nạp từ chính cây đó)
15.015 địa chỉ × 41 WORDPRESS_URL: mới nhận cũ bỏ 0 (cache, client, lõi); ngoài website 0;
site_prefix chặt hơn 8; site_base chặt hơn 2; link bài mới nhận 7.545, ngoài website 0

# Mô phỏng refresh: 60 hạt × 80 bước = 4.800 lần bấm: 0 vấn đề

# Gộp thử: 03333cc + main cục bộ 09ac0ab (main đổi app/views/write.py, storage/drafts.py, README,
# .env.example; không đụng file nào của T-124): không xung đột. 18 file (nhóm A, file Soi Lỗi,
# test_env_file, test_config, test_t101_settings_google), seo_app nạp từ bản gộp:
1390 passed, 5 skipped in 235.31s
$ ruff check .                              # trên bản gộp: All checks passed!

# Quét ký tự ẩn file test: sạch. Quét bí mật, PYTHONUTF8=1: results {}; đối chứng (bản sao thêm
# khóa giả, đặt trong thư mục đang quét): bắt được (Secret Keyword).
```

Các worktree tạm (`old`, `mut`, `gop`) đã gỡ; commit gộp tạm không đẩy.

## 7. Đề xuất

- **Lá Chắn T-124:** xem GN-1, GN-2 (thiết kế), GN-3 (phạm vi khóa).
- **Buổi thử thật (T-128):** ghi câu trả lời `metadata` của đoạn mới nhất và một đoạn cũ (GN-1, như Thợ Máy đã đề nghị).
- **T-125:** như Đề xuất của Thợ Máy; thêm GN-5.

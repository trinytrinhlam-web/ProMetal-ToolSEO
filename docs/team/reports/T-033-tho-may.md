# Báo cáo T-033 · Thiết kế Giai đoạn 4 (tối ưu on-page): tìm hiểu SiteSEO, chia phiếu

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Opus 5.5 |
| Phiếu | [T-033](../tickets/T-033-thiet-ke-giai-doan-4.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- **Ghi meta SiteSEO qua REST được, không cần plugin mới.** Website của anh **đã mở sẵn** 4 trường SiteSEO trong REST (meta title, meta description, tiêu đề và mô tả Facebook): đọc công khai thấy ngay. Chưa biết tài khoản Biên tập viên có **ghi** được không (phải thử khi có tài khoản).
- Còn một đường chính hãng: SiteSEO 1.4.2 có tính năng **"Abilities"** (WordPress 6.9+, site đã có), ghi được title, description, canonical, robots, từ khóa chính. Cần anh **bật một công tắc** trong SiteSEO.
- **Schema:** website đã tự xuất Article (tác giả là tổ chức "Cơ khí Pro-Metal", không tên người) và BreadcrumbList cho mọi bài, cộng một khối doanh nghiệp đủ chi nhánh trên mọi trang. SiteSEO thì xuất thêm một khối "Organization" **rỗng tên** → nên tắt hoặc điền. Phần mềm **không cần tự xuất** Article/Breadcrumb; chỉ bổ sung FAQPage (tùy chọn) và Service sau này.
- Đề xuất **8 phiếu** (T-034 → T-041): 5 phiếu logic thuần chạy ngay bằng test giả, 3 phiếu cần site.
- **4 câu hỏi** cho anh ở cuối báo cáo.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-033-tho-may.md` | Báo cáo này (file duy nhất). Không sửa code, cấu hình, test |

## Nguồn đã dùng

**Mã nguồn SiteSEO** bản **1.4.2** (bản mới nhất, cập nhật 2026-09-24, "Tested up to: 7.1"), tải từ `https://downloads.wordpress.org/plugin/siteseo.1.4.2.zip` (link lấy từ API chính thức `api.wordpress.org/plugins/info/1.2/?action=plugin_information&request[slug]=siteseo`). Dẫn nguồn dạng `file:dòng` trong gói đó.

**Mã lõi WordPress 6.9** (để xác minh đường REST của Abilities): `github.com/WordPress/wordpress-develop`, nhánh `6.9`, `src/wp-includes/rest-api/endpoints/class-wp-rest-abilities-v1-run-controller.php` và `…-list-controller.php`.

**Website** suachuacuasat.com: 8 lần GET, không đăng nhập, không gửi header xác thực:

| # | URL | Kết quả |
|---|---|---|
| 1 | `https://suachuacuasat.com/` | 200, HTML trang chủ |
| 2 | `https://suachuacuasat.com/wp-json/` | 200, danh sách namespace |
| 3 | `https://suachuacuasat.com/wp-json/wp/v2/posts?per_page=5&_fields=id,link,slug,status,type,meta` | 200, 4 bài |
| 4 | `https://suachuacuasat.com/wp-json/wp/v2/pages?per_page=100&_fields=id,link,slug,parent,meta` | 200, 25 trang |
| 5 | `https://suachuacuasat.com/dau-hieu-can-thay-banh-xe-cua-keo/` | 200, HTML một bài |
| 6 | `https://suachuacuasat.com/sua-cua-keo-tphcm/` | 200, HTML trang dịch vụ |
| 7 | `https://suachuacuasat.com/lien-he/` | 200, HTML trang Liên hệ |
| 8 | `https://suachuacuasat.com/robots.txt` | 200 |

4 bài + 25 trang = **29 URL**, khớp con số "29 URL đang có" trong yêu cầu YC-501.

---

## 1. SiteSEO lưu dữ liệu ở đâu

### 1.1 Khóa post meta (SiteSEO 1.4.2)

| Dữ liệu | Khóa post meta | Giá trị | Nguồn |
|---|---|---|---|
| Meta title | `_siteseo_titles_title` | chữ; rỗng = dùng mẫu chung của SiteSEO | `main/abilitiesregister.php:637-642`, `main/titlesmetas.php:626` |
| Meta description | `_siteseo_titles_desc` | chữ | `abilitiesregister.php:637-642`, `titlesmetas.php:912` |
| Canonical | `_siteseo_robots_canonical` | URL; rỗng = canonical tự động | `abilitiesregister.php:637-642`, `titlesmetas.php:346` |
| Từ khóa chính | `_siteseo_analysis_target_kw` | chữ (nhiều từ khóa cách nhau dấu phẩy) | `abilitiesregister.php:637-642` |
| noindex | `_siteseo_robots_index` | `"yes"` = noindex; **không có khóa** = index | `abilitiesregister.php:655-672`, `titlesmetas.php:109` |
| nofollow | `_siteseo_robots_follow` | `"yes"` = nofollow | như trên |
| noimageindex / noarchive / nosnippet | `_siteseo_robots_imageindex` / `_archive` / `_snippet` | `"yes"` | như trên |
| Tiêu đề / mô tả / ảnh Facebook | `_siteseo_social_fb_title`, `_siteseo_social_fb_desc`, `_siteseo_social_fb_img` | chữ / URL | `abilitiesregister.php:675-682` |
| Tiêu đề / mô tả / ảnh X (Twitter) | `_siteseo_social_twitter_title`, `_desc`, `_img` | chữ / URL | như trên |
| Chuyên mục chính | `_siteseo_robots_primary_cat` | ID chuyên mục | `main/metaboxes/settings.php:1173` |
| Loại schema / schema tùy chỉnh | `_siteseo_structured_data_type`, `_siteseo_structured_data_custom` | chỉ **SiteSEO Pro** dùng; bản miễn phí chỉ đọc để chấm điểm | `main/metaboxes/analysis.php:1200-1202`; giao diện chỉ hiện khi có Pro (`metaboxes/settings.php:341, 699-703`) |

Ghi chú:
- Tất cả khóa bắt đầu bằng `_` → WordPress coi là **meta được bảo vệ**: dù có đăng ký `show_in_rest`, nếu không khai `auth_callback` thì REST **không cho ghi** (lõi WordPress gán `__return_false` cho meta được bảo vệ, `wp-includes/meta.php` hàm `register_meta`; *chưa đối chiếu dòng cụ thể trong bản 6.9*).
- SiteSEO bản miễn phí **không có** schema theo từng bài (Article, FAQ…). Đó là tính năng Pro. Site có cài Pro không: **chưa xác minh** (trang công khai không thấy dấu hiệu Pro).

### 1.2 SiteSEO có đăng ký meta với `show_in_rest` không

**Không.** Trong toàn bộ 32 file PHP của SiteSEO 1.4.2 không có `register_meta`, `register_post_meta`, `register_rest_field` hay `register_rest_route`. Hai chỗ `show_in_rest` duy nhất (`abilitiesregister.php:68, 313`) là thuộc tính của Ability, không phải của meta.

Hộp SiteSEO trong trang soạn bài lưu meta bằng form của trình soạn (`metaboxes/settings.php:1095-1169`, kiểm `nonce` và quyền `edit_post`), không qua REST.

### 1.3 Nhưng website của anh **đã mở sẵn** 4 khóa trong REST

GET #3 và #4 (không đăng nhập) trả về trường `meta` có đúng 4 khóa SiteSEO cho mọi bài và trang:

```
_siteseo_titles_title, _siteseo_titles_desc, _siteseo_social_fb_title, _siteseo_social_fb_desc
```

Ví dụ bài 810: `_siteseo_titles_title = "6 Dấu Hiệu Cần Thay Bánh Xe Cửa Kéo | Pro Metal"`.

SiteSEO không làm việc này (mục 1.2), nên có một đoạn code riêng của site đăng ký chúng. Nhiều khả năng ở theme riêng `prometal-0` hoặc plugin Code Snippets (cả hai có mặt trên site): **chưa xác minh**.

| Câu hỏi | Trả lời |
|---|---|
| Đọc được qua REST? | **Có**, đã thấy (kể cả không đăng nhập) |
| Ghi được qua `POST /wp/v2/posts` với `"meta": {…}`? | **Chưa xác minh.** Phụ thuộc `auth_callback` của đoạn code kia. Thử bằng một bài **nháp** khi có tài khoản Biên tập viên (phiếu T-039) |
| Có canonical, robots, từ khóa chính? | **Không** có trong REST |

### 1.4 SiteSEO có đường REST riêng: "Abilities" (WordPress 6.9+)

SiteSEO 1.4.2 đăng ký các **Ability** với Abilities API của WordPress 6.9 (`abilitiesregister.php:16-24`). WordPress tự mở chúng ra REST tại namespace `wp-abilities/v1`.

| Mục | Chi tiết | Nguồn |
|---|---|---|
| Điều kiện | Công tắc **Abilities** trong SiteSEO phải **bật** (`siteseo_toggle['toggle-abilities']`) và WordPress ≥ 6.9 | `siteseo.php:77-80` |
| Site đã đủ WordPress 6.9? | **Có**: `/wp-json/` liệt kê namespace `wp-abilities/v1` (GET #2) | |
| Công tắc đã bật? | **Chưa xác minh** (danh sách ability cần đăng nhập, quyền `read`: `list-controller.php:181-183`) | |
| Ghi | `POST /wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update/run`, thân JSON `{"input": {"postId": 123, "title": "…", "description": "…", "canonical_url": "…", "focus_keyphrase": "…", "robots": {"noindex": false, "nofollow": false}}}` | `abilitiesregister.php:261-316`; `run-controller.php:45-66, 195-202` |
| Đọc | `GET …/siteseo-posts/seo-data-get/run?input[postId]=123` (ability chỉ đọc bắt buộc GET) | `abilitiesregister.php:239-258`; `run-controller.php:110-130` |
| Quyền | `edit_posts` để gọi; trong hàm kiểm thêm `current_user_can('edit_post', $post_id)` → **Biên tập viên đủ quyền**, không cần Quản trị viên | `abilitiesregister.php:190-192, 633` |
| Chỉ ghi trường được gửi | Có: "Only the fields provided in input are changed". Gửi `null` thì **xóa** meta đó | `abilitiesregister.php:262-264, 644-652` |
| Lọc dữ liệu | `sanitize_text_field` cho mọi chữ (bỏ thẻ, xuống dòng) | `abilitiesregister.php:650` |

**Rủi ro của đường Abilities** (phải chặn trong code của phần mềm):
- Ability ghi được **mọi bài** Biên tập viên sửa được, kể cả bài đã đăng. Phần mềm phải tự giới hạn: chỉ gọi cho bài nháp **do chính app tạo** (giống `set_featured_image` hiện có, `seo_app/wordpress/client.py`, `_created_post_ids`), giữ W2.
- Gửi `null` là xóa: client không bao giờ gửi `null`, bỏ hẳn trường không đổi.
- Khi bật Abilities, SiteSEO còn mở ability đọc cài đặt và kiểm toàn site; phần mềm chỉ gọi đúng 2 ability `seo-data-get` / `seo-data-update` (danh sách cố định trong code).

### 1.5 Kết luận mục 1

| Cách | Ghi được | Việc phía site | Đánh giá |
|---|---|---|---|
| **A. Meta qua `wp/v2/posts`** (đã mở sẵn) | title, description (+ Facebook) | Không, nếu Biên tập viên ghi được; nếu không thì sửa `auth_callback` (mục 2) | Đơn giản nhất, gửi cùng lúc tạo nháp |
| **B. Abilities của SiteSEO** | title, description, canonical, robots, từ khóa chính, mạng xã hội | Bật 1 công tắc trong SiteSEO | Chính hãng, đủ trường; thêm 1 lệnh gọi sau khi tạo nháp |
| C. mu-plugin mới | tùy | Anh tự cài file lên hosting | Chỉ khi A và B đều không dùng được |

**Đề xuất:** dùng **B** làm đường chính (đủ trường, do SiteSEO tự lưu đúng quy ước), **A** làm đường dự phòng cho title/description. Phần mềm tự dò: khi kiểm tra kết nối, gọi `GET /wp-abilities/v1/abilities/siteseo-posts/seo-data-update` (có xác thực); có thì dùng B, không thì A.

Với bài mới, **canonical và robots để trống** (SiteSEO tự đặt canonical = chính URL bài và `index, follow`, như đã thấy ở GET #5). Chỉ ghi khi người dùng tự đổi. Đây là cách an toàn nhất cho YC-405.

---

## 2. Nếu không ghi được qua REST: các phương án

Chỉ cần khi cả A và B không dùng được (ví dụ anh không muốn bật Abilities **và** đoạn code đang mở 4 khóa không cho ghi).

| Phương án | Ai làm | Rủi ro | Đánh giá |
|---|---|---|---|
| C1. Sửa đoạn code đang mở 4 khóa: thêm `auth_callback` kiểm `edit_post` | Anh (hoặc người làm web), sửa trong theme/Code Snippets | Thấp; sửa code đang có, nhớ sao lưu | Nên dùng nếu tìm được đoạn code |
| C2. mu-plugin mới (mã bên dưới) | Anh tải file lên `wp-content/mu-plugins/` qua trình quản lý file của hosting | Thấp; mu-plugin luôn chạy, không tắt được trong trang quản trị (muốn gỡ thì xóa file). Nếu đăng ký trùng khóa với đoạn code đang có, bản đăng ký sau thắng | Dự phòng |
| C3. Plugin Code Snippets (site đã có) chạy cùng đoạn mã | Anh dán mã vào Snippets | Như C2; nhưng Code Snippets có REST riêng (`/code-snippets/v1/…`) — app **tuyệt đối không gọi** | Được, nếu anh quen Snippets |
| C4. Phần mềm sửa trực tiếp trong trang quản trị (mô phỏng form) | — | Cao: cần đăng nhập bằng mật khẩu thật, cookie, nonce | **Không làm** |

### Mã mu-plugin soạn sẵn (C2/C3)

> **Chưa qua Lá Chắn.** Theo phiếu, phải được Lá Chắn duyệt trước khi đưa anh cài. Chưa chạy thử trên WordPress thật.

```php
<?php
/**
 * Plugin Name: ProMetal – mở trường SiteSEO cho REST API
 * Description: Cho phép tài khoản có quyền sửa bài ghi meta title, meta description,
 *              từ khóa chính của SiteSEO qua REST API. Không thêm quyền mới cho ai.
 * Version:     1.0.0
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('init', function () {
    $keys = [
        '_siteseo_titles_title',
        '_siteseo_titles_desc',
        '_siteseo_analysis_target_kw',
    ];
    foreach (['post', 'page'] as $post_type) {
        foreach ($keys as $key) {
            register_post_meta($post_type, $key, [
                'type'              => 'string',
                'single'            => true,
                'show_in_rest'      => true,
                'sanitize_callback' => 'sanitize_text_field',
                // Chỉ người được sửa đúng bài này mới ghi được (Biên tập viên, tác giả của bài).
                'auth_callback'     => function ($allowed, $meta_key, $post_id) {
                    return current_user_can('edit_post', $post_id);
                },
            ]);
        }
    }
}, 20);
```

Lý do thiết kế:
- Không mở canonical, robots: bài mới không cần (mục 1.5); mở thêm là thêm chỗ có thể làm hỏng chỉ mục.
- `show_in_rest => true` làm 3 khóa hiện trong REST **công khai** (như 4 khóa hiện nay). Title, description vốn đã hiện trong HTML trang nên không lộ gì mới; riêng **từ khóa chính** sẽ lộ ra công khai. Nếu anh không muốn lộ từ khóa, bỏ dòng `_siteseo_analysis_target_kw`. (Hạn chế này không có ở đường Abilities, vốn cần đăng nhập.)

---

## 3. Schema (YC-403, YC-404)

### 3.1 Site đang xuất schema gì (đọc từ GET #1, #5, #6, #7)

| Khối JSON-LD | Nguồn | Có ở | Nhận xét |
|---|---|---|---|
| `Organization` với `name: ""`, `logo: ""` (thẻ có `class="siteseo-schema"`) | **SiteSEO** (Knowledge Graph, `main/socialmetas.php:16-118`) | Mọi trang | **Lỗi:** tên và logo rỗng, `@type` là Organization chung chung; trùng ý với khối dưới |
| `HomeAndConstructionBusiness` `@id …/#business`: tên, hotline, trụ sở, giờ mở cửa, `areaServed`, `department` = 8 chi nhánh | Code riêng của site (theme `prometal-0` hoặc Code Snippets, **chưa xác minh**) | Mọi trang | Tốt; đây là LocalBusiness của YC-403. Có ghi `priceRange: "$$"` (xem câu hỏi 4) |
| `BreadcrumbList` | Code riêng của site | Bài, trang dịch vụ, Liên hệ | Tốt |
| `Article`: `headline`, `image`, `datePublished`, `dateModified`, `author` = **Organization "Cơ khí Pro-Metal"**, `publisher` có logo, `mainEntityOfPage` | Code riêng của site | Bài viết | Tốt; **đã giải quyết lệch "Article (có tác giả)"** đúng như chủ dự án chốt: tác giả là tổ chức, không tên người |
| `Service` | — | **Không có** ở trang dịch vụ | Thiếu so với YC-403 |
| `FAQPage` | — | Không có | Tùy chọn |

Thêm một lỗi ngoài phạm vi phiếu nhưng cùng loại "hai nguồn chồng nhau": trang chủ có **2 thẻ `meta name="description"`** khác nhau (một do SiteSEO, một do code riêng; câu thứ hai ghi "3 chi nhánh Gò Vấp, Hóc Môn, Thủ Đức", không khớp hồ sơ doanh nghiệp). Bài và trang con chỉ có 1 thẻ. Đề xuất Chỉ Huy báo anh (không thuộc phần mềm).

### 3.2 Nguồn schema đề xuất cho từng loại trang

Nguyên tắc YC-404: mỗi loại schema chỉ một nguồn. Code của site đã làm tốt phần chung, nên **phần mềm chỉ thêm cái site chưa có, và chỉ trong bài do app tạo**.

| Loại trang | Schema (YC-403) | Nguồn đề xuất | Phần mềm làm gì |
|---|---|---|---|
| Trang chủ | Organization + LocalBusiness | **Code site** (`#business`). Tắt khối Organization rỗng của SiteSEO | Không làm gì |
| Liên hệ | LocalBusiness từng địa chỉ | **Code site** (`department` đã có 8 chi nhánh) | Không. Đối chiếu 9 địa chỉ trang Liên hệ ↔ 8 `department`: việc của anh |
| Khu vực | LocalBusiness chi nhánh khu vực + Service `areaServed` + BreadcrumbList | Breadcrumb: code site. LocalBusiness + Service: **phần mềm** (chưa có nguồn nào) | Giai đoạn sau (cần dữ liệu chi nhánh theo khu vực; quy định chỉ dùng 9 địa chỉ). Không thuộc 8 phiếu dưới |
| Dịch vụ | Service + BreadcrumbList | Breadcrumb: code site. Service: **phần mềm** khi app tạo/cập nhật trang dịch vụ | Để sau: app hiện chỉ tạo **bài** (post), 25 trang dịch vụ có sẵn không được sửa (W2) |
| Hướng dẫn, công trình | Article + BreadcrumbList; FAQPage tùy chọn | Article, Breadcrumb: **code site** (đã chạy với mọi bài). FAQPage: **phần mềm** | Chỉ tạo **FAQPage** khi bài có mục Hỏi đáp và người dùng bật |
| Không dùng | HowTo | — | Bộ kiểm chặn `HowTo` |

Như vậy Giai đoạn 4 **không cần** phần mềm xuất Article: tránh được hẳn nguy cơ hai Article trên một bài.

### 3.3 Đưa JSON-LD (FAQPage) của phần mềm lên trang

| Cách | Ưu | Nhược |
|---|---|---|
| a. Trường schema của SiteSEO (`_siteseo_structured_data_custom`) | Đúng "theo SiteSEO" | Chỉ **SiteSEO Pro**; không có trong REST, không có trong Abilities. **Không dùng được** với bản miễn phí |
| b. Chèn `<script type="application/ld+json">` vào nội dung bài | Không cần gì phía site | `sanitize_html` **bỏ mọi `<script>`** (đúng chính sách 2.3); nới lọc cho script là mở cửa cho mã độc. WordPress cũng lọc `<script>` với tài khoản không có quyền `unfiltered_html` (Biên tập viên trên site đa trang, hoặc khi site tắt quyền này) |
| c. Một trường meta riêng (ví dụ `_prometal_faq_jsonld`) + code site in ra `<head>` | Tách hẳn khỏi nội dung bài; code site in ra bằng `wp_json_encode` (an toàn) | Cần thêm code phía site (mở rộng mu-plugin mục 2) |
| d. **Không gửi JSON-LD**: gửi **dữ liệu** hỏi-đáp (câu hỏi, trả lời dạng chữ) vào trường meta, code site tự dựng FAQPage | An toàn nhất: phần mềm không bao giờ gửi mã; site dựng JSON đúng một cách | Như c |

**Đề xuất:** Giai đoạn 4 **chưa đưa** FAQPage lên site (Google không còn hiện FAQ nổi bật từ 07/5/2026, yêu cầu ghi "chỉ giữ nếu có ích"). Phần mềm vẫn **dựng và kiểm** schema trong code (để xem trước ở bước SEO, phục vụ M7 #10). Khi anh muốn đưa lên, làm theo **d** trong một phiếu riêng kèm mã site (qua Lá Chắn). Không bao giờ nới `sanitize_html` cho `<script>`.

### 3.4 Kiểm schema hợp lệ không cần mạng

Kiểm bằng code thường, chỉ thư viện chuẩn + `pydantic` (đã có):

1. Phần mềm **tự dựng** JSON-LD từ dữ liệu đã kiểm (không để AI viết JSON): mỗi loại một khuôn pydantic (`FAQPage`, `Question`, `Answer`; sau này `Service`) với `extra="forbid"`.
2. Kiểm: `@context` đúng `https://schema.org`; `@type` trong danh sách cho phép (chặn `HowTo`); trường bắt buộc có và không rỗng (FAQ: `mainEntity` ≥ 1, mỗi câu có `name` và `acceptedAnswer.text`); URL là `https://` và **cùng tên miền** với `WORDPRESS_URL`; chữ không chứa thẻ HTML (`strip_tags`), độ dài có giới hạn.
3. Xuất bằng `json.dumps(..., ensure_ascii=False)` rồi **đổi `<`, `>`, `&`** thành `<`, `>`, `&` để chuỗi không thể đóng thẻ `</script>`.
4. Khớp nội dung: câu hỏi/trả lời trong FAQPage phải **có mặt nguyên văn** trong bài (Google yêu cầu nội dung schema hiện trên trang).
5. Kiểm trùng nguồn: nếu loại schema đã có ở code site (Article, BreadcrumbList, LocalBusiness) thì phần mềm từ chối dựng loại đó (danh sách cấu hình).

Test: chỉ dữ liệu giả, không gọi Google Rich Results Test.

---

## 4. Liên kết nội bộ (YC-601 → YC-604)

### 4.1 Danh sách bài/trang đã đăng

| Việc | Thiết kế |
|---|---|
| Lấy danh sách | Hàm mới `WordPressClient.list_published()`: `GET /wp/v2/posts` và `GET /wp/v2/pages` với `status=publish`, `_fields=id,type,slug,link,title,modified_gmt,meta`, `per_page=100`, dùng lại `_get_all_pages` (đã có giới hạn `MAX_PAGES`). Hiện site có 4 bài + 25 trang = 1 lần gọi mỗi loại |
| Chỉ bài đã đăng | Gửi `status=publish` **và** lọc lại phía app: bỏ mọi mục có `status != "publish"` (phòng plugin trả lẫn nháp/hẹn giờ cho tài khoản đã đăng nhập). Bài `future` (đã hẹn giờ, chưa lên) **không** được link (YC-603) |
| Dữ liệu ngoài là chưa tin cậy | Tiêu đề qua `_plain` (đã có); `link` phải là `https://` và **đúng tên máy** của `WORDPRESS_URL`, sai thì bỏ mục đó; độ dài có giới hạn |
| Cache SQLite | **Có**. Module mới `seo_app/storage/site_index.py`, file riêng `data/site_index.sqlite` (cùng thư mục với `drafts.sqlite`, đã nằm trong `.gitignore` theo D2: *Lá Chắn kiểm lại*). Bảng `pages(id, type, slug, link, title, meta_title, meta_desc, modified_gmt)` + thời điểm tải có múi giờ. Xóa file vẫn tải lại được (đúng `CLAUDE.md`). Không lưu gì bí mật |
| Làm mới | Tự tải lại nếu cache cũ hơn 6 giờ; nút "Tải lại danh sách bài" ở bước SEO; **bắt buộc tải lại ngay trước khi gửi nháp** (để kiểm link hỏng trên dữ liệu mới nhất) |

Cùng danh sách này phục vụ luôn YC-402 (kiểm trùng title/meta, mục 5.4) vì REST đã trả `_siteseo_titles_title`, `_siteseo_titles_desc` (mục 1.3).

### 4.2 AI gợi ý chỗ chèn và anchor

1. **Code chọn ứng viên trước**, AI chỉ chọn trong đó (YC-602):
   - link bắt buộc theo phiếu giao bài (trang dịch vụ đích + link khác; YC-601) luôn có mặt, không để AI bỏ;
   - quy tắc theo loại trang: hướng dẫn → trang dịch vụ đích + 2–3 bài cùng nhóm; dịch vụ → 2–3 bài hướng dẫn liên quan;
   - "cùng nhóm" lúc đầu = cùng chuyên mục hoặc trùng từ (không dấu) giữa tiêu đề; chưa cần embedding.
2. Lời dặn gửi AI: danh sách ứng viên (ID + tiêu đề) và bài viết, **mỗi thứ trong một khung dữ liệu** (`security.md` 2.4). Cần thêm tên khung mới (ví dụ `danh_sach_bai`) vào `DATA_TAGS` ở `seo_app/content/prompts.py` để được vô hiệu thẻ khung như các khung khác. **Không gửi URL cho AI**, chỉ gửi ID.
3. AI trả khuôn pydantic: `[{post_id, section, anchor}]` (`section` = số thứ tự phần như `Flag.section`), ≤ 1 link mỗi đích, tổng ≤ 5.
4. Code kiểm từng gợi ý, sai là **bỏ**, không sửa giùm:
   - `post_id` có trong danh sách ứng viên;
   - `anchor` có **nguyên văn** trong thân phần đó (không nằm trong tiêu đề H2/H3), 2–8 từ, không trùng anchor khác;
   - không 2 link vào cùng một đoạn.
5. Người dùng tick chọn trong bảng (bố cục demo đã duyệt: cột "Dùng", "Cụm từ trong bài", "Trỏ tới bài").

### 4.3 Chèn link mà không phá lớp bảo vệ đã có (T-004 → T-015)

Nguyên tắc: **AI không bao giờ viết link**. Chữ AI vẫn đi qua `clean_ai_text` như cũ (bỏ thẻ, bỏ link, `escape_link_syntax`). Không được dùng `unescape_link_syntax` hay nới bất kỳ bộ lọc nào để "cho link đi qua".

| Bước | Ở đâu | Việc |
|---|---|---|
| 1 | Bài đang soạn | Link lưu **riêng** dạng dữ liệu `InternalLink(section, anchor, post_id)`, không nhét vào chữ Markdown |
| 2 | Khi dựng HTML (Giai đoạn 5) | Markdown → HTML (bộ chuyển có escape, không autolink, theo `board.md`). **Sau đó** hàm `apply_links(html, links, index)` duyệt **nút chữ** bằng `html.parser` (không regex trên HTML), bọc lần xuất hiện đầu tiên của anchor ở đúng phần bằng `<a href="…">`. `href` lấy từ **cache**, không từ AI; `html.escape(quote=True)`. Không chèn bên trong `<a>`, `<h2>`/`<h3>`, `<code>` |
| 3 | Ngay trước gửi | `sanitize_html` cho **toàn bộ** HTML cuối (như `create_draft` đang làm) |
| 4 | Màn hình xác nhận (Giai đoạn 5, bắt buộc theo `board.md`) | Liệt kê mọi `href`; đánh dấu link không cùng tên máy với `WORDPRESS_URL`, có `@` ở phần tên máy, hoặc trỏ tới ID không còn trong danh sách đã đăng |

Như vậy link nội bộ chỉ đi vào ở **một** chỗ do code viết, các lớp T-004 → T-015 giữ nguyên.

### 4.4 Chặn link tới bài nháp (YC-603)

- Danh sách ứng viên chỉ lấy từ cache `publish` (4.1).
- Link do người dùng tự gõ trong bài (Giai đoạn 5): nếu cùng tên miền site mà đường dẫn **không** có trong cache, hoặc có dạng `?p=123` / `?page_id=123` / `preview=true` (dạng URL của nháp) → **Chặn** (M7 #11).

### 4.5 Kiểm link hỏng không gọi mạng thật trong test (YC-604)

| Loại link | Kiểm thế nào | Mức (M7 #11) |
|---|---|---|
| Nội bộ (cùng tên miền) | So với cache **vừa tải lại** (4.1): đường dẫn không có trong danh sách đã đăng = hỏng hoặc chưa đăng | Chặn |
| Bắt buộc theo phiếu (trang dịch vụ đích) | Phải có mặt trong HTML cuối và có trong cache | Chặn |
| Ra ngoài | AI không chèn được (4.3). Link người dùng tự gõ: chỉ liệt kê ở màn hình xác nhận, **không** tự gọi tới trang lạ (tránh app đi "dò" địa chỉ do bài chứa) | Cảnh báo |
| Neo trong bài (`#muc`) | Có `id` tương ứng trong HTML | Cảnh báo |

Không cần gửi HEAD/GET tới từng link: nguồn sự thật là REST của chính site, gọi bằng client đã có (https, timeout, chỉ `WORDPRESS_URL`). Test dùng `tests/fake_wordpress.py` sẵn có và cache trong thư mục tạm.

---

## 5. Meta (YC-401, YC-402)

### 5.1 Đếm độ dài tiếng Việt có dấu

- Chữ Việt có thể đến ở 2 dạng: dựng sẵn (NFC, "ữ" = 1 ký tự) hoặc tổ hợp (NFD, "ữ" = 3 ký tự; hay gặp khi dán chữ trên Mac). Đếm bằng `len()` thô thì cùng một câu có thể dài gấp đôi.
- Quy tắc: **chuẩn hóa NFC trước khi đếm và trước khi gửi**; bỏ ký tự vô hình (loại Cf, như `_neutralize` đang làm); gộp khoảng trắng; không cho xuống dòng (SiteSEO cũng bỏ qua `sanitize_text_field`).
- Bước SEO hiện đếm `len(S.meta_title)` thô (`app/views/write.py:781, 785`): sửa khi làm thật.
- Ngưỡng (giữ như demo đã duyệt, khớp YC-401):

| Trường | Nên | Cảnh báo (M7 #9) | Chặn |
|---|---|---|---|
| Meta title | 50–60 ký tự | < 30 hoặc > 65 | rỗng; có thẻ HTML; có `%%` |
| Meta description | 120–155 ký tự | < 70 hoặc > 160 | rỗng; có thẻ HTML; có `%%` |
| Slug | ≤ 60 ký tự, 3–7 từ | dài hơn | rỗng; có ký tự ngoài `a-z0-9-` |

Google cắt theo **độ rộng điểm ảnh** (khoảng 580–600 px), không theo số ký tự; ký tự có dấu rộng xấp xỉ chữ không dấu nên đếm ký tự NFC là đủ dùng. Ngưỡng điểm ảnh **chưa xác minh**, nên chỉ dùng để Cảnh báo.

`%%`: SiteSEO hiểu `%%tên%%` là biến (ví dụ `%%post_title%%`, `main/titlesmetas.php:407` `replace_variables`, mẫu mặc định `main/install.php:82`), nên chữ của phần mềm không được chứa `%%`.

### 5.2 Slug không dấu

- Dùng `seo_app/text.py` `slugify` (đã có: bỏ dấu, `đ → d`, nối `-`, cắt 80).
- Thêm: cắt mặc định 60; bỏ từ nối vô nghĩa ở **cuối** slug; slug của phiếu giao bài thắng slug tự sinh (yêu cầu 3.1).
- Kiểm trùng với `slug` trong cache: trùng thì WordPress tự thêm `-2` → **Chặn** (N5: hai trang cùng nhắm một từ khóa).

### 5.3 AI tạo meta theo lời dặn có khung dữ liệu

- Hàm mới, ví dụ `ContentWriter.meta(keyword, title, parts, research)`, gọi lớp provider đã có, việc `meta` trong `config/ai.toml` (đã khai báo sẵn: *Thợ Máy kiểm lại tên việc khi làm*).
- Dữ liệu (bài viết, ý định tìm kiếm, hồ sơ doanh nghiệp) nằm trong các khung `<bai_viet>`, `<du_lieu_tham_khao>`, `<ho_so_doanh_nghiep>` như `prompts.py` đang làm, kèm `DATA_RULES`.
- Khuôn trả về: `MetaSuggestions{titles: list[str] (3), descriptions: list[str] (2)}`.
- Kiểm kết quả trước khi dùng (A2): `strip_tags`, NFC, bỏ xuống dòng, bỏ `%%`, không link/URL, không cụm cấm (`find_banned` với `config/content.toml`), không nêu giá (theo `BAN-GIAO.md` 7.4), có từ khóa chính (không phân biệt hoa thường, so cả bản không dấu), độ dài trong ngưỡng Chặn. Gợi ý hỏng thì bỏ; hỏng hết thì báo lỗi tiếng Việt và cho viết lại.
- Nút 🔄 (đã có trong bố cục) = viết lại riêng title hoặc riêng description, giữ bản trước để quay lại (đúng quyết định "viết lại một phần không đụng phần khác").
- Hậu tố thương hiệu: site đang dùng "… | Pro Metal" ở một số bài (GET #3). Thống nhất một dạng: **câu hỏi 3**.

### 5.4 Kiểm trùng title/meta với bài khác (YC-402, M7 #6: Chặn)

- Nguồn so sánh: cache (4.1), gồm tiêu đề bài, `_siteseo_titles_title`, `_siteseo_titles_desc` của cả 29 URL. Mục meta rỗng thì so với tiêu đề bài (SiteSEO dùng mẫu `%%post_title%% %%sep%% %%sitetitle%%` khi để trống).
- Chuẩn hóa trước khi so: NFC, chữ thường, gộp khoảng trắng, bỏ dấu câu, bỏ hậu tố thương hiệu (" | Pro Metal", " - Pro-Metal"…).
- Trùng hệt sau chuẩn hóa → **Chặn**. Giống nhiều (tỉ lệ từ chung theo bản không dấu ≥ 0,8, chỉ dùng `difflib`/`set` của thư viện chuẩn) → **Cảnh báo**, hiện tên bài bị giống.
- Bỏ qua chính bài đang cập nhật (YC-804, sau này).

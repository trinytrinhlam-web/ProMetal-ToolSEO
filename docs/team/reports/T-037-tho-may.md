# Báo cáo T-037 · Danh sách bài/trang đã đăng + cache SQLite

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-037](../tickets/T-037-danh-sach-bai-da-dang-cache.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Phần mềm giờ đọc được danh sách bài và trang **đã đăng** trên suachuacuasat.com (kèm tiêu đề SEO và mô tả SiteSEO nếu có), chỉ bằng lệnh đọc, không sửa gì trên site. Danh sách được lưu tạm trong `data/site_index.sqlite`; cũ hơn 6 giờ thì tự tải lại, file hỏng hay bị xóa thì tự tạo lại. Chưa có gì thay đổi trên giao diện: các phiếu sau (T-036 kiểm trùng meta, T-039 liên kết nội bộ) sẽ dùng danh sách này.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | **Chỉ thêm**: `PublishedItem` (tự kiểm khuôn), `WordPressClient.list_published()`, `is_site_link()`, các hàm phụ `_published_from`, `_clean_text`, `_rendered`, `_matches`, hằng giới hạn độ dài. Không đổi hàm có sẵn |
| `seo_app/wordpress/__init__.py` | Xuất thêm `PublishedItem`, `is_site_link` |
| `seo_app/storage/site_index.py` | Mới: `SiteIndexStore` (`get`, `refresh`, `is_stale`, `load`, `save`, `clear`), `SiteIndex` |
| `tests/test_wordpress_published.py` | Mới: 55 test cho `list_published` |
| `tests/test_site_index.py` | Mới: 49 test cho cache |
| `tests/test_wordpress_client.py` | Sửa test `test_client_has_no_publish_function` (xem "Rủi ro" #1) |

Không tạo `seo_app/onpage/__init__.py` (không cần).

## Cách dùng (cho T-036, T-039, Giai đoạn 5)

```python
from seo_app.storage.site_index import SiteIndexStore
from seo_app.wordpress import WordPressClient

store = SiteIndexStore()                   # data/site_index.sqlite, 6 giờ
index = store.get(client)                  # cache còn mới thì dùng, không thì tải lại
index = store.refresh(client)              # nút "Tải lại" và NGAY TRƯỚC KHI GỬI NHÁP
index.items                                # tuple[PublishedItem, ...]
index.by_link()                            # {link: PublishedItem} để kiểm link hỏng
index.cache_error                          # khác "" nếu tải được nhưng không ghi được file
```

`get`/`refresh` ném `WordPressError` (tiếng Việt) khi mạng/site lỗi; cache cũ vẫn giữ nguyên.

## Thiết kế chính

**`list_published()`**
- `GET /wp/v2/posts` và `GET /wp/v2/pages`, đường cố định trong code; `status=publish`, `per_page=100`, `orderby=id`, `_fields=id,type,status,slug,link,title,modified_gmt,meta`. Không xin `context=edit`. Dùng lại `_get_all_pages` (giới hạn `MAX_PAGES`), `_request` (timeout của client, SSL bật, chỉ https).
- Lọc phía app: chỉ giữ `status == "publish"` đúng chữ (bỏ `future`, `draft`, `private`, `pending`, `trash`, thiếu status, `PUBLISH`).
- `is_site_link`: phải `https`, đúng tên máy (không phân biệt hoa thường, không nhận tên miền con), đúng cổng (443 mặc định), không có tên/mật khẩu trong địa chỉ, không khoảng trắng/ký tự điều khiển/dấu `\`, ≤ 2000 ký tự. Sai thì bỏ cả mục.
- Tiêu đề, meta title, meta description: qua `_plain`, bỏ ký tự điều khiển, gộp khoảng trắng, cắt 300 / 500 ký tự. Meta thiếu hoặc sai kiểu thì rỗng; meta dạng mảng lấy phần tử đầu.
- `id` phải là số nguyên dương thật (không nhận `"12"`, `True`, `1.5`); `type` lấy theo đường gọi, không tin trường `type` site trả. Slug/ngày sai dạng thì để rỗng (không bỏ mục). Trùng (loại, id) thì bỏ bản sau.

**Cache `site_index.py`**
- Bảng `pages(id, type, slug, link, title, meta_title, meta_desc, modified_gmt)`, khóa `(type, id)`; bảng `info(key, value)` giữ `schema_version`, `site` (WORDPRESS_URL lúc tải), `fetched_at` (ISO kèm `+07:00`).
- Ghi: một giao dịch, xóa hết rồi ghi lại; mọi SQL dùng `?`.
- Đọc (dữ liệu chưa tin cậy): giới hạn số dòng (`MAX_ITEMS` = 10.000) và độ dài từng ô bằng SQL **trước** khi đọc vào bộ nhớ; chữ không phải UTF-8 bị bắt; từng dòng dựng lại `PublishedItem` (kiểm khuôn) và `is_site_link`. Một dòng sai = cả cache hỏng: xóa file, tải lại.
- File không phải SQLite, sai cột, hoặc là **liên kết tắt** (symlink): xóa (chỉ xóa chính liên kết, không đụng file đích) rồi tạo lại. Không đổi tên sang một bên như `drafts.py` vì cache không có gì cần giữ.
- Cache của site khác (đổi `WORDPRESS_URL`) bị bỏ qua và ghi đè. `fetched_at` ở tương lai quá 5 phút (đồng hồ chỉnh lùi, file sửa tay) = cũ, tải lại.
- Không ghi được file (ổ đầy, thư mục bị khóa): vẫn trả danh sách vừa tải, kèm `cache_error`.

## Bằng chứng

```
$ uv run pytest
4762 passed, 4 skipped, 16 xfailed, 1 warning in 224.71s

$ uv run ruff check .
All checks passed!
```

(Trước phiếu: 4.658 test; thêm 104. `ruff format --check` báo 13 file cũ chưa định dạng, không file nào của phiếu này.)

## Đối chiếu tiêu chí xong

- [x] `list_published()` chỉ trả bài đã đăng, link đúng tên miền: `test_drops_future_draft_private_and_missing_status`, `test_drops_items_with_foreign_or_bad_link` (19 dạng link xấu), `test_only_get_on_fixed_paths_with_status_publish`
- [x] Tiêu đề có HTML, meta thiếu: `test_title_and_meta_are_plain_text`, `test_missing_or_odd_meta_is_empty`
- [x] Nhiều trang kết quả: `test_reads_many_pages`, `test_page_count_is_capped`
- [x] Cache tạo/đọc/làm mới: `test_first_get_downloads_and_saves`, `test_second_get_uses_cache`, `test_stale_cache_reloads_by_itself`, `test_refresh_always_downloads`
- [x] Chịu file hỏng/sai cấu trúc: `test_garbage_file_is_dropped_and_reloaded`, `test_wrong_structure_is_dropped`, `test_tampered_rows_drop_whole_cache` (17 kiểu sửa tay), `test_symlink_is_replaced_and_target_untouched`
- [x] Xóa file vẫn tạo lại: `test_deleted_file_is_recreated`, `test_deleted_folder_is_recreated`
- [x] Test không gọi site thật: chỉ `FakeWordPress` hoặc nguồn giả `Source`
- [x] `uv run pytest`, `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

1. **Sửa một test an toàn có sẵn** (`tests/test_wordpress_client.py`): `test_client_has_no_publish_function` cấm mọi tên có chữ "publish", mà phiếu bắt tên `list_published`. Đã đổi thành: chỉ cho đúng **một** tên `list_published`, mọi tên khác có "publish" vẫn đỏ. `test_only_get_on_fixed_paths_with_status_publish` chứng minh hàm này chỉ gửi `GET`. Nhờ Lá Chắn xác nhận cách này (hoặc chọn đổi tên hàm).
2. **Chữ thuần nhưng chưa escape**: `_plain` giải mã `&lt;script&gt;` thành `<script>` (hành vi cũ của `_plain`, không đổi). Tiêu đề/meta trong `PublishedItem` là chữ thuần; nơi hiện lên giao diện (`unsafe_allow_html`) hoặc ghép vào HTML bài viết **phải** `html.escape`; nơi đưa vào prompt AI phải để trong khung dữ liệu (T-033 mục 4.2). Ghi rõ trong docstring `PublishedItem`.
3. **Danh sách đường gọi cố định** (yêu cầu 3): `client.py` **chưa có** cơ chế này; `_request` nhận mọi `path`. `list_published` chỉ dùng hai chuỗi cố định, nhưng không có lớp chặn chung. Không tự làm lại client (để T-042). Đề xuất bên dưới.
4. Đọc tối đa `MAX_PAGES` = 50 trang × 100 mục mỗi loại; site có hơn 5.000 bài thì phần thừa bị bỏ lặng lẽ (hiện site có 29 URL).
5. Khi tài khoản đã đăng nhập, WordPress có thể trả `link` dạng `?p=123` cho bài chưa có đường dẫn đẹp; bài đó vẫn qua kiểm tên miền nếu `status == publish`. Với bài đã đăng thì link luôn là đường dẫn tĩnh, nên chưa xử lý thêm.
6. Chưa thử trên site thật (đúng quy tắc). Giả định: REST view context trả `meta` với 4 khóa SiteSEO như T-033 mục 1.3 đã thấy.

## Đề xuất

- **T-042 (danh sách đường gọi cố định):** trong `WordPressClient._request`, kiểm `(method, path)` với một danh sách cho phép, ví dụ:
  - `GET /`, `GET /wp/v2/users/me`, `GET /wp/v2/categories`, `GET /wp/v2/tags`, `GET /wp/v2/posts`, `GET /wp/v2/pages`;
  - `POST /wp/v2/posts`, `POST /wp/v2/posts/<số>`, `POST /wp/v2/media`, `POST /wp/v2/media/<số>`;
  - 2 ability SiteSEO (`GET …/siteseo-posts/seo-data-get/run`, `POST …/siteseo-posts/seo-data-update/run`).
  So khớp toàn chuỗi bằng regex, chặn `..`, `%2e`, `//`, và mọi namespace khác (`code-snippets/v1`, `prometal/v1`…). Kèm test liệt kê đúng các đường trên và test mọi đường ngoài danh sách bị từ chối **trước khi** gửi request.
- Soi Lỗi: thử cache khi hai tab cùng `refresh` (khóa SQLite) và trên Windows (xóa file khi kết nối vừa đóng).

## Lượt 2 (2026-10-16) · sửa theo Soi Lỗi

| Mã | Mức | Đã làm |
|---|---|---|
| SL-T037-1 | Trung bình | `_is_healthy` gặp lỗi `locked`/`busy` thì **ném lại** thay vì coi file là hỏng; `_prepare` đổi thành `SiteIndexError` "đang bận". File và `-journal` của giao dịch đang chạy không bị xóa; `refresh` vẫn trả danh sách vừa tải kèm `cache_error` "đang bận". Hàm `_is_busy` dùng chung cho cả `_connect` và `_db_message` (nhận cả chữ `busy`). Đã bỏ `xfail` của `test_locked_file_is_busy_not_corrupt`; thêm `test_locked_file_is_not_deleted_and_says_busy` |
| SL-T037-2 | Thấp | Có cờ `truncated`. `list_published()` trả `PublishedList` (là `list` bình thường, thêm `truncated`), đúng khi site báo nhiều trang kết quả hơn `MAX_PAGES`. `SiteIndex.truncated` được lưu vào bảng `info` (`"0"`/`"1"`; thiếu hoặc giá trị lạ = cache hỏng, tải lại). `SCHEMA_VERSION` lên `"2"`, nên cache ghi ở lượt 1 tự bị bỏ và tải lại |

Ghi chú:
- Để không đổi `_get_all_pages` (đang dùng cho chuyên mục/thẻ, ngoài phạm vi phiếu), `list_published` dùng hàm mới `_get_pages_checked`, cùng cách đọc và cùng giới hạn `MAX_PAGES`, thêm cờ "còn trang chưa đọc". Lặp khoảng 15 dòng; T-042 có thể gộp hai hàm khi làm lại client.
- Đúng `MAX_PAGES` trang thì **không** bật cờ; hơn mới bật (`test_exactly_max_pages_is_not_truncated`, `test_truncated_when_site_has_more_than_max_pages`).
- Sửa danh sách cho phép trong `tests/test_soi_loi_t037.py::test_client_module_publish_names_are_read_only_helpers`: thêm `PublishedList` (kiểu kết quả chỉ đọc). Test vẫn chặn mọi tên khác.
- Giai đoạn 5 (kiểm link hỏng): khi `index.truncated` thì không được báo "link hỏng" chỉ vì link không có trong danh sách.

```
$ uv run pytest
4858 passed, 4 skipped, 16 xfailed, 1 warning in 211.89s

$ uv run ruff check .
All checks passed!
```

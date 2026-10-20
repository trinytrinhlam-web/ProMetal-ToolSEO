# Biên bản bảo mật T-054 · WordPress: tải ảnh và chèn `<figure>` vào nháp (G3-8)

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Kiểm lại bằng Fable sau 01/11.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem ghi chú trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-054](../tickets/T-054-chen-anh-vao-nhap-wordpress.md) |
| Phạm vi | diff `origin/main...team/T-054` (gốc `5441a68`, đầu nhánh `1aee061`): `seo_app/wordpress/client.py`, `seo_app/images/html.py` (mới), `tests/test_wordpress_images.py`, `tests/test_soi_loi_t054.py`, 2 báo cáo. Kèm code xung quanh: `sanitize.py`, `naming.py`, `process.py` (`WebImage`, `webp_chunks`), `alt.py`, `_request`, `_own_draft`, `set_featured_image`, `create_draft` |
| Ngày | 2026-10-20 (giờ máy, +07) |
| **Kết luận** | _(đang viết, xem phần 2)_ |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (`pillow==13.0.0`, `pillow-heif==1.8.1`, `requests==2.34.2`, `urllib3==2.8.0`, `streamlit==1.65.0`…). Nguồn PyPI: `No known vulnerabilities found`. Nguồn OSV (`-s osv`): `No known vulnerabilities found`. Môi trường đã cài của worktree (`--path .venv/Lib/site-packages`): `No known vulnerabilities found` (bỏ qua `seo-app` là chính dự án) | Có. Chạy `-r` kiểu thường báo `ResolutionImpossible` (pip giải lại phụ thuộc, vướng `pillow<13` của Streamlit mà T-058 đã ép bằng `override-dependencies`), nên chạy `--disable-pip --no-deps` trên danh sách đã ghim đủ. `uv.lock`, `pyproject.toml` giống `main` (`git diff --quiet`) |
| bandit 1.9.4 | 2 file code của phiếu (`html.py`, `client.py`, 1.369 dòng): `No issues identified`. Toàn bộ `seo_app app scripts`: 1 mục Low (B101 `assert`) ở `seo_app/storage/drafts.py:203` | Có. `drafts.py` không thuộc diff (không đổi trong nhánh), là kiểm tra nội bộ có từ trước, không liên quan phiếu |
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`** (LC-T049-4), quét bằng `--all-files` trong thư mục riêng (ghi chú bàn giao Lá Chắn T-052: quét file theo tên thì không bắt mồi). Bộ quét: 6 file của nhánh, toàn bộ patch của nhánh (`git log -p origin/main..team/T-054`, 9 commit, 141 KB), patch 9 commit mới nhất của `main` (từ 15:00, 133 KB), kèm **file mồi có chữ tiếng Việt** (một khóa AWS giả, một dòng gán mật khẩu giả). Mồi: **bắt đủ 2/2**. 6 file hiện tại: **0**. Patch `main`: **0**. Patch nhánh: 1 mục (dòng 30) | Có. Mục duy nhất là biến `PASSWORD` gán khóa giả `abcd efgh…` của fixture `wp_client` (`tests/conftest.py:235`), đã đổi tên thành `KHOA_GIA` ở `1aee061`, dòng cũ còn trong lịch sử: báo nhầm. Đã xóa file mồi (nằm ngoài repo, thư mục nháp của phiên) |
| Soát lịch sử git | Lệnh `security.md` mục 5 (`grep -inE "api[_-]?key\|password\|secret\|token"`) trên `git log -p origin/main..team/T-054`: 12 dòng, đều là khóa giả `abcd efgh ijkl`, biến `AUTH` (base64 của khóa giả đó), vòng lặp kiểm "không lộ khóa" của test, câu lệnh detect-secrets trong báo cáo. `git diff --numstat`: không file nhị phân, không ảnh, không `.env`/`.sqlite`/`.json` | Có. Không có khóa thật |
| pytest | 20 file liên quan (`test_soi_loi_t054.py`, `test_wordpress_images.py`, `test_app_wordpress.py`, `test_images_process.py`, `test_safety.py`, 4 file `test_sanitize*.py`, 7 file T-042, `test_wordpress_client.py`, `test_wordpress_published.py`, `test_wordpress_site_link_t042.py`): **2123 passed, 6 xfailed in 155.58s** (Windows 11, tại `1aee061`). 6 `xfail(strict=True)` là SL-T054-1…3 | Có. Khớp số của Soi Lỗi (2123/6). Không chạy toàn bộ pytest (Chỉ Huy chạy khi gộp) |
| ruff 0.16.10 | `uv run ruff check .`: `All checks passed!` | Có |
| Kiểm gộp với `main` | `git merge-tree --write-tree origin/main team/T-054` (main `881548f`, **đã gồm T-052** `1c7bd9a`): cây `9972eec`, **không xung đột** | Có. Từ gốc `5441a68`, `main` chỉ thêm `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, test T-052 và tài liệu; không file nào T-054 dùng (`client.py`, `html.py`, `sanitize.py`, `process.py`, `naming.py`, `alt.py`, `onpage/meta.py`, `tests/conftest.py`, `tests/fake_wordpress.py`) bị đổi (`git diff --stat` rỗng), nên kết quả test của nhánh áp dụng cho bản gộp |

## Thử độc lập (không mạng, site giả `FakeWordPress`)

Script nằm trong thư mục nháp của phiên (không commit), chạy bằng `uv run python` trong worktree.

1. **Shortcode qua alt/chú thích (SL-T054-2).** 6 dạng: `[code_snippet id=1 php=true]` trong chú thích; `[code_snippet id=1]` trong alt; tên chen U+200B (`[code​_snippet id=1]`); chen U+202E (ký tự đảo chiều, người duyệt thấy chữ lộn xộn); `[[code_snippet id=1]]`; `[embed]https://www.youtube.com/watch?v=x[/embed]`. Kết quả: shortcode đi **nguyên dạng, liền mạch** vào `alt="…"`, `<figcaption>` của nội dung nháp và vào trường REST `alt_text`, `title`, `caption` của Media. Hai dạng có ký tự vô hình bị `plain_image_text` (`html.py:56-57`, `normalize_meta`) gỡ ký tự đó, nên **thành shortcode chạy được** dù chữ người dùng duyệt trông khác. `[[…]]` WordPress tự coi là thoát (không chạy).
2. **Bộ lọc giải mã `&#91;`.** `sanitize_html('<p>&#91;code_snippet id=1&#93;</p>')` → `<p>[code_snippet id=1]</p>`; trong thuộc tính `alt="&#91;…"` và `<figcaption>&#x5b;embed]…` cũng ra `[` trần. Nghĩa là: escape `[` ở `html.py` sẽ vô hiệu (`create_draft` lọc lại cả bài, `client.py:693`), và HTML phần thân viết `&#91;…&#93;` (WordPress **không** chạy) bị chính bộ lọc biến thành shortcode chạy được.
3. **Thứ tự lệnh.** `POST /wp/v2/media` → `POST /wp/v2/media/100` → `POST /wp/v2/posts` (không `_fields`) → `GET /wp/v2/posts/42?context=edit&_fields=id,status,meta` → `POST /wp/v2/posts/42` (không `_fields`). Không có `DELETE`, không đường lạ.
4. **Đối chiếu mã nguồn WordPress** (kho `wordpress-develop`, nhánh trunk, đọc qua mạng công khai, không gọi site): `WP_REST_Posts_Controller::create_item()` và `update_item()` kết thúc bằng `prepare_item_for_response()`, trong đó `content.rendered = apply_filters( 'the_content', $post->post_content )` khi trường được chọn (không gửi `_fields` thì mọi trường đều được chọn). `do_shortcode` móc vào `the_content`, và `do_shortcodes_in_html_tags()` chạy cả shortcode nằm trong thuộc tính có dấu nháy (`alt="[…]"`) rồi mới lọc kết quả bằng `wp_kses_one_attr`. Kết luận: shortcode trong nội dung **chạy trên máy chủ ngay trong lệnh tạo nháp** của app (và lại chạy ở lệnh đặt ảnh đại diện), bằng tài khoản của app, không cần ai bấm Xem trước hay Đăng.
5. **Lỗ hổng công khai của Code Snippets** (WPScan, công bố 2025-11-18): CVE-2025-13035, mọi bản tới **3.9.1**, sửa ở **3.9.2**: `evaluate_shortcode_from_flat_file` gọi `extract()` trên thuộc tính shortcode `[code_snippet]`, ghi đè `$filepath` rồi `require_once` → **chạy mã PHP trên máy chủ**. Điều kiện: tài khoản từ Contributor trở lên (tài khoản app là Biên tập viên), quản trị đã bật "Enable file-based execution", có ít nhất một Content snippet đang bật. CVSS 3.1: 8.0. Chưa biết phiên bản và cài đặt của Code Snippets trên suachuacuasat.com.
6. **Mã ảnh trùng (G3 của Soi Lỗi).** Site giả trả mã 100 cho cả 2 lần tải: hàm nhận cả hai (`images = [100, 100]`), lệnh ghi alt thứ hai đè ảnh 100 ("Ảnh một" → "Ảnh hai").
7. **SL-T054-1.** `clean_ai_text("[Trước khi sửa]: cổng sắt gỉ sét")` → `[Trước khi sửa]\: …`; `plain_image_text("Minh họa " + …)` vẫn còn `\:`. Tái hiện đúng.
8. **Không lộ mật khẩu.** Lệnh tạo nháp hết giờ, thông điệp lỗi gốc chứa mật khẩu giả: câu báo `DraftImagesError` (cả `str`, `repr`, `uploaded`) không có mật khẩu (có/không dấu cách), không có `Basic `, `__cause__` rỗng (`from None`, `client.py:1019`).
9. **Chốt cuối của `figure_html` (G5 của Soi Lỗi).** Chú thích `chữ src="https://example.com/a.webp" alt=y` ra `<figcaption>chữ src="https://example.com/a.webp" alt=y</figcaption>` (bộ lọc in lại dấu nháy trần trong chữ): chuỗi mà `html.py:102` tìm có mặt ngay trong chú thích. `figure_html` chạy 2 lượt qua `sanitize_html` vẫn như cũ.
10. **Chữ thường «[Lưu ý]»** trong chú thích đi nguyên (để T-061 có mẫu "không được phá").

## Báo nhầm đã loại

- **detect-secrets**, `branch.patch` dòng 30: biến `PASSWORD` gán khóa giả `abcd efgh…` của fixture `wp_client` (`tests/conftest.py:235`), đã đổi tên ở commit cuối của Soi Lỗi; dòng cũ còn trong lịch sử nhánh. Không phải khóa thật.
- **bandit** B101 `seo_app/storage/drafts.py:203`: `assert` có từ trước, ngoài diff.
- **Grep lịch sử nhánh** 12 dòng: khóa giả và câu lệnh trong báo cáo (xem bảng trên).
- **pip-audit `-r` báo `ResolutionImpossible`**: lỗi cách chạy (pip giải lại phụ thuộc), không phải lỗ hổng; chạy lại `--disable-pip --no-deps` ra 0.

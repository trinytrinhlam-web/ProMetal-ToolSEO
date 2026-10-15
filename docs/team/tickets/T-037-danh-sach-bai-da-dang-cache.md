# T-037 · Danh sách bài/trang đã đăng trên site + cache SQLite

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 (nhóm 1: logic thuần, test giả) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không. Chạy song song được với T-036, T-038 |
| Trạng thái | Chờ chỗ trống |

## Mục tiêu

App biết site đang có những bài/trang **đã đăng** nào, cùng meta title/description của chúng. Danh sách lưu tạm trên máy. Phục vụ:
- kiểm trùng meta (T-036);
- liên kết nội bộ (T-039);
- kiểm link hỏng trước khi gửi (Giai đoạn 5).

## Bối cảnh

Thiết kế: `docs/team/reports/T-033-tho-may.md`:
- mục 1.3: site đã mở `_siteseo_titles_title`, `_siteseo_titles_desc` trong REST;
- mục 4.1;
- mục 6: phiếu "T-035" trong báo cáo, nay là **T-037**.

## Phạm vi

- **Được sửa:**
  - `seo_app/wordpress/client.py`: chỉ **thêm** hàm đọc `list_published()`. Không đổi hàm có sẵn;
  - mới: `seo_app/storage/site_index.py`, `tests/test_site_index.py`, test cho `list_published`;
  - mới: `seo_app/onpage/__init__.py`, chỉ khi cần dùng chung, nội dung y hệt dòng nêu ở T-036.
- **Không được sửa:** `app/**`, `seo_app/ai/**`, `seo_app/content/**`, hàm ghi trong `client.py`.

## Yêu cầu

1. **`list_published()`:**
   - `GET /wp/v2/posts` và `GET /wp/v2/pages` với `status=publish` và `_fields` tối thiểu;
   - dùng lại phân trang có giới hạn sẵn (`_get_all_pages`, `MAX_PAGES`);
   - **lọc lại phía app:** chỉ giữ `status == "publish"` (bỏ `future`, `draft`, `private`…);
   - `link` phải là `https://` và **đúng tên máy** của `WORDPRESS_URL`, sai thì bỏ mục;
   - tiêu đề và meta qua `_plain` (đã có), có giới hạn độ dài;
   - meta SiteSEO không có trong kết quả thì để rỗng, không lỗi.
2. **Cache `site_index.py`:**
   - file `data/site_index.sqlite`, cùng chỗ với `drafts.sqlite` (`.gitignore` đã chặn);
   - bảng gồm id, loại, slug, link, tiêu đề, meta title, meta description, thời điểm sửa; thời điểm tải lưu kèm múi giờ (`Asia/Ho_Chi_Minh`);
   - SQL chỉ dùng tham số `?`;
   - dữ liệu đọc lại từ file là **chưa tin cậy**: kiểm như `seo_app/storage/drafts.py` (file hỏng thì bỏ cache và tải lại, không làm app chết);
   - hàm "cũ hơn N giờ chưa" (mặc định 6) và "tải lại ngay";
   - xóa file vẫn tạo lại được;
   - đường dẫn bằng `pathlib`, mở file `encoding` đúng, chạy được trên Windows/Mac.
3. **Danh sách đường gọi cố định.** Client chỉ được gọi các đường REST đã liệt kê. Nếu `client.py` chưa có cơ chế này thì ghi đề xuất vào báo cáo, **không** tự làm lại client (T-042 làm). Site có các đường nhạy cảm: `/code-snippets/v1`, `/prometal/v1/deploy-files`, `/prometal/v1/purge` (T-033 mục "Rủi ro").
4. **Test** dùng `tests/fake_wordpress.py` sẵn có hoặc giả lập tương đương, không gọi site thật:
   - lẫn bài `future`/`draft`;
   - `link` sai tên miền hoặc `http://`;
   - tiêu đề có HTML;
   - meta thiếu;
   - file cache hỏng hoặc sai cấu trúc;
   - cache cũ thì tự tải lại;
   - nhiều trang kết quả.

## Yêu cầu bảo mật riêng

W4 (https, timeout), chỉ `GET`; F1, F3; D2 (`.gitignore`); D3.

## Tiêu chí xong

- [ ] `list_published()` chỉ trả bài đã đăng, link đúng tên miền: có test
- [ ] Cache tạo/đọc/làm mới/chịu file hỏng: có test
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-037-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (W2, W4, F1, D2).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-037 Danh sách bài đã đăng, cache"**, nhánh `team/T-037` (từ `main`).

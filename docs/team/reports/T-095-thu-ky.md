# Báo cáo T-095 · README: bước SEO trên trang Soạn bài, tài khoản WordPress cho app

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-095](../tickets/T-095-readme-buoc-seo-tai-khoan-wordpress.md) |
| Ngày nộp | 2026-10-27 |
| Nhánh | `team/T-095` (từ `10c7933`; nhánh đã có T-041, T-084) |
| Kết quả | Hoàn thành yêu cầu 1–4. Chỉ sửa `README.md` |

## Tóm tắt (cho chủ dự án)

- **Mục 10 mới «Bước SEO: tiêu đề, mô tả, đường dẫn»**: cách dùng bước 4 · SEO của Soạn bài:
  - AI gợi ý tiêu đề, mô tả; nút 🔄 viết lại riêng từng ô; ↶ ↷ quay lại bản trước;
  - nhãn Nên / Cảnh báo / Chặn (bảng: nghĩa của từng màu, khi nào gặp);
  - đường dẫn (slug), kiểm trùng với bài đã đăng, khung «Chép sang SiteSEO»;
  - liên kết nội bộ, schema hỏi đáp;
  - công tắc «Ghi SEO lên website»: mặc định tắt, chỉ ghi vào bài nháp app vừa tạo, kèm bảng các câu kết quả.
- README nói rõ những gì **app chưa gửi** lên website: đường dẫn, liên kết nội bộ, schema. Phải tự làm trong WordPress tới Giai đoạn 5.
- **Mục 6 «Kết nối WordPress» viết lại theo lần thử thật 27/10**:
  - tạo tài khoản **Biên tập viên** riêng;
  - tạo mật khẩu ứng dụng **trên chính tài khoản đó**;
  - `WORDPRESS_USERNAME` là **tên đăng nhập**, không phải tên đặt cho mật khẩu ứng dụng (đây là nguyên nhân lỗi 401 hôm 27/10);
  - SiteSEO từ bản 1.4.0, bật **AI Abilities**;
  - Kiểm tra kết nối phải thấy vai `editor` và «SiteSEO: ghi được».
- Bảng lỗi mục 6: dòng «từ chối đăng nhập (mã 401)» nay bảo **kiểm tên đăng nhập trước**, rồi mới nghĩ tới hosting, plugin.
- Mục 6 thêm **«Lưu ý trên website»**:
  - không dùng trình sửa `.htaccess` của SiteSEO Pro;
  - gỡ mật khẩu ứng dụng không còn dùng, nhất là trên tài khoản quản trị.
- Đánh số lại: «Gửi bài nháp» thành mục 11, «Cập nhật» mục 12, «Xử lý sự cố» mục 13. Mọi chỗ «xem mục …» đã sửa theo.

## Đã thay đổi

| Chỗ (`README.md`) | Thay đổi |
|---|---|
| `:7` (Trạng thái) | Thêm bước SEO (mục 10), gửi nháp thành mục 11, có thể ghi luôn tiêu đề, mô tả SEO |
| `:46` | «chọn ảnh, bước SEO và gửi bài nháp cũng đã chạy thật (mục 9, 10, 11)» |
| `:65-111` (mục 6) | Viết lại thành 4 khối, 10 bước: «Tạo tài khoản riêng cho app, vai Biên tập viên» (bước 1–2), «Tạo mật khẩu ứng dụng trên chính tài khoản đó» (3–6), «Khai vào app» (7, có hai ý: tên đăng nhập khác tên mật khẩu ứng dụng; xem tên đăng nhập ở đâu), «Bật cho app ghi SEO vào SiteSEO» (8–9: SiteSEO ≥ 1.4.0, menu SiteSEO → AI Abilities, bật công tắc), «Kiểm tra» (10: «Kết nối thành công…», «vai trò: editor», «SiteSEO: ghi được» / «chưa bật» / «chưa dò được») |
| `:119-122` (mới) | «Lưu ý trên website»: trình sửa `.htaccess` của SiteSEO Pro xóa các dòng `<…>` khi lưu; thu hồi mật khẩu ứng dụng không dùng (tài khoản quản trị) |
| `:128` | Dòng 401: kiểm tên đăng nhập trước; mọi lỗi 401 app báo cùng một câu nên dễ tưởng lỗi hosting; rồi mật khẩu ứng dụng trên đúng tài khoản; sau cùng mới là plugin bảo mật, header `Authorization` |
| `:130` | «không đủ quyền»: tài khoản Biên tập viên, xem dòng «vai trò: …» |
| `:135` (mục 7) | Bước SEO không còn là bản demo; chỉ Hẹn giờ, Đăng ngay còn demo |
| `:161` (7.2) | Danh sách việc AI thêm «gợi ý tiêu đề và mô tả SEO, gợi ý liên kết nội bộ» (`[tasks.meta]`, `[tasks.links]`) |
| `:200-201` (7.4) | Bước 5 (SEO, mục 10) và bước 6 (Xuất bản, mục 11) thay câu «Bước SEO còn là bản demo» |
| `:209` (7.5) | `config/content.toml` mục `[meta]`: đuôi « \| Pro-Metal», cụm nên tránh |
| `:250` (mục 8) | Theo T-084 (đã có trên nhánh): tab Ảnh hiện tên ngắn, câu «⚠️ Chưa thấy thư mục ảnh số … trên máy này (USB chưa cắm hoặc Google Drive chưa chạy?)» |
| `:324` | «(mục 10)» → «(mục 11)» |
| `:344-420` (mục 10 mới) | Bước SEO, gồm: Tiêu đề và mô tả · bảng Nhãn · Đường dẫn (slug) (kèm dòng «Từ khóa chính» khi từ khóa hỏng) · Kiểm trùng · Xem trước và «Chép sang SiteSEO» · Liên kết nội bộ · Schema · Ghi SEO lên website (kèm bảng 7 câu kết quả) |
| `:422-439` (mục 11) | Số mục; bước 4 mới (công tắc «Ghi SEO lên website»); dòng kết quả SEO sau khi gửi; «Cần biết khi gửi»: bỏ «(bước SEO còn là bản demo)», ghi rõ chuyên mục, đường dẫn, liên kết nội bộ, schema chưa gửi; tiêu đề, mô tả SEO, từ khóa chính chỉ lên khi bật công tắc |
| `:464`, `:470` | «11. Cập nhật…» → 12, «12. Xử lý sự cố» → 13 |

## Đối chiếu với code

Code của nhánh `team/T-095`: `app/views/write.py`, `app/views/wordpress.py`, `app/views/settings.py`, `seo_app/wordpress/client.py`, `seo_app/onpage/meta.py`, `seo_app/onpage/schema.py`, `seo_app/storage/site_index.py`, `config/ai.toml`, `config/content.toml`.

**Câu trích.** Mọi câu README trích trong «…» hay tên nút in đậm đều có trong code. Kiểm 68 câu bằng `grep -rF` trên `app seo_app config`. Hai câu có emoji 4 byte (`🔄 Tải lại danh sách bài`, `📤 Gửi nháp`) `grep` của Git Bash báo sót, nên kiểm lại bằng Python (`True True` cả code lẫn README).

**Hành vi README mô tả.**

| README nói | Code |
|---|---|
| Nút «✨ AI gợi ý tiêu đề và mô tả SEO» chỉ hiện khi hai ô trống | `write.py:2353-2360` (`empty and st.button(...)`) |
| 🔄 viết lại riêng một ô; ↶ ↷; tự sửa là bản mới; «Bản N/M» | `meta_field` `:2086-2128`, `meta_edited` `:2037`, `suggest_meta(writer, field)` |
| Đuôi « \| Pro-Metal» khi còn chỗ (≤ 60), đổi ở `[meta]` | `onpage/meta.py:277` (`with_brand`, `TITLE_LIMITS.good_max`), `config/content.toml:187-191` |
| Ngưỡng 50–60 / 120–155 (Nên), < 30 / > 65, < 70 / > 160 (Cảnh báo) | `meta.py:74-75`, `_check_text` `:136-175` |
| Chặn: trống, ký tự lạ, thẻ HTML, `<` liền chữ, `%%`, `&#37;`, `[...]`, trùng hệt | `_check_text` `:140-155`; `siteseo_copy` (lượt 3 Họa Sĩ, SL-T041-11); `final_seo` `write.py:2207-2236` |
| Slug: tự gợi ý, sửa tay tự bỏ dấu, 🔄 «Gợi ý lại từ từ khóa», 3–7 từ, ≤ 60 ký tự | `slug_field` `write.py:2154-2166`, `meta.py:76-77` |
| Từ khóa chính hỏng: dòng riêng, «… Sửa từ khóa ở bước 1 · Chuẩn bị.», tối đa 200 ký tự | `keyword_problem` / `keyword_line` `write.py:2181-2204`; `MAX_SEO_KEYWORD_CHARS = 200` `client.py:269` |
| Danh sách bài lưu ở `data/site_index.sqlite`, dùng lại tới 6 giờ | `site_index.py:37-38` |
| Chưa kết nối: dòng báo nhẹ, phần khác dùng được | `MSG_NOT_CONNECTED` `site_index.py:321-324`; `step_seo` `write.py:2349-2350` |
| Liên kết nội bộ **chưa chèn** vào bài nháp | `links_panel` docstring `write.py:2258-2260` («link chỉ chèn lúc dựng bài gửi đi (`apply_links`, Giai đoạn 5)»); `send_and_record` gọi `create_draft_with_images(title, parts)` `:2748`, `seo_links` chỉ dùng ở bước SEO và nháp |
| Schema **chưa gửi**; ô «Dùng schema…» chỉ ghi nhớ | `seo_use_faq` chỉ có ở `KEEP_KEYS` `:152`, `faq_panel` `:2341` và `seo_snapshot` / `restore_seo` `:2389`, `:2404` |
| Đường dẫn **chưa gửi** khi tạo nháp | `create_draft_with_images(title, parts)` `:2748`, không truyền slug |
| Công tắc mặc định tắt; ghi tiêu đề, mô tả, từ khóa chính vào bài vừa tạo; hỏi lại còn nháp | `seo_toggle` `:2445-2458`; `write_seo` `:2461-2487`; `set_seo_meta` `client.py:939-980` (chỉ `_created_post_ids`, kiểm còn nháp trước khi ghi) |
| Không ghi vào nháp gửi lần trước | `write_seo` chỉ dùng `result["post_id"]` của lần gửi này (T-086 Ghi nhận 2, báo cáo Họa Sĩ T-041) |
| 7 câu kết quả SEO | `client.py:301-346` (`_SEO_NOT_DRAFT`, `_SEO_CHECK_FAILED`, `_SEO_UNAVAILABLE`, `_SEO_ERROR`, `_SEO_WRITTEN`, `_SEO_WRITTEN_NO_KEYWORD`), `write.py:1961-1969` (`MSG_SEO_RECHECK`, `MSG_SEO_WILL_SKIP`, `MSG_SEO_SKIPPED`, `MSG_SEO_UNEXPECTED`) |
| Dòng «✅ SEO: …» / «⚠️ SEO: … chưa dùng được (xem bước SEO)» | `seo_check` `write.py:2431-2442` |
| Trang Kết nối WordPress: «Kết nối thành công tới», «Tài khoản: … — vai trò: …», «SiteSEO: …» | `wordpress.py:64-73`; `siteseo_status` `client.py:455-464` |
| Mọi lỗi 401 cùng một câu | `_error_from` `client.py:1544-1550` (câu cố định theo mã HTTP) |
| Ghi chú T-059 (27/10) | `docs/team/tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md`: ghi chú 17:50 (SiteSEO 1.1.6 → 1.4.2, Abilities từ 1.4.0), 19:37 (401 do tên mật khẩu ứng dụng điền vào `WORDPRESS_USERNAME`; tài khoản Biên tập viên; gỡ mật khẩu ứng dụng ở tài khoản quản trị; trình sửa `.htaccess` của SiteSEO Pro xóa dòng `<…>`) |

## Kiểm tra

```
$ PYTHONUTF8=1 uvx detect-secrets scan README.md
  "results": {},

# Thử mồi: bản sao README ngoài repo (thư mục tạm của phiên) thêm 2 dòng khóa giả
$ PYTHONUTF8=1 uvx detect-secrets scan README.md     (bản sao)
  "type": "Base64 High Entropy String", "line_number": 510
  "type": "Secret Keyword",             "line_number": 510
  "type": "AWS Access Key",             "line_number": 511
  ...                                    → bộ quét đọc được file tiếng Việt

$ git diff README.md | grep "^+" | grep -nE "[A-Za-z]:[\\/]|/Users/|/home/|suachuacuasat|phan-mem-seo|sk-|AIza|ghp_"
9:+1. Đăng nhập trang quản trị WordPress (`https://ten-mien-cua-ban/wp-admin`) ...
  → chỉ khớp địa chỉ mẫu; không có đường dẫn máy thật, tên miền, tên tài khoản thật hay khóa
```

Không chạy pytest, ruff: chỉ đổi `README.md` và báo cáo (không có code, không có test đọc README).

## Rủi ro và điểm cần chú ý

- **Nhãn tiếng Việt của WordPress** («Người dùng → Thêm mới», «Tên người dùng», «Hồ sơ», «Thu hồi», «Plugin → Plugin đã cài») viết theo bản dịch tiếng Việt thường gặp, kèm tên tiếng Anh trong ngoặc như README đang làm. Tôi không mở trang quản trị thật để kiểm từng chữ. Nút tạo người dùng ghi chung «nút thêm người dùng ở cuối trang» để khỏi sai chữ.
- **Tên mục «AI Abilities» trong menu SiteSEO** lấy theo phiếu và ghi chú T-059. Changelog wordpress.org ghi «AI Abilities Pro feature»; website đang có SiteSEO Pro và đã ghi được. README không nói cần bản Pro.
- **Đường dẫn (slug) dán vào đâu.** README bảo dán vào ô đường dẫn (slug) **của bài** trong trang sửa bài WordPress, vì app không gửi slug và slug là của bài viết. Câu chú thích trên app (`write.py:2243-2246`) lại nói chung «dán vào hộp SiteSEO của bài nháp» cho cả ba khung. Xem «Đề xuất» 1.
- Mục 8 sửa theo T-084 (đã gộp trên nhánh này, `ba12878`). `origin/main` lúc tôi `fetch` (`4671104`) chưa có T-084: câu cũ «⚠️ không thấy trên máy này» mới khớp `main` đó. Nên gộp nhánh này sau, hoặc cùng lúc với T-084.
- Đánh số lại mục 10 → 13. Trong code và `run.bat` / `run.command` không chỗ nào gọi số mục README (chỉ gọi tên mục «Kết nối WordPress», «Xử lý sự cố», còn nguyên). Báo cáo, phiếu cũ trong `docs/team/` còn ghi «mục 10» theo số cũ: để nguyên vì là hồ sơ lịch sử.

## Đề xuất (ngoài phạm vi, Chỉ Huy giao nếu thấy cần)

1. **Họa Sĩ:** câu chú thích khung «Chép sang SiteSEO» (`write.py:2243-2246`) nói «dán vào hộp SiteSEO của bài nháp» cho cả ba khung. Nên tách: tiêu đề, mô tả dán vào hộp SiteSEO; đường dẫn dán vào ô đường dẫn của bài (trừ khi hộp SiteSEO có ô slug, việc này cần xem trên trang quản trị thật).
2. **`.env.example`** (tôi không được sửa):
   - dòng `WORDPRESS_USERNAME` (`:23`) nên thêm «(không phải tên đặt cho Application Password); nên là tài khoản vai Biên tập viên riêng»;
   - dòng `WORDPRESS_APP_PASSWORD` (`:25-26`) nên thêm «tạo trên chính tài khoản ở WORDPRESS_USERNAME».

   Đây đúng là chỗ đã nhầm khi thử thật 27/10.

## Câu hỏi cho chủ dự án

Không có.

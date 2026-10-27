# T-041 · Bước 4 "SEO" của Soạn bài chạy thật

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`), Thợ Máy hỗ trợ phần lưu nháp |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-036, T-037, T-038, T-039 đã gộp (T-040 nên gộp trước) |
| Trạng thái | Soi Lỗi kiểm cả phiếu |

## Mục tiêu

Thay phần demo bước 4 trong trang Soạn bài bằng chức năng thật. **Giữ bố cục chủ dự án đã duyệt.**

## Phạm vi

- **Được sửa:**
  - `app/views/write.py`: chỉ bước SEO và trạng thái liên quan;
  - `seo_app/demo.py`: xóa `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` khi không còn dùng;
  - `seo_app/storage/drafts.py`: thêm trường meta/link/schema vào nháp, giữ `extra="forbid"`. Phần này Thợ Máy làm trước, cùng nhánh;
  - test giao diện.
- **Không được sửa:** logic `seo_app/onpage/**` (báo Thợ Máy nếu cần đổi).

## Yêu cầu (tóm tắt)

1. **Meta:**
   - ô title/description có nút 🔄 viết lại riêng từng ô, quay lại bản trước được;
   - đếm ký tự NFC; màu Nên / Cảnh báo / Chặn;
   - xem trước kiểu Google (`ui.serp_preview` đã có, kiểm lại escape).
2. **Slug:** gợi ý, sửa được, kiểm trùng.
3. **Liên kết nội bộ:** bảng tick "Dùng", "Cụm từ trong bài", "Trỏ tới bài"; nút "Tải lại danh sách bài".
4. **Schema:** xem FAQPage đã dựng (nếu bài có mục Hỏi đáp), hiện chữ thuần, không HTML.
5. Lưu mọi lựa chọn vào nháp cục bộ (tự lưu như bước 1–3).
6. Bỏ nhãn "Bản demo" của bước này. `tests/test_app_pages.py` vẫn qua.

## Yêu cầu bảo mật riêng

U1 (chữ từ site và AI phải escape; không `unsafe_allow_html` với chữ chưa escape), U2, D3.

## Tiêu chí xong

- [ ] Bước SEO chạy thật, giữ bố cục
- [ ] Test giao diện bằng `AppTest`, hàm giả
- [ ] Báo cáo `docs/team/reports/T-041-hoa-si.md` (và `T-041-tho-may.md` cho phần nháp), kèm hướng dẫn chủ dự án tự mở app xem

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (U1).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-041 Lưu SEO vào nháp"** rồi **"Họa Sĩ · T-041 Bước SEO thật"**, nhánh `team/T-041`.
- 2026-10-16: chủ dự án chưa trả lời câu 1, 2 (cách ghi SEO lên SiteSEO). Bước SEO phải chạy trọn vẹn **không cần** ghi lên site:
  - có nút chép (copy) title, description, slug để chủ dự án dán tay vào hộp SiteSEO;
  - không hiện lỗi hay nút hỏng khi chưa cấu hình ghi SEO;
  - không có kết nối WordPress thì danh sách bài (liên kết nội bộ, kiểm trùng) báo nhẹ "chưa kết nối", các phần còn lại vẫn dùng được.
- 2026-10-16 (Chỉ Huy B), điều kiện của Soi Lỗi T-038, `docs/team/reports/T-038-soi-loi.md`: phần Thợ Máy của phiếu này **được sửa thêm `seo_app/onpage/schema.py`** trước khi Họa Sĩ làm giao diện.
  - SL-T038-2 (Trung bình): bỏ Markdown nội dòng (`**đậm**`, link, `` `mã` ``) ở **cả** bài lẫn câu trả lời trước khi so nguyên văn. JSON-LD không được mang dấu Markdown.
  - SL-T038-1 (Thấp): chặn ký tự surrogate lẻ (loại Cs).
  - Bỏ `xfail` tương ứng trong `tests/test_soi_loi_t038.py`.
- 2026-10-16: **Điều kiện bắt buộc của Lá Chắn T-038** (`docs/team/reports/T-038-la-chan.md`). Phải xong trước khi giao diện dùng `json_ld`, hạn chót trước khi hết Giai đoạn 4:
  1. `schema.py` chặn thêm ký tự loại Cs, Co, Cn.
  2. Bỏ Markdown nội dòng ở cả bài lẫn câu trả lời:
     - link chỉ giữ chữ, không giữ địa chỉ, nên `[x](javascript:…)` không còn trong JSON-LD;
     - ảnh: bỏ, hoặc chỉ giữ alt;
     - **không bao giờ** đổi sang HTML.
  3. Giao diện hiện `json_ld` bằng `st.code`, không dùng `unsafe_allow_html`.
- 2026-10-17 (Chỉ Huy A): **Điều kiện của Lá Chắn T-036** (`docs/team/reports/T-036-la-chan.md`, ĐẠT CÓ ĐIỀU KIỆN). Phải xong trước khi T-042 gửi meta lên site, hạn chót cuối Giai đoạn 4. Phiếu này **được thêm ngoại lệ**: phần Thợ Máy được sửa `seo_app/onpage/meta.py` cho các điểm 1–3.
  1. LC-T036-1: `normalize_meta` (`meta.py:74-85`) bỏ hoặc Chặn ký tự Cc (NUL, ESC…), Cs, Co, Cn, ở cả chữ AI lẫn chữ người dùng gõ; có test.
  2. SL-T036-10: chỉ loại trừ đúng chữ "xu hướng", không nới các đơn vị khác.
  3. SL-T036-12: giao diện không gọi `has_link` / `mentions_price` với chữ chưa cắt độ dài, hoặc cắt độ dài ngay trong hai hàm này.
  4. SL-T036-11, LC-T036-2 (bộ dò link sót vài dạng tên miền lạ): ghi nhận, không bắt buộc.
  5. Phần Họa Sĩ: hiện `FieldCheck.messages` (có tên bài lấy từ site) bằng chữ thuần hoặc đã escape, không dùng `unsafe_allow_html`.
- 2026-10-17 (Chỉ Huy A): **Điều kiện của Lá Chắn T-037** cho mọi phiếu dùng dữ liệu bài đã đăng (`site_index`):
  - Link ghép vào `href` phải qua `html.escape(quote=True)` và qua bộ lọc HTML (`security.md` mục 2.3).
  - Tiêu đề, meta lấy từ site hiện trên giao diện phải là chữ thuần hoặc đã escape; đưa vào prompt AI thì phải nằm trong khung dữ liệu.
  - Khi `truncated` bật thì không được kết luận "link hỏng"; chuẩn hóa link trước khi so bằng `by_link()`.
  - Nếu phiếu này nối `get()` vào giao diện trước T-042 thì phải sửa SL-T037-5 (file cache bận làm treo khoảng 14 giây).
- 2026-10-17 (Chỉ Huy A): **Phần giao diện cho T-042** (Thợ Máy T-042 không được sửa `app/**`, đề xuất giao Họa Sĩ trong phiếu này):
  - Công tắc "Ghi SEO lên website" (mặc định **tắt**). Sau khi tạo nháp thì gọi `WordPressClient.set_seo_meta`, hiện `result.message` bằng widget chữ thường.
  - Trang Kết nối WordPress hiện thêm `info.siteseo_status` ("SiteSEO: ghi được / chưa bật").
  - Tiêu đề truyền vào `set_seo_meta` phải gắn sẵn đuôi " | Pro-Metal" bằng `with_brand` (client không tự gắn).
- 2026-10-19 (Chỉ Huy A): **Điều kiện của Lá Chắn T-042** (`docs/team/reports/T-042-la-chan.md`) cho phần nối `set_seo_meta` / `set_featured_image` vào app:
  - `write_seo` mặc định **tắt**, công tắc trong app.
  - Không tự nạp id vào `_created_post_ids`. Muốn giữ client qua các lần bấm thì giữ cả client trong `st.session_state`, **không** dùng `st.cache_resource`.
  - Hiện câu báo bằng widget chữ thường hoặc `escape_markdown`.
  - LC-T042-2: ghi qua Abilities xong thì hỏi lại trạng thái bài; không còn nháp thì báo người dùng.
- 2026-10-22 (Chỉ Huy B): **Điều kiện Lá Chắn T-039** (điều kiện 2): (a) `[tasks.links]` trong `config/ai.toml` **không có** `web_search`; hàm gọi AI chỉ `_run("links", prompts.internal_links_prompt(...), LinkSuggestions)` rồi `check_suggestions`. (b) Nháp lưu `InternalLink` (`asdict` khi ghi, `InternalLink(**d)` trong `try` khi đọc, sai khuôn thì bỏ); chèn luôn qua `apply_links`/`place_links`. (c) U1: tiêu đề bài trên site, `LinkReview.rejected`, `LinkPlacement.skipped`, `LinkCheck.message`, `LinkCheck.href` hiện bằng chữ thường hoặc đã escape, không đưa chữ thô vào `st.markdown`/`st.write`/`unsafe_allow_html`; có test. (d) Nếu phiếu này sửa `links.py`: sửa LC-T039-2 (`place_links` giữ `[` `]` đã vô hiệu, gỡ 3 `xfail` của `tests/test_la_chan_t039.py`).
- 2026-10-23 18:01 (Chỉ Huy B): T-040 thêm mục `[meta]` vào `config/content.toml` (ngưỡng độ dài, đuôi thương hiệu, cụm nên tránh) nhưng **phần mềm chưa đọc mục này**: Thợ Máy nối ở phần logic của T-041 (hoặc phiếu riêng trước T-041).
- 2026-10-24 09:11 (Chỉ Huy B): thêm **SL-T040-1 phần code** (Soi Lỗi T-040): title AI dài đúng 49 ký tự vừa không gắn được đuôi « | Pro-Metal» vừa bị bộ kiểm ghi «hơi ngắn» (`seo_app/onpage/meta.py`, `check_title`/`accept_ai_title`); lời dặn T-040 đã tránh khoảng này. Thợ Máy quyết cách sửa (ví dụ khoảng «vừa» tính cả đuôi), gỡ `xfail` `tests/test_soi_loi_t040.py::test_sl_t040_1_title_of_49_chars_is_not_short` (sửa `reason` cũ nếu cần, Chỉ Huy duyệt). Cùng lúc nối `[meta]` của `config/content.toml` (ghi chú trước); khi nối `[meta].avoid` phải bỏ từ khóa ra trước khi dò (Đề xuất 2 Soi Lỗi T-040).
- 2026-10-24 10:27 (Chỉ Huy B): thêm **LC-T040-1** (Lá Chắn T-040, Thấp): `mentions_price` (`seo_app/onpage/meta.py:493-498`) không xóa từ khóa; tìm `_PRICE` ở mọi vị trí, chỉ bỏ qua chỗ khớp nằm trọn trong từ khóa; giữ cắt độ dài trước (SL-T036-12); gỡ 4 `xfail` `tests/test_la_chan_t040.py`; nếu nối `[meta].avoid` thì dò cụm nên tránh cùng cách. Hạn: trước khi bước SEO trên giao diện hiện gợi ý meta.
- 2026-10-26 10:02 (Chỉ Huy B): **chủ dự án duyệt giao** (T-036 → T-040 đã gộp). Nhánh `team/T-041` từ `main`, worktree `wt-T-041`. **Phần Thợ Máy trước** (phiên "Thợ Máy · T-041 Lưu SEO vào nháp"): `seo_app/storage/drafts.py` (trường SEO), `seo_app/onpage/schema.py` (LC-T038 đk 1–2, SL-T038-1, -2), `seo_app/onpage/meta.py` (LC-T036-1, SL-T036-10, -12, LC-T040-1, SL-T040-1, nối `[meta]`), `seo_app/storage/site_index.py` (SL-T037-5 vì giao diện sẽ gọi `get()`), `links.py` chỉ nếu cần (LC-T039-2). Phần Họa Sĩ (`write.py`) làm **sau khi T-086 gộp** (cùng sửa `write.py`, `drafts.py`). Chạy tới 4 phiên con cùng lúc (T-086 Soi Lỗi, T-085, T-087 Lá Chắn).
- 2026-10-26 11:07 (Chỉ Huy B): **Thợ Máy xong phần logic** (`c059b41`): mọi điều kiện logic trong ghi chú (LC-T038 đk 1–2, LC-T036-1, SL-T036-10, -12, LC-T040-1, SL-T040-1, `[meta]` + `find_avoided`, SL-T037-5, LC-T039 đk 2a, 2b); trường SEO trong nháp (nháp cũ mở được); danh sách hàm cho Họa Sĩ trong báo cáo; 37 file test liên quan 2.969 qua. **Chỉ Huy duyệt** 3 chỗ sửa test cũ (mục «Test cũ đã đổi») và phần thêm `ContentWriter.internal_links` (`39f2178`). Giao **Soi Lỗi rút gọn phần logic** ngay (song song); Họa Sĩ nối giao diện sau khi T-086 gộp. LC-T039-2 để phiếu bộ dựng HTML GĐ5 (không sửa `links.py`).
- 2026-10-26 13:53 (Chỉ Huy B): **Soi Lỗi phần logic ĐẠT CÓ ĐIỀU KIỆN** (`85b06b6`): 7 Thấp; SL-T041-1, -2, -4 phải sửa trước khi Họa Sĩ nối giao diện. Giao **Thợ Máy lượt 2**: bắt buộc -1, -2, -4; nên làm cùng -3, -5, -6, -7 nếu gọn (khỏi mở phiếu mới). Sau đó gộp `main` (có T-086) vào nhánh rồi giao Họa Sĩ.
- 2026-10-26 15:19 (Chỉ Huy B): **Thợ Máy lượt 2 xong** (`eac0431`): sửa đủ SL-T041-1 → -7, 4/6 góp ý; Chỉ Huy duyệt 4 test ngưỡng cũ thêm `suffix=""` và `TASK_EXAMPLES` (`registry.py`). Gộp `main` (có T-056, T-085, T-086, T-087) vào nhánh (`13a554c`, không xung đột; 434 test liên quan qua). Giao **Họa Sĩ** (phiên Họa Sĩ T-056) nối giao diện bước SEO.
- 2026-10-26 19:22 (Chỉ Huy B): **Họa Sĩ xong giao diện bước SEO** (`a88c6e5`, 23 test giao diện). Họa Sĩ phát hiện **lỗi lùi** do `94ba458` (lượt 1 Thợ Máy): `normalize_meta` bỏ ký tự Cc nên `_seo_text` (`client.py`) kiểm ký tự điều khiển trên chữ đã chuẩn hóa, chữ SEO có ký tự điều khiển bị lặng lẽ sửa thay vì bị chặn (15 test T-042 hỏng). Giao **Thợ Máy lượt 3**; **Chỉ Huy duyệt mở phạm vi** đúng chỗ kiểm trong `_seo_text` của `seo_app/wordpress/client.py` (tối thiểu); rà các chỗ khác dùng `normalize_meta` trước khi kiểm. Dòng `info.siteseo_status` trên trang Kết nối WordPress để sau lượt 3 (cùng phiếu). Sau đó Soi Lỗi cả phiếu, rồi Lá Chắn.
- 2026-10-26 19:55 (Chỉ Huy B): **Thợ Máy lượt 3 xong** (`cfdd56e`): `_seo_text` kiểm ký tự điều khiển trên chữ gốc (`1637957`, chỉ trong `_seo_text`); `check_title`/`check_description` chặn chữ có ký tự điều khiển hay ký tự vô hình lạ, `DraftMetaVersions` không còn lặng lẽ bỏ, gợi ý AI có ký tự lạ bị bỏ, đuôi thương hiệu lạ về mặc định (`ee1de90`); câu schema `MSG_NO_FAQ_QUESTION` (góp ý số 4 Họa Sĩ). Chỉ sửa test của chính Thợ Máy đã ghi hành vi «lặng lẽ bỏ» cũ (Chỉ Huy duyệt); test Soi Lỗi, T-042, Họa Sĩ giữ nguyên. 61 file test liên quan 8.078 qua, 0 hỏng. Giao **Họa Sĩ lượt 2** (Chỉ Huy duyệt mở `app/views/wordpress.py`): dòng `info.siteseo_status` trên trang Kết nối WordPress (yêu cầu phiếu), kiểm giao diện với chữ bị chặn. Sau đó Soi Lỗi cả phiếu.
- 2026-10-27 08:16 (Chỉ Huy B): **Họa Sĩ lượt 2 xong** (`433c533`): trang Kết nối WordPress hiện «SiteSEO: ghi được / chưa bật / chưa dò được»; chữ bị chặn sau lượt 3 có 9 test `AppTest` (không phải sửa code giao diện); câu liên kết nội bộ khi nút mờ nói đúng lý do; 11 file 497 qua. Còn «một ca chưa xử lý»: từ khóa chính có ký tự điều khiển làm client từ chối cả lệnh ghi SEO (an toàn, hiếm). Giao **Soi Lỗi rút gọn cả phiếu** (phiên Soi Lỗi T-040, người đã kiểm phần logic).

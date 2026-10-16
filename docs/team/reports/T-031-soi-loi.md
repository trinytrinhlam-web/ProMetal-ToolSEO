# Báo cáo T-031 · Soi Lỗi kiểm thử: địa chỉ trần và email không thành link

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-031](../tickets/T-031-dia-chi-tran-thanh-link.md) (kèm ghi chú mở rộng phạm vi 2026-10-16) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT** (có 1 lỗi Thấp ngoài phạm vi, xem SL-T031-1) |

## Tóm tắt (cho chủ dự án)

Tôi tự dựng lại đúng bộ hiển thị Markdown mà Streamlit dùng rồi thử hơn 18 000 mẫu chữ. Không mẫu nào thành link bấm được trên các trang có chữ AI. Người đọc vẫn thấy nguyên địa chỉ. Ô «Sửa trực tiếp» không hiện ký tự lạ. Gợi ý văn phong, viết lại và quay lại bản trước vẫn chạy đúng. Chữ thường như `TP.HCM`, `v.v.` hay số thập phân không bị đổi. Tôi tìm thêm một lỗi nhỏ ngoài phạm vi phiếu: trang Kết nối WordPress hiện tên website và tên tài khoản lấy từ WordPress mà không lọc (SL-T031-1, mức Thấp).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t031.py` | Mới: 654 ca (653 qua, 1 xfail strict `SL-T031-1`) |
| `docs/team/reports/T-031-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest
4087 passed, 4 skipped, 14 xfailed, 1 warning in 195.03s (0:03:15)

$ uv run pytest tests/test_soi_loi_t031.py
653 passed, 1 xfailed in 20.38s

$ uv run ruff check .
All checks passed!
```

4 ca skip và 13 ca xfail là của trước, không liên quan T-031. Ca xfail thứ 14 là `SL-T031-1`.

### 1. Kiểm bằng bộ hiển thị thật (độc lập, không chép script của Thợ Máy)

- **Bộ hiển thị:** `react-markdown` 9.1.0 + `remark-gfm` 4.0.1 (micromark-extension-gfm-autolink-literal 2.1.0, mdast-util-gfm-autolink-literal 2.0.1). Dựng từ **thẻ HTML `<a>` thật** sau khi hiện (`renderToStaticMarkup`). Thợ Máy thì dựng cây mdast. Chỗ nào app dùng `unsafe_allow_html=True` (thân bài qua `ui.highlight`, tiêu đề H2) thì thêm `rehype-raw`, giống Streamlit. Cài tạm bằng npm trong scratchpad, **không** thêm vào dự án.
- **Đối chiếu với Streamlit 1.65:** hai biểu thức nhận link trong `StreamlitMarkdown.abRW1By9.js` giống hệt bản trong mdast-util-gfm-autolink-literal 2.0.1.
- **82 mẫu viết tay × 9 đường hiện chữ = 738 ca → 0 link trên đường thật.**
  - Mẫu: `https://`, `http://`, `HTTPS`, `hTtP`, `www.`, `WWW.`, `wWw.`, email (cả `-`, `_`, `+`, `.` trước `@`), `mailto:`, `xmpp:`, dấu câu cuối, ngoặc, ngoặc kép, Unicode, punycode, `\.`, `\:`, `\/`, `\@`, `\\`, `&#64;`, `&#x40;`, `&#X40;`, `&commat;`, `&#46;`, `&period;`, `&#58;`, `&#47;`, `&sol;`, `&#119;`, thiếu `;`, 7–9 chữ số, `&#99999999;`, `&#x110000;`, `&#0;`, `&amp;www.`, chữ toàn khổ (`ｗｗｗ．`, `：／／`, `＠`), U+200B và U+2060 có sẵn, soft hyphen, trong đậm, nghiêng, code, danh sách, trích dẫn, bảng, tiêu đề, thẻ HTML chen giữa địa chỉ, tên mô hình chen giữa địa chỉ.
  - Đường: `clean_ai_text`, `clean_ai_line`, ô sửa rồi Lưu, trích câu (`quote_ai_text`), thân bài (`ui.highlight` + HTML), tiêu đề H2 (`html.escape`), `markdown_link` (url hỏng), `:gray[…]`, thử mù (che tên sau `clean_ai_text`).
  - Ca duy nhất ra link là `escape_link_syntax("<https://evil.com>")` gọi trên chữ **thô, chưa bỏ thẻ**. Ca này Thợ Máy đã nêu. Tôi kiểm thêm: hai chỗ app gọi `escape_link_syntax` mà không qua `strip_tags` là ô sửa khi Lưu và tiêu đề dàn ý. Ở ô sửa, thân bài hiện qua `ui.highlight` nên `<` thành `&lt;` (đã chạy thật, 0 link). Tiêu đề dàn ý chỉ hiện trong ô nhập, và `write()` lọc lại bằng `clean_ai_line`. Cả hai không ra link. Kể cả khi ra link, đích cũng hỏng (`https:/%E2%80%8B/…`).
- **Ngẫu nhiên:** 3 000 chuỗi × 5 đường, cộng 2 708 lần `apply_flag` cắt và nối ở vị trí ngẫu nhiên. **17 708 ca, 0 link.**
- **Người đọc vẫn thấy nguyên chữ:** chữ hiện ra (bỏ thẻ, bỏ U+200B) giống hệt bản gốc.
- **Mã HTML sinh nhiều ký tự:** không mã nào có `/`, `.`, `@`, `:`, `w` ở sau ký tự đầu (đã duyệt cả `html.entities.html5`).

### 2. Không hỏng chức năng

- **Ô sửa:** không hiện U+200B, trừ khi AI tự viết ra. Không hiện dấu `\` do app thêm (`test_edit_box_shows_no_zero_width_and_round_trips`, `test_edit_box_rewrite_and_undo_keep_text`).
- **`escape(unescape(t)) == t`:** đúng trên 30 000 chuỗi ngẫu nhiên. Các chuỗi đó có `[`, `]`, `:`, `>`, `-`, mã HTML, `\` và U+200B có sẵn. `escape` chạy lại không đổi gì.
- **Gợi ý văn phong** cho câu có địa chỉ vẫn hiện và Áp dụng được, dù AI chép câu có hay không có ký tự ngắt. Đã thử cả trên trang thật bằng AppTest:
  - lượt tự sửa: `auto_fixed == 1`;
  - lượt người dùng bấm Áp dụng: câu có `&#64;` và `\.`.
- **Fuzz `clean_flags`:** 20 000 câu cắt theo ranh giới từ, 0 câu bị bỏ sót.
- **Viết lại, quay lại:** viết lại phần đó rồi bấm ↶ thì về đúng bản cũ. Lưu từ ô sửa mà không đổi gì thì chữ giữ nguyên từng ký tự.
- **Chữ tiếng Việt thường không bị chèn:** `TP.HCM`, `v.v.`, `1.500.000`, `3.14`, `8:30/17:30`, `15/10/2026`, `Dr.www`, `@suachuacuasat`, `0905.123.456`… Slug không đổi (`slugify` bỏ U+200B).

### 3. Bảy chỗ Thợ Máy sửa trong test cũ

Tôi đọc từng dòng diff: **không có kiểm tra bảo mật nào bị nới.**

- Mọi khẳng định cũ vẫn còn. Chỉ chuỗi mong đợi đổi sang dạng có U+200B, và đó là chuỗi đầy đủ, không phải kiểm lỏng hơn.
- Hai chỗ có thêm khẳng định mới, `gfm_autolinks(...) == []`.
- `test_escape_only_adds_backslashes`: chỗ trước là `replace("\\", "")`, nay là `replace("\\", "").replace("​", "")`. Đây là đúng tính chất mới. Ngay sau đó vẫn so cả chuỗi kết quả.
- `test_poison_is_disabled_in_every_ai_field` (T-021) không sửa và nay xanh.

### 4. Rà `app/**`: chữ ngoài hiện bằng Markdown không qua `escape_link_syntax` / `escape_markdown`

| Chỗ | Chữ | Nguồn | Thành link? |
|---|---|---|---|
| `app/views/wordpress.py:41` `st.success(... {info.site_name} ({info.site_url}))` | tên website, địa chỉ website | WordPress trả về | **Có** (`www.`, email, cả link `[..](..)`), xem **SL-T031-1** |
| `app/views/wordpress.py:42` `st.markdown(... {info.user_name} ... {roles})` | tên tài khoản, vai trò | WordPress | **Có**, SL-T031-1 |
| `app/views/wordpress.py:119` `st.success(... {post.title})` | tiêu đề bài vừa tạo | WordPress trả lại chữ người dùng gõ | Có (chữ của chính người dùng) |
| `app/views/wordpress.py:121` `st.write(... {media.source_url})` | địa chỉ ảnh vừa tải | WordPress | Có, nhưng là địa chỉ site của mình, có chủ đích |
| `app/views/write.py:855` `ui.page_header(... keyword())` | từ khóa người dùng gõ | người dùng | Không. Nằm trong khối HTML `<p>`, Markdown không xử lý bên trong |
| `app/views/settings.py:246, 295` | tên mô hình trong `config/ai.toml` / người dùng gõ | người dùng | `246` nằm trong `` `…` ``: không. `295` có thể (chữ của người dùng) |
| `app/views/write.py:325, 863` `st.warning(str(exc))` (DraftError) | câu lỗi cố định + tên file | app | Không thấy chữ ngoài |
| `app/views/home.py`, `plan.py`, phần demo của `write.py` | dữ liệu mẫu `seo_app/demo.py` | app | Không phải chữ ngoài |

Mọi chỗ hiện **chữ AI** đều đã qua `clean_ai_text`, `clean_ai_line` hoặc `markdown_link`. Tôi đã thử trên trang thật bằng AppTest, đi qua bước nghiên cứu, bài viết, rà soát và Áp dụng: mọi `st.markdown` và `st.caption` đều 0 link. Các chỗ đó là:
- nghiên cứu: ý định, dạng bài, đối thủ (`covers`/`missing`), góc mới, câu hỏi;
- tiêu đề bài, tiêu đề mục, chỗ cần ảnh;
- thân bài, câu bị tô, lý do, câu thay thế, nhận xét;
- thử mù;
- nháp nạp lại (`seo_app/storage/drafts.py` lọc lại khi đọc).

## Lỗi tìm thấy

### SL-T031-1 · Mức Thấp · Trang WordPress hiện chữ từ WordPress bằng Markdown không escape

- **Tái hiện:** WordPress trả `site_name = "Ghé www.evil.example"` và `user_name = "a@evil.example"`. Bấm «Kiểm tra kết nối».
- **Mong đợi:** chữ hiện nguyên văn, không bấm được.
- **Thực tế:** thành link (`test_wordpress_site_name_is_not_a_link`, xfail strict). Dạng `[bấm](https://…)` trong tên website cũng thành link.
- **Đánh giá:** nguồn là website của chính chủ dự án, và đây là trang thử của Giai đoạn 1. Rủi ro thấp. Không thuộc phạm vi T-031 (phiếu không cho sửa `app/**`).
- **Gợi ý sửa:** bọc bằng `escape_markdown` (nay đã có `break_autolinks`), hoặc hiện bằng `st.text`.

### Ghi nhận khác (không phải lỗi)

- `break_autolinks` chèn U+200B trước `@` cả khi không phải email, ví dụ `e-mail@`. Ký tự này không hiện ra nên vô hại.
- `clean_flags` bỏ gợi ý khi AI cắt câu **giữa** một địa chỉ hay **giữa** một mã HTML, ví dụ câu bắt đầu bằng `ww.x.vn` hoặc `#64;`. AI thực tế trích nguyên câu nên chuyện này hiếm. Hậu quả chỉ là mất một gợi ý, không có hại về bảo mật.
- Dấu `<https://…>` để nguyên chỉ an toàn nhờ `strip_tags` hoặc `ui.highlight` chạy trước. Nếu sau này có đường hiện chữ mới gọi `escape_link_syntax` mà không qua hai bước đó, dạng này sẽ thành link (đích hỏng). Nên giữ nguyên tắc: chữ ngoài luôn qua `clean_ai_text`.

### 5. Tốc độ

`tests/timing.py`, 16 mẫu × 3 hàm: `break_autolinks`, `unbreak_autolinks`, `escape_link_syntax`. Mẫu gồm `www`, `a@`, `:/`, `&#64;`, `&`, `&#`, `&a`, `\`, `\.`, U+200B lặp lại. Thêm 3 mẫu dài: `&#111…`, `&aaa…;@`, `www…w.`. **Tất cả tuyến tính.**

### Kiểm test có bắt được lỗi không (đột biến code)

Tôi cố tình làm hỏng code ở 6 kiểu, rồi xem bộ test mới có đỏ không:
- tắt `break_autolinks`;
- `www` chỉ nhận chữ thường;
- bỏ giải mã `&…;`;
- bỏ giải mã `\`;
- thu hẹp tập ký tự trước `@`;
- bỏ `unbreak` trong ô sửa.

Cả 6 đều làm bộ test đỏ. Kiểu thu hẹp tập ký tự trước `@` lúc đầu lọt, nên tôi đã thêm ca `a-@`, `a_@`, `a+@`, `a.@`. Đã chạy thật: không lọc thì 4 dạng này thành link.

## Đối chiếu yêu cầu kiểm thử

- [x] Kiểm bằng bộ hiển thị thật, độc lập: đủ các ca ở mục 1
- [x] Không hỏng chức năng: ô sửa, round-trip, `apply_flag`, viết lại, quay lại, chữ có dấu chấm
- [x] 7 chỗ sửa test cũ: không nới
- [x] Rà `app/**`: bảng mục 4, 1 lỗi Thấp (SL-T031-1)
- [x] Tốc độ tuyến tính
- [x] Test ở `tests/test_soi_loi_t031.py`, xfail strict `SL-T031-1`, không gọi mạng, không thêm thư viện
- [x] `uv run pytest`, `uv run ruff check .` sạch (Linux; Windows chưa chạy được trên cloud)

## Rủi ro và điểm cần chú ý

- **Streamlit nâng phiên bản:** `test_streamlit_autolink_rules_unchanged` đọc file JS của Streamlit đang cài. Nếu biểu thức nhận link đổi thì test này đỏ, khi đó phải kiểm lại T-031. Không được sửa chuỗi mong đợi cho xanh khi chưa kiểm.
- **Bộ đối chiếu trong pytest** chỉ chép lại cách nhận link, nó không phải remark-gfm thật. Phép thử bằng bộ hiển thị thật nằm ngoài pytest (dùng node). Đồng ý với Thợ Máy: nên đưa script node vào `scripts/` để các phiếu sau chạy lại được.
- **Chép chữ từ vùng xem bài sẽ dính U+200B** (Thợ Máy đã nêu). Giai đoạn 5 phải gỡ ký tự này trước khi gửi WordPress.

## Đề xuất

- Lập phiếu nhỏ cho SL-T031-1 (Họa Sĩ, `app/views/wordpress.py`). Có thể gộp vào lúc làm lại trang WordPress ở Giai đoạn 5.
- Giữ ghi chú Giai đoạn 5 của Thợ Máy:
  - gỡ ký tự ngắt trước khi chuyển sang HTML;
  - tắt autolink, hoặc liệt kê mọi `href` trên màn hình xác nhận.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-044 · Kiểm thử rút gọn: chữ lấy từ WordPress hiện an toàn

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-044](../tickets/T-044-ten-site-tu-wordpress-hien-an-toan.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Tôi đã cố làm cho chữ từ WordPress (tên site, tên tài khoản, vai trò, tiêu đề bài, địa chỉ ảnh, câu lỗi) và tên mô hình ở trang thử mù thành link bấm được hoặc thẻ HTML. **Không cách nào thành công**: mọi chữ đều hiện là chữ thường. Có 2 lỗi nhỏ mới do cách sửa gây ra: nếu website trả về dữ liệu sai kiểu (địa chỉ site là số, địa chỉ ảnh rỗng kiểu `null`), trang báo lỗi kỹ thuật thay vì hiện chữ như trước. Website WordPress bình thường không trả về như vậy, nên đây là lỗi mức Thấp, không chặn gộp.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t044.py` | Mới: 49 ca qua + 3 ca `xfail(strict)` ghi lại SL-T044-1, SL-T044-2 |
| `docs/team/reports/T-044-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `conftest.py`, `timing.py`.

## Bằng chứng

```
$ git pull            (wt-T-044, team/T-044, HEAD 7d799fc)
Already up to date.

$ uv run pytest tests/test_soi_loi_t044.py -q
49 passed, 3 xfailed in 17.62s

$ uv run pytest tests/test_soi_loi_t044.py -q --runxfail -k "non_string or null_source"
3 failed   (AttributeError: 'int' / 'list' / 'NoneType' object has no attribute 'split')

$ uv run pytest            (Windows 11, toàn repo, commit 3617509)
5374 passed, 10 skipped, 33 xfailed, 1 warning in 474.10s (0:07:54)

$ uv run ruff check .
All checks passed!
```

`tests/test_app_pages.py` nằm trong lượt chạy toàn bộ ở trên.

### Đã thử (đều không ra link / HTML)

Bộ dò của tôi giải mã Markdown **một lượt** như CommonMark (dùng `markdown_decode` và `gfm_autolinks` của `test_sanitize_autolink.py`), rồi tìm: `<` chưa escape (thẻ HTML, `<https://…>`, `<javascript:…>`), `]` chưa escape đứng trước `(` / `[` / `:` (link, ảnh, link tham chiếu, dòng khai báo), địa chỉ trần, `www.`, email theo remark-gfm.

1. **`escape_markdown` với chữ khó** (`test_escape_markdown_tricky_text_is_plain`, 25 ca): `&#119;ww.`, `w&#119;w.`, `&#x77;&#x77;&#x77;&#x2e;`, `https&#58;//`, `https:/&#47;`, `ban&#64;`, `&commat;`, `&colon;&sol;&sol;`, `WWW&period;`, chữ toàn khổ `ｗｗｗ．`/`ｈｔｔｐｓ：／／`, U+200B có sẵn ở nhiều chỗ, `WwW.`/`HTTPS://`, `<https://…>`, `<mailto:…>`, `<javascript:alert(1)>`, dòng khai báo `[x]: https://…` nhiều dòng (cả `\r` đứng riêng), `[x](<https://…>)`, ảnh Markdown, `\[x\](…)` có sẵn dấu `\`, `https:\/\/`, `mailto:`/`xmpp:`, chỉ thị riêng của Streamlit (`:red[…]`, `:material/home:`, `$…$`, `~~`), `<a>`/`<img onerror>`. Thực thể số bị vô hiệu vì `#` được escape (người đọc thấy nguyên `&#119;`); thực thể có tên (`&commat;`) được giải mã khi hiện nhưng vẫn bị chèn ký tự ngắt nên không thành link.
2. **Qua client WordPress thật** (`tests/fake_wordpress.py`, đi qua `_request`, `_json`, `_plain`, `_error_from`; không chỉ thay phương thức client):
   - `test_real_client_hostile_connection_info_is_plain`: tên site và tên tài khoản mã hóa hai lần (`&amp;#119;ww.`, `&amp;commat;`, `&lt;a href=…&gt;`, `&lt;https://…&gt;`), link Markdown, chữ toàn khổ, U+200B, dòng khai báo sau `\n`; `home` = `https://evil.example/<b>x</b>?a=[1](2)`; vai trò `<b>quản trị</b>`, `www.evil.example`, `[x](y)`.
   - `test_real_client_multiline_wordpress_error_is_plain` × 3 nút: lỗi 400 có `message` nhiều dòng (`\n\n`, `\r\n`, `\r`) chứa dòng khai báo link, link tham chiếu, `&lt;https://…&gt;`, thẻ `<a>`, `www.`, email. Câu lỗi hiện một dòng, không link.
3. **Dòng địa chỉ ảnh sau khi tải lên (`wordpress.py:134`)**, trước đây chỉ kiểm bằng đọc code: `test_uploaded_image_url_line_is_plain` × 6 giả `st.file_uploader` (thay hàm của module `streamlit` bằng hàm trả về file giả), WordPress giả trả `source_url` độc (địa chỉ trần, `www.`, link Markdown, `<https://…>`, `<img onerror>`, email). Dòng hiện đúng chữ, không link; bài gửi đi vẫn `draft`, có `featured_media`.
4. `test_upload_error_with_hostile_filename_is_plain` × 2: tên file người dùng chọn (`www.evil.example.exe`, `[x](…)ban@evil.example.png` rỗng) chép vào câu lỗi, không link, không gọi WordPress.
5. **Thử mù**:
   - `test_blind_real_run_reveal_errors_are_plain` × 4: đi qua `run_blind_test` **thật** (chỉ giả hãng AI, câu lỗi chép lại tên mô hình như `gemini_provider`), tên `www.evil.example`, `https://evil.example/m1`, `ban@evil.example`, `mailto:a@b.co`. Cả 2 câu lỗi sau khi bấm «hiện tên» không link.
   - `test_blind_error_escape_fuzz_restricted_alphabet`: 3.000 tên ngẫu nhiên (hạt giống 44) từ bảng chữ được phép, trộn mảnh `https://`, `www.`, `WWW.`, `@`, `mailto:`, `xmpp:`, `//`. Không tên nào ra link; chữ hiện ra không đổi.
   - `test_blind_leftover_formatting_is_not_link_or_html`: `_abc1_`, `__abc1__`, `:smile:`, `:material/home:`, `a_b_1`. Xác nhận nhận định của Họa Sĩ: chỉ còn định dạng (nghiêng, đậm, biểu tượng), không link, không HTML, vì bảng chữ tên mô hình không có `< > [ ] ( ) & \`.
   - `test_model_name_alphabet_matches_blind_test`: chốt bảng chữ `[A-Za-z0-9._:/@-]`; ai nới bảng chữ thì test này đỏ, nhắc xét lại.

## Lỗi tìm thấy

### SL-T044-1 · Thấp · `home` không phải chuỗi làm trang Kết nối WordPress hỏng

- **Tái hiện:** WordPress giả trả `GET /wp-json/` có `"home": 123` (hoặc một danh sách), bấm **Kiểm tra kết nối**. Test: `test_non_string_site_url_does_not_crash_page[so]`, `[danh-sach]`.
- **Mong đợi:** trang vẫn hiện (như `main` trước T-044: f-string in ra `(123)`).
- **Thực tế:** `AttributeError: 'int' object has no attribute 'split'` ở `escape_markdown(info.site_url)` (`app/views/wordpress.py:53`). Nguyên nhân: `client.check_connection` lấy `site_url = root.get("home") or …` không ép kiểu, còn `escape_markdown` chỉ nhận `str`.
- **Hướng sửa gợi ý (Họa Sĩ):** `escape_markdown(str(info.site_url))`, hoặc Thợ Máy ép `str` trong client.

### SL-T044-2 · Thấp · `source_url` null làm trang hỏng sau khi đã tạo bài nháp

- **Tái hiện:** chọn ảnh, WordPress giả trả `POST /wp/v2/media` = `{"id": 9, "source_url": null}`, bấm **Tạo bài nháp**. Test: `test_null_source_url_does_not_crash_page`.
- **Mong đợi:** hiện «Đã tạo bài nháp …» và nút mở bài (như `main`: `st.write` in `None`).
- **Thực tế:** bài nháp đã tạo, hiện thông báo thành công, rồi `AttributeError: 'NoneType' object has no attribute 'split'` ở `wordpress.py:134`; nút «Mở bài trong trang quản trị WordPress» không hiện. Nguyên nhân: `Media.source_url = media.get("source_url", "")` có thể là `None`.
- **Hướng sửa gợi ý:** `escape_markdown(media.source_url or "")` (hoặc ép kiểu trong client), chỉ hiện dòng khi có địa chỉ.

Cả hai đều cần máy chủ trả dữ liệu sai kiểu (WordPress chuẩn trả chuỗi), không lộ bí mật, không làm bài bị đăng. Đã ghi bằng `xfail(strict=True)`: sửa xong thì bỏ dấu `xfail`.

## Đối chiếu tiêu chí xong

- [x] Không chữ nào từ WordPress thành link hay HTML trên trang, có test (Họa Sĩ + `tests/test_soi_loi_t044.py` mục 1–4)
- [x] Câu lỗi thử mù có tên mô hình kiểu địa chỉ không thành link (mục 5, gồm đường `run_blind_test` thật)
- [x] Dòng địa chỉ ảnh (`wordpress.py:134`) có test chạy qua
- [x] `tests/test_app_pages.py` qua; `uv run pytest` 0 hỏng, 0 lỗi trên Windows; `uv run ruff check .` sạch
- [ ] Trang không hỏng với dữ liệu WordPress sai kiểu (SL-T044-1, SL-T044-2, mức Thấp)

## Rủi ro và điểm cần chú ý

- **Bộ dò trong `tests/test_app_t044_safe_text.py` báo nhầm** với thực thể số: hàm `decode` bỏ `\` rồi mới giải mã `&…;` (hai lượt), nên coi `&\#119;ww\.x` (kết quả đúng của `escape_markdown`) là `www.x`. CommonMark giải mã một lượt nên đó là chữ thường. Hiện không ca nào của Họa Sĩ chạm trường hợp này; ai thêm ca có `&#…;` vào file đó sẽ thấy đỏ oan. Bộ dò của tôi dùng `markdown_decode` một lượt.
- **`escape_link_syntax` không chặn link kiểu `<scheme:…>`**: ký tự ngắt rộng 0 vẫn hợp lệ bên trong autolink CommonMark, nên `<https://x.y>` qua hàm này vẫn là link. Ở T-044 không với tới được (tên mô hình không có `<`, câu lỗi AI là câu cố định), nhưng nếu sau này dùng hàm này cho chữ có `<` mà không qua `clean_ai_text`, phải xét lại. Báo để Lá Chắn biết.
- Thực thể có tên còn sót sau `_plain` (ví dụ site tên `&amp;commat;`) hiện ra dạng đã giải mã (`@`), khác nguyên văn một chút; vô hại.
- Tôi chưa xem trên trình duyệt thật, chỉ kiểm bằng `AppTest` cộng bộ dò. Bộ dò mô phỏng CommonMark/remark-gfm, không phải chính bộ hiển thị của Streamlit.

## Đề xuất

- Họa Sĩ sửa SL-T044-1, SL-T044-2 (hai dòng, `str(...)` / `or ""`), bỏ `xfail` hai test tương ứng. Có thể làm ngay trên nhánh này hoặc gộp vào phiếu dọn lỗi sau; không chặn gộp.
- Lá Chắn (U1): xem ghi chú `<scheme:…>` của `escape_link_syntax` ở trên.

## Câu hỏi cho chủ dự án

Không có.

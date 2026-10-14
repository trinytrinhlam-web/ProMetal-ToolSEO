# Báo cáo T-004 + T-005 · Kiểm thử bộ lọc HTML/link và hiển thị bài AI

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-004](../tickets/T-004-loc-html-ket-qua-ai.md), [T-005](../tickets/T-005-escape-hien-thi-bai.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. **T-005: xác nhận. T-004: chưa xác nhận** (còn lỗi #1, #2 mức Trung bình) |

## Tóm tắt (cho chủ dự án)

Tôi thử khoảng 100 cách cài mã độc để lách bộ lọc. **Không cách nào làm mã JavaScript chạy được**, cả trong app lẫn trong HTML gửi WordPress. Trang Soạn bài (T-005) đứng vững hoàn toàn. Còn hai chỗ hở ở bộ lọc chữ AI (T-004): AI vẫn có thể giấu một **link ra trang lạ** trong bài bằng vài cách viết Markdown ít gặp. Ngoài ra có một lỗi làm **mất nửa sau bài** khi HTML có thẻ `<embed>`/`<meta>`/`<input>`. Cả ba lỗi đã có test đánh dấu "lỗi đã biết", sửa xong test sẽ tự báo.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_sanitize_bypass.py` (mới) | 106 trường hợp: 92 qua (bộ lọc chặn được), 14 `xfail(strict=True)` (lách được, lỗi #1–#3) |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest            # trước khi thêm test của tôi
252 passed, 9 xfailed

$ uv run pytest            # sau khi thêm tests/test_sanitize_bypass.py
344 passed, 23 xfailed in 16.88s

$ uv run ruff check .
All checks passed!
```

14 `xfailed` mới đều trong `tests/test_sanitize_bypass.py`; 9 cái cũ là lỗi T-002 không liên quan.

## Lỗi tìm thấy

### #1 (Trung bình, T-004) Link Markdown hợp lệ nhưng regex không nhận ra → link ẩn lọt qua `clean_ai_text`

Nguyên nhân: `seo_app/sanitize.py:39-41`. `_MD_URL` chỉ cho **một** cặp ngoặc trong địa chỉ và cấm xuống dòng; nhãn `[^\]\n]*` cấm `]` và xuống dòng. Theo CommonMark (Streamlit và các bộ chuyển Markdown → HTML làm theo) các dạng sau vẫn là link:

| Tái hiện: `clean_ai_text(...)` | Mong đợi | Thực tế |
|---|---|---|
| `[x](https://evil.example/a(b(c)))` | `x` | giữ nguyên, vẫn là link |
| `[a [b] c](https://evil.example)` | `a [b] c` | giữ nguyên |
| `[a\]b](https://evil.example)` | `a]b` | giữ nguyên |
| `[Xem bảng\ngiá](https://evil.example)` | chữ | giữ nguyên |
| `[x](\nhttps://evil.example)` | `x` | giữ nguyên |
| `[x](https://evil.example\n"t")` | `x` | giữ nguyên |
| `[x](javascript:a(b(c)))` | `x` | giữ nguyên |

### #2 (Trung bình, T-004) Khai báo link kiểu tham chiếu, địa chỉ ở dòng sau

Nguyên nhân: `seo_app/sanitize.py:43`, `_MD_LINK_DEF` đòi địa chỉ (`\S+`) nằm cùng dòng với `[nhãn]:`. CommonMark cho phép địa chỉ ở dòng kế tiếp.

- Tái hiện: `clean_ai_text("[x][r]\n\n[r]:\n  https://evil.example")`, tương tự với ảnh `![a][i]\n\n[i]:\n https://evil.example/t.png`.
- Mong đợi: không còn địa chỉ. Thực tế: giữ nguyên, `[x]` hiển thị thành link, ảnh ngoài được tải.

Tác hại của #1, #2: vi phạm security.md 2.3 ("không tự chèn link lạ"): chữ hiện ra bình thường, địa chỉ bị giấu. Không thành XSS trong app: theo test `test_competitor_javascript_link_is_not_rendered` của T-005, Streamlit tự bỏ `javascript:`. Khi Giai đoạn 5 chuyển Markdown sang HTML để gửi WordPress, link `https://` lạ sẽ qua cả `sanitize_html` (vì nó cho phép https) và lên website.
Gợi ý sửa (Thợ Máy quyết): thay vì đoán link bằng regex, chặn theo dấu hiệu: bỏ mọi `](`, `]:` và `<`…`>`, hoặc escape `[`/`]` trong chữ AI; nếu còn `](`/`]:` sau khi lọc thì coi là đáng ngờ.
Test: `test_clean_ai_text_drops_commonmark_link_variants` (9 trường hợp `xfail`).

### #3 (Thấp, chức năng, T-004) Thẻ rỗng nguy hiểm làm mất toàn bộ phần sau của bài

Nguyên nhân: `seo_app/sanitize.py:90` + `:154`. `embed`, `input`, `link`, `meta`, `base` nằm trong `DANGEROUS_TAGS` nhưng không có trong `VOID_TAGS`. Bộ lọc vì thế chờ một thẻ đóng không bao giờ có và bỏ hết phần còn lại.

- Tái hiện: `sanitize_html('<p>Mở bài</p><embed src="x.swf"><p>Nội dung phía sau</p>')`
- Mong đợi: `<p>Mở bài</p><p>Nội dung phía sau</p>`. Thực tế: `<p>Mở bài</p>`.
- Không có lỗ hổng bảo mật, nhưng bài gửi lên WordPress bị cụt mà không ai báo. Thợ Máy đã ghi rủi ro "thẻ không đóng", nhưng các thẻ này **theo chuẩn không bao giờ có thẻ đóng**, nên đây là lỗi chứ không phải giới hạn. Sửa: thêm chúng vào một tập "void" riêng khi kiểm tra ở `:154`.
- Test: `test_dangerous_void_tag_does_not_swallow_rest_of_article` (5 trường hợp `xfail`).

## Đã thử và bộ lọc chặn được (test qua)

- **`sanitize_html` / `is_safe_url`** (44 mẫu): chữ hoa/thường lẫn lộn; thuộc tính không ngoặc; `<img/src=x/onerror=…>`; mã thực thể thập phân/hex, có hoặc không `;`, số 0 đệm, `&Tab;` `&NewLine;` `&colon;`; ký tự điều khiển `\x00` `\x01` `&#14;` và U+2028 trong `javascript:`; `vbscript:`, `data:`, `feed:javascript:`; `srcdoc`; `<svg>`, `<math xlink:href>`; `<a>` lồng; comment điều kiện `<!--[if IE]>`; CDATA; thẻ không đóng; `< script>`; `<scr<script>ipt>`; `srcset` độc; `style`; `<noscript>` / `<style>` / `<title>` / `<xmp>` chứa thẻ; `background`, `formaction`; dấu nháy đã mã hóa trong `title`. Lý do bộ lọc vững: HTML ra được **dựng lại từ đầu** (chỉ thẻ/thuộc tính cho phép, giá trị luôn escape), không phải xóa bớt từ chuỗi gốc.
- **`clean_ai_text`** (22 mẫu): thẻ chữ hoa, thẻ thiếu `>`, `alt=">"`, autolink `<javascript:…>`, thẻ xuống dòng giữa tên và thuộc tính, comment điều kiện, CDATA, thẻ lồng; link/ảnh Markdown thường, có tiêu đề, `<…>`, ngoặc escape, link lồng; khai báo tham chiếu cùng dòng, thụt lề, tab.
- **`ui.highlight`** (9 mẫu, có cả câu được tô chứa mã độc): kết quả chỉ có thẻ `<mark class="tone|missing">`.
- **Không làm hỏng nội dung bình thường**: bài HTML tiếng Việt (tiêu đề, đoạn, danh sách, `ol start`, link https có `&`, ảnh, chú thích) đi qua `sanitize_html` **không đổi một ký tự**; Markdown tiếng Việt (đậm, nghiêng, danh sách, `<`/`>` có dấu cách, `[cần bổ sung: …]`) qua `clean_ai_text` không đổi.

## Đối chiếu tiêu chí xong

- [x] Thử lách theo phiếu T-004 (mục "Kiểm thử và kiểm định"), có test cho mọi cách đã thử.
- [x] T-005: `highlight` không lách được (`test_highlight_only_emits_mark_tags`) → **xác nhận**.
- [ ] T-004: còn lỗi #1, #2 (Trung bình) và #3 (Thấp) → **chưa xác nhận**, đề nghị giao lại Thợ Máy.
- [x] `uv run pytest`, `uv run ruff check .` sạch.

## Rủi ro và điểm cần chú ý (mức Thấp, không viết test xfail)

- `is_safe_url` chặn `\\evil.example` (lời chú thích `sanitize.py:114`) nhưng cho qua `/\evil.example` và `//evil.example`; trình duyệt hiểu cả hai là `https://evil.example`. Không nguy hiểm hơn link https thường (vốn được cho phép), chỉ là kiểm tra không nhất quán.
- `ui.highlight`: nếu câu cần tô trùng một phần mã thực thể (`amp`, `lt`), thẻ `<mark>` chèn vào giữa `&amp;` và chữ hiện sai (ví dụ `&amp;` thay vì `&`). Chỉ là hiển thị; câu tô thật là cả câu nên gần như không xảy ra.
- `ui.highlight` (suy luận, chưa thử trên trình duyệt): chữ trong `` `…` `` có `<`/`>` có thể hiện thành `&lt;`/`&gt;`, vì Markdown không giải mã thực thể trong đoạn code.
- `clean_ai_text` để lại địa chỉ viết trần (`https://…`, `www.…`) và Streamlit/GFM tự biến thành link bấm được. Thợ Máy đã nói rõ là cố ý vì người dùng nhìn thấy địa chỉ.
- `[x](https://evil.example "a)b")` → còn sót `xb")` (không còn link, chỉ thừa chữ).

## Đề xuất

- Chỉ Huy giao lại Thợ Máy sửa #1, #2, #3 trong `seo_app/sanitize.py`, rồi gỡ các dấu `xfail` tương ứng trong `tests/test_sanitize_bypass.py` (test sẽ báo XPASS khi sửa xong).
- Khi làm Giai đoạn 5 (gửi bài lên WordPress): chuyển Markdown sang HTML bằng code có escape, sau đó vẫn chạy `sanitize_html`. Nên cân nhắc chỉ cho phép link do app gắn (link nội bộ), bỏ `href` ra ngoài nếu người dùng chưa duyệt.

## Câu hỏi cho chủ dự án

Không có.

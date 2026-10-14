# Báo cáo T-004 · Lọc HTML và link trong kết quả AI, bộ lọc trước khi gửi WordPress

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-004](../tickets/T-004-loc-html-ket-qua-ai.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Thêm hai lớp lọc. Lớp 1: ngay khi AI trả bài về (mở bài, từng mục, phần viết lại, câu AI đề xuất thay thế), app bỏ hết mã HTML và bỏ địa chỉ của các link AI tự chèn, chỉ giữ chữ. Nhờ vậy dù trang đối thủ có cài lệnh để AI chèn mã độc, mã đó không chạy trong app. Lớp 2: ngay trước khi gửi bài sang WordPress, nội dung đi qua bộ lọc chỉ giữ các thẻ HTML an toàn (đoạn văn, tiêu đề, danh sách, bảng, ảnh, link http/https), bỏ `<script>`, `<iframe>`, `<form>`, `<style>`…, bỏ thuộc tính `on…=`, `style` và link `javascript:`/`data:`. Người dùng không thấy gì khác, trừ việc link do AI tự chèn sẽ chỉ còn chữ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/sanitize.py` (mới) | `clean_ai_text` / `strip_tags` / `strip_markdown_links` cho chữ AI; `sanitize_html` (danh sách cho phép, dùng `html.parser` của Python) và `is_safe_url` cho HTML gửi WordPress |
| `seo_app/content/workflow.py` | Lọc tại ranh giới nhận kết quả AI: `clean_draft` (`:28`, gọi ở `:138`), `clean_review` (`:40`, gọi ở `:145`), `rewrite_section` (`:177`) |
| `seo_app/wordpress/client.py` | `create_draft` lọc `content` và `excerpt` bằng `sanitize_html`, bỏ thẻ trong `title` (`:214-227`) |
| `tests/test_sanitize.py` (mới) | 58 trường hợp: 13 kiểu chèn mã (lồng thẻ, thẻ không đóng, chữ hoa, comment, svg, form, style…), 9 kiểu lách link `javascript:` (tab, mã thực thể `&#106;`, `data:`, `vbscript:`, `\\`), giữ nguyên bài bình thường, ranh giới AI (viết, viết lại, rà soát, tự sửa), client WordPress |
| `tests/test_content_edge_cases.py` | Gỡ `xfail` của `test_html_in_ai_article_is_not_rendered_as_html` |
| `tests/test_safety.py` | Gỡ `xfail` của `test_html_sent_to_wordpress_is_sanitized` |

Không sửa `app/`, `seo_app/ui.py`. Không thêm thư viện.

## Bằng chứng

```
$ uv run pytest
252 passed, 9 xfailed in 17.80s

$ uv run ruff check .
All checks passed!

$ uv run pytest tests/test_safety.py tests/test_content_edge_cases.py -k "html_in_ai or html_sent or highlight_escapes"
9 passed, 60 deselected in 2.83s
```

9 test `xfail` còn lại là lỗi khác của T-002 (#2, #4, #5, #6, #7, #8), không thuộc phiếu này.

**Ghi chú về T-005 (Họa Sĩ, chạy song song):** trong thư mục làm việc, `seo_app/ui.py`, `tests/test_ui_escape.py` (mới) và việc gỡ `xfail` của `test_highlight_escapes_ai_text` trong `tests/test_safety.py` là thay đổi của T-005, không phải của tôi. Kết quả pytest ở trên đã gồm cả thay đổi đó.

## Đối chiếu tiêu chí xong

- [x] `test_html_in_ai_article_is_not_rendered_as_html` qua (`tests/test_content_edge_cases.py:401`): nhờ lọc ở ranh giới AI, đứng được cả khi chưa có T-005.
- [x] `test_html_sent_to_wordpress_is_sanitized` qua (`tests/test_safety.py:166`, 4 trường hợp).
- [x] `test_highlight_escapes_ai_text` qua (`tests/test_safety.py:177`). Test này kiểm tra `ui.highlight`, thuộc T-005; dấu `xfail` do T-005 gỡ.
- [x] Test cho cả hai chỗ với `<script>`, `<img onerror>`, `javascript:`, `<iframe>` (`tests/test_sanitize.py`).
- [x] `uv run pytest`, `uv run ruff check .` sạch.
- [x] Báo cáo này.

Yêu cầu bảo mật: W3 (lọc trong `create_draft`), U1 (chữ AI không còn thẻ trước khi tới chỗ hiển thị; escape khi hiển thị là T-005), A2 (kết quả AI được kiểm tra nội dung, không chỉ kiểu dữ liệu).

## Rủi ro và điểm cần chú ý

- **Link do AI chèn bị bỏ địa chỉ, chỉ giữ chữ** (`[bảng giá](https://...)` thành `bảng giá`). Tôi chọn "bỏ" thay vì "đánh dấu" vì đơn giản và không thể lách. Địa chỉ viết trần trong câu (`https://...`) vẫn giữ và người dùng nhìn thấy. Link nội bộ sau này (Giai đoạn 4) phải do code gắn **sau** bước lọc này.
- **Bộ lọc WordPress bỏ comment HTML**, nên mã khối Gutenberg (`<!-- wp:paragraph -->`) sẽ mất. WordPress vẫn hiển thị bài như khối "Cổ điển". Nếu Giai đoạn 5 muốn gửi dạng khối thì phải sửa chỗ này.
- **Thẻ nguy hiểm không đóng** (ví dụ `<iframe>` thiếu `</iframe>`) làm mất toàn bộ phần sau nó. Chọn an toàn hơn đầy đủ.
- Bộ lọc giữ `class`, `id` và ảnh `src` http(s)/đường dẫn tương đối; bỏ `style`, `target`. Ảnh từ trang lạ vẫn được giữ trong HTML gửi lên (không chạy mã, nhưng là ảnh ngoài); việc kiểm soát ảnh thuộc Giai đoạn 3.
- Chữ có `<` ngay trước chữ cái (ví dụ `a<b`) được tách thành `a< b` để không bao giờ thành thẻ. Ít gặp trong bài tiếng Việt.
- Lớp lọc chỉ áp ở `ContentWriter`. Ô «Sửa trực tiếp» trong app (chữ người dùng gõ) **không** qua lớp này; chỗ đó được bảo vệ bởi escape khi hiển thị (T-005) và bộ lọc WordPress khi gửi.

## Đề xuất

- `Research` và `Outline` (tên/URL đối thủ, tiêu đề mục, ý chính) chưa được lọc HTML ở ranh giới AI; ngoài phạm vi phiếu. Tiêu đề mục đi vào bài nên nên lọc nốt (Thợ Máy, phiếu nhỏ).
- Soi Lỗi thử thêm các cách lách `sanitize_html` (theo phiếu). Lá Chắn kiểm định lại W3/U1/A2.
- Khi nối nút "Gửi sang WordPress" (Giai đoạn 5): bài Markdown phải chuyển sang HTML bằng code có escape, rồi mới vào `create_draft` (đã tự lọc).

## Câu hỏi cho chủ dự án

Không có.

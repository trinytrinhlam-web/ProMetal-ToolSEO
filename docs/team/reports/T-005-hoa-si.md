# Báo cáo T-005 · Hiển thị bài AI an toàn trên trang Soạn bài

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-005](../tickets/T-005-escape-hien-thi-bai.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trên trang Soạn bài, chữ trong bài (do AI viết hoặc do bạn tự sửa) giờ luôn hiện ra **dạng chữ**. Nếu trong bài có mã HTML hay JavaScript, bạn sẽ thấy nguyên văn mã đó trên màn hình chứ nó không chạy. Đây là lớp bảo vệ thứ hai: lớp thứ nhất là bộ lọc kết quả AI của Thợ Máy (T-004); nếu bộ lọc đó sót, trang vẫn an toàn. Giao diện không đổi: câu nghe máy móc vẫn tô vàng, chỗ thiếu số liệu vẫn tô đỏ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ui.py` | `highlight()` escape toàn bộ chữ và cả câu cần tô trước khi chèn `<mark>`; tô trong một lượt (không tô nhầm vào thẻ vừa chèn, bỏ qua chuỗi rỗng). `score_panel()` ép điểm về số nguyên 0–100 và escape tên tiêu chí trước khi chèn vào HTML. |
| `tests/test_safety.py` | Gỡ dấu `xfail` của `test_highlight_escapes_ai_text` (giờ đã qua). |
| `tests/test_ui_escape.py` | Mới, 20 test: escape câu được tô và chỗ thiếu số liệu với 6 kiểu mã độc; chỉ có thẻ `<mark>` trong kết quả; giữ nguyên ngoặc kép và Markdown tiếng Việt; không tô vào bên trong thẻ; bỏ qua chuỗi rỗng; `score_panel` chỉ chèn số; hai test mở trang Soạn bài thật (`AppTest`) **đi vòng qua bộ lọc T-004**: dán HTML vào ô «Sửa trực tiếp», và đặt thẳng chữ độc vào trạng thái phiên (tiêu đề bài, tiêu đề mục, thân mục). |

Không sửa `app/views/write.py` hay file nào khác trong `app/`: rà xong thì mọi chỗ `unsafe_allow_html=True` trong `app/` đều đã an toàn khi `highlight()` được sửa (bảng dưới). Không sửa `seo_app/content/`, `seo_app/wordpress/`. Không thêm thư viện.

## Bảng `unsafe_allow_html=True` (và `st.html`) trong `app/` và `seo_app/ui.py`

| Vị trí | Nội dung chèn vào HTML | Nguồn dữ liệu | Vì sao an toàn |
|---|---|---|---|
| `seo_app/ui.py:15` (`page_header`) | phụ đề trang | chuỗi cố định trong code từng trang | `html.escape(subtitle)`; khung `<p class="page-sub">` cố định |
| `app/views/home.py:45` | từ khóa, tiêu đề bài, chấm tiến độ | `demo.ARTICLES_IN_PROGRESS` (dữ liệu mẫu cố định) | `keyword`, `title` qua `html.escape`; `ui.progress_dots` chỉ chèn số nguyên do code tính |
| `app/views/home.py:54` | ghi chú, thời gian cập nhật | `demo.ARTICLES_IN_PROGRESS` | `note` qua `html.escape`; `updated` là chuỗi cố định trong `seo_app/demo.py` (vd. «hôm qua»). **Khi thay demo bằng dữ liệu thật phải escape thêm `updated`.** |
| `app/views/write.py:400` (`section_card`) | nhãn phần, số bản, tiêu đề mục | nhãn cố định; số do code đếm; tiêu đề mục từ AI | `label` là «Đoạn mở đầu»/«Mục»; số bản là `int`; tiêu đề qua `html.escape` (có test `test_unfiltered_ai_text_in_session_is_shown_as_text`) |
| `app/views/write.py:462` | **thân bài** + tô câu | AI viết, AI viết lại, người dùng sửa tay, câu thay thế AI đề xuất | **Đã sửa ở phiếu này:** `ui.highlight` escape chữ và câu được tô, chỉ thêm `<mark class="tone|missing">` cố định (`seo_app/ui.py:56-82`; test `test_highlight_escapes_ai_text`, `test_manual_edit_with_html_is_shown_as_text`, `test_unfiltered_ai_text_in_session_is_shown_as_text`) |
| `app/views/write.py:474` | bảng điểm văn phong | điểm do AI chấm, tên tiêu chí cố định (`SCORE_LABELS`) | `score_panel` ép điểm qua `int()` và kẹp 0–100, escape tên tiêu chí; nhãn «Tốt/Khá/Cần sửa» cố định (test `test_score_panel_*`) |
| `app/views/write.py:530` | tiêu đề bài | AI | `html.escape(S.article_title)` (có test vòng qua bộ lọc) |
| `app/views/write.py:567` | khung xem trước trên Google | meta title/description người dùng gõ, slug | `ui.serp_preview` escape cả 3 giá trị (`seo_app/ui.py:48-53`) |
| `app/main.py:64` (`st.html`) | CSS chung | file `app/assets/style.css` trong repo | file cố định do code viết sẵn, không có dữ liệu ngoài |

## Bằng chứng

```
$ uv run pytest
...
tests/test_ui_escape.py ....................                             [ 87%]
tests/test_wordpress_client.py .................................         [100%]
======================= 252 passed, 9 xfailed in 17.97s ========================

$ uv run ruff check .
All checks passed!
```

(Kết quả trên chạy cùng thư mục làm việc với thay đổi đang làm của T-004. 9 `xfailed` còn lại là lỗi khác trong T-002, không thuộc phiếu này.)

Đối chứng: tạm đặt lại `seo_app/ui.py` về bản gốc (`HEAD`) rồi chạy test → 22 test đỏ, gồm cả 2 test mở trang Soạn bài; đặt lại bản mới → xanh. Tức là test bắt được đúng lỗi #1, không phải qua nhờ bộ lọc T-004.

Tự kiểm tra trên giao diện: mở app (`run.bat` / `run.command`) → Soạn bài → viết bài → bấm «✏️ Sửa» ở một phần, dán `<b>thử</b> <img src=x onerror=alert(1)>`, bấm «Lưu». Mong đợi: thấy nguyên văn mã trên màn hình, không có chữ đậm, không hiện hộp thoại.

## Đối chiếu tiêu chí xong

- [x] `test_highlight_escapes_ai_text` chuyển thành `passed` (`tests/test_safety.py`, đã gỡ `xfail`)
- [x] Bảng liệt kê mọi `unsafe_allow_html=True` và lý do an toàn (mục trên)
- [x] Báo cáo `docs/team/reports/T-005-hoa-si.md`
- Ghi chú: `test_html_in_ai_article_is_not_rendered_as_html` hiện đã qua nhờ bộ lọc T-004 (Thợ Máy đã gỡ `xfail`). Riêng thay đổi của tôi **không** làm test đó qua, vì test đòi chữ `onerror` không có trong khối HTML, còn tôi giữ mã độc lại dưới dạng chữ đã escape (`&lt;img … onerror=…&gt;`) để người dùng nhìn thấy. Phần hiển thị được chứng minh riêng bằng hai test mới trong `tests/test_ui_escape.py`.

## Rủi ro và điểm cần chú ý

- **Link Markdown vẫn được dựng thành link**: escape chỉ chặn thẻ HTML, không chặn cú pháp Markdown `[chữ](địa chỉ)`. Streamlit tự bỏ `javascript:` trong link (test `test_competitor_javascript_link_is_not_rendered`), còn link `https://` lạ thì việc bỏ/đánh dấu thuộc bộ lọc T-004 (`clean_ai_text`). Nếu chữ đi vòng qua bộ lọc (ví dụ người dùng tự dán link vào ô Sửa), link vẫn hiện như link bình thường.
- **Trích dẫn Markdown (`> …`) không còn hiện dạng khối trích dẫn** vì `>` bị escape thành `&gt;`; chữ vẫn đọc được. Bài AI hiện ít dùng trích dẫn nên chấp nhận được (suy luận).
- `home.py:54` chèn `article["updated"]` chưa escape; hiện an toàn vì là dữ liệu mẫu cố định, phải escape khi trang Bài viết dùng dữ liệu thật.
- Test `AppTest` đọc thuộc tính nội bộ `proto.allow_html` của Streamlit (giống test của Soi Lỗi): nâng Streamlit có thể phải sửa test.

## Đề xuất

- Lá Chắn: kiểm định U1 với bảng trên; Soi Lỗi: thử thêm cách lách (Unicode, chữ đã escape sẵn như `&lt;script&gt;` — hiện sẽ hiện ra dạng `&lt;script&gt;` chứ không chạy).
- Khi thay demo trang Bài viết bằng dữ liệu WordPress thật: escape mọi trường (kể cả `updated`) và thêm test giống `test_unfiltered_ai_text_in_session_is_shown_as_text`.

## Câu hỏi cho chủ dự án

Không có.

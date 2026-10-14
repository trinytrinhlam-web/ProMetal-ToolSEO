# Báo cáo T-012 · Không hiện dấu `\` trong các ô người dùng sửa chữ

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-012](../tickets/T-012-an-dau-escape-o-o-sua.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Từ T-008, chữ AI được chèn thêm dấu `\` ở vài chỗ như `]\(` để AI không tạo được link. Phần bài hiển thị không thấy dấu này, nhưng trong các ô cho bạn sửa thì nó lộ ra. Giờ các ô đó hiện đúng chữ, không còn `\`. Khi bạn bấm Lưu hoặc Duyệt dàn ý, chữ được thêm `\` trở lại, nên dù bạn tự gõ link vào thì nó vẫn không thành link trong bài. Giao diện không đổi.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/sanitize.py` | **Chỉ thêm** hàm `unescape_link_syntax`, là nghịch đảo của `escape_link_syntax`. Hàm quét cùng cách và chỉ bỏ đúng dấu `\` nằm giữa `]` và `(`, `[`, hoặc `:` khi nhãn đứng đầu dòng. Không sửa hàm có sẵn. |
| `app/views/write.py` | Có 4 chỗ sửa. (1) `set_outline`: ô tiêu đề bài (H1) và ô tiêu đề từng mục nhận chữ đã bỏ `\`. (2) `current_outline`: escape lại tiêu đề bài và tiêu đề mục trước khi gửi AI viết. (3) Ô «Sửa trực tiếp» hiện `unescape_link_syntax(current_text(pid))`. (4) `save_manual`: lưu `escape_link_syntax(...)`. |
| `tests/test_edit_unescape.py` | Mới, 20 test (unit + AppTest), chi tiết dưới. |

Không sửa `config/`, không sửa test cũ, không thêm thư viện, không commit.

Các ô khác đã rà, không cần sửa:
- Ô «Hoặc ghi yêu cầu» (viết lại), các ô «Chất liệu thật» và ô từ khóa chỉ chứa chữ do người dùng gõ, không có chữ AI.
- Meta title/description còn là demo.
- Ý chính của mục dàn ý (`pts-`) và chú thích ảnh chỉ hiển thị bằng Markdown, không phải ô sửa, nên dấu `\` không lộ.

## Bằng chứng

```
$ uv run pytest tests/test_edit_unescape.py
20 passed in 3.10s

$ uv run pytest
FAILED tests/test_soi_loi_round3.py::test_normal_vietnamese_with_brackets_is_untouched[...]  (5 trường hợp)
================== 5 failed, 842 passed, 1 xfailed in 27.03s ===================

$ uv run ruff check .
All checks passed!
```

5 trường hợp đỏ là `test_normal_vietnamese_with_brackets_is_untouched` của Soi Lỗi. Test này đã đỏ từ trước do T-008 lần 2, Chỉ Huy đã báo trước, không thuộc phiếu này và tôi không sửa.

Đối chứng: đặt `app/views/write.py` về bản `HEAD` rồi chạy test thì 3 test AppTest đỏ (ô dàn ý, Duyệt dàn ý, ô Sửa trực tiếp). Đặt lại bản mới thì xanh hết.

Test mới:
- `test_unescape_is_inverse_of_escape` (9 trường hợp): bỏ escape rồi escape lại ra đúng chữ ban đầu, gồm `](`, `][`, `]:` đầu dòng, trong danh sách, trong trích dẫn, và `]:` giữa câu (giữ nguyên).
- `test_unescape_keeps_other_backslashes` (5 trường hợp): dấu `\` của chính người dùng (đường dẫn, `\[`, `\*`, `]:` giữa dòng) không bị bỏ.
- `test_unescape_on_clean_ai_text_round_trips` và `test_round_trip_on_random_strings` (20.000 chuỗi ngẫu nhiên, hạt giống cố định): luôn có `escape(unescape(t)) == t`. Nếu chữ gốc không tự có `]\` thì `unescape(escape(s)) == s`.
- AppTest:
  - `test_outline_boxes_show_text_without_escape_backslash`: ô H1 và ô tiêu đề mục không có `\`.
  - `test_outline_edits_are_escaped_again_when_approved`: gõ `Gọi [thợ](https://evil.example)` vào ô mục và `Bài [x][y]` vào ô H1 rồi Duyệt. Prompt gửi AI viết chỉ chứa bản đã escape.
  - `test_manual_edit_box_hides_backslash_and_save_escapes_again`: ô «Sửa trực tiếp» không có `\`. Lưu không sửa gì thì chữ y như trước. Gõ link rồi Lưu thì chữ lưu là `]\(`, `]\:`, và trang không có `](https`.
  - `test_draft_text_from_ai_is_unchanged_without_editing`.

Tự kiểm tra trên giao diện: mở app, vào Soạn bài, viết bài. Ở phần có chỗ `[cần bổ sung: …](…)`, bấm «✏️ Sửa»: trong ô không có dấu `\`. Gõ thêm `[bấm](https://example.com)` rồi bấm Lưu: trong bài hiện nguyên chữ `[bấm](https://example.com)`, không thành link.

## Đối chiếu tiêu chí xong

- [x] Ô sửa không hiện `\` do escape; lưu xong chữ lại được escape (`app/views/write.py`: `set_outline`, `current_outline`, `save_manual`, ô `manual-`)
- [x] Test AppTest cho ô «Sửa trực tiếp» và tiêu đề dàn ý (`tests/test_edit_unescape.py`)
- [x] Báo cáo này

## Rủi ro và điểm cần chú ý

- `escape_link_syntax` không phải đơn ánh. Nếu chữ gốc tự có `]\(` (hiếm, ví dụ người dùng cố ý gõ), ô sửa sẽ hiện `](`. Lưu lại vẫn ra đúng `]\(` như trước, nên không mất an toàn.
- `unescape_link_syntax` sao chép cách quét của `escape_link_syntax`. Nếu Thợ Máy đổi quy tắc trong `escape_link_syntax` (ví dụ thêm ký tự cần escape) thì phải sửa hàm ngược theo. Test ngẫu nhiên `test_round_trip_on_random_strings` sẽ báo đỏ nếu hai hàm lệch nhau với các ký tự trong bộ thử.
- Lưu ở ô «Sửa trực tiếp» chỉ escape cú pháp link, không lọc thẻ HTML. Phần hiển thị đã escape HTML (T-005). Còn khi gửi WordPress thì `sanitize_html` của Giai đoạn 5 phải lọc riêng.

## Đề xuất

- Thợ Máy: nên đặt `escape_link_syntax` và `unescape_link_syntax` cạnh nhau, và ghi chú trong docstring của `escape_link_syntax` rằng đổi một hàm thì phải đổi hàm kia.

## Câu hỏi cho chủ dự án

Không có.

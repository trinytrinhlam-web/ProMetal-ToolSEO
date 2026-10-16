# Báo cáo T-032 · Bộ lọc hồ sơ nhận cả nhãn gõ sai và nhãn trên tiêu đề

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Opus 5.5 |
| Phiếu | [T-032](../tickets/T-032-loc-ho-so-nhan-go-sai.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Khi anh sửa hồ sơ doanh nghiệp bằng Notepad mà gõ nhãn hơi sai (dính chữ `[CẦNXÁC NHẬN]`, quên bật bộ gõ `[CAN XAC NHAN]`, dùng ngoặc tròn `(CẦN XÁC NHẬN)`, gõ `[CHƯA XÁC NHẬN]`, hay nhãn bị xuống dòng giữa chừng) thì ý đó vẫn bị giấu khỏi AI. Gắn nhãn lên tiêu đề (`## 7. … [CẦN XÁC NHẬN]`) giờ giấu cả mục tới tiêu đề cùng cấp kế tiếp. Chỉ cần nhớ gõ **dấu mở ngoặc**: chữ "cần xác nhận" không có ngoặc là câu thường, AI vẫn thấy. Phần hồ sơ hiện tại AI thấy không đổi một ký tự nào.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/rules.py` | Mẫu nhãn mới `[\[(]\s*(?:CAN\|CHUA)\s*XAC\s*NHAN` so trên chữ đã bỏ dấu (`_tag_text`: `_visible` → NFD → bỏ dấu kết hợp → `Đ`→`D`); tìm nhãn một lần trên cả khối (các dòng nối bằng dấu cách) khi đóng khối; tiêu đề có nhãn giấu cả mục tới tiêu đề có số `#` ≤ (`hidden_level`); `_IGNORABLE_NOT_CF` → `IGNORABLE_NOT_CF`; `_visible` bỏ tham số `invisible_as` (mẫu mới cho phép thiếu dấu cách nên chỉ cần bỏ hẳn ký tự vô hình) |
| `seo_app/content/prompts.py` | Chỉ dòng nhập và chỗ dùng: `IGNORABLE_NOT_CF` |
| `config/business_profile.md` | Chỉ dòng ghi chú `>` đầu file: "TRỪ ba thứ", nhãn có dấu/không dấu, `[ ]`/`( )`, nhớ ngoặc mở, mục 3 về nhãn trên tiêu đề |
| `tests/test_profile_tag_t032.py` | Mới: 122 test (15 kiểu gõ sai × hoa/thường/Title, gõ trên Mac NFD, ký tự vô hình, khoảng trắng lạ; 6 câu thường không bị giấu; nhãn vắt hai dòng; nhãn trên `#`/`##`/`###`; tốc độ; hồ sơ thật) |
| `tests/test_profile_blocks.py` | Đổi theo hành vi mới: `test_glued_tag_and_invisible_separator_both_recognised` (thay `…still_not_recognised…`), `test_tag_in_heading_drops_whole_section` (thay `…drops_only_heading`), `test_blank_then_indented_after_heading_…` (thêm trường hợp tiêu đề sạch + đoạn thụt lề có nhãn; tiêu đề có nhãn giấu đoạn thụt lề) |
| `tests/test_soi_loi_t024.py` | `test_misspelled_tags_are_not_recognised` → `test_misspelled_tags_are_recognised` (4 trường hợp có ngoặc) + `test_tag_without_opening_bracket_is_not_recognised` (trường hợp `CẦN XÁC NHẬN` không ngoặc). Không bỏ trường hợp nào |

## Bằng chứng

```
$ uv run pytest
3238 passed, 4 skipped, 9 xfailed, 1 warning in 188.78s (0:03:08)

$ uv run ruff check .
All checks passed!
```

Lần chạy toàn bộ trước đó có 1 test hỏng: `tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail` (test chạy đua nhiều luồng của T-028, thuộc `seo_app/ai`, phiếu này không đụng tới). Chạy riêng 5 lần đều qua, chạy lại toàn bộ thì qua (kết quả trên). Có vẻ là test chập chờn; đề nghị Soi Lỗi xem ở phiếu khác.

Hồ sơ thật: lưu `confirmed_profile(...)` trước khi sửa, so `cmp` sau mỗi phần (regex, tiêu đề, hướng dẫn `>`): giống hệt (100 dòng). Test `test_real_profile_output_unchanged` so chuỗi kết quả mới với kết quả khi thay `_is_unconfirmed` bằng mẫu nhãn cũ.

## Đối chiếu tiêu chí xong

- [x] Kiểu gõ sai ở #1 bị lọc (`test_misspelled_tag_drops_item`, `…_typed_on_mac_nfd`, `…_with_invisible_chars`, `…_with_odd_spaces`, `test_tag_split_across_two_lines_of_one_item`), nhãn trên tiêu đề ở #2 (`test_tag_on_h2_hides_section_until_same_or_higher_heading`, `test_tag_on_h3_does_not_hide_following_h2`, …)
- [x] Câu thường có chữ "cần xác nhận" không bị lọc (`test_plain_sentence_with_words_is_kept`, `test_heading_with_plain_words_not_hidden`)
- [x] Phần hồ sơ thật AI thấy không đổi (`test_real_profile_output_unchanged` + `cmp`)
- [x] `uv run pytest`, `uv run ruff check .` sạch trên Linux
- [x] Báo cáo này
- [x] #4: `IGNORABLE_NOT_CF` công khai, hành vi không đổi
- [x] Tuyến tính: mỗi dòng xét một lần, mỗi khối tìm nhãn một lần trên chuỗi nối (`test_hidden_section_is_linear_on_large_input`, test tốc độ cũ T-015/T-024 vẫn qua)

## Rủi ro và điểm cần chú ý

- **Lọc thừa có chủ đích:** câu thường có ngoặc mở ngay trước cụm chữ, ví dụ `(cần xác nhận lịch với khách)`, giờ bị giấu cả ý. Bỏ dấu cũng làm `[CẠN XÁC NHẬN]` hay `(CĂN XÁC NHẬN` bị coi là nhãn. Đúng hướng "an toàn khi nghi ngờ" của phiếu; hồ sơ hiện tại không có câu nào như vậy.
- **Nhãn vắt qua hai ý khác nhau** (`- A [CẦN XÁC` rồi `- NHẬN]` ở gạch đầu dòng kế) không được nhận: phiếu chỉ yêu cầu trong cùng một ý. Đã chạy thử: cả hai ý đều tới AI (mỗi ý chỉ có nửa nhãn). Khó xảy ra khi gõ Notepad (phải tự gõ `- ` ở giữa nhãn).
- **Tiêu đề trong mục giấu:** chỉ tiêu đề không thụt lề mới kết thúc mục giấu (giữ quy tắc tiêu đề cũ). `  ## 8` thụt lề vẫn bị giấu theo (lọc thừa). Tiêu đề `##8` (thiếu dấu cách) và `＃＃` toàn khổ được tính là tiêu đề, kết thúc mục giấu.
- Soi Lỗi/Lá Chắn nên thử: nhãn trên tiêu đề kèm ghi chú `>` và dòng trống ở ranh giới mục; tiêu đề mang nhãn bên trong mục đang giấu (giữ cấp ngoài, đã có test); chữ cái Kirin/Hy Lạp trong nhãn (ngoài phạm vi, như biên bản T-022-024).

## Đề xuất

- Lỗi #3 (lọc thừa đoạn thụt lề kiểu Word) giữ nguyên theo phiếu, không đụng.
- `ruff format --check` báo 7 file ngoài phạm vi (ví dụ `seo_app/sanitize.py`) chưa định dạng; có từ trước, các file của phiếu này đã định dạng đúng.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (theo báo cáo Soi Lỗi `T-032-soi-loi.md`)

| Lỗi | Sửa | Test |
|---|---|---|
| SL-T032-1 (Trung bình) | Mục đang giấu chỉ kết thúc ở **tiêu đề thật** `_REAL_HEADING = #{1,6}(?:\s\|$)`, không thụt lề, cấp ≤. Dòng `#suachuacuasat`, `#1 khu vực` không còn làm thôi giấu | Bỏ `xfail` `test_hash_word_line_does_not_end_hidden_section`; thêm `test_hash_without_space_does_not_end_hidden_section` |
| SL-T032-2 (Thấp) | Dòng thụt lề trông như tiêu đề thật **và có nhãn** thì coi là tiêu đề: đóng khối trước rồi giấu cả mục. Đóng khối trước an toàn vì dòng bắt đầu bằng `#` không thể ghép thành nửa sau nhãn của khối trước (mẫu nhãn không cho `#` chen giữa). Tiêu đề thụt lề không nhãn vẫn là dòng tiếp của khối trước; tiêu đề thụt lề vẫn không kết thúc mục đang giấu (đã chấp nhận) | Bỏ `xfail` `test_indented_tagged_heading_hides_section`; thêm `test_indented_tagged_heading_hides_section_and_keeps_item_before` (giữ được `- ok` phía trước), `test_indented_heading_without_tag_still_belongs_to_block` |
| SL-T032-3 (Thấp) | Tiêu đề kết thúc bằng **nửa nhãn** (`_ends_with_partial_tag`: ngoặc mở rồi chỉ còn chữ là phần đầu của `CANXACNHAN`/`CHUAXACNHAN`, đã bỏ dấu; kể cả chỉ có `[`) thì chờ dòng kế (bỏ qua dòng `>`): ghép được nhãn thì giấu cả mục, kể cả dòng kế; không ghép được thì giữ tiêu đề y nguyên. Hết file mà còn nửa nhãn thì bỏ tiêu đề. Chỉ thêm một biến trạng thái, vẫn một lượt qua các dòng | Bỏ `xfail` `test_heading_tag_split_across_lines_hides_section`; thêm `test_heading_tag_split_across_lines` (4 kiểu), `…_with_note_between`, `test_heading_with_open_bracket_not_completed_is_kept` (`## Giá [`, `## Giá (tham khảo`…), `…_at_end_of_file_is_dropped`, `test_half_tag_heading_followed_by_heading` |

- **Đổi tham số `"##8. Quy tắc"`** của `test_tag_on_h2_hides_section_until_same_or_higher_heading`: theo hành vi mới `##8` (thiếu dấu cách) không kết thúc mục giấu, nên chuyển sang test riêng ghim việc nó bị giấu theo. Thay bằng hai tiêu đề thật khác: `#\tPhụ lục` (tab sau `#`) và `##` (tiêu đề rỗng).
- **Còn giữ (đã ghi, an toàn khi nghi ngờ):** dòng không thụt lề bắt đầu bằng `#` sát chữ mà **có nhãn** (`#hashtag [CẦN XÁC NHẬN]`, `##8 … [CẦN XÁC NHẬN]`) vẫn mở mục giấu với cấp bằng số `#`; với `#hashtag` là giấu tới tiêu đề thật `# ` kế tiếp (thường là hết file). Lọc thừa, không lọt.
- **Hồ sơ thật:** so `cmp` kết quả của `origin/main` (chạy trong worktree tạm) với nhánh: giống hệt, 100 dòng.

```
$ uv run pytest
3298 passed, 4 skipped, 9 xfailed, 1 warning in 139.77s (0:02:19)

$ uv run ruff check .
All checks passed!
```

Lần chạy toàn bộ trước đó có 1 test hỏng: `tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail` (test chạy đua nhiều luồng của T-028, thuộc `seo_app/ai`, phiếu này không đụng tới). Chạy riêng 5 lần đều qua, chạy lại toàn bộ thì qua (kết quả trên). Có vẻ là test chập chờn; đề nghị Soi Lỗi xem ở phiếu khác.

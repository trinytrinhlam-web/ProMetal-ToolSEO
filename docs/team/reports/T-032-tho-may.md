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
KQ_PYTEST

$ uv run ruff check .
All checks passed!
```

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

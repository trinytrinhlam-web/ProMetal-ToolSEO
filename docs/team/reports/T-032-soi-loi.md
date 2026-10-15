# Báo cáo T-032 · Kiểm thử bộ lọc hồ sơ nhận nhãn gõ sai và nhãn trên tiêu đề

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-032](../tickets/T-032-loc-ho-so-nhan-go-sai.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành |

## Kết luận: **ĐẠT CÓ ĐIỀU KIỆN**

Mọi tiêu chí của phiếu đạt: nhãn gõ sai bị lọc, câu thường "cần xác nhận" không ngoặc được giữ, nhãn vắt hai dòng của một ý bị lọc, nhãn trên tiêu đề giấu đúng tới tiêu đề cùng cấp hoặc cao hơn, phần hồ sơ thật AI thấy **giống hệt** `main`, bộ lọc vẫn tuyến tính.

Điều kiện: sửa **SL-T032-1** (Trung bình) trước khi gộp. Đây là chỗ để lọt ý chưa xác nhận tới AI, ngược hướng "an toàn khi nghi ngờ" của phiếu. SL-T032-2 và SL-T032-3 (Thấp) nên sửa cùng lúc vì cùng một chỗ code, nhưng không bắt buộc.

## Tóm tắt (cho chủ dự án)

Bộ lọc mới làm đúng việc: anh gõ nhãn hơi sai hay gắn nhãn lên tiêu đề thì phần đó vẫn không tới AI. Còn một lỗ nhỏ: trong mục đang giấu, nếu có dòng bắt đầu bằng dấu `#` sát chữ (ví dụ hashtag `#suachuacuasat`) thì bộ lọc tưởng đó là tiêu đề mới và **thôi giấu** từ dòng đó trở đi. Thợ Máy sửa xong lỗ này là gộp được.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t032.py` | Mới: 30 test qua + 7 test `xfail(strict=True)` cho 3 lỗi SL-T032-1..3 |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest
3268 passed, 4 skipped, 16 xfailed, 1 warning in 172.15s (0:02:52)

$ uv run ruff check .
All checks passed!
```

Hồ sơ thật so với `main` (lấy `seo_app/` và `config/` của `origin/main` bằng `git archive`, nạp hai bản `rules.py` cạnh nhau):

```
equal: True 4826 chars; old-func on new file equal: True
```

Tức là: bộ lọc mới trên hồ sơ mới cho đúng chuỗi như bộ lọc cũ trên hồ sơ cũ (4.826 ký tự), và chỉ dòng `>` của hồ sơ đổi.

## Đối chiếu tiêu chí phiếu

- [x] Nhãn gõ sai bị lọc, cả khi file lưu kiểu Notepad (BOM + CRLF + tab): `test_misspelled_tag_in_notepad_file`
- [x] Câu thường không ngoặc giữ lại, kể cả viết hoa, không dấu, có ngoặc ở chỗ khác trong câu (`[tham khảo] cần xác nhận`, `(sau 17h) cần xác nhận`), ngoặc kép «»: `test_plain_words_without_opening_bracket_kept`
- [x] Nhãn vắt hai dòng của một ý (thụt lề, không thụt lề, tab, ký tự vô hình, dấu cách không ngắt, ngoặc tròn cuối dòng): `test_tag_split_across_lines_of_one_item_notepad`
- [x] Tiêu đề có nhãn giấu qua `###`, `####`, dừng ở `##` hoặc `#`: `test_heading_tag_hides_until_same_or_higher_heading`, `test_heading_tag_stops_at_h1`
- [x] Hồ sơ thật: so chuỗi với `main` ở trên; test `test_real_profile_output_has_no_tag_and_only_file_lines`
- [x] Tuyến tính: `test_filter_scales_linearly` (tiêu đề giấu, nhãn vắt dòng, nhiều ngoặc mở, dòng `#chữ`), `test_one_huge_block_with_many_brackets_scales_linearly` (một khối lớn toàn `([` và `[CAN    XAC` không trọn)

Trường hợp xấu đã thử và **đạt**: NFD và dấu tổ hợp đặt sai chỗ, chữ và ngoặc toàn khổ, `＃＃` toàn khổ, ký tự vô hình giữa các dấu `#` và trong nhãn, `##7` sát chữ + CRLF, tiêu đề cấp 1 giấu tới hết file, tiêu đề có nhãn ở dòng cuối (có và không có xuống dòng cuối), lồng `##` → `###` → `##`, dòng `>` và dòng trống ở ranh giới mục giấu.

## Lỗi tìm được

### SL-T032-1 · Trung bình · Dòng bắt đầu bằng `#` sát chữ kết thúc mục đang giấu

- **Tái hiện:**
  ```
  ## 7. Chất liệu thật [CẦN XÁC NHẬN]
  - bí mật A
  #suachuacuasat #cuasat
  - bí mật B
  ## 8
  ```
  (hoặc dòng `#1 khu vực Thủ Đức`)
- **Mong đợi:** cả mục 7 bị giấu, `bí mật B` không tới AI.
- **Thực tế:** `#suachuacuasat …` được coi là tiêu đề cấp 1 (≤ 2) nên thôi giấu; AI thấy `#suachuacuasat #cuasat` và `- bí mật B`.
- **Nguyên nhân:** `rules.py` nhận tiêu đề bằng `stripped.startswith("#")`, nên `##8` (gõ thiếu dấu cách) được tính là tiêu đề (Thợ Máy chủ ý), nhưng hashtag cũng vậy. Markdown chỉ coi là tiêu đề khi sau `#` có dấu cách.
- **Đề xuất sửa:** khi đang giấu, chỉ thôi giấu ở tiêu đề "chắc chắn": `#{1,6}` rồi tới khoảng trắng hoặc hết dòng. `##8` sẽ bị giấu thừa (an toàn khi nghi ngờ). Cấu trúc khối ngoài mục giấu không cần đổi. Phải đổi tham số `"##8. Quy tắc"` của `test_profile_tag_t032.py::test_tag_on_h2_hides_section_until_same_or_higher_heading` (dòng 139), vì nó ghim `##8` kết thúc mục giấu.
- **Mức:** Trung bình, vì để lọt đúng thứ chủ dự án muốn giấu, không báo gì. Không phải lỗi lùi (trước T-032 các dòng dưới tiêu đề vốn không bị giấu).
- **Test:** `test_hash_word_line_does_not_end_hidden_section` (xfail).

### SL-T032-2 · Thấp · Tiêu đề có nhãn bị thụt lề không giấu cả mục

- **Tái hiện:** `- ok`, dòng trống, ` ## 7. Chất liệu thật [CẦN XÁC NHẬN]` (1 dấu cách đầu dòng, hoặc 3 dấu cách, tab, dấu cách không ngắt), `- bí mật A`.
- **Mong đợi:** cả mục 7 bị giấu (Markdown vẫn coi tiêu đề thụt 1–3 dấu cách là tiêu đề; người dùng lỡ gõ dấu cách đầu dòng thì vẫn nghĩ đó là tiêu đề).
- **Thực tế:** dòng tiêu đề thụt lề bị coi là dòng tiếp của khối trước, chỉ khối đó bị giấu (giấu thừa cả `- ok` khi có khối trước); `- bí mật A` tới AI.
- **Đề xuất sửa:** dòng thụt lề mà ký tự nhìn thấy đầu tiên là `#` và có nhãn thì cũng bật giấu mục (lấy số `#` từ `stripped`). Chỉ thêm chiều giấu, không bớt.
- **Test:** `test_indented_tagged_heading_hides_section` (xfail, 4 kiểu thụt lề).

### SL-T032-3 · Thấp · Nhãn vắt hai dòng trên tiêu đề không được nhận

- **Tái hiện:** `## 7. Chất liệu thật [CẦN XÁC` rồi dòng `NHẬN]`, rồi `- bí mật A`.
- **Thực tế:** tiêu đề luôn đóng khối riêng nên nhãn bị cắt đôi; cả tiêu đề, `NHẬN]` và `- bí mật A` tới AI.
- **Mong đợi:** giấu cả mục. Khó xảy ra (tiêu đề ít khi xuống dòng trong Notepad); ghi để đủ. Cách sửa gợi ý: tiêu đề có nửa nhãn mở (`[`/`(` + một phần cụm chữ ở cuối dòng) thì xét thêm dòng kế, hoặc an toàn hơn: tiêu đề kết thúc bằng ngoặc mở chưa đóng thì coi như có nhãn.
- **Test:** `test_heading_tag_split_across_lines_hides_section` (xfail).

## Đánh giá 3 điểm Thợ Máy nêu

1. **Lọc thừa với ngoặc tròn, chữ đã bỏ dấu** (`(cần xác nhận lịch với khách)`, `[CẠN XÁC NHẬN]`): **chấp nhận.** Đúng hướng phiếu; hồ sơ thật không có câu nào bị ảnh hưởng (so chuỗi với `main`). Đã ghim hành vi bằng `test_parenthesis_overfilter_is_accepted`.
2. **Nhãn vắt qua hai ý khác nhau** (`- A [CẦN XÁC` / `- NHẬN]`): **chấp nhận.** Phiếu chỉ yêu cầu trong một ý; muốn tạo ra phải tự gõ `- ` giữa nhãn. Không viết test ghim (không muốn ghim một chỗ lọt).
3. **Tiêu đề thụt lề không kết thúc mục đang giấu:** **chấp nhận** (giấu thừa, an toàn). Ghim bằng `test_indented_heading_inside_hidden_section_keeps_hiding`. Lưu ý chiều ngược lại (tiêu đề thụt lề **có nhãn** không bắt đầu mục giấu) là SL-T032-2.

## Rủi ro và điểm cần chú ý

- Ngoài phạm vi phiếu, chỉ ghi nhận: nhãn với ngoặc khác (`{…}`, `<…>`, `【…】`) hay gạch nối (`[CẦN-XÁC-NHẬN]`) không được nhận; tiêu đề kiểu gạch dưới (`Tiêu đề` rồi dòng `=====`) có nhãn chỉ giấu đoạn đó, không giấu cả mục. Hồ sơ dùng `#` nên ít gặp.
- Dòng chỉ có ký tự vô hình giữa hai nửa nhãn bị coi là dòng trống và cắt khối: hợp lý (nhìn như dòng trống).
- BOM ở đầu chuỗi được giữ y nguyên ở dòng đầu kết quả nếu gọi `confirmed_profile` trực tiếp; đường đọc file thật (`utf-8-sig`) đã bỏ BOM nên không ảnh hưởng.

## Đề xuất

Giao lại Thợ Máy sửa SL-T032-1 (bắt buộc) và SL-T032-2, SL-T032-3 (nên) trong `rules.py`; bỏ `xfail` tương ứng khi sửa xong. Sau đó Soi Lỗi chạy lại `tests/test_soi_loi_t032.py`.

## Câu hỏi cho chủ dự án

Không có.

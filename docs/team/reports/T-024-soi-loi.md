# Báo cáo T-024 · Kiểm thử bộ lọc hồ sơ doanh nghiệp theo cả ý (kèm gộp T-022)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-024](../tickets/T-024-loc-ho-so-theo-khoi.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành. Kết luận kiểm thử: **KHÔNG ĐẠT** (2 lỗi làm lọt thông tin chưa xác nhận) |

## Tóm tắt (cho chủ dự án)

Bộ lọc mới tốt hơn hẳn bộ lọc cũ: cả 6 lỗi tìm thấy ở T-022 đã được sửa. Với hồ sơ hiện tại, AI không thấy dòng chưa xác nhận nào. Nhưng còn 2 cách viết làm lọt thông tin chưa xác nhận: (1) một ý có **dòng trống ở giữa**; (2) nhãn bị **chèn ký tự vô hình**, thường gặp khi chép chữ từ web hay Zalo. Cả hai sửa được nhanh, trong phạm vi phiếu này.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| (gộp) `origin/team/T-022` | Merge vào `team/T-024`, không rebase |
| `tests/test_business_profile.py` | Bỏ `xfail` ở 6 test SL-022-1…6 (nay đều qua), sửa chú thích "chờ T-024", bỏ `import pytest` không còn dùng |
| `tests/test_soi_loi_t024.py` | Test mới: 29 test qua + 33 test `xfail(strict=True)` cho lỗi SL-024-1, SL-024-2 (tính cả tham số) |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest
1970 passed, 36 xfailed in 109.58s

$ uv run ruff check .
All checks passed!
```

36 xfailed = 33 của phiếu này + 3 có sẵn từ trước.

Kiểm tra test mới có giá trị: chạy `tests/test_soi_loi_t024.py` trên **bộ lọc cũ** (`845f048`) thì 17 test hỏng, trong đó có test thử ngẫu nhiên và test file rất dài.

### Bước 1: gộp T-022

`git merge --no-edit origin/team/T-022` không xung đột. 6 test `xfail(strict=True)` "chờ T-024" đều báo XPASS, nên đã bỏ dấu xfail cả 6:

| Mã | Test | Kết quả |
|---|---|---|
| SL-022-1 | `test_multiline_item_with_tag_on_last_line_is_dropped_whole` | Qua |
| SL-022-2 | `test_multiline_item_with_tag_on_first_line_is_dropped_whole` | Qua |
| SL-022-3 | `test_note_with_leading_space_is_dropped` | Qua |
| SL-022-4 | `test_note_with_leading_tab_is_dropped` | Qua |
| SL-022-5 | `test_nfd_tag_is_dropped` | Qua |
| SL-022-6 | `test_tag_with_nbsp_is_dropped` | Qua |

Đã lấy cả commit `24f22b3` của Thợ Máy (test NBSP và khoảng trắng Unicode), qua hết.

### Bốn điểm Thợ Máy tự nêu

| Điểm | Hành vi | Mất thông tin đúng? | Lọt thông tin chưa xác nhận? | Đánh giá |
|---|---|---|---|---|
| (1) Nhãn ở ý con bỏ cả ý cha; dòng quên thụt lề tính vào ý trước | Đúng như mô tả | Có, khi viết sai cú pháp (quên gạch đầu dòng). Viết đúng mỗi ý một gạch thì không mất gì (`test_clean_items_next_to_tagged_item_are_kept`) | Không | Chấp nhận được, thiên về an toàn |
| (2) Tiêu đề thụt lề ` ##` coi là dòng tiếp | Ý trước có nhãn thì mất tiêu đề; ý trước sạch thì tiêu đề giữ y nguyên | Chỉ mất một tiêu đề, hoặc cả ý/đoạn sau nếu không có dòng trống | Không | Chấp nhận được |
| (3) Ghi chú `>` chen giữa không cắt ý | Nhãn trước hay sau ghi chú đều bỏ cả ý | Không | Không, trừ trường hợp nhãn nằm **trong** dòng ghi chú (xem Rủi ro) | Đạt |
| (4) Nhãn viết sai hẳn không nhận | `CẦN XÁC NHẬN` thiếu ngoặc, `[CAN XAC NHAN]`, `(CẦN…)`, `[CẦNXÁC…]`, `[CHƯA XÁC NHẬN]` đều lọt | Không | Có, nhưng ngoài phạm vi phiếu (không đổi cú pháp nhãn) | Ghi nhận bằng `test_misspelled_tags_are_not_recognised`, xem Đề xuất |

### Kiểu gõ Notepad đã thử (đều qua)

Xuống dòng `\r\n` kèm ghi chú và dòng trống, xuống dòng chỉ `\r` (Mac cũ), file có BOM đọc qua `load_rules`, dòng chỉ có dấu cách / tab / NBSP **giữa các ý**, dòng chỉ có `-`, gạch `*` lồng 4 dấu cách, `1.` lồng 3 cấp, số hai chữ số `10.`, thụt bằng tab, tiêu đề `#Chữ` không cách, file 10 000 dòng, và 500 hồ sơ sinh ngẫu nhiên (hạt giống cố định) trộn mọi kiểu trên với 5 dạng nhãn: không lần nào lọt nhãn hay ghi chú.

## Lỗi tìm thấy

### SL-024-1 · Dòng trống ở giữa một ý làm lọt nửa ý (mức: Trung bình, A3)

- **Tái hiện:**
  ```python
  confirmed_profile("- Khách đã phục vụ: khoảng 500\n\n  người [CẦN XÁC NHẬN]\n- Hotline 0909")
  # -> "- Khách đã phục vụ: khoảng 500\n\n- Hotline 0909"
  confirmed_profile("- Khách đã phục vụ: khoảng 500 [CẦN XÁC NHẬN]\n\n  người trong năm 2025\n- Hotline 0909")
  # -> "người trong năm 2025\n- Hotline 0909"
  ```
  Dòng "trống" chỉ có dấu cách (`"  "`) cũng vậy.
- **Mong đợi:** dòng thụt lề sau dòng trống vẫn thuộc ý trước (đúng cách Markdown hiểu một ý nhiều đoạn), nên cả ý bị bỏ.
- **Thực tế:** dòng trống đóng khối, nửa không có nhãn lọt vào prompt. Hồ sơ hiện tại không có cách viết này, nhưng chủ dự án hoàn toàn có thể bấm Enter hai lần khi viết ý dài.
- **Test:** `test_item_with_blank_line_then_indented_tagged_continuation`, `test_tagged_item_with_blank_line_then_indented_continuation` (xfail strict).
- **Gợi ý sửa:** khi gặp dòng trống, chưa đóng khối gạch đầu dòng ngay; nếu dòng không trống kế tiếp **thụt lề** thì vẫn tính vào khối đó.

### SL-024-2 · Ký tự vô hình trong nhãn hoặc trước `>` làm lọt (mức: Trung bình, A1/A3)

Trả lời câu hỏi của Chỉ Huy về U+200B: **có lọt**. Không chỉ U+200B mà mọi ký tự vô hình loại "định dạng" (Unicode Cf) đã thử: U+200B, U+200C, U+200D, U+2060, BOM U+FEFF, gạch nối mềm U+00AD.

- **Tái hiện:**
  ```python
  confirmed_profile("- Email x [CẦN​XÁC NHẬN]\n- Hotline 0909")
  # -> nguyên văn cả hai dòng: ý chưa xác nhận lọt vào prompt
  confirmed_profile("- Hotline 0909\n​> ghi chú riêng")
  # -> ghi chú riêng của chủ dự án lọt vào prompt
  ```
  Nhãn hỏng ở mọi vị trí chèn: thay dấu cách, cạnh dấu cách, ngay sau `[`. Chỉ khi ký tự vô hình nằm **trước** `[` thì nhãn vẫn được nhận.
- **Mong đợi:** ký tự vô hình bị bỏ qua khi so nhãn và khi xét dòng ghi chú.
- **Thực tế:** nhãn không được nhận, cả ý (kèm chữ "[CẦN XÁC NHẬN") vào prompt; dòng ghi chú bắt đầu bằng ký tự vô hình không bị bỏ.
- **Vì sao xếp Trung bình:** người dùng không thấy ký tự này trong Notepad nên không tự phát hiện được, và nó hay đi kèm chữ chép từ web, Zalo, Word. Chỉ khi nhãn được gõ tay thì mới không gặp.
- **Test:** `test_tag_with_invisible_char_is_recognised` (18 trường hợp), `test_note_preceded_by_invisible_char_is_dropped` (12 trường hợp), đều xfail strict. `test_invisible_char_before_tag_bracket_still_recognised` qua.
- **Gợi ý sửa:** trong `_is_unconfirmed` và khi xét `>`, bỏ mọi ký tự có `unicodedata.category(ch) == "Cf"` (và U+00AD) trước khi so. Dòng giữ lại vẫn để y nguyên.

## Test chập chờn `test_many_lookup_inputs_catch_naive_scan`

| Lượt | Điều kiện | Hỏng |
|---|---|---|
| 1 | 20 lần, chạy chồng với các lượt pytest/uv khác của tôi | **4/20** (mỗi lần hỏng 1 trong 3 tham số) |
| 2 | 20 lần, máy rảnh | 0/20 |
| 3 | 10 lần, 4 tiến trình chiếm hết 4 nhân CPU | 0/10 |

Tổng 4/50 (8%). Đúng là chập chờn: test đo bằng thời gian CPU nên không sợ CPU bận, nhưng hỏng khi có tiến trình Python/uv khác chạy cùng lúc (tranh bộ nhớ đệm, đọc đĩa). Test này hỏng khi bản quét **lỗi** chạy "không đủ chậm", nên lần hỏng là báo động giả, không phải code thật chậm. Không sửa trong phiếu này.

## Đối chiếu tiêu chí xong (của phiếu)

- [ ] Không còn cách viết thường gặp nào làm dòng chưa xác nhận lọt vào prompt: còn SL-024-1, SL-024-2
- [x] Kết quả trên file thật không mất dòng đúng nào (`test_real_profile_only_drops_what_old_filter_leaked`, cả test file thật của T-022 qua)
- [x] `uv run pytest` và `uv run ruff check .` sạch
- [x] 6 lỗi SL-022-1…6 của T-022 đã sửa, bỏ xfail

## Rủi ro và điểm cần chú ý

- Nhãn đặt **trong** dòng ghi chú giữa một ý (`- A\n  > [CẦN XÁC NHẬN]\n  tiếp`) không làm bỏ ý, vì ghi chú luôn bị bỏ trước. Hướng dẫn đầu file bảo đặt nhãn ở cuối dòng của ý, nên không xếp là lỗi; nhưng nếu muốn chắc hơn thì có thể cho nhãn trong ghi chú cũng đánh dấu cả ý.
- Gạch đầu dòng kiểu `•` hay `–` (chép từ Word) không được coi là gạch đầu dòng: cả đoạn bị coi là một khối, có nhãn thì mất cả đoạn (mất thông tin đúng, không lọt).
- Dòng chỉ có ký tự vô hình (`​`) không được coi là dòng trống nên nối hai khối: mất thông tin đúng, không lọt.

## Đề xuất

- (Thợ Máy) Sửa SL-024-1 và SL-024-2 trong `seo_app/content/rules.py`, rồi bỏ xfail ở `tests/test_soi_loi_t024.py`.
- (Ngòi Bút) Hướng dẫn đầu `config/business_profile.md`: ghi rõ cú pháp nhãn đúng `[CẦN XÁC NHẬN — lý do]` (có ngoặc vuông, có dấu), nhắc gõ tay nhãn thay vì chép; sửa câu "`>` phải đứng ở ngay đầu dòng" như Thợ Máy đề xuất.
- (Soi Lỗi / Thợ Máy, phiếu riêng) `test_many_lookup_inputs_catch_naive_scan` chập chờn khoảng 8%, chỉ khi chạy chồng tiến trình khác. Nên nới **cỡ đầu vào** của bản quét lỗi (để tỉ lệ thời gian của nó cách xa ngưỡng 9) hoặc lấy kết quả tốt nhất trong vài lần đo, không nới ngưỡng của test tốc độ thật.

## Câu hỏi cho chủ dự án

Không có.

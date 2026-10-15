# Báo cáo T-024 · Bộ lọc hồ sơ doanh nghiệp: lọc theo cả ý, không theo từng dòng

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-024](../tickets/T-024-loc-ho-so-theo-khoi.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trước đây app chỉ giấu đúng **một dòng** có nhãn `[CẦN XÁC NHẬN`. Nếu một ý viết dài hai, ba dòng thì phần còn lại vẫn lọt vào cho AI đọc. Giờ app giấu **cả ý**: nhãn nằm ở dòng nào của ý cũng vậy. Dòng ghi chú `>` cũng được giấu cả khi lỡ gõ dấu cách trước nó. Với hồ sơ hiện tại, những gì AI thấy không thay đổi gì.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/rules.py` | `confirmed_profile` lọc theo khối; thêm `_is_unconfirmed` (NFC + viết hoa + regex chịu khoảng trắng); bỏ hằng `UNCONFIRMED_TAG` (không còn nơi nào dùng) |
| `tests/test_profile_blocks.py` | 46 test mới (tính cả tham số) |

### Cách chia khối

- Gạch đầu dòng **không thụt lề** (`- `, `* `, `+ `, `1. `, `1) `) mở khối mới. Mọi dòng sau nó, cho tới dòng trống / tiêu đề / gạch đầu dòng không thụt lề kế tiếp, thuộc khối đó. Như vậy khối gồm cả dòng thụt vào, gạch đầu dòng lồng nhau và dòng **quên thụt lề** (gõ Notepad hay gặp).
- Đoạn văn thường: cả đoạn tới dòng trống.
- Tiêu đề `#` không thụt lề: đứng riêng một khối (nhãn trong tiêu đề chỉ bỏ tiêu đề).
- Dòng ghi chú (`line.strip()` bắt đầu bằng `>`): luôn bỏ, **không cắt khối**. Nếu ghi chú chen giữa một ý thì phần sau ghi chú vẫn tính là cùng ý.
- Nhãn: `\[\s*CẦN\s+XÁC\s+NHẬN` trên chữ đã `NFC` + `upper()`. Nhận cả viết thường, dạng NFD (Mac), dấu cách thừa, tab, dấu cách không ngắt, `[ CẦN`. Phần lý do sau đó là tùy ý, như trước.
- Dòng giữ lại được để y nguyên (không đổi khoảng trắng hay dạng Unicode), dòng trống giữ như bộ lọc cũ.

## Bằng chứng

```
$ uv run pytest
1917 passed, 3 xfailed in 99.55s

$ uv run ruff check .
All checks passed!
```

Lần chạy đầu có 2 test hỏng ở `tests/test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan` (test đo tốc độ của `sanitize`, không liên quan tới phiếu). Chạy riêng file đó: 39 passed. Chạy lại cả bộ: sạch như trên.

Chạy 39 test mới với **bộ lọc cũ** (code cũ, test mới): 25 test hỏng. Tức là test bắt được đúng các chỗ lọt.

### Mục 4: so bộ lọc cũ và mới trên file thật

Script so sánh từng dòng (`difflib`) giữa bộ lọc cũ (chép lại nguyên văn) và bộ lọc mới, trên cả 3 phiên bản `config/business_profile.md` có trong lịch sử git:

| Phiên bản | Cũ | Mới | Khác nhau |
|---|---|---|---|
| `73ba839` (T-022, đang ở `team/T-022` và nhánh này) | 97 dòng | 97 dòng | **Giống hệt** |
| `55e3e61` | 103 dòng | 103 dòng | Giống hệt |
| `491d639` (bản đầu) | 95 dòng | 92 dòng | Mới bỏ thêm 3 dòng, xem dưới |

Ba dòng bộ lọc cũ để lọt ở bản `491d639` (đoạn văn có nhãn ở dòng đầu):

```
[CẦN XÁC NHẬN] Chi nhánh: website đang ghi 3 con số khác nhau      ← cũ bỏ, mới bỏ
(trang chủ "8 chi nhánh khác", Giới thiệu "3 chi nhánh: ...",       ← cũ LỌT, mới bỏ
Liên hệ liệt kê 9 địa chỉ, trong đó có Quận 1, Quận 3, Tân Bình ... ← cũ LỌT, mới bỏ
danh sách khu vực ở trên). AI chỉ dùng trụ sở Bình Tân ...          ← cũ LỌT, mới bỏ
```

Đây đúng loại lỗi phiếu mô tả, và đã từng có thật trong hồ sơ. Bản T-022 hiện tại đã được Ngòi Bút viết lại để mỗi nhãn nằm trên ý một dòng, nên kết quả không đổi.

Test `test_real_profile_only_drops_what_old_filter_leaked` kiểm trên file thật: kết quả mới là dãy con của kết quả cũ (không thêm, không đổi dòng nào), không còn nhãn, không còn dòng `>`. Test không gắn với nội dung cụ thể, để Ngòi Bút sửa hồ sơ không làm hỏng test.

### Bổ sung theo Chỉ Huy: SL-022-6 (nhãn có dấu cách không ngắt)

- Code ở commit `0abf443` đã xử lý được lỗi này. Regex `\[\s*CẦN\s+XÁC\s+NHẬN` chạy trên chữ đã chuẩn hóa NFC; `\s` của Python khớp mọi khoảng trắng Unicode (NBSP U+00A0, U+2009, U+202F, U+3000, tab, nhiều dấu cách). Kết quả giống như gộp mọi khoảng trắng thành một dấu cách rồi mới so.
- Thêm `test_tag_with_any_unicode_whitespace_between_words`: 7 kiểu khoảng trắng, đặt ở mọi chỗ trong nhãn, thử cả dạng NFC lẫn NFD.
- Đã chạy `tests/test_business_profile.py` của nhánh `team/T-022` trên code nhánh này (chép tạm, không commit): cả 6 test `xfail(strict=True)` "chờ T-024" (SL-022-1…6) đều **XPASS**, 18 test còn lại qua. Khi Soi Lỗi bỏ dấu xfail, các test này sẽ qua.
- Chưa xử lý ký tự không phải khoảng trắng như dấu cách độ rộng 0 (U+200B). Unicode không xếp U+200B vào khoảng trắng và hiếm khi gặp khi gõ Notepad.

## Đối chiếu tiêu chí xong

- [x] Không còn cách viết thường gặp nào làm dòng chưa xác nhận lọt vào prompt: nhãn ở dòng đầu, giữa, cuối (`test_multiline_bullet_dropped_whatever_line_has_tag`, `test_tag_at_end_of_second_line_as_profile_instructs`, `test_paragraph_block_is_whole_paragraph`); viết thường, NFD, dấu cách thừa, tab, NBSP và khoảng trắng Unicode khác (`test_tag_variants_recognised`, `test_tag_with_any_unicode_whitespace_between_words`); quên thụt lề (`test_unindented_continuation_of_bullet_belongs_to_bullet`); lồng nhau (`test_nested_bullets_drop_whole_parent_item`, `test_tag_on_parent_drops_nested_children`); `>` có dấu cách/tab/NBSP (`test_note_lines_dropped_even_with_leading_whitespace`); xuống dòng kiểu Windows (`test_windows_line_endings`)
- [x] Kết quả trên file thật không mất dòng đúng nào: giống hệt bộ lọc cũ (bảng trên, `test_real_profile_only_drops_what_old_filter_leaked`)
- [x] `uv run pytest` và `uv run ruff check .` sạch
- [x] Báo cáo nộp tại `docs/team/reports/T-024-tho-may.md`

## Rủi ro và điểm cần chú ý

- **Chủ ý thiên về giấu nhiều:** nhãn ở một gạch đầu dòng con thì bỏ **cả ý cha** cùng mọi ý con (đúng chữ của phiếu: "các dòng thụt vào ngay sau nó"). Một dòng quên thụt lề ngay sau gạch đầu dòng cũng bị coi là cùng ý. Nếu chủ dự án viết hai ý liền nhau mà ý sau không có gạch đầu dòng, ý sau có thể bị giấu theo. Như vậy có thể mất thông tin đúng, nhưng không lọt thông tin sai.
- Tiêu đề **thụt lề** (` ## …`) được coi là dòng tiếp của ý trước, không phải tiêu đề. Nếu ý trước có nhãn thì tiêu đề đó bị giấu theo (an toàn, chỉ mất tiêu đề).
- Ghi chú `>` chen giữa ý không cắt ý. Ngược lại, dòng `>` không bao giờ được coi là dòng trống, nên không làm hai đoạn văn tách nhau.
- Không đoán được nhãn viết sai hẳn (ví dụ thiếu `[`, gõ không dấu "CAN XAC NHAN"). Giữ đúng cú pháp nhãn như phiếu yêu cầu.
- Test tốc độ `test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan` có lúc hỏng khi chạy cả bộ (máy bận). Không liên quan phiếu này.

## Đề xuất

- (Ngòi Bút) Hướng dẫn đầu `config/business_profile.md` (dòng 5–9) vẫn ghi "Dấu `>` phải đứng ở ngay đầu dòng" và "Dòng có chữ `[CẦN XÁC NHẬN`". Sau khi gộp phiếu này nên sửa thành: "`>` đứng đầu dòng (có dấu cách trước cũng được)" và "Ý có nhãn ở bất kỳ dòng nào thì AI không thấy cả ý". Tôi không sửa vì `config/**` ngoài phạm vi.
- (Soi Lỗi) Thử thêm: file trộn tab và dấu cách, ý rất dài, dòng chỉ có `-`, nhãn đặt trong ghi chú `>` ngay giữa ý.
- (Soi Lỗi) Test `test_many_lookup_inputs_catch_naive_scan` lúc hỏng lúc không khi chạy cả bộ; nên xem lại ngưỡng.

## Câu hỏi cho chủ dự án

Không có.

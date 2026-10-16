# Báo cáo T-043 · Bộ lọc hồ sơ: 3 lỗi Thấp còn lại sau T-032

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-043](../tickets/T-043-loc-ho-so-loi-thap-sau-t032.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Bộ lọc hồ sơ doanh nghiệp nay nhận thêm 3 kiểu gõ nhãn `[CẦN XÁC NHẬN]` lạ: nhãn trên tiêu đề bị
ngắt bởi dòng trống, tiêu đề lỡ thụt lề có nhãn bị xuống dòng, và nhãn có ký tự lạ chen giữa
(`[**CẦN XÁC NHẬN**]`, `["CẦN XÁC NHẬN"]`, `[⚠ CẦN XÁC NHẬN]`, `[CẦN-XÁC-NHẬN]`…). Hồ sơ hiện tại
AI vẫn thấy y như trước. Câu thường "cần xác nhận lịch" (không ngoặc) vẫn không bị giấu.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/rules.py` | SL-T032-4: tiêu đề chờ nửa sau của nhãn thì bỏ qua dòng trống (giữ lại các dòng trống nếu không ghép được). SL-T032-5: tiêu đề thụt lề có nửa nhãn ở cuối cũng chờ dòng kế, trừ khi dòng trước còn nửa nhãn (để dòng này nối vào khối trước như cũ). LC-T032-1: mẫu nhãn cho phép khoảng trắng tùy ý cộng **tối đa 4** ký tự không phải chữ/số (trừ `)` `]`) ở đầu và giữa nhãn; `_ends_with_partial_tag` viết lại: chỉ xét 64 ký tự cuối (sau khi gộp khoảng trắng), thử từng ngoặc mở, nhận cả ký tự lạ. |
| `config/business_profile.md` | Chỉ dòng `>` hướng dẫn: thêm "có in đậm `**`, ngoặc kép hay gạch nối giữa các chữ đều được". |
| `tests/test_soi_loi_t032.py` | Bỏ 2 dấu `xfail` của SL-T032-4, SL-T032-5 (thân test giữ nguyên). |
| `tests/test_profile_tag_t032.py` | Thêm 44 test T-043: dòng trống khi chờ, tiêu đề thụt lề (4 kiểu thụt), 14 kiểu ký tự lạ trong nhãn, 7 câu thường phải giữ, nửa nhãn có ký tự lạ trên tiêu đề, 9 test tốc độ (`[[[[…`, `[****…`, `[ * [ * …`, nhiều khoảng trắng, nhiều dòng trống…). |

## Bằng chứng

```
$ uv run pytest
3605 passed, 4 skipped, 13 xfailed, 1 warning in 196.91s (0:03:16)

$ uv run ruff check .
All checks passed!
```

- Hồ sơ thật: lưu `load_rules().business_profile` trên `main` trước khi sửa, so `cmp` với bản sau
  khi sửa: giống hệt (6124 byte).
- Thử ngược: đổi `{0,4}` thành `*` thì test tốc độ chạy quá 2 phút không xong (bậc hai), tức test
  bắt được. Đã khôi phục `{0,4}`.

## Đối chiếu tiêu chí xong

- [x] SL-T032-4 (`test_round2_half_tag_heading_then_blank_then_rest`, `test_t043_half_tag_heading_*`)
- [x] SL-T032-5 (`test_round2_indented_half_tag_heading`, `test_t043_indented_*`)
- [x] LC-T032-1 (`test_t043_symbols_inside_tag`, `test_t043_heading_with_half_tag_and_symbols`)
- [x] Câu thường không bị giấu (`test_t043_plain_sentences_still_kept`)
- [x] Tuyến tính (`test_t043_filter_scales_linearly`, 9 kiểu)
- [x] Hồ sơ thật AI thấy không đổi (so chuỗi)
- [x] `uv run pytest`, `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

- Giấu thừa thêm (chấp nhận theo hướng an toàn): `(… cần xác nhận …)` có tối đa 4 ký tự lạ sau
  ngoặc mở, ví dụ `(– cần xác nhận lại)`. Đã chặn bớt bằng cách không cho `)` `]` nằm giữa, nên
  `(*) cần xác nhận lịch`, `[] cần xác nhận`, `(xem bảng) cần xác nhận` vẫn giữ.
- Từ 5 ký tự lạ trở lên (`[*****CẦN XÁC NHẬN]`) không nhận là nhãn: cái giá của giới hạn chống
  chạy bậc hai. Có test ghim.
- Tiêu đề **không** thụt lề đứng ngay sau dòng có nửa nhãn (`- x [CẦN XÁC` / `## NHẬN]`) vẫn như
  `main`: tiêu đề cắt khối, khối trước tới AI. Ngoài phạm vi phiếu, rất hiếm.

## Đề xuất

Soi Lỗi thử thêm ký tự Unicode lạ (emoji nhiều điểm mã như `⚠️` đã qua; cờ, da màu) chen trong nhãn.

## Câu hỏi cho chủ dự án

Không có.

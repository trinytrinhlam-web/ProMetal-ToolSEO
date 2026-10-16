# Báo cáo T-043 · Soi Lỗi kiểm thử: bộ lọc hồ sơ, 3 lỗi Thấp sau T-032

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-043](../tickets/T-043-loc-ho-so-loi-thap-sau-t032.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành · Kết luận: **đạt có điều kiện** |

## Tóm tắt (cho chủ dự án)

Cả 3 lỗi của phiếu đã được sửa đúng, test cũ không bị nới, bộ lọc vẫn chạy nhanh với đầu vào xấu
cỡ 1 MB, và phần hồ sơ thật AI thấy giống hệt bản trên `main`. Còn một lỗi Thấp mới: nhãn có từ
**5 ký tự lạ trở lên** (ví dụ `[❗❗❗ **CẦN XÁC NHẬN**]`, hay emoji gia đình kèm ⚠️) thì không được
nhận, nên ý đó vẫn tới AI. Đây là cái giá của giới hạn "tối đa 4" mà phiếu yêu cầu để chống chậm.
Tôi đã thử một cách sửa vừa không giới hạn số ký tự vừa vẫn nhanh (xem SL-T043-1).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t043.py` | Mới: 63 test (55 qua, 8 `xfail(strict=True)` cho SL-T043-1, SL-T043-2). |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t043.py
55 passed, 8 xfailed

$ uv run pytest
3660 passed, 4 skipped, 21 xfailed, 1 warning in 154.67s

$ uv run ruff check .
All checks passed!
```

- Diff test của Thợ Máy: `tests/test_soi_loi_t032.py` chỉ bỏ 2 dòng `xfail` (SL-T032-4, -5), thân
  test giữ nguyên; `tests/test_profile_tag_t032.py` chỉ thêm (116 dòng thêm, 0 dòng xóa).
- Hồ sơ thật: chạy `load_rules().business_profile` trên `origin/main` (worktree riêng) và trên
  `team/T-043`, so bằng `cmp`: giống hệt, 6124 byte.

## Kiểm lại 3 lỗi

| Mã | Kết quả | Test |
|---|---|---|
| SL-T032-4 | Đã sửa. Dòng trống thường, dòng chỉ có khoảng trắng/tab, dòng chỉ có U+200B, dòng ghi chú `>` xen giữa hai nửa nhãn đều nối được. Không nối được thì dòng trống giữ y nguyên. | `test_sl_t032_4_*` |
| SL-T032-5 | Đã sửa, cả khi thụt bằng tab, U+3000 và nhãn có ký tự lạ. | `test_sl_t032_5_*` |
| LC-T032-1 | Đã sửa cho tới 4 ký tự lạ: `~~**`, `***`, `` ` ``, `⚠️ **`, cờ, da màu, emoji gia đình (4 điểm mã), NBSP, U+3000, U+2800, ký tự vô hình xen ký tự lạ, dấu kết hợp trên ký tự lạ. | `test_lc_t032_1_*` |

## Lọc thừa (chỉ ghi nhận)

Giữ đúng (không bị giấu): `khách (cần) xác nhận`, `[*] cần xác nhận lịch`, `[ ] cần xác nhận…`
(ô tick Markdown), `[x] …`, `[1] Cần xác nhận…` (chú thích số), `(xem bảng) cần xác nhận`,
`(≥ 1 ngày, cần xác nhận)`.

Bị giấu thừa (hướng an toàn, đã ghim test): `(*Cần xác nhận lại với khách*)`,
`(– cần xác nhận lại)`. Link Markdown `[Cần xác nhận lịch](url)` bị giấu nhưng đã vậy từ `main`.

## Lỗi tìm thấy

### SL-T043-1 · Thấp · Từ 5 ký tự lạ trở lên thì nhãn không được nhận (lọt)

- **Tái hiện:** `confirmed_profile("- a\n- x [❗❗❗ **CẦN XÁC NHẬN**]\n- b")`. Tương tự:
  `[🇻🇳🇻🇳 **CẦN XÁC NHẬN**]` (mỗi cờ là 2 điểm mã), `[⚠️👨‍👩‍👧‍👦 CẦN XÁC NHẬN]` (emoji gia đình là 4
  điểm mã sau khi bỏ ZWJ), `[CẦN ** ⚠️ ** XÁC NHẬN]`, `[*​*​*​*​*CẦN…]`, và
  nửa nhãn trên tiêu đề `## 7 [❗❗❗ **CẦN` / `XÁC NHẬN**]`.
- **Mong đợi:** ý (hoặc mục) bị giấu.
- **Thực tế:** ý tới AI. Một hình emoji người dùng thấy có thể là 2–7 điểm mã, nên "4 ký tự" thực
  ra hẹp hơn người dùng nghĩ.
- **Đề xuất sửa (đã thử, không sửa code):** bỏ giới hạn số lượng nhưng **loại ngoặc mở** `[ (`
  khỏi phần chen giữa, dùng lượng từ chiếm hữu (Python ≥ 3.11, dự án yêu cầu 3.12):
  `_GAP = r"(?:\s|[^\w\s\[\]()]|_)*+"`. Bậc hai của `[[[[…` sinh ra vì `[` vừa là điểm bắt đầu
  vừa là ký tự chen; loại `[ (` khỏi phần chen thì mỗi điểm bắt đầu chỉ quét tới ngoặc kế tiếp.
  Thử trong scratch: nhận cả 6 ca trên, vẫn giữ `[*] …`, `(xem) …`, `[ ] …`; tỉ lệ thời gian 4×
  đầu vào ≈ 4,0 với `[[[`, `[*`, `[ * `, `[***`, `[CAN * * *`, `[CAN*[`, `(CAN XAC*(` (tuyến tính).
  `_PARTIAL_TAG_REST` cũng cần loại `[ (` cho khớp, và xem lại cửa sổ 64 ký tự (khi không giới
  hạn ký tự lạ thì nửa nhãn hợp lệ có thể dài hơn 64).
- **Test:** `test_sl_t043_1_five_or_more_symbols_hidden` (6 ca), `test_sl_t043_1_heading_half_tag_five_symbols`.

### SL-T043-2 · Thấp · Nửa sau của nhãn gõ thành tiêu đề `## NHẬN]` (có từ trước)

- **Tái hiện:** `"## 7 [CẦN XÁC\n## NHẬN]\n- bí mật\n## 8\n- ok"`.
- **Mong đợi:** `bí mật` bị giấu.
- **Thực tế:** chuỗi ghép `## 7 [CẦN XÁC ## NHẬN]` nay khớp nhãn (vì `##` là 2 ký tự lạ hợp lệ),
  nên tiêu đề đầu bị giấu; nhưng dòng `## NHẬN]` là tiêu đề thật cùng cấp nên kết thúc mục giấu
  ngay, `- bí mật` lọt. Trên `main` cũng lọt (khác là tiêu đề đầu còn giữ). Không phải hồi quy,
  rất hiếm (phải tự gõ `##` ở dòng sau).
- **Đề xuất:** khi dòng nối là tiêu đề thật cùng cấp hoặc cao hơn, coi mục vẫn đang giấu (không
  để chính dòng nối kết thúc mục).
- **Test:** `test_sl_t043_2_rest_of_tag_on_heading_line`.

## Cửa sổ 64 ký tự của `_ends_with_partial_tag`

Không lừa được: khoảng trắng/tab dài (5000), NBSP dài, U+200B dài, 1000 chữ hay 1000 ngoặc phía
trước, 100 cụm `[*****` phía trước, nửa nhãn có ký tự lạ ở mọi chỗ trống, emoji. Nửa nhãn hợp lệ
dài nhất (`[ * * * * CHUA * * * * XAC * * * * NHA`, 38 ký tự) nằm gọn trong cửa sổ; nửa nhãn dài
hơn chỉ có thể chứa ≥ 5 ký tự lạ, vốn không khớp mẫu đầy đủ (cùng gốc với SL-T043-1).
Test: `test_partial_tag_window_not_fooled` (10 ca), `test_partial_tag_longest_valid_half_fits_window`.

## Tốc độ

Đo thời gian CPU, đầu vào 250 KB rồi 1 MB (tỉ lệ ≈ 4 là tuyến tính, 16 là bậc hai):

| Đầu vào xấu | 250 KB | 1 MB | Tỉ lệ |
|---|---|---|---|
| `[[[[…` | 0,12 s | 0,53 s | 4,4 |
| `((((…` | 0,12 s | 0,50 s | 4,2 |
| `[****…` | 0,07 s | 0,18 s | 2,7 |
| `[` + khoảng trắng | 0,05 s | 0,24 s | 4,7 |
| `[CAN XAC` + khoảng trắng | 0,09 s | 0,22 s | 2,4 |
| `[ [ [ …` | 0,10 s | 0,44 s | 4,4 |
| tiêu đề `[ * [ * …` | 0,13 s | 0,40 s | 3,2 |
| `[*CAN*XAC*` lặp | 0,05 s | 0,22 s | 4,0 |
| `[*` + U+200B xen | 0,03 s | 0,17 s | 5,7 |
| tiêu đề nửa nhãn + 1 MB dòng trống | 0,13 s | 0,55 s | 4,2 |
| tiêu đề thụt lề có nửa nhãn lặp | 0,22 s | 0,81 s | 3,7 |

Tất cả tuyến tính. 12 kiểu (cỡ đầy đủ 250 KB cho nhanh) đưa vào `test_bad_input_scales_linearly`.

## Đối chiếu tiêu chí

- [x] 3 lỗi sửa đúng; chỉ bỏ `xfail`, test cũ không bị nới
- [x] Câu thường không bị giấu
- [x] Tuyến tính với đầu vào xấu cỡ 1 MB
- [x] Hồ sơ thật AI thấy không đổi so với `main` (`cmp`, 6124 byte)
- [x] Test không gọi mạng (chỉ gọi `confirmed_profile`)
- [ ] Lọc thiếu khi ≥ 5 ký tự lạ (SL-T043-1, Thấp)

## Kết luận: ĐẠT CÓ ĐIỀU KIỆN

Phiếu đạt mục tiêu và không hồi quy; có thể sang Lá Chắn. Điều kiện: Chỉ Huy quyết SL-T043-1 sửa
luôn trong T-043 (đề xuất đã thử, nhỏ) hay lập phiếu sau. SL-T043-2 có từ trước, ghi lại để biết.

## Ghi nhận ngoài phạm vi (có từ `main`, không tính lỗi phiếu này)

`【CẦN XÁC NHẬN】`, `{CẦN XÁC NHẬN}`, `<CẦN XÁC NHẬN>` (ngoặc khác `[ (`), `[<b>CẦN XÁC NHẬN</b>]`
và `[1️⃣ CẦN XÁC NHẬN]` (chữ/số chen giữa) không được nhận. Hướng dẫn trong hồ sơ đã nói rõ chỉ
`[ ]` và `( )`.

## Câu hỏi cho chủ dự án

Không có.

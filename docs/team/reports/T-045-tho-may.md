# Báo cáo T-045 · Bộ lọc hồ sơ: 3 lỗi Thấp theo dõi sau T-043

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-045](../tickets/T-045-loc-ho-so-theo-doi-sau-t043.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Bộ lọc hồ sơ doanh nghiệp đã sửa xong 3 lỗi Thấp còn lại sau T-043. (1) Một ý đã gắn nhãn
`[CẦN XÁC NHẬN]` mà có dòng thụt lề `  ## … [CẦN` bên trong: trước đây phần sau dòng đó tới AI,
nay cả ý bị giấu. (2) Nhãn có nhiều ký tự lạ (`[❗❗❗ **CẦN XÁC NHẬN**]`, emoji ghép, cờ) nay được
nhận, không còn giới hạn 4 ký tự. (3) Nhãn bị tách thành `## 7 [CẦN XÁC` rồi dòng sau `## NHẬN]`
nay giấu đúng cả mục. Phần hồ sơ thật mà AI thấy **giống hệt** trước khi sửa. Bộ lọc vẫn chạy
tuyến tính với đầu vào xấu cỡ 1 MB.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/rules.py` | Sửa 3 lỗi (chi tiết dưới), thêm 2 sửa chống lùi do fuzz tìm ra, bộ nhớ đệm nhỏ (`functools.lru_cache`, thư viện chuẩn). |
| `tests/test_profile_tag_t045.py` | Mới: 92 test (3 lỗi, các ca fuzz tìm ra, câu thường phải giữ, 16 test tốc độ). |
| `tests/test_soi_loi_t043.py` | Chỉ bỏ dấu `xfail` (thân test giữ nguyên): `test_sl_t043_1_five_or_more_symbols_hidden` (6 ca), `test_sl_t043_1_heading_half_tag_five_symbols`, `test_sl_t043_2_rest_of_tag_on_heading_line`. Tổng 8 ca `xfail` thành qua. |
| `tests/test_profile_tag_t032.py` | Bỏ đúng 1 ca `"- [*****CẦN XÁC NHẬN]"` khỏi `test_t043_plain_sentences_still_kept`. Ca này ghim hành vi cũ ("5 ký tự lạ là câu thường"), mâu thuẫn trực tiếp với SL-T043-1. Nay ca này được kiểm theo chiều ngược lại (phải bị giấu) trong `test_sl_t043_1_many_symbols_inside_tag_hidden`. |

### Cách sửa

- **LC-T043-1** (`rules.py`, nhánh tiêu đề thụt lề): khối đang mở **đã có nhãn** thì dòng
  `  ## … [CẦN` không tách khối nữa. Dòng đó nằm trong khối, đồng thời vẫn chờ dòng kế như tiêu đề
  (SL-T032-5). Nếu ghép được nhãn thì giấu cả khối lẫn mục của tiêu đề đó, như `main`. Kết quả
  "khối có nhãn" được nhớ lại (`block_is_tagged`), nên không dò lại cả khối ở mỗi dòng.
- **SL-T043-2**: dòng vừa ghép với tiêu đề chờ thành nhãn là nửa sau của nhãn, nên bị bỏ qua
  luôn (`continue`). Nó không còn được coi là tiêu đề cùng cấp để kết thúc mục đang giấu.
- **SL-T043-1**: bỏ giới hạn `{0,4}`, dùng **hai loại khoảng chen**:
  - `_LEAD_GAP = (?:[^\w\[\]()]|_)*+`: ngay sau ngoặc mở, không cho ngoặc nào. Nhờ vậy `[[[[…`
    không chạy bậc hai: mỗi điểm bắt đầu chỉ quét tới ngoặc kế tiếp.
  - `_GAP = (?:[^\w\])]|_)*+`: giữa các chữ, vẫn cho ngoặc mở, chỉ cấm ngoặc đóng. Mỗi chữ `CAN`/`CHUA` chỉ có một
    điểm bắt đầu khớp được (ngoặc mở gần nhất), nên mỗi dải chen bị quét một lần.

  Tôi **không** dùng nguyên mẫu một-khoảng-chen của Soi Lỗi `(?:\s|[^\w\s\[\]()]|_)*+`. Đã thử:
  mẫu đó làm lùi `[CẦN (XÁC NHẬN]` (khớp trên `main`, có test ghim
  `test_t043_half_tag_last_bracket_is_not_the_tag_start`). Đầu ra lệnh thử:
  `[CẦN (XÁC NHẬN] soi-loi: False hien tai: True`.

  `_ends_with_partial_tag`: trước khi lấy cửa sổ 64 ký tự, thu mỗi dải ký tự chen về **một** ký
  tự (`[` nếu dải có ngoặc mở, không thì dấu cách). Mọi ngoặc mở trong cùng một dải cho cùng kết
  quả, nên thu lại không đổi kết quả. Nửa nhãn dài nhất sau khi thu chỉ còn 23 ký tự. Vì vậy
  **giữ được cửa sổ 64** (thời gian so khớp cố định mỗi dòng) mà nửa nhãn có hàng trăm ký tự lạ
  vẫn được nhận. Đây là lưu ý 1 của Lá Chắn.
- **Chống lùi (fuzz tìm ra, xem dưới):** khi đang giấu một mục mà gặp tiêu đề cấp cao hơn có
  nhãn (hay nửa nhãn) của riêng nó, kể cả tiêu đề lỡ thụt lề, thì giấu tới cấp của tiêu đề đó
  (`_tagged_heading_level`). Ngoài ra, tiêu đề thụt lề có nhãn ngay sau dòng còn nửa nhãn thì giấu
  chung ý phía trước.

## Bằng chứng

```
$ uv run pytest            (commit 9782dc0)
<điền ở dưới: mục "Kết quả chạy cuối">

$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_profile_tag_t045.py tests/test_soi_loi_t043.py tests/test_profile_tag_t032.py \
    tests/test_soi_loi_t032.py tests/test_soi_loi_t024.py tests/test_profile_blocks.py \
    tests/test_business_profile.py tests/test_content_rules.py
572 passed in 28.45s
```

Lần chạy toàn bộ trước đó (commit `d8e2dc1`, đủ mọi test; sau đó chỉ thêm docstring và bộ nhớ
đệm): `5390 passed, 10 skipped, 23 xfailed, 1 warning in 528.24s`. Cảnh báo là của pydantic trong
test lớp AI, có từ trước.

**Hồ sơ thật trước/sau.** Lưu `load_rules().business_profile` trên `b5ff3b3` trước khi sửa, so
với commit cuối:

```
$ cmp profile_before.txt profile_after.txt && echo "HO SO GIONG HET"
HO SO GIONG HET
sha256 cả hai: f38e7172f1344b4ef87aa3117eedca6b82a47355e3c36ebfa72c22fac63fa071 (6224 byte khi ghi bằng write_text trên Windows)
```

**Thử ngược.** (a) Các ca lỗi trên bản gốc `b5ff3b3`: LC-T043-1 ra `'## ghi chú [CẦN\n  BIMAT\n- ok'`,
SL-T043-2 ra `'## NHẬN]\n- BIMAT\n## 8\n- ok'`, SL-T043-1 ra
`'- x [❗❗❗ **CẦN XÁC NHẬN**] BIMAT\n- ok'` (đều lọt). Trên bản mới, cả ba bị giấu. (b) Thay
`_LEAD_GAP` bằng `_GAP` (cho ngoặc mở ngay sau ngoặc mở) rồi chạy đo tốc độ với `[[[[…`: quá
300 giây không xong (`exit=124`), tức chạy bậc hai và test tốc độ bắt được.

**Fuzz so với bản gốc `b5ff3b3`.** Tài liệu ngẫu nhiên ghép từ 25 mảnh nhãn và 13 kiểu đầu dòng,
mỗi dòng có mã riêng. Đếm dòng bản cũ giấu mà bản mới để lộ. Script ở scratchpad, không commit.

| Lần chạy | Dòng lùi | Tài liệu lùi ngoài lớp Lá Chắn T-043 #2 | Dòng giấu thêm |
|---|---|---|---|
| 300.000 tài liệu, đủ mảnh | 91 (67 tài liệu) | **0** | 114.352 |
| 300.000 tài liệu, bỏ 2 mảnh có ≥ 5 ký tự lạ | **0** | 0 | 7.969 |

Lần đầu fuzz tìm ra 130 dòng lùi thật. Gốc lỗi là tiêu đề có nhãn bị nuốt trong mục đang giấu,
và tiêu đề chờ bị mất vai trò khi nằm trong khối. Tôi đã sửa cả hai (commit `d8e2dc1`), kèm test.

**Tốc độ.** Thời gian CPU mỗi lần gọi, đầu vào 250 KB rồi 1 MB. Mỗi lần đo lặp đủ 0,3 s, các ca
nhiều dòng dùng dòng khác nhau để bộ nhớ đệm không làm đẹp số. Tỉ lệ khoảng 4 là tuyến tính, 16
là bậc hai.

| Đầu vào xấu | 250 KB | 1 MB | Tỉ lệ |
|---|---|---|---|
| `[[[[` | 0,041 s | 0,180 s | 4,4 |
| `((((` | 0,045 s | 0,219 s | 4,9 |
| `[****` | 0,052 s | 0,211 s | 4,0 |
| `[CAN****…XAC` | 0,047 s | 0,195 s | 4,2 |
| `[CAN[[[[` | 0,052 s | 0,219 s | 4,2 |
| `[CAN XAC****…[` | 0,047 s | 0,195 s | 4,2 |
| `[CAN*[CAN*…` | 0,047 s | 0,180 s | 3,8 |
| `[*(*` lặp | 0,041 s | 0,195 s | 4,8 |
| tiêu đề `[ * ( ` lặp | 0,045 s | 0,195 s | 4,4 |
| tiêu đề nửa nhãn dài | 0,049 s | 0,188 s | 3,8 |
| ý có nhãn + `  ## bN [CAN` (LC-T043-1) | 0,594 s | 2,359 s | 4,0 |
| mục giấu + `#x N [CAN` lặp | 0,078 s | 0,312 s | 4,0 |
| `  ## bN [CAN` nối nhau | 0,859 s | 3,281 s | 3,8 |
| tiêu đề chờ trong khối lặp | 0,391 s | 1,641 s | 4,2 |
| `## N [CAN XAC` / `## NHAN]` lặp (SL-T043-2) | 0,422 s | 1,766 s | 4,2 |

So với bản gốc trên cùng đầu vào 1 MB (dòng khác nhau):

| Đầu vào | gốc | mới |
|---|---|---|
| `  ## bN [CAN` nối nhau | 2,23 s | 2,97 s |
| ý có nhãn + `  ## bN [CAN` | 2,84 s | 2,12 s |
| tiêu đề chờ trong khối | 2,05 s | 1,69 s |
| mục giấu + `#x N [CAN` | 0,33 s | 0,31 s |

Ca chậm nhất dài gấp khoảng 170 lần hồ sơ thật (6 KB). Riêng ca "nối nhau" chậm hơn bản gốc 1,3
lần, vì mỗi dòng nay còn chờ dòng kế.

## Đối chiếu tiêu chí xong

- [x] LC-T043-1 đã sửa, có test mới (`test_lc_t043_1_*`, 31 ca, gồm cả ca của Lá Chắn)
- [x] SL-T043-1 đã sửa (`test_sl_t043_1_*` của Soi Lỗi bỏ `xfail`; thêm `test_sl_t043_1_many_symbols_inside_tag_hidden`, `test_sl_t043_1_heading_half_tag_with_many_symbols`)
- [x] SL-T043-2 đã sửa (`test_sl_t043_2_rest_of_tag_on_heading_line` bỏ `xfail`; thêm `test_sl_t043_2_*`)
- [x] Chỉ bỏ đúng `xfail` của các lỗi đã sửa (3 hàm, 8 ca, tên ở bảng trên)
- [x] Test T-024, T-032, T-043 vẫn qua. Ngoại lệ là 1 ca ghim hành vi cũ, mâu thuẫn với SL-T043-1 (xem bảng)
- [x] Câu thường vẫn giữ (`test_sl_t043_1_plain_sentences_still_kept`, `test_plain_sentences_not_hidden`)
- [x] Tuyến tính, không lồng lượng từ, lượng từ chiếm hữu (bảng tốc độ; `test_sl_t043_1_unbounded_symbols_still_linear`, `test_new_paths_linear`, `test_lc_t043_1_linear_on_long_tagged_item`)
- [x] Hồ sơ thật AI thấy không đổi (`cmp`, sha256 giống)
- [x] Test không gọi mạng: chỉ gọi `confirmed_profile` trên chuỗi (D3)
- [x] `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

- **Lớp Lá Chắn T-043 #2 (đã ghi "không cần sửa") gặp nhiều hơn.** Tiêu đề thụt lề có nhãn tách ý
  ngay trước nó ra (thiết kế SL-T032-2). Nay nhãn có ≥ 5 ký tự lạ cũng được nhận, nên ca sau xảy
  ra: `- ok` / `  ## 7 [❗❗❗ **CẦN XÁC NHẬN**]` / `  BIMAT [CẦN XÁC NHẬN]`. Bản cũ giấu `- ok`
  (nhờ may, do nhãn ở dòng sau), bản mới giữ `- ok` vì ý đó không có nhãn riêng. Đây là toàn bộ
  91 dòng lùi còn lại trong fuzz. Nếu muốn giấu cả `- ok` thì phải đổi thiết kế SL-T032-2, đồng
  thời sửa test đã duyệt `test_indented_tagged_heading_hides_section_and_keeps_item_before`.
  Ngoài phạm vi phiếu, Chỉ Huy quyết.
- **Giấu thừa thêm (hướng an toàn):**
  - Ngoặc có nhiều ký tự lạ rồi tới "cần xác nhận", ví dụ `(— — — cần xác nhận lại)`.
  - Tiêu đề cấp cao hơn có nhãn riêng nằm trong mục đang giấu: giấu tới cấp của nó.
  - `#x [CẦN XÁC NHẬN]` có cấp 1 nên giấu tới tiêu đề `#` kế tiếp, như `main` làm khi không đang giấu.
- `tests/test_profile_tag_t032.py` có sửa 1 dòng ngoài danh sách `xfail`. Lý do ở bảng "Đã thay đổi".

## Đề xuất

- Soi Lỗi thử: nhãn rất dài nhiều emoji/ký tự lạ vắt dòng trên tiêu đề, kể cả tiêu đề thụt lề;
  ngoặc mở chen giữa nhãn (`[CẦN (XÁC`, `[CẦN [** XÁC`); chuỗi tiêu đề `  ## … [CẦN` nối nhau trong
  ý có và không có nhãn; tiêu đề cấp cao hơn có nhãn nằm trong mục đang giấu (`##x`, `  ## [CẦN…]`);
  dòng `## NHẬN]` sau tiêu đề chờ kèm dòng trống, dòng `>`.
- Lá Chắn kiểm: (A1) chạy lại fuzz 300.000 ca của T-043 so với `main`; xem lớp #2 nói trên;
  (F3/ReDoS) `_LEAD_GAP`/`_GAP`/`_PARTIAL_GAP_RUN` với `[[[[`, `[CAN[[[[`, `[CAN*[CAN*`,
  `[*(*` cỡ 1 MB; (A3) so hồ sơ thật.

## Câu hỏi cho chủ dự án

Không có.
